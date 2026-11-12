import { useState } from 'react';
import { Hammer, Play } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Modal, PageHeader, Spinner, useAction } from '../components/ui';

export function Builds() {
  const { data: builds, error, reload } = useApi<any[]>('/builds', 6000);
  const [sel, setSel] = useState<any>(null);
  const build = useAction(() => api('/builds', { body: {} }), { success: (r: any) => (r.status === 'success' ? `Build OK (${r.ms} ms)` : 'Build nieudany'), onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!builds) return <Spinner />;
  return (
    <div>
      <PageHeader icon={<Hammer size={20} className="text-gold" />} title="Build History" subtitle="Historia `rojo build` — weryfikuje, że wszystkie pliki (w tym .model.json) budują się do poprawnego miejsca. Wynik: dashboard/data/builds/latest.rbxlx (Twój .rbxl nie jest nadpisywany)."
        actions={<Button variant="primary" icon={<Play size={14} />} loading={build.loading} onClick={() => build.run()}>Zbuduj teraz</Button>} />
      <Card bodyClass="p-0">
        {builds.length === 0 ? <Empty icon={<Hammer size={30} />} title="Brak buildów" /> : (
          <table className="w-full text-[12.5px]">
            <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Czas</th><th>Rodzaj</th><th>Wyzwalacz</th><th>Status</th><th className="pr-4 text-right">Trwanie</th></tr></thead>
            <tbody>{builds.map((b) => (
              <tr key={b.id} className="cursor-pointer border-b border-line last:border-0 hover:bg-panel2" onClick={() => setSel(b)}>
                <td className="px-4 py-2">{fmtDateTime(b.created_at)}</td><td className="font-mono">{b.kind}</td><td className="text-mute">{b.trigger}</td>
                <td><Badge color={b.status === 'success' ? '#34d399' : '#f05252'}>{b.status}</Badge></td><td className="pr-4 text-right">{b.duration_ms} ms</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </Card>
      <Modal open={!!sel} onClose={() => setSel(null)} title={`Build ${sel?.id ?? ''}`} width="max-w-3xl">
        <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap rounded-md bg-bg p-3 font-mono text-[11.5px]">{sel?.output || '(brak wyjścia)'}</pre>
      </Modal>
    </div>
  );
}
