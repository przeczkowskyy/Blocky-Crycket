import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bug, Plus, Workflow } from 'lucide-react';
import { api, useApi, PRIORITY, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, Tabs, Textarea, useAction, NotConfigured } from '../components/ui';
import { useStatus } from '../components/Layout';

const BUG_STATUS: Record<string, { label: string; color: string }> = { open: { label: 'Otwarty', color: '#f05252' }, in_progress: { label: 'W naprawie', color: '#22d3ee' }, fixed: { label: 'Naprawiony (do re-testu)', color: '#a78bfa' }, resolved: { label: 'Rozwiązany', color: '#34d399' }, closed: { label: 'Zamknięty', color: '#5d6678' } };
const CATS = ['ui', 'luau', 'gameplay', 'performance', 'assets', 'integration'];

export function Bugs() {
  const { data: bugs, error, reload } = useApi<any[]>('/bugs', 6000);
  const { data: agents } = useApi<any[]>('/agents');
  const { status } = useStatus();
  const [tab, setTab] = useState<'open' | 'all'>('open');
  const [cat, setCat] = useState('');
  const [sel, setSel] = useState<any>(null);
  const [adding, setAdding] = useState(false);
  const patch = useAction((id: string, body: any) => api(`/bugs/${id}`, { method: 'PATCH', body }), { onDone: reload });
  const wf = useAction((id: string) => api(`/bugs/${id}/workflow`, { body: {} }), { success: 'Uruchomiono Workflow D — Naprawa błędu', onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!bugs) return <Spinner />;
  const list = bugs.filter((b) => (tab === 'all' || !['resolved', 'closed'].includes(b.status)) && (!cat || b.category === cat));

  return (
    <div>
      <PageHeader icon={<Bug size={20} className="text-gold" />} title="Bug Tracker" subtitle="Błędy zgłaszane przez Ciebie i przez SENTINEL. „Napraw przez workflow” uruchamia Workflow D: diagnoza → poprawka → re-test → Twoje zatwierdzenie."
        actions={<>{!status?.ai.configured && <NotConfigured />}<Select className="w-36" value={cat} onChange={(e) => setCat(e.target.value)}><option value="">Każda kategoria</option>{CATS.map((c) => <option key={c}>{c}</option>)}</Select><Button variant="primary" icon={<Plus size={14} />} onClick={() => setAdding(true)}>Zgłoś błąd</Button></>} />
      <Tabs value={tab} onChange={setTab} className="mb-4" tabs={[{ id: 'open', label: 'Otwarte', count: bugs.filter((b) => !['resolved', 'closed'].includes(b.status)).length }, { id: 'all', label: 'Wszystkie', count: bugs.length }]} />
      {list.length === 0 ? <Card><Empty icon={<Bug size={30} />} title="Brak błędów">Nie ma tu danych demo — pojawią się prawdziwe zgłoszenia.</Empty></Card> : (
        <Card bodyClass="p-0">
          <table className="w-full text-[12.5px]">
            <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Błąd</th><th>Ważność</th><th>Kategoria</th><th>Agent</th><th>Status</th><th>Zgłosił</th><th /></tr></thead>
            <tbody>
              {list.map((b) => (
                <tr key={b.id} className="cursor-pointer border-b border-line last:border-0 hover:bg-panel2" onClick={() => setSel(b)}>
                  <td className="px-4 py-2.5"><div className="font-medium">{b.title}</div><div className="max-w-md truncate text-[11.5px] text-mute">{b.description}</div></td>
                  <td><Badge color={PRIORITY[b.severity]?.color}>{b.severity}</Badge></td>
                  <td className="text-mute">{b.category}</td>
                  <td>{agents?.find((a) => a.id === b.assigned_agent_id)?.name ?? '—'}</td>
                  <td><Badge color={BUG_STATUS[b.status]?.color}>{BUG_STATUS[b.status]?.label}</Badge></td>
                  <td className="text-[11px] text-faint">{b.reported_by}<br />{fmtDateTime(b.created_at)}</td>
                  <td className="pr-4 text-right" onClick={(e) => e.stopPropagation()}><Button size="sm" icon={<Workflow size={12} />} disabled={!status?.ai.configured || b.status === 'resolved'} loading={wf.loading} onClick={() => wf.run(b.id)}>Napraw przez workflow</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      <Modal open={!!sel} onClose={() => setSel(null)} title={sel?.title} width="max-w-2xl">
        {sel && (
          <div className="space-y-3 text-[13px]">
            <div className="grid grid-cols-3 gap-2">
              <Field label="Status"><Select value={sel.status} onChange={(e) => { setSel({ ...sel, status: e.target.value }); patch.run(sel.id, { status: e.target.value }); }}>{Object.entries(BUG_STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></Field>
              <Field label="Ważność"><Select value={sel.severity} onChange={(e) => { setSel({ ...sel, severity: e.target.value }); patch.run(sel.id, { severity: e.target.value }); }}>{Object.keys(PRIORITY).map((k) => <option key={k}>{k}</option>)}</Select></Field>
              <Field label="Agent"><Select value={sel.assigned_agent_id ?? ''} onChange={(e) => { setSel({ ...sel, assigned_agent_id: e.target.value }); patch.run(sel.id, { assigned_agent_id: e.target.value }); }}>{(agents ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></Field>
            </div>
            <div><div className="text-xs text-mute">Opis</div><div className="whitespace-pre-wrap">{sel.description || '—'}</div></div>
            <div><div className="text-xs text-mute">Kroki reprodukcji</div><div className="whitespace-pre-wrap">{sel.repro_steps || '—'}</div></div>
            <div><div className="text-xs text-mute">Pliki</div>{(sel.related_files ?? []).map((f: string) => <Link key={f} to={`/workspace?file=${encodeURIComponent(f)}`} className="mr-2 font-mono text-[12px] text-cyan hover:underline">{f}</Link>)}</div>
            <Field label="Wynik testu"><Input defaultValue={sel.test_result ?? ''} onBlur={(e) => patch.run(sel.id, { test_result: e.target.value })} placeholder="np. Re-test w Studio OK" /></Field>
          </div>
        )}
      </Modal>
      <NewBug open={adding} agents={agents ?? []} onClose={() => setAdding(false)} onDone={() => { setAdding(false); reload(); }} />
    </div>
  );
}

function NewBug({ open, agents, onClose, onDone }: { open: boolean; agents: any[]; onClose: () => void; onDone: () => void }) {
  const [f, setF] = useState({ title: '', description: '', severity: 'medium', category: 'luau', assigned_agent_id: 'sentinel', repro_steps: '', related_files: '' });
  const add = useAction(() => api('/bugs', { body: { ...f, related_files: f.related_files.split(',').map((x) => x.trim()).filter(Boolean) } }), { success: 'Zgłoszono błąd', onDone: () => { setF({ ...f, title: '', description: '', repro_steps: '', related_files: '' }); onDone(); } });
  return (
    <Modal open={open} onClose={onClose} title="Zgłoś błąd" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={!f.title.trim()} loading={add.loading} onClick={() => add.run()}>Zgłoś</Button></>}>
      <div className="space-y-3">
        <Field label="Tytuł"><Input value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} /></Field>
        <div className="grid grid-cols-3 gap-2">
          <Field label="Ważność"><Select value={f.severity} onChange={(e) => setF({ ...f, severity: e.target.value })}>{Object.keys(PRIORITY).map((k) => <option key={k}>{k}</option>)}</Select></Field>
          <Field label="Kategoria"><Select value={f.category} onChange={(e) => setF({ ...f, category: e.target.value })}>{CATS.map((c) => <option key={c}>{c}</option>)}</Select></Field>
          <Field label="Agent"><Select value={f.assigned_agent_id} onChange={(e) => setF({ ...f, assigned_agent_id: e.target.value })}>{agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></Field>
        </div>
        <Field label="Opis"><Textarea value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} /></Field>
        <Field label="Kroki reprodukcji / log z Output"><Textarea className="font-mono text-[12px]" value={f.repro_steps} onChange={(e) => setF({ ...f, repro_steps: e.target.value })} /></Field>
        <Field label="Pliki (po przecinku)"><Input value={f.related_files} onChange={(e) => setF({ ...f, related_files: e.target.value })} /></Field>
      </div>
    </Modal>
  );
}
