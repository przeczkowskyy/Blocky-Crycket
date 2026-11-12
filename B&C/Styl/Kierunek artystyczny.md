---
status: kanon
tags: [styl]
źródło: "[[Dokumentacja projektu (oryginał)]] §2, §4"
---
# Kierunek artystyczny

Styl gry to hybryda **trzech estetyk**:

1. **Komiks i pop-art (Shakes & Fidget):** grube czarne obrysy (3–4 px, cel-shading), przerysowane proporcje, wygięta i asymetryczna architektura, subtelny wzór halftone (kropki rastrowe) w tłach i cieniach.
2. **Roblox voxel / low-poly:** żywa, mocno nasycona paleta. Postacie, pety i otoczenie 3D z kanciastych, blokowych brył.
3. **Pixel-art:** wszystkie ikony w interfejsie (przedmioty, waluty, loot, zakładki) w ostrym pixel-arcie, zamknięte w komiksowych ramkach.

## Interfejs
Płaski (flat design), czytelny na telefonach, asymetryczne ramki, lekko nachylone przyciski, komiksowe fonty i dymki („BAM!”, „POW!”).

## Zakazane
Fotorealizm, minimalistyczne korporacyjne ilustracje, generyczne sci-fi, niezwiązane estetyki fantasy, niespójne proporcje postaci, niezwiązane palety barw.

## Przełożenie na Roblox (propozycja techniczna)
- Obrys: `UIStroke` 3–4 px, `#000000`
- Lekka asymetria: `Rotation` od −2 do 2 na kartach i przyciskach
- Ikony pixel-art: `ResampleMode = Pixelated`
- Halftone: nakładka `ImageLabel` o niskiej widoczności

Zob. też: [[Style Lock]], [[Rycerz]], [[Kot-Mag]], [[Pety]].
