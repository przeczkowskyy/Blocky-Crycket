# Postacie, pety i ekwipunek (Blender, proceduralnie)

> **Status: propozycja, nie kanon.** Wygląd, sloty, kategorie i podział przedmiotów czekają na akceptację Game Directora.
> **W Roblox Studio sprawdzona jest ścieżka „z klocków”** (13.11.2026): wszystkie sześć postaci stoi w Studio zbudowane z części Roblox ze stawami i klipami, bez wgrywania czegokolwiek na konto — rozdział „Postacie z klocków w Roblox Studio”. **Import siatek (FBX/GLB) nadal nie jest sprawdzony**: pierwsza próba wgrania zatrzymała się na ustawieniu Studio (folder z plikami musi być zatwierdzony przez człowieka), więc rozdział „Import do Roblox Studio” to wciąż instrukcja nieprzetestowana.

Wszystko powstało skryptami Pythona w Blenderze 5.0 uruchamianym w tle, bez płatnych generatorów i cudzych modeli. Styl wzorowany na `assets/processed/KeyArt.png` i notatkach `B&C/Postacie/*.md`, `B&C/Gra/Pety.md`, `B&C/Styl/*.md`.

## Co tu jest

| Co | Pliki | Zawartość |
|---|---|---|
| **Prezentacja** | `wynik/_zestawienie/` | `postacie_w_skali.jpg` i `postacie_w_skali_obrys.jpg` (wszyscy w jednej skali obok szarego manekina gracza R15, 5,25 studa), `pokaz_animacji.mp4` (ok. 25 s, wszystkie klipy po kolei) i `pokaz_animacji_klatki.jpg`, `katalog_ekwipunku.jpg` (ikony w slotach i 3 przymiarki), `przymiarki_zestawow.jpg` |
| **Postacie** | `rycerz.py`, `kot_mag.py`, `karczmarz.py` → `wynik/<id>/` | Rycerz (idle, chod, atak_miecz, wiwat), Kot-Mag (idle, chod, czar, wiwat), Karczmarz (idle, zaproszenie, smiech). Rekwizyty (miecz, kapelusz i kostur, chochla) są osobnymi przedmiotami |
| **Pety** | `pies.py`, `slime.py`, `smok.py` → `wynik/<id>/` | Pies (idle, bieg, szczek), Slime (idle, skok, atak), Smok (idle_lot, lot, zioniecie) |
| **Zestawy ekwipunku** | `zestaw_rekrut.py`, `zestaw_rycerz.py`, `zestaw_mag.py` → `wynik/zestaw_*/` | Rekrut (start), Rycerz, Mag: hełm, tors, rękawice, buty, pas, broń, druga ręka, amulet, pierścień, talizman |
| **Zbrojownia** | `bronie.py` → `wynik/bronie/` | 8 broni do prawej dłoni (od pałki do chochli mistrza) |
| **Lista przedmiotów** | `przedmioty.json` | id, nazwa, slot, kategoria plecaka, zestaw, pliki, części (każda z punktem zaczepienia i gotowym ustawieniem `attachment`), plik ikony. Bez statystyk |
| **Postacie z klocków w Studio** | `roblox_postac.py`, `roblox_klatki.py`, `roblox/`, `wynik/_roblox/` | budowa rigów z części Roblox bez uploadu, arkusze klatek ze Studio, skrypt pokazu, zrzuty i dane rigów (`<id>_klocki.json`) |
| **Próba importu siatek** | `roblox_import.py`, `biblioteka/test_roblox_import.py` | wgranie FBX/GLB przez Studio (tylko z opcją `--tak-wgraj`, z ochroną przed podwójnym wgraniem), wstawienie, kontrola, naprawa skali, zrzuty; test logiki bez Studio — prawdziwego wgrania jeszcze nie było |
| **Kontrole w Studio** | `roblox_klipy.py`, `roblox_skladnia.py`, `biblioteka/test_roblox_klocki.py` | wszystkie klipy: dane kontra Animator; kompilacja skryptów i szablonów Luau; rozkład brył i zamiana układu (bez Studio) |
| **Skrypt do Studio** | `zaczepy_akcesoriow.luau` | tworzy Attachmenty w Handle zaimportowanych części według `przedmioty.json` (wygenerowany, nie testowany) |
| **Narzędzia** | `przebuduj.py`, `zestawienie.py` | przebudowa modułu do `wynik/<moduł>/`; prezentacja całości i `przedmioty.json` |
| **Biblioteka** | `biblioteka/` | kod wspólny; opis API, konwencji i faktów Roblox w `biblioteka/README.md` |
| **Wzory** | `wzor_postaci.py`, `wzor_ekwipunku.py` | najprostsze przykłady do kopiowania |

## Układ `wynik/<moduł>/` (jeden dla wszystkich)

| Plik | Co to |
|---|---|
| `<model>.fbx`, `<model>__<klip>.fbx`, `<model>.glb`, `<model>.blend`, `<model>_tekstury/` | model z kośćmi: postać, pet albo przymiarka zestawu (`<moduł>_przymiarka`, szary manekin R15 z założonym kompletem). FBX bez animacji + jeden FBX na klip (tak chce Roblox); GLB ze wszystkimi klipami |
| `<model>_plansza.jpg`, `<model>_bohater.jpg`, `<model>_ikona.png` | plansza (3/4, przód z manekinem skali, bok, tył), kadr bohaterski, ikona 512 px (dla postaci: popiersie) |
| `<model>_<klip>.mp4`, `_klatki.jpg`, `_z_filmu.jpg` | film klipu (pętla ×3), 8 klatek z renderu, 8 klatek odczytanych z gotowego MP4. Wszystkie klipy modelu mają jeden wspólny kadr |
| `przedmioty/<id>.fbx`, `.glb`, `<id>_tekstury/` | każdy przedmiot (akcesorium) osobno; tekstury-palety: kolor, metal, szorstkość, emisja |
| `ikony/<id>_ikona.png`, `<moduł>_ikony_arkusz.jpg` | ikony przedmiotów i ich arkusz |
| `raport.json`, `raport.txt` | dane z Blendera (trójkąty, wymiary w studach, kości, klipy, zaczepy, ostrzeżenia, kontrola eksportów) i to samo dla człowieka, z listą znanych słabości modułu (`SLABOSCI`) |

Sufiksy stron w nazwach są małymi literami: `_l` = lewy, `_p` = prawy (lewa strona postaci to +X).

## Jak obejrzeć
- **Najszybciej:** pliki z `wynik/_zestawienie/` (obrazy i film).
- **Pojedyncza postać:** `wynik/<id>/<id>_plansza.jpg` i filmy `<id>_<klip>.mp4`.
- **Model 3D bez Blendera:** `<id>.glb` otwiera się w przeglądarce 3D systemu Windows albo na stronie typu glTF Viewer (przeciągnij plik). W GLB są wszystkie klipy.
- **W Blenderze:** `<id>.blend`, klipy są akcjami szkieletu (Dope Sheet → Action Editor).

## Jak przebudować
Z głównego folderu repozytorium. Potrzebny Blender 5.0 (szukany w `C:\Program Files\Blender Foundation\`, albo zmienna `BLENDER_EXE`), ffmpeg w PATH i Pillow. Blender działa pod wspólną blokadą, więc kilka osób może puszczać polecenia jednocześnie.

```
# jeden albo kilka modułów do wynik/<moduł>/ (czyści folder i układa pliki według wzoru wyżej)
python -B swiat/postacie/przebuduj.py rycerz
python -B swiat/postacie/przebuduj.py zestaw_mag zestaw_rycerz --bez-filmow

# rendery próbne jednego modelu do folderu POZA repozytorium (--klip = film, --eksport = FBX/GLB/.blend + kontrola)
python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rycerz.py --wyj <folder> --klip chod --eksport

# prezentacja całości (wynik/_zestawienie/, przedmioty.json, zaczepy_akcesoriow.luau), ok. 3 min
python -B swiat/postacie/zestawienie.py
python -B swiat/postacie/zestawienie.py --tylko json            # tylko lista przedmiotów i skrypt Luau, bez Blendera
python -B swiat/postacie/zestawienie.py --tylko skala,katalog   # wybrane części: skala, film, katalog, json
```

Źródłem prawdy jest kod `.py`, a nie `.blend`. Zmiany rób w module i przebuduj go (`przebuduj.py`), potem odśwież zestawienie. `przebuduj.py` zamienia w FBX bezwzględne ścieżki tekstur na względne (tekstury i tak są osadzone w pliku) i sprawdza, czy w plikach nie została ścieżka z dysku autora.

## Postacie z klocków w Roblox Studio (bez wgrywania) — sprawdzone 13.11.2026
Te same dane, z których Blender robi siatki, da się zamienić na zwykłe części Roblox. Nic nie trafia na konto Roblox, nie ma moderacji ani czekania, a wynik widać od razu we wspólnym miejscu Team Create.

```
python -B swiat/postacie/roblox_postac.py                      # zbuduj wszystkie postacie w Workspace/TestPostaci
python -B swiat/postacie/roblox_postac.py --tylko rycerz,pies  # wybrane
python -B swiat/postacie/roblox_postac.py --sucho              # tylko policz, bez Studio
python -B swiat/postacie/roblox_postac.py --usun               # usuń własne kontenery TestPostaci (zrób to przed publikacją gry)
python -B swiat/postacie/roblox_klatki.py --model "Rycerz Blocky" --klip atak_miecz --wyj <folder>   # arkusz klatek ze Studio
python -B swiat/postacie/roblox_klipy.py --zapisz              # kontrola wszystkich klipów: dane kontra Animator w Studio
python -B swiat/postacie/roblox_skladnia.py                    # kompilacja wszystkich skryptów i szablonów Luau w Studio (nic nie wykonuje)
```

**Bezpieczeństwo we wspólnym miejscu:** każdy kod wysyłany do Studio najpierw sprawdza, czy to miejsce gry (PlaceId) i czy kontener ma atrybut `Wygenerowane`. Każda odmowa („STOP”: inne miejsce, cudzy obiekt o nazwie `TestPostaci`, dwa kontenery naraz, brak modelu) przerywa przebieg z kodem błędu 1 i komunikatem „PRZERWANO — Studio odmówiło”. `--usun` usuwa wszystkie własne kontenery, a cudzy obiekt o tej nazwie zostawia i zgłasza. Przy dwóch kontenerach (np. budowa z dwóch komputerów naraz) pomaga `--usun` i ponowna budowa — cała budowa trwa kilka sekund. Przed budową biblioteka uruchamia `Postac.sprawdz()`: błędy zatrzymują przebieg, uwagi się wypisują; bryła albo akcesorium na kości bez części Roblox (korzeń) to błąd, a kanały klipów i zaczepy na takich kościach trafiają do uwag. Sprawdzone 13.11.2026 w Studio na własnych pustych folderach testowych.

**Co powstaje** (tylko we własnym kontenerze `Workspace/TestPostaci` z atrybutem `Wygenerowane`):
- `Model` na postać: zakotwiczony `HumanoidRootPart`, niewidzialna część na każdą kość (nazwy R15), stawy `Motor6D` w miejscach stawów szkieletu, bryły przyspawane do kości (`WeldConstraint`), `Attachment`y o standardowych nazwach i orientacjach Roblox (np. `RightGripAttachment` = −90° w X), `AnimationController` z `Animator`.
- `AnimSaves` z klipami jako `KeyframeSequence` (klatka na każdą klatkę klipu, próbki z tych samych krzywych Blendera co filmy). Klipy otwierają się w Animation Editorze.
- Skrypt `PokazAnimacji` (źródło: `roblox/PokazAnimacji.server.luau`): po naciśnięciu Play albo Run każda postać odtwarza po kolei swoje klipy. Działa wyłącznie w Studio.

| Postać | Bryły → części Roblox | Kości | Klipy |
|---|---|---|---|
| Rycerz Blocky (z mieczem) | 112 → 113 | 15 | idle, chod, atak_miecz, wiwat |
| Karczmarz (z chochlą) | 90 → 98 | 15 | idle, zaproszenie, smiech |
| Kot-Mag Crycket (kapelusz, kostur) | 110 → 166 | 17 | idle, chod, czar, wiwat |
| Pies | 59 → 59 | 14 | idle, bieg, szczek |
| Slime | 35 → 42 | 12 | idle, skok, atak |
| Smok | 91 → 180 | 15 | idle_lot, lot, zioniecie |
| Manekin Rekrut (10 części zestawu) | 197 | 15 | spoczynek, chod, atak, trzymanie |
| Manekin Rycerz (14 części zestawu) | 240 | 15 | spoczynek, chod, atak, trzymanie |
| Manekin Mag (15 części zestawu) | 544 | 15 | spoczynek, chod, atak, trzymanie |

Sześć postaci to razem 658 widocznych części i 20 klipów; z trzema manekinami w kontenerze jest 1781 części. Postacie stoją na rynku Krzywego Miasteczka wokół punktu startu („komitet powitalny”), w słońcu, twarzami do płyty startu: Blocky, Karczmarz, Crycket i pies przed graczem, slime i smok po jego prawej ręce (trzeba się obrócić).

**Przymierzalnia zestawów** (`roblox/Przymierzalnia.server.luau`, tylko w Studio): przy każdym manekinie pojawia się w grze podpowiedź „Przymierz” (klawisz E albo dotknięcie). Zestaw trafia na awatar gracza jako zwykłe obiekty `Accessory` zbudowane z części Roblox i zakładane przez `Humanoid:AddAccessory` na standardowe punkty zaczepienia awatara (`HatAttachment`, `NeckAttachment`, `RightGripAttachment`…). Ponowne naciśnięcie zdejmuje zestaw. Dane części: `wynik/_roblox/ekwipunek_klocki.json`. Dane części zawsze obejmują wszystkie trzy zestawy, także gdy przebudowujesz jeden (`--tylko`), a przymierzalnia instaluje się na nowo przy każdym przebiegu bez `--bez-pokazu`. Manekiny stoją co 9 studów, a podpowiedź ma zasięg 8, żeby przy jednym nie łapał się sąsiad.

**Pety idące za graczem** (`roblox/PetyTestowe.server.luau`, tylko w Studio): przy psie, slimie i smoku pojawia się w grze podpowiedź „Weź peta” (klawisz E). Pet rusza za graczem: w marszu odtwarza klip ruchu (bieg, skok, lot), w miejscu spoczynek; klawisz R („Odeślij”) odsyła go na miejsce. Ruch liczy serwer co klatkę, przesuwając zakotwiczony korzeń postaci. To próba zachowania, nie system petów: bez omijania przeszkód, bez zapisu i bez limitu petów. Pety są szybsze od domyślnej prędkości gracza (pies 20, slime 17, smok 22 studów/s wobec 16), więc w długim marszu nie zostają w tyle.

**Co sprawdzono w Studio:**
- Wygląd z czterech stron każdej postaci i ujęcia grupowe (`wynik/_roblox/*_spoczynek_studio.jpg`, `studio_grupa*.jpg`). Strony się nie odbijają lustrzanie: miecz jest w prawej dłoni.
- Rozkład brył liczbowo: `python -B swiat/postacie/biblioteka/test_roblox_klocki.py` porównuje punkt po punkcie 400 losowych ostrosłupów z sumą części Roblox (0% punktów niezgodnych) i sprawdza zamianę układu (pozy co do 1e-15; obroty brył co do 0,15° przy kątach bliskich ±90°, co wynika z progu w bibliotece) oraz to, że nic nie znika po cichu na kościach bez części Roblox. Kierunek skosu `WedgePart` i wierzchołka `CornerWedgePart` potwierdzony promieniami w samym Studio.
- Animacje w trybie Edit przez prawdziwy `Animator` (`RegisterKeyframeSequence` → `LoadAnimation` → `StepAnimations`): **wszystkie 32 klipy** (20 klipów sześciu postaci i 12 klipów manekinów) sprawdzone narzędziem `roblox_klipy.py` — w pięciu klatkach każdego klipu każdy animowany staw ma w Studio tę samą pozę co w danych z Blendera (1431 porównań staw × klatka, największa odchyłka 0,04° i 0,0001 studa; wynik w `wynik/_roblox/klipy_kontrola.txt`). Do obejrzenia są arkusze klatek ośmiu klipów (`wynik/_roblox/*_studio.jpg`): po jednym każdej postaci, Rycerz trzy.
- Animacje w trybie Play w Studio: po stronie serwera wszystkie sześć postaci odtwarza kolejne klipy, konsola bez błędów (`wynik/_roblox/play_grupa_8_klatek.jpg`, obok stoi zwykły awatar gracza dla skali).

- Przymierzalnia w trybie Play w Studio: zestawy Rekrut (10 akcesoriów, 175 części), Rycerz (14, 223) i Mag (15, 527) założone po kolei na prawdziwy awatar R15 i zdjęte; wszystkie części trzymają się awatara, konsola bez błędów (`wynik/_roblox/play_awatar_w_zestawach_*.jpg`).

- Pety w trybie Play w Studio: po zawołaniu pies, slime i smok dochodzą do gracza (4–6 studów). W marszu przez rynek (ok. 36 studów) pies trzyma się 4–5 studów za graczem, smok 6–7, slime 6–8; po zatrzymaniu wracają do spoczynku, a odesłane wracają na miejsce i oddają sterowanie pokazowi animacji. Odległości pochodzą z odczytów po stronie serwera w trakcie marszu; zdjęcie `wynik/_roblox/play_pety_ida_za_graczem.jpg` jest z wcześniejszego, krótszego przejścia (sprzed przyspieszenia petów).

- Droga człowieka w trybie Play w Studio, z prawdziwym naciśnięciem klawisza: E przy manekinie Rycerza, Maga i Rekruta zakłada właściwy zestaw (także gdy za graczem idą dwa pety), E przy psie i smoku zabiera peta, R odsyła najbliższego idącego peta. Pierwsza wersja miała tu usterkę: manekiny stały co 6 studów przy zasięgu podpowiedzi 12, więc E zakładało zestaw sąsiada, a idący pet przechwytywał E. Poprawione: manekiny co 9 studów, zasięg 8, odsyłanie na osobnym klawiszu.

**Pułapka spawania akcesoriów (sprawdzona 13.11.2026):** części akcesorium trzeba łączyć z uchwytem obiektem `Weld` z jawnym przesunięciem (`C0`). `WeldConstraint` zapamiętuje wzajemne położenie dopiero po wejściu do świata, czyli już po tym, jak `AddAccessory` przeniesie uchwyt na awatar, i części zostają tam, gdzie powstały.

**Pułapka trybu Edit (sprawdzona 13.11.2026):** zatrzymanie ścieżki animacji ani wpisanie `Motor6D.Transform` nie cofa części — postać zostaje w ostatniej pozie, a staw, którego kolejny klip nie animuje, niesie pozę z poprzedniego. `roblox_klatki.py` odtwarza więc pod każdym klipem klip neutralny (wszystkie stawy w zerze), po zrzutach wraca nim do spoczynku i mierzy, czy części naprawdę wróciły. Sam powrót: `python -B swiat/postacie/roblox_klatki.py --model "<Nazwa>" --tylko-reset`. W uruchomionej grze tego problemu nie ma. Powrót do spoczynku idzie także po błędzie i po przerwaniu (Ctrl+C); gdy się nie uda albo pomiar go nie potwierdzi, narzędzie podaje polecenie naprawcze i kończy się kodem błędu. Kąt `--katy` liczy się od przodu postaci w stronę jej PRAWEJ ręki (90 = prawy bok, 270 = lewy bok). Tak jak budowa, narzędzie dotyka tylko miejsca gry i kontenera z atrybutem `Wygenerowane`.

**Czego klocki nie oddają i czego nie sprawdzono:**
- Krawędzie są ostre (bez fazowania), stożki są schodkowe, komiksowego obrysu nie ma (można go dać obiektem `Highlight`).
- Slime nie zgniata się naprawdę: jego ścianki przesuwają się osobno, bo części Roblox nie mają skórowania. Świecenie i półprzezroczystość nie są dopracowane.
- Zestawy są dopasowane do klockowego awatara R15 w standardowej skali. Włosy awatara przebijają przez czapki, buty obejmują stopy pudełkiem, a na innych ciałach (Rthro) części będą odstawać. Zestaw Maga ma 527 części na jednym graczu — za dużo do prawdziwej gry bez uproszczenia.
- Ostrosłup, którego góra wystaje poza podstawę (zawinięty szpic kapelusza, mankiet), jest w klockach uproszczony do zwykłego klocka. Dotyczy to sześciu brył zestawu Maga (części o nazwach „Szpic” i „Zawijas”) oraz czterech mankietów zestawu Rycerza.
- Postacie są zakotwiczonymi figurami bez `Humanoid` i bez kolizji. To nie jest jeszcze postać gracza ani chodzący NPC.
- Wydajności na telefonie nie mierzono (658 części to mało, ale liczba jest do sprawdzenia przy większej obsadzie).
- Klipy leżą w miejscu jako obiekty: 32 `KeyframeSequence` to razem ok. 12,8 tys. obiektów `Pose`, które w Play trafiają też do każdego klienta. Do próby to wystarcza; w prawdziwej grze animacje są zasobami i tego kosztu nie ma.
- **Klipy grają tylko w Studio.** W opublikowanej grze animacja musi być zasobem Animation. Publikuje się ją z Animation Editora i według dokumentacji Roblox musi należeć do właściciela gry (osoby albo grupy). To decyzja i czynność właściciela.
- Skrypty `PokazAnimacji`, `Przymierzalnia` i `PetyTestowe` oraz cały kontener `TestPostaci` trzeba usunąć przed publikacją (`--usun`).

## Import do Roblox Studio — krok po kroku
> **Nie testowane.** Każdy krok importu wgrywa zasoby na konto Roblox. 13.11.2026 właściciel konta zgodził się na próbę, ale wgranie przez Studio (Open Cloud) wymaga jeszcze zatwierdzenia folderu z plikami: Assistant → Settings → MCP Permissions → approved upload directories → folder `swiat/postacie/wynik`. Zasoby wgrane na konto współpracownika trzeba potem udostępnić grze właściciela (Creator Dashboard → uprawnienia zasobu).

**0. Próba z terminala (przygotowana, czeka na zgodę w Studio)**
```
python -B swiat/postacie/roblox_import.py --modul rycerz               # plan: co i na czyje konto by poszło (nic nie wysyła)
python -B swiat/postacie/roblox_import.py --modul rycerz --tak-wgraj   # wgraj, wstaw, sprawdź, napraw skalę, zrób zrzuty
```
Skrypt wgrywa plik przez Studio na konto osoby zalogowanej w Studio (zasób jest trwały), wstawia model do `Workspace/TestPostaci`, liczy siatki, kości, stawy i zaczepy, sprawdza tekstury, mierzy wzrost i poprawia skalę, kotwiczy części, stawia model obok wersji z klocków i robi dwa zrzuty. Wynik: `wynik/_roblox/import_<moduł>_<format>.json`.

**Ochrona przed podwójnym wgraniem.** Zanim cokolwiek wyśle, skrypt zapisuje plik stanu `wynik/_roblox/wgranie_<moduł>_<format>.json` (etapy: wysyłanie, operacja, zasób i stan moderacji). Ponowne uruchomienie tego samego polecenia z `--tak-wgraj` NIE wgrywa drugi raz: czeka na zapisaną operację albo od razu wstawia znany zasób. Gdy nie wiadomo, czy zasób powstał (przerwane połączenie, nieczytelna odpowiedź), skrypt staje i każe sprawdzić Creator Dashboard; znaleziony zasób wstawia się wtedy przez `--asset <numer>`, nigdy przez ponowne `--tak-wgraj`. Świadome drugie wgranie (kolejny trwały zasób, np. po przebudowaniu pliku) wymaga osobnej opcji `--nowy-zasob-mimo-poprzedniego`. Plik stanu zostaje tylko na tym komputerze (jest poza gitem, bo zawiera numer konta), więc chroni przed powtórką z tego samego komputera.

**Moderacja i nazwy.** Gdy zasób czeka na moderację, skrypt czeka do ok. 5 minut i staje; numer zasobu zostaje w pliku stanu i to samo polecenie później go wstawi. Każdy import dostaje w `Workspace/TestPostaci` nazwę, której tam jeszcze nie ma („… (import FBX)”, potem „… #2”); starszych importów skrypt nie usuwa, a kontrola i naprawa dotyczą nowego modelu. Uwaga: każde kolejne uruchomienie po udanym wgraniu wstawia jeszcze jedną kopię w tym samym miejscu — starą trzeba usunąć ręcznie.

**Stan na 13.11.2026:** w Studio sprawdzone są plan, kontrola (na modelu z klocków — wzrost 5,71 studa zgodny z raportem) i reakcja na niezatwierdzony folder. Logikę wgrywania sprawdza bez Studio test `biblioteka/test_roblox_import.py` (12 scenariuszy na udawanym Studio: przerwane wysyłanie, wznowienie, moderacja, duplikaty nazw). Prawdziwego wgrania jeszcze nie było, więc pierwszy import trzeba obejrzeć krok po kroku — nieznane są m.in. dokładne napisy stanu moderacji i to, jak narzędzie nazywa wstawiony model.

**Znane drobne braki skryptu importu** (zgłoszone przez weryfikatora, zostawione świadomie):
- Dwa uruchomienia `--tak-wgraj` w odstępie kilku sekund (dwa terminale, dwóch agentów) mogą oba uznać, że nic jeszcze nie wgrano. Wgrywa jedna osoba z jednego terminala.
- Błąd przy odpytywaniu operacji albo moderacji (np. brak uprawnienia, wygasła operacja) wygląda jak „jeszcze nie gotowe”: skrypt czeka do limitu czasu i dopiero ostatnia wypisana odpowiedź pokazuje prawdziwy powód.
- Gdy operacja skończy się bez numeru zasobu, komunikat każe sprawdzić Creator Dashboard, ale nie przypomina, że znaleziony zasób wstawia się przez `--asset <numer>`.
- Skrypt nie wykrywa, że model z danego zasobu już stoi w kontenerze, więc ponowne uruchomienie dokłada kopię.

**1. Postać albo pet (model z kośćmi)**
1. Studio → zakładka *Home* lub *Avatar* → **Import 3D** → wybierz `wynik/<id>/<id>.fbx` (np. `rycerz.fbx`).
2. W oknie importu: **Scale Unit = Stud**, **World Forward = Front**, **World Up = Top**. Rycerz, Karczmarz i Kot-Mag mają kości R15 (Kot-Mag ma też ogon: Tail i TailTip, więc to rig NPC, a nie ciało awatara). Pety mają własne kości, nie R15; ciało slime'a jest skórowane na dwóch kościach (Dol, Gora).
3. Po imporcie sprawdź, w którą stronę patrzy model. Jeśli tyłem, obróć go o 180° albo zaimportuj ponownie z innym *World Forward*. Kierunek nie był sprawdzony.
4. Kolory są w teksturze-palecie (osadzonej w FBX). Jeśli siatka jest szara, ustaw `SurfaceAppearance.ColorMap` na `<id>_tekstury/<id>_kolor.png`. Metal i szorstkość podepnij z PNG o tych nazwach (są dla każdego modelu i każdego przedmiotu). Świecenie (kryształy, slime, płomień) zrób w grze: część Neon, `PointLight` albo `ParticleEmitter`.
5. Komiksowego obrysu nie ma w modelu (to tylko efekt renderu). W grze może go dać obiekt `Highlight`.
6. Rekwizyty postaci (miecz Rycerza, kapelusz i kostur Kota-Maga, chochla Karczmarza) są w `wynik/<id>/przedmioty/` — w FBX postaci ich nie ma. Dołóż je jak akcesoria (punkt 2) albo jako `Tool`.

**2. Akcesoria (hełm, napierśnik, buty…)**
1. **Import 3D** części (ścieżki w `przedmioty.json`, pole `czesci[].fbx` albo `.glb`). Powstaje MeshPart; zmień nazwę na `Handle`.
2. Wstaw `Accessory` o nazwie takiej jak id części (np. `zr_helm`) i włóż do niego `Handle`.
3. Attachment w `Handle`: zaznacz akcesoria i uruchom `zaczepy_akcesoriow.luau` (ustaw w nim `ZRODLO = "glb"` albo `"fbx"`, zależnie od importowanego pliku). Skrypt dodaje `Attachment` o nazwie zaczepu z pozycją i obrotem z `czesci[].attachment` w `przedmioty.json` (minus środek skrzynki siatki od punktu zaczepienia). Ręcznie: te same liczby wpisz w `Attachment.Position` i `Orientation`.
4. Przeciągnij akcesorium na postać (albo w skrypcie `Humanoid:AddAccessory(accessory)`). Przedmiot z kilkoma częściami (np. buty L/P, szata z rękawami, napierśnik z naramiennikami i połą) to kilka akcesoriów naraz.
5. Broń można też zrobić jako `Tool` z `Handle`: `Tool.Grip` ustaw tak, żeby punkt 0,0,0 modelu (środek dłoni) trafił w dłoń.

**3. Animacje**
1. Zaznacz zaimportowany model → *Avatar* → **Animation Editor**.
2. **⋯ → Import → From FBX Animation** (w dokumentacji i starszych wersjach Studio: *From File*) → wybierz `<id>__<klip>.fbx` (np. `rycerz__chod.fbx`).
3. Ustaw pętlę zgodnie z `raport.txt` (idle, chód, bieg, lot są zapętlone; atak, czar i zianie są jednorazowe) i priorytet (Idle, Movement, Action).
4. **Publish to Roblox** daje `AnimationId`. W grze: `Animator:LoadAnimation(animation):Play()`.
5. Klipy to szkice (ok. 1–2 s), nie gotowa animacja. Żaden klip nie ma kanału skali (Roblox przenosi pozycję i obrót kości): zgniatanie slime'a robi przesunięcie kości `Gora`, a nie skala.

## Ograniczenia (najważniejsze; pełne listy w `wynik/*/raport.txt`)
- **Siatki (FBX/GLB) nie były importowane do Roblox Studio** (postacie z klocków — tak, patrz wyżej). Nie sprawdziliśmy kierunku przodu po imporcie FBX, klipów na własnych kościach petów, wag skórowania slime'a ani skryptu `zaczepy_akcesoriow.luau`.
- **Pozycje kości R15.** LowerTorso i Root nie są w 0,0,0 (biodra na wysokości ok. 1,9 studa u Rycerza). Dla NPC to nie przeszkadza; ciało awatara może tego wymagać — sprawdzić przy pierwszym imporcie.
- **Obrys tylko w renderach.** W FBX/GLB go nie ma.
- **Jeden materiał na model.** Kolory są w teksturze-palecie. Nie ma prawdziwej przezroczystości (slime udaje szkło jasną skorupką i ciemniejszym rdzeniem), a świecenie trzeba dorobić w grze.
- **Bryły są sztywno przypięte do kości** (jedna siatka na kość, przenikają się przy dużych ruchach). Do NPC i petów to wystarcza, do sprzedaży ciała awatara na Marketplace nie (brak klatek, Kot-Mag ma ogon spoza R15 i ok. 3,7 studa wzrostu).
- **Akcesoria** dopasowane do klockowego R15 biblioteki (5,25 studa). Na innym ciele (Rthro) nie będą przylegać.
- **Ikony** to rendery 3D; kanon mówi o ikonach w pixel-arcie, więc ikony z renderu to osobna propozycja.
- **Sloty i kategorie** (Ring, Trinket, OffHand, podział Chest na części) to propozycja, a nie kanon gry.
- `przedmioty.json` nie ma statystyk ani cen. To tylko katalog plików.
