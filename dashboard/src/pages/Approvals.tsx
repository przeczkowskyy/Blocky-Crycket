import { useState } from 'react';
import { Link } from 'react-router-dom';
import { DiffEditor } from '@monaco-editor/react';
import '../components/monaco';
import { MONACO_OPTIONS } from '../components/monaco';
import { CheckCheck, Check, X, MessageSquareWarning, RadioTower, ShieldAlert, AlertTriangle, FileCode2 } from 'lucide-react';
import { api, useApi, fmtDateTime, timeAgo } from '../lib/api';
import { Badge, Button, Empty, ErrorBox, Field, Modal, PageHeader, Spinner, Tabs, Textarea, useAction, cx } from '../components/ui';
import { ExecutionModal } from '../components/ExecutionView';
import { AgentAvatar } from '../components/AgentAvatar';

const ST: Record<string, { label: string; color: string }> = {
  pending: { label: 'Oczekuje', color: '#f5c542' }, approved: { label: 'Zatwierdzone', color: '#34d399' }, rejected: { label: 'Odrzucone', color: '#f05252' },
  changes_requested: { label: 'Poprawki', color: '#fb923c' }, superseded: { label: 'Zastąpione', color: '#5d6678' },
};

export function Approvals() {
  const { data: list, error, reload } = useApi<any[]>('/approvals', 4000);
  const { data: agents } = useApi<any[]>('/agents');
  const [tab, setTab] = useState<'pending' | 'done'>('pending');
  const [sel, setSel] = useState<string | null>(null);
  if (error) return <ErrorBox error={error} />;
  if (!list) return <Spinner />;
  const pending = list.filter((a) => a.status === 'pending');
  const done = list.filter((a) => a.status !== 'pending');
  const shown = tab === 'pending' ? pending : done;
  const current = list.find((a) => a.id === sel) ?? shown[0];
  const agentOf = (id: string) => agents?.find((a) => a.id === id);

  return (
    <div>
      <PageHeader icon={<CheckCheck size={20} className="text-gold" />} title="Approval Center"
        subtitle="Human-in-the-loop. Zatwierdzenie zapisuje plik na dysku (z kopią w historii wersji); działający `rojo serve` od razu przesyła go do Studio. Nic nie jest publikowane bez Twojej zgody." />
      <Tabs value={tab} onChange={(t) => { setTab(t); setSel(null); }} className="mb-4" tabs={[{ id: 'pending', label: 'Oczekujące', count: pending.length }, { id: 'done', label: 'Rozpatrzone', count: done.length }]} />
      {shown.length === 0 ? <Empty icon={<CheckCheck size={32} />} title={tab === 'pending' ? 'Brak zmian do zatwierdzenia' : 'Brak historii'}>Zmiany zaproponowane przez agentów pojawią się tutaj jako diff.</Empty> : (
        <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
          <div className="space-y-1.5">
            {shown.map((a) => {
              const ag = agentOf(a.agent_id);
              return (
                <button key={a.id} onClick={() => setSel(a.id)} className={cx('w-full rounded-md border p-2.5 text-left cursor-pointer', current?.id === a.id ? 'border-gold/50 bg-gold/5' : 'border-line bg-panel hover:border-line2')}>
                  <div className="flex items-center gap-2">{ag && <AgentAvatar agent={ag} size={20} showStatus={false} />}<span className="flex-1 truncate text-[12.5px] font-medium">{a.title}</span></div>
                  <div className="mt-1 flex flex-wrap items-center gap-1">
                    <Badge color={ST[a.status]?.color}>{ST[a.status]?.label}</Badge>
                    {a.proposed_changes?.protected && <Badge color="#fb923c">chroniony</Badge>}
                    {a.conflict && <Badge color="#f05252">konflikt</Badge>}
                    <span className="ml-auto text-[10.5px] text-faint">{timeAgo(a.created_at)}</span>
                  </div>
                </button>
              );
            })}
          </div>
          {current && <ApprovalDetail key={current.id} a={current} agent={agentOf(current.agent_id)} onDone={() => { setSel(null); reload(); }} />}
        </div>
      )}
    </div>
  );
}

function ApprovalDetail({ a, agent, onDone }: { a: any; agent: any; onDone: () => void }) {
  const [exec, setExec] = useState<string | null>(null);
  const [reqOpen, setReqOpen] = useState(false);
  const [rejOpen, setRejOpen] = useState(false);
  const [comment, setComment] = useState('');
  const pc = a.proposed_changes ?? {};
  const act = useAction(async (action: string, body: any = {}) => {
    try { return await api<any>(`/approvals/${a.id}/${action}`, { body }); }
    catch (e: any) {
      if (e.status === 409 && window.confirm(`${e.message}\n\nZatwierdzić mimo to (nadpisze obecną wersję pliku)?`)) return api<any>(`/approvals/${a.id}/${action}`, { body: { ...body, force: true } });
      throw e;
    }
  }, {
    success: (r: any) => (r?.sync ? r.sync.detail : r?.executionId ? 'Poproszono agenta o poprawki — nowa propozycja pojawi się tutaj' : 'Zapisano decyzję'),
    onDone: () => { setReqOpen(false); setRejOpen(false); setComment(''); onDone(); },
  });
  const pending = a.status === 'pending';
  const lang = pc.path?.endsWith('.json') ? 'json' : pc.path?.endsWith('.md') ? 'markdown' : 'lua';

  return (
    <div className="rounded-lg border border-line bg-panel">
      <div className="flex flex-wrap items-center gap-2 border-b border-line px-4 py-3">
        <FileCode2 size={16} className="text-gold" />
        <span className="font-mono text-[13px]">{pc.path}</span>
        {pc.before === null && <Badge color="#34d399">nowy plik</Badge>}
        {pc.protected && <Badge color="#fb923c"><ShieldAlert size={11} />plik chroniony</Badge>}
        {a.conflict && <Badge color="#f05252"><AlertTriangle size={11} />plik był zablokowany przez inne wykonanie</Badge>}
        <div className="flex-1" />
        {pending && <>
          <Button size="sm" variant="danger" icon={<X size={13} />} onClick={() => setRejOpen(true)}>Odrzuć</Button>
          <Button size="sm" icon={<MessageSquareWarning size={13} />} onClick={() => setReqOpen(true)}>Poproś o poprawki</Button>
          <Button size="sm" variant="success" icon={<Check size={13} />} loading={act.loading} onClick={() => act.run('approve')}>Zatwierdź</Button>
          <Button size="sm" variant="primary" icon={<RadioTower size={13} />} loading={act.loading} onClick={() => act.run('approve-sync')}>Zatwierdź i synchronizuj</Button>
        </>}
      </div>
      <div className="grid gap-3 border-b border-line px-4 py-3 text-[12.5px] md:grid-cols-[1fr_auto]">
        <div>
          <div className="text-mute">Wyjaśnienie agenta {agent ? <b className="text-ink">{agent.name}</b> : ''}:</div>
          <div className="mt-0.5">{a.explanation ?? '—'}</div>
          {a.review_comment && <div className="mt-2 text-amber">Komentarz recenzji: {a.review_comment}</div>}
        </div>
        <div className="text-right text-[11px] text-faint">
          <div>{fmtDateTime(a.created_at)}</div>
          {a.execution_id && <button className="text-cyan hover:underline cursor-pointer" onClick={() => setExec(a.execution_id)}>wykonanie i kontekst Brain →</button>}
          {a.task_id && <div><Link to="/tasks" className="text-cyan hover:underline">powiązane zadanie →</Link></div>}
        </div>
      </div>
      <div className="h-[560px]">
        <DiffEditor theme="studio-dark" original={pc.before ?? ''} modified={pc.after ?? ''} language={lang} options={{ ...MONACO_OPTIONS, readOnly: true, renderSideBySide: true, originalEditable: false }} />
      </div>
      <Modal open={reqOpen} onClose={() => setReqOpen(false)} title="Poproś o poprawki" footer={<><Button variant="ghost" onClick={() => setReqOpen(false)}>Anuluj</Button><Button variant="primary" disabled={!comment.trim()} loading={act.loading} onClick={() => act.run('request-changes', { comment })}>Wyślij do agenta</Button></>}>
        <Field label="Co poprawić?" hint="Agent otrzyma Twój komentarz i poprzednią propozycję, po czym przygotuje nową wersję."><Textarea autoFocus value={comment} onChange={(e) => setComment(e.target.value)} /></Field>
      </Modal>
      <Modal open={rejOpen} onClose={() => setRejOpen(false)} title="Odrzuć zmianę" footer={<><Button variant="ghost" onClick={() => setRejOpen(false)}>Anuluj</Button><Button variant="danger" loading={act.loading} onClick={() => act.run('reject', { comment: comment || null })}>Odrzuć</Button></>}>
        <Field label="Powód (opcjonalnie)"><Textarea value={comment} onChange={(e) => setComment(e.target.value)} /></Field>
      </Modal>
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}
