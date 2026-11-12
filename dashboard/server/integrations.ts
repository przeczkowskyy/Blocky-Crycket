import fs from 'node:fs';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { getSettings, insert, log, now, uid, update, get } from './db.ts';
import { DATA_DIR, PROJECT_ROOT } from './paths.ts';
import { aiConfigured } from './agents.ts';
import { health } from './brain.ts';

function sh(cmd: string, args: string[], timeoutMs = 60000): Promise<{ code: number; stdout: string; stderr: string; ms: number }> {
  const started = Date.now();
  return new Promise((resolve) => {
    execFile(cmd, args, { cwd: PROJECT_ROOT, timeout: timeoutMs, windowsHide: true, maxBuffer: 20 * 1024 * 1024 }, (err: any, stdout, stderr) => {
      resolve({ code: err ? (typeof err.code === 'number' ? err.code : 1) : 0, stdout: String(stdout ?? ''), stderr: String(stderr ?? '') + (err && err.code === 'ENOENT' ? `${cmd}: nie znaleziono w PATH` : ''), ms: Date.now() - started });
    });
  });
}

export async function rojoStatus() {
  const port = getSettings().rojoPort;
  try {
    const res = await fetch(`http://127.0.0.1:${port}/api/rojo`, { signal: AbortSignal.timeout(1500) });
    if (!res.ok) return { connected: false, port, error: `HTTP ${res.status}` };
    const j: any = await res.json();
    return { connected: true, port, serverVersion: j.serverVersion, protocolVersion: j.protocolVersion, projectName: j.projectName, sessionId: j.sessionId };
  } catch {
    return { connected: false, port, error: 'Rojo serve nie odpowiada' };
  }
}

export function studioStatus() {
  const places = fs.readdirSync(PROJECT_ROOT).filter((f) => f.toLowerCase().endsWith('.rbxl') || f.toLowerCase().endsWith('.rbxlx'));
  const locks = fs.readdirSync(PROJECT_ROOT).filter((f) => f.toLowerCase().endsWith('.rbxl.lock') || f.toLowerCase().endsWith('.rbxlx.lock'));
  return { placeFiles: places, open: locks.length > 0, method: 'Wykrywane po pliku .rbxl.lock (Studio tworzy go, gdy miejsce jest otwarte).' };
}

export async function gitStatus() {
  const r = await sh('git', ['rev-parse', '--abbrev-ref', 'HEAD'], 5000);
  if (r.code !== 0) return { configured: false, branch: null, detail: 'Folder projektu nie jest repozytorium Git.' };
  const st = await sh('git', ['status', '--porcelain'], 5000);
  const lastCommit = await sh('git', ['log', '-1', '--format=%h %s (%cr)'], 5000);
  return { configured: true, branch: r.stdout.trim(), changedFiles: st.stdout.split('\n').filter(Boolean).length, lastCommit: lastCommit.code === 0 ? lastCommit.stdout.trim() : null };
}

export async function toolVersion(cmd: string) {
  const r = await sh(cmd, ['--version'], 5000);
  return r.code === 0 ? r.stdout.trim() : null;
}

export async function integrations() {
  const [rojo, git, rojoCli, selene] = await Promise.all([rojoStatus(), gitStatus(), toolVersion('rojo'), toolVersion('selene')]);
  return {
    rojo: { ...rojo, cli: rojoCli },
    studio: studioStatus(),
    ai: { configured: aiConfigured(), provider: 'Anthropic Claude API', detail: aiConfigured() ? 'Klucz wykryty w środowisku serwera.' : 'NOT CONFIGURED — dodaj ANTHROPIC_API_KEY do dashboard/.env' },
    git,
    openCloud: { configured: !!process.env.ROBLOX_OPEN_CLOUD_API_KEY, detail: process.env.ROBLOX_OPEN_CLOUD_API_KEY ? 'Klucz wykryty (publikowanie nie jest jeszcze zaimplementowane).' : 'NOT CONFIGURED' },
    figma: { configured: false, detail: 'Figma jest podłączona w sesji Claude Code (MCP), nie w dashboardzie. Użyj skilla figma-to-roblox w Claude Code.' },
    selene: { installed: !!selene, version: selene },
  };
}

// ---------------- builds ----------------

export async function rojoBuild(trigger: string) {
  const out = path.join(DATA_DIR, 'builds');
  fs.mkdirSync(out, { recursive: true });
  const file = path.join(out, 'latest.rbxlx');
  const r = await sh('rojo', ['build', 'default.project.json', '-o', file], 120000);
  const id = uid('B-');
  const status = r.code === 0 ? 'success' : 'failed';
  insert('builds', { id, trigger, kind: 'rojo-build', status, duration_ms: r.ms, output: (r.stdout + '\n' + r.stderr).trim(), created_at: now() });
  log('Build', status === 'success' ? 'Build zakończony' : 'Build nieudany', `rojo build (${r.ms} ms)`, { type: 'build', id }, status === 'success' ? 'success' : 'error');
  return { id, status, ms: r.ms, output: (r.stdout + '\n' + r.stderr).trim() };
}

export async function rojoSourcemap() {
  const r = await sh('rojo', ['sourcemap', 'default.project.json'], 60000);
  if (r.code !== 0) throw new Error(r.stderr || 'rojo sourcemap nie powiódł się');
  return JSON.parse(r.stdout);
}

// ---------------- automated tests ----------------

export async function runTest(testId: string) {
  const t = get<any>('SELECT * FROM tests WHERE id = ?', testId);
  if (!t) throw new Error('Nie znaleziono testu');
  if (t.kind !== 'automated') throw new Error('To test manualny — ustaw wynik ręcznie.');
  let status: 'passed' | 'failed' | 'not_configured' = 'passed';
  let output = '';
  if (testId === 'test-rojo-build') {
    const b = await rojoBuild('test');
    status = b.status === 'success' ? 'passed' : 'failed';
    output = b.output;
  } else if (testId === 'test-sourcemap') {
    try { const sm = await rojoSourcemap(); output = `OK — korzeń: ${sm.name} (${sm.className}), dzieci: ${(sm.children ?? []).length}`; }
    catch (e: any) { status = 'failed'; output = e.message; }
  } else if (testId === 'test-brain') {
    const h = health();
    const problems = [...h.stale.map((s) => `nieaktualne: ${s}`), ...h.unindexed.map((s) => `niezaindeksowane: ${s}`), ...h.missing.map((s) => `brakujące: ${s}`), ...h.brokenRefs.map((b) => `zepsuta referencja: ${b.where} → ${b.ref}`)];
    status = problems.length ? 'failed' : 'passed';
    output = problems.length ? problems.join('\n') : `OK — ${h.indexed}/${h.total} źródeł zaindeksowanych.`;
  } else if (testId === 'test-lint') {
    const v = await toolVersion('selene');
    if (!v) { status = 'not_configured'; output = 'selene nie jest zainstalowany (https://github.com/Kampfkarren/selene).'; }
    else {
      const r = await sh('selene', ['src'], 60000);
      status = r.code === 0 ? 'passed' : 'failed';
      output = (r.stdout + r.stderr).trim();
    }
  } else {
    throw new Error('Nieznany test automatyczny');
  }
  update('tests', testId, { last_status: status, last_run_at: now(), last_output: output.slice(0, 20000) });
  log('SENTINEL (automat)', `Test: ${t.name}`, status, { type: 'test', id: testId }, status === 'passed' ? 'success' : status === 'failed' ? 'error' : 'warn');
  return { status, output };
}
