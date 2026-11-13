---
status: propozycja
tags: [technika, panel, workflow, narzędzia]
---
# Panel zespołu

> [!info] W skrócie
> Lokalna strona (`panel/`, port 8787) dla dwóch osób: **okno na ten sejf**, raporty z wdrożeń z akceptacją, podgląd 3D tego, co stoi w Roblox Studio, agent Claude Code na subskrypcji, głosówki, sieć notatek i analityka gry. Powstał na prośbę Karola 12.11.2026. **Nie zastępuje sejfu** (decyzja D-008): decyzje, zadania i roadmapę czyta z notatek, a własne dane to tylko raporty, komentarze i migawki. Czeka na zgodę Game Directora — [[Pytania otwarte]] #11, propozycja D-012 w [[Rejestr decyzji]].

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

## Praca na sejfie z panelu (propozycja D-028, na razie wyłączona)
Zakładka Plan potrafi zapisywać do sejfu: odpowiedź pod pytaniem otwartym, odhaczenie i dodanie zadania, a z osobistym kluczem Game Directora — zatwierdzenie albo odrzucenie decyzji. Każda zmiana to mały, czytelny wiersz w tym samym pliku Markdown co zawsze i ślad w [[Dziennik zmian]] (sekcja „Panel (ludzie)”); panel sprawdza, czy plik nie zmienił się w międzyczasie w Obsidianie. Odpowiedzi osób bez klucza lokalnego są oznaczane „gość panelu”, a zgodę Game Directora poznaje się po znaczniku stawianym przez serwer — samo imię nie daje uprawnień. Włączenie: `"zapis_sejfu": true` w konfiguracji lokalnej; link z kluczem: `python panel/serwer.py --klucz-gd`. Szczegóły i API: `panel/README.md`. Do ustalenia: [[Pytania otwarte]] #23.

## Wejście z telefonu spoza domu (tunel)
Sprawdzone naprawdę 13.11.2026: przenośny `cloudflared` (bez instalatora i uprawnień administratora) wystawia panel pod losowym adresem https, a wejście wymaga kodu dostępu. Gość z tunelu nie dostaje uprawnień osoby przy komputerze — nie uruchomi agenta, gita ani nowej migawki — nawet jeśli zna klucz lokalny. Przed udostępnieniem adresu drugiej osobie trzeba wyjąć z konfiguracji lokalnej prywatne sejfy podpięte do panelu. Kroki: `panel/INSTALACJA.md`.

## Stosunek do starego `dashboard/`
Stary dashboard (porzucony decyzją D-008) miał własną bazę z kopią decyzji i zadań oraz agentów na płatnym kluczu API. Panel robi odwrotnie: nie ma własnej bazy wiedzy, a agent działa na subskrypcji. Kodu `dashboard/` nie używa i nie zmienia.

## Powiązane
[[Jak prowadzimy sejf]] · [[Workflow i Git]] · [[Narzędzia]] · [[Klocki — Blender i Roblox]] · [[Rejestr decyzji]] · [[Pytania otwarte]]
