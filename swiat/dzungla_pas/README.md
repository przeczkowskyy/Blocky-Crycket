# swiat/dzungla_pas — Dżungla jako odcinek wąskiego pasa (plan z klocków)

Status: **propozycja** (18.11.2026) — nic tu nie jest kanonem i **w Studio nic nie jest zbudowane**. Plan, generator,
kontrola i podglądy offline, tak jak Bagno-pas (`swiat/bagno_pas/`). Wymagania: D-061 (las → bagno → dżungla → …), D-075
(pas biomów), D-076 (inkubator, przegrody, strażnik otwiera następny biom), D-077 (przelot kamery), D-069 (wymagany build
nie może stać się wymaganą klasą), D-096 (długi projekt → krótka mapa gry przez `swiat/biomy/przycinarka.py`). Zarys
biomów: `swiat/biomy/PLAN_BIOMOW.md`, rozdz. „2. Dżungla — Gąszcz Pod Parasolem”.

> **W skrócie.** Robocza nazwa **„Gąszcz Pod Parasolem”**. To **długi projekt** (57,5 s × 4,5 s) ułożony **dokładnie jak
> Bagno-pas przesunięty o +940 st wzdłuż pasa** (u 1874…2820, świat X 2974…3920, oś z = −700), żeby przycinarka zostawiła
> z niego te same odcinki co z Bagna (+940) i zrobiła krótką mapę gry (25 s × 4 s). Przez całą Dżunglę biegnie **Dróżka**
> z ubitej ziemi (w ruinach i w Kręgu z kamiennych płyt), nad nią tu i ówdzie **olbrzymie liście-parasole**; po bokach
> piętra zieleni: podszyt z kwiatami i paprociami → paprocie drzewiaste, palmy i kępy liści → drzewa-olbrzymy z koronami-
> parasolami i figowce, liany i wiszące mosty z lian; turkusowe strumienie z kaskadami, ruiny i posągi z jarzącymi się
> oczami. Układ: Taras Przybycia z inkubatorem → **Polana Zwijogonów** (Zwijogon, Zwiadowca) → **Kwietnik Gębokwiatów**
> (Gębokwiat, Mag) → **Gaj Kokosów** (Kokosowy Siłacz, Wojownik) → **Ruiny Pancernika** (Pancernik Ruin, rzadki) → **Krąg
> Stu Lian** (Wąż Stu Lian) → brama do Pustyni. **9 305 części**, kontrola **0 błędów, 0 ostrzeżeń**.

## Położenie w pasie

- Układ pasa jak w lesie-pasie i Bagnie: u wzdłuż, v w poprzek (v > 0 po prawej ręce idącego do bramy), świat Studio =
  (1100 + u; y; −700 + v), **bez obrotu**. Pole gry 72, kulisy po 24, niewidzialna ściana |v| = 38.
- Z planu Bagna (`swiat/bagno_pas/plan_bagna.json`) wzięte: brama do Dżungli **u 1874** (palisada Bagna u 1872–1877
  zostaje częścią `Workspace/BagnoPas`), rezerwacja Dżungli **u 1880…2820**, punkt przybycia **„dzungla” u 1894**, patrzy
  na u 1940. Brama do Pustyni **u 2814** (1874 + 940), Pustynia zaczyna się na u 2820 (rezerwacja z planu Bagna).
- Części Dżungli: **u 1876…2846** (X 2976…3946), |v| ≤ 90. Płyta Dżungli od u 1906 (płyta Bagna kończy się na 1906).
  Kulisy Dżungli od u 1910 — kulisy Bagna do u 1906 zostają jako skraj Bagna za bramą.
- **Przed budową trzeba usunąć `Workspace/BagnoPas/ZapowiedzDzungli`** (u 1876–1906, z niewidzialną ścianą na u 1905 —
  stoi tam, gdzie Taras Przybycia). Kontrola sprawdza, że nic z Dżungli nie wchodzi w resztę części Bagna-pasa (za bramą
  Bagna zostają koniec Krzywej Kładki z palami i drobiazgami — dlatego Taras Przybycia ma 10 × 7,6, nie 12 × 12).

### Zgodność z Bagnem (+940) i przycinarka

Wszystkie liczby wzdłuż pasa w `plan.py` są zapisane jako „liczba Bagna + D” (D = 940); `sprawdz.py` porównuje plan
z planem Bagna (433 porównania: pas, przegrody i kojce, przejścia z otwarciami i wodą, miejsca, punkty orientacyjne,
strefy z pętlami, domami i polami, Strażnik i arena, strefy spokoju, przelot). Odcinki, które przycinarka zostawi
(Bagno + 940): `[[1874,1924],[1944,2020],[2148,2232],[2360,2440],[2568,2702],[2728,2796],[2802,2846]]` — zawierają
przybycie, pierwszy kojec każdej przegrody z przejściem przed nim, leże, Krąg i bramę (kontrola to sprawdza). Wpis do
`swiat/biomy/wymiary_pasa.json` (robi go właściciel przycinarki, nie ten pakiet): `kotwica_u` 1894, `po_biomie` "bagno",
`wejscie_u` 1874, `brama_u` 2814, `strefy` {z1: z1–z3, g1: g1–g3, o1: o1–o3, t1: t1}; Bagnu dochodzi
`pomin_grupy: ["ZapowiedzDzungli"]`. Próba w pamięci (bez zapisu): 9 305 → ok. 5 170 części, przybycie → brama 25,0 s.

## Pliki

| Plik | Co to jest |
|---|---|
| `plan.py` → `plan_dzungli.json` | plan w formacie planu Bagna (pas, przegrody, przejścia, miejsca, strefy, Strażnik, przelot, punkty przybycia, czas) + opisy potworów; `python -B swiat/dzungla_pas/plan.py` drukuje czasy i strefy |
| `kontekst.py` | klasa `Dzungla` (dziedziczy `las_pas.kontekst.Pas`), `ZasadyDzungli` (dziedziczy `las_pas.zasady.Zasady`, + styk z Bagnem), oś Dróżki, paleta Dżungli `KOLORY_DZUNGLI` (prefiks `dz_`) |
| `rosliny.py` | rodziny roślin Dżungli (lista niżej) — do pożyczenia przez arenę walki |
| `teren.py` | płyta, plamy gruntu, strumienie i sadzawka bez kolizji, polanki, posadzka ruin, grządki i żywopłoty Kwietnika, Dróżka i mostki, wydeptane pętle, plamy światła, mgiełka, liście na wodzie |
| `miejsca.py` | Taras Przybycia (+ Kamień Powrotu i stanowisko jajka z lasu-pasa), punkty orientacyjne, przejścia, domy potworów, rekwizyty, liście-parasole nad Dróżką, Krąg Stu Lian, brama do Pustyni, zapowiedź Pustyni; małe rzeczy ruin (posąg-głaz, głowa posągu, kolumna, stela, pochodnia, stos kokosów, kaktus, mur ruin) |
| `kulisy.py` | kulisy (skraj, przód z kolizją, drugi rząd, głąb) z lianami między drzewami, wiszące mosty z lian, ruiny w kulisach, tło, niewidzialne ściany, drobiazgi przy Dróżce, runo |
| `generuj.py` | generator → `czesci.json`, `znaczniki.json`, `plan_dzungli.json` + raport (kod 1 = część bez roli faktury albo limit); nowe nazwy części → `FAKTURY_DZUNGLI` |
| `sprawdz.py` | **kontrola offline** (kod 1 = błąd) |
| `podglad.py` | **podgląd bez Blendera** (rysownik lasu-pasa) → `podglad/*.jpg` (≤ 1280 px) + `ujecia_swiat.json` |
| `czesci.json` | wynik: 9 305 części, format `swiat/biblioteka/scena.py` (`biblioteka-v2`), kontener `Workspace/DzunglaPas` |
| `znaczniki.json` | wynik: te same rodzaje znaczników co Bagno; brama na końcu to `brama_pustyni` (grupy `BramaPustyni/Wrota` i `BramaPustyni/Palisada`) |
| `podglad/` | `gora.jpg`, `gora_strefy.jpg` (rzut z góry), `polana`, `kwietnik`, `gaj_ruiny`, `krag_brama` (z ukosa), `oczy_przybycie`, `oczy_gaj`, `oczy_krag` (z oczu gracza) |

## Polecenia (z głównego folderu repozytorium)

```
python -B swiat/dzungla_pas/generuj.py     # ok. 3 s: plan_dzungli.json, czesci.json, znaczniki.json, raport
python -B swiat/dzungla_pas/sprawdz.py     # ok. 3 s: kontrola (woła też tools/studio_buduj.py --sucho)
python -B swiat/dzungla_pas/podglad.py     # ok. 35 s: podglad/*.jpg i ujecia_swiat.json (--tylko gora,polana; --wyj <folder>)
python -B swiat/dzungla_pas/plan.py        # sam plan + tabela czasów
```
Wynik deterministyczny (`--ziarno 11`). Wymagane: numpy, Pillow. Bez Blendera i bez Studio. Generator i kontrola czytają
`swiat/bagno_pas/plan_bagna.json` i `czesci.json` (zgodność +940 i styk z Bagnem) — po zmianie Bagna uruchom generator
Dżungli jeszcze raz.

## Plan (u w układzie pasa; bieg 16 st/s)

| Odcinek | u | Bieg przez | Od przybycia | Co tam jest |
|---|---|---|---|---|
| brama Bagna (Bagno-pas) | 1874 | — | — | palisada Bagna za plecami przybywającego |
| **Taras Przybycia** (strefa spokoju) | 1880–1944 | 4,0 s | 0 s | kamienny taras 10 × 7,6 z rombem światła (u 1894), stanowisko jajka na posadzce (1912; 22) ze świecącymi kwiatami, Kamień Powrotu (1888; −24), łąka, pochodnie |
| Turkusowy strumyk | 1944–1956 | 0,8 s | | płytki strumyk w poprzek pasa, mostek z desek 12 szer. z linami z lian, kamienie brodu |
| **Polana Zwijogonów** (3 kojce po 64) | 1956–2148 | 12,0 s | 3,9 s | słoneczne polanki w ciemnym runie, plamy światła, paprocie, kłody, posągi-głazy; **Chatka na Drzewie** (2084; 30, wys. 25) |
| Mostek nad Kaskadą | 2148–2168 | 1,3 s | | głębszy strumień z kaskadami z pięciu skalnych progów w kulisach, kamienny mostek 12 z balustradą ≤ 1,4 |
| **Kwietnik Gębokwiatów** (3 kojce) | 2168–2360 | 12,0 s | 17,1 s | wilgotna ziemia, mchowe polanki, grządki i żywopłoty kwiatowe 0,8 między kojcami (przerwa 24), świecące kwiaty; **Wielki Kielich** (2296; 32, wys. 21) |
| bambusowa przesieka | 2360–2376 | 1,0 s | | ściany bambusa 5–6 wys., przejście 32 |
| **Gaj Kokosów** (3 kojce) | 2376–2568 | 12,0 s | 30,1 s | piaszczysta ziemia, palmy pod ścianami, stosy kokosów, pniaki palm; **Kaskada Gaju** (2504; 30, wys. 25) — wodospad do sadzawki |
| omszałe schody | 2568–2584 | 1,0 s | | mur ruin 6–9 wys. ze stopniami na froncie, przejście 28 z kamiennym progiem 0,4, stele ze znakiem |
| **Ruiny Pancernika** | 2584–2684 | 6,2 s | 43,1 s | spękana posadzka, złamane kolumny, głowy posągów, stele, kości; **Zapadła Kaplica** (2664; −30, wys. 17) |
| Brama Posągów | 2684–2700 | 1,0 s | | dwa posągi strażników 13 (2692; ±16) z jarzącymi się oczami i kamiennym kapturem, niskie korzenie |
| **Krąg Stu Lian** | 2700–2788 | 5,5 s | 50,4 s | okrągła kamienna posadzka r 27 (wierzch 0,3) — wyspa w turkusowej sadzawce, 8 filarów z lianami na r 26, Wąż w (2754; 0); **Świątynia Stu Lian** (2788; 27, wys. 34) z boku osi |
| przedbramie (strefa spokoju) + brama do Pustyni | 2788–2820 | 2,0 s | | ławka, pochodnie, skrzynie; mur ruin z omszałych bloków, filary ze znakiem słońca, wrota 16 (u 2814) |
| zapowiedź Pustyni (osobna grupa) | 2816–2846 | | | piasek, wydmy, kaktusy, piaskowe głazy, czaszka, palma oazy, niewidzialna ściana u 2845 |

Od przybycia (u 1894) do bramy do Pustyni (u 2814): **57,5 s**; sąsiednie miejsca walki dzieli **4,0–7,5 s** (jak w Bagnie).

## Potwory (modele już są: `swiat/postacie/<model>.py`, dane aktorów `swiat/test_walki2/dane/<model>.json`)

Pętle i domy jak w Bagnie: pętla 8 węzłów 36 × 44 (obwód 138), dwa domy pod ścianami (|v| = 34), leże — pętla 6 węzłów.
Odstęp 25, smycz 10, plac walki r 12.

| Strefy | Potwór (model) | Klasa | Wymiary (st, z danych aktorów) | Poziomy: plan / równy | Naraz / max | Odrodzenie |
|---|---|---|---|---|---|---|
| z1 · z2 · z3 | **Zwijogon** (`zwijogon`) | Zwiadowca | wys. 3,5, dł. 5,4 | 17 · 17–18 · 18 / 25–26 · 26–27 · 27–28 | 4 / 5 | 12 s |
| g1 · g2 · g3 | **Gębokwiat** (`gebokwiat`) | Mag | wys. 5,1, szer. 3,7 | 19 · 19–20 · 20 / 28–29 · 29–30 · 30–31 | 4 / 5 | 15 s |
| o1 · o2 · o3 | **Kokosowy Siłacz** (`kokosowy_silacz`) | Wojownik | wys. 7,1, szer. 6,4 | 21 · 21–22 · 22 / 31–32 · 32–33 · 33–34 | 3 / 4 | 18 s |
| t1 | **Pancernik Ruin** (`pancernik_ruin`, rzadki) | Wojownik | wys. 4,4, dł. 7,4 | 22 / 34 | 1 / 1 | 150 s stałe |
| — | **Wąż Stu Lian** (`waz_stu_lian`, strażnik) | pół na pół fiz. i mag. | 17,3 w zwoju, szer. 11 | 23 / 35 | 1 | 120 s stałe |

Poziomy w `poziomy` rosną 17 → 23 przez przegrody (zlecenie; gra i tak nadpisuje poziomy swoimi), w `poziomy_rowny` —
tempo równe z PLAN_BIOMOW (25–35). **D-069:** trzy przegrody = trzy klasy (kontrola). Nacisk Dżungli (PLAN_BIOMOW): zwinni
przeciwnicy, uniki i krwawienie → Szczęście i Kondycja; Kokosowy Siłacz i Pancernik twardzi fizycznie, Gębokwiat rani
magią. Czasy walk w planie to **szacunek** (19 / 18 / 23 / 28 / 34 s).

## Paleta (klucze `dz_*` w `kontekst.KOLORY_DZUNGLI`)

- Grunt, podłoże, droga jak makieta krain (`swiat/teleport_chmury/krainy.json`, kraina dzungla): **2FA34A / 5C3A22 / B07A44**.
- Liście i polanki z planu: 2FA34A, 6CCB4A, ciemny liść 1F7A36; liany 3E7D2E; bambus 9DBF4A / 6E8F32.
- Korony i runo przyciemnione w stronę areny Dżungli (`swiat/areny_walki`, grunt 2E7D3A / 3F9A45): spód korony 236E33,
  korona 2E8A3E, wierzch 5CAC3F, runo 2E7D3A / 3F9A45, runo pod kulisami 235E2E; sylwety tła 2F6B3A / 568E5E / 8DB894.
- Woda turkus 2EC4B6 (głębia 1C9A92, spadająca woda 8FE3EC, piana EFFCF8); kwiaty E5392B / F2B030, świecące (Neon, jak
  arena) FF5FA2 / FFD84A; owoce F08A24; kokosy 6B4526; kamień ruin jak arena 8E9A82 / 667260 / B5BDA3, mech 5DAA45,
  złoto C9A44A, znaki (Neon) 3FE0D0; plamy światła D9E27A; mgła 8FC79A; zapowiedź Pustyni F2CC7E / C08A55 / D9A85E.

## Rośliny do pożyczenia (`swiat/dzungla_pas/rosliny.py`)

Każda funkcja buduje w bieżącym układzie (pos = podstawa, ry = obrót, k = skala) i zwraca (wysokość, promień); kolory to
klucze `dz_*` — kto pożycza, dokłada `KOLORY_DZUNGLI` do swojej palety.
`lisc_parasol(s, rnd, pos, k=1.0, ry=0.0, f=1.0, wychyl=0.0, wys=None, prosty=False)` ·
`kepa_parasoli(s, rnd, pos, k=1.0, ry=0.0, f=1.0, n=3)` · `liana(s, rnd, p1, p2, zwis=1.5, grub=0.35, liscie=2, kolor="dz_liana")` ·
`liana_zwis(s, rnd, pos, h, grub=0.3, liscie=1, kolor="dz_liana")` ·
`drzewo_dzungli(s, rnd, pos, k=1.0, ry=0.0, f=1.0, liana_=True, korzenie=3, tusz=True)` ·
`figowiec(s, rnd, pos, k=1.0, ry=0.0, f=1.0, owoce=True)` · `palma(s, rnd, pos, k=1.0, ry=0.0, f=1.0, liscie=5, kokosy=2, proste=False)` ·
`paproc_drzewiasta(s, rnd, pos, k=1.0, ry=0.0, f=1.0)` · `bambus(s, rnd, pos, wys=6.0, n=5, ry=0.0, szer=2.6)` ·
`krzew_dzungli(s, rnd, pos, k=1.0, kwiat=None)` · `swiecacy_kwiat(s, rnd, pos, k=1.0, ry=0.0, kolor=None)` ·
`kepa_kwiatow(s, rnd, pos, kolory=("dz_kwiat_czerwony", "dz_kwiat_zolty"))` · `paproc(s, rnd, pos, k=1.0)` ·
`lisc_wodny(s, rnd, pos, r=1.0, kwiat=None)`. Ruiny i posągi (w `miejsca.py`): `posag_glaz`, `glowa_posagu`, `kolumna_ruin`,
`kamien_ze_znakiem`, `pochodnia`, `stos_kokosow`, `kaktus`, `mur_ruin`.

## Liczby

**9 305 części** (Bagno-pas 9 017; cel ok. 9 000, limit 12 000). Na odcinek: Taras 387, strumyk 132, Polana 1 701,
Mostek nad Kaskadą 158, Kwietnik 1 859, przesieka 277, Gaj 1 930, schody 148, Ruiny 1 052, Brama Posągów 175, Krąg 774,
przedbramie z bramą 417, zapowiedź Pustyni 295. Na grupę: Kulisy 4 664, Teren 775, Ozdoby 772, Detale 712, Przejścia 524,
Tło 474, Ścieżka 372, Punkty 318, Kwietnik 182, Domy 136, BramaPustyni 123, ZapowiedzPustyni 108, Arena 72. Neon 169,
kule 148, walce 593, półprzezroczyste 11 (mgiełka nad wodą), niewidzialne 5, z kolizją 7%. Materiały: SmoothPlastic 63%,
Wood 17%, Slate 7% (ruiny), Grass 6%, Ground 4%, Neon 2%.

## Co pilnuje kontrola (`sprawdz.py`, wynik 18.11: 0 błędów, 0 ostrzeżeń)

Układ = Bagno + 940 i odcinki przycinarki; plan: pojemność pętli, place walki w polu gry, domy 12–20 od węzłów, węzły
≥ 25 od przybycia, jajka i Kamienia, **D-069**, poziomy 17 → 23, wymiary potworów zgodne z danymi aktorów, jeden gracz ×1
nie czeka na odrodzenie, przelot kamery (krzywa lasu, w pasie, 3–80 nad gruntem, ≤ 120 st/s, 13,4 s, nie przez punkty
orientacyjne, kończy na Wężu, ryk 2,0 s w zatrzymaniu, każda przegroda pokazana). Części: format `tools/studio_buduj.py`
i jego `--sucho`; limity i sufity; granice u 1876…2846, |v| ≤ 90; skrzynki miasteczka i prototypów; **brak nachodzenia na
Bagno-pas** poza `ZapowiedzDzungli`; place walki r 12 wolne 1,6–18 przy 79 węzłach; Dróżka wolna 0,6–7; otwarcia pięciu
przejść; pętle; przelot kamery na częściach; grunt bez dziur (płyta Dżungli + płyta Bagna do u 1906); teren płaski; woda
bez kolizji; niewidzialne ściany (|v| = 38 od u 1904 do 2844, u 2845); wrota do Pustyni zamykają otwarcie 16 na wys. ≥ 7,
a mur bramy z kolizją domyka pas do |v| 38; punkty E; wymagane grupy i domy; znaczniki zgodne z planem; każda część ma
rolę faktury. `plan_dzungli.json` musi zgadzać się z `plan.py`.

## Budowa w Studio (następny etap, po akceptacji)

Jak Bagno (README Bagna, „Budowa w Studio”): zgłosić pracę (`praca.py start … --obszar studio:DzunglaPas --obszar
studio:BagnoPas --obszar mapa:dzungla_pas`), świeży generator i kontrola, **usunąć `Workspace/BagnoPas/ZapowiedzDzungli`**,
`python -B tools/studio_buduj.py swiat/dzungla_pas/czesci.json --paczka 300 --czekaj 20`, atrybuty streamingu
(`swiat/biom_las/studio_atrybuty.py --znaczniki swiat/dzungla_pas/znaczniki.json`: 10 grup Persistent — Punkty/* i
BramaPustyni/*, 63 grupy StreamingMesh — Kulisy/<strona>/O_* i Tlo/<strona>/O_*), zrzuty z `ujecia_swiat.json`, migawka
i raport w panelu. Gra czyta krótką mapę z `krotki/` (po przycięciu).

## Ustawienia przyjęte, do zmiany

- Kontener `Workspace/DzunglaPas`; układ = Bagno + 940; Taras Przybycia 10 × 7,6 (wierzch 0,5) zamiast pomostu 12 × 12.
- Woda to tafla bez kolizji 0,2 nad gruntem (brodzi się); Dróżka i mostki z kolizją, wierzch 0,36–0,45; posadzka Kręgu 0,3.
- Liście-parasole nad Dróżką na wys. ok. 11–13 (zasada ścieżki: nic na 0,6–7 nad Dróżką), tylko poza placami walki
  (20 sztuk — głównie na wejściu, w przejściach i nad środkami kojców).
- Mgła z części tylko nad wodą (11 ławic) + mgła lokalna u gracza: propozycja FogColor 7FBF8A, FogEnd 380 (PLAN_BIOMOW)
  albo Atmosphere jak arena Dżungli (8FC79A) — w `znaczniki.json` → `mgla`.
- Ten sam Kamień Powrotu i stanowisko jajka co w lesie i Bagnie; jajko Dżungli zrobi agent petów
  (`Punkty/StanowiskoJajka/_Interakcja`).
- Ziarno generatora 11.

## Wybory dla ludzi

1. **Nazwa:** „Gąszcz Pod Parasolem” czy inna? Nazwy przegród (Polana Zwijogonów, Kwietnik Gębokwiatów, Gaj Kokosów,
   Ruiny Pancernika, Krąg Stu Lian) — zostają?
2. **Krąg jako wyspa w sadzawce** (brodzi się do posadzki) czy sucha łąka wokół?
3. **Liście-parasole nad Dróżką:** więcej (kosztem placów walki) czy tyle?
4. **Mgiełka nad wodą z części:** zostaje czy tylko mgła lokalna?
5. **Strażnik i Pancernik:** wspólni dla serwera czy osobni dla gracza (jak w Bagnie)?

## Czego nie sprawdzono

- **Wygląd w Roblox** (podglądy to własny rysunek brył w Pillow — bez faktur, cieni, poświaty Neonu i mgły).
- **Ruch w trybie Play:** wejście na Taras (0,5), Dróżkę, mostki i próg schodów, brodzenie, kolizje wrót i muru bramy.
- **Telefon i streaming:** 9,3 tys. części obok Bagna; w grze krótka mapa (ok. 5,2 tys.).
- Styk z Bagnem w Studio (ZapowiedzDzungli) i to, czy skrypty gry Bagna dadzą się użyć dla Dżungli (pole `brama_pustyni`).

## Znane słabości

- Środek kojców jest pusty z założenia (place walki r 12) — życie dają kulisy, polanki, plamy światła i rekwizyty pod
  ścianami; liści nad Dróżką w kojcach mało (tylko nad środkiem kojca jest miejsce).
- Za bramą Bagna (u 1876–1906) leży koniec Krzywej Kładki Bagna-pasa pod Dróżką i Tarasem (w Studio trzeba zobaczyć, czy
  nie migocze).
- Kulisy z góry wyglądają jak kostki koron (jak w lesie i Bagnie); tło to proste sylwetki.
- Półprzezroczysta mgiełka może w Roblox wyglądać jak szkło.
