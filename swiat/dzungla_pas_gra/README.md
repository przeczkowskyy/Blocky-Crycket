# Dżungla w grze — trzeci grywalny biom (potwory, brama do Pustyni, przelot, mgła, teleport)

*Status: **propozycja** (18.11.2026, sesja nocna — zlecenie Karola „odpalaj resztę wszystkich tasków”). Nic tu nie jest
kanonem. Wszystko stoi w osobnych kontenerach (`Workspace/DzunglaPas` — mapa, `Workspace/DzunglaPasGra` — gra), więc
całość da się cofnąć (`--usun`).*

> **W skrócie.** Gracz, który pokonał Strażnika Topieli, przechodzi bramą Bagna prosto do Dżungli. Przy pierwszym
> wejściu ogląda przelot kamery zakończony rykiem Węża Stu Lian. W trzech zagrodach walczy z trzema gatunkami trzech
> klas, w Ruinach spotyka rzadkiego Pancernika, a na końcu, w Kręgu Stu Lian, czeka trudny strażnik. Po wygranej
> otwiera się brama do Pustyni („wkrótce”). Kod gry jest TEN SAM co w lesie-pasie i Bagnie
> (`swiat/las_pas_gra`, `swiat/las_potwory`); ten pakiet daje tylko dane i konfigurację.

## Skąd co jest
| Co | Gdzie |
|---|---|
| Mapa (projekt, układ Bagna + 940 st) | `swiat/dzungla_pas/` (`generuj.py`, `sprawdz.py`, README) |
| Mapa gry, krótka (D-096: 25 s × 4 s) | `swiat/dzungla_pas/krotki/` ← `python -B swiat/biomy/przycinarka.py` (wpis `dzungla` w `swiat/biomy/wymiary_pasa.json`) |
| Dane gry | `generuj_dane.py` → `zrodla/DanePotworowDzungli.luau`, `zrodla/DaneDzungli.luau`, `silnik/DaneWalkiDzungli.luau` |
| Przeciwnicy (silnik walki v3) | `przeciwnicy.py` — potwór lasu × k = 1,19 (kalkulator, Dżungla 17 → 23) + jedna cecha na gatunek |
| Modele i aktorzy | `swiat/postacie/{zwijogon,gebokwiat,kokosowy_silacz,pancernik_ruin,waz_stu_lian}.py`, `swiat/test_walki2/aktorzy_dzungli.py` |
| Budowa w Studio | `zbuduj.py` (budowniczy lasu-pasa na konfiguracji Dżungli) |
| Testy | `testy/test_dzungli.py` (offline), `testy/proba_play.py` (Play, J00–J17, `--sprawdz` bez Studio) |
| Własne efekty umiejętności | `swiat/test_walki2/zrodla/Choreografie.luau` (`UMIEJETNOSCI_AKTORA`), `Efekty3D.luau`; testy `swiat/test_walki2/testy/test_efektow.py`, `test_odtwarzacza.py` |

## Strefy i potwory (krótki pas)
| Strefa | Gatunek | Klasa | Poziomy | Naraz / max | Cecha (inna niż w lesie i Bagnie) |
|---|---|---|---|---|---|
| z1 Polana Zwijogonów | Zwijogon | Zwiadowca | 17–19 | 3 / 4 | Skupienie + rozszarpanie, najczęstszy unik (+6 pp) |
| g1 Kwietnik Gębokwiatów | Gębokwiat | Mag | 19–21 | 3 / 4 | usypiający pyłek (w silniku lodowy pocisk: spowolnienie) |
| o1 Gaj Kokosów | Kokosowy Siłacz | Wojownik | 21–23 | 3 / 4 | Potężne cięcie (oba kokosy z góry) |
| t1 Ruiny Pancernika | Pancernik Ruin (rzadki) | Wojownik | 23 | 1 / 1 | Kamienna skóra i gruby Pancerz |
| strażnik, Krąg Stu Lian | Wąż Stu Lian | strażnik | 23 | 1 | jad (trucizna) i ukąszenie (krwawienie), częsty unik |

Razem ze strażnikiem: 8 / 11 / 14 potworów przy 1 / 8 / 20 graczach. W scalonych strefach poziomy są rozdawane po
miejscach (`poziomyPoMiejscach`, jak w lesie i Bagnie). Wygrane klas wzorcowych: `python -B swiat/dzungla_pas_gra/przeciwnicy.py`.

## Własne efekty umiejętności (18.11.2026, propozycja — wdrożone w Studio, próba w grze J15–J17 zielona)
Potwory Dżungli używają umiejętności, które silnik zna z klas i z lasu (te same id, liczby i czasy — **dane walki bez
zmian**). Dotąd pożyczały też ich wygląd. Teraz każda ma własny, podpięty danymi: tabela
`Choreografie.UMIEJETNOSCI_AKTORA` (klucz aktora → id umiejętności) w `swiat/test_walki2/zrodla/Choreografie.luau`;
efekty w `swiat/test_walki2/zrodla/Efekty3D.luau`. Aktor bez wpisu (bohaterowie, las, Bagno) gra jak dotąd. Wpis własny
nie może zmienić stylu, prędkości pocisku ani kamery (`Ch.POLA_CZASU`) — pilnują tego testy.

| Gatunek | Umiejętność (id silnika) | Co robi | Dotąd (pożyczone od) | Teraz | Napis na ekranie |
|---|---|---|---|---|---|
| Zwijogon | `skupienie` | wzmocnienie na siebie, 3 tury | złoty błysk i złota obręcz (Zwiadowca) | zielony kłąb liści; sześć liści krąży wokół ciała, złota obręcz statusu zostaje | Kamuflaż |
| Zwijogon | `rozszarpanie` | cios 1,4 × + krwawienie | trzy czerwone ślady pazurów (Cierniowy Wilk) | sześć śladów na krzyż (dwie łapy), sypią się liście | Rozszarpanie (bez zmian) |
| Gębokwiat | `lodowy_pocisk` | pocisk magiczny + spowolnienie | lodowy sopel, lodowy rozbłysk, kryształy lodu przy nogach (Mag) | żółta chmura pyłku płynie łukiem i osiada na celu; nad uśpionym trzy „Z” i opadający pyłek | Usypiający pyłek |
| Kokosowy Siłacz | `ciecie` | cios 2,06 × | biała smuga miecza (Wojownik) | brązowa smuga kokosów, biały błysk i odłamki łupiny, fala na ziemi | Kokosy z góry |
| Pancernik Ruin | `kamienna_skora` | tarcza procentowa na siebie | szary błysk, sześć szarych głazów i szara powłoka (Wojownik) | turkusowy błysk rytów; cztery płyty ruin z turkusowym rytem i turkusowa powłoka | Kamienna skóra (bez zmian) |
| Wąż Stu Lian | `zatruta_strzala` | pocisk + trucizna (stosy) | strzała z zielonym grotem (Zwiadowca) | zielona struga jadu ze smugą i kroplami, rozprysk i unoszące się bąble | Plunięcie jadem |
| Wąż Stu Lian | `rozszarpanie` | cios 1,4 × + krwawienie | trzy czerwone ślady pazurów (Cierniowy Wilk) | cztery kły (górne szerzej, dolne między nimi) zatrzaskują się na celu przodem do kamery, rozprysk krwi z kroplą jadu | Ukąszenie |

Statusy w interfejsie (ikona, kolor, napis „SPOWOLNIENIE!”, „TRUCIZNA!”, „KRWAWIENIE!”…) są te same co zawsze. Zmienia
się tylko ozdoba na postaci dla spowolnienia od pyłku („zzz”), Kamuflażu i Kamiennej skóry Pancernika; trucizna i
krwawienie mają dotychczasowe bąbelki i krople.

**Koszt** (instancje tworzone przez jeden efekt; `python -B swiat/test_walki2/testy/test_efektow.py --tabela`, liczone
prawdziwym kodem efektów na atrapach, bez Studio). Budżet własnych efektów: ≤ 16 instancji, ≤ 1 emiter, bez świateł.
Iskry wracają do puli, więc kolejny wybuch tworzy tylko swój rozbłysk.

| Efekt | Instancji | w tym części | emiterów | smug i zaczepów | trwa (s sceny) |
|---|---:|---:|---:|---:|---:|
| `pocisk:pylek` | 5 | 4 | 1 | 0 | czas lotu |
| `pocisk:jad` | 8 | 4 | 1 | 3 | czas lotu |
| `wybuch:pylek` | 11 | 10 | 1 | 0 | 1,10 |
| `wybuch:jad` | 16 | 15 | 1 | 0 | 0,90 |
| `wybuch:ukaszenie` | 10 | 10 | 0 | 0 | 0,43 |
| `wybuch:liscie` | 11 | 11 | 0 | 0 | 0,43 |
| `wybuch:kokos` | 13 | 13 | 0 | 0 | 0,43 |
| `wybuch:kamuflaz` | 13 | 13 | 0 | 0 | 0,47 |
| `wybuch:ruiny` | 14 | 14 | 0 | 0 | 0,43 |
| `ukaszenie:kly` | 4 | 4 | 0 | 0 | 0,50 |
| `pazury:krzyz` | 6 | 6 | 0 | 0 | 0,45 |
| `wyglad:sen` | 11 | 10 | 1 | 0 | do końca statusu |
| `wyglad:kamuflaz` | 8 | 8 | 0 | 0 | do końca statusu |
| `wyglad:ruiny` | 10 | 10 | 0 | 0 | do końca statusu |

Dla porównania dawne: `wybuch:kwas` 24, `wybuch:krytyk` 17, `wybuch:ogien` 16, `pocisk:strzala` 9, `wyglad:lod` 8.
Sprzątanie: efekt chwilowy niszczy swoje części po końcu, ozdoba statusu — przy końcu statusu, a pominięcie walki
i zamknięcie sceny wołają `fx:wyczysc()`. Test bez Studio sprawdza to przy kroku ×1 / ×2 / ×4 i przy pominięciu w locie.
W grze odtwarzacz zapisuje koszt w atrybucie `OstatniKosztEfektow` kontenera `TestWalki2`.

**Dźwięk** (bez nowych plików i bez zmian w `swiat/dzwiek_gra/ustawienia.json` — wpisy wskazują istniejące zdarzenia):
- pyłek: zamiast odcinka „lodowy pocisk” — „zarodniki” w chwili wyrzutu chmury (głos Gębokwiata na początku
  umiejętności to ten sam dźwięk, więc gra raz); na trafieniu cichy dźwięk wbudowany jak przy każdym pocisku;
- jad: „rzut” przy plunięciu, na trafieniu „galareta” (mokry plusk ze szczytem w chwili trafienia; bez katalogu —
  wbudowany „plusk”); ryk Węża na początku umiejętności zostaje;
- ukąszenie, rozszarpanie, kokosy: „cios” jak dotąd; Kamuflaż i Kamienna skóra: „rzut” jak dotąd.

**Próba w grze 18.11.2026** (`testy/proba_play.py`, trzy przebiegi, ostatni na końcowym kodzie 15:48–15:54, jeden
gracz, Studio na PC): **J00–J12, J14–J17 OK**, J13 (pomiar) śr. 16,7 ms, p95 17,6 ms w Gaju Kokosów.
- **J15** — z każdym z pięciu gatunków walka z ziarnem, w którym potwór trafia umiejętnością (ziarno liczy port
  silnika w Pythonie); scena zatrzymana haczykiem `wstrzymaj`; wszystkie 7 umiejętności ma wygląd z wpisu własnego,
  ozdoby statusów zgodne (`gracz:spowolnienie` = `sen`, `wrog:skupienie` = `kamuflaz`, `wrog:kamienna_skora` = `ruiny`,
  trucizna `babelki`, krwawienie `krople`). Koszt zmierzony w grze (licznik odtwarzacza i atrybut
  `OstatniKosztEfektow`): `pocisk:pylek` 5, `wybuch:pylek` 10, `wyglad:sen` 11, `pocisk:jad` 8, `wybuch:jad` 15,
  `ukaszenie:kly` 4, `pazury:krzyz` 6, `wyglad:kamuflaz` 8, `wyglad:ruiny` 10 — równy tabeli wyżej albo niższy (iskry
  z puli).
- **J16** — walki przy ×2 (Zwijogon) i ×4 (Gębokwiat) do końca: po zamknięciu 0 instancji efektów.
- **J17** — wymuszone pominięcie w locie pyłku: w locie 4 części pyłku, po pominięciu 0 instancji i 0 ozdób.
- Wąż w J15 walczy z bohaterem, który przegrywa (Wojownik poz. 20, ziarno z portu) — brama zostaje zamknięta przed
  J10; rzadki Pancernik idzie na końcu J15, bo po walce z J06 wraca dopiero po 150 s.

Co wyszło w próbie i zostało poprawione (trzy rundy):
1. Kły ustawione do atakującego było w ujęciu z boku widać tylko krawędzią (biała kreska) → paszcza stoi przodem do
   kamery, kły są większe (skala od wzrostu celu 0,45, 1,6–3,2), górne szerzej, dolne między nimi, kość słoniowa bez
   świecenia (świecące zlewały się w słupki).
2. Chmura pyłku i struga jadu w locie były z daleka za małe → większe kłęby i krople (liczba części bez zmian).
3. Liście Kamuflażu zlewały się z zielonym Zwijogonem → większe i jaśniejsze (żółtozielone), wyraźniejsza złota obręcz.
4. Próba: część efektu nazywała się „Kiel” jak części modeli Węża i Kokosowego Siłacza, więc licznik pozostałości
   liczył modele → `KielUkaszenia` (test pilnuje, że nazwy części efektów nie powtarzają nazw części modeli); koszt
   czytany z kontenera krainy; błysk umiejętności „na siebie” łapany w chwili `aura`, nie na „trafieniu”.

Zrzuty (`klatki/e_*.jpg`, z próby J15 i J17): `e_gebokwiat_lodowy_pocisk_{lot,trafienie,status}`,
`e_waz_stu_lian_zatruta_strzala_{lot,trafienie,status}`, `e_waz_stu_lian_rozszarpanie_{trafienie,status}`,
`e_zwijogon_skupienie_{trafienie,status}`, `e_zwijogon_rozszarpanie_{trafienie,status}`,
`e_kokosowy_silacz_ciecie_trafienie`, `e_pancernik_ruin_kamienna_skora_{trafienie,status}`, `e_pominiecie_w_locie`.

Czego próba nie sprawdza: dźwięków (nikt ich nie słuchał), wyglądu w ruchu (zrzuty to pojedyncze klatki), telefonu.

**Do oceny przez ludzi** (wszystko „przyjęte, do zmiany”):
1. Napisy umiejętności inne niż nazwa w silniku: „Usypiający pyłek”, „Plunięcie jadem”, „Ukąszenie”, „Kokosy z góry”,
   „Kamuflaż” — czy tak, czy zostawić nazwy silnika.
2. Litery „Z” w kolorze statusu spowolnienia (jasny błękit, jak ikona) na żółtym pyłku — czy raczej żółte.
3. Trucizna Węża i krwawienie zostają przy wspólnych bąbelkach i kroplach — czy Wąż ma mieć własną ozdobę trucizny.
4. Kokosy: fala na ziemi przy każdym trafieniu — czy nie za mocno jak na zwykłego potwora.
5. Dźwięki: plusk galarety dla jadu i zarodniki dla pyłku — do odsłuchu w grze.
6. Kły Węża: kość słoniowa bez świecenia ma czytelny kształt, ale słabszy kontrast na jasnej posadzce areny niż
   świecąca biel — do wyboru (zrzut `e_waz_stu_lian_rozszarpanie_trafienie.jpg`).
7. Płyty ruin Pancernika są szare jak sam Pancernik — z daleka czyta się głównie turkusowa powłoka i ryt.

## Styki z innymi pakietami (dokładne podmiany)
- Bagno (`swiat/bagno_pas_gra`) już wskazywało następny biom `DzunglaPas` — przy stojącej Dżungli brama Bagna
  prowadzi dalej (ZaBrama Bagna znika); krótkie Bagno nie ma już grupy `ZapowiedzDzungli`.
- Teleport (`swiat/teleport_chmury/krainy.json`): kraina `dzungla` otwarta atrybutem `PokonalStraznikaBagna`,
  przybycie przez uchwyt `PrzeniesDoDzungli`.
- Dźwięk (`swiat/dzwiek_gra/ustawienia.json`): strefa `dzungla` (utwory lasu, ciszej) i odgłosy pięciu gatunków.
- Wskazówki (`swiat/wskazowki_gry`): biom `dzungla` i kroki Dżungli (logika w Luau i lustrze Pythona).
- Prototyp walki (`swiat/test_walki2/zrodla/SerwerWalki2.server.luau`): `DzunglaPasGra` na liście źródeł walk.
- Stan gracza (źródło łupu `DzunglaPasGra`) dopisuje agent stanu gracza; jajko Dżungli — agent petów (mapa ma
  stanowisko inkubatora: miejsce `jajko` i punkt E `Punkty/StanowiskoJajka`).

## Polecenia
```
python -B swiat/dzungla_pas_gra/generuj_dane.py            # dane (po zmianie mapy albo przeciwników)
python -B swiat/dzungla_pas_gra/testy/test_dzungli.py      # testy offline
python -B swiat/dzungla_pas_gra/zbuduj.py --sucho          # plan budowy bez Studio
python -B swiat/dzungla_pas_gra/zbuduj.py                  # buduje Workspace/DzunglaPasGra (Studio, tryb Edit)
python -B swiat/dzungla_pas_gra/testy/proba_play.py <folder poza repo>   # próba w Play (J00–J17; J15–J17 = własne efekty)
python -B swiat/test_walki2/testy/test_efektow.py          # efekty 3D bez Studio: wykonanie, koszt, sprzątanie
python -B swiat/dzungla_pas_gra/testy/proba_widokow.py <folder poza repo> # bieg, szerokość, zrzuty miejsc (w_*.jpg)
```

## Co sprawdzone w grze (18.11.2026, 01:30–01:45, jeden gracz)
- `proba_play.py`: J00–J12 i J14 OK, J13 (koszt) do oceny: średnio 16,7 ms, p95 18,0 ms w Gaju Kokosów. Pierwszy
  przebieg padł, bo próba nie otwierała bramy lasu (serwer Bagna cofał gracza bez `PokonalStraznikaLasu` aż przed
  bramę lasu) — poprawione w próbie; panel testowy dostał poziom 30 (wygrana z Wężem w J10).
- `proba_widokow.py`: bieg z Tarasu do bramy **25,0 s** (398 st, 0 utknięć); szerokość pola na Tarasie **64,9 st =
  4,06 s**; przed bramą do Pustyni postać dochodzi tylko do v +15,8, bo stoi tam taras Świątyni Stu Lian (punkt
  orientacyjny areny strażnika) — to przeszkoda, nie węższe pole.
- Walki odbyły się na scenie zastępczej prototypu (arena Dżungli w `Workspace/ArenyWalki` jeszcze nie stała).

## D-107 — walka bez przestojów (19.11.2026; wdrożone w Studio i sprawdzone w grze)

*Status: decyzja D-107 ma podpis Karola i czeka na potwierdzenie Pawła; liczby dobrał agent i są **propozycją do
oceny**. Wdrożone w Studio 19.11.2026 i sprawdzone próbą w Play (jeden gracz, komputer, okno Studio na wierzchu).
Liczby w rozdziałach wyżej (8 / 11 / 14 potworów, odrodzenie 12–18 s, strażnik 120 s, rzadki potwór 150 s) opisują
stan sprzed D-107.*

Dżungla używa tego samego kodu potworów i tego samego generatora co las, więc dostaje te same zasady z jednego
miejsca (`GESTOSC_D107` w `swiat/las_pas_gra/generuj_dane.py`; plan mapy i wygląd bez zmian):

| | Było | Jest |
|---|---|---|
| Zwykła strefa (Zwijogon, Gębokwiat, Kokosowy Siłacz), potworów przy 1 / 8 / 20 graczach | 2 / 3 / 4 | 4 / 7 / 8 |
| Razem ze strażnikiem | 8 / 11 / 14 | 14 / 23 / 26 |
| Odrodzenie zwykłych | 12 / 15 / 18 s (z tłumem najszybciej 10 s) | 2 s |
| Rzadki potwór (Pancernik Ruin) | 150 s | 20 s |
| Strażnik (Wąż Stu Lian) | 120 s | 30 s |
| Odstęp potworów na pętli | 25 st | 12 st |
| Czekanie po walce obejrzanej przy ×4 (także przegranej) | do końca czasu walki ×1 | brak (blokada ÷ 4 mija przed końcem pokazu) |
| Potwór po przegranej zajęty | czas walki ×1 + 1 s | ÷ 4 + 1 s (rewanż od razu po obejrzeniu) |

**Zmierzone w grze 19.11.2026** (`testy/proba_play.py`, punkty JD1–JD5 ze wspólnego
`swiat/las_pas_gra/testy/pomoc_d107.py`):

| Co | Wynik |
|---|---|
| Liczba potworów (JD1) | 14 przy jednym graczu; po „graczy = 20” 26 po 2,4 s |
| Odradzanie (JD2) | zwykły 2,9 s (2 s + pętla odradzania co 1 s), rzadki 21,1 s, strażnik 31,2 s |
| Koszt przy pełnym zestawie (JD3; 8 Kokosowych Siłaczy, 26 potworów) | klatka śr. 16,7 ms, p95 18,5 ms, maks. 20,5 ms; 12 widoków, 1336 brył (budżet 4000); pętla ruchu serwera śr. 0,20 ms |
| Przegrana ze strażnikiem obejrzana przy ×4 (JD4) | pokaz 13,1 s; po zamknięciu wyniku bez blokady, strażnik wolny, rewanż ruszył 1,3 s po podejściu, bez odmowy |
| Pominięta walka (JD5) | od E do przycisku POMIŃ 0,36 s, spacja → wynik 0,01 s, zamknięcie → pas 0,00 s (bez czasu reakcji człowieka) |
| Reszta listy biomu | J00–J17: 18 × OK, J13 „?” (koszt ocenia człowiek: klatka śr. 16,7 ms w Gaju Kokosów), konsola bez błędów |

Pełna lista zdjętych czekań, rachunek „samotny gracz nigdy nie czeka”, zmiany po próbach i **wybory do oceny** są w
`swiat/las_pas_gra/README.md`, rozdz. „D-107 — walka bez przestojów”. Budżet brył klienta, który w lesie ograniczył
liczbę wilków, tutaj nie przeszkadza (potwory Dżungli mają po 123–246 brył).

Testy bez Studio: `python -B swiat/dzungla_pas_gra/testy/test_dzungli.py` (liczby D-107 w teście 1c) i
`python -B swiat/las_pas_gra/testy/test_bez_przestojow.py` (trzy biomy naraz). Same punkty D-107 w grze (ok. 2,5 min):
`python -B swiat/las_pas_gra/testy/proba_d107.py <folder poza repo> dzungla`.
