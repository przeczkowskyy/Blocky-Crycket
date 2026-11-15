---
status: propozycja
tags: [gra, mechanika, progresja, drzewko, monetyzacja]
źródło: "pytanie Pawła w panelu 2026-11-14 („jak rozplanować skill tree postaci”); decyzje D-035, D-038, D-039, D-040; [[Shakes & Fidget — rozbiór mechanik]]"
---
# Drzewko umiejętności postaci

> [!info] W skrócie
> Odpowiedź na pytanie Pawła z 14.11: jak rozplanować skill tree postaci. Drzewko to **trzecia warstwa siły** obok statystyk i ekwipunku — daje premie procentowe i wygodę, nie surowe liczby. Kształt: **trzy gałęzie (Walka, Wyprawa, Fortuna) i wspólny pień**, **pięć pięter otwieranych poziomem postaci**, każdy węzeł w trzech rangach: **pierwszą kupuje punkt talentu (jeden co poziom), drugą i trzecią Diamenty**. Pieniądze przyspieszają, ale nie przeskakują pięter. Jedno drzewko dla wszystkich klas na premierę. To **propozycja** (D-047) rozwijająca zatwierdzoną D-039; nic tu nie jest kanonem.

## 1. Po co drzewko i czym się różni od statystyk

Postać ma mieć trzy warstwy siły. Każda ma inne źródło i inne okno, żeby gracz wiedział, „gdzie co się kupuje”.

| Warstwa | Skąd | Co daje | Gdzie w UI |
|---|---|---|---|
| **Statystyki** (Siła, Kondycja, Inteligencja, Zręczność, Szczęście, Pancerz) | punkty za poziom i dokupywanie za Złoto (wzór z S&F, rozmowa 12.11) | surowe liczby do wzorów walki | [[Okno ekwipunku]], zakładka ATTRIBUTES, przycisk „+” |
| **Ekwipunek** | sklepy, łup, dungeony | główne źródło statystyk | [[Okno ekwipunku]] |
| **Drzewko** | punkty talentu (poziom) i Diamenty (D-038, D-039) | stałe **premie procentowe** (EXP, Złoto, obrażenia, szczęście), **wygoda** (sloty, odbieranie nagród) i **smaczki** (cios specjalny w cutscence) | nowa zakładka TALENTS albo osobne okno (§6) |

**Zasada:** drzewko **mnoży** to, co gracz już ma, a nie zastępuje przedmiotów. Płacący nie wygra „z niczego” — nadal musi zdobywać poziomy, statystyki i ekwipunek. To realizuje „trochę pay-to-win, ale nie za bardzo” Karola (D-036) i próg progresji z D-035 (gry nie da się zmaksować w dwa dni).

Prędkość ruchu w drzewku nie występuje — Karol uznał ją za nieistotną (D-039).

## 2. Kształt: trzy gałęzie, pień, pięć pięter

Nie robimy wielkiej pajęczyny węzłów (styl Path of Exile): gra jest na telefon i dla każdego wieku, a balansują ją dwie osoby. Zamiast tego **trzy pionowe gałęzie i pień**, czytelne na ekranie telefonu w trzech kolumnach.

```
poziom 60 │ piętro 5 │ ⚔️ ○ ○      🗺️ ○ ○      🍀 ○ ○    │ 🌳 ○
poziom 40 │ piętro 4 │ ⚔️ ○ ○ ○    🗺️ ○ ○ ○    🍀 ○ ○ ○  │ 🌳 ○
poziom 25 │ piętro 3 │ ⚔️ ○ ○ ○    🗺️ ○ ○ ○    🍀 ○ ○ ○  │ 🌳 ○
poziom 10 │ piętro 2 │ ⚔️ ○ ○ ○    🗺️ ○ ○ ○    🍀 ○ ○ ○  │ 🌳 ○
poziom 1  │ piętro 1 │ ⚔️ ○ ○ ○    🗺️ ○ ○ ○    🍀 ○ ○ ○  │ 🌳 ○
                       Walka       Wyprawa     Fortuna      Pień
```

| Gałąź | O czym | Przykładowe węzły (nazwy robocze, po polsku; w grze angielskie z tłumaczeniem, D-045) |
|---|---|---|
| ⚔️ **Walka** | siła w walce 3D (serwer liczy, D-016; długość walki z losowości i statystyk, D-033) | „Gruba skóra” (+% HP) · „Cios z zamachu” (+% obrażeń) · „Oko sokoła” (+szansa krytyka) · „Twarda głowa” (mniej obrażeń od krytyków) · „Jeszcze stoję” (raz na walkę cios śmiertelny zostawia 1 HP) · piętro 5: **cios specjalny** widoczny w cutscence |
| 🗺️ **Wyprawa** | karczma, strefy, dungeony | „Bystry uczeń” (+% EXP — pomysł Pawła) · „Krótsza droga” (−% czasu zadania z karczmy) · „Głęboka kieszeń” (+% Złota z zadań) · „Nos do skarbów” (lepszy łup z dungeonów) · „Gęsty las” (potwory w strefie odradzają się szybciej) |
| 🍀 **Fortuna** | szczęście i handel | „Szczęśliwa skarpeta” (większe szczęście do rolek — pomysł Pawła) · „Targowanie” (−% cen w sklepach) · „Stały klient” (sklep pokazuje jeden przedmiot więcej) · „Dodatkowy rzut” (+1 darmowy rzut dziennie u mistrza gier planszowych) · „Ciepłe gniazdo” (jajka petów wykluwają się szybciej) |
| 🌳 **Pień** (jeden węzeł na piętro, wspólny) | wygoda | „Większy plecak” (+5 slotów) · „Druga mikstura” (drugi slot mikstury) · „Hurtownik” (odbiór wszystkich nagród jednym stuknięciem) · „Dwa zadania” (drugie równoległe zadanie karczmy — tylko jeśli zostaną zadania na czas z D-034) |

**Piętra.** Piętro otwiera **poziom postaci** (robocze: 1 / 10 / 25 / 40 / 60 — las od początku, biom kryształowy wyżej, D-032) **oraz** co najmniej dwa wykupione węzły piętra niżej w tej samej gałęzi. Dzięki temu Diamenty nie przeskakują pięter: płacący ma pełniejsze niższe piętra, ale na piętro 5 wchodzi tym samym poziomem co wszyscy.

**Rangi.** Każdy węzeł ma trzy rangi (★☆☆ → ★★★), np. +3% / +6% / +10%. Trzy rangi dają więcej decyzji niż jeden przełącznik i wyraźnie rosnące liczby, które gatunek lubi.

## 3. Za co kupujemy węzły: „punkt otwiera, Diamenty pogłębiają”

D-039 mówi „drzewka za Diamenty”. Proponuję dołożyć **darmową ścieżkę**, żeby gracz, który nie płaci, też czuł, że drzewko jest jego:

| Ranga | Koszt | Kto to zdobywa |
|---|---|---|
| ★ pierwsza | **1 punkt talentu** (1 punkt za każdy poziom postaci) | każdy, samym graniem |
| ★★ druga | Diamenty (robocze: 25 / 50 / 100 / 200 / 400 za piętra 1–5) | Diamenty z gry (bossowie, pierwsze zadanie dnia, kamienie milowe — D-031) albo za Robuxy |
| ★★★ trzecia | Diamenty (robocze: 50 / 100 / 200 / 400 / 800) | jak wyżej |

Rachunek roboczy: 10 węzłów na piętro × 5 pięter = 50 węzłów. Pierwsze rangi wszystkich węzłów kupi gracz na ok. 50.–60. poziomie (50 punktów), więc **szerokość** drzewka jest darmowa, a **głębia** (rangi 2–3, razem ok. 23 000 Diamentów za całość) jest ujściem Diamentów na długie miesiące. Liczby są hipotezą do kalkulatora balansu — trzeba je zestawić z tempem zdobywania Diamentów w grze, które jeszcze nie istnieje (pytanie 9 o Twierdzę, D-031).

**Test uczciwości (do zapisania przed balansem):** gracz niepłacący ma mieć co kilka poziomów coś do kliknięcia w drzewku; płacący ma być silniejszy o mnożnik, nie o piętro.

**Chrupki** (trzecia waluta, D-040, D-046): Karol dopuścił, że „waluta game passowa może być wykorzystana do innych zakupów ulepszających”. Na premierę proponuję **nie** mieszać trzeciej waluty w drzewko (dwa portfele na jednym ekranie to za dużo na telefonie); do rozważenia później jako wymiana Chrupki → Diamenty.

## 4. Przestawienie (reset)

Pierwsze przestawienie drzewka darmowe, każde kolejne za Złoto (cena rośnie z poziomem). Wydane punkty i Diamenty **nie przepadają**: wracają jako pula do ponownego rozdania w drzewku, nie jako waluta. Dzięki temu gracz śmiało próbuje gałęzi, a Diamenty nie wyciekają z drzewka z powrotem do sklepu.

## 5. Klasy: jedno drzewko czy osobne

[[Selektor bohatera]] (propozycja) daje wybór rasy i klasy; [[Rycerz]] (miecz) i [[Kot-Mag]] (różdżka) to dwa archetypy, które pojawiły się też w D-033 („prosta animacja zamachu: miecz, różdżka”).

| Wariant | Co to znaczy | Koszt | Kiedy |
|---|---|---|---|
| **(A) Jedno wspólne drzewko** + jedna stała cecha klasy na start (np. Rycerz: szansa bloku tarczą; Kot-Mag: zaklęcia omijają część pancerza) i inne ikony węzłów Walki na klasę | jedna tabela, jeden balans, jedno okno | najniższy | **rekomendacja na premierę** |
| (B) Osobne drzewko na klasę | 2–3 razy więcej węzłów do zbalansowania, osobne okna | wysoki | aktualizacja po premierze, gdy klasy się potwierdzą |

Cecha klasy to własne liczby i nazwy — mechanik S&F nie chroni prawo autorskie, ale nazw, wartości ani ekranów nie kopiujemy ([[Shakes & Fidget — rozbiór mechanik]], „Granica inspiracji”).

**Cios specjalny (smaczek, pomysł).** Najwyższy węzeł gałęzi Walka odblokowuje cios widoczny w cutscence walki (D-033): Rycerz — „Młot z nieba”, Kot-Mag — „Rybia kula”. Nie zmienia wzoru walki ponad premię węzła; to nagroda do pokazania innym i do nagrania.

## 6. Okno

- **Rekomendacja na premierę:** zakładka **TALENTS** w [[Okno ekwipunku]] zamiast jednej z nieobsadzonych zakładek (DESCRIPTION / INFO / INTERACTIONS mają dziś pustą treść). Portret i poziom zostają po lewej, trzy kolumny gałęzi i rząd pnia po prawej.
- **Alternatywa:** osobne okno z HUD, gdy przycisków HUD będzie więcej (pytanie 5).
- Styl: „Krzywe Drzewko” — pochylone, komiksowe drzewo z ciemną kreską jak w [[Klocki — Blender i Roblox|Krzywym Miasteczku]] (D-041); węzły jako okrągłe pieczątki, kupiony w pełnym kolorze, zamknięty jako sylwetka „???” z poziomem, który go otwiera (gracz widzi, po co wraca).
- Telefon: cele dotyku co najmniej 44 pt; stuknięcie w węzeł otwiera kartę z opisem, kosztem i jednym przyciskiem „Kup za 1 punkt” albo „Kup za 50 ◆” (cena zawsze na przycisku, D-031).
- Napisy natywnie, po angielsku z tłumaczeniem (D-011, D-045).

## 7. Technika (szkic)

- **Dane, nie kod:** jedna tabela w `ReplicatedStorage.Shared` (np. `Talenty`): `{ id, galaz, pietro, nazwa, opis, efekt = { typ, wartosci = {r1, r2, r3} }, kosztDiamenty = {r2, r3} }`. Nowy węzeł to nowy wiersz.
- **Serwer liczy wszystko:** jedno zdarzenie `KupTalent(id)` ze sprawdzeniem poziomu, piętra, dwu węzłów niżej, waluty i odstępu czasu przed spamem (jak w istniejącym `StatPoints.server.luau`); zapis w profilu gracza jako `talenty = { [id] = ranga }`.
- **Jeden moduł mnożników:** po każdym zakupie serwer przelicza sumy premii i ustawia je jako atrybuty gracza (`MnoznikEXP`, `MnoznikZlota`, `SzansaKrytyka`…), które czytają walka (D-016), karczma (czas, nagrody), sklep (ceny, szanse) i pety. Klient tylko wyświetla.
- **Zgodność z zasadami Roblox:** jeśli rolki, koło albo jajka będzie się kupować za Diamenty lub Robuxy (D-037 nierozstrzygnięta, pytanie 30), węzły Fortuny zmieniające szanse to „modyfikatory prawdopodobieństwa” — panel szans przed zakupem musi pokazywać szanse **po** premii z drzewka ([[Retencja i monetyzacja — co wolno i co działa]]).

## 8. Co to zmienia w sejfie

- **Rozwija D-039 ✅** (drzewko postaci za Diamenty): dokłada punkty talentu jako darmową ścieżkę — to wymaga zgody (D-047, pytanie 34).
- **Zgodne z** D-015 (nic losowego za Diamenty), D-031 i D-038 (Diamenty premium), D-035 (próg progresji), D-036 („trochę pay-to-win”).
- **Osobno, później:** drzewka petów za Łapki (D-039, D-040 — temat Pawła w [[Sesje główne]]) i drzewko Twierdzy (pytanie 9). Ta notatka ich nie projektuje. Trzecia sesja 14.11: drzewko każdego peta odpada — jedno ogólne drzewko petów i drzewko Twierdzy jako mnożniki procentowe (propozycja D-056).
- Statystyki za punkty i Złoto to nadal propozycja (pytanie 17); drzewko zakłada, że zostają.

## Do ustalenia
- Jedno wspólne drzewko czy osobne dla klas (§5) — pytanie 34, D-047. **Druga sesja 14.11 (D-055):** Karol — osobne drzewko na klasę; klasy Wojownik, Zwiadowca, Mag ze specjalizacjami jako rozgałęzienia (D-054, pytanie 35); węzły procentowe plus **umiejętności aktywne** z 0–3 slotami odblokowywanymi w drzewku; jedno okno z sekcjami (gracz, pety, karczma, Twierdza) koło zakładki ekwipunku; za co kupuje się węzły — nie padło. Zob. [[Sesja główna 2026-11-14 (2) — zapis ustaleń]].
- Punkty talentu obok Diamentów czy tylko Diamenty (§3) — D-047. **Rozstrzygnięte 14.11:** D-047 odrzucona z dwoma podpisami (Karol: „płacimy jedynie Diamentami za drzewko”), D-055 zatwierdzona — drzewko na klasę; trzecia sesja: węzły za Gemy, bez punktów talentu, a poziom daje punkty statystyk, sklep i strefy (propozycja D-057); okno z trzema sekcjami gracz / pety / Twierdza, bez karczmy (D-056). Gałęzie i piętra z tej notatki trzeba przeprojektować pod drzewko na klasę. Zob. [[Sesja główna 2026-11-14 (3) — zapis ustaleń]].
- Pełna lista węzłów i liczby → kalkulator balansu (okno **Balans** agenta w panelu, zlecenie Karola z 14.11 w [[Zadania]]); do tego tempo zdobywania Diamentów w grze.
- Zakładka w [[Okno ekwipunku]] czy osobne okno (§6).
- Czy Chrupki (D-040) kiedykolwiek kupują węzły.

## Powiązane
[[System RPG]] · [[Okno drzewka umiejętności]] · [[Okno ekwipunku]] · [[Selektor bohatera]] · [[Rycerz]] · [[Kot-Mag]] · [[Pety]] · [[Twierdza (Tycoon)]] · [[Karczma (Questy)]] · [[HUD]] · [[Shakes & Fidget — rozbiór mechanik]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Sesja główna 2026-11-14 — zapis ustaleń]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[00 Start]]
