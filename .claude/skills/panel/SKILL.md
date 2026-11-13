---
name: panel
description: Panel zespołu BLOCKY & CRYCKET — publikowanie raportów z wdrożeń, migawek świata z Roblox Studio (podgląd 3D na telefonie) i czytanie odpowiedzi ludzi. Użyj ZAWSZE po zmianie, którą człowiek powinien zobaczyć albo zaakceptować (nowa część mapy, budynek, ekran UI, mechanika, większa zmiana w sejfie), oraz gdy ktoś mówi „panel”, „raport”, „migawka”, „podgląd 3D”, „pokaż na panelu”, „co odpowiedzieli”, „wyślij do akceptacji” — także bez słowa „skill”.
---

# Panel zespołu — jak z niego korzysta Claude

Panel (`panel/`, `http://127.0.0.1:8787`) to okno na sejf `B&C/` dla dwóch osób: Pawła (Game Director) i Karola. Ludzie oglądają w nim raporty, model 3D mapy i komentują konkretne elementy — często z telefonu. **Twoja praca jest dla nich niewidoczna, dopóki nie opublikujesz raportu.**

Narzędzia działają bez uruchomionego serwera (piszą pliki do `panel/dane/`). Uruchamiaj je z głównego folderu repozytorium.

## Po wdrożeniu: migawka → raport
1. **Migawka świata** (gdy zmieniłeś coś w Roblox Studio):
   ```
   python panel/narzedzia/migawka.py --tytul "Karczma: dach i szyld" --opis "Co się zmieniło" --korzen Workspace/DemoLesnaBaza --kto "Claude (Karol)"
   ```
   Wypisuje id migawki. `--korzen` zawęża do jednego kontenera; `--bez-zrzutow` pomija zrzuty ekranu. Zrzuty wychodzą czarne, gdy okno Studio jest zminimalizowane — wtedy użyj `--bez-zrzutow` i napisz o tym w raporcie.
2. **Raport**:
   ```
   python panel/narzedzia/raport.py dodaj --tytul "Karczma: dach i szyld" --opis-plik opis.md --rodzaj wdrozenie \
       --migawka <id migawki> --komponent "studio:Workspace/DemoLesnaBaza/Karczma:Karczma" \
       --komponent "notatka:B&C/Gra/Karczma (Questy).md:Notatka o karczmie" --zrzut obraz.png \
       --pytanie "Czy wysokość dachu pasuje?" --kto "Claude (Karol)"
   ```
   - `--rodzaj`: `wdrozenie` (czeka na Akceptuję / Do poprawy), `pytanie` (czeka na odpowiedź), `informacja` (bez decyzji).
   - `--komponent typ:cel:Etykieta` — do czego odnosi się raport: `studio:<ścieżka grupy>` (człowiek kliknie i zobaczy ten element w podglądzie 3D), `notatka:<ścieżka w repo>`, `plik:<ścieżka>`, `migawka:<id>`. Do 12 sztuk.
   - Opis po polsku, w Markdownie, **dla osoby nietechnicznej na telefonie**: co zrobiłeś, co widać, czego nie ma, co ma ocenić. Jedno konkretne pytanie w `--pytanie`. Długi opis podaj plikiem (`--opis-plik`), nie w wierszu poleceń.
   - Obrazy do 3 MB; obejrzyj każdy przed załączeniem.
3. **Sejf**: raport nie zastępuje zasad z `CLAUDE.md` — zaktualizuj notatki, `Zadania.md` i `Dziennik zmian.md`.

## Przed kontynuacją: przeczytaj odpowiedzi
```
python panel/narzedzia/raport.py odpowiedzi --od 2026-11-12T20:00      # decyzje i komentarze ludzi od tego czasu
python panel/narzedzia/raport.py odpowiedzi --raport <id>
python panel/narzedzia/raport.py lista --czeka
```
„Do poprawy” z komentarzem to zlecenie poprawki. „Akceptuję” dotyczy tego jednego raportu — **nie robi z niczego kanonu**; kanon zatwierdza Game Director w sejfie.

## Zasady
- Jeden plik na wpis: nigdy nie edytuj ani nie usuwaj cudzych plików w `panel/dane/` (raportów, komentarzy, migawek). Własny raport poprawiasz nowym raportem.
- Repozytorium jest **publiczne**: w raportach i komentarzach żadnych sekretów, danych osobowych ani prywatnych rozmów.
- Studio to wspólne miejsce Team Create: buduj we własnym kontenerze, cudzych obiektów nie zmieniaj, nie publikuj gry.
- Nie commituj i nie pushuj bez prośby człowieka. Dane panelu wysyła człowiek przyciskiem „Wyślij” albo prosi o commit.
- Gdy rozmowa toczy się przez zakładkę Agent, odpowiadaj krótko po polsku; szczegóły dawaj w raporcie.

## Gdzie co jest
| Co | Gdzie |
|---|---|
| Architektura, API, formaty danych | `panel/README.md` |
| Instalacja i uruchomienie | `panel/INSTALACJA.md` |
| Opis dla ludzi, zgodność z D-008 | `B&C/Technika/Panel zespołu.md` |
| Mapy z klocków (Blender ↔ Studio ↔ panel) | `B&C/Technika/Klocki — Blender i Roblox.md` |
| Studio z terminala | `python tools/studio_mcp.py tools \| studios \| luau <plik> \| call <narzędzie> --args '{…}'` |
