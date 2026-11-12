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
