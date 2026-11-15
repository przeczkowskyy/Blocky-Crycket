# swiat/biom_las — Biom Las „Bór Pod Ukłonem” (mapa z klocków)

Pierwszy biom gry: las 1000 × 1000 studów, 6 podbiomów, 24 lokacje, 16 stref potworów, 4 patrole, troll i strażnik.
**Wersja 2 mapy (15.11):** ten sam układ, nowe faktury z wbudowanych materiałów Roblox i detale tam, gdzie chodzi gracz
(kontrakt, rozdz. 14–15). **Zbudowana w Studio** (`Workspace/BiomLas`), faktury dobrane na zrzutach ze Studio (rozdz. 16),
potem przegląd świeżym okiem na zrzutach ze Studio i poprawki jeziora, labiryntu, rantu półek i drobiazgów (rozdz. 17).
Kontrakt (co i dlaczego): [`PROJEKT.md`](PROJEKT.md). Notatka w sejfie: `B&C/Gra/Biom Las.md`. Status: **propozycja**.

## Pliki

| Plik | Co to jest |
|---|---|
| `uklad.json` | podbiomy, lokacje, ścieżki, woda, **teren** (poziomy, kopce, rampy), strefy spokoju, piny |
| `potwory.json` | strefy potworów z węzłami walki i domami, patrole, troll, strażnik, zasady |
| `ujecia.json` | ujęcia kontrolne w układzie lasu |
| `geo.py` | geometria i model wysokości `Teren.H(x, z)` — wspólny dla budowy, kontroli i planu |
| `wezly.py` | liczy węzły walki i domy z maski terenu i zapisuje je w `potwory.json` |
| `sprawdz.py` | kontrola układu (wielokąty, uskoki, urwiska na drogach, węzły, pojemność, domy, kontrast, czasy) |
| `generuj.py` | generator mapy → `czesci.json`, `znaczniki.json`, `ujecia_swiat.json` |
| `teren.py`, `rosliny.py`, `skaly.py`, `lokacje/*.py`, `paleta.py` | moduły budowy: teren i woda, rodziny roślin i skał, lokacje (jeden plik na podbiom, Ukłon osobno), kolory |
| `detale.py` | wersja 2: drobiazgi przy ścieżkach, kępy runa i kłody, garby terenu, rekwizyty przy lokacjach (gęstości w tabelach na górze pliku) |
| `faktury.py` | wersja 2: rola części → materiał Roblox i korekta jasności koloru (jedna tabela `ROLE`); `generuj.py` nakłada ją na całą mapę |
| `czesci.json` | **wynik**: 22 419 części w układzie świata Studio (kontener `Workspace/BiomLas`, środek (0; 0; −2000), obrót 180°) |
| `znaczniki.json` | **wynik** dla kroku „potwory w Studio”: strefy, węzły z wysokością, domy, patrole, troll, strażnik, punkty E, piny, grupy stale wczytane i z niskim detalem (w układzie lasu) |
| `ujecia_swiat.json` | **wynik**: ujęcia przeliczone do świata (Blender, zrzuty ze Studio) |
| `ujecia_przeglad.json` | 10 ujęć przeglądu z oczu gracza (już w świecie): środki podbiomów, ściana rynny, labirynt, jezioro, przejścia między podbiomami |
| `plan.py` → `podglad/plan.png`, `podglad/plan_telefon.png` | plan z góry dla ludzi (pełny z legendą i sama mapa na telefon) |
| `podglad/01…20_*.jpg` | wybrane rendery z Blendera (rzut z góry obrócony: północ lasu u góry; 13–20 to kadry detali wersji 2). Blender nie pokazuje faktur Roblox — tylko geometrię |
| `podglad/studio_*.jpg` | **zrzuty ze Studio** (prawdziwe faktury i oświetlenie miejsca; 12 kadrów po etapie 3) i dwa zestawienia przed–po etapu 3 (labirynt, jezioro) |
| `studio_atrybuty.py` | ustawia w Studio streaming grup z `znaczniki.json` (tylko w kontenerze `BiomLas`) |

## Polecenia (z głównego folderu repozytorium)

```
# 1. (po zmianie terenu albo stref) węzły walki i domy — trwa ok. 2 min
python -B swiat/biom_las/wezly.py --zapisz

# 2. kontrola układu (kod 1 = błąd)
python -B swiat/biom_las/sprawdz.py

# 3. mapa z klocków (ok. 15 s): czesci.json, znaczniki.json, ujecia_swiat.json + raport części, materiałów, detali
#    i kontrola placów walki (kod 1 = plac walki zajęty albo część bez roli w faktury.py)
python -B swiat/biom_las/generuj.py

# 4. podglądy w Blenderze (Blender w tle, wspólna blokada; ok. 4 min na 28 ujęć)
python swiat/biblioteka/podglad.py --json swiat/biom_las/czesci.json --ujecia swiat/biom_las/ujecia_swiat.json --wyj <folder> [--tylko l03,l06] [--szer 1400 --probki 32]

# 4a. podgląd ze strefami potworów (czerwone place walki r 12, zastępcze bryły w skali, domy) — nie nadpisuje czesci.json
python -B swiat/biom_las/generuj.py --znaczniki-widoczne --wyj <folder>/czesci_znaczniki.json
python swiat/biblioteka/podglad.py --json <folder>/czesci_znaczniki.json --ujecia <folder>/ujecia_swiat.json --wyj <folder> --tylko l03

# 5. plan z góry
python -B swiat/biom_las/plan.py
python -B swiat/biom_las/plan.py --telefon --szer 1200
```

Pułapka Windows: uruchamiaj z `PYTHONIOENCODING=utf-8`. Wymagane: numpy (maski), Pillow (plan), Blender 5 (podglądy).
Rzut z góry `l03_mapa_gora.jpg` jest w układzie świata — obróć o 180°, żeby północ lasu była u góry.

## Budowa w Studio (zrobiona 15.11)

Las stoi w Studio w kontenerze **`Workspace/BiomLas`** (atrybut `Wygenerowane`, środek (0; 0; −2000), obrót 180°).
Pudło x −700…700, z −1300…−2700 przed budową było puste (dokładny test skrzynek otaczających: 0 cudzych części;
Baseplate kończy się na z −1024). Jak powtórzyć (z głównego folderu repozytorium; Studio w trybie **Edit**):

```
python -B swiat/biom_las/sprawdz.py
python -B swiat/biom_las/generuj.py
# budowa: kasuje TYLKO stary kontener z atrybutem Wygenerowane, punkt historii przed i po; ok. 75 paczek po 300 części
python -B tools/studio_buduj.py swiat/biom_las/czesci.json --paczka 300 --czekaj 20
# streaming grup z znaczniki.json: Punkty/* → ModelStreamingMode Persistent, kępy lasu, mur, tło → LevelOfDetail StreamingMesh
python -B swiat/biom_las/studio_atrybuty.py
# zrzuty z tych samych ujęć co podglądy Blendera (28 ujęć, ok. 2 min; --tylko _detal_ = l21–l28)
python -B tools/studio_zrzuty.py swiat/biom_las/ujecia_swiat.json --przesun 0,0,0 --wyj <folder> --czekaj 20 --rozmiar 1600
# 10 ujęć przeglądu z oczu gracza (etap 3)
python -B tools/studio_zrzuty.py swiat/biom_las/ujecia_przeglad.json --przesun 0,0,0 --wyj <folder> --czekaj 20 --rozmiar 1600
# usunięcie lasu ze Studio (cofa się też jednym Ctrl+Z)
python -B tools/studio_buduj.py swiat/biom_las/czesci.json --usun
```

`--czekaj N` (nowa, opcjonalna opcja obu narzędzi): gdy ktoś inny testuje w trybie Play, narzędzie czeka do N minut
i ponawia (paczka w Play nie wykonuje się wcale, więc ponowienie jest bezpieczne). `--rozmiar` zmniejsza zrzut (JPG < 2 MB).
Narzędzia niczego nie publikują i nie zapisują miejsca; Lighting i ustawienia miejsca zostają bez zmian.

Zrzuty ze Studio: `podglad/studio_01…12_*.jpg` (12 najlepszych po etapie 3) i `podglad/studio_przed_po_*.jpg` (ten sam kadr
ze Studio przed i po etapie 3: labirynt, jezioro). Dalej do zrobienia: pomiar na telefonie przy streamingu i kontrola kolizji
(oba wymagają trybu Play).

## Liczby

22 419 części (limit 25 000, rezerwa ok. 2,6 tys.; v1: 13 353; przed etapem 3: 22 366): Ostępy 4848, Łąka 3460,
Korona 3028, Kapeluszowo 2923, Wąwóz 2805, Serce 1199, Mur 1160, Ścieżki 1156, Woda 623, Tło 545, Teren 410, Punkty 142,
Piny 60, Chmury 60. Neon 85, przezroczyste 13 (tafle stawów i mgła; jezioro od etapu 3 nieprzezroczyste), z kolizją 16%,
bez cienia 66%. Materiały: SmoothPlastic 61,6% (głównie liście), Grass 9,0%, Wood 8,4%, Rock 6,4%, Ground 2,5%,
Sandstone 2,4%, Limestone 2,1%, Fabric 2,0% (jeżyny), Slate 1,5%, LeafyGrass 1,4%, Cobblestone 0,9%, WoodPlanks 0,9%,
Neon, Mud, Pebble, Metal, Sand po ≤ 0,4%.
**W Studio:** 22 419 części (BasePart) i 22 678 instancji w kontenerze (części + 259 folderów i modeli grup), 8 grup
Persistent, 88 grup StreamingMesh. Detale: 5 566 części (drobiazgi przy ścieżkach, kępy runa, 52 kłody, 84 garby,
62 rekwizyty). Ścieżki 6,6 tys. studów, do Ukłonu 26 s, do Kręgu 66 s.
Potwory: 64 naraz w strefach (do 86) + 4 patrole + troll + strażnik.

## Przegląd świeżym okiem (15.11, 3 rundy podglądów)

Poprawione: kryształ Kręgu urósł do ok. 95 n.p.m. (był za mały — z Rozstaju go nie było widać), menhiry i filar z łupku
z czapami mchu (były beżowe jak posadzka), ściany labiryntu z garbatym wierzchem z liści i jagodami, pod sosnami Ostępów
ciemne igliwie (place walki wyglądają jak jaśniejsze polanki), stopa Ukłonu z przyporami i korą, jama wilka z liśćmi
i kijem, okrągłe końce ścieżek (koniec szlaku przy bramie wystawał trójkątem), kwiaty i głazy przed Ławką, ujęcie
`l11_rozstaj` przesunięte (sowa zasłaniała kryształ). Rozdz. 0a kontraktu.

## Wersja 2 mapy: faktury i detale (15.11)

Uwaga Karola: „mapa logistycznie bardzo dobra, ale popracowałbym nad lepszymi teksturami i detalami”. Układ, podbiomy,
lokacje, ścieżki i strefy potworów bez zmian. Zrobione: materiał według roli części (`faktury.py`; liście, grzyby, woda,
tusz i kody zostają gładkie), drobiazgi przy ścieżkach i runo (`detale.py`), warstwy, szczeliny, zwisy i piarg na ścianach
urwisk, garby i zwisy liści na licach labiryntu, ciemne runo boru w Ostępach z jaśniejszymi placami wilków, nieregularne
plamy-podkładki zamiast kół, półprzezroczyste stawy i jezioro z jasną płycizną, 3–4 sylwetki drzew w każdym podbiomie,
garby terenu, rekwizyty przy lokacjach (bez napisów). Szczegóły i liczby: kontrakt, rozdz. 14–15.

## Faktury po zrzutach ze Studio (15.11, 4 rundy)

Próbka 40 płytek (ten sam kolor w różnych materiałach) i 3 × 28 zrzutów. Zmiany w `faktury.py` (rozdz. 14 i 16 kontraktu):
ściany Wąwozu, tama i rampy (Sandstone) z różowobiałego „marmuru” na ciepłą ochrę (ton zamiast jasności); uskoki Korony
(Limestone) przygaszone do beżu; głazy i kamyki (Rock) ciemniejsze i cieplejsze; łupek bez rozjaśnienia (był lawendowy);
wierzch półek Wąwozu z Sand (wyglądał jak plaża z falkami) na suchą trawę (Grass w tonie słomy); jeżyny z LeafyGrass
(„granit z rudymi liśćmi”) na Fabric (drobny splot, komiksowo czysty fiolet); zielone zwisy na licach labiryntu gładkie;
stawy bardziej przezroczyste, jezioro z ciemniejszą taflą (głębokie, inne niż jasna struga); kwiaty-kostki spłaszczone w talerzyki (wyglądały jak kostki do gry).

## Przegląd świeżym okiem na zrzutach ze Studio (etap 3, 15.11)

38 zrzutów ze Studio (28 kontrolnych + 10 z oczu gracza w nowych miejscach), 3 rundy. Poprawione (rozdz. 17 kontraktu):
- **jezioro**: nieprzezroczysta tafla bez szwów, na niej jasny pas płycizny i 4 ciemne plamy głębi (jak Oczko), trzcina
  w kępach zamiast „płotu” co 7 st, więcej zmarszczek; przezroczystych części 33 → 13;
- **labirynt**: zielone zwisy-prostokąty → kliny liści ostrzem w dół (postrzępiony skraj), czoła rzędów bez ciemnozielonych
  płyt, ciemny odrost u stopy lica, kości przeniesione z korytarza i placu walki pod ścianę polanki;
- **rant półek Wąwozu**: darń na skałach rantu (zamiast dużych gładkich jasnych płyt);
- **wierzch półek**: oliwkowe kępki, nowe krzaczki, gęściej przy ścieżkach;
- **kwiaty**: kępka-klin i grzbiet łanu z dwóch klinów zamiast zielonej „cegiełki z kafelkiem”;
- **garby** o połowę mniej (prawie niewidoczne) — budżet bez wzrostu (+53 części).

## Znane słabości

- **Jezioro** (po etapie 3) jest jasne i nasycone jak komiksowa woda; z brzegu plamy głębi widać dopiero dalej. Terrain Water
  byłoby wyjściem poza klocki (decyzja właściciela).
- **Labirynt**: lepszy rytm (zwisy, odrost), ale z bliska nadal płaskie fioletowe bryły.
- Polana Ukłonu: na zboczu kopca widać cienkie ciemne linie styków klinów (LeafyGrass).
- **Ścieżki**: na stykach odcinków cienka ciemna kreska (przesunięcie 0,01 przeciw migotaniu); migotanie w ruchu kamery
  niesprawdzone (zrzut to jedna klatka).
- LeafyGrass na runie ma rude listki — w Kapeluszowie i Ostępach czyta się jak ściółka, ale z bliska to szum.
- Chmury (kule z biblioteki) przy niskim kadrze wyglądają jak balony.
- Z daleka las nadal trochę jak makieta (brak mgły — wybór dla ludzi nr 7; propozycja w rozdz. 16 kontraktu).
- Niezmierzone: telefon (22,4 tys. części), streaming, kolizje na klinach, kłodach i darni rantu — wymagają trybu Play.
- `sprawdz.py` ma 2 ostrzeżenia (rozdz. 13 kontraktu).
