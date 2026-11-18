# Rasy postaci — modele z rzutów (D-104, pilotaż A1)

> **Status: propozycja, nie kanon.** Część A1 (18.11.2026): wspólny kod ras i dwie rasy — **elf i ork** — zbudowane
> i obejrzane w Blenderze. Mroczny elf, demon, goblin i półbóg mają komplet danych i szkic brył (liczony w czystym
> Pythonie, **nierenderowany i nieoglądany**). Roblox Studio: nic nie było robione. Założenia z pkt 1 to decyzje
> prowadzącego etap, do potwierdzenia przez Karola i Pawła. Decyzje: [[Rejestr decyzji]] D-071, D-079, D-080, D-104;
> rzuty: `B&C/Postacie/Rasy — rzuty dla modelarza.md`. Kontrakt ekwipunku: `EKWIPUNEK.md`, konwencje:
> `biblioteka/README.md`.

## 1. Założenia (propozycja)
1. **Rasa = ciało typu `czlowiek` bez zmiany klocków.** Te same klocki R15, kości, stawy, 18 zaczepów i klipy co
   goły Rycerz i goły Zwiadowca (`rasy.WYMIARY` to `rycerz.WYMIARY`). Każdy przedmiot `czlowiek` pasuje bez
   przeróbek (`ekwipunek.ubierz`), a klipy klas działają bez przeliczania. `ekwipunek.py` nie był zmieniany.
2. **Rasę odróżniają:** paleta skóry, twarz, uszy, włosy, rogi, kły, nos, ogon, aureola i kolor spodenek. Dodatki to
   sztywne bryły na istniejących kościach (głowa, a ogon demona na biodrach) — bez nowych kości.
3. **Skala rasy jest daną, nie geometrią.** `RASY[<rasa>]["skala"]` (ork 1,08, goblin 0,88, reszta 1,0) trafia do
   `Postac.skala_rasy` i `ekwipunek.json`. Model, eksporty i przymiarki są w skali 1. Skalę pokazuje plansza
   `rasa_<id>_skala.jpg` (`rasy.w_skali()` — kopia tylko do renderu). W grze byłaby to jednolita skala modelu.
4. **Strój bazowy z rzutów** jest warstwą 0 ciała (bryły `golas`, jak bielizna gołego Rycerza z `EKWIPUNEK.md`
   pkt 1): lniana koszula z krótkim rękawem i wycięciem w serek, spodenki w kolorze rasy, **brązowe buty**.
   Powłoka przedmiotu na tej samej kości ją zdejmuje (pkt 4 niżej).
5. **Cechy rasy nie znikają.** Twarz, uszy, kły, rogi, ogon i aureola mają znacznik `cecha` i nie mają `golas`,
   więc żadna powłoka ich nie zdejmuje (ważne dla ogona na biodrach: spodnie mają tam powłokę).
6. **Włosy** są akcesorium ciała `rasa_<id>_wlosy` na `HairAttachment` ze znacznikiem `Wlosy` — hełm i kaptur
   (`ukrywa=("Wlosy",)`) je chowają, tak jak `rycerz_wlosy`.
7. **Klipy** `idle`, `chod`, `wiwat` są skopiowane (`ekwipunek.kopiuj_klipy`, kanały = deepcopy, bez przeliczania)
   z ciała odniesienia człowieka: `rycerz.postac_odniesienia()`. Źródłem jest Rycerz, bo jego trzy klipy to proste
   szkice niezależne od geometrii stroju; klipy Zwiadowcy liczą się z łukiem i sztyletem. W grze rasa ma grać
   klipy swojej klasy (te same kości i stawy — sprawdza to test).

## 2. Pliki i polecenia
| Plik | Co to |
|---|---|
| `rasy.py` | dane sześciu ras (`RASY`: palety, cechy głowy, ogon, skala, spodenki, rzut, ikona), strój bazowy, cechy głowy, włosy, `cialo()`, `model()`, `stroj()`, `warianty()`, `w_skali()`, `ekwipunek_json()` |
| `rasa_elf.py`, `rasa_ork.py` | moduły ras w kształcie modułu postaci: `zbuduj()` → `[Postac "rasa_<id>"]`, do tego `cialo()`, `warianty()`, `STROJE`, `SLABOSCI`, `po_przebudowie()` |
| `rasy_plansze.py`, `rasy_plansze_blender.py` | plansza porównawcza z rzutem i plansza skali (własne rendery ortogonalne o stałej skali; budowa siatek i światło z `biblioteka/blender_postac.py`) |
| `biblioteka/test_rasy.py` | test bez Blendera: dane, ciało i klipy równe człowiekowi, przedmioty na rasach, moduły, bohaterowie bez zmian |
| `przebuduj.py` | jedna zmiana zgodna wstecz: moduł z funkcją `po_przebudowie(cel)` dokłada po ułożeniu wyniku własne obrazy (inne moduły przebudowują się jak dotąd) |

```
python -B swiat/postacie/przebuduj.py rasa_elf rasa_ork --bez-filmow   # wynik/rasa_<id>/ (ok. 45 s na obie)
python -B swiat/postacie/rasy_plansze.py elf ork                       # same plansze porównawcze i skali
python -B swiat/postacie/rasy_plansze.py elf --wyj <folder>            # próba poza repozytorium
python -B swiat/postacie/biblioteka/test_rasy.py                       # test bez Blendera (ok. 3 s)
```

`wynik/rasa_<id>/` ma zwykły układ (`README.md`) i dodatkowo:
- `rasa_<id>_porownanie.jpg` — u góry rzut Pawła (przód, 3/4, bok, tył), pod spodem te same cztery widoki modelu
  w jednej skali. Model stoi tam w pozie A (ręce 10° od ciała) — tylko w tym renderze.
- `rasa_<id>_skala.jpg` — manekin R15 | człowiek (goły Rycerz) | rasa pomnożona przez skalę z danych.
- `ekwipunek/rasa_<id>_ekwipunek_plansza.jpg` — przymiarka: strój bazowy | komplet Rycerza | komplet Zwiadowcy;
  obok plansze czterech widoków każdego stroju, ciało z zaczepami `Ekw<Kosc>Attachment`
  (`rasa_<id>_cialo.fbx/.glb`) i `ekwipunek.json` (dane ciała rasy, bez własnych przedmiotów).

Stan z 18.11.2026 (`przebuduj.py`, kontrola eksportów 8/8 zgodnych dla każdej rasy):

| | Elf | Ork |
|---|---|---|
| bryły ciała + włosów | 55 + 28 | 56 + 16 |
| trójkąty (15 siatek ciała + włosy) | 2492 | 2256 |
| wzrost ciała / z włosami (studs, skala 1) | 5,30 / 5,62 | 5,30 / 6,39 (kok) |
| wzrost w skali rasy (czubek głowy) | 5,30 | 5,72 |
| `rasa_<id>.glb` (3 klipy) | 420 kB | 389 kB |
| kości / zaczepy / klipy | 17 / 18 / idle 60, chod 24, wiwat 36 klatek | to samo |

## 3. Co ma każda rasa
| Rasa | Skóra | Głowa | Włosy | Dodatki | Spodenki | Skala | Stan |
|---|---|---|---|---|---|---|---|
| Elf | jasna `F9CFAE` | łagodna twarz, zielone oczy, długie uszy na boki (0,92 studa, 24° w górę) | długie złote z przedziałkiem, do łopatek | — | jasnozielone `A6DA7E` | 1,00 | **zbudowany** |
| Ork | oliwkowa `8D9B35` | szersza wysunięta szczęka, wał brwiowy, grube brwi, małe oczy, szeroki nos, krótkie uszy | czarne z kokiem związanym rzemieniem | dwa kły z dolnej szczęki (0,27 studa) | brązowe `9C6B3C` | 1,08 | **zbudowany** |
| Mroczny elf | lawendowo-szara `8E8AB6` | jak elf, fioletowe oczy | długie srebrne (te same bryły co elf) | — | fioletowe `5B2C82` | 1,00 | dane + szkic (kod elfa) |
| Demon | czerwona `CC3650` | złote świecące oczy, skośne brwi, uśmiech | brak (głowa-klocek) | czarne rogi, kieł, ogon z grotem na biodrach | czarne `2A2730` | 1,00 | dane + szkic |
| Goblin | żółtozielona `C6D92E` | wielkie uszy, długi nos z żółtawym czubkiem, szeroki uśmiech z zębami | brak | — | pomarańczowe `F06A22` | 0,88 | dane + szkic |
| Półbóg | złota `F2B63C` | łagodna twarz, świecące niebieskie oczy | jasne falowane do karku | aureola (pierścień nad głową) | białe ze złotą lamówką | 1,00 | dane + szkic |

Człowieka nie ma w tym zestawie: jego modelem jest ciało bazowe Rycerza i Zwiadowcy (notatka o rzutach, 17.11).

## 4. Strój bazowy i buty a kontrakt ekwipunku
- Koszula (tułów i ramiona), spodenki (biodra i uda) i buty (stopy) to bryły `golas` w tych samych odległościach
  od klocka co u gołego Rycerza: koszula 0,02–0,035, spodenki 0,01, góra nogawki 0,02 nad klockiem uda.
- **Buty:** kontrakt mówi, że goły Rycerz ma bose stopy, a rzuty ras mają brązowe buty. Propozycja: buty bazowe są
  warstwą 0 na kości stopy (klocek stopy w brązie, podeszwa, nosek, cholewka; do +0,04). Slot Boots ma powłokę na
  goleni i stopie, więc **każdy przedmiot „buty” zdejmuje je sam** — bez zmian w `ekwipunek.py` i bez nowego
  przedmiotu. `rasy.cialo(rasa, buty=False)` daje bose stopy jak u Rycerza, gdyby ludzie woleli jedną zasadę.
- Odrzucona alternatywa: przedmiot „buty bazowe” w slocie Boots zakładany domyślnie. Dałby zdejmowanie butów
  w grze, ale dokłada przedmiot do katalogu i regułę „pusty slot = buty bazowe”.
- Sprawdzone testem: pełne komplety Rycerza i Zwiadowcy zdejmują strój bazowy ze wszystkich kości poza głową,
  a cechy rasy zostają. Wspólnych ścian (migotanie) między strojem bazowym a pojedynczym przedmiotem skrypt
  roboczy nie znalazł (bryły nieobrócone, próg 0,006 studa; bryły obrócone nie były liczone).

## 5. Elf — wybory i czego nie oddano
- Oddane: jasna skóra, zielone oczy z białkiem i błyskiem, złote brwi, łagodny uśmiech, długie uszy na boki
  z ciemniejszym wnętrzem, włosy z przedziałkiem, grzywka na boki, kurtyny po bokach głowy ze skosem przy skroni
  (ucho wychodzi przez włosy), pasma wzdłuż żuchwy i na pierś poza obrysem twarzy, tył do łopatek ze szpicem,
  koszula w serek, jasnozielone spodenki, brązowe buty.
- Nieoddane: miękkie fale i objętość włosów (bryły są płaskie, bok głowy wygląda jak pudełko), długość pasm
  z przodu (na rzucie sięgają do połowy piersi, w modelu kończą się wyżej), kształt dłoni i stóp, zmarszczki
  koszuli, zaokrąglone noski butów.
- **Sylwetka:** rzut jest smuklejszy od klocków Rycerza. Tułów z rękami ma na rysunku ok. 0,45 wzrostu, w modelu
  0,78; sam tułów ok. 0,26 wobec 0,42 (pomiar linijką na pomniejszonym rzucie, przybliżony). To skutek
  założenia 1, nie błąd głowy (pytanie 1).

## 6. Ork — wybory i czego nie oddano
- Oddane: oliwkowa skóra, szczęka szersza o 0,1 i wysunięta o 0,075 studa, wał brwiowy z grubymi skośnymi
  brwiami, małe oczy, szeroki nos, szeroka kreska ust z uniesionym kącikiem, dwa kły z dolnej szczęki, krótkie
  spiczaste uszy, czarne włosy z klinem nad czołem, kok z rzemieniem i kosmykami.
- **Spodenki brązowe** według zamówienia; na rzucie wyszły wielokolorowe (pytanie 6).
- **Nieoddane: masywne ciało.** Szeroki tułów, grube ręce i kark z rysunku wymagałyby innych klocków, a wtedy
  przedmioty `czlowiek` przestałyby pasować. Masywność niesie głowa i skala 1,08 z danych.
- Kok jest sztywny i kanciasty (ostrosłupy), rysunkowy opada miękko do tyłu.

## 7. Klipy
- `idle` (60 klatek, pętla), `chod` (24, pętla), `wiwat` (36, pętla) — klucze co do wartości jak w `rycerz.cialo()`.
- Skutek: w `idle` i `chod` prawe przedramię jest uniesione jak do miecza (bez broni wygląda jak uniesiona
  pięść), w `wiwat` prawa ręka idzie w górę jak z mieczem. Neutralnego spoczynku dla ekranu wyboru rasy nie ma
  (pytanie 9). Model główny i plansze stoją w pozie spoczynku (bez klipu).
- W `wiwat` głowa odchyla się o 12° i tył długich włosów elfa wchodzi w plecy (szacunek z geometrii: ok. 0,1
  studa); nie było to liczone klatka po klatce ani oglądane na filmie.

## 8. Przymiarki i lista przenikań
Stroje: `rycerz` = `rycerz.KANON` (hełm, zbroja, nogawice, pas, rękawice, trzewiki, miecz), `zwiadowca` =
`zwiadowca.KANON` (kaptur z peleryną, kirys, spodnie, pas, rękawice, buty, łuk z kołczanem, sztylet); poza `idle`
klatka 0. Każdy przedmiot `czlowiek` daje się też założyć osobno na każdą z sześciu ras (test). Liczby z próbek
punktów w bryłach cech (skrypt roboczy poza repozytorium; przedmioty liczone jako skrzynki):

| Co | Elf | Ork |
|---|---|---|
| Uszy w ściance hełmu Rycerza (`Helm bok`) | ok. 42% objętości ucha; czubek 0,51 studa poza hełmem | ok. 50%; czubek 0,27 studa |
| Uszy w ściance kaptura Zwiadowcy (`Kaptur bok`) | ok. 35%; czubek 0,59 studa poza kapturem | ok. 42%; czubek 0,35 studa |
| Włosy pod hełmem i kapturem | znikają w całości — elf traci długie włosy | znikają razem z kokiem |
| Kły, szczęka, wał brwiowy a hełm | — | mieszczą się w otworze twarzy (bez przenikania po zwężeniu wału do 1,18 studa) |
| Włosy a strój bez nakrycia głowy | tył włosów przecina **kołczan Zwiadowcy** na plecach; z kompletem Rycerza bez hełmu nic (spoczynek) | nic |
| **Rękawice Zwiadowcy** | powłoka ma klocek dłoni w kolorze skóry człowieka — przy skórze elfa prawie nie widać | **dłonie orka robią się ludzkie** (widać na przymiarce) |

Poza liczeniem: przenikanie w ruchu (klipy) nie było sprawdzane; pasma włosów elfa są sztywne z głową.

## 9. Pytania do ludzi
1. **Skala i proporcje ras a ekwipunek**
   - Rasy stoją na klockach Rycerza; rzuty są smuklejsze, ork masywniejszy, goblin mniejszy.
   - A: te same klocki + skala całego modelu (ork 1,08, goblin 0,88) — każdy przedmiot pasuje (tak jest teraz).
   - B: własne klocki ras — bliżej rzutów, ale każdy przedmiot trzeba dopasować do każdej rasy.
   - Szczegóły: liczby proporcji w pkt 5 i 6; skala w grze to mnożnik modelu, więc ekwipunek rośnie razem z orkiem.
2. **Mag jest kotem — jak łączyć rasę z klasą Mag**
   - Kot-Mag ma własne ciało `kot`; rasy są ciałem `czlowiek`.
   - A: Mag dowolnej rasy na ciele `czlowiek` (nowe przedmioty Maga dla człowieka, kot zostaje maskotką).
   - B: klasa Mag bez wyboru rasy (zawsze kot).
   - Szczegóły: szata i kapelusz kota nie pasują na ciało `czlowiek` (`ubierz` zgłasza błąd typu ciała).
3. **Hełm a uszy, rogi i włosy**
   - Dziś hełm chowa włosy w całości, a uszy przechodzą przez ściankę hełmu i kaptura.
   - A: zostawić (uszy na wierzchu jak u kota przez rondo). B: hełm chowa też uszy (`ukrywa`).
   - C: hełmy z wycięciami na uszy i rogi dla ras.
   - Szczegóły: rogi demona i aureola półboga będą miały ten sam problem; lista w pkt 8.
4. **Wygląd Półboga**
   - Zależy od pytania 47 (D-080: mocniejsza rasa czy tylko wygląd).
   - Czy aureola i świecące oczy zostają przy każdym stroju, także pod hełmem?
5. **Który wariant goblina**
   - Dwa rzuty: `goblin.jpg` i `goblin_wariant2.jpg` (większa głowa, cieńsze ręce).
   - Dane mają dziś pierwszy; który budować?
6. **Kolor spodenek orka**
   - Zamówienie: brązowe; rzut: wielokolorowe. Model ma brązowe `9C6B3C`.
   - Zostają brązowe czy inny kolor (brąz zlewa się z butami)?
7. **Buty bazowe: także dla człowieka?**
   - Rasy mają brązowe buty jako warstwę ciała; goły Rycerz i Zwiadowca są boso.
   - A: człowiek też dostaje buty. B: rasy boso jak człowiek (`buty=False`). C: zostaje różnica.
8. **Kolor skóry w przedmiotach**
   - Rękawice bez palców Zwiadowcy mają dłoń w kolorze skóry człowieka — na orku wychodzi ludzka dłoń.
   - A: bryły „skóra” przedmiotu biorą kolor ciała przy zakładaniu. B: takie przedmioty nie zakrywają dłoni.
   - Szczegóły: dotyczy każdego przedmiotu, który rysuje gołą skórę (dekolty, palce); wymaga zmiany w `ekwipunek.py`.
9. **Spoczynek rasy na ekranie wyboru**
   - Klipy rasy to idle, chód i wiwat Rycerza (ręka jak do miecza).
   - Czy zrobić neutralny spoczynek bez broni dla selektora, czy rasa zawsze stoi w klipach wybranej klasy?
10. **Demon: z uszami czy bez**
    - Ikona wyboru rasy ma spiczaste uszy, rzut ich nie ma. Dane mają dziś „bez uszu”.

## 10. Czego nie zrobiono i nie sprawdzono
- Mroczny elf, demon, goblin i półbóg: brak modułów `rasa_<id>.py`, renderów i plansz; szkic brył nie był oglądany.
- Roblox Studio: nic (ani rig z klocków, ani import siatek). `roblox_postac.py` nie zna modułów ras.
- Filmy klipów: nie renderowano (`--bez-filmow`); klipy są sprawdzone tylko liczbowo (równe Rycerzowi).
- Przenikanie w ruchu i kontrola liczbowa klipów (`--kontrola` jak u bohaterów): nie ma.
- Ikony ras to rendery popiersia z biblioteki, nie ikony z `assets/processed/RaceSelect/`.
- `przedmioty.json`, `zestawienie.py` i panel nie wiedzą o rasach.

## 11. Następne etapy (po przeglądzie)
- A2: moduły czterech pozostałych ras na tym samym kodzie, plansze porównawcze, poprawki szkiców.
- B: rasy w Studio (rig z klocków bez wgrywania), przymiarka w grze, skala rasy na modelu.
