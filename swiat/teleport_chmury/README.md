# Teleport przez chmury — prototyp w Roblox Studio

> **Sprzątanie mapy 26.11.2026 (zlecenie Karola):** „Miasteczko” to zawsze bazar — przybycie z atrybutu `MiasteczkoBazarGra.PunktStartuBazaru`, a zapas (`gdy_jest: MiasteczkoBazar`) to start bazaru ze znaczników jego mapy (`zbuduj.py` sprawdza zgodność z `swiat/miasteczko_bazar/znaczniki.json`). „Las” to las-pas (uchwyt `LasPasGra/Sygnaly/PrzeniesDoLasu` albo punkt mapy `LasPas`). Wpisy starego miasteczka, starego lasu i `Workspace/LasTeleport` oraz ich obszary usunięte — tych kontenerów nie ma już w miejscu. Usuwanie z miejsca: `python -B tools/studio/sprzatanie_mapy.py` (najpierw `--sucho`); start gry na starcie bazaru: `python -B tools/studio/start_w_miasteczku.py`.

*Status: **propozycja / prototyp** (nie kanon). Wymaganie Karola z 16.11.2026 — doprecyzowanie D-075: pod przyciskiem
Teleport nie ma okna mapy ani żadnego HUD. Kamera wchodzi w chmury, z chmur wyłania się widziany z góry pas krain, a po
wyborze znów są chmury i kamera opada z góry na gracza w nowym miejscu. Zbudowane i sprawdzone w Studio w nocy
16/17.11.2026.*

Kontener w Studio: `Workspace/TeleportChmury` (atrybut `Wygenerowane = true`). Działa tylko w Studio. Poza Studio
skrypt serwera usuwa cały kontener, tak samo jak `LasTeleport` i `LasPotwory`.

## Jak to wygląda (zrzuty w `klatki/`)

| Klatka | Co widać |
|---|---|
| `0_miasteczko_przed.jpg` | gracz w miasteczku, HUD z przyciskiem TELEPORT |
| `1_wejscie_w_chmury.jpg` | kamera wznosi się, kłęby chmur zamykają obraz |
| `1b_biel_pelna.jpg` | pełna biel: tu kamera przeskakuje nad makietę |
| `2_wylonienie_z_chmur.jpg` | z rozchodzących się chmur wyłania się pas krain |
| `3_makieta_z_gory.jpg` | pas z góry: 9 krain w jednej linii, Miasteczko i Las otwarte, reszta ciemna i z kłódką |
| `4_podswietlony_wybor.jpg` | wskazany Las: złota obwódka, płytka podniesiona, złota strzałka |
| `5_zamknieta_kraina.jpg`, `5b_odmowa.jpg` | wskazana zamknięta Pustynia, potem odmowa (czerwona obwódka; płytka się trzęsie) |
| `6_zanurzenie.jpg` | kamera nurkuje ku Lasowi, chmury się zamykają |
| `7a_opadanie_poczatek.jpg`, `7_opadanie_na_gracza.jpg` | kamera opada z góry na gracza na Polanie Przybycia nowego lasu |
| `8_po_przejsciu_las.jpg` | koniec: kamera za plecami gracza, HUD wrócił |
| `edit_makieta.jpg` | makieta w trybie Edit (kadr kamery edytora) |

## Przebieg

1. **A — wejście w chmury (1,1 s).** Kamera wznosi się pionowo nad swoim miejscem i obraca w dół na gracza. Przelatuje
   przez kolumnę kłębów nad graczem, a zasłona chmur przy kamerze zamyka obraz do pełnej bieli.
2. **Przeskok w bieli.** Kamera przenosi się nad makietę pasa. W tym czasie serwer podaje, co gracz ma odblokowane, a
   klient przyciemnia zamknięte krainy i pokazuje kłódki.
3. **B — wyłonienie (1,0 s).** Chmury rozchodzą się na boki i odsłaniają makietę.
4. **Wybór, bez HUD:**
   - dotyk lub kliknięcie krainy wybiera ją od razu;
   - mysz: najechanie podświetla krainę;
   - klawiatura: strzałki albo A/D przesuwają złotą strzałkę, Enter albo spacja wybiera;
   - pad: krzyżak albo gałka przesuwa, A wybiera;
   - zamknięta kraina tylko się trzęsie i dostaje czerwoną obwódkę;
   - rezygnacja: dotknięcie z dala od pasa, Backspace, B na padzie albo otwarcie menu Roblox (Esc);
   - po 60 s bez wyboru przejście samo wraca.
5. **C — zanurzenie (0,9 s).** Kamera nurkuje ku wybranej krainie, a chmury znów się zamykają. W tym czasie serwer
   sprawdza wybór, wczytuje okolicę celu i przenosi postać.
6. **D — opadanie (1,4 s).** Z bieli kamera opada pionowo nad swoją końcową pozycję za plecami gracza i na końcu podnosi
   wzrok. Wtedy oddaje sterowanie modułowi kamery bez skoku obrazu. Nie wchodzi w dachy ani korony drzew: odsuwa ją
   promień od głowy gracza.

**Klient niczego nie przenosi.** Prosi serwer przez `Zdalne/Teleport` (RemoteFunction). Serwer sprawdza w tej
kolejności:

1. dane;
2. limit próśb (12 na 5 s);
3. czy przeniesienie już trwa;
4. blokadę czasu (3 s);
5. czy kraina istnieje;
6. czy jest odblokowana dla tego gracza;
7. czy postać żyje;
8. punkt przybycia.

Potem idzie tą samą bezpieczną drogą co `TeleportLasu`: najpierw `RequestStreamAroundAsync`, potem `PivotTo` i zerowanie
prędkości.

**Punkty przybycia** (`krainy.json` → `przybycie`, pierwszy pasujący):
- **Las, gdy stoi `Workspace/LasPasGra`** (las-pas w grze, `swiat/las_pas_gra`): postać przenosi uchwyt pakietu
  `LasPasGra/Sygnaly/PrzeniesDoLasu` (punkt „las” = Polana Przybycia). Uchwyt dostaje `przelotPo = przelot_po_s`
  (2,4 s), więc przelot kamery przy pierwszym wejściu do lasu rusza dopiero po naszym opadaniu kamery. Dopisane
  17.11.2026 po próbie w Studio: bez tego przelot startował 1,2 s po przeniesieniu, w połowie opadania (dwa skrypty
  naraz na kamerze, ucięty początek przelotu). Gdy uchwyt odmówi (np. `za_szybko`), działa zwykły punkt niżej.
- **Las:** gdy w Workspace jest `LasPas`, gracz staje na Polanie Przybycia, w świecie (1114; y; −700). Wysokość daje rzut
  promienia w dół (tylko części z kolizją), z kontrolą wolnego miejsca. Bez `LasPas` gracz trafia do `LasTeleport.PunktLas`.
- **Miasteczko, gdy stoi `Workspace/MiasteczkoBazarGra`** (nowe miasteczko-bazar, `swiat/miasteczko_bazar_gra`;
  D-075: miasteczko to pierwszy blok pasa): start bazaru z atrybutów tego kontenera `PunktStartuBazaru` /
  `PatrzStartuBazaru` (tylko odczyt; wpis „atrybut”, dopisany 17.11.2026). Makieta zna też obszar bazaru
  (`obszary_xz` miasteczka: `[882, 1066, −790, −610]`).
- **Miasteczko bez bazaru:** `LasTeleport.PunktMiasteczka` (stare Krzywe Miasteczko, tylko odczyt atrybutu), a gdy go
  nie ma — liczby zapasowe z danych.
- **Krainy zamknięte** mają punkty z planu pasa (`swiat/biom_las/pas/plan_pasa.json`). Nie są używane, póki krainy są
  zamknięte.

W czasie przejścia klient zmienia lokalnie tylko te rzeczy i wszystkie przywraca przy każdym wyjściu (koniec,
rezygnacja, błąd, śmierć postaci, usunięcie skryptu):
- kamerę: typ, kąt widzenia i Focus;
- `ProximityPromptService.Enabled`;
- postać: WalkSpeed, JumpPower i JumpHeight = 0, AutoRotate wyłączone;
- widoczność ekranów gry (ScreenGui).

Wspólnego oświetlenia nie dotyka. Chmury to zwykłe kule tworzone u klienta (w `Camera`): bez wgrywania czegokolwiek i
bez GUI na ekranie.

**Potwory:** walkę w lesie zaczyna zawsze gracz podpowiedzią E — potwór nigdy nie atakuje sam (`LasPotwory`,
`plan_pasa.json` → `zasady`). W czasie przejścia podpowiedzi są wyłączone, a postać stoi, więc to wystarcza. Serwer
potworów nie musi nic wiedzieć o teleporcie.

## Pliki

| Plik | Co robi |
|---|---|
| `krainy.json` | **jedyne źródło liczb**: kolejność, nazwy, napisy, kolory, obszary krain w świecie, punkty przybycia, stan zamknięcia, makieta, kamera, czasy, chmury, limity serwera, sterowanie |
| `makieta.py` | geometria makiety z klocków: płytki, akcent każdej krainy, tabliczki, kłódki, obłoki, strzałka, chorągiewka „tu jesteś” |
| `zbuduj.py` | budowa i usunięcie kontenera; generuje `zrodla/Dane.luau`; kontrola na sucho |
| `zrodla/Dane.luau` | wygenerowany z `krainy.json` — nie edytować ręcznie |
| `zrodla/SerwerTeleportu.server.luau` | serwer: odblokowanie gracza, kontrole, przeniesienie, haczyk `SterowanieSerwera` |
| `zrodla/KlientTeleportu.client.luau` | klient: kamera, chmury, makieta, wybór, sprzątanie, haczyk `SterowanieKlienta` |
| `testy/proba_play.py` | próba w trybie Play (testy 1–6) i seria zrzutów (`--zrzuty`) |
| `testy/zrzut_edit.py` | zrzut makiety w trybie Edit |
| `wyniki/proba_play_20261117_0010.json` | wyniki pełnego przebiegu testów (przed uchwytem lasu-pasa) |
| `wyniki/proba_play_20261117_0100.json` | wyniki ostatniego pełnego przebiegu (z uchwytem lasu-pasa) |
| `wyniki/zrzuty_20261117_0009.json` | stan po ostatniej serii zrzutów |

## Budowa i usunięcie

```
python -B swiat/teleport_chmury/zbuduj.py --sucho     # bez Studio: dane, Dane.luau, makieta (561 części), kontrola Luau
python -B swiat/teleport_chmury/zbuduj.py             # buduje / odbudowuje Workspace/TeleportChmury (Studio w trybie Edit)
python -B swiat/teleport_chmury/zbuduj.py --skrypty   # tylko Dane + dwa skrypty (makieta zostaje)
python -B swiat/teleport_chmury/zbuduj.py --usun      # usuwa kontener
python -B swiat/teleport_chmury/testy/proba_play.py             # testy 1–6 w trybie Play (ok. 90 s), wynik do wyniki/
python -B swiat/teleport_chmury/testy/proba_play.py --zrzuty    # zrzuty do klatki/
```

Budowa działa tylko w trybie Edit i tylko w miejscu gry (PlaceId sprawdzany w każdym wysyłanym kodzie). Rusza wyłącznie
własny kontener: gdy pod tą nazwą stoi coś bez atrybutu `Wygenerowane`, przerywa. Przed budową i po niej stawia punkt
historii. Miejsca nie zapisuje i nie publikuje. Oświetlenie tylko czyta: obrót makiety liczy z kierunku słońca, tak żeby
słońce świeciło zza kamery.

Zmiana krain, kolorów, czasów albo kamery to edycja `krainy.json` i ponowna budowa. Nowa kraina potrzebuje do tego
funkcji akcentu w `makieta.py`.

## Przycisk TELEPORT w HUD (Paweł)

**Dziś działa bez zmian w plikach HUD.** Klient słucha `ReplicatedStorage.HUDButtonPressed` z nazwą `"Teleport"` — tego
samego sygnału używa już `EquipmentPanelClient`. Włącza to `sterowanie.sluchaj_hud = true` w `krainy.json`.

Wywołanie wprost to jedna linijka po stronie klienta:

```lua
local t = workspace:FindFirstChild("TeleportChmury") if t then t.Otworz:Fire() end
```

Jeśli Paweł doda tę linijkę, ustawiamy `sluchaj_hud = false`. Podwójne wywołanie i tak nic nie psuje: drugie, w czasie
przejścia, jest pomijane.

Inne uchwyty:
- **Czy przejście trwa:** atrybut kontenera `Trwa` (tylko u tego klienta).
- **Odblokowanie po strażniku**, ze skryptu serwera:

  ```lua
  workspace.TeleportChmury.Sygnaly.SterowanieSerwera:Invoke("odblokuj", "bagno", gracz)
  ```

- **Test w Studio:** klawisz **T** (`sterowanie.klawisz_testowy`).

## Co sprawdzone i z jakim wynikiem

Sprawdzono 17.11.2026 o 00:10 w Studio, w trybie Play, z jednym graczem i oknem gry 2041 × 1153. Wynik: wszystkie 6 testów
OK. Zapis: `wyniki/proba_play_20261117_0010.json`.

Po dopisaniu uchwytu lasu-pasa (wyżej, „Punkty przybycia”) próba powtórzona 17.11.2026 przy zbudowanym
`Workspace/LasPasGra`: o 00:33 (`przelot_po_s` 1,8) i o 01:00 (`przelot_po_s` 2,4) — za każdym razem 6/6 OK, test 1
przeniesiony przez `uchwyt LasPasGra.PrzeniesDoLasu` (odchyłka 0,0, ruch po W 13,9 st). Próba wstrzymuje na swój czas
przelot pasa haczykiem `zapomnijPrzelot` (inaczej zakotwiczyłby postać w teście 1). Sam przelot po chmurach sprawdza
`swiat/las_pas_gra/testy/proba_dodatkowa.py` (część „drogi”): przy 2,4 s chmury kończą się po 2,99 s od wyboru, a przelot
przejmuje kamerę po 3,78 s — bez nakładania. Zapis: `wyniki/proba_play_20261117_0033.json`,
`wyniki/proba_play_20261117_0100.json`.

**Lądowanie „Miasteczka” w nowym bazarze** (wpis w `krainy.json`, `zbuduj.py --skrypty`): próba powtórzona 17.11.2026
o 01:25 przy zbudowanym `Workspace/MiasteczkoBazarGra` — **6/6 OK**, test 2 (Las → miasteczko, prawdziwe kliknięcie
myszą) postawił postać na starcie bazaru (990; −697), odchyłka 0,0. Próba sama bierze cel testu 2 z atrybutu
`MiasteczkoBazarGra.PunktStartuBazaru` (bez bazaru — stare miasteczko jak wcześniej). Zapis:
`wyniki/proba_play_20261117_0125.json`. To samo przejście sprawdza próba bazaru (`swiat/miasteczko_bazar_gra`, B07:
portal krain → chmury → Las → chmury → „Miasteczko” → start bazaru, 0,0 st).

| # | Próba | Wynik |
|---|---|---|
| 1 | miasteczko → Las | OK. Postać stanęła dokładnie w (1114; −700) na Polanie Przybycia `LasPas` (punkt z rzutu promienia, odchyłka 0,0). Po przejściu klawisz W przesuwa postać o 14,9 st. Kamera Custom z postacią, podpowiedzi włączone, chmury usunięte, ekrany gry przywrócone, kąt widzenia 70°. |
| 2 | Las → miasteczko | OK. Wybór **prawdziwym kliknięciem myszy** (narzędzie `user_mouse_input`, współrzędne okna gry). Punkt z `LasTeleport.PunktMiasteczka`, odchyłka 0,01 (od 17.11.2026 01:25 z bazarem: start bazaru, odchyłka 0,0). |
| 3 | rezygnacja | OK. Dotknięcie z dala od pasa → powrót, postać w tym samym miejscu. Backspace → powrót. W pauzie fazy A klawisze W i spacja wciśnięte przez 0,8 s przesunęły postać o **0,0**. |
| 4 | zamknięta kraina | OK. Dotknięcie Bagna: potrząśnięcie, czerwona obwódka, wybór trwa dalej (1 odmowa). Prośba wprost do serwera z pominięciem makiety: `zamknieta`. Nieznana kraina: `nieznana`. Złe argumenty: `zle_dane`. |
| 5 | dwa szybkie żądania | OK. Drugie otwarcie w czasie przejścia: `trwa`. Dwie prośby naraz do serwera: jedna przeniosła, druga dostała `trwa`. Trzecia zaraz po nich: `za_szybko` (zostało 2,95 s). Postać przeniesiona raz. |
| 6 | błąd w połowie | OK. Wstrzyknięty błąd w fazie B i w fazie C: sprzątanie zadziałało, kamera wróciła do postaci, W przesuwa postać o 10–12 st. Przy błędzie w C serwer i tak przeniósł postać do miasteczka (odchyłka 0,01), a kamera ją znalazła. Śmierć postaci w czasie wyboru: przejście przerwane, po odrodzeniu kamera Custom z nową postacią. |

**Czasy** (z pomiarów klienta):

| Odcinek | Czas |
|---|---|
| A — wejście w chmury | 1,13–1,15 s |
| B — wyłonienie | 1,00–1,07 s |
| od przycisku do makiety gotowej do wyboru | **2,20–2,28 s** |
| od wyboru do oddania sterowania | **2,53–2,55 s** (C 0,93–0,95 + czekanie w bieli 0,13 + D 1,46–1,47) |
| całe przejście w jedną stronę bez czasu wyboru | **ok. 4,8 s** |
| wczytanie okolicy celu przez serwer (Studio) | 0,02–0,03 s |

**Czas klatki:**

| Pomiar | Średnio | p95 | Maks. |
|---|---|---|---|
| w czasie przejścia | 66,7–68,5 ms (14,6–15,0 kl./s) | 68–73 ms | 72–177 ms |
| bez przejścia, ta sama sesja | 66,7 ms (15,0 kl./s) | — | 68 ms |

Przejście nie obniża płynności. Samo 15 kl./s to ograniczenie Studia z oknem w tle (bez fokusu) — nie zaciemnienia
ekranu, jak zapisano w nocy — i nie jest miarodajne dla telefonu; przy oknie Studio na wierzchu (`tools/studio_okno.py
--na-wierzch`) pomiar trzeba powtórzyć.

**Kontrola bez Studio:** `zbuduj.py --sucho` — dane poprawne, punkty przybycia zgodne z planem pasa, reguły 1–4
`swiat/las_potwory/sprawdz_luau.py` (bilans bloków i nawiasów, strażnik Studio, zakazane wywołania) bez błędów.

**Poprawione po obejrzeniu zrzutów:**
- napisy na tabliczkach były maleńkie (limit 100 px przy 40 px/stud) — teraz 12 px/stud;
- kamera przy opadaniu przechodziła przez korony Bramy Pniaków — teraz opada pionowo i odsuwa się przed przeszkodą;
- chmury makiety były pojedynczymi kulami — teraz to obłoki z pięciu kul;
- strzałka była mała i blada od odblasku, bo była zwrócona wprost do słońca za kamerą — teraz jest większa i pochylona
  jak kłódki;
- wypełnienie podświetlenia zostało wyłączone (została złota obwódka);
- kąt widzenia makiety zmieniony z 40° na 50° (mniej mgły);
- w miejscu nie ma `PlayerModule` (czekanie na niego zabierało 5 s), więc ruch blokuje teraz WalkSpeed i skok = 0.

## Czego nie sprawdzono

- **Prawdziwego telefonu.** Dotyk sprawdzony tylko haczykiem `dotknij(x, y)`, czyli tym samym kodem wyboru co dotknięcie,
  ale bez zdarzeń Touch. Nie sprawdzono też pionowego ekranu (pas byłby bardzo mały) ani tabletu 4:3.
- **Pada** (krzyżak, gałka, A, B) i klawisza **Esc**. Esc otwiera menu Roblox, a rezygnacja przez `GuiService.MenuOpened`
  jest napisana, ale nie sprawdzona. Klawiaturę sprawdzono tylko Backspace.
- **Kilku graczy naraz.** Stan jest osobny dla gracza, ale test był z jednym.
- **Opublikowanej gry.** Prototyp sam się usuwa poza Studio.
- **Wejścia do starego `BiomLas`** z mgłą `MglaLasu`. Przy `LasPas` mgła nie działa, a gdy kamera wraca ze starego lasu,
  mgła zanika 1,25 s już w czasie wyłaniania makiety.
- **Wyboru myszą na innych proporcjach okna niż 16:9.**

## Znane słabości

- **Makieta zawsze wczytana.** To model `Persistent` (561 części) daleko na niebie, w (−5000; 300; 5000), więc jest
  wczytany u każdego gracza przez całą grę.
- **Mało miejsca na telefonie.** Na poziomym ekranie (ok. 844 pt) płytka ma ok. 85–90 pt, a napisy ok. 10–12 pt. Krainy
  rozpoznaje się raczej po kształcie i kolorze niż po napisie.
- **Mgła miejsca.** `Atmosphere` o gęstości 0,3 lekko bieli makietę, bo kamera jest ok. 200 st. od pasa.
- **Wygląd chmur.** To kule z gładkiego plastiku: komiksowe, ale bez miękkich brzegów. Od spodu bywają sinoniebieskie.
- **Ukryte ekrany gry.** Na czas przejścia znikają wszystkie ekrany gry (ScreenGui), także HUD Pawła — przywracamy
  dokładnie te, które były włączone.
- **Blokada ruchu.** Stoi na WalkSpeed, JumpPower i JumpHeight = 0 ustawionych u klienta. Jeśli inny skrypt zmieni te
  wartości w trakcie przejścia, ich nie nadpisujemy (przywracamy tylko zera).
- **Odblokowania bez zapisu.** Są tylko w pamięci serwera i giną po wyjściu z gry.
- **Kamera pod koronami drzew.** Omija przeszkody jednym promieniem od głowy, więc przy gęstych koronach na chwilę
  „przykleja się” pod koroną.
- **Kosmetyka:**
  - w konsoli Studio komunikaty `warn` gubią polskie znaki;
  - litera Ż na tabliczce ma inny krój (czcionka zastępcza);
  - w zrzutach z trybu Edit napisy tabliczek pojawiają się dopiero przy drugim zrzucie.

## Wybory do decyzji

**1. Wybór krainy jednym dotknięciem czy z potwierdzeniem?**
- Teraz: jedno dotknięcie wybiera i od razu leci.
- Opcja: pierwsze dotknięcie wskazuje, drugie zatwierdza (mniej pomyłek na telefonie, o jedno dotknięcie dłużej).

**2. Czy chować HUD na czas przejścia?**
- Teraz: wszystkie ekrany gry są ukryte. Obraz jest czysty, a kolumny przycisków nie zasłaniają skrajnych krain na
  telefonie.
- Opcja: HUD zostaje (`sterowanie.ukryj_gui = false`).

**3. Przycisk TELEPORT: nasłuch sygnału HUD czy linijka Pawła?**
- Teraz: nasłuch `HUDButtonPressed("Teleport")`, bez zmian u Pawła.
- Opcja: Paweł woła `Otworz:Fire()`, a nasłuch wyłączamy (`sluchaj_hud = false`).

**4. Długość przejścia: zostawić ok. 4,8 s czy skrócić?**
- Teraz: 2,2 s do makiety i 2,5 s po wyborze.
- Opcja: ok. 3 s razem (szybciej przy częstym teleporcie, mniej widać chmury).

**5. Co robi dotknięcie krainy, w której gracz jest?**
- Teraz: przenosi na jej punkt przybycia (powrót na start krainy).
- Opcja: działa jak rezygnacja.

**6. Makieta stale wczytana czy budowana u gracza?**
- Teraz: model `Persistent` w świecie, zawsze u każdego gracza.
- Opcja: klient buduje ją przy pierwszym teleporcie (mniej pamięci przez całą grę, chwila budowy przy pierwszym
  użyciu).

**7. Zapis odblokowań i strażnik: kiedy i kto podpina?**
- Teraz: odblokowania tylko w pamięci serwera, odblokowanie haczykiem `odblokuj`.
- Do zrobienia: zapis gracza (DataStore) i wywołanie po pokonaniu Strażnika Gaju.

**8. Prototyp w Studio czy przeniesienie do `src/`?**
- Teraz: tylko w Studio, jak `LasTeleport`.
- Opcja: po akceptacji wyglądu przenieść do `src/` (wtedy działa w opublikowanej grze), a stare teleporty E
  (`LasTeleport`) usunąć — D-075 nazywa je zaślepką.
