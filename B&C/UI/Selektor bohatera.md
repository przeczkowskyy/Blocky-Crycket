---
status: propozycja
tags: [ui, klasy, wybór]
źródło: "polecenie Pawła 2026-11-16 (ekran wyboru klasy po ekranie ładowania; zrzut z innej gry tylko jako wzór układu); klasy z D-054"
---
# Selektor bohatera (wybór klasy)

> [!info] W skrócie
> Po [[Ekran ładowania|ekranie ładowania]] gracz widzi ekran wyboru klasy: trzy modele 3D na podeście w ułożeniu kołowym, strzałkami przełącza między nimi, po lewej karta statystyk klasy, na dole PLAY. Dopiero po wyborze pokazuje się [[HUD]]. Klasy według D-054: **Wojownik, Zwiadowca, Mag**. To **propozycja układu** (polecenie Pawła 16.11).

## Opis
- **Scena 3D (Paweł, 16.11):** sala karczmy-zamku z klocków, a na środku okrągły kamienny podest ze złotą obwódką. Źródło: `swiat/wybor_klasy/generuj.py` → `czesci.json` + `efekty.json` (jak mapy Karola, [[Klocki — Blender i Roblox]]). W Studio: kontener `Workspace/WyborKlasy` (400 studów nad mapą, 4000 na południe; grupy trwałe przy streamingu).
- **Sala, wersja 2 (Paweł, 16.11 wieczorem: „wzbogać kreskę, dopracuj całość”, referencje wnętrza karczmy):** sala jest obrócona o 22° względem kamery, więc widać ją „w narożnik” — tylna ściana ucieka w lewo, prawa jest odsłonięta. Tylna ściana: wnęka z kamiennym łukiem i beczkami, potrójne okno z nocnym niebem i księżycem, chorągwie, pochodnie. Prawa ściana: kominek z gzymsem, tarczą i skrzyżowanymi mieczami, regał (eliksiry, słoje, kufle, chleb, ser, księgi, girlanda liści) i lada ze stołkami pod dwiema latarniami. Do tego niższy strop z więźbą, dwa żyrandole, dywan, a na pierwszym planie stół ze świecą. Zgodnie z zasadą zespołu bez liter i bez skojarzeń z alkoholem (beczki z jabłkami, eliksiry zamiast butelek). Około 1160 części.
- **Kreska:** mury z kamieni na ciemnej fudze, szersze podkładki tuszu pod belkami, tusz pod blatami, gzymsem i półkami, pęknięcia płyt podłogi, a do tego obrys sylwetki (Highlight) dla 17 grup sali i dla trzech bohaterów.
- **Światło i nastrój:** 18 świateł z `efekty.json` (model `Workspace/WyborKlasy/Efekty`): ognie z migotaniem, reflektor na bohaterów, chłodna kontra z okna, snop światła z pyłkami nad podestem. Na czas ekranu gracz ma **tylko u siebie** nocne światło (ciemne, fioletowe otoczenie, lekko obniżona ekspozycja, delikatna poświata) — wartości w `ClassData.Scene.mood`; po PLAY wraca oświetlenie miejsca. Oświetlenia miejsca (`Lighting`) w Studio nie zmieniano. Scena rozgrzewa światła już pod ekranem ładowania, żeby nie „zapalały się” na oczach gracza.
- **Ruch:** elementy 2D wjeżdżają po kolei (tabliczka z góry, karta z lewej, przyciski wyskakują), wybrany bohater lekko podskakuje przy zmianie klasy, kamera odrobinę podąża za myszką (`ClassData.Scene.parallax`).
- **Blender:** `python -B swiat/wybor_klasy/render.py --bohaterowie <eksport GLB> --wyj <folder>` — sala z tego samego pliku i trzej bohaterowie (GLB z narzędzia Karola, z bronią na zaczepach, poza z klipu idle) na kole; render z kamery gracza.
- **Modele 3D** na kole na podeście (kopie w `ReplicatedStorage/WyborKlasyModele`): Wojownik = „Rycerz Blocky” (z klocków), Zwiadowca = „Zwiadowca (import FBX)”, Mag = „Kot-Mag Crycket” (z klocków), wszystkie z `Workspace/TestPostaci` Karola (nieruszane). Wybrany z przodu, pozostali z tyłu: Zwiadowca po lewej, Mag po prawej.
- **Strzałki** (i klawisze ←→/A-D) obracają koło; strzałka w prawo przywołuje postać z prawej. Bez emblematów po prawej (Paweł, 16.11).
- **Warstwa 2D:** tabliczka z tytułem, karta statystyk po lewej (emblemat, nazwa, podtytuł, 6 pasków natywnych w proporcjach z [[Walka v2 — silnik, klasy i umiejętności]]), strzałki przy podeście, PLAY na dole.
- **Na czas wyboru widać tylko ten ekran** (Paweł, 16.11): inne okna gry, elementy Robloxa (czat, lista graczy, plecak, pasek u góry) i podpowiedzi „E” (ProximityPrompt, np. portal „Leć do lasu” przy spawnie) są schowane i wracają po PLAY.
- **PLAY** (albo Enter): serwer ustawia atrybut gracza `Class`, kamera wraca do postaci, HUD pokazuje się dopiero wtedy.
- Napisy natywnie, po angielsku.

## Grafiki
- Wygenerowane 16.11 w Higgsfield (Nano Banana 2.1, Glossy Ink, po 1 wariancie): arkusz 8 elementów (strzałki, PLAY, tabliczka, karta statystyk, 3 emblematy) i tło 2D. Tło 2D zastąpiła sala 3D (kafelki `CsBg1–4` odrzucone). Cięcie: `tools/classselect_assets.py`, GUI: `tools/classselect_build_gui.py`.
- Makieta: Figma, strona z HUD, ramka „ClassSelect” (node 35:115).

- **Tekstury sali (16.11):** paczka 16 tekstur Glossy Ink dla Karola — [[Tekstury sali wyboru klasy]].

- **Wybór rasy (Paweł 17.11, D-079):** po PLAY na wyborze klasy ta sama sala przechodzi w wybór rasy: znikają strzałki i pozostali bohaterowie, na podeście zostaje jeden goły model (kopia gołego modelu Karola z `Workspace/TestPostaci` jako `WyborKlasyModele.Base`; dopóki nie ma modeli ras, rasa zmienia kolor skóry), tytuł „CHOOSE YOUR RACE”, karta po lewej pokazuje wybraną klasę, a po prawej panel w tej samej ramce z nazwą rasy, cechą i siedmioma okrągłymi przyciskami: człowiek, demon, mroczny elf, elf, ork, goblin oraz Półbóg (premium, D-080 — zablokowany, serwer go nie przyjmie). Od 18.11 na podeście stoi figura wybranej rasy z wystawy Karola (`Workspace/RasyProba` → `WyborKlasyModele.Race_<Id>`, bazowy strój). PLAY → RemoteEvent `ChooseRace` → atrybut `Race`; HUD pokazuje się dopiero po rasie. Strzałki ←/→ przełączają rasy. Makieta: Figma, ramka „RaceSelect” (42:107). Kod: `src/shared/RaceData.luau`, `src/shared/RaceIcons.luau`, `ClassSelectClient`, `ClassSelect.server`, `tools/classselect_build_gui.py`, `tools/raceselect_assets.py`. Ikony ras: 1 generacja Higgsfield (arkusz 6) + emblemat Półboga. Cechy ras na przyciskach to propozycja opisu, bez liczb.

## Do ustalenia
- Czy wybór klasy jest raz na zawsze, czy można go zmienić (i za ile).
- Rasa z wcześniejszej wersji tej notatki (lewy panel z rasą) — na razie pominięta.
- Zapis wyboru w DataStore (dziś stan znika po wyjściu, jak reszta statystyk).

## Stan implementacji
- [x] Grafiki i makieta w Figmie (2026-11-16)
- [x] Scena 3D: generator, render w Blenderze z bohaterami, sala w Studio (2026-11-16)
- [x] Ekran w Roblox: kamera na podest, koło modeli, strzałki, karta statystyk, PLAY, ukrywanie innych okien; serwer `Class`; HUD po wyborze (2026-11-16, test Play OK)
- [x] Upload strzałek, PLAY i tabliczki tytułu po „tak” Pawła (2026-11-16; ID w manifeście), test Play OK
- [x] Tło karty statystyk i 3 emblematy klas przed nazwą klasy, wgrane na prośbę Pawła (2026-11-16), test Play: emblemat zmienia się z klasą
- [x] Sala wersja 2: bogatszy wystrój wg referencji karczmy, mocniejsza kreska (tusz + obrysy), nocne światło z migotaniem ogni, snop światła z pyłkami, animacje wejścia; po uwadze Pawła obniżona ekspozycja (2026-11-16, test Play: strzałki, PLAY → `Class`, światło gry wraca, HUD)
- [x] Karta statystyk 17.11 (Paweł): ramka `CsStatsFrame` (wgrana 17.11) z półprzezroczystym ciemnym tłem pod spodem (60% krycia — sama ramka była nieczytelna na scenie), kolor klasy na pasach i nazwie (Wojownik niebieski, Zwiadowca zielony, Mag fioletowy), nowy profil pasków: Wojownik STR/CON/ARMOR, Zwiadowca DEX + LUCK (mniej CON i STR niż Wojownik), Mag INT + LUCK (najmniej CON, STR, ARMOR). To opis na ekranie, nie liczby silnika walki
- [x] Broń startowa w dłoni figury rasy (Paweł 18.11): na ekranie rasy figura unosi prawe przedramię i trzyma broń wybranej klasy — Wojownik kij z kamieniem, Zwiadowca procę, Mag kostur spiralny (modele z Blendera: `swiat/postacie/bronie_startowe.py`, w grze z części Roblox jako `WyborKlasyModele.Weapon_<klasa>`; `holdWeapon` w `ClassSelectClient`). Test Play 18.11: Wojownik z kijem, Mag z kosturem, po zmianie rasy na orka broń zostaje w dłoni. Propozycja wyglądu, nie kanon
- [ ] Zwiadowca to siatka z konta Karola — w opublikowanej grze zasób musi być udostępniony grze (D-044)
- [ ] Zapis klasy w DataStore; animacje idle na modelach

## Powiązane
[[Rycerz]] · [[Kot-Mag]] · [[Zwiadowca]] · [[System RPG]] · [[Ekran ładowania]] · [[HUD]] · [[00 Start]]
