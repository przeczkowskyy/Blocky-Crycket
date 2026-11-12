import { all, get, insert, log, now, run, tx, uid, getSettings, setSettings } from './db.ts';
import { AGENTS, buildAgentInstructions, STYLE_LOCK_PREFIX } from './knowledge.ts';
import { readProjectFile } from './paths.ts';

/**
 * Seeds the database on first start. Everything seeded here is PLANNING data derived from the
 * Game Director's documentation (docs/dokumentacja_projektu.md + master prompt) or facts about the
 * real repository (Rojo setup). No agent activity, executions or metrics are fabricated.
 */
export function seedIfEmpty() {
  const existing = get<{ c: number }>('SELECT COUNT(*) AS c FROM agents');
  if (existing && existing.c > 0) return false;

  const t = now();
  tx(() => {
    setSettings(getSettings());

    // ---------- project ----------
    insert('project', {
      id: 'blocky-crycket',
      name: 'BLOCKY & CRYCKET',
      description: 'Roblox RPG / Incremental / Tycoon / Pet Collector — komiksowy humor w stylu Shakes & Fidget przełożony na aktywną rozgrywkę Roblox.',
      current_phase: 'phase1',
      roadmap: ROADMAP,
      sprint: {
        name: 'Sprint 1 — Fundament Fazy 1',
        objective: 'Uporządkować StarterGui, zbudować moduł statystyk gracza i ożywić HUD (HP, EXP, waluty).',
        agentIds: ['atlas', 'architect', 'pixel', 'lucius', 'artist'],
        startDate: t.slice(0, 10),
        endDate: null,
      },
      created_at: t,
      updated_at: t,
    });

    // ---------- agents ----------
    AGENTS.forEach((a, i) =>
      insert('agents', {
        id: a.id, name: a.name, role: a.role, description: a.description,
        instructions: buildAgentInstructions(a), model_provider: 'anthropic', model: 'claude-opus-5-5',
        effort: a.id === 'atlas' || a.id === 'lorekeeper' ? 'high' : a.id === 'lucius' || a.id === 'architect' ? 'xhigh' : 'high',
        status: 'idle', current_activity: null, permissions: a.permissions, enabled: true, color: a.color, icon: a.icon,
        sort: i, created_at: t, updated_at: t,
      }),
    );

    // ---------- tasks ----------
    const taskIds: Record<string, string> = {};
    for (const s of TASKS) {
      const id = uid('T-');
      taskIds[s.key] = id;
      insert('tasks', {
        id, title: s.title, description: s.description, assigned_agent_id: s.agent, status: s.status,
        priority: s.priority, effort: s.effort, dependencies: [], related_files: s.files ?? [], related_docs: s.docs ?? [],
        brain_source_ids: [], sprint: !!s.sprint, phase: s.phase, created_by: s.createdBy ?? 'user', created_at: t, updated_at: t,
      });
    }
    for (const s of TASKS) {
      if (s.deps?.length) run('UPDATE tasks SET dependencies = ? WHERE id = ?', s.deps.map((k) => taskIds[k]), taskIds[s.key]);
    }

    // ---------- decisions ----------
    DECISIONS.forEach((d, i) =>
      insert('project_decisions', {
        id: uid('dec-'), code: `D-${String(i + 1).padStart(3, '0')}`, title: d.title, description: d.description,
        category: d.category, status: d.status, proposed_by: d.proposedBy, approved_by: d.status === 'approved' ? 'Game Director (dokumentacja)' : null,
        related_docs: d.docs ?? [], related_tasks: [], created_at: t, approved_at: d.status === 'approved' ? t : null, updated_at: t,
      }),
    );

    // ---------- questions ----------
    for (const q of QUESTIONS) insert('questions', { id: uid('Q-'), question: q.q, context: q.ctx, raised_by: q.by, status: 'open', created_at: t });

    // ---------- knowledge base documents ----------
    const raw = readProjectFile('docs/dokumentacja_projektu.md') ?? '';
    const section = (n: number) => {
      const m = raw.split(/\n(?=## )/).find((s) => s.startsWith(`## ${n}.`));
      return m?.trim() ?? '';
    };
    const docs = [
      { title: 'Koncepcja gry i Core Loop', category: 'game_design', content: `${section(1)}\n\n${section(3)}`, approved: true, source: 'docs/dokumentacja_projektu.md §1, §3' },
      { title: 'Kierunek artystyczny i postacie', category: 'art_direction', content: section(2), approved: true, source: 'docs/dokumentacja_projektu.md §2' },
      { title: 'Style Lock — reguły generowania grafik', category: 'art_direction', content: STYLE_LOCK_DOC, approved: true, source: 'docs/dokumentacja_projektu.md §5 + master prompt §2' },
      { title: 'Specyfikacja UI: HUD i Ekran Ładowania', category: 'ui', content: section(4), approved: true, source: 'docs/dokumentacja_projektu.md §4' },
      { title: 'Okno Karczmy (TavernQuestGui) — propozycja hierarchii', category: 'ui', content: TAVERN_UI_DOC, approved: false, source: 'monster_prompt_dla_claude_code.md (wcześniejsza wersja specyfikacji)' },
      { title: 'Pipeline narzędziowy', category: 'technical', content: section(5), approved: true, source: 'docs/dokumentacja_projektu.md §5' },
      { title: 'Architektura techniczna: Rojo i struktura projektu', category: 'technical', content: TECH_DOC, approved: false, source: 'Opis stanu repozytorium przygotowany przez Claude Code' },
      { title: 'Roadmapa produkcji', category: 'roadmap', content: `${section(6)}\n\n${ROADMAP_DOC}`, approved: false, source: 'docs §6 (zatwierdzone) + fazy 2–6 z master promptu (propozycja)' },
      { title: 'Rejestr zatwierdzonych faktów', category: 'decisions', content: '# Rejestr zatwierdzonych faktów\n\nTen dokument jest uzupełniany automatycznie po zatwierdzeniu aktualizacji Project Brain (Change History).\n', approved: true, source: 'system' },
    ];
    for (const d of docs) {
      const id = uid('doc-');
      insert('project_documents', { id, title: d.title, category: d.category, content: d.content, version: 1, approved: d.approved, author: d.approved ? 'Game Director' : 'Claude Code', source: d.source, created_at: t, updated_at: t });
      insert('document_versions', { id: uid('dv-'), document_id: id, version: 1, content: d.content, approved: d.approved, author: d.approved ? 'Game Director' : 'Claude Code', note: 'Wersja początkowa', created_at: t });
    }

    // ---------- UI elements ----------
    UI_ELEMENTS.forEach((u, i) =>
      insert('ui_elements', {
        id: uid('ui-'), screen: u.screen, section: u.section, name: u.name, spec: u.spec, status: u.status ?? 'specified',
        assigned_agent_id: u.agent ?? 'pixel', files: u.files ?? [], dependencies: u.deps ?? [], approval_status: 'not_submitted',
        roblox_path: u.path ?? null, sort: i, updated_at: t,
      }),
    );

    // ---------- workflows ----------
    for (const w of WORKFLOWS) insert('workflows', { id: w.id, name: w.name, description: w.description, nodes: w.nodes, created_at: t });

    // ---------- tests ----------
    for (const ts of TESTS) insert('tests', { id: ts.id, name: ts.name, kind: ts.kind, category: ts.category, description: ts.description, last_status: 'not_run', regression: !!ts.regression });

    // ---------- planned assets ----------
    for (const a of ASSETS) {
      insert('assets', {
        id: uid('A-'), name: a.name, category: a.category, subcategory: a.sub, kind: a.kind, status: 'planned',
        style_compliance: 'needs_review', style_checklist: {}, agent_id: a.kind === '3d' ? 'blocksmith' : 'artist', feature: a.feature,
        prompt: a.kind === '2d' ? `${STYLE_LOCK_PREFIX} ${a.prompt}` : a.prompt, version: 1, brain_source_ids: [], created_at: t, updated_at: t,
      });
    }
  });

  log('system', 'Studio zainicjalizowane', 'Utworzono bazę danych i dane planistyczne z dokumentacji projektu (bez symulowanej aktywności agentów).', undefined, 'success');
  return true;
}

// =====================================================================================

const ROADMAP = [
  { id: 'phase1', name: 'FAZA 1 — FRONTEND', status: 'in_progress', proposed: false, items: [
    { title: 'Architektura UI (StarterGui)', done: false }, { title: 'Logika HUD', done: false }, { title: 'Ekran ładowania', done: false },
    { title: 'Interfejs Karczmy', done: false }, { title: 'Menu główne', done: false }, { title: 'Synchronizacja Rojo', done: true } ] },
  { id: 'phase2', name: 'FAZA 2 — SYSTEM POSTACI', status: 'planned', proposed: true, items: [
    { title: 'Postać gracza', done: false }, { title: 'Podglądy ViewportFrame', done: false }, { title: 'Prezentacja postaci', done: false }, { title: 'Statystyki postaci', done: false } ] },
  { id: 'phase3', name: 'FAZA 3 — SYSTEMY ROZGRYWKI', status: 'planned', proposed: true, items: [
    { title: 'Walka', done: false }, { title: 'Questy', done: false }, { title: 'Lochy', done: false }, { title: 'Pety', done: false }, { title: 'Ekwipunek', done: false } ] },
  { id: 'phase4', name: 'FAZA 4 — TYCOON', status: 'planned', proposed: true, items: [
    { title: 'Własność działek', done: false }, { title: 'Budynki', done: false }, { title: 'Droppery', done: false }, { title: 'Dochód pasywny', done: false } ] },
  { id: 'phase5', name: 'FAZA 5 — INTEGRACJA', status: 'planned', proposed: true, items: [
    { title: 'Synchronizacja Rojo', done: false }, { title: 'Integracja z Roblox Studio', done: false }, { title: 'Systemy serwerowe', done: false } ] },
  { id: 'phase6', name: 'FAZA 6 — TESTY I SZLIF', status: 'planned', proposed: true, items: [
    { title: 'QA', done: false }, { title: 'Wydajność', done: false }, { title: 'Balans', done: false }, { title: 'Finalny szlif', done: false } ] },
];

interface TaskSeed { key: string; title: string; description: string; agent: string; status: string; priority: string; effort: string; phase: string; sprint?: boolean; files?: string[]; docs?: string[]; deps?: string[]; createdBy?: string }

const TASKS: TaskSeed[] = [
  { key: 'rojo', title: 'Skonfigurować synchronizację Rojo', description: 'default.project.json mapuje src/server, src/client, src/shared i src/gui z $ignoreUnknownInstances=true, żeby nie usuwać zawartości istniejącej tylko w pliku .rbxl.', agent: 'architect', status: 'completed', priority: 'high', effort: 'S', phase: 'phase1', files: ['default.project.json'], createdBy: 'Claude Code' },
  { key: 'figma', title: 'Pipeline Figma → Roblox GUI', description: 'Skill .claude/skills/figma-to-roblox: konwersja ramek Figmy do ScreenGui (.model.json) synchronizowanych przez Rojo do StarterGui.', agent: 'pixel', status: 'completed', priority: 'medium', effort: 'S', phase: 'phase1', files: ['.claude/skills/figma-to-roblox/SKILL.md'], createdBy: 'Claude Code' },
  { key: 'gui-tree', title: 'Uporządkować hierarchię StarterGui', description: 'Zaprojektować docelową strukturę ScreenGui (MainHUD, LoadingScreenGui, TavernQuestGui, HeroSelectorGui, PetGui, InventoryGui) w src/gui oraz konwencje nazewnictwa.', agent: 'architect', status: 'planned', priority: 'high', effort: 'M', phase: 'phase1', sprint: true, docs: ['Specyfikacja UI: HUD i Ekran Ładowania'] },
  { key: 'stats', title: 'Moduł PlayerStats (HP / Mana / EXP / Level)', description: 'Serwerowy moduł statystyk gracza z replikacją do klienta (atrybuty lub RemoteEvent), źródło danych dla HUD.', agent: 'lucius', status: 'planned', priority: 'high', effort: 'M', phase: 'phase1', sprint: true },
  { key: 'hp', title: 'Zaimplementować pasek HP w HUD', description: 'Ukośny czerwony pasek HP w lewym górnym rogu, płynna animacja TweenService, komiksowy obrys.', agent: 'pixel', status: 'planned', priority: 'high', effort: 'M', phase: 'phase1', sprint: true, deps: ['gui-tree', 'stats'] },
  { key: 'exp', title: 'Wyświetlanie postępu EXP i Levelu', description: 'Pasek EXP + okrągły awatar z poziomem; animacja level-up w stylu komiksowym ("POW!").', agent: 'pixel', status: 'backlog', priority: 'medium', effort: 'M', phase: 'phase1', deps: ['stats'] },
  { key: 'currency', title: 'Pixel-artowe ikony walut', description: 'Ikony Złota i Magicznych Kryształów w komiksowej ramce 4px; prompty z Style Lock.', agent: 'artist', status: 'planned', priority: 'medium', effort: 'S', phase: 'phase1', sprint: true },
  { key: 'tavern', title: 'Tablica questów Karczmy (TavernQuestGui)', description: 'Okno Karczmy: sekcja Karczmarza, 3 nachylone karty misji, pasek energii, przycisk START QUEST.', agent: 'pixel', status: 'planned', priority: 'high', effort: 'L', phase: 'phase1', sprint: true, deps: ['gui-tree'] },
  { key: 'loading', title: 'Ekran ładowania', description: 'Tło z bohaterami na rozwidleniu dróg, pędzlowy pasek postępu, logo z koroną, humorystyczne porady.', agent: 'pixel', status: 'backlog', priority: 'medium', effort: 'M', phase: 'phase1' },
  { key: 'viewport', title: 'ViewportFrame z modelem postaci', description: 'Podgląd Rycerza / Kota-Maga w ViewportFrame z oświetleniem i animacją idle.', agent: 'lucius', status: 'backlog', priority: 'medium', effort: 'M', phase: 'phase2' },
  { key: 'pet', title: 'Podgląd peta podążającego za graczem', description: 'Prototyp follow-behaviour dla peta (pies / slime / smok) i podgląd w UI.', agent: 'lucius', status: 'backlog', priority: 'low', effort: 'M', phase: 'phase3' },
  { key: 'migrate', title: 'Przenieść istniejące skrypty z .rbxl do src/', description: 'Skrypty istniejące tylko w pliku miejsca nie są widoczne dla agentów. Wyeksportować je w Studio (Save to File) do odpowiednich folderów src/.', agent: 'architect', status: 'backlog', priority: 'high', effort: 'S', phase: 'phase1', createdBy: 'Claude Code' },
  { key: 'name', title: 'Ujednolicić pisownię nazwy gry', description: 'Dokumentacja używa "Blocky n Crycket", a master prompt "BLOCKY & CRYCKET". Potrzebna decyzja Dyrektora Gry.', agent: 'lorekeeper', status: 'backlog', priority: 'low', effort: 'XS', phase: 'phase1', createdBy: 'Claude Code' },
  { key: 'cleanup', title: 'Usunąć pliki testowe Rojo', description: 'src/server/Hello.server.luau, src/client/Hello.client.luau i src/gui/FigmaTest.model.json służyły tylko do testu połączenia.', agent: 'architect', status: 'backlog', priority: 'low', effort: 'XS', phase: 'phase1', files: ['src/server/Hello.server.luau', 'src/client/Hello.client.luau', 'src/gui/FigmaTest.model.json'], createdBy: 'Claude Code' },
];

interface DecisionSeed { title: string; description: string; category: string; status: string; proposedBy: string; docs?: string[] }
const DECISIONS: DecisionSeed[] = [
  { title: 'Obowiązkowy prefiks Style Lock', description: `Każdy prompt generujący element 2D/UI zaczyna się od: "${STYLE_LOCK_PREFIX}"`, category: 'art_direction', status: 'approved', proposedBy: 'Game Director', docs: ['docs/dokumentacja_projektu.md'] },
  { title: 'Hybryda trzech estetyk', description: 'Komiks/pop-art Shakes & Fidget + Roblox voxel/low-poly + pixel-art ikon UI. Zakaz fotorealizmu, korporacyjnego minimalizmu i generycznego sci-fi.', category: 'art_direction', status: 'approved', proposedBy: 'Game Director', docs: ['docs/dokumentacja_projektu.md'] },
  { title: 'Projekty głównych postaci', description: 'Rycerz (stalowa zbroja, niebieski tabard, wielki miecz); Kot-Mag (pomarańczowy, za duża purpurowa szata, kostur); pety: brązowy pies, świecący niebieski slime, mały czerwony smok.', category: 'art_direction', status: 'approved', proposedBy: 'Game Director', docs: ['docs/dokumentacja_projektu.md'] },
  { title: 'Aktywna rozgrywka zamiast pasków czasu', description: 'Misje realizowane w instancjonowanych mini-dungeonach (walka 3D lub clicker), bez biernego czekania.', category: 'game_design', status: 'approved', proposedBy: 'Game Director', docs: ['docs/dokumentacja_projektu.md'] },
  { title: 'Priorytet: Faza 1 — Frontend', description: 'Najpierw logika UI, ViewportFrame postaci, ożywienie HUD i interakcje GUI. Nie restartować projektu i nie przeprojektowywać zatwierdzonych elementów bez zgody.', category: 'roadmap', status: 'approved', proposedBy: 'Game Director', docs: ['docs/dokumentacja_projektu.md'] },
  { title: 'Dashboard w ciemnym stylu deweloperskim', description: 'Aplikacja studia używa ciemnego interfejsu (VS Code / Linear); styl komiksowy dotyczy wyłącznie assetów gry.', category: 'tooling', status: 'approved', proposedBy: 'Game Director' },
  { title: 'Mapowanie Rojo z $ignoreUnknownInstances', description: 'src/server → ServerScriptService.Server, src/client → StarterPlayerScripts.Client, src/shared → ReplicatedStorage.Shared, src/gui → StarterGui. Zawartość istniejąca tylko w .rbxl jest zachowywana.', category: 'technical', status: 'awaiting_approval', proposedBy: 'Claude Code' },
  { title: 'GUI z Figmy jako pliki .model.json', description: 'Każda ramka Figmy = jeden ScreenGui w src/gui/<Nazwa>.model.json; logika w LocalScript w src/client.', category: 'technical', status: 'awaiting_approval', proposedBy: 'Claude Code' },
  { title: 'Karczma: 3 misje (Łatwa / Średnia / Epicki Boss) zużywające Energię', description: 'Pochodzi z wcześniejszej specyfikacji (monster prompt). Kanoniczna dokumentacja mówi o 3 misjach, ale nie definiuje poziomów trudności ani Energii jako kosztu.', category: 'game_design', status: 'proposed', proposedBy: 'monster_prompt_dla_claude_code.md' },
  { title: 'Fazy roadmapy 2–6', description: 'System postaci → Systemy rozgrywki → Tycoon → Integracja → Testy i szlif. Propozycja z master promptu, nie dowód wykonanych prac.', category: 'roadmap', status: 'proposed', proposedBy: 'Master prompt' },
];

const QUESTIONS = [
  { q: 'Jaka jest oficjalna pisownia nazwy gry: "Blocky n Crycket" czy "BLOCKY & CRYCKET"?', ctx: 'docs/dokumentacja_projektu.md używa "Blocky n Crycket"; master prompt i logo z dokumentacji używają "BLOCKY & CRYCKET".', by: 'LOREKEEPER (wykryte przy indeksowaniu)' },
  { q: 'Czy zespół 10 agentów z master promptu zastępuje wcześniejszy skład 5 agentów (INK & VOXEL, FRAME-BUILDER, ROJO-CODER, BLOCK-MASTER, TAVERN-KEEPER)?', ctx: 'Przyjęto skład 10 agentów jako nowszą specyfikację. Role 5 agentów mieszczą się w nowym składzie.', by: 'Claude Code' },
  { q: 'Gdzie znajduje się zaprojektowane wcześniej drzewo obiektów Karczmy (Roblox GUI)?', ctx: 'Dokumentacja mówi, że struktura istnieje, ale w repozytorium (src/gui) jej nie ma — może istnieć tylko w pliku .rbxl lub w Figmie.', by: 'Claude Code' },
];

const STYLE_LOCK_DOC = `# Style Lock

## Obowiązkowy prefiks promptu 2D/UI
> ${STYLE_LOCK_PREFIX}

## Checklista zgodności
- Komiksowe obrysy (grube, czarne 3–4px)
- Żywe, nasycone kolory
- Geometria Roblox voxel / low-poly
- Ikony UI w ostrym pixel-arcie (ResampleMode = Pixelated) w komiksowej ramce 4px
- Tekstura halftone
- Cel-shading
- Przerysowane proporcje
- Spójność z projektami postaci

## Zakazane
Fotorealizm, minimalistyczne korporacyjne ilustracje, generyczne sci-fi, niezwiązane estetyki fantasy, niespójne proporcje postaci, niezwiązane palety barw.

## Wskazówki implementacyjne w Roblox
- Obrys: UIStroke 3–4px #000000
- Lekka asymetria: Rotation -2..2 na kartach i przyciskach
- Halftone: ImageLabel overlay z niską przezroczystością`;

const TAVERN_UI_DOC = `# TavernQuestGui — propozycja hierarchii (wymaga zatwierdzenia)

Źródło: wcześniejsza specyfikacja (monster prompt). Kanoniczna dokumentacja potwierdza istnienie drzewa obiektów Karczmy, ale nie ma go w repozytorium.

\`\`\`
StarterGui
└── TavernQuestGui (ScreenGui)
    └── MainBoardFrame (Frame, UIStroke 4px #000, UICorner)
        ├── HalftoneOverlay (ImageLabel, ImageTransparency ~0.85)
        ├── InnkeeperSection (Frame)
        │   ├── InnkeeperViewport (ViewportFrame)
        │   └── DialogueBubble (Frame + TextLabel, komiksowy dymek)
        ├── QuestCards (Frame + UIListLayout Horizontal)
        │   ├── QuestCard_Easy   (Rotation -2)
        │   ├── QuestCard_Medium (Rotation 1)
        │   └── QuestCard_Boss   (Rotation 2)
        └── BottomBar (Frame)
            ├── EnergyBar (ukośny pasek)
            ├── MugButton (ImageButton — napitek odnawia Energię)
            └── StartQuestButton (TextButton "START QUEST!")
\`\`\``;

const TECH_DOC = `# Architektura techniczna (stan repozytorium)

| Folder | Cel w Roblox | Typy plików |
|---|---|---|
| src/server | ServerScriptService.Server | *.server.luau (Script), *.luau (ModuleScript) |
| src/client | StarterPlayer.StarterPlayerScripts.Client | *.client.luau (LocalScript) |
| src/shared | ReplicatedStorage.Shared | *.luau (ModuleScript) |
| src/gui | StarterGui | *.model.json (ScreenGui) |

- Rojo 7.6.1, plik projektu: default.project.json (chroniony).
- $ignoreUnknownInstances = true na każdym węźle: zawartość istniejąca tylko w pliku .rbxl jest zachowana, ale niewidoczna dla agentów.
- Plik .rbxl jest binarny — nigdy nie jest edytowany przez studio.
- Grafiki nie mogą być wysłane przez Rojo — używamy placeholderów rbxassetid://0 i Asset Managera.
- Pipeline Figma → GUI: .claude/skills/figma-to-roblox/SKILL.md.

Proponowana docelowa struktura (do zatwierdzenia przez ARCHITECT/Dyrektora): ReplicatedStorage/{Modules,Remotes,Assets,Config}, ServerScriptService/{Services,Systems,Data}, StarterGui/{HUD,MainMenu,TavernUI,PetUI,InventoryUI,LoadingScreen}, ServerStorage/{Templates,Models}.`;

const ROADMAP_DOC = `## Proponowane fazy (do zatwierdzenia)
1. FAZA 1 — FRONTEND: architektura UI, logika HUD, ekran ładowania, interfejs Karczmy, menu główne.
2. FAZA 2 — SYSTEM POSTACI: postać gracza, podglądy ViewportFrame, prezentacja i statystyki postaci.
3. FAZA 3 — SYSTEMY ROZGRYWKI: walka, questy, lochy, pety, ekwipunek.
4. FAZA 4 — TYCOON: działki, budynki, droppery, dochód pasywny.
5. FAZA 5 — INTEGRACJA: Rojo, Roblox Studio, systemy serwerowe.
6. FAZA 6 — TESTY I SZLIF: QA, wydajność, balans, szlif.`;

interface UiSeed { screen: string; section?: string; name: string; spec: string; status?: string; agent?: string; files?: string[]; deps?: string[]; path?: string }
const UI_ELEMENTS: UiSeed[] = [
  // Main HUD
  { screen: 'Main HUD', section: 'Lewa góra', name: 'Awatar postaci', spec: 'Okrągły awatar bohatera (ViewportFrame lub headshot) z komiksowym obrysem 4px.', path: 'StarterGui.MainHUD.TopLeft.Avatar', files: ['src/gui/MainHUD.model.json'] },
  { screen: 'Main HUD', section: 'Lewa góra', name: 'Level', spec: 'Odznaka poziomu przy awatarze, komiksowa czcionka.', path: 'StarterGui.MainHUD.TopLeft.Level', files: ['src/gui/MainHUD.model.json'] },
  { screen: 'Main HUD', section: 'Lewa góra', name: 'Pasek HP', spec: 'Ukośny czerwony pasek HP, animacja TweenService przy zmianie.', path: 'StarterGui.MainHUD.TopLeft.HPBar', files: ['src/gui/MainHUD.model.json', 'src/client/HUDController.client.luau'] },
  { screen: 'Main HUD', section: 'Lewa góra', name: 'Pasek Many / Energii', spec: 'Ukośny niebieski pasek Many/Energii.', path: 'StarterGui.MainHUD.TopLeft.ManaBar', files: ['src/gui/MainHUD.model.json'] },
  { screen: 'Main HUD', section: 'Lewa góra', name: 'Postęp EXP', spec: 'Pasek postępu EXP pod paskami HP/Many.', path: 'StarterGui.MainHUD.TopLeft.EXPBar', files: ['src/gui/MainHUD.model.json'] },
  { screen: 'Main HUD', section: 'Prawa góra', name: 'Licznik Złota', spec: 'Licznik z pixel-artową ikoną monety.', path: 'StarterGui.MainHUD.TopRight.Gold', agent: 'pixel', deps: ['Ikona Złota'] },
  { screen: 'Main HUD', section: 'Prawa góra', name: 'Licznik Magicznych Kryształów', spec: 'Licznik z pixel-artową ikoną kryształu.', path: 'StarterGui.MainHUD.TopRight.Crystals', deps: ['Ikona Kryształu'] },
  { screen: 'Main HUD', section: 'Nawigacja boczna', name: 'Zakładka Karczma', spec: 'Nachylona komiksowa zakładka z ikoną kufla.', path: 'StarterGui.MainHUD.SideTabs.Tavern' },
  { screen: 'Main HUD', section: 'Nawigacja boczna', name: 'Zakładka Pety', spec: 'Nachylona zakładka z ikoną jajka.', path: 'StarterGui.MainHUD.SideTabs.Pets' },
  { screen: 'Main HUD', section: 'Nawigacja boczna', name: 'Zakładka Tycoon', spec: 'Nachylona zakładka z ikoną zamku.', path: 'StarterGui.MainHUD.SideTabs.Tycoon' },
  { screen: 'Main HUD', section: 'Nawigacja boczna', name: 'Zakładka Arena', spec: 'Nachylona zakładka z ikoną mieczy.', path: 'StarterGui.MainHUD.SideTabs.Arena' },
  { screen: 'Main HUD', section: 'Nawigacja boczna', name: 'Zakładka Ekwipunek', spec: 'Nachylona zakładka z ikoną plecaka.', path: 'StarterGui.MainHUD.SideTabs.Inventory' },
  { screen: 'Main HUD', section: 'Dół', name: 'Hotbar umiejętności', spec: 'Pasek umiejętności z pixel-artowymi ikonami i cooldownami.', path: 'StarterGui.MainHUD.Bottom.Hotbar' },
  { screen: 'Main HUD', section: 'Dół', name: 'Przycisk ataku', spec: 'Wielki przycisk akcji/ataku z dymkami "BAM!" / "POW!".', path: 'StarterGui.MainHUD.Bottom.AttackButton' },
  // Loading
  { screen: 'Loading Screen', section: 'Scena', name: 'Ilustracja tła', spec: 'Rycerz i Kot-Mag biegnący na rozwidleniu dróg między krzywą Karczmą, świecącym Lochem i Zamkiem na wzgórzu.', status: 'designed', agent: 'artist', path: 'ReplicatedFirst/LoadingScreenGui.Background' },
  { screen: 'Loading Screen', section: 'Dół', name: 'Pędzlowy pasek postępu', spec: 'Gruby, malarski pasek stylizowany na pociągnięcie pędzla — osobna warstwa nad tłem.', status: 'designed', path: 'LoadingScreenGui.ProgressBar' },
  { screen: 'Loading Screen', section: 'Logo', name: 'Logo z koroną', spec: 'Logo z koroną i napisem "BLOCKY & CRYCKET".', status: 'designed', agent: 'artist', path: 'LoadingScreenGui.Logo' },
  { screen: 'Loading Screen', section: 'Treść', name: 'Humorystyczne porady', spec: 'Losowe porady (gobliny, grzyby) — teksty od GAME DESIGNER.', agent: 'designer', path: 'LoadingScreenGui.TipLabel' },
  // Tavern
  { screen: 'Tavern Interface', section: 'Główne okno', name: 'MainBoardFrame', spec: 'Drewniana tablica, UIStroke 4px, nakładka halftone.', status: 'designed', path: 'StarterGui.TavernQuestGui.MainBoardFrame', files: ['src/gui/TavernQuestGui.model.json'] },
  { screen: 'Tavern Interface', section: 'Karczmarz', name: 'Viewport Karczmarza + dymek', spec: 'ViewportFrame z grubym Karczmarzem i komiksowym dymkiem dialogowym.', status: 'designed', path: 'TavernQuestGui.MainBoardFrame.InnkeeperSection' },
  { screen: 'Tavern Interface', section: 'Misje', name: '3 karty misji', spec: 'Trzy lekko nachylone karty misji do wyboru.', status: 'designed', path: 'TavernQuestGui.MainBoardFrame.QuestCards' },
  { screen: 'Tavern Interface', section: 'Dół', name: 'Pasek energii + START QUEST', spec: 'Skośny pasek energii, przycisk kufla, przycisk "START QUEST!".', status: 'designed', path: 'TavernQuestGui.MainBoardFrame.BottomBar' },
  // Character
  { screen: 'Character Interface', section: 'Selektor bohatera', name: 'HeroSelectorGui', spec: 'Centralny ViewportFrame z postacią, panel rasy (lewo), panel klasy (prawo), przycisk "Wyrusz na szlak!". (propozycja z wcześniejszej specyfikacji)', status: 'not_started' },
  // Others
  { screen: 'Pet Interface', name: 'Okno petów', spec: 'Kolekcja petów, wykluwanie z jaj, ekwipowanie, ekspedycje.', status: 'not_started' },
  { screen: 'Inventory', name: 'Okno ekwipunku', spec: 'Siatka przedmiotów z pixel-artowymi ikonami w komiksowych ramkach.', status: 'not_started' },
  { screen: 'Shop', name: 'Sklep', spec: 'Zakup jaj, ulepszeń i przedmiotów za Złoto/Kryształy.', status: 'not_started' },
  { screen: 'Tycoon Interface', name: 'Panel Twierdzy', spec: 'Budowa i ulepszanie dropperów, podgląd dochodu.', status: 'not_started' },
  { screen: 'Quest Interface', name: 'Tracker questa w dungeonie', spec: 'Cel misji, licznik wrogów / clicker, nagrody po ukończeniu.', status: 'not_started' },
  { screen: 'Settings', name: 'Ustawienia', spec: 'Dźwięk, grafika, sterowanie mobilne.', status: 'not_started' },
];

const WF = (id: string, name: string, description: string, steps: [string, string, string?][]) => ({
  id, name, description,
  nodes: steps.map(([type, label, agentId], i) => ({ id: `${id}-${i}`, type, label, agentId: agentId ?? null })),
});
const WORKFLOWS = [
  WF('wf-ui', 'A — Nowa funkcja UI', 'Od prośby do synchronizacji GUI przez Rojo.', [
    ['input', 'Prośba użytkownika'], ['agent', 'ATLAS — plan', 'atlas'], ['brain', 'Project Brain — kontekst'], ['agent', 'PIXEL — implementacja UI', 'pixel'],
    ['agent', 'ARCHITECT — struktura', 'architect'], ['agent', 'LUCIUS — logika Luau', 'lucius'], ['agent', 'SENTINEL — QA', 'sentinel'],
    ['agent', 'LOREKEEPER — przegląd spójności', 'lorekeeper'], ['approval', 'Zatwierdzenie człowieka'], ['sync', 'Rojo Sync']]),
  WF('wf-3d', 'B — Nowy asset 3D', 'Specyfikacja modelu, prompty i przegląd Style Lock.', [
    ['input', 'Prośba użytkownika'], ['agent', 'ATLAS — plan', 'atlas'], ['brain', 'Project Brain — kontekst'], ['agent', 'BLOCKSMITH — model', 'blocksmith'],
    ['agent', 'ARTIST — tekstury i prompty', 'artist'], ['agent', 'ARCHITECT — nazewnictwo i miejsce', 'architect'], ['agent', 'SENTINEL — QA', 'sentinel'],
    ['agent', 'Style Lock Review (LOREKEEPER)', 'lorekeeper'], ['approval', 'Zatwierdzenie człowieka'], ['sync', 'Roblox Studio']]),
  WF('wf-gameplay', 'C — Nowy system rozgrywki', 'Specyfikacja, architektura, kod i testy.', [
    ['input', 'Prośba użytkownika'], ['agent', 'ATLAS — plan', 'atlas'], ['brain', 'Project Brain — kontekst'], ['agent', 'GAME DESIGNER — specyfikacja', 'designer'],
    ['agent', 'ARCHITECT — architektura', 'architect'], ['agent', 'LUCIUS — implementacja', 'lucius'], ['agent', 'SENTINEL — QA', 'sentinel'],
    ['agent', 'LOREKEEPER — przegląd', 'lorekeeper'], ['approval', 'Zatwierdzenie człowieka'], ['sync', 'Roblox Studio']]),
  WF('wf-bug', 'D — Naprawa błędu', 'Diagnoza, poprawka i ponowny test.', [
    ['input', 'Zgłoszenie błędu'], ['agent', 'SENTINEL — diagnoza', 'sentinel'], ['agent', 'ATLAS — przydział', 'atlas'], ['brain', 'Project Brain — kontekst'],
    ['agent', 'LUCIUS — poprawka', 'lucius'], ['agent', 'SENTINEL — re-test', 'sentinel'], ['approval', 'Zatwierdzenie człowieka'], ['sync', 'Sync']]),
];

const TESTS = [
  { id: 'test-rojo-build', name: 'Rojo build projektu', kind: 'automated', category: 'integration', description: 'Uruchamia `rojo build default.project.json` — wykrywa błędne pliki .model.json i mapowanie.', regression: true },
  { id: 'test-sourcemap', name: 'Rojo sourcemap', kind: 'automated', category: 'integration', description: 'Generuje sourcemap — potwierdza poprawność drzewa projektu.', regression: true },
  { id: 'test-brain', name: 'Zdrowie Project Brain', kind: 'automated', category: 'integration', description: 'Brak nieaktualnych / niezaindeksowanych źródeł i zepsutych referencji.', regression: false },
  { id: 'test-lint', name: 'Lint Luau (selene)', kind: 'automated', category: 'luau', description: 'Statyczna analiza Luau — wymaga zainstalowanego `selene` w PATH.', regression: true },
  { id: 'test-hud-mobile', name: 'HUD skaluje się na telefonie', kind: 'manual', category: 'ui', description: 'Studio → Device Emulator (iPhone SE, iPad) — elementy HUD widoczne, min. 5% od krawędzi.', regression: true },
  { id: 'test-tavern-open', name: 'Okno Karczmy otwiera się i zamyka', kind: 'manual', category: 'ui', description: 'Zakładka Karczma otwiera TavernQuestGui; zamknięcie przywraca HUD.', regression: false },
  { id: 'test-hp-tween', name: 'Pasek HP animuje się przy obrażeniach', kind: 'manual', category: 'gameplay', description: 'Zadanie obrażeń → pasek HP płynnie maleje, bez skoków.', regression: false },
];

const ASSETS = [
  { name: 'Rycerz', category: 'characters', sub: 'hero', kind: '3d', feature: 'Postać gracza', prompt: 'Blocky Roblox knight, steel armor, blue tabard, oversized sword, low-poly voxel, hand-painted Blockbench textures.' },
  { name: 'Kot-Mag', category: 'characters', sub: 'hero', kind: '3d', feature: 'Postać gracza', prompt: 'Small angular orange cat mage, oversized purple wizard robe dragging on the ground, pointy hat, magic staff, voxel low-poly.' },
  { name: 'Karczmarz', category: 'characters', sub: 'npc', kind: '3d', feature: 'Karczma', prompt: 'Fat comedic blocky innkeeper NPC with apron and beer mug, voxel low-poly.' },
  { name: 'Brązowy pies', category: 'pets', sub: 'pet', kind: '3d', feature: 'Pety', prompt: 'Blocky brown dog pet, voxel style.' },
  { name: 'Niebieski slime', category: 'pets', sub: 'pet', kind: '3d', feature: 'Pety', prompt: 'Glowing cyan-blue cube slime pet, voxel style, emissive.' },
  { name: 'Czerwony smok', category: 'pets', sub: 'pet', kind: '3d', feature: 'Pety', prompt: 'Small angular red dragon pet, voxel style.' },
  { name: 'Ikona Złota', category: 'ui', sub: 'currency', kind: '2d', feature: 'HUD', prompt: 'pixel-art gold coin icon inside a 4px comic frame, 64x64.' },
  { name: 'Ikona Kryształu', category: 'ui', sub: 'currency', kind: '2d', feature: 'HUD', prompt: 'pixel-art magic crystal icon (purple-cyan) inside a 4px comic frame, 64x64.' },
  { name: 'Ikony zakładek HUD', category: 'ui', sub: 'icons', kind: '2d', feature: 'HUD', prompt: 'set of 5 pixel-art tab icons: beer mug, egg, castle, crossed swords, backpack; tilted comic tabs.' },
  { name: 'Ilustracja ekranu ładowania', category: 'ui', sub: 'menus', kind: '2d', feature: 'Loading Screen', prompt: 'knight and orange cat mage running at a fork in the road between a crooked tavern, a glowing dungeon and a castle on a hill, no progress bar, 16:9.' },
  { name: 'Logo BLOCKY & CRYCKET', category: 'ui', sub: 'menus', kind: '2d', feature: 'Loading Screen', prompt: 'game logo with a crown and the lettering "BLOCKY & CRYCKET".' },
  { name: 'Budynek Karczmy', category: 'environment', sub: 'tavern', kind: '3d', feature: 'Karczma', prompt: 'Crooked asymmetric blocky tavern building with bent roof, voxel low-poly.' },
  { name: 'Beczka do rozbijania', category: 'environment', sub: 'props', kind: '3d', feature: 'Clicker w dungeonie', prompt: 'Blocky wooden barrel prop with breakable stages, voxel.' },
  { name: 'Dropper Twierdzy', category: 'environment', sub: 'fortress', kind: '3d', feature: 'Tycoon', prompt: 'Blocky medieval dropper building producing gold coins, voxel.' },
];
