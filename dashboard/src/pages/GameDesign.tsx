import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Swords, Beer, Castle, Egg, Shield, Gavel, Send, HelpCircle } from 'lucide-react';
import { api, useApi, DECISION_STATUS } from '../lib/api';
import { Button, Card, Empty, ErrorBox, PageHeader, Select, Spinner, StatusBadge, Textarea, useAction, NotConfigured } from '../components/ui';
import { Markdown } from '../components/Markdown';
import { ExecutionModal } from '../components/ExecutionView';
import { useStatus } from '../components/Layout';

const SYSTEMS = [
  { icon: Beer, color: '#f5c542', name: 'Karczma (Questy)', text: 'Wybór 1 z 3 misji z tablicy u Karczmarza → teleport do mini-dungeonu → walka 3D lub clicker → Złoto, EXP, Loot.' },
  { icon: Castle, color: '#60a5fa', name: 'Twierdza (Tycoon)', text: 'Własna działka, klockowe budynki i droppery generujące pasywnie Złoto i Magiczne Kryształy.' },
  { icon: Egg, color: '#34d399', name: 'Pety', text: 'Wykluwanie z jaj, podążanie za graczem, bonusy do statystyk, pasywne ekspedycje. Pies, slime, smok.' },
  { icon: Shield, color: '#f05252', name: 'RPG', text: 'Poziomy, EXP, HP, Mana/Energia, ekwipunek, umiejętności, walka, loot, progresja.' },
];

export function GameDesign() {
  const { data: docs } = useApi<any[]>('/documents');
  const { data: decisions, error } = useApi<any[]>('/decisions', 8000);
  const { data: questions } = useApi<any[]>('/questions');
  const { status } = useStatus();
  const [agent, setAgent] = useState('designer');
  const [prompt, setPrompt] = useState('');
  const [exec, setExec] = useState<string | null>(null);
  const run = useAction(() => api<{ executionId: string }>(`/agents/${agent}/run`, { body: { prompt } }), { success: 'Zlecono specyfikację', onDone: (r) => { setPrompt(''); setExec(r.executionId); } });

  if (error) return <ErrorBox error={error} />;
  const gdd = docs?.find((d) => d.category === 'game_design' && d.approved);
  const designDecisions = (decisions ?? []).filter((d) => ['game_design', 'economy'].includes(d.category));

  return (
    <div>
      <PageHeader icon={<Swords size={20} className="text-gold" />} title="Game Design" subtitle="Mechaniki, pętle rozgrywki i decyzje projektowe. Nowe mechaniki od agentów to propozycje do czasu Twojego zatwierdzenia." />
      <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {SYSTEMS.map((s) => (
          <div key={s.name} className="rounded-lg border border-line bg-panel p-4">
            <div className="mb-2 flex items-center gap-2 font-semibold"><s.icon size={18} style={{ color: s.color }} />{s.name}</div>
            <p className="text-[12.5px] leading-relaxed text-mute">{s.text}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-5 xl:grid-cols-[1fr_420px]">
        <Card title="Game Design Document (kanoniczny)" actions={gdd && <Link to={`/docs?doc=${gdd.id}`} className="text-xs text-cyan hover:underline">Otwórz w dokumentacji →</Link>}>
          {!docs ? <Spinner /> : gdd ? <Markdown text={gdd.content} /> : <Empty title="Brak zatwierdzonego GDD" />}
        </Card>
        <div className="space-y-5">
          <Card title="Zleć specyfikację" icon={<Send size={14} className="text-cyan" />} actions={!status?.ai.configured && <NotConfigured />}>
            <div className="space-y-2">
              <Select value={agent} onChange={(e) => setAgent(e.target.value)}>
                <option value="designer">GAME DESIGNER — mechaniki i pętle</option>
                <option value="balancer">BALANCER — ekonomia i progresja</option>
                <option value="lorekeeper">LOREKEEPER — spójność z dokumentacją</option>
              </Select>
              <Textarea placeholder="np. Zaprojektuj mechanikę clickera z beczką w mini-dungeonie Karczmy…" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
              <Button variant="primary" className="w-full" loading={run.loading} disabled={!prompt.trim()} onClick={() => run.run()}>Zleć agentowi</Button>
            </div>
          </Card>
          <Card title="Decyzje projektowe" icon={<Gavel size={14} className="text-violet" />} actions={<Link to="/brain/decisions" className="text-xs text-cyan hover:underline">Rejestr →</Link>}>
            {!decisions ? <Spinner /> : designDecisions.length === 0 ? <Empty title="Brak decyzji" /> : (
              <ul className="space-y-2">{designDecisions.map((d) => (
                <li key={d.id} className="rounded-md border border-line bg-panel2 p-2.5">
                  <div className="flex items-start justify-between gap-2"><span className="text-[12.5px] font-medium"><span className="font-mono text-faint">{d.code}</span> {d.title}</span><StatusBadge map={DECISION_STATUS} value={d.status} /></div>
                  <p className="mt-1 text-[11.5px] text-mute">{d.description}</p>
                </li>
              ))}</ul>
            )}
          </Card>
          <Card title="Otwarte pytania" icon={<HelpCircle size={14} className="text-amber" />}>
            {(questions ?? []).filter((q) => q.status === 'open').map((q) => <div key={q.id} className="mb-2 text-[12.5px]">• {q.question}</div>)}
            <Link to="/brain/decisions?tab=questions" className="text-xs text-cyan hover:underline">Odpowiedz w rejestrze →</Link>
          </Card>
        </div>
      </div>
      <ExecutionModal id={exec} onClose={() => setExec(null)} />
    </div>
  );
}
