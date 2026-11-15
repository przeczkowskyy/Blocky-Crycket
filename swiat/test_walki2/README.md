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
**Etap 5** (15.11) podmienił dwa modele zastępcze na właściwe: **Leśny Slime** (`swiat/postacie/lesny_slime.py`,
wersja 3 — sześcian) i **Strażnik Gaju** (`swiat/postacie/straznik_gaju.py`), a nazwa strażnika w danych walki to teraz
„Strażnik Gaju” (identyfikator `straznik_lasu` bez zmian) — patrz „Właściwe modele (etap 5)”. Zastępczych aktorów już nie ma.
**Etap 6** (15.11, „dopieszczenie” D1–D8 po obejrzeniu filmów): ujęcie pokonanego w finale, wolniejsze i czytelne
pociski i bańka kwasu z kałużą, kolejka napisów bez nakładania, dźwięki z klienta z przyciskiem wyciszenia, twarz potwora
w kadrze, jaśniejszy slime bez „soczewek”, finał w ×1 przy ×2/×4, skorupa bez skóry — patrz „Dopieszczenie (etap 6)”.
**Etap 7** (15.11, po przeglądzie etapu 6, 12 uwag): pocisk przy krytyku dolatuje bez „zawieszenia” (zwolnienie od
chwili dolotu), strzała kończy lot na powierzchni celu i zostaje wbita, słabsze światło strzały, napisy liczone z
narysowanego rozmiaru (także w wejściu i wygaszaniu) i z prawdziwej szerokości tekstu, wybór miejsca stosu z ocen
kandydatów (nigdy na małej postaci ani na głowie dużej), zwycięzca w radości obraca się do widza, gracz po obrocie do
twarzy potwora nie jest już „wielki na pierwszym planie”, płaty kałuży slime'a dopiero przy rozlanej galarecie, test 1f
bez fałszywego błędu — patrz „Poprawki po przeglądzie etapu 6 (etap 7)”.

## Jak obejrzeć (krok po kroku)

1. Studio, miejsce gry (Team Create). W `Workspace` jest folder **`TestWalki2`** (atrybut `Wygenerowane = true`).
   Jeśli go nie ma — odbuduj (niżej).
2. Naciśnij **Play** (F5). Ze spawnu idź **na południe** — zobaczysz zielony świecący słup i tablicę „WALKA v2”
   (ok. 220 studów; tablica stoi w `(16, 0, 220)`).
3. Podejdź do tablicy: podpowiedź „Walka v2 (prototyp) · Wybierz walkę”. Naciśnij **E** (telefon: dotknij).
4. Panel wyboru: **klasa** (Wojownik / Zwiadowca / Mag), **przeciwnik** (Leśny Slime, Cierniowy Wilk, Muchomornik —
   zwykli; Leśny Troll — rzadki; Strażnik Gaju — strażnik), **poziom**
   (1 / 5 / 10 — obu stron) i **WALCZ!**. Panel zamyka krzyżyk albo odejście od tablicy. Gdy serwer odmówi walki
   (np. za daleko od tablicy), gracz dostaje komunikat z powodem: przy tablicy w panelu, dalej w dymku na ekranie.
5. Walka: paski życia z nazwą, poziomem i rangą, ikony efektów z licznikiem tur, licznik tury, wstęga z nazwą
   umiejętności. Na dole **×1 / ×2 / ×4** (tempo, wybór gracza), przycisk **dźwięku** (głośnik / wyciszone) i **POMIŃ**
   (albo spacja). Na końcu panel wyniku
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
przy krytyku (0,7 s sceny w tempie 0,22, jak w v1) i przy ciosie kończącym walkę; przy ataku z lotem (pocisk, chmura,
bańka) zwolnienie zaczyna się dopiero w chwili dolotu (etap 7 — wcześniej 0,28 s przed trafieniem, więc pocisk
dolatywał ok. 1,2 s i wyglądał, jakby stał przed celem). Klipy aktorów, ruch, pociski i efekty
liczą się w czasie sceny, więc tempo i zwolnienie działają na wszystko naraz. Obsługa zdarzeń:

| Typ zdarzenia | Co widać |
|---|---|
| `cios` / `krytyk` / `blok` / `unik` | doskok (z zasięgu broni w chwili trafienia i głębokości piersi celu), klip ataku dopasowany prędkością tak, by trafienie wypadło w chwili z dziennika; odrzut, klip trafienia, iskry, liczba; krytyk: zwolnienie, „wjazd” kamery, gwiazda „KRYTYK!”; blok: klip bloku Wojownika z tarczą, niebieskie iskry; unik: klip uniku i ślizg w bok, pocisk mija cel |
| `umiejetnosc` | wstęga z nazwą (z danych silnika) i choreografia stylu z `Choreografie.luau` (tabela niżej) |
| `efekt_nalozony` | napis = nazwa efektu z danych silnika („SPOWOLNIENIE!”, „ZDARTY PANCERZ!”), ikona z licznikiem tur pod paskiem, ozdoba na postaci do końca efektu; tarcza: zapas na pasku |
| `efekt_tick` | liczba w kolorze efektu, puls ozdoby, drgnięcie; tarcza pochłaniająca: „TARCZA −n” |
| `efekt_koniec` | znika ikona i ozdoba; pęknięta tarcza: „TARCZA PĘKŁA!” |
| `utrata_tury` | „TRACI TURĘ!”, chwianie się i ozdoba spowolnienia: lód przy lodowym pocisku, pnącza przy uścisku korzeni, gwiazdki przy ogłuszeniu |

**Napisy (etap 6, D3; etap 7 przebudowane)** idą przez kolejkę w `InterfejsWalki2`: przy jednej postaci najwyżej 3 naraz,
kolejne wchodzą co 0,12 s (liczba obrażeń przed resztą; gdy czeka dłużej niż 0,3 s, najstarszy inny napis gaśnie
wcześniej). Napisy jednej postaci tworzą stos w kolejności wejścia (nowy na końcu, nikt się nie przesuwa). Miejsce w
stosie liczy się z rozmiaru **narysowanego**: prawdziwa szerokość tekstu w czcionce (`TextService`, ok. 0,37 wysokości
na znak — wcześniej 0,6, więc stos rezerwował o 60% za szerokie miejsce), obrót napisu (długie napisy obracają się
mniej), gwiazda „KRYTYK!” w każdym obrocie (kwadrat 1,15 wysokości → przekątna 1,63), obrys, cień i powiększenie przy
wejściu (1,08). Miejsce zwalnia się dopiero, gdy napis całkiem zgaśnie; dalsze napisy dojeżdżają wtedy płynnie, ale
nigdy nie wchodzą na poprzedni. Miejsce całego stosu wybiera ocena kandydatów (`_miejsceStosu`): nad postacią, obok niej
(dalej / bliżej przeciwnika), pod nią, a przy dużym celu (≥ 40% wysokości kadru) także na sylwetce przy zewnętrznym
brzegu. Twarde kary: poza kadrem, tabliczki z paskami, VS i licznik tury, wstęga umiejętności, baner, przyciski, drugi
stos, **własna mała postać** (każdy napis, nie tylko liczba), **głowa** dużej postaci (górna ćwiartka jej walca), mała
druga postać; miękkie: odległość, nachodzenie na dużego przeciwnika i na sylwetkę dużego celu, zmiana miejsca
(stos nie skacze). Gdy żaden kandydat nie jest wolny od twardych kar, napisy tej postaci maleją do 0,85, potem 0,7.
Kotwica postaci to rzut jej walca (szerokość × głębokość), a nie narożników pudła (z ukosa poszerzały postać o ok. 40%).
Stos z liczbą obrażeń układa się pierwszy, drugi go omija. Przy ×2/×4 napisy żyją krócej (0,85/0,7). Odtwarzacz liczy
w każdej walce na narysowanych prostokątach: najwięcej napisów przy postaci, klatki z nakładaniem, z napisem na własnej
małej postaci i na drugiej małej postaci, największy ułamek głowy dużej postaci pod napisami (atrybuty `OstatnieNapisy*`).

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
| Zatruta strzała | pocisk | duża strzała (jasne drzewce, świecący zielony grot z dwóch klinów, czerwone lotki na krzyż) z szeroką zieloną smugą, lot 0,45–0,7 s lekkim łukiem; od etapu 7 grot kończy lot na przedniej powierzchni celu (promień z łuku do piersi przecięty z bryłami celu, koniec liczony ze stycznej łuku) i strzała zostaje wbita 0,75 s (jedzie z celem przy odrzucie, potem gaśnie); słabe zielone światło (zasięg 3, gaśnie przy dolocie). Kamera zza łucznika z drugiej strony niż plan ogólny (`stronaKamery = -1`), w locie przechodzi w skos na obu; w tle tego ujęcia widać zabudowania wioski i ciemne tablice spoza areny (nie las — opis „od strony lasu” był błędny), zielony rozbłysk, bąbelki trucizny |
| Skupienie | na siebie | złoty rozbłysk, złoty krąg pod stopami i iskry |
| Kula ognia (Mag) | pocisk | kula z ogniem i światłem leci z kostura, wybuch, potem ogień na celu (podpalenie) |
| Lodowy pocisk | pocisk | lodowy kryształ z rdzeniem, lodowy rozprysk; przy spowolnieniu „SPOWOLNIENIE!”, lodowe kryształy przy nogach, szron i lód pod stopami |
| Bariera | na siebie | niebieska bańka (ForceField) wokół Maga, pulsuje przy pochłanianiu |
| Zwykły atak Maga | pocisk | mała fioletowa iskra z kostura (atak Maga jest magiczny) |
| Kwaśny plusk (Slime) | w klipie | klip modelu: nadyma policzki, pluje świecącą bańką, kałuża kwasu — bańka i kałuża sięgają do celu (wydłużenie w biegu); od etapu 6 lot bańki trwa ok. 0,55 s (klip gra ten odcinek wolniej), ze smugą i poświatą, przy celu duży rozprysk, fala i płaski dysk kwasu na ziemi tak długo, jak kałuża w klipie (ok. 1,1–1,4 s); zdarty pancerz |
| Rozszarpanie (Wilk) | wręcz | skok z klipu, trzy czerwone ślady pazurów, potem krople krwawienia |
| Chmura zarodników (Muchomornik) | chmura | fioletowa chmura płynie z kapelusza i otula cel, potem trucizna |
| Ogłuszające uderzenie (Troll) | wręcz | fala uderzeniowa, często spowolnienie (gwiazdki nad głową, utrata tury) |
| Uścisk korzeni (Strażnik Gaju) | w klipie | klip modelu: ryk, pięści w ziemię, pięć korzeni z klipu wyrasta pod celem (przesunięte w biegu pod cel) i zaciska się; cel bez odrzutu, uniesiony, póki korzenie trzymają; spowolnienie = pnącza wokół nóg |

**Kamera** — ujęcia planowane na zdarzenia (deterministycznie z ziarna, więc ta sama walka ma te same ujęcia):
plan ogólny (co piąty zwykły cios i na start), z boku 3/4, zza atakującego, zza broniącego, zbliżenie celu, krytyk
(niska kamera, zwolnienie, „wjazd”), lot pocisku, umiejętność na siebie, efekt / utrata tury, objazd zwycięzcy w finale.
Odległości liczone z wysokości i szerokości aktorów (Leśny Slime 3,4 – Strażnik Gaju 14,6 studa). Przeciw nudzie
i szarpaniu: zwykłe ujęcie trwa co najmniej 0,9 s czasu rzeczywistego (×1,6 przy tempie ×2/×4, ×1,5 po 12. turze),
po 12. turze kamera zmienia ujęcie tylko co drugie zdarzenie, a przy ×2/×4, w długiej walce i przy tym samym typie
ujęcia przechodzi płynnie (0,45 s) zamiast ciąć. Zza pleców dużo większego aktora (ponad 1,3×) albo przy różnicy
wzrostu ponad 1,8× kamera bierze ujęcie boczne. Etap 5: przy parze wyższej niż 8 studów (Troll, Strażnik Gaju) ujęcia
boczne, krytyk, zbliżenie, efekt i objazd stoją tak daleko, żeby korona była pod tabliczkami z paskami (zasłaniają ok.
22% kadru u góry), a „wjazd” przy krytyku kończy się na tej granicy; gdy atakujący jest olbrzymem (ponad 1,8× wyższy),
zbliżenie celu zamienia się w ujęcie boczne, a skos boczny idzie od strony celu (inaczej bryła Strażnika zasłania
Zwiadowcę); ujęcie boczne poszerza kadr, aż oba brzegi pary mieszczą się mimo skosu (szeroki slime bywał ucięty).

Kadr liczony z **bieżących** położeń aktorów (poprawka po przeglądzie): ujęcia krytyk i boczne obejmują obu aktorów
tam, gdzie są teraz — po doskoku, w powietrzu i po odrzucie — a „wjazd” przy krytyku zwęża kąt tylko do kadru,
w którym obaj się mieszczą. Uderzenie z góry ma zawsze ujęcie z boku (widać cały łuk wyskoku). Lot pocisku: przy
wypuszczeniu kamera jest zza ramienia strzelca (odsunięta w bok tak, żeby cel nie chował się za jego bryłą), a w
czasie lotu przechodzi w skos 3/4 na obu, więc w chwili trafienia cel jest duży i odsłonięty. Atak zaraz po ujęciu
jednej postaci (umiejętność na siebie, efekt) zawsze dostaje własne ujęcie — wcześniej w długiej walce kamera potrafiła
zostać na samym rzucającym. Pilnuje tego `testy/test_poprawek_play.py` (część `kadr`).

**Twarz potwora (etap 6, D5; etap 7 z pilnowaniem gracza).** Ujęcia „zza pleców” są zawsze zza gracza (zza potwora
widać tylko jego plecy), ujęcie boczne przy ataku potwora stoi od strony gracza, a po policzeniu każdego ujęcia (poza
objazdem, ujęciem pokonanego i ujęciami samego gracza) kamera obraca się wokół punktu, na który patrzy, aż **kąt twarzy**
potwora (kąt w poziomie między kierunkiem, w którym patrzy potwór, a kierunkiem do kamery; 0° = w twarz, 90° = profil)
jest ≤ 56° — ujęcie 3/4 od strony gracza. Etap 7 (przegląd: po obrocie Wojownik stał ogromny na pierwszym planie, tyłem,
ucięty krawędzią kadru): kamera wybiera z 36 kandydatów (obrót 100–0% × odjazd 1,0–1,8) najtańszy, w którym gracz ma
≥ 62% punktów próbnych w kadrze (≥ 72%, gdy potwór bije gracza), potwór ≥ 65%, gracz nie jest bliżej kamery niż 0,85
odległości potwora, nie zajmuje więcej niż 60% wysokości kadru, czubek jego głowy jest co najmniej 10% pod górną
krawędzią, a potwór nie chowa się za graczem (≥ 70% odsłonięty). Wybór co 0,1 s, wygładzany. Pomiar:
`test_dopieszczenia_play.py` część `twarz` (kąt i gracz w kadrze) i atrybut `OstatnieKatyTwarzy` (kąt w chwili każdego
trafienia w zwykłej walce oraz ułamek gracza i potwora w kadrze).

**Finał (od etapu 6):** cios kończący (zwolnienie), potem **ujęcie pokonanego** z góry 3/4 (od strony zwycięzcy i widza,
kadr z obwiedni ostatniej klatki upadku — `lezy` w tabeli aktorów, liczone w `zbuduj.py`), w którym kończy się jego klip
upadku (kałuża z oczkami, stos głazów, leżący troll albo bohater; klip dłuższy niż 1,9 s gra szybciej, Strażnik ×1,4);
ujęcie trwa 1,25–1,8 s. Dopiero potem radość zwycięzcy (`radosc`) — od etapu 7 zwycięzca w ciągu 0,45 s obraca się
w stronę kamery objazdu (kąt twarzy ok. 35°; wcześniej, gdy leżący wymuszał duży kąt objazdu, wiwat było widać od
tyłu, a panel wyniku stał na tle pleców) — objazd kamery, baner z krótką melodią, przy wygranej
wysypany łup (monety, żetony lasu, Gem, kryształ Shardu) i panel wyniku: Złoto, doświadczenie, tokeny krainy, Gem, Shard
Ewolucji (zera wyszarzone), podtytuł z liczbą tur, stopka z ziarnem i czasem dziennika. Objazd nie wjeżdża w leżącego:
kąt objazdu jest dobierany tak, żeby kamera była poza obwiednią leżącego (z zapasem), widok na zwycięzcę jej nie
przecinał, a szczątki były od kamery co najmniej tak daleko jak zwycięzca (0,95) — stos głazów Strażnika nie wchodzi na
pierwszy plan. Od chwili tuż przed ciosem kończącym scena gra **zawsze w ×1** (przy ×2/×4 ujęcie pokonanego trwałoby
ułamek sekundy); cały dziennik jest już odegrany, więc to wybór odtwarzacza, nie silnika. Scena kończy się w
`czasKonca` = radość + tyle, ile silnik przewidział po ostatnim zdarzeniu (≥ czas dziennika).

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

- **Aktor** (wzór: Leśny Slime i Strażnik Gaju z etapu 5): wpis w `AKTORZY` w `aktorzy.py` (model, klipy na akcje,
  umiejętności, punkty, `chwile` z notatki modelu, `zastepczy = None`) → `aktorzy.py --tylko <klucz>` → `zbuduj.py`
  (nowy aktor: pełna budowa, żeby galeria się przesunęła). Zasięg broni i pierś do doskoku liczy `zbuduj.py` sam
  z danych; gdy klip „trafia” dalej niż punkt `Bron` (kałuża, korzenie), wpisz `zasiegi`. Efekt, który jest w klipie
  (bańka, korzenie), a ma sięgnąć celu stojącego dalej: `wydluzenia` (kości i klatki) + styl `w_klipie` w choreografii.
  Bryły schowane w modelu tuż pod ścianą (prześwitują na rigu z klocków): `chowane` (kość → kierunek na zewnątrz,
  próg). Inny materiał albo kolor tylko w prototypie (bez Blendera): `wyglad_roblox`.
  Skórowanie modelu (`p.skoruj`) przechodzi samo (opis w `aktorzy.py` i `Klipy.luau`). Portret w interfejsie: ikona
  8×8 o tym kluczu w `IKONY` w `InterfejsWalki2.luau` (test pilnuje, że jest).
- **Umiejętność:** po dopisaniu do `tools/walka/dane_walki.json` dopisz wpis w `Choreografie.UMIEJETNOSCI` (styl i
  dodatki: `pocisk`, `wybuch`, `smuga`, `fala`, `pazury`, `aura`, `kamera`) oraz klip w tabeli aktorów.
  `testy/test_odtwarzacza.py` i `testy/test_aktorow.py` nie przejdą, dopóki umiejętność nie ma wpisu — nie zostanie
  po cichu bez animacji. Gdyby w grze trafiło się coś bez wpisu, odtwarzacz gra styl zastępczy i liczy to
  w `OstatnieBrakiChoreografii`.
- **Efekt w klipie modelu** (bańka, korzenie, fala z klipu): styl `w_klipie` (`Choreo.w_klipie`) — bez pocisku
  i ozdób z `Efekty3D`; pola `punkt` (gdzie rozbłysk), `celPrzod`, `puszcza` opisuje `Choreografie.luau`.
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
| `zrodla/Ustawienia.luau`, `Klipy.luau`, `Aktorzy.luau` | z etapu 1 (stałe, odtwarzacz klipów z danych, lokalne klony aktorów); etap 5: `Klipy` udaje skórowanie siatką (galareta slime'a) i wydłuża efekt z klipu (`graj(…, { wydluz = studs })`); etap 6: `Klipy` gra odcinki klipu z własną prędkością (`odcinki`, lot bańki) i chowa bryły schowane w klipie (`chowane`), `Ustawienia` ma listę dźwięków i melodie, `Aktorzy` nie daje skorupy bryłom skóry |
| `zbuduj.py` | odtwarza kontener w Studio (`--skrypty`, `--tylko-aktorzy`, `--sucho`, `--usun`) |
| `aktorzy.py`, `przerobki.py`, `geometria.py`, `dane/` | tabela aktorów (etap 5: skóra, `zasiegi`, `wydluzenia`; etap 6 u slime'a: `chowane`, `wyglad_roblox` — materiał i kolory tylko na rigu z klocków, bez Blendera), klipy dorobione Rycerzowi, Kotu-Magowi i Zwiadowcy, kinematyka, dane rigów |
| `testy/test_odtwarzacza.py` | testy bez Studio (pokrycie choreografii, dzienniki z portu, tury, efekty, paski) + `--ziarna` |
| `testy/sprawdz_edit.py` | tryb Edit, tylko odczyt: moduły się wczytują, serwerowa postać wzorcowa + kopia silnika = Python |
| `testy/test_walki_play.py` | pełny test w trybie Play (wynik w `testy/wynik_play.json`) |
| `testy/test_poprawek_play.py` | test Play poprawek po przeglądzie: kadr kamery w chwili trafienia, „−0”, napis i wygląd spowolnienia, odmiana w panelu wyniku, komunikat odmowy, paski / tura / ikony efektów na ekranie = stan silnika (wynik w `testy/wynik_poprawek.json`) |
| `testy/test_dopieszczenia_play.py` | etap 6–7: test Play poprawek D1–D7 i uwag przeglądu (finał z twarzą zwycięzcy, lot pocisków w czasie „jak w grze” z zasłanianiem strzały, napisy klatka po klatce w całych walkach, twarz potwora z graczem w kadrze, dźwięki, slime w upadku, tempo ×2/×4 z wilkiem) → `testy/wynik_dopieszczenia.json` |
| `testy/film_walki.py` | film MP4 z jednej całej walki (zapis poklatkowy, krok = czas „jak w grze”: zwolnienia, finał w ×1) → `klatki/film_*.mp4` |
| `testy/telefon.py` | emulacja ekranu telefonu w poziomie: zrzuty `klatki/telefon_*.jpg` i wysokość napisów w punktach (`klatki/raport_telefonu.json`) |
| `testy/klatki_walki.py` | arkusze klatek z prawdziwego odtwarzania → `klatki/walka_*.jpg` (etap 5: też pełna walka ze Slime'em i ze Strażnikiem; etap 6: finały z ujęciem pokonanego, lot strzały i bańki, tury z kilkoma napisami — chwile liczone z czasów odtwarzacza) |
| `testy/sesja_play.py`, `testy/proba_play.py` | wspólna obsługa sesji Play; próba jednej walki (arkusz albo odtworzenie na żywo) |
| `testy/ziarna.json` | ziarna pokazowe i testowe (z `test_odtwarzacza.py --ziarna`) |
| `testy/test_aktorow.py`, `test_klipow_play.py`, `klatki_aktorow.py`, `zrzut_edit.py`, `czuwanie.py` | z etapu 1 (`klatki_aktorow.py --przod`: klipy z przodu 3/4 — twarz i miny) |

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
python -B swiat/test_walki2/testy/test_dopieszczenia_play.py      # tryb Play, ok. 3 min (etap 6–7; --tylko final,lot,napisy,twarz,dzwiek,slime,tempo)
python -B swiat/test_walki2/testy/film_walki.py [--klasa … --przeciwnik … --poziom … --ziarno …]   # film MP4, 4–7 min
```

**Etap 7 (15.11, poprawki po przeglądzie etapu 6, końcowy kod, Studio na PC):** `test_odtwarzacza.py` **9/9** (2700
dzienników), `test_aktorow.py` **6/6**, `sprawdz_edit.py` **OK** (10/10 modułów, 45/45 walk = Python),
`test_klipow_play.py` **24/24**, `test_walki_play.py` **112/112 w pierwszym przebiegu** (1f bez fałszywego błędu),
`test_poprawek_play.py` **29/29**, `telefon.py` **0 napisów poniżej 12 punktów**, **`test_dopieszczenia_play.py` 38/38**
(8 finałów, 6 lotów, 9 przypadków napisów w tym 5 całych walk klatka po klatce, 5 potworów × kąt twarzy i gracz w
kadrze, dźwięki, slime w upadku, 6 pełnych walk przy ×2/×4), 34 arkusze klatek, zrzuty do raportu i 5 filmów nagrane
na końcowym kodzie i obejrzane; konsola bez komunikatów z `TestWalki2`. Studio po każdym teście w trybie Edit.

**Etap 6 (15.11, „dopieszczenie” D1–D8, końcowy kod, wszystko na Studio w PC):** `test_odtwarzacza.py` **9/9** (2700
dzienników), `test_aktorow.py` **6/6**, `sprawdz_edit.py` **OK** (10/10 modułów, 45/45 walk = Python),
`test_klipow_play.py` **24/24**, `test_walki_play.py` **112/112** (pierwszy przebieg 111/112: punkt 1f „kamera Custom po
ZAMKNIJ” — znana pułapka narzędzia `execute_luau`, opisana niżej; powtórka 112/112), `test_poprawek_play.py` **29/29**,
`telefon.py` **0 napisów poniżej 12 punktów** (po poprawce narzędzia: pomiar po zakończeniu animacji wejścia napisu),
**`test_dopieszczenia_play.py` 27/27**, `zrzuty_raportu.py` i `klatki_walki.py` (34 arkusze) odświeżone i obejrzane,
konsola bez komunikatów z `TestWalki2`. Studio po każdym teście w trybie Edit.

**Etap 5 (15.11, po podmianie modeli, pełna przebudowa kontenera, końcowy kod):** `test_odtwarzacza.py` **9/9**
(2700 dzienników), `test_aktorow.py` **6/6**, `sprawdz_edit.py` **OK** (10/10 modułów, 45/45 walk = Python),
`test_klipow_play.py` **24/24** (klony obu nowych aktorów grają spoczynek, mają punkty), `test_walki_play.py`
**112/112**, `test_poprawek_play.py` **29/29** (kadr: kwaśny plusk i uścisk korzeni w stylu `w_klipie`, każde
trafienie 24- i 33-turowej walki ze Strażnikiem Gaju — pierwszy przebieg dał 28/29: zbliżenie celu pod olbrzymem
i unik zasłonięty przez Strażnika, poprawione regułą „olbrzym” w kamerze), `telefon.py` **0 napisów poniżej
12 punktów**; silnik: `tools/walka` 41/41, `zgodnosc_studio.py` 496/496 i 38/38 (po zmianie nazwy strażnika). Klatki
odświeżone i obejrzane (14 umiejętności, finały, pełna walka z każdym nowym aktorem, arkusze aktorów z boku i slime'a
z przodu). Studio po każdym teście w trybie Edit.

Wyniki 15.11 (etap 4): `test_odtwarzacza.py` **9/9**, `test_aktorow.py` **6/6**, `sprawdz_edit.py` **OK** (10/10 modułów,
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

## Dopieszczenie (etap 6, 15.11.2026) — lista D1–D8 po obejrzeniu filmów

| Uwaga | Co zmienione | Czym sprawdzone (wynik) |
|---|---|---|
| D1 finał: od razu objazd zwycięzcy, pokonanego prawie nie widać | ujęcie `pokonany` po ciosie kończącym (1,25–1,8 s, koniec klipu upadku w ujęciu), dopiero potem radość, objazd, baner, łup, panel; objazd z kątem dobranym tak, by nie wjeżdżał w leżącego i nie miał go na pierwszym planie; duży zwycięzca dalej i bliżej środka kadru | `test_dopieszczenia_play.py` `final`: 8 finałów (wygrana / przegrana × Slime, Strażnik, Troll, Muchomornik) — ujęcie pokonanego 1,25–1,80 s, pokonany w kadrze, upadek skończony przed radością, w objeździe zwycięzca w kadrze i odsłonięty, szczątki ≥ 1,0 odległości do zwycięzcy; arkusze `walka_final_*.jpg` |
| D2 pociski za szybkie | lot pocisku 0,45–0,7 s (niższe prędkości w `Choreografie`, granice w odtwarzaczu), większa strzała; bańka kwasu: klip gra lot (kl. 21–31) wolniej, do wypuszczenia szybciej, po trafieniu ×1 — trafienie dalej w chwili z dziennika; smuga i poświata bańki, większy rozprysk, fala i dysk kwasu na ziemi | `lot`: strzała widoczna 0,55 s, pasek celu zmienia się w τ = 10,199 przy trafieniu z dziennika τ = 10,20; bańka leci 0,55 s (8,1 studa), dolatuje 0,02 s przed trafieniem, dysk kałuży 1,42 s; arkusze `walka_lot_strzaly.jpg`, `walka_lot_banki_kwasu.jpg` |
| D3 napisy nachodzą na siebie i na mały cel | kolejka, najwyżej 3 przy postaci, stos przy kotwicy postaci (opis w „Jak to działa”) | `napisy`: 4 tury z kilkoma napisami (tarcza, umiejętność + efekt, krytyk, tyknięcie + utrata tury), 56 klatek każda: 0 nakładań, 0 liczb na małym celu; pełne walki ×2/×4: `OstatnieNapisyNakladania` 0, `NaCelu` 0, najwyżej 3 przy postaci; arkusze `walka_napisy_*.jpg` |
| D4 dźwięk | 13 dźwięków z 7 wbudowanych plików (lista i uczciwy opis w `Ustawienia.luau`), głośność wyrównana do szczytów plików, melodia zwycięstwa / porażki z czterech „nut”, kliknięcia; najwyżej 3 naraz i ta sama nazwa nie częściej niż co 0,06/0,1/0,16 s (×1/×2/×4); przycisk wyciszenia obok POMIŃ (wybór zostaje do końca sesji gry) | `dzwiek`: każdy z 13 wpisów wczytuje się w kliencie (`IsLoaded`, długość > 0); klik w przycisk → wyciszone (atrybut i ikona), drugi klik → z powrotem; pełne walki: najwyżej 3 dźwięki naraz. **Dźwięków nie słyszałem** (test sprawdza wczytanie i liczbę naraz, nie brzmienie) |
| D5 twarze potworów | ujęcia zza gracza, boczne od strony gracza, obrót kamery do kąta twarzy ≤ 56°, odjazd, gdy gracz zasłaniałby cel | `twarz`: każde trafienie walki z każdym z 5 potworów (54 trafienia): kąt średnio 51–55°, najwięcej 57° (było zwykle 70–90°), nikt poza kadrem; w zwykłych walkach przy ×4 pojedyncze trafienie w trakcie płynnego przejścia kamery ma do 72°; `test_poprawek_play.py` `kadr` dalej 29/29 (zasłanianie, obie postacie w kadrze) |
| D6 slime ciemny i szklisty, „soczewki” | `wyglad_roblox` w tabeli aktorów: Glass → SmoothPlastic, galareta #8CE865, kropelki #BDF58F (plik modelu bez zmian); `chowane`: brzuszki BokL/BokP/Przod/Tyl niewidoczne, póki klip nie wysunie ich o > 0,05 studa albo nie obróci (płaty kałuży) | `slime`: w spoczynku 4/4 brzuszki schowane, po upadku 4 płaty widoczne, 0 brył Glass; zrzuty slime'a na arkuszach i w filmach |
| D7 tempo ×2 nietestowane, finał przy ×4 | finał zawsze w ×1 | `tempo`: pełna walka ×2 (24 tury) i trzy ×4 — wszystkie zdarzenia, 0 braków, 0 błędów, 0 niezgodności pasków, ujęcie pokonanego 1,53–2,13 s czasu rzeczywistego, upadek w ujęciu |
| D8 skorupa przy zgniatanej galarecie | bryły skóry (atrybut `Skora`) nie dostają skorupy — sztywna kopia rozmiaru spoczynku wystawałaby przy przysiadzie i w kałuży | sprawdzenie w trybie Edit: klon slime'a w trybie `skorupa` — 0 skorup na 23 bryłach skóry. Skutek: w trybie `skorupa` slime nie ma obrysu wcale (pozostałe jego bryły to kule, walce albo cieńsze niż próg); `highlight` działa (domyślny tryb to `brak`) |

## Poprawki po przeglądzie etapu 6 (etap 7, 15.11.2026)

Przegląd obejrzał cztery całe walki (filmy co 0,1–0,3 s) i zgłosił 12 uwag. Wszystkie przyjęte (uwaga o tle ujęcia
strzały — poprawiony opis, nie ujęcie). Do każdej poprawki jest test w `testy/test_dopieszczenia_play.py` albo
`testy/test_walki_play.py`.

| Uwaga przeglądu | Co zmienione | Czym sprawdzone (wynik) |
|---|---|---|
| D2: przy krytyku pocisk ok. 1,1–1,3 s „stoi” przed celem (zwolnienie 0,28 s przed trafieniem w tempie 0,22) | `Choreografie.ZWOLNIENIE.lot`: przy ataku z lotem (pocisk, chmura, bańka) zwolnienie krytyka i nokautu zaczyna się w chwili dolotu (rampa 0,03 s) | `lot`: pięć lotów w czasie „jak w grze” — strzała przy Slimie, krytyk strzałą przy Strażniku (325002 zd. 7) i Trollu (950601 zd. 12), iskra Maga i lodowy pocisk przy Slimie (63518 zd. 1 i 10): od chwili, gdy pocisk jest ≤ 0,5 studa od powierzchni celu, do zmiany paska 0,07–0,12 s czasu rzeczywistego (próg 0,15); film 325002: strzała przy krysztale i pasek 960 → 674 w tej samej klatce |
| D2: strzała celowała w punkt Piers w środku bryły — przy Trollu znikała w ciele na 1,4 s | lot kończy się na przedniej powierzchni celu (promień przecięty z bryłami celu), środek strzały liczony ze stycznej łuku tak, by grot dotknął powierzchni; strzała zostaje wbita 0,75 s i jedzie z celem | `lot`: strzała przy celu nie jest zasłonięta przez cel w żadnej klatce ostatnich 0,2 s przed trafieniem (promień z kamery do drzewca i lotek; Slime, Strażnik, Troll — 0/12 klatek) |
| D2: zielone światło strzały barwi cel | `PointLight` strzały: zasięg 7 → 3, jasność 2,5 → 1,2, gaśnie w ostatnich 45% lotu, po wbiciu wyłączone | `lot`: jasność światła w ostatnich 0,1 s lotu ≤ 0,35 (zmierzone 0,02), zasięg ≤ 3,5 |
| D3: napisy wchodzą na siebie w animacji wejścia i wygaszania; test liczył tylko prostokąty po ułożeniu | stos z narysowanego rozmiaru, kolejność wejścia, miejsce zwalniane po zgaśnięciu (opis w „Jak to działa”); pomiar w odtwarzaczu na narysowanych prostokątach | `napisy`: 4 tury z kilkoma napisami i 5 CAŁYCH walk klatka po klatce co 1/30 s czasu „jak w grze” (wilk z Wojownikiem i z Magiem, Strażnik ze Zwiadowcą przy ×1, Mag z wilkiem i Wojownik ze Slime'em przy ×4) — 0 klatek z nakładaniem |
| D3: zakaz przykrywania małego celu tylko dla liczb | twarda kara dla każdego napisu na własnej małej postaci (i mniejsza na drugiej małej) | `napisy`: 0 klatek z napisem na własnej małej postaci we wszystkich 5 walkach |
| D3 przy ×4: walka Wojownika z wilkiem (277334) — 6 klatek z liczbą na małym celu | ocena kandydatów zamiast stałej kolejności „nad → obok → pod”; zmniejszenie stosu, gdy nigdzie nie ma miejsca | `tempo`: pełne walki przy ×4 Wojownik z wilkiem (277334) i Mag z wilkiem (910854) w zwykłym odtwarzaniu: `NaCelu` 0, nakładania 0 |
| D3: przy dużym celu stos „liczba + KRYTYK!” przykrywał głowę i pierś Strażnika | duży cel: najpierw miejsca poza sylwetką; na sylwetce tylko przy zewnętrznym brzegu i nigdy na głowie (twarda kara); kotwica z walca, nie z pudła | `napisy`: głowa Strażnika przykryta najwyżej 0–1% w całej walce 325002 (próg 20%); film 325002: „KRYTYK!” i „−286”, „−574” obok Strażnika |
| D1: radość zwycięzcy widać od tyłu (panel na tle pleców) | zwycięzca w radości obraca się do kamery objazdu (kąt twarzy ok. 35°), także po POMIŃ | `final`: 8 finałów — kąt twarzy zwycięzcy od 0,5 s radości 35° (próg 60°); szczątki ≥ 1,00 odległości zwycięzcy |
| D5: po obrocie do twarzy gracz ogromny na pierwszym planie i ucięty | kandydaci (obrót × odjazd) z warunkami: gracz w kadrze, nie bliżej niż 0,85 odległości potwora, ≤ 60% wysokości kadru, głowa w kadrze, potwór odsłonięty | `twarz`: gracz w kadrze ≥ 50% przy każdym trafieniu i ≥ 60%, gdy obrywa od potwora (zmierzone najmniej 81%); kąt twarzy średnio 51–57°, najwięcej 61° (próg 62°); `test_poprawek_play.py` `kadr` dalej 29/29 |
| D6: płaty kałuży wychodziły na ścianę stojącego jeszcze sześcianu | obrócony brzuszek (płat) staje się widoczny dopiero przy rozlanej galarecie (przezroczystość od wysokości skóry 0,62 do 0,42); `Klipy` zapisuje wysokość skóry w atrybucie modelu `WysokoscSkory` | `slime`: upadek klatka po klatce (64 klatki) — 0 razy płat widoczny przy galarecie wyższej niż 62%; po upadku 4 płaty widoczne |
| test 1f „kamera Custom po ZAMKNIJ” niestabilny | po kliknięciu ZAMKNIJ test 2 s nie woła `execute_luau` (narzędzie przywraca typ kamery, jaki zastało na początku wywołania) | `test_walki_play.py` — wynik niżej |
| opis testu: próg szczątków 0,8 i „6 finałów” | próg 0,95 w kodzie i opisie, „8 finałów” | `final` |
| README: „kamera zza łucznika od strony lasu”, a w tle wioska | poprawiony opis w tabeli umiejętności (ujęcie bez zmian) | — |

**Tryb poklatkowy (testy, arkusze, filmy) od etapu 6 liczy czas „jak w grze”:** napisy, przejścia kamery i wstrząs
starzeją się tylko przy przewijaniu, w czasie przeliczonym na ×1 (`przewin` = czas rzeczywisty z tempem i zwolnieniem,
`przewinDo` = czas sceny przeliczony przez tempo i zwolnienie). Wcześniej starzały się w czasie rzeczywistym robienia
zrzutów, więc w filmie napis znikał po 1–2 klatkach, a przejścia kamery były cięciami. `film_walki.py` przesuwa teraz
czas przez `przewin` (zwolnienie przy krytyku i finał w ×1 są w filmie jak w grze).

## Właściwe modele (etap 5, 15.11.2026)

Dwa modele zastępcze (przemalowany slime-pet i powiększony troll) zastąpiły modele z `swiat/postacie/` — pliki modeli
nie są zmieniane, prototyp tylko je czyta (`przerobki.py` nie ma już dla nich funkcji).

| Aktor | Model | Klipy (akcja → klip) | Chwile trafienia (z notatek modelu) | Punkty |
|---|---|---|---|---|
| Leśny Slime (`lesny_slime`) | `lesny_slime.py` w. 3: sześcian 2,7 studa, z kiełkiem 3,4 studa; 115 brył, 27 kości | spoczynek `idle`, ruch `ruch`, atak i krytyk `atak`, unik `unik`, trafienie `trafienie`, upadek `upadek`, radość `wiwat`, kwaśny plusk `umiejetnosc` (blok: brak) | pacnięcie kl. 13 (0,43 s), plusk kałuży kl. 31 (1,03 s) | Bron = dół przedniej ściany, Piers = środek przedniej ściany, Pocisk = buzia, Plusk = kałuża |
| Strażnik Gaju (`straznik_lasu`) | `straznik_gaju.py`: kolos 14,6 studa z koroną; 1128 brył, 36 kości | spoczynek `idle`, ruch `ruch`, atak i krytyk `atak`, unik `unik`, trafienie `trafienie`, upadek `upadek`, radość `ryk`, uścisk korzeni `umiejetnosc` (blok: brak) | pięść kl. 17 (0,57 s), zaciśnięcie korzeni kl. 50 (1,67 s) | Bron = prawa pięść, Piers i Pocisk = kryształ, Korzenie = środek uścisku |

Skala 1,0 (wymiary jak w modelach). Napisy nad głową i „Pasek” liczą się z wysokości modelu (`pasek` = wzrost + 0,9).

**Efekt w klipie zamiast osobnego pocisku (styl `w_klipie`).** Bańka kwasu (kość `Kula`), kałuża (`Plusk`) i pięć
korzeni (`K1A…K5A` z członami) są w klipach modeli. Odtwarzacz nie puszcza już zielonej kuli ani korzeni z
`Efekty3D` (nic się nie dubluje): atakujący stoi na miejscu, a moduł Klipy przesuwa w biegu te kości do przodu
(`wydluzenia` w `aktorzy.py`, opcja `wydluz` klipu) o tyle, o ile cel stoi dalej niż w klipie — bańka leci dłuższym
łukiem i rozpryskuje się kałużą przy przodzie celu (rozprysk `kwas` na kałuży), korzenie wyrastają pod celem
(przesunięcie = odstęp aktorów − 6,6 studa). Cel w korzeniach nie dostaje odrzutu, jest lekko uniesiony, póki klip
go trzyma (do kl. 66). Chwila trafienia = chwila z notatki modelu, klip jest dopasowany do niej prędkością.

**Upadek** obu modeli kończy się leżeniem (kałuża z oczkami / stos głazów): klip upadku gra bez „potem”, więc stoi
ostatnia klatka (także po POMIŃ). **Unik slime'a** ma pełny piruet (0° → 360°): klatki są przeliczane na CFrame
i mieszane obrotem (Lerp), a ostatnia klatka 360° = 0°, więc slime nie odkręca się z powrotem (sprawdzone na danych:
kąt rośnie co klatkę o ≤ 47°, kończy na 360°, i na arkuszu `lesny_slime_unik.jpg`).

**Skórowanie galarety slime'a.** Droga klockowa nie ma wag skóry (galareta szłaby sztywno za kością `Dol`, więc slime
by się nie zgniatał, a w upadku oczy chowałyby się w nierozlanym sześcianie). Teraz 23 bryły skóry (galareta,
rumieńce, odblask, rzuty liścia i grzybka) mają `SpecialMesh`, a `Klipy` co klatkę przesuwa i rozciąga ich siatkę
w pionie wg przesunięcia kości `Gora` — to samo, co liniowe wagi Blendera dla brył w całości między y0 i y1.
Działa: przysiady, rozciąganie przy plusku i rozlanie w kałużę 0,5 studa (`lesny_slime_upadek_przod.jpg`).
**Miny** (pięć wersji oczu, cztery ust, nadęte policzki) to podmiana brył na własnych kościach — działa na rigu
z części bez zmian (`lesny_slime_*_przod.jpg`: oczy „> <”, łuki, wielkie oczy, buzia „o”, oczka na kałuży).

**Kamera przy dużym aktorze** (opis w „Kamera” wyżej): korona Strażnika ma stać pod tabliczkami z paskami, olbrzym
nie zasłania małego celu w ujęciu bocznym, a szeroki slime nie jest ucinany z brzegu kadru.

## Pomiary (PC ze Studio — **nie telefon**)

**Etap 7 (`test_walki_play.py`, końcowy kod):** nasz kod na klatkę średnio **0,61–0,92 ms**, p95 1,16–2,03 ms, maks.
4,1 ms (etap 6: 0,37–0,56 ms) — więcej przez wybór ujęcia twarzy (36 kandydatów co 0,1 s, punkty próbne obu postaci)
i ocenę miejsc stosu napisów (ok. 25 kandydatów na stos co klatkę). Czasy odtworzenia jak w etapie 6 (długa walka 44,4 s,
najdłuższa przy ×4 19,8 s). Czas klatki znów nieporównywalny: Studio rysowało w tle z ograniczeniem do 15 kl./s
(66,7–66,9 ms we wszystkich walkach). Telefonu nie mierzono.

**Etap 6 (`test_walki_play.py`, końcowy kod):** czas odtworzenia przy ×1 — slime 12 tur 29,1 s (dziennik 19,8 s),
wilk 30,2 s (23,6 s), muchomornik 25,8 s (21,0 s), długa 24 tury 44,4 s (39,1 s), krótka 13,4 s (7,3 s) — ok. 1,3 s
więcej niż w etapie 5 (ujęcie pokonanego); najdłuższa walka przy ×4: 19,9 s (dziennik 47,7 s; finał w ×1). Nasz kod na
klatkę średnio 0,37–0,56 ms, p95 0,75–1,23 ms, maks. 2,35 ms (etap 5: 0,24–0,37 ms — kolejka i stos napisów, kotwice,
pomiar twarzy); instancji lokalnie 1323–3851. **Czasu klatki w tym przebiegu nie da się porównać:** Studio rysowało
w tle z ograniczeniem do 15 kl./s (średnio 66,7 ms na klatkę we wszystkich walkach, także przy krótkiej walce bez
efektów; `test_klipow_play.py` w tej samej sesji: Heartbeat 16,66 ms) — okno Studia nie było na wierzchu.

Etap 5:

Z przebiegu `test_walki_play.py` na końcowym kodzie etapu 5 (walki przy ×1; `testy/wynik_play.json`; Leśny Slime
i Strażnik Gaju to już właściwe modele):

| Walka | Czas odtworzenia (dziennik) | Klatka śr. / p95 / maks. | Nasz kod na klatkę śr. / p95 / maks. | Instancji lokalnie | Ujęć |
|---|---|---|---|---|---|
| wojownik / lesny_slime / 1, 12 tur | 27,8 s (19,8 s) | 16,69 / 17,99 / 84 ms | 0,27 / 0,50 / 1,6 ms | 1329 | 13 |
| zwiadowca / cierniowy_wilk / 5, 12 tur | 28,9 s (23,6 s) | 16,70 / 17,93 / 95 ms | 0,30 / 0,60 / 1,7 ms | 2301 | 18 |
| mag / muchomornik / 10, 10 tur | 24,7 s (21,0 s) | 16,68 / 17,92 / 50 ms | 0,24 / 0,48 / 2,1 ms | 1768 | 14 |
| długa: wojownik / straznik_lasu / 10, 24 tury | 42,8 s (39,1 s) | 16,68 / 17,92 / 58 ms | 0,37 / 0,84 / 1,9 ms | 3785 | 22 |
| krótka: mag / muchomornik / 5, 3 tury | 12,6 s (7,3 s) | 16,66 / 18,00 / 31 ms | 0,24 / 0,48 / 1,5 ms | 1257 | 4 |

Etap 5 względem etapu 4: walka ze Strażnikiem Gaju ma 3785 instancji lokalnie (było 2310 z trollem zastępczym),
a nasz kod na klatkę 0,37 ms średnio (było 0,24) — więcej kości w klipach; walka ze Slime'em 1329 instancji (było
1108; skóra liczy 23 siatki co klatkę). Klatka dalej trzyma limit 60 FPS Studia.

- Od WALCZ do pierwszej klatki walki: 154–171 ms (w tym prośba do serwera 57–78 ms i zaciemnienie).
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
| `walka_final_wygrana.jpg`, `walka_final_przegrana.jpg` | finał (cios kończący, ujęcie pokonanego, radość, baner, łup, objazd) i panel wyniku — z Shardem Ewolucji (Strażnik) i po przegranej (Muchomornik) |
| `walka_dluga_walka.jpg` | przekrój 24-turowej walki co ok. 2,4 s — zróżnicowanie ujęć (Wojownik ze Strażnikiem Gaju) |
| `walka_pelna_walka_lesny_slime.jpg`, `walka_pelna_walka_straznik_lasu.jpg` | etap 5: pełna walka z każdym z właściwych modeli, 15 kadrów od startu do końca i panel wyniku |
| `walka_panel_wyboru.jpg` | panel wyboru przy tablicy |
| `walka_final_<przeciwnik>_<wynik>.jpg` (5) | etap 6: finały ze Slime'em, Strażnikiem i Trollem (wygrane i przegrane): cios kończący, 5 klatek ujęcia pokonanego, radość i objazd, panel wyniku |
| `walka_lot_strzaly.jpg`, `walka_lot_banki_kwasu.jpg` | etap 6: lot strzały i bańki kwasu od wypuszczenia do trafienia (8 klatek) i chwila po (kałuża) |
| `walka_napisy_tarcza.jpg`, `walka_napisy_umiejetnosc_efekt.jpg` | etap 6: tury z kilkoma napisami naraz (stos, kolejka) |
| `film_*.mp4` (5) | etap 7 (nagrane na końcowym kodzie): całe walki jako filmy (10 kl./s, czas jak w grze, bez dźwięku) — `film_zwiadowca_straznik_lasu_10.mp4` wygrana ze Strażnikiem Gaju (ziarno 325002: strzała w kryształ przy krytyku, napisy obok kolosa, stos głazów), `film_mag_lesny_slime_5.mp4` wygrana Maga ze Slime'em (63518: iskra i lodowy pocisk przy krytyku, bańka kwasu, kałuża z oczkami), `film_wojownik_cierniowy_wilk_5.mp4` wygrana Wojownika z wilkiem (277334: blok, miażdżący cios, „ZDARTY PANCERZ!”, „SPOWOLNIENIE!”, „TRACI TURĘ!” obok małego wilka), `film_zwiadowca_lesny_troll_10.mp4` przegrana z Trollem (950601: strzała wbita w Trolla, leżący Zwiadowca), `film_zwiadowca_lesny_slime_1.mp4` przegrana ze Slime'em (237612) |
| `telefon_<szer>x<wys>_{panel,walka,wynik}.jpg` | emulacja telefonu w poziomie (844 × 390, 667 × 375): panel wyboru, walka z umiejętnością i efektami, panel wyniku; `raport_telefonu.json` — wysokość każdego napisu w punktach |
| `raport_1..5_*.jpg` | duże pojedyncze kadry do raportu w panelu (panel wyboru, krytyk, kula ognia w locie, spowolnienie z lodem i utratą tury, panel wyniku z łupem) |
| `raport_klatek_walki.json` | które walki i ziarna są na arkuszach |
| `lesny_slime_*.jpg`, `straznik_lasu_*.jpg` | etap 5: spoczynek z czterech stron (bok, przód 3/4, przód, tył 3/4) i każdy klip z boku (8 klatek); `lesny_slime_<klip>_przod.jpg` — te same klipy z przodu 3/4 (twarz, miny, kałuża z oczkami) |
| reszta (`<aktor>_*.jpg`, `obrys_*.jpg`) | z etapu 1: klipy aktorów i porównanie obrysu |

Uwaga do arkuszy: zdjęcia robione są przy zatrzymanym czasie sceny (narzędzie przesuwa go skokami). Od etapu 6 napisy,
przejścia kamery i wstrząs liczą się w tym samym czasie co scena (przeliczonym na ×1), więc arkusze i filmy pokazują
napisy tak, jak gra; przy dużych skokach między klatkami arkusza napis może wypaść między nimi. Pierwsze klatki tuż po starcie Play zasłaniał ekran ładowania gry — narzędzie czeka teraz, aż zniknie.

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
- **Duże modele** (Troll 10, Strażnik Gaju 14,6 studa) — kamera trzyma koronę pod tabliczkami, ale Wojownik czy Mag
  są przy Strażniku małe (1/2,5 jego wzrostu); w krytyku przy Strażniku nie ma już „wjazdu” (kadr musi objąć
  kolosa). Na niektórych kadrach korona dotyka tabliczki z rangą. Objazd po upadku Strażnika nie wjeżdża już w stos
  głazów (etap 6); żeby wiwat nie był widziany od tyłu, zwycięzca od etapu 7 obraca się w radości do kamery — przez
  pierwsze 0,45 s radości (obrót) widać go jeszcze z boku, a kamera objazdu przy dużym kącie stoi w miejscu (nie krąży).
- **Pociski** lecą od etapu 6 czytelnie (0,45–0,7 s), ale **iskry przy trafieniu** dalej są krótkie (0,3–0,5 s).
- **Napisy** (etap 7) nie nakładają się i nie leżą na swojej małej postaci ani na głowie dużej, ale gdy obok postaci nie
  ma miejsca, stos staje na dużej drugiej postaci (np. przy Strażniku na pierwszym planie) albo maleje do 0,7 — wtedy
  na telefonie 844 × 390 najmniejszy napis efektu ma ok. 22 punkty. Kolejka opóźnia trzeci i dalsze napisy przy
  postaci o 0,12 s każdy; przy ×4 napisy żyją krócej (0,7 życia). Pomiar „nakładania” liczy prostokąty otaczające
  (z obrotem i gwiazdą), a nie dokładny kształt liter.
- **Twarz potwora (etap 6–7)** — żeby widzieć twarz potwora, kamera stoi od strony gracza, więc gracz często jest
  widziany z tyłu albo z boku (od etapu 7 dalej i mniejszy, nie „wielki na pierwszym planie”). Gdy pełnego obrotu nie da
  się pogodzić z graczem w kadrze, kamera obraca się mniej — kąt twarzy dochodzi wtedy do ok. 60° (półprofil). W płynnym
  przejściu między ujęciami kąt twarzy bywa chwilowo większy (do ok. 72° przy ×4).
- **Tło ujęcia strzały** (kamera po drugiej stronie niż plan ogólny) to zabudowania wioski i ciemne tablice spoza
  areny, nie las.
- **Na prawdziwym telefonie interfejsu nie oglądałem.** Sprawdzona jest emulacja proporcji i rozmiaru w punktach
  (844 × 390, 667 × 375; `testy/telefon.py`) — to nie mierzy dotyku, gęstości pikseli ani wydajności telefonu.
  Okno Studio miało 761 × 675 px, więc emulacja 844 × 390 jest pomniejszona do 0,9.
- **Modeli zastępczych już nie ma** (etap 5). Słabe strony właściwych modeli na rigu z części Roblox (uczciwie):
  - Leśny Slime: klocki nie mają fazowania, więc to ostry sześcian (w Blenderze krawędzie są mocno ścięte); galareta
    od etapu 6 jest gładkim plastikiem w jaśniejszej zieleni (#8CE865; ściana w cieniu nadal ciemniejsza od
    oświetlonej, bo rig z klocków nie ma podpowierzchniowego światła jak render), a brzuszki są niewidoczne, póki klip
    ich nie wysunie; nadęte policzki prawie niewidoczne. Skórowanie jest przybliżone siatką (tylko pion; przesunięcie
    w bok przesuwa bryłę bez ścinania). Płaty kałuży (obrócone brzuszki) pojawiają się dopiero przy rozlanej galarecie
    (etap 7; wcześniej wychodziły na ścianę stojącego sześcianu). Kałuża po upadku ma prostokątny środek (jak w modelu). Bańka kwasu sama jest
    mała (0,56 studa) — widać ją dzięki smudze i poświacie dodanym w etapie 6. W trybie obrysu `skorupa` slime nie ma
    obrysu (bryły skóry jej nie dostają, D8).
  - Strażnik Gaju: 1128 brył (Troll 390) — klon 2346 instancji (Troll 825), klonowanie ok. 70 ms; świecenie kryształu
    i oczu to tylko materiał `Neon` (bez PointLight); stos głazów po upadku z daleka czyta się słabo, głazy się
    przenikają (jak w modelu); chód jest w miejscu. Korzenie w biegu przesuwają się pod ziemią pod cel — w klatce
    przejścia (z tułowia pod ziemię) mogą mignąć w bryle strażnika (jedna klatka, jak w modelu).
- Wojownik nie ma w próbie walki ze wszystkimi 9 rodzajami zdarzeń naraz (brak tyknięcia w tej samej walce co blok
  i utrata tury).
- **Dźwięki (etap 6):** klient Roblox ma wbudowanych tylko 11 plików (`content/sounds`), z czego sensownie nadaje się
  7: odgłos lądowania (cios, blok, łomot), świst skoku (unik, strzał, wypuszczenie bańki), „wstawanie” (czar),
  wybuch (krytyk, trafienie pocisku), plusk wody (kwas), „oof” (upadek) i ton suwaka głośności (kliknięcia, melodie
  z czterech nut). **To za mało na dobry efekt:** strzała, kula ognia, lód i czar brzmią tak samo jak świst skoku albo
  wybuch w innej wysokości, a „oof” przy upadku potwora jest śmieszny, nie straszny. Do dobrego dźwięku potrzebne są
  własne pliki (upload — poza tą paczką). Dźwięków nie odsłuchiwałem; test sprawdza tylko, że się wczytują i ile gra naraz.
  W filmach (`film_walki.py`) dźwięku nie ma.
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
- Odtwarzacz w trybie `reczny` (testy) nie przesuwa czasu sam. Od etapu 6 napisy, przejścia kamery i wstrząs też stoją
  i ruszają tylko przy przewijaniu (wcześniej starzały się w czasie rzeczywistym). Skutek dla narzędzi: zrzut tuż po
  przewinięciu może złapać napis w połowie animacji wejścia — `telefon.py` przewija jeszcze 0,25 s przed pomiarem.
- Etap 6: części na stawach `Motor6D` (kości klipów) przestawiają się dopiero w kroku silnika — pętla przewijania
  w JEDNYM wywołaniu `execute_luau` musi po każdym kroku zrobić `task.wait()`, inaczej czyta stare położenia (kość
  bańki „stała” w miejscu). Części zakotwiczone (pociski z `Efekty3D`, korzeń aktora) są aktualne od razu.
- Etap 7: Studio bywa zastane w trybie Play przez inną sesję (wspólne miejsce) albo chwilowo nie odpowiada na
  narzędzia MCP (`screen_capture` / `start_stop_play` bez odpowiedzi w 120–180 s) — film wtedy się przerywa (Studio
  wraca do Edit, stary plik filmu zostaje); powtórka po chwili przechodzi. Narzędzie `Klipy` zapisuje wysokość skóry
  slime'a w atrybucie modelu `WysokoscSkory` (zaokrąglona do 0,02) — z niej korzysta test płatów kałuży.
- Etap 7: szerokość napisu bierz z `TextService:GetTextSize` (czcionka Bangers ma ok. 0,37 wysokości na znak), nie
  z liczby znaków — zgadywana szerokość zawyżała miejsce w stosie o 60%.
- `string.upper` w Luau nie zmienia polskich liter („STRAżNIK”); w czcionkach komiksowych prototypu (same wersaliki)
  wygląda to dobrze, ale napisy porównywane w testach (napisy efektów) są w danych od razu wielkimi literami.
- Etap 5: skórowanie modelu (`p.skoruj`) droga klockowa gubi — bryła jedzie sztywno za jedną kością. Zgniatanie
  robimy siatką (`SpecialMesh.Scale` i `Offset` co klatkę), bo zmiana `Size` części przyspawanej `WeldConstraint`
  ruszałaby fizykę złożenia. Siatka wbudowana (`Brick`, `Sphere`…) skaluje się względem rozmiaru części.
- Etap 5: przesunięcie kości „w świecie aktora” (wydłużenie efektu z klipu) liczy się z obrotów `Transform` łańcucha
  rodziców — stawy prototypu mają `C0`/`C1` bez obrotu, więc obrót części kości = iloczyn obrotów `Transform`.
- Etap 5 (kontrola): `Attachment.WorldCFrame` punktu na kości jest **o klatkę za** `Transform` ustawionym w tej
  klatce. Kałuża slime'a przeskakuje ze schowka przed niego w jednej klatce klipu (kl. 30 → 31), więc rozprysk kwasu
  czytany z `Punkt_Plusk` w chwili trafienia wypadał przy slimie albo w pół drogi. Rozbłysk stylu `w_klipie` stoi
  teraz w miejscu policzonym z zasięgu klipu i wydłużenia (`ev.zasiegEfektu`), nie z punktu.
