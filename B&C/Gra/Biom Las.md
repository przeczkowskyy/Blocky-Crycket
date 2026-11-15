---
status: propozycja
tags: [gra, swiat, biom, las, mapa]
źródło: "prośba Karola z 15.11.2026 („te biomy muszą być dosyć duże i zawierać konkretne lokalizacje i podbiomy, i będą po nich chodziły potwory”); synteza trzech koncepcji (eksploracja, pętla gry, obraz i budowa); decyzje D-032, D-034, D-035, D-041, D-042, D-059, D-060, D-061, D-064, D-068"
---
# Biom Las — „Bór Pod Ukłonem”

> [!info] W skrócie
> Pierwszy biom gry (D-061): las 1000 × 1000 studów (gra w 860 × 860, ok. 3,4 raza szerzej niż miasteczko), sześć podbiomów, 24 lokacje, 16 stref potworów i 4 patrole wędrowne. Pośrodku rośnie **Stary Ukłon** — drzewo wysokie na ok. 100, które kłania się jak domy w miasteczku i widać je z całego lasu. Na południu jest nisko, jasno i łatwo (poziomy 1–3), na północy wysoko i trudno (8–10), a na szczycie czeka **Strażnik Gaju**. Od bramy do Ukłonu biegnie się 26 s, do strażnika 66 s; sześć pinów teleportu skraca powroty. **Wersja 2 (15.11):** projekt poprawiony po krytyce i **zbudowany z klocków** (22 419 części), obejrzany w podglądach z Blendera i **zbudowany w Roblox Studio** (kontener `Workspace/BiomLas`). Po uwadze Karola z 15.11 („mapa logistycznie bardzo dobra, ale popracowałbym nad lepszymi teksturami i detalami”) mapa dostała faktury z wbudowanych materiałów Roblox (grunt, ścieżki, skały, drewno; liście, grzyby, woda i kody zostały gładkie, żeby został komiksowy charakter) — układ, lokacje, ścieżki i strefy potworów bez zmian. Doszły też detale tam, gdzie chodzi gracz: drobiazgi przy ścieżkach, runo, kłody, warstwy na ścianach skalnych, zwisy liści na labiryncie, rekwizyty przy lokacjach, płycizna i plamy głębi na jeziorze. To **propozycja** — nic tu nie jest kanonem.

Kontrakt dla budowniczych (liczby, paleta, budżet, ujęcia, odpowiedzi na krytykę): `swiat/biom_las/PROJEKT.md`; jak generować i oglądać: `swiat/biom_las/README.md`. Plan z góry: `swiat/biom_las/podglad/plan.png` (na telefon: `plan_telefon.png`), rendery: `swiat/biom_las/podglad/01…12_*.jpg`. Dane maszynowe: `uklad.json`, `potwory.json`, `ujecia.json`; wynik generatora: `czesci.json` i `znaczniki.json` (strefy, węzły walki, domy, patrole, punkty E — dla kroku „potwory w Studio”).

## Idea
Las to [[Kierunek artystyczny|Krzywe Miasteczko]] przeniesione na przyrodę: pnie z przechylonych segmentów, korony jak czapy, kanciaste skały z czapą mchu, gruby „tusz” (D-041). Krainę da się odczytać z samego widoku — im wyżej i dalej na północ, tym groźniej. **Kręta Struga** płynie z wodospadu na północnym zachodzie do stawu przy wejściu, więc woda zawsze pokazuje drogę do wyjścia. Każdy potwór ma **dom**, z którego wychodzi: slime ze stawu, muchomornik z chatki, wilki z jeżyn, troll spod własnej tamy. Lokacje rozpoznaje się po wielkim rekwizycie i kolorze, bez napisów.

## Podbiomy
| Podbiom | Poziomy | Potwory | Charakter |
|---|---|---|---|
| Łąka Galaretek (pd.) | 1–3 | [[Leśny Slime]] (4 strefy, karawana) | wejście z miasteczka, pierwsze walki, jasno i otwarto |
| Kapeluszowo (pd.-zach.) | 3–5 | [[Muchomornik]], slime | wioska olbrzymich grzybów, świecące zarodniki |
| Serce Boru (środek) | spokój | — | polana pod Ukłonem: inkubatory, walki petów, loch, odrodzenie |
| Cierniste Ostępy (zach.) | 5–7 | [[Cierniowy Wilk]] | ciemny bór, jeżyny, Wilcza Skała, labirynt, wodospad |
| Suchy Wąwóz (wsch.) | 6–9 | wilk, Bursztynowy Slime, [[Leśny Troll]] | dwie rynny między półkami (y 12), tama i jezioro trolla |
| Korona Gaju (pn.) | 8–10 | muchomornik, wilk, [[Strażnik Gaju]] | trzy poziomy (12, 22, 32) z rampami, białe brzózki, Kamienny Krąg |

## Najważniejsze lokacje
- **Stary Ukłon** (środek) — dominanta, strefa spokoju, odrodzenie, pin; w czubku sekretne Bocianie Gniazdo.
- **Brama Pniaków** — wejście z miasteczka i Kamień Powrotu; **Oczko Galaretek** 5 s dalej — pierwsza walka.
- **Gniazdo w Korzeniach** (inkubatory, [[Pety]]), **Dziupla Turniejowa** (walki petów), **Korzenna Gardziel** (loch z kłódką 5. poziomu).
- **Wielki Kapelusz** (wioska muchomorników), **Wilcza Skała**, **Jeżynowy Labirynt** ze skrzynią, **Szumiący Próg** z tunelem na sekretną Grań.
- **Trollowa Tama** z legowiskiem i Skarbczykiem, **Kamienny Krąg Korony** (strażnik), **Ławka z Widokiem** (widać miasteczko na horyzoncie), **Wrota Bagna** (zapowiedź drugiego biomu).
Pełna lista 24 lokacji z pomysłem, funkcją i współrzędnymi: rozdz. 4 kontraktu.

## Potwory
- Walkę zawsze zaczyna gracz: podchodzi, E, walka z animacją (D-034, D-068). Potwór nigdy nie atakuje sam; w walce jest „zajęty”.
- 16 stref: naraz ok. **64 zwykłych** przy 8 graczach (do 86 przy tłoku) i **4 patrole wędrowne** po ścieżkach (wataha w Ostępach, karawana slime’ów, muchomorniki z koszami, wataha z półki w Wąwozie, która zeskakuje graczowi na drogę).
- Każda strefa ma 2–3 domy 35–50 studów od miejsc walki; nowy potwór wychodzi z domu, gdy żaden gracz nie stoi bliżej niż 18 — gracz walczący w strefie nie blokuje już odradzania. Miejsca walki są płaskie i wolne od drzew i rekwizytów (sprawdzone na zbudowanej mapie).
- Pod strefami jest grunt, na którym potwora dobrze widać (ciemniejsza trawa, polanki mchu, ciemne błoto). W Wąwozie propozycja **Bursztynowego Slime’a** (ten sam model, inny kolor), żeby slime 6.–7. poziomu nie wyglądał jak ten z łąki.
- **Leśny Troll** budzi się co 8–12 min i idzie z legowiska pod tamą do stawu na łące, żeby się napić; walczyć z nim można tylko w wąwozie.
- **Strażnik Gaju**: kryształ świeci po ok. 10 wygranych z potworami nie słabszymi niż (poziom gracza − 2); propozycja: walka w osobnej przestrzeni. Statystyki: [[Walka v2 — silnik, klasy i umiejętności]].

## Co to zmienia albo doprecyzowuje względem D-061
- D-061 (💡 propozycja) mówi tylko, że każdy biom ma własnych przeciwników, strażnika i inkubatory. Ta notatka dodaje do tego **układ lasu**: rozmiar, podbiomy, lokacje, strefy potworów, poziomy 1–10 i miejsce strażnika na 10. poziomie.
- Doprecyzowuje D-034 dla lasu: gęstość, odradzanie, zachowanie potworów; w lesie **nie ma tablicy zadań** (jedna karczma) — są cztery miejsca, do których zadania z karczmy wysyłają gracza.
- D-064: sześć pinów lasu (dwa od początku, cztery po pierwszej wizycie). D-042: kłódki lochu i Wrót Bagna działają osobno dla gracza.
- Technika: las to osobny kontener w Studio, ok. 480 studów za miasteczkiem, **obrócony o 180°**, żeby słońce świeciło graczowi zza pleców (szczegóły w kontrakcie, rozdz. 2). Zbudowane: 22 419 części z 25 000 (rezerwa ok. 2,6 tys. na poprawki po pomiarze na telefonie).

## Do decyzji ludzi
1. **Strażnik Gaju:** osobny dla każdego gracza po ok. 10 wygranych (propozycja) czy wspólne „Przebudzenie Gaju” dla całego serwera?
2. **Jajka lasu:** inkubatory w lesie (Gniazdo w Korzeniach) czy w wylęgarni w mieście? D-060 mówi o obu.
3. **Loch lasu:** dodatkowe wejście w lesie (Korzenna Gardziel) czy tylko z hali portali w mieście (D-042)?
4. **Droga z miasta:** krótkie przejście z zaciemnieniem z Bramy Miejskiej (propozycja) czy prawdziwa droga przez pusty teren?
5. **Wrota Bagna:** tylko zapowiedź (do bagna teleportem po odblokowaniu, D-064) czy prawdziwe przejście — czyli czy biomy sąsiadują ze sobą?
6. **Nowe warianty i zachowania potworów:** Bursztynowy Slime w Wąwozie, karawana slime’ów, muchomorniki z koszami, wataha zeskakująca z półki — to dodatkowe kolory i animacje do zamówienia.
7. **Lekka mgła** w lesie (oświetlenie jest wspólne dla całego miejsca).

## Powiązane
[[Rejestr decyzji]] · [[Pytania otwarte]] · [[Koncepcja i Core Loop]] · [[Karczma (Questy)]] · [[Pety]] · [[Mapa teleportacji]] · [[Klocki — Blender i Roblox]] · [[Sesja główna 2026-11-14 (3) — zapis ustaleń]]
