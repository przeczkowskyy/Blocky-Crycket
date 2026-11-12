import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Play, Pause, Save, History, Cpu, ShieldCheck, MessagesSquare, ListTodo, Settings2 } from 'lucide-react';
import { api, useApi, AGENT_STATUS, EXEC_STATUS, TASK_COLUMNS, timeAgo, usd, num, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Field, PageHeader, Select, Spinner, StatusBadge, Tabs, Textarea, useAction, cx, NotConfigured } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { AssignTaskModal } from '../components/AssignTaskModal';
import { ExecutionModal } from '../components/ExecutionView';
import { ChatThread } from './Communication';

const PERMS: Record<string, string> = { write_files: 'Zapis plików (src/, docs/, assets/)', create_tasks: 'Tworzenie zadań', propose_decisions: 'Proponowanie decyzji', report_bugs: 'Zgłaszanie błędów', assign_tasks: 'Przydzielanie zadań innym' };

export function AgentProfile() {
  const { id } = useParams();
  const nav = useNavigate();
  const { data: agents } = useApi<any[]>('/agents');
  const { data: a, error, reload } = useApi<any>(`/agents/${id}`, 3000);
  const { data: settings } = useApi<any>('/settings');
  const [tab, setTab] = useState<'overview' | 'instructions' | 'tasks' | 'history' | 'chat'>('overview');
  const [assign, setAssign] = useState(false);
  const [exec, setExec] = useState<string | null>(null);
  const [instr, setInstr] = useState('');
  useEffect(() => { if (a) setInstr(a.instructions); }, [a?.id, a?.instructions]);

  const patch = useAction((body: any) => api(`/agents/${id}`, { method: 'PATCH', body }), { success: 'Zapisano', onDone: reload });

  if (error) return <ErrorBox error={error} />;
  if (!a) return <Spinner />;
  const st = AGENT_STATUS[a.status] ?? AGENT_STATUS.idle;
  const colMap = Object.fromEntries(TASK_COLUMNS.map((c) => [c.id, c]));

  return (
    <div>
      <div className="mb-4 flex gap-1.5 overflow-x-auto pb-1">
        {(agents ?? []).map((x) => (
          <button key={x.id} onClick={() => nav(`/agents/${x.id}`)} className={cx('flex shrink-0 items-center gap-1.5 rounded-md border px-2 py-1 text-xs cursor-pointer', x.id === id ? 'border-gold/50 bg-gold/10 text-ink' : 'border-line text-mute hover:text-ink')}>
            <AgentAvatar agent={x} size={18} showStatus={false} />{x.name}
          </button>
        ))}
      </div>

      <PageHeader
        icon={<AgentAvatar agent={a} size={44} />}
        title={<span className="flex flex-col"><span>{a.name}</span><span className="text-[13px] font-normal text-mute">{a.role}</span></span>}
        subtitle={a.description}
        actions={<>
          <Badge color={st.color} dot>{st.label}</Badge>
          {!a.configured && <NotConfigured />}
          {a.enabled
            ? <Button icon={<Pause size={14} />} loading={patch.loading} onClick={() => patch.run({ enabled: false })}>Wstrzymaj</Button>
            : <Button variant="success" icon={<Play size={14} />} loading={patch.loading} onClick={() => patch.run({ enabled: true })}>Wznów</Button>}
          <Button variant="primary" icon={<Play size={14} />} disabled={!a.configured || !a.enabled} onClick={() => setAssign(true)}>Zleć zadanie</Button>
        </>} />

      {a.current_activity && <div className="mb-4 rounded-md border border-line bg-panel2 px-3 py-2 text-[12.5px]"><span className="text-mute">Bieżąca aktywność: </span>{a.current_activity}</div>}

      <Tabs value={tab} onChange={setTab} className="mb-4" tabs={[
        { id: 'overview', label: 'Profil' }, { id: 'instructions', label: 'Instrukcje' }, { id: 'tasks', label: 'Zadania', count: a.tasks.length },
        { id: 'history', label: 'Historia pracy', count: a.executions.length }, { id: 'chat', label: 'Czat' },
      ]} />

      {tab === 'overview' && (
        <div className="grid gap-5 lg:grid-cols-3">
          <Card title="Model i koszty" icon={<Cpu size={14} className="text-cyan" />}>
            <div className="space-y-3">
              <Field label="Dostawca"><div className="text-[13px]">Anthropic — Claude API</div></Field>
              <Field label="Model">
                <Select value={a.model} onChange={(e) => patch.run({ model: e.target.value })}>
                  {(settings?.models ?? [a.model]).map((m: string) => <option key={m} value={m}>{m}</option>)}
                </Select>
              </Field>
              <Field label="Effort" hint="Wyższy = dokładniej, drożej i wolniej.">
                <Select value={a.effort} onChange={(e) => patch.run({ effort: e.target.value })}>
                  {['low', 'medium', 'high', 'xhigh', 'max'].map((x) => <option key={x}>{x}</option>)}
                </Select>
              </Field>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <Mini label="Wykonania" value={num(a.stats.runs)} />
                <Mini label="Śr. czas" value={a.stats.avg_ms ? `${(a.stats.avg_ms / 1000).toFixed(1)} s` : '—'} />
                <Mini label="Tokeny in" value={num(a.stats.input_tokens)} />
                <Mini label="Tokeny out" value={num(a.stats.output_tokens)} />
                <Mini label="Szacowany koszt" value={usd(a.stats.cost)} />
              </div>
            </div>
          </Card>
          <Card title="Uprawnienia narzędzi" icon={<ShieldCheck size={14} className="text-mint" />}>
            <ul className="space-y-2">
              {Object.entries(PERMS).map(([k, label]) => (
                <li key={k} className="flex items-center justify-between gap-2 text-[12.5px]">
                  <span>{label}</span>
                  <input type="checkbox" className="accent-[#34d399] cursor-pointer" checked={!!a.permissions?.[k]} onChange={(e) => patch.run({ permissions: { [k]: e.target.checked } })} />
                </li>
              ))}
            </ul>
            <p className="mt-3 text-[11px] text-faint">Pliki chronione (Settings) zawsze wymagają zatwierdzenia, niezależnie od uprawnień i trybu autonomii.</p>
          </Card>
          <Card title="Dostęp do pamięci projektu" icon={<Settings2 size={14} className="text-violet" />}>
            <ul className="space-y-1.5 text-[12.5px] text-mute">
              <li>• Zatwierdzone decyzje — zawsze w kontekście</li>
              <li>• Propozycje — oznaczone jako „nie-fakty”</li>
              <li>• Wyszukiwanie w Project Brain (FTS) dopasowane do zadania</li>
              <li>• Treść plików powiązanych z zadaniem</li>
              <li>• Style Lock {['artist', 'pixel', 'blocksmith', 'lorekeeper'].includes(a.id) ? '— tak' : '— nie (rola niewizualna)'}</li>
            </ul>
            <Link to="/brain/context" className="mt-3 inline-block text-xs text-cyan hover:underline">Podgląd kontekstu dla tego agenta →</Link>
          </Card>
        </div>
      )}

      {tab === 'instructions' && (
        <Card title="Instrukcje systemowe agenta" actions={<Button size="sm" variant="primary" icon={<Save size={13} />} disabled={instr === a.instructions} loading={patch.loading} onClick={() => patch.run({ instructions: instr })}>Zapisz</Button>}>
          <Textarea className="min-h-[260px] font-mono text-[12.5px]" value={instr} onChange={(e) => setInstr(e.target.value)} />
          <p className="mt-2 text-[11px] text-faint">Do tych instrukcji serwer zawsze dokleja: skład zespołu, reguły zespołu, brief gry (Style Lock) i opis repozytorium Rojo.</p>
        </Card>
      )}

      {tab === 'tasks' && (
        <Card title="Przypisane zadania" icon={<ListTodo size={14} />} actions={<Link to="/tasks" className="text-xs text-cyan hover:underline">Task Board →</Link>}>
          {a.tasks.length === 0 ? <Empty title="Brak zadań" /> : a.tasks.map((t: any) => (
            <div key={t.id} className="mb-1.5 flex items-center gap-2 rounded-md border border-line bg-panel2 px-2.5 py-2 text-[12.5px]">
              <span className="flex-1">{t.title}</span><StatusBadge map={colMap} value={t.status} />
            </div>
          ))}
        </Card>
      )}

      {tab === 'history' && (
        <Card title="Historia pracy" icon={<History size={14} />}>
          {a.executions.length === 0 ? <Empty title="Brak wykonań" /> : (
            <table className="w-full text-[12.5px]">
              <thead className="text-left text-[11px] text-faint"><tr><th className="py-1">Start</th><th>Zlecenie</th><th>Status</th><th className="text-right">Tokeny</th><th className="text-right">Koszt</th></tr></thead>
              <tbody>
                {a.executions.map((e: any) => (
                  <tr key={e.id} className="cursor-pointer border-t border-line hover:bg-panel2" onClick={() => setExec(e.id)}>
                    <td className="py-1.5 pr-2 text-faint whitespace-nowrap">{fmtDateTime(e.started_at)}</td>
                    <td className="max-w-[420px] truncate pr-2">{e.prompt}</td>
                    <td><StatusBadge map={EXEC_STATUS} value={e.status} /></td>
                    <td className="text-right">{num(e.input_tokens + e.output_tokens)}</td>
                    <td className="text-right">{usd(e.cost_usd)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="mt-4 text-xs text-mute">Aktywność w logach</div>
          <ul className="mt-1 space-y-1 text-[12px]">{a.activity.map((l: any) => <li key={l.id}><span className="text-faint">{timeAgo(l.timestamp)}</span> — {l.action}: <span className="text-mute">{l.details}</span></li>)}</ul>
        </Card>
      )}

      {tab === 'chat' && (
        <Card title={`Czat z ${a.name}`} icon={<MessagesSquare size={14} />} bodyClass="p-0">
          <ChatThread fixedMention={a.name} height="h-[520px]" />
        </Card>
      )}

      <AssignTaskModal agent={a} open={assign} onClose={() => setAssign(false)} onStarted={(eid) => { setAssign(false); setExec(eid); }} />
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}

const Mini = ({ label, value }: { label: string; value: string }) => <div className="rounded bg-panel2 px-2 py-1.5"><div className="text-[10.5px] text-faint">{label}</div><div className="font-semibold">{value}</div></div>;
