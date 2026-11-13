---
status: propozycja
tags: [technika, telemetria, analityka]
---
# Telemetria gry

> [!info] W skrócie
> Moduł w grze (`src/server/Telemetria`) liczy na serwerach **same liczby zbiorcze** — sesje i ich długość, graczy naraz, wydane Robuxy, błędy skryptów, serwery na żywo — i co 5 minut zapisuje je godzina po godzinie do Data Store. Panel zespołu czyta je kluczem Open Cloud **tylko do odczytu** i pokazuje w zakładce Analityka → „Telemetria gry”. **Dziś wszystko jest wyłączone**: gra jest prywatna, moduł nie jest uruchamiany przez żaden skrypt, a na żadnym komputerze nie ma klucza. Włączenie to decyzja Game Directora (kroki niżej). Kod powstał 13.11.2026 na zlecenie Karola — to propozycja, nie kanon.

## Po co
- Publiczne API Roblox (kafle w Analityce) daje tylko „gracze teraz”, wizyty i oceny, i to **dopiero dla gry publicznej**. Wbudowana analityka Roblox (Creator Dashboard) rusza od 10 DAU z ostatnich 7 dni (zob. [[Rynek Roblox i konkurencja]]).
- Telemetria działa od pierwszego testera: ile trwa sesja, ile osób odpada w pierwszej minucie, który produkt się sprzedaje, który błąd skryptu wraca najczęściej i czy serwer padł z braku pamięci — godzina po godzinie, na telefonie, bez otwierania Creator Dashboard.

## Co zbiera
Jeden wpis Data Store na godzinę zegarową UTC (klucz `g_RRRRMMDD_GG`, magazyn `BC_Telemetria_v1`). Wiele serwerów dopisuje się do tego samego wpisu przez `UpdateAsync`.

| Liczba | Skąd w grze |
|---|---|
| sesje rozpoczęte i zakończone, suma sekund gry, rozkład długości (do 1, 5, 15, 30, 60 min, dłużej) | `Players.PlayerAdded` / `PlayerRemoving` |
| gracze naraz: co minutę (suma ze wszystkich serwerów) i szczyt jednego serwera | próbka co minutę |
| Robuxy i liczba zakupów na produkt (id, nazwa produktu) | `Telemetria.zakup(…)` wołane z obsługi paragonów |
| błędy skryptów: liczba i do 40 najczęstszych sygnatur z krótkim komunikatem | `ScriptContext.Error` + `Telemetria.blad(…)` |
| serwery: starty, zapisy, powód zamknięcia (`ServerEmpty`, `OutOfMemory`…) | `BindToClose(closeReason)` |
| lejek wejścia (krok 1–100: ilu graczy doszło) i własne liczniki zdarzeń | `Telemetria.lejek(…)`, `Telemetria.zdarzenie(…)` |

Osobno każdy serwer co minutę odnawia wpis „na żywo” w sorted mapie Memory Store `BC_Telemetria_Serwery` (klucz = `JobId`, wygasa po 3 minutach): liczba graczy, czas działania, pamięć serwera w MB, klatki na sekundę, licznik błędów. Wpis `stan` w Data Store mówi panelowi, że moduł w ogóle był włączony.

## Czego NIE zbiera (prywatność dzieci)
Gra jest dla dzieci, a repozytorium jest publiczne, dlatego moduł zapisuje tylko liczby:
- **żadnych nazw graczy, DisplayName ani UserId** w zapisie zbiorczym; kto jest na serwerze i od kiedy, wie tylko pamięć serwera (do policzenia długości sesji) i zapomina to po wyjściu gracza;
- z komunikatów błędów wycinamy nazwy graczy obecnych na serwerze (i tych, którzy wyszli w ostatnich 10 minutach), identyfikatory GUID i liczby od 5 cyfr (UserId, numery assetów) — zostaje np. `Server.Walka:42: attempt to index nil with 'Zdrowie'`; stos wywołań nie jest zapisywany;
- żadnych wiadomości czatu, adresów, urządzeń, lokalizacji ani historii pojedynczego gracza;
- nazwy produktów, kroków lejka i zdarzeń podaje kod gry — **nie wolno** wstawiać do nich danych gracza;
- jeśli ktoś przekaże gracza do `zdarzenie`/`lejek`, idzie on tylko do wbudowanej `AnalyticsService` Roblox (tak samo, jak robi to każda gra), nie do naszego zapisu.

W Studio moduł domyślnie pisze **do pamięci** (nic nie trafia do prawdziwych danych), a zdarzeń `AnalyticsService` ze Studio się nie wysyła.

## Jak włączyć (kroki dla Game Directora)
1. **Moduł w grze.** Moduł jest bezwładny: samo `require` nic nie robi. Dodaj w `src/server/` skrypt serwera (np. `Telemetria.server.luau`; mapowanie: [[Rojo i struktura projektu]]):
   ```lua
   local Telemetria = require(game.ServerScriptService.Server.Telemetria)
   Telemetria.start()
   ```
   W obsłudze paragonów (`MarketplaceService.ProcessReceipt` albo `BindReceiptHandler` dla `DeveloperProduct`), **po** przyznaniu produktu i tuż przed zwróceniem „Processed”: `Telemetria.zakup(gracz, info.ProductId, info.CurrencySpent, "Nazwa produktu")`. Moduł sam nie ustawia `ProcessReceipt`; przelewów Robux (`RobuxTransfer…`) nie zgłaszamy. Opublikuj grę — dane pojawią się po pierwszym serwerze poza Studio.
   Sprawdzenie bez gry: `python tools/studio/test_telemetrii.py` generuje test Luau (atrapy zamiast usług), a `python tools/studio_mcp.py luau <plik>` uruchamia go w otwartym Studio — wynik „TEST TELEMETRII: … asercji OK”.
2. **Klucz Open Cloud tylko do odczytu.** Creator Dashboard → Open Cloud → API Keys → Create. Dla tej gry dodaj **wyłącznie**: `universe-datastores.objects:read` (odczyt wpisów Data Store) i — dla listy serwerów na żywo — `memory-store.sorted-map:read`. Żadnych uprawnień zapisu. Najlepiej ogranicz klucz do adresu IP komputera z panelem (gdy domowy adres IP się zmienia, klucz przestanie działać — panel pokaże błąd klucza i trzeba poprawić adres w ustawieniach klucza). Kto tworzy klucz, zależy od [[Pytania otwarte]] #13 (konto czy grupa).
3. **Wpis lokalny** na komputerze z panelem: zmienna środowiskowa `BC_OPEN_CLOUD_KEY` albo pole `analityka.klucz_open_cloud` w `konfiguracja.lokalna.json` (folder danych lokalnych panelu, poza repozytorium; dokładną ścieżkę pokazuje karta „Jak włączyć” osobie przy komputerze). **Nigdy** w `panel/konfiguracja.json` ani w żadnym pliku repozytorium — panel i tak zignoruje klucz z konfiguracji wspólnej.

Panel pokazuje stan każdego kroku i powód po polsku (brak klucza, klucz odrzucony, brak uprawnień, moduł jeszcze nic nie zapisał, limit Roblox). Przycisk „Pokaż przykładowe dane” (tylko przy komputerze) pokazuje, jak będzie to wyglądać — dane są wyraźnie oznaczone jako wymyślone.

## Bezpieczeństwo klucza
- Klucz idzie tylko nagłówkiem do `https://apis.roblox.com`, bez przekierowań; nie trafia do odpowiedzi panelu, logu ani lustra tylko-do-odczytu (lustro dostaje wyłącznie „niedostępne w podglądzie”).
- Wspólna konfiguracja z repozytorium nie może ustawić klucza ani zmienić adresu, pod który jest wysyłany. Szczegóły techniczne: `panel/README.md` → „Telemetria gry” i [[Panel zespołu]].
- Nieużywany klucz Open Cloud wygasa sam po 60 dniach — panel pokaże wtedy „klucz odrzucony”.

## Limity i koszty
Koszt w pieniądzach: **zero** (Data Store, Memory Store i Open Cloud są w cenie gry). Koszt w limitach:

| Limit (dokumentacja Roblox, stan na 13.11.2026) | Ile bierze telemetria |
|---|---|
| Serwer: 60 + 40 × gracze zapisów i odczytów Data Store na minutę | 1–2 `UpdateAsync` na 5 minut (przed zapisem sprawdza budżet i ustępuje) |
| Cała gra: 300 + 40 × gracze odczytów i 300 + 20 × gracze zapisów na minutę, **wspólnie** dla serwerów i Open Cloud | panel: pierwszy odczyt doby to 26 zapytań, potem ok. 5 co 5 minut przy otwartym widoku (zamknięte godziny pamięta 6 h); twardy limit panelu 120 na minutę — żeby nie zabrać budżetu zapisom profili graczy |
| Jeden klucz Data Store: 4 MB zapisu na minutę; wartość do 4 MB; nazwa klucza do 50 znaków | wpis godziny ma kilka–kilkanaście KB; przy setkach serwerów naraz trzeba będzie rozłożyć wpisy na kilka kluczy |
| Pamięć gry: 500 MB + 1 MB × wszyscy gracze od początku | 24 wpisy na dobę po kilka KB (ok. 3–5 MB rocznie); starych godzin nikt nie kasuje — do decyzji |
| Memory Store: 64 KB + 1,2 KB × gracze pamięci, 1000 + 120 × gracze jednostek zapytań na minutę, wartość do 32 KB | wpis serwera ok. 200 B, jedno odnowienie na minutę |
| `AnalyticsService`: 120 + 20 × gracze zdarzeń na minutę, 100 nazw własnych zdarzeń, 10 lejków, kroki 1–100 | serwer bierze najwyżej 20 × swoi gracze, nadmiar pomija |
| `BindToClose`: serwer czeka najwyżej 30 s | ostatni zapis przy zamykaniu, z ponowieniem |

## Źródła (dokumentacja Roblox)
- Limity Data Store (serwer, gra, Open Cloud, wielkości, pamięć): https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
- Typy budżetu (`StandardRead`, `StandardWrite`): https://create.roblox.com/docs/reference/engine/enums/DataStoreRequestType
- Open Cloud — wpis Data Store i lista sorted mapy (`maxPageSize` do 200, `orderBy` asc/desc, uprawnienia): https://create.roblox.com/docs/cloud/reference/features/storage
- Memory Store — limity i wygasanie (do 45 dni): https://create.roblox.com/docs/cloud-services/memory-stores , `SetAsync`: https://create.roblox.com/docs/reference/engine/classes/MemoryStoreSortedMap
- `AnalyticsService` (`LogCustomEvent`, `LogOnboardingFunnelStepEvent`) i limity zdarzeń: https://create.roblox.com/docs/reference/engine/classes/AnalyticsService , https://create.roblox.com/docs/production/analytics/event-types
- `ScriptContext.Error`: https://create.roblox.com/docs/reference/engine/classes/ScriptContext
- `ProcessReceipt`, `BindReceiptHandler`, pola paragonu: https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
- `BindToClose` i `CloseReason`: https://create.roblox.com/docs/reference/engine/classes/DataModel , https://create.roblox.com/docs/reference/engine/enums/CloseReason
- Klucze API (wygasanie po 60 dniach, ograniczenie IP): https://create.roblox.com/docs/cloud/auth/api-keys
- Wcześniejsze rozpoznanie: [[Narzędzia i skille do Roblox]] (sekcja „Open Cloud i dane do panelu”).

## Stan implementacji
- [x] Moduł w grze: `init.luau` (API: `start`, `zdarzenie`, `lejek`, `zakup`, `blad`, `zapisz_teraz`, `stan`), `Agregator.luau` (czysta logika), `Magazyn.luau` (zapis co 5 min i w `BindToClose`, ponawianie, budżet), `Zrodla.luau` (gracze, błędy, próbki)
- [x] Panel: `GET /api/telemetria`, karta „Jak włączyć”, cztery karty z liczbami, wykres godzinowy, dane przykładowe; testy `panel/testy/test_telemetria.py`
- [x] Generator testu Luau `tools/studio/test_telemetrii.py` (logika sprawdzona poza Studio pomocniczym interpreterem; **w Studio jeszcze nieuruchomiony**)
- [ ] Uruchomić test w Studio (gdy będzie wolne)
- [ ] Decyzje z listy niżej, potem kroki włączenia

## Otwarte pytania
Do przeniesienia do [[Pytania otwarte]], jeśli Game Director uzna je za ważne:
1. **Czy w ogóle włączamy własną telemetrię**, czy wystarczy wbudowana analityka Roblox (od 10 DAU) i jej API `universe.analytics:read` (przychód, crashe, retencja)? Własna działa od pierwszego testera i pokazuje błędy z treścią; wbudowana nie wymaga kodu w grze.
2. **Kto tworzy klucz Open Cloud** i na czyim komputerze leży (pytanie #13: konto czy grupa)?
3. **Jak długo trzymamy godziny** w Data Store — kasować starsze niż np. 90 dni, czy zostawić (kilka MB rocznie)?
4. **Lista produktów i kroków lejka** — nazwy wpisuje kod gry; trzeba je ustalić razem ze sklepem i pierwszą sesją (zob. propozycje monetyzacji).
5. **Kto widzi liczby sprzedaży**: dziś każdy z kodem dostępu do panelu (telefon); czy to w porządku?

## Powiązane
- [[Panel zespołu]] — gdzie liczby są pokazywane
- [[Rojo i struktura projektu]] — skąd skrypt w `src/server` trafia do gry
- [[Pytania otwarte]] — #13 (własność gry i klucza), #14 (repozytorium publiczne)
- [[Narzędzia i skille do Roblox]] — wcześniejsze rozpoznanie Open Cloud
