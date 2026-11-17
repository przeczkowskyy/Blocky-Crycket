---
status: propozycja
tags: [ui, klasy, tekstury, swiat]
źródło: "polecenie Pawła 2026-11-16 (paczka tekstur dla Karola do sali wyboru bohaterów); arkusz z Higgsfield wygenerował Paweł"
---
# Tekstury sali wyboru klasy

> [!info] W skrócie
> Paczka 16 komiksowych tekstur (Glossy Ink) **dla sali ekranu wyboru bohatera** ([[Selektor bohatera]]). Wygenerował ją Paweł 16.11 jednym arkuszem w Higgsfield, a Claude pociął ją na osobne pliki. **Dla Karola:** do nałożenia na obiekty sali `Workspace/WyborKlasy` (generator `swiat/wybor_klasy/generuj.py`). Tylko do tego ekranu, nie na mapy gry. **Stan 17.11:** wgrane do Roblox po „tak” Pawła (ID w `assets/manifest.json`, `CsTex01`–`CsTex16`) i nałożone na salę. Potem na prośbę Pawła („tekstury na wszystko”) doszła reguła ogólna według materiału (kamień, drewno, deski, tynk, metal, złoto, tkanina) i beczki — razem 726 z 1160 widocznych części, 3881 ścian. Bez tekstur zostają tylko kreska (czarne obrysy i ciemna fuga, SmoothPlastic), drobne rekwizyty z SmoothPlastic (kufle, talerze, świece, księgi, eliksiry) i światła Neon. Reguły „co na co”: `swiat/wybor_klasy/tekstury.json`; nakłada `tools/studio/deploy_classselect.py` (po każdej przebudowie sali przez `tools/studio_buduj.py` trzeba uruchomić go ponownie).

## Pliki
- Pocięte kafelki 1024 × 1024 px: `assets/processed/ClassSelectTextures/CsTex01_…png` – `CsTex16_…png`.
- Podgląd całego arkusza: `assets/processed/ClassSelectTextures/_arkusz_v1.jpg`. Oryginał 4096 px leży lokalnie u Pawła w `assets/raw/ClassSelectTextures/v1.png` (folder `raw` nie trafia do gita).
- Model i prompt: Nano Banana 2.1, format 1:1, 4k, referencja `assets/refs/KeyArt_ref.jpg`. Części stałe promptu są z [[Instrukcja promptów — Glossy Ink]], środek opisuje siatkę 4 × 4 kafelków bez szwów.

## Drobne rekwizyty (druga paczka, 17.11)
- Na prośbę Pawła („tekstury na drobnostki w jednej generacji”) drugi arkusz 4 × 4 w Higgsfield (Nano Banana 2.1, 1 wariant): wosk świec, skórka jabłka, kamionka kufli, porcelana talerzy, skóra okładek ksiąg, glina słojów, skórka chleba, ser, liście, stal miecza, owijka rękojeści, malowana tarcza, korek, ciemny kamień wnęki, szkło eliksirów, wiklina kosza.
- Pocięte narzędziem `tools/tex_sheet.py` (generator dorysował kafelkom czarne ramki — cięcie z wcięciem 40 px): `assets/processed/ClassSelectTextures/CsProp01`–`CsProp16`, podgląd `_arkusz_CsProp.jpg`; oryginał lokalnie w `assets/raw/ClassSelectProps/v1.png`.
- Reguły w `swiat/wybor_klasy/tekstury.json` (wpisy z `_drobne`). Świecące części (Neon) i kreska zostają bez tekstur. Stan 17.11: wgrane po „tak” Pawła (`CsProp01`–`CsProp16` w manifeście) i nałożone — razem z pierwszą paczką teksturę ma 879 z 1160 widocznych części sali (4799 ścian); bez tekstur tylko 173 ciemne części kreski i 108 świecących.

## Co na co (propozycja)
| Plik | Tekstura | Gdzie w sali (grupa / części z `generuj.py`) |
|---|---|---|
| CsTex01_KamienMuru | kamienne bloki, ciemna fuga | Mury: cokół, „Mur kamień” |
| CsTex02_PlytyPodlogi | duże płyty z pęknięciami | Podloga: „Płyta”, płyta wnęki |
| CsTex03_Tynk | kremowy tynk z cegiełkami | Mury: „Mur tynk”, szczyty dachu |
| CsTex04_Cegla | czerwona cegła | łaty cegieł, komin (do wyboru) |
| CsTex05_BelkaDrewno | słoje belki, sęki | Szkielet (słupy, rygle, oczep), Wiezba |
| CsTex06_DeskiPolki | poziome deski z gwoździami | Regal (półki, plecy), Lada (blat, korpus) |
| CsTex07_DeskiDachu | ciemny gont od spodu | Dach: „Deski dachu” |
| CsTex08_Beczka | klepki z obręczą | Beczki (walce boczne) |
| CsTex09_KamienKominka | okrągłe kamienie | Kominek (obudowa, komin), łuk wnęki |
| CsTex10_Palenisko | okopcona cegła z żarem | Kominek: tył paleniska, „Sadza” |
| CsTex11_KamienPodestu | jasny gładki kamień | Podest (blat, kamienie obwodu) |
| CsTex12_Zloto | złota blacha z nitami | złota obwódka podestu, gałki, okucia |
| CsTex13_Dywan | czerwony dywan, złote romby | Dywan: „Dywan pole” |
| CsTex14_Tkanina | jasna tkanina do przebarwienia | Choragwie (kolor przez `Texture.Color3`) |
| CsTex15_Zelazo | kuta blacha z nitami | żelazo: żyrandole, pochodnie, latarnie |
| CsTex16_DeskiSkrzyni | deski skrzyni w jodełkę | Skrzynie |

## Uwagi do jakości
- Prawie wszystkie kafelki powtarzają się bez szwów. Nie da się tego powiedzieć o czterech: **11** (kamień podestu) i **15** (żelazo) mają ramkę przy brzegu, **14** (tkanina) to cały wiszący płat, a nie wzór. Z tego powodu 11, 14 i 15 nakładać raczej jako jedną teksturę na całą ścianę części (bez powtarzania), nie jako kafelek.
- W rogach kilku kafelków są kropki rastra: przy gęstym kafelkowaniu mogą tworzyć siatkę. Wtedy większy `StudsPerTile`.
- Na kafelkach nie ma liter ani butelek (zasada zespołu).

## Do ustalenia
- Czy Karol nakłada tekstury jako `Texture` na części, czy jako `MaterialVariant` (jedna zmiana dla wszystkich części danego materiału).
- Wgranie 16 plików do Roblox (Open Cloud) dopiero po „tak” Karola albo Pawła; ID trafią do `assets/manifest.json`.
- Związek z D-079 (agent Karola ma dać hali kreskówkowe faktury jak w Krzywym Miasteczku) — ta paczka może być ich źródłem.

## Powiązane
- [[Selektor bohatera]] · [[Klocki — Blender i Roblox]] · [[Pipeline assetów]] · [[00 Start]]
