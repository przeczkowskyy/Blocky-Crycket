import { Link } from 'react-router-dom';
import { Brain, FileCode2, ListPlus, Gavel, HelpCircle, Bug, AlertTriangle } from 'lucide-react';
import { useApi, EXEC_STATUS, fmtDateTime, usd, num } from '../lib/api';
import { Badge, Modal, Spinner, StatusBadge, ErrorBox } from './ui';
import { Markdown } from './Markdown';

export function ExecutionModal({ id, onClose }: { id: string | null; onClose: () => void }) {
  const { data: e, error } = useApi<any>(id ? `/executions/${id}` : null, 2500);
  return (
    <Modal open={!!id} onClose={onClose} width="max-w-4xl" title={e ? <span className="flex items-center gap-2">{e.agent_name} · <span className="font-mono text-xs text-mute">{e.id}</span> <StatusBadge map={EXEC_STATUS} value={e.status} /></span> : 'Wykonanie'}>
      {error && <ErrorBox error={error} />}
      {!e ? <Spinner /> : <ExecutionBody e={e} />}
    </Modal>
  );
}

export function ExecutionBody({ e }: { e: any }) {
  const r = e.result ?? {};
  const p = r.processed ?? {};
  const snap = e.snapshot;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-5">
        <Meta label="Model" value={e.model ?? '—'} />
        <Meta label="Start" value={fmtDateTime(e.started_at)} />
        <Meta label="Czas" value={e.duration_ms ? `${(e.duration_ms / 1000).toFixed(1)} s` : e.status === 'running' ? 'w toku…' : '—'} />
        <Meta label="Tokeny (in/out)" value={`${num(e.input_tokens)} / ${num(e.output_tokens)}`} />
        <Meta label="Koszt" value={usd(e.cost_usd)} />
      </div>
      <div>
        <div className="mb-1 text-xs font-medium text-mute">Zlecenie</div>
        <div className="whitespace-pre-wrap rounded-md border border-line bg-panel2 p-3 text-[13px]">{e.prompt}</div>
      </div>
      {e.status === 'running' && <Spinner label="Agent pracuje… (odpowiedź pojawi się po zakończeniu)" />}
      {e.error && <ErrorBox error={e.error} />}
      {r.message && (
        <div>
          <div className="mb-1 text-xs font-medium text-mute">Odpowiedź agenta</div>
          <div className="rounded-md border border-line bg-panel2 p-3"><Markdown text={r.message} /></div>
        </div>
      )}
      {e.status === 'completed' && (
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge color="#f5c542"><FileCode2 size={12} /> {p.approvals ?? 0} do zatwierdzenia</Badge>
          <Badge color="#34d399"><FileCode2 size={12} /> {p.applied ?? 0} zastosowanych automatycznie</Badge>
          <Badge color="#60a5fa"><ListPlus size={12} /> {p.tasks ?? 0} nowych zadań</Badge>
          <Badge color="#a78bfa"><Gavel size={12} /> {p.decisions ?? 0} propozycji decyzji</Badge>
          <Badge color="#f05252"><Bug size={12} /> {p.bugs ?? 0} błędów</Badge>
          {(r.questions?.length ?? 0) > 0 && <Badge color="#fb923c"><HelpCircle size={12} /> {r.questions.length} pytań</Badge>}
        </div>
      )}
      {p.rejected?.length > 0 && <div className="rounded-md border border-amber/40 bg-amber/10 p-2 text-xs text-amber"><AlertTriangle size={12} className="inline mr-1" />Odrzucone ścieżki: {p.rejected.join('; ')}</div>}
      {r.assumptions?.length > 0 && <ListBlock title="Założenia agenta (nie są faktami)" items={r.assumptions} />}
      {e.approvals?.length > 0 && (
        <div className="text-xs"><span className="text-mute">Zatwierdzenia: </span>{e.approvals.map((a: any) => <Link key={a.id} to="/approvals" className="mr-2 text-cyan hover:underline">{a.title} ({a.status})</Link>)}</div>
      )}
      {snap && (
        <div className="rounded-md border border-line">
          <div className="flex items-center gap-2 border-b border-line px-3 py-2 text-xs font-medium"><Brain size={14} className="text-violet" /> Kontekst z Project Brain <span className="text-mute font-normal">— {snap.context_summary}</span></div>
          <div className="max-h-60 space-y-1.5 overflow-y-auto p-3">
            {(snap.retrieved_chunks ?? []).map((c: any) => (
              <div key={c.chunkId} className="rounded border border-line bg-panel2 p-2 text-xs">
                <div className="font-medium text-ink">{c.sourceName}{c.heading ? ` — ${c.heading}` : ''}</div>
                <div className="mt-0.5 line-clamp-2 text-mute">{c.preview}</div>
              </div>
            ))}
            {(snap.decisions ?? []).length > 0 && <div className="pt-1 text-[11px] text-mute">Zatwierdzone decyzje w kontekście: {snap.decisions.map((d: any) => d.code).join(', ')}</div>}
            <Link to={`/brain/context?execution=${e.id}`} className="block pt-1 text-[11px] text-cyan hover:underline">Pełny kontekst w Context Inspector →</Link>
          </div>
        </div>
      )}
    </div>
  );
}

const Meta = ({ label, value }: { label: string; value: string }) => (
  <div className="rounded-md border border-line bg-panel2 px-2.5 py-1.5"><div className="text-[10.5px] text-faint">{label}</div><div className="truncate font-medium">{value}</div></div>
);
const ListBlock = ({ title, items }: { title: string; items: string[] }) => (
  <div><div className="mb-1 text-xs font-medium text-mute">{title}</div><ul className="list-disc space-y-0.5 pl-5 text-[13px]">{items.map((x, i) => <li key={i}>{x}</li>)}</ul></div>
);
