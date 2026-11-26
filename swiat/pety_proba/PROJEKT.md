---
status: propozycja
---
# Jajka i pety na próbę — pierwsze ujście Złota i pierwsza „zdobycz”

**Status: propozycja** (zlecenie Karola z 17.11.2026). Nic tu nie jest kanonem: liczby, nazwy, wygląd i kolejność
zakupów czekają na decyzje Karola i Pawła (lista „Przyjęte, do zmiany” niżej; to, co już zdecydowane — „Zdecydowane”).
Decyzje, których się trzymamy:
D-052 (jajka za Złoto w każdej strefie, karmienie), D-058 (jeden stały skill, poziom, ewolucja za shardy peta, Shard
Ewolucji i tokeny krainy), D-060 (inkubator w biomie, wyklucie od razu z animacją, bez jajek z potworów), D-076
(inkubator przy teleporcie biomu), D-085 (zagroda petów w miasteczku), D-086 (jajka tylko za Złoto, szanse jawne).

> **W skrócie.** Na Polanie Przybycia lasu-pasa, na kamiennym stanowisku jajka z mapy, stoi **wielkie leśne jajko**
> ze słupem światła, napisem i tablicą z **jawnymi szansami**. **E (przytrzymanie) → serwer pobiera Złoto** (przez
> właściciela stanu gracza) i losuje peta → jajko się trzęsie, pęka w kolorze rzadkości, pet wyskakuje, radość,
> napis „NOWY PET!” albo „KOPIA +1”. **Aktywny pet chodzi za graczem** (widzą go wszyscy), znika w walce, przelocie,
> chmurach i mini-grze. **W zagrodzie w bazarze** stoją posiadane pety, tablica „TWOJE PETY · PRÓBA” z liczbą kopii,
> a E opiekunki otwiera tymczasowe okno wyboru aktywnego peta. **Pet daje premię do Złota albo doświadczenia z walk**
> (liczy ją StanGracza, napis „+N Rybek od peta” przy łupie). Wskazówka celu: „Masz dość Rybek na jajko…”.
> Od 26.11.2026 waluta w napisach to **Rybki** (D-146; atrybut `Gold`, pola zapisu i nazwy w kodzie bez zmian): odmiana przy liczbie „1 Rybka / 2–4 Rybki / 5 Rybek”, w dopełniaczu „Brakuje ci 1 Rybki / 150 Rybek”. Helper `L.ileRybek(D, n, "m"|"b"|"d")` (lustro `ile_rybek`): „cena: 1 Rybka”, „Kup za 1 Rybkę”,
> „od 1 Rybki”; przychód zagrody „+3 Rybki/min”, „+2,4 Rybki/min”, „+12 Rybek/min”.
>
> **Od 17.11 (wieczór) drugie jajko — Jajko Bagna** (D-060: inkubator w każdym biomie): na tym samym stanowisku przy
> Pomoście Przybycia Bagna stoi **błotne gniazdo z trzcin na palach z latarenką-ognikiem** i tablicą szans; pięć petów
> Bagna, trochę lepszych od leśnych tej samej rzadkości. **Cena jajka jest stała** (decyzja Karola 17.11): jajko leśne
> 300 Złota, jajko Bagna 750 — rośnie tylko między biomami (pierwsze jajko po ok. 6 min gry w biomie). Jajko = wpis
> w `ustawienia.json` → `jajka` (trzeci biom = nowy wpis, bez kodu).
> Jajka (leśne też) są od teraz **gładkie — z elipsoid**, nie ze schodków klocków („ul”, para przed / po niżej).
>
> **Od 18.11 (noc) trzecie jajko — Jajko Dżungli** (propozycja, bez Studio): turkusowe jajko z hibiskusem na mchu
> stanowiska na Tarasie Przybycia Dżungli, obok **kamienny totem ruin** ze świecącym kwiatem i tablica szans; pięć
> petów Dżungli (sekcja niżej), cena **1350 Złota** z tej samej reguły co Bagno.

## Pięć petów leśnego jajka

Modele w `swiat/postacie/` (plansze i portrety w `swiat/postacie/wynik/<id>/`); od nocy 25/26.11 przebudowane według
arkuszy Pawła — obłe bryły z elipsoid i walców, okrągłe oczy z odblaskami, jasne łaty (porównanie arkusz / nowy / stary:
`podglad/noc2511_pet_<id>.jpg`, w grze: `klatki/noc2511_*.jpg`). Szanse:
`tools/walka/progresja.py` (`ZALOZENIA["szanse_jajka"]`). Rzadszy = efektowniejszy: pospolity, zwykły i rzadki bez
świecenia, epicki i legendarny świecą (Neon) i mają słup światła przy wykluciu.

| Pet | Rzadkość | Szansa | Skill (pasywny, z walk) | Wygląd |
|---|---|---:|---|---|
| Żołędziak | Pospolity | 50% | Zbieracz: +2% Złota z walk | obła kropla-żołądź na nóżkach-walcach, jasny dół brzuszka, czapka-kopułka w ciemne pasy z daszkiem z przodu, ogonek z listkiem, rączki-patyczki z trzema palcami |
| Mchowy Ślimak | Zwykły | 25% | Muszla: +3% Pancerza | duża zielona głowa-kostka z buzią, czułki z zielonymi kulkami, obła stopa z jaśniejszym spodem, muszla z kwadratową spiralą w mchu z czerwonym grzybkiem w białe kropki |
| Liściolis | Rzadki | 15% | Lisi Spryt: +15% Zręczności i Szczęścia | „chibi” lisek z wielką kanciastą głową i kremowym pyszczkiem, uszy z dużych liści, kołnierz z pięciu liści, mały tułów z kremową piersią, gruby zadarty ogon z liściem |
| Świetlikówka | Epicki | 8% | Blask Świetlików: Światło (szybsza mana), +20% Inteligencji, +5% doświadczenia | ciemnośliwkowa sówka z wielką głową-kostką, jasną maską i pomarańczowymi świecącymi oczami, wisząca świecąca latarenka, szerokie skrzydła, fioletowe nóżki; krążą wokół niej trzy świetliki |
| Jelonek Gaju | Legendarny | 2% | Kryształowe Poroże: Kryształ (ciosy mocniej trafiają), +20% Siły, +5% Złota i doświadczenia | jelonek z dużą okrągłą głową i kremową maską, wielkie uszy z różowym środkiem, świecące kryształowe poroże z kwiatkiem, wianek z liści ze świecącym klejnotem, białe cętki, złote dolne części nóg z kopytkami (45 części — limit) |

Klipy każdego peta: `spoczynek`, `chod`, `radosc`, `wyklucie`. Jajko: `spoczynek`, `trzesienie`, `pekniecie`.
Pies, Slime i Smok (pety z kanonu) zostają na inne jajka (np. miejskie).

## Pięć petów Jajka Bagna (obok leśnych tej samej rzadkości)

Własne projekty pod klimat Bagna (mokradła, mgła, ogniki, pomosty), sylwetki inne niż pety lasu i niż potwory Bagna
(ropuchy, błotniak, kłoda) — pety „do kochania”. Te same rzadkości i szanse. Skille od 18.11 według D-101 (sekcja
„Skille petów” niżej): różne premie i żywioły, zwykłe pety tylko mała pasywka.

| Rzadkość · szansa | Pet Bagna | Skill Bagna | Pet lasu | Skill lasu | Wygląd (Bagno) |
|---|---|---|---|---|---|
| Pospolity · 50% | Pałkuś | Pałka: +3% Siły | Żołędziak | +2% Złota z walk | brązowa kolba pałki wodnej z buzią na zielonej łodyżce, liście-rączki, puch na czubku |
| Zwykły · 25% | Nenufarek | Spokojna Toń: +3% Kondycji | Mchowy Ślimak | +3% Pancerza | miętowy żółwik z pancerzem z liścia grzybienia i różowym kwiatem nenufaru |
| Rzadki · 15% | Ważeczka | Jadowite Żądło: Jad (zatruwa wroga przy ciosie, 30%) | Liściolis | +15% Zręczności i Szczęścia | turkusowa ważka z oczami-kopułami, odwłokiem w paski i czterema błękitnymi skrzydłami (unosi się) |
| Epicki · 8% | Ognik | Błędny Ogień: Ogień (podpala wroga przy ciosie, 25%) | Świetlikówka | Światło, +20% Inteligencji, +5% doświadczenia | miętowy błędny ognik z buzią i świecącym, zawiniętym płomieniem, dwie krążące iskry (unosi się) |
| Legendarny · 2% | Perłowa Wydra | Perła Topieli: Woda (lepsza obrona), +15% Kondycji, +6% Złota i doświadczenia | Jelonek Gaju | Kryształ, +20% Siły, +5% Złota i doświadczenia | wydra na tylnych łapkach z otwartą muszlą i świecącą perłą, wianek z grzybienia, naszyjnik z pereł |

Podgląd zbiorczy: `podglad/pety_bagna.jpg` (ten sam układ co `podglad/pety_lesne.jpg`, pod skillem — pet lasu tej
rzadkości). Jajko Bagna: miętowe w ciemnozielone i turkusowe cętki, z liściem grzybienia i kwiatkiem na czubku.

## Pięć petów Jajka Dżungli (18.11 noc, propozycja)

Własne projekty pod klimat Dżungli (liście, liany, kwiaty, ruiny, turkusowa woda; paleta mapy 2FA34A / 6CCB4A, pnie
5C3A22, turkus 2EC4B6, kwiaty E5392B / F2B030, świecące FF5FA2 / FFD84A). Sylwetki inne niż pety lasu i Bagna i niż
potwory Dżungli (kameleon Zwijogon, kwiat Gębokwiat, małpa Kokosowy Siłacz, Pancernik Ruin, Wąż Stu Lian); nazwy nie
mylą się z nimi ani z petami lasu i Bagna. Szanse jak w innych jajkach (jawne na tablicy, legendarny 2%).

| Rzadkość · szansa | Pet Dżungli | Skill | Wygląd |
|---|---|---|---|
| Pospolity · 50% | Ananasik | Słodki Sok: +3% Zręczności | pękaty złocisty ananas w łuski-romby, z buzią, koroną z sześciu liści i listkami-rączkami |
| Zwykły · 25% | Leniwczyk | Senne Lekcje: +2% doświadczenia z walk | przygarbiony leniwiec z ciemnymi opaskami wokół oczu, długimi łapami z pazurkami, szalikiem z liany i kwiatem za uchem |
| Rzadki · 15% | Tukanik | Dziób Łowcy: +15% Siły, +5% Szczęścia | czarne pisklę tukana z kremowym śliniaczkiem, turkusową obwódką oczu i ogromnym zielono-pomarańczowo-czerwonym dziobem (skacze obunóż) |
| Epicki · 8% | Posążek | Kamień Ruin: Runy (częstsze umiejętności), +30% Kondycji | kanciasty kamienny bożek z ruin z wielką głową, świecącymi turkusowymi oczami i runami, w lianie, z pióropuszem z liści i świecącym kwiatem |
| Legendarny · 2% | Jaguarek | Zew Dżungli: Dzikość (mocniejsze ciosy), +20% Szczęścia, +5% Złota i doświadczenia | złociste kocię jaguara w czarne rozety ze świecącym turkusowym środkiem, z wiankiem z kwiatów i ogonem w lianie ze świecącym kwiatkiem |

Pospolite i zwykłe dają małą premię każdej klasie (zwykłe pety trzech biomów mają różne premie: Złoto, Pancerz, Siła,
Kondycja, Zręczność, doświadczenie). Dwa nowe żywioły z pasywek silnika, których nie miał jeszcze żaden pet:
**Dzikość** (pasywki, które zwolnił Ogień: zwykły cios +10,8 / 13,4 / 11,7% dla Wojownika / Zwiadowcy / Maga) i **Runy**
(pasywki broni: mana z ciosów +25%, zwykły cios −10% — umiejętności dużo częściej). Podgląd zbiorczy:
`podglad/pety_dzungli.jpg`; modele `swiat/postacie/ananasik.py`, `leniwczyk.py`, `tukanik.py`, `posazek.py`,
`jaguarek.py`, `jajko_dzungli.py` (plansze w `swiat/postacie/wynik/<id>/`).

**Jajko i inkubator Dżungli** (`jajko_dzungli.py`): stanowisko z mapy jak w lesie (płyta, korzenie, gniazdo z mchem —
jajko ×1,8 leży na mchu), więc gra stawia tylko dwie stałe bryły: **totem ruin** (kolumna z runami, w lianie, ze
świecącym różowym kwiatem; z prawej strony gniazda, przed wiaderkami mapy) i **tablicę szans** z liśćmi na daszku
(z przodu po lewej, przed świecącym kwiatem mapy — kwiat zostaje za tablicą, nauczka z tablicy Bagna). Słup światła
różowy (FF6FB0). Punkt E i miejsce z `swiat/dzungla_pas/krotki/znaczniki.json` (mapy nie zmieniam).

**Cena 1350 Złota — ta sama reguła co Bagno** (`ekonomia_jajek.py`, `MINUT_CENY` = 6): cena = Złoto z pierwszych 6 min
walk w biomie (mediana graczy, którzy przeszli poprzednie biomy jak w symulacji lasu), zaokrąglone do 50. Sprawdzenie
reguły: Bagno 752 → 750 (to cena z D-105), las 271 → 250 (D-105 ma 300 — cena lasu była wcześniej, pierwsze jajko
po 6,4 min), Dżungla 1362 → **1350** (gracz wchodzi na 18. poziomie, 10–90%: 17–20; walka daje ok. 160–230 Złota).
Przy 1350: pierwsze jajko Dżungli po 6,0 min (10–90%: 4,5–8,2), kolejne co ok. 5 min; do wygranej z Wężem Stu Lian
(mediana 48 min) gracz kupi ok. 9 jajek (las 10,5, Bagno 10). Jajka tylko za Złoto z gry (D-086).

## Skille petów (D-101): różne premie i żywioły (18.11, liczby — propozycja)

**D-101** (zatwierdzona w rejestrze: Karol, potwierdził Paweł, 17.11): pety dają różne premie — doświadczenie, Złoto,
Siłę, Zręczność…; mają żywioły; zwykłe pety tylko małą pasywkę, mocniejsze dodatki lepsze pety; projekt i liczby robi
agent („wolna ręka, zrób coś ciekawego”). Pet nie walczy obok gracza (D-059) — żywioł to pasywka w ciosach gracza.
Jeden stały skill na typ peta (D-058). **Liczby poniżej są propozycją** (do zatwierdzenia).

Skill = jedno krótkie zdanie (tablica szans, okno zagrody, napis po wykluciu; na tablicy zagrody — sam żywioł albo
pierwsza premia). W grze idzie przez **`StanGracza/Sygnaly/Modyfikatory`** (źródło `"pety"`, bez zmian w silniku
i w stanie gracza): `procent` → mnożnik statystyk (pole silnika `pet`, D-059), `lup` → premia do łupu, `pasywki` →
pasywki silnika żywiołu (stan gracza liczy tylko te klasy gracza, dlatego Światło, Kryształ i Woda mają pasywkę dla
każdej klasy), `zaklecie` → zaklęcie broni bohatera (podpalenie albo trucizna przy niezablokowanym ciosie, każda klasa).
Serwer petów ustawia modyfikator przy wejściu gracza, po zakupie i wyborze, a zdejmuje przy odstawieniu; pierwsze
wywołanie przejmuje źródło — dawna premia z `Pety("kup")` już się nie liczy (bez podwójnej premii, test `5i`).

| Żywioł | Gracz widzi | Pasywki silnika (klasa) |
|---|---|---|
| Ogień | „podpala wroga przy ciosie (25%)” | zaklęcie `podpalenie` (25% na niezablokowany cios, każda klasa; w walce napis „PODPALENIE!”), Mag dodatkowo `ognista_rozdzka` (podpalenie trwa o 2 tury dłużej) |
| Jad | „zatruwa wroga przy ciosie (30%)” | zaklęcie `trucizna` (30% na niezablokowany cios, każda klasa), Mag dodatkowo `kumulowanie_trucizny` (więcej stosów, mocniejsza trucizna) |
| Dzikość (Dżungla) | „mocniejsze ciosy” | Wojownik `furia` (+10,8%), Zwiadowca `seria` (+13,4%), Mag `magiczny_pocisk` (+11,7%) — zwykły cios |
| Runy (Dżungla) | „częstsze umiejętności” | pasywki broni: Wojownik `miecz_runiczny`, Zwiadowca `luk_runiczny`, Mag `kostur_many` — mana z ciosów +25%, zwykły cios −10% |
| Światło | „szybsza mana” | `bitewny_rytm` / `przyplyw_adrenaliny` / `przeplyw_many` — mana z ciosów +10%, +15 many na start walki |
| Kryształ | „ciosy mocniej trafiają” | Wojownik `rozdzieracz` (Pancerz wroga −12%), Zwiadowca `oko_lowcy` (krytyk), Mag `skupiona_magia` (moc +2,5%) |
| Woda | „lepsza obrona” | Wojownik `mur_tarczy` (blok +4,2%, Pancerz +15,7%), Zwiadowca `zwinnosc` (unik +7,1%), Mag `przeplyw_many` (szybsza bariera) |

**Wpływ na walki** (`skille_petow.py`, silnik walki, bohater jak w grze — rozkład klasy z danych gracza, bez treningu;
600 ziaren; pp = punkty procentowe szansy wygranej przy graczu na poziomie strażnika; W / Z / M = Wojownik /
Zwiadowca / Mag; czas i Złoto na minutę — przejście gracz po graczu, 15 na klasę, pet od początku — górna granica):

| Pet | Strażnik Gaju (bez peta 36 / 37 / 33%) | Strażnik Topieli (bez peta 11 / 23 / 11%) | Las do Strażnika (28,2 min) | Bagno do Strażnika (49,1 min) | Złoto/min las / Bagno (120 / 166) |
|---|---|---|---|---|---|
| Żołędziak (+2% Złota) | +0 / +0 / +0 | +0 / +0 / +0 | +0,0 | +0,0 | +2 / +3 |
| Mchowy Ślimak (+3% Pancerza) | +0 / +0 / +0 | +1 / +0 / +0 | +0,0 | −0,2 | −1 / +0 |
| Pałkuś (+3% Siły) | +2 / +1 / +0 | +1 / +1 / +0 | −0,7 | −3,1 | +0 / +1 |
| Nenufarek (+3% Kondycji) | +0 / +0 / +2 | +2 / +0 / +0 | −1,2 | −3,8 | −0 / −2 |
| Liściolis (+15% Zręczności i Szczęścia) | +8 / +3 / +4 | +5 / +4 / +3 | −2,4 | −5,4 | +5 / +7 |
| Ważeczka (Jad: trucizna 30% przy ciosie) | +7 / +5 / +6 | +6 / +6 / +4 | −0,7 | −6,9 | +3 / −2 |
| Świetlikówka (Światło, +20% Int., +5% dośw.) | +8 / +4 / +5 | +5 / +4 / +3 | −3,7 | −8,3 | +10 / +10 |
| Ognik (Ogień: podpalenie 25% przy ciosie) | +12 / +7 / +12 | +9 / +6 / +7 | −2,8 | −9,0 | +6 / +14 |
| Jelonek Gaju (Kryształ, +20% Siły, +5% / +5%) | +13 / +8 / +6 | +9 / +7 / +5 | −5,1 | −9,7 | +19 / +27 |
| Perłowa Wydra (Woda, +15% Kondycji, +6% / +6%) | +12 / +16 / +6 | +10 / +12 / +4 | −4,7 | −9,5 | +19 / +24 |

Wnioski: pospolite i zwykłe to tylko ozdoba (±2 pp, w granicach szumu); rzadkie i epickie wyraźnie pomagają; legendarne
są pożądane (−17% czasu lasu, −19% Bagna), ale nie obowiązkowe — bez peta strażnik lasu na swoim poziomie to ok. 35%
wygranych, a gracz i tak zdobywa poziom wyżej. Klasa ma znaczenie: Wojownikowi najbardziej Jelonek (Siła) i Wydra,
Zwiadowcy Wydra (unik), Magowi Ognik (Ogień); Zręczność i Inteligencja w silniku działają słabiej niż Siła i Kondycja.
Po zmianie na prawdziwe zaklęcie (18.11 noc) Ognik jest najmocniejszym epickim (+12 pp Wojownikowi i Magowi — blisko
legendarnych w walce, ale bez premii do Złota), a Ważeczka pomaga każdej klasie po równo (+5–7 pp, trucizna działa
z każdą bronią). Czas Bagna przy małych petach (±3 min) i czas lasu Ważeczki to szum 45 graczy na wariant.

**Dżungla (18.11 noc): Wąż Stu Lian (poziom 23) i przejście Dżungli** — ta sama symulacja (`skille_petow.py` liczy teraz
trzech strażników i trzy biomy; gracz wchodzi do Dżungli po Strażniku Topieli). Bez peta: Wąż 18 / 25 / 21%, Dżungla do
Węża 53,5 min, 265 Złota/min. Czas biomu przy małych petach (±5 min) to szum 45 graczy na wariant (pp ze strażnikami — 600
ziaren — są pewniejsze).

| Pet | Strażnik Gaju (pp) | Wąż Stu Lian (pp) | Dżungla do Węża (53,5 min) | Złoto/min Dżungla (265) |
|---|---|---|---|---|
| Ananasik (+3% Zręczności) | +0 / +0 / +0 | +0 / +0 / +1 | −5,4 (szum) | +0 |
| Leniwczyk (+2% doświadczenia) | +0 / +0 / +0 | +0 / +0 / +0 | −4,3 (szum) | −8 (szum) |
| Tukanik (+15% Siły, +5% Szczęścia) | +8 / +6 / +5 | +5 / +2 / +1 | −6,1 | +27 |
| Posążek (Runy, +30% Kondycji) | +10 / +8 / +10 | +5 / +7 / +6 | −9,9 | +17 |
| Jaguarek (Dzikość, +20% Szczęścia, +5% / +5%) | +10 / +9 / +5 | +8 / +3 / +3 | −12,1 | +58 |
| dla porównania: Ważeczka / Ognik | +7 / +5 / +6 · +12 / +7 / +12 | +3 / +2 / +2 · +6 / +4 / +6 | −5,1 · −8,2 | +8 · +29 |
| dla porównania: Jelonek / Wydra | +13 / +8 / +6 · +12 / +16 / +6 | +9 / +4 / +3 · +13 / +12 / +4 | −9,5 · −8,7 | +43 · +43 |

**Reguła wyważenia (pety późniejszych biomów nie są mocniejsze tylko dlatego, że biom jest późniejszy):** każda
rzadkość ma ten sam „budżet” we wszystkich biomach, mierzony w punktach procentowych szansy wygranej ze strażnikiem
na jego poziomie i w minutach biomu — pospolite i zwykłe ok. 0 (najwyżej 3%, bez żywiołu), rzadkie ok. +5–8 pp
(Strażnik Gaju), epickie ok. +8–12 pp, legendarne ok. +10–16 pp i do 6% łupu. Procenty premii są w każdym biomie te same
(15–30% statystyk) — procent mnoży statystyki gracza, więc sam rośnie z jego poziomem; nie podnoszę ich za biom.
W pierwszej wersji Posążek (Runy, +20% Pancerza) dawał tylko +0–2 pp, a Tukanik (+20% Szczęścia) +2–4 pp — za mało
na swoją rzadkość, więc dostali Kondycję i Siłę (Szczęście i Zręczność działają w silniku słabiej). Jaguarek najlepiej
przechodzi samą Dżunglę (−12 min, krytyki na zwinnych przeciwnikach Dżungli), ale ze strażnikami jest jak Jelonek.

**Zaklęcie przy ciosie (18.11 noc):** stan gracza ma już pole `zaklecie` w `Modyfikatorach` (ustawia zaklęcie broni
bohatera, `bron.zaklecie`; przy kilku źródłach wygrywa pierwsze alfabetycznie). Ognik daje więc prawdziwe podpalenie
(25% na niezablokowany cios, każda klasa, w walce napis „PODPALENIE!”) zamiast `furii` / `serii` i bez premii do Złota,
a Ważeczka — trucizna (30%) zamiast +20% Inteligencji (pasuje do wyglądu: ważka z odwłokiem w paski i różowym końcem ogonka jak żądło; model bez zmian).
Liczby w tabeli wyżej są już po tej zmianie.

## Gładkie jajka (17.11 wieczór)

Jajko to trzy elipsoidy (`swiat/postacie/pety_lesne.py` → `jajko_gladkie`): dół, „bark” i kopułka czubka (odskakuje
przy pęknięciu), pod nią świecące „Wnetrze” w kolorze rzadkości; cętki to wtopione kulki. W Robloksie elipsoida to
Part ze SpecialMesh „Sphere” (prawie okrągła — Ball), więc sylwetka jest naprawdę gładka (w Blenderze widać jeszcze
paski siatki) i brył jest mniej: jajko leśne 16 zamiast 22, Bagna 21. Para „przed / po”:
`podglad/jajko_lesne_przed_po.jpg`.

## Cena jajka: stała, rośnie tylko między biomami (zdecydowane 17.11)

**Decyzja Karola (17.11.2026, czat):** cena jajka jest **stała** — „bo opener jajka jest per biom, więc tak czy siak
źródło dropienia jajek się zmienia, gdy gracz zmieni biom”. Jajko leśne **300 Złota**, jajko Bagna **750 Złota**
(dotychczasowe ceny startowe; liczby zostawione do doboru — trzymają pierwsze jajko w 5–10 minutach gry w biomie).
Cena nie rośnie z zakupami; rośnie tylko między biomami. W `ustawienia.json` → `jajka[].cena`: `tryb` = `"stala"`
(domyślny, pole `stala`); `"rosnaca"` (`start`, `krok`, `maks`) i `"kalkulator"` (stała z `tools/walka/progresja.py`)
zostają jako przełącznik. Gracz widzi cenę przy E („Kup za 300 Rybek”), nad jajkiem („Cena: 300 Rybek”, bez
„następne…”) i na tablicy („cena: 300 Rybek”; do 26.11.2026 „Złota”). Premii petów (+% Rybek) symulacja nie liczy — to
dolna granica tempa.

**Las** (`ekonomia_jajek.py`, 100 graczy na klasę, gracz jak w `swiat/stan_gracza/symulacja_lasu.py`, las-pas po
skróceniu; minuty od wejścia do lasu, mediana i 10–90% graczy):

| Cena | 1. jajko | 2. | 3. | 4. | 5. | odstępy (mediany) | jajek do Strażnika Gaju |
|---|---|---|---|---|---|---|---|
| **stała 300 (decyzja)** | **6,4 (5,1–8,3)** | 9,8 | 12,7 | 15,3 | 17,6 | 6,4 → 3,4 → 2,9 → 2,5 → 2,4 | **10–11 (9–13)** |
| rosnąca 300 +400 do 2000 (przełącznik) | 6,4 (5,1–8,3) | 13,5 | 21,6 | 29,1 | 38,4 | 6,4 → 7,1 → 8,1 → 7,5 → 9,3 | 3 (3–4) |
| kalkulator: stała 1000 | 13,5 (11,7–15,9) | 21,1 | 26,6 | 31,0 | 36,1 | 13,5 → 7,6 → 5,5 → 4,4 → 5,1 | 3 (2–4) |

Strażnik Gaju pada po ok. 26,7 min lasu (22,0–33,4). Przy stałej cenie kolejne jajka przychodzą coraz częściej
(dochód rośnie z poziomem) — to skutek decyzji, nie błąd; jajka liczy się do tempa przejścia, nie do sklepu.

**Bagno** (`ekonomia_jajek.py --biom bagno`, 100 graczy na klasę): gracz przechodzi las do wygranej ze Strażnikiem
Gaju (wchodzi do Bagna na ok. 11. poziomie, 10–90%: 11–12), potem walczy w przegrodach Bagna (`swiat/bagno_pas_gra`,
przeciwnicy z `przeciwnicy.py` dopisani do silnika w pamięci, Ropucha z Chatką jak Leśny Troll; limit 120 min).
Liczy się **tylko Złoto z Bagna** (dolna granica — zwykle gracz przynosi resztkę z lasu). Minuty od wejścia do Bagna:

| Cena | 1. jajko | 2. | 3. | 4. | 5. | odstępy (mediany) | jajek do Strażnika Topieli |
|---|---|---|---|---|---|---|---|
| **stała 750 (decyzja)** | **6,1 (4,5–8,3)** | 11,9 | 17,6 | 23,1 | 28,3 | 6,1 → 5,8 → 5,8 → 5,4 → 5,2 | **10 (7–12)** |
| rosnąca 750 +300 do 2500 (przełącznik) | 6,1 (4,5–8,3) | 14,1 | 24,3 | 34,7 | 44,1 | 6,1 → 8,0 → 10,2 → 10,4 → 9,4 | 5 (4–6) |
| rosnąca 750 +1000 do 5000 | 6,1 (4,5–8,3) | 19,7 | 37,3 | 53,0 | 71,4 | 6,1 → 13,5 → 17,6 → 15,7 → 18,4 | 3 (3–4) |

Strażnik Topieli pada po ok. 46 min Bagna (33,7–59,3; wszyscy 300 graczy w limicie). Złoto z Bagna to ok. 120 na
minutę — 2,5 raza więcej niż na początku lasu, stąd 750 = 2,5 × 300.

### Licznik ceny (osobny / wspólny) — przy cenie stałej nieużywany

Licznik kupionych jajek (wydatki na cel = id jajka w profilu StanGracza) wpływa na cenę **tylko w trybie
`"rosnaca"`**. Przy cenie stałej (domyślnej od 17.11) jest nieużywany do ceny; mechanizm zostaje (przełącznik
`licznik_ceny.tryb`: **osobny** — cena rośnie od zakupów tego jajka, **wspólny** — od sumy kupionych jajek wszystkich
biomów; testy `5e2b` i `5e3` na prawdziwym serwerze), a liczba kupionych jajek biomu i tak trafia do atrybutu gracza
`PetyKupioneJajka*` (wskazówka celu „pierwsze jajko biomu”).

## Zagroda daje Rybki (25.11.2026 noc, część A bez Studio — propozycja D-153, LICZBY ROBOCZE)

Ustalenia z sesji głównej 25.11 (Karol i Paweł na głos, w sejfie jako propozycja D-153): **pety stojące w zagrodzie
dają Rybki na sekundę** (Rybki = atrybut `Gold`, D-146), **pet założony** (idący za graczem) daje swój skill i **nie stoi
w zagrodzie**, pety na wyprawie też nie (wypraw nie ma — haczyk `naWyprawie` w `SerwerPetow`), **miejsc 2 → 4 → 6 → 8**
u opiekunki Jagody za Rybki, zagroda fizycznie nie rośnie, bez animacji budowy.

- **Kto stoi:** posiadane pety (jeden na gatunek — kopie to shardy), bez aktywnego i bez petów na wyprawie; wybór
  gracza („Do zagrody” / „Z zagrody” w oknie) albo domyślnie **najrzadsze** (przy tej samej rzadkości wyższa stawka,
  czyli dalszy biom); najwyżej tyle, ile miejsc ma poziom. Pety ponad limit zostają w posiadaniu i nic nie dają.
  „Najrzadsze” wraca do wyboru domyślnego. Przy wyborze ręcznym zmiana peta za graczem to zamiana miejscami
  (nowy wychodzi z zagrody, stary wchodzi na jego miejsce), a „Odstaw peta” odstawia go do zagrody, gdy jest miejsce.
- **Naliczanie:** serwer petów co `tik_s` = 5 s liczy Rybki/s petów w zagrodzie × czas od poprzedniego razu (najwyżej
  `tik_maks_s` = 15 s — przerwa serwera nie daje zaległości), całe Rybki dopisuje **StanGracza** (`Sygnaly/Pety
  ("przychod")`, źródło z listy `PAKIETY_PRZYCHODOW` w `swiat/stan_gracza/dane.py`), ułamek czeka na następny raz.
  Tylko gracz w grze z wczytanym profilem — **bez przychodu offline** (przyjęte). Klient tylko pokazuje: napis
  „+N Rybek” nad zagrodą (gdy gracz jest blisko) i wiersz zagrody w tymczasowym oknie („ZAGRODA: 3/4 miejsc · +2,4
  Rybek/min”, „Więcej miejsc: 6 za 3000 Rybek”, „Najrzadsze”), przy pecie w zagrodzie „· w zagrodzie: +N Rybek/min”.
- **Miejsca:** poziom = 1 + licznik wydatków na cel `zagroda_miejsca` w profilu StanGracza — zakup (`WydajZloto`) i poziom
  zapisują się jednym wywołaniem. Za mało Rybek = „Brakuje ci N Rybek (masz M, ulepszenie kosztuje C)”, nic nie zmienione.
  Wybór petów żyje w profilu przez `Sygnaly/DanePakietu` (pakiet `PetyProba`, pole `zagroda`).
- **Mapa:** klient stawia modele na tylu miejscach, ile znaczników `zagroda_miejsce_N` ma mapa bazaru (dane z
  `swiat/miasteczko_bazar/znaczniki.json` przy `dane_petow.py`; było 6, przebudowa miasta 25.11 daje 8); gdy petów
  w zagrodzie jest więcej niż znaczników, nadmiar daje Rybki bez modelu.

**Liczby robocze** (`ustawienia.json` → `zagroda`; rachunek `ekonomia_zagrody.py`, 30 graczy na klasę, symulacja walk jak
`ekonomia_jajek.py`): stawka peta = stawka rzadkości × mnożnik jajka biomu (las ×1, Bagno ×2,5, Dżungla ×4,5 — jak ceny
jajek 300 / 750 / 1350).

| Rzadkość | Las | Bagno | Dżungla |
|---|---:|---:|---:|
| Pospolity | 0,015/s (54/h) | 0,0375/s (135/h) | 0,0675/s (243/h) |
| Zwykły | 0,025/s (90/h) | 0,0625/s (225/h) | 0,1125/s (405/h) |
| Rzadki | 0,04/s (144/h) | 0,1/s (360/h) | 0,18/s (648/h) |
| Epicki | 0,065/s (234/h) | 0,1625/s (585/h) | 0,2925/s (1053/h) |
| Legendarny | 0,1/s (360/h) | 0,25/s (900/h) | 0,45/s (1620/h) |

Ceny miejsc: 2 → 4 za **1000**, 4 → 6 za **3000**, 6 → 8 za **7500** Rybek. Rybki z walk (mediana, od wejścia do
wygranej ze strażnikiem): las ok. 7900/h (28 min), Bagno ok. 10 100/h (44 min), Dżungla ok. 16 300/h (48 min).
Zagroda pełna, „typowa” (jajka kupione za całe Rybki z biomów, najrzadszy za graczem) · „najwięcej” (najlepsze pety):

| Etap | 2 miejsca | 4 | 6 | 8 |
|---|---|---|---|---|
| koniec lasu | 234/h (3%) · 378 (5%) | 288 (4%) · 522 (7%) | jak 4 (las ma 5 petów) | jak 4 |
| koniec Bagna | 504 (5%) · 945 (9%) | 819 (8%) · 1539 (15%) | 1008 (10%) · 1908 (19%) | 1008 (10%) · 2133 (21%) |
| koniec Dżungli | 882 (5%) · 1260 (8%) | 1557 (10%) · 2898 (18%) | 2016 (12%) · 3780 (23%) | 2349 (14%) · 4284 (26%) |

Zagroda to dodatek (typowo 3–14% Rybek z walk, najwyżej ok. 26%), pętla „Rybki → miejsca → Rybki” jest ograniczona
(8 miejsc, jeden pet na gatunek, ulepszenie 2 → 4 zwraca się w lesie po ok. 18 h gry, w Dżungli po 1,5 h).
Uwaga: zagroda nalicza także stojącemu bez ruchu graczowi (AFK) — do decyzji razem z D-050.

## Pety chodzą luzem po zagrodzie (26.11.2026, propozycja)

Paweł w opinii do raportu z nocy (26.11, przekazał Karol): „z petami nawet okej, ale fajnie by było, jakby chodziły luzem
po tej zagrodzie, a nie były przyklejone do stanowisk”. Karol: „Wykonaj te zadania”.

- **Co widzi gracz:** pety stojące w zagrodzie spacerują po wybiegu, przystają na 2–6 s, omijają się, a co piąty raz
  odpoczywają dłużej tam, gdzie stoją (5–9 s). Latające (Świetlikówka) unoszą się jak przy graczu. Imię idzie z petem.
- **Tylko obraz u gracza** (`KlientPetow.client.luau`, tabela `Wybieg`): o tym, kto stoi w zagrodzie i ile daje Rybek,
  dalej decyduje serwer. Serwer, zapis i liczby D-153 bez zmian. Każdy gracz widzi w zagrodzie swoje pety, jak dotąd.
- **Wybieg** to prostokąt policzony z miejsc petów na mapie (znaczniki) i marginesów (`dane_petow.py` → `D.polozenia.wybieg`): 20 × 11,8
  studa; margines 2 do bocznych płotów, 0,4 do koryta, 1 do misek przy bramce. Mapy nie trzeba było zmieniać.
- **Ustawienia:** `ustawienia.json` → `zagroda.wybieg` (prędkość 1,8–3 st/s, tempo klipu chodu 0,6, postoje, odstęp nowego
  celu 3,4 st, mijanie 2,6 st). `wlaczony: false` przywraca stanie na miejscach z mapy.
- **Legowiska znikają** (Paweł na Telegramie 26.11, 15:42, po obejrzeniu spaceru: „legowiska znikają, tempo okej”):
  z mapy zniknęło osiem kolorowych poduch (16 części), znaczniki miejsc zostały jako niewidoczne dane — liczba miejsc
  i punkty, w których pety pojawiają się w zagrodzie. Pet nie wraca już na „swoje” miejsce, tylko co piąty raz
  odpoczywa dłużej tam, gdzie stoi. Ile miejsc ma zagroda (2 → 4 → 6 → 8), widać w oknie zagrody u Jagody (wiersz
  zagrody i przycisk ulepszenia) — na samym wybiegu nic już tego nie pokazuje.

**Sprawdzone w Play 26.11** (`testy/proba_play.py --zagroda`, cztery przebiegi, 14 punktów OK, 0 niezaliczeń):
- Z10 — dwa pety przez 14 s: oba w wybiegu, model dokładnie tam, gdzie liczy go spacer, najdłuższa droga 8,5–11 st.
- Z11 — pełna zagroda, osiem petów przez 36 s: ruszyło 8 z 8, poza wybiegiem 0 próbek, środki nie bliżej niż 2,6 st,
  naraz idzie średnio 2–3 pety (najwyżej 6). Zrzuty `klatki/z11_pelna_zagroda_1…3.jpg`.

**Czego nie sprawdzono:** czas klatki na telefonie, dwóch graczy naraz (każdy widzi w zagrodzie tylko swoje pety — tak
było i przed zmianą), ocena człowieka, czy ruch jest ładny.

**Znane słabości:** pet idzie po prostej i zatrzymuje się przed innym petem (nie obchodzi go łukiem); po odświeżeniu listy
(np. po zmianie wyboru) pet zostaje na miejscu, ale zaczyna od postoju; okno PETS po dokupieniu petów haczykiem próby
pokazywało trzy pety zamiast dziesięciu (okno Pawła — do sprawdzenia przy okazji).

## Jak działa zakup i gdzie żyje stan

1. Gracz przytrzymuje E przy jajku (`ProximityPrompt` na niewidzialnej części w punkcie E mapy, 0,5 s; jeden punkt E
   na jajko: „E inkubator” w lesie, „E inkubator Bagna” w Bagnie). Jajko wynika z podpowiedzi, którą odpalono, a serwer
   sam sprawdza, że gracz stoi przy inkubatorze TEGO jajka (promień E 10 + zapas 4 studa w poziomie; inaczej
   „Podejdź bliżej inkubatora”, test `5c1`). Przy pierwszym wejściu do Bagna trwa przelot kamery — w tym czasie
   podpowiedzi E nie działają (jak w lesie).
2. **Serwer** (`SerwerPetow`): blokada na czas wyklucia (4,6 s, ustawiona *przed* jakimkolwiek wywołaniem — drugi E
   dostaje „Jajko jeszcze się wykluwa…”), cena jajka (stała; przy przełączniku „rosnaca” — z licznika kupionych jajek
   w profilu), los `Random:NextNumber()` →
   pet z jawnych szans, potem **jedno** wywołanie `Workspace/StanGracza/Sygnaly/Pety("kup")`.
3. **StanGracza** w jednym wywołaniu, bez przerwy: sprawdza kwotę i źródło, oddaje do atrybutów łup czekający na
   pokazanie, odejmuje Złoto (nigdy poniżej zera — za mało = odmowa z brakującą kwotą), liczy wydatek na cel, dodaje
   kopię peta; pierwszy pet od razu idzie za graczem. Atrybuty gracza `PetAktywny` i `PetyLiczba` widzą klienci.
4. Serwer petów wysyła klientowi „wyklucie”; animację gra **klient** (nic w niej nie decyduje). Reset postaci w trakcie
   niczego nie zabiera — pet jest już w profilu.
5. **Zakup „bez pokazu” (26.11.2026, jajka w świecie ze scenką Pawła — `src/server/JajkoKorowe.server.luau`):**
   haczyk `SterowanieSerwera("kup", gracz, jajko, { bezPokazu = true })` (trzeci argument: liczba r jak dotąd albo
   tabela `{ r?, bezPokazu? }`). Zakup, cena, zapis peta, PetAktywny, liczniki i ceny — bez zmian; „wyklucie” do
   klienta ma pole `bezPokazu`. Klient wtedy nie gra animacji inkubatora, chowa swojego peta przy graczu (jak w czasie
   animacji) i trzyma napis „Wykluł się: … — premia” do lokalnego sygnału `Sygnaly/PokazWyklucia` (BindableEvent,
   tworzy go klient): „odsloniety” → napis (scenka woła go razem z „NEW PET!”), „koniec”, Vector3 jaja → pet rusza za
   graczem od jaja. Bez sygnału po 45 s napis i pet same. Zakup z inkubatora prawdziwym E — jak dotąd (animacja
   i napis). Próba: `swiat/jajka_biomow/testy/proba_play.py` (punkty xA, xB).

**Stan petów żyje w profilu StanGracza** (`pety = { kopie, aktywny, premia }`, `wydatki`, wersja profilu 2), nie
w serwerze petów. Uzasadnienie: StanGracza jest jedynym właścicielem stanu gracza; Złoto i pety muszą się zapisać
razem (jeden klucz, jedna blokada sesji przy przyszłym zapisie), inaczej awaria między zapisami da „Złoto zabrane,
peta brak” albo odwrotnie. Zakup to jedno wywołanie u właściciela, więc dziś i po dodaniu zapisu jest
niepodzielny. Bez `StanGracza` inkubator odmawia napisem „Inkubator nieczynny — brak stanu gracza (próba)”,
a zagroda pokazuje ten sam napis — bez błędów.

## Pet przy graczu, zagroda, premia, wskazówka

- **Pet przy graczu:** każdy klient buduje lokalnie model aktywnego peta *każdego* gracza (atrybut `PetAktywny`) —
  płynnie (wygładzanie, grunt z promienia w dół), bez kolizji (części bez `CanCollide`/`CanQuery`), 2,6 studa w bok
  i 3,2 w tył, chód / spoczynek / radość przy skoku; 21–45 części na peta. Znika u siebie od razu, gdy HUD jest
  schowany, kamera nie jest zwykła, trwa mini-gra (`TreningGra`), przelot (`BlokadaWalki`), chmury (`Trwa`), wybór
  klasy — wtedy chowa też cudze pety (nie wchodzą w kadr walki), a innym graczom zgłasza „czekaj” (atrybut `PetCzeka`).
- **Zagroda (bazar):** od 25.11 stoją w niej pety, które dają Rybki (rozdział „Zagroda daje Rybki” wyżej — wybór gracza
  albo najrzadsze, tyle, ile miejsc ma poziom; dawniej: do 6 posiadanych petów bez aktywnego) i stoją na miejscach
  z mapy `zagroda_miejsce_1…6` z napisem „Nazwa ×N” (kopie = shardy peta, D-058); tablica przy bramie zagrody w dwóch
  kolumnach — jajko po jajku („► ” przy aktywnym, „jeszcze żadnego” w pustej); **E opiekunki** (pakiet bazaru, zdarzenie
  `ReplicatedStorage.OknoMiejsca`, id `zagroda_petow`) otwiera tymczasowe okno „TWOJE PETY · PRÓBA”: **przewijane**,
  podzielone na jajka (nagłówek jajka w jego kolorze), wiersz na peta (kolor rzadkości, ×kopie, rzadkość, skill),
  przycisk „Wybierz” i „Odstaw peta”. Wybór sprawdza serwer (tylko posiadany pet, tylko przy zagrodzie). Gdy nie ma
  `MiasteczkoBazarGra`, działa zapasowe E przy tablicy. Przycisku Pets w HUD i plików Pawła pakiet nie rusza
  (docelowe okno robi Paweł).
- **Premia i skill (D-101):** skill aktywnego peta trafia do StanGracza przez `Sygnaly/Modyfikatory` (źródło `"pety"`):
  statystyki, pasywki i zaklęcie żywiołu w bohaterze walki, premię do łupu liczy stan gracza przy przyjęciu łupu (zaokrąglony
  ułamek Złota / doświadczenia, 0,5 w górę) i przy pokazaniu łupu wysyła klientowi „premia” → napis „+N Złota od peta:
  Jelonek Gaju” (tylko pety z premią do łupu). Silnik walki bez zmian; bez sygnału `Modyfikatory` (starszy stan
  gracza) premia do łupu idzie jak dawniej przez `Pety`.
- **Wskazówka celu** (`swiat/wskazowki_gry`): dla biomu, w którym jest gracz — w lesie „Masz dość Złota na jajko —
  inkubator przy wejściu do lasu”, w Bagnie „Masz dość Złota na jajko Bagna — inkubator przy pomoście” (znacznik nad
  punktem E inkubatora tego biomu), w mieście „…: TELEPORT → Las (inkubator)” ze strzałką — tylko do pierwszego jajka
  tego biomu (atrybuty `PetyCenaJajka*` i `PetyKupioneJajka*` z serwera petów), nie za bramą.

## Następne kroki (opis, liczby z `tools/walka/BALANS_1711.md`, część 3)

- **Pet w walce petów (D-059):** skill peta działa w walkach petów; gracza pet wzmacnia tylko pasywnie. Dziś premia
  jest do łupu; docelowo D-059 mówi o mnożniku statystyk gracza — wejście w `Sygnaly/Bohater` (opis bohatera) bez
  zmiany silnika, do policzenia w kalkulatorze przed włączeniem.
- **Poziom i karmienie (D-052, D-058):** poziom peta robocze maks. 30; karmienie słabszym petem przez rzadkość zjadanego.
- **Ewolucja (D-058):** 3 ewolucje na poziomach peta 10 / 20 / 30; tokeny krainy 60 / 180 / 450 (27 / 82 / 205 minut
  walk); kopie peta 2 / 3 / 5 (płasko 10 na komplet) albo według rzadkości 10 / 8 / 6 / 4 / 3; jeden Shard Ewolucji na
  ewolucję (10% ze Strażnika, średnio 14 prób, z ochroną po 20 wygranych — 12). Komplet legendarnego przy jajku
  z rosnącą ceną to setki jajek — pytanie 41 (ewolucje: wszystkie czy tylko lepsze; liczby).
- **Zapis między sesjami:** profil StanGracza (wersja 2) ma już `pety` i `wydatki`; zapis to zadanie właściciela stanu.

## Zdecydowane

- **Cena jajka stała** (Karol, 17.11.2026, czat: „bo opener jajka jest per biom, więc tak czy siak źródło dropienia
  jajek się zmienia, gdy gracz zmieni biom”): jajko leśne 300 Złota, jajko Bagna 750 — cena nie rośnie z zakupami,
  rośnie tylko między biomami; liczby do doboru (trzymają pierwsze jajko w 5–10 min gry w biomie). Rosnąca i kalkulator
  zostają przełącznikiem w `ustawienia.json`.

## Przyjęte, do zmiany

1. ~~Cena rosnąca~~ — zdecydowane wyżej (stała).
2. **Szanse** 50 / 25 / 15 / 8 / 2% z kalkulatora (D-052 mówi o ok. 1% na legendarnego w najdroższym jajku).
3. **Skille (D-101, liczby do zatwierdzenia)**: tabela w „Skille petów” — pospolite i zwykłe +2–3% (Złoto, Pancerz,
   Siła, Kondycja), rzadkie +15–20% statystyk, epickie i legendarne żywioł + premie; przez `Modyfikatory` stanu gracza.
4. **Pierwszy pet sam idzie za graczem**; kolejne trafiają do zagrody (zmiana tylko w zagrodzie).
5. **Wyklucie automatyczne** ok. 4 s (trzęsienie 1,4 s, pęknięcie 0,6 s, wyskok 1 s, radość 1,2 s), bez „klikania kilka
   razy” z D-060 i bez skracania drzewkiem (D-056).
6. **Jedno jajko na biom** (las, Bagno), jeden aktywny pet (drzewko petów zwiększy ich liczbę, D-056).
7. **Pety od początku gry** — inkubator czynny od pierwszego wejścia do lasu (pytanie 38 nierozstrzygnięte).
8. **E z przytrzymaniem 0,5 s** (chroni przed przypadkowym zakupem); cena widoczna w podpowiedzi i nad jajkiem.
9. **Pet znika** w walce, przelocie, chmurach, mini-grze i przy wyborze klasy (nie czeka obok).
10. **Kopie** liczone jako shardy peta (D-058), rozbiórki jeszcze nie ma.
11. **Napisy „PRÓBA”** na tablicy i w oknie zagrody — okno tymczasowe do czasu okna Pets Pawła.
12. **Jajko Bagna** za stałe 750 Złota (liczba do doboru); licznik ceny osobny (używany tylko przy cenie rosnącej).
13. **Skille Bagna** — od 18.11 według D-101 (różne premie, nie „trochę lepsze od leśnych”; dawniej 6 / 10 / 14 / 18 /
    24% Złota albo doświadczenia).
17. **Jajko Dżungli** za stałe 1350 Złota (reguła 6 min, jak Bagno) i pięć petów Dżungli (tabela wyżej) — 18.11 noc,
    bez Studio; liczby i projekty do zatwierdzenia.
15. **Żywioły** — Światło, Kryształ i Woda z pasywek silnika; Ogień (Ognik) i Jad (Ważeczka) to prawdziwa szansa na
    podpalenie (25%) / zatrucie (30%) przy ciosie przez pole `zaklecie` Modyfikatorów stanu gracza (18.11 noc).
16. **Latarenka i tablica Bagna przestawione, jajko Bagna ciemniejsze** (18.11, po zrzutach z gry): latarenka z boku
    gniazda za tablicą, tablica bliżej punktu E, skorupka `86C6AB`. 18.11 noc (zrzuty `klatki/d101_*`): tablica krok
    przed kępą trzcin stanowiska (z bliska zasłaniała prawy brzeg tablicy), napis „Cena: … Złota” nad całym jajkiem
    (kwiatek na czubku jajka Bagna zasłaniał liczbę).
14. **Gniazdo Bagna na palach** i latarenka stoją we własnym kontenerze na stanowisku jajka z mapy Bagna (mapa bez
    zmian); jajko w gnieździe, wysokość z modelu inkubatora.

## Pliki

| Plik | Co to jest |
|---|---|
| `ustawienia.json` | jedyne źródło: pety, skille, rzadkości, **jajka** (pula, cena, model, stanowisko, punkt E, atrybuty), licznik ceny, teksty, czasy |
| `dane_petow.py` | generator `zrodla/DanePetow.luau` i `zrodla/rigi/*.luau` (rigi z modeli `swiat/postacie`, szanse i cena z kalkulatora, położenia z map, stałe bryły inkubatorów); `--sprawdz` |
| `logika_petow.py` | lustro `zrodla/LogikaPetow.luau` (cena, licznik osobny / wspólny, losowanie, jajko peta i biomu, teksty, zagroda, decyzja serwera) |
| `zrodla/SerwerPetow.server.luau`, `KlientPetow.client.luau`, `RigPetow.luau` | serwer, klient, budowa petów z klocków i klipy przez Motor6D |
| `ekonomia_jajek.py` | kiedy gracz kupi kolejne jajka (tabele wyżej; `--biom bagno`) |
| `skille_petow.py` | wpływ skilli petów (D-101) na walki: szansa wygranej ze strażnikami (Gaj, Topiel, Wąż Stu Lian), czas przejścia trzech biomów, Złoto na minutę |
| `swiat/postacie/ananasik.py`, `leniwczyk.py`, `tukanik.py`, `posazek.py`, `jaguarek.py`, `jajko_dzungli.py` | modele Dżungli (jajko + inkubator: totem ruin, tablica) |
| `podglad.py` → `podglad/pety_lesne.jpg`, `podglad/pety_bagna.jpg` | pięć portretów petów jajka z rzadkością, szansą i skillem + inkubator i jajko (do raportu); `podglad/jajko_lesne_przed_po.jpg` — para przed / po |
| `sprawdz_luau_petow.py` | kontrola statyczna Luau (m.in. bez Robuxów, bez zapisu Złota w pakiecie, klient bez liczb) |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_petow.py` | 51 testów offline (w tym prawdziwe SerwerPetow + SerwerStanu w `luau_mini`, trzy jajka, cena stała i przełączniki; od 25.11 zagroda: Rybki, miejsca, wybór, 6 albo 8 znaczników) |
| `ekonomia_zagrody.py` | zagroda (25.11): Rybki/h pełnej zagrody na każdym poziomie wobec Rybek z walk, koszt miejsc w minutach walk i zwrot |
| `testy/proba_play.py` | próba w Play P00–P15 (+ P07b: każdy pet za graczem); `--bagno`: B00–B09 (jajko Bagna), `--dzungla`: te same punkty dla jajka Dżungli (zrzuty `dz…`); zrzuty do `klatki/`; `--sprawdz` bez Studio. Atrybut klienta `TestKameraProby` na kontenerze: kamera do zrzutów nie chowa petów (tylko próby) |
| `testy/proba_ludzka.py` | przejście „po ludzku”: walki do Złota na jajko (liczba walk i minut), wskazówka, E, wyklucie, pet, premia, zagroda (L01–L09) |
| `swiat/postacie/zoledziak.py`, `mchowy_slimak.py`, `lisciolis.py`, `swietlikowka.py`, `jelonek_gaju.py`, `jajko_lesne.py`, `pety_lesne.py` | modele lasu (Blender i klocki); `pety_lesne.py` — wspólne klipy, oczy, gładkie jajko, tablica szans |
| `swiat/postacie/palkus.py`, `nenufarek.py`, `wazeczka.py`, `ognik.py`, `perlowa_wydra.py`, `jajko_bagienne.py` | modele Bagna (jajko + inkubator: gniazdo na palach, latarenka, tablica) |

## Polecenia

```
python -B swiat/pety_proba/dane_petow.py                 # po zmianie ustawień albo modeli
python -B swiat/pety_proba/testy/test_petow.py           # 51 testów, ok. 50 s
python -B swiat/pety_proba/ekonomia_zagrody.py           # zagroda: Rybki/h wobec walk (liczby robocze)
python -B swiat/pety_proba/zbuduj.py --sucho             # bez Studio
python -B swiat/pety_proba/ekonomia_jajek.py --biom bagno  # cena jajka Bagna
python -B swiat/pety_proba/ekonomia_jajek.py --biom dzungla  # cena jajka Dżungli (reguła 6 min)
python -B swiat/pety_proba/podglad.py                    # podglad/pety_lesne.jpg, pety_bagna.jpg
python -B swiat/postacie/przebuduj.py zoledziak mchowy_slimak lisciolis swietlikowka jelonek_gaju jajko_lesne --bez-filmow
python -B swiat/postacie/przebuduj.py palkus nenufarek wazeczka ognik perlowa_wydra jajko_bagienne --bez-filmow
# Studio (Edit), po kolei: stan gracza (pełna budowa — nowe sygnały WydajZloto i Pety), wskazówki, pety, próba
python -B swiat/stan_gracza/zbuduj.py
python -B swiat/wskazowki_gry/zbuduj.py
python -B swiat/pety_proba/zbuduj.py
python -B swiat/pety_proba/testy/proba_play.py <folder wyników poza repo>
python -B swiat/pety_proba/testy/proba_play.py <folder wyników poza repo> --bagno   # jajko Bagna (B00–B09)
python -B swiat/pety_proba/testy/proba_play.py <folder wyników poza repo> --dzungla # jajko Dżungli (B00–B09, zrzuty dz…)
python -B swiat/pety_proba/zbuduj.py --usun              # wyłącznik: gra wraca do stanu sprzed próby
```

## Zmiany w innych pakietach (małe, w osobnych miejscach)

- `swiat/stan_gracza`: sygnały `Sygnaly/WydajZloto` i `Sygnaly/Pety` (`zbuduj.py` → `INNE`); `dane.py` (`wydatki`,
  `pety`, wersja profilu 2, przypadki wzorcowe `wydatek`, `wydaj`, `premia`, `premia_lupu`); `logika_stanu.py`
  i `LogikaStanu.luau` (`czysty_wydatek`, `wydaj`, `czysta_premia`, `premia_lupu`, profil z `pety` i `wydatki`);
  `SerwerStanu.server.luau` (wydatek, pety, premia przy przyjęciu łupu, komunikat „premia”, atrybuty `PetAktywny`
  i `PetyLiczba`); testy `4f`, `8i`, `8j`, zmieniony `6e`.
- `swiat/wskazowki_gry`: kroki `f_jajko`, `f_jajko_miasto` i (17.11 wieczór) `f_jajko_bagno`, cel `jajko`, pola stanu
  `jajko` i `kupione` (wcześniej `pety`: od jajka Bagna krok jest „do pierwszego jajka biomu”), źródła per biom
  w `ustawienia.json` (`zrodla.biomy[].inkubator`, `atrybut_ceny_jajka`, `atrybut_kupionych_jajek`); klient bierze
  jajko biomu, w którym stoi gracz; testy `2g` i `5e`, README.
- `swiat/postacie`: nowe moduły modeli (lista wyżej); istniejących plików nie zmieniano.
- `swiat/stan_gracza` (25.11, zagroda daje Rybki): polecenie `Pety("przychod", gracz, { ile, zrodlo, cel })` — Rybki
  spoza walki od źródła z listy `PAKIETY_PRZYCHODOW` (`dane.py`, `D.przychody`), dopisane do `Gold` jak łup, bez premii
  i licznika walk; `czysty_przychod` / `czystyPrzychod` z przypadkami wzorcowymi; test `8j2`. Wdrożenie:
  `zbuduj.py --skrypty` (bez nowych obiektów).

## Co sprawdzone w grze (Studio, tryb Play, 17.11.2026)

**`testy/proba_play.py` — 16 z 17 punktów OK** (P06 raz OK, raz „BŁĄD” progu: po marszu pet stał 7,4 st od postaci
zamiast ≤ 6 — postać jeszcze szła; w P07b przy postoju każdy pet stoi 4,8–5,2 st od środka postaci):
brak Złota → „Brakuje ci 300 Złota (masz 0, jajko kosztuje 300)”; kupno prawdziwym E (przytrzymanie) → Złoto −300,
pet, cena następnego 700, podpowiedź „Kup za 300 Złota”; drugie E w trakcie → „Jajko jeszcze się wykluwa…”; każdy
z pięciu petów idzie za graczem (pety kupione haczykiem z wymuszonym losem, wybór haczykiem — tylko w próbie);
zagroda: 4 pety na miejscach, tablica z kopiami, E opiekunki otwiera okno „PRÓBA”, wybór zmienia peta za graczem;
premia przy łupie: łup 100 + 12 (Liściolis) i napis „+12 Złota od peta: Liściolis”; reset postaci w trakcie
wyklucia — pet jest, po odrodzeniu idzie za graczem; **walka na arenie (D-095)**: w walce 0 petów u gracza
i `PetCzeka` dla innych, po walce pet wraca; bez sygnału `Pety` → „Inkubator nieczynny…”; konsola bez błędów.

**`testy/proba_ludzka.py` — 9 z 9 OK**, nowy gracz, prawdziwe klawisze i kliknięcia: TELEPORT → chmury → las,
**15 walk (14 wygranych) do pierwszych 300 Złota** (poziom 4), wskazówka „Masz dość Złota na jajko — inkubator przy
wejściu do lasu”, E przy inkubatorze → Mchowy Ślimak, pet za graczem (5,1 st), walka z premią („+1 doświadczenia od
peta”), Kamień Powrotu → bazar → E opiekunki → okno → „Odstaw peta” → „Wybierz” (kliknięcia). Czas do 300 Złota
w prawdziwej grze: ok. 8 min (15 walk × ok. 31 s jak w symulacji); pomiar próby (11 min) jest zawyżony, bo czas
ekranu walki w tempie ×4 liczony z opóźnieniem narzędzia razy cztery.

**Poprawione po zrzutach:** napisy na tablicy szans (równe wiersze, czytelne z punktu E); jajko cieplejsze w kolorze
(z bliska było białe); części w świecie jako Model „Persistent” (przez streaming klient nie miał punktu E i napisu
ceny — E nie działało przy pierwszym podejściu); pet po wykluciu ląduje obok gracza, nie w nim; mniejszy błysk przy
pęknięciu (cały kadr był różowy); napis „NOWY PET!” bez AlwaysOnTop (inaczej nie było go na zrzutach); okno zagrody
wyższe (5. wiersz był ucięty); poroże Jelonka świeci tylko na kryształach (z bliska zlewało się w cyjanową plamę).

**Jajko Bagna i cena stała (17.11 wieczór, pas skrócony — D-096) — `proba_play.py --bagno`: 14 z 14 OK**
(B05, B07 — zrzuty do obejrzenia): dwa jajka u klienta, ceny 300 / 750; brama lasu otwarta haczykiem
(`otworzBrame`, jak próby Bagna), przelot kamery Bagna przeczekany; przy inkubatorze Bagna bez Złota → „Brakuje ci 750
Złota (masz 0, jajko kosztuje 750)”; wskazówka „Masz dość Złota na jajko Bagna — inkubator przy pomoście”; kupno
prawdziwym E → Złoto −750, cena Bagna 750, cena lasu 300 bez zmian; każdy z pięciu petów Bagna idzie za graczem
(5,0–5,1 st; wybór haczykiem); zagroda z dziesięcioma petami (6 na miejscach), tablica w dwóch kolumnach, okno
przewinięte; wybór Perłowej Wydry z okna. **Regresja lasu: 17 z 17 OK** (kupno za 300, następna cena 300).
Pierwsza próba `--bagno` innego agenta: B02–B04 bez otwartej bramy (gracz cofany przed bramę lasu), a ręczne E
w Bagnie bez zakupu — najpewniej w trakcie przelotu kamery (podpowiedzi wtedy nie działają); odtworzone po przelocie
kupno działa. Mylący był też haczyk klienta: `akcjaE` pokazywało zawsze jajko leśne — teraz jajko najbliższego
inkubatora (`jajkoPrzy`). Serwer od teraz sam sprawdza zasięg inkubatora (test `5c1`).

## Czego nie sprawdzono

**Zagroda daje Rybki i nowe modele leśnych petów — wdrożone w Studio 26.11 (00:13–01:05)**: `stan_gracza/zbuduj.py
--skrypty`, pełna `pety_proba/zbuduj.py` i pełna `miasteczko_bazar_gra/zbuduj.py` (po przebudowie miasta 25.11 część
z podpowiedzią E Jagody stała jeszcze w starym miejscu w głębi zagrody — E przed Jagodą kupowało wtedy jajko Pawła).
`proba_play.py --zagroda`: **Z01–Z09 9/9 OK** + P01, P02, P15 (naliczanie +3 Rybki w 22 s przy 9,9/min, napis „+N”,
2 modele na 8 znacznikach, okno z wierszem zagrody, odmowa „Brakuje ci 1000 Rybek…”, ulepszenie 2 → 4, „Z zagrody” /
„Najrzadsze”, pet za graczem poza zagrodą). Regresja: las 14 OK + 3 „?” (zrzuty; P07b — każdy z pięciu nowych petów idzie za graczem, 4,6–5,3 st), `--bagno` 10 OK + 4 „?” (zrzuty), `--dzungla`
10 OK + 4 „?”. W próbach poprawione: stanowisko przed Jagodą, P09 i B08 (na legowiskach stoją tylko pety W zagrodzie — na
starcie 2, nie wszystkie posiadane), Z07 i P11 (zagroda dopisuje Rybki także w trakcie punktu). Ręcznie (Play ze
znacznikiem próby): 9 petów, zagroda 8/8 (+36 Rybek/min), pety równo na legowiskach, bez kolizji z płotem, Jelonek
45/45 widocznych części; okno Pets Pawła (`stan`, „zaloz”, „najlepsze”; „usun” → „coming soon”) i jego jajko
(prawdziwe E: −300 Rybek, +1 pet) działają. Zrzuty `klatki/noc2511_*.jpg`. Teksty: „Miejsca w zagrodzie: N” zamiast
„Zagroda ma teraz N miejsc”, napis „+1 Rybka / +3 Rybki / +5 Rybek”.
Znane kłopoty (do decyzji): pet ze slotu 2 okna Pets Pawła stoi też w zagrodzie i daje Rybki; E Jagody otwiera naraz
tymczasowe okno „PRÓBA” i okno Pets Pawła; jajko Pawła stoi ok. 3 st od stoiska Jagody (z boku E kupuje jajko, przodem
do Jagody otwiera okno); tablica „TWOJE PETY” stoi na placu ok. 14 st przed bramą (`tablica_od_e` liczone od nowego
punktu E); Neon oczu Świetlikówki (F26A00) wygląda w grze na żółto-pomarańczowy.

**Jajko Dżungli (18.11, 03:10–03:24, Studio)** — `proba_play.py --dzungla`: **14 z 14 OK** (trzy jajka lokalne, ceny
300 / 750 / 1350, brak Złota → „Brakuje ci 1350 Złota”, wskazówka `f_jajko_dzungla`, kupno prawdziwym E, pięć petów
Dżungli za graczem ok. 5,1 st, wyklucie każdego, zagroda z 10 petami, wybór Jaguarka; zgodność logiki 229/229, konsola
czysta). Regresja: `--bagno` 14/14, las 17/17, próba dymna 14/14 (D04 łup 0 → 16). Walka w Dżungli z Jaguarkiem
(Zwijogon, arena Dżungli) rusza po przelocie kamery biomu; modyfikator gracza: źródła `kowal`, `pety`,
`szczescie_poczatkujacego`, pasywki Dzikości. Zrzuty `klatki/dz*`. Niesprawdzone w grze: Mag i Zwiadowca z petami
Dżungli, Runy w walce.

Dwóch graczy naraz (pet widoczny dla innych — kod rysuje pety wszystkich graczy u każdego klienta, ale w Studio był
jeden gracz), telefon i dotyk (E przytrzymane palcem), wydajność przy wielu graczach z petami.
