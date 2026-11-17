# swiat/bagno_pas — Bagno jako odcinek wąskiego pasa (plan z klocków)

Status: **propozycja** (17.11.2026) — nic tu nie jest kanonem i **w Studio nic nie jest zbudowane**. Ten etap to plan,
generator, kontrola i podglądy offline, tak jak było z lasem-pasem (`swiat/las_pas/`). Budowa w Studio dopiero po
akceptacji człowieka. Wymagania: D-061 (las → bagno → …), D-075 (pas biomów), D-076 (inkubator, przegrody, strażnik
otwiera następny biom; korekta Karola: ok. 10 h do ostatniego biomu), D-077 (przelot kamery), D-069 (wymagany build
nie może stać się wymaganą klasą). Zarys pozostałych biomów: `swiat/biomy/PLAN_BIOMOW.md`.

> **D-096 (17.11.2026):** ta mapa jest teraz **projektem** (57,5 s × 4,5 s). Gra buduje krótką mapę z `krotki/`
> (25 s × 4 s), którą robi z niej `swiat/biomy/przycinarka.py` — generator tutaj bez zmian. Plików w `krotki/` nie
> edytuj ręcznie; po zmianie projektu: `python -B swiat/biomy/przycinarka.py`.

> **W skrócie.** Robocza nazwa **„Moczary Krzywej Kładki”**. Bagno to ten sam pas 72 st co las (4,5 s biegu), za bramą
> do Bagna lasu-pasa: u 934…1880 (świat X 2034…2980, ta sama oś z = −700). Przez całe Bagno biegnie **Krzywa Kładka**
> z desek; obok woda bez kolizji (brodzi się), trawiaste kępy, błoto, cypryśniki z brodami mchu, trzcina, niska mgła.
> Układ jak w lesie: Pomost Przybycia z inkubatorem → **Rechotne Oczka** (Rechotek, Zwiadowca) → **Bulgotne
> Trzęsawisko** (Bulgotnik, Mag) → **Kłapiące Kępy** (Kłodokłap, Wojownik) → **Leże Ropuchy** (Ropucha z Chatką,
> rzadka) → **Topiel Strażnika** (Strażnik Topieli) → brama do Dżungli. Bieg od przybycia do bramy **57,5 s**.
> **9 017 części**, kontrola **0 błędów, 0 ostrzeżeń**.

## Położenie w pasie

- Układ pasa **jak w lesie-pasie** (`swiat/biom_las/pas/plan_pasa.json`): u wzdłuż (liczone od początku lasu), v w poprzek
  (v > 0 po prawej ręce idącego do bramy), świat Studio = (1100 + u; y; −700 + v), **bez obrotu**. Szerokość pola gry
  72, kulisy po 24, niewidzialna ściana |v| = 38.
- Z planu lasu wzięte: brama do Bagna **u 934** (palisada lasu u 932–936 zostaje częścią `Workspace/LasPas`),
  rezerwacja Bagna **u 940…1880**, punkt przybycia **„bagno” u 954**, patrzy na u 1000. Brama do Dżungli **u 1874**
  (934 + 940, ta sama odległość co w lesie), Dżungla zaczyna się na u 1880 (rezerwacja z planu lasu).
- Części Bagna: **u 936…1906** (X 2036…3006), |v| ≤ 90. Płyta Bagna od u 966 (płyta lasu kończy się na 966). Kulisy
  Bagna od u 970 — kulisy lasu do u 966 zostają jako skraj lasu za bramą.
- **Przed budową trzeba usunąć `Workspace/LasPas/ZapowiedzBagna`** (u 934–966, z niewidzialną ścianą na u 965 —
  stoi tam, gdzie Pomost Przybycia). Las-pas opisuje to jako krok „po zbudowaniu Bagna”. Kontrola sprawdza, że nic
  z Bagna nie wchodzi w resztę części lasu-pasa.

## Pliki

| Plik | Co to jest |
|---|---|
| `plan.py` → `plan_bagna.json` | plan w formacie planu lasu (pas, przegrody, przejścia, miejsca, strefy, Strażnik, przelot, punkty przybycia, czas) + opisy potworów; `python -B swiat/bagno_pas/plan.py` drukuje czasy |
| `kontekst.py` | klasa `Bagno` (dziedziczy `las_pas.kontekst.Pas`), `ZasadyBagna` (dziedziczy `las_pas.zasady.Zasady`), oś Krzywej Kładki, paleta Bagna |
| `rosliny.py` | nowe rodziny: cypryśnik, wierzba płacząca, korzeniak, suche drzewo z brodą, kępa trzciny, grzybień, błędny ognik |
| `teren.py` | płyta, woda i toń bez kolizji, kępy, błoto Trzęsawiska, rowy, Krzywa Kładka, wydeptane pętle, niska mgła, lilie |
| `miejsca.py` | Pomost Przybycia (+ Kamień Powrotu i stanowisko jajka z lasu-pasa), punkty orientacyjne, przejścia, domy potworów, rekwizyty, Topiel, brama do Dżungli, zapowiedź Dżungli |
| `kulisy.py` | kulisy (skraj, przód z kolizją, drugi rząd, głąb), tło, niewidzialne ściany, drobiazgi przy kładce, runo |
| `generuj.py` | generator → `czesci.json`, `znaczniki.json`, `plan_bagna.json` + raport (kod 1 = część bez roli faktury albo limit) |
| `sprawdz.py` | **kontrola offline** (kod 1 = błąd) |
| `podglad.py` | **podgląd bez Blendera** (rysownik lasu-pasa) → `podglad/*.jpg` (≤ 1280 px) + `ujecia_swiat.json` |
| `czesci.json` | wynik: 9 017 części, format `swiat/biblioteka/scena.py` (`biblioteka-v2`), kontener `Workspace/BagnoPas` |
| `znaczniki.json` | wynik: te same rodzaje znaczników co las-pas: start/przybycie, inkubator, przegrody i przejścia, strefy z węzłami i domami (pas i świat), Strażnik, brama do Dżungli (zamiast `brama_bagna`), przelot kamery w świecie, punkty E, punkty przybycia, strefy spokoju, mgła, streaming |
| `podglad/` | `gora.jpg`, `gora_strefy.jpg` (rzut z góry), `oczka`, `trzesawisko`, `kepy_leze`, `topiel_brama` (z ukosa), `oczy_przybycie`, `oczy_kepy` (z oczu gracza) |

## Polecenia (z głównego folderu repozytorium)

```
python -B swiat/bagno_pas/generuj.py     # ok. 3 s: plan_bagna.json, czesci.json, znaczniki.json, raport
python -B swiat/bagno_pas/sprawdz.py     # ok. 3 s: kontrola (woła też tools/studio_buduj.py --sucho)
python -B swiat/bagno_pas/podglad.py     # ok. 35 s: podglad/*.jpg i ujecia_swiat.json (--tylko gora,oczka; --wyj <folder>)
python -B swiat/bagno_pas/plan.py        # sam plan + tabela czasów
```
Wynik deterministyczny (`--ziarno 11`). Wymagane: numpy, Pillow. Bez Blendera i bez Studio.

## Plan (u w układzie pasa; bieg 16 st/s)

| Odcinek | u | Bieg przez | Od przybycia | Co tam jest |
|---|---|---|---|---|
| brama lasu (las-pas) | 934 | — | — | palisada lasu za plecami przybywającego |
| **Pomost Przybycia** (strefa spokoju) | 940–1004 | 4,0 s | 0 s | pomost 12 × 12 z rombem światła (u 954), stanowisko jajka na pomoście (972; 22), Kamień Powrotu (948; −24), łąka, lampiony |
| rów z kładką | 1004–1016 | 0,8 s | | płytki rów w poprzek pasa, kładka 12 szer. |
| **Rechotne Oczka** (3 kojce po 64) | 1016–1208 | 12,0 s | 3,9 s | jasne kępy na płytkiej wodzie, oczka i pałki, łódki; **Chata na Palach** (1144; 30, wys. 17) |
| Kładka nad Topielą | 1208–1228 | 1,3 s | | ciemna, szersza woda, kładka 12 z poręczami ≤ 1,4 |
| **Bulgotne Trzęsawisko** (3 kojce) | 1228–1420 | 12,0 s | 17,1 s | ciemne błoto, bąblujące kałuże, niska trzcina 0,8 między kojcami (przerwa 24), lampiony; **Stary Cypryś** (1356; 32, wys. 31) |
| trzcinowa przesieka | 1420–1436 | 1,0 s | | ściany trzciny 5–6 wys., przejście 32 |
| **Kłapiące Kępy** (3 kojce) | 1436–1628 | 12,0 s | 30,1 s | ciemne kępy na czarnej toni, korzeniaki, kłody, pniaki; **Wrak Łodzi** (1564; 30, wys. 19) |
| zatopione pnie | 1628–1644 | 1,0 s | | karpy i zwalone pnie 5–8,5 wys., przejście 28, pale z czaszką |
| **Leże Ropuchy** | 1644–1744 | 6,2 s | 43,1 s | udeptana łacha z kałużami, głazy, kości; **Ropusza Chata** (1724; −30, wys. 18) z kominem i kotłem |
| Latarnie Topieli | 1744–1760 | 1,0 s | | dwa krzywe słupy 14 z zielonymi latarniami (1752; ±16), niskie korzenie |
| **Topiel Strażnika** | 1760–1848 | 5,5 s | 50,4 s | okrągły pomost r 27 (wierzch 0,3) na toni, 8 pni z latarniami na r 26, Strażnik w (1814; 0) twarzą do wejścia; **Wieża Topieli** (1848; 27, wys. 40) z boku osi |
| przedbramie (strefa spokoju) + brama do Dżungli | 1848–1880 | 2,0 s | | ławka, lampiony, skrzynie; palisada z pni oplątana lianami, wrota 16 (u 1874) |
| zapowiedź Dżungli (osobna grupa) | 1876–1906 | | | soczysta trawa, olbrzymie liście, palmy, niewidzialna ściana u 1905 |

Od przybycia (u 954) do bramy do Dżungli (u 1874): **57,5 s**; sąsiednie miejsca walki dzieli **4,0–7,5 s**.

## Potwory (tylko opis — modele po akceptacji)

Kształty pętli i domów jak w lesie: pętla 8 węzłów 36 × 44 (obwód 138), dwa domy pod ścianami (|v| = 34, 13,4 od
węzła), leże — pętla 6 węzłów. Odstęp 25, smycz 10, plac walki r 12. Gracz ma 5,7 st wzrostu.

| Strefy | Potwór | Klasa | Wygląd | Wys. (st) | Poziomy: rosnący / równy | Naraz 1/8/20 | Odrodzenie |
|---|---|---|---|---|---|---|---|
| r1 · r2 · r3 | **Rechotek** | Zwiadowca | przysadzista ropucha z klocków, płaski łeb, oczy-kulki, skacze susami; oliwka 7E8C3E w ciemne plamy, żółty brzuch, pomarańczowe oczy | 3,0 (dł. 3,6) | 11 · 11–12 · 12–13 / 11–12 · 12–13 · 13–14 | po 2/4/5 | 12 s |
| b1 · b2 · b3 | **Bulgotnik** | Mag | mały błotny szaman: kopczyk z błota na nóżkach, głowa to bańka gazu z oczami, kij z ognikiem | 4,2 | 13–14 · 14 · 14–15 / 15–16 · 16–17 · 17–18 | po 2/4/5 | 15 s |
| k1 · k2 · k3 | **Kłodokłap** | Wojownik | żywa omszała kłoda na łapach-korzeniach, przód rozcięty w paszczę z kołkami-zębami, grzybek na grzbiecie | 3,2 (dł. 8,6) | 15–16 · 16–17 · 17 / 19–20 · 20–21 · 21–22 | po 2/3/4 | 18 s |
| t1 | **Ropucha z Chatką** (rzadka) | Mag | ogromna stara ropucha z krzywą chatką na grzbiecie; z komina dym | 11 (szer. 12) | 18 / 23–24 | 1 | 150 s stałe |
| — | **Strażnik Topieli** | strażnik (pół na pół: fizyczne i magiczne) | olbrzym z błota i korzeni wynurzony z wody, przewrócona łódka jak kapelusz, w piersi zielona latarnia, broda mchu | 16 (szer. 10) | 19 / 25 | 1 | 120 s stałe |
| **razem** | | | | | | **20 / 35 / 44** (ze Strażnikiem) | |

Walka (propozycja do danych silnika): Rechotek często unika, „lepki język” spowalnia (efekt Spowolnienie); Bulgotnik
bije słabo, „bańka gazu” rani magią i spowalnia; Kłodokłap ma gruby Pancerz, mocno gryzie, czasem ogłusza, nie unika;
Ropucha — dym z komina truje i spowalnia, skok rani fizycznie; Strażnik — „wciągnięcie w topiel” unieruchamia (jak
Uścisk korzeni), uderzenie błotem rani magią. **Bagno uczy długiej walki**: Spowolnienie i trucizna wydłużają starcie,
więc płaci się za Kondycję i rozsądny Pancerz / odporność na magię.

**D-069 (wymagany build ≠ wymagana klasa).** W trzech przegrodach jest po jednym potworze każdej klasy (kontrola to
sprawdza), a nacisk Bagna idzie przez cechy dostępne każdej klasie: Kondycja (pula życia — wszyscy), Pancerz (punktowo,
wszyscy), Inteligencja (odporność na magię — wszyscy). Wojownik: Pancerz i tarcza na Kłodokłapy, punkty w Inteligencję
na Bulgotniki. Zwiadowca: unik na Kłodokłapy, Kondycja na długie walki. Mag: naturalnie odporny na Bulgotniki (jego
Inteligencja), więc Bagno nie może być „samą magią” — Kłodokłapy i połowa ciosów Strażnika są fizyczne. Ryzyko: Mag ma
lżej w Trzęsawisku i na Ropusze, Wojownik — w Kępach; do sprawdzenia w tabeli balansu.

**Ile walk na minutę** (wzór z `sprawdz_plan.py` lasu): Oczka 23,5 / 15,8 przy 8 graczach (walka 15 / 30 s), bez
czekania 9 graczy w przegrodzie; Trzęsawisko 20,8 / 14,5, 9; Kępy 14,5 / 10,3, 6 (mniej, większych potworów); Leże 0,3
(rzadka z założenia). Jeden gracz oglądający walki ×1 nigdy nie czeka w kojcu swojego poziomu (kontrola).

## Czas

Model tempa `tools/walka/tempo.py` (krzywa 11,71 × L^1,6, ta sama co dla lasu): Bagno **45 min ≈ 83 walki** (tempo
rosnące 30/45/60/75/95/125/170, poziomy 11–19) albo **ok. 95 min ≈ 174 walki** (tempo równe po lesie: las 30 min,
pozostałe sześć biomów po ok. 95; poziomy 11–25). Przy szacowanych czasach walk Bagna (Rechotek 18 s, Bulgotnik 17,
Kłodokłap 21, Ropucha 26, Strażnik 32 — **szacunek**, potwory nie mają danych walki) plan daje 48,9 / 100,1 min przy
walkach ×1 (26,4 / 51,4 min z pomijaniem), chodzenie **7,6% / 6,8%**. Mapa jest tak długa jak las: dłuższy czas ma
wynikać z liczby walk i treningu, nie z chodzenia (plan lasu, rozdz. 5).

## Liczby

**9 017 części** (las-pas 8 601; cel ok. 9 000, limit 12 000). Na odcinek: Pomost Przybycia 406, rów 166, Rechotne
Oczka 1 835, Kładka nad Topielą 202, Trzęsawisko 1 649, przesieka 225, Kępy 1 901, zatopione pnie 149, Leże 977,
Latarnie 135, Topiel 768, przedbramie z bramą 362, zapowiedź Dżungli 242. Na grupę: Kulisy 5 164, Detale 867, Teren 802,
Tło 468, Ozdoby 460, Przejścia 350, Ścieżka (kładka) 308, Punkty 174, Domy 124, BramaDzungli 82, ZapowiedzDzungli 70,
Arena 48, Trzęsawisko 29, Przedbramie 27, Mgła 20, Wejście 14, Piny 10 (ognisko Kamienia Powrotu). Neon 82, kule 62,
walce 1 133, półprzezroczyste 20 (niska mgła), niewidzialne 5, z kolizją 11%. Materiały: SmoothPlastic 54%, Wood 29%,
Grass 9%, WoodPlanks 4%, Ground, Mud, Rock, Metal, Neon po ok. 1%.

## Co pilnuje kontrola (`sprawdz.py`, wynik 17.11: 0 błędów, 0 ostrzeżeń)

Plan: pojemność pętli, place walki r 12 w polu gry, domy 12–20 od węzłów, węzły ≥ 25 od przybycia, jajka i Kamienia,
**D-069** (trzy przegrody = trzy klasy), jeden gracz ×1 nie czeka na odrodzenie, przelot kamery (ta sama krzywa
Catmull-Rom co w lesie: w pasie, 3–80 nad gruntem, najszybciej 110 st/s, 13,4 s, nie przez punkty orientacyjne,
kończy na Strażniku, ryk w zatrzymaniu, każda przegroda pokazana). Części: format `tools/studio_buduj.py`
(`las_pas.sprawdz.sprawdz_format` z kontenerem Bagna) i jego `--sucho`; limity i sufity; granice u 936…1906, |v| ≤ 90;
skrzynki miasteczka, starego lasu, prototypów i Baseplate; **brak nachodzenia na las-pas** poza `ZapowiedzBagna`; place
walki r 12 wolne 1,6–18 przy 79 węzłach; Krzywa Kładka wolna 0,6–7; otwarcia pięciu przejść; pętle; przelot kamery na
częściach (269 próbek); grunt bez dziur (płyta Bagna + płyta lasu do u 966); teren płaski; woda bez kolizji;
niewidzialne ściany (|v| = 38 od u 964 do 1904, u 1905); wrota do Dżungli zamykają otwarcie 16 na wys. ≥ 7; punkty E;
wymagane grupy i domy; znaczniki zgodne z planem; każda część ma rolę faktury. Plik `plan_bagna.json` musi zgadzać się
z `plan.py`.

## Co użyte ponownie, co nowe

- **Import bez zmian** (nic nie kopiowane): `swiat/biblioteka/scena.py`, `swiat/biom_las/paleta.py`, `faktury.py`
  (`naloz`, role; + nazwy dodatkowe lasu-pasa i 31 nowych nazw Bagna w `generuj.FAKTURY_BAGNA`; `Płyta` dostaje błoto
  Mud), `rosliny.py` (suche drzewo, trzcina, pniak, kulisa, kwiaty), `skaly.py`, `detale.py`, `teren.py` (wstęga, dysk,
  wielokąt), `lokacje/wspolne.py`, `swiat/krzywe_miasteczko/zestaw.py`; z lasu-pasa: `kontekst.Pas` (maski i miejsce),
  `zasady.Zasady` (plac, otwarcia, pętle, kamera) i `postaw`, `punkty.kamien_powrotu`, `punkty.stanowisko_jajka`,
  `kulisy.drzewo` / `drobne` / `bez_kolizji`, `generuj.FAKTURY_DODATKOWE`, rysownik `podglad.py`, `sprawdz.sprawdz_format`;
  `swiat/biom_las/pas/sprawdz_plan.py` (krzywa przelotu, przepustowość, obwód).
- **Nowe**: plan Bagna, oś Krzywej Kładki i zasada ścieżki/granic dla Bagna, rodziny roślin Bagna, woda i kępy, kładki,
  punkty orientacyjne, przejścia, domy, Topiel, brama do Dżungli, zapowiedź Dżungli, kontrola i kadry podglądu.

## Budowa w Studio (następny etap, po akceptacji — dokładne polecenia)

Studio w trybie **Edit**, wspólne miejsce Team Create: budujemy tylko własny kontener, punkty historii robi narzędzie.
```
# 0. zgłoś pracę (CLAUDE.md) — obszar Bagna i lasu-pasa (usuwamy z niego ZapowiedzBagna)
python panel/narzedzia/praca.py start --id bagno-pas-studio --tytul "Bagno-pas w Studio" --koniec +45m --obszar studio:BagnoPas --obszar studio:LasPas --obszar mapa:bagno_pas --stop-przy-kolizji

# 1. świeży plik i kontrola (kod 0)
python -B swiat/bagno_pas/generuj.py
python -B swiat/bagno_pas/sprawdz.py

# 2. usunąć Workspace/LasPas/ZapowiedzBagna (punkt historii przed i po) — dziś nie ma do tego narzędzia: albo krótki
#    skrypt Luau przez tools/studio_mcp.py, albo przełącznik w swiat/las_pas/generuj.py (zmiana lasu-pasa — za zgodą)

# 3. budowa: kasuje TYLKO Workspace/BagnoPas z atrybutem Wygenerowane; ok. 31 paczek po 300 części
python -B tools/studio_buduj.py swiat/bagno_pas/czesci.json --paczka 300 --czekaj 20

# 4. streaming: Punkty/* i BramaDzungli/* → Persistent (10 grup), Kulisy/<strona>/O_* i Tlo/<strona>/O_* → StreamingMesh (61)
python -B swiat/biom_las/studio_atrybuty.py --znaczniki swiat/bagno_pas/znaczniki.json --sucho
python -B swiat/biom_las/studio_atrybuty.py --znaczniki swiat/bagno_pas/znaczniki.json

# 5. zrzuty z tych samych kamer co podglądy, potem migawka i raport w panelu (skill panel)
python -B tools/studio_zrzuty.py swiat/bagno_pas/ujecia_swiat.json --wyj <folder> --czekaj 20 --rozmiar 1600
python panel/narzedzia/migawka.py --tytul "Bagno-pas w Studio" --korzen Workspace/BagnoPas

# cofnięcie: Ctrl+Z albo
python -B tools/studio_buduj.py swiat/bagno_pas/czesci.json --usun
python panel/narzedzia/praca.py koniec --id bagno-pas-studio
```
`studio_atrybuty.py --sucho` na tych znacznikach działa już dziś (sprawdzone: 10 grup Persistent, 61 StreamingMesh).

**Potem (skrypty gry):** `swiat/las_pas_gra/zrodlo_mapy.py` ma na sztywno ścieżki lasu i pole `brama_bagna` — trzeba
mu podać plan i znaczniki Bagna (`plan_bagna.json`, `znaczniki.json` → `brama_dzungli`); potwory Bagna potrzebują
danych walki (`tools/walka/dane_walki.json`) i modeli; mgła lokalna Bagna (prostokąt i kolory w `znaczniki.json` → `mgla`);
przelot kamery z `przelot_kamery.punkty_swiat`; brama do Dżungli otwierana graczowi po Strażniku Topieli.

## Ustawienia przyjęte, do zmiany

- Kontener `Workspace/BagnoPas`; układ i oś pasa jak w lesie (X0 1100, Z0 −700, bez obrotu), pole gry 72, kulisy 24.
- Bagno u 934…1880 (z planu lasu), przybycie u 954, brama do Dżungli u 1874, zapowiedź Dżungli do u 1906.
- Długość jak las (57,5 s biegu); dłuższy czas biomu z liczby walk (45 min ≈ 83 walki albo 95 min ≈ 174).
- Poziomy: w `poziomy` tempo rosnące (11–19, Strażnik 19), w `poziomy_rowny` tempo równe po lesie (11–25, Strażnik 25).
- Pętle, domy, odstęp, smycz i plac walki jak w lesie; naraz/max 4/5 (Kłodokłap 3/4), odrodzenie 12 / 15 / 18 s,
  Ropucha 150 s stałe, Strażnik 120 s stałe.
- Teren płaski (y 0); woda to tafla bez kolizji 0,2 nad gruntem — gracz brodzi bez spowolnienia; kładka ≤ 0,45 (grunt),
  pomost Topieli 0,3.
- Ten sam Kamień Powrotu (E → miasteczko) i to samo stanowisko jajka co w lesie (import z lasu-pasa).
- Kulisy Bagna od u 970; kulisy, płyta i ścieżka lasu do u 966 zostają.
- Czasy walk potworów Bagna: szacunek 18 / 17 / 21 / 26 / 32 s.
- Niska mgła: 20 półprzezroczystych dysków (limit 30) + mgła lokalna u gracza (propozycja FogColor 9AA58E, FogEnd 260);
  wspólnego `Lighting` nie zmieniamy.
- Paleta w zgodzie z makietą przejścia przez chmury (`swiat/teleport_chmury/krainy.json`: grunt 7E8C3E, podłoże 4A3F2A,
  droga 9C7A4A).
- Ziarno generatora 11.

## Wybory dla ludzi

1. **Tempo Bagna:** 45 min (poziomy 11–19) czy ok. 95 min (11–25)? Mapa ta sama, zmieniają się poziomy i liczba walk.
2. **Nazwa:** „Moczary Krzywej Kładki” czy inna?
3. **Potwory:** Rechotek (Zwiadowca), Bulgotnik (Mag), Kłodokłap (Wojownik), Ropucha z Chatką (rzadka), Strażnik
   Topieli — zostają czy wymienić któregoś? Modele robi Karol w Blenderze (D-065) dopiero po akceptacji.
4. **Strażnik Topieli i Ropucha:** wspólni dla serwera (jak w lesie) czy osobni dla gracza?
5. **Woda:** brodzenie bez spowolnienia (propozycja) czy woda spowalnia poza kładką (czasy biegu urosną)?
6. **Niska mgła z części:** zostaje (20 dysków) czy tylko mgła lokalna u gracza? Dyski mogą w Roblox wyglądać jak szkło.
7. **Teleport:** tylko Pomost Przybycia czy także punkt „przed Topielą” (u 1752) po pierwszym dojściu?
8. **Zapowiedź Bagna w lesie-pasie:** usunąć ręcznie w Studio czy dodać do generatora lasu-pasa przełącznik (zmiana w
   `swiat/las_pas/`)?

## Czego nie sprawdzono

- **Wygląd w Roblox**: podglądy to własny rysunek brył w Pillow (bez faktur, cieni, poświaty Neonu, mgły i światła
  miejsca); nie wiadomo, jak wyglądają półprzezroczyste dyski mgły i woda Mud/SmoothPlastic w świetle pasa.
- **Ruch w trybie Play**: wejście na kładkę (0,4) i pomost, brodzenie, kolizje wrót, czy potwory chodzą po kępach
  i przez kładkę tak, jak pętle w planie.
- **Telefon i streaming**: 9 tys. części Bagna obok 8,6 tys. lasu, przelot kamery.
- Czasy walk i poziomy potworów Bagna (brak danych walki; poziomy z modelu tempa, nie z gry).
- Styk z lasem w Studio (ZapowiedzBagna) i to, czy skrypty gry lasu dadzą się użyć dla Bagna bez zmian.

## Znane słabości

- Środek kojców jest pusty z założenia (place walki r 12 muszą być wolne) — życie dają kulisy, kępy, kładka i rekwizyty
  pod ścianami.
- Kulisy z bliska bywają regularne jak aleja; tło to proste bryły-sylwetki (jak w lesie-pasie).
- Ogniki (świecące kostki) wiszą w powietrzu z założenia — w podglądzie wyglądają jak zwykłe kostki.
- Pomost Przybycia z góry zlewa się z kładką; Wieża Topieli z góry chowa się w koronach kulis (z boku jest widoczna).
- Lista materiałów w `czesci.json` zawiera dwa nieużywane wpisy (LeafyGrass, Slate) po nadpisaniu ról — nieszkodliwe.
