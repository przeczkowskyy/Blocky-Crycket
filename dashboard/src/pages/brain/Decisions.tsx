import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Gavel, Plus, Check, X, Replace, HelpCircle, Send } from 'lucide-react';
import { api, useApi, DECISION_STATUS, fmtDateTime } from '../../lib/api';
import { Badge, Button, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, StatusBadge, Tabs, Textarea, useAction, Card } from '../../components/ui';

const CATS = ['game_design', 'art_direction', 'technical', 'ui', 'economy', 'roadmap', 'tooling'];

export function Decisions() {
  const [params, setParams] = useSearchParams();
  const tab = (params.get('tab') ?? 'pending') as 'approved' | 'pending' | 'rejected' | 'superseded' | 'questions';
  const { data: decisions, error, reload } = useApi<any[]>('/decisions', 8000);
  const { data: questions, reload: reloadQ } = useApi<any[]>('/questions', 8000);
  const [adding, setAdding] = useState(false);
  const [supersede, setSupersede] = useState<any>(null);
  const setStatus = useAction((id: string, status: string) => api(`/decisions/${id}`, { method: 'PATCH', body: { status } }), { success: 'Zmieniono status decyzji', onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!decisions || !questions) return <Spinner />;
  const by = (s: string[]) => decisions.filter((d) => s.includes(d.status));
  const lists: Record<string, any[]> = { approved: by(['approved']), pending: by(['proposed', 'awaiting_approval']), rejected: by(['rejected']), superseded: by(['superseded']) };
  const openQ = questions.filter((q) => q.status === 'open');

  return (
    <div>
      <PageHeader icon={<Gavel size={20} className="text-gold" />} title="Decisions & Rules" subtitle="Tylko zatwierdzone decyzje są autorytatywne i trafiają do każdego kontekstu agenta. Zatwierdzonej decyzji się nie edytuje — zastępuje się ją nową (supersede), zachowując historię."
        actions={<Button variant="primary" icon={<Plus size={14} />} onClick={() => setAdding(true)}>Nowa decyzja</Button>} />
      <Tabs value={tab} onChange={(t) => setParams({ tab: t })} className="mb-4" tabs={[
        { id: 'pending', label: 'Oczekujące', count: lists.pending.length }, { id: 'approved', label: 'Zatwierdzone', count: lists.approved.length },
        { id: 'rejected', label: 'Odrzucone', count: lists.rejected.length }, { id: 'superseded', label: 'Zastąpione', count: lists.superseded.length },
        { id: 'questions', label: 'Pytania', count: openQ.length },
      ]} />
      {tab === 'questions' ? <Questions questions={questions} onChanged={reloadQ} /> : lists[tab].length === 0 ? <Card><Empty title="Brak decyzji" /></Card> : (
        <div className="grid gap-3 lg:grid-cols-2">
          {lists[tab].map((d) => {
            const sup = d.supersedes_decision_id ? decisions.find((x) => x.id === d.supersedes_decision_id) : null;
            return (
              <div key={d.id} className="rounded-lg border border-line bg-panel p-4">
                <div className="flex items-start justify-between gap-2">
                  <div><span className="font-mono text-[11px] text-faint">{d.code}</span> <span className="font-semibold">{d.title}</span></div>
                  <StatusBadge map={DECISION_STATUS} value={d.status} />
                </div>
                <p className="mt-2 whitespace-pre-wrap text-[12.5px] text-mute">{d.description}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-faint">
                  <Badge color="#a78bfa">{d.category}</Badge>
                  <span>zaproponował: {d.proposed_by}</span>
                  {d.approved_by && <span>· zatwierdził: {d.approved_by} ({fmtDateTime(d.approved_at)})</span>}
                  {sup && <span>· zastępuje {sup.code}</span>}
                  {(d.related_docs ?? []).length > 0 && <span>· {d.related_docs.join(', ')}</span>}
                </div>
                <div className="mt-3 flex gap-1.5">
                  {['proposed', 'awaiting_approval'].includes(d.status) && <>
                    <Button size="sm" variant="success" icon={<Check size={12} />} onClick={() => setStatus.run(d.id, 'approved')}>Zatwierdź</Button>
                    <Button size="sm" variant="danger" icon={<X size={12} />} onClick={() => setStatus.run(d.id, 'rejected')}>Odrzuć</Button>
                  </>}
                  {d.status === 'approved' && <Button size="sm" icon={<Replace size={12} />} onClick={() => setSupersede(d)}>Zastąp nową decyzją</Button>}
                  {d.status === 'rejected' && <Button size="sm" onClick={() => setStatus.run(d.id, 'awaiting_approval')}>Przywróć do rozważenia</Button>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      <DecisionForm open={adding} title="Nowa decyzja" onClose={() => setAdding(false)} submit={(f) => api('/decisions', { body: f })} onDone={() => { setAdding(false); reload(); }} allowApproved />
      <DecisionForm open={!!supersede} title={`Zastąp ${supersede?.code}: ${supersede?.title}`} initial={supersede} onClose={() => setSupersede(null)} submit={(f) => api(`/decisions/${supersede.id}/supersede`, { body: f })} onDone={() => { setSupersede(null); reload(); }} />
    </div>
  );
}

function DecisionForm({ open, title, initial, onClose, submit, onDone, allowApproved }: { open: boolean; title: string; initial?: any; onClose: () => void; submit: (f: any) => Promise<any>; onDone: () => void; allowApproved?: boolean }) {
  const [f, setF] = useState<any>({ title: '', description: '', category: 'game_design', status: 'proposed' });
  const [prev, setPrev] = useState<any>(null);
  if (open && initial !== prev) { setPrev(initial); setF({ title: initial?.title ?? '', description: initial?.description ?? '', category: initial?.category ?? 'game_design', status: 'proposed' }); }
  const go = useAction(() => submit(f), { success: 'Zapisano decyzję', onDone });
  return (
    <Modal open={open} onClose={onClose} title={title} footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={!f.title.trim() || !f.description.trim()} loading={go.loading} onClick={() => go.run()}>Zapisz</Button></>}>
      <div className="space-y-3">
        <Field label="Tytuł"><Input value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} /></Field>
        <Field label="Opis"><Textarea value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} /></Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Kategoria"><Select value={f.category} onChange={(e) => setF({ ...f, category: e.target.value })}>{CATS.map((c) => <option key={c}>{c}</option>)}</Select></Field>
          {allowApproved && <Field label="Status"><Select value={f.status} onChange={(e) => setF({ ...f, status: e.target.value })}><option value="proposed">Proposed</option><option value="approved">Approved (moja decyzja)</option></Select></Field>}
        </div>
        {initial && <p className="text-[11px] text-faint">Nowa decyzja zostanie od razu zatwierdzona, a {initial.code} oznaczona jako Superseded.</p>}
      </div>
    </Modal>
  );
}

function Questions({ questions, onChanged }: { questions: any[]; onChanged: () => void }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [newQ, setNewQ] = useState('');
  const answer = useAction((id: string, body: any) => api(`/questions/${id}`, { method: 'PATCH', body }), { success: 'Zapisano odpowiedź', onDone: onChanged });
  const add = useAction(() => api('/questions', { body: { question: newQ } }), { onDone: () => { setNewQ(''); onChanged(); } });
  return (
    <div className="space-y-3">
      <p className="text-[12px] text-mute">Pytania i niejasności zgłoszone przez agentów lub wykryte przy indeksowaniu. Odpowiedzi trafiają do kontekstu jako zamknięte pytania; jeśli odpowiedź jest decyzją projektową — dodaj ją też jako decyzję.</p>
      <div className="flex gap-2"><Input value={newQ} onChange={(e) => setNewQ(e.target.value)} placeholder="Dodaj własne pytanie otwarte…" /><Button icon={<Plus size={13} />} disabled={!newQ.trim()} loading={add.loading} onClick={() => add.run()}>Dodaj</Button></div>
      {questions.length === 0 && <Empty title="Brak pytań" />}
      {questions.map((q) => (
        <div key={q.id} className="rounded-lg border border-line bg-panel p-4">
          <div className="flex items-start gap-2"><HelpCircle size={16} className={q.status === 'open' ? 'text-amber' : 'text-mint'} /><div className="flex-1"><div className="font-medium">{q.question}</div>{q.context && <div className="mt-1 text-[12px] text-mute">{q.context}</div>}<div className="mt-1 text-[11px] text-faint">zgłosił: {q.raised_by} · {fmtDateTime(q.created_at)}</div></div><Badge color={q.status === 'open' ? '#f5c542' : '#34d399'}>{q.status === 'open' ? 'otwarte' : q.status === 'dismissed' ? 'odrzucone' : 'odpowiedziane'}</Badge></div>
          {q.answer && <div className="mt-2 rounded bg-mint/5 px-3 py-2 text-[12.5px]"><b className="text-mint">Odpowiedź:</b> {q.answer}</div>}
          {q.status === 'open' && (
            <div className="mt-3 flex gap-2">
              <Input value={answers[q.id] ?? ''} onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })} placeholder="Twoja odpowiedź…" />
              <Button icon={<Send size={13} />} disabled={!answers[q.id]?.trim()} onClick={() => answer.run(q.id, { answer: answers[q.id] })}>Odpowiedz</Button>
              <Button variant="ghost" onClick={() => answer.run(q.id, { status: 'dismissed' })}>Odrzuć</Button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
