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
- **Stany → klipy**: spoczynek / chod / bieg z prędkości (od danych 3: patrz „Dane 3 i interfejs”); BITE gryz1–3
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
- **Niezgodności z umową danych (wersja 2, usunięte w wersji 3)**: jajo w `stadia`, `predkosc` maluchów niezgodna
  z prędkością gry, długi `koziolek`; nadal: jajo ma korzeń przesunięty w Z (−0,19).
- `tempo.py` liczy już zasady walki1 (życie, łańcuch, bez połykania dotykiem). Tempo (6 prób, mediana): forma 2 0:21,
  forma 3 1:10, forma 5 6:08, ANCIENT 14:55 (5/6 doszło), 1. ulepszenie 1:38, 1. pościg 1:59 — w celach; najdłuższa
  przerwa bez nowości 2:51 (cel ≤ 2:30, wcześniej 2:18) — liczb wzrostu nie zmieniałem (przekroczenie niewielkie).
- Wyniki: testy offline 30 (29 OK + 1 pominięty: stary generator części), Play P01–P30, telefon T1–T7; zrzuty
  `01_start` (wyklucie w gnieździe), `02_jedzenie`, `09_legowisko_swiat` (cokoły z trofeami), `12_olbrzym` (stadium 8,
  korona), `14`–`16` walka, `18_szybowanie`, `06`/`17` telefon; film `%TEMP%\ewolucja_demo\ewolucja_smok_blender.mp4`.

## Dane 3 i interfejs (interfejs1, 23.11.2026)
**Dane modeli w wersji 3** (`modele/dane/indeks.json`, tylko odczyt): `stadia` = osiem stadiów, jajo pod `jajo`, nowe
`efekty`, `warianty_modeli`, `predkosc_stworow`; `dane.py` przyjmuje wersję 2 i 3.
- **Chód i bieg**: tempo = prędkość po ziemi ÷ `predkosc` klipu (chód 7, bieg 18 st./s w każdym stadium), granice
  0,1–3,0; chód ↔ bieg przy środku geometrycznym (≈ 11,2 st./s) z histerezą 1,5 (`blender.lod.bieg_hist`), przenikanie
  pętli 0,18 s z zachowaną fazą (`KlipyEwolucji.chodBieg`). Owca (chód 1,76 / ucieczka 5,0) i golem (6,5–8,5) — swoje
  `predkosc`. Kamera i pole trafienia na korzeniu.
- **Przewrót**: krótki `koziolek` (14 klatek) w tempie 1, ostatnia poza trzymana do końca przewrotu (0,5 s);
  `koziolek_dlugi` dla przewrotów od 0,9 s (serwer podaje czas przewrotu w zdarzeniu `rana.pw`).
- **Ogień**: rig `Efekt_ogien_stozek` przypięty do `PyskAttachment` (przód −Z), skala = zasięg ÷ 10, klip `migotanie`
  w pętli, lekko pochylony ku ziemi, plus żar z pyska; dawne kule Neon zostają tylko jako zapas bez wzorca (rig czyta się
  z kamery gry wyraźniej). INFERNO: `Rekwizyt_przypalenie` w skali promień ÷ 10 na wysokości ziemi (promień w dół),
  pulsuje i gaśnie, płomyki z `E:plama` bez dawnego krążka.
- **Portrety** (drabina, panel, odsłona, góra ekranu): poza `portret`, kamera z przodu po lewej (¾), popiersie z zaczepów
  `Glowa`/`Piers`; trofea na cokołach w świecie dalej w pozie `cokol`.
- **Pisklę**: `blender.piskle` = `"obecne"` (domyślnie) albo `"lagodne"` (`smok_1_lagodny_rig.json`) — wybór ludzi.

**Interfejs z makiet** (moduł `InterfejsKlienta`, przewodnik stylu z `modele/README.md`; wzór 844 × 390 pt, skala
min(szer./844, wys./390) w granicach 0,6–1,8):
- góra na środku: portret obecnego stadium w kole z pierścieniem żaru (żywy rig w ViewportFrame), nazwa, `STAGE n / 8`,
  pasek wzrostu 288 × 18 z gradientem żaru, następne stadium jako czarna sylwetka z „?”, pasek życia; obok dwie pigułki
  (złoto; skarb legowiska z dochodem /s) — razem przycisk legowiska. Górne rogi puste (≥ 146 pt od prawej);
- drabina przy lewej krawędzi: zdobyte stadia — portrety, następne — sylwetka, dalsze — „?”, obecne 36 pt z pierścieniem
  żaru i nazwą;
- przyciski: BITE 103 pt (#FFF6E0), DASH / FIRE / POWER 68 pt (#60C8DC, #E84C2C, #3A80EA), wewnętrzny pierścień, połysk,
  cień; wciśnięcie 0,92 i 15% ciemniej; odnowa — ciemny wycinek od godziny 12 (dwie połówki z UIGradient o twardej
  krawędzi) z sekundami i błyskiem żaru na końcu; zamknięta linia — płytka #463C58 z kłódką; pigułki
  „<ZDOLNOŚĆ> at <STADIUM>” nad przyciskami; lewy dół wolny dla drążka;
- panel legowiska (697 × 345 pt): karty trofeów 4 × 2 (portret, poziomy, dochód, odznaka wariantu, cena poziomu —
  dotknięcie karty kupuje; zamknięte: sylwetka, „???”, kłódka), kolumna ulepszeń z paskiem i ceną, zakładka UPGRADES
  z dużymi kartami, linia szans wariantów, korona z trofeami bossa, złoto, X; pola dotyku ≥ 54 pt wzoru (≥ 44 pt na A06);
- odsłona: kokon (poświata) → EVOLVED! + nazwa, portret nowego stadium, NEW POWER z opisem (bez nowej mocy: dochód
  trofeum) → sylwetka następnego (NEXT) → CONTINUE; zamyka się sama po 3,4 s (`ui.odslona_s`) albo przyciskiem.
- **Ikony**: tabela numerów obrazów **`ustawienia.json → "ikony" → "id"`** (24 nazwy z `modele/README.md`, wszystkie 0 =
  nie wgrano; w grze `D.ikony`). Wybór w `zrodla/IkonyEwolucji.luau`: numer > 0 → obraz `rbxassetid://…`; inaczej
  zastępstwo — model 3D z wzorców (kule `Rekwizyt_kula_*`, kopiec `Rekwizyt_stos_zlota_1`), moneta i korona z części,
  kłódka i romby wariantów rysowane, reszta krótki napis na płytce (BITE, DASH, EMBER, BREATH, INFERNO, TAIL, GLIDE,
  ROAR, METEOR, JAW, SPEED, EAT). Zdolności, warianty i ulepszenia mają pole `ikona`. Po wgraniu: wpisać numery,
  przebudować (`zbuduj.py`) — bez zmian w kodzie. Podpis pod przyciskiem pojawia się dopiero przy obrazie.
- **Czcionki** (sprawdzone w Studio jako `Enum.Font`): tytuły, nazwy i liczby `FredokaOne`, etykiety i pigułki
  `BuilderSansExtraBold` (`ui.czcionka`, `ui.czcionka_cyfr`, `ui.czcionka_etykiet`).
- **Poślizg stóp** (P40, Play; pozycja stopy z łańcucha stawów tej klatki, podpora = dolne 0,03 st. nad ziemią pod
  korzeniem, mediana prędkości poziomej): bieg stadium 2 — 0,19–0,45 st./s, stadium 3 — 0,55–1,7, stadium 4 — 0,56–1,2
  (przy 16–19 st./s); **stadium 1 — 16–23** i chód stadium 2 — 0,4–5,8. Kinematyka z samych danych (offline, te same
  próbki co 2 klatki) daje to samo: sus pisklęcia ma podporę 2 klatek, której próbkowanie co 2 klatki nie oddaje (stopa
  przy ziemi jedzie z ciałem ~19 st./s); przednie łapy w chodzie stadium 2 — 11,8. Naprawa po stronie danych: chód i bieg
  z `krok` 1 (albo podpora ≥ 3 klatek). Pomiar bywa niestabilny (stadium 2 raz 11–18 tuż po pomiarze stadium 1 — nie
  znalazłem przyczyny). Próg P40: mediana biegu stadiów 2–4 ≤ 2 st./s; stadium 1 i chód tylko zgłaszane.
- Wyniki: testy offline 34 (33 OK + 1 pominięty), nowe: `test_33` (tempo chód/bieg z prędkości, histereza, owca, golem),
  `test_34` (tabela ikon i zastępstwa); Play 42/42 (P34–P41: HUD, drabina, odnowa, kłódki, panel, odsłona, poślizg,
  ogień z rigu), telefon Samsung Galaxy A06 (705 × 338, skala 0,84) 8/8 i iPad 6 (1023 × 768, skala 1,21) 8/8; klatka
  16,7 ms, praca skryptu 3,2–3,4 ms, krok serwera 0,54 ms. Zrzuty `28_hud`, `29_panel`, `29b_panel_ulepszenia`,
  `30_odslona`, `31_ogien_rig`, `32_inferno_przypalenie`, `33_telefon_odslona`, `34_telefon_panel`, `06`/`17` telefon
  (`_tablet` — iPad); film `%TEMP%\ewolucja_demo\ewolucja_interfejs.mp4` (35 s, `demo_wideo.py --interfejs`).

## Powody, by wrócić (odrodzenie1, 23.11.2026)
Ustawienia: `ustawienia.json → odrodzenie`, `wydarzenia`, `jajo_dnia`; logika w `LogikaEwolucji` (czyste funkcje,
testy offline), serwer i klient tylko wołają.
- **REBIRTH** na ANCIENT DRAGON (przycisk EVOLVE zmienia się w REBIRTH!): ceremonia 3,2 s (smok nieruchomy i nietykalny,
  gaśnie w rosnącym jaju koloru nowej linii, nakładka „REBIRTH n / <LINIA> LINE”), potem pisklę wykluwa się z jaja nowej
  linii. Złoto, ulepszenia i legowisko zostają. Mnożnik wzrostu i złota legowiska ×1,25 za odrodzenie (najwyżej ×3,0 —
  od 5. odrodzenia). Linie po kolei: EMBER (dzisiejsze kolory) → FROST (lodowe błękity, biała poświata) → STORM (fiolet,
  elektryczna żółć) → SHADOW (czerń, karmazyn) → znów EMBER z zachowanym postępem. Te same modele, przemalowane przez
  regiony (`SmokiKlienta.barwLinii`); linia jedzie w migawce w bajcie wariantu (wariant + 8 × (linia − 1)).
- **Trofea linii**: każda linia ma swoje 8 trofeów (poziomy, warianty); trofea poprzednich linii zostają w legowisku
  i zarabiają (× mnożnik). Panel legowiska: przyciski linii EMBER / FROST / STORM / SHADOW nad kartami (inne linie —
  podgląd i dochód, zakup poziomów tylko w obecnej). W HUD na szczycie drabiny: sylwetka ANCIENT następnej linii
  w pierścieniu jej koloru i pigułka „R<n> x<mnożnik>” (przed pierwszym odrodzeniem nazwa następnej linii).
- **Zapis**: `odrodzenia`, `linia`, `linie` (postęp pozostałych linii: maxForma, warianty, poziomy) i `dzienJaja` w tym
  samym profilu (walidacja i migracja w `L.profilZ`; w Studio magazyn w pamięci).
- **DRAGON RAIN** co 20 min (pierwszy po 20 min od startu serwera) na 2 min: wszystkie kule łąki od razu żywe i złote
  (u klienta Neon, nowe spadają z nieba złotą kroplą), wracają po 2,5 s, wzrost ×3 i +2 złota za kulę.
- **GOLEM RAMPAGE** co 45 min na 3 min: KNIGHT GOLEM najwyższego stopnia osiągniętego na serwerze (stopień serwera albo
  trofea bossa gracza + 1) wychodzi bramą na łąkę, ściga graczy poza legowiskami (zasięg × 1,6); każdy, kto go trafił,
  dostaje równą część skrzyni × 2 (z jednym graczem — całą). Koniec po czasie albo po pokonaniu, golem wraca do lasu.
  Pigułka pod złotem: odliczanie do najbliższego wydarzenia albo czas trwającego; ogłoszenie banerem i dymkiem.
- **DAILY EGG**: raz na dzień UTC jajo w gnieździe własnego legowiska (świeci); przycisk DAILY EGG w legowisku wykluwa
  darmowe losowanie wariantu dla trofeum obecnego stadium (GOLD 70, CRYSTAL 22, RUBY 7, RAINBOW 1; zostaje tylko lepszy).
- **Poprawki**: liczby i napisy nad stworkami w warstwie pod całym HUD (panel i odsłona zawsze na wierzchu); własny smok
  w świecie schowany, gdy odsłona pokazuje portret; drabina większa (węzły 27 pt, obecne 38 pt, odstęp 30 pt); P05
  (druga ewolucja) i P15 (mini-boss) bez przypadku (pewna ścieżka z ponowieniem, gracz zwrócony do bossa, odnowa
  zerowana); pigułki i dymek przesunięte pod pigułkę wydarzeń.
- **Tempo** (`tempo.py`, teraz z owcami; 6 prób): przed strojeniem pierwszy ANCIENT tylko w 3/6 prób do 22 min
  (18:23–20:55), forma 5 9:07. Zmiana: `potrzeba` FIRE DRAKE 480 → 340, WAR DRAGON 4200 → 3400, ELDER DRAGON 13800 → 11500.
  Po strojeniu (6 prób, 24 min): forma 3 0:59, forma 4 3:33, forma 5 8:40, forma 6 11:21, forma 7 14:56, **pierwszy
  ANCIENT, czyli pierwsze odrodzenie: 19:31** (11:41–23:47, 6/6) — w celu 15–20 min; nadal poza celami: forma 5 (cel 6–7
  min) i najdłuższa przerwa bez nowości 3:48 (cel ≤ 2:30; stadium 4 w lesie trwa ok. 5 min) — do strojenia z ludźmi.
- Wyniki: testy offline 39 (38 OK + 1 pominięty), nowe `test_35`–`test_39` (odrodzenie i mnożnik, kolory linii i bajt
  migawki, wydarzenia zegarowe z rampage jednego gracza, jajo dnia po dniu UTC, zapis nowych pól); Play P01–P47 (P42
  REBIRTH z ceremonią i linią FROST, P43 DRAGON RAIN, P44 GOLEM RAMPAGE z jednym graczem, P45 jajo dnia, P46 wyjście
  i powrót, P47 legowisko z dwiema liniami), telefon A06 8/8, iPad 8/8; zrzuty `35_odrodzenie`, `36_frost`,
  `37_deszcz`, `38_rampage`, `39_legowisko_linie`, `40_jajo_dnia`; film `%TEMP%\ewolucja_demo\ewolucja_odrodzenie.mp4`
  (39 s, `demo_wideo.py --odrodzenie`). Próby: hak `boty_cisza` (boty bez ciosów na czas pomiarów HUD i poślizgu).

## Retencja (retencja1, 23.11.2026)
- **Stopy piskląt (dane, runda 6)**: `chod` i `bieg` wszystkich stadiów co klatkę (pole klipu `krok` 1 i okna podporu
  `podpor`; `modele/README.md`, „Runda 6”; `generuj.py krok1` bez Blendera). Gra czyta krok klipu
  (`KlipyEwolucji.probka`). Przesuw stopy w podporze: dane (`sprawdz_dane.py`) 0,000–0,060 studa; Play (P40, okna
  podporu z danych, pozycja stopy z łańcucha stawów) — zob. wyniki niżej.
- **Seria logowań** (`ustawienia.json → seria`): kalendarz 7 dni (dzień UTC); wejście dzień po dniu = następny dzień,
  przerwa = od 1, po 7. znów 1. Nagrody od razu przy wejściu, tylko waluta gry: 100 / 200 / 150 + ×2 wzrostu 5 min /
  400 / 250 + ×2 wzrostu 10 min / 800 / 1500 + losowanie wariantu najwyższego trofeum. Przyspieszenie liczone w czasie
  gry i zapisywane.
- **Zadania dnia** (`ustawienia.json → zadania`): 3 z puli 8 (owce, walki, zdolności, wyspa lawy, skarb legowiska,
  kule, ewolucje, golem; część od zdobytej formy), losowanie stałe dla (dzień UTC, gracz), reset o 00:00 UTC. Postęp ze
  zdarzeń kroku logiki (`L.krokZadan`), nagroda od razu: złoto + 15–20% potrzeby obecnego stadium. HUD: pigułka pod
  paskiem życia z pierwszym niegotowym zadaniem i licznikiem; baner QUEST DONE!. AnalyticsService: `QuestCompleted`
  (CustomField01 = id), `LoginStreakDay`, przepływy złota `quest_*` i `streak_day_*`.
- **Ekran powitania** przy każdym wejściu: WELCOME BACK! / WELCOME, DRAGON!, „DAY n STREAK”, kalendarz 7 dni
  (dzisiaj na pomarańczowo, odebrane „OK”), nagroda dnia i złoto skarbu z nieobecności, 3 zadania z paskami, CONTINUE
  (zamyka się też sam po 20 s; telefon 620 × 330 pt × skala).
- **Zapis w wersji 2**: `seria`, `zadania`, `boostS` w tym samym profilu; migracja z wersji 1 = wartości domyślne;
  walidacja w `L.profilZ`. Blokada sesji bez zmian; w Studio i próbach magazyn w pamięci.
- **Ranking**: leaderstats `Stage` i `Rebirths`; tablica TOP REBIRTHS w świecie na łące (−18, −96): globalny top 10
  odrodzeń z OrderedDataStore `Ewolucja_Odrodzenia_v1` (zapis tylko przy zmianie liczby odrodzeń, odczyt co 120 s,
  wszystko w pcall, nazwy z cache); w Studio i próbach z pamięci z nazwami „Player N”.
- **Kolory linii**: boty w liniach EMBER / FROST / STORM / SHADOW (po kolei z numeru bytu), trofea na cokołach
  w linii właściciela.
- **Wydarzenia z zegara UTC**: DRAGON RAIN, gdy (czas UTC) mod 1200 s < 120 s; GOLEM RAMPAGE, gdy (czas UTC − 600)
  mod 2700 s < 180 s (po pokonaniu golema spokój do końca cyklu) — ten sam rozkład na każdym serwerze. Próby Play
  wyłączają rozkład hakiem `wydarzenia_zegar` (zostają wymuszone).
- **Tempo** (`tempo.py` z owcami i zadaniami dnia jako nowością): `potrzeba` DRAKE 170 → 160, FIRE DRAKE 340 → 230,
  WAR DRAGON 3400 → 4500, ELDER DRAGON 11500 → 17000; wzrost z zadań 15–20% potrzeby. 12 prób, 26 min: forma 5
  **5:49** (cel ≤ 7:00), pierwszy ANCIENT = pierwsze odrodzenie **20:11** (10:58–22:40, 10/12; cel 18–22), najdłuższa
  przerwa bez nowości w 0–10 min **3:08** (2:03–7:23; cel ≤ 2:30 — niespełniony, duży rozrzut prób).
- **Błąd naprawiony przy okazji (ważny)**: w rigach z danych 7 kości smoka (Tulow, Szyja1–2, Ogon1–4) ma widoczną część
  o tej samej nazwie; `RigiEwolucji` brał `FindFirstChild(nazwa)`, a kolejność dzieci po replikacji jest dowolna —
  w części sesji tułów, szyja i ogon nie dostawały animacji (u wszystkich smoków, także cudzych i botów), stąd też
  „losowy” poślizg stóp piskląt. Teraz kość = część z Motor6D (`Rigi.kosc`); to samo dla stożka ognia, owcy i golema.
- Wyniki: testy offline 42 (41 OK + 1 pominięty; nowe `test_40` seria, `test_41` zadania, `test_42` zapis v2
  i migracja; `test_29` i `test_37` rozszerzone); `sprawdz_dane.py` 0 uwag; Play P01–P52 (nowe P48 powitanie, P49 zadania,
  P50 seria i zapis, P51 ranking i leaderstats, P52 kolory linii; P40 = przesuw stopy w podporze); telefon A06 9/9 i iPad
  9/9 (nowe T8 powitanie); zrzuty `41_powitanie`–`46_telefon_powitanie`; film
  `%TEMP%\ewolucja_demo\ewolucja_retencja.mp4` (30 s, `demo_wideo.py --retencja`; kamera z bliska: `EW_TestZoom`,
  `EW_TestKat`).

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
