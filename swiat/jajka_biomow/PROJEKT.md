---
status: propozycja
---
# Jajka biomów — Bagno i Dżungla na wzór leśnego jaja Pawła

Zlecenie Karola z sesji 25.11.2026: wziąć leśne jajo Pawła (artefakt „Leśne jajo 3D”, zasób 92671202213818,
`tools/studio/jajo_lesne_ustaw.luau`, scenka `src/client/JajkoKoroweClient.client.luau`) jako wzór i zrobić takie same
jakościowo jajka do Bagna i Dżungli, z animacją spoczynku i wyklucia. **Propozycja** — nic tu nie jest kanonem;
stan etapu „Studio” z nocy 25/26.11 — w sekcji „Stan w Studio” niżej (modele jeszcze NIE w grze).

Całość jednym poleceniem (Blender 5.0 bez okna, jedna instancja naraz; ok. 30 s z teksturami):

    python -B swiat/jajka_biomow/zbuduj.py            # tekstury + modele + plansze
    python -B swiat/jajka_biomow/studio_skrypty.py    # skrypty ustawiające dla Studio

## Co jest w pakiecie

| Plik | Co |
|---|---|
| `ksztalt.py` | wspólny kształt jaja (te same wymiary dla obu biomów) i linie podziału skorupy — z nich i siatki, i tekstura |
| `atlas.py` | układ atlasu ozdób 1024 × 1024 i kształty liści (siatka i rysunek mają ten sam obrys) |
| `tekstury.py` | tekstury malowane skryptem (numpy + Pillow, bez generatorów) → `tekstury/` |
| `blender_jajko.py` | siatki, eksport GLB + FBX, rendery podglądu |
| `zbuduj.py` | wszystko po kolei + plansze `podglad/`; czyści ścieżki dysku w FBX |
| `studio_skrypty.py` → `studio/jajko_<biom>_ustaw.luau` | ustawienie modelu w Studio (wzór: `jajo_lesne_ustaw.luau`) — maski i miejsce wpisane 26.11, na modelach jeszcze nie uruchamiane |
| `wdroz.py` | wysyłka do Studio: `wgraj` (GLB → zasoby Model, prawo Use, manifest), `wstaw` (do kontenera + skrypty ustawiające), `skrypty` (animacja spoczynku), `wszystko`, `--sucho` |
| `studio/JajkaBiomowDane.luau` | dane animacji (spoczynek, wyklucie, reakcje ozdób) — docelowo `src/shared/` |
| `studio/JajkaBiomowSpoczynek.client.luau` | ruch w spoczynku i reakcja ozdób na finał — docelowo `src/client/` |
| `modele/jajko_<biom>.glb`, `.fbx`, `_statystyki.json` | modele do importu (tekstury koloru osadzone) i liczby |
| `podglad/*.jpg` | plansze: 4 strony każdego jajka, skorupa i rozpad, zestawienie w jednej skali; `scenka_*.jpg` — zrzuty scenki wyklucia z Play (26.11; Bagno i Dżungla na atrapach) |
| `testy/proba_play.py` | próba scenki w Play (leśne + każde jajko biomu, które stoi w kontenerze): karta, spoczynek, odmowa, zakup prawdziwym E, 5 kliknięć, rozpad, słup, pet, kolory, ozdoby, konsola; `--tylko-lesne`, `--bez-zrzutow` |

## Budowa (zgodna ze scenką Pawła)

Te same nazwy i układ co leśne jajo, więc klient Pawła obsłuży nowe jajka bez przepisywania scenki:

- **Egg** — całe jajo (2484 trójkąty), tekstura koloru 2048 × 1024 (UV jak u Pawła: U wokół, V z góry na dół),
  na nim w Studio `SurfaceAppearance` z maską blasku pęknięć (`EmissiveMaskContent`, `EmissiveTint`).
- **ShellBottom, ShellTopLeft, ShellTopRight** — kawałki skorupy z grubością 5 cm (wnętrze i krawędź pęknięcia mają
  własny pas tekstury: krawędź świeci). Złożone dają dokładnie bryłę Egg; dzielą ją zębate linie, które na teksturze
  są najjaśniejszymi pęknięciami. ShellTopRight leży po +X (odlatuje pierwszy, jak u Pawła), ShellTopLeft po −X.
  Z tyłu podział idzie prosto po szwie tekstury (tam jest tylko cienka ciemna kreska, bez blasku).
- **Korzeń** (tworzy go skrypt ustawiający): najniższy punkt modelu = Y 0 pliku, przód = +Z pliku.
  Rdzeń klienta (1,59 nad korzeniem) siedzi w dolnej skorupie, słup światła od 1,66 — jak w leśnym.
- Skala ×1,5 w Studio (1 m pliku = 1 stud). Jajo: 1,64 × 2,3 m pliku = 2,5 × 3,45 studa po skali.

Ozdoby — osobne siatki o czytelnych nazwach (kolory siatek bez tekstury ustawia skrypt, jak `KOLORY` u Pawła):

| Bagno | Dżungla |
|---|---|
| `MudBed` błotne gniazdo z kamieniami (atlas) | `StoneBase` ośmiokątny dwustopniowy cokół z fryzami (meander ze złotem, turkusowe trójkąty), luźne bloki, dwa kamienne „strażniki” ze złotym czubkiem po bokach przodu (atlas) |
| `Water` kałuża z prawej z przodu (atlas, w Studio lekko odbija) | `MossNest` mchowe gniazdo na cokole (atlas) |
| `Roots` 5 korzeni spod jaja (atlas) | `BigLeaves` 7 wielkich liści, wachlarz z tyłu i z boków (atlas, dwustronne) |
| `Reeds` 4 kępy trzcin z pałkami (atlas, liście dwustronne) | `Vines` liany oplatające cokół, z listkami (atlas) |
| `Lilies` liście grzybienia i 2 kwiaty lilii (atlas) | `Flowers` 4 hibiskusy z precikiem (atlas) |
| `MushroomStems` / `MushroomCaps` / `MushroomSpots` fioletowe muchomory bagienne ze świecącymi cętkami | `Crystals` bursztynowe kryształy (Neon) |
| `Bubbles` świecące bąble, `Crystals`, `Shards` (Neon, trująca zieleń) | `Shards` bursztynowe odłamki (Neon) |

Trójkąty w spoczynku (bez kawałków skorupy, które są niewidoczne): Bagno ok. 7,4 tys., Dżungla ok. 5 tys.
(dokładnie w `modele/*_statystyki.json`). Tekstury: kolor jaja 2048 × 1024 (Roblox i tak zmniejsza do 1024 — jak
leśne), maska blasku 2048 × 1024 (szarości: kolor daje `EmissiveTint`), atlas ozdób 1024 × 1024.

## Animacja

Dane w `studio/JajkaBiomowDane.luau` (gotowy ModuleScript), czyta je `studio/JajkaBiomowSpoczynek.client.luau`.

- **Spoczynek (wszyscy gracze, gdy kamera < 160 studów):** Egg buja się wokół korzenia (0,012 rad, jak leśne),
  pęknięcia pulsują (`EmissiveStrength` 0,55 ± 15%). Bagno: trzciny na wietrze, lilie bujają się na wodzie, bąble
  unoszą się i mrugają, kryształy i cętki grzybów pulsują jaśniej. Dżungla: liście na wietrze, kwiaty się kołyszą,
  bursztyn pulsuje.
- **Wyklucie:** ta sama scenka co leśne (5 kliknięć, szarpnięcia, mocniejszy blask, BOOM, ShellTopRight odlatuje,
  po 0,95 s ShellTopLeft, rdzeń w kolorze rzadkości, słup światła, pet ze słupa) — liczby Pawła przepisane do
  `wspolne.wyklucie`. Różni się tylko kolor żył (`kolorZyl`: Bagno 155, 255, 79; Dżungla 255, 95, 168) i reakcja
  ozdób w chwili BOOM (`ozdobyFinal`): Bagno — bąble pękają (wracają po 4,5 s), trzciny odchylają się od jaja,
  kryształy i cętki błyskają; Dżungla — liście i kwiaty odchylają się i wracają sprężyną, bursztyn błyska.
- **Umowa ze scenką:** na czas scenki atrybut modelu `Wyklucie = true` (spoczynek nie rusza wtedy Egg), w chwili BOOM
  `Final += 1` (ozdoby grają finał), opcjonalnie `KolorRzadkosci` (Color3) — błysk kryształów w kolorze trafionego peta.

## Modele w grze (26.11.2026, popołudnie)

- **Modele wgrane i wstawione.** Karol w oknie pytania: „Tak, przez folder modeli” → `wdroz.py wgraj --poczekalnia
  <folder wyników postaci>` (kopia pliku tylko na czas wysyłki, potem usunięta). Zasoby Model: **Jajko Bagna
  93451448952125**, **Jajko Dżungli 74304827925305** (moderacja Approved, prawo „Use” dla gry), stan w
  `studio/zasoby.json`, wpisy `JajkoBagnaModel` / `JajkoDzungliModel` w `assets/manifest.json`. `wdroz.py wstaw`:
  Bagno 15 części, 6,4 × 4,8 × 6,6 studa; Dżungla 11 części, 8,3 × 4,8 × 6,7 studa; punkty E „Punkt Jajko Bagna”
  i „Punkt Jajko Dżungli”.
- **Próba w Play na prawdziwych modelach** (`testy/proba_play.py`): 30 OK, 0 błędów, 3 „?” (zrzuty do oceny) — karta
  szans i cena każdego jajka (300 / 750 / 1350), odmowa bez Rybek, zakup prawdziwym E, 5 kliknięć, rozpad, słup, pet
  z właściwej puli, kolor żył z atrybutu, reakcja ozdób w finale, konsola czysta. Zrzuty `podglad/scenka_*.jpg` są
  z tej próby (prawdziwe modele).
- **Poprawione 26.11 (wieczór): zakup ze scenki idzie „bez pokazu”.** Wcześniej komunikat „Wykluł się: …” pojawiał
  się zaraz po E i zdradzał peta przed otwarciem jaja (także przy leśnym), a stary inkubator biomu grał swoją
  animację. Teraz `JajkoKorowe.server.luau` woła haczyk `SterowanieSerwera("kup", gracz, id, { bezPokazu = true })`;
  serwer petów dopisuje `bezPokazu` do swojego „wyklucie”, a klient petów nie gra animacji inkubatora, chowa
  własnego peta gracza (jak w czasie animacji) i trzyma napis. Scenka (`JajkoKoroweClient`) woła lokalny sygnał
  `PetyProba/Sygnaly/PokazWyklucia`: „odsloniety” razem z dymkiem „NEW PET!” (ok. 0,7 s po wyłonieniu peta ze słupa) →
  napis „Wykluł się: … — premia”; „koniec” po zamknięciu kina → pet rusza za graczem od jaja. Bez sygnału napis
  i pet same po 45 s. Zakup ze starego inkubatora prawdziwym E — bez zmian (animacja i napis jak dotąd).
  Próba `testy/proba_play.py` na prawdziwych modelach: **36 OK / 0 BŁĄD / 3 ?** (nowe punkty: brak animacji inkubatora,
  napis dopiero po wyłonieniu peta, pet za graczem po scence ok. 4,8 st); zrzuty `podglad/scenka_*.jpg` nadpisane —
  w kadrze „CLICK!” już bez napisu. Stary inkubator dalej stoi z własnym E (decyzja ludzi; wskazówka celu „kup jajko”
  w Bagnie i Dżungli prowadzi do niego, nie do nowego jajka). Nie sprawdzono: widoku u drugiego gracza, dotyku
  i myszy, prawdziwego telefonu.
- Sekcje niżej opisują stan sprzed wgrania (noc 25/26.11) i kroki etapu — zostają jako historia.

## Stan w Studio (noc 25/26.11.2026)

- **Maski blasku wgrane** (Studio MCP `upload_image`, konto osoby w Studio; gra ma prawo „Use”): JajkoBagnaBlask
  **111489350305678**, JajkoDzungliBlask **119055456876620** — w `assets/manifest.json` i w `studio_skrypty.py` (`BLASK_ID`).
- **Modele GLB NIE wgrane:** Studio odrzuciło plik przed wysłaniem — folder `swiat/jajka_biomow/modele` nie jest
  zatwierdzony do wgrywania (Assistant → Settings → MCP Permissions → approved upload directories), a narzędzie zabrania
  kopiowania pliku do innego zatwierdzonego folderu. Do zrobienia przez człowieka: dodać ten folder do zatwierdzonych
  (albo wyraźnie zgodzić się na drogę przez folder wyników postaci), potem `python -B swiat/jajka_biomow/wdroz.py wszystko`.
- **Miejsce sprawdzone na mapie i poprawione** (było: 9 studów +Z od stanowiska, przód −X): +Z stawiało jajo za starym
  gniazdem, z dala od drogi, a po +X stanowisk płynie woda (Bagno: rów `Przejscia/Rowy/Toń`, Dżungla: strumień).
  Teraz: Bagno −16 X / −2 Z od `BagnoPas/Punkty/StanowiskoJajka` → ok. (1533, 0, −681,6); Dżungla −13 X / −2 Z od
  `DzunglaPas/...` → ok. (1955,9, 0, −682,1); oba na twardym gruncie, bez wody, widoczne z kładki/drogi; przód −Z (na
  drogę). Promień gruntu pomija mgłę (w Dżungli „Mgla/Mgiełka” na Y 1,25) i części bez kolizji. Zrzuty miejsc:
  `podglad/studio_miejsce_bagno.jpg`, `studio_miejsce_dzungla.jpg`; leśne jajo Pawła dla porównania:
  `podglad/studio_lesne_pawla_przod.jpg`.
- **Animacja spoczynku wdrożona z pakietu** (`wdroz.py skrypty`, jak `swiat/pety_proba/zbuduj.py`, bez `src/`):
  `Workspace/JajkaBiomowPodglad/Moduly/JajkaBiomowDane` (ModuleScript) i `JajkaBiomowPodglad/JajkaBiomowSpoczynek`
  (Script, RunContext = Client, strażnik Studio). Skrypt szuka danych najpierw w kontenerze, potem w
  `ReplicatedStorage.Shared`. Sprawdzona w Play na atrapach (jajo z siatki leśnego + maski, ozdoby z klocków; atrapy
  potem usunięte): bujanie, puls blasku 0,41–0,54, wiatr, lilie, bąble, puls kryształów, finał (odchylenie 5,8–7,8°,
  bąble pękają i wracają po 4,5 s, błysk w `KolorRzadkosci`), `Wyklucie = true` zatrzymuje Egg; konsola bez błędów
  tych skryptów. Modele dostają `ModelStreamingMode = Atomic` (StreamingEnabled jest włączone).
- **Scenka wyklucia w skryptach Pawła (26.11, agent Karola za zgodą Pawła: „niech zrobi agent Karola, wzorując się
  na animacji jaja lasu”)** — wdrożona w Studio (przed nadpisaniem sprawdzone: Source w Studio = repo, hash po
  ujednoliceniu końców wierszy). `src/client/JajkoKoroweClient.client.luau`: lista jajek zamiast jednego (leśne
  + modele z atrybutem `JajkoId` w `JajkaBiomowPodglad`, sprawdzane co sekundę — StreamingEnabled), stan ruchu,
  blokada scenki i pokazany pet osobno dla każdego jajka, `KolorZyl` / `KolorBlasku` z atrybutów (bez atrybutu —
  leśne), `Wyklucie = true` na czas scenki, w chwili BOOM `KolorRzadkosci` i `Final += 1`; jajkami biomów ten skrypt
  rusza tylko w scence (w spoczynku — `JajkaBiomowSpoczynek`); karta szans osobna dla każdego jajka (FOREST / SWAMP /
  JUNGLE EGG). `src/server/JajkoKorowe.server.luau`: stanowiska z id jajka (leśne + modele z `JajkoId`), podpowiedź E
  na `Punkt <nazwa modelu>`, zakup tym samym haczykiem `SterowanieSerwera("kup", gracz, id)`, „info” z id jajka,
  w wyniku wyklucia pole `jajko`, przy odmowie id jajka; poprawka błędu z oryginału: odmowa (np. brak Złota)
  blokowała gracza na 45 s („Jajko już pęka…” przy następnym E) — teraz bez zakupu nie ma blokady.
  **Próba w Play** (`testy/proba_play.py`, atrapy: jajo z siatki leśnego + maski biomów + ozdoby z klocków, potem
  usunięte): **30 OK / 0 BŁĄD / 3 ?** (zrzuty) — dla leśnego, Bagna i Dżungli: karta z ceną 300 / 750 / 1350, jeden
  „pisarz” CFrame jaja (spoczynek i scenka: 1,0 zmiany na klatkę), odmowa bez Złota bez scenki, zakup prawdziwym E
  (Złoto − cena, pet z puli tego jajka, quest „jajka” +1), 5 kliknięć (blask do 1,67), rozpad, odlot, słup, pet
  z napisami, `Final` +1, kolory (światło rdzenia i iskry = `KolorZyl`, `KolorRzadkosci` = kolor peta), ozdoby
  w finale (Bagno: trzciny, błysk kryształów i cętek, bąble pękają; Dżungla: liście i kwiaty, błysk), drugi E
  w scence → „Jajko już pęka…”, konsola bez błędów. Po usunięciu atrap krótki Play (`--tylko-lesne`): 12 OK / 0 BŁĄD,
  konsola czysta. Zrzuty `podglad/scenka_<lesne|bagno|dzungla>_<1_pekanie|2_slup|3_pet>.jpg` (Bagno i Dżungla —
  atrapy, nie prawdziwe modele).

## Etap „Studio” (kroki)

1. **Wgranie modeli:** `wdroz.py wgraj` — `modele/jajko_bagno.glb` i `jajko_dzungla.glb` jako zasoby Model
   (open_cloud_invoke z folderu `modele/`, który musi być zatwierdzony w Studio), czekanie na operację i moderację,
   prawo „Use” dla gry (universe 10776202722), wpisy `JajkoBagnaModel` / `JajkoDzungliModel` w manifeście, stan
   w `studio/zasoby.json` (ochrona przed podwójnym wgraniem). Każda siatka < 3,1 tys. trójkątów.
2. **Maski blasku:** zrobione (wyżej).
3. **Wstawienie:** `wdroz.py wstaw` — Studio w trybie Edit; kontener `Workspace/JajkaBiomowPodglad` (atrybut
   `Wygenerowane`), `insert_asset` jako `JajkoBagnaImport` / `JajkoDzungliImport`, potem `studio/jajko_<biom>_ustaw.luau`
   (skala ×1,5, kolory, maska, korzeń, miejsce jak wyżej). Niczego cudzego nie usuwa — stare gniazda z klocków zostają.
   Potem zrzuty z gry (każde jajko z dwóch stron i z bliska) i ocena: tekstura, siła Neonu, skala.
4. **Animacja spoczynku:** zrobione (`wdroz.py skrypty`); po wstawieniu modeli sprawdzić w Play na prawdziwych siatkach.
5. **Scenka wyklucia (pliki Pawła, za jego zgodą):** zrobione 26.11 (opis wyżej, „Stan w Studio”). Bez modeli
   nowych jajek gra działa jak dotąd (stanowiska biomów po prostu nie powstają). Zakup przez haczyk serwera petów,
   bez zmian w `swiat/pety_proba`. Jeden „pisarz” ruchu jaja sprawdzony w Play.
6. **Próba w Play:** zrobiona na atrapach 26.11 (30 OK). **Po wgraniu prawdziwych modeli** (człowiek zatwierdza folder
   `swiat/jajka_biomow/modele` w Studio: Assistant → Settings → MCP Permissions → approved upload directories):

       python -B swiat/jajka_biomow/wdroz.py wgraj      # GLB → zasoby Model, prawo Use, manifest
       python -B swiat/jajka_biomow/wdroz.py wstaw      # Studio w Edit: modele + punkty E do JajkaBiomowPodglad
       python -B swiat/jajka_biomow/testy/proba_play.py "%LOCALAPPDATA%\BlockyCrycket\proby\<data>_jajka_modele"

   Potem obejrzeć `podglad/scenka_*.jpg` na prawdziwych siatkach (skala i wysokość kamery — `ujecie()` liczy z
   wysokości leśnego jaja ze skałami 3,03 m; nowe ok. 3,0 m z ozdobami — powinno pasować; czy skorupy po rozpadzie
   i słup są w kadrze; czy liście Dżungli nie zasłaniają peta), raport w panelu.

## Niepewne

- Leśne jajo Pawła stoi w Studio („Jajko korowe” w `JajkoKorowePodglad`, (955, 0,2, −695), skala 1,5, całość z ozdobami
  4,7 × 4,8 × 4,6 studa; nowe: Bagno ok. 5,6 × 4,5 × 5,7, Dżungla ok. 7,5 × 4,5 × 5,7). Pliku GLB leśnego nie ma w repo — skala i liczba trójkątów nowych jajek
  są dobrane z liczb w skryptach Pawła (rdzeń 1,59, kula 1,35, skala ×1,5) i z jego tekstury; zestawienie
  `podglad/jajka_zestawienie.jpg` pokazuje leśne tylko jako teksturę Pawła na tej samej bryle.
- FBX: skala jednostek w imporcie Roblox niesprawdzona — zalecany GLB (ta sama droga co leśne).
- Rendery to Blender (Eevee, obrys odwróconą otoczką = jak `Highlight` w kliencie) — w Roblox oświetlenie i Neon będą
  wyglądać inaczej; ocenić dopiero zrzutem ze Studio.
- Miejsce i przód sprawdzone na mapie 26.11 (wyżej), ale bez prawdziwego modelu — po wstawieniu obejrzeć zrzutem,
  czy liście Dżungli (7,5 studa szerokości) nie wchodzą w kwiaty obok i czy trzcina obok jaja Bagna nie przebija jaja.
- **Stary inkubator z pakietu petów obok nowego jajka (do decyzji ludzi):** spoiler i podwójna animacja poprawione
  26.11 wieczorem („bez pokazu”, wyżej). Zostaje: stary inkubator ma dalej własne E (Bagno ok. 15,5 st od punktu
  nowego jajka, Dżungla ok. 12,6 st) — ta sama cena, pula i zapis, ale dwa miejsca zakupu, quest „jajka” liczą tylko
  nowe stanowiska, a wskazówka celu prowadzi do starego inkubatora. Do decyzji: chować E i jajko inkubatora biomu,
  gdy w `JajkaBiomowPodglad` stoi model z tym `JajkoId` (zależą od niego próby petów, wskazówki i miejsce z D-076).
- Napis z nazwą i rzadkością peta nad słupem: tabliczka istnieje (próba czyta „Żołędziak / POSPOLITY”), ale na
  zrzutach jej nie widać — przy leśnym jaju nad jajem wisi tabliczka NPC Jagody; niesprawdzone wzrokowo.
- Przy leśnym jaju w kadrze scenki stoi Jagoda (NPC zagrody, ok. 3 st za jajem) — scenka chowa tylko gracza, jego
  bohatera i pety.
