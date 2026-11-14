---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/straznik_gaju.py (model z Blendera, 14.11.2026)"
---
# Strażnik Gaju

Strażnik biomu lasu, czyli najważniejszy przeciwnik lasu w walce. Ma najwięcej życia, a jego umiejętność to uścisk korzeni, który unieruchamia (statystyki: [[Walka v2 — silnik, klasy i umiejętności]], w danych walki pod id `straznik_lasu` i nazwą „Strażnik Lasu” — która nazwa obowiązuje, jest jeszcze do decyzji). W tym samym lesie walczą [[Leśny Troll]], [[Cierniowy Wilk]] i [[Muchomornik]]. Model 3D jest **propozycją** do oceny i nie ma go jeszcze w Roblox.

## Wygląd
- Wysoki, dostojny kolos z ciepłoszarego kamienia i plecionego drewna. Tułów w kształcie odwróconego klina, wielkie głazy z mchem na barkach, długie ręce z kamiennymi pięściami.
- Zamiast stóp ma pnie, które u dołu rozchodzą się w korzenie leżące na ziemi.
- Kanciasta głowa z ciężkimi brwiami w V, świecącymi zielonymi oczami i brodą z korzonków. Na głowie korona z gałęzi z klockowymi liśćmi.
- W piersi świeci zielony kryształ w kamiennej oprawie. Ta zieleń (kryształ, oczy, żyłki) to jedyny mocny akcent koloru.

## Wymiary
- Ok. 14,5 studa wzrostu z koroną, 12,8 bez niej (gracz ma 5,7, [[Leśny Troll]] 9,9). Szerokość w barkach 8,9 studa.
- Model ma 11 168 trójkątów w 36 siatkach (największa ok. 2000, limit Roblox to 20 000 na siatkę). Szkielet ma 37 własnych kości, w tym 15 kości korzeni umiejętności (to nie R15).

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2,4 s): spokojny oddech, rozgląda się, kryształ pulsuje, raz mruga.
- `ruch` (pętla 2 s): powolny, ciężki chód w miejscu.
- `atak` (1,4 s): pięść w górze na zewnątrz prawego barku, potem młot z góry przed siebie z wykrokiem. Trafienie w kl. 17, ok. 5 studów przed nim.
- `umiejetnosc` (3 s): uścisk korzeni. Ryczy z pięściami w górze, wbija je w ziemię, a ok. 6,6 studa przed nim wyrasta pięć korzeni, które zaginają się jak palce i zaciskają (kl. 50–66), potem chowają się pod ziemię.
- `trafienie` (0,7 s): szarpnięcie w tył, oczy się mrużą.
- `unik` (1 s): ciężki odskok w bok i powrót.
- `upadek` (2,7 s): osiada, kryształ gaśnie, oczy się zamykają, a potem rozsypuje się na stos głazów.
- `ryk` (pętla 2 s): pięści w górze, otwarta paszcza, mocny puls kryształu.

## Pliki
- Moduł: `swiat/postacie/straznik_gaju.py`
- Wynik: `swiat/postacie/wynik/straznik_gaju/`. Są tam: FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, ikona, filmy, arkusze klatek i `raport.txt`.
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (tabliczka nad koroną), `KrysztalAttachment` (poświata, cel trafień), `PiescLAttachment` i `PiescPAttachment` oraz `KorzenieAttachment` (środek uścisku korzeni).

## Znane słabości
- Importu do Roblox Studio nie testowaliśmy. Szkielet jest własny, nie R15.
- Świecenie działa tylko w Blenderze. W Roblox trzeba dać materiał Neon albo PointLight. Puls kryształu z daleka jest słaby.
- Korzenie umiejętności poza klipem siedzą schowane w tułowiu. Przerwanie umiejętności innym klipem przeciągnie je przez ciało, więc lepiej jej nie przerywać.
- Upadek: głazy spadają po prostych torach i trochę się przenikają, a stos głazów z daleka czyta się słabo.
- Chód jest w miejscu, a w uniku stopy przesuwają się razem z ciałem.
- Z kamery 3/4 moment trafienia w ataku widać jako pięść wysuniętą w stronę widza. Z boku czyta się lepiej.
- Pełna lista jest w `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
