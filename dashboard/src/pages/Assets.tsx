import { useMemo, useState } from 'react';
import { Image, Box, Upload, Wand2, Copy, Plus, ScanEye, CheckCircle2, Trash2 } from 'lucide-react';
import { api, useApi, STYLE_STATUS } from '../lib/api';
import { Badge, Button, Card, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner, StatusBadge, Tabs, Textarea, useAction, useToast, cx, NotConfigured, Confirm } from '../components/ui';
import { Markdown } from '../components/Markdown';
import { useStatus } from '../components/Layout';

const CATS: Record<string, string> = { characters: 'Postacie', pets: 'Pety', ui: 'UI', environment: 'Otoczenie', effects: 'Efekty' };
const ASSET_STATUS: Record<string, { label: string; color: string }> = { planned: { label: 'Zaplanowany', color: '#5d6678' }, created: { label: 'Utworzony', color: '#60a5fa' }, approved: { label: 'Zatwierdzony', color: '#34d399' }, rejected: { label: 'Odrzucony', color: '#f05252' } };
const PRESETS_2D: Record<string, string> = {
  hud: 'Przycisk/Ramka HUD', icon: 'Ikona Pixel-Art', panel: 'Okno/Panel 9-Slice', bubble: 'Dymek akcji BAM/POW', keyart: 'Loading Screen / Key Art',
};
const SUFFIX_2D: Record<string, string> = {
  hud: 'flat game UI element, slightly tilted, mobile-readable, isolated on transparent background',
  icon: 'crisp pixel-art icon, 64x64, limited palette, inside a 4px black comic frame, isolated on transparent background',
  panel: '9-slice friendly panel with uniform border thickness, flat center area, isolated',
  bubble: 'comic onomatopoeia speech bubble, bold lettering, explosive shape, isolated on transparent background',
  keyart: 'wide establishing scene, characters consistent with canonical designs, no UI, no progress bar',
};
const NEGATIVE = 'photorealistic, realistic lighting, minimalist corporate illustration, generic sci-fi, thin outlines, blurry, watermark, text artifacts, inconsistent character proportions';
const MESHY_SUFFIX = 'Roblox-style blocky low-poly voxel model, hand-painted Blockbench-like texture, chunky proportions, under 5k triangles, game-ready, single object';

export function Assets({ kind }: { kind: 'all' | '3d' }) {
  const { data: assets, error, reload } = useApi<any[]>('/assets', 6000);
  const { data: lock } = useApi<any>('/style-lock');
  const [cat, setCat] = useState('all');
  const [open, setOpen] = useState<string | null>(null);
  const list = useMemo(() => (assets ?? []).filter((a) => (kind === '3d' ? a.kind === '3d' : true) && (cat === 'all' || a.category === cat)), [assets, kind, cat]);

  if (error) return <ErrorBox error={error} />;
  if (!assets) return <Spinner />;
  const counts = Object.fromEntries(Object.keys(CATS).map((c) => [c, (assets ?? []).filter((a) => a.category === c && (kind !== '3d' || a.kind === '3d')).length]));
  const sel = assets.find((a) => a.id === open);

  return (
    <div>
      <PageHeader icon={kind === '3d' ? <Box size={20} className="text-gold" /> : <Image size={20} className="text-gold" />} title={kind === '3d' ? '3D Assets' : 'Asset Library'}
        subtitle={kind === '3d' ? 'Modele voxel/low-poly: specyfikacje, prompty Meshy AI i pliki Blockbench. Pliki trafiają do assets/ w projekcie.' : 'Wyłącznie assety BLOCKY & CRYCKET. Status zgodności „Compliant” wymaga prawdziwej analizy obrazu (Style Lock) lub Twojego ręcznego potwierdzenia.'} />
      <PromptBuilder kind={kind} lock={lock} onSaved={reload} />
      <Tabs value={cat} onChange={setCat} className="mb-4 mt-6" tabs={[{ id: 'all', label: 'Wszystkie', count: list.length }, ...Object.entries(CATS).map(([k, v]) => ({ id: k, label: v, count: counts[k] }))]} />
      {list.length === 0 ? <Empty title="Brak assetów w tej kategorii" /> : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
          {list.map((a) => (
            <button key={a.id} onClick={() => setOpen(a.id)} className="overflow-hidden rounded-lg border border-line bg-panel text-left hover:border-line2 cursor-pointer">
              <div className="flex aspect-[4/3] items-center justify-center bg-panel2" style={{ backgroundImage: 'radial-gradient(#252c39 1px, transparent 1.2px)', backgroundSize: '10px 10px' }}>
                {a.preview_path ? <img src={`/api/files/raw?path=${encodeURIComponent(a.preview_path)}`} className="max-h-full max-w-full object-contain" style={{ imageRendering: a.subcategory === 'currency' || a.subcategory === 'icons' ? 'pixelated' : 'auto' }} alt={a.name} />
                  : <div className="text-center text-[11px] text-faint">{a.kind === '3d' ? <Box size={28} className="mx-auto mb-1" /> : <Image size={28} className="mx-auto mb-1" />}brak pliku</div>}
              </div>
              <div className="space-y-1.5 p-3">
                <div className="flex items-center justify-between gap-2"><span className="truncate font-medium">{a.name}</span><Badge color="#8a93a6">{a.kind.toUpperCase()}</Badge></div>
                <div className="flex flex-wrap gap-1"><StatusBadge map={ASSET_STATUS} value={a.status} /><StatusBadge map={STYLE_STATUS} value={a.style_compliance} /></div>
                <div className="text-[11px] text-faint">{CATS[a.category]} · {a.feature ?? '—'} · v{a.version} · {a.agent_id?.toUpperCase() ?? '—'}</div>
              </div>
            </button>
          ))}
        </div>
      )}
      {sel && <AssetModal asset={sel} lock={lock} onClose={() => setOpen(null)} onChanged={reload} />}
    </div>
  );
}

function PromptBuilder({ kind, lock, onSaved }: { kind: 'all' | '3d'; lock: any; onSaved: () => void }) {
  const toast = useToast();
  const [type, setType] = useState(kind === '3d' ? 'meshy' : 'icon');
  const [desc, setDesc] = useState('');
  const [name, setName] = useState('');
  const [category, setCategory] = useState(kind === '3d' ? 'environment' : 'ui');
  const is3d = type === 'meshy';
  const core = is3d ? `${desc}, ${MESHY_SUFFIX}` : `${lock?.prefix ?? ''} ${desc}, ${SUFFIX_2D[type]}`;
  const variants = is3d
    ? [{ label: 'Meshy AI (text-to-3D)', text: `${core}\nNegative: ${NEGATIVE}` }]
    : [
      { label: 'Midjourney', text: `${core} --ar ${type === 'keyart' ? '16:9' : '1:1'} --sw 800 --style raw --no ${NEGATIVE.split(', ').slice(0, 5).join(', ')}` },
      { label: 'DALL-E 3', text: `${core}. Avoid: ${NEGATIVE}.` },
      { label: 'Higgsfield AI', text: `${core}\nNegative prompt: ${NEGATIVE}` },
    ];
  const save = useAction(() => api('/assets', { body: { name, category, kind: is3d ? '3d' : '2d', prompt: is3d ? core : `${desc}, ${SUFFIX_2D[type]}`, agent_id: is3d ? 'blocksmith' : 'artist' } }), { success: 'Zapisano asset z promptem', onDone: () => { setName(''); setDesc(''); onSaved(); } });
  const copy = (t: string) => { void navigator.clipboard.writeText(t); toast('success', 'Skopiowano prompt'); };
  return (
    <Card title="Style-Lock Prompt Studio" icon={<Wand2 size={14} className="text-violet" />} actions={<span className="text-[11px] text-faint">Prefiks Style Lock jest wymuszany dla każdego promptu 2D/UI</span>}>
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <div className="space-y-3">
          <Field label="Typ zasobu"><Select value={type} onChange={(e) => setType(e.target.value)}>{Object.entries(PRESETS_2D).map(([k, v]) => <option key={k} value={k}>{v}</option>)}<option value="meshy">Model 3D Voxel (Meshy AI)</option></Select></Field>
          <Field label="Opis obiektu"><Textarea value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="np. ikona mikstury energii w kuflu" /></Field>
          <div className="grid grid-cols-2 gap-2">
            <Field label="Nazwa assetu"><Input value={name} onChange={(e) => setName(e.target.value)} /></Field>
            <Field label="Kategoria"><Select value={category} onChange={(e) => setCategory(e.target.value)}>{Object.entries(CATS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</Select></Field>
          </div>
          <Button variant="primary" icon={<Plus size={14} />} className="w-full" disabled={!name.trim() || !desc.trim()} loading={save.loading} onClick={() => save.run()}>Zapisz w bibliotece</Button>
        </div>
        <div className="space-y-2">
          {!desc.trim() ? <Empty title="Opisz obiekt, aby wygenerować prompty" /> : variants.map((v) => (
            <div key={v.label} className="rounded-md border border-line bg-panel2">
              <div className="flex items-center justify-between border-b border-line px-3 py-1.5 text-xs font-medium">{v.label}<Button size="sm" variant="ghost" icon={<Copy size={12} />} onClick={() => copy(v.text)}>Kopiuj</Button></div>
              <pre className="whitespace-pre-wrap p-3 font-mono text-[11.5px] text-ink/85">{v.text}</pre>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function AssetModal({ asset: a, lock, onClose, onChanged }: { asset: any; lock: any; onClose: () => void; onChanged: () => void }) {
  const { status } = useStatus();
  const toast = useToast();
  const [prompt, setPrompt] = useState(a.prompt ?? '');
  const [del, setDel] = useState(false);
  const patch = useAction((body: any) => api(`/assets/${a.id}`, { method: 'PATCH', body }), { success: 'Zapisano', onDone: onChanged });
  const upload = useAction(async (file: File) => {
    const buf = await file.arrayBuffer();
    let bin = ''; const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    return api(`/assets/${a.id}/upload`, { body: { fileName: file.name, dataBase64: btoa(bin) } });
  }, { success: 'Wgrano plik do assets/', onDone: onChanged });
  const check = useAction(() => api(`/assets/${a.id}/style-check`, { body: {} }), { success: (r: any) => `Analiza Style Lock: ${r.verdict}`, onDone: onChanged });
  const remove = useAction(() => api(`/assets/${a.id}`, { method: 'DELETE' }), { success: 'Usunięto asset', onDone: () => { onChanged(); onClose(); } });

  return (
    <Modal open onClose={onClose} width="max-w-4xl" title={<span className="flex items-center gap-2">{a.name}<StatusBadge map={STYLE_STATUS} value={a.style_compliance} /></span>}>
      <div className="grid gap-5 md:grid-cols-[1fr_1.2fr]">
        <div className="space-y-3">
          <div className="flex aspect-square items-center justify-center rounded-lg border border-line bg-panel2">
            {a.preview_path ? <img src={`/api/files/raw?path=${encodeURIComponent(a.preview_path)}&v=${a.version}`} className="max-h-full max-w-full object-contain" alt="" /> : <span className="text-xs text-faint">Brak podglądu</span>}
          </div>
          <label className="flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed border-line2 py-2.5 text-[12.5px] text-mute hover:border-gold/50 hover:text-ink">
            <Upload size={14} />{upload.loading ? 'Wgrywanie…' : 'Wgraj plik (PNG/JPG/WEBP/FBX/OBJ/bbmodel)'}
            <input type="file" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) void upload.run(f); }} />
          </label>
          {a.source_path && <div className="font-mono text-[11px] text-faint">{a.source_path}</div>}
          <div className="text-[11px] text-faint">Do gry: wgraj plik w Studio → Asset Manager i wstaw <code>rbxassetid://…</code> w GUI.</div>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <Field label="Status"><Select value={a.status} onChange={(e) => patch.run({ status: e.target.value })}>{Object.entries(ASSET_STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</Select></Field>
            <Field label="Funkcja w grze"><Input defaultValue={a.feature ?? ''} onBlur={(e) => e.target.value !== (a.feature ?? '') && patch.run({ feature: e.target.value })} /></Field>
          </div>
          <Field label="Prompt generowania"><Textarea className="font-mono text-[11.5px]" value={prompt} onChange={(e) => setPrompt(e.target.value)} /></Field>
          <div className="flex gap-2">
            <Button size="sm" disabled={prompt === (a.prompt ?? '')} loading={patch.loading} onClick={() => patch.run({ prompt })}>Zapisz prompt</Button>
            <Button size="sm" variant="ghost" icon={<Copy size={12} />} onClick={() => { void navigator.clipboard.writeText(prompt); toast('success', 'Skopiowano'); }}>Kopiuj</Button>
            {a.kind === '2d' && lock && !prompt.startsWith(lock.prefix.slice(0, 40)) && <Badge color="#f05252">brak prefiksu Style Lock</Badge>}
          </div>
          <div className="rounded-md border border-line p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium">Checklista Style Lock</span>
              <div className="flex items-center gap-1.5">{!status?.ai.configured && <NotConfigured />}
                <Button size="sm" icon={<ScanEye size={12} />} disabled={!a.preview_path || !status?.ai.configured || !/\.(png|jpe?g|webp|gif)$/i.test(a.preview_path ?? '')} loading={check.loading} onClick={() => check.run()} title={!a.preview_path ? 'Wgraj obraz, aby przeanalizować' : ''}>Analizuj obraz</Button>
              </div>
            </div>
            <ul className="space-y-1">
              {(lock?.checklist ?? []).map((c: any) => {
                const v = a.style_checklist?.[c.key];
                return (
                  <li key={c.key} className="flex items-center justify-between gap-2 text-[12px]">
                    <span>{c.label}</span>
                    <Select className="h-6 w-32 text-[11px]" value={v ?? ''} onChange={(e) => patch.run({ style_checklist: { ...a.style_checklist, [c.key]: e.target.value } })}
                      style={{ color: v === 'pass' ? '#34d399' : v === 'fail' ? '#f05252' : undefined }}>
                      <option value="">nie sprawdzono</option><option value="pass">pass</option><option value="fail">fail</option><option value="not_applicable">n/d</option>
                    </Select>
                  </li>
                );
              })}
            </ul>
            {a.style_report ? <div className="mt-3 rounded bg-panel2 p-2 text-[12px]"><div className="mb-1 text-[11px] text-faint">Raport analizy obrazu (LOREKEEPER):</div><Markdown text={a.style_report} /></div>
              : <div className="mt-2 text-[11px] text-faint">Ten asset nie przeszedł jeszcze analizy obrazu — status zgodności nie jest potwierdzony.</div>}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant="success" icon={<CheckCircle2 size={12} />} onClick={() => patch.run({ style_compliance: 'approved', status: 'approved', manualOverride: true })}>Zatwierdź asset</Button>
            <Button size="sm" variant="danger" onClick={() => patch.run({ style_compliance: 'inconsistent' })}>Oznacz jako niespójny</Button>
            <Button size="sm" onClick={() => patch.run({ style_compliance: 'compliant', manualOverride: true })}>Ręcznie: Compliant</Button>
            <div className="flex-1" />
            <Button size="sm" variant="ghost" icon={<Trash2 size={12} />} onClick={() => setDel(true)}>Usuń</Button>
          </div>
        </div>
      </div>
      <Confirm open={del} onClose={() => setDel(false)} danger title="Usunąć asset z biblioteki?" text="Rekord zostanie usunięty. Plik w assets/ pozostaje na dysku." loading={remove.loading} onConfirm={() => remove.run()} />
    </Modal>
  );
}
