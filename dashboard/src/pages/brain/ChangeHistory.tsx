import { useState } from 'react';
import { Link } from 'react-router-dom';
import { History, Check, X, Brain, BookText, FileCode2 } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, PageHeader, Spinner, Tabs, useAction } from '../../components/ui';
import { ExecutionModal } from '../../components/ExecutionView';

const ST: Record<string, string> = { pending: '#f5c542', approved: '#34d399', rejected: '#f05252' };

export function ChangeHistory() {
  const [tab, setTab] = useState<'updates' | 'docs' | 'decisions' | 'files'>('updates');
  const { data: updates, error, reload } = useApi<any[]>('/brain/updates', 6000);
  const { data: logs } = useApi<any[]>(tab === 'docs' ? '/logs?entity_type=document&limit=200' : tab === 'decisions' ? '/logs?entity_type=decision&limit=200' : tab === 'files' ? '/logs?entity_type=file&limit=300' : null);
  const [exec, setExec] = useState<string | null>(null);
  const [facts, setFacts] = useState<Record<string, string[]>>({});
  const act = useAction((id: string, action: string, body: any = {}) => api(`/brain/updates/${id}/${action}`, { body }), { success: 'Zapisano', onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!updates) return <Spinner />;
  const pending = updates.filter((u) => u.status === 'pending');

  return (
    <div>
      <PageHeader icon={<History size={20} className="text-violet" />} title="Change History"
        subtitle="Kontrolowane aktualizacje pamięci. Po każdym zadaniu agent zgłasza podsumowanie (co, dlaczego, pliki, testy, nowe fakty). Zatwierdzone fakty trafiają do „Rejestru zatwierdzonych faktów” (wersjonowany, z rollbackiem)." />
      <Tabs value={tab} onChange={setTab} className="mb-4" tabs={[{ id: 'updates', label: 'Aktualizacje Brain', count: pending.length }, { id: 'docs', label: 'Dokumenty' }, { id: 'decisions', label: 'Decyzje' }, { id: 'files', label: 'Pliki' }]} />
      {tab === 'updates' && (updates.length === 0 ? <Card><Empty icon={<Brain size={28} />} title="Brak zgłoszonych aktualizacji">Pojawią się po pierwszych zadaniach wykonanych przez agentów.</Empty></Card> : (
        <div className="space-y-3">
          {updates.map((u) => {
            const pc = u.proposed_changes ?? {};
            const sel = facts[u.id] ?? pc.new_facts ?? [];
            return (
              <Card key={u.id} title={<span className="flex items-center gap-2">{u.agent_name ?? u.agent_id}<span className="font-mono text-[11px] text-faint">{u.id}</span></span>}
                actions={<><Badge color={ST[u.status]}>{u.status}</Badge>{u.agent_execution_id && <Button size="sm" variant="ghost" onClick={() => setExec(u.agent_execution_id)}>wykonanie</Button>}</>}>
                <div className="grid gap-3 text-[12.5px] md:grid-cols-2">
                  <div><div className="text-xs text-mute">Co się zmieniło</div>{pc.what_changed || '—'}</div>
                  <div><div className="text-xs text-mute">Dlaczego</div>{pc.why || '—'}</div>
                  <div><div className="text-xs text-mute">Pliki</div>{(pc.files_affected ?? []).length ? pc.files_affected.map((f: string) => <div key={f} className="font-mono text-[11.5px]">{f}</div>) : '—'}</div>
                  <div><div className="text-xs text-mute">Testy</div>{pc.tests_performed || '—'}</div>
                </div>
                {(pc.docs_to_update ?? []).length > 0 && <div className="mt-2 text-[12px]"><span className="text-mute">Dokumentacja do aktualizacji: </span>{pc.docs_to_update.join(', ')} <Link to="/docs" className="text-cyan hover:underline">→ edytuj</Link></div>}
                {(pc.assumptions ?? []).length > 0 && <div className="mt-2 text-[12px] text-amber">Założenia (nie fakty): {pc.assumptions.join('; ')}</div>}
                <div className="mt-3">
                  <div className="mb-1 text-xs text-mute">Nowe fakty {u.status === 'pending' && '(odznacz te, których nie akceptujesz)'}</div>
                  {(pc.new_facts ?? []).length === 0 ? <div className="text-[12px] text-faint">brak</div> : pc.new_facts.map((f: string) => (
                    <label key={f} className="flex items-start gap-2 text-[12.5px]">
                      <input type="checkbox" disabled={u.status !== 'pending'} checked={sel.includes(f)} onChange={(e) => setFacts({ ...facts, [u.id]: e.target.checked ? [...sel, f] : sel.filter((x: string) => x !== f) })} className="mt-0.5" />{f}
                    </label>
                  ))}
                </div>
                {u.status === 'pending' ? (
                  <div className="mt-3 flex gap-2">
                    <Button size="sm" variant="success" icon={<Check size={12} />} loading={act.loading} onClick={() => act.run(u.id, 'approve', { facts: sel })}>Zatwierdź {sel.length} faktów</Button>
                    <Button size="sm" variant="danger" icon={<X size={12} />} onClick={() => act.run(u.id, 'reject')}>Odrzuć</Button>
                  </div>
                ) : <div className="mt-2 text-[11px] text-faint">Rozpatrzył: {u.reviewed_by} · {fmtDateTime(u.reviewed_at)}</div>}
              </Card>
            );
          })}
        </div>
      ))}
      {tab !== 'updates' && (
        <Card bodyClass="p-0">
          {!logs ? <Spinner /> : logs.length === 0 ? <Empty title="Brak zmian" /> : (
            <table className="w-full text-[12.5px]"><tbody>{logs.map((l) => (
              <tr key={l.id} className="border-b border-line last:border-0">
                <td className="whitespace-nowrap px-4 py-2 text-[11px] text-faint">{fmtDateTime(l.timestamp)}</td>
                <td className="pr-3">{tab === 'docs' ? <BookText size={13} className="text-sky" /> : tab === 'files' ? <FileCode2 size={13} className="text-cyan" /> : <Brain size={13} className="text-violet" />}</td>
                <td className="pr-3 font-medium">{l.actor}</td><td className="pr-3">{l.action}</td>
                <td className="pr-4 text-mute">{tab === 'files' ? <Link to={`/workspace?file=${encodeURIComponent(l.entity_id)}`} className="font-mono text-cyan hover:underline">{l.details}</Link> : l.details}</td>
              </tr>
            ))}</tbody></table>
          )}
          <div className="border-t border-line px-4 py-2 text-[11px] text-faint">Rollback: dokumenty — Game Documentation → Wersje; pliki — Workspace → Wersje.</div>
        </Card>
      )}
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}
