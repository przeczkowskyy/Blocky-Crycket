# Las Potworów — potwory w ruchu w Borze Pod Ukłonem (kontrakt etapu A)

*Status (15.11.2026, po recenzji): **kod obu połówek napisany i przejrzany, testy offline przechodzą, w Studio jeszcze
nie uruchomiony.** Następny krok to wdrożenie w Studio według rozdz. 9.2 (lista z gotowymi poleceniami); wynik recenzji,
lista poprawek i słabe miejsca są w rozdz. 13. Kontrakt nadal jest propozycją, a nie kanonem: kanonem może go uczynić
tylko Karol albo Paweł.
Pierwotny status: **propozycja** (15.11.2026), kontrakt do wykonania.
Wzór formy: `swiat/biom_las/PROJEKT.md` i `swiat/test_walki2/README.md`. Wiążą: D-016 (serwer liczy, klient nie
przysyła liczb), D-068 (długość walki tylko ze statystyk i losowości), D-069 (klasy bez kontrowania), D-071 (ekwipunek
widoczny na modelu; tarcza tylko wyekwipowana), D-034 (strefy z odradzającymi się potworami, E, walka), D-061 (strażnik
biomu). Źródło zasad ruchu: `swiat/biom_las/potwory.json` („zasady”) i `swiat/biom_las/PROJEKT.md` rozdz. 6.*

> **W skrócie.** Po 16 strefach Boru chodzą potwory (35 przy jednym graczu, 64 przy ośmiu, 86 przy dwudziestu) plus
> Strażnik Gaju w Kamiennym Kręgu. Serwer przesuwa tylko punkt bazowy każdego potwora po pętli węzłów 4 razy na sekundę
> i zapisuje go w atrybutach; klient buduje modele tylko dla najbliższych (najwyżej 12 w promieniu 120), wygładza ruch,
> gra klipy „spoczynek” i „ruch”, pokazuje tabliczkę poziomu i ikonę skrzyżowanych mieczy. Gracz podchodzi na 8 studów,
> naciska E (na telefonie stuka podpowiedź) i ogląda walkę w **przyjętym odtwarzaczu walki v2 na arenie prototypu**
> (cięcie do areny i z powrotem — działa bez zmian w plikach prototypu; jedna mała poprawka P1 usuwa usterkę wyglądu).
> Po wygranej potwór znika, a w jego miejsce z domu strefy wychodzi nowy. Całość to jeden kontener
> `Workspace/LasPotwory` z atrybutem `Wygenerowane = true`, który poza Studio sam się usuwa.

---

## 0. Zakres etapu A i co zostaje na etap B

**W etapie A (ten kontrakt):** 16 stref z `potwory.json` (z01–z16), watahy wilków jako grupy, Bursztynowy Slime (z12)
jako odmiana koloru, Strażnik Gaju jako cel strefy, skalowanie liczby potworów z liczbą graczy, odradzanie w wolnym
domu ze wzorem skracania, odstęp 25 na pętli, zajętość w walce, walka silnikiem v2 jak w `SerwerWalki2`, łup z silnika
pokazany w oknie wyniku odtwarzacza (bez zapisu).

**Poza etapem A (świadomie, z powodu czasu 2 × 45 min):** patrole p1–p4, Leśny Troll (budzenie co 8–12 min, trasa do
Oczka), zachowania z pola `zachowanie` (ciekawski slime, wataha okrążająca gracza, muchomornik pod chatką, siadanie
watahy w odległości ≥ 14), warunek odblokowania strażnika (10 wygranych), osobny strażnik dla każdego gracza, walka
„na miejscu” w lesie (rozdz. 6, wariant a). Generator danych zapisuje jednak listę pominiętych elementów (`pominiete`),
żeby etap B wiedział, od czego zacząć.

**Dlaczego tak:** zasady wspólne (dom, węzeł, pojemność, skracanie, skalowanie, E, zajętość, ruch 4 Hz, 12 najbliższych)
dają pełną pętlę „podejdź → E → walka → łup → odrodzenie”, o którą prosi właściciel. Zachowania i patrole to osobne
automaty, które dokłada się do tych samych grup bez zmiany kontraktu.

---

## 1. Kontener, instancje i układ współrzędnych

### 1.1 Co powstaje i gdzie

Wszystko, co buduje `zbuduj.py` (tryb Edit), leży w **jednym** kontenerze `Workspace/LasPotwory` (Folder):

| Ścieżka | Klasa | Kto tworzy | Po co |
|---|---|---|---|
| `LasPotwory` | Folder | `zbuduj.py` | atrybuty: `Wygenerowane = true`, `Zrodlo = "swiat/las_potwory"`, `Zbudowano` (czas ISO), `Skrot` (skrót danych z `DanePotworow.skrot`) |
| `LasPotwory/Moduly/Stale` | ModuleScript | `zbuduj.py` ← `zrodla/Stale.luau` | stałe wspólne serwera i klienta (rozdz. 8.4) |
| `LasPotwory/Moduly/DanePotworow` | ModuleScript | `zbuduj.py` ← `zrodla/DanePotworow.luau` (wygenerowany) | strefy, trasy, domy, gatunki w układzie świata (rozdz. 2) |
| `LasPotwory/Moduly/Logika` | ModuleScript | `zbuduj.py` ← `zrodla/Logika.luau` | czysta matematyka ruchu i odradzania (rozdz. 3.7); tylko serwer |
| `LasPotwory/Moduly/Wzorcowe` | ModuleScript | `zbuduj.py` ← **kopia** `swiat/test_walki2/zrodla/Wzorcowe.luau` | postać wzorcowa klasy na poziomie (serwer) |
| `LasPotwory/Moduly/Walka/{Dane, Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik}` | ModuleScript | `zbuduj.py` ← **kopie** `src/server/Walka/*.luau` ze strażnikiem Studio na początku | silnik walki v2 (serwer) |
| `LasPotwory/Stan` | Folder | `zbuduj.py` (pusty) | serwer wkłada tu po jednej `Configuration` na żywego potwora (rozdz. 3.8) |
| `LasPotwory/Zdalne/RozpocznijWalke2` | RemoteFunction | `zbuduj.py` | prośba o walkę; **nazwa i miejsce są wymuszone przez odtwarzacz** (rozdz. 5.1) |
| `LasPotwory/Sygnaly/SterowanieSerwera` | BindableFunction | `zbuduj.py` | haczyk testowy serwera (rozdz. 8.6) |
| `LasPotwory/Sygnaly/SterowanieKlienta` | BindableFunction | `zbuduj.py` | haczyk testowy klienta (rozdz. 8.6) |
| `LasPotwory/SerwerPotworow` | Script, `RunContext = Server` | `zbuduj.py` ← `zrodla/SerwerPotworow.server.luau` | serwer |
| `LasPotwory/KlientPotworow` | Script, `RunContext = Client` | `zbuduj.py` ← `zrodla/KlientPotworow.client.luau` | klient |

Powstaje dopiero w trybie Play (znika po zatrzymaniu Play):

| Ścieżka | Kto | Po co |
|---|---|---|
| `LasPotwory/Stan/<id>` (Configuration) | serwer | stan jednego potwora w atrybutach (rozdz. 3.8) |
| `ReplicatedStorage/LasPotworySzablony` (Folder, `Wygenerowane = true`) | serwer, przy starcie | kopie szablonów aktorów z `Workspace/TestWalki2/Aktorzy/{lesny_slime, cierniowy_wilk, muchomornik, straznik_lasu}` (rozdz. 4.3 — powód: streaming) |
| `LasPotwory/Widoki` (Folder, **lokalny**) | klient | lokalne modele potworów, kotwica podpowiedzi E |
| `PlayerGui/LasPotworyBohater`, `PlayerGui/LasPotworyBaner` (ScreenGui, `ResetOnSpawn = false`) | klient | panel bohatera, baner po wygranej ze strażnikiem |

**Dlaczego jeden kontener w Workspace, a nie ReplicatedStorage.** (1) Odtwarzacz walki wymaga, żeby kontener, który mu
podajemy, był w Workspace i miał dziecko `Zdalne/RozpocznijWalke2` (`Sesja:poprosSerwer`, `Sesja:pilnujPrzerwania`
przerywa sesję, gdy kontener nie jest potomkiem Workspace). (2) Prototyp walki działa tak samo (skrypty z `RunContext`
w kontenerze w Workspace) i to jest sprawdzone w tym miejscu. (3) `--usun` usuwa wtedy jeden obiekt. `Stan`, `Moduly`,
`Zdalne` i `Sygnaly` nie zawierają części, więc streaming ich nie dotyczy (instancje bez brył replikują się w całości).
Jedyny wyjątek to kopie szablonów w ReplicatedStorage (rozdz. 4.3) — powstają w Play i znikają razem z sesją.

**Zasady wspólnego miejsca.** Nic poza tym kontenerem, kopią szablonów w ReplicatedStorage i własnymi ScreenGui w
`PlayerGui`. Żadnych zmian w Lighting, StarterGui, StarterPlayer, ustawieniach Workspace ani w cudzych instancjach
(BiomLas i TestWalki2 tylko czytamy; jedyne „dotknięcie” TestWalki2 to `Clone()` jego szablonów). Każdy skrypt i moduł
zaczyna się od strażnika Studio jak w prototypie:

```lua
if not game:GetService("RunService"):IsStudio() then
	return {}          -- moduły; SerwerPotworow: script.Parent:Destroy() return; KlientPotworow: return
end
```

`SerwerPotworow` poza Studio **niszczy cały kontener** `script.Parent` zanim zrobi cokolwiek innego (wzór:
`SerwerWalki2.server.luau`, linie 23–28).

### 1.2 Układ współrzędnych: las → świat

Wszystkie pliki lasu (`potwory.json`, `znaczniki.json`, `uklad.json`) są w **układzie lasu**; `czesci.json` jest już w
świecie. Kontener `Workspace/BiomLas` ma środek w świecie (0; 0; −2000) i jest obrócony o 180° wokół pionu
(`znaczniki.json` → `kontener.wzor`, `swiat/biom_las/PROJEKT.md` rozdz. 2):

```
świat = (−x_las,  y_las,  −2000 − z_las)
kierunek (dx; dz) w lesie → (−dx; −dz) w świecie, czyli yaw_świat = yaw_las + π
```

**Przykład.** Pierwszy węzeł strefy z01 w lesie (206,3; 0; 294,5) → świat **(−206,3; 0; −2294,5)**. Miejsce Strażnika
(0; 32; −373) → świat **(0; 32; −1627)**. Wejście do lasu (200; 0; 400) → (−200; 0; −2400).

**Przeliczenie robi generator** (`generuj_dane.py`), więc moduł `DanePotworow` ma już współrzędne świata, a serwer i
klient niczego nie przeliczają. Funkcja `Logika.swiatZLasu` istnieje tylko dla testów i komunikatów.

**Konwencja kierunku (yaw).** Kierunek potwora to liczba `yaw` w radianach taka, że
`CFrame.Angles(0, yaw, 0).LookVector` = kierunek ruchu. Dla ruchu (dx; dz) w świecie: `yaw = math.atan2(−dx, −dz)`.
Przykład: ruch w +X świata → yaw = −π/2; ruch w +Z → yaw = π; ruch w −Z → yaw = 0. Model stawia się w
`CFrame.new(pozycja) * CFrame.Angles(0, yaw, 0)` (to jest `cfZiemi` z modułu Aktorzy: punkt na ziemi, LookVector = przód).

### 1.3 Jak serwer znajduje BiomLas i co robi, gdy go nie ma

Przy starcie serwer czeka na `workspace:WaitForChild("BiomLas", 15)` i sprawdza:

1. `BiomLas:GetAttribute("Wygenerowane") == true`;
2. istnieje `BiomLas/Teren/Grunt/Płyta` (BasePart), `Size` ≈ (1400; 2; 1400) (±0,5), `Position` ≈ (0; −1; −2000)
   (±0,5), a `math.abs(Orientation.Y)` ≈ 180 (±1). Te liczby generator bierze z `czesci.json` (pierwsza część,
   nazwa „Płyta”, grupa `Workspace/BiomLas/Teren/Grunt`) i zapisuje w `DanePotworow.biom.plyta`.

Gdy któryś warunek nie przejdzie: **głośno, ale nieszkodliwie** — jeden `warn("[LasPotwory] …")` z tym, co zmierzył
(np. „Płyta w (0, −1, −1500) zamiast (0, −1, −2000) — potwory nie wystartują”), atrybut kontenera
`StanBiomu = "brak_biomu"` albo `"zle_polozenie"`, **zero potworów**, zdalna funkcja odpowiada `zly_wybor`.
Klient pokazuje wtedy jeden dymek „Las Potworów: brak lasu w tym miejscu (szczegóły w Output)” i nic więcej.
Do testów bez lasu: atrybut kontenera `TestBezBiomu = true` (ustawiany w Edit, czyta go tylko serwer) pomija kontrolę;
potwory chodzą wtedy po pustym miejscu na tych samych współrzędnych.

---

## 2. Dane: generator i moduł `DanePotworow`

### 2.1 Generator

`python -B swiat/las_potwory/generuj_dane.py` zapisuje `swiat/las_potwory/zrodla/DanePotworow.luau`;
`--sprawdz` tylko porównuje plik na dysku z tym, co by zapisał (kod 1, gdy nieaktualny) — jak
`tools/walka/generuj_dane.py`. Generator jest deterministyczny: stała kolejność (jak w plikach źródłowych), liczby
zaokrąglone do 0,01 (współrzędne) i 0,001 (długości), zapis UTF-8 bez BOM, końce linii LF, **bez daty** w treści.
`skrot` = pierwsze 12 znaków SHA-1 kanonicznego JSON wejść (`json.dumps(..., sort_keys=True, ensure_ascii=False,
separators=(",", ":"))` z czterech wczytanych struktur), więc zależy od treści, a nie od końców linii.

Wejścia (tylko odczyt):

| Plik | Co bierzemy |
|---|---|
| `swiat/biom_las/potwory.json` | `zasady` (odstęp 25, smycz 10, blokada domu 18, prędkości), `rozmiary`, dla każdej strefy: `id`, `podbiom`, `potwor`, `wariant`, `poziomy`, `naraz`, `max`, `srodek`, `r`, `y`, `odrodzenie_s`, `grupa` |
| `swiat/biom_las/znaczniki.json` | `strefy[].wezly` i `strefy[].domy` **z wysokością** (wynik `generuj.py`), `strefy_spokoju`, `straznik`, `kontener` |
| `swiat/biom_las/uklad.json` | wielokąt Serca Boru (strefa spokoju „serce”), ścieżka `korytarz_labiryntu` (trasa z09) |
| `swiat/biom_las/czesci.json` | rekord części „Płyta” (kontrola położenia BiomLas) |
| `tools/walka/dane_walki.json` | lista `przeciwnicy[].id` (kontrola, że gatunek istnieje w silniku) |

Generator **przerywa z czytelnym komunikatem**, gdy: nazwa potwora nie ma odpowiednika w silniku; węzły z
`znaczniki.json` różnią się od `trasa` z `potwory.json` (dziś są identyczne); poziom poza 1–10; strefa nie mieści swoich
grup (`grupy × ((miejsc − 1) × odstepWGrupie + 25) > L`); dom jest bliżej niż 35 albo dalej niż 50 od najbliższego
węzła. Na końcu wypisuje tabelę stref (jak w dodatku A).

### 2.2 Nazwy potworów → identyfikatory silnika

| `potwory.json` | Silnik (`Dane.przeciwnicy[].id`) i klucz aktora | Prędkość (st/s) | Promień (do E) | `odstepWGrupie` |
|---|---|---|---|---|
| Leśny Slime | `lesny_slime` | 6 | 1,35 (szer 2,7 / 2) | 7,7 |
| Muchomornik | `muchomornik` | 5 | 1,475 (szer 2,95 / 2) | 7,95 |
| Cierniowy Wilk | `cierniowy_wilk` | 10 | 3,85 (dł 7,7 / 2) | 12,7 |
| Leśny Troll | `lesny_troll` | 7 | 6,35 | (etap B) |
| Strażnik Gaju | `straznik_lasu` (nazwa w silniku: „Strażnik Gaju”) | 0 (stoi) | 4,45 (szer 8,9 / 2) | — |

`promien = max(szer, dl) / 2` z `rozmiary`; `odstepWGrupie = max(szer, dl) + 5` (odstęp 4–6 między zwierzętami
w watasze z pola `zachowanie`, liczony od punktów bazowych, więc dodajemy długość ciała). Bursztynowy Slime (z12) to
`lesny_slime` z `wariant = { id = "bursztynowy", nazwa = "Bursztynowy Slime", kolor = "F2B030" }` (kolor `zloto`
z palety miasteczka, `swiat/krzywe_miasteczko/paleta.py`).

### 2.3 Grupy, miejsca i trasy (odczytanie zasad)

- **Strefy bez watahy** (slime’y, muchomorniki, samotniki z10): każdy potwór to osobna grupa z jednym miejscem;
  `grupy = max` (najwięcej naraz), `miejsc = 1`. Grupy powstają i znikają razem z potworem (rozdz. 3.3).
- **Strefy z watahami** (z07, z08, z09, z11, z13, z15): `grupy = watahy` (stałe, żyją cały czas, także puste),
  `miejsc = ceil(max / watahy)`; członek na miejscu `j` stoi `(j − 1) × odstepWGrupie` za czołem grupy. To zgadza się
  z `wezly.py → jednostki()` (wataha liczy się jako jeden w pojemności): z08 = 2 watahy po 5 miejsc.
- **Trasa** to zamknięta pętla węzłów w kolejności z pliku (`zasady.kolejnosc`). Wyjątek **z09** (labirynt): w
  `generuj.py` (linia ~90) z09 jest trasą otwartą, ale prosta z placu wejścia do polanki środka przecina ściany jeżyn.
  Dlatego trasa z09 = węzeł 1 → punkty ścieżki `korytarz_labiryntu` z `uklad.json` (7 punktów, środek (−200; −262) =
  węzeł 2) → węzeł 3, **tam i z powrotem**. Trasę „tam i z powrotem” o długości `Lp` zapisujemy jako pętlę parametru
  o okresie `L = 2 × Lp` (rozdz. 3.7, `punktTrasy`). Długość z09: Lp = 237,6, L = 475,1.
- **Dom → wejście.** Dla każdego domu generator liczy najbliższy węzeł `wezel` i **przedpole** `wejscie` = węzeł + 6 ×
  jednostkowy wektor (dom − węzeł): tu nowy potwór czeka na miejsce na pętli, 6 studów obok trasy, żeby nie stać na
  drodze idących. `s` = lista parametrów pętli, w których leży węzeł (pętla: `{dl[wezel]}`; tam i z powrotem:
  `{d, L − d}`). Przykład z02, dom 1: las (39,1; 320,6), najbliższy węzeł 2 (4,8; 329,4) w odległości 35,4,
  przedpole w lesie (10,61; 327,91) → świat (−10,61; 0; −2327,91).
- **Strażnik Gaju** to strefa `id = "straznik"` z jednym punktem, `L = 0`, jednym domem (tym samym punktem),
  `naraz = max = 1`, `poziomy = {10, 10}`, `odrodzenieS = 120` (**wartość testowa**, plan jej nie podaje — „dłuższe
  odrodzenie”), `yaw = 0` (twarzą na południe lasu, do wejścia serpentyną). **Miejsce:** plan podaje (0; −385), ale
  to oś filara z kryształem (`swiat/biom_las/lokacje/korona.py`, `kamienny_krag`: Filar 8 × 8 z kolizją w środku
  Kręgu). Strażnik stoi więc **12 studów na południe od osi, (0; 32; −373)** w lesie = **(0; 32; −1627)** w świecie: na
  posadzce Kręgu (r 13,5), 23 od menhirów, 12 od ogniska pinu (−8; −364), plecami ok. 9,5 od osi filara.

### 2.4 Format modułu (wiąże obu programistów)

```lua
-- Wygenerowane przez swiat/las_potwory/generuj_dane.py z potwory.json, znaczniki.json, uklad.json — nie edytuj ręcznie.
if not game:GetService("RunService"):IsStudio() then
	return {}
end
return {
	wersja = 1,
	skrot = "3f9a0c…",                       -- 12 znaków
	biom = { nazwa = "BiomLas", srodek = { 0, 0, -2000 }, obrotY = 180,
		plyta = { sciezka = "Teren/Grunt/Płyta", pozycja = { 0, -1, -2000 }, rozmiar = { 1400, 2, 1400 } } },
	zasady = { odstep = 25, smycz = 10, blokadaDomu = 18, zasiegE = 8, minOdrodzenia = 10, skracanie = 0.15 },
	gatunki = {
		lesny_slime = { nazwa = "Leśny Slime", predkosc = 6, promien = 1.35, wymiary = { 2.7, 2.7, 2.7 } },
		muchomornik = { … }, cierniowy_wilk = { … }, straznik_lasu = { nazwa = "Strażnik Gaju", predkosc = 0, … },
	},                                       -- wymiary = { szer, wys, dł } (model zastępczy, rozdz. 4.3)
	strefy = {                               -- kolejność jak w potwory.json; strażnik na końcu
		{ id = "z01", podbiom = "laka", gatunek = "lesny_slime", wariant = false,
			poziomy = { 1, 2 }, naraz = 6, max = 9,
			srodek = { -250, 0, -2300 }, r = 50, zasiegGraczy = 100,   -- r + 50 (rozdz. 3.5)
			grupy = 9, miejsc = 1, odstepWGrupie = 7.7, watahy = false, odrodzenieS = 15, straznik = false,
			trasa = { x = { … }, y = { … }, z = { … }, dl = { 0, 38.1, …, 267.2 }, L = 267.2, zamknieta = true },
			domy = { { x = …, y = 0, z = …, wejscie = { x, z }, wezel = 2, s = { 38.1 } }, … } },
		…,
		{ id = "straznik", podbiom = "korona", gatunek = "straznik_lasu", wariant = false, poziomy = { 10, 10 },
			naraz = 1, max = 1, srodek = { 0, 32, -1627 }, r = 30, zasiegGraczy = 0, grupy = 1, miejsc = 1,
			odstepWGrupie = 0, watahy = false, odrodzenieS = 120, straznik = true,
			trasa = { x = { 0 }, y = { 32 }, z = { -1627 }, dl = { 0 }, L = 0, zamknieta = true, yaw = 0 },
			domy = { { x = 0, y = 32, z = -1627, wejscie = { 0, -1627 }, wezel = 1, s = { 0 } } } },
	},
	spokoj = { { id = "brama_pniakow", x = …, z = …, r = 45 }, … },   -- świat; tylko do testów
	serce = { { x, z }, … },                                           -- wielokąt Serca w świecie; tylko do testów
	pominiete = { "p1", "p2", "p3", "p4", "troll" },
}
```

`trasa.dl` ma dla pętli `n + 1` wpisów (`dl[1] = 0`, `dl[n + 1] = L`, odcinek `n` wraca z ostatniego węzła do
pierwszego), a dla trasy tam i z powrotem `n` wpisów (`dl[n] = Lp`, `L = 2 × Lp`). `watahy = true` w strefach z07,
z08, z09, z11, z13, z15.

---

## 3. Serwer (autorytatywny)

### 3.1 Stany potwora

| Stan wewnętrzny | Gdzie jest punkt bazowy | Atrybut `Stan` | Przejście |
|---|---|---|---|
| `wychodzi` | idzie po prostej z domu do przedpola z prędkością gatunku (`Logika.krokDo`) | `"idzie"` | doszedł → `czeka` |
| `czeka` | stoi w przedpolu, twarzą do węzła | `"stoi"` | dostał miejsce na pętli → `chodzi` |
| `chodzi` | `punktTrasy(trasa, wGrupie(s_grupy, miejsce, odstepWGrupie, L))` | `"idzie"` albo `"stoi"` (czy przesunął się w tym tyknięciu o > 0,05) | walka → `zajety` |
| `zajety` | tam, gdzie zaczęła się walka; jego grupa stoi | `"zajety"` | koniec walki: wygrana gracza → usunięty; przegrana → poprzedni stan |

Walczyć można z każdym żywym potworem, który nie jest zajęty (także z idącym z domu i czekającym) — najprostsze
odczytanie „walkę zaczyna gracz”.

### 3.2 Ruch (4 Hz, bez PathfindingService)

Pętla serwera: `while kontener.Parent do local dt = math.min(task.wait(Stale.OKRES_RUCHU), 0.5) … end`. W każdym
tyknięciu, dla każdej strefy:

1. Grupy strefy: `s` (położenie czoła na parametrze pętli), `dlugosc = (miejsc − 1) × odstepWGrupie`, `stoi` = grupa ma
   zajętego członka **albo** jest rezerwacją (3.3). Nowe położenia: `Logika.krokGrup(s, dlugosc, stoi, L, v × dt, 25)`.
2. Członkowie grup: pozycja i yaw z `Logika.punktTrasy`.
3. Potwory `wychodzi`: `Logika.krokDo` w stronę przedpola (y = y strefy).
4. Potwory `czeka`: próba wejścia na pętlę (3.3).
5. Zapis atrybutów (3.8), tylko gdy coś się zmieniło.

**Odstęp 25** liczymy między czołem grupy a **ogonem** grupy przed nią (wataha liczy się jako jeden odcinek długości
`dlugosc`). `krokGrup` gwarantuje, że żadna luka nie spadnie poniżej 25 (dowód w testach lustra, rozdz. 9.1): grupa
przesuwa się o `min(v·dt, luka + krok_grupy_przed − 25)`, a kroki liczone są jednocześnie (punkt stały, rozdz. 3.7).
Grupa za zatrzymaną dochodzi do niej na 25 i staje; po walce cała kolejka rusza naraz.

**Smycz 10 i strefy spokoju.** W etapie A potwór jest zawsze na pętli albo na odcinku dom → przedpole, a te punkty
leżą w terytorium i poza strefami spokoju z danych (`wezly.py` odsunął węzły od stref spokoju o 10). Smycz nie ma więc
w etapie A czego pilnować w czasie gry — **sprawdzamy ją offline**: test lustra wymaga, by każdy punkt pętli był
najwyżej `r + 10` od środka strefy, a żaden punkt pętli ani odcinka dom → przedpole (próbki co 2 studa) nie leżał w
kole strefy spokoju ani w wielokącie Serca. W etapie B zachowania zbliżania (slime podskakuje 6 studów) dostaną
obcięcie do `r + 10` funkcją, którą wtedy dopiszemy do `Logika`.

### 3.3 Wejście na pętlę (nowy potwór)

- **Strefa bez watahy.** Czekający w przedpolu węzła o parametrze `s_w`:
  1. *Rezerwacja:* gdy liczba grup strefy (z rezerwacjami) < `grupy` i `Logika.tylDo(s_w, czoła_grup, L) ≥ 25`
     (najbliższe czoło za węzłem jest co najmniej 25 z tyłu), serwer tworzy w `s_w` grupę-rezerwację o długości 0,
     która **stoi** — grupa z tyłu zatrzyma się więc 25 przed węzłem.
  2. *Wejście:* gdy `Logika.przodDo(s_w, czoła_innych, długości_innych, L) ≥ 25` (ogon najbliższej grupy przed węzłem
     odszedł o 25), rezerwacja staje się zwykłą grupą tego potwora, a potwór przechodzi z przedpola na węzeł (skok o
     6 studów — klient go wygładzi).
  Dlaczego tak: wcześniejsze proste reguły („wejdź, gdy z przodu i z tyłu jest 25”) w symulacji przy pełnej strefie
  potrafiły czekać bez końca albo dawały nakładanie potworów (luka 0,1). Rezerwacja nie łamie odstępu nigdy (symulacja
  30 min, 10 stref, gęste walki: najmniejsza luka dokładnie 25,000; średnie czekanie 1–20 s przy jednym graczu).
- **Strefa z watahami.** Czekający wchodzi na **wolne miejsce** dowolnej watahy w chwili, gdy to miejsce przechodzi
  przez węzeł: `Logika.minal(s_miejsca_przed, s_miejsca_po, s_w, L)` dla któregoś `s_w` z listy `dom.s`. Wataha ma
  stałą długość, więc wejście nie zmienia odstępów.
- **Strażnik** (`L = 0`): wchodzi od razu (funkcje zwracają `math.huge` / `true` dla `L = 0`).

### 3.4 Start serwera

Po kontroli BiomLas i skopiowaniu szablonów (4.3) serwer liczy `cel` dla każdej strefy (3.5) i **od razu** stawia
potwory na pętli, bez wychodzenia z domów: strefa bez watahy — `cel` grup rozstawionych równo
(`Logika.poczatkowePolozenia(cel, L)`); strefa z watahami — `grupy` watah rozstawionych równo, członkowie rozdzieleni
`Logika.rozdzialStartowy(cel, grupy, miejsc)`. Poziom każdego potwora: losowa liczba całkowita z `poziomy[1]..poziomy[2]`
(`Random.new()` serwera). Identyfikator: `"<id strefy>-<licznik>"`, licznik osobny na strefę od 1 (`z01-1`, `z01-2`,
…, `straznik-1`); nowy potwór po odrodzeniu dostaje **nowy** identyfikator. Na koniec serwer drukuje
`[LasPotwory] gotowy: 35 potworów w 16 strefach + Strażnik Gaju; zgodność logiki 70/70` i ustawia `SerwerGotowy = true`.

### 3.5 Skalowanie i odradzanie (raz na sekundę)

**Liczba graczy `G`** = atrybut kontenera `TestGraczy` (liczba, tylko Studio) albo `#Players:GetPlayers()`, najmniej 1.
Liczby z `potwory.json` są „na serwer” (pole `opis`), więc liczymy graczy całego serwera, nie tylko lasu.

**Cel** (`Logika.cel(naraz, max, G)`): „naraz to liczba przy ok. 8 graczach; mniej graczy → mniej (najmniej połowa),
więcej → do max”. Odczytanie: przy 1 graczu `ceil(naraz / 2)`, przy 8 `naraz`, przy 20 `max` (20 = górna granica huba
z D-016 i druga liczba przepływu z `sprawdz.py`), liniowo pomiędzy, zaokrąglenie połówek w górę:

```
pol = ceil(naraz / 2)
G ≤ 8:  c = pol + (naraz − pol) × (G − 1) / 7
G > 8:  c = naraz + (max − naraz) × min(1, (G − 8) / 12)
cel = floor(c + 0,5)
```

Razem: 35 potworów przy G = 1, 64 przy G = 8, 86 przy G = 20 (zgodne z planem: 64 i 86) — plus Strażnik.

**Odradzanie.** Co sekundę, dla każdej strefy: `istnieje` = liczba potworów strefy w dowolnym stanie, `kolejka` = lista
czasów odrodzenia. Gdy `istnieje + #kolejka < cel`, serwer dopisuje do kolejki `teraz + czas` dla każdego brakującego:

```
gracze_w_strefie = liczba graczy, których HumanoidRootPart jest w poziomie ≤ zasiegGraczy (r + 50) od środka strefy
czas = max(10, odrodzenieS / (1 + 0,15 × (max(1, gracze_w_strefie) − 1)))     -- Logika.czasOdrodzenia
Strażnik: czas = odrodzenieS (120 s), bez skracania
```

`r + 50` obejmuje domy (leżą do ok. 60 od środka). `max(1, …)` — przy pustej strefie czas nie rośnie ponad bazę.
Gdy pierwszy wpis kolejki dojrzał: jeśli `istnieje ≥ cel` — wpis przepada (graczy ubyło); w przeciwnym razie
`Logika.wolnyDom(domy, gracze_xz, ostatniDom, 18)` wybiera **pierwszy wolny dom po ostatnio użytym** (karuzela; dom jest
wolny, gdy żaden gracz nie jest w poziomie bliżej niż 18). Brak wolnego domu → wpis czeka do następnej sekundy.
**Strażnik nie ma domu** (w `potwory.json` zasada domów dotyczy stref, a `straznik` domu nie ma), więc dla niego
blokada wynosi 0: wraca dokładnie po 120 s, także gdy zwycięzca stoi obok (odczytanie recenzji, rozdz. 13).
Nowy potwór powstaje w domu w stanie `wychodzi`. Nadmiaru potworów (gdy graczy ubyło) **nie usuwamy** — zniknie
naturalnie po walkach.

### 3.6 Zajętość w walce

Gdy serwer przyjmie walkę (5.1): `zajetyPrzez = gracz`, `wynik = walka.wynik`, `zajetyDo = teraz + walka.czas +
Stale.ZAPAS_ZAJETOSCI (1 s)`. To pełny czas dziennika przy tempie ×1 — ten sam, który prototyp bierze na blokadę sesji
gracza (`SerwerWalki2`, `walkaDo`). W każdym tyknięciu, gdy `teraz ≥ zajetyDo`: wygrana gracza → potwór usunięty
(Configuration niszczona, grupa bez watahy znika, miejsce w watasze się zwalnia, kolejka odrodzeń dostaje wpis wg 3.5);
przegrana → potwór wraca do poprzedniego stanu, grupa rusza. `Players.PlayerRemoving` kończy zajętość od razu
(wynik zostaje: wygrana → usunięty teraz; przegrana → wolny teraz).

### 3.7 Moduł `Logika` (czysta matematyka) i jego lustro w Pythonie

`zrodla/Logika.luau` nie dotyka instancji, zegara ani `Random`; `logika.py` to jego wierna kopia (nazwy w Pythonie
`snake_case`, ta sama kolejność argumentów). Zwraca się tylko liczby, napisy, wartości logiczne i tabele liczb.

| Luau | Python | Co robi |
|---|---|---|
| `cel(naraz, max, gracze) → n` | `cel` | wzór z 3.5 (`gracze < 1` jak 1) |
| `czasOdrodzenia(baza, graczeWStrefie) → s` | `czas_odrodzenia` | wzór z 3.5, najmniej 10 |
| `przod(a, b, L) → d` | `przod` | odległość „do przodu” po pętli `(b − a) mod L` w [0; L); `L ≤ 0` → `math.huge` |
| `punktTrasy(trasa, s) → (x, y, z, yaw)` | `punkt_trasy` | punkt i kierunek na trasie; `s` brane mod `L`; trasa otwarta: dla `s > Lp` punkt `L − s` i kierunek odwrócony; w wierzchołku obowiązuje odcinek, który się w nim **kończy**; `L = 0` → pierwszy punkt i `trasa.yaw` (albo 0) |
| `krokGrup(s, dlugosc, stoi, L, krok, odstep) → s2` | `krok_grup` | nowe położenia czół (opis niżej) |
| `przodDo(sCel, s, dlugosc, L) → d` | `przod_do` | min po grupach `przod(sCel, s_k) − dlugosc_k`; brak grup → `math.huge` |
| `tylDo(sCel, s, L) → d` | `tyl_do` | min po grupach `przod(s_k, sCel)`; brak grup → `math.huge` |
| `minal(sStary, sNowy, sCel, L) → bool` | `minal` | `L ≤ 0` → true; true, gdy ruch z `sStary` do `sNowy` przeszedł przez `sCel` (`przod(sStary, sCel) ≤ przod(sStary, sNowy) + 1e-9`) albo `sNowy` jest najwyżej 0,5 od `sCel` w którąkolwiek stronę (≤ 0,5 — wymaga tego przypadek `minal(10, 12.5, 13, 100)`) |
| `wGrupie(sGrupy, miejsce, odstepWGrupie, L) → s` | `w_grupie` | `(sGrupy − (miejsce − 1) × odstepWGrupie) mod L`; `L ≤ 0` → 0 |
| `rozdzialStartowy(cel, grup, miejsc) → {{grupa, miejsce}}` | `rozdzial_startowy` | `cel` obcięty do `grup × miejsc`; `miejsc = 1`: i-ty (od 0) → grupa `floor(i × grup / cel) + 1`; inaczej grupa `i mod grup + 1`, miejsce `floor(i / grup) + 1` |
| `poczatkowePolozenia(n, L) → {s}` | `poczatkowe_polozenia` | `(i − 1) × L / n` |
| `wolnyDom(domy, gracze, ostatni, blokada) → i?` | `wolny_dom` | domy i gracze jako `{x, z}`; sprawdza domy od `ostatni + 1` w kółko; wolny, gdy każdy gracz ma odległość ≥ `blokada`; brak → nil / None |
| `krokDo(x, z, cx, cz, krok) → (x2, z2, doszedl)` | `krok_do` | krok po prostej, bez przeskoczenia celu |
| `swiatZLasu(x, y, z) → (x, y, z)` | `swiat_z_lasu` | `(−x, y, −2000 − z)` |
| `yaw(dx, dz) → r` | `yaw` | `math.atan2(0 − dx, 0 − dz)` (zapis `−dx` daje przy `dx = 0` ujemne zero i −π zamiast π; przypadek `punktTrasy(T1, 15)` oczekuje +3,1416) |
| `sprawdzPrzypadki() → (ok, n, bledy)` | (testy) | liczy wszystkie przypadki z tabeli 3.7a; serwer woła ją przy starcie |

**`krokGrup` dokładnie.** `kr_i = 0` dla stojących, `krok` dla pozostałych. Potem najwyżej `2n + 2` razy, dopóki coś
się zmienia: dla każdej nie-stojącej grupy `lim = L − dlugosc_i − odstep`, a dla każdej innej grupy `k`
`lim = min(lim, przod(s_i, s_k, L) − dlugosc_k + kr_k − odstep)`; `nowy = clamp(lim, 0, krok)`; gdy `nowy < kr_i`,
`kr_i = nowy`. Jeśli po limicie powtórzeń coś się jeszcze zmieniało (możliwe tylko przy złych danych wejściowych),
wszystkie `kr` = 0 i `warn` raz na strefę. Wynik: `(s_i + kr_i) mod L`; `L ≤ 0` albo brak grup → kopia wejścia.
Złożoność O(n²) na powtórzenie przy n ≤ 9 grup — pomijalna.

#### 3.7a Przypadki wzorcowe (to samo w `testy/test_logiki.py` i w `Logika.sprawdzPrzypadki`; tolerancja 1e-4)

Policzone przy pisaniu kontraktu kopią lustra; `inf` = `math.huge`.

| Wywołanie | Wynik |
|---|---|
| `cel(6,9,0)`, `cel(6,9,1)`, `cel(6,9,4)`, `cel(6,9,8)`, `cel(6,9,14)`, `cel(6,9,20)`, `cel(6,9,50)` | 3, 3, 4, 6, 8, 9, 9 |
| `cel(2,3,1)`, `cel(2,3,20)`, `cel(5,7,4)`, `cel(1,1,20)`, `cel(3,4,12)` | 1, 3, 4, 1, 3 |
| `czasOdrodzenia(15,0)`, `(15,1)`, `(15,4)`, `(25,4)`, `(15,8)`, `(25,8)`, `(20,3)` | 15, 15, 10,3448, 17,2414, 10, 12,1951, 15,3846 |
| `przod(10,5,100)`, `przod(90,10,100)`, `przod(3,3,100)`, `przod(1,2,0)` | 95, 20, 0, inf |
| trasa T1 = `{x={0,10,10}, y={0,0,0}, z={0,0,10}, dl={0,10,20,34.1421356}, L=34.1421356, zamknieta=true}`: `punktTrasy(T1, s)` dla s = 0, 5, 10, 15, 27,0710678, 34,1421356, −5 | (0,0,0,−1,5708), (5,0,0,−1,5708), (10,0,0,−1,5708), (10,0,5,3,1416), (5,0,5,0,7854), (0,0,0,−1,5708), (3,5355,0,3,5355,0,7854) |
| trasa T2 = `{x={0,10,10}, y={0,0,0}, z={0,0,10}, dl={0,10,20}, L=40, zamknieta=false}`: s = 0, 15, 20, 25, 35, 40 | (0,0,0,−1,5708), (10,0,5,3,1416), (10,0,10,3,1416), (10,0,5,0), (5,0,0,1,5708), (0,0,0,−1,5708) |
| `krokGrup({0,30},{0,0},{false,false},100,2.5,25)` | {2,5, 32,5} |
| `krokGrup({0,26},{0,0},{false,false},100,2.5,25)` | {2,5, 28,5} |
| `krokGrup({0,30},{0,0},{false,true},100,2.5,25)` | {2,5, 30} |
| `krokGrup({0,25.3,50.6,75.9},{0,0,0,0},{false,false,false,false},101.2,1.5,25)` | {1,5, 26,8, 52,1, 77,4} |
| to samo z `stoi = {false,false,false,true}` | {0,9, 25,9, 50,9, 75,9} |
| `krokGrup({0},{38.1},{false},63,2.5,25)` | {0} |
| `krokGrup({5,10},{0,0},{false,true},0,1,25)` | {5, 10} |
| `przodDo(10,{30,5},{0,0},100)`, `przodDo(10,{20},{15},100)`, `przodDo(10,{},{},100)` | 20, −5, inf |
| `tylDo(10,{30,5},100)`, `tylDo(10,{},100)` | 5, inf |
| `minal(98,1,0,100)`, `minal(10,12.5,12,100)`, `minal(10,12.5,13,100)`, `minal(10,10,10.3,100)`, `minal(10,10,11,100)`, `minal(5,5,7,0)` | true, true, true, true, false, true |
| `wGrupie(5,1,12.7,100)`, `wGrupie(5,3,12.7,100)`, `wGrupie(5,2,12.7,0)` | 5, 79,6, 0 |
| `rozdzialStartowy(3,9,1)`, `(3,2,5)`, `(2,1,4)`, `#rozdzialStartowy(12,2,5)` | {{1,1},{4,1},{7,1}}, {{1,1},{2,1},{1,2}}, {{1,1},{1,2}}, 10 |
| `poczatkowePolozenia(7,177.3)` | {0, 25,3286, 50,6571, 75,9857, 101,3143, 126,6429, 151,9714} |
| `wolnyDom({{0,0},{100,0},{0,100}},{{5,5}},0,18)`, to samo z `ostatni = 2`, `wolnyDom({{0,0},{100,0}},{{5,5},{95,0}},1,18)`, `wolnyDom({{0,0}},{{18,0}},1,18)` | 2, 3, nil, 1 |
| `krokDo(0,0,3,4,2)`, `krokDo(0,0,3,4,6)` | (1,2, 1,6, false), (3, 4, true) |
| `swiatZLasu(206.3,0,294.5)`, `swiatZLasu(0,32,-373)` | (−206,3, 0, −2294,5), (0, 32, −1627) |

Razem 70 wywołań (wiersz z kilkoma wywołaniami liczy się jako tyle przypadków, ile ma wywołań), więc
`sprawdzPrzypadki()` zwraca `n = 70`, a atrybut `ZgodnoscLogiki` przy zgodności to „OK 70/70”.

### 3.8 Co i jak replikujemy (lekko)

Jedna `Configuration` na potwora: `LasPotwory/Stan/<id>`. Atrybuty (pisze **tylko** serwer):

| Atrybut | Typ | Kiedy się zmienia | Znaczenie |
|---|---|---|---|
| `Gatunek` | string | raz | id silnika i klucz aktora (`lesny_slime`, `muchomornik`, `cierniowy_wilk`, `straznik_lasu`) |
| `Nazwa` | string | raz | „Leśny Slime”, „Bursztynowy Slime”, „Strażnik Gaju”… |
| `Wariant` | string | raz | `""` albo `"bursztynowy"` |
| `Strefa` | string | raz | `"z01"` … `"z16"`, `"straznik"` |
| `Poziom` | number | raz | 1–10 |
| `Straznik` | boolean | raz | true tylko dla Strażnika |
| `Pozycja` | Vector3 | ≤ 4 Hz, gdy przesunięcie > 0,05 | punkt bazowy na ziemi trasy (y = y strefy: 0 / 12 / 22 / 32; klient sam dopasuje do gruntu) |
| `Kierunek` | number | ≤ 4 Hz, gdy zmiana > 2° | yaw wg 1.2 |
| `Stan` | string | przy zmianie | `"idzie"`, `"stoi"`, `"zajety"` |

Atrybuty ustawia się **przed** `Parent = Stan`, żeby klient w `ChildAdded` miał komplet. Usunięcie potwora =
`Destroy()` jego Configuration. Ruch to ok. 25 idących potworów × 4 Hz przy jednym graczu ≈ 100–200 zmian atrybutów
na sekundę, kilka KB/s na klienta. Bez RemoteEventów stanu i bez pozycji członków grupy liczonych przez klienta.

Atrybuty kontenera (serwer → wszyscy): `SerwerGotowy` (bool), `StanBiomu` (`"ok"`, `"brak_biomu"`, `"zle_polozenie"`),
`SzablonyGotowe` (bool), `Graczy` (użyte `G`), `Potworow` (liczba żywych), `ZgodnoscLogiki` („OK 70/70” albo opis
błędu), `SerwerLicznikWalk`, `SerwerOstatniaWalka` (np. `"z01-2/wojownik/auto→1/wygrana"`), `SerwerOstatnieZiarno`,
`StraznikWraca` (czas serwera powrotu Strażnika albo 0).

---

## 4. Klient (tylko wygląd)

### 4.1 Wybór potworów do pokazania (co 0,5 s)

Odległość liczymy od kamery (`workspace.CurrentCamera.CFrame.Position`) do `Pozycja`. Sortujemy wszystkie dzieci
`Stan`. **Budujemy** widok, gdy potwór jest w pierwszej dwunastce najbliższych i ≤ 120 studów
(`Stale.MAKS_WIDOKOW`, `Stale.PROMIEN_WIDOKU`). **Niszczymy**, gdy wypadł poza 14 najbliższych albo jest dalej niż 135
(`MAKS_WIDOKOW_TWARDO`, `PROMIEN_USUNIECIA`) — zapas chroni przed migotaniem na granicy. Dodatkowo suma części
(`TabelaAktorow.aktorzy[klucz].liczbaCzesci`) wszystkich widoków ≤ `Stale.BUDZET_CZESCI` (4000): gdy kolejny by ją
przekroczył, nie budujemy go. Klipy liczymy tylko dla 12 najbliższych istniejących widoków; dalsze (13. i 14.) stoją w
ostatniej pozie. **Budujemy najwyżej jeden widok na 0,1 s** (`BUDOWA_CO`): klon wilka to ok. 1138 instancji, Strażnika
ok. 2346 (pomiar prototypu: klonowanie Strażnika ok. 70 ms). `Stan.ChildRemoved` niszczy widok od razu.

### 4.2 Wygładzanie, grunt, klipy

- **Ruch:** gdy `Pozycja` się zmieni (sprawdzane co klatkę dla widoków przez `GetAttribute`), widok dostaje nowy cel i
  prędkość `(cel − widok) / OKRES_RUCHU` — dochodzi do celu dokładnie wtedy, gdy przyjdzie następny. Skok > 20 studów
  (`SKOK_WYGLADZANIA`) → przestawienie bez wygładzania.
- **Grunt:** przy każdym nowym celu jeden promień w dół (`workspace:Raycast(cel + (0, 6, 0), (0, −14, 0))`, filtr
  `Include { workspace.BiomLas }`); gdy trafienie jest w ±3 od y celu — stawiamy na nim, inaczej na y z serwera.
  Najwyżej ok. 56 promieni na sekundę.
- **Obrót:** yaw widoku goni `Kierunek` z prędkością 8 rad/s najkrótszą drogą.
- **Klipy:** `Stan = "idzie"` → klip akcji `ruch` (pętla, przejście 0,2 s); inaczej `spoczynek` (pętla). Nazwy klipów z
  `TabelaAktorow.aktorzy[klucz].klipy` (np. `spoczynek → "idle"`, `ruch → "ruch"`); brak klipu → bez animacji.

### 4.3 Skąd modele (ponowne użycie prototypu bez edycji)

**Problem streamingu.** `Aktorzy.nowy` (prototyp) klonuje szablon z `Workspace/TestWalki2/Aktorzy/<klucz>` (funkcja
`szablon()` w `Aktorzy.luau`). Szablony stoją w galerii przy arenie (ok. (−62…; 0; 214)), ponad 2000 studów od lasu.
Przy włączonym streamingu (plan lasu zakłada promień 256) części szablonów nie ma u klienta, który stoi w lesie — klon
byłby pusty. W walce problem nie występuje, bo serwer przed odpowiedzią woła `RequestStreamAroundAsync` przy arenie.

**Rozwiązanie bez zmian w prototypie:**

1. **Serwer przy starcie** czeka na `workspace.TestWalki2.Aktorzy` (10 s) i klonuje cztery szablony
   (`lesny_slime`, `cierniowy_wilk`, `muchomornik`, `straznik_lasu`) do `ReplicatedStorage/LasPotworySzablony`
   (Folder, `Wygenerowane = true`). ReplicatedStorage nie podlega streamingowi. Serwer widzi wszystkie instancje, więc
   klon jest pełny. Potem `SzablonyGotowe = true`. Brak TestWalki2 → `SzablonyGotowe = false` i jeden `warn`.
2. **Klient** bierze z `Workspace/TestWalki2/Moduly` (ModuleScripty — nie są bryłami, więc są u klienta zawsze):
   `Klipy`, `TabelaAktorow`, `DaneAktorow/<klucz>`, i buduje widok **tymi samymi krokami co `Aktorzy.nowy`**:
   ```lua
   local wpis = Tabela.aktorzy[klucz]
   local model = szablonyRS[klucz]:Clone()
   model.Name = id
   model:SetAttribute("Lokalny", true)
   local hrp = model:FindFirstChild("HumanoidRootPart") :: BasePart
   hrp.Anchored = true
   model:PivotTo(cfZiemi)                      -- cfZiemi = CFrame.new(pozycja) * CFrame.Angles(0, yaw, 0)
   local przes = CFrame.new(wpis.hrp[1], wpis.hrp[2], wpis.hrp[3])
   model.Parent = widoki                        -- LasPotwory/Widoki (lokalny)
   local klipy = Klipy.nowy(model, require(daneAktorow[klucz]), { reczny = true })
   klipy:graj(wpis.klipy.spoczynek, { petla = true, przejscie = 0 })
   -- co klatkę (12 najbliższych): klipy:krok(dt); klipy:zastosuj()
   -- przestawienie: hrp.CFrame = cfZiemi * przes
   -- usunięcie: klipy:zniszcz(); model:Destroy()
   ```
   Obrysu nie robimy (w prototypie `Ustawienia.OBRYS = "brak"`).
3. **Bursztynowy Slime:** po klonie każda `BasePart` z atrybutem `Skora` (galareta; ustawia go `budowa/szablon.luau`)
   dostaje `Color = Stale.KOLOR_BURSZTYNOWY`. W walce slime będzie zielony (odtwarzacz nie zna odmian) — pytanie 7.
4. **Tryb zastępczy:** gdy brak `TestWalki2/Moduly` albo `SzablonyGotowe ~= true` po czekaniu na serwer (po
   recenzji do 40 s zamiast 15 s: serwer potrzebuje do 15 s na BiomLas i do 2 × 10 s na TestWalki2/Aktorzy, a przy
   15 s klient nie zdążył zobaczyć złego `StanBiomu`; w zwykłym przypadku czekanie trwa ok. 1 s), klient pokazuje każdy
   potwór jako jedną bryłę `Part` o wymiarach `DanePotworow.gatunki[g].wymiary` (kolor: slime `zielony`, bursztynowy
   `KOLOR_BURSZTYNOWY`, muchomornik `czerwony`, wilk `fiolet`, strażnik `szary` ze `Stale.KOLORY`), bez klipów, i
   ustawia `KlientTryb = "zastepczy"`. Tak sprawdzi się ruch serwera nawet bez prototypu (to jest „pętla na zastępczych
   bryłach” z kroku 5 planu lasu).

Wszystkie części widoków: `CanCollide = false`, `CanQuery = false`, `CanTouch = false` (klon szablonu już je ma;
bryła zastępcza ustawia sama), `CastShadow` bez zmian.

### 4.4 Tabliczka poziomu i ikona zajętości

Na widok jeden `BillboardGui` „Tabliczka” (`Adornee` = Attachment „Glowa” w `HumanoidRootPart`, pozycja
`(−hrp[1], wpis.pasek − hrp[2], −hrp[3])`, czyli punkt „Pasek” z `Aktor:punkt`), `MaxDistance = 80`,
`AlwaysOnTop = false`, `LightInfluence = 0`, rozmiar 76 × 30 px. W środku `TextLabel` „poz. N” (czcionka Bangers,
biały tekst z obrysem `tusz`, tło `krem`). **Czerwona** (tło `czerwony`): gdy `Poziom ≥ poziomGracza + 3`, gdzie
`poziomGracza` to wybrany w panelu poziom bohatera (1, 5 albo 10); przy „auto” tabliczka nie czerwienieje (bohater
zawsze ma poziom potwora — rozdz. 5.2). Obok tekstu ramka 28 × 28 „Miecze”: dwa paski `Frame` 4 × 24 px obrócone o
+45° i −45° z poprzeczkami 10 × 3 px (bez obrazków — zakaz uploadu), widoczna tylko przy `Stan = "zajety"`.

### 4.5 Podpowiedź E (i przycisk na telefonie)

Jedna lokalna kotwica `Part` „KotwicaE” w `Widoki` (niewidzialna, `Anchored`, bez kolizji i zapytań) z
`ProximityPrompt` „PodpowiedzLasu”: `KeyboardKeyCode = E`, `GamepadKeyCode = ButtonX`, `HoldDuration = 0`,
`RequiresLineOfSight = false`, `ClickablePrompt = true` (na telefonie podpowiedź jest przyciskiem do stuknięcia),
`MaxActivationDistance = 40` (bramkę robimy sami). Co 0,1 s klient wybiera **najbliższego dozwolonego** potwora:
istnieje, `Stan ~= "zajety"`, nie jest ukryty lokalnie (4.6), odległość w poziomie od `HumanoidRootPart` do `Pozycja` ≤
`8 + promien`, różnica wysokości ≤ 6 (żeby nie walczyć z wilkami na półce 12 nad głową). Kotwica staje w punkcie głowy
jego widoku (albo `Pozycja + (0, wymiary[2] / 2, 0)`), `ObjectText = "Leśny Slime · poz. 2"`, `ActionText = "Walcz"`
albo `"Walcz (za N s)"`, gdy `Odtwarzacz.wolnaZa() > 0`, albo `"Walka niedostępna"`, gdy nie ma odtwarzacza.
Brak kandydata albo trwa walka (`Odtwarzacz.czyTrwa()`) → `Enabled = false`.

### 4.6 Panel bohatera, start walki, po walce

- **Panel bohatera** (`LasPotworyBohater`, `DisplayOrder = 5`): stały mały przycisk w lewym górnym rogu (pod paskiem
  Roblox, `IgnoreGuiInset = false`, pozycja 12 × 12 px) z napisem „Bohater: Wojownik · poz. auto”. Stuknięcie otwiera
  okienko: klasa [Wojownik] [Zwiadowca] [Mag], poziom [auto] [1] [5] [10], [GOTOWE]. Domyślnie `wojownik` i `auto` —
  pierwsze E od razu zaczyna walkę. Wybór żyje w pamięci klienta (i lokalnie w atrybutach `KlientKlasa`,
  `KlientPoziom` kontenera — dla testów). Kolory i czcionka jak w `WyborWalki2` (Bangers, `krem`, `tusz`, wybrany
  przycisk `zolty`). Odtwarzacz sam chowa wszystkie ScreenGui na czas walki (`Sesja:ukryjInneGui`).
- **Start:** `PromptTriggered` (tylko nasza podpowiedź, `kto == LocalPlayer`) → gdy `Odtwarzacz.czyTrwa()` albo
  `wolnaZa() > 0` — nic; inaczej klient zapamiętuje `mojaWalka = { id, gatunek, straznik }`, czyści lokalnie atrybut
  kontenera `OstatniWynik` (`kontener:SetAttribute("OstatniWynik", nil)`) i woła
  `task.spawn(Odtwarzacz.uruchom, kontener, { klasa = klasa, przeciwnik = id, poziom = poziom }, nil)`, gdzie
  `kontener = Workspace.LasPotwory`, a `Odtwarzacz = require(workspace.TestWalki2.Moduly.OdtwarzaczWalki2)` (ten sam
  egzemplarz modułu co w `KlientWalki2`, więc dwie walki naraz nie ruszą).
- **Po walce:** klient co 0,25 s sprawdza `Odtwarzacz.czyTrwa()`; gdy sesja się skończy, czyta lokalny atrybut
  kontenera `OstatniWynik` (ustawia go odtwarzacz w `Sesja:pokazWynik`). `"wygrana"` → widok tego potwora znika od razu
  i id trafia na listę ukrytych lokalnie (dopóki serwer go nie usunie); gdy to był Strażnik — baner
  `LasPotworyBaner` „STRAŻNIK GAJU POKONANY!” i pod spodem „Wróci za 2 min” na 5 s. Inny wynik albo brak — nic.
- **Odmowa serwera** pokazuje dymek `KlientWalki2` (prototyp ustawia `Odtwarzacz.naOdmowe`); własnego dymka nie
  robimy. Klient sam nie dopuszcza do większości odmów (bramka podpowiedzi).

---

## 5. Walka

### 5.1 Ścieżka prośby (D-016)

Klient nie wysyła nic sam — **prośbę wysyła odtwarzacz prototypu** (`Sesja:poprosSerwer`) do
`LasPotwory/Zdalne/RozpocznijWalke2`, bo tak dostał kontener. Ładunek jest dokładnie taki:

```
klient → serwer: { klasa = "wojownik" | "zwiadowca" | "mag", przeciwnik = "<id potwora, np. z01-7>", poziom = "auto" | "1" | "5" | "10" }
serwer → klient: { ok = true, walka = <dziennik v2 z Silnik.symuluj>, nastepnaOd = <czas serwera> }
              | { ok = false, powod = "za_szybko" | "zly_wybor" | "brak_postaci" | "za_daleko" | "walka_trwa" | "blad_silnika", ponowZa = <s>? }
```

Jedyne liczby w odpowiedzi to te, które prototyp już przyjmuje. Serwer (`OnServerInvoke`), kolejno jak `SerwerWalki2`:

1. Nie częściej niż raz na 1 s (`ODSTEP_PROSB`), także odrzucona → `za_szybko` z `ponowZa`.
2. Tylko trzy pola przez `rawget`, wszystkie napisy: `klasa` z listy `Wzorcowe.KLASY`, `poziom` z listy
   `{"auto","1","5","10"}`, `przeciwnik` ≤ 32 znaki, wzór `^[%w_]+%-%d+$`, istnieje w rejestrze żywych → inaczej
   `zly_wybor`.
3. Postać żyje (`Humanoid.Health > 0`, jest `HumanoidRootPart`) → inaczej `brak_postaci`.
4. Sesja gracza: `teraz < walkaDo[gracz]` (i brak `TestBezSesji`) → `walka_trwa` z `ponowZa`.
5. Potwór zajęty przez **innego** gracza albo zajęty przez tego samego po jego **wygranej** → `zly_wybor`
   (odtwarzacz zna tylko powody z listy `POWODY_CICHE`; inny powód skończyłby się `warn` i stanem „blad”).
   Zajęty przez tego samego po **przegranej** → dozwolone (rewanż przyciskiem JESZCZE RAZ).
6. Odległość w poziomie `HumanoidRootPart` → `Pozycja` ≤ `8 + promien + 6` (zapas 6 na opóźnienie i ruch 4 Hz) i
   różnica wysokości ≤ 6 → inaczej `za_daleko` (dymek prototypu mówi wtedy o „tablicy” — znana usterka tekstu).
7. Bohater: `Wzorcowe.postac(klasa, poziomBohatera)`, gdzie `poziomBohatera` = poziom potwora przy `"auto"`, inaczej
   liczba z listy. Przeciwnik: `{ potwor = Gatunek, poziom = Poziom }`. Ziarno: atrybut kontenera `ZiarnoTestowe`
   (liczba ≥ 1, jak w prototypie) albo `Random.new():NextInteger(1, 2147483646)`.
8. `pcall(Silnik.symuluj, bohater, przeciwnik, ziarno)`; błąd → `warn` i `blad_silnika`.
9. `walkaDo[gracz] = teraz + walka.czas − 0,4` (jak prototyp; `TestBezSesji = true` → `teraz`); potwór zajęty (3.6).
10. `pcall(gracz.RequestStreamAroundAsync, gracz, Stale.ARENA_PROTOTYPU, 3)` — arena musi być wczytana, zanim
    odtwarzacz ruszy (gracz stoi 2000+ studów dalej).
11. Atrybuty `SerwerLicznikWalk`, `SerwerOstatniaWalka`, `SerwerOstatnieZiarno`; zwrot `{ ok = true, walka, nastepnaOd = walkaDo[gracz] }`.

Długość walki to wyłącznie wynik silnika (D-068): ani serwer, ani klient niczego nie skracają; ×2, ×4 i POMIŃ to wybór
gracza w odtwarzaczu. Klasy bez kontrowania (D-069) — nic w tym pakiecie nie zależy od pary klasa–potwór.

### 5.2 Kim gracz walczy — reguła testowa T1 (do decyzji ludzi)

**T1 (tylko na czas testów):** gracz wybiera raz w panelu klasę (Wojownik, Zwiadowca, Mag) i poziom bohatera
(„auto”, 1, 5, 10). Serwer buduje **postać wzorcową** `Wzorcowe.postac(klasa, poziom)` (dokładny port
`tools/walka/wzorcowe.py`, ta sama pula punktów dla każdej klasy). „auto” = poziom bohatera równy poziomowi potwora —
uczciwy pojedynek w każdej strefie, testerzy mogą obejść cały las i dojść do Strażnika. 1 / 5 / 10 pozwalają
sprawdzić czerwone tabliczki i przegrane. Wojownik wzorcowy ma wyekwipowaną tarczę (`p.tarcza`), więc tarcza na
modelu w walce zgadza się z D-071. **To nie jest docelowa reguła:** w grze bohater to postać gracza z jego poziomem,
statystykami i ekwipunkiem — do ustalenia przy zapisie postaci (pytanie 1).

### 5.3 Łup, wygrana, przegrana, pominięcie, rozłączenie

| Sytuacja | Serwer | Klient |
|---|---|---|
| Łup | liczy go silnik w tym samym wywołaniu (`walka.lup`); **niczego nie zapisujemy** (w grze tu byłby zapis) | okno wyniku odtwarzacza pokazuje łup z dziennika |
| Wygrana | potwór zajęty do `zajetyDo`, potem usunięty i wpis do kolejki odrodzeń | po zamknięciu okna wyniku widok znika od razu; inni widzą miecze do `zajetyDo` |
| Przegrana | potwór zajęty do `zajetyDo`, potem wraca na trasę; rewanż JESZCZE RAZ dozwolony | postać gracza stoi tam, gdzie stała (bez teleportu na polanę — HP nie jest zapisywane, więc „śmierci” nie ma) |
| POMIŃ, ×2, ×4 | nic (czas zajętości i blokady sesji to pełny czas ×1) | odtwarzacz kończy wcześniej; podpowiedź pokazuje „Walcz (za N s)” |
| JESZCZE RAZ po wygranej | `zly_wybor` (potwór już pokonany) | dymek prototypu „Serwer nie przyjął tego wyboru…” — znana usterka, poprawka P2 |
| Rozłączenie w trakcie | `PlayerRemoving`: wygrana → usunięty teraz; przegrana → wolny teraz; `walkaDo` czyszczone | — |
| Reset postaci w trakcie | nic (zajętość do `zajetyDo`) | odtwarzacz przerywa sesję sam (`pilnujPrzerwania`) |

---

## 6. Gdzie pokazać walkę

**Co w odtwarzaczu zakłada stałą arenę** (przeczytane w `OdtwarzaczWalki2.luau` i `Ustawienia.luau`):

1. `Sesja:ustawAktorow`: `self.cfSceny = U.scena()` — scena zawsze w (0; 1; 250) (`U.SRODEK` + podest 1,0). Wszystko
   inne (miejsca aktorów `cfDomu`, ujęcia kamery, objazd, kąt twarzy) liczy się względem `self.cfSceny` (14 użyć) —
   samo przesunięcie sceny jest więc jedną zmianą.
2. `Sesja:schowajObcych`: chowa lokalnie wszystko w pudle `U.OBSZAR_SRODEK` / `U.OBSZAR_ROZMIAR` (140 × 400 × 124 wokół
   areny) poza `self.scena`, płytą `Baseplate`, `Terrain` i dziećmi **podanego kontenera** o nazwach `Arena`,
   `Aktorzy`, `Galeria`.
3. `Sesja:przygotujScene`: chowa szablony z `self.kontener:FindFirstChild("Aktorzy")`.
4. `Sesja:poprosSerwer`: zdalna funkcja to `self.kontener.Zdalne.RozpocznijWalke2`.
5. `Aktorzy` klonuje szablony zawsze z `TestWalki2/Aktorzy` (kontener modułu), niezależnie od podanego kontenera.

**Wariant (b) — cięcie do areny prototypu i z powrotem (ZALECANY na start).** Działa bez zmian w plikach prototypu:
podajemy własny kontener (punkt 4 kieruje prośbę do naszego serwera), scena jest na arenie, kamera wraca do postaci
w lesie po zamknięciu (odtwarzacz przywraca `CameraType` i `CameraSubject`). **Usterka bez poprawki:** skoro
podany kontener to `LasPotwory`, punkt 2 nie wyklucza `TestWalki2/Arena` — podest, polana i las areny zostaną
schowane jak „obcy”, a aktorzy staną 1 stud nad płytą Baseplate (scena ma wysokość podestu). Walka, łup i wynik
działają; wygląda gorzej. Poprawka **P1** (niżej) usuwa to i niczego nie zmienia w walkach przy tablicy prototypu.

**Wariant (a) — walka na miejscu, na węźle.** Każdy węzeł jest płaskim placem (r 12 czysty), ale: trzeba przesunąć
scenę (punkt 1), przenieść i obrócić pudło chowania obcych (punkt 2) i wykluczyć z niego grunt lasu (inaczej odtwarzacz
schowa płytę i ścieżki — aktorzy zawisną w próżni), a drzewa poza r 12 i korony od 18 w górę wejdą kamerze w kadr przy
odległościach ujęć 12–30 studów. To wymaga zmian w prototypie i obejrzenia kadrów w kilku strefach (rynna Wąwozu,
labirynt — plan lasu sam wskazuje to ryzyko w rozdz. 13). **Nie na pierwszy raz.**

**Decyzja: (b) z poprawką P1** (dla Studio, wykonuje opiekun `swiat/test_walki2/`; ten pakiet tych plików nie zmienia):

- **P1 (zalecana).** `swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau`:
  - `Sesja:schowajObcych`, pętla `for _, n in { "Arena", "Aktorzy", "Galeria" } do … self.kontener:FindFirstChild(n)` →
    przechodzić po dwóch korzeniach: `{ self.kontener, moduly.Parent }` (`moduly.Parent` = `Workspace/TestWalki2`) i
    dopisywać znalezione do `wyklucz`.
  - `Sesja:przygotujScene`, `local szablony = self.kontener:FindFirstChild("Aktorzy")` →
    `local szablony = moduly.Parent:FindFirstChild("Aktorzy")`.
  - Dla walk przy tablicy prototypu `self.kontener == moduly.Parent`, więc zachowanie się nie zmienia.
- **P2 (opcjonalna).** Opcja `opcje.bezPowtorki`: w `Sesja:pokazWynik` przy `self.opcje.bezPowtorki` ukryć przycisk
  JESZCZE RAZ (`InterfejsWalki2`, element `jeszcze` z `Interfejs:pokazWynik`, `Visible = false`, bez podłączania
  `naJeszczeRaz`). Nasz klient podawałby wtedy zawsze `{ bezPowtorki = true }` (wynik znamy dopiero po walce), a
  rewanż po przegranej byłby ponownym E. Bez P2 wszystko działa — zostaje tylko usterka tekstu z 5.3.
- **P1 i P2 jako dokładna łata** (sprawdzona przy recenzji 15.11.2026 na bieżącym `OdtwarzaczWalki2.luau`, z
  nieskomitowanymi zmianami drugiego agenta; numery linii są przybliżone, bo plik się zmienia — szukać po tekście).
  Wykonuje opiekun `swiat/test_walki2/`; ten pakiet tych plików nie zmienia. Test `testy/test_styku.py`
  (`test_api_odtwarzacza`) sprawdza, że miejsca „było” wciąż istnieją; po wgraniu P1 trzeba w nim zmienić dwie
  asercje na nowy tekst.

  ```lua
  -- P1a. OdtwarzaczWalki2.luau, Sesja:schowajObcych (ok. linia 387). BYŁO:
  	local wyklucz = { self.scena }
  	for _, n in { "Arena", "Aktorzy", "Galeria" } do
  		local d = self.kontener:FindFirstChild(n)
  		if d then
  			table.insert(wyklucz, d)
  		end
  	end
  -- MA BYĆ (moduly = script.Parent = TestWalki2/Moduly, więc moduly.Parent = Workspace/TestWalki2):
  	local wyklucz = { self.scena }
  	for _, korzen in { self.kontener, moduly.Parent } do
  		for _, n in { "Arena", "Aktorzy", "Galeria" } do
  			local d = korzen:FindFirstChild(n)
  			if d and not table.find(wyklucz, d) then
  				table.insert(wyklucz, d)
  			end
  		end
  	end

  -- P1b. OdtwarzaczWalki2.luau, Sesja:przygotujScene (ok. linia 482). BYŁO:
  	local szablony = self.kontener:FindFirstChild("Aktorzy")
  -- MA BYĆ:
  	local szablony = moduly.Parent:FindFirstChild("Aktorzy")

  -- P2a (opcjonalna). OdtwarzaczWalki2.luau, Sesja:pokazWynik, zaraz PO wywołaniu ui:pokazWynik(self.walka, …) dopisać:
  	if self.opcje.bezPowtorki then
  		local przycisk = ui.wynik and ui.wynik.jeszcze -- TextButton „Przycisk”; jego rodzic to ramka „JeszczeRaz” z cieniem
  		if przycisk and przycisk.Parent then
  			przycisk.Parent.Visible = false
  		end
  	end

  -- P2b (opcjonalna). OdtwarzaczWalki2.luau, Sesja:jeszczeRaz, pierwszy warunek. BYŁO:
  	if self.faza ~= "wynik" or wolnaZa() > 0 then
  -- MA BYĆ:
  	if self.faza ~= "wynik" or wolnaZa() > 0 or self.opcje.bezPowtorki then
  ```

  Po P2 w `KlientPotworow.client.luau` zmienić `local OPCJE_WALKI = nil` na `local OPCJE_WALKI = { bezPowtorki = true }`.
  Dla walk przy tablicy prototypu nic się nie zmienia (`KlientWalki2` nie podaje `bezPowtorki`, a przy nim
  `self.kontener == moduly.Parent`).
- **Lista zmian dla wariantu (a) na później:** (A1) `Sesja:ustawAktorow`: `self.cfSceny = self.opcje.cfSceny or
  U.scena()`; (A2) `Sesja:schowajObcych`: pudło w `self.cfSceny * CFrame.new(U.OBSZAR_SRODEK − U.SRODEK)` z tym samym
  rozmiarem i dodatkowe wykluczenia `self.opcje.wyklucz` (np. `BiomLas/Teren`, `BiomLas/Sciezki`, `BiomLas/Woda`);
  (A3) jak P1; (A4) nasz serwer: `RequestStreamAroundAsync` przy węźle zamiast areny; nasz klient: `opcje.cfSceny` =
  węzeł potwora, scena obrócona tak, by kamera planu ogólnego miała słońce za plecami (w lesie słońce świeci z pd.-wsch.
  świata). Kadry do obejrzenia: z01, z11 (rynna), z09 (labirynt), z15 (taras), Strażnik.

---

## 7. Strażnik Gaju — cel strefy

- **Gdzie:** (0; 32; −373) w lesie = (0; 32; −1627) w świecie, na posadzce Kamiennego Kręgu przed filarem, twarzą na
  południe (rozdz. 2.3). Krąg jest strefą spokoju „tylko Strażnik Gaju” — zwykłe potwory i tak tu nie wchodzą.
- **Jak zaczyna się walka:** tak samo jak z każdym potworem — E w promieniu 8 + 4,45, poziom 10, gatunek
  `straznik_lasu` (w silniku ranga „straznik”, łup z Shardem Ewolucji z szansą — D-058). Przy „auto” bohater ma poziom 10.
- **Po wygranej:** zwycięzca widzi baner „STRAŻNIK GAJU POKONANY!” / „Wróci za 2 min”; Strażnik znika dla wszystkich
  po `zajetyDo` i wraca po 120 s (atrybut `StraznikWraca`). Nic więcej (bez słupa światła, kopca i warunku 10 wygranych).
- **Dlaczego wspólny, a nie osobny dla gracza:** plan domyślnie chce strażnika osobnego dla każdego gracza (wybór dla
  ludzi nr 1). Wspólny Strażnik to ta sama ścieżka kodu co zwykły potwór (strefa z jednym punktem i `L = 0`), bez
  nowego systemu. Wariant osobny = brak zajętości dla innych i czas powrotu liczony na gracza — etap B (pytanie 2).

---

## 8. Pliki, właściciele, zdalne, stałe, haczyki, budowa

### 8.1 Pliki i właściciele (rozłączne)

| Plik (`swiat/las_potwory/…`) | Pisze | Zależy od |
|---|---|---|
| `PROJEKT.md` | projektant (ten plik); wyniki Studio dopisuje osoba wdrażająca w rozdz. 9.3 | — |
| `logika.py` | **S** (serwer) | — |
| `testy/test_logiki.py` | **S** | `logika.py`, `generuj_dane.py` |
| `generuj_dane.py` | **S** | pliki lasu (tylko odczyt), `logika.py` (przeliczenie i kontrola pojemności) |
| `zrodla/DanePotworow.luau` | **wynik** `generuj_dane.py` (S uruchamia i commituje razem z kodem) | — |
| `zrodla/Logika.luau` | **S** | — |
| `zrodla/SerwerPotworow.server.luau` | **S** | `Stale`, `DanePotworow`, `Logika`, `Wzorcowe`, `Walka/*` |
| `zrodla/Stale.luau` | **K** (klient) — przepisuje tabelę 8.4 słowo w słowo | — |
| `zrodla/KlientPotworow.client.luau` | **K** | `Stale`, `DanePotworow` (tylko `gatunki`), moduły `TestWalki2/Moduly` |
| `zbuduj.py` | **K** | `generuj_dane.py --sprawdz`, `sprawdz_luau.py`, (w Studio) `tools/studio_mcp.py`, `swiat/test_walki_roblox/cel_studio.py` |
| `sprawdz_luau.py` | **K** | — |
| `testy/test_styku.py` | recenzent (15.11) | czyta jak tekst: oba skrypty, `zbuduj.py`, bieżące pliki `swiat/test_walki2/`, `src/server/Walka/Silnik.luau` |
| `README.md` | recenzent (15.11) | krótko: co to jest, budowa, usuwanie, testy |

Obaj zaczynają od razu: S nie potrzebuje kodu K (stałe ma w 8.4), K nie potrzebuje kodu S (format danych w 2.4,
atrybuty w 3.8; do prób offline może napisać sobie w notatniku kilka linii `DanePotworow` ręcznie — **poza
repozytorium**). Jedyny punkt spotkania to ten dokument.

### 8.2 Zdalne

Jedna: `LasPotwory/Zdalne/RozpocznijWalke2` (RemoteFunction), ładunki w 5.1. **Żadnych innych** RemoteEventów ani
RemoteFunction. Stan idzie atrybutami (3.8). Klient nie wywołuje jej sam — robi to odtwarzacz.

### 8.3 Atrybuty — pełna lista

- `LasPotwory/Stan/<id>`: `Gatunek`, `Nazwa`, `Wariant`, `Strefa`, `Poziom`, `Straznik`, `Pozycja`, `Kierunek`,
  `Stan` (3.8). Pisze serwer, czyta klient.
- `LasPotwory` (serwer): `SerwerGotowy`, `StanBiomu`, `SzablonyGotowe`, `Graczy`, `Potworow`, `ZgodnoscLogiki`,
  `SerwerLicznikWalk`, `SerwerOstatniaWalka`, `SerwerOstatnieZiarno`, `StraznikWraca`.
- `LasPotwory` (ustawia człowiek w Edit, czyta serwer; tylko testy): `ZiarnoTestowe` (number), `TestBezSesji` (bool),
  `TestGraczy` (number), `TestBezBiomu` (bool). Zmiana u klienta się nie replikuje, więc klient ich nie nadużyje.
- `LasPotwory` (klient, lokalnie, dla testów): `KlientGotowy`, `KlientTryb` (`"aktorzy"` / `"zastepczy"`),
  `KlientKlasa`, `KlientPoziom`, `KlientWidoki`; oraz `Ostatni*` i `NastepnaWalkaOd` ustawiane przez odtwarzacz na
  podanym kontenerze (`OstatniWynik`, `OstatniStan`, … — lista w `Sesja:pokazWynik`).

### 8.4 `zrodla/Stale.luau` (treść wiążąca)

```lua
--[[
	Stale — wspólne stałe pakietu „potwory w ruchu” (serwer i klient czytają je z jednego miejsca).
	Liczby zasad (odstęp, smycz, blokada domu, prędkości) są w DanePotworow (z potwory.json), nie tutaj.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local S = {}
S.WERSJA = "las_potwory etap A (2026-11-15)"
S.NAZWA_KONTENERA = "LasPotwory"
S.NAZWA_BIOMU = "BiomLas"
S.NAZWA_PROTOTYPU = "TestWalki2"
S.NAZWA_SZABLONOW = "LasPotworySzablony"         -- ReplicatedStorage
S.SZABLONY = { "lesny_slime", "cierniowy_wilk", "muchomornik", "straznik_lasu" }
S.PREFIKS = "[LasPotwory] "
S.GADATLIWY = false           -- true: serwer drukuje każde odrodzenie i wejście na pętlę

------------------------------------------------------------------ serwer
S.OKRES_RUCHU = 0.25          -- s (4 Hz)
S.OKRES_ODRADZANIA = 1.0      -- s
S.ODSTEP_PROSB = 1.0          -- s, jak SerwerWalki2
S.ZAPAS_SESJI = 0.4           -- s, jak SerwerWalki2
S.ZAPAS_ZAJETOSCI = 1.0       -- s ponad walka.czas
S.ZASIEG_E = 8                -- studs w poziomie od punktu bazowego + promień gatunku
S.ZAPAS_E_SERWER = 6          -- studs zapasu po stronie serwera (opóźnienie, ruch 4 Hz) — 17.11.2026 (M6): 10, a klient ma
                              -- histerezę HISTEREZA_E = 7 dla bieżącego kandydata (patrz Stale.luau i testy/test_podpowiedzi_e.py)
S.MAKS_ROZNICA_WYSOKOSCI = 6
-- 17.11.2026 (runda 3, propozycja): zatrzymanie przy graczu — potwór, do którego gracz podszedł na
-- ZASIEG_E + promień + ZATRZYMANIE_ZAPAS, staje (Stan "stoi", klient gra spoczynek) i obraca się do najbliższego
-- gracza, najwyżej ZATRZYMANIE_MAKS_S naraz, potem idzie co najmniej ZATRZYMANIE_PRZERWA_S; jego grupa stoi jak
-- grupa z zajętym (Logika.krokGrup, odstęp 25 bez zmian); Strażnik bez zmian. Decyduje serwer (SerwerPotworow:
-- aktualizujZatrzymania); TestBezZatrzyman = true na kontenerze wyłącza (pomiar „przed”). Symulacja w Pythonie nie ma graczy.
S.ZATRZYMANIE_ZAPAS = 4
S.ZATRZYMANIE_MAKS_S = 20
S.ZATRZYMANIE_PRZERWA_S = 5
S.PRZEDPOLE = 6               -- studs od węzła w stronę domu
S.PROG_POZYCJI = 0.05         -- studs: mniejszej zmiany nie zapisujemy
S.PROG_KIERUNKU = math.rad(2)
S.KLASY = { "wojownik", "zwiadowca", "mag" }
S.POZIOMY_BOHATERA = { "auto", "1", "5", "10" }
S.ARENA_PROTOTYPU = Vector3.new(0, 1, 250)  -- = Ustawienia.scena().Position w swiat/test_walki2

------------------------------------------------------------------ klient
S.PROMIEN_WIDOKU = 120
S.PROMIEN_USUNIECIA = 135
S.MAKS_WIDOKOW = 12           -- budujemy i animujemy najwyżej tylu najbliższych
S.MAKS_WIDOKOW_TWARDO = 14
S.BUDZET_CZESCI = 4000        -- suma brył wszystkich widoków (telefon: zacząć od 1500, rozdz. 10)
S.BUDOWA_CO = 0.1             -- s między kolejnymi klonami
S.WYBOR_CO = 0.5              -- s między przeliczeniami listy widoków
S.PODPOWIEDZ_CO = 0.1
S.SKOK_WYGLADZANIA = 20
S.OBROT_NA_S = 8              -- rad/s
S.CZERWONA_OD = 3             -- poziomów ponad poziom bohatera
S.TABLICZKA_ZASIEG = 80
S.BANER_S = 5

------------------------------------------------------------------ kolory (jak Ustawienia.KOLORY prototypu)
local function hex(h: string): Color3
	return Color3.fromHex(h)
end
S.KOLORY = {
	tusz = hex("#17121F"), bialy = hex("#FFFFFF"), krem = hex("#FFF3D1"), zolty = hex("#FFD23F"),
	czerwony = hex("#E8364F"), zielony = hex("#52D273"), fiolet = hex("#7B4DFF"), szary = hex("#8D93A6"),
}
S.KOLOR_BURSZTYNOWY = hex("#F2B030")

return S
```

### 8.5 Szkielet skryptów (żeby było łatwo czytać i debugować)

- **Nagłówek** każdego pliku `.luau`: komentarz `--[[ … ]]` po polsku jak w `zrodla/` prototypu (co plik robi, API,
  co sprawdza test), potem strażnik Studio. Identyfikatory po polsku (`potwor`, `strefa`, `grupa`, `widok`).
- **Komunikaty:** `print`/`warn` zawsze z `Stale.PREFIKS`. Serwer drukuje: start (liczby jak w 3.4), każdą walkę
  (`walka z01-2 wojownik/auto→1 lesny_slime 1 → wygrana, 23,4 s`), a każde odrodzenie i wejście na pętlę tylko przy
  `Stale.GADATLIWY = true`.
- **Błędy w pętlach** (`xpcall` wokół tyknięcia serwera i klatki klienta) → jeden `warn` z `debug.traceback`, pętla
  działa dalej; po 10 błędach z rzędu pętla serwera staje i ustawia `SerwerGotowy = false`.

### 8.6 Haczyki testowe (tylko Studio, jak w prototypie)

`Sygnaly/SterowanieSerwera` (BindableFunction, `OnInvoke` ustawia serwer; wołać z kodu po stronie serwera w Play):

| Polecenie | Wynik |
|---|---|
| `"strefy"` | `{ [id] = { cel, istnieje, kolejka, grupy = { {s, dlugosc, stoi} }, minLuka, czekajacy } }` |
| `"potwor", id` | stan wewnętrzny jednego potwora (stan, grupa, miejsce, zajetyDo, wynik) |
| `"zabij", id` | potwór usunięty jak po wygranej (wpis do kolejki) — test odradzania |
| `"gracze", n` | jak atrybut `TestGraczy` (nil = wyłącz) |
| `"zgodnosc"` | `{ ok, n, bledy }` z `Logika.sprawdzPrzypadki()` |

`Sygnaly/SterowanieKlienta` (BindableFunction, ustawia klient):

| Polecenie | Wynik |
|---|---|
| `"stan"` | `{ tryb, widoki, animowane, czesciWidokow, najblizszy = id?, podpowiedz = bool, bohater = { klasa, poziom }, walka = Odtwarzacz.czyTrwa() }` |
| `"walcz", id` | zaczyna walkę z tym potworem jak po E (serwer i tak sprawdza odległość) |
| `"bohater", klasa, poziom` | ustawia wybór z panelu |

### 8.7 `zbuduj.py` (pisze K, uruchamia później osoba wdrażająca)

Wzór: `swiat/test_walki2/zbuduj.py` — te same zasady bezpieczeństwa (tylko tryb Edit, `game.PlaceId` z
`swiat/test_walki_roblox/cel_studio.py` w każdym kodzie, kontener z `Wygenerowane = true`, przerwanie, gdy pod nazwą
`LasPotwory` jest coś bez atrybutu, punkty historii `ChangeHistoryService` przed i po, kontrola strażnika Studio w
każdym źródle, niczego nie publikuje ani nie zapisuje miejsca).

```
python -B swiat/las_potwory/zbuduj.py --sucho      # bez Studio: generuj_dane --sprawdz, sprawdz_luau, strażniki, plan
python -B swiat/las_potwory/zbuduj.py              # buduje / odbudowuje Workspace/LasPotwory (idempotentnie)
python -B swiat/las_potwory/zbuduj.py --skrypty    # tylko skrypty i moduły do istniejącego kontenera
python -B swiat/las_potwory/zbuduj.py --usun       # usuwa Workspace/LasPotwory (np. przed publikacją)
python -B swiat/las_potwory/zbuduj.py --studio <studio_id>
```

- `--sucho` **nie importuje** `studio_mcp` ani `cel_studio` (import dopiero po gałęzi `--sucho`, jak w prototypie) i
  wypisuje: każdą instancję (ścieżka, klasa, `RunContext`, liczba znaków), wynik `generuj_dane.py --sprawdz` (przerwij,
  gdy dane nieaktualne), wynik `sprawdz_luau.py` (przerwij przy błędzie), skrót danych.
- Budowa tworzy foldery `Moduly`, `Moduly/Walka`, `Stan`, `Zdalne`, `Sygnaly`; instancje `RemoteFunction
  Zdalne/RozpocznijWalke2`, `BindableFunction Sygnaly/SterowanieSerwera`, `BindableFunction Sygnaly/SterowanieKlienta`;
  moduły i skrypty z tabeli 1.1. Kopie `src/server/Walka/*.luau` dostają na początku linię
  `-- KOPIA <plik> zrobiona przez swiat/las_potwory/zbuduj.py (<data>) — źródło prawdy jest w repozytorium.` i
  strażnika modułu; `Wzorcowe.luau` ma własnego strażnika — kopiować bez dopisku, tylko sprawdzić strażnika.
- W Studio przed budową (tylko odczyt, ostrzeżenia, nie przerywa): czy jest `Workspace/BiomLas` z `Wygenerowane`,
  czy jest `Workspace/TestWalki2/Moduly/OdtwarzaczWalki2` i `TestWalki2/Aktorzy/<4 klucze>`. Żadnych części, więc bez
  kontroli pudła. Na koniec: liczba instancji i skryptów w kontenerze.

### 8.8 `sprawdz_luau.py` (pisze K) — tania kontrola statyczna

`python -B swiat/las_potwory/sprawdz_luau.py [pliki…]` (domyślnie `swiat/las_potwory/zrodla/*.luau`), kod 1 przy błędzie:

1. Po usunięciu komentarzy (`--[[…]]`, `--[==[…]==]`, `--…`) i napisów (`"…"`, `'…'`, `[[…]]`, `` `…` `` z `{}`)
   bilans bloków: otwierają `function`, `do`, `repeat` oraz `then` po instrukcji `if`; zamykają `end`, `until`.
   `then` po `elseif` niczego nie otwiera. **Wyrażenie `if`** (Luau: `local x = if a then b else c`) nie otwiera
   bloku: `if` jest wyrażeniem, gdy poprzedni znaczący token to `=`, `(`, `,`, `{`, `[`, `return`, `and`, `or`,
   `not`, `..`, operator arytmetyczny lub porównania, `+=`, `-=`, `..=`. Na końcu pliku stos pusty; błąd podaje linię
   bloku bez pary.
2. Bilans `()`, `{}`, `[]`.
3. Pierwsza instrukcja (po komentarzach) to strażnik Studio.
4. Zakazane: `PathfindingService`, `Lighting`, `loadstring`, `getfenv`, `setfenv`, `InvokeClient`, wywołania
   globalnych `wait(`, `spawn(`, `delay(` (bez `task.`).
5. Atrybuty stanu: każdy napis z `GetAttribute("…")` w `KlientPotworow` należący do listy 8.3 (stan potwora) musi
   występować w `SetAttribute("…")` w `SerwerPotworow`; każdy z 9 atrybutów stanu musi być ustawiany przez serwer.
6. Samosprawdzenie: `--test` przepuszcza wszystkie `swiat/test_walki2/zrodla/*.luau` (znany dobry zbiór — oczekiwane
   0 błędów bilansu; reguły 3–5 tam pomijamy) i dwa zepsute fragmenty z pamięci skryptu (brak `end`, nadmiarowy `end`).

---

## 9. Testy

### 9.1 Teraz, offline (bez Studio)

`python -B swiat/las_potwory/testy/test_logiki.py` (unittest, pisze S):

1. Wszystkie przypadki wzorcowe z 3.7a.
2. **Odstęp:** dla każdej strefy z wygenerowanych danych symulacja 30 min (dt 0,25) przy `cel = max`: losowe walki
   (co ok. 25 s jedna, 8–40 s, 60% wygranych → usunięcie i odrodzenie wg 3.5, wejście wg 3.3, dom wybierany losowo).
   Wymagane: luka czoło → ogon dla każdej prawdziwej grupy ≥ 25 − 1e-6 w każdym tyknięciu; żadna grupa nie cofa się
   ani nie robi kroku > v·dt; po wyłączeniu walk na ostatnie 120 s każdy czekający wchodzi na pętlę. Ziarna 3 i 11.
3. **Pojemność:** `grupy × ((miejsc − 1) × odstepWGrupie + 25) ≤ L` dla każdej strefy (najciaśniej: z02 zapas 2,3,
   z12 zapas 3,4 — dodatek A).
4. **Liczby:** suma `cel` po strefach = 35 / 64 / 86 dla G = 1 / 8 / 20.
5. **Geometria danych:** każdy węzeł i punkt pętli (próbki co 2 st) ≤ `r + 10` od środka strefy; żaden punkt pętli ani
   odcinka dom → przedpole w kole strefy spokoju ani w wielokącie Serca (w świecie, z `spokoj` i `serce`); dom 35–50 od
   najbliższego węzła; przedpole dokładnie 6 od węzła; z09: 9 punktów trasy, `zamknieta = false`, L = 475,1 ± 0,2.
6. **Przeliczenie:** węzeł 1 z01 → (−206,3; 0; −2294,5); Strażnik → (0; 32; −1627); `trasa.y` = y strefy.
7. **Generator:** dwa uruchomienia do katalogu tymczasowego dają identyczne bajty; `--sprawdz` przechodzi na pliku z
   repozytorium; plik nie zawiera daty ani ścieżek lokalnych.

8. **Brzegi (dopisane przy recenzji, klasa `TestBrzegi`):** 0, −3 i 1 gracz dają 35 potworów, 4 graczy 45, 100
   graczy 86; cel nigdy nie przekracza `grupy × miejsc`; przy 0 graczach w strefie odrodzenie trwa dokładnie bazę
   (15 s w z01); minimum 10 s działa (20 graczy w z01 → 10 s, a nie 2,4 s); Strażnik (strefa z jednym punktem,
   `L = 0`) wraca dokładnie po 120 s także przy graczu 2 studa obok i w jednym tyknięciu staje na miejscu;
   wszystkie domy zablokowane → wpis czeka, a po odejściu gracza powstaje potwór w następnym domu karuzeli; nadmiar po
   odejściu graczy zostaje, a wpisy, które dojrzały przy mniejszym celu, przepadają; trzy uruchomienia generatora i
   plik z repozytorium są identyczne co do bajtu; kolejność kroków tyknięcia w Luau jest ta sama co w klasie
   `Symulacja` (prosty wykrywacz rozjazdu lustra). Klasa `Symulacja` kopiuje od recenzji także odradzanie serwera
   (karuzela domów, blokada 18, gracze w strefie, wyjątek Strażnika), a nie losowy dom.

`python -B swiat/las_potwory/testy/test_styku.py` (dopisany przy recenzji): punkty styku czytane z plików jak tekst —
każda dosłowna nazwa z `WaitForChild`/`FindFirstChild` w serwerze i kliencie istnieje w planie `zbuduj.py` albo w
prototypie; każdy atrybut, który klient czyta, ktoś ustawia; odtwarzacz wysyła dokładnie trzy pola, a serwer czyta
dokładnie te trzy; każdy powód odmowy serwera (poza `blad_silnika`) jest w `POWODY_CICHE`; klient nie ma
`InvokeServer`/`FireServer`; kolejność kontroli 1–9 w `OnServerInvoke`; bieżące API odtwarzacza, Klipy, pól
`TabelaAktorow`, `Wzorcowe.KLASY`, wyniku silnika i położenia areny; strażnik Studio i samousunięcie; brak ścieżek
lokalnych. **Uruchomić go jeszcze raz tuż przed wdrożeniem**, bo prototyp zmienia inny agent.

`python -B swiat/las_potwory/sprawdz_luau.py` i `--test` (pisze K). `python -B swiat/las_potwory/zbuduj.py --sucho`
(pisze K) — zbiera wszystko powyżej i pokazuje plan budowy.

### 9.2 Później, w Studio (osoba wdrażająca; nic z tego nie robimy teraz)

**Przed budową (w terminalu, bez Studio), wszystko ma skończyć się kodem 0:**

```
python -B swiat/las_potwory/testy/test_logiki.py      # 17 testów, ok. 6 s
python -B swiat/las_potwory/testy/test_styku.py       # 15 testów, < 1 s (czyta bieżący prototyp)
python -B swiat/las_potwory/sprawdz_luau.py           # „5 plików, OK”
python -B swiat/las_potwory/zbuduj.py --sucho         # „sucho: OK”, 12 modułów i skryptów, Skrot danych 3f657732d08e
```

Gdy `test_styku.py` nie przechodzi, prototyp się zmienił: najpierw ustalić z jego opiekunem, co się zmieniło, i
poprawić klienta albo serwer, zanim cokolwiek trafi do Studio. Opcjonalnie P1 (i P2) u opiekuna prototypu (rozdz. 6).

**Budowa (Studio w trybie Edit, właściwe miejsce):** `python -B swiat/las_potwory/zbuduj.py` (przy kilku oknach Studio
`--studio <studio_id>`). Skrypt wypisuje najpierw „w miejscu (tylko odczyt): …” — tam jest zmierzona Płyta i ewentualne
ostrzeżenia o TestWalki2 — a na końcu „gotowe: instancji: N, skryptów: 12, części: 0, Skrot = 3f657732d08e”.
Liczba części musi wynosić 0. Wymiana samych skryptów po poprawce: `--skrypty`. Usunięcie: `--usun`.

**Edit — polecenia na pasek poleceń (tylko odczyt), wyniki do 9.3:**

```lua
-- E1: kontener i Płyta (sprawdzenie wzoru świat = (−x, y, −2000 − z) na prawdziwym kontenerze)
local f = workspace.LasPotwory print(f:GetAttribute("Wygenerowane"), f:GetAttribute("Skrot"), #f.Stan:GetChildren())
local p = workspace.BiomLas.Teren.Grunt["Płyta"] print(p.Position, p.Size, p.Orientation)
-- oczekiwane: true 3f657732d08e 0 | 0, -1, -2000 | 1400, 2, 1400 | 0, 180, 0 (albo 0, -180, 0)

-- E2: trzy promienie w dół — tylko trzeci i drugi rozróżniają obrót o 180° (lustrzany punkt leży na Łące, y 0)
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Include rp.FilterDescendantsInstances = { workspace.BiomLas }
for _, o in { Vector3.new(-206.3, 10, -2294.5), Vector3.new(-174.8, 22, -1889.6), Vector3.new(0, 40, -1627) } do
	local r = workspace:Raycast(o, Vector3.new(0, -30, 0), rp)
	print(o, r and r.Instance:GetFullName(), r and r.Position.Y)
end
-- oczekiwane: y 0,0–0,5 (węzeł 1 z01); y ≈ 12 (węzeł 1 z13, Półka Zachodnia); y 32,1–32,3 w „Krąg posadzka…”, NIE „Filar”
```

Do tego: dzieci `LasPotwory` jak w tabeli 1.1 (`Moduly` z 5 modułami i folderem `Walka` z 6, `Stan` pusty, `Zdalne`,
`Sygnaly`, dwa skrypty z `RunContext` Server i Client); jest `Workspace/TestWalki2/Moduly/{OdtwarzaczWalki2, Klipy,
TabelaAktorow, DaneAktorow/<4>}` i `TestWalki2/Aktorzy/<4>`; poza `LasPotwory` w Workspace nic nowego.

**Play solo (1 gracz) — co ma się pojawić i jakie liczby:**

```lua
-- P1 (widok serwera, pasek poleceń)
local f = workspace.LasPotwory
print(f:GetAttribute("SerwerGotowy"), f:GetAttribute("StanBiomu"), f:GetAttribute("SzablonyGotowe"), f:GetAttribute("Potworow"),
	f:GetAttribute("Graczy"), f:GetAttribute("ZgodnoscLogiki"), #game.ReplicatedStorage.LasPotworySzablony:GetChildren())
-- oczekiwane: true ok true 36 1 OK 70/70 4
local S = f.Sygnaly.SterowanieSerwera
for id, s in S:Invoke("strefy") do print(id, s.cel, s.istnieje, #s.kolejka, s.minLuka) end
-- oczekiwane przy 1 graczu: cel = istnieje = kolumna G = 1 z dodatku A (z01 3, z02 3, z16 2, …, z08 3, z10 1, straznik 1),
-- kolejka 0, minLuka ≥ 25 (albo inf w strefach z jedną grupą)

-- P4 (prędkość, widok serwera): czoło grupy z01 w 10 s przesuwa się o 60 ± 1 (6 st/s), gdy przed nią jest wolno
local a = S:Invoke("strefy").z01.grupy[1][1] task.wait(10) local b = S:Invoke("strefy").z01.grupy[1][1] print((b - a) % 267.242)

-- P3/P5/P6 (widok klienta): przestaw postać i zajrzyj w stan klienta
game.Players.LocalPlayer.Character:PivotTo(CFrame.new(-250, 6, -2300)) -- środek z01
local s = workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan")
print(s.tryb, s.widoki, s.animowane, s.czesciWidokow, s.najblizszy, s.podpowiedz, s.bledy)
-- oczekiwane: aktorzy 3 3 ok. 345 (3 slime’y × liczbaCzesci z TabelaAktorow, ok. 115) nil albo „z01-…” false/true 0
```

Lista Play (numeracja jak w pierwotnym kontrakcie, liczby i polecenia po recenzji):

1. Output w 5 s: `[LasPotwory] gotowy: 35 potworów w 16 strefach + Strażnik Gaju; zgodność logiki 70/70` i po
   stronie klienta `[LasPotwory] klient gotowy: tryb aktorzy, potworów w Stan: 36`; bez czerwonych błędów i bez
   `warn` z prefiksem `[LasPotwory]` (poza ostrzeżeniem o `TestBezBiomu`, jeśli ustawiony).
2. Atrybuty jak w P1 wyżej; `Stan` ma 36 dzieci.
3. W z01: `tryb = "aktorzy"`, `widoki = 3`, slime’y skaczą klipem `ruch`, tabliczki „poz. 1” / „poz. 2”.
4. Prędkość 60 ± 1 w 10 s; okrążenie z01 ok. 44,5 s; `minLuka ≥ 25` w każdej strefie.
5. Podpowiedź pojawia się w poziomie ≤ 9,35 od slime’a, znika dalej; teksty „Leśny Slime · poz. N” i „Walcz”.
6. E → zaciemnienie → walka na arenie prototypu (z P1 na podeście; bez P1 na płycie, aktorzy 1 stud wyżej) → okno
   wyniku z łupem → ZAMKNIJ → kamera wraca do postaci w lesie. Output serwera: jedna linia
   `[LasPotwory] walka z01-… wojownik/auto→N lesny_slime N → wygrana|przegrana, X,X s`; `SerwerLicznikWalk = 1`.
   Przez `walka.czas + 1` s potwór ma `Stan = "zajety"` (miecze nad nim widać z drugiego klienta).
7. Po wygranej: widok znika od razu po zamknięciu okna; po `zajetyDo` Configuration znika (`Potworow = 35`); po
   15 s (1 gracz w strefie; 0 graczy też daje 15 s) pojawia się `z01-4` w jednym z trzech domów w stawie, idzie ok.
   39–44 st (ok. 7 s), staje w przedpolu i wchodzi na pętlę. Szybciej: `S:Invoke("zabij", "z01-1")` w widoku serwera.
8. Przegrana: `SterowanieKlienta:Invoke("bohater", "wojownik", "1")`, walka z muchomornikiem z05 (poz. 4–5), aż do
   przegranej; po `zajetyDo` potwór wraca na trasę; JESZCZE RAZ (gdy minie blokada „ZA N s”) zaczyna rewanż.
9. Tabliczki: przy poziomie „1” czerwone od poz. 4 (z04 poz. 4, z05); przy „auto” żadna.
10. Strażnik: `Character:PivotTo(CFrame.new(0, 36, -1640))` → model Strażnika na posadzce przed filarem, podpowiedź
    „Strażnik Gaju · poz. 10”; wygrana (poziom „10” albo „auto”) → baner na 5 s; `StraznikWraca` ≈ teraz + 120 (czas
    `workspace:GetServerTimeNow()`); Strażnik wraca po tym czasie **także wtedy, gdy stoisz obok** (po recenzji nie
    trzeba odchodzić).
11. Skalowanie (widok serwera): `S:Invoke("gracze", 8)` → `Potworow` dochodzi do 65 w ok. 30 s (najdłuższa baza 25 s
    plus wyjście z domu); `S:Invoke("gracze", 20)` → 87; `S:Invoke("gracze", 1)` → 87 zostaje, nikt nie znika sam;
    `S:Invoke("gracze", nil)` wyłącza.
12. Dwóch graczy (Test → Local Server, 2 graczy): B widzi miecze nad potworem A i nie ma podpowiedzi;
    `SterowanieKlienta:Invoke("walcz", id)` u B → dymek „Serwer nie przyjął tego wyboru…”; zamknięcie okna A
    w trakcie walki → potwór od razu wolny albo usunięty.
13. Wydajność w Ostępach (`PivotTo(CFrame.new(325, 6, -1895))`, z08 + z07): `widoki ≤ 12`, `czesciWidokow ≤ 4000`;
    MicroProfiler: nasz kod klienta < 1 ms na klatkę średnio, tyknięcie serwera < 1 ms.
14. Emulator telefonu 844 × 390 i 667 × 375: stuknięcie podpowiedzi zaczyna walkę; panel bohatera czytelny i w kadrze.
15. Po zatrzymaniu Play: nie ma `ReplicatedStorage/LasPotworySzablony`, w Workspace tylko zbudowany `LasPotwory`.
16. (Dopisane przy recenzji) Ścieżki „zły las” i „brak prototypu” **nie testujemy we wspólnym miejscu**: wymagałoby
    to przestawiania cudzych kontenerów (BiomLas, TestWalki2). Sprawdza się je tylko wtedy, gdy ktoś ma własną kopię
    miejsca. W wspólnym miejscu wystarczy upewnić się, że w Output nie ma ostrzeżeń `… potwory nie wystartują`.

**Filmy do nagrania:** (F1) przelot nad z01 z 30 st: slime’y idą pętlą, tabliczki (30 s); (F2) z08: dwie watahy,
jedna z zajętym wilkiem (dwóch graczy) — kolejka staje za zajętą; (F3) pełny cykl w z01: podejście → E → walka ×2 →
łup → powrót → nowy slime wychodzi ze stawu i wchodzi na pętlę; (F4) Strażnik: wygrana i baner; (F5) emulator
telefonu: stuknięcie podpowiedzi i panel bohatera. Do filmów walki jest `swiat/test_walki2/testy/film_walki.py`.

### 9.3 Wyniki Studio

**15.11.2026, godz. 19:32–19:46, wspólne miejsce, Play solo, Skrot danych `3f657732d08e`.** Jedna długa sesja
skryptem `testy/kontrola_play.py` i trzy krótkie sesje uzupełniające (dokładny czas odrodzenia z dziennika zdarzeń
`Stan` po stronie serwera, prawdziwe naciśnięcie E). Studio było w trybie Edit przed każdą sesją (bez czekania) i
po każdej do niego wróciło. Liczby: zmierzone obok oczekiwanych.

| Punkt 9.2 | Oczekiwane | Zmierzone | Wynik |
|---|---|---|---|
| P1 atrybuty | true ok 36 1 OK 70/70, `Stan` 36 | true ok 36 1 „OK 70/70”, `Stan` 36 | tak |
| 1 Output | dwie linie „gotowy”, bez błędów | obie linie, zero błędów i `warn` z `[LasPotwory]` | tak |
| 3 z01 | aktorzy, 3 widoki, ok. 345 części | aktorzy, 3 widoki, 3 animowane, 345 części, 0 błędów | tak |
| 4 odstępy | `minLuka ≥ 25` | 25,0 i więcej w każdej strefie (po skalowaniu z01: 24,9 — haczyk zaokrągla w dół do 0,1) | tak |
| 5 podpowiedź E | E zaczyna walkę | prawdziwe naciśnięcie E przy Strażniku i przy slime'ie zaczyna walkę; dymek „Prompt” jest w `PlayerGui/ProximityPrompts`, teksty „Leśny Slime · poz. 1” / „Strażnik Gaju · poz. 10”, „Walcz” | tak, ale zob. uwagę 2 |
| 6 walka i ZAMKNIJ | arena → wynik → ZAMKNIJ → kamera w lesie | wojownik poz. 10 kontra slime poz. 2: wygrana, 11,0 s; ZAMKNIJ kliknięte myszą; potem kamera `Custom` na humanoidzie, 12 st od postaci, W przez 0,9 s = 15 st; postać w lesie | tak |
| 7 odrodzenie | widok znika od razu; nowy po 15 s, wychodzi z domu i wchodzi na pętlę | widok zniknął od razu; `zajetyDo` = start + 9,4 s; nowy `z01-4` 15,5 s po usunięciu (dziennik serwera), start w stanie `wychodzi` przy domu w stawie, po ok. 10 s `chodzi`; wilk z08: 25,7 s (oczekiwane 25) | tak |
| 10 Strażnik | `StraznikWraca` ≈ teraz + 120; wraca także, gdy stoisz obok | `StraznikWraca` = chwila zabicia + 120,7 s; wrócił po 121,8 s, postać cały czas obok; potem podpowiedź włączona i 1 widok | tak (zabity haczykiem „zabij”; baneru po wygranej nie sprawdzano) |
| 11 skalowanie | 8 graczy → 65, 20 → 87, z powrotem 1 → 87 zostaje | 64 + Strażnik = 65, 86 + Strażnik = 87, po zmianie na 1: 87; cel każdej strefy równy kolumnom G = 1 / 8 / 20 z dodatku A; kolejki puste po 40–45 s | tak |
| 13 koszt (Ostępy, 87 potworów) | widoki ≤ 12, części ≤ 4000, klient < 1 ms, serwer < 1 ms | widoki 7, części 3808, animowane 7; **klient 2,0 ms na klatkę średnio (maks. 4,2)**, z tego przestawianie korzeni 0,38 ms na wywołanie (ok. 112 ms na sekundę gry), klipy 0,02 ms; serwer: tyknięcie ruchu 0,51 ms średnio (maks. 1,1), odradzanie 0,04 ms | klient **nie**, serwer tak |
| wilki i Muchomorniki | widoki stoją na ziemi, animują się, walka rusza | z08: 7 widoków wilków, spód modelu 0,09–0,10 przy gruncie 0,10–0,11, 7/7 animowanych; walka z `z08-3` (poz. 6) wygrana, 11,2 s. z04: 8 widoków, spód 0,08–0,25 przy gruncie 0,10–0,27; 12 z 13 widoków w kadrze animowanych (dalszy widok liczony rzadziej); walka z `z04-8` (poz. 3) wygrana, 18,3 s | tak |
| 14 telefon | panel czytelny i w kadrze 844 × 390 i 667 × 375 | emulacja prototypu działa tylko dla jego interfejsu, więc zmierzono nasz panel: 360 × 220 pkt (mieści się w obu ekranach), najmniejszy napis 16 pkt (próg 12), przycisk u góry 250 × 34 pkt; wycinek ekranu o rozmiarze telefonu w `klatki/kontrola_telefon.jpg` | tak (stuknięcia palcem nie sprawdzono) |
| 15 po Stop | tryb Edit | tryb Edit po każdej z czterech sesji | tak |

Nie sprawdzono: 8 (przegrana i rewanż), 9 (czerwone tabliczki przy poziomie „1”), 12 (dwóch graczy), baner Strażnika
po wygranej, prawdziwy dotyk na telefonie, MicroProfiler (koszt mierzony haczykami „koszt”).

**Poprawione przy kontroli:** nagłówki „KLASA” i „POZIOM BOHATERA” w panelu bohatera miały szary kolor na kremowym
tle i na wycinku telefonu były ledwo widoczne; mają teraz kolor tuszu (`KlientPotworow.client.luau`, przebudowa
`zbuduj.py --skrypty`: 12 skryptów, 0 części). Skrypt `testy/kontrola_play.py` dostał dziennik zdarzeń `Stan` (dokładny
czas odrodzenia) i nie wkleja już zrzutów z Ostępów do filmu.

**Uwagi:**
1. Koszt klienta przy watasze wilków jest dwa razy wyższy od celu (2,0 ms zamiast 1 ms na klatkę, na komputerze).
   Prawie cały to przestawianie modelu wilka z 1154 elementami; łagodzenie z 15.11 (rzadsze klatki dla dalszych)
   nie pomaga, gdy gracz stoi w środku watahy. Na telefonie będzie gorzej. To sprawa lżejszych modeli albo mocniejszego
   cięcia klatek, nie drobnej poprawki.
2. Zrzut ekranu z narzędzia MCP nie pokazuje dymka podpowiedzi (ani nad slime'em, ani przy Strażniku), choć dymek
   istnieje i E działa. Tabliczki poziomu, które są w świecie, na zrzutach widać. Wygląd dymka trzeba raz ocenić okiem.
3. Po pominięciu walki (przewinięcie, POMIŃ) blokada prototypu liczy się w czasie rzeczywistym, więc przez resztę
   długości walki E przy następnym potworze nic nie zaczyna (podpowiedź pokazuje „Walcz (za N s)”). Zgodnie z
   kontraktem, ale gracz, który pomija walki, odczuje to jako przerwę.

Film: `klatki/film_las_potwory.mp4` (35 s, 1280 × 720, H.264): slime'y w lesie, gracz przy slime'ie, walka na arenie,
okno wyniku, powrót do lasu, nowy slime wychodzi z domu w stawie. Zrzuty: `klatki/kontrola_*.jpg`, przebieg kontroli:
`klatki/kontrola_postep.txt`.

---

## 10. Ryzyka i budżet wydajności (telefon)

**Instancje na model** (z danych `swiat/test_walki2/dane/*.json` i pomiarów prototypu; ok. 2 × bryły + 2 × kości):

| Gatunek | Bryły | Instancje klonu | Uwagi |
|---|---|---|---|
| Leśny Slime | 115 | ok. 320 | skóra: 23 siatki przeliczane co klatkę |
| Muchomornik | 157 | ok. 380 | |
| Cierniowy Wilk | 544 | 1138 (pomiar) | najdroższy z chodzących |
| Strażnik Gaju | 1128 | 2346 (pomiar), klon ok. 70 ms | jeden, stoi |

**Przy jednym graczu:** 36 potworów na serwerze (36 Configuration po 9 atrybutów), u klienta najwyżej 12 widoków i 4000
brył (np. 12 slime’ów = 1380 brył; w Ostępach 7 wilków = 3808 — budżet tnie resztę). Do tego las: 22 366 części.
Sieć: kilka KB/s. Serwer: ok. 25 grup na tyknięcie, pomijalnie.

**Co ciąć najpierw (w tej kolejności):** (1) `BUDZET_CZESCI` 4000 → 1500; (2) `MAKS_WIDOKOW` 12 → 8 i
`PROMIEN_WIDOKU` 120 → 80; (3) klipy tylko w promieniu 50 (dalej poza spoczynku); (4) bryła zastępcza dla widoków
dalej niż 60 (mechanizm już jest — tryb zastępczy); (5) `OKRES_RUCHU` 0,25 → 0,5 (połowa ruchu sieci).

**Ryzyka:**

- **Prototyp się zmienia** (inny agent kończy prace w `swiat/test_walki2/`). Punkty styku, które ten pakiet zakłada i
  które Studio musi sprawdzić ponownie: `Odtwarzacz.uruchom(kontener, wybor, opcje)`, `czyTrwa()`, `wolnaZa()`;
  ścieżka `kontener.Zdalne.RozpocznijWalke2` i pola `{klasa, przeciwnik, poziom}` w `Sesja:poprosSerwer`; lista
  `POWODY_CICHE`; lokalne atrybuty `OstatniWynik`/`OstatniStan` na podanym kontenerze; `Klipy.nowy(model, dane,
  {reczny = true})`, `:graj`, `:krok`, `:zastosuj`, `:zniszcz`; pola `TabelaAktorow.aktorzy[k].hrp`, `.pasek`,
  `.klipy`, `.liczbaCzesci`; atrybut `Skora` na bryłach galarety; `Wzorcowe.postac`, `Wzorcowe.KLASY`.
- **Streaming:** zakładamy, że `Configuration` w Workspace i ModuleScripty TestWalki2 są u klienta zawsze (nie są
  bryłami). Gdyby nie — przenieść `Stan` do `ReplicatedStorage/LasPotworyStan` (zmiana jednej ścieżki po obu stronach).
- **Cięcie do areny** przerywa wrażenie „walki w lesie” (wariant a później). Bez P1 scena bez podestu.
- **„Pociąg”:** po wielu walkach grupy w strefie mogą zbić się w kolejkę co 25 st (odstęp tylko zatrzymuje, nie
  rozluźnia). W etapie A akceptujemy; w B łagodne rozluźnianie prędkością.
- **Wilki na małych pętlach** (z11: okrążenie 10,6 s, z15: 12,3 s przy 10 st/s) mogą wyglądać nerwowo — pytanie 5.
- **Blokada sesji ×1:** po wygranej z pominięciem gracz czeka pełny czas walki (tak działa prototyp i D-068).
- **Bursztynowy Slime w walce jest zielony.**
- **Lokalne ProximityPrompt** działają u klienta (zdarzenia tylko lokalnie) — sprawdzić w 9.2 p. 5 i 14.
- **Kopie szablonów w ReplicatedStorage** (ok. 4200 instancji) idą do każdego klienta przy dołączeniu (raz).

---

## 11. Pytania do ludzi (Karol, Paweł)

1. **Reguła testowa T1** (klasa i poziom z panelu, „auto” = poziom potwora): zostawić na testy? Docelowo: postać gracza
   z poziomem i ekwipunkiem — kiedy powstanie zapis postaci?
2. **Strażnik:** wspólny z powrotem po 120 s (etap A) czy osobny dla gracza (domyślnie w planie, wybór nr 1)? Warunek
   10 wygranych z potworami ≥ (poziom − 2) — włączyć dopiero z zapisem postępu?
3. **Gdzie walka:** zgoda na cięcie do areny prototypu na czas testów? Czy robić wariant „na miejscu” (rozdz. 6) w
   etapie B?
4. **Poprawka P1** w odtwarzaczu (wykluczenie areny prototypu z chowania) — zgoda opiekuna `swiat/test_walki2/`?
   P2 (bez JESZCZE RAZ w lesie)?
5. **Prędkość wilków** 10 st/s na pętlach 106–123 st (z11, z15) — zostawić, zmniejszyć w tych strefach, czy powiększyć
   pętle w `potwory.json`?
6. **Etap B:** kolejność — zachowania stref, patrole p1–p4, Troll, kolory odmian w walce?
7. **Bursztynowy Slime w walce zielony** — zamówić odmianę koloru w odtwarzaczu (zmiana prototypu)?
8. **Skalowanie na serwer** (wszyscy gracze, także w mieście), a nie na graczy w lesie — tak jak pisze `potwory.json`?
9. **Odrodzenie po wygranej liczy się od końca pełnego czasu walki** (potwór zajęty przez czas ×1) — w porządku?

---

## 12. Instrukcje dla dwóch programistów

**Wspólne:** piszecie **tylko** w `swiat/las_potwory/`. Wszystko inne w repozytorium tylko czytacie (szczególnie
`swiat/test_walki2/`, `swiat/biom_las/`, `src/`, `tools/`). Bez Studio, bez narzędzi Studio, bez gita zmieniającego
stan. Styl jak `swiat/test_walki2/zrodla/`: nagłówek `--[[ … ]]` po polsku, strażnik Studio, adnotacje typów Luau,
`task.*` zamiast `wait/spawn/delay`. Pliki tymczasowe — poza repozytorium. Gdy coś w kontrakcie jest niejasne, wybierz
najprostsze odczytanie, zapisz je w komentarzu na górze pliku i w opisie zmiany.

**Programista S (serwer), ok. 45 min, w tej kolejności:**

1. `logika.py` — funkcje z tabeli 3.7 (15 funkcji, ok. 130 linii), bez zależności.
2. `testy/test_logiki.py` — przypadki 3.7a; gdy przechodzą, masz pewność co do wzorów.
3. `generuj_dane.py` — format 2.4, kontrole 2.1, z09 przez korytarz, Strażnik w (0; 32; −373) lasu; uruchom, zapisz
   `zrodla/DanePotworow.luau`; dopisz testy 9.1 p. 2–7.
4. `zrodla/Logika.luau` — te same funkcje i `sprawdzPrzypadki()` z tabelą 3.7a.
5. `zrodla/SerwerPotworow.server.luau` — kolejność: strażnik Studio i usunięcie poza Studio; kontrola BiomLas (1.3);
   kopie szablonów (4.3); rejestr stref i potworów; start (3.4); pętla ruchu 4 Hz (3.2–3.3); odradzanie 1 Hz (3.5);
   `OnServerInvoke` (5.1); koniec zajętości i `PlayerRemoving` (3.6); haczyk (8.6); atrybuty (3.8).
   Gotowe = testy przechodzą, `sprawdz_luau.py` (od K) nie zgłasza błędów w twoich plikach.

**Programista K (klient), ok. 45 min, w tej kolejności:**

1. `zrodla/Stale.luau` — przepisz 8.4.
2. `sprawdz_luau.py` — reguły 8.8 z `--test`; od razu sprawdzaj nim swoje pliki.
3. `zrodla/KlientPotworow.client.luau` — kolejność: strażnik; czekanie na `SerwerGotowy` i `SzablonyGotowe` (15 s) i
   wybór trybu (4.3); wybór widoków 0,5 s (4.1); budowa/niszczenie (4.3); klatka: wygładzanie, grunt, obrót, klipy
   (4.2); tabliczka i miecze (4.4); podpowiedź 0,1 s (4.5); panel bohatera, start i koniec walki, baner (4.6);
   haczyk (8.6); atrybuty lokalne `Klient*`.
4. `zbuduj.py` — wg 8.7, na podstawie `swiat/test_walki2/zbuduj.py`; sprawdź **tylko** `--sucho`.
   Gotowe = `zbuduj.py --sucho` przechodzi (gdy S dostarczy dane) i `sprawdz_luau.py` czysto.

**Osoba wdrażająca (później):** `zbuduj.py --sucho` → (opcjonalnie P1 u opiekuna prototypu) → `zbuduj.py` → lista 9.2
→ wyniki w 9.3 → filmy. Przed publikacją miejsca: `zbuduj.py --usun` (i tak usuwa się sam poza Studio).

---

## 13. Recenzja (15.11.2026, offline, bez Studio)

**Werdykt.** Obie połówki są zgodne z kontraktem i ze sobą: nazwy, ścieżki, ładunek zdalnej funkcji, atrybuty i
kolejność gotowości pasują do planu `zbuduj.py` i do bieżących plików prototypu. Zasady ruchu z `potwory.json`
(„zasady”) i z rozdz. 6 planu lasu są zaimplementowane tak, jak je odczytał kontrakt; przeliczenie las → świat robi
tylko generator, raz. Serwer sam sprawdza każdą prośbę (D-016) i niczego od klienta nie bierze poza
identyfikatorem potwora i dwoma napisami z list. Recenzja znalazła i poprawiła jedną usterkę zachowania (Strażnik
mógł nie wracać), jedną usterkę startu klienta (brak dymka przy złym lesie), dwie słabości odporności i lukę w lustrze
testów (odradzanie w Pythonie nie było kopią serwera). Kodu Luau nikt jeszcze nie uruchomił, więc pierwsze
uruchomienie w Studio może pokazać błędy czasu wykonania, których czytanie nie wyłapie; pętle mają `xpcall`,
a haczyki i atrybuty pozwalają szybko je namierzyć.

**Co sprawdziłem.** Przeczytałem każdy plik pakietu linia po linii. Porównałem każdą ścieżkę `WaitForChild` /
`FindFirstChild` z wyjściem `zbuduj.py --sucho` i z `swiat/test_walki2/zbuduj.py`. Porównałem API odtwarzacza,
`Klipy`, `Aktorzy.nowy`, `TabelaAktorow`, `budowa/szablon.luau`, `Wzorcowe`, `SerwerWalki2`, `KlientWalki2`,
`InterfejsWalki2` i `Silnik` z tym, czego używają nasze skrypty — na plikach z 15.11 po południu, razem z
nieskomitowanymi zmianami drugiego agenta (nie ruszają punktów styku). Sprawdziłem bilans bloków, zmienne, przypadki
nil, nazwy i kolejność argumentów API, miejsca z `yield`, połączenia, pętle bez końca i miejsca, które zakładają
postać. Sprawdziłem wzór przeliczenia z `generuj.py` lasu (`do_swiata`) i `znaczniki.json`. Przejrzałem zasady
zaufania: odstęp próśb, rejestr żywych, postać żyje, sesja gracza, zajętość, odległość i wysokość liczone z położenia
serwera, poziom bohatera z listy, brak `yield` między kontrolą a zajęciem potwora (dwie prośby naraz nie dadzą dwóch
walk). Uruchomiłem wszystkie testy, `sprawdz_luau.py` (także `--test`) i `zbuduj.py --sucho`; generator dał trzy
razy te same bajty co plik w repozytorium.

**Poprawki recenzji.**

| Plik | Co |
|---|---|
| `zrodla/SerwerPotworow.server.luau` | Strażnik bez blokady domu (blokada 0): wraca dokładnie po 120 s; wcześniej przy zwycięzcy w promieniu 18 nie wracał, a lista 9.2 p. 10 (postać 13 studów od niego) nie mogła przejść. `StraznikWraca` jest teraz zawsze prawdziwy. |
| `zrodla/SerwerPotworow.server.luau` | Gdy pętla stanie po 10 błędach, serwer przestaje przyjmować walki (`gotowy = false`); wcześniej przyjmowałby je dalej, a zajętość nigdy by się nie skończyła. |
| `zrodla/KlientPotworow.client.luau` | Czekanie na serwer 40 s zamiast 15 s: serwer potrzebuje do 15 s na BiomLas i do 20 s na TestWalki2, więc przy brakującym lesie klient nie widział `StanBiomu` i zamiast dymka cicho przechodził w tryb zastępczy. W zwykłym przypadku nic się nie zmienia (ok. 1 s). |
| `zrodla/KlientPotworow.client.luau` | Widok jest rejestrowany przed budową tabliczki, a tabliczka i miecze są sprawdzane przed użyciem; wcześniej błąd w tabliczce zostawiłby model poza rejestrem, a pętla budowy klonowałaby go co 0,1 s od nowa. |
| `zrodla/KlientPotworow.client.luau` | Własne ScreenGui (`LasPotworyBohater`, `LasPotworyBaner`) mają atrybut `Wygenerowane = true`, jak reszta pakietu. |
| `testy/test_logiki.py` | `Symulacja.odradzaj` jest teraz kopią `odradzaj()` serwera (karuzela domów, blokada 18, gracze w strefie, cel z liczby graczy, wyjątek Strażnika) zamiast losowego domu; nowa klasa `TestBrzegi` (7 testów, rozdz. 9.1 p. 8). |
| `testy/test_styku.py` | Nowy: 15 testów punktów styku (rozdz. 9.1). |
| `PROJEKT.md`, `README.md`, `UWAGI_S.md`, `UWAGI_K.md` | Status, odczytania (Strażnik, `yaw`, `minal`, 40 s), dokładna łata P1/P2, testy, lista Studio z poleceniami, ta recenzja. |

**Słabe miejsca i niepewności, od największego ryzyka.**

1. **Luau nigdy nie było uruchomione.** Kontrola statyczna łapie bilans bloków, nawiasy, strażnika i zakazane nazwy,
   ale nie łapie literówki w nazwie pola tabeli ani złego typu. Pierwszy Play może skończyć się błędem w Output.
   Każdy taki błąd ma prefiks `[LasPotwory]` i traceback; serwer i klient działają dalej.
2. **Streaming.** Gdy miejsce ma `StreamingEnabled`: (a) zakładamy, że `Configuration` w folderze w Workspace i
   ModuleScripty prototypu są u klienta zawsze (nie są bryłami); (b) arena i galeria szablonów prototypu są ponad 2000
   studów od lasu — serwer woła `RequestStreamAroundAsync` z limitem 3 s, a odtwarzacz klonuje szablony z galerii
   (`Aktorzy.szablon`, `WaitForChild` 5 s). Jeśli arena nie zdąży dojść, walka skończy się stanem „blad” i `warn`
   prototypu. Wyjście awaryjne: przenieść `Stan` do `ReplicatedStorage/LasPotworyStan` (jedna ścieżka po obu stronach)
   albo podnieść limit `RequestStreamAroundAsync`.
3. **Bez P1 scena walki stoi na płycie Baseplate**, a podest areny jest schowany. Walka, łup i wynik działają.
4. **Lokalna `ProximityPrompt`** na lokalnej części ma działać z E i stuknięciem na telefonie; nie sprawdzone.
5. **Wspólny egzemplarz odtwarzacza.** Zakładamy, że `require` tego samego ModuleScriptu z naszego skryptu klienta
   (`RunContext = Client`) i z `KlientWalki2` daje ten sam egzemplarz modułu. Gdyby nie, dwie walki naraz (las i
   tablica) byłyby możliwe u jednego klienta; serwery i tak mają osobne blokady sesji.
6. **Wydajność na telefonie:** wilk ma 544 bryły na Motor6D przesuwane co klatkę; budżet 4000 brył. Kolejność cięć
   w rozdz. 10.
7. **JESZCZE RAZ po wygranej** daje dymek „Serwer nie przyjął tego wyboru…” (poprawka P2).
8. **Wygląd:** Bursztynowy Slime w walce jest zielony; wataha z09 składa się przy zawracaniu; odcinki dom → przedpole
   w z09 mogą iść przez jeżyny (bez kolizji); dwa `UIStroke` na przycisku GOTOWE i obrócone ramki mieczy — tylko wygląd.
9. **„Pociąg”:** po wielu walkach grupy zbijają się w kolejki co 25 st (odstęp tylko zatrzymuje).
10. **Uwagi do danych lasu** (zmiany poza tym pakietem, dla opiekuna `swiat/biom_las/`): z04 ma
    `liczba_wezlow = 7`, a węzłów 6; `generuj.py` rysuje z09 prostymi odcinkami, a my prowadzimy trasę korytarzem;
    `straznik.miejsce` to oś filara, więc Strażnik stoi 12 studów na południe. Żadna z tych rzeczy nie blokuje wdrożenia.

**Decyzje recenzji (najprostsze odczytania, do zatwierdzenia przez ludzi).** Strażnik nie podlega blokadzie domu
(nie ma domu w `potwory.json`). `yaw = atan2(0 − dx, 0 − dz)` i `minal` z `≤ 0,5` — tak, jak wymaga tabela 3.7a.
Klient czeka na serwer do 40 s.

## Dodatek A. Strefy — liczby oczekiwane (z generatora; pętla w świecie, prędkości z `potwory.json`)

| Strefa | Potwór | Poz. | naraz / max | L (st) | Trasa | Grupy × miejsca | Zapas pojemności | Okrążenie | Cel G = 1 / 4 / 8 / 20 | Odrodzenie (1 / 4 / 8 graczy w strefie) |
|---|---|---|---|---|---|---|---|---|---|---|
| z01 | Leśny Slime | 1–2 | 6 / 9 | 267,2 | pętla | 9 × 1 | 42,2 | 44,5 s | 3 / 4 / 6 / 9 | 15 / 10,3 / 10 s |
| z02 | Leśny Slime | 1–3 | 5 / 7 | 177,3 | pętla | 7 × 1 | 2,3 | 29,5 s | 3 / 4 / 5 / 7 | 15 / 10,3 / 10 s |
| z16 | Leśny Slime | 1–2 | 4 / 5 | 144,7 | pętla | 5 × 1 | 19,7 | 24,1 s | 2 / 3 / 4 / 5 | 15 / 10,3 / 10 s |
| z03 | Leśny Slime | 2–3 | 4 / 5 | 144,7 | pętla | 5 × 1 | 19,7 | 24,1 s | 2 / 3 / 4 / 5 | 15 / 10,3 / 10 s |
| z04 | Muchomornik | 3–4 | 6 / 8 | 234,1 | pętla | 8 × 1 | 34,1 | 46,8 s | 3 / 4 / 6 / 8 | 20 / 13,8 / 10 s |
| z05 | Muchomornik | 4–5 | 4 / 5 | 192,7 | pętla | 5 × 1 | 67,7 | 38,5 s | 2 / 3 / 4 / 5 | 20 / 13,8 / 10 s |
| z06 | Leśny Slime | 3–4 | 4 / 5 | 144,7 | pętla | 5 × 1 | 19,7 | 24,1 s | 2 / 3 / 4 / 5 | 15 / 10,3 / 10 s |
| z07 | Cierniowy Wilk | 5 | 3 / 4 | 192,7 | pętla | 1 × 4 | 129,6 | 19,3 s | 2 / 2 / 3 / 4 | 25 / 17,2 / 12,2 s |
| z08 | Cierniowy Wilk | 5–6 | 6 / 9 | 187,1 | pętla | 2 × 5 | 35,5 | 18,7 s | 3 / 4 / 6 / 9 | 25 / 17,2 / 12,2 s |
| z09 | Cierniowy Wilk | 6–7 | 3 / 4 | 475,1 | tam i z powrotem (korytarz) | 1 × 4 | 412,0 | 47,5 s | 2 / 2 / 3 / 4 | 25 / 17,2 / 12,2 s |
| z10 | Cierniowy Wilk | 7 | 2 / 3 | 168,7 | pętla | 3 × 1 | 93,7 | 16,9 s | 1 / 1 / 2 / 3 | 25 / 17,2 / 12,2 s |
| z11 | Cierniowy Wilk | 7–8 | 3 / 4 | 106,4 | pętla | 1 × 4 | 43,3 | 10,6 s | 2 / 2 / 3 / 4 | 25 / 17,2 / 12,2 s |
| z12 | Bursztynowy Slime | 6–7 | 4 / 5 | 128,4 | pętla | 5 × 1 | 3,4 | 21,4 s | 2 / 3 / 4 / 5 | 15 / 10,3 / 10 s |
| z13 | Cierniowy Wilk | 8 | 3 / 4 | 154,2 | pętla (y 12) | 1 × 4 | 91,1 | 15,4 s | 2 / 2 / 3 / 4 | 25 / 17,2 / 12,2 s |
| z14 | Muchomornik | 8–9 | 4 / 5 | 154,2 | pętla (y 12) | 5 × 1 | 29,2 | 30,8 s | 2 / 3 / 4 / 5 | 20 / 13,8 / 10 s |
| z15 | Cierniowy Wilk | 9–10 | 3 / 4 | 123,5 | pętla (y 22) | 1 × 4 | 60,4 | 12,3 s | 2 / 2 / 3 / 4 | 25 / 17,2 / 12,2 s |
| straznik | Strażnik Gaju | 10 | 1 / 1 | 0 | stoi (y 32) | 1 × 1 | — | — | 1 / 1 / 1 / 1 | 120 s (stałe) |
| **Razem** | | | 64 / 86 | | | | | | **35 / 45 / 64 / 86** + Strażnik | |

„Zapas pojemności” = `L − grupy × ((miejsc − 1) × odstepWGrupie + 25)`. Kolumna G = 4 sumuje się do 45.

## Dodatek B. Co sprawdziłem w kodzie przy pisaniu kontraktu

- `swiat/biom_las/PROJEKT.md` rozdz. 2 (położenie i obrót BiomLas), 6 (zasady, tabela stref, Troll, Strażnik), 7
  (systemy); `potwory.json` (zasady, rozmiary, prędkości, 16 stref, troll, strażnik, patrole); `znaczniki.json`
  (kontener i wzór, węzły i domy z wysokością — identyczne z `potwory.json`, strefy spokoju, straznik); `uklad.json`
  (wielokąt Serca, `korytarz_labiryntu`); `wezly.py` (`jednostki`, odsunięcie węzłów od stref spokoju o 10, z09
  ręcznie); `generuj.py` linia ~90 (z09 trasą otwartą); `lokacje/korona.py` `kamienny_krag` (filar w osi Kręgu);
  `czesci.json` (Płyta: (0; −1; −2000), 1400 × 2 × 1400, obrót Y = π).
- `swiat/test_walki2/zrodla/SerwerWalki2.server.luau` (kolejność kontroli, blokada sesji `walka.czas − 0,4`, ziarno,
  `RequestStreamAroundAsync`, usuwanie poza Studio), `Wzorcowe.luau` (`postac`, `KLASY`, tarcza Wojownika),
  `Ustawienia.luau` (`SRODEK`, `scena()`, `OBSZAR_*`), `KlientWalki2.client.luau` (`naOdmowe`, nazwa podpowiedzi),
  `Aktorzy.luau` (`nowy`, `szablon()` z kontenera modułu, `ustaw`, `punkt("Pasek")`), `Klipy.luau` (API `reczny`,
  `krok`, `zastosuj`), `OdtwarzaczWalki2.luau` (`uruchom`, `poprosSerwer`, `POWODY_CICHE`, `schowajObcych`,
  `przygotujScene`, `ustawAktorow` z `cfSceny = U.scena()`, `pokazWynik` → `OstatniWynik`, `jeszczeRaz`, `zakoncz`,
  `ukryjInneGui`, `pilnujPrzerwania`), `InterfejsWalki2.luau` (`pokazWynik`, przycisk JESZCZE RAZ),
  `budowa/szablon.luau` (atrybut `Skora`), `zbuduj.py` (tryby, bezpieczeństwo, `TabelaAktorow`: `hrp`, `pasek`,
  `liczbaCzesci`), `README.md` (pomiary instancji, pułapki), `dane/*.json` (liczby brył i kości).
- `src/server/Walka/Silnik.luau` (`symuluj(gracz, {potwor, poziom}, ziarno)`, pola wyniku), `Przeciwnicy.luau`,
  `tools/walka/dane_walki.json` (5 przeciwników lasu), `tools/walka/generuj_dane.py` (wzór generatora),
  `B&C/Produkcja/Rejestr decyzji.md` (D-016, D-068, D-069, D-071).
- Policzone kopią lustra poza repozytorium: przypadki 3.7a, dodatek A, symulacje odstępu i wejścia na pętlę
  (najmniejsza luka 25,000 we wszystkich strefach; reguła bez rezerwacji dawała luki 0,0–2,1 — odrzucona).
