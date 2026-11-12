import { useNavigate, Link } from 'react-router-dom';
import { Bot, ListTodo, CheckCheck, Bug, CheckCircle2, Image, AlertTriangle, HelpCircle, Gavel, Brain, Flag, Activity, Target, Sparkles } from 'lucide-react';
import { useApi, AGENT_STATUS, fmtTime, timeAgo, TASK_COLUMNS } from '../lib/api';
import { Card, Stat, Spinner, ErrorBox, Badge, Progress, Empty, StatusBadge } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { useStatus } from '../components/Layout';

const LEVEL_COLOR: Record<string, string> = { info: '#8a93a6', success: '#34d399', warn: '#f5c542', error: '#f05252' };

export function Overview() {
  const { data, error } = useApi<any>('/overview', 5000);
  const { status } = useStatus();
  const nav = useNavigate();
  if (error) return <ErrorBox error={error} />;
  if (!data) return <Spinner />;
  const { project, stats, progress, sprint, activity, agents, attention, lastActivity } = data;
  const phases = project.roadmap as any[];
  const current = phases.find((p) => p.id === project.current_phase);
  const pct = progress.total ? Math.round((progress.done / progress.total) * 100) : 0;
  const nextMilestone = current?.items.find((i: any) => !i.done)?.title ?? '—';
  const attentionCount = attention.approvals.length + attention.failed.length + attention.conflicts.length + attention.questions.length + (attention.decisionsAwaiting ? 1 : 0) + (attention.brainUpdates ? 1 : 0);

  return (
    <div className="space-y-5">
      {/* header */}
      <section className="relative overflow-hidden rounded-xl border border-line bg-panel p-5">
        <div className="pointer-events-none absolute inset-0 opacity-[0.06]" style={{ backgroundImage: 'radial-gradient(#f5c542 1px, transparent 1.2px)', backgroundSize: '10px 10px' }} />
        <div className="relative flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="brand-mark text-3xl text-gold">BLOCKY &amp; CRYCKET</h1>
            <p className="mt-1 text-[13px] text-mute">Twoja fantasy RPG jest budowana przez Twój zespół AI.</p>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
              <Badge color="#f5c542"><Flag size={12} /> {current?.name}</Badge>
              <Badge color="#60a5fa"><Target size={12} /> Następny kamień milowy: {nextMilestone}</Badge>
              <span className="text-faint">Ostatnia aktywność: {lastActivity ? `${lastActivity.actor} — ${lastActivity.action} (${timeAgo(lastActivity.timestamp)})` : '—'}</span>
            </div>
          </div>
          <div className="w-full max-w-xs">
            <div className="mb-1 flex justify-between text-xs"><span className="text-mute">Postęp roadmapy</span><span className="font-semibold">{pct}%</span></div>
            <Progress value={progress.done} max={progress.total} />
            <div className="mt-1 text-[11px] text-faint">{progress.done}/{progress.total} elementów roadmapy oznaczonych jako ukończone</div>
            {!status?.ai.configured && <div className="mt-3 rounded-md border border-ruby/30 bg-ruby/10 px-2.5 py-1.5 text-[11.5px] text-ruby">Agenci: NOT CONFIGURED — dodaj <code>ANTHROPIC_API_KEY</code> w <code>dashboard/.env</code>.</div>}
          </div>
        </div>
      </section>

      {/* stats */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <Stat label="Aktywni agenci" value={stats.activeAgents} icon={<Bot size={18} />} color="#22d3ee" onClick={() => nav('/agents')} />
        <Stat label="Zadania w trakcie" value={stats.tasksInProgress} icon={<ListTodo size={18} />} color="#60a5fa" onClick={() => nav('/tasks')} />
        <Stat label="Oczekujące zatwierdzenia" value={stats.pendingApprovals} icon={<CheckCheck size={18} />} color="#f5c542" onClick={() => nav('/approvals')} />
        <Stat label="Otwarte błędy" value={stats.openBugs} icon={<Bug size={18} />} color="#f05252" onClick={() => nav('/bugs')} />
        <Stat label="Ukończone zadania" value={`${stats.completedTasks}/${stats.totalTasks}`} icon={<CheckCircle2 size={18} />} color="#34d399" onClick={() => nav('/tasks')} />
        <Stat label="Utworzone assety" value={`${stats.assetsCreated}/${stats.assetsTotal}`} icon={<Image size={18} />} color="#a78bfa" onClick={() => nav('/assets')} />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        {/* roadmap */}
        <Card title="Faza rozwoju" icon={<Flag size={15} className="text-gold" />} className="xl:col-span-2" actions={<Link to="/roadmap" className="text-xs text-cyan hover:underline">Edytuj roadmapę →</Link>}>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {phases.map((ph) => {
              const done = ph.items.filter((i: any) => i.done).length;
              const isCur = ph.id === project.current_phase;
              return (
                <div key={ph.id} className={`rounded-lg border p-3 ${isCur ? 'border-gold/50 bg-gold/5' : 'border-line bg-panel2'}`}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-[12.5px] font-semibold leading-tight">{ph.name}</div>
                    {ph.proposed && <Badge color="#8a93a6">propozycja</Badge>}
                  </div>
                  <Progress value={done} max={ph.items.length} className="mt-2" color={isCur ? '#f5c542' : '#60a5fa'} />
                  <ul className="mt-2 space-y-0.5 text-[11.5px] text-mute">
                    {ph.items.slice(0, 5).map((it: any) => <li key={it.title} className={it.done ? 'text-mint line-through decoration-mint/40' : ''}>• {it.title}</li>)}
                  </ul>
                </div>
              );
            })}
          </div>
        </Card>

        {/* attention */}
        <Card title="Wymaga Twojej uwagi" icon={<AlertTriangle size={15} className="text-amber" />} actions={<Badge color={attentionCount ? '#f5c542' : '#34d399'}>{attentionCount}</Badge>}>
          <div className="space-y-2 text-[12.5px]">
            {attention.approvals.map((a: any) => <AttnRow key={a.id} to="/approvals" icon={<CheckCheck size={14} className="text-gold" />} text={a.title} sub={timeAgo(a.created_at)} />)}
            {attention.conflicts.map((a: any) => <AttnRow key={a.id} to="/approvals" icon={<AlertTriangle size={14} className="text-ruby" />} text={`Konflikt plików: ${a.title}`} />)}
            {attention.failed.map((f: any) => <AttnRow key={f.id} to="/agents" icon={<AlertTriangle size={14} className="text-ruby" />} text={`${f.agent_name}: ${f.error}`} sub={timeAgo(f.started_at)} />)}
            {attention.questions.map((q: any) => <AttnRow key={q.id} to="/brain/decisions?tab=questions" icon={<HelpCircle size={14} className="text-amber" />} text={q.question} />)}
            {attention.decisionsAwaiting > 0 && <AttnRow to="/brain/decisions" icon={<Gavel size={14} className="text-violet" />} text={`${attention.decisionsAwaiting} decyzji czeka na Twoją akceptację`} />}
            {attention.brainUpdates > 0 && <AttnRow to="/brain/history" icon={<Brain size={14} className="text-violet" />} text={`${attention.brainUpdates} aktualizacji wiedzy do przeglądu`} />}
            {attention.missingAssets > 0 && <AttnRow to="/assets" icon={<Image size={14} className="text-mute" />} text={`${attention.missingAssets} zaplanowanych assetów bez pliku`} />}
            {attentionCount === 0 && !attention.missingAssets && <Empty title="Wszystko pod kontrolą" />}
          </div>
        </Card>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        {/* sprint */}
        <Card title={sprint.name} icon={<Sparkles size={15} className="text-cyan" />} actions={<Link to="/roadmap" className="text-xs text-cyan hover:underline">Edytuj sprint →</Link>}>
          <p className="text-[12.5px] text-mute">{sprint.objective}</p>
          <div className="my-3 grid grid-cols-3 gap-2 text-center">
            <div className="rounded-md bg-panel2 p-2"><div className="text-lg font-semibold text-mint">{sprint.completed}</div><div className="text-[10.5px] text-faint">ukończone</div></div>
            <div className="rounded-md bg-panel2 p-2"><div className="text-lg font-semibold">{sprint.remaining}</div><div className="text-[10.5px] text-faint">pozostałe</div></div>
            <div className="rounded-md bg-panel2 p-2"><div className="text-lg font-semibold text-ruby">{sprint.blocked}</div><div className="text-[10.5px] text-faint">zablokowane</div></div>
          </div>
          <div className="mb-2 flex -space-x-1">{(sprint.agentIds ?? []).map((id: string) => { const a = agents.find((x: any) => x.id === id); return a ? <Link key={id} to={`/agents/${id}`} title={a.name}><AgentAvatar agent={a} size={26} showStatus={false} /></Link> : null; })}</div>
          <ul className="space-y-1">
            {sprint.tasks.map((t: any) => (
              <li key={t.id} className="flex items-center justify-between gap-2 text-[12px]">
                <span className="truncate">{t.title}</span>
                <StatusBadge map={Object.fromEntries(TASK_COLUMNS.map((c) => [c.id, c]))} value={t.status} />
              </li>
            ))}
          </ul>
        </Card>

        {/* agents */}
        <Card title="Co robią agenci" icon={<Bot size={15} className="text-cyan" />} actions={<Link to="/agents" className="text-xs text-cyan hover:underline">Command Center →</Link>}>
          <div className="space-y-2">
            {agents.map((a: any) => (
              <Link key={a.id} to={`/agents/${a.id}`} className="flex items-center gap-2.5 rounded-md p-1 hover:bg-panel2">
                <AgentAvatar agent={a} size={28} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 text-[12.5px] font-medium">{a.name}<span className="text-[10.5px] font-normal" style={{ color: AGENT_STATUS[a.status]?.color }}>{AGENT_STATUS[a.status]?.label}</span></div>
                  <div className="truncate text-[11px] text-faint">{a.current_activity ?? a.role}</div>
                </div>
              </Link>
            ))}
          </div>
        </Card>

        {/* activity feed */}
        <Card title="Aktywność" icon={<Activity size={15} className="text-mint" />} actions={<Link to="/logs" className="text-xs text-cyan hover:underline">Wszystkie logi →</Link>}>
          {activity.length === 0 ? <Empty title="Brak zdarzeń" /> : (
            <ul className="space-y-1.5 font-mono text-[11.5px]">
              {activity.map((l: any) => (
                <li key={l.id} className="flex gap-2">
                  <span className="text-faint">[{fmtTime(l.timestamp)}]</span>
                  <span className="min-w-0"><span style={{ color: LEVEL_COLOR[l.level] }} className="font-semibold">{l.actor}</span> <span className="text-ink/90">— {l.action}</span>{l.details && <span className="block truncate text-faint">{l.details}</span>}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 text-[10.5px] text-faint">Pokazywane są wyłącznie prawdziwe zdarzenia z tej instalacji — brak danych demo.</div>
        </Card>
      </div>
    </div>
  );
}

function AttnRow({ to, icon, text, sub }: { to: string; icon: React.ReactNode; text: string; sub?: string }) {
  return (
    <Link to={to} className="flex items-start gap-2 rounded-md border border-line bg-panel2 px-2.5 py-1.5 hover:border-line2">
      <span className="mt-0.5 shrink-0">{icon}</span>
      <span className="min-w-0 flex-1"><span className="line-clamp-2">{text}</span>{sub && <span className="text-[10.5px] text-faint">{sub}</span>}</span>
    </Link>
  );
}
