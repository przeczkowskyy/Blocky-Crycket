# Biom Las „Bór Pod Ukłonem” — projekt mapy (kontrakt dla budowniczych), wersja 2

*Status: **propozycja** (15.11.2026), nie kanon — kanonem może go uczynić tylko Karol albo Paweł. Wzór formy: `swiat/krzywe_miasteczko/PROJEKT.md`. Ustalenia, których się trzymamy: D-061 (osiem biomów, las pierwszy; strażnik biomu i inkubatory), D-032 (trudność lokalna, las od początku), D-034 (strefy z odradzającymi się potworami, E, walka), D-035, D-059 i D-060 (walki petów, inkubatory), D-064 (mapa teleportacji z pinami), D-068 (animacja przy każdej walce), D-041 i D-042 (styl Krzywego Miasteczka, wrota z kłódką). Notatka w sejfie: `B&C/Gra/Biom Las.md`.*

> **W skrócie.** Las ma 1000 × 1000 studów (gra w 860 × 860, ok. 3,4 raza szerzej niż miasteczko). Pośrodku rośnie **Stary Ukłon** — drzewo wysokie na ok. 100, które kłania się na wschód i widać je z całego lasu. Sześć podbiomów: **na południu nisko, jasno i łatwo, na północy wysoko i trudno**. Kręta Struga płynie od wodospadu do stawu przy wejściu. 24 lokacje rozpoznaje się po wielkim rekwizycie. Po lesie chodzi 64 zwykłych potworów w 16 strefach (do 86 przy tłoku), 4 patrole wędrowne, rzadki troll i strażnik biomu; walkę zawsze zaczyna gracz klawiszem E. Od bramy do Ukłonu biegnie się 26 s, do Kręgu strażnika 66 s. **Mapa jest zbudowana z klocków** (`generuj.py` → `czesci.json`, 13 353 części z 25 000) i obejrzana w Blenderze (`podglad/`); w Studio jeszcze jej nie ma.

**Pliki:** `uklad.json` (obrys, podbiomy, lokacje, ścieżki, woda, **teren**, strefy spokoju, piny), `potwory.json` (strefy, węzły walki, domy, patrole, troll, strażnik), `ujecia.json` (ujęcia kontrolne w układzie lasu), `paleta.py`, `geo.py` (geometria i model wysokości — wspólny dla wszystkiego), `wezly.py` (węzły walki i domy z maski terenu), `sprawdz.py` (kontrola), `generuj.py` + `teren.py`, `rosliny.py`, `skaly.py`, `lokacje/*.py` (budowa), wyniki `czesci.json`, `znaczniki.json`, `ujecia_swiat.json`, `plan.py` → `podglad/plan.png` i `plan_telefon.png`. Jak tego używać: `README.md`.

**Sprawdzone skryptem** (`python -B swiat/biom_las/sprawdz.py`: 0 błędów, 2 ostrzeżenia, rozdz. 13) i generatorem (`generuj.py`: place walki czyste na prawdziwych częściach, kontrola biblioteki 0 ostrzeżeń).

---

## 0. Co się zmieniło w wersji 2 (po krytyce)

Każda uwaga krytyka i co z nią zrobiłem:

| # | Uwaga | Decyzja |
|---|---|---|
| 1 (wysoka) | Wielokąt dna wąwozu przecina sam siebie; ścieżka i troll idą przez ścianę | **Przyjęte, teren przebudowany.** Wąwóz to teraz **rynna między półkami**: dno = poziom łąki (0), ściany = brzegi prostych wielokątów półek (y 12) wyliczonych z osi dwóch rynien (północna do tamy, Ujście na łąkę). Wszystkie wielokąty terenu są proste (test). Nowy test: **żadnego urwiska na drodze** — wysokość wzdłuż każdej ścieżki, przejść między węzłami, trasy trolla i patroli zmienia się najwyżej o 0,6 na studzie; na wyższe poziomy prowadzą tylko rampy. |
| 2 | Węzły walki przy Kapeluszu, Skale, chatkach, ścianach | **Przyjęte.** Węzły liczy `wezly.py` z maski (grunt ±0,5 w r 15,5, woda ≥ 12, rdzenie lokacji ≥ 12, strefy spokoju + smycz); `generuj.py` sprawdza je jeszcze **na prawdziwych częściach** (nic od 1,5 do 18 w r 12) i rozsiew omija place. Chatki stoją w domach, ≥ 35 od węzłów. W labiryncie walka tylko na polance środka (r 17) i na placach przed wejściem i wyjściem. |
| 3 | Gracz w strefie blokuje odradzanie | **Przyjęte.** 2–3 domy na strefę, 35–50 od węzłów, blokada 18. Czwarta strefa Łąki (z16, poz. 1–2). Przepływ policzony w `sprawdz.py`: 8 graczy — do 46 walk/min przy popycie ok. 20, 20 graczy — do 71 przy ok. 50. |
| 4 | Slime’y 2–3 i 6–7 dzieli 49 st bez progu | **Przyjęte.** z03 przeniesiona na wschód Oczka (brzegi ok. 150 st od z12). W Wąwozie **Bursztynowy Slime** (ten sam model, kolor `zloto`, na ciemnym błocie) — wybór dla ludzi nr 6. Przy wylocie Ujścia **próg**: łuk z dwóch żeber, czaszka-klocek, drogowskaz i maczuga wbita w ziemię; grunt zmienia się z trawy na ziemię. Trasa trolla nie przechodzi już przez z03; przez z01 (Oczko) **zostaje celowo** — troll schodzi do wodopoju, slime’y chowają się wtedy do wody, a na łące troll nie ma E. |
| 5 | „Chodzące potwory” to 9% mapy w kółkach | **Przyjęte częściowo.** 4 patrole wędrowne po ścieżkach (wataha na Wilczym Trakcie, karawana slime’ów na Dróżce Paproci, muchomorniki z koszami na Dróżce Kapeluszowej, **wataha z półki** w Wąwozie, która zeskakuje graczowi na drogę). Wyróżniki podbiomów: Bursztynowy Slime i wataha z półki (Wąwóz). Więcej gatunków = więcej modeli → wybór dla ludzi nr 6. Pokrycie ścieżek potworami ≤ 40 st: 68% (było 64%). |
| 6 | Streaming 256 zabierze dalekie widoki | **Przyjęte jako plan na krok Studio.** `znaczniki.json` wymienia grupy **stale wczytane** (`Punkty/*` — sylwetki 7 punktów orientacyjnych, ModelStreamingMode = Persistent) i grupy **z niskim detalem** (kępy `*/Las_i_j`, mur, tło — LevelOfDetail = StreamingMesh). Pomiar z Ławki i z bramy przy włączonym streamingu jest w kroku 1 budowy w Studio. Mgła — decyzja człowieka (wybór nr 7). |
| 7 | Łyse plamy, mur 1 część na 4 st | **Przyjęte częściowo.** Rozsiew sadzi ok. 85% drzew w pasie 45 st od ścieżek; Ostępy mają ok. 300 sosen (odstęp ok. 10–12) — z góry to ciemny bór. Mur to skały-kulisy co ok. 24 st i dwa rzędy kulis-drzew, plus niewidzialna ściana. Pusty róg pn.-wsch. zajęło jezioro, wschodnia półka dostała ścieżkę i patrol. Mapa ma 13,4 tys. części — **rezerwa ok. 11,6 tys.** na zagęszczenie po pomiarze na telefonie. |
| 8 | Skarpa 8, uskok 8, brak wysokości Korony i Ostępów | **Przyjęte.** Poziomy: 0 (łąka, Kapeluszowo, Ostępy, dno rynien, Rozstaj), kopce (polana 4, Pagórek 6), 12 (półki wąwozu, korona tamy, taras dolny Korony), 22 (taras górny), 32 (płaskowyż Kręgu i Grań). Uskoki 10–12 albo zbocze; jezioro 11 (dno 9,5). Ostępy **uproszczone do 0** (bez progów 2 → 8) — groźniej robi się przez ciemny bór i ścianę Grani 32. Test pasma 6,5–9 na siatce co 2 st: 0 miejsc. |
| 9 | Strażnik po 10 wygranych ze slime’ami, dwóch kolosów w Kręgu | **Przyjęte.** Liczą się wygrane z potworami nie niższymi niż (poziom gracza − 2). Propozycja: walka ze strażnikiem w osobnej przestrzeni (jak wnętrze Dziupli); wariant: jeden Krąg i kolejka. Wybór nr 1. |
| 10 | Slime’a nie widać na trawie i kamieniu | **Przyjęte.** Przykazanie 13: potwór na gruncie swojej strefy ΔL* ≥ 20 albo podkładka. Pod strefami Łąki ciemniejsza „wydeptana” trawa (`runo`), pod muchomornikami polanki mchu, Bursztynowy Slime na ciemnym błocie. Test w `sprawdz.py` (16 stref OK) i ujęcie `l16_slime_z_60`. |
| 11 | Trasy nie mieszczą potworów z odstępem 25 | **Przyjęte.** Pojemność = obwód pętli węzłów / 25, wataha liczy się jako jeden; „max” obniżone tam, gdzie trzeba. Siedzące wilki ≥ 14 od walki (w zachowaniu). |
| 12 | Jezioro 71 st od tamy, niedostępne | **Przyjęte.** Jezioro przylega do tylnej ściany tamy, ma nieregularny brzeg (do muru lasu), brzeg dostępny z korony tamy i z półki (Brzeg Jeziora). |
| 13 | Labirynt przecina strugę | **Przyjęte.** Labirynt r 45, przesunięty na (−200; −262); woda 32 st od obrysu z murami; test w `sprawdz.py`. |
| 14 | Plan: czasy to długości ścieżek, brak G, telefon | **Przyjęte.** Na planie nazwy 8 najważniejszych miejsc z czasem „od bramy”, znak G obok Kręgu, podpis strzałki „przejście z Bramy Miejskiej”, druga wersja `plan_telefon.png` (sama mapa). |
| 15 | Struga z koryta = cięcie gruntu | **Przyjęte.** Struga to cienka tafla na gruncie (0,18) z ciemnym brzegiem, kamieniami i trzciną; nic nie wycinamy. Stawy też (tafla + ciemniejszy środek). |
| 16 | Wrota Bagna zakładają sąsiedztwo biomów | **Przyjęte.** Wrota to rekwizyt (kłódka, mgła); decyzja o przejściu: wybór nr 5. |

Inne zmiany wersji 2: Stary Ukłon ok. 100 nad polaną (czapa z kęp, Bocianie Gniazdo na jej wierzchu); trzy rampy serpentyny; Schody Głazów to rampa wzdłuż zachodniej ściany rynny na koronę tamy; nowe ścieżki (Półka Zachodnia, Półka Wschodnia, Dróżka Słoneczna, Dróżka Kępek, Dróżka Chatek, Brzeg Jeziora).

### 0a. Przegląd świeżym okiem (15.11, po wersji 2)

Przegląd jak dyrektor artystyczny i jak gracz, który pierwszy raz wchodzi do lasu: wszystkie 20 ujęć, rzut z góry obok
planu, miasteczka i KeyArtu; 3 rundy poprawek z podglądem. Co poprawione:

| Co było źle (podgląd) | Poprawka (plik) |
|---|---|
| Kryształ Kręgu ok. 58 n.p.m. — z Rozstaju i Łąki niewidoczny, Korona nie ma znaku z daleka | filar z łupku i iglica kryształu do ok. 95 n.p.m., dwa odłamki (`lokacje/korona.py`); widać go z Rozstaju nad brzózkami |
| Menhiry i filar beżowe jak posadzka — Krąg czytał się jak stos pudeł | menhiry `dach_dom_lupek` (Slate) z czapami mchu |
| Ściany labiryntu: gładkie fioletowe bloki | garbaty wierzch z kęp liści (ciemna zieleń i jaśniejszy fiolet), jagody, kolce na licach (`lokacje/ostepy.py`) |
| Ostępy z oczu gracza miały jasne runo jak Łąka | ciemne igliwie (`runo_ciemne`, 0,12 nad gruntem) pod sosnami; place walki zostają na jaśniejszym runie (`generuj.py`) |
| Dolny segment pnia Ukłonu: prosty blok | stopa z czterech przypór (kliny), pasy kory (`lokacje/stary_uklon.py`) |
| Jama wilka z półki: fioletowe pudło z rogami | garby liści na wierzchu, kij nad otworem (`lokacje/wspolne.py`) |
| Koniec szlaku przy bramie wystawał trójkątem na dróżkę | okrągłe czapki na końcach ścieżek, bez duplikatów (`teren.py`) |
| Pusty, ciemny pierwszy plan z Ławki | niskie kwiaty i dwa płaskie głazy po bokach korytarza widoku |
| Ujęcie `l11_rozstaj`: sowa zasłaniała cel | kamera przesunięta o 14 w bok (`ujecia.json`) |

Nadal słabe (nie poprawione w tym przeglądzie): jasne gładkie ściany rynien Wąwozu i rant półki (mało faktury), duże płaskie
lica labiryntu z bliska, jasne runo Ostępów między pniami, płaskie jezioro, podkładki stref jak koła z kół, brak mgły.

---

## 1. Idea i konwencje

**Idea w trzech zdaniach.** Las to Krzywe Miasteczko przeniesione na przyrodę: pnie z przechylonych segmentów, korony jak czapy, kanciaste skały. Krainę da się odczytać z widoku: im wyżej i dalej na północ, tym groźniej, a z każdego miejsca widać Stary Ukłon albo zielony kryształ Kręgu. Każdy potwór ma dom (staw, kałuża galarety, chatka-grzyb, jama w jeżynach, szpara w głazach, legowisko pod tamą).

**Konwencje.** 1 jednostka = 1 stud; Y w górę; **północ lasu = −Z** układu lasu; środek Ukłonu = (0; 0); y = 0 to łąka. Obroty jak w `scena.py`. Wszystkie współrzędne w plikach są w **układzie lasu**; `czesci.json` jest już w układzie świata Studio (rozdz. 2).

---

## 2. Rozmiar, położenie i teren

| Co | Wartość |
|---|---|
| Płyta gruntu | 1400 × 1400 z wierzchem na 0 (pod lasem i tłem) |
| Obszar gry | 860 × 860 (±430) |
| Mur Pni | pas 436–466: skały-kulisy (16–30 wys.) co ok. 24 i dwa rzędy kulis-drzew (bez kolizji); niewidzialna ściana na 470; nad płaskowyżem pod Ławką i nad jeziorem tylko niskie skały; przerwa we Wrotach Bagna (ściana i tak zatrzymuje) |
| Tło | rząd kulis 482–528, 22 wzgórza z trzech klocków na r 640 (z przerwą na północy), atrapa miasteczka na (40; −720), 12 chmur |
| Podbiomy | Łąka 19%, Kapeluszowo 16%, Serce 8%, Ostępy 22%, Wąwóz 23%, Korona 12% |

**Model wysokości** (`uklad.json` → `teren`, liczy go `geo.Teren`; ta sama funkcja steruje budową, kontrolą i planem):

| Element | Wysokość | Jak zbudowany |
|---|---|---|
| płyta | 0 | jeden blok 1400 × 2 × 1400 + plamy podbiomów z klinów |
| polana Ukłonu | 4 (walec r 70, zbocze 1 : 10 do r 110) | walec + 28 klinów |
| Pagórek | 6 (r 20, zbocze 1 : 4 do r 44) | walec + 18 klinów |
| półki wąwozu: Zachodnia, Wschodnia, Wyspa Sosen | 12 | proste wielokąty → pryzmaty z klinów (kolor skały) + cienki wierzch |
| korona tamy | 12 | czworokąt w poprzek końca rynny północnej |
| dno jeziora | 9,5 (lustro 11) | wielokąt od tamy do muru |
| Korona: taras dolny / górny / płaskowyż | 12 / 22 / 32 | nachodzące na siebie wielokąty (wyższy stoi na niższym) |
| Grań nad Ostępami | 32 | wielokąt z wąską zatoką na sekretną rampę za wodospadem |
| rynny wąwozu | 0 | przerwy między półkami (oś północna szer. 54, Ujście szer. 52) |

**Rampy** (jedyne wejścia na wyższe poziomy; wysoki koniec dotyka krawędzi): serpentyna 0 → 12 (1 : 3,9), 12 → 22 (1 : 5), 22 → 32 (1 : 5,2); Trakt 12 → 22 i 22 → 32; **Schody Głazów** 0 → 12 wzdłuż zachodniej ściany rynny na koronę tamy (1 : 4,2); sekretna rampa za wodospadem 0 → 32 (22°). Uskoki między poziomami: 10–12 (albo zbocze kopca) — **nic w paśmie 6,5–9**. Krawędzie poziomów obłożone skałami (rant ≤ 1,1 nad wierzchem, żeby nie psuć placów walki).

**Położenie w Studio.** Kontener **`Workspace/BiomLas`**, środek w świecie **(0; 0; −2000)**, **obrót 180° wokół pionu**: punkt lasu (x; y; z) → świat **(−x; y; −2000 − z)**. `generuj.py` zapisuje części już w świecie. Miasteczko stoi w (0; 0; −700) z tłem do z ≈ −900; las zaczyna się na z ≈ −1300 (płyta) — ok. 400 studów przerwy. Przed budową sprawdzić, czy to miejsce jest puste.

**Dlaczego obrót.** Słońce miejsca świeci z pn.-zach. świata; w obróconym lesie świeci z **pd.-wsch.** — gracz idzie na północ plecami do słońca, fronty lokacji są oświetlone. Podglądy w Blenderze robimy w układzie świata (`ujecia_swiat.json`), więc słońce jest takie jak w Studio; rzut z góry trzeba obrócić o 180°, żeby północ lasu była u góry.

**Wejście z miasteczka.** E przy Bramie Miejskiej → zaciemnienie → gracz stoi w (200; 400) i patrzy na Ukłon. Powrót: Kamień Powrotu przy Bramie Pniaków (E) albo mapa.

**Czasy biegu od bramy** (po ścieżkach, 16 st/s): Oczko 5 s, Wóz 7 s, Most 15 s, Pagórek 15 s, Wyschnięta Kałuża 22 s, **Ukłon 26 s**, Gniazdo i Dziupla 29 s, Kapelusz 33 s, Gardziel 36 s, Schody Głazów 40 s, Krąg Zarodników 41 s, Rozstaj 42 s, Tama 44 s, Wilcza Skała 49 s, Jezioro 52 s, Labirynt i Wrota Bagna 61 s, Ławka 65 s, **Kamienny Krąg 66 s**, Szumiący Próg 81 s.

---

## 3. Podbiomy

| Podbiom | Rola | Wygląd | Potwory i poziomy |
|---|---|---|---|
| **Łąka Galaretek** (pd.) | wejście, samouczek | jasna trawa, okrągłe drzewa, krzaki, kwiaty, staw z pomostem; ciemniejsze „wydeptane” plamy pod strefami | Leśny Slime 1–3 (4 strefy, 19 naraz), karawana slime’ów |
| **Kapeluszowo** (pd.-zach.) | wioska potworów | grzyby-olbrzymy (czerwone w kropki, brązowe, kremowe) 8–22 na ciemnym runie, polanki mchu, dęby, paprocie | Muchomornik 3–5, slime 3–4, muchomorniki z koszami |
| **Serce Boru** (środek) | spokój: inkubatory, walki petów, loch, odrodzenie | polana na 4 z pierścieniem ścieżki, korzenie-ławki, lampiony, rdzawo-miodowa czapa Ukłonu | brak |
| **Cierniste Ostępy** (zach.) | pierwsze groźne miejsce, sekrety | gęsty ciemny bór sosnowy, kępy jeżyn, łupkowe głazy; nad lasem Wilcza Skała, na północy łupkowa Grań 32 z wodospadem | Cierniowy Wilk 5–7, wataha na Wilczym Trakcie |
| **Suchy Wąwóz** (wsch.) | średnio zaawansowani, dom trolla | dwie rynny z ziemi między piaskowymi półkami (12) z sosnami, ściany z ciepłego kamienia, tama z głazów, jezioro w rogu | wilk 7–8 (dno, półka), Bursztynowy Slime 6–7, wataha z półki, Leśny Troll 8–9 |
| **Korona Gaju** (pn.) | szczyt i cel | trzy poziomy (12, 22, 32) z kamiennymi uskokami, białe brzózki, głazy-pięści, Kamienny Krąg z zielonym kryształem | Muchomornik 8–9, wilk 9–10, Strażnik Gaju 10 |

---

## 4. Lokacje

Numery jak na planie. „Pkt” = punkt orientacyjny (główne bryły w grupie `Punkty/<Nazwa>`, w Studio stale wczytane). Moduł = plik w `lokacje/`.

| # | Lokacja | (x; z), y | Co stoi | Moduł |
|---|---|---|---|---|
| 1 | Brama Pniaków (pkt) | (200; 418), 0 | dwa pnie 22 kłaniające się sobie, lampion na linie, chorągiewki duetu, Kamień Powrotu (E), ognisko pinu, drogowskaz | `laka.py` |
| 2 | Oczko Galaretek | (250; 300), 0 | staw r 28 (tafla), pomost od zachodu z wędką i galaretowym spławikiem, grzybienie, kamienie brodu przy ujściu strugi | `laka.py` |
| 3 | Most Rechotek | (60; 215), 0 | garbaty most z poręczami, kamienna żaba z otwartym pyskiem | `laka.py` |
| 4 | Przewrócony Wóz | (110; 345), 0 | wóz na boku, koło, skrzynie, jabłka, słonecznik z piasty (E: zadania) | `laka.py` |
| 5 | Pagórek Wypadniętego Klocka (pkt) | (370; 240), 6 | złoty klocek 12 × 6 × 6 pod 25°, czerwona strzałka w niebo | `laka.py` |
| 6 | Kładka z Pnia | (−98; 95), 0 | pień z mchem i czerwonymi kropkami przez strugę, grzybki | `kapeluszowo.py` |
| 7 | Wielki Kapelusz (pkt) | (−290; 270), 0 | muchomor ok. 45 (trzon w kontrze, kapelusz r 17), spirala kapeluszy-stopni na wierzch ze skrzynią (E), lampiony zarodników, ognisko pinu | `kapeluszowo.py` |
| 8 | Krąg Zarodników | (−370; 160), 0 | koło 9 grzybów, głaz z mchem, świecące zarodniki (E: zadania) | `kapeluszowo.py` |
| 9 | Stary Ukłon (pkt) | (0; 0), 4 | pień z 3 segmentów pochylony na wschód, 7 korzeni-ławek, 19 konarów-stopni, czapa z kęp, złote owoce, świetliki, ognisko pinu | `stary_uklon.py` |
| 10 | Bocianie Gniazdo | na wierzchu czapy, y ok. 97 | gniazdo z belek i złote jajo | `stary_uklon.py` |
| 11 | Gniazdo w Korzeniach | (−62; 15), 4 | dwa jaja (zielone w liście, brązowe w kropki) z kapslami, dwa punkty E (inkubatory) | `serce.py` |
| 12 | Dziupla Turniejowa | (85; 55), ok. 1 | leżący pień Ø 16 × 52 wzdłuż poziomicy, ciemne otwory, girlanda, tron z szyszki (E) | `serce.py` |
| 13 | Korzenna Gardziel | (75; −80), 0 | talerz korzeni, zwalony pień, paszcza z zielonym blaskiem, wrota z kłódką (E) | `serce.py` |
| 14 | Wilcza Skała (pkt) | (−300; −50), 0 | łupkowa iglica ok. 50 z uchem, jasne ranty, bursztynowe oczy, 9 półek na szczyt, ognisko pinu | `ostepy.py` |
| 15 | Jeżynowy Labirynt | (−200; −262), 0 | ściany jeżyn 10–11,5 wycięte wzdłuż korytarza 14, polanka r 17, skrzynia i kości (E) | `ostepy.py` |
| 16 | Szumiący Próg (pkt) | (−345; −388), 0 | wodospad 32 z Grani przed sekretną szczeliną, misa, mgiełka, tęcza z 3 łuków, niebieski klocek w wodzie | `ostepy.py` |
| 17 | Wrota Bagna | (−418; −180), 0 | pale z mchem, belka, łańcuch, kłódka, mgła za bramą | `ostepy.py` |
| 18 | Schody Głazów | (266; −150), 0 | rampa na koronę tamy, głazy-stopnie od strony rynny, bruzda po maczudze, półki na ścianie | `wawoz.py` |
| 19 | Wyschnięta Kałuża | (342; 105), 0 | ciemne popękane błoto (podkładka strefy), kałuża, szkielet łódki | `wawoz.py` |
| 20 | Trollowa Tama (pkt) | (248; −196), 12 | głazy czoła, wysokie głazy na końcach (do ok. 29 nad dnem), legowisko z kotłem, ukradziony szyld, kości, strużka, ognisko pinu na tarasie | `wawoz.py` |
| 21 | Jezioro za Tamą | (330; −345), 11 | tafla od tamy do muru, trzcina, wysepka z sosną, złota kaczka | `wawoz.py`, `teren.py` |
| 22 | Rozstaj pod Sową | (0; −150), 0 | słup z sową, 5 ramion z rekwizytami podbiomów, lampion | `korona.py` |
| 23 | Kamienny Krąg Korony (pkt) | (0; −385), 32 | 7 łupkowych menhirów z mchem, filar z zieloną iglicą kryształu (ok. 63 nad płaskowyżem, ok. 95 n.p.m.), posadzka, ognisko pinu | `korona.py` |
| 24 | Ławka z Widokiem | (62; −424), 32 | dwa pniaki, deska, luneta na trójnogu w stronę atrapy miasteczka; korytarz widoku bez drzew | `korona.py` |

Poza listą: drogowskazy na 12 rozwidleniach (`generuj.py`), lampiony polany, próg przy Ujściu (`wawoz.py`), domy potworów i podkładki stref (`generuj.py` z `potwory.json`).

---

## 5. Ścieżki i przeszkody

| Rodzaj | Szer. | Nawierzchnia (wierzch nad gruntem) | Gdzie |
|---|---|---|---|
| Szlak główny | 12 | `bruk` 0,32, krawężnik `tusz` po obu stronach, kamień-kod co 20 w kolorze celu | Szlak Ukłonu (pd. i pn. z serpentyną), Wilczy Trakt, Trakt Wąwozem |
| Dróżka | 8 | `ziemia` 0,26, krawężnik tylko na Łące | pozostałe (19 dróżek) |
| Pierścień polany | 10 | `ziemia` 0,30 | wokół Ukłonu, r 50 |
| Korytarz labiryntu | 14 | `ziemia` | w labiryncie |
| Sekretna | 4 | `kamien_cieply` | szczelina za wodospadem i Grań do zachodniego boku Kręgu |

Razem 6,6 tys. studów, jedna sieć (123 węzły), **zero urwisk na drodze**. Różne wysokości nawierzchni rodzajów ścieżek usuwają migotanie na skrzyżowaniach. Pętle: południowa (Szlak + Kapeluszowa + Paproci), Dróżka Kępek (skrót Szlak → Paproci), zachodnia (Wilczy Trakt + Sowia), wschodnia (Trakt + Ujście), Półka Zachodnia i Wschodnia od korony tamy.

**Przeszkody:** struga do przejścia wszędzie (tafla bez kolizji); urwiska poziomów ≥ 10; ściany labiryntu 10–11,5; jezioro bez kolizji (dno 1,5 pod lustrem); Mur Pni i niewidzialna ściana. Prześwit ≥ 16 w rynnach i na rampach (troll 12,7 szer.). Drzewa nie stoją bliżej osi ścieżki niż pół szerokości + ok. 0,9 promienia korony.

---

## 6. Potwory w ruchu

Dane: `potwory.json` (projekt) i `znaczniki.json` (wynik generatora: węzły z wysokością, domy, patrole, troll, strażnik, punkty E, piny). Rozmiary modeli: slime 2,7, wilk 4,4 (dł. 7,7), muchomornik 3,6, troll 9,9, strażnik 14,5.

**Zasady wspólne.**
- **Dom → terytorium.** Każda strefa ma 2–3 domy (kałuża galarety, chatka-grzyb, jama w jeżynach, szpara w głazach; slime’y Oczka wyskakują z wody) **35–50 st od węzłów walki**. Nowy potwór wychodzi z wolnego domu (żaden gracz bliżej niż **18**) i idzie do najbliższego węzła. Smycz 10 poza terytorium, nigdy do strefy spokoju.
- **Węzeł = miejsce walki.** Grunt ±0,5 w r 15,5, nic od 1,5 do 18 w r 12 (sprawdzone na częściach), woda ≥ 12 (Oczko ≥ 10). Węzły tworzą pętlę; przejścia między nimi bez urwisk.
- **Pojemność** = obwód pętli / 25 (wataha = jeden). Naraz = liczba przy ok. 8 graczach; więcej graczy → do max; odradzanie = baza / (1 + 0,15 × (gracze w strefie − 1)), najmniej 10 s.
- **Walkę zaczyna gracz** (E w r 8), potwór w walce „zajęty”, tabliczka poziomu czerwona przy +3 (widoczna z 60–80 st).
- **Ruch:** serwer przesuwa punkt bazowy po węzłach 4 × na s; klient gra klipy tylko w r 120 dla 12 najbliższych.

| Strefa | Podbiom | Potwór | Poz. | Naraz (max) | Gdzie | Dom |
|---|---|---|---|---|---|---|
| z01 | Łąka | Leśny Slime | 1–2 | 6 (9) | wokół Oczka | woda stawu |
| z02 | Łąka | Leśny Slime | 1–3 | 5 (7) | (−10; 355) przy Dróżce Paproci | kałuże |
| z16 | Łąka | Leśny Slime | 1–2 | 4 (5) | (75; 305) przy Dróżce Kępek — **nowa** | kałuże |
| z03 | Łąka | Leśny Slime | 2–3 | 4 (5) | (376; 336) przy Dróżce Słonecznej — **przeniesiona** | kałuże |
| z04 | Kapeluszowo | Muchomornik | 3–4 | 6 (8) | wioska Wielkiego Kapelusza | chatki |
| z05 | Kapeluszowo | Muchomornik | 4–5 | 4 (5) | wokół Kręgu Zarodników | chatki |
| z06 | Kapeluszowo | Leśny Slime | 3–4 | 4 (5) | (−170; 232) | kałuże |
| z07 | Ostępy | Cierniowy Wilk | 5 | 3 (4), wataha | za Brodzikiem | jamy |
| z08 | Ostępy | Cierniowy Wilk | 5–6 | 6 (9), 2 watahy | u stóp Wilczej Skały | jamy |
| z09 | Ostępy | Cierniowy Wilk | 6–7 | 3 (4), wataha | plac wejścia, polanka środka, plac wyjścia labiryntu | jamy |
| z10 | Ostępy | Cierniowy Wilk | 7 | 2 (3), samotniki | (−320; −320) pod Granią | jamy |
| z11 | Wąwóz | Cierniowy Wilk | 7–8 | 3 (4), wataha | dno rynny przy Schodach | szpary |
| z12 | Wąwóz | **Bursztynowy Slime** | 6–7 | 4 (5) | Wyschnięta Kałuża (ciemne błoto) | kałuże |
| z13 | Wąwóz | Cierniowy Wilk | 8 | 3 (4), wataha | Półka Zachodnia (y 12) | jamy |
| z14 | Korona | Muchomornik | 8–9 | 4 (5) | taras dolny (y 12) przy Dróżce Chatek | chatki |
| z15 | Korona | Cierniowy Wilk | 9–10 | 3 (4), wataha | taras górny (y 22) | szpary |

**Razem 64 zwykłych naraz (do 86)** + **4 patrole** (13 potworów): p1 wataha 5–6 na Wilczym Trakcie, p2 karawana slime’ów 2–3 na Dróżce Paproci, p3 dwa muchomorniki 3–4 z koszami na Dróżce Kapeluszowej, p4 wataha 7–8 na Półce Wschodniej (zeskakuje do rynny, gdy gracz idzie dnem) + troll + strażnik. Patrol walczy w dowolnym miejscu swojej ścieżki — rozsiew trzyma pień ≥ 12 od osi patrolu.

**Leśny Troll.** Śpi w legowisku pod tamą (dom (256; −182)). Co 8–12 min budzi się z rykiem i idzie dnem rynien, Ujściem i skrajem łąki do Oczka (506 st, ok. 72 s), pije i wraca. **E tylko w Wąwozie** (do wylotu Ujścia); na łące jest „w drodze”, a slime’y z01 chowają się do wody.

**Strażnik Gaju.** Kopiec menhirów w Kręgu (0; −385), y 32. Odblokowanie: ok. 10 wygranych z potworami ≥ (poziom gracza − 2). Propozycja: walka w osobnej przestrzeni; łup wg D-058.

---

## 7. Miejsca systemów i wybory dla ludzi

| System | Gdzie |
|---|---|
| Wejście i powrót | Brama Pniaków: Kamień Powrotu (E) |
| Odrodzenie po przegranej | polana (0; 50) |
| Piny (D-064) | Brama i Ukłon od początku; Kapelusz (−240; 232), Skała (−252; −45), Tama (205; −212, na tarasie przy koronie tamy), Krąg (−8; −364) po pierwszej wizycie; przy każdym ognisko |
| Inkubatory (D-060) | Gniazdo w Korzeniach, dwa punkty E |
| Walki petów (D-059) | Dziupla Turniejowa (E) |
| Loch (D-035, D-042) | Korzenna Gardziel, kłódka 5. poziomu |
| Zadania z karczmy (D-034) | Wóz, Krąg Zarodników, Labirynt, Schody Głazów (punkty E w `znaczniki.json`) |
| Strażnik biomu (D-061) | Kamienny Krąg |
| Następny biom | Wrota Bagna (rekwizyt) |

**Wybory dla ludzi:** (1) strażnik osobny dla gracza w osobnej przestrzeni czy wspólne wydarzenie serwera; (2) jajka lasu w lesie czy w wylęgarni w mieście; (3) loch z wejściem w lesie czy tylko z hali portali; (4) przejście z Bramy Miejskiej z zaciemnieniem czy droga; **(5) Wrota Bagna: tylko zapowiedź (teleport po odblokowaniu) czy prawdziwe przejście między biomami; (6) Bursztynowy Slime i nowe zachowania (karawana, kosze, zeskok z półki) — warianty koloru i animacje do zamówienia; (7) lekka mgła w lesie (wspólne oświetlenie miejsca).**

---

## 8. Przykazania stylu natury

Przykazania miasteczka obowiązują dalej (tusz, kontra, zakaz kątów 1–3°, rekwizyt zamiast napisu, SmoothPlastic, Neon tylko jako światło).

| # | Przykazanie | Liczby (jak w kodzie) |
|---|---|---|
| 1 | Zero prostych pni | pnie z 2–3 segmentów w kontrze (6–16°), Ukłon −7/−9/+5 |
| 2 | Kontra korony | korona przechylona przeciwnie 4–8° |
| 3 | Korona jak czapa | spód ciemny, środek, wierzch jasny; 2–4 bryły |
| 4 | Trzy walory | pnie i jeżyny ciemne, runo średnie, ścieżki i kamień jasne |
| 5 | Tusz tam, gdzie patrzy gracz | pierścień u stopy pnia, podkładka pod kapeluszem, krawężniki, policzki ramp |
| 6 | Rodziny z kodu | obrót co 15°, skala 0,8–1,75, odstęp zależny od rodziny |
| 7 | Korytarze kamery | pień ≥ pół szerokości ścieżki + 0,9 promienia korony od osi; place walki r 12 + korona wolne |
| 8 | Kadr ma oddech | polany, ścieżki, niebo; Ukłon widać z bramy |
| 9 | Gęsto tam, gdzie gracz | ok. 85% roślin w pasie 45 od ścieżek |
| 10 | Woda z klocków | cienka tafla 0,18 bez kolizji, ciemny brzeg, kamienie i trzcina; stawy z ciemniejszym środkiem |
| 11 | Neon tylko jako światło | 78 części (≤ 300) |
| 12 | Materiały | SmoothPlastic 89%, Wood 9% (pnie), Slate (Grań, Wilcza Skała, menhiry), Fabric (chorągiewki), Neon |
| **13** | **Potwór widoczny na swoim gruncie** | **ΔL* ≥ 20 albo podkładka strefy** (test w `sprawdz.py`) |
| **14** | **Rant urwiska ≤ 1,5 nad poziomem** | skały krawędzi wystają ≤ 1 poza krawędź i ≤ 1,1 ponad wierzch |

**Rodziny** (`rosliny.py`, `skaly.py`, części na sztukę): Okrąglak 6, Krzywy Dąb 9, Sosna 5, Brzózka 6, Grzyb-olbrzym 4–8, Pniak 2, Kulisa 2, Krzak 3–4, Kwiaty 3, Paproć 2, Jeżyna 3, Trzcina 2; Głaz-pięść 3–5, Kanciak 2, Menhir 3, Skała urwiska 1–2.

**Cechy części:** z kolizją 24%, bez cienia 52% (cel ≥ 50%), przezroczyste 11 (mgła), kule 59, walce 887, Neon 79.

---

## 9. Paleta

`paleta.py`: paleta miasteczka bez zmian + 15 kolorów lasu (tabela w wersji 1 bez zmian: `runo`, `runo_ciemne`, `mech`, `galareta`, `lisc_rudy/miodowy/rdza`, `jezyna`, `jezyna_kolec`, `trzcina`, `sylweta_1–3`, `neon_zarodnik`, `neon_swietlik`). Użycie w v2: płyta `runo`, Łąka `trawa`, Kapeluszowo `runo_ciemne`, dno rynien `ziemia`, półki `bruk_ciemny`, ściany poziomów `kamien_cieply` (Grań `kamien_lochu`), tarasy Korony `runo_ciemne` / `trawa` / `runo_ciemne`, podkładki stref `runo` / `mech` / `kamien_cokol`. Kolorów nie sprawdzono w prawdziwym Studio — pierwszy krok budowy to próbka.

---

## 10. Budżet części (zbudowane)

| Grupa | Części | Uwagi |
|---|---|---|
| Ostepy | 2 759 | ok. 300 sosen z igliwiem, jeżyny, labirynt z garbatym wierzchem, Wilcza Skała, Próg, Wrota, urwiska Grani |
| Korona | 1 644 | 150 brzózek, głazy, uskoki, Rozstaj, Krąg, Ławka |
| Kapeluszowo | 1 578 | 75 grzybów, 45 dębów, chatki, Kapelusz, Krąg Zarodników |
| Laka | 1 545 | 85 okrąglaków, krzaki, kwiaty, Brama, Oczko, Most, Wóz, Pagórek |
| Wawoz | 1 169 | sosny na półkach, urwiska rynien, tama, kałuża, jezioro |
| Mur | 1 160 | skały-kulisy, dwa rzędy kulis, niewidzialna ściana |
| Sciezki | 1 156 | wstęgi, okrągłe końce, krawężniki, kamienie-kody, drogowskazy |
| Serce | 688 | Ukłon (detal), gniazdo, Dziupla, Gardziel, lampiony |
| Tlo | 545 | kulisy, wzgórza, atrapa miasteczka |
| Woda | 449 | struga, stawy, jezioro, trzcina |
| Teren | 398 | płyta, plamy, pryzmaty poziomów, kopce, rampy |
| Punkty | 142 | sylwetki 7 punktów orientacyjnych (stale wczytane) |
| Piny, Chmury | 60 + 60 | ogniska pinów, chmury |
| **Razem** | **13 353** | limit 25 000 — **rezerwa ok. 11,6 tys.** na zagęszczenie po pomiarze na telefonie |

Plan budżetu z wersji 1 (22 020) zostaje w `uklad.json` jako górna granica podziału na podbiomy.

---

## 11. Ujęcia kontrolne

`ujecia.json` (układ lasu) → `ujecia_swiat.json` (świat, do Blendera i do `tools/studio_zrzuty.py` z `--przesun 0,0,0`). Ogniskowa 14,5 = kamera gracza.

| Ujęcie | Co pokazuje |
|---|---|
| `l01_oczy_brama`, `l02_kamera_gracza` | pierwszy kadr: Szlak prowadzi prosto na Ukłon |
| `l03_mapa_gora` | rzut 1000 × 1000 (w świecie — obrócić o 180°) |
| `l04_lot_teleportu` | przelot D-064: plamy podbiomów, atrapa miasteczka na horyzoncie |
| `l05_most_rechotek`, `l06_polana` | most i żaba; Ukłon z polany (korzenie, lampiony, Dziupla) |
| `l07_kapeluszowo`, `l08_wilcza_skala`, `l09_prog` | grzyby i Wielki Kapelusz; Skała w borze; wodospad z tęczą przed łupkową Granią |
| `l10_wawoz_dno`, `l17_polka_nad_rynna`, `l18_tama_z_dna` | rynna ze ścianami; widok z półki w dół; tama, legowisko, Schody Głazów |
| `l11_rozstaj`, `l12_krag`, `l13_lawka_las` | sowa i rampa serpentyny; menhiry i kryształ; widok z Ławki |
| `l14_plac_walki_oczko`, `l16_slime_z_60` | plac walki; strefa slime’ów z 60 st |
| `l15_pod_slonce`, `l19_labirynt`, `l20_bor_ostepy` | przegląd pod słońce; korytarz jeżyn; Wilczy Trakt w borze |

---

## 12. Kolejność budowy

1. ~~Układ, teren, potwory~~ — **zrobione** (v2, `sprawdz.py` 0 błędów).
2. ~~Generator z klocków, rodziny, lokacje, podglądy w Blenderze~~ — **zrobione** (`generuj.py`, 4 rundy podglądów).
3. **Studio, krok 1 (następny):** sprawdzić, że pudło (−700…700; −1300…−2700) jest puste; `python tools/studio_buduj.py swiat/biom_las/czesci.json`; ustawić atrybuty grup z `znaczniki.json` (Persistent, StreamingMesh); zrzuty `python tools/studio_zrzuty.py swiat/biom_las/ujecia_swiat.json --przesun 0,0,0 --wyj <folder>`; próbka kolorów; **pomiar na telefonie** (667 × 375 i 844 × 390): klatki, pamięć, dalekie widoki z Ławki i z bramy przy streamingu; kontrola kolizji (rampy, krawędzie, korona tamy).
4. **Pętla gry na zastępczych bryłach** z `znaczniki.json`: strefy, węzły, domy, patrole, troll, strażnik, E, walka v2, łup, odradzanie; potem modele z Blendera.
5. Zagęszczenie (rezerwa ok. 11,6 tys. części) tam, gdzie zrzuty pokażą pustki.

**Biblioteka:** nie zmieniałem. Rzeczy, których nie umie, są w plikach lasu: triangulacja i pryzmaty wielokątów, wstęgi ścieżek i wody (`teren.py`, `geo.py`), rozsiew z maską (`generuj.py`), przeliczenie ujęć z obrotem (`generuj.py` → `ujecia_swiat.json`), atrybuty grup (lista w `znaczniki.json`, bo `czesci.json` ich nie przenosi). Do przeniesienia do biblioteki przy drugim biomie.

---

## 13. Ryzyka i znane słabości

- **Telefon:** 13,4 tys. części + ok. 80 potworów — niezmierzone. Pierwszy pomiar w Studio.
- **Streaming:** bez ustawienia grup z `znaczniki.json` punkty orientacyjne znikną z daleka.
- **Wygląd z bliska** (podglądy): lica ścian labiryntu to duże płaskie fioletowe płaszczyzny (wierzch już garbaty); ściany rynien Wąwozu gładkie; teren wszędzie płaski poza kopcami i poziomami (Ostępy bez progów); plamy-podkładki stref widać z góry jako koła; niebo bez mgły — las daleko wygląda jak makieta.
- **Rampy:** 1 : 2,5 (sekretna) do 1 : 5; sprawdzić w Studio, czy postać nie ślizga się na klinach i czy krawędź rampy z poziomem nie ma szczeliny.
- **Kamera walki** w rynnie (szer. 54, węzły ≤ 12 od osi) i w labiryncie — sprawdzić na zrzutach z kamery walki v2.
- **Ostrzeżenia `sprawdz.py`:** strefa z06 ma brzeg 16 st od ścieżki (1 st ponad próg); ujęcie `l20_bor_ostepy` ma w kadrze 1 punkt orientacyjny (kadr lokacji, Ukłon zasłania bór).
- **Kolory w Studio** (nasycenie) — tylko założenie.
- **Grzyby** to teren jednego podbiomu i dom kanonicznego Muchomornika, bez ikonowego użycia.
