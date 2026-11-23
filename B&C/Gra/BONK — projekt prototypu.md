---
status: propozycja
tags: [gra, bonk, prototyp, rdzeń]
źródło: "D-112 — polecenie Karola z 19.11.2026 na czacie; [[Diagnoza 2026-11-19 — prostota i szansa na hit]] (wariant b)"
---
# BONK — projekt prototypu

> [!info] W skrócie
> Osobna, prosta gra zbudowana z naszych zasobów: **uderzasz potwory, a one odlatują daleko jak szmaciane lalki; za monety kupujesz jajka i lepsze pałki, rośnie twoja Moc, odblokowujesz kolejne krainy.** Jedna czynność, jedna liczba, moment do nagrania, pokazanie się przed innymi. Prototyp powstaje w nocy 19/20.11 w osobnym pakiecie `swiat/bonk/`, w odosobnionym miejscu obecnej gry; B&C zostaje nietknięte. Wszystkie liczby to propozycja do pomiaru.

## Gra w jednym zdaniu
*Bonk monsters into the sky, hatch pets, get stronger, unlock bigger lands.*

## Pętla
1. **BONK:** jeden duży przycisk (telefon: przycisk w prawym dolnym rogu, komputer: klik albo E, pad: przycisk akcji) uderza najbliższego potwora w zasięgu. Cios zadaje obrażenia równe Mocy. Ostatni cios wystrzeliwuje potwora łukiem, z obrotem, komiksowym „ŁUP!” i śladem; im większa nadwyżka Mocy, tym dalej leci. Daleki lot = premia monet i napis „HOME RUN!”.
2. **Nagroda od razu:** monety wylatują z potwora i same lecą do gracza; każdy BONK daje też trochę Mocy (trend „+1”).
3. **Moc** (jedna liczba nad głową) = Moc z uderzeń × mnożnik pałki × mnożnik petów.
4. **Pałki:** 8 broni z `swiat/postacie/bronie.py` jako kolejne stopnie, kupowane za monety, widoczne w dłoni.
5. **Jajka i pety:** inkubator w każdej krainie, stała cena (D-105), jawne szanse (D-015), efektowne wyklucie; do 3 petów idzie za graczem i mnoży Moc; Księga petów z sylwetkami nieodkrytych.
6. **Krainy:** las, Bagno, Dżungla (mapy z naszych pasów). W każdej zagrody coraz cięższych potworów, rzadki potwór i Strażnik.
7. **Strażnik:** wspólny dla serwera — bije go każdy, kto jest w pobliżu; po pokonaniu odlatuje w niebo, nagroda dla wszystkich, którzy trafili, i komunikat dla całego serwera. Brama do następnej krainy po pokonaniu Strażnika.
8. **Pokazanie się:** Moc nad głową, korona dla najsilniejszego na serwerze, tablice: Moc, najdalszy BONK, Księga petów; komunikaty o legendarnym pecie i Strażniku.
9. **Powód powrotu:** kolejne jajka i krainy, Księga petów, dzienny prezent bez kary za opuszczony dzień ([[Psychologia gracza v2]]).

## Start gry
Gracz pojawia się od razu w lesie, własnym awatarem, bez wyboru klasy i menu. Trzy krótkie podpowiedzi; pierwszy BONK w ciągu 30 sekund, pierwsze jajko po 3–5 minutach, Strażnik lasu po ok. 10 minutach (cele do strojenia).

## Czego w BONK nie ma
Klas, ras, statystyk do rozdawania, auto-walki, mini-gier, kowala, Twierdzy, karczmy, drzewek, dodatkowych walut. Bez sprzedaży za Robuxy w prototypie; jajka tylko za monety (D-086).

## Technika
- Pakiet `swiat/bonk/` jest **samowystarczalny**: buduje mapę, potwory, pety, pałki, interfejs, dźwięki i zapis we własnych kontenerach i nie zależy w grze od innych pakietów — da się go zbudować w pustym miejscu przy publikacji.
- Na czas prototypu stoi w odosobnionym miejscu obecnej gry; wejście portalem ze startu i atrybutem do prób. Własny magazyn zapisu.
- Lot potwora liczy serwer, rysuje klient (bez fizyki sieciowej) — tanio na telefonie.
- Powtórne użycie: mapy pasów (`czesci.json`), modele potworów i petów, bronie, efekty komiksowe, arkusz dźwięków i wgrana muzyka.

## Stan budowy
- [x] 2026-11-19 (noc) — **etap 1, rdzeń:** trzy krainy z map pasów, 12 potworów, BONK z lotem po łuku, HOME RUN, rzadki złoty potwór, monety i Moc, bramy Mocą (Bagno 2.4K, Dżungla 55K), wejście bramą przy starcie obecnej gry, własny zapis. Próba w Studio 17/17, śr. 16,7 ms na klatkę. Szczegóły: `swiat/bonk/README.md`.
- [x] 2026-11-20 (noc) — **etap 2:** pałki (8 stopni z naszej zbrojowni, w dłoni), jajka w każdej krainie ze stałą ceną i jawnymi szansami, 15 petów, do 3 za graczem, Księga z sylwetkami; Strażnicy bici wspólnie (brama wymaga Strażnika i Mocy; progi podniesione do 4.5K i 600K); Moc nad głową, korona, tablice, komunikaty; dzienny prezent bez kary za opuszczony dzień; zapis v2. Próba w Studio 27/27, testy 34/34. Tempo z rachunku: pierwsza pałka ok. 2 min, jajko ok. 4 min, brama Bagna ok. 9,5 min, Dżungli ok. 24 min.
- [x] 2026-11-20 (noc) — **etap 3:** zamach ręką z pałką widoczny dla wszystkich, ruch petów i jajek, tupot Strażnika, napisy u góry w jednym stosie, pad, przyciski na telefon i tablet, ikona i trzy miniatury (szkice z Higgsfield, napisy dodane u nas), krótkie demo wideo, lista kroków publikacji w README. Próba w Studio 33/33, testy 37 OK; obecna gra bez nowych błędów (próba dymna 14/14, zapis 10/10).
- [x] 2026-11-20 — **prywatna wersja testowa** (D-113): osobne doświadczenie „BONK!” (universe 10777975015, place 92789057272917), zbudowane `zbuduj.py --publikacja`, prywatne, wszystkie urządzenia; Paweł zaproszony jako tester. Właściciel: konto Karola — grupy nie było w wyborze twórcy (pytanie 31).
- [ ] próba we dwóch na tej wersji (telefon i pad), potem przeniesienie do grupy, ikona i miniatury, kwestionariusz dojrzałości i przełączenie na publiczne.

## Do ustalenia
- Wyniki pierwszego pomiaru na prawdziwych graczach (D1, czas gry) — progi w [[Diagnoza 2026-11-19 — prostota i szansa na hit]].
- Publikacja jako osobna gra w grupie (D-044) — decyzja i czynność ludzi.

## Powiązane
- [[Diagnoza 2026-11-19 — prostota i szansa na hit]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Ring Potworów — pomysł]] · [[00 Start]]
