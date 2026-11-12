import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Editor, { DiffEditor, type OnMount } from '@monaco-editor/react';
import '../components/monaco';
import { MONACO_OPTIONS } from '../components/monaco';
import { Code2, FileCode, Folder, FolderOpen, File, Save, Undo2, Redo2, Search, History, Lock, Plus, Trash2, X, Bot, Hammer, ShieldAlert, Wand2, RotateCcw, ChevronRight, ChevronDown, Image as ImageIcon } from 'lucide-react';
import { api, useApi, fmtDateTime, timeAgo, EXEC_STATUS } from '../lib/api';
import { Badge, Button, Confirm, Empty, Field, Input, Modal, Select, Spinner, StatusBadge, Tabs, Textarea, useAction, useToast, cx, NotConfigured } from '../components/ui';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

interface OpenFile { path: string; content: string; saved: string; language: string; modifiedAt: string; writable: boolean; protected: boolean }

export function Workspace({ mode }: { mode: 'all' | 'luau' }) {
  const { data: treeData, reload: reloadTree } = useApi<any>('/files/tree', 5000);
  const [params, setParams] = useSearchParams();
  const [open, setOpen] = useState<OpenFile[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [showVersions, setShowVersions] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [exec, setExec] = useState<string | null>(null);
  const editorRef = useRef<any>(null);
  const toast = useToast();

  const cur = open.find((f) => f.path === active) ?? null;
  const { data: meta, reload: reloadMeta } = useApi<any>(active ? `/files/content?path=${encodeURIComponent(active)}` : null, 4000);

  const openFile = useCallback(async (path: string) => {
    if (/\.(png|jpe?g|gif|webp|svg)$/i.test(path)) { window.open(`/api/files/raw?path=${encodeURIComponent(path)}`, '_blank'); return; }
    setActive(path);
    setParams({ file: path }, { replace: true });
    if (open.some((f) => f.path === path)) return;
    try {
      const r = await api<any>(`/files/content?path=${encodeURIComponent(path)}`);
      setOpen((o) => (o.some((f) => f.path === path) ? o : [...o, { path, content: r.content, saved: r.content, language: r.language, modifiedAt: r.modifiedAt, writable: r.writable, protected: r.protected }]));
    } catch (e: any) { toast('error', e.message); }
  }, [open, setParams, toast]);

  useEffect(() => { const f = params.get('file'); if (f && !active) void openFile(f); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // pick up external changes (agent approvals, Rojo, other editors) when the tab is not dirty
  useEffect(() => {
    if (!meta || !cur) return;
    if (meta.modifiedAt !== cur.modifiedAt && cur.content === cur.saved) {
      setOpen((o) => o.map((f) => (f.path === meta.path ? { ...f, content: meta.content, saved: meta.content, modifiedAt: meta.modifiedAt } : f)));
    }
  }, [meta]); // eslint-disable-line react-hooks/exhaustive-deps

  const save = useAction(async (force = false) => {
    if (!cur) return;
    const r = await api<any>('/files/content', { method: 'PUT', body: { path: cur.path, content: cur.content, expectedModifiedAt: cur.modifiedAt, force } });
    setOpen((o) => o.map((f) => (f.path === cur.path ? { ...f, saved: f.content, modifiedAt: r.modifiedAt } : f)));
    reloadMeta();
    return r;
  }, { success: 'Zapisano — Rojo zsynchronizuje plik ze Studio' });

  const onMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => document.getElementById('ws-save')?.click());
  };
  const trigger = (id: string) => { editorRef.current?.focus(); editorRef.current?.trigger('toolbar', id, null); };
  const close = (path: string) => {
    const f = open.find((x) => x.path === path);
    if (f && f.content !== f.saved && !window.confirm(`${path} ma niezapisane zmiany. Zamknąć?`)) return;
    const rest = open.filter((x) => x.path !== path);
    setOpen(rest);
    if (active === path) { setActive(rest[rest.length - 1]?.path ?? null); }
  };

  const filterFn = useCallback((n: any): any => {
    if (mode === 'all') return n;
    if (n.type === 'file') return /\.(luau|lua)$/i.test(n.name) ? n : null;
    if (!n.path.startsWith('src')) return null;
    const children = (n.children ?? []).map(filterFn).filter(Boolean);
    return { ...n, children };
  }, [mode]);
  const tree = useMemo(() => (treeData?.tree ?? []).map(filterFn).filter(Boolean), [treeData, filterFn]);
  const locks: any[] = treeData?.locks ?? [];

  return (
    <div className="-m-4 flex h-[calc(100vh-48px)] flex-col sm:-m-6">
      <div className="flex items-center gap-2 border-b border-line bg-panel px-4 py-2">
        {mode === 'luau' ? <FileCode size={16} className="text-gold" /> : <Code2 size={16} className="text-gold" />}
        <span className="font-semibold">{mode === 'luau' ? 'Luau Editor' : 'Development Workspace'}</span>
        <span className="text-xs text-faint">— pliki projektu Rojo; zapis trafia na dysk, a Rojo przesyła go do Studio</span>
      </div>
      <div className="flex min-h-0 flex-1">
        {/* explorer */}
        <aside className="w-64 shrink-0 overflow-y-auto border-r border-line bg-panel py-2 max-md:hidden">
          <div className="flex items-center justify-between px-3 pb-1 text-[10.5px] font-semibold tracking-wider text-faint">
            PLIKI <button className="rounded p-0.5 hover:bg-panel3 cursor-pointer" title="Nowy plik" onClick={() => setCreating(true)}><Plus size={13} /></button>
          </div>
          {!treeData ? <Spinner /> : tree.map((n: any) => <TreeNode key={n.path} node={n} depth={0} active={active} onOpen={openFile} locks={locks} />)}
        </aside>

        {/* editor */}
        <section className="flex min-w-0 flex-1 flex-col">
          <div className="flex h-9 shrink-0 items-stretch overflow-x-auto border-b border-line bg-panel">
            {open.map((f) => (
              <div key={f.path} onClick={() => { setActive(f.path); setParams({ file: f.path }, { replace: true }); }}
                className={cx('group flex cursor-pointer items-center gap-1.5 border-r border-line px-3 text-[12px]', f.path === active ? 'bg-bg text-ink' : 'text-mute hover:text-ink')}>
                <File size={12} />{f.path.split('/').pop()}{f.content !== f.saved && <span className="h-1.5 w-1.5 rounded-full bg-gold" />}
                <button onClick={(e) => { e.stopPropagation(); close(f.path); }} className="ml-1 rounded opacity-50 hover:bg-panel3 hover:opacity-100 cursor-pointer"><X size={12} /></button>
              </div>
            ))}
          </div>
          {cur ? (
            <>
              <div className="flex flex-wrap items-center gap-1.5 border-b border-line bg-panel px-3 py-1.5">
                <span className="mr-2 font-mono text-[11.5px] text-mute">{cur.path}</span>
                {cur.protected && <Badge color="#fb923c"><ShieldAlert size={11} /> chroniony</Badge>}
                {!cur.writable && <Badge color="#f05252">tylko do odczytu</Badge>}
                {meta?.lock && <Badge color="#f05252"><Lock size={11} /> edytuje {meta.lock.agent_name}</Badge>}
                {meta?.pending?.length > 0 && <Link to="/approvals"><Badge color="#f5c542">{meta.pending.length} oczekujących zmian od agentów</Badge></Link>}
                <span className="text-[11px] text-faint">zmod. {timeAgo(meta?.modifiedAt ?? cur.modifiedAt)}</span>
                <div className="flex-1" />
                <Button size="sm" variant="ghost" icon={<Undo2 size={13} />} onClick={() => trigger('undo')} title="Cofnij" />
                <Button size="sm" variant="ghost" icon={<Redo2 size={13} />} onClick={() => trigger('redo')} title="Ponów" />
                <Button size="sm" variant="ghost" icon={<Search size={13} />} onClick={() => trigger('actions.find')} title="Szukaj (Ctrl+F)" />
                <Button size="sm" variant="ghost" icon={<Wand2 size={13} />} disabled={cur.language !== 'json'} onClick={() => trigger('editor.action.formatDocument')} title={cur.language === 'json' ? 'Formatuj' : 'Formatowanie dostępne dla JSON (brak formattera Luau)'} />
                <Button size="sm" variant="ghost" icon={<History size={13} />} onClick={() => setShowVersions(true)}>Wersje</Button>
                {cur.writable && <Button size="sm" variant="ghost" icon={<Trash2 size={13} />} onClick={() => setDeleting(cur.path)} />}
                <Button id="ws-save" size="sm" variant="primary" icon={<Save size={13} />} disabled={!cur.writable || cur.content === cur.saved} loading={save.loading}
                  onClick={async () => { const r = await save.run(false); if (r === undefined && window.confirm('Zapis nie powiódł się (plik zmieniony na dysku lub zablokowany). Wymusić zapis?')) void save.run(true); }}>Zapisz</Button>
              </div>
              <div className="min-h-0 flex-1">
                <Editor key={cur.path} theme="studio-dark" path={cur.path} language={cur.language} value={cur.content} options={{ ...MONACO_OPTIONS, readOnly: !cur.writable }} onMount={onMount}
                  onChange={(v) => setOpen((o) => o.map((f) => (f.path === cur.path ? { ...f, content: v ?? '' } : f)))} />
              </div>
            </>
          ) : <div className="flex flex-1 items-center justify-center"><Empty icon={<Code2 size={32} />} title="Otwórz plik z drzewa po lewej">Edytujesz prawdziwe pliki projektu. Pliki .rbxl nie są edytowalne.</Empty></div>}
          <OutputConsole onExec={setExec} />
        </section>

        {/* assistant */}
        <AgentAssistant file={cur?.path ?? null} onExec={setExec} />
      </div>

      {cur && <VersionsModal open={showVersions} path={cur.path} current={cur.saved} onClose={() => setShowVersions(false)} onRestored={() => { setShowVersions(false); setOpen((o) => o.filter((f) => f.path !== cur.path)); void openFile(cur.path); }} />}
      <NewFileModal open={creating} onClose={() => setCreating(false)} onCreated={(p) => { setCreating(false); reloadTree(); void openFile(p); }} />
      <DeleteFile path={deleting} onClose={() => setDeleting(null)} onDone={(p) => { setDeleting(null); setOpen((o) => o.filter((f) => f.path !== p)); setActive(null); reloadTree(); }} />
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}

function TreeNode({ node, depth, active, onOpen, locks }: { node: any; depth: number; active: string | null; onOpen: (p: string) => void; locks: any[] }) {
  const [open, setOpen] = useState(depth < 1);
  const pad = { paddingLeft: 10 + depth * 12 };
  if (node.type === 'dir') {
    return (
      <div>
        <button style={pad} onClick={() => setOpen(!open)} className="flex w-full items-center gap-1 py-0.5 pr-2 text-left text-[12.5px] text-mute hover:bg-panel3 hover:text-ink cursor-pointer">
          {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}{open ? <FolderOpen size={13} className="text-gold" /> : <Folder size={13} className="text-gold" />}<span className="truncate">{node.name.split('/').pop()}</span>
        </button>
        {open && node.children?.map((c: any) => <TreeNode key={c.path} node={c} depth={depth + 1} active={active} onOpen={onOpen} locks={locks} />)}
      </div>
    );
  }
  const lock = locks.find((l) => l.path === node.path);
  const img = /\.(png|jpe?g|gif|webp|svg)$/i.test(node.name);
  return (
    <button style={{ paddingLeft: 24 + depth * 12 }} onClick={() => onOpen(node.path)} title={node.path}
      className={cx('flex w-full items-center gap-1.5 py-0.5 pr-2 text-left text-[12.5px] cursor-pointer', active === node.path ? 'bg-gold/10 text-gold' : 'text-ink/85 hover:bg-panel3')}>
      {img ? <ImageIcon size={12} className="shrink-0 text-violet" /> : <File size={12} className="shrink-0 text-faint" />}
      <span className="truncate">{node.name}</span>
      {lock && <Lock size={11} className="ml-auto shrink-0 text-ruby" />}
    </button>
  );
}

function OutputConsole({ onExec }: { onExec: (id: string) => void }) {
  const [tab, setTab] = useState<'output' | 'errors' | 'warnings' | 'agents' | 'builds' | 'tests'>('output');
  const [collapsed, setCollapsed] = useState(false);
  const { data: builds, reload: reloadBuilds } = useApi<any[]>('/builds', 6000);
  const { data: logs } = useApi<any[]>('/logs?limit=120', 5000);
  const { data: execs } = useApi<any[]>('/executions', 4000);
  const { data: tests } = useApi<any[]>('/tests', 8000);
  const build = useAction(() => api('/builds', { body: {} }), { success: (r: any) => (r.status === 'success' ? `Build OK (${r.ms} ms)` : 'Build nieudany — zobacz Output'), onDone: reloadBuilds });
  const errors = (logs ?? []).filter((l) => l.level === 'error');
  const warnings = (logs ?? []).filter((l) => l.level === 'warn');
  const last = builds?.[0];
  return (
    <div className={cx('shrink-0 border-t border-line bg-panel', collapsed ? 'h-9' : 'h-56')}>
      <div className="flex items-center pr-2">
        <Tabs className="flex-1 border-0" value={tab} onChange={(t) => { setTab(t); setCollapsed(false); }} tabs={[
          { id: 'output', label: 'Output' }, { id: 'errors', label: 'Errors', count: errors.length }, { id: 'warnings', label: 'Warnings', count: warnings.length },
          { id: 'agents', label: 'Agent Logs' }, { id: 'builds', label: 'Build Logs' }, { id: 'tests', label: 'Test Results' },
        ]} />
        <Button size="sm" variant="ghost" icon={<Hammer size={12} />} loading={build.loading} onClick={() => build.run()}>rojo build</Button>
        <Button size="sm" variant="ghost" onClick={() => setCollapsed(!collapsed)}>{collapsed ? '▲' : '▼'}</Button>
      </div>
      {!collapsed && (
        <div className="h-[calc(100%-38px)] overflow-y-auto px-3 py-2 font-mono text-[11.5px]">
          {tab === 'output' && (last ? <pre className={cx('whitespace-pre-wrap', last.status === 'failed' ? 'text-ruby' : 'text-ink/80')}>[{fmtDateTime(last.created_at)}] rojo build — {last.status} ({last.duration_ms} ms){'\n'}{last.output}</pre> : <span className="text-faint">Brak wyjścia. Uruchom „rojo build”, aby zweryfikować projekt.</span>)}
          {tab === 'errors' && (errors.length ? errors.map((l) => <div key={l.id} className="text-ruby">[{fmtDateTime(l.timestamp)}] {l.actor}: {l.action} — {l.details}</div>) : <span className="text-faint">Brak błędów.</span>)}
          {tab === 'warnings' && (warnings.length ? warnings.map((l) => <div key={l.id} className="text-gold">[{fmtDateTime(l.timestamp)}] {l.actor}: {l.action} — {l.details}</div>) : <span className="text-faint">Brak ostrzeżeń.</span>)}
          {tab === 'agents' && ((execs ?? []).length ? (execs ?? []).slice(0, 40).map((e) => (
            <div key={e.id} className="flex cursor-pointer gap-2 hover:bg-panel2" onClick={() => onExec(e.id)}>
              <span className="text-faint">[{fmtDateTime(e.started_at)}]</span><span style={{ color: e.agent_color }}>{e.agent_name}</span><StatusBadge map={EXEC_STATUS} value={e.status} /><span className="truncate text-mute">{e.result?.summary ?? e.error ?? e.prompt}</span>
            </div>
          )) : <span className="text-faint">Brak wykonań agentów.</span>)}
          {tab === 'builds' && ((builds ?? []).length ? (builds ?? []).map((b) => <div key={b.id} className={b.status === 'failed' ? 'text-ruby' : 'text-mint'}>[{fmtDateTime(b.created_at)}] {b.kind} ({b.trigger}) — {b.status} · {b.duration_ms} ms</div>) : <span className="text-faint">Brak buildów.</span>)}
          {tab === 'tests' && (tests ?? []).map((t) => <div key={t.id}><span className={t.last_status === 'passed' ? 'text-mint' : t.last_status === 'failed' ? 'text-ruby' : 'text-faint'}>[{t.last_status}]</span> {t.name} <span className="text-faint">{t.last_run_at ? fmtDateTime(t.last_run_at) : ''}</span></div>)}
        </div>
      )}
    </div>
  );
}

function AgentAssistant({ file, onExec }: { file: string | null; onExec: (id: string) => void }) {
  const { status } = useStatus();
  const { data: agents } = useApi<any[]>('/agents');
  const [agent, setAgent] = useState('lucius');
  const [prompt, setPrompt] = useState('');
  const run = useAction(() => api<{ executionId: string }>(`/agents/${agent}/run`, { body: { prompt, relatedFiles: file ? [file] : [] } }), { success: 'Agent pracuje — zmiany trafią do Approvals', onDone: (r) => { setPrompt(''); onExec(r.executionId); } });
  return (
    <aside className="w-72 shrink-0 overflow-y-auto border-l border-line bg-panel p-3 max-xl:hidden">
      <div className="mb-2 flex items-center gap-2 text-[12.5px] font-semibold"><Bot size={14} className="text-cyan" />Agent Assistant {!status?.ai.configured && <NotConfigured />}</div>
      <div className="space-y-2">
        <Select value={agent} onChange={(e) => setAgent(e.target.value)}>{(agents ?? []).map((a) => <option key={a.id} value={a.id}>{a.name} — {a.role}</option>)}</Select>
        <div className="rounded-md border border-line bg-panel2 px-2 py-1.5 text-[11px] text-mute">Kontekst: {file ? <span className="font-mono text-ink">{file}</span> : 'brak otwartego pliku'}</div>
        <Textarea className="min-h-[120px]" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={file ? 'np. Dodaj animację TweenService do paska HP' : 'Otwórz plik lub opisz zadanie'} />
        <Button variant="primary" className="w-full" loading={run.loading} disabled={!prompt.trim() || !status?.ai.configured || status?.emergencyStop} onClick={() => run.run()}>Poproś agenta</Button>
        <p className="text-[11px] text-faint">Agent widzi aktualną treść pliku i kontekst Project Brain. Proponowane zmiany zobaczysz jako diff w Approvals (w trybie ASSISTANT).</p>
      </div>
    </aside>
  );
}

function VersionsModal({ open, path, current, onClose, onRestored }: { open: boolean; path: string; current: string; onClose: () => void; onRestored: () => void }) {
  const { data: versions } = useApi<any[]>(open ? `/files/versions?path=${encodeURIComponent(path)}` : null);
  const [sel, setSel] = useState<any>(null);
  const restore = useAction((id: string) => api('/files/rollback', { body: { versionId: id } }), { success: 'Przywrócono wersję', onDone: onRestored });
  return (
    <Modal open={open} onClose={onClose} title={`Historia wersji — ${path}`} width="max-w-6xl">
      <div className="grid gap-3 md:grid-cols-[240px_1fr]">
        <div className="space-y-1">
          {!versions ? <Spinner /> : versions.length === 0 ? <Empty title="Brak zapisanych wersji">Wersje powstają przy każdym zapisie z dashboardu lub zatwierdzeniu zmiany agenta.</Empty> : versions.map((v) => (
            <button key={v.id} onClick={async () => setSel(await api(`/files/versions/${v.id}`))} className={cx('w-full rounded-md border px-2 py-1.5 text-left text-xs cursor-pointer', sel?.id === v.id ? 'border-gold/50' : 'border-line hover:border-line2')}>
              <div className="font-medium">{fmtDateTime(v.created_at)}</div><div className="text-faint">{v.author}</div><div className="truncate text-mute">{v.note}</div>
            </button>
          ))}
        </div>
        <div className="min-h-[420px] rounded-md border border-line">
          {sel ? (
            <>
              <div className="flex items-center justify-between border-b border-line px-3 py-1.5 text-xs"><span className="text-mute">Lewa: stan przed zmianą z {fmtDateTime(sel.created_at)} · Prawa: obecny</span>
                <Button size="sm" icon={<RotateCcw size={12} />} loading={restore.loading} onClick={() => restore.run(sel.id)}>{sel.content === null ? 'Przywróć (usuń plik)' : 'Przywróć tę wersję'}</Button></div>
              <div className="h-[420px]"><DiffEditor theme="studio-dark" original={sel.content ?? ''} modified={current} language={path.endsWith('.json') ? 'json' : 'lua'} options={{ ...MONACO_OPTIONS, readOnly: true, renderSideBySide: true }} /></div>
            </>
          ) : <Empty title="Wybierz wersję, aby zobaczyć diff" />}
        </div>
      </div>
    </Modal>
  );
}

function NewFileModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: (p: string) => void }) {
  const [path, setPath] = useState('src/client/');
  const [kind, setKind] = useState('client');
  const templates: Record<string, { suffix: string; content: string }> = {
    client: { suffix: '.client.luau', content: '--!strict\n-- LocalScript (StarterPlayerScripts.Client)\nlocal Players = game:GetService("Players")\nlocal player = Players.LocalPlayer\n' },
    server: { suffix: '.server.luau', content: '--!strict\n-- Script (ServerScriptService.Server)\n' },
    module: { suffix: '.luau', content: '--!strict\nlocal Module = {}\n\nreturn Module\n' },
    gui: { suffix: '.model.json', content: '{\n  "ClassName": "ScreenGui",\n  "Properties": { "ResetOnSpawn": false, "ZIndexBehavior": "Sibling" },\n  "Children": []\n}\n' },
    doc: { suffix: '.md', content: '# Nowy dokument\n' },
  };
  const create = useAction(() => api<{ path: string }>('/files/create', { body: { path, content: templates[kind].content } }), { success: 'Utworzono plik', onDone: (r) => onCreated(r.path) });
  return (
    <Modal open={open} onClose={onClose} title="Nowy plik" footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" loading={create.loading} onClick={() => create.run()}>Utwórz</Button></>}>
      <div className="space-y-3">
        <Field label="Typ"><Select value={kind} onChange={(e) => { setKind(e.target.value); const dir = { client: 'src/client/', server: 'src/server/', module: 'src/shared/', gui: 'src/gui/', doc: 'docs/' }[e.target.value]!; setPath(dir); }}>
          <option value="client">LocalScript (src/client)</option><option value="server">Script (src/server)</option><option value="module">ModuleScript (src/shared)</option><option value="gui">ScreenGui .model.json (src/gui)</option><option value="doc">Dokument .md (docs)</option>
        </Select></Field>
        <Field label="Ścieżka" hint={`Zakończ nazwą z rozszerzeniem ${templates[kind].suffix}`}><Input value={path} onChange={(e) => setPath(e.target.value)} /></Field>
      </div>
    </Modal>
  );
}

function DeleteFile({ path, onClose, onDone }: { path: string | null; onClose: () => void; onDone: (p: string) => void }) {
  const del = useAction(() => api(`/files?path=${encodeURIComponent(path!)}`, { method: 'DELETE' }), { success: 'Usunięto (kopia w historii wersji)', onDone: () => onDone(path!) });
  return <Confirm open={!!path} onClose={onClose} danger loading={del.loading} title="Usunąć plik?" text={<>Plik <code>{path}</code> zostanie usunięty z dysku (i ze Studio przez Rojo). Kopia trafi do historii wersji.</>} onConfirm={() => del.run()} />;
}
