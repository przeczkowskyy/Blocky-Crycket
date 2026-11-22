---
status: propozycja
typ: pomysł-gry
gra: BONK: Chain Reaction
etap: ocena
zdanie: "Bonk monsters into each other — every monster reacts differently."
ocena_agenta: 16
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
# BONK Chain Reaction

Pomysł agenta z badania 20.11.2026 (do oceny na sesji, pytanie 75). Wszystkie liczby karty to szacunek agenta, nie dane od graczy.

## W jednym zdaniu
Bonk monsters into each other — every monster reacts differently.

## Pierwsze 10 sekund
uderzasz slime'a, odbija się jak piłka w muchomorka, muchomorek wybucha zarodnikami i przewraca trzech sąsiadów — „COMBO ×4!”.

## Hak ciekawości
każdy gatunek reaguje inaczej (slime odbija się i dzieli, muchomorek wybucha chmurą, kamienny golem toczy się jak kula do kręgli, balonik unosi się i pęka deszczem monet, jeż przykleja się do tego, w co trafi). Co 2 min pojawia się **„?” — potwór o nieznanej reakcji**. Księga reakcji z odkrytymi połączeniami („slime + ogień = ?”). Prawdziwa fizyka zamiast zaplanowanego łuku — każdy lot jest inny.

## Głębia
koniec „linii” potworów: stada są mieszane, a wartość potwora zależy od sąsiadów (muchomorek sam jest nic niewart, w tłumie mnoży kombo) — **to odpowiada wprost na „po co slime, skoro muchomorek daje więcej”**. Pałki zmieniają **efekt**, nie mnożnik (kij = daleko, młot = fala w dół, kij golfowy = wysoki łuk, packa = szerokie pchnięcie). Pety zmieniają reakcje (ptak łapie lecącego potwora i odbija go drugi raz) — **pet robi coś, co widać**, więc jajko ma wartość.

## Inni gracze i pokazanie się
lecące potwory przewracają innych graczy (ragdoll); kombo przechodzą między graczami („kombo serwera”); Strażnik to boss, którego trzeba zepchnąć z wyspy łańcuchem uderzeń wielu graczy.

Pokazanie się: największe kombo serwera na tablicy i nad głową, korona.

## Moment do nagrania
łańcuch 20 potworów; Strażnik spada z wyspy.

## Powód powrotu
dzienny „?”-potwór, Księga reakcji, nowy gatunek co tydzień.

## Monetyzacja
kosmetyczne ślady i dźwięki pałek (przepustki), 2× monety, produkt „deszcz potworów dla całego serwera” (zakup, z którego korzystają wszyscy — dobrze widziany), prywatny serwer.

## Z naszych zasobów
cały pakiet `swiat/bonk/` (3 krainy, 12 potworów, 8 pałek, 15 petów, Strażnicy, efekty komiksowe). Nowe: lot fizyką serwera i skrypty reakcji.

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie | 2 | | |
| Pierwsze 10 sekund | 3 | | |
| Hak ciekawości | 2 | | |
| Głębia | 1 | | |
| Inni gracze | 1 | | |
| Pokazanie się | 1 | | |
| Moment do nagrania | 2 | | |
| Powód powrotu | 1 | | |
| Trend | 1 | | |
| Koszt dla nas | 2 | | |

## Krytyka agenta
**Ocena odświeżona 2026-11-22 (agent): 16/30, werdykt: popraw.** Fizyka nadal rośnie, ale w drugiej generacji: Hyper Realistic Ragdoll miał 22.11 o 18:10 UTC 141 tys. graczy, a czyste piaskownice pierwszej fali (ponad 100 gier) tracą 25–45% tygodniowo. Pomysł nie ma ani majątku z dochodem, ani niczego do stracenia, a bez tego gasną nawet gry z oceną 98%; głębia kombo istnieje tylko na papierze (gracze klikną najbliższego potwora). Wyrasta z gry o uderzaniu, którą właściciel porzucił jako nudną i której falę uznał za minioną — stąd 22 → 16, dolna granica „popraw”, na końcu kolejki. Źródła: [[Fale na Roblox 2026 i gdzie jest otwarcie]] · [[Wschodzące trendy 2026-11-22]] · [[Anatomia pętli, która trzyma (2026-11-22)]] · [[Walidacja wariantu nocne fale i potwory-obrońcy (2026-11-22)]] · [[Lekcje z prototypów]].

Pre-mortem — dlaczego może przegrać:
1. Fizyka wielu potworów na serwerze → przycięcia na telefonie i rozjazd obrazu między graczami.
  2. Gracze nie planują kombo, tylko klikają najbliższego — głębia istnieje tylko na papierze.
  3. Dalej nic nie można stracić → nuda po 15 min, jak dziś.

## Najtańszy test
jedna polana, 5 gatunków z reakcjami, fizyka serwera, 30 potworów naraz. 4 osoby po 15 min (Karol, Paweł + dwoje dzieci ze znajomych). Mierzymy: czy ktoś sam zaczyna „ustawiać” kombo; czy po 10 min chce dalej; klatki na telefonie w MicroProfilerze; 10 zrzutów momentów — czy któryś bawi bez opisu.

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[Karta oceny pomysłu]] · [[Radar trendów]] · [[Rozbiór hitów — listopad 2026]]
