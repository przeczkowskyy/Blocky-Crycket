import fs from 'node:fs';
import path from 'node:path';
import express, { type Request, type Response, type NextFunction } from 'express';
import { all, get, insert, log, now, run, uid, update, getSettings, setSettings, tx, db, DEFAULT_SETTINGS } from './db.ts';
import { seedIfEmpty } from './seed.ts';
import { DASHBOARD_ROOT, isImage, isWritablePath, normalizeRel, readProjectFile, resolveProjectPath, walkProject, languageFor, isProtectedPath } from './paths.ts';
import { aiConfigured, deleteProjectFile, emergencyStop, listExecutions, MODELS, PRICING, runningCount, startExecution, styleCheckAsset, testConnection, writeProjectFile } from './agents.ts';
import { buildContext, discoverSources, health, indexAll, indexSource, search } from './brain.ts';
import { integrations, rojoBuild, rojoSourcemap, rojoStatus, runTest, studioStatus, gitStatus } from './integrations.ts';
import { recoverInterruptedRuns, resumeWorkflow, startWorkflow, stopWorkflow } from './workflows.ts';
import { STYLE_CHECKLIST, STYLE_LOCK_PREFIX, STYLE_FORBIDDEN } from './knowledge.ts';

const PORT = Number(process.env.STUDIO_PORT ?? 4310);
const app = express();
app.use(express.json({ limit: '40mb' }));

type H = (req: Request, res: Response) => any;
const h = (fn: H) => async (req: Request, res: Response, next: NextFunction) => {
  try {
    const r = await fn(req, res);
    if (!res.headersSent) res.json(r ?? { ok: true });
  } catch (e) { next(e); }
};
const bad = (msg: string, status = 400) => Object.assign(new Error(msg), { status });
const need = (v: any, name: string) => { if (v === undefined || v === null || (typeof v === 'string' && !v.trim())) throw bad(`Pole "${name}" jest wymagane`); return v; };

// ================= status / overview =================

app.get('/api/status', h(async () => {
  const s = getSettings();
  const project = get<any>('SELECT * FROM project LIMIT 1');
  const [rojo, git] = await Promise.all([rojoStatus(), gitStatus()]);
  return {
    phase: project?.roadmap?.find((p: any) => p.id === project.current_phase)?.name ?? project?.current_phase,
    branch: git.configured ? git.branch : null,
    activeAgents: get<{ c: number }>("SELECT COUNT(*) AS c FROM agents WHERE status IN ('thinking','working')")!.c,
    runningExecutions: runningCount(),
    pendingApprovals: get<{ c: number }>("SELECT COUNT(*) AS c FROM approvals WHERE status = 'pending'")!.c,
    rojo, studio: studioStatus(), ai: { configured: aiConfigured() },
    autonomyMode: s.autonomyMode, emergencyStop: s.emergencyStop,
  };
}));

app.post('/api/emergency-stop', h((req) => {
  const active = !!req.body?.active;
  setSettings({ emergencyStop: active });
  let stopped = 0;
  if (active) stopped = emergencyStop();
  log('Game Director', active ? 'EMERGENCY STOP aktywowany' : 'EMERGENCY STOP wyłączony', active ? `Przerwano ${stopped} wykonań.` : '', undefined, active ? 'error' : 'info');
  return { active, stopped };
}));

app.get('/api/overview', h(() => {
  const project = get<any>('SELECT * FROM project LIMIT 1');
  const count = (sql: string, ...p: any[]) => get<{ c: number }>(sql, ...p)!.c;
  const sprintTasks = all<any>('SELECT id, title, status, assigned_agent_id FROM tasks WHERE sprint = 1');
  const roadmap = project.roadmap as any[];
  const items = roadmap.flatMap((p) => p.items);
  const attention = {
    approvals: all("SELECT id, title, agent_id, created_at FROM approvals WHERE status = 'pending' ORDER BY created_at DESC LIMIT 6"),
    failed: all("SELECT e.id, e.error, e.started_at, a.name AS agent_name FROM agent_executions e JOIN agents a ON a.id = e.agent_id WHERE e.status = 'failed' ORDER BY e.started_at DESC LIMIT 5"),
    conflicts: all("SELECT id, title FROM approvals WHERE status = 'pending' AND conflict = 1"),
    missingAssets: count("SELECT COUNT(*) AS c FROM assets WHERE status = 'planned'"),
    questions: all("SELECT id, question FROM questions WHERE status = 'open' LIMIT 5"),
    decisionsAwaiting: count("SELECT COUNT(*) AS c FROM project_decisions WHERE status IN ('awaiting_approval','proposed')"),
    brainUpdates: count("SELECT COUNT(*) AS c FROM brain_updates WHERE status = 'pending'"),
  };
  return {
    project,
    stats: {
      activeAgents: count("SELECT COUNT(*) AS c FROM agents WHERE status IN ('thinking','working')"),
      tasksInProgress: count("SELECT COUNT(*) AS c FROM tasks WHERE status = 'in_progress'"),
      pendingApprovals: count("SELECT COUNT(*) AS c FROM approvals WHERE status = 'pending'"),
      openBugs: count("SELECT COUNT(*) AS c FROM bugs WHERE status NOT IN ('resolved','closed')"),
      completedTasks: count("SELECT COUNT(*) AS c FROM tasks WHERE status = 'completed'"),
      totalTasks: count('SELECT COUNT(*) AS c FROM tasks'),
      assetsCreated: count("SELECT COUNT(*) AS c FROM assets WHERE status IN ('created','approved')"),
      assetsTotal: count('SELECT COUNT(*) AS c FROM assets'),
    },
    progress: { done: items.filter((i) => i.done).length, total: items.length },
    sprint: {
      ...project.sprint,
      completed: sprintTasks.filter((t) => t.status === 'completed').length,
      remaining: sprintTasks.filter((t) => t.status !== 'completed').length,
      blocked: sprintTasks.filter((t) => t.status === 'blocked').length,
      tasks: sprintTasks,
    },
    activity: all('SELECT * FROM activity_logs ORDER BY id DESC LIMIT 15'),
    lastActivity: get<any>('SELECT * FROM activity_logs ORDER BY id DESC LIMIT 1'),
    agents: all('SELECT id, name, role, status, current_activity, color, icon, enabled FROM agents ORDER BY sort'),
    attention,
  };
}));

app.patch('/api/project', h((req) => {
  const p = get<any>('SELECT * FROM project LIMIT 1')!;
  const { roadmap, sprint, current_phase, description } = req.body ?? {};
  update('project', p.id, { roadmap, sprint, current_phase, description, updated_at: now() });
  log('Game Director', 'Zaktualizował projekt', Object.keys(req.body ?? {}).join(', '), { type: 'project', id: p.id });
  return get('SELECT * FROM project LIMIT 1');
}));

// ================= settings =================

app.get('/api/settings', h(() => ({ settings: getSettings(), defaults: DEFAULT_SETTINGS, models: MODELS, pricing: PRICING })));
app.patch('/api/settings', h((req) => {
  const b = req.body ?? {};
  if (b.autonomyMode && !['assistant', 'semi', 'autonomous'].includes(b.autonomyMode)) throw bad('Nieprawidłowy tryb autonomii');
  for (const k of ['maxIterations', 'costLimitUsd', 'timeLimitSec', 'rojoPort', 'maxContextChunks']) {
    if (b[k] !== undefined && (typeof b[k] !== 'number' || !(b[k] > 0))) throw bad(`${k} musi być liczbą dodatnią`);
  }
  if (b.protectedFiles && !Array.isArray(b.protectedFiles)) throw bad('protectedFiles musi być listą');
  const s = setSettings(b);
  log('Game Director', 'Zmienił ustawienia', Object.keys(b).join(', '));
  return s;
}));

// ================= agents & executions =================

app.get('/api/agents', h(() => {
  const agents = all<any>('SELECT * FROM agents ORDER BY sort');
  const stats = all<any>("SELECT agent_id, COUNT(*) AS runs, SUM(input_tokens) AS input_tokens, SUM(output_tokens) AS output_tokens, SUM(cost_usd) AS cost FROM agent_executions GROUP BY agent_id");
  const tasks = all<any>("SELECT assigned_agent_id, COUNT(*) AS c FROM tasks WHERE status NOT IN ('completed') GROUP BY assigned_agent_id");
  return agents.map((a) => ({
    ...a,
    stats: stats.find((s) => s.agent_id === a.id) ?? { runs: 0, input_tokens: 0, output_tokens: 0, cost: 0 },
    openTasks: tasks.find((t) => t.assigned_agent_id === a.id)?.c ?? 0,
    configured: aiConfigured(),
  }));
}));

app.get('/api/agents/:id', h((req) => {
  const a = get<any>('SELECT * FROM agents WHERE id = ?', req.params.id);
  if (!a) throw bad('Nie znaleziono agenta', 404);
  return {
    ...a,
    configured: aiConfigured(),
    tasks: all('SELECT * FROM tasks WHERE assigned_agent_id = ? ORDER BY updated_at DESC', a.id),
    executions: all('SELECT id, prompt, status, started_at, finished_at, error, input_tokens, output_tokens, cost_usd, duration_ms, model FROM agent_executions WHERE agent_id = ? ORDER BY started_at DESC LIMIT 50', a.id),
    stats: get('SELECT COUNT(*) AS runs, COALESCE(SUM(input_tokens),0) AS input_tokens, COALESCE(SUM(output_tokens),0) AS output_tokens, COALESCE(SUM(cost_usd),0) AS cost, COALESCE(AVG(duration_ms),0) AS avg_ms FROM agent_executions WHERE agent_id = ?', a.id),
    activity: all("SELECT * FROM activity_logs WHERE actor = ? ORDER BY id DESC LIMIT 30", a.name),
  };
}));

app.patch('/api/agents/:id', h((req) => {
  const a = get<any>('SELECT * FROM agents WHERE id = ?', req.params.id);
  if (!a) throw bad('Nie znaleziono agenta', 404);
  const { model, effort, instructions, enabled, permissions } = req.body ?? {};
  if (model && !MODELS.includes(model)) throw bad('Nieobsługiwany model');
  if (effort && !['low', 'medium', 'high', 'xhigh', 'max'].includes(effort)) throw bad('Nieprawidłowy poziom effort');
  if (instructions !== undefined && String(instructions).trim().length < 20) throw bad('Instrukcje są za krótkie');
  update('agents', a.id, {
    model, effort, instructions, permissions: permissions ? { ...a.permissions, ...permissions } : undefined,
    enabled: enabled === undefined ? undefined : !!enabled,
    status: enabled === false ? 'offline' : enabled === true && a.status === 'offline' ? 'idle' : undefined,
    updated_at: now(),
  });
  log('Game Director', `Zmienił konfigurację ${a.name}`, Object.keys(req.body ?? {}).join(', '), { type: 'agent', id: a.id });
  return get('SELECT * FROM agents WHERE id = ?', a.id);
}));

app.post('/api/agents/:id/run', h((req) => {
  const { prompt, taskId, relatedFiles } = req.body ?? {};
  need(prompt, 'prompt');
  const { executionId } = startExecution({ agentId: req.params.id, prompt, taskId, relatedFiles: Array.isArray(relatedFiles) ? relatedFiles : [] });
  log('Game Director', 'Zlecił zadanie', `${req.params.id}: ${String(prompt).slice(0, 200)}`, { type: 'execution', id: executionId });
  return { executionId };
}));

app.get('/api/executions', h((req) => {
  const agentId = req.query.agentId as string | undefined;
  return agentId ? all('SELECT e.*, a.name AS agent_name, a.color AS agent_color FROM agent_executions e JOIN agents a ON a.id = e.agent_id WHERE agent_id = ? ORDER BY started_at DESC LIMIT 100', agentId) : listExecutions(150);
}));
app.get('/api/executions/:id', h((req) => {
  const e = get<any>('SELECT e.*, a.name AS agent_name, a.color AS agent_color FROM agent_executions e JOIN agents a ON a.id = e.agent_id WHERE e.id = ?', req.params.id);
  if (!e) throw bad('Nie znaleziono wykonania', 404);
  return { ...e, snapshot: get('SELECT * FROM agent_context_snapshots WHERE agent_execution_id = ?', e.id), approvals: all('SELECT id, title, status FROM approvals WHERE execution_id = ?', e.id) };
}));

// ================= tasks =================

const TASK_STATUSES = ['backlog', 'planned', 'in_progress', 'waiting_approval', 'testing', 'completed', 'blocked'];
const PRIORITIES = ['low', 'medium', 'high', 'critical'];

app.get('/api/tasks', h(() => all('SELECT * FROM tasks ORDER BY CASE priority WHEN \'critical\' THEN 0 WHEN \'high\' THEN 1 WHEN \'medium\' THEN 2 ELSE 3 END, updated_at DESC')));
app.get('/api/tasks/:id', h((req) => {
  const t = get<any>('SELECT * FROM tasks WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono zadania', 404);
  return {
    ...t,
    comments: all('SELECT * FROM task_comments WHERE task_id = ? ORDER BY created_at', t.id),
    history: all("SELECT * FROM activity_logs WHERE entity_type = 'task' AND entity_id = ? ORDER BY id DESC", t.id),
    executions: all('SELECT e.id, e.status, e.started_at, e.error, a.name AS agent_name FROM agent_executions e JOIN agents a ON a.id = e.agent_id WHERE task_id = ? ORDER BY started_at DESC', t.id),
    subtasks: all('SELECT id, title, status, assigned_agent_id FROM tasks WHERE parent_id = ?', t.id),
    approvals: all('SELECT id, title, status FROM approvals WHERE task_id = ?', t.id),
  };
}));
app.post('/api/tasks', h((req) => {
  const b = req.body ?? {};
  need(b.title, 'title');
  if (b.status && !TASK_STATUSES.includes(b.status)) throw bad('Nieprawidłowy status');
  if (b.priority && !PRIORITIES.includes(b.priority)) throw bad('Nieprawidłowy priorytet');
  const id = uid('T-');
  insert('tasks', {
    id, title: String(b.title).trim(), description: b.description ?? '', assigned_agent_id: b.assigned_agent_id || null, status: b.status ?? 'backlog',
    priority: b.priority ?? 'medium', effort: b.effort ?? null, dependencies: b.dependencies ?? [], related_files: b.related_files ?? [],
    related_docs: b.related_docs ?? [], brain_source_ids: [], sprint: !!b.sprint, phase: b.phase ?? 'phase1', created_by: 'Game Director', created_at: now(), updated_at: now(),
  });
  log('Game Director', 'Utworzył zadanie', b.title, { type: 'task', id });
  return get('SELECT * FROM tasks WHERE id = ?', id);
}));
app.patch('/api/tasks/:id', h((req) => {
  const t = get<any>('SELECT * FROM tasks WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono zadania', 404);
  const b = req.body ?? {};
  if (b.status && !TASK_STATUSES.includes(b.status)) throw bad('Nieprawidłowy status');
  if (b.priority && !PRIORITIES.includes(b.priority)) throw bad('Nieprawidłowy priorytet');
  if (b.status && b.status !== t.status && ['in_progress', 'testing', 'completed'].includes(b.status)) {
    const deps = (t.dependencies as string[]).map((d) => get<any>('SELECT title, status FROM tasks WHERE id = ?', d)).filter(Boolean);
    const open = deps.filter((d) => d.status !== 'completed');
    if (open.length && !b.force) throw bad(`Zadanie zależy od nieukończonych: ${open.map((d) => d.title).join(', ')}. Wyślij ponownie z force, aby kontynuować.`, 409);
  }
  const fields = ['title', 'description', 'assigned_agent_id', 'status', 'priority', 'effort', 'dependencies', 'related_files', 'related_docs', 'sprint', 'phase'];
  const patch: any = { updated_at: now() };
  for (const f of fields) if (b[f] !== undefined) patch[f] = b[f];
  update('tasks', t.id, patch);
  const changes = fields.filter((f) => b[f] !== undefined && JSON.stringify(b[f]) !== JSON.stringify(t[f])).map((f) => `${f}: ${JSON.stringify(t[f])} → ${JSON.stringify(b[f])}`);
  if (changes.length) log('Game Director', 'Zmienił zadanie', `${t.title} — ${changes.join('; ')}`.slice(0, 600), { type: 'task', id: t.id });
  return get('SELECT * FROM tasks WHERE id = ?', t.id);
}));
app.delete('/api/tasks/:id', h((req) => {
  const t = get<any>('SELECT * FROM tasks WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono zadania', 404);
  run('DELETE FROM tasks WHERE id = ?', t.id);
  log('Game Director', 'Usunął zadanie', t.title, { type: 'task', id: t.id }, 'warn');
}));
app.post('/api/tasks/:id/comments', h((req) => {
  need(req.body?.body, 'body');
  insert('task_comments', { id: uid('C-'), task_id: req.params.id, author: req.body.author ?? 'Game Director', body: req.body.body, created_at: now() });
  log('Game Director', 'Skomentował zadanie', String(req.body.body).slice(0, 200), { type: 'task', id: req.params.id });
}));
app.post('/api/tasks/:id/run', h((req) => {
  const t = get<any>('SELECT * FROM tasks WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono zadania', 404);
  if (!t.assigned_agent_id) throw bad('Zadanie nie ma przypisanego agenta');
  const { executionId } = startExecution({ agentId: t.assigned_agent_id, taskId: t.id, prompt: req.body?.prompt || 'Wykonaj to zadanie w ramach swojej roli.' });
  update('tasks', t.id, { status: 'in_progress', updated_at: now() });
  log('Game Director', 'Uruchomił zadanie', t.title, { type: 'task', id: t.id });
  return { executionId };
}));
app.post('/api/tasks/:id/breakdown', h((req) => {
  const t = get<any>('SELECT * FROM tasks WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono zadania', 404);
  const { executionId } = startExecution({ agentId: 'atlas', taskId: t.id, prompt: 'Rozbij to zadanie na mniejsze podzadania (new_tasks) i przypisz każde najlepszemu specjaliście. Nie pisz kodu.' });
  log('Game Director', 'Poprosił ATLAS o rozbicie zadania', t.title, { type: 'task', id: t.id });
  return { executionId };
}));

// ================= approvals =================

app.get('/api/approvals', h((req) => {
  const status = req.query.status as string | undefined;
  return status ? all('SELECT * FROM approvals WHERE status = ? ORDER BY created_at DESC', status) : all('SELECT * FROM approvals ORDER BY CASE status WHEN \'pending\' THEN 0 ELSE 1 END, created_at DESC LIMIT 300');
}));

app.post('/api/approvals/:id/:action', h(async (req) => {
  const a = get<any>('SELECT * FROM approvals WHERE id = ?', req.params.id);
  if (!a) throw bad('Nie znaleziono zatwierdzenia', 404);
  if (a.status !== 'pending' && a.status !== 'changes_requested') throw bad(`Już rozpatrzone (${a.status})`);
  const action = req.params.action;
  const comment = req.body?.comment ?? null;
  const agent = a.agent_id ? get<any>('SELECT * FROM agents WHERE id = ?', a.agent_id) : null;

  if (action === 'approve' || action === 'approve-sync') {
    let syncInfo: any = null;
    if (a.change_type === 'file') {
      const pc = a.proposed_changes;
      const current = readProjectFile(pc.path);
      if ((current ?? null) !== (pc.before ?? null) && !req.body?.force) throw bad('Plik zmienił się od czasu propozycji (konflikt). Przejrzyj diff ponownie i zatwierdź z wymuszeniem.', 409);
      writeProjectFile(pc.path, pc.after, `Game Director (zatwierdzenie ${a.id})`, a.id, `Zmiana od ${agent?.name ?? 'agenta'}`);
      if (action === 'approve-sync') {
        const rs = await rojoStatus();
        syncInfo = rs.connected ? { synced: true, detail: `Rojo serve (${rs.projectName}) przesyła zmianę do Studio.` } : { synced: false, detail: 'Plik zapisany, ale Rojo serve nie działa — uruchom `rojo serve`.' };
      }
    }
    update('approvals', a.id, { status: 'approved', review_comment: comment, reviewed_at: now() });
    log('Game Director', action === 'approve-sync' ? 'Zatwierdził i zsynchronizował' : 'Zatwierdził zmianę', a.title, { type: 'approval', id: a.id }, 'success');
    afterReview(a);
    return { ok: true, sync: syncInfo };
  }
  if (action === 'reject') {
    update('approvals', a.id, { status: 'rejected', review_comment: comment, reviewed_at: now() });
    log('Game Director', 'Odrzucił zmianę', `${a.title}${comment ? ` — ${comment}` : ''}`, { type: 'approval', id: a.id }, 'warn');
    afterReview(a);
    return { ok: true };
  }
  if (action === 'request-changes') {
    need(comment, 'comment');
    update('approvals', a.id, { status: 'changes_requested', review_comment: comment, reviewed_at: now() });
    log('Game Director', 'Poprosił o poprawki', `${a.title} — ${comment}`, { type: 'approval', id: a.id }, 'warn');
    let executionId: string | null = null;
    if (agent && aiConfigured() && !getSettings().emergencyStop) {
      const pc = a.proposed_changes ?? {};
      executionId = startExecution({
        agentId: agent.id, taskId: a.task_id, workflowRunId: a.workflow_run_id, relatedFiles: pc.path ? [pc.path] : [],
        prompt: `The Game Director requested changes to your proposal "${a.title}".\nFeedback: ${comment}\nYour previous proposed content is below — produce a corrected version.`,
        extraContext: pc.after ? `PREVIOUS PROPOSAL for ${pc.path}:\n\`\`\`\n${pc.after}\n\`\`\`` : undefined,
      }).executionId;
      update('approvals', a.id, { status: 'superseded' });
    }
    afterReview(a);
    return { ok: true, executionId };
  }
  throw bad('Nieznana akcja');
}));

function afterReview(a: any) {
  if (a.agent_id) {
    const left = get<{ c: number }>("SELECT COUNT(*) AS c FROM approvals WHERE agent_id = ? AND status = 'pending'", a.agent_id)!.c;
    const ag = get<any>('SELECT status FROM agents WHERE id = ?', a.agent_id);
    if (!left && ag?.status === 'waiting_approval') update('agents', a.agent_id, { status: 'idle', current_activity: null });
  }
  if (a.task_id) {
    const left = get<{ c: number }>("SELECT COUNT(*) AS c FROM approvals WHERE task_id = ? AND status = 'pending'", a.task_id)!.c;
    const t = get<any>('SELECT status FROM tasks WHERE id = ?', a.task_id);
    if (!left && t?.status === 'waiting_approval') update('tasks', a.task_id, { status: 'testing', updated_at: now() });
  }
}

// ================= chat =================

app.get('/api/chat', h(() => all('SELECT * FROM chat_messages ORDER BY created_at DESC, rowid DESC LIMIT 200').reverse()));
app.post('/api/chat', h((req) => {
  const body = String(need(req.body?.body, 'body'));
  const agents = all<any>('SELECT id, name FROM agents');
  const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
  const resolve = (raw: string) => {
    const n = norm(raw);
    if (!n) return undefined;
    return agents.find((a) => norm(a.name) === n || a.id === n)?.id ?? agents.find((a) => norm(a.name).startsWith(n) && n.length >= 3)?.id;
  };
  const mentions = Array.from(new Set(Array.from(body.matchAll(/@([\p{L}\w-]+(?: [A-Z]{3,})?)/gu)).map((m) => resolve(m[1]) ?? resolve(m[1].split(' ')[0])).filter(Boolean))) as string[];
  const targets = mentions.length ? mentions : ['atlas'];
  const msgId = uid('M-');
  insert('chat_messages', { id: msgId, author_type: 'user', author: 'Game Director', body, mentions: targets, created_at: now() });

  if (!aiConfigured()) {
    insert('chat_messages', { id: uid('M-'), author_type: 'system', author: 'system', body: 'Agenci mają status NOT CONFIGURED — dodaj ANTHROPIC_API_KEY do dashboard/.env i zrestartuj serwer. Wiadomość zapisano, ale żaden agent jej nie przetworzył.', created_at: now() });
    return { ok: true, executions: [] };
  }
  const history = all<any>('SELECT author, body FROM chat_messages ORDER BY created_at DESC LIMIT 12').reverse().map((m) => `${m.author}: ${m.body}`).join('\n');
  const execs: string[] = [];
  for (const agentId of targets) {
    try {
      const { executionId, done } = startExecution({ agentId, chatMessageId: msgId, prompt: body, extraContext: `RECENT TEAM CHAT:\n${history}` });
      execs.push(executionId);
      const ag = agents.find((a) => a.id === agentId)!;
      done.then(() => {
        const ex = get<any>('SELECT * FROM agent_executions WHERE id = ?', executionId)!;
        if (ex.status === 'completed') {
          insert('chat_messages', { id: uid('M-'), author_type: 'agent', author: ag.name, body: ex.result?.message ?? '', execution_id: executionId, meta: { summary: ex.result?.summary, processed: ex.result?.processed }, created_at: now() });
        } else {
          insert('chat_messages', { id: uid('M-'), author_type: 'system', author: 'system', body: `${ag.name}: ${ex.status === 'cancelled' ? 'przerwano' : 'błąd'} — ${ex.error ?? ''}`, execution_id: executionId, created_at: now() });
        }
      });
    } catch (e: any) {
      insert('chat_messages', { id: uid('M-'), author_type: 'system', author: 'system', body: `${agentId.toUpperCase()}: ${e.message}`, created_at: now() });
    }
  }
  return { ok: true, executions: execs };
}));

// ================= workflows =================

app.get('/api/workflows', h(() => all('SELECT * FROM workflows ORDER BY id')));
app.get('/api/workflow-runs', h(() => all('SELECT r.*, w.name AS workflow_name FROM workflow_runs r JOIN workflows w ON w.id = r.workflow_id ORDER BY r.created_at DESC LIMIT 50')));
app.post('/api/workflows/:id/run', h((req) => ({ runId: startWorkflow(req.params.id, String(need(req.body?.input, 'input')), req.body?.taskId ?? null) })));
app.post('/api/workflow-runs/:id/resume', h((req) => { resumeWorkflow(req.params.id); }));
app.post('/api/workflow-runs/:id/stop', h((req) => { stopWorkflow(req.params.id); log('Game Director', 'Zatrzymał workflow', req.params.id, { type: 'workflow_run', id: req.params.id }, 'warn'); }));

// ================= files =================

app.get('/api/files/tree', h(() => ({ tree: walkProject(), locks: all('SELECT l.*, a.name AS agent_name FROM file_locks l LEFT JOIN agents a ON a.id = l.owner_agent_id') })));
app.get('/api/files/content', h((req) => {
  const rel = normalizeRel(String(need(req.query.path, 'path')));
  const content = readProjectFile(rel);
  if (content === null) throw bad('Plik nie istnieje', 404);
  const s = getSettings();
  return {
    path: rel, content, language: languageFor(rel), writable: isWritablePath(rel), protected: isProtectedPath(rel, s.protectedFiles),
    lock: get('SELECT l.*, a.name AS agent_name FROM file_locks l LEFT JOIN agents a ON a.id = l.owner_agent_id WHERE path = ?', rel),
    pending: all("SELECT id, title, agent_id, created_at FROM approvals WHERE status = 'pending' AND json_extract(proposed_changes, '$.path') = ?", rel),
    modifiedAt: fs.statSync(resolveProjectPath(rel)).mtime.toISOString(),
  };
}));
app.get('/api/files/raw', (req, res, next) => {
  try {
    const rel = normalizeRel(String(req.query.path ?? ''));
    if (!isImage(rel)) throw bad('Tylko obrazy');
    res.sendFile(resolveProjectPath(rel));
  } catch (e) { next(e); }
});
app.put('/api/files/content', h((req) => {
  const rel = normalizeRel(String(need(req.body?.path, 'path')));
  if (typeof req.body?.content !== 'string') throw bad('Brak treści');
  if (!isWritablePath(rel)) throw bad('Ten plik nie może być edytowany z dashboardu');
  const lock = get<any>('SELECT l.*, a.name AS agent_name FROM file_locks l LEFT JOIN agents a ON a.id = l.owner_agent_id WHERE path = ?', rel);
  if (lock && !req.body?.force) throw bad(`Plik jest zablokowany przez ${lock.agent_name} (trwa wykonanie). Zapisz z wymuszeniem, jeśli jesteś pewien.`, 423);
  const expected = req.body?.expectedModifiedAt;
  const abs = resolveProjectPath(rel);
  if (expected && fs.existsSync(abs) && fs.statSync(abs).mtime.toISOString() !== expected && !req.body?.force) throw bad('Plik został zmieniony na dysku od czasu otwarcia (np. przez agenta lub Rojo). Odśwież lub zapisz z wymuszeniem.', 409);
  writeProjectFile(rel, req.body.content, 'Game Director', null, 'Zapis z edytora');
  return { ok: true, modifiedAt: fs.statSync(abs).mtime.toISOString() };
}));
app.post('/api/files/create', h((req) => {
  const rel = normalizeRel(String(need(req.body?.path, 'path')));
  if (!isWritablePath(rel)) throw bad('Dozwolone tylko w src/, docs/, assets/');
  if (readProjectFile(rel) !== null) throw bad('Plik już istnieje', 409);
  writeProjectFile(rel, req.body?.content ?? '', 'Game Director', null, 'Nowy plik');
  return { path: rel };
}));
app.delete('/api/files', h((req) => { deleteProjectFile(normalizeRel(String(need(req.query.path, 'path'))), 'Game Director'); }));
app.get('/api/files/versions', h((req) => all('SELECT id, path, author, approval_id, note, created_at, LENGTH(content) AS size FROM file_versions WHERE path = ? ORDER BY created_at DESC', normalizeRel(String(need(req.query.path, 'path'))))));
app.get('/api/files/versions/:id', h((req) => get('SELECT * FROM file_versions WHERE id = ?', req.params.id)));
app.post('/api/files/rollback', h((req) => {
  const v = get<any>('SELECT * FROM file_versions WHERE id = ?', need(req.body?.versionId, 'versionId'));
  if (!v) throw bad('Nie znaleziono wersji', 404);
  if (v.content === null) deleteProjectFile(v.path, 'Game Director (rollback)');
  else writeProjectFile(v.path, v.content, 'Game Director (rollback)', null, `Rollback do wersji ${v.id}`);
  return { ok: true };
}));

app.get('/api/explorer', h(async () => {
  try { return { ok: true, tree: await rojoSourcemap() }; }
  catch (e: any) { return { ok: false, error: e.message }; }
}));

// ================= UI elements =================

app.get('/api/ui-elements', h(() => all('SELECT * FROM ui_elements ORDER BY sort').map((u: any) => ({
  ...u, fileStatus: (u.files ?? []).map((f: string) => { try { return { path: f, exists: readProjectFile(f) !== null }; } catch { return { path: f, exists: false }; } }),
}))));
app.post('/api/ui-elements', h((req) => {
  const b = req.body ?? {};
  need(b.screen, 'screen'); need(b.name, 'name');
  const id = uid('ui-');
  insert('ui_elements', { id, screen: b.screen, section: b.section ?? null, name: b.name, spec: b.spec ?? '', status: 'specified', assigned_agent_id: b.assigned_agent_id ?? 'pixel', files: b.files ?? [], dependencies: [], approval_status: 'not_submitted', roblox_path: b.roblox_path ?? null, sort: 999, updated_at: now() });
  log('Game Director', 'Dodał element UI', `${b.screen} / ${b.name}`, { type: 'ui', id });
  return get('SELECT * FROM ui_elements WHERE id = ?', id);
}));
app.patch('/api/ui-elements/:id', h((req) => {
  const u = get<any>('SELECT * FROM ui_elements WHERE id = ?', req.params.id);
  if (!u) throw bad('Nie znaleziono', 404);
  const b = req.body ?? {};
  update('ui_elements', u.id, { status: b.status, spec: b.spec, assigned_agent_id: b.assigned_agent_id, files: b.files, approval_status: b.approval_status, roblox_path: b.roblox_path, updated_at: now() });
  log('Game Director', 'Zmienił element UI', `${u.screen} / ${u.name}: ${Object.keys(b).join(', ')}`, { type: 'ui', id: u.id });
  return get('SELECT * FROM ui_elements WHERE id = ?', u.id);
}));

// ================= assets =================

app.get('/api/assets', h(() => all('SELECT * FROM assets ORDER BY category, name')));
app.get('/api/style-lock', h(() => ({ prefix: STYLE_LOCK_PREFIX, checklist: STYLE_CHECKLIST, forbidden: STYLE_FORBIDDEN })));
app.post('/api/assets', h((req) => {
  const b = req.body ?? {};
  need(b.name, 'name'); need(b.category, 'category');
  const id = uid('A-');
  let prompt: string | null = b.prompt ?? null;
  if (prompt && (b.kind ?? '2d') === '2d' && !prompt.startsWith(STYLE_LOCK_PREFIX.slice(0, 40))) prompt = `${STYLE_LOCK_PREFIX} ${prompt}`;
  insert('assets', { id, name: b.name, category: b.category, subcategory: b.subcategory ?? null, kind: b.kind ?? '2d', prompt, status: 'planned', style_compliance: 'needs_review', style_checklist: {}, agent_id: b.agent_id ?? null, feature: b.feature ?? null, version: 1, brain_source_ids: [], created_at: now(), updated_at: now() });
  log('Game Director', 'Dodał asset', b.name, { type: 'asset', id });
  return get('SELECT * FROM assets WHERE id = ?', id);
}));
app.patch('/api/assets/:id', h((req) => {
  const a = get<any>('SELECT * FROM assets WHERE id = ?', req.params.id);
  if (!a) throw bad('Nie znaleziono', 404);
  const b = req.body ?? {};
  if (b.style_compliance === 'compliant' && !a.style_report && !b.manualOverride) throw bad('Status "Compliant" wymaga analizy Style Lock lub ręcznego potwierdzenia (manualOverride).');
  update('assets', a.id, { name: b.name, status: b.status, style_compliance: b.style_compliance, style_checklist: b.style_checklist, prompt: b.prompt, agent_id: b.agent_id, feature: b.feature, notes: b.notes, updated_at: now() });
  log('Game Director', 'Zmienił asset', `${a.name}: ${Object.keys(b).join(', ')}`, { type: 'asset', id: a.id });
  return get('SELECT * FROM assets WHERE id = ?', a.id);
}));
app.post('/api/assets/:id/upload', h((req) => {
  const a = get<any>('SELECT * FROM assets WHERE id = ?', req.params.id);
  if (!a) throw bad('Nie znaleziono', 404);
  const name = String(need(req.body?.fileName, 'fileName')).replace(/[^\w.\-]+/g, '_');
  if (!/\.(png|jpe?g|webp|gif|svg|fbx|obj|bbmodel|glb|rbxm)$/i.test(name)) throw bad('Nieobsługiwany typ pliku');
  const data = Buffer.from(String(need(req.body?.dataBase64, 'dataBase64')), 'base64');
  const rel = `assets/${a.category}/${name}`;
  const abs = resolveProjectPath(rel);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, data);
  const img = isImage(rel);
  update('assets', a.id, { source_path: rel, preview_path: img ? rel : a.preview_path, status: 'created', version: a.source_path ? a.version + 1 : a.version, style_compliance: 'needs_review', style_report: null, updated_at: now() });
  log('Game Director', 'Wgrał plik assetu', `${a.name} → ${rel}`, { type: 'asset', id: a.id }, 'success');
  return get('SELECT * FROM assets WHERE id = ?', a.id);
}));
app.post('/api/assets/:id/style-check', h(async (req) => styleCheckAsset(req.params.id)));
app.delete('/api/assets/:id', h((req) => { run('DELETE FROM assets WHERE id = ?', req.params.id); log('Game Director', 'Usunął asset', req.params.id, { type: 'asset', id: req.params.id }, 'warn'); }));

// ================= bugs / tests / builds =================

app.get('/api/bugs', h(() => all("SELECT * FROM bugs ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC")));
app.post('/api/bugs', h((req) => {
  const b = req.body ?? {};
  need(b.title, 'title');
  const id = uid('BUG-');
  insert('bugs', { id, title: b.title, description: b.description ?? '', severity: b.severity ?? 'medium', category: b.category ?? 'luau', assigned_agent_id: b.assigned_agent_id ?? 'sentinel', related_files: b.related_files ?? [], repro_steps: b.repro_steps ?? '', status: 'open', reported_by: 'Game Director', created_at: now(), updated_at: now() });
  log('Game Director', 'Zgłosił błąd', b.title, { type: 'bug', id }, 'warn');
  return get('SELECT * FROM bugs WHERE id = ?', id);
}));
app.patch('/api/bugs/:id', h((req) => {
  const b = req.body ?? {};
  const bug = get<any>('SELECT * FROM bugs WHERE id = ?', req.params.id);
  if (!bug) throw bad('Nie znaleziono', 404);
  update('bugs', bug.id, { title: b.title, description: b.description, severity: b.severity, category: b.category, assigned_agent_id: b.assigned_agent_id, status: b.status, test_result: b.test_result, repro_steps: b.repro_steps, related_files: b.related_files, updated_at: now() });
  log('Game Director', 'Zmienił błąd', `${bug.title}: ${Object.keys(b).join(', ')}`, { type: 'bug', id: bug.id });
  return get('SELECT * FROM bugs WHERE id = ?', bug.id);
}));
app.post('/api/bugs/:id/workflow', h((req) => {
  const bug = get<any>('SELECT * FROM bugs WHERE id = ?', req.params.id);
  if (!bug) throw bad('Nie znaleziono', 404);
  const runId = startWorkflow('wf-bug', `BUG ${bug.id}: ${bug.title}\n${bug.description}\nRepro: ${bug.repro_steps}\nFiles: ${(bug.related_files ?? []).join(', ')}`, null);
  update('bugs', bug.id, { status: 'in_progress', updated_at: now() });
  return { runId };
}));

app.get('/api/tests', h(() => all('SELECT * FROM tests ORDER BY kind, name')));
app.post('/api/tests/:id/run', h(async (req) => runTest(req.params.id)));
app.post('/api/tests/run-all', h(async () => {
  const out: any[] = [];
  for (const t of all<any>("SELECT id FROM tests WHERE kind = 'automated'")) out.push({ id: t.id, ...(await runTest(t.id)) });
  return out;
}));
app.patch('/api/tests/:id', h((req) => {
  const t = get<any>('SELECT * FROM tests WHERE id = ?', req.params.id);
  if (!t) throw bad('Nie znaleziono', 404);
  if (t.kind !== 'manual') throw bad('Wynik testu automatycznego ustawia jego uruchomienie');
  const st = req.body?.status;
  if (!['passed', 'failed', 'not_run'].includes(st)) throw bad('Nieprawidłowy status');
  update('tests', t.id, { last_status: st, last_run_at: now(), last_output: req.body?.note ?? `Ręcznie oznaczone przez Game Director` });
  log('Game Director', `Test manualny: ${t.name}`, st, { type: 'test', id: t.id }, st === 'passed' ? 'success' : 'warn');
}));
app.post('/api/tests', h((req) => {
  const b = req.body ?? {};
  need(b.name, 'name');
  const id = uid('test-');
  insert('tests', { id, name: b.name, kind: 'manual', category: b.category ?? 'ui', description: b.description ?? '', last_status: 'not_run', regression: !!b.regression });
  return get('SELECT * FROM tests WHERE id = ?', id);
}));

app.get('/api/builds', h(() => all('SELECT * FROM builds ORDER BY created_at DESC LIMIT 100')));
app.post('/api/builds', h(async () => rojoBuild('manual')));

// ================= logs / integrations / performance =================

app.get('/api/logs', h((req) => {
  const where: string[] = []; const p: any[] = [];
  for (const k of ['actor', 'level', 'entity_type', 'entity_id']) if (req.query[k]) { where.push(`${k} = ?`); p.push(req.query[k]); }
  if (req.query.q) { where.push('(action LIKE ? OR details LIKE ?)'); p.push(`%${req.query.q}%`, `%${req.query.q}%`); }
  const limit = Math.min(Number(req.query.limit ?? 300), 1000);
  return all(`SELECT * FROM activity_logs ${where.length ? 'WHERE ' + where.join(' AND ') : ''} ORDER BY id DESC LIMIT ${limit}`, ...p);
}));
app.get('/api/integrations', h(() => integrations()));
app.post('/api/integrations/ai/test', h(async () => {
  if (!aiConfigured()) throw bad('NOT CONFIGURED: brak ANTHROPIC_API_KEY');
  const r = await testConnection(getSettings().defaultModel);
  log('System', 'Test połączenia AI', `OK: ${r.id}`, undefined, 'success');
  return r;
}));
app.get('/api/performance', h(() => ({
  byAgent: all('SELECT a.name, a.color, COUNT(e.id) AS runs, COALESCE(SUM(e.input_tokens),0) AS input_tokens, COALESCE(SUM(e.output_tokens),0) AS output_tokens, COALESCE(SUM(e.cost_usd),0) AS cost, COALESCE(AVG(e.duration_ms),0) AS avg_ms, SUM(CASE WHEN e.status = \'failed\' THEN 1 ELSE 0 END) AS failures FROM agents a LEFT JOIN agent_executions e ON e.agent_id = a.id GROUP BY a.id ORDER BY a.sort'),
  daily: all("SELECT substr(started_at,1,10) AS day, COUNT(*) AS runs, SUM(cost_usd) AS cost, SUM(input_tokens + output_tokens) AS tokens FROM agent_executions GROUP BY day ORDER BY day"),
  builds: all("SELECT created_at, duration_ms, status FROM builds ORDER BY created_at DESC LIMIT 30").reverse(),
  totals: get('SELECT COUNT(*) AS runs, COALESCE(SUM(cost_usd),0) AS cost, COALESCE(SUM(input_tokens),0) AS input_tokens, COALESCE(SUM(output_tokens),0) AS output_tokens, COALESCE(SUM(cache_read_tokens),0) AS cache_read_tokens FROM agent_executions'),
  costLimit: getSettings().costLimitUsd,
})));

// ================= project brain =================

app.get('/api/brain/overview', h(() => {
  const hl = health();
  const layers = {
    canonicalFacts: get<{ c: number }>("SELECT COUNT(*) AS c FROM brain_sources WHERE authoritative = 1 AND archived = 0")!.c,
    approvedDecisions: get<{ c: number }>("SELECT COUNT(*) AS c FROM project_decisions WHERE status = 'approved'")!.c,
    documentation: get<{ c: number }>("SELECT COUNT(*) AS c FROM brain_sources WHERE source_type IN ('documentation','kb-document') AND archived = 0")!.c,
    repository: get<{ c: number }>("SELECT COUNT(*) AS c FROM brain_sources WHERE source_type IN ('luau','gui-model','rojo-config','json','skill') AND archived = 0")!.c,
    assets: get<{ c: number }>('SELECT COUNT(*) AS c FROM assets')!.c,
    history: get<{ c: number }>('SELECT COUNT(*) AS c FROM agent_executions')!.c,
    proposals: get<{ c: number }>("SELECT COUNT(*) AS c FROM project_decisions WHERE status IN ('proposed','awaiting_approval')")!.c + get<{ c: number }>("SELECT COUNT(*) AS c FROM questions WHERE status = 'open'")!.c,
  };
  const categories = all<any>('SELECT categories FROM brain_sources WHERE archived = 0').flatMap((r) => r.categories ?? []);
  const catCounts: Record<string, number> = {};
  for (const c of categories) catCounts[c] = (catCounts[c] ?? 0) + 1;
  return { health: hl, layers, categories: catCounts, pendingUpdates: get<{ c: number }>("SELECT COUNT(*) AS c FROM brain_updates WHERE status = 'pending'")!.c };
}));
app.get('/api/brain/sources', h(() => all('SELECT id, name, source_type, origin, content_hash, version, indexing_status, authoritative, categories, access, archived, error, chunk_count, last_indexed_at, created_at, updated_at FROM brain_sources ORDER BY archived, source_type, name')));
app.get('/api/brain/sources/:id', h((req) => {
  const s = get<any>('SELECT * FROM brain_sources WHERE id = ?', req.params.id);
  if (!s) throw bad('Nie znaleziono', 404);
  return { ...s, chunks: all('SELECT id, ord, heading, content FROM brain_chunks WHERE source_id = ? ORDER BY ord', s.id), usedBy: all("SELECT agent_execution_id, created_at FROM agent_context_snapshots WHERE retrieved_source_ids LIKE ? ORDER BY created_at DESC LIMIT 20", `%${s.id}%`) };
}));
app.post('/api/brain/sources', h((req) => {
  const b = req.body ?? {};
  need(b.name, 'name'); need(b.content, 'content');
  const id = uid('src-');
  insert('brain_sources', { id, name: b.name, source_type: 'manual', origin: `manual:${id}`, version: 0, indexing_status: 'registered', authoritative: !!b.authoritative, categories: b.categories ?? ['manual'], access: 'all-agents', archived: false, content: b.content, created_at: now(), updated_at: now() });
  log('Game Director', 'Dodał źródło wiedzy', b.name, { type: 'brain_source', id });
  return indexSource(id);
}));
app.patch('/api/brain/sources/:id', h((req) => {
  const b = req.body ?? {};
  update('brain_sources', req.params.id, { archived: b.archived, authoritative: b.authoritative, categories: b.categories, access: b.access, updated_at: now() });
  log('Game Director', 'Zmienił źródło wiedzy', `${req.params.id}: ${Object.keys(b).join(', ')}`, { type: 'brain_source', id: req.params.id });
  return get('SELECT * FROM brain_sources WHERE id = ?', req.params.id);
}));
app.post('/api/brain/sources/:id/index', h((req) => indexSource(req.params.id)));
app.post('/api/brain/index', h((req) => indexAll(!!req.body?.onlyChanged)));
app.post('/api/brain/discover', h(() => ({ added: discoverSources() })));
app.get('/api/brain/search', h((req) => search(String(req.query.q ?? ''), Number(req.query.limit ?? 10))));
app.post('/api/brain/preview-context', h((req) => {
  const agent = get<any>('SELECT * FROM agents WHERE id = ?', need(req.body?.agentId, 'agentId'));
  if (!agent) throw bad('Nieznany agent');
  return buildContext({ agentId: agent.id, agentRole: agent.role, task: String(need(req.body?.task, 'task')), relatedFiles: req.body?.relatedFiles ?? [] });
}));
app.get('/api/brain/health', h(() => health()));
app.get('/api/brain/snapshots', h(() => all('SELECT s.id, s.agent_execution_id, s.context_summary, s.retrieved_source_ids, s.created_at, e.prompt, e.status, a.name AS agent_name FROM agent_context_snapshots s JOIN agent_executions e ON e.id = s.agent_execution_id JOIN agents a ON a.id = e.agent_id ORDER BY s.created_at DESC LIMIT 100')));
app.get('/api/brain/snapshots/:executionId', h((req) => get('SELECT * FROM agent_context_snapshots WHERE agent_execution_id = ?', req.params.executionId)));

app.get('/api/brain/updates', h(() => all('SELECT u.*, a.name AS agent_name FROM brain_updates u LEFT JOIN agents a ON a.id = u.agent_id ORDER BY CASE u.status WHEN \'pending\' THEN 0 ELSE 1 END, u.created_at DESC')));
app.post('/api/brain/updates/:id/:action', h((req) => {
  const u = get<any>('SELECT * FROM brain_updates WHERE id = ?', req.params.id);
  if (!u) throw bad('Nie znaleziono', 404);
  if (u.status !== 'pending') throw bad('Już rozpatrzone');
  if (req.params.action === 'approve') {
    const facts: string[] = req.body?.facts ?? u.proposed_changes?.new_facts ?? [];
    const reg = get<any>("SELECT * FROM project_documents WHERE title = 'Rejestr zatwierdzonych faktów'");
    if (reg && facts.length) {
      const content = `${reg.content}\n\n## ${now().slice(0, 10)} — ${u.agent_id ?? 'agent'} (${u.id})\n${facts.map((f) => `- ${f}`).join('\n')}`;
      saveDocVersion(reg, content, 'Game Director (Brain update)', true, `Fakty z ${u.id}`);
    }
    update('brain_updates', u.id, { status: 'approved', reviewed_by: 'Game Director', review_note: req.body?.note ?? null, reviewed_at: now() });
    log('Game Director', 'Zatwierdził aktualizację wiedzy', `${facts.length} faktów`, { type: 'brain_update', id: u.id }, 'success');
  } else if (req.params.action === 'reject') {
    update('brain_updates', u.id, { status: 'rejected', reviewed_by: 'Game Director', review_note: req.body?.note ?? null, reviewed_at: now() });
    log('Game Director', 'Odrzucił aktualizację wiedzy', u.id, { type: 'brain_update', id: u.id }, 'warn');
  } else throw bad('Nieznana akcja');
}));

// decisions
app.get('/api/decisions', h(() => all('SELECT * FROM project_decisions ORDER BY code')));
app.post('/api/decisions', h((req) => {
  const b = req.body ?? {};
  need(b.title, 'title'); need(b.description, 'description');
  const n = get<{ c: number }>('SELECT COUNT(*) AS c FROM project_decisions')!.c + 1;
  const id = uid('dec-');
  const approved = b.status === 'approved';
  insert('project_decisions', { id, code: `D-${String(n).padStart(3, '0')}`, title: b.title, description: b.description, category: b.category ?? 'game_design', status: b.status ?? 'proposed', proposed_by: 'Game Director', approved_by: approved ? 'Game Director' : null, related_docs: b.related_docs ?? [], related_tasks: b.related_tasks ?? [], created_at: now(), approved_at: approved ? now() : null, updated_at: now() });
  log('Game Director', 'Dodał decyzję', b.title, { type: 'decision', id });
  return get('SELECT * FROM project_decisions WHERE id = ?', id);
}));
app.patch('/api/decisions/:id', h((req) => {
  const d = get<any>('SELECT * FROM project_decisions WHERE id = ?', req.params.id);
  if (!d) throw bad('Nie znaleziono', 404);
  const b = req.body ?? {};
  const statuses = ['proposed', 'awaiting_approval', 'approved', 'rejected', 'superseded'];
  if (b.status && !statuses.includes(b.status)) throw bad('Nieprawidłowy status');
  if (d.status === 'approved' && (b.title || b.description) && !b.status) throw bad('Zatwierdzonej decyzji nie edytuje się — użyj "Zastąp" (supersede).');
  update('project_decisions', d.id, {
    title: b.title, description: b.description, category: b.category, status: b.status,
    approved_by: b.status === 'approved' ? 'Game Director' : undefined, approved_at: b.status === 'approved' ? now() : undefined, updated_at: now(),
  });
  log('Game Director', b.status ? `Decyzja ${d.code}: ${b.status}` : `Edytował decyzję ${d.code}`, d.title, { type: 'decision', id: d.id }, b.status === 'approved' ? 'success' : 'info');
  return get('SELECT * FROM project_decisions WHERE id = ?', d.id);
}));
app.post('/api/decisions/:id/supersede', h((req) => {
  const d = get<any>('SELECT * FROM project_decisions WHERE id = ?', req.params.id);
  if (!d) throw bad('Nie znaleziono', 404);
  need(req.body?.title, 'title'); need(req.body?.description, 'description');
  const n = get<{ c: number }>('SELECT COUNT(*) AS c FROM project_decisions')!.c + 1;
  const id = uid('dec-');
  tx(() => {
    insert('project_decisions', { id, code: `D-${String(n).padStart(3, '0')}`, title: req.body.title, description: req.body.description, category: d.category, status: 'approved', proposed_by: 'Game Director', approved_by: 'Game Director', related_docs: d.related_docs, related_tasks: d.related_tasks, supersedes_decision_id: d.id, created_at: now(), approved_at: now(), updated_at: now() });
    update('project_decisions', d.id, { status: 'superseded', updated_at: now() });
  });
  log('Game Director', `Zastąpił decyzję ${d.code}`, req.body.title, { type: 'decision', id }, 'success');
  return get('SELECT * FROM project_decisions WHERE id = ?', id);
}));

// questions
app.get('/api/questions', h(() => all("SELECT * FROM questions ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, created_at DESC")));
app.post('/api/questions', h((req) => {
  need(req.body?.question, 'question');
  const id = uid('Q-');
  insert('questions', { id, question: req.body.question, context: req.body.context ?? null, raised_by: 'Game Director', status: 'open', created_at: now() });
  return get('SELECT * FROM questions WHERE id = ?', id);
}));
app.patch('/api/questions/:id', h((req) => {
  const answer = req.body?.answer;
  update('questions', req.params.id, { answer, status: req.body?.status ?? (answer ? 'answered' : undefined), answered_at: answer ? now() : undefined });
  log('Game Director', 'Odpowiedział na pytanie', String(answer ?? '').slice(0, 200), { type: 'question', id: req.params.id });
  return get('SELECT * FROM questions WHERE id = ?', req.params.id);
}));

// documents
function saveDocVersion(doc: any, content: string, author: string, approved: boolean, note: string, title?: string) {
  const v = doc.version + 1;
  tx(() => {
    update('project_documents', doc.id, { content, title: title ?? doc.title, version: v, approved, author, updated_at: now() });
    insert('document_versions', { id: uid('dv-'), document_id: doc.id, version: v, content, approved, author, note, created_at: now() });
  });
  const src = get<any>('SELECT id FROM brain_sources WHERE origin = ?', `kb:${doc.id}`);
  discoverSources();
  if (src) indexSource(src.id);
}

app.get('/api/documents', h(() => all('SELECT * FROM project_documents ORDER BY category, title')));
app.get('/api/documents/:id', h((req) => {
  const d = get<any>('SELECT * FROM project_documents WHERE id = ?', req.params.id);
  if (!d) throw bad('Nie znaleziono', 404);
  return { ...d, versions: all('SELECT id, version, approved, author, note, created_at FROM document_versions WHERE document_id = ? ORDER BY version DESC', d.id) };
}));
app.get('/api/documents/:id/versions/:version', h((req) => get('SELECT * FROM document_versions WHERE document_id = ? AND version = ?', req.params.id, Number(req.params.version))));
app.post('/api/documents', h((req) => {
  const b = req.body ?? {};
  need(b.title, 'title'); need(b.category, 'category');
  const id = uid('doc-');
  insert('project_documents', { id, title: b.title, category: b.category, content: b.content ?? '', version: 1, approved: false, author: 'Game Director', source: 'dashboard', created_at: now(), updated_at: now() });
  insert('document_versions', { id: uid('dv-'), document_id: id, version: 1, content: b.content ?? '', approved: false, author: 'Game Director', note: 'Utworzenie', created_at: now() });
  discoverSources();
  const src = get<any>('SELECT id FROM brain_sources WHERE origin = ?', `kb:${id}`);
  if (src) indexSource(src.id);
  log('Game Director', 'Utworzył dokument', b.title, { type: 'document', id });
  return get('SELECT * FROM project_documents WHERE id = ?', id);
}));
app.put('/api/documents/:id', h((req) => {
  const d = get<any>('SELECT * FROM project_documents WHERE id = ?', req.params.id);
  if (!d) throw bad('Nie znaleziono', 404);
  if (typeof req.body?.content !== 'string') throw bad('Brak treści');
  saveDocVersion(d, req.body.content, 'Game Director', false, req.body?.note ?? 'Edycja (wymaga zatwierdzenia)', req.body?.title);
  log('Game Director', 'Edytował dokument', `${d.title} → v${d.version + 1} (niezatwierdzona)`, { type: 'document', id: d.id });
  return get('SELECT * FROM project_documents WHERE id = ?', d.id);
}));
app.post('/api/documents/:id/approve', h((req) => {
  const d = get<any>('SELECT * FROM project_documents WHERE id = ?', req.params.id);
  if (!d) throw bad('Nie znaleziono', 404);
  update('project_documents', d.id, { approved: true, updated_at: now() });
  run('UPDATE document_versions SET approved = 1 WHERE document_id = ? AND version = ?', d.id, d.version);
  discoverSources();
  const src = get<any>('SELECT id FROM brain_sources WHERE origin = ?', `kb:${d.id}`);
  if (src) indexSource(src.id);
  log('Game Director', 'Zatwierdził dokument', `${d.title} v${d.version} — teraz kanoniczny`, { type: 'document', id: d.id }, 'success');
  return get('SELECT * FROM project_documents WHERE id = ?', d.id);
}));
app.post('/api/documents/:id/rollback', h((req) => {
  const d = get<any>('SELECT * FROM project_documents WHERE id = ?', req.params.id);
  const v = get<any>('SELECT * FROM document_versions WHERE document_id = ? AND version = ?', req.params.id, Number(need(req.body?.version, 'version')));
  if (!d || !v) throw bad('Nie znaleziono', 404);
  saveDocVersion(d, v.content, 'Game Director (rollback)', v.approved, `Rollback do v${v.version}`);
  log('Game Director', 'Przywrócił wersję dokumentu', `${d.title} → v${v.version}`, { type: 'document', id: d.id }, 'warn');
  return get('SELECT * FROM project_documents WHERE id = ?', d.id);
}));

// ================= export / import =================

const EXPORT_TABLES = ['project', 'agents', 'tasks', 'task_comments', 'approvals', 'assets', 'project_documents', 'document_versions', 'project_decisions', 'brain_updates', 'questions', 'chat_messages', 'workflows', 'workflow_runs', 'ui_elements', 'bugs', 'tests', 'builds', 'agent_executions', 'agent_context_snapshots', 'activity_logs'];
app.get('/api/export', (_req, res) => {
  const data: Record<string, any[]> = {};
  for (const t of EXPORT_TABLES) data[t] = db.prepare(`SELECT * FROM ${t}`).all() as any[];
  const settings = getSettings();
  res.setHeader('Content-Disposition', `attachment; filename="blocky-crycket-studio-${now().slice(0, 10)}.json"`);
  res.json({ format: 'blocky-crycket-studio', version: 1, exportedAt: now(), settings: { ...settings, emergencyStop: false }, data });
});
app.post('/api/import', h((req) => {
  const b = req.body;
  if (b?.format !== 'blocky-crycket-studio' || !b.data) throw bad('To nie jest eksport BLOCKY & CRYCKET Studio');
  tx(() => {
    db.exec('PRAGMA defer_foreign_keys = ON');
    for (const t of [...EXPORT_TABLES].reverse()) db.exec(`DELETE FROM ${t}`);
    for (const t of EXPORT_TABLES) {
      for (const row of b.data[t] ?? []) {
        const keys = Object.keys(row);
        if (!keys.length) continue;
        db.prepare(`INSERT INTO ${t} (${keys.join(',')}) VALUES (${keys.map(() => '?').join(',')})`).run(...keys.map((k) => row[k]));
      }
    }
  });
  if (b.settings) setSettings(b.settings);
  indexAll(false);
  log('Game Director', 'Zaimportował stan projektu', `Eksport z ${b.exportedAt}`, undefined, 'warn');
  return { ok: true };
}));

// ================= static (production) =================

const dist = path.join(DASHBOARD_ROOT, 'dist');
if (fs.existsSync(dist)) {
  app.use(express.static(dist));
  app.get(/^(?!\/api\/).*/, (_req, res) => res.sendFile(path.join(dist, 'index.html')));
}

app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  const status = err?.status ?? 500;
  if (status >= 500) console.error(err);
  res.status(status).json({ error: String(err?.message ?? err) });
});

// ================= boot =================

const seeded = seedIfEmpty();
recoverInterruptedRuns();
run("UPDATE agents SET status = 'idle', current_activity = NULL WHERE status IN ('thinking','working')");
run("UPDATE agent_executions SET status = 'cancelled', error = 'Serwer zrestartowany w trakcie wykonania', finished_at = ? WHERE status = 'running'", now());
run('DELETE FROM file_locks');
const idx = indexAll(!seeded);
console.log(`[studio] Project Brain: ${idx.indexed} zaindeksowanych, ${idx.skipped} bez zmian, ${idx.failed} błędów`);

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[studio] BLOCKY & CRYCKET AI Development Studio API → http://127.0.0.1:${PORT}`);
  console.log(`[studio] AI: ${aiConfigured() ? 'skonfigurowane' : 'NOT CONFIGURED (brak ANTHROPIC_API_KEY w dashboard/.env)'}`);
});
