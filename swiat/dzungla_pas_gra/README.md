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

## Własne efekty umiejętności (18.11.2026, propozycja — część A bez Studio; próba w grze J15–J17 jeszcze nie uruchomiona)
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
| Wąż Stu Lian | `rozszarpanie` | cios 1,4 × + krwawienie | trzy czerwone ślady pazurów (Cierniowy Wilk) | cztery kły zatrzaskują się na celu, rozprysk krwi z kroplą jadu | Ukąszenie |

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

**Do oceny przez ludzi** (wszystko „przyjęte, do zmiany”):
1. Napisy umiejętności inne niż nazwa w silniku: „Usypiający pyłek”, „Plunięcie jadem”, „Ukąszenie”, „Kokosy z góry”,
   „Kamuflaż” — czy tak, czy zostawić nazwy silnika.
2. Litery „Z” w kolorze statusu spowolnienia (jasny błękit, jak ikona) na żółtym pyłku — czy raczej żółte.
3. Trucizna Węża i krwawienie zostają przy wspólnych bąbelkach i kroplach — czy Wąż ma mieć własną ozdobę trucizny.
4. Kokosy: fala na ziemi przy każdym trafieniu — czy nie za mocno jak na zwykłego potwora.
5. Dźwięki: plusk galarety dla jadu i zarodniki dla pyłku — do odsłuchu w grze.

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
