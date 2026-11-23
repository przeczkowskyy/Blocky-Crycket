# Próba ubierania postaci (D-071) — przymierzalnia i strój w walce

> **Status: propozycja (prototyp w Studio), nie kanon i nie kod gry.** Projekt, zasady i ustawienia „przyjęte, do
> zmiany”: `PROJEKT.md`. Przed publikacją miejsca: `python -B swiat/stroje_proba/zbuduj.py --usun`.

Gracz podchodzi do stojaka „Przymierzalnia” przy placu startowym, naciska **E** i w tymczasowym oknie zakłada albo
zdejmuje przedmioty po jednym na slot. Na podeście przed lustrem stoi jego bohater w tym stroju (z ruchami walki).
Następna walka — próba walki przy tablicy i walki w lesie — pokazuje bohatera w tym samym stroju.

## Przedmioty do kupienia w trzech stopniach (D-106, 19.11.2026 — wgrane do Studio tego dnia)

Dane przymierzalni mają teraz **80 przedmiotów**: 20 dzisiejszych (bez zmian, na początku, w dawnej kolejności) i 60
nowych z `swiat/postacie/stopnie.py` (las, bagno, dżungla; wpisy z `swiat/postacie/sklep_przedmioty.json`, te same
kontrole pól co dla dzisiejszych). Strój odniesienia dalej równa się szablonowi walki co do bryły.

- **Cztery moduły zamiast jednego** (granica długości jednego modułu to ok. 200 000 znaków, a dane razem mają ok.
  263 tys.): `DaneStrojow.luau` (ustawienia, klasy, 20 dzisiejszych przedmiotów — ok. 82 tys. znaków) oraz
  `DaneStrojowLas.luau` (42 tys.), `DaneStrojowBagno.luau` (58 tys.), `DaneStrojowDzungla.luau` (81 tys.) — po 20
  przedmiotów stopnia. Moduł główny **sam scala** moduły stopni (szuka ich obok siebie, a potem w
  `Workspace/StrojeProba/Moduly`), więc `Ubieranie`, serwer, klient i inne pakiety dalej biorą jedno `D`.
- **Gdy modułu stopnia nie ma** (np. test innego pakietu wczytuje sam `DaneStrojow.luau`), stopnia po prostu nie ma w
  danych: jego nazwa trafia do `D.brakStopni`, znika z list klas i zestawów, a dzisiejsze przedmioty działają jak
  dawniej. Kto chce w teście mieć wszystkie 80 przedmiotów, wkłada do folderu `Moduly` także trzy moduły stopni.
- **W danych klasy:** `przedmioty` to nadal 8 / 8 / 4 dzisiejszych przedmiotów (żeby nic, co je wylicza, nie urosło),
  a nowe pole `stopnie` = lista `{ id, nazwa, przedmioty }`; pełną listę klasy daje `L.przedmiotyKlasy(D, klasa)`
  (w Pythonie `logika_strojow.przedmioty_klasy`). Każdy przedmiot stopnia ma pole `stopien`.
- **Zestawy:** obok `golas` i `komplet` są gotowe komplety `las`, `bagno`, `dzungla` (akcja `zestaw` serwera i
  `L.zestaw`). Okno przymierzalni ma te same przyciski co dawniej (`zestawy_okna` bez zmian); w każdym slocie można
  teraz przełączać cztery przedmioty (dzisiejszy i trzy stopnie), a stopnie wolno mieszać slot po slocie. Nogawice i
  spodnie stopnia idą za zbroją swojego stopnia.
- `zbuduj.py` wgrywa także moduły stopni (przed modułem głównym); `--sucho`, kontrola Luau i testy je obejmują.
- Komplety stopni w klipach walki: test `3d` wypisuje, o ile głębiej pod ziemię schodzą niż strój odniesienia
  (najwięcej Zwiadowca w komplecie Dżungli: 0,535 studa w uniku), i pilnuje, żeby nie było gorzej. Przenikanie broni
  w ciało mierzy `python -B swiat/postacie/przenikanie_stopni.py`.
- **W Studio 19.11.2026** (`zbuduj.py --skrypty`, próba w Play rozszerzona o komplety stopni): S05 — 18 strojów
  (dzisiejsze 3 + komplety las / bagno / Dżungla w każdej klasie) w podglądzie z dokładnie tymi bryłami co w danych;
  S06 — 186 przebiegów klipów klatka po klatce, nic nie odpada od kości, a komplety stopni schodzą pod ziemię
  najwyżej tyle, ile pozwalają granice `GRANICA_STOPNI` z testu 3d (te same liczby w próbie). S03 z kowalem: „>” przy
  hełmie przechodzi do następnego posiadanego hełmu (po nadaniu przedmiotów stopni — leśnego), nie do „bez hełmu”.
  Wynik: 10 × OK, 1 × ? (S09 — las ręcznie), 0 × BŁĄD. S03 puszczony sam (`--tylko S03`, bez S02) bywa za szybki —
  kliknięcie trafia przed narysowaniem okna; w pełnym przebiegu i z S02 przechodzi.

## W Studio (17.11.2026)

**Kontener:** `Workspace/StrojeProba` (atrybut `Wygenerowane`): 6 skryptów i modułów, 14 części stojaka,
1 podpowiedź E. **Stojak:** punkt `(28,6; 0,8; −16,5)`, przodem do startu (kierunek `(−0,87; 0,50)`), podest
`(29,5; 1,5; −17,0)` — na trawie na północny wschód od placu startowego, obok ścieżki na wschód i straganu
w paski. Nie stoi na żadnej ścieżce, nie zasłania tablicy Training Center (zachód placu) ani bramy do lasu
(południe). Miejsce wybrane ręcznie (atrybut `RecznyPunktStojaka`): automatyczne szukanie postawiło stojak na
ścieżce przed różowym portalem. Zrzuty: `klatki/00_stojak_od_startu.jpg`, `klatki/00_stojak_z_daleka.jpg`.
W `Workspace/TestWalki2` jest moduł `Aktorzy` z haczykiem stroju (`zeStrojem`).

**Próba w Play** — `testy/proba_play.py` (`testy/wynik_play.json`), Studio na wierzchu, okno 2041 × 1153:

| Punkt | Wynik |
|---|---|
| S01 gotowość | OK — serwer i klient gotowi, podpowiedź E włączona, skrót danych = lokalny, haczyk w `Aktorzy` |
| S02 prawdziwe E przy stojaku | OK — okno otwarte, kamera na podgląd; X zamyka, kamera postaci wraca |
| S03 prawdziwe kliknięcie „>” przy hełmie | OK — serwer zdjął hełm, podgląd w nowym stroju |
| S04 odmowy serwera | OK — przedmiot innej klasy, część zbroi, zła klasa, zły slot, nieznany przedmiot; 5 z 8 zapytań naraz „za szybko”; strój bez zmian |
| S05 podgląd: 3 klasy × (goły, komplet, mieszany) | OK — w każdym dokładnie te bryły co w danych; cały bohater nad oknem, w środku ekranu |
| S06 każdy klip każdej klasy w 3 strojach, klatka po klatce | OK — 93 przebiegi; żadna bryła nie odeszła od kości (> 0,02 st); nic głębiej pod ziemią niż komplet; kapelusz i kostur kota leżą po upadku na ziemi |
| S07 próba walki w stroju z przymierzalni (3 klasy) | OK — bohater gracza w walce ma strój i liczbę brył z danych; zrzuty w trzech chwilach |
| S08 „Dawny wygląd” | OK — walka z dawnym szablonem (127 brył, bez atrybutu stroju) |
| S09 walka w lesie | ? — las gra tym samym `Aktorzy.nowy` (sprawdzone w kodzie), próby w lesie nie było |
| S10 konsola | OK — bez wierszy `[StrojeProba]` (po poprawce czekania na szablon, niżej) |
| S11 okno na ekranie 667 × 375 (emulacja) | OK — tekst 12 pt, bohater na 0,01–0,35 wysokości ekranu, góra okna 0,40 |

Zawis ciała w ostatniej klatce upadku (sprawa „do ustalenia”, PROJEKT.md pkt 4.3) — w Studio te same liczby co bez
Studio: goły Rycerz 0,247 studa, Rycerz w hełmie, butach, z mieczem i tarczą 0,049, goły kot 0,198, kot w kapeluszu
z kosturem 0,198 (kapelusz i kostur leżą na ziemi), Zwiadowca w każdym stroju na ziemi.

**Stara próba walki** po haczyku: `test_walki2/testy/test_walki_play.py --szybko` — **111/111** (jak rano), konsola bez komunikatów próby walki. Końcowy przebieg `proba_play.py` na ostatecznym kodzie: **10 × OK, 1 × ? (S09), 0 × BŁĄD**.

## Poprawione po zrzutach i pomiarach

1. **Kadr podglądu.** Zrzuty pokazały bohatera do połowy schowanego za oknem. Pomiar (`SterowanieKlienta`
   „kadr”: rzut obrysu postaci na ekran i góra okna) wykazał, że kamera stawała się z powrotem kamerą postaci
   (inny skrypt zmieniał jej typ tuż po starcie) — teraz okno trzyma kamerę co klatkę, a kąt jest liczony dokładnie
   (środek postaci na 0,21 wysokości ekranu, postać ok. 0,34 ekranu). Wynik w S05 i S11.
2. **Napisy dla gracza** bez języka twórców: zamiast kodów odmowy „Tego nie da się teraz założyć.”, polskie nazwy
   ruchów („Chód”, „Miażdżący cios”), „Przywrócono dawny wygląd.”, nagłówek tylko „PRÓBA”.
3. **Szablon walki ze strumieniowania.** Szablony aktorów stoją przy arenie walki, daleko od stojaka; tuż po
   starcie klienta podgląd raz trafił na niedoszły szablon (ostrzeżenie w konsoli, podgląd bez ruchu). Teraz czeka na
   korzeń i kości szablonu i ponawia budowę.
4. **Miejsce stojaka** — patrz wyżej.

## Czego nie sprawdzono

- Walki w lesie (stary las, las-pas) w stroju — ten sam kod co próba walki, ale bez próby w Play.
- Prawdziwego telefonu i dotyku (okno na emulacji 667 × 375, kamera w proporcjach ekranu Studio).
- Dwóch graczy naraz (każdy ma własny atrybut stroju i lokalny podgląd).
- Pełnych starych prób walki (`test_v3_play`, `test_poprawek_play`) — wspólna regresja koordynatora na koniec dnia.

## Polecenia

```
python -B swiat/stroje_proba/dane.py --sprawdz            # dane aktualne i zgodne z szablonem walki
python -B swiat/stroje_proba/testy/test_strojow.py        # bez Studio, ok. 30 s
python -B swiat/stroje_proba/zbuduj.py --sucho
python -B swiat/stroje_proba/zbuduj.py [--studio <id>]    # kontener i stojak (Edit)
python -B swiat/stroje_proba/zbuduj.py --skrypty          # tylko moduły i skrypty
python -B swiat/stroje_proba/zbuduj.py --walka            # tylko moduł TestWalki2/Moduly/Aktorzy
python -B tools/studio_okno.py --na-wierzch
python -B swiat/stroje_proba/testy/proba_play.py [--tylko S05,S11] [--bez-zrzutow]
```
