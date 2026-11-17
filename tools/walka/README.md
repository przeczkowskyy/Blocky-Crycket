# Silnik walki v3 — narzędzia (Python)

Silnik walki gry liczy **serwer** w Luau (`src/server/Walka/`), a klient tylko odtwarza dziennik
(`src/shared/Walka/Dziennik.luau`). Ten folder to **dosłowny port w Pythonie** (ten sam generator liczb, ta sama
kolejność rzutów, te same zaokrąglenia), jedno źródło danych, testy, tabela balansu, model tempa i sprawdzenie
zgodności z Luau (w Studio albo bez Studio — małym interpreterem Luau).
Zasady v3 (mana, statusy, tarcza procentowa, blok każdej klasy, limit Pancerza, pasywki, klasy potworów) i wyniki:
`tools/walka/ZMIANY_SESJA_1611.md`. Opis silnika v2 dla zespołu: `B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md`.

Wszystko działa na samej bibliotece standardowej Pythona. Uruchamiaj z `-B` (bez plików `.pyc`).

## Pliki

| Plik | Co robi |
|---|---|
| `dane_walki.json` | **jedyne źródło danych**: stałe wzorów, klasy (gracza i potworów), modyfikatory (zamknięta lista z granicami), efekty, zaklęcia broni, umiejętności aktywne, pasywne, pasywki broni, przeciwnicy lasu z łupem |
| `generuj_dane.py` | z `dane_walki.json` robi moduł Luau `src/server/Walka/Dane.luau` (nie edytuj go ręcznie) |
| `silnik.py` | port silnika; sekcje odpowiadają modułom Luau (Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik) |
| `dziennik.py` | port `Dziennik.sprawdz` — niezmienniki dziennika v3 (także mana i stosy) |
| `wzorcowe.py` | wzorcowe postacie (te same co w v2 i w prototypie Studio) i buildy (pod manę, zwykłe ataki, unik, Pancerz i blok, truciznę) |
| `balans.py` | tabela balansu (Markdown, części a–k): klasy z potworami, klasa na klasę, wartość punktu statystyki, użycia umiejętności, buildy, blok 25% / 50% / 0%, sloty, nabijanie jednej statystyki, wysokie poziomy, Pancerz, wskrzeszenie |
| `tempo.py` | model tempa: las gracz po graczu prawdziwym silnikiem i ogólny model biomów 1–7 (propozycja liczb doświadczenia i poziomów) |
| `progresja.py` | kalkulator balansu 17.11 (propozycja liczb): Pancerz a obrażenia potworów w ośmiu biomach, drzewko Twierdzy, ewolucja petów, Gemy na drzewka, pytanie 40 (Wojownik z tarczą i unikiem), wzór przyrostu z mini-gier Training Center; wynik, założenia i wybory: `BALANS_1711.md` |
| `test_progresja.py` | szybkie testy kalkulatora (drzewka z `src/shared/SkillTreeData.luau`, zgodność z `tempo.py`, wzór treningu, warianty zasad z pytania 40, potwory biomu) |
| `wzorce.py`, `wzorce.json` | wzorce zgodności: podpisy dzienników z Pythona dla ustalonych wejść i ziaren, złe wejścia |
| `zgodnosc_studio.py` | liczy te same walki modułami Luau i porównuje z wzorcami: w Studio (tylko odczyt) albo `--offline` |
| `luau_mini.py` | mały interpreter **podzbioru** Luau w Pythonie (tylko do `--offline` i testów; nie zastępuje Studio) |
| `test_walki.py` | testy (unittest) |

## Jak uruchomić

```
python -B -m unittest discover -s tools/walka -p "test_*.py"     # wszystkie testy (kilka minut)
python -B tools/walka/balans.py                                  # tabela balansu, 2000 ziaren na parę, poziomy 1–10, 12, 15, 20
python -B tools/walka/balans.py --start 50001                    # to samo na innych ziarnach (kontrola dopasowania)
python -B tools/walka/balans.py --ziaren 500 --czesci a,b --md balans.md   # szybciej, wybrane części, z zapisem
python -B tools/walka/tempo.py --md tempo.md                     # model tempa (las + biomy 1–7)
python -B tools/walka/progresja.py --md wynik.md                 # kalkulator 17.11: sześć rachunków (kilka minut)
python -B tools/walka/progresja.py --czesci 2,3,4                # tylko Twierdza, pety i Gemy (kilka sekund)
python -B tools/walka/silnik.py --klasa mag --wrog straznik_lasu --poziom 5 --ziarno 7   # jedna walka (JSON)
python -B tools/walka/zgodnosc_studio.py --offline               # Luau kontra Python bez Studio (interpreter luau_mini)
```

`balans.py` liczy domyślnie w 3 procesach (`--procesy 1` — w jednym; na zajętym komputerze używaj `--procesy 1`).
Silnik odrzuca nieznane pola wejścia (postać, broń, tarcza, przeciwnik) błędem „Walka: nieznane pole …” — literówka
w nazwie pola (np. `premia` zamiast `premie`) nie przechodzi po cichu. Ziarno walki musi być liczbą całkowitą od 0 do
2^31 − 1 (oba porty odrzucają inne). Serwer, który złoży ziarno np. z UserId i licznika, musi je sprowadzić do tego
przedziału (np. resztą z dzielenia przez 2147483647).

Testy pilnują m.in.: równości klas (U10) na poziomach 1–10, 12, 15 i 20 — różnica klas przy tym samym potworze
najwyżej 7 pp, pojedynki klasa na klasę 45–55%; buildów (każdy 45–55% z wzorcową swojej klasy; „swój” i „nie
swój” potwór — tylko dla buildów z listy `BUILDY_ROZNE`, patrz ZMIANY_SESJA_1611.md); wskrzeszenia (propozycja D-094:
raz na walkę, tylko po nokaucie, tylko ze slotu); długości walki (U7) — każde zdarzenie trwa swój
naturalny czas, ta sama akcja w 1. i 50. turze daje te same obrażenia; many, rotacji slotów i statusów — niezależną
„wyrocznią”, która odtwarza każdy dziennik z reguł zapisanych w teście; zgodności Luau z Pythonem w interpreterze.

## Jak dodać przeciwnika, umiejętność, pasywkę albo modyfikator

1. Dopisz wpis w `dane_walki.json`:
   - **przeciwnik** — do listy `przeciwnicy`: `id`, `nazwa`, `ranga` (`zwykly` / `rzadki` / `straznik`; tylko interfejs
     i łup), `kraina`, `charakter`, `wyglad`, **`klasa`** (klasa gracza albo klasa z `klasy_potworow`), punkty
     `statystyki` (pary `[baza, na_poziom]` dla sześciu statystyk), `bron` i `pancerz_przedmiotow` (pary), `tarcza`
     (szansa bloku tarczy, zwykle 0), `modyfikatory` (np. więcej życia, słabszy cios — klucze z listy `modyfikatory`),
     `umiejetnosci` (aktywne i pasywne z `klasa: "potwor"`) i `lup`. Potwór przechodzi przez TEN SAM wzór co postać.
   - **umiejętność aktywna** — do `umiejetnosci`: `klasa`, `cel` (`wrog` / `sam`), `koszt_many` (1..mana_maks),
     `mnoznik`, `rodzaj`, `premia_krytyka`, `czas` (setne sekundy) i `efekty` (lista `{efekt, szansa}`). Dopisz ją do
     listy `umiejetnosci` klasy.
   - **pasywna umiejętność do slotu** — do `pasywne`: `nazwa`, `klasa`, `opis`, `modyfikatory`; dopisz do `pasywne`
     klasy. **Pasywka broni** — do `pasywki_broni` (`klasa` = "" dla każdej klasy).
   - **efekt** — wszystkie pola z `test_dane_spojne` (typy: `obrazenia_w_czasie`, `spowolnienie`, `ogluszenie`,
     `zdarcie`, `oslona`, `wzmocnienie`). Nowy **modyfikator** — wpis `{id, min, max, opis}` na liście
     `modyfikatory` i obsługa w `bojowe` (oba porty).
2. `python -B tools/walka/generuj_dane.py` — odświeża `Dane.luau`.
3. `python -B tools/walka/balans.py --ziaren 500` — sprawdź, czy klasy i buildy dalej są równe.
4. `python -B tools/walka/wzorce.py` — odświeża wzorce zgodności (test pilnuje, że są aktualne).
5. Testy, w tym `zgodnosc_studio.py --offline`. Nowy **typ** efektu albo zmiana wzoru to zmiana kodu w OBU językach
   (`silnik.py` i moduły Luau) — wtedy trzeba też przejść sprawdzenie zgodności w Studio. Nowa umiejętność albo nowy
   efekt potrzebuje też choreografii i wyglądu w prototypie (`swiat/test_walki2`, patrz jego README).

## Jak sprawdzić zgodność Luau z Pythonem

```
python -B tools/walka/zgodnosc_studio.py --offline          # bez Studio: interpreter luau_mini (podzbiór Luau)
python -B tools/studio_mcp.py studios                       # lista okien Studio (id, placeId)
python -B tools/walka/zgodnosc_studio.py --studio <id>      # Studio w trybie Edit (nie Play), tylko odczyt
python -B tools/walka/zgodnosc_studio.py --sucho            # bez Studio: tylko złóż kod i pokaż rozmiar
```

Skrypt czyta źródła modułów z repozytorium jako tekst (nie potrzebuje Rojo), składa je w jeden kawałek kodu i wysyła
przez `execute_luau` do okna wybranego przez `swiat/test_walki_roblox/cel_studio.py` (jedno okno albo `--studio`;
zawsze placeId gry, sprawdzany jeszcze raz w Studio przez `game.PlaceId`). W Studio niczego nie tworzy, nie zmienia,
nie zapisuje i nie publikuje. Wynik: powtarzalność, niezmienniki, zgodność z portem (np. „N/N identycznych
dzienników”) i odrzucanie złych wejść. Przy różnicy pokazuje pierwszy niezgodny podpis z Luau i z Pythona.

`--offline` robi te same cztery sprawdzenia w interpreterze `luau_mini.py`. To podzbiór Luau napisany w Pythonie
(liczby double, ta sama kolejność działań), więc łapie błędy portu (kolejność rzutów, nazwy pól, indeksy), ale NIE
sprawdza kompilatora Luau ani zachowania w prawdziwym Studio — po zmianie silnika trzeba też przejść tryb ze Studio.
