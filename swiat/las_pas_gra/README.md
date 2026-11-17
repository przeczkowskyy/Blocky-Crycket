# Las-pas w grze — potwory w przegrodach, brama, teleport, mgła, przelot kamery

*Status: **propozycja** (16–17.11.2026). Kod sprawdzony bez Studio, a 17.11.2026 w nocy **wdrożony do Studio
i sprawdzony w trybie Play** (jeden gracz, komputer; wyniki niżej, rozdz. „Co sprawdzone w grze”). Źródło wymagań:
plan `swiat/biom_las/pas/PLAN_PASA.md` (zaakceptowany plan lasu) i decyzje D-075,
D-076, D-077 (przelot przy pierwszym wejściu, bez pomijania). D-078 (pomijanie walk) nie należy do tego pakietu.
Ustawienia przyjęte przez właściciela: Strażnik i Troll wspólni dla serwera, walka na arenie prototypu, teleport do
wejścia biomu, przelotu nie da się pominąć, stary las zostaje nietknięty i działa dalej.*

> **W skrócie.** Jeden kontener `Workspace/LasPasGra` (atrybut `Wygenerowane = true`, osobny od
> `Workspace/LasPotwory`) obok mapy z klocków `Workspace/LasPas` (robi ją inny agent w `swiat/las_pas/`). W nim:
> **ten sam kod potworów** co w starym lesie (`swiat/las_potwory`), uruchomiony na nowych danych — 10 stref w
> przegrodach pasa i Strażnik (20 / 36 / 46 potworów przy 1 / 8 / 20 graczach); **brama do Bagna** zamknięta, dopóki
> gracz nie pokona Strażnika (otwiera się tylko u niego, serwer cofa nieuprawnionych); **teleport** — dzisiejsza brama
> w miasteczku prowadzi na Polanę Przybycia pasa, gdy jest mapa, a Kamień Powrotu wraca do miasteczka (od 17.11.2026 do
> nowego miasteczka-bazaru, gdy stoi `Workspace/MiasteczkoBazarGra`; inaczej do starego); **mgła** tylko
> u gracza w prostokącie pasa; **przelot kamery** 13,4 s przy pierwszym wejściu z rykiem Strażnika, bez pomijania.

## Pliki

| Plik | Co to jest |
|---|---|
| `zrodlo_mapy.py` | cienka warstwa źródła mapy: znaczniki `swiat/las_pas/znaczniki.json` + Płyta z `czesci.json`, gdy są, inaczej sam plan; przy obu sprawdza zgodność (rozjazd = błąd) |
| `generuj_dane.py` | generator: `zrodla/DanePotworowPasa.luau` (format `DanePotworow` starego lasu) i `zrodla/DanePasa.luau` (liczby świata dla skryptów pasa); `--sprawdz`, `--wyjscie DIR`, `--bez-mapy` |
| `logika_pasa.py` | lustro `zrodla/LogikaPasa.luau` w Pythonie (te same funkcje i 39 przypadków wzorcowych) |
| `zrodla/LogikaPasa.luau` | czysta logika: prostokąty, waga mgły, brama, ratunek, krzywa Catmull-Rom przelotu, automat przelotu |
| `zrodla/PamiecGracza.luau` | co serwer pamięta o graczu (przelot widziany, Strażnik pokonany) — dziś w pamięci, z opisanym miejscem na zapis |
| `zrodla/SerwerPasa.server.luau` | serwer: brama, cofanie, ratunek, przekierowanie bramy miasteczka, Kamień Powrotu, przelot, uchwyty |
| `zrodla/KlientPasa.client.luau` | klient: przelot kamery (ze sprzątaniem), otwieranie bramy u zwycięzcy, komunikaty, baner |
| `zrodla/MglaPasa.client.luau` | mgła tylko u gracza (Atmosphere lokalnie), prostokąt pasa, łagodne wejście i wyjście |
| `zrodla/DanePotworowPasa.luau`, `zrodla/DanePasa.luau` | **wygenerowane** — nie edytować ręcznie |
| `sprawdz_luau_pasa.py` | kontrola statyczna Luau pakietu (bilans, strażnik, zakazy, Lighting tylko w mgle) + parsowanie interpreterem `tools/walka/luau_mini.py`, gdy jest |
| `zbuduj.py` | budowa kontenera w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_pasa.py` | 45 testów offline (opis w nagłówku pliku) |
| `testy/proba_play.py` | próba w Studio (Play) z listą kontrolną P01–P16 i listą zrzutów |
| `testy/proba_dodatkowa.py` | druga próba w Play: obie drogi do lasu z przelotem, bieg Polana → brama, ściany i ratunek, walka z każdym gatunkiem, Strażnik (przegrana i wygrana), koszt przy pełnym zestawie, ujęcia potworów |
| `wyniki/` | zapisy prób w Play (JSON, zapisywane po każdym kroku) |
| `klatki/` | wybrane zrzuty z gry (bez filmów) |

## Co jest w kontenerze `Workspace/LasPasGra`

| Ścieżka | Klasa | Skąd |
|---|---|---|
| `Moduly/{Stale, Logika, Wzorcowe, Walka/*}`, `SerwerPotworow`, `KlientPotworow` | moduły i skrypty | **te same pliki** co stary las (lista z `swiat/las_potwory/zbuduj.py`, kopia silnika `src/server/Walka` przy budowie) |
| `Moduly/DanePotworow` | ModuleScript | `zrodla/DanePotworowPasa.luau` (strefy pasa) |
| `Moduly/{DanePasa, LogikaPasa, PamiecGracza}`, `SerwerPasa`, `KlientPasa`, `MglaPasa` | moduły i skrypty | ten pakiet |
| `Stan/` | Folder | serwer potworów wkłada tu `Configuration` żywych potworów (Play) |
| `Zdalne/RozpocznijWalke2` (RemoteFunction), `Zdalne/ZdarzeniaPasa` (RemoteEvent) | zdalne | walka (odtwarzacz prototypu); przelot i komunikaty |
| `Sygnaly/{SterowanieSerwera, SterowanieKlienta}` | BindableFunction | haczyki potworów (klient ma nowe `"wymus"`, `"klip"`) |
| `Sygnaly/WynikWalki` | BindableEvent | serwer potworów → serwer pasa: wynik przyjętej walki (brama) |
| `Sygnaly/PrzeniesDoLasu` | BindableFunction | **uchwyt dla innych skryptów serwera** (przejście przez chmury) |
| `Sygnaly/{SterowaniePasa, SterowaniePasaKlienta}` | BindableFunction | haczyki testowe pasa |
| `Brama` (Model, Persistent): `Zapora`, `Napis` | części | niewidzialna zapora przez cały pas (40 wys.) i napis „ZAMKNIĘTE / Pokonaj Strażnika Gaju” |
| `ZaBrama`: `Podloga`, `Sciana`, `Tabliczka` | części | zapasowa niewidzialna podłoga i ściana za bramą, tabliczka „BAGNO — WKRÓTCE” |
| `Punkty/KamienPowrotu` | część + ProximityPrompt | punkt E przy Kamieniu Powrotu z mapy → start nowego miasteczka-bazaru (uchwyt `MiasteczkoBazarGra/Sygnaly/PrzeniesDoBazaru`), a bez niego → stare miasteczko |

Atrybuty kontenera ustawiane przy budowie: `Wygenerowane`, `Zrodlo`, `Zbudowano`, `Skrot` oraz nadpisania stałych
pakietu potworów `Stale_*`: `NAZWA_KONTENERA = LasPasGra`, `NAZWA_BIOMU = LasPas` (promień do gruntu), `NAZWA_SZABLONOW
= LasPasGraSzablony` (osobna kopia szablonów w ReplicatedStorage — stary las ma swoją), `SZABLONY` (z `lesny_troll`),
`PREFIKS = [LasPasGra] `, `GUI_BOHATERA`, `GUI_BANERA`, `PANEL_Y = 48` (panel bohatera pasa pod panelem starego lasu),
`PANEL_PREFIKS = "Las-pas · "`. Atrybuty testowe (ustawia człowiek w Edit, przechodzą przy odbudowie): `ZiarnoTestowe`,
`TestBezSesji`, `TestGraczy`, `TestBezBiomu` (pakiet działa bez mapy), `PrzekierujBrameMiasteczka` (`false` = brama
w miasteczku zostaje przy starym lesie), `MglaWylaczona`.

## Jak zbudować i usunąć

```
python -B swiat/las_pas_gra/generuj_dane.py          # po każdej zmianie planu albo mapy (tabela stref na ekranie)
python -B swiat/las_pas_gra/testy/test_pasa.py       # 45 testów, ok. 3 s
python -B swiat/las_pas_gra/zbuduj.py --sucho        # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/las_pas_gra/zbuduj.py                # Studio w trybie Edit: buduje / odbudowuje Workspace/LasPasGra
python -B swiat/las_pas_gra/zbuduj.py --skrypty      # tylko kod, zdalne i Stale_* (bez części)
python -B swiat/las_pas_gra/zbuduj.py --usun         # usuwa Workspace/LasPasGra (stary las zostaje)
```

Przy kilku oknach Studio dopisz `--studio <studio_id>`. Budowa sprawdza `game.PlaceId` gry w każdym wysyłanym kodzie,
działa tylko w trybie Edit, rusza tylko kontener z `Wygenerowane`, robi punkty historii (Ctrl+Z cofa całość) i niczego
nie publikuje ani nie zapisuje.

## Kolejność wdrożenia w Studio (następny etap)

1. `git pull`, potem offline: `python -B swiat/las_potwory/testy/test_logiki.py`, `python -B
swiat/las_potwory/testy/test_styku.py`,
   `python -B swiat/las_potwory/sprawdz_luau.py`, `python -B swiat/las_pas_gra/testy/test_pasa.py`,
   `python -B swiat/las_pas_gra/zbuduj.py --sucho` — wszystko kod 0. Zgłoś pracę: `python panel/narzedzia/praca.py start
   --id las-pas-gra --tytul "Las-pas: potwory, brama, przelot" --koniec +60m --obszar studio:LasPasGra --obszar
   swiat/las_pas_gra --stop-przy-kolizji`.
2. Mapa: `Workspace/LasPas` musi stać w Studio (buduje ją pakiet `swiat/las_pas/` — jego README). Bez niej potwory i
   brama nie startują (`StanBiomu`/`StanMapy`), a brama miasteczka prowadzi dalej do starego lasu.
3. Prototyp walki: `Workspace/TestWalki2` z `Aktorzy/lesny_troll` (nowy gatunek w pasie). Brak jednego szablonu = cały
   klient potworów pasa w trybie brył zastępczych (zachowanie pakietu potworów) — `zbuduj.py` ostrzega.
4. `python -B swiat/las_pas_gra/zbuduj.py` (tryb Edit). Ma wypisać „w miejscu (tylko odczyt): …” z Płytą
   (1566, −1, −700), 1000 × 2 × 176, obrót 0, a na końcu „części: 7” (zapora, napis, podłoga, ściana, słupek, deska,
   punkt E) i `Skrot` równy temu z `--sucho`. Silnik walki musi być tą samą wersją co w `TestWalki2`: gdy
   `src/server/Walka` jest w trakcie zmian, ustaw przed budową `BC_SILNIK_KORZEN` na katalog z kopią zatwierdzonej
   wersji (tak budowano 17.11.2026 — silnik v2, bo v3 czeka na odtwarzacz).
5. Próba w Play: `python -B swiat/las_pas_gra/testy/proba_play.py <folder poza repo>` — lista P01–P16 z wynikami w
   `<folder>/lista.txt` i `wyniki.json`, zrzuty 01–20 w tym samym folderze. Potem
   `python -B swiat/las_pas_gra/testy/proba_dodatkowa.py <folder zrzutów poza repo>` (ok. 10 min; JSON w `wyniki/`).
   Ręcznie: telefon (emulator Studio) i dwóch graczy (Test → Clients and Servers, 2): brama otwarta tylko u
   zwycięzcy, drugi cofany.
6. Raport na panel z zrzutami (skill `panel`), wpisy w sejfie (stan wdrożenia, Dziennik zmian) i `praca.py koniec`.

## Co sprawdzone bez Studio (17.11.2026)

- **Dane** (`generuj_dane.py`, testy 1a–1d): plik deterministyczny i aktualny; ze znacznikami mapy i bez nich (sam
  plan) strefy i przelot wychodzą identyczne; przesunięty węzeł w kopii znaczników → błąd; 20 / 36 / 46 potworów
  (ze Strażnikiem) — to samo co `sprawdz_plan.py`.
- **Przegrody** (2a–2e): gatunek, poziomy, liczby i odrodzenie jak w planie; trasy, domy i odcinki dom → przedpole
  w polu strefy, w kojcu i w pasie, poza strefami spokoju; symulacja ruchu (ta sama klasa `Symulacja` co w testach
  starego lasu, lustro tyknięcia `SerwerPotworow`) 2 × 15 min na strefę z losowymi walkami: odstęp ≥ 25, nikt nie
  wychodzi z pola strefy, wszyscy wracają na pętlę; troll wraca po stałych 150 s także przy 5 graczach obok.
- **Brama** (3a–3d): decyzja serwera, otwarcie tylko po wygranej ze Strażnikiem (także złe dane), ratunek, położenie
  zapory, tabliczki, zabezpieczenia i punktów względem planu i mapy.
- **Przelot** (4a–4h): automat — pierwsze wejście, brak drugiego, klient niegotowy, brak odpowiedzi (serwer kończy
  sam), odmowa (ponowienie po 5 s), „odtwórz ponownie”, utrata postaci, opóźnienie `przelotPo`; 300 losowych przebiegów
  — postać zawsze odblokowana.
- **Krzywa** (5a–5d): próbki co 0,05 s identyczne z `sprawdz_plan.krzywa_kamery` (± 1e-6), kontrola przelotu planu
  0 błędów, najwyżej 110 st/s, postój 10,5–13,4 s na Strażniku, ryk 10,7–12,7 s mieści się w postoju (klip `ryk`
  Strażnika ma 2,0 s), cała trasa w lesie na wysokości 8–32.
- **Mgła** (6a–6c): prostokąt z planu, przejście 0 → 1 w ok. 1,25 s, mgła rozłączna z mgłą starego lasu, Lighting
  tylko przez `Atmosphere` w skrypcie mgły.
- **Luau** (7a–7e, gdy jest `tools/walka/luau_mini.py`): wszystkie 7 plików pakietu parsują się; `LogikaPasa` wykonana
  w interpreterze daje te same wyniki co lustro (39 przypadków, 250 losowych wywołań na funkcję, 60 losowych przebiegów
  automatu); oba wygenerowane moduły danych wczytane w Luau są równe danym z generatora.
- **Styki** (8a–8j): nazwy instancji, atrybuty, wiadomości zdalne (typy, id, limit), nadpisania `Stale_*`, haczyki
  `"wymus"`/`"klip"`, sprzątanie przelotu, strażnik Studio, brak ścieżek lokalnych, `zbuduj.py --sucho`, składnia kodu
  wysyłanego do Studio.
- **Stary las bez zmian w zachowaniu**: `test_logiki.py` 17/17, `test_styku.py` 15/15, `sprawdz_luau.py` 5/5,
  `generuj_dane.py --sprawdz` (skrót 3f657732d08e), `zbuduj.py --sucho` — przed i po zmianach.

## Co sprawdzone w grze (17.11.2026, Studio, tryb Play)

**Warunki.** Miejsce gry w Studio (Team Create), jeden gracz na komputerze, okno gry 2041 × 1153. Ekran był przykryty
czarnym oknem — Studio rysuje wtedy ok. 15 kl./s, więc czas klatki 66,7 ms to ograniczenie Studia, nie gry. Silnik
walki: kopia zatwierdzonej wersji v2 (ta sama co w `TestWalki2`; przy budowie zmienna `BC_SILNIK_KORZEN`), **nie**
wersja 3 z drzewa roboczego `src/server/Walka`. Kontener zbudowany 17.11 o 00:17 (Skrot `e8762ea11804`, 59 instancji,
18 skryptów, 7 części) i od tej pory bez zmian w kodzie gry pasa. Zapisy: `wyniki/*.json`, zrzuty: `klatki/`.

**Lista P01–P16** (`testy/proba_play.py`): **15 × OK, P14 „?”** (koszt ocenia człowiek — tabela niżej) w ostatnim
przebiegu o 01:02 (`wyniki/proba_play_20261117_0102.json`, `…_lista.txt`). Przebieg o 00:21 (`…_0021.json`): 14 × OK i
P08 BŁĄD (s1, w1) — błąd próby, nie gry (poprawka 3 niżej). Pierwszy przebieg o 00:18 przerwany: ekran wyboru klasy
(poprawka 2). Najważniejsze liczby: przekierowana brama miasteczka stawia na Polanie z odchyłką 0,0 st; przelot
13,6–14,1 s z rykiem, postać zakotwiczona (ruch 0,00 st), walka w czasie przelotu odrzucona przez serwer (licznik walk
0 → 0); 400 próbek pozycji potworów w 40 s — 0 poza polem przegrody; nieuprawniony za bramą cofnięty przed bramę (x
2024) z komunikatem; po wygranej wrota u zwycięzcy bez kolizji, na serwerze z kolizją; stary las działa obok (36
potworów, widoki „aktorzy”, jego mgła).

**Kamień Powrotu → nowe miasteczko (17.11.2026, 01:49).** Zmiana minimalna (D-075: miasteczko to pierwszy blok
pasa): `SerwerPasa` przy E na Kamieniu woła uchwyt `MiasteczkoBazarGra/Sygnaly/PrzeniesDoBazaru` (`{ punkt = "start" }`,
nazwy w `D.miasteczko.bazar`, `generuj_dane.py`), gdy ten kontener stoi; bez niego — stare miasteczko jak dotąd. Nasza
blokada (`za_szybko`, `przelot_trwa`) działa przed wołaniem uchwytu; odmowa uchwytu (np. `trwa`) nie przenosi nigdzie
indziej; błąd uchwytu → stare miasteczko. Haczyk testowy `przenies … "miasteczko"` dalej prowadzi do starego.
Przebudowa `zbuduj.py --skrypty` ze starym silnikiem v2 (`BC_SILNIK_KORZEN`). Lista P01–P16 po zmianie: **15 × OK,
P14 „?”** (`wyniki/proba_play_20261117_0149.json`, `…_lista.txt`): P12 — prawdziwe E przy Kamieniu → start bazaru
(990; 3; −697); reszta lasu bez zmian — walka z każdym gatunkiem (s1, m1, w1, t1) i powrót do pasa, slime wraca po
12,3 s, nieuprawniony za bramą cofnięty (x 2024) z komunikatem, po wygranej ze Strażnikiem wrota tylko u zwycięzcy,
przelot 13,4 s przy pierwszym wejściu i **bez drugiego przelotu** (P05: faza „brak”, licznik 1 → 1), stary las działa,
0 błędów w konsoli. P12 w próbie sprawdza teraz cel zależnie od tego, czy stoi `MiasteczkoBazarGra`. Bez bazaru
(uchwyt odpięty na czas próby, tylko w sesji Play) Kamień prowadzi do `LasTeleport.PunktMiasteczka` — próba
`swiat/miasteczko_bazar_gra/testy/proba_dodatkowa.py`, D04.

**Próba dodatkowa** (`testy/proba_dodatkowa.py`, `wyniki/proba_dodatkowa_20261117_0047.json`; pierwszy przebieg
`…_0035.json`):

| Co | Wynik |
|---|---|
| Brama w miasteczku, prawdziwe E (podpowiedź `LasTeleport/BramaMiejska`) | postać na Polanie Przybycia po 0,1 s, w (1114; 3,56; −700); **przelot** przy pierwszym wejściu: 13,9 s, ryk Strażnika zagrał, czarny ekran najdłużej 0,45 s, potem kamera `Custom` i W przesuwa postać o 16 st w 1 s |
| Drugie wejście bramą | bez przelotu (faza „brak” przez 6 s, licznik przelotów 1 → 1) |
| Kamień Powrotu, prawdziwe E | miasteczko (−63,6; 3,37; −771,9) — przed zmianą z 17.11.2026 01:49; teraz przy stojącym `MiasteczkoBazarGra` start bazaru (990; 3; −697) |
| Przejście przez chmury, świeży gracz | postać w lesie 0,4 s po wyborze (przez uchwyt `PrzeniesDoLasu`); chmury kończą się po 2,99 s, **przelot** przejmuje kamerę po 3,78 s, 13,9 s z rykiem, czarny ekran 0,37 s; potem `Custom` i W = 16 st |
| Drugie przejście przez chmury | bez przelotu (licznik 2 → 2), kamera `Custom` |
| Bieg piechotą Polana → brama (`Humanoid:MoveTo`, WalkSpeed 16) | **57,0 s** na 906 st (plan 57,5 s), bez zatrzymań i bez cofnięć; furtka, mostek (najwyżej y 4,5) i bród, zwężenie, próg i brama menhirów bez przeszkód. Kryształowy filar Strażnika (`LasPas/Punkty/FilarKrysztal`, 7 × 7 st) stoi na osi pasa w (1994; −700) — dróżka go obchodzi; idąc na wprost postać na nim utknęła (pierwszy bieg 73,9 s) |
| Niewidzialne ściany i ratunek | marsz w bok ze skokami w 7 miejscach (x 1110–1975): najdalej \|v\| = 36,5 st (ściany kulis na \|v\| = 38, wys. 80); w tył za Polanę najdalej x = 1096,5; za otwartą bramą w bok — stop na z = −736,5, bez spadku; spadek w pustkę (y −60) w środku pasa → ratunek na Polanę |
| Walka z każdym gatunkiem: s1 slime (poz. 1), m1 muchomornik (4), w1 wilk (6), t1 troll (9) | podpowiedź E przy potworze, prawdziwe E, kamera jedzie na arenę prototypu (`TestWalki2`), wynik, potem kamera `Custom`; postać w czasie walki stoi w pasie, więc wraca w to samo miejsce (0,0 st) |
| Odrodzenie | slime 12,4 s (plan 12), muchomornik 15,4 s (15), wilk 18,4 s (18), Strażnik 120,9 s (120); P09: slime 12,5 s. Troll (150 s) w grze niezmierzony (pokonany tylko w P08, która odrodzenia nie mierzy) |
| Strażnik: przegrana (wojownik poz. 1) | brama zamknięta; wejście za bramę → cofnięcie przed bramę |
| Strażnik: wygrana (zwiadowca poz. 10, drugie ziarno) | baner „BRAMA DO BAGNA OTWARTA!”, wrota u klienta 17/17 niewidoczne i bez kolizji (na serwerze z kolizją — P11), przejście za bramę piechotą 1,9 s bez cofnięcia; tabliczka „BAGNO — WKRÓTCE / tu zaczyna się następny biom” czytelna (`klatki/09`) |
| Mgła (P13) | waga 1 w pasie (gęstość 0,36), 0 w miasteczku; na serwerze `Atmosphere` bez zmian (0,30) |
| Przelot: płynność | 212 klatek przelotu, śr. 66,8 ms, p95 69–70 ms, najdłuższa 85–106 ms (0–1 klatka > 100 ms) przy limicie Studia 15 kl./s; widać potwory w przegrodach (`klatki/02`), ryk na końcu (`klatki/03`) |
| Konsola | bez błędów i bez ostrzeżeń `[LasPasGra]` we wszystkich przebiegach |

**Koszt** (1 gracz; zestaw na 1 gracza = 19–20 potworów, „pełny zestaw” = `TestGraczy = 20` → 45 potworów, bo Strażnik
był akurat pokonany):

| Miejsce | Klient potworów, ms na klatkę (śr. / maks.) | Brył widoków | Części u klienta | Serwer potworów, pętla ruchu ms (śr. / maks.) | Serwer pasa ms |
|---|---|---|---|---|---|
| przybycie, zestaw na 1 gracza | 0,39 / 0,91 | 230 | 18 681 | 0,12 / 0,21 | 0,03 |
| wilki, zestaw na 1 gracza | 1,42 / 3,07 (budowa widoku do 12,5 ms jednorazowo) | 3034–3578 | 21 597 | 0,14 / 0,37 | 0,03 |
| przy Strażniku, zestaw na 1 gracza (Strażnik pokonany — sam troll) | 0,25 / 0,51 | 390 | 14 793 | 0,14 / 0,24 | 0,02 |
| przybycie, pełny zestaw | 0,51 / 1,27 | 575 | 15 730 | 0,20 / 0,44 | 0,02 |
| wilki, pełny zestaw | 1,64 / 2,76 (budowa do 5,5 ms) | **3965** (budżet 4000) | 19 163 | 0,28 / 0,48 | 0,02 |
| przy Strażniku, pełny zestaw (Strażnik pokonany) | 0,25 / 0,46 | 390 | 11 413 | 0,28 / 0,52 | 0,02 |

Serwer: fizyka 60 kl./s, Heartbeat 0,02–0,16 ms. Osobny pomiar z żywym Strażnikiem
(`wyniki/proba_dodatkowa_20261117_0107.json`): przy Strażniku 2 widoki (Strażnik i troll) = **1518 brył**, klient
potworów 0,25 ms na klatkę; pełny zestaw = 46 potworów; przy wilkach w pełnym zestawie jedna klatka klienta potworów
17 ms (budowa widoków), średnio 1,66 ms.

**Poprawione po próbach w Studio** (w kodzie gry pasa nie było błędów — kontener z 00:17 jest wersją końcową):
1. **Przejście przez chmury przerywało przelot** — chmury przenosiły gracza same, a przelot ruszał 1,2 s później, w
   połowie opadania kamery chmur (dwa skrypty na kamerze, ucięty początek przelotu). Teraz `swiat/teleport_chmury`
   przenosi do lasu przez uchwyt `PrzeniesDoLasu` z `przelotPo` 2,4 s (`krainy.json`, `SerwerTeleportu`); próba chmur
   znów 6/6. Test offline 8k pilnuje, żeby przelot nie ruszył przed końcem chmur.
2. **Próby w Play nie zamykały ekranu wyboru klasy** (`src/client/ClassSelectClient` trzyma kamerę w sali klas i wyłącza
   podpowiedzi E) — pierwszy przebieg dał fałszywe błędy P04, P13. Teraz Enter jak gracz; test 8l.
3. **P08: dwie walki „nie zaczęły się”** — test przewija walkę, a serwer słusznie nie przyjmuje następnej przed upływem
   prawdziwego czasu poprzedniej (odtwarzacz: `walka_trwa_lokalnie`); potwory też odchodzą od gracza między E a
   kontrolą serwera. Teraz P08 ustawia `TestBezSesji` i ponawia E.

## Czego nie sprawdzono (także po próbach w Studio)

- **Prawdziwy telefon** ani emulator Studio: dotyk, przycisk E na ekranie, przelot i czytelność tabliczki na małym
  ekranie, koszt klienta na słabym sprzęcie (na komputerze klient potworów przy wilkach 1,4–1,6 ms na klatkę).
- **Dwóch graczy** (Test → Clients and Servers, 2): brama otwarta tylko u zwycięzcy, drugi cofany, wspólny Strażnik
  i troll. Logika tylko u jednego gracza (P10, P11) i offline.
- **Pad** i prawdziwy czas klatki (Studio pod zaciemnieniem rysuje 15 kl./s).
- **Odrodzenie trolla** po wygranej (150 s) — w grze niezmierzone; sprawdzone offline (testy 2a–2e).
- **Podpowiedzi E na zrzutach**: narzędzie zrzutu ekranu nie rysuje `BillboardGui` z `AlwaysOnTop` (sprawdzone:
  etykieta „MIASTECZKO (E)” po włączeniu `AlwaysOnTop` też znika ze zrzutu). Podpowiedzi w grze są (`PlayerGui.
  ProximityPrompts/Prompt` z `Adornee` = Kamień Powrotu, `Enabled`), a prawdziwe E działa — ale nikt ich nie widział.
- **Opublikowana gra** — pakiet działa tylko w Studio (poza Studio usuwa kontener).

## Czego nie da się sprawdzić bez Studio

Całe działanie w grze: czy przekierowana brama miasteczka i Kamień Powrotu przenoszą tam, gdzie trzeba; jak wygląda
i jak płynny jest przelot (zwłaszcza na telefonie i przy streamingu), czy Strażnik zdąży się zbudować i czy klip `ryk`
gra na widoku; czy moduł kamery Roblox po przelocie staje za plecami gracza; czy lokalne `CanCollide = false` i
`LocalTransparencyModifier` na wrotach mapy działają u klienta tak, jak zakładamy; jak czuć cofnięcie za bramę; czy
prośby o wczytanie mapy wystarczą; czytelność tabliczki i napisu bramy; mgła na oko; koszt klienta i serwera; dwóch
graczy; prawdziwy dotyk. To wszystko jest w `testy/proba_play.py` (P01–P16) albo na liście ręcznej w jego nagłówku.

## Zmiany w `swiat/las_potwory` (minimalne, zgodne wstecz)

Stary las nie ma żadnego z nowych atrybutów ani instancji, więc jego zachowanie się nie zmienia (testy przed i po: te
same wyniki).

- `zrodla/Stale.luau`: nowe stałe `GUI_BOHATERA`, `GUI_BANERA`, `PANEL_Y`, `PANEL_PREFIKS`, `SYGNAL_WYNIKU`,
  `ATRYBUT_BLOKADY` (wartości domyślne = dotychczasowe nazwy i liczby) i na końcu pliku nadpisania z atrybutów
  kontenera `Stale_<NAZWA>` (napis, liczba, wartość logiczna; lista napisów jako napis z przecinkami).
- `zrodla/SerwerPotworow.server.luau`: `biom.plyta = false` → kontrola tylko obecności mapy; `odrodzenieStale = true`
  → stały czas jak u Strażnika; gracz z atrybutem `BlokadaWalki` → odmowa `brak_postaci`; opcjonalny
  `Sygnaly/WynikWalki` → `Fire(gracz, { id, strefa, gatunek, straznik, wynik, poziom, koniec })` po przyjęciu walki.
- `zrodla/KlientPotworow.client.luau`: nazwy ScreenGui i pozycja panelu ze stałych; haczyki `"wymus", id` (widok
  budowany zawsze i przed innymi) i `"klip", id, nazwa` (jednorazowy klip, potem spoczynek).
- `testy/test_logiki.py`: lustro `Symulacja.odradzaj` zna `odrodzenieStale` (jak serwer).
- `README.md`: akapit o drugim kontenerze.

## Uchwyt dla „przejścia przez chmury” (`swiat/teleport_chmury`)

```lua
local f = workspace:WaitForChild("LasPasGra"):WaitForChild("Sygnaly"):WaitForChild("PrzeniesDoLasu")
local w = f:Invoke(gracz, { punkt = "las", przelotPo = 0 })   -- tylko po stronie serwera
-- w = { ok = true, punkt = Vector3, patrz = Vector3 }
--   | { ok = false, powod = "brak_mapy" | "brak_postaci" | "za_szybko" | "przelot_trwa" | "nieznany_punkt" | "zly_gracz" }
```

`punkt`: `"las"` (Polana Przybycia, domyślnie), `"przed_brama"`, `"za_brama"` (tylko po pokonaniu Strażnika).
`przelotPo` (0–10 s) opóźnia ewentualny pierwszy przelot, gdy wołający gra własną animację kamery (opadanie z wys. 60).
Punkt przybycia jest też w atrybutach kontenera `PunktPrzybyciaLasu` / `PatrzPrzybyciaLasu` (serwer i klient).
Przelot startuje sam przy pierwszym wejściu do prostokąta lasu — niezależnie od tego, kto przeniósł gracza.
**Od 17.11.2026 przejście przez chmury korzysta z tego uchwytu** (`swiat/teleport_chmury/krainy.json`: pierwszy punkt
przybycia lasu `uchwyt = "PrzeniesDoLasu"`, `przelot_po_s = 2.4`), żeby przelot nie ruszył w czasie opadania kamery
chmur (sprawdzone w Play: chmury do 2,99 s, przelot od 3,78 s).
Gdy przejście przez chmury przejmie bramę miasteczka, ustaw w Edit `PrzekierujBrameMiasteczka = false`.

## Haczyki testowe (Play)

- serwer: `workspace.LasPasGra.Sygnaly.SterowaniePasa:Invoke("stan" | "gracz", nazwa? | "odtworzPrzelot", nazwa? |
  "zapomnijPrzelot", nazwa? | "otworzBrame", nazwa? | "zamknijBrame", nazwa? | "przenies", nazwa?, "las" | "przed_brama" |
  "za_brama" | "miasteczko" | "koszt", zeruj? | "zgodnosc")`;
- klient: `workspace.LasPasGra.Sygnaly.SterowaniePasaKlienta:Invoke("stan")`;
- potwory pasa: te same haczyki co w starym lesie (`swiat/las_potwory/README.md`), w kontenerze `LasPasGra`.

## Znane ryzyka

- **Sprawdzone w Studio tylko z jednym graczem i na komputerze** (rozdz. „Co sprawdzone w grze”). Offline Luau
  sprawdzone statycznie, sparsowane i — dla czystej logiki — wykonane w interpreterze `tools/walka/luau_mini.py`,
  który jest plikiem innego agenta, jeszcze nie w git (gdy zniknie, testy 7a–7e i parsowanie są pomijane z uwagą).
- **Kryształowy filar Strażnika stoi na osi pasa** (mapa `swiat/las_pas`, `Punkty/FilarKrysztal` w (1994; −700),
  7 × 7 st, wys. ok. 18): dróżka go obchodzi, ale kto idzie na wprost (pad, autobieg), zatrzyma się na nim
  i może na niego wskoczyć. Wybór do decyzji 8.
- **Wilki przy pełnym zestawie: 3965 brył widoków przy budżecie 4000**, a budowa widoku wilka to jednorazowo do
  12,5 ms (krótkie zacięcie przy wejściu w Zarośla) — na telefonie może być za dużo.
- **Przelot po chmurach**: po końcu chmur ok. 0,8 s zwykłej kamery za plecami, potem 0,37 s czerni i przelot —
  cięcie, nie płynne przejście (wybór do decyzji 9).
- **Kolejna walka dopiero po prawdziwym czasie poprzedniej** (sesja serwera potworów): gdy walkę przewinąć, E przy
  następnym potworze przez kilkanaście sekund nic nie robi (odtwarzacz: `walka_trwa_lokalnie`). Dotyczy pomijania
  walk (D-078) — nie tego pakietu.
- **Narzędzie Studio `execute_luau` cofa zmianę typu kamery** zrobioną w czasie wywołania (komunikat Assistanta w
  konsoli) — próby ustawiają kamerę do zrzutów przez `task.delay`. Nie dotyczy gry.
- **Przekierowanie bramy miasteczka zmienia w trybie Play atrybuty cudzego kontenera** `LasTeleport` (`PunktLas`,
  `PatrzLas`); w Edit nic się nie zmienia, przy usunięciu kontenera wartości wracają. Ten sam cel dostaje portal przy
  starcie (`PortalStart`, też „las”). Wybór do decyzji 1.
- **Silnik walki jest właśnie zmieniany** (`src/server/Walka`, niezacommitowane zmiany innego agenta): kopia silnika
  powstaje przy budowie, a odtwarzacz prototypu sprawdza dziennik swoją kopią modułu `Dziennik` — budować pas razem
  z prototypem po tej samej wersji silnika, inaczej walki mogą być odrzucane jako zły dziennik (to samo dotyczy
  starego lasu).
- **Plan podaje kontener `Workspace/PasLas`**, a mapa i zadanie — `Workspace/LasPas`; bierzemy nazwę z mapy (bez
  znaczników: z zadania). Generator wypisuje to jako uwagę.
- **Klient: budżet 4000 brył** widoków potworów; w Leżu i na Arenie Strażnik (1128 brył rigu) + troll (390) + wilki
  (544 każdy). Na telefonie może być za dużo (stary las: 2,0 ms na klatkę w watasze na komputerze).
- **Przelot korzysta z haczyka testowego** `SterowanieKlienta` klienta potworów (`"wymus"`, `"klip"`); gdy Strażnik
  jest akurat pokonany (120 s), przelot leci bez ryku. Przed przelotem do 4 s czarnej zasłony (wczytywanie mapy).
- **Dwa panele bohatera** (stary las i pas, jeden pod drugim) i dwa banery po Strażniku („STRAŻNIK GAJU POKONANY!”
  z pakietu potworów, „BRAMA DO BAGNA OTWARTA!” z pasa) — reguła testowa T1 pakietu potworów.
- **Brama otwiera się przy przyjęciu walki**, nie po obejrzeniu (serwer zna wynik od razu; klient i tak dostaje go
  w dzienniku walki). Wybór do decyzji 2.
- **Pamięć tylko w serwerze**: restart serwera = przelot jeszcze raz i brama znów zamknięta (miejsce na zapis w
  `PamiecGracza`). Pole `zachowanie` stref (ciekawski slime, troll ryczy na gracza) — nie zrobione, jak w starym lesie.
- `zasiegGraczy` stref = pół przekątnej pola + 4 st (48 st, troll 61) zamiast r + 50 starego lasu — inaczej gracz w
  sąsiednim kojcu skracałby odrodzenie (odczytanie, opisane w generatorze).

## Wybory do decyzji

**1. Brama w miasteczku: przekierować w grze czy przebudować teleport?**
- Dziś: SerwerPasa w trybie Play podmienia cel `LasTeleport` na las-pas (gdy jest mapa); wyłącznik w atrybucie.
- Albo: zmienić `swiat/biom_las/teleport.py`, żeby czytał listę punktów przybycia.
- Albo: bramę przejmuje przejście przez chmury (`swiat/teleport_chmury`) i woła `PrzeniesDoLasu`.

**2. Kiedy otworzyć bramę po wygranej ze Strażnikiem?**
- Od razu przy przyjęciu walki (dziś; wynik i tak jest w dzienniku walki).
- Dopiero po końcu odtwarzania walki (koniec zajętości Strażnika).

**3. Dokąd cofać gracza, który przeszedł bramę bez prawa?**
- Przed bramę, twarzą do niej, z komunikatem (dziś).
- Na Polanę Przybycia (surowiej, 57 s biegu z powrotem).

**4. Ryk w przelocie, gdy Strażnik jest akurat pokonany?**
- Przelot bez ryku (dziś).
- Osobna kopia Strażnika tylko do przelotu (zawsze ryczy, więcej kodu).

**5. Panel bohatera: dwa (stary las i pas) czy jeden?**
- Dwa, jeden pod drugim (dziś, bez zmian w zachowaniu starego lasu).
- Jeden wspólny — zmiana w kliencie potworów; w grze i tak zastąpi go postać gracza.

**6. Mgła w czasie przelotu: rzadsza czy pełna?**
- Rzadsza o połowę (dziś) — widać więcej przegród.
- Pełna, jak przy chodzeniu — przelot pokazuje to, co gracz zobaczy.

**7. Zapis przelotu i bramy: kiedy przenieść z pamięci serwera?**
- Razem z zapisem postaci (profil gracza; miejsce przygotowane w `PamiecGracza`).
- Teraz osobnym DataStore (więcej pracy, ryzyko utraty zapisu bez profili).

**8. Kryształowy filar Strażnika na osi dróżki (mapa `swiat/las_pas`)**
- Zostawić — dróżka go obchodzi, filar jest punktem orientacyjnym areny (dziś).
- Przesunąć z osi o kilka studów albo dać mu kolizję tylko u podstawy (zmiana mapy, inny pakiet).

**9. Przelot po przejściu przez chmury: cięcie czy ciągłość?**
- Dziś: chmury opadają na gracza, 0,8 s zwykłej kamery, czerń 0,37 s, przelot (`przelot_po_s` 2,4 s w `krainy.json`).
- Albo: przy pierwszym wejściu chmury nie opadają na gracza, tylko z bieli od razu startuje przelot (zmiana w obu
  pakietach).
