# BLOCKY & CRYCKET — Panel zespołu

Lokalny panel dla dwóch osób pracujących nad grą: **okno na sejf Obsidiana** (decyzje, harmonogram, zadania), **raporty z wdrożeń** z akceptacją, **podgląd 3D** tego, co jest w Roblox Studio (także z telefonu), **agent Claude Code** na subskrypcji osoby przy komputerze, **głosówki**, **sieć neuronowa** (graf sejfu) i **analityka gry**.

- Uruchomienie i instalacja: [INSTALACJA.md](INSTALACJA.md).
- Zasada nadrzędna (decyzja D-008): **mózgiem projektu jest sejf `B&C/`**. Panel niczego nie trzyma „obok” sejfu: decyzje, zadania i roadmapę czyta z notatek, a własne dane to tylko raporty, komentarze i migawki.
- Stary `dashboard/` (Node/React, agenci przez klucz API) jest archiwalny — panel go nie używa i nie zmienia.

## Architektura

```
przeglądarka (komputer / telefon)
   │  HTTP + SSE, bez kroku budowania (czyste moduły ES, three.js w vendor/)
   ▼
panel/serwer.py  (Python 3.9+, sama biblioteka standardowa, port 8787)
   ├─ bc/sejf.py        czyta notatki B&C/ (i dodatkowe sejfy) → plan, graf, treść notatek
   ├─ bc/gitsync.py     stan repozytorium, pobierz / wyślij dane panelu
   ├─ bc/obecnosc.py    kto jest na panelu, kto w Studio (Team Create), ostatnie commity
   ├─ bc/studio.py      sesja MCP z Roblox Studio (tools/studio_mcp.py)
   ├─ bc/podglad.py     migawki świata gry (części + zrzuty ekranu) → podgląd 3D
   ├─ bc/analityka.py   gracze online / wizyty (publiczne API Roblox), konsola Studio
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
| `%LOCALAPPDATA%\BlockyCrycket\panel\` | kod dostępu, klucz lokalny, log, wątki agenta, nagrania, historia analityki, `konfiguracja.lokalna.json` | **nie** (stan tego komputera) |

**Jeden plik na wpis** (raport, komentarz, migawka) — dwie osoby mogą dopisywać równocześnie i git nigdy nie ma konfliktu.

Porty: panel **8787**. Zajęte przez inne narzędzia: 8765–8767 (Saga), 4310 i 5173 (stary dashboard), 34872 (Rojo).

## Bezpieczeństwo
- Domyślnie tylko `127.0.0.1`. `--lan` otwiera sieć lokalną; każde żądanie spoza komputera wymaga **kodu dostępu** (link z kodem w Ustawieniach → Telefon).
- Prawa osoby przy komputerze (`lokalny`: agent, git, nowa migawka, ustawienia, adresy z kodem) daje **klucz lokalny**, a nie samo połączenie z `127.0.0.1` — tunel, przekierowanie portu i obcy program na tym komputerze też przychodzą z pętli zwrotnej. Klucz leży w danych lokalnych; panel przy starcie otwiera przeglądarkę adresem `/?l=<klucz>`, serwer zamienia go na ciasteczko `bc_l` (HttpOnly, SameSite=Strict) i przekierowuje na adres bez klucza. Programy podają go nagłówkiem `X-BC-Lokalny`. Klucz działa tylko z pętli zwrotnej, z hostem `127.0.0.1`/`localhost` i bez nagłówków pośrednika.
- Wspólna `panel/konfiguracja.json` (z repozytorium) nie może zmienić ustawień bezpieczeństwa: `dozwolone_hosty`, `agent.zdalnie`, `agent.sciezka`, `agent.dozwolone_narzedzia`, `glos.katalog_modeli`, sejfy spoza repozytorium i tryb agenta `auto` działają tylko z `konfiguracja.lokalna.json` na danym komputerze.
- `Host` musi być znany; każdy `POST` wymaga nagłówka `X-BC: 1`; `Origin` musi być własny.
- Agent z telefonu jest **domyślnie wyłączony** (`agent.zdalnie` w konfiguracji lokalnej; przełącznik w Ustawieniach → Telefon, dostępny tylko z kluczem lokalnym) — to zdalne sterowanie komputerem.
- Sekretów nie ma w repozytorium. Nagrania głosowe i rozmowy z agentem zostają na komputerze; do repo trafia tylko tekst komentarza.
- Repozytorium jest **publiczne**: wszystko w `panel/dane/` i w sejfie widzi cały świat.

## Kontrakt serwera (dla modułów `bc/*.py`)
Moduł ma funkcję `zarejestruj(app)` i opcjonalnie `zdrowie() -> dict`. Szczegóły i przykład w nagłówku [`bc/http.py`](bc/http.py); narzędzia wspólne w [`bc/rdzen.py`](bc/rdzen.py) (`REPO`, `DANE`, `RUNTIME`, `konfiguracja()`, `czytaj_json`, `zapisz_json`, `teraz()`, `nowe_id()`, `w_katalogu()`, `uruchom()`, `log()`, `BladHTTP`). Zasady: sama biblioteka standardowa; zapis tylko przez `zapisz_json` / `zapisz_bajty`; nic ciężkiego przy imporcie; operacje wolniejsze niż ~1 s z pamięcią podręczną i limitem czasu; komunikaty błędów po polsku, zrozumiałe dla człowieka. Odpowiedzi błędów: `{"blad": "…"}` ze statusem 4xx/5xx (niepoprawny identyfikator `400`, nieistniejący `404`, „tylko lokalnie” `403`, żądanie spoza komputera bez kodu dostępu `401`).

Testy (z katalogu `panel/`): `python -m unittest discover -s testy -t .` — w tym `testy/test_api.py`, test dymny całego API na prawdziwym serwerze z katalogami tymczasowymi (bez Studio, sieci, agenta i zapisu do gita).

## API
Wszystkie odpowiedzi to JSON, chyba że napisano inaczej. Czasy w ISO 8601 ze strefą. `?` = pole opcjonalne.

### Rdzeń (`serwer.py`)
| Trasa | Odpowiedź |
|---|---|
| `GET /api/ping` | `{ok, app:"bc-panel", wersja, start, pid, port, lan}` |
| `GET /api/ja` | `{kto, lokalny, gospodarz, tryb_statyczny, wersja}` — `kto` z nagłówka `X-BC-Kto` (URL-encoded) albo `git config user.name` |
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
```
Formaty źródłowe: decyzja `### D-001 Tytuł` + linia `✅ zatwierdzona · styl · źródło: …` + opis; roadmapa `## ▶ Faza 1 — Frontend (kanon, w trakcie)` z listą `- [x]`; zadania: sekcje `## 🔥 Teraz (…)` z `- [ ] tekst · #wysoki` (w sekcji assetów kilka pól w jednej linii: `- [ ] A · [x] B`), zrobione `- [x] 2026-11-12: tekst`; pytania `## 1. Tytuł` + treść + `**Odpowiedź:**`; dziennik `## 2026-11-12 · Kto (temat)` + punkty.

### Git (`bc/gitsync.py`)
| Trasa | Odpowiedź / działanie |
|---|---|
| `GET /api/git/stan` | `{galaz, czyste, zmienione:[{plik, stan}], zmiany_panelu, do_wyslania, do_pobrania, ostatni_fetch, ostatnie_commity:[{hash, autor, data, temat}], zdalne}` (fetch w tle najwyżej co 5 min) |
| `POST /api/git/pobierz` | `git pull --rebase --autostash` → `{ok, wyjscie, uwaga?}` (tylko lokalnie) |
| `POST /api/git/wyslij` `{opis?}` | commit **wyłącznie** ścieżek z `git.sciezki_panelu` + push → `{ok, commit?, wyjscie, uwaga?}` (tylko lokalnie) |

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

`raport`: `{id, tytul, opis_md, kto, czas, rodzaj:"wdrozenie"|"pytanie"|"informacja", status:"czeka"|"zaakceptowane"|"do_poprawy"|"informacja", komponenty:[{typ:"studio"|"notatka"|"plik"|"migawka", cel, etykieta}], migawka?, zrzuty:[nazwa…], pytanie?, decyzja?:{kto, czas, wartosc, komentarz}, komentarzy}`. `status` wynika z `rodzaj` i decyzji (wdrożenie/pytanie bez decyzji = `czeka`; decyzja ma pierwszeństwo, liczy się ostatnia). `migawka` musi istnieć w `panel/dane/podglad/` (inaczej `400`); zrzuty dołącza tylko CLI (`--zrzut`). Typy celu komentarza: `raport` (id), `studio` (ścieżka grupy, np. `Workspace/DemoLesnaBaza/Karczma`), `notatka` (ścieżka w repo), `migawka` (id).

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

### Lustro statyczne (`bc/statyczny.py`)
`python panel/serwer.py` nie jest potrzebny do podglądu: `python -m bc.statyczny --do <folder>` (z katalogu `panel/`) zapisuje stronę tylko-do-odczytu z odpowiedziami GET jako plikami `dane/<klucz>.json`. W trybie statycznym `static/tryb.js` ustawia `window.BC_STATYCZNY = true`, a `wspolne/api.js` czyta pliki zamiast API. `klucz(ścieżka z zapytaniem)` = 8 znaków hex FNV-1a 32-bit + 8 znaków hex djb2 32-bit, liczone po bajtach UTF-8.

## Kontrakt interfejsu (dla `static/`)
```
static/index.html  app.js  styl.css  tryb.js
static/wspolne/api.js        api(sciezka, {metoda?, cialo?}) → Promise<obiekt>; rzuca Error z .status i .message (pole blad)
                             apiSurowe(sciezka, blob, mime) → Promise; sse(sciezka, naZdarzenie) → {zamknij()}; STATYCZNY (bool)
static/wspolne/ui.js         el(znacznik, atrybuty, …dzieci); ikona(nazwa); czasTemu(iso); dataKrotka(iso); toast(tekst, typ?);
                             arkusz({tytul, tresc}) → {el, zamknij()} (dolny arkusz na telefonie, okno na komputerze)
static/wspolne/markdown.js   md(tekst, {naWikilink?}) → bezpieczny HTML (nagłówki, listy, pola wyboru, tabele, cytaty i callouty,
                             pogrubienie, kursywa, kod, linki, wikilinki jako <a data-wikilink="Nazwa">)
static/wspolne/komentarze.js komentarze(ctx, cel) → HTMLElement (lista + pole + przycisk głosówki)
static/wspolne/dyktafon.js   dyktafon(ctx, {naTekst}) → HTMLElement (nagrywa albo przyjmuje plik audio; wysyła do /api/glos)
static/widoki/<id>.js        export default { id, tytul, ikona, kolejnosc, utworz(ctx) → { el, pokaz(parametry), ukryj() } }
```
`ctx`: `{api, apiSurowe, sse, ja:{kto, lokalny}, statyczny, konfiguracja, idz(id, parametry), toast, licznik(id, n)}`. Widoki i kolejność: `pulpit`, `plan`, `raporty`, `podglad`, `agent`, `siec`, `analityka`, `ustawienia`. Nawigacja po `#/<id>`; parametry przekazywane między widokami: `idz("podglad", {migawka, grupa})`, `idz("agent", {kontekst:[{typ, cel, etykieta}], tekst?})`, `idz("siec", {notatka})`, `idz("raporty", {raport})`. Każde żądanie niesie `X-BC-Kto` (imię z Ustawień, `localStorage["bc.kto"]`), a POST także `X-BC: 1`.

Wygląd: ciemny, „warsztat komiksowej gry”. Zmienne CSS w `:root`: `--tlo:#12141c; --karta:#1b1f2b; --karta2:#232838; --obrys:#2a3042; --tekst:#e8eaf2; --przygaszony:#9aa3b8; --zloto:#f5b82e; --fiolet:#8b5cf6; --zielen:#3ecf8e; --czerwien:#ef5a5a; --niebieski:#4ea8ff; --promien:14px`. Klasy wspólne: `.karta`, `.karta-tytul`, `.przycisk` (+ `.glowny`, `.cichy`, `.grozny`, `.maly`), `.chip` (+ `.zloto`, `.zielen`, `.czerwien`, `.fiolet`, `.niebieski`), `.lista`, `.wiersz`, `.siatka` (karty obok siebie od 720 px), `.pusty` (stan pusty z podpowiedzią), `.pasek` > `.pasek-wypelnienie`, `.pole` (input/textarea), `.etykieta`, `.md` (treść z Markdownu), `.cichy-tekst`. Układ: telefon — dolny pasek nawigacji (5 pozycji + „Więcej”), komputer (≥ 900 px) — lewy pasek. Cele dotykowe ≥ 44 px, bez przewijania w poziomie, czcionki systemowe (bez pobierania z sieci), ikony jako SVG w kodzie.
