---
status: propozycja
tags: [gra, systemy, mvp, ekonomia, live-ops, v2]
---
# Systemy gry v2

> [!info] W skrócie
> Gracz ma jeden duży przycisk BONK: uderzony potwór leci w stado jak kula w kręgle, banda dobija ogłuszonych, a kot składa pokonanych krzywo w nowych kumpli. Szybsze tempo daje tylko lepsza gra, a pieniądze przyspieszają wyłącznie złoto. Budujemy w dwóch etapach: Etap A (ok. 128 h) to rdzeń i pierwsze 10 minut, Etap B (ok. 66 h) to wszystko, czego potrzebuje uczciwy pomiar. Grudzień to miękka premiera tylko do sprawdzenia pierwszych minut, a decyzje „rozwijać / zmienić / zakończyć” zapadają na kohortach od stycznia. Cztery tygodnie na Etap A są realne tylko przy ok. 20 h pracy na osobę tygodniowo.

Szczegóły dla agentów i liczby robocze: [[Specyfikacja v2.1 — Krzywa Banda]]. Myśl przewodnia: [[Myśl przewodnia v2]]. Schemat: [[Gra/Pętla gry v2.canvas]].

## Pętla rdzenia

**Czynność.** Gracz chodzi swoim awatarem po wspólnej strefie, a za nim idą Crycket i do trzech kumpli, którzy biją sami. Gracz ma jeden duży przycisk **BONK**. Trafiony potwór leci łukiem w stronę, w którą gracz patrzy, przewraca innych („KOMBO ×3”) i ogłusza ich na chwilę, a banda bije ogłuszonych mocniej.

**Decyzja co 2–5 sekund:** w kogo i w którą stronę uderzyć; czekać, aż stado się zbije, czy zdejmować pojedynczo; kiedy odpalić Finał; jak ominąć Tarczaka z tarczą z przodu. Kto nie chce celować, ma autocel, który zawsze pokazuje krążek pod celem i nigdy nie wybiera celu, którego nie da się trafić.

**Hałas wabi.** Dobre kombo i duży Finał ściągają kolejne stado. Tempo rośnie z ok. 18 do ok. 30 nokautów na minutę wyłącznie dzięki grze. To naprawia największy zarzut sceptyków: wcześniej po godzinie gracz głównie czekał na kolejnego potwora.

**Finał Crycketa: Wielkie Sklejenie.** Pasek Kleju rośnie z nokautów. Pełny po 5 s zaczyna powoli opadać, więc czekanie na większe stado kosztuje. Finał skleja potwory w chwiejną wieżę, a drugi BONK decyduje, w którą stronę wieża runie.

**PODANIE.** Wybity potwór może polecieć w cudze stado albo w echo cudzej bandy. Obaj gracze dostają klocek i dymek „PODANIE!”.

**Krzywy montaż.** Klocki z pokonanych lecą do torby Crycketa. Gdy strona gatunku się zapełni, kot z kamienną miną składa potwora źle, a błąd daje moc. Kolejne stopnie pogłębiają błąd:

| Stopień | Próg | Przykład: Tarczak |
|---|---|---|
| Krzywy | 10 nokautów | tarcza z tyłu, osłania ci plecy |
| Bardziej Krzywy | 60 | dwie tarcze plecami do siebie, blok z obu stron |
| Arcydzieło Krzywizny | 300 | tarcza-kapelusz, która się kręci i odbija wokoło |

**Sok** ma własne godziny w planie: stop-klatka przy trafieniu, dymki BONK!/KLONK!/PUF!, dźwięk coraz wyższy z kombo, rozpad na klocki, zbliżenie na minę kota w rogu ekranu, lądowania z gagiem. Sceptycy policzyli, że ok. 80% soku da się zrobić z klocków. Nie da się tanio zrobić rozciągania brył ani tuszu na modelach 3D, więc tusz zostaje w interfejsie, dymkach i miniaturach.

## Pierwsza minuta

Bez tekstu i bez okien. Pierwsza minuta dzieje się tylko u gracza, więc nikt inny jej nie zepsuje.

| Kiedy | Co się dzieje |
|---|---|
| 0:00 | ładowanie znika od razu (dziś wymusza co najmniej 5,8 s); obok stoi Blocky, przycisk pulsuje |
| do 0:10 | BONK: Blocky ląduje głową w Kotle i pokazuje kciuk w górę |
| ok. 0:15 | Słojak (słój z ogórkami na nóżkach) kradnie chochlę, wbiega Burek, KOMBO ×3 |
| ok. 0:20 | Słojaki pękają na klocki, pojawia się Crycket, licznik przeskakuje z 7 na 10 |
| do 0:30 | zbliżenie: kot z kamienną miną przykręca wieko do góry nogami, „PUF!”, Słojak dołącza i łapie wiekiem monety |
| 0:30–1:00 | większe stado, nowy licznik „Bardziej Krzywy”, smuga do Krzywego Lasu |

## Pierwsze 10 minut

Pięć pojęć, jedno co ok. 2 minuty:
1. **BONK** (do 0:10).
2. **Banda i krzywy montaż** (do 0:30); w lesie drugi kumpel, Pniak z korzeniami na górze, który wiruje.
3. **Finał** (ok. 2:00): ten sam przycisk zaczyna świecić.
4. **Album** (ok. 3:00): zakładka tylko pulsuje, nie otwiera się sama.
5. **Żarłok** (ok. 7–10 min): wyskakuje z Kotła i biegnie do gracza, bez marszu na plac. Nagroda: Patelnia, czyli BONK w linii. Blocky łapie Żarłoka chochlą.

Tarczak przychodzi dopiero po pierwszym Finale. Uderzenie w tarczę to jedno KLONK i od razu strzałka „z boku”, bez sekund bezradności.

## Systemy i kolejność odblokowań

| System | Gracz widzi go | Etap budowy |
|---|---|---|
| BONK, kombo, banda, krzywy montaż, Finał, Album | pierwsze 3 minuty | A |
| Żarłok z Kotła, Patelnia, „Moc bandy” (jedna duża liczba) | pierwsze 10 minut | A |
| Zaproszenie znajomego, premia za przybyłych razem, serwery prywatne | zawsze | A |
| Pasek „Na jutro” po bossie i po 40 minutach | koniec sesji | A |
| Echo bandy, Kocioł świata | od pierwszego lasu | B |
| Spiżarnia Bez Dna: zamówienie u Chochli, instancja z piętrami bez końca, rekord i top 100 | po pierwszym Żarłoku | B |
| Strefa 2 i Sława ★ (★1 boss, ★2 wszystkie Bardziej Krzywe otwierają strefę 2) | ok. 20–25 min gry | B |
| Warianty za wyczyn (np. Złoty Słojak za KOMBO ×6), Żarłok na Trudnym | gdy gracz opanuje strefę | B |
| Sklep (2× Złoto, Zupa, Kostium) | po pierwszym Żarłoku | B |
| Pracownia (wygląd stanowiska za złoto) | — | miesiąc 2 |
| Wyprawa (prestiż), Drużyna Karczmy, pojedynki, pełna działka z [[Twierdza (Tycoon)]], miasteczko | — | po bramce D7, jeden system na kwartał |

**Krzywe (symulacja, hipoteza).** Wersja do pomiaru ma 2 strefy po 4 gatunki.

| Kto | Strefa 2 otwarta | Cały Album na Arcydziełach | Co dalej |
|---|---|---|---|
| gra 15 min dziennie | dzień 2 | ok. 13. dnia | Spiżarnia, wyczyny, paczka co 3–4 tygodnie |
| gra 45 min dziennie | dzień 1 | ok. 5. dnia | tylko Spiżarnia i wyczyny |

Z jedną strefą (miękka premiera) Album kończy się w 2.–6. dniu. Dlatego pomiar retencji czeka na drugą strefę i Spiżarnię.

## Ekonomia

| Waluta | Skąd | Na co |
|---|---|---|
| **Złoto** | walka (więcej przy kombo), Zupa | poziomy kumpli do limitu stopnia; od miesiąca 2 wygląd Pracowni |
| **Magiczne Kryształy** | bossowie, wyczyny, progi Albumu | kosmetyka zdobywana w grze, kolor szaty kota |
| **Klocki gatunku** | tylko nokauty | strony Albumu; nigdy na sprzedaż |

Diamenty znikają, a waluty za Robuxy nie ma. Liczby rosną ×10 w każdej strefie, żeby było widowisko „cyferek”, ale limity poziomów zostają.

**Niezmiennik:** płatny mnożnik działa tylko na złoto, a złoto podnosi poziomy tylko do limitu stopnia. Płacący dochodzi do strefy 2 po ok. 21 min, niepłacący po ok. 23 min.

## Społeczność

Przy premierowym ruchu na serwerze będzie średnio 0,3–3 graczy naraz, więc wszystko musi działać także w pojedynkę.
- **Echo bandy:** migawka cudzej bandy stoi w strefie, gdy żywych graczy jest mniej niż 3. Ma wyraźną ikonę „echo”, nie ma nicku, nie pisze i nigdy nie udaje żywego gracza. Właściciel widzi przy następnym wejściu raport „Twoje echo podało 4 razy”.
- **Kocioł świata:** dzienny licznik nokautów ze wszystkich serwerów, widoczny na placu. Progi dają wspólne efekty na teraz (czapki-garnki, częstszy Żarłok), a nie przedmioty dnia do zebrania.
- **Plac bez pustych stoisk:** stoją tylko stanowiska obecnych graczy i stoisko Crycketa.
- **Razem:** zaproszenie w dwa stuknięcia i premia +20% klocków tylko dla przybyłych razem.
- **Bez czatu:** gotowe hasła i gesty.
- **Twórcy wideo:** dopiero po wejściu gry do kont 9–15 lat, bo wcześniej ich widzowie nie mogą zagrać.

## Monetyzacja

| Produkt | Cena | Co daje |
|---|---|---|
| 2× Złoto | 199 R$ | napis na przycisku: „×2 złota z walki. Nie przyspiesza klocków, Albumu ani Spiżarni.” |
| Zupa dla wszystkich | 49 R$ | cały serwer: Kocioł 2× szybciej i czapki-garnki na 15 min; kupujący +20% złota; anonimowo |
| Kostium kumpla | 99–199 R$ | wygląd, widoczny też na echach i w Albumie |
| Serwer prywatny | ok. 100 R$ miesięcznie | darmowy dla Roblox Plus |

**Nigdy:** los za Robuxy, waluta za Robuxy, sprzedaż kumpli i stron Albumu, skracanie liczników, oferty po porażce, „ostatnia szansa”, imię kupującego na serwerze. **Uczciwie:** sufit przychodu jest niski z wyboru, a pierwszy sensowny pomiar sprzedaży wymaga ok. 2000 nowych graczy.

## Live-ops

Nowa treść to wiersz w tabeli, a nie kod. Gatunek składa się z jednej zasady wroga i jednej zdolności kumpla z zamkniętej biblioteki (osłona, krąg, lot, szarża, dzielenie, odbicie; magnes, wir, leczenie, prowokacja), do tego model w trzech stopniach i trzy żarty. Boss to sekwencja 2–3 zasad. Próba generalna: nowy gatunek z samych danych w ≤ 2 h.

| Okres | Rytm | Godzin tygodniowo (obie osoby) |
|---|---|---|
| do 100 graczy dziennie | automatyczny „Gatunek tygodnia” z kalendarza, paczka 2 gatunków co 3–4 tygodnie, 2 klipy od agenta | ≤ 10 |
| po D7 ≥ 3% | wydarzenie weekendowe z „Notify me”, paczka co 2–3 tygodnie, jeden nowy system na kwartał | ≤ 15 |

Gdy pojawi się klon gry, w 48 h wychodzi wydarzenie z konfiguracji.

## MVP na 4 tygodnie z bramkami

**Etap A, ok. 128 h:** Karol ok. 74 h (zapis, walka, sok, strefa 1, Żarłok, pierwsza minuta, telefon, bot-klikacz), Game Director ok. 25 h (HUD, panel Bandy, Album, „Na jutro”, interfejs soku), wspólnie ok. 29 h (decyzje, szkice, testy). **Etap B, ok. 66 h:** echo, Kocioł świata, Spiżarnia, strefa 2, wyczyny, sklep, okno „Banda i Ekwipunek”, garnek zamówień.

| Godzin na osobę tygodniowo | Etap A | Kohorty decyzyjne |
|---|---|---|
| 20 | ok. 18.12 | od ok. 25.01 |
| 15 | ok. 11.01 (przerwa świąteczna) | od ok. 8.02 |
| 10 | ok. 1.02 | marzec |

Przy braku godzin przesuwa się data, a nie zakres pomiaru. Soku, pierwszej minuty, echa, Spiżarni i telefonu nie tniemy.

| Bramka | Kiedy | Warunek |
|---|---|---|
| Dzień 0 | 13.11 | start werbunku testerów 16+, zakup taniego telefonu z Androidem (3 GB RAM) |
| Makieta siatki | przed B1 | 12 kafelków z prawdziwą konkurencją, co najmniej 40 graczy 16+; nasza karta wybierana ≥ 1,5 raza częściej niż przypadek, ≥ 8/10 wie, „co się robi” |
| B0 | 16–18.11 | sześć decyzji dnia 0, scalone gałęzie, dziennik godzin |
| Pomiar techniczny | ok. 23.11 | ≥ 30 klatek/s przy 8 bandach na tanim telefonie; porażka = naprawić |
| B1 | 30.11 | szary prototyp, 6–8 obcych, każdy gra BONK i wariant z auto-biciem; porażka tylko przy wyraźnym wyniku: BONK krótszy od auto-bicia, mniej niż 3 z 8 gra ponad 5 min albo człowiek nie bije bota-klikacza nawet o 10% |
| B2 | ok. 2 tygodnie po B1 | kumpel do 0:30, Żarłok do 10:00 na telefonie, zapis i exploity sprawdzone, gatunek z danych ≤ 2 h, znaki towarowe tytułu sprawdzone |
| B3 | po B2, poza 20.12–3.01 | publiczna miękka premiera 16+; mierzymy tylko pierwsze minuty, bez decyzji „zakończyć” |
| Przerwa | 20.12–3.01 | bez nowych funkcji, dyżur poprawek |
| B4 | dwie kohorty po Etapie B, nie wcześniej niż 11.01 | ok. 400 nowych graczy tygodniowo w dwóch oknach reklamy po 2 h; kohorta ważna tylko przy co najmniej 3 graczach naraz |

**Po B4:** rozwijać przy D1 ≥ 10% i sesji ≥ 10 min; zmienić pętlę przy D1 7–10%; zakończyć dopiero przy D1 < 7% w dwóch ważnych kohortach. Pierwszy nowy system po D7 ≥ 3%.

## Powiązane
[[Myśl przewodnia v2]] · [[Psychologia gracza v2]] · [[Karta ocen v2 i plan sprawdzenia]] · [[Diagnoza pomysłu 2026-11-13]] · [[Gra/Pętla gry v2.canvas]] · [[Karczma (Questy)]] · [[Pety]] · [[HUD]] · [[Telemetria gry]] · [[Klocki — Blender i Roblox]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Zadania]]
