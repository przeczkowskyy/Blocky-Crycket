import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { BookText, BookMarked, Plus, Pencil, CheckCircle2, History, Save, RotateCcw, Search, ShieldCheck } from 'lucide-react';
import { api, useApi, fmtDateTime } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, Textarea, useAction, cx, Confirm } from '../components/ui';
import { Markdown } from '../components/Markdown';

export const DOC_CATEGORIES: Record<string, string> = {
  game_design: 'Game Design Document', art_direction: 'Art Direction', ui: 'UI Documentation',
  technical: 'Technical Documentation', roadmap: 'Production Roadmap', decisions: 'Decisions and Approvals',
};

export function Documentation({ canonicalOnly = false }: { canonicalOnly?: boolean }) {
  const { data: docs, error, reload } = useApi<any[]>('/documents');
  const { data: sources } = useApi<any[]>(canonicalOnly ? '/brain/sources' : null);
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState('');
  const [creating, setCreating] = useState(false);
  const selectedId = params.get('doc');

  const list = useMemo(() => (docs ?? []).filter((d) => (!canonicalOnly || d.approved) && (!q || (d.title + d.content).toLowerCase().includes(q.toLowerCase()))), [docs, q, canonicalOnly]);
  useEffect(() => { if (!selectedId && list.length) setParams({ doc: list[0].id }, { replace: true }); }, [list, selectedId, setParams]);

  if (error) return <ErrorBox error={error} />;
  if (!docs) return <Spinner />;
  const grouped = Object.keys(DOC_CATEGORIES).map((c) => ({ c, items: list.filter((d) => d.category === c) })).filter((g) => g.items.length);

  return (
    <div>
      <PageHeader
        icon={canonicalOnly ? <BookMarked size={20} className="text-gold" /> : <BookText size={20} className="text-gold" />}
        title={canonicalOnly ? 'Canonical Documentation' : 'Game Documentation'}
        subtitle={canonicalOnly ? 'Tylko zatwierdzone dokumenty — to źródło prawdy, które agenci traktują jako autorytatywne.' : 'Baza wiedzy projektu. Każda edycja tworzy nową wersję, która wymaga zatwierdzenia, zanim stanie się kanoniczna.'}
        actions={!canonicalOnly && <Button variant="primary" icon={<Plus size={14} />} onClick={() => setCreating(true)}>Nowy dokument</Button>} />

      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <div className="space-y-3">
          <div className="relative"><Search size={14} className="absolute left-2.5 top-2 text-faint" /><Input className="pl-8" placeholder="Szukaj w dokumentacji…" value={q} onChange={(e) => setQ(e.target.value)} /></div>
          {grouped.map((g) => (
            <div key={g.c}>
              <div className="mb-1 px-1 text-[10.5px] font-semibold uppercase tracking-wider text-faint">{DOC_CATEGORIES[g.c]}</div>
              {g.items.map((d) => (
                <button key={d.id} onClick={() => setParams({ doc: d.id })}
                  className={cx('mb-1 flex w-full items-center gap-2 rounded-md border px-2.5 py-2 text-left text-[12.5px] cursor-pointer', selectedId === d.id ? 'border-gold/50 bg-gold/5' : 'border-line bg-panel hover:border-line2')}>
                  <span className="flex-1 truncate">{d.title}</span>
                  {d.approved ? <CheckCircle2 size={13} className="text-mint shrink-0" /> : <Badge color="#f5c542">v{d.version} niezatw.</Badge>}
                </button>
              ))}
            </div>
          ))}
          {!grouped.length && <Empty title="Brak dokumentów" />}
          {canonicalOnly && sources && (
            <Card title="Autorytatywne pliki w repozytorium" icon={<ShieldCheck size={14} className="text-mint" />} bodyClass="p-3">
              <ul className="space-y-1 text-[12px]">
                {sources.filter((s) => s.authoritative && s.origin.startsWith('file:') && !s.archived).map((s) => <li key={s.id} className="font-mono text-mute">{s.name}</li>)}
              </ul>
            </Card>
          )}
        </div>
        {selectedId ? <DocViewer key={selectedId} id={selectedId} onChanged={reload} readOnly={canonicalOnly} /> : <Card><Empty title="Wybierz dokument" /></Card>}
      </div>
      <NewDocModal open={creating} onClose={() => setCreating(false)} onCreated={(d) => { reload(); setParams({ doc: d.id }); setCreating(false); }} />
    </div>
  );
}

function DocViewer({ id, onChanged, readOnly }: { id: string; onChanged: () => void; readOnly?: boolean }) {
  const { data: doc, error, reload } = useApi<any>(`/documents/${id}`);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState('');
  const [title, setTitle] = useState('');
  const [note, setNote] = useState('');
  const [showVersions, setShowVersions] = useState(false);
  const [viewVersion, setViewVersion] = useState<any>(null);
  const [rollback, setRollback] = useState<number | null>(null);
  const done = () => { reload(); onChanged(); };

  const save = useAction(() => api(`/documents/${id}`, { method: 'PUT', body: { content: draft, title, note: note || undefined } }), { success: 'Zapisano nową wersję (wymaga zatwierdzenia)', onDone: () => { setEditing(false); done(); } });
  const approve = useAction(() => api(`/documents/${id}/approve`, { body: {} }), { success: 'Dokument jest teraz kanoniczny', onDone: done });
  const doRollback = useAction((v: number) => api(`/documents/${id}/rollback`, { body: { version: v } }), { success: 'Przywrócono wersję', onDone: () => { setRollback(null); setViewVersion(null); done(); } });

  if (error) return <ErrorBox error={error} />;
  if (!doc) return <Card><Spinner /></Card>;

  return (
    <Card
      title={<span className="flex items-center gap-2">{doc.title}<Badge color="#8a93a6">v{doc.version}</Badge>{doc.approved ? <Badge color="#34d399">kanoniczny</Badge> : <Badge color="#f5c542">wymaga zatwierdzenia</Badge>}</span>}
      actions={!editing && <>
        <Button size="sm" variant="ghost" icon={<History size={13} />} onClick={() => setShowVersions(true)}>Wersje ({doc.versions.length})</Button>
        {!readOnly && <Button size="sm" icon={<Pencil size={13} />} onClick={() => { setDraft(doc.content); setTitle(doc.title); setNote(''); setEditing(true); }}>Edytuj</Button>}
        {!doc.approved && <Button size="sm" variant="success" icon={<CheckCircle2 size={13} />} loading={approve.loading} onClick={() => approve.run()}>Zatwierdź</Button>}
      </>}>
      <div className="mb-3 text-[11px] text-faint">{DOC_CATEGORIES[doc.category]} · autor: {doc.author} · źródło: {doc.source ?? '—'} · aktualizacja: {fmtDateTime(doc.updated_at)}</div>
      {editing ? (
        <div className="space-y-3">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} />
          <Textarea className="min-h-[420px] font-mono text-[12.5px]" value={draft} onChange={(e) => setDraft(e.target.value)} />
          <Input placeholder="Notatka do wersji (opcjonalnie)" value={note} onChange={(e) => setNote(e.target.value)} />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setEditing(false)}>Anuluj</Button>
            <Button variant="primary" icon={<Save size={14} />} loading={save.loading} disabled={!draft.trim()} onClick={() => save.run()}>Zapisz jako v{doc.version + 1}</Button>
          </div>
          <p className="text-[11px] text-faint">Zmiana dokumentacji kanonicznej wymaga zatwierdzenia — do tego czasu agenci widzą ją jako propozycję.</p>
        </div>
      ) : <Markdown text={doc.content} />}

      <Modal open={showVersions} onClose={() => { setShowVersions(false); setViewVersion(null); }} title={`Historia wersji — ${doc.title}`} width="max-w-4xl">
        <div className="grid gap-3 md:grid-cols-[220px_1fr]">
          <ul className="space-y-1">
            {doc.versions.map((v: any) => (
              <li key={v.id}>
                <button onClick={async () => setViewVersion(await api(`/documents/${id}/versions/${v.version}`))}
                  className={cx('w-full rounded-md border px-2 py-1.5 text-left text-xs cursor-pointer', viewVersion?.version === v.version ? 'border-gold/50' : 'border-line hover:border-line2')}>
                  <div className="flex items-center justify-between"><b>v{v.version}</b>{v.approved ? <CheckCircle2 size={12} className="text-mint" /> : null}</div>
                  <div className="text-faint">{v.author} · {fmtDateTime(v.created_at)}</div>
                  {v.note && <div className="truncate text-mute">{v.note}</div>}
                </button>
              </li>
            ))}
          </ul>
          <div className="min-h-[200px] rounded-md border border-line p-3">
            {viewVersion ? (
              <>
                <div className="mb-2 flex items-center justify-between"><b className="text-xs">v{viewVersion.version}</b>
                  {viewVersion.version !== doc.version && <Button size="sm" icon={<RotateCcw size={12} />} onClick={() => setRollback(viewVersion.version)}>Przywróć tę wersję</Button>}</div>
                <Markdown text={viewVersion.content} />
              </>
            ) : <Empty title="Wybierz wersję" />}
          </div>
        </div>
      </Modal>
      <Confirm open={rollback !== null} onClose={() => setRollback(null)} title="Przywrócić wersję?" loading={doRollback.loading}
        text={`Utworzy nową wersję v${doc.version + 1} z treścią v${rollback}. Historia zostaje zachowana.`} onConfirm={() => doRollback.run(rollback!)} />
    </Card>
  );
}

function NewDocModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: (d: any) => void }) {
  const [title, setTitle] = useState(''); const [category, setCategory] = useState('game_design'); const [content, setContent] = useState('');
  const create = useAction(() => api('/documents', { body: { title, category, content } }), { success: 'Utworzono dokument (niezatwierdzony)', onDone: (d) => { setTitle(''); setContent(''); onCreated(d); } });
  return (
    <Modal open={open} onClose={onClose} title="Nowy dokument" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" loading={create.loading} disabled={!title.trim()} onClick={() => create.run()}>Utwórz</Button></>}>
      <div className="space-y-3">
        <Field label="Tytuł"><Input value={title} onChange={(e) => setTitle(e.target.value)} /></Field>
        <Field label="Kategoria"><Select value={category} onChange={(e) => setCategory(e.target.value)}>{Object.entries(DOC_CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</Select></Field>
        <Field label="Treść (Markdown)"><Textarea className="min-h-[240px] font-mono text-[12.5px]" value={content} onChange={(e) => setContent(e.target.value)} /></Field>
      </div>
    </Modal>
  );
}
