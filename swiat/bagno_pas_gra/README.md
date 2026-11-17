# Bagno w grze — drugi grywalny biom (potwory, brama do Dżungli, przelot, mgła, teleport)

*Status: **propozycja** (17.11.2026). Plan Bagna (`swiat/bagno_pas/`) nie jest kanonem; zlecenie budowy dał Karol
(„Leć wszystko”). Wszystko stoi w osobnych kontenerach (`Workspace/BagnoPas` — mapa, `Workspace/BagnoPasGra` — gra),
więc całość da się cofnąć (`--usun`). **17.11.2026 zbudowane w Studio i sprawdzone w trybie Play (jeden gracz, komputer)
— wyniki w rozdz. „Co sprawdzone w grze”.***

> **W skrócie.** Gracz, który pokonał Strażnika Gaju, przechodzi bramą lasu prosto do Bagna (las w Play usuwa swoją
> tabliczkę „BAGNO — WKRÓTCE”, gdy stoi mapa Bagna) albo wybiera „Bagno” w przejściu przez chmury (kraina otwarta tym
> samym stanem bramy lasu). W Bagnie: przelot kamery przy pierwszym wejściu z rykiem Strażnika Topieli, pięć gatunków w
> przegrodach (poziomy 10 → 16), walki na tym samym silniku i ekranie co w lesie (nagrody i POMIŃ przy znanym gatunku
> działają tak samo), Strażnik Topieli otwiera bramę do Dżungli tylko zwycięzcy, a za nią tabliczka
> „DŻUNGLA — WKRÓTCE”; Kamień Powrotu → bazar; szarozielona mgła tylko u gracza (`Lighting` bez zmian).
> **Ten sam kod co las-pas** (`swiat/las_pas_gra`, `swiat/las_potwory`, silnik `src/server/Walka`) — różnią się dane.

## Pliki

| Plik | Co to jest |
|---|---|
| `generuj_dane.py` | konfiguracja Bagna dla generatora lasu-pasa (mapa `swiat/bagno_pas`, gatunki, poziomy, mgła, teksty, nazwy `biom`) → trzy moduły niżej; `--sprawdz`, `--wyjscie DIR`, `--bez-mapy` |
| `przeciwnicy.py` | dane walki pięciu gatunków (przepis z kalkulatora balansu + jedna cecha na gatunek); `python -B … --ziaren N` drukuje tabelę wygranych klas |
| `zbuduj.py` | budowa `Workspace/BagnoPasGra` budowniczym lasu-pasa (`ustaw_konfiguracje`): `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `zrodla/DanePotworowBagna.luau`, `zrodla/DaneBagna.luau`, `silnik/DaneWalkiBagna.luau` | **wygenerowane** — nie edytować |
| `podglad_potworow.py` | podgląd potworów bez Blendera i Studio (Pillow) → `podglad/` (`szereg.jpg`: pięć potworów w jednej skali obok gracza) |
| `studio/usun_zapowiedz_bagna.luau` | usuwa `Workspace/LasPas/ZapowiedzBagna` przed budową mapy (tryb Edit, punkty historii) |
| `testy/test_bagna.py` | 26 testów offline (opis w nagłówku), ok. 2 s |
| `testy/proba_play.py` | próba w Studio (Play), lista B00–B14 w nagłówku; `--sprawdz` parsuje bez Studio wszystkie 32 kawałki Luau; zrzuty → `klatki/`, wyniki do folderu poza repo |

Modele potworów (nowe pliki, format lasu): `swiat/postacie/{rechotek, bulgotnik, klodoklap, ropucha_z_chatka,
straznik_topieli}.py`; tabela aktorów `swiat/test_walki2/aktorzy_bagna.py` (dołączona na końcu `aktorzy.py`); dane
rigów i klipów `swiat/test_walki2/dane/<klucz>.json` (`python -B swiat/test_walki2/aktorzy.py --tylko <klucze> --liniowo`
— klipy mają klucz w każdej klatce, więc próbki liniowe = ruch z modułu, bez Blendera).

## Potwory (przyjęte, do zmiany)

Statystyki: potwór lasu o podobnej roli × **k = 1,14** (kalkulator balansu 17.11, Bagno w planie rosnącym; przepis
`tools/walka/progresja.potwor_biomu`: broń i Siła × k, życie (1 + m) × k − 1) i poprawki niżej. Poziomy z kalkulatora
(gracz wchodzi z lasu na ok. 10. poziomie, wychodzi na ok. 17.; rzadki i strażnik o poziom niżej niż gracz na wyjściu)
— **nie** 11–19 z planu Bagna, bo od 17.11 gracz walczy na swoim prawdziwym poziomie (`swiat/stan_gracza`).
Wygrane: postacie wzorcowe bez treningu, 400 walk na parę (`przeciwnicy.py`).

| Gatunek | Strefy · poziomy | Klasa (baza) | Umiejętności | Cecha w walce (inna niż w lesie) | Wygrane W / Z / M |
|---|---|---|---|---|---|
| Rechotek | r1–r3 · 10–12 | Zwiadowca (Cierniowy Wilk) | Uderzenie z góry | sus z góry z premią krytyka + unik +6 pp | 75 / 74 / 72% (poz. 10) |
| Bulgotnik | b1–b3 · 12–14 | Mag (Muchomornik) | Bariera, Chmura zarodników | osłania się bańką (tarcza procentowa) i truje | 74 / 75 / 74% (poz. 12) |
| Kłodokłap | k1–k3 · 14–16 | Wojownik (Leśny Troll) | Miażdżący cios | blokuje korą (szansa bloku 15%), Pancerz +20%, zero uniku; kłapnięcie zdziera pancerz | 75 / 77 / 83% (poz. 14) |
| Ropucha z Chatką (rzadka) | t1 · 16 | Mag (Leśny Troll, Int ↑) | Chmura zarodników, Uderzenie z góry | rzadki Mag z dwiema umiejętnościami: dym z komina truje, ciężki sus | 52 / 55 / 56% (gracz 17) |
| Strażnik Topieli | arena · 16 | strażnik (Strażnik Gaju) | Ogłuszające uderzenie | fizyczne uderzenie w taflę (60% ogłuszenia), zysk many +25%, odporność na magię +30% | 20 / 36 / 20% (gracz 17) |

Dla porównania las (gracz 10): Wilk 85%, Troll (poz. 9) 68%, Strażnik Gaju 36%. Kalkulator dla Bagna bez treningu:
zwykłe na wejściu 73%, strażnik na wyjściu 24%.

**Bez zmiany silnika.** Umiejętności i efekty są istniejące (odtwarzacz walki zna ich nazwy i choreografie). Dane
gatunków żyją w `przeciwnicy.py`, a kontener Bagna dostaje kopię `Dane` z dopisanymi przeciwnikami
(`silnik/DaneWalkiBagna.luau`); `tools/walka/dane_walki.json` i jego testy bez zmian (testy silnika wymagają m.in.
jednego strażnika i znanej listy klas potworów). Spowolnienia (plan: „lepki język”) nie ma — w silniku daje je tylko
Lodowy pocisk (lód); własna umiejętność bagienna wymaga wpisu w danych silnika i choreografii (do decyzji).

## Co jest w kontenerze `Workspace/BagnoPasGra`

Jak `LasPasGra` (README lasu-pasa), z różnicami: `Moduly/DanePotworow` ← `DanePotworowBagna`, `Moduly/DanePasa` ←
`DaneBagna`, `Moduly/Walka/Dane` ← `DaneWalkiBagna`; `Sygnaly/PrzeniesDoBagna` (uchwyt dla przejścia przez chmury,
punkty `przybycie`/`las`, `przed_brama`, `za_brama`; odmowa `zamkniete` bez bramy lasu); części: zapora i napis
„ZAMKNIĘTE / Pokonaj Strażnika Topieli” na bramie do Dżungli (x 2974), `ZaBrama` z tabliczką „DŻUNGLA — WKRÓTCE”,
punkt E Kamienia Powrotu (2048,5; −718,5). Stale_*: `BagnoPasGraSzablony`, GUI `BagnoPasGraBohater`/`BagnoPasGraBaner`,
prefiks `[BagnoPasGra] `, panel „Bagno · ”, poziomy panelu `auto,10,15,20`, `PANEL_ZAPAS = -40` (przy bramie nie widać
dwóch paneli), tytuł banera „STRAŻNIK TOPIELI POKONANY!”. Pamięć gracza: `widzialPrzelotBagna`,
`pokonalStraznikaBagna` (atrybuty `WidzialPrzelotBagna`, `PokonalStraznikaBagna`).

## Co sprawdzone w grze (17.11.2026, Studio, tryb Play)

**Zbudowane:** `LasPas/ZapowiedzBagna` usunięta (49 części, skrypt z punktami historii), mapa `Workspace/BagnoPas`
(9017 części, streaming: 10 grup Persistent, 61 StreamingMesh), aktorzy Bagna i dane Maga w `TestWalki2`
(`--tylko-aktorzy`, potem `--skrypty`; `testy/sprawdz_edit.py` WYNIK: OK, 45/45 walk zgodnych z Pythonem), skrypty
`las_potwory`, `las_pas_gra`, `teleport_chmury`, `dzwiek_gra`, `stan_gracza` (Bagno dopisane do źródeł łupu) i
`Workspace/BagnoPasGra` (Skrot `55c50b774178`, 60 instancji, 18 skryptów, 7 części).

**Próba Bagna** (`testy/proba_play.py`, drugi przebieg, okno Studio na wierzchu; `wyniki/proba_play_20261117_drugi.json`):
**14 × OK, B13 „?”** (koszt ocenia człowiek).
- B01: 20 potworów przy 1 graczu, zgodność logiki 70/70 i 39/39, `Przekierowanie` „nie_ten_biom”; las:
  `NastepnyBiomJest`, bez `ZaBrama`; klient w trybie „aktorzy”.
- B02: bez bramy lasu uchwyt `PrzeniesDoBagna` → „zamkniete”, teleport bez Bagna, gracz z x 2400 cofnięty do 2024 z
  komunikatem „Bagno jest za bramą lasu — najpierw pokonaj Strażnika Gaju.”
- B03: bieg przez otwartą bramę lasu → przelot Bagna 13,9 s z rykiem Strażnika Topieli, kamera Custom, przelot lasu
  nie ruszył. B04: chmury → uchwyt `PrzeniesDoBagna` → Pomost (2054; −700), bez drugiego przelotu.
- B05: 600 próbek pozycji w 30 s — 0 poza polem strefy.
- B06: prawdziwe E przy każdym gatunku (r1 Rechotek, b1 Bulgotnik, k1 Kłodokłap, t1 Ropucha), walka do końca, kamera i
  postać wracają do Bagna; mostek pomijania prototypu przyjął 4 walki. Wynik każdej walki z Studio (ziarno serwera)
  powtórzony w Pythonie (`silnik.py`) — 5/5 identycznych; osobno 4 pary × 100 walk w kopii silnika w Studio = Python.
- B07: druga walka z Rechotkiem — przycisk POMIŃ, spacja, serwer „ok”.
- B08 (stan gracza): Level 11 → walka na 11. poziomie (Rechotki r1 mają 10), łup 93 zł i 69 XP w atrybutach, żeton
  Bagna (`TokenyKrainy_bagno` 1). Pierwszy przebieg: łup odrzucony (`zle_zrodlo`) — poprawka w `swiat/stan_gracza`.
- B09: za bramą do Dżungli cofnięty do 2964 z komunikatem; wrota z kolizją.
- B10: Wojownik poz. 10 przegrał ze Strażnikiem (brama zamknięta), Zwiadowca poz. 20 wygrał za 1. razem → jeden baner
  „STRAŻNIK TOPIELI POKONANY! / Brama do Dżungli otwarta — Dżungla wkrótce”, wrota u klienta bez kolizji (serwer z
  kolizją), przejście za bramę (x 2987) bez cofnięcia, tabliczka „DŻUNGLA — WKRÓTCE”.
- B11: Kamień Powrotu → bazar (990; 3; −697). B12: mgła Bagna 1 / lasu 0 (gęstość 0,42), w lesie odwrotnie (0,36);
  serwer bez zmian (0,30). B14: konsola bez błędów Bagna.
- B13: Kępy — klatka klienta śr. 16,7 ms, p95 18,2, maks. 18,8 ms (okno na wierzchu); 7 widoków, 748 brył.

**Przejście „po ludzku”** (`testy/proba_ludzka.py`, `wyniki/proba_ludzka_20261117.json`): **4 × OK** — gracz poz. 11 po
Strażniku lasu przechodzi bramą chodzeniem, ogląda przelot, prawdziwe E przy Rechotku (wygrana w 11 turach, +96 zł,
+67 XP, HUD = atrybuty), teleport przez chmury pokazuje Bagno otwarte i przenosi na Pomost. Zrzuty `klatki/h01…h08`.

**Las z Bagnem** (`swiat/las_pas_gra/testy/proba_play.py`, `swiat/las_pas_gra/wyniki/proba_play_20261117_z_bagnem.json`):
**21 × OK, P14 „?”** (klatka 16,7 ms), w tym P11n (ZaBrama lasu usunięta) i ratunek za bramą lasu przez serwer Bagna.

**Poprawione po pierwszym przebiegu:** B03 i B06 — błędy próby (czas lotu z pomiaru klienta, kamera z haczyka klienta
Bagna); B08 — `swiat/stan_gracza/dane.py` przyjmuje łup z `BagnoPasGra` (test 6b czyta listę kontenerów z pakietów).

**Zauważone, nie naprawiane (do właściciela odtwarzacza):** karta wyniku walki w Bagnie pisze „TOKENY LASU” (napis na
sztywno w `swiat/test_walki2/zrodla/InterfejsWalki2.luau`, linia 898), choć łup to żeton Bagna — zrzut
`klatki/h06_wynik_walki.jpg`. Wskrzeszenia w walkach Bagna nie było (postacie wzorcowe go nie mają).

**Niesprawdzone:** telefon i emulator, dwóch graczy (brama i wrota tylko u zwycięzcy, wspólny Strażnik), pad,
odrodzenie Ropuchy (150 s) i Strażnika (120 s) zmierzone w grze, wszystkie klasy w zwykłym trybie (tylko Warrior).

## Jedno pilnowanie przy bramie lasu

Przy bramie lasu stykają się dwa serwery pasa. Reguła pierwszeństwa (w `SerwerPasa`, test `3e`): gdy stoi mapa
następnego biomu, las pilnuje przelotu i ratunku tylko przed linią swojej bramy (x < 2034), Bagno od niej; cofanie
graczy bez prawa wejścia robi las do x 2234 (brama + głębokość 200), Bagno dopiero dalej (`biom.wymaganie.odX`). W żadnym
miejscu dwa serwery nie przenoszą gracza naraz, a gracz bez przelotu lasu nie dostaje na Pomoście dwóch przelotów.

## Zmiany we wspólnych plikach (dokładne podmiany)

- `swiat/las_pas_gra/`: konfiguracja biomu w `zrodlo_mapy.py`, `generuj_dane.py`, `zbuduj.py`; skrypty `SerwerPasa`,
  `KlientPasa`, `MglaPasa`, `PamiecGracza` czytają `D.biom`; las bez mapy Bagna działa jak dotąd (opis w README lasu,
  „Drugi biom”). `DanePasa.luau` przegenerowany (nowe pole `biom`). `testy/proba_play.py` lasu: przy stojącym Bagnie P11
  wyłącza przelot Bagna (haczyk `zapomnijPrzelot`), liczy ratunki obu kontenerów i ma nowy punkt P11n (ZaBrama lasu
  usunięta, `NastepnyBiomJest`).
- `swiat/las_potwory/zrodla/Stale.luau` + `KlientPotworow.client.luau`: tytuł banera po Strażniku jako stała
  `TYTUL_BANERA_STRAZNIKA` (las: ten sam napis).
- `swiat/test_walki2/`: `aktorzy.py` dołącza `aktorzy_bagna.py` (na końcu — galeria lasu bez zmian); 5 ikon w
  `zrodla/InterfejsWalki2.luau`; `zrodla/SerwerWalki2.server.luau` — `BagnoPasGra` w źródłach pomijania (D-078), a
  gatunek z mostka jest sprawdzany także w kopii `Dane` kontenera źródła (bez tego walki Bagna nie dałyby się pominąć).
- `swiat/teleport_chmury/`: `krainy.json` — Bagno z `odblokowanie.atrybut_gracza = PokonalStraznikaLasu` i uchwytem
  `PrzeniesDoBagna` (przelot po chmurach 2,4 s); `SerwerTeleportu` — funkcja `otwarta()` (jedno źródło: stan bramy lasu).
- `swiat/dzwiek_gra/ustawienia.json`: odgłosy pięciu gatunków z istniejącego arkusza (galareta, zarodniki, wilk, troll,
  ryk strażnika) i strefa muzyki „bagno” (na razie utwory lasu, ciszej); `KatalogDzwiekow.luau` przegenerowany.

## Jak zbudować (część B — po zwolnieniu Studio; tryb Edit; szacunki czasu)

```
# 1. offline (ok. 5 min): wszystko kod 0
python -B swiat/bagno_pas_gra/generuj_dane.py --sprawdz
python -B swiat/bagno_pas_gra/testy/test_bagna.py
python -B swiat/las_pas_gra/testy/test_pasa.py
python -B swiat/las_potwory/testy/test_logiki.py && python -B swiat/las_potwory/testy/test_styku.py
python -B swiat/test_walki2/testy/test_aktorow.py && python -B swiat/test_walki2/testy/test_przenikania.py
python -B swiat/bagno_pas/generuj.py && python -B swiat/bagno_pas/sprawdz.py
# 2. zapowiedź Bagna w lesie (1 min)
python -B tools/studio_mcp.py luau swiat/bagno_pas_gra/studio/usun_zapowiedz_bagna.luau
# 3. mapa Bagna (ok. 10–15 min: 31 paczek po 300 części) i streaming (2 min)
python -B tools/studio_buduj.py swiat/bagno_pas/czesci.json --paczka 300 --czekaj 20
python -B swiat/biom_las/studio_atrybuty.py --znaczniki swiat/bagno_pas/znaczniki.json
# 4. aktorzy Bagna w prototypie walki (2–3 min; TabelaAktorow bierze też bieżące dane bohaterów z dysku — uzgodnić
#    z agentami bohaterów) i skrypty prototypu (SerwerWalki2, ikony)
python -B swiat/test_walki2/zbuduj.py --tylko-aktorzy rechotek,bulgotnik,klodoklap,ropucha_z_chatka,straznik_topieli
python -B swiat/test_walki2/zbuduj.py --skrypty
# 5. las, teleport, dźwięk — skrypty (po 1 min; las może już wdrożyć agent stanu gracza)
python -B swiat/las_potwory/zbuduj.py --skrypty
python -B swiat/las_pas_gra/zbuduj.py --skrypty
python -B swiat/teleport_chmury/zbuduj.py --skrypty
python -B swiat/dzwiek_gra/zbuduj.py --skrypty
# 6. Bagno (1–2 min)
python -B swiat/bagno_pas_gra/zbuduj.py
# 7. zrzuty Edit (3 min)
python -B tools/studio_zrzuty.py swiat/bagno_pas/ujecia_swiat.json --wyj <folder poza repo> --czekaj 20 --rozmiar 1600
# 8. próba Bagna w Play (ok. 15–20 min; najpierw --sprawdz bez Studio), potem próba lasu (ok. 12 min)
python -B swiat/bagno_pas_gra/testy/proba_play.py --sprawdz
python -B swiat/bagno_pas_gra/testy/proba_play.py <folder poza repo>
python -B swiat/las_pas_gra/testy/proba_play.py <folder poza repo>
# 9. Studio zostaje w trybie Edit (próby same wyłączają Play)
```
Cofnięcie: `python -B swiat/bagno_pas_gra/zbuduj.py --usun`, `python -B tools/studio_buduj.py swiat/bagno_pas/czesci.json --usun`
(i ponowna budowa mapy lasu przywraca zapowiedź).

## Ustawienia przyjęte, do zmiany

- Poziomy stref 10–10 / 10–11 / 11–12 · 12–13 / 13 / 13–14 · 14–15 / 15 / 15–16 · Ropucha 16 · Strażnik 16
  (`generuj_dane.POZIOMY_STREF`); mnożnik biomu 1,14; cechy gatunków i ich liczby (`przeciwnicy.PRZEPISY`).
- „Gracz jest w Bagnie” (przelot, prawo wejścia) od x 2036 (2 st za bramą lasu); ratunek Bagna od bramy lasu (x 2034).
- Mgła Bagna (Atmosphere u gracza): gęstość 0,42, offset 0,08, haze 2,2, kolor 9AA58E, decay 5E6B4E; prostokąt
  u 934–1880, przejście 120 st; na granicy z lasem przejmuje mgłę lasu bez przebłysku.
- Strażnik Topieli i Ropucha wspólni dla serwera (jak w lesie); odrodzenie 120 / 150 s stałe.
- Teleport do Bagna: Pomost Przybycia (u 954), przelot czeka 2,4 s na koniec chmur.
- Muzyka Bagna: utwory lasu, głośność 0,3. Odgłosy potworów z arkusza efektów (bez nowych plików).

## Ryzyka

- **Nic nie sprawdzone w Studio** (część B): wejście bramą i chmurami, przelot, walki z nowymi modelami w odtwarzaczu
  (doskok, chwile trafień, kadr kamery przy Ropusze 10,8 i Strażniku 15,4 st), koszt widoków (582 bryły na pięć
  gatunków — dużo mniej niż las), mgła na oko, dwóch graczy, telefon.
- ~~Przy bramie lasu oba serwery pilnują tego samego miejsca~~ — zamknięte regułą pierwszeństwa (rozdz. „Jedno
  pilnowanie”); działa dopiero po wdrożeniu nowych skryptów lasu (`las_pas_gra/zbuduj.py --skrypty`).
- **Próba w Play nieuruchomiona** — kod Luau się parsuje, ale kolejność kroków, czasy i nazwy pól odtwarzacza
  (`pomijanie`, `faza`) sprawdzi dopiero pierwszy przebieg.
- **Ponowna budowa mapy lasu** (`swiat/las_pas`) przywraca `ZapowiedzBagna` z niewidzialną ścianą na Pomoście Bagna.
- **TabelaAktorow prototypu** buduje się z bieżących danych wszystkich aktorów z dysku — wdrożenie aktorów Bagna w
  czasie pracy agentów bohaterów może wysłać ich niedokończone dane.
- Strażnik Topieli jest trudny (wzorcowy gracz bez treningu wygrywa 20–36% o poziom wyżej) — zgodnie z kalkulatorem,
  ale bez treningu i petów długo.
- Bez spowolnienia w Bagnie (nacisk planu „spowolnienie i trucizna” zostaje tylko jako trucizna i osłony).

## Wybory dla ludzi

1. **Poziomy Bagna:** 10 → 16 z kalkulatora (dziś) czy 11 → 19 z planu Bagna?
2. **Własna umiejętność bagienna** (np. „Lepki język” ze spowolnieniem): dopisać do danych silnika i choreografii
   (zmiana `tools/walka` i prototypu) czy zostać przy istniejących?
3. **Zapowiedź Bagna w lesie:** usuwać skryptem po każdej budowie lasu czy dodać przełącznik w `swiat/las_pas/generuj.py`?
4. **Muzyka Bagna:** utwory lasu czy własne (Higgsfield, osobne zadanie)?
