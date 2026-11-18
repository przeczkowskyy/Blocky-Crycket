# Rasy postaci — modele z rzutów (D-104, etapy A1 i A2)

> **Status: propozycja, nie kanon.** Zbudowane i obejrzane w Blenderze jest wszystkie sześć ras: **elf i ork**
> (pilotaż A1, 18.11.2026) oraz **mroczny elf, demon, goblin i półbóg** (etap A2, 18.11.2026). Roblox Studio: nic
> nie było robione. Założenia z pkt 1 to decyzje prowadzącego etap, do potwierdzenia przez Karola i Pawła.
> Decyzje: [[Rejestr decyzji]] D-071, D-079, D-080, D-104; rzuty: `B&C/Postacie/Rasy — rzuty dla modelarza.md`.
> Kontrakt ekwipunku: `EKWIPUNEK.md`, konwencje: `biblioteka/README.md`.

## 1. Założenia (propozycja)
1. **Rasa = ciało typu `czlowiek` bez zmiany klocków.** Te same klocki R15, kości, stawy, 18 zaczepów i klipy co
   goły Rycerz i goły Zwiadowca (`rasy.WYMIARY` to `rycerz.WYMIARY`). Każdy przedmiot `czlowiek` pasuje bez
   przeróbek (`ekwipunek.ubierz`), a klipy klas działają bez przeliczania. `ekwipunek.py` nie był zmieniany.
2. **Rasę odróżniają:** paleta skóry, twarz, uszy, włosy, rogi, kły, nos, ogon, aureola i kolor spodenek. Dodatki to
   sztywne bryły na istniejących kościach (głowa, a ogon demona na biodrach) — bez nowych kości.
3. **Skala rasy jest daną, nie geometrią.** `RASY[<rasa>]["skala"]` (ork 1,08, goblin 0,88, reszta 1,0) trafia do
   `Postac.skala_rasy` i `ekwipunek.json`. Model, eksporty i przymiarki są w skali 1. Skalę pokazują plansze
   `rasa_<id>_skala.jpg` i `_rasy/rasy_razem.jpg` (`rasy.w_skali()` — kopia tylko do renderu). W grze byłaby to
   jednolita skala modelu.
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

Ustalenia prowadzącego z etapu A2 (też propozycja): goblin według pierwszego rzutu (`goblin.jpg`), demon bez uszu
i z ogonem sztywnym na biodrach, półbóg z aureolą i świecącymi oczami (emisja w teksturze-palecie).

## 2. Pliki i polecenia
| Plik | Co to |
|---|---|
| `rasy.py` | dane sześciu ras (`RASY`: palety, cechy głowy, ogon, skala, spodenki, rzut, ikona), strój bazowy, twarze, uszy, rogi, aureola, ogon, włosy, `cialo()`, `model()`, `stroj()`, `warianty()`, `w_skali()`, `ekwipunek_json()` |
| `rasa_elf.py`, `rasa_ork.py`, `rasa_mroczny_elf.py`, `rasa_demon.py`, `rasa_goblin.py`, `rasa_polbog.py` | moduły ras w kształcie modułu postaci: `zbuduj()` → `[Postac "rasa_<id>"]`, do tego `cialo()`, `warianty()`, `STROJE`, `SLABOSCI`, `po_przebudowie()` |
| `rasy_plansze.py`, `rasy_plansze_blender.py` | plansza porównawcza z rzutem, plansza skali i plansza zbiorcza (własne rendery ortogonalne o stałej skali; budowa siatek i światło z `biblioteka/blender_postac.py`) |
| `biblioteka/test_rasy.py` | test bez Blendera: dane, ciało i klipy równe człowiekowi, przedmioty na rasach, sześć modułów, bohaterowie bez zmian |
| `przebuduj.py` | jedna zmiana zgodna wstecz (A1): moduł z funkcją `po_przebudowie(cel)` dokłada po ułożeniu wyniku własne obrazy (inne moduły przebudowują się jak dotąd) |

```
python -B swiat/postacie/przebuduj.py rasa_elf rasa_ork rasa_mroczny_elf rasa_demon rasa_goblin rasa_polbog --bez-filmow
                                                                       # wynik/rasa_<id>/ (ok. 22 s na rasę)
python -B swiat/postacie/rasy_plansze.py elf ork                       # same plansze porównawcze i skali
python -B swiat/postacie/rasy_plansze.py --razem                       # wynik/_rasy/rasy_razem.jpg (ok. 7 s)
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

`wynik/_rasy/rasy_razem.jpg` — plansza zbiorcza: człowiek (goły Rycerz) i sześć ras obok siebie, każda pomnożona
przez swoją skalę; górny wiersz z przodu, dolny 3/4. Robi ją osobne polecenie `--razem` (nie `przebuduj.py`),
więc po zmianie ras trzeba je puścić jeszcze raz.

Stan z 18.11.2026 (`przebuduj.py`, kontrola eksportów 8/8 zgodnych dla każdej rasy; każda rasa ma 17 kości,
18 zaczepów i klipy idle 60, chod 24, wiwat 36 klatek):

| | Elf | Mroczny elf | Ork | Demon | Goblin | Półbóg |
|---|---|---|---|---|---|---|
| bryły ciała + włosów | 55 + 42 | 55 + 42 | 56 + 16 | 63 + 0 | 57 + 0 | 59 + 17 |
| trójkąty | 2924 | 2924 | 2412 | 2166 | 1844 | 2888 |
| wzrost ciała / najwyższy punkt (studs, skala 1) | 5,30 / 5,70 | 5,30 / 5,70 | 5,30 / 6,20 (kok) | 5,30 / 6,10 (rogi) | 5,30 / 5,30 | 5,30 / 6,20 (aureola) |
| skala rasy → wzrost w skali (czubek głowy) | 1,00 → 5,30 | 1,00 → 5,30 | 1,08 → 5,72 | 1,00 → 5,30 | 0,88 → 4,66 | 1,00 → 5,30 |
| `rasa_<id>.glb` (3 klipy) | 482 kB | 482 kB | 410 kB | 374 kB | 327 kB | 478 kB |

Raport Blendera ostrzega u demona i półboga, że siatka głowy z rogami (2,30 studa) i z aureolą (2,40) jest wyższa
niż limit części ciała awatara (2,00). To limit ciał sprzedawanych na Marketplace; postaci w grze nie blokuje.

## 3. Co ma każda rasa
| Rasa | Skóra | Głowa | Włosy | Dodatki | Spodenki | Skala |
|---|---|---|---|---|---|---|
| Elf | jasna `F9CFAE` | łagodna twarz, zielone oczy, długie uszy na boki (0,92 studa, 24° w górę) | długie złote z przedziałkiem, do łopatek | — | jasnozielone `A6DA7E` | 1,00 |
| Mroczny elf | lawendowo-szara `8E8AB6` | te same bryły co elf, fioletowe oczy | długie srebrne (bryły elfa) | — | fioletowe `5B2C82` | 1,00 |
| Ork | oliwkowa `8D9B35` | szersza wysunięta szczęka, wał brwiowy, grube brwi, małe oczy, szeroki nos, krótkie uszy 44° w górę | czarne z obłym kokiem i kosmykiem opadającym do tyłu | dwa kły z dolnej szczęki (0,27 studa) | brązowe `9C6B3C` | 1,08 |
| Demon | czerwona `CC3650` | głowa-klocek bez uszu, złote świecące skośne oczy, skośne brwi, uśmiech w łuk | brak | czarne rogi w łuk (0,8 studa nad głową), jeden kieł, ogon z grotem na biodrach | czarne `2A2730` | 1,00 |
| Goblin | żółtozielona `C6D92E` | wielkie uszy na boki (1,0 studa), grube brwi, małe oczy, długi nos z żółtawym czubkiem, uśmiech z zębami | brak | — | pomarańczowe `F06A22` | 0,88 |
| Półbóg | złota `F2B63C` | łagodna twarz, świecące niebieskie oczy bez źrenic | jasne falowane do karku | świecąca aureola 0,68 studa nad głową (pierścień z 12 belek, pochylony 16°) | białe ze złotą lamówką | 1,00 |

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
- Sprawdzone testem dla sześciu ras: pełne komplety Rycerza i Zwiadowcy zdejmują strój bazowy ze wszystkich kości
  poza głową, a cechy rasy zostają. Wspólnych ścian (migotanie) między strojem bazowym a pojedynczym przedmiotem
  skrypt roboczy w A1 nie znalazł (bryły nieobrócone, próg 0,006 studa; bryły obrócone nie były liczone).

## 5. Czego nie oddano z rzutów
Wspólne dla wszystkich ras:
- **Sylwetka.** Rzuty są smuklejsze od klocków Rycerza: tułów z rękami ma na rysunku ok. 0,45 wzrostu, w modelu
  0,78; sam tułów ok. 0,26 wobec 0,42 (pomiar linijką na pomniejszonym rzucie elfa, przybliżony). To skutek
  założenia 1 (pytanie 1).
- Rysunki stoją w pozie A, model w spoczynku ma ręce prosto w dół. Dłonie i stopy to klocki, buty są płaskie,
  twarze nie mają mimiki, zmarszczek koszuli nie ma.

| Rasa | Oddane | Nieoddane albo uproszczone |
|---|---|---|
| Elf | jasna skóra, zielone oczy, złote brwi, łagodny uśmiech, długie uszy z ciemniejszym wnętrzem, włosy: przedziałek, grzywka na boki, pasma po bokach, po dwa pasma na pierś do połowy piersi, tył w trzech warstwach ze szpicem do łopatek | miękkie fale włosów (są klocki i schodki), płynna linia pasm |
| Mroczny elf | lawendowa skóra, srebrne włosy, fioletowe oczy i spodenki | jak elf; na rzucie oczy są węższe (przymknięte), model ma oczy elfa |
| Ork | oliwkowa skóra, szczęka, wał brwiowy, brwi, kły, krótkie uszy w górę, czarna czapa włosów z klinem nad czołem, obły kok z rzemieniem i kosmykiem do tyłu | **masywne ciało** (szeroki tułów, grube ręce, kark) — niesie je tylko głowa i skala 1,08; spodenki są brązowe według zamówienia, rzut ma wielokolorowe |
| Demon | czerwona skóra, głowa-klocek, rogi w łuk, świecące złote oczy, brwi, uśmiech z kłem, rumieńce, ogon z grotem po lewej stronie postaci, czarne spodenki | ogon jest sztywną łamaną z sześciu klocków (na rzucie cienki, miękki łuk), rogi kanciaste; ikona wyboru rasy ma spiczaste uszy, rzut i model nie |
| Goblin | żółtozielona skóra, wielkie uszy, brwi, małe oczy, długi nos z żółtawym czubkiem, szeroki uśmiech z zębami, pomarańczowe spodenki | **cienkie ręce i nogi oraz duża głowa na małym ciele** — mały wzrost niesie tylko skala 0,88; nos to trzy klocki bez haczykowatego łuku, zęby to prosty rząd |
| Półbóg | złota skóra, aureola, jasne falowane włosy, świecące niebieskie oczy, białe spodenki ze złotą lamówką | poświata wokół całej postaci (efekt do zrobienia w grze), włosy to kanciaste fale z klocków |

## 6. Świecenie
Oczy demona i półboga oraz aureola mają materiał `swiecacy`: emisja jest zapisana w teksturze-palecie
`rasa_<id>_tekstury/rasa_<id>_emisja.png` (jak kryształy i slime w innych modułach). W renderach Blendera świecą;
w grze emisję trzeba podpiąć albo zastąpić częścią Neon / `PointLight` — nie było to sprawdzane.

## 7. Klipy
- `idle` (60 klatek, pętla), `chod` (24, pętla), `wiwat` (36, pętla) — klucze co do wartości jak w `rycerz.cialo()`.
- Skutek: w `idle` i `chod` prawe przedramię jest uniesione jak do miecza (bez broni wygląda jak uniesiona
  pięść), w `wiwat` prawa ręka idzie w górę jak z mieczem. Neutralnego spoczynku dla ekranu wyboru rasy nie ma
  (pytanie 9). Model główny i plansze stoją w pozie spoczynku (bez klipu).
- Dodatki są sztywne: ogon demona nie rusza się w klipach, pasma włosów elfa idą z głową. W `wiwat` głowa
  odchyla się o 12° i tył długich włosów wchodzi w plecy (szacunek z geometrii, ok. 0,1–0,2 studa). Żaden klip
  ras nie był liczony klatka po klatce ani oglądany na filmie.

## 8. Przymiarki i lista przenikań
Stroje: `rycerz` = `rycerz.KANON` (hełm, zbroja, nogawice, pas, rękawice, trzewiki, miecz), `zwiadowca` =
`zwiadowca.KANON` (kaptur z peleryną, kirys, spodnie, pas, rękawice, buty, łuk z kołczanem, sztylet); poza `idle`
klatka 0. Każdy przedmiot `czlowiek` daje się też założyć osobno na każdą z sześciu ras (test). Liczby: próbki
punktów w bryłach cech i narożniki brył w pozie spoczynku (skrypt roboczy poza repozytorium; przedmioty liczone
jako skrzynki). Przenikanie w ruchu nie było sprawdzane.

**Uszy a hełm Rycerza i kaptur Zwiadowcy** (uszy przechodzą przez ściankę i wystają na zewnątrz):

| Rasa | objętość uszu w ściance hełmu / kaptura | czubek poza hełmem / kapturem |
|---|---|---|
| Elf, mroczny elf | ok. 42% / 32% | 0,51 / 0,59 studa |
| Ork | ok. 58% / 53% | 0,07 / 0,15 studa (prawie całe schowane) |
| Goblin | ok. 37% / 26% | 0,65 / 0,73 studa |

**Rogi i aureola a nakrycie głowy:**
- Rogi demona przebijają górę hełmu (`Helm kopula`, `Helm czubek`) i czubek kaptura (`Kaptur czubek`): ok. 50%
  i 53% objętości rogów siedzi w nakryciu głowy, czubki wystają 0,39 studa nad hełm i 0,34 nad kaptur.
- Aureola półboga nie przecina nakrycia głowy: jej najniższy (przedni) punkt jest 0,05 studa nad grzebieniem
  hełmu, a kaptur Zwiadowcy sięga najwyżej do poziomu przodu pierścienia (5,76 studa) i też go nie dotyka.

**Ogon demona a spodnie, pas i poły:**
- Spodnie i nogawice go nie zdejmują (cecha rasy); nasada ogona zaczyna się w klocku bioder (ok. 4% objętości
  ogona jest schowane w biodrach — tak ma być).
- Tylna poła tabardu Rycerza: bez przecięcia, ogon wychodzi tuż nad jej górną krawędzią.
- Pas Zwiadowcy: ogon przechodzi przez pas z tyłu (ok. 4% objętości ogona). Peleryna Zwiadowcy: ogon dotyka
  dolnego liścia peleryny (ok. 2%).

**Pozostałe:**
- Nos goblina wystaje przez otwór twarzy 0,47 studa przed hełm i 0,55 przed kaptur, bez przecięcia.
- Kły, szczęka i wał brwiowy orka mieszczą się w otworze twarzy hełmu. Szczęka (szersza od głowy o 0,05 na stronę
  i wysunięta o 0,075) zachodzi na obojczyk zbroi Rycerza (12% objętości szczęki) oraz na kołnierz kaptura, chustę
  i barki peleryny Zwiadowcy (37%). Te bryły sięgają nad linię szyi, więc dół głowy człowieka też w nich siedzi;
  czy wysunięta szczęka przebija je na zewnątrz, nie oglądałem z bliska.
- Włosy pod hełmem i kapturem znikają w całości: elf i mroczny elf tracą długie włosy, ork kok, półbóg fale.
- Bez kaptura tył włosów elfa, mrocznego elfa i półboga przecina **kołczan Zwiadowcy** na plecach; z kompletem
  Rycerza bez hełmu włosy niczego nie przecinają (spoczynek).
- **Rękawice Zwiadowcy** mają w powłoce klocek dłoni w kolorze skóry człowieka: na orku, demonie, goblinie,
  półbogu i mrocznym elfie dłonie robią się ludzkie (widać na przymiarkach); u elfa prawie nie widać.

## 9. Pytania do ludzi
1. **Skala i proporcje ras a ekwipunek**
   - Rasy stoją na klockach Rycerza; rzuty są smuklejsze, ork masywniejszy, goblin drobny z dużą głową.
   - A: te same klocki + skala całego modelu (ork 1,08, goblin 0,88) — każdy przedmiot pasuje (tak jest teraz).
   - B: własne klocki ras — bliżej rzutów, ale każdy przedmiot trzeba dopasować do każdej rasy.
   - Szczegóły: liczby proporcji w pkt 5; skala w grze to mnożnik modelu, więc ekwipunek rośnie razem z orkiem.
2. **Mag jest kotem — jak łączyć rasę z klasą Mag**
   - Kot-Mag ma własne ciało `kot`; rasy są ciałem `czlowiek`.
   - A: Mag dowolnej rasy na ciele `czlowiek` (nowe przedmioty Maga dla człowieka, kot zostaje maskotką).
   - B: klasa Mag bez wyboru rasy (zawsze kot).
   - Szczegóły: szata i kapelusz kota nie pasują na ciało `czlowiek` (`ubierz` zgłasza błąd typu ciała).
3. **Hełm a uszy, rogi i włosy**
   - Dziś hełm chowa włosy w całości, a uszy i rogi przechodzą przez hełm i kaptur.
   - A: zostawić (uszy i rogi na wierzchu, jak uszy kota przez rondo). B: hełm chowa też uszy i rogi (`ukrywa`).
   - C: hełmy z wycięciami na uszy i rogi dla ras.
   - Szczegóły: liczby w pkt 8; aureola wisi nad hełmem i niczego nie przecina.
4. **Wygląd Półboga**
   - Zależy od pytania 47 (D-080: mocniejsza rasa czy tylko wygląd).
   - Czy aureola i świecące oczy zostają przy każdym stroju i czy dodać poświatę postaci w grze?
5. **Goblin: pierwszy rzut czy wariant 2**
   - Zbudowany według `goblin.jpg` (polecenie prowadzącego etap); `goblin_wariant2.jpg` ma większą głowę
     i cieńsze ręce.
   - Zostaje pierwszy?
6. **Kolor spodenek orka**
   - Zamówienie: brązowe; rzut: wielokolorowe. Model ma brązowe `9C6B3C`.
   - Zostają brązowe czy inny kolor (brąz zlewa się z butami)?
7. **Buty bazowe: także dla człowieka?**
   - Rasy mają brązowe buty jako warstwę ciała; goły Rycerz i Zwiadowca są boso.
   - A: człowiek też dostaje buty. B: rasy boso jak człowiek (`buty=False`). C: zostaje różnica.
8. **Kolor skóry w przedmiotach**
   - Rękawice bez palców Zwiadowcy mają dłoń w kolorze skóry człowieka — na pięciu rasach wychodzi ludzka dłoń.
   - A: bryły „skóra” przedmiotu biorą kolor ciała przy zakładaniu. B: takie przedmioty nie zakrywają dłoni.
   - Szczegóły: dotyczy każdego przedmiotu, który rysuje gołą skórę (dekolty, palce); wymaga zmiany w `ekwipunek.py`.
9. **Spoczynek rasy na ekranie wyboru**
   - Klipy rasy to idle, chód i wiwat Rycerza (ręka jak do miecza).
   - Czy zrobić neutralny spoczynek bez broni dla selektora, czy rasa zawsze stoi w klipach wybranej klasy?
10. **Demon: z uszami czy bez**
    - Ikona wyboru rasy ma spiczaste uszy, rzut ich nie ma. Model jest bez uszu (polecenie prowadzącego etap).
11. **Ogon demona: sztywny czy ruchomy**
    - Dziś to sztywna łamana na biodrach: nie rusza się w klipach, przechodzi przez pas Zwiadowcy.
    - A: zostaje sztywny. B: własne kości ogona (jak u kota) — wtedy demon przestaje być zwykłym ciałem `czlowiek`.

## 10. Czego nie zrobiono i nie sprawdzono
- Roblox Studio: nic (ani rig z klocków, ani import siatek). `roblox_postac.py` nie zna modułów ras.
- Filmy klipów: nie renderowano (`--bez-filmow`); klipy są sprawdzone tylko liczbowo (równe Rycerzowi).
- Przenikanie w ruchu i kontrola liczbowa klipów (`--kontrola` jak u bohaterów): nie ma. Dotyczy zwłaszcza ogona
  demona przy nodze w chodzie i długich włosów przy ruchach głowy.
- Emisja oczu i aureoli w grze (pkt 6) i GLB w podglądzie 3D panelu: nie sprawdzane (GLB wczytano z powrotem
  tylko do Blendera).
- Ikony ras to rendery popiersia z biblioteki, nie ikony z `assets/processed/RaceSelect/`.
- `przedmioty.json`, `zestawienie.py` i panel nie wiedzą o rasach.

## 11. Następny etap (po przeglądzie)
- B: rasy w Studio (rig z klocków bez wgrywania), przymiarka w grze, skala rasy na modelu, świecenie.
