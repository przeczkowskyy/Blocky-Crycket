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

## Stan implementacji
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
