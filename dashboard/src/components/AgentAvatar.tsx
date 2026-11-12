import { Crown, Code2, LayoutDashboard, Box, Palette, ShieldCheck, Network, Swords, Scale, BookOpen, Bot } from 'lucide-react';
import { AGENT_STATUS } from '../lib/api';
import { cx } from './ui';

const ICONS: Record<string, any> = { Crown, Code2, LayoutDashboard, Box, Palette, ShieldCheck, Network, Swords, Scale, BookOpen };

export function AgentAvatar({ agent, size = 36, showStatus = true }: { agent: { name: string; color?: string; icon?: string; status?: string }; size?: number; showStatus?: boolean }) {
  const Icon = ICONS[agent.icon ?? ''] ?? Bot;
  const color = agent.color ?? '#8a93a6';
  const st = AGENT_STATUS[agent.status ?? 'idle'];
  const busy = agent.status === 'working' || agent.status === 'thinking';
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <div className={cx('flex h-full w-full items-center justify-center rounded-lg border-2 border-black', busy && 'pulse-ring')}
        style={{ background: `linear-gradient(135deg, ${color} 0%, ${color}b0 100%)`, boxShadow: '2px 2px 0 #000' }}>
        <Icon size={size * 0.5} color="#0c0f15" strokeWidth={2.4} />
      </div>
      {showStatus && st && <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-panel" style={{ background: st.color }} title={st.label} />}
    </div>
  );
}
