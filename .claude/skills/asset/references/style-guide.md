# Style guide – Blocky&Crycket

Źródło: key art + istniejące assety (`assets/processed/`: KeyArt, Teleport, Equipment, Pets, Quests, Shop, Guilds, PlayerFrame, Coin, Gem) oraz komponenty w Figmie.
Od 13.11.2026 nadrzędna jest instrukcja **Glossy Ink** z sejfu (`B&C/Styl/Instrukcja promptów — Glossy Ink.md`, kanon, D-027). Tekst promptu bierzesz wyłącznie z `prompt-templates.md`; ten plik służy do oceny wariantów i obróbki. Przy sprzeczności wygrywa instrukcja Glossy Ink.

## Charakter
- Kreskówka w stylu Roblox: blokowe postacie, przesadzone proporcje, wesołe, czytelne sylwetki.
- Fantasy-średniowiecze: drewno, kamień, złoto, ametysty, magiczne portale, sztandary.
- ~~Akcenty pixel art~~ — **zastąpione przez Glossy Ink (D-027):** ikony i ich akcenty malujemy cel-shadingiem z połyskiem, bez pikselowych iskierek. Pixelowy font zostaje tylko jako natywny font drobnych napisów UI (niżej, „Typografia”), nigdy w obrazie AI.
- Obramowania lekkie: bezramkowe żelkowe kafelki, cienka obwódka ze szczotkowanego złota albo cienkie drewniane listwy; bez ciężkich kamiennych ram.

## Linia i cieniowanie
- **Gruby, ciemny obrys** (`#1A1410` / `#2B1A10`), równej grubości, zaokrąglone łączenia. Na ikonie 512 px ≈ 10–14 px.
- Cel-shading 2–3 tony + **błyszczący highlight** (białe owalne odblaski w lewej górnej części).
- Delikatne światło od góry-lewej, cień pod obiektem (ciemniejszy kolor, nie czarny).
- UI: **kropki halftone** w rogu panelu, „szklany” połysk na górze przycisku.

## Paleta (HEX)
| Rola | Kolory |
|---|---|
| Obrys | `#1A1410`, `#2B1A10` |
| Złoto / UI rim | `#FFE07A` → `#F2C24A` → `#D18A12`, rim `#D9B45A` |
| Drewno | `#9A6532`, `#6E4627`, `#4A2D17` |
| Kamień | `#B9BEC8`, `#8D929E`, `#5F6470` |
| Granat paneli (istniejące assety) | `#2B3552` → `#1A2034` — tylko dla zgodności z już wdrożonymi panelami; w nowych dużych oknach tło to ciepłe wnętrze średniowiecznego domu (Glossy Ink, D-027), bez ciemnego, ponurego tła |
| Cyjan / slime / premium | `#41F5D6`, `#1BA9DA`, `#8AF0FF` |
| Ametyst / magia | `#F2A6FF`, `#B54BF0`, `#6A1FB8` |
| Zielony XP / natura | `#B6F26A`, `#4CB33C` |
| Przyciski HUD (tła) | Teleport `#8FDDF4`, Equipment `#FFC06A`, Pets `#78D2A4`, Quests `#EC6E66`, Shop `#5A6A92`, Guilds `#BE78F0` |
| Napisy UI | żółty `#FFD23F` (gradient `#FFF07A→#F2A81E`), biały, cyjan `#8AF0FF` |

## Typografia (natywnie, nigdy w obrazie AI)
- Nagłówki / liczby: **Luckiest Guy** (Roblox: `Enum.Font.LuckiestGuy`), obrys `#1A1410`, twardy cień w dół.
- Drobny tekst: **Pixelify Sans** (Figma) / `Enum.Font.Arcade` (Roblox).

## Kompozycja assetów
- Obiekt wyśrodkowany, wypełnia ~80% kadru, **1 główny obiekt** (+ max 2–3 drobne detale: iskierki, monety).
- Perspektywa: lekko z góry / 3/4, nie płaski profil.
- Generowanie: **czysto białe tło `#FFFFFF`**, bez cienia rzucanego na tło, bez ramki, bez napisów.
- Pełne przyciski HUD: zaokrąglony kwadrat (radius ~23%), kolorowe tło z gradientem, połysk, halftone, ikona w górnych ~65%, **dół pusty na napis** (napis dokładamy natywnie).

## QA checklist (wybór wariantu)
1. Obrys ciągły, gruby, ciemny – brak „rozmytych” krawędzi.
2. Paleta zgodna z tabelą (brak przypadkowych neonów / realistycznych tekstur).
3. Czytelne w **64 px** (sylwetka rozpoznawalna).
4. Brak tekstu, liter, znaków wodnych, logotypów.
5. Tło jednolite białe (łatwe wycięcie), obiekt nie dotyka krawędzi kadru.
6. Spójne z referencjami (`assets/refs/`) – styl jak key-art ekranu ładowania (`KeyArt_ref.jpg`), stopień detalu jak w `Shop.png` / `Coin.png`.
7. Żelazne zasady Glossy Ink: nic nie wystaje poza obrys ramki ani przycisku; portret, sloty i pola liczb puste; brak pasków postępu i nawiasów „[+]”; na mapach brak pinezek, kłódek i napisów.

## Czego unikać
Fotorealizm, 3D render z PBR, gradienty w tle, cienkie linie, pastelowe wyprane kolory, anime-style oczy, krew/gore (moderacja Roblox), znane postacie/IP.
