import { useState } from 'react';
import { FlaskConical, Play, PlayCircle, Plus, Check, X } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, Textarea, useAction, Stat } from '../components/ui';

export const TEST_STATUS: Record<string, { label: string; color: string }> = {
  passed: { label: 'Passed', color: '#34d399' }, failed: { label: 'Failed', color: '#f05252' }, not_run: { label: 'Nie uruchomiony', color: '#5d6678' }, not_configured: { label: 'NOT CONFIGURED', color: '#fb923c' },
};

export function Testing() {
  const { data: tests, error, reload } = useApi<any[]>('/tests');
  const { data: bugs } = useApi<any[]>('/bugs');
  const [out, setOut] = useState<any>(null);
  const [adding, setAdding] = useState(false);
  const runOne = useAction((id: string) => api(`/tests/${id}/run`, { body: {} }), { onDone: (r: any) => { reload(); setOut(r); } });
  const runAll = useAction(() => api('/tests/run-all', { body: {} }), { success: 'Uruchomiono wszystkie testy automatyczne', onDone: reload });
  const mark = useAction((id: string, status: string) => api(`/tests/${id}`, { method: 'PATCH', body: { status } }), { onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!tests) return <Spinner />;
  const c = (s: string) => tests.filter((t) => t.last_status === s).length;
  const openBugs = (bugs ?? []).filter((b) => !['resolved', 'closed'].includes(b.status));

  return (
    <div>
      <PageHeader icon={<FlaskConical size={20} className="text-gold" />} title="Testing Center"
        subtitle="Testy automatyczne uruchamiają prawdziwe narzędzia (rojo build, rojo sourcemap, selene). Testy manualne wykonujesz w Studio i oznaczasz wynik. Agenci nie uruchamiają gry — SENTINEL przegląda kod statycznie."
        actions={<><Button icon={<Plus size={14} />} onClick={() => setAdding(true)}>Test manualny</Button><Button variant="primary" icon={<PlayCircle size={14} />} loading={runAll.loading} onClick={() => runAll.run()}>Uruchom automatyczne</Button></>} />
      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
        <Stat label="Passed" value={c('passed')} icon={<Check size={18} />} color="#34d399" />
        <Stat label="Failed" value={c('failed')} icon={<X size={18} />} color="#f05252" />
        <Stat label="Nie uruchomione" value={c('not_run')} icon={<Play size={18} />} color="#8a93a6" />
        <Stat label="Regresyjne" value={tests.filter((t) => t.regression).length} icon={<FlaskConical size={18} />} color="#a78bfa" />
        <Stat label="Otwarte błędy" value={openBugs.length} icon={<X size={18} />} color="#fb923c" />
      </div>
      <Card bodyClass="p-0">
        <table className="w-full text-[12.5px]">
          <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Test</th><th>Typ</th><th>Kategoria</th><th>Wynik</th><th>Ostatnio</th><th /></tr></thead>
          <tbody>
            {tests.map((t) => (
              <tr key={t.id} className="border-b border-line last:border-0">
                <td className="px-4 py-2.5"><div className="font-medium">{t.name} {t.regression && <Badge color="#a78bfa">regresja</Badge>}</div><div className="text-[11.5px] text-mute">{t.description}</div></td>
                <td>{t.kind === 'automated' ? 'automatyczny' : 'manualny'}</td>
                <td className="text-mute">{t.category}</td>
                <td><button className="cursor-pointer" onClick={() => t.last_output && setOut({ status: t.last_status, output: t.last_output, name: t.name })}><Badge color={TEST_STATUS[t.last_status]?.color}>{TEST_STATUS[t.last_status]?.label}</Badge></button></td>
                <td className="text-[11px] text-faint">{fmtDateTime(t.last_run_at)}</td>
                <td className="pr-4 text-right">
                  {t.kind === 'automated'
                    ? <Button size="sm" icon={<Play size={12} />} loading={runOne.loading} onClick={() => runOne.run(t.id)}>Uruchom</Button>
                    : <div className="flex justify-end gap-1"><Button size="sm" variant="success" onClick={() => mark.run(t.id, 'passed')}>Pass</Button><Button size="sm" variant="danger" onClick={() => mark.run(t.id, 'failed')}>Fail</Button></div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      <Modal open={!!out} onClose={() => setOut(null)} title={`Wynik testu ${out?.name ?? ''}`} width="max-w-3xl">
        {out && <><Badge color={TEST_STATUS[out.status]?.color}>{TEST_STATUS[out.status]?.label}</Badge><pre className="mt-3 max-h-[60vh] overflow-auto whitespace-pre-wrap rounded-md bg-bg p-3 font-mono text-[11.5px]">{out.output || '(brak wyjścia)'}</pre></>}
      </Modal>
      <AddTest open={adding} onClose={() => setAdding(false)} onDone={() => { setAdding(false); reload(); }} />
    </div>
  );
}

function AddTest({ open, onClose, onDone }: { open: boolean; onClose: () => void; onDone: () => void }) {
  const [f, setF] = useState({ name: '', category: 'ui', description: '', regression: false });
  const add = useAction(() => api('/tests', { body: f }), { success: 'Dodano test', onDone: () => { setF({ name: '', category: 'ui', description: '', regression: false }); onDone(); } });
  return (
    <Modal open={open} onClose={onClose} title="Nowy test manualny" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={!f.name.trim()} loading={add.loading} onClick={() => add.run()}>Dodaj</Button></>}>
      <div className="space-y-3">
        <Field label="Nazwa"><Input value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></Field>
        <Field label="Kategoria"><Select value={f.category} onChange={(e) => setF({ ...f, category: e.target.value })}>{['ui', 'luau', 'gameplay', 'performance', 'assets', 'integration'].map((c) => <option key={c}>{c}</option>)}</Select></Field>
        <Field label="Kroki / oczekiwany wynik"><Textarea value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} /></Field>
        <label className="flex items-center gap-2 text-[12.5px]"><input type="checkbox" checked={f.regression} onChange={(e) => setF({ ...f, regression: e.target.checked })} /> Test regresyjny</label>
      </div>
    </Modal>
  );
}
