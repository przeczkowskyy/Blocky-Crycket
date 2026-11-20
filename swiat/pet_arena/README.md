# Pet Arena — etap 1: rdzeń (D-118, propozycja)

*Throw your pet into the pit, hold the golden center, knock the others out.* Osobna, samowystarczalna gra we własnym
miejscu Roblox (plik lokalny `PetArena.rbxlx`, kontener `Workspace/PetArenaGra`). Projekt: `B&C/Gra/Pet Arena — projekt
prototypu.md`. Warsztat skopiowany i przerobiony z `swiat/bonk/` (w czasie gry i budowy nic nie jest importowane z BONK;
modele petów czytane są z tych samych danych klocków `swiat/postacie/<id>.py`, z których korzystał BONK).

## Co działa (etap 1)

- **Scena** (598 części + 12 wzorców petów): okrągły dół, obrzeże-trybuna z poręczą i niewidzialną barierą, 8 miejsc
  graczy (kolorowe płytki), platforma-arena r 24 z pasami krawędzi (czerwono-białe), trzy strefy złota z napisami na
  podłodze (**x5** złoty środek r 4,5 · **x2** pierścień do r 12 · **x1** do krawędzi; napisy obrócone lokalnie do kamery
  gracza), fosa z wodą i 6 gejzerami, ściana dołu, stopnie trybuny, łąka i 18 drzew z klocków, makiety na etap 2 (trzy
  jajka na cokołach z tablicą „EGGS — COMING SOON”, mata „TRAINING MAT — SOON”), SpawnLocation, światło (14:30,
  Atmosphere, Sky).
- **Kamera stała** (Scriptable) za miejscem gracza: cała arena w kadrze bez ruszania kamerą (pas 0,17–0,85 wysokości
  ekranu, także na telefonie 667 × 375), własny awatar w lewym dolnym rogu kadru. Sterowanie postacią wyłączone — gracz
  stoi na swoim miejscu, stuknięcia idą w arenę.
- **Rzut:** telefon — stuknięcie w arenę, komputer — klik (pod myszą podgląd celu), pad — lewa gałka przesuwa celownik,
  A rzuca. Pet leci łukiem z ręki gracza (znacznik celu na arenie), przy lądowaniu odpycha sąsiadów. Serwer sprawdza:
  typy, cel na arenie, najwyżej 8 petów (napis ARENA FULL!), jeden pet gracza naraz, odpoczynek, wiadro tempa akcji.
- **Walka na serwerze w 2D** stałym krokiem 0,05 s (bez fizyki Roblox): pet idzie do środka, a gdy wróg w zasięgu
  wzroku — do najbliższego; bije w zasięgu; **odrzut = siła × (1 + 2 × ubytek życia) / waga**, tarcie, krytyki 10 %
  (×1,5 obrażeń, ×1,6 odrzutu, napis CRIT!), rozrzut ±14°, krótkie oszołomienie po ciosie, rozpychanie (cięższy ustępuje
  mniej). **RING OUT** (środek peta za krawędzią): zsuwa się do fosy, SPLASH!, gejzer wystrzeliwuje go łukiem do
  właściciela; **KO** (życie 0): gwiazdki, wirujący odlot. Wybicie zalicza się ostatniemu, kto trafił w ciągu 4 s.
- **Umiejętności** (pasek: z czasem 0,06/s, +0,06 za cios, +0,04 za trafienie; przycisk ABILITY z wypełnieniem i nazwą,
  pulsuje, gdy gotowy; spacja / Q / X na padzie) — **12 petów, 12 różnych umiejętności, 9 rodzajów**: Slime BOUNCE
  (rykoszet po 3 celach), Acornling HEADBUTT (krótka szarża, staje na pierwszym), Croaker TONGUE (przyciąga i przerzuca
  za siebie), Shroomling SPORE CLOUD (ogłuszenie wokół 1,5 s), Moss Snail SHELL (3 s nie do ruszenia, odbija
  napastników), Leaf Fox DASH (przelot po linii), Thorn Wolf POUNCE (skok na króla), Wisp BURN (stożek ognia,
  obrażenia w czasie), Dragonfly FREEZE (zamrożenie 2,2 s — zamrożony ślizga się dalej), Forest Troll GROUND SLAM (fala
  odrzutu), Ruin Armadillo ROLL (toczy się przez całą arenę), Hut Toad SKY DIVE (wyskok i lądowanie z wielką falą na
  największym tłumie).
- **Złoto:** co sekundę baza 1 × mnożnik strefy × stopień peta; „+N G/s” nad własnym petem (napis „YOU +5 G/s”), w
  liczniku u góry i wyskakujące „+5”; premia za wybicie 15 × stopień ofiary (dziki: 10 × stopień), monety lecą do gracza.
- **Nagroda za głowę:** król środka (pet najdłużej w złotym środku, od 1,5 s) nosi koronę z klocków i napis BOUNTY N;
  nagroda startuje od 10 i rośnie 3/s; kto wybije króla, zgarnia ją (napis BOUNTY +N!). Król wypchnięty ze środka na
  dłużej niż 1,5 s traci koronę i nagrodę. Napisy KING! (mój) i NEW KING! (cudzy).
- **Dzikie pety (boty):** dopełniają arenę do 5 petów (po jednym co 2,2 s), wyskakują z gejzerów, stopnie losowane z wag
  50/30/14/5/1, życie × 0,9, używają umiejętności (wróg w zasięgu albo po 1–4 s czekania), dają premię za wybicie i
  nagrodę za głowę, gdy są królem.
- **Gracz:** profil w pamięci serwera (`L.profilNowy` / `L.profil` z wersją — gotowy pod zapis w etapie 2), dwa pety
  startowe (Slime, Acornling) i trzeci **pet próbny** (losowy od Uncommon w górę, napis TRIAL — zamiast jajek, żeby ludzie
  spróbowali mocniejszych umiejętności), drużyna — trzy karty po lewej (stuknięcie wybiera, 1/2/3 na klawiaturze, LB/RB na
  padzie) ze stanem READY / IN ARENA / RESTING 42s. Po RING OUT albo KO pet odpoczywa 60 s; rzut sam wybiera gotowego peta.
- **Ekran po angielsku:** GOLD i +G/s u góry, karty drużyny, przycisk ABILITY (prawy dolny róg, 104 pt) z życiem i
  paskiem umiejętności własnego peta nad nim, podpowiedź „Tap the arena to throw your pet!” (komputer: Click…, pad:
  Aim with the stick…; znika po pierwszym rzucie; potem raz „Ability ready — tap ABILITY!”), napisy zdarzeń (RING OUT!,
  KO!, KING!, NEW KING!, ARENA FULL!). Nad każdym petem napis (YOU / Player N / WILD) i pasek życia w kolorze właściciela.
- **Czytelność:** własny pet — żółty obrys widoczny przez innych (Highlight AlwaysOnTop), żółty krążek pod nim i napis
  YOU; pety innych graczy — obrys i krążek w kolorze ich miejsca; dzikie — szary krążek, bez obrysu. Stany widać
  wypełnieniem: lód (niebieski), skorupa (zielony), ogień (pomarańczowy, migocze), ogłuszenie (żółty, kiwanie).
- **Dźwięki:** te same odcinki arkusza efektów co BONK (cios, krytyk, plusk, monety, klik, umiejętność, król, KO) —
  w pliku lokalnym ładują się (18/18 w próbie). Bez muzyki.

## Liczby (propozycja do strojenia — wszystkie w `ustawienia.json`)

| Co | Wartość |
|---|---|
| Arena / strefy | r 24; złoty środek r 4,5 (×5), pierścień r 12 (×2), reszta (×1) |
| Klasy wagi (lekki / średni / ciężki) | waga 0,7 / 1,0 / 1,5; życie 100 / 120 / 150; cios 4,5 / 5,2 / 6; odrzut ciosu 12 / 14 / 16; prędkość 9 / 7,5 / 6; przerwa 0,85 / 1,0 / 1,2 s; wysokość modelu 5 / 6 / 7,5 st |
| Stopień (rzadkość 1–5) | życie +20 %, cios +15 %, odrzut +6 % na stopień |
| Odrzut | v = siła × (1 + 2 × ubytek życia) / waga; tarcie 5,5/s; pełne życie lekkiego: ok. 3 st drogi, przy 25 % życia ok. 7–8 st |
| Złoto na minutę (pet Common, stopień 1) | środek **300**, pierścień ×2 **120**, ×1 **60**; Rare (stopień 3): 900 / 360 / 180 |
| Premie | wybicie 15 × stopień (dziki 10 × stopień); nagroda za głowę 10 + 3/s |
| Arena | najwyżej 8 petów; dzikie dopełniają do 5 |
| Odpoczynek | 60 s |
| Tempo akcji | wiadro 3/s, zapas 4 |

**Symulacja logiki** (ta sama `LogikaPetArena.luau` w interpreterze, bez Studio):
- Same dzikie pety, 5 naraz, 60 s: 14 wybić (10 RING OUT, 4 KO), średnie życie peta **17 s**, pierwsze wybicie po 9 s.
- Gracz przez 4 min (Slime, Acornling, Shroomling; rzut blisko środka, umiejętność od razu, gdy pełna; 4 dzikie obok):
  **134–140 złota na minutę**, życie jego peta średnio **13–16 s** (od 4 do 35 s), **pierwsze własne wybicie po 34–54 s**,
  7–8 wybić w 4 min. Przy odpoczynku 60 s gracz **przez ok. 95 s z 240 (40 %) nie ma kogo rzucić**; przy 25 s — 2–31 s,
  a złoto rośnie do 158–186 na minutę. Odpoczynek to do decyzji po graniu (`odpoczynek_s`).

## Jak zbudować i zagrać

```
python -B swiat/pet_arena/dane.py                    # po zmianie ustawień: zrodla/DanePetArena.luau
python -B swiat/pet_arena/testy/test_pet_arena.py    # testy bez Studio (--tabela: symulacja walki)
python -B swiat/pet_arena/zbuduj.py --sucho          # plan i kontrola Luau bez Studio
python -B swiat/pet_arena/zbuduj.py                  # budowa w otwartym miejscu PetArena (ok. 3 s; --studio <id>)
python -B swiat/pet_arena/zbuduj.py --skrypty        # po zmianie samego kodu
python -B swiat/pet_arena/zbuduj.py --stan | --usun | --wlacz on|off
python -B swiat/pet_arena/testy/proba_play.py <folder poza repo> [--studio <id>]   # próba w Play (P00–P16)
```

Budowa odmawia w miejscu obecnej gry B&C, działa tylko w trybie Edit i tylko we własnym kontenerze. Zagrać: otworzyć
plik miejsca `PetArena.rbxlx` w Studio, **Play** (F5) — gracz staje na obrzeżu, stuka / klika w arenę. Prywatna
wersja testowa (D-044, decyzja ludzi): puste miejsce, `zbuduj.py --publikacja` (skrypty bez strażnika Studio).

## Struktura

| Plik | Co |
|---|---|
| `ustawienia.json` | jedyne źródło liczb: scena, strefy, kamera, walka, rzut, złoto, nagroda, umiejętność, odpoczynek, boty, gracz, klasy wagi, rzadkości, 12 petów z umiejętnościami, teksty, dźwięki |
| `dane.py` | generator `zrodla/DanePetArena.luau` (liczby petów z klasy wagi i stopnia, sloty, kamera, dźwięki), wzorców petów (bryły z `swiat/postacie/<id>.py`, skala do wysokości klasy) i części sceny; rzut kamery na ekran (test kadru) |
| `zbuduj.py` | budowa w Studio: kontener, moduły i skrypty, sygnały, scena (paczki po 300), wzorce, napisy stref i makiet, SpawnLocation, Lighting; `--skrypty`, `--stan`, `--usun`, `--wlacz`, `--publikacja` |
| `zrodla/LogikaPetArena.luau` | czyste rachunki (wykonywane też w testach bez Studio): strefy, odrzut, wiadro tempa, stan areny, ciosy, 9 rodzajów umiejętności, krok walki (lądowanie, akcje, chodzenie, odrzut i tarcie, rozpychanie, ogień, RING OUT / KO z zaliczeniem), król i nagroda, złoto co sekundę, boty, profil, drużyna, odpoczynek |
| `zrodla/SerwerPetArena.server.luau` | serwer: gracze i miejsca, rzuty i umiejętności z kontrolą, pętla stałego kroku, nagrody, odpoczynek, boty, migawki (bufor), zdarzenia, haczyki prób |
| `zrodla/KlientPetArena.client.luau` | klient: widoki petów (wzorce, wygładzanie, lot rzutu, skok, RING OUT i KO), korona, napisy nad petami (warstwa 2D), efekty zdarzeń, dźwięki, kamera, wejście (dotyk, mysz, klawiatura, pad), haczyki prób |
| `zrodla/EfektyPetArena.luau`, `zrodla/InterfejsPetArena.luau` | efekty w świecie (z EfektyBonk + gejzer, chmura, lód, płomień, język, pierścień) i ekran gracza |
| `testy/test_pet_arena.py`, `testy/proba_play.py` | testy bez Studio (21) i próba w Play (P00–P16) |
| `klatki/` | zrzuty z próby (Player 1, bez nazwy konta i listy graczy) |

W Studio (`Workspace/PetArenaGra`, atrybut `Wygenerowane`): `Scena/{Arena, Fosa, Sciana, Obrzeze, Trybuna, Sloty, Drzewa,
Teren, Makiety}`, `Wzorce/Pet_<id>` (w grze serwer przenosi je do `ReplicatedStorage/PetArenaWzorce`), `Start`
(SpawnLocation), `Moduly/*`, `SerwerPetArena`, `KlientPetArena`, `Sygnaly/{Akcja, Zdarzenia, Stan, SterowanieSerwera,
SterowanieKlienta}`. Atrybuty kontenera: `PetArenaWlaczony`, `Skrot`, w grze `SerwerGotowy`, `WzorceGotowe`, `ZapisStan`,
`KlientGotowy` (u klienta).

**Sieć:** od klienta tylko `Sygnaly/Akcja (rodzaj, a, b, c)`: `"rzut", nr w drużynie, x, z` · `"umiejetnosc"` ·
`"wybierz", nr` — serwer sprawdza typ rodzaju i argumentów, wiadro tempa (wspólne dla akcji), cel na arenie, limit 8,
jeden pet gracza, odpoczynek. Do klientów: `Sygnaly/Stan` (UnreliableRemoteEvent, bufor 14 + 22 bajty na peta co 0,066 s:
id, pet, właściciel, faza, flagi stanów, x, z, życie, pasek, złoto/s, kierunek; król i nagroda) i `Sygnaly/Zdarzenia`
(lista z kroku: `rzut`, `ladowanie`, `cios`, `umiejetnosc`, `ladowanie_skoku`, `odbicie`, `odbicie_slime`, `ringout`,
`ko`, `krol`, `krol_stracil`, `zloto`, `odmowa`). Stan gracza w atrybutach `PA_*` (ustawia tylko serwer): `PA_Slot`,
`PA_Nazwa`, `PA_Zloto`, `PA_GS`, `PA_Pet`, `PA_Rzucil`, `PA_Wybicia`, `PA_Druzyna`, `PA_Odpoczynek` (czasy serwera),
`PA_Probny`, `PA_Wybrany`, `PA_NaArenie`.

## Próba w Studio (20.11.2026, wieczór)

`python -B swiat/pet_arena/testy/proba_play.py <folder poza repo>` — **17/17 OK** (okno Studio na wierzchu, nocne
zaciemnienie ekranu). Testy bez Studio: **21 OK** (dane, kadr kamery na czterech ekranach, logika: odrzut a życie i waga,
krawędź, KO z zaliczeniem, strefy złota, nagroda za głowę, limit areny i cel, odpoczynek i drużyna, wiadro tempa, boty,
każda umiejętność, symulacja; źródła: kontrola Luau, strażnik, sieć, znacznik prób; `zbuduj.py --sucho`).

| Punkt | Wynik |
|---|---|
| P00 budowa zgodna z repo | 6 źródeł, scena 598 części, 12 wzorców, start, ClockTime 14,5 |
| P01–P02 wejście i kamera | klient gotowy 3 s po Play; „Player 1”, slot 1; kamera Scriptable; arena w pasie 0,17–0,85 ekranu (okno i telefon); awatar w kadrze (lewy dół); podpowiedź „Click the arena…”; dźwięki 18/18 załadowane |
| P03 pierwszy rzut | **3,5 s** od wejścia (droga stuknięcia: punkt ekranu → promień → arena), pet ląduje i walczy |
| P04 walka i odrzut | ciosy padają (ok. 20 w 4 s); ten sam cios Slime'a: odrzut **23 przy pełnym życiu, 47 przy 25 %** |
| P05 RING OUT | pet gracza za krawędzią → fosa, gejzer, łuk do właściciela; karta RESTING 58s |
| P06 KO | dziki pet z życiem 0 → KO, gracz +20 złota (premia), licznik wybić |
| P07 strefy złota | +5 / +2 / +1 G/s (Acornling, stopień 1) — na serwerze i na ekranie |
| P08 umiejętności | HEADBUTT przyciskiem ABILITY (przycisk gotowy, nazwa), GROUND SLAM (Troll), SKY DIVE (Toad) — zdarzenia i efekty |
| P09 dzikie pety | dopełniają do 5 w 7 s, w 12 s ok. 5 umiejętności, 60–70 ciosów, 3–4 wybicia |
| P10 nagroda za głowę | mój pet królem (korona, BOUNTY 17,6); dziki król wybity przez mojego peta → **+43 złota** (premia 20 + nagroda 17) |
| P11 odpoczynek i drugi pet | rzut sam wybrał gotowego (Acornling); karty: RESTING 55s / IN ARENA / READY |
| P12 limit areny i tempo | przy 8 petach rzut odrzucony (ARENA FULL!); 30 akcji naraz → 26 odrzuconych |
| P13 telefon 667 × 375 | wszystko w ekranie, najmniejszy przycisk **56 pt**, bez nakładania; zrzut `pa_telefon.jpg` |
| P14 czas klatki, 8 petów | **16,7 ms (60 kl./s)**, najwyżej 22–28 ms; pętla klienta 0,7–1,2 ms; krok serwera 0,012 ms |
| P15 konsola | bez błędów pakietu |
| P16 | Studio w Edit; miejsce zapisane do pliku (save_place) |

Zrzuty (`klatki/`, „Player 1”, bez nazwy konta i listy graczy): `pa_wejscie.jpg` (po wejściu), `pa_rzut.jpg` (pet w
locie), `pa_ring_out.jpg` (RING OUT, SPLASH, pet w łuku nad dołem), `pa_ko.jpg` (KO! +10), `pa_krol.jpg` (korona,
BOUNTY), `pa_umiejetnosc_troll.jpg` (GROUND SLAM), `pa_umiejetnosc_toad.jpg` (SKY DIVE, BOOM!), `pa_arena.jpg` (walka z
dzikimi), `pa_osiem_petow.jpg` (8 petów), `pa_telefon.jpg` (ekran telefonu 667 × 375 powiększony do okna — obraz 3D ma
proporcje telefonu).

## Czego jeszcze nie ma i ograniczenia

- Brak zapisu do magazynu (profil w pamięci; znacznik próby z `tools/zapis_prob.py` stawiany też na `PetArenaGra`).
- Pad: działa celownik, rzut, umiejętność i wybór peta, ale bez znaczków przycisków na ekranie i bez prób na padzie.
- Gracz nie animuje rzutu (awatar stoi); brak muzyki.
- Pet próbny w trzecim slocie to zastępstwo jajek na czas etapu 1.
- Tarcza słabszego (różnica stopni) — etap 2; dziś silny pet bije słabych bez ograniczeń.
- Etykiety „+G/s” tylko nad własnym petem; obcy pokazują imię gracza.
- Kamera nie da się obracać (celowo: cała arena zawsze w kadrze).

## Co zostaje na etap 2

Jajka (trzy stopnie, jawne szanse, za złoto) i kolekcja, Księga petów, trener i mata AFK (poziom gracza dla wszystkich
petów), BOSS i GOLDEN PET z zapowiedzią i odliczaniem, tarcza słabszego, tablice (złoto/s, najdłużej w środku, wybicia)
i komunikaty serwera, zapis z ochroną prób, pad do końca, animacja rzutu, muzyka, demo wideo i grafiki strony.
