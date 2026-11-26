# Kontrakt: ciało bazowe + zakładany ekwipunek (D-071)

**Status: propozycja (etap 1, projekt systemu); etap 2 — Rycerz, Kot-Mag i Zwiadowca zbudowani według kontraktu
(doprecyzowania z budowy: pkt 9, 10 i 11); etap 3 — przegląd i poprawki (pkt 12); etap 4 — porządki: wspólny kod
w `swiat/postacie/ekwipunek.py`, 20 przedmiotów bohaterów w katalogu `przedmioty.json` i w propozycji Luau
(pkt 13).** Ten plik wiąże budowniczych
modułów `rycerz.py`, `zwiadowca.py`, `kot_mag.py` i wspólnego modułu ekwipunku. Decyzja właściciela: każdy
element ekwipunku (zbroja, miecz, spodnie, kapelusz, szata, tarcza) widać na modelu 3D, także w walce. Postacie
dostają gołe modele bazowe, a dzisiejszy wygląd staje się kompletem przedmiotów. **Tarczę widać tylko wtedy, gdy jest
wyekwipowana** ([[Rejestr decyzji]] D-071). Konwencje osi, kości i zaczepów: `biblioteka/README.md`.

## 0. Trzy zasady, których nie wolno złamać
1. **`zbuduj()` się nie zmienia.** Zwraca to samo co dziś: `[Postac(ID w pełnym stroju), broń…]`. Postać ma ten sam
   `id`, te same kości (17 Rycerz/Zwiadowca, 23 kot), te same punkty zaczepienia (18/18/20), te same klipy (nazwy,
   długości, klucze co do wartości, `CHWILE`) i ten sam zbiór brył. **Jedyny wyjątek:** Rycerz nie ma już założonej
   tarczy (`rycerz_tarcza` zostaje w zwracanej liście jako osobny przedmiot, tak jak dziś). Z `zbuduj()` korzystają
   `przebuduj.py`, `roblox_postac.py`, `roblox_import*.py`, `zestawienie.py` i prototyp walki
   (`swiat/test_walki2/aktorzy.py` bierze pierwszą postać z listy).
2. **Klipy należą do ciała i są wspólne dla każdego stroju.** Dziś klipy walki liczą się z geometrii: „stopy płasko”,
   „nic pod ziemią”, a w upadku kota „kapelusz i kostur lądują na ziemi”
   (`rycerz._najnizej` → `_bryly(p)` z akcesoriami, `zwiadowca._najnizej` → `p.czesci`,
   `kot_mag._dno_akcesorium`). Dlatego klipy liczymy **raz, na postaci odniesienia** = dzisiejszy pełny strój
   **razem z tarczą** (u kota z kapeluszem i kosturem, u Zwiadowcy z łukiem i sztyletem). Potem kopiujemy je
   (`kanaly`, deepcopy) na ciało i na każdy strój. **Nie przeliczamy klipów od założonych przedmiotów.** Tak samo działa
   gra: jedna animacja na klasę, niezależnie od ubrania.
3. **Ciało bazowe ma dzisiejsze klocki R15** (`wymiary` w konstruktorze, `rozstaw_nog`, stawy, zaczepy). Dzięki temu
   zaczepy, kości i klipy zostają bez zmian.

## 1. Ciała bazowe („gołe”)
Typy ciała: **`czlowiek`** (Rycerz i Zwiadowca, te same klocki: Head 1,6×1,5×1,45, UpperTorso 2,2×1,5×1,2,
LowerTorso 2,2×0,4×1,2, UpperArm 0,95³, LowerArm 0,95×0,75×0,95, Hand 0,9×0,35×0,9, UpperLeg 1,05×0,8×1,05,
LowerLeg 1,05×0,75×1,05, Foot 1,05×0,35×1,35) i **`kot`** (klocki z `kot_mag.py`). Do tego `manekin`: domyślny
klocek R15 biblioteki, na którym siedzą dzisiejsze zestawy. Przedmiot pasuje do jednego typu ciała. Broń na zaczepie
dłoni pasuje do każdego typu ciała.

| | Zostaje na ciele (zawsze) | Prosta bielizna / futro (nowe bryły) | Nowe kolory (propozycja) |
|---|---|---|---|
| Rycerz | głowa skóra z dzisiejszą twarzą (oczy, brwi, nos, uśmiech, rumieńce) | **włosy** jako osobne akcesorium `rycerz_wlosy` (Hair, `HairAttachment`; krótka brązowa czupryna); lniana koszula z krótkim rękawem (UpperTorso + UpperArm), krótkie spodenki (LowerTorso + UpperLeg, z rąbkiem nad kolanem); skóra: przedramiona, dłonie, golenie, bose stopy | len `EDE3CC`, spodenki w kolorze tabardu `2C6BE0` (maskotkę poznać po kolorze) |
| Zwiadowca | głowa „Twarz” z oczami, piegami, brwiami, uśmiechem **i grzywką** (Kosmyk 0–2, część twarzy) | włosy `zwiadowca_wlosy` (Hair, ciemny brąz `4A2C17`); koszula lniana, spodenki zielone; skóra jak u Rycerza | len, spodenki `26633A` |
| Kot | cała głowa z futrem, mordką i wąsami, uszy (kości `LeftEar`/`RightEar`), łapki, uda, łydki, łapy, ogon (`Tail`, `TailTip`) | futro na kościach, które dziś zakrywa szata: tułów (`kot`) z jasnym brzuszkiem (`kot_jasny`, 0,02 przed ścianą) i dwoma ciemnymi paskami na plecach, ramię, przedramię, LowerTorso | paleta kota bez zmian |

- Klocki ciała mają **pełny rozmiar klocka** (`p.cialo(...)` albo `p.klocek`). Bielizna i detale wystają o 0,02–0,03
  (jak oczy). Nie robimy wcięć, bo wcięty tułów zostawiłby szparę 0,08 między tułowiem a ramieniem. **Wyjątek:
  spodenki** (ściągacz i nogawka) wystają tylko o 0,01, bo pas i poły tuniki leżą o 0,02 nad klockiem — przy tej samej
  odległości ściany migotałyby, gdy pas albo kirys są założone bez spodni (pkt 12).
- Twarz i ogon nigdy nie znikają. Włosy są akcesorium ciała, więc hełm może je schować (`ukrywa`). Uszy kota
  znikają tylko pod hełmem, który mieści je w całości i deklaruje `ukrywa=("Uszy",)` (od 26.11.2026, pkt 14).
- Kości nośne kota `HatPivot` i `StaffPivot` zostają w gołym ciele bez brył. Klipy dalej nimi ruszają, co bez
  przedmiotu nic nie zmienia.
- Goły bohater wygląda sympatycznie: ta sama mina co w pełnym stroju, jasna koszula, kolorowe spodenki. Bez nagości.

## 2. Widoczne sloty i warstwy
Sloty gry: Helmet, Chest, Gloves, Boots, Amulet, Belt, Ring, Trinket, Weapon (`src/shared/Items.luau`), a w zestawach
także **OffHand**.

| Slot | Gdzie na modelu (człowiek) | Kot | Warstwa |
|---|---|---|---|
| Helmet | Head (+ opcjonalnie UpperTorso: kołnierz, peleryna przy kapturze) | kość `HatPivot`, zaczep `KapeluszAttachment` (ramka = `HatAttachment`) | nakładka; `ukrywa=("Wlosy",)` |
| Chest | UpperTorso, L/R UpperArm, L/R LowerArm (powłoka); poły i tabard na LowerTorso/UpperLeg (nakładka) | UpperTorso, ramiona, przedramiona, LowerTorso (dzwon szaty) | powłoka + nakładki |
| Chest — część „spodnie” | LowerTorso, L/R UpperLeg (powłoka) | — (szata zakrywa nogi) | powłoka |
| Gloves | L/R Hand | L/R Hand | powłoka |
| Boots | L/R LowerLeg, L/R Foot | L/R Foot | powłoka |
| Belt | LowerTorso | LowerTorso | nakładka |
| Weapon | `RightGripAttachment` | `KosturAttachment` (kość `StaffPivot`), korekta chwytu `obrot=(−90,0,0)`, `pos=(−0,08,0,0)` | zaczep |
| OffHand | `LeftGripAttachment`: tarcza (tylko Wojownik, D-062), łuk Zwiadowcy z kołczanem na plecach (druga siatka na UpperTorso) | — | zaczep (+ nakładka) |
| Amulet | widoczny: medalion na piersi, środek `z = d/2 + 0,16` (przed najdalej wysuniętą bryłą kanonu: węzeł chusty +0,14), `y = góra tułowia − 0,35` | jak u człowieka, na wierzchu szaty | wierzchnia |
| Trinket | widoczny: wisior przy lewym biodrze (LowerTorso, `x = +w/2 − 0,25`, `z = d/2 + 0,12`) | to samo | wierzchnia |
| Ring | **niewidoczny na modelu** (pierścień < 0,15 studa na klocku dłoni nie czyta się); tylko ikona | — | — |

**Peleryna i kołczan:** gra nie ma slotu „plecy”. Peleryna należy do przedmiotu, z którym się ją nosi (u Zwiadowcy
kaptur z peleryną to jedno okrycie, Helmet), a kołczan do łuku (OffHand).

**Spodnie** (właściciel je wymienił, a okno ekwipunku nie ma takiego slotu). Propozycja: **część zbroi**. Spodnie są
osobnym przedmiotem w danych, `slot: "Chest"`, `czesc_od: <zbroja>`, tak jak dziś `mag_szata_dol`. W plecaku jest
jeden przedmiot. Przejście na osobny slot `Legs` oznacza zmianę pola `slot` i usunięcie `czesc_od` (bez przebudowy
modeli), ale wymaga nowego slotu w oknie ekwipunku i w grafice. **Wybór do decyzji (pkt 8).**

### Warstwy i dopasowanie (liczby w studach, od ściany klocka kości)
| Warstwa | Co | Gdzie | Zasada |
|---|---|---|---|
| 0 ciało | klocek + bielizna/futro | klocek, detale do +0,03 | znika, gdy na tej kości jest powłoka |
| 1 powłoka (`zakrywa=True`) | zbroja, rękaw, nogawica, rękawica, but | od −0,06 (dzisiejsze cieńsze bryły Zwiadowcy) do +0,02 | **na jednej kości najwyżej jedna powłoka**; właściciel kości jest stały (tabela niżej) |
| 2 nakładka | hełm, pas, naramiennik, nałokcica, tabard, poły | ≥ +0,03, cel 0,03–0,05 dla nowych rzeczy | żadna zewnętrzna ściana nie może leżeć w odległości < 0,02 od ściany klocka (migotanie) |
| 3 wierzchnia | peleryna, kołczan, amulet, talizman | ≥ +0,10 | na wierzchu każdego kanonicznego stroju tej kości |

**Właściciel powłoki na kości:** człowiek: UpperTorso, UpperArm, LowerArm → Chest; LowerTorso, UpperLeg → Chest
(spodnie); Hand → Gloves; LowerLeg, Foot → Boots; Head → nikt. Kot: UpperTorso, UpperArm, LowerArm, LowerTorso →
Chest; Hand → Gloves; Foot → Boots; Head, uszy, ogon, uda i łydki → nikt.

Wyjątki kanonu (zostają, bo mają wyglądać jak dziś):
- poły tuniki Zwiadowcy leżą +0,02 nad udem;
- pas kołczanu leży +0,025 nad klockiem;
- tabard Rycerza tylną ścianą przylega do klocka (0,00). To ściana schowana, więc nie migocze.

**Przedmiot z wielu kości** (zbroja z naramiennikami, para rękawic, buty z cholewą) dzieli się na **sztywne
segmenty, po jednym na kość**. Każdy segment to jedno `Akcesorium` (jedna siatka, ≤ 4000 trójkątów) modelowane w
układzie **środka klocka swojej kości**, tak jak dziś `with p.na(kosc, od="srodek")`, więc dzisiejszy kod brył
przenosi się 1:1. Nic nie przechodzi przez staw: naramiennik leży na ramieniu, nałokcica na przedramieniu, nakolannik
na goleni.

**Brak przenikania w klipach:**
- segment porusza się sztywno z kością;
- nakładka nie wystaje poza koniec klocka w stronę sąsiedniego stawu o więcej niż 0,1 (wyjątek kanonu: naramienniki
  Rycerza, które już dziś wchodzą w hełm do 0,18 przy uniesionej ręce, opisane w `SLABOSCI`);
- kontrola liczbowa każdego bohatera (`--kontrola`) działa na wspólnych klipach dla trzech strojów: **kanon**,
  **kanon + druga ręka** (Rycerz z tarczą) i **największy strój tego ciała**;
- bazą do porównań jest stan dzisiejszy. Pomiar z 15.11 dla Rycerza: przenika tylko stary `atak_miecz` (11 klatek,
  do 0,15 studa), naramiennik w hełmie do 0,18. Nowe przedmioty nie mogą tej bazy pogorszyć. Próg dla broni i dłoni
  w głowie i tułowiu: 0,06, jak dziś.

## 3. Rozbiór dzisiejszego stroju na przedmioty (zestaw kanoniczny)
Nazwy brył są takie jak dziś w modułach. Segment ma id `<przedmiot>_<kość>`, gdzie kość to `glowa`, `tulow`,
`biodra`, `ramie_l/p`, `przedramie_l/p`, `dlon_l/p`, `udo_l/p`, `golen_l/p` albo `stopa_l/p`. Przedmiot na zaczepie
ma segment o id samego przedmiotu, więc pliki `przedmioty/rycerz_miecz.*` zostają. Nie używamy `__`: tak
`przebuduj.py` oznacza pliki klipów. Powłoka = `zakrywa`. Zwykle zaczyna się od bryły o rozmiarze klocka w
dzisiejszym kolorze (u Rycerza to dzisiejszy klocek z `p.cialo`).

### Rycerz (`czlowiek`, klasa `wojownik`)
| id | nazwa | slot | segmenty: kość (warstwa) ← bryły dzisiejszego modelu |
|---|---|---|---|
| `rycerz_helm` | Hełm Rycerza | Helmet | Head (nakładka, ukrywa Wlosy) ← Helm bok L/P, Policzek L/P, Nit L/P, Obrecz bok L/P, Nit bok ×4, Helm tyl, Obrecz tyl, Helm tyl listwa, Helm kopula, Helm czubek, Grzebien, Czolo, Czolo obrecz (20) |
| `rycerz_zbroja` | Zbroja Rycerza z tabardem | Chest | UpperTorso (powłoka) ← klocek `stal`, Obojczyk, Tabard, Tabard tyl, Lamowka ×2, Lamowka tyl ×2, Godlo, Godlo srodek (10) · L/R UpperArm (powłoka) ← klocek `stal_ciemna`, Naramiennik, lama 1, lama 2, nit, nit 2 (6+6) · L/R LowerArm (powłoka) ← klocek `stal`, Nalokcica (2+2) · LowerTorso (nakładka) ← poły przód i tył: Pola, Pola lamowka ×2, Pola szpic, Pola rabek, Pola rabek poziom (12) |
| `rycerz_nogawice` | Nogawice Rycerza | Chest, `czesc_od: rycerz_zbroja` | LowerTorso (powłoka) ← klocek `brazowy` · L/R UpperLeg (powłoka) ← klocek `stal`, Udo plyta (2+2) |
| `rycerz_pas` | Pas Rycerza | Belt | LowerTorso (nakładka) ← Klamra, Klamra srodek (2) |
| `rycerz_rekawice` | Rękawice Rycerza | Gloves | L/R Hand (powłoka) ← klocek `stal_ciemna`, Mankiet (2+2) |
| `rycerz_buty` | Trzewiki z nagolennikami | Boots | L/R LowerLeg (powłoka) ← klocek `stal`, Nakolannik, Nagolennik (3+3) · L/R Foot (powłoka) ← klocek `stal_ciemna`, Czubek, Podeszwa (3+3) |
| `rycerz_miecz` | Wielki miecz Rycerza | Weapon | `RightGripAttachment` ← `miecz()` bez zmian |
| `rycerz_tarcza` | Tarcza Rycerza | OffHand (tylko `wojownik`) | `LeftGripAttachment` ← `tarcza()` bez zmian. **Poza kanonem**, ale jest w postaci odniesienia klipów |

Liczby się zgadzają: Head 36 = klocek + 15 brył twarzy + 20 hełmu; UpperTorso 10; LowerTorso 15 = 1 + 2 + 12;
ramię 6, przedramię 2, dłoń 2, udo 2, goleń 3, stopa 3, razem 97 brył. Słabość: pas Rycerza to sama klamra,
bo brązowy pas biodrowy to klocek LowerTorso (powłoka należy do spodni). Szerszy pas jako nakładka zmieni wygląd,
więc wymaga zgody właściciela.

### Zwiadowca (`czlowiek`, klasa `zwiadowca`)
| id | nazwa | slot | segmenty |
|---|---|---|---|
| `zwiadowca_kaptur` | Kaptur z peleryną | Helmet | Head (nakładka, ukrywa Wlosy, grzywka zostaje) ← Kaptur bok L/P, Podszewka L/P, Kaptur tyl, Kaptur tyl szew, Kaptur czubek, Podszewka gora, Daszek, Daszek szpic, Kaptur szpic, Kaptur szpic koniec (12) · UpperTorso (wierzchnia) ← Kaptur kolnierz, Peleryna barki, Peleryna przod ×2, Peleryna przod lisc ×2, Peleryna plecy, Peleryna lisc ×3, Peleryna zylka ×3 (13) |
| `zwiadowca_kurtka` | Skórzany kirys z tuniką | Chest | UpperTorso (powłoka) ← Tunika, Kirys, Kirys brzeg, Przeszycie, Sznurowanie ×2, Chusta, Chusta wezel, Chusta koniec (9) · L/R UpperArm (powłoka) ← Rekaw, Naramiennik, Naramiennik brzeg (3+3) · L/R LowerArm (powłoka) ← Karwasz, Karwasz brzeg, Karwasz sznur ×2 (4+4) · L/R UpperLeg (nakładka) ← Pola, Pola lisc, Pola lisc tyl (3+3) |
| `zwiadowca_spodnie` | Spodnie Zwiadowcy | Chest, `czesc_od: zwiadowca_kurtka` | LowerTorso (powłoka) ← Biodra · L/R UpperLeg (powłoka) ← Udo |
| `zwiadowca_pas` | Pas z sakwą | Belt | LowerTorso (nakładka) ← Pas, Klamra, Klamra srodek, Sakwa, Sakwa klapka (5) |
| `zwiadowca_rekawice` | Rękawice bez palców | Gloves | L/R Hand (powłoka) ← Dlon (skóra), Rekawica (2+2) |
| `zwiadowca_buty` | Buty z wywiniętą cholewą | Boots | L/R LowerLeg (powłoka) ← Cholewa, Cholewa wywiniecie, Cholewa pasek (3+3) · L/R Foot (powłoka) ← But, Podeszwa, Czubek (3+3) |
| `zwiadowca_sztylet` | Sztylet Zwiadowcy | Weapon | `RightGripAttachment` ← `sztylet()` |
| `zwiadowca_luk` | Łuk z kołczanem | OffHand (do decyzji, pkt 8) | `LeftGripAttachment` ← `luk()` · UpperTorso (wierzchnia) ← Kolczan, dno, wylot, pas, Drzewce ×3, Lotka ×3, Lotka b ×3, Pas kolczanu, Pas kolczanu tyl, Sprzaczka pasa (16) |

Bilans: UpperTorso 38 = 9 + 13 + 16; Head 35 = Twarz + 22 bryły twarzy z grzywką + 12; razem 117. Cieńsze bryły
Zwiadowcy (Tunika, Rekaw, Udo, Cholewa o 0,06 węższe od klocka) muszą mieć `zakrywa=True`, inaczej pełny klocek
gołego ciała przebije ubranie.

### Kot-Mag (`kot`, klasa `mag`)
| id | nazwa | slot | segmenty |
|---|---|---|---|
| `kot_mag_kapelusz` | Kapelusz Kota-Maga | Helmet | `KapeluszAttachment` (kość `HatPivot`, korekta `pos=(0, 0,02, 0)`) ← `kapelusz()` bez zmian; nic nie ukrywa, uszy przechodzą przez rondo zgodnie z projektem |
| `kot_mag_szata` | Szata Kota-Maga | Chest | UpperTorso (powłoka) ← Szata gora, Piers, Kolnierz ×2, Listwa, Zapinka, Klejnot, Ramiona, Kaptur, Kaptur szpic (10) · L/R UpperArm (powłoka) ← Rekaw · L/R LowerArm (powłoka) ← Mankiet, Obszycie rekawa, Wnetrze rekawa (3+3) · LowerTorso (powłoka) ← Szata dzwon, Szata rabek, Szata lamowka, Szata pola, Tren (5) |
| `kot_mag_pas` | Szarfa z klamrą | Belt | LowerTorso (nakładka) ← Pas, Pas klamra (2) |
| `kot_mag_kostur` | Kostur Kota-Maga | Weapon | `KosturAttachment` (kość `StaffPivot`, `obrot=(−90,0,0)`, `pos=(−0,08,0,0)`) ← `kostur()` bez zmian |

**Kości specjalne kota:**
- Każde nakrycie głowy kota siedzi na `KapeluszAttachment` (kość `HatPivot`), a każda broń w prawej łapie na
  `KosturAttachment` (kość `StaffPivot`) z korektą chwytu kota. Dzięki temu w `upadek` kapelusz się zsuwa, a broń
  wypada, niezależnie od tego, jaki przedmiot jest założony. Tor lotu liczono dla dzisiejszego kapelusza i kostura
  (postać odniesienia), więc inny przedmiot może w tym klipie wejść w ziemię. Sprawdza to `--kontrola`; tak tylko
  zapisujemy wynik, nie przeliczamy klipu.
- Korekty chwytu są danymi bohatera (`KOREKTY_CHWYTU = {"RightGripAttachment": ("KosturAttachment", pos, obrot)}`),
  a nie przedmiotu. Miecz z `bronie.py` w łapie kota dostaje tę samą korektę.
- W Roblox (rig z części) przedmiot przypina się do części `HatPivot`/`StaffPivot`, a nie do `HatAttachment` głowy.
  Tak już opisuje to `SLABOSCI` kota.

## 4. API modułu bohatera
Wspólny kod jest w module `swiat/postacie/ekwipunek.py` (od 15.11, pkt 13), nie w bibliotece. Biblioteka wystarcza:
segment to zwykłe `Akcesorium`, wtopienie dopisuje bryły do `Postac.czesci`, a przedmiot na zaczepie to
`Postac.zaloz`. Nie trzeba nowych zaczepów w `zbuduj()`.

```python
# swiat/postacie/ekwipunek.py (wspólne)
class Przedmiot:      # (id, nazwa, slot, kategoria, miara, cialo="czlowiek", klasy=(), czesc_od=None, ukrywa=(),
                      #  zestaw=None, paleta=None); miara = postać z klockami ciała (wymiary i środki kości)
    def segment(self, kosc, zakrywa=False, klocek=None) -> Akcesorium   # bryły w układzie ŚRODKA KLOCKA kości
    def na_zaczepie(self, akc, zaczep=None, pos=(0,0,0), obrot=(0,0,0))  # broń, kapelusz
    def opis(self, korekty=None) -> dict                    # wpis PRZEDMIOTY / format z pkt 5
    def ikona(self) -> Akcesorium                           # cały przedmiot do ikony (poza spoczynku)
def ubierz(cialo, przedmioty, id=None, nazwa=None, korekty=None) -> Postac
def kopiuj_klipy(zrodlo, cel)                               # nowe Klip na `cel`, kanaly = deepcopy, ta sama kolejność
def zaczep_ekwipunku(kosc) -> str                           # "Ekw<Kosc>Attachment"
SKROTY_KOSCI, ZACZEPY_CHWYTU                                # kość -> skrót w id segmentu; zaczepy broni w dłoni

# moduł bohatera (rycerz.py itd.)
KANON = ("rycerz_helm", "rycerz_zbroja", "rycerz_nogawice", "rycerz_pas", "rycerz_rekawice", "rycerz_buty",
         "rycerz_miecz")
ODNIESIENIE_KLIPOW = KANON + ("rycerz_tarcza",)          # geometria, na której liczą się klipy (= dzisiejszy model)
STROJE = {"golas": (), "pelny": KANON, "bojowy": KANON + ("rycerz_tarcza",),
          "lekki": ("rycerz_zbroja", "rycerz_nogawice", "rycerz_miecz")}   # plansze w przebuduj.py
def cialo(zaczepy_ekwipunku=False) -> Postac  # id "<ID>_cialo": kości, zaczepy, gołe bryły, włosy, KLIPY z odniesienia
def przedmioty() -> list[Przedmiot]            # wszystkie przedmioty bohatera, łącznie z tarczą
def zbuduj():                                  # jak dziś: [ubierz(cialo(), KANON, id=ID, nazwa=NAZWA), miecz, tarcza]
def warianty() -> list                         # dla przebuduj.py: golas i STROJE + segmenty + ikony całych przedmiotów
```

**Co robi `ubierz` (w Blenderze i w czystym Pythonie):**
1. Dla każdego `ukrywa` zdejmuje z `zalozone` akcesoria ciała o tym znaczniku (włosy).
2. Segment z `zakrywa=True` usuwa **wszystkie** gołe bryły swojej kości.
3. Bryły segmentu kostnego **wtapia** do `Postac.czesci` tej kości (`p` = `srodek(kosc)` + pozycja w segmencie).
   Kolory są już w hex, więc palety bohaterów się nie gryzą. Dzięki temu pełny strój ma te same siatki `<Kosc>_Geo`
   co dziś.
4. Segment na zaczepie zakłada przez `zaloz(..., eksport=False)` z korektą chwytu bohatera, jak dziś miecz i kapelusz.
5. Kasuje pamięć podręczną geometrii (`p._bryly`, `p._pkt`).
6. Nie rusza klipów.

Dwie powłoki na tej samej kości to błąd (`ValueError` z nazwami przedmiotów). Przedmiot dla innego typu ciała to
także błąd.

**Kolejność w `cialo()`:**
1. Gołe ciało bez klipów.
2. Postać odniesienia = `ubierz(gołe, ODNIESIENIE_KLIPOW)`.
3. Dzisiejsze funkcje klipów (`idle(p)`, `blok(p)` …) bez zmian, na postaci odniesienia.
4. `kopiuj_klipy` na gołe ciało, potem `ustaw_poze_renderu("idle", 0)`.

Postać odniesienia można zapamiętać w module, bo liczenie klipów trwa (kontrola Rycerza ok. 30 s).
`zaczepy_ekwipunku=True` dodaje tylko do eksportu gołego ciała 15 zaczepów `Ekw<Kosc>Attachment` (środek klocka,
obrót 0). Z nich importer Roblox robi Attachmenty, a przedmioty zakłada `Humanoid:AddAccessory`. **W `zbuduj()`
ich nie ma.**

**`przebuduj.py`:** gdy moduł ma `cialo` i `przedmioty`, ten sam przebieg (folder `wynik/<moduł>/` jest czyszczony
w całości) robi drugie wywołanie podglądu na module-opakowaniu w katalogu roboczym (`zbuduj = warianty`). Wyniki
idą do `wynik/<moduł>/ekwipunek/`:
- plansze `<id>_golas_plansza.jpg`, `<id>_<stroj>_plansza.jpg` dla każdego `STROJE` oraz jedna zbiorcza
  `<id>_ekwipunek_plansza.jpg`: goły | pełny | dwa częściowe;
- `<id>_cialo.fbx/.glb/_tekstury` (gołe ciało z włosami jako osobną siatką i zaczepami `Ekw…`);
- `przedmioty/<segment>.fbx/.glb` dla każdego segmentu, `ikony/<przedmiot>_ikona.png`: ikona całego przedmiotu
  złożona z segmentów w pozie spoczynku, jak dziś `mag_szata_cala` (`przymierz=False`);
- `ekwipunek.json` (pkt 5);
- film jednego klipu walki w stroju częściowym (np. `blok` w stroju „bojowy”) jako dowód, że przedmioty idą za
  kośćmi.

Główne pliki (`rycerz.fbx`, klipy, filmy) zostają bez zmian. Identyfikatory wariantów: `<ID>_golas`,
`<ID>_<stroj>`, nigdy samo `<ID>`.

## 5. Format danych dla gry (propozycja, plików gry teraz nie zmieniamy)
Format jest spójny z `przedmioty.json` (pola `czesci[].attachment` z wariantem `glb`/`fbx`, liczony z raportu jak
dziś) i z polami `Items.luau` (`name`, `slot`, `category`, `icon`). Dochodzą pola `body`, `classes`, `hides`,
`parent` i `meshes`. Układ biblioteki: przód +Z, lewa strona +X. Generator przelicza na układ Roblox tak jak
`roblox_klocki.py`: (x, y, z) → (−x, y, −z).

```json
{"id": "rycerz_zbroja", "nazwa": "Zbroja Rycerza z tabardem", "slot": "Chest", "kategoria": "Armor",
 "cialo": "czlowiek", "klasy": ["wojownik"], "czesc_od": null, "ukrywa": [], "zestaw": "rycerz",
 "czesci": [
  {"id": "rycerz_zbroja_tulow", "kosc": "UpperTorso", "zakrywa": true, "zaczep": "EkwUpperTorsoAttachment",
   "pos": [0, 0, 0], "rot": [0, 0, 0],          "trojkaty": 0,
   "fbx": "wynik/rycerz/ekwipunek/przedmioty/rycerz_zbroja_tulow.fbx", "glb": "…glb",
   "attachment": {"glb": {"pos": [], "rot": []}, "fbx": {"pos": [], "rot": []}}},
  {"id": "rycerz_zbroja_ramie_l", "kosc": "LeftUpperArm", "zakrywa": true, "zaczep": "EkwLeftUpperArmAttachment"}
 ],
 "plik_ikony": "wynik/rycerz/ekwipunek/ikony/rycerz_zbroja_ikona.png"}
```
- `cialo` przedmiotu, który składa się tylko z broni na zaczepie chwytu (`RightGripAttachment`/`LeftGripAttachment`:
  miecz, tarcza, sztylet, kostur), to `"dowolne"` — pasuje do każdego ciała (u kota z korektą chwytu). Łuk Zwiadowcy
  ma kołczan na tułowiu, więc zostaje `"czlowiek"`, a kapelusz kota `"kot"`.
- `pos`/`rot` to ramka segmentu względem **środka klocka kości**. Przedmioty kostne mają (0,0,0). Przedmiot na
  zaczepie ma `zaczep` standardowy (np. `RightGripAttachment`) i `kosc` tego zaczepu. U kota to `HatPivot` albo
  `StaffPivot`.
- **Rig z części Roblox** (sprawdzona droga, bez wgrywania): część kości ma środek w środku klocka. Segment to
  części przyspawane do części kości z tym przesunięciem. `zakrywa` oznacza `Transparency = 1` gołych części tej
  kości, a `ukrywa` to samo dla części włosów.
- **Rig z siatek** (droga z wgrywaniem): segment to `Accessory` z `Handle` i Attachmentem `Ekw<Kosc>Attachment`.
  `zakrywa` oznacza `Transparency = 1` siatki `<Kosc>_Geo`. Bezpieczne, bo powłoka nigdy nie dotyczy głowy.
  Włosy są osobną siatką. Nic z tego nie było sprawdzane w Studio.
- Wpis Luau (propozycja, generuje `przedmioty_luau.py`):
  `rycerz_zbroja = { name = "…", slot = "Chest", category = "Armor", icon = "", iconFile = "…", set = "rycerz",
  body = "czlowiek", classes = { "wojownik" }, hides = {}, parent = nil, meshes = { { bone = "UpperTorso",
  covers = true, attachment = "EkwUpperTorsoAttachment" }, … } }`.
- Jak to wyszło w katalogu (`przedmioty.json`, `roblox/PrzedmiotyPropozycja.luau`): pkt 13.

## 6. Istniejące zestawy (`zestaw_rycerz/mag/rekrut.py`, `bronie.py`, `wzor_ekwipunku.py`)
**Zostają bez zmian i bez dopasowania teraz** (najtańsza sensowna droga):
- są zrobione na `manekin` (głowa 1,25, tułów 2×1,6×1) i dalej służą przymierzalni na awatarze gracza w Studio;
- w danych dostają `cialo: "manekin"`;
- **broń** (`bronie.py`, miecze, kostury, tarcze, księga z zestawów) siedzi na zaczepie dłoni, więc już dziś pasuje
  do każdego typu ciała. Kot dostaje swoją korektę chwytu. Można ją pokazać na bohaterach od razu, ale rozmiar broni
  w łapie kota (miecz 3,9 przy kocie 3,15) to osobna sprawa.

Dopasowanie do ciał bohaterów robimy dopiero dla zestawów wybranych do gry. Sposób: automatycznie przeskalować
segmenty na kość (stosunek klocka bohatera do klocka manekina na osiach X, Y, Z; bryły obrócone tylko o
wielokrotność 90° skalują się dokładnie), a potem obejrzeć plansze. Zestaw Maga przed tym trzeba odchudzić (527
części).

## 7. Ryzyka i kolejność przebudowy
**Ryzyka:**
1. Klipy przeliczone na gołym ciele albo na stroju bez tarczy dadzą inne klucze, przez co postać zmieni się w ruchu
   (zasada 0.2).
2. Nieaktualna pamięć podręczna `_bryly`/`_pkt` po `ubierz`.
3. `kontrola()` w modułach zakłada `zrodlo == "cialo"` dla stroju i nazwy `rycerz_tarcza`/`kot_mag_*`. Po wtopieniu
   strój dalej jest „ciałem”, więc kontrola działa bez zmian. Tarczę trzeba sprawdzać w stroju „bojowy”.
4. Kolejność brył i komórek palety zmieni się po przebudowie, więc tekstury PNG i bajty FBX będą inne przy tym samym
   wyglądzie. Regresję porównujemy na danych i na planszach, nie na bajtach.
5. Dwa przedmioty o tym samym id dadzą w Blenderze nazwę `<id>_Akc.001`. Prototyp walki zakłada własną
   `rycerz_tarcza` na `TarczaAttachment`, więc nie wolno go łączyć ze strojem „bojowy”.
6. **Stan zastany:** prototyp walki (`swiat/test_walki2/przerobki.py`, moduł innego agenta, nie ruszamy) już dziś
   wywraca się na Rycerzu i Kocie: `Klip 'trafienie' już istnieje`, bo moduły dostały własne klipy walki. To nie
   skutek tej zmiany, ale ktoś musi o tym wiedzieć.
7. Ścieżka siatek w Roblox (Attachmenty `Ekw…`, przezroczystość, `AddAccessory` z własnymi nazwami) jest
   niesprawdzona.

**Kolejność:**
1. Zrzut stanu przed pierwszą zmianą, do katalogu tymczasowego: `pakiet(zbuduj())` trzech bohaterów jako JSON oraz
   wynik `rycerz.py --kontrola` i `kot_mag.py --kontrola`.
2. `ekwipunek.py` i test w czystym Pythonie (bez Blendera): ubierz, zakrywa, ukrywa, kolizja powłok, kopiowanie
   klipów, `opis()`.
3. **Rycerz.** Test regresji:
   - postać odniesienia równa się dzisiejszemu `zbuduj()[0]`: kości, zaczepy, klipy z kluczami co do wartości,
     `CHWILE`, multizbiór brył (kość, kształt, p, r, s, kolor, materiał, faza) i akcesoria;
   - nowe `zbuduj()[0]` to samo bez tarczy;
   - kontrola nie gorsza od zrzutu;
   - przebudowa i obejrzenie plansz: gołego, pełnego, „bojowy”, „lekki” i dzisiejszej `rycerz_plansza.jpg`.
4. **Zwiadowca**, to samo ciało `czlowiek`. Dodatkowa plansza krzyżowa: zbroja Rycerza na Zwiadowcy.
5. **Kot.**
6. `zestawienie.py` → `przedmioty.json` z przedmiotami bohaterów, potem `przedmioty_luau.py` (zrobione 15.11,
   pkt 13).
7. Roblox: ubieranie na rigu z części, dopiero po zwolnieniu Studio.

## 8. Wybory do decyzji ludzi
1. **Spodnie:** część zbroi (Chest, `czesc_od`, bez zmian w oknie ekwipunku) — *rekomendacja* — czy osobny slot
   `Legs` (nowy slot w oknie ekwipunku i w grafice)?
2. **Druga ręka i plecy Zwiadowcy:** łuk z kołczanem w slocie drugiej ręki obok sztyletu w Weapon (D-062 daje slot
   tarczy tylko Wojownikowi), a peleryna razem z kapturem jako jeden przedmiot Helmet — czy inaczej?
3. **Drobne przedmioty:** amulet widoczny na piersi, talizman jako wisior przy pasie, pierścień niewidoczny na modelu
   (za mały) — czy tak?

## 9. Doprecyzowania z budowy Rycerza (etap 2, 15.11)
Co praktyka pokazała i dlaczego kontrakt trzeba było dopowiedzieć:
- **Wspólny kod chwilowo w `rycerz.py`** (przeniesiony 15.11, pkt 13). Etap Rycerza nie obejmował nowego pliku, więc `Przedmiot`, `ubierz`,
  `kopiuj_klipy`, `SKROTY_KOSCI` i `zaczep_ekwipunku` są w sekcji „ekwipunek: wspólne” na górze `rycerz.py`
  (nic tam nie zależy od Rycerza). Przy Zwiadowcy przenieść je 1:1 do `swiat/postacie/ekwipunek.py`, a w
  `rycerz.py` zostawić import — bez zmiany zachowania.
- **Które bryły są „gołe”.** `ubierz` musi odróżnić gołe bryły kości od brył nakładek wtopionych wcześniej (poły
  zbroi i powłoka nogawic leżą na tej samej kości `LowerTorso`). Gołe ciało oznacza swoje bryły polem
  `"golas": True` w słowniku części (eksport go nie widzi: `_czesc_json` bierze tylko znane klucze). Powłoka
  zdejmuje tylko bryły z tym polem.
- **Znacznik włosów.** Akcesorium włosów ma atrybut `znacznik = "Wlosy"`; `ukrywa=("Wlosy",)` hełmu zdejmuje
  z `zalozone` akcesoria o tym znaczniku.
- **Typ ciała.** Gołe ciało ma atrybut `typ_ciala` („czlowiek”/„kot”); `ubierz` porównuje go z `Przedmiot.cialo`
  tylko dla segmentów kostnych (broń pasuje do każdego ciała).
- **Wtapianie bez dodatkowych zaokrągleń.** Bryła segmentu trafia do ciała jako `p = srodek(kosc) + p_segmentu`
  (kopiowane są surowe `Akcesorium.czesci`, nie `czesci_w()`), więc liczby są co do bitu takie jak w dawnym
  `with p.na(kosc, od="srodek")`. Wynik: postać odniesienia Rycerza = dawny `zbuduj()[0]` (multizbiór 97 brył,
  kości, zaczepy, klipy co do klucza), a plansza stroju „bojowy” jest identyczna co do piksela z dawną planszą,
  choć kolejność brył się zmieniła.
- **Kontrola z włosami.** W `kontrola()` akcesoria na kościach głowy, tułowia i pasa (włosy) wchodzą do skrzynki
  swojej kości, a nie do „ruchomych” — inaczej włosy „przenikają” głowę.
- **`przebuduj.py`** (opcjonalnie, gdy moduł ma `cialo`, `przedmioty`, `warianty` i `STROJE`): dwa wywołania
  podglądu na module-opakowaniu w katalogu roboczym — `warianty("plansze")` bez eksportu (plansze strojów i ikony
  całych przedmiotów) i `warianty("eksport")` z `--eksport --bez-renderu` (gołe ciało i segmenty) — plus filmy
  z `FILMY_EKWIPUNKU = ((strój, klip), …)`. Moduł podaje też `NAZWY_STROJOW` (podpisy) i `PLANSZA_ZBIORCZA`
  (cztery stroje na planszę zbiorczą). Ciało w eksporcie ma tylko klip `idle` (pozostałe: `<ID>__<klip>.fbx`,
  te same kości) — 11 klipów × kolejne pliki nic by nie wniosło. Broń zostaje w głównym `przedmioty/`.
- **Ikony całych przedmiotów** w domyślnym kadrze ikon (przód, 3/4 od lewej, ok. 20° z góry) wyglądają dobrze bez
  `ikona_obrot`; para rękawic i pas-klamra wychodzą małe, bo leżą daleko od siebie albo są małe.
- **Stroje Rycerza do plansz:** `golas`, `pelny` (= kanon), `bojowy` (kanon + tarcza = postać odniesienia),
  `lekki` (zbroja, nogawice, trzewiki, miecz — widać włosy i gołe dłonie), `helm_i_miecz`.

## 10. Doprecyzowania z budowy Kota-Maga (etap 2, 15.11)
Co praktyka pokazała przy kocie i dlaczego trzeba to dopisać:
- **Wspólny kod dalej w `rycerz.py`** (stan z etapu 2; przeniesiony 15.11, pkt 13 — zapasowego importu z
  `rycerz.py` już nie ma). Na etapie 2 `kot_mag.py` importował `Przedmiot`, `ubierz`, `kopiuj_klipy` i
  `zaczep_ekwipunku` najpierw z `swiat/postacie/ekwipunek.py`, a gdy tego pliku jeszcze nie było — z `rycerz.py`.
- **Bryły modelowane od stawu.** Dawny kot modelował biodra (dzwon szaty, szarfa) i przedramiona (mankiet) od
  STAWU kości (`with p.na(kosc)`), a nie od środka klocka. W segmencie wystarczy `with a.uklad(pos=−srodek(kosc))`
  i dawny kod bez zmian. Wynik zostaje co do bitu: multizbiór 85 brył postaci odniesienia = dawny `zbuduj()[0]`.
- **Korekty chwytu przez `ubierz(..., korekty=KOREKTY_CHWYTU)`.** Kot podaje
  `{"HatAttachment": ("KapeluszAttachment", (0, 0,02, 0), (0, 0, 0)), "RightGripAttachment": ("KosturAttachment",
  (−0,08, 0, 0), (−90, 0, 0))}` przy każdym `ubierz` (ciało odniesienia, stroje, `zbuduj`) i w `opis(korekty)`.
  W `ekwipunek.json` kapelusz i kostur mają więc `zaczep` KapeluszAttachment / KosturAttachment, `kosc` HatPivot /
  StaffPivot i `pos`/`rot` korekty. `przebuduj.raport_ekwipunku` pokazuje zaczep po korekcie (opcjonalnie: gdy
  moduł ma `KOREKTY_CHWYTU`; u Rycerza bez zmian). Miecz Rycerza w łapie kota dostaje tę samą korektę (sprawdzone
  w czystym Pythonie).
- **Nazwa stroju nie może dać id przedmiotu.** Strój `szata` dałby postać `kot_mag_szata`, a to id przedmiotu
  (ikona) — w Blenderze pliki i raporty nazywają się od id, więc by się nadpisały. U kota strój nazywa się
  `sama_szata`. Zasada: `<ID>_<strój>` ≠ id żadnego przedmiotu ani segmentu.
- **Ogon kota wychodzi nisko** (staw ogona na wysokości łydek, pod dawną szatą). Goły kot ma dlatego „futro
  u nasady ogona”: bryłę bioder schodzącą z tyłu do stawu ogona. To goła bryła bioder, więc znika pod szatą
  (powłoka na LowerTorso), a ogon w pełnym stroju jest bez zmian.
- **Kot: klipy liczone na pełnym stroju** (`ODNIESIENIE_KLIPOW = KANON`; kot nie ma drugiej ręki). Stroje do plansz
  i kontroli: `golas`, `pelny`, `bez_kapelusza` (kapelusz to wciąż propozycja kanonu), `kapelusz_i_kostur`,
  `sama_szata` (szata z szarfą). Kontrola na wszystkich pięciu: nic nowego nie przenika; pełny strój daje
  dokładnie dawny wynik (tylko stary `chod`: rękaw w dzwonie do 0,24 studa).
- **Upadek bez szaty.** Klip kładzie kota na dzwonie szaty, więc goły kot leży ok. 0,20 studa nad ziemią (jak goły
  Rycerz: 0,25). Do decyzji razem z Rycerzem (osobny upadek ciała albo korekta korzenia w grze).
- **Szarfa w kanonie** prawie cała siedzi w górze dzwonu szaty (tak było); widać ją na gołym futrze.

## 11. Doprecyzowania z budowy Zwiadowcy (etap 2, 15.11)
Co praktyka pokazała przy Zwiadowcy i dlaczego trzeba to dopisać:
- **Wspólny kod dalej w `rycerz.py`** (stan z etapu 2; przeniesiony 15.11, pkt 13). Etap Zwiadowcy obejmował tylko
  `zwiadowca.py` (i opcjonalnie `przebuduj.py`), więc `ekwipunek.py` jeszcze nie powstał. `zwiadowca.py` importował
  wspólny kod tak jak kot: najpierw z `ekwipunek.py`, a gdy go nie było — z `rycerz.py`.
- **Przedmiot mieszany: segment kostny + segment na zaczepie.** „Łuk z kołczanem” ma kołczan z pasem na skos
  (segment `zwiadowca_luk_tulow` wtapiany w UpperTorso, wierzchnia warstwa) i łuk na `LeftGripAttachment` (segment
  o id samego przedmiotu, `zwiadowca_luk`). `ubierz`, `opis()` i `przebuduj.py` obsługują to bez zmian. Wspólna
  `Przedmiot.ikona()` bierze jednak tylko segmenty kostne, więc ikona pokazałaby sam kołczan. Zwiadowca ma
  podklasę `_Przedmiot`, która dokłada łuk obok kołczanu (ramka łuku w `IKONA_ZACZEPIONYCH`) i pokazuje ikonę od
  tyłu. Segment kostny musi być pierwszy (od niego ikona bierze zaczep). `zbuduj()` zwraca akcesorium łuku
  z segmentu na zaczepie, jak dawniej.
- **Kolejność w `KANON`.** Łuk stoi przed sztyletem, bo `ubierz` zakłada przedmioty w kolejności listy. Dzięki
  temu `zalozone` ma dawną kolejność `[łuk, sztylet]` (tak jak dawne `zbuduj()`).
- **„Co do bitu” nie zawsze się da.** Bryła w zagnieżdżonym `uklad` wewnątrz segmentu liczy się jako
  `srodek + (pos + R·v)`, a dawniej `(srodek + pos) + R·v`. Dodawanie liczb zmiennoprzecinkowych nie jest łączne.
  U Zwiadowcy 2 ze 117 brył (Kolczan dno, Kolczan pas) różnią się o 1,1·10⁻¹⁶ w ostatnim bicie. Klipy (klucze co do
  wartości) i pakiet JSON dla Blendera (zaokrąglony do 4 miejsc) wyszły identyczne. Test regresji porównuje więc
  bryły do 1e-9, a klipy i JSON dokładnie. U Rycerza i Kota liczby akurat wyszły co do bitu.
- **Kontrola Zwiadowcy liczy każdą bryłę osobno.** Dawny moduł nie miał `--kontrola` (sprawdzano skryptem poza
  repozytorium). Nowa `kontrola()` w `zwiadowca.py` nie używa jednej skrzynki na kość. Kołczan ze strzałami sięga
  nad prawy bark, więc taka skrzynka obejmowałaby prawą rękę. Dlatego każda bryła głowy (z kapturem i włosami),
  tułowia i bioder jest osobną skrzynką. Ruchome są łuk, sztylet, przedramiona i dłonie. Wynik jest taki sam jak
  w dawnym modelu: w żadnym z pięciu strojów nic nie przenika.
- **Upadek nie wisi.** Zwiadowca leży na brzuchu oparty na dłoniach i przedramionach, więc każdy strój leży na
  ziemi: ostatnia klatka od −0,025 (gołe dłonie są o 0,02 grubsze niż w rękawicach) do 0,000. Inaczej niż Rycerz
  i kot nie potrzebuje decyzji o osobnym upadku ciała.
- **Krzyżowe ubieranie (pkt 7.4) działa w czystym Pythonie i na renderze próbnym.** Sprawdzone stroje:
  - zbroja, nogawice, rękawice, trzewiki i miecz Rycerza z kapturem Zwiadowcy na ciele Zwiadowcy;
  - kaptur, kirys, spodnie, pas, buty i łuk Zwiadowcy na ciele Rycerza.

  Oba siedzą na ciele. Hełm Rycerza chowa włosy Zwiadowcy. Kirys i zbroja Rycerza naraz dają `ValueError`
  (dwie powłoki na UpperTorso), a szata kota na człowieku też `ValueError`. Plansz krzyżowych nie ma w
  `wynik/`, bo stroje modułu biorą tylko jego własne przedmioty.
- **Stroje Zwiadowcy do plansz i kontroli:**
  - `golas`;
  - `pelny` (kanon = postać odniesienia klipów);
  - `bez_kaptura`: widać czuprynę, a kołczan leży na kirysie;
  - `lekki`: kirys, spodnie, buty i łuk z kołczanem;
  - `kaptur_i_sztylet`: kaptur z peleryną na lnianej koszuli.

  Nazwy strojów sprawdzone pod kątem kolizji z id przedmiotów i segmentów.

## 12. Przegląd świeżym okiem i poprawki (etap 3, 15.11)
Co sprawdził przegląd i co z tego wynikło:
- **Zgodność wstecz, liczona niezależnie od budowniczych.** Moduły z ostatniego commitu i dzisiejsze, zbudowane obok siebie:
  - kości, zaczepy i klipy są identyczne co do wartości (Rycerz 17/18/11, kot 23/20/11, Zwiadowca 17/18/9);
  - `CHWILE` się nie zmieniły;
  - multizbiory brył są równe (97/85/117), pakiet JSON dla Blendera też;
  - jedyna różnica: Rycerz nie ma założonej tarczy.
- **Prototyp walki.** `aktorzy.przygotuj(..., liniowo=True)` uruchomiony na sucho, z wynikiem w katalogu tymczasowym:
  - dane aktorów `zwiadowca` i `mag` są identyczne z wersją sprzed zmian (multizbiór części);
  - `wojownik` ma 14 części mniej, czyli brakuje tylko tarczy.

  Przeróbki prototypu dla Rycerza i kota (`przerobki.py`) wywracają się także na starych modułach („Klip 'trafienie' już
  istnieje”), więc te dwie klasy sprawdzono bez przeróbek.
- **Migotanie między przedmiotami a gołym ciałem.** Nowy test (poza repozytorium) szuka par równoległych ścian brył
  w odległości < 0,006 studa na tej samej kości, w każdym stroju, dla każdego przedmiotu osobno na gołym ciele i
  krzyżowo (Rycerz ↔ Zwiadowca). Znalazł trzy usterki gołego ciała:
  - nogawka i rąbek spodenek Zwiadowcy;
  - poły tuniki Zwiadowcy założone bez spodni (na obu ciałach człowieka);
  - pas z sakwą na ściągaczu spodenek (na obu ciałach).

  Poprawka: spodenki obu ludzi wystają o 0,01 (pkt 1), a górę nogawki Zwiadowcy podniesiono o 0,01. Zostały tylko pary
  z dawnego kanonu (wewnątrz jednego przedmiotu) oraz ściany schowane w środku brył.
- **Ikona rękawic.** Na postaci dłonie są ok. 3 studa od siebie, więc w ikonie wychodziły maleńkie. `Przedmiot.ikona()`
  kładzie teraz parę dłoni obok siebie (odstęp 0,2 studa). Zmienia się tylko ikona, segmenty zostają.
- **`cialo: "dowolne"`** dla broni w dłoni (pkt 5).
- **Zostaje do decyzji albo do gry:**
  - goły Rycerz leży w ostatniej klatce `upadek` 0,25 studa nad ziemią, a goły kot 0,20 (klip kładzie ich na zbroi
    albo szacie); Zwiadowca leży na dłoniach, więc u niego tego nie ma;
  - pas Rycerza to sama klamra (ikona wygląda jak ramka);
  - ~~wspólny kod dalej siedzi w `rycerz.py` (pkt 9)~~ — przeniesiony do `ekwipunek.py` (pkt 13).

## 13. Porządki i katalog przedmiotów (etap 4, 15.11)
Bez Blendera i bez Studio. Wygląd, klipy i dane postaci się nie zmieniły.

**Wspólny kod w `swiat/postacie/ekwipunek.py`.**
- Sekcja „ekwipunek: wspólne” z `rycerz.py` przeszła do `ekwipunek.py` 1:1: `Przedmiot`, `ubierz`, `kopiuj_klipy`,
  `zaczep_ekwipunku`, `SKROTY_KOSCI`, `ZACZEPY_CHWYTU` i prywatne `_ID_OK`. Nazwy są te same, kod ten sam.
- Trzej bohaterowie importują wspólny kod z `ekwipunek.py`. Zapasowy import z `rycerz.py` w `kot_mag.py`
  i `zwiadowca.py` jest usunięty.
- `rycerz.py` dalej udostępnia `rycerz.Przedmiot`, `rycerz.ubierz`, `rycerz.kopiuj_klipy`,
  `rycerz.zaczep_ekwipunku`, `rycerz.SKROTY_KOSCI` i `rycerz.ZACZEPY_CHWYTU` (import z `ekwipunek.py`).
  W repozytorium (`swiat/`, `tools/`, `panel/`) nikt poza dwoma bohaterami nie importował ich z `rycerz.py`.
- Z przestrzeni nazw `rycerz` zniknęły tylko nazwy, których `rycerz.py` już nie używa: `I3` (stała biblioteki),
  `_ID_OK` oraz moduły `copy` i `re`. Klasy i funkcje mają teraz `__module__ == "swiat.postacie.ekwipunek"`
  (dawniej `swiat.postacie.rycerz`); nic w repozytorium z tego nie korzysta.

**Regresja.** Zrzut przed zmianą i po niej, w czystym Pythonie, dla każdego bohatera:
- `pakiet(...)` dla Blendera z `zbuduj()`, `warianty("plansze")` i `warianty("eksport")`;
- pełny stan obiektów `zbuduj()`, `warianty()`, `przedmioty()`, ikon, `cialo()`, każdego stroju i postaci
  odniesienia, z surowymi liczbami;
- `ekwipunek_json()`, stałe modułu (`KANON`, `STROJE`, `CHWILE`, `KOREKTY_CHWYTU`…) i wynik `--kontrola`
  (kod wyjścia i tekst).

Wszystko wyszło identyczne co do bajtu, także postacie aktorów prototypu walki (`aktorzy.postac_aktora`).
Niezależna kontrola (moduły z ostatniego commitu uruchomione z kopii w katalogu tymczasowym, obok dzisiejszych):
- stan obiektów (kości, zaczepy, klipy z każdym kluczem, `CHWILE`, bryły z surowymi liczbami, akcesoria z zaczepem,
  `pos` i `rot`) i pakiety JSON są identyczne dla `zbuduj()`, obu `warianty()`, `cialo()` z zaczepami `Ekw…`
  i bez nich, każdego stroju (5/5/5) i postaci odniesienia;
- `--kontrola`: ten sam tekst i kod wyjścia (Rycerz 1, kot 1 — dawne `atak_miecz` i `chod`; Zwiadowca 0);
- dane aktorów `wojownik`, `zwiadowca`, `mag` z `aktorzy.przygotuj(..., liniowo=True)` (zapis do katalogu
  tymczasowego) są identyczne co do bajtu;
- ścieżka `przebuduj.py` bez Blendera: opakowanie `OPAKOWANIE` daje ten sam pakiet co `warianty()`, a
  `raport_ekwipunku()` tę samą sekcję co w dzisiejszym `wynik/<bohater>/raport.txt`.

**`cialo: "dowolne"` dla broni w dłoni** liczy wspólne `Przedmiot.opis()`, czyli moduły, a nie ręczna poprawka
pliku. `ekwipunek_json()` trzech bohaterów zgadza się z `wynik/<id>/ekwipunek/ekwipunek.json` we wszystkich polach
modułu. Przebudowa nie cofnie więc przeglądu, a żadnego pliku JSON nie trzeba było przepisywać.
`zestawienie.py --tylko json` porównuje to przy każdym przebiegu i ostrzega, gdy plik jest nieaktualny.

**Katalog: `przedmioty.json`** (`zestawienie.py --tylko json`, dane z `wynik/<bohater>/ekwipunek/ekwipunek.json`
i z raportów Blendera).
- 58 przedmiotów: 41 dawnych − 3 rekwizyty bohaterów + 20 przedmiotów bohaterów (Rycerz 8, Kot-Mag 4,
  Zwiadowca 8).
- Wpisy zestawów (Rekrut, Rycerz, Mag), Zbrojowni i chochla Karczmarza zostały bez zmian (38 wpisów, ta sama
  kolejność).
- Dawne rekwizyty `kot_mag_kapelusz`, `kot_mag_kostur` i `rycerz_miecz` to teraz przedmioty bohaterów.
  Dawne pola zostały bez zmian: id, nazwa, slot, kategoria, zestaw, plik modelu, części z zaczepem i `attachment`
  oraz plik ikony. Doszły tylko pola D-071.
- Ikony: przedmiot z jednym segmentem na zaczepie (miecz, tarcza, kapelusz, kostur, sztylet) wskazuje ikonę
  z głównego przebiegu, `wynik/<bohater>/ikony/` — to ten sam model i obraz co do piksela jak w
  `wynik/<bohater>/ekwipunek/ikony/`, a dawne wpisy wskazywały właśnie ją. Pozostałe przedmioty bohaterów
  (także łuk z kołczanem) mają ikonę z `wynik/<bohater>/ekwipunek/ikony/`.

Pola przedmiotu bohatera (oprócz dawnych):

| Pole | Znaczenie |
|---|---|
| `cialo` | typ ciała: `czlowiek`, `kot` albo `dowolne` (broń w dłoni) |
| `klasy` | lista klas postaci, np. `["wojownik"]` |
| `czesc_od` | przedmiot nadrzędny: nogawice → zbroja, spodnie → kirys |
| `ukrywa` | znaczniki akcesoriów ciała chowanych pod przedmiotem (`["Wlosy"]` dla hełmu i kaptura) |

Pola części (segmentu):

| Pole | Znaczenie |
|---|---|
| `kosc` | kość segmentu |
| `zakrywa` | powłoka: gołe bryły tej kości znikają |
| `zaczep` | `Ekw<Kosc>Attachment` dla segmentu kostnego; dla przedmiotu na zaczepie zaczep standardowy |
| `pos`, `rot` | ramka segmentu względem środka klocka kości |
| `trojkaty` | liczba trójkątów siatki |
| `fbx`, `glb` | segmenty kostne w `wynik/<bohater>/ekwipunek/przedmioty/`, broń w `wynik/<bohater>/przedmioty/` |
| `attachment` | gotowe ustawienie Attachmentu w Handle, liczone tak jak dla zestawów (minus środek skrzynki siatki od zaczepu) |
| `korekta` | `{cialo, zaczep, kosc, pos, rot}`: zaczep na ciele kota |

O zaczepie przedmiotu na zaczepie:
- Zaczep standardowy to `HatAttachment` (kość Head) albo `RightGripAttachment` / `LeftGripAttachment` (kość dłoni).
- Korekta chwytu to dane bohatera, nie przedmiotu (pkt 3). Kostur na człowieku siada więc na `RightGripAttachment`,
  a na kocie według `korekta` (`KosturAttachment` na `StaffPivot`, −0,08 / −90°).
- Kapelusz kota ma `korekta` z `KapeluszAttachment` na `HatPivot`.
- W `ekwipunek.json` bohatera te przedmioty dalej mają zaczep po korekcie (pkt 10). Katalog przelicza go z powrotem
  na zaczep standardowy (`korekty_chwytu` z tego samego pliku). Dzięki temu dawne wpisy kapelusza i kostura mają
  ten sam `zaczep` i `attachment` co przed zmianą.
- Nowe pole główne `bohaterowie` opisuje te pola. `zestawy` mają nazwy trzech bohaterów (`kot_mag` zamiast
  „Rekwizyty Kota-Maga” ma „Kot-Mag Crycket — strój bohatera”).
- Ten sam przebieg pisze `zaczepy_akcesoriow.luau` (102 części: 55 dawnych wierszy bez zmian, tylko
  `rycerz_miecz` stoi teraz w grupie Rycerza, + 47 nowych części bohaterów: 44 segmenty kostne, tarcza Rycerza,
  łuk i sztylet Zwiadowcy). Przedmioty bohaterów mają razem 50 części.

**Propozycja Luau** (`przedmioty_luau.py` → `roblox/PrzedmiotyPropozycja.luau`).
- Wpisy zestawów i broni są jednolinijkowe, bez zmian.
- Przedmiot bohatera ma dawne pola (`name`, `slot`, `category`, `icon`, `iconFile`, `set`) i w kolejnych wierszach
  `body`, `classes`, `hides`, `parent` (`nil` albo id) oraz `meshes = { { id, bone, covers, attachment, fbx, glb[,
  onBody = { kot = { attachment, bone, pos, rot } }] }, … }`. Ustawienia Attachmentu w Handle (pos/rot dla glb
  i fbx) w `meshes` nie ma — są w `zaczepy_akcesoriow.luau` i w `przedmioty.json` pod tym samym id części.
- Narzędzie wypisuje, czego moduł gry `Items` nie zna:
  - slot `OffHand` (`rycerz_tarcza`, `zwiadowca_luk`, `zr_tarcza`, `mag_ksiega`);
  - pola spoza `name`/`slot`/`category`/`icon`;
  - typy ciała i klasy;
  - przedmioty z `parent` (brak slotu `Legs`);
  - 15 zaczepów `Ekw<Kosc>Attachment`, które istnieją tylko w gołym ciele bohatera.
- Kategorie są wszystkie znane grze.

**Zostaje otwarte:**
- decyzje z pkt 8: spodnie (`parent`) czy slot `Legs`; slot `OffHand` dla łuku i tarczy; drobne przedmioty;
- czy gra przyjmie pola `body`, `classes`, `hides`, `parent`, `meshes` i `onBody` — to decyzja Game Directora,
  bo `src/shared/Items.luau` ich nie ma;
- pliki siatek (FBX/GLB) są w `.gitignore`, więc są tylko lokalnie; ikony są w repozytorium. Na koncie Roblox
  nie ma ani jednych, ani drugich;
- droga przez gołe ciało z zaczepami `Ekw…` i `AddAccessory` dalej nie była sprawdzana w Studio;
- testu jednostkowego samego `ekwipunek.py` (pkt 7, kolejność 2) w repozytorium nie ma — wspólny kod sprawdzają
  `--kontrola` bohaterów i regresja z tego etapu (poza repozytorium);
- `katalog_ekwipunku.jpg` (tryb Blendera w `zestawienie.py`) nie pokazuje jeszcze przedmiotów bohaterów:
  `ikony_katalogu()` i `ZESTAWY` (podpis „Rekwizyty Kota-Maga”) są sprzed tego etapu.

## 14. Uszy kota pod hełmem (`ukrywa` „Uszy”, 26.11.2026, propozycja)
Paweł (26.11.2026, przez Karola): hełmy puli wojownika mają zasłaniać kocie uszy. Uszy kota to gołe bryły kości
`LeftEar`/`RightEar` (ostrosłupy), a nie akcesorium ze `znacznik`, więc dawne `ukrywa` (tylko akcesoria ciała,
pkt 9) ich nie obejmowało. Najmniejsze rozszerzenie, bez nowego pola:
- `ekwipunek.ZNACZNIKI_CIALA = {"Uszy": ("LeftEar", "RightEar")}` — znacznik w `ukrywa`, który jest w tej tabeli,
  zdejmuje w `ubierz()` gołe bryły (`golas`) tych kości, tak jak powłoka zdejmuje gołe bryły swojej kości, ale bez
  własnych brył na tych kościach. Znaczniki spoza tabeli (np. „Wlosy”) działają jak dotąd. Ciało bez tych kości
  (człowiek): znacznik nic nie robi.
- **Warunek:** przedmiot z `ukrywa=("Uszy",)` musi mieścić całe uszy w pozie spoczynku — chowamy ucho pod hełmem,
  a nie ucinamy je hełmowi za małemu. Pomiar: `python -B swiat/postacie/pula_wojownika.py --uszy` (zapas = o ile każdy
  punkt brył uszu da się przesunąć w 26 kierunkach, nie wychodząc z hełmu; walce jak gładkie walce Roblox; kod 1, gdy
  zapas < 0,04). Uszy w ramce `HatAttachment` kota: x 0,35…0,98 (na zewnątrz głowy 0,825), y −0,04…0,70 nad czubkiem
  głowy, z −0,21…0,14 — hełm mieszczący uszy ma ok. 2,2 szerokości i sięga ok. 0,8–1,0 nad głowę.
- **Dane dla gry:** `ukrywa: ["Uszy"]` w przedmiocie i `znaczniki_ciala: {"Uszy": ["LeftEar", "RightEar"]}` w
  `ekwipunek.json` bohatera (pula wojownika). Rig z części: `Transparency = 1` części kości uszu, gdy przedmiot jest
  założony (jak włosy); rig z siatek: siatki `LeftEar_Geo`/`RightEar_Geo`.
- **Upadek:** w klipie `upadek` hełm zsuwa się z głowy (kość `HatPivot`), a uszu w modelu nie ma przez cały klip —
  eksport (FBX/GLB, części Roblox) nie zna przełączania widoczności w czasie klipu, a klipy nie mają kanału skali.
  W grze może to zrobić skrypt: odsłonić uszy w chwili zsunięcia hełmu (klatka 30 klipu upadku kota,
  `kot_mag.UPADEK_LOT`). Niezrobione.
- W ruchu uszy (gdyby były widoczne) wychodziłyby poza hełm do 0,17 studa (`trafienie`, `unik` — uszy kładą się po
  sobie); są schowane, więc nie przenikają.
- Stan kontraktu dla innych ciał bez zmian: kapelusz Kota-Maga dalej nic nie ukrywa (uszy przez rondo).

## 15. Rodzaje chwytu broni (`Akcesorium.chwyt`, 26.11.2026, propozycja)
Karol (26.11.2026): „odróżniaj różdżkę od miecza i łuk itd.”. Do dziś każda broń w prawej łapie kota szła przez
jedną korektę — chwyt kostura (`KosturAttachment`, obrót (−90, 0, 0)), więc miecz stał pionowo przy biodrze jak
kostur. Teraz broń deklaruje rodzaj, a ciało ma korektę na każdy rodzaj:
- **Deklaracja w broni:** pole `Akcesorium.chwyt` (to samo, które biblioteka ma od dawna dla „drzewce” w przymiarce),
  np. `Akcesorium(..., zaczep="RightGripAttachment", typ="Bron", chwyt="miecz")`. Konwencja modelu bez zmian
  (rękojeść w (0, 0, 0), oś główna w +Y, lico +Z); tarcza i księga jak tarcza Rycerza (blok `uklad(obrot=(−90, 0,
  0))`, osie dłoni).
- **Korekta w ciele:** `KOREKTY_CHWYTU` bohatera ma obok kluczy-zaczepów klucze-rodzaje: {rodzaj: (zaczep ciała, pos,
  obrot)}. `ekwipunek.korekta()` (używają jej `ubierz()` i `Przedmiot.opis()`) bierze najpierw wpis rodzaju, potem
  wpis zaczepu, potem brak korekty — **broń bez rodzaju i ciała bez wpisów rodzajów budują się co do bitu jak
  dotąd** (sprawdzone 26.11.2026: JSON postaci, strojów i `ekwipunek_json` Kota-Maga, Rycerza, Zwiadowcy,
  Kota-Demona, kotów ras i kotów klas — 40 pozycji identycznych przed i po zmianie).
- **Tabela rodzajów i korekty kota:** `swiat/postacie/chwyty.py` (`RODZAJE`, `POCHYLENIE_KOTA` → `KOREKTY_KOTA`).
  Korekta kota to pochylenie broni w ramce dłoni (do przodu, na zewnątrz, skręt), w pozie spoczynku dłoń kota ≈ osie
  świata. Na dziś korekty ma tylko kot (pula wojownika: `KOREKTY_CHWYTU = KM.KOREKTY_CHWYTU + chwyty.KOREKTY_KOTA`);
  Kot-Mag (`kot_mag.py`, zamrożony) i koty klas Pawła (`kot_klasy.py`) mają dawne korekty.

| rodzaj | łapa | zaczep kota | pochylenie (przód, zewnątrz, skręt) | pos | rot korekty |
|---|---|---|---|---|---|
| `miecz` — miecz, tasak, pałka, pogrzebacz | prawa | `KosturAttachment` (StaffPivot) | 10°, 20°, 0 | (−0,08, 0, 0) | (−80, 20, 0) |
| `rozdzka` — różdżka | prawa | `KosturAttachment` | 60°, 10°, 0 | (−0,08, 0, 0) | (−30, 10, 0) |
| `drzewce` — kostur, włócznia (dzisiejszy chwyt) | prawa | `KosturAttachment` | 0, 0, 0 | (−0,08, 0, 0) | (−90, 0, 0) |
| `proca` | prawa | `KosturAttachment` | 5°, 30°, 0 | (−0,08, 0, 0) | (−85, 30, 0) |
| `luk` | lewa | `LeftGripAttachment` | 45°, 30°, −55° (łuk bokiem do patrzącego z przodu) | (0,15, 0,2, 0) | (−6,66, −51,94, 45,58) |
| `tarcza` | lewa | `LeftGripAttachment` | jak u człowieka | (−0,12, 0, 0) | (0, 0, 0) |
| `ksiega` | lewa | `LeftGripAttachment` | jak u człowieka (atrapa wisi pod łapą) | (0, 0, 0) | (0, 0, 0) |

- **Dlaczego miecz odchyla się głównie na zewnątrz, a nie do przodu:** w klipie `upadek` kość `StaffPivot` kładzie
  broń na ziemi tak, że oś dłoni „do przodu” patrzy w dół. Każdy stopień pochylenia do przodu wbija czubek w ziemię
  (miecz 2 studa: 30° → 0,74–0,84 studa pod ziemią, 10° → do 0,19). Odchylenie na zewnątrz leży w płaszczyźnie ziemi.
  Różdżka (60° do przodu) w upadku wchodzi w ziemię — do decyzji, gdy różdżka trafi na kota w grze.
- **Lewa łapa kota nie ma kości nośnej** (jak `StaffPivot` w prawej): łuk, tarcza i księga zostają w łapie także
  w upadku (nie sprawdzane w klipach).
- **Dane dla gry:** część broni w `ekwipunek.json` ma pole `chwyt` (tylko gdy broń je deklaruje), `zaczep`/`pos`/`rot`
  już po korekcie rodzaju; bohater ma `korekty_chwytu` (klucze: zaczepy i rodzaje) i `rodzaje_chwytu` (rodzaj →
  łapa, zaczep standardowy, opis, korekta kota) — `chwyty.dla_gry()`.
- **Jak nowa broń deklaruje rodzaj:** `chwyt="<rodzaj>"` w `Akcesorium`; nowy rodzaj — wpis w `chwyty.RODZAJE` i
  w `chwyty.POCHYLENIE_KOTA`, potem `--przenikanie` puli i plansza `pula_wojownika_chwyty`.
- **Sprawdzenie:** `pula_wojownika.py --przenikanie` (miecz w głowie, hełmie i tułowiu w klipach walki kota; próg
  głowy 0,02, tułowia 0,10; odniesienie Kot-Mag z kosturem), plansza `wynik/_pula_wojownika/d2611_chwyty.jpg`
  (przód i 3/4 każdego rodzaju: `python -B swiat/postacie/przebuduj.py pula_wojownika_chwyty --bez-filmow`).
- **Uwaga dla katalogu:** `zestawienie.py` odwraca `korekty_chwytu` po zaczepie ciała (`{v["zaczep"]: …}`); gdy
  kiedyś obejmie bohatera z rodzajami, kilka kluczy ma ten sam `KosturAttachment` — trzeba będzie brać rodzaj z pola
  `chwyt` części. Dziś katalog czyta tylko Rycerza, Kota-Maga i Zwiadowcę (bez rodzajów).
