import fs from 'node:fs';
import { all, get, insert, log, now, run, sha256, uid, update, FTS_AVAILABLE, tx, getSettings, db } from './db.ts';
import { listFilesRecursive, readProjectFile, resolveProjectPath } from './paths.ts';
import { STYLE_LOCK_PREFIX } from './knowledge.ts';

export interface BrainSource {
  id: string; name: string; source_type: string; origin: string; content_hash: string | null; version: number;
  indexing_status: 'registered' | 'indexing' | 'indexed' | 'failed' | 'stale' | 'missing'; authoritative: boolean;
  categories: string[]; access: string; archived: boolean; content: string | null; error: string | null;
  chunk_count: number; last_indexed_at: string | null; created_at: string; updated_at: string;
}

// ---------------- discovery ----------------

function classify(rel: string): { type: string; categories: string[]; authoritative: boolean } {
  if (rel === 'default.project.json') return { type: 'rojo-config', categories: ['technical'], authoritative: true };
  if (rel.startsWith('docs/')) return { type: 'documentation', categories: ['documentation'], authoritative: true };
  if (rel.startsWith('.claude/skills/')) return { type: 'skill', categories: ['technical', 'tooling'], authoritative: false };
  if (rel.startsWith('src/gui/')) return { type: 'gui-model', categories: ['ui', 'repository'], authoritative: false };
  if (rel.endsWith('.json')) return { type: 'json', categories: ['repository'], authoritative: false };
  return { type: 'luau', categories: ['repository', 'code'], authoritative: false };
}

const TEXT_FILE = /\.(md|txt|luau|lua|json)$/i;

/** Registers file sources that exist in the project (does not index them). */
export function discoverSources() {
  const files = [
    ...listFilesRecursive('docs', (r) => /\.(md|txt)$/i.test(r)),
    ...listFilesRecursive('src', (r) => TEXT_FILE.test(r)),
    ...listFilesRecursive('.claude/skills', (r) => r.endsWith('.md')),
    ...(fs.existsSync(resolveProjectPath('default.project.json')) ? ['default.project.json'] : []),
  ];
  const t = now();
  let added = 0;
  for (const rel of files) {
    const origin = `file:${rel}`;
    if (get('SELECT id FROM brain_sources WHERE origin = ?', origin)) continue;
    const c = classify(rel);
    insert('brain_sources', {
      id: uid('src-'), name: rel, source_type: c.type, origin, version: 0, indexing_status: 'registered',
      authoritative: c.authoritative, categories: c.categories, access: 'all-agents', archived: false, created_at: t, updated_at: t,
    });
    added++;
  }
  // knowledge base documents
  for (const d of all<{ id: string; title: string; category: string; approved: boolean }>('SELECT id, title, category, approved FROM project_documents')) {
    const origin = `kb:${d.id}`;
    const existing = get<BrainSource>('SELECT * FROM brain_sources WHERE origin = ?', origin);
    if (existing) {
      update('brain_sources', existing.id, { name: d.title, authoritative: d.approved, categories: [d.category, 'knowledge-base'] });
      continue;
    }
    insert('brain_sources', {
      id: uid('src-'), name: d.title, source_type: 'kb-document', origin, version: 0, indexing_status: 'registered',
      authoritative: d.approved, categories: [d.category, 'knowledge-base'], access: 'all-agents', archived: false, created_at: t, updated_at: t,
    });
    added++;
  }
  // mark missing files
  for (const s of all<BrainSource>("SELECT * FROM brain_sources WHERE origin LIKE 'file:%' AND indexing_status != 'missing'")) {
    const rel = s.origin.slice(5);
    if (readProjectFile(rel) === null) update('brain_sources', s.id, { indexing_status: 'missing', updated_at: t });
  }
  return added;
}

export function sourceContent(s: BrainSource): string | null {
  if (s.origin.startsWith('file:')) return readProjectFile(s.origin.slice(5));
  if (s.origin.startsWith('kb:')) {
    const d = get<{ title: string; content: string; approved: boolean; version: number }>('SELECT title, content, approved, version FROM project_documents WHERE id = ?', s.origin.slice(3));
    return d ? `# ${d.title}\n(status: ${d.approved ? 'APPROVED canonical' : 'NOT APPROVED — proposal'}, v${d.version})\n\n${d.content}` : null;
  }
  return s.content;
}

// ---------------- chunking ----------------

function chunk(text: string, type: string): { heading: string | null; content: string }[] {
  const MAX = 1400;
  const out: { heading: string | null; content: string }[] = [];
  const blocks = type === 'luau' || type === 'json' || type === 'gui-model' || type === 'rojo-config'
    ? [{ heading: null as string | null, body: text }]
    : text.split(/\n(?=#{1,3} )/).map((b) => ({ heading: (b.match(/^#{1,3} (.+)$/m)?.[1] ?? null), body: b }));
  for (const b of blocks) {
    if (b.body.length <= MAX) { if (b.body.trim()) out.push({ heading: b.heading, content: b.body.trim() }); continue; }
    const lines = b.body.split('\n');
    let cur = '';
    for (const line of lines) {
      if ((cur + '\n' + line).length > MAX && cur) { out.push({ heading: b.heading, content: cur.trim() }); cur = ''; }
      cur += (cur ? '\n' : '') + line;
    }
    if (cur.trim()) out.push({ heading: b.heading, content: cur.trim() });
  }
  return out;
}

// ---------------- indexing ----------------

export function indexSource(id: string): BrainSource {
  const s = get<BrainSource>('SELECT * FROM brain_sources WHERE id = ?', id);
  if (!s) throw new Error('Nie znaleziono źródła');
  const t = now();
  update('brain_sources', id, { indexing_status: 'indexing', updated_at: t });
  try {
    const content = sourceContent(s);
    if (content === null) {
      update('brain_sources', id, { indexing_status: 'missing', error: 'Źródło nie istnieje', updated_at: t });
      return get<BrainSource>('SELECT * FROM brain_sources WHERE id = ?', id)!;
    }
    const hash = sha256(content);
    const pieces = chunk(content, s.source_type);
    tx(() => {
      if (FTS_AVAILABLE) run('DELETE FROM brain_fts WHERE source_id = ?', id);
      run('DELETE FROM brain_chunks WHERE source_id = ?', id);
      pieces.forEach((p, i) => {
        const cid = uid('ch-');
        insert('brain_chunks', { id: cid, source_id: id, ord: i, heading: p.heading, content: p.content, metadata: { source: s.name, type: s.source_type } });
        if (FTS_AVAILABLE) run('INSERT INTO brain_fts (content, heading, chunk_id, source_id) VALUES (?,?,?,?)', p.content, p.heading ?? '', cid, id);
      });
      update('brain_sources', id, {
        content_hash: hash, version: hash === s.content_hash ? s.version : s.version + 1, indexing_status: 'indexed',
        chunk_count: pieces.length, error: null, last_indexed_at: now(), updated_at: now(),
      });
    });
  } catch (e: any) {
    update('brain_sources', id, { indexing_status: 'failed', error: String(e?.message ?? e), updated_at: now() });
    log('Project Brain', 'Błąd indeksowania', `${s.name}: ${e?.message ?? e}`, { type: 'brain_source', id }, 'error');
  }
  return get<BrainSource>('SELECT * FROM brain_sources WHERE id = ?', id)!;
}

export function indexAll(onlyChanged = false) {
  discoverSources();
  const sources = all<BrainSource>('SELECT * FROM brain_sources WHERE archived = 0');
  let indexed = 0, failed = 0, skipped = 0;
  for (const s of sources) {
    if (onlyChanged && s.indexing_status === 'indexed') {
      const c = sourceContent(s);
      if (c !== null && sha256(c) === s.content_hash) { skipped++; continue; }
    }
    const r = indexSource(s.id);
    if (r.indexing_status === 'indexed') indexed++; else failed++;
  }
  log('Project Brain', 'Indeksowanie zakończone', `Zaindeksowano ${indexed}, pominięto (bez zmian) ${skipped}, błędy ${failed}.`, undefined, failed ? 'warn' : 'success');
  return { indexed, failed, skipped, total: sources.length };
}

/** Marks sources whose underlying content changed since last indexing as stale. */
export function refreshStaleness() {
  for (const s of all<BrainSource>("SELECT * FROM brain_sources WHERE indexing_status = 'indexed' AND archived = 0")) {
    const c = sourceContent(s);
    if (c === null) update('brain_sources', s.id, { indexing_status: 'missing' });
    else if (sha256(c) !== s.content_hash) update('brain_sources', s.id, { indexing_status: 'stale' });
  }
}

// ---------------- retrieval ----------------

export interface RetrievedChunk { chunkId: string; sourceId: string; sourceName: string; heading: string | null; content: string; score: number; authoritative: boolean }

const STOP = new Set(['oraz', 'który', 'która', 'które', 'jest', 'dla', 'przez', 'with', 'that', 'this', 'from', 'have', 'into', 'the', 'and', 'nie', 'się', 'jak', 'aby', 'żeby']);

function terms(q: string) {
  return Array.from(new Set(
    q.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l')
      .split(/[^a-z0-9_]+/).filter((w) => w.length >= 3 && !STOP.has(w)),
  )).slice(0, 40);
}

export function search(query: string, limit = 8): RetrievedChunk[] {
  const ts = terms(query);
  if (!ts.length) return [];
  let rows: any[] = [];
  if (FTS_AVAILABLE) {
    const match = ts.map((t) => `"${t}"*`).join(' OR ');
    try {
      rows = db.prepare(
        `SELECT f.chunk_id AS chunkId, f.source_id AS sourceId, bm25(brain_fts) AS score
         FROM brain_fts f JOIN brain_sources s ON s.id = f.source_id
         WHERE brain_fts MATCH ? AND s.archived = 0 AND s.indexing_status IN ('indexed','stale')
         ORDER BY score LIMIT ?`,
      ).all(match, limit * 3) as any[];
    } catch { rows = []; }
  }
  if (!rows.length) {
    // keyword fallback
    const chunks = all<any>(`SELECT c.id AS chunkId, c.source_id AS sourceId, c.content FROM brain_chunks c JOIN brain_sources s ON s.id = c.source_id WHERE s.archived = 0`);
    rows = chunks
      .map((c) => {
        const text = c.content.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        const sc = ts.reduce((acc, t) => acc + (text.split(t).length - 1), 0);
        return { chunkId: c.chunkId, sourceId: c.sourceId, score: -sc };
      })
      .filter((r) => r.score < 0)
      .sort((a, b) => a.score - b.score)
      .slice(0, limit * 3);
  }
  const out: RetrievedChunk[] = [];
  for (const r of rows) {
    const c = get<any>('SELECT c.*, s.name AS source_name, s.authoritative FROM brain_chunks c JOIN brain_sources s ON s.id = c.source_id WHERE c.id = ?', r.chunkId);
    if (!c) continue;
    // authoritative sources get a boost (bm25: lower is better)
    const score = Number(r.score) * (c.authoritative ? 1.4 : 1);
    out.push({ chunkId: c.id, sourceId: c.source_id, sourceName: c.source_name, heading: c.heading, content: c.content, score, authoritative: !!c.authoritative });
  }
  return out.sort((a, b) => a.score - b.score).slice(0, limit);
}

export interface ContextPackage {
  text: string;
  summary: string;
  sourceIds: string[];
  chunks: RetrievedChunk[];
  decisions: { code: string; title: string }[];
  query: string;
}

const VISUAL_AGENTS = new Set(['artist', 'pixel', 'blocksmith', 'lorekeeper']);

export function buildContext(opts: { agentId: string; agentRole: string; task: string; relatedFiles?: string[]; extra?: string }): ContextPackage {
  const settings = getSettings();
  const query = `${opts.task}\n${opts.agentRole}\n${(opts.relatedFiles ?? []).join(' ')}`;
  const chunks = search(query, settings.maxContextChunks);
  const decisions = all<{ code: string; title: string; description: string; category: string }>("SELECT code, title, description, category FROM project_decisions WHERE status = 'approved' ORDER BY code");
  const pending = all<{ code: string; title: string; status: string }>("SELECT code, title, status FROM project_decisions WHERE status IN ('proposed','awaiting_approval') ORDER BY code");
  const questions = all<{ question: string }>("SELECT question FROM questions WHERE status = 'open' LIMIT 5");

  const parts: string[] = [];
  parts.push('## APPROVED DECISIONS (authoritative)\n' + (decisions.map((d) => `- ${d.code} [${d.category}] ${d.title}: ${d.description}`).join('\n') || '- none'));
  if (pending.length) parts.push('## PENDING PROPOSALS (NOT facts — do not treat as approved)\n' + pending.map((d) => `- ${d.code} (${d.status}) ${d.title}`).join('\n'));
  if (questions.length) parts.push('## OPEN QUESTIONS\n' + questions.map((q) => `- ${q.question}`).join('\n'));
  if (VISUAL_AGENTS.has(opts.agentId)) parts.push(`## STYLE LOCK\nMandatory 2D/UI prompt prefix: "${STYLE_LOCK_PREFIX}"`);
  if (chunks.length) {
    parts.push('## RETRIEVED PROJECT KNOWLEDGE\n' + chunks.map((c) => `### [${c.authoritative ? 'AUTHORITATIVE' : 'reference'}] ${c.sourceName}${c.heading ? ' — ' + c.heading : ''}\n${c.content}`).join('\n\n'));
  }
  const fileParts: string[] = [];
  for (const f of opts.relatedFiles ?? []) {
    try {
      const c = readProjectFile(f);
      fileParts.push(c === null ? `### ${f}\n(file does not exist yet)` : `### ${f}\n\`\`\`\n${c}\n\`\`\``);
    } catch (e: any) { fileParts.push(`### ${f}\n(cannot read: ${e.message})`); }
  }
  if (fileParts.length) parts.push('## RELATED FILES (current content)\n' + fileParts.join('\n\n'));
  if (opts.extra) parts.push('## ADDITIONAL CONTEXT\n' + opts.extra);

  const sourceIds = Array.from(new Set(chunks.map((c) => c.sourceId)));
  const summary = `${chunks.length} fragmentów z ${sourceIds.length} źródeł, ${decisions.length} zatwierdzonych decyzji, ${pending.length} propozycji, ${(opts.relatedFiles ?? []).length} powiązanych plików.`;
  return { text: parts.join('\n\n'), summary, sourceIds, chunks, decisions: decisions.map((d) => ({ code: d.code, title: d.title })), query };
}

// ---------------- health ----------------

export function health() {
  refreshStaleness();
  const sources = all<BrainSource>('SELECT * FROM brain_sources WHERE archived = 0');
  const byHash = new Map<string, string[]>();
  for (const s of sources) if (s.content_hash) byHash.set(s.content_hash, [...(byHash.get(s.content_hash) ?? []), s.name]);
  const duplicates = [...byHash.values()].filter((v) => v.length > 1);

  const brokenRefs: { where: string; ref: string }[] = [];
  for (const t of all<{ id: string; title: string; related_files: string[]; status: string }>('SELECT id, title, related_files, status FROM tasks')) {
    if (t.status !== 'completed') continue;
    for (const f of t.related_files ?? []) { try { if (readProjectFile(f) === null) brokenRefs.push({ where: `Zadanie: ${t.title}`, ref: f }); } catch { brokenRefs.push({ where: `Zadanie: ${t.title}`, ref: f }); } }
  }
  const missingUiFiles: { where: string; ref: string }[] = [];
  for (const u of all<{ name: string; files: string[]; status: string }>('SELECT name, files, status FROM ui_elements')) {
    for (const f of u.files ?? []) { try { if (readProjectFile(f) === null) missingUiFiles.push({ where: `UI: ${u.name}`, ref: f }); } catch { /* ignore */ } }
  }
  const unapprovedDocs = all<{ id: string; title: string }>('SELECT id, title FROM project_documents WHERE approved = 0');
  const outdatedDocs = all<{ id: string; title: string; updated_at: string }>("SELECT id, title, updated_at FROM project_documents WHERE updated_at < datetime('now','-30 days')");
  const openQuestions = all('SELECT * FROM questions WHERE status = ?', 'open');
  const conflicts = detectConflicts();

  return {
    total: sources.length,
    indexed: sources.filter((s) => s.indexing_status === 'indexed').length,
    stale: sources.filter((s) => s.indexing_status === 'stale').map((s) => s.name),
    unindexed: sources.filter((s) => s.indexing_status === 'registered' || s.indexing_status === 'failed').map((s) => s.name),
    missing: sources.filter((s) => s.indexing_status === 'missing').map((s) => s.name),
    duplicates,
    brokenRefs,
    missingUiFiles,
    unapprovedDocs,
    outdatedDocs,
    openQuestions,
    conflicts,
    lastIndexedAt: get<{ t: string }>('SELECT MAX(last_indexed_at) AS t FROM brain_sources')?.t ?? null,
    ftsAvailable: FTS_AVAILABLE,
  };
}

/** Heuristic conflict detection — results are labelled as heuristics in the UI. */
export function detectConflicts() {
  const out: { title: string; detail: string; sources: string[] }[] = [];
  const docs = all<{ title: string; content: string; updated_at: string }>('SELECT title, content, updated_at FROM project_documents');
  const files = listFilesRecursive('docs', (r) => r.endsWith('.md')).map((r) => ({ title: r, content: readProjectFile(r) ?? '', updated_at: '' }));
  const corpus = [...docs, ...files];
  const nameVariants = new Map<string, string[]>();
  for (const d of corpus) {
    for (const m of d.content.matchAll(/blocky\s*(&|n|and|'n')\s*crycket/gi)) {
      const v = m[0].replace(/\s+/g, ' ');
      const key = v.toLowerCase().replace(/\s/g, '');
      nameVariants.set(key, Array.from(new Set([...(nameVariants.get(key) ?? []), d.title])));
    }
  }
  if (nameVariants.size > 1) {
    out.push({ title: 'Niespójna nazwa gry', detail: `Znaleziono warianty: ${[...nameVariants.keys()].join(', ')}`, sources: Array.from(new Set([...nameVariants.values()].flat())) });
  }
  const approvedByTitle = new Map<string, string[]>();
  for (const d of all<{ code: string; title: string; category: string }>("SELECT code, title, category FROM project_decisions WHERE status = 'approved'")) {
    const k = `${d.category}:${d.title.toLowerCase()}`;
    approvedByTitle.set(k, [...(approvedByTitle.get(k) ?? []), d.code]);
  }
  for (const [k, codes] of approvedByTitle) if (codes.length > 1) out.push({ title: 'Zduplikowane zatwierdzone decyzje', detail: k, sources: codes });
  return out;
}
