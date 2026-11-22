# Zabawki — „EAT & EVOLVE” i „LURE A MONSTER” (21/22.11.2026, propozycja)

Po lekcji z Pet Areny (`B&C/Wytwórnia/Lekcje z prototypów.md`: w trzech grach sama czynność gracza nie bawiła) dwie małe
**zabawki**: sama czynność od pierwszych sekund, bez złota, jajek, sklepu, zapisu, tablic, prezentów i samouczków.
Kierunki: `B&C/Wytwórnia/Kierunki z rynku 2026-11-21.md`. Karol rano wybiera tę, przy której chce „jeszcze raz”.

Wejście: ekran wyboru z dwoma dużymi przyciskami (nazwa + jedno zdanie); w zabawce mały przycisk MENU wraca do wyboru.
Kontener `Workspace/ZabawkiGra` w miejscu „Throw & Catch Monsters”; każda zabawka na własnym terenie (1: wokół
(0, 0, 700), 2: wokół (700, 0, 0)). Pet Arena wyłączona wyłącznikiem (`swiat/pet_arena/zbuduj.py --wlacz off`),
kontener zostaje. **Skrypty bez strażnika „tylko Studio”** — działają w prywatnej wersji testowej na telefonie. Haczyki
prób tylko po stronie serwera (`Sygnaly/SterowanieSerwera`); klient czyta wejście prób z atrybutów lokalnego gracza
(`ZT_TestSter`, `ZT_TestDash`, `ZT_TestRzut`, `ZT_TestCel`) — to samo, co palec.

## Zabawka 1 — EAT & EVOLVE (jesteś potworem, jesz i rośniesz)
- Pole: koło o promieniu 120 st z niskim murem, 9 skał i 150 świecących kulek. Kulki stoją w stałych miejscach i wracają
  po 7 s.
- Gracz od razu jest najmniejszym potworem i startuje obok kulki, więc pierwsze zjedzenie zdarza się w ok. 0,5 s.
- Sterowanie:
  - telefon: drążek pojawia się pod lewym kciukiem;
  - komputer: WASD / strzałki, DASH na spacji;
  - pad: lewa gałka, DASH na A / R2.
- **DASH**: zryw × 2,3 na 0,38 s, odnowienie 3 s (cień na przycisku).
- Kamera z góry ma stałą orientację i oddala się, gdy rośniesz.
- **Zjadanie**:
  - zjadasz, gdy jesteś większy o co najmniej 15 % i środek ofiary wejdzie w ciebie;
  - podobni się odbijają (kurz, dźwięk, spłaszczenie);
  - mały jest szybszy: v = 30 / (1 + 0,28 √m).
  - Krążek pod każdym potworem mówi, co możesz: zielony — zjesz go, czerwony — on zje ciebie, biały — odbijecie się.
- **Ewolucja**: masa → rozmiar rośnie płynnie, a 6 form zmienia się na progach 2,2 / 6 / 12 / 22 / 38 (kulka +0,2):
  Slime → Shroomling → Leaf Fox → Thorn Wolf → Forest Troll → Hut Toad.
  - Przy zmianie formy: błysk, pierścień, „EVOLVED!” i wstrząs.
  - Pasek „do następnej formy” jest jedynym stałym elementem ekranu poza DASH i MENU.
- **Zjedzony**: „POP!” i wstrząs. Po 2 s wracasz formę niżej, z tarczą na 3 s.
- **Świat żyje sam**: 20 botów od 0,6 do 26 masy. Gonią mniejszych i kulki, uciekają przed większymi i czasem robią
  DASH. Duzi powoli tracą masę, a zjedzone boty wracają małe, więc zawsze jest co jeść i przed kim uciekać.
- **APEX**: największy (od masy 20) dostaje koronę. Gdy APEX-em zostaje gracz, serwer ogłasza „<nazwa> is the APEX!”.
  Obgryzania APEX-a przez małych nie zdążyłem zrobić.
- Serwer liczy wszystko w 2D (krok 0,05 s). Własny potwór jest przewidywany u klienta: rusza w tej samej klatce, a serwer
  łagodnie go dociąga.

## Zabawka 2 — LURE A MONSTER (rzuć przynętę, zwab potwora)
- 8 zagród obok siebie na skraju łąki (każdy gracz ma swoją); łąka 150 × 260 st w trzech strefach: NEAR (Common /
  Uncommon, wolne), MID (Uncommon / Rare), FAR (Rare–Legendary, większe i szybkie).
- **Proca**: przytrzymaj i odciągnij palcem (mysz: przeciągnij) — kierunek ± 38°, siła 0–1; kropki toru tylko na
  początku łuku; kamera patrzy tam, gdzie wyląduje. Puść — przynęta leci łukiem od razu (bez czekania na serwer).
- Trafienie: potwór w promieniu 4 st + promień potwora przy lądowaniu zjada przynętę i idzie do twojej zagrody; krótka
  scena **LURED!** (rzadkość, odmiana BIG / GOLDEN / GIANT — 8 / 3 / 0,5 %). Pudło płoszy pobliskie.
- Co 40 s przez daleką strefę przebiega **rzadki potwór** (Epic / Legendary, złoty) — „RARE MONSTER!”.
- Zasięg rośnie z każdym zwabieniem (105 + 8 za zwabionego, do 250) — daleka strefa po ok. 8–12 zwabieniach.
- Zwabione stoją w zagrodzie (najwyżej 12 widocznych); licznik u góry: ile potworów i najlepsza zdobycz.
- Ten sam potwór i dwie przynęty: idzie do tej, która wylądowała pierwsza.

## Jak zbudować i sprawdzić
```
python -B swiat/zabawki/dane.py                      # dane (pety, dźwięki z Pet Areny) → zrodla/DaneZabawek.luau
python -B swiat/zabawki/testy/test_zabawek.py        # logika bez Studio
python -B swiat/zabawki/zbuduj.py --studio <id>      # budowa (--skrypty: same skrypty; --sucho: bez Studio)
python -B swiat/zabawki/testy/proba_play.py --studio <id> [--tylko 1|2] [--bez-zrzutow]
```
Budowa odmawia w miejscu gry B&C, poza trybem Edit i przy obcym obiekcie `ZabawkiGra`.
Wyłącznik (22.11.2026, dodany przy Monster Evolution): `python -B swiat/zabawki/zbuduj.py --wlacz on|off --studio <id>` —
atrybut `ZabawkiWlaczone` i `Enabled` obu skryptów (źródła bez zmian; pełna budowa zachowuje stan). Wzorce potworów kopiuje z
`Workspace/PetArenaGra/Wzorce`.

## Próby (22.11.2026 ok. 00:00–00:05)
- Testy logiki: 7 OK.
- Play: zabawka 1 12/12, zabawka 2 (pełny przebieg razem z zabawką 1) 18/18; okno Studio 2041 × 1113.

| Punkt | Wynik |
|---|---|
| menu | po wejściu ekran wyboru; Pet Arena nie startuje (serwer PA nieaktywny, gracz bez miejsca PA, kamera nieruszana) |
| Z11 pierwsza akcja | pierwsza kulka zjedzona **ok. 0,5 s** po wyborze (start obok kulki) |
| Z12–Z15 | EVOLVED! na progu; zjedzenie mniejszego bota; DASH; zjedzony przez większego → po 2 s forma niżej z tarczą |
| Z16 klatka | **16,7–17,5 ms** przy 20 botach i 150 kulkach (okno komputera; emulacji telefonu nie było) |
| Z17 opóźnienie 2 × 60 ms | własny potwór przesunięty o ok. 1,5 st w 0,15 s — rusza od razu |
| W21 pierwszy rzut / zwabienie | pierwszy rzut ok. 1,5–3,4 s od wyboru, **pierwsze zwabienie 2,1–4,1 s** (celowany rzut w najbliższego) |
| W22–W25 | pudło płoszy; GIANT z wymuszonym losem; rzadki biegacz; zasięg po 12 zwabieniach 201 st; klatka 16,7 ms |

Zrzuty: `klatki/menu.jpg`, `zj_gra.jpg`, `zj_ewolucja.jpg`, `zj_duzy.jpg`, `wb_celowanie.jpg`, `wb_zwabiony.jpg`, `wb_giant.jpg`.

## Telefon 667 × 375 (emulacja, 22.11 ok. 00:11)

`python -B swiat/zabawki/testy/proba_telefon.py --studio <id>` — **3/3 OK**: ekran wyboru (oba przyciski w całości,
286 × 230 pt), EAT & EVOLVE (MENU 88 × 46 pt, DASH 96 pt, pasek formy — bez nakładania), LURE A MONSTER (licznik,
MENU, kropki toru); klatka 16,7 ms w obu. Poprawione: MENU było 40 pt wysokości (teraz 46), zwabione potwory w zagrodzie
są o połowę mniejsze, a kamera łąki stoi bliżej zagrody — zagroda nie zasłania łąki. Emulacja: atrybut `ZT_Emulacja`.
Zrzuty: `klatki/tel_menu.jpg`, `tel_eat.jpg`, `tel_lure.jpg`.

## Ograniczenia
- Prawdziwego dotyku nie da się wywołać z prób — drążek i procę sprawdza wejście prób (to samo co palec po stronie
  logiki); sam dotyk trzeba potwierdzić na telefonie.
- Obgryzanie APEX-a przez małych i rozsypywanie kulek przy jego rozbiciu: nie ma.
- Boty są proste (nie zastawiają pułapek); przy wielu graczach zagrody 1–8, dziewiąty gracz zostaje w menu.
- Liczby to propozycja do strojenia po graniu.
