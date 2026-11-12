import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Save, ShieldCheck, Zap, Bot } from 'lucide-react';
import { api, useApi, usd } from '../lib/api';
import { Badge, Button, Card, ErrorBox, Field, Input, PageHeader, Select, Spinner, useAction, cx, NotConfigured } from '../components/ui';
import { AgentAvatar } from '../components/AgentAvatar';
import { useStatus } from '../components/Layout';

const MODES = [
  { id: 'assistant', name: 'ASSISTANT', desc: 'Agenci proponują rozwiązania i szkice. Każda zmiana pliku trafia do Approvals.' },
  { id: 'semi', name: 'SEMI-AUTONOMOUS', desc: 'Agenci z uprawnieniem zapisu mogą tworzyć NOWE pliki w src/, docs/ i assets/. Zmiany istniejących plików i pliki chronione wymagają zatwierdzenia.' },
  { id: 'autonomous', name: 'AUTONOMOUS', desc: 'Agenci z uprawnieniem zapisu stosują zmiany w niechronionych plikach automatycznie (z historią wersji i rollbackiem), w granicach limitów. Pliki chronione nadal wymagają zatwierdzenia.' },
];

export function AIConfig() {
  const { data, error, reload } = useApi<any>('/settings');
  const { data: agents, reload: reloadAgents } = useApi<any[]>('/agents');
  const { status, reload: reloadStatus } = useStatus();
  const [s, setS] = useState<any>(null);
  useEffect(() => { if (data) setS({ ...data.settings }); }, [data]);
  const save = useAction(() => api('/settings', { method: 'PATCH', body: { autonomyMode: s.autonomyMode, maxIterations: Number(s.maxIterations), costLimitUsd: Number(s.costLimitUsd), timeLimitSec: Number(s.timeLimitSec), maxContextChunks: Number(s.maxContextChunks), defaultModel: s.defaultModel } }), { success: 'Zapisano konfigurację AI', onDone: () => { reload(); reloadStatus(); } });
  const patchAgent = useAction((id: string, body: any) => api(`/agents/${id}`, { method: 'PATCH', body }), { onDone: reloadAgents });
  if (error) return <ErrorBox error={error} />;
  if (!s || !agents) return <Spinner />;
  const dirty = JSON.stringify(s) !== JSON.stringify(data.settings);
  const pricing = data.pricing as Record<string, { in: number; out: number }>;

  return (
    <div>
      <PageHeader icon={<Cpu size={20} className="text-gold" />} title="AI Configuration" subtitle="Tryb autonomii, limity bezpieczeństwa i modele agentów. Klucz API ustawiasz wyłącznie w dashboard/.env (serwer), nigdy w przeglądarce."
        actions={<>{!status?.ai.configured && <NotConfigured />}<Button variant="primary" icon={<Save size={14} />} disabled={!dirty} loading={save.loading} onClick={() => save.run()}>Zapisz</Button></>} />
      <div className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <div className="space-y-5">
          <Card title="Tryb autonomii" icon={<Zap size={14} className="text-gold" />}>
            <div className="grid gap-3 md:grid-cols-3">
              {MODES.map((m) => (
                <button key={m.id} onClick={() => setS({ ...s, autonomyMode: m.id })} className={cx('rounded-lg border p-3 text-left cursor-pointer', s.autonomyMode === m.id ? 'border-gold/60 bg-gold/5' : 'border-line hover:border-line2')}>
                  <div className="text-[12.5px] font-bold">{m.name}</div><p className="mt-1 text-[11.5px] leading-relaxed text-mute">{m.desc}</p>
                </button>
              ))}
            </div>
          </Card>
          <Card title="Agenci — modele i effort" icon={<Bot size={14} className="text-cyan" />} bodyClass="p-0">
            <table className="w-full text-[12.5px]">
              <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Agent</th><th>Model</th><th>Effort</th><th>Zapis plików</th><th className="pr-4">Aktywny</th></tr></thead>
              <tbody>{agents.map((a) => (
                <tr key={a.id} className="border-b border-line last:border-0">
                  <td className="px-4 py-2"><Link to={`/agents/${a.id}`} className="flex items-center gap-2 hover:text-gold"><AgentAvatar agent={a} size={22} showStatus={false} />{a.name}</Link></td>
                  <td><Select className="h-7 w-44 text-xs" value={a.model} onChange={(e) => patchAgent.run(a.id, { model: e.target.value })}>{data.models.map((m: string) => <option key={m}>{m}</option>)}</Select></td>
                  <td><Select className="h-7 w-24 text-xs" value={a.effort} onChange={(e) => patchAgent.run(a.id, { effort: e.target.value })}>{['low', 'medium', 'high', 'xhigh', 'max'].map((x) => <option key={x}>{x}</option>)}</Select></td>
                  <td><input type="checkbox" className="accent-[#34d399] cursor-pointer" checked={!!a.permissions?.write_files} onChange={(e) => patchAgent.run(a.id, { permissions: { write_files: e.target.checked } })} /></td>
                  <td className="pr-4"><input type="checkbox" className="accent-[#34d399] cursor-pointer" checked={a.enabled} onChange={(e) => patchAgent.run(a.id, { enabled: e.target.checked })} /></td>
                </tr>
              ))}</tbody>
            </table>
          </Card>
        </div>
        <div className="space-y-5">
          <Card title="Limity bezpieczeństwa" icon={<ShieldCheck size={14} className="text-mint" />}>
            <div className="space-y-3">
              <Field label="Limit kosztów API (USD, łącznie)" hint="Po przekroczeniu nowe wykonania są blokowane."><Input type="number" min={0.5} step={0.5} value={s.costLimitUsd} onChange={(e) => setS({ ...s, costLimitUsd: e.target.value })} /></Field>
              <Field label="Limit czasu jednego wykonania (s)"><Input type="number" min={30} value={s.timeLimitSec} onChange={(e) => setS({ ...s, timeLimitSec: e.target.value })} /></Field>
              <Field label="Maks. iteracji agentów na workflow"><Input type="number" min={1} value={s.maxIterations} onChange={(e) => setS({ ...s, maxIterations: e.target.value })} /></Field>
              <Field label="Maks. fragmentów kontekstu z Project Brain"><Input type="number" min={1} max={30} value={s.maxContextChunks} onChange={(e) => setS({ ...s, maxContextChunks: e.target.value })} /></Field>
              <Field label="Model do testów połączenia i analizy obrazów"><Select value={s.defaultModel} onChange={(e) => setS({ ...s, defaultModel: e.target.value })}>{data.models.map((m: string) => <option key={m}>{m}</option>)}</Select></Field>
            </div>
          </Card>
          <Card title="Cennik (USD / 1M tokenów)">
            <ul className="space-y-1 text-[12px]">{Object.entries(pricing).map(([m, p]) => <li key={m} className="flex justify-between"><span className="font-mono">{m}</span><span className="text-mute">{usd(p.in)} in · {usd(p.out)} out</span></li>)}</ul>
            <p className="mt-2 text-[11px] text-faint">Agenci używają ustrukturyzowanego wyjścia (JSON schema), adaptacyjnego myślenia z ustawionym effort, cache promptu oraz serwerowego fallbacku przy odmowie modelu (<Badge color="#8a93a6">fallbacks: default</Badge>).</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
