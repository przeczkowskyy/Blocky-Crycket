# swiat/las_pas — Las jako wąski pas (mapa z klocków)

Mapa lasu-pasa zrobiona z zaakceptowanego planu układu (`swiat/biom_las/pas/PLAN_PASA.md`, `plan_pasa.json`; plan
zaakceptował Karol 16.11.2026, ustawienia: pole gry 72 st, pas na wschód od miasteczka, stary las nietknięty,
Strażnik i Troll wspólni, walka na arenie prototypu, teleport do wejścia biomu, przelotu kamery nie da się pominąć).
**W Studio nic nie jest zbudowane** — ten etap to generator, kontrola i podglądy offline. Następny etap buduje w Studio.
Status: **propozycja**.

> **D-096 (17.11.2026):** ta mapa jest teraz **projektem** (57,5 s × 4,5 s). Gra buduje krótką mapę z `krotki/`
> (25 s × 4 s), którą robi z niej `swiat/biomy/przycinarka.py` — generator tutaj bez zmian. Plików w `krotki/` nie
> edytuj ręcznie; po zmianie projektu: `python -B swiat/biomy/przycinarka.py`.

- Kontener w Studio: **`Workspace/LasPas`** (osobny od starego `Workspace/BiomLas`). Uwaga: `plan_pasa.json` i
  `PLAN_PASA.md` piszą `PasLas` — nazwa z zamówienia tego etapu to `LasPas`; plan nie był zmieniany.
- Układ pasa: u wzdłuż (0 = początek lasu), v w poprzek (v > 0 po prawej ręce idącego do bramy). Świat Studio =
  (1100 + u; y; −700 + v), **bez obrotu**. Części stoją w pliku tam, gdzie mają stanąć w Studio: X 1066…2066,
  Z −790…−610 (u −34…966, |v| ≤ 90). Baseplate kończy się na X 1024.

## Pliki

| Plik | Co to jest |
|---|---|
| `generuj.py` | generator: plan → `czesci.json` + `znaczniki.json` + raport części (kod 1 = część bez roli faktury albo limit) |
| `kontekst.py` | plan, układ pasa, maski miejsca (węzły walki, pętle, ścieżka, zajęte), oś ścieżki `v_sciezki(u)` |
| `zasady.py` | zasady liczone na prawdziwych częściach (place walki, ścieżka, otwarcia, pętle, przelot kamery, granice) — wspólne dla generatora (wycofuje rzecz, która je łamie) i kontroli |
| `grunt.py` | płyta, plamy przegród, ścieżka, strumyk z mostkiem i brodem, wydeptane pętle, polanki stref |
| `punkty.py` | punkty orientacyjne i miejsca: Brama Pniaków, Kamień Powrotu, stanowisko jajka, krąg przybycia, paśnik, Wielki Kapelusz, Wilcza Skała, głazy legowiska z kotłem, menhiry, arena z filarem, Brama do Bagna, zapowiedź Bagna |
| `przegrody.py` | przejścia (płot z furtką, jeżyny, kamienny próg, niskie kamienie), domy potworów, rekwizyty i ozdoby przegród |
| `kulisy.py` | ściana lasu po bokach (skraj, przód z kolizją, drugi rząd, głąb), tło, ściana zamykająca, niewidzialne ściany |
| `detale_pasa.py` | drobiazgi przy ścieżce, kępy runa, kłody, kwiaty |
| `sprawdz.py` | **kontrola offline** (kod 1 = błąd) |
| `podglad.py` | **podgląd bez Blendera** (Pillow + numpy, własny rysownik brył) → `podglad/*.jpg` + `ujecia_swiat.json` |
| `czesci.json` | **wynik**: 8 601 części, format `swiat/biblioteka/scena.py` (generator `biblioteka-v2`, cechy w 16. polu) |
| `znaczniki.json` | **wynik** dla następnych etapów: przegrody, przejścia, strefy z węzłami i domami (układ pasa i świat), Strażnik, miejsca, punkty przybycia, strefy spokoju, punkty E, przelot kamery w świecie, grupa wrót, grupy do streamingu |
| `ujecia_swiat.json` | te same kamery co podglądy, w świecie Studio (format `tools/studio_zrzuty.py`) |
| `podglad/` | `gora.jpg`, `gora_strefy.jpg` (rzut z góry całego pasa — do porównania z `plan_pasa.png`), `polana_wejscie`, `polana_zagroda`, `lasek`, `zarosla_leze`, `arena_brama` (z ukosa), `oczy_przybycie`, `oczy_zarosla` (z oczu gracza) |

## Polecenia (z głównego folderu repozytorium)

```
python -B swiat/las_pas/generuj.py        # ok. 3 s: czesci.json, znaczniki.json, raport
python -B swiat/las_pas/sprawdz.py        # ok. 3 s: kontrola offline (woła też tools/studio_buduj.py --sucho)
python -B swiat/las_pas/podglad.py        # ok. 30 s: podglad/*.jpg i ujecia_swiat.json (--tylko gora,lasek; --wyj <folder>)
```
Wynik jest deterministyczny (`--ziarno 7`). Wymagane: numpy, Pillow. Bez Blendera i bez Studio.

## Budowa w Studio (następny etap — dokładne polecenia)

Studio w trybie **Edit**, wspólne miejsce Team Create: budujemy tylko własny kontener, punkty historii robi narzędzie.

```
# 0. zgłoś pracę (CLAUDE.md, obszar studio:LasPas) i sprawdź, czy nikt inny nie pracuje nad tym samym
python panel/narzedzia/praca.py start --id las-pas-studio --tytul "Las-pas w Studio" --koniec +45m --obszar studio:LasPas --obszar mapa:las_pas --stop-przy-kolizji

# 1. świeży plik i kontrola (kod 0)
python -B swiat/las_pas/generuj.py
python -B swiat/las_pas/sprawdz.py

# 2. budowa: kasuje TYLKO Workspace/LasPas z atrybutem Wygenerowane (cudzego nie rusza), punkt historii przed i po,
#    ok. 29 paczek po 300 części; --czekaj 20 = gdy ktoś testuje w Play, czeka do 20 min i ponawia paczkę
python -B tools/studio_buduj.py swiat/las_pas/czesci.json --paczka 300 --czekaj 20

# 3. streaming grup z znaczniki.json: Punkty/* i BramaBagna/* → Persistent, Kulisy/<strona>/O_* i Tlo/<strona>/O_* → StreamingMesh
#    (narzędzie starego lasu czyta nazwę kontenera z pliku znaczników; najpierw --sucho, żeby zobaczyć listę)
python -B swiat/biom_las/studio_atrybuty.py --znaczniki swiat/las_pas/znaczniki.json --sucho
python -B swiat/biom_las/studio_atrybuty.py --znaczniki swiat/las_pas/znaczniki.json

# 4. zrzuty ze Studio z tych samych kamer co podglądy (okno Studio widoczne)
python -B tools/studio_zrzuty.py swiat/las_pas/ujecia_swiat.json --wyj <folder> --czekaj 20 --rozmiar 1600

# 5. panel: migawka z podglądem 3D i raport do akceptacji (skill panel)
python panel/narzedzia/migawka.py --tytul "Las-pas w Studio" --korzen Workspace/LasPas
python panel/narzedzia/raport.py dodaj --tytul "…" --opis-plik opis.md --migawka <id>

# cofnięcie: Ctrl+Z w Studio albo
python -B tools/studio_buduj.py swiat/las_pas/czesci.json --usun
python panel/narzedzia/praca.py koniec --id las-pas-studio
```
Narzędzia niczego nie publikują i nie zapisują miejsca; Lighting zostaje bez zmian. Stary `BiomLas`, `LasMgla`,
`LasTeleport` zostają nietknięte (plan, wybór 10).

## Liczby

**8 601 części** (cel ok. 9 000, twardy limit 12 000; stary las 22 419). Na odcinek pasa (z kulisami i tłem w tym
pasie u; płyta gruntu liczy się do odcinka swojego środka):

| Odcinek | Części |
|---|---|
| ściana zamykająca (u −34…0) | 145 |
| Polana Przybycia | 738 |
| płot z furtką | 139 |
| Zagroda Slime'ów | 1 655 |
| strumyk z mostkiem | 263 |
| Lasek Muchomorowy | 1 678 |
| jeżynowe zwężenie | 154 |
| Wilcze Zarośla | 1 496 |
| kamienny próg | 113 |
| Leże Trolla | 828 |
| brama menhirów | 141 |
| Arena Strażnika Gaju | 729 |
| przedbramie i Brama do Bagna | 330 |
| zapowiedź Bagna (u 940–966) | 192 |

Na grupę: Kulisy 4 596 (skraj 258 rzeczy, przód 234 drzewa z kolizją pnia, drugi rząd 165, głąb 254), Detale 1 468,
Tło 520, Teren 458, Przejścia 302, Zagroda 263, Ścieżka 157, Punkty 139, Domy 138, Lasek 127, BramaBagna 84, Leże 79,
Polana 78, Zarośla 58, ZapowiedzBagna 49, Arena 48, Przedbramie 27, Piny 10 (ognisko z `wspolne.ognisko`).
Kulisy i tło są cięższe niż w szacunku planu (2 900) — ściana lasu ma być gęsta z każdej strony; w polu gry zostały
place walki. Neon 73, kule 8, walce 771, półprzezroczyste 5 (mgła Bagna), niewidzialne 6, z kolizją 11%.
Materiały (faktury starego lasu): SmoothPlastic 63%, Wood 19%, Rock 5%, Ground 4%, Grass 3%, Slate, WoodPlanks,
LeafyGrass, Fabric po ok. 1%, Neon, Cobblestone, Pebble, Mud, Metal poniżej 1%.

## Co gdzie stoi (krótko)

- **Ściana zamykająca** (u −34…0): skały „muru” niższe na osi (nad nimi startuje przelot kamery), krzaki, wysokie kulisy;
  niewidzialna ściana na u −5. **Brama Pniaków** (u 4, pnie v ±10, ok. 22 wys.) z lampionem i chorągiewkami duetu.
- **Polana Przybycia**: kamienny krąg przybycia z rombem światła na ścieżce i krąg grzybków, **stanowisko jajka**
  (podest 12 × 12, puste gniazdo z korzeni, punkt E, wiaderka farby, lampion), **Kamień Powrotu** (głaz z rombem Neon,
  punkt E, ognisko), drogowskaz z pięcioma ramionami-rekwizytami kolejnych przegród, beczka, skrzynka, kosz, lampiony.
- **Płot z furtką** (1,2 wys., furtka 16 otwarta, słupki z lampionami, tabliczka ze znakiem galarety).
- **Zagroda**: płot wzdłuż obu ścian, przegródki z żywopłotu 0,8 z przerwą 24, wydeptane pętle, kałuże galarety (domy
  i ozdoby), koryta z galaretą, **paśnik-wieża** z przelewającą się galaretą.
- **Strumyk**: woda bez kolizji przez cały pas, garbaty mostek 12 szer. (≤ 1,5 wys.), bród z kamieni przy v ±24,
  lilie, bliki, trzcina tylko w kulisach.
- **Lasek**: ciemne runo, trzy polanki mchu, grzyby-olbrzymy w kulisach i rogach, kręgi grzybków na granicach polanek,
  chatki-grzyby (domy), **Wielki Kapelusz** (kapelusz r 12, spód ok. 20 — nad placami walki), świecące zarodniki.
- **Jeżynowe zwężenie**: fioletowe ściany jeżyn 6 wys. do otwarcia 32 st.
- **Zarośla**: ciemny bór (sosny, świerki, suche drzewa), jaśniejsze polanki pod pętlami wilków, płaty igliwia,
  wykroty, jamy w jeżynach i szpary w głazach (domy), pale z czaszką, **Wilcza Skała** z bursztynowymi oczami.
- **Kamienny próg**: głazy 8–10 do otwarcia 28 st, kości, ukradziony szyld karczmy, czaszka.
- **Leże**: udeptana ziemia i błotna polanka, głazy przy ścianach, grota trolla (dom), **głazy legowiska z kotłem**
  (zupa z galarety, ogień, dym), łupy (beczki, skrzynia, stos drewna, maczuga), pniaki, kości.
- **Brama menhirów**: dwa menhiry 14 wys., niskie kamienie ≤ 1,2.
- **Arena**: krąg menhirów r 26 z przerwami na ścieżkę, posadzka 0,3, **filar z zielonym kryształem** (ok. 41), odłamki.
- **Przedbramie** (strefa spokoju): ławka, lampiony, stos kamieni, suche drzewa. **Brama do Bagna** (u 934):
  palisada przez cały pas, `BramaBagna/Wrota` = dwa skrzydła z kolizją, łańcuch i złota kłódka (osobna grupa).
- **ZapowiedzBagna** (u 934–966, osobna grupa — usunąć, gdy powstanie Bagno): błoto, kałuże, mgła z kul, suche
  drzewa, niewidzialna ściana na u 965 — żeby przez wrota nie było widać pustki.

## Co pilnuje kontrola (`sprawdz.py`, wynik 16.11: 0 błędów, 0 ostrzeżeń)

Format wymagany przez `tools/studio_buduj.py` (jeden kontener, wiersze, typy, indeksy, Enum.Material, kolory, cechy)
i jego tryb `--sucho`; rozmiary > 0,05; limity i sufity; granice pasa i brak nachodzenia na miasteczko, stary las,
oba prototypy walki i Baseplate (skrzynki z `plan_pasa.json`, jak w `sprawdz_plan.py`); place walki r 12 wolne od
1,6 do 18 nad gruntem przy 79 węzłach (z miejscem Strażnika); ścieżka wolna od 0,6 do 7; otwarcia pięciu przejść nie
wyższe niż w planie; pętle potworów wolne; krzywa przelotu kamery (269 próbek) nie wchodzi w żadną część; grunt
płaski i bez dziur (płyta z kolizją, wierzch 0); woda bez kolizji; niewidzialne ściany |v| = 38, u −5, u 965; wrota
zamykają otwarcie 16 st na wysokość ≥ 7; punkty E; obecność wszystkich przegród, przejść, punktów i domów; zgodność
znaczników z planem i z `studio_atrybuty.py`; każda część ma rolę faktury.

## Co użyte ponownie, co nowe

- **Import bez zmian**: `swiat/biblioteka/scena.py` (scena, układy, cechy, kontrola jakości), `swiat/biom_las/paleta.py`,
  `faktury.py` (`naloz`, role, korekty kolorów — plus 3 nowe nazwy części w `generuj.FAKTURY_DODATKOWE`: Żywopłot, Furtka,
  Dym), `rosliny.py` (wszystkie rodziny drzew, grzybów, krzaków, kulis), `skaly.py` (głaz, kanciak, menhir, kamyki),
  `detale.py` (drobiazgi, kłody, skrzynka, kosz, stos drewna i kamieni, tabliczka, czaszka), `teren.py` (wstęga, dysk,
  wielokąt z klinów), `lokacje/wspolne.py` (kałuża galarety, chatka-grzyb, jama, szpara, plama, lampion, punkt E,
  ognisko, drogowskaz), `swiat/krzywe_miasteczko/zestaw.py` (łamana, beczka, skrzynia, ławka, dym, chorągiewka duetu),
  `swiat/biom_las/pas/sprawdz_plan.krzywa_kamery` (ta sama krzywa przelotu co w planie).
- **Wzorowane, ale złożone od nowa** (funkcje starych lokacji budują w stałych miejscach starego lasu — ogniska,
  drogowskazy do jego podbiomów): Brama Pniaków i Kamień Powrotu (`laka.py`), gniazdo (`serce.py`), Wielki Kapelusz
  (`kapeluszowo.py`), Wilcza Skała i wrota (`ostepy.py`), legowisko i kocioł (`wawoz.py`), filar i krąg (`korona.py`).
- **Nowe**: generator pasa z planu, zasady na częściach z wycofywaniem, kulisy rzędami z rodzinami przegród, przejścia,
  paśnik, stanowisko jajka, krąg przybycia, brama z osobnymi wrotami, zapowiedź Bagna, kontrola i rysownik podglądów.

## Podgląd 3D w panelu

Podgląd 3D panelu pokazuje tylko **migawki** z `panel/dane/podglad/<id>/` (`meta.json` + `czesci.json`), robione
z otwartego Studio (`panel/narzedzia/migawka.py --korzen Workspace/LasPas`); plików `swiat/<scena>/czesci.json` sam
nie czyta. Żeby las-pas był tam widoczny: (a) po budowie w Studio zrobić migawkę (krok 5 wyżej) — bez zmian w kodzie;
albo (b) przed budową dopisać do panelu małe narzędzie „migawka z pliku”, które złoży folder migawki z `czesci.json`
funkcjami `podglad.zbuduj_meta` i `podglad.zapisz_migawke` (`panel/bc/podglad.py`) ze źródłem innym niż „studio” —
to zmiana w `panel/`, w tym etapie niezrobiona. Format pliku jest ten sam (16. pole z cechami panel pomija, części
niewidzialne ukrywa).

## Czego nie sprawdzono

- **Wygląd w Roblox**: podglądy to własny rysunek brył w Pillow — bez faktur materiałów, cieni rzucanych, poświaty
  Neonu, mgły i oświetlenia miejsca. Kolory po korekcie `faktury.py`, ale jak wyglądają faktury w świetle pasa (słońce
  za plecami) — niesprawdzone. Kąt widzenia Studio (`studio_zrzuty.py`) jest inny niż w podglądach.
- **Kolizje i ruch w trybie Play**: niewidzialne ściany, wejście na mostek i bród, skok przez płot 1,2, zahaczanie
  o przechylone pale, kolizje z korzeniami Brama Pniaków, czy potwór wychodzi z domu w punkt z planu.
- **Płynność i telefon**: 8,6 tys. części, streaming (Persistent / StreamingMesh dopiero po kroku 3), przelot kamery.
- Czy przez wrota i nad kulisami nie widać końca świata z różnych miejsc (w podglądach nie widać).
- Rozmiar Baseplate (±1024) i kierunek słońca wzięte z planu, nie z miejsca.

## Do zrobienia w następnych etapach

1. Budowa w Studio (wyżej), zrzuty, przegląd świeżym okiem, raport w panelu.
2. **Potwory w przegrodach**: `swiat/las_potwory/generuj_dane.py` przepiąć na `znaczniki.json` → `strefy`
   (`wezly_swiat`, `domy_swiat`, `odrodzenie_s`, `odrodzenie_stale` trolla), Strażnik z `straznik.miejsce_swiat`
   (stoi na posadzce 0,3), domy 12–20 od węzłów i blokada 12 (plan rozdz. 7), Leśny Troll w `GATUNKI`.
3. **Teleport**: punkty przybycia z `znaczniki.json` → `punkty_przybycia` (Polana u 14 twarzą do +X), Kamień Powrotu
   i stanowisko jajka — punkty E w `punkty_e`; wyłączyć stary `LasTeleport` dopiero po akceptacji.
4. **Mgła pasa**: prostokąt X 1076…2040, |Z + 700| ≤ 60, przy bramie przejście w mgłę Bagna, rzadsza na przelot.
5. **Brama dla gracza**: skrypt klienta, który dla gracza po wygranej ze Strażnikiem wyłącza kolizję i ukrywa części
   `Workspace/LasPas/BramaBagna/Wrota` (serwer pilnuje atrybutu); za bramą jest tylko `ZapowiedzBagna` — przed
   otwarciem bramy trzeba Bagna albo dłuższej ściany za nią.
6. **Przelot kamery** (D-077): krzywa z `znaczniki.json` → `przelot_kamery.punkty_swiat` (Catmull-Rom jak
   `sprawdz_plan.krzywa_kamery`), ryk Strażnika, flaga pierwszego wejścia, prośba o streaming u 200 / 450 / 700 / 874.
7. Strefy spokoju (Polana, przedbramie) są prostokątami — `znaczniki.json` ma je też w świecie.
8. Po decyzji ludzi: usunięcie starego lasu; po zbudowaniu Bagna: usunięcie `ZapowiedzBagna`.

## Znane słabości

- Grunt pola gry jest płaski i jednolity — w kojcach poza wydeptanymi pętlami jest pusto (place walki muszą zostać
  wolne); życie dają kulisy, domy i rekwizyty pod ścianami.
- Kłód w polu prawie nie ma (nie mieszczą się poza placami walki); wykroty tylko 3, kępy jeżyn w polu 2.
- Rzędy drzew w kulisach z bliska bywają regularne jak aleja; tło to proste bryły-sylwetki.
- Łańcuch na wrotach to kilka kostek — z bliska mało czytelny.
