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
Części: `dane` · `rekwizyty` · `stwory` · `styl` · `podglady` · `obrazy` · `siatki` · `eksport [id…]` · `licz`;
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
| `podglad/` | 16 małych JPG: styl, rzędy stadiów, przegląd z wersją uproszczoną, plansze 1/4/8, paski klatek, wyklucie, warianty i rekwizyty, ikona, trzy miniatury |

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

## Co jest słabe (uczciwie)
- Stopy stoją na ziemi, ale poślizg w poprzek przy kołysaniu tułowia i obrót stóp w `ogon_zamach` zostają;
  w galopie nogi maluchów chwilami wiszą w powietrzu (to zamierzone „kicanie”, nie każdemu się spodoba).
- Mrugają tylko maluchy; z boku powieka nie zakrywa oka. Oczy dorosłych to świecące szczeliny bez mrugania.
- KNIGHT GOLEM i owca to pierwsza wersja: proste bryły, klipy bez sadzenia stóp, golem jeszcze za mało groźny.
- Napis na miniaturach jest z liter 5 × 7 — czytelny, ale surowy; kopiec złota jest regularny („tort”).
- Żar to nadal płaskie pasy Neon — blask da dopiero światło i cząsteczki w zaczepach żaru.
- Kolory stadiów są propozycją (pisklę żółte, bo zielony znika na łące) — do decyzji ludzi.
