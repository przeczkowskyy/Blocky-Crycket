---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/cierniowy_wilk.py (model z Blendera, 14.11.2026)"
---
# Cierniowy Wilk

Zwykły, szybki przeciwnik lasu w walce. Jego umiejętność to rozszarpanie (statystyki: [[Walka v2 — silnik, klasy i umiejętności]]). Rzadszy i cięższy przeciwnik lasu to [[Leśny Troll]]. Model 3D jest **propozycją** do oceny i nie ma go jeszcze w Roblox.

## Wygląd
- Chudy, kanciasty wilk o długich łapach, z głęboką klatką piersiową i wciętą talią. Duża głowa jest wysunięta nisko do przodu, ma długi pysk z kłami na zewnątrz i wysokie, spiczaste uszy.
- Futro jest łupkowo-granatowe w trzech odcieniach, a na karku ma zjeżoną grzywę. Na grzbiecie jasne kolce jeżyny przeplatają się z ciemnymi kępkami sierści, a wokół klatki, zadu i szyi oplatają go zielone pędy.
- Ogon trzyma poziomo. Kończy się gęstwiną pędów z kolcami i listkami, jak zarośla.
- Twarz ma ciężkie brwi w kształcie V i świecące bursztynowe oczy z pionową źrenicą. To jedyny mocny akcent koloru na modelu.

## Wymiary
- W kłębie ok. 3 study, a z uszami 4,4. Pies-pet ma w kłębie 2,2, a gracz 5,7 wzrostu. Długość od nosa do końca ogona to 7,7 studa.
- Model ma 4470 trójkątów w 21 siatkach (największa ok. 820, a limit Roblox to 20 000 na siatkę). Szkielet ma 22 kości: Root i 21 własnych (to nie R15).

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2,4 s): oddycha, rozgląda się z nisko opuszczonym łbem, warczy i raz mruga.
- `ruch` (pętla 0,53 s): galop w miejscu, z łapami wyciąganymi daleko do przodu i do tyłu.
- `atak` (0,9 s): przysiad, szeroko otwarta paszcza, wypad i kłapnięcie w kl. 13, szarpnięcie łbem i powrót.
- `umiejetnosc` (1,8 s): rozszarpanie. Wilk skacze, w locie dwa razy kłapie (kl. 17 i 23), a po wylądowaniu 2,4 studa dalej szarpie łbem i odskakuje na miejsce.
- `trafienie` (0,6 s): szarpnięcie w tył ze skowytem i powrót.
- `unik` (0,93 s): odskok w lewo i powrót.
- `upadek` (1,9 s): chwieje się, pada na pierś i przewraca na prawy bok. Ostatnia klatka to leżenie z opadłymi łapami i zamkniętymi oczami.
- `ryk` (pętla 2 s): wycie po wygranej, z łbem zadartym do nieba.

## Pliki
- Moduł: `swiat/postacie/cierniowy_wilk.py`
- Wynik: `swiat/postacie/wynik/cierniowy_wilk/`. Są tam: FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, ikona, filmy, arkusze klatek i `raport.txt`.
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (tabliczka nad głową) i `PyskAttachment` (miejsce na efekt ugryzienia lub krwawienia).

## Znane słabości
- Importu do Roblox Studio nie testowaliśmy. Szkielet jest własny, nie R15.
- Galop i pozostałe klipy dzieją się w miejscu, więc łapy ślizgają się po ziemi. Rozszarpanie przesuwa wilka o 2,4 studa do przodu, co trzeba zgrać z odległością od celu w walce.
- Oczy świecą tylko w teksturze. W grze trzeba dodać Neon albo PointLight. Krwawienia, kurzu ani śladów pazurów nie ma.
- Kolce, pędy i ogon-zarośla są sztywne i nie kołyszą się w biegu.
- Pełna lista jest w `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[Pety]]
- [[00 Start]]
