import { useEffect, useRef, useState } from 'react';
import { Settings, Download, Upload, Save, ShieldAlert, Plus, X } from 'lucide-react';
import { api, useApi } from '../lib/api';
import { Badge, Button, Card, Confirm, ErrorBox, Field, Input, PageHeader, Spinner, useAction } from '../components/ui';

export function SettingsPage() {
  const { data, error, reload } = useApi<any>('/settings');
  const [prot, setProt] = useState<string[]>([]);
  const [port, setPort] = useState(34872);
  const [newPat, setNewPat] = useState('');
  const [importData, setImportData] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  useEffect(() => { if (data) { setProt(data.settings.protectedFiles); setPort(data.settings.rojoPort); } }, [data]);
  const save = useAction(() => api('/settings', { method: 'PATCH', body: { protectedFiles: prot, rojoPort: Number(port) } }), { success: 'Zapisano ustawienia', onDone: reload });
  const doImport = useAction(() => api('/import', { body: importData }), { success: 'Zaimportowano stan projektu', onDone: () => { setImportData(null); window.location.reload(); } });
  if (error) return <ErrorBox error={error} />;
  if (!data) return <Spinner />;
  const dirty = JSON.stringify(prot) !== JSON.stringify(data.settings.protectedFiles) || Number(port) !== data.settings.rojoPort;

  return (
    <div>
      <PageHeader icon={<Settings size={20} className="text-gold" />} title="Settings" actions={<Button variant="primary" icon={<Save size={14} />} disabled={!dirty} loading={save.loading} onClick={() => save.run()}>Zapisz</Button>} />
      <div className="grid gap-5 lg:grid-cols-2">
        <Card title="Pliki chronione" icon={<ShieldAlert size={14} className="text-amber" />}>
          <p className="mb-3 text-[12px] text-mute">Zmiany w tych ścieżkach zawsze wymagają Twojego zatwierdzenia, w każdym trybie autonomii. Wzorce: dokładna ścieżka, <code>folder/**</code>, <code>*.rozszerzenie</code>. Pliki .rbxl nigdy nie są zapisywane.</p>
          <div className="mb-3 flex flex-wrap gap-1.5">{prot.map((p) => <button key={p} onClick={() => setProt(prot.filter((x) => x !== p))} className="cursor-pointer"><Badge color="#fb923c">{p} <X size={10} /></Badge></button>)}</div>
          <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (newPat.trim() && !prot.includes(newPat.trim())) setProt([...prot, newPat.trim()]); setNewPat(''); }}>
            <Input value={newPat} onChange={(e) => setNewPat(e.target.value)} placeholder="np. src/server/** lub src/shared/Config.luau" />
            <Button type="submit" icon={<Plus size={13} />}>Dodaj</Button>
          </form>
        </Card>
        <Card title="Rojo">
          <Field label="Port rojo serve" hint="Domyślnie 34872. Używany do sprawdzania statusu synchronizacji."><Input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} /></Field>
        </Card>
        <Card title="Eksport / import stanu projektu">
          <p className="mb-3 text-[12px] text-mute">Eksport zawiera zadania, decyzje, dokumentację, zatwierdzenia, historię agentów, assety (metadane) i logi. Nie zawiera kluczy API ani plików z dysku.</p>
          <div className="flex gap-2">
            <a href="/api/export"><Button icon={<Download size={14} />}>Eksportuj .json</Button></a>
            <Button icon={<Upload size={14} />} onClick={() => fileRef.current?.click()}>Importuj .json</Button>
            <input ref={fileRef} type="file" accept=".json,application/json" className="hidden" onChange={async (e) => { const f = e.target.files?.[0]; if (!f) return; try { setImportData(JSON.parse(await f.text())); } catch { alert('Nieprawidłowy plik JSON'); } e.target.value = ''; }} />
          </div>
        </Card>
        <Card title="Bezpieczeństwo">
          <ul className="space-y-1.5 text-[12.5px] text-mute">
            <li>• Serwer studia nasłuchuje wyłącznie na 127.0.0.1.</li>
            <li>• Klucz API czytany jest tylko przez serwer z <code>dashboard/.env</code>.</li>
            <li>• Agenci mogą pisać tylko w <code>src/</code>, <code>docs/</code>, <code>assets/</code> (i chroniony <code>default.project.json</code>).</li>
            <li>• Każdy zapis tworzy kopię w historii wersji (rollback w Workspace).</li>
            <li>• Emergency Stop przerywa trwające wykonania i blokuje nowe.</li>
          </ul>
        </Card>
      </div>
      <Confirm open={!!importData} onClose={() => setImportData(null)} danger loading={doImport.loading} title="Zastąpić stan projektu?"
        text={<>Import z <b>{importData?.exportedAt}</b> zastąpi wszystkie dane studia (zadania, decyzje, dokumentację, historię). Pliki na dysku nie są zmieniane.</>} onConfirm={() => doImport.run()} />
    </div>
  );
}
