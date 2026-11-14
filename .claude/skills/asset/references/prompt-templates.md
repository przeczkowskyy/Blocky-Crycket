# Szablony promptów (Higgsfield) — format „Glossy Ink”

Źródło zasad: sejf `B&C/Styl/Instrukcja promptów — Glossy Ink.md` (instrukcja Game Directora z 13.11.2026,
oryginał w `B&C/Źródła/Instrukcja stylu i promptowania (oryginał 2026-11-13).md`). Przy rozbieżności wygrywa sejf.

## Model i ustawienia (domyślne)
| pole | wartość |
|---|---|
| model | **`nano_banana_2_1`** (polecenie Game Directora 2026-11-13; nie GPT Image) |
| `medias` | `image_references`: **`assets/refs/KeyArt_ref.jpg`** (ekran ładowania = Style Reference) + 0–1 ref najbliższej kategorii (`Shop.png`, `Coin.png` …) |
| `resolution` | `2k` (ikony, przyciski) · `4k` (okna, tła, mapy) |
| `aspect_ratio` | `1:1` ikony/przyciski/pety · `16:9` okna, tła, mapy · `21:9`/`4:1` arkusz przycisków |
| `seed` | stały w obrębie jednej serii (np. wszystkie piny, wszystkie ikony HUD) |

Model **nie ma osobnego pola negative** → negative prompt dopisz na końcu tekstu promptu jako osobny akapit
zaczynający się od `Negative Prompt:`.

## Budowa promptu (zawsze, po angielsku)
**STAŁY POCZĄTEK** → **ZMIENNY ŚRODEK** (szablon kategorii niżej) → **STAŁY KONIEC** → pusta linia → **STAŁY NEGATIVE**.
Części stałe kopiuj **1:1, bez zmian**. Zmieniasz wyłącznie środek.

### STAŁY POCZĄTEK
```
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo).
```

### STAŁY KONIEC (UI, ikony, okna, przyciski, przedmioty, pety)
```
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.
```
**Wyjątek — pełnoekranowa mapa miasteczka:** pomiń zdanie o białym tle; zakończ tak:
```
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. The whole map is enclosed in a thin wooden frame with a glossy red "X" close button in the top-right corner, no external drop shadows.
```

### STAŁY NEGATIVE
```
Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

---

## Zasady środka (pilnuj zawsze)
1. **Zamknięte krawędzie** — nic (miecz, ikona, napis) nie wystaje poza obrys przycisku/ramki.
2. **Puste kontenery** — portret: `completely EMPTY dark glossy portrait frame, NO character inside`; plecak: `empty rounded-square slots`; sloty ekwipunku: tylko `semi-transparent item silhouettes`.
3. **Okna** — wieloczęściowe jako `ONE single unified connected board, no gap in the middle`; statystyki `2 WIDE COLUMNS x 3 ROWS`, wiersz: ikona | nazwa + niebieski podtytuł | `EXTRA-WIDE elongated recessed dark number box` | `square glossy button with 3D gold "+" cross, NO brackets`. Bez pasków postępu.
4. **Mapy** — `high-angle isometric world map perspective`, budynki pomniejszone o 30–40 %, szerokie kamienne ścieżki, dużo zieleni, `NO floating map pins, NO labels on buildings`. Piny osobnym promptem (arkusz).
5. **Ramki lekkie** — `frameless glossy jelly tile`, `thin delicate brushed-gold rim` albo cienkie drewniane listwy. Zakaz ciężkich kamiennych ram.
6. **Tła dużych okien** — `warm medieval house interior background, wooden beams, stone walls, candlelight`. Zakaz ciemnomorskiego/ponurego tła.
7. **Napisy (reguła projektu)** — w Roblox teksty robimy natywnie (Luckiest Guy + `UIStroke`), bo wypalony tekst trzeba potem wycierać (tak było w oknie ekwipunku). Domyślnie w środku pisz `blank empty plaques and buttons with NO text on them`. Dokładny napis w cudzysłowie dawaj tylko wtedy, gdy Game Director chce go w obrazie (np. logo, grafika marketingowa).
8. **Kolory** — żywe kolory Robloxa: turkus, pomarańcz, szmaragd, czerwień, królewski fiolet, złoto (HEX w `style-guide.md`). Ikony malarskie z połyskiem, nie pixel-art.

---

## Środki wg kategorii (wstaw między STAŁY POCZĄTEK a STAŁY KONIEC)

### icon — ikona HUD / menu
```
Single game UI icon of {subject}, {details}, viewed slightly from above, bold chunky silhouette that reads clearly at 64 px, centered, filling about 80% of the frame, nothing touching the image edges.
```
Przykład: `{subject}` = "a crossed sword and shield arena emblem", `{details}` = "steel sword, round wooden shield with thin brushed-gold rim, small red flag".

### button — pełny przycisk HUD
```
Single square game menu button with rounded corners (about 23% radius), frameless glossy jelly tile in {color_name}, light top to darker bottom, subtle halftone dots in the top-right corner, glassy shine on the top-left, centered icon of {subject} in the upper two-thirds, empty blank lower third reserved for a label with NO text on it.
```
`{color_name}`: sky blue `#8FDDF4` / orange `#FFC06A` / green `#78D2A4` / red `#EC6E66` / slate blue `#5A6A92` / purple `#BE78F0`.

### item — broń / magia / zbroja / mikstura
```
Single RPG inventory item icon of {item}, {material} with {accent}, three-quarter view, slightly tilted diagonally, {rarity_glow}, centered, filling about 80% of the frame.
```
`{rarity_glow}`: common = "no glow", rare = "soft blue glow around the item", epic = "soft purple magical glow and tiny sparkles", legendary = "warm golden glow and tiny sparkles".

### pet
```
Single cute chibi pet companion, {creature}, {color_scheme}, big friendly eyes with simple shine dots, chunky round blocky body, three-quarter front view, happy expression, {accessory}, centered, filling about 80% of the frame.
```
Bohaterowie z DNA stylu: kanciasty rycerz w stalowym hełmie, pomarańczowy kot-mag w fioletowej szacie, niebieski slime-kostka, brązowy pies, mały czerwony smok.

### currency
```
Single game currency icon, {currency_object}, chunky and shiny, strong glossy rim highlight, slight 3/4 tilt, centered.
```
Dodatkowe referencje: `assets/refs/Coin.png`, `assets/refs/Gem.png`.

### frame — okno / panel UI
```
Layout ({window_name}): ONE single unified connected board with a warm medieval house interior background (wooden beams, stone walls, candlelight glow), thin delicate brushed-gold rim, blank empty title banner with NO text, glossy red rounded-square "X" button in the top-right corner. {sections: Left/Right/Center, empty slots, number boxes}. No numbers, no stat bars.
```
Uwaga: **żadnych wypalonych pasków z liczbami ani napisów** – liczby i teksty robimy natywnie.

### sheet — arkusz przycisków (piny mapy, seria ikon)
```
Sprite sheet of {N} separate {object_type} buttons arranged in a clean grid of {cols} columns and {rows} rows with wide even white gaps between them, all the same size and shape, each one: {shared_description}. Button contents in reading order: 1) {a}; 2) {b}; ... Each button is fully separate, nothing overlapping or touching.
```
Obróbka: arkusz tniesz na pojedyncze pliki (po wycięciu białego tła — osobne wyspy), każdy dalej jak zwykły asset.

### map — pełnoekranowa mapa (koniec z wyjątku mapy, `--bg none`)
```
Layout (Isometric Town Map): high-angle isometric world map perspective of a cozy original medieval fantasy hub town at sunset, buildings shrunk by 30-40% with wide cobblestone paths and lots of green grass, trees and bushes between locations. {Top-Left / Center / Top-Right / Bottom-Left / Bottom-Right: landmarks}. Completely clean buildings with NO floating map pins, NO padlocks and NO labels or text on the map.
```

### background / keyart (bez wycinania tła → `--bg none`)
```
Wide 16:9 full illustrated cartoon fantasy game scene, {scene}, Roblox-like blocky characters, warm sunset sky, readable foreground path, {key_elements}, leave the {free_area} area calmer for UI overlay.
```
Dla tła zamiast STAŁEGO KOŃCA daj: `All elements are fully inside the image, full illustrated background, no external drop shadows.`
