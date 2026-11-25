---
status: propozycja
---
# Jajka biomów — Bagno i Dżungla na wzór leśnego jaja Pawła

Zlecenie Karola z sesji 25.11.2026: wziąć leśne jajo Pawła (artefakt „Leśne jajo 3D”, zasób 92671202213818,
`tools/studio/jajo_lesne_ustaw.luau`, scenka `src/client/JajkoKoroweClient.client.luau`) jako wzór i zrobić takie same
jakościowo jajka do Bagna i Dżungli, z animacją spoczynku i wyklucia. **Propozycja** — nic tu nie jest kanonem;
nie wgrane do Roblox i nie wstawione do Studio (osobny etap, kroki niżej).

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
| `studio_skrypty.py` → `studio/jajko_<biom>_ustaw.luau` | ustawienie modelu w Studio (wzór: `jajo_lesne_ustaw.luau`) — **nie uruchamiane** |
| `studio/JajkaBiomowDane.luau` | dane animacji (spoczynek, wyklucie, reakcje ozdób) — docelowo `src/shared/` |
| `studio/JajkaBiomowSpoczynek.client.luau` | ruch w spoczynku i reakcja ozdób na finał — docelowo `src/client/` |
| `modele/jajko_<biom>.glb`, `.fbx`, `_statystyki.json` | modele do importu (tekstury koloru osadzone) i liczby |
| `podglad/*.jpg` | plansze: 4 strony każdego jajka, skorupa i rozpad, zestawienie w jednej skali |

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

## Etap „Studio” (po tym pakiecie — kroki)

1. **Wgranie modelu:** `modele/jajko_bagno.glb` i `jajko_dzungla.glb` jako zasoby Model (Open Cloud albo 3D Importer
   w Studio). Importer sam utworzy obrazy z osadzonych tekstur koloru i atlasu. Każda siatka < 3,1 tys. trójkątów.
2. **Maski blasku:** wgrać `tekstury/bagno_jajo_blask.png` i `dzungla_jajo_blask.png` (obrazy), wpisać do
   `assets/manifest.json` (np. `JajkoBagnaBlask`, `JajkoDzungliBlask`) i podać ID w `studio_skrypty.py` (`BLASK_ID`
   w `KONFIG`) → `python -B swiat/jajka_biomow/studio_skrypty.py`.
3. **Zgoda „Use”:** jeśli zasoby wgrał ktoś inny niż właściciel gry, w Creator Hub → zasób → Permissions dodać
   doświadczenie Blocky & Crycket z prawem Use (inaczej `insert_asset` nie wstawi modelu).
4. **Wstawienie:** Studio w trybie Edit, bez innego agenta w Studio; ChangeHistory przed i po. Utworzyć kontener
   `Workspace/JajkaBiomowPodglad` (atrybut `Wygenerowane`), wstawić model jako `JajkoBagnaImport` /
   `JajkoDzungliImport`, uruchomić `studio/jajko_<biom>_ustaw.luau` (MCP `execute_luau`). Skrypt stawia jajko obok
   stanowiska z mapy (`BagnoPas/Punkty/StanowiskoJajka`, `DzunglaPas/...`, przesunięcie 9 studów, przód −X) i niczego
   nie usuwa — stare gniazda z klocków zostają do decyzji. Sprawdzić zrzutem, czy przód patrzy na ścieżkę.
5. **Animacja spoczynku:** `studio/JajkaBiomowDane.luau` → `src/shared/JajkaBiomowDane.luau`,
   `studio/JajkaBiomowSpoczynek.client.luau` → `src/client/` (Rojo zsynchronizuje).
6. **Scenka wyklucia (pliki Pawła — za jego zgodą albo przez niego):** w `JajkoKoroweClient` zamiast jednego modelu
   lista jajek (`Jajko korowe` + modele z `JajkaBiomowPodglad`), `KOLOR_ZYL` i `KOLOR_BLASKU` z atrybutów modelu
   `KolorZyl` / `KolorBlasku`, ustawianie `Wyklucie` i `Final`; w `JajkoKorowe.server.luau` zamiast stałej
   `JAJKO = "jajko_lesne"` — id z atrybutu `JajkoId` modelu (`jajko_bagienne`, `jajko_dzungli`), podpowiedź E na
   `Punkt Jajko Bagna` / `Punkt Jajko Dżungli` (skrypt ustawiający tworzy te punkty bez podpowiedzi). Zakup dalej przez
   haczyk serwera petów Karola (`SterowanieSerwera("kup", gracz, id)`), bez zmian w `swiat/pety_proba`.
   Jeden „pisarz” ruchu jaja: w spoczynku Egg nowych jajek rusza `JajkaBiomowSpoczynek`, a klient Pawła tylko
   w czasie scenki (gdy `Wyklucie = true`) — inaczej dwa skrypty co klatkę ustawiają ten sam CFrame.
7. Próba w Play (kupno, 5 kliknięć, rozpad, słup, pet), zrzuty, raport w panelu.

## Niepewne

- Modelu leśnego jaja (GLB) nie ma w repo ani w Studio w trybie Edit tej nocy — skala i liczba trójkątów nowych jajek
  są dobrane z liczb w skryptach Pawła (rdzeń 1,59, kula 1,35, skala ×1,5) i z jego tekstury; zestawienie
  `podglad/jajka_zestawienie.jpg` pokazuje leśne tylko jako teksturę Pawła na tej samej bryle.
- FBX: skala jednostek w imporcie Roblox niesprawdzona — zalecany GLB (ta sama droga co leśne).
- Rendery to Blender (Eevee, obrys odwróconą otoczką = jak `Highlight` w kliencie) — w Roblox oświetlenie i Neon będą
  wyglądać inaczej; ocenić dopiero zrzutem ze Studio.
- Miejsce i przód w Studio to założenie (stanowisko z map `bagno_pas` / `dzungla_pas` sprzed przebudowy biomów
  z 19.11) — do sprawdzenia na mapie.
