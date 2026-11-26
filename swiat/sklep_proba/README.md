# Sklep zbrojmistrza na próbę — kupowanie przedmiotów za Złoto (D-106)

Status: **propozycja (prototyp)**. 19.11.2026 wdrożony w Studio (kontener `Workspace/SklepProba`, kowal z wejściem
`Sygnaly/Sklep`, przymierzalnia z przedmiotami stopni); próba w grze 12/12 zielona (wyniki niżej). Okno jest
tymczasowe: docelowe okno 2D zrobi druga osoba — podmienia się jeden moduł (`OknoSklepu.luau`).

## Co to jest
Gracz podchodzi do zbrojmistrza w bazarze, naciska E i kupuje przedmioty swojej klasy za Złoto: komplet startowy
i trzy stopnie (leśny, bagienny, Dżungli) — 72 pozycje w katalogu `swiat/postacie/sklep_przedmioty.json`
(wojownik i zwiadowca po 28, mag 16). Kupiony przedmiot liczy się w walce dokładnie tak jak przedmioty z łupu
(wpis „kowal” w `StanGracza/Sygnaly/Modyfikatory`) i można go ulepszać u kowala.

Podział pracy:

| Kto | Co robi |
|---|---|
| **kowal** (`swiat/kowal_proba`) | właściciel przedmiotów gracza; zna 72 przedmioty (18 dzisiejszych z własnych ustawień + 54 nowe prosto z katalogu), sprawdza kupno, **płaci** przez `StanGracza/Sygnaly/WydajZloto`, zapisuje posiadanie, zakłada, przelicza `Modyfikatory`, pisze atrybut `SklepStacNa` |
| **sklep** (`swiat/sklep_proba`) | cienki serwer (typy, limit zapytań, odległość od stoiska) + tymczasowe okno; o niczym nie decyduje i niczego nie trzyma |
| **StanGracza** | Złoto (nigdy poniżej zera) |
| **przymierzalnia** (`swiat/stroje_proba`) | strój na postaci (atrybut `StrojProba_<klasa>`) |
| **bazar** (`swiat/miasteczko_bazar_gra`) | stoisko, zbrojmistrz, podpowiedź E, zdarzenie okien |

## Jak działa kupno (kolejność kroków)
1. Klient wysyła `Zdalne/Sklep:InvokeServer("kup", id)` — tylko nazwę akcji i id z oferty (żadnych cen ani liczb).
2. Serwer sklepu: typy i długość id, limit jednego zapytania na 0,25 s, odległość postaci od stoiska zbrojmistrza
   (10 + 6 st zapasu). Potem woła `KowalProba/Sygnaly/Sklep:Invoke("kup", gracz, id)`.
3. Kowal — czysta funkcja `LogikaKowala.kup(dane, klasa, poziom, Złoto, id)`: odmowa z powodem albo plan kupna.
4. Kowal płaci: `WydajZloto:Invoke(gracz, { ile = cena, zrodlo = "KowalProba", cel = "zakup_przedmiotu" })`.
   Odmowa stanu gracza = odmowa kupna, **nic nie jest zapisane**.
5. Zapis posiadania w profilu (`DanePakietu`, pakiet „kowal”): `przedmioty[id] = { poziom = 0, zapas = 0 }`.
6. Założenie według reguły (niżej) przez przymierzalnię (`StrojeProba/Sygnaly/SterowanieSerwera "ustaw"`).
7. Przeliczenie `Modyfikatory` (źródło „kowal”) i atrybutów gracza (`KowalDostepne`, `SklepStacNa`…).
8. Sklep odsyła zdanie dla gracza i odświeżoną ofertę.

**Reguła zakładania po kupnie:** przedmiot zakłada się sam, gdy jego slot jest pusty albo założony w nim przedmiot
ma niższy stopień (`nr_stopnia`); przy tym samym lub wyższym stopniu zostaje dotychczasowy, a kupiony czeka — gracz
zakłada go ręcznie przyciskiem „Załóż” w oknie sklepu albo w przymierzalni. Ta sama reguła obowiązuje teraz nowy
przedmiot z łupu (startowy hełm z walki nie zdejmie kupionego hełmu). Zawsze najwyżej jeden przedmiot na slot;
bez przymierzalni liczy się w każdym slocie posiadany przedmiot najwyższego stopnia.

**Część zbroi** (nogawice, spodnie; `sprzedawany = false`) nie ma własnej pozycji ani własnego wpisu w posiadanych:
należy do swojej zbroi (`czesc_od`) — kto ma zbroję, ma i część, a przymierzalnia zakłada je razem (tak jak dziś
przy zbroi startowej). Odpowiedź kupna podaje ją w polu `czesc`.

## Odmowy
| Powód | Kiedy | Zdanie dla gracza |
|---|---|---|
| `nieznany_przedmiot` | id spoza katalogu, zły typ | „Zbrojmistrz nie ma takiego przedmiotu.” |
| `czesc_zbroi` | nogawice / spodnie | „Tę część dostajesz razem ze zbroją.” |
| `inna_klasa` | przedmiot innej klasy niż klasa gracza | „Ten przedmiot jest dla innej klasy.” |
| `masz` | gracz już go ma | „Masz już ten przedmiot.” |
| `za_niski_poziom` (+ `brakuje` poziomów, `wymagany`) | poziom gracza < poziom przedmiotu | „Potrzebujesz poziomu 13.” |
| `za_malo_zlota` (+ `brakuje`) | Rybki (atrybut `Gold`) < cena (także odmowa `WydajZloto`) | „Brakuje ci 150 Rybek.” („1 Rybki”, od 26.11.2026 — D-146) |
| `daleko` | postać dalej niż 16 st od stoiska | „Podejdź bliżej zbrojmistrza.” |
| `za_szybko` | drugie zapytanie przed upływem 0,25 s albo w trakcie kupna | „Chwileczkę…” |
| `nieczynny` | brak kowala albo stanu gracza | „Sklep nieczynny (próba).” |
| `nie_masz`, `nie_zalozono` | „Załóż” bez przedmiotu / bez przymierzalni | „Najpierw kup ten przedmiot.” / „Nie udało się założyć — spróbuj w przymierzalni.” |

Kolejność sprawdzeń w logice: nieznany → część zbroi → inna klasa → posiadany → poziom → Złoto.

## Wejścia
- `SklepProba/Zdalne/Sklep` (RemoteFunction): `InvokeServer(akcja, id?)` → `{ ok, powod?, brakuje?, zalozony?, tekst?, widok? }`;
  akcje `"oferta"`, `"kup"`, `"zaloz"`; `widok = { oferta, zloto, poziom, klasa }`.
- `KowalProba/Sygnaly/Sklep` (BindableFunction, wejście kowala):
  `Invoke("oferta", gracz)` → `{ ok, oferta, zloto, poziom, klasa }`;
  `Invoke("kup", gracz, id)` → `{ ok, powod?, brakuje?, wymagany?, zalozony, zloto, id?, nazwa?, cena?, czesc? }`;
  `Invoke("zaloz", gracz, id)` → `{ ok, powod?, zalozony, zloto, nazwa? }`.
- Wiersz oferty: `{ id, nazwa, slot, slotNazwa, stopien, nrStopnia, cena, poziom, stan, brakuje, ulepszenie, staty }`,
  `stan` = `kup | za_drogie | za_niski_poziom | masz | zalozone`.
- Atrybut gracza `SklepStacNa` (pisze kowal): ile przedmiotów gracz może teraz kupić (klasa, poziom i Złoto pasują,
  jeszcze ich nie ma); odświeżany przy zmianie Złota, poziomu, klasy i posiadania.
- Haczyki prób: `SklepProba/Sygnaly/SterowanieSerwera` (`"stan"`, `"zgodnosc"`), `SterowanieKlienta` (`"otworz"`,
  `"zamknij"`, `"stan"`, `"zakladka"`, `"kliknij"`). Atrybut kontenera `EmulacjaEkranu = Vector2(667, 375)` — okno
  jak na telefonie.

## Jak otwiera się okno — E bazaru, bez zmian w bazarze
Okno otwiera **istniejąca podpowiedź E bazaru** przy zbrojmistrzu (miejsce `zbrojownia`, znacznik
`sklepy/zbrojownia`). Klient bazaru po E odpala u klienta zdarzenie `ReplicatedStorage.OknoMiejsca` z id miejsca;
klient sklepu słucha id `zbrojownia`. Własnej podpowiedzi E sklep nie ma (dwie podpowiedzi w jednym miejscu myliłyby
gracza). Dymek bazaru „broń i zbroje już wkrótce” wyłącza przewidziany przez bazar atrybut zdarzenia
(`OknoMiejsca:SetAttribute("zbrojownia", true)` — haczyk z README bazaru). Okno zamyka X albo odejście dalej niż
20 st od stoiska.

**Dwa okna przy zbrojowni (sprawdzone 19.11.2026).** W miejscu gry (tylko w Studio, nie w repo) stoi skrypt
`StarterPlayerScripts/Client/ShopClient` — makieta okna sklepu z HUD (ScreenGui `Shop`, „WEAPON SHOP” / „MAGIC SHOP”,
puste sloty). Słucha tego samego zdarzenia `OknoMiejsca` dla `zbrojownia` i `sklep_magiczny` (i kliknięcia
w figurę sprzedawcy) i sam zgłasza oba miejsca atrybutem zdarzenia. Bez zmian po E przy zbrojowni stałyby dwa okna
naraz. Dlatego klient sklepu, gdy otwiera okno po E zbrojowni, **chowa u gracza makietę `Shop`** (`Enabled = false`,
tylko po stronie klienta; ShopClient przy następnym otwarciu włącza ją sam). Wyłącznik: atrybut kontenera
`ChowajOknoShop = false`; licznik schowań: `SchowanoOknoShop`. Sklep magiczny dalej otwiera makietę `Shop`. Sygnał
HUD `Shop`, który bazar też wysyła przy zbrojowni, dziś nic nie otwiera (nikt go nie słucha). Gdy docelowe okno
przejmie kupno, kontener `SklepProba` usuwa się (`zbuduj.py --usun`) albo podmienia `OknoSklepu.luau`.

## Okno (tymczasowe)
Nagłówek: tytuł z napisem PRÓBA, poziom, Złoto, X (co najmniej 44 px). Zakładki stopni (startowy / leśny / bagienny /
Dżungli) w kolorze stopnia, z liczbą pozycji do kupienia. Przewijana lista: kolorowe pole stopnia zamiast ikony
(bez wgrywanych obrazków), nazwa, slot i statystyki (+0; posiadany — na swoim poziomie ulepszenia), wymagany poziom
i cena, stan, przycisk „Kup” albo „Załóż”. Na dole pasek ze zdaniem odmowy albo potwierdzenia. Układ liczy czysta
funkcja `LogikaSklepu.uklad(D, W, H)`; na telefonie 667 × 375: okno 480 × 352 px, wiersz 48 px, przycisk 44 px,
tekst 14 pt, pięć wierszy bez przewijania.

## Pliki
| Plik | Co to |
|---|---|
| `ustawienia.json` | jedyne źródło liczb i tekstów sklepu (bez cen — te ma katalog) |
| `dane.py` → `zrodla/DaneSklepu.luau` | generator danych (`--sprawdz`), przypadki wzorcowe logiki |
| `logika_sklepu.py`, `zrodla/LogikaSklepu.luau` | czysta strona sklepu: układ okna, teksty stanów i odmów, zakładki |
| `zrodla/SerwerSklepu.server.luau` | cienki serwer |
| `zrodla/KlientSklepu.client.luau`, `zrodla/OknoSklepu.luau` | klient i tymczasowe okno |
| `sprawdz_luau_sklepu.py` | kontrola statyczna Luau (sklep nie płaci i nie zapisuje sam) |
| `zbuduj.py` | budowa kontenera (`--sucho`, `--skrypty`, `--usun`) |
| `testy/test_sklepu.py` | testy bez Studio (26) |
| `testy/proba_play.py` | próba w Play S00–S11 (`--sprawdz` bez Studio; `--wynik <plik>` — wynik poza repo) |
| `klatki/` | zrzuty z próby 19.11.2026 (lista niżej) |

Zmiany u kowala (`swiat/kowal_proba`): `dane.py` (wpisy z katalogu sklepu, pola `cena`, `poziom`, `stopien`,
`nrStopnia`, lista `klasy[k].wszystkie`), `logika_kowala.py` + `zrodla/LogikaKowala.luau` (`kup`, `oferta`, `stacNa`,
`czyZalozyc`, `strojZPrzedmiotem`, jeden przedmiot na slot), `zrodla/SerwerKowala.server.luau` (wejście
`Sygnaly/Sklep`, atrybut `SklepStacNa`), `zbuduj.py` (nowy sygnał), `ustawienia.json` (sekcja `sklep`), testy.

## Polecenia bez Studio
```
python -B swiat/kowal_proba/dane.py --sprawdz
python -B swiat/kowal_proba/testy/test_kowala.py
python -B swiat/kowal_proba/sprawdz_luau_kowala.py
python -B swiat/kowal_proba/zbuduj.py --sucho
python -B swiat/sklep_proba/dane.py --sprawdz
python -B swiat/sklep_proba/testy/test_sklepu.py
python -B swiat/sklep_proba/sprawdz_luau_sklepu.py
python -B swiat/sklep_proba/zbuduj.py --sucho
python -B swiat/sklep_proba/testy/proba_play.py --sprawdz
```

## Część ze Studio — polecenia w kolejności
Przed budową: zgłoszenie pracy (`praca.py start … --obszar studio:KowalProba --obszar studio:StrojeProba
--obszar studio:SklepProba`), Studio w trybie Edit.
1. `python -B swiat/stroje_proba/zbuduj.py` — przymierzalnia z przedmiotami stopni (według jej README; bez tego kupiony
   przedmiot nie pokaże się na postaci).
2. `python -B swiat/kowal_proba/zbuduj.py` — **cała** budowa kowala, nie `--skrypty`: nowy obiekt `Sygnaly/Sklep`
   powstaje tylko przy pełnej budowie (ze starym kontenerem serwer kowala działa jak dawniej, atrybut
   `WejscieSklepu = false`, a sklep pisze „Sklep nieczynny (próba)”).
3. `python -B swiat/sklep_proba/zbuduj.py` — kontener sklepu.
4. `python -B tools/studio_okno.py --na-wierzch`, potem próby: `python -B swiat/kowal_proba/testy/proba_play.py`
   (czy dzisiejsze zachowanie kowala zostało), `python -B swiat/stroje_proba/testy/proba_play.py` (jeśli jest),
   `python -B swiat/sklep_proba/testy/proba_play.py`.
5. Zrzuty z `klatki/` do raportu w panelu; `praca.py koniec`.

## Wskazówka „stać cię na nowy przedmiot” — co dopisać w `swiat/wskazowki_gry`
Pakietu wskazówek ta część nie zmienia. Wzór: krok (g) „kowal” z 18.11 (teksty `g_kowal_*`, cel `kowal`, atrybuty
`KowalZapasy`, `KowalMoznaUlepszyc`, `KowalUlepszen`). Do dopisania:
- `ustawienia.json`, teksty: `h_sklep` = „Stać cię na nowy przedmiot — zajrzyj do zbrojmistrza w bazarze”
  (cel `sklep`) i `h_sklep_las` = „Stać cię na nowy przedmiot: Kamień Powrotu → zbrojmistrz” (cel `kamien`), tak jak
  para `g_kowal_ulepsz` / `g_kowal_ulepsz_las`.
- `ustawienia.json`, cele: `sklep` = `SklepProba` (bez tego kontenera krok się nie pokazuje), znacznik nad punktem E
  zbrojowni (w kontenerze bazaru `MiasteczkoBazarGra` punkty E leżą w `Punkty/E <id>` — dokładną ścieżkę trzeba
  sprawdzić w Studio), `atrybut_sklep_stac_na` = `SklepStacNa`.
- Logika (Luau i lustro): krok (h) pokazuje się, gdy `SklepStacNa > 0`, **tylko zamiast kroku (c)** — tak jak (g),
  czyli nigdy przed TELEPORT, pierwszą walką, jajkiem i treningiem — i **po** (g): rozbiórka zapasu i ulepszenie są
  tańsze i ważniejsze. Żeby nie wisiał stale (gracz z dużą ilością Złota zawsze „stać na coś”), proponowane
  wyciszenie: krok znika po otwarciu okna sklepu i wraca dopiero, gdy `SklepStacNa` wzrośnie ponad wartość
  zapamiętaną przy ostatnim otwarciu (klient wskazówek trzyma ją u siebie; atrybut kontenera sklepu `OknoOtwarte`
  mówi, kiedy okno było otwarte).
- Testy wskazówek: krok (h) nie przykrywa (a)–(g), znika bez kontenera `SklepProba`, wraca po wzroście atrybutu.

## Co zgłosić właścicielowi stanu gracza
Lista źródeł wydatków (`PAKIETY_WYDATKOW`) to dziś `PetyProba` i `KowalProba` — `SklepProba` na niej nie ma, dlatego
za zakup płaci kowal (źródło `KowalProba`, cel `zakup_przedmiotu`). Po dopisaniu `SklepProba` do źródeł sklep mógłby
płacić sam, ale i tak kowal musiałby potwierdzić nadanie przedmiotu — płatność u właściciela przedmiotów jest
prostsza (jedno miejsce, jeden zapis). Propozycja: zostawić jak jest; ewentualnie osobne źródło tylko dla czytelności
dziennika wydatków.

## Przyjęte „do zmiany”
- Reguła zakładania po kupnie (wyżej) i to, że obejmuje także nowy przedmiot z łupu.
- Kolory stopni (szary / zielony / morski / złoty), teksty, zasięgi (10 st + 6 st zapasu serwera, okno do 20 st),
  limit zapytań 0,25 s.
- Zakładka na start: pierwszy stopień, w którym coś da się kupić.
- Przedmioty startowe spoza zestawu podstawowego (np. hełm rycerza, 75 Złota) też są w sklepie — zgodnie z katalogiem;
  dalej wypadają z walk.
- Łup z walk losuje wyłącznie ze stopnia startowego (jak dziś); stopnie krain w łupie — do decyzji.
- Okno kowala pokazuje najwyżej 8 wierszy: gracz z wieloma kupionymi przedmiotami widzi najpierw założone kupione,
  potem resztę posiadanych — nie wszystkie zmieszczą się na liście (do ulepszenia trzeba przedmiot założyć). Okno
  kowala wymaga przewijania albo zakładek stopni — do zrobienia razem z docelowym oknem.
- Napis po łupie „Nowy przedmiot: … Założony.” pojawia się także wtedy, gdy reguła zostawiła lepszy przedmiot.
- Sprzedaży przedmiotów (odkupu) nie ma.

## Próba w grze 19.11.2026 (Studio, tryb Play) — 12 × OK
Budowa: `stroje_proba/zbuduj.py --skrypty`, `kowal_proba/zbuduj.py` (pełna), `sklep_proba/zbuduj.py`; potem
`testy/proba_play.py` (pełny przebieg 12/12; pierwszy przebieg 10/12 — poprawki niżej).

| Punkt | Wynik |
|---|---|
| S00–S01 | kontenery, skrót danych = lokalny, serwer i klient gotowe, zgodność logiki „OK 42/42”, okno podpięte pod E |
| S02 | prawdziwe E przy zbrojmistrzu → okno (zakładka startowa, 7 wierszy, oferta wojownika 28 pozycji); na ekranie jedno okno — makieta `Shop` schowana |
| S03 | kupno prawdziwym kliknięciem: pas leśny za 100 Złota (20 000 → 19 900), „Kupiono: … Założono od razu.” |
| S04 | pas w stroju przymierzalni |
| S05 | hełm bagienny założył się sam, leśny (niższy stopień) nie; „Załóż” kliknięciem zmienia |
| S06 | miecz leśny: wpis kowala broń 0 → 2, obrażenia bohatera 128 → 130 |
| S07 | odmowy: za mało Złota, za niski poziom, posiadany, inna klasa, nieznany, część zbroi, daleko — dane i Złoto bez zmian |
| S08 | ekran 667 × 375: tekst 14 pt, okno w ekranie (góra 3%, dół 97% wysokości) |
| S09 | komplety leśny, bagienny, Dżungli trzech klas kupione i w całości na postaci (9 zrzutów) |
| S11 | prawdziwa walka w kupionym komplecie Dżungli (TELEPORT → chmury → Las, E przy slime'ie): bohater L30 broń 134 / pancerz 66 = wzór + wpis kowala (broń 6, pancerz 18), model w walce w komplecie, karta wyniku |
| S10 | konsola bez wierszy o sklepie i kowalu |

Poprawki po pierwszym przebiegu: S08 mierzył okno względem całego ScreenGui (z `IgnoreGuiInset` pozycje są przesunięte
o pasek u góry) — teraz względem ramki ekranu; S09 zakłada przyciskiem „Załóż” przedmiot kupiony wcześniej (hełm
bagienny z S05 — reguła zakładania słusznie go nie zdjęła); zdjęcia postaci na placu startowym bazaru zamiast przy
ladzie (kamera wpadała w ladę), plecami do tablicy „RANKING SERWERA” (nazwy graczy nie trafiają na zrzut). W kodzie
gry jedna zmiana: chowanie makiety `Shop` po E zbrojowni (wyżej).

Zrzuty (`klatki/`): `s02_okno_sklepu` (komputer), `s08_okno_maly_ekran` (667 × 375), `s03_po_kupnie`,
`s05_zaloz_recznie`, `s04_postac_po_kupnie`, `s09_<klasa>_<stopień>` (9 postaci), `s11_walka_w_komplecie`.

Zauważone: na zrzutach z komputera (tekst 14 pt, zrzut zmniejszony do 1280 px) w oknie nie widać liter „ś ę ż ń ć”
(„Le ny”, „D ungli”). Sprawdzone osobno w grze w pełnej rozdzielczości: litery są, ale Roblox bierze je z cieńszej
czcionki zastępczej (FredokaOne ich nie ma), więc przy małym tekście są blade i znikają po zmniejszeniu zrzutu; od
ok. 18 pt i na ekranie telefonu (okno powiększone) są dobrze widoczne. Do decyzji przy docelowym oknie: większy tekst
na komputerze albo czcionka z polskimi literami.

## Czego nie sprawdzono
- Dwóch graczy naraz i zapisu postępu (przełącznik zapisu zostaje wyłączony).
- Kliknięcia w figurę zbrojmistrza (ShopClient otwiera wtedy makietę `Shop`, a sklep — nie; okno sklepu otwiera
  tylko E).
- Prawdziwego telefonu (tylko emulacja 667 × 375 atrybutem `EmulacjaEkranu`).
