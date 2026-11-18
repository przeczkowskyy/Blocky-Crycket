# Bohater w świecie — gracz chodzi bohaterem swojej klasy

> **Status: propozycja (prototyp w Studio), nie kanon i nie kod gry.** Projekt, powody wyborów i sprawy do decyzji:
> `PROJEKT.md`. Przed publikacją miejsca: `python -B swiat/bohater_swiat/zbuduj.py --usun`.

Po wyborze klasy gracz chodzi po świecie bohaterem swojej klasy (Wojownik = Rycerz, Zwiadowca, Mag = Kot-Mag)
w stroju, który ma założony, zamiast awatara Roblox. Bohater stoi w spoczynku, idzie i biegnie w tempie postaci,
skacze, spada i ląduje. Każdy gracz widzi bohaterów pozostałych graczy. Przed wyborem klasy widać awatara, jak dotąd.

## Stan (18.11.2026)

- **Zbudowane w Studio:** `Workspace/BohaterSwiat` (9 instancji: 4 skrypty i moduły, 3 sygnały, 0 części), wyłącznik
  `BohaterWSwiecie = true`. Miejsce nie było zapisywane ani publikowane.
- **Próba w Play** (`testy/proba_play.py`, lista B00–B19): **19 × OK, 1 × ?, 0 × BŁĄD** — tabela niżej.
- **Sąsiedzi z bohaterem w świecie:** próba dymna całej gry 14/14, próba walki `test_walki_play.py --szybko` 111/111,
  próba przymierzalni 10 × OK i jej stałe „?” (S09).
- **Bez Studio:** 33 testy OK, kontrola Luau, `zbuduj.py --sucho`, `proba_play.py --sprawdz`.

## W Studio (18.11.2026)

Próba: jedno okno Studio, jeden gracz (Wojownik po wyborze klasy klawiszem Enter), tryb z kowalem na próbę (gracz ma
część przedmiotów). Wyniki z nazwą konta leżą poza repozytorium.

| Punkt | Wynik |
|---|---|
| B00 kontener w Edit | OK — skrót danych = lokalny, 4 skrypty, 0 części, zależności i wszystkie dodatki na miejscu |
| B01 przed wyborem klasy | OK — bohaterów 0, awatar widoczny (16 części), `RuchBohatera "stan"` → `nil` |
| B02 wybór klasy → bohater | OK — Wojownik w stroju gracza: 120 brył = dane, 293 instancje, budowa 3 ms; awatar: 0 części widocznych |
| B03 fizyka postaci | OK — 0 części bohatera w fizyce, korzeń zakotwiczony; masa 13,940 / 13,940, HipHeight 2,00 / 2,00, WalkSpeed 16 / 16, skok 7,2 / 7,2 (z bohaterem / bez) |
| B04 stopy na ziemi | OK — stopy 0,000 st nad ziemią, bohater 0,000 st od punktu pod postacią, przód zgodny |
| B05 ruch (prawdziwy W) | OK — spoczynek → bieg → spoczynek, do 16 st/s, stopy −0,13…0,14 st względem ziemi pod postacią (plac ma stopnie do 0,32 st); droga z W przez 1 s: 16,3 st z bohaterem i 16,3 st bez |
| B06 skok (spacja) | OK — skok → spadanie → lądowanie → spoczynek, wzniesienie 7,3 st |
| B07 wyłącznik | OK — `false`: bohater znika, awatar wraca (16 części), `"stan"` → `nil`; `true`: bohater wraca (po 0,2 s razem z zapytaniami próby) |
| B08 trzy klasy | OK — Wojownik 121 brył / 294 instancje (budowa 3 ms), Zwiadowca 133 / 318 (27 ms), Mag 145 / 361 (31 ms) — w strojach z przedmiotów, które gracz ma |
| B09 strój z przymierzalni | OK — goły 74, mieszany 107, komplet 127 brył = dane; stopy 0,000 st |
| B10 kowal | OK — nowy przedmiot z łupu (hełm) założył się sam: bohater w świecie 121 brył z hełmem |
| B11 reset postaci | OK — klip `upadek`, po odrodzeniu bohater wraca, awatar niewidoczny, pola ochronnego nie widać |
| B12 umowa `RuchBohatera` | OK — `stan`, pięć klipów, zły klip → `false`, `nil` → ruch samoczynny, `przesun (0, 2, 0)` → 2,00 st, postać stoi |
| B13 pet | OK — pet idzie za bohaterem: w biegu do 6,5 st, po zatrzymaniu ok. 5 st |
| B14 walka w lesie-pasie | OK — w walce bohater świata schowany, aktor walki w tym samym stroju (127 brył), po walce bohater wraca |
| B15 teleport przez chmury | OK — po przejściu bohater przy postaci, stopy 0,000 st, kamera gracza |
| B16 runda Training Center | ? — runda rusza, błędów nie ma, ale nikt w nią w tej próbie nie gra; całą rundę z bohaterem przechodzi próba dymna gry (D07 OK) |
| B17 wielu bohaterów | OK — 12 bohaterów (1861 brył; 2 postacie poza zasięgiem bez bohatera): pętla pakietu 0,3–0,9 ms średnio na klatkę w czterech przebiegach (najwięcej 3,3 ms); 1 bohater: 0,05–0,14 ms; 60 kl./s bez bohatera, z jednym i z dwunastoma |
| B18 konsola | OK — 0 wierszy `[BohaterSwiat]`, 0 błędów pętli |
| B19 cykl biegu | OK — stopa w podporze stoi w miejscu: w zatrzymanych fazach 0,000 st, w prawdziwym biegu 16 st/s klatka po klatce 0,000 st (Wojownik 7 podporów / 40 klatek, Zwiadowca 7 / 41, Mag 11 / 23) |

Skąd liczby: pełny przebieg na ostatniej wersji skryptów dał 17 × OK, „?” w B16 i 2 × BŁĄD (B05, B19) — droga biegu
trafiła wtedy w przeszkodę na placu (stopy do 0,99 st od ziemi pod postacią, w jednym podporze Rycerza przesunięcie
0,56 st). Próba wybiera teraz kierunek biegu promieniami (najdłuższa wolna i najrówniejsza droga od startu); po tej
zmianie B05, B06 i B19 przeszły na tej samej wersji skryptów. Próba dymna gry po ostatniej poprawce: 14/14. Próby
walki i przymierzalni szły wersję wcześniej (przed „korzeniem o klatkę później”, poprawką w samym ustawianiu modelu).

### Poprawione po zobaczeniu gry

1. **Ślizganie stóp w biegu.** Klip chodu z walki przy 16 st/s grał na granicy tempa i stopy jechały po ziemi.
   Powstał proceduralny cykl biegu (`PROJEKT.md` pkt 2.3).
2. **Stopa w biegu „pływała” o jedną klatkę** (do 0,27 st na podpór w pomiarze): silnik stosuje pozę stawów klatkę
   później niż położenie korzenia. Teraz korzeń bohatera też staje z miejscem z poprzedniej klatki
   (`ruch.korzen_klatke_pozniej`), a cykl biegu idzie drogą postaci, nie zegarem — pomiar 0,000 st.
3. **Poza skoku wracała na chwilę przy lądowaniu** (odbicie postaci w górę): kto już spada, wraca do pozy skoku
   dopiero przy wyraźnym wznoszeniu.
4. **Czubek stopy kota wchodził w ziemię w wymachu** — generator zmniejsza kąt stopy dla klasy, której stopa jest
   długa względem nogi.
5. **Próba:** przymierzalnia przy działającym kowalu zakłada tylko posiadane przedmioty (próba najpierw je daje),
   nowy przedmiot zakłada się sam po łupie (nie po zwykłym nadaniu), po wejściu do lasu-pasa trzeba przeczekać
   przelot kamery, runda treningu rusza tylko przy tablicy.

### Zrzuty (`klatki/`)

| Plik | Co widać |
|---|---|
| `01_bazar_bieg.jpg` | Rycerz w biegu na placu bazaru (klatka cyklu biegu) |
| `02_zza_plecow_kamera_gracza.jpg` | Rycerz od tyłu — tak, jak widzi go gracz zwykłą kamerą |
| `03_las_bieg.jpg` | Rycerz w biegu w lesie-pasie |
| `04_skok_w_powietrzu.jpg` | Rycerz w powietrzu, poza skoku |
| `05_obok_peta.jpg` | Rycerz i jego pet (ślimak) obok |
| `06_klasa_wojownik.jpg`, `06_klasa_zwiadowca.jpg`, `06_klasa_mag.jpg` | każda klasa w stroju gracza |
| `07_wylacznik_awatar.jpg` | wyłącznik `false`: awatar jak dawniej |
| `08_stroj_golas.jpg`, `08_stroj_mieszany.jpg`, `08_stroj_komplet.jpg` | strój z przymierzalni na bohaterze w świecie |
| `08_kowal_nowy_przedmiot.jpg` | hełm z łupu kowala założony sam |
| `09_upadek.jpg`, `09_po_odrodzeniu.jpg` | upadek po śmierci i bohater po odrodzeniu |
| `10_umowa_skok.jpg`, `10_umowa_padnij.jpg`, `10_umowa_rece_gora.jpg` | pozy mini-gier z umowy `RuchBohatera` |
| `11_wielu_bohaterow.jpg` | plac z bohaterami postaci testowych |
| `12_walka_w_lesie.jpg`, `12_po_walce.jpg` | walka (bohater świata schowany) i powrót po walce |
| `13_po_teleporcie.jpg` | po przejściu przez chmury |
| `14_trening.jpg` | stanowisko Training Center |
| `15_bieg_wojownik_arkusz.jpg`, `15_bieg_zwiadowca_arkusz.jpg`, `15_bieg_mag_arkusz.jpg` | osiem kolejnych klatek cyklu biegu przy 16 st/s, kamera nieruchoma w świecie — stopa w podporze zostaje w tym samym miejscu ziemi |

## Jak to działa

- **Kontener:** `Workspace/BohaterSwiat` (atrybut `Wygenerowane`): `Moduly/DaneBohatera` (wygenerowany),
  `Moduly/LogikaBohatera`, `SerwerBohatera`, `KlientBohatera`, `Sygnaly/RuchBohatera`, `Sygnaly/SterowanieSerwera`,
  `Sygnaly/SterowanieKlienta`. Żadnych części — bohaterów składa klient w grze, lokalnie (folder
  `BohaterowieLokalni`).
- **Postać Roblox zostaje** (fizyka, sterowanie, kamera, dotyk, podpowiedzi E, `HumanoidRootPart`, `WalkSpeed`).
  Jej części są u klienta niewidoczne (`Transparency = 1`, dawne wartości wracają po wyłączeniu).
- **Bohater** to osobny model z zakotwiczonym korzeniem, co klatkę ustawiany pod postacią: stopy na ziemi, przodem
  jak postać. Części bez kolizji, dotyku, zapytań i masy; bez spawu z postacią.
- **Klasa** z atrybutu gracza `Class` (`Warrior` / `Scout` / `Mage` — ekran wyboru klasy). **Strój** z atrybutu
  `StrojProba_<klasa>` (przymierzalnia, kowal); bez atrybutu — wygląd z walki. Zmiana klasy albo stroju → bohater
  przebudowany. Odrodzenie → bohater wraca przy nowej postaci.
- **Ruch:** klipy `idle` i `chod` / `ruch` bohatera z danych walki; skok, spadanie i lądowanie to pozy proceduralne.
  Powyżej prędkości, przy której klip chodu przestaje nadążać (Rycerz 6,2 st/s, Zwiadowca 14,3, kot 2,3), gra
  **proceduralny cykl biegu**: nogi z odwrotnej kinematyki tak, żeby stopa w podporze stała w miejscu, podskok
  bioder, wymach rąk, pochylenie tułowia (`PROJEKT.md` pkt 2.3; liczby w `ustawienia.json` → `bieg`).
- **Znika razem z awatarem:** walka, mini-gra i widok z pierwszej osoby chowają awatara przez
  `LocalTransparencyModifier` — bohater przejmuje tę wartość co klatkę.
- **Potrzebuje w grze** (tylko odczyt): `Workspace/TestWalki2` (`Moduly/Klipy`, `Moduly/DaneAktorow`)
  i `Workspace/StrojeProba` (`Moduly/Ubieranie`). Bez nich bohatera nie ma, awatar zostaje, bez błędów.

## Wyłącznik

Atrybut kontenera **`BohaterWSwiecie`** (domyślnie `true`). `false` → awatar jak dawniej, od razu, bez przebudowy:

```lua
workspace.BohaterSwiat:SetAttribute("BohaterWSwiecie", false)   -- w Edit (zostaje po odbudowie) albo na serwerze w grze
```

## Umowa z mini-grami: `Sygnaly/RuchBohatera`

`BindableFunction` u **klienta** (`Workspace/BohaterSwiat/Sygnaly/RuchBohatera`). Dotyczy bohatera lokalnego gracza.

| Wywołanie | Wynik |
|---|---|
| `Invoke("stan")` | `nil`, gdy lokalny gracz nie ma aktywnego bohatera; inaczej `{ aktywny = true, klasa = "wojownik" \| "zwiadowca" \| "mag", klip = "…" }` |
| `Invoke("klip", nazwa)` | `true`, gdy przyjęte. `nazwa`: `"bieg"` (bieg w miejscu, w pętli), `"skok"` (trzymana poza skoku), `"padnij"` (trzymana poza przysiadu), `"rece_gora"` (obie ręce w górze), `"radosc"` (klip `wiwat` bohatera raz, potem spoczynek). Trwa do zmiany. |
| `Invoke("klip", nil)` | `true` — powrót do ruchu samoczynnego |
| `Invoke("przesun", Vector3)` | `true` — bohater przesunięty względem postaci o ten wektor (układ postaci: X w prawo, Y w górę, −Z do przodu); od razu, bez wygładzania — podskok albo unik rysuje wołający, klatka po klatce |
| `Invoke("przesun", nil)` | `true` — bez przesunięcia |

Szczegóły:

- `klip` w `"stan"`: w ruchu samoczynnym `"idle"`, `"chod"`, `"bieg"`, `"skok"`, `"spadanie"`, `"ladowanie"` albo
  `"upadek"`; przy klipie wymuszonym — jego nazwa z umowy. Dodatkowe pole `wymuszony` (nazwa albo brak) odróżnia
  wymuszony `"bieg"` (w miejscu) od biegu samoczynnego.
- `false` zamiast `true`: nie ma aktywnego bohatera, nieznana nazwa klipu, `przesun` z czymś innym niż `Vector3`.
  Nieznane polecenie → `nil`.
- Każde `Invoke("klip", "radosc")` gra wiwat od nowa.
- Przesunięcie dłuższe niż 30 st jest skracane do 30; `NaN` → zero.
- Wymuszony klip i przesunięcie **zerują się**, gdy lokalny bohater znika (odrodzenie postaci, wyłącznik, utrata
  klasy). Zmiana stroju ich nie zeruje. Limitu czasu nie ma (`kontrakt.wymuszenie_maks_s = 0`).
- Martwa postać gra `upadek` mimo wymuszenia.
- Klipy i przesunięcie widzi tylko ten gracz (inni widzą jego bohatera w ruchu samoczynnym).
- Odpowiedź przychodzi od razu: obsługa nigdzie nie czeka i nie zgłasza błędu (błąd w środku = ostrzeżenie
  w konsoli i wynik `nil` / `false`).
- `OnInvoke` jest ustawiane na samym początku skryptu klienta; zanim wczytają się dane, `"stan"` zwraca `nil`,
  reszta `false`. Gdy kontenera nie ma (`workspace:FindFirstChild("BohaterSwiat") == nil`), wołający pomija umowę.
- Awatar jest chowany przez `Transparency` (nie przez `LocalTransparencyModifier`), więc mini-gra nie musi go
  chować ani odsłaniać, gdy bohater jest aktywny.
- Dodatek poza umową: `Invoke("przezroczystosc", 0…1 | nil)` chowa samego bohatera (awatar i tak jest niewidoczny).
  Schowanie awatara przez `LocalTransparencyModifier` chowa też bohatera.

```lua
local k = workspace:FindFirstChild("BohaterSwiat")
local ruch = k and k:FindFirstChild("Sygnaly") and k.Sygnaly:FindFirstChild("RuchBohatera")
local stan = ruch and ruch:Invoke("stan")
if stan then
	ruch:Invoke("klip", "skok")
	ruch:Invoke("przesun", Vector3.new(0, 2.5, 0))
	-- … koniec ruchu:
	ruch:Invoke("przesun", nil)
	ruch:Invoke("klip", nil)
else
	-- bohatera nie ma: ruch awatara jak dotąd
end
```

## Haczyki testowe

- `Sygnaly/SterowanieKlienta` (klient): `"stan"` → gotowość, zależności, liczba bohaterów i brył, czas klatki pętli,
  `lokalny` (klasa, tryb, klip, tempo, strój, bryły, instancje, spód rigu, wysokość stóp nad ziemią, odległość od
  punktu pod postacią, przezroczystość, wagi póz, części awatara schowane / widoczne, fizyka); `"pomiar", "zeruj"?`;
  `"ruch", polecenie, arg` (to samo co `RuchBohatera`); `"przezroczystosc", x`; `"manekin", model, klasa, napis?`
  (postać testowa dostaje bohatera jak cudzy gracz); `"manekin_usun"`; `"faza_biegu", 0…1 | nil` (zatrzymana faza
  cyklu biegu, do zrzutów); `"nagraj", sekundy` i `"nagranie"` (klatka po klatce: faza biegu, miejsce stóp i postaci).
- `Sygnaly/SterowanieSerwera` (serwer): `"stan"` → wyłącznik, zależności, klasy i stroje graczy; `"wlacz", bool`.
- Atrybuty kontenera: `SerwerGotowy`, `SkrotSerwera` (serwer), `KlientGotowy`, `SkrotKlienta` (u klienta).

## Pliki

| Plik | Co robi |
|---|---|
| `ustawienia.json` | liczby, pozy proceduralne (kąty), nazwy — jedyne miejsce do strojenia |
| `dane.py` | generator `zrodla/DaneBohatera.luau` (prędkość naturalna chodu, podniesienie, przysiady póz, liczby biegu z długości nóg) |
| `logika_bohatera.py` | lustro `LogikaBohatera.luau` (automat ruchu, cykl biegu, tempo, wagi póz, zasięg, umowa) |
| `sprawdz_luau_bohatera.py` | kontrola statyczna źródeł Luau |
| `zbuduj.py` | budowa kontenera w Studio (`--sucho`, `--skrypty`, `--usun`, `--studio`) |
| `zrodla/KlientBohatera.client.luau` | cały ruch i wygląd u klienta, umowa, haczyk testowy |
| `zrodla/SerwerBohatera.server.luau` | wyłącznik, haczyk testowy; poza Studio usuwa kontener |
| `zrodla/LogikaBohatera.luau` | czysta logika (wykonywana też bez Studio) |
| `testy/test_bohatera.py` | testy bez Studio |
| `testy/proba_play.py` | próba w Play, lista B00–B19 |

Pakiet nie zmienia żadnego pliku poza swoim folderem. Moduły postaci (`swiat/postacie`), dane walki
(`swiat/test_walki2/dane`), przymierzalnia i odtwarzacz klipów są tylko czytane.

## Polecenia

```
python -B swiat/bohater_swiat/dane.py                     # po zmianie ustawień: nowy zrodla/DaneBohatera.luau
python -B swiat/bohater_swiat/dane.py --sprawdz           # dane aktualne i zgodne z danymi walki i przymierzalni
python -B swiat/bohater_swiat/testy/test_bohatera.py      # bez Studio, ok. 30 s
python -B swiat/bohater_swiat/sprawdz_luau_bohatera.py
python -B swiat/bohater_swiat/zbuduj.py --sucho
python -B swiat/bohater_swiat/testy/proba_play.py --sprawdz
python -B swiat/bohater_swiat/zbuduj.py [--studio <id>]   # kontener (Edit)
python -B swiat/bohater_swiat/zbuduj.py --skrypty         # tylko moduły i skrypty
python -B tools/studio_okno.py --na-wierzch
python -B swiat/bohater_swiat/testy/proba_play.py <folder wyników POZA repo> [--tylko B05,B06] [--bez-zrzutow]
```

## Wyniki bez Studio (18.11.2026)

- `testy/test_bohatera.py`: 33 testy, OK. Dane (klasy = klasy gry, klipy z tabeli aktorów, stopy na ziemi
  w spoczynku i w chodzie, pozy sprawdzone kinematyką w przód, bryły i spód nóg w każdym dopuszczalnym stroju,
  liczby biegu z długości nóg), cykl biegu na rigu każdej klasy przy czterech prędkościach (stopa w podporze
  przesuwa się o mniej niż 0,005 st, w wymachu jest nad ziemią, kąty bez szarpnięć), logika (automat ruchu z biegiem,
  umowa), `LogikaBohatera.luau` wykonana interpreterem = lustro w Pythonie na 9 tys. losowych kroków i 4 tys.
  losowych wywołań, 12 celowo zepsutych wersji logiki wykrytych, miara dryfu stóp z próby w Play, kontrola kodu.
- `sprawdz_luau_bohatera.py` i `swiat/las_potwory/sprawdz_luau.py`: 4 pliki, OK.
- `zbuduj.py --sucho`: OK. `proba_play.py --sprawdz`: 42 kawałki Luau, 20 punktów listy, OK.

## Czego nie sprawdzono

- **Dwóch prawdziwych graczy naraz.** Próba B17 używa postaci testowych u jednego klienta; wykrywanie lotu u cudzej
  postaci (po prędkości pionowej) jest sprawdzone tylko w logice.
- **Prawdziwego telefonu** (czas klatki mierzony na komputerze, 60 kl./s).
- **Ruchu ocenianego okiem w grze.** Arkusze klatek i pomiary mówią, że stopa stoi w miejscu; czy bieg „dobrze
  wygląda” (kadencja, wymach rąk z bronią, kot w szacie zakrywającej nogi), musi ocenić człowiek w grze.
- **Biegu po łuku i po pochyłości** — pomiar stopy był w biegu po prostej, po płaskim.
- **Całej rundy Training Center w próbie tego pakietu** (B16 „?”) — przechodzi ją próba dymna gry.
- Awatara R6 (wzór na stopy go obejmuje, ale miejsce gra R15).
- Chodu wolniejszego niż bieg u gracza: przy zwykłej prędkości 16 st/s postać od razu biegnie; klip chodu gra tylko
  przy małej prędkości (np. dotyk z lekkim wychyleniem) i przez chwilę przy ruszaniu i hamowaniu.
