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
- Miecza nie ma, bo nie było go w pliku `rycerz.fbx` (eksport zawierał tylko ciało). Import bierze wszystko, co jest w pliku; broń trzymaną osobno trzeba dopiąć osobno.
- Animacje nie wchodzą razem z modelem. Czy klipy z postaci z klocków odtworzą się na tej postaci, jest w sprawdzaniu.
- Nie importowano pozostałych postaci. Pety mają własne szkielety, więc ich wynik może być inny.
- Zasób należy do konta Karola. Żeby wczytał się w opublikowanej grze właściciela, trzeba go udostępnić w Creator Dashboard — tego nie sprawdzano.
- Wydajności na telefonie nie mierzono.

## Co trzeba wiedzieć o platformie
- **Animacje.** Klipy stoją w Studio jako `KeyframeSequence` w `AnimSaves` każdej postaci i odtwarzają się w Studio. W opublikowanej grze animacja musi być zasobem Animation; publikuje się ją z Animation Editora i według dokumentacji Roblox ma należeć do właściciela gry (osoby albo grupy). To czynność i decyzja właściciela — zob. [[Pytania otwarte]] #24.
- **Zasoby wgrane przez współpracownika** (siatki, obrazy) trzeba udostępnić grze właściciela w Creator Dashboard, inaczej się nie wczytają.
- **Wgrywanie przez Studio (Open Cloud)** wymaga dwóch zgód w Assistant → Settings → MCP Permissions: zakresów `asset:read`/`asset:write` (włączone) i zatwierdzonego folderu z plikami (od 13.11.2026 zatwierdzony jest `swiat/postacie/wynik` na komputerze Karola).
- **„W grze” znaczy tu wszędzie: po naciśnięciu Play w Roblox Studio.** Kontener `TestPostaci` ma skrypty pokazu, przymierzalni i petów działające tylko w Studio, a klipy nie są jeszcze zasobami. Przed publikacją gry trzeba go usunąć, tak jak `TestWalki`.

## Modele lasu (14.11.2026) — co wiedzieć przy imporcie
Sześć modeli do walki (każdy `propozycja`, raport do akceptacji w panelu, pliki w `swiat/postacie/wynik/<id>/`). Od 15.11.2026 w Roblox są Zwiadowca i Leśny Troll (zob. „Import modeli lasu” niżej); pozostałe cztery jeszcze nie.

| Model | Rola | Szkielet | Broń | Wzrost (gracz 5,7) | Klipy |
|---|---|---|---|---|---|
| [[Zwiadowca]] | druga klasa gracza | R15 (zaczepy jak Rycerz) | łuk i sztylet jako osobne przedmioty | 5,76 | idle, ruch, atak, umiejetnosc (strzał), uderzenie_z_gory, trafienie, unik, upadek, wiwat |
| [[Leśny Troll]] | rzadki, ciężki przeciwnik | własny, 18 kości | maczuga jako kość modelu | 9,94 | idle, ruch, atak, umiejetnosc, trafienie, unik, upadek, ryk |
| [[Cierniowy Wilk]] | zwykły, szybki | własny, 22 kości (czworonóg) | brak | ok. 3 w kłębie | jak wyżej |
| [[Muchomornik]] | zwykły | własny, 29 kości (w tym zarodniki) | laska jako kość modelu | 3,60 | jak wyżej (wiwat zamiast ryku) |
| [[Strażnik Gaju]] | strażnik biomu | własny, 37 kości (w tym korzenie) | brak — pięści | 14,54 | jak wyżej |
| [[Leśny Slime]] | zwykły | własny, skórowanie galarety na dwóch kościach | brak | 2,6 | jak wyżej (wiwat) |

Wspólne uwagi z przeglądów (szczegóły i klatki trafień w notatkach modeli):
- Tylko Zwiadowca jest R15. Pięć potworów ma własne szkielety, więc ich klipy importuje się na własny rig, nie na Humanoida R15.
- Eksport FBX ma przód w +Z — przy pierwszym imporcie sprawdzić, w którą stronę postać patrzy (możliwy obrót o 180°). GLB zachowuje przód.
- Klipy przesuwają kości (unik, wypad, upadek, zarodniki, kula kwasu), nie tylko je obracają — import musi przenosić pozycję. Kanału skali nie ma w żadnym klipie.
- Upadek kończy się leżeniem albo rozsypaniem — odtwarzacz ma zatrzymać ostatnią klatkę, bez powrotu do spoczynku.
- Leśny Slime: galareta jest skórowana na dwóch kościach — najpierw sprawdzić, czy importer Roblox zachowa wagi.
- Świecenie (oczy wilka, kryształ strażnika, zarodniki, kwas) jest tylko w teksturze emisji — w Studio trzeba dać Neon albo światło. Czarny obrys jest tylko w renderach z Blendera.
- Efekty do dorobienia w grze: lecąca strzała i smuga trucizny, fala uderzenia maczugi, chmura zarodników, rozprysk kwasu.
- Nazwa strażnika biomu jest od 15.11.2026 jedna — „Strażnik Gaju” — w modelu, notatce, silniku walki i prototypie (identyfikator w danych został `straznik_lasu`).

## Import modeli lasu (15.11.2026)
Wgrywał Claude Code na konto Karola (zalogowane w Studio), narzędziem `swiat/postacie/roblox_import_lasu.py` według listy kroków w `swiat/postacie/IMPORT_LASU.md`. Wynik: `swiat/postacie/wynik/_roblox/import_lasu.txt`. Modele stoją w `Workspace/TestPostaci`.

| Model | Zasób | Kiedy | Szkielet po imporcie | Werdykt |
|---|---|---|---|---|
| [[Zwiadowca]] | 108959205720843 | 15.11.2026, 19:15 | R15 (`Humanoid`, 15 stawów `AnimationConstraint`, 18 zaczepów) | ZGODNY w danych; na zrzucie kształt i przód dobre, ale szary (niżej) |
| [[Leśny Troll]] | 105984421059465 | 15.11.2026, 19:24 | kości (`Bone` 17 + `AnimationController`), drzewo kości jak w GLB | NIEZGODNY — błąd kontroli, nie modelu (niżej) |

Pozostałe cztery modele (Wilk, Muchomornik, Strażnik Gaju, Slime) nie zostały wgrane: lista każe stanąć po Trollu, a Troll nie dostał werdyktu „zgodny”. Sonda skóry slime'a też czeka.

Co ustalono:
- **Szaro w Studio.** Oba modele, a teraz także Rycerz z 13.11, rysują się w Studio szaro. Tekstura-paleta jest na miejscu i zatwierdzona przez moderację. Ta sama tekstura podana jako `TextureID` na próbnej kopii głowy rysuje się w kolorach, a `SurfaceAppearance` (także nowo utworzony) — szaro. Wniosek: w tej sesji Studio nie rysuje `SurfaceAppearance`; danych modelu to nie dotyczy. Przyczyny nie ustalono.
- **Troll: kontrola liczy niewidzialny `RootPart`.** Import dodał część `RootPart` (1,82 studa), której środek jest na wysokości stóp, więc wystaje pod model. Wzrost z nią wyszedł 10,94 zamiast 9,94, a naprawa zmniejszyła trolla do ×0,909 i postawiła na ziemi `RootPart` zamiast stóp. Siatki mają naprawdę skalę 1:1, a obrys w układzie modelu jest dokładnie jak w pliku (12,71 × 6,23). Teraz troll jest o 9% za mały i wisi ok. 0,9 studa nad brukiem. Poprawka należy do `roblox_import.py` (kontrola i naprawa mają pomijać `RootPart`).
- **Czego import nie przeniósł:** świecenia (tylko w teksturze emisji; Zwiadowca i Troll go nie mają), broni trzymanej osobno (łuk i sztylet Zwiadowcy są poza plikiem; maczuga trolla jest kością modelu i przyszła), znaczników zaczepów `_Att` (zamieniły się w zaczepy albo zniknęły zgodnie z oczekiwaniem), skóry (nie dotyczy tych dwóch modeli; sprawdzian jest przy slimie).
- Animacje na zaimportowanych rigach to osobny krok; prototyp walki nadal używa modeli z klocków.

**Kolory po imporcie (ustalone 15.11 wieczorem).** Zaimportowane modele były szare, bo importer dokłada każdej części SurfaceAppearance z błędnym odwołaniem emisji (`rbxassetid://5`) i Studio nie składa paczki tekstur. Pomaga ustawienie mapy koloru jako `TextureID` części i usunięcie SurfaceAppearance — robi to `python -B swiat/postacie/roblox_import_kolory.py` (uruchamiać po każdym imporcie). Zwiadowca, Leśny Troll i Rycerz z 13.11 mają po tej poprawce właściwe kolory.

## Ciało bazowe i strój z przedmiotów (15.11.2026)
Propozycja — realizacja [[Rejestr decyzji|D-071]] dla [[Rycerz|Rycerza]], [[Kot-Mag|Kota-Maga]] i [[Zwiadowca|Zwiadowcy]]. Pełny opis i umowa dla kodu: `swiat/postacie/EKWIPUNEK.md`.
- **Goły model + przedmioty.** Każdy bohater ma ciało bazowe (człowiek w lnianej koszuli i krótkich spodenkach, kot w futrze), a dzisiejszy wygląd to komplet przedmiotów. Przedmiot z kilku kości (zbroja, rękawice, buty) dzieli się na sztywne kawałki, po jednym na kość; broń, tarcza i kapelusz kota wiszą na punktach zaczepienia.
- **Powłoka zastępuje ciało.** Zbroja, szata, spodnie, rękawice i buty chowają gołe bryły swojej kości (na jednej kości najwyżej jedna powłoka); hełm i kaptur chowają włosy. Pas, poły i peleryna leżą nad ciałem.
- **Ruch wspólny dla każdego stroju.** Klipy liczy się raz, na pełnym stroju (u Rycerza z tarczą), i kopiuje bez zmian — tak jak w grze: jedna animacja na klasę.
- **Zgodność wstecz.** Funkcja `zbuduj()` każdego bohatera daje ten sam model w pełnym stroju co przedtem (te same kości, punkty zaczepienia i klipy); jedyna zmiana: Rycerz bez założonej tarczy. Rycerz i Zwiadowca mają to samo ciało, więc ich przedmioty pasują na obu; broń w dłoni pasuje do każdego ciała.

W grze i w walce ubieranie jeszcze nie działa — to następny krok (Studio i prototyp walki).

## Kontrola jakości kodu (13.11.2026)
Niezależny przegląd dzisiejszego kodu znalazł dziewięć usterek w ścieżkach błędów (m.in. możliwość dwukrotnego wgrania zasobu przy ponownym uruchomieniu, postać zostająca w pozie po nieudanym zrzucie, brak kodu błędu przy odmowie). Wszystkie poprawiono; każdą grupę poprawek sprawdził osobny, wrogo nastawiony weryfikator, a potem przeszły próby w Studio (odmowy, usuwanie i odbudowa kontenera, powrót do spoczynku po błędzie, prawdziwe klawisze). Osobna kontrola twierdzeń poprawiła osiem nieścisłości w opisach.

## Czego nie sprawdzono
- Importu siatek dla postaci innych niż Rycerz oraz animacji i broni na zaimportowanej postaci (zob. wyżej).
- Wydajności na telefonie.
- Postaci jako awatara gracza i chodzącego NPC (dziś to zakotwiczone figury bez `Humanoid`).
- Sloty ekwipunku: 41 przedmiotów katalogu ma te same nazwy slotów i zakładek plecaka co moduł przedmiotów w kodzie gry (stan z 13.11.2026: Helmet, Chest, Gloves, Boots, Amulet, Belt, Ring, Trinket, Weapon; Weapons, Armor, Amulets, Others). Poza kodem gry jest tylko slot „druga ręka” (tarcza, księga), a tors bywa złożony z kilku części modelu. Gotowa tabela w formacie kodu gry leży jako propozycja w `swiat/postacie/roblox/PrzedmiotyPropozycja.luau` (nigdzie niewczytywana). To propozycja, nie kanon ([[System RPG]], [[Pytania otwarte]] #24).

## Powiązane
[[Klocki — Blender i Roblox]] · [[Pipeline assetów]] · [[Panel zespołu]] · [[Rejestr decyzji]] D-029 · [[Pytania otwarte]] #24
