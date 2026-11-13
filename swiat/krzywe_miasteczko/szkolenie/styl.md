# Styl „Krzywe Miasteczko” — język kształtów i jego przekład na klocki

*Szkolenie „styl” · 2026-11-13 · status: propozycja dla budowniczych mapy v2, nie kanon.*

**W skrócie.** Komiksowe miasteczko robi się czterema ruchami: przerysowana sylwetka (pękate albo wyciągnięte bryły, piętro szersze od parteru, dach jak czapa), krzywizna od 5° wzwyż, obrys „tuszem” z wystających ciemnych klocków i kolor, który sam rozdziela bryły, bo światło jest płaskie. Każdy budynek dostaje jeden wielki rekwizyt-szyld zamiast napisu.

**Jednostki:** studs; **P = 5 studs** (wysokość postaci); kąty w stopniach; front budynku = +Z; obrót części `(rx, ry, rz)` jak w `generuj.py` (kolejność Y→X→Z).

**Kolejność budowy:** bryły w czerni (test sylwetki) → kolory ról → krzywizna → tusz → otwory → rekwizyt → znaki własne.

## 1. Diagnoza v1 w liczbach

|Cecha (karczma v1)|v1|Cel v2|
|---|---|---|
|Pochylenie ścian|0°|5–8°|
|Pochylenie komina|3,5° (w renderze niewidoczne)|8–12°, łamaną do 15°|
|Nawis piętra|1,5 z każdej strony, symetrycznie|2–3,5 z frontu, nierówno|
|Udział dachu w wysokości|39% (15,5 z 40)|45–60%|
|Połacie|obie 41°|różnica ≥10°|
|Belki|0,7–1,1; brąz o jasności 35%|1,2–1,5; tusz ≤12%|
|Szyld|deska 6,4×6, kufel 2,6×3,2 (0,6 P)|rekwizyt 8–12 (1,6–2,4 P)|
|Okna frontu|7 prawie jednakowych|3–5, każde inne|
|Symetria|lustrzana (także arena i brama)|zakaz|
|Bruk|szary, nasycenie 8%|piaskowy, ≥20%|

Wniosek: v1 jest poprawną makietą bez gestu; w domyślnym świetle Studio zlewa się w zielono-szarą plamę.

## 2. Fakty bazowe

|Fakt|Wartość|Źródło|
|---|---|---|
|1 stud|28 cm|Ź1|
|Postać klasyczna|ok. 5 studs (smuklejsze 6–6,5)|Ź2|
|Kąt widzenia kamery|70° w pionie|Ź3|
|Chód / skok|16 studs/s; 7,2 studs|Ź4|
|Przejścia w samouczku Roblox|drzwi i korytarze ≥10 szer., ściany ≥10 wys.|Ź5|
|`Highlight`|max 255 naraz, nadmiar znika bez ostrzeżenia|Ź6|
|Neon|część „wygląda, jakby świeciła”|Ź7|
|Drobne części|wyłączyć `CastShadow` i kolizje|Ź8|
|Ułamek wysokości ekranu|f = h / (1,4·d)|wyliczenie z FOV 70°|
|Wieża w Pizie|3,97° (przed naprawą 5,5°)|Ź16|
|Pub The Crooked House|15°, jeden koniec niżej o 1,2 m|Ź17|
|Piętra fasad w parku rozrywki|1 : 5/8 : 1/2, ściany zwężane ku górze|Ź13|
|Strzecha|≥45–50°|Ź21, Ź22|
|Kontrast grafiki|≥3:1|Ź27|
|Kreska tuszem|trzy grubości: 10/5/2 px|Ź25|

Precedensy krzywej zabudowy: styl „storybook” z Hollywood lat 20. (dachy celowo nierówne, okna i drzwi nie do pary, Ź18), scenografia ekspresjonistyczna (budowle „pochylone i skręcone”, cienie malowane na dekoracji, Ź19), kraina kreskówkowa w parku rozrywki (budynki „grube i napompowane, bez kątów prostych”, squash & stretch ze stałą objętością, Ź15), Krzywy Domek w Sopocie (2004, wzór: ilustracje bajkowe, Ź23). Bierzemy zasady, nie budynki.

## 3. Reguły R1–R30

### A. Bryła i sylwetka

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R1|Trzy wielkości|bryła główna ≈60% objętości, 1–2 średnie ≈30% (wykusz, przybudówka, komin), drobne + rekwizyt ≈10%; każda forma 0,4–0,6 poprzedniej|Ź9, Ź10|
|R2|Test czarnej sylwetki|budynek zalany czernią rozpoznawalny ze 100 studs; każdy typ ma inny kształt bazowy (§5)|Ź9, Ź12|
|R3|Zakaz bliźniaków|połowy fasady różnią się ≥3 cechami: okap wyżej o ≥1,5, okna, strona komina, strona nawisu|Ź14|
|R4|Squash & stretch|wysokość ×k → szerokość i głębokość ×1/√k: 0,75→1,15; 0,8→1,12; 1,4→0,85; 1,6→0,79|Ź14, Ź15|
|R5|Głowa większa od nóg|piętro szersze od parteru: front 2–3,5, boki 0,5–2 (nierówno); wysokości maleją: parter 11–12, piętro 0,7–0,8 parteru, poddasze 0,5–0,6|Ź13, Ź20|
|R6|Skala od postaci|budynki 4–8 P (20–40), kioski 3–4 P; parter ≥2,2 P|Ź2, Ź5|

### B. Krzywizna

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R7|Progi kąta|0° albo ≥4°; ściany i kondygnacje 5–8°; kominy, słupy, latarnie, wieżyczki 8–12°; jeden akcent do 15°; 1–3° zakazane (wygląda jak błąd)|Ź16, Ź17, v1|
|R8|Kontra i skręt|sąsiednie kondygnacje pochylone w przeciwne strony (np. +6°, −5°) i skręcone wokół Y o 4–8° naprzemiennie; dach dodatkowo 4–6°; wierzchołek ≤3 studs od osi podstawy|Ź19|
|R9|Łuk to łamana|wygięcie = 3–5 segmentów po 4–6° (łącznie 12–25°), zakładka 0,3–0,5; łuki bram i koła: krok ≤20°|v1 (portal 19,6°)|
|R10|Prosty grunt|podłogi, schody, podesty: 0°, równo ±0,2; krzywe ozdoby bez kolizji|własne|

### C. Dach

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R11|Wielka czapa|dach = 45–60% wysokości budynku (typ „squash” od 40%; baszty z blankami bez dachu); okap 2,5–3,5 poza ścianę; szczyt wysunięty 2–3; grubość połaci 1,5–2|Ź22, Ź28|
|R12|Kąt i asymetria|„squash” 30–40°, zwykły 45–55°, „stretch” 60–70°; kalenica przesunięta o 10–15% rozpiętości (podział 60/40) → różnica połaci ≥10°; klin: wysokość/bieg = 0,70 (35°), 1,00 (45°), 1,19 (50°), 1,43 (55°), 1,73 (60°), 2,14 (65°)|Ź21, Ź22|
|R13|Dach wygięty|wklęsły „kapelusz”: pasy 35°→50°→65°; wypukły „grzyb”: odwrotnie; kalenica opada 4–6° albo „siodło”: środkowy z 3 segmentów niższy o 1–1,5|Ź18|
|R14|Komin|przekrój 3,5–4,5; 7–10 ponad kalenicę; 3 segmenty po +5°; czapa szersza o 1 z każdej strony; 2–4 kule dymu Ø2,5–5|własne|

### D. Obrys tuszem

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R15|Jeden tusz|`#1D1916`, SmoothPlastic; ciepła ciemna barwa zamiast czystej czerni|Ź24, Ź25|
|R16|Trzy grubości 4:2:1|sylwetka 1,2–1,5 (narożniki, deski czołowe dachu, kalenica, cokół); średnie 0,6–0,8 (ramy, belka stropowa, szyld); detal 0,3 (szprosy, okucia); nic cieńszego. Zasięg czytelności ≈130× grubość: 1,25→160, 0,65→85, 0,3→40 studs|Ź25, wyliczenie|
|R17|Gdzie i ile|tylko sylwetka i granice kolorów: słupy narożne, cokół, belka między kondygnacjami, deski czołowe i kalenica, ramy otworów, podkładka rekwizytu; wysunięcie 0,3–0,5 poza lico, nigdy współpłaszczyznowo (min. 0,05); tusz + ciemne drewno = 12–20% widoku frontu, powyżej 25% robi się ponuro|Ź24, Ź26|
|R18|Podkładka|kopia kształtu w tuszu większa o 0,5 z każdej strony, grubość 0,4, 0,2–0,3 za rekwizytem; koło → walec Ø+1; obowiązkowa dla jasnych form (złoto na jasnym niebie ≈1:1, z tuszem 9,8:1)|Ź26, wyliczenie|
|R19|Jasny obrys na ciemnym|dachy granatowe i grafitowe mają z tuszem tylko 2,1–2,6:1 → kalenica i deski czołowe kremowe lub złote|wyliczenie|

### E. Kolor w płaskim świetle

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R20|Paleta 3 + 1 + tusz|ściana ≈60%, dach ≈30%, akcent ≤10%; z materiałami max 5–6; SmoothPlastic na ≥80% części, faktura tylko w jednej roli|Ź24, Ź28, Ź30|
|R21|Stopnie jasności|jasne (tynk): V ≥84%, S 20–30%; nasycone (dachy, akcenty): S ≥40%, V 40–90%; ciemne tła (drewno, kamień lochów): V 35–45%; tusz: V ≤12%. Stykające się duże płaszczyzny ≥3:1 (krem–czerwień 3,5 tak; krem–jasna mięta 1,9 nie → ciemniejsza mięta `#1C9886` na skorupie `#FFF1CC` daje 3,2)|Ź27, Ź31|
|R22|Zero szarości|duże płaszczyzny S ≥20%; kamień barwiony (`#D6C6AC` ciepły, `#8E93B5` chłodny); bruk piaskowy `#E0C48E` z krawężnikiem tuszu 0,6 (bruk–trawa tylko 1,5:1)|wyliczenie|
|R23|Cień z klocka|pas pod okapem i nawisem: kolor ściany ×0,82 (`#F6E7B8`→`#CABD97`), wysokość 1–1,5; połać odwrócona od rynku ×0,85; opcjonalny raster: 3–5 płaskich walców Ø1,2/0,9/0,6 po skosie 45°, ≤2 skupiska na fasadę|Ź19, Ź24|
|R24|Dach = kod funkcji|każdy typ ma własny kolor dachu (§5), sąsiedzi bez powtórzeń; Neon ≤3% powierzchni (latarnie, magia, żar); szyby SmoothPlastic `#FFD76A` z białym „błyskiem” 0,4×2 pod 35°|Ź7, Ź29|

### F. Otwory i detal

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R25|Drzwi|otwór 7×9 (min. 6×8); rama 1,0 wysunięta 0,4; nadproże 1,2, szersze o 1 z każdej strony, przechylone 4–6°; przesunięte o 15–25% szerokości fasady od osi|Ź5, Ź19|
|R26|Okna|3–5 na front: 4×5, 3×4, okrągłe Ø3; żadne dwa jednakowe (≥20% różnicy lub inny kształt); obrót 4–8°; rama 0,7; parapet 0,6 wysunięty 0,8; jedna okiennica zwisa pod 10–15°|Ź18, Ź19|
|R27|Belki|szerokość 1,0–1,2, wysunięcie 0,35; 3–5 ukośnych pod różnymi kątami 50–70°, bez symetrycznych X|własne|
|R28|Detal i ulica|≥60% fasady to czysta płaszczyzna; 60% detali w pasie 0–14 studs przy wejściu; beczki, skrzynie, latarnie ×1,25–1,5, w trójkach duży–średni–mały, przechył 5–12°|Ź10, Ź12, Ź24, Ź33|

### G. Rekwizyt i sąsiedztwo

|Nr|Reguła|Liczby|Źródło|
|---|---|---|---|
|R29|Rekwizyt-szyld|wysokość 8–12 (1,6–2,4 P; kiosk min. 6), szerokość 35–55% fasady; na telefonie czytelny do ≈9× wysokość; środek 12–20 nad ziemią, dół ≥9; pochylony 10–15° ku rynkowi i 5–10° w bok; ≥25% wystaje poza obrys budynku; jeden żart + max 2 małe echa; bez liter|Ź31, Ź32, wyliczenie|
|R30|Sąsiedztwo i budżet|sąsiedzi: różnica wysokości ≥20%, przeciwne pochylenia, inny kształt bazowy; front do rynku ±5–10°; w stożku 60° przed fasadą nic wyższego niż 6 studs; budżet roboczy: budynek 250–450 części, kiosk 80–150, rekwizyt 30–80|Ź11, własne|

## 4. Przepisy: krzywa bryła z prostych części

|Technika|Przepis|Liczby|
|---|---|---|
|Skręt|cała kondygnacja obrócona wokół Y|4–8°; 0 części, 0 szczelin|
|Ścięcie klinem|rdzeń (blok) + klin-nakładka `Size = (długość ściany, H, d)`, d = H·tan α, ten sam kolor i SmoothPlastic (szew znika). Przypora (grubsza u dołu): przód `(0,180,0)`, tył `(0,0,0)`, prawa `(0,-90,0)`, lewa `(0,90,0)`. Nawis (grubsza u góry): to samo z `rz = 180`. Równoległobok = przypora z jednej strony i nawis z drugiej; „grzyb” = nawis z obu|α = 6°, H = 12 → d = 1,26|
|Przechył kondygnacji|obrót bryły wokół Z lub X o θ, potem obniżenie o (W/2)·sin θ, żeby wyższy koniec nie odstawał|W = 24, 5° → 1,05; W = 40, 4° → 1,40|
|Schodek|piętro przesunięte w bok względem parteru|1–2,5|
|Łamana|segmenty z rosnącym kątem i zakładką|3–5 segmentów po 4–6°|
|Słup narożny|`belka(p_dół, p_góra)` w tuszu; zakrywa styki klinów|1,2–1,5|
|Grupa|bryłę budować lokalnie, potem jedna macierz R = Ry·Rx·Rz; rozkład: `rx = asin(-R[1][2])`, `ry = atan2(R[0][2], R[2][2])`, `rz = atan2(R[1][0], R[1][1])`|—|

Orientacje klinów i rozkład macierzy sprawdzone rachunkiem na geometrii z `KSZTALTY.md`, nie w Studio — pierwszą ścianę obejrzeć w podglądzie.

## 5. Typy budynków (wymiary orientacyjne, rozstrzyga plan miasta)

|Typ|Kształt bazowy|k|Szer.×gł.|Wys.|Ściany|Dach|Gest|
|---|---|---|---|---|---|---|---|
|Karczma|pękaty prostokąt|0,8|42×26|37|`#F6E7B8`|`#D8452E`|piętro +5°, parter −4°; połacie 39° i 51°|
|Zbrojownia / kuźnia|niski ciężki kwadrat|0,75|28×22|22 (komin 32)|`#D6C6AC`|`#3F4E6E`|dach wgnieciony 33°, komin 12°|
|Sklep magiczny|trójkąt, iglica|1,6|16×16|39|`#F6E7B8`|`#7B4FB5`|trzon łamany 3×5°, dach 61°|
|Wylęgarnia|jajo|0,9|Ø20|21|`#FFF1CC`|`#1C9886`|dyski przesunięte o 0,5–1|
|Stajnia|długi niski prostokąt|0,6|36×18|21|`#6E4526`|`#E2A93A`|dach w siodło 37°, okap 3,5|
|Arena|pierścień z kolcami|0,6|brama 22×10, mur Ø60|filary 24 i 18|`#D6C6AC`|pasy `#C4302B` / `#F6E7B8`|filary +5° i −7°|
|Gildia|wieża-kwadrat|1,4|20×20|40|`#C5CEF5`|`#2F4F9E`|skręt pięter 6°, korona przechylona 6°|
|Brama lochów|paszcza (trójkąt w dół)|0,85|22×12|21|`#4A4560`|`#7FBF3F`|łuk z 11 segmentów|
|Koło fortuny|koło na trójkącie|1,0|16×10|20|—|`#D93A8C`|koło Ø14 odchylone 8°|
|Brama twierdzy|dwa nierówne kwadraty|1,3 i 0,9|44×14|30 i 20|`#D6C6AC`|`#2659B3`|baszty +5° i −7°|

Pary ściana–dach mają kontrast 3,2–5,0:1. Koło, kwadrat i trójkąt traktujemy jako konwencję czytelności, nie psychologię (Ź11 ją odrzuca).

## 6. Rekwizyty-szyldy (pomysły własne)

**Karczma**
1. Kufel-komin: kufel Ø7×10 zamiast komina, przechylony 12°; piana z 6 białych kul Ø2–4 ścieka po połaci.
2. Beczka-wykusz: leżąca beczka Ø8×10 wbita w piętro nad drzwiami; z kranu kapią 3 bursztynowe kule do kufla-donicy.
3. Kiełbasa na widelcu: widelec 12 studs, kiełbasa z 3 łamanych walców Ø2,5.
4. Dach-pokrywka: róg dachu uchylony 10° jak pokrywka garnka, uchwyt-kula Ø3, spod spodu 3 kule pary.

**Zbrojownia / kuźnia**
1. Kowadło na dachu: 12×7×5 na kalenicy, dach pod nim spłaszczony do 30° — widać ciężar.
2. Miecz w dachu: 16–18 studs, wbity pod 15°, wokół 4 odchylone „dachówki”.
3. Młot w zamachu: 10 studs na wysięgniku, obrócony 30°, pod nim sztaba Neon.
4. Tarcza reklamacyjna: Ø9, trzy wbite strzały, wyszczerbiona krawędź.
5. Hełm na kominie: Ø6×7, dym wychodzi wizjerem.

**Sklep magiczny**
1. Dach-kapelusz: ostrosłup o wysokości 1,2–1,5 szerokości, czubek złamany o 20–25°, rondo wystaje 3, klamra 3×3.
2. Kostur z kryształem: 18 studs, oparty o narożnik pod 10°; kryształ (2 ostrosłupy, Neon) lewituje 1 stud nad końcem.
3. Kot w domu: pomarańczowy ogon z 5 segmentów (8 studs) wystaje z okna, nad kalenicą dwoje uszu z klinów 2,5.
4. Kociołek: Ø8 przed wejściem; zielone kule Ø1–3 unoszą się spiralą do 14 studs.
5. Lewitujące okno: jedna rama 1,5 od ściany, obrócona 12°.

**Wylęgarnia**
1. Jajo-budynek: 6 dysków Ø13/18/20/18/14/8 po 3,5; zygzak pęknięcia w tuszu; „kapsel” odchylony 20°, spod niego wygląda cyjanowa kostka-slime.
2. Gniazdo na dachu: 16 belek w okręgu Ø12, jaja Ø5/4/3.
3. Ślady łap: 7 różowych odcisków (walec Ø2 + 3 walce Ø0,8) od rynku do drzwi i dalej po ścianie na dach.
4. Smoczy ogon: czerwony, 6 segmentów (10 studs) z kolcami-klinami, owinięty wokół komina.
5. Miska z kością: miska Ø9, kość 7 studs.

**Stajnia**
1. Podkowa-brama: łuk 12×13 z 11 segmentów, 7 „dziur na gwoździe” 0,8.
2. Koń na biegunach: 10 studs, na kalenicy, przechylony 12°.
3. Marchew na wędce: wędka 14 studs ze strychu, marchew 5 studs wisi 1,5 przed pyskiem konia w boksie.
4. Bela XXL: Ø9×7, zaklinowana w otworze strychu, wbite widły 10 studs.

**Arena**
1. Brama-hełm: przejście pod przyłbicą hełmu 16×18; pióropusz z 5 czerwonych płyt.
2. Odcisk zawodnika: w murze wklęsła sylwetka ludzika 6×7,5 (tusz, głębokość 0,5), jakby ktoś wyleciał przez ścianę.
3. Puchar z plastrem: 10 studs, pęknięcie zaklejone dwoma beżowymi blokami na krzyż.
4. Gong: Ø10 na dwóch krzywych słupach, pałka 7 studs.
5. Spadła gwiazdka: trzy nad bramą, jedna wbita w ziemię.

**Gildia**
1. Sztandar-olbrzym: płótno 6×14 z 3 segmentów (±8°) na maszcie 26 studs; herb „trzy kształty”: koło, kwadrat, trójkąt.
2. Róg: 5 walców Ø1,5→5, łamanych co 12°, razem 12 studs.
3. Stół narad na balkonie: blat Ø9 w połowie poza balkonem, mapa z czerwonym X, wbity sztylet.
4. Kłódka skarbca: 6×7, pałąk z 5 segmentów.

**Brama lochów**
1. Paszcza: łuk jako pysk — 7 zębów-klinów u góry (1,5–3 studs, każdy inny), 5 u dołu; oczy Ø3 patrzą w różne strony; schody-język wysunięte 8.
2. Krzywy znak: żółty trójkąt 8 studs na jednym gwoździu, obrócony 25°, z czaszką z klocków.
3. Pęknięta kłódka: łańcuch z 8 ogniw zwisa z łuku, kłódka leży na ziemi.
4. Kryształy-kły: ostrosłupy 2–7 studs po bokach; Neon tylko największy.

**Koło fortuny**
1. Koło-słońce: tarcza Ø14, 8 pól, 8 promieni-klinów 2–3; wskaźnik = dłoń z palcem 5 studs.
2. Krzywy namiot: pasy magenta/krem, czubek odchylony 20°, chorągiewka.
3. Sakwa: worek Ø7, 7 monet Ø2,5 w łuku spadania do kosza.
4. Korba: 6 studs, z rączką-walcem.

**Brama twierdzy**
1. Baszty nie do pary: Ø14×30 i 18×18×20, pochylone +5° i −7°, blanki szerokości 2–4.
2. Klucz i wycieraczka: złoty klucz 14 studs na haku, pod bramą wycieraczka 8×4.
3. Armata z gniazdem: lufa 10 studs, w wylocie 3 jajka Ø1,5.
4. Żuraw z klockiem: dźwig z belek, na linie blok 4×4×4 w kolorze muru — zapowiedź budowania twierdzy.
5. Łatany sztandar: błękit tabardu Rycerza, kwadratowa łata, 4 „szwy” z tuszu.

## 7. Znaki własne miasteczka (na każdym budynku)

- **Wypadnięty klocek:** wnęka 2×2×0,5 w tuszu i ten sam klocek na ziemi, obrócony 15–30°; 1–3 na budynek.
- **Łata z fastrygą:** prostokąt 2–3 studs w kolorze akcentu + 4–6 szwów 0,3×0,8; 2–4 na budynek.
- **Chorągiewki duetu:** kliny 2×3 na szczytach, błękit (tabard Rycerza) oraz pomarańcz z purpurą (Kot-Mag), przechylone 10–15°.

## 8. Czego nie robić

**Z gry-inspiracji nie przejmujemy** (zgodnie z notatką sejfu o granicy inspiracji): nazw własnych gry, bohaterów, właściciela koła, eventów, lochów, potworów i petów; grzyba jako symbolu waluty ani ozdoby sklepów; układu panoramy miasta 1:1 (kolejność i sąsiedztwo budynków); wyglądu konkretnych budynków, sprzedawców i ikon; żartów sytuacyjnych, w tym toalety jako magicznego urządzenia. Cudze marki też odpadają (maskotka-zabawka z rozmowy 12.11).

**W stylu:**
1. Pudełek pod kątem prostym, lustrzanych fasad, dwóch takich samych domów.
2. Pochyleń 1–3° i powyżej 15°; krzywych podłóg i schodów.
3. Szarych płaszczyzn (S <20%), więcej niż 5–6 barw na budynek, faktur na wszystkim.
4. Obrysu na każdej krawędzi, detali cieńszych niż 0,3, współpłaszczyzn.
5. Liter na szyldach, szyldów-desek, rekwizytów poniżej 6 studs.
6. Neonu ponad 3%, stosów półprzezroczystych części.
7. `Highlight` jako obrysu, unii, siatek, tekstur, zmian `Lighting`.
8. Drzew i straganów zasłaniających fasady.
9. Symboli hazardu przy kole: kości, kart, żetonów, dźwigni automatu.

## 9. Niepewności

- Limit wyszukiwań w tej sesji skończył się w trakcie badań. Bez potwierdzenia w źródle pierwotnym zostały: podział 60/30/10 (heurystyka), realny wysięg nadwieszenia w metrach, rozmiar drzwi z forum Roblox (7,5–8 × 5–6 znane tylko ze streszczenia wyniku).
- Progi „8% wysokości ekranu” i „4 px” to założenia własne (telefon, 720 px).
- Pomysłów z §6 nie porównano z ekranami gry-inspiracji (zakaz użycia jej nazwy w wyszukiwaniu) — potrzebny przegląd człowieka.
- Tusz `#1D1916` odbiega od kanonicznej czerni UI `#000000` — decyzja Game Directora.

## 10. Źródła (dostęp do wszystkich: 2026-11-13)

- Ź1 https://create.roblox.com/docs/physics/units — stud = 28 cm
- Ź2 https://create.roblox.com/docs/studio/avatar-settings — wysokość postaci
- Ź3 https://create.roblox.com/docs/reference/engine/classes/Camera — FOV 70°
- Ź4 https://create.roblox.com/docs/reference/engine/classes/StarterPlayer — chód, skok
- Ź5 https://create.roblox.com/docs/tutorials/curriculums/environmental-art/greybox-your-environment — przejścia ≥10
- Ź6 https://create.roblox.com/docs/reference/engine/classes/Highlight — limit 255
- Ź7 https://create.roblox.com/docs/parts — kształty, Neon
- Ź8 https://create.roblox.com/docs/performance-optimization/improve — cienie, kolizje
- Ź9 https://worldofleveldesign.com/categories/game_environments_design/silhouette-design-game-environments.php — sylwetka, formy 1-2-3
- Ź10 https://wiki.frozenbyte.com/index.php/Level_Art:_Composition — unikać 90°, puste pola
- Ź11 https://book.leveldesignbook.com/process/blockout/massing — bryła dominująca
- Ź12 https://rocketbrush.com/blog/shape-language-in-game-character-design-how-to-make-characters-readable-and-consistent — kształty, 70/30
- Ź13 https://paprikamagazine.com/articles/main-st-is-almost-alright — piętra 1 : 5/8 : 1/2
- Ź14 https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation — stała objętość, „bliźniaki”
- Ź15 https://www.micechat.com/15529-mickeys-toontown/ — squash & stretch w architekturze
- Ź16 https://en.wikipedia.org/wiki/Leaning_Tower_of_Pisa — 3,97°
- Ź17 https://en.wikipedia.org/wiki/The_Crooked_House — 15°
- Ź18 https://en.wikipedia.org/wiki/Storybook_house — nierówne dachy
- Ź19 https://en.wikipedia.org/wiki/The_Cabinet_of_Dr._Caligari — pochylone dekoracje
- Ź20 https://en.wikipedia.org/wiki/Jettying — nadwieszenie
- Ź21 https://www.designingbuildings.co.uk/wiki/Thatch_roofing — strzecha ≥50°
- Ź22 https://westeroscraft.com/docs/building/fundamentals/exteriors — okap, strzecha ≥45°
- Ź23 https://en.wikipedia.org/wiki/Krzywy_Domek — Sopot 2004
- Ź24 https://gamedeveloper.com/art/a-comic-book-style-action-shooter-creating-the-visual-look-of-hawked — ciepły obrys, bez drobnych faktur
- Ź25 https://www.retrosupply.co/blogs/tutorials/10-more-tips-to-level-up-your-digital-inking — 10/5/2 px
- Ź26 https://en.wikipedia.org/wiki/Cel_shading — obrys jako większa czarna kopia
- Ź27 https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html — 3:1
- Ź28 https://minecraft.how/blog/post/minecraft-building-styles — paleta 5–6, duży okap
- Ź29 https://devforum.roblox.com/t/how-to-make-the-best-cartoony-feel/680546 — SmoothPlastic, neon w oknach za jasny
- Ź30 https://devforum.roblox.com/t/how-could-i-make-a-cartoony-type-of-building/866347 — żywe barwy, mało detalu
- Ź31 https://cgmasteracademy.com/blog/6-steps-to-create-a-stylized-dwarven-feast-hall — rekwizyt-bohater, zlewające się walory
- Ź32 https://en.wikipedia.org/wiki/Walt_Disney_Imagineering — „magnes wizualny”
- Ź33 https://80.lv/articles/creating-a-stylized-fantasy-house-in-blender-and-3dcoat/ — detal w punktach skupienia
- Lokalne: `swiat/demo_lesna_baza/generuj.py` i rendery, `panel/luau/KSZTALTY.md`, zrzut ze Studio, notatki sejfu o stylu i granicy inspiracji.
