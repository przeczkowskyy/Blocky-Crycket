import { useState } from 'react';
import { Plug, RefreshCw, Radio, MonitorPlay, Cpu, GitBranch, Cloud, Figma, Terminal, CheckCircle2, Circle, Copy } from 'lucide-react';
import { api, useApi } from '../lib/api';
import { Badge, Button, Card, ErrorBox, Kbd, PageHeader, Spinner, useAction, useToast } from '../components/ui';

export function Integrations() {
  const { data: d, error, reload, loading } = useApi<any>('/integrations', 10000);
  const toast = useToast();
  const [aiTest, setAiTest] = useState<string | null>(null);
  const test = useAction(() => api<any>('/integrations/ai/test', { body: {} }), { success: (r: any) => `Połączenie OK: ${r.display_name ?? r.id}`, onDone: (r: any) => setAiTest(`OK — ${r.display_name ?? r.id}`) });
  if (error) return <ErrorBox error={error} />;
  if (!d) return <Spinner />;
  const copy = (t: string) => { void navigator.clipboard.writeText(t); toast('success', 'Skopiowano'); };

  const checklist = [
    { ok: !!d.rojo.cli, label: `Rojo CLI zainstalowane${d.rojo.cli ? ` (${d.rojo.cli})` : ''}` },
    { ok: d.rojo.connected, label: 'rojo serve działa' },
    { ok: d.studio.open, label: 'Miejsce otwarte w Roblox Studio' },
    { ok: d.ai.configured, label: 'Klucz Claude API w dashboard/.env' },
    { ok: d.git.configured, label: 'Repozytorium Git' },
    { ok: d.selene.installed, label: 'Linter selene (opcjonalnie)' },
    { ok: d.openCloud.configured, label: 'Roblox Open Cloud (opcjonalnie)' },
  ];

  return (
    <div>
      <PageHeader icon={<Plug size={20} className="text-gold" />} title="Integrations" subtitle="Rzeczywisty stan połączeń. Niczego nie udajemy — nieskonfigurowane integracje mają status NOT CONFIGURED."
        actions={<Button icon={<RefreshCw size={14} />} loading={loading} onClick={reload}>Sprawdź ponownie</Button>} />
      <div className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
        <Integ icon={<Radio size={18} />} name="Rojo" ok={d.rojo.connected}
          detail={d.rojo.connected ? `rojo serve ${d.rojo.serverVersion} na porcie ${d.rojo.port} · projekt „${d.rojo.projectName}” · protokół ${d.rojo.protocolVersion}` : `Brak odpowiedzi na porcie ${d.rojo.port}. Uruchom serwer w folderze projektu.`}
          cmd={!d.rojo.connected ? 'rojo serve' : undefined} onCopy={copy} />
        <Integ icon={<MonitorPlay size={18} />} name="Roblox Studio" ok={d.studio.open} warn
          detail={`${d.studio.open ? 'Miejsce jest otwarte.' : 'Miejsce nie jest otwarte.'} Pliki: ${d.studio.placeFiles.join(', ') || '—'}. ${d.studio.method} W Studio: Plugins → Rojo → Connect.`} />
        <Integ icon={<Cpu size={18} />} name="Claude API (agenci)" ok={d.ai.configured} detail={d.ai.detail + (aiTest ? ` · Test: ${aiTest}` : '')}
          action={d.ai.configured && <Button size="sm" loading={test.loading} onClick={() => test.run()}>Testuj połączenie</Button>}
          cmd={!d.ai.configured ? 'copy .env.example .env   # potem wpisz ANTHROPIC_API_KEY i zrestartuj' : undefined} onCopy={copy} />
        <Integ icon={<GitBranch size={18} />} name="Git" ok={d.git.configured} warn
          detail={d.git.configured ? `Gałąź ${d.git.branch} · ${d.git.changedFiles} zmienionych plików · ${d.git.lastCommit ?? 'brak commitów'}` : d.git.detail}
          cmd={!d.git.configured ? 'git init' : undefined} onCopy={copy} />
        <Integ icon={<Cloud size={18} />} name="Roblox Open Cloud" ok={d.openCloud.configured} warn detail={d.openCloud.detail + ' Publikowanie miejsca nie jest jeszcze zaimplementowane — celowo, bez zatwierdzonej decyzji.'} />
        <Integ icon={<Figma size={18} />} name="Figma" ok={false} warn detail={d.figma.detail} />
      </div>
      <Card className="mt-6" title="Lista kontrolna środowiska" icon={<Terminal size={14} className="text-mint" />}>
        <ul className="grid gap-2 sm:grid-cols-2">
          {checklist.map((c) => <li key={c.label} className="flex items-center gap-2 text-[13px]">{c.ok ? <CheckCircle2 size={15} className="text-mint" /> : <Circle size={15} className="text-faint" />}{c.label}</li>)}
        </ul>
        <div className="mt-4 space-y-1 text-[12px] text-mute">
          <div>Uruchomienie studia: <Kbd>cd dashboard</Kbd> → <Kbd>npm run dev</Kbd> → <Kbd>http://127.0.0.1:5173</Kbd></div>
          <div>Serwer studia nasłuchuje tylko na 127.0.0.1 — klucze API nigdy nie trafiają do przeglądarki.</div>
        </div>
      </Card>
    </div>
  );
}

function Integ({ icon, name, ok, warn, detail, cmd, onCopy, action }: { icon: React.ReactNode; name: string; ok: boolean; warn?: boolean; detail: string; cmd?: string; onCopy?: (t: string) => void; action?: React.ReactNode }) {
  const color = ok ? '#34d399' : warn ? '#f5c542' : '#f05252';
  return (
    <div className="rounded-lg border border-line bg-panel p-4">
      <div className="flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md" style={{ background: `${color}1a`, color }}>{icon}</div>
        <div className="flex-1 font-semibold">{name}</div>
        <Badge color={color} dot>{ok ? 'CONNECTED' : 'NOT CONFIGURED'}</Badge>
      </div>
      <p className="mt-3 text-[12.5px] leading-relaxed text-mute">{detail}</p>
      {cmd && <div className="mt-3 flex items-center gap-2 rounded-md bg-bg px-2.5 py-1.5 font-mono text-[11.5px]"><span className="flex-1 truncate">{cmd}</span><button className="text-faint hover:text-ink cursor-pointer" onClick={() => onCopy?.(cmd)}><Copy size={12} /></button></div>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
