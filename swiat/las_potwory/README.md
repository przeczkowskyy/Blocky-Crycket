# Las Potworów — potwory w ruchu w Borze Pod Ukłonem

Ten pakiet sprawia, że po 16 strefach lasu `Workspace/BiomLas` chodzą potwory. Przy jednym graczu jest ich 35, przy
ośmiu 64, a przy dwudziestu 86. Do tego w Kamiennym Kręgu stoi Strażnik Gaju, który jest celem strefy. Gracz
podchodzi do potwora i naciska E (na telefonie stuka podpowiedź). Wtedy serwer liczy walkę silnikiem v3 (od 17.11.2026; wcześniej v2), a klient
pokazuje ją w przyjętym odtwarzaczu walki z `swiat/test_walki2/`, na arenie prototypu, razem z łupem. Pokonany
potwór znika, a z domu strefy wychodzi nowy.

Całość to jeden kontener `Workspace/LasPotwory` z atrybutem `Wygenerowane = true`, bez żadnych części. Poza Studio
serwer usuwa go w całości, zanim ktokolwiek dołączy. Pakiet działa tylko na czas testów w Studio i niczego nie
zapisuje. Kontrakt, odczytania zasad, lista do sprawdzenia w Studio i wynik recenzji są w [PROJEKT.md](PROJEKT.md).

## Wymagania w miejscu

- `Workspace/BiomLas` (las z `swiat/biom_las/`, środek (0; 0; −2000), obrót 180°). Bez niego serwer nie wystawia
  potworów i mówi o tym w Output.
- `Workspace/TestWalki2` (prototyp walki v2). Daje modele potworów i odtwarzacz walki. Bez niego potwory są
  kolorowymi bryłami, a walka jest niedostępna.

## Przed budową (bez Studio)

```
python -B swiat/las_potwory/testy/test_logiki.py
python -B swiat/las_potwory/testy/test_styku.py
python -B swiat/las_potwory/zbuduj.py --sucho
```

Wszystkie trzy mają skończyć się kodem 0. `test_styku.py` czyta bieżące pliki prototypu, więc uruchom go tuż przed
budową. Gdy zmienisz któryś plik lasu, najpierw uruchom `python -B swiat/las_potwory/generuj_dane.py`.

## Budowa, wymiana skryptów, usuwanie (Studio w trybie Edit)

```
python -B swiat/las_potwory/zbuduj.py              # buduje albo odbudowuje Workspace/LasPotwory
python -B swiat/las_potwory/zbuduj.py --skrypty    # tylko skrypty i moduły do istniejącego kontenera
python -B swiat/las_potwory/zbuduj.py --usun       # usuwa Workspace/LasPotwory
```

Gdy otwartych jest kilka okien Studio, dopisz `--studio <studio_id>`. Skrypt rusza tylko kontener z atrybutem
`Wygenerowane`, robi punkty historii (Ctrl+Z cofa całość) i niczego nie publikuje.

## Test w Studio (skrót)

W trybie Play Output ma pokazać w ciągu kilku sekund:

```
[LasPotwory] gotowy: 35 potworów w 16 strefach + Strażnik Gaju; zgodność logiki 70/70
[LasPotwory] klient gotowy: tryb aktorzy, potworów w Stan: 36
```

Haczyki testowe wołasz z paska poleceń:

- w widoku serwera: `workspace.LasPotwory.Sygnaly.SterowanieSerwera:Invoke("strefy" | "potwor", id | "zabij", id | "gracze", n | "zgodnosc")`;
- w widoku klienta: `workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan" | "walcz", id | "bohater", klasa, poziom)`.

Pełna lista z poleceniami i oczekiwanymi liczbami jest w PROJEKT.md, rozdz. 9.2, a miejsce na wyniki w rozdz. 9.3.

## Drugi kontener: las-pas (16.11.2026)

Ten sam kod (Stale, Logika, SerwerPotworow, KlientPotworow) działa też w `Workspace/LasPasGra` na danych pasa —
buduje go `swiat/las_pas_gra/zbuduj.py`. Różnice ustawia tamten kontener sam: atrybuty `Stale_<NAZWA>` (osobne
szablony w ReplicatedStorage, osobne GUI, mapa `LasPas`), dane z `odrodzenieStale` (troll) i `biom.plyta = false`
(gdy mapa nie ma Płyty), opcjonalny `Sygnaly/WynikWalki` i atrybut gracza `BlokadaWalki` (przelot kamery). Klient ma
dwa nowe haczyki: `"wymus", id` i `"klip", id, nazwa`. Ten kontener (`LasPotwory`) nie ma żadnego z nich, więc działa
jak dotąd. Szczegóły: `swiat/las_pas_gra/README.md`. (Od 17.11.2026 `LasPotwory` ma też `Sygnaly/WynikWalki` — niżej.)

## Silnik walki v3 i pomijanie walk (17.11.2026, noc)

**Co zmieniono.** Walki liczy kopia silnika **v3** z `src/server/Walka` (przebudowa `zbuduj.py --skrypty`, bez
`BC_SILNIK_KORZEN`), a pokazuje odtwarzacz prototypu pod dziennik v3 (mana, statusy, blok, pasywki, wskrzeszenie).
Dwie nowe instancje w `INNE` (`zbuduj.py`) — **wybory przyjęte na noc, do zmiany** (`swiat/test_walki2/README.md`,
„Wybory do decyzji” 1 i 2):
- `Sygnaly/WynikWalki` (BindableEvent) — serwer potworów strzelał nim już wcześniej, gdy był; teraz słucha go mostek
  serwera prototypu (`SerwerWalki2`), więc **stary las też ma pomijanie walk (D-078)**: pierwsza walka z gatunkiem bez
  pomijania, przy następnych przycisk POMIŃ i spacja;
- `Sygnaly/ZwolnijPoPominieciu` (BindableFunction) i jej obsługa w `zrodla/SerwerPotworow.server.luau` (wspólna z
  lasem-pasem; tylko serwer, sprawdza, że argument to `Player`): po pominięciu przyjętym przez serwer prototypu gracz
  (`walkaDo`) i jego potwór (`zajety.koniec`) są wolni od razu — zajętość zamyka zwykła pętla ruchu (do 0,25 s;
  wygrana: potwór znika).
Testy offline: `test_styku.py` 16/16 (nowy test `test_pomijanie_walk_most_z_prototypem`: nazwy po obu stronach,
treść uchwytu), `test_logiki.py` 17/17, `sprawdz_luau.py` OK, `zbuduj.py --sucho` kod 0.

**Próba w Play** — `testy/proba_play.py` przepisana pod v3 (stara diagnoza podpowiedzi E zastąpiona listą L1–L5;
wyniki `wyniki/proba_play_20261117_0312.json`, `…_lista.txt`): **5/5 OK**.
- L1: serwer gotowy (36 potworów, zgodność logiki 70/70), `WynikWalki` i `ZwolnijPoPominieciu` są, ekran wyboru klasy
  zamknięty Enterem, kamera `Custom`.
- L2: pierwsza walka ze slime'em (Mag) z dziennika v3 — mana obu stron na paskach (44/94), bez pomijania
  (`pierwsza_walka`, bez przycisku), kontrola pasków, many i błędów = 0, po walce kamera `Custom`.
- L3: Strażnik Gaju (Zwiadowca poz. 10) — też pierwsza walka z gatunkiem, bez pomijania; zrzut
  `swiat/test_walki2/klatki/v3_las_stary_walka.jpg` (mana z kryształem gotowości, „KRYTYK!”, ranga STRAŻNIK).
- L4: druga walka ze slime'em bez `TestBezSesji`: zgoda serwera, przycisk POMIŃ, spacja → wynik, serwer „ok”, gracz
  wolny od razu (`NastepnaWalkaOd` 1,45 s przed „teraz”), potwór zwolniony, kolejna walka przyjęta od razu.
- L5: konsola bez błędów i ostrzeżeń `[LasPotwory]` / `[TestWalki2]`.
Niesprawdzone w tej próbie: przegrana i rewanż z pominięciem, dwóch graczy, telefon, koszt klienta (bez zmian w kodzie
klienta potworów).

## Jeden komplet na ekranie (17.11.2026, dzień)

Gdy w miejscu stoją oba kontenery potworów (stary las i las-pas), każdy klient potworów budował swój panel bohatera
i po Strażniku dawał baner — w lesie-pasie widać było dwa panele i dwa banery. Zmiany we wspólnym kodzie
(`zrodla/KlientPotworow.client.luau`, `zrodla/Stale.luau`):
- **panel bohatera tylko w swoim lesie**: `Stale.PANEL_TYLKO_W_LESIE = true`, prostokąt = płyta biomu z
  `DanePotworow.biom.plyta` + `PANEL_ZAPAS` 40 studów (stary las: X −740…740, Z −2740…−1260; las-pas: X 1026…2106,
  Z −828…−572). Chowany jest przycisk i okno, a `ScreenGui.Enabled` zostaje dla odtwarzacza walki (on chowa GUI na
  czas walki). Lokalny atrybut kontenera `KlientPanelWidoczny` (do prób). Poza lasami panelu nie ma;
- **jeden baner po Strażniku**: podpis banera „STRAŻNIK GAJU POKONANY!” może podmienić inny skrypt kontenera lokalnym
  atrybutem `PodpisBaneraStraznika` (las-pas: „Brama do Bagna otwarta — idź za arenę”); klient potworów go zużywa
  (`BanerStraznikaZPodpisem`). Domyślny podpis: `Stale.PODPIS_STRAZNIKA` („Wróci za 2 min”, jak dotąd).
Test offline `test_styku.py` 16/16 (podpis z lasu-pasa dopisany do atrybutów, które klient może czytać). Próba starego
lasu w Play (`testy/proba_play.py`, okno Studio na wierzchu, kod końcowy; `wyniki/proba_play_20261117_0944.json`,
`…_lista.txt`): **5/5 OK** (L1–L5 jak w nocy). Panel w Borze sprawdza próba lasu-pasa (P15: widoczny tylko panel
starego lasu), w pasie — P08j. W lesie-pasie: `swiat/las_pas_gra/README.md` (P08j, P11j, P15).

## Pliki

| Plik | Co to jest |
|---|---|
| `zrodla/SerwerPotworow.server.luau` | serwer: ruch 4 Hz, odradzanie, kontrola prośby o walkę, silnik v3, zwolnienie po pominięciu |
| `zrodla/KlientPotworow.client.luau` | klient: modele najbliższych potworów, tabliczki, podpowiedź E, panel bohatera |
| `zrodla/Stale.luau`, `zrodla/Logika.luau` | wspólne stałe; czysta matematyka ruchu (tylko serwer) |
| `zrodla/DanePotworow.luau` | dane stref w układzie świata, wygenerowane przez `generuj_dane.py` |
| `logika.py`, `generuj_dane.py` | lustro `Logika` w Pythonie; generator danych |
| `testy/test_logiki.py`, `testy/test_styku.py` | testy offline: logika, symulacja serwera, brzegi; punkty styku |
| `testy/proba_play.py`, `wyniki/` | próba w Play pod v3 i pomijanie (L1–L5); wyniki prób bez nazw kont |
| `sprawdz_luau.py`, `zbuduj.py` | tania kontrola statyczna Luau; budowa w Studio |
| `UWAGI_S.md`, `UWAGI_K.md` | odczytania kontraktu programistów serwera i klienta |

## Stan w Studio (15.11.2026)

Pakiet działa w Roblox Studio w kontenerze `Workspace/LasPotwory` (zbudowany z tych źródeł, skrót danych `3f657732d08e`).
Pierwsze uruchomienie i poprawki błędów zrobił agent wdrożeniowy; jego praca urwała się na pomiarach kosztu (limit
użycia), więc lista kontrolna z `PROJEKT.md` rozdz. 9.2 nie była wtedy przejdzona w całości. Krótką próbę końcową zrobiono
skryptem `testy/proba_play.py` (Play, zrzuty w `klatki/`):

- serwer: „gotowy: 35 potworów w 16 strefach + Strażnik Gaju”, zgodność logiki 70/70, 36 wpisów w `Stan`;
- klient: tryb „aktorzy”, po 14 s przy bramie lasu 4 widoki slime'ów (460 części), wszystkie animowane, 0 błędów;
  przy Strażniku 3 widoki (2216 części);
- tabliczki poziomu nad potworami („POZ. 1”, „POZ. 10”), plakietka wybranego bohatera u góry ekranu;
- podpowiedź przy Strażniku Gaju: włączona, gdy postać stoi obok;
- walka zaczęta z lasu: serwer przyjął prośbę, policzył walkę (Zwiadowca poz. 10 kontra Strażnik Gaju poz. 10, przegrana
  w 18 turach, 30,6 s), odtwarzacz pokazał ją na arenie prototypu z podestem (łata P1) i oknem wyniku bez przycisku
  „jeszcze raz” (łata P2);
- prośba o walkę z potworem, który odszedł dalej niż 8 studów: serwer odmawia (potwór zostaje wolny) — zgodnie z D-016.

**Kontrola tego samego dnia wieczorem (19:32–19:46)** przeszła resztę listy skryptem `testy/kontrola_play.py`; pełne
liczby są w `PROJEKT.md` rozdz. 9.3, a film w `klatki/film_las_potwory.mp4` (35 s). W skrócie:

- po wygranej i kliknięciu ZAMKNIJ kamera i sterowanie wracają, postać stoi w lesie, pokonany potwór znika od razu;
- nowy slime pojawia się 15,5 s po zniknięciu pokonanego (wilk po 25,7 s), wychodzi z domu i wchodzi na pętlę;
- Strażnik Gaju wraca po 121,8 s, także gdy gracz stoi obok;
- liczba potworów rośnie z liczbą graczy: 36 przy 1 graczu, 65 przy 8, 87 przy 20 (z Strażnikiem); gdy graczy ubywa,
  nikt nie znika sam;
- wilki i Muchomorniki stoją na ziemi, ruszają się, walka z nimi rusza; E naprawdę zaczyna walkę;
- panel bohatera mieści się na ekranie telefonu, najmniejszy napis 16 punktów (poprawiony kolor nagłówków);
- **słabe miejsce:** koszt klienta w środku watahy wilków to 2,0 ms na klatkę przy celu 1 ms (komputer; telefon gorzej).

Nadal niesprawdzone: przegrana i rewanż, czerwone tabliczki przy niskim poziomie bohatera, dwóch graczy naraz,
prawdziwy dotyk na telefonie, wygląd dymka podpowiedzi okiem (zrzut ekranu MCP go nie pokazuje).

Uwagi z próby:
- Slime idzie 6 studów na sekundę, więc trzeba do niego podbiec; podpowiedź gaśnie, gdy odejdzie dalej niż 8 studów.
- Okno wyniku trzyma walkę otwartą, dopóki gracz nie kliknie ZAMKNIJ; po dłuższej chwili tło areny znika zza okna
  (arena leży ponad 2000 studów od lasu i wypada ze streamingu).
- Zrzuty i filmy wymagają włączonego ekranu: przy wygaszonym monitorze Studio nie rysuje obrazu i `screen_capture`
  wisi. `testy/proba_play.py` budzi ekran przed każdym zrzutem (`swiat/test_walki2/testy/czuwanie.py`).

## D-107 — walka bez przestojów (19.11.2026; część A: bez Studio)

*Status: decyzja D-107 ma podpis Karola i czeka na potwierdzenie Pawła. Sprawdzone tylko testami bez Studio — w grze
jeszcze nie wdrożone (część B).*

Zmiana we wspólnym kodzie (działa w każdym kontenerze potworów: `LasPasGra`, `BagnoPasGra`, `DzunglaPasGra` i stary
`LasPotwory`):

| | Było | Jest |
|---|---|---|
| Blokada sesji gracza po przyjęciu walki (`walkaDo`) | `walka.czas − ZAPAS_SESJI` (pełny czas ×1) | `walka.czas / TEMPO_POKAZU_MAKS − ZAPAS_SESJI` (najkrótszy pokaz, ÷ 4) |
| Zajętość potwora | `walka.czas + ZAPAS_ZAJETOSCI` | `walka.czas / TEMPO_POKAZU_MAKS + ZAPAS_ZAJETOSCI` |
| `koniec` w sygnale `WynikWalki` (pamięć pomijania prototypu) | koniec zajętości | bez zmian w wartości: koniec pokazu ×1 |
| Komunikaty `walka_trwa`, `odpoczynek` | „Odpoczywasz po walce…” | „Poprzednia walka jeszcze trwa…” (widać tylko po przerwanym pokazie) |
| Podpis banera po Strażniku | „Wróci za 2 min” | „Wróci za chwilę” |

- `Stale.TEMPO_POKAZU_MAKS = 4` — najszybsze tempo odtwarzacza. `1` (także atrybutem kontenera
  `Stale_TEMPO_POKAZU_MAKS`) przywraca dawne zachowanie. Stałą czyta też symulacja `swiat/przejscie_gry`.
- Zostaje ochrona przed podwójnym startem: `ODSTEP_PROSB` 1 s, blokada na czas najkrótszego pokazu, zajętość potwora
  dla innych graczy. Pominięcie (`ZwolnijPoPominieciu`) zwalnia od razu, jak dotąd. Silnik walki i łup bez zmian.
- Dane starego lasu (`zrodla/DanePotworow.luau`) bez zmian: liczby potworów i odradzanie jak dotąd — D-107 mówi o
  pasach. Liczby pasów, rachunek i wybory do oceny: `swiat/las_pas_gra/README.md`, rozdz. „D-107”.
- Nowe pole danych pasów `rzadki` (rzadki potwór przegrody); `odrodzenieStale` mają teraz wszystkie strefy pasów
  (stały czas, bez dolnej granicy 10 s z `Logika.czasOdrodzenia`). `Logika` i jej 70 przypadków bez zmian.

### D-107, część B (19.11.2026): najbliższy potwór ma pierwszeństwo w budżecie brył

Próba w Play 19.11 przy pełnym zestawie lasu-pasa: 8 wilków w strefie, a widoki miało 6 — budżet 4000 brył
(`Stale.BUDZET_CZESCI`) zajmowały widoki muchomorników zbudowane wcześniej (dalsze, ale wciąż w promieniu 135 st),
więc dwa wilki tuż przy graczu były niewidoczne (z podpowiedzią E w pustym miejscu). Zmiana w
`zrodla/KlientPotworow.client.luau` (`zbudujKolejny`): gdy potwór z kolejki budowy nie mieści się w budżecie, klient
zwalnia najdalsze widoki — tylko dalsze od niego — i buduje bliższego. Budżet (koszt klienta) zostaje ten sam, nic nie
miga (zwolniony widok nie wyprze potem bliższego). Wynik w próbie: 7 wilków = 7 widoków wilków (3965 brył z jednym
muchomornikiem). Liczbę wilków w lesie zmniejszono do 3 / 6 / 7 (8 wilków to 4352 bryły — ponad budżet).
