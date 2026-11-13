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
| # | Budynek na mapie | System | Ikona w pinie (pixel-art) | Akcent pinu |
|---|---|---|---|---|
| 1 | Karczma | [[Karczma (Questy)]] | kufel piwa z pianą | pomarańcz `#FFC06A` |
| 2 | Arena | [[Arena (PvP)]] | skrzyżowane miecze na tarczy | czerwień `#EC6E66` |
| 3 | Twierdza gracza | [[Twierdza (Tycoon)]] | klockowa wieża zamku + moneta | złoto `#F2C24A` |
| 4 | Zagroda petów | [[Pety]] | łapka z serduszkiem | zieleń `#78D2A4` |
| 5 | Targ | Shop (HUD) | sakiewka złota | granit `#5A6A92` |
| 6 | Siedziba Gildii | Guilds (HUD) | sztandar z herbem | fiolet `#BE78F0` |
| 7 | Portal do lochów | mini-dungeony z [[Karczma (Questy)\|Karczmy]] | wirujący portal | cyjan `#41F5D6` |

## Wygląd i zachowanie (natywnie w Roblox)
- **Otwarcie:** tło przyciemnione (czarne, przezroczystość ~0,45). Ramka wskakuje z efektem *pop* (skala 0,85 → 1,0, `Back` Out, 0,25 s). Piny pojawiają się po kolei z lekkim podskokiem.
- **Proporcje:** obraz 16:9 z `UIAspectRatioConstraint`. Okno zajmuje ~90% szerokości na PC i 100% na telefonie.
- **Piny:** `ImageButton` pozycjonowane w **Scale względem obrazu mapy**, więc trzymają się budynków przy każdej rozdzielczości. Nazwa lokacji natywnie pod pinem (Luckiest Guy, obrys `#1A1410`), nie w obrazku.
- **Stany pinu:** *hover* (skala 1,1 i lekkie bujanie ±3°), *wciśnięty* (skala 0,95), *zablokowany* (szarość, natywna kłódka i dymek „Od poziomu X”), *nowość* (natywny wykrzyknik „!”).
- **X:** jeśli jest wypalony w ramce, nad nim leży przezroczysty `TextButton`. Pewniejsza opcja: osobna grafika X jako `ImageButton`. Zamykanie także klawiszem `Esc`/`B` i kliknięciem w przyciemnione tło.
- **Teleport:** klient wysyła `RemoteEvent` z ID lokacji. Serwer sprawdza odblokowanie i cooldown, potem przenosi postać na `CFrame` punktu lokacji w tym samym miejscu. Inne place obsługuje `TeleportService`. Ekran przejścia: krótkie zaciemnienie z iskierkami.

## Prompt 1: ramka z mapą miasteczka (Higgsfield, 16:9, najwyższa rozdzielczość, bez wycinania tła)
```
Game UI screen, hybrid of hand-inked comic book style and vibrant Roblox aesthetic: thick solid black uniform outlines on every shape, painterly cel shading with 2-3 tones, subtle pop-art halftone dot texture inside shadows, vibrant saturated colors, glossy white highlights on the top-left of objects, exaggerated chunky proportions, slightly crooked asymmetrical cartoon architecture built from blocky voxel and low-poly shapes, tiny pixel-art sparkles as accents.

A wide 16:9 ornate fantasy game window filling the entire image. FRAME: a thick chunky border of dark carved wood planks (#4A2D17 to #9A6532) wrapped in gold metal trim (#FFE07A to #D18A12) with big rivets, reinforced metal corner caps each holding a small faceted amethyst crystal (#B54BF0), slightly uneven comic-book silhouette, a thin dark navy bevel (#1A2034) along the inner edge. At the top center of the frame, an empty blank wooden title plaque with gold trim and no writing on it. In the top-right corner, overlapping the frame edge, a round glossy close button: thick gold rim, red (#EC6E66) glossy center, a bold chunky white X symbol with black outline.

INSIDE THE FRAME: an illustrated bird's-eye isometric map (about 35 degrees from above) of a cozy original medieval fantasy hub town at golden hour. Seven clearly separated landmarks, each with a distinct color and silhouette, connected by winding cobblestone paths:
1) a crooked two-story timber tavern with warm glowing windows, barrels, a wooden quest notice board out front and a giant hanging tankard sign without text;
2) a round stone arena with red and gold banners, a sand floor and crossed-sword ornaments;
3) a small blocky player castle keep on a hill with wooden scaffolding, piles of gold coins and glowing purple crystals;
4) a pet sanctuary: a green fenced meadow with a cute red wooden barn, a small dog, a blue slime and a baby red dragon playing;
5) a market square with colorful striped stall awnings, crates and coin sacks;
6) a tall stone guild hall with purple banners and a big round wooden door;
7) an ancient stone archway with a swirling cyan (#41F5D6) magic portal set into rocky hills at the edge of town.
Around them: a central plaza with a fountain, a blue river (#1BA9DA) with a wooden bridge, blocky voxel trees, lanterns, a few tiny Roblox-style blocky villagers. Warm sunset sky glow, light from the top-left, warm orange window light, soft magical purple and cyan accents. Keep the open space directly above each landmark calm and uncluttered for map markers that will be added later.

Avoid: text, letters, numbers, words, logos, watermark, map pins, map markers, location icons, padlocks, any UI except the close X button, photorealism, 3D render, PBR materials, thin lines, blurry edges, washed-out pastel colors, gloomy night palette, anime style, gore, blood, characters or buildings from existing games or brands.
```

## Prompt 2: przycisk lokacji (pin), jeden prompt na lokację (1:1, białe tło → wycięcie)
Podmień `{ICON}` i `{ACCENT}` według tabeli lokacji. Wszystkie piny generuj z tym samym seedem.
```
Game UI component, hybrid of hand-inked comic book style and vibrant Roblox aesthetic: thick solid black uniform outlines, painterly cel shading with 2-3 tones, subtle pop-art halftone dot texture, vibrant saturated colors, chunky exaggerated proportions.

A single chunky map location marker button shaped like an upside-down teardrop map pin standing upright, slightly tilted about 3 degrees for comic energy. Thick gold metal rim (#FFE07A to #F2C24A to #D18A12) with a glossy white highlight on the top-left and two small rivets. Inside the rim, a thin {ACCENT} colored inner ring, then a round dark navy face (#2B3552 to #1A2034) with subtle halftone dots and a glassy shine on its upper half. Centered on the navy face: a crisp sharp pixel-art icon of {ICON}, drawn with hard square pixels and its own 1-pixel black outline, bright and readable. Two or three tiny pixel-art sparkles around the pin. A soft dark oval shadow directly under the pin's tip. Front view, centered, the pin fills about 80% of the frame height, isolated on a pure flat white #FFFFFF background, nothing touching the image edges.

Avoid: text, letters, numbers, words, logo, watermark, padlock, exclamation mark, background scenery, gradient or colored background, drop shadow on the background, photorealism, 3D render, thin lines, blurry edges, washed-out pastel colors, anime style.
```

## Wskazówki do generowania
- Jako referencję stylu w Higgsfield podawaj **nasze** assety (`assets/refs/KeyArt_ref.jpg`, `assets/processed/Teleport.png`), nie zrzuty cudzej gry. Inaczej model skopiuje cudze budynki.
- Mapa: 4 warianty, wybieramy wg checklisty [[Style Lock]]. Piny: najpierw jeden (Karczma), po akceptacji reszta z tym samym seedem.
- Jeśli X lub ramka wyjdą słabo, wygenerować je osobno: ramka jako panel do 9-slice, a X jako osobny przycisk.

## Do ustalenia
- Lista lokacji (tabela wyżej) i ich polskie lub angielskie nazwy (zob. [[Pytania otwarte]] #5 i #25).
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
