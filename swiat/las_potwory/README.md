# Las Potworów — potwory w ruchu w Borze Pod Ukłonem

Ten pakiet sprawia, że po 16 strefach lasu `Workspace/BiomLas` chodzą potwory. Przy jednym graczu jest ich 35, przy
ośmiu 64, a przy dwudziestu 86. Do tego w Kamiennym Kręgu stoi Strażnik Gaju, który jest celem strefy. Gracz
podchodzi do potwora i naciska E (na telefonie stuka podpowiedź). Wtedy serwer liczy walkę silnikiem v2, a klient
pokazuje ją w przyjętym odtwarzaczu walki z `swiat/test_walki2/`, na arenie prototypu, razem z łupem. Pokonany
potwór znika, a z domu strefy wychodzi nowy.

Całość to jeden kontener `Workspace/LasPotwory` z atrybutem `Wygenerowane = true`, bez żadnych części. Poza Studio
serwer usuwa go w całości, zanim ktokolwiek dołączy. Pakiet działa tylko na czas testów w Studio i niczego nie
zapisuje. Kontrakt, odczytania zasad, lista do sprawdzenia w Studio i wynik recenzji są w [PROJEKT.md](PROJEKT.md).

## Wymagania w miejscu

- `Workspace/BiomLas` (las z `swiat/biom_las/`, środek (0; 0; −2000), obrót 180°). Bez niego serwer nie wystawia
  potworów i mówi o tym w Output.
- `Workspace/TestWalki2` (prototyp walki v2). Daje modele potworów i odtwarzacz walki. Bez niego potwory są
  kolorowymi bryłami, a walka jest niedostępna.

## Przed budową (bez Studio)

```
python -B swiat/las_potwory/testy/test_logiki.py
python -B swiat/las_potwory/testy/test_styku.py
python -B swiat/las_potwory/zbuduj.py --sucho
```

Wszystkie trzy mają skończyć się kodem 0. `test_styku.py` czyta bieżące pliki prototypu, więc uruchom go tuż przed
budową. Gdy zmienisz któryś plik lasu, najpierw uruchom `python -B swiat/las_potwory/generuj_dane.py`.

## Budowa, wymiana skryptów, usuwanie (Studio w trybie Edit)

```
python -B swiat/las_potwory/zbuduj.py              # buduje albo odbudowuje Workspace/LasPotwory
python -B swiat/las_potwory/zbuduj.py --skrypty    # tylko skrypty i moduły do istniejącego kontenera
python -B swiat/las_potwory/zbuduj.py --usun       # usuwa Workspace/LasPotwory
```

Gdy otwartych jest kilka okien Studio, dopisz `--studio <studio_id>`. Skrypt rusza tylko kontener z atrybutem
`Wygenerowane`, robi punkty historii (Ctrl+Z cofa całość) i niczego nie publikuje.

## Test w Studio (skrót)

W trybie Play Output ma pokazać w ciągu kilku sekund:

```
[LasPotwory] gotowy: 35 potworów w 16 strefach + Strażnik Gaju; zgodność logiki 70/70
[LasPotwory] klient gotowy: tryb aktorzy, potworów w Stan: 36
```

Haczyki testowe wołasz z paska poleceń:

- w widoku serwera: `workspace.LasPotwory.Sygnaly.SterowanieSerwera:Invoke("strefy" | "potwor", id | "zabij", id | "gracze", n | "zgodnosc")`;
- w widoku klienta: `workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan" | "walcz", id | "bohater", klasa, poziom)`.

Pełna lista z poleceniami i oczekiwanymi liczbami jest w PROJEKT.md, rozdz. 9.2, a miejsce na wyniki w rozdz. 9.3.

## Pliki

| Plik | Co to jest |
|---|---|
| `zrodla/SerwerPotworow.server.luau` | serwer: ruch 4 Hz, odradzanie, kontrola prośby o walkę, silnik v2 |
| `zrodla/KlientPotworow.client.luau` | klient: modele najbliższych potworów, tabliczki, podpowiedź E, panel bohatera |
| `zrodla/Stale.luau`, `zrodla/Logika.luau` | wspólne stałe; czysta matematyka ruchu (tylko serwer) |
| `zrodla/DanePotworow.luau` | dane stref w układzie świata, wygenerowane przez `generuj_dane.py` |
| `logika.py`, `generuj_dane.py` | lustro `Logika` w Pythonie; generator danych |
| `testy/test_logiki.py`, `testy/test_styku.py` | testy offline: logika, symulacja serwera, brzegi; punkty styku |
| `sprawdz_luau.py`, `zbuduj.py` | tania kontrola statyczna Luau; budowa w Studio |
| `UWAGI_S.md`, `UWAGI_K.md` | odczytania kontraktu programistów serwera i klienta |

## Stan w Studio (15.11.2026)

Pakiet działa w Roblox Studio w kontenerze `Workspace/LasPotwory` (zbudowany z tych źródeł, skrót danych `3f657732d08e`).
Pierwsze uruchomienie i poprawki błędów zrobił agent wdrożeniowy; jego praca urwała się na pomiarach kosztu (limit
użycia), więc lista kontrolna z `PROJEKT.md` rozdz. 9.2 **nie jest przejdzona w całości**. Krótką próbę końcową zrobiono
skryptem `testy/proba_play.py` (Play, zrzuty w `klatki/`):

- serwer: „gotowy: 35 potworów w 16 strefach + Strażnik Gaju”, zgodność logiki 70/70, 36 wpisów w `Stan`;
- klient: tryb „aktorzy”, po 14 s przy bramie lasu 4 widoki slime'ów (460 części), wszystkie animowane, 0 błędów;
  przy Strażniku 3 widoki (2216 części);
- tabliczki poziomu nad potworami („POZ. 1”, „POZ. 10”), plakietka wybranego bohatera u góry ekranu;
- podpowiedź przy Strażniku Gaju: włączona, gdy postać stoi obok;
- walka zaczęta z lasu: serwer przyjął prośbę, policzył walkę (Zwiadowca poz. 10 kontra Strażnik Gaju poz. 10, przegrana
  w 18 turach, 30,6 s), odtwarzacz pokazał ją na arenie prototypu z podestem (łata P1) i oknem wyniku bez przycisku
  „jeszcze raz” (łata P2);
- prośba o walkę z potworem, który odszedł dalej niż 8 studów: serwer odmawia (potwór zostaje wolny) — zgodnie z D-016.

Czego ta próba NIE sprawdziła: zamknięcia okna wyniku i powrotu sterowania, zniknięcia pokonanego potwora i odrodzenia,
powrotu Strażnika po 120 s, skalowania liczby potworów, widoku na telefonie, kosztu na klatkę, wilków i Muchomorników.

Uwagi z próby:
- Slime idzie 6 studów na sekundę, więc trzeba do niego podbiec; podpowiedź gaśnie, gdy odejdzie dalej niż 8 studów.
- Okno wyniku trzyma walkę otwartą, dopóki gracz nie kliknie ZAMKNIJ; po dłuższej chwili tło areny znika zza okna
  (arena leży ponad 2000 studów od lasu i wypada ze streamingu).
- Zrzuty i filmy wymagają włączonego ekranu: przy wygaszonym monitorze Studio nie rysuje obrazu i `screen_capture`
  wisi. `testy/proba_play.py` budzi ekran przed każdym zrzutem (`swiat/test_walki2/testy/czuwanie.py`).
