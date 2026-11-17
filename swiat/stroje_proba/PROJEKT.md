# Próba ubierania postaci w grze i w walce (D-071) — projekt pakietu

> **Status: propozycja (prototyp w Studio), nie kanon i nie kod gry.** Działa tylko w Roblox Studio (strażnik
> `RunService:IsStudio()` w każdym pliku; poza Studio serwer usuwa cały kontener). Przed publikacją miejsca:
> `python -B swiat/stroje_proba/zbuduj.py --usun`. Część A (kod, dane, testy bez Studio) i część B (budowa w Studio,
> próby w Play, zrzuty `klatki/`) — 17.11.2026; wyniki z Studio, miejsce stojaka i poprawki: `README.md`.

Wymaganie (D-071): każdy założony przedmiot widać na modelu 3D bohatera, także w walce i w każdym klipie walki.
Kontrakt ciała i przedmiotów: `swiat/postacie/EKWIPUNEK.md`; katalog: `swiat/postacie/przedmioty.json`.

## 1. Jak to działa (w skrócie)

1. **Dane** (`dane.py` → `zrodla/DaneStrojow.luau`, 75 tys. znaków): dla Wojownika (Rycerz), Zwiadowcy i Maga (Kot-Mag)
   gołe ciało (bryły z `cialo()` modułu bohatera, włosy jako akcesorium ze znacznikiem `Wlosy`) i 20 przedmiotów
   z katalogu (`przedmioty()` modułu), każda bryła **w układzie środka części kości rigu Roblox**. Nazwy, sloty,
   klasy, `czesc_od`, `ukrywa` i segmenty bierzemy z katalogu i sprawdzamy z modułem (rozjazd = błąd danych).
2. **Szkielet** = szablon aktora próby walki (`Workspace/TestWalki2/Aktorzy/<klasa>`: HumanoidRootPart, części kości,
   Motor6D, zaczepy, punkty `Punkt_*`). `Ubieranie.zbuduj` kopiuje szablon, **zdejmuje jego bryły** i dokłada bryły
   stroju: gołe bryły kości bez powłoki, akcesoria ciała bez schowanych znaczników, segmenty założonych przedmiotów.
   Każda bryła ma `Weld` (Part0 = część kości, `C0` = położenie z danych) — idzie za kością w każdym klipie.
3. **Klipy** zostają wspólne dla klasy (EKWIPUNEK.md zasada 0.2): te same `DaneAktorow/<klasa>` i moduł `Klipy`.
   Kapelusz i kostur kota są na kościach nośnych `HatPivot` / `StaffPivot`, więc w upadku spadają jak dawniej.
4. **Źródło prawdy** = serwer (`SerwerStrojow`): atrybut **gracza** `StrojProba_<klasa>` = `id,id,…` (pusty napis =
   goły bohater, brak atrybutu = dawny szablon walki). Ustawia go wyłącznie serwer po sprawdzeniu każdej reguły
   (`LogikaStrojow`); klient prosi przez `Zdalne/ZmienStroj` (RemoteFunction) i tylko czyta.
5. **Walka**: `swiat/test_walki2/zrodla/Aktorzy.luau` (`Aktorzy.nowy`) woła `Ubieranie.dlaAktora(klasa, szablon)`.
   Klasa = id strony w opisie walki (`walka.strony.<strona>.id`), więc działa tak samo w próbie walki (tablica) i w
   walkach w lesie (stary las i las-pas grają odtwarzaczem próby). Bez kontenera `StrojeProba`, bez atrybutu u gracza
   albo przy błędzie — **dawny szablon** (stare próby walki bez zmian).
6. **Przymierzalnia** (`Workspace/StrojeProba/Przymierzalnia`): podłoga, rama z taflą lustra, podest, tablica,
   wieszak i punkt **E**. Na podeście stoi lokalny podgląd bohatera w stroju gracza (ten sam `Aktorzy.nowy`, więc te
   same klipy). E otwiera **tymczasowe okno**: zakładki klas, po jednym przedmiocie na slot (`<` `>`), zestawy
   „Goły” / „Komplet”, „Dawny wygląd”, przycisk ruchu (każdy klip po kolei albo „Wszystkie”). Kamera na podgląd
   (trzymana co klatkę, środek postaci na 0,21 wysokości ekranu, nad oknem), postać gracza schowana i bez ruchu do
   zamknięcia okna (X albo odejście dalej niż 16 st). Podgląd czeka, aż szablon walki dojdzie strumieniowaniem.

## 2. Punkty zaczepienia

| Przedmiot | Kość w rigu Roblox | Jak siedzi |
|---|---|---|
| segment kostny (hełm, zbroja, spodnie, pas, rękawice, buty, kołczan, szata) | kość segmentu (`Head`, `UpperTorso`…) | bryły w układzie środka części kości (w danych gry: `Ekw<Kosc>Attachment` = środek klocka) |
| broń w prawej ręce (miecz, sztylet) | `RightHand` | `RightGripAttachment` |
| druga ręka (tarcza, łuk) | `LeftHand` | `LeftGripAttachment` |
| kapelusz kota | `HatPivot` | korekta chwytu kota: `KapeluszAttachment` (+0,02) |
| kostur kota | `StaffPivot` | korekta chwytu kota: `KosturAttachment` (−0,08; −90°) |

Rig z części nie potrzebuje obiektów `Attachment` dla segmentów kostnych: `Weld` do części kości z `C0` z danych robi
to samo (droga przez siatki, `Accessory` i `AddAccessory` — EKWIPUNEK.md pkt 5 — dalej niesprawdzona; ta próba jej
nie używa i niczego nie wgrywa).

## 3. Co sprawdzają testy bez Studio (`testy/test_strojow.py`)

- strój odniesienia (Wojownik z tarczą, pełny Zwiadowca, pełny Mag) złożony z naszych danych = szablon walki
  `swiat/test_walki2/dane/<klasa>.json` co do bryły (127 / 182 / 166 brył, te same kości i zaczepy);
- **każdy** dopuszczalny strój (128 + 128 + 16) złożony z naszych danych = biblioteczne `ubierz()` modułu bohatera;
- w każdej klatce każdego klipu nic nie schodzi pod ziemię głębiej niż w stroju odniesienia (najwięcej 0,030 studa:
  gołe dłonie Zwiadowcy są o 0,02 grubsze niż w rękawicach);
- w ostatniej klatce upadku kapelusz i kostur kota leżą na ziemi w każdym stroju, w którym są;
- logika stroju: przypadki wzorcowe w obu ustawieniach spodni i obu doborach, ten sam plik Luau w `luau_mini` =
  lustro w Pythonie (3600 losowych wywołań + każdy strój), 4 zepsute wersje logiki wykryte;
- kontrola statyczna Luau, haczyk w `Aktorzy.luau`, `zbuduj.py --sucho`, brak ścieżek lokalnych.

## 4. Przyjęte, do zmiany (nie decyzje — czekają na Karola i Pawła)

1. **Spodnie = część zbroi.** Nogawice Rycerza i spodnie Zwiadowcy (`czesc_od`) nie mają własnego wyboru: zakładają
   się i zdejmują ze zbroją / kirysem (jak rekomenduje EKWIPUNEK.md pkt 8.1; gra nie ma slotu `Legs`). Przełącznik:
   `"spodnie": "osobny_slot"` w `ustawienia.json` → w oknie wiersz „Spodnie” (slot `Legs`), bez przebudowy modeli.
2. **Łuk Zwiadowcy z kołczanem = jeden przedmiot w drugiej ręce** (`OffHand`, jak w katalogu): łuk w lewej dłoni,
   kołczan na plecach. Sztylet w slocie broni.
3. **Upadek bez zbroi: klip wspólny, bez korekty.** Goły Rycerz (i każdy strój bez zbroi) leży w ostatniej klatce
   upadku **0,247 studa nad ziemią**, kot bez szaty **0,198**, Zwiadowca leży na ziemi w każdym stroju. Propozycje:
   (A) korekta korzenia w odtwarzaczu liczona ze stroju (najniższa bryła w ostatniej klatce — dane już są),
   (B) osobny klip upadku gołego ciała, (C) zostawić (widać szparę tylko w finale walki).
4. **Dobór przedmiotów: tylko własnej klasy** (`"dobor": "klasa"`, pole `klasy` z katalogu). Przełącznik `"cialo"`
   pozwala na stroje krzyżowe (Rycerz w kapturze Zwiadowcy, kostur w ręce Rycerza) — sprawdzone tylko w logice.
5. **Przeciwnik „lustro”** w próbie walki nosi strój gracza (obaj aktorzy powstają przez ten sam `Aktorzy.nowy`).
6. **Brak stroju = dawny wygląd.** Dopóki gracz nic nie zmieni (albo po „Dawny wygląd”), walka bierze dawny szablon.
   Strój żyje w atrybutach gracza do końca sesji (bez zapisu — to próba).
7. **Strój to tylko wygląd.** Silnik walki dalej liczy postać wzorcową (np. Wojownik blokuje tarczą także bez tarczy
   w stroju — klip bloku jest wspólny); punkty `Bron` / `Tarcza` i zasięgi ciosów są z postaci odniesienia.
8. **Okno tymczasowe** w pasie między kolumnami przycisków HUD (x 0,24–0,76) i pod panelem gracza (y od 0,47 ekranu),
   osobny `ScreenGui` (`StrojeProbaOkno`, DisplayOrder 15). Docelowe okno 2D robi Paweł (D-093).

## 5. Do przekazania Pawłowi (moduł `Items`, okno ekwipunku) — kod Pawła nie był zmieniany

- `src/shared/Items.luau` nie zna slotu `OffHand` (tarcza, łuk) ani pól `body`, `classes`, `hides`, `parent`,
  `meshes` — propozycja jest w `swiat/postacie/roblox/PrzedmiotyPropozycja.luau`; próba czyta własny katalog.
- Okno ekwipunku (`EquipmentPanelClient`): gdy ma zakładać przedmioty na model, wystarczy, że poprosi serwer o to
  samo co okno próby (`ZmienStroj`: `zaloz` / `zdejmij`) albo że serwer gry ustawi atrybut `StrojProba_<klasa>`
  (format wyżej); wygląd w walce i na podglądzie złoży wtedy `Ubieranie`. Do ustalenia: nazwa atrybutu w grze i czy
  strój ma być w zapisie gracza (dziś nie jest).
- Gdy przyjdzie slot `Legs` — patrz pkt 4.1 (jedna zmiana w ustawieniach).

## 6. Pliki

| Plik | Co to |
|---|---|
| `ustawienia.json` | jedyne źródło liczb i tekstów pakietu (sloty okna, stojak, kamera, okno, przełączniki z pkt 4) |
| `dane.py` | generator `zrodla/DaneStrojow.luau` (`--sprawdz`: aktualność + zgodność z szablonem walki) |
| `logika_strojow.py` | lustro `LogikaStrojow.luau` w Pythonie (testy) |
| `zrodla/LogikaStrojow.luau` | czysta logika stroju (wykonywana też przez `luau_mini`) |
| `zrodla/Ubieranie.luau` | składanie modelu z ciała i przedmiotów (walka i podgląd) |
| `zrodla/OknoStrojow.luau` | tymczasowe okno przymierzalni |
| `zrodla/SerwerStrojow.server.luau`, `zrodla/KlientStrojow.client.luau` | serwer (źródło prawdy) i klient (podgląd, E, kamera) |
| `sprawdz_luau_strojow.py` | kontrola statyczna Luau |
| `zbuduj.py` | budowa w Studio (`--sucho`, `--skrypty`, `--walka`, `--usun`) |
| `testy/test_strojow.py` | testy bez Studio |
| `testy/proba_play.py` | próba w Play (część B) |

Zmiana poza pakietem: `swiat/test_walki2/zrodla/Aktorzy.luau` — funkcja `zeStrojem` i jedna linia w `Aktorzy.nowy`
(`local model = zeStrojem(klucz, wzor, opcje.stroj) or wzor:Clone()`), opis opcji `stroj`. Nic więcej w próbie walki,
lasach, klipach ani przeciwnikach.

## 7. Jak uruchomić

Bez Studio:
```
python -B swiat/stroje_proba/dane.py                 # po zmianie katalogu, modułu bohatera albo ustawień
python -B swiat/stroje_proba/testy/test_strojow.py   # ok. 30 s
python -B swiat/stroje_proba/zbuduj.py --sucho
```
W Studio (tryb Edit, część B): `zbuduj.py` (kontener i stojak), `zbuduj.py --walka` (tylko moduł `Aktorzy` w
`TestWalki2`), potem w Play `testy/proba_play.py`.

## 8. Ryzyka

- Kod Luau klienta, okna i serwera nie był jeszcze uruchomiony w Studio (logika — tak, w `luau_mini`).
- Wymiana `TestWalki2/Moduly/Aktorzy` w Studio (`--walka`) wysyła tylko ten moduł; kto przebuduje próbę walki jej
  `zbuduj.py --skrypty`, wyśle ten sam plik (z haczykiem) — zgodnie.
- Gdy ktoś zmieni bryły bohatera albo przebuduje `dane/<klasa>.json` walki, `dane.py --sprawdz` (i `zbuduj.py
  --sucho`) zgłosi rozjazd — trzeba wtedy przebudować `DaneStrojow.luau`.
- Miejsce stojaka: budowa szuka go sama (pierścienie 24–42 st wokół SpawnLocation, z dala od tablicy Training
  Center, bazaru i portalu), ale nie widzi ścieżek — 17.11 postawiła stojak na ścieżce, więc stoi w punkcie ręcznym
  (`RecznyPunktStojaka`, README). Atrybut przechodzi na odbudowany kontener.
