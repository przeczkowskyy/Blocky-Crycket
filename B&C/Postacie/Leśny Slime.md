---
status: propozycja
tags: [postacie, potwor, model-3d]
źródło: "swiat/postacie/lesny_slime.py (model z Blendera, 14.11.2026, wersja 2 po uwadze „ma być bardziej cute”; 15.11.2026: bryła zmieniona na sześcian)"
---
# Leśny Slime

Zwykły przeciwnik lasu w walce: pulchna kostka galarety z dużą ilością życia i słabymi ciosami. Bije całym ciałem, a jego umiejętność to kwaśny plusk, który zdziera pancerz (statystyki: [[Walka v2 — silnik, klasy i umiejętności]]). To leśny kuzyn slime'a-peta z [[Pety]]: przeciwnik, ale uroczy, a nie groźny. W tym samym lesie walczą [[Muchomornik]], [[Cierniowy Wilk]] i [[Leśny Troll]]. Model 3D jest **propozycją** do oceny i nie ma go jeszcze w Roblox. Wersja 2 powstała po uwadze Karola z 14.11.2026: ma być bardziej uroczy.

## Wygląd
- Niska i szeroka kostka galarety z mocno ściętymi krawędziami, przysadzista jak galaretka. Cała jest w jednym kolorze: jasnej, soczystej zieleni. Nie ma osobnych „szybek” na ścianach, więc przód nie wygląda jak ekran telewizorka w ramce (tym różni się też od niebieskiego peta).
- Twarz: duże, okrągłe, błyszczące oczy z dwoma białymi błyskami, osadzone nisko i szeroko. Pod nimi malutki uśmiech z języczkiem i różowe rumieńce. Nad oczami dużo „czoła”.
- Na czubku kiełek z dwoma listkami. Kiwa się przy każdym ruchu.
- W środku „pływają” liść i mały czerwony grzybek. Widać je z tyłu i z prawego boku. Przy podstawie leżą małe, okrągłe kropelki galarety.
- Kwas (bańka i kałuża z umiejętności) to limonkowa żółć. Ciepłe akcenty to rumieńce, języczek i grzybek.

## Miny
- Oczy: otwarte, zamknięte (mrugnięcie), szczęśliwe łuki, zaciśnięte „> <” i wielkie zaskoczone.
- Usta: mały uśmiech, buzia „o”, szeroki uśmiech z języczkiem i falka.
- Policzki nadymają się przy kwaśnym plusku.

## Wymiary
- Kostka to sześcian 2,7 × 2,7 × 2,7 studa (pet ma 2,25 wysokości, gracz 5,7) — od 15.11.2026, po uwadze Karola „powinien być sześcianowy”; twarz i animacje bez zmian. Z kiełkiem i kropelkami zajmuje 3,8 × 3,4 × 3,3 studa.
- Model ma 4396 trójkątów w 25 siatkach (limit Roblox to 20 000 na siatkę). Szkielet ma 28 kości: Root i 27 własnych (to nie R15). Każda wersja oczu i ust ma własną kość.

## Klipy (30 kl./s, patrzy w +Z)
- `idle` (pętla 2 s): radosne bujanie na boki, mrugnięcie, kiełek się kiwa.
- `ruch` (pętla 0,8 s): mały hopek z szerokim uśmiechem w locie.
- `atak` (1 s): rozpęd z zaciśniętymi oczami i niezdarne pacnięcie brzuszkiem w kl. 13, ok. 1,85 studa przed nim. Potem odbicie ze zdziwioną minką.
- `umiejetnosc` (2,2 s): kwaśny plusk. Nadyma policzki, z buzi wychodzi świecąca bańka kwasu. W kl. 21 pluje, bańka leci łukiem i w kl. 31 rozpryskuje się w kałużę ok. 4,3 studa przed nim. Potem zadowolona minka.
- `trafienie` (0,6 s): wielkie zaskoczone oczy, buzia „o” i odskok w tył.
- `unik` (0,9 s): hopek w lewo z piruetem i powrót ślizgiem.
- `upadek` (2 s): zaskoczenie, chwianie z zaciśniętymi oczami i rozpływanie się w kałużę. Oczka leżą na wierzchu kałuży i mrugają, buzia robi „o” („ojej”), kiełek więdnie w tył, grzybek przewraca się na bok. Kończy się leżeniem.
- `wiwat` (pętla 1,3 s): dwa podskoki ze szczęśliwymi oczami i szerokim uśmiechem.

## Pliki
- Moduł: `swiat/postacie/lesny_slime.py`
- Wynik: `swiat/postacie/wynik/lesny_slime/`. Są tam: FBX modelu i każdego klipu, GLB ze wszystkimi klipami, plansza, kadr bohaterski, ikona, filmy, arkusze klatek i `raport.txt`.
- Punkty zaczepienia dla gry: `RootAttachment`, `GlowaAttachment` (tabliczka nad głową), `PyskAttachment` (start bańki kwasu) i `PluskAttachment` (efekt rozprysku).

## Znane słabości
- Importu do Roblox Studio nie testowaliśmy. Szkielet jest własny, nie R15, a galareta jest skórowana na dwóch kościach.
- Miny to podmiana gotowych kształtów oczu i ust (bez klatek pośrednich). W grze obrys obejmie tylko sylwetkę, więc oczy i usta nie będą miały czarnej obwódki z renderów.
- Nie ma prawdziwej przezroczystości. Liść i grzybek „w środku” to płaskie obrazki z tyłu i na prawym boku. Na renderach, gdy slime się obraca, mają wokół siebie ciemny cień od obrysu.
- Kałuża po upadku z bliska ma prostokątny środek. Unik kończy się obrotem o 360°, co odtwarzacz walki musi traktować jak 0°.
- W filmach slime jest mały, bo kadr obejmuje lot bańki. Pełna lista jest w `raport.txt` w folderze wyniku.

## Powiązane
- [[Kierunek artystyczny]]
- [[Postacie 3D — Blender i Roblox]]
- [[00 Start]]
