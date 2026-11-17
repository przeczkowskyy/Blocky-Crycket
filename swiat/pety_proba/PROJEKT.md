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
> (liczy ją StanGracza, napis „+N Złota od peta” przy łupie). Wskazówka celu: „Masz dość Złota na jajko…”.
>
> **Od 17.11 (wieczór) drugie jajko — Jajko Bagna** (D-060: inkubator w każdym biomie): na tym samym stanowisku przy
> Pomoście Przybycia Bagna stoi **błotne gniazdo z trzcin na palach z latarenką-ognikiem** i tablicą szans; pięć petów
> Bagna, trochę lepszych od leśnych tej samej rzadkości. **Cena jajka jest stała** (decyzja Karola 17.11): jajko leśne
> 300 Złota, jajko Bagna 750 — rośnie tylko między biomami (pierwsze jajko po ok. 6 min gry w biomie). Jajko = wpis
> w `ustawienia.json` → `jajka` (trzeci biom = nowy wpis, bez kodu).
> Jajka (leśne też) są od teraz **gładkie — z elipsoid**, nie ze schodków klocków („ul”, para przed / po niżej).

## Pięć petów leśnego jajka

Własne projekty (modele z klocków w `swiat/postacie/`, plansze i portrety w `swiat/postacie/wynik/<id>/`). Szanse:
`tools/walka/progresja.py` (`ZALOZENIA["szanse_jajka"]`). Rzadszy = efektowniejszy: pospolity, zwykły i rzadki bez
świecenia, epicki i legendarny świecą (Neon) i mają słup światła przy wykluciu.

| Pet | Rzadkość | Szansa | Skill (pasywny, z walk) | Wygląd |
|---|---|---:|---|---|
| Żołędziak | Pospolity | 50% | Zbieracz: +5% Złota | pulchny żołądź w czapeczce z listkiem na ogonku, z patyczkowymi rączkami |
| Mchowy Ślimak | Zwykły | 25% | Cierpliwość: +8% doświadczenia | bladozielony ślimak z oczami na czułkach i muszlą w mchu z czerwonym grzybkiem |
| Liściolis | Rzadki | 15% | Lisi Spryt: +12% Złota | pomarańczowy lisek z uszami-liśćmi, liściastym kołnierzykiem i liściem na końcu ogona |
| Świetlikówka | Epicki | 8% | Nocna Nauka: +15% doświadczenia | śliwkowa sówka ze świecącymi oczami i brzuszkiem-latarenką, krążą wokół niej trzy świetliki |
| Jelonek Gaju | Legendarny | 2% | Błogosławieństwo Gaju: +20% Złota i doświadczenia | cętkowany jelonek ze świecącym kryształowym porożem w kwiatkach i złotymi kopytkami |

Klipy każdego peta: `spoczynek`, `chod`, `radosc`, `wyklucie`. Jajko: `spoczynek`, `trzesienie`, `pekniecie`.
Pies, Slime i Smok (pety z kanonu) zostają na inne jajka (np. miejskie).

## Pięć petów Jajka Bagna (obok leśnych tej samej rzadkości)

Własne projekty pod klimat Bagna (mokradła, mgła, ogniki, pomosty), sylwetki inne niż pety lasu i niż potwory Bagna
(ropuchy, błotniak, kłoda) — pety „do kochania”. Te same rzadkości i szanse. Skill Bagna jest **trochę lepszy** niż
leśny tej samej rzadkości (o 17–25%), ale **słabszy od leśnego o stopień rzadszego** — leśny legendarny (+20% obu)
wygrywa z epickim Ognikiem, przegrywa tylko z legendarną Perłową Wydrą (test `1f`).

| Rzadkość · szansa | Pet Bagna | Skill Bagna | Pet lasu | Skill lasu | Wygląd (Bagno) |
|---|---|---|---|---|---|
| Pospolity · 50% | Pałkuś | Szelest Trzcin: +6% Złota | Żołędziak | +5% Złota | brązowa kolba pałki wodnej z buzią na zielonej łodyżce, liście-rączki, puch na czubku |
| Zwykły · 25% | Nenufarek | Spokojna Toń: +10% doświadczenia | Mchowy Ślimak | +8% doświadczenia | miętowy żółwik z pancerzem z liścia grzybienia i różowym kwiatem nenufaru |
| Rzadki · 15% | Ważeczka | Bystre Oko: +14% Złota | Liściolis | +12% Złota | turkusowa ważka z oczami-kopułami, odwłokiem w paski i czterema błękitnymi skrzydłami (unosi się) |
| Epicki · 8% | Ognik | Błędny Blask: +18% doświadczenia | Świetlikówka | +15% doświadczenia | miętowy błędny ognik z buzią i świecącym, zawiniętym płomieniem, dwie krążące iskry (unosi się) |
| Legendarny · 2% | Perłowa Wydra | Perła Topieli: +24% Złota i doświadczenia | Jelonek Gaju | +20% Złota i doświadczenia | wydra na tylnych łapkach z otwartą muszlą i świecącą perłą, wianek z grzybienia, naszyjnik z pereł |

Podgląd zbiorczy: `podglad/pety_bagna.jpg` (ten sam układ co `podglad/pety_lesne.jpg`, pod skillem — pet lasu tej
rzadkości). Jajko Bagna: miętowe w ciemnozielone i turkusowe cętki, z liściem grzybienia i kwiatkiem na czubku.

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
zostają jako przełącznik. Gracz widzi cenę przy E („Kup za 300 Złota”), nad jajkiem („Cena: 300 Złota”, bez
„następne…”) i na tablicy („cena: 300 Złota”). Premii petów (+% Złota) symulacja nie liczy — to dolna granica tempa.

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
- **Zagroda (bazar):** do 6 posiadanych petów (bez aktywnego; przy dziesięciu — najrzadsze najpierw) stoi na miejscach
  z mapy `zagroda_miejsce_1…6` z napisem „Nazwa ×N” (kopie = shardy peta, D-058); tablica przy bramie zagrody w dwóch
  kolumnach — jajko po jajku („► ” przy aktywnym, „jeszcze żadnego” w pustej); **E opiekunki** (pakiet bazaru, zdarzenie
  `ReplicatedStorage.OknoMiejsca`, id `zagroda_petow`) otwiera tymczasowe okno „TWOJE PETY · PRÓBA”: **przewijane**,
  podzielone na jajka (nagłówek jajka w jego kolorze), wiersz na peta (kolor rzadkości, ×kopie, rzadkość, skill),
  przycisk „Wybierz” i „Odstaw peta”. Wybór sprawdza serwer (tylko posiadany pet, tylko przy zagrodzie). Gdy nie ma
  `MiasteczkoBazarGra`, działa zapasowe E przy tablicy. Przycisku Pets w HUD i plików Pawła pakiet nie rusza
  (docelowe okno robi Paweł).
- **Premia:** skill peta liczy StanGracza przy przyjęciu łupu (zaokrąglony ułamek Złota / doświadczenia z tej walki,
  0,5 w górę) i przy pokazaniu łupu wysyła klientowi „premia” → napis „+N Złota od peta: Liściolis”. Silnik walki
  bez zmian.
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
3. **Skille**: premia do Złota albo doświadczenia z walk 5 / 8 / 12 / 15 / 20% (legendarny: oba), poza silnikiem walki.
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
13. **Skille Bagna** 6 / 10 / 14 / 18 / 24% — o 17–25% lepsze od leśnych tej samej rzadkości, słabsze od leśnych
    o stopień rzadszych.
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
| `podglad.py` → `podglad/pety_lesne.jpg`, `podglad/pety_bagna.jpg` | pięć portretów petów jajka z rzadkością, szansą i skillem + inkubator i jajko (do raportu); `podglad/jajko_lesne_przed_po.jpg` — para przed / po |
| `sprawdz_luau_petow.py` | kontrola statyczna Luau (m.in. bez Robuxów, bez zapisu Złota w pakiecie, klient bez liczb) |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--skrypty`, `--usun`, `--studio` |
| `testy/test_petow.py` | 41 testów offline (w tym prawdziwe SerwerPetow + SerwerStanu w `luau_mini`, oba jajka, cena stała i przełączniki) |
| `testy/proba_play.py` | próba w Play P00–P15 (+ P07b: każdy pet za graczem); `--bagno`: B00–B09 (jajko Bagna); zrzuty do `klatki/`; `--sprawdz` bez Studio. Atrybut klienta `TestKameraProby` na kontenerze: kamera do zrzutów nie chowa petów (tylko próby) |
| `testy/proba_ludzka.py` | przejście „po ludzku”: walki do Złota na jajko (liczba walk i minut), wskazówka, E, wyklucie, pet, premia, zagroda (L01–L09) |
| `swiat/postacie/zoledziak.py`, `mchowy_slimak.py`, `lisciolis.py`, `swietlikowka.py`, `jelonek_gaju.py`, `jajko_lesne.py`, `pety_lesne.py` | modele lasu (Blender i klocki); `pety_lesne.py` — wspólne klipy, oczy, gładkie jajko, tablica szans |
| `swiat/postacie/palkus.py`, `nenufarek.py`, `wazeczka.py`, `ognik.py`, `perlowa_wydra.py`, `jajko_bagienne.py` | modele Bagna (jajko + inkubator: gniazdo na palach, latarenka, tablica) |

## Polecenia

```
python -B swiat/pety_proba/dane_petow.py                 # po zmianie ustawień albo modeli
python -B swiat/pety_proba/testy/test_petow.py           # 41 testów, ok. 13 s
python -B swiat/pety_proba/zbuduj.py --sucho             # bez Studio
python -B swiat/pety_proba/ekonomia_jajek.py --biom bagno  # cena jajka Bagna
python -B swiat/pety_proba/podglad.py                    # podglad/pety_lesne.jpg, pety_bagna.jpg
python -B swiat/postacie/przebuduj.py zoledziak mchowy_slimak lisciolis swietlikowka jelonek_gaju jajko_lesne --bez-filmow
python -B swiat/postacie/przebuduj.py palkus nenufarek wazeczka ognik perlowa_wydra jajko_bagienne --bez-filmow
# Studio (Edit), po kolei: stan gracza (pełna budowa — nowe sygnały WydajZloto i Pety), wskazówki, pety, próba
python -B swiat/stan_gracza/zbuduj.py
python -B swiat/wskazowki_gry/zbuduj.py
python -B swiat/pety_proba/zbuduj.py
python -B swiat/pety_proba/testy/proba_play.py <folder wyników poza repo>
python -B swiat/pety_proba/testy/proba_play.py <folder wyników poza repo> --bagno   # jajko Bagna (B00–B09)
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

Dwóch graczy naraz (pet widoczny dla innych — kod rysuje pety wszystkich graczy u każdego klienta, ale w Studio był
jeden gracz), telefon i dotyk (E przytrzymane palcem), wydajność przy wielu graczach z petami.
