---
status: propozycja
tags: [gra, mechanika]
---
# System RPG

> [!warning] Status: propozycja
> Kanoniczna dokumentacja mówi tylko o „rozbudowanym systemie RPG” i o HUD z Levelem, HP, Maną/Energią i EXP. Poniższa lista pochodzi z późniejszej specyfikacji i czeka na potwierdzenie.

- Poziomy postaci i EXP
- HP, Mana / Energia
- Ekwipunek i inwentarz
- Umiejętności (hotbar w [[HUD]])
- Walka i loot

## Potwierdzone pośrednio przez kanon
- Elementy HUD: Level, pasek HP (czerwony), Many/Energii (niebieski), EXP ([[HUD]]).
- Nagrody z questów: Złoto, EXP, Loot ([[Karczma (Questy)]]).

## Decyzje i propozycje (stan 2026-11-14)
- **D-039 ✅ (Karol, 14.11):** drzewka umiejętności za Diamenty — postaci (bonus do EXP, większe szczęście do rolek), Twierdzy i każdego peta osobno. Waluty: D-038 (Złoto i Diamenty), D-040 (trzecia waluta i waluta petów).
- **Drzewko postaci:** [[Drzewko umiejętności postaci]] — D-047 (trzy gałęzie, punkty talentu) **odrzucona 14.11** z dwoma podpisami (Karol: płacimy tylko Diamentami), **D-055 zatwierdzona** (drzewko na klasę, pasywki procentowe, 0–3 sloty umiejętności); pytanie 34 zamknięte.
- **Statystyki** (Siła, Kondycja, Inteligencja, Zręczność, Szczęście, Pancerz) z punktami za poziom i dokupywaniem za Złoto: propozycja z rozmowy 12.11, w kodzie test `StatPoints.server.luau` i [[Okno ekwipunku]]; czeka na pytanie 17.
- **Druga sesja 14.11 (propozycje D-048–D-055):** rezygnacja z Energii — pasek „Many/Energii” w [[HUD]] zostałby paskiem Many (D-048); **Training Center** w Twierdzy jako źródło surowych punktów statystyk z mini-gier, bez limitu, z trybem AFK (D-050, pytanie 36); **klasy** Wojownik, Zwiadowca, Mag ze specjalizacjami w drzewku (D-054, pytanie 35); **drzewko na klasę** z pasywkami procentowymi i 0–3 slotami umiejętności aktywnych (D-055, wariant wobec D-047). Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]]. Po sesji D-050 (Karol: „bez trybu AFK — na razie”), D-054 i D-055 dostały oba podpisy.
- **Trzecia sesja 14.11 (propozycje D-056–D-063):** **model statystyk** — Siła: obrażenia zwykłych ciosów, Kondycja: życie, Inteligencja: moc umiejętności **i** odporność na magię, Zręczność: unik z limitem zależnym od klasy (Zwiadowca najwyższy), Szczęście: krytyk, **Pancerz jako punkty odejmowane od ciosu** (nie procent), blok z tarczy tylko u Wojownika (D-062; sporne: Pancerz trenowany czy z przedmiotów — pytanie 39, Wojownik z tarczą i unikiem — pytanie 40); Training Center jako **jeden budynek** z wyborem mini-gry, od pierwszego poziomu, pięć czy sześć mini-gier (D-063); węzły drzewek za Gemy bez punktów talentu, poziom daje punkty statystyk, sklep i strefy (D-057); trzy sekcje drzewek gracz / pety / Twierdza (D-056). Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
