# Plan biomów 2–8 — zarys

> **Status: PROPOZYCJA (17.11.2026).** Nic w tym pliku nie jest ustalone. Zatwierdzone są tylko: osiem biomów w tej
> kolejności (D-061: las → bagno → dżungla → pustynia → góry z tundrą → lodowiec → wulkaniczny → kryształowy; strażnik
> w każdym biomie, inkubatory z petami biomu, Zaklinacz na pustyni), pas biomów (D-075), układ biomu z inkubatorem,
> przegrodami i strażnikiem (D-076), przelot kamery przy pierwszym wejściu (D-077) i zasada, że wymagany build nie może
> stać się wymaganą klasą (D-069). Nazwy, potwory, kolory, poziomy i czasy niżej to robocze pomysły do oceny przez
> Karola i Pawła. Wszystkie projekty są własne — bez nazw, postaci i wyglądu z innych gier.

Wzór: las-pas (`swiat/las_pas/`, plan `swiat/biom_las/pas/PLAN_PASA.md`). Szczegółowy plan drugiego biomu (Bagna) z
generatorem i podglądami: `swiat/bagno_pas/README.md`.

## Wspólne dla wszystkich biomów (propozycja)

- **Ten sam pas:** pole gry 72 st (4,5 s biegu), kulisy po 24, ta sama oś (z = −700), bez obrotu. Każdy biom zajmuje
  940 st pasa zarezerwowane w planie lasu (`kolejne_biomy`): bagno u 940–1880, dżungla 1880–2820, pustynia 2820–3760,
  góry 3760–4700, lodowiec 4700–5640, wulkan 5640–6580, kryształy 6580–7520. Brama jednego biomu jest wejściem
  następnego; od przybycia do bramy ok. 57,5 s biegu.
- **Ten sam układ (D-076):** wejście z inkubatorem (stanowisko jajka, ok. 10 petów biomu — D-059, D-060) i Kamieniem
  Powrotu → trzy przegrody po trzy kojce rosnących poziomów → leże rzadkiego potwora → arena strażnika → brama. Na
  potworach można farmić cały czas. Przy pierwszym wejściu przelot kamery (D-077) kończy się okrzykiem strażnika.
- **Klasy potworów i D-069:** w każdym biomie trzy główne przegrody mają potwory trzech różnych klas (Wojownik,
  Zwiadowca, Mag), więc każdy gracz trafia na „swojego” i „nie swojego” przeciwnika. Każdy biom ma jeden **nacisk**
  (czego uczy), ale nacisk idzie przez cechy dostępne każdej klasie: Kondycja, Pancerz (punktowy), Inteligencja
  (odporność na magię), Szczęście. Unik (limit Zwiadowcy wyższy) i blok tarczą (tylko Wojownik) mogą pomagać, ale nie
  mogą być jedyną drogą. Zasada robocza: jeśli nacisk biomu sprzyja naturalnie jednej klasie (np. magia → Mag ma
  odporność z Inteligencji), to jedna przegroda i połowa ciosów strażnika idą w przeciwną stronę.
- **Mgła i światło lokalnie:** skrypt klienta zmienia mgłę i tonację tylko u gracza, który stoi w prostokącie biomu
  (tak działa mgła lasu-pasa); efekt koloru jako efekt kamery. Wspólnego `Lighting` na serwerze nie zmieniamy. Do tego
  światło z części (Neon) i niskie ławice mgły z części tam, gdzie pasuje.
- **Budżet:** ok. 9 000 części na biom (las-pas 8 601, Bagno-plan 9 017), razem ok. 70 tys.; przy streamingu gracz ma
  wczytane 1–2 biomy.
- **Paleta:** kolory gruntu, podłoża i drogi w zgodzie z makietą przejścia przez chmury (`swiat/teleport_chmury/krainy.json`).

## Tempo — widełki poziomów (model `tools/walka/tempo.py`, krzywa 11,71 × L^1,6)

Dwa warianty z korekty Karola do D-076 (ok. 10 h do ostatniego biomu). Las-pas jest już zaplanowany na ok. 30 min
(poziomy 1–10/11), więc wariant „równy” liczę jako **las 30 min + po ok. 95 min** na sześć kolejnych biomów (razem
600 min). Kryształowy jest ostatni i leży poza tymi 10 godzinami — jego długość to założenie (200 / 95 min).

| Biom | Rosnący: min · poziomy · walk | Równy po lesie: min · poziomy · walk |
|---|---|---|
| Bagno | 45 · **11–19** · ok. 83 | 95 · **11–25** · ok. 174 |
| Dżungla | 60 · **19–26** · ok. 110 | 95 · **25–35** · ok. 173 |
| Pustynia | 75 · **26–34** · ok. 137 | 95 · **35–44** · ok. 173 |
| Góry z tundrą | 95 · **34–43** · ok. 173 | 95 · **44–51** · ok. 174 |
| Lodowiec | 125 · **43–53** · ok. 229 | 95 · **51–58** · ok. 174 |
| Wulkaniczny | 170 · **53–65** · ok. 311 | 95 · **58–65** · ok. 174 |
| Kryształowy (poza 10 h) | (200) · **65–77** · ok. 366 | (95) · **65–71** · ok. 174 |

Ścisły wariant „równo ok. 85 min na każdy z siedmiu biomów” (razem z lasem) dałby las 1–20, bagno 20–30, dżungla
30–39, pustynia 39–46, góry 46–53, lodowiec 53–59, wulkan 59–65 — ale wymaga przebudowy planu lasu (dziś 30 min).
Liczby są z modelu (`python -B tools/walka/tempo.py --plan …`), nie z gry; potwory biomów 2–8 zastępczo liczone jako
potwory lasu przeskalowane do poziomu.

W tabelach biomów poziom przegrody podaję jako **rosnący / równy**.

---

## 1. Bagno — „Moczary Krzywej Kładki”

Szczegółowy plan: `swiat/bagno_pas/` (generator, kontrola, podglądy).

- **Paleta:** kępy 7E8C3E, błoto 5B4A34, podłoże 4A3F2A, woda herbaciano-zielona 4E6E5E i ciemna toń 2E4A44, deski
  9C7A4A, trzcina B59A52, broda mchu A9B48E; akcenty: zielonożółte ogniki C8E05A (Neon), fioletowe kwiaty 8C5A9E.
- **Z klocków:** Krzywa Kładka z desek przez cały biom; cypryśniki z płaską koroną, „kolanami” i brodą mchu, wierzby
  płaczące, korzeniaki na szczudłach; kępy-wyspy na wodzie bez kolizji (brodzi się); chata na palach, wrak łodzi.
- **Nacisk:** długa walka — spowolnienie i trucizna; płaci się za Kondycję oraz rozsądny Pancerz i odporność na magię.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Rechotne Oczka | Rechotek | Zwiadowca | przysadzista ropucha z klocków, skacze susami (3,0) | 11–13 / 11–14 |
| Bulgotne Trzęsawisko | Bulgotnik | Mag | błotny szaman z głową-bańką gazu i kijem z ognikiem (4,2) | 13–15 / 15–18 |
| Kłapiące Kępy | Kłodokłap | Wojownik | żywa omszała kłoda z paszczą na łapach-korzeniach (3,2, dł. 8,6) | 15–17 / 19–22 |
| Leże (rzadki) | Ropucha z Chatką | Mag | stara ropucha z krzywą chatką na grzbiecie (11) | 18 / 23–24 |
| **Strażnik** | **Strażnik Topieli** | strażnik (fiz. + mag.) | olbrzym z błota i korzeni, łódka jak kapelusz, latarnia w piersi (16) | 19 / 25 |

- **Każda klasa ma drogę:** Wojownik — Pancerz i tarcza na Kłodokłapy, trochę Inteligencji na Bulgotniki; Zwiadowca —
  unik na Kłodokłapy, Kondycja na długie walki; Mag — odporny na Bulgotniki z natury, więc Kłodokłapy i połowa ciosów
  Strażnika są fizyczne.
- **Mgła i światło lokalnie:** gęsta, niska, szarozielona (FogColor 9AA58E, FogStart 30, FogEnd 260) + 20 ławic mgły
  z części nad wodą; tonacja lekko oliwkowa, mniej nasycona.
- **Ryzyka:** półprzezroczyste ławice mogą wyglądać jak szklane talerze (wtedy tylko mgła lokalna); oliwkowy potwór
  na oliwkowej kępie — sprawdzić kontrast; brodzenie bez spowolnienia może dziwić; woda + Neon na telefonie.

## 2. Dżungla — „Gąszcz Pod Parasolem”

- **Paleta:** soczysta zieleń 2FA34A i 6CCB4A, ciemne pnie 5C3A22, droga B07A44, turkus wody 2EC4B6; akcenty: czerwone
  i żółte kwiaty E5392B / F2B030, pomarańczowe owoce.
- **Z klocków:** olbrzymie liście-parasole na łodygach (dach nad ścieżką, poza placami walki), mosty z lian między
  pniami w kulisach, kaskady wody z bloków, omszałe kamienne schody i posągi-głazy własnego wzoru.
- **Nacisk:** zwinni przeciwnicy, którzy często unikają i ranią krwawieniem — opłaca się Szczęście (krytyk skraca walkę)
  i Kondycja.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Polana Liściołazów | Liściołaz | Zwiadowca | kameleon z liści na pazurzastych łapach, zwinięty ogon (3,4) | 19–21 / 25–28 |
| Kwietnik Gębokwiatów | Gębokwiat | Mag | kwiat z paszczą na krótkich korzeniach-nóżkach, sypie usypiający pyłek (5,0) | 21–23 / 28–31 |
| Gaj Kokosów | Kokosowy Siłacz | Wojownik | krępa małpa-siłacz z dwoma kokosami w pięściach (7,0) | 23–25 / 31–34 |
| **Strażnik** | **Wąż Stu Lian** | strażnik | ogromny wąż spleciony z lian, z kwiatem na głowie, zwinięty w spiralę (18 w zwoju) | 26 / 35 |

- **Każda klasa ma drogę:** krytyk (Szczęście) mają wszystkie klasy; Wojownik — Pancerz i blok na krwawienie, Zwiadowca —
  własny unik na Kokosowego Siłacza, Mag — umiejętności Inteligencji trafiają mimo uników tak samo jak ciosy (D-073).
- **Mgła i światło lokalnie:** ciepła zielona mgła (FogColor 7FBF8A, FogEnd 380), jaśniej przy polanach; plamy światła
  z części (żółte łaty na ziemi) zamiast promieni.
- **Ryzyka:** gęste liście zasłaniają potwory i ścieżkę (place walki muszą zostać czyste); dużo części w koronach;
  zielony potwór na zielonym tle.

## 3. Pustynia — „Piaski Pod Patelnią”

- **Paleta:** piasek F2CC7E, ochra C08A55, droga D9A85E, terakota B84A18, biel kości F3E6C8; akcenty: turkus kafli oazy
  2EC4B6, czerwone tkaniny namiotów.
- **Z klocków:** wydmy z klinów w kulisach, kaktusy-słupy ze zgięciami, łuki z piaskowca, oaza z palmami i stawem,
  namioty i **Pracownia Zaklinacza** (D-061) przy wejściu — obok inkubatora.
- **Nacisk:** opancerzeni przeciwnicy (wysoki Pancerz). Magia omija Pancerz (D-062), więc Zaklinacz stoi tu nie bez
  powodu: daje broni pasywki (podpalenie, trucizna — D-051), dzięki którym Wojownik i Zwiadowca też ranią „obok” Pancerza.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Kulnica | Skarabeusz Kulacz | Wojownik | żuk w lśniącym pancerzu, toczy przed sobą kulę piasku (3,5) | 26–28 / 35–38 |
| Wirowisko | Piaskowir | Mag | wirujący słup piasku z dwojgiem oczu i rękami z pyłu, wysoka odporność na magię (6,0) | 29–31 / 38–41 |
| Cierniowy Wąwóz | Skorpion Cierniogon | Zwiadowca | piaskowy skorpion z ogonem jak kaktus, truje (3,0, dł. 6,5) | 31–33 / 41–43 |
| **Strażnik** | **Strażnik Klepsydry** | strażnik | golem z piaskowca z klepsydrą w piersi; co kilka tur twardnieje (Kamienna skóra) | 34 / 44 |

- **Każda klasa ma drogę:** Mag przebija Pancerz z natury — dlatego Piaskowir ma wysoką odporność na magię (tam lepiej
  idzie Wojownikowi i Zwiadowcy); Wojownik i Zwiadowca na żuki i Strażnika biorą pasywki Zaklinacza i zdzieranie
  Pancerza; Zwiadowca ma unik na skorpiony, Wojownik Pancerz na truciznę.
- **Mgła i światło lokalnie:** jasno i daleko (FogColor F0D9A8, FogEnd 600), lekko podbity kontrast i ciepła tonacja;
  w kulisach wydmy jaśniejące ku horyzontowi.
- **Ryzyka:** pustynia łatwo wychodzi pusta i płaska — potrzebne mocne punkty orientacyjne; jasny piasek oślepia na
  telefonie; Zaklinacz to też okno 2D i ekonomia (osobne zadanie).

## 4. Góry z tundrą — „Hale Pod Czapą”

- **Paleta:** zieleń hal A9BC86, szarość skał 6B6F7A, droga 8E8A80, śnieg F2F6FA; akcenty: fiolet wrzosów 8C5A9E,
  czerwone dachy szałasów D8452E.
- **Z klocków:** szałasy pasterskie i kamienne kopczyki, kosodrzewina z niskich brył, ośnieżone turnie w kulisach
  (wysokie, pas zostaje płaski), mostek linowy nad potokiem.
- **Nacisk:** ciężkie ciosy i ogłuszenia — Pancerz i Kondycja.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Hala Baranów | Baran Taranek | Wojownik | baran z kręconymi rogami-ślimakami i dzwonkiem, taranuje i ogłusza (5,0) | 34–37 / 44–46 |
| Kamienne Nory | Śnieżny Świstak | Zwiadowca | pękaty świstak w futrze, gwiżdże, skacze i unika (2,8) | 37–40 / 46–48 |
| Wietrzna Przełęcz | Wichrzyk | Mag | duszek wiatru z kłębów i szalika, mroźny podmuch spowalnia (4,5) | 40–42 / 48–50 |
| **Strażnik** | **Kamienny Pasterz** | strażnik | olbrzymi pasterz z kamienia w płaszczu z mchu i śniegu, z krzywym kosturem (19) | 43 / 51 |

- **Każda klasa ma drogę:** Pancerz i Kondycja trenuje każdy (D-074); Wojownik ma lżej na barany (tarcza), więc Wichrzyk
  bije magią; Zwiadowca unika ciosów, Mag zabija szybciej i bierze Kondycję na ogłuszenia.
- **Mgła i światło lokalnie:** chłodne, przejrzyste powietrze (FogColor D8E2EA, FogEnd 500), mgła w dolinach z części
  przy potoku; lekko niebieska tonacja.
- **Ryzyka:** płaski pas nie oddaje gór — całą „wysokość” muszą zrobić kulisy i tło; przelot kamery między turniami;
  biel śniegu obok bieli lodowca (dwa biomy z rzędu).

## 5. Lodowiec — „Lodowy Jęzor”

- **Paleta:** biel lodu E8F4FF, błękit 7FA8D8, droga B8D4F0, turkus szczelin 5FBCE6, granat cieni 2E3E68; akcent:
  pomarańczowe flagi i namioty wyprawy F08A24 (żeby gracz miał punkt dla oka).
- **Z klocków:** seraki z klinów, szczeliny jako ciemne pasy na ziemi (bez dziur), zamarznięte wodospady, obóz
  wyprawy z flagami, zorza z pasów Neon w tle (oszczędnie).
- **Nacisk:** mróz i magia lodu — spowolnienie i obrażenia magiczne: odporność na magię (Inteligencja) i Kondycja.
  Spowolnienie zabiera Magowi manę (kara many w silniku), więc Mag nie ma tu za darmo.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Ślizgawka | Ślizgun | Zwiadowca | ptak-kulka w czarno-białym upierzeniu, sunie na brzuchu i unika (3,0) | 43–46 / 51–53 |
| Szczeliny | Szroniak | Mag | żywa bryła lodu z sopli, rzuca lodowe pociski (5,0) | 46–49 / 53–55 |
| Zatoka Kłów | Mroźny Mors | Wojownik | mors z ogromnymi kłami i szronem na wąsach, miażdży ciałem (6,0) | 49–52 / 55–57 |
| **Strażnik** | **Mamut Szronogrzywy** | strażnik | mamut z grzywą z sopli i lodową czapą na łbie (20) | 53 / 58 |

- **Każda klasa ma drogę:** Inteligencję i Kondycję ma każdy; Mag — odporny na Szroniaki, ale traci manę na
  spowolnieniu; Wojownik — tarcza i Pancerz na morsy; Zwiadowca — unik na morsy i ślizguny.
- **Mgła i światło lokalnie:** chłodna jasna mgła (FogColor DCEBFA, FogEnd 350), zimna tonacja; zorza tylko w tle.
- **Ryzyka:** biel na bieli — potwory i ścieżka muszą mieć ciemniejsze kontury i podkładki; materiał Ice błyszczy
  i może migotać; mniej detali = pusto.

## 6. Wulkaniczny — „Kotlina Krzywego Komina”

- **Paleta:** bazalt 2E2424 i 4E3C3A, droga 6E5450, popiół 9A8E88; akcenty: lawa FF6A1A / F2B030 (Neon, oszczędnie),
  siarka E8D84A.
- **Z klocków:** krzywe kominy wulkaniczne jak kominy Krzywego Miasteczka (segmenty w kontrze) z dymem, rzeki lawy
  z Neonu w kulisach i rowach (bez kolizji, przejście po bazaltowych mostkach), gejzery z dymu, ostre obsydianowe kliny.
- **Nacisk:** ogień — podpalenie (magia w czasie) i duże ciosy: odporność na magię i Kondycja.

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Iskrowisko | Iskrzak | Zwiadowca | mały chochlik z żaru z płomykiem na głowie, szybki, podpala (3,0) | 53–57 / 58–60 |
| Bazaltowe Tarasy | Bazaltowy Żółw | Wojownik | żółw ze skorupą z bazaltu i szczelinami lawy (5,0, dł. 9) | 57–61 / 60–62 |
| Dymne Doły | Dymnik | Mag | duch z kłębów dymu z żarzącymi się oczami, kule ognia (6,0) | 61–64 / 62–64 |
| **Strażnik** | **Strażnik Komina** | strażnik | olbrzymi krzywy komin na kamiennych nogach, dymi i plunie żarem (22) | 65 / 65 |

- **Każda klasa ma drogę:** odporność na magię ma każdy, kto bierze Inteligencję; Mag ma lżej na Dymniki, więc Żółw
  i połowa ciosów Strażnika są fizyczne; Wojownik — Pancerz i tarcza na żółwie, Zwiadowca — unik na iskrzaki.
- **Mgła i światło lokalnie:** ciemna, czerwonawa mgła z popiołem (FogColor 5A3A30, FogEnd 300), ciepła tonacja;
  światło głównie z lawy (Neon).
- **Ryzyka:** limit Neonu (≤ 300) i czytelność czerwieni na ciemnym tle; ogień i dym na telefonie; cały biom może
  wyjść zbyt ciemny.

## 7. Kryształowy — „Szklany Sad”

- **Paleta:** fiolet 8E6BD8, lawenda B49AE8, droga B49AE8, podłoże 4A3A78; akcenty: róż F2A0C8, mięta 9EF0C8, biel.
- **Z klocków:** kryształowe drzewa (sad) z pni-pryzmatów i koron z klinów, wiszące kryształowe dzwonki, ścieżka
  z płytek jak witraż, wejście do kopalni (zapowiedź kopalni kryształów w Twierdzy, D-061/D-049).
- **Nacisk:** egzamin końcowy — tarcze i osłony (Bariera, Kamienna skóra), mieszane obrażenia: pełny build (Kondycja,
  Pancerz, odporność na magię i krytyk, żeby przebić osłony).

| Przegroda | Potwór | Klasa | Wygląd (wys.) | Poziomy |
|---|---|---|---|---|
| Dzwonnica | Brzęczyk | Zwiadowca | kryształowy skrzat-dzwonek na cienkich nóżkach, dzwoni przy uniku (3,0) | 65–69 / 65–67 |
| Pryzmaty | Pryzmak | Mag | chodzący pryzmat rozszczepiający światło, stawia barierę (5,0) | 69–73 / 67–69 |
| Kopalniane Wrota | Kwarcowy Golem | Wojownik | golem z bloków kwarcu, Kamienna skóra i ciężkie pięści (9,0) | 73–76 / 69–70 |
| **Strażnik** | **Strażniczka Sadu** | strażnik (wszystkiego po trochu) | kryształowe drzewo-duch z koroną dzwonków, osłony i magia (20) | 77 / 71 |

- **Każda klasa ma drogę:** biom miesza wszystkie wcześniejsze lekcje; nie ma jednej odpowiedzi, więc żadna klasa nie
  jest wymagana — każda potrzebuje pełnego, zrównoważonego buildu.
- **Mgła i światło lokalnie:** fioletowa poświata (FogColor C8B8F0, FogEnd 450), lekki blask (efekt kamery tylko
  u gracza); kryształy z Neonu.
- **Ryzyka:** Neon i materiał Glass na telefonie; za dużo fioletu męczy oczy; dźwięk dzwonków (osobne zadanie).

---

## Sprawdzenie D-069 — skrót

| Biom | Nacisk | Sprzyja naturalnie | Jak wyrównane |
|---|---|---|---|
| Bagno | spowolnienie, trucizna, długa walka | Mag (Bulgotniki magiczne) | Kłodokłapy i połowa ciosów Strażnika fizyczne |
| Dżungla | uniki i krwawienie | nikt wyraźnie | krytyk i Kondycja dla wszystkich |
| Pustynia | wysoki Pancerz | Mag (magia omija Pancerz) | Piaskowir odporny na magię; pasywki Zaklinacza dla Wojownika i Zwiadowcy |
| Góry | ciężkie ciosy, ogłuszenie | Wojownik (tarcza) | Wichrzyk bije magią |
| Lodowiec | magia lodu, spowolnienie | Mag (odporność) | spowolnienie zabiera manę; Mors fizyczny |
| Wulkan | podpalenie (magia) | Mag (odporność) | Żółw i połowa ciosów Strażnika fizyczne |
| Kryształowy | osłony, wszystko naraz | nikt | pełny build |

Do potwierdzenia w tabeli balansu silnika (`tools/walka/balans.py`), kiedy potwory dostaną dane walki.

## Wybory dla ludzi

1. Tempo: rosnące (30/45/60/75/95/125/170) czy równe (las 30, potem po ok. 95 min)? Od tego zależą poziomy w tabelach.
2. Nazwy biomów i potworów: które zostają, które zmienić?
3. Czy każdy biom ma mieć leże rzadkiego potwora jak las i Bagno (dziś opisane tylko dla Bagna)?
4. Zaklinacz na Pustyni: w strefie wejścia (propozycja) czy przy arenie, po pokonaniu strażnika?
5. Góry z tundrą: pas zostaje płaski (wysokość tylko w kulisach) czy dopuszczamy rampy i tarasy?

## Ryzyka wspólne

- Osiem biomów po ok. 9 000 części i po pięć nowych potworów (z modelami i animacjami) to dużo pracy przed premierą —
  do zestawienia z roadmapą w sejfie (D-061 mówi to samo).
- Poziomy i czasy są z modelu tempa, a nie z gry; potwory biomów 2–8 nie mają danych walki.
- Ten sam układ w każdym biomie może się znudzić — różnice muszą dać wygląd, nacisk biomu i punkty orientacyjne.
