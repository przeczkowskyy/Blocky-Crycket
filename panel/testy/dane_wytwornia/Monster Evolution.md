---
status: propozycja
typ: pomysł-gry
gra: Monster Evolution
etap: ocena
zdanie: "Start as a tiny slime, eat smaller monsters, evolve into a giant beast."
ocena_agenta: 26
werdykt_agenta: popraw
ocena_karol:
ocena_pawel:
d1:
d7:
sesja_min:
ccu:
miejsce:
tags: [wytwórnia, pomysł]
---
# Monster Evolution

Pomysł agenta z badania 20.11.2026 (do oceny na sesji, pytanie 75). Wszystkie liczby karty to szacunek agenta, nie dane od graczy.

## W jednym zdaniu
Start as a tiny slime, eat smaller monsters, evolve into a giant beast.

## Pierwsze 10 sekund
jesteś małym slime'em; wpadasz na drobne kulki — zjadasz, rośniesz, „+1”.

## Hak ciekawości
w co ewoluujesz? Rozgałęzienia (ogień, las, bagno) pokazane jako sylwetki; mutacje (kolor, rozmiar, skrzydła) z jawnymi szansami i licznikiem gwarancji; pierwszy na serwerze, kto dojdzie do nowej formy — ogłoszenie.

## Głębia
wybór gałęzi = inne umiejętności (szybkość, pancerz, atak z daleka); ryzyko: polować na graczy podobnej wielkości czy bezpiecznie na kulki; sojusze.

## Inni gracze i pokazanie się
jesz albo jesteś zjedzony (tylko w zasięgu ±2 stadiów — jak w Ant Evolution, żeby duzi nie gnębili małych). **Zwrot:** gdy ktoś osiągnie formę szczytową, serwer dostaje wydarzenie „Apex” — ten gracz staje się bossem, na którego mogą się rzucić wszyscy mali naraz. To odpowiada na „brakuje bossów”.

Pokazanie się: rozmiar i forma widoczne z daleka; korona Apexa; Księga form.

## Moment do nagrania
mały slime ucieka smokowi; dziesięciu małych powala Apexa.

## Powód powrotu
odrodzenie do nowej gałęzi, kolekcja form, nowa forma co tydzień.

## Monetyzacja
skórki form, 2× wzrost, tarcza po odrodzeniu (zużywalna), prywatny serwer. Mutacje losowane tylko za walutę z gry.

## Z naszych zasobów
ok. 30 potworów jako stadia (3 gałęzie po 8–10), silnik walki (jedna umiejętność na formę), efekty, mapy z klocków, Księga z BONK.

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie | 3 | | |
| Pierwsze 10 sekund | 3 | | |
| Hak ciekawości | 3 | | |
| Głębia | 2 | | |
| Inni gracze | 3 | | |
| Pokazanie się | 3 | | |
| Moment do nagrania | 3 | | |
| Powód powrotu | 2 | | |
| Trend | 3 | | |
| Koszt dla nas | 1 | | |

## Krytyka agenta
Pre-mortem — dlaczego może przegrać:
1. Frustracja: dzieci zjadane przez większych wychodzą po pierwszej śmierci (Ant Evolution łagodzi to limitem stadiów i utratą tylko części postępu — trzeba to skopiować).
  2. Koszt: 30 form × animacje ruchu, hitboxy, umiejętności — to 2–3 tygodnie, nie tydzień; nasze modele mogą nie mieć animacji chodu.
  3. „Ant Evolution z potworami” — jeśli miniatura nie pokaże różnicy (Apex-boss, zjadanie potworów), nikt nie kliknie.

## Najtańszy test
6 form jednej gałęzi (istniejące modele, skalowanie + jedna umiejętność), kulki do zjadania, zjadanie graczy, wydarzenie Apex. 4–6 testerów. Mierzymy: czy po zjedzeniu wracają do gry, czas do pierwszej ewolucji, czy pytają „w co ewoluuję dalej”.

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[Karta oceny pomysłu]] · [[Radar trendów]] · [[Rozbiór hitów — listopad 2026]]
