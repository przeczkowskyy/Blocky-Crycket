# Walka v2 — prototyp w Roblox Studio (aktorzy, serwer, odtwarzacz, interfejs, poprawki po przeglądzie)

> **Status: prototyp, nie kanon i nie kod gry.** Działa wyłącznie w Roblox Studio (każdy skrypt i moduł zaczyna się
> od strażnika `RunService:IsStudio()`; poza Studio serwer usuwa cały kontener przy starcie — patrz „Bezpieczeństwo”).
> **Przed publikacją miejsca:** `python -B swiat/test_walki2/zbuduj.py --usun` i zapis miejsca.
>
> Cel całej paczki (prośba właściciela z 14.11): nowe zasady walki (silnik v2) i nowe modele widoczne jako walki na
> ekranie. Gracz podchodzi do tablicy, wybiera klasę, przeciwnika i poziom, i ogląda walkę policzoną przez silnik v2.
> Wzór i punkt odniesienia: prototyp v1 w `swiat/test_walki_roblox/` (zostaje bez zmian, obok).

**Etap 1** zrobił kontener z leśną areną, ośmiu aktorów z własnymi klipami z danych i porównanie obrysu.
**Etap 2** dodał: serwer (wybór z zamkniętej listy → postać wzorcowa → `Silnik.symuluj` → dziennik),
odtwarzacz całego dziennika v2 z choreografią każdej umiejętności, efektami na postaciach, kamerą i finałem,
interfejs walki i panel wyboru przy tablicy, testy bez Studio i w trybie Play, arkusze klatek i pomiary.
**Etap 3** to niezależny przegląd (8 uwag). **Etap 4** (15.11) je poprawił — patrz „Poprawki po przeglądzie”.

## Jak obejrzeć (krok po kroku)

1. Studio, miejsce gry (Team Create). W `Workspace` jest folder **`TestWalki2`** (atrybut `Wygenerowane = true`).
   Jeśli go nie ma — odbuduj (niżej).
2. Naciśnij **Play** (F5). Ze spawnu idź **na południe** — zobaczysz zielony świecący słup i tablicę „WALKA v2”
   (ok. 220 studów; tablica stoi w `(16, 0, 220)`).
3. Podejdź do tablicy: podpowiedź „Walka v2 (prototyp) · Wybierz walkę”. Naciśnij **E** (telefon: dotknij).
4. Panel wyboru: **klasa** (Wojownik / Zwiadowca / Mag), **przeciwnik** (Leśny Slime, Cierniowy Wilk, Muchomornik —
   zwykli; Leśny Troll — rzadki; Strażnik Lasu — strażnik; „model zastępczy” przy Slime'ie i Strażniku), **poziom**
   (1 / 5 / 10 — obu stron) i **WALCZ!**. Panel zamyka krzyżyk albo odejście od tablicy. Gdy serwer odmówi walki
   (np. za daleko od tablicy), gracz dostaje komunikat z powodem: przy tablicy w panelu, dalej w dymku na ekranie.
5. Walka: paski życia z nazwą, poziomem i rangą, ikony efektów z licznikiem tur, licznik tury, wstęga z nazwą
   umiejętności. Na dole **×1 / ×2 / ×4** (tempo, wybór gracza) i **POMIŃ** (albo spacja). Na końcu panel wyniku
   z łupem z dziennika i przyciskami **JESZCZE RAZ** (ten sam wybór, nowe ziarno) i **ZAMKNIJ**.
6. Zatrzymaj Play (Shift+F5).

Do powtarzalnego pokazu: w trybie Play w oknie **Server** ustaw atrybut `ZiarnoTestowe` folderu `Workspace.TestWalki2`
(ziarna niżej, „Ziarna pokazowe”) i wybierz w panelu tę samą klasę, przeciwnika i poziom.
Najszybciej bez Studio: arkusze klatek `klatki/walka_*.jpg` (opis niżej).

## Ziarna pokazowe (`testy/ziarna.json`, liczy `testy/test_odtwarzacza.py --ziarna`)

| Pokaz | Wybór (klasa / przeciwnik / poziom) | Ziarno | Wynik, tury, czas dziennika |
|---|---|---|---|
| długa walka (> 20 tur), wygrana | wojownik / straznik_lasu / 10 | 348759 | wygrana, 24 tury, 33 zdarzenia, 39,1 s |
| najdłuższa znaleziona | zwiadowca / straznik_lasu / 1 | 158424 | przegrana, 33 tury, 47,7 s |
| krótka walka | mag / muchomornik / 5 | 823742 | przegrana, 3 tury, 7,3 s |
| wygrana z Shardem Ewolucji | zwiadowca / straznik_lasu / 10 | 325002 | wygrana, 13 tur (łup: 554 złota, 503 dośw., 5 tokenów, 1 Shard) |
| wygrana z Gemem | mag / cierniowy_wilk / 1 | 617727 | wygrana, 5 tur |
| wszystkie rodzaje zdarzeń — Zwiadowca | zwiadowca / lesny_troll / 10 | 950601 | 11 tur: cios, krytyk, unik, umiejętność, tyknięcie, nałożenie, koniec, utrata tury |
| wszystkie rodzaje zdarzeń — Mag | mag / cierniowy_wilk / 5 | 910854 | 9 tur, 8 rodzajów (bloku Mag nie widzi: blokuje tylko tarcza Wojownika) |
| prawie wszystkie — Wojownik | wojownik / cierniowy_wilk / 5 | 277334 | 10 tur, 8 rodzajów; brak tyknięcia — w 1800 walkach Wojownika nie trafiła się walka ze wszystkimi 9 naraz |

Dla każdej umiejętności jest też walka, w której ona trafia (`ziarna.json` → `umiejetnosci`), np. kula ognia:
mag / cierniowy_wilk / 1, ziarno 47559; uścisk korzeni: wojownik / straznik_lasu / 5, ziarno 689121.

## Jak to działa

**Serwer** (`zrodla/SerwerWalki2.server.luau`) — jedyny punkt styku z klientem: `Zdalne/RozpocznijWalke2`.
Klient wysyła tylko `{ klasa, przeciwnik, poziom }` jako **napisy** z zamkniętej listy (poziom to `"1" | "5" | "10"`,
nie liczba). Serwer sprawdza je ze swoją listą (klasy z `Wzorcowe`, przeciwnicy z kopii `Dane`), sam buduje postać
wzorcową (`zrodla/Wzorcowe.luau` = `tools/walka/wzorcowe.py`) i przeciwnika, losuje ziarno, woła `Silnik.symuluj`
i odsyła dziennik. Zabezpieczenia jak w v1: limit 1 prośby na sekundę, odległość od tablicy (≤ 20 studów), **sesja
walki** = pełny czas dziennika przy ×1 (tempo ×2/×4 i POMIŃ skracają tylko odtwarzanie; „JESZCZE RAZ” odlicza do jej
końca), łup wyłącznie w odpowiedzi z walką. Złe wybory → `zly_wybor`; dodatkowe pola i argumenty są pomijane.

**Odtwarzacz** (`zrodla/OdtwarzaczWalki2.luau`) odtwarza **cały** dziennik: każde zdarzenie startuje w swoim `t`
i trwa swoje `trwa` (D-068 — nic nie jest skracane ani ściskane). Czas sceny τ biegnie z tempem gracza i **zwalnia**
przy krytyku (0,7 s sceny w tempie 0,22, jak w v1) i przy ciosie kończącym walkę. Klipy aktorów, ruch, pociski i efekty
liczą się w czasie sceny, więc tempo i zwolnienie działają na wszystko naraz. Obsługa zdarzeń:

| Typ zdarzenia | Co widać |
|---|---|
| `cios` / `krytyk` / `blok` / `unik` | doskok (z zasięgu broni w chwili trafienia i głębokości piersi celu), klip ataku dopasowany prędkością tak, by trafienie wypadło w chwili z dziennika; odrzut, klip trafienia, iskry, liczba; krytyk: zwolnienie, „wjazd” kamery, gwiazda „KRYTYK!”; blok: klip bloku Wojownika z tarczą, niebieskie iskry; unik: klip uniku i ślizg w bok, pocisk mija cel |
| `umiejetnosc` | wstęga z nazwą (z danych silnika) i choreografia stylu z `Choreografie.luau` (tabela niżej) |
| `efekt_nalozony` | napis = nazwa efektu z danych silnika („SPOWOLNIENIE!”, „ZDARTY PANCERZ!”), ikona z licznikiem tur pod paskiem, ozdoba na postaci do końca efektu; tarcza: zapas na pasku |
| `efekt_tick` | liczba w kolorze efektu, puls ozdoby, drgnięcie; tarcza pochłaniająca: „TARCZA −n” |
| `efekt_koniec` | znika ikona i ozdoba; pęknięta tarcza: „TARCZA PĘKŁA!” |
| `utrata_tury` | „TRACI TURĘ!”, chwianie się i ozdoba spowolnienia: lód przy lodowym pocisku, pnącza przy uścisku korzeni, gwiazdki przy ogłuszeniu |

Obrażenia **magiczne** mają fioletowe liczby, fizyczne białe (zadane) / różowe (otrzymane). Gdy całe trafienie weźmie
tarcza (kamienna skóra, bariera), zamiast „−0” jest tylko „TARCZA −n” — przy zwykłym ciosie, krytyku i bloku. Paski dostają życie
z dziennika (`hp_gracz`, `hp_wrog`) w chwili trafienia; na początku każdego zdarzenia odtwarzacz sprawdza, czy pasek
zgadza się z poprzednim zdarzeniem (licznik `OstatniaNiezgodnoscPaskow`, w testach zawsze 0).

| Umiejętność | Styl | Co dzieje się na ekranie |
|---|---|---|
| Potężne cięcie (Wojownik) | wręcz | klip cięcia, biała smuga za mieczem |
| Miażdżący cios | wręcz | złota smuga, fala uderzeniowa pod celem, potem „ZDARTY PANCERZ!” (odłamki i pęknięta tarczka nad głową) |
| Kamienna skóra | na siebie | szary rozbłysk, potem kamienie krążące wokół i szara powłoka (ForceField) |
| Uderzenie z góry (Zwiadowca) | skok | wyskok łukiem nad celem, cios z góry, fala na ziemi |
| Zatruta strzała | pocisk | strzała z zielonym grotem i smugą (kamera zza łucznika od strony lasu, w locie przechodzi w skos na obu), zielony rozbłysk, bąbelki trucizny |
| Skupienie | na siebie | złoty rozbłysk, złoty krąg pod stopami i iskry |
| Kula ognia (Mag) | pocisk | kula z ogniem i światłem leci z kostura, wybuch, potem ogień na celu (podpalenie) |
| Lodowy pocisk | pocisk | lodowy kryształ z rdzeniem, lodowy rozprysk; przy spowolnieniu „SPOWOLNIENIE!”, lodowe kryształy przy nogach, szron i lód pod stopami |
| Bariera | na siebie | niebieska bańka (ForceField) wokół Maga, pulsuje przy pochłanianiu |
| Zwykły atak Maga | pocisk | mała fioletowa iskra z kostura (atak Maga jest magiczny) |
| Kwaśny plusk (Slime) | pocisk | zielona kula łukiem, kwaśny rozprysk, zdarty pancerz |
| Rozszarpanie (Wilk) | wręcz | skok z klipu, trzy czerwone ślady pazurów, potem krople krwawienia |
| Chmura zarodników (Muchomornik) | chmura | fioletowa chmura płynie z kapelusza i otula cel, potem trucizna |
| Ogłuszające uderzenie (Troll) | wręcz | fala uderzeniowa, często spowolnienie (gwiazdki nad głową, utrata tury) |
| Uścisk korzeni (Strażnik) | korzenie | korzenie (kliny z liśćmi) wyrastają wokół celu i trzymają go do końca zdarzenia, zielona poświata; spowolnienie = pnącza wokół nóg |

**Kamera** — ujęcia planowane na zdarzenia (deterministycznie z ziarna, więc ta sama walka ma te same ujęcia):
plan ogólny (co piąty zwykły cios i na start), z boku 3/4, zza atakującego, zza broniącego, zbliżenie celu, krytyk
(niska kamera, zwolnienie, „wjazd”), lot pocisku, umiejętność na siebie, efekt / utrata tury, objazd zwycięzcy w finale.
Odległości liczone z wysokości i szerokości aktorów (Muchomornik 3,6 – Strażnik 12 studów). Przeciw nudzie
i szarpaniu: zwykłe ujęcie trwa co najmniej 0,9 s czasu rzeczywistego (×1,6 przy tempie ×2/×4, ×1,5 po 12. turze),
po 12. turze kamera zmienia ujęcie tylko co drugie zdarzenie, a przy ×2/×4, w długiej walce i przy tym samym typie
ujęcia przechodzi płynnie (0,45 s) zamiast ciąć. Zza pleców dużo większego aktora (ponad 1,3×) albo przy różnicy
wzrostu ponad 1,8× kamera bierze ujęcie boczne.

Kadr liczony z **bieżących** położeń aktorów (poprawka po przeglądzie): ujęcia krytyk i boczne obejmują obu aktorów
tam, gdzie są teraz — po doskoku, w powietrzu i po odrzucie — a „wjazd” przy krytyku zwęża kąt tylko do kadru,
w którym obaj się mieszczą. Uderzenie z góry ma zawsze ujęcie z boku (widać cały łuk wyskoku). Lot pocisku: przy
wypuszczeniu kamera jest zza ramienia strzelca (odsunięta w bok tak, żeby cel nie chował się za jego bryłą), a w
czasie lotu przechodzi w skos 3/4 na obu, więc w chwili trafienia cel jest duży i odsłonięty. Atak zaraz po ujęciu
jednej postaci (umiejętność na siebie, efekt) zawsze dostaje własne ujęcie — wcześniej w długiej walce kamera potrafiła
zostać na samym rzucającym. Pilnuje tego `testy/test_poprawek_play.py` (część `kadr`).

**Finał:** upadek pokonanego (klip `upadek`), radość zwycięzcy (`radosc`), baner, przy wygranej wysypany łup (monety,
żetony lasu, Gem, kryształ Shardu), objazd kamery i panel wyniku: Złoto, doświadczenie, tokeny krainy, Gem, Shard
Ewolucji (zera wyszarzone), podtytuł z liczbą tur, stopka z ziarnem i czasem dziennika.

**Sprzątanie** jak w v1: blokada sterowania (także dotykowego), ukryte GUI gry i elementy Roblox, wyłączona podpowiedź,
lokalnie schowani wszyscy gracze, obiekty z tagiem `TestWalki2Ukryj` i obce części w pudle sceny; po ZAMKNIJ, resecie
postaci, zniknięciu kontenera albo błędzie wszystko wraca, a wszystko lokalne jest niszczone. Kamera wraca do
zwykłej (`Custom`) także wtedy, gdy przed walką była skryptowa.

**Interfejs** (`zrodla/InterfejsWalki2.luau`, `zrodla/WyborWalki2.luau`) — w `PlayerGui`, tworzony w czasie działania
(nic w `StarterGui`). Kadr 16:9 z czarnymi pasami przy węższych proporcjach (na szerokim ekranie telefonu kadr zajmuje
cały ekran). Ekrany walki mają `DisplayOrder` 101–103,
czyli **nad** ekranem ładowania gry (`LoadingScreen`, 100) — ten zostaje włączony po załadowaniu i przechwytywał
kliknięcia (wyszło w teście Play). Gdy pasek Roblox u góry spycha tabliczki z paskami w dół (telefon, okno bez pasów),
wstęga z nazwą umiejętności idzie na dół ekranu, między przyciski tempa a POMIŃ. Panel wyniku odmienia liczebniki
(„w 1 turze”, „3 tury”, „24 tury”, „33 zdarzenia”).

**Telefon (emulacja):** `testy/telefon.py` ustawia atrybut `EmulacjaEkranu` (np. 844 × 390 punktów) — panel wyboru
i interfejs walki układają się wtedy w prostokącie o proporcjach telefonu, kamera kadruje jak na tym ekranie, a skrypt
mierzy wysokość każdego widocznego napisu w punktach telefonu i zapisuje wycięte zrzuty `klatki/telefon_*.jpg`.

## Jak odbudować

```
python -B swiat/test_walki2/zbuduj.py --sucho           # sprawdza źródła, strażniki, dane i plan — bez Studio
python -B swiat/test_walki2/zbuduj.py                   # buduje / odbudowuje cały kontener (idempotentnie, ok. 7 s)
python -B swiat/test_walki2/zbuduj.py --skrypty         # tylko skrypty i moduły (zrodla/, kopia silnika, tabela) — ok. 1 s
python -B swiat/test_walki2/zbuduj.py --tylko-aktorzy mag,wojownik   # tylko dane i szablony tych aktorów
python -B swiat/test_walki2/zbuduj.py --usun            # usuwa kontener (np. przed publikacją)
python -B swiat/test_walki2/aktorzy.py [--tylko k]      # dane aktorów z modeli (Blender pod wspólną blokadą, ok. 15 s)
```

Budowa wymaga Studio w trybie **Edit** z serwerem MCP; przy kilku oknach `--studio <id>` (lista:
`python -B tools/studio_mcp.py studios`). Silnik trafia do `Moduly/Walka` jako **kopia** `src/server/Walka` przy każdej
budowie (i `Moduly/Dziennik` z `src/shared/Walka`) — źródło prawdy zostaje w `src/`.

## Jak dodać aktora, umiejętność albo choreografię

- **Aktor** (np. docelowy Leśny Slime albo Strażnik Gaju): wpis w `AKTORZY` w `aktorzy.py` (model, klipy na akcje,
  umiejętności, punkty, `zastepczy = None`) → `aktorzy.py --tylko <klucz>` → `zbuduj.py` (nowy aktor: pełna budowa,
  żeby galeria się przesunęła). Zasięg broni i pierś do doskoku liczy `zbuduj.py` sam z danych. Portret w interfejsie:
  ikona 8×8 o tym kluczu w `IKONY` w `InterfejsWalki2.luau` (test pilnuje, że jest).
- **Umiejętność:** po dopisaniu do `tools/walka/dane_walki.json` dopisz wpis w `Choreografie.UMIEJETNOSCI` (styl i
  dodatki: `pocisk`, `wybuch`, `smuga`, `fala`, `pazury`, `aura`, `kamera`) oraz klip w tabeli aktorów.
  `testy/test_odtwarzacza.py` i `testy/test_aktorow.py` nie przejdą, dopóki umiejętność nie ma wpisu — nie zostanie
  po cichu bez animacji. Gdyby w grze trafiło się coś bez wpisu, odtwarzacz gra styl zastępczy i liczy to
  w `OstatnieBrakiChoreografii`.
- **Nowa choreografia** (nowy styl): funkcja `Choreo.<styl>` w `OdtwarzaczWalki2.luau` (wzór: `Choreo.pocisk` —
  `zaplanujAtak` z funkcją „wypuszczenia”), nazwa w `Choreografie.STYLE`; nowy pocisk / rozbłysk / ozdoba efektu to
  funkcja `Pocisk.<x>` / `Wybuch.<x>` / `Wyglad.<x>` w `Efekty3D.luau`. Nowy typ zdarzenia: `Choreografie.ZDARZENIA` +
  `Obsluga.<nazwa>`.

## Pliki

| Plik | Co robi |
|---|---|
| `zrodla/SerwerWalki2.server.luau` | serwer: wybór z listy → postać wzorcowa → `Silnik.symuluj` → dziennik; zabezpieczenia; poza Studio usuwa kontener |
| `zrodla/Wzorcowe.luau` | port `tools/walka/wzorcowe.py` (pula punktów, rozkład klasy, broń, pancerz, sloty, tarcza) |
| `zrodla/OdtwarzaczWalki2.luau` | cutscenka: sesja, scena lokalna, plan zdarzeń (tury, efekty, czasy trafień, ujęcia, zwolnienia), choreografie, kamera, finał, POMIŃ, JESZCZE RAZ, sprzątanie, pomiary |
| `zrodla/Choreografie.luau` | **dane** choreografii: typ zdarzenia → obsługa, umiejętność → styl i dodatki, efekt → wygląd, ikona, kolor |
| `zrodla/Efekty3D.luau` | efekty z części i wbudowanych efektów: pociski, rozbłyski, fale, pazury, chmura, korzenie, smugi, ozdoby efektów, łup |
| `zrodla/InterfejsWalki2.luau` | interfejs walki (paski, rangi, ikony efektów, tura, nazwa umiejętności, tempo, POMIŃ, napisy, panel wyniku) |
| `zrodla/WyborWalki2.luau` | panel wyboru przy tablicy |
| `zrodla/KlientWalki2.client.luau` | podpowiedź → panel → odtwarzacz; komunikat odmowy serwera; haczyki testowe `Sygnaly/PokazAktora`, `Sygnaly/Sterowanie` (m.in. „kadr”, „napisy”) |
| `zrodla/Ustawienia.luau`, `Klipy.luau`, `Aktorzy.luau` | z etapu 1 (stałe, odtwarzacz klipów z danych, lokalne klony aktorów) |
| `zbuduj.py` | odtwarza kontener w Studio (`--skrypty`, `--tylko-aktorzy`, `--sucho`, `--usun`) |
| `aktorzy.py`, `przerobki.py`, `geometria.py`, `dane/` | z etapu 1: tabela aktorów, klipy zastępcze, kinematyka, dane rigów |
| `testy/test_odtwarzacza.py` | testy bez Studio (pokrycie choreografii, dzienniki z portu, tury, efekty, paski) + `--ziarna` |
| `testy/sprawdz_edit.py` | tryb Edit, tylko odczyt: moduły się wczytują, serwerowa postać wzorcowa + kopia silnika = Python |
| `testy/test_walki_play.py` | pełny test w trybie Play (wynik w `testy/wynik_play.json`) |
| `testy/test_poprawek_play.py` | test Play poprawek po przeglądzie: kadr kamery w chwili trafienia, „−0”, napis i wygląd spowolnienia, odmiana w panelu wyniku, komunikat odmowy, paski / tura / ikony efektów na ekranie = stan silnika (wynik w `testy/wynik_poprawek.json`) |
| `testy/telefon.py` | emulacja ekranu telefonu w poziomie: zrzuty `klatki/telefon_*.jpg` i wysokość napisów w punktach (`klatki/raport_telefonu.json`) |
| `testy/klatki_walki.py` | arkusze klatek z prawdziwego odtwarzania → `klatki/walka_*.jpg` |
| `testy/sesja_play.py`, `testy/proba_play.py` | wspólna obsługa sesji Play; próba jednej walki (arkusz albo odtworzenie na żywo) |
| `testy/ziarna.json` | ziarna pokazowe i testowe (z `test_odtwarzacza.py --ziarna`) |
| `testy/test_aktorow.py`, `test_klipow_play.py`, `klatki_aktorow.py`, `zrzut_edit.py`, `czuwanie.py` | z etapu 1 |

W kontenerze: `Moduly/` (moduły wyżej, `TabelaAktorow`, `DaneAktorow/<klucz>/<klip>`, `Walka/` — kopia silnika,
`Dziennik`), `Aktorzy/` (szablony), `Galeria/`, `Arena/`, `Zdalne/RozpocznijWalke2`, `Sygnaly/PokazAktora`,
`Sygnaly/Sterowanie`, `SerwerWalki2`, `KlientWalki2`.

## Testy (ostatni pełny przebieg 15.11.2026, Studio na PC, na końcowym kodzie)

```
python -B swiat/test_walki2/testy/test_odtwarzacza.py            # bez Studio, ok. 1 s
python -B swiat/test_walki2/testy/test_aktorow.py                # bez Studio (etap 1)
python -B swiat/test_walki2/testy/sprawdz_edit.py                # tryb Edit, tylko odczyt
python -B swiat/test_walki2/testy/test_klipow_play.py            # tryb Play (etap 1), ok. 1 min
python -B swiat/test_walki2/testy/test_walki_play.py             # tryb Play, ok. 6 min, sam wraca do Edit
python -B swiat/test_walki2/testy/test_poprawek_play.py          # tryb Play, ok. 1,5 min (--tylko kadr,zero,efekt,wynik,odmowa,paski)
python -B swiat/test_walki2/testy/telefon.py                     # tryb Play, ok. 1 min (emulacja telefonu)
python -B swiat/test_walki2/testy/klatki_walki.py                # tryb Play, ok. 4 min (--lista, --tylko a,b)
python -B swiat/test_walki2/testy/zrzuty_raportu.py              # tryb Play: duże kadry do raportu → klatki/raport_*.jpg
```

Wyniki 15.11: `test_odtwarzacza.py` **9/9**, `test_aktorow.py` **6/6**, `sprawdz_edit.py` **OK** (10/10 modułów,
45/45 walk = Python, funkcje pomocnicze), `test_klipow_play.py` **24/24**, `test_walki_play.py` **112/112**,
`test_poprawek_play.py` **29/29**, `telefon.py` **0 napisów poniżej 12 punktów**; klatki odświeżone i obejrzane.
Studio po każdym teście w trybie Edit.

- **`test_poprawek_play.py`: 29/29** — kadr: 11 umiejętności ataku (0,25 s przed trafieniem, w chwili trafienia,
  0,2 s po) i każde trafienie walki 24-turowej (21) i 33-turowej (32); progi: w ujęciach dwóch postaci obie ≥ 60%
  części w kadrze, cel ≥ 45% niezasłonięty; zza pleców postać z przodu może być ucięta (≥ 25%), zbliżenie celu
  pokazuje z atakującego rękę z bronią (≥ 15%); ujęcie jednej postaci w chwili ataku = błąd (ten błąd test znalazł
  w długich walkach i jest poprawiony). Bez „−0” (blok i cios w całości na tarczy), „SPOWOLNIENIE!” z lodem / pnączami
  / gwiazdkami, odmiana w panelu wyniku, komunikat odmowy (dymek i panel), paski + „TURA n” + ikony efektów z
  licznikami na ekranie = migawka stanu silnika po każdym zdarzeniu (5 walk, 93 zdarzenia), konsola czysta.
- **Bez Studio — `test_odtwarzacza.py`: 9/9** (doszły: napis efektu = nazwa z danych, wygląd spowolnienia dla każdej
  umiejętności, która je nakłada). Każdy z 9 typów zdarzeń ma obsługę, każda z 14 umiejętności ma
  choreografię ze znanym stylem, pociskiem i rozbłyskiem (i odwrotnie), każdy z 8 efektów ma wygląd i ikonę, każdy
  aktor ma portret, `Wzorcowe.luau` ma te same liczby co `wzorcowe.py`. **2700 dzienników** z portu (3 klasy × 5
  przeciwników × poziomy 1/5/10 × 60 ziaren; 3–33 tury): wszystkie przechodzą `Dziennik.sprawdz`, wystąpiło 9/9 typów
  i 14/14 umiejętności, tury liczone przez odtwarzacz = tury silnika, liczniki efektów nie gubią efektu i schodzą do
  zera przy `efekt_koniec`, paski = dziennik po każdym zdarzeniu.
- **Edit — `sprawdz_edit.py`:** 10/10 modułów się wczytuje; **45/45 walk** (3 klasy × 5 przeciwników × 3 poziomy)
  z `Wzorcowe.luau` + kopii silnika w Studio = Python (wynik, tury, zdarzenia, czas, życie, łup).
- **Play — `test_walki_play.py`: 112/112** (drugi i trzeci przebieg po poprawkach; pierwszy 91/112 — patrz „Co wyszło
  w testach”): E przy tablicy otwiera panel, kliki myszą w klasę, przeciwnika, poziom i WALCZ → walka; **9 pełnych
  walk** (każda klasa z 3 różnymi przeciwnikami, poziomy 1/5/10, ×1 i ×4; pierwsza z panelu) + **długa 24 tury** (×1) + **najdłuższa
  33 tury** (×4 kliknięte w trakcie: 15,6 s zamiast ok. 54 s) + **krótka 3 tury** — po każdej: dziennik = Python,
  wszystkie zdarzenia obsłużone, 0 braków choreografii, 0 błędów, 0 niezgodności pasków, licznik tur = silnik, łup na
  panelu = dziennik; długa walka odtwarza się ≥ czas dziennika (42,8 s przy 39,1 s — nic nie skrócone, zwolnienia
  przy krytykach dokładają czas); POMIŃ → panel w 0,07 s, „JESZCZE RAZ” szare z odliczaniem („ZA 19 s”), klik w trakcie
  blokady nic nie robi, po czasie JESZCZE RAZ → nowa walka z tym samym wyborem; ZAMKNIJ → kamera `Custom`, GUI,
  lista graczy, czat, podpowiedź, szablony wracają, postać chodzi; **reset postaci w trakcie** → wszystko posprzątane,
  po odrodzeniu kamera i sterowanie działają; **bezpieczeństwo**: zła klasa, poziom jako liczba, poziom spoza listy,
  nieznany przeciwnik, nie-tabela, brak argumentów → `zly_wybor`; wybór z dopisanymi liczbami (`zycie = 1e9`,
  `statystyki`, `zloto`, `ziarno`, `wynik`, dodatkowe argumenty) → walka liczona po swojemu (ziarno i życie serwera);
  druga prośba w 1 s → `za_szybko`; prośba w trakcie sesji → `walka_trwa` („ponów za 18,9 s”); 34 studów od tablicy →
  `za_daleko`; odmowy nie niosą łupu; **obcy w kadrze** (część w pudle sceny i część z tagiem `CanQuery = false`)
  schowani w walce, widoczni przed i po; **symulacja publikacji**: kopia serwera z `IsStudio() = false` usuwa swój
  folder (u serwera i klienta); konsola bez komunikatów z `TestWalki2`; Studio wraca do Edit.
- **Klatki — `klatki_walki.py`:** 23 arkusze (niżej), wszystkie obejrzane; konsola bez komunikatów z `TestWalki2`.
- Testy z etapu 1 (`test_aktorow.py` 6/6) przechodzą dalej.

Macierz walk w teście Play idzie z atrybutem serwera **`TestBezSesji`** (bez czekania na koniec sesji między walkami),
tak samo narzędzie klatek. Atrybut ustawia tylko kod po stronie serwera (zmiana u klienta się nie replikuje); blokadę
sesji testują osobno punkty 3f–3k i 5d bez tego atrybutu.

### Co wyszło w testach i zostało poprawione

- Kliknięcia nie trafiały: ekran ładowania gry (`LoadingScreen`, `DisplayOrder` 100) zostaje włączony i łapie
  wejście → nasze ekrany mają teraz `DisplayOrder` 101–103. (Do tego błąd w samym teście: zła ścieżka przycisku.)
- Po resecie w trakcie walki raz zostawała kamera `Scriptable` → przyczyną było narzędzie `execute_luau`, które po
  każdym wywołaniu przywraca typ kamery (patrz „Pułapki”), a nie gra; zamiana `Scriptable` → `Custom` zostaje jako
  zabezpieczenie.
- Na klatkach: przy dużym Trollu ujęcia były za blisko, zza pleców Trolla nie było widać Wojownika, plakietka rangi
  zasłaniała nazwę przeciwnika, napisy wchodziły na wstęgę umiejętności, „−0” przy pełnym pochłonięciu przez tarczę,
  za dużo napisów „koniec: …”, ujęcia zza szerokiego Slime'a, korzenie poza kadrem, za mocny „wjazd” przy krytyku —
  wszystko poprawione (kadrowanie z wysokości i szerokości aktorów, reguły zamiany ujęć, układanie napisów pod sobą).

## Poprawki po przeglądzie (etap 4, 15.11.2026)

| Uwaga przeglądu | Co zmienione | Czym sprawdzone |
|---|---|---|
| kamera nie pokazuje chwili trafienia (pocisk: cel za strzelcem; krytyk Potężnego cięcia: Wojownik poza kadrem; Uderzenie z góry: widać tylko nogi) | kadr krytyka i ujęcia bocznego z bieżących położeń obu aktorów (doskok, wyskok, odrzut); Uderzenie z góry zawsze z boku; lot pocisku: zza ramienia → skos 3/4 na obu, odsunięcie w bok, gdy cel chowałby się za strzelcem; atak po ujęciu jednej postaci zawsze dostaje własne ujęcie | `test_poprawek_play.py` część `kadr` (pomiar z kamery: ułamek części aktora w kadrze 16:9 i niezasłoniętych przez drugiego) — każda umiejętność ataku przed, w chwili i po trafieniu oraz każde trafienie dwóch najdłuższych walk; świeże arkusze klatek obejrzane |
| czytelność na telefonie nie sprawdzona | emulacja ekranu (`EmulacjaEkranu`); panel wyboru przebudowany (karta większa, styl klasy pełną szerokością pod nazwą, ranga osobno, naklejka „ZASTĘPCZY”, nazwy przeciwników w dwóch wierszach); większe liczniki tur przy ikonach efektów; wstęga umiejętności na dole, gdy pasek Roblox spycha tabliczki | `telefon.py`: 844 × 390 i 667 × 375 punktów, najmniejszy napis ≥ 12 punktów (poza techniczną stopką panelu wyniku, 11 punktów); zrzuty obejrzane |
| „−0” przy bloku na tarczy | ten sam warunek w gałęziach bloku, krytyka i zwykłego ciosu (`Sesja.pokazLiczbe`) | `sprawdz_edit.py` (funkcja) + `test_poprawek_play.py` część `zero` (blok i cios w całości na tarczy: tylko „TARCZA −n”) |
| „OGŁUSZENIE!” przy spowolnieniu od lodowego pocisku i korzeni | napisy efektów = nazwy z danych silnika („SPOWOLNIENIE!”, „ZDARTY PANCERZ!”); wygląd spowolnienia od umiejętności: lód, pnącza, gwiazdki (`Choreografie.WYGLAD_SPOWOLNIENIA`) | `test_odtwarzacza.py` (napis = nazwa z danych; każda umiejętność ze spowolnieniem ma wygląd) + część `efekt` w Play |
| „3 tur”, „w 1 turach” | `Interfejs.liczebnik`, `Interfejs.wTurach` w podtytule i stopce | `sprawdz_edit.py` (14 liczb) + część `wynik` w Play |
| przyczyna „kamery Scriptable” nieustalona | ustalona: narzędzie `execute_luau` przywraca typ kamery po każdym wywołaniu (sprawdzone) — opis w „Pułapkach” | próba w Play |
| odmowa serwera bez komunikatu | `Odtwarzacz.naOdmowe` → KlientWalki2: przy tablicy panel wyboru z polem Status, dalej dymek na 3,5 s | część `odmowa` (za daleko → dymek; zły wybór przy tablicy → panel z komunikatem) |
| test pasków prawie tautologiczny | nowy test na EKRANIE: po każdym zdarzeniu napis paska, „TURA n” i ikony efektów z licznikami kontra migawka stanu silnika (port Pythona z podglądem stanu przy każdym zdarzeniu) | część `paski`: 5 walk, w tym 24-turowa |

## Pomiary (PC ze Studio — **nie telefon**)

Z przebiegu `test_walki_play.py` (walki przy ×1; kolejny przebieg na końcowym kodzie dał te same wartości w granicach
±0,1 ms, maks. klatki 36–94 ms — `testy/wynik_play.json`):

| Walka | Czas odtworzenia (dziennik) | Klatka śr. / p95 / maks. | Nasz kod na klatkę śr. / p95 / maks. | Instancji lokalnie | Ujęć |
|---|---|---|---|---|---|
| wojownik / lesny_slime / 1, 12 tur | 27,8 s (19,8 s) | 16,67 / 17,94 / 45 ms | 0,21 / 0,42 / 1,9 ms | 1108 | 13 |
| zwiadowca / cierniowy_wilk / 5, 12 tur | 28,9 s (23,6 s) | 16,70 / 17,79 / 95 ms | 0,30 / 0,63 / 1,7 ms | 2301 | 16 |
| mag / muchomornik / 10, 10 tur | 24,8 s (21,0 s) | 16,68 / 18,01 / 54 ms | 0,24 / 0,50 / 2,4 ms | 1768 | 14 |
| długa: wojownik / straznik_lasu / 10, 24 tury | 42,8 s (39,1 s) | 16,67 / 17,83 / 37 ms | 0,24 / 0,48 / 2,2 ms | 2310 | 22 |
| krótka: mag / muchomornik / 5, 3 tury | 12,6 s (7,3 s) | 16,67 / 18,03 / 31 ms | 0,24 / 0,50 / 1,6 ms | 1257 | 4 |

- Od WALCZ do pierwszej klatki walki: 152–170 ms (w tym prośba do serwera 57–91 ms i zaciemnienie).
- „Nasz kod na klatkę” = czas procesora całej funkcji klatki odtwarzacza (oś czasu, pozy, klipy, efekty, kamera,
  interfejs, chowanie obcych), bez renderowania. Średni czas klatki = limit 60 FPS Studia; pojedyncze długie klatki
  (do 95 ms) przypadają na start walki (klonowanie aktorów; Wilk ma 1138 instancji).
- Czas odtworzenia jest dłuższy od czasu dziennika o zwolnienia (krytyk ok. +2,5 s, cios kończący ok. +1 s) i
  zasłonę/finał; przy ×2 / ×4 dzieli się odpowiednio. Silnik ani odtwarzacz niczego nie skracają.
- **Telefonu nie zmierzono** — w Studio na PC nie da się tego zrobić (emulator urządzeń nie mierzy wydajności);
  pomiar wymaga uruchomienia na prawdziwym telefonie (np. testowa publikacja — bez zgody nie publikuję). Nie
  zmierzono też zapasu mocy PC (Studio trzyma 60 FPS), GPU, pamięci, prawdziwej sieci i wielu graczy.

## Klatki (`klatki/`)

| Plik | Co pokazuje |
|---|---|
| `walka_umiejetnosc_<id>.jpg` (14) | choreografia każdej umiejętności z prawdziwej walki: 8 klatek od początku zdarzenia do końca nałożonego efektu; podpis = czas sceny, zdarzenie, umiejętność, ujęcie |
| `walka_krytyk.jpg`, `walka_blok.jpg`, `walka_unik.jpg` | krytyk wręcz (zwolnienie, wjazd), blok tarczą Wojownika, unik |
| `walka_tykniecie.jpg`, `walka_utrata_tury.jpg` | tyknięcie trucizny, ogłuszenie i utrata tury |
| `walka_final_wygrana.jpg`, `walka_final_przegrana.jpg` | finał (upadek, radość, baner, łup, objazd) i panel wyniku — z Shardem Ewolucji i po przegranej |
| `walka_dluga_walka.jpg` | przekrój 24-turowej walki co ok. 2,4 s — zróżnicowanie ujęć |
| `walka_panel_wyboru.jpg` | panel wyboru przy tablicy |
| `telefon_<szer>x<wys>_{panel,walka,wynik}.jpg` | emulacja telefonu w poziomie (844 × 390, 667 × 375): panel wyboru, walka z umiejętnością i efektami, panel wyniku; `raport_telefonu.json` — wysokość każdego napisu w punktach |
| `raport_1..5_*.jpg` | duże pojedyncze kadry do raportu w panelu (panel wyboru, krytyk, kula ognia w locie, spowolnienie z lodem i utratą tury, panel wyniku z łupem) |
| `raport_klatek_walki.json` | które walki i ziarna są na arkuszach |
| reszta (`<aktor>_*.jpg`, `obrys_*.jpg`) | z etapu 1: klipy aktorów i porównanie obrysu |

Uwaga do arkuszy: zdjęcia robione są przy zatrzymanym czasie sceny (narzędzie przesuwa go skokami), a napisy nad
postaciami starzeją się w czasie rzeczywistym — dlatego na arkuszach napisy z kilku zdarzeń częściej stoją naraz niż
przy zwykłym oglądaniu. Pierwsze klatki tuż po starcie Play zasłaniał ekran ładowania gry — narzędzie czeka teraz, aż zniknie.

## Bezpieczeństwo

- Wszystko w jednym kontenerze `Workspace/TestWalki2` z atrybutem `Wygenerowane = true`; budowa, odbudowa i `--usun`
  ruszają tylko go (gdy pod tą nazwą jest coś bez atrybutu — przerywają). Przed pełną budową `GetPartBoundsInBox`
  sprawdza pudło sceny. Każdy kod wysyłany do Studio sprawdza `game.PlaceId`; okno wybiera
  `swiat/test_walki_roblox/cel_studio.py`. Punkty historii przed i po budowie. Tylko tryb Edit; bez publikacji, zapisu
  miejsca, zmian w Lighting, StarterGui, ReplicatedFirst i skryptach gry.
- Każdy skrypt i moduł w kontenerze zaczyna się od strażnika Studio (sprawdza `zbuduj.py`); `SerwerWalki2` poza
  Studio usuwa cały kontener (sprawdzone symulacją w teście Play); podpowiedź jest zbudowana jako wyłączona.
- Klient nie wysyła liczb (D-016): tylko trzy napisy z listy; serwer liczy postać, przeciwnika, ziarno, walkę i łup.
- Niczego nie wgrano: części Roblox, klipy z danych, `ParticleEmitter` z domyślną teksturą, `Fire`, `Trail`, materiały
  `Neon` / `ForceField` / `Glass`, dźwięki `rbxasset://`.
- Haczyki testowe (`Sygnaly/Sterowanie`, atrybuty serwera `ZiarnoTestowe`, `TestBezSesji`) działają tylko w Studio
  jak cały prototyp; w grze nie istnieją.

## Ograniczenia i słabe strony (uczciwie)

- **Klipy zastępcze z etapu 1** (Rycerz, Kot-Mag) to szkice: „Potężne cięcie” to obrót z mieczem — w ujęciu krytyka
  Wojownik obraca się ku kamerze i wypełnia lewą część kadru; garda Rycerza odwraca go przodem do kamery.
- **Szerokie i duże modele** (Slime 4,9 studa szerokości, Troll 10 i Strażnik 12 wysokości) czasem wchodzą częściowo
  poza kadr albo zasłaniają część sceny w ujęciach z bliska; reguły kadrowania to ograniczają, ale nie zawsze.
- **Strzały i iskry są szybkie** — w zwykłym tempie lot strzały trwa ok. 0,25 s; na arkuszach rzadko widać ją w locie.
- **Dużo napisów naraz** w turach z kilkoma zdarzeniami (cios + nałożenie + tarcza) — układają się pod sobą, ale
  bywa tłoczno, zwłaszcza na małym ekranie.
- **Na prawdziwym telefonie interfejsu nie oglądałem.** Sprawdzona jest emulacja proporcji i rozmiaru w punktach
  (844 × 390, 667 × 375; `testy/telefon.py`) — to nie mierzy dotyku, gęstości pikseli ani wydajności telefonu.
  Okno Studio miało 761 × 675 px, więc emulacja 844 × 390 jest pomniejszona do 0,9.
- Leśny Slime i Strażnik Lasu są **zastępcze** (etap 1). Wojownik nie ma w próbie walki ze wszystkimi 9 rodzajami
  zdarzeń naraz (brak tyknięcia w tej samej walce co blok i utrata tury).
- Dźwięki: tylko cztery wbudowane z v1 (cios, krytyk, upadek, przycisk); pociski i czary są ciche.
- Arena stoi w świecie wspólnym — obcy są chowani lokalnie jak w v1 (te same ograniczenia: części z `CanQuery = false`
  bez tagu, dźwięki innych graczy).
- Komunikaty „TexturePack … Referenced Asset 5 is NOT found” w konsoli przy starcie Play pochodzą z
  `Workspace/TestPostaci` (SurfaceAppearance importu FBX Rycerza), nie z prototypu — pojawiają się też bez walki.

## Pułapki (sprawdzone przy tej pracy)

- Etap 1: układy osi (biblioteka postaci przód +Z, rig Roblox przód −Z; lokalne (x, y, z) sceny = świat (−x, y + 1,
  250 − z)), Motor6D w trybie Edit nie rusza części (klipy oglądać w Play), limit `Source` 200 000 znaków (dane klipów
  po jednym module na klip), wygładzanie Blendera potrafi przerzucić broń przez głowę.
- `user_mouse_input` w Play: ścieżka przycisku zaczyna się od `LocalPlayer.PlayerGui.` (nie `game.Players.…`).
- `screen_capture` w Play sam ustawia kamerę — podawaj bieżącą kamerę odtwarzacza (`Sygnaly/Sterowanie` „stan”
  zwraca jej pozycję i punkt, na który patrzy).
- Ekran gaśnie → Studio przestaje rysować: narzędzia testowe wołają `testy/czuwanie.py`.
- Ekran ładowania gry zostaje włączony po załadowaniu i łapie kliknięcia — interfejs nad nim (`DisplayOrder` > 100).
- **Narzędzie `execute_luau` (MCP) po każdym wywołaniu przywraca typ kamery, jaki zastało na jego początku**
  (sprawdzone 15.11: `Scriptable` ustawione w jednym wywołaniu → `Custom` w następnym). To była przyczyna „kamery
  `Scriptable` po resecie”, którą etap 2 opisał jako niewyjaśnioną: nie gra, tylko narzędzie testowe. Kamerę po
  ZAMKNIJ czytaj w tym samym wywołaniu albo zamykaj kliknięciem (`user_mouse_input`) — inaczej test dostanie
  fałszywy błąd. Zamiana `Scriptable` → `Custom` przy przywracaniu kamery zostaje jako zwykłe zabezpieczenie.
- Odtwarzacz w trybie `reczny` (testy) nie przesuwa czasu sam; zrzuty z przewijania pokazują nawarstwione napisy, bo
  napisy starzeją się w czasie rzeczywistym.
- `string.upper` w Luau nie zmienia polskich liter („STRAżNIK”); w czcionkach komiksowych prototypu (same wersaliki)
  wygląda to dobrze, ale napisy porównywane w testach (napisy efektów) są w danych od razu wielkimi literami.
