---
status: propozycja
tags: [technika, blender, mapa, 3d, pipeline]
---
# Klocki — Blender i Roblox

> [!info] W skrócie
> Mapa z prostych brył (bloki, kliny, walce, kule) ma **jeden plik źródłowy `czesci.json`**, z którego powstają trzy rzeczy: scena w Blenderze (podgląd i ręczna edycja), części w Roblox Studio oraz model w podglądzie 3D [[Panel zespołu|panelu]]. Sprawdzone 12.11.2026 na demie „Leśna baza startowa” (2599 części). Bez wgrywania assetów na konto Roblox, bez moderacji, wszystko da się cofnąć jednym Ctrl+Z.

## Przepływ
```
swiat/<scena>/generuj.py ──► czesci.json ──► Blender   (tools/blender/klocki.py --z-json … --render …)
                                  ▲      ├──► Roblox    (tools/studio_buduj.py czesci.json)
        ręczna edycja w Blenderze │      └──► panel     (migawka: python panel/narzedzia/migawka.py)
        (tools/blender/klocki.py --do-json)
```
- **Generator** (`generuj.py`) opisuje scenę kodem: budynki z funkcji, las z losowania o stałym ziarnie. Zmiana liczby w skrypcie = nowa wersja mapy.
- **Blender** jest podglądem i warsztatem: każdy klocek to obiekt ze skalą równą rozmiarowi części; po przesunięciu lub przeskalowaniu `--do-json` zapisuje zmiany z powrotem.
- **Studio**: `tools/studio_buduj.py` wkłada części do jednego kontenera (`Workspace/<Nazwa>`), po jednym Modelu na budowlę. Kontener ma atrybut `Wygenerowane`; skrypt nie rusza niczego poza nim.
- Geometria klinów i walców zmierzona w Studio: `panel/luau/KSZTALTY.md`.

## Demo: Leśna baza startowa
Plac ze spawnem i studnią, karczma z szyldem-kuflem, tablica zleceń, koło fortuny, stragan sklepu, stajnia z koniem, wylęgarnia z jajami, brama areny, portal lochów, brama z palisadą, ognisko, staw z pomostem, las. Pliki: `swiat/demo_lesna_baza/` (`generuj.py`, `czesci.json`, `lesna_baza_claude_v1.blend`, `podglad/*.jpg`). W Studio: `Workspace/DemoLesnaBaza`. To szkic do rozmowy o stylu i skali, nie gotowa mapa — wnętrz budynków nie ma.

## Mapy v2: biblioteka krzywych brył i Krzywe Miasteczko (13.11.2026)
Demo v1 było zbyt grzeczne: proste ściany, drobne szyldy, mapa ginęła w lesie. Wersja v2 ma trzy nowe rzeczy.
- **Biblioteka `swiat/biblioteka/`.** `scena.py` pozwala budować w układach lokalnych: budynek powstaje wokół własnego (0, 0, 0), a `with s.uklad(pos, obrot, skala)` ustawia go, obraca i pochyla — układy można zagnieżdżać (przekrzywione piętro na pochylonym parterze). Do tego obrys „tuszem” z ciemnych klocków, cechy części (bez kolizji, bez cienia) i kontrola jakości (migotanie nakładających się ścian, budżet części). `podglad.py` renderuje pojedynczy budynek albo całą mapę w Blenderze w tle, także w płaskim świetle podobnym do domyślnego oświetlenia miejsca.
- **Mapa `swiat/krzywe_miasteczko/`** (`Workspace/KrzyweMiasteczko`, 700 studów na północ od dema): rynek ze studnią i straganami, gospoda z tablicą zleceń, zbrojownia, sklep magiczny, wylęgarnia, stajnia, brama lochów, brama twierdzy, brama miejska, arena i gildia (zamknięte), koło, domy tła, mur i wzgórza. Kontrakt dla budowniczych: `PROJEKT.md` (przykazania stylu z liczbami, paleta, układ, karty budynków). Każdy budynek to osobny plik w `budynki/`.
- **Proces**, który się sprawdził: szkolenie (styl, rzemiosło Roblox, układ hubu, przepisy na bryły, rubryka oceny) → projekt z liczbami → wspólny zestaw elementów → budynki równolegle, każdy z podglądem → złożenie miasta → niezależna krytyka na renderach → poprawki → zrzuty z prawdziwego Studio (`tools/studio_zrzuty.py`).

Najważniejsze ustalenia ze szkolenia: krzywizna od 4° wzwyż (mniej wygląda jak błąd), dach to 45–60% wysokości budynku, rekwizyt-szyld ma 8–12 studów, trzy walory koloru zamiast polegania na cieniu, kolor dachu jako kod funkcji; słońce tego miejsca stoi na północnym zachodzie, więc fronty głównych budynków patrzą w tę stronę; bez odniesień do alkoholu (Roblox dopuszcza je tylko w grach 18+). Według propozycji v2 gry miasteczko wchodzi do rozgrywki dopiero po sprawdzeniu pętli — na razie to demo stylu (propozycja D-025).

## Kiedy klocki, a kiedy siatki
| | Klocki (części) | Siatki z Blendera (FBX/GLB) |
|---|---|---|
| Do czego | blockout, teren, proste budynki, wszystko „klockowe” | postacie, pety, detale, organiczne kształty |
| Wgranie | od razu, przez MCP | upload na konto Roblox (trwały asset, moderacja, zgoda właściciela) |
| Edycja w Studio | obie osoby, na żywo | tylko podmiana siatki |
| Podgląd w panelu | dokładny | ramka + zrzut ze Studio |

Import siatek wymaga jednorazowej zgody w Studio (Assistant → uprawnienia MCP: zasoby + zatwierdzony folder) — opis w notatce Warsztatu „Z Blendera do Robloxa”.

## Zasady
- Skala: 1 jednostka = 1 stud; postać ma ok. 5 studs wysokości, drzwi 5–6 × 8.
- Kolory z palety w `generuj.py`; materiały to nazwy `Enum.Material`.
- Liście, kwiaty, dym, ogień i woda nie mają kolizji; wszystko jest zakotwiczone.
- Oświetlenia (`Lighting`) skrypty nie zmieniają — jest wspólne dla całego miejsca.

## Powiązane
[[Panel zespołu]] · [[Kierunek artystyczny]] · [[Styl UI gier Roblox]] · [[Rojo i struktura projektu]] · [[Narzędzia]] · [[Zadania]]
