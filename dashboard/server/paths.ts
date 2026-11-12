import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

/** dashboard/ */
export const DASHBOARD_ROOT = path.resolve(here, '..');
/** Roblox project root (the folder containing default.project.json and the .rbxl) */
export const PROJECT_ROOT = path.resolve(DASHBOARD_ROOT, '..');
export const DATA_DIR = path.join(DASHBOARD_ROOT, 'data');
fs.mkdirSync(DATA_DIR, { recursive: true });

/**
 * Obsidian vault = a top-level folder of the project that contains `.obsidian/`.
 * Detected at startup (the user's vault is "B&C").
 */
function detectVault(): string | null {
  try {
    for (const name of fs.readdirSync(PROJECT_ROOT)) {
      const p = path.join(PROJECT_ROOT, name);
      if (fs.statSync(p).isDirectory() && fs.existsSync(path.join(p, '.obsidian'))) return name;
    }
  } catch { /* ignore */ }
  return null;
}
export const VAULT_DIR: string | null = detectVault();
/** Folder inside the vault that the studio regenerates (read-only mirror of the dashboard). */
export const VAULT_MIRROR = 'Studio';

/** Top-level folders agents / approvals may write into. */
export const WRITABLE_ROOTS = ['src', 'docs', 'assets', ...(VAULT_DIR ? [VAULT_DIR] : [])];
/** Additional single files that may be written (always through approval — they are protected by default). */
export const WRITABLE_FILES = ['default.project.json'];
/** What the workspace explorer shows. */
export const BROWSABLE_ROOTS = ['src', 'docs', 'assets', ...(VAULT_DIR ? [VAULT_DIR] : []), '.claude/skills', 'default.project.json'];

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const NEVER_WRITE = [
  /\.rbxl$/i, /\.rbxlx$/i, /\.rbxl\.lock$/i, /\.rbxm$/i, /(^|\/)\.env/i,
  /(^|\/)\.obsidian(\/|$)/i, /(^|\/)\.trash(\/|$)/i,
  ...(VAULT_DIR ? [new RegExp(`^${esc(VAULT_DIR)}/${VAULT_MIRROR}(/|$)`)] : []),
];

/** True for notes the user writes in the vault (excludes the generated mirror and Obsidian internals). */
export function isUserVaultNote(rel: string) {
  if (!VAULT_DIR || !rel.startsWith(VAULT_DIR + '/') || !rel.toLowerCase().endsWith('.md')) return false;
  const inner = rel.slice(VAULT_DIR.length + 1);
  return !inner.startsWith(VAULT_MIRROR + '/') && !inner.startsWith('.obsidian/') && !inner.startsWith('.trash/');
}

export function toPosix(p: string) {
  return p.split(path.sep).join('/');
}

/** Resolve a project-relative path, refusing anything that escapes the project root. */
export function resolveProjectPath(rel: string): string {
  if (typeof rel !== 'string' || !rel.trim()) throw new Error('Pusta ścieżka');
  const cleaned = rel.replace(/\\/g, '/').replace(/^\/+/, '');
  if (cleaned.split('/').some((seg) => seg === '..')) throw new Error(`Niedozwolona ścieżka: ${rel}`);
  const abs = path.resolve(PROJECT_ROOT, cleaned);
  if (abs !== PROJECT_ROOT && !abs.startsWith(PROJECT_ROOT + path.sep)) throw new Error(`Ścieżka poza projektem: ${rel}`);
  if (abs.startsWith(DASHBOARD_ROOT + path.sep) || abs === DASHBOARD_ROOT) throw new Error('Dashboard nie modyfikuje własnych plików');
  return abs;
}

export function relFromAbs(abs: string) {
  return toPosix(path.relative(PROJECT_ROOT, abs));
}

export function normalizeRel(rel: string) {
  return relFromAbs(resolveProjectPath(rel));
}

export function isWritablePath(rel: string): boolean {
  const n = normalizeRel(rel);
  if (NEVER_WRITE.some((r) => r.test(n))) return false;
  if (WRITABLE_FILES.includes(n)) return true;
  const top = n.split('/')[0];
  return WRITABLE_ROOTS.includes(top);
}

export function isProtectedPath(rel: string, protectedPatterns: string[]): boolean {
  const n = normalizeRel(rel);
  return protectedPatterns.some((pat) => {
    if (pat.endsWith('/**')) return n.startsWith(pat.slice(0, -3) + '/') || n === pat.slice(0, -3);
    if (pat.startsWith('*.')) return n.toLowerCase().endsWith(pat.slice(1).toLowerCase());
    return n === pat;
  });
}

export function readProjectFile(rel: string): string | null {
  const abs = resolveProjectPath(rel);
  if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) return null;
  return fs.readFileSync(abs, 'utf8');
}

export function languageFor(rel: string): string {
  const ext = path.extname(rel).toLowerCase();
  if (ext === '.luau' || ext === '.lua') return 'lua';
  if (ext === '.json') return 'json';
  if (ext === '.md') return 'markdown';
  if (ext === '.ts' || ext === '.tsx') return 'typescript';
  return 'plaintext';
}

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size?: number;
  modifiedAt?: string;
  children?: FileNode[];
}

const IMAGE_EXT = /\.(png|jpe?g|gif|webp|svg)$/i;

export function walkProject(): FileNode[] {
  const out: FileNode[] = [];
  for (const root of BROWSABLE_ROOTS) {
    const abs = path.join(PROJECT_ROOT, root);
    if (!fs.existsSync(abs)) continue;
    out.push(walk(abs));
  }
  return out;
}

function walk(abs: string): FileNode {
  const st = fs.statSync(abs);
  const rel = relFromAbs(abs);
  if (st.isFile()) {
    return { name: path.basename(abs), path: rel, type: 'file', size: st.size, modifiedAt: st.mtime.toISOString() };
  }
  const children = fs
    .readdirSync(abs)
    .filter((n) => !n.startsWith('.') || n === '.claude')
    .map((n) => walk(path.join(abs, n)))
    .sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name) : a.type === 'dir' ? -1 : 1));
  return { name: rel, path: rel, type: 'dir', children };
}

export function listFilesRecursive(relRoot: string, filter: (rel: string) => boolean): string[] {
  const abs = path.join(PROJECT_ROOT, relRoot);
  if (!fs.existsSync(abs)) return [];
  const st = fs.statSync(abs);
  if (st.isFile()) return filter(relRoot) ? [relRoot] : [];
  const out: string[] = [];
  const stack = [abs];
  while (stack.length) {
    const cur = stack.pop()!;
    for (const name of fs.readdirSync(cur)) {
      const p = path.join(cur, name);
      const s = fs.statSync(p);
      if (s.isDirectory()) stack.push(p);
      else {
        const rel = relFromAbs(p);
        if (filter(rel)) out.push(rel);
      }
    }
  }
  return out.sort();
}

export function isImage(rel: string) {
  return IMAGE_EXT.test(rel);
}
