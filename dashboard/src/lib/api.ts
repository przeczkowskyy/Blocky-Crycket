import { useCallback, useEffect, useRef, useState } from 'react';

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function api<T = any>(path: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: opts.method ?? (opts.body !== undefined ? 'POST' : 'GET'),
    headers: opts.body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  let data: any = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) throw new ApiError(data?.error ?? `HTTP ${res.status}`, res.status);
  return data as T;
}

/** Loads `path` (null = skip) and optionally re-polls every `intervalMs`. */
export function useApi<T = any>(path: string | null, intervalMs?: number) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(!!path);
  const pathRef = useRef(path);
  pathRef.current = path;

  const reload = useCallback(async () => {
    const p = pathRef.current;
    if (!p) return;
    try {
      const d = await api<T>(p);
      if (pathRef.current === p) { setData(d); setError(null); }
    } catch (e: any) {
      if (pathRef.current === p) setError(e.message);
    } finally {
      if (pathRef.current === p) setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!path) { setData(null); setLoading(false); return; }
    setLoading(true);
    void reload();
    if (!intervalMs) return;
    const t = setInterval(() => { if (document.visibilityState === 'visible') void reload(); }, intervalMs);
    return () => clearInterval(t);
  }, [path, intervalMs, reload]);

  return { data, error, loading, reload, setData };
}

export const AGENT_STATUS: Record<string, { label: string; color: string }> = {
  idle: { label: 'Idle', color: '#8a93a6' },
  thinking: { label: 'Thinking', color: '#a78bfa' },
  working: { label: 'Working', color: '#22d3ee' },
  waiting_approval: { label: 'Waiting for Approval', color: '#f5c542' },
  blocked: { label: 'Blocked', color: '#fb923c' },
  error: { label: 'Error', color: '#f05252' },
  offline: { label: 'Offline', color: '#5d6678' },
};

export const TASK_COLUMNS: { id: string; label: string; color: string }[] = [
  { id: 'backlog', label: 'Backlog', color: '#5d6678' },
  { id: 'planned', label: 'Planned', color: '#60a5fa' },
  { id: 'in_progress', label: 'In Progress', color: '#22d3ee' },
  { id: 'waiting_approval', label: 'Waiting for Approval', color: '#f5c542' },
  { id: 'testing', label: 'Testing', color: '#a78bfa' },
  { id: 'completed', label: 'Completed', color: '#34d399' },
  { id: 'blocked', label: 'Blocked', color: '#f05252' },
];

export const PRIORITY: Record<string, { label: string; color: string }> = {
  critical: { label: 'Krytyczny', color: '#f05252' },
  high: { label: 'Wysoki', color: '#fb923c' },
  medium: { label: 'Średni', color: '#f5c542' },
  low: { label: 'Niski', color: '#8a93a6' },
};

export const DECISION_STATUS: Record<string, { label: string; color: string }> = {
  proposed: { label: 'Proposed', color: '#8a93a6' },
  awaiting_approval: { label: 'Awaiting Approval', color: '#f5c542' },
  approved: { label: 'Approved', color: '#34d399' },
  rejected: { label: 'Rejected', color: '#f05252' },
  superseded: { label: 'Superseded', color: '#5d6678' },
};

export const UI_STATUS: Record<string, { label: string; color: string }> = {
  not_started: { label: 'Nie rozpoczęte', color: '#5d6678' },
  specified: { label: 'Wyspecyfikowane', color: '#8a93a6' },
  designed: { label: 'Zaprojektowane', color: '#60a5fa' },
  in_progress: { label: 'W trakcie', color: '#22d3ee' },
  implemented: { label: 'Zaimplementowane', color: '#a78bfa' },
  approved: { label: 'Zatwierdzone', color: '#34d399' },
};

export const STYLE_STATUS: Record<string, { label: string; color: string }> = {
  compliant: { label: 'Compliant', color: '#34d399' },
  needs_review: { label: 'Needs Review', color: '#f5c542' },
  inconsistent: { label: 'Inconsistent', color: '#f05252' },
  approved: { label: 'Approved', color: '#22d3ee' },
};

export const EXEC_STATUS: Record<string, { label: string; color: string }> = {
  running: { label: 'W toku', color: '#22d3ee' },
  completed: { label: 'Ukończone', color: '#34d399' },
  failed: { label: 'Błąd', color: '#f05252' },
  cancelled: { label: 'Przerwane', color: '#8a93a6' },
};

export function timeAgo(iso?: string | null) {
  if (!iso) return '—';
  const s = Math.round((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return `${s}s temu`;
  if (s < 3600) return `${Math.round(s / 60)} min temu`;
  if (s < 86400) return `${Math.round(s / 3600)} h temu`;
  return new Date(iso).toLocaleDateString('pl-PL');
}
export const fmtTime = (iso?: string | null) => (iso ? new Date(iso).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' }) : '—');
export const fmtDateTime = (iso?: string | null) => (iso ? new Date(iso).toLocaleString('pl-PL', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—');
export const usd = (n?: number | null) => `$${(n ?? 0).toFixed((n ?? 0) < 1 ? 4 : 2)}`;
export const num = (n?: number | null) => (n ?? 0).toLocaleString('pl-PL');
