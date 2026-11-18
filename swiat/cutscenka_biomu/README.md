# Cutscenka przelotu przez biom (D-077) — `swiat/cutscenka_biomu`

> **Status: propozycja wykonania zatwierdzonej decyzji D-077.** Część A (18.11.2026): kod, dane i testy bez Studio.
> W Studio **nic jeszcze nie stoi** i nic nie było uruchomione w grze — budowa, próba w Play, zrzuty i pomiar klatek
> to część B. Wybory i pytania do ludzi: `PROJEKT.md`.

## Co robi
Przy pierwszym wejściu gracza do biomu (las, Bagno, Dżungla) w danej sesji — przez chmury albo bramą pieszo —
gracz dostaje krótką cutscenkę; przy kolejnych wejściach jej nie ma. Widzi ją tylko ten gracz.

1. **Oprawa:** zasłona, czarne pasy u góry i dołu (po 11% wysokości), plansza z nazwą biomu, przycisk **POMIŃ**
   (dotyk, mysz, Spacja, Enter, B na padzie). HUD, pozostałe ekrany, lista graczy, czat i podpowiedzi E znikają na
   czas cutscenki i wracają po niej.
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
- **Wyłącznik pomijania:** atrybut kontenera `Pomijanie = false` (ustawiony w Edit przechodzi na odbudowany kontener).

## Trasy (liczone z map, nie wpisane ręcznie)
`dane.py` czyta `krotki/znaczniki.json` i `krotki/czesci.json` każdego biomu oraz moduł danych pakietu gry. Węzły:
start 12 st za plecami gracza → inkubator → wejście każdej przegrody (na zmianę po lewej i prawej, 7 st od osi) →
wejście areny → ujęcie strażnika. Wysokość węzła to najniższa z listy z odstępem 4 st od brył mapy; gdy krzywa wejdzie
bliżej niż 2,8 st od bryły, sąsiednie węzły idą w górę i trasa liczy się od nowa. Prędkość: start z miejsca,
zwolnienie nad każdą przegrodą, hamowanie do zera przed strażnikiem. Klient gra próbki co 0,1 s połączone
jednostajną krzywą Catmull-Rom (ciągła prędkość).

| Biom | Droga | Czas | Prędkość przelotowa / przy przegrodach | Przyspieszenie | Obrót | Odstęp od brył | Wysokość |
|---|---|---|---|---|---|---|---|
| Las | 360 st | 11,2 s | 68 / 27–31 st/s | do 133 st/s² | do 51°/s | 3,44 st (pień Bramy Pniaków) | 7,2–30,0 st |
| Bagno | 349 st | 11,2 s | 67 / 27–30 st/s | do 129 st/s² | do 51°/s | 7,89 st (kładka) | 8,3–15,4 st |
| Dżungla | 349 st | 11,2 s | 67 / 27–30 st/s | do 132 st/s² | do 50°/s | 4,13 st (liść olbrzym) | 8,9–21,0 st |

Przystanki (czas najwolniejszego miejsca): las — Zagroda Slime'ów 1,7 s, Lasek Muchomorowy 3,2 s, Wilcze Zarośla
4,6 s, Leże Trolla 6,0 s; Bagno — Rechotne Oczka 1,7 s, Bulgotne Trzęsawisko 3,2 s, Kłapiące Kępy 4,6 s, Leże
Ropuchy 6,1 s; Dżungla — Polana Zwijogonów 1,7 s, Kwietnik Gębokwiatów 3,2 s, Gaj Kokosów 4,6 s, Ruiny Pancernika
6,1 s. Strażnik na końcu zajmuje 74–80% wysokości kadru między pasami (16:9, 667 × 375, 844 × 390).
Podglądy z góry i z boku: `podglady/trasa_las.jpg`, `trasa_bagno.jpg`, `trasa_dzungla.jpg`.

## Haczyk w pakiecie lasu-pasa (jedyna zmiana poza tym pakietem)
Pakiety gry biomów mają własny, starszy przelot kamery (bez pomijania, bez oprawy) — bez haczyka grałyby oba naraz.
W `swiat/las_pas_gra/zrodla/SerwerPasa.server.luau` (wspólny skrypt lasu, Bagna i Dżungli) doszło 13 linii:
- skrypt ogłasza atrybut swojego kontenera `UstepujeCutscence = true`;
- gdy stoi `Workspace/CutscenkaBiomu` z atrybutem `Przejmuje_<id biomu>` = true, automat pasa nie zaczyna własnego
  przelotu. Bez kontenera albo atrybutu wszystko działa jak dotąd.

`SerwerCutscenki` przejmuje biom tylko wtedy, gdy kontener gry ogłosił `UstepujeCutscence`; inaczej zostawia stary
przelot i pisze dlaczego (`StanBiomu_<id>` = `brak_haczyka` / `brak_biomu`). **W Studio haczyk zadziała dopiero po
wgraniu skryptów pasa do trzech kontenerów gry** (budowniczowie tamtych pakietów) — to część B.
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
| `testy/proba_play.py` | próba w grze C00–C14 (napisana, **nieuruchomiona**) |

## Wyniki (18.11.2026, bez Studio)
| Polecenie | Wynik |
|---|---|
| `python -B swiat/cutscenka_biomu/testy/test_cutscenki.py` | 39 testów OK |
| `python -B swiat/cutscenka_biomu/sprawdz_luau_cutscenki.py` | 4 pliki OK (z parserem `luau_mini`) |
| `python -B swiat/cutscenka_biomu/zbuduj.py --sucho` | OK, Studio nieużywane |
| `python -B swiat/cutscenka_biomu/dane.py --sprawdz` | moduł danych aktualny |
| testy pakietów biomów przed haczykiem i po nim | `test_pasa` 45 OK, `test_poziomow` 4 OK, `test_bagna` 26 OK, `test_dzungli` 27 OK przed / 28 OK po (jeden test dopisał w tym czasie inny agent), `sprawdz_luau_pasa` 7 plików OK |

Testy sprawdzają m.in.: nazwy biomów, strażników i atrybutów równe nazwom z pakietów; czas 8–12 s; ciągłość,
prędkość, przyspieszenie i obrót w progach; odstęp od brył mapy; kolejność i zwolnienia przy przegrodach; inkubator
i strażnika w kadrze; że przesunięcie strażnika albo przegrody w mapie przesuwa trasę, a ściana w poprzek pasa ją
podnosi; automat (pierwsze i drugie wejście, odmowa, cisza klienta, pominięcie, śmierć postaci, odtworzenie, 300
losowych przebiegów bez pozostawionej blokady); zgodność Luau z lustrem w Pythonie; układ napisów i przycisku na
667 × 375 i 844 × 390.

## Czego nie sprawdzono
- **Niczego w grze**: skrypty nie były uruchomione w Roblox (tylko parser i interpreter `luau_mini` dla logiki).
  Kamera, ekrany, sterowanie, dźwięk, wczytywanie mapy, haczyk potworów — do sprawdzenia w części B.
- Odstęp od brył liczony jest dla położenia kamery (bryły jako pudełka); test nie sprawdza, czy coś zasłania widok.
  Potwory i strażnik nie są częścią mapy — w kadrze strażnika liczone jest pudło z rozmiarów w znacznikach.
- Szerokość napisów w teście telefonu to oszacowanie (0,52 wysokości czcionki na znak), nie pomiar w grze.
- Płynność na telefonie (D-077: „do sprawdzenia”) — pomiar czasu klatki jest w próbie, prawdziwego telefonu nie ma.
- Po wdrożeniu próby starego przelotu w pakietach biomów (`las_pas_gra`, `bagno_pas_gra`, `dzungla_pas_gra`,
  regresja całości) zobaczą, że stary przelot nie rusza — do uzgodnienia w części B.
