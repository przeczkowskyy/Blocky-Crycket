---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/muchomornik.py (model z Blendera, 14.11.2026)"
---
# Muchomornik

Zwykły przeciwnik lasu w walce: mały, trochę śmieszny i trochę złośliwy szaman. Bije laską, a jego umiejętność to chmura zarodników, która truje magią (statystyki: [[Walka v2 — silnik, klasy i umiejętności]]). W tym samym lesie walczą [[Cierniowy Wilk]] i [[Leśny Troll]]. Model 3D jest **propozycją** do oceny i nie ma go jeszcze w Roblox.

## Wygląd
- Niski grzybowy ludek z wielkim czerwonym kapeluszem w białe kropki. Kapelusz jest szerszy niż całe ciało, przekrzywiony zawadiacko na bok i rozpoznawalny po samym kształcie.
- Kremowa głowa-trzon, brwi z mchu w złośliwe V, oczy zezujące w bok, nos-kartofel, krzywy uśmieszek z jednym zębem i zielona bródka z mchu.
- Beczkowaty tułów z białym pierścieniem pod szyją, jak u prawdziwego muchomora, spodenki z kory i drewniane chodaki na krótkich nóżkach.
- W prawej ręce trzyma krzywą laskę z korzenia ze świecącą bulwą, wokół której krążą zarodniki. Ich trująca zieleń to jedyny mocny akcent koloru.

## Wymiary
- Ok. 3,6 studa wzrostu z kapeluszem (gracz ma 5,7), kapelusz ma 2,95 studa szerokości.
- Model ma 4272 trójkąty w 28 siatkach (limit Roblox to 20 000 na siatkę). Szkielet ma 29 kości: Root i 28 własnych, w tym 13 kości zarodników (to nie R15).

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2,4 s): oddycha, rozgląda się z ukosa, kapelusz się kołysze, raz mruga.
- `ruch` (pętla 0,8 s): drobny, kołyszący chód w miejscu, laska jak kij wędrowca.
- `atak` (0,9 s): laska w górę, naciąg z kapeluszem przechylonym do tyłu i „rąbnięcie” z góry przed siebie. Trafienie w kl. 12.
- `umiejetnosc` (2 s): chmura zarodników. Uderza laską w ziemię i potrząsa kapeluszem, a 10 świecących zarodników wylatuje w górę i opada półkolem ok. 2 studów przed nim.
- `trafienie` (0,6 s): szarpnięcie w tył, kapelusz podskakuje.
- `unik` (0,9 s): podskok w lewo i powrót.
- `upadek` (2 s): zawroty, klapnięcie na pupę z obrotem w bok, przewrót na plecy. Kapelusz wylatuje w górę i zsuwa mu się na twarz. Kończy się leżeniem.
- `wiwat` (pętla 2 s): złośliwy śmiech z podskokami i laską w górze.

## Pliki
- Moduł: `swiat/postacie/muchomornik.py`
- Wynik: `swiat/postacie/wynik/muchomornik/`. Są tam: FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, ikona, filmy, arkusze klatek i `raport.txt`.
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (tabliczka nad kapeluszem), `ChmuraAttachment` (efekt chmury) i `LaskaAttachment` (świecąca bulwa laski).

## Znane słabości
- Importu do Roblox Studio nie testowaliśmy. Szkielet jest własny, nie R15.
- Chmura to 10 małych brył, bez dymu i trucizny. Trzeba dodać cząsteczki na `ChmuraAttachment`, a świecenie dać materiałem Neon albo PointLight.
- Chód jest w miejscu, a nóżki nie mają kolan. Laska z bliska trochę ślizga się w dłoni.
- W ataku widzianym od przodu laska leci w stronę kamery, a kapelusz na chwilę zasłania twarz. Z boku cios czyta się lepiej.
- Pełna lista jest w `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
