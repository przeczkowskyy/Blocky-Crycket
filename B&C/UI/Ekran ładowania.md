---
status: kanon
tags: [ui]
źródło: "[[Dokumentacja projektu (oryginał)]] §4, §6"
implementacja: zbudowany w Roblox (ReplicatedFirst), 2026-11-11
---
# Ekran ładowania

- **Scena:** przerysowani bohaterowie ([[Rycerz]] i [[Kot-Mag]]) biegnący na rozwidleniu dróg między **krzywą Karczmą**, **świecącym Lochem** i **Zamkiem na wzgórzu**.
- **Dół:** gruby, malarski pasek postępu stylizowany na pociągnięcie pędzla.
- **Logo:** z koroną i napisem „BLOCKY & CRYCKET”.

Według dokumentacji kompozycja ekranu jest już wypracowana.

## Propozycje
- ~~Minimalny czas wyświetlania ekranu~~ → wdrożone 2026-11-11 (zob. niżej), do akceptacji.
- Font `Arcade` w pasku nie ma wielkiego „Ó” (wyświetla „WSKAZóWKA”); do rozważenia inny pikselowy font.
- Tło generowane **bez paska postępu**, a pasek jako osobna warstwa nad nim.
- Losowe humorystyczne porady (gobliny, grzyby).

## Projekt w Figmie
- Komponent paska postępu (źródło prawdy wyglądu): [Figma node 2:2](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-2)
- Cały kadr 2752×1536 (pozycja paska): [Figma node 2:75](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-75)
- Key-art zawiera już logo z koroną, Karczmę z [[Karczmarz|Karczmarzem]], portal Lochu, Zamek, [[Rycerz|Rycerza]], [[Kot-Mag|Kota-Maga]], slime'a i psa.
- Pasek: kamienna rama z nitami, drewniany tor z deskami, cyjanowe wypełnienie z ukośnymi paskami, pikselowa iskra na końcu, złoto-ametystowe klejnoty po bokach, procent na środku, pod spodem pikselowa „WSKAZÓWKA”.

## Zachowanie paska i treści (propozycja, wdrożone 2026-11-11)
- Pasek napełnia się **co najmniej 4,5 s** (`MIN_DURATION`), nawet gdy wszystko jest już załadowane. Przy wolnym ładowaniu czeka na prawdziwy postęp.
- Postęp nie rośnie równo: kilka losowych „przystanków” z płynnym zwalnianiem. Na 100% pauza 0,6 s, potem fade-out.
- Tekst pod paskiem to `TextLabel` (`Tip` + cień `TipShadow`), nie obraz. Co 2,6 s (`TIP_INTERVAL`) zmienia się z płynnym przejściem: losowa kategoria i losowy wpis, bez powtórek, dopóki pula się nie wyczerpie.
- Kategorie: **WSKAZÓWKA** (tylko mechaniki z kanonu: [[Twierdza (Tycoon)]], [[Pety]], [[Karczma (Questy)]]), **PLOTKA Z KARCZMY** i **CIEKAWOSTKA** (humor: gobliny, grzyby, bohaterowie).
- Przed fade-outem `LoadingClient` ustawia atrybut gracza `LoadingDone = true`: to sygnał dla [[HUD]], że może się pojawić.
- Wszystkie teksty i ustawienia są na górze `LoadingClient` (źródło: `tools/studio/build_loading_screen.luau`).
- Usunięto wcześniejsze wskazówki o Arenie i „Sklepie z magią”, bo tych mechanik nie ma w kanonie.

## Stan implementacji
- [x] Ilustracja tła (key-art gotowy w Figmie)
- [x] Logo (w key-arcie)
- [x] Tło wgrane do Roblox: `rbxassetid://129202798952612` (2026-11-11)
- [x] `ReplicatedFirst.LoadingScreen` (ScreenGui) + `ReplicatedFirst.LoadingClient` (LocalScript), zbudowane przez Roblox Studio MCP skryptem `tools/studio/build_loading_screen.luau` (2026-11-11)
- [x] Podgląd w Studio zgodny z Figmą (node 2:75); Play Solo bez błędów skryptu (2026-11-11)
- [x] Plik `.rbxl` zapisany w Studio: po ponownym otwarciu Studio obiekty w ReplicatedFirst były na miejscu (2026-11-11)
- [ ] Test na prawdziwym serwerze / telefonie (w Studio ładowanie trwa ~1 s)

> [!note] Uwaga techniczna
> ReplicatedFirst nie jest mapowany przez Rojo, więc te obiekty będą istnieć tylko w pliku `.rbxl`. Skrypt budujący warto trzymać też jako plik, żeby dało się go odtworzyć.
