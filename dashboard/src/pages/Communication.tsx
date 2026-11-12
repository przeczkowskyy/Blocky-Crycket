import { useEffect, useRef, useState } from 'react';
import { MessagesSquare, Send, Loader2, FileCode2, ListPlus, Gavel } from 'lucide-react';
import { api, useApi, fmtTime } from '../lib/api';
import { Badge, Button, PageHeader, Textarea, useAction, cx, NotConfigured, Card } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { Markdown } from '../components/Markdown';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

export function Communication() {
  const { status } = useStatus();
  return (
    <div>
      <PageHeader icon={<MessagesSquare size={20} className="text-gold" />} title="Agent Communication"
        subtitle={<>Wspólny czat zespołu. Bez wzmianki odpowiada ATLAS (koordynator). Wspomnij agentów: <code className="text-gold">@PIXEL</code>, <code className="text-gold">@LUCIUS</code>, <code className="text-gold">@SENTINEL</code>, <code className="text-gold">@LOREKEEPER</code>…</>}
        actions={!status?.ai.configured && <NotConfigured />} />
      <Card bodyClass="p-0"><ChatThread height="h-[calc(100vh-230px)]" /></Card>
    </div>
  );
}

export function ChatThread({ fixedMention, height }: { fixedMention?: string; height: string }) {
  const { data: msgs, reload } = useApi<any[]>('/chat', 2500);
  const { data: agents } = useApi<any[]>('/agents', 3000);
  const { data: execs } = useApi<any[]>('/executions', 2500);
  const [text, setText] = useState('');
  const [exec, setExec] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const send = useAction(() => api('/chat', { body: { body: fixedMention && !text.includes('@') ? `@${fixedMention.replace(/\s/g, '_')} ${text}` : text } }), { onDone: () => { setText(''); reload(); } });

  const shown = (msgs ?? []).filter((m) => !fixedMention || m.author === fixedMention || m.body.toUpperCase().includes(`@${fixedMention.replace(/\s/g, '_')}`) || (m.author_type === 'system' && m.body.startsWith(fixedMention)));
  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }); }, [shown.length]);
  const pending = (execs ?? []).filter((e) => e.status === 'running' && e.chat_message_id);
  const agentByName = (n: string) => agents?.find((a) => a.name === n);

  return (
    <div className={cx('flex flex-col', height)}>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {shown.length === 0 && <div className="py-10 text-center text-xs text-faint">Brak wiadomości. Napisz pierwszą — np. „@ATLAS jaki jest plan na Sprint 1?”</div>}
        {shown.map((m) => {
          const ag = m.author_type === 'agent' ? agentByName(m.author) : null;
          if (m.author_type === 'system') return <div key={m.id} className="mx-auto max-w-2xl rounded-md border border-ruby/30 bg-ruby/5 px-3 py-1.5 text-center text-[12px] text-ruby">{m.body}</div>;
          const mine = m.author_type === 'user';
          return (
            <div key={m.id} className={cx('flex gap-2.5', mine && 'flex-row-reverse')}>
              {ag ? <AgentAvatar agent={ag} size={30} showStatus={false} /> : <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-lg bg-gold text-[11px] font-bold text-black">GD</div>}
              <div className={cx('max-w-[78%] rounded-lg border px-3 py-2', mine ? 'border-gold/30 bg-gold/5' : 'border-line bg-panel2')}>
                <div className="mb-0.5 flex items-center gap-2 text-[11px]"><b style={{ color: ag?.color }}>{m.author}</b><span className="text-faint">{fmtTime(m.created_at)}</span></div>
                {mine ? <div className="whitespace-pre-wrap text-[13px]">{m.body}</div> : <Markdown text={m.body} className="text-[13px]" />}
                {m.meta?.processed && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {m.meta.processed.approvals > 0 && <Badge color="#f5c542"><FileCode2 size={11} /> {m.meta.processed.approvals} zmian do zatwierdzenia</Badge>}
                    {m.meta.processed.tasks > 0 && <Badge color="#60a5fa"><ListPlus size={11} /> {m.meta.processed.tasks} zadań</Badge>}
                    {m.meta.processed.decisions > 0 && <Badge color="#a78bfa"><Gavel size={11} /> {m.meta.processed.decisions} decyzji</Badge>}
                    {m.execution_id && <button className="text-[11px] text-cyan hover:underline cursor-pointer" onClick={() => setExec(m.execution_id)}>szczegóły i źródła →</button>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {pending.map((e) => (
          <div key={e.id} className="flex items-center gap-2 text-[12px] text-mute"><Loader2 size={14} className="animate-spin text-cyan" /> {e.agent_name} pracuje nad odpowiedzią…</div>
        ))}
        <div ref={bottom} />
      </div>
      <form className="flex gap-2 border-t border-line p-3" onSubmit={(e) => { e.preventDefault(); if (text.trim()) void send.run(); }}>
        <Textarea className="min-h-[44px] flex-1" rows={2} value={text} placeholder={fixedMention ? `Wiadomość do ${fixedMention}…` : 'Wiadomość do zespołu (@AGENT, aby wskazać adresata)…'}
          onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (text.trim()) void send.run(); } }} />
        <Button type="submit" variant="primary" icon={<Send size={14} />} loading={send.loading} disabled={!text.trim()}>Wyślij</Button>
      </form>
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}
