# Areny walki zależne od biomu (D-095) — projekt

Status: **propozycja** (decyzja D-095 Karola z 17.11.2026: „arena walki musi zmieniać się z biomem” i ma mieć
dopracowane tło; wygląd i ustawienia z rozdz. „Do zmiany” czekają na ocenę Karola).

Dziś każda walka (tablica „PRÓBA WALKI”, stary las, las-pas, Bagno) toczy się na jednej polanie prototypu
`Workspace/TestWalki2/Arena`. Ten pakiet daje trzy osobne areny z klocków i cienkie wywołanie w odtwarzaczu walki, które
stawia scenę na arenie biomu źródła walki. Bez kontenera `Workspace/ArenyWalki` (albo przy błędzie) wszystko działa jak dziś.

## Trzy areny

| Arena | Charakter | Z czego |
|---|---|---|
| **Polana Pod Koronami** (las, las-pas) | słoneczna polana w starym lesie: jasny ubity plac i nasłoneczniona trawa, za nimi ciemniejsze wnętrze lasu | olbrzymie pnie (Ø 7–9) z koronami wysoko nad polaną (dziura nieba nad placem), smugi światła między pniami, wielkie muchomory jako kulisy po bokach walczących, wysepki z paproci i grzybków, dwa rzędy drzew coraz ciemniejsze w głąb, korony nad polaną, dalekie sylwety i wzgórza w mgle |
| **Pomost Nad Topielą** (Bagno) | okrągły pomost z desek nad ciemną wodą, mgła przy wodzie | kładka prowadzi do krzywej chatki na palach w środku tła (między walczącymi w planie ogólnym), dwie kolejne chatki i wieża z zieloną latarnią, korzeniaki, trzcina i pale z latarniami po bokach, kępy z grzybieniami, cypryśniki z brodą mchu i wierzby, sylwety cypryśników w mgle |
| **Plac Ćwiczeń Pod Murem** (tablica prototypu) | piaszczysty krąg z kredowym pierścieniem pod murem miasteczka | manekiny, stojaki z drewnianą bronią, tarcze łucznicze i bele po bokach walczących; trybuna, namioty, chorągwie z girlandą; mur z bramą na osi tła i basztami, dachy domków za murem, twierdza na wzgórzu; od strony widowni jarmark i drzewa |

Rodziny drzew, grzybów, skał, roślin Bagna i rekwizytów miasteczka są **importowane** z map (`swiat/biom_las`,
`swiat/bagno_pas`, `swiat/krzywe_miasteczko`) — te same sylwetki i paleta co w biomach; własne są tylko rzeczy aren
(`rekwizyty.py`). Żadnych nazw ani wyglądu z innych gier, żadnych uploadów — klocki i wbudowane materiały.

## Warstwy scenografii (od placu na zewnątrz)

1. **Plac** r 22 (= `Ustawienia.PROMIEN_PODESTU`, jak dziś), wierzch dokładnie na wysokości sceny; nic nad nim.
2. **Obręcz** r 23–25, ≤ 1 wys.: kamienie / pale z liną / niska barierka (przerwy na osi tła).
3. **Bliskie** — niskie rekwizyty w kępach (nie rozsypane), na tle i od widowni.
4. **Kulisy boczne** — wyższe rzeczy w klinach ±15° za walczącymi (tam kamery nie latają): brzegi kadru planu ogólnego.
5. **Ściana biomu** r ok. 62–125: drzewa, chatki, mur z domkami — generator sam odsuwa je poza wolną przestrzeń kamer.
6. **Korony / dachy** — korony nad polaną od 31 wys. (nad wszystkimi kamerami), dachy za murem.
7. **Dalekie sylwety** r 130–225 jaśniejące ku mgle + ciągły niski **wał horyzontu** r 232 i grunt r 240.

## Wolna przestrzeń kamer (liczona, nie zgadywana)

`kamery.py` przenosi wzory ujęć z `OdtwarzaczWalki2.luau` (plan ogólny, z boku, zza pleców, zbliżenie, krytyk ze skokiem
i zamachem, lot pocisku z obu stron, na siebie, efekt, pokonany, objazd 20°–142°) i poprawkę „twarz potwora” (wszystkie
36 kandydatów obrót × odjazd 1,0–1,8) dla każdej pary: 3 klasy × 10 potworów i lustro, wymiary z `swiat/test_walki2/dane`.
Wynik: 120 900 położeń kamery + odcinki widoku do celu i do postaci (0,25 / 0,6 / 1,0 wysokości) →
`profil_kamer.json` (promień wolny w przedziałach 3° × 0,5 wys.). Liczby: kamery do **r 87** (Strażnik Topieli, odjazd
1,8 od strony widowni) i **y 25,4**; od tła (−Z) wolne trzeba trzymać do ok. r 62 do wysokości 23, od widowni (+Z) do
r 88, a kliny ±15° za walczącymi są wolne już od r ≈ 17 — stąd kulisy boczne. Profil liczy się sam od nowa, gdy zmienią
się wymiary aktorów (odcisk danych; nowy duży potwór, np. Wąż Stu Lian 18 wys., odsunie ścianę sam).

Kontrola (`generuj.py` przy każdym obiekcie, `sprawdz.py` i `testy/test_aren.py` na gotowych plikach): **żaden punkt
bryły żadnej części** (chmura punktów wypełniająca blok, klin, klin narożny, walec, kulę) nie leży w wolnej przestrzeni
(zapas 1 stud), a nad placem nie ma nic poza gruntem. Odtwarzacz nie omija brył otoczenia, więc tę zasadę trzyma arena.

## Horyzont i tło za postaciami

`sprawdz.py` rzuca promienie z 27 kamer skrajnych (najdalsza w każdej ósemce kierunków, najwyższa, plany ogólne trzech
par z obu stron, objazd co 30°) co 1° w poziomie i 0,5° w pionie od krawędzi gruntu do +2°: każdy trafia w bryłę albo
grunt — nigdzie pustego nieba nisko ani „końca świata” (przecięcia dokładne z wielościanami i kulą). Tło za postaciami:
w planie ogólnym trzech par z obu stron — średni walor L* tła w prostokącie postaci, udział bardzo jasnych (L* > 85)
i Neonu (uwaga powyżej 12 % / 4 %). Wyniki ostatniego przebiegu: `sprawdz_wynik.json`.

## Budżet części

**1200 na arenę** (twardy limit 1500); dziś las 1126, Bagno 1197, plac ćwiczeń 1108. Uzasadnienie: w walce na ekranie
jest jedna arena (pozostałe stoją ≥ 800 studów dalej i telefon na niższej jakości ich nie rysuje), dwóch aktorów
(do ok. 1100 brył Strażnika Gaju), efekty i interfejs. Mapy biomów mają 8–9 tys. części i chodzą na telefonie, a arena
to ok. 1/8 tego. Wszystkie części: Anchored, bez CanCollide, CanQuery i CanTouch (poza fizyką i zapytaniami), dalej niż
110 bez cienia; duże proste bryły zamiast drobnicy (sylwety 2–3 części, wał 24 kliny). Pamięć: trzy areny Persistent to
ok. 3,4 tys. części u każdego gracza przez całą grę (rzędu kilku MB).

## Gdzie stoją i streaming

`Workspace/ArenyWalki/{Las, Bagno, Proba}` w (−3000, 0, 1000 / 1800 / 2600) — z dala od wszystkich map (najbliżej
teleport krain i demo, > 2,5 tys. studów) i od siebie (800). Modele mają **`ModelStreamingMode = Persistent`**: przychodzą
do klienta po dołączeniu i nie są wypychane, więc wejście w walkę nigdy nie pokazuje pustej areny, choć postać gracza
stoi tysiące studów dalej (dziś serwery lasów co sekundę proszą o streaming starej areny — dla nowych aren nie trzeba).
Aktorzy dalej klonują się z szablonów `TestWalki2/Aktorzy`, które te prośby nadal wczytują. Gdyby arena jeszcze nie
doszła do klienta (pierwsze sekundy po dołączeniu), moduł zwraca „arena_niewczytana” i walka idzie na starej arenie.

## Wybór areny i zapas

`OdtwarzaczWalki2.luau` (5 dokładnych podmian): `modulAren()` szuka `Workspace/ArenyWalki/Moduly/ArenyWalki`,
`Sesja:wybierzArene()` woła `ArenyWalki.przygotuj({ zrodlo = nazwa kontenera, kontener, folder = scena lokalna })` w
`pcall` przed chowaniem obcych, `cfSceny` = znacznik `Scena` areny albo `U.scena()`, pudło chowania obcych z areny, model
areny wykluczony. Źródła: `TestWalki2` → plac ćwiczeń, `LasPotwory` i `LasPasGra` → las, `BagnoPasGra` → Bagno; atrybut
`BiomAreny` kontenera źródła ma pierwszeństwo. Atrybuty klienta: `OstatniaArena`, `OstatniaArenaPowod`. Wyłączenie bez
usuwania: atrybut `Wylaczone = true` na `Workspace/ArenyWalki`.

## Nastrój lokalny (tylko u gracza, tylko na czas walki)

- Mgła: lokalne właściwości `Lighting.Atmosphere` (Density, Offset, Haze, Glare, Color, Decay z planu); przy końcu wracają
  wartości zastane. Kontener ustawia lokalnie `CelMglyPasa = 1`, więc mgły pasów (`MglaPasa` lasu-pasa i Bagna) ustępują
  według swojej umowy i przejmują po walce bez mignięcia. Wspólne ustawienia miejsca nietknięte.
- Detale (lokalne części w folderze sceny, ≤ ok. 40 instancji, ruch `BulkMoveTo`, położenia z czystych funkcji
  `LogikaAren`): las — spadające liście i pyłki w smugach światła; Bagno — 9 błędnych ogników (3 ze światłem) i bąbelki;
  plac — łopot chorągwi i girlandy (lokalna zmiana CFrame części areny, przywracana), kurz, trzy ptaki wysoko.
- Sprzątanie: `uchwyt:zakoncz()` z listy sprzątania sesji (ZAMKNIJ, POMIŃ, reset postaci, błąd) i sam, gdy zniknie scena.

## Przepis na kolejną arenę (Dżungla i dalej)

1. W `plan.py` nowy wpis w `ARENY`: nazwa, `model`, `biom`, źródła (nazwa kontenera biomu), `O` (wolne miejsce ≥ 800 od
   innych aren), ziarno, grunt, plac (`ziemia` / `pomost` / `piasek`), obręcz, warstwy z rodzinami, punkty (kulisy boczne
   i znaki biomu), sylwety z wałem, nastrój (Atmosphere) i detale.
2. Brakujące rodziny (np. liście-parasole, posągi, mosty z lian) — funkcja w `rekwizyty.py` + wpis w `generuj.RODZINY`.
3. `python -B swiat/areny_walki/generuj.py` → `sprawdz.py` → `podglad.py --blender` → `testy/test_aren.py`.
4. Studio: `zbuduj.py --tylko <arena>`; kontener biomu może zamiast wpisu w źródłach mieć atrybut `BiomAreny`.
Kod odtwarzacza i modułu się nie zmienia.

## Pliki i polecenia

| Plik | Co robi |
|---|---|
| `plan.py` | dane aren (warstwy, punkty, sylwety, nastrój, detale, źródła) |
| `rekwizyty.py` | rodziny rekwizytów aren + paleta (mapy + kolory aren) |
| `kamery.py`, `profil_kamer.json` | wolna przestrzeń kamer z wzorów odtwarzacza (`--odswiez` liczy od nowa, ok. 20 s) |
| `generuj.py` | plan → `<arena>/czesci.json`, `<arena>/znaczniki.json`, `zrodla/DaneAren.luau` |
| `sprawdz.py`, `sprawdz_wynik.json` | kontrola: wolna przestrzeń, budżet, horyzont, tło, zakres (ok. 3 min) |
| `podglad.py`, `render_blender.py` | podglądy z kamer walki (Pillow szybko albo Blender z mgłą) → `<arena>/podglad/` |
| `geom.py` | geometria części, przejście scena ↔ świat |
| `zrodla/ArenyWalki.luau`, `LogikaAren.luau`, `DaneAren.luau` | moduły klienta (Workspace/ArenyWalki/Moduly) |
| `zbuduj.py` | budowa w Studio (`--sucho`, `--tylko`, `--moduly`, `--usun`) |
| `testy/test_aren.py` | testy bez Studio (logika interpreterem luau_mini, dane, areny, wywołania w odtwarzaczu) |
| `testy/zrzuty_aren_play.py`, `klatki_wyniki.json` | Play: walki z każdego źródła, zrzuty każdego ujęcia → `<arena>/klatki/`, `--klatka` czas klatki (też na starej arenie) |

## Do zmiany (ustawienia przyjęte bez decyzji)

Położenia aren w świecie; budżet 1200; nastrój (las Density 0,34 Color CFE3C9, Bagno 0,44 AAB68F, plac 0,27 EADBC2);
gęstość ogników, liści i ptaków; kąty i odległości kulis; mapowanie stary las → arena leśna; plac ćwiczeń dla tablicy
prototypu (tablica nie ma biomu — mógłby to być też las); koronę nad polaną od wysokości 31.

## Ryzyka

- Mgła starego lasu (`MglaLasu`) nie zna umowy `CelMglyPasa` — zmierzone w Studio 17.11: bez poprawki pierwsza sekunda
  walki miała mgłę pośrednią (Haze 0,91 zamiast 1,3, kolor D1DAD3); moduł oddaje teraz wartość areny zaraz po cudzym
  zapisie (`Atmosphere.Changed`) — w próbie 355 przywróceń w 1,5 s, od pierwszej klatki dokładnie mgła areny.
- Persistent to stałe kilka MB na kliencie i trzy areny rysowane z daleka na wysokiej jakości grafiki (PC).
- Kamery giganta (odjazd 1,8) wypychają ścianę daleko — przy zwykłych parach arena wydaje się przestronna.
- Podglądy (Pillow, Blender) nie pokazują faktur, Neonu ani mgły Roblox; prawdziwy wygląd ocenią zrzuty z części B.

## Część B — Studio (17.11.2026)

- Stoi `Workspace/ArenyWalki` (Wygenerowane): Las 1126, Bagno 1194, Proba 1108 części + znaczniki `Scena`, modele
  Persistent, moduły ArenyWalki / LogikaAren / DaneAren; odtwarzacz z pięcioma podmianami wysłany (`zbuduj.py --skrypty`).
- Walki z każdego źródła w Play (`testy/zrzuty_aren_play.py`): tablica → `proba`, las-pas → `las`, stary las → `las`,
  Bagno → `bagno` (`OstatniaArenaPowod = ok`); z `Wylaczone = true` → `stara` (zapas działa). Mgła areny od startu walki,
  detale 9–19 instancji, po walce mgła i detale posprzątane.
- Czas klatki (Studio na wierzchu, walka ×1): stara arena 16,72 ms śr. / 17,96 p95; plac 16,68 / 17,92; las 16,70 /
  17,88; Bagno 16,69 / 17,87 — bez zmian (ograniczenie 60 kl./s; to PC ze Studio, nie telefon).
- Poprawki po zrzutach (pary „przed” bez przyrostka i „po” z `_po` w `<arena>/klatki/`): trzcina Bagna z wąskich źdźbeł
  z pałkami zamiast płaskich snopów (czytały się jak deski), mgła Bagna zieleńsza (AAB68F / 5B7046, Density 0,44),
  plac polany z ciepłej, jasnej, ubitej ziemi (Sand, BE9363) zamiast szarego Ground, smugi światła mocniejsze (0,8),
  mgła starego lasu (wyżej), pierwszy kadr bez baneru „WALKA!”, plan ogólny z drugiej strony (kamera po odtwarzaczu).
- Stare próby walki na nowej arenie placu: `test_walki_play.py --szybko` 111/111 (po dopasowaniu próby 6: intruz stoi
  w pudle sceny, w której toczy się walka — przy arenie biomu, jako Model Persistent, bo inaczej nie dochodzi do
  klienta), `test_poprawek_play.py` 27/27. Kontrola `sprawdz.py` po poprawkach: zero naruszeń, horyzont ≥ 2°, budżet.
- Do sprawdzenia dalej: telefon (czas klatki i pamięć z trzema arenami Persistent), walka gracza bez trybu testowego
  bohatera w Bagnie (próby szły z `TestBohater`), dźwięk otoczenia areny (brak — tylko nastrój wizualny).
