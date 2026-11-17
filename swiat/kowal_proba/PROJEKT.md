---
status: propozycja
---
# Kowal na próbę — przedmioty z liczbami, łup, rozbiórka i ulepszanie (D-102, D-051)

**Status: propozycja (prototyp w Studio), nie kanon.** Zlecenie z sesji głównej 17.11 (temat 5, D-102: „Dajemy Kowala…
proszę o pracę i logikę Kowala”). Wszystkie liczby i zasady z listy „Przyjęte, do zmiany” czekają na Karola i Pawła.
Działa tylko w Studio (strażnik `RunService:IsStudio()`; poza Studio serwer usuwa kontener). Przed publikacją miejsca:
`python -B swiat/kowal_proba/zbuduj.py --usun`.

## Zasady w pięciu zdaniach
1. Każdy z 18 całych przedmiotów bohaterów z katalogu (`swiat/postacie/przedmioty.json`; nogawice i spodnie to części
   zbroi, więc razem 20) ma statystyki i poziom ulepszenia +0…+5, a do walki liczą się przedmioty **założone**
   w przymierzalni (`swiat/stroje_proba`) — przez `StanGracza/Sygnaly/Modyfikatory`, źródło „kowal”.
2. Gracz zaczyna z **podstawowym zestawem** klasy (broń i zbroja, Wojownik także tarcza), który liczy się dokładnie jak
   dzisiejszy wzór poziomu, a resztę przedmiotów dostaje **z łupu walk** (zwykły potwór 10%, rzadki 30%, strażnik 50%;
   najpóźniej co 10. wygrana daje przedmiot na pewno).
3. Przedmiot, który gracz już ma, wypada jako **zapas** — u kowala rozbiera się go na **3 materiały**; własnego
   przedmiotu nie da się rozebrać ani stracić.
4. **Ulepszenie** kosztuje Złoto (przez `WydajZloto`, nigdy poniżej zera) i materiały, rośnie z poziomem i dodaje stały
   przyrost do statystyk przedmiotu; decyduje wyłącznie serwer (klient wysyła tylko akcję i id).
5. Kuźnia z kowalem stoi w bazarze naprzeciw zbrojowni; **E przy kowalu** otwiera tymczasowe okno „KUŹNIA · PRÓBA”
   z listą przedmiotów klasy, statystykami, kosztem i przyciskami „Ulepsz” i „Rozbierz zapas”.

## Jak to działa
- **Dane gracza** (`StanGracza/Sygnaly/DanePakietu`, pakiet „kowal”): `{ przedmioty = { [id] = { poziom, zapas } },
  materialy, bezLupu, klasy }` — w profilu właściciela stanu, więc przyszły zapis obejmie je razem ze Złotem. Serwer
  kowala trzyma tylko kopię roboczą i podmienia ją po udanym zapisie.
- **Wpływ na walkę:** `Modyfikatory("ustaw", gracz, "kowal", mod)` z sumy założonych przedmiotów: `bron`, `pancerz`
  (dodatki do wzoru poziomu), `tarcza` (ułamek bloku) i `statystyki` (Siła, Kondycja…). Wpis odnawia się po każdej
  zmianie przedmiotów, stroju, klasy i po przebudowie `StanGracza` (kontrola co 2 s).
- **Łup:** serwer kowala słucha atrybutów gracza `TokenyKrainy_<kraina>` (pisze je StanGracza przy pokazaniu łupu).
  Przyrost 1–2 = wygrana ze zwykłym potworem, 3–4 = z rzadkim, 5–6 = ze strażnikiem (`tools/walka/silnik.py`);
  inny przyrost (wczytanie, kilka walk naraz) — bez losowania. Nowy przedmiot od razu zakładamy w przymierzalni, gracz
  widzi napis „Nowy przedmiot: …! Założony.” albo „Zapasowy przedmiot: … — rozbierz go u kowala w bazarze.”.
- **Przymierzalnia:** przy działającym kowalu (kontener `KowalProba` i atrybut gracza `KowalDostepne`) pokazuje
  i zakłada tylko posiadane przedmioty, a „Dawny wygląd” znika. Bez kowala — wszystko jak dawniej.
- **Bez `StanGracza`:** okno odpowiada „Kuźnia nieczynna — brak stanu gracza (próba).”, atrybutów kowala nie ma,
  przymierzalnia działa jak dawniej; żadnych błędów.

## Przedmioty — statystyki (+0 i przyrost za poziom ulepszenia)

| Klasa | Przedmiot | Slot | Skąd | +0 | Za poziom | +5 (najwyższy) |
|---|---|---|---|---|---|---|
| Wojownik | Wielki miecz Rycerza | Broń | start | — (broń ze wzoru) | Broń +1 | Broń +5 |
| Wojownik | Tarcza Rycerza | Druga ręka | start | blok 28% (wzór) | Blok +1% | Blok +5% |
| Wojownik | Zbroja Rycerza z tabardem (+ nogawice) | Zbroja | start | — (pancerz ze wzoru) | Pancerz +3 | Pancerz +15 |
| Wojownik | Hełm Rycerza | Hełm | łup | Pancerz +2 · Kondycja +1 | Kondycja +1 | Pancerz +2 · Kondycja +6 |
| Wojownik | Rękawice Rycerza | Rękawice | łup | Siła +2 | Siła +1 | Siła +7 |
| Wojownik | Trzewiki z nagolennikami | Buty | łup | Zręczność +2 | Zręczność +1 | Zręczność +7 |
| Wojownik | Pas Rycerza | Pas | łup | Kondycja +1 | Kondycja +1 | Kondycja +6 |
| Zwiadowca | Sztylet Zwiadowcy | Broń | start | — | Broń +1 | Broń +5 |
| Zwiadowca | Skórzany kirys z tuniką (+ spodnie) | Zbroja | start | — | Pancerz +3 | Pancerz +15 |
| Zwiadowca | Łuk z kołczanem | Druga ręka | łup | Szczęście +2 | Broń +1 | Broń +5 · Szczęście +2 |
| Zwiadowca | Kaptur z peleryną | Hełm | łup | Pancerz +2 · Zręczność +1 | Szczęście +1 | Pancerz +2 · Zręczność +1 · Szczęście +5 |
| Zwiadowca | Rękawice bez palców | Rękawice | łup | Siła +1 | Siła +1 | Siła +6 |
| Zwiadowca | Buty z wywiniętą cholewą | Buty | łup | Zręczność +2 | Zręczność +1 | Zręczność +7 |
| Zwiadowca | Pas z sakwą | Pas | łup | Kondycja +1 | Kondycja +1 | Kondycja +6 |
| Mag | Kostur Kota-Maga | Broń | start | — | Broń +1 · Inteligencja +1 | Broń +5 · Inteligencja +5 |
| Mag | Szata Kota-Maga | Zbroja | start | — | Pancerz +3 · Kondycja +1 | Pancerz +15 · Kondycja +5 |
| Mag | Kapelusz Kota-Maga | Hełm | łup | Kondycja +2 · Inteligencja +2 | Kondycja +1 · Inteligencja +1 | Kondycja +7 · Inteligencja +7 |
| Mag | Szarfa z klamrą | Pas | łup | Siła +1 · Kondycja +2 | Siła +1 · Kondycja +1 | Siła +6 · Kondycja +7 |

Mag ma w katalogu 4 przedmioty, pozostałe klasy po 7, dlatego przedmioty Maga mają **wagę 1,75**: większe przyrosty
i koszty ×1,75 — cały zestaw każdej klasy do +5 kosztuje tyle samo (ok. 17 150 Złota i 112–116 materiałów).

## Siła bohatera — podstawowy zestaw = dziś
Kalkulator `balans_kowala.py` (silnik `tools/walka/silnik.py`, bohater i modyfikatory z prawdziwej logiki
`swiat/stan_gracza`). Szansa wygranej, średnio po 10 przegrodach lasu-pasa i Bagna (bohater na najniższym poziomie
przegrody), 500 walk na komórkę:

| Wariant | Wojownik | Zwiadowca | Mag | różnica klas |
|---|---:|---:|---:|---:|
| dziś (wzór poziomu) | 52% | 53% | 53% | 0,8 pp |
| **podstawowy zestaw +0** | **52%** | **53%** | **53%** | 0,8 pp — co do pola ten sam opis bohatera (test na poziomach 1–30) |
| pełny zestaw +0 (wszystko z łupu) | 59% | 59% | 60% | 1,0 pp |
| pełny +2 | 71% | 71% | 73% | 2,4 pp |
| pełny +5 (najwyższy) | 84% | 83% | 87% | 3,9 pp |
| Wojownik w podstawowym bez tarczy | 33% | — | — | (blok tarczy ze wzoru należy do tarczy) |

Bohater na 10. poziomie (broń / pancerz z przedmiotów): dziś 48 / 18, pełny +0 — 48 / 20, pełny +5 — 53 / 35
(Wojownik też blok 28% → 33%).

## Gracz w lesie i w Bagnie (łup przedmiotów, zapas od razu rozebrany, wizyta u kowala najwyżej co 5 min)

| Wariant (60 graczy na klasę) | Las: do Strażnika | Bagno: do Strażnika | Przegrane las / Bagno | Przedmioty z łupu (nowe) las / Bagno | Ulepszeń las / Bagno | 1. ulepszenie |
|---|---|---|---|---|---|---|
| bez kowala (dziś) | 26,9 min | 48,1 min | 8 / 18 | — | — | — |
| całe Złoto na kowala | 27,4 min | 41,8 min | 7 / 10 | 6 (2) / 7 (1) | 5 / 7 | po 8,3 min lasu |
| połowa Złota na kowala (reszta na jajka) | 26,5 min | 43,8 min | 6 / 10 | 6 (2) / 7 (1) | 5 / 8 | po 9,3 min lasu |

**Las się nie rozjeżdża** (pierwsze ulepszenia przychodzą w drugiej połowie lasu, wizyty kosztują czas), Bagno skraca
się o ok. 13% i przegranych jest mniej (18 → 10). Klasy w Bagnie z kowalem: Wojownik 44,2 min, Zwiadowca 42,4, Mag 37,1
(bez kowala 53,6 / 46,9 / 42,6 — kolejność jak dziś).

## Ulepszenia: koszt, przyrost, ile walk na jedno ulepszenie

| Poziom | Złoto (Mag) | Materiały (Mag) | Przyrost miecza / sztyletu | Walk w lesie (za Złoto / za materiały) | Walk w Bagnie | Razem Złota / materiałów |
|---|---:|---:|---|---|---|---|
| +1 | 150 (265) | 1 (2) | Broń +1 | 2,0 / 3,8 → **3,8** | 1,1 / 2,9 → **2,9** | 150 / 1 |
| +2 | 300 (525) | 2 (4) | Broń +1 | 4,0 / 7,6 → **7,6** | 2,2 / 5,9 → **5,9** | 450 / 3 |
| +3 | 450 (790) | 3 (5) | Broń +1 | 6,0 / 11,4 → **11,4** | 3,3 / 8,8 → **8,8** | 900 / 6 |
| +4 | 650 (1140) | 4 (7) | Broń +1 | 8,6 / 15,2 → **15,2** | 4,8 / 11,7 → **11,7** | 1550 / 10 |
| +5 | 900 (1575) | 6 (11) | Broń +1 | 11,9 / 22,8 → **22,8** | 6,7 / 17,6 → **17,6** | 2450 / 16 |

Średnio na walkę: las 76 Złota i 0,26 materiału, Bagno 135 Złota i 0,34 materiału. Przy całym Złocie na kowala
hamują materiały; przy połowie Złota (reszta na jajka 300 / 750) Złoto i materiały hamują podobnie — Złoto naprawdę
idzie na przedmioty (D-097).

## Skąd przedmioty i materiały
- **Wdrożone: łup z walk** (D-050: potwory dają przedmioty). Najprostsze, bo nie zmienia pakietów lasu: wygraną
  rozpoznajemy po tokenach krainy. Duplikaty zasilają rozbiórkę (D-051: „rozbiera zbędne przedmioty na materiały”).
- **Opisane: sklep zbrojmistrza za Złoto** (D-097: „Złoto tylko na przedmioty”). E zbrojmistrza w bazarze wysyła już
  zdarzenie okien bazaru (`ReplicatedStorage.OknoMiejsca`, id `zbrojownia`) — to samo okno kowala w trybie „sklep”
  sprzedawałoby brakujące przedmioty klasy (np. waga × 600 Złota) jednym wywołaniem `WydajZloto` (cel
  `zakup_przedmiotu`, już dopuszczony przez StanGracza). Wtedy łup dawałby głównie zapasy na materiały.
- **Lepszy sygnał łupu (następny krok):** jedna linijka w `nagrodaZaWalke` serwera lasu (`swiat/las_potwory`) —
  wywołanie sygnału kowala z gatunkiem i wynikiem walki — zamiast wnioskowania z tokenów.

## Przyjęte, do zmiany (nie decyzje)
1. **Miejsce:** kuźnia w bazarze naprzeciw zbrojowni (przed prawą częścią Wrót lochów, poza pasem uliczki, punkt E
   ≥ 10 st od punktów E Bramy Leśnej i lochów). D-049 i D-051 mówią: kowal w Twierdzy — przeniesiemy, gdy powstanie.
2. **Podstawowy zestaw liczy się jak dzisiejszy wzór poziomu** (broń 8 + 4 × poziom, pancerz 3 + 1,5 × poziom zostają);
   przedmioty dodają ponad wzór. Alternatywa na później: przedmioty zamiast wzoru (gracz musi ulepszać, żeby nadążyć).
3. **Blok tarczy ze wzoru należy do tarczy:** Wojownik bez założonej tarczy traci blok (D-073: „tarcza daje
   Wojownikowi większą szansę na blok”); okno ostrzega na czerwono.
4. **Łup:** 10% / 30% / 50% (zwykły / rzadki / strażnik), najpóźniej co 10. wygrana — przedmiot na pewno, każdy
   przedmiot klasy z równą szansą; tylko przedmioty własnej klasy.
5. **Jeden egzemplarz + zapas**, rozbiórka tylko zapasu, 3 materiały za sztukę, jeden rodzaj materiału.
6. **Ulepszenia +1…+5**, koszty z tabeli, przyrost stały co poziom, waga Maga 1,75; ulepszać można każdy posiadany
   przedmiot klasy (także zdjęty). Bez tierów (D-051: „nie teraz”) — kolejne biomy będą potrzebowały lepszych
   przedmiotów albo wyższych poziomów.
7. **Nowy przedmiot zakłada się sam**; przy działającym kowalu przymierzalnia nie ma „Dawnego wyglądu”.
8. **Zmiana klasy** daje podstawowy zestaw nowej klasy; przedmioty starej zostają.
9. **Okno tymczasowe** w pasie między kolumnami HUD (jak okno przymierzalni); docelowe okno 2D — pytanie 57.
10. **Bez zapisu** poza profilem StanGracza (zapis to zadanie właściciela stanu); bez DataStore i Robuxów.

## Co zgłosić Pawłowi (okno ekwipunku, moduł `Items`) — jego pliki nie są zmieniane
- `src/shared/Items.luau` nie ma statystyk, poziomu ulepszenia ani slotu `OffHand` (tarcza, łuk). Propozycja: okno
  ekwipunku czyta liczby z `DaneKowala` (przedmiot: `baza`, `krok`, `koszt`) i stan gracza z atrybutów
  `KowalDostepne` (posiadane), `KowalMaterialy`, `KowalZapasy`, a szczegóły z serwera kowala (widok: poziom, zapas,
  statystyki, następne ulepszenie).
- Zakładanie w oknie ekwipunku = to samo co przymierzalnia (`StrojeProba/Zdalne/ZmienStroj`): wtedy strój widać na
  modelu (D-071), a kowal sam przelicza wpływ na walkę.
- Okno kowala (pytanie 57): układ próby — lista przedmiotów klasy z poziomem i zapasem, szczegóły wybranego
  (statystyki, „Ulepszenie: +…”, koszt albo czego brakuje), „Ulepsz”, „Rozbierz zapas”, materiały i Złoto
  w nagłówku, broń / pancerz / blok bohatera w stopce. Zrzuty z części B.
- Plecak 5×5 i zakładka OTHERS mogłyby pokazywać materiały i zapasy.

## Wskazówka celu (pakietu `swiat/wskazowki_gry` nie ruszam)
Proponowany krok „kowal”: gdy `KowalZapasy` > 0 albo gracz ma Złoto i materiały na ulepszenie założonego przedmiotu —
„Masz zapasowy przedmiot — rozbierz go u kowala w bazarze” / „Możesz ulepszyć przedmiot u kowala w bazarze”, znacznik
nad punktem E kowala (`KowalProba/Kuznia/E`), w lesie i Bagnie z dopiskiem „Kamień Powrotu → bazar”. Tylko do
pierwszego ulepszenia (licznik `KowalProba` `LicznikUlepszen` albo poziom > 0 w widoku).

## Kowal i kuźnia (modele, podglądy)
- **Kowal** (`swiat/postacie/kowal.py`, własny projekt): krępy łysy kowal w czerwonej chustce z mosiężnymi goglami,
  czarna broda z warkoczykami, skórzany fartuch, młot w prawej, szczypce z rozżarzoną sztabą w lewej; klipy
  `spoczynek`, `kucie` (zamach i uderzenie dobrane kinematyką rigu — młot trafia w sztabę na kowadle, test 4b),
  `radosc` (po udanym ulepszeniu). Plansza i portret: `swiat/postacie/wynik/kowal/kowal_plansza.jpg`,
  `kowal_bohater.jpg`, `kowal_ikona.png`.
- **Kuźnia** (`kuznia.py` → `kuznia/czesci.json`, 104 części): kamienna podłoga, palenisko z żarem, okapem i kominem,
  miech, kowadło na pniu z rozżarzoną sztabą, kadź z wodą i szczypcami, stojak z mieczami, toporem i tarczą, kupka
  złomu, daszek w kolorach zbrojowni z falbaną i szyld „KUŹNIA / próba”. W Studio dochodzą światło, ogień i iskry.
  Podglądy (Blender, otoczenie z mapy bazaru): `podglad/kuznia_przod.jpg`, `kuznia_34_lewo.jpg`, `kuznia_34_prawo.jpg`,
  `kuznia_z_gory.jpg`, `kuznia_od_zbrojowni.jpg`, `kuznia_w_bazarze.jpg`, `kowal_przy_kowadle.jpg`.

## Zmiany w cudzych pakietach (małe, w osobnych miejscach)
- `swiat/stroje_proba/zrodla/SerwerStrojow.server.luau`: funkcje `dostepne` i `tylkoDostepne` oraz cztery warunki
  w `wykonaj` (nieposiadany przedmiot → „nie_masz”, „dawny” → „dawny_niedostepny”, strój i zestaw tylko z posiadanych).
- `swiat/stroje_proba/zrodla/KlientStrojow.client.luau`: funkcja `ofertaGracza` (oferta tylko z posiadanych) i pole
  `bezDawnego` w `odswiezOkno`.
- `swiat/stroje_proba/zrodla/OknoStrojow.luau`: bez przycisku „Dawny wygląd”, gdy `bezDawnego`.
- Bez `KowalProba` wszystkie trzy działają jak dawniej (testy przymierzalni 22/22, kontrola Luau OK).
- `swiat/stan_gracza` — tylko czytany (dopisanie `KowalProba` do źródeł wydatków zrobił jego agent).
- `swiat/postacie/kowal.py` — nowy moduł (istniejących nie zmieniano).

## Pliki
| Plik | Co to |
|---|---|
| `ustawienia.json` | jedyne źródło liczb i tekstów (przedmioty, koszty, łup, miejsce kuźni, okno) |
| `dane.py` | generator `zrodla/DaneKowala.luau`, `zrodla/RigKowal.luau`, `kuznia/czesci.json`; sprawdza katalog i miejsce w bazarze (`--sprawdz`) |
| `logika_kowala.py` | lustro `zrodla/LogikaKowala.luau` (czysta logika) |
| `kuznia.py` | kuźnia z klocków (biblioteka scen v2, paleta bazaru) |
| `zrodla/SerwerKowala.server.luau`, `KlientKowala.client.luau`, `OknoKowala.luau`, `RigKowala.luau` | serwer, klient, okno, rig z klipami |
| `balans_kowala.py` | kalkulator: siła bohatera, gracz w lesie i Bagnie, ile walk na ulepszenie |
| `podglad.py` | podglądy kuźni w Blenderze → `podglad/` |
| `sprawdz_luau_kowala.py` | kontrola statyczna Luau |
| `zbuduj.py` | budowa w Studio (`--sucho`, `--skrypty`, `--usun`, `--studio`) |
| `testy/test_kowala.py` | 30 testów bez Studio (w tym prawdziwe SerwerKowala + SerwerStanu + SerwerStrojow w `luau_mini`) |
| `testy/proba_play.py` | próba w Play K00–K13 (część B); `--sprawdz` bez Studio |

## Polecenia
```
python -B swiat/kowal_proba/dane.py                    # po zmianie ustawień, katalogu, mapy bazaru albo modelu kowala
python -B swiat/kowal_proba/testy/test_kowala.py       # 30 testów, ok. 20 s
python -B swiat/kowal_proba/zbuduj.py --sucho
python -B swiat/kowal_proba/balans_kowala.py           # tabele (ok. 30 s); --md <plik>
python -B swiat/kowal_proba/podglad.py                 # podglądy kuźni (Blender w tle)
python -B swiat/postacie/przebuduj.py kowal --bez-filmow
# Studio (Edit), po przebudowie StanGracza: kuźnia, skrypty przymierzalni, próba
python -B swiat/kowal_proba/zbuduj.py
python -B swiat/stroje_proba/zbuduj.py --skrypty
python -B swiat/kowal_proba/testy/proba_play.py
python -B swiat/kowal_proba/zbuduj.py --usun           # wyłącznik: gra wraca do stanu sprzed próby
```

## Sprawdzone w Studio (część B, 18.11.2026, 00:35–01:00)
`testy/proba_play.py` (wynik `testy/wynik_play.json`, zrzuty `klatki/`): **13 × OK, 1 × ?, 0 × BŁĄD** (drugi przebieg).

| Punkt | Wynik |
|---|---|
| K00 Edit | OK — kontenery, skrót danych = lokalny, w StanGracza są Modyfikatory, DanePakietu, WydajZloto |
| K01 gotowość | OK — serwer i klient, zgodność logiki „OK 161/161”, podpowiedź E, stan gracza podłączony, kowal animowany |
| K02 start | OK — Wojownik ma miecz, tarczę i zbroję (z nogawicami) w przymierzalni; źródła „kowal” i „szczescie_poczatkujacego”; broń 12 i pancerz 4,5 = wzór 1. poziomu |
| K03 kuźnia | zrzuty `k03_kuznia_przod`, `_lewo`, `_prawo`, `_z_gory`, `_od_zbrojowni`, `k03_kowal_przy_kowadle` (kowal w zamachu, ogień, żarząca się sztaba, szyld) |
| K04 prawdziwe E | OK — okno z 7 przedmiotami klasy (`k04_okno_kowala`) |
| K05 łup | OK — nowy hełm założony sam, napis „Nowy przedmiot: Hełm Rycerza! Założony.”; prawdziwa droga przez przyrost tokenów dała przedmiot (`k05_lup_nowy_przedmiot`) |
| K06 walka | ? — wpis kowala = oczekiwany (hełm: pancerz +2, Kondycja +1; bohater: pancerz 4,5 → 6,5); walka w lesie-pasie nie ruszyła haczykiem „walcz” po przestawieniu gracza (prawdopodobnie las czeka na przybycie przez TELEPORT) — skutek widać w opisie bohatera, nie w walce |
| K07 rozbiórka | OK — prawdziwe kliknięcia: materiały 0 → 3 (`k07_rozbiorka`) |
| K08 ulepszenie | OK — prawdziwe kliknięcia: miecz +0 → +1, Złoto i materiały w dół, broń bohatera 12 → 13, klip radości kowala (`k08a_przed_ulepszeniem`, `k08b_po_ulepszeniu`) |
| K09 odmowy | OK — „Brakuje ci 300 Złota.”, „Brakuje ci 2 materiałów…”, obcy przedmiot, „daleko”; Złoto bez zmian |
| K10 reset postaci | OK — przedmioty, materiały i wpis Modyfikatory zostają, okno działa |
| K11 przymierzalnia | OK — nieposiadane rękawice: „nie_masz”, „Dawny wygląd”: „dawny_niedostepny” |
| K12 mały ekran | OK — 667 × 375, tekst 12 pt, okno 0,42–0,93 wysokości (`k12_okno_maly_ekran`) |
| K13 konsola | OK — bez wierszy kowala |

Regresja: próba przymierzalni `swiat/stroje_proba/testy/proba_play.py --bez-zrzutow` **bez** kontenera `KowalProba`
(czyli jak dawniej) — 10 × OK, 1 × ? (S09, jak dotąd), 0 × BŁĄD; próba dymna `swiat/przejscie_gry/proba_dymna.py`
z kuźnią w miejscu — 14/14 OK (walka w lesie, łup 0 → 30 Złota, bazar, trening, konsola bez błędów).

Poprawione po pierwszym przebiegu: u klienta `FindFirstChild` stawu kości trafiał w bryłę o tej samej nazwie (np.
„RightHand”), więc kowal stał bez ruchu — `RigKowala.uchwyt` szuka teraz stawu po klasie (Motor6D). Dodane zrzuty
przed i po ulepszeniu oraz diagnoza walki w K06.

## Ryzyka i czego nie sprawdzono
- Walka w lesie z przedmiotami nie była oglądana w Studio (K06 — haczyk lasu nie ruszył walki); dwóch graczy naraz,
  telefon i dotyk — nie sprawdzone.
- Łup z tokenów: gdy StanGracza pokaże kilka walk naraz, losowań jest mniej; przyszłe tokeny spoza walk (zadania)
  dawałyby przedmioty — lepszy jest sygnał z serwera lasu (wyżej).
- Złoto wydane, a zapis do profilu odrzucony (StanGracza zniknął w tej samej chwili) — ulepszenie zostaje tylko
  w pamięci serwera kowala.
- Mag ma 4 przedmioty — postęp grubszy (różnica klas przy +5: 3,9 pp); pełna równość po dorobieniu rękawic i butów kota.
- Kuźnia stoi blisko Bramy Leśnej i kryształów Wrót lochów — do oceny na zrzutach z części B.
- Liczby z symulacji, nie z gry ludzi; jajka i premia petów w kalkulatorze tylko jako wariant „połowa Złota”.
