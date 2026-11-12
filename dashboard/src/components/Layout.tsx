import { createContext, useContext, useState, type ReactNode } from 'react';
import { NavLink, Outlet, Link } from 'react-router-dom';
import {
  LayoutGrid, Map, BookText, Swords, Users, UserCircle2, MessagesSquare, Workflow, Code2, FolderTree, FileCode, LayoutDashboard,
  Box, Image, KanbanSquare, CheckCheck, FlaskConical, Bug, Gauge, Hammer, ScrollText, Plug, Cpu, Settings, Brain, Database,
  BookMarked, Gavel, SearchCode, History, OctagonX, GitBranch, Radio, MonitorPlay, Sparkles, Menu, Bot,
} from 'lucide-react';
import { api, useApi } from '../lib/api';
import { cx, useAction, Confirm } from './ui';

export interface StudioStatus {
  phase: string; branch: string | null; activeAgents: number; runningExecutions: number; pendingApprovals: number;
  rojo: { connected: boolean; port: number; serverVersion?: string; projectName?: string };
  studio: { open: boolean; placeFiles: string[] }; ai: { configured: boolean };
  autonomyMode: 'assistant' | 'semi' | 'autonomous'; emergencyStop: boolean;
}

const StatusCtx = createContext<{ status: StudioStatus | null; reload: () => void }>({ status: null, reload: () => {} });
export const useStatus = () => useContext(StatusCtx);

const NAV: { group: string; items: { to: string; label: string; icon: any; end?: boolean }[] }[] = [
  { group: 'PROJECT', items: [
    { to: '/', label: 'Overview', icon: LayoutGrid, end: true },
    { to: '/roadmap', label: 'Development Roadmap', icon: Map },
    { to: '/docs', label: 'Game Documentation', icon: BookText },
    { to: '/game-design', label: 'Game Design', icon: Swords },
  ] },
  { group: 'AI TEAM', items: [
    { to: '/agents', label: 'Agent Command Center', icon: Users, end: true },
    { to: '/agents/atlas', label: 'Individual Agents', icon: UserCircle2 },
    { to: '/chat', label: 'Agent Communication', icon: MessagesSquare },
    { to: '/workflows', label: 'Workflows', icon: Workflow },
  ] },
  { group: 'DEVELOPMENT', items: [
    { to: '/workspace', label: 'Development Workspace', icon: Code2 },
    { to: '/explorer', label: 'Roblox Explorer', icon: FolderTree },
    { to: '/luau', label: 'Luau Editor', icon: FileCode },
    { to: '/ui', label: 'UI Development', icon: LayoutDashboard },
    { to: '/assets-3d', label: '3D Assets', icon: Box },
    { to: '/assets', label: 'Asset Library', icon: Image },
    { to: '/tasks', label: 'Task Board', icon: KanbanSquare },
    { to: '/approvals', label: 'Approvals', icon: CheckCheck },
  ] },
  { group: 'QUALITY', items: [
    { to: '/testing', label: 'Testing Center', icon: FlaskConical },
    { to: '/bugs', label: 'Bug Tracker', icon: Bug },
    { to: '/performance', label: 'Performance', icon: Gauge },
    { to: '/builds', label: 'Build History', icon: Hammer },
  ] },
  { group: 'SYSTEM', items: [
    { to: '/logs', label: 'Activity Logs', icon: ScrollText },
    { to: '/integrations', label: 'Integrations', icon: Plug },
    { to: '/ai-config', label: 'AI Configuration', icon: Cpu },
    { to: '/settings', label: 'Settings', icon: Settings },
  ] },
  { group: 'PROJECT BRAIN', items: [
    { to: '/brain', label: 'Brain Overview', icon: Brain, end: true },
    { to: '/brain/sources', label: 'Knowledge Sources', icon: Database },
    { to: '/brain/canonical', label: 'Canonical Documentation', icon: BookMarked },
    { to: '/brain/decisions', label: 'Decisions & Rules', icon: Gavel },
    { to: '/brain/context', label: 'Context and Retrieval', icon: SearchCode },
    { to: '/brain/history', label: 'Change History', icon: History },
  ] },
];

export function Layout() {
  const { data: status, reload } = useApi<StudioStatus>('/status', 4000);
  const [mobileNav, setMobileNav] = useState(false);
  return (
    <StatusCtx.Provider value={{ status, reload }}>
      <div className="flex h-full flex-col">
        <TopBar status={status} reload={reload} onMenu={() => setMobileNav((v) => !v)} />
        <div className="flex min-h-0 flex-1">
          <Sidebar status={status} open={mobileNav} onNavigate={() => setMobileNav(false)} />
          <main className="min-w-0 flex-1 overflow-y-auto">
            {status?.emergencyStop && (
              <div className="flex items-center gap-2 border-b border-ruby/40 bg-ruby/10 px-6 py-2 text-[13px] text-ruby">
                <OctagonX size={16} /> EMERGENCY STOP aktywny — żadne nowe wykonania agentów ani workflowy nie zostaną uruchomione.
              </div>
            )}
            <div className="mx-auto max-w-[1500px] p-4 sm:p-6"><Outlet /></div>
          </main>
        </div>
      </div>
    </StatusCtx.Provider>
  );
}

function Sidebar({ status, open, onNavigate }: { status: StudioStatus | null; open: boolean; onNavigate: () => void }) {
  return (
    <nav className={cx('w-60 shrink-0 overflow-y-auto border-r border-line bg-panel py-3', 'max-lg:fixed max-lg:inset-y-12 max-lg:left-0 max-lg:z-40 max-lg:shadow-2xl', open ? '' : 'max-lg:hidden')}>
      {NAV.map((g) => (
        <div key={g.group} className="mb-3">
          <div className="px-4 pb-1 text-[10.5px] font-semibold tracking-wider text-faint">{g.group}</div>
          {g.items.map((it) => (
            <NavLink key={it.to} to={it.to} end={it.end} onClick={onNavigate}
              className={({ isActive }) => cx('mx-2 flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[13px] transition-colors',
                isActive ? 'bg-gold/10 text-gold' : 'text-mute hover:bg-panel3 hover:text-ink')}>
              <it.icon size={15} />
              <span className="flex-1 truncate">{it.label}</span>
              {it.to === '/approvals' && !!status?.pendingApprovals && <span className="rounded-full bg-gold px-1.5 text-[10px] font-bold text-black">{status.pendingApprovals}</span>}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}

function Pill({ ok, label, icon, title, warn }: { ok: boolean; label: ReactNode; icon: ReactNode; title?: string; warn?: boolean }) {
  const color = ok ? '#34d399' : warn ? '#f5c542' : '#f05252';
  return (
    <span title={title} className="hidden md:inline-flex items-center gap-1.5 rounded-md border border-line bg-panel2 px-2 py-1 text-[11.5px] text-mute">
      {icon}<span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />{label}
    </span>
  );
}

function TopBar({ status, reload, onMenu }: { status: StudioStatus | null; reload: () => void; onMenu: () => void }) {
  const [confirm, setConfirm] = useState(false);
  const stop = useAction((active: boolean) => api('/emergency-stop', { body: { active } }), {
    success: (r: any) => (r.active ? `EMERGENCY STOP: przerwano ${r.stopped} wykonań` : 'Emergency Stop wyłączony'),
    onDone: () => { setConfirm(false); reload(); },
  });
  const mode = useAction((autonomyMode: string) => api('/settings', { method: 'PATCH', body: { autonomyMode } }), { success: 'Zmieniono tryb autonomii', onDone: reload });

  return (
    <header className="flex h-12 shrink-0 items-center gap-3 border-b border-line bg-panel px-3">
      <button className="lg:hidden rounded p-1.5 text-mute hover:bg-panel3" onClick={onMenu}><Menu size={18} /></button>
      <Link to="/" className="flex items-center gap-2 pr-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-md border-2 border-black bg-gold" style={{ boxShadow: '2px 2px 0 #000' }}>
          <Sparkles size={15} color="#000" strokeWidth={2.6} />
        </div>
        <div className="leading-tight">
          <div className="brand-mark text-[14px] text-gold">BLOCKY &amp; CRYCKET</div>
          <div className="text-[10px] text-faint -mt-0.5">AI Development Studio</div>
        </div>
      </Link>
      {status && (
        <>
          <span className="hidden xl:inline-flex rounded-md border border-gold/30 bg-gold/10 px-2 py-1 text-[11.5px] font-medium text-gold">{status.phase}</span>
          <Pill ok={!!status.branch} warn label={status.branch ?? 'brak Git'} icon={<GitBranch size={12} />} title="Gałąź Git" />
          <Pill ok={status.activeAgents > 0} warn label={`${status.activeAgents} aktywnych`} icon={<Bot size={12} />} title="Agenci w trakcie pracy" />
          <Link to="/approvals"><Pill ok={status.pendingApprovals === 0} warn label={`${status.pendingApprovals} zatwierdzeń`} icon={<CheckCheck size={12} />} /></Link>
          <div className="flex-1" />
          <Pill ok={status.studio.open} warn label="Studio" icon={<MonitorPlay size={12} />} title={status.studio.open ? 'Miejsce otwarte w Roblox Studio (.rbxl.lock)' : 'Studio zamknięte'} />
          <Pill ok={status.rojo.connected} label={`Rojo${status.rojo.connected ? ` ${status.rojo.serverVersion}` : ''}`} icon={<Radio size={12} />} title={status.rojo.connected ? `rojo serve :${status.rojo.port}` : 'rojo serve nie działa'} />
          <Pill ok={status.ai.configured} label={status.ai.configured ? 'Claude API' : 'AI: NOT CONFIGURED'} icon={<Cpu size={12} />} />
          <select value={status.autonomyMode} onChange={(e) => mode.run(e.target.value)} title="Globalny tryb autonomii"
            className="h-7 rounded-md border border-line2 bg-panel2 px-1.5 text-[11.5px] text-ink cursor-pointer">
            <option value="assistant">ASSISTANT</option>
            <option value="semi">SEMI-AUTONOMOUS</option>
            <option value="autonomous">AUTONOMOUS</option>
          </select>
          {status.emergencyStop ? (
            <button onClick={() => stop.run(false)} className="flex h-7 items-center gap-1.5 rounded-md border border-mint/40 bg-mint/10 px-2.5 text-[11.5px] font-semibold text-mint cursor-pointer">Wznów pracę</button>
          ) : (
            <button onClick={() => setConfirm(true)} className="flex h-7 items-center gap-1.5 rounded-md bg-ruby px-2.5 text-[11.5px] font-bold text-white hover:bg-[#ff6464] cursor-pointer">
              <OctagonX size={14} /> STOP
            </button>
          )}
        </>
      )}
      <Confirm open={confirm} onClose={() => setConfirm(false)} danger loading={stop.loading} title="Emergency Stop"
        text={<>Przerwie <b>{status?.runningExecutions ?? 0}</b> trwających wykonań agentów, zatrzyma workflowy i zablokuje nowe uruchomienia do czasu wznowienia.</>}
        onConfirm={() => stop.run(true)} />
    </header>
  );
}
