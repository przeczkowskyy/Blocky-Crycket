---
status: propozycja
tags: [wytwórnia, analiza, rynek, pomysły]
źródło: "analiza agenta (Fable) z 2026-11-22 na zlecenie Karola: analiza i pomysł na kolejny hit we wschodzącym trendzie, bez kopiowania 1:1; dane: listy Roblox, trackery, własny spis ok. 3 tys. gier, rozbiór wzoru"
---
# Anatomia pętli, która trzyma (2026-11-22)

> [!info] W skrócie
> Model pętli w dziesięciu zasadach z dowodami — co wytwarza oczekiwanie, niespodziankę i „co dalej” w obecnych hitach z kolekcją i odsłonięciem; oraz czego ten model nie tłumaczy.

Stan na 22.11.2026 (niedziela rano UTC). Oznaczenia: **[F]** fakt ze źródła, **[W]** wniosek, **[?]** nie da się ustalić.

**Skąd dane i co to ogranicza**
- Szczegółowy rozbiór Throw Food For Animals i jej kopii zrobił drugi analityk: pliki `rozbior_throw\[[Rozbiór wzoru — Throw Food For Animals]]`, `[[Kopie pętli rzutu — listopad 2026]]`, `[[Zasady pętli z odsłonięciem]]` (dalej „rozbiór wzoru”). Korzystam z niego, nie powtarzam.
- Liczby graczy naraz i daty utworzenia: API Roblox z 22.11.2026 ok. 07:10 UTC ([lista Up-and-Coming](https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=abc123&sortId=up-and-coming&cpuCores=4&maxResolution=1920x1080&maxMemory=8192&networkType=wifi), [Top Trending](https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=abc123&sortId=top-trending&cpuCores=4&maxResolution=1920x1080&maxMemory=8192&networkType=wifi), `games.roblox.com/v1/games`, wyszukiwarka `omni-search`). To dołek tygodnia (noc w USA), więc liczby są niższe niż w sobotni wieczór z notatki z 21.11.
- Średnie 7- i 14-dniowe, sesje i szczyty: [RoTrends](https://www.rotrends.com) i [RoWatcher](https://rowatcher.com), strony poszczególnych gier.
- **Nikt z nas nie grał w te gry.** Mechaniki znam z opisów gier, poradników i jednego filmu z napisami. To rozbiór na papierze. Poprzednie oceny na papierze pomyliły się dwa razy.

---

## 1. Jeden szablon, wiele czynności

[F] Opisy lidera i gier rosnących są prawie tym samym zdaniem z podmienionym czasownikiem:

| Gra (utworzona) | Gracze naraz 22.11 rano | Jak zdobywasz | Gdzie siedzi emocja | Ryzyko | Liczba bohatera | Inni gracze |
|---|---|---|---|---|---|---|
| Grow a Garden (25.03.2025) | 22 tys. (szczyt 22,3 mln w 2025) | sadzisz i czekasz | losowy towar w sklepie co 5 min, mutacje z pogody | brak | pieniądze | ogródki obok, handel |
| Steal a Brainrot (16.05.2025) | 41 tys. (szczyt ponad 25 mln) | kupujesz z taśmy | kradzież między graczami | wysokie (okradną cię) | odrodzenia | rdzeń gry |
| **Steal An Egg** (25.07.2026) | **981 tys.**, śr. 7 dni 763 tys. | kradniesz jajko strażnikowi i uciekasz | pościg, potem wyklucie | pościg; kradzież między graczami | szybkość (bieżnia) | kradną sobie |
| Break and Steal an Egg (05.09.2026) | 82 tys. | rozbijasz jajko kilofem na miejscu, uciekasz ze zwierzęciem | odsłona przed ucieczką | pościg | szybkość, kilof | słabo |
| **Throw Food For Animals** (18.09.2026) | 330–347 tys., śr. 7 dni 285 tys. | rzucasz jedzenie | scenka podejścia w 4–5 krokach | **żadne** | siła rzutu (drążek) | prawie nieważni (5 osób) |
| Throw a Seed (07.11) | 40 tys. | rzucasz nasiono | roślina wyrasta | żadne | siła | — |
| Pull a Dino (03.11) | 6 tys. | harpun w błoto, wyciągasz | co wyjdzie z błota | żadne | siła (ławki), szczęście | klany |
| Summon a Pet Army (20.10) | 12,8 tys., śr. 7 dni 7,9 tys. | bijesz dzikiego peta, pokonany dołącza | armia rośnie i walczy z bossem | walka | bęben wzmacnia armię | — |
| Scare Your Favorite Streamer (01.11) | 18 tys. (szczyt 35 tys.) | pukasz do drzwi, straszysz, kradniesz paczkę | fani rozbijają paczkę na przedmioty | — | bieżnia, „trener straszenia” | 7 osób |
| Stay the Night (17.10) | 11,6 tys. (szczyt 20 tys.) | znosisz meble, „przytulność” ściąga rzadszych lokatorów | noc: kto na zewnątrz, tego zjada bestia | okno nocy | dom | 7 osób |
| Fisch (2024) / Fish It! (2024) | 78 tys. / 71 tys. | zarzucasz, minigra | ryba z wagą i mutacją („400 tys.” / „milion odmian”) | brak | wędka | handel, wspólne wyprawy |

Źródła: opisy i liczby z API Roblox 22.11; średnie z RoTrends ([Steal An Egg](https://www.rotrends.com/game/10563114921), [Summon a Pet Army](https://www.rotrends.com/game/10772133952)); szczyty z RoWatcher ([Stay the Night](https://rowatcher.com/games/10771533429/dying), [Scare Your Favorite Streamer](https://rowatcher.com/games/10774160414/dying)); rozbiór wzoru; notatka „Radar trendów” w sejfie.

[W] **Wspólna podstawa** (ma ją każda gra z tabeli, także kopie, które zgasły): zdobyty stwór staje w bazie i daje dochód na sekundę, także gdy gracza nie ma → pieniądze idą w jedną liczbę bohatera → ta liczba otwiera dalszą strefę z rzadszymi stworami → rozmiar i kolor jako dwie osie rzadkości → Indeks → sobotnie wydarzenie. **To warunek wejścia, nie przewaga.** Throw Lucky Block For Animals ma to wszystko i spadł z 13 tys. do 3 tys. (rozbiór wzoru, `[[Kopie pętli rzutu — listopad 2026]]`).

[W] **Gry różnią się jednym: miejscem, w którym siedzi emocja.** Każdy kolejny lider przeniósł ją gdzie indziej: czekanie na towar (ogród) → okradanie ludzi (Brainrot) → ucieczka przed strażnikiem i wyklucie (Egg) → sama odsłona rozciągnięta na kilka kroków (Throw Food). To najważniejsza obserwacja dla części B i D.

---

## 2. Rytm wzoru (Throw Food For Animals)

| Co | Jak często | Pewność |
|---|---|---|
| Rzut i cała scenka | ok. 10–20 s na cykl | [W] szacunek z montowanego filmu (rozbiór wzoru) |
| „Coś specjalnego” w odsłonie | ok. 20% rzutów ma kolor, ok. 20% rozmiar → mniej więcej **co trzeci rzut** (1 − 0,795 × 0,80 ≈ 36%) | [F] szanse z poradnika games.gg, rachunek mój |
| Wielka wygrana | rozmiar Infinite raz na ok. 20 000 rzutów | [F] |
| Powtórka tego samego stwora | ostatnio złapany jest 200 razy mniej prawdopodobny | [F] game.guide |
| Trening | powtórzenie co 0,5 s, także bez gracza; premia do kliknięcia co 4–6 s | [F] |
| Zakup (jedzenie, drążek, miejsca w bazie) | co 1–3 min na początku | [W] z cen: drążek $1, potem $50, $2 tys. |
| Nowa kraina | pierwsza od poziomu 28, czyli po kilkunastu–kilkudziesięciu minutach bez płacenia; potem coraz dłużej; każda daje nową pulę i ok. 10 razy większy dochód | [F] progi, [W] czas |
| Postęp wewnątrz krainy | trzy części krainy z coraz wyższym sufitem rang | [F] |
| Wydarzenie na serwerze | odliczanie 5:00 przy „admin abuse”; w tygodniu wydarzenia zmiana siedliska co 30 min | [F] |
| Wydarzenie tygodnia | każda sobota od 25.10: nowa mapa albo wydarzenie; następne zapowiedziane z wyprzedzeniem | [F] |
| Nowa treść | 15 → 17 → 19 krain w trzy tygodnie | [F] |

[F] Średnia sesja 17,7 min, w ostatnim tygodniu −9% (RoTrends). Szczyt 2,4–2,5 mln padł w dzień wydarzenia 21.11 przy średniej ok. 285 tys.

---

## 3. Model pętli — dziesięć zasad

**M1. Wynik losuje się od razu, ale gra odsłania go w kilku krokach.**
Dowód: we wzorze kolejno rośnie licznik „1 in X” i napisy stopnia szczęścia, kamera odsuwa się zależnie od rozmiaru, widać kolor poświaty, imię jest zakryte pustymi literami, gatunek widać na końcu (film z napisami w rozbiorze wzoru). Gracz zgaduje na głos. Najlepsza kopia (Throw a Seed, szczyt 171 tys.) zmieniła właśnie odsłonę. Kopie, które zmieniły tylko przedmiot do rzucania, mają 6–400 graczy.

**M2. Dwie niezależne osie „lepszości”, widoczne przed odsłoną i mnożące wartość.**
Dowód: mutacje ×1,5 do ×20 i rozmiary ×1,5 do ×38 we wzorze; „sizes and mutations” w opisie Steal An Egg; albinosy i odmiany barwne w Realistic Hunting; złote, diamentowe i tęczowe cegły w Brick a House. Skutek uboczny: ze 148 modeli robi się kilka tysięcy różnych wyników.

**M3. Często coś małego, bardzo rzadko coś ogromnego.**
Dowód: co trzeci rzut ma „coś”, a szczyt drabiny to 1 na 20 000. Nadzieja nie gaśnie, a wielka wygrana pozostaje historią do opowiedzenia.

**M4. Gra aktywnie tłumi powtórkę.**
Dowód: kara 200× za ostatnio złapanego stwora. Nasze trzy prototypy tego nie miały („cały czas to samo”).

**M5. Jedna liczba bohatera, która dosłownie znaczy „dalej”, i widać ją w świecie.**
Dowód: siła rzutu przenosi jedzenie za widoczną granicę krainy; szybkość w Steal An Egg decyduje, z których stref zdążysz uciec. Trening idzie też bez gracza, ale obecność jest nagradzana.

**M6. Horyzont widać, zanim da się do niego dojść, i przesuwa się co tydzień.**
Dowód: następna kraina leży na tym samym pasie („it's looking green… we need to get there”); liczba krain rosła 15 → 17 → 19. Każda kraina dewaluuje stary majątek, więc trzeba iść dalej.

**M7. Zdobycz ma od razu dwie role: trofeum na widoku i źródło dochodu, także offline.**
Dowód: wszystkie gry z tabeli. Ograniczona liczba miejsc wymusza wybór (sprzedać czy postawić).

**M8. Pierwsza minuta nie pozwala się zgubić ani przegrać.**
Dowód: we wzorze gra sama mówi, co kupić; pierwszy stwór po kilkunastu sekundach; pierwszy drążek kosztuje $1.

**M9. Stała pora wydarzeń i licznik uczą, kiedy wrócić.**
Dowód: wzór był mały przez 5 tygodni i wybił się dopiero z pierwszą dużą aktualizacją (25.10); od tego czasu coś dzieje się w każdą sobotę; szczyt w dzień wydarzenia to 8–9 razy zwykły dzień.

**M10. Płacenie wzmacnia to samo, co bawi (szczęście), i bywa wspólne.**
Dowód: płatny rzut ×100 i szczęście dla całego serwera; wzór jest nr 5 w zarobkach (RoTrends).

---

## 4. Obserwacje właściciela jako hipotezy

| Hipoteza | Werdykt | Uzasadnienie |
|---|---|---|
| „Ciekawi mnie, jaka kraina i jakie potwory będą dalej” | **potwierdzona** | M6; to jedyna rzecz, której nie dał żaden nasz prototyp |
| „Rozmiar sugeruje rzadkość” | **częściowo** | rozmiar to osobna oś, nie rzadkość gatunku; dla gracza „duży = dobry”, bo mnoży dochód |
| „Otoczka złota, platynowa, rubinowa, tęczowa” | **potwierdzona** | Gold → Diamond → Emerald → Ruby → Rainbow; „platynowa” to Diamond |
| „Do końca nie wiadomo, jaki to potwór” | **potwierdzona** | imię zakryte pustymi literami aż do końca |
| „Gra ma wydarzenia” | **potwierdzona i ważniejsza, niż brzmi** | wydarzenia to główny silnik powrotów i przyczyna wybicia się gry |
| „Przepis: czynność + ulepszanie bohatera + potworki dające złoto” | **prawdziwa, ale niewystarczająca** | to podstawa, którą mają też kopie z 6 graczami; we wzorze bohater ma jedną liczbę (siłę), szybkość pochodzi z rodziny Steal An Egg |
| „Mógłbym grać praktycznie cały czas” | **nie dla przeciętnego gracza** | średnia sesja 17,7 min i spada; gracz z płatnym szczęściem dochodzi do końca treści w ok. godzinę |

---

## 5. Czego ten model NIE tłumaczy

1. **Dlaczego wygrał wzór, a nie 25 podobnych gier.** Widzę tylko zwycięzców. Nie widzę wydatków na reklamę, umów z twórcami ani szczęścia w poleceniach. Część sukcesu to praca po starcie (cotygodniowe aktualizacje), a tej nie da się skopiować pomysłem.
2. **Dlaczego właściciela znudziła nasza zabawka z trafianiem w biegnące potwory, a bawi go gra, w której robi się jedno kliknięcie.** To sugeruje, że w tym gatunku **sprawczość i zręczność nie są źródłem frajdy**, tylko oczekiwanie i postęp. Model nie mówi, czy dodanie zręczności pomoże, czy zaszkodzi.
3. **Hitów bez kolekcji:** Hyper Realistic Ragdoll (108 tys., serwer jednoosobowy, zero majątku), 100 Miles Down the River (wspólna wyprawa), Survive Your Ideas (chaos od graczy), Ant Evolution (postęp można stracić). Tam działa niespodzianka z fizyki, wspólna historia albo ryzyko.
4. **Długości życia.** Wzór jest 4 tygodnie po wybiciu. Steal An Egg trzyma 763 tys. po czterech miesiącach i ma kradzież między graczami. Czy gra bez ryzyka i bez ludzi utrzyma się równie długo — nie wiadomo.
5. **Roli dźwięku i tempa scenki.** Nie udało się ustalić, ile trwa scenka i co w niej słychać, a to może być połowa efektu.
6. **Dzieci.** Jedyny tester to dorosły twórca. Trzy razy trafnie wskazał nudę, więc jest dobrym filtrem „to nie działa”. Nie jest dowodem „to zadziała”.

## Powiązane
- [[00 Wytwórnia pomysłów]] · [[Fale na Roblox 2026 i gdzie jest otwarcie]] · [[Wschodzące trendy 2026-11-22]] · [[Trzy pomysły na następną grę (2026-11-22)]] · [[Następna gra — rekomendacja 2026-11-22]] · [[Lekcje z prototypów]]
