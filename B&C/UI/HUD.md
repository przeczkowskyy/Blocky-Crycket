---
status: kanon
tags: [ui]
źródło: "[[Dokumentacja projektu (oryginał)]] §4"
implementacja: wersja z Figmy (panel gracza + 6 przycisków) w Roblox, 2026-11-11
---
# HUD (główny ekran)

| Obszar | Elementy |
|---|---|
| **Lewa góra** | okrągły awatar bohatera, Level, ukośne paski: HP (czerwony), Mana/Energia (niebieski), postęp EXP |
| **Prawa góra** | liczniki Złota i Magicznych Kryształów z pixel-artowymi ikonami |
| **Krawędzie boczne** | nachylone, komiksowe zakładki: Karczma (kufel), Pety (jajko), Tycoon (zamek), Arena (miecze), Ekwipunek (plecak) |
| **Dół** | hotbar umiejętności i wielki przycisk akcji/ataku |

## Wersja z Figmy (wdrożona 2026-11-11, układ przycisków czeka na decyzję)
> [!warning] Konflikt z kanonem
> Kanon (tabela wyżej) przewiduje 5 zakładek: Karczma, Pety, Tycoon, Arena, Ekwipunek. Figma ma 6 przycisków: **Teleport, Equipment, Pets** (lewa) i **Quests, Shop, Guilds** (prawa), z angielskimi napisami. Wdrożono wersję z Figmy na polecenie Game Directora; kanon bez zmian do decyzji. Zob. [[Pytania otwarte]].

- Figma: layout [node 9:1571](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1571), panel gracza [14:145](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=14-145), przyciski [9:1570](https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1570).
- **Panel gracza (lewa góra):** ramka portretu (`rbxassetid://128244393062229`) z paskiem XP i poziomem; Złoto (`…139011825868727`), Diamenty (`…130974323293639`) i **Rybki** (trzeci wiersz pod Diamentami, dodany na polecenie Game Directora 2026-11-14; atrybut `Fish`, licznik `#FFA53D`; rola waluty → [[Pytania otwarte]] #44). Liczby z separatorem tysięcy („125 430”), animowane.
- **Przyciski:** 150 px @1080p (Figma: 128; powiększone na prośbę Game Directora 2026-11-11), odstęp 21, 40 px od boku, dół 160 px od dołu jak w Figmie. Limity: min 66 px, max 175 px. Telefon: kolumny wyśrodkowane na 55% wysokości.
- **Wejście:** HUD ukryty do końca [[Ekran ładowania|ekranu ładowania]] (atrybut gracza `LoadingDone`), potem panel zjeżdża z góry, przyciski wjeżdżają z boków.
- **Dane (tymczasowo):** atrybuty gracza `Level, XP, XPMax, Gold, Gems, Fish` ustawiane przez `PlayerStatsDefaults` (placeholder do czasu DataStore).
- **Kliknięcia:** `ReplicatedStorage.HUDButtonPressed` (BindableEvent na kliencie) z nazwą przycisku. Okien (Shop, Pets…) jeszcze nie ma.
- Pliki: `src/gui/HUD.model.json`, `src/client/HUDClient.client.luau`, `src/server/PlayerStatsDefaults.server.luau`.

## Układ z 2026-11-25 (polecenie Pawła, czeka na Karola)
> [!warning] Propozycja w grze
> Wdrożone na próbę w Studio; układ z Figmy (dwie kolumny) i tabela kanonu wyżej zostają bez zmian do decyzji — [[Pytania otwarte]] 102.

- **Pięć podłużnych przycisków jeden pod drugim** (Paweł 25–26.11, zamiast dwóch rzędów po 3): Teleport, Equipment, Pets, Index, Shop — ikona po lewej, napis po prawej. Kolumna zaczyna się pod panelem gracza, środek na wysokości strzałki szuflady questów; przycisk ok. 89 × 272 px przy 1080p. Na telefonie ta sama kolumna, wyższa względem ekranu (przycisk ok. 38 px przy 375 px) — dół sięga ok. 80% ekranu, w strefę drążka; do sprawdzenia na telefonie.
- **Gildie wyłączone na razie** (Paweł 25.11): `GuildsSlot` zostaje w modelu, ukryty.
- **Grafiki:** przyciski z jednej generacji Higgsfield (wzór: stare kwadratowe ikony) — `HudWide<Nazwa>`, `tools/hud_podluzne_ui.py`; napisy jako obrazki w stylu z Figmy (Luckiest Guy, żółty gradient, gruby czarny obrys, brązowy cień od dołu; EQUIPMENT biały) — `HudLabel<Nazwa>`, `tools/hud_napisy_figma.py`, edytowalne źródło w pliku Figmy „Blocky & Crycket — napisy przycisków HUD” na drugim koncie Pawła. Zapas: napisy wycięte ze starych ikon (`assets/processed/HudPodluzne/wyciete_ze_starych/`, `tools/hud_podluzne_napisy.py`).
- **Index zamiast Quests:** otwiera okno kolekcji — [[Okno Index i podpowiedź przedmiotu (propozycja)]] (od 26.11).
- **Questy w szufladzie po prawej:** zakładka ze strzałką wysuwa panel zza krawędzi ekranu i chowa go. Treść to na razie trzy przykładowe wpisy bez postępu i nagród; docelowo miejsce na zadania na czas z [[Karczma (Questy)|karczmy]] (D-034: licznik zadania w HUD).
- **Pets** otwiera [[Okno petów (propozycja)]].
- Pliki: `tools/hud_pety_build_gui.py` (przerabia `src/gui/HUD.model.json`), `src/client/HUDClient.client.luau`, `src/client/QuestyClient.client.luau`. Kolumna nazywa się nadal `LeftColumn`, bo wskazówki Karola szukają `HUD/LeftColumn/TeleportSlot/Teleport`.

## Stan implementacji
- [x] 2026-11-26 (Paweł): pięć podłużnych przycisków w jednej kolumnie, bez gildii, napisy w stylu z Figmy — wgrane (10 obrazów po „tak” Pawła), wdrożone w Studio, sprawdzone w Play na komputerze (napisy wczytane, Teleport otwiera mapę krain, kliknięcia Equipment/Pets/Index/Shop dochodzą). Nie sprawdzone: telefon.
- [x] 2026-11-25 (Paweł): szuflada questów pokazuje questy wybrane na tablicy — [[Tablica questów (propozycja)]]; pusta mówi, gdzie je wziąć.
- [x] 2026-11-25 (Paweł): przyciski w dwóch rzędach po lewej, Index zamiast Quests, szuflada questów po prawej, okno petów pod przyciskiem Pets — sprawdzone w Play (opis wyżej).
- [x] 2026-11-24 (Paweł): HUD od razu na miejscu (bez wlatywania przycisków), okna bez wjazdu, wczytywanie i podgrzewanie grafik przy starcie (`PreloadUI`); licznik Rybek usunięty (D-146), ikona Złota → rybka po wgraniu `GoldFish`.
- [x] 2026-11-24 (Paweł): ramki portretu z kotami (`RaceFrame<Id>_v2`): ta sama złota ramka i tor paska co do piksela, nowy portret kota (`tools/raceportraits_koty.py`); wgrane, pasek w Play na miejscu.
- [x] 2026-11-23: ramka portretu z portretem rasy gracza (`RaceFrame<Rasa>`, Shared.RacePortraitUI podmienia FrameArt; bez rasy pusta PlayerFrame).
- [x] ScreenGui `HUD` (`src/gui/HUD.model.json`), zgodny z Figmą 9:1571 (2026-11-11)
- [x] Logika HUD: `src/client/HUDClient.client.luau` (2026-11-11)
- [x] Ikony walut: moneta i diament z Figmy (2026-11-11)
- [x] Wiersz Rybek: Figma (komponent Player Panel 14:145, ikona 30:114), `HUD.model.json`, `HUDClient`, `PlayerStatsDefaults`, miejsce z chmury przez MCP; test Play OK (2026-11-14)
- [x] Ikona Rybki w Roblox: `rbxassetid://92474194471064` (upload po „tak” Game Directora, 2026-11-14; test Play: wczytana)
- [x] Test Play Solo: ukryty podczas ładowania, animacje wejścia, zmiany XP/Złota/Poziomu/Diamentów z serwera, kliknięcia w Output (2026-11-11)
- [ ] Test na telefonie (Device Emulator): przyciski vs joystick/skok, panel vs przyciski Robloxa
- [ ] Hover na przyciskach sprawdzony ręcznie myszą
- [ ] Moduł statystyk gracza / DataStore jako prawdziwe źródło danych ([[Zadania]])
- [ ] Paski HP i Many/Energii (kanon, brak w Figmie)
- [ ] Portret bohatera w `PortraitSlot` (ViewportFrame)
- [ ] Okna po kliknięciu przycisków

Propozycja techniczna: skalowanie przez Scale z `UIAspectRatioConstraint` (telefony), elementy co najmniej 5% od krawędzi, animacje pasków przez `TweenService`.

Zob. [[Kierunek artystyczny]], [[System RPG]].
- [x] 2026-11-17 (Paweł): znaczek klasy na dolnym rogu portretu, nad paskiem poziomu (w pierwszej wersji zasłaniał początek paska XP).
- [x] 2026-11-17 (Paweł): paski Złota, Diamentów i Rybek z półprzezroczystym ciemnym tłem (60% krycia, jak karta wyboru klasy) — ikony, liczby i złota ramka z cienkim tuszem zostają; znaczek klasy (emblemat z ekranu wyboru klasy) przy liczbie poziomu.
