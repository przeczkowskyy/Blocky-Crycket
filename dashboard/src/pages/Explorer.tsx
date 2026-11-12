import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FolderTree, ChevronDown, ChevronRight, RefreshCw, Info, Box, FileCode, Folder, Monitor, Layers, Database, Server, User } from 'lucide-react';
import { useApi } from '../lib/api';
import { Button, Card, ErrorBox, PageHeader, Spinner, Badge } from '../components/ui';

const CLASS_ICON: Record<string, any> = {
  DataModel: Database, Folder, ModuleScript: FileCode, Script: FileCode, LocalScript: FileCode, ScreenGui: Monitor, Frame: Layers,
  ReplicatedStorage: Box, ServerScriptService: Server, StarterGui: Monitor, StarterPlayer: User, StarterPlayerScripts: User,
};
const CLASS_COLOR: Record<string, string> = { Script: '#60a5fa', LocalScript: '#22d3ee', ModuleScript: '#a78bfa', ScreenGui: '#f472b6', Folder: '#f5c542' };

const PROPOSED: Record<string, string[]> = {
  Workspace: ['Map', 'Tavern', 'Dungeons', 'Fortress', 'Pets', 'NPCs'],
  ReplicatedStorage: ['Modules', 'Remotes', 'Assets', 'Config'],
  ServerScriptService: ['Services', 'Systems', 'Data'],
  StarterPlayer: ['StarterPlayerScripts', 'StarterCharacterScripts'],
  StarterGui: ['HUD', 'MainMenu', 'TavernUI', 'PetUI', 'InventoryUI', 'LoadingScreen'],
  ServerStorage: ['Templates', 'Models'],
};

export function Explorer() {
  const { data, error, reload, loading } = useApi<any>('/explorer');
  return (
    <div>
      <PageHeader icon={<FolderTree size={20} className="text-gold" />} title="Roblox Explorer"
        subtitle="Prawdziwe drzewo instancji zarządzanych przez Rojo (wygenerowane przez `rojo sourcemap`). Kliknij skrypt, aby otworzyć go w edytorze."
        actions={<Button icon={<RefreshCw size={14} />} loading={loading} onClick={reload}>Odśwież</Button>} />
      <div className="grid gap-5 xl:grid-cols-[1fr_420px]">
        <Card title="Drzewo projektu (Rojo)" bodyClass="p-2">
          {error && <ErrorBox error={error} />}
          {!data ? <Spinner /> : data.ok ? <Node node={data.tree} depth={0} /> : <ErrorBox error={data.error} />}
        </Card>
        <div className="space-y-5">
          <Card title="Czego tu nie widać" icon={<Info size={14} className="text-sky" />}>
            <p className="text-[12.5px] leading-relaxed text-mute">Mapowanie używa <code>$ignoreUnknownInstances</code>, więc instancje istniejące tylko w pliku <code>.rbxl</code> (Workspace, mapy, stare skrypty) nie są tu pokazane i agenci ich nie widzą. Aby je udostępnić, wyeksportuj skrypty w Studio (<i>Save to File</i>) do folderów <code>src/</code>.</p>
          </Card>
          <Card title="Proponowana struktura (master prompt)" icon={<Layers size={14} className="text-violet" />}>
            <p className="mb-2 text-[11.5px] text-faint">To propozycja, nie stan faktyczny. Zmiany struktury przeprowadza ARCHITECT przez zatwierdzenia — bez tworzenia duplikatów.</p>
            {data?.ok && Object.entries(PROPOSED).map(([svc, kids]) => {
              const svcNode = data.tree.children?.find((c: any) => c.name === svc);
              const names = new Set<string>();
              const walk = (n: any) => { names.add(n.name); (n.children ?? []).forEach(walk); };
              if (svcNode) walk(svcNode);
              return (
                <div key={svc} className="mb-2">
                  <div className="text-[12px] font-medium">{svc} {svcNode ? <Badge color="#34d399">istnieje</Badge> : <Badge color="#5d6678">tylko w .rbxl / brak</Badge>}</div>
                  <div className="mt-1 flex flex-wrap gap-1">{kids.map((k) => <Badge key={k} color={names.has(k) ? '#34d399' : '#5d6678'}>{k}</Badge>)}</div>
                </div>
              );
            })}
            <Link to="/agents/architect" className="text-xs text-cyan hover:underline">Zleć ARCHITECT reorganizację →</Link>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Node({ node, depth }: { node: any; depth: number }) {
  const [open, setOpen] = useState(depth < 3);
  const Icon = CLASS_ICON[node.className] ?? Box;
  const color = CLASS_COLOR[node.className] ?? '#8a93a6';
  const file = (node.filePaths ?? []).find((f: string) => !f.endsWith('.meta.json'));
  const hasKids = (node.children ?? []).length > 0;
  return (
    <div>
      <div className="flex items-center gap-1.5 rounded py-0.5 pr-2 text-[12.5px] hover:bg-panel2" style={{ paddingLeft: 6 + depth * 16 }}>
        <button onClick={() => setOpen(!open)} className="w-3 text-faint cursor-pointer">{hasKids ? (open ? <ChevronDown size={12} /> : <ChevronRight size={12} />) : null}</button>
        <Icon size={13} style={{ color }} />
        <span className="font-medium">{node.name}</span>
        <span className="text-[10.5px] text-faint">{node.className}</span>
        {file && <Link to={`/workspace?file=${encodeURIComponent(file)}`} className="ml-auto truncate font-mono text-[10.5px] text-cyan hover:underline">{file}</Link>}
      </div>
      {open && node.children?.map((c: any, i: number) => <Node key={c.name + i} node={c} depth={depth + 1} />)}
    </div>
  );
}
