# Uwagi programisty S (serwer): etap A

*15.11.2026. Kontrakt: `PROJEKT.md`. Ten plik opisuje tylko połowę serwerową: co powstało, jak to sprawdziłem, jak
odczytałem niejasne miejsca kontraktu i czego nie jestem pewien. Pisałem offline, bez Studio. Luau nie było uruchamiane.*

## Co napisałem

| Plik | Co to jest |
|---|---|
| `logika.py` | Lustro modułu `Logika` w Pythonie: 15 funkcji z tabeli 3.7, bez zależności. |
| `generuj_dane.py` | Generator `zrodla/DanePotworow.luau` (format 2.4, kontrole 2.1, z09 przez `korytarz_labiryntu`, Strażnik w (0; 32; −373) lasu). Ma tryby `--sprawdz` i `--wyjscie PLIK`. |
| `zrodla/DanePotworow.luau` | Wynik generatora. Skrót `3f657732d08e`, 16 stref i Strażnik, współrzędne świata. |
| `zrodla/Logika.luau` | Te same 15 funkcji co `logika.py` oraz `sprawdzPrzypadki()` z 70 przypadkami z tabeli 3.7a. |
| `zrodla/SerwerPotworow.server.luau` | Serwer. Kolejność jak w rozdz. 12: strażnik Studio (poza Studio niszczy kontener), kontrola BiomLas, kopie szablonów, start, ruch 4 Hz z rezerwacją, odradzanie co 1 s, `OnServerInvoke` (kontrole 1–11), koniec zajętości i `PlayerRemoving`, haczyk `SterowanieSerwera`, atrybuty. |
| `testy/test_logiki.py` | Testy z rozdz. 9.1, punkty 1–7, oraz test zgodności tabeli przypadków w `Logika.luau` z Pythonem. |

Tabela stref z generatora zgadza się co do liczby z dodatkiem A: L, zapasy, okrążenia, cele 35 / 45 / 64 / 86
i czasy odrodzeń.

## Jak sprawdziłem

- `python -B swiat/las_potwory/testy/test_logiki.py` przechodzi: 10 testów w około 5 s. Sprawdzają one:
  - wszystkie 70 przypadków z 3.7a;
  - czy `Logika.luau` ma te same 15 funkcji i te same 70 opisów i wyników (test czyta plik Luau);
  - symulację każdej strefy przez 30 min dla ziaren 3 i 11. Najmniejsza luka wyszła dokładnie 25,000, nikt się nie
    cofa, a w każdej strefie było około 40–60 odrodzeń. Próba kontrolna z wejściem bez rezerwacji daje luki 21,7,
    więc test naprawdę łapie błąd;
  - pojemność, sumy celów, geometrię (smycz r + 10, strefy spokoju, Serce, domy 35–50, przedpole 6, z09: 9 punktów
    i L = 475,11), przeliczenie las → świat oraz determinizm generatora (dwa uruchomienia dają te same bajty,
    `--sprawdz` przechodzi, w pliku nie ma daty, ścieżek ani BOM).
- `python -B swiat/las_potwory/generuj_dane.py --sprawdz` daje kod 0.
- `python -B swiat/las_potwory/sprawdz_luau.py` (narzędzie K) daje „5 plików, OK”, a `--test` daje „samosprawdzenie: OK”.
- `python -B swiat/las_potwory/zbuduj.py --sucho` (narzędzie K, tylko tryb na sucho) daje „sucho: OK”. Plan budowy
  ma 12 modułów i skryptów.
- Przeczytałem cały `SerwerPotworow.server.luau` i `Logika.luau` od góry do dołu. Sprawdziłem bilans bloków, nazwy
  zmiennych, przypadki nil i nazwy API Roblox. Sprawdziłem też, czy pola `Stale` są takie jak w `zrodla/Stale.luau`
  od K oraz czy kolejność atrybutów pasuje do czekania klienta (`StanBiomu`, potem `SzablonyGotowe`, a na końcu
  `SerwerGotowy`).

## Odczytania kontraktu (najprostsze; opisane też w nagłówkach plików)

1. **yaw = atan2(0 − dx, 0 − dz).** Zapis `atan2(−dx, −dz)` z kontraktu przy dx = 0 daje −0, a wtedy ruch w +Z
   wychodzi −π. Przypadek `punktTrasy(T1, 15)` oczekuje +3,1416, więc piszemy 0 − dx. Kierunek jest ten sam, różni się
   tylko liczba.
2. **minal: „bliżej niż 0,5” znaczy ≤ 0,5.** Przypadek `minal(10, 12.5, 13, 100) = true` tego wymaga, bo 13 − 12,5 to
   dokładnie 0,5.
3. **krokGrup w Luau zwraca drugą wartość `zbiezne`.** Na jej podstawie serwer robi warn raz na strefę. Lustro
   w Pythonie zwraca tylko listę. Zachowanie przy braku zbieżności jest takie samo: nikt się nie rusza.
4. **Zajętość nie zmienia stanu wewnętrznego.** Pole `zajety = { gracz, wynik, koniec }` stoi obok stanu wychodzi /
   czeka / chodzi. Po przegranej potwór po prostu wraca do swojego stanu. Atrybut `Stan` przy zajętości to `"zajety"`.
5. **Zegar.** Czas zajętości, kolejki, blokady sesji i `StraznikWraca` liczy `workspace:GetServerTimeNow()`, czyli
   ten sam zegar, którego odtwarzacz używa dla `nastepnaOd`. Odstęp między prośbami liczy `os.clock()`, jak w
   `SerwerWalki2`.
6. **Strażnik idzie tą samą ścieżką kodu co inne potwory.** ~~Jego jedyny „dom” to miejsce walki, więc zasada
   „dom wolny, gdy nikt nie stoi bliżej niż 18” też go dotyczy.~~ **Zmienione przy recenzji (15.11):** Strażnik nie
   ma domu w `potwory.json`, więc blokada domu go nie dotyczy (blokada 0). Wraca dokładnie po 120 s, także gdy
   zwycięzca stoi obok, a `StraznikWraca` jest zawsze prawdziwy. Tester w 9.2 p. 10 nie musi odchodzić.
7. **Przy złym biomie `SerwerGotowy` zostaje false**, a powód jest w `StanBiomu`. Klient K przerywa czekanie na
   `StanBiomu`, więc to do siebie pasuje. Zdalna funkcja i haczyk działają: odpowiadają `zly_wybor` i zwracają puste
   strefy. Przy `TestBezBiomu = true` `StanBiomu` ma wartość `"ok"`, a w Output pojawia się warn, że kontrolę pominięto.
8. **`skrot`.** To SHA-1 z kanonicznego JSON czterech struktur: potwory.json, znaczniki.json, uklad.json i czwartej
   `{"plyta": rekord Płyty, "przeciwnicy": lista id z dane_walki.json}`. Z dwóch dużych plików bierzemy więc tylko to,
   co czytamy. Dzięki temu nowy krzak w lesie nie zmienia skrótu.
9. **`wezel` domu to numer punktu trasy.** W z09 trasa ma 9 punktów, a węzły walki 1 i 3 mają numery 1 i 9. Najbliższy
   węzeł szukamy wśród węzłów walki z znaczniki.json, a nie wśród punktów korytarza. Lista `s` ma jedną wartość, gdy
   węzeł jest na końcu trasy tam i z powrotem. Tak jest dla wszystkich trzech domów z09.
10. **Wymiary wilka** to `{ 7.7, 4.4, 7.7 }`, bo w `rozmiary` jest tylko `dl`. Brakujący wymiar poziomy bierzemy z
    drugiego. To ma znaczenie tylko dla bryły zastępczej, bo `promien` = 3,85 jest zgodny z kontraktem.
11. **Haczyk `"strefy"`.** Pole `kolejka` to lista sekund do kolejnych odrodzeń, a nie sama liczba wpisów (liczba to
    `#kolejka`). Doszły pola `minLukaTeraz` i `wychodzacy`. `minLuka` to najmniejsza luka od startu; `math.huge`
    oznacza, że w strefie nie ma dwóch grup. Haczyk `"potwor"` zwraca też `s`, `pozycja`, `stanAtrybutu` i `zajetyPrzez`.
12. **Kolejka odrodzeń** w jednej sekundzie obsługuje wszystkie dojrzałe wpisy, każdy w następnym wolnym domu
    (karuzela). Wpis bez wolnego domu czeka do następnej sekundy.
13. **Zasady słowne** (zasięg E 8, najmniej 10 s, skracanie 0,15) generator przepisuje jako liczby. Najpierw sprawdza
    jednak, że teksty w `potwory.json` wciąż je zawierają. Jeśli nie, przerywa.

## Do uzgodnienia z połową K i z recenzentem

- **Brak sprzeczności w punktach styku.** Wszystkie 9 atrybutów stanu serwer ustawia dosłownie
  (`SetAttribute("Pozycja", …)` itd.), więc reguła 5 z `sprawdz_luau.py` przechodzi. Klient i serwer tak samo mierzą
  wysokość (Y `HumanoidRootPart` minus Y `Pozycja`, ≤ 6) i tak samo liczą zasięg w poziomie. Serwer dodaje zapas 6.
- **Kontrakt wspomina „tylko wartości z listy”, a my potrzebowaliśmy dwóch odstępstw od zapisu wzorów (punkty 1 i 2
  wyżej).** Tabela 3.7a z kontraktu jest jednak spełniona co do joty. Projektant mógłby dopisać „≤ 0,5” i
  „atan2(0 − dx, 0 − dz)” w tabeli 3.7.
- **Czekanie na szablony.** Gdy w miejscu nie ma `TestWalki2`, serwer czeka na niego do 10 s, a potem jeszcze do
  10 s na `Aktorzy`, i dopiero wtedy stawia potwory. Klient po 15 s przechodzi w tryb zastępczy. Potwory i tak
  przychodzą później atrybutami, więc nic się nie psuje, ale start jest wolniejszy.

## Czego nie jestem pewien (sprawdzić w Studio)

- Czy `math.atan2` działa w tym Luau. Powinno, bo Luau je ma, mimo że Lua 5.3 go usunęło. Gdyby nie działało,
  `ZgodnoscLogiki` pokaże błąd przypadków `punktTrasy`, a serwer wywróci się przy pierwszym ruchu.
- Czy `Orientation.Y` Płyty to +180 czy −180. Kontrola bierze wartość bezwzględną, więc oba przechodzą. Gdyby Studio
  rozłożyło obrót inaczej, na przykład jako (180; 0; 180), kontrola zgłosi `zle_polozenie` z liczbą w Output.
- Czy szablony aktorów mają `Archivable = true`. Gdy nie, `Clone()` zwraca nil, warn wymieni brakujące klucze, a
  klient przejdzie w tryb zastępczy.
- `kontener.Destroying` usuwa kopię szablonów, gdy ktoś w trakcie Play skasuje kontener. Nie wiem, czy połączenie
  zdąży zadziałać, gdy niszczony jest też sam skrypt. Bez tego kopia i tak znika po zatrzymaniu Play.
- Czy `Configuration` w Workspace z atrybutami zmienianymi 4 razy na sekundę dochodzi do klienta przy streamingu.
  To ryzyko z rozdz. 10.
- `RequestStreamAroundAsync` jest w `pcall`, jak w prototypie. Nie wiem, ile trwa w lesie (gracz stoi 2000+ studów
  od areny). Prośba czeka na nie przed odpowiedzią, ale potwór jest już wtedy zajęty.
- Wataha z09 na trasie tam i z powrotem zawraca w s = 0 i s = Lp na parametrze. Przez chwilę członkowie mijają się
  wtedy w miejscu. Wygląda to jak przejście przez siebie i to tylko kosmetyka do obejrzenia.
- Odcinek dom → przedpole sprawdzam offline tylko pod kątem stref spokoju i Serca, a nie ścian labiryntu czy głazów.
  Domy z09 („kąty labiryntu”) mogą prowadzić przez jeżyny. Widoki nie mają kolizji, więc to tylko wygląd.

## Dla osoby wdrażającej (tylko po stronie serwera)

1. Przed budową uruchom `python -B swiat/las_potwory/testy/test_logiki.py` i `python -B swiat/las_potwory/zbuduj.py --sucho`.
2. W Play solo Output ma pokazać w ciągu 5 s:
   `[LasPotwory] gotowy: 35 potworów w 16 strefach + Strażnik Gaju; zgodność logiki 70/70`.
   Atrybuty mają wynosić: `ZgodnoscLogiki = "OK 70/70"`, `Potworow = 36`, `StanBiomu = "ok"`, `SzablonyGotowe = true`.
3. Haczyk wołasz z paska poleceń w widoku serwera:
   `print(workspace.LasPotwory.Sygnaly.SterowanieSerwera:Invoke("strefy").z01)`, `…:Invoke("potwor", "z01-1")`,
   `…:Invoke("zabij", "z01-1")` (test odradzania), `…:Invoke("gracze", 8)` / `…:Invoke("gracze", nil)`,
   `…:Invoke("zgodnosc")`.
4. Prędkość (9.2 p. 4) sprawdzasz przez porównanie `grupy[k][1]` (czoło `s`) z dwóch wywołań `"strefy"` w odstępie
   10 s. Odczyt jest na pętli parametru, więc przez punkt `L` licz modulo.
5. Żeby zobaczyć każde odrodzenie i wejście na pętlę w Output, ustaw `Stale.GADATLIWY = true` w module `Moduly/Stale`
   (tylko na czas testu).
6. Na Strażnika (9.2 p. 10): po recenzji wraca po 120 s także wtedy, gdy stoisz obok (punkt 6 odczytań).
