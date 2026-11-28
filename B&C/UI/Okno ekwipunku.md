---
status: propozycja
tags: [ui, ekwipunek, figma]
źródło: "grafika od Game Directora 2026-11-13 (assets/raw/EquipmentPanel/source.png)"
---
# Okno ekwipunku

## Opis
Okno otwierane przyciskiem **Equipment** w [[HUD]]. Lewa część **CHARACTER**: 8 slotów ekwipunku (hełm, zbroja, rękawice, buty, amulet, pas, pierścień, talizman), slot broni, portret postaci z plakietką poziomu, zakładki ATTRIBUTES / DESCRIPTION / INFO / INTERACTIONS, 6 kart statystyk z przyciskiem „+” i 3 sloty mikstur. Prawa część **BACKPACK**: zakładki WEAPONS / ARMOR / AMULETS / OTHERS i siatka 5×5 slotów. X w prawym górnym rogu zamyka okno.

Statystyki na grafice (Strength, Constitution, Intelligence, Dexterity, Luck, Armor) to **propozycja**. Kanon systemu RPG jest w [[System RPG]].

## Jak zbudowane
- Grafika od Game Directora → `tools/eq_clean_text.py` usuwa wypalony tekst → `tools/eq_paint.py` poprawia tabliczki kart i mikstury → `tools/eq_slice.py` tnie na elementy i zapisuje `layout.json` → `tools/eq_build_gui.py` generuje GUI.
- **Tło**: 4 kafelki `EqBg1–4` (2048×1166 pocięte 2×2, bo Roblox zmniejsza obraz do 1024 px).
- **Osobne grafiki**: `EqClose`, `EqPlus`, 8× `EqTab*` (przezroczyste tło, nakładane w to samo miejsce co w tle).
- **Natywnie**: wszystkie napisy (Luckiest Guy + `UIStroke`), sloty / mikstury / plecak jako niewidzialne przyciski (bez ramek; decyzja Game Directora 2026-11-13), portret jako `ViewportFrame`.
- Figma: plik `BbLd4jDnvxAmOWZN1hAZQJ`, strona „Equipment Panel”, ramka [EquipmentPanel 23:74](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=23-74), komponent `EqPlus` (23:112).
- Roblox: `src/gui/EquipmentPanel.model.json` (generator `tools/eq_build_gui.py`), logika `src/client/EquipmentPanelClient.client.luau`. Zdarzenia dla innych skryptów: `ReplicatedStorage.EquipmentPanelAction` (`Opened`, `Closed`, `Tab`, `Slot`, `BagSlot`, `Potion`, `AddStat`).

## Do ustalenia
- Koszt „+” (punkty statystyk? złoto?) i zapis w DataStore. Wzory podpisów w kodzie są tymczasowe (dobrane do wartości z grafiki).
- Lista statystyk i wzory (Damage, Hit Points, Defense, Critical Hit, Damage Red.) → [[System RPG]].
- Co pokazują zakładki DESCRIPTION / INFO / INTERACTIONS.
- Napisy po angielsku czy po polsku ([[Pytania otwarte]] #5).

## Stan implementacji
- [ ] 2026-11-26 (Paweł): zakładka DESCRIPTION → SKILLS (3 sloty umiejętności z kłódkami, lista do wyboru), podpowiedź przedmiotu i przycisk porównania — kod gotowy, opis: [[Okno Index i podpowiedź przedmiotu (propozycja)]].
- [x] 2026-11-23: bez przycisków „+” przy statystykach (statystyki z treningu i przedmiotów); zakładki wymazane z tła i animowane (aktywna większa, najechanie, kliknięcie).
- [x] 2026-11-23: ramka postaci z portretem rasy (`RaceFrame<Rasa>`); stara ramka wymazana z tła `EqBg1` (tools/wymaz_stare_ramki.py).
- [x] Grafika oczyszczona z tekstu i pocięta na elementy (2026-11-13)
- [x] Ramka w Figmie z warstwami i natywnym tekstem (2026-11-13)
- [x] `EquipmentPanel.model.json` + `EquipmentPanelClient` (otwieranie z HUD, zakładki, hover slotów, „+”) (2026-11-13)
- [x] Upload 14 grafik przez Roblox Studio MCP (2026-11-13, po „tak”)
- [x] Poprawki po teście (2026-11-13): obramowania mikstur w pierścieniu, flaszka w 1. slocie, skróty STR/CONST/INT/DEX/LUCK/ARMOR, zaokrąglone tabliczki kart (`tools/eq_paint.py`), mniejsze natywne „+” z animacją, `EqBg3` v2
- [x] Przeciąganie przedmiotów (test: `Scrap` w slocie Trinket, `ReplicatedStorage.Shared.Items`; stan tylko po stronie klienta)
- [x] Test Play w Studio: okno otwiera się z HUD, brak błędów skryptu (2026-11-13)
- [x] Przeciąganie naprawione i przetestowane myszą w Play (2026-11-13): Trinket → plecak, odrzucenie na hełmie (ikona się trzęsie i wraca), plecak → Trinket
- [x] Poprawki 2 (2026-11-13): karty bez ciemnych krawędzi i plam pod nazwą (`EqBg3` v3, wgrany 2026-11-13, ID 101459179682764; Figma zsynchronizowana), „+” podnosi statystykę przez serwer (`StatPoints.server.luau`, RemoteEvent `AddStatPoint`, test bez kosztu), podpisy DMG/HP/DEF/CRIT przeliczane (wzory: propozycja), plecak z osobną stroną na każdą zakładkę (Scrap = Amulets). Test Play: STR 20→23, Scrap widoczny tylko w AMULETS
- [x] Karty v4 (każda kolumna z własnymi granicami) wgrane: `EqBg3` 134448521798525 (2026-11-13)
- [x] Zasłonka sylwetki w slotach ekwipunku: natywna ramka `Cover` w kolorze wnętrza slotu, widoczna tylko z przedmiotem (`ZIndex` 1, ikona 2). Test Play OK (2026-11-13)
- [x] Rozmiary napisów: statystyki 15 px, zakładki postaci 16 px, zakładki plecaka 20 px (2026-11-14)
- [x] Hover bez artefaktów (2026-11-14): przyciski powiększają się wokół środka (zakładki: wokół środka dolnej krawędzi, podstawa zostaje przy panelu), 8 zakładek wyciętych od nowa bez kawałków tła (`tools/eq_slice.py`, tryb `tight`) i wgranych po „tak” Game Directora; X i „+” bez zmian
- [x] Broń startowa w slocie broni (Paweł 18.11): po wyborze klasy `Slot_Weapon` dostaje broń klasy — `StarterClub` (Wojownik), `StarterSlingshot` (Zwiadowca), `StarterStaff` (Mag) w `Shared.Items`, klasa → broń w `ClassData.Classes[].weapon`. Ikony z górnego rzędu arkusza Pawła (`tools/bronie_startowe_ikony.py`), wgrane po „tak” Pawła przez Studio MCP (ID w manifeście `Weapon*`). Stan tylko po stronie klienta, jak reszta ekwipunku; bez statystyk. Test Play: Mag → ikona kostura w slocie broni
- [x] Sloty broni według klasy (Paweł 18.11): Wojownik — slot broni przesunięty w lewo i nowy slot tarczy `Slot_OffHand` obok (para na środku pod paskiem poziomu), Mag — sylwetka kostura, Zwiadowca — sylwetka procy. Sylwetki z jednego arkusza Higgsfield (wariant 3 wybrany przez Pawła, `assets/raw/SlotPlaceholders/`), pocięte i złożone z prawdziwą ramką slotu z tła (`tools/slot_placeholders.py`: wymazany miecz, w miejscu starego slotu odtworzona ściana), w Figmie na stronie „Equipment Panel” (ramka „Weapon slot placeholders”, 43:74), wgrane po „tak” Pawła (`SlotPairWarrior`, `SlotWeaponMage`, `SlotWeaponScout`). W grze nakładka `Background.ClassSlots` w `EquipmentPanelClient`. Test Play: Wojownik (kij + tarcza), Mag (jeden slot na środku). Propozycja wyglądu
- [x] Pasek doświadczenia natywny (Paweł 18.11: wypalony w tle był rozmazany i miał łatę po usuniętym napisie „LV”): `Background.ExpBar` na wnętrzu złotej ramki, zielone wypełnienie z gradientem i połyskiem = `XP / XPMax`, animowane. Test Play: XP 7/12 → 58%
- [x] 2026-11-23 (Paweł): stan ekwipunku we wspólnym module `src/client/EkwipunekStan.luau` — ten sam stan pokazuje lewa strona sklepu ([[Sklepy i bronie startowe — prompty]], „Sklep oskryptowany”). Przedmioty kupione u zbrojmistrza (kowal Karola) trafiają do EQ: założone do swojego slotu, reszta do plecaka; bez ikony kolorowy kafelek stopnia z nazwą, ulepszenie jako „+N”. Test Play: kupiony kapelusz w slocie hełmu w EQ i w sklepie
- [ ] Test na telefonie (Device Emulator)
- [ ] Prawdziwe dane: statystyki z serwera, portret postaci; przełożenie przedmiotu w EQ nie zakłada go jeszcze u kowala (zakładanie: przycisk EQUIP w sklepie albo przymierzalnia)
- [x] 2026-11-17 (Paweł): przyczyna „czegoś pod przyciskiem”: zakładki i X miały miękki, półprzezroczysty brzeg, przez który przy przyciemnieniu prześwitywała jasna kopia wypalona w tle. Wymazywanie kopii z tła (pierwsza próba) zostawiało rozmazane plamy, np. na karcie STR — cofnięte, tło wróciło do oryginału. Twardy brzeg (druga próba) dawał grube czarne krawędzie — też cofnięty. Ostatecznie: oryginalne grafiki zakładek i X leżą co do piksela na swoich kopiach w tle i nigdy się nie skalują ani nie przyciemniają same; reakcję robi klient — cień-nakładka w kształcie przycisku (nieaktywna zakładka, najechanie, wciśnięcie) i podskok napisu (`flatButton` w `EquipmentPanelClient`). Znaczek klasy (emblemat z ekranu wyboru) przy „LV”.

## Powiązane
- [[HUD]] · [[System RPG]] · [[Pipeline assetów]] · [[Pipeline Figma → Roblox]] · [[00 Start]]
