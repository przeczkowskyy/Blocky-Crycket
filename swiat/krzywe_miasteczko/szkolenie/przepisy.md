# Przepisy na bryły — książka kucharska mapy v2 „Krzywe Miasteczko”

*Szkolenie nocne, 13.11.2026. Temat: „przepisy”. Jednostka: stud; kąty w stopniach.*

> **W skrócie.** 50 funkcji-przepisów na bryły z samych prymitywów, zapisanych w API `swiat/biblioteka/scena.py`. Każdą zbudowałem, narysowałem własnym rasteryzatorem w płaskim świetle i przepuściłem przez ogólny wykrywacz migotania — wynik końcowy: 0 par ścian różnych kolorów w jednej płaszczyźnie. Blendera ani Studio nie uruchamiałem, więc wygląd w prawdziwym oświetleniu Studio trzeba jeszcze potwierdzić.
> Kod do skopiowania: `<folder roboczy>/mapa/_przepisy_robocze/przepisy_kod.py`; obok `migot.py` (wykrywacz), `test.py` i `rendery/`.

## 1. Konwencje (sprawdzone liczbowo)

`obrot = (rx, ry, rz)`, R = Ry·Rx·Rz. **rx > 0** — szczyt bryły ucieka ku +Z (do frontu). **rz > 0** — szczyt ucieka ku −X. **ry = θ** — front (+Z) patrzy w (sin θ, cos θ). Klin: wysoka pionowa ściana po +Z, skos opada ku −Z. Klin narożny: wierzchołek nad rogiem (+X, −Z).

| Chcę uzyskać | Część i obrót (rx, ry, rz) |
|---|---|
| połać opadającą ku +Z / −Z / +X / −X | klin: (0, 180, 0) / (0, 0, 0) / (0, −90, 0) / (0, 90, 0) |
| ćwiartkę ostrosłupa w ćwiartce (−X,+Z) / (+X,+Z) / (+X,−Z) / (−X,−Z) | klin narożny: ry = 0 / 90 / 180 / 270; przy 90 i 270 zamień rozmiar X↔Z |
| odwrócony trójkąt w narożu otworu, przy prawym / lewym filarze | klin: (0, 90, 180) / (0, −90, 180) |
| płaski trójkąt w płaszczyźnie XY (sztych miecza, ogon chorągwi) | klin o grubości w X: (0, ∓90, 0); odwrócony: (0, −90, 180) |

**Pięć reguł szczelności**

1. Ściany różnych kolorów nigdy w jednej płaszczyźnie: schodki lica co ≥ 0,1 (minimum 0,05, liczone **po** skalowaniu — `skala=0.42` zamienia 0,1 w 0,042).
2. Elementy powtarzane (klińce, segmenty mostu, cembrowina, blanki): co drugi głębszy lub wyższy o 0,2 i w innym tonie.
3. Rant, gzyms, wieko: większe o ≥ 0,25 w bok **i** o 0,1 w górę. Różnica 0,02 migocze.
4. Segment doklejany pod kątem α: zakładka = (połowa grubości)·tan α + 0,05; inaczej po zewnętrznej stronie zgięcia zieje szpara.
5. Bryła pochylona stoi w prostym cokole i zaczyna się niżej o zagłębienie = (W/2)·tan|rz| + (D/2)·tan|rx| + 0,1 (dom 22 × 16, rz 3°, rx 1°: 0,82).

**Płaskie światło domyślnego Studio.** Kształt muszą nieść kolory, nie cienie. (1) Materiał domyślny to SmoothPlastic — płaski kolor czyta się pewniej niż faktura; Wood, Cobblestone i Slate dopuścić dopiero po próbie w Studio. (2) Każda bryła w 2–3 tonach: połać frontowa jaśniejsza od tylnej (`kolor2`), segmenty dachu na przemian, korona drzewa jasna u góry, ciemna u dołu. (3) Ciemna linia w każdym styku brył: rant cokołu, wieniec, okap, kalenica, gzymsy. (4) Okna i lampy z Neonu — jedyne powierzchnie niezależne od światła.

## 2. Czego brakowało w v1

| Brak | Liczby z v1 | Odpowiedź v2 |
|---|---|---|
| Krzywizn | karczma 222 części, wszystkie bryły główne proste i symetryczne; krzywy tylko komin (3,5°) i szyld (3°) | układy lokalne: parter −3°, piętro +5,5°, dach −2,5°, komin z 3 segmentów |
| Obrysu | belki 0,7 i ramy okien 0,5 = 3–5 pikseli z 80 studów (720p); brak linii okapu i kalenicy | ramy 0,6–0,8, podkładki, rant dachu 0,7, wieniec 2,5 |
| Dachu z charakterem | 2 płaskie płyty jednego koloru | segmenty w 2 tonach, ugięcie 1,3, kąt 55° |
| Miasta | jedna budowla (40 × 28), reszta to wiaty | 8–10 domów 20–26 × 16–20 |
| Oszczędności | 65 % części to roślinność: 1685 z 2599; z 792 klinów narożnych 672 siedzą w świerkach; w szarym świetle Studio ciemna zieleń zlewa się i zasłania budynki | drzewo 7 części, wzgórze 1–2, las tylko jako tło |
| Dużych szyldów | kufel 6,4 × 6,0 z płytek 0,3; miecze grubości 0,3 | rekwizyty 3D 8,5–15 studów z obrysem 0,55 |
| Kontroli migotania | wykrywacz: 420 par ścian różnych kolorów bliżej niż 0,045 (bruk↔bruk 50, droga↔droga 16, droga↔łata trawy 11; część zakryta) | reguły z §1 i wykrywacz w `sprawdz()` |
| Tła | płaska płyta 230 × 230 w szarej pustce, 15 części przezroczystych | wzgórza-kule dookoła, chmury, przezroczystość 0 |

## 3. Funkcje pomocnicze biblioteki v2

W `scena.py` już są: `uklad`, `cechy`, `blok`, `kula`, `klin`, `naroznik`, `walec`, `slup`, `belka`, `ostroslup`, `szczyt`, `ramka`, `podkladka`, `sprawdz`. Do dodania (prototypy gotowe):

| Funkcja | Co daje | Części |
|---|---|---|
| `lamana(segmenty)` | krzywy słup, pień, komin; zakładkę liczy sama; kontekst zostaje w układzie wierzchołka (dobudowa lampy, korony) | n |
| `pierscien(r, n, size, co_drugi)` | bloki na okręgu frontem na zewnątrz; styczna = 2·R_zewn·tan(180°/n) | n |
| `sciety(a, b, h, t)` | ostrosłup ścięty: rdzeń + 4 kliny + 4 narożne, ściany dokładnie płaskie — zwężane wieże, skarpy, filary, dachy dzwonowe | 9 |
| `dach_pelny`, `dach_plytowy` | jawny kąt i **poziomy** okap; y = 0 układu to krawędź ścian | 3 / 5 |
| `dach_ugiety`, `dach_czterospadowy`, `helm_gwiazda`, `helm_tort`, `helm_krzywy` | §4.2 | 16–26 / 6 / 8 / 5 / 14 |
| `luk`, `okno`, `okno_okragle`, `drzwi`, `daszek`, `lukarna` | warstwy lica zaszyte w funkcji | 4–11 |
| `migotanie()` | test współpłaszczyznowości dla brył obróconych (obecny `sprawdz` widzi tylko bloki równoległe do osi świata) | — |

Uwagi do istniejącego kodu: (a) `dach_dwuspadowy(okap=…)` daje realny wysięg poziomy okap·(0,5·cos k + 0,32) − 0,5·grub·sin k, czyli 0,72 dla okap = 2, k = 55°, grub = 1,2; spód płyty przy licu ściany leży 0,3 nad `srodek_okapu`, wierzch 2,4 nad. (b) `obrys_sylwetki` zakłada limit 31 Highlightów, dokumentacja podaje dziś 255 — sprawdzić w Studio; obrys i tak budujemy z klocków.

## 4. Przepisy

### 4.1 Krzywy dom szachulcowy (22 × 16; kalenica na 38, komin 43, z dymem 50)

| Krok | Budowa |
|---|---|
| 1. Cokół, prosty | blok (W+1,8; hc; D+1,8), hc = max(2; zagłębienie + 1,2); ciemniejszy rant (W+2,6; 0,5; D+2,6) wystający 0,1 nad cokół |
| 2. Parter, `uklad(obrot=(1, 0, −3))` | blok (22; 10 + zagłębienie; 16) zaczynający się w cokole |
| 3. Belki = hierarchia lica | słupy narożne 1,2 × 1,2, lico +0,35, o 0,4 dłuższe niż ściana; rygle 1,0 × 0,5, lico +0,25; słupki 0,9, lico +0,30; zastrzały 0,7, lico +0,15 (`belka(…, grub=0.7, szer=0.4)`) |
| 4. Piętro, `uklad(pos=(0, hp − zagł2, 0.4), obrot=(−1.5, 5, 5.5))` | ciemny wieniec (Wp+0,9; zagł2+1,0; Dp+0,9); blok (Wp; 10; Dp), Wp = W + 2·1,3, Dp = D + 2·1,6; 6 czół belek 0,9; słupy kończą się 0,6 pod krawędzią ściany; krzyżaki 0,65 |
| 5. Dach, `uklad(obrot=(0, 0, −2.5))` | `dach_ugiety`: kąt 55°, 4 segmenty, ugięcie 1,3, okap 1,0, długość Wp + 4; tynkowe szczyty opuszczone o 0,8, z ciemną belką |
| 6. Komin | `lamana`: (5,0 × 3,0; +5°), (4,0 × 2,6; −11°), (3,0 × 2,3; +8°); czapa 3,3 × 0,7; dym — kule 2,0 / 2,8 / 3,6 |

Części: 108 (dach płytowy), 98 (pełny), 121 z daszkiem i lukarną. **Tani: 61** (68 z kominem) — bez rygli bocznych, słupków, zastrzałów, okiennic, parapetów piętra i czół belek, dach z 2 segmentów. Reguły: skręt piętra ≤ 5° przy wysięgu 1,3–1,6 (wysięg ≥ 0,5·przekątna·sin(skręt) + 0,2); kondygnacje przechylać naprzemiennie; okna piętra ze środkiem na 35 % wysokości ściany. Błędy: belki równe z krawędzią ściany; goły tył (gracz obchodzi dom — minimum 2 krzyżaki).

### 4.2 Dachy

| Dach | Budowa | Części |
|---|---|---|
| Pełny dwuspadowy | 2 kliny (dl; P·tan k; P), P = pol + okap; ciemna płyta-rant 0,5 pod spodem, większa o 0,35 | 3 |
| Płytowy | 2 płyty grub. 1,2 i długości (pol+okap)/cos k + grub·tan k (krzyżują się w kalenicy); pod każdą ciemna podkładka 0,6 większa o 0,35; kalenica 0,9 × 1,7 | 5 |
| Ugięty | n segmentów, każdy w układzie obróconym o nachylenie linii y(x) = −u·(1 − (2x/dl)²); zakładka 0,5; co drugi segment grubszy o 0,12 i jaśniejszy. Dla n = 4, u = 1,3, dl = 29: −7,6°, −2,5°, +2,5°, +7,6° | 26 płytowy, 16 pełny; tani n = 2: 16 / 10 |
| Czterospadowy | 2 kliny (W−D; h; D/2) + 4 narożne (D/2; h; D/2); na kwadracie same narożne | 6 / 4 |
| Dzwonowy | `sciety` h 3,2, t 4,0 (39°) + ostrosłup h 11 na podstawie 9 (68°) | 13 |
| Stożek „gwiazda” | 2 ostrosłupy obrócone o 45°, drugi o 0,05 wyżej | 8 |
| Stożek „tort” | 4 walce r·(1 − i/4)^0,8 + gałka | 5 |
| Hełm krzywy | rondo r·1,22; 3 ostrosłupy: kolejny rośnie z 45 % wysokości poprzedniego, podstawa × 0,63, wysokość × 0,9, zgięcie 13°, skręt 20°; gałka | 14 |
| Daszek nad wejściem | klin (7,5; 1,9; 3,0) wysoką krawędzią do ściany + rant + 2 zastrzały; dwuspadowy szczytem do frontu: 5 | 4 |
| Lukarna | skrzynka 3,6 × 5,0 × 5,0 wpuszczona w połać o 0,5 + ugięcie; okno; daszek z 2 klinów + rant | 8 (tania 6) |
| Komin krzywy | jak w 4.1 | 7 |

Płytowy wygląda grubiej i ma duży wysięg nad szczytem; pełny jest tańszy i odporniejszy na błędy osadzenia.

**Osadzenie dachu.** Grubość pionowa płyty = grub/cos k (2,09 dla 1,2 i 55°). Dach płytowy: układ 0,3 **poniżej** krawędzi ścian, ugięcie ≤ grub/cos k − 0,7 (1,39). Dach pełny: układ o ugięcie + 0,1 **powyżej** krawędzi i okap·tan k ≥ ugięcie + (dl/2)·sin(przechył dachu) + 0,2 (wychodzi okap 1,5). Opad okapu poniżej krawędzi ścian: płytowy okap·tan k + 0,8 (2,2), pełny okap·tan k + 0,45 (2,6) — górna krawędź okien piętra co najmniej 0,8 niżej. Przy kącie ≥ 50° okap ≤ 1,5; wysięg nad szczytami 2,0 (płyty) albo 0,8 (pełny).

### 4.3 Wieże

| Wieża | Budowa | Części |
|---|---|---|
| Okrągła, zwężana schodkowo | stopa r + 0,9; 3 walce o wysokościach 42 / 33 / 25 % i promieniach r, 0,86 r, 0,74 r; na stykach ciemny gzyms r + 0,45 × 0,7; całość pochylona 4°, każde piętro dalej o ±2° | 16 z blankami, 20 z hełmem |
| Blanki okrągłe | głowica r + 1,3 (ciemna) i r + 1,0; 8 zębów szer. 2·(r+0,6)·sin 22,5°·0,56, wys. 1,6, co drugi +0,25 | w cenie |
| Kwadratowa zwężana | `sciety`: góra 7,2, dół 10,4, h 22 (zbieżność 4,2°); gzyms 0,7; głowica +0,9; 8 zębów 1,6; dach czterospadowy przechylony 4° | 24 |
| Tania | walec + hełm „tort” | 6 |

Hełm zamiast blanków, nie razem (zęby zasłaniają rondo). Dla r = 4,2 i h = 24: hełm r 4,4, wysokość 13.

### 4.4 Łuki, bramy, mosty, schody, mury, palisady

| Element | Budowa | Części i liczby |
|---|---|---|
| Łuk półkolisty | n nieparzyste; kliniec i: środek na promieniu r + grub/2 pod kątem φ = 180°·(i+0,5)/n, obrót rz = φ − 90°, styczna = 2·(r+grub)·tan(90°/n)·1,02; co drugi głębszy o 0,2; zwornik 1,25 × szerszy, 1,36 × wyższy, o 0,7 głębszy | 9; r 5, grub 2,4 → styczna 2,66 |
| Brama | 2 filary-`sciety` (t 0,5, h 7) + ciemny impost + łuk; prześwit 10 | 29 |
| Brama tania | 2 filary + nadproże 2,4 + 2 odwrócone kliny 2,2 × 2,2 | 5 |
| Most łukowy | R = (L²/4 + f²)/(2f); segment i obrócony o −φ, długość 2R·tan(φ_k/n) + 0,15; co drugi szerszy o 0,2; balustrada 0,9 × 2,2 wysunięta 0,25 poza bok pomostu; ciemna poręcz 1,4 × 0,5 | 25; L 26, f 3,2 → R 28,0, wjazd 27,7° |
| Schody | stopień = pełny blok od ziemi, 1,0 × 1,6, każdy węższy o 0,15; tanie: 1 klin | n |
| Mur z blankami | korpus 9 × 3; skarpa-klin 5,4 × 1,2; ciemny rant +0,3; zęby 2,0 × 1,7 co 1,6, co drugi +0,3 | 11 na 30 studów |
| Palisada | pale r 1,2 co 2,1, wys. 9 ± 0,9, przechył ±3°; ostrze: klin-ścięcie 1,8, co trzeci ostrosłup 2,4; żerdź 0,8 | 35 na 24 study (tania 23) |

### 4.5 Okna i drzwi

| Warstwa od lica ściany | Okno | Drzwi |
|---|---|---|
| Ciemna rama-podkładka | (szer+1,2; wys+1,2; 0,4), lico +0,40 | (szer+1,6; wys+1,0; 0,5), lico +0,50, wpuszczona 0,1 w próg |
| Wnętrze | szyba Neon `FFD98A`, lico +0,50, bez cienia | skrzydło, lico +0,60 |
| Podział | szprosy 0,35, lica +0,60 i +0,62, krótsze od szyby o 0,12 | 3 deski, lico +0,68; 2 okucia 0,6, lico +0,76; gałka-kula 0,9 |
| Dodatki | parapet (szer+2,1; 0,55; 1,2); okiennice 1,5 odchylone o 14° z własną podkładką; łuk = 2 walce o osi Z | łuk = 2 walce |

Części: okno 5, łukowe z okiennicami 11, okrągłe 4, drzwi 8; tanie okno 2 (podkładka + szyba). Wymiary: okno 2,6–3,2 × 3,0–3,8, drzwi 5 × 7,6 (gracz 5,3), każde okno przechylone inaczej, ±2–4°. Błędy: szpros równy z krawędzią szyby; rama cieńsza niż 0,5.

### 4.6 Szyldy-rekwizyty czytelne z 80 studów

Zasady: wysokość 8,5–15 (większe niż drzwi); najmniejszy ważny detal ≥ 1,0; **płetwa obrysu** — ciemna płyta albo tarcza grubości 0,3–0,5 w płaszczyźnie środka, większa o 0,55 z każdej strony (działa z przodu i z tyłu); najwyżej 3 kolory + tusz; wieszać krzywo (−3…−6°), miecz pod 35°; bez kolizji. Test: FOV 70° daje kadr wysokości 1,4·d; z 80 studów to 6,4 piksela na stud przy 720p — szyld 10 studów ma 64 piksele, obrys 3,5. Wszystkie 7 rozpoznawalne na renderze.

| Szyld | Budowa | Wymiar | Części |
|---|---|---|---|
| Kufel | walec r 3,0 × 6,4; 2 obręcze r 3,28 i dno r 3,4 (tusz); piana z 6 kul 1,5–3,7; ucho z 3 bloków tuszu | 9,4 × 10,2 | 13 |
| Miecz | ostrze 1,8 × 8,0; sztych z 2 klinów 0,9 × 1,8; zbrocze 0,5; jelec 6,0 × 1,1 z podgiętymi końcami; rękojeść 2,8; głowica-kula 2,0; płetwy | 7,5 × 15,9 | 15 |
| Mikstura | kula 6,4 + tarcza r 3,75; szyjka r 1,1 × 2,6; kryza; korek przechylony 9°; blik-kula 1,6 z obu stron; 3 bąble Neon | 7,5 × 14,6 | 11 |
| Jajko | kule 7,0 / 6,2 / 4,9 co 1,5 w górę (proporcja 1,28) + 3 tarcze; 6 kropek-kul 1,2–1,9 | 8,1 × 10,1 | 12 |
| Podkowa | 7 bloków na łuku 240°, promień środka 3,6, pas 1,7, styczna 2,75; pięty; 6 hufnali; płetwy | 10,4 × 8,3 | 22 (tania 12) |
| Moneta | tarcza r 4,65; krążek r 4,1 × 1,2; rant r 3,3 × 1,5; romb 2,5; blik | 9,3 × 9,3 | 5 |
| Czaszka | kula 7,0 + szczęka 4,6 × 3,0; oczodoły-walce r 1,1 na wylot; nos-romb; 3 zęby; piszczele 12 z kulami 1,5 | 12,2 × 12,0 | 21 (bez piszczeli 11) |

Wysięgnik: belka 0,9 + zastrzał + 2 łańcuchy = 4 części.

### 4.7 Roślinność i tło

| Element | Budowa | Części |
|---|---|---|
| Drzewo kulowe | pień `lamana`: (4,2; r 1,25; +6°), (3,6; r 1,0; −12°); korona z kul 10 / 8,6 (ciemna, niżej) / 6,8 (jasna, wyżej) / 6,4 / 5,6 | 7 |
| Drzewo klockowe | pień z 2 bloków; 4 bloki 8,5 / 6,0 / 4,2 / 3,8 obrócone do ±12° | 6 |
| Świerk | pień r 0,9; 2–3 ostrosłupy o podstawie 8,8 (kolejne × 0,72), h 6,2, skręt 45° | 9–13 |
| Krzak | kule 3,6 / 2,8 / 2,6 + 3 jagody 0,6 | 6 |
| Chmura | kule 11 / 15 / 13 / 9 + płaski spód 24 × 3,2 × 8; bez kolizji i cienia; y = 110–150 | 5 |
| Wzgórze | **jedna kula**: czasza o promieniu a i wysokości h → R = (a² + h²)/(2h), środek na y = h − R. a 70, h 30: średnica 193, brzeg 46°. a 90, h 22: średnica 390, brzeg 27,5°. Do chodzenia h/a ≤ 0,25. Jaśniejsza czapa = druga kula | 1–2 |

Trzy tony zieleni, najjaśniejszy u góry (udawane światło). W mieście ≤ 12 drzew; tło robią wzgórza i chmury.

### 4.8 Woda i rekwizyty

| Element | Budowa | Części |
|---|---|---|
| Staw | bez przezroczystości, wierzchy warstw: ciemny brzeg r + 0,7 na 0,10 → tafla 0,19 → ciemniejsza toń 0,29 → bliki 0,4 × 2–3 na 0,40; dwa zachodzące koła | 9 |
| Studnia | `pierscien`: 10 kamieni 2,31 × 2,6 × 1,1 na r 3,0, co drugi +0,25; woda 1,2 poniżej; słupy ±4°; wał; dach pełny przechylony 5° | 21 |
| Fontanna | misa r 7 × 1,8 z rantem; 12 kamieni; trzon r 1 × 4,4; czasza r 3; 4 strugi po 2 belki 0,5; moneta w skali 0,42 | 32 |
| Stragan | 4 słupy odchylone 3–4°; lada 3,4; markiza z 7 pasów pod kątem 11° + 7 zębów + rant; 4 kule towaru | 25 (tani 13) |
| Beczka | walec r 1,5 × 3,6; brzuch r + 0,16 na 42 % wysokości; 2 obręcze r + 0,26; wieko | 5 |
| Skrzynia | blok 3; 4 listwy 0,5; krzyżak; wieko większe o 0,5 | 7 |
| Latarnia | `lamana` 3 segmenty (+5°, −9°, −38°); klatka: daszek-romb, Neon 1,3 × 1,7, 4 pręty 0,2, spód | 12 (tania 4) |
| Chorągiew | maszt r 0,32 × 14; 3 pasy skręcone +14°, −26°, +22°; ogon z 2 klinów | 7 |

## 5. Typowe błędy (każdy złapany testem na własnych szkicach)

1. Rant cokołu równy z jego wierzchem — 424 study² migotania. Rant zawsze 0,1 wyżej.
2. Ugięty dach schodzi poniżej górnych belek ściany — na połaci pojawia się cienka kreska. Stosować warunki z 4.2; górnego rygla od strony okapu nie dawać, zastępuje go ciemny rant dachu.
3. Okap zasłania łuki okien piętra — liczyć opad okapu przed ustawieniem okien.
4. Szczyt pod dachem pełnym przebija połać — ma być panelem na czole klinów, mniejszym o 0,9.
5. Segmenty łuku i mostu jednej głębokości — boki sąsiadów migoczą.
6. Rekwizyt pomniejszony skalą — odstępy spadają poniżej 0,05.
7. Balustrada, wieko, pięta podkowy „prawie równo” (0,02–0,04) z sąsiadem.
8. Kolizje na dekoracjach: zostawić je tylko na bryłach głównych (6–10 części na dom zamiast 108), resztę budować w `s.cechy(kolizja=False)`, drobiazgi także `cien=False`.

## 6. Budżet i twarde fakty o Roblox

| Zestaw | Części |
|---|---|
| 10 domów (4 pełne, 6 tanich) | ok. 800 |
| 3 wieże, brama, 60 studów muru, most | ok. 150 |
| 8 szyldów z wysięgnikami | ok. 140 |
| Rynek: fontanna, studnia, 3 stragany, 12 latarni, 6 chorągwi, 10 beczek i skrzyń | ok. 300 |
| 12 drzew, 20 krzaków, 10 wzgórz, 8 chmur, staw | ok. 270 |
| Razem bez nawierzchni | ok. 1700 (v1: 2599) |

- Rozmiar części: 0,001–2048; poniżej 0,05 fizyka liczy jak 0,05.
- Dokumentacja: trzymać się poniżej 1000 wywołań rysowania i 1 000 000 trójkątów na urządzeniu bazowym; przezroczystość tylko 0 albo 1; wyłączać `CastShadow` małym częściom oraz `CanCollide`, `CanTouch`, `CanQuery` częściom bez kolizji; wbudowane materiały zużywają mniej pamięci niż własne tekstury; refrakcja szkła nie działa na telefonach.
- Postać: prędkość 16 studów/s, skok 7,2, podejście do 89°; samouczek greybox trzyma przejścia ≥ 10 szerokości i ściany ≥ 10 wysokości. 1 stud = 28 cm.
- Migotanie rośnie z odległością (spada precyzja głębi). W zgłoszeniu ze starszego iPhone'a migotały nawet części tylko stykające się, a autor podał potrzebny odstęp „około 0,1065” (wątek niejednoznaczny) — stąd próg 0,1 dla wszystkiego większego niż detal.

## 7. Źródła (dostęp 13.11.2026)

- https://create.roblox.com/docs/reference/engine/classes/BasePart — rozmiary, przezroczystość, kolizje.
- https://create.roblox.com/docs/parts oraz /docs/parts/materials — kształty, 43 materiały, szkło.
- https://create.roblox.com/docs/performance-optimization/design oraz /improve — budżety, cienie, kolizje.
- https://create.roblox.com/docs/reference/engine/classes/Humanoid, /StarterPlayer, /Camera, /Highlight — skok, prędkość, FOV 70°, limit 255.
- https://create.roblox.com/docs/physics/units — 1 stud = 28 cm.
- https://create.roblox.com/docs/tutorials/curriculums/environmental-art/greybox-your-environment — skala przejść i ścian, rampy z klinów.
- https://devforum.roblox.com/t/z-fight-rendering-issues-that-occur-on-mobile-which-do-not-occur-on-pclaptop/3134388 — odstępy na telefonach.
- https://devforum.roblox.com/t/z-fighting-merger-if-bricks-are-the-same-color/34077 — precyzja głębi a odległość.
- https://devforum.roblox.com/t/whats-a-good-maximum-part-count-for-low-end-devices/1930430 — opinie: 15–20 tys. części.
- https://worldofleveldesign.com/categories/game_environments_design/silhouette-design-game-environments.php — sylwetka: kształty duże, średnie, małe; test czarnej plamy.
- https://studio.blender.org/blog/modeling-stylised-assets-on-pet-projects — przerysowanie, zwężanie, unikanie symetrii.
- https://www.designingbuildings.co.uk/wiki/Jetty — nadwieszenie piętra zwykle 400 mm, do 1200 mm (1,4–4,3 studa).
- Pomiary własne: `panel/luau/KSZTALTY.md`, `swiat/demo_lesna_baza/czesci.json`, rendery kontrolne w folderze roboczym.

Zastrzeżenie: limit wyszukiwań tej sesji wyczerpał się przed dwoma zapytaniami (liczba trójkątów prymitywów, normy wielkości piktogramów) — czytelność szyldów policzyłem z FOV i sprawdziłem renderem.
