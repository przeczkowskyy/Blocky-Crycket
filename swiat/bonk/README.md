# BONK — prosta gra z naszych zasobów (etap 1: rdzeń)

> **Status: propozycja (prototyp, D-112).** Projekt gry: `B&C/Gra/BONK — projekt prototypu.md`. Wszystkie liczby
> to propozycja do pomiaru. Każdy skrypt i moduł zaczyna się od strażnika `RunService:IsStudio()` (poza Studio serwer
> usuwa kontener); wersja bez strażnika: `zbuduj.py --publikacja` (tylko do pustego miejsca).

*Uderzasz potwory, a one odlatują daleko; rośnie Moc, otwierasz kolejne krainy.* Etap 1 to rdzeń: od wejścia do
pokonywania potworów w trzech krainach. Etap 2 (jajka i pety z Księgą, sklep pałek, Strażnicy, tablice i komunikaty,
dzienny prezent) i etap 3 (dopracowanie, telefon i pad, ikona, próba całości) — niżej, „Jak rozszerzać”.

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
| **Moc** | `floor(Moc z uderzeń × mnożnik pałki × mnożnik petów)` — mnożniki z atrybutów gracza `BonkMnoznikPalki`, `BonkMnoznikPetow` (dziś 1) |
| **Krainy** | las, Bagno, Dżungla z map pasów (`swiat/*_pas/krotki/czesci.json`), przesunięte o `przesuniecie` daleko od obecnej gry (obszar sprawdzony odczytem: pusty). Potwory w skali 1,35 modelu walki, najbliższe (do 10) z komiksowym obrysem. W każdej 4 zagrody (strefy z `znaczniki.json`): 5 + 5 + 4 potwory i 2 w leżu; rzadki potwór (2,5% przy odrodzeniu: złoty, większy, „RARE”, życie ×8, Moc ×5, monety ×10); odrodzenie 2–4 s; potwory stoją, bujają się i robią małe kroki |
| **Bramy** | niewidzialna ściana z napisem „NEED 2.4K POWER” na granicy krain; gracz z Mocą ma u siebie otwartą ścianę i wrota mapy (`BramaBagna/Wrota`…); serwer cofa każdego, kto jest dalej niż otwarte krainy. Brama Dżungli: „COMING SOON” |
| **Interfejs** (angielski, D-045) | POWER i COINS na górze, przycisk BONK, trzy podpowiedzi (do potwora → BONK → Moc otwiera bramę), nazwa krainy przy wejściu; skala z okna (wzór 667 × 375) |
| **Zapis** | magazyn `BONK_Gracz_v1` (w Studio `…_Studio`), klucz `g_<UserId>`, profil w wersji 1 (Moc, monety, BONK-i, najdalszy lot, HOME RUN-y, rzadkie, otwarte krainy, kraina, samouczek, pałka, pety, Strażnicy); wczytanie przy wejściu (3 próby; bez wczytania nie zapisujemy), zapis przy wyjściu, co 3 min, przy wyjściu portalem i przy zamknięciu serwera |
| **Próby** | `tools/zapis_prob.py` stawia znacznik próby także na `Workspace/BonkGra`: serwer BONK nie otwiera wtedy magazynu (gracz w pamięci); z `ZapisProbaMagazyn = true` — osobny magazyn `BONK_Gracz_v1_Studio_Proba` |
| **Dźwięk** | odcinki arkusza efektów (cios, BONK, krytyk = HOME RUN, monety, plusk = lądowanie, fanfara = otwarta brama), muzyka lasu (A w lesie, B w Bagnie i Dżungli — własne utwory tych krain nie mają praw gry) |

## Liczby i tempo

`ustawienia.json` — jedyne źródło liczb. Rachunek tempa bez Studio: `python -B swiat/bonk/tempo.py`.

| Kraina | Zagrody (życie / Moc za BONK / monety) | Brama |
|---|---|---|
| THE FOREST | Slime 1/1/1 · Shroomling 30/2/2 · Thorn Wolf 90/4/4 · Forest Troll 270/8/10 | 2.4K Power |
| THE SWAMP | Croaker 800/16/20 · Bubbler 2.4K/32/40 · Log Snapper 7.2K/64/80 · Hut Toad 22K/128/170 | 55K Power |
| THE JUNGLE | Curltail 65K/256/350 · Chomp Flower 200K/512/700 · Coconut Brute 600K/1024/1.4K · Ruin Armadillo 1.8M/2048/3K | 650K (COMING SOON) |

Gracz bez dodatków (3,5 uderzenia/s, 1,5 s na dojście, wybiera najlepszą zagrodę): **pierwszy BONK po ok. 5 s,
brama lasu po 9,2 min, Bagna po 22,4 min, Dżungli po 40,9 min** (cele: ≤ 30 s, 8–10, 20–25, ok. 40). Kolejne zagrody:
życie ×3, Moc ×2 — opłaca się iść dalej, gdy poprzednie bije się kilkoma ciosami. Duże liczby: `1.2K`, `3.4M`, `5.6B`
(kropka, bo tekst po angielsku).

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
| `ustawienia.json` | liczby: krainy i zagrody, gatunki, potwory, rzadki, BONK, Moc, lot, zapis, portal, widok, interfejs, dźwięki, model tempa |
| `dane.py` | generator `zrodla/DaneBonk.luau` (położenia w świecie BONK z `znaczniki.json` pasów, wymiary modeli, odcinki dźwięków) i wzorców (bryły z `swiat/test_walki2/dane/<gatunek>.json` w pozie spoczynku) |
| `tempo.py` | rachunek tempa (bez Studio) |
| `zbuduj.py` | budowa w Studio: kontener, moduły i skrypty, sygnały, mapa (paczki po 400 części), wzorce, bramy, portale; `--teren`, `--stan`, `--usun`, `--publikacja` |
| `zrodla/LogikaBonk.luau` | czyste rachunki (liczby, Moc, bramy, wiadro tempa, wędrówka, wybór celu, lot, nagrody, magazyn, profil) — wykonywane też w testach bez Studio |
| `zrodla/SerwerBonk.server.luau` | serwer: potwory, BONK, nagrody, bramy, portale, zapis, haczyki prób |
| `zrodla/KlientBonk.client.luau` | klient: widoki potworów, loty, wejście, cudze ekrany, bramy u gracza, muzyka, haczyki prób |
| `zrodla/EfektyBonk.luau`, `zrodla/InterfejsBonk.luau` | efekty w świecie (napisy, iskry, monety, plusk, ślad) i ekran |
| `testy/test_bonk.py`, `testy/proba_play.py` | testy bez Studio (26) i próba w Play (B00–B16; `--bez-okna` — bez wysuwania okna Studio) |

W Studio (`Workspace/BonkGra`, atrybut `Wygenerowane`): `Mapa/{Las,Bagno,Dzungla}`, `Wzorce/<gatunek>` (w grze
serwer przenosi je do `ReplicatedStorage/BonkWzorce`), `Bramy/Brama1–3`, `Portal` (przy płycie startu), `Powrot`
(EXIT), `Moduly/*`, `SerwerBonk`, `KlientBonk`, `Sygnaly/{Bonk, Zdarzenia, SterowanieSerwera, SterowanieKlienta}`;
w grze `Stan/Potwory/<id>` (Configuration: Gatunek, Kraina, Zagroda, Hp, HpMax, Zywy, Rzadki, Nr, Od, Cel, T0, Pr,
Promien). Atrybuty kontenera: `BonkWlaczony`, `AutoStart`, `PortalPoz`, `PortalWyjscie`, `PowrotPoz`, `Skrot`,
w grze `SerwerGotowy`, `KlientGotowy` (u klienta), `WzorceGotowe`, `ZapisStan`, `ZapisMagazyn`, liczniki zapisu.

**Sieć:** od klienta tylko `Sygnaly/Bonk` (bez argumentów; serwer sam wybiera cel). Do klientów `Sygnaly/Zdarzenia`:
`{ t = "cios", id, nr, ile, hp, g }` i `{ t = "lot", id, nr, g, ile, od, ko, wys, czas, hr, rz, monety, moc, brama? }`.
Stan gracza w atrybutach gracza: `BonkAktywny`, `BonkMoc`, `BonkMocBaza`, `BonkMonety`, `BonkOdblokowane`,
`BonkKraina`, `BonkBonki`, `BonkNajdalej`, `BonkSamouczek`, `BonkProfilGotowy`, `BonkMnoznikPalki`, `BonkMnoznikPetow`.

## Jak rozszerzać (etap 2)

- **Pałki:** ustaw atrybut gracza `BonkMnoznikPalki` (serwer sam przelicza Moc — `przelicz()`); stopień pałki
  w profilu: `profil.palka`. Model w dłoni: `swiat/postacie/bronie.py` (8 broni) — dołóż wzorce jak potworów.
- **Pety:** `BonkMnoznikPetow` (iloczyn mnożników petów za graczem), profil: `profil.pety` (tabela — format do
  ustalenia; `L.profil` przepuszcza tabelę bez zmian). Inkubatory: punkty `inkubator` w `znaczniki.json` Bagna i
  Dżungli (las — do wyznaczenia).
- **Strażnik:** dane areny są już w `DaneBonk.krainy[i].straznik` (`miejsce`, `arena`, `r`). Brama:
  `L.mozePrzejsc(nr, moc, D, profil)` — dopisz warunek `profil.straznicy[nr]` (profil już ma tabelę `straznicy`).
- **Sklep, tablice, komunikaty, dzienny prezent:** monety są w `profil.monety` / `BonkMonety`; najdalszy lot
  `BonkNajdalej`, liczba BONK `BonkBonki` (tablice). Nowe remotes przez wiadro `L.wiadro` jak BONK.
- **Wersja profilu:** podnieś `zapis.wersja_profilu` i dopisz migrację w `L.profil` (dziś: zła wartość = domyślna).

## Próba w Studio (19.11.2026, noc)

`python -B swiat/bonk/testy/proba_play.py <folder poza repo>` — **17/17 OK** (szósta próba; wcześniejsze znalazły
i poprawiły: wejście w trakcie wyboru klasy, rekord magazynu próby z poprzedniej próby, kolejność próby bramy).

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

- Brak zamachu ręką awatara (jest tylko łuk zamachu przed graczem) i pałki w dłoni (etap 2).
- `AutoStart` w obecnym miejscu: najpierw wybór klasy obecnej gry (dwa Entery), dopiero potem BONK.
- Pętla klienta kosztuje ok. 1,6 ms na klatkę przy pełnej zagrodzie (16 potworów, 4,3 tys. brył; komputer z próby) —
  na słabym telefonie do sprawdzenia; następny krok to odczyt atrybutów potworów z pamięci zamiast co klatkę.
- Wzorce potworów są statyczne (bez klipów szkieletu): ruch to bujanie, obrót i kroki — tanio na telefonie.
- Liczby tempa z modelu, nie z graczy (pomiar D1 i czasu gry — `B&C/Gra/BONK — projekt prototypu.md`).
