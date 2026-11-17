---
status: propozycja
data: 2026-11-18
dotyczy: D-099 (Gemy bez płacenia), pytanie 51; D-100 (Rebirth) — ODRZUCONA
---

# Gemy bez płacenia — liczby do D-099 (Rebirth odrzucony)

> **Rebirth NIE jest planem.** Decyzja D-100 (Rebirth) została **odrzucona** 17.11.2026 (Karol, potwierdził Paweł:
> „Zostaw rebirth na później”). Część 2 tego dokumentu to tylko zapis rachunku na później — **nie wdrażać**.
> Obowiązuje część 1: Gemy bez płacenia (D-099 ✅ zatwierdzona 17.11), liczby „do zmiany”. W `swiat/stan_gracza`
> wdrożone są od 18.11.2026 Gemy za poziom (+10) i za pierwsze pokonanie strażnika biomu (+100); +1 za każde
> 10 wygranych i kopalnia w Twierdzy — jeszcze nie.

Źródła liczb (tylko odczyt):
- tempo poziomów: `tools/walka/BALANS_1711.md`, tabela „Tempo: poziom gracza na granicach biomów” (krzywa
  11,71 × L^1,6 z `tempo.py`, plan rosnący z D-076);
- Gemy: tamże, część 4 (koszt drzewek z `src/shared/SkillTreeData.luau`, kamienie milowe, kopalnia diamentów);
- trening: tamże, część 6 (wzór z paskiem — pytanie 50, odpowiedź Karola: a);
- ceny jajek: `swiat/pety_proba/ustawienia.json` (las 300, Bagno 750 Złota);
- premie do łupu: `swiat/stan_gracza` (`Sygnaly/Modyfikatory`, suma premii do łupu najwyżej +100%).

## 1. Gemy bez płacenia (D-099 ✅) — propozycja liczb

Źródła z D-099 (bez Rebirthu — D-100 odrzucona); liczby dobrane do celu z pytania 51 (ok. 200 Gemów na godzinę → ćwierć drzewka gracza
w 10 godzin):

| Źródło | Ile | Uwagi |
|---|---|---|
| za poziom | +10 za każdy awans | kamień milowy z `BALANS_1711.md`, część 4 |
| za walki | +1 za każde 10 wygranych (licznik, nie los) + dzisiejszy łup (1–15% szansy na 1 Gem) | pewna nagroda jest czytelniejsza dla dzieci niż rzadki los |
| za strażnika | +100 za pierwsze pokonanie strażnika każdego biomu | raz na biom (po Rebirthie znowu) |
| kopalnia w Twierdzy (D-049) | od 25. poziomu: 30 na godzinę, ×1,25 co poziom budynku | jak w `BALANS_1711.md`; tylko czas gry |

Gemy zebrane do końca biomu (plan rosnący; walki ok. 1,2 wygranej na minutę):

| Biom | Minuta | Poziom | Za poziomy | Za strażników | Za walki | Kopalnia | Razem | Drzewko gracza (8105) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Las | 30 | 11 | 100 | 100 | 4 | 0 | 204 | 2,5% |
| Bagno | 75 | 19 | 180 | 200 | 9 | 0 | 389 | 4,8% |
| Dżungla | 135 | 26 | 250 | 300 | 16 | 8 | 574 | 7,1% |
| Pustynia | 210 | 34 | 330 | 400 | 25 | 51 | 806 | 9,9% |
| Góry z tundrą | 305 | 43 | 420 | 500 | 37 | 132 | 1089 | 13,4% |
| Lodowiec | 430 | 53 | 520 | 600 | 52 | 293 | 1465 | 18,1% |
| Wulkaniczny (10 h) | 600 | 65 | 640 | 700 | 72 | 644 | **2056** | **25,4%** |
| Kryształowy | 830 | 79 | 780 | 800 | 100 | 1507 | 3187 | 39,3% |

- Sloty umiejętności (25 / 70 / 125 Gemów z korzeniem) gracz kupi wszystkie w lesie (204 Gemy na końcu lasu). Model
  balansu walki zakłada sloty od 1., 5. i 10. poziomu, więc to się zgadza.
- Po 10 godzinach ok. 2050 Gemów to ćwierć drzewka gracza, czyli cel z pytania 51 (wariant a).

## Gdzie to jest w kodzie
- `swiat/stan_gracza` (18.11.2026): `GEMY_ZA_POZIOM` i `GEMY_ZA_STRAZNIKA` w `dane.py`; pokonani strażnicy w profilu
  (`straznicy`). Do zrobienia: +1 za każde 10 wygranych (licznik wygranych jest już w profilu: `walki.wygrane`).
- Kopalnia: Twierdza (D-049), poza tym pakietem.

## 2. Rebirth — ODRZUCONY (D-100 ❌, 17.11.2026): zapis rachunku na później, nie wdrażać

### Co wyszło (archiwum)
- **100. poziom to ok. 20,5 godziny gry**, czyli dwa razy więcej niż pierwsza wersja (10 godzin do ostatniego biomu,
  gracz kończy ją na ok. 65. poziomie). Rebirth od 100. poziomu jest więc treścią „po przejściu gry”.
- Proponuję: Rebirth zeruje poziom, Złoto i postęp biomów; zostają Gemy, pety, drzewka i ćwierć treningu.
- **Nagroda za n-ty Rebirth:** 500 × n Gemów (najwyżej 2500), 1000 × n Złota na start (najwyżej 5000) i stała premia
  +10% Złota i doświadczenia z walk za każdy Rebirth (najwyżej +50%).
- **Gemy bez płacenia:** +10 za poziom, +100 za pierwsze pokonanie strażnika biomu, +1 za każde 10 wygranych walk,
  do tego kopalnia w Twierdzy. To daje ok. 2000 Gemów w 10 godzin, czyli ok. 25% drzewka gracza (cel z pytania 51).
  Wszystkie trzy sloty umiejętności gracz kupi już w lesie.

### 2.1 Kiedy Rebirth: 100. poziom przy dzisiejszym tempie

| Chwila gry (plan rosnący) | Minuta | Poziom | Doświadczenie na minutę |
|---|---:|---:|---:|
| koniec lasu | 30 | 11 | 68 |
| koniec Pustyni | 210 | 34 | 282 |
| 10 godzin — koniec 7. biomu (Wulkaniczny) | 600 | 65 | 556 |
| koniec 8. biomu (Kryształowy) | 830 | 79 | 661 |
| **100. poziom** (dalej w ostatnim biomie, tempo rośnie z poziomem) | **ok. 1225** | **100** | ok. 830 |

Od 79. do 100. poziomu jest ok. 326 000 doświadczenia, czyli ok. 6,6 godziny walk w ostatnim biomie. Rebirth
na 100. poziomie przychodzi więc po ok. 20 godzinach, ok. 10 godzin po przejściu pierwszej wersji gry.

Do wyboru dla ludzi:
- (a) zostaje 100. poziom — Rebirth jest celem dla tych, którzy grają dalej po ostatnim biomie;
- (b) próg ok. 70. poziomu — Rebirth tuż po 10-godzinnej wersji (koniec 8. biomu przy planie równym);
- (c) szybsza krzywa doświadczenia od 65. poziomu — zmienia balans biomów, wymaga przeliczenia.

Rekomendacja: (a). Kolejne Rebirthy też od 100. poziomu, bo poziom wraca do 1. „Co 100 poziomów” z D-100 rozumiem jako
„za każdym razem trzeba znów dojść do 100.”. Jeśli Paweł miał na myśli 200., 300. itd., to dla krzywej L^1,6 każdy
kolejny Rebirth trwałby kilkadziesiąt godzin, więc to odradzam.

### 2.2 Co się zeruje, a co zostaje

| Rzecz | Po Rebirthie | Dlaczego |
|---|---|---|
| Poziom, doświadczenie | 1. poziom, 0 | sedno Rebirthu |
| Statystyki z poziomu (5 samo + 5 do rozdania, D-097) | od nowa | idą za poziomem |
| Trening (wytrenowane punkty i licznik malejącego zysku) | **zostaje ćwierć** | Cały trening z 10 godzin (ok. 260–290 punktów, połowa puli 56. poziomu) na 1. poziomie to dziesięciokrotność puli startowej (30), więc las byłby bez walki. Ćwierć (ok. 70) daje mocny start, który znika do ok. 40. poziomu, a trening od razu znów rośnie (licznik też ×0,25). |
| Złoto | zastąpione nagrodą startową | inaczej Rebirth nic nie zmienia w ekonomii |
| Postęp biomów (strażnicy, bramy) | od nowa | gracz przechodzi biomy jeszcze raz, szybciej |
| Gemy | zostają + nagroda | waluta premium nie może przepadać |
| Drzewka (kupione za Gemy), sloty umiejętności | zostają | opłacone Gemami |
| Pety i ich kopie | zostają | kolekcja; ich premie liczą się dalej |
| Przedmioty i ulepszenia Kowala (D-102) | **do decyzji** | Jeśli przedmioty mają wymagany poziom, mogą zostać; bez tego zostawiony przedmiot z 90. poziomu robi z lasu spacer. Proponuję: zostają w ekwipunku, nosi się je od ich poziomu. |

### 2.3 Nagroda i jak rośnie z kolejnymi Rebirthami

Stała premia działa przez `Sygnaly/Modyfikatory` (źródło „rebirth”, pole `lup`). Razem z petem (najwyżej +50%) daje to
najwyżej +100%, a tyle wynosi limit złożenia w stanie gracza.

| Rebirth | Gemy | Złoto na start (las: jajko 300) | Premia Złota i doświadczenia z walk | Czas do kolejnego (szacunek) |
|---:|---:|---:|---:|---:|
| 1. | 500 | 1000 (3 jajka) | +10% | ok. 18,5 h |
| 2. | 1000 | 2000 | +20% | ok. 17 h |
| 3. | 1500 | 3000 | +30% | ok. 16 h |
| 4. | 2000 | 4000 | +40% | ok. 14,5 h |
| 5. i dalej | 2500 | 5000 | +50% (koniec) | ok. 13,5 h |

Czas do kolejnego Rebirthu = 20,5 h ÷ (1 + premia doświadczenia). Nie liczy szybszego lasu dzięki ćwierci treningu,
Złota na pety i znajomości biomów, więc w praktyce będzie krócej. Po co gracz robi Rebirth:
- 500–2500 Gemów naraz to 6–31% drzewka gracza (8105);
- każdy Rebirth przyspiesza następny o ok. 10%;
- pety kupione za Złoto startowe dają premie od pierwszych minut.

Bez osobnego drzewka Rebirthów i bez premii do statystyk (zgodnie z D-100: „bez drzewka Rebirthów”).

## Czego nie sprawdziłem
- (Rebirth, archiwum) czasu po Rebirthie symulacją walk (szacunek z krzywej i tempa planu, bez biomów 3–8 w danych walki).
- Wpływu ćwierci treningu na pierwsze biomy po Rebirthie (wymaga przeliczenia z `progresja.py` z niezerowym
  licznikiem W[s]).
- Gemów przy planie równym (część 4 `BALANS_1711.md` ma go dla kamieni milowych; tu tylko plan rosnący).
