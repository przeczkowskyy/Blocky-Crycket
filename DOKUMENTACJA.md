# BLOCKY & CRYCKET — dokumentacja projektu

> **Stan na:** 12.11.2026 · **Faza:** 1 — Frontend
> **Źródło prawdy:** sejf Obsidian [`B&C/`](B%26C/00%20Start.md). Ten plik zbiera w jednym miejscu wiedzę z sejfu i z kodu. Jeśli coś się nie zgadza, obowiązuje sejf.

**Jak czytać statusy** (te same co w sejfie):

| Oznaczenie | Znaczenie |
|---|---|
| ✅ **kanon** | zatwierdzone przez Karola albo Pawła (wystarczy jeden, D-030), obowiązuje |
| 💡 **propozycja** | pomysł albo starsza specyfikacja, **nie jest faktem** |
| ❓ **do decyzji** | czeka na decyzję jednego z nich |

## Spis treści
1. [Gra w skrócie](#1-gra-w-skrócie)
2. [Postacie i świat](#2-postacie-i-świat)
3. [Mechaniki](#3-mechaniki)
4. [Kierunek artystyczny](#4-kierunek-artystyczny)
5. [Interfejs (UI)](#5-interfejs-ui)
6. [Architektura techniczna](#6-architektura-techniczna)
7. [Narzędzia](#7-narzędzia)
8. [Workflow](#8-workflow)
9. [Decyzje, pytania i roadmapa](#9-decyzje-pytania-i-roadmapa)
10. [Znane problemy i pułapki](#10-znane-problemy-i-pułapki)
11. [Słowniczek](#11-słowniczek)
12. [Historia zmian](#12-historia-zmian)

---

## 1. Gra w skrócie
✅ kanon · [Koncepcja i Core Loop](B%26C/Gra/Koncepcja%20i%20Core%20Loop.md)

- **Platforma:** Roblox.
- **Gatunek:** RPG / Incremental / Tycoon / Pet Collector.
- **Core loop:** powtarzalne pętle znane z Robloxa (ciągły progres, zbieranie petów, rozbudowa bazy) połączone z rozbudowanym systemem RPG i przerysowanym humorem inspirowanym przeglądarkową grą *Shakes & Fidget*.
- **Różnica względem inspiracji:** zamiast biernego czekania na odliczanie czasu misji gra stawia na akcję: instancjonowane mini-dungeony, mechaniki clicker/incremental i ruch w świecie 3D.
- **Zasada nadrzędna (D-004):** rozgrywka ma być **aktywna**. Każdy pomysł z pasywnym timerem trzeba uzasadnić i oznaczyć jako propozycję.
- **Nazwa:** oryginalna dokumentacja pisze „Blocky n Crycket”, logo i nowsze materiały „BLOCKY & CRYCKET”. Oficjalna pisownia ❓ (pytanie otwarte #1).

## 2. Postacie i świat
✅ kanon (poza kolumną „do potwierdzenia”) · [Rycerz](B%26C/Postacie/Rycerz.md) · [Kot-Mag](B%26C/Postacie/Kot-Mag.md) · [Karczmarz](B%26C/Postacie/Karczmarz.md) · [Pety](B%26C/Gra/Pety.md)

| Postać | Opis (kanon) | Do potwierdzenia (💡) |
|---|---|---|
| **Rycerz** (bohater) | kanciasty ludzik Roblox, stalowa zbroja, niebieski tabard, wielki miecz | — |
| **Kot-Mag** (bohater) | mały, kanciasty, pomarańczowy kot w purpurowej, za dużej szacie czarodzieja (ciągnie się po ziemi), z magicznym kosturem | spiczasty kapelusz, fioletowy kryształ na kosturze |
| **Karczmarz** (NPC) | prowadzi Karczmę; u niego gracz wybiera misje z drewnianej tablicy | gruby i prześmiewczy; w oknie Karczmy pokazany w ViewportFrame z komiksowym dymkiem |
| **Pies** (pet) | brązowy, kanciasty | — |
| **Slime** (pet) | świecący, niebieski (cyjanowy), w kształcie kostki | — |
| **Smok** (pet) | mały, czerwony, kanciasty | — |

Rycerz i Kot-Mag to wizytówka gry. Wszystkie postacie i pety są w stylu voxel (blokowe bryły).
**Miejsca** znane z ekranu ładowania: krzywa **Karczma**, świecący **Loch** (portal) i **Zamek na wzgórzu**.

## 3. Mechaniki

### Karczma (questy) ✅
[Karczma (Questy)](B%26C/Gra/Karczma%20%28Questy%29.md)
- Gracz wybiera **jedną z trzech misji** z drewnianej tablicy u Karczmarza i **teleportuje się do mini-dungeonu**.
- W dungeonie albo pokonuje określoną liczbę wrogów (walka 3D), albo przyspiesza questa **mechaniką clickera** na obiekcie (np. uderzanie w beczkę).
- Nagrody: **Złoto, EXP, Loot**.
- 💡 Propozycja (D-009): poziomy misji Łatwa / Średnia / Epicki Boss oraz **Energia** zużywana przez misje i odnawiana napitkiem w kuflu.

### Twierdza (tycoon) ✅
[Twierdza (Tycoon)](B%26C/Gra/Twierdza%20%28Tycoon%29.md)
- Każdy gracz ma **własną działkę (plot)**.
- Za surowce z misji buduje klockowe budynki, tak zwane **droppery**.
- Droppery **pasywnie generują Złoto i Magiczne Kryształy**.
- Do ustalenia: lista budynków, koszty, ścieżka ulepszeń, balans dochodu względem questów.

### Pety ✅
[Pety](B%26C/Gra/Pety.md)
- Wykluwają się z **jaj** (mechanika w stylu Pet Simulator).
- **Towarzyszą postaci** w świecie 3D i **modyfikują statystyki**.
- Mogą jechać na **pasywne ekspedycje**. To jedyny element pasywny, więc trzeba go pogodzić z zasadą aktywnej rozgrywki.
- Do ustalenia: rzadkości, ceny jaj, bonusy, czas i nagrody ekspedycji.

### System RPG 💡
[System RPG](B%26C/Gra/System%20RPG.md)
Kanon mówi tylko o „rozbudowanym systemie RPG” i o HUD z poziomem, HP, Maną/Energią i EXP. Lista z późniejszej specyfikacji (do potwierdzenia): poziomy i EXP, HP i Mana/Energia, ekwipunek i inwentarz, umiejętności na hotbarze, walka i loot.

### Arena (PvP) 💡
[Arena (PvP)](B%26C/Gra/Arena%20%28PvP%29.md)
Kanon wspomina tylko zakładkę Arena (ikona mieczy) w HUD. Pomysł: pojedynki z innymi graczami i komiksowe dymki obrażeń („BAM!”, „POW!”, „CRIT!”).

### Waluty
- ✅ Kanon: **Złoto** i **Magiczne Kryształy**.
- HUD z Figmy pokazuje **Złoto** i **Diamenty (Gems)**, opisane jako waluta premium. Czy Diamenty to Magiczne Kryształy, i czy są płatne? ❓ (pytanie otwarte #6).

## 4. Kierunek artystyczny
✅ kanon · [Kierunek artystyczny](B%26C/Styl/Kierunek%20artystyczny.md) · [Instrukcja promptów — Glossy Ink](B%26C/Styl/Instrukcja%20prompt%C3%B3w%20%E2%80%94%20Glossy%20Ink.md)

Styl to hybryda **trzech estetyk** (D-002):
1. **Komiks i pop-art (Shakes & Fidget):** grube czarne obrysy 3–4 px (cel-shading), przerysowane proporcje, wygięta i asymetryczna architektura, subtelny wzór halftone (kropki rastrowe) w tłach i cieniach.
2. **Roblox voxel / low-poly:** żywa, mocno nasycona paleta; postacie, pety i otoczenie z kanciastych, blokowych brył.
3. **Pixel-art:** wszystkie ikony w interfejsie (przedmioty, waluty, loot, zakładki) w ostrym pixel-arcie, zamknięte w komiksowych ramkach.

**Interfejs:** płaski (flat design), czytelny na telefonach, asymetryczne ramki, lekko nachylone przyciski, komiksowe fonty i dymki („BAM!”, „POW!”).

**Zakazane:** fotorealizm, minimalistyczne korporacyjne ilustracje, generyczne sci-fi, niezwiązane estetyki fantasy, niespójne proporcje postaci, niezwiązane palety barw.

> **Zmiana z 13.11.2026 (D-027).** Instrukcja „Glossy Ink” zastąpiła dwa zapisy: pixel-art ikon (punkt 3) i słowa „płaski (flat design)” w opisie interfejsu. Reszta obowiązuje dalej: komiks/pop-art, voxel/low-poly, czytelność na telefonach, asymetryczne ramki, nachylone przyciski i komiksowe dymki (te trzy ostatnie czekają na pytanie otwarte #25). Wzmianki o pixel-artowych ikonach w dalszych sekcjach (ustawienie `Pixelated`, ikony walut w HUD) są sprzed tej decyzji.

### Instrukcja promptów „Glossy Ink” (D-027, obowiązuje od 13.11.2026)
[Instrukcja promptów — Glossy Ink](B%26C/Styl/Instrukcja%20prompt%C3%B3w%20%E2%80%94%20Glossy%20Ink.md)

Każdy prompt generujący grafikę składa się z czterech części kopiowanych z notatki bez zmian: stałego początku, zmiennego środka (opis konkretnego assetu), stałego końca i osobnego negative promptu. Do tego dochodzą żelazne zasady z instrukcji: zamknięte krawędzie, puste kontenery, okna ze statystykami i mapy izometryczne.

Dawny prefiks Style Lock (D-001, z nazwą gry-inspiracji) jest zastąpiony i zostaje w sejfie tylko jako historia: [Style Lock](B%26C/Styl/Style%20Lock.md).

### Przełożenie na Roblox 💡
`UIStroke` 3–4 px `#000000` jako obrys · `Rotation` od −2 do 2 na kartach i przyciskach · `ResampleMode = Pixelated` dla ikon pixel-art · halftone jako nakładka `ImageLabel` o niskiej widoczności.

## 5. Interfejs (UI)

| Ekran | Projekt | Implementacja w Roblox | Notatka |
|---|---|---|---|
| Ekran ładowania | ✅ kanon | ✅ gotowy (`ReplicatedFirst`) | [Ekran ładowania](B%26C/UI/Ekran%20%C5%82adowania.md) |
| HUD | ✅ kanon (specyfikacja) + wersja z Figmy ❓ | ✅ wersja z Figmy: panel gracza + 6 przycisków | [HUD](B%26C/UI/HUD.md) |
| Okno Karczmy | ❓ do decyzji | ⬜ nie rozpoczęte | [Okno Karczmy](B%26C/UI/Okno%20Karczmy.md) |
| Selektor bohatera | 💡 propozycja | ⬜ nie rozpoczęty | [Selektor bohatera](B%26C/UI/Selektor%20bohatera.md) |
| Menu główne | w roadmapie Fazy 1 | ⬜ nie rozpoczęte | — |

Projekty UI są w Figmie (plik `BbLd4jDnvxAmOWZN1hAZQJ`). Numery węzłów (node) podane są przy ekranach.

### 5.1 Ekran ładowania
**Projekt ✅:** przerysowani bohaterowie (Rycerz i Kot-Mag) biegnący na rozwidleniu dróg między krzywą Karczmą, świecącym Lochem i Zamkiem na wzgórzu. Na dole gruby, malarski pasek postępu. Logo z koroną i napisem „BLOCKY & CRYCKET”.
**Figma:** pasek postępu [node 2:2](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-2) (źródło prawdy wyglądu paska), cały kadr 2752×1536 [node 2:75](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-75).

**Implementacja:**
- `ReplicatedFirst.LoadingScreen` (ScreenGui-szablon, `IgnoreGuiInset = true`, `DisplayOrder = 100`) i `ReplicatedFirst.LoadingClient` (LocalScript).
- `ReplicatedFirst` **nie jest mapowany przez Rojo**, więc oba obiekty istnieją tylko w pliku `.rbxl`. Ich źródłem jest skrypt [`tools/studio/build_loading_screen.luau`](tools/studio/build_loading_screen.luau): usuwa stare wersje i buduje obie od nowa (uruchamiany przez Roblox Studio MCP albo z Command Bar w Studio).
- Pasek postępu jest odtworzony **natywnie** z elementów Roblox. Obrazem jest tylko tło (key-art).

```
LoadingScreen (ScreenGui)
├── Background        ImageLabel: key-art rbxassetid://129202798952612, ScaleType Crop
├── Vignette          Frame + UIGradient: przyciemnienie dolnych 30% ekranu
└── ProgressBar       Frame: 58% szerokości, proporcje 1600×300, przy dolnej krawędzi
    ├── Label (+Shadow)           „ŁADOWANIE PRZYGODY...” (LuckiestGuy)
    ├── StoneShadow, StoneFrame   kamienna rama z gradientem, nity Rivet1–4, wycięcia Slot1–6
    ├── Track                     drewniany tor z deskami Plank1–9
    │   └── Fill (CanvasGroup)    cyjanowe wypełnienie: ukośne paski, Highlight, Shade
    ├── Spark                     pikselowa iskra na końcu wypełnienia
    ├── GemL, GemR                złoto-ametystowe klejnoty po bokach
    ├── Percent (+Shadow)         procent na środku (LuckiestGuy)
    └── Tip (+Shadow)             tekst pod paskiem (Arcade)
```

**Zachowanie** (💡 wdrożone 11.11.2026, czeka na akceptację):
- Wyłącza domyślny ekran Robloxa, wstawia kopię `LoadingScreen` do `PlayerGui`, najpierw ładuje tło, potem w tle zasoby z `ReplicatedStorage` (paczki po 25).
- Pasek napełnia się **co najmniej 4,5 s** (`MIN_DURATION`), nawet gdy wszystko jest już załadowane. Przy wolnym ładowaniu czeka na prawdziwy postęp. Rośnie nierówno: kilka losowych „przystanków” z płynnym przyspieszaniem i zwalnianiem.
- Przy 100%: pauza 0,6 s (`HOLD_AT_100`), ustawienie atrybutu gracza `LoadingDone = true` (sygnał dla HUD), wygaszenie w 0,6 s, usunięcie GUI.
- Tekst pod paskiem zmienia się co 2,6 s (`TIP_INTERVAL`) z płynnym przejściem. Pula 19 tekstów w 3 kategoriach: **WSKAZÓWKA** (tylko mechaniki z kanonu), **PLOTKA Z KARCZMY** i **CIEKAWOSTKA** (humor). Losowanie bez powtórek, dopóki pula się nie wyczerpie.
- Wszystkie ustawienia i teksty są na górze `LoadingClient` (`MIN_DURATION`, `TIP_INTERVAL`, `HOLD_AT_100`, `TIPS`).
- Grubość obrysów skaluje się do rozdzielczości (atrybut `BaseThickness` na `UIStroke`).

**Do zrobienia:** test na prawdziwym serwerze i telefonie. Font `Arcade` nie ma wielkiego „Ó”, więc wyświetla „WSKAZóWKA” (do rozważenia inny font).

### 5.2 HUD
**Specyfikacja ✅ kanon** (oryginalna dokumentacja):

| Obszar | Elementy |
|---|---|
| Lewa góra | okrągły awatar bohatera, Level, ukośne paski: HP (czerwony), Mana/Energia (niebieski), postęp EXP |
| Prawa góra | liczniki Złota i Magicznych Kryształów z pixel-artowymi ikonami |
| Krawędzie boczne | nachylone, komiksowe zakładki: Karczma (kufel), Pety (jajko), Tycoon (zamek), Arena (miecze), Ekwipunek (plecak) |
| Dół | hotbar umiejętności i wielki przycisk akcji/ataku |

> **❓ Konflikt z kanonem.** Figma ma 6 przycisków zamiast 5 zakładek: **Teleport, Equipment, Pets** (lewa kolumna) i **Quests, Shop, Guilds** (prawa), z angielskimi napisami. Wdrożona jest wersja z Figmy, na polecenie Game Directora. Kanon pozostaje bez zmian do decyzji (pytanie otwarte #5).

**Wdrożona wersja z Figmy** (layout [node 9:1571](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1571), panel gracza [14:145](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=14-145), przyciski [9:1570](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1570)):
- **ScreenGui `HUD`:** na starcie `Enabled = false`. `ResetOnSpawn = false`, `IgnoreGuiInset = false` i `ScreenInsets = CoreUISafeInsets`, więc nie wchodzi pod pasek Robloxa ani pod notch. `DisplayOrder = 10`.
- **Panel gracza (lewa góra):** x 40, y 30 przy 1920×1080, rozmiar 470×212 px (19,6% wysokości ekranu).
  - `FrameArt`: ramka portretu (PNG).
  - `PortraitSlot`: puste miejsce na awatar.
  - `XPBar` + `XPFill`: zielony pasek XP, ukryty przy 0.
  - `Level`: złota cyfra poziomu.
  - Pigułki **Złota** i **Diamentów** z ikonami. Liczby mają separator tysięcy („125 430”).
- **Przyciski:**
  - Rozmiar 150 px przy 1080p. Figma ma 128 px; przyciski zostały powiększone na prośbę Game Directora.
  - Odstęp 21 px, 40 px od boku, dół kolumny 160 px od dolnej krawędzi.
  - Limity rozmiaru: min 66 px, max 175 px.
  - Na telefonie (dotyk bez klawiatury) kolumny są wyśrodkowane na 55% wysokości, nad joystickiem i przyciskiem skoku.
- **Animacje:**
  - Panel zjeżdża z góry (Back, 0,5 s).
  - Przyciski wjeżdżają z boków (Back, 0,45 s, kolejno co 0,08 s, z fade-in).
  - Hover powiększa przycisk do 1,08 (tylko przy myszy), wciśnięcie zmniejsza do 0,92.
  - Liczniki walut „odliczają” do nowej wartości (0,5 s) z krótkim „pop”, a pasek XP płynnie się wypełnia (0,4 s).
- **Pliki:** [`src/gui/HUD.model.json`](src/gui/HUD.model.json), [`src/client/HUDClient.client.luau`](src/client/HUDClient.client.luau), [`src/server/PlayerStatsDefaults.server.luau`](src/server/PlayerStatsDefaults.server.luau).

**Jeszcze nie ma:** pasków HP i Many/Energii (są w kanonie, nie ma ich w Figmie), portretu bohatera (ViewportFrame), okien otwieranych przyciskami i prawdziwego źródła danych (moduł statystyk / DataStore). Nie było też testu na telefonie ani ręcznego testu hovera.

### 5.3 Okno Karczmy ❓
Dokumentacja twierdzi, że struktura UI Karczmy jest już zaprojektowana, ale nie ma jej w plikach. Gdzie jest, to pytanie otwarte #2. Proponowana hierarchia z wcześniejszej specyfikacji (💡):
```
TavernQuestGui (ScreenGui)
└── MainBoardFrame (UIStroke 4px #000, UICorner)
    ├── HalftoneOverlay (ImageLabel)
    ├── InnkeeperSection: InnkeeperViewport (ViewportFrame), DialogueBubble
    ├── QuestCards (UIListLayout poziomo): QuestCard_Easy (−2°), QuestCard_Medium (1°), QuestCard_Boss (2°)
    └── BottomBar: EnergyBar (ukośny), MugButton (napitek odnawia Energię), StartQuestButton („START QUEST!”)
```

### 5.4 Selektor bohatera 💡
Nie ma go w kanonie. Pomysł: centralny ViewportFrame z postacią (na beczce w karczmie), po lewej wybór **rasy** (zmienia model), po prawej wybór **klasy** (zabawne animacje idle), wielki przycisk „Wyrusz na szlak!”.

## 6. Architektura techniczna

### 6.1 Struktura repozytorium
```
Blocky&Crycket/
├── B&C/                       Sejf Obsidian: mózg projektu, źródło prawdy
│   ├── 00 Start.md            strona startowa sejfu
│   ├── Jak prowadzimy sejf.md zasady sejfu
│   ├── Gra/ Postacie/ Styl/ UI/ Technika/ Produkcja/
│   ├── Badania/               rozeznanie rynku, mechanik i narzędzi (propozycje ze źródłami)
│   ├── Szablony/              szablony notatek i decyzji
│   ├── Źródła/                oryginalna dokumentacja (tylko do odczytu)
│   └── .obsidian/             ustawienia Obsidiana
├── src/                       kod gry synchronizowany przez Rojo
│   ├── server/                → ServerScriptService.Server
│   ├── client/                → StarterPlayer.StarterPlayerScripts.Client
│   ├── shared/                → ReplicatedStorage.Shared
│   └── gui/                   → StarterGui (*.model.json)
├── panel/                     💡 Panel zespołu: okno na sejf, raporty, podgląd 3D, agent (Python, port 8787)
│   ├── serwer.py  bc/  static/   serwer bez zależności, moduły, interfejs
│   ├── narzedzia/             CLI dla agentów: raport.py, migawka.py
│   └── dane/                  wspólne dane panelu: raporty, komentarze, migawki (plik na wpis)
├── swiat/                     💡 mapy z klocków: generator → czesci.json → Blender / Studio / panel
│   ├── demo_lesna_baza/       demo „Leśna baza startowa” (generuj.py, czesci.json, .blend, podglad/)
│   └── postacie/              💡 postacie, pety i ekwipunek z kodu: Blender (siatki, animacje) i postacie z klocków w Studio
├── tools/studio/              skrypty Luau uruchamiane w Studio (rzeczy spoza Rojo)
├── tools/studio_mcp.py        klient MCP Roblox Studio z terminala (bez zależności)
├── tools/studio_buduj.py      buduje w Studio scenę z czesci.json (jeden kontener, do cofnięcia)
├── tools/blender/klocki.py    czesci.json ↔ scena Blendera, rendery podglądu
├── tools/sejf_lint.py         kontrola sejfu: linki, statusy, sekrety
├── tools/*.py                 narzędzia pipeline'u assetów (obróbka, upload, manifest)
├── assets/                    pipeline assetów: manifest.json, refs/, processed/, raw/ (poza Git)
├── docs/                      instrukcja pipeline'u i wcześniejsze prompty (HUD, pasek ładowania)
├── .claude/skills/            skille Claude Code (figma-to-roblox, asset)
├── .mcp.json                  serwery MCP: Higgsfield (pipeline assetów) i Roblox Studio
├── requirements.txt           zależności Pythona pipeline'u
├── dashboard/                 ARCHIWUM: porzucona aplikacja „AI Development Studio”
├── Blocky&Crycket.rbxl        plik miejsca Roblox (binarny)
├── default.project.json       konfiguracja Rojo
├── CLAUDE.md                  instrukcje dla Claude Code
├── DOKUMENTACJA.md            ten plik
└── README.md
```

| Plik | Co robi |
|---|---|
| `src/gui/HUD.model.json` | ScreenGui HUD: panel gracza i dwie kolumny przycisków |
| `src/client/HUDClient.client.luau` | logika HUD: pokazanie po ekranie ładowania, animacje, dane z atrybutów, kliknięcia |
| `src/server/PlayerStatsDefaults.server.luau` | domyślne staty gracza jako atrybuty (tymczasowo, do czasu DataStore) |
| `src/shared/Config.luau` | wspólna konfiguracja serwera i klienta (na razie nazwa gry) |
| `tools/studio/build_loading_screen.luau` | buduje `ReplicatedFirst.LoadingScreen` i `LoadingClient` |
| `src/server/Hello.server.luau`, `src/client/Hello.client.luau`, `src/gui/FigmaTest.model.json` | pliki testowe Rojo i pipeline'u, do usunięcia |
| `.claude/skills/figma-to-roblox/SKILL.md` | przepis dla Claude Code: ramka z Figmy → `.model.json` |

### 6.2 Rojo
[Rojo i struktura projektu](B%26C/Technika/Rojo%20i%20struktura%20projektu.md) · Rojo **7.6.1** · konfiguracja: [`default.project.json`](default.project.json)

| Folder na dysku | Miejsce w Roblox | Typy plików |
|---|---|---|
| `src/server` | `ServerScriptService.Server` | `*.server.luau` → Script, `*.luau` → ModuleScript |
| `src/client` | `StarterPlayer.StarterPlayerScripts.Client` | `*.client.luau` → LocalScript |
| `src/shared` | `ReplicatedStorage.Shared` | `*.luau` → ModuleScript |
| `src/gui` | `StarterGui` | `*.model.json` → jeden ScreenGui na plik |

Zasady:
- Każdy węzeł ma `$ignoreUnknownInstances: true`. Rojo **nie usuwa** niczego, co istnieje tylko w `.rbxl`, ale takiej zawartości **nie widać w plikach**, więc narzędzia plikowe (i Claude) jej nie znają. Rozwiązanie: wyeksportować skrypty w Studio (prawy przycisk → *Save to File*) do `src/`.
- `ReplicatedFirst`, `Workspace`, `Lighting`, `ServerStorage` itd. nie są mapowane. Treść z tych miejsc żyje tylko w `.rbxl`.
- Zmiany z Rojo trafiają do pliku `.rbxl` dopiero po zapisaniu w Studio (**Ctrl+S**).
- Grafik nie da się wgrać przez Rojo. W plikach zostaje tylko `rbxassetid://…`.
- 💡 Proponowana docelowa struktura: `ReplicatedStorage/{Modules, Remotes, Assets, Config}`, `ServerScriptService/{Services, Systems, Data}`, `StarterGui/{HUD, MainMenu, TavernUI, PetUI, InventoryUI, LoadingScreen}`, `ServerStorage/{Templates, Models}`.

### 6.3 Mapa obiektów w grze
| Obiekt w Roblox | Typ | Skąd się bierze | Rola |
|---|---|---|---|
| `ReplicatedFirst.LoadingScreen` | ScreenGui | tylko `.rbxl` (odtwarzany przez `tools/studio/build_loading_screen.luau`) | szablon ekranu ładowania |
| `ReplicatedFirst.LoadingClient` | LocalScript | jak wyżej | logika ekranu ładowania |
| `StarterGui.HUD` | ScreenGui | `src/gui/HUD.model.json` | HUD |
| `StarterGui.FigmaTest` | ScreenGui | `src/gui/FigmaTest.model.json` | test pipeline'u (wyłączony), do usunięcia |
| `StarterPlayerScripts.Client.HUDClient` | LocalScript | `src/client/HUDClient.client.luau` | logika HUD |
| `ServerScriptService.Server.PlayerStatsDefaults` | Script | `src/server/PlayerStatsDefaults.server.luau` | domyślne staty gracza |
| `ReplicatedStorage.Shared.Config` | ModuleScript | `src/shared/Config.luau` | wspólna konfiguracja |
| `ReplicatedStorage.HUDButtonPressed` | BindableEvent | tworzony w locie przez `HUDClient` (tylko na kliencie) | sygnał kliknięcia przycisku HUD |
| `…Server.Hello`, `…Client.Hello` | Script / LocalScript | `src/*/Hello.*.luau` | test połączenia Rojo, do usunięcia |

### 6.4 Start gry krok po kroku
1. **Klient:** `ReplicatedFirst` uruchamia się pierwszy. `LoadingClient` wyłącza domyślny ekran Robloxa i pokazuje `LoadingScreen`.
2. **Serwer:** `PlayerStatsDefaults` przy wejściu gracza ustawia atrybuty `Level = 1, XP = 0, XPMax = 100, Gold = 0, Gems = 0`, o ile nie są już ustawione.
3. **Klient:** `HUDClient` czeka na `PlayerGui.HUD`, podpina się pod zmiany atrybutów i czeka na `LoadingDone`. Najdłużej 30 s; po tym czasie pokazuje HUD mimo braku sygnału i wypisuje ostrzeżenie.
4. **Klient:** `LoadingClient` kończy pasek, ustawia `LoadingDone = true` i wygasza ekran.
5. **Klient:** `HUDClient` odczekuje 0,7 s na koniec wygaszania, ustawia wartości startowe bez animacji, włącza HUD i odpala animacje wejścia.

### 6.5 Kontrakty danych (API między skryptami)
**Atrybuty na obiekcie `Player`:**

| Atrybut | Typ | Kto ustawia | Kto czyta | Domyślnie |
|---|---|---|---|---|
| `Level` | number | serwer (dziś `PlayerStatsDefaults`, docelowo system RPG / DataStore) | `HUDClient` | 1 |
| `XP` | number | serwer | `HUDClient` | 0 |
| `XPMax` | number | serwer | `HUDClient` | 100 |
| `Gold` | number | serwer | `HUDClient` | 0 |
| `Gems` | number | serwer | `HUDClient` | 0 |
| `LoadingDone` | boolean | klient (`LoadingClient`) | `HUDClient` | brak, `true` po ładowaniu |

`LoadingDone` jest ustawiany na kliencie, więc **nie trafia na serwer**. Służy tylko skryptom klienta. Docelowo staty mają pochodzić z DataStore (osobne zadanie, Faza 5).

```lua
-- serwer: zmiana statów (HUD aktualizuje się sam, z animacją)
player:SetAttribute("XP", 40)
player:SetAttribute("Level", 2)
player:SetAttribute("Gold", player:GetAttribute("Gold") + 250)

-- klient: reakcja na kliknięcie przycisku HUD
game:GetService("ReplicatedStorage"):WaitForChild("HUDButtonPressed").Event:Connect(function(name)
	-- "Teleport" | "Equipment" | "Pets" | "Quests" | "Shop" | "Guilds"
end)
```

### 6.6 Format `.model.json` (sprawdzony na Rojo 7.6.1)
- `UDim2` **musi** mieć jawny typ: `{"UDim2": [[xScale, xOffset], [yScale, yOffset]]}`. Zapis bez typu nie przechodzi.
- `UDim`: `{"UDim": [scale, offset]}`.
- Font: `{"Font": {"family": "rbxasset://fonts/families/<Nazwa>.json", "weight": "Bold", "style": "Normal"}}`.
- `ColorSequence`: `{"ColorSequence": {"keypoints": [{"time": 0, "color": [r, g, b]}, …]}}`.
- `Color3` jako `[r, g, b]` (0–1), `Vector2` jako `[x, y]`, enumy jako tekst (`"TextXAlignment": "Left"`).
- Obiekt główny pliku nie ma `Name`: nazwą jest nazwa pliku. Kolejność dzieci w pliku = kolejność rodzeństwa.
- Walidacja: `rojo build default.project.json -o <katalog_tymczasowy>/check.rbxlx`.

### 6.7 Assety (Asset ID)
| Asset | Asset ID | Gdzie użyty |
|---|---|---|
| Key-art ekranu ładowania | `rbxassetid://129202798952612` | `LoadingScreen.Background` |
| Przycisk Teleport | `rbxassetid://133130837278176` | HUD, lewa kolumna |
| Przycisk Equipment | `rbxassetid://72063518170257` | HUD, lewa kolumna |
| Przycisk Pets | `rbxassetid://114125804667140` | HUD, lewa kolumna |
| Przycisk Quests | `rbxassetid://97193506181159` | HUD, prawa kolumna |
| Przycisk Shop | `rbxassetid://101275423490142` | HUD, prawa kolumna |
| Przycisk Guilds | `rbxassetid://133105071163555` | HUD, prawa kolumna |
| Ramka portretu (PNG 416×476) | `rbxassetid://128244393062229` | `HUD.PlayerPanel.FrameArt` |
| Moneta (Złoto) | `rbxassetid://139011825868727` | `HUD.PlayerPanel.GoldIcon` |
| Diament (Gems) | `rbxassetid://130974323293639` | `HUD.PlayerPanel.GemsIcon` |

Ramka portretu ma w PNG wypalony zielony pasek. Pasek XP w HUD jest nałożony dokładnie na niego (współrzędne wyliczone z PNG 416×476), więc ramki nie wolno podmieniać na inaczej przycięty plik.

**Fonty:** `LuckiestGuy` (napisy, liczby, poziom) i `Arcade` (pikselowe wskazówki pod paskiem ładowania).

### 6.8 Skalowanie i urządzenia
- Pozycje i rozmiary są w **Scale** (ułamek ekranu albo rodzica), liczone względem ramki z Figmy (HUD: 1920×1080, pasek ładowania: kadr 2752×1536).
- Kształt pilnują `UIAspectRatioConstraint`, minimalny i maksymalny rozmiar `UISizeConstraint`.
- Grubości obrysów (`UIStroke`) są zapisane w px dla 1080p, a skrypty przeliczają je w grze (HUD według wysokości ekranu, ekran ładowania według szerokości paska). W edytorze, przed uruchomieniem gry, obrysy mają grubość bazową.
- Telefony: HUD respektuje bezpieczne marginesy (`CoreUISafeInsets`), a przyciski przesuwają się nad kontrolki dotykowe.

## 7. Narzędzia
[Narzędzia](B%26C/Technika/Narz%C4%99dzia.md)

### Używane na co dzień
| Narzędzie | Do czego | Uwagi |
|---|---|---|
| **Roblox Studio** | silnik, edycja miejsca, testy (Play Solo, Device Emulator) | plik `Blocky&Crycket.rbxl` |
| **Rojo 7.6.1** | synchronizacja plików `src/` ↔ Studio | `rojo serve` + wtyczka Rojo w Studio (port 34872); `rojo build` do walidacji |
| **VS Code** | edytor kodu i plików projektu | |
| **Claude Code** (rozszerzenie VS Code) | asystent AI: kod Luau, GUI z Figmy, praca w Studio przez MCP, prowadzenie sejfu, Git | instrukcje projektu w [`CLAUDE.md`](CLAUDE.md) |
| **Skill `figma-to-roblox`** | przepis Claude Code na zamianę ramki z Figmy na `.model.json` | [`.claude/skills/figma-to-roblox/SKILL.md`](.claude/skills/figma-to-roblox/SKILL.md) |
| **Figma** + **Figma MCP** | projekty UI (źródło prawdy wyglądu); Claude odczytuje układ, kolory, fonty i zrzuty | konto Figma z miejscem typu *View* wystarcza do odczytu |
| **Roblox Studio MCP** | Claude steruje otwartym Studio: uruchamia Luau, robi zrzuty ekranu, startuje i zatrzymuje Play, czyta Output, symuluje mysz | Studio musi być otwarte |
| **Obsidian** | sejf `B&C`: wiedza, zadania, decyzje, dziennik | szablony w `B&C/Szablony` |
| **Git + GitHub** | wersjonowanie i kopia zapasowa | [repozytorium](https://github.com/przeczkowskyy/Blocky-Crycket) (publiczne), gałąź `main` |
| **Pipeline assetów `/asset`** | grafiki z Higgsfield (MCP) → obróbka → Figma → upload przez Roblox Open Cloud, zawsze z akceptacją Game Directora | w projekcie gry (`.claude/skills/asset`, `tools/*.py`, `assets/`); zainstalowany 12.11.2026, czeka na klucz Open Cloud i logowanie Higgsfield ([Pipeline assetów](B%26C/Technika/Pipeline%20asset%C3%B3w.md)) |
| Python | jednorazowe skrypty pomocnicze Claude (np. generowanie `.model.json`) | nie jest częścią gry |
| 💡 **Panel zespołu** | lokalna strona dla dwóch osób: decyzje i zadania z sejfu, raporty z wdrożeń z akceptacją, podgląd 3D mapy (także z telefonu), agent Claude Code na subskrypcji, głosówki, graf sejfu, analityka | `panel\start.bat` albo `python panel/serwer.py` → `http://127.0.0.1:8787` (start otwiera panel z kluczem lokalnym — tylko wtedy działa agent, git i nowa migawka); instrukcja [`panel/INSTALACJA.md`](panel/INSTALACJA.md); propozycja D-012, czeka na zgodę ([Panel zespołu](B%26C/Technika/Panel%20zespo%C5%82u.md)) |
| 💡 **Klocki: Blender ↔ Roblox** | mapa z prostych brył z jednego pliku `czesci.json`: Blender (podgląd, edycja), Studio (części), panel (model 3D) | `swiat/`, `tools/blender/klocki.py`, `tools/studio_buduj.py`; demo `Workspace/DemoLesnaBaza` ([Klocki — Blender i Roblox](B%26C/Technika/Klocki%20%E2%80%94%20Blender%20i%20Roblox.md)) |
| 💡 **Postacie 3D** | postacie, pety i ekwipunek opisane kodem: w Blenderze siatki ze szkieletem i animacjami, w Studio postacie z części Roblox ze stawami i klipami (bez wgrywania zasobów) | `swiat/postacie/` (`README.md`), `python -B swiat/postacie/roblox_postac.py`; kontener `Workspace/TestPostaci` ([Postacie 3D — Blender i Roblox](B%26C/Technika/Postacie%203D%20%E2%80%94%20Blender%20i%20Roblox.md)) |

### Przewidziane w dokumentacji do tworzenia assetów ✅
| Obszar | Narzędzia |
|---|---|
| UI i grafika 2D | Figma (Design System), Aseprite (pixel art), Midjourney / DALL-E 3 / Higgsfield AI |
| Modele 3D | Blockbench (low-poly z malowanymi teksturami), Meshy AI |

Oryginalna dokumentacja wymienia też Cursor/Copilot do skryptów Luau. W praktyce tę rolę pełni Claude Code.

### Archiwum: `dashboard/`
„AI Development Studio” to lokalna aplikacja webowa (React + Vite, serwer Node 24, SQLite) z 10 agentami AI i własną „pamięcią projektu”. **Porzucona 11.11.2026** na rzecz sejfu Obsidian (decyzja D-008). Zostaje w repo jako archiwum i nie jest rozwijana. Instrukcja uruchomienia jest w [`dashboard/README.md`](dashboard/README.md). Klucz API (`.env`), baza danych (`data/`) i `node_modules/` nie trafiają do repozytorium.

## 8. Workflow

### 8.1 Pierwsze uruchomienie (nowy komputer)
1. Zainstaluj: Roblox Studio, Git, Rojo 7.6.1 (CLI), VS Code z rozszerzeniem Claude Code, Obsidian.
2. Sklonuj repo: `git clone https://github.com/przeczkowskyy/Blocky-Crycket.git`.
3. Zainstaluj wtyczkę Rojo w Studio: `rojo plugin install`.
4. Otwórz `Blocky&Crycket.rbxl` w Roblox Studio.
5. W folderze projektu uruchom `rojo serve`, a w Studio kliknij **Plugins → Rojo → Connect**.
6. W Obsidianie: **Open folder as vault** → folder `B&C`.
7. Otwórz folder projektu w VS Code. Claude Code sam wczyta `CLAUDE.md`. Do pełnego workflow potrzebne są połączenia MCP z Figmą i z Roblox Studio.

### 8.2 Codzienna praca
1. `git pull`, żeby mieć najnowszą wersję.
2. Otwórz Studio z `Blocky&Crycket.rbxl`.
3. Uruchom `rojo serve` i kliknij **Connect** w Studio. Trzeba to robić **po każdym ponownym otwarciu Studio**; bez połączenia zmiany w plikach nie trafiają do gry.
4. Sprawdź w sejfie [Zadania](B%26C/Produkcja/Zadania.md) i [Pytania otwarte](B%26C/Produkcja/Pytania%20otwarte.md).
5. Pracuj z Claude Code. Opisuj, co ma powstać; Claude czyta sejf przed pracą i aktualizuje go po pracy.
6. Na koniec: **Ctrl+S** w Studio, potem commit i push (8.7).

### 8.3 Zasady sejfu
[Jak prowadzimy sejf](B%26C/Jak%20prowadzimy%20sejf.md)
- Każda notatka ma w nagłówku `status`: `kanon`, `propozycja` albo `do-decyzji`.
- Na `kanon` zmienia coś i decyzję zatwierdza (✅) Karol albo Paweł — obaj mają takie same prawa i wystarczy decyzja jednego (D-030, 13.11.2026). Każda decyzja zostaje w logach: podpis `zdecydował: <imię> <data>` w Rejestrze decyzji i wpis w Dzienniku zmian. Zatwierdzonej decyzji się nie przepisuje: dodaje się nową, która ją zastępuje.
- Od 13.11.2026 na sejfie pracuje się też z panelu zespołu (D-028): odpowiedzi na pytania, zadania i statusy decyzji zapisują się do tych samych plików sejfu.
- Gdy prośba jest sprzeczna z kanonem, konflikt trafia do [Pytań otwartych](B%26C/Produkcja/Pytania%20otwarte.md), a kanon się nie zmienia.
- Po pracy aktualizuje się:
  - notatki, których dotyczyła zmiana (np. „Stan implementacji” w `B&C/UI/*.md`),
  - [Zadania](B%26C/Produkcja/Zadania.md), z datą,
  - [Dziennik zmian](B%26C/Produkcja/Dziennik%20zmian.md): wpis na górze.
- Nowe pomysły zapisuje się jako notatki `propozycja` albo wpisy 💡 w [Rejestrze decyzji](B%26C/Produkcja/Rejestr%20decyzji.md).
- Sejf pisze się po polsku i linkuje `[[wikilinkami]]`. Folderu `B&C/Źródła/` nie edytuje się (tylko cytuje), a nowe notatki zaczyna od szablonów z `B&C/Szablony/`.

### 8.4 Nowy ekran z Figmy do Roblox
[Pipeline Figma → Roblox](B%26C/Technika/Pipeline%20Figma%20%E2%86%92%20Roblox.md)
1. **Figma:** prawy przycisk na ramce → **Copy link to selection**.
2. **Claude Code:** wklej link z prośbą, np. „przenieś to do Robloxa”.
3. **Claude czyta projekt** przez Figma MCP: strukturę warstw, kolory, fonty i zrzut ekranu. Gdy trzeba, mierzy pozycje na renderze w pełnej rozdzielczości. Sprawdza też kanon w sejfie, a konflikty zapisuje w Pytaniach otwartych.
4. **Claude buduje:**
   - elementy w obszarach Rojo (GUI w `StarterGui`, skrypty) trafiają do plików: `src/gui/<Nazwa>.model.json` i logika w `src/client/…`;
   - elementy spoza Rojo (np. `ReplicatedFirst`) dostają skrypt budujący w `tools/studio/`, który Claude uruchamia w Studio przez MCP.
5. **Grafiki:** wgrywasz je według 8.5 i podajesz Claude ID.
6. **Test** według 8.6.
7. **Claude aktualizuje sejf**, a Ty zapisujesz Studio (Ctrl+S) i robisz commit.

Zamiany warstw: Frame → `Frame`, tekst → `TextLabel`, przycisk → `TextButton`/`ImageButton`, zaokrąglenia → `UICorner`, obrys → `UIStroke`, gradient → `UIGradient`, auto layout → `UIListLayout`. Proste kształty odtwarza się natywnie, a obrazy wgrywa tylko tam, gdzie to konieczne. Fonty spoza Robloxa zastępuje się najbliższymi. Cienie, rozmycia i tryby mieszania nie mają odpowiedników w Roblox.

### 8.5 Grafiki i Asset ID
1. Wyeksportuj PNG z Figmy: przycięte, z przezroczystym tłem.
2. Studio → **View → Asset Manager → Bulk Import** → zaznacz pliki.
3. Na każdym obrazku: prawy przycisk → **Copy Asset ID**, a potem wklej ID Claude razem z nazwą.
4. Jeśli nie wiadomo, które ID jest którym obrazkiem, Claude wyświetla je w Studio i rozpoznaje po podglądzie.
5. ID są zapisywane w notatce ekranu w sejfie i w tabeli 6.7.

Rojo nie wgrywa grafik. **W trakcie wdrażania:** pipeline `/asset` wgrywa obrazki sam przez Roblox Open Cloud (po akceptacji Game Directora) i zapisuje ID w manifeście. Zob. [Pipeline assetów](B%26C/Technika/Pipeline%20asset%C3%B3w.md) i propozycję D-011.

### 8.6 Testowanie
- **Walidacja plików:** `rojo build default.project.json -o <katalog_tymczasowy>/check.rbxlx` musi się udać.
- **Podgląd w edytorze:** tymczasowa kopia GUI z `Enabled = true` w `StarterGui`, z nazwą zaczynającą się od `_`. Po zrzucie ekranu kopia jest usuwana.
- **Play Solo** (w Studio albo przez MCP): sprawdzanie Output, odczyt stanu obiektów po stronie klienta i serwera, symulacja kliknięć.
- **Testy statów** w Command Bar, w trybie serwera, w trakcie gry:
  ```lua
  game.Players:GetPlayers()[1]:SetAttribute("XP", 50)        -- pasek XP do 50%
  game.Players:GetPlayers()[1]:SetAttribute("Gold", 125430)  -- licznik „125 430”
  game.Players:GetPlayers()[1]:SetAttribute("Level", 2)      -- poziom „2”
  ```
- **Ręcznie:** emulator telefonu (Test → Device), hover myszą, test na prawdziwym serwerze.

### 8.7 Zapisywanie i Git
[Workflow i Git](B%26C/Technika/Workflow%20i%20Git.md) (💡: zalecenia do akceptacji)
- **Repozytorium:** <https://github.com/przeczkowskyy/Blocky-Crycket>, gałąź `main`. Repo jest **publiczne**, więc widzi je każdy.
- **Nie trafia do repo** (`.gitignore`):
  - `node_modules/`;
  - w dashboardzie: `data/` i `.env`;
  - pliki `*.rbxl.lock`;
  - stan okien Obsidiana (`workspace.json`);
  - `.claude/settings.local.json`.
- **Zalecenia:**
  - Commituj po skończonym kawałku pracy, razem z aktualizacją sejfu.
  - Przed commitem zapisz Studio (**Ctrl+S**). Część gry, np. ekran ładowania, istnieje tylko w `.rbxl`.
  - `Blocky&Crycket.rbxl` jest binarny i Git nie umie go scalać. Miejsce naraz edytuje jedna osoba, a przed otwarciem Studio robi się `git pull`.
  - Nigdy nie commituj sekretów (`.env`, kluczy API, tokenów).
  - Claude Code robi commit i push tylko na wyraźną prośbę.
- ❓ Gra jest już opublikowana na Roblox i Studio otwiera wersję z chmury. Czy `.rbxl` w repo dalej aktualizujemy (File → Save to File), jest do ustalenia.

```bash
git pull
git add -A
git commit -m "Krótki opis zmian"
git push
```

### 8.8 Grafiki generowane przez AI
Każdy prompt składa się według instrukcji „Glossy Ink” (sekcja 4): stały początek, zmienny środek, stały koniec i osobny negative prompt. Wynik sprawdza się z zasadami instrukcji, a dopiero potem wgrywa do gry (8.5).

## 9. Decyzje, pytania i roadmapa

### Rejestr decyzji
[Rejestr decyzji](B%26C/Produkcja/Rejestr%20decyzji.md) · ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja

| ID | Decyzja | Status |
|---|---|---|
| D-001 | Obowiązkowy prefiks Style Lock w promptach 2D/UI | ♻️ zastąpiona przez D-027 |
| D-002 | Hybryda trzech estetyk (komiks, voxel, pixel-art) | ✅ (pixel-art ikon i płaski interfejs zastąpione przez D-027) |
| D-003 | Projekty głównych postaci (Rycerz, Kot-Mag, pety) | ✅ |
| D-004 | Aktywna rozgrywka zamiast pasków czasu | ✅ |
| D-005 | Priorytet: Faza 1 — Frontend | ✅ |
| D-006 | Mapowanie Rojo z `$ignoreUnknownInstances` | 🕓 (w praktyce stosowane) |
| D-007 | GUI z Figmy jako pliki `.model.json` | 🕓 (w praktyce stosowane w HUD) |
| D-008 | Sejf Obsidian `B&C` jest mózgiem projektu; dashboard porzucony | ✅ |
| D-009 | Karczma: poziomy misji i Energia | 💡 |
| D-010 | Fazy roadmapy 2–6 | 💡 |
| D-011 | Pipeline assetów `/asset` i moduł `AssetIds` (ID obrazków nie wpisane na sztywno) | 💡 |
| D-027 | Instrukcja promptów „Glossy Ink” zastępuje prefiks Style Lock | ✅ 13.11.2026 |
| D-028 | Panel jako miejsce pracy: zapis do sejfu z panelu | ✅ 13.11.2026 |
| D-030 | Decyzje zatwierdza Karol albo Paweł; każda zostaje w logach | ✅ 13.11.2026 |

Propozycje D-012–D-026 i D-029 (💡) są opisane w rejestrze.

### Pytania otwarte
[Pytania otwarte](B%26C/Produkcja/Pytania%20otwarte.md)
1. Oficjalna pisownia nazwy gry: „Blocky n Crycket” czy „BLOCKY & CRYCKET”?
2. Gdzie jest zaprojektowane drzewo obiektów Karczmy (`.rbxl`, Figma, gdzie indziej)?
3. Czy w `.rbxl` są już skrypty lub GUI, które trzeba wyeksportować do `src/`?
4. Czy propozycje D-006, D-007, D-009, D-010 są zatwierdzone?
5. Przyciski HUD: Figma (6 przycisków, angielskie napisy) czy kanon (5 zakładek)? Gdzie trafią Tycoon i Arena?
6. Diamenty (Gems) w HUD a Magiczne Kryształy w kanonie: ta sama waluta? Waluta premium?

### Roadmapa
[Roadmapa](B%26C/Produkcja/Roadmapa.md)

**▶ Faza 1 — Frontend ✅ (w trakcie)**
- [x] Synchronizacja Rojo
- [x] Pipeline Figma → Roblox
- [x] Ekran ładowania w Roblox
- [ ] Logika HUD (gotowa wersja z Figmy: panel gracza i przyciski; brakuje pasków HP/Many i okien)
- [ ] Architektura UI (StarterGui)
- [ ] Okno Karczmy
- [ ] Modele postaci w ViewportFrame
- [ ] Menu główne

**Fazy 2–6 💡 (do zatwierdzenia)**
- **Faza 2 — System postaci:** postać gracza, podglądy ViewportFrame, statystyki.
- **Faza 3 — Systemy rozgrywki:** walka, questy, lochy, pety, ekwipunek.
- **Faza 4 — Tycoon:** działki, budynki, droppery, dochód pasywny.
- **Faza 5 — Integracja:** systemy serwerowe, DataStore.
- **Faza 6 — Testy i szlif:** QA, wydajność, balans.

### Najbliższe zadania
Z [Zadań](B%26C/Produkcja/Zadania.md), Sprint 1:
- wyeksportować skrypty z `.rbxl` do `src/`;
- uporządkować hierarchię StarterGui;
- moduł statystyk gracza (HP / Mana / EXP / Level) z replikacją do klienta;
- pasek HP w HUD;
- Okno Karczmy (najpierw ustalić, gdzie jest drzewo);
- test HUD na telefonie i ręczny test hovera;
- decyzja w sprawie przycisków HUD.

## 10. Znane problemy i pułapki
- **Znak `&` w nazwie folderu.** Na Windows psuje skróty `.cmd` w `node_modules/.bin` (dotyczy archiwalnego dashboardu: skrypty npm wołają `node` bezpośrednio). W terminalu ścieżki trzeba brać w cudzysłów, a w linkach Markdown na GitHubie `&` zapisuje się jako `%26`.
- **Rojo po ponownym otwarciu Studio.** Wtyczka się rozłącza. Trzeba uruchomić `rojo serve` i kliknąć Connect, inaczej zmiany w plikach nie dochodzą do Studio.
- **`ReplicatedFirst` poza Rojo.** Ekran ładowania istnieje tylko w `.rbxl`. Po zmianach trzeba zapisać Studio (Ctrl+S); źródłem do odtworzenia jest `tools/studio/build_loading_screen.luau`.
- **Treść tylko w `.rbxl` jest niewidoczna dla plików** (pytanie otwarte #3).
- **Font `Arcade` nie ma wielkiego „Ó”**, więc pod paskiem ładowania widać „WSKAZóWKA”.
- **Ostrzeżenia `rbxassetid://203785492 … Asset type does not match`** w Output nie pochodzą z obiektów projektu (sprawdzone 11.11.2026). To najpewniej domyślny zasób Robloxa albo awatara i jest niegroźne.
- **W Studio wszystko ładuje się w ~1 s.** Dlatego ekran ładowania ma minimalny czas wyświetlania.
- **Symulowana mysz przez MCP nie wywołuje `MouseEnter`**, więc hover trzeba sprawdzać ręcznie.
- **Pliki testowe** `Hello.server.luau`, `Hello.client.luau` i `FigmaTest.model.json` są do usunięcia.
- **Windows blokuje `rembg`** (Inteligentna kontrola aplikacji nie wpuszcza biblioteki `numba`). Pipeline assetów sam przełącza się na wycinanie tła flood fill, które dobrze działa przy białym tle.

## 11. Słowniczek
| Pojęcie | Znaczenie |
|---|---|
| **Sejf** | baza notatek Obsidian w folderze `B&C/`; źródło prawdy o projekcie |
| **Kanon / propozycja / do decyzji** | statusy notatek i decyzji (zob. początek dokumentu) |
| **Rojo** | narzędzie synchronizujące pliki z dysku z Roblox Studio |
| **MCP** | Model Context Protocol; pozwala Claude korzystać z Figmy i sterować Roblox Studio |
| **`.rbxl`** | binarny plik miejsca (place) Roblox |
| **ScreenGui** | kontener interfejsu 2D na ekranie gracza |
| **StarterGui / PlayerGui** | `StarterGui` przechowuje szablony GUI; przy wejściu gracza trafiają one do jego `PlayerGui` |
| **ReplicatedFirst** | miejsce w grze ładowane jako pierwsze; tu działa ekran ładowania |
| **Scale / Offset** | rozmiar i pozycja jako ułamek rodzica (Scale) albo w pikselach (Offset) |
| **Asset ID** | numer obrazka wgranego do Robloxa, `rbxassetid://…` |
| **Play Solo** | test gry w Studio z jednym graczem |
| **Atrybut** | własna wartość zapisana na obiekcie Roblox (`SetAttribute` / `GetAttribute`) |
| **Dropper** | budynek w Twierdzy, który pasywnie generuje walutę |
| **Glossy Ink** | obowiązująca instrukcja składania promptów do grafik (D-027) |
| **Style Lock** | dawny prefiks promptów do grafik 2D/UI, zastąpiony przez Glossy Ink |

## 12. Historia zmian
Pełna historia: [Dziennik zmian](B%26C/Produkcja/Dziennik%20zmian.md).
- **11.11.2026:**
  - konfiguracja Rojo i skill `figma-to-roblox`;
  - zbudowany i porzucony dashboard; sejf Obsidian ustanowiony mózgiem projektu (D-008);
  - ekran ładowania w Roblox: key-art i natywny pasek z Figmy, potem minimalny czas ładowania i rotujące wskazówki;
  - HUD: najpierw 6 przycisków (160 px, wyśrodkowane), potem pełny HUD z Figmy (panel gracza i przyciski 128 px niżej przy krawędzi), na koniec przyciski powiększone do 150 px.
- **12.11.2026:** projekt w repozytorium GitHub, ten dokument; instalacja pipeline'u assetów `/asset`.
- **13.11.2026 (wieczór, Karol i Paweł z Claude Code u Karola):** ✅ D-030 — decyzje zatwierdza Karol albo Paweł, wystarczy jeden, każda zostaje w logach; ✅ D-027 — instrukcja „Glossy Ink” zastępuje prefiks Style Lock; ✅ D-028 — panel jako miejsce pracy, zapis do sejfu z panelu włączony; propozycja D-024 o walce zmieniona na „trzy długości”; import siatek sprawdzony na Rycerzu (postać R15 z 15 części w `Workspace/TestPostaci`).
- **13.11.2026 (popołudnie, Claude Code u Karola):** 💡 postacie, pety i ekwipunek z kodu (`swiat/postacie/`: 6 postaci, 3 zestawy, 8 broni, 20 klipów animacji) oraz te same postacie w Studio jako postacie z klocków ze stawami (`Workspace/TestPostaci`), animacje sprawdzone w trybie Edit i Play; import siatek nie sprawdzony (propozycja D-029, pytanie 24); 💡 zapis do sejfu z panelu (D-028, wyłączony do decyzji).
- **13.11.2026 (noc i poranek, Claude Code u Karola):** diagnoza całego pomysłu (dziś 3,8/10) i propozycja v2 „krzywy montaż” z uczciwą oceną 6,0/10 i planem pomiarów (`B&C/Gra/*v2*.md`, `B&C/Badania/Diagnoza pomysłu 2026-11-13.md`; propozycje D-019–D-027, pytania 16–22); 💡 mapa v2 „Krzywe Miasteczko” i biblioteka krzywych brył (`swiat/biblioteka/`, `swiat/krzywe_miasteczko/`, `Workspace/KrzyweMiasteczko`); 💡 test cutscenki walki w samym Roblox (`swiat/test_walki_roblox/`, `Workspace/TestWalki`); panel: zakładka Assety, telemetria gry (`src/server/Telemetria`, bezwładna do włączenia), tunel sprawdzony naprawdę; instrukcja promptów „Glossy Ink” od Game Directora (`B&C/Styl/`). Wszystko jako propozycje do zatwierdzenia.
- **12.11.2026 (wieczór, Claude Code u Karola):** rozmowa o grze spisana i skomentowana, sześć notatek badawczych i ocena potencjału (`B&C/Badania/`), propozycje D-012–D-018 i pytania 7–14; 💡 panel zespołu (`panel/`); 💡 pipeline klocków i demo mapy „Leśna baza startowa” w Blenderze i w Studio (`swiat/`). Wszystko jako propozycje do zatwierdzenia.
