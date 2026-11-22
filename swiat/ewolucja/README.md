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
python -B swiat/ewolucja/testy/test_ewolucji.py          # logika bez Studio (32 testy: dane modeli, klipy, przeszkody świata, owce)
python -B swiat/ewolucja/tempo.py [--prob 8]             # symulacja tempa „sprawnego gracza”
python -B swiat/ewolucja/testy/walka_sim.py [--pojedynkow 40] # walka1: pojedynki, boss, zdolności na prawdziwej logice
python -B swiat/ewolucja/zbuduj.py --studio <id>         # budowa (--sucho, --skrypty, --stan, --usun, --publikacja)
python -B swiat/ewolucja/zbuduj.py --wlacz on|off --studio <id>     # wyłącznik EwolucjaWlaczona
python -B swiat/ewolucja/testy/proba_play.py --studio <id>          # próba Play (P01–P33, zrzuty do klatki/)
python -B swiat/ewolucja/testy/proba_telefon.py --studio <id>       # Device Simulator: najmniejszy telefon, układ HUD
python -B swiat/ewolucja/testy/demo_wideo.py --studio <id>          # film demo ok. 35 s + plansza (poza repo)
python -B swiat/ewolucja/testy/demo_wideo.py --studio <id> --walka --wyj <TEMP>/ewolucja_demo/ewolucja_walka.mp4   # film walki
python -B swiat/ewolucja/testy/demo_wideo.py --studio <id> --blender --wyj <TEMP>/ewolucja_demo/ewolucja_smok_blender.mp4   # smoki z Blendera
python -B swiat/ewolucja/testy/demo_wideo.py --studio <id> --swiat --wyj <TEMP>/ewolucja_demo/ewolucja_swiat.mp4   # wycieczka po świecie
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

## Pierwsze wrażenie (22.11.2026)
- HATCHLING i WHELP jako małe smoki: duża głowa, duże oczy ze źrenicą, krótki pysk, widoczne pąki skrzydeł; pisklę
  ma kawałki skorupki, WHELP jest większy i ma małe rogi. FIRE DRAKE ma płomienny grzbiet i żarzący się brzuch
  i pierś (Neon). Parametry `oczy`, `pysk`, `skorupka`, `plomien`, `zar` są w `formy_smok[].smok`.
- Skrzydła: większe, z kontrastową błoną, w spoczynku półuniesione; w zrywie i szybowaniu rozłożone.
- Start: pisklę wykluwa się z jajka w legowisku (2,6 s, ruch pomija), potem zwykła pierwsza minuta.
- Obrazy strony gry: `testy/obrazy_gry.py --studio <id>` renderuje w Studio z własnych modeli ikonę 512 × 512 i dwie
  miniatury 1920 × 1080 (tytuł nanosi PIL). Pliki trafiają do `%TEMP%\ewolucja_demo\`, podglądy do `klatki/20–22`.

## Walka (walka1, 22.11.2026)
Jedna zasada dla wszystkich (gracz, dziki smok, boss) — liczby w `ustawienia.json` → `walka`, `zdolnosci`, `wyspa`, `boss`.
- **Życie** według stadium (`hp_baza × hp_wzrost^(stadium−1)`; boss: `boss.stopnie_hp`). **BITE** zadaje
  `gryz_baza × gryz_wzrost^(stadium−1) × Szczęka × cios łańcucha × rozmiar`; rozmiar zależy od różnicy stadiów
  (`rozmiar_x`: −3…+3). Zero życia = zjedzony z chrupnięciem na koniec: zjadający rośnie, zjedzony gracz spada
  o stadium. Kulki leczą (`kulka_leczy`), bez ran regeneracja. Połykania dotykiem już nie ma — wszyscy się odbijają.
  Stadia 1–2 graczy chronione przed graczami w obie strony; w legowisku nikt nie rani i nikogo; atak zdejmuje tarczę.
- **Przyciski** (4): BITE, DASH, FIRE, POWER. BITE to łańcuch trzech ciosów (snap, snap, chomp): trzeci odrzuca
  i przewraca na chwilę; lekkie celowanie (najpierw cel przed pyskiem). Linie zdolności ewoluują:
  FIRE: EMBER SPIT (2, pocisk) → FIRE BREATH (4, kanał sterowany ruchem) → INFERNO BREATH (7, szerzej, płonąca ziemia);
  POWER: TAIL SWEEP (3, krąg 360°, odrzut) → WING GLIDE (5, szybowanie nad mniejszymi i nad lawą) → ROAR (6, mniejsze
  boty uciekają, reszta ogłuszona) → METEOR DIVE (8, skok i wybuch). Każda ma widoczny zamach (pozy, żar w pysku,
  krąg zasięgu na ziemi); przewrót w zamachu go przerywa. Zamknięta linia: ciemny przycisk „at <STADIUM>”; następna
  wersja: ciemna sylwetka nad przyciskiem. Klawisze: Spacja/klik BITE, Shift DASH, E FIRE, Q/R POWER; pad A/B/X/R1.
- **SKY NEST**: wyspa w fosie lawy na łące (−36, −42) z wielkimi kulkami — tylko WING GLIDE albo METEOR DIVE.
- **Odczucie trafienia**: liczby ran (kryt złoty), błysk trafionego (Highlight), zatrzymanie klatki 40–140 ms
  i wstrząs według siły ciosu (gdy dotyczy mnie), paski życia nad zranionymi, własny pasek HP pod paskiem wzrostu,
  spowolnienie 0,7 s przy zjedzeniu gracza, dźwięki z arkusza (cios, kryt, złapanie, plusk, trzęsienie, boss).
- **Boty** walczą tymi samymi zasadami: łańcuch BITE, zdolności swojego stadium (bez szybowania) z tym samym zamachem,
  odwet na tym, kto je ranił (do stadium większego), ucieczka przed rykiem.
- **Modele z Blendera**: efekty zaczepione w nazwanych punktach — `Pysk`, `Ogon`, `SkrzydloL`, `SkrzydloP`, `Brzuch`
  (Attachment albo Bone o tej nazwie w modelu ze szkieletem; w smokach z generatora atrybut `Kotwica_<Nazwa>`).
  Opcjonalne klipy w danych formy: `anim.chod`, `anim.gryz`, `anim.ogien`, `anim.moc`, `anim.przewrot`.
- **Sieć**: migawka 18 bajtów na byt (+ życie u8, akcja u8: zdolność, zamach, kanał, przewrót); FIRE/POWER przez
  `Akcja("umiejetnosc", "ogien"|"moc")`, serwer sprawdza typ, stan, odnowę i wiadro.
- **Symulacja** (`testy/walka_sim.py`, prawdziwa logika w interpreterze, model gracza: gryzie od razu, gdy cel
  w zasięgu, z opóźnieniem 0–0,35 s): wyniki w raporcie etapu; testy `test_26–28` pilnują progów (równe stadia 4–6 s,
  o stadium większy wygrywa 10–15 z 16, o dwa — 1–2 ugryzienia, każda zdolność 0,45–2 × BITE).
- Wyniki symulacji (40 pojedynków na parę, 6 walk z bossem na stopień): równe stadia 4,7–5,2 s; o stadium większy
  wygrywa 85% (cel „ok. 3 z 4”; przy tym modelu gracza wynik prawie nie zależy od wzrostu na stadium — decyduje kto
  zaczyna i krytyki); o dwa stadia większy zabija w 2 ugryzieniach; boss stopnie 1–5 solo (stadium 3 + stopień,
  Szczęka = stopień): 6/6 wygranych, 11–23 s, gracz kończy z 35–51% życia. Zdolności względem samego BITE: EMBER ×0,66,
  BREATH ×0,74, INFERNO ×1,56 (z płonącą ziemią), TAIL ×0,62, GLIDE ×0,59, ROAR ×0,58, METEOR ×0,70 (jeden cel;
  ogień, ogon, ryk i meteor trafiają wielu).
- Zrzuty: `klatki/14_walka_gryzienie.jpg`, `15_ogien.jpg`, `16_moc.jpg`, `17_telefon_walka.jpg`; film
  `%TEMP%\ewolucja_demo\ewolucja_walka.mp4` (poza repo).

## Świat (swiat1, 22.11.2026)
Mapa z `modele/dane/mapa_propozycja.json` (tylko odczyt) przez `swiat_mapa.py`; ustawienia `ustawienia.json → swiat`.
- **Budowa** (`zbuduj.py`, krok SWIAT): rekwizyty jako zakotwiczone bryły w `Scena/Swiat/<strefa>` (łąka, las, woda, lawa,
  znaki, legowiska z modelami `legowisko_krag_<n>`, `legowisko_brama_<n>`, `sztandar_<n>`), płaty ziemi, stawy (Glass
  3E8FD8). W scenie z dawnej łąki zostają tylko brama lasu (płot chowany przez klienta) i fosa wyspy. Razem ok. 4080
  części statycznych (rekwizyty 3468, płaty i woda 101).
- **Zmiany względem propozycji**: wyspa lawy z propozycji leży za łąką w jeziorze (−250, 70) — szybowanie (34 st.) nie
  przeleci 68 st. wody, więc jej bazalt, skały lawy i ołtarz kul stoją na wyspie gry SKY NEST (−36, −42) w fosie lawy
  (× 0,55); jeziora nie ma; mały staw przesunięty o (−4, −4) od fosy; nic nie stoi na wyspie i w fosie. Fosa ciemniejsza
  (C2410F), bo pomarańcz Neon z bloomem świecił na biało. Boss to KNIGHT GOLEM (nazwa w HUD).
- **Kolizje**: blokują głazy, pnie drzew i sosen, trzon wielkiego grzyba, filary ruin, kłody, nogi łuku korzeni, menhiry
  kamiennego kręgu, czaszka smoka, posąg, ołtarz, 11 skał kręgu każdego legowiska i 2 filary bramy (wejście od łąki
  wolne) — koła w `D.przeszkody` (233) z siatką komórek 24 st. (`przSiatka`) w `L.ogranicz`. Trawa, kwiaty, krzaki,
  kamyki, grzybki, lilie, trzcina, drogowskazy i sztandary — bez kolizji. Boty rodzą się poza przeszkodami i legowiskami
  i trzymają się 8 st. dalej od legowisk niż ich promień (wejście i kulki startowe zostają dla graczy). Autopilot prób
  wychodzi z legowiska wejściem.
- **Światło i niebo** ustawia klient w czasie gry (moduł `SwiatKlienta`, lokalnie; liczby z modele/README): Atmosphere,
  Sky, chmury, Bloom, ColorCorrection, SunRays; nastrój stref: las (gęściej, zielono, ciemniej), wyspa lawy (pomarańcz).
  `Technology` (Future) nie da się ustawić skryptem — zostaje z miejsca. Wyjątek w kontroli Luau (`zakazane Lighting`)
  tylko dla `SwiatKlienta`, jawnie w `zbuduj.py`.
- **Światło PointLight** tylko w zaczepach żaru własnego smoka (inne smoki: żar bez światła).
- **Owce**: 4 stadka po 3 na łące; pasą się, uciekają przed smokami (16 st.), zjedzone dotykiem przez gracza dowolnego
  stadium albo boty do stadium 3 dają +5 wzrostu (× Apetyt) i 6% życia; wracają po 25 s. Klipy: spoczynek, chod,
  ucieczka, zjedzona. Migawka: owce po bytach (11 bajtów na owcę).
- **Kule** z modeli danych (kula_mala / duza / wielka), unoszą się tylko blisko gracza. Kopiec złota legowiska:
  `stos_zlota_1–3`. Sztandar legowiska w kolorze właściciela (`swiat.kolory_legowisk`, kolor miejsca).
- **Poprawki**: miniatury drabiny i panelu w pozie cokołu (WorldModel w ViewportFrame), przenikanie 0,25 s przy zmianie
  pełny ↔ uproszczony rig, stożek ognia jako bryła (7 kul Neon wzdłuż stożka + cząsteczki zamiast płaskich Beamów).

## Smoki z Blendera (smok-blender1, 22.11.2026)
Zestaw `"zestaw": "blender"` (domyślny; `smok` = dawny generator części, `potwory` = Pet Arena — jedna wartość
w `ustawienia.json`). Dane tylko do odczytu z `modele/dane/` (format /2, opis: `modele/README.md`).
- **Budowa** (`zbuduj.py`, krok RIGI po pełnej budowie, 9 wywołań): z `<id>_rig.json` i `<id>_lod_rig.json` powstają w
  `Wzorce` modele `SmokB_1…8` (74–92 części + 26 kości) i `SmokB_1…8_lod` (35 + 26), `SmokB_jajo`, rekwizyty
  `Rekwizyt_cokol|gniazdo|skarb_1–3`, `Stwor_golem_1–5`, `Stwor_owca`. Kość = niewidzialna część, `Motor6D` w dziecku,
  bryły na `WeldConstraint` z atrybutem `Region`, 13 zaczepów na kościach; korzeń `Korzen` zakotwiczony, punkt modelu
  na ziemi. Klipy jako `StringValue` (JSON) w `Wzorce/Klipy/<id>`. Tablica DEEP WOODS dostaje sylwetki po rigach.
- **Odtwarzanie** po stronie klienta, bez Animatora i bez wgrań: `KlipyEwolucji` (czyste liczby: próbka, mieszanie kątów
  najkrótszą drogą, zdarzenia, tempo z `predkosc`), `RigiEwolucji` (pętla z przenikaniem 0,18 s + akcja na wierzchu,
  `Motor6D.Transform`), `SmokiKlienta` (klony, warianty, koszt, efekty, golem), `LegowiskaKlienta` (cokoły, trofea,
  gniazdo, skarb).
- **Stany → klipy**: spoczynek / chod / bieg z prędkości (tempo `v / predkosc`, granice 0,55–2,4); BITE gryz1–3
  (ugryzienie 0,08 s po naciśnięciu); EMBER `splun`; BREATH/INFERNO `ogien_start` → `ogien_petla` → `ogien_koniec`;
  TAIL `ogon_zamach`; ROAR `ryk`; GLIDE `szybowanie_start` → `_petla` → `_ladowanie`; METEOR `nurkowanie_skok` →
  `nurkowanie_ladowanie`; trafienie `trafienie`, przewrót `koziolek`, zjedzenie `pozarcie`, ewolucja `radosc`,
  start `wyklucie` (z jajem `smok_jajo`), trofea na cokołach `cokol` (poza nieruchoma). Zamach zdolności na serwerze =
  chwila zdarzenia w klipie stadium (`formy[f].czasy`, z `dane.py`), więc rana, sygnał i ruch wypadają razem.
- **Koszt** (`blender.lod`): własny smok — pełny rig co klatkę; inni gracze pełny do 90 st., boty do 45 st.; dalej
  uproszczony; animacja co 2 klatki blisko, co 4 dalej, co 12 poza kadrem / ponad 170 st. (histereza 8 st.).
- **Efekty z zaczepów**: żar (cząsteczki na `Zar1–3`) i światło (`Gardlo` / `Piers`) rosną ze stadium; ślady ogona
  i skrzydeł w zrywie i locie; stożek ognia: trzy `Beam` od `PyskAttachment` + cząsteczki (INFERNO różowo-pomarańczowy).
- **Warianty**: przemalowanie regionów (`blender.warianty`: cialo, luski, brzuch, blona, kolce, zar, zar_rdzen; oko
  i stałe zostają). **Korona** Olbrzyma nad `GlowaAttachment`, rozmiar głowy (koniec żółtego bloku).
- **KNIGHT GOLEM** zamiast węża: rig stopnia 1–5, klipy spoczynek/chod/zamach/zachwianie/upadek; serwer czeka
  `boss.zamach_s` (= „uderzenie” w klipie „zamach”, 0,6 s) przed ciosem, krąg zasięgu na ziemi. Owcy nie ma w grze
  (wymaga nowego rodzaju stworka na serwerze — poza budżetem).
- **Niezgodności z umową danych**: `indeks.json → stadia` zawiera też `smok_jajo` (pomijamy); `predkosc` biegu
  maluchów (2,78 st./s pisklęcia) a prędkość gry 16 st./s — tempo przycięte do 2,4×, stopy stadiów 1–4 ślizgają się;
  `koziolek` trwa 1,2 s, przewrót w grze 0,5 s — grany szybciej; jajo ma korzeń przesunięty w Z (−0,19).
- `tempo.py` liczy już zasady walki1 (życie, łańcuch, bez połykania dotykiem). Tempo (6 prób, mediana): forma 2 0:21,
  forma 3 1:10, forma 5 6:08, ANCIENT 14:55 (5/6 doszło), 1. ulepszenie 1:38, 1. pościg 1:59 — w celach; najdłuższa
  przerwa bez nowości 2:51 (cel ≤ 2:30, wcześniej 2:18) — liczb wzrostu nie zmieniałem (przekroczenie niewielkie).
- Wyniki: testy offline 30 (29 OK + 1 pominięty: stary generator części), Play P01–P30, telefon T1–T7; zrzuty
  `01_start` (wyklucie w gnieździe), `02_jedzenie`, `09_legowisko_swiat` (cokoły z trofeami), `12_olbrzym` (stadium 8,
  korona), `14`–`16` walka, `18_szybowanie`, `06`/`17` telefon; film `%TEMP%\ewolucja_demo\ewolucja_smok_blender.mp4`.

## Pomiar prób z graczami (D-128, 22.11.2026)
- **AnalyticsService** (tylko serwer opublikowanej gry; w Studio wywołania pomijamy):
  - lejek startu: Spawned → FirstOrb → FirstEvolve → HoardCollected → FirstUpgrade;
  - lejek stadiów `DragonStages` (sesja = losowy id);
  - ekonomia `Gold`: źródła hoard i boss_chest, wydatki upgrade_* i trophy_*;
  - zdarzenia `Death` (stadium), `BossTierBeaten`, `VariantRolled` (wariant, stadium).
  - Według dokumentacji wykresy agregują się dziennie, do 24 h. Pełne wskaźniki pulpitu wymagają ponad 10 DAU i 10 h
    gry przez 7 kolejnych dni (`production/analytics/analytics-dashboard`), więc przy ok. 10 graczach mogą się nie
    pokazać.
- **Własny, anonimowy zapis**: na koniec sesji jedno podsumowanie w magazynie `Ewolucja_Proby_v1`, klucz
  `RRRR-MM-DD_<losowy id>`. Bez id i nazwy gracza; „nowy” i „dni od pierwszej gry” pochodzą z jego zapisu (pole
  `pierwszy`). Limit: 60 zapisów na serwer i 900 znaków na rekord. W Studio i przy znaczniku próby magazyn jest tylko
  w pamięci.
- **Odczyt**: `testy/odczyt_prob.py` (`--fixtury`, `--play`, albo prawdziwy magazyn `--studio <id> --od --do`) drukuje
  tabelę D-128. Prawdziwy magazyn Studio przeczyta tylko po włączeniu przez człowieka Game Settings → Security →
  „Enable Studio Access to API Services” (skrypt tylko czyta). Nie przetestowane na prawdziwym magazynie.

## Czego nie ma (etap 4 i dalej)
Dźwięki poza arkuszem Pet Areny, modele z Blendera z klipami (podpięcie przez dane — patrz Walka), tempo po walce1. Prawdziwego dotyku nie da się wywołać z prób — drążek i przyciski
sprawdza wejście prób (to samo co palec po stronie logiki); dotyk trzeba potwierdzić na telefonie.
