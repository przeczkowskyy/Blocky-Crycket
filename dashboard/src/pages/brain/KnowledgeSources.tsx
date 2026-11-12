import { useMemo, useState } from 'react';
import { Database, Plus, RefreshCw, Archive, ArchiveRestore, ShieldCheck, Search, Radar } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../../lib/api';
import { Badge, Button, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, Textarea, useAction, cx, Card } from '../../components/ui';

const IDX: Record<string, string> = { indexed: '#34d399', stale: '#f5c542', registered: '#8a93a6', indexing: '#22d3ee', failed: '#f05252', missing: '#f05252' };
const IDX_LABEL: Record<string, string> = { indexed: 'zaindeksowane', stale: 'nieaktualne', registered: 'tylko zarejestrowane', indexing: 'indeksowanie…', failed: 'błąd', missing: 'brak źródła' };

export function KnowledgeSources() {
  const { data: sources, error, reload } = useApi<any[]>('/brain/sources', 8000);
  const [q, setQ] = useState('');
  const [type, setType] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [sel, setSel] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const discover = useAction(() => api('/brain/discover', { body: {} }), { success: (r: any) => `Wykryto ${r.added} nowych źródeł`, onDone: reload });
  const list = useMemo(() => (sources ?? []).filter((s) => (showArchived || !s.archived) && (!type || s.source_type === type) && (!q || s.name.toLowerCase().includes(q.toLowerCase()))), [sources, q, type, showArchived]);
  if (error) return <ErrorBox error={error} />;
  if (!sources) return <Spinner />;
  const types = Array.from(new Set(sources.map((s) => s.source_type)));

  return (
    <div>
      <PageHeader icon={<Database size={20} className="text-violet" />} title="Knowledge Sources" subtitle="Każde źródło ma typ, pochodzenie, hash treści, wersję i status indeksowania. „Zarejestrowane” ≠ „zaindeksowane” — agenci widzą tylko zaindeksowane fragmenty."
        actions={<><Button icon={<Radar size={14} />} loading={discover.loading} onClick={() => discover.run()}>Wykryj nowe pliki</Button><Button variant="primary" icon={<Plus size={14} />} onClick={() => setAdding(true)}>Dodaj źródło</Button></>} />
      <div className="mb-3 flex flex-wrap gap-2">
        <div className="relative"><Search size={14} className="absolute left-2.5 top-2 text-faint" /><Input className="w-64 pl-8" placeholder="Szukaj źródeł…" value={q} onChange={(e) => setQ(e.target.value)} /></div>
        <Select className="w-44" value={type} onChange={(e) => setType(e.target.value)}><option value="">Każdy typ</option>{types.map((t) => <option key={t}>{t}</option>)}</Select>
        <label className="flex items-center gap-1.5 text-[12.5px] text-mute"><input type="checkbox" checked={showArchived} onChange={(e) => setShowArchived(e.target.checked)} /> pokaż zarchiwizowane</label>
      </div>
      <Card bodyClass="p-0">
        <table className="w-full text-[12.5px]">
          <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line"><th className="px-4 py-2">Źródło</th><th>Typ</th><th>Status</th><th>Autorytatywne</th><th>Wersja</th><th>Fragmenty</th><th>Zaindeksowano</th><th className="pr-4">Hash</th></tr></thead>
          <tbody>{list.map((s) => (
            <tr key={s.id} onClick={() => setSel(s.id)} className={cx('cursor-pointer border-b border-line last:border-0 hover:bg-panel2', s.archived && 'opacity-50')}>
              <td className="px-4 py-2"><div className="font-medium">{s.name}</div><div className="font-mono text-[10.5px] text-faint">{s.origin}</div></td>
              <td><Badge color="#60a5fa">{s.source_type}</Badge></td>
              <td><Badge color={IDX[s.indexing_status]} dot>{IDX_LABEL[s.indexing_status] ?? s.indexing_status}</Badge></td>
              <td>{s.authoritative ? <ShieldCheck size={15} className="text-mint" /> : <span className="text-faint">—</span>}</td>
              <td>v{s.version}</td><td>{s.chunk_count}</td>
              <td className="text-[11px] text-faint">{fmtDateTime(s.last_indexed_at)}</td>
              <td className="pr-4 font-mono text-[10.5px] text-faint">{s.content_hash?.slice(0, 10) ?? '—'}</td>
            </tr>
          ))}</tbody>
        </table>
        {list.length === 0 && <Empty title="Brak źródeł" />}
      </Card>
      {sel && <SourceModal id={sel} onClose={() => setSel(null)} onChanged={reload} />}
      <AddSource open={adding} onClose={() => setAdding(false)} onDone={() => { setAdding(false); reload(); }} />
    </div>
  );
}

function SourceModal({ id, onClose, onChanged }: { id: string; onClose: () => void; onChanged: () => void }) {
  const { data: s, reload } = useApi<any>(`/brain/sources/${id}`);
  const done = () => { reload(); onChanged(); };
  const index = useAction(() => api(`/brain/sources/${id}/index`, { body: {} }), { success: 'Zaindeksowano ponownie', onDone: done });
  const patch = useAction((body: any) => api(`/brain/sources/${id}`, { method: 'PATCH', body }), { success: 'Zapisano', onDone: done });
  return (
    <Modal open onClose={onClose} width="max-w-4xl" title={s?.name ?? 'Źródło'}>
      {!s ? <Spinner /> : (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge color={IDX[s.indexing_status]} dot>{IDX_LABEL[s.indexing_status]}</Badge>
            <Badge color="#60a5fa">{s.source_type}</Badge>
            {(s.categories ?? []).map((c: string) => <Badge key={c} color="#a78bfa">{c}</Badge>)}
            <span className="text-[11px] text-faint">v{s.version} · hash {s.content_hash?.slice(0, 16)} · dostęp: {s.access}</span>
            <div className="flex-1" />
            <Button size="sm" icon={<RefreshCw size={12} />} loading={index.loading} onClick={() => index.run()}>Re-indeksuj</Button>
            <Button size="sm" icon={<ShieldCheck size={12} />} onClick={() => patch.run({ authoritative: !s.authoritative })}>{s.authoritative ? 'Usuń status autorytatywny' : 'Oznacz jako autorytatywne'}</Button>
            <Button size="sm" variant="ghost" icon={s.archived ? <ArchiveRestore size={12} /> : <Archive size={12} />} onClick={() => patch.run({ archived: !s.archived })}>{s.archived ? 'Przywróć' : 'Archiwizuj'}</Button>
          </div>
          {s.error && <ErrorBox error={s.error} />}
          {s.origin.startsWith('kb:') && <div className="text-[11.5px] text-faint">Status autorytatywny dokumentów KB wynika z ich zatwierdzenia w Game Documentation.</div>}
          <div>
            <div className="mb-1 text-xs text-mute">Fragmenty ({s.chunks.length})</div>
            <div className="max-h-[45vh] space-y-2 overflow-y-auto">
              {s.chunks.map((c: any) => <div key={c.id} className="rounded-md border border-line bg-panel2 p-2.5"><div className="mb-1 text-[11px] text-faint">#{c.ord}{c.heading ? ` — ${c.heading}` : ''}</div><pre className="whitespace-pre-wrap font-mono text-[11.5px] text-ink/85">{c.content}</pre></div>)}
            </div>
          </div>
          <div className="text-[12px]"><span className="text-mute">Użyte w wykonaniach: </span>{s.usedBy.length === 0 ? <span className="text-faint">jeszcze nie</span> : s.usedBy.map((u: any) => <a key={u.agent_execution_id} href={`/brain/context?execution=${u.agent_execution_id}`} className="mr-2 font-mono text-cyan hover:underline">{u.agent_execution_id}</a>)}</div>
        </div>
      )}
    </Modal>
  );
}

function AddSource({ open, onClose, onDone }: { open: boolean; onClose: () => void; onDone: () => void }) {
  const [f, setF] = useState({ name: '', content: '', categories: 'manual', authoritative: false });
  const add = useAction(() => api('/brain/sources', { body: { ...f, categories: f.categories.split(',').map((x) => x.trim()).filter(Boolean) } }), { success: 'Dodano i zaindeksowano źródło', onDone: () => { setF({ name: '', content: '', categories: 'manual', authoritative: false }); onDone(); } });
  return (
    <Modal open={open} onClose={onClose} title="Nowe źródło wiedzy" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={!f.name.trim() || !f.content.trim()} loading={add.loading} onClick={() => add.run()}>Dodaj i zaindeksuj</Button></>}>
      <div className="space-y-3">
        <p className="text-[12px] text-mute">Dla plików w repozytorium użyj „Wykryj nowe pliki” — trafiają tu automatycznie z docs/, src/ i skilli. Tu wklejasz notatki, ustalenia lub teksty z innych narzędzi.</p>
        <Field label="Nazwa"><Input value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></Field>
        <Field label="Kategorie (po przecinku)"><Input value={f.categories} onChange={(e) => setF({ ...f, categories: e.target.value })} /></Field>
        <Field label="Treść"><Textarea className="min-h-[220px] font-mono text-[12px]" value={f.content} onChange={(e) => setF({ ...f, content: e.target.value })} /></Field>
        <label className="flex items-center gap-2 text-[12.5px]"><input type="checkbox" checked={f.authoritative} onChange={(e) => setF({ ...f, authoritative: e.target.checked })} /> Autorytatywne (traktowane jak kanon)</label>
        <p className="text-[11px] text-faint">Nie wklejaj tu sekretów ani kluczy API.</p>
      </div>
    </Modal>
  );
}
