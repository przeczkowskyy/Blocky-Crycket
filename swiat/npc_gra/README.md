# Postacie niezależne w grze (D-109) — `swiat/npc_gra`

> **Status: propozycja.** Decyzja D-109 (Karol, 19.11.2026; czeka na potwierdzenie Pawła) mówi, że karczmarz, sprzedawcy,
> mistrz gier i postacie przy mini-grach mają być NPC ze szkieletem i animacją, a nie figurami z klocków. Wygląd,
> imiona i gesty poszczególnych postaci to propozycje do oceny (lista na końcu).
> **Stan 19.11.2026: kontener `Workspace/NpcGra` stoi w Studio** (17 źródeł, zero części; miejsce nie było zapisywane
> ani publikowane), próba w grze **15 × OK**. Trenerzy mini-gier są przygotowani, ale nie stoją — czekają na wdrożenie
> nowej areny pakietu treningu (rozdział „Jak postawić trenera mini-gry”). Przed publikacją miejsca:
> `python -B swiat/npc_gra/zbuduj.py --usun`.
> **Uwaga:** po próbie doszły zmiany bez Studio (Pancerz bez trenera-NPC, klip „akcja” — skrót danych d66df4377d67),
> a w Studio stoi kontener sprzed nich (skrót 8bb3a982837a). Przed `--trenerzy` trzeba go odświeżyć:
> `python -B swiat/npc_gra/zbuduj.py` (kotwice zostają).

## Co to jest

NPC to model postaci z pakietu postaci (`swiat/postacie`: kości R15, stawy, klipy), złożony w grze ze zwykłych części
Roblox — bez wgrywania czegokolwiek. Każdy klient składa NPC u siebie i sam je animuje:

- **spoczynek** w pętli (oddech), co 9–18 s **gest roli**, **powitanie** (machanie i krótki tekst), gdy gracz podejdzie
  na 14 studów, **głowa i tułów obracają się ku graczowi** (głowa do 62°, tułów do 22°), nad głową **tabliczka**
  z imieniem i rolą (ustępuje dymkowi bazaru po E);
- **tanio:** rig powstaje dopiero ≤ 150 studów od gracza, rusza się tylko ≤ 55 studów (dalej stoi w pierwszej klatce
  spoczynku), bliżej niż 25 studów liczony co klatkę, dalej co drugą;
- **nie przeszkadza:** żadna część NPC nie ma kolizji, dotyku ani promieni; podpowiedzi E zostają na częściach
  swoich pakietów (bazar: `_Interakcja`), więc działają w tym samym miejscu.

## Obsada (propozycja)

| NPC (id) | Imię · rola | Gdzie | Klipy: spoczynek / powitanie / gest | Bryły | Skala |
|---|---|---|---|---|---|
| `karczmarz` | Bolko · Karczmarz | bazar, karczma (za ladą) | idle / zaproszenie / śmiech ×2 | 98 | 1,15 |
| `mistrz_gier` | Pionek · Mistrz gier | bazar, karczma (na stołku przy planszy) | siedzi i macha nogami / machanie / rzut kostką | 75 | 1,10 |
| `mag` | Zefir · Mag | bazar, sklep magiczny | oddech / machanie / unosi kostur, dłoń krąży nad kryształem | 78 | 1,15 |
| `zbrojmistrz` | Radomir · Zbrojmistrz | bazar, zbrojownia | oddech / machanie / ogląda klingę i salutuje mieczem | 72 | 1,15 |
| `trener` | Tymon · Trener | bazar, Training Center (wejście na mini-gry) | oddech / machanie / napina bicepsy | 62 | 1,15 |
| `opiekunka` | Jagoda · Opiekunka | bazar, zagroda petów | oddech / machanie / potrząsa wiadrem z kością | 80 | 1,10 |
| `kowal` | Krzesimir · Kowal | bazar, kuźnia — **stoi już jako rig z klipami** w `Workspace/KowalProba` (18.11) | spoczynek / kucie / radość (jego pakiet) | 90 | 1,00 |
| `trener_sila` | Borys · Trener Siły | arena, mini-gra Siły | oddech / machanie / wyciska hantlę ×2; **akcja:** jeden rzut (0,6 s) | 61 | 1,10 |
| `golem` | Głaz · Kamienny golem | **zapas — nie stoi w grze**: w mini-grze Pancerza golem gry jest przeciwnikiem i trenerem naraz | ciężki oddech / unosi pięść / zamach i cios pięścią | 52 | 1,50 |
| `trener_kondycja` | Iskra · Trenerka Kondycji | arena, mini-gra Kondycji | oddech / machanie / trzy uderzenia pałką i krok w miejscu; **akcja:** jedno uderzenie (0,6 s) | 58 | 1,10 |
| `trener_zrecznosc` | Wiór · Trener Zręczności | arena, mini-gra Zręczności | oddech / machanie / zamach siekierą i cięcie | 66 | 1,10 |
| `trener_inteligencja` | Runa · Trenerka Inteligencji | arena, mini-gra Inteligencji | oddech / machanie / kreśli znak nad księgą | 85 | 1,10 |
| `trener_szczescie` | Fart · Trener Szczęścia | arena, mini-gra Szczęścia | oddech / machanie / podlewa konewką | 79 | 1,10 |

Postacie: `swiat/postacie/karczmarz.py`, `kowal.py` (były) i jedenaście nowych modułów `swiat/postacie/npc_<id>.py`
na wspólnym ciele człowieka (`npc_wspolne.py`: klocki ciała „czlowiek” — te same co goły Rycerz — twarz, fryzury,
zarost, stroje, wspólny zestaw klipów `spoczynek`, `powitanie`, `gest`); golem ma własne klocki. Rekwizyt jest
bryłami na kości dłoni. Kowalowi ten pakiet dokłada tylko tabliczkę — jego rig i klipy zostają w `swiat/kowal_proba`.

**Plansza zbiorcza** (wszyscy w skali gry obok człowieka gracza): `podglady/npc_razem.jpg`. Pojedyncze postacie
z czterech stron: `swiat/postacie/wynik/npc_<id>/npc_<id>_plansza.jpg`.

## Jak działa animacja w grze i ile kosztuje

- Kontener `Workspace/NpcGra` (atrybut `Wygenerowane`): `Moduly/DaneNpc`, `Moduly/LogikaNpc`, `Moduly/RigNpc`,
  `Moduly/Rigi/Rig_<id>` (12 modułów), `Sygnaly/Polecenie`, `Sygnaly/SterowanieKlienta`, `Sygnaly/SterowanieSerwera`,
  skrypty `SerwerNpc` i `KlientNpc`, folder `Kotwice`. **Zero części** — rigi składa klient w grze, lokalnie,
  w folderze `Workspace/NpcLokalni`.
- `KlientNpc` buduje rig z danych (`RigNpc.zbuduj`: zakotwiczony korzeń, 15 niewidzialnych części kości na `Motor6D`,
  bryły na `Weld`) i co klatkę wpisuje pozę w `Motor6D.Transform`: klatki klipu co 1/15 s, liniowo między nimi,
  płynne przejście 0,25 s przy zmianie klipu, do tego obrót głowy i tułowia ku graczowi dołożony do pozy z klipu.
- O tym, co NPC robi, decyduje czysta logika `LogikaNpc` (lustro w Pythonie: `logika_npc.py`).
- Klipy pochodzą z modułów postaci, próbkowane bez Blendera (`roblox_klocki.probki_liniowe`), co drugą klatkę.

Rachunek (z `python -B swiat/npc_gra/dane.py --tabela`):

| Co | Ile |
|---|---|
| Bazar: 6 NPC | 465 brył, **567 części u klienta** (bryły + 15 kości + korzeń + tabliczka na postać); bez cieni |
| Figury z klocków, które zastępują | 250 części (zostają w mapie, u gracza niewidoczne) |
| Wszystkie 12 rigów (z trenerami) | 866 brył |
| Dane | `DaneNpc` 8 kB + 12 rigów po 21–33 kB = **306 kB** źródeł modułów (pobierane raz; rig wczytuje się dopiero przy pierwszej budowie postaci) |
| Serwer | nic nie buduje i nic nie wysyła: jeden skrypt z wyłącznikiem |
| Praca co klatkę | tylko NPC ≤ 55 studów: na postać 15 interpolacji pozy i 15 wpisów stawów (≤ 25 studów co klatkę, dalej co drugą); przegląd odległości co 0,25 s |
| Zmierzony czas pętli klienta | **0,035–0,039 ms średnio w siedmiu przebiegach (najdłuższa klatka pętli 0,06–0,24 ms)** przy czterech NPC w ruchu, na komputerze autora przy 60 kl./s (próg próby 1,5 ms); czas klatki 16,7 ms |

## Podmiana w bazarze

Kto stoi w którym miejscu, mówi **pakiet bazaru**: w `swiat/miasteczko_bazar_gra/miejsca.json` sześć miejsc dostało
pole `"npc"` (karczma → `karczmarz`, mistrz_gier → `mistrz_gier`, sklep_magiczny → `mag`, zbrojownia →
`zbrojmistrz`, training_center → `trener`, zagroda_petow → `opiekunka`). To jedyna zmiana w bazarze: pola nie czyta
generator danych bazaru, więc `DaneBazaru.luau`, jego skrót i skrypty bazaru są bez zmian (testy bazaru zielone,
bazaru nie trzeba wdrażać od nowa).

`dane.py` tego pakietu bierze z bazaru resztę: Model figury ze znaczników (`znaczniki.json` → `model`), a z mapy
(`czesci.json`) część „Korzeń” figury — **NPC staje stopami dokładnie tam, gdzie stała figura, twarzą w tę samą
stronę**; rola na tabliczce to `obiekt · akcja_tekst` miejsca (np. „Karczmarz · Zadania”).

Figur z klocków nikt nie usuwa z mapy. Klient chowa figurę u gracza (`LocalTransparencyModifier`), gdy na jej miejscu
stoi NPC; kolizje figury zostają (gracz nie wchodzi w sprzedawcę, kamera nie wchodzi mu w głowę — poprawka bazaru
z 17.11), dymek bazaru dalej liczy wysokość z Modelu figury, podpowiedzi E są nietknięte. Bez kontenera `NpcGra` albo
przy wyłączniku `NpcWGrze = false` figury są widoczne jak dawniej — można porównać stare z nowym jednym atrybutem:

```lua
workspace.NpcGra:SetAttribute("NpcWGrze", false)   -- w Edit albo na serwerze w grze
```

Mistrz gier siedzi na stołku karczmy (stanowisko ma przesunięcie: 0,06 st w dół, 0,3 st w tył). Skale i przesunięcia
stanowisk: `ustawienia.json` → `stanowiska_bazaru`.

## Jak postawić trenera mini-gry

**Po wdrożeniu nowej areny pakietu treningu w Studio — jedno polecenie:**

```
python -B swiat/npc_gra/zbuduj.py --trenerzy          # pięć kotwic w Workspace/NpcGra/Kotwice
python -B swiat/npc_gra/zbuduj.py --trenerzy --stan   # samo porównanie areny w Studio z danymi (nic nie zmienia)
python -B swiat/npc_gra/zbuduj.py --bez-trenerow      # cofnięcie
```

Punkty bierze z danych pakietu treningu (`swiat.<gra>.trener_npc`: miejsce, `patrz`, `figura` — czytane generatorem
tamtego pakietu, bez kopiowania liczb). Najpierw sprawdza w Studio, czy figura każdej gry stoi przy swoim punkcie
(do 3 st); gdy nie — „STOP: arena w Studio nie zgadza się z danymi” i nic nie powstaje (19.11.2026 tak właśnie
odpowiada, bo w Studio stoi jeszcze stara arena). Wysokość stóp mierzy promieniem w dół.

| Gra | NPC | Skala | Figura do schowania | Zostaje widoczne |
|---|---|---|---|---|
| Siła | Borys (`trener_sila`) | 1,10 | `Arena/Sila/Miotacz` | — |
| Pancerz | — bez NPC: golem gry jest przeciwnikiem i trenerem naraz | — | — | — |
| Kondycja | Iskra (`trener_kondycja`) | 1,10 | `Arena/Kondycja/Trener` | `Beben*`, `NogaBebna*` (bęben) |
| Zręczność | Wiór (`trener_zrecznosc`) | 1,10 | `Arena/Zrecznosc/Trener` | — |
| Inteligencja | Runa (`trener_inteligencja`) | 1,10 | `Arena/Inteligencja/Mag` | `Kula` |
| Szczęście | Fart (`trener_szczescie`) | 1,10 | `Arena/Szczescie/Ogrodnik` | — |

**Ruchy, które animuje klient mini-gier** (do uzgodnienia z pakietem treningu):

- `RamieP` miotacza Siły i trenera Bieżni to części figury — po schowaniu figury ruszają się dalej, ale niewidocznie
  (klient treningu niczego nie zauważy, błędów nie będzie). Skrzynka miotacza wyleci więc „z ręki” NPC, który w tej
  chwili nie robi zamachu. Żeby NPC ruszał się z grą, klient treningu woła
  `workspace.NpcGra.Sygnaly.Polecenie:Invoke("graj", "trening_sila", "gest")` (to samo dla `trening_kondycja`).
  Gesty roli są dłuższe niż jeden rzut albo jedno uderzenie (2,0 s i 1,8 s), więc obie postacie mają osobny krótki
  klip **„akcja”** (jeden rzut prawą ręką; jedno uderzenie pałką): `Invoke("graj", "trening_sila", "akcja")` →
  czas klipu. Trwa `trenerzy.akcja_s` = **0,6 s — wartość przyjęta**, do podmiany na czas ruchu `RamieP` z pakietu
  treningu (zmiana ustawienia i `dane.py`, bez Blendera). W grze klip „akcja” nie był jeszcze oglądany.
- `Kula` maga i bęben Bieżni to elementy gry, więc zostają widoczne (`trenerzy.zostaw` w `ustawienia.json` → atrybut
  kotwicy `NpcZostaw`). Kula została przy dawnym miejscu dłoni figury — czy pasuje do Runy z księgą, pokaże zrzut.
- **Pancerz nie ma trenera-NPC** (ustalenie z 19.11.2026): golem gry jest tam przeciwnikiem i trenerem naraz,
  a pakiet treningu nie daje dla niego punktu. Gra, dla której pakiet treningu nie ma punktu trenera, jest przez
  `--trenerzy` pomijana (jeden wiersz informacji), pozostali trenerzy stają. Postać golema (`npc_golem`) zostaje
  w pakiecie jako zapas.

Pojedynczego trenera można postawić też ręcznie — NPC pojawia się u gracza, gdy ten jest bliżej niż 150 studów:

1. **Kotwica w kodzie budowniczego** (zalecane): niewidzialna część z tagiem `NpcGraKotwica` i atrybutem `Npc`.
   Stopy NPC stają w środku części, przodem tam, gdzie przód części.
   ```python
   import zbuduj as NPC                      # swiat/npc_gra/zbuduj.py (wczytany po ścieżce)
   kod += NPC.kotwica_luau(NPC.DN.ustawienia(), "trener_sila", "trening_sila",
                           poz=(x, y_podlogi, z), patrz=(x_gracza, z_gracza), rodzic="arena")   # rodzic = wyrażenie Luau
   ```
   Atrybuty kotwicy: `Npc` (id z tabeli), `NpcKlucz` (nazwa stanowiska do poleceń), opcjonalnie `NpcSkala` (domyślnie
   1,1; golem 1,5), `NpcImie`, `NpcRola`, `NpcZastepuje` (ścieżka Modelu figury do schowania, np.
   `Workspace/TreningProba/Arena/Sila/Miotacz`). Która postać do której gry: `DaneNpc.trenerzy.gry`
   (sila → `trener_sila`, kondycja → `trener_kondycja`, zrecznosc → `trener_zrecznosc`,
   inteligencja → `trener_inteligencja`, szczescie → `trener_szczescie`).
2. **Polecenie budowniczego** (kotwica w `Workspace/NpcGra/Kotwice`):
   `python -B swiat/npc_gra/zbuduj.py --kotwica trener_sila --klucz trening_sila --poz 10,0.5,20 --patrz 10,30`
   (usunięcie: `--bez-kotwicy trening_sila`).
3. **W grze, u klienta:** `workspace.NpcGra.Sygnaly.Polecenie:Invoke("postaw", "trening_sila", "trener_sila", CFrame, skala?)`
   i `Invoke("usun", "trening_sila")`.

Ruch na życzenie mini-gry (u klienta): `Polecenie:Invoke("graj", "trening_sila", "gest")` → czas klipu w sekundach
(albo `false`, gdy NPC nie stoi albo jest za daleko); `"powitanie"`, `"spoczynek"` i — u trenera Siły i trenerki
Kondycji — `"akcja"` tak samo. Części gry (pięść golema, ramię miotacza) zostają częściami `trening_proba`; NPC ich
nie zastępuje, dopóki tamten pakiet tak nie postanowi.

## Pliki

| Plik | Co to |
|---|---|
| `ustawienia.json` | obsada (imiona, role, teksty powitań, klipy), skale, zasięgi, czasy, wzrok, tabliczka — jedyne miejsce do strojenia |
| `dane.py` | generator `zrodla/DaneNpc.luau` i `zrodla/rigi/Rig_<id>.luau`; tabela obsady i rachunek (`--tabela`) |
| `logika_npc.py` | lustro `LogikaNpc.luau` |
| `zbuduj.py` | budowa kontenera w Studio (`--sucho`, `--stan`, `--usun`, `--kotwica`, `--trenerzy`), `kotwica_luau()` dla innych pakietów |
| `plansza.py` | plansza zbiorcza `podglady/npc_razem.jpg` (Blender) |
| `sprawdz_luau_npc.py` | kontrola statyczna źródeł Luau i kodu budowniczego |
| `zrodla/LogikaNpc.luau` | czysta logika: stopień szczegółów, powitanie, gesty, wzrok, numer klatki |
| `zrodla/RigNpc.luau` | budowa rigu z danych, klipy, przejścia, wzrok |
| `zrodla/KlientNpc.client.luau` | stanowiska (dane, kotwice, polecenia), chowanie figur, tabliczki, pętla |
| `zrodla/SerwerNpc.server.luau` | wyłącznik i haczyk prób; poza Studio usuwa kontener |
| `testy/test_npc.py` | testy bez Studio (29) |
| `testy/proba_play.py` | próba w grze N00–N14 (`--sprawdz` działa bez Studio) |
| `klatki/` | zrzuty z gry |
| `swiat/postacie/npc_wspolne.py`, `npc_<id>.py` | wspólne ciało i jedenaście nowych postaci |

## Polecenia

```
python -B swiat/postacie/przebuduj.py npc_mag --bez-filmow      # po zmianie postaci: wynik/npc_mag/ (Blender)
python -B swiat/npc_gra/dane.py                                 # po zmianie postaci albo ustawień: nowe dane gry
python -B swiat/npc_gra/dane.py --sprawdz
python -B swiat/npc_gra/plansza.py                              # plansza zbiorcza (Blender, ok. 1 min)
python -B swiat/npc_gra/testy/test_npc.py
python -B swiat/npc_gra/sprawdz_luau_npc.py
python -B swiat/npc_gra/zbuduj.py --sucho
python -B swiat/npc_gra/testy/proba_play.py --sprawdz
# Studio w trybie Edit:
python -B swiat/npc_gra/zbuduj.py [--studio <id>]
python -B swiat/npc_gra/testy/proba_play.py <folder wyników POZA repo> [--bez-zrzutow]
python -B swiat/npc_gra/zbuduj.py --usun                        # przed publikacją miejsca
```

## Próba w grze (19.11.2026) — 15 × OK, 0 × ?, 0 × BŁĄD

Jedno okno Studio, jeden gracz; po próbie Studio w trybie Edit. Wynik i konsola leżą poza repozytorium.

| Punkt | Wynik |
|---|---|
| N00 Edit | OK — 17 źródeł = lokalne, skrót zgodny, zero części |
| N01 serwer | OK — gotowy, wyłącznik włączony, 12 rigów |
| N02 NPC przy karczmie | OK — 6 NPC bazaru zbudowanych, 465 brył = dane, zero części z kolizją, dotykiem albo promieniami, stopy na posadzce, sześć figur z klocków schowanych u gracza, kolizje figur zostały |
| N03 tabliczki | OK — Bolko / Karczmarz · Zadania; Pionek / Mistrz gier · Zagraj; Zefir / Mag · Sklep; Radomir / Zbrojmistrz · Sklep; Tymon / Trener · Mini-gry; Jagoda / Opiekunka · Zagroda petów; kowal ma tabliczkę |
| N04 spoczynek | OK — NPC w zasięgu się ruszają (głowa 0,09–0,68 st między odczytami), dalsze stoją uśpione |
| N05 powitanie | OK — zbrojmistrz: jedno powitanie po podejściu, tekst nad tabliczką, potem spoczynek |
| N06 wzrok | OK — gracz z lewej strony opiekunki: tułów +0,18 rad, głowa +0,34 rad, głowa patrzy na gracza (zgodność kierunku 1,00) |
| N07 gest na polecenie | OK — `graj` zwraca 1,8 s, klip gest, po czasie spoczynek; nieznany klucz → `false` |
| N08 kotwica i `postaw` | OK — kotwica z tagiem → trener Siły (61 brył, skala 1,1); `postaw` → golem (52 bryły, skala 1,5, stopy na ziemi); po usunięciu nic nie zostaje |
| N09 wyłącznik | OK — `false`: NPC 0, figury znów widoczne; `true`: NPC wracają |
| N10 podpowiedź E i dymek | OK — podpowiedź E karczmy włączona, 6,0 st od głowy gracza na stoisku (zasięg 10); dymek bazaru chowa tabliczkę NPC na swój czas, potem tabliczka wraca |
| N11 czas pętli | OK — 0,035–0,039 ms średnio w siedmiu przebiegach (najdłuższa klatka pętli 0,06–0,24 ms), czas klatki 16,7 ms |
| N12 konsola | OK — bez wpisów pakietu |
| N13 zrzuty | OK — osiem zrzutów w `klatki/` |
| N14 powrót do Edit | OK |

**Sąsiedzi po wdrożeniu NPC** (`swiat/przejscie_gry/regresja_calosci.py <folder> "proba dymna,bazar"`, 10:04–10:10): próba dymna całej gry 13 × OK (w tym E przy trenerze w bazarze i runda mini-gry; klatka 16,7 ms). Próba bazaru 11 × OK, 1 × ? (czas klatki — ocenia człowiek), 2 × BŁĄD: B04 i B13, oba o zbrojowni — E dochodzi do serwera i klienta (zdarzenie okna, sygnał `Shop`), ale dymek zastępczy się nie pokazuje, bo zbrojownia otwiera już prawdziwe okno sklepu (pakiet `swiat/sklep_proba`), czego próba bazaru jeszcze nie zna. To wniosek z odczytów próby (dymek `false` przy otwartym oknie), nie osobno sprawdzony przebieg bez NPC.

### Poprawione po próbie i po zrzutach

1. **Tabliczka a dymek bazaru.** Dymek bazaru (tekst po E) wypada dokładnie w miejscu tabliczki. Tabliczka NPC znika
   teraz na czas każdego cudzego dymka zaczepionego nad głową NPC i wraca po nim. Podpowiedź E Roblox (też dymek
   „zawsze na wierzchu”, ale przy tułowiu) tabliczki nie chowa — pierwsza wersja chowała ją przez cały czas stania
   przy ladzie.
2. **Koniec dymka** wykrywa przegląd co 0,25 s, a nie zdarzenie zniszczonej instancji (przy odroczonych sygnałach
   takie zdarzenie nie dochodzi i tabliczka nie wracała).
3. **Tabliczka maga** wisiała 10 st nad posadzką: kapelusz jest niższy (czubek 8,6 zamiast 9,3 st), a odstęp
   tabliczki od głowy mniejszy u wszystkich (0,55 zamiast 0,75 st).
4. **Tabliczka kowala** nad głową była z uliczki niewidoczna (daszek, falbana i szyld kuźni). Wisi teraz przed
   falbaną, tuż nad szyldem „KUŹNIA” (`obce_modele` → `dol`, `przod`).
5. **Próba:** czeka, aż klient zobaczy gracza po przeniesieniu; podpowiedzi E szuka w kontenerze pakietu bazaru.

### Zrzuty (`klatki/`, bez interfejsu i nazw graczy)

| Plik | Co widać |
|---|---|
| `npc_karczma.jpg` | Bolko za ladą karczmy, tabliczka z imieniem i rolą |
| `npc_mistrz_gier.jpg` | Pionek przy planszy, w tle karczmarz |
| `npc_mistrz_gier_z_boku.jpg` | Pionek z boku: siedzi na stołku, nogi pod stołem (kadr kontrolny, ciemny) |
| `npc_sklep_magiczny.jpg` | Zefir za ladą sklepu magicznego, tekst powitania nad tabliczką (lampa sklepu zasłania jego część) |
| `npc_zbrojownia.jpg` | Radomir z mieczem, tekst powitania „Dobra stal czeka!” |
| `npc_training_center.jpg` | Tymon przy tablicy wyboru mini-gier |
| `npc_zagroda_petow.jpg` | Jagoda w zagrodzie petów, patrzy na gracza |
| `npc_kowal.jpg` | kowal w kuźni z tabliczką „Krzesimir / Kowal” nad szyldem |

## Wyniki bez Studio (19.11.2026)

- `przebuduj.py` jedenastu modułów `npc_*` (`--bez-filmow`): każdy 12 plików, kontrola eksportów 5/5 zgodnych.
- `testy/test_npc.py`: 29 testów OK — dane, bazar, logika, `LogikaNpc.luau` wykonana interpreterem = lustro
  (3 × 1500 losowych wywołań, 7 zepsutych wersji wykrytych), zasady, punkty trenerów z pakietu treningu.
- `sprawdz_luau_npc.py`: 17 plików i kod budowniczego bez błędów. `zbuduj.py --sucho` i `--trenerzy --sucho`: OK.
  `proba_play.py --sprawdz`: 15 punktów, składnia bez błędów.
- Bazar: `dane.py --sprawdz` — aktualny, skrót bez zmian; `testy/test_bazaru.py` — 38 testów OK.

## Czego nie sprawdzono

- **Trenerów na arenie:** `--trenerzy` sprawdzone bez Studio i odmową na starej arenie; w nowych sceneriach nie stali.
- **Zmian po próbie** (Pancerz bez trenera, klip „akcja”, krótsze przejście do niego): tylko bez Studio — kontener
  w Studio jest sprzed nich, a próba N00–N14 nie była po nich powtarzana.
- **Zrzutu tabliczki obok dymka bazaru:** narzędzie zrzutów nie pokazuje dymków z interfejsu gracza, więc zachowanie
  (tabliczka znika i wraca) jest sprawdzone odczytem (N10), nie obrazem.
- **Prawdziwego naciśnięcia E przy NPC** w tej próbie — robi to próba pakietu bazaru.
- Wnętrza sklepów są ciemne: NPC w zbrojowni i karczmie widać słabiej niż figury w mocnych barwach — do oceny okiem.
- Mistrz gier: z boku widać, że siedzi na stołku i mieści się pod stołem; kadr jest ciemny, dokładnie nie mierzono.
- Lampa sklepu magicznego wisi między graczem a tabliczką maga i zasłania jej część z miejsca przy ladzie.
- Klipy to szkice (1,6–2,7 s); ruch okiem oceni człowiek w grze. Telefonu ani dwóch graczy naraz nikt nie mierzył.

## Wybory do oceny

- **Imiona:** Bolko, Pionek, Zefir, Radomir, Tymon, Jagoda, Krzesimir, Borys, Głaz, Iskra, Wiór, Runa, Fart.
- **Wygląd każdej postaci** (plansza zbiorcza) — w tym: karczmarz z pakietu postaci (brązowe włosy, wąsy, chochla)
  zamiast łysego rudobrodego z figury bazaru; mag-sklepikarz jako starszy człowiek (bohater Mag to kot).
- **Skala:** sprzedawcy 1,10–1,15 (figury miały ok. 6,8 studa, gracz 5,3), trenerzy 1,10, golem 1,50.
- **Gesty roli** i teksty powitań („Witaj w karczmie!”, „Zagrasz w kostkę?”…).
- **Zachowanie:** zasięg powitania 14 st, gest co 9–18 s, kąty wzroku.
- **Figury z klocków:** zostają w mapie schowane u gracza (odwracalne) — po akceptacji NPC można je usunąć z generatora mapy.
- **Kowal:** zostaje w swoim pakiecie (już jest NPC) i dostaje tylko tabliczkę, czy przenieść go tutaj (wzrok, powitanie).
