import fs from 'node:fs';
import path from 'node:path';
import Anthropic from '@anthropic-ai/sdk';
import { all, get, insert, log, now, run, uid, update, getSettings } from './db.ts';
import { buildContext } from './brain.ts';
import { GAME_BRIEF, REPO_BRIEF, TEAM_ROSTER, TEAM_RULES, AGENTS } from './knowledge.ts';
import { isProtectedPath, isWritablePath, normalizeRel, readProjectFile, resolveProjectPath } from './paths.ts';

// ---------------- client ----------------

export function aiConfigured(): boolean {
  return !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
}

let _client: Anthropic | null = null;
function client(): Anthropic {
  if (!aiConfigured()) throw new Error('NOT CONFIGURED: brak ANTHROPIC_API_KEY w dashboard/.env');
  if (!_client) _client = new Anthropic();
  return _client;
}

/** USD per 1M tokens (input, output, cache read). */
export const PRICING: Record<string, { in: number; out: number; cacheRead: number }> = {
  'claude-opus-5-5': { in: 4, out: 20, cacheRead: 0.2 },
  'claude-sonnet-5-5': { in: 2, out: 10, cacheRead: 0.1 },
  'claude-haiku-5-5': { in: 0.1, out: 0.5, cacheRead: 0.01 },
  'claude-fable-5-2': { in: 8, out: 40, cacheRead: 0.2 },
};
export const MODELS = Object.keys(PRICING);

function costOf(model: string, u: { input_tokens?: number | null; output_tokens?: number | null; cache_read_input_tokens?: number | null; cache_creation_input_tokens?: number | null }) {
  const p = PRICING[model] ?? PRICING['claude-opus-5-5'];
  const input = (u.input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0) * 1.25;
  return (input * p.in + (u.output_tokens ?? 0) * p.out + (u.cache_read_input_tokens ?? 0) * p.cacheRead) / 1_000_000;
}

export async function testConnection(model: string) {
  const m = await client().models.retrieve(model);
  return { id: m.id, display_name: m.display_name };
}

// ---------------- output schema ----------------

const AGENT_IDS = AGENTS.map((a) => a.id);
const str = { type: 'string' };
const strArr = { type: 'array', items: { type: 'string' } };
const OUTPUT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['message', 'summary', 'file_changes', 'new_tasks', 'decision_proposals', 'questions', 'assumptions', 'bugs', 'brain_update'],
  properties: {
    message: { type: 'string', description: 'Reply to the Game Director, in Polish.' },
    summary: { type: 'string', description: 'One-paragraph summary of what you did (Polish).' },
    file_changes: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['path', 'content', 'explanation'],
        properties: { path: str, content: { type: 'string', description: 'COMPLETE new file content' }, explanation: str },
      },
    },
    new_tasks: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['title', 'description', 'assigned_agent', 'priority'],
        properties: { title: str, description: str, assigned_agent: { type: 'string', enum: AGENT_IDS }, priority: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] } },
      },
    },
    decision_proposals: {
      type: 'array',
      items: { type: 'object', additionalProperties: false, required: ['title', 'description', 'category'], properties: { title: str, description: str, category: { type: 'string', enum: ['game_design', 'art_direction', 'technical', 'ui', 'economy', 'roadmap', 'tooling'] } } },
    },
    questions: strArr,
    assumptions: strArr,
    bugs: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['title', 'description', 'severity', 'category', 'related_file', 'repro_steps'],
        properties: { title: str, description: str, severity: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] }, category: { type: 'string', enum: ['ui', 'luau', 'gameplay', 'performance', 'assets', 'integration'] }, related_file: str, repro_steps: str },
      },
    },
    brain_update: {
      type: 'object', additionalProperties: false,
      required: ['what_changed', 'why', 'files_affected', 'tests_performed', 'new_facts', 'docs_to_update'],
      properties: { what_changed: str, why: str, files_affected: strArr, tests_performed: str, new_facts: strArr, docs_to_update: strArr },
    },
  },
} as const;

export interface AgentOutput {
  message: string; summary: string;
  file_changes: { path: string; content: string; explanation: string }[];
  new_tasks: { title: string; description: string; assigned_agent: string; priority: string }[];
  decision_proposals: { title: string; description: string; category: string }[];
  questions: string[]; assumptions: string[];
  bugs: { title: string; description: string; severity: string; category: string; related_file: string; repro_steps: string }[];
  brain_update: { what_changed: string; why: string; files_affected: string[]; tests_performed: string; new_facts: string[]; docs_to_update: string[] };
}

// ---------------- run control ----------------

const controllers = new Map<string, AbortController>();

export function emergencyStop() {
  for (const [, c] of controllers) c.abort(new Error('EMERGENCY STOP'));
  const n = controllers.size;
  run("UPDATE agents SET status = 'idle', current_activity = NULL WHERE status IN ('thinking','working')");
  run("UPDATE workflow_runs SET status = 'stopped', updated_at = ? WHERE status IN ('running','queued')", now());
  run('DELETE FROM file_locks');
  return n;
}

export function runningCount() {
  return controllers.size;
}

function totalSpend(): number {
  return get<{ s: number }>('SELECT COALESCE(SUM(cost_usd),0) AS s FROM agent_executions')?.s ?? 0;
}

// ---------------- execution ----------------

export interface ExecuteOptions {
  agentId: string;
  prompt: string;
  taskId?: string | null;
  workflowRunId?: string | null;
  chatMessageId?: string | null;
  relatedFiles?: string[];
  extraContext?: string;
}

/** Creates an execution record and runs it in the background. Returns the execution id immediately. */
export function startExecution(opts: ExecuteOptions): { executionId: string; done: Promise<void> } {
  const settings = getSettings();
  const agent = get<any>('SELECT * FROM agents WHERE id = ?', opts.agentId);
  if (!agent) throw new Error('Nieznany agent');
  if (settings.emergencyStop) throw new Error('EMERGENCY STOP jest aktywny — wyłącz go w nagłówku, aby uruchamiać agentów.');
  if (!agent.enabled) throw new Error(`${agent.name} jest wstrzymany (Offline).`);
  if (!aiConfigured()) throw new Error('NOT CONFIGURED: dodaj ANTHROPIC_API_KEY do dashboard/.env i zrestartuj serwer.');
  if (totalSpend() >= settings.costLimitUsd) throw new Error(`Osiągnięto limit kosztów API (${settings.costLimitUsd} USD). Zmień go w AI Configuration.`);

  const id = uid('EX-');
  insert('agent_executions', {
    id, agent_id: agent.id, task_id: opts.taskId ?? null, workflow_run_id: opts.workflowRunId ?? null, chat_message_id: opts.chatMessageId ?? null,
    prompt: opts.prompt, status: 'running', model: agent.model, started_at: now(),
  });
  const done = execute(id, agent, opts).catch(() => undefined);
  return { executionId: id, done };
}

async function execute(executionId: string, agent: any, opts: ExecuteOptions) {
  const settings = getSettings();
  const started = Date.now();
  const controller = new AbortController();
  controllers.set(executionId, controller);
  const timer = setTimeout(() => controller.abort(new Error(`Przekroczono limit czasu (${settings.timeLimitSec}s)`)), settings.timeLimitSec * 1000);

  const task = opts.taskId ? get<any>('SELECT * FROM tasks WHERE id = ?', opts.taskId) : null;
  const relatedFiles = Array.from(new Set([...(opts.relatedFiles ?? []), ...((task?.related_files as string[]) ?? [])]));
  const locked: string[] = [];

  try {
    update('agents', agent.id, { status: 'thinking', current_activity: `Pobiera kontekst: ${opts.prompt.slice(0, 80)}`, updated_at: now() });

    // file locks
    for (const f of relatedFiles) {
      let rel: string;
      try { rel = normalizeRel(f); } catch { continue; }
      const lock = get<any>('SELECT * FROM file_locks WHERE path = ?', rel);
      if (lock && lock.execution_id !== executionId) continue;
      run('INSERT OR REPLACE INTO file_locks (path, owner_agent_id, execution_id, locked_at) VALUES (?,?,?,?)', rel, agent.id, executionId, now());
      locked.push(rel);
    }

    // Project Brain context
    const taskText = task ? `TASK ${task.id}: ${task.title}\n${task.description}` : '';
    const ctx = buildContext({ agentId: agent.id, agentRole: agent.role, task: `${taskText}\n${opts.prompt}`, relatedFiles, extra: opts.extraContext });
    insert('agent_context_snapshots', {
      id: uid('ctx-'), agent_execution_id: executionId, retrieved_source_ids: ctx.sourceIds,
      retrieved_chunks: ctx.chunks.map((c) => ({ chunkId: c.chunkId, sourceId: c.sourceId, sourceName: c.sourceName, heading: c.heading, score: c.score, preview: c.content.slice(0, 280) })),
      decisions: ctx.decisions, query: ctx.query, context_summary: ctx.summary, context_text: ctx.text, created_at: now(),
    });

    update('agents', agent.id, { status: 'working', current_activity: opts.prompt.slice(0, 120), updated_at: now() });

    const system = [
      agent.instructions,
      `TEAM:\n${TEAM_ROSTER}`,
      TEAM_RULES,
      GAME_BRIEF,
      REPO_BRIEF,
      `AUTONOMY MODE: ${settings.autonomyMode}. File changes you return are ${settings.autonomyMode === 'assistant' ? 'always queued for human approval' : 'applied automatically only when permitted by policy; protected files always need approval'}.`,
    ].join('\n\n');

    const userContent = `# PROJECT BRAIN CONTEXT\n${ctx.text}\n\n# ${task ? 'ASSIGNED TASK' : 'REQUEST FROM THE GAME DIRECTOR'}\n${taskText}\n${opts.prompt}`;

    const params: Anthropic.Beta.Messages.MessageCreateParamsStreaming = {
      model: agent.model,
      max_tokens: 64000,
      stream: true,
      betas: ['server-side-fallback-2026-07-01'],
      fallbacks: 'default',
      cache_control: { type: 'ephemeral' },
      system,
      output_config: { effort: agent.effort, format: { type: 'json_schema', schema: OUTPUT_SCHEMA as any } },
      messages: [{ role: 'user', content: userContent }],
    } as any;

    const stream = client().beta.messages.stream(params as any, { signal: controller.signal });
    const msg = await stream.finalMessage();

    const usage: any = msg.usage ?? {};
    const cost = costOf(agent.model, usage);
    const base = {
      model: msg.model ?? agent.model, input_tokens: (usage.input_tokens ?? 0) + (usage.cache_creation_input_tokens ?? 0),
      output_tokens: usage.output_tokens ?? 0, cache_read_tokens: usage.cache_read_input_tokens ?? 0, cost_usd: cost,
      duration_ms: Date.now() - started, finished_at: now(),
    };

    if (msg.stop_reason === 'refusal') {
      const d: any = (msg as any).stop_details;
      throw Object.assign(new Error(`Model odmówił wykonania (kategoria: ${d?.category ?? 'brak'}). ${d?.explanation ?? ''}`), { base });
    }
    if (msg.stop_reason === 'max_tokens') throw Object.assign(new Error('Odpowiedź przekroczyła max_tokens — podziel zadanie na mniejsze.'), { base });

    const text = msg.content.filter((b: any) => b.type === 'text').map((b: any) => b.text).join('');
    let out: AgentOutput;
    try { out = JSON.parse(text); } catch { throw Object.assign(new Error('Nieprawidłowy JSON w odpowiedzi agenta.'), { base }); }

    const processed = processOutput(executionId, agent, out, task, opts.workflowRunId ?? null);
    update('agent_executions', executionId, { ...base, status: 'completed', result: { ...out, processed } });
    update('agents', agent.id, { status: processed.approvals > 0 ? 'waiting_approval' : 'idle', current_activity: processed.approvals > 0 ? `Czeka na zatwierdzenie ${processed.approvals} zmian` : null, updated_at: now() });
    log(agent.name, 'Zakończył zadanie', `${out.summary}`.slice(0, 500), { type: 'execution', id: executionId }, 'success');
  } catch (e: any) {
    const aborted = controller.signal.aborted;
    const message = aborted ? String((controller.signal.reason as any)?.message ?? 'Przerwano') : errorMessage(e);
    update('agent_executions', executionId, { ...(e?.base ?? { finished_at: now(), duration_ms: Date.now() - started }), status: aborted ? 'cancelled' : 'failed', error: message });
    update('agents', agent.id, { status: aborted ? 'idle' : 'error', current_activity: aborted ? null : message.slice(0, 200), updated_at: now() });
    log(agent.name, aborted ? 'Wykonanie przerwane' : 'Błąd wykonania', message, { type: 'execution', id: executionId }, aborted ? 'warn' : 'error');
    throw e;
  } finally {
    clearTimeout(timer);
    controllers.delete(executionId);
    for (const p of locked) run('DELETE FROM file_locks WHERE path = ? AND execution_id = ?', p, executionId);
  }
}

function errorMessage(e: any): string {
  if (e instanceof Anthropic.AuthenticationError) return 'Nieprawidłowy klucz API (401).';
  if (e instanceof Anthropic.PermissionDeniedError) return 'Brak uprawnień do modelu (403).';
  if (e instanceof Anthropic.NotFoundError) return 'Nie znaleziono modelu (404) — sprawdź nazwę modelu w AI Configuration.';
  if (e instanceof Anthropic.RateLimitError) return 'Limit zapytań API (429) — spróbuj za chwilę.';
  if (e instanceof Anthropic.BadRequestError) return `Błędne zapytanie (400): ${e.message}`;
  if (e instanceof Anthropic.APIConnectionError) return 'Brak połączenia z API Anthropic.';
  if (e instanceof Anthropic.APIError) return `Błąd API ${e.status}: ${e.message}`;
  return String(e?.message ?? e);
}

// ---------------- output processing ----------------

function processOutput(executionId: string, agent: any, out: AgentOutput, task: any, workflowRunId: string | null) {
  const settings = getSettings();
  const t = now();
  let approvals = 0, applied = 0, tasks = 0, decisions = 0, bugs = 0, rejected: string[] = [];

  for (const fc of out.file_changes ?? []) {
    let rel: string;
    try { rel = normalizeRel(fc.path); } catch (e: any) { rejected.push(`${fc.path}: ${e.message}`); continue; }
    if (!isWritablePath(rel)) { rejected.push(`${rel}: ścieżka poza dozwolonymi folderami`); continue; }
    const before = readProjectFile(rel);
    if (before === fc.content) continue;
    const prot = isProtectedPath(rel, settings.protectedFiles);
    const lock = get<any>('SELECT * FROM file_locks WHERE path = ? AND execution_id != ?', rel, executionId);
    const canWrite = !!agent.permissions?.write_files;
    const auto = canWrite && !prot && !lock && (
      settings.autonomyMode === 'autonomous' || (settings.autonomyMode === 'semi' && before === null)
    );
    if (auto) {
      writeProjectFile(rel, fc.content, agent.name, null, fc.explanation);
      applied++;
    } else {
      insert('approvals', {
        id: uid('AP-'), task_id: task?.id ?? null, agent_id: agent.id, execution_id: executionId, workflow_run_id: workflowRunId,
        change_type: 'file', title: `${before === null ? 'Nowy plik' : 'Zmiana'}: ${rel}`, explanation: fc.explanation,
        proposed_changes: { path: rel, before, after: fc.content, protected: prot, agentCanWrite: canWrite }, status: 'pending',
        conflict: !!lock, created_at: t,
      });
      approvals++;
    }
  }

  if (agent.permissions?.create_tasks) {
    for (const nt of out.new_tasks ?? []) {
      insert('tasks', {
        id: uid('T-'), title: nt.title, description: nt.description, assigned_agent_id: AGENT_IDS.includes(nt.assigned_agent) ? nt.assigned_agent : null,
        status: 'backlog', priority: nt.priority, dependencies: [], related_files: [], related_docs: [], brain_source_ids: [], sprint: false,
        phase: task?.phase ?? 'phase1', parent_id: task?.id ?? null, created_by: agent.name, created_at: t, updated_at: t,
      });
      tasks++;
    }
  }

  if (agent.permissions?.propose_decisions) {
    for (const d of out.decision_proposals ?? []) {
      const n = (get<{ c: number }>('SELECT COUNT(*) AS c FROM project_decisions')?.c ?? 0) + 1;
      insert('project_decisions', {
        id: uid('dec-'), code: `D-${String(n).padStart(3, '0')}`, title: d.title, description: d.description, category: d.category,
        status: 'awaiting_approval', proposed_by: agent.name, related_docs: [], related_tasks: task ? [task.id] : [], created_at: t, updated_at: t,
      });
      decisions++;
    }
  }

  for (const q of out.questions ?? []) insert('questions', { id: uid('Q-'), question: q, context: `Execution ${executionId}`, raised_by: agent.name, status: 'open', created_at: t });

  if (agent.permissions?.report_bugs) {
    for (const b of out.bugs ?? []) {
      insert('bugs', {
        id: uid('BUG-'), title: b.title, description: b.description, severity: b.severity, category: b.category, assigned_agent_id: 'lucius',
        related_files: b.related_file ? [b.related_file] : [], repro_steps: b.repro_steps, status: 'open', reported_by: agent.name, created_at: t, updated_at: t,
      });
      bugs++;
    }
  }

  const bu = out.brain_update;
  if (bu && (bu.new_facts?.length || bu.docs_to_update?.length || bu.what_changed)) {
    insert('brain_updates', { id: uid('BU-'), agent_execution_id: executionId, agent_id: agent.id, proposed_changes: { ...bu, assumptions: out.assumptions ?? [] }, status: 'pending', created_at: t });
  }

  if (task && approvals > 0 && task.status !== 'completed') update('tasks', task.id, { status: 'waiting_approval', updated_at: t });
  else if (task && applied > 0 && task.status !== 'completed') update('tasks', task.id, { status: 'testing', updated_at: t });

  return { approvals, applied, tasks, decisions, bugs, rejected };
}

// ---------------- file writes with version history ----------------

export function writeProjectFile(rel: string, content: string, author: string, approvalId: string | null, note?: string) {
  if (!isWritablePath(rel)) throw new Error(`Zapis do ${rel} jest niedozwolony`);
  const abs = resolveProjectPath(rel);
  const before = fs.existsSync(abs) ? fs.readFileSync(abs, 'utf8') : null;
  insert('file_versions', { id: uid('FV-'), path: rel, content: before, author, approval_id: approvalId, note: note ?? 'Stan przed zmianą', created_at: now() });
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, content, 'utf8');
  log(author, before === null ? 'Utworzył plik' : 'Zmodyfikował plik', rel, { type: 'file', id: rel }, 'success');
}

export function deleteProjectFile(rel: string, author: string) {
  if (!isWritablePath(rel)) throw new Error(`Usunięcie ${rel} jest niedozwolone`);
  const abs = resolveProjectPath(rel);
  if (!fs.existsSync(abs)) return;
  insert('file_versions', { id: uid('FV-'), path: rel, content: fs.readFileSync(abs, 'utf8'), author, note: 'Stan przed usunięciem', created_at: now() });
  fs.unlinkSync(abs);
  log(author, 'Usunął plik', rel, { type: 'file', id: rel }, 'warn');
}

// ---------------- style check (real image analysis) ----------------

export async function styleCheckAsset(assetId: string) {
  const asset = get<any>('SELECT * FROM assets WHERE id = ?', assetId);
  if (!asset) throw new Error('Nie znaleziono assetu');
  if (!asset.preview_path) throw new Error('Asset nie ma podglądu (pliku obrazu) do analizy.');
  const abs = resolveProjectPath(asset.preview_path);
  if (!fs.existsSync(abs)) throw new Error('Plik podglądu nie istnieje.');
  const ext = path.extname(abs).toLowerCase();
  const media = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : ext === '.gif' ? 'image/gif' : ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : null;
  if (!media) throw new Error('Analiza obsługuje PNG, JPG, WEBP i GIF.');
  const settings = getSettings();
  if (settings.emergencyStop) throw new Error('EMERGENCY STOP jest aktywny.');
  const keys = ['outlines', 'saturated', 'voxel', 'pixel_icons', 'halftone', 'cel_shading', 'proportions', 'characters'];
  const schema = {
    type: 'object', additionalProperties: false, required: ['checklist', 'verdict', 'report'],
    properties: {
      checklist: { type: 'object', additionalProperties: false, required: keys, properties: Object.fromEntries(keys.map((k) => [k, { type: 'string', enum: ['pass', 'fail', 'not_applicable'] }])) },
      verdict: { type: 'string', enum: ['compliant', 'needs_review', 'inconsistent'] },
      report: { type: 'string' },
    },
  };
  const started = Date.now();
  const msg = await client().beta.messages.create({
    model: 'claude-opus-5-5', max_tokens: 4000, betas: ['server-side-fallback-2026-07-01'], fallbacks: 'default',
    output_config: { effort: 'medium', format: { type: 'json_schema', schema } },
    system: `You are LOREKEEPER, Style Lock guardian of the Roblox game BLOCKY & CRYCKET.\n${GAME_BRIEF}\nEvaluate the image strictly against the Style Lock. Report in Polish.`,
    messages: [{ role: 'user', content: [
      { type: 'image', source: { type: 'base64', media_type: media as any, data: fs.readFileSync(abs).toString('base64') } },
      { type: 'text', text: `Asset: ${asset.name} (${asset.category}). Generation prompt: ${asset.prompt ?? '—'}\nChecklist keys: outlines (thick black 3-4px), saturated (vivid colors), voxel (Roblox blocky geometry), pixel_icons (crisp pixel-art for UI icons), halftone, cel_shading, proportions (exaggerated), characters (matches canonical designs). Use not_applicable when a criterion doesn't apply to this asset type.` },
    ] }],
  } as any);
  if ((msg as any).stop_reason === 'refusal') throw new Error('Model odmówił analizy obrazu.');
  const text = (msg as any).content.filter((b: any) => b.type === 'text').map((b: any) => b.text).join('');
  const r = JSON.parse(text);
  const cost = costOf('claude-opus-5-5', (msg as any).usage ?? {});
  insert('agent_executions', {
    id: uid('EX-'), agent_id: 'lorekeeper', prompt: `Style Lock check: ${asset.name}`, status: 'completed', model: 'claude-opus-5-5',
    started_at: new Date(started).toISOString(), finished_at: now(), result: { message: r.report, summary: `Style check: ${r.verdict}` },
    input_tokens: (msg as any).usage?.input_tokens ?? 0, output_tokens: (msg as any).usage?.output_tokens ?? 0, cost_usd: cost, duration_ms: Date.now() - started,
  });
  update('assets', assetId, { style_checklist: r.checklist, style_compliance: r.verdict, style_report: r.report, updated_at: now() });
  log('LOREKEEPER', 'Analiza Style Lock', `${asset.name}: ${r.verdict}`, { type: 'asset', id: assetId }, r.verdict === 'compliant' ? 'success' : 'warn');
  return r;
}

export function listExecutions(limit = 100) {
  return all('SELECT e.*, a.name AS agent_name, a.color AS agent_color FROM agent_executions e JOIN agents a ON a.id = e.agent_id ORDER BY e.started_at DESC LIMIT ?', limit);
}
