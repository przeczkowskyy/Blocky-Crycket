# Sklep z przedmiotami — stopnie ekwipunku trzech klas (D-106)

**Status: propozycja do oceny, nie kanon.** Część A zlecenia z 19.11.2026 (D-106: „kupując itemy… dojść do bramy
Pustyni”): katalog, modele w Blenderze, dane dla gry i testy — **bez Roblox Studio**. Przedmiotów nie ma jeszcze w grze
i nie da się ich kupić; to następne części (plan na końcu). Wygląd, nazwy, ceny, poziomy i statystyki czekają na ocenę
Karola i Pawła. Kontrakt modeli: `EKWIPUNEK.md` (D-071).

**Stan 19.11.2026 po części B (dalej bez Studio):** przymierzalnia zna wszystkie 80 przedmiotów, kowal liczy
statystyki nowych przedmiotów i umie je sprzedać, jest pakiet sklepu zbrojmistrza `swiat/sklep_proba/` z tymczasowym
oknem i testami. W Roblox Studio nic z tego nie jest jeszcze zbudowane ani obejrzane — rozdziały „Przedmioty w grze
i sklep” i „Plan części ze Studio” niżej.

## W skrócie
- Cztery stopnie: **startowy** (dzisiejsze 20 przedmiotów bohaterów, bez zmian) i trzy kupowane, po jednym na krainę:
  **leśny**, **bagienny**, **Dżungli**.
- Na stopień: Wojownik 8 przedmiotów (hełm, zbroja z nogawicami, pas, rękawice, buty, miecz, tarcza), Zwiadowca 8
  (kaptur, kirys ze spodniami, pas, rękawice, buty, sztylet, łuk z kołczanem), Mag 4 (nakrycie głowy, szata, szarfa,
  kostur) — tyle slotów ma dziś każda klasa. Razem **60 nowych przedmiotów**, w sklepie **54 pozycje** (nogawice
  i spodnie są w cenie zbroi) plus 18 startowych.
- Komplet stopnia kosztuje tyle samo w każdej klasie: **1 400 / 3 300 / 5 200 Złota** (las / Bagno / Dżungla),
  wymagane poziomy **2–7 / 10–15 / 17–22**.
- Dane do wczytania: `sklep_przedmioty.json` (jeden plik: wygląd, sloty, ceny, poziomy, statystyki).

## Czym różnią się stopnie z wyglądu
Każdy stopień ma własne materiały i własną sylwetkę hełmu, napierśnika i broni (nie sama zmiana koloru).
Plansze: `wynik/stopnie_wojownik/stopnie_wojownik_cztery_stopnie.jpg`,
`wynik/stopnie_zwiadowca/stopnie_zwiadowca_cztery_stopnie.jpg`, `wynik/stopnie_mag/stopnie_mag_cztery_stopnie.jpg`;
ikony: `wynik/stopnie_<klasa>/stopnie_<klasa>_ikony_arkusz.jpg`.

| | Las — skóra, drewno, futro, poroże | Bagno — łuski, kość, mosiądz | Dżungla — złoto, jadeit, pióra |
|---|---|---|---|
| **Wojownik** | hełm z porożem, futrzany kołnierz, naramienniki z kory, zielony tabard; miecz-liść; okrągła dębowa tarcza | hełm z kościanym grzebieniem i kłami, napierśnik z łusek z żebrami, kolce na naramiennikach (bez tabardu); szeroki tasak z zębami; owalna skorupa z kolcami | hełm z pióropuszem i dyskiem słońca, napierśnik z jadeitowym słońcem, uniesione skrzydła naramienników, pióra na plecach; zębaty miecz z dyskiem zamiast jelca; tarcza-słońce z piórami |
| **Zwiadowca** | brązowy kaptur z rudym piórem i futrem na barkach, ciemnozielony kirys z drewnianymi płytkami; nóż myśliwski ze ściętym czubkiem; łuk z listkami | ciemny kaptur z kolcami na grzbiecie i kłami, kolce na barkach i ramionach, łuski na kirysie; zakrzywiony kościany kieł; łuk z rogowymi końcami | kaptur bez szpica ze złotą opaską i wachlarzem piór, złoty pektorał, pióra na ramionach; jadeitowy sierp; złoty łuk z piórami |
| **Mag (kot)** | szeroki kapelusz zielarza z grzybkiem i piórem, brązowa szata z peleryną z liści; kostur zakręcony jak pastorał ze świecącym kryształem | łuskowy czepiec z rogami i czaszką, szata z kolczastymi naramiennikami i naszyjnikiem z kłów; kostur z rogatą czaszką | złota tiara z dyskiem słońca i wachlarzem piór, jadeitowa szata z pektorałem i piórami; berło z dyskiem słońca |

Jak to jest zbudowane (`stopnie.py`): części zbroi na kościach to dzisiejsze bryły (te same warstwy, powłoki i kości
co w kontrakcie) w materiałach krainy, bez wybranych brył (grzebień hełmu, tabard, szpic kaptura…) i z dołożonymi
bryłami sylwetki; broń, tarcze, nakrycia głowy kota i kostury są nowe, w tej samej ramce chwytu. Pas, rękawice i buty
różnią się materiałem i jedną ozdobą (futro / kolec / jadeit z piórami).

## Katalog
Statystyki to te same rodzaje i ta sama skala co u kowala (`swiat/kowal_proba/ustawienia.json`): „+0” = `baza`,
„za ulepszenie” = `krok` (przyrost za każdy poziom +1…+5). „Jak dziś” = broń i pancerz ze wzoru poziomu.

### Wojownik

| Stopień | Slot | Przedmiot (id) | Wygląd | Statystyki +0 | Za ulepszenie | Poziom | Cena |
|---|---|---|---|---|---|---:|---:|
| Startowy | Nakrycie głowy | Hełm Rycerza (`rycerz_helm`) | dzisiejszy przedmiot bohatera | Pancerz +2 · Kondycja +1 | Kondycja +1 | 1 | 75 |
| Startowy | Zbroja | Zbroja Rycerza z tabardem (`rycerz_zbroja`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Pancerz +3 | 1 | od startu |
| Startowy | Zbroja | Nogawice Rycerza (`rycerz_nogawice`) | dzisiejszy przedmiot bohatera | w cenie: `rycerz_zbroja` | | | |
| Startowy | Pas | Pas Rycerza (`rycerz_pas`) | dzisiejszy przedmiot bohatera | Kondycja +1 | Kondycja +1 | 1 | 75 |
| Startowy | Rękawice | Rękawice Rycerza (`rycerz_rekawice`) | dzisiejszy przedmiot bohatera | Siła +2 | Siła +1 | 1 | 75 |
| Startowy | Buty | Trzewiki z nagolennikami (`rycerz_buty`) | dzisiejszy przedmiot bohatera | Zręczność +2 | Zręczność +1 | 1 | 75 |
| Startowy | Broń | Wielki miecz Rycerza (`rycerz_miecz`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Broń +1 | 1 | od startu |
| Startowy | Druga ręka | Tarcza Rycerza (`rycerz_tarcza`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Blok +1 pp | 1 | od startu |
| Leśny | Nakrycie głowy | Hełm Leśnego Strażnika (`rycerz_las_helm`) | skórzany hełm z jasnym porożem po bokach i futrem na karku | Pancerz +2 · Kondycja +2 | Kondycja +1 | 5 | 200 |
| Leśny | Zbroja | Zbroja Leśnego Strażnika (`rycerz_las_zbroja`) | utwardzana skóra, futrzany kołnierz, naramienniki z płatów kory, zielony tabard z drewnianą lamówką | Pancerz +4 | Pancerz +3 | 6 | 350 |
| Leśny | Zbroja | Nogawice Leśnego Strażnika (`rycerz_las_nogawice`) | skórzane uda z ciemną płytą, część zbroi | w cenie: `rycerz_las_zbroja` | | | |
| Leśny | Pas | Pas Leśnika z Sakiewką (`rycerz_las_pas`) | szeroki ciemny pas z drewnianą klamrą i sakiewką przy biodrze | Kondycja +2 | Kondycja +1 | 2 | 100 |
| Leśny | Rękawice | Rękawice z Futrem (`rycerz_las_rekawice`) | skórzane rękawice z futrzanym mankietem | Siła +3 | Siła +1 | 3 | 100 |
| Leśny | Buty | Buty Leśnika z Futrem (`rycerz_las_buty`) | skórzane buty z futrzanym wywinięciem pod kolanem | Zręczność +3 | Zręczność +1 | 4 | 100 |
| Leśny | Broń | Liściasty Miecz Gaju (`rycerz_las_miecz`) | żelazna klinga w kształcie liścia z zieloną żyłką, jelec z gałązek | Broń +2 | Broń +1 | 7 | 350 |
| Leśny | Druga ręka | Dębowa Tarcza (`rycerz_las_tarcza`) | okrągła tarcza z jasnych desek z ciemną obręczą, żelaznym umbem i listkiem | Blok +2 pp · Kondycja +1 | Blok +1 pp | 5 | 200 |
| Bagienny | Nakrycie głowy | Hełm Topielca (`rycerz_bagno_helm`) | łuskowy hełm z kościanym grzebieniem i dwoma kłami przy policzkach | Pancerz +4 · Kondycja +4 | Kondycja +2 | 13 | 450 |
| Bagienny | Zbroja | Łuskowa Zbroja Topieli (`rycerz_bagno_zbroja`) | napierśnik z rombów łusek, kościane żebra i mostek, po trzy kolce na naramiennikach, mosiężne okucia | Pancerz +8 | Pancerz +4 | 14 | 800 |
| Bagienny | Zbroja | Łuskowe Nogawice Topieli (`rycerz_bagno_nogawice`) | łuskowe uda z ciemniejszą płytą, część zbroi | w cenie: `rycerz_bagno_zbroja` | | | |
| Bagienny | Pas | Pas z Kłami (`rycerz_bagno_pas`) | ciemny pas z mosiężną klamrą i dwoma wiszącymi kłami | Kondycja +4 | Kondycja +2 | 10 | 250 |
| Bagienny | Rękawice | Kolczaste Rękawice Topieli (`rycerz_bagno_rekawice`) | łuskowe rękawice z kościanymi kolcami na kostkach | Siła +6 | Siła +2 | 11 | 250 |
| Bagienny | Buty | Łuskowe Buty z Kolcem (`rycerz_bagno_buty`) | łuskowe buty z kościanym kolcem na kolanie | Zręczność +6 | Zręczność +2 | 12 | 250 |
| Bagienny | Broń | Kościany Tasak Topieli (`rycerz_bagno_miecz`) | szeroki tasak rozszerzający się ku górze, zęby z kości na ostrzu, mosiężny jelec | Broń +4 | Broń +2 | 15 | 850 |
| Bagienny | Druga ręka | Tarcza ze Skorupy (`rycerz_bagno_tarcza`) | owalna skorupa z płytkami, mosiężny brzeg, cztery kościane kolce i guz | Blok +4 pp · Kondycja +2 | Blok +1 pp | 13 | 450 |
| Dżungli | Nakrycie głowy | Hełm Słońca z Pióropuszem (`rycerz_dzungla_helm`) | złoty hełm z wachlarzem pięciu piór i słonecznym dyskiem na czole | Pancerz +6 · Kondycja +6 | Kondycja +3 | 20 | 750 |
| Dżungli | Zbroja | Złota Zbroja Słońca (`rycerz_dzungla_zbroja`) | złoty napierśnik z jadeitowym dyskiem i promieniami, uniesione skrzydła naramienników, trzy pióra na plecach | Pancerz +12 | Pancerz +5 | 21 | 1 250 |
| Dżungli | Zbroja | Złote Nogawice Słońca (`rycerz_dzungla_nogawice`) | złote uda z płytą, część zbroi | w cenie: `rycerz_dzungla_zbroja` | | | |
| Dżungli | Pas | Pas z Jadeitowym Dyskiem (`rycerz_dzungla_pas`) | ciemnozłoty pas z jadeitowym dyskiem i piórami przy biodrach | Kondycja +6 | Kondycja +3 | 17 | 400 |
| Dżungli | Rękawice | Rękawice z Jadeitem (`rycerz_dzungla_rekawice`) | złote rękawice z jadeitową bransoletą | Siła +9 | Siła +3 | 18 | 400 |
| Dżungli | Buty | Złote Buty z Jadeitem (`rycerz_dzungla_buty`) | złote buty z jadeitowym dyskiem na kolanie i opaską z piór przy kostce | Zręczność +9 | Zręczność +3 | 19 | 400 |
| Dżungli | Broń | Zębaty Miecz Słońca (`rycerz_dzungla_miecz`) | płaska złota klinga z jadeitowymi zębami po obu stronach, dysk słońca zamiast jelca, pióra przy głowicy | Broń +6 | Broń +3 | 22 | 1 250 |
| Dżungli | Druga ręka | Tarcza Słońca (`rycerz_dzungla_tarcza`) | złoty dysk z jadeitowym pierścieniem, promienie u góry i pióra u dołu | Blok +6 pp · Kondycja +3 | Blok +1 pp | 20 | 750 |

### Zwiadowca

| Stopień | Slot | Przedmiot (id) | Wygląd | Statystyki +0 | Za ulepszenie | Poziom | Cena |
|---|---|---|---|---|---|---:|---:|
| Startowy | Nakrycie głowy | Kaptur z peleryną (`zwiadowca_kaptur`) | dzisiejszy przedmiot bohatera | Pancerz +2 · Zręczność +1 | Szczęście +1 | 1 | 60 |
| Startowy | Zbroja | Skórzany kirys z tuniką (`zwiadowca_kurtka`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Pancerz +3 | 1 | od startu |
| Startowy | Zbroja | Spodnie Zwiadowcy (`zwiadowca_spodnie`) | dzisiejszy przedmiot bohatera | w cenie: `zwiadowca_kurtka` | | | |
| Startowy | Pas | Pas z sakwą (`zwiadowca_pas`) | dzisiejszy przedmiot bohatera | Kondycja +1 | Kondycja +1 | 1 | 60 |
| Startowy | Rękawice | Rękawice bez palców (`zwiadowca_rekawice`) | dzisiejszy przedmiot bohatera | Siła +1 | Siła +1 | 1 | 60 |
| Startowy | Buty | Buty z wywiniętą cholewą (`zwiadowca_buty`) | dzisiejszy przedmiot bohatera | Zręczność +2 | Zręczność +1 | 1 | 60 |
| Startowy | Druga ręka | Łuk z kołczanem (`zwiadowca_luk`) | dzisiejszy przedmiot bohatera | Szczęście +2 | Broń +1 | 1 | 60 |
| Startowy | Broń | Sztylet Zwiadowcy (`zwiadowca_sztylet`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Broń +1 | 1 | od startu |
| Leśny | Nakrycie głowy | Kaptur Tropiciela z Futrem (`zwiadowca_las_kaptur`) | brązowy skórzany kaptur z rudym piórem i futrem na barkach | Pancerz +2 · Zręczność +3 | Szczęście +1 | 5 | 200 |
| Leśny | Zbroja | Kirys Tropiciela (`zwiadowca_las_kurtka`) | ciemnozielony kirys na brązowej tunice, drewniane płytki na ramionach, jasnozielona chusta | Pancerz +4 | Pancerz +3 | 6 | 350 |
| Leśny | Zbroja | Spodnie Tropiciela (`zwiadowca_las_spodnie`) | ciemnobrązowe spodnie, część kirysu | w cenie: `zwiadowca_las_kurtka` | | | |
| Leśny | Pas | Pas Tropiciela (`zwiadowca_las_pas`) | ciemny pas z drewnianą klamrą i sakwą | Kondycja +2 | Kondycja +1 | 2 | 100 |
| Leśny | Rękawice | Rękawice Tropiciela (`zwiadowca_las_rekawice`) | rękawice bez palców z futrzanym mankietem | Siła +3 | Siła +1 | 3 | 100 |
| Leśny | Buty | Buty Tropiciela (`zwiadowca_las_buty`) | buty z futrzanym wywinięciem | Zręczność +3 | Zręczność +1 | 4 | 100 |
| Leśny | Druga ręka | Łuk Gaju z Kołczanem (`zwiadowca_las_luk`) | ciemny drewniany łuk z listkami na końcach, zielone lotki | Broń +2 · Szczęście +2 | Broń +1 | 5 | 200 |
| Leśny | Broń | Nóż Myśliwski (`zwiadowca_las_sztylet`) | szeroki nóż ze ściętym czubkiem i ząbkami na grzbiecie, rękojeść z poroża | Broń +2 | Broń +1 | 7 | 350 |
| Bagienny | Nakrycie głowy | Kaptur z Wężowej Łuski (`zwiadowca_bagno_kaptur`) | ciemny kaptur z kościanymi kolcami na grzbiecie, kłami nad czołem i kolcami na barkach | Pancerz +4 · Zręczność +6 | Szczęście +2 | 13 | 450 |
| Bagienny | Zbroja | Łuskowy Kirys Topieli (`zwiadowca_bagno_kurtka`) | łuskowy kirys z rombami łusek, kościane kolce na ramionach, kościana chusta | Pancerz +8 | Pancerz +4 | 14 | 800 |
| Bagienny | Zbroja | Spodnie z Wężowej Skóry (`zwiadowca_bagno_spodnie`) | ciemne spodnie, część kirysu | w cenie: `zwiadowca_bagno_kurtka` | | | |
| Bagienny | Pas | Pas z Mosiężną Klamrą (`zwiadowca_bagno_pas`) | łuskowy pas z mosiężną klamrą i sakwą | Kondycja +4 | Kondycja +2 | 10 | 250 |
| Bagienny | Rękawice | Rękawice z Kolcami (`zwiadowca_bagno_rekawice`) | rękawice bez palców z kościanymi kolcami na kostkach | Siła +6 | Siła +2 | 11 | 250 |
| Bagienny | Buty | Buty Brodzące (`zwiadowca_bagno_buty`) | łuskowe buty z mosiężnym wywinięciem i kolcem na kolanie | Zręczność +6 | Zręczność +2 | 12 | 250 |
| Bagienny | Druga ręka | Kościany Łuk z Kołczanem (`zwiadowca_bagno_luk`) | łuk z kości z rogowymi końcami, kościane lotki | Broń +4 · Szczęście +4 | Broń +2 | 13 | 450 |
| Bagienny | Broń | Kieł Topielca (`zwiadowca_bagno_sztylet`) | zakrzywiony kościany kieł na mosiężnym jelcu | Broń +4 | Broń +2 | 15 | 850 |
| Dżungli | Nakrycie głowy | Pióropusz Jaguara (`zwiadowca_dzungla_kaptur`) | jadeitowy kaptur bez szpica, złota opaska z klejnotem i wachlarz pięciu piór z tyłu głowy | Pancerz +6 · Zręczność +9 | Szczęście +3 | 20 | 750 |
| Dżungli | Zbroja | Kirys ze Złotym Pektorałem (`zwiadowca_dzungla_kurtka`) | złoty kirys na jadeitowej tunice, szeroki pektorał z klejnotem, pióra na ramionach | Pancerz +12 | Pancerz +5 | 21 | 1 250 |
| Dżungli | Zbroja | Jadeitowe Spodnie (`zwiadowca_dzungla_spodnie`) | ciemnojadeitowe spodnie, część kirysu | w cenie: `zwiadowca_dzungla_kurtka` | | | |
| Dżungli | Pas | Pas Jaguara (`zwiadowca_dzungla_pas`) | złoty pas z jadeitową klamrą i sakwą | Kondycja +6 | Kondycja +3 | 17 | 400 |
| Dżungli | Rękawice | Rękawice z Jadeitową Bransoletą (`zwiadowca_dzungla_rekawice`) | rękawice bez palców z jadeitową bransoletą | Siła +9 | Siła +3 | 18 | 400 |
| Dżungli | Buty | Złote Buty Jaguara (`zwiadowca_dzungla_buty`) | złote buty z jadeitowym dyskiem na kolanie i piórami przy kostce | Zręczność +9 | Zręczność +3 | 19 | 400 |
| Dżungli | Druga ręka | Łuk Słońca z Kołczanem (`zwiadowca_dzungla_luk`) | złoty łuk z piórami na końcach, czerwone lotki | Broń +6 · Szczęście +6 | Broń +3 | 20 | 750 |
| Dżungli | Broń | Jadeitowy Sierp (`zwiadowca_dzungla_sztylet`) | szerokie jadeitowe ostrze z zagiętym czubkiem, złote skrzydełka jelca, czerwony klejnot w głowicy | Broń +6 | Broń +3 | 22 | 1 250 |

### Mag

| Stopień | Slot | Przedmiot (id) | Wygląd | Statystyki +0 | Za ulepszenie | Poziom | Cena |
|---|---|---|---|---|---|---:|---:|
| Startowy | Nakrycie głowy | Kapelusz Kota-Maga (`kot_mag_kapelusz`) | dzisiejszy przedmiot bohatera | Kondycja +2 · Inteligencja +2 | Kondycja +1 · Inteligencja +1 | 1 | 150 |
| Startowy | Zbroja | Szata Kota-Maga (`kot_mag_szata`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Pancerz +3 · Kondycja +1 | 1 | od startu |
| Startowy | Pas | Szarfa z klamrą (`kot_mag_pas`) | dzisiejszy przedmiot bohatera | Siła +1 · Kondycja +2 | Siła +1 · Kondycja +1 | 1 | 150 |
| Startowy | Broń | Kostur Kota-Maga (`kot_mag_kostur`) | dzisiejszy przedmiot bohatera | jak dziś (wzór poziomu) | Broń +1 · Inteligencja +1 | 1 | od startu |
| Leśny | Nakrycie głowy | Kapelusz Zielarza (`kot_mag_las_kapelusz`) | szeroki skórzany kapelusz z płaską główką, zieloną wstążką, grzybkiem na rondzie i piórem | Kondycja +2 · Inteligencja +3 | Kondycja +1 · Inteligencja +1 | 5 | 300 |
| Leśny | Zbroja | Szata z Liści (`kot_mag_las_szata`) | brązowa szata z zielonymi obszyciami i peleryną z liści na ramionach | Pancerz +5 · Kondycja +2 | Pancerz +3 · Kondycja +1 | 6 | 400 |
| Leśny | Pas | Szarfa Zielarza (`kot_mag_las_pas`) | zielona szarfa z drewnianą klamrą i sakiewką | Siła +2 · Kondycja +2 | Siła +1 · Kondycja +1 | 2 | 200 |
| Leśny | Broń | Kostur z Korzenia (`kot_mag_las_kostur`) | ciemny kostur zakręcony u góry jak pastorał, w zakręcie świecący kryształ | Broń +2 · Inteligencja +2 | Broń +1 · Inteligencja +1 | 7 | 500 |
| Bagienny | Nakrycie głowy | Rogaty Czepiec Szamana (`kot_mag_bagno_kapelusz`) | łuskowy czepiec bez ronda z dwoma rogami, kościaną czaszką nad czołem i grzebieniem | Kondycja +4 · Inteligencja +6 | Kondycja +2 · Inteligencja +2 | 13 | 650 |
| Bagienny | Zbroja | Szata Szamana Topieli (`kot_mag_bagno_szata`) | łuskowa szata z kapturem, naramienniki z kolcami i naszyjnik z kłów | Pancerz +10 · Kondycja +4 | Pancerz +4 · Kondycja +2 | 14 | 1 000 |
| Bagienny | Pas | Szarfa z Kłem (`kot_mag_bagno_pas`) | ciemna szarfa z mosiężną klamrą i kłem | Siła +4 · Kondycja +4 | Siła +2 · Kondycja +2 | 10 | 550 |
| Bagienny | Broń | Kostur z Czaszką (`kot_mag_bagno_kostur`) | kościany kostur z rogatą czaszką o świecących oczach i mosiężnymi obręczami | Broń +4 · Inteligencja +4 | Broń +2 · Inteligencja +2 | 15 | 1 100 |
| Dżungli | Nakrycie głowy | Tiara Słońca (`kot_mag_dzungla_kapelusz`) | złota tiara z jadeitowym klejnotem, dyskiem słońca i wachlarzem piór | Kondycja +6 · Inteligencja +9 | Kondycja +3 · Inteligencja +3 | 20 | 1 050 |
| Dżungli | Zbroja | Szata Kapłana Słońca (`kot_mag_dzungla_szata`) | jadeitowa szata ze złotym pektorałem, wachlarze piór na ramionach i dysk słońca na plecach | Pancerz +15 · Kondycja +6 | Pancerz +5 · Kondycja +3 | 21 | 1 550 |
| Dżungli | Pas | Szarfa z Jadeitem (`kot_mag_dzungla_pas`) | jadeitowa szarfa ze złotą klamrą i dyskiem | Siła +6 · Kondycja +6 | Siła +3 · Kondycja +3 | 17 | 850 |
| Dżungli | Broń | Berło Słońca (`kot_mag_dzungla_kostur`) | złote berło z dyskiem słońca, promieniami, jadeitowym klejnotem i piórami | Broń +6 · Inteligencja +6 | Broń +3 · Inteligencja +3 | 22 | 1 750 |

## Rachunek cen, poziomów i statystyk (`sklep_ceny.py`, propozycja do oceny)

### 1. Źródła: potwory krain, ich poziomy i Złoto za wygraną

Złoto za wygraną = baza + przyrost × poziom potwora (średnio; silnik losuje 80–120% tej liczby). Przegrody z pakietów krain (`zrodla/DanePotworow*.luau`), łup z `tools/walka/dane_walki.json` i `przeciwnicy.py` Bagna i Dżungli.

| Kraina | Przegroda | Potwór | Poziomy | Złoto za wygraną |
|---|---|---|---|---|
| Las | s1 | Leśny Slime | 1–3 | 28–44 |
| Las | m1 | Muchomornik | 3–5 | 49–67 |
| Las | w1 | Cierniowy Wilk | 6–8 | 76–94 |
| Las | t1 | Leśny Troll (rzadki) | 8–9 | 270–295 |
| Las | straznik | Strażnik Gaju (Strażnik) | 10 | 650 |
| Bagno | r1 | Rechotek | 10–12 | 112–130 |
| Bagno | b1 | Bulgotnik | 12–14 | 130–148 |
| Bagno | k1 | Kłodokłap | 14–16 | 148–166 |
| Bagno | t1 | Ropucha z Chatką (rzadki) | 16 | 470 |
| Bagno | straznik | Strażnik Topieli (Strażnik) | 16 | 950 |
| Dżungla | z1 | Zwijogon | 17–19 | 175–193 |
| Dżungla | g1 | Gębokwiat | 19–21 | 193–211 |
| Dżungla | o1 | Kokosowy Siłacz | 21–23 | 211–229 |
| Dżungla | t1 | Pancernik Ruin (rzadki) | 23 | 645 |
| Dżungla | straznik | Wąż Stu Lian (Strażnik) | 23 | 1 300 |

### 2. Dochód Złota dziś (bez sklepu)

60 graczy na klasę przechodzi po kolei las, Bagno i Dżunglę prawdziwym silnikiem walki; bohater ze wzoru poziomu (broń 8 + 4 × poziom, pancerz 3 + 1,5 × poziom), polityka gracza jak w `symulacja_lasu.py`. Mediany; Złoto na walkę liczone ze wszystkich walk (także przegranych). Bez petów, łupu przedmiotów i ulepszeń — to dolna granica dochodu.

| Kraina | Poziom na wejściu → po Strażniku | Minut do Strażnika | Walk | Przegranych | Złoto z walk | Złoto na walkę | Złoto na minutę | Cena jajka |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Las | 1 → 12 | 26,4 | 42 | 9 | 3 413 | 82 | 130 | 300 |
| Bagno | 12 → 19 | 46,6 | 62 | 18 | 8 341 | 137 | 180 | 750 |
| Dżungla | 19 → 25 | 48,0 | 70 | 19 | 13 027 | 193 | 274 | 1 350 |

### 3. Ceny

Komplet stopnia = 40% Złota, które kraina daje do wygranej ze Strażnikiem (tabela 2), zaokrąglone do 100. Reszta zostaje na jajka i ulepszenia u kowala (jeden przedmiot do +5: 2 450 Złota). Podział na sloty: broń 24%, tors 24%, nakrycie głowy 14%, druga ręka 14%, rękawice, buty i pas po 8%; Mag ma cztery przedmioty (broń 34%, tors 30%, nakrycie głowy 20%, pas 16%), więc komplet każdej klasy kosztuje tyle samo. Ceny zaokrąglone do 50, resztę z zaokrągleń bierze broń.

| Stopień | Wymagany poziom | Komplet | Walk na komplet | Minut na komplet | Część Złota krainy | Jajek za tę samą kwotę |
|---|---|---:|---:|---:|---:|---:|
| Leśny (Las) | 2–7 | 1 400 | 17 | 11 | 41% | 4,7 |
| Bagienny (Bagno) | 10–15 | 3 300 | 24 | 18 | 40% | 4,4 |
| Dżungli (Dżungla) | 17–22 | 5 200 | 27 | 19 | 40% | 3,9 |

Stopień startowy: zestaw podstawowy (broń, tors, tarcza Wojownika) gracz ma od początku, cena 0. Pozostałe przedmioty startowe (dziś tylko z łupu) kosztują razem 300 Złota w każdej klasie — tyle, ile daje 8 wygranych w pierwszej przegrodzie lasu — po równo na sztukę (Wojownik 4 sztuki, Zwiadowca 5, Mag 2).

| Slot | Wymagany poziom: las / Bagno / Dżungla | Wojownik i Zwiadowca: start / las / Bagno / Dżungla | Walk na sztukę: las / Bagno / Dżungla | Mag: start / las / Bagno / Dżungla |
|---|---|---|---|---|
| nakrycie głowy | 5 / 13 / 20 | 75 (Zwiadowca 60) / 200 / 450 / 750 | 2,4 / 3,3 / 3,9 | 150 / 300 / 650 / 1 050 |
| tors (z nogami) | 6 / 14 / 21 | 0 / 350 / 800 / 1 250 | 4,3 / 5,8 / 6,5 | 0 / 400 / 1 000 / 1 550 |
| pas | 2 / 10 / 17 | 75 (Zwiadowca 60) / 100 / 250 / 400 | 1,2 / 1,8 / 2,1 | 150 / 200 / 550 / 850 |
| rękawice | 3 / 11 / 18 | 75 (Zwiadowca 60) / 100 / 250 / 400 | 1,2 / 1,8 / 2,1 | — |
| buty | 4 / 12 / 19 | 75 (Zwiadowca 60) / 100 / 250 / 400 | 1,2 / 1,8 / 2,1 | — |
| broń | 7 / 15 / 22 | 0 / 350 / 850 / 1 250 | 4,3 / 6,2 / 6,5 | 0 / 500 / 1 100 / 1 750 |
| druga ręka | 5 / 13 / 20 | 0 (Zwiadowca 60) / 200 / 450 / 750 | 2,4 / 3,3 / 3,9 | — |

### 4. Statystyki (+0 → przyrost za poziom ulepszenia)

Rodzaje statystyk w slocie jak u kowala. Stopień lasu = przepis slotu × 1, Bagna × 2, Dżungli × 3 — wzór poziomu rośnie liniowo (broń ze wzoru w połowie lasu 28, Bagna 60, Dżungli 88), więc stałe dodatki rosną z krainą w tym samym tempie i komplet znaczy w każdej krainie mniej więcej tyle samo. Blok tarczy +2 pp na stopień. Broń i tors startowe liczą się ze wzoru poziomu, a przedmioty stopni dodają ponad wzór. Przyrost za ulepszenie: stopień lasu jak przedmiot startowy, wyżej × numer stopnia (pancerz +1 na stopień, blok zawsze +1 pp).

**Wojownik**

| Slot | Startowy | Leśny | Bagienny | Dżungli |
|---|---|---|---|---|
| nakrycie głowy | Pancerz +2 · Kondycja +1 → Kondycja +1 | Pancerz +2 · Kondycja +2 → Kondycja +1 | Pancerz +4 · Kondycja +4 → Kondycja +2 | Pancerz +6 · Kondycja +6 → Kondycja +3 |
| tors (z nogami) | — (ze wzoru poziomu) → Pancerz +3 | Pancerz +4 → Pancerz +3 | Pancerz +8 → Pancerz +4 | Pancerz +12 → Pancerz +5 |
| pas | Kondycja +1 → Kondycja +1 | Kondycja +2 → Kondycja +1 | Kondycja +4 → Kondycja +2 | Kondycja +6 → Kondycja +3 |
| rękawice | Siła +2 → Siła +1 | Siła +3 → Siła +1 | Siła +6 → Siła +2 | Siła +9 → Siła +3 |
| buty | Zręczność +2 → Zręczność +1 | Zręczność +3 → Zręczność +1 | Zręczność +6 → Zręczność +2 | Zręczność +9 → Zręczność +3 |
| broń | — (ze wzoru poziomu) → Broń +1 | Broń +2 → Broń +1 | Broń +4 → Broń +2 | Broń +6 → Broń +3 |
| druga ręka | — (ze wzoru poziomu) → Blok +1% | Kondycja +1 · Blok +2% → Blok +1% | Kondycja +2 · Blok +4% → Blok +1% | Kondycja +3 · Blok +6% → Blok +1% |

**Zwiadowca**

| Slot | Startowy | Leśny | Bagienny | Dżungli |
|---|---|---|---|---|
| nakrycie głowy | Pancerz +2 · Zręczność +1 → Szczęście +1 | Pancerz +2 · Zręczność +3 → Szczęście +1 | Pancerz +4 · Zręczność +6 → Szczęście +2 | Pancerz +6 · Zręczność +9 → Szczęście +3 |
| tors (z nogami) | — (ze wzoru poziomu) → Pancerz +3 | Pancerz +4 → Pancerz +3 | Pancerz +8 → Pancerz +4 | Pancerz +12 → Pancerz +5 |
| pas | Kondycja +1 → Kondycja +1 | Kondycja +2 → Kondycja +1 | Kondycja +4 → Kondycja +2 | Kondycja +6 → Kondycja +3 |
| rękawice | Siła +1 → Siła +1 | Siła +3 → Siła +1 | Siła +6 → Siła +2 | Siła +9 → Siła +3 |
| buty | Zręczność +2 → Zręczność +1 | Zręczność +3 → Zręczność +1 | Zręczność +6 → Zręczność +2 | Zręczność +9 → Zręczność +3 |
| broń | — (ze wzoru poziomu) → Broń +1 | Broń +2 → Broń +1 | Broń +4 → Broń +2 | Broń +6 → Broń +3 |
| druga ręka | Szczęście +2 → Broń +1 | Broń +2 · Szczęście +2 → Broń +1 | Broń +4 · Szczęście +4 → Broń +2 | Broń +6 · Szczęście +6 → Broń +3 |

**Mag**

| Slot | Startowy | Leśny | Bagienny | Dżungli |
|---|---|---|---|---|
| nakrycie głowy | Kondycja +2 · Inteligencja +2 → Kondycja +1 · Inteligencja +1 | Kondycja +2 · Inteligencja +3 → Kondycja +1 · Inteligencja +1 | Kondycja +4 · Inteligencja +6 → Kondycja +2 · Inteligencja +2 | Kondycja +6 · Inteligencja +9 → Kondycja +3 · Inteligencja +3 |
| tors (z nogami) | — (ze wzoru poziomu) → Pancerz +3 · Kondycja +1 | Pancerz +5 · Kondycja +2 → Pancerz +3 · Kondycja +1 | Pancerz +10 · Kondycja +4 → Pancerz +4 · Kondycja +2 | Pancerz +15 · Kondycja +6 → Pancerz +5 · Kondycja +3 |
| pas | Kondycja +2 · Siła +1 → Kondycja +1 · Siła +1 | Kondycja +2 · Siła +2 → Kondycja +1 · Siła +1 | Kondycja +4 · Siła +4 → Kondycja +2 · Siła +2 | Kondycja +6 · Siła +6 → Kondycja +3 · Siła +3 |
| broń | — (ze wzoru poziomu) → Broń +1 · Inteligencja +1 | Broń +2 · Inteligencja +2 → Broń +1 · Inteligencja +1 | Broń +4 · Inteligencja +4 → Broń +2 · Inteligencja +2 | Broń +6 · Inteligencja +6 → Broń +3 · Inteligencja +3 |

### 5. Szansa wygranej w krainie (300 walk na przegrodę)

Bohater na najniższym poziomie przegrody, potwór z jej zakresu (jak w kalkulatorze kowala), więc Strażnik wypada tu trudniej niż w grze, gdzie gracz przychodzi do niego o poziom–dwa wyżej. „Potwory” = średnia po przegrodach bez Strażnika. Zestaw podstawowy = dzisiejszy wzór poziomu. Zapis: potwory / Strażnik.

| Kraina | Klasa | Zestaw podstawowy | Komplet poprzedniego stopnia | Komplet stopnia krainy +0 | Komplet stopnia krainy +5 |
|---|---|---:|---:|---:|---:|
| Las | Wojownik | 58% / 41% | 68% / 44% | 81% / 58% | 97% / 90% |
| Las | Zwiadowca | 60% / 39% | 65% / 45% | 77% / 57% | 96% / 88% |
| Las | Mag | 59% / 32% | 68% / 41% | 80% / 56% | 98% / 94% |
| Bagno | Wojownik | 60% / 15% | 69% / 29% | 78% / 39% | 96% / 85% |
| Bagno | Zwiadowca | 61% / 18% | 70% / 38% | 78% / 38% | 93% / 78% |
| Bagno | Mag | 60% / 12% | 75% / 15% | 80% / 33% | 98% / 78% |
| Dżungla | Wojownik | 63% / 17% | 82% / 41% | 88% / 53% | 98% / 85% |
| Dżungla | Zwiadowca | 64% / 22% | 79% / 37% | 84% / 43% | 96% / 78% |
| Dżungla | Mag | 67% / 16% | 82% / 28% | 87% / 36% | 98% / 85% |

Różnica między klasami w komplecie stopnia krainy (potwory): Las 3,4 pp, Bagno 2,5 pp, Dżungla 5,0 pp.

### 6. Gracz ze sklepem (te same krainy, 60 graczy na klasę)

50% Złota z wygranych idzie do sakiewki sklepu; przy wizycie (najwyżej co 5 min, trwa 40 s) gracz kupuje najtańsze przedmioty stopnia krainy, na które go stać i które wolno mu nosić. Bez łupu przedmiotów, ulepszeń, jajek i petów — sam wpływ sklepu.

| Kraina | Minut do Strażnika: dziś → ze sklepem | Przegranych: dziś → ze sklepem | Kupionych do Strażnika | Komplet przed Strażnikiem | Minut ze sklepem: Wojownik / Zwiadowca / Mag |
|---|---|---|---:|---|---|
| Las | 26,4 → 26,3 | 9 → 7 | 5 | 38% graczy, mediana po 27 min | 27,2 / 27,0 / 25,2 |
| Bagno | 46,6 → 40,3 | 18 → 11 | 7 | 80% graczy, mediana po 37 min | 42,3 / 41,5 / 36,9 |
| Dżungla | 48,0 → 43,8 | 19 → 11 | 4 | 63% graczy, mediana po 41 min | 46,2 / 44,1 / 40,5 |

### 7. Co przyjęte ręcznie (wybory do oceny)

1. **Komplet = 40% Złota krainy.** Mniej — sklep przestaje być celem; więcej — nie zostaje na jajka i kowala.
2. **Podział ceny na sloty** (broń i tors najdroższe, pas, rękawice i buty najtańsze — pierwszy zakup po jednej–dwóch wygranych) i **równa cena kompletu w każdej klasie** (Mag: cztery droższe sztuki).
3. **Wymagane poziomy:** od najniższego poziomu potworów krainy (las od 2.), sloty co poziom w kolejności pas, rękawice, buty, nakrycie głowy i druga ręka, tors, broń. Bez wymagań gracz kupiłby komplet Dżungli za Złoto nazbierane w Bagnie.
4. **Wielkość statystyk:** mnożniki stopni 1 / 2 / 3 i przepisy slotów — dobrane tak, żeby komplet podnosił szansę z potworami swojej krainy z ok. 60% do ok. 80%, a ze Strażnikiem z ok. 10–40% do ok. 35–60% (tabela 5); klasy wyrównane doborem przepisów.
5. **Przedmiot wyższego stopnia przy +0 jest słabszy niż poprzedni ulepszony do +2 i wyżej.** Do decyzji: czy ulepszenia przechodzą na nowy przedmiot, czy stary idzie do rozbiórki na materiały.
6. **Przedmioty startowe spoza zestawu podstawowego za Złoto** (razem 300 w klasie) — dziś wypadają tylko z łupu; cena jest dopłatą dla tych, którzy nie chcą czekać na łup.
7. **Koszty ulepszeń u kowala bez zmian** (te same dla każdego stopnia, waga Maga 1,75) — przy droższych stopniach ulepszenie robi się względnie tanie; osobny wybór dla kowala.
8. **D-107** (walka bez przestojów, więcej potworów) skróci czas między walkami, więc Złoto na minutę wzrośnie, a Złoto na walkę i ceny liczone w walkach zostaną.

_python -B swiat/postacie/sklep_ceny.py (graczy 60, walk 300, ziarno 1)_

## Kontrola modeli (bez Blendera)
`python -B swiat/postacie/test_stopnie.py` — 11 testów, ok. 10 s. Pomiar przenikania kompletów **w pozie wyjściowej
szkieletu** (bryły liczone jak prostopadłościany, więc kolce i pióra wychodzą trochę za głęboko): pierwsza liczba —
jak głęboko przedmiot z dłoni albo z głowy kota wchodzi w głowę, tułów, biodra i nogi (próg kontraktu 0,06 studa albo
wynik kompletu startowego); druga — jak głęboko bryły zbroi wchodzą w bryły innych kości (próg: komplet startowy
+ 0,10).

| Klasa | Komplet | W dłoni / na głowie → ciało | Gdzie | Zbroja między kośćmi | Gdzie | W progu |
|---|---|---:|---|---:|---|---|
| wojownik | start | 0.08 | RightHand/Jelec koniec w LowerTorso/LowerTorso | 0.12 | LeftHand/Mankiet w LeftLowerArm/LeftLowerArm | tak |
| wojownik | las | 0.05 | RightHand/Jelec w LowerTorso/Pas | 0.15 | Head/Head w UpperTorso/Futro kolnierza | tak |
| wojownik | bagno | 0.00 | RightHand/Jelec w LowerTorso/Pas | 0.12 | LeftHand/Mankiet w LeftLowerArm/LeftLowerArm | tak |
| wojownik | dzungla | 0.00 | — | 0.12 | LeftHand/Mankiet w LeftLowerArm/LeftLowerArm | tak |
| zwiadowca | start | 0.00 | — | 0.25 | UpperTorso/Kaptur kolnierz w Head/Twarz | tak |
| zwiadowca | las | 0.00 | — | 0.25 | UpperTorso/Kaptur kolnierz w Head/Twarz | tak |
| zwiadowca | bagno | 0.00 | — | 0.25 | UpperTorso/Kaptur kolnierz w Head/Twarz | tak |
| zwiadowca | dzungla | 0.00 | — | 0.25 | UpperTorso/Kaptur kolnierz w Head/Twarz | tak |
| mag | start | 0.23 | StaffPivot/Owijka w LowerTorso/Szata dzwon | 0.40 | LeftUpperLeg/Udo w LowerTorso/Szata dzwon | tak |
| mag | las | 0.23 | StaffPivot/Owijka w LowerTorso/Szata dzwon | 0.40 | LeftUpperLeg/Udo w LowerTorso/Szata dzwon | tak |
| mag | bagno | 0.23 | StaffPivot/Owijka w LowerTorso/Szata dzwon | 0.40 | LeftUpperLeg/Udo w LowerTorso/Szata dzwon | tak |
| mag | dzungla | 0.23 | StaffPivot/Owijka w LowerTorso/Szata dzwon | 0.40 | LeftUpperLeg/Udo w LowerTorso/Szata dzwon | tak |

Pomiar wyłapał i pozwolił poprawić trzy rzeczy: jelec miecza-liścia wchodził w nowy pas (zwężony jelec, cieńszy pas),
futrzany mankiet i bransoleta wchodziły w przedramię (obniżone), a głowice kosturów lasu i Dżungli wchodziły w bok głowy
kota (zakręt odwrócony od głowy, dysk berła podniesiony nad głowę). Klipy walki mierzy osobny pomiar (rozdział „Przenikanie broni w klipach walki”). **Nie sprawdzono** niczego w Studio.

## Umowa dla sklepu (okna robi druga osoba)
Jedno źródło: `swiat/postacie/sklep_przedmioty.json`, lista `przedmioty`. Okno sklepu potrzebuje tylko tych pól:

| Pole | Znaczenie |
|---|---|
| `id` | identyfikator (ten sam w przymierzalni, u kowala i w sklepie), np. `rycerz_las_helm` |
| `nazwa`, `opis` | nazwa dla gracza i krótki opis wyglądu |
| `klasa` | `wojownik` / `zwiadowca` / `mag` — tylko ta klasa kupuje i zakłada |
| `stopien`, `nr_stopnia` | `start` / `las` / `bagno` / `dzungla`, 0–3 (zakładki albo sortowanie) |
| `slot` | `Helmet`, `Chest`, `Gloves`, `Boots`, `Belt`, `Weapon`, `OffHand` |
| `cena` | Złoto; 0 = gracz ma od startu |
| `poziom` | wymagany poziom postaci |
| `baza`, `krok` | statystyki przy +0 i przyrost za ulepszenie (klucze: `bron`, `pancerz`, `tarcza` jako ułamek bloku, `Strength`, `Constitution`, `Intelligence`, `Dexterity`, `Luck`) |
| `sprzedawany` | `false` = część zbroi (nogawice, spodnie): bez osobnej pozycji, gracz dostaje ją z przedmiotem z `czesc_od` |
| `ikona` | plik ikony (PNG z Blendera; do gry trzeba ją wgrać — po zgodzie) |

Zasady po stronie serwera (propozycja, do zrobienia w następnej części — okno tylko wysyła `kup <id>`):
1. Odmowa, gdy: nieznane `id`, `sprzedawany = false`, inna klasa niż klasa gracza, poziom gracza < `poziom`, gracz już
   ma przedmiot, za mało Złota.
2. Zapłata jednym wywołaniem `StanGracza/WydajZloto` (cel `zakup_przedmiotu`, już dopuszczony), nigdy poniżej zera.
3. Po zakupie przedmiot trafia do posiadanych w pakiecie „kowal” (`przedmioty[id] = { poziom = 0, zapas = 0 }`) razem
   ze swoją częścią (`czesc_od`) i zakłada się w swoim slocie przez przymierzalnię (`StrojeProba/Zdalne/ZmienStroj`)
   — tak jak dziś nowy przedmiot z łupu.
4. Wpływ na walkę liczy kowal z `baza` i `krok` założonych przedmiotów (bez zmian w silniku walki).

**Wykonanie (część B):** serwer i okno są w `swiat/sklep_proba/` (opis: jego `README.md`). Różnice względem zasad
wyżej: płaci serwer kowala (źródło wydatku `KowalProba` — lista źródeł w stanie gracza nie ma `SklepProba`), a część
zbroi nie ma własnego wpisu w posiadanych (idzie za swoją zbroją, jak dziś przy zbroi startowej).

Pozostałe pola wpisu (`kategoria`, `cialo`, `klasy`, `czesc_od`, `ukrywa`, `zestaw`, `czesci`, `podstawowy`, `waga`) są
dla przymierzalni i kowala — te same nazwy i znaczenie co we wpisach bohaterów w `przedmioty.json` i w ustawieniach
kowala.

## Pliki
| Plik | Co to |
|---|---|
| `stopnie.py` | geometria 60 nowych przedmiotów, palety krain, nazwy i opisy; `przedmioty(klasa, stopien)`, `komplet()`, `postac()` |
| `stopnie_wojownik.py`, `stopnie_zwiadowca.py`, `stopnie_mag.py` | opakowania dla `przebuduj.py` (cztery komplety na bohaterze + ikony) |
| `sklep_ceny.py` → `sklep_liczby.json` | kalkulator cen, poziomów i statystyk z danych gry (silnik walki, pakiety krain, stan gracza, kowal) |
| `sklep_katalog.py` → `sklep_przedmioty.json` | katalog końcowy (modele + liczby); `--sprawdz`, `--md` |
| `przenikanie_stopni.py` | pomiar przenikania broni w klipach walki dla kompletów stopni (`--md`) |
| `test_stopnie.py` | testy: bohaterowie bez zmian, zakładanie, przenikanie w spoczynku, spójność katalogu |
| `wynik/stopnie_<klasa>/` | plansza czterech stopni, arkusz ikon, ikony, raport; lokalnie także GLB / FBX / .blend kompletów i GLB każdego przedmiotu (`przedmioty/<id>.glb`) |

```
python -B swiat/postacie/stopnie.py                              # lista nowych przedmiotów
python -B swiat/postacie/sklep_ceny.py                           # liczy od nowa sklep_liczby.json (20–30 s)
python -B swiat/postacie/sklep_ceny.py --spojnosc                # sama spójność zapisanych liczb
python -B swiat/postacie/sklep_katalog.py                        # sklep_przedmioty.json
python -B swiat/postacie/test_stopnie.py                         # 11 testów
python -B swiat/postacie/przebuduj.py stopnie_wojownik stopnie_zwiadowca stopnie_mag --bez-filmow   # Blender, ok. 1,5 min
```
Uwaga: `sklep_ceny.py --sprawdz` liczy z żywych plików krain — po zmianie liczby potworów albo odradzania (D-107)
zgłosi plik jako nieaktualny; wtedy trzeba policzyć od nowa i odświeżyć katalog.

## Przedmioty w grze i sklep — część B (bez Studio)

### Przymierzalnia (`swiat/stroje_proba/`) — strój na postaci w świecie i w walce
- Dane mają **80 przedmiotów** (20 dzisiejszych + 60 stopni z `stopnie.py`, wpisy z `sklep_przedmioty.json`). Jeden
  moduł przekroczyłby granicę długości źródła, więc dane są w czterech: `DaneStrojow.luau` (dzisiejsze przedmioty,
  klasy, scalenie) i `DaneStrojowLas` / `Bagno` / `Dzungla.luau` (po 20 przedmiotów); `Ubieranie`, serwer i klient dalej
  dostają jedno `D`. Dzisiejsze bryły i strój odniesienia bez zmian (kontrola z szablonem walki przechodzi).
- Lista dzisiejszych przedmiotów klasy (`przedmioty`) zostaje przy 8 / 8 / 4; nowe są w polu `stopnie`, a gotowe
  zestawy `las`, `bagno`, `dzungla` — obok dzisiejszych. Brak modułu stopnia nie jest błędem (stopień znika z list).
- Testy: 29 (było 22) — każdy nowy przedmiot w danych, komplety stopni przez logikę i lustro Luau, obca klasa
  odrzucona, część zbroi idzie za zbroją, stroje mieszane między stopniami.

### Kowal (`swiat/kowal_proba/`) — statystyki i kupno
- `dane.py` kowala bierze 18 dzisiejszych wpisów z ustawień (bez zmian) i **54 nowe wprost z katalogu**; wszystkie 72
  mają też `cena`, `poziom`, `stopien`. Założony nowy przedmiot liczy się w walce tym samym torem co dzisiejsze
  (`Modyfikatory`, źródło „kowal”) i da się go ulepszać.
- **Łup z walk losuje dalej tylko ze stopnia startowego**; gracz, który nic nie kupił, ma wszystko jak dziś (logika
  sprzed zmiany i po niej dała te same wyniki w 4000 losowych stanach).
- Nowe w logice (Luau + lustro w Pythonie, 355 przypadków wzorcowych): `kup`, `oferta`, `stacNa`, reguła zakładania.
  Nowe wejście serwera `KowalProba/Sygnaly/Sklep`: `oferta`, `kup`, `zaloz`; atrybut gracza `SklepStacNa`.

### Sklep zbrojmistrza (`swiat/sklep_proba/`, kontener `Workspace/SklepProba`)
Pełny opis: `swiat/sklep_proba/README.md`. W skrócie:
1. Okno otwiera istniejące E bazaru przy zbrojmistrzu (klient sklepu słucha zdarzenia okien bazaru dla miejsca
   `zbrojownia`; bazar i NPC bez zmian). Klient wysyła tylko akcję i id.
2. Serwer sklepu sprawdza limit zapytań i odległość od stoiska i woła wejście kowala.
3. Kowal sprawdza logiką `kup`, płaci przez `WydajZloto` (cel `zakup_przedmiotu`), zapisuje posiadanie, zakłada według
   reguły i przelicza wpływ na walkę.

- **Reguła zakładania:** kupiony przedmiot zakłada się sam, gdy slot jest pusty albo założony ma niższy stopień; przy
  tym samym lub wyższym zostaje dotychczasowy, a kupiony zakłada się przyciskiem „Załóż” albo w przymierzalni.
- **Odmowy:** nieznany przedmiot, część zbroi, inna klasa, już posiadany, za niski poziom („Potrzebujesz poziomu 13.”),
  za mało Złota („Brakuje ci 150 Złota.”), za daleko, za szybko, sklep nieczynny (brak kowala albo stanu gracza).
- **Okno tymczasowe:** zakładki czterech stopni, przewijana lista slotów; nazwa, statystyki, poziom, cena, stan
  (kup / za drogie / za niski poziom / masz / założone), „Kup” albo „Załóż”; kolorowe pole stopnia zamiast ikony.
  Na ekranie 667 × 375: okno 480 × 352 px, wiersz 48 px, przycisk 44 px, tekst 14 pt (policzone testem, nie widziane).
- **Wskazówka „stać cię na nowy przedmiot”:** serwer pisze atrybut `SklepStacNa`; pakietu wskazówek nie zmieniano —
  README sklepu opisuje, co trzeba w nim dopisać (dwa teksty, cel, warunek kroku i wyciszenie po otwarciu okna).

### Liczba brył i uproszczenia modeli
Bohater w świecie ma limit 220 brył (`swiat/bohater_swiat`). Pierwsza wersja kompletów Bagna i Dżungli go przekraczała
(pióro = 10 części Roblox, kolec = 4), więc pióra, zęby, kły i płetwy grzebieni są teraz **płaskimi trójkątami
z dwóch klinów**; trójwymiarowe zostały kolce naramienników, rogi i guzy. Plansze i ikony są przebudowane.

| Części Roblox w komplecie | Start | Las | Bagno | Dżungla |
|---|---:|---:|---:|---:|
| Wojownik | 127 | 144 | 213 (było 259) | 181 (było 321) |
| Zwiadowca | 182 | 187 | 216 (było 250) | 210 (było 333) |
| Mag | 166 | 173 | 182 | 171 (było 299) |

### Przenikanie broni w klipach walki
`python -B swiat/postacie/przenikanie_stopni.py --md` (narzędzie `przenikanie/` na bohaterze w komplecie stopnia; broń,
tarcza, łuk i kostur kontra głowa z nakryciem i tułów; progi: głowa 0,02, tułów 0,10 studa; komplety startowe nie mają
miejsc ponad próg). Pierwszy pomiar (połowa gęstości próbek) znalazł: sztylet Dżungli — pióra głowicy w tułowiu 0,30
(klip umiejętności); łuk Dżungli — pióro końca w tułowiu 0,26 (upadek); kostur bagienny — róg w rogu czepca 0,13
(atak) i rogi w uchu kota 0,04–0,06 już w spoczynku; berło Dżungli — promienie w uchu 0,03–0,05; łuk bagienny — róg
końca w tułowiu 0,10. Poprawione w `stopnie.py`: sztylet bez piór przy głowicy, krótsze ozdoby końców łuków, krótsze
i bardziej pionowe rogi kostura, promienie berła tylko u góry. Pomiar po poprawkach:

| klasa | stopień | scenariusz (klip) | strefa | głębokość | start | gorzej o | co w co | chwila [s] | ocena |
|---|---|---|---|---|---|---|---|---|---|
| mag | bagno | unik | nakrycie | 0,030 | 0,000 | +0,030 | kostur: Rog 3 → HatPivot/Rog | 0,100 | PONAD PRÓG |
| wojownik | bagno | atak_miecz | glowa | 0,026 | 0,000 | +0,026 | miecz: Zab → Head/Helm bok P | 0,158 | PONAD PRÓG |
| wojownik | bagno | atak_miecz | nakrycie | 0,026 | 0,000 | +0,026 | miecz: Zab → Head/Helm bok P | 0,158 | PONAD PRÓG |
| zwiadowca | las | upadek (+1 innych) | tulow | 0,076 | 0,000 | +0,076 | łuk: Listek konca → UpperTorso/Futro barkow | 1,000 | gorzej |
| zwiadowca | dzungla | upadek (+1 innych) | tulow | 0,067 | 0,000 | +0,067 | łuk: Pioro konca → UpperTorso/Kirys | 0,900 | gorzej |
| wojownik | dzungla | unik (+1 innych) | tulow | 0,057 | 0,000 | +0,057 | miecz: Pioro glowicy → LowerTorso/LowerTorso | 0,333 | gorzej |
| wojownik | dzungla | trafienie | tulow | 0,052 | 0,000 | +0,052 | miecz: Pioro glowicy → UpperTorso/UpperTorso | 0,292 | gorzej |
| zwiadowca | dzungla | umiejetnosc | tulow | 0,049 | 0,000 | +0,049 | sztylet: Glowica → UpperTorso/Kirys | 0,192 | gorzej |
| zwiadowca | bagno | umiejetnosc | tulow | 0,042 | 0,000 | +0,042 | sztylet: Glowica → UpperTorso/Kirys | 0,175 | gorzej |
| zwiadowca | bagno | upadek (+1 innych) | tulow | 0,033 | 0,000 | +0,033 | łuk: Rog konca → UpperTorso/Kirys | 0,900 | gorzej |

Po poprawkach ponad progiem zostały dwa drobne miejsca (róg kostura bagiennego w rogu czepca 0,03 w uniku; ząb tasaka w boku hełmu 0,03 w ataku), reszta jest pod progiem (najwięcej 0,08 studa w tułowiu). Pomiar z połową gęstości próbek; „start” = komplet startowy.

Nie zmierzono: broni w rękach i nogach, ozdób zbroi wchodzących w ciało bez udziału broni (poroże, pióropusze, skrzydła
naramienników przy rękach uniesionych nad głowę), zasłaniania twarzy z kamery. Test przymierzalni mierzy za to
schodzenie pod ziemię względem stroju odniesienia i ma na to granice z zapasem — do obniżenia po próbie w Studio.

### Ceny po zmianach walki bez przestojów (D-107)
`sklep_ceny.py` przeliczony 19.11 po porannych zmianach plików krain: **żadna cena, poziom ani statystyka się nie
przesunęły** względem zapisanego katalogu. Jedyne przesunięcie tego dnia zaszło jeszcze przed zapisaniem katalogu
(Złoto lasu do Strażnika 3 262 → 3 413) i jest już w cenach. Więcej potworów i szybsze odradzanie zmienia Złoto na
minutę, a nie Złoto na walkę, od którego liczą się ceny.

## Plan części ze Studio (polecenia w kolejności)
Praca zgłoszona z obszarami `studio:StrojeProba`, `studio:KowalProba`, `studio:SklepProba`; Studio w trybie Edit.
1. `python -B swiat/stroje_proba/zbuduj.py --skrypty` — cztery moduły danych i logika przymierzalni (bez tego kupiony
   przedmiot nie pokaże się na postaci).
2. `python -B swiat/kowal_proba/zbuduj.py` — **pełna** budowa (nie `--skrypty`): tylko ona tworzy `Sygnaly/Sklep`.
3. `python -B swiat/sklep_proba/zbuduj.py` — kontener sklepu.
4. `python -B tools/studio_okno.py --na-wierzch`, potem próby: `python -B swiat/kowal_proba/testy/proba_play.py`
   (dzisiejsze zachowanie kowala), `python -B swiat/stroje_proba/testy/proba_play.py` (przymierzalnia; do rozszerzenia
   o komplety stopni), `python -B swiat/sklep_proba/testy/proba_play.py` (prawdziwe E przy zbrojmistrzu, kupno
   kliknięciem, strój po kupnie, wpis kowala i opis bohatera, odmowy, mały ekran, konsola, zrzuty trzech klas w trzech
   stopniach).
5. Walka w kupionym komplecie w lesie i w próbie walki (oglądana, ze zrzutami), potem regresja całości.
6. Zrzuty do raportu w panelu, zakończenie pracy. Wyłącznik: `zbuduj.py --usun` sklepu; kowal i przymierzalnia bez
   kupionych przedmiotów działają jak przed zmianą.

## Wybory do oceny przez ludzi
1. **Wygląd stopni** — trzy plansze wyżej: czy kierunek (materiały krain, poroże / kość / pióra) się podoba i co
   zmienić.
2. **Nazwy przedmiotów** — propozycje; każdą można podmienić w `stopnie.py` (`OPISY`).
3. **Ceny:** komplet = 40% Złota, które kraina daje do Strażnika (reszta na jajka i kowala). Drożej czy taniej?
4. **Wymagane poziomy:** od najniższego poziomu potworów krainy, sloty co poziom (pas najwcześniej, broń najpóźniej).
5. **Siła przedmiotów:** przepis slotu × 1 / 2 / 3; komplet podnosi szansę z potworami krainy z ok. 60% do ok. 80%.
6. **Ulepszenia a nowy stopień:** nowy przedmiot przy +0 jest słabszy niż poprzedni ulepszony do +2 — czy poziom
   ulepszenia ma przechodzić na nowy przedmiot, czy gracz ulepsza od zera?
7. **Przedmioty startowe za Złoto** (razem 300 w klasie) — dziś wypadają tylko z łupu; czy sklep ma je sprzedawać?
8. **Mag ma cztery sloty** — droższe sztuki (waga 1,75); czy dorobić kotu rękawice i buty, żeby miał tyle co inni?
9. **Łuk i kaptur Zwiadowcy** mają w stopniach inne statystyki niż u kowala (wyrównanie klas) — zostawić?
10. **Sloty** — bez zmian względem dziś; spodnie dalej jako część zbroi (pytanie z `EKWIPUNEK.md` pkt 8 zostaje otwarte).
11. **Rozmiar:** głowa Wojownika z pióropuszem ma 2,8 studa (limit części awatara 2,0 dotyczy tylko rigu z wgrywanych
    siatek; rig z części, którym gra dziś ubiera bohatera, tego limitu nie ma); berło Dżungli jest o 0,7 studa
    dłuższe od dzisiejszego kostura.
12. **Reguła zakładania po kupnie:** sam zakłada się tylko przedmiot wyższego stopnia niż założony (albo do pustego
    slotu). Czy tak, czy zawsze zakładać kupiony?
13. **Łup z walk:** dalej tylko przedmioty startowe; czy potwory krain mają dawać także przedmioty swojego stopnia?
14. **Uproszczone pióra i kolce** (płaskie trójkąty) przez limit 220 brył bohatera w świecie — zostawić, czy podnieść
    limit i wrócić do pełniejszych kształtów?
15. **Okno kowala** pokazuje najwyżej 8 wierszy — przy wielu kupionych przedmiotach potrzebuje przewijania albo
    zakładek (do zrobienia razem z docelowym oknem).
16. **Płatność przez kowala** (źródło wydatku `KowalProba`) — zostawić, czy dopisać `SklepProba` do źródeł w stanie gracza?
17. **Wskazówka „stać cię na nowy przedmiot”** — czy dopisać krok w pakiecie wskazówek według opisu z README sklepu?
