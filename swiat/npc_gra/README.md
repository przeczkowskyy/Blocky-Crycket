# Postacie niezależne w grze (D-109) — `swiat/npc_gra`

> **Status: propozycja.** Decyzja D-109 (Karol, 19.11.2026; czeka na potwierdzenie Pawła) mówi, że karczmarz, sprzedawcy,
> mistrz gier i postacie przy mini-grach mają być NPC ze szkieletem i animacją, a nie figurami z klocków. Wygląd,
> imiona i gesty poszczególnych postaci to propozycje do oceny (lista na końcu).
> **Stan 19.11.2026: część A — wszystko, co da się zrobić bez Roblox Studio.** W Studio nic jeszcze nie stoi:
> budowa kontenera, próba w grze i zrzuty to część B.

## Co to jest

NPC to model postaci z pakietu postaci (`swiat/postacie`: kości R15, stawy, klipy), złożony w grze ze zwykłych części
Roblox — bez wgrywania czegokolwiek. Każdy klient składa NPC u siebie i sam je animuje:

- **spoczynek** w pętli (oddech), co 9–18 s **gest roli**, **powitanie** (machanie i krótki tekst), gdy gracz podejdzie
  na 14 studów, **głowa i tułów obracają się ku graczowi** (głowa do 62°, tułów do 22°), nad głową **tabliczka**
  z imieniem i rolą;
- **tanio:** rig powstaje dopiero ≤ 150 studów od gracza, rusza się tylko ≤ 55 studów (dalej stoi w pierwszej klatce
  spoczynku), bliżej niż 25 studów liczony co klatkę, dalej co drugą;
- **nie przeszkadza:** żadna część NPC nie ma kolizji, dotyku ani promieni; podpowiedzi E zostają na częściach
  swoich pakietów (bazar: `_Interakcja`), więc działają w tym samym miejscu.

## Obsada (propozycja)

| NPC (id) | Imię · rola | Gdzie | Klipy: spoczynek / powitanie / gest | Bryły | Skala |
|---|---|---|---|---|---|
| `karczmarz` | Bolko · Karczmarz | bazar, karczma (za ladą) | idle / zaproszenie / śmiech ×2 | 98 | 1,15 |
| `mistrz_gier` | Pionek · Mistrz gier | bazar, karczma (na stołku przy planszy) | siedzi i macha nogami / machanie / rzut kostką | 75 | 1,10 |
| `mag` | Zefir · Mag | bazar, sklep magiczny | oddech / machanie / unosi kostur, dłoń krąży nad kryształem | 79 | 1,15 |
| `zbrojmistrz` | Radomir · Zbrojmistrz | bazar, zbrojownia | oddech / machanie / ogląda klingę i salutuje mieczem | 72 | 1,15 |
| `trener` | Tymon · Trener | bazar, Training Center (wejście na mini-gry) | oddech / machanie / napina bicepsy | 62 | 1,15 |
| `opiekunka` | Jagoda · Opiekunka | bazar, zagroda petów | oddech / machanie / potrząsa wiadrem z kością | 80 | 1,10 |
| `kowal` | Krzesimir · Kowal | bazar, kuźnia — **stoi już jako rig z klipami** w `Workspace/KowalProba` (18.11) | spoczynek / kucie / radość (jego pakiet) | 90 | 1,00 |
| `trener_sila` | Borys · Trener Siły | arena, mini-gra Siły | oddech / machanie / wyciska hantlę ×2 | 61 | 1,10 |
| `golem` | Głaz · Trener Pancerza | arena, mini-gra Pancerza (golem zostaje golemem) | ciężki oddech / unosi pięść / zamach i cios pięścią | 52 | 1,50 |
| `trener_kondycja` | Iskra · Trenerka Kondycji | arena, mini-gra Kondycji | oddech / machanie / trzy uderzenia pałką i krok w miejscu | 58 | 1,10 |
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
| Bazar: 6 NPC | 466 brył, **568 części u klienta** (bryły + 15 kości + korzeń + tabliczka na postać); bez cieni |
| Figury z klocków, które zastępują | 250 części (zostają w mapie, u gracza niewidoczne) |
| Wszystkie 12 rigów (z trenerami) | 867 brył |
| Dane | `DaneNpc` 8 kB + 12 rigów po 21–33 kB = **306 kB** źródeł modułów (pobierane raz; rig wczytuje się dopiero przy pierwszej budowie postaci) |
| Serwer | nic nie buduje i nic nie wysyła: jeden skrypt z wyłącznikiem |
| Praca co klatkę | tylko NPC ≤ 55 studów: na postać 15 interpolacji pozy i 15 wpisów stawów (≤ 25 studów co klatkę, dalej co drugą); przegląd odległości co 0,25 s |
| Spodziewany czas pętli | rząd 0,1–0,2 ms na klatkę przy sześciu NPC w zasięgu (dla porównania: 12 stojących bohaterów w `swiat/bohater_swiat` to 0,29–0,44 ms) — **do zmierzenia w części B** (próg próby 1,5 ms) |

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

Trenerów ten pakiet nie stawia (arenę przebudowuje `swiat/trening_proba`). Są trzy równoważne sposoby — NPC pojawia
się u gracza, gdy ten jest bliżej niż 150 studów:

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
   (sila → `trener_sila`, pancerz → `golem`, kondycja → `trener_kondycja`, zrecznosc → `trener_zrecznosc`,
   inteligencja → `trener_inteligencja`, szczescie → `trener_szczescie`).
2. **Polecenie budowniczego** (kotwica w `Workspace/NpcGra/Kotwice`):
   `python -B swiat/npc_gra/zbuduj.py --kotwica trener_sila --klucz trening_sila --poz 10,0.5,20 --patrz 10,30`
   (usunięcie: `--bez-kotwicy trening_sila`).
3. **W grze, u klienta:** `workspace.NpcGra.Sygnaly.Polecenie:Invoke("postaw", "trening_sila", "trener_sila", CFrame, skala?)`
   i `Invoke("usun", "trening_sila")`.

Ruch na życzenie mini-gry (u klienta): `Polecenie:Invoke("graj", "trening_sila", "gest")` → czas klipu w sekundach
(albo `false`, gdy NPC nie stoi albo jest za daleko); `"powitanie"` i `"spoczynek"` tak samo. Gesty odpowiadają
mechanice: golem — cios pięścią, trenerka Kondycji — uderzenia pałką, drwal — cięcie. Części gry (pięść golema,
ramię miotacza) zostają częściami `trening_proba`; NPC ich nie zastępuje, dopóki tamten pakiet tak nie postanowi.

## Pliki

| Plik | Co to |
|---|---|
| `ustawienia.json` | obsada (imiona, role, teksty powitań, klipy), skale, zasięgi, czasy, wzrok, tabliczka — jedyne miejsce do strojenia |
| `dane.py` | generator `zrodla/DaneNpc.luau` i `zrodla/rigi/Rig_<id>.luau`; tabela obsady i rachunek (`--tabela`) |
| `logika_npc.py` | lustro `LogikaNpc.luau` |
| `zbuduj.py` | budowa kontenera w Studio (`--sucho`, `--stan`, `--usun`, `--kotwica`), `kotwica_luau()` dla innych pakietów |
| `plansza.py` | plansza zbiorcza `podglady/npc_razem.jpg` (Blender) |
| `sprawdz_luau_npc.py` | kontrola statyczna źródeł Luau i kodu budowniczego |
| `zrodla/LogikaNpc.luau` | czysta logika: stopień szczegółów, powitanie, gesty, wzrok, numer klatki |
| `zrodla/RigNpc.luau` | budowa rigu z danych, klipy, przejścia, wzrok |
| `zrodla/KlientNpc.client.luau` | stanowiska (dane, kotwice, polecenia), chowanie figur, tabliczki, pętla |
| `zrodla/SerwerNpc.server.luau` | wyłącznik i haczyk prób; poza Studio usuwa kontener |
| `testy/test_npc.py` | testy bez Studio (28) |
| `testy/proba_play.py` | próba w grze N00–N14 (napisana; `--sprawdz` działa bez Studio) |
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
# część B (Studio w trybie Edit):
python -B swiat/npc_gra/zbuduj.py [--studio <id>]
python -B swiat/npc_gra/testy/proba_play.py <folder wyników POZA repo> [--bez-zrzutow]
python -B swiat/npc_gra/zbuduj.py --usun                        # przed publikacją miejsca
```

## Wyniki bez Studio (19.11.2026)

- `przebuduj.py` jedenastu modułów `npc_*` (`--bez-filmow`): każdy 12 plików, kontrola eksportów 5/5 zgodnych.
- `testy/test_npc.py`: 28 testów OK — dane (13 postaci, 12 rigów, klipy, stopy na ziemi, źródła poniżej limitu,
  zapis deterministyczny), bazar (6 stanowisk = miejsca z polem `npc`, miejsce i kierunek figury, dane bazaru bez
  zmian), logika (podejście i odejście, histereza, powitanie raz i po powrocie, gesty co 9–18 s, wzrok),
  `LogikaNpc.luau` wykonana interpreterem = lustro na 3 × 1500 losowych wywołaniach, 7 celowo zepsutych wersji
  wykrytych, zasady (strażnik Studio, brak kolizji, tylko własny kontener, brak ścieżek z dysku).
- `sprawdz_luau_npc.py`: 17 plików i kod budowniczego bez błędów. `zbuduj.py --sucho`: OK (17 źródeł, 336 kB).
  `proba_play.py --sprawdz`: 15 punktów, 14 kawałków Luau, składnia bez błędów.
- Bazar po zmianie `miejsca.json`: `dane.py --sprawdz` — aktualny, skrót bez zmian; `testy/test_bazaru.py` — OK.

## Czego nie sprawdzono (część B)

- **Niczego w Studio:** budowy kontenera, wyglądu NPC z klocków w grze, chowania figur, tabliczek, powitania, wzroku,
  czasu pętli, podpowiedzi E przy NPC, zrzutów. Lista prób: `testy/proba_play.py` (N00–N14).
- Mistrz gier na stołku: wysokość i odsunięcie policzone z danych mapy; kolana wchodzą pod blat stołu (ok. 0,2 st
  w rant) — do obejrzenia na zrzucie.
- Mag jest wyższy od figury o kapelusz i kostur (czubek kapelusza 9,3 st): tabliczka wisi nad nim, do oceny.
- Dymek bazaru (tekst po E) i tabliczka NPC są blisko siebie nad głową — czy się nie zasłaniają, pokaże zrzut.
- Klipy to szkice (1,6–2,7 s), próbkowane liniowo; ruch okiem oceni człowiek w grze.
- Telefonu ani dwóch graczy naraz nikt nie mierzył.

## Wybory do oceny

- **Imiona:** Bolko, Pionek, Zefir, Radomir, Tymon, Jagoda, Krzesimir, Borys, Głaz, Iskra, Wiór, Runa, Fart.
- **Wygląd każdej postaci** (plansza zbiorcza) — w tym: karczmarz z pakietu postaci (brązowe włosy, wąsy, chochla)
  zamiast łysego rudobrodego z figury bazaru; mag-sklepikarz jako starszy człowiek (bohater Mag to kot).
- **Skala:** sprzedawcy 1,10–1,15 (figury miały ok. 6,8 studa, gracz 5,3), trenerzy 1,10, golem 1,50.
- **Gesty roli** i teksty powitań („Witaj w karczmie!”, „Zagrasz w kostkę?”…).
- **Zachowanie:** zasięg powitania 14 st, gest co 9–18 s, kąty wzroku.
- **Figury z klocków:** zostają w mapie schowane u gracza (odwracalne) — po akceptacji NPC można je usunąć z generatora mapy.
- **Kowal:** zostaje w swoim pakiecie (już jest NPC) i dostaje tylko tabliczkę, czy przenieść go tutaj (wzrok, powitanie).
