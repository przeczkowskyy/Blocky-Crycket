---
status: kanon
tags: [postacie, bohater]
źródło: "[[Dokumentacja projektu (oryginał)]] §2"
---
# Rycerz

Jeden z dwóch głównych bohaterów i wizytówka gry.

- Kanciasty ludzik Roblox.
- **Stalowa zbroja** i **niebieski tabard**.
- **Wielki miecz**.

Styl: [[Kierunek artystyczny]] (voxel / low-poly, grube czarne obrysy w grafikach 2D).
Występuje na: [[Ekran ładowania]] (razem z [[Kot-Mag|Kotem-Magiem]]).

## Klipy walki
To propozycja animacji modelu 3D (15.11.2026, po przeglądzie) — wygląd Rycerza pozostaje kanonem i się nie zmienił; doszła tylko **tarcza** jako osobny przedmiot na lewej dłoni (Wojownik blokuje tarczą), do decyzji, bo kanon jej nie wymienia. Klasa i umiejętności: [[Walka v2 — silnik, klasy i umiejętności]]. 30 kl./s.
- `blok` (1 s) — zasłona tarczą, cios w tarczę w **kl. 11**; `unik` (1 s) — ciężki odskok w lewo i powrót (szczyt kl. 10, lądowanie kl. 14); `trafienie` (0,67 s) — szarpnięcie w tył w **kl. 4**; `upadek` (2 s) — pada na plecy w kl. 36, leży od kl. 46 (ostatnią klatkę zatrzymać), miecz obok.
- `ciecie` (1,6 s) — Potężne cięcie: szeroki poziomy zamach z obrotem tułowia, trafienie w **kl. 18**.
- `miazdzacy_cios` (1,67 s) — wyskok i cios z góry, trafienie w **kl. 22**, sztych w ziemi przed nim w kl. 23.
- `kamienna_skora` (1,47 s) — tupnięcie w **kl. 14** i poza obronna (tarcza przed siebie, miecz nad tarczą).
- Pliki: moduł `swiat/postacie/rycerz.py` (klatki trafienia w słowniku `CHWILE`, kontrola: `python -B swiat/postacie/rycerz.py --kontrola`), filmy, arkusze klatek i FBX w `swiat/postacie/wynik/rycerz/`.
- Znane słabości: naramienniki ocierają się o boki hełmu przy uniesionej ręce (do 0,18 studa — bryły modelu, nie broń); tarcza wisi na dłoni, więc w bloku nadgarstek jest mocno zgięty; pancerz i tabard sztywne, twarz bez mimiki; stary `atak_miecz` ma dłoń w tułowiu i stopy pod ziemią (do decyzji, czy go przerobić). Pełna lista: `raport.txt` w folderze wyniku.

## Model bazowy i strój
Propozycja modelu 3D (15.11.2026) — realizacja [[Rejestr decyzji|D-071]]: strój Rycerza to przedmioty zakładane na goły model, a w pełnym stroju wygląda tak jak dotąd.
- **Bez stroju:** ta sama twarz i mina, krótka brązowa czupryna (hełm ją chowa), lniana koszula z krótkim rękawem, niebieskie krótkie spodenki w kolorze tabardu, bose stopy.
- **Komplet (slot):** hełm (Helmet) · zbroja z tabardem (Chest) · nogawice — część zbroi (Chest; osobny slot spodni do decyzji) · pas, dziś sama klamra (Belt) · rękawice (Gloves) · trzewiki z nagolennikami (Boots) · wielki miecz (Weapon) · tarcza (druga ręka, tylko Wojownik).
- **Tarcza** nie należy do stałego wyglądu — widać ją tylko po założeniu; bez niej `blok` to zasłona przedramieniem.
- Ruchy są wspólne dla każdego stroju. Bez zbroi Rycerz w ostatniej klatce `upadek` leży ok. 0,25 studa nad ziemią (do poprawy w grze).
- Pliki: `swiat/postacie/wynik/rycerz/ekwipunek/` (plansze strojów, goły model, przedmioty, ikony, `ekwipunek.json`); zasady: `swiat/postacie/EKWIPUNEK.md`.
