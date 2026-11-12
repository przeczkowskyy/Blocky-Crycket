---
status: propozycja
tags: [gra, game-design, rozmowa, rekomendacje]
---
# Propozycje z rozmowy 2026-11-12

> [!info] W skrócie
> Komentarz Claude'a do pomysłów z [[Rozmowa 2026-11-12 — zapis ustaleń]] — o to prosiliście w [32:45], łącznie z prawem do niezgody. Kierunek jest dobry: hub 3D, szybka pętla, pety, lochy. W trzech miejscach się nie zgadzam: **czekanie na quest** (nawet 3 minuty to za długo na pierwszą sesję), **płatna losowość** (zasady Roblox i nadchodzące przepisy) oraz **twierdza dopiero od 25. poziomu** (to najmocniejszy haczyk gatunku, powinien wejść w pierwszej sesji). Nic tutaj nie jest kanonem — rozstrzygnięcia czekają w [[Pytania otwarte]] i [[Rejestr decyzji]].

## Pętla, którą proponuję
```
plac → karczma: wybierz strefę → walka 8–15 s (auto, cutscenka) → łup + rozgłos strefy
     → sklep / ulepszenie statystyk → mocniejszy quest → loch (10 przeciwników + boss) → nowa strefa
w tle, równolegle: jajko w wylęgarni · najemnik na wyprawie · budynki twierdzy dające zasoby na sekundę
```
Zasada: **gracz nigdy nie patrzy na pasek czasu, nie mając nic innego do kliknięcia**. Długie liczniki istnieją, ale tylko jako równoległe sloty (jajko, wyprawa najemnika, budowa), a ich odbiór jest powodem powrotu do gry. To godzi obie strony sporu z [11:32–13:14] i nie łamie decyzji D-004 (aktywna rozgrywka).

## Komentarz punkt po punkcie
| Temat [czas] | Wasz pomysł | Zdanie Claude'a | Rekomendacja |
|---|---|---|---|
| Hub 3D + mapa 2D [1:32–2:56] | Miasteczko 3D, teleport z mapy z budynkami | **Tak.** Mapa 2D to jednocześnie nawigacja i ekran postępu (wyszarzone, niezbudowane miejsca kuszą) | MVP: 5 punktów na mapie — karczma, sklep, wylęgarnia, loch, arena (wyszarzona) |
| Teleport za Robuxy albo od poziomu [3:42] | Początkujący ma chodzić | **Nie zgadzam się.** Ok. 80% graczy gra na telefonie, a Roblox mierzy wyjścia w pierwszej minucie; przymusowe chodzenie na starcie to utrata graczy, nie zaangażowanie | Budynek odkryty pieszo = odblokowany na mapie za darmo. Sprzedawać wygodę inną: wierzchowce, sloty, VIP |
| Sprint i wierzchowce [4:35–5:04] | Shift = sprint, stajnia = mounty | **Tak.** Wierzchowiec to kolekcja i prestiż widoczny dla innych graczy | Sprint za darmo; wierzchowce z gry i jako kosmetyka premium, bez wpływu na walkę |
| Quest 3 min skracany rozgłosem [8:54–10:17] | Od 3 min do 5 s | **Mechanika rozgłosu świetna, punkt startu zły.** Trzy minuty czekania w pierwszej sesji to ryzyko, którego nie da się odrobić | Start: walka od razu (8–15 s). Rozgłos strefy zwiększa nagrody i odblokowuje „serię” (kilka walk jednym kliknięciem). Długie wyprawy tylko w slocie równoległym |
| Najemnik [10:18–13:14] | Automat do questów | **Wariant Karola.** Pełny automat zabija powód, by grać | Najemnik = drugi, równoległy slot wyprawy w strefie już opanowanej; bez wpływu na PvP |
| Walka 2D czy cutscenka 3D [7:06, 16:44] | Do sprawdzenia | Decyzja po teście. Wynik walki zawsze liczy serwer, a klient tylko go odtwarza — wygląd można zmienić później bez ruszania balansu | Test: 2 postacie R15, 3 animacje, 8–10 s, kamera skryptowa, przycisk „pomiń”; pomiar na tanim telefonie |
| Zbieractwo [26:46–28:02] | Odrzucone | **Zgoda z Pawłem** | Różnorodność dawać typami przeciwników i bossów, nie zbieraniem |
| Lochy [28:19–29:57] | 10 przeciwników po lokacji, boss, 3 trudności | **Najmocniejszy element rozmowy.** To oś, wokół której warto zbudować pierwsze demo | Jeden loch w MVP; trudność średnia i trudna jako powód powrotu |
| Sklep 6 slotów co 5 min [14:15] | Osobny dla gracza | **Tak** | Odświeżanie za darmo co 5 min; tokeny odświeżenia tylko z gry |
| Tokeny odświeżenia za Robuxy [14:49] | Dokupowane | **Nie.** To płatne losowanie: Roblox wymaga wtedy tabeli szans i blokady w części krajów, a projekt unijnych przepisów mierzy właśnie w takie mechaniki dla nieletnich | Sprzedawać pewność zamiast losu: przypięcie slotu, zakup konkretnego przedmiotu po stałej cenie, dodatkowe darmowe odświeżenie dziennie w VIP |
| Gwarantowany epik co 30 min [15:10] | Żeby gracze kampili | **Częściowo.** Zegar uczy stania bez ruchu. Wspólne wydarzenia co 30/60 min są za to bardzo dobre | Sklep: widoczny licznik „epik za N zakupów/walk”. Świat: boss strefy co 30 min dla całego serwera, z ogłoszeniem |
| Koło fortuny i „gambling” [6:56, 17:35] | Darmowy spin + płatne tokeny | **Darmowe koło tak, hazard nie.** Stawianie waluty na szansę wygranej to symulowany hazard, zakazany w zasadach Roblox. „Labubu” to cudza marka | Koło tylko z darmowymi spinami (czas, aktywność, VIP +1 dziennie). Własna postać i nazwa |
| Pojedynki [16:19] | Okienko nad graczem | **Tak**, liczone jak quest (log z serwera) | Bez przewagi z płatnych mnożników albo osobne ligi — inaczej zarzut pay-to-win |
| Ekwipunek [18:17] | 8 slotów, 4 zakładki | **Tak** | 6 poziomów rzadkości kolorem ramki; dodatkowe sloty jako uczciwy produkt premium |
| Statystyki [19:19] | Punkty za poziom + ulepszanie za złoto | **Tak.** Duże, rosnące liczby to sedno gatunku | Od początku zapis walut jako mantysa i wykładnik; formatowanie K / M / B |
| Serwer [20:13–21:13] | 20 czy 1000 graczy | **Rację ma Paweł.** Limit platformy to 200, a gry z działkami trzymają kilka–kilkanaście osób | Hub na 16–20 graczy; tłum przy bossie robi wspólny stan wszystkich serwerów, nie jeden wielki serwer |
| Twierdza od 25. poziomu [21:46] | Tycoon jako późna nagroda | **Nie zgadzam się z progiem.** Dochód na sekundę to najsilniejszy haczyk gier Roblox w 2025–2026; schowany za 25 poziomami nie zadziała na większość graczy | Pierwszy budynek w pierwszej sesji (10–15 min), rozbudowa z poziomami; pełna działka i rajdy później |
| Rajdy i wojny gildii [22:48–25:35] | Także między światami | **Wykonalne, ale asynchronicznie** (walka symulowana ze statystyk, ranking miesiąca) | Po MVP. W HUD przycisk gildii oznaczyć „wkrótce” albo schować |
| Strefy przez portale [25:53] | Portale do biomów | **Tak** | Na start jedno miejsce z doczytywaniem świata; osobne miejsca dopiero dla dużych biomów |
| Pety [30:13–31:09] | Od wyższego poziomu, wylęganie na czas | **Tak, ale wcześniej.** Pety to trzon gatunku — powinny być w MVP | Pierwsze jajko wykluwa się od razu (samouczek), kolejne 1–10 min w slotach; walki petów jako event tygodniowy później |
| Eventy tygodniowe [31:09] | Środa, weekend | **Tak**, i to tanio: konfiguracja zmieniana bez publikowania nowej wersji gry | Kalendarz 3 eventów na start |
| Wypuszczanie etapami [23:13] | Nie wszystko naraz | **Zdecydowanie tak** | MVP jednej pętli i test popytu, zob. [[Ocena potencjału gry]] |

## „Wciągająca i zarabiająca” — gdzie stawiam granicę
Prosiliście o grę uzależniającą i skłaniającą do mikropłatności [3:42, 27:40]. Pomogę zrobić grę, do której chce się wracać, i uczciwie ją spieniężyć. Nie będę projektował mechanik, które żerują na dzieciach: ukrytych kosztów, sztucznej presji czasu na zakup, hazardu. To nie tylko kwestia zasad — to też rachunek: około 70% zweryfikowanych graczy Roblox to nieletni, platforma i regulatorzy zaostrzają reguły co kwartał, a gra oparta na płatnej losowości może stracić źródło przychodu jedną zmianą regulaminu. Uzasadnienie i lista „rób / ostrożnie / nie rób”: [[Retencja i monetyzacja — co wolno i co działa]].

Na czym zarabiać: przepustka VIP (wygoda: dodatkowe sloty, +1 darmowe odświeżenie, +1 spin), pakiet startowy, sloty ekwipunku / wylęgarni / wypraw, mnożniki czasowe 2×, kosmetyka (wierzchowce, skórki petów, wygląd twierdzy), przepustka sezonowa z darmową ścieżką.

## Sprzeczności z kanonem do rozstrzygnięcia
- **D-004** (aktywna rozgrywka, bez pasków czasu) a questy na czas i wylęganie → proponowana pętla wyżej je godzi; decyzja należy do Was ([[Pytania otwarte]] #7).
- **Kanon [[Karczma (Questy)]]** (trzy misje, mini-dungeon) a strefy z rozgłosem i osobne lochy (#8).
- **Kanon [[Twierdza (Tycoon)]]** (droppery, Złoto i Magiczne Kryształy) a surowce i klejnoty do gniazd (#9, łączy się z #6).
- **Styl**: kanon mówi o pixel-arcie i płaskim designie, a wdrożone grafiki to „bubbly cartoon”, który na Roblox się sprawdza (#10, [[Styl UI gier Roblox]]).
- **D-008** (porzucony dashboard) a [[Panel zespołu]] (#11).

## Powiązane
[[Rozmowa 2026-11-12 — zapis ustaleń]] · [[Ocena potencjału gry]] · [[Shakes & Fidget — rozbiór mechanik]] · [[Technika gry — serwery, światy, walki]] · [[Rynek Roblox i konkurencja]] · [[Koncepcja i Core Loop]] · [[Rejestr decyzji]]
