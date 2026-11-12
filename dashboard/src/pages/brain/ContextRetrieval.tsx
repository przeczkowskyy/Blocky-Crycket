import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SearchCode, Search, Eye, ShieldCheck } from 'lucide-react';
import { api, useApi, fmtDateTime, EXEC_STATUS } from '../../lib/api';
import { Badge, Button, Card, Empty, Field, Input, PageHeader, Select, Spinner, StatusBadge, Tabs, Textarea, useAction, cx } from '../../components/ui';

export function ContextRetrieval() {
  const [params, setParams] = useSearchParams();
  const execId = params.get('execution');
  const [tab, setTab] = useState<'inspector' | 'search' | 'preview'>(execId ? 'inspector' : 'search');
  return (
    <div>
      <PageHeader icon={<SearchCode size={20} className="text-violet" />} title="Context and Retrieval"
        subtitle="Zobacz dokładnie, co agent dostał w kontekście: które źródła, fragmenty i decyzje. Przetestuj wyszukiwanie i podgląd pakietu kontekstu przed uruchomieniem zadania." />
      <Tabs value={tab} onChange={setTab} className="mb-4" tabs={[{ id: 'inspector', label: 'Agent Context Inspector' }, { id: 'search', label: 'Test wyszukiwania' }, { id: 'preview', label: 'Podgląd pakietu kontekstu' }]} />
      {tab === 'inspector' && <Inspector execId={execId} onSelect={(id) => setParams({ execution: id })} />}
      {tab === 'search' && <SearchTest />}
      {tab === 'preview' && <Preview />}
    </div>
  );
}

function Inspector({ execId, onSelect }: { execId: string | null; onSelect: (id: string) => void }) {
  const { data: snaps } = useApi<any[]>('/brain/snapshots', 6000);
  const { data: snap } = useApi<any>(execId ? `/brain/snapshots/${execId}` : null);
  const [showFull, setShowFull] = useState(false);
  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <Card title="Wykonania" bodyClass="p-2">
        {!snaps ? <Spinner /> : snaps.length === 0 ? <Empty title="Brak wykonań">Kontekst pojawi się po pierwszym uruchomieniu agenta.</Empty> : snaps.map((s) => (
          <button key={s.id} onClick={() => onSelect(s.agent_execution_id)} className={cx('mb-1 w-full rounded-md border px-2.5 py-2 text-left cursor-pointer', execId === s.agent_execution_id ? 'border-gold/50 bg-gold/5' : 'border-line hover:border-line2')}>
            <div className="flex items-center justify-between gap-2"><b className="text-[12px]">{s.agent_name}</b><StatusBadge map={EXEC_STATUS} value={s.status} /></div>
            <div className="truncate text-[11.5px] text-mute">{s.prompt}</div>
            <div className="text-[10.5px] text-faint">{fmtDateTime(s.created_at)} · {s.retrieved_source_ids.length} źródeł</div>
          </button>
        ))}
      </Card>
      <Card title={execId ? `Kontekst wykonania ${execId}` : 'Wybierz wykonanie'} actions={snap && <Button size="sm" icon={<Eye size={12} />} onClick={() => setShowFull(!showFull)}>{showFull ? 'Fragmenty' : 'Pełny tekst kontekstu'}</Button>}>
        {!execId ? <Empty title="Wybierz wykonanie z listy" /> : !snap ? <Spinner /> : showFull ? (
          <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap rounded-md bg-bg p-3 font-mono text-[11.5px]">{snap.context_text}</pre>
        ) : (
          <div className="space-y-3">
            <div className="text-[12.5px]"><span className="text-mute">Podsumowanie: </span>{snap.context_summary}</div>
            <div className="text-[12px]"><span className="text-mute">Zapytanie wyszukiwania: </span><span className="font-mono text-[11.5px]">{snap.query?.slice(0, 300)}</span></div>
            <div><div className="mb-1 text-xs text-mute">Zatwierdzone decyzje w kontekście</div><div className="flex flex-wrap gap-1">{(snap.decisions ?? []).map((d: any) => <Badge key={d.code} color="#34d399">{d.code} {d.title}</Badge>)}</div></div>
            <div>
              <div className="mb-1 text-xs text-mute">Pobrane fragmenty (ranking BM25)</div>
              {(snap.retrieved_chunks ?? []).length === 0 ? <div className="text-[12px] text-amber">Brak dopasowanych fragmentów — agent działał tylko na decyzjach i briefie gry.</div> : snap.retrieved_chunks.map((c: any, i: number) => (
                <div key={c.chunkId} className="mb-1.5 rounded-md border border-line bg-panel2 p-2.5 text-[12px]">
                  <div className="flex items-center gap-2"><span className="text-faint">#{i + 1}</span><b>{c.sourceName}</b>{c.heading && <span className="text-mute">— {c.heading}</span>}<span className="ml-auto font-mono text-[10.5px] text-faint">score {Number(c.score).toFixed(2)}</span></div>
                  <div className="mt-1 text-mute">{c.preview}…</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

function SearchTest() {
  const [q, setQ] = useState('');
  const [res, setRes] = useState<any[] | null>(null);
  const search = useAction(() => api<any[]>(`/brain/search?q=${encodeURIComponent(q)}&limit=12`), { onDone: setRes });
  return (
    <Card>
      <form className="mb-4 flex gap-2" onSubmit={(e) => { e.preventDefault(); if (q.trim()) void search.run(); }}>
        <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="np. pasek HP, karczma questy, Style Lock prefix, UDim2" />
        <Button type="submit" variant="primary" icon={<Search size={14} />} loading={search.loading}>Szukaj</Button>
      </form>
      {res === null ? <Empty title="Wpisz zapytanie, aby zobaczyć, co znajdzie Project Brain" /> : res.length === 0 ? <Empty title="Brak wyników" /> : res.map((r, i) => (
        <div key={r.chunkId} className="mb-2 rounded-md border border-line bg-panel2 p-3">
          <div className="flex items-center gap-2 text-[12.5px]"><span className="text-faint">#{i + 1}</span><b>{r.sourceName}</b>{r.heading && <span className="text-mute">— {r.heading}</span>}{r.authoritative && <Badge color="#34d399"><ShieldCheck size={10} />autorytatywne</Badge>}<span className="ml-auto font-mono text-[10.5px] text-faint">{r.score.toFixed(2)}</span></div>
          <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap font-mono text-[11.5px] text-ink/85">{r.content}</pre>
        </div>
      ))}
    </Card>
  );
}

function Preview() {
  const { data: agents } = useApi<any[]>('/agents');
  const [agentId, setAgentId] = useState('pixel');
  const [task, setTask] = useState('');
  const [files, setFiles] = useState('');
  const [res, setRes] = useState<any>(null);
  const go = useAction(() => api('/brain/preview-context', { body: { agentId, task, relatedFiles: files.split(',').map((x) => x.trim()).filter(Boolean) } }), { onDone: setRes });
  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <Card title="Parametry">
        <div className="space-y-3">
          <Field label="Agent"><Select value={agentId} onChange={(e) => setAgentId(e.target.value)}>{(agents ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></Field>
          <Field label="Zadanie"><Textarea value={task} onChange={(e) => setTask(e.target.value)} placeholder="np. Stwórz Pet Inventory UI" /></Field>
          <Field label="Powiązane pliki (po przecinku)"><Input value={files} onChange={(e) => setFiles(e.target.value)} /></Field>
          <Button variant="primary" className="w-full" disabled={!task.trim()} loading={go.loading} onClick={() => go.run()}>Zbuduj pakiet kontekstu</Button>
          <p className="text-[11px] text-faint">Bez wywołania modelu — darmowe. Pokazuje dokładnie to, co trafiłoby do agenta.</p>
        </div>
      </Card>
      <Card title={res ? res.summary : 'Pakiet kontekstu'}>
        {!res ? <Empty title="Zbuduj pakiet, aby zobaczyć kontekst" /> : (
          <>
            <div className="mb-3 flex flex-wrap gap-1">{res.chunks.map((c: any) => <Badge key={c.chunkId} color={c.authoritative ? '#34d399' : '#60a5fa'}>{c.sourceName}{c.heading ? ` › ${c.heading}` : ''}</Badge>)}</div>
            <pre className="max-h-[65vh] overflow-auto whitespace-pre-wrap rounded-md bg-bg p-3 font-mono text-[11.5px]">{res.text}</pre>
          </>
        )}
      </Card>
    </div>
  );
}
