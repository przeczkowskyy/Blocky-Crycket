import { Link } from 'react-router-dom';
import { Brain, RefreshCw, ShieldCheck, Gavel, BookText, Code2, Image, History, HelpCircle, AlertTriangle, CheckCircle2, FileWarning, Copy, Unlink, Clock } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, PageHeader, Spinner, useAction } from '../../components/ui';

export function BrainOverview() {
  const { data, error, reload } = useApi<any>('/brain/overview', 10000);
  const reindex = useAction((onlyChanged: boolean) => api('/brain/index', { body: { onlyChanged } }), { success: (r: any) => `Zaindeksowano ${r.indexed}, bez zmian ${r.skipped}, błędy ${r.failed}`, onDone: reload });
  if (error) return <ErrorBox error={error} />;
  if (!data) return <Spinner />;
  const h = data.health; const L = data.layers;
  const layers = [
    { icon: ShieldCheck, color: '#34d399', name: 'Kanoniczne fakty', n: L.canonicalFacts, to: '/brain/sources', desc: 'Autorytatywne źródła' },
    { icon: Gavel, color: '#f5c542', name: 'Zatwierdzone decyzje', n: L.approvedDecisions, to: '/brain/decisions', desc: 'Zawsze w kontekście agentów' },
    { icon: BookText, color: '#60a5fa', name: 'Dokumentacja', n: L.documentation, to: '/docs', desc: 'GDD, specyfikacje, roadmapa' },
    { icon: Code2, color: '#22d3ee', name: 'Wiedza o repozytorium', n: L.repository, to: '/explorer', desc: 'Luau, GUI, Rojo, skille' },
    { icon: Image, color: '#a78bfa', name: 'Wiedza o assetach', n: L.assets, to: '/assets', desc: 'Prompty, wersje, Style Lock' },
    { icon: History, color: '#fb923c', name: 'Historia wykonań', n: L.history, to: '/agents', desc: 'Wyniki i zmiany agentów' },
    { icon: HelpCircle, color: '#f472b6', name: 'Propozycje i pytania', n: L.proposals, to: '/brain/decisions?tab=questions', desc: 'NIE są faktami' },
  ];
  const issues = [
    { icon: Clock, label: 'Nieaktualne (zmienione od indeksowania)', items: h.stale },
    { icon: FileWarning, label: 'Niezaindeksowane', items: h.unindexed },
    { icon: AlertTriangle, label: 'Brakujące źródła', items: h.missing },
    { icon: Copy, label: 'Duplikaty', items: h.duplicates.map((d: string[]) => d.join(' = ')) },
    { icon: Unlink, label: 'Zepsute referencje', items: h.brokenRefs.map((b: any) => `${b.where} → ${b.ref}`) },
    { icon: FileWarning, label: 'Pliki UI jeszcze nieistniejące (oczekiwane)', items: h.missingUiFiles.map((b: any) => `${b.where} → ${b.ref}`) },
    { icon: BookText, label: 'Niezatwierdzone dokumenty', items: h.unapprovedDocs.map((d: any) => d.title) },
    { icon: Clock, label: 'Dokumenty starsze niż 30 dni', items: h.outdatedDocs.map((d: any) => d.title) },
  ];

  return (
    <div>
      <PageHeader icon={<Brain size={20} className="text-violet" />} title="Project Brain"
        subtitle="Trwała, ustrukturyzowana pamięć projektu i źródło prawdy. Każde wykonanie agenta otrzymuje dopasowany pakiet kontekstu (FTS5/BM25 + zatwierdzone decyzje), zapisany do inspekcji."
        actions={<><Button icon={<RefreshCw size={14} />} loading={reindex.loading} onClick={() => reindex.run(true)}>Indeksuj zmienione</Button><Button variant="primary" icon={<RefreshCw size={14} />} loading={reindex.loading} onClick={() => reindex.run(false)}>Pełne indeksowanie</Button></>} />
      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Box label="Zaindeksowane źródła" value={`${h.indexed}/${h.total}`} color="#34d399" />
        <Box label="Ostatnie indeksowanie" value={fmtDateTime(h.lastIndexedAt)} color="#60a5fa" />
        <Box label="Aktualizacje do przeglądu" value={data.pendingUpdates} color="#f5c542" to="/brain/history" />
        <Box label="Wykryte konflikty" value={h.conflicts.length} color={h.conflicts.length ? '#f05252' : '#34d399'} />
      </div>
      <Card title="Warstwy wiedzy" className="mb-5">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-7">
          {layers.map((l) => (
            <Link key={l.name} to={l.to} className="rounded-lg border border-line bg-panel2 p-3 hover:border-line2">
              <l.icon size={18} style={{ color: l.color }} />
              <div className="mt-2 text-xl font-semibold">{l.n}</div>
              <div className="text-[12px] font-medium">{l.name}</div>
              <div className="text-[11px] text-faint">{l.desc}</div>
            </Link>
          ))}
        </div>
      </Card>
      <div className="grid gap-5 xl:grid-cols-2">
        <Card title="Konflikty (heurystyka)" icon={<AlertTriangle size={14} className="text-ruby" />}>
          {h.conflicts.length === 0 ? <Empty icon={<CheckCircle2 size={24} />} title="Nie wykryto konfliktów" /> : h.conflicts.map((c: any, i: number) => (
            <div key={i} className="mb-2 rounded-md border border-ruby/30 bg-ruby/5 p-3 text-[12.5px]">
              <div className="font-medium text-ruby">{c.title}</div><div className="text-mute">{c.detail}</div>
              <div className="mt-1 flex flex-wrap gap-1">{c.sources.map((s: string) => <Badge key={s} color="#8a93a6">{s}</Badge>)}</div>
              <Link to="/brain/decisions?tab=questions" className="mt-1 inline-block text-[11px] text-cyan hover:underline">Rozstrzygnij w rejestrze pytań →</Link>
            </div>
          ))}
          <p className="mt-2 text-[11px] text-faint">Wykrywanie oparte na regułach (warianty nazw, zduplikowane decyzje). Głębszą analizę sprzeczności może wykonać LOREKEEPER.</p>
        </Card>
        <Card title="Zdrowie wiedzy" icon={<ShieldCheck size={14} className="text-mint" />}>
          <ul className="space-y-2">
            {issues.map((it) => (
              <li key={it.label} className="text-[12.5px]">
                <div className="flex items-center gap-2"><it.icon size={13} className={it.items.length ? 'text-amber' : 'text-mint'} /><span className="flex-1">{it.label}</span><Badge color={it.items.length ? '#f5c542' : '#34d399'}>{it.items.length}</Badge></div>
                {it.items.length > 0 && <ul className="ml-6 mt-0.5 list-disc pl-3 text-[11.5px] text-mute">{it.items.slice(0, 6).map((x: string) => <li key={x}>{x}</li>)}</ul>}
              </li>
            ))}
          </ul>
          <div className="mt-3 text-[11px] text-faint">Wyszukiwanie: {h.ftsAvailable ? 'SQLite FTS5 (BM25)' : 'awaryjne dopasowanie słów kluczowych'}. Embeddingi wektorowe nie są używane.</div>
        </Card>
      </div>
      {Object.keys(data.categories).length > 0 && (
        <Card title="Kategorie wiedzy" className="mt-5"><div className="flex flex-wrap gap-1.5">{Object.entries(data.categories).map(([k, v]) => <Badge key={k} color="#a78bfa">{k} · {String(v)}</Badge>)}</div></Card>
      )}
    </div>
  );
}

function Box({ label, value, color, to }: { label: string; value: React.ReactNode; color: string; to?: string }) {
  const inner = <div className="rounded-lg border border-line bg-panel p-3.5"><div className="text-lg font-semibold" style={{ color }}>{value}</div><div className="text-[11.5px] text-mute">{label}</div></div>;
  return to ? <Link to={to}>{inner}</Link> : inner;
}
