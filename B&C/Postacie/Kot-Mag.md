---
status: kanon
tags: [postacie, bohater]
źródło: "[[Dokumentacja projektu (oryginał)]] §2"
---
# Kot-Mag

Jeden z dwóch głównych bohaterów i wizytówka gry.

- Mały, kanciasty, **pomarańczowy kot**.
- **Purpurowa, za duża szata czarodzieja**, ciągnąca się po ziemi.
- **Magiczny kostur**.

Do potwierdzenia (z późniejszej specyfikacji, `propozycja`): spiczasty kapelusz i fioletowy kryształ na kosturze.

Występuje na: [[Ekran ładowania]] (razem z [[Rycerz|Rycerzem]]).

## Klipy walki
To propozycja animacji modelu 3D (15.11.2026) — wygląd kota się nie zmienił. Klasa i umiejętności: [[Walka v2 — silnik, klasy i umiejętności]]. 30 kl./s.
- `atak` (0,87 s) — szybki błysk z kostura, wypuszczenie iskry w **kl. 9**; `kula_ognia` (1,8 s) — zamach kosturem w górę i w tył z prawej strony głowy, rzut do przodu z wyciągniętą wolną łapą i dobicie w dół, wypuszczenie w **kl. 27**; `lodowy_pocisk` (1,53 s) — kostur nisko i poziomo jak lanca, pchnięcie z wypadem, wypuszczenie w **kl. 21**; `bariera` (1,4 s) — przyczajenie, potem kostur wzniesiony pionowo w górę, łapka dłonią do przodu, krąg w **kl. 10**, poza do kl. 30.
- `unik` (0,93 s) — koci odskok w tył i w bok (ogon w górę, uszy po sobie) i powrót na miejsce; `trafienie` (0,67 s) — szarpnięcie w tył w **kl. 4**; `upadek` (2 s) — pada na lewy bok, kostur wypada z łapy i ląduje przed nim, kapelusz zsuwa się i staje obok głowy; leży od kl. 44 (ostatnią klatkę zatrzymać).
- Poprawione `czar` i `wiwat`: kostur nie przechodzi już przez głowę i kapelusz.
- Uszy i ogon żyją w klipach walki (uszy dostały własne kości, kapelusz i kostur — kości nośne do upadku).
- Pliki: moduł `swiat/postacie/kot_mag.py` (klatki w słowniku `CHWILE`, kontrola: `python -B swiat/postacie/kot_mag.py --kontrola`), filmy, arkusze klatek i FBX w `swiat/postacie/wynik/kot_mag/`.
- Znane słabości: łapy są tak krótkie, że nie sięgają nad głowę ani do siebie nawzajem — w lodowym pocisku drzewce trzyma tylko prawa łapa, a bariera wygląda podobnie jak `czar`; w chwili wypuszczenia atak, kula i lodowy pocisk mają podobną sylwetkę (różnią się zamachem), a z kamery zza pleców kostur skierowany do przodu chowa się za głową; czary bez efektów (do zrobienia w grze); stary `chod` ma palce łap pod ziemią. Pełna lista: `raport.txt` w folderze wyniku.
