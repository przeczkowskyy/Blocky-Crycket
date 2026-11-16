# Las-pas w grze — potwory w przegrodach, brama, teleport, mgła, przelot kamery

*Status: **propozycja** (16–17.11.2026), kod przygotowany i sprawdzony bez Studio, **w Studio jeszcze nie
uruchomiony**. Źródło wymagań: plan `swiat/biom_las/pas/PLAN_PASA.md` (zaakceptowany plan lasu) i decyzje D-075,
D-076, D-077 (przelot przy pierwszym wejściu, bez pomijania). D-078 (pomijanie walk) nie należy do tego pakietu.
Ustawienia przyjęte przez właściciela: Strażnik i Troll wspólni dla serwera, walka na arenie prototypu, teleport do
wejścia biomu, przelotu nie da się pominąć, stary las zostaje nietknięty i działa dalej.*

> **W skrócie.** Jeden kontener `Workspace/LasPasGra` (atrybut `Wygenerowane = true`, osobny od
> `Workspace/LasPotwory`) obok mapy z klocków `Workspace/LasPas` (robi ją inny agent w `swiat/las_pas/`). W nim:
> **ten sam kod potworów** co w starym lesie (`swiat/las_potwory`), uruchomiony na nowych danych — 10 stref w
> przegrodach pasa i Strażnik (20 / 36 / 46 potworów przy 1 / 8 / 20 graczach); **brama do Bagna** zamknięta, dopóki
> gracz nie pokona Strażnika (otwiera się tylko u niego, serwer cofa nieuprawnionych); **teleport** — dzisiejsza brama
> w miasteczku prowadzi na Polanę Przybycia pasa, gdy jest mapa, a Kamień Powrotu wraca do miasteczka; **mgła** tylko
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
| `testy/test_pasa.py` | 43 testy offline (opis w nagłówku pliku) |
| `testy/proba_play.py` | gotowa próba w Studio (Play) z listą kontrolną P01–P16 i listą zrzutów — **dla następnego etapu, nieuruchomiona** |

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
| `Punkty/KamienPowrotu` | część + ProximityPrompt | punkt E przy Kamieniu Powrotu z mapy → miasteczko |

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
python -B swiat/las_pas_gra/testy/test_pasa.py       # 43 testy, ok. 3 s
python -B swiat/las_pas_gra/zbuduj.py --sucho        # bez Studio: dane, Luau, strażniki, plan budowy
python -B swiat/las_pas_gra/zbuduj.py                # Studio w trybie Edit: buduje / odbudowuje Workspace/LasPasGra
python -B swiat/las_pas_gra/zbuduj.py --skrypty      # tylko kod, zdalne i Stale_* (bez części)
python -B swiat/las_pas_gra/zbuduj.py --usun         # usuwa Workspace/LasPasGra (stary las zostaje)
```

Przy kilku oknach Studio dopisz `--studio <studio_id>`. Budowa sprawdza `game.PlaceId` gry w każdym wysyłanym kodzie,
działa tylko w trybie Edit, rusza tylko kontener z `Wygenerowane`, robi punkty historii (Ctrl+Z cofa całość) i niczego
nie publikuje ani nie zapisuje.

## Kolejność wdrożenia w Studio (następny etap)

1. `git pull`, potem offline: `python -B swiat/las_potwory/testy/test_logiki.py`, `python -B swiat/las_potwory/testy/test_styku.py`,
   `python -B swiat/las_potwory/sprawdz_luau.py`, `python -B swiat/las_pas_gra/testy/test_pasa.py`,
   `python -B swiat/las_pas_gra/zbuduj.py --sucho` — wszystko kod 0. Zgłoś pracę: `python panel/narzedzia/praca.py start
   --id las-pas-gra --tytul "Las-pas: potwory, brama, przelot" --koniec +60m --obszar studio:LasPasGra --obszar swiat/las_pas_gra --stop-przy-kolizji`.
2. Mapa: `Workspace/LasPas` musi stać w Studio (buduje ją pakiet `swiat/las_pas/` — jego README). Bez niej potwory i
   brama nie startują (`StanBiomu`/`StanMapy`), a brama miasteczka prowadzi dalej do starego lasu.
3. Prototyp walki: `Workspace/TestWalki2` z `Aktorzy/lesny_troll` (nowy gatunek w pasie). Brak jednego szablonu = cały
   klient potworów pasa w trybie brył zastępczych (zachowanie pakietu potworów) — `zbuduj.py` ostrzega.
4. `python -B swiat/las_pas_gra/zbuduj.py` (tryb Edit). Ma wypisać „w miejscu (tylko odczyt): …” z Płytą
   (1566, −1, −700), 1000 × 2 × 176, obrót 0, a na końcu „części: 7” (zapora, napis, podłoga, ściana, słupek, deska,
   punkt E) i `Skrot` równy temu z `--sucho`.
5. Próba w Play: `python -B swiat/las_pas_gra/testy/proba_play.py <folder poza repo>` — lista P01–P16 z wynikami w
   `<folder>/lista.txt` i `wyniki.json`, zrzuty 01–20 w tym samym folderze. Ręcznie: telefon (emulator Studio) i dwóch
   graczy (Test → Clients and Servers, 2): brama otwarta tylko u zwycięzcy, drugi cofany.
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
Gdy przejście przez chmury przejmie bramę miasteczka, ustaw w Edit `PrzekierujBrameMiasteczka = false`.

## Haczyki testowe (Play)

- serwer: `workspace.LasPasGra.Sygnaly.SterowaniePasa:Invoke("stan" | "gracz", nazwa? | "odtworzPrzelot", nazwa? |
  "zapomnijPrzelot", nazwa? | "otworzBrame", nazwa? | "zamknijBrame", nazwa? | "przenies", nazwa?, "las" | "przed_brama" |
  "za_brama" | "miasteczko" | "koszt", zeruj? | "zgodnosc")`;
- klient: `workspace.LasPasGra.Sygnaly.SterowaniePasaKlienta:Invoke("stan")`;
- potwory pasa: te same haczyki co w starym lesie (`swiat/las_potwory/README.md`), w kontenerze `LasPasGra`.

## Znane ryzyka

- **Nic nie było uruchomione w Studio.** Luau sprawdzone statycznie, sparsowane i — dla czystej logiki — wykonane
  w interpreterze `tools/walka/luau_mini.py`, który jest plikiem innego agenta, jeszcze nie w git (gdy zniknie,
  testy 7a–7e i parsowanie są pomijane z uwagą, reszta działa).
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
