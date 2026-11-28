# Balans 27.11 — przejście trzech biomów z treningiem AFK, sklepem trenera, Rybkami i Diamentami

> **PROPOZYCJA, NIE KANON.** Liczone offline (port silnika walki, dane czytane z plików gry 27.11), bez Studio.
> Żadne pliki gry nie zostały zmienione — zmiany niżej to diffy do decyzji. Autor: agent Karola, 27.11.2026.

## Na telefon (krótko)

- **Dziś gra bez treningu AFK prawie nie przechodzi.** Za poziom wchodzi tylko 5 punktów statystyk (drugich 5 „do rozdania” nie ma czym wydać od 24.11), a potwory są strojone pod 10. Gracz, który tylko walczy: ok. **130 min**, ze Strażnikiem wygrywa za pierwszym razem w 2–5% prób, **72–95% graczy odbija się od Strażnika 5+ razy**, kara za przegrane zabiera mu **85% zarobionych Rybek**.
- **Trening AFK jest za mocny (pytanie 117 potwierdzone).** 15 min na stanowiskach daje wygraną ze Strażnikiem Gaju w 99–100%, Topieli 64–85%, Węża 47–56%. Minuta AFK oszczędza **3,6 min walki**. Gracz, który trenuje i pcha do przodu, kończy grę w **47 min** i bije Węża na 18. poziomie zamiast 23.
- **Propozycja (dwie dźwignie):** **A** — 10 punktów za poziom rozdzielanych samo (jedna stała w stanie gracza); **B** — limit treningu: najwyżej 2 × poziom punktów na statystykę, powyżej pasek 10× wolniej (dwie nowe liczby w `TreningAFKDane`). Po A + B: sama walka **68 min** i do 15% utkniętych; typowy gracz (walki + 10 min AFK na godzinę + kowal + pety) **84 min**, Strażnik za pierwszym razem 60 / 63 / 81%; minuta AFK oszczędza 0,4 min walki.
- **Do decyzji Karola i Pawła:** A kłóci się z **D-140** (za poziom tylko Diamenty). Symulacja D-140 bez punktów za poziom: sama walka ok. **461 min**, 100% utkniętych u Strażnika Gaju — D-140 wymaga dużo większego treningu albo słabszych potworów. Długość gry: 84 min wobec roboczego celu 30 / 45 / 60 min na biom (D-076); wydłużenie krzywą doświadczenia ×1,5 daje 113 min, ale serie jednego potwora rosną z 23 do 35 walk.

Szczegóły: niżej — co liczy symulator, cele ze źródłami, krzywa dziś, propozycja w liczbach z diffami, otwarte punkty i pełne tabele.

## Wdrożone 27.11 (decyzja Karola, czeka na Pawła)

Karol 27.11 (okno wyboru): „A + B (zalecane)” i „Tak, +25%” (pytanie 70). Zmienia D-140; Paweł potwierdzi albo się sprzeciwi. Każda dźwignia to jedna nazwana liczba — powrót w jednym miejscu:

| Dźwignia | Plik | Liczba (było → jest) | Powrót |
|---|---|---|---|
| A | `swiat/stan_gracza/dane.py` | `PUNKTY_SAMO_NA_POZIOM` 5 → 10, `PUNKTY_DO_ROZDANIA` 5 → 0 | 5 i 5 |
| B | `src/shared/TreningAFKDane.luau` | `D.limitNaPoziom` — → 2, `D.ponadLimitem` — → 0.1 (napis `D.tekstLimitu`) | `limitNaPoziom = 0` |
| XP Dżungli | `swiat/dzungla_pas_gra/przeciwnicy.py` | `MNOZNIK_DOSWIADCZENIA` — → 1.25 | 1.0 |

Do tego: stan gracza wystawia wytrenowane punkty każdej statystyki jako atrybuty gracza `Wytrenowane<Atrybut>` (np. `WytrenowaneStrength`; z profilu „wytrenowane”, który był już w zapisie — stare zapisy bez zmian); serwer treningu liczy od nich limit i dolicza po każdym pasku; panel treningu ponad limitem pokazuje „LIMIT: LEVEL UP TO TRAIN FASTER” zamiast podpowiedzi o skill checkach.

**Symulacja na prawdziwych danych po zmianie** (nie na nakładce propozycji; 40 graczy na klasę) — zgodna z propozycją „A + B + XP Dżungli ×1,25” liczba w liczbę:

| Sposób gry | Przed 27.11 | Po wdrożeniu | Strażnik za 1. razem po | Utknęło po |
|---|---:|---:|---|---|
| Tylko walki | 130 min | **63 min** | 33 / 25 / 29% | 2 / 9 / 8% |
| Walki + 10 min AFK/h | 85 (17 AFK) | **73 (17 AFK)** | 47 / 50 / 68% | 1 / 2 / 1% |
| Typowy (AFK + kowal + pety + trener) | 89 | **80** | **60 / 63 / 83%** | 0% |
| Gracz AFK 20 min/h | 109 (43 AFK) | 101 (40 AFK) | 72 / 73 / 87% | 0% |
| AFK i przeskakiwanie | 47 | 47 (ale ok. 44 przegranych; Węża bije na 19. poziomie, było 17–18.) | 0 / 1 / 9% | 89 / 68 / 45% |

Minuta AFK oszczędza teraz **0,41 min walki** (było 3,6). Typowy gracz: 80 min, a nie 84, bo doliczone jest doświadczenie Dżungli ×1,25 (bez niego 84). Seria jednego potwora 23 → 19–20. Sam bohater na poziomie Strażnika: 17–42% (było 0–3%).

Uwaga: przeskakujący gracz nadal kończy w 47 min — ale nie dzięki treningowi (punkty z AFK 334 → 65), tylko przez pomijanie walk i dziesiątki przegranych ze Strażnikami; to sprawa stylu, nie limitu.

**Wdrożone w Studio 27.11 ok. 18:15–18:40 i sprawdzone w trybie Play** (miejsce niezapisane — zapisuje koordynator):
- stan gracza: S14 — awans 3 → 4 daje dokładnie +10 do sumy statystyk samo, licznik „Punkty do rozdania” schowany, atrybuty `Wytrenowane*` są (zrzut `swiat/stan_gracza/klatki/15_awans_10_punktow.jpg`); cała próba bez błędów, próba zapisu Z00–Z08 OK;
- trening AFK: L01 — przy limicie 4 punktów cztery paski co 4,81 s, potem `TreningAFKLimit` i czerwony napis „LIMIT: LEVEL UP TO TRAIN FASTER”; L02 — następny pasek **47,97 s** (10 × 4,8 s); 28 z 28 punktów próby OK;
- Dżungla: J08b — wygrana z Zwijogonem 19. poziomu dała **142 XP** (z mnożnikiem 137–168, bez niego najwyżej 134); próba Dżungli bez błędów;
- próba dymna całej gry D00–D14 OK (90 s).

Co gracz zobaczy inaczej (sprawdzone w kodzie):
- licznik „Punkty do rozdania” na dole ekranu znika (0); stare zapisy: niewydana pula (5 za każdy dawny poziom) znika przy pierwszym przeliczeniu, a jej wartość daje teraz pula rozdzielana samo (+5 na poziom więcej);
- komunikat „Brak punktów — zdobądź poziom” pokazuje się tylko przy zmianie statystyki spoza serwera (przycisków „+” nie ma od 24.11) — tekst jest już nieprawdziwy, ale gracz do niego nie dojdzie;
- Diamenty za poziom (10) i za Strażnika (100) zostają; drzewko dalej nie wpływa na walkę (D-140 w części o Diamentach nie jest wdrożona w walce);
- limit liczy się na początku treningu i po każdym pasku — awans w trakcie stania na macie zmienia tempo dopiero od następnego paska (awansu w trakcie treningu w grze nie ma, poza paskiem poleceń);
- ponad limitem podpowiedź panelu zmienia się na czerwone „LIMIT: LEVEL UP TO TRAIN FASTER”, a pasek trwa ok. 48 s.

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

Od przeliczenia po wdrożeniu (27.11 wieczorem) tabele niżej opisują grę PO zmianach A + B + XP Dżungli (pliki gry); stan sprzed 27.11 jest w porównaniach („Przed 27.11”) i w drugiej tabeli Strażników. Liczby z sekcji 3 i 4 to stan sprzed wdrożenia. „Najdłużej bez awansu” liczy się razem z czasem na stanowiskach.

<!-- TABELE:START -->

### Czasy do kamieni milowych — świat „po zmianie D-107 (pliki gry)” (minuty gry, mediana)

| Sposób gry | Klasa | 1. wygrana | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla | Koniec: 10%–90% graczy | W tym AFK | Skończyło |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Tylko walki | Wojownik | 0,8 | 18 | 40 | 67 | 63–72 | 0,0 | 100% |
| Tylko walki | Zwiadowca | 0,8 | 18 | 40 | 65 | 60–71 | 0,0 | 100% |
| Tylko walki | Mag | 0,7 | 16 | 38 | 59 | 54–65 | 0,0 | 100% |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 0,8 | 22 | 47 | 76 | 73–80 | 17 | 100% |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 0,7 | 21 | 47 | 74 | 71–78 | 17 | 100% |
| Walki + trening AFK (10 min na godzinę) | Mag | 0,7 | 21 | 45 | 70 | 63–74 | 17 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 0,7 | 24 | 53 | 82 | 79–85 | 18 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 0,8 | 23 | 51 | 81 | 77–85 | 18 | 100% |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 0,7 | 22 | 49 | 77 | 73–80 | 18 | 100% |
| Wszystko + sklep z przedmiotami | Wojownik | 0,7 | 24 | 53 | 84 | 80–87 | 17 | 100% |
| Wszystko + sklep z przedmiotami | Zwiadowca | 0,7 | 24 | 52 | 82 | 78–85 | 17 | 100% |
| Wszystko + sklep z przedmiotami | Mag | 0,7 | 23 | 50 | 78 | 75–82 | 17 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 0,7 | 28 | 62 | 107 | 94–110 | 43 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 0,7 | 29 | 60 | 106 | 92–108 | 43 | 100% |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 0,7 | 28 | 59 | 91 | 90–94 | 32 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 0,6 | 18 | 30 | 48 | 45–51 | 22 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 0,6 | 18 | 28 | 46 | 44–49 | 22 | 100% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 0,6 | 19 | 28 | 46 | 44–51 | 22 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 0,6 | 10 | 24 | 40 | 37–44 | 0,0 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 0,5 | 9,9 | 24 | 40 | 37–44 | 0,0 | 100% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 0,6 | 9,7 | 23 | 38 | 34–42 | 0,0 | 100% |

Czas gry liczony razem ze staniem na stanowiskach AFK (kolumna „W tym AFK”). Brama otwiera się od razu po wygranej ze Strażnikiem; dokładne czasy bram są w pliku JSON (pola `brama_…`).

### Minut na krainę — świat „po zmianie D-107 (pliki gry)” (mediana; w nawiasie bez czasu AFK)

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---:|---:|---:|
| Tylko walki | Wojownik | 18 (18) | 22 (22) | 26 (26) |
| Tylko walki | Zwiadowca | 18 (18) | 21 (21) | 26 (26) |
| Tylko walki | Mag | 16 (16) | 21 (21) | 21 (21) |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 22 (16) | 26 (20) | 28 (22) |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 21 (15) | 26 (20) | 27 (22) |
| Walki + trening AFK (10 min na godzinę) | Mag | 21 (15) | 24 (18) | 25 (20) |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 24 (18) | 29 (23) | 30 (24) |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 23 (17) | 27 (21) | 29 (23) |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 22 (16) | 27 (22) | 27 (21) |
| Wszystko + sklep z przedmiotami | Wojownik | 24 (18) | 28 (23) | 30 (24) |
| Wszystko + sklep z przedmiotami | Zwiadowca | 24 (18) | 27 (21) | 29 (24) |
| Wszystko + sklep z przedmiotami | Mag | 23 (17) | 27 (21) | 28 (22) |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 28 (17) | 33 (22) | 45 (24) |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 29 (18) | 31 (20) | 39 (23) |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 28 (17) | 31 (20) | 32 (21) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 18 (7,3) | 11 (11) | 17 (7,5) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 18 (7,2) | 9,4 (9,4) | 18 (7,4) |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 19 (7,8) | 10 (10) | 17 (5,9) |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 10 (10) | 14 (14) | 16 (16) |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 9,7 (9,7) | 13 (13) | 17 (17) |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 9,5 (9,5) | 13 (13) | 15 (15) |

### Poziom, walki i Rybki — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Rybki zarobione (w tym zagroda) | Wydane: przedmioty / kowal / jajka / trener / zagroda | Stracone po przegranych | Punkty z treningu AFK | Diamenty |
|---|---|---|---:|---:|---:|---|---:|---:|---:|
| Tylko walki | Wojownik | 11 / 17 / 24 | 163 | 42 | 20852 (0) | 0 / 0 / 0 / 0 / 0 | 6108 | 0 | 532 |
| Tylko walki | Zwiadowca | 12 / 17 / 24 | 163 | 44 | 20548 (0) | 0 / 0 / 0 / 0 / 0 | 6402 | 0 | 532 |
| Tylko walki | Mag | 11 / 18 / 24 | 157 | 39 | 20791 (0) | 0 / 0 / 0 / 0 / 0 | 5519 | 0 | 532 |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 11 / 17 / 24 | 143 | 23 | 20690 (0) | 0 / 0 / 0 / 0 / 0 | 3291 | 84 | 532 |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 11 / 17 / 24 | 147 | 26 | 20708 (0) | 0 / 0 / 0 / 0 / 0 | 3750 | 85 | 532 |
| Walki + trening AFK (10 min na godzinę) | Mag | 11 / 17 / 24 | 144 | 24 | 20659 (0) | 0 / 0 / 0 / 0 / 0 | 3236 | 86 | 531 |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 11 / 17 / 24 | 134 | 13 | 21319 (471) | 0 / 6300 / 7200 / 300 / 0 | 560 | 79 | 532 |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 11 / 17 / 24 | 136 | 16 | 21528 (434) | 0 / 6050 / 7200 / 300 / 0 | 940 | 80 | 532 |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 11 / 17 / 24 | 132 | 14 | 21458 (450) | 0 / 6320 / 7200 / 1000 / 1000 | 564 | 82 | 532 |
| Wszystko + sklep z przedmiotami | Wojownik | 11 / 17 / 24 | 133 | 11 | 21692 (382) | 4900 / 5700 / 7200 / 0 / 0 | 242 | 77 | 532 |
| Wszystko + sklep z przedmiotami | Zwiadowca | 11 / 17 / 24 | 132 | 13 | 21570 (400) | 6000 / 5125 / 7200 / 0 / 0 | 358 | 78 | 532 |
| Wszystko + sklep z przedmiotami | Mag | 11 / 17 / 24 | 132 | 13 | 21546 (390) | 5000 / 5440 / 7200 / 0 / 0 | 276 | 80 | 531 |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 11 / 17 / 24 | 128 | 8 | 21756 (488) | 6250 / 5350 / 7200 / 300 / 0 | 184 | 130 | 531 |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 11 / 17 / 24 | 129 | 8 | 21765 (495) | 6300 / 4900 / 7200 / 0 / 0 | 248 | 128 | 532 |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 11 / 17 / 24 | 128 | 9 | 21528 (418) | 5150 / 4565 / 7200 / 0 / 0 | 188 | 94 | 531 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 10 / 16 / 19 | 70 | 46 | 6738 (0) | 0 / 0 / 0 / 1000 / 0 | 2580 | 65 | 481 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 10 / 15 / 19 | 66 | 41 | 7617 (0) | 0 / 0 / 0 / 1000 / 0 | 2750 | 65 | 481 |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 10 / 15 / 19 | 70 | 44 | 7264 (0) | 0 / 0 / 0 / 1000 / 0 | 2635 | 65 | 481 |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 11 / 16 / 23 | 150 | 60 | 16846 (0) | 0 / 0 / 0 / 0 / 0 | 8059 | 0 | 521 |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 11 / 16 / 23 | 151 | 60 | 17143 (0) | 0 / 0 / 0 / 0 / 0 | 8228 | 0 | 522 |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 11 / 17 / 23 | 144 | 52 | 17210 (0) | 0 / 0 / 0 / 0 / 0 | 6841 | 0 | 522 |

### Rybki w kieszeni przy Strażnikach — świat „po zmianie D-107 (pliki gry)” (mediana: posiadane / zarobione do tej chwili; przedmiotów ze sklepu)

| Sposób gry | Klasa | Strażnik: Las | Strażnik: Bagno | Strażnik: Dżungla |
|---|---|---|---|---|
| Tylko walki | Wojownik | 3036 / 3510; 0 szt. | 6916 / 9257; 0 szt. | 14516 / 20852; 0 szt. |
| Tylko walki | Zwiadowca | 2888 / 3316; 0 szt. | 6802 / 9342; 0 szt. | 14434 / 20548; 0 szt. |
| Tylko walki | Mag | 2834 / 3262; 0 szt. | 7758 / 9925; 0 szt. | 15153 / 20791; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 2997 / 3287; 0 szt. | 7846 / 9271; 0 szt. | 17410 / 20690; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 2916 / 3066; 0 szt. | 7616 / 9408; 0 szt. | 16852 / 20708; 0 szt. |
| Walki + trening AFK (10 min na godzinę) | Mag | 2910 / 3270; 0 szt. | 7968 / 9422; 0 szt. | 17524 / 20659; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 1516 / 3150; 0 szt. | 3302 / 9461; 0 szt. | 7062 / 21310; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 1443 / 3065; 0 szt. | 3346 / 9693; 0 szt. | 6592 / 21507; 0 szt. |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 1482 / 3055; 0 szt. | 3512 / 9871; 0 szt. | 6077 / 21452; 0 szt. |
| Wszystko + sklep z przedmiotami | Wojownik | 1234 / 3078; 3 szt. | 1769 / 9653; 4 szt. | 3219 / 21682; 5 szt. |
| Wszystko + sklep z przedmiotami | Zwiadowca | 1202 / 3184; 3 szt. | 2096 / 9592; 5 szt. | 3472 / 21566; 6 szt. |
| Wszystko + sklep z przedmiotami | Mag | 1322 / 3068; 1 szt. | 2360 / 9662; 2 szt. | 3672 / 21540; 3 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 1166 / 3041; 3 szt. | 1992 / 9785; 5 szt. | 2237 / 21739; 6 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 1109 / 3054; 4 szt. | 2278 / 9758; 5 szt. | 2898 / 21728; 6 szt. |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 1327 / 3012; 1 szt. | 2100 / 9908; 3 szt. | 3512 / 21520; 3 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 1259 / 1387; 0 szt. | 2308 / 4118; 0 szt. | 3021 / 6738; 0 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 1332 / 1447; 0 szt. | 2454 / 3828; 0 szt. | 3362 / 7617; 0 szt. |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 1218 / 1430; 0 szt. | 2565 / 4078; 0 szt. | 3327 / 7264; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 2189 / 2526; 0 szt. | 4096 / 7529; 0 szt. | 8476 / 16846; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 2075 / 2399; 0 szt. | 4380 / 7516; 0 szt. | 9396 / 17143; 0 szt. |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 2142 / 2508; 0 szt. | 4692 / 7948; 0 szt. | 10404 / 17210; 0 szt. |

### Strażnicy — świat „po zmianie D-107 (pliki gry)”

Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · wygrana za pierwszym razem · ilu graczy utknęło (co najmniej 5 przegranych prób).

| Sposób gry | Klasa | Las | Bagno | Dżungla |
|---|---|---|---|---|
| Tylko walki | Wojownik | poz. 10 · 2 / 4 · 1. raz 28% · 5% | poz. 16 · 2 / 4 · 1. raz 40% · 8% | poz. 23 · 2 / 5 · 1. raz 18% · 8% |
| Tylko walki | Zwiadowca | poz. 10 · 2 / 4 · 1. raz 32% · 0% | poz. 16 · 2 / 5 · 1. raz 18% · 2% | poz. 23 · 2 / 5 · 1. raz 32% · 10% |
| Tylko walki | Mag | poz. 10 · 2 / 5 · 1. raz 40% · 2% | poz. 16 · 3 / 6 · 1. raz 18% · 18% | poz. 23 · 2 / 5 · 1. raz 38% · 8% |
| Walki + trening AFK (10 min na godzinę) | Wojownik | poz. 10 · 2 / 3 · 1. raz 42% · 0% | poz. 16 · 2 / 4 · 1. raz 50% · 2% | poz. 23 · 1 / 2 · 1. raz 72% · 0% |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | poz. 10 · 1 / 3 · 1. raz 55% · 0% | poz. 16 · 2 / 4 · 1. raz 50% · 2% | poz. 23 · 1 / 3 · 1. raz 65% · 2% |
| Walki + trening AFK (10 min na godzinę) | Mag | poz. 10 · 2 / 3 · 1. raz 42% · 2% | poz. 16 · 2 / 3 · 1. raz 50% · 0% | poz. 23 · 1 / 2 · 1. raz 65% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | poz. 10 · 2 / 3 · 1. raz 50% · 0% | poz. 16 · 1 / 2 · 1. raz 68% · 0% | poz. 23 · 1 / 1 · 1. raz 92% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | poz. 10 · 1 / 2 · 1. raz 65% · 0% | poz. 16 · 1 / 2 · 1. raz 68% · 0% | poz. 23 · 1 / 2 · 1. raz 70% · 0% |
| Walki + AFK + sklep trenera + pety + kowal | Mag | poz. 10 · 1 / 3 · 1. raz 65% · 0% | poz. 16 · 1 / 3 · 1. raz 55% · 0% | poz. 23 · 1 / 2 · 1. raz 88% · 0% |
| Wszystko + sklep z przedmiotami | Wojownik | poz. 10 · 1 / 2 · 1. raz 70% · 0% | poz. 16 · 1 / 2 · 1. raz 78% · 0% | poz. 23 · 1 / 2 · 1. raz 75% · 0% |
| Wszystko + sklep z przedmiotami | Zwiadowca | poz. 10 · 1 / 3 · 1. raz 58% · 0% | poz. 16 · 1 / 3 · 1. raz 70% · 0% | poz. 23 · 1 / 2 · 1. raz 75% · 0% |
| Wszystko + sklep z przedmiotami | Mag | poz. 10 · 1 / 2 · 1. raz 62% · 0% | poz. 16 · 1 / 2 · 1. raz 70% · 0% | poz. 23 · 1 / 2 · 1. raz 85% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | poz. 10 · 1 / 2 · 1. raz 82% · 0% | poz. 16 · 1 / 2 · 1. raz 80% · 0% | poz. 23 · 1 / 2 · 1. raz 85% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | poz. 10 · 1 / 2 · 1. raz 62% · 0% | poz. 16 · 1 / 2 · 1. raz 75% · 0% | poz. 23 · 1 / 2 · 1. raz 80% · 0% |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | poz. 10 · 1 / 2 · 1. raz 70% · 0% | poz. 16 · 1 / 2 · 1. raz 65% · 0% | poz. 23 · 1 / 1 · 1. raz 95% · 0% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | poz. 4 · 7 / 9 · 1. raz 0% · 85% | poz. 11 · 10 / 16 · 1. raz 0% · 72% | poz. 16 · 4 / 11 · 1. raz 8% · 48% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | poz. 4 · 7 / 10 · 1. raz 0% · 95% | poz. 11 · 6 / 14 · 1. raz 2% · 52% | poz. 16 · 6 / 10 · 1. raz 10% · 50% |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | poz. 4 · 8 / 11 · 1. raz 0% · 88% | poz. 11 · 9 / 14 · 1. raz 0% · 78% | poz. 16 · 4 / 10 · 1. raz 10% · 38% |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | poz. 9 · 3 / 5 · 1. raz 20% · 5% | poz. 15 · 4 / 9 · 1. raz 22% · 30% | poz. 22 · 2 / 7 · 1. raz 22% · 12% |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | poz. 9 · 3 / 5 · 1. raz 30% · 10% | poz. 15 · 3 / 6 · 1. raz 15% · 22% | poz. 22 · 4 / 8 · 1. raz 40% · 42% |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | poz. 9 · 3 / 6 · 1. raz 22% · 15% | poz. 15 · 4 / 9 · 1. raz 15% · 32% | poz. 22 · 2 / 7 · 1. raz 35% · 18% |

### Nuda i przestoje — świat „po zmianie D-107 (pliki gry)” (mediana)

| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego potwora | Czekanie (odradzanie + blokada) |
|---|---|---|---|---|---:|
| Tylko walki | Wojownik | 5,5 min (bagno/r1) | 10 min (bagno/k1) | 20 × Zwijogon | 0,0 min |
| Tylko walki | Zwiadowca | 5,4 min (dzungla/straznik) | 9,3 min (bagno/k1) | 18 × Zwijogon | 0,0 min |
| Tylko walki | Mag | 4,6 min (bagno/b1) | 8,4 min (bagno/b1) | 20 × Kłodokłap | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Wojownik | 10 min (bagno/k1) | 14 min (bagno/k1) | 20 × Zwijogon | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Zwiadowca | 9,8 min (bagno/k1) | 14 min (dzungla/o1) | 20 × Kokosowy Siłacz | 0,0 min |
| Walki + trening AFK (10 min na godzinę) | Mag | 9,3 min (bagno/k1) | 12 min (bagno/k1) | 20 × Zwijogon | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Wojownik | 10 min (bagno/b1) | 13 min (bagno/b1) | 19 × Kokosowy Siłacz | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Zwiadowca | 10,0 min (bagno/b1) | 13 min (bagno/b1) | 19 × Kokosowy Siłacz | 0,0 min |
| Walki + AFK + sklep trenera + pety + kowal | Mag | 9,8 min (bagno/b1) | 13 min (bagno/b1) | 18 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Wojownik | 11 min (bagno/b1) | 13 min (bagno/b1) | 18 × Kokosowy Siłacz | 0,0 min |
| Wszystko + sklep z przedmiotami | Zwiadowca | 10 min (bagno/b1) | 13 min (dzungla/g1) | 18 × Kłodokłap | 0,0 min |
| Wszystko + sklep z przedmiotami | Mag | 9,9 min (bagno/b1) | 13 min (bagno/b1) | 18 × Kokosowy Siłacz | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Wojownik | 15 min (bagno/r1) | 18 min (bagno/b1) | 18 × Gębokwiat | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Zwiadowca | 15 min (bagno/r1) | 18 min (dzungla/z1) | 18 × Kokosowy Siłacz | 0,0 min |
| Gracz AFK (20 min na godzinę, wszystko) | Mag | 15 min (bagno/b1) | 17 min (dzungla/z1) | 18 × Kokosowy Siłacz | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Wojownik | 14 min (dzungla/straznik) | 15 min (bagno/straznik) | 6 × Rechotek | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Zwiadowca | 13 min (dzungla/straznik) | 14 min (dzungla/straznik) | 4 × Zwijogon | 0,0 min |
| AFK 20 min/h i przeskakiwanie zagród (pytanie 117) | Mag | 13 min (dzungla/straznik) | 13 min (dzungla/straznik) | 5 × Rechotek | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Wojownik | 3,3 min (bagno/b1) | 6,3 min (bagno/k1) | 21 × Kokosowy Siłacz | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Zwiadowca | 3,3 min (dzungla/z1) | 6,3 min (dzungla/o1) | 21 × Gębokwiat | 0,0 min |
| Niecierpliwy (pomija walki, pcha do przodu) | Mag | 3,2 min (dzungla/z1) | 5,7 min (dzungla/g1) | 20 × Kokosowy Siłacz | 0,0 min |

### Gdzie schodzi czas — „Tylko walki”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 1,5 | 4 | 0,8 |
| las/m1 | Muchomornik (3–5) | 3 | 3,8 | 11 | 1,7 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 3,7 | 18 | 2,3 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,0 | 6 | 2,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 3,2 | 2 | 1,0 |
| bagno/r1 | Rechotek (10–12) | 11 | 1,2 | 12 | 2,0 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 7,2 | 17 | 4,7 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 8,3 | 17 | 4,0 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 0,9 | 3 | 1,3 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 3,8 | 2 | 1,3 |
| dzungla/z1 | Zwijogon (17–19) | 17 | 4,5 | 20 | 5,2 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 6,9 | 21 | 4,7 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 7,4 | 18 | 3,7 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,4 | 3 | 1,3 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 3,5 | 2 | 1,3 |

### Gdzie schodzi czas — „Walki + AFK + sklep trenera + pety + kowal”, świat „po zmianie D-107 (pliki gry)” (mediana, średnio z klas)

Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.

| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |
|---|---|---:|---:|---:|---:|
| las/s1 | Leśny Slime (1–3) | 1 | 7,1 | 3 | 0,3 |
| las/m1 | Muchomornik (3–5) | 3 | 4,2 | 10 | 1,0 |
| las/w1 | Cierniowy Wilk (6–8) | 6 | 5,3 | 14 | 1,3 |
| las/t1 | Leśny Troll (8–9) | 8 | 4,0 | 4 | 1,0 |
| las/straznik | Strażnik Gaju (10–10) | 10 | 1,8 | 1 | 0,2 |
| bagno/r1 | Rechotek (10–12) | 11 | 3,4 | 7 | 0,7 |
| bagno/b1 | Bulgotnik (12–14) | 12 | 14 | 16 | 1,8 |
| bagno/k1 | Kłodokłap (14–16) | 14 | 7,5 | 18 | 0,3 |
| bagno/t1 | Ropucha z Chatką (16–16) | 16 | 0,9 | 1 | 0,0 |
| bagno/straznik | Strażnik Topieli (16–16) | 16 | 1,4 | 1 | 0,0 |
| dzungla/z1 | Zwijogon (17–19) | 17 | 7,5 | 17 | 2,0 |
| dzungla/g1 | Gębokwiat (19–21) | 19 | 12 | 17 | 1,0 |
| dzungla/o1 | Kokosowy Siłacz (21–23) | 21 | 6,9 | 18 | 0,3 |
| dzungla/t1 | Pancernik Ruin (23–23) | 23 | 1,3 | 1 | 0,0 |
| dzungla/straznik | Wąż Stu Lian (23–23) | 23 | 0,9 | 1 | 0,0 |

### Szansa wygranej ze Strażnikiem (%) — pula statystyk „gra”, liczby z plików gry

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

### Szansa wygranej ze Strażnikiem (%) — dla porównania: „Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0)”

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

### Propozycje zmian liczb — „przed / po” (świat „po zmianie D-107 (pliki gry)”, mediana z trzech klas)

Liczone na kopii danych; pliki gry bez zmian. Kolumny: minuty do końca (razem z AFK) · w tym AFK · różnica między klasami (najwolniejsza − najszybsza) · przegranych · wygrana ze Strażnikiem za pierwszym razem i ilu graczy na nim utknęło (Las / Bagno / Dżungla) · najdłuższa seria jednego potwora · najdłużej bez awansu · punkty z treningu · Rybki stracone po przegranych · wydane u trenera.

**Tylko walki**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Wdrożone 27.11: A + B + doświadczenie Dżungli ×1,25 (pliki gry) | 63 | 0,0 | 7,9 | 42 | 33 / 25 / 29 | 2 / 9 / 8 | 20 | 5,2 | 0 | 6010 | 0 |
| Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0) | 130 | 0,0 | 28 | 163 | 3 / 2 / 2 | 79 / 88 / 88 | 20 | 10 | 0 | 17140 | 0 |
| Bez B (limitu treningu) | 63 | 0,0 | 7,9 | 42 | 33 / 25 / 29 | 2 / 9 / 8 | 20 | 5,2 | 0 | 6010 | 0 |
| Bez doświadczenia Dżungli ×1,25 | 68 | 0,0 | 7,9 | 46 | 33 / 25 / 35 | 2 / 9 / 15 | 24 | 5,6 | 0 | 6787 | 0 |
| Dla porównania: krzywa doświadczenia ×1,5 (dłuższa gra) | 92 | 0,0 | 7,0 | 64 | 31 / 24 / 31 | 2 / 15 / 13 | 30 | 7,1 | 0 | 9342 | 0 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 420 | 0,0 | 75 | 542 | 0 / 4 / 0 | 100 / 93 / 96 | 39 | 19 | 0 | 48760 | 0 |

**Walki + trening AFK (10 min na godzinę)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Wdrożone 27.11: A + B + doświadczenie Dżungli ×1,25 (pliki gry) | 73 | 17 | 5,4 | 24 | 47 / 50 / 68 | 1 / 2 / 1 | 20 | 9,7 | 85 | 3426 | 0 |
| Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0) | 85 | 17 | 11 | 29 | 22 / 30 / 48 | 7 / 7 / 0 | 24 | 10 | 186 | 4125 | 0 |
| Bez B (limitu treningu) | 65 | 14 | 10 | 8 | 75 / 78 / 83 | 0 / 0 / 0 | 19 | 9,4 | 145 | 1176 | 0 |
| Bez doświadczenia Dżungli ×1,25 | 78 | 17 | 5,8 | 27 | 47 / 50 / 59 | 1 / 2 / 1 | 24 | 10 | 84 | 3759 | 0 |
| Dla porównania: krzywa doświadczenia ×1,5 (dłuższa gra) | 100 | 21 | 13 | 32 | 43 / 48 / 71 | 1 / 0 / 0 | 30 | 11 | 97 | 4372 | 0 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 145 | 31 | 31 | 116 | 0 / 10 / 7 | 97 / 72 / 70 | 16 | 13 | 233 | 13106 | 0 |

**Walki + AFK + sklep trenera + pety + kowal**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Wdrożone 27.11: A + B + doświadczenie Dżungli ×1,25 (pliki gry) | 80 | 18 | 5,0 | 14 | 60 / 63 / 83 | 0 / 0 / 0 | 19 | 10 | 80 | 688 | 533 |
| Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0) | 89 | 18 | 9,6 | 15 | 38 / 59 / 73 | 1 / 0 / 0 | 23 | 11 | 194 | 801 | 400 |
| Bez B (limitu treningu) | 76 | 18 | 6,0 | 4 | 89 / 94 / 92 | 0 / 0 / 0 | 18 | 9,5 | 224 | 144 | 1067 |
| Bez doświadczenia Dżungli ×1,25 | 84 | 18 | 5,6 | 15 | 60 / 63 / 81 | 0 / 0 / 0 | 23 | 10 | 79 | 765 | 300 |
| Dla porównania: krzywa doświadczenia ×1,5 (dłuższa gra) | 108 | 24 | 6,4 | 15 | 72 / 74 / 78 | 0 / 0 / 0 | 28 | 11 | 116 | 894 | 3483 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 132 | 27 | 29 | 84 | 2 / 7 / 15 | 80 / 48 / 41 | 15 | 13 | 209 | 2433 | 300 |

**Gracz AFK (20 min na godzinę, wszystko)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Wdrożone 27.11: A + B + doświadczenie Dżungli ×1,25 (pliki gry) | 101 | 40 | 16 | 8 | 72 / 73 / 87 | 0 / 0 / 0 | 18 | 15 | 117 | 207 | 100 |
| Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0) | 109 | 43 | 5,8 | 4 | 80 / 96 / 100 | 0 / 0 / 0 | 22 | 16 | 516 | 50 | 533 |
| Bez B (limitu treningu) | 90 | 32 | 3,8 | 1 | 97 / 99 / 100 | 0 / 0 / 0 | 18 | 15 | 375 | 22 | 0 |
| Bez doświadczenia Dżungli ×1,25 | 109 | 43 | 4,7 | 9 | 72 / 73 / 90 | 0 / 0 / 0 | 23 | 16 | 131 | 235 | 300 |
| Dla porównania: krzywa doświadczenia ×1,5 (dłuższa gra) | 133 | 51 | 16 | 9 | 79 / 87 / 92 | 0 / 0 / 0 | 28 | 16 | 142 | 433 | 2467 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 147 | 54 | 17 | 56 | 8 / 22 / 32 | 51 / 27 / 8 | 18 | 17 | 228 | 1096 | 100 |

**AFK 20 min/h i przeskakiwanie zagród (pytanie 117)**

| Zmiana | Koniec (min) | W tym AFK | Różnica klas | Przegranych | Strażnik za 1. razem (%) | Utknęło (%) | Seria | Bez awansu (min) | Punkty AFK | Rybki stracone | U trenera |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| Wdrożone 27.11: A + B + doświadczenie Dżungli ×1,25 (pliki gry) | 47 | 22 | 2,1 | 44 | 0 / 1 / 9 | 89 / 68 / 45 | 5 | 13 | 65 | 2655 | 1000 |
| Przed 27.11 (5 + 5 punktów, bez limitu, Dżungla ×1,0) | 47 | 22 | 5,6 | 36 | 0 / 2 / 35 | 45 / 90 / 16 | 4 | 13 | 334 | 2176 | 883 |
| Bez B (limitu treningu) | 33 | 14 | 15 | 24 | 7 / 10 / 13 | 16 / 48 / 47 | 2 | 12 | 214 | 2111 | 333 |
| Bez doświadczenia Dżungli ×1,25 | 47 | 22 | 3,6 | 45 | 0 / 1 / 10 | 89 / 68 / 50 | 6 | 14 | 65 | 2749 | 1000 |
| Dla porównania: krzywa doświadczenia ×1,5 (dłuższa gra) | 54 | 22 | 6,1 | 62 | 0 / 8 / 2 | 98 / 73 / 66 | 8 | 14 | 58 | 3737 | 583 |
| Dla porównania: D-140 wdrożona (0 punktów za poziom) i limit 4 × poziom | 103 | 40 | 18 | 128 | 0 / 18 / 8 | 100 / 55 / 65 | 15 | 15 | 241 | 8043 | 2367 |

_Uruchomienie: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 40 --ziarno 1` · 40 przebiegów na komórkę · krzywa doświadczenia 11,71 × L^1,6 · pula statystyk „gra” · trening AFK: pasek 4 × 1,2 s, +1 za pasek (750 punktów na godzinę na stanowisku) · katalog sklepu: swiat/postacie/sklep_liczby.json · liczone 2026-11-27._

<!-- TABELE:KONIEC -->
