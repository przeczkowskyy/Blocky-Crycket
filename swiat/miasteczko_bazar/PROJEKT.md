# Krzywe Miasteczko jako ciasny bazar — projekt

*Status: **propozycja** (noc 16/17.11.2026), nie kanon i nic nie jest zbudowane w Studio. Wymagania: D-084 (do sklepu
się wchodzi, E na sprzedawcy otwiera okno 2D) i D-085 (miasto ciasne jak bazar) — obie zatwierdzone przez Karola
i Pawła — oraz D-041 (styl), D-042 (wrota lochów z kłódką), D-049 i D-063 (działka, Training Center), D-052 i D-060
(pety, jajka w biomach), D-067 (gildie po premierze), D-075 (pas biomów). Miasto robi Karol (odpowiedź na pytanie 49).*

> **W skrócie.** Bazar to pierwszy blok pasa świata: prostokąt pola gry **163 × 72 st** (szerokość 4,5 s biegu jak
> w Lesie) na osi Z −700, którego wschodni brzeg leży dokładnie na początku pasa Lasu (X 1066). Środkiem biegnie
> uliczka szerokości 28 st, po obu stronach budynek przy budynku. Gracz pojawia się na placu w środku, twarzą ku
> Lasowi: **po lewej portal do krain, po prawej Brama Twierdzy (działka)**, obok tablica z rankingiem. Do każdego
> sklepu biegnie się **2,7–4,4 s**, do portalu **1,6 s**. Pięć budynków ma wnętrza ze sprzedawcą za ladą, zagroda
> petów jest otwartym wybiegiem z opiekunką. Scena ma **4388 części** (cel 8000, limit 12 000). Kontrola: **0 błędów**.

Pliki: `uklad.json` (jedno źródło układu), `generuj.py` → `czesci.json` + `znaczniki.json`, `sprawdz.py`,
`podglad.py` → `podglad/*.jpg` i `ujecia.json`, moduły w `budynki/`, postacie w `postacie.py`, wspólne klocki
w `wspolne.py`. Polecenia: [README.md](README.md).

---

## 1. Położenie w świecie

- **Układ bazaru:** x wzdłuż pasa (+x na wschód, ku Lasowi), z w poprzek (+z na południe, czyli po prawej ręce gracza
  idącego do Lasu), y w górę. **Świat = (994 + x; y; −700 + z), bez obrotu** — ta sama oś i ten sam kierunek co pas
  Lasu (`swiat/biom_las/pas/plan_pasa.json`: świat = (1100 + u; y; −700 + v)).
- **Granice części:** x −112…72, z −90…90 (świat X 882…1066, Z −790…−610 — ta sama połowa szerokości z tłem co Las,
  90 st). **Pole gry:** x −95…68, z −36…36, zamknięte niewidzialnymi ścianami.
- **Nic nie nachodzi** na Krzywe Miasteczko (X −293…392), stary las, oba prototypy walki ani na pas Lasu (X ≥ 1066).
  Sprawdza to `sprawdz.py` na tych samych skrzynkach co `sprawdz_plan.py` Lasu. Dzisiejsze miasteczko
  (`Workspace/KrzyweMiasteczko`) zostaje nietknięte do porównania.
- **Baseplate — świadome odstępstwo.** Plan Lasu liczy płytę Baseplate (założone ±1024) jako zajętą. Między jej
  krawędzią (X 1024) a początkiem Lasu (X 1066) jest tylko 42 st, więc bazar przyłożony do Lasu musi stać na
  wschodnim końcu płyty (X 882–1024). Grunt bazaru ma wierzch 0,1 nad płytą i spód dokładnie na niej, więc nic nie
  migocze. Około 85 drobnych części (kamienie, beczki, kryształy Wrót lochów) jest wtopionych w grunt do 0,4 st
  głęboko, jak w dzisiejszym miasteczku. Decyzja ludzi: wybór 1.

## 2. Układ

```
   pn (−z)   TC      KARCZMA        PORTAL TABLICA  MAGICZNY  ZBROJOWNIA
           ┌──────┬────────────┬───────────┬──────────┬───────────┐
 placyk    │      │            │   PLAC    │          │           │  BRAMA
 studni  ══╪══════╧════════════╧═══(START)═╧══════════╧═══════════╪═ LEŚNA ═▶ Las
 (studnia) │ stragany  ZAGRODA  │  BRAMA    │ kiosk  WROTA LOCHÓW  │
           └────────────────────┴ TWIERDZY ─┴──────────────────────┘
   pd (+z)
```

- **Uliczka** z −14…14 (28 st = 1,75 s w poprzek), od placyku studni (x −70) do Bramy Leśnej (x 61). Środkowy pas
  8 st jest pusty na całej długości (sprawdzane). Fronty budynków stoją na linii z ±14, krzywo (obrót ±2–4°).
- **Plac startu** x −17…17: na północnym brzegu portal do krain, na południowym Brama Twierdzy, w kątach tablica
  z rankingiem i kąt z beczkami i ławką.
- **Placyk studni** na zachodnim końcu: studnia-pomnik z dzisiejszego miasteczka zamyka widok uliczki, wokół domy.
- **Kulisy** za rzędami (|z| 39–70): dwa rzędy domów tła, drzewa, schodkowe pagórki — od strony uliczki widać nad
  dachami sklepów miasto, które „ciągnie się dalej”, a z góry nie widać szarej płyty.
- Wszystkie miejsca z punktem E mają kwadrat 4 × 4 wolny od przeszkód. Wejścia do sklepów mają 11,8–14,8 st światła i 12,3–12,7 st wysokości, przejście Bramy Twierdzy 10 × 12, Wrót lochów 12 × 14, bramka zagrody 9,9.

| # | Miejsce (grupa w Studio) | Dlaczego jest w bazarze (sejf) | Środek (x; z), obrót | Obrys × wys. | Wejście | Kto stoi | Części | Bieg ze startu |
|---|---|---|---|---|---|---|---|---|
| 1 | Start (`Start`) | miejsce startu (sesja 16.11) | (−4; 3), patrzy na +x | krąg Ø 6,8 | — | — | 7 | 0 s |
| 2 | Portal do krain (`PortalKrain`) | D-085 „portal do biomów, np. po lewej”, D-075 | (0; −28), 0° | 22 × 12 × 26 | wir Ø 11,2 | — | 54 | **1,6 s** |
| 3 | Brama Twierdzy (`BramaTwierdzy`) | D-085 przejście na działkę; D-049, D-063 | (0; 27), 180° | 32 × 18 × 36 | 10 × 12 | — | 229 | 0,8 s |
| 4 | Tablica z rankingiem (`Tablica`) | D-085, po premierze panel gildii (D-067) | (−14,6; −19), 8° | 8 × 4 × 13 | — | — | 41 | 1,3 s |
| 5 | Karczma (`Karczma`) | kanon Karczma (Questy), Karczmarz; mistrz gier D-053 | (−32; −25), −2° | 26 × 22 × 37 | 14,8 × 12,7 | barman, mistrz gier | 296 | **3,0 s** / 2,7 s |
| 6 | Sklep magiczny (`SklepMagiczny`) | D-085 „zaraz obok magiczny”, D-084 mag-sklepikarz | (28,8; −24), −4° | 18 × 20 × 42 | 11,8 × 12,3 | mag | 237 | **3,0 s** |
| 7 | Zbrojownia (`Zbrojownia`) | D-085 sklep zbrojeniowy; pyt. 28: broń i pancerz w jednym | (50,4; −24), 3° | 20 × 20 × 36 | 12,8 × 12,3 | zbrojmistrz | 212 | **4,4 s** |
| 8 | Training Center (`TrainingCenter`) | D-063 jeden budynek, wybór mini-gry; D-085 mini-gry z jednego panelu | (−58,5; −24), 3° | 22 × 20 × 30 | 13,8 × 12,3 | trener | 213 | **4,3 s** |
| 9 | Zagroda petów (`ZagrodaPetow`) | D-085 zagroda (pety chodzą za bohaterem, można je odstawić) | (−32; 24), 182° | 26 × 20 × 17 | bramka 9,9 | opiekunka, pies, slime, smok | 219 | **2,7 s** |
| 10 | Wrota lochów (`BramaLochow`) | D-042 wrota z kłódką → hala portali | (44,5; 24), 180° | 30 × 20 × 36 | 12 × 14 | — | 271 | 3,2 s |
| 11 | Brama Leśna (`BramaLesna`) | D-075: miasto jest pierwszym blokiem pasa, za nim Las | (64,5; 0), −90° | 24 × 6 × 22 | wrota (zamknięte) | — | 39 | 4,0 s |
| 12 | Studnia-pomnik (`StudniaPomnik`) | punkt orientacyjny z dzisiejszego miasteczka | (−81; 0), 90° | 18 × 18 × 22 | — | — | 77 | 4,1 s |
| — | Stragany ×3, domy placyku ×4 | bazar, „budynek przy budynku” | wg `uklad.json` | 10 × 7, 16 × 14 | — | — | 75, 259 | — |

Czas = najkrótsza droga po siatce 0,5 st z omijaniem przeszkód (postać Ø 4), od startu do punktu E, bieg 16 st/s
(Roblox domyślnie; gra nie zmienia `WalkSpeed`). **Cel spełniony:** sklepy ≤ 5 s (najdalej zbrojownia 4,4 s), portal
≤ 6 s (1,6 s). Izochrony co 1 s są na planszy `podglad/plan_gora.jpg`.

**Czego nie ma i dlaczego:** areny PvP (notatka Arena jest propozycją, D-092 nie mówi, gdzie trafi), siedziby gildii
(D-067: po premierze — jej rolę przejmie tablica), kowala (D-049, D-051: w Twierdzy), koła fortuny (D-046 odrzucona,
w panelu „Krzywe Koło jest okej” bez decyzji o miejscu) i jajek (D-060: inkubatory stoją w biomach, w Lesie przy
przybyciu). Każde z nich można dostawić w kulisach albo zamiast straganu — wybór 7.

## 3. Wnętrza i kamera

Problem: w ciasnym wnętrzu kamera Roblox (12,5 st za postacią) wpada za ścianę, a Roblox przysuwa ją wtedy do głowy
gracza i widok skacze. **Wybór w tej propozycji: front sklepu od strony uliczki jest otwarty** — wąskie filary (2–6 st)
i nadproże, otwór **12–15 × 12,6–13 st**. Do tego:

- **wysoki strop:** parter 14–15 st (w starym miasteczku 11–12), strop na 13,5–14,5 z belkami; przechylone piętro
  i dach stoją nad stropem i nic z nich nie schodzi niżej (sprawdzone w generatorze: piętro jest uniesione tak, że jego
  najniższy punkt leży 0,05 nad ścianami);
- **głębokość tak dobrana, że kamera wypada w otworze:** sprzedawca stoi przy tylnej ścianie za ladą (wys. 3,35),
  gracz staje 2,3–3 st przed ladą (punkt E), więc kamera 12,5 za nim ląduje w otworze albo tuż przed nim, ok. 9 st nad
  ziemią — pod nadprożem (13) i markizą (spód ≥ 12,4);
- **markiza w pasy** nad otworem w kolorze kodu sklepu (dach), nie niżej niż 12,4 — gracz i kamera przechodzą pod nią;
- **wnętrze widać z uliczki:** sprzedawca jest widoczny przez otwór, więc sklep „zaprasza”.

Odrzucone na tym etapie: pełna ściana z drzwiami 8 × 10 (kamera w środku na pewno skacze), niższa ścianka od strony
kamery (przy otwartym froncie zbędna), przezroczyste ściany (niezgodne ze stylem). Jeśli w Studio kamera mimo to
przeszkadza, następny etap może dodać skrypt zbliżający kamerę we wnętrzu albo ustawić `CameraMaxZoomDistance` w strefie
sklepu (wybór 4).

## 4. Sprzedawcy i pety

Postacie z klocków (`postacie.py`), ok. 8 st przed skalą ×0,85, czyli ok. 6,8 st (gracz ok. 5,3) — głowa większa od
nóg jak w przykazaniach stylu. Każda postać to **Model** `<Budynek>/<Postać>` z niewidzialną częścią „Korzeń” pod
stopami (pierwsza część grupy, więc `tools/studio_buduj.py` robi z niej Model) i podgrupami **Glowa, Tulow, Rece,
Nogi** (+ Kapelusz, Rekwizyt). Kolizję mają tułów i nogi.

| Postać | Gdzie | Rozpoznawalna po | Okno (Paweł) |
|---|---|---|---|
| Barman (Karczmarz) | Karczma, za ladą | łysy, krótka ruda broda z bakami bez wąsów, czerwona opaska karczmy, złoty kolczyk, zielona koszula, skórzany fartuch, wielki brzuch, ręcznik, kufel (17.11.2026: własny projekt zamiast wąsacza w czerwieni i bieli) | zadania karczmy |
| Mistrz gier | Karczma, przy stole z planszą 3 × 3 i kostką | miękki beret ze złotą kostką, okrągłe okulary, bródka, kamizelka w szachownicę, siedzi (17.11.2026: bez cylindra, monokla i wąsika) | plansza (D-053) |
| Mag-sklepikarz | Sklep magiczny | spiczasty fioletowy kapelusz z gwiazdką, biała broda do pasa, kostur z kryształem | sklep magiczny |
| Zbrojmistrz | Zbrojownia | hełm z nosalem, ruda broda, skórzany fartuch, młot na ramieniu | broń i pancerz |
| Trener | Training Center, przy tablicy wyboru | niebieska opaska na pot (17.11.2026, była czerwona), gwizdek, podkoszulek, ręka wskazuje tablicę | wybór mini-gry |
| Opiekunka | Zagroda petów, przy korycie | słomkowy kapelusz, rude warkocze, morskie ogrodniczki, wiadro z kością | zagroda petów |
| Pies, slime, smok | w zagrodzie (+ slime na dachu budki) | pety z kanonu (Pety.md) | — |

Punkt E każdego sprzedawcy to dwie niewidzialne części w `<Budynek>/_Interakcja`: **„Punkt E <id>”** na posadzce, gdzie
staje gracz, i **„Podpowiedź E <id>”** na wysokości piersi sprzedawcy, gdzie skrypt wstawi `ProximityPrompt` (≤ 10 st
od głowy gracza — sprawdzane). Identyfikatory sklepów: `karczma`, `mistrz_gier`, `sklep_magiczny`, `zbrojownia`,
`training_center`, `zagroda_petow`.

## 5. Znaczniki (`znaczniki.json`)

Każdy znacznik ma `swiat` (świat Studio) i `bazar` (układ bazaru): **start** (punkt i kierunek patrzenia),
**sklepy** (stoisko, podpowiedź, grupa zaczepu, Model sprzedawcy, id sklepu, nazwa okna), **training_center**
(+ lista sześciu statystyk mini-gier), **zagroda** (punkt E + 6 miejsc na odstawione pety), **portal_krain** (punkt E
+ środek wiru i promień — gdyby portal działał przez dotyk), **dzialka** (Brama Twierdzy), **lochy** (punkt E + grupa
`BramaLochow/Blokada` z kłódką i łańcuchami do schowania po odblokowaniu), **tablica** (powierzchnia na SurfaceGui:
środek, normalna, rozmiar 6,4 × 4,8), **las** (Brama Leśna i punkt połączenia na brzegu X 1066), **wejscia** (światło
każdego wejścia — w tym wejście Training Center), liczba części na budynek.

## 6. Co wzięte z dzisiejszego miasteczka (import, nie kopia)

- `swiat/biblioteka/scena.py` (układy lokalne, format `czesci.json`), `paleta.py` (żadnych nowych kolorów),
  `zestaw.py`: okna, drzwi, dach-czapa, komin, latarnie, beczki, skrzynie, stragany, chorągwie, chorągiewki duetu,
  łaty, wypadnięte klocki, płotki, ławki, kwiaty, drzewa, chmury i domy tła (`dom_mieszkalny`, 22 sztuki).
- Całe moduły budynków: **Brama Twierdzy** (przejście na działkę), **Brama lochów** (+ nowa kłódka z łańcuchami według
  D-042) i **Studnia-pomnik**.
- Szyldy-rekwizyty: pieczony udziec karczmy (`karczma._udziec`), miecz w dachu i tarcza ze strzałami zbrojowni
  (`zbrojownia._miecz`, `_tarcza`), dach-kapelusz sklepu magicznego (`sklep_magiczny._kapelusz`, ×0,7).
- Kody kolorów dachów: karczma czerwień, zbrojownia granat ze złotą kalenicą, sklep fiolet, zagroda morski (kod petów),
  portal „brama” (kod wyjścia do krain), tablica zieleń gildii; Training Center dostał róż koła fortuny (koła na
  bazarze nie ma, a czerwień zostaje dla karczmy). Ścieżki-kody na bruku od startu do wejść też są z dzisiejszego
  rynku.

Nowe: wnętrza (`wspolne.skorupa`: posadzka, ściany z otworem, strop z belkami, uniesione piętro, szachulec, banery),
lady, półki, lampy, markizy, girlandy, postacie, zagroda, portal, tablica, Brama Leśna, rysownik podglądów i siatka
chodzenia.

**Odstępstwa od przykazań stylu:** parter 14–15 zamiast 11–12 (wnętrze i kamera), front parteru otwarty zamiast drzwi
8 × 10 (D-084), budynki 18–26 szerokie zamiast 24–46 (ciasny bazar). Dolne 10 st ścian zostaje pionowe, krzywe są
piętra i dachy.

## 7. Budżet części

| Grupa | Części |
|---|---|
| Sklepy z wnętrzami i sprzedawcami: karczma 296, sklep magiczny 237, Training Center 213, zbrojownia 212, zagroda 219 | 1177 |
| Bramy z dzisiejszego miasteczka: lochy 271, Twierdza 229, studnia 77 | 577 |
| Portal 54, tablica 41, Brama Leśna 39, stragany 75, start 7 | 216 |
| Domy placyku 259, domy tła 1149 | 1408 |
| Bruk 292, ścieżki-kody 57, teren 2, mury i łączniki 88, rekwizyty 296, drzewa, pagórki i chmury 271, niewidzialne ściany 4 | 1010 |
| **Razem** | **4388** (cel ok. 8000, limit 12 000) |

Kule 25, walce 383, Neon 85, przezroczyste 0, z kolizją 19%, SmoothPlastic 85%. Bazar jest mały i gęsty, więc do celu
8000 brakuje ok. 3600 części — świadomie: to miejsce, w którym gracze spędzają najwięcej czasu, także na telefonie.
Zapas można wydać w następnym etapie na szczegóły wnętrz i życie uliczki, gdy pomiar na telefonie pokaże, ile wolno.

## 8. Wybory do decyzji

**1. Bazar na końcu płyty Baseplate — zostawić płytę?**
- Bazar stoi na płycie (X 882–1024), grunt 0,1 nad nią — działa od razu.
- Przyciąć albo usunąć Baseplate (decyzja w Studio, cudza instancja) — czystszy świat, ale prototypy walki stoją na niej.
- Przesunąć bazar za płytę — wtedy nie styka się z Lasem (za mało miejsca).

**2. Brama Leśna: przejście pieszo do Lasu czy tylko E?**
- Tylko E przed zamkniętymi wrotami (propozycja) — Las ma za Polaną skały i niewidzialną ścianę.
- Otworzyć przejście: generator Lasu musi zrobić bramę w ścianie zamykającej (u −34…0).

**3. Training Center w mieście czy na działce?**
- W mieście (propozycja, D-085 „mini-gry z jednego panelu”) — 4,3 s od startu.
- Na działce (D-049 tak go wymienia) — w mieście zostaje tylko wejście/teleport.

**4. Wnętrza: otwarty front czy pełne drzwi?**
- Otwarty front 12–15 st (propozycja) — kamera bez skoków, sprzedawca widoczny z uliczki.
- Drzwi 8 × 10 i skrypt zbliżający kamerę we wnętrzu — bardziej „dom”, więcej pracy i ryzyko na telefonie.

**5. Portal do krain: dotyk czy E?**
- E przed portalem (propozycja) — spójne ze sklepami, nie teleportuje przypadkiem.
- Wejście w wir — szybciej; znacznik `portal_krain_wir` ma środek i promień.

**6. Tablica z rankingiem: tylko podgląd czy też E?**
- Tylko SurfaceGui na desce (najwyższy poziom, zdolności).
- Plus E → pełny ranking w oknie 2D (punkt E już jest).

**7. Czego jeszcze brakuje w mieście?**
- Krzywe Koło, arena PvP, inkubator jajek w mieście — każde może zastąpić stragan albo stanąć w kulisach.
- Zostawić bez nich (propozycja) — mniej chodzenia, kanon ich tu nie wymaga.

**8. Stare Krzywe Miasteczko po akceptacji bazaru?**
- Usunąć `Workspace/KrzyweMiasteczko` (5259 części mniej).
- Zostawić jako osobną strefę do zwiedzania.

Szczegóły: wybory 1 i 2 dotykają planu Lasu (`swiat/biom_las/pas/`), którego ta praca nie zmienia. Ścieżki-kody na
bruku (kolorowe kreski od startu do wejść) i girlandy to dodatki stylu — jeśli w Studio będzie za kolorowo, można je
wyłączyć w `uklad.json` (`kody`, `girlandy`).

## 9. Czego nie sprawdzono

- **Nic nie było budowane ani oglądane w Roblox Studio** (zakaz pracy ze Studio w tym etapie). Podglądy w `podglad/`
  rysuje lekki rysownik z klocków (Pillow): bez faktur, cieni rzucanych, świecenia Neonu i oświetlenia miejsca. To nie
  jest wygląd z Roblox.
- Kamera we wnętrzach, kolizje, chodzenie postacią i schodki (progi 0,3, stopnie portalu 0,5) — liczone na siatce,
  niesprawdzone w trybie Play. Czasy biegu to geometria, nie pomiar.
- Telefon: wydajność 4388 części i czytelność sprzedawców i szyldów na małym ekranie.
- Rozmiar płyty Baseplate (±1024) jest założony, jak w planie Lasu.
- Słońce z pn.-zach. wzięte z dokumentacji starego miasteczka: fronty rzędu północnego (karczma, sklepy) stoją w cieniu
  — mają jasne ściany i Neon w oknach, ale ocenić to trzeba na zrzutach ze Studio.
- Postacie są z klocków; D-065 mówi, że postacie i pety projektuje Karol w Blenderze — sprzedawców można później
  zastąpić siatkami, Modele i punkty E zostają.
