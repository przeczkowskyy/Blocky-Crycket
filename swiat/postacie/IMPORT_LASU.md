# Import modeli lasu do Roblox — plan, decyzje i lista kroków w Studio

> **Status: propozycja, przygotowanie bez Studio (15.11.2026).** Nic nie zostało wgrane. Ten dokument i narzędzie
> `roblox_import_lasu.py` przygotowują etap w Studio tak, żeby był samym wykonaniem. Właściciel konta zgodził się
> (14.11.2026) na wgrywanie modeli i materiałów gry, póki gra jest w testach; publikacja miejsca nadal wymaga jego zgody.
> Sześć modeli przyjął właściciel 15.11.2026: Zwiadowca, Leśny Troll, Cierniowy Wilk, Muchomornik, Strażnik Gaju,
> Leśny Slime (moduły w `swiat/postacie/`, pliki w `swiat/postacie/wynik/<id>/`). Plan i narzędzie przeszły tego samego
> dnia niezależną kontrolę bez Studio; jej poprawki i to, co nadal jest założeniem, opisuje rozdz. 2.6.

## 1. W skrócie

- **Wgrywamy sześć plików FBX, po jednym zasobie Model na model.** Klipów nie wgrywamy. GLB zostaje w zapasie.
- **Animacje w fazie testów: propozycja to nasz własny odtwarzacz klipów z prototypu walki**
  (`swiat/test_walki2/zrodla/Klipy.luau`). Po imporcie miałby poruszać stawami zaimportowanego modelu zamiast stawów
  rigu z klocków. To jedyna z trzech dróg, która nie wymaga kolejnych 49 zasobów Animation ani rejestrowania klipów,
  które działa tylko w Studio. **Na zaimportowanym modelu nikt tej drogi jeszcze nie sprawdził.** Sprawdzona jest tylko
  na rigach z klocków w trybie Play w Studio (rozdz. 3.2). Zmiany w odtwarzaczu są opisane, ale nie zostały zrobione.
- **Kolejność importu idzie od najbezpieczniejszego modelu:** Zwiadowca (R15, ta sama droga co Rycerz 13.11), potem
  Troll, Wilk, Muchomornik i Strażnik. Na końcu idzie Slime, bo jego galareta jest skórowana na dwóch kościach.
  Narzędzie pilnuje tej kolejności samo.
- **Narzędzie:** `python -B swiat/postacie/roblox_import_lasu.py`. Domyślnie pokazuje plan i z niczym się nie łączy.
  Wgrywa tylko z `--tylko <id> --tak-wgraj`, model po modelu, i staje na pierwszej niezgodności. Wznowienie nie wgrywa
  niczego drugi raz. Plik, który nie jest przyjętą wersją (sha256 z rozdz. 8), w ogóle nie zostanie wgrany.
- **Etap w Studio zajmie ok. 45–65 minut pracy** (rozdz. 5; z próbą pozy do 70). Do tego dochodzi czekanie na
  odpowiedź właściciela po Trollu (krok S4), bo tam zawsze jest stop. Najwięcej czasu bierze oglądanie zrzutów;
  czekanie na moderację to zwykle 1–3 minuty na model, a najwyżej 9 minut, bo potem narzędzie samo staje.

## 2. Ustalone fakty (z plików, bez Blendera i bez Studio)

Źródła: `wynik/<id>/raport.json` i `raport.txt`, plik GLB tego samego eksportu, odczytany czystym Pythonem (drzewo
kości, wagi skóry, kanały klipów), oraz dane modułów (które bryły świecą). Moduły są tylko czytane: `zbuduj()` zwraca opis
postaci w czystym Pythonie. Te same liczby wypisuje plan narzędzia. FBX nie da się sensownie rozebrać czystym Pythonem.
Jego zawartość potwierdza kontrola eksportu z raportu: Blender wczytał każdy plik z powrotem i liczby się zgadzają.

### 2.1 Modele

| Model | Szkielet | Kości (głęb. drzewa) | MeshPart po imporcie | Trójkąty w pliku | FBX | Wzrost | Kości bez siatki |
|---|---|---|---|---|---|---|---|
| Zwiadowca | R15 | 17 (6) | 15 | 3374 (z łukiem i sztyletem 4198) | 405 596 B | 5,76 | Root, HumanoidRootNode |
| Leśny Troll | własny | 18 (6) | 17 | 7778 | 549 004 B | 9,94 | Root |
| Cierniowy Wilk | własny (czworonóg) | 22 (5) | 21 | 4470 | 655 116 B | 4,36 | Root |
| Muchomornik | własny | 29 (6) | 28 | 4272 | 1 006 732 B | 3,60 | Root |
| Strażnik Gaju | własny | 37 (5) | 36 | 11 168 | 1 667 996 B | 14,54 | Root |
| Leśny Slime | własny | 28 (4) | 25 | 4396 | 879 372 B | 3,38 | Root, **Cialo, Gora** |

- **Jedna siatka na kość.** Każda bryła kości jest jedną siatką `<Kość>_Geo` z wagą 1 na tej kości (modyfikator
  Armature). W GLB wszystkie siatki ciała są skórowane (mają `skin`: 15, 17, 21, 28, 36 i 25 siatek), a nie
  podpięte pod kość jako dzieci. Wyjątkiem co do wag jest siatka `Dol_Geo` slime'a: 1104 z 1136 wierzchołków (97,2%)
  ma wagi na dwóch kościach, `Dol` i `Gora`. Inne siatki skórowane na kilku kościach nie występują. Trójkąty w tabeli
  liczą tylko siatki z pliku; `trojkaty_razem` z raportu liczy też przedmioty spoza pliku (u Zwiadowcy łuk i sztylet).
- **Znaczniki zaczepów.** Każdy model ma w FBX sześcienne siatki `<Nazwa>_Att` (12 trójkątów). W GLB są dziećmi kości,
  bez skóry. U Rycerza (R15) importer zamienił je na `Attachment`; przy własnym szkielecie nie wiadomo, co z nimi zrobi.
  Stąd w kontroli eksportu jest więcej siatek niż w tabeli (Troll: 21 = 17 + 4 znaczniki).
- **Korzeń.** Każdy szkielet ma korzeń `Root` bez siatki. Zwiadowca ma też `HumanoidRootNode`. U Rycerza nie ma po
  imporcie żadnej kości `Bone`, za to jest część `HumanoidRootPart`; to, że powstała z tych dwóch kości, jest
  wnioskiem, a nie czymś zmierzonym.
- **Materiał.** W całym modelu jest jeden materiał z teksturą-paletą (32 albo 64 px), a w `<id>_tekstury/` leżą kolor, metal,
  szorstkość i emisja.
- **Czego nie ma w pliku.** Łuk i sztylet Zwiadowcy mają `eksport: False`, więc w `zwiadowca.fbx` ich nie ma. Tak samo
  było z mieczem Rycerza, więc notatka w sejfie („import bierze tylko części ciała”) myli przyczynę. Importer niczego
  nie zgubił, bo miecza nie było w pliku. `roblox_import.py` liczy w polu `siatek_ciala` także przedmioty spoza pliku
  (Rycerz: 16, w pliku 15, Zwiadowca: 17, w pliku 15). Narzędzie lasu liczy tylko siatki z pliku.

### 2.2 Klipy

Długości są w klatkach przy 30 kl./s. Liczba próbek to klatki + 1. „Przesuwa” znaczy, że pozycja kości odchodzi w klipie od
spoczynku (wartości z GLB, w studach). Żaden klip żadnego modelu nie ma kanału skali, co sprawdzono na wartościach
w GLB, a nie tylko na nazwach kanałów.

| Model | Klipy (klatki) | Kości przesuwane w klipach (największe przesunięcie) |
|---|---|---|
| Zwiadowca | idle 60, ruch 20, atak 28, umiejetnosc 54, uderzenie_z_gory 46, trafienie 20, unik 40, upadek 60, wiwat 48 | tylko `LowerTorso` (staw Root), do 3,25 w uniku, 1,70 w uderzeniu z góry |
| Leśny Troll | idle 72, ruch 48, atak 36, umiejetnosc 60, trafienie 20, unik 30, upadek 60, ryk 60 | tylko `Biodra`, do 1,60 w uniku (idle nie przesuwa niczego) |
| Cierniowy Wilk | idle 72, ruch 16, atak 27, umiejetnosc 54, trafienie 18, unik 28, upadek 56, ryk 60 | `Zad` do 2,40 (umiejętność), `Powieki` 0,35 |
| Muchomornik | idle 72, ruch 24, atak 27, umiejetnosc 60, trafienie 18, unik 27, upadek 60, wiwat 60 | 17 kości: `Zarodnik0–9` 3,3–3,6 (zarodniki), `Kapelusz` 2,32 (upadek), `Biodra` 1,57, `Laska` 0,54 |
| Strażnik Gaju | idle 72, ruch 60, atak 42, umiejetnosc 90, trafienie 20, unik 30, upadek 80, ryk 60 | 33 kości: korzenie `K1A` 13,45 … `K4A` 10,06 (umiejętność), w upadku `Glowa` 9,76 i `RamieL` 6,32 (rozsypanie), `Biodra` 4,46 |
| Leśny Slime | idle 60, ruch 24, atak 30, umiejetnosc 66, trafienie 18, unik 27, upadek 60, wiwat 40 | 23 kości: `Plusk` 4,30 i `Kula` 3,40 (kula kwasu), `Gora` 2,20 (zgniecenie w upadku), `Cialo` 1,85 (skok ataku) |

Klipy przesuwają więc kości naprawdę i pozycja musi przejść do gry razem z obrotem. Pętle: idle, ruch i ryk albo
wiwat; reszta jest jednorazowa. Upadek kończy się leżeniem albo rozsypaniem i odtwarzacz ma zatrzymać ostatnią klatkę.

### 2.3 Świecenie

Importer przenosi kolor (u Rycerza każda część dostała `SurfaceAppearance` z teksturą-paletą). Czy przenosi emisję,
nie wiadomo, a w modelu emisja jest tylko w teksturze. W Roblox świecenie trzeba więc dorobić, a jedna siatka na kość
wyznacza, co się da.

| Model | Siatki w całości świecące (Neon na całą część) | Świecenie tylko w części siatki (Neon odpada) |
|---|---|---|
| Zwiadowca, Leśny Troll | brak | brak |
| Cierniowy Wilk | brak | `Glowa` (2 z 36 brył: oczy) |
| Muchomornik | 13: `Zarodnik0–9`, `ZarodekL0–2` | `Laska` (1 z 14: bulwa) |
| Strażnik Gaju | 2: `Krysztal`, `Blask` | `Glowa` 5/22, `Korona` 2/53, korzenie `K1A–K5B` po 2 bryły |
| Leśny Slime | 9: `BokL`, `BokP`, `Przod`, `Tyl`, `Kula`, `Plusk`, `KroplaL/P/T` | `Dol` 5/19 (galareta), `Oczy` 4/8, `OczyWiel` 4/8, `Policzki` 2/4 |

### 2.4 Co wiadomo z importu Rycerza (13.11.2026, `wynik/_roblox/import_rycerz_fbx.json`)

- Rycerz wyszedł jako R15: 15 części `MeshPart` o nazwach R15 bez `_Geo`, do tego `Humanoid`, `HumanoidRootPart` (Part),
  15 stawów `AnimationConstraint`, 14 `BallSocketConstraint` i **0 kości `Bone`**.
- Skala wyszła 1:1 (wzrost 5,71). Każda część dostała `SurfaceAppearance` z tą samą teksturą-paletą.
- Na modelu jest 52 `Attachment`, w tym 18 standardowych zaczepów. Brakuje zaczepu ze znacznika `Root_Att`, czyli
  `RootAttachment`, więc narzędzie nie wymaga go u żadnego modelu.
- Przód zmierzony przed naprawą różnił się od zadanego o ok. 0,25°. Obrót nie był potrzebny, a lewa ręka była po lewej,
  więc model nie wyszedł w lustrze. Dlaczego model od razu patrzył we właściwą stronę, nie wiadomo.
- `insert_asset` wstawił Rycerza jako **pakiet**: odpowiedź ma `"isPackage": true`, a w modelu jest `PackageLink`.
  Naprawa zmienia potem zawartość pakietu (kotwiczenie, skala, położenie). Dla oglądania to bez znaczenia, ale zanim
  import posłuży za szablon aktora albo trafi do publikacji, trzeba zdecydować, czy `PackageLink` zostaje.
- **Klipy na imporcie Rycerza nie mają zapisanego wyniku.** Eksperyment `roblox_import_klipy.py`, który leży w repo
  poza gitem, porównuje pozy liczbowo, ale pliku `import_rycerz_klipy.txt` nie ma. Notatka w sejfie mówi „w sprawdzaniu”.
  Czy `KeyframeSequence` rejestrowane w trakcie gry ruszają stawami `AnimationConstraint`, nadal nie jest potwierdzone.

### 2.5 Usterki narzędzi znalezione przy przygotowaniu (poprawione wstecznie zgodnie)

1. W KONTROLA kość `Bone` była sprawdzana po `Attachment`, a `Bone` dziedziczy po `Attachment`. Przy własnych
   szkieletach wszystkie kości trafiłyby więc na listę zaczepów, a lista kości zostałaby pusta (u Rycerza kości nie było,
   więc nic nie wyszło na jaw). Teraz kości są sprawdzane pierwsze, a KONTROLA zapisuje też drzewo kości
   (`kosci_drzewo`: nazwa, rodzic, głębokość), stawy (`stawy`) i materiał każdej siatki.
2. Kierunek przodu był liczony tylko z części R15 (stopa i łydka). Teraz punkty przodu są parametrem, a domyślnie są to
   te same części R15.
3. Naprawa skali i obrotu, ustawienie modelu i zrzuty działały tylko dla modułów z `roblox_postac.ROZMIESZCZENIE`.
   Modele lasu tam nie są, więc zostałyby wstawione bez naprawy i bez zrzutów. Teraz miejsce może przyjść z `profil`.
   Kamera zrzutów ma też mnożnik, bo Strażnik ma 14,5 studa i nie zmieściłby się w kadrze robionym na 5,7 studa.
4. `roblox_import.py` bez `--tak-wgraj` **łączy się ze Studio** (sprawdza miejsce i konto), więc nie jest planem bez
   kontaktu. Taki plan daje dopiero `roblox_import_lasu.py`.

Zgodność wstecz sprawdza test `biblioteka/test_roblox_import.py`. Bez profilu kod KONTROLA ma punkty R15, kamera ma te
same liczby co wcześniej, a moduł spoza ROZMIESZCZENIE nadal nie dostaje naprawy. Z profilem dostaje naprawę i zrzuty
z kamerą przeskalowaną.

### 2.6 Niezależna kontrola (15.11.2026) i poprawki w `roblox_import_lasu.py`

Kontrola przeliczyła fakty z rozdz. 2.1–2.3 osobnym skryptem z GLB i `raport.json`. Kości, głębokości, klipy, długości,
przesunięcia, brak kanałów skali, skóra slime'a, świecenie i rozmiary plików się zgadzają. Jedyna zła liczba to
trójkąty Zwiadowcy: 4198 liczy łuk i sztylet, a w pliku jest 3374. Poprawione w tabeli i w planie narzędzia.

Wersja `roblox_import.py` z HEAD i wersja robocza dały na udawanym Studio dla Rycerza (`--asset`) te same wywołania
w tej samej kolejności: ten sam kod SPIS, PRZENIES i NAPRAWA, te same parametry naprawy, te same kamery obu zrzutów
i ten sam plik wyniku. Różnią się tylko kody KONTROLA (zmiana z rozdz. 2.5) i KTO (poprawka 9 niżej), i tak miało być.
Stary test z HEAD przechodzi na nowym kodzie.

Poprawki (każdą sprawdza `biblioteka/test_roblox_import_lasu.py` albo, przy pkt 9, `test_roblox_import.py`; wyłączenie pkt 1–7 po kolei wywraca test):

1. `--tak-wgraj` działa tylko z `--tylko`. Wcześniej samo `--tak-wgraj` wgrywało wszystkie sześć modeli po kolei
   i szło dalej po Trollu, choć po nim plan każe zawsze stanąć.
2. Opcji nie da się skracać. Wcześniej argparse przyjmował `--tak` albo `--tak-wg` jako `--tak-wgraj`, a `--s` jako
   `--sonda-skory`.
3. Kolejność jest pilnowana. Model wgrywa się dopiero wtedy, gdy wszystkie wcześniejsze mają w tabeli werdykt
   „zgodny” albo idą wcześniej w tym samym poleceniu. Świadome odstępstwo wymaga `--mimo-kolejnosci`.
4. sha256 każdego pliku jest wpisane w narzędzie (`PRZYJETE_SHA256`, te same liczby co w rozdz. 8). Inny plik to BRAK
   w planie, a wgranie go odmawia. Wcześniej porównanie sześciu długich liczb było zadaniem dla człowieka w kroku S1.
5. Model wpisany w `roblox_postac.ROZMIESZCZENIE` to BRAK. `roblox_import` stawia takie modele według ROZMIESZCZENIE, a nie
   według profilu, więc ocena kierunku liczyłaby od złego miejsca.
6. Ocena głębokości drzewa kości przyjmuje teraz także o 1 mniej. Gdyby importer zamienił `Root` na część (jak
   u Rycerza), każdy potwór wyszedłby „niezgodny” po wgraniu. Wcześniej przechodziło tylko tyle samo albo o 1 więcej.
7. Sonda skóry odróżnia „błąd” (inne miejsce, brak kontenera, modelu albo siatki) od „nie” (skóra przepadła).
   Kody wyjścia: 0 TAK, 1 NIE, 2 BŁĄD, 3 NIEZNANY. Wcześniej błąd miejsca dawał werdykt „NIE”.
8. Komunikat po przerwaniu mówi, co zrobi to samo polecenie, zależnie od etapu w pliku stanu. Wcześniej zawsze
   obiecywał wznowienie, także wtedy, gdy stan jest nieznany i narzędzie znowu się zatrzyma.
9. `roblox_import.py`, kod KTO: liczy obiekty `Workspace/TestPostaci` i czyta atrybut `Wygenerowane`. Inny niż jeden
   własny kontener zatrzymuje skrypt jeszcze przed wgraniem (scenariusz T w `test_roblox_import.py`). Wcześniej skrypt
   sprawdzał tylko, że kontener o tej nazwie istnieje, więc mógłby wstawiać do cudzego obiektu.
10. Ocena nie liczy znaczników `<Nazwa>_Att`, które wyszłyby jako `MeshPart`, do siatek ciała ani do koloru. Pokazuje je
    jako osobny punkt do obejrzenia; brak zaczepów i tak wychodzi w punkcie „zaczepy”.
11. Miejsca modeli przesunięte o 1–3 studa, żeby każdy obrys miał co najmniej 3 studa do straganów, studni i sąsiadów
    (rozdz. 4).

Plan sprawdzono pod strażnikiem, który blokuje gniazda sieciowe, uruchamianie procesów i każdy zapis pliku, a mostek
Studio był ustawiony na polecenie, które zostawiłoby ślad. Wynik: kod 0, zero zablokowanych prób, brak śladu mostka,
katalog `wynik/_roblox` bez zmian.

## 3. Decyzje

### 3.1 Co wgrywamy (a)

- **Jeden plik `<id>.fbx` na model, jako jeden zasób Model.** To ta sama droga, co u Rycerza. FBX jest w każdym modelu
  mniejszy albo podobny do GLB (Troll ma FBX 0,55 MB, a GLB 1,30 MB). W FBX nie ma klipów, a siatki, kości, znaczniki
  zaczepów i tekstura są w jednym pliku. Razem sześć plików waży 5,16 MB, przy limicie 20 MB na jeden plik.
- **Klipów (`<id>__<klip>.fbx`, 49 plików) nie wgrywamy.** W fazie testów gra je odtwarzacz z danych (rozdz. 3.2).
  Pliki klipów zostają do drogi przez zasoby Animation, gdyby kiedyś była potrzebna.
- **GLB jest zapasem.** Wgrywa się go tylko wtedy, gdy FBX danego modelu wyjdzie źle (np. zgubi skórę slime'a) i właściciel
  zgodzi się na drugi zasób. Plik stanu jest osobny dla każdego formatu (`wgranie_<id>_glb.json`), więc ochrona przed
  podwójnym wgraniem działa także wtedy.
- Broń Zwiadowcy (łuk, sztylet) nie jest częścią tego etapu, bo to osobne przedmioty z `wynik/zwiadowca/przedmioty/`.

### 3.2 Jak animacje trafiają do gry (b)

| | A. `KeyframeSequence` rejestrowane w trakcie (`KeyframeSequenceProvider:RegisterKeyframeSequence`) | B. Zasoby Animation | C. Własny odtwarzacz klipów (`Klipy.luau`) |
|---|---|---|---|
| Gdzie działa | Tylko w Studio: kod `PokazAnimacji` i `PetyTestowe` sam się wyłącza poza Studio (`RunService:IsStudio()`), bo tak mówi dokumentacja `RegisterKeyframeSequence`. Tą drogą sprawdzały klipy `roblox_klipy.py` i `roblox_import_klipy.py` | wszędzie (dokumentacja) | sprawdzone w Play w Studio. W opublikowanej grze to **założenie**: `Klipy.luau` tak twierdzi, bo nie używa `KeyframeSequenceProvider`, ale miejsce nie było publikowane |
| Co trzeba wgrać | nic | 49 zasobów Animation (9 klipów Zwiadowcy i po 8 na każdego potwora), każdy z moderacją | nic poza sześcioma modelami |
| Czyje zasoby | — | według dokumentacji Roblox animacja musi należeć do właściciela gry (osoby albo grupy); tu niesprawdzane. To decyzja właściciela | — |
| Pozycja kości | tak (`Pose.CFrame`) | tak | tak (`Transform` ma pozycję), już działa na rigach z klocków |
| Stan sprawdzenia | 32 klipy na rigach z klocków **starszych postaci** (Karczmarz, Kot-Mag, Pies, Rycerz, Slime, Smok) zgodne w Studio, tryb Edit (13.11, `wynik/_roblox/klipy_kontrola.txt`). Modeli lasu tą drogą nie sprawdzano. Na imporcie Rycerza wyniku nie zapisano | niesprawdzone | klipy ośmiu aktorów prototypu (sześć modeli lasu, mag, wojownik) grają na rigach z klocków w Play w Studio, według README prototypu i jego testów Play. **Na żadnym imporcie niesprawdzone** |
| Własny szkielet | Animator dopasowuje `Pose` po nazwach kości, a drzewo póz musi odtwarzać drzewo kości | import FBX klipu w Animation Editor na zaimportowanym rigu | odtwarzacz trzeba nauczyć stawów importu (niżej); wszystko, co niżej, to plan, nie wynik |

**Propozycja na fazę testów: droga C.** Tylko ona nie wymaga wgrywania animacji ani decyzji o własności i nie zależy
od rejestrowania klipów, które działa tylko w Studio. Używa też tych samych danych klipów
(`swiat/test_walki2/dane/<klucz>.json`; klucz Strażnika to `straznik_lasu`, nie `straznik_gaju`), które już grają
w prototypie. Droga A poza Studio odpada, a droga B czeka na decyzję właściciela gry. **Zastrzeżenie:** C jest
sprawdzona tylko na rigach z klocków, w których stawy to `Motor6D` z `C0`/`C1` bez obrotu. Że da się ją przenieść na
import, to założenie. Rozstrzygnie je dopiero pierwsza próba odtwarzacza na imporcie, po tym etapie (ryzyko 7).

**Co musiałoby się zmienić w `swiat/test_walki2/` (opis, bez zmian w kodzie; każdy punkt zakłada coś o wyniku
importu, czego jeszcze nie widziano):**

1. **`Klipy.luau`, wyszukiwanie stawów (`Klipy.nowy`).** Dziś odtwarzacz szuka w części kości `Motor6D`
   i przy jego braku zgłasza błąd. Dla importu trzeba przyjąć trzy rodzaje stawu:
   - `Motor6D`: tak jak dziś;
   - `AnimationConstraint`: Zwiadowca R15, a może też sztywne potwory. Staw znajduje się po
     `Attachment1.Parent == część kości`;
   - `Bone`: import skórowany, szukany po nazwie kości (`model:FindFirstChild(nazwa, true)`, `IsA("Bone")`).
   Wszystkie trzy mają `Transform`, a odtwarzacz wpisuje tylko tę wartość.
2. **`Klipy.luau`, układ stawu.** Dane klipów są liczone dla stawów, których `C0` i `C1` nie mają obrotu, a osie leżą
   równo z osiami modelu (przód −Z). U importu osie stawu (orientacja zaczepu albo kości w spoczynku) mogą być obrócone.
   Przy `Klipy.nowy` trzeba więc raz zmierzyć obrót spoczynkowy R każdego stawu względem korzenia modelu i co klatkę
   wpisywać `R⁻¹ · T · R` zamiast `T`. Pozycję trzeba przy tym obrócić tak samo, a przy modelu przeskalowanym przez
   naprawę pomnożyć ją przez `model:GetScale()`. Dla rigów z klocków R jest jednostkowe, więc ta zmiana ich nie rusza.
3. **`Klipy.luau`, skóra.** `przygotujSkory` udaje skórę slime'a siatką `SpecialMesh` (przesunięcie i rozciąganie
   brył z atrybutem `Skora`). Przy prawdziwej skórze z importu tego nie robimy, bo wagi robią to same. Brzuszki
   „chowane” (`przygotujChowane` szuka części po `WeldConstraint`) trzeba szukać po nazwie siatki `<Kość>_Geo`. Gdyby
   importer złączył siatki w jedną część, chowanie przestanie być możliwe.
4. **`Aktorzy.luau`.** Szablon aktora bierze się dziś z `Workspace/TestWalki2/Aktorzy/<klucz>`, a buduje go `zbuduj.py`
   z rigu z klocków. Dla importu szablonem byłaby kopia zaimportowanego modelu. Ten model nie może mieć `Animator`
   grającego własne ścieżki (u Zwiadowcy `Humanoid` importu go dostanie, jeśli ktoś go doda), bo nadpisałby `Transform`.
   Obrys „skorupa” działa tylko dla brył-klocków, więc importy dostają tryb „highlight”. Przesunięcie korzenia
   `wpis.hrp` trzeba zmierzyć od nowa, bo `HumanoidRootPart` importu może stać gdzie indziej niż w rigu z klocków.
   Punkty `Punkt_*` (broń, pocisk, pierś) to zaczepy dodawane kodem, więc można je przenieść na import z tych samych liczb.
5. **Niepewne:** czy `AnimationConstraint.Transform` i `Bone.Transform` da się wpisywać ze skryptu co klatkę i czy
   Studio to rysuje. Prototyp v1 (`swiat/test_walki_roblox/zrodla/OdtwarzaczWalki.luau`) przy stawach
   `AnimationConstraint` awatarów obraca `Attachment0.CFrame`, ale tylko jako nakładkę na animacje grane przez
   Animator Roblox, a nie jako cały odtwarzacz. Jako zapasowa droga dla Zwiadowcy to też jest niesprawdzone.

**Opublikowana gra (później).** Że droga C działa po publikacji, to założenie (wyżej). Kosztem są dane klipów
w kodzie (pliki `dane/<klucz>.json` mają dziś 0,21–0,45 MB i jako moduł trafiają do każdego klienta) oraz liczenie
stawów w Luau co klatkę (do 37 kości na aktora).
Oba koszty trzeba zmierzyć na telefonie. Zasoby Animation (droga B) będą potrzebne wtedy, gdy zechcemy mieszać klipy
z animacjami Roblox awatara gracza (Zwiadowca jako postać gracza z `Humanoid`) albo zrezygnować z danych w kodzie.
Wtedy właściciel gry wgrywa animacje na swoje konto albo grupę. To osobna decyzja do zapisania w sejfie jako propozycja.

### 3.3 Jak sprawdzamy skórę, świecenie i przód (c)

- **Skóra slime'a.**
  1. Kontrola struktury: kości `Dol`, `Gora` i `Cialo` muszą być w modelu jako `Bone`. W wariancie „sztywne części”
     kości `Cialo` i `Gora` nie mają siatki i znikają, więc ocena daje wtedy „niezgodny”.
  2. Sonda `--sonda-skory` odczytuje w Studio wagi siatki `Dol` przez `EditableMesh`, niczego nie wgrywając ani nie
     zmieniając. **Zaliczone**, gdy udział wierzchołków na dwóch kościach wynosi co najmniej 0,875 (0,9 × 0,972 z GLB),
     a wagi należą do kości `Dol` i `Gora`. **Niezaliczone**, gdy udział jest mniejszy (np. 0, czyli wszystko na jednej
     kości). Gdy API nie odpowie, wynik jest „nieznany” i decyduje próba pozy. Gdy sonda nie dojdzie do siatki (inne
     miejsce, brak kontenera, modelu albo siatki `Dol`), wynik to „błąd”: o skórze nic jeszcze nie wiadomo.
     Ile wierzchołków ma siatka po imporcie, nie wiadomo (Roblox może je łączyć albo dzielić inaczej niż GLB), dlatego
     próg dotyczy udziału, a nie liczby.
  3. Próba pozy (krok S8): kość `Gora` w dół o 1,35 studa. **Zaliczone**, gdy góra galarety opada, a spód zostaje.
     **Niezaliczone**, gdy kość się ruszyła, a galareta stoi albo przesuwa się w całości. Założenie: tryb Edit rysuje
     skórę od razu (niesprawdzone).
- **Świecenie.** Po imporcie muszą się odnaleźć po nazwie wszystkie siatki z kolumny „w całości świecące” z rozdz. 2.3
  (Muchomornik 13, Strażnik 2, Slime 9). Inaczej ocena daje „niezgodny”, bo Neon nie miałby na co trafić. Samo świecenie
  (Neon, `PointLight` na zaczepach oczu i kryształu) dokłada się dopiero po decyzji o wyglądzie i nie jest warunkiem tego
  etapu. W tabeli wyniku zostaje materiał każdej siatki (`mat`).
- **Przód.**
  - KONTROLA mierzy przód z pary punktów, które w danych leżą wzdłuż +Z, i lewą stronę z pary wzdłuż +X. Pary i odstępy
    w danych: Troll `Szczeka→Tulow` 2,95, Wilk `Glowa→Zad` 3,24, Muchomornik `Broda→Glowa` 0,52, Strażnik
    `Krysztal→Tulow` 2,04, Slime `Przod→Tyl` 1,84. Lewe-prawe pary dają od 0,80 do 6,60 studa. Zwiadowca ma pary R15.
  - Naprawa obraca model o różnicę między zmierzonym przodem a kierunkiem na punkt wejścia. Dlatego sprawdzenie
    „przód po naprawie ≤ 10°” przechodzi zawsze, gdy pomiar się udał. Mówi tylko, że pomiar i obrót zadziałały,
    a nie, że import patrzy dobrze. **O imporcie mówią naprawdę dwie rzeczy:** „lewa po lewej” (obrót nie zmienia
    stron, więc NIE znaczy lustro) i zrzut, na którym widać, czy zmierzony przód jest prawdziwym przodem (pysk, twarz).
  - Obrót wykonany przy naprawie jest zapisywany. Około ±180° znaczy, że FBX patrzył tyłem, a około ±90°, że bokiem.
    Trzeba to uwzględnić w przeliczeniu osi stawów (rozdz. 3.2 pkt 2).

### 3.4 Kiedy model jest zrobiony (d)

Model jest zrobiony, gdy ocena w `wynik/_roblox/import_lasu.txt` ma werdykt **ZGODNY** i człowiek obejrzał dwa zrzuty
(rozdz. 5, kroki S3–S6). Liczby pochodzą z `raport.json` i GLB.

| Sprawdzenie | Zwiadowca | Troll | Wilk | Muchomornik | Strażnik | Slime |
|---|---|---|---|---|---|---|
| `MeshPart` (dokładnie) | 15 | 17 | 21 | 28 | 36 | 25 |
| szkielet | `Humanoid` 1, stawy 15 | 17 `Bone` albo 17±1 stawów | 21 `Bone` albo 21±1 | 28 `Bone` albo 28±1 | 36 `Bone` albo 36±1 | **27 `Bone`** (sztywne części = niezgodny) |
| rodzice kości jak w GLB, głębokość (−1 = Root zamieniony na część, +1 = dodatkowa kość nad Root) | — | 5 … 7 | 4 … 6 | 5 … 7 | 4 … 6 | 3 … 5 |
| wzrost przed naprawą (±2%) | 5,76 | 9,94 | 4,36 | 3,60 | 14,54 | 3,38 |
| szerokość × głębokość (±5% albo 0,25) | 2,66 × 4,23 | 6,23 × 12,71 | 2,17 × 7,67 | 2,67 × 2,95 | 4,94 × 8,90 | 3,29 × 3,82 |
| zaczepy (bez RootAttachment) | 18 standardowych R15 | Glowa, Pysk, Maczuga | Glowa, Pysk | Glowa, Chmura, Laska | Glowa, Krysztal, PiescL, PiescP, Korzenie | Glowa, Pysk, Plusk |
| siatki do świecenia odnalezione | — | — | — | 13 | 2 | 9 |
| kolor | każda siatka ma teksturę albo `SurfaceAppearance` | ← | ← | ← | ← | ← |
| przód po naprawie (tylko pomiar, rozdz. 3.3) / lustro | ≤ 10°, lewa po lewej | ← | ← | ← | ← | ← |
| podłoże (y spodu) | −0,4 … 0,8 (bruk 0,2) | ← | ← | ← | ← | ← |
| skóra | — | — | — | — | — | sonda ≥ 0,875 albo próba pozy |

Zaczep liczy się pod nazwą `XAttachment`, `X_Att` albo `X`, bo nie wiadomo, jak importer nazwie znaczniki przy własnym
szkielecie. Tabela wyniku zapisuje, która forma wyszła.

## 4. Narzędzie `roblox_import_lasu.py`

| Polecenie | Co robi | Kontakt |
|---|---|---|
| `python -B swiat/postacie/roblox_import_lasu.py` | plan sześciu modeli: plik, rozmiar, sha256, stan wcześniejszego wgrania, fakty, oczekiwane sprawdzenia | żaden (nie importuje nawet `studio_mcp`) |
| `… --tylko zwiadowca` | plan wybranych | żaden |
| `… --tylko zwiadowca --tak-wgraj` | wgranie, wstawienie, kontrola, naprawa, zrzuty i ocena jednego modelu | Studio i Open Cloud **przez `roblox_import.main`** |
| `… --tylko a,b,c --tak-wgraj` | kilka po kolei (kolejność zawsze z KOLEJNOSC); stop na pierwszym przerwaniu albo niezgodności | jw. |
| `… --tak-wgraj` bez `--tylko` | **odmowa** (kod 2), nic nie wysyła | żaden |
| `… --tylko <id> --tak-wgraj --mimo-kolejnosci` | wgranie mimo wcześniejszego modelu bez werdyktu „zgodny”; tylko po decyzji właściciela | jw. |
| `… --sonda-skory` | wagi skóry siatki `Dol` zaimportowanego slime'a; kod 0 TAK, 1 NIE, 2 BŁĄD, 3 NIEZNANY | Studio, tylko odczyt |

- Opcji nie da się skracać (`--tak` to błąd, a nie wgranie).
- Przed każdym wgraniem narzędzie sprawdza bez Studio: plik istnieje i ma sha256 wersji przyjętej, raport i GLB się
  czytają, model nie jest w `roblox_postac.ROZMIESZCZENIE`, a wcześniejsze modele z kolejności są „zgodne”.
  Każdy brak zatrzymuje przed wysłaniem czegokolwiek.
- Logiki wgrywania tu nie ma. Narzędzie woła `roblox_import.main([... "--tak-wgraj"], profil=…)`, więc plik stanu,
  wznowienie, moderacja i wybór nowego modelu działają tak samo jak u Rycerza.
- **Wznowienie.** Model z werdyktem „zgodny” dla tego samego zasobu jest pomijany. Jeśli plik wyniku ma już ten sam
  numer zasobu co plik stanu, model jest oceniany z pliku i nie jest wstawiany drugi raz (każde wstawienie dokłada kopię
  w kontenerze). Resztę wznawia sam `roblox_import.py` z pliku stanu.
- **Przejścia pliku stanu** (`wynik/_roblox/wgranie_<id>_fbx.json`), sprawdzone czytaniem kodu i testem
  `test_roblox_import.py` (scenariusze A–Q):

  | Przerwanie | Co jest w pliku stanu | Co zrobi to samo polecenie |
  |---|---|---|
  | przed wysłaniem albo w trakcie (zanim przyszedł numer operacji) | etap `wysylanie` (zapisany PRZED wysłaniem) albo `nieznane` | **stop bez wgrania**: nie wiadomo, czy zasób powstał. Creator Dashboard; znaleziony zasób wstawia `roblox_import.py --modul <id> --asset <numer>` |
  | po wysłaniu, numer operacji zapisany, operacja trwa dłużej niż 4 min | etap `operacja` | czeka dalej na tę samą operację, nic nie wgrywa |
  | operacja skończona błędem | etap `operacja_blad` | stop bez wgrania; Creator Dashboard |
  | zasób jest, moderacja trwa dłużej niż 5 min | etap `zasob`, moderacja „Reviewing” itp. | czeka na moderację tego zasobu i wstawia go po zatwierdzeniu |
  | moderacja odrzuciła zasób | etap `zasob`, moderacja odrzucona | stop; drugiego wgrania tego pliku nie robi |
  | sukces | etap `zasob`, moderacja zatwierdzona, plik `import_<id>_fbx.json` | ocena z pliku, bez wstawiania; z werdyktem „zgodny” model jest pomijany |
  | po wstawieniu, a przed zapisem `import_<id>_fbx.json` (błąd przeniesienia albo kontroli) | etap `zasob` | **wstawia ten sam zasób drugi raz** pod nazwą „… #2”. Drugiego wgrania nie ma, ale w kontenerze zostaje kopia do ręcznego usunięcia |
  | nieudany zrzut | plik wyniku jest, z polem `bledy` | ocena z pliku daje „niezgodny” (błędy kroków), bez wstawiania. Zrzut robi się wtedy ręcznie i decyzję podejmuje człowiek |
- **Wynik:** `wynik/_roblox/import_lasu.json` i `import_lasu.txt` (werdykt, zasób, nazwa modelu, rodzaj szkieletu,
  każde sprawdzenie z liczbą). Numeru konta tam nie ma, bo ten zostaje tylko w plikach stanu, które są poza gitem.
  Zrzuty lądują w `import_<id>_fbx_0.png` i `_1.png`, a pełne dane w `import_<id>_fbx.json`.
- **Miejsce w Studio:** pas rynku między studnią a straganami 2, 3 i 5, w układzie miasta (świat ma −700 w Z). Wilk
  stoi w (−14; −15), Muchomornik w (−5; −17), Zwiadowca w (3; −18), Troll w (13; −14), Strażnik w (28; −15), a Slime
  w (36; −8). Wszyscy patrzą na punkt wejścia. Miejsca wyliczono z `swiat/krzywe_miasteczko/uklad.json` i w Studio ich
  nie oglądano. Po kontroli obrys każdego modelu ma co najmniej 3 studa do obrysu straganów i studni i do sąsiadów
  (wcześniej Troll miał 1,3 studa do straganu 3, a Zwiadowca i Troll 0,4 studa między sobą). Daszki straganów i to, co
  stoi w miejscu, a nie ma tego w `uklad.json`, pokaże dopiero zrzut.
- Sprawdziany bez Studio: `biblioteka/test_roblox_import.py` (wgrywanie i zgodność wstecz) oraz
  `biblioteka/test_roblox_import_lasu.py`. Ten drugi sprawdza plan na prawdziwych plikach i ocenę na prawdziwym wyniku
  Rycerza, która ma dać „zgodny”, a osiem zepsutych kopii tego wyniku ma dać „niezgodny”. Sprawdza też warianty
  szkieletu i wznowienie na udawanym imporcie.

## 5. Lista kroków w Studio (po kolei)

Wszystkie polecenia uruchamia się w terminalu w katalogu głównym repozytorium (tam, gdzie leży folder `swiat`).
Czas liczy się od chwili, gdy Studio jest wolne. Czasy są szacunkami. U Rycerza moderacja zatwierdziła zasób od razu.
Narzędzie czeka najwyżej 4 min na operację i 5 min na moderację, a potem samo staje (wznowienie: to samo polecenie).

| Krok | Co zrobić | Czego oczekiwać | Kiedy stop | Czas |
|---|---|---|---|---|
| **S0** | Sprawdź, że inny agent skończył pracę w Studio. Studio jest w trybie **Edit** (nie Play), otwarte jest miejsce gry, w `Workspace` stoi `TestPostaci` z atrybutem `Wygenerowane = true`. W Assistant → Settings → MCP Permissions są włączone `asset:read` i `asset:write`, a folder `swiat/postacie/wynik` jest na liście approved upload directories (zatwierdzony 13.11) | wszystko na miejscu | brak `TestPostaci`: nie budować go samemu, tylko zapytać właściciela (budowa to `python -B swiat/postacie/roblox_postac.py`) | 3 min |
| **S1** | `python -B swiat/postacie/roblox_import_lasu.py` | sześć bloków `[1/6] zwiadowca` … `[6/6] lesny_slime`; w każdym wierszu `plik:` napis „(wersja przyjęta 15.11)”, a w wierszu `stan:` „brak pliku … pierwsze wgranie”; na końcu „braków 0”; kod wyjścia 0 | kod 1, słowo `BRAK` albo „INNY NIŻ PRZYJĘTY”: **stop, zapytaj właściciela** (plik przebudowano po przyjęciu) | 1 min |
| **S2** | `python -B swiat/postacie/biblioteka/test_roblox_import.py`, potem `python -B swiat/postacie/biblioteka/test_roblox_import_lasu.py` | oba kończą się wierszem `WYNIK: ZGODNE` | `WYNIK: NIEZGODNE`: stop, nic nie wgrywać | 1 min |
| **S3** | `python -B swiat/postacie/roblox_import_lasu.py --tylko zwiadowca --tak-wgraj` | kolejno: „wgrano, operacja …”, „zasób …, moderacja: … (zatwierdzony)”, `klasy:` z `MeshPart 15`, `Humanoid 1`, `AnimationConstraint 15`, `wymiary:` z wysokością ok. 5,76, `naprawa: postawiono w (…; 0,2…0,3; …)`, dwa wiersze `zrzut:` i na końcu `WERDYKT zwiadowca: ZGODNY (szkielet: R15)`. **Na zrzutach** `wynik/_roblox/import_zwiadowca_fbx_0.png` i `_1.png`: cała postać w kadrze, stoi na bruku, kolory jak na `wynik/zwiadowca/zwiadowca_plansza.jpg`, nic szarego, twarz zwrócona mniej więcej do kamery na zrzucie 0, strony jak na planszy (brak lustra), bez łuku i sztyletu | `WERDYKT … NIEZGODNY`, „NIE WIADOMO, CZY ZASÓB POWSTAŁ”, „ODRZUCONY”, postać w straganie albo tyłem na zrzucie: **stop, zapytaj właściciela** (rozdz. 6) | 5–8 min |
| **S4** | `python -B swiat/postacie/roblox_import_lasu.py --tylko lesny_troll --tak-wgraj` | `WERDYKT lesny_troll: ZGODNY (szkielet: …)`. W nawiasie jest „kości (Bone)” albo „sztywne części ze stawami”. Na zrzutach maczuga w prawej dłoni trolla (strona −X danych), garb z grzybami z tyłu | **zawsze stop po tym kroku:** wyślij właścicielowi rodzaj szkieletu i oba zrzuty. Dalej dopiero po jego odpowiedzi | 6–9 min + odpowiedź właściciela |
| **S5** | `python -B swiat/postacie/roblox_import_lasu.py --tylko cierniowy_wilk,muchomornik,straznik_gaju --tak-wgraj` | trzy razy `WERDYKT …: ZGODNY`, w kolejności wilk, muchomornik, strażnik. Na zrzutach: wilk pyskiem w stronę kamery, zarodniki na kapeluszu muchomornika, cały Strażnik w kadrze (kamera ×2,55) | narzędzie samo staje na pierwszej niezgodności albo przerwaniu; wtedy **stop, zapytaj właściciela**. „STOP przed wgraniem … nie mają jeszcze werdyktu „zgodny””: Troll nie jest „zgodny”; dalej tylko po decyzji właściciela, z `--mimo-kolejnosci` | 12–20 min |
| **S6** | `python -B swiat/postacie/roblox_import_lasu.py --tylko lesny_slime --tak-wgraj` | `WERDYKT lesny_slime: ZGODNY (szkielet: kości (Bone))`; w ocenie `[tak    ] kości Bone (bez Root)` z liczbą 27, więc są też `Cialo` i `Gora` | „sztywne części” albo brak kości `Cialo`/`Gora`: skóra przepadła, **stop, zapytaj właściciela** (ryzyko 6) | 5–8 min |
| **S7** | `python -B swiat/postacie/roblox_import_lasu.py --sonda-skory` | `Sonda skóry …: TAK — udział … (GLB 0.972, próg 0.875); kości wag: Dol, Gora`, kod 0 | kod 1 (NIE): **stop**. Kod 2 (BŁĄD): sonda nie doszła do siatki; usuń przyczynę z komunikatu (miejsce, kontener, nazwa) i powtórz. Kod 3 (NIEZNANY): przejdź do S8 | 2 min |
| **S8** | Tylko wtedy, gdy S7 dało NIEZNANY. Wklej kod niżej w pasek poleceń Studio (View → Command Bar), w trybie Edit, i patrz na slime'a | przez 5 s góra galarety jest niżej o ok. 1,35 studa, a spód zostaje na ziemi; potem wszystko wraca samo, a w Output jest „Import lasu: próba skóry skończona” | galareta stoi albo przesuwa się w całości: najpierw sprawdź w Output, że kość się ruszyła (wiersz „kość Gora: … → …”). Jeśli kość się ruszyła, a galareta nie: skóra przepadła, **stop** | 5 min |
| **S9** | Przejrzyj `wynik/_roblox/import_lasu.txt` i 12 zrzutów `wynik/_roblox/import_<id>_fbx_0.png` i `_1.png`. Raport dla właściciela przygotowuje osobny krok (panel) | sześć wierszy `ZGODNY` | — | 10 min |

**Razem: ok. 45–65 minut pracy** (S0–S9; z próbą pozy S8 do 70 minut). Do tego dochodzi czas odpowiedzi właściciela po S4.
Czekanie na wgranie i moderację to zwykle 1–3 min na model; jeśli moderacja się przeciąga, narzędzie po 9 minutach
staje, a to samo polecenie później wznawia bez drugiego wgrania. Przykład: gdy Studio zwolni się o 16:30, a właściciel
odpowie po Trollu w ciągu 15 minut, koniec wypada ok. 17:30–17:50.

Próba pozy (S8) sprawdza najpierw miejsce gry i kontener, robi punkt historii przed zmianą i po niej, a po 5 s
przywraca położenie kości:

```lua
local MODEL = "Leśny Slime (import FBX)" -- albo nazwa z wiersza „model:” w wyniku S6, np. „… #2”
local CH = game:GetService("ChangeHistoryService")
if game.PlaceId ~= 129485428021967 then
	warn("To nie jest miejsce gry (PlaceId " .. tostring(game.PlaceId) .. ") — nic nie zmieniono")
	return
end
local kont = workspace:FindFirstChild("TestPostaci")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	warn("Brak kontenera TestPostaci z atrybutem Wygenerowane — nic nie zmieniono")
	return
end
local m = kont:FindFirstChild(MODEL)
local gora = m and m:FindFirstChild("Gora", true)
if not (gora and gora:IsA("Bone")) then
	warn("Nie ma kości Gora w modelu " .. MODEL .. " — nic nie zmieniono")
	return
end
CH:SetWaypoint("Import lasu: przed próbą skóry")
local start = gora.WorldPosition
gora.WorldPosition = start + Vector3.new(0, -1.35, 0)
print(string.format("kość Gora: %.2f → %.2f (y)", start.Y, gora.WorldPosition.Y))
task.wait(5)
gora.WorldPosition = start
CH:SetWaypoint("Import lasu: po próbie skóry")
print("Import lasu: próba skóry skończona")
```

Założenie w S8: Studio w trybie Edit od razu rysuje skórę po przesunięciu kości. Tak robi Animation Editor, ale tutaj
tego nie sprawdzano. Dlatego najpierw trzeba zobaczyć w Output, że sama kość się ruszyła.

## 6. Kiedy stanąć i zapytać właściciela

- Werdykt któregoś modelu jest NIEZGODNY. Narzędzie staje samo, a w tabeli widać, które sprawdzenie nie przeszło.
- Pojawi się komunikat „NIE WIADOMO, CZY ZASÓB POWSTAŁ”, moderacja odrzuci zasób albo operacja skończy się błędem.
  Trzeba wtedy sprawdzić Creator Dashboard (Development Items → Models) i niczego nie wgrywać na ślepo.
- Plan pokazuje BRAK, na przykład „INNY NIŻ PRZYJĘTY” przy sha256 albo model w `ROZMIESZCZENIE`. Narzędzie i tak
  odmówi wgrania.
- „STOP przed wgraniem”: wcześniejszy model z kolejności nie jest „zgodny”. Dalej tylko po decyzji właściciela,
  z `--mimo-kolejnosci`.
- Po Trollu (S4) zawsze, bo rodzaj szkieletu decyduje o dalszej pracy nad odtwarzaczem.
- Skóra slime'a przepadła (S6, S7 = NIE albo S8).
- Na zrzucie model wchodzi w stragan albo budynek albo stoi tyłem. Model jest już wtedy wstawiony, więc przesuwa się
  go ręcznie w Studio, a nie wstawia drugi raz.
- W kontenerze pojawi się kopia „… #2” (przerwanie po wstawieniu, rozdz. 4). Kopię usuwa się ręcznie; zasób jest jeden.
- Zanim cokolwiek pójdzie do publikacji miejsca: zasoby są na koncie osoby zalogowanej w Studio i trzeba je udostępnić
  grze właściciela w Creator Dashboard. Kontener `TestPostaci` usuwa się przed publikacją.

## 7. Ryzyka (od najbardziej prawdopodobnego) i wyjścia awaryjne

| # | Ryzyko | Jak to wyjdzie | Wyjście |
|---|---|---|---|
| 1 | Emisja się nie przeniesie (prawie pewne) | modele bez świecenia na zrzutach | Neon na siatkach w całości świecących (rozdz. 2.3), `PointLight` albo `ParticleEmitter` na zaczepach oczu, kryształu i zarodników. Decyzja o wyglądzie należy do właściciela |
| 2 | Zasoby są na koncie osoby zalogowanej w Studio, a wstawiony model jest pakietem z `PackageLink` (u Rycerza tak było) | pewne; przeszkadza dopiero przy szablonach aktorów i publikacji | udostępnienie zasobów grze w Creator Dashboard przed publikacją; decyzja, czy `PackageLink` zostaje |
| 3 | Importer potraktuje własny szkielet inaczej niż R15: zmieni nazwy kości albo siatek, złączy siatki w jedną część, zamieni `Root` na część albo doda własny korzeń | ocena: zła liczba `MeshPart`, brak kości, inni rodzice. Głębokość drzewa o 1 mniejsza albo większa jest dopuszczona | gdy zmieniły się tylko nazwy, wystarczy tabela nazw w odtwarzaczu. Gdy siatki są złączone albo kości zgubione, ten jeden potwór zostaje przy rigu z klocków z prototypu (działa dziś), a import zostaje w kontenerze do porównania |
| 4 | Znaczniki `_Att` nie zamienią się w `Attachment` (wyjdą jako zwykłe `MeshPart`) albo dostaną inne nazwy; u Rycerza przepadł już `RootAttachment` | ocena: punkt „znaczniki _Att jako MeshPart” i „zaczepy” na NIE; werdykt NIEZGODNY | zaczepy dodaje się kodem z liczb modułu (położenie i obrót są w danych), tak jak dziś punkty `Punkt_*` w prototypie. Kolejne modele z tym samym objawem idą wtedy po jednym, z `--mimo-kolejnosci`, po decyzji właściciela |
| 5 | `EditableMesh` nie odczyta wag: inna nazwa metody (nazwy są z pamięci), brak uprawnień do siatki albo wyłączone API siatek w ustawieniach gry | sonda daje NIEZNANY (kod 3) | próba pozy S8 |
| 6 | `Transform` stawów importu nie daje się wpisywać ze skryptu albo Studio go nie rysuje | pierwsza próba odtwarzacza na imporcie (po tym etapie) | `AnimationConstraint`: obrót `Attachment0.CFrame` jak w prototypie v1. `Bone`: wpisywanie `Bone.CFrame`. Ostatecznie droga B (zasoby Animation, po decyzji o własności) |
| 7 | Miejsce na rynku koliduje ze straganem, budynkiem albo czymś, czego nie ma w `uklad.json` | zrzut, podłoże y > 0,8 | ręczne przesunięcie w Studio. Na przyszłość można zmienić `PROFILE[…]["miejsce"]` w narzędziu. Według `uklad.json` (studnia 18 × 18 obrócona o 50°, stragany 10 × 7) każdy model ma co najmniej 3 studa zapasu |
| 8 | Skóra slime'a przepadnie (wagi na jednej kości albo sztywne części) | S6, S7, S8 | slime importuje się jako sztywne części: eksport z `Dol_Geo` podzielonym na dolną i górną siatkę (zmiana w module, po zgodzie właściciela) albo zostaje przy rigu z klocków, gdzie zgniatanie udaje dziś `SpecialMesh` |
| 9 | FBX patrzy tyłem albo bokiem | wiersz „obrót przy naprawie” pokaże ok. ±180° albo ±90°; zrzut | naprawa obraca model sama. Przeliczenie osi stawów w odtwarzaczu (rozdz. 3.2 pkt 2) obejmuje to pomiarem R |
| 10 | Moderacja trwa długo albo odrzuci zasób | „czeka na moderację”, „ODRZUCONY” | to samo polecenie później wznowi pracę bez wgrywania. Odrzucenie znaczy: stop i pytanie do właściciela |
| 11 | Skala nie wyjdzie 1:1 (u Rycerza wyszła 1:1) | „wzrost przed naprawą” i „skala przy naprawie” na NIE | naprawa wyrównuje wzrost, ale wtedy przesunięcia z klipów trzeba mnożyć przez skalę, więc to stop i decyzja |
| 12 | Przerwane połączenie ze Studio w trakcie wgrywania | „NIE WIADOMO, CZY ZASÓB POWSTAŁ” | Creator Dashboard. Znaleziony zasób wstawia się przez `roblox_import.py --modul <id> --asset <numer>` (to niczego nie wgrywa) |
| 13 | Przerwanie po wstawieniu, a przed zapisem wyniku | w kontenerze kopia „… #2” po wznowieniu | ręczne usunięcie kopii; zasób jest jeden |

## 8. Co uruchomiono bez Studio (15.11.2026) i wyniki

- `python -B swiat/postacie/biblioteka/test_roblox_import.py` daje „WYNIK: ZGODNE”, a wśród scenariuszy są nowe
  R i S (zgodność wstecz i profil). Wersja tego testu z HEAD też przechodzi na nowym `roblox_import.py`.
- `python -B swiat/postacie/biblioteka/test_roblox_import_lasu.py` daje „WYNIK: ZGODNE”: plan, ocena Rycerza
  (zgodny, osiem zepsutych kopii niezgodnych), warianty szkieletu (także `Root` zamieniony na część i znaczniki `_Att`
  jako `MeshPart`), sonda, wznowienie i bezpieczniki wgrania z rozdz. 2.6. Za pierwszym razem test znalazł błąd
  w wyliczaniu miejsca, bo odsunięcie o 6,5 studa liczone z celu, a nie z „poz”, chybiało o 1,2 studa. Poprawione.
  Siedem celowo zepsutych wersji narzędzia (każdy bezpiecznik z rozdz. 2.6 wyłączony po kolei) test wykrył wszystkie.
- `python -B swiat/postacie/roblox_import_lasu.py` drukuje sześć pełnych wierszy, przy każdym pliku „(wersja przyjęta
  15.11)”, „braków 0” i kończy się kodem 0. Pliki ważą razem 5,16 MB. sha256 (te same wartości są w narzędziu jako
  `PRZYJETE_SHA256`):

| Model | sha256 pliku FBX |
|---|---|
| zwiadowca | `2e46f26f2af037aaecb16fadbc28e159a5780712dbd76eadf483754802a27624` |
| lesny_troll | `9a7d7c3d894e5da8742e24da501b530384f52cb8f08f86178297ff47652c67f1` |
| cierniowy_wilk | `b3b8845eb2d7c664cb9fb1ef11143fb273d04fa94cce935c480797f30b7dd72c` |
| muchomornik | `e8d7dd6c8d673b14ce9a52a00e781d1b05e62e0125f566055503ace69a80db18` |
| straznik_gaju | `f7dc8f428fb3b8dd57157f85a561fe563aef6f57431f26d1ed4d14c23a1947c2` |
| lesny_slime | `e57cb1df744dd1908e573f71145e684e76304596d08dfc5d2ce077305e72e1a4` |

**Kod Luau, który narzędzie wyśle.** Sprawdzono go czytaniem, bo bez Studio nie da się go skompilować:

- `roblox_import.py`: KTO, SPIS, PRZENIES i NAPRAWA bez zmian (działały 13.11) oraz KONTROLA po zmianie;
- `roblox_import_lasu.py`: SONDA SKORY (najpierw `game.PlaceId`, potem kontener z atrybutem `Wygenerowane`, potem
  tylko odczyt; `EditableMesh` niszczy na końcu);
- kod próby pozy z rozdz. 5 (po kontroli też najpierw sprawdza `PlaceId` i atrybut `Wygenerowane`).

Kontrola przeczytała każdy z tych kodów jeszcze raz: bloki `if`/`for`/`function` są domknięte, każde `nil`
(brak kontenera, modelu, części stawu, zaczepu) jest obsłużone przed użyciem, a kod dotyka tylko
`Workspace/TestPostaci`. KTO, SPIS i KONTROLA tylko czytają; PRZENIES i NAPRAWA zmieniają wyłącznie nowo
wstawiony model w kontenerze. Miejsce gry i to, że `TestPostaci` jest jeden i ma atrybut `Wygenerowane`, sprawdza
`roblox_import.py` po stronie Pythona (wynik KTO) przed każdym innym wywołaniem, a więc i przed wgraniem. Same SPIS,
PRZENIES, KONTROLA i NAPRAWA miejsca już nie sprawdzają; idą w tej samej sesji zaraz po KTO.

Składnia (`for … in t do`, `+=`, `if … then … elseif`, domknięcia) jest taka jak w działającym kodzie obok. Pewności
nie ma co do tych wywołań API (wszystkie w sondzie są w `pcall`):

- `AssetService:CreateEditableMeshAsync(Content.fromUri(meshId))`: forma z `Content` i to, czy wolno otworzyć siatkę
  z konta współpracownika;
- `EditableMesh:GetBones`, `GetBoneName`, `GetVertexBones`, `GetVertexBoneWeights`: nazwy według pamięci, niesprawdzone;
- zapis `Bone.WorldPosition` w trybie Edit i to, czy Studio od razu przelicza skórę;
- zapis `AnimationConstraint.Transform` i `Bone.Transform` ze skryptu (dotyczy odtwarzacza, nie tego etapu);
- czy `HttpService:JSONEncode` przyjmie listę `kosci_drzewo` z polem logicznym `kr` (powinien, bo to zwykłe tabele).
