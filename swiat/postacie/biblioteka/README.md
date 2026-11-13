# Biblioteka postaci i ekwipunku (Blender, proceduralnie)

Kręgosłup do budowania **postaci, stworów (petów) i ekwipunku** z kanciastych brył w stylu gry — skryptem Pythona, w Blenderze 5.0 uruchamianym w tle, bez okna. Jeden moduł `.py` = jedna postać albo jeden zestaw ekwipunku. Biblioteka robi z niego siatki, szkielet, animacje, rendery prezentacyjne, ikony, film, eksport FBX/GLB i raport z limitami Roblox.

> **Status: propozycja.** Nic, co tu powstaje, nie jest kanonem gry — kanon wyglądu postaci jest w sejfie (`B&C/Postacie/*.md`, `B&C/Styl/*.md`). **Import siatek do Roblox Studio nie był testowany** (wymaga uploadu) — patrz „Czego biblioteka NIE gwarantuje”. Sprawdzona jest za to ścieżka bez uploadu: postacie z części Roblox (`roblox_klocki.py`, opis w `../README.md`).

| Plik | Co to jest |
|---|---|
| `postac.py` | czysty Python (bez `bpy`): `Postac`, `Akcesorium`, `Klip`, manekin R15, gotowe klipy, paleta, limity Roblox, zapis do JSON |
| `blender_postac.py` | uruchamiany w Blenderze: JSON → siatki, szkielet, akcje, raport, eksport, rendery, film, kontrola eksportów |
| `roblox_klocki.py` | czysty Python: postać → rig z części Roblox (rozkład brył na Part/WedgePart/CornerWedgePart, stawy, zaczepy, próbki klipów) w układzie Roblox (przód −Z) |
| `blender_probki.py` | uruchamiany w Blenderze: wartości krzywych każdego klipu co klatkę (te same wygładzenia co w filmach) |
| `podglad_postaci.py` | zwykły Python z folderu repozytorium: moduł → JSON → Blender pod wspólną blokadą → lista plików |
| `../wzor_postaci.py` | wzór: prosty ludzik R15 z jednym klipem (`machanie`) |
| `../wzor_ekwipunku.py` | wzór: hełm i miecz przymierzone na manekinie, z ikonami |

## Szybki start

```
# z głównego folderu repozytorium; --wyj = folder na rendery próbne (najlepiej POZA repozytorium)
python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_postaci.py --wyj <folder>
python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_postaci.py --wyj <folder> --klip machanie
python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_ekwipunku.py --wyj <folder> --klip atak
python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_postaci.py --wyj <folder> --ikony --eksport
```

| Opcja | Co robi |
|---|---|
| (zawsze) | `<id>_raport.json` + raport w konsoli, `<id>_plansza.jpg` (2×2: bohater 3/4 z obrysem, przód z szarym manekinem skali, bok prawy, tył), `<id>_bohater.jpg` (900 px); dla akcesoriów też `<id>_ikona.png` |
| `--klip X` | `<id>_X.mp4` (H.264, yuv420p, 480 px, pętla ×3), `<id>_X_klatki.jpg` (8 klatek z renderu, czytaj wierszami), `<id>_X_z_filmu.jpg` (8 klatek **odczytanych z gotowego MP4** — dowód, że film się odtwarza). Kadr liczony z obwiedni WSZYSTKICH klipów modelu (stała ogniskowa), więc filmy różnych klipów mają tę samą skalę |
| `--ikony` | ikona 512 px (przezroczyste PNG, obrys ok. 3 px) także dla postaci; postać R15 w kadrze popiersia (głowa + górne 40% tułowia) |
| `--eksport` | `<id>.fbx` (model bez animacji), `<id>__<klip>.fbx` (jeden klip na plik), `<id>.glb` (wszystkie klipy), `<id>.blend`, `<id>_tekstury/*.png`, potem **KONTROLA**: każdy plik wczytany z powrotem do pustego Blendera i porównany (siatki, kości, długości klipów, trójkąty, wzrost) |
| `--bez-obrysu` | kadr bohaterski i film bez obrysu (ikony zawsze z obrysem) |
| `--bez-renderu` | tylko dane, kontrola i raport (Blender startuje tylko do raportu) |
| `--tylko a,b` · `--szer 900` · `--probki 16` | wybrane modele · szerokość kadru bohaterskiego · próbki EEVEE |

Moduł ma funkcję `zbuduj()`, która zwraca `Postac`, `Akcesorium` albo listę. **Same akcesoria** podgląd zakłada na szarego manekina R15 (model `<moduł>_przymiarka`, funkcja `przymiarka()`; z bronią w pozie `trzymanie`, a w chodzie z uniesionym przedramieniem). Do folderu `wynik/<moduł>/` w stałym układzie przebudowuje `../przebuduj.py` (opis w `../README.md`); moduł może podać `FILMY` (lista klipów do filmów), `SLABOSCI` (lista do `raport.txt`) i `EKSPORT_MODELI = False` (z przymiarek tylko plansze). Blender działa pod wspólną blokadą (`zajmij_blender`/`zwolnij_blender` z `swiat/biblioteka/podglad.py`), więc wielu autorów może wołać podgląd naraz — czekają w kolejce. Typowy czas: model bez filmu 2–10 s, z filmem 15–35 s.

## Konwencje
- **Jednostka = stud** (1 jednostka Blendera = 1 stud). **Y w górę. Postać patrzy w +Z. Jej LEWA strona to +X** (prawa ręka jest po stronie −X). Tak samo jak front budynku w `swiat/biblioteka/scena.py`.
- W Blenderze: dane `(x, y, z)` → `(x, −z, y)`, czyli postać patrzy w −Y (widok Front), lewa strona = +X.
- **Obrót** = `(rx, ry, rz)` w stopniach, kolejność Roblox `CFrame.fromOrientation` (R = Ry·Rx·Rz); w Blenderze Euler `ZXY`.
- **Kości** w spoczynku mają osie równoległe do osi modelu (kość skierowana w górę, roll 0). Obrót kości w klipie = obrót wokół osi modelu zaczepiony w stawie: **rx < 0 unosi zwisającą rękę/nogę do przodu**, **rz > 0 odchyla ją w stronę +X** (lewa ręka na zewnątrz; prawa na zewnątrz = rz < 0), ry > 0 skręca przód w stronę +X, dla głowy rx > 0 = skłon w przód.
- **Bryły** są przypięte sztywnie do kości (jedna siatka na kość: `<Kosc>_Geo`, waga 1). Układ lokalny kości: `(0, 0, 0)` = staw; `with p.na("Kosc", od="srodek")` = środek klocka kości. Wyjątek: `p.skoruj(kosc, druga, y0, y1)` — siatka `<kosc>_Geo` dostaje wagi na dwóch kościach zależnie od wysokości wierzchołka (slime: zgniatanie przesunięciem kości zamiast skali).
- **Nazwy** id, kości, klipów i zaczepów: ASCII (`^[A-Za-z][A-Za-z0-9_]*$`). Nazwy brył dowolne (to tylko etykiety).
- Elementy na powierzchni (oczy, klamry) **wystają 0,02–0,05** przed ścianę — nigdy w tej samej płaszczyźnie (migotanie).
- Bez napisów i liter na modelach. Własne projekty — nie odtwarzamy postaci ani przedmiotów z innych gier.

## Ściąga API

```python
from swiat.postacie.biblioteka.postac import (Postac, Akcesorium, manekin_r15, KOLORY,
    klip_spoczynek_r15, klip_chod_r15, klip_atak_r15, klip_trzymanie_r15)

# --- postać R15: szkielet z proporcji (stawy liczą się same z wysokości klocków)
p = Postac("karczmarz", "Karczmarz", typ="r15", skala=1.0, faza=0.05,
           wymiary={"Head": (1.5, 1.4, 1.4), "UpperTorso": (2.8, 1.7, 1.8), "UpperLeg": (1.0, 0.7, 1.0)},
           rozstaw_nog=None, rozstaw_rak=None, bark=None)
p.cialo({"glowa": "skora", "tulow": "bialy", "pas": "brazowy", "ramiona": "bialy",
         "dlonie": "skora", "nogi": "brazowy_ciemny", "stopy": "tusz"})   # albo klucze = nazwy kości
p.wymiary("Head"), p.srodek("Head"), p.staw("Head")     # klocek kości: rozmiar, środek względem stawu, staw

# --- bryły (pos = środek skrzynki części, size = (szer X, wys Y, głęb Z); kolor = klucz KOLORY albo "RRGGBB")
with p.na("Head", od="srodek"):                          # od="staw" (domyślnie) albo "srodek"; też pos=, obrot=
    p.blok(nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), faza=None)
    p.klin(...)        # jak WedgePart: pionowa ściana +Z, skos opada ku −Z
    p.naroznik(...)    # jak CornerWedgePart: wierzchołek (+X, +Y, −Z)
    p.walec(nazwa, pos, size, kolor, mat, rot, faza=None, segm=8)        # stojący (oś Y); leżący: rot=(0, 0, 90)
    p.stozek(nazwa, pos, size, kolor, mat, rot, gora=0.0, segm=8)        # gora = ułamek promienia (0 = szpic)
    p.kula(nazwa, pos, size_albo_srednica, kolor, mat, rot, segm=8)
    p.ostroslup(nazwa, pos, size, kolor, mat, rot, gora=(0, 0), przes_gory=(0, 0))  # góra w studach; krzywy szpic
    with p.uklad(pos=(..), obrot=(..), skala=1.0):        # zagnieżdżalny układ lokalny (jak scena.py)
        ...
p.klocek("LeftHand", "skora", powieksz=(0.1, 0, 0.1))    # klocek o wymiarach części kości

# --- stwór: własne kości (Root powstaje sam; staw w układzie modelu, czesc = klocek kości)
s = Postac("pies", "Pies", typ="stwor", skala=0.7)
s.kosc("Tulow", "Root", staw=(0, 1.2, 0), czesc=(1.4, 1.0, 2.2), srodek=(0, 0, 0))
s.kosc("Glowa", "Tulow", staw=(0, 1.5, 1.0), czesc=(1.1, 1.0, 1.0), srodek=(0, 0.3, 0.4))

# --- punkty zaczepienia i akcesoria (akcesorium = JEDNA sztywna siatka w układzie swojego zaczepu)
p.zaczep("PlecyAttachment", "UpperTorso", pos, rot=(0, 0, 0))        # własny albo przestawienie standardowego
p.skoruj("Dol", "Gora", 0.0, 2.25)                       # siatka Dol_Geo na dwóch kościach (wagi z wysokości)
a = Akcesorium("helm", "Hełm", zaczep="HatAttachment", typ="Hat", skala=1.0, ikona_obrot=(0, 0, 0),
               chwyt=None, przymierz=True)               # chwyt="drzewce": kostur/włócznia; przymierz=False: tylko ikona
a.blok(...)                                              # te same bryły, bez kości; (0,0,0) = zaczep
p.zaloz(a, zaczep=None, pos=(0, 0, 0), obrot=(0, 0, 0), eksport=True)   # eksport=False: tylko do podglądu

# --- klipy (klatki 0…dlugosc, 30 kl./s; pętla domyka się sama: brakujący klucz końcowy = klucz z klatki 0)
k = p.klip("chod", 24, fps=30, petla=True)
k.klucz(klatka, "LeftUpperLeg", obrot=(rx, ry, rz), przes=(dx, dy, dz), skala=(sx, sy, sz), wyg="gladko")
k.poza(klatka, {"RightUpperArm": (0, 0, -150), "Head": {"obrot": (5, 0, 0)}})   # wiele kości naraz
k.cykl("LeftUpperLeg", "obrot", (30, 0, 0), faza=0.0, czestosc=1, srodek=None)  # sinus; cykle się SUMUJĄ
k.zamach("RightUpperArm", wziecie=(-165, 0, -10), uderzenie=(-50, 0, 5), czasy=(0.35, 0.5, 0.62), dobicie=0.12)
p.ustaw_poze_renderu("chod", 6)                          # rendery i ikona w tej klatce zamiast spoczynku
klip_chod_r15(p); klip_spoczynek_r15(p); klip_atak_r15(p, reka="Right"); klip_trzymanie_r15(p)  # gotowe R15
chod_z_bronia(k, drzewce=False)                          # chód z bronią: przedramię −35° (drzewce −80°, pionowo)
przymiarka("zestaw_x_przymiarka", akcesoria)             # manekin R15 z założonymi akcesoriami

def zbuduj():
    return [p, a]                                        # Postac / Akcesorium / lista
```

- **Wygładzanie** klucza dotyczy odcinka od niego do następnego: `gladko` (Bezier, auto), `liniowo`, `stale`. Klip zapętlony dostaje w Blenderze modyfikator Cycles na krzywych — szew pętli jest gładki.
- **Kanały:** `obrot` (stopnie), `przes` (studs, osie modelu; mnożone przez `skala` postaci), `skala` (mnożniki; skaluje też dzieci kości). **Nie używaj `skala` w klipach dla Roblox**: animacje Roblox przenoszą pozycję i obrót kości, skali najpewniej nie — podgląd i raport ostrzegają („klip ma kanał skali”). Moduły w `swiat/postacie/` nie mają już żadnego kanału skali.
- **Przełączanie klipów** w Blenderze zawsze najpierw zeruje pozę (`ustaw_akcje`): kanały, których nowy klip nie animuje, nie zostają w wartości z poprzedniego klipu (wcześniej miecz Rycerza w pokazie i kolejnych FBX klipów zostawał w pozie z ataku).
- **`skala` postaci** mnoży kości, bryły, zaczepy i przesunięcia; założone akcesoria zachowują własny rozmiar (`Akcesorium.skala`), zmienia się tylko miejsce zaczepu.
- **`faza`** (domyślnie 0,05 studa, model-wide w konstruktorze albo na bryle) ścina twarde krawędzie (> ~57°) jednym segmentem; boki walców i krawędzie schodzące do szpica zostają ostre; faza jest przycinana do 22% najmniejszego wymiaru bryły.
- **`segm`** walca/stożka/kuli: wielokrotność 4 trzyma dokładny rozmiar skrzynki (ściany, nie rogi, dotykają skrzynki).

### Materiały i kolory
Materiały: `zwykly` (plastik z połyskiem, szorstkość 0,42), `matowy` (tkanina, drewno, 0,85), `polysk` (oczy, lakier, 0,15), `metal` (metaliczność 0,7, szorstkość 0,28), `swiecacy` (emisja 1,0), `poswiata` (lekka emisja 0,6, np. skorupka slime'a). Paleta `KOLORY`: `tusz, bialy, skora, skora_cien, rumieniec, stal, stal_cien, stal_ciemna, zloto, zloto_ciemne, niebieski(_ciemny/_jasny), fiolet(_ciemny/_jasny), pomarancz(_jasny/_ciemny), brazowy(_ciemny/_jasny), czerwony(_ciemny), zielony(_ciemny), turkus(_ciemny), szary(_ciemny)`; własna: `paleta={"klucz": "RRGGBB"}` w konstruktorze.

Roblox wymaga **jednego materiału na siatkę**, więc każdy model ma jeden materiał `<id>_Mat`, a różnice siedzą w czterech małych **teksturach-paletach** (`<id>_tekstury/<id>_kolor|metal|szorstkosc|emisja.png`, komórki 8×8 px, UV każdej ściany wskazuje środek komórki). Dodatkowo kolory wierzchołków (atrybut `Col`).

### R15: kości, stawy, zaczepy
Hierarchia (jak w specyfikacji Roblox): `Root > HumanoidRootNode > LowerTorso > UpperTorso > Head`; `UpperTorso > {Left,Right}UpperArm > LowerArm > Hand`; `LowerTorso > {Left,Right}UpperLeg > LowerLeg > Foot`. `Root` w (0, 0, 0) na ziemi, `HumanoidRootNode` i `LowerTorso` w stawie bioder (brak wpływów na `Root`/`HumanoidRootNode` — bryła na nich to błąd).

Domyślne klocki (szer × wys × głęb, studs; razem **5,25 studa wzrostu**, biodra na 2,0, szyja na 4,0): Head 1,25³ · UpperTorso 2×1,6×1 · LowerTorso 2×0,4×1 · UpperArm 1×0,95×1 · LowerArm 1×0,75×1 · Hand 1×0,3×1 · UpperLeg 1×0,85×1 · LowerLeg 1×0,8×1 · Foot 1×0,35×1. Stawy: bark 0,25 pod górą tułowia na środku ręki (x = ±1,5), łokieć/nadgarstek/kolano/kostka na górze swoich klocków, biodra x = ±0,5. To **własny wybór** biblioteki (dokumentacja Roblox nie podaje wymiarów klockowego R15, tylko limity), zgodny z ludzikiem skali z `swiat/biblioteka/podglad.py`.

Zaczepy (nazwy jak obiekty `Attachment` w Studio; liczone z klocków, przestawialne `p.zaczep`): Head — `FaceCenterAttachment` (środek), `FaceFrontAttachment` (przód), `HatAttachment` i `HairAttachment` (środek góry); UpperTorso — `NeckAttachment` (góra), `BodyFrontAttachment`, `BodyBackAttachment`, `LeftCollarAttachment`, `RightCollarAttachment` (górne rogi); LowerTorso — `WaistCenterAttachment`, `WaistFrontAttachment`, `WaistBackAttachment`; `Left/RightShoulderAttachment` (góra UpperArm); `Left/RightGripAttachment` (środek dłoni, obrót (90, 0, 0)); `Left/RightFootAttachment` (spód stopy). W eksporcie powstają z nich siatki-znaczniki `<Nazwa>_Att` (np. `Hat_Att`, plus `Root_Att` w stawie LowerTorso) przypięte do kości — tak nazywa je importer Roblox.

**Broń** na `RightGripAttachment`: modeluj pionowo — rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z). Gdy ręka zwisa, ostrze celuje do przodu; w pozie `trzymanie` (przedramię rx = −80) sterczy w górę. **Hełm** na `HatAttachment` (środek górnej ściany głowy; głowa manekina to sześcian 1,25, jej środek w (0, −0,625, 0) od zaczepu).

## Raport i kontrola
Raport (`<id>_raport.json` + konsola): trójkąty i wymiary (szer × wys × głęb w studach) każdej siatki, wymiary ciała i całości z akcesoriami, kości, klipy (klatki, sekundy, pętla), zaczepy, rozmiar tekstury, a dla R15 budżety grup ciała i **ostrzeżenia** względem limitów niżej. Dla akcesorium: zakres od zaczepu i sprawdzenie pudełka typu (skala Classic). Ostrzeżenia o ciele awatara (np. wzrost < 4 studów u małego kota) dotyczą tylko ciała na Marketplace — NPC w grze to nie blokuje.

Kontrola po `--eksport` wczytuje FBX/GLB do pustego Blendera i porównuje z tym, co wyeksportowano. Sprawdzone 13.11.2026 na wzorach: 13 plików (FBX modeli, FBX klipów, GLB), wszystkie ZGODNE (np. `wzor_ludzik`: 34 siatki = 15 części + 19 znaczników, 17 kości, 1568 trójkątów, wzrost 5,64; klip `machanie` 36 klatek w FBX i GLB; `przymiarka`: 4 klipy w jednym GLB). Ścieżka „stwor” (własne kości, `skala`, kanał skali, akcesorium na własnym zaczepie) sprawdzona osobnym testem — 5 plików ZGODNE.

## Fakty Roblox (źródła sprawdzone 13.11.2026)
| Temat | Wartość | Źródło |
|---|---|---|
| Siatka (MeshPart) | ≤ **20 000 trójkątów**; ≤ 4 kości na wierzchołek; kości zamrożone (skala 1, obrót 0), korzeń w 0,0,0 bez wpływów; **jedna ścieżka animacji na siatkę/model** | create.roblox.com/docs/art/modeling/specifications |
| Ciało awatara | **15 siatek** `Head_Geo, UpperTorso_Geo, LowerTorso_Geo, Left/RightUpperArm_Geo, …LowerArm_Geo, …Hand_Geo, …UpperLeg_Geo, …LowerLeg_Geo, …Foot_Geo`; szczelne, bez n-gonów, transformacje zamrożone, pivot 0,0,0; **przód +Z, góra +Y**; poza I/A/T | create.roblox.com/docs/art/characters/specifications |
| Kości R15 | `Root > HumanoidRootNode > LowerTorso > UpperTorso > Head …` (jak wyżej); Root i LowerTorso „w 0,0,0”; brak wpływów na Root; maks. 4 wpływy | jw. |
| Budżety ciała | Head 4000, Torso (Upper+Lower) 1750, każda ręka i noga 1248, **razem 10 742** trójkątów | jw. |
| Wymiary ciała (studs, szer/wys/głęb) | Head 0,05/0,5/0,05 … 4/2/4; Arm i Leg … 4/4,5/4; Torso 0,05/0,65/0,05 … 4/4/4; **całość 1/4/0,5 … 8/10/4** | jw. |
| Zaczepy ciała | 19 siatek `_Att`: Head 4 (FaceCenter, FaceFront, Hat, Hair), UpperTorso 5 (Left/RightCollar, Neck, BodyBack, BodyFront), LowerTorso 4 (Root — „0,0,0”, WaistFront, WaistBack, WaistCenter), Left/RightShoulder, Left/RightGrip (obrót 90,0,0 w pozie I), Left/RightFoot; importer zamienia `_Att` na `…Attachment` | jw. + /docs/art/characters/export-settings |
| Skala ciała | Normal → typ rigu „Rthro”, Slender → „Rthro Narrow”, **Classic → „Default”** (Classic ok. 4,75 studa, Normal 5,75–6,5) | jw. + /docs/art/accessories/specifications |
| Akcesorium sztywne | **jedna siatka, ≤ 4000 trójkątów**, szczelna; mieści się w pudełku typu wokół zaczepu; Classic: Hat 3×4×3, Hair 3×5×3,5 (2 w górę/3 w dół, 1,5 przód/2 tył), Face 3×2×2, Neck 3×3×2, Shoulder 3×3×3 (na NeckAttachment 7×3×3), Front 3×3×3, Back 10×7×4,5 (1,5 przód/3 tył), Waist 4×3,5×7 (1,5 w górę/2 w dół); **importu zaczepów z zewnętrznych narzędzi dla akcesoriów sztywnych nie ma** (Attachment w Handle robi się w Studio) | create.roblox.com/docs/art/accessories/specifications |
| Tekstury | Marketplace ≤ 2048×2048 (większe zmniejszane); w pracy bezpiecznie ≤ 1024 | jw. + notatka właściciela „Z Blendera do Robloxa” |
| Blender → FBX | Units: System **None**, 1 jednostka = 1 stud; **Apply Scalings = FBX Unit Scale**; **Forward = Z, Up = Y**; Path Mode Copy + Embed Textures; Custom Properties on; **Add Leaf Bones off**; Bake Animation tylko dla animacji (NLA Strips, All Actions, Force Start/End off, Simplify 0, zakres osi czasu obejmuje klucze); w szkielecie 15 siatek i 19 zaczepów | /docs/art/blender, /docs/art/characters/export-settings, /docs/art/modeling/export-requirements |
| Import do Studio | File → Import 3D: Scale Unit = Stud, World Forward = Front, World Up = Top; glTF nie wymaga poprawek skali | /docs/art/blender |
| Animacja z FBX | Animation Editor na rigu: **⋯ > Import > From FBX Animation** (w dokumentacji emotek i starszych wersjach: *From File*) (.fbx); emote < 10 s i musi odnosić się do standardowego rigu R15 | /docs/avatar/emotes/import, /docs/avatar/emotes/specifications |
| Stawy w grze | `Humanoid:BuildRigFromAttachments()` łączy części przez pary zaczepów o nazwach kończących się na `RigAttachment` | /docs/reference/engine/classes/Humanoid |

## Czego biblioteka NIE gwarantuje
- **Import siatek (FBX/GLB) do Roblox Studio nie był testowany** — wymaga uploadu, który robi człowiek. Kontrola sprawdza tylko zgodność eksportu z Blenderem (wczytanie z powrotem).
- **Kierunek po imporcie.** Eksport FBX idzie z Forward = Z, Up = Y (zalecenie Roblox dla Blendera), co obraca model o 180° wokół pionu: w pliku FBX postać patrzy w −Z (= LookVector w Roblox). Specyfikacja ciał awatara mówi jednocześnie „przód +Z” (konwencja Maya). Przy pierwszym imporcie sprawdź, w którą stronę patrzy postać. GLB zachowuje układ danych (przód +Z).
- **`Root_Att` i pozycje kości R15.** Dokumentacja każe trzymać Root, LowerTorso i Root_Att „w 0,0,0”; biblioteka czyta to jako zerowe przesunięcie lokalne (LowerTorso = HumanoidRootNode w stawie bioder, Root na ziemi). Do potwierdzenia przy pierwszym imporcie ciała.
- **Ciało awatara na Marketplace**: brak klatek (`_OuterCage`), brak sprawdzenia „wypełnienia 50% skrzynki”, bryły w jednej siatce przenikają się (nie są zszyte w jedną powłokę — szczelna jest każda bryła z osobna). Do NPC i postaci w grze to wystarcza; do sprzedaży ciała trzeba więcej.
- **Kolory w Studio**: tekstura-paleta działa jako `TextureID`/`SurfaceAppearance.ColorMap`; metaliczność, szorstkość i emisję trzeba podpiąć ręcznie z PNG. Nie wiadomo, czy importer czyta kolory wierzchołków.
- **Akcesoria**: plik ma punkt zaczepienia w (0, 0, 0), ale `Attachment` w uchwycie (`Handle`) trzeba utworzyć w Studio. Gotowe liczby (minus `srodek_skrzynki_od_zaczepu` z raportu, osobno dla GLB i FBX) są w `../przedmioty.json` (`czesci[].attachment`), a tworzy je skrypt `../zaczepy_akcesoriow.luau` — oba nie były sprawdzone w Studio. Broń jako `Tool` (Grip) — ręcznie.
- **Obrys** (komiksowa „tusz”-linia) to wyłącznie efekt renderu w Blenderze — nie ma go w FBX/GLB. W grze obrys robi np. `Highlight`.
- Gotowe klipy R15 (`chod`, `atak` …) są szkicami do przerobienia, nie zatwierdzoną animacją.

## Pułapki (sprawdzone na Blenderze 5.0.1)
- Nowy atrybut siatki może przenieść w pamięci pozostałe warstwy: wynik `uv_layers.new()` po `color_attributes.new()` jest nieważny i zapis przez niego psuje stertę (crash `0xC0000374`/`0xC0000005` w `tbbmalloc.dll`). W `siatka()` każda warstwa jest wypełniana od razu i pobierana świeżo po nazwie.
- Importer glTF dokłada pomocniczy kształt kości (`Icosphere`, kolekcja `glTF_not_exported`) — kontrola go pomija.
- FBX po ponownym wczytaniu ma klip w klatkach 1…N+1 (przesunięty o 1) — długość się zgadza.
- Blender pod blokadą: blokada starsza niż 12 min jest uznawana za porzuconą — nie puszczaj jednego wywołania z wieloma długimi filmami.
