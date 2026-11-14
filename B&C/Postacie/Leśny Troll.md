---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/lesny_troll.py (model z Blendera, 14.11.2026)"
---
# Leśny Troll

Rzadki, ciężki przeciwnik lasu w walce (statystyki i umiejętność: [[Walka v2 — silnik, klasy i umiejętności]]). Model 3D jest **propozycją** do oceny — nie ma go jeszcze w Roblox.

## Wygląd
- Ogromny, przygarbiony troll z kory: krótkie grube nogi, wielki pochylony tułów z garbem, bardzo długie ręce z pięściami przy kolanach.
- Mała głowa wciśnięta w barki, ciężkie brwi, kartoflany nos, wielka wysunięta żuchwa z dwoma kłami.
- Poduchy mchu na garbie, barkach i plecach, czerwone grzyby z kremowymi kropkami (jedyny mocny akcent koloru), przepaska z liści.
- W prawej ręce maczuga z wyrwanego pnia z bryłą korzeni; w spoczynku korzenie leżą na ziemi z prawej strony, w chodzie wlecze ją za sobą.

## Wymiary
- Wzrost ok. 9,9 studa razem z grzybami (gracz ma 5,7); szerokość z maczugą leżącą z boku 12,7, sam troll ok. 7,8.
- 7778 trójkątów (największa siatka, tułów, ok. 2400; limit Roblox 20 000 na siatkę), 18 własnych kości (nie R15), maczuga jest kością modelu.

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2,4 s) — ciężki oddech, rozgląda się, żuje.
- `ruch` (pętla 1,6 s) — powolny chód w miejscu, maczuga wleczona za sobą.
- `atak` (1,2 s) — pień zarzucony na bark, płaski łuk przed sobą, trafienie w kl. 16.
- `umiejetnosc` (2 s) — ogłuszające uderzenie: maczuga znad głowy w ziemię przed sobą (kl. 29), przysiad, powolne wstawanie.
- `trafienie` (0,67 s) — szarpnięcie w tył i powrót.
- `unik` (1 s) — ciężki odskok w bok i powrót.
- `upadek` (2 s) — chwieje się, siada i pada na plecy; ostatnia klatka to leżenie.
- `ryk` (pętla 2 s) — po wygranej: paszcza otwarta, maczuga i pięść w górze.

## Pliki
- Moduł: `swiat/postacie/lesny_troll.py`
- Wynik: `swiat/postacie/wynik/lesny_troll/` (FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, filmy, arkusze klatek, `raport.txt`).
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (nad garbem), `PyskAttachment`, `MaczugaAttachment` (miejsce na falę uderzenia).

## Znane słabości
- Import do Roblox Studio nie był testowany; własny szkielet zamiast R15.
- W filmach troll jest mały w kadrze (kadr obejmuje cały zasięg maczugi ze wszystkich klipów).
- Chód w miejscu, stopy się ślizgają; twarz bez mimiki poza żuchwą.
- Ogłuszające uderzenie to sam ruch — fala, kurz i gwiazdki do dorobienia w grze.
- Pełna lista: `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
