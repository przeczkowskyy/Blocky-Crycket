import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, Play, FileCheck2, FileX2, Plus } from 'lucide-react';
import { api, useApi, UI_STATUS } from '../lib/api';
import { Badge, Button, Card, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, Tabs, Textarea, useAction, cx, NotConfigured } from '../components/ui';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

const SCREENS = ['Main HUD', 'Loading Screen', 'Tavern Interface', 'Pet Interface', 'Inventory', 'Character Interface', 'Shop', 'Tycoon Interface', 'Quest Interface', 'Settings'];
const APPROVAL: Record<string, { label: string; color: string }> = { not_submitted: { label: 'Nie zgłoszone', color: '#5d6678' }, pending: { label: 'Do przeglądu', color: '#f5c542' }, approved: { label: 'Zatwierdzone', color: '#34d399' }, rejected: { label: 'Odrzucone', color: '#f05252' } };

export function UIDevelopment() {
  const { data: els, error, reload } = useApi<any[]>('/ui-elements', 6000);
  const { data: agents } = useApi<any[]>('/agents');
  const { status } = useStatus();
  const [screen, setScreen] = useState('Main HUD');
  const [exec, setExec] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const patch = useAction((id: string, body: any) => api(`/ui-elements/${id}`, { method: 'PATCH', body }), { onDone: reload });
  const runAgent = useAction((el: any) => api<{ executionId: string }>(`/agents/${el.assigned_agent_id ?? 'pixel'}/run`, {
    body: { prompt: `Zaimplementuj element UI "${el.name}" (ekran: ${el.screen}${el.section ? `, sekcja: ${el.section}` : ''}).\nSpecyfikacja: ${el.spec}\nŚcieżka w Roblox: ${el.roblox_path ?? '—'}\nZachowaj istniejącą zawartość plików i Style Lock.`, relatedFiles: el.files ?? [] },
  }), { success: 'Agent pracuje nad elementem', onDone: (r) => setExec(r.executionId) });

  const counts = useMemo(() => Object.fromEntries(SCREENS.map((s) => [s, (els ?? []).filter((e) => e.screen === s).length])), [els]);
  if (error) return <ErrorBox error={error} />;
  if (!els) return <Spinner />;
  const list = els.filter((e) => e.screen === screen);
  const sections = Array.from(new Set(list.map((e) => e.section ?? '—')));
  const done = (s: string) => { const l = els.filter((e) => e.screen === s); return l.length ? Math.round((l.filter((e) => ['implemented', 'approved'].includes(e.status)).length / l.length) * 100) : 0; };

  return (
    <div>
      <PageHeader icon={<LayoutDashboard size={20} className="text-gold" />} title="UI Development Center"
        subtitle="Faza 1 — Frontend. Każdy element ma specyfikację, status, agenta, pliki i zależności. Status „Zaimplementowane” ustawiasz po sprawdzeniu w Studio."
        actions={<>{!status?.ai.configured && <NotConfigured />}<Button icon={<Plus size={14} />} onClick={() => setAdding(true)}>Dodaj element</Button></>} />
      <Tabs value={screen} onChange={setScreen} className="mb-4" tabs={SCREENS.map((s) => ({ id: s, label: <span>{s} <span className="text-faint">{done(s)}%</span></span>, count: counts[s] }))} />

      {['Main HUD', 'Tavern Interface', 'Loading Screen'].includes(screen) && (
        <Card title="Podgląd makiety (wireframe)" className="mb-5" actions={<span className="text-[11px] text-faint">kolory = status elementu</span>}>
          {screen === 'Main HUD' && <HudWireframe els={list} />}
          {screen === 'Tavern Interface' && <TavernWireframe els={list} />}
          {screen === 'Loading Screen' && <LoadingWireframe els={list} />}
        </Card>
      )}

      {sections.map((sec) => (
        <Card key={sec} title={sec} className="mb-4" bodyClass="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-[12.5px]">
              <thead className="text-left text-[11px] text-faint"><tr className="border-b border-line">
                <th className="px-4 py-2">Element</th><th>Specyfikacja</th><th>Status</th><th>Agent</th><th>Pliki</th><th>Zatwierdzenie</th><th />
              </tr></thead>
              <tbody>
                {list.filter((e) => (e.section ?? '—') === sec).map((e) => (
                  <tr key={e.id} className="border-b border-line align-top last:border-0">
                    <td className="px-4 py-2.5 font-medium">{e.name}{e.roblox_path && <div className="font-mono text-[10.5px] text-faint">{e.roblox_path}</div>}{e.dependencies?.length > 0 && <div className="text-[10.5px] text-amber">zależy od: {e.dependencies.join(', ')}</div>}</td>
                    <td className="max-w-[320px] py-2.5 pr-3 text-mute">{e.spec}</td>
                    <td className="py-2.5 pr-2"><Select className="h-7 w-40 text-xs" value={e.status} style={{ color: UI_STATUS[e.status]?.color }} onChange={(x) => patch.run(e.id, { status: x.target.value })}>{Object.entries(UI_STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></td>
                    <td className="py-2.5 pr-2"><Select className="h-7 w-32 text-xs" value={e.assigned_agent_id ?? ''} onChange={(x) => patch.run(e.id, { assigned_agent_id: x.target.value })}>{(agents ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</Select></td>
                    <td className="py-2.5 pr-2">{(e.fileStatus ?? []).length === 0 ? <span className="text-faint">—</span> : e.fileStatus.map((f: any) => (
                      <Link key={f.path} to={f.exists ? `/workspace?file=${encodeURIComponent(f.path)}` : '#'} className={cx('flex items-center gap-1 font-mono text-[11px]', f.exists ? 'text-mint hover:underline' : 'text-faint')} title={f.exists ? 'Plik istnieje' : 'Plik jeszcze nie istnieje'}>
                        {f.exists ? <FileCheck2 size={11} /> : <FileX2 size={11} />}{f.path.split('/').pop()}
                      </Link>
                    ))}</td>
                    <td className="py-2.5 pr-2"><Select className="h-7 w-36 text-xs" value={e.approval_status} style={{ color: APPROVAL[e.approval_status]?.color }} onChange={(x) => patch.run(e.id, { approval_status: x.target.value })}>{Object.entries(APPROVAL).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></td>
                    <td className="py-2.5 pr-4"><Button size="sm" variant="primary" icon={<Play size={12} />} disabled={!status?.ai.configured} loading={runAgent.loading} onClick={() => runAgent.run(e)}>Zleć</Button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ))}
      <AddElement open={adding} screen={screen} onClose={() => setAdding(false)} onDone={() => { setAdding(false); reload(); }} />
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}

function AddElement({ open, screen, onClose, onDone }: { open: boolean; screen: string; onClose: () => void; onDone: () => void }) {
  const [f, setF] = useState({ name: '', section: '', spec: '', files: '', roblox_path: '' });
  const add = useAction(() => api('/ui-elements', { body: { screen, name: f.name, section: f.section || null, spec: f.spec, roblox_path: f.roblox_path || null, files: f.files.split(',').map((x) => x.trim()).filter(Boolean) } }), { success: 'Dodano element', onDone: () => { setF({ name: '', section: '', spec: '', files: '', roblox_path: '' }); onDone(); } });
  return (
    <Modal open={open} onClose={onClose} title={`Nowy element — ${screen}`} footer={<><Button variant="ghost" onClick={onClose}>Anuluj</Button><Button variant="primary" disabled={!f.name.trim()} loading={add.loading} onClick={() => add.run()}>Dodaj</Button></>}>
      <div className="space-y-3">
        <Field label="Nazwa"><Input value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></Field>
        <Field label="Sekcja"><Input value={f.section} onChange={(e) => setF({ ...f, section: e.target.value })} /></Field>
        <Field label="Specyfikacja"><Textarea value={f.spec} onChange={(e) => setF({ ...f, spec: e.target.value })} /></Field>
        <Field label="Ścieżka w Roblox"><Input value={f.roblox_path} onChange={(e) => setF({ ...f, roblox_path: e.target.value })} placeholder="StarterGui.MainHUD.…" /></Field>
        <Field label="Pliki (po przecinku)"><Input value={f.files} onChange={(e) => setF({ ...f, files: e.target.value })} placeholder="src/gui/MainHUD.model.json" /></Field>
      </div>
    </Modal>
  );
}

// ---------------- wireframes ----------------

const colorOf = (els: any[], name: string) => UI_STATUS[els.find((e) => e.name === name)?.status ?? 'not_started']?.color ?? '#5d6678';
function Box({ els, name, className, children, rotate = 0 }: { els: any[]; name: string; className?: string; children?: React.ReactNode; rotate?: number }) {
  const c = colorOf(els, name);
  return (
    <div className={cx('flex items-center justify-center rounded-md border-[3px] text-center text-[10.5px] font-bold leading-tight text-black', className)} title={name}
      style={{ borderColor: '#000', background: `${c}`, boxShadow: '3px 3px 0 #000', transform: `rotate(${rotate}deg)` }}>{children ?? name}</div>
  );
}
const Stage = ({ children }: { children: React.ReactNode }) => (
  <div className="relative mx-auto aspect-video w-full max-w-4xl overflow-hidden rounded-lg border-2 border-black" style={{ background: 'linear-gradient(160deg,#3b6d3a 0%,#2d4f6b 100%)' }}>
    <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1.3px)', backgroundSize: '9px 9px' }} />
    {children}
  </div>
);

function HudWireframe({ els }: { els: any[] }) {
  return (
    <Stage>
      <div className="absolute left-[3%] top-[5%] flex items-start gap-2">
        <Box els={els} name="Awatar postaci" className="h-16 w-16 !rounded-full">Awatar</Box>
        <div className="space-y-1.5">
          <Box els={els} name="Level" className="h-5 w-14">LVL</Box>
          <Box els={els} name="Pasek HP" className="h-4 w-44" rotate={-2}>HP</Box>
          <Box els={els} name="Pasek Many / Energii" className="h-4 w-40" rotate={-2}>MANA</Box>
          <Box els={els} name="Postęp EXP" className="h-2.5 w-36" rotate={-2}>{' '}</Box>
        </div>
      </div>
      <div className="absolute right-[3%] top-[5%] space-y-1.5">
        <Box els={els} name="Licznik Złota" className="h-7 w-32">🪙 ZŁOTO</Box>
        <Box els={els} name="Licznik Magicznych Kryształów" className="h-7 w-32">💎 KRYSZTAŁY</Box>
      </div>
      <div className="absolute left-[2%] top-[38%] space-y-2">
        {['Karczma', 'Pety', 'Tycoon', 'Arena', 'Ekwipunek'].map((t, i) => <Box key={t} els={els} name={`Zakładka ${t}`} className="h-8 w-20" rotate={i % 2 ? 2 : -2}>{t}</Box>)}
      </div>
      <div className="absolute bottom-[5%] left-1/2 flex -translate-x-1/2 items-end gap-3">
        <Box els={els} name="Hotbar umiejętności" className="h-12 w-72">HOTBAR</Box>
      </div>
      <Box els={els} name="Przycisk ataku" className="absolute bottom-[5%] right-[4%] h-20 w-20 !rounded-full" rotate={-3}>BAM!</Box>
    </Stage>
  );
}

function TavernWireframe({ els }: { els: any[] }) {
  return (
    <Stage>
      <div className="absolute inset-[6%] rounded-lg border-[4px] border-black p-3" style={{ background: colorOf(els, 'MainBoardFrame') + '33' }}>
        <div className="mb-1 text-[11px] font-black text-white" style={{ textShadow: '1px 1px 0 #000' }}>MainBoardFrame</div>
        <div className="flex h-[78%] gap-3">
          <Box els={els} name="Viewport Karczmarza + dymek" className="h-full w-[28%]">Karczmarz + dymek</Box>
          <div className="flex flex-1 items-center justify-around">
            {[-2, 1, 2].map((r, i) => <Box key={i} els={els} name="3 karty misji" className="h-[85%] w-[28%]" rotate={r}>{['ŁATWA', 'ŚREDNIA', 'BOSS'][i]}</Box>)}
          </div>
        </div>
        <Box els={els} name="Pasek energii + START QUEST" className="mt-2 h-[12%] w-full" rotate={-1}>ENERGIA ▰▰▰▱ · 🍺 · START QUEST!</Box>
      </div>
    </Stage>
  );
}

function LoadingWireframe({ els }: { els: any[] }) {
  return (
    <Stage>
      <Box els={els} name="Ilustracja tła" className="absolute inset-[4%] opacity-80">Rycerz + Kot-Mag na rozwidleniu: Karczma · Loch · Zamek</Box>
      <Box els={els} name="Logo z koroną" className="absolute left-1/2 top-[8%] h-14 w-64 -translate-x-1/2">👑 BLOCKY &amp; CRYCKET</Box>
      <Box els={els} name="Humorystyczne porady" className="absolute bottom-[18%] left-1/2 h-7 w-96 -translate-x-1/2">„Nie karm goblinów grzybami po północy”</Box>
      <Box els={els} name="Pędzlowy pasek postępu" className="absolute bottom-[7%] left-[10%] h-6 w-[80%]" rotate={-1}>▓▓▓▓▓▓▓░░░░</Box>
    </Stage>
  );
}
