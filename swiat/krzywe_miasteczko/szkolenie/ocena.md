# Ocena wizualna map — rubryka, werdykt dla v1, ujęcia kontrolne

> Szkolenie nocne 13.11.2026, temat „ocena”. Dla krytyków renderów i budowniczych mapy v2 „Krzywe Miasteczko”. Materiał roboczy, nie kanon.
> Podstawa: 7 renderów v1, 1 zrzut z Roblox Studio w domyślnym oświetleniu, `czesci.json` (2599 części), paleta z `generuj.py`. Liczby o v1 to pomiary skryptami z rozdz. 6. Progi stylu i wymiarów uzgodnione ze `styl.md` (R1–R30) i `rzemioslo.md`.

## 1. W skrócie
- v1 dostaje **3,6/10**. Karczma jest poprawna, ale mapa to las z jednym domem: 80% planu to zieleń, 65% części to drzewa i runo, 8 z 9 miejsc jest niższych od przeciętnego drzewa.
- W prawdziwym Studio jest gorzej niż w Blenderze: kolory tracą 20–35 pkt nasycenia i przesuwają się ku zimnej zieleni, kremowy tynk szarzeje, a front karczmy stoi w cieniu, bo patrzy w stronę przeciwną do słońca.
- Oświetlenia nie zmieniamy, więc formę i kontrast trzeba **namalować geometrią i kolorem**: trzy grupy waloru, obrys tuszem, fasady frontowe do słońca, kolory z zapasem nasycenia.
- Liczy się zrzut ze Studio z oczu gracza. Blender jest podglądem roboczym.

## 2. Jak oceniać

„Miejsce” to punkt, do którego gracz chodzi: karczma, sklep, wylęgarnia, loch, arena.

**Cztery testy każdego kadru** (16:9, 1920×1080):

| Test | Jak wykonać | Zaliczony, gdy |
|---|---|---|
| T1 miniatura | pomniejsz do 256×144 px (ikona: środkowy wycinek 150×150), patrz 3 s | nazwiesz temat i dominantę; widać najwyżej 3 duże plamy barwne |
| T2 telefon | pomniejsz do 640×360 px, oglądaj w 100% | każde miejsce w kadrze rozpoznane po kształcie i kolorze; symbole ≥24 px |
| T3 szarość | usuń kolor | trzy grupy waloru; miejsce różni się od tła o ΔL* ≥20 |
| T4 zmrużenie | rozmycie Gaussa o promieniu 1,2% szerokości | najmocniejszy kontrast leży na celu gracza; najwyżej 3 ogniska |

**Skala.** 0–3: kryterium złamane. 4–6: działa, ale generycznie. 7–8: dobre, jeden próg niespełniony. 9–10: wszystkie progi z kolumny „10/10” spełnione na zrzucie ze Studio. Wynik = Σ(ocena × waga)/100. Każda ocena podaje pomiar i jedną poprawkę z liczbą; bez liczby jest nieważna.

**Bramki (pułap wyniku).** Brak zrzutu ze Studio z oczu gracza: najwyżej 7,0. W ujęciu U1 na teście telefonu mniej niż 4 rozpoznane miejsca: 6,0. Dominanta w szarości bliżej tła niż ΔL* 20: 6,0. Widoczna płyta bazowa lub krawędź mapy z poziomu gracza: 7,0. Skopiowany budynek, postać, logo albo żart gry-inspiracji: kryterium 11 = 0 i wynik najwyżej 5,0.

**Wzory** (kamera Roblox: pole widzenia 70° w pionie, domyślny dystans 12,5 studs; awatar ok. 5 studs, chód 16 studs/s, czyli 80 studs w 5 s):

| Co | Wzór | Przykład |
|---|---|---|
| Udział obiektu o wysokości H w wysokości ekranu z odległości d | H/(1,4·d) | wieża 42 studs ze 100 studs: 30% |
| Piksele na telefonie (kadr 360 px) | 257·H/d | 4 studs z 40 studs: 26 px |
| Najmniejszy czytelny symbol na szyldzie | d/10 studs | z 40 studs: 4 studs (4,4 mm na ekranie 5″) |
| Dolna krawędź nadproża bramy, by nie zasłonić dominanty | h_oka + d_bramy·tan(α+5°), α to kąt szczytu dominanty | v1: 5,8 + 15,7·tan 18,3° = 11 studs (jest 8) |
| Walor L* (0–100) | 116·Y^(1/3) − 16, gdzie Y = 0,2126R + 0,7152G + 0,0722B (wartości liniowe) | trawa v1 #5FB548: 66,5; ΔL* 30 to kontrast ok. 3:1 |

## 3. Rubryka: 11 kryteriów (wagi sumują się do 100)

| Kryterium (waga) | Pytanie kontrolne | Jak wygląda 10/10 | Typowe błędy | Naprawa samą geometrią i kolorem |
|---|---|---|---|---|
| **1. Miniatura i telefon (12)** | Czy w 3 s na kadrze 256×144 px nazwę temat i dominantę, a na 640×360 px każde miejsce? | Dominanta zajmuje 15–30% kadru; najwyżej 3 duże plamy barwne; każde miejsce ma ≥24 px wysokości i własny kolor dachu; symbol szyldu ≥d/10 studs. | Drobnica poniżej 1 stud; wszystko jednej wielkości; miejsca zasłonięte zielenią. | Łączyć drobne części w płaszczyzny koloru; symbole powiększyć 2–3×; opróżnić korytarz widoku kamera–miejsce. |
| **2. Hierarchia punktów orientacyjnych (12)** | Czy jest jedna dominanta, 2–3 punkty drugiego rzędu i tło, a każdy punkt czemuś służy? | Każdy rząd niższy od poprzedniego o ≥30% (np. 42, 29 i 20 studs); dominanta ≥2× najwyższe drzewo; zewsząd widać ≥2 punkty. | Kilka równych „dominant”; miejsca niższe od tła; ozdobne wieże bez funkcji. | Wybrać jedną dominantę i podnieść ją iglicą lub basztą; równe wysokości zróżnicować o ≥30%; obniżyć tło. |
| **3. Sylwetki na tle nieba (10)** | Czy po zaczernieniu brył rozpoznam każde miejsce po samym obrysie? | Ze spawnu ≥50% linii horyzontu tworzą budynki, ≤25% drzewa, 0% pustki; każde miejsce ma inny kształt bazowy i szczyt; obrys łamie się co 8–15 studs; szczyt ciemniejszy od nieba o ≥25 L* albo obwiedziony tuszem. | Wszędzie pudełko z trójkątem; drzewa wyższe od dachów; jasna ściana na tle jasnego nieba. | Ściany 5–8°, kominy i wieżyczki 8–12°; kalenica łamana z 3–5 odcinków po 4–6°; dach 45–60% wysokości, okap 2,5–3,5 studs; komin lub rekwizyt ponad kalenicę. |
| **4. Kontrast walorowy (12)** | Czy w szarości odróżniam ziemię, ściany, dachy i miejsca od tła? | Trzy grupy waloru: jasne ściany i bruk (L* ≥78), średnie dachy i zieleń, ciemny tusz i otwory (≤20). Ściana od dachu ≥30 L*, miejsce od tła ≥20, droga od trawy ≥15 albo ciemny krawężnik; żadna strefa nie zajmuje ponad 60% kadru. | Wszystko w L* 55–67; dach w walorze drzew; najjaśniejsza plama poza celem. | Rozjaśnić bruk, dodać krawężnik tuszem; namalować cień: pas 1–1,5 studs pod okapem ciemniejszy o 18–30%, ciemny cokół. |
| **5. Harmonia palety (8)** | Czy policzone piksele dają około 60/30/10 i czy akcent trafia tylko w cele? | Dominanta ≤60% (piaskowy bruk, tynk); uzupełnienie ok. 30% (dachy, drewno, zieleń ≤30%); akcent ≤10%: jeden kolor-kod na miejsce plus złoto; najwyższe nasycenie tylko na małych polach; duże płaszczyzny bez szarości (nasycenie ≥20%). | Zieleń 80%; ten sam czerwony na 4 dachach; akcenty rozsypane po runie. | Każdemu miejscu dać własny kolor dachu, sąsiedzi bez powtórzeń; kwiaty tylko przy wejściach; tło mniej nasycone o 15–20 pkt niż cele. |
| **6. Rytm i różnorodność brył (8)** | Czy bryły układają się w duże–średnie–małe, a powtórzenia mają wariację? | Trzy klasy wielkości; sąsiedzi różnią się wysokością ≥20%, kształtem bazowym i kierunkiem przechyłu; fronty odchylone od osi rynku o 5–10°; ≥4 typy dachów; żaden moduł więcej niż 3 razy bez zmiany; plan bez osi symetrii. | Siatka prostopadła; lustrzane pary; klonowane drzewa. | Obrót wokół Y, rozciągnięcie lub spłaszczenie bryły, inny dach, dobudówka z jednej strony, nawis piętra 2–3,5 studs. |
| **7. Prowadzenie wzroku i gracza (10)** | Czy ze spawnu, bez UI, wiem, dokąd iść, i widzę cel, zanim ruszę? | Ze spawnu widać ≥4 miejsca, każde ≥10% wysokości ekranu i ≤80 studs; drogi jaśniejsze od otoczenia o ≥15 L*; wejście to najbardziej kontrastowe pole fasady; fasady frontowe w słońcu. | Cel zasłonięty własną bramą lub szyldem; droga w walorze trawy; front w cieniu. | Nadproże ze wzoru; latarnie i chorągiewki co 12–16 studs jako „okruszki”; drzwi w barwie dopełniającej ścianę. |
| **8. Gęstość detalu (8)** | Czy detal skupia się przy wejściach i szyldach, a duże płaszczyzny dają oku odpocząć? | ≥55% części w miejscach i na rynku, ≤25% w zieleni; ≥60% każdej fasady gładkie; 60% detalu w pasie 0–14 studs przy wejściu; części poniżej 1 stud ≤5%. | Równy szum wszędzie; detal poza wzrokiem (runo, tyły); puste połacie dachów. | Przenieść budżet z runa na fasady; dach podzielić 3–5 pasami lub łatami; rekwizyty grupować w trójki duży–średni–mały. |
| **9. Skala względem postaci (6)** | Czy przy awatarze 5 studs wszystko jest przerysowane o tę samą miarę? | Drzwi ≥6 na 8 studs (zalecane 7 na 9–10); uliczki ≥10, ulica główna 16–20; parter 11–12; rekwizyty 1,25–1,5× wielkości realnej; stopień ≤1 stud; w każdym kadrze manekin 5 studs. | Realistycznie małe okna; meble do kolan; inna skala w każdym budynku. | Jedna tabela wymiarów w generatorze; powiększać rekwizyt-symbol, nie cały budynek. |
| **10. Spójność stylu (8)** | Czy każdy budynek spełnia te same reguły: obrys, krzywizna, przerysowanie, nasycenie? | Obrys tuszem ≥3 px w kadrze telefonu (0,5 studs z 40 studs; listwy sylwetki 1,2–1,5 studs czytelne ze 100), wysunięty 0,3–0,5 poza lico; przechył ścian 5–8°; SmoothPlastic na ≥80% części; jedna paleta. | Bryła prosta obok krzywej; faktury materiałów brudzą kolor; przechył 1–3° wygląda jak błąd. | Pod jasną formę podłożyć kopię w tuszu większą o 0,5 studs; naroża, cokół i krawędzie dachu obwieść listwą. |
| **11. Charakter i humor (6)** | Czy każde miejsce ma jeden własny gag czytelny z 30 studs? | Jeden rekwizyt-szyld na miejsce: 8–12 studs (kiosk ≥6), bez liter, mówi, kto tu mieszka; budynek ma „postawę” (kłania się, pęka w szwach); zero kopii cudzych budynków i żartów. | Generyczna wioska fantasy; humor w detalu poniżej 1 stud; cytaty z gry-inspiracji. | Rekwizyt powiększyć i wynieść ponad okap (środek 12–20 studs nad ziemią); powtórzyć na nim kolor-kod. |

Krzywe ma być to, co duże i ozdobne. Proste zostaje to, czego gracz używa: podłoga, schody, otwory drzwi.

## 4. Werdykt dla v1 „Leśna baza startowa”: 3,6/10

v1 było szkicem do rozmowy o skali; tu oceniam je jak kandydata na mapę.

**Punktacja:** miniatura 4, hierarchia 3, sylwetki 3, walor 3, paleta 3, rytm 4, prowadzenie 5, detal 3, skala 6, styl 3, charakter 4. Suma ważona: 36,4/100.

| # | Priorytet | Słabość (pomiar) | Jak v2 ma jej uniknąć |
|---|---|---|---|
| 1 | P0 | **Zieleń zalewa kadr.** W planie z góry 80% pikseli to zieleń, a czerwień, żółć i fiolet razem 6%. W Studio na 100 px zieleni przypada 9 px innych barw. | Zieleń ≤30% planu; podłoże miasta to piaskowy bruk i ubita ziemia; najwyżej 20 drzew, tylko za pierzejami. |
| 2 | P0 | **Drzewa wyższe od budynków, jedna dominanta.** 92 drzewa, mediana 22,9 studs (maks. 31,7). Karczma 44,6; arena 20,9 i brama 20,2; pozostałe sześć miejsc 7,7–15,0. Ze spawnu 50% linii horyzontu to las, karczma 21%. | Rzędy wysokości co ≥30% (np. 42, 29, 20 studs); każde miejsce ≥20 studs; drzewo w hubie ≤15 studs; budynki ≥50% horyzontu. |
| 3 | P0 | **Walory zlane.** Trawa L* 66,5, bruk 65,6, woda 65,6, dach stajni 64,2, droga 60,6; dach karczmy 48,4 przy igłach 45,3 (ΔL* 3,1). W szarości plac, drogi i dachy znikają. | Bruk L* ≥80 z krawężnikiem tuszem, zieleń 55–65, ściana od dachu ≥30 L*. Przed budową policzyć ΔL* każdej pary sąsiadów. |
| 4 | P0 | **Studio gasi i ochładza kolory.** Trawa: nasycenie 60% → 32–41% (w Blenderze 54%), odcień 107° → ok. 135°. Tynk karczmy w cieniu: L* 90 i nasycenie 25% → L* 60–75 i 5–9% (szarozielony). Dach: nasycenie 77% → 43–48%. Drzewa to plamy L* 27–37 zlane z własnym cieniem (27% kadru). Zrzut z 250–300 studs, więc część straty to mgiełka atmosfery. | Zapas nasycenia 10–15 pkt ponad cel; zieleń o odcieniu 85–105°, nasyceniu ≥65% i L* ≥60; liście ze SmoothPlastic. Przed budową tablica próbek palety w Studio, pomiar w słońcu i w cieniu. |
| 5 | P0 | **Front dominanty w cieniu.** Na zrzucie cienie padają na południowy wschód, a karczma patrzy na południe. Obie widoczne ściany mają L* 70,1 i 74,6, więc bryła nie ma modelunku, a gracz ze spawnu patrzy pod słońce. | Odczytać kierunek słońca (`game.Lighting:GetSunDirection()`, sam odczyt) i stawiać dominantę po stronie rynku przeciwnej do słońca — według tego zrzutu po wschodniej lub południowej (x + z > 0). Spawn obrócić ku oświetlonym frontom. |
| 6 | P0 | **Stylu z kanonu nie ma.** Żadna z 2 głównych brył karczmy nie jest przechylona; jedyny przechył to komin 3,5° (6% wysokości). Fasada lustrzana, brak obrysu, nawis piętra 1,5 studs, dach to 39% wysokości. | Ściany 5–8°, kominy 8–12°, nawis piętra 2–3,5 studs, dach 45–60% wysokości, obrys tuszem (reguły R1–R30 w `styl.md`). |
| 7 | P0 | **Mapa leży na szarej płycie.** Trawa w Studio (L* 58–64) ma walor płyty bazowej (50–60); widać krawędź kwadratu 230×230 i pusty horyzont. | Pierścień zamykający ≥16 studs (lepiej schodkowo 24–40) w promieniu 120–140 studs; oko w skoku sięga 12 studs. |
| 8 | P1 | **Brama zasłania cel.** 16 studs przed bramą szyld zajmuje 8–20° nad horyzontem, a dach karczmy 8–13°. Z wejścia widać tylko ciemny parter. | Nadproże ze wzoru (tu ≥11 studs) albo szyld obok osi drogi. |
| 9 | P1 | **Budżet części poszedł w runo.** Las 40% i runo 25% części; 9 miejsc razem 23%. 258 części kwiatów po 0,5 studs (6 px z 20 studs); 17,6% części poniżej 1 stud. | ≥55% części w miejscach i na rynku; nic poniżej 1 stud poza szyldami. |
| 10 | P1 | **Kolor nie koduje miejsc.** Ten sam czerwony na karczmie, studni, tablicy i arenie; w ujęciu spod karczmy daszek studni zlewa się z jej dachem. | Jeden kolor-kod na miejsce, powtórzony na dachu, szyldzie i znaczniku mapy. |
| 11 | P1 | **Układ „krzyż na polanie”.** Arena i portal leżą lustrzanie (x = ∓74), drogi są proste, plac to idealne koło. Strefa bez drzew wokół placu to 6,5% mapy. Różnica poziomów: 0. | Zwarty, nieregularny rynek Ø 64–72; uliczki łamane co 20–30 studs; miejsca 25–80 studs od spawnu; 2–3 poziomy (+4 i +8 studs), dominanta najwyżej. |
| 12 | P1 | **Wzrok ucieka od celu.** Koło fortuny stoi przed szyldem i oknami karczmy, latarnia w osi portalu, studnia w osi wejścia. W Studio największy kontrast kadru ma brzeg stawu z cieniami drzew (4,6% przy średniej 2,1%), nie karczma. | W stożku 60° przed fasadą nic wyższego niż 6 studs; najjaśniejsza plama mapy ma być celem. |
| 13 | P2 | **Symbole za małe, neon wypalony.** Jajo na szyldzie wylęgarni ma 1,5 studs (potrzeba 3,9 z 39 studs); koło z prostokątów czyta się jak wiatraczek; wir portalu to biały krążek. | Symbol ≥d/10; koło z klinów; Neon najwyżej 3% powierzchni, w kolorze-kodzie. |

**Co zachować z v1:** walory karczmy (tynk L* 90, belki 28, świecące okna), markizę w pasy, jaja w gnieździe i łuk portalu z kamieni obróconych o 15–20° (tu krzywizna działa).

## 5. Osiem ujęć kontrolnych

W v1 nie było ani jednego kadru z kamery gracza. Układ lokalny miasta: środek rynku (0, 0), północ = −Z, wysokości nad ziemią, pole widzenia 70°. R to promień zabudowy. Każde ujęcie przechodzi testy T1–T4, najpierw w Blenderze, potem w Studio.

| Ujęcie | Kamera | Co sprawdza i próg |
|---|---|---|
| **U1. Oczy gracza na spawnie** | 12 studs za punktem spawnu (przeciwnie do kierunku patrzenia postaci), 8 studs nad ziemią, celuje w punkt 5 studs nad spawnem; w kadrze manekin 5 studs | ≥4 miejsca rozpoznane w T2; dominanta 30–60% wysokości kadru; widać wejście pierwszego celu (kryteria 1, 2, 7) |
| **U2. Panorama ze spawnu** | 4 kadry z wysokości 5,5 studs, poziomo, na północ, wschód, południe i zachód | w każdym ≥2 punkty orientacyjne; budynki ≥50% horyzontu; 0% płyty bazowej (2, 3) |
| **U3. Wejście do miasta** | 16 studs przed bramą, w osi drogi, 5,5 studs, na środek rynku | dominanta widoczna w prześwicie; droga czytelna w szarości (4, 7) |
| **U4. Z progu dominanty** | w drzwiach głównego budynku, 5,5 studs, na rynek | widać 3 kolejne cele, nic ich nie zasłania (7, 8) |
| **U5. Uliczka z manekinem** | najwęższa uliczka, 5,5 studs, manekin 10 studs przed kamerą | skala, przechyły ≥5°, detal w pasie 0–14 studs (9, 10, 11) |
| **U6. Miniatura 3/4** | od strony słońca: (−0,75R; 0,6R; −0,5R), cel (0; 8; 0); dla R = 80 to (−60; 48; −40) | T1 w 256×144 i w ikonie 150×150; trzy plamy barwne (1, 5, 6) |
| **U7. Plan z góry** | rzut prostokątny z 300 studs, północ u góry | 60/30/10, zieleń ≤30%, brak osi symetrii (5, 6, 8) |
| **U8. Pod słońce** | lustrzanie do U6: (0,75R; 0,6R; 0,5R) | najgorszy przypadek, widać zacienione ściany; miejsca nadal różne od tła o ΔL* ≥20 (4, 10) |

U6 i U8 zakładają słońce na północnym zachodzie (odczyt z jednego zrzutu, ±30°); po sprawdzeniu w Studio obrócić. Słońce w Blenderze ustawić tak samo, inaczej podgląd kłamie.

## 6. Narzędzia pomiarowe

Folder `<folder roboczy>/ocena_robocze/`, tylko odczyt danych:
- `python ocena_kadru.py KADR.png --wyj KATALOG` — udziały barw, walor, 6 dominujących kolorów, pola największego kontrastu; zapisuje wersje do T1–T4.
- `python ocena_czesci.py czesci.json --spawn X Z` — wysokości grup, budżet części, mikrodetal, przechyły dużych brył, linia horyzontu ze spawnu, udział miejsc w wysokości ekranu.

## 7. Źródła (dostęp 13.11.2026)

Progi liczbowe to wartości robocze z geometrii kamery i pomiarów v1; źródła dają zasady. Limit wyszukiwań skończył się po 12 zapytaniach. Dystans kamery (archiwalne skrypty Roblox) i kierunek słońca trzeba potwierdzić w Studio.

- Roblox, Thumbnails (16:9, 1920×1080): https://create.roblox.com/docs/production/publishing/thumbnails
- Roblox, Icons (512×512, wyświetlane też w 150×150): https://create.roblox.com/docs/production/publishing/experience-icons
- Roblox, Customize the camera (pole widzenia 70°): https://create.roblox.com/docs/workspace/camera
- Roblox, Humanoid (chód 16 studs/s, skok 7,2 studs): https://create.roblox.com/docs/reference/engine/classes/Humanoid
- Roblox, Avatar Settings (awatar 5–6,5 studs): https://create.roblox.com/docs/studio/avatar-settings
- Roblox, Greybox your environment (przejścia i ściany od 10 studs): https://create.roblox.com/docs/tutorials/curriculums/environmental-art/greybox-your-environment
- Roblox, Test on hardware (większość graczy na słabszych telefonach; ekran 5″): https://create.roblox.com/docs/performance-optimization/test-on-hardware
- Roblox, Atmosphere (mgiełka zasłania dalekie obiekty): https://create.roblox.com/docs/reference/engine/classes/Atmosphere
- Roblox, Core-Scripts, RootCamera.lua (dystans kamery 12,5 studs; archiwum): https://github.com/Roblox/Core-Scripts/blob/master/PlayerScripts/StarterPlayerScripts/CameraScript/RootCamera.lua
- The Level Design Book, Composition (hierarchia z kontrastu; punkt orientacyjny musi być użyteczny): https://book.leveldesignbook.com/process/blockout/massing/composition
- The Level Design Book, Wayfinding (pięć elementów mapy mentalnej; gracz nie patrzy w górę bez powodu): https://book.leveldesignbook.com/process/blockout/wayfinding
- Valve, Illustrative Rendering in Team Fortress 2, slajdy 2007 (kontrast waloru, proste formy, mało szumu i powtórzeń): https://cdn.fastly.steamstatic.com/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2_Slides.pdf
- Valve, Dota 2 Workshop Character Art Guide (nasycenie na małych polach, miejsca odpoczynku; za wynikiem wyszukiwania): https://help.steampowered.com/faqs/view/0688-7692-4D5A-1935
- Game Developer, How to Reduce Visual Confusion in Your Game, 12.03.2015 (test szarości): https://www.gamedeveloper.com/design/how-to-reduce-visual-confusion-in-your-game
- 80.lv, The Strings of Environment Design, 4.07.2017 (mocna sylwetka; szum detalu zabija stylizację): https://80.lv/articles/the-strings-of-environment-design/
- itch.io, Color palettes and the 60-30-10 rule, 20.01.2023: https://itch.io/blog/478705/a-short-recommendation-color-palettes-and-the-60-30-10-rule
- Sejf, `B&C/Badania/Styl UI gier Roblox.md` (ok. 80% graczy na urządzeniach mobilnych, 2024).
