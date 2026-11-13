---
status: kanon
tags: [styl, prompty, grafika, ui]
źródło: "[[Instrukcja stylu i promptowania (oryginał 2026-11-13)]]"
---
# Instrukcja promptów — Glossy Ink

*Zatwierdzona 13.11.2026 decyzją D-027 w [[Rejestr decyzji]] (zdecydował Karol). Zastępuje prefiks z [[Style Lock]] (D-001) oraz zapisy o pixel-arcie ikon i płaskim interfejsie z [[Kierunek artystyczny]] (D-002).*

> [!info] W skrócie
> Instrukcja Game Directora (Pawła) z 13.11.2026 dla każdego, kto pisze prompty do generatorów grafiki (Higgsfield, Midjourney, DALL-E 3). **Złota zasada:** opisu stylu nie wymyśla się od zera — każdy prompt zaczyna się od stałego początku, kończy stałym końcem i ma osobny stały negative prompt; zmienia się tylko środek z układem i obiektami. Styl nazywa się „Glossy Ink” i jest wzorowany na ekranie ładowania. Pełny tekst z przykładem: [[Instrukcja stylu i promptowania (oryginał 2026-11-13)]].

> [!success] Obowiązuje (kanon, D-027)
> Każdy nowy prompt graficzny składamy według tej instrukcji. Dawny prefiks z [[Style Lock]] nie obowiązuje — zawierał nazwę cudzej gry, a ta wersja odwołuje się do własnego obrazu referencyjnego. Z [[Kierunek artystyczny]] (D-002) Glossy Ink zastępuje tylko pixel-art ikon i płaski (flat) design interfejsu. Reszta D-002 obowiązuje dalej: komiks i pop-art, Roblox voxel / low-poly, czytelność na telefonach, asymetryczne ramki, lekko nachylone przyciski, komiksowe fonty i dymki. Skill `/asset` składa prompty według tej notatki ([[Pipeline assetów]]).

## Jak używać
1. Wgraj do generatora ekran ładowania gry jako obraz referencyjny stylu (Style Reference).
2. Sklej prompt po angielsku z części: **stały początek → zmienny środek → stały koniec**; negative prompt podaj osobno.
3. W zmiennym środku opisz tylko układ i obiekty (lewo / prawo / środek, kolory kafelków, ikony, dokładne napisy w cudzysłowie) i pilnuj żelaznych zasad niżej.

## Części stałe — kopiować 1:1

**Stały początek**
```text
2D game UI asset, strictly matching the exact hand-drawn cartoon comic style of the "Blocky & Crycket" reference art. Art Style: "Glossy Ink" aesthetic with thick 4px black comic ink outlines, vibrant painterly cel-shading, subtle pop-art halftone dots in dark corners, and crisp curved glossy white specular highlights along top-left inner edges. Typography: Chunky, slightly tilted 3D extruded blocky cartoon font with thick black outlines and dark bottom shadows (matching the "BLOCKY & CRYCKET" logo).
```

**Stały koniec** (interfejs, ikony, okna)
```text
All icons, elements, and 3D texts are strictly contained inside the borders with nothing sticking out. Clean flat 2D mobile game UI asset, isolated on a solid flat white background, no external drop shadows.
```
Wyjątek: przy pełnoekranowej mapie miasteczka pomiń zdanie o białym tle i zakończ opisem cienkiej drewnianej ramki z czerwonym przyciskiem „X” w prawym górnym rogu.

**Stały negative prompt** (zawsze osobno)
```text
Negative Prompt: realistic 3D, photorealism, plastic texture, blurry, external drop shadow, elements sticking out of frame, broken borders, cropped text, dark gloomy teal palette, square text brackets "[+]", stat progress bars, character inside portrait frame, floating map pins.
```

## DNA stylu
| Element | Zasada |
|---|---|
| Obrys i cieniowanie | grube czarne obrysy komiksowe 4 px, miękki cel-shading, kropki rastrowe w cieniach, szklisty biały odblask przy wewnętrznej krawędzi (jak na niebieskim slime'ie z ekranu ładowania) |
| Obramowania | lekkie: bezramkowe żelkowe kafelki, cienka obwódka ze szczotkowanego złota albo cienkie drewniane listwy; zakaz ciężkich kamiennych ram |
| Kolory | żywe kolory Robloxa: turkus, pomarańcz, szmaragd, czerwień, królewski fiolet, złoto |
| Tła dużych okien | ciepłe wnętrze średniowiecznego domu (belki, kamienne ściany, światło świec); zakaz ciemnomorskiego, ponurego tła |
| Typografia | kanciasta, lekko pochylona czcionka 3D z czarnym obrysem i dolnym cieniem — jak w logo |
| Bohaterowie i ikony | kanciasty rycerz w stalowym hełmie, pomarańczowy kot-mag w fioletowej szacie, niebieski slime-kostka, brązowy pies, mały czerwony smok |

## Żelazne zasady (pod Roblox Studio)
1. **Zamknięte krawędzie.** Żaden miecz, ikona ani napis nie wystaje poza obrys przycisku ani ramki.
2. **Puste kontenery.** Ramka portretu gracza jest pusta w środku; sloty plecaka są puste; sloty założonego ekwipunku mają tylko półprzezroczystą sylwetkę przedmiotu. Zawartość wstawia silnik gry.
3. **Okna i statystyki.** Okno z kilku części powstaje jako jedna scalona bryła. Statystyki w 2 szerokich kolumnach po 3 wiersze; wiersz to: ikona, nazwa z niebieskim podtytułem, bardzo szerokie ciemne pole na liczby sześciocyfrowe, kwadratowy przycisk ze złotym „+”. Bez pasków postępu i bez nawiasów „[+]”.
4. **Mapy izometryczne** (teleport, miasteczko). Kamera wysoko nad ziemią, budynki pomniejszone o 30–40%, szerokie kamienne ścieżki i dużo zieleni. Bez pływających pinezek, kłódek i napisów — pinezki powstają osobnym promptem jako arkusz przycisków.

## Co zmieniła względem wcześniejszego kanonu
| Temat | Kanon do 13.11.2026 | Glossy Ink (od 13.11.2026) |
|---|---|---|
| Początek promptu | [[Style Lock]]: prefiks z nazwą gry-inspiracji | stały początek „Glossy Ink” z odwołaniem do własnego obrazu referencyjnego |
| Ikony | pixel-art w komiksowych ramkach ([[Kierunek artystyczny]]) | malarski cel-shading z połyskiem |
| Interfejs | płaski (flat design) | połysk, lekkie ramki, ciepłe tła wnętrz (asymetryczne ramki, nachylone przyciski i komiksowe dymki z [[Kierunek artystyczny]] obowiązują dalej) |
| Negative prompt | brak | stały, podawany osobno |

Instrukcja zgadza się z propozycją D-018 (styl „bubbly cartoon”) i z wnioskiem z [[Diagnoza pomysłu 2026-11-13]], że opis stylu nie powinien zawierać cudzej nazwy.

## Wdrożenie w skillu `/asset`
Szablony promptów skilla (`.claude/skills/asset/references/prompt-templates.md`) składają od 13.11.2026 każdy prompt według tej instrukcji: stały początek, zmienny środek z szablonu kategorii, stały koniec i osobny negative prompt. Dawny opis stylu paczki i ciemnogranatowe tło ramek zostały usunięte. Szczegóły: [[Pipeline assetów]].

## Do ustalenia
- Instrukcja opisuje angielskie zakończenie mapy miasteczka (drewniana ramka z przyciskiem „X”) tylko po polsku, a pełnych teł i key-artu nie opisuje wcale. Skill `/asset` ma na to własne zakończenia, oznaczone w szablonach jako nasze — przy wątpliwościach decyduje Game Director.
- Instrukcja pozwala na dokładne napisy w cudzysłowie, a zasady skilla `/asset` mówią „zero tekstu w grafikach AI” (napisy robimy natywnie). Skill dopuszcza napisy w obrazie tylko na wyraźną prośbę, np. przy makiecie okna.
- Stały negative prompt zawiera „floating map pins” i „character inside portrait frame”, a żelazna zasada 4 każe robić pinezki osobnym promptem jako arkusz przycisków. Przy takim arkuszu negative prompt działa więc przeciw celowi promptu. Szablon skilla `/asset` opisuje pinezki jako samodzielne przyciski UI w kształcie pinezki, nieumieszczone na mapie, a stałego negative promptu nie zmienia. Czy przy arkuszu pinezek wolno pominąć „floating map pins”, decyduje Game Director.
- Instrukcja zaleca połysk i lekkie ramki, ale nie mówi nic o asymetrycznych ramkach ani lekko nachylonych przyciskach z [[Kierunek artystyczny]]. Te zapisy obowiązują dalej (D-027 ich nie zmienia); czy pasują do Glossy Ink, decyduje Game Director.
- Przykład z instrukcji (okno Kowala) używa diamentów i przycisków „+” przy statystykach, co łączy się z pytaniami #6 (waluty) i #17 (statystyki) w [[Pytania otwarte]].

## Powiązane
[[Style Lock]] · [[Kierunek artystyczny]] · [[Pipeline assetów]] · [[Ekran ładowania]] · [[HUD]] · [[Rejestr decyzji]] · [[Pytania otwarte]]
