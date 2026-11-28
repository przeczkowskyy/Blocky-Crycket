---
status: propozycja
tags: [ui, index, przedmioty, pety, sklep, ekwipunek, umiejętności]
źródło: "polecenia Pawła w Claude Code 26.11.2026 (Index, awans z konfetti, ikony przedmiotów, podpowiedź i porównanie, losowanie towaru, rybka przy cenie, zakładka SKILLS)"
---
# Okno Index i podpowiedź przedmiotu (propozycja)

> [!info] W skrócie
> - **Index** (przycisk w [[HUD]]): zakładka PETS — wszystkie pety do zdobycia według krain (Forest, Swamp, Jungle), zdobyte w kolorze, niezdobyte jako sylwetka „???”; zakładka ITEMS — przedmioty z katalogu Karola **tylko dla klasy gracza**, według krain/stopni, z ikonami.
> - **Awans na poziom:** złota wstęga LEVEL UP!, wybuch światła, napis LEVEL N i konfetti (wybuch spod wstęgi i deszcz z góry). Bez dźwięku — w projekcie brak dźwięków UI.
> - **Podpowiedź przedmiotu** (Index, ekwipunek, sklep): nazwa, rzadkość i kraina, statystyki, wymagany poziom; w sklepie cena z rybką. **Porównanie** (lupa w sklepie i ekwipunku): +N / −N / 0 przy każdej statystyce względem założonego przedmiotu w tym samym slocie.
> - **Sklep:** towar losowany przy każdym otwarciu i odświeżeniu (zamiast przewijania stałej listy), tylko przedmioty klasy gracza; rybka przed ceną na ladzie i na karcie.
> - **Okno ekwipunku (przebudowa po konsultacji, Paweł 26.11 wieczorem):** CHARACTER ma dwie szerokie zakładki ATTRIBUTES i INFO; BACKPACK — trzy: ITEMS, OTHERS, SKILLS, a ITEMS i OTHERS mają po 3 strony po 25 slotów (strzałki i tabliczka „1 / 3” pod plecakiem). Pas z 3 slotami umiejętności stoi między postacią a plecakiem, pod lupą; zdobyte umiejętności leżą w zakładce SKILLS i **przeciąga się je na sloty** (ze slotu poza pas = zdjęcie). Zamknięty slot: kłódka na placeholderze kuli ognia. Podpowiedź umiejętności: aktywna/pasywna, koszt many, obrażenia, efekty, premia z drzewka (dane walki Karola, `src/shared/SkilleDane.luau`). Sklep po lewej: te same zakładki ITEMS / OTHERS i strony po 15 slotów.

## Skąd dane
- Pety: dane Karola (`Workspace/PetyProba/Moduly/DanePetow`) przez `src/server/Indeks.server.luau`; kraina peta = kraina jego jajka. Moduły Karola działają tylko w Studio.
- Przedmioty: `src/shared/IndeksPrzedmioty.luau` generowany z katalogu Karola (`swiat/postacie/sklep_przedmioty.json`) przez `tools/indeks_dane.py` — klasa, slot, stopień, poziom, cena, statystyki (baza + poziom ulepszenia × krok, jak u kowala).
- Ikony 80 przedmiotów: render z Blendera Karola, przycięte do 256 px, wgrane 26.11 po „tak” Pawła — `src/shared/IkonyPrzedmiotow.luau`.
- Umiejętności: drzewko (`SkillTreeData`, gałąź SKILLS), wybór w slotach: `src/server/SkillSloty.server.luau`, atrybut gracza `SkillLoadout`.

## Pliki
`src/gui/OknoIndeksu.model.json`, `src/gui/Awans.model.json` (`tools/okno_indeksu_build_gui.py`, grafika `tools/okno_indeksu_ui.py`), `src/client/OknoIndeksuClient.client.luau`, `src/client/AwansClient.client.luau`, `src/client/PodpowiedzPrzedmiotu.luau`, `src/client/ShopClient.client.luau`, `src/client/EquipmentPanelClient.client.luau`, `tools/shop_build_gui.py`, `tools/eq_skille_build.py` (wołany z `tools/eq_build_gui.py`), grafiki slotów: `tools/skille_ui.py`.

## Do ustalenia
- Nazwy przedmiotów w katalogu Karola są po polsku, a reszta interfejsu po angielsku.
- Rzadkość przedmiotów: dziś każdy przedmiot to „COMMON” — system epików i legend czeka na decyzję ([[Rzadkość przedmiotów — zwykłe, epickie, legendarne, sekretne (propozycja)]], pytanie 96).
- Losowanie towaru jest po stronie klienta (serwer Karola i tak sprawdza klasę, poziom i Rybki przy zakupie). Uczciwe losowanie odporne na „przelosowywanie” powinno żyć na serwerze sklepu Karola.
- Przypisanie umiejętności drzewka do walki (propozycja agenta): Power Slash = Potężne cięcie, Crushing Blow = Miażdżący cios, Stone Skin = Kamienna skóra, Shield Block = Mur tarczy (pasywna), War Cry = Furia (pasywna) — `tools/skille_dane.py`.
- Wybór umiejętności w slotach nie zapisuje się między sesjami (stan gracza Karola nie zna pola `SkillLoadout`) i silnik walki go jeszcze nie czyta.

## Stan implementacji
- [x] 2026-11-26: Index (pety według krain, przedmioty klasy z ikonami) i awans z konfetti — wdrożone w Studio, sprawdzone w Play.
- [x] 2026-11-26: 80 ikon przedmiotów wgranych i podpiętych (Index, ekwipunek, sklep).
- [x] 2026-11-26: 5 grafik (ramka slotu, kula ognia, kłódka, strzałka, lupa) wgranych po „tak” Pawła; zakładka SKILLS (tło pod slotami gładkie — zasłona kart statystyk, Paweł), wybór umiejętności z listy, podpowiedź przedmiotu, lupa (między slotem amuletu a plecakiem — Paweł), rybka przy cenie, losowy towar — wdrożone i sprawdzone w Play na komputerze.
- [x] 2026-11-26 (wieczór): przebudowa EQ (zakładki 2 + 3, strony plecaka, pas umiejętności pod lupą, przeciąganie umiejętności, podpowiedź umiejętności), strony w sklepie — 8 grafik z jednej generacji wgranych po „tak” Pawła, wdrożone, w Play sprawdzony układ, zakładka SKILLS i podpowiedź przedmiotu. Przeciągania umiejętności na pas nie udało się sprawdzić (Paweł grał w tej samej sesji). Telefon niesprawdzony.

## Powiązane
- [[HUD]] · [[Okno ekwipunku]] · [[Sklepy i bronie startowe — prompty]] · [[Okno petów (propozycja)]] · [[Okno drzewka umiejętności]]
