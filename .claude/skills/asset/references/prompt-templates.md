# Szablony promptów (Higgsfield) — Glossy Ink

Źródło: notatka sejfu `B&C/Styl/Instrukcja promptów — Glossy Ink.md` (kanon, decyzja D-027 zatwierdzona 13.11.2026), oryginał `B&C/Źródła/Instrukcja stylu i promptowania (oryginał 2026-11-13).md`.
Ta instrukcja zastępuje dawny prefiks z notatki `Style Lock` (D-001) i dawny „STYLE BLOCK” tej paczki. Nie używaj ich w nowych promptach.

## Budowa każdego promptu

Każdy prompt składa się z czterech części, po angielsku:

1. **STAŁY POCZĄTEK** — kopiowany 1:1, znak w znak.
2. **ZMIENNY ŚRODEK** — szablon kategorii niżej, z podstawionymi `{...}`. Tylko układ i obiekty: lewo / prawo / środek, kolory kafelków, konkretne ikony.
3. **STAŁY KONIEC** — kopiowany 1:1, znak w znak (wyjątki niżej, tylko dla map i teł).
4. **STAŁY NEGATIVE PROMPT** — kopiowany 1:1 i podawany **zawsze osobno**.

Prompt główny = `STAŁY POCZĄTEK` + spacja + `ZMIENNY ŚRODEK` + spacja + `STAŁY KONIEC`.

Zasady:
- Części stałych nie tłumacz, nie skracaj, nie poprawiaj i nie dopisuj do nich słów. Wszystkie dopiski (np. po nieudanym wariancie „no text, no letters” albo „pure white #FFFFFF background”) idą do **zmiennego środka**.
- Negative prompt: jeśli narzędzie ma osobne pole na negative prompt, wpisz tam treść bloku po etykiecie `Negative Prompt:` (tak podaje ją przykład w oryginale instrukcji). Jeśli narzędzie nie ma takiego pola, dodaj cały blok, razem z etykietą, jako osobny akapit po stałym końcu. Treści negative promptu nie zmieniaj.
- **Obraz referencyjny stylu:** jeśli narzędzie przyjmuje obraz referencyjny, zawsze dołącz key-art ekranu ładowania `assets/refs/KeyArt_ref.jpg` (instrukcja: ekran ładowania jako *Style Reference*), a obok najwyżej jeden plik z `assets/refs/` najbliższy kategorii (np. `Shop.png` dla przycisków, `Coin.png` dla walut).

## STAŁY POCZĄTEK (kopiuj 1:1)
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo).
```

## STAŁY KONIEC (kopiuj 1:1 — interfejs, ikony, okna)
```text
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.
```
Białe tło z tego zdania jest zgodne z zasadą paczki „białe, jednolite tło przy generowaniu” (`project-rules.md`, reguła 3) — dzięki niemu `tools/process_image.py` wycina tło.

### Wyjątek z instrukcji: pełnoekranowa mapa miasteczka
Pomiń zdanie o białym tle (drugie zdanie stałego końca) i zakończ opisem cienkiej drewnianej ramki z czerwonym przyciskiem „X” w prawym górnym rogu. Instrukcja podaje ten opis tylko po polsku, więc angielskie sformułowanie jest nasze:
```text
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. The whole map is framed by a thin wooden frame with a glossy red "X" button in the top-right corner.
```

### Rozszerzenie paczki: tło / key-art (`background`, `keyart`)
Instrukcja nie opisuje pełnych teł bez ramki. Robimy to tak jak przy mapie: zostaje pierwsze zdanie stałego końca, a zdanie o białym tle odpada, bo tła nie wycinamy (`--bg none`):
```text
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out.
```
To rozszerzenie nie pochodzi z instrukcji — przy wątpliwościach pytamy Game Directora.

## STAŁY NEGATIVE PROMPT (zawsze osobno, kopiuj 1:1)
```text
Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

---

## Żelazne zasady zmiennego środka (sprawdź przed generowaniem)
1. **Zamknięte krawędzie.** Żaden miecz, ikona ani napis nie wystaje poza obrys przycisku ani ramki.
2. **Puste kontenery.** Ramka portretu gracza jest pusta (`completely EMPTY dark glossy portrait frame, NO character inside`). Sloty plecaka są puste (`empty rounded-square slots`). Sloty założonego ekwipunku mają tylko półprzezroczyste sylwetki przedmiotów (`semi-transparent item silhouettes`). Zawartość wstawia silnik gry.
3. **Okna i statystyki.** Okno z kilku części to jedna scalona bryła (`ONE single unified connected board, no gap in the middle`). Statystyki w 2 szerokich kolumnach po 3 wiersze (`2 WIDE COLUMNS x 3 ROWS`). Bez pasków postępu i bez nawiasów `[+]`.
4. **Mapy izometryczne** (teleport, miasteczko). Kamera wysoko (`high-angle isometric world map perspective`), budynki pomniejszone o 30–40%, szerokie kamienne ścieżki, dużo zieleni. Bez pływających pinezek, kłódek i napisów (`NO floating map pins, NO labels on buildings`). Pinezki osobnym promptem jako arkusz przycisków.

DNA stylu, którego środek nie może łamać: lekkie obramowania (bezramkowe żelkowe kafelki, cienka obwódka ze szczotkowanego złota albo cienkie drewniane listwy; **zakaz ciężkich kamiennych ram**), żywe kolory Robloxa (turkus, pomarańcz, szmaragd, czerwień, królewski fiolet, złoto), tła dużych okien jako ciepłe wnętrze średniowiecznego domu (**zakaz ciemnomorskiego, ponurego tła**).

## Napisy w obrazie
Instrukcja Glossy Ink pozwala wpisać w zmiennym środku dokładne napisy w cudzysłowie, a stały początek opisuje wygląd czcionki. Paczka ma regułę „zero tekstu w grafikach AI” (`project-rules.md`, reguła 2): napisy w grze robimy natywnie.
- **Domyślnie** (każdy asset, który trafia do gry): w środku dopisz `no text, no letters`, a miejsca na napisy zostaw puste.
- **Tylko na wyraźną prośbę** (np. makieta okna do pokazania w Figmie albo na panelu): dokładny napis po angielsku w cudzysłowie w zmiennym środku, jak w przykładzie z instrukcji. Taki obraz nie idzie do Roblox jako gotowy element interfejsu bez osobnej zgody.

---

## Warianty — zmienny środek

Wspólna końcówka środka dla pojedynczych obiektów (`icon`, `button`, `item`, `pet`, `currency`):
```
centered composition, single object filling about 80% of the frame, no text, no letters, no logo, no watermark
```

### icon — ikona HUD / menu
```
game UI icon of {subject}, {details}, viewed slightly from above, bold silhouette that reads clearly at small sizes, + wspólna końcówka
```
Przykład: `{subject}` = "a crossed sword and shield arena emblem", `{details}` = "steel sword, round wooden shield with gold rim, small flag".

### button — pełny przycisk HUD (bez napisu)
```
square game menu button with rounded corners (about 23% radius), thick dark outline, {color_name} glossy gradient fill from light top to darker bottom, subtle halftone dot pattern in the top-right corner, glassy shine on the top-left, centered icon of {subject} in the upper two-thirds fully inside the button outline, empty lower third reserved for a label, + wspólna końcówka
```
`{color_name}`: sky blue `#8FDDF4` / orange `#FFC06A` / green `#78D2A4` / red `#EC6E66` / slate blue `#5A6A92` / purple `#BE78F0` – albo nowy, spójny z paletą.

### button — arkusz pinezek mapy (osobny prompt, żelazna zasada 4)
```
sprite sheet of {count} standalone pin-shaped UI buttons in one row, isolated on the white background and not placed on any map, {pin_shapes_and_colors}, each button with a small icon of {location_icons}, evenly spaced with clear white gaps between them, every icon fully inside its button outline, no text, no letters
```
Uwaga: `tools/process_image.py` nie tnie arkusza na pojedyncze pliki — cięcie trzeba zrobić osobno.

> **Znany konflikt z oryginału instrukcji.** Stały negative prompt zawiera „floating map pins” (a także „character inside portrait frame”), a ten szablon zamawia właśnie pinezki. Generator może przez to osłabiać albo psuć kształt pinezek. Dlatego środek opisuje je jako samodzielne przyciski UI w kształcie pinezki na białym tle, „not placed on any map”, a w `{location_icons}` nie wstawiaj postaci w ramkach portretowych. **Stałego negative promptu nie zmieniaj** — czy przy arkuszu pinezek wolno pominąć „floating map pins”, rozstrzyga Game Director (pytanie w `B&C/Produkcja/Pytania otwarte.md`). Jeśli wynik jest zły, pokaż go człowiekowi zamiast samodzielnie wycinać frazę z negative promptu.

### item — broń / magia / zbroja / mikstura
```
RPG inventory item icon of {item}, {material} with {accent}, three-quarter view, slightly tilted diagonally, {rarity_glow}, + wspólna końcówka
```
`{rarity_glow}`: common = "no glow", rare = "soft blue glow around the item", epic = "soft purple magical glow and tiny sparkles", legendary = "warm golden glow and glossy sparkles". Poświata mieści się w kadrze i nie dotyka jego krawędzi.

### pet
```
cute chibi pet companion, {creature}, {color_scheme}, big friendly eyes with simple shine dots, chunky round body, three-quarter front view, happy expression, {accessory}, + wspólna końcówka
```
Bohaterowie i pety z instrukcji: kanciasty rycerz w stalowym hełmie, pomarańczowy kot-mag w fioletowej szacie, niebieski slime-kostka, brązowy pies, mały czerwony smok.

### currency
```
game currency icon, {currency_object}, chunky and shiny, strong rim highlight, slight 3/4 tilt, + wspólna końcówka
```
Referencje: `assets/refs/Coin.png`, `assets/refs/Gem.png` (obok `KeyArt_ref.jpg`).

### frame — ramka / panel / portret / slot
```
empty game UI frame panel, {shape}, {frame_style}, {inner_area}, glossy top reflection and subtle halftone dots, no content inside, no text, no numbers
```
- `{frame_style}`: "frameless glossy ink tile" / "thin delicate brushed-gold rim" / "thin wooden strips"; zakaz ciężkich kamiennych ram.
- `{inner_area}`: portret gracza = "completely EMPTY dark glossy portrait frame, NO character inside"; slot plecaka = "empty rounded-square slots"; slot założonego ekwipunku = "empty slot with a semi-transparent {item} silhouette"; duży panel = "warm medieval house interior background, wooden beams, stone walls, candlelight".

Uwaga: **żadnych wypalonych pasków z liczbami** – paski i liczby robimy natywnie.

### frame — okno (np. Postać + Plecak, Kowal)
```
Layout ({window_name}): ONE single unified connected board, no gap in the middle, warm medieval house interior background, wooden beams, stone walls, candlelight, {frame_style}, a blank banner on top without text and a glossy red "X" button in the top-right corner. {sections}. Stats in 2 WIDE COLUMNS x 3 ROWS; each row: {stat_icon} icon on the left, empty name plate with a blue subtitle strip, EXTRA-WIDE elongated recessed dark number box with plenty of space for 6-digit numbers, left empty, square glossy button with 3D gold "+" cross, NO brackets. Backpack: empty rounded-square slots. Equipped slots: semi-transparent item silhouettes. Player portrait: completely EMPTY dark glossy portrait frame, NO character inside. No text, no letters, no numbers.
```
`{sections}` opisuje rozkład stref: lewo / prawo / środek, kolory kafelków, konkretne ikony. Usuń zdania o statystykach, plecaku lub portrecie, jeśli okno ich nie ma. Obróbka: `--category frame`.

### background / keyart (bez wycinania tła → `--bg none`)
```
wide 16:9 cartoon fantasy game scene, {scene}, Roblox-like blocky characters, warm sunset to night sky gradient, readable foreground path, {key_elements}, leave the {free_area} area calmer for UI overlay, full illustrated background
```
Koniec: wariant „tło / key-art” wyżej (bez zdania o białym tle).

### background — mapa izometryczna (teleport, miasteczko; `--bg none`)
```
high-angle isometric world map perspective, {locations}, buildings scaled down by 30-40%, wide stone paths and plenty of greenery between locations, NO floating map pins, NO labels on buildings, no padlocks, no text
```
Koniec: pełnoekranowa mapa miasteczka → wyjątek z drewnianą ramką; inna mapa → wariant „tło / key-art”. Pinezki osobno: „arkusz pinezek mapy”.

---

## Co zmieniło się względem starych szablonów (13.11.2026, D-027)
- Usunięty dawny STYLE BLOCK paczki i dawny NEGATIVE; ich miejsce zajęły stałe części Glossy Ink. Kompozycja (środek, ok. 80% kadru) i zakaz tekstu przeszły do wspólnej końcówki środka.
- `frame`: usunięte ciemnogranatowe wnętrze `#1E2740` (sprzeczne z zakazem ciemnego, ponurego tła i z negative promptem „dark gloomy teal palette”); materiał ramki zawężony do lekkich obramowań, wnętrza według zasady pustych kontenerów.
- `item`: „pixel sparkles” zamienione na „glossy sparkles” (D-027 zastępuje pixel-art ikon malarskim cel-shadingiem).
- `button`: dopisane „fully inside the button outline” (zasada zamkniętych krawędzi).
- Nowe warianty z żelaznych zasad: okno, mapa izometryczna, arkusz pinezek.
