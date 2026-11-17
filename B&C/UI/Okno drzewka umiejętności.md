---
status: propozycja
tags: [ui, drzewko, prompty, higgsfield]
źródło: "polecenie Pawła 2026-11-15 (okno drzewka: Player / Fortress / Pets); decyzje D-055, D-056, D-057"
---
# Okno drzewka umiejętności

## Opis
Okno drzewek z D-055/D-056 według polecenia Pawła z 15.11. To **propozycja układu**; zasady kupowania węzłów są w [[Drzewko umiejętności postaci]] (węzły za Gemy, D-057).

- **Wejście:** okrągła ikonka drzewa w [[Okno ekwipunku]], w prawym górnym rogu ramki portretu gracza. Kliknięcie otwiera okno.
- **Wykrzyknik** nad ikonką, gdy gracz może kupić jakiś węzeł (stać go na najtańszy dostępny).
- **Okno:** jedna karta, nagłówek „SKILL TREE”, trzy zakładki **Player / Fortress / Pets**. Napisy natywnie w Roblox.
- **Otwiera się od razu na zakładce Player** — bez dodatkowego pustego okna ani ekranu wyboru (Paweł, 15.11).

| Zakładka | Tło karty | Gałęzie |
|---|---|---|
| **Player** (domyślna) | Roblox-rycerz | **Stats** — % do statystyk (na start klasa Wojownik) · **Income** — % do zdobywanego Złota, EXP i Diamentów · **Skills** — umiejętności walki aktywne i pasywne, sloty (D-055) |
| **Fortress** | mały kanciasty zamek | **Training Center** — szybsze zdobywanie statystyk w budynku · **Income** — więcej surowców, czasowe gainy · **Timer** — krótszy czas budowy |
| **Pets** | gniazdo z kolorowymi jajkami | **Pet Stats** — % do statystyk petów (m.in. PET INTELLIGENCE i PET DEXTERITY — Paweł 15.11) · **Eggs** — szybsze jajka, kilka naraz · **Luck** — lepsze szanse w jajkach · **Capacity** — więcej petów przy graczu i większy ekwipunek petów |

Ikony węzłów to okrągłe medaliony, po 6 na gałąź. Wartości („+5% Gold”) są tekstem natywnym, nie w grafice.

### Układ: przesuwana mapa węzłów (Paweł, 15.11)
Zamiast równych rzędów — **rozgałęziona mapa**, którą przeciąga się myszką albo palcem w obrębie karty (tło karty stoi w miejscu).
- W środku węzeł startowy zakładki (Player: ikona drzewa), od niego gałęzie w różne strony: Stats w lewo, Income w prawo, Skills w dół; gałęzie się rozwidlają.
- **Kupiony** węzeł: pełny kolor, licznik poziomu („1/5”), złota linia do rodzica. **Dostępny** (rodzic kupiony): kolor, nazwa i cena w Gemach. **Ukryty**: ciemne kółko „?” — sąsiad dostępnego. Dalsze węzły są niewidoczne, dopóki gracz do nich nie dojdzie.
- Ikony powtarzają się z numerem (STR I, STR II…), więc mapa może być duża bez nowych grafik.
- **Start (Paweł, 15.11):** na początku widać tylko węzeł centralny zakładki — mini rycerz (Player), mini twierdza (Fortress), gniazdo z jajkami (Pets) — i trzy „?” wokół niego. Gracz kupuje go za niewielką liczbę Diamentów; dopiero wtedy odkrywają się gałęzie.
- Cena przy węźle: nasza ikona Diamentu z [[HUD]] + liczba (nie symbol).
- Zakryty węzeł: osobna ikona „?” (`NodeHidden`).
- Makieta: Figma, strona „Equipment Panel”, ramka „SkillTreeWindow — mapa” (node 33:78).

## Prompty (Higgsfield, format [[Instrukcja promptów — Glossy Ink|Glossy Ink]])
Ustawienia dla każdego: model **Nano Banana 2.1**, referencja stylu `assets/refs/KeyArt_ref.jpg`, proporcje i rozdzielczość jak w tabeli. Części stałe są skopiowane 1:1 z szablonów skilla `/asset`; negative jest ostatnim akapitem promptu, bo model nie ma osobnego pola.

**Gdzie zapisać wynik:** wybrany obraz wrzuć do `assets/raw/<Nazwa>/` (np. `assets/raw/IconsPlayerStats/v1.png`). Dalej skill `/asset` tnie arkusze, wrzuca do Figmy i — po „tak” — do Roblox.

| Nazwa | Co | Proporcje | Rozdzielczość |
|---|---|---|---|
| `SkillTreeButtons` | Przycisk drzewka + wykrzyknik (2 ikony na arkuszu) | 3:2 | 2k |
| `SkillTreeFrame` | Okno Skill Tree: nagłówek + 3 zakładki, puste wnętrze | 4:3 | 4k |
| `SkillTreeBgPlayer` | Tło karty Player: Roblox-rycerz | 3:2 | 4k |
| `SkillTreeBgFortress` | Tło karty Fortress: mały kanciasty zamek | 3:2 | 4k |
| `SkillTreeBgPets` | Tło karty Pets: gniazdo z kolorowymi jajkami | 3:2 | 4k |
| `IconsPlayerStats` | Player → Stats (Wojownik): % do STR, CONST, INT, DEX, LUCK, ARMOR | 3:2 | 2k |
| `IconsPlayerIncome` | Player → Income: Złoto, EXP, Diamenty | 3:2 | 2k |
| `IconsPlayerSkills` | Player → Skills (Wojownik): umiejętności aktywne i pasywne, sloty | 3:2 | 2k |
| `IconsFortressTraining` | Fortress → Training Center: zdobywanie statystyk | 3:2 | 2k |
| `IconsFortressIncome` | Fortress → Income: surowce i czasowe gainy | 3:2 | 2k |
| `IconsFortressTimer` | Fortress → Timer: krótsza budowa | 3:2 | 2k |
| `IconsPetsStats` | Pets → Pet Stats: % do statystyk petów | 3:2 | 2k |
| `IconsPetsEggs` | Pets → Eggs: szybsze jajka, kilka naraz | 3:2 | 2k |
| `IconsPetsLuck` | Pets → Luck: lepsze szanse w jajkach | 3:2 | 2k |
| `IconsPetsCapacity` | Pets → Capacity: więcej petów przy graczu, większy ekwipunek petów | 3:2 | 2k |

### SkillTreeButtons — Przycisk drzewka + wykrzyknik (2 ikony na arkuszu)
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 2 separate round game UI buttons side by side with a wide white gap between them, both fully separate and not touching. Left: a round glossy button with a thin delicate brushed-gold rim and an emerald green #4CB33C jelly face with a glassy shine on its upper-left, centered on it a chunky cartoon tree with a thick brown trunk, a round leafy crown and three tiny glowing gold orbs hanging in the leaves, the whole tree fully inside the circle. Right: a smaller round notification badge, a glossy red #EC6E66 jelly circle with a thin gold rim and one bold chunky white exclamation mark with a thick black outline in its center. no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### SkillTreeFrame — Okno Skill Tree: nagłówek + 3 zakładki, puste wnętrze
Proporcje 4:3, 4k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Layout (Skill Tree Window): ONE single unified connected card window with a thin delicate brushed-gold rim and thin wooden strips, a blank wooden banner plaque on the top center without text, and a glossy red rounded-square "X" button in the top-right corner. Directly under the banner, a row of 3 wide blank glossy jelly tabs without text attached to the top edge of the content area like folder tabs, left to right: orange #FFC06A, royal purple #BE78F0, green #78D2A4, each with a thick black outline. Below the tabs: one large EMPTY content area with a soft light parchment-beige inner panel and a subtle inner shadow, completely empty, nothing drawn inside, it will be filled by the game engine. No text, no letters, no numbers, no icons inside the content area. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### SkillTreeBgPlayer — Tło karty Player: Roblox-rycerz
Proporcje 3:2, 4k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Wide 3:2 soft calm background illustration for the inside of a game skill tree card, a warm medieval house interior with wooden beams, stone walls and soft candlelight glow, in the center a big friendly blocky Roblox-style knight with a steel helmet, steel armor, a sword and a round wooden shield with a gold rim, standing heroically, painted slightly faded and low-contrast so that small round icons placed on top later stay readable, the main subject in the center with lots of calm empty space around it, no UI elements, no icons, no frame, no text, no letters, no numbers, no logo, no watermark, full illustrated background. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### SkillTreeBgFortress — Tło karty Fortress: mały kanciasty zamek
Proporcje 3:2, 4k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Wide 3:2 soft calm background illustration for the inside of a game skill tree card, a small chunky blocky cartoon castle keep with slightly crooked square towers, red and gold banners and a wooden gate, standing on a little green hill with a few blocky voxel trees, warm sunset sky, painted slightly faded and low-contrast so that small round icons placed on top later stay readable, the main subject in the center with lots of calm empty space around it, no UI elements, no icons, no frame, no text, no letters, no numbers, no logo, no watermark, full illustrated background. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### SkillTreeBgPets — Tło karty Pets: gniazdo z kolorowymi jajkami
Proporcje 3:2, 4k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Wide 3:2 soft calm background illustration for the inside of a game skill tree card, a big cozy bird nest woven from twigs and straw resting on soft green grass, holding many colorful spotted eggs in blue, pink, gold, green and purple, a few tiny glossy sparkles, warm soft light, painted slightly faded and low-contrast so that small round icons placed on top later stay readable, the main subject in the center with lots of calm empty space around it, no UI elements, no icons, no frame, no text, no letters, no numbers, no logo, no watermark, full illustrated background. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPlayerStats — Player → Stats (Wojownik): % do STR, CONST, INT, DEX, LUCK, ARMOR
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a royal purple #B54BF0 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a steel sword (strength); 2) a big red heart (constitution and health); 3) an open blue spell book (intelligence); 4) a winged leather boot (dexterity); 5) a green four-leaf clover (luck); 6) a round steel shield with a gold rim (armor). Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPlayerIncome — Player → Income: Złoto, EXP, Diamenty
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a emerald green #4CB33C jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a shiny gold coin; 2) a glowing yellow experience star; 3) a cyan faceted diamond gem; 4) a bulging brown coin pouch; 5) an open treasure chest full of gold; 6) an hourglass with golden sand. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPlayerSkills — Player → Skills (Wojownik): umiejętności aktywne i pasywne, sloty
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a red #EC6E66 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a steel sword with a wide glowing white slash arc; 2) a heavy war hammer smashing down onto a cracked armor plate; 3) a clenched fist made of grey stone with a glowing rune; 4) a raised round shield with a bright blocking spark; 5) a knight helmet with shouting sound waves; 6) an empty golden skill slot frame with a small open padlock. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsFortressTraining — Fortress → Training Center: zdobywanie statystyk
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a orange #FFC06A jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a wooden training dummy; 2) a heavy iron dumbbell; 3) two crossed wooden practice swords; 4) an archery target with an arrow in the center; 5) a sword on an anvil with sparks; 6) a flexing arm with a green up arrow. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsFortressIncome — Fortress → Income: surowce i czasowe gainy
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a green #78D2A4 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a pickaxe over a chunk of gold ore; 2) stacked wooden logs with an axe; 3) a pile of grey stone blocks; 4) a glowing purple magic crystal cluster; 5) a mine cart full of ore; 6) a round clock with a gold coin in front of it. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsFortressTimer — Fortress → Timer: krótsza budowa
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a sky blue #8FDDF4 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) an hourglass with a yellow lightning bolt; 2) a builder hammer crossed with a small clock; 3) a stopwatch with a speed arrow; 4) a small blocky building with wooden scaffolding; 5) a small construction crane lifting a block; 6) two gears with a fast-forward arrow. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPetsStats — Pets → Pet Stats: % do statystyk petów
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a red #EC6E66 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a paw print with a small sword; 2) a paw print with a heart; 3) a paw print with a shield; 4) a paw print with a lightning bolt; 5) a paw print with a four-leaf clover; 6) a paw print with a gold star. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPetsEggs — Pets → Eggs: szybsze jajka, kilka naraz
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a sky blue #8FDDF4 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a spotted egg with a yellow lightning bolt; 2) three spotted eggs in a row; 3) a spotted egg in front of a small clock; 4) a cracking egg with sparkles; 5) a warm glowing lamp over an egg; 6) a woven basket full of eggs. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPetsLuck — Pets → Luck: lepsze szanse w jajkach
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a emerald green #4CB33C jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) a shiny golden egg; 2) a rainbow striped egg; 3) an egg with a four-leaf clover; 4) a white dice next to an egg; 5) a shooting star over an egg; 6) an egg wearing a small gold crown. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

### IconsPetsCapacity — Pets → Capacity: więcej petów przy graczu, większy ekwipunek petów
Proporcje 3:2, 2k.
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo). Sprite sheet of 6 separate round skill tree node icons arranged in a clean grid of 3 columns and 2 rows with wide even white gaps between them, all exactly the same size and shape. Each icon: a round glossy medallion with a thin delicate brushed-gold rim and a slate blue #5A6A92 jelly face with a glassy shine on its upper-left, and one chunky painterly symbol centered fully inside the circle. Symbols in reading order (top row left to right, then bottom row left to right): 1) two paw prints side by side; 2) a pet collar with a heart tag; 3) a cozy round pet bed; 4) a big backpack with a paw print; 5) a stack of wooden pet crates; 6) a small wooden dog house. Each icon is fully separate, nothing overlapping or touching, every symbol fully inside its circle, no text, no letters, no numbers, no logo, no watermark. All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.

Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

## Do ustalenia
- Liczby: koszt węzłów w Gemach i wartości procentów — do kalkulatora balansu ([[Drzewko umiejętności postaci]]).
- Gałąź **Timer** w Twierdzy i premia do zdobywania **Diamentów** w gałęzi Income — nowe względem D-056, zob. [[Pytania otwarte]] #45.
- Ile węzłów na gałąź i czy węzły mają rangi (na razie 6 ikon na gałąź).

## Stan implementacji
- [x] Specyfikacja i prompty (2026-11-15)
- [x] Grafiki wygenerowane (Paweł z promptów; 4 ikony startowe i „?” dogenerowane przez Claude, 1 wariant) (2026-11-15)
- [x] Pocięte (`tools/skilltree_assets.py`), w Figmie (strona „Equipment Panel”, sekcja „Skill Tree — Assets”), w Roblox po „tak” Pawła — 74 grafiki (2026-11-15)
- [x] Okno w Roblox: ikonka w ekwipunku, wykrzyknik, karta z 3 zakładkami (start na Player), przesuwana mapa z zoomem (2026-11-15)
- [x] Logika: dane węzłów (`src/shared/SkillTreeData.luau`), zakup za Diamenty na serwerze (`src/server/SkillTree.server.luau`, RemoteEvent `SkillTreeBuy`), premie jako atrybuty `ST_<stat>` (2026-11-15)
- [x] Test Play: zakup węzła startowego, odkrycie gałęzi (2026-11-15)
- [ ] Poprawki po uwagach Pawła (mniejsze i wyśrodkowane napisy, nazwy gałęzi bez nachodzenia, animacje) — w plikach, czeka na wdrożenie do Studio
- [x] Poprawki Pawła 17.11 (propozycja): jedno tło dla wszystkich zakładek (gwiazdozbiory rycerza i kota-maga, `SkillTreeBgStars`, 1 wariant Higgsfield), bez obwódki przy kliknięciu kółka, cena pod każdym kółkiem, bez przycisku UNLOCK — ulepszenie przez **przytrzymanie kółka** (Diamenty lecą do kółka, kółko napełnia się cieczą w 0,85 s; puszczenie cofa), zakładki jak w ekwipunku: oryginalne grafiki bez skalowania, reakcja cieniem-nakładką i podskokiem napisu (`flatButton`); X = niewidoczne pole kliknięcia nad X wypalonym w ramce (wcześniej leżał na nim inny X z ekwipunku i wychodził jasny róg). Tło wgrane
- [ ] Premie `ST_<stat>` czytane przez walkę, karczmę, Twierdzę, pety; zapis w DataStore
- [ ] Balans cen i procentów

## Powiązane
- [[Drzewko umiejętności postaci]] · [[Okno ekwipunku]] · [[Twierdza (Tycoon)]] · [[Pety]] · [[Pipeline assetów]] · [[00 Start]]
