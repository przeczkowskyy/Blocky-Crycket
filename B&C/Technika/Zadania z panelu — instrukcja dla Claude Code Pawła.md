---
status: propozycja
tags: [technika, panel, agent, wdrozenie]
---
# Zadania z panelu — instrukcja dla Claude Code Pawła

> [!info] W skrócie
> Karol albo Paweł przypisuje zadanie do agenta Pawła (w panelu albo słownie na sesji — pole `· agent: Paweł` w [[Zadania]]). Takie zadanie ma się wykonać **samo, na koncie Claude Pawła i na jego komputerze**. Nasłuchuje i uruchamia **panel Pawła**, nie otwarte okno Claude Code: panel co półtorej minuty pobiera zmiany z GitHuba, a co dwie minuty sprawdza, czy jest nowe zadanie dla Pawła, i sam uruchamia na nie Claude Code (`claude -p`, tryb Praca). Ta notatka mówi, co raz ustawić i jak ma się zachowywać Claude Code Pawła. Przygotował Claude na prośbę Karola 16.11.2026; zasada to propozycja D-072 w [[Rejestr decyzji]].

## Jak zadanie dochodzi do Pawła
1. Karol przypisuje zadanie do „Paweł” w swoim panelu (albo agent dopisuje to po sesji).
2. Panel Karola sam wysyła zmianę na GitHuba — po ok. minucie.
3. Panel Pawła sam ją pobiera — do półtorej minuty.
4. Panel Pawła sam uruchamia agenta na to zadanie — do dwóch minut, po jednym zadaniu naraz. Na Pulpicie obu osób widać „w pracy” (wymiana prac jest włączona).
5. Agent kończy: odhacza zadanie, wpis w [[Dziennik zmian]], raport w panelu. Jeden przebieg trwa najwyżej 30 minut.

Razem od przypisania do startu: zwykle ok. 5 minut. Warunek: komputer Pawła włączony, a panel Pawła uruchomiony.

## Prompt do wklejenia w Claude Code Pawła
Otwórz Claude Code w folderze repozytorium i wklej:

> Przeczytaj `B&C/Technika/Zadania z panelu — instrukcja dla Claude Code Pawła.md` i przeprowadź mnie przez część „Co ustawić raz” krok po kroku. Przy krokach 5 i 6 zapytaj mnie o zgodę, zanim cokolwiek zmienisz, bo wydają moje tokeny i zmieniają start mojego komputera. Na końcu dopisz w Dzienniku zmian, co ustawiliśmy.

## Co ustawić raz
1. **Kod:** `git pull` na gałęzi `main` (zatrzymaj się przy konflikcie i rozwiążcie go razem).
2. **Czyj to komputer:** `git config bc.osoba "Paweł"` w repozytorium (tylko ten klon, nie trafia do repozytorium). Sprawdzenie: `python panel/narzedzia/praca.py kolizje` ma wypisać `Ja: Paweł`.
3. **Claude Code na koncie Pawła:** `python panel/serwer.py --sprawdz` ma znaleźć Claude Code, a `claude` w terminalu ma być zalogowany na konto Pawła. Panel uruchamia ten sam program, więc zadania pójdą na tę subskrypcję.
4. **Panel:** uruchom `panel\start.bat`, w Ustawieniach wpisz imię „Paweł”. Pliku `telegram.json` z komputera Karola **nie kopiuj** — bot działa tylko na jednym komputerze.
5. **Samo uruchamianie (za zgodą Pawła):** w panelu Ustawienia → Telefon → „Zadania mojego agenta” → **Włącz**. Bez tego zadania czekają na przycisk „Uruchom” przy zadaniu. Ustawienie zmienia się tylko przy własnym komputerze i nie przychodzi z repozytorium.
6. **Start razem z Windowsem (za zgodą Pawła):** skrót do `panel\start.bat` z argumentem `--bez-przegladarki` w folderze Autostart (`shell:startup`), okno zminimalizowane. Wtedy panel nasłuchuje od włączenia komputera; zamknięcie jego okna zatrzymuje nasłuch. Przykład w PowerShell (ścieżkę repozytorium podstaw własną):
   ```
   $repo = "C:\ścieżka\do\repozytorium"
   $s = (New-Object -ComObject WScript.Shell).CreateShortcut("$([Environment]::GetFolderPath('Startup'))\Panel BC.lnk")
   $s.TargetPath = "$repo\panel\start.bat"; $s.Arguments = "--bez-przegladarki"
   $s.WorkingDirectory = $repo; $s.WindowStyle = 7; $s.Save()
   ```
7. **Próba:** poproś Karola o małe zadanie próbne z „agent: Paweł” (np. „Próba: przeczytaj Zadania i odpowiedz jednym zdaniem”). Po ok. 5 minutach na Pulpicie obu osób ma stać „w pracy”, a potem odhaczone zadanie.

## Jak ma się zachowywać Claude Code Pawła
- **W zwykłej rozmowie z Pawłem**, na początku sesji: sprawdź otwarte zadania z `· agent: Paweł` w [[Zadania]] i powiedz o nich jednym zdaniem. Pytaj, czy je robić — chyba że panel już je robi (praca `zadanie-…` w `python panel/narzedzia/praca.py lista`).
- **Zadań z `· agent: Karol` nie rób** — idą na koncie Karola, na jego komputerze. Zadanie bez tego pola robisz tylko na wyraźną prośbę Pawła.
- **Przy pracy nad zadaniem** obowiązuje `CLAUDE.md` i sejf: zmiany w projekcie gry tylko jako propozycje, praca zgłoszona przez `praca.py`, na końcu odhaczenie, [[Dziennik zmian]] i raport w panelu. Niejasne albo wymagające zgody (wgranie do Roblox, publikacja, przebudowa czegoś, nad czym pracuje Karol) — krótkie pytanie w [[Pytania otwarte]] zamiast zgadywania.
- **Wysyłanie na GitHuba:** dopóki Paweł nie potwierdzi D-070, `CLAUDE.md` każe pytać go przed pushem. Agent uruchomiony przez panel nie ma kogo zapytać, więc zostawia zmiany niewysłane i pisze to w odpowiedzi — Karol ich wtedy nie zobaczy. Żeby wyniki same wracały do Karola, Paweł potwierdza D-070 w panelu (Zgoda).
- **Koszt:** każde zadanie to tokeny Pawła. Panel robi po jednym zadaniu naraz i nie ponawia sam zadania, które raz już uruchomił. Wyłączyć: ten sam przełącznik w Ustawieniach. Stan limitu: `/usage` w Claude Code.

## Do ustalenia
- Zgoda na D-072 (Karol albo Paweł w panelu) i potwierdzenie D-070 przez Pawła.
- Czy Paweł chce samo uruchamianie (krok 5) i start z Windowsem (krok 6), czy woli przycisk „Uruchom”.

## Powiązane
- [[Panel zespołu]] · [[Zadania]] · [[Rejestr decyzji]] · [[Start z Blenderem — prompt dla Pawła]] · [[00 Start]]
