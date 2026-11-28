# Test walki 3D w Roblox — prototyp cutscenki

> **Sprzątanie mapy 26.11.2026 (zlecenie Karola):** kontener `Workspace/TestWalki` (stara próba walki v1) **usunięty z miejsca** — walki grają w `TestWalki2`. Źródła i `cel_studio.py` (wybór okna Studio dla wszystkich narzędzi) zostają.

> **Status: prototyp do decyzji „walka jako ekran 2D czy cutscenka 3D”.** Nie jest to kanon ani kod gry.
> Działa wyłącznie w Roblox Studio (każdy skrypt zaczyna się od strażnika `RunService:IsStudio()`; poza Studio
> serwer usuwa cały kontener przy starcie — patrz „Bezpieczeństwo”).
>
> **Przed publikacją miejsca usuń kontener:** `python -B swiat/test_walki_roblox/zbuduj.py --usun` (albo w Studio
> usuń `Workspace/TestWalki` ręcznie) i zapisz miejsce. Samousuwanie przy starcie serwera to zabezpieczenie, nie zamiennik.
> Zadanie z `B&C/Produkcja/Zadania.md`: „Test cutscenki w samym Roblox: 2 postacie R15, 3 animacje, 8–10 s,
> kamera skryptowa, przycisk »pomiń«; pomiar wydajności”. Wcześniejszy szkic z Blendera: `swiat/test_cutscenki/`.

## Co to jest

Na wschód od placu (środek podestu w punkcie `(190, 0, 0)`) stoi mała arena z tablicą i świecącym słupem.
Gracz podchodzi do tablicy, naciska **E** i ogląda 8–10-sekundową auto-walkę 3D: Rycerz kontra Zbir.

Wynik walki liczy **serwer**: zwraca gotowy dziennik zdarzeń (kto bije, cios / blok / unik / krytyk, obrażenia,
życie po ciosie, łup). **Klient tylko ten dziennik odtwarza** — na lokalnych klonach aktorów, więc każdy gracz
widzi własną walkę, a inni jej nie widzą. To ta sama architektura, której potrzebuje ekran 2D: dziennik się nie
zmienia, zmienia się tylko odtwarzacz.

Co widać w cutscence:

- plan ogólny i napis „WALKA!”, potem jedno ujęcie na każdą wymianę (kamera z boku atakującego, strony ekranu
  stałe: Rycerz zawsze po lewej, Zbir po prawej);
- komiksowe napisy nad postaciami: „−131”, „BLOK!” z liczbą, „UNIK!”, „KRYTYK!” z dużą liczbą;
- paski życia z „duchem” (biały pasek, który kurczy się z opóźnieniem), drżenie kamery, iskry z klocków;
- cios krytyczny w zwolnieniu z „wjazdem” kamery (zawężenie kąta widzenia);
- finał: upadek pokonanego, wiwat zwycięzcy, wysypane monety i jajko, baner „ZWYCIĘSTWO!” / „PORAŻKA!”,
  objazd kamery i panel wyniku z łupem (złoto, doświadczenie, jajko) oraz przyciskami „JESZCZE RAZ” i „ZAMKNIJ”;
- przycisk **„POMIŃ”** (albo spacja / przycisk B pada) — od razu panel wyniku.

Na czas walki: blokada sterowania (także dotykowego), ukryty HUD gry i elementy Roblox (lista graczy, czat,
plecak), wyłączona podpowiedź. Arena stoi w świecie wspólnym dla wszystkich, więc klient **lokalnie chowa
wszystko obce**, co mogłoby wejść w kadr: postacie wszystkich graczy (także własną — stoi przy tablicy, obok
kamery planu ogólnego), obiekty z tagiem `TestWalkiUkryj` i każdą obcą część w pudle sceny. Po zamknięciu,
resecie postaci albo błędzie wszystko wraca do stanu sprzed walki, a wszystko, co powstało lokalnie, jest niszczone.

Po walce serwer przez jej pełny czas nie przyjmie następnej. Jeśli walkę pominięto, „JESZCZE RAZ” jest szare
i odlicza („ZA 6 S”), a podpowiedź przy tablicy pokazuje „Walcz! (za N s)”.

## Jak obejrzeć (Roblox Studio)

1. Otwórz miejsce w Studio (Team Create). W `Workspace` powinien być folder **`TestWalki`** (atrybut
   `Wygenerowane = true`). Jeśli go nie ma — odbuduj (niżej).
2. Naciśnij **Play** (F5).
3. Ze spawnu idź **na wschód** (ok. 160 studów — za plac i las), aż zobaczysz **żółty świecący słup** i czerwoną
   tablicę przy wejściu na arenę.
4. Podejdź do tablicy — pojawi się podpowiedź „Test walki 3D (prototyp) · Walcz!”. Naciśnij **E** (na telefonie: dotknij).
5. Oglądaj. „POMIŃ” w prawym dolnym rogu albo spacja przeskakuje do wyniku. Na panelu wyniku:
   „JESZCZE RAZ” (nowa walka, nowy wynik) albo „ZAMKNIJ” (powrót do gry).
6. Zatrzymaj Play (Shift+F5).

Każda walka jest inna (losowe ziarno na serwerze). Do powtarzalnego pokazu: w trybie Play, w oknie **Server**,
ustaw atrybut `ZiarnoTestowe` folderu `Workspace.TestWalki` na np. `770` (wygrana, 5 wymian, cios, blok, unik,
krytyk) albo `153` (przegrana, dwa krytyki Zbira).

## Jak odbudować kontener

```
python -B swiat/test_walki_roblox/zbuduj.py --studio <studio_id>   # buduje / odbudowuje (idempotentnie)
python -B swiat/test_walki_roblox/zbuduj.py --sucho                # tylko sprawdza źródła i pokazuje plan
python -B swiat/test_walki_roblox/zbuduj.py --studio <studio_id> --usun   # usuwa kontener (np. przed publikacją)
python -B tools/studio_mcp.py studios                              # lista okien Studio z id i placeId
```

`--studio` można pominąć tylko wtedy, gdy otwarte jest **dokładnie jedno** okno Studio. Wymaga Studio w trybie
**Edit** z włączonym serwerem MCP. Zasady bezpieczeństwa (wspólne miejsce Team Create):

- okno wybiera `cel_studio.py`: przy kilku oknach bez `--studio` skrypt przerywa i wypisuje listę; otwarte miejsce
  musi mieć placeId gry `129485428021967` (sprawdzane z listy okien i jeszcze raz w Studio przez `game.PlaceId`) —
  inne miejsce → przerwanie, zanim cokolwiek się zmieni. Tak samo działają `testy/test_play.py` i `testy/test_silnika.py`;
- wszystko trafia do jednego folderu `Workspace/TestWalki` z atrybutem `Wygenerowane = true`; odbudowa i `--usun`
  ruszają **tylko** ten folder — jeśli pod tą nazwą jest coś bez atrybutu, skrypt przerywa;
- przed budową sprawdza, czy w miejscu areny nie stoi nic obcego (`GetPartBoundsInBox`);
- przed i po stawia punkt historii (`ChangeHistoryService`), całość cofa się przez Ctrl+Z;
- każdy skrypt musi zaczynać się od strażnika „tylko Studio” (sprawdzane przed wysłaniem);
- zdalna funkcja i sygnały testowe leżą w kontenerze; interfejs powstaje w czasie działania w `PlayerGui`
  (nic w `StarterGui`); niczego nie publikuje, nie zapisuje miejsca, nie zmienia `Lighting`.

## Pliki

| Plik | Co robi |
|---|---|
| `zrodla/SilnikWalki.luau` | czysta funkcja: statystyki + ziarno → dziennik, wynik, łup, czas (8–10 s); własny generator liczb (ten sam wynik na każdej platformie); `sprawdz()` — niezmienniki dziennika |
| `zrodla/SerwerWalki.server.luau` | jedyny punkt styku z klientem: `RemoteFunction RozpocznijWalke` bez argumentów; statystyki zna tylko serwer; sprawdza odległość od tablicy i sesję walki (patrz „Bezpieczeństwo”); poza Studio usuwa kontener |
| `zrodla/OdtwarzaczWalki.luau` | kliencka cutscenka: klony aktorów, animacje, ruch proceduralny, kamera, efekty, chowanie obcych w kadrze, sprzątanie, pomiary |
| `zrodla/InterfejsWalki.luau` | interfejs w `PlayerGui`: paski życia, napisy, baner, „POMIŃ”, panel wyniku (z odliczaniem na „JESZCZE RAZ”), ikony z pikseli; kadr 16:9 z czarnymi pasami |
| `zrodla/KlientWalki.client.luau` | spina wejścia: podpowiedź (E, z odliczaniem po walce), haczyki testowe `Sygnaly/StartTestu`, `PominTest`, `ZamknijTest` |
| `zrodla/Ustawienia.luau` | wspólne stałe: położenie areny, pudło sceny, tag `TestWalkiUkryj`, identyfikatory domyślnych animacji, kolory, dźwięki |
| `budowa/arena.luau`, `budowa/aktorzy.luau` | budowa areny i dwóch rigów R15 (domyślny opis + przyspawane klocki), uruchamiane przez `zbuduj.py`; podpowiedź powstaje wyłączona |
| `zbuduj.py` | odtwarza kontener w Studio ze źródeł (patrz wyżej) |
| `cel_studio.py` | wybór okna Studio dla `zbuduj.py` i testów: jedno okno albo `--studio`, zawsze placeId gry |
| `testy/test_silnika.py` | silnik w Studio: powtarzalność, niezmienniki na 1500 ziarnach, zgodność z portem w Pythonie, odrzucanie złych danych |
| `testy/symulacja.py` | kontrolny port silnika w Pythonie (do testu zgodności i szybkich symulacji balansu) |
| `testy/test_play.py` | test w trybie Play (patrz niżej); sam wraca do trybu Edit |
| `klatki/*.jpg` | 10 klatek z odtworzenia (ziarno 770 i 153) |

Animacje: wyłącznie **domyślne animacje Roblox R15** (`idle`, `toolnone`, `toolslash`, `toollunge`, `cheer`,
`laugh` — identyfikatory czytane na żywo ze skryptu `Animate` postaci gracza) plus ruch proceduralny liczony co
klatkę (doskok, zamach, garda z tarczą, unik, odrzut, upadek). Dźwięki: wbudowane w klienta Roblox (`rbxasset://`).
Żadnych uploadów.

## Testy (13.11.2026, Studio na PC)

```
python -B swiat/test_walki_roblox/testy/test_silnika.py [--studio <id>]     # tryb Edit, tylko odczyt
python -B swiat/test_walki_roblox/testy/test_play.py [--studio <id>] [--zrzuty <folder>]
```

- **Silnik:** powtarzalność OK; niezmienniki na 1500 ziarnach OK (4–6 wymian, 8–10 s, zgodne `hp_po`, nokaut
  w ostatniej wymianie); port w Pythonie daje 1500/1500 identycznych dzienników; złe dane odrzucane 4/4.
- **Play — 42/42 zaliczonych (druga runda, po weryfikacji):** wejście przez podpowiedź (nawigacja do tablicy + E →
  start po 0,08 s); „POMIŃ” kliknięty myszą → panel wyniku po 0,07 s, „JESZCZE RAZ” szare z odliczaniem („ZA 5 S”),
  kliknięcie w trakcie blokady nic nie robi, po czasie walki przycisk wraca; „JESZCZE RAZ” → nowa walka; po pełnej
  walce przycisk od razu dostępny; „ZAMKNIJ” → kamera `Custom` na postaci, GUI gry, lista graczy i czat z powrotem,
  blokady klawiszy zdjęte, postać chodzi (klawisz W); **reset postaci w trakcie** (Health = 0 na serwerze) →
  cutscenka przerwana, wszystko lokalne posprzątane, po odrodzeniu własna postać widoczna, kamera i sterowanie
  działają; bezpieczeństwo (niżej); **obcy w kadrze** (manekin R15 na środku podestu, część z tagiem i
  `CanQuery = false`, część dodana w trakcie walki, własna postać) → w trakcie walki schowani, po niej widoczni;
  **symulacja publikacji** (niżej); konsola bez ostrzeżeń i błędów z naszego kodu.
- **Kadry** sprawdzone na zrzutach co ok. 0,08–0,25 s czasu sceny (odtwarzanie zwolnione 4×, obie wersje:
  wygrana i przegrana). Poprawione w tej rundzie: cel ciosu nie chowa się już za plecami atakującego, Zbir nie
  wypada z kadru, „BLOK!” i liczba nie zlewają się, krytyk nie zasłania ekranu iskrami i błyskiem, panel wyniku
  nie zasłania paska życia, zwycięzca w finale stoi przodem do kamery i obok panelu.

## Pomiary (PC z Roblox Studio — **nie telefon**)

| Co | Wartość |
|---|---|
| Długość cutscenki (od pierwszej klatki walki do panelu wyniku) | 9,23–9,24 s (ziarno 770), 8,76 s (ziarno 153); zawsze 8–10 s z założenia silnika |
| Od naciśnięcia E do pierwszej klatki walki | ok. 0,16 s (w tym prośba do serwera 43–60 ms i zaciemnienie) |
| Średni czas klatki | 16,66–16,67 ms (= limit 60 FPS w Studio) |
| 95. percentyl czasu klatki | 17,8–18,0 ms |
| Najdłuższa klatka | 24–33 ms (pojedyncze klatki) |
| Czas procesora zużyty przez nasz kod na klatkę | średnio 0,15 ms, 95. percentyl 0,31–0,32 ms, maks. 1,2–1,7 ms (druga runda, z chowaniem obcych: zapytanie o pudło sceny co 0,2 s + pilnowanie schowanych części co klatkę; wcześniej 0,13 / 0,24–0,29 / 1,1–1,4 ms) |
| Instancje utworzone lokalnie na jedną walkę | 947 (dwa klony aktorów ≈ 570, reszta to interfejs, efekty i obiekty animacji) — wszystkie niszczone po walce |
| Stałe instancje w `Workspace/TestWalki` | 882 (384 części, 6 skryptów) |
| Wymian w walce / ujęć kamery | 4–6 / 6–8 |

**Czego NIE dało się zmierzyć:**

- **telefonu** — to był główny cel zadania („pomiar na tanim telefonie”); emulator urządzeń w Studio nie mierzy
  wydajności, a pomiar wymaga uruchomienia na prawdziwym telefonie (np. przez publikację testowego miejsca —
  bez zgody nie publikowałem);
- zapasu mocy na PC — Studio trzyma limit 60 FPS, więc wiemy tylko, że limit jest utrzymany, nie ile zostaje;
- czasu GPU, pamięci i rozgrzewania się telefonu;
- prawdziwych opóźnień sieci (serwer i klient działały na jednym komputerze) i zachowania przy wielu **prawdziwych**
  graczach — chowanie obcych sprawdzono na manekinie i częściach testowych, kosztu przy 16–20 graczach nie mierzono;
- dźwięku (testy były bez odsłuchu) i odbioru przez człowieka w normalnym tempie — kadry oceniałem na zrzutach.

## Bezpieczeństwo (sprawdzone)

- Klient **nie wysyła żadnych liczb**: `InvokeServer()` bez argumentów; serwer argumentów nie czyta. Test: klient
  wysłał „hp = 1e9, złoto = 1e9, »wygrana«” i lokalnie zmienił atrybut ziarna → serwer policzył walkę po swojemu
  (hp 480, złoto 97, ziarno z serwera).
- Łup liczy serwer w tym samym wywołaniu co walkę (w prawdziwej grze: tam też go zapisuje).
- Serwer sam decyduje, czy wolno zacząć walkę (kolejno):
  1. najwyżej 1 prośba na gracza na sekundę (także odrzucona) → inaczej `za_szybko`;
  2. postać żyje i stoi najwyżej **20 studów od tablicy** (podpowiedź działa z 14) → inaczej `brak_postaci` / `za_daleko`.
     Test: postać 35 studów od tablicy → `za_daleko`;
  3. **sesja walki:** serwer pamięta, do kiedy trwa walka gracza (czas serwera + `walka.czas` − 0,4 s zapasu na sieć),
     i do tej chwili odpowiada `walka_trwa`. „POMIŃ” skraca tylko odtwarzanie, nie ten limit. Test: prośba 1,1 s po
     udanej → `walka_trwa`, „ponów za 7,6 s”. Wcześniej wystarczał odstęp 1,5 s, więc skrypt klienta mógł brać
     ok. 40 walk z łupem na minutę bez oglądania i spod spawnu; teraz najwyżej jedną walkę na jej czas (ok. 6–7 na minutę)
     i tylko przy tablicy.
- **Poza Studio w świecie nic nie zostaje:** strażnik `SerwerWalki` w opublikowanej grze nie tylko kończy skrypt,
  ale **usuwa cały kontener** (arenę, świecący słup, szablony Rycerza i Zbira, podpowiedź) przy starcie serwera,
  zanim ktokolwiek dołączy; usunięcie replikuje się do klientów. Do tego podpowiedź jest zbudowana jako **wyłączona**
  i włącza ją dopiero serwer w Studio — gdyby skrypt serwera z jakiegoś powodu nie ruszył, nikt nie zobaczy
  podpowiedzi, która nic nie robi. Test „symulacja publikacji” (w trybie Play): kopia `SerwerWalki` z
  `IsStudio()` zamienionym na `false` w osobnym folderze kontenera usunęła ten folder — u serwera i u klienta.
  Zasada mimo to: **przed publikacją `zbuduj.py --usun`** (wyżej) — zabezpieczenie nie zastępuje sprzątania.
- Strażnik „tylko Studio” w każdym skrypcie (sprawdzany przez `zbuduj.py`).
- Poza `Workspace/TestWalki` prototyp niczego nie zmienia (porównany spis usług sprzed i po pracy; różnice
  w `ReplicatedStorage/Shared`, `ServerScriptService/Server` i `StarterGui/EquipmentPanel` z 13.11 to praca
  współtwórców w Team Create, nie prototypu).

**Lekcja dla architektury z propozycji D-016 („serwer liczy, klient odtwarza”):** sam limit częstotliwości nie
wystarcza — to on wyznaczałby tempo zdobywania łupu. Serwer musi (1) sprawdzać, czy gracz naprawdę stoi przy
przeciwniku / tablicy (pozycja `HumanoidRootPart` po stronie serwera), (2) trzymać sesję walki z czasem końca
i nie zaczynać następnej przed nim, a „pomiń” ma skracać tylko odtwarzanie, (3) docelowo mieć koszt walki
(energia, bilet, odnowienie przeciwnika) — to już decyzja projektowa, nie techniczna.

## Ograniczenia prototypu

- Jedna stała arena obok placu — walka **nie** dzieje się w biomie, w którym stoi gracz. Walka „na miejscu”
  wymaga kamer odpornych na drzewa, ściany i nierówny teren — tego nie sprawdzano.
- **Świat wspólny = obcy w kadrze.** Inni gracze widzą arenę, a cutscenka gra tylko u jednego. Prototyp chowa
  lokalnie postacie wszystkich graczy (też tych, którzy dołączą lub odrodzą się w trakcie), obiekty z tagiem
  `TestWalkiUkryj` i każdą obcą część w pudle sceny (zapytanie co 0,2 s). Nie złapie: części z `CanQuery = false`
  bez tagu (część petów i efektów — systemy gry musiałyby je tagować), efektów spoza pudła widocznych w tle,
  dźwięków innych graczy. Przy decyzji 2D/3D to **koszt walki „na miejscu”**: każdy system gry, który coś
  wstawia do świata, musi o cutscence wiedzieć. Alternatywa bez tego kosztu: scena w odległym, pustym miejscu
  tylko u klienta (np. kopia areny na Y = 5000) — za cenę innego tła i dodatkowych ~300 lokalnych części.
- Dwóch stałych aktorów i cztery rodzaje zdarzeń (cios, blok, unik, krytyk). Brak magii, strzał, petów, kilku
  przeciwników naraz.
- Domyślne animacje Roblox + ruch proceduralny wyglądają poprawnie, ale „klockowo” i podobnie w każdej walce;
  brak własnych animacji (wymagałyby uploadu).
- Brak przycisku „×2” i trybu „tylko wynik” (oba wskazane w `B&C/Badania/Technika gry — serwery, światy, walki.md`).
- Statystyki wpisane na sztywno w `SerwerWalki`; łup nie jest nigdzie zapisywany; balans umowny.
- Przy krytyku broniący na chwilę bieleje (błysk trafienia przez `Highlight`) — celowe, ale w zwolnieniu wyraźne.
- Nawigacja postaci przez MCP bywa zawodna na długim dystansie; `test_play.py` dochodzi wtedy drugi raz.

## Wnioski dla decyzji „2D czy 3D” (propozycja, nie decyzja)

1. **Technicznie 3D na PC działa lekko:** nasz kod zużywa ok. 0,15 ms na klatkę (z chowaniem obcych), 60 FPS utrzymane, sprzątanie po
   walce pewne (także przy resecie). Największą niewiadomą zostaje **telefon** (GPU, pamięć na ~950 lokalnych
   instancji, nagrzewanie) — trzeba to zmierzyć przed decyzją.
2. **Architektura „serwer liczy, klient odtwarza” sprawdziła się** i nie zależy od wyboru: ten sam dziennik może
   napędzać ekran 2D, a później cutscenkę 3D. Decyzję o wyglądzie można więc odłożyć bez ryzyka dla balansu.
3. **Koszt produkcji — uczciwie:**
   - cutscenka **nie** powstaje osobno dla każdej walki: jedna choreografia odtwarza każdy dziennik
     (koszt na walkę = 0);
   - stały koszt silnika odtwarzania jest duży: odtwarzacz ok. 1200 linii, interfejs ok. 800, plus dopieszczanie
     kadrów na zrzutach — w sumie ok. jednej nocy pracy agenta (≈ 8 h) dla 2 aktorów i 4 rodzajów zdarzeń;
   - **każdy nowy przeciwnik** to model z klocków na rigu R15 (rząd 1–3 h) i sprawdzenie, czy kadry pasują do jego
     rozmiaru i broni; **każdy nowy rodzaj akcji** (czar, strzał, pet, kilku wrogów) to nowa choreografia i ujęcia
     (rząd 0,5–1 dnia pracy agenta + testy na zrzutach); **własne animacje** zamiast domyślnych — Animation Editor
     i upload, rząd 1–3 h na animację;
   - dla porównania ekran 2D: na przeciwnika portret / grafika z pipeline’u assetów i ten sam interfejs pasków,
     napisów i panelu wyniku (ten z prototypu da się przenieść prawie bez zmian).
4. **Zmęczenie widza:** 9 s × np. 30 walk dziennie ≈ 4,5 min oglądania. „POMIŃ” jest, ale przed wdrożeniem
   potrzebne są „×2” i tryb „tylko wynik”.
5. Możliwa ścieżka (do decyzji Game Directora): MVP z ekranem 2D na tym samym dzienniku, cutscenka 3D jako
   późniejsza aktualizacja albo nagroda za ważne walki (bossowie, arena) — po pomiarze na tanim telefonie.

## Klatki

| Plik | Co pokazuje |
|---|---|
| `klatki/01_walka_plan_ogolny.jpg` | plan ogólny, baner „WALKA!”, paski życia, „POMIŃ” |
| `klatki/02_cios_rycerza_-131.jpg` | cios Rycerza, „−131”, pasek Zbira z „duchem” |
| `klatki/03_blok_zbira.jpg` | atak Zbira, Rycerz blokuje tarczą: „BLOK!” i „−17” |
| `klatki/04_unik.jpg` | „UNIK!” — Rycerz schodzi z linii ciosu |
| `klatki/05_krytyk_zwolnienie.jpg` | krytyk w zwolnieniu: „KRYTYK!” i „−680” |
| `klatki/06_zwyciestwo_lup.jpg` | wiwat zwycięzcy, wysypane jajko i monety, baner u dołu |
| `klatki/07_panel_wyniku_wygrana.jpg` | panel wyniku z łupem (+97 złota, +50 doświadczenia, +1 jajko) |
| `klatki/08_panel_wyniku_przegrana.jpg` | wersja przegranej (ziarno 153): Zbir po prawej, panel po lewej |
| `klatki/09_panel_po_pomin_odliczanie.jpg` | panel wyniku po „POMIŃ”: „JESZCZE RAZ” szare z odliczaniem („ZA 6 S”), bo serwer nie uznał jeszcze walki za skończoną |
| `klatki/10_obcy_schowani_w_walce.jpg` | plan ogólny w teście „obcy w kadrze”: manekin R15 na środku podestu, zielona i fioletowa kostka są w świecie, ale u oglądającego schowane |
