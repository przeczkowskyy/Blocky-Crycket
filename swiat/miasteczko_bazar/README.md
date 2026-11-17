# Miasteczko jako ciasny bazar — scena z klocków

Pierwszy blok pasa świata (D-075): ciasny bazar ze sklepami, do których się wchodzi (D-084, D-085), portalem do krain,
przejściem na działkę, zagrodą petów, tablicą z rankingiem i Bramą Leśną na styku z pasem Lasu. Status: **propozycja**
(16/17.11.2026). Projekt, uzasadnienia i wybory do decyzji: [PROJEKT.md](PROJEKT.md).

| Plik | Co to jest |
|---|---|
| `uklad.json` | jedno źródło układu: położenie w świecie, granice, poziomy, budynki, stragany, domy, mury, latarnie, girlandy, ścieżki-kody, cele czasu |
| `generuj.py` | składa scenę → `czesci.json` (format panelu i `tools/studio_buduj.py`) + `znaczniki.json` + raport części |
| `sprawdz.py` | kontrola bez Studio: format, granice, nachodzenie, przejścia, osiągalność, czasy biegu, rozmiary, sprzedawcy, znaczniki |
| `podglad.py`, `rysownik.py` | podglądy w Pillow → `podglad/*.jpg` i `ujecia.json` (te same kamery w świecie Studio) |
| `siatka.py` | siatka chodzenia: przeszkody, promień postaci, najkrótsze drogi i czasy biegu |
| `budynki/*.py` | moduły: karczma, zbrojownia, sklep magiczny, Training Center, zagroda petów, portal do krain, tablica, Brama Leśna |
| `postacie.py` | sprzedawcy (barman, mistrz gier, mag, zbrojmistrz, trener, opiekunka) i pety (pies, slime, smok) |
| `wspolne.py` | skorupa sklepu z wnętrzem, lada, półki, markiza, lampa, girlanda, punkty E, rejestr znaczników |
| `podglad/` | `plan_gora.jpg` (plansza z podpisami, izochronami biegu i skalą) i `u1`–`u5` (całość, uliczka, wnętrze karczmy, plac z portalem i działką, zagroda z tablicą) |

**Liczby:** 4410 części (po zmianie postaci 17.11.2026; cel ok. 8000, twardy limit 12 000), 93 grupy. Kontener `Workspace/MiasteczkoBazar`.
Świat = (994 + x; y; −700 + z), bez obrotu: części stoją w pliku już tam, gdzie mają stanąć (X 882…1066,
Z −790…−610), więc przy budowie i zrzutach **nie podaje się `--przesun`**. Wschodni brzeg (X 1066) to początek pasa
Lasu. Bazar stoi na wschodnim końcu płyty Baseplate (PROJEKT.md, wybór 1).

## Polecenia (z głównego folderu repozytorium)

```
python -B swiat/miasteczko_bazar/generuj.py      # → czesci.json, znaczniki.json, raport części
python -B swiat/miasteczko_bazar/sprawdz.py      # kontrola (kod 1 = błąd); --krotko = tylko błędy i ostrzeżenia
python -B swiat/miasteczko_bazar/podglad.py      # → podglad/*.jpg i ujecia.json; --tylko plan,u2; --wyj <folder>
```

Wynik kontroli z 17.11.2026: **0 błędów, 2 ostrzeżenia** (ok. 85 drobnych części wtopionych w grunt do 0,4 st, czyli
w płytę Baseplate — jak w dzisiejszym miasteczku; 31 drobiazgów mniejszych niż 0,5 — oczy, guziki, oczka kostki).

## Budowa w Studio (następny etap — w tym etapie Studio nie było używane)

Studio to wspólne miejsce Team Create: najpierw zgłoś pracę, buduj tylko we własnym kontenerze, Lighting bez zmian,
niczego nie publikuj.

```
python panel/narzedzia/praca.py start --id bazar-studio --tytul "Bazar w Studio" --koniec +45m ^
    --obszar studio:MiasteczkoBazar --obszar swiat/miasteczko_bazar --stop-przy-kolizji
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json --sucho   # tylko pokaże kontener i liczbę części
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json           # Workspace/MiasteczkoBazar (ok. 30 paczek po 150)
python tools/studio_zrzuty.py swiat/miasteczko_bazar/ujecia.json --wyj <folder>   # te same kadry co podglad/, bez --przesun
python tools/studio_buduj.py swiat/miasteczko_bazar/czesci.json --usun    # usuwa tylko własny kontener (atrybut Wygenerowane)
python panel/narzedzia/praca.py koniec --id bazar-studio
```

Po budowie: migawka i raport na panelu (skill `.claude/skills/panel/SKILL.md`), porównanie zrzutów ze Studio
z `podglad/`.

## Następny etap — lista

1. **Budowa i zrzuty** jak wyżej; obejrzeć kadry `u1`–`u5` i `plan_gora` ze Studio, poprawić kolory frontów rzędu
   północnego (stoją w cieniu) i ewentualne migotanie.
2. **Miejsce startu:** `SpawnLocation` na znaczniku `start` (część „Punkt startu” w grupie `Start`, patrzy na +x —
   `tools/studio_buduj.py` tworzy tylko części). Co z dzisiejszym spawnem — decyzja człowieka.
3. **Podpowiedzi E i uchwyt dla okien Pawła:** `ProximityPrompt` w każdej części „Podpowiedź E <id>”
   (`znaczniki.json` → `sklepy`, `training_center`, `zagroda`, `tablica`); `MaxActivationDistance` 10 (sprawdzone:
   podpowiedź jest bliżej), `RequiresLineOfSight` do sprawdzenia przy ladach. Uchwyt: jedno zdarzenie po stronie
   klienta z identyfikatorem sklepu (`karczma`, `mistrz_gier`, `sklep_magiczny`, `zbrojownia`, `training_center`,
   `zagroda_petow`, opcjonalnie `tablica`), na które okna 2D Pawła się podpinają — nazwę i miejsce ustala Paweł (D-093:
   okna i ich skrypty są po jego stronie).
4. **Portal do krain:** E (albo wejście w wir — znacznik `portal_krain_wir`) → przejście przez chmury i wybór krainy
   (D-075); na razie cel: Las — Polana Przybycia (u 14 w planie pasa). Punkt przybycia „miasteczko” w planie Lasu
   (dziś przy Bramie Miejskiej starego miasteczka) zmienić na start bazaru.
5. **Brama Leśna:** E → Las (albo przejście pieszo — wybór 2 w PROJEKT.md, wymaga bramy w ścianie zamykającej Lasu).
6. **Brama Twierdzy:** E → działka gracza, gdy Twierdza powstanie.
7. **Wrota lochów:** blokada osobna dla gracza — klient chowa `BramaLochow/Blokada` po odblokowaniu (cutscenka, D-042).
8. **Zagroda petów:** sześć miejsc `miejsce_peta` na odstawione pety; okno zagrody — Paweł.
9. **Tablica:** SurfaceGui na powierzchni ze znacznika `tablica_ranking` (środek, normalna, 6,4 × 4,8).
10. **Pomiar:** chodzenie w Play (progi, schodki portalu, kamera we wnętrzach), telefon (części, streaming — bazar to
    hub, rozważyć `Persistent`), czytelność sprzedawców i szyldów.
11. **Sejf:** wpis w `B&C/Technika/Klocki — Blender i Roblox.md`, `Zadania.md` i `Dziennik zmian.md` (w tym etapie
    zakres zapisu był ograniczony do tego folderu).

## Poprawki po pierwszej próbie w grze (17.11.2026, w nocy)

Mapa stoi w Studio (`Workspace/MiasteczkoBazar`, 4410 części) razem z pakietem gry `swiat/miasteczko_bazar_gra`
(podpowiedzi E, przejścia, tablica). Wyniki prób w trybie Play i zrzuty z gry: `swiat/miasteczko_bazar_gra/README.md`
i `swiat/miasteczko_bazar_gra/klatki/`. Zmiany w tym folderze:

- **Postacie — własne projekty** (`postacie.py`): karczmarz nie jest już wąsaczem w czerwieni i bieli (za bardzo
  przypominał znaną postać z cudzych gier) — teraz łysy, z krótką rudą brodą i bakami BEZ wąsów, czerwona opaska
  karczmy zawiązana z tyłu (bez czapki z daszkiem), złoty kolczyk, zielona koszula, skórzany fartuch na szelkach,
  ręcznik na ramieniu, w prawej dłoni kufel z pianą. Przegląd pozostałych: **mistrz gier** miał cylinder, monokl,
  podkręcony wąsik i muszkę (razem — maskotka znanej gry planszowej) → miękki beret w kolorze koła fortuny ze złotą
  kostką, okrągłe okulary (same oprawki), bródka bez wąsów; **trener** — czerwona opaska z białą koszulką była blisko
  znanego wojownika z bijatyk, a czerwoną opaskę ma już karczmarz → niebieska opaska na pot. Mag (fioletowa szata,
  spiczasty kapelusz z gwiazdką), zbrojmistrz (hełm z nosalem, ruda broda, skórzany fartuch, młot) i opiekunka
  (słomkowy kapelusz, rude warkocze, ogrodniczki) to ogólne typy fantasy/wiejskie — bez zmian.
- **Kamera we wnętrzach:** kamera gracza w Roblox (Poppercam) zatrzymuje się tylko na częściach **z kolizją**. Przy
  obróconej kamerze przy mistrzu gier wchodziła między tylną ścianę karczmy a tablicę zleceń (cały ekran zasłaniał tył
  deski), w sklepie magicznym — między ścianę a księgi na półce, a słupek ramy drzwi karczmy zasłaniał postać, gdy
  kamera stała za drzwiami. Teraz z kolizją: rama i deska tablicy zleceń (`budynki/karczma.py`), księgi i kryształy
  dolnej półki maga (`budynki/sklep_magiczny.py`, nad głową gracza) i rama otworu drzwi każdego sklepu
  (`wspolne.py`; wystaje 0,1 st w otwór — przejście bez zmian, `sprawdz.py` 0 błędów).
- Kontrola po zmianach: **0 błędów, 2 ostrzeżenia** (jak wcześniej). Styk z płytą Baseplate sprawdzony skryptem na
  `czesci.json`: żadna płaska część nie ma górnej ściany w płaszczyźnie gruntu (0,1) ani płyty (0,0) — nie ma czego
  migotać; 85 części wtopionych głębiej niż 0,05 jest pod gruntem i niewidocznych.
- Zrzut `klatki/u3_wnetrze.jpg` (ujęcie u3, tryb Edit) zrobiony ponownie z nowym karczmarzem i mistrzem gier.

## Czego nie sprawdzono

- Wyglądu w Roblox Studio — podglądy to rysunek z klocków (bez faktur, cieni rzucanych i świecenia Neonu).
- ~~Kolizji, kamery we wnętrzach i chodzenia postacią w trybie Play~~ — sprawdzone 17.11.2026 (wyżej i w README pakietu gry).
- Telefonu: wydajności, czytelności, streamingu.
- Rozmiaru płyty Baseplate (założone ±1024, jak w planie Lasu).
- Podglądy z Lasem za Bramą Leśną doklejają do rysunku początek `swiat/las_pas/czesci.json` (inny etap, praca w toku) —
  te części nie należą do bazaru i nie ma ich w `czesci.json`.
