---
status: propozycja
tags: [ui, questy]
implementacja: w Studio na próbę, 2026-11-25 (polecenie Pawła, czeka na Karola)
---
# Tablica questów (propozycja)

Paweł 25.11.2026: tablica ogłoszeń w miasteczku ma być **tablicą questów** zamiast rankingu serwera. Gracz podchodzi, wciska E i w oknie wybiera questy; wybrane trafiają same do wysuwanej szuflady po prawej stronie [[HUD]].

## Opis
- **Dwa rodzaje:** DAILY — questy dzienne (zerują się o północy UTC) i GOALS — osiągnięcia (jednorazowe).
- **Wiersz questa:** nazwa, postęp (np. „Roll the dice 1/5”), nagroda w Rybkach albo Diamentach, przycisk.
- **TRACK / UNTRACK** przypina quest do szuflady (najwyżej 3 naraz). Postęp liczy się zawsze, także bez przypięcia.
- **CLAIM** wypłaca nagrodę gotowego questa (przez stan gracza Karola); potem wiersz jest wyszarzony jako DONE.
- Na tablicy w świecie zamiast rankingu wisi napis „QUEST BOARD”, a podpowiedź E mówi „Quests”.

## Questy na start (liczby robocze — do kalkulatora balansu)
| Dzienne | Cel | Nagroda |
|---|---|---|
| Forest Patrol — wygraj walki | 5 | 200 Rybek |
| Egg Hunter — wykluj jajka | 3 | 300 Rybek |
| Lucky Roll — rzuć kostką u mistrza gier | 5 | 150 Rybek |
| Fish Market — zarób Rybki | 500 | 3 Diamenty |
| Student — kup ulepszenie w drzewku | 1 | 2 Diamenty |

| Osiągnięcia | Cel | Nagroda |
|---|---|---|
| Rising Star — poziom | 5 | 10 Diamentów |
| Local Hero — poziom | 10 | 25 Diamentów |
| Monster Slayer — wygraj walki | 25 | 500 Rybek |
| Pet Collector — wykluj jajka | 10 | 15 Diamentów |
| Board Master — ukończ planszę mistrza gier | 1 | 10 Diamentów |
| Fish Tycoon — zarób Rybki | 5000 | 20 Diamentów |

## Czego dziś nie ma (ograniczenia próby)
- **Brak zapisu:** postęp, wybór i odebrane nagrody żyją do wyjścia z gry (pamięć serwera). Zapis dojdzie ze stanem gracza Karola.
- **Postęp z obserwacji atrybutów gracza**, bez zmian w plikach Karola: „wygrane walki” to wzrost XP albo poziomu, „zarobione Rybki” to przyrost Rybek z dowolnego źródła, jajka liczy tylko leśne jajo Pawła (inkubatory Karola nie). Pierwsze 10 s po wejściu nie liczy się (wtedy wczytuje się profil).
- **Tablica w świecie:** ranking Karola jest wyłączany tylko u gracza w czasie gry (obiekty Karola w Studio bez zmian); docelowo powinien to przełączyć jego pakiet bazaru — [[Pytania otwarte]] 105.
- **Kanon mówi inaczej:** [[Karczma (Questy)]] i D-034 opisują zadania na czas brane w karczmie. Tablica ich nie zastępuje ani nie zmienia — to osobna propozycja; jak je pogodzić: pytanie 105.
- Okno po angielsku; teksty questów wpisane w skrypcie serwera.

## Stan implementacji
- [x] 2026-11-25: serwer `src/server/Questy.server.luau`, okno `src/gui/OknoQuestow.model.json` (`tools/okno_questow_build_gui.py`) i `src/client/OknoQuestowClient.client.luau`, szuflada `src/client/QuestyClient.client.luau` (koniec przykładowych wpisów). W Play sprawdzone: otwarcie z tablicy, obie karty, TRACK (dwa questy w szufladzie), CLAIM (+3 Diamenty), postęp po rzucie kostką.
- [x] 2026-11-25: grafika z jednej generacji (`assets/raw/OknoQuestow/arkusz_v1.png`, `tools/okno_questow_ui.py`): okno, wiersz, dwie karty kategorii, dwa przyciski, dwie ikony — 11 plików w `assets/processed/OknoQuestow/`.
- [x] 2026-11-25: grafika wgrana do Roblox po „tak” Pawła (11 obrazów, ID w `assets/manifest.json`) i podpięta w oknie — sprawdzone w Play.
- [ ] Arkusz w Figmie: ramka makiety założona na stronie „HUD Buttons” (węzeł 58:130), obrazki wgrane; wiersze 2–5 i zrzut kontrolny czekają — Figma zablokowała dalsze operacje (limit planu Starter).
- [ ] Telefon.

## Powiązane
- [[HUD]] · [[Karczma (Questy)]] · [[Pytania otwarte]] · [[Dziennik zmian]]
