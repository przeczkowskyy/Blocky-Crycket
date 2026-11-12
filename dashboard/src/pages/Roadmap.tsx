import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Map, Plus, Trash2, Save, Flag, Sparkles, CheckCircle2 } from 'lucide-react';
import { api, useApi, TASK_COLUMNS } from '../lib/api';
import { Badge, Button, Card, ErrorBox, Input, PageHeader, Progress, Select, Spinner, Textarea, useAction, StatusBadge, cx } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';

export function Roadmap() {
  const { data: project, error, reload } = useApi<any>('/overview');
  const { data: agents } = useApi<any[]>('/agents');
  const { data: tasks, reload: reloadTasks } = useApi<any[]>('/tasks');
  const [phases, setPhases] = useState<any[] | null>(null);
  const [current, setCurrent] = useState('');
  const [sprint, setSprint] = useState<any>(null);
  const [newItem, setNewItem] = useState<Record<string, string>>({});

  useEffect(() => {
    if (project?.project) {
      setPhases(structuredClone(project.project.roadmap));
      setCurrent(project.project.current_phase);
      setSprint(structuredClone(project.project.sprint));
    }
  }, [project]);

  const save = useAction(() => api('/project', { method: 'PATCH', body: { roadmap: phases, current_phase: current, sprint } }), { success: 'Zapisano roadmapę i sprint', onDone: reload });
  const toggleSprint = useAction((t: any) => api(`/tasks/${t.id}`, { method: 'PATCH', body: { sprint: !t.sprint } }), { onDone: reloadTasks });

  if (error) return <ErrorBox error={error} />;
  if (!phases || !sprint) return <Spinner />;

  const dirty = JSON.stringify(phases) !== JSON.stringify(project.project.roadmap) || current !== project.project.current_phase || JSON.stringify(sprint) !== JSON.stringify(project.project.sprint);
  const upd = (i: number, patch: any) => setPhases(phases.map((p, j) => (j === i ? { ...p, ...patch } : p)));
  const colMap = Object.fromEntries(TASK_COLUMNS.map((c) => [c.id, c]));

  return (
    <div>
      <PageHeader icon={<Map size={20} className="text-gold" />} title="Development Roadmap"
        subtitle="Fazy 2–6 to propozycja z master promptu — nie dowód wykonanych prac. Oznacz fazę jako zatwierdzoną, gdy ją akceptujesz."
        actions={<Button variant="primary" icon={<Save size={14} />} disabled={!dirty} loading={save.loading} onClick={() => save.run()}>Zapisz zmiany</Button>} />

      <div className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
        {phases.map((ph, i) => {
          const done = ph.items.filter((x: any) => x.done).length;
          return (
            <Card key={ph.id} className={cx(current === ph.id && 'border-gold/50')}
              title={<span className="flex items-center gap-2">{current === ph.id && <Flag size={14} className="text-gold" />}{ph.name}</span>}
              actions={ph.proposed ? <Button size="sm" variant="ghost" onClick={() => upd(i, { proposed: false })}>Zatwierdź fazę</Button> : <Badge color="#34d399">zatwierdzona</Badge>}>
              <div className="mb-3 flex items-center gap-2">
                <Select value={ph.status} onChange={(e) => upd(i, { status: e.target.value })} className="w-40">
                  <option value="planned">Planowana</option><option value="in_progress">W trakcie</option><option value="done">Ukończona</option>
                </Select>
                <Button size="sm" variant={current === ph.id ? 'primary' : 'secondary'} onClick={() => setCurrent(ph.id)}>{current === ph.id ? 'Bieżąca faza' : 'Ustaw jako bieżącą'}</Button>
              </div>
              <Progress value={done} max={ph.items.length} />
              <ul className="mt-3 space-y-1">
                {ph.items.map((it: any, k: number) => (
                  <li key={k} className="group flex items-center gap-2 text-[13px]">
                    <input type="checkbox" checked={it.done} className="accent-[#34d399] cursor-pointer"
                      onChange={() => upd(i, { items: ph.items.map((x: any, j: number) => (j === k ? { ...x, done: !x.done } : x)) })} />
                    <span className={cx('flex-1', it.done && 'text-mute line-through')}>{it.title}</span>
                    <button className="opacity-0 group-hover:opacity-100 text-faint hover:text-ruby cursor-pointer" onClick={() => upd(i, { items: ph.items.filter((_: any, j: number) => j !== k) })}><Trash2 size={13} /></button>
                  </li>
                ))}
              </ul>
              <form className="mt-3 flex gap-2" onSubmit={(e) => { e.preventDefault(); const v = (newItem[ph.id] ?? '').trim(); if (!v) return; upd(i, { items: [...ph.items, { title: v, done: false }] }); setNewItem({ ...newItem, [ph.id]: '' }); }}>
                <Input placeholder="Nowy kamień milowy…" value={newItem[ph.id] ?? ''} onChange={(e) => setNewItem({ ...newItem, [ph.id]: e.target.value })} />
                <Button type="submit" size="sm" icon={<Plus size={13} />}>Dodaj</Button>
              </form>
            </Card>
          );
        })}
      </div>

      <Card className="mt-6" title={<span className="flex items-center gap-2"><Sparkles size={15} className="text-cyan" />Bieżący sprint</span>}>
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            <Input value={sprint.name} onChange={(e) => setSprint({ ...sprint, name: e.target.value })} placeholder="Nazwa sprintu" />
            <Textarea value={sprint.objective} onChange={(e) => setSprint({ ...sprint, objective: e.target.value })} placeholder="Cel sprintu" />
            <div>
              <div className="mb-1.5 text-xs text-mute">Przypisani agenci</div>
              <div className="flex flex-wrap gap-2">
                {(agents ?? []).map((a) => {
                  const on = sprint.agentIds?.includes(a.id);
                  return (
                    <button key={a.id} onClick={() => setSprint({ ...sprint, agentIds: on ? sprint.agentIds.filter((x: string) => x !== a.id) : [...(sprint.agentIds ?? []), a.id] })}
                      className={cx('flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs cursor-pointer', on ? 'border-gold/50 bg-gold/10' : 'border-line opacity-60 hover:opacity-100')}>
                      <AgentAvatar agent={a} size={18} showStatus={false} />{a.name}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          <div>
            <div className="mb-1.5 flex items-center justify-between text-xs text-mute"><span>Zadania (kliknij, aby dodać/usunąć ze sprintu)</span><Link to="/tasks" className="text-cyan hover:underline">Task Board →</Link></div>
            <div className="max-h-80 space-y-1 overflow-y-auto">
              {(tasks ?? []).filter((t) => t.status !== 'completed' || t.sprint).map((t) => (
                <button key={t.id} onClick={() => toggleSprint.run(t)} className={cx('flex w-full items-center gap-2 rounded-md border px-2 py-1.5 text-left text-[12.5px] cursor-pointer', t.sprint ? 'border-cyan/40 bg-cyan/5' : 'border-line hover:border-line2')}>
                  {t.sprint ? <CheckCircle2 size={14} className="text-cyan shrink-0" /> : <span className="h-3.5 w-3.5 shrink-0 rounded-full border border-line2" />}
                  <span className="flex-1 truncate">{t.title}</span>
                  <StatusBadge map={colMap} value={t.status} />
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
