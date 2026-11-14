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
| Pulpit, Pytania (lista „Do odpowiedzi”, historia, wyszukiwarka, zadania, roadmapa, dziennik), Sieć notatek | nic |
| Odpowiadanie na pytania otwarte, odhaczanie i dodawanie zadań (zapis w sejfie) | nic — także dla gościa z kodem dostępu |
| Zatwierdzanie i odrzucanie decyzji (zmiana kanonu, Karol albo Paweł) | komputer z panelem albo link z kluczem zatwierdzania (niżej) i imię w Ustawieniach |
| Potwierdzanie decyzji drugiej osoby w panelu (Zgoda / Brak zgody / Przedyskutuj) | to samo co zatwierdzanie |
| Alert o decyzji na telefon i potwierdzanie przyciskiem w Telegramie | bot Telegram i plik `telegram.json` na komputerze z panelem (niżej); komputer musi być włączony |
| Podgląd 3D zapisanych migawek | nic |
| Assety — rejestr grafik gry z `assets/manifest.json`: statusy, numery Roblox, linki do Figmy (tylko podgląd) | nic |
| Nowa migawka ze Studio, „kto jest w Studio”, konsola Studio | uruchomione Roblox Studio z włączonym serwerem MCP (niżej) |
| Agent | Claude Code zainstalowany i zalogowany na tym komputerze |
| Głosówki zamieniane na tekst | `pip install faster-whisper` (model ok. 1,6 GB pobiera się przy pierwszym nagraniu) |
| Sesja: rozmowa głosowa w panelu | przeglądarka z mikrofonem; strona po https (link tunelu) albo na komputerze z panelem |
| Sesja: „Agent słucha” (transkrypcja i notatki) | to samo co głosówki (`faster-whisper`) i — do notatek i ustaleń — Claude Code na komputerze z panelem |
| Mniejsze zrzuty w migawkach i raportach, lekkie miniatury w Assetach | `pip install pillow` (opcjonalnie) |
| Wejście z telefonu | uruchomienie przez `panel\start_lan.bat` (niżej) |

### Praca na sejfie i zatwierdzanie decyzji
W zakładce **Pytania** można pracować wprost na sejfie: odpowiadać na pytania otwarte, zatwierdzać decyzje, akceptować raporty, odhaczać i dodawać zadania. Na górze jest wyszukiwarka i jedna lista **Do odpowiedzi** — wszystko, co czeka na człowieka, a każda pozycja to pytanie: pytanie z notatki Pytania otwarte (z polem odpowiedzi), decyzja „Czy zatwierdzamy: …?” (przyciski **Tak** / **Nie**) albo raport „Czy akceptujesz: …?” (**Akceptuję** / **Do poprawy**). Bez dubli: pytanie i decyzje, które je rozstrzygają (wiersz `Rozstrzyga: D-0XX` w notatce Pytania otwarte), są jedną kartą, a zatwierdzenie ostatniej takiej decyzji samo zamyka pytanie. Najnowsze i najważniejsze są na górze. Pod listą jest historia **Odpowiedziane** (pytania z odpowiedziami, decyzje po zatwierdzeniu albo odrzuceniu, raporty po decyzji) i zwijany **Plan** (zadania, roadmapa, dziennik zmian). Lista odświeża się sama (co kilkanaście sekund i po każdej akcji), ale nie rusza karty, w której właśnie piszesz. Przycisk **Na sesję główną** odkłada sprawę do agendy zakładki Sesja; tę samą listę pytań widać w zakładce **Sesja** obok Agendy, żeby odpowiadać w trakcie rozmowy. Dawne adresy zakładek Plan, Raporty i Decyzje (np. zapisane zakładki w telefonie) same przechodzą do Pytań. Kto jest teraz na panelu (i w której zakładce, czy rozmawia w Sesji, czy agent słucha), widać w lewym dolnym rogu; na telefonie — znaczek z liczbą osób w górnym pasku. Panel zapisuje to w tych samych plikach co Obsidian (`B&C/Produkcja/Pytania otwarte.md`, `Zadania.md`, `Dziennik zmian.md`) — małymi zmianami, z podpisem imieniem z Ustawień i wpisem w Dzienniku zmian. Jeśli w tym samym czasie ktoś zmienił plik (druga osoba, Obsidian, agent), panel nic nie nadpisze: pokaże „Ktoś zmienił ten plik — odświeżam” i zostawi wpisany tekst do ponownego wysłania.

**Co wolno gościowi** (telefon, tunel, wejście z kodem dostępu): czytać wszystko, komentować, odpowiadać na pytania, odhaczać i dodawać zadania (najwyżej 30 zapisów na 10 minut). Nie wolno: agent (chyba że włączony „Agent z telefonu”), git, nowa migawka, ustawienia — i **zmiana statusu decyzji**.

**Podpis odpowiedzi.** Imię z Ustawień każdy wpisuje sam, dlatego serwer dopisuje znacznik: `- Paweł (klucz zatwierdzania, 2026-11-13): …` (przeglądarka z kluczem zatwierdzania), `- Karol (2026-11-13): …` (komputer z panelem), `- Paweł (gość panelu, 2026-11-13): …` (gość z kodem dostępu). **Zgodą jest tylko odpowiedź z komputera z panelem albo ze znacznikiem „(klucz zatwierdzania, data)”** — „Tak, zatwierdzam” od „gościa panelu” nią nie jest, nawet podpisane „Paweł”. Wpisy z 13.11.2026 sprzed tej zmiany mają znacznik „(Game Director, data)” — znaczy on to samo co „klucz zatwierdzania”. Pod polem odpowiedzi panel pokazuje, jak zostanie podpisana. Uwaga: włączony „Agent z telefonu” pozwala gościowi z kodem dostępu zmieniać przez agenta dowolne pliki sejfu — klucz zatwierdzania tego nie blokuje.

**Zatwierdzanie decyzji to zmiana kanonu.** Od 13.11.2026 Karol i Paweł mają równe prawa: wystarcza decyzja jednego z nich, a panel podpisuje każdą imieniem i datą (w Rejestrze decyzji `zdecydował: Paweł 2026-11-13`, przy „do decyzji” `oznaczył: Karol 2026-11-13`; ślad w Dzienniku zmian). Dlatego przed zatwierdzaniem **wpisz swoje imię w Ustawieniach** — bez imienia panel decyzji nie zapisze. Dotyczy to także komputera z panelem: imię, którym podpisuje się tam Git, nie wystarcza (do publicznego Rejestru trafiłoby pełne imię i nazwisko albo nazwa konta), więc imię trzeba zapisać w Ustawieniach tej przeglądarki. W panelu decyzję może zmienić:
- osoba **przy komputerze, na którym działa panel** — bez żadnego dodatkowego klucza;
- przeglądarka z **kluczem zatwierdzania** (dawniej „klucz Game Directora”) — także zdalnie, przez tunel albo z telefonu.

Samo imię „Paweł” w Ustawieniach nic nie daje; gość z samym kodem dostępu decyzji nie zmienia. Klucz zatwierdzania:
1. Na komputerze, na którym działa panel, uruchom:
   ```
   python panel/serwer.py --klucz-zatwierdzania
   ```
   Polecenie wypisze link `http://127.0.0.1:8787/?gd=…` (klucz leży w `%LOCALAPPDATA%\BlockyCrycket\panel\klucz_gd.txt`). Dawna nazwa polecenia, `--klucz-gd`, działa dalej, a link zapisany wcześniej w przeglądarce nadal działa.
2. Przy tym komputerze: otwórz link w przeglądarce, w której działa już panel.
   Zdalnie (tunel, telefon): do adresu z kodem dostępu dopisz `&gd=…`, np. `https://<adres-tunelu>/?k=<kod>&gd=<klucz>`.
3. Przeglądarka zapamięta klucz na rok i usunie go z adresu. W **Ustawieniach** pojawi się „Zatwierdzanie decyzji: tak”, a w zakładce **Pytania** przy decyzjach „Czy zatwierdzamy: …?” przyciski **Tak** / **Nie** (z potwierdzeniem, podglądem podpisu i polem na uzasadnienie). Pozostali widzą tam „Zatwierdza Karol albo Paweł (klucz zatwierdzania)” i mogą komentować.

Link działa jak hasło: przekaż go tylko Karolowi albo Pawłowi i nie wklejaj w publicznych miejscach (repozytorium jest publiczne). Gdy wycieknie: `python panel/serwer.py --nowy-klucz-zatwierdzania` (dawniej `--nowy-klucz-gd`) — stary klucz przestaje działać od razu, bez restartu panelu.

**Druga osoba potwierdza (decyzja D-043).** Gdy Karol zatwierdzi albo odrzuci decyzję, Paweł dostaje pytanie (i odwrotnie): w zakładce **Pytania** jako „Karol zatwierdził: … — zgadzasz się?” z przyciskami **Zgoda**, **Brak zgody** (z polem na powód) i **Przedyskutuj** (temat trafia na agendę sesji głównej), a gdy działa bot — także na Telegramie. Decyzja z jednym podpisem to robocze ustalenie; obowiązuje po zgodzie drugiej osoby (w Rejestrze: `… · zdecydował: Karol 2026-11-14 · potwierdził: Paweł 2026-11-14`). Brak zgody i „przedyskutuj” cofają decyzję na „do decyzji” i zostawiają ślad w Rejestrze. Własnej decyzji nie da się potwierdzić. W historii **Odpowiedziane** Twoje decyzje mają znacznik „Czeka na potwierdzenie: Paweł”, a po potwierdzeniu „Dwa podpisy”.

Zmiany sejfu z panelu wysyła ten sam przycisk **Pulpit → Wyślij** (commit `panel: …`), ale tylko pliki, które naprawdę zmienił panel. Okno „Wyślij” pokazuje dodane i usunięte wiersze tych plików — repozytorium jest publiczne, więc przejrzyj, co piszą goście, zanim klikniesz. Jeśli w tym samym pliku są też Twoje niezatwierdzone zmiany z Obsidiana albo od agenta, panel go pominie i powie, żeby wysłać go zwykłym commitem. Zapis do sejfu można wyłączyć wpisem `"zapis_sejfu": false` w konfiguracji.

### Bot Telegram (potwierdzanie decyzji)
Bot wysyła drugiej osobie alert o decyzji z przyciskami **Zgoda / Brak zgody / Przedyskutuj** i zapisuje odpowiedź w sejfie. Działa na **jednym** komputerze — tym, na którym stale chodzi panel (dwa panele z tym samym botem przeszkadzają sobie). Komputer musi być włączony, żeby alert wyszedł i kliknięcie się zapisało (kliknięcia z czasu, gdy był wyłączony, Telegram przechowuje do 24 godzin).

1. **Bot.** W Telegramie napisz do **@BotFather**: `/newbot`, podaj nazwę (np. „B&C decyzje”) i nazwę konta bota kończącą się na `bot`. BotFather poda **token** — działa jak hasło: nie wklejaj go do repozytorium, czatu z agentem ani do grupy.
2. **Grupa.** Załóż grupę (np. „B&C decyzje”) z Karolem i Pawłem i dodaj do niej bota. Ustawień prywatności bota nie trzeba zmieniać (bot widzi komendy, kliknięcia i odpowiedzi na swoje wiadomości).
3. **Numery.** Każdy pisze w grupie cokolwiek, np. `/start`. Numery osób i grupy odczytasz, otwierając w przeglądarce `https://api.telegram.org/bot<TOKEN>/getUpdates` (z prawdziwym tokenem, **zanim** zapiszesz go w panelu — działający bot sam odbiera te wiadomości): `from.id` to numer osoby, `chat.id` (ujemny) to numer grupy. Gdy panel już działa z botem, `/start` w grupie od osoby, której bot nie zna, odpowie jej numerem.
4. **Plik ustawień.** Na komputerze z panelem utwórz `%LOCALAPPDATA%\BlockyCrycket\panel\telegram.json` (poza repozytorium). Przykład na **zmyślonych** wartościach:
   ```json
   {
     "token": "123456:TU-WKLEJ-TOKEN-OD-BOTFATHERA",
     "bot": "bc_decyzje_przyklad_bot",
     "osoby": { "100000001": "Karol", "100000002": "Paweł" },
     "grupy": { "-1001000000001": "B&C decyzje" }
   }
   ```
   Imiona w `osoby` to krótkie imiona (pierwsze słowo imienia z Ustawień panelu). Panel czyta plik przy starcie i po każdej zmianie — odbiór wiadomości startuje po restarcie panelu z nową wersją, potem zmiana pliku działa bez restartu.
5. **Próba.** W grupie wpisz `/start` — bot odpowie „Znam Cię”. `/czeka` pokaże decyzje, które czekają na Twoje potwierdzenie (po 5 naraz, dalej „Następne”), `/pomoc` — krótki opis. Stan bota (bez tokenu): `GET /api/telegram/stan` na komputerze z panelem.

Przy **Brak zgody** bot prosi o krótki powód — odpowiedz na jego wiadomość w ciągu 15 minut, a powód trafi do Rejestru decyzji (można nic nie pisać). Bez pliku `telegram.json` panel działa jak dotąd, a potwierdzać można w zakładce Pytania. Token wyciekł: w @BotFather `/revoke` (nowy token) i wpisz go do pliku.

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

Agent zawsze działa na subskrypcji osoby zalogowanej w Claude Code **na komputerze z panelem** — także gdy pisze do niego ktoś z telefonu albo przez tunel (np. Paweł do panelu Karola). Na liście rozmów w zakładce **Agent** widać przy każdym wątku, kto go założył i czy zdalnie, oraz kto jeszcze w nim pisał. Jeśli druga osoba ma pracować na własnej subskrypcji, musi uruchomić agenta (Claude Code albo własny panel) na swoim komputerze.

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

### Sesja — długa rozmowa głosowa we dwóch (zakładka „Sesja”)
Zakładka działa jak rozmowa na Discordzie, tylko w panelu: obaj wchodzicie na **ten sam** panel, klikacie **Dołącz** i rozmawiacie. Po włączeniu **Agent słucha** agent spisuje rozmowę, co kilka minut robi notatki, a na koniec spisuje ustalenia do sejfu jako propozycje do zatwierdzenia.
1. **Gospodarz** (osoba, na której komputerze działa panel): uruchamia panel jak zwykle (`panel\start.bat`) i tunel jak w części wyżej (`cloudflared tunnel --url http://127.0.0.1:8787`). Wysyła drugiej osobie adres `https://….trycloudflare.com/?k=<kod>`. Sam wchodzi w zakładkę **Sesja** na swoim komputerze (adres `127.0.0.1` też jest „bezpieczny” dla mikrofonu).
2. **Druga osoba** otwiera link tunelu (https — tylko po https przeglądarka daje mikrofon), wpisuje swoje imię, wchodzi w **Sesja** i klika **Dołącz**.
3. **Zgoda na mikrofon**: przy pierwszym „Dołącz” przeglądarka zapyta o mikrofon — trzeba kliknąć **Zezwól**. Gdy ktoś kliknął „Blokuj”: ikona kłódki (albo mikrofonu) przy adresie → Mikrofon → Zezwalaj, potem jeszcze raz Dołącz. Bez mikrofonu można słuchać.
4. **Agent słucha** włącza Karol albo Paweł: przy komputerze z panelem albo z kluczem zatwierdzania (link z `--klucz-zatwierdzania`, przez tunel dopisany `&gd=…`). Wszyscy w pokoju widzą wtedy czerwony znacznik. Każdy nagrywa **swój** mikrofon, więc w zapisie przy każdej wypowiedzi jest właściwe imię. Nagrania i zapis zostają na komputerze z panelem; dźwięk jest kasowany zaraz po spisaniu.
5. **Rozłącz** i wyłączenie „Agent słucha” nie gubią ostatnich zdań — przeglądarka wysyła jeszcze nagrany do tej chwili kawałek.
6. **Notatki teraz** i **Zakończ sesję i spisz ustalenia** uruchamiają agenta na subskrypcji gospodarza — działają przy komputerze z panelem (zdalnie tylko z kluczem zatwierdzania i włączonym „Agentem z telefonu”). Tematy na rozmowę zbiera notatka sejfu **Sesje główne** (agenda w zakładce; „Zaproponuj tematy” prosi agenta o propozycje).

**Przeglądarki:** Chrome, Edge i Firefox na komputerze; Chrome na Androidzie; Safari na iPhonie (iOS 14.3+; tej przeglądarki nie sprawdzaliśmy jeszcze w prawdziwej rozmowie). Telefon nie może przejść w uśpienie w trakcie rozmowy — zgaszony ekran zwykle wyłącza mikrofon. Gdy panel pokaże „Miernik mikrofonu nie działa w tej przeglądarce”, nagrywanie i tak działa (agent dostaje całe nagranie); gdy pokaże „Agent może cię nie słyszeć”, sprawdź, czy przeglądarka używa właściwego mikrofonu.

**Przed pierwszą prawdziwą sesją** warto sprawdzić, czy komputer z panelem nadąża ze spisywaniem: włączcie „Agent słucha” na kilka minut i patrzcie na „Czeka na spisanie”. Jeśli ta liczba stale rośnie (panel pokaże „Transkrypcja nie nadąża”), tekst pojawia się coraz później, a na koniec agent może spisać ustalenia z niepełnego zapisu (napisze to wprost). Pomaga zamknięcie ciężkich programów na komputerze z panelem.

**Gdy głos się nie łączy** (panel pokaże „Głosu nie udało się połączyć bezpośrednio”): niektóre sieci (np. komórkowe, firmowe) nie przepuszczają bezpośredniego połączenia. Wtedy rozmawiajcie przez Discord, a zakładkę Sesja zostawcie otwartą z włączonym mikrofonem — nagrywanie i transkrypcja działają dalej, bo każdy wysyła swój mikrofon do panelu zwykłym https. Na stałe pomaga serwer TURN — tylko w konfiguracji lokalnej, nigdy w repozytorium: `{ "sesje": { "turn": { "adres": "turn:…:3478", "uzytkownik": "…", "haslo": "…" } } }`. Echo albo pisk: załóżcie słuchawki.

Poza domem, przy wyłączonym komputerze, działa **lustro tylko do odczytu** (plan, raporty, podgląd 3D, sieć): `python panel/serwer.py --eksport <folder>` zapisuje stronę statyczną, którą można wystawić np. na GitHub Pages (workflow `.github/workflows/panel-lustro.yml`, uruchamiany ręcznie po włączeniu Pages w ustawieniach repozytorium).

## Codzienna praca we dwóch
1. **Pulpit → Pobierz** (albo `git pull`) — ściąga raporty, komentarze i migawki drugiej osoby.
2. Pracujesz z Claude'em; po wdrożeniu Claude publikuje migawkę i raport (skill `.claude/skills/panel/`).
3. Oglądasz raport (Pulpit → Czeka na Ciebie albo zakładka Pytania), klikasz **Akceptuję** albo **Do poprawy**, komentujesz elementy w podglądzie 3D. W **Pytaniach** odpowiadasz na pytania, odhaczasz zadania (Plan), a Karol albo Paweł zatwierdza decyzje (przy komputerze z panelem albo z kluczem zatwierdzania).
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
| Sesja: „Rozmowa zacznie działać po restarcie panelu” | panel działa w starej wersji — zamknij okno serwera panelu i uruchom `panel\start.bat` jeszcze raz |
| Sesja: „Mikrofon działa tylko przez bezpieczne połączenie” | wejdź przez link tunelu (https) albo na komputerze z panelem przez `127.0.0.1`; adres `http://192.168…` z sieci domowej nie daje mikrofonu |
| Sesja: nie słychać drugiej osoby | sprawdź, czy przy jej imieniu jest „głos połączony”; jeśli „głos się nie łączy” — rozmawiajcie przez Discord (zapis działa dalej) |
| Telegram: bot nie odpowiada | panel musi działać (w nowej wersji); sprawdź `telegram.json` (token, numery) i `GET /api/telegram/stan` — „Inny program odbiera wiadomości tego bota” znaczy, że ten sam token ma drugi komputer albo program |
| Telegram: „Nie znam Cię” | dopisz numer tej osoby w `osoby` w `telegram.json` (bot podaje go po `/start`) |
| Sesja: brak tekstu w transkrypcji | agent musi słuchać (czerwony znacznik), mikrofon nie może być wyciszony, a na komputerze z panelem musi być `faster-whisper` |

## Gdzie są dane
| Dane | Miejsce |
|---|---|
| Wspólne (raporty, komentarze, migawki) | `panel/dane/` w repozytorium |
| Odpowiedzi, zadania, statusy decyzji z panelu | w sejfie: `B&C/Produkcja/*.md` (te same pliki co w Obsidianie) |
| Tylko ten komputer (kod dostępu, klucz lokalny, klucz zatwierdzania, log, rozmowy z agentem, nagrania, zapisy rozmów z zakładki Sesja, ustawienia lokalne, ustawienia i stan bota Telegram: `telegram.json`, `telegram_stan.json`) | `%LOCALAPPDATA%\BlockyCrycket\panel\` (zapisy rozmów: podfolder `sesje\`) |
| Tematy na sesje główne | w sejfie: `B&C/Produkcja/Sesje główne.md` |

Usunięcie folderu z danymi lokalnymi przywraca panel do stanu początkowego; danych wspólnych to nie rusza.

## Testy (dla rozwijających panel)
```
cd panel
python -B -m unittest discover -s testy -t .
```
(`-B` = bez plików `__pycache__` w folderze projektu.) Testy w prawdziwej przeglądarce (Pytania i Sesja, potrzebują Edge albo Chrome i Node 22+) uruchamia zmienna `BC_TEST_PRZEGLADARKA=1`.
