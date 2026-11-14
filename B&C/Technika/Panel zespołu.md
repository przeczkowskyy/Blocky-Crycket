---
status: propozycja
tags: [technika, panel, workflow, narzędzia]
---
# Panel zespołu

> [!info] W skrócie
> Lokalna strona (`panel/`, port 8787) dla dwóch osób: **okno na ten sejf**, raporty z wdrożeń z akceptacją, podgląd 3D tego, co stoi w Roblox Studio, agent Claude Code na subskrypcji, głosówki, sieć notatek i analityka gry. Powstał na prośbę Karola 12.11.2026. **Nie zastępuje sejfu** (decyzja D-008): decyzje, zadania i roadmapę czyta z notatek, a własne dane to tylko raporty, komentarze i migawki. Czeka na zgodę (Karol albo Paweł, decyzja D-030) — [[Pytania otwarte]] #11, propozycja D-012 w [[Rejestr decyzji]].

## Po co, skoro jest sejf
| Potrzeba | Sejf w Obsidianie | Panel |
|---|---|---|
| Decyzje, zadania, roadmapa, dziennik | źródło prawdy | tylko wyświetla, też na telefonie |
| „Co zostało wdrożone i czy to akceptuję?” | wpis w dzienniku | karta raportu ze zrzutami i przyciskami Akceptuję / Do poprawy |
| Zobaczyć mapę bez uruchamiania Studio | — | podgląd 3D z migawki części + zrzuty ze Studio |
| Komentarz do konkretnego budynku | — | klik w element modelu → wątek komentarzy, także głosowy |
| Polecenie dla Claude'a bez otwierania edytora | — | zakładka Agent (ten sam Claude Code, to samo konto) |
| Graf notatek bez Obsidiana | widok grafu | zakładka Sieć |
| Kto teraz pracuje | — | osoby w Team Create, na panelu, ostatnie commity |
| Rejestr grafik i ich etap w pipeline | plik `assets/manifest.json` | zakładka Assety: miniatury, etapy, numery Roblox, komentarze (tylko do odczytu) |
| Liczby z opublikowanej gry | — | Analityka → Telemetria gry (po włączeniu, zob. [[Telemetria gry]]) |
| Długa rozmowa głosowa z zapisem ustaleń | [[Sesje główne]] (tematy) | zakładka Sesja: rozmowa jak na Discordzie, agent słucha, spisuje i robi notatki |

## Uruchomienie
```
python panel/serwer.py              # http://127.0.0.1:8787
python panel/serwer.py --lan        # także telefon w tej samej sieci Wi-Fi (z kodem dostępu)
python panel/serwer.py --sprawdz    # kontrola środowiska
```
Bez instalowania zależności (sam Python 3.9+). Pełna instrukcja: `panel/INSTALACJA.md`, architektura i API: `panel/README.md`.

## Jak działa wspólna praca
- **Wspólne dane idą przez git**: raport, komentarz i migawka to osobne pliki w `panel/dane/`, więc dwie osoby mogą dopisywać naraz bez konfliktów. Przyciski Pobierz i Wyślij na Pulpicie robią `git pull` i commit samych danych panelu.
- **Agent** to `claude -p` uruchamiany w folderze projektu: czyta `CLAUDE.md`, ten sejf i skille, działa na subskrypcji osoby, na której komputerze stoi panel. Tryby: Plan (tylko czyta), Praca (edytuje i używa dozwolonych narzędzi), Auto.
- **Raport od Claude'a**: po wdrożeniu czegokolwiek Claude robi migawkę (`python panel/narzedzia/migawka.py`) i publikuje raport (`python panel/narzedzia/raport.py dodaj …`) z odwołaniem do elementów; odpowiedź człowieka czyta poleceniem `raport.py odpowiedzi`. Opis dla agentów: skill `.claude/skills/panel/`.
- **Podgląd 3D** rysuje części Roblox (bloki, kliny, walce, kule) w przeglądarce z pliku `czesci.json`; siatki z importu pokazuje jako ramki, a prawdziwy wygląd dają zrzuty ze Studio.

## Bezpieczeństwo i prywatność
- Domyślnie panel słucha tylko na tym komputerze. Wejście z telefonu wymaga kodu; agent z telefonu jest domyślnie wyłączony (włącza go osoba przy komputerze: Ustawienia → Telefon).
- Uprawnienia „osoby przy komputerze” (agent, git, nowa migawka) daje **klucz lokalny** zapamiętany w przeglądarce po uruchomieniu `panel\start.bat` — samo połączenie z tego samego komputera nie wystarcza. Wspólna konfiguracja z repozytorium nie może zmienić ustawień bezpieczeństwa.
- Kod przeszedł przegląd bezpieczeństwa 12.11.2026 (14 potwierdzonych uwag, wszystkie poprawione; lista w opisie commita).
- Rozmowy z agentem i nagrania głosowe zostają lokalnie. Do repozytorium trafia tylko tekst raportów i komentarzy.
- **Repozytorium jest publiczne** — wszystko w `panel/dane/` jest widoczne dla każdego. Zob. [[Workflow i Git]].

## Praca na sejfie z panelu (D-028)
Zakładka Plan potrafi zapisywać do sejfu: odpowiedź pod pytaniem otwartym, odhaczenie i dodanie zadania oraz zatwierdzenie albo odrzucenie decyzji. Każda zmiana to mały, czytelny wiersz w tym samym pliku Markdown co zawsze i ślad w [[Dziennik zmian]] (sekcja „Panel (ludzie)”); panel sprawdza, czy plik nie zmienił się w międzyczasie w Obsidianie. Odpowiedzi gości z samym kodem dostępu (bez klucza lokalnego i bez klucza zatwierdzania) są oznaczane „gość panelu” — samo imię nie daje uprawnień. Zapis jest włączony (D-028; odpowiedź Karola na [[Pytania otwarte]] #23); wyłączenie: `"zapis_sejfu": false` w konfiguracji. Szczegóły i API: `panel/README.md`.

### Kto zatwierdza decyzje w panelu (D-030)
Od 13.11.2026 Karol i Paweł mają równe prawa: wystarcza decyzja jednego z nich, a każda zostaje w logach z imieniem i datą. W panelu status decyzji zmienia:
- osoba **przy komputerze, na którym działa panel** (klucz lokalny) — bez dodatkowego klucza;
- przeglądarka z **kluczem zatwierdzania** (dawniej „klucz Game Directora”) — także z telefonu i przez tunel. Link z kluczem wypisuje `python panel/serwer.py --klucz-zatwierdzania` (dawna nazwa `--klucz-gd` działa dalej, link zapisany wcześniej w przeglądarce też).

Gość z samym kodem dostępu decyzji nie zmienia. Przed zatwierdzaniem trzeba wpisać imię w Ustawieniach — bez imienia panel decyzji nie zapisze, bo musi ją podpisać. Dotyczy to także komputera z panelem: imię, którym podpisuje się tam Git, decyzji nie podpisuje.

Jak panel podpisuje:
- w [[Rejestr decyzji]]: `zdecydował: Paweł 2026-11-13` (zatwierdzona albo odrzucona), `oznaczył: Karol 2026-11-13` („do decyzji”), wiersz `Uzasadnienie — Paweł, 2026-11-13: …`;
- w [[Dziennik zmian]]: `- Paweł (klucz zatwierdzania): decyzja D-019 zatwierdzona` (z kluczem zatwierdzania) albo `- Karol: decyzja D-019 zatwierdzona` (przy komputerze z panelem);
- w odpowiedziach w [[Pytania otwarte]]: `- Paweł (klucz zatwierdzania, 2026-11-13): …`, `- Karol (2026-11-13): …` albo `- Paweł (gość panelu, 2026-11-13): …`. Odpowiedź „gościa panelu” nie jest zgodą, nawet podpisana imieniem Karola albo Pawła.

Wpisy z 13.11.2026 sprzed tej zmiany mają jeszcze znacznik „Game Director” (np. `zdecydował: Game Director (Paweł) 2026-11-13` albo `- Paweł (Game Director): …`) — znaczy on dokładnie to samo co „klucz zatwierdzania”. Zapis podpisany imieniem „Game Director”, „klucz zatwierdzania” albo „gość panelu” panel odrzuca, bo takie imię udawałoby znacznik serwera.

## Sesja — długa rozmowa głosowa z agentem
Zakładka **Sesja** (dodana 13.11.2026 na prośbę Karola, czeka na zgodę jak cały panel) służy do „sesji głównych”, czyli długich rozmów Karola i Pawła. Obaj wchodzą na ten sam panel (gospodarz przy komputerze, druga osoba przez link tunelu), klikają **Dołącz** i rozmawiają w przeglądarce — głos idzie wprost między nimi.
- **Agenda**: tematy do omówienia czyta i zapisuje notatka [[Sesje główne]]. Temat można dopisać w zakładce, a agent na przycisk „Zaproponuj tematy” przegląda [[Pytania otwarte]], [[Rejestr decyzji]] i [[Dziennik zmian]] i dopisuje propozycje (z dopiskiem „propozycja agenta”). Gdy ktoś odkłada decyzję „na sesję długą”, temat ląduje właśnie tam.
- **Agent słucha**: włącza Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania). Wszyscy w pokoju widzą wtedy czerwony znacznik nagrywania. Każdy nagrywa swój mikrofon, panel spisuje to lokalnie (Whisper, jak głosówki) i pokazuje transkrypcję na żywo; dźwięk kasuje zaraz po spisaniu. Co kilka minut agent aktualizuje robocze notatki: o czym mowa, ustalenia, zadania, otwarte pytania i tematy z agendy, które jeszcze nie padły.
- **Zakończ sesję i spisz ustalenia**: agent zapisuje w sejfie notatkę z ustaleniami (status `propozycja`, wzór: [[Rozmowa 2026-11-12 — zapis ustaleń]]), dopisuje ustalenia jako propozycje do [[Rejestr decyzji]], pytania i zadania, oznacza omówione tematy i wysyła raport z listą do zatwierdzenia. **Agent niczego nie zatwierdza** — robi to człowiek w panelu. Panel najpierw czeka na ostatnie wypowiedzi (także te z ostatnich sekund przed kliknięciem) i na ich spisanie; jeśli spisywanie nie nadąża, agent dostaje informację, że zapis jest niepełny, i zaznacza to w ustaleniach.
- **Agent nie słucha poleceń z rozmowy**: to, co ktoś powie do mikrofonu albo wpisze w agendzie, jest dla agenta treścią rozmowy, nie poleceniem. Przy notatkach agent może tylko czytać, a przy spisywaniu ustaleń ma wąski zestaw narzędzi (bez internetu, bez Roblox Studio).
- **Prywatność**: pełny zapis bieżącej rozmowy i notatki zostają tylko na komputerze z panelem (nie w repozytorium); widzą je osoby w pokoju. Dawne sesje widzi i pobiera tylko osoba przy komputerze. Gdy głos nie połączy się bezpośrednio, można rozmawiać przez Discord — nagrywanie i transkrypcja działają dalej.
- Kroki dla dwóch osób: `panel/INSTALACJA.md` (część „Sesja”), szczegóły techniczne: `panel/README.md`.

## Wejście z telefonu spoza domu (tunel)
Sprawdzone naprawdę 13.11.2026: przenośny `cloudflared` (bez instalatora i uprawnień administratora) wystawia panel pod losowym adresem https, a wejście wymaga kodu dostępu. Gość z tunelu nie dostaje uprawnień osoby przy komputerze — nie uruchomi agenta, gita ani nowej migawki — nawet jeśli zna klucz lokalny. Przed udostępnieniem adresu drugiej osobie trzeba wyjąć z konfiguracji lokalnej prywatne sejfy podpięte do panelu. Kroki: `panel/INSTALACJA.md`.

## Stosunek do starego `dashboard/`
Stary dashboard (porzucony decyzją D-008) miał własną bazę z kopią decyzji i zadań oraz agentów na płatnym kluczu API. Panel robi odwrotnie: nie ma własnej bazy wiedzy, a agent działa na subskrypcji. Kodu `dashboard/` nie używa i nie zmienia.

## Powiązane
[[Jak prowadzimy sejf]] · [[Workflow i Git]] · [[Narzędzia]] · [[Klocki — Blender i Roblox]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Sesje główne]]
