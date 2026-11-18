# Cutscenka przelotu przez biom (D-077) — `swiat/cutscenka_biomu`

> **Status: propozycja wykonania zatwierdzonej decyzji D-077.** Od 18.11.2026 kontener `Workspace/CutscenkaBiomu`
> **stoi w Studio**, a próba w grze jest zielona (wyniki niżej). Miejsce nie było zapisywane ani publikowane.
> Wybory i pytania do ludzi: `PROJEKT.md`.

## Co robi
Przy pierwszym wejściu gracza do biomu (las, Bagno, Dżungla) w danej sesji — przez chmury albo bramą pieszo —
gracz dostaje krótką cutscenkę; przy kolejnych wejściach jej nie ma. Widzi ją tylko ten gracz.

1. **Oprawa:** zasłona, czarne pasy u góry i dołu (po 11% wysokości), plansza z nazwą biomu. HUD, pozostałe
   ekrany, lista graczy, czat i podpowiedzi E znikają na czas cutscenki i wracają po niej. **Pominąć się nie da**
   (wcześniejsze ustalenie właściciela); przycisk **POMIŃ** (dotyk, mysz, Spacja, Enter, B na padzie) jest w kodzie
   i pojawia się dopiero po włączeniu przełącznika `Pomijanie`.
2. **Przelot (8,6 s):** kamera startuje za plecami gracza, mija inkubator, zwalnia nad każdą przegrodą z potworami
   (krótki podpis z nazwą przegrody) i nad leżem rzadkiego potwora, zniża się przez wejście areny.
3. **Strażnik (2,6 s):** zbliżenie z dołu, napis z imieniem strażnika, klip ryku (haczyk klienta potworów), dźwięk
   ryku z katalogu `DzwiekGra` (gdy katalog ma wgrany plik — bez niego cicho), wstrząs kamery, lekki najazd.
4. **Koniec:** zaciemnienie, kamera wraca za plecy postaci (typ `Custom`), sterowanie i ekrany wracają. To samo
   sprzątanie działa po pominięciu, śmierci albo zniknięciu postaci, przerwaniu przez serwer, błędzie i usunięciu
   kontenera.

Postać stoi zakotwiczona przez serwer i ma atrybut `BlokadaWalki` (serwer potworów odmawia wtedy walki). Bohater
z `BohaterSwiat` i pet zostają przy postaci — pakiet ich nie rusza.

## Wyzwalanie i pamięć
- Serwer (`SerwerCutscenki`) co 0,25 s sprawdza, w którym biomie stoi gracz (prostokąt wejścia z pakietu gry biomu,
  ucięty na linii bramy), czy ma prawo wejścia (atrybut wymagania biomu) i czy już widział cutscenkę.
- Kolejność: 0,5 s uspokojenia → pytanie do klienta → klient odmawia, gdy trwa walka, przejście przez chmury,
  mini-gra albo kamerę trzyma inny skrypt (serwer pyta ponownie po 1 s i **niczego nie zapisuje**) → po zgodzie
  kotwica, wczytanie mapy wzdłuż trasy (do 4 s) → start. Gdy klient nie odpowie, serwer sprząta sam.
- **Pamięć „widział”:** tabela serwera według `UserId` (przeżywa odrodzenie i ponowne wejście na ten sam serwer)
  oraz atrybut gracza z pakietu biomu: `WidzialPrzelotLasu`, `WidzialPrzelotBagna`, `WidzialPrzelotDzungli`.
  Zapis postępu w `swiat/stan_gracza` ma już te atrybuty na liście (`atrybuty_prefiksy`), więc po jego włączeniu
  pamięć utrwali się bez zmian w kodzie. **Zapis zostaje wyłączony** — ten pakiet go nie włącza i sam nic nie zapisuje.
- **Odtworzenie ponownie:** w widoku serwera ustaw atrybut kontenera `Odtworz` = `las` / `bagno` / `dzungla`
  (gra wszystkim graczom, atrybut sam się czyści) albo z kodu serwera:
  `workspace.CutscenkaBiomu.Sygnaly.SterowanieCutscenki:Invoke("odtworz", nazwaGracza, "las")`.
  Inne polecenia uchwytu: `"stan"`, `"gracz"`, `"zapomnij"` (cutscenka zagra przy następnym wejściu), `"oznacz"`,
  `"przerwij"`.
- **Przełącznik pomijania:** atrybut kontenera `Pomijanie`, domyślnie `false`; wartość ustawiona w Edit przechodzi
  na odbudowany kontener.

## Trasy (liczone z map, nie wpisane ręcznie)
`dane.py` czyta `krotki/znaczniki.json` i `krotki/czesci.json` każdego biomu oraz moduł danych pakietu gry. Węzły:
start 12 st za plecami gracza → inkubator → wejście każdej przegrody (na zmianę po lewej i prawej, 7 st od osi) →
wejście areny → ujęcie strażnika (węzeł leża stoi 26 st przed środkiem strefy rzadkiego potwora). Wysokość węzła to
najniższa z listy z odstępem 6 st od brył mapy; gdy krzywa wejdzie bliżej niż 5 st od bryły, sąsiednie węzły idą
w górę i trasa liczy się od nowa (po obejrzeniu kadrów 18.11: przy 2,8 st liść olbrzym zasłaniał pół kadru). Prędkość: start z miejsca,
zwolnienie nad każdą przegrodą, hamowanie do zera przed strażnikiem. Klient gra próbki co 0,1 s połączone
jednostajną krzywą Catmull-Rom (ciągła prędkość).

| Biom | Droga | Czas | Prędkość przelotowa / przy przegrodach | Przyspieszenie | Obrót | Odstęp od brył | Wysokość |
|---|---|---|---|---|---|---|---|
| Las | 360 st | 11,2 s | 68 / 27–31 st/s | do 138 st/s² | do 51°/s | 6,27 st (pień Bramy Pniaków) | 7,2–34,0 st |
| Bagno | 349 st | 11,2 s | 67 / 27–30 st/s | do 132 st/s² | do 50°/s | 7,89 st (kładka) | 8,3–15,4 st |
| Dżungla | 352 st | 11,2 s | 67 / 27–30 st/s | do 132 st/s² | do 47°/s | 6,28 st (liść olbrzym) | 8,9–21,0 st |

Przystanki (czas najwolniejszego miejsca): las — Zagroda Slime'ów 1,7 s, Lasek Muchomorowy 3,2 s, Wilcze Zarośla
4,6 s, Leże Trolla 6,2 s; Bagno — Rechotne Oczka 1,7 s, Bulgotne Trzęsawisko 3,2 s, Kłapiące Kępy 4,6 s, Leże
Ropuchy 6,2 s; Dżungla — Polana Zwijogonów 1,7 s, Kwietnik Gębokwiatów 3,2 s, Gaj Kokosów 4,6 s, Ruiny Pancernika
6,3 s. Strażnik na końcu zajmuje 74–80% wysokości kadru między pasami (16:9, 667 × 375, 844 × 390).
Podglądy z góry i z boku: `podglady/trasa_las.jpg`, `trasa_bagno.jpg`, `trasa_dzungla.jpg`.

## Haczyk w pakiecie lasu-pasa (jedyna zmiana poza tym pakietem)
Pakiety gry biomów mają własny, starszy przelot kamery (bez pomijania, bez oprawy) — bez haczyka grałyby oba naraz.
W `swiat/las_pas_gra/zrodla/SerwerPasa.server.luau` (wspólny skrypt lasu, Bagna i Dżungli) doszło 13 linii:
- skrypt ogłasza atrybut swojego kontenera `UstepujeCutscence = true`;
- gdy stoi `Workspace/CutscenkaBiomu` z atrybutem `Przejmuje_<id biomu>` = true, automat pasa nie zaczyna własnego
  przelotu. Bez kontenera albo atrybutu wszystko działa jak dotąd.

`SerwerCutscenki` przejmuje biom tylko wtedy, gdy kontener gry ogłosił `UstepujeCutscence`; inaczej zostawia stary
przelot i pisze dlaczego (`StanBiomu_<id>` = `brak_haczyka` / `brak_biomu`). Skrypty pasa z haczykiem są wgrane do
trzech kontenerów gry od 18.11.2026 (`zbuduj.py --skrypty` tamtych pakietów).
Lokalnie u klienta pakiet ustawia też na kontenerze gry atrybut `KlientPrzelot` (mgła biomu rzednie jak przy starym
przelocie) i woła haczyk klienta potworów `SterowanieKlienta` (`"wymus"`, `"klip"`).

## Jak zbudować, sprawdzić i usunąć
```
python -B swiat/cutscenka_biomu/dane.py                       # policz trasy, zapisz zrodla/DaneCutscenki.luau
python -B swiat/cutscenka_biomu/dane.py --opis                # tabela tras bez zapisu
python -B swiat/cutscenka_biomu/podglad.py                    # podglady/trasa_<biom>.jpg
python -B swiat/cutscenka_biomu/testy/test_cutscenki.py       # test bez Studio (kilka sekund)
python -B swiat/cutscenka_biomu/sprawdz_luau_cutscenki.py     # kontrola statyczna źródeł Luau
python -B swiat/cutscenka_biomu/zbuduj.py --sucho             # dane aktualne, kontrola Luau, plan budowy
python -B swiat/cutscenka_biomu/zbuduj.py                     # zbuduj Workspace/CutscenkaBiomu (Studio w trybie Edit)
python -B swiat/cutscenka_biomu/zbuduj.py --skrypty           # tylko wymień moduły i skrypty
python -B swiat/cutscenka_biomu/zbuduj.py --stan              # odczyt kontenera
python -B swiat/cutscenka_biomu/zbuduj.py --usun              # usuń własny kontener (wraca stary przelot pasa)
python -B swiat/cutscenka_biomu/testy/proba_play.py <folder poza repo> [--bez-zrzutow]   # próba w grze (część B)
```
Budowniczy sprawdza miejsce gry i tryb Edit, rusza wyłącznie własny kontener (atrybut `Wygenerowane`), stawia
punkty historii, niczego nie zapisuje, nie publikuje i nie dotyka `Lighting`. Kontener nie ma ani jednej części.
Skrypty zaczynają się od strażnika `RunService:IsStudio()` — poza Studio serwer usuwa cały kontener.

## Pliki
| Plik | Co to |
|---|---|
| `ustawienia.json` | biomy, kształt trasy, oprawa i układ napisów, liczby serwera, nazwy zależności, progi testów |
| `dane.py` | mapy → trasy → `zrodla/DaneCutscenki.luau`; miary tras (`--opis`) |
| `logika_cutscenki.py` | lustro `LogikaCutscenki.luau` w Pythonie |
| `podglad.py` | rysunki tras z góry i z boku (Pillow) → `podglady/` |
| `zbuduj.py` | budowniczy (`--sucho`, `--skrypty`, `--stan`, `--usun`) |
| `sprawdz_luau_cutscenki.py` | kontrola statyczna Luau (reguły z `swiat/las_potwory/sprawdz_luau.py` + własne) |
| `zrodla/DaneCutscenki.luau` | WYGENEROWANE: trasy, oprawa, nazwy |
| `zrodla/LogikaCutscenki.luau` | krzywa, automat serwera, układ napisów, przypadki wzorcowe |
| `zrodla/SerwerCutscenki.server.luau` | kto i kiedy: pamięć, blokady, wczytanie mapy, uchwyt |
| `zrodla/KlientCutscenki.client.luau` | co widać: kamera, oprawa, strażnik, pominięcie, sprzątanie |
| `testy/test_cutscenki.py` | 39 testów bez Studio |
| `testy/proba_play.py` | próba w grze C00–C14; wynik i konsola idą do folderu poza repozytorium |
| `pomoc_prob.py` | wspólna pomoc prób lasu, Bagna i Dżungli: punkt „przelot” sprawdza nową cutscenkę albo stary przelot |
| `klatki/` | zrzuty z gry (bez interfejsu, listy graczy i nazwy nad postacią) |

## Wyniki próby w grze (18.11.2026, okno Studio na wierzchu)
`python -B swiat/cutscenka_biomu/testy/proba_play.py <folder poza repo>` — przebieg bez zrzutów (17:08, pomiar klatek): 15 OK, 1 `?` (C09 zrzuty pominięte), 0 BŁĄD; przebieg ze zrzutami (16:30): 15 OK, 1 `?` (C08 — przy zrzutach czas klatki jest niemiarodajny), 0 BŁĄD.

| Punkt | Wynik | Co wyszło |
|---|---|---|
| C00 Edit: kontener, skrypty, haczyki | OK | 10 instancji, 4 skrypty, 0 części; haczyk w `SerwerPasa` lasu, Bagna i Dżungli |
| C01 Play: gotowość | OK | serwer i klient gotowe, trzy biomy „przejety”, zgodność logiki 21/21, zapis postępu nieaktywny; liczniki starego przelotu 0 → 0 przez całą próbę |
| C02 las, pierwsze wejście | OK | start 1,5–1,8 s po wejściu; kamera skryptowa, pasy, plansza „LAS”, postać zakotwiczona, blokada walki, podpowiedzi E i ekrany gry schowane |
| C03 w trakcie | OK | próba walki: walka nie ruszyła; postać przesunęła się o 0,000 st |
| C04 koniec ze strażnikiem | OK | 11,2 s (dane 11,2), napis „STRAŻNIK GAJU”, klip ryku zagrał, dźwięk ryku z katalogu zagrał, 4 podpisy przegród |
| C05 po cutscence | OK | kamera `Custom`, W przesuwa postać o 14,7 st, kotwica i blokada zdjęte, ekrany, podpowiedzi E i lista graczy jak przed |
| C06 drugie wejście | OK | licznik cutscenek 1 → 1, pamięć lasu i atrybut `WidzialPrzelotLasu` = true |
| C07 Bagno, pomijanie | OK | domyślnie `Pomijanie = false`: przycisku nie ma, Spacja nic nie robi; po włączeniu przełącznika przycisk 210 × 66 px, Spacja kończy w 0,4 s, wszystko wraca, licznik pominięć 0 → 1 |
| C08 Dżungla, czas klatki | OK | 11,2 s, napis „WĄŻ STU LIAN”, ryk; 673 klatki lotu: średnio 16,6 ms, 95% 18,1 ms, najdłuższa 23,7 ms (próg 34 ms; przebieg bez zrzutów) |
| C09 zrzuty | OK | osiem kadrów w `klatki/` |
| C10 odtworzenie i śmierć postaci | OK | odtworzenie na życzenie startuje po 3,4–3,8 s; po śmierci w trakcie: kamera `Custom`, nic zablokowane, ekrany jak przed |
| C11 przejście przez chmury | OK | w czasie chmur cutscenka nie gra (2 odmowy, pamięć pusta, bez kotwicy), po chmurach start po 1,1 s |
| C12 telefon | OK | układ 667 × 375 i 844 × 390 u klienta = układ z testu bez Studio; na ekranie próby 2041 × 1153 nazwa 100 px, nadtytuł 30 px |
| C13 konsola | OK | bez błędów i ostrzeżeń pakietu (poza zapowiedzianym przerwaniem przy śmierci postaci) |
| C14 powrót do Edit | OK | Studio po próbie w trybie Edit |

Zrzuty (`klatki/`): `01_las_plansza.jpg`, `02_las_przegroda.jpg`, `03_las_straznik.jpg`, `04_bagno_przycisk_pomin.jpg`
(jedyny kadr z włączonym przełącznikiem pomijania), `05_dzungla_plansza.jpg`, `06_dzungla_przegroda.jpg`,
`07_dzungla_leze.jpg`, `08_dzungla_straznik.jpg`.

Po obejrzeniu kadrów poprawione: wersaliki napisów z polskimi literami (`string.upper` w Luau zostawiał „ż”, „ą”),
odstęp kamery od brył z 2,8 na 5 st (liść olbrzym w Dżungli zasłaniał pół kadru), węzeł leża bliżej środka strefy
rzadkiego potwora, śmierć postaci w trakcie bez wpisu błędu w konsoli.

## Próby pakietów biomów i regresja (18.11.2026)
Punkty o przelocie w `swiat/las_pas_gra/testy/proba_play.py` (P04–P06), `swiat/bagno_pas_gra/testy/proba_play.py`
(B03, B04) i `swiat/dzungla_pas_gra/testy/proba_play.py` (J03, J04) sprawdzają to, co akurat gra: nową cutscenkę,
gdy `CutscenkaBiomu` przejął biom, albo stary przelot pasa, gdy kontenera nie ma (`pomoc_prob.py`: te same pola
wyniku w obu przypadkach). Próby innych biomów oznaczają wcześniejsze biomy jako widziane (`"oznacz"`), tak jak
dotąd wstrzymywały stary przelot; to samo robi próba przejścia przez chmury.

**Czarny zrzut `swiat/dzungla_pas_gra/klatki/02_przelot_kwietnik.jpg` — przyczyna i zabezpieczenie.** Próby Bagna
i Dżungli wchodzą do biomu pieszo, a narzędzie marszu wraca dopiero, gdy postać stanie — czyli pod koniec lotu
(postać jest w locie zakotwiczona). Próba liczyła chwile zrzutów od momentu, w którym sama zauważyła lot, więc kadr
„z połowy lotu” trafiał w końcowe zaciemnienie (jasność pliku 0,0). Teraz zrzuty przelotu idą według czasu lotu
u klienta, tylko przy odsłoniętej zasłonie, a kadr spóźniony o ponad 1,2 s wypada z planu, zamiast pokazać co innego,
niż mówi nazwa pliku (`pomoc_prob.pora_na_zrzut`, test 6g). Skutek uboczny: próby Bagna i Dżungli robią same tylko
końcowe kadry lotu (strażnik, ryk); kadry z początku lotu Dżungli odświeżył 18.11 osobny krótki przebieg tym samym
narzędziem zrzutu.

`python -B swiat/przejscie_gry/regresja_calosci.py <folder poza repo> "proba dymna,las-pas,bagno,dzungla,chmury,bohater"`
(18.11.2026, 16:35–17:00, z kontenerem `CutscenkaBiomu` w grze; wszystkie próby zakończone kodem 0, Studio po każdej
w trybie Edit):

| Próba | Wynik | Punkty o przelocie |
|---|---|---|
| próba dymna | 14 OK | D02: chmury → las, po cutscence kamera `Custom` |
| las-pas | 22 OK, 1 `?` (P14 koszt — ocenia człowiek) | P04 nowa cutscenka 11,4 s z rykiem, walka w trakcie odrzucona; P05 i P05t bez drugiej (licznik 1 → 1); P06 odtworzenie uchwytem cutscenki 11,3 s |
| Bagno | 15 OK, 1 `?` (B13 koszt) | B03 wejście bramą pieszo: 11,2 s, ryk, kamera `Custom`, przelot lasu nie ruszył; B04 i B04b bez drugiej |
| Dżungla | 18 OK, 1 `?` (J13 koszt) | J03 wejście bramą pieszo: 11,2 s, ryk, kamera `Custom`; J04 i J04b bez drugiej |
| bohater | 19 OK, 1 `?` (B16 runda mini-gry — jak przed zmianą) | B14 bieg i walka w lesie po cutscence |
| chmury | 6 z 6 testów OK | biomy oznaczone jako widziane na czas testów |

Próba chmur zapisuje własny plik wyniku w `swiat/teleport_chmury/wyniki/` — zostaje poza repozytorium.

## Wyniki bez Studio (18.11.2026)
| Polecenie | Wynik |
|---|---|
| `python -B swiat/cutscenka_biomu/testy/test_cutscenki.py` | 40 testów OK |
| `python -B swiat/cutscenka_biomu/sprawdz_luau_cutscenki.py` | 4 pliki OK (z parserem `luau_mini`) |
| `python -B swiat/cutscenka_biomu/zbuduj.py --sucho` | OK, Studio nieużywane |
| `python -B swiat/cutscenka_biomu/dane.py --sprawdz` | moduł danych aktualny |
| testy pakietów biomów | `test_pasa` 45 OK, `test_poziomow` 4 OK, `test_bagna` 26 OK, `test_dzungli` 28 OK, `sprawdz_luau_pasa` 7 plików OK |

Testy sprawdzają m.in.: nazwy biomów, strażników i atrybutów równe nazwom z pakietów; czas 8–12 s; ciągłość,
prędkość, przyspieszenie i obrót w progach; odstęp od brył mapy; kolejność i zwolnienia przy przegrodach; inkubator
i strażnika w kadrze; że przesunięcie strażnika albo przegrody w mapie przesuwa trasę, a ściana w poprzek pasa ją
podnosi; automat (pierwsze i drugie wejście, odmowa, cisza klienta, pominięcie, śmierć postaci, odtworzenie, 300
losowych przebiegów bez pozostawionej blokady); zgodność Luau z lustrem w Pythonie; układ napisów i przycisku na
667 × 375 i 844 × 390; pomoc prób dla starego i nowego przelotu.

## Czego nie sprawdzono
- **Telefonu**: ani prawdziwego, ani emulatora Studio. Układ na 667 × 375 i 844 × 390 jest policzony (ta sama funkcja
  u klienta i w teście), a szerokość napisów oszacowana (0,52 wysokości czcionki na znak); dotyk przycisku POMIŃ nie
  był naciskany. Czas klatki mierzony na komputerze autora przy limicie 60 kl./s — płynność na telefonie
  (D-077: „do sprawdzenia”) zostaje otwarta.
- Dwóch graczy naraz i wyjścia gracza w trakcie cutscenki (próba ma jednego gracza).
- Opublikowanej gry: skrypty kończą się tam na strażniku Studio, a serwer usuwa kontener.
- Zasłonięć widoku poza obejrzanymi kadrami: test liczy odstęp położenia kamery od brył, nie to, co stoi między
  kamerą a celem. W kadrze leża Dżungli rzadkiego potwora nie widać (stoi poza kadrem albo za liśćmi).
- Tabliczki poziomu potworów (`POZ. 18`) prześwitują pod planszą z nazwą biomu — to napisy świata z pakietu potworów.
- Uchwyty przenoszenia pasa nie wiedzą o nowej cutscence: inny skrypt serwera mógłby przenieść gracza w jej trakcie
  (gracz sam tego nie wywoła — ma schowany interfejs i wyłączone podpowiedzi E).
