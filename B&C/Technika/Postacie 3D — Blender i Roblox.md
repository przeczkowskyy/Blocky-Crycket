---
status: propozycja
tags: [technika, blender, postacie, 3d, pipeline, animacje]
---
# Postacie 3D — Blender i Roblox

> [!info] W skrócie
> Postacie, pety i ekwipunek powstają **z kodu** (jeden plik Pythona na postać albo zestaw), a z tego samego opisu robimy dwie rzeczy: siatki ze szkieletem i animacjami w Blenderze (FBX/GLB, filmy, ikony) oraz **postacie z części Roblox ze stawami**, które stoją w Studio bez wgrywania czegokolwiek na konto. Sprawdzone 13.11.2026 w Roblox Studio: wszystkie klipy (20 klipów sześciu postaci i 12 klipów manekinów) przechodzą kontrolę w Animatorze — pozy stawów zgadzają się z danymi z Blendera — a po naciśnięciu Play w Studio postacie odtwarzają je po kolei. W opublikowanej grze nic z tego jeszcze nie działa. Druga droga — import siatki — jest sprawdzona na Rycerzu od 13.11.2026 wieczorem. Wszystko ma status propozycji — wygląd postaci zatwierdza Karol albo Paweł (kanon wyglądu: [[Rycerz]], [[Kot-Mag]], [[Karczmarz]], [[Pety]]). 14.11.2026 Karol zaakceptował w panelu raport o Rycerzu (klocki Roblox główną drogą), a na trzeciej sesji tego dnia obaj skłonili się do Blendera dla postaci i petów (propozycja D-065) — sprzeczność do rozstrzygnięcia ([[Pytania otwarte]] #24, [[Sesja główna 2026-11-14 (3) — zapis ustaleń]]).

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
| Stan | **sprawdzone w Studio** (Edit i Play) | **import sprawdzony na Rycerzu** (13.11.2026 wieczorem); animacje i broń na tej postaci jeszcze w sprawdzaniu |
| Wygląd | ostre krawędzie, stożki schodkowe | fazowane krawędzie, jedna siatka brył na kość |
| Koszt w grze | 42–180 części na postać (Rycerz: 129) | Rycerz: 15 części-siatek; pozostałych postaci nie importowano |
| Zgniatanie (slime) | nie (ścianki przesuwają się osobno) | tak (skórowanie) |

Polecenia i szczegóły: `swiat/postacie/README.md`. Budowa w Studio: `python -B swiat/postacie/roblox_postac.py`; usunięcie: `--usun`.

## Import siatek — wynik próby na Rycerzu (13.11.2026)
Po zatwierdzeniu folderu w Studio plik `rycerz.fbx` został wgrany na konto Karola (jeden zasób Model; moderacja zatwierdziła go od razu) i wstawiony do `Workspace/TestPostaci` jako „Rycerz Blocky (import FBX)”, obok wersji z klocków. Polecenie: `python -B swiat/postacie/roblox_import.py --modul rycerz --tak-wgraj`.

Co zmierzono:
- Roblox zrobił z pliku postać R15: 15 części-siatek o standardowych nazwach, `Humanoid` i `HumanoidRootPart`.
- Skala wyszła 1:1 — wzrost 5,71 studa, bez poprawek.
- Kolory są poprawne: każda część ma teksturę-paletę (`SurfaceAppearance`).
- Wszystkie 18 punktów zaczepienia akcesoriów jest na miejscu (głowa, tors, pas, dłonie, stopy, barki).
- Stawy to nowy typ Robloxa (`AnimationConstraint`), a nie `Motor6D` jak w postaci z klocków.

Czego import nie przeniósł i czego jeszcze nie wiemy:
- Miecza nie ma — import bierze tylko części ciała. Broń trzeba dopiąć osobno.
- Animacje nie wchodzą razem z modelem. Czy klipy z postaci z klocków odtworzą się na tej postaci, jest w sprawdzaniu.
- Nie importowano pozostałych postaci. Pety mają własne szkielety, więc ich wynik może być inny.
- Zasób należy do konta Karola. Żeby wczytał się w opublikowanej grze właściciela, trzeba go udostępnić w Creator Dashboard — tego nie sprawdzano.
- Wydajności na telefonie nie mierzono.

## Co trzeba wiedzieć o platformie
- **Animacje.** Klipy stoją w Studio jako `KeyframeSequence` w `AnimSaves` każdej postaci i odtwarzają się w Studio. W opublikowanej grze animacja musi być zasobem Animation; publikuje się ją z Animation Editora i według dokumentacji Roblox ma należeć do właściciela gry (osoby albo grupy). To czynność i decyzja właściciela — zob. [[Pytania otwarte]] #24.
- **Zasoby wgrane przez współpracownika** (siatki, obrazy) trzeba udostępnić grze właściciela w Creator Dashboard, inaczej się nie wczytają.
- **Wgrywanie przez Studio (Open Cloud)** wymaga dwóch zgód w Assistant → Settings → MCP Permissions: zakresów `asset:read`/`asset:write` (włączone) i zatwierdzonego folderu z plikami (od 13.11.2026 zatwierdzony jest `swiat/postacie/wynik` na komputerze Karola).
- **„W grze” znaczy tu wszędzie: po naciśnięciu Play w Roblox Studio.** Kontener `TestPostaci` ma skrypty pokazu, przymierzalni i petów działające tylko w Studio, a klipy nie są jeszcze zasobami. Przed publikacją gry trzeba go usunąć, tak jak `TestWalki`.

## Kontrola jakości kodu (13.11.2026)
Niezależny przegląd dzisiejszego kodu znalazł dziewięć usterek w ścieżkach błędów (m.in. możliwość dwukrotnego wgrania zasobu przy ponownym uruchomieniu, postać zostająca w pozie po nieudanym zrzucie, brak kodu błędu przy odmowie). Wszystkie poprawiono; każdą grupę poprawek sprawdził osobny, wrogo nastawiony weryfikator, a potem przeszły próby w Studio (odmowy, usuwanie i odbudowa kontenera, powrót do spoczynku po błędzie, prawdziwe klawisze). Osobna kontrola twierdzeń poprawiła osiem nieścisłości w opisach.

## Czego nie sprawdzono
- Importu siatek dla postaci innych niż Rycerz oraz animacji i broni na zaimportowanej postaci (zob. wyżej).
- Wydajności na telefonie.
- Postaci jako awatara gracza i chodzącego NPC (dziś to zakotwiczone figury bez `Humanoid`).
- Sloty ekwipunku: 41 przedmiotów katalogu ma te same nazwy slotów i zakładek plecaka co moduł przedmiotów w kodzie gry (stan z 13.11.2026: Helmet, Chest, Gloves, Boots, Amulet, Belt, Ring, Trinket, Weapon; Weapons, Armor, Amulets, Others). Poza kodem gry jest tylko slot „druga ręka” (tarcza, księga), a tors bywa złożony z kilku części modelu. Gotowa tabela w formacie kodu gry leży jako propozycja w `swiat/postacie/roblox/PrzedmiotyPropozycja.luau` (nigdzie niewczytywana). To propozycja, nie kanon ([[System RPG]], [[Pytania otwarte]] #24).

## Powiązane
[[Klocki — Blender i Roblox]] · [[Pipeline assetów]] · [[Panel zespołu]] · [[Rejestr decyzji]] D-029 · [[Pytania otwarte]] #24
