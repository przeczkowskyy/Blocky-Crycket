---
status: propozycja
tags: [produkcja, sesja, zadania]
źródło: "sesja główna Karola i Pawła 2026-11-25 (21:53–22:20); zapis rozmowy lokalnie u gospodarza"
---
# Po sesji 2026-11-25 — podział prac

> [!info] Co to jest
> Lista „kto co robi” po sesji głównej z 25.11.2026, spisana przez agenta Karola na prośbę Karola z końca sesji. To **robocze ustalenia z rozmowy, nie kanon**: decyzje trafiają do [[Rejestr decyzji]] jako propozycje i czekają na potwierdzenie obu osób w panelu. Zadania są też w [[Zadania]].

## Paweł — do zrobienia
1. **Ikony broni (obrazy referencyjne)** — wrzucić na GitHuba; agent Karola zrobi z nich modele 3D. Dziś w repo jest jedna broń (`ItemSplintersword`).
2. **Okno Kowala: zakładki** zamiast przebudowy całego okna — Ulepszanie · Rozbiórka · Sklep składników. Dolna siatka to przedmioty gracza do rozbiórki, górna to składniki. Składniki można też kupić u Kowala za Rybki.
3. **Mistrz gier** — poprawki, o których mówił Paweł.
4. **Questy: tablica ogłoszeń** — wykrzyknik nad tablicą; po podejściu i kliknięciu okno z questami do wyboru.
5. **Modele kotów wszystkich ras** — Paweł kończy sam (ma je u siebie). Otwarte: chwyt broni wspólny dla wszystkich kotów czy osobny dla rasy.
6. **Drzewko umiejętności** — w pierwszej wersji tylko dwie gałęzie: postać i pety. Gałąź Twierdzy zablokowana kłódką albo ukryta; kod zostaje.
7. **Referencje petów** — obrazy petów z jajek, żeby agent Karola poprawił ich modele.
8. **Sklep petów znika** — pety są tylko pod przyciskiem Pet. Kto go wyłącza, ustalimy po sprawdzeniu, czyje to okno.

## Agent Karola — robi tej nocy (25/26.11)
- **Zagroda:** bez smoka, psa i domku; Jagoda stoi przed zagrodą; osiem miejsc na pety.
- **Rybki z zagrody:** pety stojące w zagrodzie dają Rybki na sekundę; pet założony daje perki i w zagrodzie nie stoi; miejsca 2 → 4 → 6 → 8 kupowane u Jagody. Liczby robocze.
- **Training Center:** rozszerzony budynek, sześć stanowisk treningu w środku, poprawki animacji (nic w łapie podczas treningu, sztanga nie przechodzi przez ubranie, książka w łapach).
- **Jajka Bagna i Dżungli** na wzór leśnego jajka Pawła, z animacjami.
- **Nazwa gry:** propozycje z „Cat” do wyboru.

## Pawle, uwaga na pliki
- Agent Karola zmienia tej nocy trzy Twoje pliki, za zgodą z sesji (przeniesienie stanowisk i animacje): `src/shared/TreningAFKDane.luau`, `src/server/TreningAFK.server.luau`, `src/client/TreningAFKClient.client.luau`. Nie zmieniaj ich równolegle. Reszty `src/` agent Karola nie dotyka.
- Przed startem swojego agenta zrób `git pull`. Po pobraniu zrestartuj własny panel: pulpit jest teraz osobno dla każdej gry.

## Ustalenia z sesji (do potwierdzenia w panelu)
- Pierwsza wersja gry bez Twierdzy, bez walk petów i bez Pet Areny; treść dochodzi aktualizacjami. Loch: bez jasnego „tak”.
- Nowa nazwa gry z „Cat”; Blocky znika z tytułu.
- Gracz chodzi kotem w wyglądzie swojej rasy; Mag jest kotem.
- Rzadkość: legendarny przedmiot daje co najmniej półtora raza więcej statystyk niż zwykły; epickie i legendarne mają unikalną zdolność.
- Teraz grywalność, bez nowych biomów.
- „Pierwsze 10 sekund” i „czym gracz zajmuje się najpierw” odłożone do rozmowy o poradniku.

## Uwaga agenta (D-114)
Zakres pierwszej wersji został przycięty i to pomaga ją wydać. W tej samej rozmowie doszła jednak nowa mechanika (Rybki z zagrody), więc robię ją w najprostszej postaci. Wydanie nadal blokuje pytanie 90 w [[Pytania otwarte]] (pakiety Karola działają tylko w Studio) — proponuję wziąć je zaraz po tej nocy.
