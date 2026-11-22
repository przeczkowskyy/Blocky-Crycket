# Smok ewolucji — modele, klipy i dane dla gry (styl „Żarołuska”)

> **Status: propozycja.** Nic stąd nie jest jeszcze wpięte w grę — `swiat/ewolucja/smok.py` i kod gry są nietknięte.
> Niczego nie wgrano do Roblox. **W Studio nikt jeszcze tego smoka nie zbudował ani nie odtworzył**: dane mają układ,
> który biblioteka postaci sprawdziła wcześniej w Studio (`swiat/postacie/roblox_postac.py`), a klipy sprawdza poza
> Studio `sprawdz_dane.py` (odtwarza je tak, jak zrobi to gra) — to nie jest próba w Studio.

Osiem stadiów jednego smoka (HATCHLING … ANCIENT DRAGON) z jednego parametrycznego modułu, 23 klipy na stadium,
wersja uproszczona każdego stadium, jajo, rekwizyty legowiska, owca, mini-boss KNIGHT GOLEM, obrazy strony gry.

## Wersja danych 2 (runda 2, 22.11.2026) — co się zmieniło względem wersji 1
- **Stawy: 26 zamiast 21.** Każda noga ma trzeci staw stopy (`NogaPL3`, `NogaPP3`, `NogaTL3`, `NogaTP3`), doszedł
  staw `Powieki` (mruganie maluchów). Kolejność: `indeks.json` → `stawy`.
- **Zaczepy: 13 zamiast 7** — doszły miejsca na światło i cząsteczki żaru: `GardloAttachment`, `PiersAttachment`,
  `Zar1Attachment`, `Zar2Attachment`, `Zar3Attachment` (wzdłuż grzbietu), `ZarOgonAttachment`.
- **Regiony: 9 zamiast 8** — doszedł `zar_rdzen` (jasny rdzeń żaru; region `zar` to miękka zewnętrzna poświata).
- Nowe pliki: `<id>_lod_rig.json` (wersja uproszczona), `rekwizyt_<id>_rig.json`, `owca_*`, `golem_<1–5>_*`.
- Klipy `chod` i `bieg` mają pole `predkosc` (studs/s, przy której stopy się nie ślizgają).
- Pola `format` kończą się na `/2`, `indeks.json` ma `"wersja": 2`.

## Jedno polecenie
```
python -B swiat/ewolucja/modele/generuj.py wszystko     # dane + podglądy + obrazy + siatki + eksport (ok. 3–4 min)
python -B swiat/ewolucja/modele/sprawdz_dane.py          # sprawdzian danych bez Studio
python -B swiat/ewolucja/modele/generuj.py filmy         # filmy stadiów 1, 3, 5, 8 (ok. 10 min)
```
Części: `dane` · `rekwizyty` · `stwory` · `swiat` · `golem_grozny` · `styl` · `podglady` · `obrazy` · `mapa` · `siatki` · `eksport [id…]` · `licz`;
robocze: `przeglad [nr…]`, `paski <nr> [klipy…]`. Blender 5.0 startuje w tle pod wspólną blokadą biblioteki.
Duże pliki trafiają POZA repozytorium: `%LOCALAPPDATA%\BlockyCrycket\modele\smok_ewolucja\` (`obrazy`, `filmy`,
`eksport`, `siatki`, `podglady` i foldery robocze).

| Plik | Co to jest |
|---|---|
| `smok_model.py` | dane stadiów (`STADIA`), palety, `zbuduj_stadium(nr)`, `zbuduj_stadium_lod(nr)`, jajo |
| `smok_klipy.py` | klipy `dodaj_klipy(p)`; nogi sadzone na ziemi odwrotną kinematyką (`_posadz`), zdarzenia |
| `rekwizyty.py` | skarb w trzech rozmiarach, cokół trofeum, gniazdo z jajami (i ogień do obrazów) |
| `stwory.py` | owca (ofiara maluchów), KNIGHT GOLEM w pięciu stopniach |
| `obrazy_gry.py` | ikona i trzy miniatury strony gry (sceny z Blendera, tło i klockowy napis z PIL) |
| `generuj.py`, `sprawdz_dane.py`, `smoki.py` | polecenia, sprawdzian, moduł dla `podglad_postaci.py` biblioteki |
| `blender_widoki.py`, `blender_siatki.py` | skrypty uruchamiane w Blenderze |
| `dane/` | **przekazanie dla gry** (opis niżej) |
| `podglad/` | 20 małych JPG (17–19 mapa i zestaw świata, 20 groźny golem): styl, rzędy stadiów, przegląd z wersją uproszczoną, plansze 1/4/8, paski klatek, wyklucie, warianty i rekwizyty, ikona, trzy miniatury |

## Styl i regiony koloru
Klockowa bryła w kolorze ciała; od karku po ogon ciemne **łuski-dachówki**, w szczelinach **żar**: miękka poświata
i jasny rdzeń (Neon), z wiekiem coraz szerszy; rogi, kolce i pazury to **kryształowe ostrza**; skrzydło ma kości
palców i pola błony na przemian w dwóch odcieniach, lekko załamane. Region części = ostatnia liczba wiersza `czesci`:

`0 cialo` · `1 luski` (ciemny akcent) · `2 brzuch` · `3 blona` · `4 kolce` · `5 zar` · `6 oko` · `7 stale`
(zęby, język, skorupka — nie przemalowywać) · `8 zar_rdzen`.

Wariant albo linia żywiołu = podmiana kolorów regionów (słownik `WARIANTY` w `generuj.py`); materiał części zostaje.

## Jednostki i osie
- Jednostka = **stud**; model jest w skali gry: nos–zad = 2 × `promien_gry`. Początek układu = ziemia pod środkiem
  tułowia; `wymiary`: `przod` (nos), `tyl` (koniec ogona), `szer`, `wys`.
- `dane/` są w **układzie rigu Roblox**: przód **−Z**, lewa strona **−X**, Y w górę. Kąty części: radiany dla
  `CFrame.fromOrientation(rx, ry, rz)`; kąty w klipach: dziesiąte stopnia; przesunięcia w klipach: tysięczne studa.

## Rig: `<id>_rig.json` (pełny) i `<id>_lod_rig.json` (uproszczony, te same stawy, zaczepy i klipy)
- `hrp` — położenie części-korzenia. `kosci[i]` = `[nazwa, rodzic (0 = korzeń), staw x, y, z, środek x, y, z,
  rozmiar x, y, z, nazwa stawu]` (indeksy od 1). `czesci[j]` = `[kość, kształt, nazwa, px, py, pz, rx, ry, rz, sx, sy,
  sz, kolor, materiał, grupa, siatka, region]`; kształt: 0 Block, 1 Ball, 2 Cylinder, 3 Wedge, 4 CornerWedge.
  `materialy[k]` = `[materiał Roblox, Reflectance]`. `zaczepy` = `[nazwa, kość, x, y, z od środka części kości, rx, ry, rz]`.
- Budowa jak w budowniczym biblioteki: kość = niewidzialna część o `rozmiar` w `środek`; `Motor6D` w części-dziecku:
  `C0 = CFrame.new(staw − środek rodzica)`, `C1 = CFrame.new(staw − środek)`; widoczne części
  `CFrame.new(p) * CFrame.fromOrientation(r)` względem ziemi modelu, spięte `WeldConstraint` z częścią swojej kości.

**Stawy smoka (26):** `Tulow` · `Szyja1` > `Szyja2` > `Glowa` > `Szczeka`, `Glowa` > `Powieki` · `SkrzydloL1` >
`SkrzydloL2`, `SkrzydloP1` > `SkrzydloP2` · `Ogon1` > `Ogon2` > `Ogon3` > `Ogon4` · nogi `NogaPL`, `NogaPP` (przednie
lewa / prawa), `NogaTL`, `NogaTP` (tylne), każda `…1` (udo) > `…2` (podudzie) > `…3` (stopa). Jajo: `Dol` > `Gora`,
`OdlamekL`, `OdlamekP`.

| Stadium | części pełny | części uproszczony | siatek / trójkątów (ścieżka siatek) |
|---|---|---|---|
| smok_1 HATCHLING | 74 | 35 | 49 / 2252 |
| smok_2 WHELP | 74 | 35 | 49 / 2288 |
| smok_3 DRAKE | 86 | 35 | 57 / 2520 |
| smok_4 FIRE DRAKE | 87 | 35 | 60 / 2620 |
| smok_5 DRAGON | 90 | 35 | 57 / 2620 |
| smok_6 WAR DRAGON | 92 | 35 | 58 / 2784 |
| smok_7 ELDER DRAGON | 92 | 35 | 62 / 2696 |
| smok_8 ANCIENT DRAGON | 91 | 35 | 60 / 2744 |

Do tego 26 niewidzialnych części kości na smoka. Jajo 11 części. Aktualne liczby: `dane/indeks.json`.

## Klipy: `<id>_klipy.json`
`fps` 30, `krok` 2 (próbka co 2 klatki). Klip: `{"dl", "petla", "zdarzenia": {nazwa: klatka}, "predkosc" (tylko chód
i bieg), "stawy": [indeksy], "przes": [indeksy z przesunięciem], "probki": [[…], …]}`. Wiersz próbki idzie po `stawy`:
dla kości z `przes` najpierw `x, y, z`, potem zawsze `rx, ry, rz`. Próbka `i` = klatka `i × krok`.

```lua
local f = t * 30 / 2                                   -- t = czas klipu w sekundach
local a, u = math.floor(f), f % 1
local A, B = K.probki[a + 1], K.probki[math.min(a + 2, #K.probki)]
local o = 0
for _, i in K.stawy do
    local p = Vector3.zero
    if maPrzes[i] then
        p = Vector3.new(A[o+1] + (B[o+1]-A[o+1])*u, A[o+2] + (B[o+2]-A[o+2])*u, A[o+3] + (B[o+3]-A[o+3])*u) / 1000
        o += 3
    end
    local rx, ry, rz = A[o+1] + (B[o+1]-A[o+1])*u, A[o+2] + (B[o+2]-A[o+2])*u, A[o+3] + (B[o+3]-A[o+3])*u
    o += 3
    motor[i].C0 = C0[i] * CFrame.new(p) * CFrame.fromOrientation(math.rad(rx/10), math.rad(ry/10), math.rad(rz/10))
end
```
Interpolować LICZBY, nie CFrame (`ogon_zamach` i `koziolek` przechodzą przez 360°). Kości spoza `stawy` wracają do
`C0[i]`. Klipy są „w miejscu” — przesuw, wysokość lotu i obrót całości robi kod gry. Zmiana skali o `s`: pozycje,
rozmiary i przesunięcia × `s`, kąty bez zmian.

**Nogi na ziemi.** Klucze nóg liczy odwrotna kinematyka: w klipach naziemnych kostka stoi w miejscu mimo ruchu
tułowia, stopa zostaje płaska; w `chod` i `bieg` stopa w podporze jedzie w tył ze stałą prędkością. Żeby stopy nie
ślizgały się po mapie, grać klip z szybkością `prędkość smoka / predkosc` (po przeskalowaniu modelu `predkosc × s`).
Gdy cel jest poza zasięgiem nogi (skok, lot), noga przechodzi płynnie do pozy z klipu.

| Klip | Pętla | Co robi | Zdarzenia |
|---|---|---|---|
| `spoczynek` | tak | oddech, rozglądanie, ogon; maluchy mrugają (staw `Powieki`) | — |
| `chod`, `bieg` | tak | kłus po przekątnej; pisklę kica, dorosły galopuje | — |
| `gryz1`, `gryz2`, `gryz3` | nie | kłapnięcie w lewo / w prawo, wypad całym ciałem | `ugryzienie` |
| `ogien_start` → `ogien_petla` → `ogien_koniec` | nie / tak / nie | wdech, zionięcie, zamknięcie pyska | `ogien_start`, `ogien_stop` |
| `trafienie` | nie | wzdrygnięcie po ciosie | — |
| `wyklucie` | nie | zwinięty w jaju → wyskok → otrząśnięcie (jajo: klip `wyklucie` w `smok_jajo`) | `pekniecie` |
| `splun` | nie | splunięcie kulą ognia | `strzal` |
| `ogon_zamach` | nie | obrót ciała o 360° z ogonem | `uderzenie_start`, `uderzenie_stop` |
| `ryk` | nie | ryk z rozłożonymi skrzydłami | `ryk_start`, `ryk_stop` |
| `szybowanie_start` → `_petla` → `_ladowanie` | nie / tak / nie | odbicie, lot ślizgowy, lądowanie | `odbicie`, `ladowanie` |
| `nurkowanie_skok` → `nurkowanie_ladowanie` | nie | skok i pikowanie, uderzenie w ziemię | `odbicie`, `szczyt`, `uderzenie` |
| `koziolek` | nie | bezwładny koziołek po mocnym ciosie, wstaje | `upadek` |
| `pozarcie` | nie | finisher: chaps, podrzut głowy, przełknięcie | `ugryzienie`, `polkniecie` |
| `radosc` | nie | po ewolucji: wyskok, skrzydła, ryk radości | `szczyt` |
| `cokol` | tak | dumna poza na cokół trofeum | — |

Klatki zdarzeń różnią się między stadiami — czytać z `zdarzenia`; znaczenia: `indeks.json` → `zdarzenia`.
Jajo jest dopasowane do pisklęcia; dla innego stadium skalować × (`promien_gry` / 1,6) i rozciągnąć czas klipu.

## Rekwizyty, owca, KNIGHT GOLEM (te same formaty plików)
- `rekwizyt_skarb_1|2|3_rig.json` (14 / 25 / 45 części, zaczep `SzczytAttachment`), `rekwizyt_cokol_rig.json`
  (9 części, płyta 5 × 5, zaczep `TrofeumAttachment`), `rekwizyt_gniazdo_rig.json` (22 części). Jedna kość `Podstawa`.
- `owca_rig.json`, `owca_klipy.json` — 17 części; stawy `Tulow`, `Glowa`, `NogaPL`, `NogaPP`, `NogaTL`, `NogaTP`,
  `Ogonek`; klipy `spoczynek`, `chod`, `ucieczka`, `zjedzona` (zdarzenie `zjedzona`).
- `golem_<1–5>_rig.json`, `golem_<1–5>_klipy.json` — 33–42 części; stawy `Tulow`, `Klatka`, `Glowa`, `RekaL1/2`,
  `RekaP1/2`, `NogaL1/2`, `NogaP1/2`; zaczepy `SerceAttachment`, `MieczAttachment`, `GlowaAttachment`; klipy
  `spoczynek`, `chod`, `zamach`, `uderzenie` (zdarzenie `uderzenie` w obu), `zachwianie`, `upadek` (zdarzenie
  `upadek`). Stopień = paleta regionów + dodatki (kolce barków, tarcza, rogi, peleryna); każdy stopień jest o 8% większy.
- Spis: `indeks.json` → `rekwizyty`, `stwory`.

## Obrazy strony gry
`generuj.py obrazy` (po `dane`): `…\smok_ewolucja\obrazy\ikona_512.png`, `miniatura_1|2|3_1920x1080.png`,
`sprawdzian_150px.png`; podglądy `podglad/13–16`. Jedyny tekst: tytuł z własnych klockowych liter i „?”.

## Ścieżka siatek (na później — nic nie wgrano)
`generuj.py siatki` → `…\siatki\<id>_czesci.fbx|.glb`: jedna siatka na **staw i region**, nazwa
`<Staw>__<region>[_neon | _RRGGBB]`, jeden kolor i materiał, punkt obrotu w stawie, bez szkieletu; lista z trójkątami
w `indeks.json` → `siatki`. `generuj.py eksport` → `…\eksport\`: `<id>.fbx`, `<id>__<klip>.fbx`, `<id>.glb`,
`<id>.blend` (szkielet, siatka na staw, wszystkie klipy), każdy plik wczytany z powrotem i porównany.
**Import do Studio nie był testowany** (uwagi o kierunku FBX: `swiat/postacie/biblioteka/README.md`).

## Zestaw świata i propozycja mapy (runda 3 — tylko NOWE pliki, wersja danych 2 bez zmian)
Polecenia: `generuj.py swiat` (rigi zestawu), `generuj.py mapa` (mapa + rendery + plansza zestawu),
`generuj.py golem_grozny`. Istniejących plików smoków, jaja, owcy, golema i rekwizytów te polecenia nie dotykają;
`indeks.json` dostał tylko nowe klucze `swiat`, `mapa`, `stwory_grozne`. Kod: `swiat_zestaw.py`, `mapa.py`, `stwory_grozne.py`.

**Język:** te same fazowane klocki co smok, ciemna opaska-dachówka na pniach, głazach i filarach, żar (Neon) tylko tam,
gdzie coś jest gorące albo magiczne (lawa, ołtarz, brama, grzyby, runy), kryształowe ostrza jako akcent.
Każdy rekwizyt: `rekwizyt_<id>_rig.json`, jedna kość `Podstawa`, przód rekwizytu = −Z rigu. Części (limit):

| Strefa | id · części |
|---|---|
| Łąka (drobiazg ≤ 8, drzewa i skały ≤ 20) | `trawa_1` 3 · `trawa_2` 5 · `kwiat_czerwony`, `kwiat_zolty`, `kwiat_niebieski`, `kwiat_bialy` 5 · `kamyk` 2 · `glaz_1` 5 · `glaz_2` 7 · `krzak` 7 · `drzewo_1` 9 · `drzewo_2` 10 · `drzewo_3` 9 · `grzyb` 5 · `kloda` 7 · `drogowskaz` 7 · `sciana_skalna` 7 (odcinek obrzeża 24 studs) |
| Deep Woods | `sosna_1` 7 · `sosna_2` 8 · `grzyb_wielki` 11 · `grzyby_swiecace` 7 · `luk_korzeni` 14 · `filar_ruin` 8 · `krag_kamienny` 16 |
| Legowisko | `legowisko_krag` 26 (podkowa skał r 13, otwarta ku przodowi) · `legowisko_brama` 10 · `sztandar` 7 (płat w regionie `cialo` = kolor gracza) · `stos_zlota_1|2|3` 14 / 27 / 56 (kopiec monet i klejnotów; zastępuje wizualnie `skarb_*`) |
| Wyspa lawy | `bazalt_1` 6 · `bazalt_2` 8 · `skala_lawy` 7 · `oltarz_kul` 22 (zaczep `KulaAttachment`) |
| Woda | `lilia` 5 · `trzcina` 7 |
| Punkty charakterystyczne (≤ 80) | `czaszka_smoka` 33 · `posag_prastarego` 41 (z brył uproszczonego ANCIENT) · `brama_zapieczetowana` 30 |
| Kule | `kula_mala` 3 (żółta, bez pierścienia) · `kula_duza` 4 (błękitna, jeden złoty pierścień) · `kula_wielka` 8 (różowa, dwa pierścienie i kryształy) — promienie jak w grze: 0,6 / 1,15 / 1,6 |

Groźny golem: `golem_grozny_<1–5>_rig.json` + `_klipy.json` (55–62 części, te same stawy i klipy co `golem_<n>`).

**Mapa: `dane/mapa_propozycja.json`** — układ gry (środek łąki = (0, 0), DEEP WOODS w +Z, studs, obrót w stopniach wokół
pionu): `instancje` = `{id: [[x, z, obrót, skala], …]}`, `platy_ziemi` = `[x, z, promień, kolor, wysokość, świeci]`
(płaskie koła — tanie urozmaicenie ziemi), `szablon_legowiska` = `[id, w prawo, ku środkowi łąki, obrót]` do
powtórzenia w każdym legowisku gry (pozycje 12 legowisk w pliku są przykładowe: kąt 42°–318° od kierunku lasu).
Razem **3761 części statycznych**: łąka 1951, las 602, legowiska 516 (12 ×), woda 312, wyspa lawy 174, znaki 104,
płaty ziemi 102. Kule, cokoły, złoto i smoki są dynamiczne i nie wchodzą do tej liczby.

Gdzie co stoi (gęstości):
- **Łąka (koło 150):** 110 pojedynczych kępek + 16 kęp po 5; kwiaty w kwietnikach (4 kolory × 4 kwietniki × 6) — bogato
  w kępach, pusto pomiędzy; 20 kamyków, 8 głazów, 30 krzaków (20 w zewnętrznej jednej trzeciej), 10 drzew w środku
  i 22 za obrzeżem; 14 grzybów, 4 kłody, 3 drogowskazy (do lasu, do wyspy, do bramy); obrzeże: 31 odcinków
  `sciana_skalna` na promieniu 158 z przerwami na bramy; plac r 17 pośrodku, ścieżka z płatów do lasu i wzdłuż legowisk.
- **Woda:** dwa stawy (r 16 i r 11) po 6 lilii i 6 trzcin na brzegu; jezioro r 80 wokół wyspy (14 + 14).
- **Deep Woods (koło 115):** 26 sosen na obwodzie (nie zasłaniają wejścia od łąki), 8 w środku, 8 wielkich grzybów,
  20 kęp świecących grzybków, łuk z korzeni jako brama wejściowa (skala 1,3) + 3 w lesie, kamienny krąg i posąg
  Prastarego z ruinami filarów wokół.
- **Wyspa lawy (r 42):** 10 skupisk bazaltu na brzegu, 12 skał z żarem, ołtarz wielkich kul pośrodku; brzeg świeci.
- **Punkty charakterystyczne:** czaszka smoka na łące (widać ją z pierwszych kroków), zapieczętowana brama na obrzeżu
  naprzeciw wyspy, posąg w głębi lasu — każdy widoczny z daleka i stawia pytanie „co tam jest?”.

**Światło i niebo (propozycja dla agenta gry, liczby do `Lighting`):** późne popołudnie, ciepłe słońce i chłodny,
fioletowawy cień — żar i kryształy mają świecić na tle spokojnej zieleni.
- `ClockTime` 16,2 · `GeographicLatitude` 35 · `Technology` Future (ShadowMap na słabszych telefonach) ·
  `Brightness` 2,6 · `ExposureCompensation` 0,15 · `ShadowSoftness` 0,25 · `EnvironmentDiffuseScale` 0,6 ·
  `EnvironmentSpecularScale` 0,4.
- `Ambient` (30, 26, 44) · `OutdoorAmbient` (128, 118, 150) · `ColorShift_Top` (255, 226, 178).
- `Atmosphere`: `Density` 0,28 · `Offset` 0,15 · `Color` (255, 217, 176) · `Decay` (122, 90, 168) · `Glare` 0,25 ·
  `Haze` 1,6. Bez Atmosphere: `FogColor` (190, 200, 230), `FogStart` 250, `FogEnd` 900.
- Niebo: zwykłe z chmurami — `Clouds.Cover` 0,55, `Density` 0,3, `Color` (255, 238, 220); `SunAngularSize` 14, gwiazdy 0.
- Efekty: `Bloom` (`Intensity` 0,45, `Size` 28, `Threshold` 1,1 — to on robi żar), `ColorCorrection`
  (`Saturation` 0,12, `Contrast` 0,08, `TintColor` (255, 248, 236)), `SunRays` (`Intensity` 0,06, `Spread` 0,6).
- Nastrój stref (płynna zmiana po wejściu): las — `Atmosphere.Density` 0,42, `Color` (120, 150, 140), `Brightness` 1,9;
  wyspa lawy — `Color` (255, 150, 90), `Density` 0,35. `PointLight` tylko na znakach i w zaczepach żaru własnego smoka
  i bossa (zasięg ok. 8 × skala, jasność 0,8), najwyżej kilkanaście naraz.
- Woda: płaska część `Glass`, kolor 3E8FD8, przezroczystość 0,25, `Reflectance` 0,15.

Rendery mapy: `…\smok_ewolucja\mapa\mapa_z_gory.png`, `mapa_kamera_gry.png`; podglądy `podglad/17–19` (19 = cały zestaw).

## Interfejs: ikony, portrety, makiety i przewodnik stylu (runda 4)
`generuj.py interfejs` (kod: `interfejs.py`; tylko czyta `dane/` i render mapy, żadnego pliku danych nie zmienia).
Pełne pliki poza repozytorium, `…\smok_ewolucja\interfejs\`:
- `ikony\*.png` — 24 ikony 256 × 256, przezroczyste, sprawdzone w 64 i 44 px: `bite`, `dash`, linia OGNIA `ember_spit`,
  `fire_breath`, `inferno_breath`, linia MOCY `tail_sweep`, `wing_glide`, `roar`, `meteor_dive`, `zablokowane` (kłódka),
  `moneta`, `skarb`, `kula_mala`, `kula_duza`, `kula_wielka`, `wariant_gold`, `wariant_crystal`, `wariant_ruby`,
  `wariant_rainbow`, `korona`, `ulepszenie_jaw`, `ulepszenie_speed`, `ulepszenie_appetite`, `czaszka`.
- `portrety\stadium_<1–8>.png` i `stadium_<1–8>_sylwetka.png` — popiersia 256 × 256 i pasujące czarne sylwetki
  (drabina ewolucji, odsłona, panel legowiska).
- `makiety\hud_telefon_1280x590.png`, `panel_legowiska_1280x590.png`, `odslona_ewolucji_1280x590.png` — docelowy wygląd.
  Napisy w makietach to czcionka zastępcza z tego komputera (Arial Rounded, tytuły Cooper Black) — w grze czcionki Roblox.
Podglądy: `podglad/21_ikony.jpg`, `22_portrety.jpg`, `23_makieta_hud.jpg`, `24_makieta_legowisko.jpg`, `25_makieta_ewolucja.jpg`.

**Przewodnik stylu.** Punkt odniesienia: telefon poziomo 844 × 390 pt (makieta 1280 × 590 px, 1 pt ≈ 1,5 px).
- **Kolory:** panel `#2B2238` · karta / wypukłość `#3E3250` · pas tytułu i tło pasków `#1C162C` · obrys `#1A1424` ·
  tekst `#FFF6E0` · tekst pomocniczy `#BEB2D4` · żar (postęp, przycisk główny, aktywna zakładka) `#FF7A2A` z jasną
  górą `#FFD23F` · życie `#FF4D6A` / `#FF9AA8` · złoto `#FFC934` · kryształ (paski ulepszeń) `#7FF8FF` · kup / plus
  `#7CE38B`. Płytki przycisków: BITE `#FFF6E0`, DASH `#60C8DC`, linia OGNIA `#E84C2C`, linia MOCY `#3A80EA`,
  zablokowany `#463C58`.
- **Kształt:** panele — promień 16 pt, karty 11 pt, pigułki i paski w pełni zaokrąglone, przyciski akcji okrągłe.
  Obrys `#1A1424`: 3 pt na panelach i przyciskach, 2 pt na pigułkach i paskach (`UIStroke`); ikony mają własny obrys
  (ok. 2,7% boku). Cień: ciemna kopia kształtu przesunięta o 3 pt w dół (`#080410`, ok. 40%) — bez rozmycia też działa.
  Pod pasem tytułu panelu linia żaru 4 pt — to jest „żar w szczelinie” przeniesiony do interfejsu.
- **Czcionka (z dostępnych w Studio; do potwierdzenia przez agenta gry):** tytuły, nazwy stadiów i liczby —
  `FredokaOne` (zamienniki: `LuckiestGuy`, `Bangers`); etykiety i opisy — `GothamBold` / Montserrat Bold albo
  `BuilderSansExtraBold` (zamiennik: `Nunito` w grubym kroju). Zawsze jasny tekst z ciemnym obrysem 2 pt; rozmiary
  na telefonie: nazwa stadium 17 pt, liczniki 11 pt, pigułki 8–9 pt (nigdy mniej niż 8), podpisy przycisków 9 pt.
- **Stany przycisku:** zwykły — płytka w kolorze linii, obrys, wewnątrz jasny pierścień (biel 27%) i połysk u góry,
  ikona na 81% średnicy; wciśnięty — skala 0,92, płytka o 15% ciemniejsza, bez cienia, 0,08 s; odnowa — ciemny
  wycinek (`#100A1C`, 67%) kurczący się zgodnie z zegarem od godziny 12 i liczba sekund pośrodku, na koniec błysk
  pierścienia żaru 0,15 s; zablokowany — płytka `#463C58`, zamiast ikony kłódka, nad przyciskiem pigułka
  „<UMIEJĘTNOŚĆ> at <STADIUM>”.
- **Rozstaw na telefonie:** marginesy bezpieczne 24 pt z lewej i prawej, 10 pt u góry, 14 pt u dołu. Górne rogi puste
  (lewy zajmują przyciski Roblox, prawy bywa pod wcięciem ekranu) — pasek wzrostu 290 × 18 pt z portretem i nazwą na
  środku u góry, pod nim pasek życia, liczniki złota i skarbu tuż obok paska. Drabina ewolucji przy lewej krawędzi,
  w połowie wysokości: węzły 24 pt (obecne stadium 36 pt z pierścieniem żaru, następne jako sylwetka ze znakiem
  zapytania, dalsze jako kropki), odstęp 28 pt. Lewy dół (35% szerokości, 55% wysokości) zostaje dla drążka.
  Przyciski w prawym dolnym rogu: BITE 103 pt, pozostałe 68 pt (minimum 44 pt), odstęp co najmniej 10 pt, ułożone
  łukiem wokół BITE w zasięgu kciuka.

## Runda 5 — etap (`dane_nastepne/`): prędkość ruchu, krótki koziołek, ogień, indeks 3
`generuj.py etap` zapisuje zmienione i nowe pliki do **`dane_nastepne/`** pod tymi samymi nazwami i **nie dotyka `dane/`**
(agent gry czyta `dane/` przy każdej budowie). Po przeniesieniu plików przez sesję główną zwykłe `generuj.py dane`
da to samo. Do tego czasu **nie uruchamiać `dane` ani `wszystko`** — nadpisałyby `dane/` nowymi klipami.
`sprawdz_dane.py` czyta najpierw `dane_nastepne/`, potem `dane/`. Rigi smoków są bez zmian (porównane bajt w bajt).

- **Chód i bieg pod prędkość gry.** Każde stadium: `chod` = **7 studs/s**, `bieg` = **18 studs/s** (pole `predkosc`).
  Grać z szybkością `prędkość po ziemi / predkosc`: przy 16–26 studs/s bieg idzie w tempie 0,89–1,44. Maluchy kicają —
  przednie i tylne łapy po 2 klatki na ziemi, potem długi sus, a tułów zostaje nad stopami i nadrabia w locie
  (pisklę ±0,7 studa w przód i w tył względem korzenia: kamerę i pole trafienia trzymać na korzeniu, nie na tułowiu);
  średnie galopują, wielkie stawiają długie kroki. Sprawdzian liczy poślizg stopy w podporze: chód do 0,2, bieg do
  0,4 studs/s przy prędkości z `predkosc`. Cykle (klatki): chód 8, 8, 12, 12, 16, 18, 22, 30; bieg 10, 10, 12, 12, 16, 16, 20, 24.
- **`koziolek`** ma teraz 14 klatek (0,47 s, jeden obrót; `upadek` w klatce 12) — gra trzyma ostatnią pozę do 0,5 s.
  Dawny długi koziołek z wstawaniem to **`koziolek_dlugi`**.
- **`portret`** — poza na jedną klatkę (klip 2-klatkowy, obie takie same): głowa zwrócona w lewo-przód smoka, skrzydła
  półotwarte, pysk lekko uchylony; kamera z przodu po lewej stronie smoka (trzy czwarte).
- **Indeks w wersji 3:** `stadia` = tylko osiem stadiów (każde z polem `predkosc`), jajo pod kluczem `jajo`; nowe
  klucze `efekty`, `warianty_modeli`, `predkosc_stworow`. Format plików rigów i klipów bez zmian (`/2`).
- **`predkosc` u stworów:** owca `chod` 1,76 i `ucieczka` 5,0 studs/s; golem `chod` 6,5–8,5 (rośnie ze stopniem),
  groźny golem 6,9–9,1.
- **Stożek ognia** `ogien_stozek_rig.json` + `ogien_stozek_klipy.json` (28 części; stawy `Podstawa` > `Rdzen`,
  `Pierscien1`, `Pierscien2`, `Pierscien3`; zaczep `KoniecAttachment`; klip `migotanie`, pętla 12 klatek): wachlarz
  języków ognia ok. 60° z jasnym rdzeniem, początek układu w pysku, długość 10 studów wzdłuż przodu (−Z rigu) —
  przypiąć do `PyskAttachment`, skala = zasięg / 10 (kąt wachlarza stały). **Przypalenie** `rekwizyt_przypalenie_rig.json`
  (12 części, promień 10; skala = promień INFERNO / 10): krąg sadzy z żarem i świecącymi pęknięciami.
- **Łagodne pisklę** `smok_1_lagodny_rig.json`: mniejsze oczy (84%) i krótkie jasne brwi uniesione na zewnątrz; te same
  stawy, zaczepy i klipy co `smok_1` — do wyboru przez ludzi (`podglad/05_stadium_1.jpg`); wybrany plik podmienia rig.
- Film: `…\smok_ewolucja\filmy\smok_<1|3|8>_bieg_16_studs_krata.mp4` (bieg przy 16 studs/s nad kratą jadącą z prędkością
  gry); pasek klatek `podglad/26_bieg_16_studs.jpg`.

## Co jest słabe (uczciwie)
- Ruch (runda 5): kicanie maluchów jest zrywne (tułów staje nad łapami i skacze) — tak musi być przy 16–26 studs/s
  na łapach długości pół studa, ale to kwestia gustu; przy 26 studs/s (tempo 1,44) susy są bardzo szybkie.
  Uproszczone pisklę ma oczy wielkości starego wariantu. Stożek ognia to nadal klocki — z bliska kanciasty.
- Interfejs (runda 4): ikony `wing_glide`, `meteor_dive`, `czaszka` i `korona` są najmniej czytelne w 44 px; makiety są
  obrazami — układu nie sprawdzono na prawdziwym telefonie ani w Studio; nazwy czcionek Roblox podane z pamięci.
- Świat (runda 3): ziemia jest płaska — bez wzniesień i klifów w środku łąki; drobiazg z kamery gry nadal jest rzadki
  poza kępami (budżet 4000 części na koło o średnicy 300 studów); rekwizytów nie sprawdzono w Studio; kolizje
  i przeszkody dla logiki gry trzeba wskazać osobno. Groźny golem ma krótkie, schowane nogi.
- Stopy stoją na ziemi, ale poślizg w poprzek przy kołysaniu tułowia i obrót stóp w `ogon_zamach` zostają;
  w galopie nogi maluchów chwilami wiszą w powietrzu (to zamierzone „kicanie”, nie każdemu się spodoba).
- Mrugają tylko maluchy; z boku powieka nie zakrywa oka. Oczy dorosłych to świecące szczeliny bez mrugania.
- KNIGHT GOLEM i owca to pierwsza wersja: proste bryły, klipy bez sadzenia stóp, golem jeszcze za mało groźny.
- Napis na miniaturach jest z liter 5 × 7 — czytelny, ale surowy; kopiec złota jest regularny („tort”).
- Żar to nadal płaskie pasy Neon — blask da dopiero światło i cząsteczki w zaczepach żaru.
- Kolory stadiów są propozycją (pisklę żółte, bo zielony znika na łące) — do decyzji ludzi.
