# BONK — prosta gra z naszych zasobów (etap 1: rdzeń, etap 2: pałki, pety, Strażnicy)

> **Status: propozycja (prototyp, D-112).** Projekt gry: `B&C/Gra/BONK — projekt prototypu.md`. Wszystkie liczby
> to propozycja do pomiaru. Każdy skrypt i moduł zaczyna się od strażnika `RunService:IsStudio()` (poza Studio serwer
> usuwa kontener); wersja bez strażnika: `zbuduj.py --publikacja` (tylko do pustego miejsca).

*Uderzasz potwory, a one odlatują daleko; rośnie Moc, otwierasz kolejne krainy.* Etap 1 to rdzeń: od wejścia do
pokonywania potworów w trzech krainach. Etap 2 (noc 19/20.11.2026) dokłada drugą warstwę pętli: pałki za monety,
jajka i pety z Księgą, Strażników bitych wspólnie, pokazanie się (Moc nad głową, korona, tablice, komunikaty) i dzienny
prezent. Etap 3 (dopracowanie, zamach ręką, dźwięki, pad, ikona) — niżej, „Co zostaje na etap 3”.

## Co działa (etap 2)

| Część | Jak |
|---|---|
| **Pałki** | 8 stopni z `swiat/postacie/bronie.py` (Nail Club ×1,5 … Master Ladle ×15), kupowane po kolei za monety (stopień n wymaga n−1). Stoisko CLUB SHOP przy starcie każdej krainy (lada, daszek, szyld, wystawiona pałka); przy stoisku przycisk OPEN SHOP → okno 4 × 2 kart (podgląd modelu, mnożnik, BUY z ceną / OWNED / EQUIPPED / LOCKED). Zakup sprawdza serwer (odległość od stoiska, kolejność, monety, wiadro akcji). Najlepsza kupiona pałka w prawej dłoni (bryły z wzorca przyspawane do RightGripAttachment na serwerze — widzą wszyscy). Bez Robuxów |
| **Jajka** | inkubator w każdej krainie w miejscu „jajko” mapy pasa (las 27,3; 20 — to samo kamienne stanowisko co w próbie petów; Bagno i Dżungla — punkty inkubatora): jajko z brył na cokole, tablica z ceną i **jawnymi szansami** (D-015). **Stała cena** w monetach (D-105): 800 / 20K / 300K; tylko za monety z gry (D-086). Przy inkubatorze przycisk HATCH z ceną, nad nim lista szans (pet, rzadkość, %) |
| **Wyklucie** | jajko przed kamerą trzęsie się coraz mocniej (dźwięk), pęka błyskiem w kolorze rzadkości, pet wyskakuje i rośnie, napis **NEW PET!** albo **DUPLICATE x2** (kopie się liczą), nazwa i rzadkość w jej kolorze; legendarny — komunikat na cały serwer. Los z serwera (`Random`), przerwa 3,2 s między jajkami |
| **Pety** | 15 (po 5 na krainę, modele z `swiat/postacie`, nazwy angielskie: Acornling, Moss Snail, Leaf Fox, Glow Owl, Crystal Fawn; Cattail Kid, Lily Turtle, Dragonfly, Wisp, Pearl Otter; Pineapple Pal, Sleepy Sloth, Toucan Chick, Ruin Idol, Jaguar Cub), rzadkości Common 50% · Uncommon 25% · Rare 15% · Epic 8% · Legendary 2%. Do 3 idzie za graczem (wachlarz za plecami, podskoki w biegu) — rysuje **każdy klient dla wszystkich graczy** z atrybutu `BonkPety`, tylko do 140 st od kamery. Domyślnie AUTO BEST (najlepsze 3, kopie też); okno PETS: klik zakłada / zdejmuje kopię (pełne — zastępuje najsłabszego), przycisk AUTO BEST |
| **Mnożnik petów** | `BonkMnoznikPetow = 1 + suma premii aktywnych` (liniowo, najwyżej 3 pety — nie wybucha jak iloczyn; najwyżej 1 + 3 × 9 = 28 w Dżungli). Premie: las 0,1 / 0,2 / 0,35 / 0,6 / 1; Bagno ×3; Dżungla ×9 (rosną z rzadkością i krainą) |
| **Księga petów** | okno INDEX: 3 rzędy (jajka) po 5, odkryte w kolorze z nazwą, nieodkryte jako **czarne sylwetki** „???” (ViewportFrame z `ImageColor3` czarnym), pasek koloru rzadkości, licznik „7/15” w tytule |
| **Strażnicy** | GROVE GUARDIAN (las), MIRE GUARDIAN (Bagno), VINE SERPENT (Dżungla) — modele z `swiat/test_walki2/dane` w skali 1,35, na arenach map (`straznik.miejsce`). Bije każdy w zasięgu tym samym BONK (serwer wybiera najbliższy cel); **wspólny pasek życia u góry ekranu** dla każdego w promieniu 75 st (nazwa, `1.2M / 3M`, po pokonaniu „back in 42s”). Po pokonaniu wielki lot w niebo z błyskiem; nagroda dla każdego, kto trafił: monety i Moc × max(udział w obrażeniach, 25%); komunikat na cały serwer; odrodzenie po 60–90 s |
| **Brama** | wymaga Mocy **i** pokonania Strażnika krainy raz (`profil.straznicy[nr] > 0`, `L.mozePrzejsc`); przy Mocy bez Strażnika napis bramy „BEAT THE GUARDIAN!”, serwer cofa. Otwartej bramy się nie zamyka (gracz z etapu 1 zachowuje Bagno). Brama Dżungli dalej COMING SOON |
| **Pokazanie się** | Moc nad głową każdego gracza (warstwa ekranu, do 90 st), **korona** z brył (serwer, przyspawana do głowy — widzą wszyscy) dla najsilniejszego na serwerze, `leaderstats` → Power, trzy tablice przy starcie lasu: TOP POWER, FARTHEST BONK, PET INDEX (8 wierszy, odświeżane co 4 s), komunikaty: legendarny pet, Strażnik pokonany, nowa kraina. **W próbie** (znacznik próby) zamiast nazw „Player 1”, „Player 2” na tablicach i w komunikatach |
| **Dzienny prezent** | przycisk GIFT (czerwona kropka, gdy czeka), okno 7 dni (dzień serii podświetlony, kwoty), CLAIM; raz na dzień UTC; nagroda 200 / 400 / 700 / 1K / 1,5K / 2,2K / 3K × mnożnik krainy (1 / 20 / 300 wg najdalszej otwartej); **opuszczony dzień nie zeruje serii** (tylko pauza; napis „Missed a day? Your streak stays!”) |
| **Zapis v2** | profil w wersji 2 (pałka, pety z kopiami, aktywne, AUTO, Księga, Strażnicy, prezent, liczba jajek) z migracją z v1 w `L.profil` (postęp zostaje, nowe pola od zera; pałka z v1 = brak). Bez wczytania nie zapisujemy (jak w etapie 1) |

## Co działa (etap 1)

| Część | Jak |
|---|---|
| **Wejście** | brama „BONK” przy płycie startu obecnej gry (we własnym kontenerze, pierwsze wolne miejsce 16–24 st od płyty) albo atrybut kontenera `AutoStart = true` (gracz po wejściu do gry od razu w BONK — próby i przyszła publikacja). Brama „EXIT” na starcie lasu wraca do bramy BONK |
| **Własny awatar** | serwer daje graczowi w BONK atrybut `BezBohatera = true` — bohater klasy (`swiat/bohater_swiat`) się nie rysuje, awatar widać |
| **Cudze ekrany** | klient chowa u siebie każdy ScreenGui wprost w PlayerGui (HUD, ekrany pasów, wskazówki…: `Enabled = false`, pilnowane) i przywraca je po wyjściu. Własne ekrany leżą w `PlayerGui/BonkUI` (`BonkEkran`, `BonkNapisy`), bo ekran wyboru klasy wyłącza każdy nowy ScreenGui dodany wprost do PlayerGui. **Wybór klasy obecnej gry** (przy `AutoStart` w obecnym miejscu, gracz bez zapisu): BONK czeka, aż gracz go skończy (ekran trzyma kamerę i swoje nocne światło sali) — potem kamera wraca do postaci i rusza ekran BONK; ekranu wyboru nie przywracamy po wyjściu, gdy klasa jest już wybrana. W osobnym miejscu (publikacja) wyboru klasy nie ma |
| **BONK** | przycisk (telefon: duży, prawy dolny róg nad skokiem; komputer: mniejszy z „E”), klik, E, pad X / R2; trzymanie = BONK co 0,22 s. Serwer wybiera najbliższego żywego potwora w zasięgu (8 st od brzegu modelu), obrażenia = Moc, limit 5 uderzeń/s (wiadro z zapasem 2). Pierścień pod celem w zasięgu |
| **Lot** | ostatni cios: serwer liczy łuk (kierunek od gracza ± 18°, odległość 15 + 18·log₂(1 + Moc/życie), najwyżej 260 st), klienci rysują lot z obrotem i śladem, „BONK! / POW! / WHAM!…”, lądowanie „SPLAT!” z kręgiem (napisy, liczby obrażeń, paski życia i „RARE” rysuje warstwa ekranu `BonkNapisy` rzutem ze świata — BillboardGui tworzone u klienta nie wychodzą w zrzutach z Play); od 120 st — **HOME RUN!** (napis na ekranie, dźwięk krytyka, monety ×2) |
| **Trafienie bez zabicia** | drgnięcie, pasek życia nad potworem (3 s), liczba obrażeń |
| **Nagrody** | monety wylatują i same lecą do gracza (serwer dopisuje od razu), BONK daje Moc („+2” przy liczbie) |
| **Moc** | `floor(Moc z uderzeń × mnożnik pałki × mnożnik petów)` — mnożniki liczy serwer z profilu i wystawia w atrybutach gracza `BonkMnoznikPalki`, `BonkMnoznikPetow` (etap 2) |
| **Krainy** | las, Bagno, Dżungla z map pasów (`swiat/*_pas/krotki/czesci.json`), przesunięte o `przesuniecie` daleko od obecnej gry (obszar sprawdzony odczytem: pusty). Potwory w skali 1,35 modelu walki, najbliższe (do 10) z komiksowym obrysem. W każdej 4 zagrody (strefy z `znaczniki.json`): 5 + 5 + 4 potwory i 2 w leżu; rzadki potwór (2,5% przy odrodzeniu: złoty, większy, „RARE”, życie ×8, Moc ×5, monety ×10); odrodzenie 2–4 s; potwory stoją, bujają się i robią małe kroki |
| **Bramy** | niewidzialna ściana z napisem „NEED 4.5K POWER” na granicy krain; gracz z Mocą (i od etapu 2 pokonanym Strażnikiem) ma u siebie otwartą ścianę i wrota mapy (`BramaBagna/Wrota`…); serwer cofa każdego, kto jest dalej niż otwarte krainy. Brama Dżungli: „COMING SOON” |
| **Interfejs** (angielski, D-045) | POWER i COINS na górze, przycisk BONK, trzy podpowiedzi (do potwora → BONK → Moc otwiera bramę), nazwa krainy przy wejściu; skala z okna (wzór 667 × 375) |
| **Zapis** | magazyn `BONK_Gracz_v1` (w Studio `…_Studio`), klucz `g_<UserId>`, profil (Moc, monety, BONK-i, najdalszy lot, HOME RUN-y, rzadkie, otwarte krainy, kraina, samouczek; od etapu 2 wersja 2 z pałką, petami, Księgą, Strażnikami i prezentem — wyżej); wczytanie przy wejściu (3 próby; bez wczytania nie zapisujemy), zapis przy wyjściu, co 3 min, przy wyjściu portalem i przy zamknięciu serwera |
| **Próby** | `tools/zapis_prob.py` stawia znacznik próby także na `Workspace/BonkGra`: serwer BONK nie otwiera wtedy magazynu (gracz w pamięci); z `ZapisProbaMagazyn = true` — osobny magazyn `BONK_Gracz_v1_Studio_Proba` |
| **Dźwięk** | odcinki arkusza efektów (cios, BONK, krytyk = HOME RUN, monety, plusk = lądowanie, fanfara = otwarta brama), muzyka lasu (A w lesie, B w Bagnie i Dżungli — własne utwory tych krain nie mają praw gry) |

## Liczby i tempo

`ustawienia.json` — jedyne źródło liczb. Rachunek tempa bez Studio: `python -B swiat/bonk/tempo.py`.

| Kraina | Zagrody (życie / Moc za BONK / monety) | Strażnik (życie / Moc / monety) | Jajko | Brama |
|---|---|---|---|---|
| THE FOREST | Slime 1/1/1 · Shroomling 30/2/2 · Thorn Wolf 90/4/4 · Forest Troll 270/8/10 | GROVE GUARDIAN 810K / 300 / 3K | 800 | 4.5K Power + Strażnik |
| THE SWAMP | Croaker 800/16/20 · Bubbler 2.4K/32/40 · Log Snapper 7.2K/64/80 · Hut Toad 22K/128/170 | MIRE GUARDIAN 108M / 8K / 60K | 20K | 600K Power + Strażnik |
| THE JUNGLE | Curltail 65K/256/350 · Chomp Flower 200K/512/700 · Coconut Brute 600K/1024/1.4K · Ruin Armadillo 1.8M/2048/3K | VINE SERPENT 900M / 80K / 900K | 300K | 5M (COMING SOON) |

Pałki (cena → mnożnik): Nail Club 500 → ×1,5 · Frying Pan 1,5K → ×2 · War Hammer 9K → ×3 · Great Axe 40K → ×4 ·
Banner Spear 150K → ×6 · Flame Sword 600K → ×8 · Ice Staff 2,5M → ×11 · Master Ladle 10M → ×15.

**Tempo (etap 2, `python -B swiat/bonk/tempo.py`):** gracz 3,5 uderzenia/s, 1,5 s na dojście, najlepsza zagroda,
kupuje to (następną pałkę albo jajko krainy), co daje największy przyrost mnożnika na monetę; wyklucia „średnim
szczęściem” (kolejność rzadkości wg szans); przy Mocy bramy bije Strażnika sam. Wynik: **pierwszy BONK 5 s, pierwsza
pałka 2,1 min, pierwsze jajko 4,2 min, Strażnik lasu i brama Bagna 9,5 min, Strażnik Bagna i brama Dżungli 23,8 min**
(cele: ≤ 30 s, 2–4, 3–5, 9–11, 23–27 — w celach). Samotny gracz z Mocą bramy bije Strażnika **51 s** w modelu
(3,5/s; trzymany BONK 4,5/s — ok. 40 s; cel 45–60 s). Bez dodatków (`--bez-dodatkow`, jak etap 1) brama lasu dopiero
po ok. 16 min — pałki i pety są odczuwalne. Bramy podniesione względem etapu 1 (2,4K → 4,5K, 55K → 600K), bo mnożniki
przyspieszają grę. Kolejne zagrody: życie ×3, Moc ×2. Duże liczby: `1.2K`, `3.4M`, `5.6B` (kropka, tekst po angielsku).

## Jak zbudować, wejść, wyłączyć, usunąć

```
python -B swiat/bonk/dane.py                 # po zmianie ustawień: zrodla/DaneBonk.luau
python -B swiat/bonk/testy/test_bonk.py      # testy bez Studio
python -B swiat/bonk/zbuduj.py --sucho       # plan i kontrola Luau bez Studio
python -B swiat/bonk/zbuduj.py --teren       # odczyt: czy obszar mapy BONK jest pusty (przed pierwszą budową)
python -B swiat/bonk/zbuduj.py               # budowa (mapa ok. 15 tys. części tylko za pierwszym razem; --mapa = od nowa)
python -B swiat/bonk/zbuduj.py --skrypty     # po zmianie samego kodu (szybko)
python -B swiat/bonk/zbuduj.py --autostart on|off
python -B swiat/bonk/zbuduj.py --wlacz off   # wyłącznik: serwer i klient BONK nic nie robią (on — z powrotem)
python -B swiat/bonk/zbuduj.py --usun        # usuwa Workspace/BonkGra (przed publikacją obecnej gry)
python -B swiat/bonk/testy/proba_play.py <folder poza repo>   # próba w Play (Play wyłącznie przez tools/studio_mcp.py)
```

W grze: przejdź przez bramę BONK obok płyty startu (albo `AutoStart`). Wyjście: brama EXIT na starcie lasu.
Publikacja jako osobna gra (D-044, decyzja ludzi): puste miejsce, `zbuduj.py --publikacja --studio <id>` (bez
strażnika Studio, bez bramy przy starcie obecnej gry, `AutoStart = true`).

## Struktura

| Plik | Co |
|---|---|
| `ustawienia.json` | liczby: krainy i zagrody, gatunki, potwory, rzadki, **pałki, rzadkości, jajka i pety, Strażnicy, pokazanie się, prezent, akcje**, BONK, Moc, lot, zapis, portal, widok, interfejs, dźwięki, model tempa |
| `dane.py` | generator `zrodla/DaneBonk.luau` (położenia w świecie BONK z `znaczniki.json` pasów, wymiary modeli, odcinki dźwięków) i wzorców: potwory i Strażnicy (bryły z `swiat/test_walki2/dane/<gatunek>.json`), pety i jajka (rig z klocków `swiat/postacie/<id>.py` przez `roblox_klocki.rig`, poza spoczynku), pałki (`swiat/postacie/bronie.py`, bryły w układzie RightGripAttachment) — wszystko tylko odczytem |
| `tempo.py` | rachunek tempa (bez Studio): zakupy pałek i jajek, wyklucia „średnim szczęściem”, Strażnicy, bramy |
| `zbuduj.py` | budowa w Studio: kontener, moduły i skrypty, sygnały, mapa (paczki po 400 części), wzorce (41), bramy, portale, **stanowiska** (inkubatory z tablicą szans, stoiska pałek, trzy tablice); `--teren`, `--stan`, `--usun`, `--publikacja` |
| `zrodla/LogikaBonk.luau` | czyste rachunki (liczby, Moc, bramy ze Strażnikiem, wiadro tempa, wędrówka, wybór celu, lot, nagrody, magazyn, profil v2 z migracją, pałki, losowanie i wyklucie, najlepsze pety, mnożnik petów, Księga, nagroda Strażnika, prezent) — wykonywane też w testach bez Studio |
| `zrodla/SerwerBonk.server.luau` | serwer: potwory i Strażnicy, BONK, nagrody, bramy, portale, zapis, akcje (sklep, jajko, pety, prezent), pałka w dłoni, korona, leaderstats, tablice, komunikaty, haczyki prób |
| `zrodla/KlientBonk.client.luau` | klient: widoki potworów i Strażników, loty (Strażnik w niebo), wejście, cudze ekrany, bramy u gracza, muzyka, wyklucie przed kamerą, pety za graczami, Moc nad głowami, strefy stoiska i inkubatora, haczyki prób |
| `zrodla/EfektyBonk.luau`, `zrodla/InterfejsBonk.luau`, `zrodla/OknaBonk.luau` | efekty w świecie (napisy, iskry, monety, plusk, ślad), ekran (Moc, monety, BONK) i okna etapu 2 (przyciski boczne, przycisk przy stoisku / inkubatorze z szansami, sklep, pety, Księga, prezent, komunikat, dymek, pasek Strażnika, napisy wyklucia) |
| `testy/test_bonk.py`, `testy/proba_play.py` | testy bez Studio (34) i próba w Play (B00–B27; `--bez-okna` — bez wysuwania okna Studio) |

W Studio (`Workspace/BonkGra`, atrybut `Wygenerowane`): `Mapa/{Las,Bagno,Dzungla}`, `Wzorce/<gatunek | Pet_<id> |
Jajko_<n> | Palka_<n>>` (w grze serwer przenosi je do `ReplicatedStorage/BonkWzorce`), `Bramy/Brama1–3`,
`Stanowiska/{Inkubator1–3, Sklep1–3, Tablica1–3}`, `Portal` (przy płycie startu), `Powrot` (EXIT), `Moduly/*`,
`SerwerBonk`, `KlientBonk`, `Sygnaly/{Bonk, Zdarzenia, Akcja, SterowanieSerwera, SterowanieKlienta}`; w grze
`Stan/Potwory/<id>` (Configuration: Gatunek, Kraina, Zagroda, Hp, HpMax, Zywy, Rzadki, Nr, Od, Cel, T0, Pr, Promien;
Strażnik: `straznik_<nr>` z `Straznik = nr` i `Powrot` — czas serwera odrodzenia). Atrybuty kontenera: `BonkWlaczony`,
`AutoStart`, `PortalPoz`, `PortalWyjscie`, `PowrotPoz`, `Skrot`, w grze `SerwerGotowy`, `KlientGotowy` (u klienta),
`WzorceGotowe`, `ZapisStan`, `ZapisMagazyn`, liczniki zapisu. W postaci gracza (serwer): `BonkPalka`, `BonkKorona`.

**Sieć:** od klienta `Sygnaly/Bonk` (bez argumentów; serwer sam wybiera cel — potwora albo Strażnika) i
`Sygnaly/Akcja (rodzaj, arg)`: `"palka", nr` · `"jajko", nr krainy` · `"pety", { id, … }` · `"auto", bool` ·
`"prezent"` — serwer sprawdza znany rodzaj, typy, odległość od stoiska / inkubatora, monety, kolejność pałek, przerwę
między jajkami i wiadro akcji (4/s, zapas 4). Do klientów `Sygnaly/Zdarzenia`: `cios`, `lot` (Strażnik: `niebo = true`),
`wyklucie {jajko, pet, nowy, kopie, rzadkosc}`, `kupiono {nr}`, `odmowa {powod}`, `prezent {monety, dzien}`,
`nagroda_straznika {monety, moc, nazwa, udzial}`, `ogloszenie {tekst, kolor}`. Stan gracza w atrybutach gracza
(ustawia tylko serwer): `BonkAktywny`, `BonkMoc`, `BonkMocBaza`, `BonkMonety`, `BonkOdblokowane`, `BonkKraina`,
`BonkBonki`, `BonkNajdalej`, `BonkSamouczek`, `BonkProfilGotowy`, `BonkMnoznikPalki`, `BonkMnoznikPetow`, `BonkPalka`,
`BonkPety` („id,id,id” — aktywne, rysują je wszyscy klienci), `BonkPetyMam` („id:kopie,…”), `BonkKsiega`,
`BonkAutoPety`, `BonkStraznicy` („1,0,0”), `BonkPrezentMozna`, `BonkPrezentNagroda`, `BonkPrezentDzien`, `BonkKorona`.

## Jak rozszerzać

- **Nowa pałka / jajko / pet / Strażnik:** wpis w `ustawienia.json` (`palki.lista`, `jajka[].pety` i `premie`,
  `straznicy`), potem `dane.py` i `zbuduj.py` (pełna budowa — nowe wzorce i stanowiska). Model peta: moduł
  `swiat/postacie/<id>.py`; pałki: `swiat/postacie/bronie.py`.
- **Profil v2:** `profil.palka` (0–8), `pety = { [id] = kopie }`, `aktywne = { id, … }`, `autoPety`, `ksiega = { [id] =
  true }`, `straznicy = { n1, n2, n3 }` (gęsta lista), `prezent = { dzien, seria }`, `jajek`. Nowe pole: podnieś
  `zapis.wersja_profilu` i dopisz migrację w `L.profil` (wzór: gałąź `wersja < 2`).
- **Nowa akcja gracza:** dopisz rodzaj do `AKCJE` w serwerze i gałąź w `evAkcja` (wiadro akcji jest wspólne).

## Próba w Studio (etap 2: noc 19/20.11.2026)

`python -B swiat/bonk/testy/proba_play.py <folder poza repo>` — **27/27 OK** (trzecia próba etapu 2; wcześniejsze
znalazły i poprawiły: tablice szukane w złym folderze, wyklucie przed kamerą zasłaniane przez świat — teraz scena
w ViewportFrame na środku ekranu, komunikat nachodzący na pasek Strażnika, kolejność tablic; w próbie: dojście do
pierwszego slime'a ścieżką przez furtkę polany, odczyt napisu bramy po odświeżeniu u klienta). Testy bez Studio: **34 OK**.

| Punkt (etap 2) | Wynik |
|---|---|
| B17 sklep pałek | przy stoisku przycisk OPEN SHOP, okno 8 kart z podglądami; zakup nie po kolei i bez monet — odmowa serwera; Nail Club: monety 600 → 100, mnożnik ×1,5, **pałka w prawej dłoni** (27 części, widzą wszyscy) |
| B18 jajko | przy inkubatorze HATCH 800 i szanse nad przyciskiem; wyklucie: scena (trzęsienie → błysk → pet, „NEW PET!”, „Acornling · Common”), drugie jajko po 0,3 s odrzucone (przerwa), po 3 jajkach **3 pety idą za graczem** (w promieniu 9 st), mnożnik petów ×1,3 |
| B19 Księga i pety | INDEX: 15 miejsc (15 podglądów, nieodkryte jako sylwetki), licznik „1/15”; okno PETS: wybór ręczny → aktywny 1 pet, AUTO wyłączone; AUTO BEST → najlepsze 3 |
| B21a brama bez Strażnika | przy Mocy bramy napis „BEAT THE GUARDIAN!”, Bagno zamknięte, serwer cofa |
| B20 Strażnik lasu | sam gracz z Mocą bramy (4,5K), trzymany BONK: **42,0 s** od pierwszego ciosu do lotu (pasek „805K / 810K” u góry), lot w niebo, nagroda +3K monet i +300 Mocy, komunikat „Player 1 defeated the GROVE GUARDIAN!”, odrodzenie za 60–90 s („back in 64s”) |
| B21 brama | po Strażniku przejście do Bagna, komunikat „Player 1 unlocked THE SWAMP!” |
| B22 pokazanie się | tablice „1. Player 1 — 5K / 0 studs / 1/15”, **korona** na głowie, `leaderstats.Power` = Moc, Moc nad głową („5K POWER”) |
| B23 prezent | kropka na GIFT, CLAIM +4K (200 × 20 — otwarte Bagno), drugi raz tego dnia — odmowa, po dwóch opuszczonych dniach seria 2 (+8K) — **bez kary** |
| B27 czas klatki | 3 pety za graczem + Strażnik (1128 brył) + zagroda, okno Studio na wierzchu: **śr. 16,7 ms (60 kl./s), najwyżej 19,1 ms**; pętla BONK śr. 1,35 ms, najwyżej 2,7 ms |
| B24 zapis v2 | rekord w magazynie próby: `v = 2`, pałka, pety z kopiami, Strażnicy — ponowne wczytanie zgodne; rekord w formacie v1 → profil v2 (Moc 3000, monety 900 zostają; pałka 0, Strażnicy 0, prezent od nowa; pałka znika z dłoni) |
| B25 telefon | emulacja 667 × 375: okna sklepu, petów, Księgi i prezentu mieszczą się w ekranie; przyciski PETS / INDEX / GIFT i przycisk przy stoisku nie nachodzą na BONK |

Punkty etapu 1 w tej samej próbie: B00 (7 źródeł, 41 wzorców, 9 stanowisk), B01 (51 potworów: 48 + 3 Strażników),
B02–B16 jak niżej; B03 pierwszy BONK 4,7 s od pokazania się ekranu, B11 pełna zagroda lasu z 3 petami 16,7 ms /
pętla 1,9 ms. Zrzuty etapu 2 (`klatki/`, bez nazwy konta i listy graczy, „Player 1” zamiast nazw): `bonk_sklep.jpg`,
`bonk_palka.jpg`, `bonk_wyklucie_trzesie.jpg`, `bonk_wyklucie.jpg`, `bonk_pety.jpg`, `bonk_ksiega.jpg`,
`bonk_okno_petow.jpg`, `bonk_straznik.jpg`, `bonk_straznik_lot.jpg`, `bonk_tablice.jpg`, `bonk_prezent.jpg`,
`bonk_telefon_sklep.jpg`.

## Próba w Studio (etap 1: 19.11.2026, noc)

17/17 OK (szósta próba; wcześniejsze znalazły i poprawiły: wejście w trakcie wyboru klasy, rekord magazynu próby
z poprzedniej próby, kolejność próby bramy).

| Punkt | Wynik |
|---|---|
| B00 Edit | kontener zgodny z repo: 6 źródeł, mapa 14 907 części, 12 wzorców, 3 bramy, brama BONK 16 st od płyty startu (Workspace.SpawnLocation), brama EXIT |
| B01 serwer | 48 potworów (16 w każdej krainie); zapis: `włączony (magazyn próby)` → `BONK_Gracz_v1_Studio_Proba` (prawdziwy klucz nietknięty; bez `ZapisProbaMagazyn`: `wyłączony (próba gry)`) |
| B02 wejście | `AutoStart`: po wyborze klasy gracz w lesie, kamera na postaci, ekran BONK, 12 cudzych ekranów schowanych (HUD, ekrany pasów, wskazówki, pety…), awatar widoczny (16/16 części), bohater klasy się nie rysuje (`BezBohatera`); muzyka BONK gra, **muzyka obecnej gry nie gra** (żaden inny dźwięk) |
| B03 pierwszy BONK | 4,0 s od pokazania się ekranu BONK (2,7 s dojścia i trzymanego BONK) — gracz biega i bije od razu |
| B04 lot i monety | lot u klienta, monety i Moc rosną, dźwięki grają, podpowiedź 3 |
| B05 odradzanie | zagroda pełna po ≤ 2,4 s |
| B06 trafienie | wilk 80/90 po ciosie Mocy 10 |
| B07 limit tempa | 30 BONK naraz od klienta → przyjęte 2, odrzucone 28 |
| B08 HOME RUN | lot 260 st, licznik HOME RUN-ów |
| B09 brama | bez Mocy serwer cofa za bramę; z Mocą przejście do Bagna, napis THE SWAMP, muzyka lasu B |
| B10 trzy krainy | widoki: las 12 (2460 brył), Bagno 14 (1813), Dżungla 14 (1928) |
| B11 czas klatki | pełna zagroda lasu (16 potworów, 4332 bryły + mapa 14 907 części), okno Studio na wierzchu: **śr. 16,7 ms (60 kl./s, limit Studio), najwyżej 19–20 ms**; pętla BONK śr. 1,6 ms, najwyżej 2,6–4,3 ms. Mapy nie trzeba odchudzać |
| B12 zapis | zapis do magazynu próby, odczyt (wersja 1), ponowne wczytanie — zgodne |
| B13 portale | EXIT: ekran BONK znika, 12 cudzych ekranów wraca, gracz przy bramie BONK; ponowne wejście bramą BONK |
| B14 telefon | emulacja 667 × 375: przycisk 104 × 104 w prawym dolnym rogu (nad skokiem), POWER i COINS czytelne |
| B15 konsola | bez błędów pakietu |
| B16 | Studio w trybie Edit, `AutoStart` przywrócony (`false`) |

Zrzuty: `klatki/bonk_lot.jpg`, `bonk_home_run.jpg`, `bonk_las.jpg`, `bonk_bagno.jpg`, `bonk_dzungla.jpg`,
`bonk_telefon.jpg` (bez nazwy konta i listy graczy).

## Czego jeszcze nie ma i ograniczenia

- Brak zamachu ręką awatara (jest tylko łuk zamachu przed graczem); pałka trzymana w dłoni sztywno (w pozie ręki
  awatara celuje do przodu, jak Tool).
- Pety i jajka to statyczne wzorce (poza spoczynku, bez klipów `chod` / `radosc` z próby petów): ruch to podskoki
  w biegu, obrót i lekkie bujanie. Pety latające (Dragonfly, Wisp) też podskakują po ziemi.
- Strażnicy stoją w miejscu i nie oddają ciosów (to „worek do bicia” dla całego serwera) — atak Strażnika, fazy
  i zasięg areny zostają na później. Nagroda: każdy, kto trafił choćby raz, dostaje co najmniej 25%.
- Tablice to SurfaceGui na częściach z Edit (serwer wpisuje wiersze) — widać je w zrzutach z Play. Dzień prezentu liczy
  się w UTC (`os.time()`), nie w strefie gracza.
- Księga liczy odkryte pety; kopie nie mają jeszcze innego użytku niż drugi i trzeci aktywny pet tego samego rodzaju
  (brak łączenia kopii w lepszą wersję).
- `AutoStart` w obecnym miejscu: najpierw wybór klasy obecnej gry (dwa Entery), dopiero potem BONK.
- Pętla klienta kosztuje ok. 1,7 ms na klatkę przy pełnej zagrodzie z 3 petami (komputer z próby) — na słabym
  telefonie do sprawdzenia; następny krok to odczyt atrybutów potworów z pamięci zamiast co klatkę.
- Liczby tempa z modelu, nie z graczy (pomiar D1 i czasu gry — `B&C/Gra/BONK — projekt prototypu.md`).

## Co zostaje na etap 3

- Zamach ręką awatara przy BONK (klip ramienia z pałką), klipy petów (`chod`, `radosc`, `wyklucie`) i jajka
  (`trzesienie`, `pekniecie`) z rigów próby petów zamiast statycznych wzorców.
- Dopracowanie: atak Strażnika i jego okno „sprint” dla grupy, dźwięki BONK, pęknięcia jajka i Strażnika z własnych
  nagrań (Higgsfield — etap 3), ikona gry i miniatura, pad (przyciski okien na krzyżaku), próba na prawdziwym telefonie.
- Ekonomia z graczy: D1, czas do pierwszej pałki / jajka / Strażnika (strojenie liczb w `ustawienia.json`).
