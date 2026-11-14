---
status: propozycja
tags: [postacie, bohater, model-3d]
źródło: "swiat/postacie/zwiadowca.py (model z Blendera, 14.11.2026)"
---
# Zwiadowca

Druga klasa gracza obok [[Rycerz|Rycerza]] i maga ([[Kot-Mag]]): zwinny leśny zwiadowca, styl walki „unik i krytyk” (klasa i umiejętności: [[Walka v2 — silnik, klasy i umiejętności]]). Model 3D jest **propozycją** do oceny — nie ma go jeszcze w Roblox.

## Wygląd
- Zielony kaptur z szpicem nad czołem i spiczastym końcem odchylonym do tyłu, krótka peleryna z brzegiem ciętym w liście.
- Lekki skórzany kirys z pasem kołczanu na skos, kołczan na plecach z pomarańczowymi lotkami, wysokie buty z wywiniętą cholewą.
- Pogodna, bystra twarz: duże oczy z błyskami, jedna brew uniesiona, otwarty uśmiech, rumieńce.
- Paleta: dwie zielenie lasu, trzy brązy skóry, drewno łuku; jedyny jasny akcent to pomarańczowa chusta i lotki.

## Wymiary
- Wzrost 5,76 studa (Rycerz 5,71) — te same klocki R15 co Rycerz, więc pasują te same zaczepy ekwipunku.
- 4198 trójkątów w 17 siatkach (w eksporcie 3602), 17 kości R15, ostrzeżeń w raporcie brak.
- Broń to dwa osobne przedmioty: łuk (3,3 studa) na `LeftGripAttachment`, sztylet (2,4 studa) na `RightGripAttachment`.

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2 s) — gotowość na ugiętych kolanach, oddech.
- `ruch` (pętla 0,67 s) — lekki bieg w miejscu.
- `atak` (0,93 s) — zamach sztyletem za biodro, wypad i pchnięcie, trafienie w kl. 11.
- `umiejetnosc` (1,8 s) — zatruta strzała: lewym barkiem do celu, łuk na wysokości barku, naciąg z łokciem w tył, wypuszczenie w kl. 31.
- `uderzenie_z_gory` (1,53 s) — druga umiejętność: wyskok ze sztyletem nad barkiem i cios w dół przy lądowaniu (kl. 20).
- `trafienie` (0,67 s) — szarpnięcie w tył i powrót.
- `unik` (1,33 s) — znak klasy: boczne salto w lewo i odskok z powrotem.
- `upadek` (2 s) — chwieje się, pada na kolana i twarzą w dół; ostatnia klatka to leżenie.
- `wiwat` (pętla 1,6 s) — podskoki, łuk i pięść ze sztyletem w górze.

## Pliki
- Moduł: `swiat/postacie/zwiadowca.py`
- Wynik: `swiat/postacie/wynik/zwiadowca/` (FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, filmy, arkusze klatek, `raport.txt`); broń w `przedmioty/`.

## Znane słabości
- Import do Roblox Studio nie był testowany.
- Strzał to sam ruch: łuk się nie ugina, nie ma strzały ani smugi trucizny (efekt do dorobienia w grze). Najlepiej czyta się z boku i z tyłu; od przodu pięść z łukiem zasłania dół twarzy.
- Ręce R15 są za krótkie, żeby dłoń sięgnęła twarzy — naciąg kończy się przy barku.
- Unik i uderzenie z góry przesuwają postać w samym klipie (salto ok. 3,25 studa w bok i powrót).
- Kaptur i peleryna nie falują, twarz bez mimiki; w filmach postać jest mała w kadrze (kadr obejmuje salto).
- Pełna lista: `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
