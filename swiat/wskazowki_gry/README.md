---
status: propozycja
---
# Wskazówki celu dla nowego gracza

**Status: propozycja** (17.11.2026, raport przejścia gry `swiat/przejscie_gry/RAPORT_PRZEJSCIA.md`, M3: „brak celu
w pierwszej minucie”). Teksty i kolejność kroków nie są kanonem — do decyzji Karola i Pawła.

> **W skrócie.** Kontener `Workspace/WskazowkiGry` (atrybut `Wygenerowane`) z samym kodem klienta. U góry ekranu
> mała linijka celu z krzyżykiem (jedno kliknięcie chowa wskazówki do końca sesji), a do tego strzałka przy przycisku
> TELEPORT albo znacznik ▼ nad celem w świecie. Krok wynika ze stanu gracza, nie ze sztywnego scenariusza. Niczego nie
> wysyła do serwera, cudzych instancji tylko czyta. Schowane w walce, przelocie, chmurach, mini-grze i przy wyborze
> klasy.

## Kroki

| Kiedy | Tekst (z `ustawienia.json`) | Cel |
|---|---|---|
| (a) po wyborze klasy, poza lasem | Otwórz TELEPORT i wybierz Las | strzałka przy TELEPORT |
| (b) w lesie, przed pierwszą wygraną | Podejdź do potwora i wciśnij E | ▼ nad najbliższym potworem (do 160 st) |
| (c) po pierwszej wygranej, ze stanem gracza | Zdobywaj poziomy (masz N) — Strażnik czeka na końcu lasu | ▼ nad Strażnikiem |
| (c) bez stanu gracza | Strażnik Gaju czeka na końcu lasu | ▼ nad Strażnikiem |
| (d) po przegranej, gdy trening wzmacnia walkę | Wróć do miasta i potrenuj u trenera / Potrenuj u trenera… | ▼ nad Kamieniem Powrotu / trenerem |
| (d) po przegranej bez stanu gracza | Spróbuj słabszego potwora — poziom widać nad głową | ▼ nad potworem |
| (e) po Strażniku | Brama otwarta — idź dalej, za arenę Strażnika | ▼ za bramą |
| za bramą | Bagno już wkrótce… (albo „Idź dalej — przed tobą Bagno”, gdy stoi `BagnoPasGra`) | — |
| (e) po Strażniku lasu, gdy stoi Bagno | Brama otwarta — idź do Bagna / w mieście: Bagno otwarte: TELEPORT → Bagno | ▼ za bramą lasu / strzałka |
| w Bagnie | jak w lesie: potwór → „Zdobywaj poziomy (masz N) — Strażnik Topieli na końcu Bagna” → po Strażniku Topieli „Brama do Dżungli otwarta — Dżungla już wkrótce” | ▼ nad potworem / Strażnikiem Topieli / bramą |
| (f) Złoto ≥ cena jajka biomu, w którym jest gracz (w mieście: lasu), i jeszcze żadnego jajka tego biomu (17.11.2026, stoi `PetyProba`) — przed innymi krokami, nie za bramą | Masz dość Złota na jajko — inkubator przy wejściu do lasu / w Bagnie: Masz dość Złota na jajko Bagna — inkubator przy pomoście / w mieście: …: TELEPORT → Las (inkubator) | ▼ nad punktem E inkubatora biomu / strzałka |

Biomy (las-pas, Bagno) są w `ustawienia.json` → `zrodla.biomy`: kontener, moduł danych (`Moduly/DanePasa`), Kamień
Powrotu, atrybut pokonanego Strażnika. Biom rozpoznaje się po prostokącie `wejscie` z jego danych (Bagno ma
pierwszeństwo — jego początek leży w prostokącie lasu za bramą). Liczniki walk są osobne dla każdego biomu, więc
w Bagnie kroki zaczynają się od „potwora”, choć w lesie gracz już wygrywał.
Znaki: strzałka przy TELEPORT to „<” w GothamBlack (84 px), a znacznik w świecie to romb z ramki — znaki „◀” i „▼”
gra rysowała zastępczą, malutką czcionką (wspólna próba 17.11.2026).

W mieście kroki (c)–(e) mają wersję z „TELEPORT → Las” i strzałką przy przycisku. Kroki (d) „trening” i (c)
„poziomy” pokazują się tylko, gdy działa `Workspace/StanGracza` (`SerwerStanuGotowy`, a dla treningu
`TreningPodlaczony`) — bez niego trening i poziomy nic nie zmieniają, więc wskazówka by kłamała. Przegrana przestaje
liczyć się do (d), gdy gracz wejdzie na stanowisko Training Center albo wygra kolejną walkę.

## Skąd stan (tylko odczyt)

- atrybuty gracza: `Class`, `Level`, `PokonalStraznikaLasu`, `TreningGra` (stanowisko mini-gry); `Gold`; dla każdego
  biomu z inkubatorem (`zrodla.biomy[].atrybut_ceny_jajka` i `atrybut_kupionych_jajek`): `PetyCenaJajka` /
  `PetyCenaJajkaBagna` (cena następnego jajka) i `PetyKupioneJajka` / `PetyKupioneJajkaBagna` (ile jajek biomu gracz
  kupił) — pisze je `swiat/pety_proba`;
- walki w lesie: u klienta na `LasPasGra` / `LasPotwory` odtwarzacz ustawia `OstatnieZiarno`, `OstatniWynik` i
  `OstatniStan = "wynik"` — jedna walka na wejście w stan „wynik” z nowym ziarnem (walka przerwana resetem się nie
  liczy); liczniki tylko w pamięci klienta (sesja);
- położenie: prostokąt `wejscie` i `brama.x` z modułu `LasPasGra/Moduly/DanePasa` (bez niego wskazówki zakładają
  „miasto”);
- cele: `LasPasGra/Stan` (potwory, Strażnik), `DanePasa.zaBrama`, `LasPasGra/Punkty/KamienPowrotu`,
  `MiasteczkoBazarGra/Punkty/E training_center`, `TreningProba/TablicaWejscia/E`;
- ekrany: `HUD` (Pawła — tylko położenie przycisku TELEPORT), `TestWalki2Cutscenka`, `ClassSelect`;
  `TeleportChmury.Trwa`, typ kamery.

## Pliki

| Plik | Co to jest |
|---|---|
| `ustawienia.json` | jedyne źródło: teksty kroków, nazwy instancji innych pakietów, wygląd |
| `dane.py` | generator `zrodla/DaneWskazowek.luau` (+ przypadki wzorcowe); `--sprawdz` |
| `logika_wskazowek.py` | lustro `zrodla/LogikaWskazowek.luau` (wybór kroku, miejsce) |
| `zrodla/KlientWskazowek.client.luau` | klient: linijka celu, strzałka, znacznik, zbieranie stanu, haczyk testowy |
| `sprawdz_luau_wskazowek.py` | kontrola statyczna Luau (reguły jak w `swiat/las_potwory`, SetAttribute tylko na kontenerze, bez FireServer, bez przełączania cudzych ekranów) |
| `zbuduj.py` | budowa w Studio: `--sucho`, `--usun`, `--studio` |
| `testy/test_wskazowek.py` | 24 testy offline (dane, logika, Luau w luau_mini, styki z innymi pakietami, prywatność) |

## Budowa i wyłączenie

```
python -B swiat/wskazowki_gry/dane.py                 # po zmianie ustawień
python -B swiat/wskazowki_gry/testy/test_wskazowek.py # 24 testy, < 1 s
python -B swiat/wskazowki_gry/zbuduj.py --sucho       # bez Studio
python -B swiat/wskazowki_gry/zbuduj.py               # Studio w trybie Edit
python -B swiat/wskazowki_gry/zbuduj.py --usun        # gra wraca do stanu sprzed pakietu
```

Haczyk testowy (klient): `workspace.WskazowkiGry.Sygnaly.SterowanieKlienta:Invoke("stan" | "wylacz" | "wlacz" |
"zeruj" | "ustaw", pole, wartość)`. Próba w Play: `swiat/przejscie_gry/proba_dymna.py` (punkty D11, D12).

## Czego nie sprawdzono (pakiet napisany bez Studio)

- Nic w grze: wygląd linijki i strzałki, położenie strzałki przy TELEPORT (HUD Pawła może ignorować pasek Robloxa —
  kod przelicza wcięcie), znacznik nad potworem w ruchu, telefon.
- Czy linijka nie zachodzi na panel bohatera lasu (u góry na środku, `PANEL_Y = 8`) — linijka stoi 56 px niżej.

## Do decyzji

- **Teksty i kolejność kroków** (propozycja) — czy (c) ma prowadzić do Strażnika od razu po pierwszej wygranej.
- **Wyłączenie na stałe:** dziś krzyżyk działa do końca sesji (bez zapisu). Zapis w profilu gracza — razem ze stanem
  gracza.
- **Bór (stary las):** traktowany jak miasto (krok „TELEPORT → Las”), bo wskazówki znają tylko las-pas.
