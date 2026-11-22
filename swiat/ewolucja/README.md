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
python -B swiat/ewolucja/testy/test_ewolucji.py          # logika bez Studio (12 testów)
python -B swiat/ewolucja/tempo.py [--prob 8]             # symulacja tempa „sprawnego gracza”
python -B swiat/ewolucja/zbuduj.py --studio <id>         # budowa (--sucho, --skrypty, --stan, --usun, --publikacja)
python -B swiat/ewolucja/zbuduj.py --wlacz on|off --studio <id>     # wyłącznik EwolucjaWlaczona
python -B swiat/ewolucja/testy/proba_play.py --studio <id>          # próba Play (13 punktów, zrzuty do klatki/)
python -B swiat/ewolucja/testy/proba_telefon.py --studio <id>       # Device Simulator: najmniejszy telefon, układ HUD
```
Przed próbą Play inne gry wyłączone: `swiat/pet_arena/zbuduj.py --wlacz off`, `swiat/zabawki/zbuduj.py --wlacz off`.

## Wyniki (22.11.2026)
- Testy logiki 12/12. Play 13/13, telefon (Samsung Galaxy A06, 705 × 338) 6/6, konsola bez błędów, klatka 16,7 ms.
- Tempo (symulacja, 8 prób, mediana): forma 2 0:26, forma 3 1:12, 1. ulepszenie 1:32, 1. pościg 1:23, forma 5 6:30,
  Olbrzym 13:49. W Play autopilot: pierwszy pełny pasek 19–36 s, druga ewolucja 52–61 s po pierwszej.
- Opóźnienie 2 × 60 ms: własny potwór przesunięty o 2,7 st po 0,15 s, 0 poprawek serwera, BITE gra w tej samej klatce.
- Zrzuty: `klatki/01_start.jpg`, `02_jedzenie.jpg`, `03_odslona.jpg`, `04_legowisko.jpg`, `05_pogon.jpg`, `06_telefon.jpg`.

## Czego nie ma (etap 2 i dalej)
Legowisko jako miejsce w świecie, złoto pod nieobecność, zapis postępu, odmiany barwne, Olbrzym jako boss serwera,
umiejętności botów, dźwięki poza arkuszem Pet Areny. Prawdziwego dotyku nie da się wywołać z prób — drążek i przyciski
sprawdza wejście prób (to samo co palec po stronie logiki); dotyk trzeba potwierdzić na telefonie.
