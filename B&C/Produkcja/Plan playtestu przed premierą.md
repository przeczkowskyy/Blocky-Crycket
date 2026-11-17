---
status: propozycja
tags: [produkcja, playtest, balans]
---
# Plan playtestu przed premierą

## Opis
Co sprawdzamy na żywych graczach, zanim gra wyjdzie, i jakie liczby zbieramy. To propozycja agenta Karola z 17.11.2026 — odpowiedź na zapowiedź Karola i Pawła z trzeciej sesji 14.11 („playtest przed premierą”). Nic tu nie jest ustalone. Plan opiera się na D-060 (jajka: „do playtestu”), D-074 (mini-gra Pancerza „na próbę”), D-076 z korektą Karola (ok. 10 godzin gry do ostatniego biomu), D-078 (pomijanie walk) i liczbach roboczych z `tools/walka/BALANS_1711.md`.

### Trzy pytania, na które test ma odpowiedzieć

| Pytanie | Co mierzymy | Cel roboczy (z kalkulatora, do zmiany) |
|---|---|---|
| **Jajka (D-060):** same inkubatory czy także rzadki drop z potworów? | po ilu minutach gracz kupuje pierwsze jajko; ile jajek w pierwszej godzinie; czy wraca do inkubatora po każdej przegrodzie | pierwsze jajko w pierwszych 15 minutach u większości graczy |
| **Training Center i Pancerz (D-050, D-074):** czy trening bawi i nie wypiera walki? | jaka część czasu gry idzie na trening; jak rundy rozkładają się na mini-gry; odsetek trafień w 1. i w 10. rundzie; czy ktoś w ogóle wybiera mini-grę Pancerza | ok. 20% czasu na trening; żadna mini-gra nie zbiera ponad połowy rund |
| **Tempo i trudność (D-076):** czy las trwa tyle, ile ma trwać, i czy da się przegrać? | czas do pokonania Strażnika lasu; odsetek wygranych walk ze zwykłymi potworami i ze Strażnikiem; ile przegranych przed pierwszą wygraną ze Strażnikiem; jaka część walk jest pomijana | las ok. 30 minut (wariant rosnący); zwykłe potwory ok. 85% wygranych, Strażnik ok. 65% |

### Jak testujemy
- **Tura 1 — wewnętrzna:** Karol, Paweł i 3–5 znajomych, po 45–60 minut. Jedna osoba patrzy graczowi przez ramię i notuje, gdzie się gubi. Na koniec pięć pytań: co było najfajniejsze, co nudziło, czego nie zrozumiałeś, czy zagrałbyś jutro, co byś kupił.
- **Tura 2 — zamknięta:** 15–25 graczy z docelowej grupy wiekowej (za zgodą rodziców), co najmniej 30 minut, większość na telefonie. W tej turze połowa serwerów dostaje wariant z rzadkim dropem jajek z potworów — porównujemy długość sesji i liczbę walk.
- **Liczby zbiera telemetria gry** (D-023, [[Telemetria gry]]): same liczby zbiorcze, bez nazw i identyfikatorów graczy. Do włączenia potrzebna jest testowa publikacja miejsca — to decyzja ludzi.

### Lejek pierwszej godziny (kroki do `Telemetria.lejek`)
1. wejście do gry → 2. wybrana klasa → 3. pierwsza walka → 4. pierwsza wygrana → 5. pierwsze jajko → 6. pierwsza runda treningu → 7. druga przegroda lasu → 8. pierwsza próba ze Strażnikiem → 9. Strażnik pokonany → 10. wejście do Bagna.

Do tego liczniki zdarzeń: walka wygrana / przegrana / pominięta (z gatunkiem potwora), runda treningu (z nazwą mini-gry i odsetkiem trafień w przedziałach), kupione jajko, użyty Kamień Powrotu.

### Kiedy wynik zmienia decyzję (progi robocze)
- **Jajka:** jeśli mniej niż połowa graczy kupi jajko w pierwszych 30 minutach albo wariant z dropem wydłuża sesję o ponad 15%, wracamy do rozmowy o dropie z potworów (D-060).
- **Trening:** jeśli jedna mini-gra zbiera ponad połowę rund albo trening zajmuje ponad 40% czasu gry, wzór przyrostów wymaga poprawki ([[Pytania otwarte]] #50).
- **Pancerz:** jeśli mini-grę Pancerza wybiera mniej niż co dziesiąty trenujący, decyzja z D-074 („na próbę”) wraca na sesję.
- **Trudność:** jeśli ponad 30% graczy odchodzi po przegranej ze Strażnikiem albo nikt z nim nie przegrywa, zmieniamy liczby potworów.

## Do ustalenia
- Od kiedy test ma sens: co musi działać (zapis postępu, okna sklepów Pawła, jajka i pety, sześć mini-gier czy dwie).
- Kto zbiera testerów i zgody rodziców.
- Czy robimy testową publikację miejsca (prywatną) — bez niej telemetria i telefon nie zadziałają.
- Progi z tabel wyżej: czy takie liczby przyjmujemy.

## Powiązane
- [[Telemetria gry]]
- [[Rejestr decyzji]] (D-023, D-050, D-060, D-074, D-076, D-078)
- [[Pytania otwarte]] (50 i 51)
- [[Biom Las]]
- [[Zadania]]
