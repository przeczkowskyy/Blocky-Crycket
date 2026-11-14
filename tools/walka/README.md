# Silnik walki v2 — narzędzia (Python)

Silnik walki gry liczy **serwer** w Luau (`src/server/Walka/`), a klient tylko odtwarza dziennik
(`src/shared/Walka/Dziennik.luau`). Ten folder to **dosłowny port w Pythonie** (ten sam generator liczb, ta sama
kolejność rzutów, te same zaokrąglenia), jedno źródło danych, testy, tabela balansu i sprawdzenie zgodności w Studio.
Opis zasad i wzorów dla zespołu: `B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md`.

Wszystko działa na samej bibliotece standardowej Pythona. Uruchamiaj z `-B` (bez plików `.pyc`).

## Pliki

| Plik | Co robi |
|---|---|
| `dane_walki.json` | **jedyne źródło danych**: stałe wzorów, klasy, umiejętności, efekty, zaklęcia broni, przeciwnicy lasu z łupem |
| `generuj_dane.py` | z `dane_walki.json` robi moduł Luau `src/server/Walka/Dane.luau` (nie edytuj go ręcznie) |
| `silnik.py` | port silnika; sekcje odpowiadają modułom Luau (Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik) |
| `dziennik.py` | port `Dziennik.sprawdz` — niezmienniki dziennika |
| `wzorcowe.py` | wzorcowe postacie: równa pula punktów, ta sama broń i pancerz z przedmiotów dla każdej klasy |
| `balans.py` | tabela balansu (Markdown): klasy przeciw potworom, klasa na klasę, wrażliwość statystyk, Wojownik z tarczą i unikiem |
| `wzorce.py`, `wzorce.json` | wzorce zgodności: podpisy dzienników z Pythona dla ustalonych wejść i ziaren |
| `zgodnosc_studio.py` | liczy te same walki w Studio modułami Luau i porównuje z wzorcami (tylko odczyt) |
| `test_walki.py` | testy (unittest) |

## Jak uruchomić

```
python -B -m unittest discover -s tools/walka -p "test_*.py"     # wszystkie testy (ok. 1,5–2 min)
python -B tools/walka/balans.py                                  # tabela balansu, 2000 ziaren na parę, poziomy 1–10, 12, 15, 20
python -B tools/walka/balans.py --start 50001                    # to samo na innych ziarnach (kontrola dopasowania)
python -B tools/walka/balans.py --ziaren 500 --md balans.md      # szybciej, z zapisem do pliku
python -B tools/walka/silnik.py --klasa mag --wrog straznik_lasu --poziom 5 --ziarno 7   # jedna walka (JSON)
```

Ziarno walki musi być liczbą całkowitą od 0 do 2^31 − 1 (oba porty odrzucają inne: przy większych liczbach Luau
i Python liczyłyby inny stan generatora). Serwer, który złoży ziarno np. z UserId i licznika, musi je sprowadzić do
tego przedziału (np. resztą z dzielenia przez 2147483647).

Testy pilnują m.in.: równości klas (U10) na poziomach 1–10, 12, 15 i 20 — różnica klas przy tym samym potworze
najwyżej 7 pp, pojedynki klasa na klasę 45–55%; długości walki (U7) — każde zdarzenie trwa swój naturalny czas
z danych, ta sama akcja w 1. i 50. turze daje te same obrażenia, późne ciosy nie są mocniejsze od wczesnych,
bezpiecznik tur nie zadziałał ani razu.

## Jak dodać przeciwnika albo umiejętność

1. Dopisz wpis w `dane_walki.json`:
   - **przeciwnik** — do listy `przeciwnicy`: `id`, `nazwa`, `ranga` (`zwykly` / `rzadki` / `straznik`; to tylko
     informacja dla interfejsu i łupu — ranga nie zmienia zasad walki), `kraina`, `charakter`, `wyglad` (jedno zdanie
     do modelu), `rodzaj_ciosu`, pary `[baza, na_poziom]` dla `zycie`, `cios`, `pancerz`, `odpornosc`, szanse `unik`,
     `krytyk`, `mnoznik_krytyka`, `blok` (zawsze 0 — blok to tarcza gracza), `moc`, `umiejetnosci` (identyfikatory
     z `klasa: "potwor"`) i `lup`. Shard Ewolucji (`szansa_sharda` > 0) tylko u strażnika; pola z jajkiem nie ma.
   - **umiejętność** — do słownika `umiejetnosci`: `klasa`, `cel` (`wrog` albo `sam`), `odnowienie` (co ile własnych
     akcji), `mnoznik` (× cios; > 0 dla umiejętności na przeciwnika), `rodzaj`, `premia_krytyka`, `czas` (setne
     sekundy animacji) i `efekty` (lista `{efekt, szansa}`; efekty opisuje słownik `efekty`). Umiejętność klasy dopisz
     też do listy `umiejetnosci` tej klasy.
2. `python -B tools/walka/generuj_dane.py` — odświeża `Dane.luau`.
3. `python -B tools/walka/balans.py --ziaren 500` — sprawdź, czy klasy dalej są równe.
4. `python -B tools/walka/wzorce.py` — odświeża wzorce zgodności (test pilnuje, że są aktualne).
5. Testy. Nowy **typ** efektu albo zmiana wzoru to zmiana kodu w OBU językach (`silnik.py` i moduły Luau) — tylko
   wtedy trzeba przejść sprawdzenie zgodności w Studio.

## Jak sprawdzić zgodność Luau z Pythonem w Studio

Kod Luau nie był jeszcze uruchomiony (na komputerze nie ma interpretera Luau, a Studio było zajęte).
Sprawdzenie robi `zgodnosc_studio.py`:

```
python -B tools/studio_mcp.py studios                       # lista okien Studio (id, placeId)
python -B tools/walka/zgodnosc_studio.py --studio <id>      # Studio w trybie Edit (nie Play), tylko odczyt
python -B tools/walka/zgodnosc_studio.py --sucho            # bez Studio: tylko złóż kod i pokaż rozmiar
```

Skrypt czyta źródła modułów z repozytorium jako tekst (nie potrzebuje Rojo), składa je w jeden kawałek kodu i wysyła
przez `execute_luau` do okna wybranego przez `swiat/test_walki_roblox/cel_studio.py` (jedno okno albo `--studio`;
zawsze placeId gry, sprawdzany jeszcze raz w Studio przez `game.PlaceId`). W Studio niczego nie tworzy, nie zmienia,
nie zapisuje i nie publikuje. Wynik: powtarzalność, niezmienniki, zgodność z portem (np. „496/496 identycznych
dzienników”) i odrzucanie złych wejść. Przy różnicy pokazuje pierwszy niezgodny podpis z Luau i z Pythona.
