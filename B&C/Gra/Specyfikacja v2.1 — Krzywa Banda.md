---
status: propozycja
tags: [gra, specyfikacja, v2, mvp]
---
# Specyfikacja v2.1 — Krzywa Banda

> [!info] W skrócie
> Pełna specyfikacja robocza poprawionej gry (wersja 2.1, po przeglądzie czerwonego zespołu) — dla agentów i dla osób, które chcą znać liczby i uzasadnienia. Krótsze wersje dla ludzi: [[Myśl przewodnia v2]], [[Systemy gry v2]], [[Psychologia gracza v2]], [[Karta ocen v2 i plan sprawdzenia]]. To **propozycja**: nic tu nie jest kanonem, a zmiany kanonu wymagają decyzji Game Directora (rozdział 10).

> [!note] Pliki robocze, na które powołuje się tekst
> Raporty ośmiu soczewek, weryfikacje, cztery koncepcje, oceny sędziów i raporty czerwonego zespołu (`diagnoza.md`, `czerwony_*.md` itd.) nie są w repozytorium — leżą lokalnie u Karola (`%LOCALAPPDATA%\BlockyCrycket\prywatne\diagnoza_2026-11-13\`). Skrót diagnozy ze źródłami: [[Diagnoza pomysłu 2026-11-13]].

13.11.2026, redaktor prowadzący. **Propozycja, nie kanon**; zmiany kanonu wymagają decyzji Game Directora (§10). **F** = fakt ze źródłem (adresy w `diagnoza.md`, weryfikacjach i raportach czerwonego zespołu), **W** = wniosek, **H** = hipoteza.

Wersja v2 sprzed przeglądu leży w `v2_spec_przed_czerwonym.md` (ten folder). Ta wersja wprowadza naprawy zarzutów z `czerwony_gracz.md` (oznaczenia G-Z…), `czerwony_rynek.md` (R-Z…) i `czerwony_produkcja.md` (P-Z…). Każdy zarzut o wadze ≥ 3 ma odpowiedź w §12. Nowa symulacja krzywych: `v21_sim/krzywe_v21.py`.

---

## 0. Co zmieniło się po czerwonym zespole

1. **Fantazja przesuwa akcent z „armii kumpli” na „krzywy montaż”.** Półka „pokonany wróg dołącza” jest zajęta i przetrzebiona (**F**: ARISE CROSSOVER 3 719 graczy naraz wobec rekordu 334 189; Catch a Monster 2 298; Evomon 2 178 z polowaniem na „Shiny”; odczyt API 13.11.2026, R-Z3). Jedyne, czego konkurencja nie ma, to widoczny błąd montażu z Crycketem.
2. **Lśniący wypada w całości.** Zastępują go warianty za wyczyn: bez losu, bez terminu, za umiejętność (G-Z10, R-Z3). Gra nie ma już żadnej losowej nagrody.
3. **Umiejętność przyspiesza postęp, pieniądze nie.** „Hałas wabi” podnosi tempo nokautów tylko za grę (G-Z2). Finał liczy mnożnik z długości łańcucha i ma koszt czekania (G-Z6).
4. **Postęp pogłębia żart, a nie go prostuje.** Stopnie: Krzywy → Bardziej Krzywy → Arcydzieło Krzywizny (G-Z7).
5. **Gra działa na pustym serwerze.** Echa band (wyraźnie oznaczone), Kocioł świata, plac skalowany do obecnych graczy (R-Z2, G-Z11).
6. **Dwa etapy zamiast jednego MVP.** Etap A (MVP-4, rdzeń i pierwsze 10 minut, ok. 128 h) i Etap B (pakiet na pomiar: echo, druga strefa, Spiżarnia, sklep, ok. 66 h). Pomiar i decyzje dopiero po Etapie B (P-Z1, G-Z1).
7. **Grudzień to miękka premiera bez decyzji „zakończyć”.** Decyzje zapadają na dwóch ważnych kohortach w styczniu albo później, z warunkiem gęstości ruchu (R-Z1, R-Z7). Zamrożenie 20.12–3.01.
8. **Natywna replikacja Robloxa zamiast własnej.** Własna powstaje tylko, gdy pomiar na telefonie tego wymaga (P-Z4).
9. **Bramka B1 z jedną miarą główną i botem-klikaczem jako linią bazową** (P-Z2, G-Z4).
10. **Karta ocen liczona dla wersji, która trafi do pomiaru**, bez pozycji z kolejki cięć (P-Z8). Średnia 7,4 → **6,0**, minimum 6 → **5** (§11).

---

## 1. Myśl przewodnia

**Zdanie fantazji (12 słów):** *Rozbij potwora na klocki, a kot złoży go krzywo — z błędem, który daje moc.*
EN (do testu): *Bonk monsters to bits — a wizard cat rebuilds them wrong, and wrong works.*

**Obietnica dla gracza:** im bardziej krzywo, tym lepiej. Każdy pokonany potwór może wrócić jako kumpel z błędem montażu, który coś robi, a każdy kolejny stopień dokłada błąd i moc. Szybciej idzie temu, kto lepiej gra, a nie temu, kto płaci. Nic ci nie przepada.

**Filary:**

| Filar | Co widać w 5 s | Usuwa |
|---|---|---|
| **1. Krzywo znaczy mocniej** | Crycket z kamienną miną przykręca Tarczakowi tarczę tyłem, a Tarczak osłania ci plecy | P1, P10, R-Z3 |
| **2. Umiejętność przyspiesza, pieniądze nie** | BONK posyła wroga w stado jak kulę w kręgle, KOMBO ściąga następne stado | P2, G-Z2 |
| **3. Twoja banda gra też u innych** | na leśnej ścieżce stoi oznaczone echo cudzej bandy, twój wybity wróg leci w nie: „PODANIE!” | P6, R-Z2 |
| **4. Nic nie przepada** | strona Albumu 80% i sylwetka „???” czekają, aż wrócisz | P4, P7 |

Zmiana wobec v2: filar „Serwer gotuje razem” wymagał ludzi, których w pierwszych tygodniach nie będzie (**W**, R-Z2). Filar „Banda pracuje bez ciebie” stał na Pracowni offline i Najemniku z tygodnia 5. Oba zastępuje filar 3, który działa przy jednym graczu na serwerze.

**Anty-cele.** Gra nie jest:
- portem cudzej gry;
- grą o armii (nie konkurujemy liczbą kumpli, tylko ich krzywizną);
- symulatorem petów z jajkami za R$ ani grą o polowaniu na rzadkie;
- oglądaniem walki ani tycoonem czekania;
- hubem-miasteczkiem z teleportem przed bramką D7;
- MMO z czatem i gildiami, PvP z utratą, grą na kampienie, grą z 20 systemami.

Nie projektujemy pod konta Kids 5–8, ale ich nie blokujemy (treść na ocenę Mild).

**Publiczność:** najpierw 16+, bo tylko oni widzą nową grę (**F**, kids-and-select); po progu 250 dochodzą 9–15.

**Marka.** Logo dostaje sens w świecie: **Pracownia Montażu BLOCKY & CRYCKET** („Rozbijamy. Składamy. Prawie dobrze.”) na szyldzie placu, okładce Albumu i komiksie po bossie.

**Tytuł na platformie** (ZMIANA KANONU, inny niż logo). Zasady (G-Z9, R-Z3, R-Z10): bez słów Monster, Build, Maker, Catch i Shadow, bez wzoru „Bonk & …”, najwyżej 3 słowa, czytelny przy 150 px, zwrot akcji zamiast kategorii. Kandydaci do makiety siatki: „Crooked Crew”, „Rebuilt Wrong!”, „Almost Fixed”. **F** (omni-search, 13.11.2026): słowo „Crooked” jest prawie wolne („Crooked Bus”: 129 graczy). Sprawdzenie znaków towarowych (EUIPO, USPTO, Roblox) to warunek B2 z przypisanym właścicielem, a nie dopisek.

**Ikona.** Jeden kadr: Crycket z kamienną twarzą przykręca potworowi część tyłem (R-Z3). Do makiety idą trzy szkice: (a) montaż tyłem, (b) krzywy potwór idzie za awatarem, (c) podział po przekątnej „przed i po” (G-Z9).

**Obsada.** Wygląd zgodny z D-003, bez żartów z wyglądu. Zmiany ról to ZMIANA KANONU (§10).

| Postać | Rola | Wada | Powiedzonko | Gag |
|---|---|---|---|---|
| **Crycket** (Kot-Mag) | kot przy każdym graczu (gracz wybiera kolor szaty); jeden „prawdziwy” Crycket jako NPC, szef Pracowni | składa „prawie dobrze” | „Pasuje. Prawie.” | przy montażu śmiertelnie poważny, widać to w zbliżeniu |
| **Blocky** (Rycerz) | strażnik placu, pierwszy cel BONK-a | przecenia się | „Mam to pod kontrolą!” | ląduje w Kotle; raz w sesji wygrywa: łapie Żarłoka chochlą (G-Z19) |
| **Mistrz Chochla** (Karczmarz) | „Zupa u Chochli”, zamówienia z garnka | każda zupa wychodzi inna | „Zupa dnia. Nie pytaj.” | z garnka wyskakuje potworek |
| **Burek** (pies) | pierwszy towarzysz | nie odda miecza | „Wrr-mf!” | miecz w pysku zahacza o drzewa |
| **Kisiel** (slime) | wsparcie, z jaja (po D7) | wszystko się do niego klei | „Blup.” | w środku widać but i monetę |
| **Maks** (smok) | dalekosiężny (po D7) | myśli, że jest ogromny | „Kłaniać się!” | jego cień jest wielki |

**Ton.** Slapstick w ruchu dla 9–15 (lądowania, krzywe modele) i ironia **w obrazie** dla 16+ (zbliżenie na kamienną minę kota, pieczątka „PRAWIE”, miniatura jak strona instrukcji montażu z przekreślonym krokiem). Tekstu w MVP najwyżej 20 linii (P-Z14). Bez alkoholu: zupa, kompot, ogórki, mikstury. Beczka staje się **słojem z ogórkami** (Słojak), bo beczka przy 150 px wygląda jak beczka piwa (H, R-Z11).

---

## 2. Pętla rdzenia

**Czynność.** Gracz chodzi awatarem R15 po wspólnej strefie, za nim Crycket i do 3 towarzyszy, którzy biją sami. Jeden duży przycisk **BONK** (odnowienie ok. 0,8 s, H): trafiony wróg leci 10–20 studs po łuku w kierunku, w który gracz patrzy (G: 6–14 studs ledwo się czyta), przewraca innych („KOMBO ×N”) i ogłusza ich na 1,5 s. Banda zadaje ogłuszonym podwójne obrażenia.

**Hałas wabi (G-Z2).** W opanowanej strefie wrogowie przychodzą stadami po 4–8 co 8–12 s. KOMBO ≥ 3 i Finał z ≥ 5 wrogami ściągają dodatkowe stado. Tempo rośnie z ok. 18 nokautów na minutę (bot) do najwyżej ok. 30 (wprawny gracz) **wyłącznie dzięki grze**. Decyzja: czekać, aż stado się zbije, czy zdejmować pojedynczo.

**Finał Crycketa: Wielkie Sklejenie (G-Z6).** Klej rośnie z nokautów. Pełny pasek po 5 s zaczyna powoli opadać, więc czekanie kosztuje. Finał skleja wrogów w promieniu w chwiejną wieżę. Mnożnik złota liczy się z długości ostatniego łańcucha (geometria), a klocki są stałe: +1 za każdego sklejonego. Drugi BONK ustawia kierunek upadku wieży, która może przewrócić kolejne stado.

**Decyzje co 2–5 s:** kogo uderzyć, w którą stronę i kiedy; czekać na zbite stado czy bić pojedynczo; kiedy odpalić Finał przed opadnięciem Kleju; ucieczka z kręgu Pniaka; Tarczak z boku. Decyzja jest **dostępna** co ≤ 5 s, a **wymagana** na froncie i przy bossie. Kto stoi, ma autocel w stożku 60°, który nigdy nie wybiera celu niemożliwego do trafienia i zawsze pokazuje krążek pod celem (G-Z14).

**Wspólni wrogowie i PODANIE (P-Z9).** Wrogowie należą do obszaru, nie do gracza: najwyżej 8 wokół gracza, przy kilku graczach budżet obszaru = 6 × liczba graczy w promieniu. Łup dostaje każdy, kto trafił w ciągu 5 s, ale liczy mu się do własnego limitu nokautów na minutę. **PODANIE:** wybity wróg z naprowadzaniem leci do najbliższego cudzego stada (żywej bandy albo echa) w promieniu 30 studs. Obaj dostają +1 klocek i dymek, nie drugi pełny łup.

**Sok (G-Z5) — osobny blok godzin w §9:** stop-klatka 60–80 ms tylko przy trafieniu przewidzianym u klienta; dymki BONK!/KLONK!/PUF!; dźwięk coraz wyższy z kombo; rozpad na klocki z pulą obiektów (tylko własne i bliskie nokauty); animacja BONK awatara R15; wieża Finału z kołysaniem i upadkiem; zbliżenie montażu w rogu ekranu (ViewportFrame 1,5 s, bez odbierania sterowania) przy pierwszym montażu każdego gatunku i przy każdym nowym stopniu; 3 lądowania z gagiem (w drzewie, w Kotle, w cudzym stadzie), tylko przy kombo ≥ 3, Finale i pierwszym nokaucie gatunku, żeby pula nie zużyła się w kwadrans. Trafienie ≤ 0,3 s, bez błysków na cały ekran. **Nie da się tanio** (G, sekcja 3): rozciągania brył i tuszu na modelach 3D. Tusz zostaje w UI, dymkach, miniaturach i komiksie; obrys Highlight na modelach tylko po pomiarze na telefonie (limit 255 obiektów na klienta, **F**).

**Kompresja.** W opanowanej strefie jeden BONK nokautuje. Stara strefa to szybkie farmienie stopni, a wyzwanie przechodzi na front: nowa strefa, Żarłok na Trudnym, Spiżarnia.

**Dlaczego wytrzyma setne powtórzenie (W, do obalenia w B1):** tempo zależy od geometrii BONK-a i decyzji o stadzie; Finał to prawdziwy zakład z kosztem; każdy stopień zmienia zdolność kumpla, więc skład się zmienia; warianty za wyczyn dają cele zależne od umiejętności; echa i inni gracze zmieniają planszę. Jeśli człowiek nie bije bota-klikacza, ta teza upada (§9, B1).

**Serwer i klient (P-Z4).** W B1 i MVP wrogowie to zwykłe modele z jedną częścią główną, a lot liczy serwer impulsem z natywną interpolacją Robloxa. U klienta natychmiast pojawia się tylko efekt kosmetyczny: stop-klatka, dźwięk, dymek. Serwer sprawdza zasięg z tolerancją +3 studs i oknem 300 ms. Własna replikacja albo własność sieciowa trafionego wroga u atakującego (H, ryzyko exploitów, serwer i tak liczy łup z limitem) wchodzą tylko wtedy, gdy pomiar na telefonie pokaże < 30 kl./s albo bramka soku pęknie z powodu opóźnienia.

**Budżet telefonu.** 8 graczy na serwer (próba 12 botami w pomiarze technicznym). Krzywe Miasteczko (6160 części) poza MVP (P-Z10). Twardy budżet części statycznych ustalony z pomiaru w dniu 5 (≈ 23.11).

---

## 3. Oś czasu gracza

### Pierwsza minuta (lokalna, bez tekstu, bez okien)

Aktorzy samouczka istnieją tylko u klienta, w miejscu 20 studs od placu; serwer zapisuje kroki lejka i przyznaje stałą nagrodę (P-Z5). Pierwsza minuta nie obiecuje innych graczy.

| Czas | Co się dzieje | Lejek (próg H) |
|---|---|---|
| 0:00 | Ekran ładowania znika ≤ 1 s po zasobach (dziś ≥ 5,8 s, **F**). HUD: duży przycisk i Złoto. Obok Blocky | F0 |
| 0:01 | Blocky stuka się w hełm i wskazuje na siebie. Przycisk pulsuje ikoną dłoni i czeka (gracz najpierw rusza kamerą, G) | — |
| ≤ 0:10 | **BONK!** Blocky ląduje głową w Kotle, kciuk w górę | F1 ≥ 90% (≤ 10 s) |
| +2 s | Słojak (słój z ogórkami na nóżkach) porywa chochlę. Wbiega Burek z mieczem w pysku | — |
| +4 s | BONK w Słojaka: wpada w dwóch innych, „KOMBO ×3”, Burek gryzie ogłuszonych | — |
| +7 s | Słojaki pękają na klocki. Z „pop!” pojawia się Crycket, klocki lecą do torby, licznik przeskakuje z 7 do 10 (siedem pól wypełnionych od początku, bez zdania) | F2 ≥ 85% |
| ≤ 0:30 | Zbliżenie w rogu: kamienna mina kota, wieko przykręcone do góry nogami, pieczątka „PRAWIE”. **PUF!** Słojak dołącza i łapie wiekiem monety | F3 ≥ 80% (≤ 30 s) |
| 0:30–0:50 | Stado 4–6 Słojaków; nowy licznik „Bardziej Krzywy 10/60” | — |
| 0:50–1:00 | Smuga do Krzywego Lasu | F4 ≥ 70% (≤ 75 s) |

Poprawka wobec v2: licznik nie dobijał do 10/10 w 0:33, tylko w 0:10 (niespójność, G). „Wow” montażu przychodzi wcześniej.

### Pierwsze 10 minut (MVP-4): 5 pojęć, jedno co ok. 2 min

1. **BONK** (≤ 0:10).
2. **Banda i krzywy montaż** (≤ 0:30); w lesie ok. 1:40 drugi kumpel: Pniak z korzeniami na górze, który wiruje.
3. **Finał** (~2:00): ten sam przycisk świeci, „Wielkie Sklejenie ×5”, drugi BONK przewraca wieżę.
4. **Album** (~3:00): zakładka tylko pulsuje, sama się nie otwiera; sylwetki „???”.
5. **Żarłok** (~7:00–10:00): Kocioł się zapełnia, Żarłok wyskakuje i biegnie do strefy gracza (bez marszu na plac, G-Z14). Dwie fazy z biblioteki zachowań, ok. 90 s. Nagroda: Patelnia (BONK w linii), Kryształy, Blocky łapie Żarłoka chochlą.

Tarczak dopiero po Finale (~3:30). Porażka to jedno KLONK i od razu strzałka z boku (≤ 1 s), bez „5 s bezradności” (G-Z14). Ok. 6–8 min pierwszy kumpel awansuje na Bardziej Krzywego: nowy błąd w zbliżeniu. Po bossie pasek „Na jutro” na 3 s (G-Z18), bo karty przy wyjściu przez menu Robloxa nie da się pokazać (**F**, GuiService, pewność średnia). F9: sesja ≥ 10 min u ≥ 30%.

Czego v2.1 świadomie nie spełnia z „dziesiątki” K2 w briefie: dochodu na sekundę w ≤ 5 min (Pracownia w miesiącu 2) i komiksowej okładki po bossie (Etap B).

### Dzień 2, tydzień 2, miesiąc (wersja do pomiaru: 2 strefy, Spiżarnia)

Symulacja `v21_sim/krzywe_v21.py` (H): 4 gatunki na strefę, progi 10/60/300, tempo 9 → 18 nokautów/min (bot), 23 (człowiek 1,3×), 29 (wprawny 1,6×), 70% czasu na froncie.

| Ile gra dziennie | Strefa 2 otwarta | Wszystkie Bardziej Krzywe w s2 | Arcydzieła s2 | Wszystkie Arcydzieła (obie strefy) |
|---|---|---|---|---|
| 15 min, człowiek | dzień 2 (21 min gry) | dzień 4 | dzień 9 | dzień 13 (187 min) |
| 45 min, człowiek | dzień 1 | dzień 2 | dzień 4 | dzień 5 |
| 15 min, bot | dzień 2 | dzień 4 | dzień 10 | dzień 15 (218 min) |

Dla porównania jedna strefa (stan miękkiej premiery): wszystkie Arcydzieła po 70–82 min gry, czyli w 2.–3. dniu przy 45 min dziennie i w 5.–6. przy 15 min. To potwierdza G-Z1: z jedną strefą pomiar D2–7 mierzy ścianę treści.

**W:** gracz grający 15 min dziennie ma cele z Albumu do ok. 2. tygodnia. Gracz grający 45 min kończy Album w 5. dniu, a dni 6–28 niosą mu tylko Spiżarnia (nieskończone piętra), warianty za wyczyn i paczka danych co 2–3 tygodnie. Dlatego K4 ma 6, a nie 8 (§11). Prestiż (Wyprawa) wchodzi dopiero po bramce D7.

---

## 4. Systemy i ekonomia

| System | Rola | Etap |
|---|---|---|
| BONK, kombo, hałas wabi, PODANIE | rdzeń | A |
| Banda (3 miejsca i Crycket), poziomy za złoto do limitu stopnia | rdzeń, kolekcja | A |
| Album: Krzywy / Bardziej Krzywy / Arcydzieło (każdy stopień dokłada błąd i moc) | drabina 1 | A |
| Finał Crycketa (Klej z opadaniem) | decyzja | A |
| Moc bandy: jedna duża liczba, liczby ×10 na strefę | most do „cyferek” Game Directora (G-Z15) | A |
| Lokalny Kocioł i Żarłok (normalny) | szczyt sesji | A |
| Patelnia (druga geometria BONK-a) | wariacja | A |
| Zaproszenie, premia +20% za przybyłych razem, serwery prywatne | społeczność | A |
| Pasek „Na jutro” i mini-panel w Albumie | powroty | A |
| Echo bandy (raport bez waluty) | filar 3 | B |
| Kocioł świata (dzienny licznik globalny) | „nasze” | B |
| Spiżarnia Bez Dna: zamówienie u Chochli → instancja; piętra HP × 1,15^piętro; dopalacz 1 z 3 na bieg; rekord i top 100 | drabina 2; kanoniczny mini-dungeon z D-004 | B |
| Strefa 2 z samych danych (4 gatunki), 4. gatunek strefy 1, Sława ★ jako brama | treść, próba generalna | B |
| Warianty za wyczyn (1–2 na gatunek), Żarłok na Trudnym | drabina 3, status | B |
| Sklep: 2× Złoto, Zupa, Kostium towarzysza | K7 | B |
| Okno „Banda i Ekwipunek” w układzie rzędu bandy | UI | B |
| Pracownia-lite (wygląd stanowiska za złoto, zł/s online) | „moje”, ujście złota | miesiąc 2 |
| Jaja i Kisiel, komiksowa okładka po bossie, tryb zdjęcia, „Zapisz klip” | — | B (okładka) / po D7 |
| Wielka Wyprawa (prestiż), Drużyna Karczmy, Sparing, pełna Twierdza, hub z mapą | systemy | po bramce D7, najwyżej jeden na kwartał |

**Waluty** (odpowiedź na #6, propozycja):

| Waluta | Skąd | Na co |
|---|---|---|
| **Złoto** | walka (× kombo), Zupa | poziomy towarzyszy do limitu stopnia (Krzywy 10, Bardziej Krzywy 25, Arcydzieło 50); od miesiąca 2 wygląd Pracowni |
| **Magiczne Kryształy** | bossowie, wyczyny, progi Albumu | kosmetyka zdobywana w grze, kolor szaty Crycketa, ozdoby |
| **Klocki gatunku** | tylko nokauty | licznik strony Albumu, nigdy na sprzedaż i nigdy przyspieszane zakupem |

Diamenty znikają. Nie ma waluty za R$.

**Niezmiennik ekonomii.** Płatny mnożnik działa tylko na złoto, złoto podnosi poziomy tylko do limitu stopnia, a tempo nokautów ogranicza budżet spawnu, który rośnie wyłącznie dzięki grze (hałas wabi). Płacący skraca jedynie rozbieg w strefie: do strefy 2 po ok. 21 min wobec 23 min (1,1×, H, `v2_sim/krzywe.py`). Mnożniki eventów +25–100%, przed każdym arkusz wartości oczekiwanej.

**Telefon:** joystick po lewej, BONK po prawej (ok. 1,5 × przycisk skoku), Finał nad nim tylko wtedy, gdy jest gotowy; cele dotyku ≥ 44 pt (H); zasady wrogów rozpoznawalne po kształcie, nie tylko po kolorze; tekst wyłącznie natywny, z tabeli.

---

## 5. Psychologia gracza

| Potrzeba | Mechanika | Wersja uczciwa | Czerwona linia |
|---|---|---|---|
| Kompetencja | geometria BONK, hałas wabi, Finał z kosztem czekania, Żarłok na Trudnym, Spiżarnia | szybciej idzie temu, kto lepiej gra | brak płatnej siły w Spiżarni i Sparingu; brak ofert po porażce |
| Autonomia | które stado, kiedy Finał, skład, zamówienie z garnka | zamówienie ważne do wykonania | żadnych misji przepadających o północy |
| Ciekawość | sylwetki „???”, odsłona błędu w zbliżeniu, nowy błąd na każdym stopniu | wszystko deterministyczne i jawne | zero losowych nagród, także darmowych |
| Własność | Album, rekord Spiżarni, kolor szaty kota | nic nie przepada | brak sprzedaży towarzyszy, stron i klocków |
| Więź | PODANIE, echo, Kocioł świata, zaproszenie | premia tylko za przybyłych razem | echa nigdy nie udają żywych graczy; brak „zaproś 3, by odblokować” i premii za obcych |
| Status | warianty za wyczyn, top 100 pięter, złota ramka Arcydzieła | widać zasługi, nie wydatki | tablica bez listy ostatnich, z wyłącznikiem widoczności; brak ogłaszania zakupów |
| Humor | błędy montażu, lądowania, Blocky w Kotle | z potworów i bohaterów | nigdy z gracza ani z wyglądu |

**Błąd montażu to zdolność, a postęp go pogłębia (G-Z7).** Tarczak: tarcza z tyłu (osłania plecy) → dwie tarcze plecami do siebie (blok z obu stron) → tarcza-kapelusz, która się kręci (odbija wokoło). Słojak: wieko do góry nogami łapie monety → dwa wieczka (większy magnes) → słój dnem do góry, ogórki wylatują jak pociski. Koszt: dwie podmiany klocków w `czesci.json` na gatunek i jeden wiersz danych. Żart odnawia się trzy razy na gatunek.

**Kształt sesji.** Cel 12–25 min z naturalnymi wyjściami: Żarłok, ukończona strona, rekord Spiżarni. Po 40 min Crycket ziewa i pokazuje pasek „Na jutro”, niczego nie blokując, bo ponad 60 min dziennie nie liczy się do sygnałów (**F**). Pasek pokazuje: niedokończone (strona 80%), ciekawe (sylwetka „???”), moje (rekord Spiżarni, raport echa), nasze (Kocioł świata). Mechanizmy (**F**): zaliczka 7/10 (Nunes i Drèze); ludzie wznawiają przerwane zadania w 67% przypadków, ale ich nie pamiętają, więc gra sama pokazuje, co przerwano.

**Zegary i test „co tracę, gdy nie wrócę?”**

| Zegar | Co tracę |
|---|---|
| Wypoczynek: za każdy dzień kalendarzowy 15 min ×2 klocków, narasta bez limitu, w jednej sesji zużywa się najwyżej 60 min (R-Z14) | nic; łączna premia nie zależy od rytmu wizyt |
| Kocioł świata | nic: daje wspólne efekty na teraz, a nie przedmioty dnia do zebrania |
| Raport echa | nic: licznik czeka |
| Gatunek tygodnia | nic: wraca w rotacji |
| Karta Bywalca | poza MVP, domyślnie wyłączona |

Wszystkie mechaniki regularności mają jeden wyłącznik w Configs i w ustawieniach (kierunek projektów DFA art. 17 i EU KIDS Act art. 15; to projekty, nie prawo, **F**, W-psychologia #7).

---

## 6. Społeczność i wirusowość

**Echo bandy (R-Z2, G-Z11; Etap B, ok. 7 h).**
- Serwer zapisuje migawkę składu, stopni i kostiumów każdej bandy do wspólnej puli.
- Gdy w strefie jest mniej niż 3 żywych graczy, serwer wpuszcza do 2 ech. Mają wyraźną ikonę „echo” i półprzezroczysty obrys, nie mają nicków, nie piszą i nigdy nie udają żywych graczy.
- PODANIE działa na echa: żywy gracz dostaje +1 klocek, a właściciel echa +1 w liczniku „Twoje echo podało 4 razy”, widocznym przy następnym wejściu.
- W Etapie B nagrodą jest tylko raport i pieczątka w Albumie. Kryształy za echa dopiero przez skrzynkę z wpisami tylko dopisywanymi, nigdy przez zapis do cudzego profilu (P-Z13).
- Pulę na start zasilają bandy zespołu, opisane jako „Banda Pracowni”.

**Kocioł świata (R-Z2).** Dzienny licznik globalny nokautów ze wszystkich serwerów, widoczny na placu („Dziś świat ugotował 3 zupy”). Progi wyzwalają wspólne efekty na teraz (czapki-garnki, częstszy Żarłok przez godzinę), a nie przedmioty do zebrania. Lokalny Kocioł przywołuje Żarłoka z progiem ∝ √(liczba graczy), więc przychodzi co 10–12 min także w pojedynkę.

**Plac skalowany do obecnych.** Stoją tylko stoiska obecnych graczy i stoisko Crycketa (jawnie NPC), bez pustych miejsc, które działają jak ujemny dowód społeczny (R-Z2).

**Razem:** zaproszenie w ≤ 2 stuknięcia (`PromptGameInvite`); +20% klocków płasko dla przybyłych razem; zwykłe dołączenie do znajomego; serwery prywatne (darmowe dla Roblox Plus). **Bez czatu:** własne Quick Words („PODANIE!”, „Do Kotła!”, „Jeszcze raz?”) po D7; w MVP domyślne gesty.

**Momenty do nagrania (≤ 10 s):** odsłona błędu montażu w zbliżeniu, upadek wieży Finału, Blocky łapiący Żarłoka, nowy stopień kumpla. Tryb zdjęcia i przycisk „Zapisz klip” po D7, po sprawdzeniu, co CaptureService umie nagrać (H, R-Z6).

**Twórcy wideo (R-Z6).** Zero pracy z twórcami przed wejściem do kont Kids i Select, bo widzowie 9–15 nie wejdą do gry w okresie próbnym (**F**). Potem 3–5 mikrotwórców za 50–200 $ albo 3–10% przychodu przez 30–90 dni (niska pewność), oznaczonych jako reklama; decyzja finansowa Game Directora (#13). Klipy zespołu: 2 tygodniowo, nagrywane przez agenta, wliczone w live-ops.

**Progi (H), liczone uczciwie:**
- w sesjach z ≥ 2 żywymi graczami: ≥ 50% z interakcją;
- w sesjach solo: ≥ 30% z co najmniej jednym PODANIEM na echo;
- ≥ 10% nowych graczy przychodzi ze znajomym albo kogoś zaprasza;
- raport echa u ≥ 30% graczy z D7.

---

## 7. Monetyzacja uczciwa

| Produkt | Typ | R$ | Co daje | Etap |
|---|---|---|---|---|
| 2× Złoto | pass | 199 | Napis na przycisku: „×2 złota z walki. Nie przyspiesza klocków, Albumu ani Spiżarni.” Jeśli konwersja < 0,3% w 30 dni, zamiana na pass wygody | B |
| Zupa dla wszystkich | developer product | 49 | cały serwer: Kocioł 2× szybciej i czapki-garnki na 15 min; kupujący +20% złota; anonimowo, najwyżej 1 aktywna; działa też w pojedynkę | B |
| Kostium towarzysza | product | 99–199 | wygląd kumpla, widoczny na echach i w Albumie (wartość także solo) | B |
| Serwer prywatny | private server | ok. 100 / mies. | darmowy dla Plus; twórca dostaje do 100 R$ miesięcznie za czas subskrybenta (**F**) | A |
| Album Deluxe, Klub Crycketa, skórka Pracowni, taniec bandy | pass | 149–349 | kosmetyka i wygląd | po D7 |
| Tor sezonu | pass | 449 | kosmetyka bez terminu, z wyrównaniem | po D7, tydzień 10+ |
| Reklama nagradzana | darmowa Zupa | — | tylko 13+, od 2000 gości miesięcznie (**F**) | później |

**Zasady:** ceny z API i w Configs, cena w R$ na każdym przycisku; jedno wejście do sklepu, po pierwszym Żarłoku; osobiste płatne mnożniki ≤ ×2; PolicyService gotowy na reklamy i subskrypcje; Plus tylko w menu serwerów.

**Nigdy:** los ani szczęście za R$ (także w passach), waluta za R$, sprzedaż towarzyszy, stron, klocków i automatycznego farmienia, skracanie liczników, oferty po porażce, „ostatnia szansa”, przepustki z terminem, podpis kupującego (także opcjonalny), ogłaszanie zakupów.

**Cele zapisane przed testem (H):**
- K7 jest niemierzalny do ≥ 2000 nowych graczy (240 osób przy 1,5% to 3–4 zakupy, P-Z15);
- pierwszy zakup w 30 dni u ≥ 1,5% graczy 16+, z czego ≥ 1/3 to produkty o wartości solo;
- ≥ 1,2 dnia z wydatkiem na płacącego (sygnał „dni z wydatkami”, **F**, od 20.08.2026);
- bramka monetyzacji jako percentyl R$ na DAU w panelu, a płatny ruch poza progiem 250 tylko wtedy, gdy przychód na nowego gracza ≥ koszt wejścia zmierzony we własnej kampanii (R-Z5);
- test pay-to-progress: mediana czasu do strefy 2 bez płacenia ≤ 1,4 × czas z płaceniem;
- test z rodzicem: po 30 s rodzic umie powiedzieć, co kupuje i za ile; ankieta treści: Mild.

**Uczciwie: sufit przychodu jest niski z wyboru.** Przy 15 graczach naraz i średniej platformy to ok. 130 $ miesięcznie (W, R-Z5). W scenariuszu pesymistycznym (ok. 65%) gra może przez kwartał nie przekroczyć progu wypłaty 30 000 R$ = 114 $. W zamian katalog jest odporny na DFA, PEGI i IARC. Game Director potwierdza to wprost w decyzjach #6 i #12.

---

## 8. Live-ops: treść jako dane

**Zamknięta biblioteka zachowań (P-Z6, G-Z13).**
- Zasady wrogów: `osłona(kąt)`, `krąg(promień, czas)`, `lot(wysokość)`, `szarża(dystans)`, `dzielenie(liczba)`, `odbicie(liczba)`.
- Zdolności kumpli: `osłona(kąt)`, `magnes(zasięg)`, `wir(czas)`, `leczenie(ile)`, `prowokacja(promień)`, `odbicie(liczba)`.
- Gatunek = 1 zasada + 1 zdolność z parametrami + model z 3 wariantami stopni i 1 wariantem wyczynu + 3 żarty. Boss = sekwencja 2–3 zasad z progami HP.
- Nowe zachowanie liczy się jako system (najwyżej jeden na kwartał).
- **Próba generalna:** nowy gatunek z samych danych w ≤ 2 h bez nowego kodu. Pierwszy raz przed B3 (4. gatunek strefy 1), drugi raz w Etapie B (strefa 2).

**Jednostka treści.** Wiersz `Gatunek{id, strefa, zasada, zdolność, parametry, hp, progi={10,60,300}, błędy[3], wyczyn, model=swiat/potwory/<id>/czesci.json, żarty[3]}`. Inne tabele: Strefa, Boss, Broń, Modyfikator, Piętro, Żart. Kalendarz liczony z czasu UTC w kodzie, wartości z Configs, wydarzenia zakłada agent przez Open Cloud, grafiki człowiek akceptuje paczką raz w tygodniu.

**Rytm, który nie wypali (P-Z7, G-Z12, R-Z12):**

| Okres | Rytm | h/tydz. (obie osoby) |
|---|---|---|
| do 100 DAU | automatyczna rotacja „Gatunek tygodnia” z istniejących gatunków (liczona z kalendarza w kodzie, 0 h tygodniowo po zbudowaniu); paczka danych co 3–4 tygodnie (2 gatunki z biblioteki, ≤ 8 h); 2 klipy od agenta; bez wydarzeń z „Notify me” | ≤ 10 |
| po D7 ≥ 3% i ≥ 100 DAU | wydarzenie weekendowe z Configs (≤ 1 h) z „Notify me” (od ≥ 100 wizyt; H: ≥ 500 ulubionych); paczka co 2–3 tygodnie; boss co 4 tygodnie; jeden system na kwartał | ≤ 15 |
| zawsze | raz w miesiącu tydzień bez nowej treści (spłata długu, testy zapisu) | — |

Gdy dwa tygodnie z rzędu przekraczają limit, kolejna paczka wypada, a rotacja trwa dalej.

**Odpowiedź na klona (R-Z3):** wydarzenie z Configs w 48 h po pojawieniu się klona; maskotka na każdej miniaturze i grupa Roblox, żeby gracze szukali gry po nazwie.

**Spadek po szczycie.** Gasną wszystkie hity: Bee Swarm −88%, PS99 −94% od szczytu (**F**). Cel to ≥ 30% szczytu z dnia powszedniego po 8 tygodniach (H).

---

## 9. Plan produkcji: Etap A (MVP-4) i Etap B

**Zasady pracy (P-Z1, P-Z11, P-Z14):**
- dziennik godzin od dnia 0 z kategoriami gra / narzędzia / świat / dokumenty; narzędzia ≤ 10% godzin;
- do B2 każda noc agenta dotyka wyłącznie `src/` i `swiat/strefa1/`, a każde zlecenie ma linijkę „który próg B1/B2 to przybliża”;
- Krzywe Miasteczko i mapa teleportu jako propozycja hubu po D7, bez koła fortuny; kontener `TestWalki` usunięty ze wspólnego miejsca przed pierwszą publikacją;
- każda pozycja z właścicielem i datą w `Zadania.md`;
- **przy braku godzin przesuwa się data, a nie zakres pomiaru.**

### Etap A: MVP-4 (rdzeń i pierwsze 10 minut)

| Kto | Pozycja | h (H) |
|---|---|---|
| Karol | Zapis ProfileStore v1 (wersja schematu, migracje, dni gry do własnego D1) | 8 |
| | Sieć i straż (5 zdarzeń: BONK, Finał, Skład, Odbierz, Zaproś) | 4 |
| | Walka natywna: BONK, ogłuszenie, kombo, budżet obszaru, łup „kto trafił”, hałas wabi i stada, PODANIE +1 | 16 |
| | Biblioteka zachowań (3 zasady i 3 zdolności z parametrami, rozszerzana w B) i 3 gatunki | 4 |
| | Sok i Finał (lista z §2) | 16 |
| | Strefa 1 z generatora, lokalny Kocioł, Żarłok, Patelnia | 9 |
| | Pierwsza minuta lokalna | 5 |
| | Lejek F0–F9 (istniejąca Telemetria) i bot-klikacz | 4 |
| | Telefon bazowy i boty wydajności | 6 |
| | Zaproszenie, premia za przybyłych razem, serwery prywatne | 2 |
| | **Karol razem** | **74** |
| Game Director | HUD z odsłanianiem (BONK, Klej, Moc bandy) | 6 |
| | Panel Bandy (rząd 4 portretów; pełne okno w B) | 3 |
| | Album jako lista z sylwetkami i stopniami | 6 |
| | Pasek „Na jutro” i mini-panel | 3 |
| | UI soku: dymki, liczby, zbliżenie montażu | 3 |
| | Telefon dla każdego okna | 4 |
| | **Game Director razem** | **25** |
| Oboje | B0: jedna strona decyzji, scalenie gałęzi, osobne miejsca robocze | 5 |
| | Człowiek: szkic Crycketa i logo, 3 szkice ikony, miniatura „katalogowa”, ≤ 20 linii tekstu, paczki akceptacji | 10 |
| | Testy: werbunek, makieta siatki (n ≥ 40), B1, B2, ankieta treści | 14 |
| | **Oboje razem** | **29** |
| **Razem** | | **128 (widełki 105–150)** |

### Etap B: pakiet na pomiar

| Pozycja | h (H) |
|---|---|
| Echo bandy (raport, pula „Banda Pracowni”) | 7 |
| Kocioł świata | 2 |
| Spiżarnia-lite: zamówienie u Chochli, instancja, piętra, dopalacz 1 z 3, rekord, top 100 | 9 |
| Biblioteka do 6 + 6, strefa 2 z danych (4 gatunki, wariant Żarłoka), 4. gatunek strefy 1, modele | 15 |
| Sława ★ i brama strefy 2; warianty za wyczyn; Żarłok na Trudnym | 5 |
| Sklep: 2× Złoto, Zupa (paragony), Kostium | 6 |
| Rotacja „Gatunek tygodnia” z kalendarza | 2 |
| Game Director: garnek zamówień, okno Spiżarni, sklep, okno „Banda i Ekwipunek” w układzie rzędu bandy | 12 |
| Komiksowa okładka po Żarłoku (4 s, jedyny odcinek bez sterowania) | 4 |
| Kampania kohort: dwa okna reklamy dziennie, odczyt | 4 |
| **Razem** | **66 (widełki 50–85)** |

**Ile to trwa (W, z buforem 30%, czyli 70% deklarowanych godzin to praca):**

| Godzin na osobę tygodniowo | Etap A gotowy | Miękka premiera (B3) | Etap B gotowy | Kohorty decyzyjne |
|---|---|---|---|---|
| 20 | ok. 4,5 tygodnia → ok. 18.12 | 18.12 albo 8.01 | ok. 20.01 | od ok. 25.01 |
| 15 | ok. 6 tygodni + przerwa świąteczna → ok. 11.01 | ok. 15.01 | ok. 5.02 | od ok. 8.02 |
| 10 | ok. 9 tygodni → ok. 1.02 | luty | marzec | marzec |

**Uczciwie:** „MVP w 4 tygodnie” dotyczy Etapu A i jest realne tylko przy zmierzonych ≥ 20 h na osobę tygodniowo, a Karol niesie ok. 3/4 godzin technicznych. Dlatego: (1) Game Director przejmuje UI soku i Albumu po stronie klienta; (2) datę wybiera B0 z godzin ostatnich 2 tygodni, a potwierdza dziennik po B1.

**Kolejka cięć Etapu A** (oceny w §11 jej nie zakładają): lądowania z gagiem 3 → 1, Patelnia → po B, serwery prywatne → B, zbliżenie montażu tylko przy pierwszym gatunku. **Etapu B:** warianty za wyczyn 2 → 1 na gatunek, strefa 2 z 3 gatunkami zamiast 4, komiksowa okładka → po D7. **Nie tniemy:** soku, pierwszej minuty, echa, Spiżarni, telefonu.

**Bramki:**

| Bramka | Kiedy | Warunek |
|---|---|---|
| Dzień 0 | 13.11 | start werbunku testerów 16+ (formularz w 2–3 społecznościach twórców i na Discordzie); sprawdzić, czy testerzy prywatnej wersji muszą mieć sprawdzony wiek albo uprawnienia przez grupę (P-Z12); zakup lub pożyczenie telefonu z Androidem i 3 GB RAM |
| Makieta siatki | przed B1 | 12 kafelków: 8 z bieżącej topki i nowości, 3 z półki (Monster Maker, Catch a Monster, Evomon) i nasz; 3 permutacje na osobę; n ≥ 40 osób 16+ grających co tydzień. Zalicza: udział pierwszych wyborów ≥ 1,5 × oczekiwany (≥ 12,5% wobec 8,3%), ≥ 8/10 opisuje „co się robi” słowem „krzywo” albo „składa źle”, ≥ 6/10 mówi „to gra dla kogoś w moim wieku”, < 30% wskazuje konkretną grę (R-Z8, G-Z3, G-Z9) |
| B0 | 16–18.11 | 6 decyzji dnia 0 (§10), scalenie gałęzi z przenumerowaniem pytań, osobne miejsca robocze, dziennik godzin, data z godzin |
| Pomiar techniczny | ok. 23.11 | prywatne miejsce, 48 wrogów i 8 band jako boty, telefon 3 GB: ≥ 30 kl./s, opóźnienie BONK ≤ 150 ms. Porażka znaczy „naprawić”, nie „zmienić pętlę” |
| **B1** | **30.11** | szary prototyp, jedna strefa, natywna fizyka. Każdy z 6–8 obcych graczy 16+ gra A (BONK i Finał) i B (banda i auto-BONK) w losowej kolejności, dwie sesje dzień po dniu, a bot-klikacz gra A jako linia bazowa. **Miara główna (zapisana z góry):** dobrowolny czas gry, mediana stosunku A/B w parze. **Porażka tylko przy wyraźnym wyniku:** mediana A < B; mniej niż 3 z 8 gra A ponad 5 min bez zachęty; człowiek ÷ bot (klocki na minutę, minuty 3–10, front) < 1,1×. **Diagnoza, nie bramka:** człowiek ÷ bot (cel ≥ 1,3×), sok (cel: ≥ 5 z 8 śmieje się albo samo chwali uderzenie), druga sesja wobec pierwszej, liczba decyzji (BONK w innym kierunku niż autocel, Finał przy ≥ 5 wrogach), spadek BONK na minutę. Wynik 1,1–1,3× albo pęknięty sok: poprawka i powtórka za tydzień |
| B2 | ok. 2 tygodnie po B1 | kumpel ≤ 0:30, Album, Żarłok ≤ 10:00 na telefonie; testy zapisu (przeskok serwera, BindToClose) i exploitów zaliczone; 4. gatunek z samych danych ≤ 2 h; znaki towarowe tytułu sprawdzone |
| B3 | po B2, poza 20.12–3.01 | publiczna miękka premiera 16+: ankieta Mild, lejek, miniatura „katalogowa”. **Mierzy tylko lejek F0–F4 i odbicie < 60 s oraz 61–180 s. Bez decyzji „zakończyć”** (R-Z1) |
| Zamrożenie | 20.12–3.01 | bez nowych funkcji, dyżur poprawek z ustalonym dyżurnym (R-Z7) |
| B4 | dwie kolejne kohorty po Etapie B, nie wcześniej niż 11.01 | ≥ 400 nowych graczy tygodniowo w dwóch oknach reklamy po 2 h dziennie (W: wtedy ok. 3 graczy naraz; przy 240 tygodniowo tylko ok. 1,8). D1 osobno dla graczy z rekomendacji i z reklam. **Kohorta jest ważna tylko przy medianie ≥ 3 graczy naraz w oknach** |

**Progi po B4 (H):**
- **rozwijać:** D1 ≥ 10% i ≥ P50 panelu, mediana sesji ≥ 10 min, F3 ≥ 80%, człowiek ÷ bot ≥ 1,3×;
- **zmienić pętlę:** D1 7–10% albo sesja < 8 min (jedna poprawka w tydzień, druga porażka → wariant B jako główny czasownik);
- **zakończyć:** D1 < 7% w dwóch kolejnych **ważnych** kohortach.
- Dalej: D7 ≥ 3% w 3.–5. tygodniu po B4, D30 ≥ 1% i rosnące dni D8–28 po 8 tygodniach. Pierwszy nowy system dopiero po D7 ≥ 3%.

**Decyzja #13 przed B3:** jeśli w miękkiej premierze F3 ≥ 80% i odbicie ≤ P50, wpłacić przegląd przyspieszony 50 000 R$ (zwrotna kaucja; ok. 620 $ według W-retencja #9; dokumentacja i ogłoszenie z 16.06.2026 podają różne kwoty, sprawdzić). Wtedy kohorty decyzyjne zmierzą także 9–15. Przedtem kampania testowa za 50 $ z celem „Engagement”, żeby oszacować koszt progu 250 (R-Z13).

---

## 10. Zgodność z kanonem

Każdy wiersz z „ZMIANA” = **ZMIANA KANONU — wymaga decyzji Game Directora**.

**Sześć decyzji dnia 0** (reszta po makiecie siatki i B1), zgodnie z P-Z3 jako jedna strona tak/nie i 15-minutowy szary prototyp BONK do zagrania:
1. czasownik i fantazja v2.1 do prototypu;
2. **rdzeń bez statystyk postaci** (G-Z15), z mostami: grind statystyk → poziomy bandy i „Moc bandy”; „dzieci chcą cyferek” → liczby ×10 na strefę; plecak 8 slotów → bronie BONK-a i kosmetyka w oknie Bandy; 20 graczy → 8 z próbą 12;
3. najpierw publiczność 16+, kalendarz z miękką premierą i decyzją na kohortach styczniowych lub późniejszych;
4. waluty Złoto i Kryształy, bez waluty za R$;
5. Karczma bez alkoholu: „Zupa u Chochli”, kociołek zamiast kufla;
6. dwa tory pracy z dziennikiem godzin, zamrożeniem narzędzi i datą wynikającą z godzin.

| Element | Zostaje / zmienia się | Dlaczego | Rozstrzyga |
|---|---|---|---|
| D-001 prefiks | ZMIANA: cechy stylu („chunky voxel, 4 px black ink outlines, halftone, saturated”) bez cudzej nazwy | nazwa inspiracji to zarejestrowany znak słowny (**F**) | konflikt 2 |
| D-002 / D-018 | ZMIANA → D-002 v2: komiks i klocki zostają; UI „bubbly” z tuszowym obrysem; pixel-art tylko w pieczątkach Albumu; miniatury okresu próbnego w stylu „katalogu montażu” (tusz, raster) | wdrożone grafiki, „distinct visuals” dla 16+ (**F**, newsroom 30.04.2026) | #10, konflikt 3 |
| D-003 | wygląd zostaje; imiona Blocky i Crycket; ZMIANA ról: gracz gra awatarem R15, Crycket to kot przy graczu i NPC szef Pracowni, Blocky to strażnik placu | DevEx 18+ bez R6 (**F**); logo dostaje sens | #1 |
| D-004 | zostaje; ZMIANA interpretacji: instancjonowany mini-dungeon = Spiżarnia z zamówienia u Chochli; strefy wspólne | aktywna gra; kanon Karczmy | #7 |
| D-005 | ZMIANA kolejności: tor Karola zaczyna od pętli; tor Game Directora robi UI pod pętlę; okno ekwipunku przerabiane (rama i plecak zostają, środek jako rząd bandy, 3 sloty z 8, karty statystyk ukryte, nie usunięte; `StatPoints` usunięty przed publikacją) | najmniejsza strata pracy Game Directora (P-Z3); układ inny niż w grze-inspiracji (R-Z9) | #5 |
| Koncepcja i Core Loop | ZMIANA: definicja przez zdanie fantazji, bez odwołania do inspiracji; Tycoon i statystyki RPG odsunięte | P1 | — |
| Karczma | ZMIANA: „Zupa u Chochli” (EN „Ladle's Soup Shack”); zamiast tablicy 3 kart garnek, z którego wypływają 1–3 zamówienia w bańkach, bez czasu trwania; teleport do instancji zostaje (Spiżarnia); beczka → Słojak; bez Energii (D-009) | alkohol tylko 18+ (**F**); własny układ (R-Z9) | #8, konflikt 1 |
| Twierdza | ZMIANA: Pracownia-lite w miesiącu 2, pełna działka po D7 | zakres (P-Z1) | #9 |
| Pety | ZMIANA: pokonane potwory stają się towarzyszami; jaja wykluwane walkami (Kisiel) po D7; ekspedycje → echo bandy | aktywność, gra przy pustym serwerze | — |
| HUD | ZMIANA: BONK jako duży przycisk, Klej zamiast Many, Moc bandy; zakładki odsłaniane z systemami (Banda, Album, Zupa u Chochli z kociołkiem; Pracownia i Arena później); bez kufla, Teleportu i Gildii | — | #5, konflikt 4 |
| Waluty | ZMIANA: Diamenty → Kryształy; brak waluty za R$ | — | #6, konflikt 5 |
| Ekran ładowania | scena i logo zostają; bez wymuszonych 5,8 s; żarty o kuflu i grzybach do wymiany | P3 | — |
| Propozycje D-013…D-018 | D-013: walka od razu tak, cutscenka tylko jako okładka po bossie. D-014: bramki z percentylami na ważnych kohortach. D-015 v2: zero losu (także darmowego) i waluty za R$. D-016: 8 graczy. D-017 zostaje | §2, §7, §9 | #7, #12 |
| Rozmowa 12.11 (propozycje Game Directora) | odsunięte: hub-miasteczko z mapą, auto-walka, sklep z tokenami, koło, statystyki gra-inspiracja, gildie, wierzchowce | §1 anty-cele, P2, P7, P8 | decyzja 2 dnia 0 |
| Praca tej nocy poza v2.1 | Krzywe Miasteczko (z kołem fortuny i stajnią), cutscenka auto-walki `TestWalki` | P-Z11 | Karol i Game Director |

---

## 11. Karta ocen (po czerwonym zespole)

Oceniam wersję, która trafi do pomiaru (Etap A + Etap B), bez pozycji z kolejki cięć, przy domyślnej mocy 15 h na osobę tygodniowo (brief: 10–20 h). Trzy raporty czerwonego zespołu oceniły v2 na 5,3, 5,9 i 5,6, a swoje naprawy na ok. 6,5, 6,7 i 6,1. Moje oceny leżą przy dolnej krawędzi tych szacunków, bo tamte zakładały, że każda naprawa się uda, a ja liczę wersję z datą wynikającą z godzin.

| K | Dziś | v2 (autor) | Czerwony (średnia) | **v2.1** | Dlaczego tyle | Pomiar, który potwierdzi albo obali |
|---|---|---|---|---|---|---|
| K1 Haczyk | 3 | 7 | 5,7 | **6** | tytuł i ikona z błędem montażu, ironia w obrazie; półka zajęta, nic nie zmierzone | makieta siatki (§9); kampania 10 miniatur po B3; wejścia ≥ P75 |
| K2 Pierwsze 10 min | 4 | 8 | 6,3 | **7** | lokalna pierwsza minuta, sok z godzinami, okno 61–180 s naprawione; telefon niezmierzony, brak dochodu/s | F1 ≥ 90%, F3 ≥ 80%, F4 ≥ 70%; odbicie ≥ P50; sesja ≥ 10 min |
| K3 Rdzeń | 3 | 7 | 6,0 | **6** | hałas wabi, Finał z kosztem, stopnie zmieniają zdolności; frajda niesprawdzona | B1 (§9); po publikacji sesja D7 ≥ D1, ≥ 2 sesje dziennie |
| K4 Postęp | 4 | 8 | 5,7 | **6** | 2 strefy, Spiżarnia, wyczyny; gracz 45 min dziennie kończy Album w 5. dniu, prestiż po D7 | symulacja §3; D7 ≥ 3%, D30 ≥ 1%; ≥ 50% graczy z D7 rośnie na ≥ 2 drabinach |
| K5 Powroty | 5 | 7 | 5,7 | **6** | uczciwe powody bez zegarów straty; „moje” słabsze bez Pracowni | D1 ≥ 10% i ≥ P50 w ważnej kohorcie; dni D2–7 rosną |
| K6 Społeczność | 3 | 8 | 5,0 | **5** | echa i Kocioł świata działają solo, ale przy 0,3–3 graczach naraz warstwa społeczna jest cienka, a twórcy zablokowani do Select | progi warunkowe z §6 |
| K7 Monetyzacja | 4 | 7 | 5,3 | **6** | odporność wzorowa, potencjał niski z wyboru; mierzalne od ≥ 2000 graczy | cele z §7 |
| K8 Tożsamość | 4 | 8 | 6,3 | **7** | Crycket i krzywy montaż jako jedyny wyróżnik półki, własne układy ekranów | < 10% kojarzy z inną grą; ≥ 50% nazywa maskotkę; ≥ 50% klipów z Crycketem |
| K9 Wykonalność | 4 | 6 | 4,3 | **5** | Etap A ok. 128 h, Etap B ok. 66 h; 4 tygodnie tylko przy ≥ 20 h; przy 15 h kohorty od lutego | dziennik godzin; bramki ±3 dni; godziny ≤ +20% planu |
| K10 Live-ops | 4 | 8 | 5,7 | **6** | biblioteka zachowań, rotacja z kalendarza, limit godzin; próba generalna niezrobiona | gatunek z danych ≤ 2 h; live-ops ≤ 10 h tygodniowo do 100 DAU |

**Średnia v2.1: 6,0. Minimum: 5 (K6, K9).** Względem v2 karta spada o 1,4 pkt, a względem stanu dzisiejszego (3,8) rośnie o 2,2.

**Gdzie leży sufit papieru.** K6 i K9 ograniczają ruch i moc zespołu, a nie projekt. K6 podniesie dopiero gęstość (≥ 3 graczy naraz organicznie) i wejście do Select. K9 podniesie dziennik godzin z ≥ 20 h na osobę i dotrzymane B1. K1, K3 i K5 rozstrzyga pomiar. Dziewiątki i dziesiątki da się wpisać dopiero po B1, makiecie siatki i ważnych kohortach.

**Najtańsze testy, które rozstrzygną najwięcej:**
1. makieta siatki z prawdziwą konkurencją (K1, K8): ok. 3 h pracy, przed B1;
2. szary prototyp z botem-klikaczem (K3): jeśli człowiek nie bije bota o ≥ 1,1×, rdzeń nie przekroczy 5, cokolwiek dopiszemy;
3. symulacja premiery z jedną i dwiema strefami (K4): zrobiona tej nocy, wynik w §3.

---

## 12. Zarzuty czerwonego zespołu i odpowiedzi

Werdykty: **przyjęty** (naprawa jak w zarzucie), **przyjęty z korektą** (naprawa zmieniona, powód w kolumnie), **częściowo** (część naprawy odrzucona z powodem), **odrzucony**. Zarzuty o wadze 2 są na końcu w skrócie.

### Gracz (`czerwony_gracz.md`)

| Nr | Zarzut | Waga | Werdykt | Co zmieniono albo dlaczego nie |
|---|---|---|---|---|
| G-Z1 | jedna strefa na premierę, pusto po tygodniu | 5 | przyjęty z korektą | Spiżarnia-lite i strefa 2 w Etapie B, przed pomiarem, a nie w MVP-4 (koszt); pomiar dopiero po Etapie B; §3 przeliczony dla 1 i 2 stref (§3, §4, §9). Nie zgadzam się z R-Z12 i P-Z7, że Spiżarnia może czekać do miesiąca 2: bez niej gracz 45 min dziennie kończy grę w 5. dniu, a Spiżarnia jest kanonicznym mini-dungeonem z D-004 |
| G-Z2 | budżet spawnu odcina umiejętność od postępu | 5 | przyjęty | hałas wabi i stada 4–8 (§2) |
| G-Z3 | warstwa 16+ w połowie fasadą | 4 | przyjęty | zbliżenie montażu, top 100 Spiżarni z wyłącznikiem, pytanie o wiek w makiecie, miniatura „instrukcja montażu” (§1, §2, §9) |
| G-Z4 | detektor autopilota liczy wciśnięcia | 4 | przyjęty z korektą | bot-klikacz jako linia bazowa; porażka dopiero < 1,1×, cel ≥ 1,3×, bo przy n = 6–8 sztywny próg 1,3× oblewałby dobrą grę (symulacja P-Z2) (§9) |
| G-Z5 | sok bez godzin | 4 | przyjęty z korektą | blok 16 h + 3 h UI (dolna granica widełek 20–30 h, bo natywna fizyka zdejmuje własne przewidywanie lotu); bramka soku jako diagnoza w B1, pęknięta = poprawka i powtórka; sok poza kolejką cięć (§2, §9) |
| G-Z6 | Finał rozwiązany, nagroda dwuznaczna | 3 | przyjęty | mnożnik z łańcucha, klocki stałe, opadanie Kleju, kierunek upadku (§2) |
| G-Z7 | „Prosty” prostuje żart | 3 | przyjęty | Krzywy → Bardziej Krzywy → Arcydzieło, każdy stopień dokłada błąd i moc (§5) |
| G-Z8 | banda na 3 miejsca w gatunku „armii” | 3 | częściowo | nie gonimy armii, bo to zajęta obietnica (R-Z3); wyróżnikiem jest krzywizna. „Cała Banda!” i kolekcja przy Pracowni dopiero w miesiącu 2 jako kosmetyka Finału (anty-cel w §1) |
| G-Z9 | tytuł na zajętej półce, ikona niezaprojektowana | 3 | przyjęty | nowe zasady tytułu, trzy szkice ikony, pytanie „z jaką grą się kojarzy” (§1, §9) |
| G-Z10 | kolekcja deterministyczna bez rzadkości | 3 | przyjęty | warianty za wyczyn zastępują Lśniącego (§4, §5) |
| G-Z11 | serwer na 8 osób bez widowni | 3 | przyjęty z korektą | echa, PODANIE z naprowadzaniem, progi warunkowe. Korekta rachunku: dwa okna po 2 h przy 240 nowych tygodniowo dają ok. 1,8 gracza naraz, a nie 3–4 (34 dziennie × 13 min ÷ 240 min); 3 naraz wymaga ok. 400 nowych tygodniowo (§6, §9) |
| G-Z12 | cztery systemy w święta | 3 | przyjęty | zamrożenie 20.12–3.01, nowe systemy dopiero po D7, rotacja z kalendarza zamiast ręcznych wydarzeń (§8, §9) |
| G-Z13 | „treść z danych” w połowie kodem | 3 | przyjęty | biblioteka zachowań, próba generalna jako bramka B2 (§8) |
| G-Z14 | okno 61–180 s: frustracja i menu | 3 | przyjęty | Tarczak po Finale, KLONK ≤ 1 s, autocel z krążkiem, Album pulsuje, Żarłok przychodzi do gracza (§3) |
| G-Z15 | rdzeń odwraca wizję Game Directora | 3 | przyjęty | szósta decyzja dnia 0 i tabela mostów, liczby ×10 na strefę (§10) |
| G-Z16 | słabe produkty, myląca etykieta | 3 | częściowo | uczciwy napis, 199 R$, Zupa z zabawnym efektem dla wszystkich, Kostium w B. **Odrzucam opcjonalny podpis przy Zupie:** widoczne imię płacącego tworzy presję na dzieci, które nie płacą, a wspólny efekt i tak daje radość (§7) |

### Rynek (`czerwony_rynek.md`)

| Nr | Zarzut | Waga | Werdykt | Co zmieniono albo dlaczego nie |
|---|---|---|---|---|
| R-Z1 | śmierć w okresie próbnym: kohorta, pusty serwer, święta, „zakończyć” | 5 | przyjęty | miękka premiera bez „zakończyć”, ważne kohorty z warunkiem gęstości, D1 według źródła, warunkowy przegląd przyspieszony (§9) |
| R-Z2 | filary 3 i 4 bez ludzi | 4 | przyjęty z korektą | echo w Etapie B (nie w MVP-4, bo B3 mierzy tylko lejek), nagroda echa bez waluty do czasu skrzynki (P-Z13), Kocioł świata bez przedmiotów dnia, plac skalowany, progi warunkowe (§1, §6) |
| R-Z3 | udowodniona fantazja to przetrzebiona półka | 4 | częściowo | akcent na krzywy montaż, ikona z montażem, zakaz słów, plan na klona. **Zapas treści mniejszy niż „6 tygodni danych”:** 8 gatunków na pomiar i paczka co 3–4 tygodnie, bo większy zapas łamie budżet godzin (P-Z1, P-Z7) |
| R-Z4 | 16+ dostaje grę, która wygląda na dziecięcą | 4 | przyjęty | ironia w obrazie, miniatura „katalogowa”, wynik makiety osobno 16–17 i 18+, kampania 10 miniatur (§1, §9) |
| R-Z5 | katalog sprzedaje obecność, rachunek na starej liczbie | 4 | przyjęty z korektą | produkty solo (Kostium widoczny na echach i w Albumie), Zupa działa solo, 2× za 199 R$ z uczciwym napisem, bramka jako percentyl, niski sufit wprost. Album Deluxe przesunięty po D7, a sklep do Etapu B, bo w miękkiej premierze nic nie zmierzy (P-Z15) (§7) |
| R-Z6 | twórców blokuje bramka wieku | 4 | przyjęty | zero pracy z twórcami przed Select, 2 klipy tygodniowo w budżecie, „Zapisz klip” po sprawdzeniu możliwości CaptureService (§6) |
| R-Z7 | grudzień | 3 | przyjęty | zamrożenie 20.12–3.01, bez wydarzeń z „Notify me” do progów (§8, §9) |
| R-Z8 | test kart to szum i porównanie rodzeństwa | 3 | przyjęty | makieta siatki z n ≥ 40 i konkurencją z półki (§9) |
| R-Z9 | karczma z 3 kartami i okno ekwipunku jak w inspiracji | 3 | przyjęty | garnek zamówień, rząd bandy w oknie, prywatne repozytorium i dziennik pochodzenia ekranów jako decyzje Game Directora (§10) |
| R-Z12 | live-ops bez zapasu, 5–6 systemów w 6 tygodni | 3 | przyjęty z korektą | strefa 2 przed pomiarem, rytm z rotacji, K10 = 6 do próby generalnej. Spiżarnia zostaje w Etapie B (zob. G-Z1) |

### Produkcja (`czerwony_produkcja.md`)

| Nr | Zarzut | Waga | Werdykt | Co zmieniono albo dlaczego nie |
|---|---|---|---|---|
| P-Z1 | 24–28 mechanik, godziny ×2–3 | 5 | przyjęty z korektą | MVP-4 jako baza Etapu A, ale z blokiem soku, botem i hałasem wabi, które dokładają godziny (128 h zamiast 113); Etap B osobno (66 h); daty z tabeli mocy (§9) |
| P-Z2 | B1 23.11 niewykonalne, bramka oblewa dobrą grę | 5 | przyjęty | B1 30.11, układ wewnątrzosobowy, jedna miara główna, porażka tylko przy wyraźnym wyniku, technika osobno (§9) |
| P-Z3 | decyzje dnia 0 sprzeczne ze świeżą pracą Game Directora | 5 | przyjęty | jedna strona i prototyp do zagrania, plan użycia okna ekwipunku, mapa teleportu jako propozycja po D7 (§10) |
| P-Z4 | najdroższa architektura sieci przed pomiarem | 4 | przyjęty | natywna replikacja; własna tylko po pomiarze (§2) |
| P-Z5 | pierwsza minuta jako nieliczony system | 4 | przyjęty | lokalni aktorzy, osobny wiersz godzin, 5 pojęć w 10 min (§3, §9) |
| P-Z6 | treść jako dane nie obejmuje gatunków i bossów | 4 | przyjęty | biblioteka 6 + 6, boss jako sekwencja (§8) |
| P-Z7 | kalendarz po premierze w święta | 5 | przyjęty | systemy po D7, limit ≤ 10 h tygodniowo do 100 DAU, bez cotygodniowych wydarzeń z „Notify me” (§8) |
| P-Z8 | oceny K4–K7, K10 stoją na rzeczach spoza MVP | 4 | przyjęty | karta dla wersji do pomiaru, bez kolejki cięć; Sława wraca dopiero z drugą strefą (§11) |
| P-Z9 | PODANIE i osobny budżet się wykluczają | 3 | przyjęty | wspólni wrogowie, łup w limicie, PODANIE +1 klocek (§2) |
| P-Z10 | telefon bez urządzenia i pomiaru | 4 | przyjęty | telefon w dniu 0, pomiar z botami ok. 23.11, Miasteczko poza MVP (§9) |
| P-Z11 | grawitacja narzędzi | 4 | przyjęty | zasady pracy w §9 do zatwierdzenia w B0 |
| P-Z12 | rekrutacja testerów na ścieżce krytycznej | 3 | przyjęty | werbunek od dnia 0, sprawdzenie dostępu dla testerów, n ≥ 40 w makiecie (§9) |
| P-Z13 | zapis i cudze profile | 3 | przyjęty | schemat z wersją, skrzynka tylko dopisywana, brak ekonomii między graczami w MVP (§6, §9) |
| P-Z14 | jedna osoba wąskim gardłem | 3 | przyjęty | humor w obrazie, ≤ 20 linii tekstu, recenzent angielskiego z testerów B1, akceptacje paczką raz w tygodniu (§1, §8) |

### Waga 2, w skrócie

- **G-Z17** (paczki ponad 1000 B): rozwiązany natywną replikacją (§2).
- **G-Z18** (karta przy wyjściu niewykonalna): przyjęty, pasek „Na jutro” w przerwach (§3).
- **G-Z19** (osiem klonów maskotki): przyjęty jako decyzja ról (§1, §10).
- **R-Z10** („Monster” w tytule): przyjęty (§1).
- **R-Z11** („tavern” i beczki): przyjęty, „Ladle's Soup Shack” i Słojak (§1, §10).
- **R-Z13** (koszt progu 250): przyjęty, kampania testowa za 50 $ (§9).
- **R-Z14** (limit 72 h wypoczynku, Karta Bywalca): przyjęty, wypoczynek neutralny czasowo (§5).
- **P-Z15** (sklep w MVP nic nie zmierzy): przyjęty dla miękkiej premiery, odrzucony dla pomiaru, bo dni z wydatkami są sygnałem dystrybucji od 20.08.2026 (**F**) (§7).
- **P-Z16** (publiczne repozytorium): przyjęty jako decyzja #14 przed pierwszym commitem pętli (§10).

**Gdzie czerwony zespół się mylił albo się różnił** (rozstrzygnięcia redaktora):
1. Spiżarnia: gracz chce ją w MVP, rynek i produkcja w miesiącu 2. Rozstrzygam: w Etapie B, przed pomiarem (G-Z1).
2. Rachunek „3–4 graczy naraz” przy 240 nowych tygodniowo jest zawyżony około dwa razy (G-Z11).
3. Próg bota 1,3× jako warunek porażki przy n = 6–8 jest za ostry (G-Z4).
4. Zapas „6 tygodni danych” przed premierą nie mieści się w godzinach (R-Z3).
5. Podpis przy Zupie, nawet opcjonalny, jest sprzeczny z czerwoną linią (G-Z16).
6. Sklep jest potrzebny w wersji do pomiaru, choć nie w miękkiej premierze (P-Z15).

## Powiązane
[[Myśl przewodnia v2]] · [[Systemy gry v2]] · [[Psychologia gracza v2]] · [[Karta ocen v2 i plan sprawdzenia]] · [[Diagnoza pomysłu 2026-11-13]] · [[Rejestr decyzji]] · [[Pytania otwarte]]
