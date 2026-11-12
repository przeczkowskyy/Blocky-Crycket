import path from 'node:path';
import crypto from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { DATA_DIR } from './paths.ts';

export const db = new DatabaseSync(path.join(DATA_DIR, 'studio.db'));
db.exec('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 3000;');

const SCHEMA = `
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, current_phase TEXT,
  roadmap TEXT NOT NULL DEFAULT '[]', sprint TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL, description TEXT, instructions TEXT NOT NULL,
  model_provider TEXT NOT NULL DEFAULT 'anthropic', model TEXT NOT NULL, effort TEXT NOT NULL DEFAULT 'high',
  status TEXT NOT NULL DEFAULT 'idle', current_activity TEXT, permissions TEXT NOT NULL DEFAULT '{}',
  enabled INTEGER NOT NULL DEFAULT 1, color TEXT, icon TEXT, sort INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
  assigned_agent_id TEXT REFERENCES agents(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'backlog', priority TEXT NOT NULL DEFAULT 'medium', effort TEXT,
  dependencies TEXT NOT NULL DEFAULT '[]', related_files TEXT NOT NULL DEFAULT '[]', related_docs TEXT NOT NULL DEFAULT '[]',
  brain_source_ids TEXT NOT NULL DEFAULT '[]', sprint INTEGER NOT NULL DEFAULT 0, phase TEXT, parent_id TEXT,
  created_by TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(assigned_agent_id);

CREATE TABLE IF NOT EXISTS task_comments (
  id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_executions (
  id TEXT PRIMARY KEY, agent_id TEXT NOT NULL REFERENCES agents(id), task_id TEXT, workflow_run_id TEXT, chat_message_id TEXT,
  prompt TEXT NOT NULL, status TEXT NOT NULL, model TEXT, started_at TEXT NOT NULL, finished_at TEXT,
  result TEXT, error TEXT, input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
  cache_read_tokens INTEGER NOT NULL DEFAULT 0, cost_usd REAL NOT NULL DEFAULT 0, duration_ms INTEGER
);
CREATE INDEX IF NOT EXISTS idx_exec_agent ON agent_executions(agent_id);

CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY, task_id TEXT, agent_id TEXT, execution_id TEXT, workflow_run_id TEXT,
  change_type TEXT NOT NULL, title TEXT NOT NULL, explanation TEXT, proposed_changes TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'pending', review_comment TEXT, conflict INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, reviewed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, subcategory TEXT, kind TEXT NOT NULL DEFAULT '2d',
  source_path TEXT, preview_path TEXT, prompt TEXT, style_compliance TEXT NOT NULL DEFAULT 'needs_review',
  style_checklist TEXT NOT NULL DEFAULT '{}', style_report TEXT, status TEXT NOT NULL DEFAULT 'planned',
  agent_id TEXT, feature TEXT, version INTEGER NOT NULL DEFAULT 1, brain_source_ids TEXT NOT NULL DEFAULT '[]',
  notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT NOT NULL, action TEXT NOT NULL, details TEXT,
  entity_type TEXT, entity_id TEXT, level TEXT NOT NULL DEFAULT 'info', timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_logs_entity ON activity_logs(entity_type, entity_id);

CREATE TABLE IF NOT EXISTS project_documents (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, content TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1, approved INTEGER NOT NULL DEFAULT 0, author TEXT NOT NULL DEFAULT 'user',
  source TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS document_versions (
  id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES project_documents(id) ON DELETE CASCADE,
  version INTEGER NOT NULL, content TEXT NOT NULL, approved INTEGER NOT NULL, author TEXT NOT NULL, note TEXT, created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS brain_sources (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, source_type TEXT NOT NULL, origin TEXT NOT NULL UNIQUE,
  content_hash TEXT, version INTEGER NOT NULL DEFAULT 0, indexing_status TEXT NOT NULL DEFAULT 'registered',
  authoritative INTEGER NOT NULL DEFAULT 0, categories TEXT NOT NULL DEFAULT '[]', access TEXT NOT NULL DEFAULT 'all-agents',
  archived INTEGER NOT NULL DEFAULT 0, content TEXT, error TEXT, chunk_count INTEGER NOT NULL DEFAULT 0,
  last_indexed_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS brain_chunks (
  id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES brain_sources(id) ON DELETE CASCADE,
  ord INTEGER NOT NULL, heading TEXT, content TEXT NOT NULL, metadata TEXT NOT NULL DEFAULT '{}', embedding_reference TEXT
);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON brain_chunks(source_id);

CREATE TABLE IF NOT EXISTS project_decisions (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, title TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'proposed', proposed_by TEXT NOT NULL, approved_by TEXT,
  related_docs TEXT NOT NULL DEFAULT '[]', related_tasks TEXT NOT NULL DEFAULT '[]', supersedes_decision_id TEXT,
  created_at TEXT NOT NULL, approved_at TEXT, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS brain_updates (
  id TEXT PRIMARY KEY, agent_execution_id TEXT, agent_id TEXT, proposed_changes TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', reviewed_by TEXT, review_note TEXT, created_at TEXT NOT NULL, reviewed_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_context_snapshots (
  id TEXT PRIMARY KEY, agent_execution_id TEXT NOT NULL, retrieved_source_ids TEXT NOT NULL DEFAULT '[]',
  retrieved_chunks TEXT NOT NULL DEFAULT '[]', decisions TEXT NOT NULL DEFAULT '[]', query TEXT,
  context_summary TEXT, context_text TEXT, created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY, question TEXT NOT NULL, context TEXT, raised_by TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open',
  answer TEXT, created_at TEXT NOT NULL, answered_at TEXT
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id TEXT PRIMARY KEY, author_type TEXT NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL,
  mentions TEXT NOT NULL DEFAULT '[]', execution_id TEXT, task_id TEXT, meta TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflows (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, nodes TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workflow_runs (
  id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL REFERENCES workflows(id), input TEXT NOT NULL, task_id TEXT,
  status TEXT NOT NULL, current_step INTEGER NOT NULL DEFAULT 0, step_results TEXT NOT NULL DEFAULT '[]',
  error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ui_elements (
  id TEXT PRIMARY KEY, screen TEXT NOT NULL, section TEXT, name TEXT NOT NULL, spec TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'specified', assigned_agent_id TEXT, files TEXT NOT NULL DEFAULT '[]',
  dependencies TEXT NOT NULL DEFAULT '[]', approval_status TEXT NOT NULL DEFAULT 'not_submitted', roblox_path TEXT,
  sort INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bugs (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', severity TEXT NOT NULL DEFAULT 'medium',
  category TEXT NOT NULL DEFAULT 'luau', assigned_agent_id TEXT, related_files TEXT NOT NULL DEFAULT '[]',
  repro_steps TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'open', test_result TEXT, reported_by TEXT NOT NULL DEFAULT 'user',
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tests (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL, category TEXT NOT NULL, description TEXT,
  last_status TEXT NOT NULL DEFAULT 'not_run', last_run_at TEXT, last_output TEXT, regression INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS builds (
  id TEXT PRIMARY KEY, trigger TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, duration_ms INTEGER,
  output TEXT, created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS file_versions (
  id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT, author TEXT NOT NULL, approval_id TEXT, note TEXT, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fv_path ON file_versions(path);

CREATE TABLE IF NOT EXISTS file_locks (
  path TEXT PRIMARY KEY, owner_agent_id TEXT NOT NULL, execution_id TEXT, locked_at TEXT NOT NULL
);
`;
db.exec(SCHEMA);

export let FTS_AVAILABLE = true;
try {
  db.exec(`CREATE VIRTUAL TABLE IF NOT EXISTS brain_fts USING fts5(content, heading, chunk_id UNINDEXED, source_id UNINDEXED, tokenize = 'unicode61 remove_diacritics 2');`);
} catch {
  FTS_AVAILABLE = false;
}

// ---------- helpers ----------

const JSON_COLS = new Set([
  'roadmap', 'sprint', 'permissions', 'dependencies', 'related_files', 'related_docs', 'brain_source_ids',
  'result', 'proposed_changes', 'style_checklist', 'categories', 'metadata', 'retrieved_source_ids',
  'retrieved_chunks', 'decisions', 'mentions', 'meta', 'nodes', 'step_results', 'files', 'related_tasks', 'value',
]);
const BOOL_COLS = new Set(['enabled', 'approved', 'authoritative', 'archived', 'sprint_flag', 'conflict', 'regression']);

export type Row = Record<string, any>;

export function parseRow<T = Row>(r: any): T {
  if (!r) return r;
  const o: Row = { ...r };
  for (const k of Object.keys(o)) {
    if (JSON_COLS.has(k) && typeof o[k] === 'string') {
      try { o[k] = JSON.parse(o[k]); } catch { /* keep string */ }
    } else if (BOOL_COLS.has(k)) {
      o[k] = !!o[k];
    }
  }
  if ('sprint' in o && typeof o.sprint === 'number') o.sprint = !!o.sprint;
  return o as T;
}

function toDb(v: unknown): any {
  if (v === undefined) return null;
  if (typeof v === 'boolean') return v ? 1 : 0;
  if (v !== null && typeof v === 'object') return JSON.stringify(v);
  return v;
}

export function all<T = Row>(sql: string, ...params: any[]): T[] {
  return db.prepare(sql).all(...params.map(toDb)).map((r) => parseRow<T>(r));
}
export function get<T = Row>(sql: string, ...params: any[]): T | undefined {
  const r = db.prepare(sql).get(...params.map(toDb));
  return r ? parseRow<T>(r) : undefined;
}
export function run(sql: string, ...params: any[]) {
  return db.prepare(sql).run(...params.map(toDb));
}

export function insert(table: string, obj: Row) {
  const keys = Object.keys(obj).filter((k) => obj[k] !== undefined);
  const sql = `INSERT INTO ${table} (${keys.join(',')}) VALUES (${keys.map(() => '?').join(',')})`;
  db.prepare(sql).run(...keys.map((k) => toDb(obj[k])));
  return obj;
}

export function update(table: string, id: string, patch: Row, idCol = 'id') {
  const keys = Object.keys(patch).filter((k) => patch[k] !== undefined && k !== idCol);
  if (!keys.length) return;
  const sql = `UPDATE ${table} SET ${keys.map((k) => `${k} = ?`).join(', ')} WHERE ${idCol} = ?`;
  db.prepare(sql).run(...keys.map((k) => toDb(patch[k])), id);
}

export function tx<T>(fn: () => T): T {
  db.exec('BEGIN');
  try {
    const r = fn();
    db.exec('COMMIT');
    return r;
  } catch (e) {
    db.exec('ROLLBACK');
    throw e;
  }
}

export const now = () => new Date().toISOString();
export const uid = (prefix = '') => prefix + crypto.randomUUID().replace(/-/g, '').slice(0, 12);
export const sha256 = (s: string) => crypto.createHash('sha256').update(s).digest('hex');

// ---------- settings ----------

export interface StudioSettings {
  autonomyMode: 'assistant' | 'semi' | 'autonomous';
  emergencyStop: boolean;
  maxIterations: number;
  costLimitUsd: number;
  timeLimitSec: number;
  protectedFiles: string[];
  rojoPort: number;
  defaultModel: string;
  maxContextChunks: number;
}

export const DEFAULT_SETTINGS: StudioSettings = {
  autonomyMode: 'assistant',
  emergencyStop: false,
  maxIterations: 8,
  costLimitUsd: 10,
  timeLimitSec: 600,
  protectedFiles: ['default.project.json', 'docs/**', '*.rbxl'],
  rojoPort: 34872,
  defaultModel: 'claude-opus-5-5',
  maxContextChunks: 8,
};

export function getSettings(): StudioSettings {
  const rows = all<{ key: string; value: any }>('SELECT key, value FROM settings');
  const s: any = { ...DEFAULT_SETTINGS };
  for (const r of rows) s[r.key] = r.value;
  return s;
}

export function setSettings(patch: Partial<StudioSettings>) {
  for (const [k, v] of Object.entries(patch)) {
    if (!(k in DEFAULT_SETTINGS)) continue;
    run('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value', k, JSON.stringify(v));
  }
  return getSettings();
}

// ---------- activity log ----------

export function log(actor: string, action: string, details = '', entity?: { type: string; id: string }, level: 'info' | 'warn' | 'error' | 'success' = 'info') {
  run(
    'INSERT INTO activity_logs (actor, action, details, entity_type, entity_id, level, timestamp) VALUES (?,?,?,?,?,?,?)',
    actor, action, details, entity?.type ?? null, entity?.id ?? null, level, now(),
  );
}
