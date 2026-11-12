import { useState } from 'react';
import { api, useApi } from '../lib/api';
import { Button, Field, Input, Modal, Select, Textarea, useAction, NotConfigured } from './ui';
import { useStatus } from './Layout';

export function AssignTaskModal({ agent, open, onClose, onStarted }: { agent: any; open: boolean; onClose: () => void; onStarted: (executionId: string) => void }) {
  const { data: tasks } = useApi<any[]>(open ? '/tasks' : null);
  const { status } = useStatus();
  const [prompt, setPrompt] = useState('');
  const [taskId, setTaskId] = useState('');
  const [files, setFiles] = useState('');
  const run = useAction(
    () => api<{ executionId: string }>(`/agents/${agent.id}/run`, { body: { prompt, taskId: taskId || null, relatedFiles: files.split(',').map((f) => f.trim()).filter(Boolean) } }),
    { success: `${agent?.name} rozpoczął pracę`, onDone: (r) => { setPrompt(''); setTaskId(''); setFiles(''); onStarted(r.executionId); } },
  );
  if (!agent) return null;
  return (
    <Modal open={open} onClose={onClose} title={`Zleć zadanie — ${agent.name}`}
      footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" loading={run.loading} disabled={!prompt.trim() || !status?.ai.configured || status?.emergencyStop} onClick={() => run.run()}>Uruchom agenta</Button></>}>
      <div className="space-y-3">
        {!status?.ai.configured && <div className="flex items-center gap-2 text-xs text-mute"><NotConfigured /> Dodaj klucz API, aby uruchamiać agentów.</div>}
        <Field label="Polecenie" hint="Agent otrzyma automatycznie kontekst z Project Brain (dokumentacja, decyzje, powiązane pliki).">
          <Textarea autoFocus className="min-h-[120px]" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={`Co ma zrobić ${agent.name}?`} />
        </Field>
        <Field label="Powiązane zadanie (opcjonalnie)">
          <Select value={taskId} onChange={(e) => setTaskId(e.target.value)}>
            <option value="">— brak —</option>
            {(tasks ?? []).filter((t) => t.status !== 'completed').map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}
          </Select>
        </Field>
        <Field label="Powiązane pliki (opcjonalnie, po przecinku)" hint="np. src/gui/MainHUD.model.json, src/client/HUDController.client.luau">
          <Input value={files} onChange={(e) => setFiles(e.target.value)} />
        </Field>
      </div>
    </Modal>
  );
}
