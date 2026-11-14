---
status: do-decyzji
tags: [styl, prompty, grafika, ui]
źródło: "[[Instrukcja stylu i promptowania (oryginał 2026-11-13)]]"
---
# Instrukcja promptów — Glossy Ink

> [!info] W skrócie
> Instrukcja Game Directora (Pawła) z 13.11.2026 dla każdego, kto pisze prompty do generatorów grafiki (Higgsfield, Midjourney, DALL-E 3). **Złota zasada:** opisu stylu nie wymyśla się od zera — każdy prompt zaczyna się od stałego początku, kończy stałym końcem i ma osobny stały negative prompt; zmienia się tylko środek z układem i obiektami. Styl nazywa się „Glossy Ink” i jest wzorowany na ekranie ładowania. Pełny tekst z przykładem: [[Instrukcja stylu i promptowania (oryginał 2026-11-13)]].

> [!warning] Status: do decyzji — ale to najnowsze polecenie Game Directora
> Instrukcja zastępuje prefiks z zatwierdzonego [[Style Lock]] (D-001) i zmienia zapisy o pixel-arcie i płaskim interfejsie z [[Kierunek artystyczny]] (D-002), więc potrzebuje wpisu w [[Rejestr decyzji]] (D-027, [[Pytania otwarte]] #22). Dokument przekazał Karol; formalne „tak” należy do Game Directora. **Przy nowych promptach stosujemy tę instrukcję** — stary prefiks zawiera cudzą nazwę, a ta wersja odwołuje się do własnego obrazu referencyjnego.

## Jak używać
1. Wgraj do generatora ekran ładowania gry jako obraz referencyjny stylu (Style Reference).
2. Sklej prompt po angielsku z części: **stały początek → zmienny środek → stały koniec**; negative prompt podaj osobno.
3. W zmiennym środku opisz tylko układ i obiekty (lewo / prawo / środek, kolory kafelków, ikony, dokładne napisy w cudzysłowie) i pilnuj żelaznych zasad niżej.
4. Generuj w Higgsfield modelem **Nano Banana 2.1** (`nano_banana_2_1`, polecenie Game Directora z 13.11), nie GPT Image. Model nie ma osobnego pola na negative prompt, więc negative dopisujemy jako ostatni akapit promptu (`Negative Prompt: …`).
5. Napisy na przyciskach i tabliczkach robimy w Roblox natywnie. W środku promptu prosimy więc o puste tabliczki (`NO text`), chyba że napis ma być częścią grafiki (logo, grafika marketingowa).

Gotowe środki dla każdej kategorii (ikona, przycisk, przedmiot, pet, okno, arkusz przycisków, mapa, tło) są w szablonach skilla `/asset`: `.claude/skills/asset/references/prompt-templates.md`. Przykład pełnych promptów: [[Mapa teleportacji]].

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

## Co to zmienia względem kanonu
| Temat | Kanon dziś | Instrukcja |
|---|---|---|
| Początek promptu | [[Style Lock]]: prefiks z nazwą gry-inspiracji | stały początek „Glossy Ink” z odwołaniem do własnego obrazu referencyjnego |
| Ikony | pixel-art w komiksowych ramkach ([[Kierunek artystyczny]]) | malarski cel-shading z połyskiem |
| Interfejs | płaski, asymetryczne ramki | połysk, lekkie ramki, ciepłe tła wnętrz |
| Negative prompt | brak | stały, podawany osobno |

Instrukcja zgadza się z propozycją D-018 (styl „bubbly cartoon”) i z wnioskiem z [[Diagnoza pomysłu 2026-11-13]], że opis stylu nie powinien zawierać cudzej nazwy.

## Do ustalenia
- Formalne potwierdzenie Game Directora, że instrukcja zastępuje prefiks z D-001 i zapisy o pixel-arcie z D-002 (D-027, pytanie #22).
- ~~Przepięcie szablonów skilla `/asset`~~ — zrobione 2026-11-14 na polecenie Game Directora ([[Pipeline assetów]]).
- Przykład z instrukcji (okno Kowala) używa diamentów i przycisków „+” przy statystykach, co łączy się z pytaniami #6 (waluty) i #17 (statystyki) w [[Pytania otwarte]].

## Powiązane
[[Style Lock]] · [[Kierunek artystyczny]] · [[Pipeline assetów]] · [[Ekran ładowania]] · [[HUD]] · [[Rejestr decyzji]] · [[Pytania otwarte]]
