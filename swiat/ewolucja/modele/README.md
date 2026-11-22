# Smok ewolucji — modele, klipy i dane dla gry (styl „Żarołuska”)

> **Status: propozycja** (praca nocna 22.11.2026, kierunek stylu przyjęty bez sprzeciwu w sesji głównej). Nic stąd nie jest
> jeszcze wpięte w grę — `swiat/ewolucja/smok.py` i kod gry są nietknięte. Niczego nie wgrano do Roblox.
> **Tej nocy nie było dostępu do Studio**: dane mają dokładnie ten układ, który biblioteka postaci sprawdziła wcześniej
> w Studio (`swiat/postacie/roblox_postac.py`), ale samego smoka w Studio nikt jeszcze nie zbudował ani nie odtworzył.

Osiem stadiów jednego smoka (HATCHLING … ANCIENT DRAGON) z jednego parametrycznego modułu, 23 klipy na stadium,
jajo do wyklucia. Wszystko proceduralnie, biblioteką `swiat/postacie/biblioteka/`.

## Jedno polecenie

```
python -B swiat/ewolucja/modele/generuj.py wszystko     # dane/ + podglad/ + siatki + eksport FBX/GLB (ok. 2–3 min)
```

Części: `dane` · `styl` · `podglady` · `siatki` · `eksport [id…]` · `filmy [klipy…]` · `licz` (bez Blendera) oraz robocze
`przeglad [nr…]`, `paski <nr> [klipy…]`. Blender 5.0 startuje w tle pod wspólną blokadą biblioteki.
Duże pliki trafiają POZA repozytorium: `%LOCALAPPDATA%\BlockyCrycket\modele\smok_ewolucja\` (podfoldery `eksport`,
`siatki`, `filmy`, `podglady`, `przeglad`, `paski`, `styl`).

| Plik | Co to jest |
|---|---|
| `smok_model.py` | dane stadiów (`STADIA`), palety (`PALETY`), budowa modelu `zbuduj_stadium(nr, zmiany_kolorow=…)`, jajo |
| `smok_klipy.py` | klipy parametryczne `dodaj_klipy(p)`, opis zdarzeń `ZDARZENIA_OPIS`, klip jaja |
| `smoki.py` | moduł dla `podglad_postaci.py` biblioteki (`zbuduj()` → 8 stadiów + jajo) |
| `generuj.py` | polecenia; zapis `dane/`, składanie plansz |
| `blender_widoki.py`, `blender_siatki.py` | skrypty uruchamiane w Blenderze (kadry z kamery gry; siatki na staw i region) |
| `dane/` | **przekazanie dla gry**: `indeks.json`, `<id>_rig.json`, `<id>_klipy.json` (id: `smok_1` … `smok_8`, `smok_jajo`) |
| `podglad/` | 12 małych JPG: plansza stylu, rzędy stadiów, plansze 1/4/8, paski klatek, wyklucie, warianty |

## Styl i regiony koloru
Klockowa bryła w kolorze ciała; od karku po ogon ciemne **łuski-dachówki**, w szczelinach **żar** (Neon), którego
z wiekiem jest coraz więcej (`zar` 0,15 → 1,0); rogi, kolce i pazury to **kryształowe ostrza**; błona skrzydeł
w kontrastowym kolorze. Każda część ma region (ostatnia liczba wiersza `czesci`, nazwy w `regiony`):

`0 cialo` · `1 luski` (ciemny akcent: łuski, stopy, hełm; domyślnie kolor ciała przyciemniony) · `2 brzuch` ·
`3 blona` · `4 kolce` · `5 zar` · `6 oko` · `7 stale` (zęby, język, skorupka — nie przemalowywać).

Wariant albo linia żywiołu = podmiana kolorów regionów 0–5 (przykład: `podglad/12_warianty_kolorow.jpg`, słownik
`WARIANTY` w `generuj.py`). Materiał części zostaje (Neon świeci nowym kolorem).

## Jednostki i osie
- Jednostka = **stud**. Model jest już w skali gry: odległość nos–zad = 2 × `promien_gry` (1,6 … 15).
  Początek układu = ziemia pod środkiem tułowia; `wymiary` podają zasięg: `przod` (nos), `tyl` (koniec ogona), `szer`, `wys`.
- Dane w `dane/` są w **układzie rigu Roblox**: smok patrzy w **−Z**, jego lewa strona to **−X**, Y w górę.
  (Kod Pythona używa konwencji biblioteki: przód +Z, lewa +X — zamiana siedzi w `roblox_klocki.py`.)
- Kąty części: radiany dla `CFrame.fromOrientation(rx, ry, rz)`. Kąty w klipach: dziesiąte części stopnia.

## Rig: `<id>_rig.json`
- `hrp` — położenie części-korzenia (środek tułowia).
- `kosci[i]` = `[nazwa, rodzic (0 = korzeń), staw x, y, z, środek x, y, z, rozmiar x, y, z, nazwa stawu]`; indeksy od 1.
- `czesci[j]` = `[kość, kształt, nazwa, px, py, pz, rx, ry, rz, sx, sy, sz, kolor RRGGBB, materiał, grupa, siatka, region]`;
  kształt: 0 Block, 1 Ball, 2 Cylinder, 3 Wedge, 4 CornerWedge; `siatka` = `""` albo SpecialMesh (`Sphere`, `Cylinder`).
- `materialy[k]` = `[materiał Roblox, Reflectance]` (SmoothPlastic, Neon).
- `zaczepy` = `[nazwa, kość, x, y, z względem środka części kości, rx, ry, rz]`.

Budowa (jak w sprawdzonym budowniczym biblioteki): każda kość = niewidzialna część o `rozmiar` w `środek`; staw
`Motor6D` w części-dziecku: `C0 = CFrame.new(staw − środek rodzica)`, `C1 = CFrame.new(staw − środek)`, `Part0` = część
rodzica (albo korzeń w `hrp`), `Part1` = część kości; widoczne części `CFrame.new(p) * CFrame.fromOrientation(r)`
względem ziemi modelu, spięte `WeldConstraint` z częścią swojej kości.

**Stawy (21, te same we wszystkich stadiach):** `Tulow` · `Szyja1` > `Szyja2` > `Glowa` > `Szczeka` ·
`SkrzydloL1` > `SkrzydloL2`, `SkrzydloP1` > `SkrzydloP2` · `Ogon1` > `Ogon2` > `Ogon3` > `Ogon4` ·
`NogaPL1` > `NogaPL2`, `NogaPP1` > `NogaPP2` (przednie lewa / prawa), `NogaTL1` > `NogaTL2`, `NogaTP1` > `NogaTP2` (tylne).
Jajo: `Dol` > `Gora`, `OdlamekL`, `OdlamekP`.

**Zaczepy:** `PyskAttachment` (wylot ognia), `GlowaAttachment` (nad głową), `OgonKoniecAttachment`,
`SkrzydloLKoniecAttachment`, `SkrzydloPKoniecAttachment`, `BrzuchAttachment`, `GrzbietAttachment`.

| Stadium | części Roblox | siatek / trójkątów (ścieżka siatek) |
|---|---|---|
| smok_1 HATCHLING | 61 | 44 / 1960 |
| smok_2 WHELP | 61 | 44 / 1996 |
| smok_3 DRAKE | 77 | 53 / 2316 |
| smok_4 FIRE DRAKE | 89 | 63 / 2524 |
| smok_5 DRAGON | 90 | 62 / 2484 |
| smok_6 WAR DRAGON | 92 | 56 / 2656 |
| smok_7 ELDER DRAGON | 91 | 57 / 2604 |
| smok_8 ANCIENT DRAGON | 91 | 58 / 2616 |
| smok_jajo | 11 | 6 / 556 |

Do tego 21 niewidzialnych części kości na smoka. Aktualne liczby zawsze w `dane/indeks.json`.

## Klipy: `<id>_klipy.json`
`fps` 30, `krok` 2 (próbka co 2 klatki = 15 na sekundę, wartości z krzywych Blendera). Klip:
`{"dl": klatki, "petla": bool, "zdarzenia": {nazwa: klatka}, "stawy": [indeksy kości], "przes": [indeksy kości
z przesunięciem], "probki": [[…], …]}`. Wiersz próbki idzie po `stawy`: dla kości z listy `przes` najpierw
`x, y, z` w **tysięcznych studa**, potem zawsze `rx, ry, rz` w **dziesiątych stopnia**. Próbka `i` to klatka `i × krok`;
ostatnia = klatka `dl` (w pętli równa pierwszej).

```lua
-- t = czas klipu w sekundach; K = klip; motor[i] = Motor6D kości i; C0[i] = jego C0 spoczynkowe
local f = t * 30 / 2
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

Interpolować LICZBY, nie CFrame (w `ogon_zamach` i `koziolek` kąt przechodzi przez 360°). Kości, których klip nie ma
w `stawy`, wracają do pozy spoczynkowej (`C0[i]`). Zamiast `C0` można ustawiać `Motor6D.Transform` w `RunService.PreSimulation`.
Klipy są „w miejscu”: przesuw po mapie, wysokość lotu ponad to, co niesie `Tulow`, i obrót całości robi kod gry.
Zmiana skali modelu o `s`: pozycje, rozmiary i przesunięcia w klipach × `s`, kąty bez zmian.

| Klip | Pętla | Co robi | Zdarzenia |
|---|---|---|---|
| `spoczynek` | tak | oddech, rozglądanie, ogon | — |
| `chod` | tak | kłus po przekątnej; pisklę człapie i kiwa się, prastary stąpa ciężko | — |
| `bieg` | tak | pisklę kica, dorosły galopuje, skrzydła półotwarte | — |
| `gryz1`, `gryz2` | nie | szybkie kłapnięcie w lewo / w prawo | `ugryzienie` |
| `gryz3` | nie | wypad całym ciałem i chaps | `ugryzienie` |
| `ogien_start` → `ogien_petla` → `ogien_koniec` | nie / tak / nie | wdech, zionięcie (pętla trzyma pozę), zamknięcie pyska | `ogien_start`, `ogien_stop` |
| `trafienie` | nie | wzdrygnięcie po ciosie | — |
| `wyklucie` | nie | zwinięty w jaju → wyskok → otrząśnięcie (jajo: klip `wyklucie` w `smok_jajo`) | `pekniecie` |
| `splun` | nie | splunięcie kulą ognia | `strzal` |
| `ogon_zamach` | nie | obrót ciała o 360° z ogonem | `uderzenie_start`, `uderzenie_stop` |
| `ryk` | nie | ryk z rozłożonymi skrzydłami | `ryk_start`, `ryk_stop` |
| `szybowanie_start` → `szybowanie_petla` → `szybowanie_ladowanie` | nie / tak / nie | odbicie, lot ślizgowy, lądowanie | `odbicie`, `ladowanie` |
| `nurkowanie_skok` → `nurkowanie_ladowanie` | nie / nie | skok w górę i pikowanie, uderzenie w ziemię | `odbicie`, `szczyt`, `uderzenie` |
| `koziolek` | nie | bezwładny koziołek w tył po mocnym ciosie, wstaje | `upadek` |
| `pozarcie` | nie | finisher: chaps, podrzut głowy, przełknięcie | `ugryzienie`, `polkniecie` |
| `radosc` | nie | po ewolucji: wyskok, skrzydła, ryk radości | `szczyt` |
| `cokol` | tak | dumna poza na cokół trofeum (prawie nieruchoma) | — |

Klatki zdarzeń różnią się między stadiami (cięższe stadia mają dłuższe klipy) — czytać z `zdarzenia`. Znaczenie
zdarzeń: `dane/indeks.json` → `zdarzenia`. Klipy łańcuchowe kończą się pozą, od której zaczyna się następny.
Jajo jest dopasowane do pisklęcia; dla innego stadium skalować model × (`promien_gry` / 1,6) i rozciągnąć czas klipu
jaja do długości `wyklucie` tego stadium.

## Ścieżka siatek (na później — nic nie wgrano)
`generuj.py siatki` zapisuje poza repozytorium (`…\smok_ewolucja\siatki\`) `<id>_czesci.fbx` i `<id>_czesci.glb`:
jedna siatka na **staw i region koloru**, nazwa `<Staw>__<region>[_neon | _RRGGBB]` (np. `Glowa__kolce`,
`Tulow__zar_neon`, `Glowa__stale_FFFDF4`). Każda siatka ma jeden kolor i jeden materiał (przemalowanie =
`MeshPart.Color`, `_neon` = materiał Neon), fazowane krawędzie, punkt obrotu (origin obiektu) w stawie, bez szkieletu.
Lista z kolorem i trójkątami: `dane/indeks.json` → `siatki`. Stawy i klipy te same co w ścieżce z części.
`generuj.py eksport` robi zwykły eksport biblioteki (`…\eksport\`): `<id>.fbx`, `<id>__<klip>.fbx`, `<id>.glb`,
`<id>.blend` — szkielet, jedna siatka na staw (`<Staw>_Geo`, kolory z tekstury-palety), wszystkie klipy; każdy plik
wczytany z powrotem i porównany. **Import do Studio nie był testowany**; uwagi o kierunku po imporcie FBX
(obrót o 180°) i o punktach obrotu: `swiat/postacie/biblioteka/README.md`.

## Co jest słabe (uczciwie)
- Sylwetki stadiów 3–5 z kamery gry są podobne (różni je kolor, rogi i wielkość skrzydeł, mniej sam obrys).
- Nogi bez odwrotnej kinematyki: przy pochyleniu tułowia stopy lekko ślizgają się, a przy wykroku czubek stopy
  wchodzi w ziemię (do ok. 6% wysokości smoka — liczy to `sprawdz_dane.py`); w `koziolek` kończyny są sztywne.
- Oczy piskląt widać tylko z przodu; z kamery gry „słodkość” niosą proporcje (wielka głowa, małe skrzydła, skorupka).
- Skrzydła to płaskie płyty; błona nie faluje. Żar to płaskie pasy Neon — w grze dojdzie światło i cząsteczki.
- Stadia 4–8 mają 89–92 części (cel: ok. 90), stadia 1–3: 61, 61, 77. Kolory stadiów są propozycją (pisklę żółte
  zamiast zielonego, bo zielony znika na łące) — do decyzji ludzi.
- Sprawdzian bez Studio: `python -B swiat/ewolucja/modele/sprawdz_dane.py` odtwarza klipy z `dane/` tak jak gra
  (stawy, zdarzenia, domknięcie pętli, wypad pyska, zasięg ogona). Budowy i odtwarzania w Studio nie sprawdzono.
