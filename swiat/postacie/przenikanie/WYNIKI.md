# Przenikanie broni w głowę i tułów — wyniki (17.11.2026)

*Status: pomiar i poprawki bez Studio (propozycja, nie kanon). Zadanie z `B&C/Produkcja/Zadania.md` — uwaga Karola
z panelu z 13.11: „broń trzymana w ręku nie może nachodzić na twarz w żadnej animacji ani po wygranej walce”.
Dwie części tego samego dnia: (1) pomiar, test i poprawka upadku Maga; (2) poprawki w odtwarzaczu (wskrzeszenie,
obrót zwycięzcy przed radością) i skręt kostura Maga. Wszystkie liczby poniżej — z bieżących danych po obu częściach.*

## W skrócie

- **Policzone:** 6 aktorów z bronią w ręku (Wojownik, Zwiadowca, Mag, Leśny Troll, Muchomornik i nowy Bulgotnik
  z Bagna) — każdy klip z danych gry i każde przejście, które robi odtwarzacz: **133 scenariusze, 20 591 póz,
  0 ponad próg**.
- **Oblane przed poprawkami: 3** — klip `upadek` Maga (kostur przez głowę w połowie klatki 23→24, głowa 0,185) oraz
  wskrzeszenie Wojownika (jelec w biodrach, tułów 0,171) i Maga (kostur przez głowę, głowa 0,209, tułów 0,144).
  Wszystkie poprawione.
- **Poprawione w klipach Maga** (`swiat/postacie/kot_mag.py`, dane przeliczone generatorem):
  `upadek` (orientacja łapki w pozie „leci”) i — część 2 — **skręt kostura w jednej klatce** w `atak`,
  `kula_ognia`, `lodowy_pocisk` (przód kryształu w pozach ataku w dół): 156° / 150° / 84° na klatkę → 6° / 6° / 4°.
- **Poprawione w odtwarzaczu** (część 2): wskrzeszenie gra upadek wstecz zamiast mieszać leżenie ze spoczynkiem
  (głowa Maga 0,209 → odstęp 0,158; tułów Wojownika 0,171 → odstęp 0,155); obrót zwycięzcy do kamery zaczyna się
  0,45 s przed radością (twarz w chwili cięcia do objazdu: oczy Wojownika 100% → 0%, Zwiadowcy 77% → 0%, rysy
  najwyżej 4%). Czas zdarzeń z dziennika bez zmian.
- **Kamera finału:** z przodu i przy cięciu do objazdu broń nie zasłania oczu ani rysów twarzy u żadnej klasy.
  **Do decyzji ludzi (nie zmieniane):** z ukosa w walce (ujęcia „efekt”, „zbliżenie” na gracza, ok. 60–70°) miecz
  Wojownika w spoczynku zasłania prawe oko (oczy 86%, rysy 74%) — wymagałoby zmiany pozy spoczynku.
- **Test na stałe:** `swiat/test_walki2/testy/test_przenikania.py` — **12/12**. Pilnuje przenikania we wszystkich
  klipach i przejściach (także nowych klipów i nowych aktorów z bronią rozpoznaną po nazwie — sam złapał Bulgotnika),
  kamery finału i skrętu broni (≤ 70°/klatkę). Wskrzeszenie i obrót zwycięzcy czyta z kodu odtwarzacza. `ZNANE` puste.

## Jak liczone (i skąd pewność, że tak jak w grze)

**Dane.** `swiat/test_walki2/dane/<klucz>.json` — dokładnie to, co odtwarza gra (rig z klocków i klipy co klatkę,
30 kl./s, z Blendera przez `aktorzy.py`). Narzędzie czyta też dowolny plik z `roblox_klocki.rig()` (`--dane`).

**Pozy** (`pozy.py`) — lustro modułu gry `zrodla/Klipy.luau` i stawów z `budowa/szablon.luau`:
klatka kości = `CFrame.new(x, y, z) * CFrame.fromOrientation(rx, ry, rz)`; między klatkami `CFrame:Lerp` (położenie
liniowo, obrót po kwaternionach) jak `probka`; mieszanie torów przy przejściu (`ustawWagi`, `krok`, `zastosuj`):
nowy tor 0 → 1, stare 1 → 0 w czasie przejścia, poza = `stara:Lerp(nowa, w / suma)`; staw
`Part1 = Part0 · C0 · Transform · C1⁻¹`. Odtwarzacz nie używa nakładek kości (`ustawNakladke` nie jest wołane),
a ruch proceduralny (doskok, pochylenie, obrót, zejście w tył) przesuwa całego aktora sztywno — nie zmienia broni
względem ciała, więc go nie liczę.

Zgodność z grą (policzone):
1. wzór stawów potwierdzony w Play próbą `testy/klatki_aktorow.py` — odchyłka stawów 0,0 u wszystkich 8 aktorów
   (`klatki/raport_klatek.json`);
2. `pozy.py` = istniejące lustro `geometria.py` (używane przez testy pakietu) w każdej klatce: różnica ≤ 7·10⁻¹⁵;
3. liczby zmierzone wcześniej w Studio wychodzą z lustra: Bariera Maga — biodra +0,196 (Studio +0,20), najniższy
   punkt brył −0,012…0,000 (Studio 0 ± 0,011); blok Wojownika — biodra w tył 0,414 (klip 0,41, Play 0,37–0,40);
   unik Wojownika — odskok 1,73 (1,70);
4. klipy walki Maga i Wojownika z modułów policzone bez Blendera (klucz w każdej klatce) = dane gry co do bitu.

Założenie niesprawdzone w Studio: `CFrame:Lerp` obraca slerpem po krótszym łuku (między sąsiednimi klatkami różnica
slerp/nlerp jest pomijalna).

**Próbkowanie.** Każdy klip z danych (także nieużywany w walce `czar` Maga): 120 próbek na sekundę czasu klipu
(cztery na klatkę danych, w tym połowy klatek, gdzie gra liczy Lerp) i koniec klipu. Przejścia, które gra robi
naprawdę (`OdtwarzaczWalki2.luau`):

| Przejście | Skąd w grze | Jak próbkowane |
|---|---|---|
| spoczynek → akcja (atak, krytyk, unik, blok, trafienie, umiejętności) | `Sesja:klip`, przejście 0,12 s | 8 faz pętli spoczynku × prędkość klipu ×1 i ×2 |
| akcja → spoczynek | opcja `potem`, 0,15 s | od ostatniej klatki akcji |
| → upadek | `Sesja:upadek`, 0,08 s | ze spoczynku (8 faz) i z każdej chwili trafienia |
| wskrzeszenie (tylko klasy) | `Obsluga.wskrzeszenie` — model czytany z kodu (`pomiar.model_wskrzeszenia`) | od 17.11 (część 2): upadek wstecz (wszystkie chwile klipu) i 0,15 s z klatki 0 upadku do spoczynku; wcześniej: mieszanie ostatniej klatki upadku ze spoczynkiem 0,45 s |
| spoczynek → radość | finał, 0,2 s | 8 faz (radość zaczyna się ≥ 1,48 s po trafieniu kończącym — atak już się skończył) |

**Bryły.** Dokładne kształty Roblox z wierszy `czesci` (blok, klin, narożnik, walec, kula, siatki Sphere / Cylinder)
wg pomiarów w `panel/luau/KSZTALTY.md` (`bryly.py`, test sprawdza punkty kontrolne z tej notatki).

**Miara** (`pomiar.py`). Dla pary bryła broni W × bryła ciała B: m = min po punktach W odległości ze znakiem od B.
m < 0 → **głębokość** = jak głęboko pod powierzchnią bryły ciała leży najgłębszy punkt broni; m ≥ 0 → **odstęp**.
Siatka punktów w bryłach broni co 0,08 studa, potem zagęszczanie wokół najlepszego punktu do ok. 0,0015 studa
(funkcja jest wypukła, więc minimum jest jedno). Głębokość liczona też w **sumie brył strefy** (promienie z punktu do
wyjścia ze wszystkich brył), bo stos cienkich warstw (dzwon szaty Maga: dyski 0,23 studa) ograniczałby ją do połowy
grubości warstwy. Pary dalej niż 0,6 studa — „≥ 0,6”.

**Strefy.** Głowa = bryły ciała na kości głowy (Wojownik: z hełmem; Zwiadowca: z kapturem; Mag: z uszami),
kapelusz Maga osobno, tułów = UpperTorso + LowerTorso (u potworów Tułów + Biodra; u stworów z kością `Cialo`, np.
Bulgotnika — `Cialo`). Broń: miecz i tarcza Wojownika, łuk i sztylet Zwiadowcy, kostur Maga (z kryształem), maczuga
Trolla, laska Muchomornika, kij Bulgotnika. Bez broni w ręku (pominięci): Slime, Wilk, Strażnik Gaju, Rechotek,
Kłodokłap, Ropucha z chatką, Strażnik Topieli.

**Progi.**
- **Głowa i kapelusz: 0,02 studa.** Tolerancja rzędu grubości krawędzi: najcieńsze bryły twarzy (oczy, brwi, nity)
  mają 0,03–0,06 studa i wystają z głowy o połowę grubości; 0,02 studa to mniej niż piksel na telefonie (głowa
  bohatera to ok. 40–90 pikseli wysokości).
- **Tułów: 0,10 studa — dotyk dozwolony.** Broń trzymana przy ciele dotyka ubrania z założenia: rękojeść przy pasie,
  tarcza przy boku, łuk przy kołczanie, dolne okucie kostura przy dzwonie szaty, kij Bulgotnika przy błotnym kopcu.
  Dozwolone jest „wgniecenie” warstwy ubrania (tabard, pas, peleryna, szata: 0,05–0,12 studa), nie wejście w ciało
  pod nią. Najgłębszy dozwolony dotyk w danych: okucie kostura w dzwonie szaty Maga 0,077 (`kula_ognia`, kl. 36) —
  podgląd `podglad/mag_kula_ognia_dotyk_szaty.png`.
- **Skręt broni wokół własnej osi: 70° na klatkę** (część 2, `pomiar.PROG_SKRETU`). Liczony po drodze gry
  (klatka → pół klatki → klatka, Lerp), oś = najdłuższy wymiar broni; broń prawie kulista albo płaska (wydłużenie
  < 2, np. tarcza) pomijana. Uzasadnienie: najszybszy zamierzony skręt w klipach to 54° (sztylet Zwiadowcy), maczuga
  42°, laska 46°, miecz 32°; przy 30 kl./s skręt ponad ok. 70° (2100°/s) nie czyta się jako obrót, tylko jako
  mignięcie — kryształ kostura (4 jednakowe ściany) przy 90° wygląda jak bez ruchu, przy 120–180° jak przeskok
  w drugą stronę. Wyjątki (zamierzone szybkie obroty): `pomiar.WYJATKI_SKRETU` — dziś puste.

## Wyniki — klasa × klip, przed i po

Liczby w studach. **Pogrubione** = głębokość ponad próg; „dotyk” = głębokość poniżej progu; „odst.” = odstęp.
„Przed” = dane i odtwarzacz sprzed 17.11.2026; „po” = bieżące. Przejścia zebrane według rodzaju (w nawiasie liczba
scenariuszy; podany najgorszy; w wierszu wskrzeszenia „po” czas to chwila klipu upadku odgrywanego wstecz). Pełna
lista: `python -B swiat/postacie/przenikanie/przenikanie.py --md`.

#### Wojownik (miecz, tarcza; strój „bojowy”)

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|
| `idle` | 0,23 s (kl. 7,0) · Jelec koniec → Helm bok P | odst. 0,133 | odst. 0,133 | odst. 0,328 | odst. 0,328 | OK |
| `chod` | 0,01 s (kl. 0,2) · Jelec koniec → Helm bok P | odst. 0,214 | odst. 0,214 | odst. 0,272 | odst. 0,272 | OK |
| `atak_miecz` | 0,76 s (kl. 22,8) · Glowica → LowerTorso | odst. 0,134 | odst. 0,134 | odst. 0,055 | odst. 0,055 | OK |
| `wiwat` | 0,90 s (kl. 27,0) · Jelec koniec → Helm kopula | odst. 0,475 | odst. 0,475 | ≥ 0,6 | ≥ 0,6 | OK |
| `blok` | 0,12 s (kl. 3,5) · Jelec koniec → UpperTorso | odst. 0,117 | odst. 0,117 | odst. 0,091 | odst. 0,091 | OK |
| `unik` | 0,33 s (kl. 10,0) · Glowica → UpperTorso | odst. 0,103 | odst. 0,103 | odst. 0,093 | odst. 0,093 | OK |
| `trafienie` | 0,62 s (kl. 18,5) · Jelec koniec → Helm bok P | odst. 0,133 | odst. 0,133 | odst. 0,277 | odst. 0,277 | OK |
| `upadek` | 0,00 s (kl. 0,0) · Jelec koniec → Helm bok P | odst. 0,143 | odst. 0,143 | odst. 0,155 | odst. 0,155 | OK |
| `ciecie` | 1,60 s (kl. 48,0) · Jelec koniec → Helm bok P | odst. 0,143 | odst. 0,143 | odst. 0,330 | odst. 0,330 | OK |
| `miazdzacy_cios` | 0,00 s (kl. 0,0) · Jelec koniec → Helm bok P | odst. 0,143 | odst. 0,143 | odst. 0,330 | odst. 0,330 | OK |
| `kamienna_skora` | 1,46 s (kl. 43,7) · Jelec koniec → Helm bok P | odst. 0,141 | odst. 0,141 | odst. 0,330 | odst. 0,330 | OK |
| spoczynek → akcja (0,12 s; wszystkie akcje) (7) | idle→blok: 0,08 s przejścia · Jelec koniec → UpperTorso | odst. 0,106 | odst. 0,106 | odst. 0,065 | odst. 0,065 | OK |
| akcja → spoczynek (0,15 s) (7) | atak_miecz→idle: 0,15 s przejścia · Jelec koniec → Helm bok P | odst. 0,134 | odst. 0,134 | odst. 0,329 | odst. 0,329 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,01 s przejścia · Jelec koniec → Helm bok P | odst. 0,140 | odst. 0,140 | odst. 0,310 | odst. 0,310 | OK |
| wskrzeszenie (przed: mieszanie 0,45 s; po: upadek wstecz + 0,15 s) (1) | upadek wstecz→idle (wskrzeszenie): 0,15 s przejścia · Jelec koniec → Helm bok P | odst. 0,147 | odst. 0,134 | **0,171** | odst. 0,155 | OBLANY → **OK** |
| spoczynek → radość (0,2 s) (1) | idle→wiwat: 0,01 s przejścia · Jelec koniec → Helm bok P | odst. 0,189 | odst. 0,189 | odst. 0,399 | odst. 0,399 | OK |

#### Zwiadowca (łuk, sztylet)

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|
| `idle` | 1,00 s (kl. 30,0) · Jelec koniec → Kirys | odst. 0,500 | odst. 0,500 | odst. 0,418 | odst. 0,418 | OK |
| `ruch` | 0,32 s (kl. 9,5) · Jelec koniec → Kirys | odst. 0,387 | odst. 0,387 | odst. 0,143 | odst. 0,143 | OK |
| `atak` | 0,12 s (kl. 3,8) · Jelec koniec → Kirys | odst. 0,515 | odst. 0,515 | odst. 0,262 | odst. 0,262 | OK |
| `umiejetnosc` | 0,18 s (kl. 5,3) · Glowica → Kirys | odst. 0,130 | odst. 0,130 | odst. 0,004 | odst. 0,004 | OK |
| `uderzenie_z_gory` | 0,13 s (kl. 4,0) · Jelec koniec → Kirys brzeg | odst. 0,515 | odst. 0,515 | odst. 0,302 | odst. 0,302 | OK |
| `trafienie` | 0,37 s (kl. 11,0) · Jelec koniec → Kirys | odst. 0,515 | odst. 0,515 | odst. 0,431 | odst. 0,431 | OK |
| `unik` | 1,16 s (kl. 34,8) · Jelec koniec → Kirys | odst. 0,515 | odst. 0,515 | odst. 0,431 | odst. 0,431 | OK |
| `upadek` | 0,90 s (kl. 27,0) · Okucie dol → Kirys | odst. 0,505 | odst. 0,505 | odst. 0,173 | odst. 0,173 | OK |
| `wiwat` | 0,00 s (kl. 0,0) · Glowica → Kirys brzeg | ≥ 0,6 | ≥ 0,6 | odst. 0,597 | odst. 0,597 | OK |
| `skupienie` | 0,34 s (kl. 10,2) · Jelec koniec → Kaptur bok P | odst. 0,025 | odst. 0,025 | odst. 0,172 | odst. 0,172 | OK |
| spoczynek → akcja (0,12 s; wszystkie akcje) (6) | idle→umiejetnosc: 0,10 s przejścia · Glowica → Kirys | odst. 0,170 | odst. 0,170 | odst. 0,115 | odst. 0,115 | OK |
| akcja → spoczynek (0,15 s) (6) | atak→idle: 0,15 s przejścia · Jelec koniec → Kirys | odst. 0,513 | odst. 0,513 | odst. 0,430 | odst. 0,430 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,01 s przejścia · Jelec koniec → Kirys | odst. 0,502 | odst. 0,502 | odst. 0,421 | odst. 0,421 | OK |
| wskrzeszenie (przed: mieszanie 0,45 s; po: upadek wstecz + 0,15 s) (1) | upadek wstecz→idle (wskrzeszenie): 0,90 s przejścia · Okucie dol → Kirys | odst. 0,502 | odst. 0,505 | odst. 0,277 | odst. 0,173 | OK |
| spoczynek → radość (0,2 s) (1) | idle→wiwat: 0,01 s przejścia · Jelec koniec → Kirys | odst. 0,521 | odst. 0,521 | odst. 0,450 | odst. 0,450 | OK |

#### Mag (kostur; kapelusz liczony osobno)

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | kapelusz przed | kapelusz po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|---|---|
| `idle` | 1,00 s (kl. 30,0) · Okucie → Szata lamowka | odst. 0,146 | odst. 0,146 | odst. 0,071 | odst. 0,071 | odst. 0,024 | odst. 0,024 | OK |
| `chod` | 0,43 s (kl. 13,0) · Okucie → Szata rabek | odst. 0,192 | odst. 0,192 | odst. 0,083 | odst. 0,083 | odst. 0,008 | odst. 0,008 | OK |
| `czar` | 0,03 s (kl. 1,0) · Okucie → Szata lamowka | odst. 0,105 | odst. 0,105 | odst. 0,057 | odst. 0,057 | odst. 0,023 | odst. 0,023 | OK |
| `wiwat` | 0,00 s (kl. 0,0) · Odlamek → Ucho P 4 | odst. 0,045 | odst. 0,045 | odst. 0,049 | odst. 0,049 | odst. 0,121 | odst. 0,121 | OK |
| `atak` | 0,83 s (kl. 25,0) · Okucie → Szata lamowka | odst. 0,125 | odst. 0,182 | odst. 0,096 | odst. 0,096 | dotyk 0,025 | odst. 0,027 | OK |
| `kula_ognia` | 0,03 s (kl. 1,0) · Okucie → Szata lamowka | odst. 0,123 | odst. 0,179 | odst. 0,096 | odst. 0,096 | dotyk 0,077 | odst. 0,021 | OK |
| `lodowy_pocisk` | 0,02 s (kl. 0,5) · Okucie → Szata lamowka | odst. 0,195 | odst. 0,195 | odst. 0,096 | odst. 0,096 | odst. 0,016 | odst. 0,016 | OK |
| `bariera` | 1,37 s (kl. 41,0) · Okucie → Szata lamowka | odst. 0,107 | odst. 0,107 | odst. 0,096 | odst. 0,096 | odst. 0,031 | odst. 0,031 | OK |
| `unik` | 0,83 s (kl. 25,0) · Okucie → Szata lamowka | odst. 0,085 | odst. 0,085 | odst. 0,096 | odst. 0,096 | odst. 0,012 | odst. 0,012 | OK |
| `trafienie` | 0,63 s (kl. 19,0) · Okucie → Szata lamowka | odst. 0,194 | odst. 0,194 | odst. 0,088 | odst. 0,088 | odst. 0,021 | odst. 0,021 | OK |
| `upadek` | 0,02 s (kl. 0,5) · Okucie → Szata lamowka | **0,185** | odst. 0,207 | odst. 0,096 | odst. 0,096 | **0,136** | odst. 0,026 | OBLANY → **OK** |
| spoczynek → akcja (0,12 s; wszystkie akcje) (6) | idle→atak: 0,04 s przejścia · Okucie → Szata dzwon | odst. 0,120 | odst. 0,083 | odst. 0,074 | odst. 0,074 | dotyk 0,044 | dotyk 0,011 | OK |
| akcja → spoczynek (0,15 s) (6) | atak→idle: 0,15 s przejścia · Okucie → Szata lamowka | odst. 0,158 | odst. 0,158 | odst. 0,080 | odst. 0,080 | odst. 0,032 | odst. 0,032 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,04 s przejścia · Okucie → Szata lamowka | odst. 0,154 | odst. 0,154 | odst. 0,077 | odst. 0,077 | odst. 0,019 | odst. 0,019 | OK |
| wskrzeszenie (przed: mieszanie 0,45 s; po: upadek wstecz + 0,15 s) (1) | upadek wstecz→idle (wskrzeszenie): 0,02 s przejścia · Okucie → Szata lamowka | **0,209** | odst. 0,158 | odst. 0,084 | odst. 0,080 | **0,144** | odst. 0,026 | OBLANY → **OK** |
| spoczynek → radość (0,2 s) (1) | idle→wiwat: 0,01 s przejścia · Okucie → Szata lamowka | odst. 0,144 | odst. 0,144 | odst. 0,071 | odst. 0,071 | odst. 0,028 | odst. 0,028 | OK |

#### Muchomornik (laska) — przeciwnik

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|
| `idle` | 1,46 s (kl. 43,8) · Laska gora → Bokobrod P | dotyk 0,002 | dotyk 0,002 | odst. 0,085 | odst. 0,085 | OK |
| `ruch` | 0,18 s (kl. 5,3) · Sek 2 → Bokobrod P | odst. 0,058 | odst. 0,058 | odst. 0,099 | odst. 0,099 | OK |
| `atak` | 0,00 s (kl. 0,0) · Laska gora → Bokobrod P | odst. 0,026 | odst. 0,026 | odst. 0,028 | odst. 0,028 | OK |
| `umiejetnosc` | 0,00 s (kl. 0,0) · Laska gora → Bokobrod P | odst. 0,026 | odst. 0,026 | odst. 0,028 | odst. 0,028 | OK |
| `trafienie` | 0,00 s (kl. 0,0) · Laska gora → Bokobrod P | odst. 0,026 | odst. 0,026 | odst. 0,028 | odst. 0,028 | OK |
| `unik` | 0,00 s (kl. 0,0) · Laska gora → Bokobrod P | odst. 0,026 | odst. 0,026 | odst. 0,028 | odst. 0,028 | OK |
| `upadek` | 1,13 s (kl. 34,0) · Laska dol → Pas | odst. 0,026 | odst. 0,026 | dotyk 0,015 | dotyk 0,015 | OK |
| `wiwat` | 0,27 s (kl. 8,0) · Laska dol → Pas | odst. 0,173 | odst. 0,173 | odst. 0,131 | odst. 0,131 | OK |
| spoczynek → akcja (0,12 s; wszystkie akcje) (4) | idle→umiejetnosc: 0,01 s przejścia · Laska gora → Bokobrod P | odst. 0,000 | odst. 0,000 | odst. 0,076 | odst. 0,076 | OK |
| akcja → spoczynek (0,15 s) (4) | atak→idle: 0,01 s przejścia · Laska gora → Bokobrod P | odst. 0,029 | odst. 0,029 | odst. 0,031 | odst. 0,031 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,01 s przejścia · Laska gora → Bokobrod P | odst. 0,001 | odst. 0,001 | odst. 0,029 | odst. 0,029 | OK |
| spoczynek → radość (0,2 s) (1) | idle→wiwat: 0,01 s przejścia · Laska gora → Bokobrod P | odst. 0,041 | odst. 0,041 | odst. 0,125 | odst. 0,125 | OK |

#### Leśny Troll (maczuga) — przeciwnik

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|
| `idle` | 1,80 s (kl. 54,0) · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,289 | odst. 0,289 | OK |
| `ruch` | 1,39 s (kl. 41,8) | ≥ 0,6 | ≥ 0,6 | ≥ 0,6 | ≥ 0,6 | OK |
| `atak` | 0,06 s (kl. 1,8) · Przelom → Lisc bok P 1 2 | ≥ 0,6 | ≥ 0,6 | odst. 0,320 | odst. 0,320 | OK |
| `umiejetnosc` | 0,00 s (kl. 0,0) · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,342 | odst. 0,342 | OK |
| `trafienie` | 0,00 s (kl. 0,0) · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,342 | odst. 0,342 | OK |
| `unik` | 0,00 s (kl. 0,0) · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,342 | odst. 0,342 | OK |
| `upadek` | 0,00 s (kl. 0,0) · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,342 | odst. 0,342 | OK |
| `ryk` | 0,00 s (kl. 0,0) | ≥ 0,6 | ≥ 0,6 | ≥ 0,6 | ≥ 0,6 | OK |
| spoczynek → akcja (0,12 s; wszystkie akcje) (4) | idle→atak: 0,06 s przejścia · Przelom → Lisc bok P 1 6 | ≥ 0,6 | ≥ 0,6 | odst. 0,268 | odst. 0,268 | OK |
| akcja → spoczynek (0,15 s) (4) | atak→idle: 0,01 s przejścia · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,342 | odst. 0,342 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,01 s przejścia · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,296 | odst. 0,296 | OK |
| spoczynek → radość (0,2 s) (1) | idle→ryk: 0,01 s przejścia · Przelom → Biodra | ≥ 0,6 | ≥ 0,6 | odst. 0,500 | odst. 0,500 | OK |

#### Bulgotnik (kij) — przeciwnik Bagna, nowy (bez kolumny „przed”)

| Klip / przejście | Najgorsza chwila (po) · bryła broni → bryła ciała | głowa przed | głowa po | tułów przed | tułów po | Wynik |
|---|---|---|---|---|---|---|
| `idle` | 1,80 s (kl. 54,0) · Kij 0 → Kopiec 1 | — | odst. 0,179 | — | odst. 0,022 | OK |
| `ruch` | 0,33 s (kl. 10,0) · Kij 0 → Kopiec 1 | — | dotyk 0,018 | — | dotyk 0,045 | OK |
| `atak` | 0,90 s (kl. 27,0) · Kij 0 → Kopiec 1 | — | odst. 0,111 | — | dotyk 0,071 | OK |
| `umiejetnosc` | 1,70 s (kl. 51,0) · Kij 0 → Gruda 1 | — | odst. 0,111 | — | dotyk 0,074 | OK |
| `trafienie` | 0,30 s (kl. 9,0) · Kij 0 → Kopiec 1 | — | odst. 0,111 | — | dotyk 0,071 | OK |
| `unik` | 0,83 s (kl. 25,0) · Kij 0 → Kopiec 1 | — | odst. 0,043 | — | dotyk 0,071 | OK |
| `upadek` | 0,00 s (kl. 0,0) · Kij 0 → Kopiec 1 | — | odst. 0,111 | — | dotyk 0,071 | OK |
| `wiwat` | 0,83 s (kl. 25,0) · Kij 0 → Kopiec 2 | — | odst. 0,413 | — | dotyk 0,053 | OK |
| spoczynek → akcja (0,12 s; wszystkie akcje) (4) | idle→unik: 0,10 s przejścia · Kij 0 → Kopiec 1 | — | odst. 0,119 | — | dotyk 0,052 | OK |
| akcja → spoczynek (0,15 s) (4) | atak→idle: 0,01 s przejścia · Kij 0 → Kopiec 1 | — | odst. 0,116 | — | dotyk 0,068 | OK |
| spoczynek / trafienie → upadek (0,08 s) (1) | →upadek: 0,01 s przejścia · Kij 0 → Kopiec 1 | — | odst. 0,111 | — | dotyk 0,071 | OK |
| spoczynek → radość (0,2 s) (1) | idle→wiwat: 0,01 s przejścia · Kij 0 → Kopiec 1 | — | odst. 0,210 | — | odst. 0,025 | OK |

## Klipy i przejścia oblane przed poprawkami

| Aktor | Klip / przejście | Najgorsza chwila | Głębokość | Ile trwa | Co widać | Teraz |
|---|---|---|---|---|---|---|
| Mag | `upadek` (klip) | 0,783 s = połowa klatki 23→24 | głowa **0,185**, tułów **0,136** | < 1/60 s | kostur przelatuje przez twarz w jednej klatce ekranu (łapa obraca się w klipie o 176° między kl. 23 i 24, a kostur na kości StaffPivot kompensuje to o 167° — gra interpoluje obie kości osobno) | głowa odst. 0,207, tułów odst. 0,026 |
| Wojownik | wskrzeszenie | 0,242 s przejścia 0,45 s | tułów **0,171** | ok. 0,10 s | jelec miecza wchodzi w biodra, gdy leżący „wstaje” | głowa odst. 0,134, tułów odst. 0,155 |
| Mag | wskrzeszenie | 0,275 s przejścia 0,45 s | głowa **0,209**, tułów **0,144** | ok. 0,19 s | kostur z ziemi wraca do łapy w linii prostej w układzie łapy i przechodzi przez głowę | głowa odst. 0,158, kapelusz odst. 0,080, tułów odst. 0,026 |

Podgląd przed / po: `podglad/mag_upadek_przed_po.png`, `podglad/wojownik_wskrzeszenie.png`,
`podglad/mag_wskrzeszenie.png` (rzuty brył; czerwone kółko = bryła broni najgłębiej w ciele).

## Poprawione — klipy (`swiat/postacie/kot_mag.py`)

Dane gry przeliczone generatorem `aktorzy.py --tylko mag` (Blender w tle, `-t 2`). W `dane/mag.json` zmieniły się
tylko klipy `upadek`, `atak`, `kula_ognia`, `lodowy_pocisk`; chwile (`CHWILE` modułu i `chwile` w danych), części,
kości i obwiednia leżenia bez zmian. Kontrola własna modułu (`kontrola`, klatki całkowite, wszystkie stroje) przed
i po dla tych czterech klipów: bez przenikania, rękaw i najniższy punkt bez zmian.

1. **`upadek`** (l. 1206–1215, poza kluczowa „leci”, kl. 27): prawa łapka w locie `RightHand = (30, −15, 90)` zamiast
   `(0, 0, 0)` — osie łapy przechodzą płynnie z pozy „ugina” do leżenia, łapa nie obraca się już o 176° w jednej
   klatce i kostur wylatuje z łapy łukiem z dala od twarzy. Głowa 0,185 → odstęp 0,207, tułów 0,136 → odstęp 0,026;
   w świecie zmienione tylko klatki 21–32 (łapka i początek lotu kostura), od kl. 33 bez zmian.
2. **`atak`, `kula_ognia`, `lodowy_pocisk`** (część 2; l. 891–896 stała `DOL` z opisem, l. 1004, 1008, 1045, 1049,
   1075, 1081): w pozach z kosturem wyciągniętym do przodu (błysk i dobicie ataku, rzut i dobicie kuli ognia,
   cofnięcie i pchnięcie lodowego pocisku) przód kryształu w dół (`przod=DOL`) zamiast w górę — pozy sąsiednie mają
   przód kryształu do przodu przy kosturze w górze, a przeniesiony z nimi obrót drzewca daje właśnie „w dół”, więc
   wejście i wyjście z pozy ataku nie wymaga już skrętu ok. 175°, który mieszanie osi w `_sekwencja` robiło
   w jednej klatce. Policzone (skręt kostura wokół osi na klatkę): `atak` 156° (kl. 16→17) → 6°, `kula_ognia` 150°
   (kl. 36→37; też 24→25) → 6°, `lodowy_pocisk` 84° (kl. 5→6 i 6→7) → 4°. Oś drzewca w pozach kluczowych i chwile
   wypuszczenia bez zmian; punkt wylotu pocisku (`Pocisk`, 0,08 studa obok osi) w chwili wypuszczenia przesuwa się
   o 0,16 studa (kryształ obrócony o 180° wokół drzewca) — test aktorów (kryształ ≤ 0,35 od punktu, punkt przed
   aktorem na wysokości 1–4) przechodzi. Przenikanie tych klipów bez zmian (głowa najbliżej 0,12, tułów dotyk szaty
   ≤ 0,077). Podgląd: `podglad/mag_kostur_skret_przed_po.png` (kryształ w kl. 16 → 16,5 → 17: przed — odłamki
   skaczą, po — stoją).

## Poprawione — odtwarzacz (część 2, `swiat/test_walki2/zrodla/`)

1. **Wskrzeszenie bez przenikania** (`OdtwarzaczWalki2.luau`, `Obsluga.wskrzeszenie`, l. 1909–1930;
   `Choreografie.luau`, `Ch.WSKRZESZENIE`, l. 172–175). Wstawanie = klip upadku odegrany **wstecz** od bieżącej
   chwili do klatki 0 (od `wstaje` do nowego `stoi = 0.78` ułamka zdarzenia; przy 1,5 s zdarzenia 0,33 → 1,17 s, czyli
   0,84 s — tyle co szybki upadek przy powaleniu), potem 0,15 s do spoczynku. Pozy są te same co przy padaniu, więc
   kostur wraca do łapy po swoim torze. Bez klipu upadku, gdy upadek nie jest bieżącym klipem, albo po pominięciu —
   jak dawniej (przejście 0,45 s). **Czas zdarzenia się nie zmienia** (trwanie z dziennika; światło, pasek życia
   0,38, napis 0,3 i uniesienie do 0,92 trwania bez zmian) — zmienia się tylko to, co aktor robi w środku zdarzenia,
   więc plan walki i testy czasu nie mają czego się rozjechać (`test_odtwarzacza.py` 18/18; próba v3 sprawdza pasek,
   światło i napis, nie pozy). Jedyna nowa liczba czasu jest w jednym miejscu: `Ch.WSKRZESZENIE.stoi`.
   Policzone: Wojownik tułów 0,171 → odstęp 0,155; Mag głowa 0,209 → odstęp 0,158, tułów 0,144 → odstęp 0,026.
2. **Obrót zwycięzcy przed radością** (`OdtwarzaczWalki2.luau`: stała `OBROT_ZWYCIEZCY = { przed = 0.45, czas = 0.45 }`
   l. 1111–1116; `Sesja:aktualizujPozy` l. 2129–2132; `Sesja:krokSceny` l. 3048–3064; `Sesja:rozpocznij` l. 2947;
   `Sesja:pomin` l. 3346). Po ciosie kończącym obrót do kamery objazdu zaczyna się 0,45 s przed `tRadosc` (końcówka
   ujęcia pokonanego), a kąt objazdu (`przygotujObjazd`) jest liczony w tej chwili raz — przy cięciu do objazdu
   zwycięzca stoi już twarzą do kamery (kąt twarzy 35° i maleje). Bez ciosu kończącego — jak dawniej (obrót razem
   z radością). Po POMIŃ bez zmian (zwycięzca od razu obrócony). Czas finału (`tRadosc`, `tObjazdu`, `czasKonca`) bez
   zmian.

## Kamera — czy broń zasłania twarz

Kamera finału z `Sesja:ujecieSurowe` („objazd”) i `Sesja:przygotujObjazd`: kamera R = 1,25·wzrost + 6,5 od
zwycięzcy, na wysokości 0,55·wzrost + 1,6; kąt objazdu `max(62 − 22·wyjscie(τ/2,6), kąt_min)`, obrót zwycięzcy
`(kąt_startu − 35)·gladko((τ + przed)/czas)` z `OBROT_ZWYCIEZCY` (narzędzie czyta je z kodu; `kamera.przebieg_finalu`).
Kąt startu 62° (zwykle) oraz 90, 120, 150° (duży leżący pokonany wypycha kamerę dalej); kamera z prawej (gracz stoi
po lewej) i z lewej (przeciwnik-lustro). Radość wchodzi ze spoczynku przez 0,2 s — kąt i poza w tej samej chwili.
Ujęcia z ukosa w walce („naSiebie” ok. 63°, „efekt” ok. 66°, „zbliżenie” ok. 70° od twarzy) — 40–70° jako
informacja. Miara: promienie z kamery przez siatkę 80 × 80 na tarczy głowy; zasłonięty piksel = broń trafiona bliżej
niż głowa (ręka czy rękaw się nie liczą). Próg: oczy (oba razem) ≤ 25%, rysy twarzy (oczy, brwi, nos, usta,
rumieńce, wąsy) ≤ 35%; oczy liczą się, gdy widać ich ≥ 12 pikseli.

| Klasa | Początek finału (τ 0–0,6 s od radości): przed → po | Radość, kąt ≤ 35° | Postawa, kąt ≤ 35° | Z ukosa 40–70° (informacja, bez zmian) |
|---|---|---|---|---|
| Wojownik | oczy **100%**, rysy **97%** (τ 0,03 s, 61°: jeszcze w spoczynku, miecz przed twarzą) → oczy 0%, rysy 4% (35°, τ 0,07 s) | 0% / 0% | 0% / 0% | spoczynek: oczy **86%**, rysy **74%** (+60°, z prawej); radość 0% |
| Zwiadowca | oczy **60–77%**, rysy **49–70%** (τ 0,07–0,27 s, 59–77°: sztylet unoszony w radości) → 0% / 0% | 0% / 0% | 0% / 0% | radość: oczy 92%, rysy 77% (+65°, kl. 6 — w grze już nie występuje: przy 65° zwycięzca jest jeszcze w ujęciu pokonanego); spoczynek: oczy 6%, rysy 21% |
| Mag | 0% / 0% → 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |

Ocena na oko (podgląd `podglad/final_obrot_do_kamery.png`, przed i po w chwilach 0; 0,1; 0,2; 0,3 s objazdu):
po zmianie twarz Wojownika i Zwiadowcy jest odsłonięta od pierwszej klatki objazdu. Inne podglądy:
`podglad/radosc_kamera_finalu.png` (radość z przodu, trzy klasy), `podglad/wojownik_spoczynek_kamera.png`
(spoczynek 0°, 30°, 50°, 70° z prawej).

**Nie zmieniane — do decyzji ludzi:** miecz Wojownika w spoczynku z ukosa (ujęcia „efekt” i „zbliżenie” na gracza,
ok. 60–70° od twarzy, z prawej) zasłania prawe oko — oczy 86%, rysy 74% (kl. 54 spoczynku, +60°). To poza spoczynku
(miecz w gotowości przed ciałem), z której startują i na której kończą się wszystkie klipy Wojownika; zmiana
wymagałaby przebudowy wszystkich jego klipów.

## Uwagi poboczne (policzone, bez przenikania — nie poprawiane)

- **Mag: lewa łapka (bez broni) obraca się o 113–166° w jednej klatce** (`atak` kl. 6→7 i 16→17; tamże ramię
  lewe 69–166°), a w `lodowy_pocisk` prawe ramię i dłoń o 79–89° w kl. 18→20 — ta sama przyczyna co przy kosturze
  (mieszanie osi łapy w `_sekwencja`), ale bez broni, więc poza tym zadaniem; kostur w tych klatkach skręca się
  najwyżej o 6°. Do ewentualnej osobnej poprawki.
- Muchomornik: laska muska bokobrody w spoczynku (0,002 studa, poniżej progu); Troll: maczuga zawsze ≥ 0,6 od głowy.
- Strój Wojownika „bojowy” (z tarczą) — tarcza nigdy nie dochodzi do głowy (najbliżej: jelec miecza przy boku hełmu
  0,10–0,14 studa).
- Wstawanie wstecz u Maga: pierwsze ok. 0,4 s z 0,84 s to jeszcze klatki leżenia (kl. 60 → 33), samo podnoszenie
  ok. 0,45 s — do obejrzenia w Play, czy tempo się podoba (liczba w jednym miejscu: `Ch.WSKRZESZENIE.stoi`).

## Nowi aktorzy (Bagno)

Tabela aktorów walki ma pięciu przeciwników Bagna (`aktorzy_bagna.py`, praca innego agenta). Broń w ręku rozpoznana
po nazwie ma tylko **Bulgotnik** (kość `Kij` na prawym ramieniu; głowa `Glowa`, tułów `Cialo` — wykryte z nazw).
Test wykrył go sam: na danych z 17.11 13:29 oblewał — kij w ciele w `atak` 0,246, `unik` 0,175, `upadek` 0,349
(i głowa 0,042, kij w kołnierzu). Agent Bagna poprawił kij w swoich klipach; **na bieżących danych Bulgotnik
przechodzi bez wyjątków**: tułów najwyżej dotyk 0,074 (`umiejetnosc`; `atak`, `trafienie`, `unik`, `upadek` 0,071),
głowa bez przenikania (najbliżej dotyk 0,018 w `ruch`, poniżej progu 0,02), skręt kija ≤ 3°/klatkę (tabela wyżej).
Podglądy `podglad/bulgotnik_*.png` pokazują stan z 13:29 (przed jego poprawką).

## Ocena w grze (część 3, Studio, 17.11.2026 ok. 16:00)

Zmiany z części 1–2 są w Studio od 14:50. Zrzuty z trybu Play (klon aktora przez prawdziwy moduł `Klipy` albo walka
w trybie ręcznym, czas sceny przewijany co 0,1 s przez `Sygnaly/Sterowanie „przewinDo”`), zestawione z rzutami brył
„przed”. Arkusze dla ludzi: `podglad/gra_*.jpg` (podpisy przy każdym wierszu i klatce).

| Arkusz | Co pokazuje | Ocena (na oko, z zrzutów) |
|---|---|---|
| `gra_mag_upadek.jpg` | upadek Maga kl. 22–25 co pół klatki (przód 3/4); u góry rzut brył sprzed poprawki | **dobrze** — w grze kostur idzie łukiem w górę i za głowę, potem przed kota na ziemię (kl. 21–32 w zrzutach roboczych z boku i z przodu); w kl. 23,5 (dawny błąd) nic nie przechodzi przez twarz |
| `gra_mag_kostur.jpg` | kryształ kostura przed / po (zbliżenie z rzutu brył) i w grze: atak kl. 16–17, kula ognia kl. 36–37, lodowy pocisk kl. 5–7 co pół klatki | **dobrze** — ruch kostura płynny, w grze nie widać przeskoku; kryształ w zrzutach z gry jest mały (cała postać w kadrze), więc mignięcie oceniam głównie z liczb (6°/klatkę) i ze zbliżenia z rzutu brył |
| `gra_wskrzeszenie.jpg` | Wojownik i Mag: rzut brył „przed” (mieszanie), w grze co 0,2 s ze słupem światła i — tylko do oceny ruchu — ze słupem schowanym lokalnie w sesji Play | **dobrze, liczby bez zmian** — leży ok. 0,45 s (w tym 0,33 s przed `wstaje`), wstaje w ok. 0,4–0,45 s (Mag 14,1 → 14,5 s, Wojownik 15,9 → 16,3 s), broń wraca do ręki przed ciałem; czyta się jak „przewinięcie” upadku, co pasuje do magicznego wskrzeszenia. Ze słupem światła samo wstawanie jest prawie całe zasłonięte — widać lot kostura / miecza do ręki i stojącą postać od ok. 1,25 s zdarzenia. `Ch.WSKRZESZENIE.stoi = 0.78` zostaje |
| `gra_final.jpg` | od ostatniej klatki ujęcia pokonanego do ok. 0,7 s objazdu: Wojownik i Zwiadowca z wilkiem, Wojownik z Trollem (duży pokonany); u góry rzut brył „przed” | **dobrze** — w pierwszej klatce objazdu twarz odsłonięta u obu (miecz uniesiony obok głowy, sztylet z boku); w ujęciu pokonanego zwycięzcy nie ma w kadrze (wilk, Troll), więc obrotu nie widać i nie wygląda dziwnie |

Czego nie oceniłem: obrót zwycięzcy w ujęciu pokonanego przy innych parach (Strażnik Gaju, Slime, lustro) — w
sprawdzonych trzech zwycięzca jest poza kadrem; finał Maga (liczby: 0% zasłonięcia); wskrzeszenie przeciwnika-lustra
(ta sama obsługa, kamera z drugiej strony). Zrzuty robocze (klatki 21–32 upadku z boku i z przodu, pełne serie
walk) nie są w repozytorium — w arkuszach jest wybór.

Naprawione przy okazji (narzędzie prób, nie gra): `swiat/test_walki2/testy/klatki_aktorow.py` dawał w każdej klatce
salę wyboru klasy — ekran wyboru klasy (Pawła, bez zmian) przyjmuje Enter tylko przy włączonym swoim GUI, a narzędzie
najpierw chowało cały interfejs. Teraz najpierw Enter (jak `sesja_play.py`), potem chowanie interfejsu, a kamera
narzędzia jest trzymana w każdej klatce po kamerze ekranu wyboru; nowe opcje `--klipy klip@od-do/krok`, `--oba`,
`--bez-spoczynku`.

## Testy (bez Studio, pojedynczo, na bieżącym drzewie)

- `python -B swiat/test_walki2/testy/test_przenikania.py` — **12/12 OK** (ok. 2,5 min): lustro = `geometria.py`
  u 13 aktorów, mieszanie torów jak w `Klipy.luau`, liczby ze Studio, kształty z `KSZTALTY.md`, zepsuty klip wykryty
  (miecz w hełmie), znani aktorzy z bronią mierzeni, **brak przenikania we wszystkich klipach i przejściach**
  (`ZNANE` puste), skręt broni ≤ 70°/klatkę, model przejść czytany z kodu odtwarzacza, twarz niezasłonięta
  z przodu i przy cięciu do objazdu (trzy klasy). Ten sam test na dawnych danych Maga oblewa (`upadek`: głowa 0,185).
- `python -B swiat/test_walki2/testy/test_aktorow.py` — **15/15 OK**.
- `python -B swiat/test_walki2/testy/test_odtwarzacza.py` — **18/18 OK** (4644 dzienniki, 10/10 typów, 14/14
  umiejętności, 9/9 efektów, 77 726 tur ze stanem silnika, wskrzeszenia: gracz 330, przeciwnik 82, obu 59).
- `python -B swiat/test_walki2/zbuduj.py --sucho` — kod 0; `swiat/las_potwory/sprawdz_luau.py` na zmienionych
  plikach Luau — OK.

## Wdrożenie w Studio i próby w Play

Zmieniły się: dane Maga (`dane/mag.json`) i dwa moduły (`OdtwarzaczWalki2`, `Choreografie`). Studio w trybie Edit:

```
python -B swiat/test_walki2/zbuduj.py --sucho
python -B tools/studio_mcp.py studios
python -B swiat/test_walki2/zbuduj.py --tylko-aktorzy mag --studio <id>
python -B swiat/test_walki2/zbuduj.py --skrypty --studio <id>
python -B swiat/test_walki2/testy/sprawdz_edit.py --studio <id>
```

Las-pas i stary las biorą odtwarzacz, moduły i aktorów z `TestWalki2` — ich nie trzeba przebudowywać. Próby w Play:
1. `testy/test_klipow_play.py` — klon Maga gra spoczynek, ma punkty Bron / Pocisk / Piers.
2. `testy/klatki_aktorow.py --tylko mag --wszystkie` i to samo z `--przod` — **na co patrzeć:** `upadek` kl. 21–32:
   łapka bez obrotu, kostur wylatuje łukiem z dala od twarzy, ląduje jak dotąd; `atak`, `kula_ognia`,
   `lodowy_pocisk`: kryształ i odłamki nie przeskakują między klatkami (dawniej kl. 16→17, 24→25, 36→37, 5→7).
3. `testy/test_v3_play.py` — części wskrzeszenia (gracz, przeciwnik-lustro, obu) z Magiem i Wojownikiem. **Na zrzutach
   wskrzeszenia:** leżący wstaje „cofając” upadek (najpierw chwilę leży, potem podnosi się tym samym ruchem, którym
   padł), kostur Maga wraca do łapy po łuku i ani przez chwilę nie przechodzi przez głowę, jelec miecza Wojownika
   nie wchodzi w biodra; po ok. 0,85 s od światła stoi, dalej spoczynek; pasek życia, napis „WSKRZESZENIE!” i
   światło jak dotąd.
4. `testy/test_dopieszczenia_play.py` część `final` — kąt twarzy zwycięzcy od 0,5 s radości (teraz ok. 27°, próg
   60°), szczątki w ujęciu. **Na zrzutach finału:** w końcówce ujęcia pokonanego zwycięzca obraca się w stronę
   kamery (ok. 0,45 s); w pierwszej klatce objazdu twarz Wojownika i Zwiadowcy jest odsłonięta (miecz / sztylet
   nie przed oczami), radość zaczyna się już przodem; panel wyniku jak dotąd. Sprawdzić też, czy obrót w ujęciu
   pokonanego nie przeszkadza (zwycięzca bywa w jego kadrze).
5. `testy/test_walki_play.py --szybko` i `testy/test_poprawek_play.py` — regresja całości (w tym POMIŃ: zwycięzca
   od razu obrócony).

Pliki Blendera Maga (FBX, filmy w `swiat/postacie/wynik/kot_mag/`) dostaną poprawione klipy przy następnym
`swiat/postacie/przebuduj.py kot_mag` (nie przebudowywałem — ciężka praca na wspólnym modelu).

## Pliki

| Plik | Co robi / co zmienione |
|---|---|
| `swiat/postacie/przenikanie/przenikanie.py` | wiersz poleceń: pomiar, tabela, `--md`, `--kamera`, `--podglad`, `--json`, `--dane` |
| `swiat/postacie/przenikanie/pozy.py` | lustro `Klipy.luau` + stawy Motor6D (numpy), Lerp i mieszanie torów |
| `swiat/postacie/przenikanie/bryly.py` | kształty Roblox: odległość ze znakiem, punkty próbne, promienie, głębokość w sumie brył |
| `swiat/postacie/przenikanie/pomiar.py` | strefy, broń aktorów, progi, scenariusze, model wskrzeszenia z kodu gry, skręt broni |
| `swiat/postacie/przenikanie/kamera.py` | zasłonięcie twarzy z kamery finału (obrót zwycięzcy z kodu gry), obrazy PNG |
| `swiat/postacie/przenikanie/podglad/*.png` | podglądy wyżej (rzuty brył) |
| `swiat/postacie/przenikanie/podglad/gra_*.jpg` | część 3: „przed” (rzuty brył) i „w grze po” (zrzuty z Play) — upadek, kostur, wskrzeszenie, finał |
| `swiat/test_walki2/testy/klatki_aktorow.py` | część 3: działa przy ekranie wyboru klasy; `--klipy`, `--oba`, `--bez-spoczynku` |
| `swiat/test_walki2/testy/test_przenikania.py` | test na stałe (12 testów) |
| `swiat/postacie/kot_mag.py` | `DOL` + 6 × `przod=DOL` (atak, kula_ognia, lodowy_pocisk), łapka w `upadek` |
| `swiat/test_walki2/dane/mag.json` | przeliczone generatorem (`aktorzy.py --tylko mag`) |
| `swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau` | `OBROT_ZWYCIEZCY`, obrót przed radością, wskrzeszenie wstecz |
| `swiat/test_walki2/zrodla/Choreografie.luau` | `Ch.WSKRZESZENIE.stoi = 0.78` |
| `swiat/test_walki2/README.md` | opis wskrzeszenia, obrotu w finale, ryzyka, wiersz testu w „Pliki” |

Dlaczego narzędzie jest w `swiat/postacie/`, a nie obok pakietu walki: liczy dowolny rig z
`swiat/postacie/biblioteka/roblox_klocki.rig()` (aktorów walki i każdą postać z klocków), a z pakietu walki bierze
tylko dane, lustro `geometria.py` (do porównania) i kod odtwarzacza (model przejść); test pakietu walki woła je
z `testy/`.
