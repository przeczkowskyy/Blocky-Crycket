# Cutscenka biomu (D-077) — przyjęte wybory i pytania do ludzi

> **Status: propozycja.** D-077 jest zatwierdzona; poniższe wybory to sposób jej wykonania i każdy można zmienić
> jedną liczbą w `ustawienia.json` (potem `dane.py`, testy, `zbuduj.py --skrypty`). Nic z tej listy nie jest kanonem.

## Co mówi decyzja, a co dodałem
Decyzja: krótka cutscenka przy pierwszym wejściu do każdego biomu, kamera leci przez cały biom od przodu, pokazuje
mini-biomy i potwory, na końcu strażnik robi emotkę albo krzyczy; przy kolejnych wejściach jej nie ma; do
sprawdzenia płynność na telefonie. Reszta (oprawa, pomijanie, napisy, długość) to wybory wykonawcze.

## Przyjęte wybory
| Sprawa | Wybór | Gdzie zmienić |
|---|---|---|
| Długość | 11,2 s: lot 8,6 s + strażnik 2,6 s | `trasa.lot_s`, `trasa.postoj_s` |
| Trasa | z map: węzły przy inkubatorze, wejściu każdej przegrody, leżu, arenie i strażniku; wysokość najniższa z odstępem od brył | `trasa.*` |
| Zwolnienia | nad każdą przegrodą do ok. 45% prędkości przelotowej, nad leżem do 40% | `trasa.przegroda.zwolnienie*` |
| Plansza | nadtytuł „NOWA KRAINA” i nazwa biomu z pakietu gry, 0,1–1,9 s | `oprawa.plansza` |
| Podpisy przegród | nazwa przegrody z mapy przy każdym zwolnieniu (1,3 s) | `oprawa.podpisy_przegrod` |
| Strażnik | klip `ryk` z modelu, dźwięk ryku z katalogu, wstrząs 1,3 s, najazd o 6°, imię z mapy | `oprawa.straznik` |
| Pomijanie | **wyłączone** (wcześniejsze ustalenie właściciela: przelotu nie da się pominąć); przycisk POMIŃ i przełącznik są w kodzie | atrybut kontenera `Pomijanie = true`, `oprawa.pomijanie.domyslnie` |
| Wejście pieszo | cutscenka gra także po przejściu bramą (gracz staje zaraz za bramą) | — (jedna reguła wejścia) |
| Pamięć | sesja serwera + atrybut gracza gotowy pod zapis postępu (zapis wyłączony) | — |
| Stary przelot pasa | ustępuje przez haczyk, gdy ten pakiet stoi; bez pakietu działa jak dotąd | `README.md` |
| Zajęty gracz | walka, chmury, mini-gra, cudza kamera → cutscenka czeka i pyta co sekundę | `serwer.ponow_po_odmowie_s` |

Rzeczy, których świadomie nie ma: osobnej muzyki cutscenki, dźwięku na starcie (przejście przez chmury gra własny),
osobnej kopii strażnika (gdy strażnik jest akurat pokonany, cutscenka kończy się napisem bez ryku).

## Pytania do ludzi

### 1. Czy cutscenkę da się pominąć?
- Dziś wyłączone zgodnie z wcześniejszym ustaleniem (właściciel: „przelotu nie da się pominąć”); przełącznik gotowy.
- Włączenie: atrybut kontenera `Pomijanie = true` — pojawia się przycisk POMIŃ (dotyk, mysz, Spacja, Enter, B).
- Opcje: zostawić wyłączone / pomijalna zawsze / pomijalna dopiero przy odtworzeniu na życzenie.

Szczegóły: próba w grze z 18.11.2026 sprawdziła oba tryby (domyślnie przycisku nie ma i Spacja nic nie robi; po
włączeniu przełącznika Spacja kończy cutscenkę w 0,4 s i wszystko wraca). D-077 o pomijaniu nie mówi; D-078 dotyczy
tylko walk. Wartość domyślną trzyma `oprawa.pomijanie.domyslnie` w `ustawienia.json`.

### 2. Długość: 11 sekund czy krócej?
- Dziś: 11,2 s na biom (8,6 s lotu, 2,6 s strażnika), w granicach 8–12 s ze zlecenia.
- Krócej (ok. 9 s) = szybszy lot albo krótsze zwolnienia, potwory widać gorzej.
- Stary przelot trwał 10,2 s.

Szczegóły: jedna liczba `trasa.lot_s`; testy pilnują przyspieszenia i obrotu, więc przy zbyt krótkim locie powiedzą,
że kamera szarpie.

### 3. Co kamera pokazuje po drodze — czy dodać coś jeszcze?
- Dziś: inkubator, trzy przegrody z potworami, leże rzadkiego potwora, strażnik.
- Nie pokazuje osobno: Kamienia Powrotu, bramy do następnego biomu, domków potworów pod ścianami.
- Opcje: zostawić / dodać ujęcie bramy za strażnikiem (dłużej o ok. 1 s).

Szczegóły: brama do następnego biomu stoi za areną; ujęcie po ryku pokazałoby graczowi cel („pokonaj strażnika,
żeby przejść”), ale wydłuża cutscenkę ponad 12 s albo skraca przegrody.

### 4. Gest strażnika: sam ryk czy coś więcej?
- Dziś: klip `ryk` z modelu strażnika, dźwięk ryku, wstrząs kamery, napis z imieniem.
- Opcje: zostawić / osobny gest dla każdego strażnika (wymaga nowych klipów w modelach) / ryk dwa razy.
- Gdy strażnik jest akurat pokonany (odradza się 120 s), cutscenka kończy się bez ryku.

Szczegóły: nowe klipy to praca w `swiat/postacie/` i ponowny import modeli; pakiet weźmie nazwę klipu ze
znaczników mapy (`straznik.ryk.klip`).

### 5. Cutscenka także przy wejściu bramą pieszo?
- Dziś: tak — gra zaraz po przekroczeniu bramy, gracz stoi tuż za nią.
- Opcje: zostawić / przy wejściu pieszo krótsza wersja (sam strażnik) / pieszo wcale.
- Po cutscence gracz stoi tam, gdzie stanął (nie jest przenoszony na punkt przybycia).

Szczegóły: wejście pieszo zdarza się raz na biom (po pokonaniu strażnika poprzedniego), więc pełna cutscenka pełni
tu rolę nagrody. Krótsza wersja to osobna trasa — do zrobienia, jeśli wybierzecie tę opcję.

### 6. Napisy: nadtytuł „NOWA KRAINA” i podpisy przegród — zostawić?
- Nadtytuł „NOWA KRAINA” to jedyny tekst, którego nie ma w pakietach (nazwy biomów, przegród i strażników są z map).
- Podpisy przegród („Zagroda Slime'ów”, „Leże Trolla”…) pokazują się na 1,3 s przy zwolnieniach.
- Opcje: zostawić / inny nadtytuł / bez nadtytułu / bez podpisów przegród.

Szczegóły: `oprawa.plansza.nadtytul` i `oprawa.podpisy_przegrod.wlaczone`.

### 7. Stary przelot pasa — zostawić jako zapas czy usunąć?
- Dziś: zostaje w kodzie i gra sam, gdy kontenera `CutscenkaBiomu` nie ma.
- Próby lasu, Bagna i Dżungli sprawdzają od 18.11 to, co akurat gra: nową cutscenkę albo stary przelot.
- Opcje: zostawić zapas / usunąć stary przelot z pakietów biomów po akceptacji nowej cutscenki.

Szczegóły: wspólna pomoc prób to `pomoc_prob.py`; usunięcie starego przelotu to osobna zmiana w `swiat/las_pas_gra`
(skrypty pasa, dane, testy trzech pakietów).
