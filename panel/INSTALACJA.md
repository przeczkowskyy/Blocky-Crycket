# Panel zespołu — instalacja i uruchomienie

Panel działa na Twoim komputerze i **nie wymaga instalowania niczego poza Pythonem** (3.9 lub nowszym) i Gitem. Trzy kroki zajmują około dwóch minut.

> **Najprościej: poproś swojego Claude Code.** Wklej mu:
> *„Przeczytaj `panel/INSTALACJA.md` i wykonaj kroki 1–3. Jeśli kontrola pokaże problem, napraw go według podpowiedzi z tego pliku. Niczego nie instaluj bez pytania. Na końcu podaj mi adres panelu.”*

## 1. Pobierz aktualną wersję
```
git pull
```
Jeśli po tym nie masz folderu `panel/`, zmiany są jeszcze na gałęzi roboczej: `git fetch origin`, a potem `git switch karol/panel-wiedza-demo`.

## 2. Sprawdź środowisko
```
python panel/serwer.py --sprawdz
```
Na końcu ma być `WYNIK: gotowe do uruchomienia`. Linie w nawiasach kwadratowych pokazują, co panel znalazł: Roblox Studio, Claude Code, Whisper (głosówki).

## 3. Uruchom
Dwuklik w `panel\start.bat` albo:
```
python panel/serwer.py
```
Panel otworzy się w przeglądarce (`http://127.0.0.1:8787`). Przy pierwszym wejściu zapyta o imię — podpisuje nim komentarze i decyzje. Okno z serwerem zostaw otwarte; `Ctrl+C` zatrzymuje panel.

**Klucz lokalny.** Przy starcie panel otwiera się adresem z jednorazowo wypisanym kluczem (`…/?l=…`), a przeglądarka zapamiętuje go na rok. Ten klucz mówi panelowi, że siedzisz przy komputerze: tylko wtedy działa agent, git, nowa migawka i ustawienia. Kto wejdzie bez klucza (inny program na komputerze, telefon, tunel), zobaczy prośbę o kod dostępu i dostanie uprawnienia gościa. Jeśli panel poprosi o kod na Twoim własnym komputerze (inna przeglądarka, wyczyszczone ciasteczka), uruchom jeszcze raz `panel\start.bat` — otworzy działający panel z kluczem. Adresu z kluczem nikomu nie wysyłaj.

## Co działa od razu, a co wymaga dodatków
| Funkcja | Wymaga |
|---|---|
| Pulpit, Plan (decyzje, zadania, roadmapa), Raporty, Sieć notatek | nic |
| Odpowiadanie na pytania otwarte, odhaczanie i dodawanie zadań (zapis w sejfie) | nic — także dla gościa z kodem dostępu |
| Zatwierdzanie i odrzucanie decyzji (zmiana kanonu) | link Game Directora (niżej) |
| Podgląd 3D zapisanych migawek | nic |
| Assety — rejestr grafik gry z `assets/manifest.json`: statusy, numery Roblox, linki do Figmy (tylko podgląd) | nic |
| Nowa migawka ze Studio, „kto jest w Studio”, konsola Studio | uruchomione Roblox Studio z włączonym serwerem MCP (niżej) |
| Agent | Claude Code zainstalowany i zalogowany na tym komputerze |
| Głosówki zamieniane na tekst | `pip install faster-whisper` (model ok. 1,6 GB pobiera się przy pierwszym nagraniu) |
| Mniejsze zrzuty w migawkach i raportach, lekkie miniatury w Assetach | `pip install pillow` (opcjonalnie) |
| Wejście z telefonu | uruchomienie przez `panel\start_lan.bat` (niżej) |

### Praca na sejfie i Game Director
W zakładce **Plan** można pracować wprost na sejfie: odpowiadać na pytania otwarte, odhaczać i dodawać zadania. Panel zapisuje to w tych samych plikach co Obsidian (`B&C/Produkcja/Pytania otwarte.md`, `Zadania.md`, `Dziennik zmian.md`) — małymi zmianami, z podpisem imieniem z Ustawień i wpisem w Dzienniku zmian. Jeśli w tym samym czasie ktoś zmienił plik (druga osoba, Obsidian, agent), panel nic nie nadpisze: pokaże „Ktoś zmienił ten plik — odświeżam” i zostawi wpisany tekst do ponownego wysłania.

**Co wolno gościowi** (telefon, tunel, wejście z kodem dostępu): czytać wszystko, komentować, odpowiadać na pytania, odhaczać i dodawać zadania (najwyżej 30 zapisów na 10 minut). Nie wolno: agent (chyba że włączony „Agent z telefonu”), git, nowa migawka, ustawienia — i **zmiana statusu decyzji**.

**Podpis odpowiedzi.** Imię z Ustawień każdy wpisuje sam, dlatego serwer dopisuje znacznik: `- Paweł (Game Director, 2026-11-13): …` (przeglądarka z kluczem Game Directora), `- Karol (2026-11-13): …` (komputer z panelem), `- Paweł (gość panelu, 2026-11-13): …` (gość z kodem dostępu). **Zgodą Game Directora jest tylko odpowiedź ze znacznikiem „(Game Director, data)”** — „Tak, zatwierdzam” od „gościa panelu” nią nie jest, nawet podpisane „Paweł”. Pod polem odpowiedzi panel pokazuje, jak zostanie podpisana. Uwaga: włączony „Agent z telefonu” pozwala gościowi z kodem dostępu zmieniać przez agenta dowolne pliki sejfu — klucz Game Directora tego nie blokuje.

**Zatwierdzanie decyzji to zmiana kanonu** — może ją zrobić tylko Game Director. Samo imię „Paweł” w Ustawieniach nic nie daje; potrzebny jest **klucz Game Directora**:
1. Na komputerze, na którym działa panel, uruchom:
   ```
   python panel/serwer.py --klucz-gd
   ```
   Polecenie wypisze link `http://127.0.0.1:8787/?gd=…` (klucz leży w `%LOCALAPPDATA%\BlockyCrycket\panel\klucz_gd.txt`).
2. Game Director przy tym komputerze: otwiera link w przeglądarce, w której działa już panel.
   Game Director zdalnie (tunel, telefon): do adresu z kodem dostępu dopisuje `&gd=…`, np. `https://<adres-tunelu>/?k=<kod>&gd=<klucz>`.
3. Przeglądarka zapamięta klucz na rok i usunie go z adresu. W **Ustawieniach** pojawi się „Game Director: tak”, a w **Plan → Decyzje** przy propozycjach i decyzjach „do decyzji” przyciski **Zatwierdź** / **Odrzuć** (z potwierdzeniem i polem na uzasadnienie). Pozostali widzą tam „Zatwierdza Game Director” i mogą komentować.

Link działa jak hasło: przekaż go tylko Game Directorowi i nie wklejaj w publicznych miejscach (repozytorium jest publiczne). Gdy wycieknie: `python panel/serwer.py --nowy-klucz-gd` — stary klucz przestaje działać od razu, bez restartu panelu.

Zmiany sejfu z panelu wysyła ten sam przycisk **Pulpit → Wyślij** (commit `panel: …`), ale tylko pliki, które naprawdę zmienił panel. Okno „Wyślij” pokazuje dodane i usunięte wiersze tych plików — repozytorium jest publiczne, więc przejrzyj, co piszą goście, zanim klikniesz. Jeśli w tym samym pliku są też Twoje niezatwierdzone zmiany z Obsidiana albo od agenta, panel go pominie i powie, żeby wysłać go zwykłym commitem. Zapis do sejfu można wyłączyć wpisem `"zapis_sejfu": false` w konfiguracji.

### Roblox Studio
W Studio: **Assistant → … → Manage MCP Servers → Enable Studio as MCP server**. Test z terminala:
```
python tools/studio_mcp.py studios
```
Ma wypisać otwarte miejsce. Zrzuty ekranu do migawek wychodzą czarne, gdy okno Studio jest zminimalizowane — przed kliknięciem „Nowa migawka” przywróć okno.

### Agent
Panel sam szuka programu `claude` (PATH, `%USERPROFILE%\.local\bin`, rozszerzenie VS Code). Agent działa na Twojej subskrypcji Claude — tak samo jak Claude Code w edytorze, w tym samym folderze projektu. Gdy panel go nie znajdzie, wpisz ścieżkę w pliku `%LOCALAPPDATA%\BlockyCrycket\panel\konfiguracja.lokalna.json`:
```json
{ "agent": { "sciezka": "C:/pełna/ścieżka/do/claude.exe" } }
```
Tryby: **Plan** (tylko czyta i planuje), **Praca** (edytuje pliki i używa dozwolonych narzędzi, reszty odmawia), **Auto**.

### Telefon
1. Uruchom `panel\start_lan.bat` (albo `python panel/serwer.py --lan`). Windows może zapytać o zgodę zapory — zezwól dla sieci prywatnej.
2. W panelu: **Ustawienia → Telefon** — skopiuj adres z kodem i otwórz go w telefonie podłączonym do tej samej sieci Wi-Fi.
3. Głosówki z telefonu w sieci domowej idą przez dyktafon telefonu (przeglądarka nie daje mikrofonu stronom bez https).
4. Agent z telefonu jest domyślnie **wyłączony**, bo to zdalne sterowanie komputerem. Świadome włączenie: na komputerze z panelem **Ustawienia → Telefon → „Agent z telefonu” → Włącz**. Od tej chwili każdy, kto ma kod dostępu, może zlecać agentowi pracę (najwyżej w trybie Praca); wyłącza się tym samym przyciskiem.

### Jeden panel dla obu osób na żywo (tunel, opcjonalnie)
Domyślnie każdy uruchamia panel u siebie, a wspólne dane płyną przez git (Pobierz / Wyślij). Gdy chcecie patrzeć na **ten sam** panel jednocześnie albo wejść z telefonu poza domem przy włączonym komputerze:
1. Pobierz darmowy `cloudflared` (bez konta). Najprościej wersję przenośną — jeden plik `cloudflared-windows-amd64.exe` z oficjalnej strony wydań Cloudflare, bez instalatora i bez uprawnień administratora. (`winget install Cloudflare.cloudflared` też działa, ale instalator prosi o uprawnienia administratora.)
2. W `%LOCALAPPDATA%\BlockyCrycket\panel\konfiguracja.lokalna.json` dopisz: `{ "dozwolone_hosty": [".trycloudflare.com"] }`.
3. Uruchom panel jak zwykle, a w drugim oknie: `cloudflared tunnel --url http://127.0.0.1:8787` — program wypisze adres `https://….trycloudflare.com`.
4. Wyślij drugiej osobie ten adres z dopiskiem `/?k=<kod>` (kod: Ustawienia → Telefon).

Wejście przez tunel zawsze wymaga kodu i nie ma uprawnień osoby przy komputerze: agent, git i nowa migawka są dla niego wyłączone. Adres zmienia się przy każdym uruchomieniu tunelu. Zabezpieczenia sprawdzone 13.11.2026 na prawdziwym tunelu, od zewnątrz: bez kodu panel odmawia, z kodem gość nie ma agenta, gita ani lokalnych ścieżek, a klucz lokalny przez tunel nie działa.

**Zanim wyślesz adres drugiej osobie:** jeśli w `konfiguracja.lokalna.json` masz podpięte prywatne sejfy (np. własne notatki), wyjmij je na czas tunelu — gość z kodem widzi wszystkie sejfy panelu. Komputer musi zostać włączony i nie może zasnąć.

Poza domem, przy wyłączonym komputerze, działa **lustro tylko do odczytu** (plan, raporty, podgląd 3D, sieć): `python panel/serwer.py --eksport <folder>` zapisuje stronę statyczną, którą można wystawić np. na GitHub Pages (workflow `.github/workflows/panel-lustro.yml`, uruchamiany ręcznie po włączeniu Pages w ustawieniach repozytorium).

## Codzienna praca we dwóch
1. **Pulpit → Pobierz** (albo `git pull`) — ściąga raporty, komentarze i migawki drugiej osoby.
2. Pracujesz z Claude'em; po wdrożeniu Claude publikuje migawkę i raport (skill `.claude/skills/panel/`).
3. Oglądasz raport, klikasz **Akceptuję** albo **Do poprawy**, komentujesz elementy w podglądzie 3D. W **Plan** odpowiadasz na pytania, odhaczasz zadania, a Game Director zatwierdza decyzje.
4. **Pulpit → Wyślij** — commit i push danych panelu (`panel/dane/`) i plików sejfu zmienionych w panelu. Resztę zmian commitujesz jak zwykle.

Pamiętaj: repozytorium jest publiczne, więc raporty i komentarze widzi każdy. Rozmowy z agentem i nagrania głosowe zostają tylko na Twoim komputerze.

## Gdy coś nie działa
| Objaw | Co zrobić |
|---|---|
| „Nie mogę zająć portu 8787” | port zajął inny program: `python panel/serwer.py --port 8790` (gdy panel już działa, drugie uruchomienie samo otwiera go w przeglądarce) |
| Panel prosi o kod dostępu na komputerze, na którym działa | uruchom `panel\start.bat` — otworzy panel z kluczem lokalnym; wejście „z ręki” pod `127.0.0.1:8787` w nowej przeglądarce nie ma klucza |
| Moduł z błędem w `--sprawdz` | przeczytaj komunikat; `git pull`; szczegóły w `%LOCALAPPDATA%\BlockyCrycket\panel\panel.log` |
| Studio „niepodłączone” | Studio musi być uruchomione z włączonym serwerem MCP; test `python tools/studio_mcp.py studios` |
| Agent „niedostępny” | zainstaluj Claude Code i zaloguj się; w razie potrzeby podaj ścieżkę w `konfiguracja.lokalna.json` |
| Głosówka „brak Whispera” | `pip install faster-whisper` |
| „Nieznany adres panelu” w przeglądarce | wchodź przez `127.0.0.1` / `localhost` albo adres z Ustawień → Telefon; własną nazwę hosta dopisz do `dozwolone_hosty` w `konfiguracja.lokalna.json` |
| Telefon nie łączy się | ta sama sieć Wi-Fi, panel uruchomiony z `--lan`, zgoda w zaporze Windows |

## Gdzie są dane
| Dane | Miejsce |
|---|---|
| Wspólne (raporty, komentarze, migawki) | `panel/dane/` w repozytorium |
| Odpowiedzi, zadania, statusy decyzji z panelu | w sejfie: `B&C/Produkcja/*.md` (te same pliki co w Obsidianie) |
| Tylko ten komputer (kod dostępu, klucz lokalny, klucz Game Directora, log, rozmowy z agentem, nagrania, ustawienia lokalne) | `%LOCALAPPDATA%\BlockyCrycket\panel\` |

Usunięcie folderu z danymi lokalnymi przywraca panel do stanu początkowego; danych wspólnych to nie rusza.

## Testy (dla rozwijających panel)
```
cd panel
python -B -m unittest discover -s testy -t .
```
(`-B` = bez plików `__pycache__` w folderze projektu.)
