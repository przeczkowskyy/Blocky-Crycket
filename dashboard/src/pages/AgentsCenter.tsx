import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Play, Workflow, Activity } from 'lucide-react';
import { useApi, AGENT_STATUS, EXEC_STATUS, timeAgo, usd, num } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, PageHeader, Spinner, StatusBadge, NotConfigured } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { AssignTaskModal } from '../components/AssignTaskModal';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

export function AgentsCenter() {
  const { data: agents, error } = useApi<any[]>('/agents', 3000);
  const { data: execs } = useApi<any[]>('/executions', 3000);
  const { status } = useStatus();
  const [assign, setAssign] = useState<any>(null);
  const [exec, setExec] = useState<string | null>(null);

  if (error) return <ErrorBox error={error} />;
  if (!agents) return <Spinner />;
  const running = (execs ?? []).filter((e) => e.status === 'running');

  return (
    <div>
      <PageHeader icon={<Users size={20} className="text-gold" />} title="Agent Command Center"
        subtitle="Dziesięciu wyspecjalizowanych agentów pracujących nad jedną grą. Wszyscy dzielą Project Brain, decyzje i roadmapę."
        actions={<>{!status?.ai.configured && <NotConfigured />}<Link to="/workflows"><Button icon={<Workflow size={14} />}>Uruchom workflow</Button></Link></>} />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
        {agents.map((a) => {
          const st = AGENT_STATUS[a.status] ?? AGENT_STATUS.idle;
          return (
            <div key={a.id} className="flex flex-col rounded-lg border border-line bg-panel p-3.5 transition-colors hover:border-line2">
              <div className="flex items-start gap-3">
                <AgentAvatar agent={a} size={40} />
                <div className="min-w-0 flex-1">
                  <Link to={`/agents/${a.id}`} className="font-semibold hover:text-gold">{a.name}</Link>
                  <div className="truncate text-[11.5px] text-mute">{a.role}</div>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                <Badge color={st.color} dot>{st.label}</Badge>
                {!a.configured && <Badge color="#f05252">NOT CONFIGURED</Badge>}
                {!a.enabled && <Badge color="#5d6678">wstrzymany</Badge>}
              </div>
              <div className="mt-2 min-h-[32px] text-[11.5px] text-faint line-clamp-2">{a.current_activity ?? a.description}</div>
              <div className="mt-2 grid grid-cols-3 gap-1 text-center text-[11px]">
                <div className="rounded bg-panel2 py-1"><div className="font-semibold">{a.openTasks}</div><div className="text-faint">zadań</div></div>
                <div className="rounded bg-panel2 py-1"><div className="font-semibold">{a.stats.runs}</div><div className="text-faint">wykonań</div></div>
                <div className="rounded bg-panel2 py-1"><div className="font-semibold">{usd(a.stats.cost)}</div><div className="text-faint">koszt</div></div>
              </div>
              <div className="mt-3 flex gap-1.5">
                <Button size="sm" variant="primary" className="flex-1" icon={<Play size={12} />} disabled={!a.configured || !a.enabled} onClick={() => setAssign(a)}>Zleć zadanie</Button>
                <Link to={`/agents/${a.id}`}><Button size="sm">Konsola</Button></Link>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 grid gap-5 xl:grid-cols-2">
        <Card title={`W toku (${running.length})`} icon={<Activity size={14} className="text-cyan" />}>
          {running.length === 0 ? <Empty title="Żaden agent teraz nie pracuje" /> : running.map((e) => <ExecRow key={e.id} e={e} onClick={() => setExec(e.id)} />)}
        </Card>
        <Card title="Ostatnie wykonania" icon={<Activity size={14} className="text-mint" />}>
          {(execs ?? []).length === 0 ? <Empty title="Brak wykonań">Wykonania pojawią się po pierwszym zleceniu zadania agentowi.</Empty> : (execs ?? []).filter((e) => e.status !== 'running').slice(0, 12).map((e) => <ExecRow key={e.id} e={e} onClick={() => setExec(e.id)} />)}
        </Card>
      </div>

      <AssignTaskModal agent={assign} open={!!assign} onClose={() => setAssign(null)} onStarted={(id) => { setAssign(null); setExec(id); }} />
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}

export function ExecRow({ e, onClick }: { e: any; onClick: () => void }) {
  return (
    <button onClick={onClick} className="mb-1.5 flex w-full items-center gap-2.5 rounded-md border border-line bg-panel2 px-2.5 py-2 text-left hover:border-line2 cursor-pointer">
      <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: e.agent_color }} />
      <span className="w-24 shrink-0 text-[12px] font-semibold">{e.agent_name}</span>
      <span className="min-w-0 flex-1 truncate text-[12px] text-mute">{e.prompt}</span>
      <span className="hidden text-[11px] text-faint sm:inline">{num(e.input_tokens + e.output_tokens)} tok</span>
      <StatusBadge map={EXEC_STATUS} value={e.status} />
      <span className="w-20 text-right text-[11px] text-faint">{timeAgo(e.started_at)}</span>
    </button>
  );
}
