import { useMemo, useState } from 'react';
import { ReactFlow, Background, Controls, Handle, Position, type Node, type Edge, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Workflow, Play, Square, RotateCw, User, Brain, CheckCheck, Radio, Bot } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Field, PageHeader, Select, Spinner, Textarea, useAction, cx, NotConfigured } from '../components/ui';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

const RUN_STATUS: Record<string, { label: string; color: string }> = {
  running: { label: 'W toku', color: '#22d3ee' }, waiting_approval: { label: 'Czeka na zatwierdzenie', color: '#f5c542' },
  completed: { label: 'Ukończony', color: '#34d399' }, failed: { label: 'Błąd', color: '#f05252' }, stopped: { label: 'Zatrzymany', color: '#8a93a6' },
};
const STEP_COLOR: Record<string, string> = { completed: '#34d399', running: '#22d3ee', failed: '#f05252', waiting: '#f5c542', skipped: '#5d6678' };
const TYPE_ICON: Record<string, any> = { input: User, agent: Bot, brain: Brain, approval: CheckCheck, sync: Radio };

function FlowNode({ data }: { data: any }) {
  const Icon = TYPE_ICON[data.type] ?? Bot;
  const color = data.state ? STEP_COLOR[data.state] : data.color ?? '#5d6678';
  return (
    <div className={cx('w-[180px] rounded-lg border-2 bg-panel2 px-3 py-2 text-ink', data.state === 'running' && 'pulse-ring')} style={{ borderColor: color }}>
      <Handle type="target" position={Position.Left} style={{ background: '#323a4a', border: 0 }} />
      <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider" style={{ color }}><Icon size={12} />{data.type}</div>
      <div className="mt-0.5 text-[12px] font-medium leading-tight">{data.label}</div>
      {data.state && <div className="mt-1 text-[10px]" style={{ color }}>{data.state}</div>}
      <Handle type="source" position={Position.Right} style={{ background: '#323a4a', border: 0 }} />
    </div>
  );
}
const nodeTypes = { step: FlowNode };

export function Workflows() {
  const { data: wfs, error } = useApi<any[]>('/workflows');
  const { data: runs, reload } = useApi<any[]>('/workflow-runs', 2500);
  const { data: tasks } = useApi<any[]>('/tasks');
  const { data: agents } = useApi<any[]>('/agents');
  const { status } = useStatus();
  const [sel, setSel] = useState('wf-ui');
  const [runSel, setRunSel] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [taskId, setTaskId] = useState('');
  const [exec, setExec] = useState<string | null>(null);

  const start = useAction(() => api<{ runId: string }>(`/workflows/${sel}/run`, { body: { input, taskId: taskId || null } }), { success: 'Workflow uruchomiony', onDone: (r) => { setInput(''); setRunSel(r.runId); reload(); } });
  const resume = useAction((id: string) => api(`/workflow-runs/${id}/resume`, { body: {} }), { success: 'Wznowiono', onDone: reload });
  const stop = useAction((id: string) => api(`/workflow-runs/${id}/stop`, { body: {} }), { success: 'Zatrzymano', onDone: reload });

  const wf = wfs?.find((w) => w.id === sel);
  const run = runs?.find((r) => r.id === runSel && r.workflow_id === sel) ?? null;

  const { nodes, edges } = useMemo(() => {
    if (!wf) return { nodes: [], edges: [] };
    const perRow = 5;
    const stepState = (nodeId: string) => {
      if (!run) return undefined;
      const s = [...(run.step_results ?? [])].reverse().find((x: any) => x.nodeId === nodeId);
      if (s) return s.status;
      const idx = wf.nodes.findIndex((n: any) => n.id === nodeId);
      if (run.status === 'waiting_approval' && idx === run.current_step) return 'waiting';
      return undefined;
    };
    const nodes: Node[] = wf.nodes.map((n: any, i: number) => {
      const row = Math.floor(i / perRow); const col = row % 2 === 0 ? i % perRow : perRow - 1 - (i % perRow);
      return { id: n.id, type: 'step', position: { x: col * 225, y: row * 120 }, data: { ...n, state: stepState(n.id), color: n.agentId ? agents?.find((a) => a.id === n.agentId)?.color : undefined } };
    });
    const edges: Edge[] = wf.nodes.slice(1).map((n: any, i: number) => ({ id: `e${i}`, source: wf.nodes[i].id, target: n.id, animated: stepState(n.id) === 'running', markerEnd: { type: MarkerType.ArrowClosed, color: '#4b5568' }, style: { stroke: '#4b5568' } }));
    return { nodes, edges };
  }, [wf, run, agents]);

  if (error) return <ErrorBox error={error} />;
  if (!wfs) return <Spinner />;

  return (
    <div>
      <PageHeader icon={<Workflow size={20} className="text-gold" />} title="Workflows" subtitle="Predefiniowane przepływy pracy zespołu. Każdy krok agenta to prawdziwe wykonanie z kontekstem Project Brain; krok „Zatwierdzenie człowieka” wstrzymuje przebieg, dopóki nie rozpatrzysz zmian." actions={!status?.ai.configured && <NotConfigured />} />
      <div className="mb-4 flex flex-wrap gap-2">
        {wfs.map((w) => <Button key={w.id} variant={w.id === sel ? 'primary' : 'secondary'} onClick={() => { setSel(w.id); setRunSel(null); }}>{w.name}</Button>)}
      </div>
      <div className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <Card title={wf?.name} actions={run && <Badge color={RUN_STATUS[run.status]?.color}>{RUN_STATUS[run.status]?.label} · {run.id}</Badge>} bodyClass="p-0">
          <div className="h-[330px]">
            <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView fitViewOptions={{ padding: 0.15 }} nodesDraggable={false} nodesConnectable={false} proOptions={{ hideAttribution: true }}>
              <Background color="#252c39" gap={18} />
              <Controls showInteractive={false} />
            </ReactFlow>
          </div>
          <div className="border-t border-line px-4 py-2 text-[12px] text-mute">{wf?.description}</div>
          {run && (
            <div className="border-t border-line p-4">
              <div className="mb-2 flex items-center justify-between">
                <div className="text-xs text-mute">Przebieg: <span className="text-ink">{run.input}</span></div>
                <div className="flex gap-1.5">
                  {['waiting_approval', 'failed', 'stopped'].includes(run.status) && <Button size="sm" variant="success" icon={<RotateCw size={12} />} loading={resume.loading} onClick={() => resume.run(run.id)}>{run.status === 'waiting_approval' ? 'Kontynuuj po zatwierdzeniu' : 'Wznów'}</Button>}
                  {run.status === 'running' && <Button size="sm" variant="danger" icon={<Square size={12} />} loading={stop.loading} onClick={() => stop.run(run.id)}>Zatrzymaj</Button>}
                </div>
              </div>
              {run.error && <div className="mb-2"><ErrorBox error={run.error} /></div>}
              <ol className="space-y-1.5">
                {(run.step_results ?? []).map((s: any, i: number) => {
                  const node = wf?.nodes.find((n: any) => n.id === s.nodeId);
                  return (
                    <li key={i} className="flex items-start gap-2 text-[12px]">
                      <span className="mt-1 h-2 w-2 shrink-0 rounded-full" style={{ background: STEP_COLOR[s.status] }} />
                      <span className="min-w-0 flex-1"><b>{node?.label}</b> <span className="text-mute">— {s.summary ?? s.status}</span></span>
                      {s.executionId && <button className="shrink-0 text-cyan hover:underline cursor-pointer" onClick={() => setExec(s.executionId)}>szczegóły</button>}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
        </Card>
        <div className="space-y-5">
          <Card title="Uruchom przebieg" icon={<Play size={14} className="text-mint" />}>
            <div className="space-y-3">
              <Field label={sel === 'wf-bug' ? 'Opis błędu' : 'Prośba'}><Textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="np. Zbuduj pasek HP w lewym górnym rogu HUD z animacją obrażeń" /></Field>
              <Field label="Powiązane zadanie (opcjonalnie)">
                <Select value={taskId} onChange={(e) => setTaskId(e.target.value)}><option value="">— brak —</option>{(tasks ?? []).filter((t) => t.status !== 'completed').map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}</Select>
              </Field>
              <Button variant="primary" className="w-full" icon={<Play size={14} />} loading={start.loading} disabled={!input.trim() || !status?.ai.configured || status?.emergencyStop} onClick={() => start.run()}>Uruchom {wf?.name.split('—')[0]}</Button>
              <p className="text-[11px] text-faint">Każdy krok agenta kosztuje tokeny. Limit iteracji i kosztów ustawisz w AI Configuration.</p>
            </div>
          </Card>
          <Card title="Przebiegi">
            {(runs ?? []).filter((r) => r.workflow_id === sel).length === 0 ? <Empty title="Brak przebiegów" /> : (
              <ul className="space-y-1.5">
                {(runs ?? []).filter((r) => r.workflow_id === sel).map((r) => (
                  <li key={r.id}>
                    <button onClick={() => setRunSel(r.id)} className={cx('w-full rounded-md border px-2.5 py-2 text-left cursor-pointer', runSel === r.id ? 'border-gold/50 bg-gold/5' : 'border-line hover:border-line2')}>
                      <div className="flex items-center justify-between gap-2"><span className="truncate text-[12px]">{r.input}</span><Badge color={RUN_STATUS[r.status]?.color}>{RUN_STATUS[r.status]?.label}</Badge></div>
                      <div className="text-[10.5px] text-faint">{fmtDateTime(r.created_at)} · krok {Math.min(r.current_step + 1, wf?.nodes.length ?? 0)}/{wf?.nodes.length}</div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </div>
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}
