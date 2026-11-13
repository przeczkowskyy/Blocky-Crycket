---
status: propozycja
tags: [badania, ui, styl, mobile]
---
# Styl UI gier Roblox

> [!info] W skrócie
> Na Roblox wygrywa „bubbly cartoon”: grube ciemne obrysy z zaokrąglonymi narożnikami, nasycone gradienty, błysk w lewym górnym rogu, ikony rysowane jak 3D, duże cyfry i mocne animacje „pop”. Obecne przyciski projektu (Shop, Pets, Quests…) już trafiają w ten standard, ale **przeczą kanonowi** („pixel-art”, „flat design”): kanon trzeba dopasować do grafik, nie odwrotnie. Około 80% graczy gra na telefonie, więc projektujemy najpierw pod telefon: bezpieczne obszary, wolne rogi pod joystick i skok, cele dotykowe ≥ 44 pt. Największe ryzyka obecnego UI to napisy wtopione w PNG (nie da się ich przetłumaczyć) i lewa kolumna przycisków, która na telefonie może kolidować z joystickiem.

## Kontekst platformy
| Fakt | Wartość | Źródło |
|---|---|---|
| Gracze na urządzeniach mobilnych (2024) | ok. 80% z 82,9 mln DAU; telefony dają tylko 46% przychodu z Robuxów | pocketgamer.biz |
| Górny pasek Robloxa (nowy) | rezerwuje 58 px zamiast 36; zależy od urządzenia, nie wpisywać na sztywno, czytać `GuiService.TopbarInset` | devforum 2567355 (36 → 58 px potwierdzone); wątek 3237388 podaje tylko stare 36 px |
| Domyślne sterowanie dotykowe | joystick lewy dół, skok prawy dół; tych stref nie zastawiać | docs: position-and-size, wireframe |
| Tekst w obrazkach | automatyczne tłumaczenie go nie obejmuje | docs: automatic-translations |

Hity gatunku (Grow a Garden, Steal a Brainrot) biły w 2025 rekordy: platforma ok. 47,3–47,4 mln równoczesnych graczy w sierpniu 2025, a Steal a Brainrot jako pierwsza gra przekroczyła 25 mln w październiku 2025 (liczby poszczególnych gier różnią się między źródłami; pocketgamer.biz/robloxs-peak-concurrent-user-count-hits-record-474m-as-steal-a-brainrot-and-grow-a-garden-compete, pocketgamer.biz/robloxs-steal-a-brainrot-becomes-first-game-to-surpass-25m-concurrent-players). Ich UI jest proste i czytelne, a na pierwszym planie są wielkie liczby i nagrody (opis wzorców poniżej to obserwacja gatunku, szczegóły poszczególnych gier: niezweryfikowane).

## Wzorce UI w simulator / tycoon / pet / incremental
| Element | Standard gatunku |
|---|---|
| **Waluty** | pigułki z ikoną 3D po lewej, liczba skrótowa (1,2K / 3,4M), przycisk „+” prowadzący do sklepu; zwykle lewa krawędź albo góra |
| **Przyciski boczne** | kolumna 3–6 kwadratowych kafli (ikona + krótki podpis) przy lewej krawędzi, na środku wysokości ekranu |
| **Dół** | pasek akcji albo hotbar wyśrodkowany, z dala od rogów |
| **Obrys** | gruby, ciemny, zaokrąglone łączenia; w symulatorach „prawie zawsze Round” (devforum 1116289) |
| **Kształty** | duże zaokrąglenia, „cukierkowe” bryły, błysk (highlight) w rogu, wewnętrzny cień |
| **Ikony** | renderowane / malowane „jak 3D” z obrysem; płaskie piktogramy tylko w drobnych miejscach |
| **Rzadkość** | kolor tła i obwódki slotu + świecenie albo animowany gradient od epickiego wzwyż |
| **Animacje** | sprężyste wejście okien, „pop” przy kliknięciu, liczniki odliczające do nowej wartości, wylatujące „+1000” |
| **Powiadomienia** | czerwona kropka albo licznik na kaflu, „!” nad NPC |
| **Okna** | jedno okno modalne naraz, przyciemnione tło, duży czerwony „X” w prawym górnym rogu |

## Ocena obecnego UI projektu
Obejrzane: `assets/processed/` (Coin, Gem, Shop, Pets, Quests, Guilds, Equipment, Teleport, PlayerFrame) i `assets/refs/KeyArt_ref.jpg`.

| Cecha | Stan | Werdykt |
|---|---|---|
| Kafle przycisków: zaokrąglony kwadrat, czarny obrys, kolorowe tło na kategorię, błysk w rogu, delikatny halftone | zgodne ze standardem Roblox | **zostawić** |
| Ikony (wózek z klejnotami, jajo, zwój z mieczem, sztandar, plecak, wir) | malowane cartoon, **nie pixel-art** | zostawić styl, **zmienić kanon** w [[Kierunek artystyczny]] i [[Style Lock]] |
| Moneta i diament | błyszczące, czytelne w małym rozmiarze | zostawić |
| Napisy SHOP / PETS… wtopione w PNG, po angielsku | nie da się ich przetłumaczyć ani zmienić | **zmienić**: grafika bez tekstu + `TextLabel` z `UIStroke` |
| Napisy w trzech wariantach (złote, cyjan w Guilds, białe w Equipment) | niespójne | ujednolicić jeden styl podpisu |
| PlayerFrame: granatowe szkło + złota rama + zielona pigułka poziomu | zgodne z gatunkiem | zostawić; dołożyć paski HP / Energii z kanonu [[HUD]] |
| Key art (szachulcowa karczma, sosny, portal, fiolet zmierzchu) | spójny cartoon fantasy | wzorzec dla świata 3D |
| Kanon „flat design”, „nachylone przyciski” | grafiki nie są płaskie ani nachylone | zastąpić „bubbly cartoon”; nachylenie ±2° tylko dla kart questów |
| Lewa kolumna na 55% wysokości (telefon) | ryzyko kolizji z joystickiem | przesunąć wyżej (środek ~40–45%), przetestować w Device Emulator |
| Font `Arcade` | brak „Ó” (zapis w [[Ekran ładowania]]) | nie używać do polskiego tekstu |

## Telefon: twarde reguły
- `ScreenGui.ScreenInsets = CoreUISafeInsets` dla każdego interaktywnego UI; to domyślna i zalecana wartość (docs: on-screen-containers). `DeviceSafeInsets` / `None` tylko dla tła na cały ekran.
- Położenie i rozmiar przez **Scale**, kształt przez `UIAspectRatioConstraint`; Roblox odradza Offset na wielu ekranach (docs: cross-platform). Sam Scale bywa za mały na telefonie i za duży na TV, dlatego globalny `UIScale` liczony z rozmiaru ekranu (devforum 3183426, 4260179).
- Cele dotykowe ≥ 44×44 pt (Apple) / 48×48 dp (Material), odstęp ≥ 8 (niezweryfikowane dla Robloxa; źródło ogólne: tetralogical.com). Obecne 150 px @1080p daje ok. 54 px na telefonie o wysokości 390 pkt, więc wystarcza; limit min 66 px w [[HUD]] jest bezpieczny.
- Interaktywne elementy blisko naturalnego położenia kciuków, ale nie w skrajnych dolnych rogach (docs: wireframe).
- `GuiService.ViewportDisplaySize` (Small / Medium / Large) i `UserInputService.PreferredInput` przełączają układ i podpowiedzi (docs: cross-platform).
- Wibracje: `HapticEffect` typu `UIClick` przy kluczowych kliknięciach (docs: input/mobile).
- `TopbarInset` czytać przez sygnał zmiany; w pierwszej klatce bywa zerem (devforum 2973508).
- Teksty: `TextScaled` + `UITextSizeConstraint` (min 14, max wg projektu), bez cienkich i ozdobnych fontów (docs: adaptive-design).

## Biblioteki i zasoby
| Narzędzie | Do czego | Uwagi |
|---|---|---|
| **Fusion** (dphfox) | reaktywne UI w Luau | v0.3 wydana 30.08.2024 (tag `v0.3-beta`, oznaczona jako „Latest”, nie pre-release; api.github.com/repos/Elttob/Fusion/releases) |
| **react-luau** (Roblox) | React 17 w Luau | ciężki dla małego zespołu |
| **Vide** (centau) | lekki, w stylu Solid, MIT | dobry kompromis |
| **Iris** (SirMallard) | panele debug w stylu Dear ImGui | tylko narzędzia dev, nie UI gracza |
| **TopbarPlus v3** | własne ikony w górnym pasku | MPL 2.0; warunek: zostawić moduł `Attribute` bez zmian albo podać TopbarPlus w opisie gry; instalacja przez Wally to 3.5.0 (github.com/1ForeverHD/TopbarPlus) |
| Figma → Roblox: MonkeyPTR, UILint v2, Figma Importer Assistant, FigBloxUI | import układu | por. [[Pipeline Figma → Roblox]] |
| Zestawy UI (BuiltByBit, itch.io, Gumroad) | przyciski, ikony | licencje różne; zgłoszono kradzione paczki, sprawdzać źródło |

Rekomendacja: przy obecnej skali (ręczne ScreenGui + `TweenService`) **nie dodawać frameworka** do czasu pierwszego dużego okna (ekwipunek). Wtedy Vide albo Fusion i jeden moduł `UITheme` (kolory, fonty, czasy animacji).

## Proponowany zestaw UI
### Paleta (przybliżony odczyt z grafik projektu)
| Rola | Hex |
|---|---|
| Obrys / tekst-cień | `#141018` |
| Panel tło (granat) | `#1E2A44` → `#2C3B5E` gradient |
| Rama premium (złoto) | `#E8B04A` |
| Podpis przycisku (złoto) | `#FFE066` → `#F5A623` |
| Złoto (waluta) | `#F5C542` |
| Kryształy | `#6FD6F0` |
| Akcja pozytywna / XP | `#7ED957` |
| HP | `#E5484D` |
| Energia / Mana | `#3E8BFF` |
| Kategorie kafli | Sklep `#3B4C66`, Pety `#4FAE7A`, Questy `#D9534F`, Gildie `#9B5BD6`, Ekwipunek `#F0A050`, Teleport `#5BC0E8` |

### Kolory rzadkości
Konwencja z WoW (szary, biały, zielony, niebieski, fioletowy, pomarańczowy: warcraft.wiki.gg) jest powszechnie rozpoznawana. Proponowane odcienie dla ciemnego panelu:

| Poziom | Hex | Efekt |
|---|---|---|
| Pospolity | `#B8C0CC` | brak |
| Niepospolity | `#4CD964` | brak |
| Rzadki | `#3AA0FF` | lekka poświata |
| Epicki | `#B05CFF` | poświata + błysk |
| Legendarny | `#FFA22B` | obracający się `UIGradient` |
| Mityczny | `#FF4D6D` | tęczowy gradient + cząsteczki przy odkryciu |

### Fonty (Enum.Font / Font.fromName)
| Zastosowanie | Font |
|---|---|
| Podpisy przycisków, tytuły okien, „+1000” | `LuckiestGuy` albo `FredokaOne` (tylko Regular) |
| Liczby walut | `FredokaOne` |
| Tekst opisów | `BuilderSans` (`BuilderSansBold`) albo `Font.fromName("Nunito", Enum.FontWeight.Bold)` |
| Komiksowe dymki („POW!”) | `Bangers` |

Polskie znaki (ąćęłńóśźż) w każdym z tych fontów: **niezweryfikowane**, przed decyzją przetestować w Studio.

### Siatka i rozmiary (projekt 1920×1080, `UIScale` 0,5–1,25)
- Jednostka 8 px; marginesy od krawędzi ≥ 40 px; odstęp między kaflami 16–24.
- Kafel HUD 128–150 px; przycisk w oknie min. 96×56; „X” zamknięcia 72 px.
- Obrys `UIStroke` 4 px (panele), 3 px (sloty), 2,5 px (tekst); `LineJoinMode = Round`; `StrokeSizingMode = ScaledSize` tam, gdzie obrys ma się skalować (zachowanie: niezweryfikowane).
- `UICorner`: 12% krótszego boku (kafle), 24 px (okna).

### Komponenty
- **Przycisk:** `ImageButton` (tło bez tekstu) + `TextLabel` (złoty gradient, czarny obrys) + błysk; stany: normalny, wciśnięty, wyłączony (szarość 60%).
- **Okno:** przyciemnienie 50%, panel granatowy ze złotą ramą (9-slice), tytuł na wstędze u góry, „X” w rogu; jedno okno naraz.
- **Pasek waluty:** pigułka, ikona wychodząca poza lewą krawędź, liczba skrótowa, „+” otwiera sklep.
- **Slot przedmiotu:** kwadrat 1:1, tło = gradient rzadkości, obwódka w kolorze rzadkości, ikona, poziom lub liczba w prawym dolnym rogu, czerwona kropka „nowy” w prawym górnym, kłódka na zablokowanym.
- **Ekwipunek:** 4 zakładki (Bronie / Pancerz / Akcesoria / Zużywalne, zgodnie z rozmową 12.11 [18:39]–[19:08]), w każdej **8 slotów w siatce 4×2**; po lewej postać w `ViewportFrame` z polami założonego ekwipunku jak w Shakes & Fidget.
- **Pasek postępu:** zaokrąglona rynna `#141018`, wypełnienie z gradientem i ukośnymi pasami, liczba na środku; ten sam język co pasek w [[Ekran ładowania]].
- **Toast:** u góry na środku, pod paskiem Robloxa; ikona + tekst; 2,5 s; max 3 na stosie.
- **Kropka powiadomień:** czerwona `#E5484D`, biały obrys 2 px, cyfra przy wartości > 1.

### Animacje i dźwięk (propozycja)
| Zdarzenie | Tween (`TweenService`) | Dźwięk |
|---|---|---|
| Najechanie (PC) | skala 1,06, 0,10 s, Quad Out | brak |
| Wciśnięcie | 0,92, 0,06 s → 1,0 Back Out 0,15 s | klik + `HapticEffect` |
| Otwarcie okna | skala 0,8 → 1, przezroczystość 1 → 0, 0,25 s Back Out | „whoosh” |
| Zamknięcie | 0,15 s Quad In | cichy klik |
| Wzrost waluty | odliczanie liczby 0,5 s + puls ikony | brzęk monet |
| Nagroda / rzadki drop | pop 0 → 1,2 → 1, promienie, kolor rzadkości | narastający dźwięk zależny od rzadkości |
| Kropka powiadomienia | puls 1,0 ↔ 1,15 co 1,2 s | brak |

Zasada: wszystko krótsze niż 0,3 s, poza nagrodami. Dzieci chcą widzieć duże cyfry („+1000 siły”, rozmowa [27:40]), więc wylatujące liczby to obowiązek, nie ozdoba.

## Styl świata 3D
- Na Roblox dominuje stylizowany low-poly, bo jest wydajny na telefonach, szybki w budowie i lubiany przez młodych graczy (devforum 317249, 511551; opinie społeczności, bez twardych danych).
- Telefony mają mało pamięci; najmocniejszą dźwignią jest streaming instancji (`StreamingEnabled`; docs nazywają to „instance streaming” i włączają domyślnie dla nowych miejsc). Tekstura 1024² zużywa 4 razy więcej pamięci niż 512² (docs: memory). Kolizja dekoracji: Box / Hull, nie Precise (docs: improve).
- **Leśna baza startowa z karczmą:** przenieść key art do 3D: szachulcowa, lekko krzywa karczma z czerwonym dachem i ciepłym światłem w oknach, grube sosny o prostych sylwetkach, kamienna ścieżka, portal z żółtym wirem, beczki i drogowskazy. Kolory nasycone, mało drobnej roślinności, tekstury ≤ 512 px.
- Nad budynkami ikony 2D (`BillboardGui`) w stylu kafli HUD, np. kufel nad karczmą (rozmowa [2:38]); łączy świat 3D z UI i ułatwia orientację na małym ekranie.
- Postacie i pety mają klockowe proporcje (Rycerz z key artu); komiksowy obrys w 3D tylko tam, gdzie da się go tanio zrobić (`Highlight` ma limit liczby instancji, niezweryfikowane).

## Powiązane
[[HUD]] · [[Kierunek artystyczny]] · [[Style Lock]] · [[Ekran ładowania]] · [[Okno Karczmy]] · [[Pipeline Figma → Roblox]] · [[Pipeline assetów]] · [[System RPG]] · [[Pety]] · [[Pytania otwarte]] · [[Rynek Roblox i konkurencja]] · [[Narzędzia i skille do Roblox]]

## Weryfikacja
Sprawdzone 2026-11-12 w źródłach pierwotnych.
- 80% DAU na telefonach (82,9 mln, 2024), 46% Robuxów ze sklepów mobilnych -> potwierdzone -> pocketgamer.biz (link w Źródłach)
- Górny pasek 36 → 58 px, zależy od urządzenia -> potwierdzone (tylko wątek 2567355; 3237388 nie podaje 58) -> devforum 2567355
- `ScreenInsets` domyślnie i zalecanie `CoreUISafeInsets` -> potwierdzone -> create.roblox.com/docs/ui/on-screen-containers
- Tekst w obrazkach poza tłumaczeniem automatycznym -> potwierdzone („Images with embedded text” wyłączone z ATC) -> docs automatic-translations
- `HapticEffect` typ `UIClick` -> potwierdzone -> docs input/mobile
- Tekstura 1024² = 4x pamięci względem 512² -> potwierdzone -> docs memory
- Fonty LuckiestGuy, FredokaOne, Bangers, BuilderSans(Bold), Arcade istnieją w Enum.Font -> potwierdzone; obsługa polskich znaków -> niezweryfikowane -> docs Font
- Cele dotykowe 44 pt (Apple) / 48 dp (Material) -> potwierdzone; odstęp ≥ 8 -> niezweryfikowane -> tetralogical.com
- react-luau = React 17 -> potwierdzone -> github.com/Roblox/react-luau
- Vide = MIT, w stylu Solid -> potwierdzone -> github.com/centau/vide
- TopbarPlus = MPL 2.0 -> potwierdzone, dopisano warunek atrybucji -> github.com/1ForeverHD/TopbarPlus
- Fusion 0.3 -> poprawione: wydane 30.08.2024 (wcześniej „niezweryfikowany”) -> api.github.com/repos/Elttob/Fusion/releases
- „Rekordy ponad 20 mln” -> poprawione: platforma 47,3–47,4 mln (sierpień 2025), Steal a Brainrot 25 mln (październik 2025) -> pocketgamer.biz
- `StrokeSizingMode.ScaledSize` istnieje; działanie -> niezweryfikowane (docs nie opisują) -> docs enums/StrokeSizingMode
- Streaming: docs mówią „instance streaming”, domyślnie włączony w nowych miejscach -> poprawione -> docs memory
- Limit instancji `Highlight`, „prawie zawsze Round” w simulatorach (devforum 1116289), brak „Ó” w foncie Arcade -> niezweryfikowane w tej rundzie

## Źródła
Dostęp 2026-11-12.
- https://www.pocketgamer.biz/80-of-roblox-users-are-on-mobile-contributing-46-of-robux-revenue/
- https://tribune.com.pk/story/2563322/roblox-breaks-concurrent-user-record-after-grow-a-garden-and-steal-a-brainrot-player-surge
- https://create.roblox.com/docs/ui/on-screen-containers
- https://create.roblox.com/docs/reference/engine/enums/ScreenInsets
- https://create.roblox.com/docs/en-us/ui/position-and-size
- https://create.roblox.com/docs/projects/cross-platform
- https://create.roblox.com/docs/production/publishing/adaptive-design
- https://create.roblox.com/docs/tutorials/curriculums/user-interface-design/wireframe-your-layouts
- https://create.roblox.com/docs/input/mobile
- https://create.roblox.com/docs/production/localization/automatic-translations
- https://create.roblox.com/docs/reference/engine/enums/Font
- https://create.roblox.com/docs/reference/engine/datatypes/Font
- https://create.roblox.com/docs/reference/engine/classes/UIStroke
- https://create.roblox.com/docs/reference/engine/enums/StrokeSizingMode
- https://create.roblox.com/docs/projects/performance-optimization/memory
- https://create.roblox.com/docs/en-us/performance-optimization/improve
- https://devforum.roblox.com/t/studio-beta-for-experience-controls-available-now/2567355
- https://devforum.roblox.com/t/what-are-the-new-topbar-inset-dimensions/3237388
- https://devforum.roblox.com/t/guiservicegetguiinset-returns-0-0-0-0-for-the-first-frame-of-the-game-with-new-topbar-ui/2973508
- https://devforum.roblox.com/t/uistroke-studio-beta-update-re-enabled/1116289
- https://devforum.roblox.com/t/why-should-i-use-uiaspectratioconstraint-over-just-scaling-the-ui/3183426
- https://devforum.roblox.com/t/we-should-deprecate-guiobjectsize-in-favor-of-uiscale/4260179
- https://devforum.roblox.com/t/topbarplus-v340-construct-topbar-icons-with-ease-customise-them-with-themes-dropdowns-captions-labels-and-more/1017485
- https://devforum.roblox.com/t/why-is-the-low-poly-graphics-style-so-common/317249
- https://devforum.roblox.com/t/why-the-low-poly-graphics-style-is-so-common/511551
- https://devforum.roblox.com/t/figma-importer-assistant-a-faster-way-to-create-your-ui/2961561
- https://devforum.roblox.com/t/plugin-uilint-v2-import-figma-ui-into-roblox-studio/4765869
- https://github.com/Elttob/Fusion/releases
- https://github.com/Roblox/react-luau
- https://github.com/centau/vide
- https://github.com/SirMallard/Iris
- https://warcraft.wiki.gg/wiki/Quality
- https://tetralogical.com/blog/2022/12/20/foundations-target-size/
- https://builtbybit.com/resources/roblox/graphics-ui/
