import { Gauge, Coins, Cpu, Timer, Database } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line, Cell } from 'recharts';
import { useApi, usd, num } from '../lib/api';
import { Card, Empty, ErrorBox, PageHeader, Spinner, Stat, Progress } from '../components/ui';

const axis = { stroke: '#5d6678', fontSize: 11 };
const tip = { contentStyle: { background: '#181d27', border: '1px solid #323a4a', borderRadius: 8, fontSize: 12 }, labelStyle: { color: '#e2e6ee' } };

export function Performance() {
  const { data, error } = useApi<any>('/performance', 8000);
  if (error) return <ErrorBox error={error} />;
  if (!data) return <Spinner />;
  const t = data.totals;
  const hasRuns = t.runs > 0;
  return (
    <div>
      <PageHeader icon={<Gauge size={20} className="text-gold" />} title="Performance" subtitle="Rzeczywiste zużycie tokenów, koszty i czasy wykonań agentów oraz czasy buildów Rojo. Koszt szacowany wg cennika modelu." />
      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
        <Stat label="Wykonania agentów" value={num(t.runs)} icon={<Cpu size={18} />} color="#22d3ee" />
        <Stat label="Tokeny wejściowe" value={num(t.input_tokens)} icon={<Database size={18} />} color="#60a5fa" />
        <Stat label="Tokeny wyjściowe" value={num(t.output_tokens)} icon={<Database size={18} />} color="#a78bfa" />
        <Stat label="Z cache" value={num(t.cache_read_tokens)} icon={<Timer size={18} />} color="#34d399" />
        <Stat label="Szacowany koszt" value={usd(t.cost)} icon={<Coins size={18} />} color="#f5c542" hint={`limit ${usd(data.costLimit)}`} />
      </div>
      <Card className="mb-5" title="Wykorzystanie limitu kosztów"><Progress value={t.cost} max={data.costLimit} color={t.cost / data.costLimit > 0.8 ? '#f05252' : '#f5c542'} /><div className="mt-1 text-[11px] text-faint">{usd(t.cost)} z {usd(data.costLimit)} — po przekroczeniu nowe wykonania są blokowane.</div></Card>
      {!hasRuns ? <Card><Empty icon={<Gauge size={30} />} title="Brak danych">Wykresy pojawią się po pierwszych wykonaniach agentów. Nie pokazujemy danych demo.</Empty></Card> : (
        <div className="grid gap-5 xl:grid-cols-2">
          <Card title="Koszt wg agenta (USD)">
            <div className="h-64"><ResponsiveContainer><BarChart data={data.byAgent}><CartesianGrid stroke="#252c39" vertical={false} /><XAxis dataKey="name" {...axis} /><YAxis {...axis} /><Tooltip {...tip} formatter={(v: number) => usd(v)} /><Bar dataKey="cost" radius={[4, 4, 0, 0]}>{data.byAgent.map((a: any) => <Cell key={a.name} fill={a.color} />)}</Bar></BarChart></ResponsiveContainer></div>
          </Card>
          <Card title="Średni czas wykonania (s)">
            <div className="h-64"><ResponsiveContainer><BarChart data={data.byAgent.map((a: any) => ({ ...a, sec: +(a.avg_ms / 1000).toFixed(1) }))}><CartesianGrid stroke="#252c39" vertical={false} /><XAxis dataKey="name" {...axis} /><YAxis {...axis} /><Tooltip {...tip} /><Bar dataKey="sec" radius={[4, 4, 0, 0]}>{data.byAgent.map((a: any) => <Cell key={a.name} fill={a.color} />)}</Bar></BarChart></ResponsiveContainer></div>
          </Card>
          <Card title="Dziennie: tokeny i koszt">
            <div className="h-64"><ResponsiveContainer><LineChart data={data.daily}><CartesianGrid stroke="#252c39" vertical={false} /><XAxis dataKey="day" {...axis} /><YAxis yAxisId="l" {...axis} /><YAxis yAxisId="r" orientation="right" {...axis} /><Tooltip {...tip} /><Line yAxisId="l" dataKey="tokens" stroke="#22d3ee" dot={false} strokeWidth={2} /><Line yAxisId="r" dataKey="cost" stroke="#f5c542" dot={false} strokeWidth={2} /></LineChart></ResponsiveContainer></div>
          </Card>
          <Card title="Agenci — szczegóły" bodyClass="p-0">
            <table className="w-full text-[12.5px]"><thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Agent</th><th className="text-right">Wykonania</th><th className="text-right">Błędy</th><th className="text-right">Tokeny</th><th className="pr-4 text-right">Koszt</th></tr></thead>
              <tbody>{data.byAgent.map((a: any) => <tr key={a.name} className="border-b border-line last:border-0"><td className="px-4 py-1.5" style={{ color: a.color }}>{a.name}</td><td className="text-right">{a.runs}</td><td className="text-right">{a.failures ?? 0}</td><td className="text-right">{num(a.input_tokens + a.output_tokens)}</td><td className="pr-4 text-right">{usd(a.cost)}</td></tr>)}</tbody></table>
          </Card>
        </div>
      )}
      {data.builds.length > 0 && (
        <Card className="mt-5" title="Czas buildu Rojo (ms)">
          <div className="h-48"><ResponsiveContainer><BarChart data={data.builds.map((b: any) => ({ ...b, t: new Date(b.created_at).toLocaleTimeString('pl-PL') }))}><CartesianGrid stroke="#252c39" vertical={false} /><XAxis dataKey="t" {...axis} /><YAxis {...axis} /><Tooltip {...tip} /><Bar dataKey="duration_ms" radius={[4, 4, 0, 0]}>{data.builds.map((b: any, i: number) => <Cell key={i} fill={b.status === 'success' ? '#34d399' : '#f05252'} />)}</Bar></BarChart></ResponsiveContainer></div>
        </Card>
      )}
    </div>
  );
}
