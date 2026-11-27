# Balans 27.11 — przejście trzech biomów z treningiem AFK, sklepem trenera, Rybkami i Diamentami

> **PROPOZYCJA, NIE KANON.** Liczone offline (port silnika walki, dane czytane z plików gry 27.11), bez Studio.
> Żadne pliki gry nie zostały zmienione — zmiany niżej to diffy do decyzji. Autor: agent Karola, 27.11.2026.

## Na telefon (krótko)

- **Dziś gra bez treningu AFK prawie nie przechodzi.** Za poziom wchodzi tylko 5 punktów statystyk (drugich 5 „do rozdania” nie ma czym wydać od 24.11), a potwory są strojone pod 10. Gracz, który tylko walczy: ok. **130 min**, ze Strażnikiem wygrywa za pierwszym razem w 2–5% prób, **72–95% graczy odbija się od Strażnika 5+ razy**, kara za przegrane zabiera mu **85% zarobionych Rybek**.
- **Trening AFK jest za mocny (pytanie 117 potwierdzone).** 15 min na stanowiskach daje wygraną ze Strażnikiem Gaju w 99–100%, Topieli 64–85%, Węża 47–56%. Minuta AFK oszczędza **3,6 min walki**. Gracz, który trenuje i pcha do przodu, kończy grę w **47 min** i bije Węża na 18. poziomie zamiast 23.
- **Propozycja (dwie dźwignie):** **A** — 10 punktów za poziom rozdzielanych samo (jedna stała w stanie gracza); **B** — limit treningu: najwyżej 2 × poziom punktów na statystykę, powyżej pasek 10× wolniej (dwie nowe liczby w `TreningAFKDane`). Po A + B: sama walka **68 min** i do 15% utkniętych; typowy gracz (walki + 10 min AFK na godzinę + kowal + pety) **84 min**, Strażnik za pierwszym razem 60 / 63 / 81%; minuta AFK oszczędza 0,4 min walki.
- **Do decyzji Karola i Pawła:** A kłóci się z **D-140** (za poziom tylko Diamenty). Symulacja D-140 bez punktów za poziom: sama walka ok. **461 min**, 100% utkniętych u Strażnika Gaju — D-140 wymaga dużo większego treningu albo słabszych potworów. Długość gry: 84 min wobec roboczego celu 30 / 45 / 60 min na biom (D-076); wydłużenie krzywą doświadczenia ×1,5 daje 113 min, ale serie jednego potwora rosną z 23 do 35 walk.

Szczegóły: niżej — co liczy symulator, cele ze źródłami, krzywa dziś, propozycja w liczbach z diffami, otwarte punkty i pełne tabele.

## 1. Co symulator liczy od 27.11 (`symulacja_przejscia.py`)

Nowe w symulatorze (wszystko z plików gry przy każdym uruchomieniu):

| Część | Skąd liczby | Jak liczone |
|---|---|---|
| Pula statystyk za poziom | `swiat/stan_gracza/dane.py` (`pulaSama`) | jak serwer stanu dziś: 30 + 5 × (L − 1) samo; `--punkty rozdane` = 30 + 10 × (L − 1); `--punkty d140` = 30 |
| Trening AFK (D-141) | `src/shared/TreningAFKDane.luau` | pasek 4 × 1,2 s, +1 za pasek (750 / h na stanowisku), `przyrostCoPoziomow`, skill checki (styl gracza; domyślnie AFK nie klika), reszta paska przechodzi na następną sesję; jedno stanowisko naraz |
| Sklep trenera (D-164) | to samo | ulepszenia 300 / 700 / 1600 / 3600 / 8400 (+10% tempa na poziom), wzmacniacz ×2 na 10 min za 600; gracz kupuje dopiero po przedmiotach i kowalu, z zapasem (`TRENER`) |
| Rybki z zagrody (D-153) | `swiat/pety_proba` | pety stojące w zagrodzie × stawka na sekundę, miejsca 2 → 4 → 6 → 8, ulepszenie u Jagody |
| Diamenty | `swiat/stan_gracza/dane.py` | 10 za poziom + 100 za pierwsze pokonanie Strażnika + Gemy z łupu |
| Wydatki | jw. | po kategoriach: przedmioty, kowal, jajka, trener, zagroda |
| Rzadki potwór | mapy biomów | nie zamyka drogi (bramę ma tylko Strażnik) — do 27.11 symulacja kazała go pokonać |
| Limity (D-144) | silnik | port silnika ma własne: krytyk ≤ 75%, unik ≤ 60%, obrona ≤ 75% ciosu, Zręczność / Szczęście / Inteligencja z malejącym zyskiem (połowa = 4 + 2 × poziom); **Siła, Kondycja i Pancerz rosną liniowo** — dlatego trening tak mocno działa |

Nowe sposoby gry: „Walki + trening AFK”, „Gracz AFK (20 min na godzinę)”, „AFK i przeskakiwanie zagród” (sprawdzian pytania 117: po każdej wygranej idzie dalej, nie patrząc na poziom). Pierwsza sesja AFK zaraz po pierwszej wygranej (start w miasteczku, D-159), potem co 30 min. Nowe opcje: `--afk-min`, `--punkty`, `--propozycje`, `--ziaren-straznikow`. Testy: `test_symulacji.py` — **20 testów, wszystkie zielone** (było 16; nowe: tempo i reszta paska, limit, odczyt `TreningAFKDane`, Rybki / Diamenty / zagroda / wydatki, tabela Strażników). Stare mini-gry wypadły z symulacji (w grze nie mają wejścia, D-162).

**Czego symulator nie liczy:** drzewka (Diamenty się zbierają, ale atrybuty `ST_*` z drzewka nie trafiają do walki — sprawdzone w kodzie), sklepu składników kuźni (D-152 — nie ma go w danych), sprzedaży petów (D-161), drugiego slotu peta, gry kilku graczy na serwerze (liczony 1 gracz), wyrzucenia po 20 min bez ruchu (sesje AFK są krótsze), wzmacniacza płynącego poza grą, przedmiotów rzadkich z D-142 / D-155 (jeszcze ich nie ma w danych). Styl gracza (kiedy trenuje, co kupuje, kiedy idzie dalej) to założenia z `STYLE`, `TRYBY`, `TRENER`.

## 2. Cele — skąd i jakie

| # | Cel | Źródło | Status źródła |
|---|---|---|---|
| T1 | Trzy biomy u typowego gracza (walki + 10 min AFK na godzinę + kowal + pety): czas rośnie z biomem; roboczo 30 / 45 / 60 min (razem ok. 135 min) | D-076 (korekta Karola 16.11: ok. 10 h do ostatniego z siedmiu biomów; podział 30 / 45 / … to rachunek agenta), D-149 (beta, „nie zmaksować w 4–5 dni”) | D-076 ✅; podział i D-149 — propozycje |
| T2 | Strażnik ma być trudny: sam bohater na poziomie Strażnika wygrywa 25–45%; typowy gracz za pierwszym razem 40–65%; utyka (5+ przegranych) ≤ 10% w każdym stylu z dodatkami, a gracz bez treningu ≤ 15% | D-111 („gracz słusznie ma się pomęczyć”, ok. 6% utkniętych), D-076 („ma się dać przegrać”) | D-111 ✅ (jeden podpis); progi — **moje** |
| T3 | Bez czekania; najdłuższa seria jednego potwora ≤ 15 walk; bez awansu ≤ 5 min czystej walki | D-107 („ciągła dopamina”), Mózg #15 i #34 | D-107 ✅; liczby — **moje** |
| T4 | Minuta AFK oszczędza najwyżej 1 minutę walki; trening nie pozwala bić Strażnika więcej niż 2 poziomy poniżej jego poziomu | pytanie 117 (zdanie agenta: trening ok. połowy przyrostu walki), uwaga agenta w D-141 (limit zależny od poziomu), Mózg #5 (żadnej strategii zdominowanej) | **moje** |
| T5 | Zagroda 5–15% Rybek, nie główne źródło | D-153 („miły dodatek”, rachunek `ekonomia_zagrody.py`) | propozycja |
| T6 | Komplet stopnia biomu w zasięgu przy jego Strażniku | `SKLEP_PRZEDMIOTY.md` §7.1 (komplet = 40% Rybek krainy) | propozycja |

## 3. Krzywa dziś (pliki gry 27.11, 40 graczy na klasę, średnio z trzech klas)

| Sposób gry | Koniec (min) | W tym AFK | Las / Bagno / Dżungla (min) | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Rybki stracone / zarobione |
|---|---:|---:|---|---|---|---:|---|
| Tylko walki | 130 (118–145) | 0 | 33 / 43 / 51 | 3 / 2 / 1 | 79 / 88 / 88 | 21 | 17 100 / 20 100 (85%) |
| Walki + AFK 10 min/h | 85 | 17 | 25 / 27 / 32 | 22 / 30 / 48 | 7 / 7 / 0 | 24 | 4 100 / 22 800 |
| Walki + AFK + sklep trenera + pety + kowal | 89 | 18 | 26 / 29 / 35 | 37 / 59 / 73 | 1 / 0 / 0 | 23 | 800 / 23 800 |
| + sklep z przedmiotami | 92 | 19 | 27 / 29 / 35 | 43 / 65 / 85 | 0 / 0 / 0 | 23 | 300 / 23 800 |
| Gracz AFK 20 min/h | 109 (66 bez AFK) | 43 | 29 / 36 / 43 | 80 / 96 / 100 | 0 / 0 / 0 | 22 | 50 / 24 400 |
| AFK 20 min/h i przeskakiwanie | **47** | 22 | 17 / 19 / 10 | 0 / 3 / 35 | 45 / 90 / 16 | 4 | 2 200 / 6 900 (Węża bije na 17–18. poziomie) |
| Niecierpliwy (bez treningu) | 78 | 0 | 19 / 26 / 33 | 2 / 1 / 1 | 93 / 94 / 92 | 19 | 13 400 / 15 300 |

Sam bohater na poziomie Strażnika (300 walk): Gaj 1–2%, Topiel 0–2%, Wąż 0–3%. Po 15 min AFK: 99–100% / 64–85% / 47–56%. Do 50% wystarcza 6–7 min AFK przy Gaju, 10–12 min przy Topieli, 14–16 min przy Wężu.

Wobec celów: **T1** — 89 min, za krótko o ok. 1/3 wobec roboczych 135 min; **T2** — bez treningu nie do zagrania (utyka 72–95%), z treningiem za łatwo dla gracza AFK; **T3** — czekania 0 (D-107 działa), ale serie 22–25 walk jednego potwora (Kokosowy Siłacz, Zwijogon: w każdej zagrodzie Dżungli gracz robi 2 poziomy po ok. 11 walk); **T4** — minuta AFK oszczędza 3,6 min walki, przeskakujący bije Węża 5 poziomów za wcześnie; **T5** — zagroda daje ok. 490 Rybek na całą grę (2%); **T6** — tak: przy Strażnikach gracz ze sklepem ma zarobione 3,3 / 9,6 / 23,8 tys. wobec kompletów 1 400 / 3 300 / 5 200 i kupuje Wojownikiem i Zwiadowcą 6 rzeczy, Magiem 3 z 4 (reszta przegrywa z przedmiotem kowala +2, §7.5); na końcu zostaje mu 3–8 tys. Rybek. Sklep trenera: typowy gracz wydaje u trenera 300–1 100 Rybek; komplet ulepszeń (87 600) to 3,7 × wszystkich Rybek z trzech biomów. Diamenty: ok. 520 na całą grę (sama walka: 560–570).

## 4. Propozycja w liczbach (nie wdrożona)

| Dźwignia | Przed → po | Efekt w symulacji (średnio z klas) |
|---|---|---|
| **A. Punkty za poziom** (`swiat/stan_gracza/dane.py`, pakiet Karola) | `PUNKTY_SAMO_NA_POZIOM` 5 → **10**, `PUNKTY_DO_ROZDANIA` 5 → **0** (pula 30 + 10 × (L − 1), jak przy strojeniu potworów) | Tylko walki: 130 → **68 min**, utknęło 79 / 88 / 88 → 2 / 9 / 15%, Rybki stracone 85% → 30%; sam bohater przy Strażniku 0–3% → 22–42%. Sama A daje jednak graczowi AFK łatwą grę (Strażnik za 1. razem 97–100%) |
| **B. Limit treningu** (`src/shared/TreningAFKDane.luau`, pliki Pawła — dwie nowe liczby i odczyt wytrenowanych punktów w serwerze) | brak → `limitNaPoziom = 2` (wytrenowane w jednej statystyce < 2 × poziom gracza: pełne tempo), `ponadLimitem = 0.1` (powyżej pasek 10× dłuższy); tempo podstawowe bez zmian (4 × 1,2 s — Paweł chciał szybki pasek) | Z A: minuta AFK oszczędza 0,76 → **0,41** min walki; typowy gracz 80 → 84 min, Strażnik za 1. razem 89 / 94 / 93 → **60 / 63 / 81%**; gracz AFK 20 min/h: 97–100% → 72 / 73 / 90%; 15 min AFK przy Strażniku: 90–92 / 69–87 / 76–81% (ponad limitem prawie nic). Bez A pogarsza grę (typowy 107 min, Gaj utyka 16%) — B tylko razem z A |
| **(b) Potwory i łup** | potwory, życie Strażników, zagrody i odradzanie — **bez zmian** (po A wracają do stanu ze strojenia D-111: sam bohater 22–42%). Opcjonalnie pytanie 70: doświadczenie potworów Dżungli ×1,25 (zwykłe 14 + 6 × L → 17,5 + 7,5 × L) w `swiat/dzungla_pas_gra/przeciwnicy.py` | Z A + B: koniec 84 → 80 min, seria 23 → 19, gracz bez treningu u Węża utyka 15 → 8%. Odradzanie: czekania już 0 — zostaje |
| **(c1) Zagroda** (`swiat/pety_proba/ustawienia.json`, `zagroda.stawki_s`) | 0,015 / 0,025 / 0,04 / 0,065 / 0,1 → **×3** (0,045 / 0,075 / 0,12 / 0,195 / 0,3) | Rachunek z wyników (bez nowego przebiegu): 490 → ok. 1 470 Rybek na grę, 2% → ok. 6% (T5); kafelek „+0.05/s” zamiast „+0.015/s” jest widoczny |
| (c2) Sklep trenera | ceny bez zmian (sprawdzone 150 / 350 / 800 / 1800 / 4200: wydatki u trenera 300 → 500, wynik gry ten sam) | Przy B ulepszenie tylko szybciej dobija do limitu — sklep zostaje wydatkiem „na zapas”; ceny ruszać po decyzji o B (pytanie 118) |
| (c3) D-140 bez A | (dla porównania) 0 punktów za poziom + limit 4 × poziom | Tylko walki **461 min**, utknęło 100 / 93 / 94%; typowy 134 min, Gaj utyka 80%. D-140 w tej postaci psuje przejście — potrzebuje treningu jako głównego źródła statystyk (większy limit, ok. 4–5 × poziom, i wskazówka „idź trenować”) albo słabszych potworów lasu |

Długość gry (T1): A + B daje 84 min (23 / 28 / 33 min na biom — rośnie, ale za krótko wobec 30 / 45 / 60). Wydłużenie samą krzywą doświadczenia ×1,5: 113 min (28 / 38 / 46), ale serie jednego potwora 23 → **35 walk** i 70 przegranych u gracza bez treningu. **Moje zdanie (D-114):** nie wydłużać grindu przed betą — dłuższa gra ma przyjść z treścią (nowe zagrody, rzadkie odmiany w każdej zagrodzie, „co piąte powtórzenie coś ponad zwykły wynik” — Mózg #34), bo serie 20+ tego samego potwora już dziś są najsłabszym miejscem.

### Dokładne zmiany (diffy do decyzji, nie zastosowane)

```diff
# A — swiat/stan_gracza/dane.py (potem: python -B swiat/stan_gracza/dane.py — przebudowa DaneStanu.luau)
-PUNKTY_DO_ROZDANIA = 5
-PUNKTY_SAMO_NA_POZIOM = 5
+PUNKTY_DO_ROZDANIA = 0
+PUNKTY_SAMO_NA_POZIOM = 10
```

To samo do szybkiej próby w Studio daje istniejący wyłącznik: atrybut kontenera `PunktyStatystyk = false` (serwer liczy wtedy 10 samo na poziom) — ale ten tryb przyjmuje też darmowe „+”, więc na stałe lepsza zmiana stałych.

```diff
# B — src/shared/TreningAFKDane.luau (plik Pawła)
 D.przyrostCoPoziomow = 0 -- 0 = stały przyrost; np. 10 = +1 za każde 10 poziomów gracza
+-- propozycja 27.11 (BALANS_2711.md): limit treningu zależny od poziomu gracza
+D.limitNaPoziom = 2 -- wytrenowane punkty jednej statystyki < 2 × poziom gracza: pełne tempo; 0 = bez limitu
+D.ponadLimitem = 0.1 -- powyżej limitu pasek liczy się tyle razy wolniej (0.1 = pasek 10× dłuższy); 0 = trening staje
+
+function D.pasekPrzyLimicie(pasek: number, wytrenowane: number, poziomGracza: number): number
+	if D.limitNaPoziom <= 0 or wytrenowane < D.limitNaPoziom * poziomGracza then
+		return pasek
+	end
+	return if D.ponadLimitem > 0 then pasek / D.ponadLimitem else math.huge
+end
```

W `src/server/TreningAFK.server.luau` pasek stanowiska (`t.pasek`, dziś `D.powtorzenDla(...)`) przelicza się po każdym pełnym pasku przez `D.pasekPrzyLimicie(..., wytrenowane, Level)`. Serwer treningu musi znać **wytrenowane** punkty statystyki — są w profilu stanu gracza (`wytrenowane`), więc stan gracza musi je wystawić (np. atrybut gracza na statystykę albo odpowiedź na sygnale). Okno treningu powinno pokazać „MAX dla twojego poziomu — zdobądź poziom”.

```diff
# (b) opcjonalnie, pytanie 70 — swiat/dzungla_pas_gra/przeciwnicy.py, po skopiowaniu łupu
             "lup": copy.deepcopy(po_id[LUP_PO_RANDZE[p["ranga"]]]["lup"]),
         }
+        d["lup"]["doswiadczenie"] = [round(x * 1.25, 4) for x in d["lup"]["doswiadczenie"]]
# (c1) — swiat/pety_proba/ustawienia.json
-"stawki_s": {"pospolity": 0.015, "zwykly": 0.025, "rzadki": 0.04, "epicki": 0.065, "legendarny": 0.1}
+"stawki_s": {"pospolity": 0.045, "zwykly": 0.075, "rzadki": 0.12, "epicki": 0.195, "legendarny": 0.3}
```

## 5. Otwarte punkty dla Karola i Pawła

1. **A a D-140.** D-140 (Paweł 23.11, Karol 25.11) zabiera punkty za poziom; symulacja pokazuje, że bez nich przejście nie działa. Do wyboru: (a) na betę A (10 samo), Diamenty za poziom zostają obok; (b) D-140 i trening jako główne źródło statystyk (osobny projekt: limit 4–5 × poziom, wskazówka treningu, przeliczone potwory lasu); (c) inaczej. Moje zdanie: (a).
2. **Limit treningu (B) w plikach Pawła** — rozstrzyga pytanie 117 (wariant a); potrzebny odczyt wytrenowanych punktów ze stanu gracza.
3. **Długość bety:** 84 min (A + B) wobec roboczych 135 min z D-076 — wydłużać krzywą (×1,5: 113 min, serie 35) czy treścią po becie?
4. **Pytanie 70:** doświadczenie Dżungli +25% — zostawić otwarte czy przyjąć razem z A + B (80 min, seria 19)?

Pliki: `symulacja_przejscia.py`, `test_symulacji.py`, wynik `balans_2711.json`, ten raport. Stare `PRZEJSCIE_W_LICZBACH.md` i `RAPORT_PRZEJSCIA.md` (19.11) opisują grę sprzed treningu AFK — nie przeliczałem ich, żeby nie rozjechać ręcznych wniosków; aktualne liczby są tutaj.

## 6. Tabele (generowane: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 40 --warianty po_zmianie --tryby walki,walki_afk,wszystko,ze_sklepem,afk_duzo,afk_przeskok,niecierpliwy --json swiat/przejscie_gry/balans_2711.json --md swiat/przejscie_gry/BALANS_2711.md`)

Druga tabela Strażników jest liczona na propozycji „A + B + C”; C nie zmienia tej tabeli (minuty AFK liczone bez ulepszeń stanowisk), więc to są liczby dla A + B. „Najdłużej bez awansu” liczy się razem z czasem na stanowiskach.

<!-- TABELE:START -->

### Czasy do kamieni milowych — świat „po zmianie D-107 (pliki gry)” (minuty gry, mediana)

| Sposób gry | Klasa | 1. wygrana | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla | Koniec: 10%–90% graczy | W tym AFK | Skończyło |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Tylko walki | Wojownik | 0,8 | 36 | 87 | 145 | 123–167 | 0,0 | 100% |
| Tylko walki | Zwiadowca | 0,8 | 34 | 76 | 126 | 112–145 | 0,0 | 100% |
| Tylko walki | Mag | 0,7 | 30 | 71 | 118 | 99–145 | 0,0 | 100% |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 0,8 | 25 | 56 | 91 | 88–102 | 17 | 100% |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 0,7 | 26 | 50 | 83 | 80–88 | 17 | 100% |
| Walki + trening AFK (10 min na godzinę) | Mag | 0,7 | 26 | 50 | 80 | 77–84 | 17 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 0,7 | 26 | 59 | 95 | 91–103 | 18 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 0,8 | 25 | 53 | 88 | 85–92 | 18 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 0,7 | 27 | 53 | 85 | 82–89 | 18 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,7 | 27 | 60 | 101 | 91–104 | 23 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,7 | 26 | 53 | 88 | 85–91 | 17 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 28 | 54 | 86 | 83–88 | 17 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 0,7 | 29 | 76 | 113 | 111–116 | 43 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 0,7 | 29 | 59 | 107 | 94–110 | 43 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 0,7 | 30 | 61 | 107 | 94–109 | 43 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 0,6 | 17 | 43 | 49 | 46–51 | 22 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 0,6 | 17 | 27 | 44 | 43–46 | 22 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 0,6 | 20 | 43 | 48 | 46–51 | 22 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,6 | 20 | 49 | 84 | 69–96 | 0,0 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 20 | 43 | 77 | 65–89 | 0,0 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,6 | 19 | 45 | 74 | 62–85 | 0,0 | 100% |

Czas gry liczony razem ze staniem na stanowiskach AFK (kolumna „W tym AFK”). Brama otwiera się od razu po wygranej ze Strażnikiem; dokładne czasy bram są w pliku JSON (pola `brama_…`).

### Minut na krainę — świat „po zmianie D-107 (pliki gry)” (mediana; w nawiasie bez czasu AFK)

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---:|---:|---:|
| Tylko walki | Wojownik | 36 (36) | 52 (52) | 53 (53) |
| Tylko walki | Zwiadowca | 34 (34) | 41 (41) | 51 (51) |
| Tylko walki | Mag | 30 (30) | 37 (37) | 50 (50) |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 25 (19) | 32 (26) | 34 (28) |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 25 (20) | 25 (19) | 33 (27) |
| Walki + trening AFK (10 min na godzinę) | Mag | 26 (20) | 25 (19) | 30 (24) |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 26 (20) | 32 (27) | 38 (30) |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 25 (19) | 27 (21) | 35 (29) |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 26 (21) | 27 (22) | 32 (27) |
| Wszystko + sklep z przedmiotami | Wojownik | 26 (21) | 33 (27) | 39 (29) |
| Wszystko + sklep z przedmiotami | Zwiadowca | 26 (20) | 27 (21) | 34 (29) |
| Wszystko + sklep z przedmiotami | Mag | 28 (22) | 27 (21) | 31 (26) |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 29 (18) | 47 (26) | 37 (26) |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 29 (18) | 30 (19) | 48 (26) |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 29 (19) | 31 (20) | 45 (24) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 17 (6,0) | 24 (14) | 9,0 (6,7) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 16 (5,7) | 10 (10) | 16 (5,4) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 19 (8,5) | 24 (13) | 4,6 (4,5) |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 20 (20) | 28 (28) | 35 (35) |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 19 (19) | 24 (24) | 31 (31) |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 18 (18) | 25 (25) | 32 (32) |

### Poziom, walki i Rybki — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Rybki zarobione (w tym zagroda) | Wydane: przedmioty / kowal / jajka / trener / zagroda | Stracone po przegranych | Punkty z treningu AFK | Diamenty |
|---|---|---|---:|---:|---:|---|---:|---:|---:|
| Tylko walki | Wojownik | 14 / 21 / 28 | 314 | 175 | 21074 (0) | 0 / 0 / 0 / 0 / 0 | 17797 | 0 | 572 |
| Tylko walki | Zwiadowca | 14 / 20 / 27 | 284 | 158 | 19510 (0) | 0 / 0 / 0 / 0 / 0 | 16573 | 0 | 562 |
| Tylko walki | Mag | 14 / 20 / 27 | 286 | 156 | 19801 (0) | 0 / 0 / 0 / 0 / 0 | 17051 | 0 | 562 |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 12 / 17 / 23 | 157 | 27 | 22668 (0) | 0 / 0 / 0 / 0 / 0 | 4060 | 186 | 524 |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 12 / 17 / 24 | 156 | 26 | 22953 (0) | 0 / 0 / 0 / 0 / 0 | 4069 | 186 | 528 |
| Walki + trening AFK (10 min na godzinę) | Mag | 12 / 17 / 23 | 164 | 34 | 22660 (0) | 0 / 0 / 0 / 0 / 0 | 4244 | 186 | 524 |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 12 / 17 / 23 | 146 | 15 | 23648 (490) | 0 / 6950 / 7200 / 600 / 0 | 716 | 198 | 522 |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 11 / 17 / 23 | 143 | 11 | 23978 (489) | 0 / 6900 / 7200 / 300 / 0 | 872 | 192 | 523 |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 11 / 17 / 23 | 152 | 20 | 23667 (472) | 0 / 7460 / 7200 / 300 / 0 | 814 | 192 | 524 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 23 | 142 | 10 | 23975 (509) | 6100 / 6100 / 7200 / 300 / 0 | 264 | 255 | 522 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 23 | 143 | 9 | 24063 (452) | 6300 / 5050 / 7200 / 0 / 0 | 363 | 186 | 523 |
| Wszystko + sklep z przedmiotami | Mag | 12 / 17 / 23 | 146 | 18 | 23343 (389) | 6350 / 4692 / 7200 / 0 / 0 | 336 | 186 | 522 |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 11 / 17 / 23 | 136 | 1 | 24512 (561) | 6200 / 5950 / 7200 / 300 / 0 | 10 | 512 | 522 |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 11 / 17 / 23 | 136 | 1 | 24414 (648) | 6300 / 4900 / 7200 / 1000 / 1000 | 6 | 525 | 522 |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 11 / 17 / 23 | 142 | 9 | 24135 (536) | 8300 / 4825 / 7200 / 300 / 0 | 136 | 512 | 522 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 9 / 16 / 18 | 58 | 36 | 6620 (0) | 0 / 0 / 0 / 1000 / 0 | 2161 | 337 | 471 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 9 / 15 / 17 | 48 | 27 | 6479 (0) | 0 / 0 / 0 / 1000 / 0 | 2051 | 337 | 461 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 10 / 16 / 18 | 72 | 46 | 7545 (0) | 0 / 0 / 0 / 650 / 0 | 2317 | 329 | 472 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 14 / 21 / 28 | 289 | 200 | 15364 (0) | 0 / 0 / 0 / 0 / 0 | 13404 | 0 | 572 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 13 / 20 / 27 | 278 | 182 | 15576 (0) | 0 / 0 / 0 / 0 / 0 | 14134 | 0 | 560 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 14 / 20 / 27 | 254 | 170 | 14944 (0) | 0 / 0 / 0 / 0 / 0 | 12584 | 0 | 562 |

### Rybki w kieszeni przy Strażnikach — świat „po zmianie D-107 (pliki gry)” (mediana: posiadane / zarobione do tej chwili; przedmiotów ze sklepu)

| Sposób gry | Klasa | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla |
|---|---|---|---|---|
| Tylko walki | Wojownik | 2706 / 4030; 0 szt. | 2884 / 11512; 0 szt. | 2484 / 21074; 0 szt. |
| Tylko walki | Zwiadowca | 2698 / 4372; 0 szt. | 2846 / 10483; 0 szt. | 2786 / 19510; 0 szt. |
| Tylko walki | Mag | 2864 / 4368; 0 szt. | 2538 / 10038; 0 szt. | 3101 / 19801; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 3270 / 3644; 0 szt. | 7210 / 9119; 0 szt. | 18572 / 22668; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 3140 / 3494; 0 szt. | 8226 / 9416; 0 szt. | 19018 / 22953; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Mag | 2687 / 3622; 0 szt. | 7632 / 9719; 0 szt. | 18316 / 22660; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 1712 / 3492; 0 szt. | 2782 / 9350; 0 szt. | 6762 / 23560; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 1511 / 3122; 0 szt. | 3441 / 9548; 0 szt. | 8087 / 23964; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 1400 / 3151; 0 szt. | 3148 / 9625; 0 szt. | 8274 / 23660; 0 szt. |
| Wszystko + sklep z przedmiotami | Wojownik | 1227 / 3298; 3 szt. | 1477 / 9571; 5 szt. | 3600 / 23886; 6 szt. |
| Wszystko + sklep z przedmiotami | Zwiadowca | 1216 / 3119; 3 szt. | 1866 / 9734; 5 szt. | 4953 / 24052; 6 szt. |
| Wszystko + sklep z przedmiotami | Mag | 1080 / 3389; 2 szt. | 2062 / 9464; 3 szt. | 4080 / 23336; 3 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 1318 / 3038; 2 szt. | 1496 / 9938; 5 szt. | 4717 / 24504; 6 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 1249 / 3032; 4 szt. | 2387 / 9906; 5 szt. | 3956 / 24405; 6 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 1154 / 3112; 1 szt. | 1882 / 9589; 3 szt. | 3158 / 24060; 4 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 1316 / 1377; 0 szt. | 1878 / 3962; 0 szt. | 3512 / 6620; 0 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 1259 / 1326; 0 szt. | 2609 / 3838; 0 szt. | 3465 / 6479; 0 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 1194 / 1381; 0 szt. | 2414 / 4818; 0 szt. | 4293 / 7545; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 2072 / 3188; 0 szt. | 1970 / 8493; 0 szt. | 1843 / 15364; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 1646 / 2878; 0 szt. | 2160 / 8092; 0 szt. | 1959 / 15576; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 2000 / 3473; 0 szt. | 1885 / 7650; 0 szt. | 2373 / 14944; 0 szt. |

### Strażnicy — świat „po zmianie D-107 (pliki gry)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · wygrana za pierwszym razem · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki | Wojownik | poz. 10 · 10 / 13 · 1. raz 2% · 90% | poz. 18 · 17 / 33 · 1. raz 5% · 85% | poz. 25 · 16 / 40 · 1. raz 2% · 90% |
| Tylko walki | Zwiadowca | poz. 10 · 9 / 13 · 1. raz 5% · 75% | poz. 17 · 14 / 22 · 1. raz 2% · 88% | poz. 24 · 13 / 30 · 1. raz 2% · 78% |
| Tylko walki | Mag | poz. 10 · 8 / 12 · 1. raz 2% · 72% | poz. 17 · 16 / 27 · 1. raz 0% · 90% | poz. 24 · 18 / 42 · 1. raz 0% · 95% |
| Walki + trening AFK (10 min na godzinę) | Wojownik | poz. 10 · 3 / 4 · 1. raz 28% · 0% | poz. 16 · 3 / 6 · 1. raz 20% · 20% | poz. 23 · 1 / 3 · 1. raz 52% · 0% |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | poz. 10 · 2 / 5 · 1. raz 28% · 5% | poz. 16 · 2 / 4 · 1. raz 45% · 0% | poz. 23 · 2 / 3 · 1. raz 42% · 0% |
| Walki + trening AFK (10 min na godzinę) | Mag | poz. 10 · 3 / 6 · 1. raz 10% · 15% | poz. 16 · 2 / 5 · 1. raz 25% · 0% | poz. 23 · 2 / 3 · 1. raz 50% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | poz. 10 · 2 / 4 · 1. raz 30% · 0% | poz. 16 · 1 / 3 · 1. raz 55% · 0% | poz. 23 · 1 / 1 · 1. raz 90% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | poz. 10 · 1 / 3 · 1. raz 52% · 0% | poz. 16 · 1 / 2 · 1. raz 72% · 0% | poz. 23 · 1 / 3 · 1. raz 72% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Mag | poz. 10 · 2 / 4 · 1. raz 30% · 2% | poz. 16 · 2 / 3 · 1. raz 50% · 0% | poz. 23 · 1 / 2 · 1. raz 58% · 0% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 2 / 3 · 1. raz 48% · 0% | poz. 16 · 1 / 2 · 1. raz 72% · 0% | poz. 23 · 1 / 2 · 1. raz 88% · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 1 / 2 · 1. raz 60% · 0% | poz. 16 · 1 / 2 · 1. raz 75% · 0% | poz. 23 · 1 / 2 · 1. raz 82% · 0% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 3 / 5 · 1. raz 22% · 0% | poz. 16 · 2 / 3 · 1. raz 48% · 0% | poz. 23 · 1 / 2 · 1. raz 85% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | poz. 10 · 1 / 1 · 1. raz 95% · 0% | poz. 16 · 1 / 1 · 1. raz 100% · 0% | poz. 23 · 1 / 1 · 1. raz 100% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | poz. 10 · 1 / 1 · 1. raz 92% · 0% | poz. 16 · 1 / 1 · 1. raz 98% · 0% | poz. 23 · 1 / 1 · 1. raz 100% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | poz. 10 · 1 / 3 · 1. raz 52% · 0% | poz. 16 · 1 / 1 · 1. raz 90% · 0% | poz. 23 · 1 / 1 · 1. raz 100% · 0% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | poz. 4 · 5 / 6 · 1. raz 0% · 28% | poz. 11 · 12 / 17 · 1. raz 0% · 98% | poz. 16 · 2 / 6 · 1. raz 28% · 20% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | poz. 4 · 4 / 6 · 1. raz 0% · 15% | poz. 10 · 10 / 16 · 1. raz 0% · 90% | poz. 16 · 2 / 6 · 1. raz 42% · 12% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | poz. 4 · 10 / 11 · 1. raz 0% · 92% | poz. 12 · 12 / 15 · 1. raz 8% · 82% | poz. 17 · 2 / 7 · 1. raz 35% · 15% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 13 / 17 · 1. raz 0% · 98% | poz. 17 · 22 / 31 · 1. raz 0% · 95% | poz. 24 · 27 / 49 · 1. raz 0% · 90% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 12 / 17 · 1. raz 2% · 90% | poz. 16 · 14 / 29 · 1. raz 2% · 92% | poz. 23 · 19 / 38 · 1. raz 0% · 95% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 12 / 17 · 1. raz 5% · 92% | poz. 16 · 23 / 36 · 1. raz 2% · 95% | poz. 23 · 20 / 44 · 1. raz 2% · 92% |

### Nuda i przestoje — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki | Wojownik | 11 min (dzungla/straznik) | 40 min (bagno/straznik) | 21 × Zwijogon | 0,0 min |
| Tylko walki | Zwiadowca | 9,9 min (dzungla/straznik) | 31 min (dzungla/straznik) | 22 × Zwijogon | 0,0 min |
| Tylko walki | Mag | 9,0 min (dzungla/straznik) | 29 min (dzungla/straznik) | 19 × Zwijogon | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 11 min (dzungla/z1) | 15 min (bagno/b1) | 25 × Kokosowy Siłacz | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 10 min (dzungla/z1) | 14 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Mag | 9,9 min (dzungla/o1) | 14 min (dzungla/g1) | 24 × Kokosowy Siłacz | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 12 min (bagno/r1) | 16 min (bagno/b1) | 23 × Kokosowy Siłacz | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 11 min (bagno/b1) | 14 min (dzungla/g1) | 24 × Zwijogon | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 10 min (bagno/b1) | 14 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Wojownik | 11 min (bagno/b1) | 14 min (bagno/b1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 min (dzungla/g1) | 14 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Mag | 10 min (dzungla/g1) | 13 min (dzungla/g1) | 23 × Kokosowy Siłacz | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 16 min (bagno/r1) | 20 min (bagno/k1) | 23 × Kokosowy Siłacz | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 16 min (dzungla/z1) | 18 min (dzungla/o1) | 22 × Kokosowy Siłacz | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 15 min (dzungla/z1) | 18 min (dzungla/o1) | 22 × Kokosowy Siłacz | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 13 min (bagno/straznik) | 18 min (bagno/straznik) | 4 × Bulgotnik | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 13 min (dzungla/straznik) | 13 min (dzungla/straznik) | 2 × Bulgotnik | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 13 min (bagno/straznik) | 19 min (bagno/straznik) | 6 × Rechotek | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 5,8 min (dzungla/z1) | 23 min (dzungla/straznik) | 18 × Zwijogon | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 5,9 min (dzungla/z1) | 20 min (dzungla/o1) | 20 × Zwijogon | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 5,5 min (dzungla/z1) | 21 min (dzungla/straznik) | 18 × Zwijogon | 0,0 min |

### Gdzie schodzi czas — „Tylko walki”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,7 | 10 | 2,3 |
| las/m1 | Muchomornik (3–5) | 3 | 5,7 | 18 | 4,7 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 5,0 | 24 | 6,7 |
| las/t1 | Leśny Troll (8–9) | 8 | 6,3 | 14 | 8,7 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 14 | 9 | 8,0 |
| bagno/r1 | Rechotek (10–12) | 14 | 1,1 | 37 | 13 |
| bagno/b1 | Bulgotnik (12–14) | 14 | 6,1 | 13 | 8,2 |
| bagno/k1 | Kłodokłap (14–16) | 15 | 12 | 8 | 4,8 |
| bagno/t1 | Ropucha z Chatką (16–16) | 17 | 0,8 | 18 | 15 |
| bagno/straznik | Strażnik Topieli (16–16) | 17 | 22 | 16 | 15 |
| dzungla/z1 | Zwijogon (17–19) | 20 | 1,8 | 57 | 22 |
| dzungla/g1 | Gębokwiat (19–21) | 21 | 4,4 | 13 | 8,5 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 22 | 17 | 6 | 3,8 |
| dzungla/t1 | Pancernik Ruin (23–23) | 24 | 1,3 | 16 | 16 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 24 | 21 | 16 | 15 |

### Gdzie schodzi czas — „Walki + AFK + sklep trenera + pety + kowal”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 7,1 | 3 | 0,0 |
| las/m1 | Muchomornik (3–5) | 3 | 4,4 | 11 | 0,0 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 5,7 | 16 | 1,2 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,6 | 5 | 2,2 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 3,5 | 2 | 0,7 |
| bagno/r1 | Rechotek (10–12) | 11 | 2,9 | 7 | 0,7 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 14 | 14 | 2,0 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 8,1 | 17 | 0,3 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 1,1 | 1 | 0,3 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 2,0 | 1 | 0,2 |
| dzungla/z1 | Zwijogon (17–19) | 17 | 12 | 21 | 2,3 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 11 | 22 | 1,0 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 8,5 | 23 | 0,3 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,5 | 1 | 0,0 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 1,2 | 1 | 0,0 |

### Szansa wygranej ze Strażnikiem (%) — pula statystyk „gra”, liczby z plików gry

„Sam” = bohater bez treningu i przedmiotów na poziomie Strażnika −1 / 0 / +1 / +2. „AFK” = na poziomie Strażnika po 5 / 15 / 30 minutach na stanowiskach (bez ulepszeń, bez skill checków, czas dzielony na trzy główne statystyki klasy). „Kowal +2” = pełny zestaw kowala ulepszony o 2, bez treningu. Ostatnia kolumna: ile minut AFK daje 50% / 80% wygranych.

| Strażnik | Klasa | Sam: -1 / +0 / +1 / +2 | AFK: 5 / 15 / 30 min | Kowal +2 | Minut AFK do 50% / 80% |
|---|---|---|---|---:|---|
| Strażnik Gaju (poz. 10) | Wojownik | 0 / 1 / 3 / 12 | 39 / 100 / 100 | 11 | 6,6 / 9,4 |
| Strażnik Gaju (poz. 10) | Zwiadowca | 0 / 2 / 7 / 14 | 38 / 99 / 100 | 14 | 6,6 / 9,4 |
| Strażnik Gaju (poz. 10) | Mag | 0 / 1 / 4 / 13 | 45 / 100 / 100 | 16 | 5,6 / 8,4 |
| Strażnik Topieli (poz. 16) | Wojownik | 0 / 0 / 0 / 1 | 7 / 85 / 100 | 3 | 10 / 14 |
| Strażnik Topieli (poz. 16) | Zwiadowca | 0 / 2 / 2 / 6 | 15 / 74 / 100 | 5 | 11 / 18 |
| Strażnik Topieli (poz. 16) | Mag | 0 / 0 / 2 / 3 | 9 / 64 / 98 | 3 | 12 / 19 |
| Wąż Stu Lian (poz. 23) | Wojownik | 1 / 0 / 1 / 1 | 5 / 56 / 99 | 2 | 16 / 20 |
| Wąż Stu Lian (poz. 23) | Zwiadowca | 1 / 3 / 4 / 6 | 11 / 54 / 93 | 5 | 14 / 24 |
| Wąż Stu Lian (poz. 23) | Mag | 1 / 1 / 1 / 4 | 9 / 47 / 92 | 2 | 14 / 22 |

### Szansa wygranej ze Strażnikiem (%) — po propozycji „A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200”

„Sam” = bohater bez treningu i przedmiotów na poziomie Strażnika −1 / 0 / +1 / +2. „AFK” = na poziomie Strażnika po 5 / 15 / 30 minutach na stanowiskach (bez ulepszeń, bez skill checków, czas dzielony na trzy główne statystyki klasy). „Kowal +2” = pełny zestaw kowala ulepszony o 2, bez treningu. Ostatnia kolumna: ile minut AFK daje 50% / 80% wygranych.

| Strażnik | Klasa | Sam: -1 / +0 / +1 / +2 | AFK: 5 / 15 / 30 min | Kowal +2 | Minut AFK do 50% / 80% |
|---|---|---|---|---:|---|
| Strażnik Gaju (poz. 10) | Wojownik | 21 / 38 / 55 / 77 | 86 / 92 / 96 | 67 | 0,9 / 4,7 |
| Strażnik Gaju (poz. 10) | Zwiadowca | 18 / 42 / 58 / 72 | 78 / 90 / 92 | 60 | 1,9 / 4,7 |
| Strażnik Gaju (poz. 10) | Mag | 17 / 31 / 52 / 72 | 89 / 92 / 96 | 68 | 1,9 / 3,8 |
| Strażnik Topieli (poz. 16) | Wojownik | 17 / 26 / 35 / 53 | 65 / 87 / 91 | 38 | 2,8 / 9,4 |
| Strażnik Topieli (poz. 16) | Zwiadowca | 21 / 34 / 39 / 47 | 66 / 72 / 81 | 41 | 3,8 / 19 |
| Strażnik Topieli (poz. 16) | Mag | 12 / 22 / 30 / 45 | 54 / 69 / 75 | 38 | 4,7 / 40 |
| Wąż Stu Lian (poz. 23) | Wojownik | 24 / 28 / 38 / 45 | 59 / 81 / 88 | 43 | 4,7 / 10 |
| Wąż Stu Lian (poz. 23) | Zwiadowca | 29 / 31 / 39 / 42 | 53 / 76 / 80 | 37 | 4,7 / 31 |
| Wąż Stu Lian (poz. 23) | Mag | 24 / 29 / 35 / 45 | 50 / 78 / 81 | 38 | 4,7 / 21 |

### Propozycje zmian liczb — „przed / po” (świat „po zmianie D-107 (pliki gry)”, mediana z trzech klas)

Liczone na kopii danych; pliki gry bez zmian. Kolumny: minuty do końca (razem z AFK) · w tym AFK · różnica między klasami (najwolniejsza − najszybsza) · przegranych · wygrana ze Strażnikiem za pierwszym razem i ilu graczy na nim utknęło (Las / Bagno / Dżungla) · najdłuższa seria jednego potwora · najdłużej bez awansu · punkty z treningu · Rybki stracone po przegranych · wydane u trenera.

**Tylko walki**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Bez zmian (liczby z plików gry) | 130 | 0,0 | 28 | 163 | 3 / 2 / 2 | 79 / 88 / 88 | 20 | 10 | 0 | 17140 | 0 |
| A: 10 punktów za poziom rozdzielanych samo | 68 | 0,0 | 7,9 | 46 | 33 / 25 / 35 | 2 / 9 / 15 | 24 | 5,6 | 0 | 6787 | 0 |
| B: limit treningu 2 × poziom na statystykę (ponad limitem pasek ×10) | 130 | 0,0 | 28 | 163 | 3 / 2 / 2 | 79 / 88 / 88 | 20 | 10 | 0 | 17140 | 0 |
| A + B | 68 | 0,0 | 7,9 | 46 | 33 / 25 / 35 | 2 / 9 / 15 | 24 | 5,6 | 0 | 6787 | 0 |
| A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200 | 68 | 0,0 | 7,9 | 46 | 33 / 25 / 35 | 2 / 9 / 15 | 24 | 5,6 | 0 | 6787 | 0 |
| Dla porównania: A + B i doświadczenie Dżungli +25% (pytanie 70) | 63 | 0,0 | 7,9 | 42 | 33 / 25 / 29 | 2 / 9 / 8 | 20 | 5,2 | 0 | 6010 | 0 |
| Dla porównania: A + B i krzywa doświadczenia ×1,5 (dłuższa gra) | 99 | 0,0 | 7,0 | 70 | 31 / 24 / 28 | 2 / 15 / 12 | 37 | 7,9 | 0 | 10518 | 0 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 461 | 0,0 | 79 | 581 | 0 / 4 / 1 | 100 / 93 / 94 | 49 | 23 | 0 | 57407 | 0 |

**Walki + trening AFK (10 min na godzinę)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Bez zmian (liczby z plików gry) | 85 | 17 | 11 | 29 | 22 / 30 / 48 | 7 / 7 / 0 | 24 | 10 | 186 | 4125 | 0 |
| A: 10 punktów za poziom rozdzielanych samo | 72 | 17 | 4,8 | 8 | 75 / 78 / 83 | 0 / 0 / 0 | 23 | 9,7 | 186 | 1200 | 0 |
| B: limit treningu 2 × poziom na statystykę (ponad limitem pasek ×10) | 107 | 22 | 16 | 76 | 2 / 10 / 22 | 56 / 48 / 27 | 16 | 12 | 105 | 10254 | 0 |
| A + B | 78 | 17 | 5,8 | 27 | 47 / 50 / 59 | 1 / 2 / 1 | 24 | 10 | 84 | 3759 | 0 |
| A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200 | 78 | 17 | 5,8 | 27 | 47 / 50 / 59 | 1 / 2 / 1 | 24 | 10 | 84 | 3759 | 0 |
| Dla porównania: A + B i doświadczenie Dżungli +25% (pytanie 70) | 73 | 17 | 5,4 | 24 | 47 / 50 / 68 | 1 / 2 / 1 | 20 | 9,7 | 85 | 3426 | 0 |
| Dla porównania: A + B i krzywa doświadczenia ×1,5 (dłuższa gra) | 108 | 23 | 7,9 | 34 | 43 / 48 / 68 | 1 / 0 / 0 | 37 | 12 | 107 | 4659 | 0 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 148 | 31 | 34 | 118 | 0 / 10 / 5 | 97 / 72 / 72 | 17 | 14 | 235 | 13937 | 0 |

**Walki + AFK + sklep trenera + pety + kowal**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Bez zmian (liczby z plików gry) | 89 | 18 | 9,6 | 15 | 38 / 59 / 73 | 1 / 0 / 0 | 23 | 11 | 194 | 801 | 400 |
| A: 10 punktów za poziom rozdzielanych samo | 80 | 18 | 6,0 | 4 | 89 / 94 / 93 | 0 / 0 / 0 | 22 | 9,7 | 203 | 151 | 1117 |
| B: limit treningu 2 × poziom na statystykę (ponad limitem pasek ×10) | 107 | 22 | 18 | 49 | 7 / 26 / 45 | 16 / 13 / 6 | 23 | 11 | 103 | 2060 | 733 |
| A + B | 84 | 18 | 5,6 | 15 | 60 / 63 / 81 | 0 / 0 / 0 | 23 | 10 | 79 | 765 | 300 |
| A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200 | 84 | 18 | 5,6 | 15 | 60 / 64 / 79 | 0 / 0 / 0 | 23 | 10 | 80 | 751 | 500 |
| Dla porównania: A + B i doświadczenie Dżungli +25% (pytanie 70) | 80 | 18 | 5,0 | 14 | 60 / 63 / 83 | 0 / 0 / 0 | 19 | 10 | 80 | 688 | 533 |
| Dla porównania: A + B i krzywa doświadczenia ×1,5 (dłuższa gra) | 113 | 24 | 7,1 | 16 | 72 / 74 / 84 | 0 / 0 / 0 | 35 | 12 | 115 | 1018 | 3550 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 134 | 27 | 22 | 84 | 2 / 7 / 23 | 80 / 48 / 30 | 18 | 13 | 208 | 2729 | 400 |

**Gracz AFK (20 min na godzinę, wszystko)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Bez zmian (liczby z plików gry) | 109 | 43 | 5,8 | 4 | 80 / 96 / 100 | 0 / 0 / 0 | 22 | 16 | 516 | 50 | 533 |
| A: 10 punktów za poziom rozdzielanych samo | 97 | 36 | 15 | 1 | 97 / 99 / 100 | 0 / 0 / 0 | 22 | 15 | 421 | 23 | 100 |
| B: limit treningu 2 × poziom na statystykę (ponad limitem pasek ×10) | 123 | 43 | 9,3 | 30 | 13 / 57 / 60 | 0 / 1 / 0 | 24 | 16 | 121 | 810 | 50 |
| A + B | 109 | 43 | 4,7 | 9 | 72 / 73 / 90 | 0 / 0 / 0 | 23 | 16 | 131 | 235 | 300 |
| A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200 | 109 | 43 | 4,6 | 9 | 72 / 72 / 89 | 0 / 0 / 0 | 23 | 16 | 132 | 238 | 433 |
| Dla porównania: A + B i doświadczenie Dżungli +25% (pytanie 70) | 101 | 40 | 16 | 8 | 72 / 73 / 87 | 0 / 0 / 0 | 18 | 15 | 117 | 207 | 100 |
| Dla porównania: A + B i krzywa doświadczenia ×1,5 (dłuższa gra) | 142 | 54 | 6,3 | 9 | 79 / 87 / 96 | 0 / 0 / 0 | 35 | 17 | 155 | 458 | 3400 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 154 | 58 | 32 | 57 | 8 / 22 / 36 | 51 / 27 / 2 | 21 | 18 | 236 | 1227 | 100 |

**AFK 20 min/h i przeskakiwanie zagród (pytanie 117)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Bez zmian (liczby z plików gry) | 47 | 22 | 5,6 | 36 | 0 / 2 / 35 | 45 / 90 / 16 | 4 | 13 | 334 | 2176 | 883 |
| A: 10 punktów za poziom rozdzielanych samo | 34 | 14 | 15 | 24 | 7 / 10 / 14 | 16 / 48 / 52 | 2 | 12 | 214 | 2178 | 333 |
| B: limit treningu 2 × poziom na statystykę (ponad limitem pasek ×10) | 77 | 33 | 5,0 | 91 | 0 / 5 / 10 | 99 / 68 / 63 | 13 | 15 | 114 | 5496 | 1450 |
| A + B | 47 | 22 | 3,6 | 45 | 0 / 1 / 10 | 89 / 68 / 50 | 6 | 14 | 65 | 2749 | 1000 |
| A + B + C: ulepszenia stanowisk 150 / 350 / 800 / 1800 / 4200 | 48 | 22 | 3,5 | 46 | 0 / 1 / 10 | 89 / 68 / 49 | 6 | 14 | 65 | 2775 | 1300 |
| Dla porównania: A + B i doświadczenie Dżungli +25% (pytanie 70) | 47 | 22 | 2,1 | 44 | 0 / 1 / 9 | 89 / 68 / 45 | 5 | 13 | 65 | 2655 | 1000 |
| Dla porównania: A + B i krzywa doświadczenia ×1,5 (dłuższa gra) | 54 | 22 | 7,2 | 63 | 0 / 8 / 8 | 98 / 73 / 66 | 9 | 14 | 58 | 3800 | 700 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 105 | 40 | 20 | 129 | 0 / 18 / 7 | 100 / 55 / 72 | 16 | 15 | 242 | 8564 | 2567 |

_Uruchomienie: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 40 --ziarno 1` · 40 przebiegów na komórkę · krzywa doświadczenia 11,71 × L^1,6 · pula statystyk „gra” · trening AFK: pasek 4 × 1,2 s, +1 za pasek (750 punktów na godzinę na stanowisku) · katalog sklepu: swiat/postacie/sklep_liczby.json · liczone 2026-11-27._

<!-- TABELE:KONIEC -->
