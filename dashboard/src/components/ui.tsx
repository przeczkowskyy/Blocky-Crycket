import { createContext, useCallback, useContext, useEffect, useState, type ReactNode, type ButtonHTMLAttributes, type InputHTMLAttributes, type TextareaHTMLAttributes, type SelectHTMLAttributes } from 'react';
import { Loader2, X, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export const cx = (...c: (string | false | null | undefined)[]) => c.filter(Boolean).join(' ');

// ---------------- toast ----------------

type Toast = { id: number; kind: 'success' | 'error' | 'info'; text: string };
const ToastCtx = createContext<(kind: Toast['kind'], text: string) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = useCallback((kind: Toast['kind'], text: string) => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, kind, text }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), kind === 'error' ? 7000 : 3500);
  }, []);
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
        {toasts.map((t) => (
          <div key={t.id} className={cx('flex items-start gap-2 rounded-lg border px-3 py-2.5 shadow-xl text-[13px] bg-panel2',
            t.kind === 'success' && 'border-mint/40', t.kind === 'error' && 'border-ruby/50', t.kind === 'info' && 'border-sky/40')}>
            {t.kind === 'success' ? <CheckCircle2 size={16} className="text-mint shrink-0 mt-0.5" /> : t.kind === 'error' ? <AlertTriangle size={16} className="text-ruby shrink-0 mt-0.5" /> : <Info size={16} className="text-sky shrink-0 mt-0.5" />}
            <span className="whitespace-pre-wrap">{t.text}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

/** Wraps an async action with loading state + toast on success/error. */
export function useAction<A extends any[], R>(fn: (...args: A) => Promise<R>, opts: { success?: string | ((r: R) => string); onDone?: (r: R) => void } = {}) {
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const run = async (...args: A): Promise<R | undefined> => {
    setLoading(true);
    try {
      const r = await fn(...args);
      if (opts.success) toast('success', typeof opts.success === 'function' ? opts.success(r) : opts.success);
      opts.onDone?.(r);
      return r;
    } catch (e: any) {
      toast('error', e.message ?? String(e));
      return undefined;
    } finally {
      setLoading(false);
    }
  };
  return { run, loading };
}

// ---------------- primitives ----------------

type BtnVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
export function Button({ variant = 'secondary', loading, icon, children, className, size = 'md', ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: BtnVariant; loading?: boolean; icon?: ReactNode; size?: 'sm' | 'md' }) {
  return (
    <button
      {...rest}
      disabled={rest.disabled || loading}
      className={cx(
        'inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap cursor-pointer',
        size === 'sm' ? 'h-7 px-2.5 text-xs' : 'h-8 px-3 text-[13px]',
        variant === 'primary' && 'bg-gold text-black hover:bg-[#ffd55e]',
        variant === 'secondary' && 'bg-panel3 border border-line2 hover:bg-[#262d3b] text-ink',
        variant === 'ghost' && 'hover:bg-panel3 text-mute hover:text-ink',
        variant === 'danger' && 'bg-ruby/15 text-ruby border border-ruby/40 hover:bg-ruby/25',
        variant === 'success' && 'bg-mint/15 text-mint border border-mint/40 hover:bg-mint/25',
        className,
      )}
    >
      {loading ? <Loader2 size={14} className="animate-spin" /> : icon}
      {children}
    </button>
  );
}

export function Card({ title, actions, children, className, bodyClass, icon }: { title?: ReactNode; actions?: ReactNode; children: ReactNode; className?: string; bodyClass?: string; icon?: ReactNode }) {
  return (
    <section className={cx('rounded-lg border border-line bg-panel', className)}>
      {(title || actions) && (
        <header className="flex items-center justify-between gap-2 border-b border-line px-4 py-2.5">
          <h3 className="flex items-center gap-2 text-[13px] font-semibold text-ink">{icon}{title}</h3>
          <div className="flex items-center gap-1.5">{actions}</div>
        </header>
      )}
      <div className={cx('p-4', bodyClass)}>{children}</div>
    </section>
  );
}

export function Badge({ color = '#8a93a6', children, className, dot }: { color?: string; children: ReactNode; className?: string; dot?: boolean }) {
  return (
    <span className={cx('inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] font-medium whitespace-nowrap', className)} style={{ color, background: `${color}1f`, border: `1px solid ${color}40` }}>
      {dot && <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />}
      {children}
    </span>
  );
}

export function StatusBadge({ map, value }: { map: Record<string, { label: string; color: string }>; value: string }) {
  const s = map[value] ?? { label: value, color: '#8a93a6' };
  return <Badge color={s.color} dot>{s.label}</Badge>;
}

export function PageHeader({ title, subtitle, actions, icon }: { title: ReactNode; subtitle?: ReactNode; actions?: ReactNode; icon?: ReactNode }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="flex items-center gap-2 text-xl font-semibold tracking-tight">{icon}{title}</h1>
        {subtitle && <p className="mt-1 text-[13px] text-mute max-w-3xl">{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Empty({ icon, title, children }: { icon?: ReactNode; title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center text-mute">
      {icon && <div className="text-faint">{icon}</div>}
      <div className="text-[13px] font-medium text-ink/80">{title}</div>
      {children && <div className="text-xs max-w-md">{children}</div>}
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return <div className="flex items-center gap-2 py-8 justify-center text-mute text-xs"><Loader2 size={16} className="animate-spin" />{label ?? 'Ładowanie…'}</div>;
}

export function ErrorBox({ error }: { error: string }) {
  return <div className="rounded-md border border-ruby/40 bg-ruby/10 px-3 py-2 text-[13px] text-ruby">{error}</div>;
}

const fieldCls = 'w-full rounded-md border border-line2 bg-panel2 px-2.5 py-1.5 text-[13px] text-ink placeholder:text-faint focus:outline-none focus:border-gold/60 focus:ring-1 focus:ring-gold/30';
export const Input = (p: InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={cx(fieldCls, 'h-8', p.className)} />;
export const Textarea = (p: TextareaHTMLAttributes<HTMLTextAreaElement>) => <textarea {...p} className={cx(fieldCls, 'min-h-[80px] font-[inherit]', p.className)} />;
export const Select = ({ children, ...p }: SelectHTMLAttributes<HTMLSelectElement>) => <select {...p} className={cx(fieldCls, 'h-8 pr-6', p.className)}>{children}</select>;

export function Field({ label, hint, children, error }: { label: string; hint?: string; children: ReactNode; error?: string | null }) {
  return (
    <label className="block space-y-1">
      <span className="text-xs font-medium text-mute">{label}</span>
      {children}
      {error ? <span className="block text-[11px] text-ruby">{error}</span> : hint ? <span className="block text-[11px] text-faint">{hint}</span> : null}
    </label>
  );
}

export function Modal({ open, onClose, title, children, width = 'max-w-2xl', footer }: { open: boolean; onClose: () => void; title: ReactNode; children: ReactNode; width?: string; footer?: ReactNode }) {
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/60 p-4 pt-[6vh]" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className={cx('w-full rounded-xl border border-line2 bg-panel shadow-2xl', width)}>
        <header className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm font-semibold">{title}</h2>
          <button onClick={onClose} className="rounded p-1 text-mute hover:bg-panel3 hover:text-ink cursor-pointer"><X size={16} /></button>
        </header>
        <div className="max-h-[75vh] overflow-y-auto p-4">{children}</div>
        {footer && <footer className="flex justify-end gap-2 border-t border-line px-4 py-3">{footer}</footer>}
      </div>
    </div>
  );
}

export function Tabs<T extends string>({ tabs, value, onChange, className }: { tabs: { id: T; label: ReactNode; count?: number }[]; value: T; onChange: (v: T) => void; className?: string }) {
  return (
    <div className={cx('flex gap-1 border-b border-line overflow-x-auto', className)}>
      {tabs.map((t) => (
        <button key={t.id} onClick={() => onChange(t.id)}
          className={cx('relative -mb-px flex items-center gap-1.5 whitespace-nowrap border-b-2 px-3 py-2 text-[13px] cursor-pointer', value === t.id ? 'border-gold text-ink' : 'border-transparent text-mute hover:text-ink')}>
          {t.label}
          {t.count !== undefined && <span className="rounded bg-panel3 px-1.5 text-[10px] text-mute">{t.count}</span>}
        </button>
      ))}
    </div>
  );
}

export function Stat({ label, value, icon, color = '#f5c542', hint, onClick }: { label: string; value: ReactNode; icon: ReactNode; color?: string; hint?: string; onClick?: () => void }) {
  return (
    <button onClick={onClick} disabled={!onClick} className="group flex items-center gap-3 rounded-lg border border-line bg-panel p-3.5 text-left transition-colors enabled:hover:border-line2 enabled:cursor-pointer">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md" style={{ background: `${color}1a`, color }}>{icon}</div>
      <div className="min-w-0">
        <div className="text-xl font-semibold leading-none tabular-nums">{value}</div>
        <div className="mt-1 truncate text-[11.5px] text-mute">{label}</div>
        {hint && <div className="text-[10.5px] text-faint">{hint}</div>}
      </div>
    </button>
  );
}

export function Progress({ value, max = 100, color = '#f5c542', className }: { value: number; max?: number; color?: string; className?: string }) {
  const pct = max ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return <div className={cx('h-1.5 w-full overflow-hidden rounded-full bg-panel3', className)}><div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color }} /></div>;
}

export function Confirm({ open, title, text, onConfirm, onClose, danger, loading }: { open: boolean; title: string; text: ReactNode; onConfirm: () => void; onClose: () => void; danger?: boolean; loading?: boolean }) {
  return (
    <Modal open={open} onClose={onClose} title={title} width="max-w-md"
      footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant={danger ? 'danger' : 'primary'} loading={loading} onClick={onConfirm}>Potwierdź</Button></>}>
      <div className="text-[13px] text-mute">{text}</div>
    </Modal>
  );
}

export function Kbd({ children }: { children: ReactNode }) {
  return <code className="rounded border border-line2 bg-panel3 px-1.5 py-0.5 font-mono text-[11.5px] text-ink">{children}</code>;
}

export function DemoTag({ children = 'DEMO' }: { children?: ReactNode }) {
  return <Badge color="#fb923c">{children}</Badge>;
}

export function NotConfigured({ what = 'AI' }: { what?: string }) {
  return <Badge color="#f05252">{what}: NOT CONFIGURED</Badge>;
}
