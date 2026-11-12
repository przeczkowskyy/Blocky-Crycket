import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { KanbanSquare, Plus, Play, Split, Send, Trash2, Link2, Sparkles } from 'lucide-react';
import { api, useApi, TASK_COLUMNS, PRIORITY, timeAgo, fmtDateTime, EXEC_STATUS } from '../lib/api';
import { Badge, Button, Confirm, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, StatusBadge, Textarea, useAction, cx } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

export function TaskBoard() {
  const { data: tasks, error, reload } = useApi<any[]>('/tasks', 4000);
  const { data: agents } = useApi<any[]>('/agents');
  const [agentFilter, setAgentFilter] = useState('');
  const [prioFilter, setPrioFilter] = useState('');
  const [q, setQ] = useState('');
  const [open, setOpen] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [dragId, setDragId] = useState<string | null>(null);
  const [forceMove, setForceMove] = useState<{ id: string; status: string; msg: string } | null>(null);

  const move = useAction(async (id: string, status: string, force = false) => {
    try { return await api(`/tasks/${id}`, { method: 'PATCH', body: { status, force } }); }
    catch (e: any) { if (e.status === 409 && !force) { setForceMove({ id, status, msg: e.message }); return null; } throw e; }
  }, { onDone: reload });

  const filtered = useMemo(() => (tasks ?? []).filter((t) => (!agentFilter || t.assigned_agent_id === agentFilter) && (!prioFilter || t.priority === prioFilter) && (!q || (t.title + t.description).toLowerCase().includes(q.toLowerCase()))), [tasks, agentFilter, prioFilter, q]);
  if (error) return <ErrorBox error={error} />;
  if (!tasks || !agents) return <Spinner />;
  const agentOf = (id: string) => agents.find((a) => a.id === id);

  return (
    <div>
      <PageHeader icon={<KanbanSquare size={20} className="text-gold" />} title="Task Board" subtitle="Wszystkie zadania należą do BLOCKY & CRYCKET. Przeciągnij kartę między kolumnami; zadania z nieukończonymi zależnościami wymagają potwierdzenia."
        actions={<>
          <Input className="w-48" placeholder="Szukaj…" value={q} onChange={(e) => setQ(e.target.value)} />
          <Select className="w-40" value={agentFilter} onChange={(e) => setAgentFilter(e.target.value)}><option value="">Wszyscy agenci</option>{agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select>
          <Select className="w-36" value={prioFilter} onChange={(e) => setPrioFilter(e.target.value)}><option value="">Każdy priorytet</option>{Object.entries(PRIORITY).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select>
          <Button variant="primary" icon={<Plus size={14} />} onClick={() => setCreating(true)}>Nowe zadanie</Button>
        </>} />
      <div className="flex gap-3 overflow-x-auto pb-3">
        {TASK_COLUMNS.map((col) => {
          const items = filtered.filter((t) => t.status === col.id);
          return (
            <div key={col.id} className="flex w-72 shrink-0 flex-col rounded-lg border border-line bg-panel"
              onDragOver={(e) => e.preventDefault()} onDrop={() => { if (dragId) { const t = tasks.find((x) => x.id === dragId); if (t && t.status !== col.id) void move.run(dragId, col.id); } setDragId(null); }}>
              <div className="flex items-center gap-2 border-b border-line px-3 py-2 text-[12.5px] font-semibold"><span className="h-2 w-2 rounded-full" style={{ background: col.color }} />{col.label}<span className="ml-auto text-xs font-normal text-faint">{items.length}</span></div>
              <div className="flex min-h-[120px] flex-1 flex-col gap-2 p-2">
                {items.map((t) => {
                  const ag = agentOf(t.assigned_agent_id);
                  return (
                    <div key={t.id} draggable onDragStart={() => setDragId(t.id)} onClick={() => setOpen(t.id)}
                      className={cx('cursor-pointer rounded-md border border-line bg-panel2 p-2.5 hover:border-line2', dragId === t.id && 'opacity-50')}>
                      <div className="flex items-start gap-2">
                        <span className="flex-1 text-[12.5px] font-medium leading-snug">{t.title}</span>
                        {ag && <AgentAvatar agent={ag} size={20} showStatus={false} />}
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-1">
                        <Badge color={PRIORITY[t.priority]?.color}>{PRIORITY[t.priority]?.label}</Badge>
                        {t.sprint && <Badge color="#22d3ee"><Sparkles size={10} />sprint</Badge>}
                        {t.dependencies?.length > 0 && <Badge color="#8a93a6"><Link2 size={10} />{t.dependencies.length}</Badge>}
                        {t.effort && <span className="text-[10.5px] text-faint">{t.effort}</span>}
                        <span className="ml-auto text-[10.5px] text-faint">{t.created_by !== 'user' && t.created_by !== 'Game Director' ? t.created_by : ''}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      {open && <TaskDrawer id={open} agents={agents} tasks={tasks} onClose={() => setOpen(null)} onChanged={reload} />}
      <NewTask open={creating} agents={agents} onClose={() => setCreating(false)} onDone={() => { setCreating(false); reload(); }} />
      <Confirm open={!!forceMove} onClose={() => setForceMove(null)} title="Nieukończone zależności" text={forceMove?.msg} onConfirm={() => { void move.run(forceMove!.id, forceMove!.status, true); setForceMove(null); }} />
    </div>
  );
}

function NewTask({ open, agents, onClose, onDone }: { open: boolean; agents: any[]; onClose: () => void; onDone: () => void }) {
  const [f, setF] = useState({ title: '', description: '', assigned_agent_id: 'atlas', priority: 'medium', status: 'backlog', effort: 'M', related_files: '', sprint: false });
  const create = useAction(() => api('/tasks', { body: { ...f, related_files: f.related_files.split(',').map((x) => x.trim()).filter(Boolean) } }), { success: 'Utworzono zadanie', onDone: () => { setF({ ...f, title: '', description: '', related_files: '' }); onDone(); } });
  return (
    <Modal open={open} onClose={onClose} title="Nowe zadanie" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={f.title.trim().length < 3} loading={create.loading} onClick={() => create.run()}>Utwórz</Button></>}>
      <div className="space-y-3">
        <Field label="Tytuł" error={f.title && f.title.trim().length < 3 ? 'Min. 3 znaki' : null}><Input value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} /></Field>
        <Field label="Opis"><Textarea value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} /></Field>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Field label="Agent"><Select value={f.assigned_agent_id} onChange={(e) => setF({ ...f, assigned_agent_id: e.target.value })}>{agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></Field>
          <Field label="Priorytet"><Select value={f.priority} onChange={(e) => setF({ ...f, priority: e.target.value })}>{Object.entries(PRIORITY).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></Field>
          <Field label="Status"><Select value={f.status} onChange={(e) => setF({ ...f, status: e.target.value })}>{TASK_COLUMNS.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}</Select></Field>
          <Field label="Nakład"><Select value={f.effort} onChange={(e) => setF({ ...f, effort: e.target.value })}>{['XS', 'S', 'M', 'L', 'XL'].map((x) => <option key={x}>{x}</option>)}</Select></Field>
        </div>
        <Field label="Powiązane pliki (po przecinku)"><Input value={f.related_files} onChange={(e) => setF({ ...f, related_files: e.target.value })} placeholder="src/gui/MainHUD.model.json" /></Field>
        <label className="flex items-center gap-2 text-[12.5px]"><input type="checkbox" className="accent-[#22d3ee]" checked={f.sprint} onChange={(e) => setF({ ...f, sprint: e.target.checked })} /> Dodaj do bieżącego sprintu</label>
      </div>
    </Modal>
  );
}

function TaskDrawer({ id, agents, tasks, onClose, onChanged }: { id: string; agents: any[]; tasks: any[]; onClose: () => void; onChanged: () => void }) {
  const { data: t, reload } = useApi<any>(`/tasks/${id}`, 4000);
  const { status } = useStatus();
  const [comment, setComment] = useState('');
  const [exec, setExec] = useState<string | null>(null);
  const [del, setDel] = useState(false);
  const done = () => { reload(); onChanged(); };
  const patch = useAction((body: any) => api(`/tasks/${id}`, { method: 'PATCH', body: { ...body, force: true } }), { onDone: done });
  const addComment = useAction(() => api(`/tasks/${id}/comments`, { body: { body: comment } }), { onDone: () => { setComment(''); reload(); } });
  const run = useAction(() => api<{ executionId: string }>(`/tasks/${id}/run`, { body: {} }), { success: 'Agent rozpoczął zadanie', onDone: (r) => { setExec(r.executionId); done(); } });
  const breakdown = useAction(() => api<{ executionId: string }>(`/tasks/${id}/breakdown`, { body: {} }), { success: 'ATLAS rozbija zadanie', onDone: (r) => setExec(r.executionId) });
  const remove = useAction(() => api(`/tasks/${id}`, { method: 'DELETE' }), { success: 'Usunięto zadanie', onDone: () => { onChanged(); onClose(); } });

  return (
    <Modal open onClose={onClose} width="max-w-3xl" title={t ? t.title : 'Zadanie'}>
      {!t ? <Spinner /> : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Field label="Status"><Select value={t.status} onChange={(e) => patch.run({ status: e.target.value })}>{TASK_COLUMNS.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}</Select></Field>
            <Field label="Agent"><Select value={t.assigned_agent_id ?? ''} onChange={(e) => patch.run({ assigned_agent_id: e.target.value || null })}><option value="">—</option>{agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></Field>
            <Field label="Priorytet"><Select value={t.priority} onChange={(e) => patch.run({ priority: e.target.value })}>{Object.entries(PRIORITY).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></Field>
            <Field label="Sprint"><Select value={t.sprint ? '1' : '0'} onChange={(e) => patch.run({ sprint: e.target.value === '1' })}><option value="0">Nie</option><option value="1">Tak</option></Select></Field>
          </div>
          <Field label="Opis"><Textarea defaultValue={t.description} onBlur={(e) => e.target.value !== t.description && patch.run({ description: e.target.value })} /></Field>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Zależności">
              <Select value="" onChange={(e) => e.target.value && patch.run({ dependencies: [...t.dependencies, e.target.value] })}>
                <option value="">+ dodaj zależność…</option>{tasks.filter((x) => x.id !== t.id && !t.dependencies.includes(x.id)).map((x) => <option key={x.id} value={x.id}>{x.title}</option>)}
              </Select>
              <div className="mt-1 flex flex-wrap gap-1">{t.dependencies.map((d: string) => { const dt = tasks.find((x) => x.id === d); return <button key={d} onClick={() => patch.run({ dependencies: t.dependencies.filter((x: string) => x !== d) })} className="cursor-pointer"><Badge color={dt?.status === 'completed' ? '#34d399' : '#f5c542'}>{dt?.title ?? d} ✕</Badge></button>; })}</div>
            </Field>
            <Field label="Powiązane pliki">
              <Input defaultValue={t.related_files.join(', ')} onBlur={(e) => patch.run({ related_files: e.target.value.split(',').map((x) => x.trim()).filter(Boolean) })} />
              <div className="mt-1 flex flex-wrap gap-1">{t.related_files.map((f: string) => <Link key={f} to={`/workspace?file=${encodeURIComponent(f)}`} className="font-mono text-[11px] text-cyan hover:underline">{f}</Link>)}</div>
            </Field>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" icon={<Play size={14} />} disabled={!t.assigned_agent_id || !status?.ai.configured} loading={run.loading} onClick={() => run.run()}>Zleć przypisanemu agentowi</Button>
            <Button icon={<Split size={14} />} disabled={!status?.ai.configured} loading={breakdown.loading} onClick={() => breakdown.run()}>ATLAS: rozbij na podzadania</Button>
            <div className="flex-1" />
            <Button variant="ghost" icon={<Trash2 size={14} />} onClick={() => setDel(true)}>Usuń</Button>
          </div>
          {t.subtasks.length > 0 && <div><div className="mb-1 text-xs text-mute">Podzadania</div>{t.subtasks.map((s: any) => <div key={s.id} className="text-[12.5px]">• {s.title} <span className="text-faint">({s.status})</span></div>)}</div>}
          {t.executions.length > 0 && <div><div className="mb-1 text-xs text-mute">Wykonania</div>{t.executions.map((e: any) => <button key={e.id} onClick={() => setExec(e.id)} className="mr-2 mb-1 cursor-pointer"><StatusBadge map={EXEC_STATUS} value={e.status} /> <span className="text-[12px]">{e.agent_name} · {timeAgo(e.started_at)}</span></button>)}</div>}
          {t.approvals.length > 0 && <div className="text-[12px]"><span className="text-mute">Zatwierdzenia: </span>{t.approvals.map((a: any) => <Link key={a.id} to="/approvals" className="mr-2 text-cyan hover:underline">{a.title} ({a.status})</Link>)}</div>}
          <div>
            <div className="mb-1 text-xs text-mute">Komentarze</div>
            {t.comments.length === 0 && <div className="text-[12px] text-faint">Brak komentarzy</div>}
            {t.comments.map((c: any) => <div key={c.id} className="mb-1.5 rounded bg-panel2 px-2.5 py-1.5 text-[12.5px]"><b>{c.author}</b> <span className="text-[10.5px] text-faint">{fmtDateTime(c.created_at)}</span><div className="whitespace-pre-wrap">{c.body}</div></div>)}
            <div className="mt-2 flex gap-2"><Input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Dodaj komentarz…" onKeyDown={(e) => e.key === 'Enter' && comment.trim() && addComment.run()} /><Button icon={<Send size={13} />} disabled={!comment.trim()} loading={addComment.loading} onClick={() => addComment.run()} /></div>
          </div>
          <div>
            <div className="mb-1 text-xs text-mute">Historia</div>
            {t.history.length === 0 ? <div className="text-[12px] text-faint">Brak zmian</div> : <ul className="space-y-0.5 text-[11.5px] text-mute">{t.history.map((h: any) => <li key={h.id}><span className="text-faint">{fmtDateTime(h.timestamp)}</span> {h.actor}: {h.action} — {h.details}</li>)}</ul>}
          </div>
          <div className="text-[11px] text-faint">Utworzone przez {t.created_by} · {fmtDateTime(t.created_at)} · ID {t.id}</div>
        </div>
      )}
      <Confirm open={del} onClose={() => setDel(false)} danger title="Usunąć zadanie?" text="Tej operacji nie można cofnąć." loading={remove.loading} onConfirm={() => remove.run()} />
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </Modal>
  );
}
