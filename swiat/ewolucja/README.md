# Monster Evolution — etap 1 próbki (22.11.2026, propozycja)

Projekt: „Projekt próbki — Monster Evolution”, sekcja **Etap 1**. Gracz jest potworem na polu: je kulki i mniejsze
stworki, zapełnia pasek, **EVOLVE** → odsłona następnej formy (stała drabina 8 form do Olbrzyma). Każda zdobyta forma
zostaje w **legowisku** (panel DEN) i daje złoto na sekundę (1, 2, 4, 7, 12, 20, 35, 60). Złoto kupuje trzy stałe
ulepszenia: Szczęka (zasięg i tempo gryzienia), Szybkość (16 → 19 → 22), Apetyt (×1,25, ×1,5). Zjedzony gracz spada
o jedną formę (legowisko, złoto i ulepszenia zostają), wraca po 2 s z tarczą na 5 s. Formy 1–2 chronione przed
graczami; boty zjadają je tylko, gdy na nie polują, a przez pierwszą minutę sesji nikt nie poluje na nowego gracza.
Bez zapisu między sesjami. Napisy w grze po angielsku.

- Drabina: SLIME (SLURP) → ACORNLING (HEADBUTT) → CROAKER (TONGUE) → SHROOMLING (SPORE CLOUD) → LEAF FOX (DASH) →
  THORN WOLF (POUNCE) → FOREST TROLL (GROUND SLAM) → GIANT (model bossa Strażnik Topieli; GIANT STOMP, korona i ogłoszenie).
  Modele z Pet Areny (bez szkieletów) — ruch proceduralny: krok-podskok, zgniecenie i rozciągnięcie, pochylenie
  w biegu i w zakrętach, kiwanie, wypad przy gryzieniu, łuk skoku, chwianie po ogłuszeniu.
- Sterowanie: telefon — drążek pod lewym kciukiem, BITE, DASH, przycisk umiejętności, EVOLVE przy pełnym pasku, DEN;
  komputer — WASD, spacja / klik = BITE, Shift = DASH, E = umiejętność, F = EVOLVE, Tab = DEN; pad — A / B / X / Y.
- Responsywność: własny potwór przewidywany u klienta (ruch, DASH, szarża); serwer przyjmuje pozycję zgodną z prędkością,
  inaczej poprawia klienta. Jedzenie, wzrost, złoto i zakupy liczy tylko serwer; akcje sprawdzane (typy, NaN, stan)
  i ograniczone wiadrem (30/s).
- Miary w pamięci (atrybut gracza `EW_Miary`, haczyk `miary`): czas sesji, czas dojścia do każdej formy, śmierci i czy
  gracz po śmierci grał dalej (akcja w 20 s), kupione ulepszenia.
- Kontener `Workspace/EwolucjaGra` (atrybut `Wygenerowane`), pole wokół (0, 0, −800); wzorce 8 modeli kopiowane
  z `PetArenaGra/Wzorce`. Skrypty ze strażnikiem „tylko Studio” — `--publikacja` buduje bez niego.

## Jak zbudować i sprawdzić
```
python -B swiat/ewolucja/dane.py                         # ustawienia.json + dane Pet Areny → zrodla/DaneEwolucji.luau
python -B swiat/ewolucja/testy/test_ewolucji.py          # logika bez Studio (15 testów)
python -B swiat/ewolucja/tempo.py [--prob 8]             # symulacja tempa „sprawnego gracza”
python -B swiat/ewolucja/zbuduj.py --studio <id>         # budowa (--sucho, --skrypty, --stan, --usun, --publikacja)
python -B swiat/ewolucja/zbuduj.py --wlacz on|off --studio <id>     # wyłącznik EwolucjaWlaczona
python -B swiat/ewolucja/testy/proba_play.py --studio <id>          # próba Play (15 punktów, zrzuty do klatki/)
python -B swiat/ewolucja/testy/proba_telefon.py --studio <id>       # Device Simulator: najmniejszy telefon, układ HUD
python -B swiat/ewolucja/testy/demo_wideo.py --studio <id>          # film demo ok. 35 s + plansza (poza repo)
```
Przed próbą Play inne gry wyłączone: `swiat/pet_arena/zbuduj.py --wlacz off`, `swiat/zabawki/zbuduj.py --wlacz off`.

## Wyniki etapu 1 (22.11.2026)
- Testy logiki 12/12. Play 13/13, telefon (Samsung Galaxy A06, 705 × 338) 6/6, konsola bez błędów, klatka 16,7 ms.
- Tempo (symulacja, 8 prób, mediana): forma 2 0:26, forma 3 1:12, 1. ulepszenie 1:32, 1. pościg 1:23, forma 5 6:30,
  Olbrzym 13:49. W Play autopilot: pierwszy pełny pasek 19–36 s, druga ewolucja 52–61 s po pierwszej.
- Opóźnienie 2 × 60 ms: własny potwór przesunięty o 2,7 st po 0,15 s, 0 poprawek serwera, BITE gra w tej samej klatce.
- Zrzuty: `klatki/01_start.jpg`, `02_jedzenie.jpg`, `03_odslona.jpg`, `04_legowisko.jpg`, `05_pogon.jpg`, `06_telefon.jpg`,
  etap 2: `07_las.jpg`, `08_boss.jpg`.

## Etap 2 — „pierwsze dziesięć minut” (22.11.2026)
- **DEEP WOODS**: drugie koło na północ od łąki za niskim płotem z tablicą (sylwetki mieszkańców, „REACH FORM 4”);
  otwiera się po zdobyciu formy 4 (płot przygasa, baner, strzałka do bramy). Większe kulki (+5 i +14), boty form 4–7
  (4/2/1/1), boty nie wychodzą ze swojej strefy. **Mini-boss VINE SERPENT** (model bossa Pet Areny): pasek życia, BITE
  i umiejętności zadają rany, sam gryzie (odrzut, krótkie ogłuszenie, −8 % paska, bez zjadania), pokonany daje
  skrzynię 1500 złota i ogłoszenie na serwerze, wraca po 90 s.
- **Tempo**: łaska nowicjusza 110 s (pierwszy pościg nie przed 1:50), ulepszenia mają poziomy 4 i 5 (drożej),
  potrzeby form przestrojone (`tempo.py` liczy też las, bossa i najdłuższą przerwę bez nowości w pierwszych 10 min).
- **Wygląd pola**: kępki trawy, grzyby, krzaki przy murze, staw z liliami na łące i w lesie, kamienny krąg, menhiry,
  ciemna ściółka lasu, drzewa w lesie i za jego murem; ok. 1490 części sceny (z sylwetkami na tablicy).
- **Ruch**: jeden ogólny system z parametrów formy w danych (`chod`: skok / klus / dwunozny / pelzanie, `podskok`,
  `pochyl`, `krok`, opcjonalnie `anim` z identyfikatorami klipów dla modelu ze szkieletem). Grupy części (nogi, ogon,
  głowa) liczone z geometrii modelu, więc formę można podmienić samymi danymi. Kurz przy krokach, kłapnięcie głową.
- **Odczucie jedzenia**: „+N” nad kulkami, chrupanie przy stworkach, puls paska, błysk i wstrząs przy ewolucji
  (silniejszy dla większych), kamera dalej dla większych form.
- Wydanie do prywatnej publikacji: `zbuduj.py --publikacja --wydanie etap2` (bez strażnika Studio, atrybut `Wydanie`);
  powrót do wersji tylko w Studio: `zbuduj.py --studio <id>` (pełna budowa ze strażnikiem).
- Film demo: `testy/demo_wideo.py --studio <id>` → folder tymczasowy systemu (`%TEMP%\ewolucja_demo\`), poza repo.
- **Wyniki etapu 2**: testy logiki 15/15; Play 15/15 na wydaniu do publikacji (start, jedzenie, 2 ewolucje, legowisko,
  zakup, pościg i zjedzenie, boty, miary, odpowiedź na wejście, DEEP WOODS, mini-boss; konsola bez błędów; klatka
  16,7 ms przy 35 potworach); telefon 6/6; film 33,7 s. Tempo (8 prób, mediana): forma 2 0:20, forma 3 1:09, las 2:49,
  boss spotkany 4:29 i pokonany 5:26, forma 5 6:47, forma 6 8:20, Olbrzym 13:29, 1. pościg 1:59, 1. ulepszenie 1:33;
  **najdłuższa przerwa bez nowości w 10 min 3:02 — cel 2:30 niespełniony** (rozrzut między próbami 2:08–3:31).

## Etap 3 — legowisko w świecie, warianty, zapis (22.11.2026)
- **Legowisko w świecie**: 12 działek na skraju łąki (po jednej na miejsce na serwerze). Gracz rodzi się w swoim legowisku.
  Na 8 cokołach stoją trofea zdobytych form, widoczne dla wszystkich (u siebie także ciemne sylwetki niezdobytych
  i tabliczki „LV n”). Złoto z trofeów zbiera się w legowisku (kupka złota rośnie) i trafia do gracza, gdy wejdzie.
  HUD pokazuje osobno złoto zebrane i złoto w legowisku, a podpowiedź ze strzałką prowadzi po złoto. Własne
  legowisko to strefa bezpieczna: nikt cię tam nie zje, ty też nie jesz, boty nie wchodzą.
- W napisach dla gracza legowisko to **LAIR**, a kupka złota w nim to **HOARD** (pod przyszłego smoka; nazwy w kodzie
  bez zmian).
- **Poziomy trofeów** (5, ×1 / 1,5 / 2,2 / 3,2 / 4,5): kupowane w legowisku w zakładce TROPHIES panelu DEN, złotem
  zebranym. Ulepszenia (zakładka UPGRADES) można kupować wszędzie.
- **Warianty** przy każdej ewolucji, losuje je serwer: GOLD 8 %, CRYSTAL 3 %, RUBY 1 %, RAINBOW 0,2 %. Szanse są
  pokazane w panelu. Kokon świeci kolorem wariantu przed odsłoną. Trofeum w wariancie mnoży dochód formy ×2 / ×4 / ×8 /
  ×20 i stoi na cokole w kolorach wariantu. Zostaje najlepszy wariant formy. Niczego nie da się kupić.
- **VINE SERPENT w stopniach 1–5**: życie 220 → 980, skrzynia 1500 → 20 000. Pierwsza wygrana na stopniu daje trofeum
  bossa (dochód legowiska). Gwiazdki stopnia widać w pasku bossa.
- **Olbrzym jako boss serwera** (od 2 graczy): inni gryzą go za 25 złota za trafienie. Kto zbije mu życie do zera,
  dostaje skrzynię 3000, a Olbrzym spada o formę. Olbrzym z koroną dostaje 25 złota/s.
- **Zapis** (`player_<UserId>` w magazynie `Ewolucja_Gracz_v1`, pole `wersja`, uzgadnianie z szablonem i walidacja
  liczb): złoto zebrane i w legowisku, ulepszenia, zdobyte formy, najlepsze warianty, poziomy trofeów, trofea bossa,
  czas ostatniej wizyty. Po wejściu gracz zaczyna od formy 1, reszta zostaje. Legowisko zarabia pod nieobecność
  (najwyżej 2 h), a gra mówi, ile. Blokada sesji przez `UpdateAsync` (job serwera, 600 s). Zapis co 60 s, przy wyjściu
  i przy zamknięciu serwera; cudza blokada albo nieudane wczytanie oznacza grę bez zapisu (nie nadpisujemy postępu).
  **W Studio i w każdej próbie zawsze magazyn w pamięci** (atrybut kontenera `ZapisTryb = pamiec`), nigdy prawdziwy
  DataStore. Kontener `EwolucjaGra` dopisany do listy znacznika prób w `tools/zapis_prob.py`.
- **Tempo**: łaska 110 s, ceny i potrzeby przestrojone; najdłuższa przerwa bez nowości w pierwszych 10 min 2:27
  (cel 2:30 spełniony), stopnie bossa wypełniają minuty 7–13.
- **Wyniki etapu 3**: testy logiki 21/21 (zapis i wczytanie z magazynem w pamięci, blokada sesji, limit 2 h, szanse
  wariantów na 20 000 losowaniach, poziomy trofeów, strefa bezpieczna, stopnie bossa, Olbrzym). Play 21/21 na wydaniu
  do publikacji, w tym wyjście i powrót po godzinie: stan odtworzony, złoto legowiska +stawka × 3600, komunikat
  u klienta. Telefon 7/7; klatka 16,7 ms; konsola bez błędów; film 30,7 s (`%TEMP%\ewolucja_demo\ewolucja_etap3.mp4`).
  Tempo (8 prób): forma 2 0:22, forma 3 1:22, las 2:56, boss 3:30 / 4:38, forma 5 6:06, stopnie 2–3 7:00 / 8:41,
  forma 6 8:26, forma 7 10:33, Olbrzym 13:15, 1. pościg 1:51, 1. ulepszenie 1:41.
- W Studio ogłoszenia używają nazwy „Player N” zamiast nazwy konta (zrzuty i filmy bez prywatnych danych).

## Smok (22.11.2026) — jeden smok w ośmiu stadiach
- `"zestaw": "smok"` w `ustawienia.json` (domyślnie); `"potwory"` przywraca osiem modeli Pet Areny jedną zmianą.
- **Generator** `smok.py`: smok z klocków, bez wgrywania. Tułów, brzuch, szyja, głowa z pyskiem, szczęką, oczami
  i rogami, cztery nogi, ogon z segmentów, dwa skrzydła, kolce; płyty, grzebień i świecenie zależnie od stadium.
  Stadia: HATCHLING 31, WHELP 35, DRAKE 42, FIRE DRAKE 43, DRAGON 45, WAR DRAGON 51, ELDER DRAGON 51,
  ANCIENT DRAGON 60 części (potwory Pet Areny miały 32–545).
  Parametry stadium (proporcje, kolory, dodatki) są danymi w `formy_smok[].smok`. Zrzut `klatki/13_stadia_smoka.jpg`
  pokazuje stadia obok siebie w wyrównanej wysokości; w grze różnica wielkości jest dużo większa.
- **Model do podmiany bez kodu**: części z atrybutem `Grupa` — 1–4 nogi (LP, PP, LT, PT), 6 głowa, 7 szczęka,
  8/9 skrzydło L/P, 11+ kolejne segmenty ogona — oraz atrybuty modelu `Pivot<k>` (punkt obrotu w skali 1).
  Część `Korzen` w (0, 0, 0) jest PrimaryPart, przód to −Z. Opcjonalnie pole `anim` z klipami dla modelu z Animatorem.
- **Ruch**: nogi kłusem po przekątnej, ogon łańcuchem segmentów, skrzydła złożone z lekkim drżeniem i otwarte
  w zrywie, szarży i szybowaniu, szczęka kłapie przy BITE, oddech w spoczynku. Większe stadia stąpają wolniej i ciężej.
- **Umiejętności**: NIBBLE, TAIL WHIP, EMBER SPIT, WING GUST (nowy typ: odepchnięcie), FIRE BREATH (nowy typ: stożek),
  ROAR, WING GLIDE (niskie szybowanie nad mniejszymi — jedyny „lot”), INFERNO. Efekty dobierane polem `efekt`.
- **Warianty** jako wygląd smoka: GOLD (metal), CRYSTAL (szkło), RUBY, RAINBOW. Widać je także u innych graczy
  (bajt wariantu w migawce stanu).
- **Legowisko**: na cokołach stoją stadia smoka; sylwetki na tablicy lasu i rozmiar na cokole biorą się z danych.
  Na łące napis „DRAGON LAIR EVOLUTION”. Przy każdym legowisku 6 kulek startowych: pierwsza kulka w 1–3 s.
- Mini-boss VINE SERPENT bez zmian. Bossem serwera jest teraz ANCIENT DRAGON (ostatnie stadium).
- Tempo (6 prób, domyślnie): forma 2 0:17 i forma 5 5:12 — wcześniej niż cele (bez przestrajania). Reszta w celach:
  przerwa 2:18, pościg 1:52, ulepszenie 1:31, ANCIENT 13:55.

## Czego nie ma (etap 4 i dalej)
Legowisko jako miejsce w świecie, złoto pod nieobecność, zapis postępu, odmiany barwne, Olbrzym jako boss serwera,
umiejętności botów, dźwięki poza arkuszem Pet Areny. Prawdziwego dotyku nie da się wywołać z prób — drążek i przyciski
sprawdza wejście prób (to samo co palec po stronie logiki); dotyk trzeba potwierdzić na telefonie.
