import { all, get, insert, log, now, uid, update, getSettings } from './db.ts';
import { buildContext } from './brain.ts';
import { startExecution } from './agents.ts';
import { rojoStatus } from './integrations.ts';

interface WfNode { id: string; type: 'input' | 'agent' | 'brain' | 'approval' | 'sync'; label: string; agentId: string | null }
interface StepResult { nodeId: string; status: 'completed' | 'failed' | 'skipped' | 'waiting' | 'running'; executionId?: string; summary?: string; at: string }

const active = new Set<string>();

export function startWorkflow(workflowId: string, input: string, taskId: string | null) {
  const wf = get<any>('SELECT * FROM workflows WHERE id = ?', workflowId);
  if (!wf) throw new Error('Nie znaleziono workflow');
  const s = getSettings();
  if (s.emergencyStop) throw new Error('EMERGENCY STOP jest aktywny.');
  const id = uid('WR-');
  insert('workflow_runs', { id, workflow_id: workflowId, input, task_id: taskId, status: 'running', current_step: 0, step_results: [], created_at: now(), updated_at: now() });
  log('Workflow', 'Uruchomiono workflow', `${wf.name}: ${input.slice(0, 200)}`, { type: 'workflow_run', id });
  void advance(id);
  return id;
}

export function resumeWorkflow(runId: string) {
  const r = get<any>('SELECT * FROM workflow_runs WHERE id = ?', runId);
  if (!r) throw new Error('Nie znaleziono przebiegu');
  if (r.status !== 'waiting_approval' && r.status !== 'failed' && r.status !== 'stopped') throw new Error(`Przebieg ma status ${r.status}`);
  if (getSettings().emergencyStop) throw new Error('EMERGENCY STOP jest aktywny.');
  if (r.status === 'waiting_approval') {
    const pending = get<{ c: number }>("SELECT COUNT(*) AS c FROM approvals WHERE workflow_run_id = ? AND status = 'pending'", runId)?.c ?? 0;
    if (pending > 0) throw new Error(`Najpierw rozpatrz ${pending} oczekujących zatwierdzeń tego przebiegu.`);
    const steps: StepResult[] = r.step_results;
    steps.push({ nodeId: (get<any>('SELECT nodes FROM workflows WHERE id = ?', r.workflow_id)!.nodes as WfNode[])[r.current_step].id, status: 'completed', summary: 'Zatwierdzone przez człowieka', at: now() });
    update('workflow_runs', runId, { status: 'running', current_step: r.current_step + 1, step_results: steps, updated_at: now() });
  } else {
    update('workflow_runs', runId, { status: 'running', error: null, updated_at: now() });
  }
  void advance(runId);
}

export function stopWorkflow(runId: string) {
  update('workflow_runs', runId, { status: 'stopped', updated_at: now() });
}

async function advance(runId: string) {
  if (active.has(runId)) return;
  active.add(runId);
  try {
    const settings = getSettings();
    let agentSteps = 0;
    for (;;) {
      const r = get<any>('SELECT * FROM workflow_runs WHERE id = ?', runId)!;
      if (r.status !== 'running') return;
      if (getSettings().emergencyStop) { update('workflow_runs', runId, { status: 'stopped', error: 'EMERGENCY STOP', updated_at: now() }); return; }
      const wf = get<any>('SELECT * FROM workflows WHERE id = ?', r.workflow_id)!;
      const nodes: WfNode[] = wf.nodes;
      if (r.current_step >= nodes.length) {
        update('workflow_runs', runId, { status: 'completed', updated_at: now() });
        log('Workflow', 'Workflow zakończony', wf.name, { type: 'workflow_run', id: runId }, 'success');
        return;
      }
      const node = nodes[r.current_step];
      const steps: StepResult[] = r.step_results;
      const push = (s: Omit<StepResult, 'nodeId' | 'at'>) => { steps.push({ nodeId: node.id, at: now(), ...s }); };

      if (node.type === 'input') {
        push({ status: 'completed', summary: r.input.slice(0, 200) });
      } else if (node.type === 'brain') {
        const ctx = buildContext({ agentId: 'atlas', agentRole: 'workflow', task: r.input });
        push({ status: 'completed', summary: `Project Brain: ${ctx.summary} Źródła: ${ctx.chunks.map((c) => c.sourceName).slice(0, 5).join(', ')}` });
      } else if (node.type === 'approval') {
        const pending = get<{ c: number }>("SELECT COUNT(*) AS c FROM approvals WHERE workflow_run_id = ? AND status = 'pending'", runId)?.c ?? 0;
        if (pending > 0) {
          update('workflow_runs', runId, { status: 'waiting_approval', step_results: steps, updated_at: now() });
          log('Workflow', 'Czeka na zatwierdzenie', `${pending} zmian do przejrzenia`, { type: 'workflow_run', id: runId }, 'warn');
          return;
        }
        push({ status: 'completed', summary: 'Brak zmian wymagających zatwierdzenia' });
      } else if (node.type === 'sync') {
        const rs = await rojoStatus();
        push({ status: 'completed', summary: rs.connected ? `Rojo serve działa (${rs.projectName}) — zatwierdzone pliki są synchronizowane do Studio na żywo.` : 'Rojo serve NIE działa — uruchom `rojo serve`, aby zsynchronizować zmiany ze Studio.' });
      } else if (node.type === 'agent' && node.agentId) {
        agentSteps++;
        if (agentSteps > settings.maxIterations) {
          update('workflow_runs', runId, { status: 'failed', error: `Przekroczono maksymalną liczbę iteracji (${settings.maxIterations})`, step_results: steps, updated_at: now() });
          return;
        }
        const previous = steps.filter((s) => s.summary && s.executionId).map((s) => {
          const n = nodes.find((x) => x.id === s.nodeId);
          return `- ${n?.label}: ${s.summary}`;
        }).join('\n');
        const filesSoFar = all<any>('SELECT proposed_changes FROM approvals WHERE workflow_run_id = ?', runId).map((a) => a.proposed_changes?.path).filter(Boolean);
        let exec;
        try {
          exec = startExecution({
            agentId: node.agentId, workflowRunId: runId, taskId: r.task_id,
            prompt: `Workflow "${wf.name}", step "${node.label}".\nOriginal request: ${r.input}\n\nYour job in this step: act strictly within your role. Build on previous steps; do not repeat their work.`,
            extraContext: previous ? `PREVIOUS WORKFLOW STEPS:\n${previous}` : undefined,
            relatedFiles: filesSoFar,
          });
        } catch (e: any) {
          update('workflow_runs', runId, { status: 'failed', error: e.message, step_results: steps, updated_at: now() });
          return;
        }
        steps.push({ nodeId: node.id, status: 'running', executionId: exec.executionId, at: now() });
        update('workflow_runs', runId, { step_results: steps, updated_at: now() });
        await exec.done;
        const ex = get<any>('SELECT * FROM agent_executions WHERE id = ?', exec.executionId)!;
        steps.pop();
        if (ex.status !== 'completed') {
          steps.push({ nodeId: node.id, status: 'failed', executionId: ex.id, summary: ex.error, at: now() });
          update('workflow_runs', runId, { status: ex.status === 'cancelled' ? 'stopped' : 'failed', error: ex.error, step_results: steps, updated_at: now() });
          return;
        }
        steps.push({ nodeId: node.id, status: 'completed', executionId: ex.id, summary: ex.result?.summary ?? '', at: now() });
      } else {
        push({ status: 'skipped' });
      }
      update('workflow_runs', runId, { current_step: r.current_step + 1, step_results: steps, updated_at: now() });
    }
  } catch (e: any) {
    update('workflow_runs', runId, { status: 'failed', error: String(e?.message ?? e), updated_at: now() });
  } finally {
    active.delete(runId);
  }
}

/** On server restart, runs that were mid-flight cannot continue in-process. */
export function recoverInterruptedRuns() {
  for (const r of all<any>("SELECT id FROM workflow_runs WHERE status = 'running'")) {
    update('workflow_runs', r.id, { status: 'stopped', error: 'Serwer został zrestartowany w trakcie przebiegu — wznów ręcznie.', updated_at: now() });
  }
}
