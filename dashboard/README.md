# BLOCKY & CRYCKET — AI Development Studio

Lokalne centrum dowodzenia produkcją gry Roblox **BLOCKY & CRYCKET**: 10 agentów AI, Project Brain (wspólna pamięć projektu), zatwierdzenia z diffem, workflowy, IDE z Monaco i integracja z Rojo.

## Uruchomienie

```bash
cd dashboard
npm install          # tylko za pierwszym razem
copy .env.example .env   # wpisz ANTHROPIC_API_KEY
npm run dev
```

Otwórz **http://127.0.0.1:5173**. Bez klucza API wszystko działa poza wykonaniami agentów (status NOT CONFIGURED).

W drugim terminalu, w folderze gry, powinien działać `rojo serve` — zatwierdzone zmiany plików trafiają wtedy na żywo do Studio.

## Jak to działa

| Element | Co robi naprawdę |
|---|---|
| Agenci | Wywołania Claude API (`claude-opus-5-5`, ustrukturyzowane wyjście JSON). Zwracają: odpowiedź, zmiany plików, nowe zadania, propozycje decyzji, pytania, błędy, aktualizację wiedzy. |
| Project Brain | SQLite FTS5 (BM25) nad `docs/`, `src/`, `default.project.json`, skillami i dokumentami KB. Każde wykonanie zapisuje snapshot kontekstu (Context Inspector). |
| Zatwierdzenia | Zmiany plików od agentów → diff → zatwierdź → zapis na dysk (z kopią w historii wersji) → Rojo → Studio. |
| Tryby autonomii | ASSISTANT: wszystko przez zatwierdzenia. SEMI: agenci mogą tworzyć nowe pliki. AUTONOMOUS: zmiany niechronionych plików stosowane automatycznie. Pliki chronione zawsze wymagają zatwierdzenia. |
| Emergency Stop | Przerywa trwające wywołania API (AbortController), zatrzymuje workflowy, blokuje nowe uruchomienia. |
| Testy | `rojo build`, `rojo sourcemap`, zdrowie Project Brain, `selene` (jeśli zainstalowany) + testy manualne. |

## Bezpieczeństwo

- Serwer nasłuchuje tylko na `127.0.0.1`; klucz API czyta wyłącznie serwer z `dashboard/.env`.
- Zapis możliwy tylko w `src/`, `docs/`, `assets/` (+ chroniony `default.project.json`). Pliki `.rbxl` nigdy nie są modyfikowane.
- Dane studia: `dashboard/data/studio.db` (eksport/import w Settings).

## Uwaga o ścieżce z `&`

Folder projektu zawiera `&`, co psuje skróty `.cmd` w `node_modules/.bin` na Windows. Dlatego skrypty npm wywołują `node` bezpośrednio, a serwer działa na natywnym wsparciu TypeScript w Node 24.
