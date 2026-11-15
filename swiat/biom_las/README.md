# swiat/biom_las — Biom Las „Bór Pod Ukłonem” (mapa z klocków)

Pierwszy biom gry: las 1000 × 1000 studów, 6 podbiomów, 24 lokacje, 16 stref potworów, 4 patrole, troll i strażnik.
Kontrakt (co i dlaczego): [`PROJEKT.md`](PROJEKT.md). Notatka w sejfie: `B&C/Gra/Biom Las.md`. Status: **propozycja**.

## Pliki

| Plik | Co to jest |
|---|---|
| `uklad.json` | podbiomy, lokacje, ścieżki, woda, **teren** (poziomy, kopce, rampy), strefy spokoju, piny |
| `potwory.json` | strefy potworów z węzłami walki i domami, patrole, troll, strażnik, zasady |
| `ujecia.json` | ujęcia kontrolne w układzie lasu |
| `geo.py` | geometria i model wysokości `Teren.H(x, z)` — wspólny dla budowy, kontroli i planu |
| `wezly.py` | liczy węzły walki i domy z maski terenu i zapisuje je w `potwory.json` |
| `sprawdz.py` | kontrola układu (wielokąty, uskoki, urwiska na drogach, węzły, pojemność, domy, kontrast, czasy) |
| `generuj.py` | generator mapy → `czesci.json`, `znaczniki.json`, `ujecia_swiat.json` |
| `teren.py`, `rosliny.py`, `skaly.py`, `lokacje/*.py`, `paleta.py` | moduły budowy: teren i woda, rodziny roślin i skał, lokacje (jeden plik na podbiom, Ukłon osobno), kolory |
| `czesci.json` | **wynik**: 13 353 części w układzie świata Studio (kontener `Workspace/BiomLas`, środek (0; 0; −2000), obrót 180°) |
| `znaczniki.json` | **wynik** dla kroku „potwory w Studio”: strefy, węzły z wysokością, domy, patrole, troll, strażnik, punkty E, piny, grupy stale wczytane i z niskim detalem (w układzie lasu) |
| `ujecia_swiat.json` | **wynik**: ujęcia przeliczone do świata (Blender, zrzuty ze Studio) |
| `plan.py` → `podglad/plan.png`, `podglad/plan_telefon.png` | plan z góry dla ludzi (pełny z legendą i sama mapa na telefon) |
| `podglad/01…12_*.jpg` | wybrane rendery z Blendera (rzut z góry obrócony: północ lasu u góry) |

## Polecenia (z głównego folderu repozytorium)

```
# 1. (po zmianie terenu albo stref) węzły walki i domy — trwa ok. 2 min
python -B swiat/biom_las/wezly.py --zapisz

# 2. kontrola układu (kod 1 = błąd)
python -B swiat/biom_las/sprawdz.py

# 3. mapa z klocków (ok. 8 s): czesci.json, znaczniki.json, ujecia_swiat.json + raport części i kontrola placów walki
python -B swiat/biom_las/generuj.py

# 4. podglądy w Blenderze (Blender w tle, wspólna blokada; ok. 1–2 min na 20 ujęć)
python swiat/biblioteka/podglad.py --json swiat/biom_las/czesci.json --ujecia swiat/biom_las/ujecia_swiat.json --wyj <folder> [--tylko l03,l06] [--szer 1400 --probki 32]

# 4a. podgląd ze strefami potworów (czerwone place walki r 12, zastępcze bryły w skali, domy) — nie nadpisuje czesci.json
python -B swiat/biom_las/generuj.py --znaczniki-widoczne --wyj <folder>/czesci_znaczniki.json
python swiat/biblioteka/podglad.py --json <folder>/czesci_znaczniki.json --ujecia <folder>/ujecia_swiat.json --wyj <folder> --tylko l03

# 5. plan z góry
python -B swiat/biom_las/plan.py
python -B swiat/biom_las/plan.py --telefon --szer 1200
```

Pułapka Windows: uruchamiaj z `PYTHONIOENCODING=utf-8`. Wymagane: numpy (maski), Pillow (plan), Blender 5 (podglądy).
Rzut z góry `l03_mapa_gora.jpg` jest w układzie świata — obróć o 180°, żeby północ lasu była u góry.

## Budowa w Studio (następny krok — jeszcze niezrobiony)

1. Sprawdź, że w świecie pudło x −700…700, z −1300…−2700 jest puste (miasteczko kończy się ok. z −900).
2. `python tools/studio_buduj.py swiat/biom_las/czesci.json` (jeden kontener `Workspace/BiomLas`, do cofnięcia; `--usun` usuwa).
3. Ustaw atrybuty grup z `znaczniki.json`: `grupy_stale_wczytane` → `ModelStreamingMode = Persistent`, `grupy_niski_detal` → `LevelOfDetail = StreamingMesh` (`czesci.json` nie przenosi atrybutów).
4. Zrzuty z tych samych ujęć: `python tools/studio_zrzuty.py swiat/biom_las/ujecia_swiat.json --przesun 0,0,0 --wyj <folder>`.
5. Próbka kolorów, pomiar na telefonie (667 × 375, 844 × 390) przy włączonym streamingu, kontrola kolizji na rampach i krawędziach.

## Liczby

13 353 części (limit 25 000, rezerwa ok. 11,6 tys.): Ostępy 2759, Korona 1644, Kapeluszowo 1578, Łąka 1545, Wąwóz 1169,
Mur 1160, Ścieżki 1156, Serce 688, Tło 545, Woda 449, Teren 398, Punkty 142, Piny 60, Chmury 60. Neon 79, przezroczyste 11,
z kolizją 24%, bez cienia 52%, SmoothPlastic 89%, Wood 9%. Ścieżki 6,6 tys. studów, do Ukłonu 26 s, do Kręgu 66 s.
Potwory: 64 naraz w strefach (do 86) + 4 patrole + troll + strażnik.

## Przegląd świeżym okiem (15.11, 3 rundy podglądów)

Poprawione: kryształ Kręgu urósł do ok. 95 n.p.m. (był za mały — z Rozstaju go nie było widać), menhiry i filar z łupku
z czapami mchu (były beżowe jak posadzka), ściany labiryntu z garbatym wierzchem z liści i jagodami, pod sosnami Ostępów
ciemne igliwie (place walki wyglądają jak jaśniejsze polanki), stopa Ukłonu z przyporami i korą, jama wilka z liśćmi
i kijem, okrągłe końce ścieżek (koniec szlaku przy bramie wystawał trójkątem), kwiaty i głazy przed Ławką, ujęcie
`l11_rozstaj` przesunięte (sowa zasłaniała kryształ). Rozdz. 0a kontraktu.

## Znane słabości

- Nic nie było jeszcze w Studio: kolory, wydajność na telefonie, streaming i kolizje na klinach są niezmierzone.
- Ostępy z oczu gracza nadal jasnozielone pod koronami (igliwie pomaga tylko trochę); ciemność boru robią korony.
- Ściany labiryntu z bliska to nadal duże płaskie fioletowe lica; teren poza poziomami i kopcami jest płaski.
- Ściany rynien Wąwozu i rant półki (ujęcie l17) to duże gładkie jasne płaszczyzny — mało faktury.
- Podkładki stref (ciemniejsza trawa, polanki mchu) z góry wyglądają jak koła z kół.
- Jezioro to jedna płaska tafla; Łąka trochę „parkowa”.
- Z daleka las wygląda jak makieta (brak mgły — wybór dla ludzi).
- `sprawdz.py` ma 2 ostrzeżenia (rozdz. 13 kontraktu).
