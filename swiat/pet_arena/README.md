# Pet Arena — etap 1 (rdzeń) i etap 2 (jajka, wydarzenia, trener, zapis) — D-118, propozycja

*Throw your pet into the pit, hold the golden center, knock the others out.* Osobna, samowystarczalna gra we własnym
miejscu Roblox (plik lokalny `PetArena.rbxlx`, kontener `Workspace/PetArenaGra`). Projekt: `B&C/Gra/Pet Arena — projekt
prototypu.md`. Warsztat skopiowany i przerobiony z `swiat/bonk/` (w czasie gry i budowy nic nie jest importowane z BONK;
modele petów, jajek i bossów czytane są z tych samych danych — `swiat/postacie/<id>.py`, `swiat/test_walki2/dane/` —
z których korzystał BONK).

## Co nowego (etap 2, 20/21.11.2026)

- **Czytelność:** pety ok. 1,6 × większe (8,8 / 9,6 / 10,5 st; na telefonie 667 × 375 lekki pet ok. 70–78 pt), kamera
  bliżej i niżej (nachylenie 40°, cała arena w pasie 0,12–0,82 wysokości i 0,17–0,83 szerokości — sprawdzane na 4
  ekranach). Ekran w rogach: GOLD i poziom w lewym górnym, EGGS / PETS / TRAIN w prawym górnym, drużyna po lewej,
  ABILITY w prawym dolnym — środek areny odkryty. Napisy „WILD” zastąpione kolorem krążka pod petem (szary — dziki,
  żółty — mój, kolor miejsca — inni gracze, złoty — złoty pet, czerwony — boss); paski życia cienkie nad petem.
- **Słowa komiksowe:** małe i krótkie tylko przy ciosach własnego peta; duże (RING OUT, KO, nazwa własnej
  umiejętności, +złoto, boss) najwyżej 2 naraz, ok. 0,75 s; KING / NEW KING / BOSS jako napis u góry ekranu.
- **Soczystość:** błysk trafienia (białe wypełnienie), podskok i przechył po ciosie, spłaszczenie i odbicie (do 3 petów
  naraz), smuga lotu (rzut, RING OUT, KO, szarża), większy rozbryzg w fosie, krótkie zatrzymanie (0,07 s) i wstrząs
  kamery przy wybiciach własnego peta, króla i bossa; KO — wirujący lot ok. 46 st (pół ekranu).
- **Rzut z ręki:** awatar trzyma w dłoni następnego peta (zmniejszony model), przy rzucie zamach ręką (obrót barku
  doklejony do `Transform`, jak w BONK), pet startuje z dłoni.
- **Odpoczynek 30 s** (było 60). Decyzja projektanta etapu 2 z symulacji: przy 60 s gracz z trzema petami ok. 40 % czasu
  nie ma kogo rzucić. **Karol mówił o ok. minucie** — jedna liczba `odpoczynek_s` w `ustawienia.json`, do sprawdzenia
  graniem.
- **Jajka i kolekcja:** stanowisko jajek na obrzeżu (trzy jajka na cokołach + tablica szans), okno EGGS: FOREST EGG
  360 G, SWAMP EGG 2000 G, RUIN EGG 8000 G, jawne szanse na rzadkość, tylko za złoto z gry; **pierwsze jajko darmowe**
  (drugi krok samouczka: „Hatch your free egg!”, przycisk EGGS pulsuje) — zamiast peta TRIAL z etapu 1. Scena wyklucia
  (jajko trzęsie się, pęka błyskiem w kolorze rzadkości, pet wyskakuje: NEW PET! albo **+1 STAR!**). Kopie dają
  **gwiazdki** (do 5, każda +8 % życia i siły — obrażeń i odrzutu), przy 5 gwiazdkach kopia zwraca 30 % ceny.
  Gwiazdki widać nad petem, na kartach drużyny i w oknach.
- **Okno PETS:** zakładka TEAM — trzy miejsca drużyny (dotknij miejsca, potem peta z kolekcji) i kolekcja z modelami,
  gwiazdkami i znaczkiem IN TEAM; zakładka **INDEX** — Księga: 12 miejsc, nieznane jako czarne sylwetki „???”, licznik
  INDEX n/12. Nowy pet z jajka trafia do drużyny, gdy jest wolne miejsce.
- **Wydarzenia serwera** na zmianę co 150 s (pierwsze po 90 s), z odliczaniem u góry („GOLDEN PET IN 0:30”, „BOSS IN
  0:30”): **GOLDEN PET** (złoty slime ucieka po arenie, każdy cios peta gracza = 6 × stopień złota, wybicie +150) i
  **BOSS** (Strażnik z BONK: MIRE GUARDIAN / VINE SERPENT na zmianę; ląduje z nieba w środku ze wstrząsem; życie 1400 +
  500 na gracza; co 3,2 s fala odrzutu; po 70 s ucieka; pokonany — pula 400 złota dzielona według zadanych obrażeń, co
  najmniej 80 dla każdego, kto trafił; deszcz monet i komunikat). Pasek życia bossa u góry ekranu.
- **Tarcza słabszego:** pet o ≥ 2 stopnie silniejszy zadaje słabszemu 35 % obrażeń i odrzutu (bez bossa i złotego);
  przy słabszym ikona 🛡 nad paskiem.
- **Trener:** doświadczenie za sekundę peta na arenie (1), wybicie (12), udział w bossie (40) i za stanie na macie
  (TRAIN — awatar przechodzi na matę obok swojego miejsca i ćwiczy pajacyki; 0,6 / s); poziom n wymaga 60 × n^1,45;
  każdy poziom +3 % życia i siły wszystkich petów. LV i pasek w lewym górnym rogu, napis LEVEL UP!, poziom i
  najlepszy pet nad głową każdego gracza („LV 3  Hut Toad ★★”).
- **Zapis:** własny magazyn `PetArena_Gracz_v1` (w Studio z przyrostkiem `_Studio`), ochrona prób jak w BONK (znacznik
  `ZapisProbaDo` z `tools/zapis_prob.py` — magazyn nieczytany i niepisany), wczytanie przy wejściu (3 próby), **bez
  udanego wczytania nie zapisujemy**, zapis przy wyjściu, co 60 s i przy zamknięciu serwera. Profil v2: złoto, pety z
  gwiazdkami, drużyna, Księga, doświadczenie, samouczek, wybicia, rzuty, jajka, najdłuższe panowanie; migracja z v1.
  W pliku lokalnym (miejsce nieopublikowane) magazyn bywa niedostępny — gra działa wtedy w pamięci bez błędów.
- **Pokazanie się:** trzy tablice na ścianie dołu (TOP GOLD/S, LONGEST KING, KNOCKOUTS — gracze serwera, co 2 s),
  komunikaty (Epic / Legendary z jajka, zgarnięta nagroda za głowę ≥ 40, pokonany boss), napisy nad graczami.
- **Pad:** lewa gałka — celownik, A rzut, X umiejętność, LB/RB wybór peta, Y okno PETS, w górę EGGS, w dół TRAIN,
  B zamyka okno; w oknach zaznaczenie przycisków (GuiService) i A klika; znaczki przycisków na ekranie, gdy gra pad.
- **Demo wideo** (`testy/demo_wideo.py`, ok. 40 s, 1280 × 720) i plansza klatek — poza repo.

## Co działa (etap 1 — rdzeń, bez zmian w zasadach)

Scena (dół, obrzeże-trybuna, arena r 24 z pasami krawędzi, strefy x5 / x2 / x1 z napisami na podłodze obróconymi do
kamery gracza, fosa z gejzerami, drzewa, światło), kamera stała, rzut w wybrane miejsce (serwer sprawdza cel, limit 8,
jednego peta gracza, odpoczynek, tempo), walka na serwerze w 2D (odrzut = siła × (1 + 2 × ubytek życia) / waga, tarcie,
krytyki, RING OUT do fosy i gejzer, KO), 12 petów z 12 umiejętnościami (9 rodzajów), złoto co sekundę według strefy,
król środka z koroną i nagrodą za głowę, dzikie pety (boty) dopełniające arenę do 5. Szczegóły liczb niżej.

## Sterowanie

| Co | Telefon | Komputer | Pad |
|---|---|---|---|
| Rzut | stuknięcie w arenę | klik (podgląd celu pod myszą) | gałka — celownik, A |
| Umiejętność | ABILITY | spacja / Q | X |
| Wybór peta | karta po lewej | 1 / 2 / 3 | LB / RB |
| Jajka / Pety / Trening | EGGS / PETS / TRAIN | E / P / T | w górę / Y / w dół |
| Zamknij okno | X | X | B |

## Liczby (propozycja do strojenia — wszystkie w `ustawienia.json`)

| Co | Wartość |
|---|---|
| Arena / strefy | r 24; złoty środek r 5,5 (×5), pierścień r 13 (×2), reszta (×1) |
| Klasy wagi (lekki / średni / ciężki) | waga 0,7 / 1,0 / 1,5; życie 100 / 120 / 150; cios 4,5 / 5,2 / 6; odrzut 12 / 14 / 16; prędkość 9 / 7,5 / 6; wysokość 8,8 / 9,6 / 10,5 st |
| Stopień (rzadkość 1–5) | życie +20 %, cios +15 %, odrzut +6 % na stopień |
| Gwiazdki / trener | +8 % życia i siły na gwiazdkę (do 5); +3 % na poziom trenera |
| Złoto na minutę (pet stopnia 1) | środek **300**, ×2 **120**, ×1 **60**; Rare (stopień 3): 900 / 360 / 180 |
| Premie | wybicie 15 × stopień (dziki 10 × stopień); nagroda za głowę 10 + 3/s; złoty pet 6 × stopień za cios, 150 za wybicie; boss pula 400 (min. 80) |
| Jajka | 360 / 2000 / 8000 G; szanse (C/U/R/E/L): 58/30/11/1/0 · 20/42/30/7,5/0,5 · 0/28/42/25/5 % |
| Odpoczynek / arena / tempo akcji | 30 s / najwyżej 8 petów, dzikie do 5 / wiadro 3/s, zapas 4 |

**Tempo jajek** (`tempo.py`, 2000 przebiegów, samotny gracz, model przybliżony): pierwsze jajko darmowe od razu,
pierwsze kupione — mediana **1,5 min** (pomaga złoty pet w 1,5 min), pierwszy Rare — mediana **6,8 min** (65 % graczy
do 10 min), pierwszy Epic — **29 % do 30 min** (mediana później; model nie liczy gwiazdek ani trenera — do strojenia po
graniu). Symulacja walki (logika): pet żyje średnio ok. 17 s, pierwsze wybicie na arenie po ok. 10 s; gracz z
Common-ami zarabia ok. 150–190 G/min (odpoczynek 30 s: czekanie bez peta 2–30 s na 4 min zamiast ok. 95 s przy 60 s).

## Jak zbudować i zagrać

```
python -B swiat/pet_arena/dane.py                    # po zmianie ustawień: zrodla/DanePetArena.luau
python -B swiat/pet_arena/testy/test_pet_arena.py    # testy bez Studio (--tabela: symulacja walki)
python -B swiat/pet_arena/tempo.py                   # rachunek tempa jajek (Monte Carlo)
python -B swiat/pet_arena/zbuduj.py --sucho          # plan i kontrola Luau bez Studio
python -B swiat/pet_arena/zbuduj.py                  # budowa w otwartym miejscu PetArena (ok. 3 s; --studio <id>)
python -B swiat/pet_arena/zbuduj.py --skrypty        # po zmianie samego kodu
python -B swiat/pet_arena/zbuduj.py --stan | --usun | --wlacz on|off
python -B swiat/pet_arena/testy/proba_play.py <folder poza repo> [--studio <id>]   # próba w Play (P00–P27)
python -B swiat/pet_arena/testy/demo_wideo.py <plik.mp4 poza repo>                  # film demo ok. 40 s + plansza
```

Zagrać: otworzyć plik miejsca `PetArena.rbxlx` w Studio, **Play** (F5) — gracz staje na obrzeżu z petem w dłoni,
stuka / klika w arenę. Budowa odmawia w miejscu obecnej gry B&C, działa tylko w trybie Edit i we własnym kontenerze.

## Publikacja jako prywatna wersja testowa — kroki dla ludzi (decyzja ludzi, agent nie publikuje)

1. W Studio: **File → New** (puste miejsce, Baseplate) i zapis jako osobne doświadczenie (**File → Publish to Roblox As…
   → Create new experience**, nazwa robocza „Pet Arena”, prywatne).
2. W terminalu: `python -B swiat/pet_arena/zbuduj.py --publikacja --studio <id tego okna>` (skrypty bez strażnika
   Studio, wszystko inne jak w pliku lokalnym), potem w Studio **File → Publish to Roblox**.
3. Na stronie doświadczenia (Creator Hub): **Access → Private**, dodać testera (Paweł / znajomi), włączyć **Enable
   Studio Access to API Services** tylko jeśli chcemy zapis w wersji testowej (bez tego gra działa w pamięci).
4. Ikona i miniatury: na wzór `swiat/bonk/grafika/` (osobne zlecenie). Po teście — wrażenia do `B&C/Wytwórnia/Lekcje z prototypów.md`.

## Struktura

| Plik | Co |
|---|---|
| `ustawienia.json` | jedyne źródło liczb: scena, strefy, kamera, walka, rzut, złoto, nagroda, umiejętność, odpoczynek, boty, gracz, gwiazdki, jajka, tarcza, trener, wydarzenia, boss, złoty pet, zapis, tablice, pokazanie, klasy wagi, rzadkości, 12 petów, teksty, dźwięki |
| `dane.py` | generator `zrodla/DanePetArena.luau`, wzorców (12 petów, 3 jajka, 2 bossowie) i części sceny (612: arena, fosa, ściana, obrzeże, trybuna, miejsca, maty, cokoły jajek, drzewa, łąka); rzut kamery na ekran (test kadru) |
| `tempo.py` | rachunek tempa jajek (pierwsze jajko, pierwszy Rare, pierwszy Epic) |
| `zbuduj.py` | budowa w Studio: kontener, moduły i skrypty, sygnały, scena, wzorce, stanowisko jajek, tablice wyników, napisy stref, SpawnLocation, Lighting; `--skrypty`, `--stan`, `--usun`, `--wlacz`, `--publikacja` |
| `zrodla/LogikaPetArena.luau` | czyste rachunki (też w testach bez Studio): walka, umiejętności, król, złoto, boty, tarcza, boss, złoty pet, jajka, kolekcja i gwiazdki, trener, profil v2, zapis z podanym magazynem, tablice |
| `zrodla/SerwerPetArena.server.luau` | serwer: gracze, rzuty, umiejętności, jajka, drużyna, trening, wydarzenia, nagrody, zapis, tablice, komunikaty, migawki, haczyki prób |
| `zrodla/KlientPetArena.client.luau` | klient: widoki petów i bossa, loty, RING OUT / KO, korona, napisy, słowa, soczystość, ręce awatarów, kamera, wejście (dotyk, mysz, klawiatura, pad), haczyki prób |
| `zrodla/InterfejsPetArena.luau`, `zrodla/OknaPetArena.luau`, `zrodla/EfektyPetArena.luau` | ekran (rogi), okna (EGGS, PETS / INDEX, wyklucie), efekty w świecie |
| `testy/test_pet_arena.py`, `testy/proba_play.py`, `testy/demo_wideo.py` | testy bez Studio, próba w Play, film demo |
| `klatki/` | zrzuty z próby („Player 1”, bez nazwy konta i listy graczy) |

W Studio (`Workspace/PetArenaGra`, atrybut `Wygenerowane`): `Scena/{Arena, Fosa, Sciana, Obrzeze, Trybuna, Sloty, Maty,
Jajka, Drzewa, Teren}`, `Stanowisko/Jajko1–3`, `Tablice/Tablica1–3`, `Wzorce/{Pet_<id>, Jajko_<model>, Boss_<model>}`
(w grze serwer przenosi je do `ReplicatedStorage/PetArenaWzorce`), `Start` (SpawnLocation), `Moduly/*`, `SerwerPetArena`,
`KlientPetArena`, `Sygnaly/{Akcja, Zdarzenia, Stan, SterowanieSerwera, SterowanieKlienta}`. Atrybuty kontenera:
`PetArenaWlaczony`, `Skrot`, w grze `SerwerGotowy`, `WzorceGotowe`, `ZapisStan`, `ZapisMagazyn`, `PA_WydTyp`, `PA_WydT`.

**Sieć:** od klienta tylko `Sygnaly/Akcja (rodzaj, a, b, c)`: `"rzut", nr, x, z` · `"umiejetnosc"` · `"wybierz", nr` ·
`"jajko", nr` · `"druzyna", { id, … }` · `"trening", bool` — serwer sprawdza typ rodzaju i argumentów, wiadro tempa,
cel, limit areny, jednego peta gracza, odpoczynek, złoto (darmowe tylko pierwsze jajko), przerwę między jajkami,
posiadanie petów w drużynie. Do klientów: `Sygnaly/Stan` (UnreliableRemoteEvent, bufor 14 + 24 bajty na peta co
0,066 s: id, pet / boss, właściciel, faza, flagi stanów, x, z, życie, pasek, złoto/s, kierunek, gwiazdki, tarcza / boss /
złoty) i `Sygnaly/Zdarzenia` (`rzut`, `ladowanie`, `cios`, `umiejetnosc`, `ladowanie_skoku`, `odbicie`, `odbicie_slime`,
`ringout`, `ko`, `krol`, `krol_stracil`, `zloto`, `zloto_cios`, `boss`, `boss_fala`, `boss_uciekl`, `zloty`,
`zloty_uciekl`, `wyklucie`, `poziom`, `ogloszenie`, `odmowa`). Stan gracza w atrybutach `PA_*` (tylko serwer): `PA_Slot`,
`PA_Nazwa`, `PA_Zloto`, `PA_GS`, `PA_Pet`, `PA_Rzucil`, `PA_Wybicia`, `PA_Druzyna` („id:gwiazdki,…”), `PA_Odpoczynek`,
`PA_Kolekcja`, `PA_Ksiega`, `PA_Wybrany`, `PA_NaArenie`, `PA_Poziom`, `PA_Xp`, `PA_XpPotrzeba`, `PA_Samouczek`,
`PA_Trening`, `PA_Najlepszy`, `PA_ProfilGotowy`.

## Próby w Studio

`python -B swiat/pet_arena/testy/proba_play.py <folder poza repo>` — **28/28 OK** (21.11.2026 ok. 22:27, okno Studio na
wierzchu przy nocnym zaciemnieniu ekranu). Testy bez Studio: **28 OK** (dane i kadr kamery na 4 ekranach, logika etapu
1, tarcza słabszego, boss, złoty pet, jajka i gwiazdki, trener, zapis z atrapą magazynu — wczytanie z ponowieniem, brak
zapisu bez wczytania, tam i z powrotem, migracja v1 — tablice i wydarzenia, źródła, `zbuduj.py --sucho`).

| Punkt | Wynik |
|---|---|
| P00–P02 | budowa zgodna (612 części, 17 wzorców); „Player 1”, zapis „wyłączony (próba gry)”; kamera: arena 0,13–0,82 × 0,17–0,83 (okno i telefon); awatar w kadrze; dźwięki 18/18 |
| P03 pierwszy rzut | **3,4 s** od wejścia, pet z dłoni ląduje i walczy |
| P04 odrzut | ten sam cios: **21 przy pełnym życiu, 45 przy 25 %** |
| P05–P07, P10, P11 | RING OUT (karta RESTING 28s), KO +20, złoto 5 / 2 / 1 G/s, król i nagroda +42, drugi pet sam wybrany |
| P08 umiejętności | HEADBUTT przyciskiem, GROUND SLAM, SKY DIVE |
| P09, P12 | dzikie pety (5 w 7 s, umiejętności), limit 8 (ARENA FULL!), 26 z 30 akcji odrzuconych |
| P14 czas klatki, 8 petów | **16,7 ms (60 kl./s)**, najwyżej 21–25 ms; pętla klienta 0,9–1,3 ms; krok serwera 0,012 ms |
| P17 jajka | okno EGGS (przyciski ≥ 74 pt), darmowe pierwsze jajko (złoto 0 → 0), scena wyklucia NEW PET! / +1 STAR!, zakup za 360, odmowa NOT ENOUGH GOLD |
| P18 gwiazdki | ★★★ nad petem, życie 116 zamiast 100, siła × 1,16 |
| P19 drużyna i Księga | okno PETS — Wisp dotknięciem do miejsca 1, zakładka INDEX |
| P20 boss | odliczanie „BOSS IN 0:11”, pasek MIRE GUARDIAN, udział w obrażeniach, po pokonaniu **+407 złota** |
| P21 złoty pet | 3 ciosy = złoto, +188 (z premią) |
| P22 tarcza | Slime przy Forest Trollu chroniony, ikona 🛡 |
| P23 trener | mata (awatar na macie, doświadczenie rośnie), LV 2 na ekranie i nad głową |
| P24 zapis | w próbie gracz w pamięci, bez zapisu i bez błędów |
| P25 pad | Y → PETS z zaznaczonym przyciskiem, B zamyka, w górę → EGGS |
| P26 tablet 1024 × 768 | ekran i okno EGGS w ekranie, przyciski ≥ 44 pt |
| P27 tablice | TOP GOLD/S i KNOCKOUTS z „Player 1” |
| P13 telefon 667 × 375 w bitce | wszystko w ekranie, bez nakładania, najmniejszy przycisk 46 pt, **pety 68–81 pt** |
| P15, P16 | konsola bez błędów pakietu; Studio w Edit, miejsce zapisane (save_place) |

Zrzuty (`klatki/`, „Player 1”, bez nazwy konta i listy graczy): `pa_wejscie`, `pa_rzut`, `pa_ring_out`, `pa_ko`,
`pa_krol`, `pa_umiejetnosc_troll`, `pa_umiejetnosc_toad`, `pa_arena`, `pa_osiem_petow`, `pa_wyklucie`, `pa_okno_pety`,
`pa_ksiega`, `pa_boss`, `pa_boss_nagroda`, `pa_zloty`, `pa_trening`, `pa_telefon` (ekran telefonu w środku bitki).
Film demo (38 s, 1280 × 720) i plansza klatek — poza repo (`testy/demo_wideo.py`).

## Ograniczenia i znane problemy

- Pety są duże, więc przy 7–8 petach środek areny robi się ciasny (to cena czytelności na telefonie); dzikie pety
  dopełniają arenę tylko do 5.
- Zapis sprawdzony testem z atrapą magazynu; w pliku lokalnym w Play działa w pamięci (znacznik próby). Prawdziwy
  magazyn — dopiero w opublikowanej wersji testowej.
- Tempo jajek to model (`tempo.py`), nie pomiar — po pierwszym graniu do poprawy.
- Gracz nie chodzi (sterowanie wyłączone, kamera stała); trening przenosi awatara na matę obok miejsca.
- Napisy nad petami i graczami są na warstwie 2D (BillboardGui nie wychodzą w zrzutach z Play).
- Brak muzyki; dźwięki — odcinki arkusza efektów z BONK.

## Co dalej (propozycja)

Granie ludzi (Karol rano): czy po 10 min dalej wrzucają, czy czekają z umiejętnością, ile razy się śmieją, czy pytają
„co wypadnie z jajka”. Potem: strojenie odpoczynku i cen, osobne areny albo serwery według stopnia, codzienna nagroda,
nowy pet co tydzień, wydarzenie o stałej godzinie, ikona i miniatury, prywatna publikacja.
