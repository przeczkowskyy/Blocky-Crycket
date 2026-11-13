---
status: propozycja
tags: [technika, blender, postacie, 3d, pipeline, animacje]
---
# Postacie 3D — Blender i Roblox

> [!info] W skrócie
> Postacie, pety i ekwipunek powstają **z kodu** (jeden plik Pythona na postać albo zestaw), a z tego samego opisu robimy dwie rzeczy: siatki ze szkieletem i animacjami w Blenderze (FBX/GLB, filmy, ikony) oraz **postacie z części Roblox ze stawami**, które stoją w Studio bez wgrywania czegokolwiek na konto. Sprawdzone 13.11.2026 w Roblox Studio: wszystkie klipy (20 klipów sześciu postaci i 12 klipów manekinów) przechodzą kontrolę w Animatorze — pozy stawów zgadzają się z danymi z Blendera — a po naciśnięciu Play w Studio postacie odtwarzają je po kolei. W opublikowanej grze nic z tego jeszcze nie działa. Wszystko ma status propozycji — wygląd postaci zatwierdza Game Director (kanon wyglądu: [[Rycerz]], [[Kot-Mag]], [[Karczmarz]], [[Pety]]).

## Co powstało (`swiat/postacie/`)
| Co | Zawartość |
|---|---|
| Postacie | Rycerz Blocky, Kot-Mag Crycket, Karczmarz — szkielet R15 (Kot-Mag ma dodatkowo ogon) |
| Pety | Pies, Slime, Smok — własne szkielety |
| Ekwipunek | zestawy Rekrut, Rycerz, Mag i 8 broni: 41 przedmiotów w `przedmioty.json` (bez statystyk), 65 ikon |
| Animacje | 20 klipów: spoczynek, chód/bieg/lot, atak/czar/zianie, wiwat, zaproszenie, śmiech, szczekanie, skok |
| Prezentacja | `wynik/_zestawienie/` (postacie w jednej skali, katalog ekwipunku, film ze wszystkimi klipami) |
| W Studio | `Workspace/TestPostaci`: sześć postaci na rynku Krzywego Miasteczka ([[Klocki — Blender i Roblox]]), przed punktem startu, oraz trzy manekiny z zestawami ekwipunku |

Dwóch niezależnych krytyków oceniło pierwszą wersję: wygląd 6,5/10, technika 6/10 (40 uwag, część poprawiona). Najsłabsze: brzuch Karczmarza, przeładowany zestaw Maga, sztywne szaty w ruchu, ikony części ubioru. Drugiej wersji krytycy nie oceniali.

## Przymierzalnia zestawów
Przy manekinach z zestawami Rekruta, Rycerza i Maga po naciśnięciu Play w Studio pojawia się podpowiedź „Przymierz”. Po naciśnięciu zestaw ląduje na awatarze gracza jako zwykłe akcesoria Roblox zbudowane z klocków — znów bez wgrywania zasobów. Sprawdzone 13.11.2026 na zwykłym awatarze R15: wszystkie trzy zestawy zakładają się i zdejmują. Dopasowanie jest liczone dla klockowego awatara; zestaw Maga jest za ciężki (527 części) i wymaga uproszczenia, zanim trafi do gry. Sloty i podział na części to nadal propozycja ([[Pytania otwarte]] #24).

## Pety idące za graczem
W uruchomionej grze (w Studio) przy psie, slimie i smoku pojawia się podpowiedź „Weź peta”. Pet idzie wtedy za awatarem: pies biegnie, slime skacze, smok leci nad ziemią, a gdy gracz stoi, pet odpoczywa obok. Klawisz R („Odeślij”) odsyła go na miejsce. Sprawdzone 13.11.2026 w marszu przez rynek. To próba zachowania pod [[Pety]], a nie system: bez omijania przeszkód, zapisu i ekonomii.

## Dwie drogi do Robloxa
| | Postać z klocków (części Roblox) | Siatka (FBX/GLB) |
|---|---|---|
| Wgrywanie na konto | nie | tak (zasób Model, tekstury) |
| Moderacja, czekanie | nie | tak |
| Stan | **sprawdzone w Studio** (Edit i Play) | **nie sprawdzone** — pierwsza próba zatrzymała się na ustawieniu Studio |
| Wygląd | ostre krawędzie, stożki schodkowe | fazowane krawędzie, jedna siatka brył na kość |
| Koszt w grze | 42–180 części na postać | nie sprawdzono (w pliku 13–36 siatek na postać, razem ze znacznikami punktów zaczepienia) |
| Zgniatanie (slime) | nie (ścianki przesuwają się osobno) | tak (skórowanie) |

Polecenia i szczegóły: `swiat/postacie/README.md`. Budowa w Studio: `python -B swiat/postacie/roblox_postac.py`; usunięcie: `--usun`.

## Co trzeba wiedzieć o platformie
- **Animacje.** Klipy stoją w Studio jako `KeyframeSequence` w `AnimSaves` każdej postaci i odtwarzają się w Studio. W opublikowanej grze animacja musi być zasobem Animation; publikuje się ją z Animation Editora i według dokumentacji Roblox ma należeć do właściciela gry (osoby albo grupy). To czynność i decyzja właściciela — zob. [[Pytania otwarte]] #24.
- **Zasoby wgrane przez współpracownika** (siatki, obrazy) trzeba udostępnić grze właściciela w Creator Dashboard, inaczej się nie wczytają.
- **Wgrywanie przez Studio (Open Cloud)** wymaga dwóch zgód w Assistant → Settings → MCP Permissions: zakresów `asset:read`/`asset:write` (włączone) i zatwierdzonego folderu z plikami (brak — do kliknięcia przez człowieka).
- **„W grze” znaczy tu wszędzie: po naciśnięciu Play w Roblox Studio.** Kontener `TestPostaci` ma skrypty pokazu, przymierzalni i petów działające tylko w Studio, a klipy nie są jeszcze zasobami. Przed publikacją gry trzeba go usunąć, tak jak `TestWalki`.

## Kontrola jakości kodu (13.11.2026)
Niezależny przegląd dzisiejszego kodu znalazł dziewięć usterek w ścieżkach błędów (m.in. możliwość dwukrotnego wgrania zasobu przy ponownym uruchomieniu, postać zostająca w pozie po nieudanym zrzucie, brak kodu błędu przy odmowie). Wszystkie poprawiono; każdą grupę poprawek sprawdził osobny, wrogo nastawiony weryfikator, a potem przeszły próby w Studio (odmowy, usuwanie i odbudowa kontenera, powrót do spoczynku po błędzie, prawdziwe klawisze). Osobna kontrola twierdzeń poprawiła osiem nieścisłości w opisach.

## Czego nie sprawdzono
- Importu siatek: skali, kierunku przodu, kolorów z tekstury-palety, kości i punktów zaczepienia po imporcie.
- Wydajności na telefonie.
- Postaci jako awatara gracza i chodzącego NPC (dziś to zakotwiczone figury bez `Humanoid`).
- Sloty ekwipunku: 41 przedmiotów katalogu ma te same nazwy slotów i zakładek plecaka co moduł przedmiotów w kodzie gry (stan z 13.11.2026: Helmet, Chest, Gloves, Boots, Amulet, Belt, Ring, Trinket, Weapon; Weapons, Armor, Amulets, Others). Poza kodem gry jest tylko slot „druga ręka” (tarcza, księga), a tors bywa złożony z kilku części modelu. Gotowa tabela w formacie kodu gry leży jako propozycja w `swiat/postacie/roblox/PrzedmiotyPropozycja.luau` (nigdzie niewczytywana). To propozycja, nie kanon ([[System RPG]], [[Pytania otwarte]] #24).

## Powiązane
[[Klocki — Blender i Roblox]] · [[Pipeline assetów]] · [[Panel zespołu]] · [[Rejestr decyzji]] D-029 · [[Pytania otwarte]] #24
