---
status: kanon
tags: [styl]
źródło: "[[Dokumentacja projektu (oryginał)]] §2, §4"
---
# Kierunek artystyczny

Styl gry to hybryda **trzech estetyk** (od 13.11.2026 trzecią, pixel-art ikon, zastępuje „Glossy Ink” — decyzja D-027, zob. niżej):

1. **Komiks i pop-art (Shakes & Fidget):** grube czarne obrysy (3–4 px, cel-shading), przerysowane proporcje, wygięta i asymetryczna architektura, subtelny wzór halftone (kropki rastrowe) w tłach i cieniach.
2. **Roblox voxel / low-poly:** żywa, mocno nasycona paleta. Postacie, pety i otoczenie 3D z kanciastych, blokowych brył.
3. ~~**Pixel-art:** wszystkie ikony w interfejsie (przedmioty, waluty, loot, zakładki) w ostrym pixel-arcie, zamknięte w komiksowych ramkach.~~

> [!warning] Punkt 3 zastąpiony (D-027, 13.11.2026)
> Ikony nie są już w pixel-arcie. Według [[Instrukcja promptów — Glossy Ink]] malujemy je cel-shadingiem z połyskiem, w lekkich ramkach. Punkty 1 i 2 obowiązują nadal.

## Interfejs
~~Płaski (flat design)~~, czytelny na telefonach, asymetryczne ramki, lekko nachylone przyciski, komiksowe fonty i dymki („BAM!”, „POW!”).

> [!warning] Zastąpione jest tylko „płaski (flat design)” (D-027, 13.11.2026)
> Zamiast płaskiego designu obowiązuje styl „Glossy Ink” z [[Instrukcja promptów — Glossy Ink]]: połysk, lekkie ramki (żelkowe kafelki, cienka złota obwódka albo cienkie drewniane listwy) i ciepłe tła wnętrz w dużych oknach. Reszty tego akapitu D-027 nie zmienia: czytelność na telefonach, asymetryczne ramki, lekko nachylone przyciski, komiksowe fonty i dymki („BAM!”, „POW!”) obowiązują dalej jako część D-002. Słowa „flat 2D” w stałym końcu promptu Glossy Ink oznaczają płaski obraz 2D na białym tle do wycięcia, a nie płaski design interfejsu. Czy asymetria i nachylenie dobrze współgrają z Glossy Ink, to otwarte pytanie do Game Directora — do jego decyzji obowiązuje zapis wyżej.

## Zakazane
Fotorealizm, minimalistyczne korporacyjne ilustracje, generyczne sci-fi, niezwiązane estetyki fantasy, niespójne proporcje postaci, niezwiązane palety barw.

## Przełożenie na Roblox (propozycja techniczna)
- Obrys: `UIStroke` 3–4 px, `#000000`
- Lekka asymetria: `Rotation` od −2 do 2 na kartach i przyciskach
- ~~Ikony pixel-art: `ResampleMode = Pixelated`~~ — nieaktualne po D-027 (ikony nie są już w pixel-arcie)
- Halftone: nakładka `ImageLabel` o niskiej widoczności

Zob. też: [[Instrukcja promptów — Glossy Ink]] (obowiązująca instrukcja promptów), [[Style Lock]] (historia), [[Rycerz]], [[Kot-Mag]], [[Pety]].
