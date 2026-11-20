---
status: propozycja
typ: pomysł-gry
gra: BONK
etap: porzucona
zdanie: "Bonk monsters into the sky, hatch pets, get stronger, unlock bigger lands."
ocena_agenta: 19
werdykt_agenta: popraw
ocena_karol: 
ocena_pawel: 
d1: 
d7: 
sesja_min: 
ccu: 
miejsce: 92789057272917
tags: [wytwórnia, pomysł, bonk]
---
# BONK

> [!warning] Porzucony 20.11.2026 (D-117)
> Nie rozwijamy i nie publikujemy. Prywatna wersja testowa zostaje. Zasoby i wiedza idą do [[Pet Arena]]: lot i nokauty, pety i jajka, Strażnicy jako bossowie, efekty, zapis, narzędzia budowy i prób. Co z niego wynieśliśmy: [[Lekcje z prototypów]].

Prywatna wersja testowa od 20.11.2026 (D-113). Projekt i stan budowy: [[BONK — projekt prototypu]], kod: `swiat/bonk/`.

## W jednym zdaniu
Uderzasz potwory, odlatują łukiem; monety, Moc, pałki, jajka i pety, trzy krainy ze Strażnikami.

## Pierwsze 10 sekund
Mocne: gracz od razu w lesie, przycisk BONK, pierwszy lot po ok. 5 s.

## Hak ciekawości
Słaby: tylko rzadki złoty potwór (2,5%). Poza tym każdy następny krok wiadomo z góry.

## Głębia
Słaba: rośnie jedna liczba; zagrody tworzą strategię zdominowaną (bije się tylko najlepszą dostępną).

## Inni gracze i pokazanie się
Strażnik bity wspólnie, Moc nad głową, korona, tablice — ale gracze nie wpływają na siebie.

## Moment do nagrania
Lot po łuku i HOME RUN — średni (efektowny raz, potem powtarzalny).

## Powód powrotu
Dzienny prezent i kolejne krainy — słaby.

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie | 3 | | |
| Pierwsze 10 sekund | 3 | | |
| Hak ciekawości | 1 | | |
| Głębia | 1 | | |
| Inni gracze | 1 | | |
| Pokazanie się | 2 | | |
| Moment do nagrania | 2 | | |
| Powód powrotu | 1 | | |
| Trend | 2 | | |
| Koszt dla nas | 3 | | |

## Krytyka agenta
- **Karol ma rację** (20.11, [[Lekcje z prototypów]]): BONK jest prosty i logiczny, ale nie ma haka ani głębi — nudzi po kilku minutach. To nie wina motywu „bonk”, tylko pętli „liczba rośnie” bez niczego nieznanego.
- **Najmocniejszy argument za obecną wersją:** symulatory „liczba rośnie” trzymają dzieci (np. Pet Simulator); Karol grał sam, bez innych graczy, i nie jest graczem docelowym. **Odpowiedź:** tamte gry mają ogromną głębię (setki petów, handel, wydarzenia); my nie mamy żadnej warstwy, która to zastępuje — więc ten argument nie ratuje obecnej wersji.
- **„Viral na bonki przeminął” — w połowie prawda** (badanie 20.11, [[Radar trendów]]): format „uderzaj dla liczby” umarł (Kick a Lucky Block: 1,7 mln graczy naraz → ok. 11 tys.), a BONK dziś to właśnie on. Ale „uderz i zobacz, co się stanie” rośnie najszybciej (Hyper Realistic Ragdoll: od zera do 113–132 tys. w trzy tygodnie). BONK ma czasownik z trendu, ale każdy lot jest taki sam — wariant z reakcjami potworów i prawdziwą fizyką: [[BONK Chain Reaction]] (22/30).
- **Pre-mortem (dlaczego BONK przegra):** (1) brak niewiadomej — gracz wie, co będzie za 10 minut; (2) pety i jajka nic nie zmieniają w graniu; (3) brak powodu, żeby obchodzili mnie inni gracze.
- **Co by to naprawiło (BONK 2.0, propozycja, ok. 2–3 dni pracy agenta):**
  1. **Cel do trafienia:** gracz celuje kierunkiem; potwory lądują na polu tarcz (x2, x5, x25, jackpot). Każdy potwór leci inaczej (slime się odbija, muchomor szybuje, wilk wiruje) — wybór potwora do tarczy to decyzja, a trafienie jackpotu to klip.
  2. **Pety, które coś robią na ekranie:** sam uderza, łapie monety, dodaje odbicie, magnes; rzadkie warianty „Huge” z komunikatem dla serwera.
  3. **Boss jako wydarzenie serwera:** odliczanie „boss za 2:00”, jedna prosta mechanika (tupot — skacz; świecący słaby punkt — krytyk), deszcz łupu z tajemniczymi zdobyczami.
  4. **Tajemniczy łup z każdego lotu:** mała szansa na rzadki przedmiot lub ozdobę, widoczny dla innych.
- **Werdykt:** popraw — ale **tylko jeśli** BONK 2.0 na karcie wyjdzie wyżej niż najlepszy nowy pomysł z Wytwórni. Jeśli nowy pomysł ma 22+ przy podobnym koszcie, lepiej budować nowy, a z BONK zabrać lot, efekty i pety.

## Najtańszy test
Pole tarcz + różne loty potworów w samym lesie (1 dzień), granie we dwóch: czy chce się „jeszcze jeden rzut”.

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[BONK — projekt prototypu]] · [[Lekcje z prototypów]] · [[Karta oceny pomysłu]]
