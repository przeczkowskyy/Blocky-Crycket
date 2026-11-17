# Dźwięk gry — własne efekty i muzyka stref (podpięcie bez wgranych plików)

> **Status: propozycja (17.11.2026), prototyp — działa tylko w Roblox Studio.** Pliki audio NIE są wgrane do Roblox
> (na wgranie czekamy na zgodę człowieka). Do tego czasu identyfikatory w `identyfikatory.json` są 0: muzyki nie ma,
> a walka gra dzisiejsze dźwięki wbudowane w klienta. Po wgraniu wystarczy jedno polecenie (niżej).

## W skrócie

- **Kontener** `Workspace/DzwiekGra` (atrybut `Wygenerowane = true`): moduł `Moduly/KatalogDzwiekow`, skrypt klienta
  `MuzykaStref` i haczyk testowy `Sygnaly/SterowanieMuzyki`. Żadnych części, niczego nie zmienia w cudzych kontenerach.
- **Efekty walki**: 22 efekty siedzą w JEDNYM pliku `assets/audio/arkusz/sfx_arkusz_a.ogg` (arkusz). Odtwarzacz walki
  prototypu (`swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau`, także w obu lasach) gra z niego odcinki
  (`Sound.PlaybackRegion`), gdy kontener jest i arkusz ma identyfikator ≠ 0. Bez tego — dźwięki wbudowane jak dziś.
- **Muzyka stref**: bazar (3 utwory na zmianę) i las-pas (2 utwory), płynne przejścia, przyciszenie na czas walki.
  Menu główne (ekran Pawła) ma tylko pozycję w katalogu — skrypt go nie gra.
- **Wpisanie identyfikatorów po wgraniu**: `python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory <plik.json>`.

## Pliki

| Plik | Co to |
|---|---|
| `zbuduj.py` | budowniczy: `--sucho` (odświeża katalog, kontrola, plan), pełna budowa, `--skrypty`, `--usun`, `--identyfikatory plik.json`, `--studio <id>` |
| `ustawienia.json` | głośności efektów, które zdarzenie walki gra który efekt (i czy jest uderzeniem), odgłosy potworów, muzyka stref (utwory, głośność, czas przejścia, przyciszenie w walce) |
| `identyfikatory.json` | identyfikatory zasobów Roblox: arkusz efektów i siedem pętli muzyki (dziś 0) |
| `zrodla/KatalogDzwiekow.luau` | **wygenerowany** z mapy arkusza (`assets/audio/arkusz/sfx_arkusz_a.json`: początek, koniec, atak, szczyt każdego efektu), `ustawienia.json` i `identyfikatory.json` — nie edytować ręcznie |
| `zrodla/MuzykaStref.client.luau` | klient: strefa z położenia postaci, utwory na zmianę, przenikanie, przyciszenie w walce |
| `testy/test_dzwieku.py` | testy bez Studio: katalog = mapa arkusza i ustawienia, wpisywanie identyfikatorów, strażniki, odtwarzacz zna zdarzenia |
| `testy/proba_play.py` | próba w Play bez wgranych plików (lista D1–D6 w nagłówku) |

## Jak wpisać identyfikatory po wgraniu

Plik JSON w jednej z dwóch postaci:

```json
{"arkusz": 1234567890, "muzyka": {"muzyka_02_bazar_targ_petla": 1234567891, "muzyka_05_las_a_petla": 1234567892}}
```

albo rejestr narzędzia wgrywania (`assets/audio/wgrane.json` z `tools/roblox_upload_audio.py`: lista `wgrane` z polami
`plik` i `assetId` — plik `…/sfx_arkusz_a.ogg` to arkusz, `…/muzyka_XX_…_petla.ogg` to utwory). Potem, w Studio
w trybie Edit:

```
python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory <plik.json>
```

Polecenie sprawdza nazwy i liczby (nieznana nazwa albo liczba ≤ 0 = błąd, nic nie zapisuje), zapisuje
`identyfikatory.json`, odświeża `zrodla/KatalogDzwiekow.luau` i wysyła moduł do `Workspace/DzwiekGra` (jak
`--skrypty`). Z `--sucho` tylko zapis w repozytorium. Odtwarzacza walki nie trzeba przebudowywać — czyta katalog przy
każdej walce.

## Jak działa

**Efekty w walce** (`OdtwarzaczWalki2`, „Własne dźwięki” w nagłówku pliku):
- `przygotujScene` szuka `Workspace/DzwiekGra/Moduly/KatalogDzwiekow`; gdy arkusz ma identyfikator, robi pulę 6
  dźwięków z tym plikiem (`arkusz.naraz`). Każdy odcinek: `PlaybackRegionsEnabled = true`, `PlaybackRegion =
  (początek + pominięty wstęp, koniec)`, `TimePosition = początek`, zapasowe zatrzymanie po długości odcinka.
- **Uderzenia** (cios, krytyk, blok, unik, kula ognia, lodowy pocisk, kwaśny plusk galarety): start planowany w czasie
  sceny tak, żeby od startu do trafienia minęło `szczyt` sekund RZECZYWISTYCH przy bieżącym tempie i zwolnieniach
  (`Sesja:tempoSceny`). Gdy zdarzenie zaczyna się za późno (np. cios krytyczny ma 1,36 s świstu przed uderzeniem, a przy
  ×4 zdarzenie trwa ułamek sekundy), odcinek gra od razu z pominiętym wstępem — najwyżej do 0,03 s przed `atak`.
  Wtedy wbudowany dźwięk uderzenia nie gra (jeden dźwięk na trafienie).
- **Reszta zdarzeń**: rzut umiejętności (Skupienie, Kamienna skóra, czar Maga), tarcza magiczna (Bariera), tik
  trucizny i podpalenia, ogłuszenie (nałożenie), zwycięstwo i porażka (zamiast melodii z tonu), „awans” przy
  wskrzeszeniu (wznoszący pasaż — w walce nie ma awansu poziomu), monety (łup), klik przycisków, zarodniki przy chmurze,
  odgłosy potworów przy ich umiejętności i w ich radości po wygranej (galareta, wilk, troll, zarodniki, ryk strażnika).
  Zdarzenie bez wpisu w katalogu (strzała, krwawienie, upadek, łomot) gra dźwięk wbudowany.
- Wynik odtworzenia (atrybuty kontenera walki u klienta): `OstatniZestawDzwiekow` („arkusz” / „wbudowany”),
  `OstatnieOdcinkiArkusza` (JSON: efekt, region w pliku, pominięty wstęp, odchylenie szczytu od trafienia),
  `OstatnieRegionyArkusza`.

**Muzyka stref** (`MuzykaStref`): co 0,5 s strefa z położenia postaci — prostokąty gruntu map policzone przy budowie
z `swiat/miasteczko_bazar/czesci.json` (bazar: X 882–1066, Z −790…−610) i `swiat/las_pas/czesci.json` (las-pas: X
1066–2066, Z −788…−612); strefa liczy się tylko, gdy jej mapa (`Workspace/MiasteczkoBazar`, `Workspace/LasPas`) stoi w
miejscu (tylko odczyt). Dwa dźwięki na zmianę, przenikanie `przejscie_s` (2,5 s), każdy utwór raz do końca, potem
następny utwór strefy; w walce (odtwarzacz prototypu `czyTrwa`) głośność × `przyciszenie_walki` (0,25) w 0,8 s. Utwór
z identyfikatorem 0 jest pomijany; strefa bez utworów = cisza bez komunikatów w konsoli.

**Próba bez wgranych plików** (tylko Play, lokalne atrybuty `Workspace/DzwiekGra` u klienta): `TestArkuszId` =
dowolny dźwięk (np. `rbxasset://sounds/action_falling.mp3`, wbudowany w klienta), `TestArkuszSkala` = mnożnik czasów
odcinków (krótszy plik); muzyka: `Sygnaly/SterowanieMuzyki:Invoke("probny", strefa, id)` i `("wymus", strefa)`.

## Wyniki (17.11.2026)

- Bez Studio: `testy/test_dzwieku.py` **11/11**, `zbuduj.py --sucho` kod 0 (katalog: 22 efekty, 22 zdarzenia, strefy
  bazar 0/3 i las 0/2 utworów z identyfikatorem, menu niepodpięte).
- W Studio: kontener zbudowany (`zbuduj.py`, 5 instancji, 2 skrypty), `testy/proba_play.py` **6/6** (okno na
  wierzchu, bez wgranych plików, końcowy kod o 09:47; wyniki poza repozytorium):
  - D1 `PlaybackRegionsEnabled` i `PlaybackRegion` istnieją i działają (zapis i odczyt 1,5–2,5);
  - D2 katalog z identyfikatorem 0 → walka na dźwiękach wbudowanych (21 zagranych, 0 odcinków);
  - D3 „arkusz” próbny (`rbxasset://sounds/action_falling.mp3`, czasy × 0,19): 14 odcinków (cios, krytyk, blok, unik,
    fanfara, monety, warknięcie wilka), region każdego = odcinek z katalogu × skala, pozycja odtwarzania zawsze
    w regionie (30 próbek), **szczyt 11 uderzeń względem klatki trafienia: od −0,028 do +0,004 s** (×1, czas
    rzeczywisty);
  - D4 po zabraniu identyfikatora próbnego — znów dźwięki wbudowane;
  - D5 muzyka: przy tablicy brak strefy i cisza; na bazarze strefa „bazar”, w lesie-pasie „las” (bez identyfikatorów
    cisza); z identyfikatorem próbnym gra utwór bazaru z głośnością 0,35, w walce przyciszenie 0,25; po zabraniu cisza,
    0 błędów;
  - D6 konsola bez błędów i ostrzeżeń `[DzwiekGra]` / `[TestWalki2]`.
- Poprawione po pierwszej próbie: zabranie identyfikatora próbnego i wymuszenia w jednym wywołaniu zostawiało grający
  utwór (strefa „brak” = „brak” — bez przeliczenia); teraz haczyki wymuszają przeliczenie (`przelicz`).

**Niesprawdzone:** prawdziwe pliki (głośność względem siebie, czy cios krytyczny z 1,36 s świstu nie męczy, czy pętle
muzyki są płynne w Roblox), dwa różne pliki w jednym arkuszu po transkodowaniu Roblox (czasy odcinków mogą się
przesunąć o kilka ms — warto odsłuchać po wgraniu), telefon, przejście przez chmury (efekt `chmury` jest w katalogu,
ale pakiet `swiat/teleport_chmury` go nie gra).

## Przyjęte, do zmiany (ustawienia agenta, nikt ich nie słyszał)

- mapowanie zdarzeń na efekty i głośności (`ustawienia.json`); arkusz × 0,6, muzyka 0,35;
- „awans” gra przy wskrzeszeniu (w walce nie ma awansu poziomu);
- odgłos potwora tylko przy jego umiejętności i w radości po wygranej (nie przy każdym ciosie);
- strzała, krwawienie, upadek i łomot zostają na dźwiękach wbudowanych (w arkuszu nie ma takich efektów);
- muzyka: każdy utwór raz do końca i następny (nie pętla jednego), przenikanie 2,5 s, w walce 25% głośności;
- poza bazarem i lasem-pasem (np. plac startowy, stary las) — cisza.

## Bezpieczeństwo i zasady

Każdy skrypt i moduł zaczyna się od strażnika `RunService:IsStudio()`. Budowniczy rusza tylko `Workspace/DzwiekGra`
z atrybutem `Wygenerowane` (cudzy obiekt o tej nazwie = przerwanie), ustawia punkty historii przed i po, działa tylko
w trybie Edit, niczego nie zapisuje w miejscu, nie publikuje i nie wgrywa. Przed publikacją miejsca:
`python -B swiat/dzwiek_gra/zbuduj.py --usun`.
