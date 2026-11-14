---
status: propozycja
tags: [ui, teleport, mapa, prompty]
źródło: "polecenie Game Directora 2026-11-12 (referencje: zrzuty mapy miasta z gry-inspiracji)"
---
# Mapa teleportacji

## Opis
Po kliknięciu przycisku **Teleport** w [[HUD]] na środku ekranu otwiera się okno z ilustrowaną **mapą miasteczka 2D** w ramce. Nad każdym budynkiem jest **przycisk-znacznik (pin)**. Kliknięcie pinu przenosi gracza do tej lokacji. Okno zamyka **X w prawym górnym rogu**.

Zrzuty z gry-inspiracji pokazują tylko **zasadę działania** (mapa i piny nad budynkami). Nie kopiujemy ich układu ani budynków. Nasze miasto ma własne budynki wynikające z systemów gry.

## Lokacje (propozycja, do potwierdzenia)
Układ na mapie według promptu-wytycznej Game Directora (2026-11-13). Zmiana względem wersji z 12.11: zamiast Targu jest **Kuźnia** obok Siedziby Gildii.

| # | Budynek na mapie | Miejsce na mapie | System | Ikona w pinie | Akcent pinu |
|---|---|---|---|---|---|
| 1 | Karczma | lewa góra | [[Karczma (Questy)]] | kufel piwa z pianą | pomarańcz `#FFC06A` |
| 2 | Arena | środek | [[Arena (PvP)]] | skrzyżowane miecze na tarczy | czerwień `#EC6E66` |
| 3 | Portal do lochów | środek, obok Areny | mini-dungeony ([[Karczma (Questy)]]) | wirujący złoty portal | cyjan `#41F5D6` |
| 4 | Twierdza gracza | prawa góra | [[Twierdza (Tycoon)]] | wieża zamku z fioletowym kryształem | złoto `#F2C24A` |
| 5 | Siedziba Gildii | lewy dół | Guilds (HUD) | sztandar z herbem | fiolet `#BE78F0` |
| 6 | Kuźnia | lewy dół, obok Gildii | ulepszanie (okno Kowala z przykładu instrukcji) | kowadło z młotem | granit `#5A6A92` |
| 7 | Zagroda petów | prawy dół | [[Pety]] | świecące jajo | zieleń `#78D2A4` |

Targ (Shop z HUD) nie ma budynku na mapie: Shop otwiera się z HUD ([[Pytania otwarte]] #28).

## Wygląd i zachowanie (natywnie w Roblox)
- **Otwarcie:** tło przyciemnione (czarne, przezroczystość ~0,45). Ramka wskakuje z efektem *pop* (skala 0,85 → 1,0, `Back` Out, 0,25 s). Piny pojawiają się po kolei z lekkim podskokiem.
- **Proporcje:** obraz 16:9 z `UIAspectRatioConstraint`. Okno zajmuje ~90% szerokości na PC i 100% na telefonie.
- **Piny:** `ImageButton` pozycjonowane w **Scale względem obrazu mapy**, więc trzymają się budynków przy każdej rozdzielczości. Nazwa lokacji natywnie pod pinem (Luckiest Guy, obrys `#1A1410`), nie w obrazku.
- **Stany pinu:** *hover* (skala 1,1 i lekkie bujanie ±3°), *wciśnięty* (skala 0,95), *zablokowany* (szarość, natywna kłódka i dymek „Od poziomu X”), *nowość* (natywny wykrzyknik „!”).
- **X:** jeśli jest wypalony w ramce, nad nim leży przezroczysty `TextButton`. Pewniejsza opcja: osobna grafika X jako `ImageButton`. Zamykanie także klawiszem `Esc`/`B` i kliknięciem w przyciemnione tło.
- **Teleport:** klient wysyła `RemoteEvent` z ID lokacji. Serwer sprawdza odblokowanie i cooldown, potem przenosi postać na `CFrame` punktu lokacji w tym samym miejscu. Inne place obsługuje `TeleportService`. Ekran przejścia: krótkie zaciemnienie z iskierkami.

## Prompty (format [[Instrukcja promptów — Glossy Ink|Glossy Ink]])
Stały początek, stały koniec (dla mapy w wersji z wyjątku) i stały negative są skopiowane 1:1. Zmienia się tylko środek. Szablony dla wszystkich kategorii są w skillu `/asset` (`.claude/skills/asset/references/prompt-templates.md`).

**Ustawienia Higgsfield:**
- model `nano_banana_2_1`;
- referencja stylu `assets/refs/KeyArt_ref.jpg` (ekran ładowania);
- mapa: 16:9, `4k`, bez wycinania tła;
- piny: arkusz 21:9, `4k`, białe tło (potem cięcie na 7 plików);
- negative dopisany na końcu promptu, bo model nie ma na niego osobnego pola.

### Prompt 1: mapa miasteczka w ramce
```
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Layout (Teleport Town Map Popup): A wide 16:9 popup window filling the whole image, with a thin wooden-plank border, a thin delicate brushed-gold inner rim and small corner rivets, and a blank empty wooden title plaque at the top center with NO text on it. Inside: a high-angle isometric world map perspective of a cozy original medieval fantasy hub town at sunset, buildings shrunk by 30-40% so there is lots of space around them, wide cobblestone paths, plenty of green grass, blocky trees and bushes between locations, a small blue river with a wooden bridge. Top-Left: a crooked red-roofed Tavern with warm glowing yellow windows and barrels. Center: a circular stone PvP Colosseum Arena lit by flaming braziers, next to it a glowing golden swirling Dungeon Portal chained to the ground. Top-Right: a fairytale Tycoon Castle on a cliff with a giant floating purple crystal and a waterfall. Bottom-Left: a medieval Guild Hall with blue banners and, beside it, a Blacksmith forge with an anvil and a glowing furnace. Bottom-Right: a fenced Pet Habitat pen with glowing eggs and green grass. Vibrant Roblox colors: turquoise, orange, emerald, red, royal purple, gold. Completely clean buildings with NO floating map pins, NO padlocks and NO labels or text on the map; keep the open space directly above each building calm for markers added later in the game engine. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. The whole map is enclosed in a thin wooden frame with a glossy red "X" close button in the top-right corner, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### Prompt 2: arkusz 7 pinów lokacji
```
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Layout (Map Pin Button Sprite Sheet): 7 separate map location marker buttons in one straight row with wide even white gaps between them, all exactly the same size and shape. Each one: an upright upside-down teardrop map pin with a thin delicate brushed-gold rim, a thin colored inner ring, a round glossy jelly face in the same color and a glassy shine on its upper half, with one chunky painterly icon centered on the face. Pins in order from left to right: 1) orange #FFC06A face with a foaming beer tankard; 2) red #EC6E66 face with crossed swords over a round shield; 3) cyan #41F5D6 face with a swirling golden portal; 4) gold #F2C24A face with a small castle tower and a purple crystal; 5) purple #BE78F0 face with a banner bearing a crest; 6) slate blue #5A6A92 face with an anvil and a hammer; 7) green #78D2A4 face with a glowing spotted egg. NO text, letters or numbers on any pin. Each pin is fully separate, nothing overlapping or touching. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

## Wskazówki do generowania
- Jako referencję stylu podawaj **nasze** assety (`assets/refs/KeyArt_ref.jpg`), nie zrzuty cudzej gry. Inaczej model skopiuje cudze budynki.
- Mapa: 4 warianty, wybieramy wg checklisty [[Style Lock]]. Piny: jeden arkusz, po wybraniu wariantu tniemy go na 7 plików `Pin*`.
- Ramka jest lekka (cienkie drewno ze złotą obwódką), bo instrukcja zakazuje ciężkich kamiennych ram. Prompt-wytyczna Game Directora miał „chunky stone-and-wood border”; zostawiona jest cienka ramka z wyjątku dla map (do potwierdzenia, [[Pytania otwarte]] #28).
- Jeśli X lub ramka wyjdą słabo, generujemy je osobno: ramkę jako panel do 9-slice, a X jako osobny przycisk.
- Wcześniejsze próby z GPT Image (`assets/raw/TeleportMap`, `assets/raw/PinTavern`) są nieaktualne.

## Do ustalenia
- Lista lokacji (tabela wyżej) i ich polskie lub angielskie nazwy (zob. [[Pytania otwarte]] #5 i #28).
- Które lokacje są zablokowane na start i od jakiego poziomu.
- Teleport w obrębie jednego place czy osobne place (`TeleportService`)?

## Stan implementacji
- [x] Specyfikacja i prompty (2026-11-12)
- [ ] Wygenerowana mapa z ramką
- [ ] Wygenerowane piny (7)
- [ ] ScreenGui `TeleportMapGui` w `src/gui`
- [ ] Logika teleportu (RemoteEvent + serwer)

## Powiązane
- [[HUD]] · [[Kierunek artystyczny]] · [[Style Lock]] · [[Pipeline assetów]] · [[00 Start]]
