---
status: propozycja
tags: [wytwórnia, projekt, próbka]
źródło: "projekt agenta z 2026-11-22 po walidacji kierunku; budowa zlecona przez Karola (D-129)"
---
# Projekt próbki — Monster Evolution

> [!info] W skrócie
> Najmniejsza pełna pętla gry o ewolucji potwora: jesz, rośniesz po drabinie ośmiu form do Olbrzyma, zdobyte formy zarabiają w legowisku, złoto ulepsza bohatera. Budowa w czterech etapach, progi dla prawdziwych graczy zapisane przed próbą, warunek z rynku na 29.11. Kod: `swiat/ewolucja/`, kontener w Studio `EwolucjaGra`.

Stan na 22.11.2026. Wszystkie liczby to wartości startowe do strojenia, nie wyniki pomiarów.

## Jedno zdanie
Zaczynasz jako najmniejszy potwór, jesz i rośniesz po czytelnej drabinie ośmiu form aż do Olbrzyma, a każda zdobyta forma zostaje w twoim legowisku i zarabia złoto.

## Skąd ten kształt (dowody z walidacji)
| Decyzja projektu | Dowód |
|---|---|
| Stała, czytelna drabina form, a nie losowanie formy | filmy niesie „ostatnia forma” i „od słabego do najsilniejszego” (931 tys. wyświetleń); gra z całą ewolucją losowaną ma 0 graczy |
| Legowisko: zdobyte formy zarabiają | gatunkowi brakuje powodu powrotu (hity gasną w tygodnie, lider ma 3 ulubione na 1000 wizyt); tego elementu nikt tu nie sprawdził — to nasz wyróżnik i największa niewiadoma |
| Łagodna strata i ochrona najmniejszych | bycie zjadanym odstrasza nowych graczy (kilka gier poleca prywatne serwery, lider sprzedaje „nie tracisz mocy”) |
| Następna forma jako ciemna sylwetka, szczyt drabiny jako wielki cień | ciekawość „w co się zmienię” bez odbierania czytelnego celu |
| Odmiana barwna jako dodatek przy ewolucji (później) | losowanie jako premia działa u lidera; jako rdzeń nie działa |

## Pętla (pełna, w najmniejszej postaci)
1. **Jesz:** kulki małe (+1) i duże (+5) oraz mniejsze stworki sterowane przez grę (boty). Pasek wzrostu się zapełnia.
2. **Ewoluujesz:** przycisk „Evolve” → odsłona 3–4 s (kokon, kamera odjeżdża tym dalej, im większa forma, tabliczka z nazwą) → nowa forma z własną umiejętnością.
3. **Legowisko:** każda forma zdobyta choć raz zostaje w legowisku jako trofeum i daje złoto na sekundę. W etapie 1 legowisko to panel na ekranie.
4. **Ulepszasz bohatera za złoto:** Szczęka (zasięg i tempo gryzienia), Szybkość, Apetyt (mnożnik wzrostu). To zostaje na zawsze.
5. **Ryzyko:** większy może cię zjeść. Tracisz jedną formę, ale legowisko, złoto i ulepszenia zostają.
6. **Cel:** szczyt drabiny — Olbrzym. Kto nim zostanie, dostaje koronę i ogłoszenie na serwerze.

## Sterowanie (telefon najpierw)
Ruch gałką, przycisk Gryź, przycisk Zryw (krótki sprint z odnowieniem), przycisk Evolve pojawia się po zapełnieniu paska. Umiejętność formy pod jednym przyciskiem.

## Drabina (8 form)
- Osiem istniejących modeli potworów ułożonych od najmniejszego do największego; ostatnia forma jest wyraźnie ogromna.
- Panel drabiny z boku: zdobyte formy w kolorze, następna jako ciemna sylwetka, dalsze jako „?”, na szczycie wielki cień.
- Każda forma ma jedną umiejętność z gotowej puli.

## Zasady jedzenia
- Zjadasz kulki, boty i graczy co najmniej o jedną formę mniejszych.
- Formy 1 i 2 są chronione przed graczami (zagrażają im tylko boty).
- Zjedzony: spada o jedną formę (nigdy poniżej pierwszej), odradza się po 2 s z 5-sekundową tarczą.
- Boty: 20–30 stworków w formach 1–6, jedzą kulki, uciekają przed większymi, gonią mniejszych, nie stoją przy miejscu startu.

## Złoto i ulepszenia (startowo)
- Trofea w legowisku dają kolejno 1, 2, 4, 7, 12, 20, 35, 60 złota na sekundę.
- Szczęka, Szybkość (16 → 19 → 22) i Apetyt (×1,25, ×1,5) po trzy poziomy; pierwszy zakup możliwy ok. 1:30–2:00 gry.

## Tempo (cele do sprawdzenia symulacją i próbą)
| Zdarzenie | Kiedy |
|---|---|
| Pierwsza ewolucja z odsłoną | 20–30 s |
| Druga ewolucja | do 1:30 |
| Pierwsze ulepszenie | 1:30–2:00 |
| Pierwsze realne zagrożenie | ok. 2:00 |
| Forma 5 | 6–7 min |
| Olbrzym | ok. 15 min dla sprawnego gracza |

## Pierwsze 60 sekund
Start jako forma 1 obok kulek → strzałka do kulek → pasek pełny ok. 25. sekundy → Evolve z odsłoną → dymek „Legowisko: +1 złota/s” → sylwetka następnej formy na drabinie → większe kulki i pierwszy mały bot do zjedzenia.

## Etapy budowy
1. **Etap 1 (ten):** pole, jedzenie, boty, drabina 8 form z odsłoną i panelem, zasady jedzenia i straty, legowisko jako panel ze złotem, trzy ulepszenia, sterowanie na telefon, zapis miar w grze. Bez zapisu między sesjami.
2. **Etap 2:** legowisko jako miejsce w świecie, złoto także pod nieobecność gracza, odmiany barwne przy ewolucji (jawne szanse, tylko waluta z gry), zapis postępu.
3. **Etap 3:** Olbrzym jako boss serwera z nagrodą dla atakujących, wydarzenia z zegara, dopracowane pierwsze 60 sekund, wersja do prywatnej publikacji.
4. **Etap 4:** próba z 8–12 graczami spoza zespołu.

## Czego w próbce nie robimy
Sklepu i płatności, odrodzeń, zwierzaków z jaj, handlu, gildii, drugiej mapy, rankingów poza koroną Olbrzyma, muzyki poza kilkoma dźwiękami.

## Miary sukcesu u prawdziwych graczy (zapisane przed próbą)
Próba: 8–12 osób spoza zespołu, 9–15 lat, telefon, bez instrukcji, przerwanie po 20 minutach.

| Decyzja | Próg |
|---|---|
| Budujemy dalej | mediana gry co najmniej 12 min z 20; co najmniej 70% dochodzi do formy 5; co najmniej połowa umie nazwać następny cel; co najmniej połowa prosi o więcej albo wraca w ciągu dwóch dni |
| Poprawiamy raz | mediana 7–12 min albo 40–70% dochodzi do formy 5 |
| Porzucamy | mediana poniżej 7 min albo mniej niż 40% dochodzi do formy 5 |

Gra zapisuje: czas sesji, czas dojścia do każdej formy, liczbę śmierci i to, czy gracz po śmierci grał dalej, kupione ulepszenia.

## Warunek z rynku
Jeśli do 29.11 średnia 7-dniowa lidera fali (Ant Evolution) zacznie spadać o ponad 30% tygodniowo, wstrzymujemy budowę przed etapem 3 i oceniamy ponownie.

## Uczciwa skala
Dobrze zrobiona druga generacja w tej fali ma zwykle szczyt 0,5–5 tys. graczy naraz; 10 tys. i więcej mniej więcej raz na dziesięć. Hity tego gatunku gasną w 4–8 tygodni, jeśli nie mają powodu powrotu — dlatego legowisko jest najważniejszą rzeczą do sprawdzenia.

## Stan implementacji
- [ ] Etap 1 — pełna pętla w najmniejszej postaci (w budowie od 2026-11-22)
- [ ] Etap 2 — legowisko w świecie, złoto pod nieobecność, odmiany, zapis
- [ ] Etap 3 — Olbrzym jako boss, wydarzenia, pierwsze 60 sekund, wersja do prywatnej publikacji
- [ ] Etap 4 — próba z 8–12 graczami

## Powiązane
- [[Monster Evolution]] · [[Walidacja kierunku jesteś potworem (2026-11-22)]] · [[Kierunki z rynku 2026-11-22]] · [[00 Wytwórnia pomysłów]] · [[Lekcje z prototypów]] · [[Karta oceny pomysłu]]
