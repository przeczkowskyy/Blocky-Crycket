---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/lesny_slime.py (model z Blendera, 14.11.2026)"
---
# Leśny Slime

Zwykły przeciwnik lasu w walce: duża, ciężka kostka galarety z dużą ilością życia i słabymi ciosami. Bije całym ciałem, a jego umiejętność to kwaśny plusk, który zdziera pancerz (statystyki: [[Walka v2 — silnik, klasy i umiejętności]]). To leśna, złośliwa odmiana slime'a-peta z [[Pety]]. W tym samym lesie walczą [[Muchomornik]], [[Cierniowy Wilk]] i [[Leśny Troll]]. Model 3D jest **propozycją** do oceny i nie ma go jeszcze w Roblox.

## Wygląd
- Mchowozielona kostka galarety ze ściętymi krawędziami: jasna, lekko świecąca skorupka i ciemniejszy środek, jak u peta, ale w kolorze lasu.
- Złośliwa mina w stylu gry: oczy jak przechylone trapezy pod grubymi brwiami w V, krzywy uśmieszek z dwoma kłami i kroplą kwasu w kąciku.
- W środku „pływają” liść i mały czerwony grzybek. Widać je z boków, z tyłu i z góry. Po rozlaniu przy upadku prawdziwy liść i grzybek wypływają na wierzch.
- Jedyny mocny akcent koloru to kwaśna limonka: kula kwasu, kałuża i kropla przy ustach. Przy podstawie leżą lepkie krople galarety.

## Wymiary
- Kostka ma 2,9 × 2,6 × 2,8 studa (pet ma 2,25 wysokości, gracz 5,7). Z kroplami przy podstawie zajmuje 3,9 × 2,7 × 3,3 studa.
- Model ma 2472 trójkąty w 15 siatkach (limit Roblox to 20 000 na siatkę). Szkielet ma 18 kości: Root i 17 własnych, w tym kula kwasu na własnej kości `Kula` (to nie R15).

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2 s): ciężki oddech galarety, lekki przechył w przód, jedno mrugnięcie.
- `ruch` (pętla 0,8 s): podskok naprzód w miejscu, z przysiadem i lądowaniem ze zgnieceniem.
- `atak` (1 s): przysiad z odchyleniem w tył, wybicie i uderzenie całym ciałem z otwartą paszczą. Trafienie w kl. 13, ok. 1,9 studa przed nim.
- `umiejetnosc` (2,2 s): kwaśny plusk. Nadyma się i otwiera paszczę, w której świeci kula kwasu. W kl. 21 pluje, kula leci łukiem i w kl. 31 rozpryskuje się w kałużę ok. 4,3 studa przed nim.
- `trafienie` (0,6 s): szarpnięcie w tył ze zgnieceniem i zaciśniętymi oczami.
- `unik` (0,9 s): odskok w lewo i powrót ślizgiem.
- `upadek` (2 s): chwieje się z zamkniętymi oczami i rozlewa w płaską kałużę z płatami. Na wierzch wypływają grzybek, liść i kula kwasu. Kończy się leżeniem.
- `wiwat` (pętla 1,3 s): dwa podskoki z otwartą paszczą i kołysaniem na boki.

## Pliki
- Moduł: `swiat/postacie/lesny_slime.py`
- Wynik: `swiat/postacie/wynik/lesny_slime/`. Są tam: FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, ikona, filmy, arkusze klatek i `raport.txt`.
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (tabliczka nad głową), `PyskAttachment` (start kuli kwasu) i `PluskAttachment` (efekt rozprysku).

## Znane słabości
- Importu do Roblox Studio nie testowaliśmy. Szkielet jest własny, nie R15, a galareta jest skórowana na dwóch kościach.
- Nie ma prawdziwej przezroczystości. Liść i grzybek „w środku” to płaskie obrazki na bokach, z tyłu i na górze, a od przodu ich nie widać (tam jest twarz).
- Kałuża po upadku z bliska nadal ma prostokątny środek spłaszczonej kostki. Rozprysku kwasu (cząsteczek) nie ma, trzeba go dodać na `PluskAttachment`.
- W filmach slime jest mały, bo kadr obejmuje lot kuli. Pełna lista jest w `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
