import { useState } from 'react';
import { ScrollText } from 'lucide-react';
import { useApi, fmtDateTime } from '../lib/api';
import { Card, Empty, ErrorBox, Input, PageHeader, Select, Spinner } from '../components/ui';

const LEVEL: Record<string, string> = { info: '#8a93a6', success: '#34d399', warn: '#f5c542', error: '#f05252' };

export function ActivityLogs() {
  const [q, setQ] = useState('');
  const [level, setLevel] = useState('');
  const [type, setType] = useState('');
  const qs = new URLSearchParams({ limit: '500', ...(q ? { q } : {}), ...(level ? { level } : {}), ...(type ? { entity_type: type } : {}) }).toString();
  const { data: logs, error } = useApi<any[]>(`/logs?${qs}`, 5000);
  if (error) return <ErrorBox error={error} />;
  return (
    <div>
      <PageHeader icon={<ScrollText size={20} className="text-gold" />} title="Activity Logs" subtitle="Pełny ślad audytowy: kto, co i kiedy zmienił. Pokazujemy podsumowania działań i wyniki — nigdy prywatne rozumowanie modeli."
        actions={<>
          <Input className="w-56" placeholder="Szukaj w akcjach i szczegółach…" value={q} onChange={(e) => setQ(e.target.value)} />
          <Select className="w-32" value={level} onChange={(e) => setLevel(e.target.value)}><option value="">Każdy poziom</option>{Object.keys(LEVEL).map((l) => <option key={l}>{l}</option>)}</Select>
          <Select className="w-40" value={type} onChange={(e) => setType(e.target.value)}><option value="">Każdy obiekt</option>{['task', 'execution', 'approval', 'file', 'decision', 'document', 'brain_source', 'brain_update', 'asset', 'bug', 'test', 'build', 'workflow_run', 'agent', 'ui'].map((t) => <option key={t}>{t}</option>)}</Select>
        </>} />
      <Card bodyClass="p-0">
        {!logs ? <Spinner /> : logs.length === 0 ? <Empty title="Brak wpisów" /> : (
          <table className="w-full font-mono text-[11.5px]">
            <tbody>{logs.map((l) => (
              <tr key={l.id} className="border-b border-line align-top last:border-0">
                <td className="whitespace-nowrap px-4 py-1.5 text-faint">{fmtDateTime(l.timestamp)}</td>
                <td className="whitespace-nowrap pr-3 font-semibold" style={{ color: LEVEL[l.level] }}>{l.actor}</td>
                <td className="pr-3">{l.action}</td>
                <td className="pr-3 text-mute">{l.details}</td>
                <td className="whitespace-nowrap pr-4 text-faint">{l.entity_type ? `${l.entity_type}:${String(l.entity_id).slice(0, 18)}` : ''}</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
