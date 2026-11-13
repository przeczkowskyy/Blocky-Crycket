# BLOCKY & CRYCKET — Panel zespołu

Lokalny panel dla dwóch osób pracujących nad grą: **okno na sejf Obsidiana** (decyzje, harmonogram, zadania), **raporty z wdrożeń** z akceptacją, **podgląd 3D** tego, co jest w Roblox Studio (także z telefonu), **agent Claude Code** na subskrypcji osoby przy komputerze, **głosówki**, **sieć neuronowa** (graf sejfu), **assety** (rejestr grafik gry) i **analityka gry**.

- Uruchomienie i instalacja: [INSTALACJA.md](INSTALACJA.md).
- Zasada nadrzędna (decyzja D-008): **mózgiem projektu jest sejf `B&C/`**. Panel niczego nie trzyma „obok” sejfu: decyzje, zadania i roadmapę czyta z notatek, a własne dane to tylko raporty, komentarze i migawki. Gdy człowiek odpowiada w panelu na pytanie, odhacza albo dodaje zadanie czy zatwierdza decyzję, panel zapisuje to **w tych samych plikach Markdown** sejfu (małe zmiany jak przy edycji ręcznej) — patrz [Zapis do sejfu](#zapis-do-sejfu-bczapispy).
- Stary `dashboard/` (Node/React, agenci przez klucz API) jest archiwalny — panel go nie używa i nie zmienia.

## Architektura

```
przeglądarka (komputer / telefon)
   │  HTTP + SSE, bez kroku budowania (czyste moduły ES, three.js w vendor/)
   ▼
panel/serwer.py  (Python 3.9+, sama biblioteka standardowa, port 8787)
   ├─ bc/sejf.py        czyta notatki B&C/ (i dodatkowe sejfy) → plan, graf, treść notatek
   ├─ bc/zapis.py       praca na sejfie: odpowiedzi, zadania, statusy decyzji (małe zmiany w B&C/Produkcja/*.md)
   ├─ bc/gitsync.py     stan repozytorium, pobierz / wyślij dane panelu
   ├─ bc/obecnosc.py    kto jest na panelu, kto w Studio (Team Create), ostatnie commity
   ├─ bc/studio.py      sesja MCP z Roblox Studio (tools/studio_mcp.py)
   ├─ bc/podglad.py     migawki świata gry (części + zrzuty ekranu) → podgląd 3D
   ├─ bc/analityka.py   gracze online / wizyty (publiczne API Roblox), konsola Studio
   ├─ bc/telemetria.py  telemetria gry z modułu src/server/Telemetria (Open Cloud, klucz tylko lokalnie)
   ├─ bc/assety.py      rejestr grafik gry (assets/manifest.json) i gotowe obrazy — tylko do odczytu
   ├─ bc/raporty.py     raporty z wdrożeń, decyzje, komentarze (plik na wpis)
   ├─ bc/agent.py       agent = `claude -p` (subskrypcja Claude Code tej osoby), wątki, strumień odpowiedzi
   ├─ bc/glos.py        głosówki → lokalna transkrypcja (faster-whisper, opcjonalnie)
   └─ bc/statyczny.py   eksport lustra tylko-do-odczytu (GitHub Pages) — podgląd z telefonu bez włączonego komputera
```

| Gdzie | Co | W git? |
|---|---|---|
| `panel/dane/raporty/<id>.json`, `<id>.decyzja.json` | raporty z wdrożeń i decyzje ludzi | tak |
| `panel/dane/komentarze/<id>.json` | komentarze do raportów, komponentów, notatek | tak |
| `panel/dane/podglad/<id>/` | migawka: `meta.json`, `czesci.json`, `zrzut_N.jpg` | tak |
| `panel/konfiguracja.json` | wspólna konfiguracja (port, ID gry, sejfy) | tak |
| `assets/manifest.json`, `assets/processed/` | rejestr grafik i gotowe obrazy — pisze je pipeline `/asset`, panel **tylko czyta** (zakładka Assety) | tak |
| `B&C/Produkcja/{Pytania otwarte,Zadania,Rejestr decyzji,Dziennik zmian}.md` | zmiany z panelu (odpowiedzi, zadania, statusy decyzji, ślad w dzienniku) — w tych samych plikach co Obsidian | tak (przycisk „Wyślij” albo zwykły commit) |
| `%LOCALAPPDATA%\BlockyCrycket\panel\` | kod dostępu, klucz lokalny, klucz zatwierdzania (`klucz_gd.txt` — nazwa po dawnym kluczu Game Directora), ślad zmian sejfu z panelu (`zapis_sejfu.json`), log, wątki agenta, nagrania, historia analityki, `konfiguracja.lokalna.json` | **nie** (stan tego komputera) |

**Jeden plik na wpis** (raport, komentarz, migawka) — dwie osoby mogą dopisywać równocześnie i git nigdy nie ma konfliktu.

Porty: panel **8787**. Zajęte przez inne narzędzia: 8765–8767 (Saga), 4310 i 5173 (stary dashboard), 34872 (Rojo).

## Bezpieczeństwo
- Domyślnie tylko `127.0.0.1`. `--lan` otwiera sieć lokalną; każde żądanie spoza komputera wymaga **kodu dostępu** (link z kodem w Ustawieniach → Telefon).
- Prawa osoby przy komputerze (`lokalny`: agent, git, nowa migawka, ustawienia, adresy z kodem) daje **klucz lokalny**, a nie samo połączenie z `127.0.0.1` — tunel, przekierowanie portu i obcy program na tym komputerze też przychodzą z pętli zwrotnej. Klucz leży w danych lokalnych; panel przy starcie otwiera przeglądarkę adresem `/?l=<klucz>`, serwer zamienia go na ciasteczko `bc_l` (HttpOnly, SameSite=Strict) i przekierowuje na adres bez klucza. Programy podają go nagłówkiem `X-BC-Lokalny`. Klucz działa tylko z pętli zwrotnej, z hostem `127.0.0.1`/`localhost` i bez nagłówków pośrednika.
- Wspólna `panel/konfiguracja.json` (z repozytorium) nie może zmienić ustawień bezpieczeństwa: `dozwolone_hosty`, `agent.zdalnie`, `agent.sciezka`, `agent.dozwolone_narzedzia`, `glos.katalog_modeli`, sejfy spoza repozytorium i tryb agenta `auto` działają tylko z `konfiguracja.lokalna.json` na danym komputerze.
- `Host` musi być znany; każdy `POST` wymaga nagłówka `X-BC: 1`; `Origin` musi być własny.
- **Status decyzji** (zmiana kanonu) zmienia „decydent”. Od decyzji z 13.11.2026 Karol i Paweł mają równe prawa: wystarcza decyzja jednego, a każda zostaje w logach z imieniem i datą. W panelu decydentem jest **osoba przy komputerze z panelem** (klucz lokalny) albo przeglądarka z **kluczem zatwierdzania** (dawniej „klucz Game Directora”). Gość z samym kodem dostępu decyzji nie zmienia (`403`, `kod: "brak_klucza_zatwierdzania"`). Klucz zatwierdzania to osobny sekret w danych lokalnych (`klucz_gd.txt`); tworzy go i wypisuje link `python panel/serwer.py --klucz-zatwierdzania` (`--nowy-klucz-zatwierdzania` unieważnia stary — nowy działa od razu, bez restartu; dawne nazwy `--klucz-gd` i `--nowy-klucz-gd` działają dalej). Link `/?gd=<klucz>` serwer zamienia na ciasteczko `bc_gd` (HttpOnly, SameSite=Lax, rok) i przekierowuje na adres bez klucza; programy mogą podać nagłówek `X-BC-GD`. Nazwy pliku, ciasteczka i parametru `gd` zostały po dawnym kluczu, żeby zapisane linki działały dalej. Porównanie w stałym czasie, nieudane próby liczą się do limitu kodu dostępu (10 na 5 min). Klucz działa także przez tunel i z telefonu, ale zawsze **obok** zwykłego dostępu (kod dostępu albo klucz lokalny), nigdy zamiast niego. Imię z Ustawień (`X-BC-Kto`) służy wyłącznie do podpisu i niczego nie odblokowuje; zaufanie niesie znacznik dopisywany przez serwer (`(klucz zatwierdzania, data)` / `(gość panelu, data)`, patrz [Zapis do sejfu](#zapis-do-sejfu-bczapispy)). Czego klucz **nie** chroni: (1) kto ma dostęp do komputera z panelem, może zmieniać pliki sejfu wprost; (2) przy włączonym „Agencie z telefonu” (`agent.zdalnie`, tryb Praca z Edit/Write) gość z kodem dostępu może poprosić agenta o zmianę dowolnego pliku sejfu, także Rejestru decyzji — klucz zatwierdzania tego nie blokuje, dlatego przełącznik jest domyślnie wyłączony i powinien zostać wyłączony, gdy kod dostępu znają osoby spoza zespołu; (3) agenci, którzy na podstawie odpowiedzi w `Pytania otwarte.md` wpisują ✅, muszą sprawdzać znacznik — samo imię „Paweł” w odpowiedzi gościa nie jest zgodą.
- Agent z telefonu jest **domyślnie wyłączony** (`agent.zdalnie` w konfiguracji lokalnej; przełącznik w Ustawieniach → Telefon, dostępny tylko z kluczem lokalnym) — to zdalne sterowanie komputerem.
- Sekretów nie ma w repozytorium. Nagrania głosowe i rozmowy z agentem zostają na komputerze; do repo trafia tylko tekst komentarza.
- Repozytorium jest **publiczne**: wszystko w `panel/dane/` i w sejfie widzi cały świat.

## Kontrakt serwera (dla modułów `bc/*.py`)
Moduł ma funkcję `zarejestruj(app)` i opcjonalnie `zdrowie() -> dict`. Szczegóły i przykład w nagłówku [`bc/http.py`](bc/http.py); narzędzia wspólne w [`bc/rdzen.py`](bc/rdzen.py) (`REPO`, `DANE`, `RUNTIME`, `konfiguracja()`, `czytaj_json`, `zapisz_json`, `teraz()`, `nowe_id()`, `w_katalogu()`, `uruchom()`, `log()`, `BladHTTP`). Zasady: sama biblioteka standardowa; zapis tylko przez `zapisz_json` / `zapisz_bajty`; nic ciężkiego przy imporcie; operacje wolniejsze niż ~1 s z pamięcią podręczną i limitem czasu; komunikaty błędów po polsku, zrozumiałe dla człowieka. Odpowiedzi błędów: `{"blad": "…"}` ze statusem 4xx/5xx (niepoprawny identyfikator `400`, nieistniejący `404`, „tylko lokalnie” `403`, żądanie spoza komputera bez kodu dostępu `401`).

Testy (z katalogu `panel/`): `python -m unittest discover -s testy -t .` — w tym `testy/test_api.py`, test dymny całego API na prawdziwym serwerze z katalogami tymczasowymi (bez Studio, sieci, agenta i zapisu do gita). `testy/__init__.py` ustawia `BC_PANEL_RUNTIME` i `BC_PANEL_DANE` na katalog tymczasowy, zanim jakikolwiek test zaimportuje `bc.rdzen` — testy nie czytają prawdziwej konfiguracji lokalnej ani `panel/dane`. Na żądanie: `testy/test_przegladarka.py` (`BC_TEST_PRZEGLADARKA=1`, potrzebuje Edge albo Chrome i Node 22+, ok. minuty) — Plan w prawdziwej przeglądarce bez okna: okno decyzji a odświeżenie w tle, podwójny Ctrl+Enter, odhaczenie przy cudzej zmianie, podwójny klik (`testy/przegladarka.mjs`; zrzuty: `BC_TEST_ZRZUTY=<katalog>`).

## API
Wszystkie odpowiedzi to JSON, chyba że napisano inaczej. Czasy w ISO 8601 ze strefą. `?` = pole opcjonalne.

### Rdzeń (`serwer.py`)
| Trasa | Odpowiedź |
|---|---|
| `GET /api/ping` | `{ok, app:"bc-panel", wersja, start, pid, port, lan}` |
| `GET /api/ja` | `{kto, lokalny, gospodarz, tryb_statyczny, wersja, game_director, decydent, zapis_sejfu}` — `kto` z nagłówka `X-BC-Kto` (URL-encoded) albo, bez nagłówka, `git config user.name` (przy komputerze z panelem) lub „gość” — imię z gita nie podpisuje decyzji; `game_director` = żądanie niesie klucz zatwierdzania (stara nazwa pola, zostaje dla zgodności); `decydent` = może zmieniać statusy decyzji (klucz zatwierdzania albo `lokalny`; w lustrze zawsze `false`; interfejs przy starym serwerze bez tego pola używa `game_director`); `zapis_sejfu` = działa zapis do sejfu z panelu (w lustrze zawsze `false`) |
| `GET /api/konfiguracja` | `{port, gra:{nazwa, universeId, placeId}, sejfy:[{id,nazwa}], agent:{…}, glos:{…}}` |
| `POST /api/konfiguracja/lokalna` | tylko lokalnie; ciało `{agent_zdalnie: bool}` → `{agent:{zdalnie}}` (zapis w `konfiguracja.lokalna.json`) |
| `GET /api/dostep` | tylko lokalnie: `{lan, token, adresy:[url z kodem], podpowiedz, link_lokalny}` |
| `GET /api/zdrowie` | `{rdzen:{…}, moduly:{nazwa:{ok,blad}}, szczegoly:{nazwa: wynik zdrowie()}}` — dla gościa bez lokalnych ścieżek i ze skróconymi szczegółami |

### Sejf (`bc/sejf.py`)
Sejfy z `konfiguracja()["sejfy"]` (`[{id, nazwa, sciezka}]`, ścieżka względem repo albo bezwzględna; nieistniejący sejf jest pomijany). Pomijane foldery: `.obsidian`, `.trash`, `_narzędzia`, `__pycache__`. Wikilinki `[[Nazwa]]`, `[[Nazwa|alias]]`, `[[Nazwa#Nagłówek]]` rozwiązywane po nazwie pliku (bez `.md`, bez rozróżniania wielkości liter), najpierw w tym samym sejfie.

| Trasa | Odpowiedź |
|---|---|
| `GET /api/sejf/plan` | `{roadmapa, zadania, decyzje, pytania, dziennik, zrodla}` — patrz niżej |
| `GET /api/sejf/siec` | `{wezly:[{id, tytul, sejf, folder, kategoria, status, tagi:[…], slowa, zmieniono, stopien, sciezka}], krawedzie:[[i,j],…], kategorie:[{id, nazwa, sejf, kolor, liczba}], nierozwiazane:[{z, link}], statystyki:{notatki, powiazania, sejfy}}` — `id` = indeks w `wezly`; `sciezka` względem repo (albo `sejf:<id>/…` dla sejfu spoza repo); `kategoria` = pierwszy folder w sejfie (albo `(korzeń)`) |
| `GET /api/sejf/notatka?sciezka=` | `{sciezka, tytul, sejf, frontmatter:{…}, tresc_md (bez frontmattera), linki_wy:[{tytul, sciezka}], linki_we:[{tytul, sciezka}], zmieniono}` |
| `GET /api/sejf/szukaj?q=` | `{wyniki:[{sciezka, tytul, sejf, fragment}]}` (do 40) |

`plan` (parsowane z `B&C/Produkcja/*.md`; brak pliku = pusta lista, nigdy błąd):
```
roadmapa: {fazy:[{nazwa, opis, status_tekst, aktywna, pozycje:[{tekst_md, zrobione}], postep (procent 0–100)}], propozycje:[{nr, nazwa, opis_md}]}
zadania:  {sekcje:[{nazwa, pozycje:[{tekst_md, zrobione, priorytet?: "wysoki"|"średni"|"niski", data?}]}], otwarte, zrobione}
decyzje:  [{id:"D-008", tytul (bez `), tytul_md, status:"zatwierdzona"|"do_decyzji"|"propozycja"|"odrzucona"|"zastapiona", emoji, kategoria, meta:[…], opis_md}]
pytania:  [{nr, tytul, tresc_md, odpowiedz_md, otwarte}]
dziennik: [{data, kto, temat, punkty_md:[…]}]      (30 najnowszych)
zrodla:   {"B&C/Produkcja/Zadania.md": "<ISO mtime>", …}
pliki:    {roadmapa|zadania|decyzje|pytania|dziennik: "B&C/Produkcja/….md"}   (albo „sejf:<id>/…” dla sejfu spoza repo)
wersje:   {roadmapa|zadania|decyzje|pytania|dziennik: "<16 hex>" | null}   (znacznik do zapisu, patrz Zapis do sejfu)
```
Każda pozycja `zadania.sekcje[].pozycje[]` ma też `id` (`z` + 10 hex: skrót surowego tekstu pola, z priorytetem).
Formaty źródłowe: decyzja `### D-001 Tytuł` + linia `✅ zatwierdzona · styl · źródło: …` + opis; roadmapa `## ▶ Faza 1 — Frontend (kanon, w trakcie)` z listą `- [x]`; zadania: sekcje `## 🔥 Teraz (…)` z `- [ ] tekst · #wysoki` (w sekcji assetów kilka pól w jednej linii: `- [ ] A · [x] B`), zrobione `- [x] 2026-11-12: tekst`; pytania `## 1. Tytuł` + treść + `**Odpowiedź:**`; dziennik `## 2026-11-12 · Kto (temat)` + punkty.

### Zapis do sejfu (`bc/zapis.py`)
Praca na sejfie z panelu: odpowiedzi na pytania otwarte, odhaczanie i dodawanie zadań, statusy decyzji. Sejf zostaje jedynym źródłem prawdy (D-008) — panel nie ma własnej bazy, tylko zmienia te same pliki `<sejf B&C>/Produkcja/*.md` (sejf z `konfiguracja()["sejfy"]`, nie sztywna ścieżka; testy i próby działają na kopii).

| Trasa | Kto | Działanie |
|---|---|---|
| `POST /api/sejf/pytania/<nr>/odpowiedz` `{tekst, wersja}` | każdy z dostępem (także gość z kodem) | wiersz `- <Imię> (<znacznik, >RRRR-MM-DD): <tekst>` pod `**Odpowiedź:**` pytania `## <nr>. …` w `Pytania otwarte.md`, pod dotychczasowymi odpowiedziami (do pierwszej pustej linii poza blokiem kodu albo `---`); gdy pytanie nie ma wiersza `**Odpowiedź:**`, dochodzi on na końcu pytania (w ostatnim pytaniu przed `---` stopki). Sekcja pytania sięga do następnego `##`, tak jak w parserze planu (linia `---` w treści pytania jej nie kończy). Znacznik dopisuje serwer — patrz „Podpis i znaczniki” niżej. Ta sama odpowiedź tej samej osoby z tego samego dnia drugi raz = `409` (`kod: "juz_zapisane"`) |
| `POST /api/sejf/zadania/odhacz` `{id` albo `tekst, wersja}` | każdy z dostępem | `Zadania.md`: pozycja z sekcji „Teraz”/„Backlog” znika i trafia na górę sekcji „Zrobione” jako `- [x] RRRR-MM-DD: <tekst bez priorytetu>` (wcięte linie pod nią idą razem z nią; zadanie z **otwartymi** podzadaniami = `409`, `kod: "otwarte_podzadania"` — najpierw podzadania); pozycja z listy wielopolowej (`- [ ] A · [ ] B`, np. „Assety do stworzenia”), z innej sekcji, wcięte podzadanie albo otwarta pozycja, która już leży w „Zrobione”, dostaje `[x]` w miejscu. `id` z planu albo dokładny `tekst` (surowy albo bez priorytetu). Rodzaj sekcji = pierwsze słowo nazwy bez emoji („✅ Zrobione (archiwum backlogu)” to „Zrobione”); dwie sekcje tego samego rodzaju = `409` (`kod: "powtorzona_sekcja"`) |
| `POST /api/sejf/zadania/dodaj` `{tekst, sekcja: "teraz"`/`"backlog", priorytet: "wysoki"`/`"średni"`/`"niski", wersja}` | każdy z dostępem | `- [ ] <tekst> · #<priorytet>` na końcu sekcji (za ostatnią niepustą linią); identyczne otwarte zadanie = `409` |
| `POST /api/sejf/decyzje/<id>/status` `{status: "zatwierdzona"`/`"odrzucona"`/`"do_decyzji", uzasadnienie?, wersja}` | **decydent**: Karol albo Paweł — osoba przy komputerze z panelem (klucz lokalny) albo klucz zatwierdzania; wymagane prawdziwe imię | wiersz statusu pod `### D-0XX …` w `Rejestr decyzji.md`: w pierwszym polu podmieniane są **tylko** emoji i słowo statusu (`✅ zatwierdzona` / `❌ odrzucona` / `🕓 do decyzji`; dopisek typu „(wstępna, czeka na test B1)”, pozostałe pola i odstępy zostają bajt w bajt), na końcu ` · zdecydował: <Imię> RRRR-MM-DD` (przy „do decyzji”: ` · oznaczył: <Imię> RRRR-MM-DD`; poprzedni podpis „zdecydował/oznaczył” jest zastępowany — także dawne `zdecydował: Game Director` i `zdecydował: Game Director (Paweł) 2026-11-13`); opcjonalnie wiersz `Uzasadnienie — <Imię>, RRRR-MM-DD: <tekst>` na końcu opisu decyzji (przed linią `---` i stopką rejestru). Imię puste albo domyślne „gość” = `400` (`kod: "brak_imienia"`) — decyzja musi mieć podpis. Liczy się tylko imię z nagłówka `X-BC-Kto` (wpisane w Ustawieniach): gdy przeglądarka go nie wysyła, serwer przy komputerze z panelem bierze do innych podpisów `git config user.name`, ale decyzji takim domyślnym imieniem nie podpisze — też `400 brak_imienia`. Przejścia tylko z `💡 propozycja` i `🕓 do decyzji`. Dwie decyzje o tym samym numerze = `409` (`kod: "powtorzony_numer"`) — tak samo dwa pytania o tym samym numerze |

Odpowiedź każdej trasy: `{ok, opis, plik, wersja (nowy znacznik), plan (cały plan jak GET /api/sejf/plan), uwaga?}`. Błędy: `400` złe dane albo próba wstrzyknięcia; `403` status decyzji bez klucza zatwierdzania i spoza komputera z panelem (`kod: "brak_klucza_zatwierdzania"`; komunikat mówi, jak zdobyć klucz) albo zapis wyłączony; `404` nie ma pytania / zadania / decyzji / sekcji; `409` konflikt wersji (`kod: "konflikt_wersji"`, `wersja` = aktualna), decyzja zamknięta (`kod: "status_zamkniety"`: zatwierdzona, odrzucona, zastąpiona), ten sam status, zadanie już odhaczone, powtórzony numer / sekcja, otwarte podzadania, ta sama odpowiedź drugi raz, znaczniki konfliktu gita w pliku (`kod: "konflikt_gita"`), samotne znaki CR (`kod: "konce_linii"` — parser planu liczy je jako nową linię, zapis nie), plik nie w UTF-8, trwa inny zapis; `429` limit zapisów gościa (`kod: "limit_zapisow"`); `400` także status decyzji bez imienia z Ustawień — puste, „gość” albo brak nagłówka `X-BC-Kto` (`kod: "brak_imienia"`) i imię brzmiące jak znacznik serwera — „Game Director”, „klucz zatwierdzania”, „gość panelu”, bez względu na wielkość liter, dla każdego, także z kluczem (`kod: "imie_zastrzezone"`).

**Podpis i znaczniki.** Imię (`X-BC-Kto`) każdy wpisuje sam, więc o zaufaniu mówi **znacznik, który dopisuje serwer** na podstawie kluczy, nie imienia. Z imienia usuwane są znaki formatowania oraz `(`, `)`, `,`, `·`, więc znacznika nie da się podrobić w imieniu:

| Kto pisze | Odpowiedź w `Pytania otwarte.md` | Wiersz w Dzienniku zmian |
|---|---|---|
| przeglądarka z kluczem zatwierdzania | `- Paweł (klucz zatwierdzania, 2026-11-13): …` | `- Paweł (klucz zatwierdzania): …` (np. `- Paweł (klucz zatwierdzania): decyzja D-019 zatwierdzona`) |
| osoba przy komputerze z panelem (klucz lokalny) | `- Karol (2026-11-13): …` | `- Karol: …` |
| gość z kodem dostępu (telefon, tunel) | `- Paweł (gość panelu, 2026-11-13): …` | `- Paweł (gość panelu): …` |

W Rejestrze decyzji podpis to samo imię i data: `zdecydował: Paweł 2026-11-13` (zatwierdzona / odrzucona), `oznaczył: Karol 2026-11-13` (do decyzji), `Uzasadnienie — Paweł, 2026-11-13: …`. To, czy zmiana przyszła z klucza zatwierdzania, czy od osoby przy komputerze, widać w Dzienniku zmian (znacznik albo jego brak). **Wpisy z 13.11.2026 sprzed tej zmiany** mają jeszcze znacznik `Game Director` (`- Paweł (Game Director, 2026-11-13): …`, `zdecydował: Game Director (Paweł) 2026-11-13`, `- Paweł (Game Director): decyzja …`) — znaczy on dokładnie to samo co `klucz zatwierdzania`.

**Zgodę z panelu poznaje się po znaczniku serwera albo po podpisie w Rejestrze, nigdy po samym imieniu.** Odpowiedź „Tak, zatwierdzam” podpisana `(gość panelu, …)` nie jest zgodą, nawet gdy imię to „Paweł”. Imiona brzmiące jak znaczniki („Game Director”, „klucz zatwierdzania”, „gość panelu”, bez względu na wielkość liter) są odrzucane (`400`).

**Zasady zapisu**
- **Tylko wskazane miejsce.** Plik jest dzielony na linie z ich własnymi końcami; zmienia się wyłącznie wskazana linia albo dochodzą nowe. Reszta zostaje bajt w bajt: BOM, końce linii (nowe wiersze dostają koniec linii sąsiada — CRLF w pliku CRLF, LF w LF), spacje, frontmatter. Jedyny wyjątek: gdy wiersz dochodzi za ostatnią linią bez końca linii, ta linia dostaje koniec linii.
- **Kontrola wersji.** `wersja` = pierwsze 16 znaków SHA-256 treści pliku z `GET /api/sejf/plan` (`wersje`). Gdy plik zmienił się od odczytu (drugi człowiek, Obsidian, agent) — `409` i nic nie jest zapisywane; interfejs pokazuje „Ktoś zmienił ten plik — odświeżam”, a wpisany tekst zostaje w polu.
- **Jedna blokada zapisu na cały sejf**, zapis atomowy (plik tymczasowy obok + `os.replace`, z ponowieniami przy blokadzie przez OneDrive), po zapisie unieważniana pamięć planu i indeksu w `bc/sejf.py`. Przed każdą próbą `os.replace` plik jest czytany ponownie — blokada pliku zwykle znaczy, że Obsidian albo agent właśnie go zapisuje, więc zmieniona treść daje `409` zamiast nadpisania cudzego zapisu. Pliki tymczasowe panelu pozostawione po przerwanym zapisie (`<plik>.md.<pid>.<6 hex>.tmp`, starsze niż 10 min) są usuwane przy pierwszym zapisie do folderu.
- **Ten sam podział pliku co parser planu.** Nagłówki i bloki kodu rozpoznaje ta sama reguła (`sejf._RX_NAGLOWEK`, `sejf.zamyka_plot`: płotek zamyka tylko płotek tego samego znaku, co najmniej tak długi, bez tekstu za nim). Pliki, które parser i zapis widziałyby inaczej (samotne CR, znaczniki konfliktu gita), są odrzucane z `409`.
- **Limit gości:** najwyżej 30 zapisów na 10 min z jednego połączenia (za tunelem liczy się `Cf-Connecting-Ip`) i 120 na 10 min dla wszystkich gości razem → `429`. Osoba przy komputerze i przeglądarka z kluczem zatwierdzania bez limitu.
- **Ślad w Dzienniku zmian:** każda operacja dopisuje `- <Imię>< (znacznik)>: <opis> ([[<notatka>]])` (np. `- Paweł (gość panelu): odpowiedź na pytanie 22 ([[Pytania otwarte]])`) w sekcji dnia `## RRRR-MM-DD · Panel (ludzie)` (na końcu sekcji; gdy jej nie ma — nowa sekcja nad pierwszym wpisem z datą). Opisy: `odpowiedź na pytanie 16`, `odhaczone zadanie: …`, `dodane zadanie: … (Backlog)`, `decyzja D-019 zatwierdzona` / `odrzucona` / `oznaczona „do decyzji”`. Długie teksty skracane do 140 znaków (bez urwanego wikilinku).
- **Tekst od ludzi:** limit długości (odpowiedź 2000, zadanie 300, uzasadnienie 1000 znaków), usunięte znaki sterujące i znaki odwracania kierunku tekstu, zawsze jedna linia (nowe linie → ` / `). Odrzucane (`400`): tekst zaczynający się nagłówkiem (`#`, `## …`) albo polem zadania (`- [ ]`, `[x]`), zawierający `**Odpowiedź` albo kolejne pole `· [ ]`; w zadaniu także priorytet w treści (`#wysoki` — od tego jest pole `priorytet`). Imię do podpisu: jedna linia, bez znaków formatowania (`*`, `_`, `[`, `]`, `#`, `` ` ``, `|`, `<`, `>`, `:`), najwyżej 40 znaków, puste = „gość”.
- **Wyłączenie:** `"zapis_sejfu": false` w konfiguracji (wspólnej albo lokalnej) — trasy zwracają `403`, a interfejs chowa przyciski. Lustro statyczne nigdy nie zapisuje (`/api/ja` ma tam `zapis_sejfu: false`, `game_director: false`, `decydent: false`).
- **„Wyślij” (bc/gitsync.py):** po zapisie panel zapamiętuje w danych lokalnych (`zapis_sejfu.json`) skrót pliku przed pierwszą zmianą panelu (`baza`), po ostatniej (`ostatni`) i opisy zmian. Przycisk „Wyślij” dołącza plik sejfu do commita tylko, gdy: leży w repozytorium, jest jednym z czterech plików powyżej, jego treść to dokładnie ostatni zapis panelu, a wersja w `HEAD` to ta, od której panel zaczynał. Plik z cudzymi niezatwierdzonymi zmianami jest pomijany z uwagą „wyślij go zwykłym commitem”; plik zacommitowany ręcznie znika ze śladu. Po commicie ślad jest czyszczony. Od sprawdzenia plików do wyczyszczenia śladu „Wyślij” trzyma **blokadę zapisu sejfu** (`zapis.blokada_wysylania()`; push idzie już poza nią) — odpowiedź z telefonu zapisana w trakcie commita czeka na jego koniec i zostaje w śladzie. Gdy Obsidian albo agent zmieni plik między sprawdzeniem a commitem, commit „panel: …” zawiera też tę zmianę — wtedy odpowiedź „Wyślij” ma `uwaga` z nazwą pliku (`zapis.po_commicie`). `GET /api/git/stan` zwraca `podglad_sejfu: [{plik, wiersze: ["+ …", "- …"], ucieto}]` (z `git diff HEAD`, do 40 wierszy na plik), a okno „Wyślij” pokazuje te wiersze, zanim cokolwiek pójdzie do publicznego repozytorium.

**Interfejs** (`static/widoki/plan.js`): Pytania — pod każdym pytaniem dotychczasowe odpowiedzi i pole „Twoja odpowiedź” z podpisem, jaki nada serwer („Podpis w sejfie: Paweł (gość panelu, …)”; przy odpowiedzianych zwinięte „Dopisz odpowiedź”); Zadania — pole wyboru odhacza po 5 s (toast z „Cofnij”; przejście do innego widoku, ukrycie karty albo zamknięcie strony wysyła od razu, z `keepalive`), przycisk „Dodaj zadanie” (arkusz z sekcją i priorytetem); Decyzje — przy propozycjach i „do decyzji” przyciski „Zatwierdź” / „Odrzuć” z arkuszem potwierdzenia (z opisem decyzji, podglądem podpisu i uzasadnieniem) tylko dla decydenta (`ja.decydent`; przy starym serwerze bez tego pola — `ja.game_director`), pozostali widzą „Zatwierdza Karol albo Paweł (klucz zatwierdzania)” i zwinięte komentarze (cel komentarza: typ `notatka`, `<ścieżka rejestru>#D-0XX`); Ustawienia — wiersz „Zatwierdzanie decyzji: tak/nie” z instrukcją. Zabezpieczenia: arkusz decyzji wysyła **wersję Rejestru z chwili otwarcia** (to, co decydujący przeczytał) — gdy odpytywanie w tle wczyta nowszą treść, „Zatwierdzam” daje `409`, okno się zamyka i nic nie jest zapisane; formularze mają flagę „w toku” (podwójny Ctrl+Enter / Enter = jedno żądanie), szkic nie wraca do pola, gdy odpowiedź już jest w sejfie; podwójny klik w pole wyboru (< 400 ms) liczy się jako jeden; odhaczenie po `409 konflikt_wersji` ponawia się raz z aktualną wersją (id = skrót treści, więc zmienione zadanie nie zostanie odhaczone), a gdy się nie uda — toast „Nie odhaczono: …”.

### Git (`bc/gitsync.py`)
| Trasa | Odpowiedź / działanie |
|---|---|
| `GET /api/git/stan` | `{galaz, czyste, zmienione:[{plik, stan}], zmiany_panelu, zmiany_sejfu:[ścieżka], uwagi_sejfu?:[…], podglad_sejfu?:[{plik, wiersze, ucieto}], do_wyslania, do_pobrania, ostatni_fetch, ostatnie_commity:[{hash, autor, data, temat}], zdalne}` (fetch w tle najwyżej co 5 min; `zmiany_panelu` liczy też `zmiany_sejfu`) |
| `POST /api/git/pobierz` | `git pull --rebase --autostash` → `{ok, wyjscie, uwaga?}` (tylko lokalnie) |
| `POST /api/git/wyslij` `{opis?}` | commit **wyłącznie** ścieżek z `git.sciezki_panelu` oraz plików sejfu, które naprawdę zmienił panel (patrz [Zapis do sejfu](#zapis-do-sejfu-bczapispy)) + push → `{ok, commit?, wyjscie, uwaga?, pliki_sejfu?}` (tylko lokalnie). Bez `opis` przy zmianach sejfu opisem commita jest lista zmian: `panel: odpowiedź na pytanie 16; odhaczone zadanie: …` |

Porażka pobierz/wyślij (konflikt, odrzucony push, brak logowania) to `409` (przekroczony czas `502`) z `{blad, ok:false, wyjscie, commit?}`; `blad` mówi po polsku, co zrobić. `stan` ma dodatkowo `fetch_trwa`, `blad_fetch?`, `blad?`, a każdy element `zmienione` także surowy `kod` (XY z `git status`).

### Obecność (`bc/obecnosc.py`)
| Trasa | Odpowiedź |
|---|---|
| `POST /api/obecnosc/puls` `{klient, widok}` | zapisuje puls przeglądarki (żyje 45 s) i zwraca to samo co GET |
| `GET /api/obecnosc` | `{panel:[{kto, widok, od, ostatnio, lokalny}], studio:{dostepne, osoby:[{nazwa, id}], tryb?}, git:[{autor, ostatnio, temat}]}` |

### Studio i podgląd (`bc/studio.py`, `bc/podglad.py`)
| Trasa | Odpowiedź |
|---|---|
| `GET /api/studio/stan` | `{mostek, polaczone, studio?:{id, placeId, universeId, tryb, nazwa}, osoby:[{nazwa,id}], blad?, zajete?}` (pamięć 10 s; `?odswiez=1` wymusza) |
| `GET /api/studio/konsola` | `{linie:[{poziom:"info"|"ostrzezenie"|"blad", tekst}], bledy, ostrzezenia, polaczone, blad?}` (pamięć 5 s) |
| `GET /api/podglad` | `{migawki:[meta…] (najnowsza pierwsza), najnowsza}` |
| `POST /api/podglad/migawka` `{tytul?, opis?, zrzuty?:true, korzen?:"Workspace"}` | robi migawkę z otwartego Studio (tylko lokalnie) → `200 meta`; `503` bez Studio, `409` gdy inna migawka trwa, `400` zły korzeń |
| `GET /api/podglad/<id>/czesci` | zawartość `czesci.json` |
| `GET /api/podglad/<id>/plik/<nazwa>` | plik migawki (obraz, GLB) |

`meta.json`: `{id, tytul, opis, kto, czas, zrodlo:"studio"|"blender", czesci, grupy:[{sciezka, czesci}], zrzuty:["zrzut_1.jpg",…], zakres:{min:[x,y,z], max:[x,y,z]}, miejsce:{placeId, nazwa}, korzen?, uwagi?:["…"], model?: "scena.glb"}` — `uwagi` to komunikaty po polsku (np. puste zrzuty przy zminimalizowanym Studio; wtedy `zrzuty` bywa puste). Migawka bez `czesci.json` (np. z Blendera): `/czesci` → 404.

`czesci.json` (zwarty, jednostka = stud, układ jak w Roblox: Y w górę):
```
{"wersja":1, "grupy":["Workspace/DemoLesnaBaza/Karczma", …], "materialy":["SmoothPlastic", …],
 "czesci":[[ksztalt, grupa, x,y,z, rx,ry,rz, sx,sy,sz, "RRGGBB", material, przezroczystosc, "Nazwa"], …]}
```
`ksztalt`: 0 blok, 1 kula, 2 walec (oś X), 3 klin (WedgePart), 4 klin narożny (CornerWedgePart), 5 siatka MeshPart (ramka), 6 unia (ramka), 7 kratownica. `rx,ry,rz` = `CFrame:ToOrientation()` w **radianach** (kolejność YXZ, w three.js `Euler(rx, ry, rz, "YXZ")`). `grupa` i `material` to indeksy. Geometrię klinów opisuje `luau/KSZTALTY.md`.

### Raporty i komentarze (`bc/raporty.py`)
| Trasa | Odpowiedź / działanie |
|---|---|
| `GET /api/raporty` | `{raporty:[raport…] (najnowszy pierwszy), czeka}` |
| `GET /api/raporty/<id>` | `raport` + `komentarze:[…]` |
| `POST /api/raporty` | tworzy raport (pola jak niżej bez `id/czas/decyzja`) → `201 raport` |
| `POST /api/raporty/<id>/decyzja` `{wartosc:"zaakceptowane"|"do_poprawy", komentarz?}` | zapisuje `<id>.decyzja.json` → `raport` |
| `GET /api/raporty/<id>/plik/<nazwa>` | załącznik raportu (obraz) z `panel/dane/raporty/<id>/` |
| `GET /api/komentarze?typ=&cel=` | `{komentarze:[{id, cel:{typ, cel, etykieta?}, kto, czas, tekst, zrodlo:"tekst"|"glos"}]}` (bez filtrów: 100 najnowszych) |
| `POST /api/komentarze` `{cel:{typ, cel, etykieta?}, tekst, zrodlo?}` | `201 komentarz` |

`raport`: `{id, tytul, opis_md, kto, czas, rodzaj:"wdrozenie"|"pytanie"|"informacja", status:"czeka"|"zaakceptowane"|"do_poprawy"|"informacja", komponenty:[{typ:"studio"|"notatka"|"plik"|"migawka", cel, etykieta}], migawka?, zrzuty:[nazwa…], pytanie?, decyzja?:{kto, czas, wartosc, komentarz}, komentarzy}`. `status` wynika z `rodzaj` i decyzji (wdrożenie/pytanie bez decyzji = `czeka`; decyzja ma pierwszeństwo, liczy się ostatnia). `migawka` musi istnieć w `panel/dane/podglad/` (inaczej `400`); zrzuty dołącza tylko CLI (`--zrzut`). Typy celu komentarza: `raport` (id), `studio` (ścieżka grupy, np. `Workspace/DemoLesnaBaza/Karczma`), `notatka` (ścieżka w repo), `migawka` (id), `plik` (ścieżka pliku w repo, np. obraz assetu `assets/processed/Teleport.png`).

CLI dla agentów (działa bez serwera, pisze pliki): `python panel/narzedzia/raport.py dodaj --tytul … --opis … [--rodzaj wdrozenie] [--komponent studio:Workspace/X:"Etykieta"]… [--migawka ID] [--zrzut plik.png]… [--pytanie "…"] [--kto "Claude (Karol)"]`, `… lista`, `… odpowiedzi [--od ISO]`.

### Agent (`bc/agent.py`)
Agent to proces `claude -p --output-format stream-json` uruchamiany w katalogu repozytorium — ten sam Claude Code (CLAUDE.md, skille, serwery MCP z `.mcp.json`), na subskrypcji osoby, na której komputerze działa panel. Wątek pamięta `session_id` i wznawia rozmowę (`--resume`).

| Trasa | Odpowiedź / działanie |
|---|---|
| `GET /api/agent/stan` | `{dostepny, sciezka?, wersja?, zdalnie, tryby:[{id, nazwa, opis}], tryb_domyslny, model, powod?}` |
| `GET /api/agent/watki` | `{watki:[{id, tytul, utworzono, ostatnio, wiadomosci, trwa}]}` |
| `POST /api/agent/watki` `{tytul?}` | `201 watek` |
| `GET /api/agent/watki/<id>` | `{id, tytul, trwa, wiadomosci:[{nr, rola:"user"|"assistant"|"narzedzie"|"system", tekst, czas, kto?, kontekst?}]}` |
| `POST /api/agent/watki/<id>/wiadomosc` `{tekst, tryb?, model?, kontekst?:[{typ, cel, etykieta}]}` | startuje przebieg → `202 {ok, nr, od, tryb}` (`od` = numer pierwszego zdarzenia przebiegu, `tryb` = faktycznie użyty); `409`, gdy wątek pracuje albo trwają już 2 przebiegi |
| `GET /api/agent/watki/<id>/strumien?od=<nr zdarzenia>` | SSE: `{n, typ:"tekst", delta}` · `{n, typ:"narzedzie", nazwa, opis}` · `{n, typ:"wiadomosc", wiadomosc}` · `{n, typ:"blad", tekst}` · `{n, typ:"koniec", koszt_usd?, czas_s?, przerwano?, bezczynny?}` — wysyła zdarzenia ostatniego przebiegu o `n >= od` (`od=0` = cały bieżący przebieg; wznowienie: ostatnie `n` + 1); `koniec` przychodzi zawsze, z `n >= od` |
| `POST /api/agent/watki/<id>/stop` | przerywa przebieg |

Tryby: `plan` (tylko czyta i planuje: `--permission-mode plan`), `praca` (edytuje pliki i używa dozwolonych narzędzi: `acceptEdits` + lista `--allowedTools`, reszta odmawiana), `auto` (`--permission-mode auto`). Żądania nielokalne: `403`, dopóki `agent.zdalnie` nie jest `true`; wtedy najwyżej tryb `praca`.

### Głosówki (`bc/glos.py`)
| Trasa | Odpowiedź / działanie |
|---|---|
| `GET /api/glos/stan` | `{whisper, model, urzadzenie?: "karta graficzna"|"procesor", powod?}` |
| `POST /api/glos` (surowe audio, `Content-Type: audio/*`) | `201 {id, stan:"czeka"}` |
| `GET /api/glos/<id>` | `{id, stan:"czeka"|"transkrybuje"|"gotowe"|"blad"|"brak_whispera", tekst?, dlugosc_s?, blad?}` |

Nagrania leżą w `RUNTIME/nagrania/<id>/`; spisuje je osobny proces-robotnik (`python -m bc.glos --robotnik`), jeden naraz.

### Analityka (`bc/analityka.py`)
`GET /api/analityka` → `{gra:{universeId, placeId, nazwa?, gracze, wizyty, ulubione, max_graczy?, glosy?:{za, przeciw}, zaktualizowano, publiczna, blad?}, historia:[{t, gracze}], studio:{polaczone, tryb?, bledy, ostrzezenia, konsola:[…]}, telemetria:{podlaczona, opis}, robuxy:{dostepne, opis}}` — dane publiczne z `games.roblox.com` odświeżane najwyżej co 60 s i tylko, gdy ktoś pyta.

### Telemetria gry (`bc/telemetria.py`)
Liczby zbiorcze z modułu w grze `src/server/Telemetria` (bezwładny — działa dopiero po `Telemetria.start()` w skrypcie serwera): kubełki godzinowe UTC w Data Store `BC_Telemetria_v1` (klucz `g_RRRRMMDD_GG`, wpis `stan` = ślad, że moduł był włączony) i serwery na żywo w sorted mapie Memory Store `BC_Telemetria_Serwery`. Panel czyta je przez Open Cloud v2 kluczem **tylko do odczytu** (`universe-datastores.objects:read`, opcjonalnie `memory-store.sorted-map:read`). Opis dla ludzi, włączanie i prywatność: notatka sejfu `B&C/Technika/Telemetria gry.md`.

| Trasa | Odpowiedź |
|---|---|
| `GET /api/telemetria?godzin=24` | `{wlaczona, zrodlo:"open_cloud"\|"probka"\|null, kod?, powod?, kroki?:{modul, klucz}, chwilowe?, szczegoly? (tylko lokalnie), plik_konfiguracji? (tylko lokalnie, gdy wyłączona), okres:{od, do, godzin}, zaktualizowano, modul?:{wersja, starty, pierwszy_start, ostatni_start}, suma:{sesje, sredni_czas_sesji_s, ccu_max, robuxy, zakupy, bledy, sesje_zakonczone, sesje_ponizej_minuty, serwerogodziny, serwery_start, serwery_koniec, brak_pamieci, niedomkniete, serwery_teraz, gracze_teraz}, godziny:[{t, sesje, ccu_max, robuxy, bledy}], zakupy:[{id, nazwa, n, robuxy}], bledy:[{sygnatura, komunikat, n}], serwery:[{id (8 znaków), gracze, od, pamiec_mb?, fps?, bledy?}], lejek:[{krok, nazwa, n}], zdarzenia:[{nazwa, n}], dlugosci_sesji:{do_1…ponad_60}, uwagi?:[…], nieaktualne?, blad?}` — `godzin` 1–168. Pola od `okres` w dół są tylko, gdy są dane (`zrodlo` niepuste) |
| `GET /api/telemetria?probka=1` | dane **przykładowe** (`zrodlo:"probka"`, `przykladowe:true`, `wlaczona:false`) — tylko osoba przy komputerze (`403` dla innych); bez wyjścia do sieci |
| `?odswiez=1` | tylko lokalnie: odczyt z pominięciem pamięci, najwcześniej 30 s po poprzednim |

- **Wyłączona** (`wlaczona:false`, `zrodlo:null`) z `kod`: `brak_universe`, `brak_klucza`, `klucz_odrzucony` (401 albo zły kształt klucza), `brak_uprawnien` (403), `modul_wylaczony` (klucz działa, ale gra nie zapisała `stan`), `limit` (429 albo ogranicznik panelu), `siec`, `blad_roblox`, `blad_panelu`; `chwilowe:true` = awaria, a nie brak konfiguracji. Po awarii chwilowej panel pokazuje ostatnie dobre dane z `nieaktualne:true` i `blad`.
- **Klucz** wyłącznie ze zmiennej `BC_OPEN_CLOUD_KEY` albo `analityka.klucz_open_cloud` w `konfiguracja.lokalna.json`; `analityka.klucz_open_cloud` i `analityka.adres_open_cloud` są na liście „tylko lokalne” (`rdzen.TYLKO_LOKALNE_SEKCJE`) — wspólna konfiguracja z repo nie ustawi klucza ani nie przekieruje go pod inny adres. Klucz idzie tylko nagłówkiem `x-api-key` do `https://apis.roblox.com` (bez przekierowań); nie trafia do odpowiedzi, logu, `zdrowie()` ani lustra (każdy tekst z Roblox przechodzi przez wycinanie klucza). `analityka.magazyn` i `analityka.mapa_serwerow` (nazwy, `[A-Za-z0-9_.-]{1,50}`) można zmienić we wspólnej konfiguracji.
- **Koszt i limity**: odpowiedź pamiętana 5 min (błąd 1 min), godziny starsze niż 3 h — 6 h; każde żądanie 8 s, cały odczyt ≤ 25 s; najwyżej 120 żądań do Roblox na minutę ze wszystkich tras (budżet odczytów Data Store gra dzieli z Open Cloud). Dane z gry są normalizowane jak obce (typy, długości, ≤ 300 kluczy w słowniku, czasy spoza kalendarza → `null`).
- **Lustro statyczne** dostaje wyłącznie `{wlaczona:false, powod:"niedostępne w podglądzie"}`.
- `zdrowie()`: `{klucz_open_cloud (bool), skad_klucz, universeId, magazyn, ostatni_odczyt, ostatni_wynik}`.

### Assety (`bc/assety.py`)
Okno na rejestr grafik gry `assets/manifest.json` (prowadzi go pipeline `/asset`: skill `.claude/skills/asset/`, narzędzie `tools/manifest.py`). **Tylko do odczytu** — same trasy GET: panel niczego nie zmienia, nie wgrywa i nie zatwierdza. Zgodę na upload do Roblox daje człowiek w rozmowie z agentem; panel pokazuje tylko, co na nią czeka.

| Trasa | Odpowiedź |
|---|---|
| `GET /api/assety` | `{zrodlo:"assets/manifest.json", brak_manifestu?: true, blad?, figma_plik?, zaktualizowano?, assety:[asset…] (kolejność z manifestu), liczniki:{status: n}, etapy:[{id, nazwa, skrot, opis, bramka?: true, liczba}], statusy:[{id, nazwa, etap, opis, liczba, nieznany?}], czeka}` |
| `GET /api/assety/plik/<nazwa>` | gotowy obraz assetu (plik z pola `processed`); `<nazwa>` = nazwa assetu, opcjonalnie z rozszerzeniem obrazu (`Teleport.png`). `404` — nie ma assetu albo obrazu, `403` — manifest wskazuje plik spoza `assets/processed/` albo nie obraz |
| `GET /api/assety/miniatura/<nazwa>` | obraz pomniejszony do 384 px (WEBP albo PNG; wymaga opcjonalnej biblioteki Pillow, liczony w pamięci serwera). Bez Pillow — pełny plik |

`asset`: `{nazwa, kategoria, kategoria_opis, status, status_opis, status_wyjasnienie, status_nieznany?, etap (indeks w etapy albo null), uzycie, notatki, obraz (adres do <img> z wersją pliku ?v=… albo null), miniatura, plik? (ścieżka w repo), rozmiar? (bajty), wymiary?:[szer, wys], roblox_id?, roblox_decal?, roblox_cel?, moderacja?, figma_wezel?, figma_adres?, utworzono?, zmieniono?, historia:[{opis, pole?, wartosc?, kiedy?}], czeka_na_zgode, zgoda?:{jest, kiedy?, aktualna?}, prompt?, surowe?, inne?:{pole: wartość}, uwagi?:[…], cel_komentarzy}`.

- **Etapy** (pole `etap`): `generowanie` (0) → `obrobka` (1) → `figma` (2) → `zgoda` (3, bramka) → `roblox` (4). Statusy z `tools/manifest.py`: `planned`, `generated` → 0; `processed` → 1; `in_figma` → 2; `awaiting_approval`, `approved` → 3; `pending_studio`, `in_roblox`, `done` → 4; `rejected` poza etapami (`etap: null`). Status spoza tej listy albo jego brak (`brak`) to nie błąd: `status_nieznany: true`.
- **`czeka_na_zgode`**: status `awaiting_approval` albo `approved` bez ważnej zgody (`approved_by_user` inne niż `true`, albo plik zmienił się po akceptacji — jego sha256 różni się od `approved_sha256`). `czeka` = liczba takich assetów.
- **Odporność**: manifest czytany jako słownik nazwa → wpis (także lista wpisów z polem `name`); brakujące pola dają puste wartości, nieznane proste pola trafiają do `inne` (bez kluczy wyglądających na sekret), wpis o dziwnym kształcie nie wywraca odpowiedzi. Brak pliku: `brak_manifestu: true`; uszkodzony plik: `blad` z komunikatem — odpowiedź nadal `200`.
- **Bezpieczeństwo plików**: adres niesie tylko nazwę assetu. Ścieżkę bierze się z manifestu i po rozwiązaniu (`..`, dowiązania, litery dysków) musi leżeć w `assets/processed/` i mieć rozszerzenie `.png`, `.jpg`, `.jpeg`, `.webp` albo `.gif`. Nic z `assets/raw/`, nic spoza repozytorium. Adres obrazu = nazwa + rozszerzenie pliku (`Coin` → `…/plik/Coin.png`); serwer najpierw szuka nazwy bez rozszerzenia, więc asset o nazwie `Coin.png` nie przejmie obrazu `Coin`. Nazwa ze znakami, których nie ma w nazwach plików Windows (`< > : " | * ? # % / \`, kropka na końcu), nie dostaje adresu obrazu — tylko uwagę (lustro zapisuje obraz pod tą nazwą). Komunikat o nieczytelnym manifeście nie zawiera ścieżki z komputera.
- **Miniatury**: obraz większy niż 40 Mpx (wymiary z nagłówka, przed rozpakowaniem) nie dostaje miniatury — idzie pełny plik.
- **Pamięć podręczna**: manifest po czasie modyfikacji i rozmiarze pliku; wymiary i suma kontrolna obrazu po czasie modyfikacji obrazu. Moduł niczego nie zapisuje na dysku.
- **Komentarze** do assetu: typ celu `plik`, cel = `cel_komentarzy` (ścieżka obrazu w repo; zanim obraz powstanie — `assets/processed/<Nazwa>.png`).
- `zdrowie()`: `{manifest, assety, bez_obrazu, czeka_na_zgode, blad?}`. Lustro statyczne dostaje rejestr, obrazy i miniatury pod tymi samymi ścieżkami.

### Lustro statyczne (`bc/statyczny.py`)
`python panel/serwer.py` nie jest potrzebny do podglądu: `python -m bc.statyczny --do <folder>` (z katalogu `panel/`) zapisuje stronę tylko-do-odczytu z odpowiedziami GET jako plikami `dane/<klucz>.json`. W trybie statycznym `static/tryb.js` ustawia `window.BC_STATYCZNY = true`, a `wspolne/api.js` czyta pliki zamiast API. `klucz(ścieżka z zapytaniem)` = 8 znaków hex FNV-1a 32-bit + 8 znaków hex djb2 32-bit, liczone po bajtach UTF-8.

## Kontrakt interfejsu (dla `static/`)
```
static/index.html  app.js  styl.css  tryb.js
static/wspolne/api.js        api(sciezka, {metoda?, cialo?}) → Promise<obiekt>; rzuca Error z .status i .message (pole blad)
                             apiSurowe(sciezka, blob, mime) → Promise; sse(sciezka, naZdarzenie) → {zamknij()}; STATYCZNY (bool)
static/wspolne/ui.js         el(znacznik, atrybuty, …dzieci); ikona(nazwa); czasTemu(iso); dataKrotka(iso); toast(tekst, typ?, {akcja?, czas?});
                             arkusz({tytul, tresc}) → {el, zamknij()} (dolny arkusz na telefonie, okno na komputerze)
static/wspolne/markdown.js   md(tekst, {naWikilink?}) → bezpieczny HTML (nagłówki, listy, pola wyboru, tabele, cytaty i callouty,
                             pogrubienie, kursywa, kod, linki, wikilinki jako <a data-wikilink="Nazwa">)
static/wspolne/komentarze.js komentarze(ctx, cel) → HTMLElement (lista + pole + przycisk głosówki)
static/wspolne/dyktafon.js   dyktafon(ctx, {naTekst}) → HTMLElement (nagrywa albo przyjmuje plik audio; wysyła do /api/glos)
static/widoki/<id>.js        export default { id, tytul, ikona, kolejnosc, utworz(ctx) → { el, pokaz(parametry), ukryj() } }
```
`ctx`: `{api, apiSurowe, sse, ja:{kto, lokalny, game_director, decydent, zapis_sejfu}, statyczny, konfiguracja, idz(id, parametry), toast, licznik(id, n)}`. Widoki i kolejność: `pulpit`, `plan`, `raporty`, `podglad`, `agent`, `siec`, `assety`, `analityka`, `ustawienia`. Nawigacja po `#/<id>`; parametry przekazywane między widokami: `idz("podglad", {migawka, grupa})`, `idz("agent", {kontekst:[{typ, cel, etykieta}], tekst?})`, `idz("siec", {notatka})`, `idz("raporty", {raport})`, `idz("assety", {asset})` (otwiera szczegóły assetu o tej nazwie). Każde żądanie niesie `X-BC-Kto` (imię z Ustawień, `localStorage["bc.kto"]`), a POST także `X-BC: 1`.

Wygląd: ciemny, „warsztat komiksowej gry”. Zmienne CSS w `:root`: `--tlo:#12141c; --karta:#1b1f2b; --karta2:#232838; --obrys:#2a3042; --tekst:#e8eaf2; --przygaszony:#9aa3b8; --zloto:#f5b82e; --fiolet:#8b5cf6; --zielen:#3ecf8e; --czerwien:#ef5a5a; --niebieski:#4ea8ff; --promien:14px`. Klasy wspólne: `.karta`, `.karta-tytul`, `.przycisk` (+ `.glowny`, `.cichy`, `.grozny`, `.maly`), `.chip` (+ `.zloto`, `.zielen`, `.czerwien`, `.fiolet`, `.niebieski`), `.lista`, `.wiersz`, `.siatka` (karty obok siebie od 720 px), `.pusty` (stan pusty z podpowiedzią), `.pasek` > `.pasek-wypelnienie`, `.pole` (input/textarea), `.etykieta`, `.md` (treść z Markdownu), `.cichy-tekst`. Układ: telefon — dolny pasek nawigacji (5 pozycji + „Więcej”), komputer (≥ 900 px) — lewy pasek. Cele dotykowe ≥ 44 px, bez przewijania w poziomie, czcionki systemowe (bez pobierania z sieci), ikony jako SVG w kodzie.
