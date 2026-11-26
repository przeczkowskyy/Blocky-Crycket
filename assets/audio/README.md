# Muzyka i dźwięki — pierwsza partia (do odsłuchu)

Wygenerowane 16.11.2026 w Higgsfield (zgoda Karola z 16.11.2026). **Status wszystkich plików: do odsłuchu** — nic nie jest wybrane ani wgrane do Roblox.
**Stan na 16.11.2026 wieczorem:** Karol przesłuchał partię, zaakceptował ją w panelu („jest bardzo dobre”; dalsze poprawki możliwe) i poprosił o wypchnięcie plików. Gotowe pliki są więc w repo: `muzyka/` (pełne wersje `.mp3` i wersje do pętli `_petla.ogg`) oraz `dzwieki/` (warianty A i B). Lokalnie zostają tylko oryginały sprzed obróbki (`oryginaly/`) i składanki do odsłuchu (`przeglad/`). `manifest_audio.json` ma prompty, identyfikatory zleceń, koszty i pomiary. Sekcja „Zanim wgramy do Roblox” niżej pozostaje aktualna — do Roblox nic nie jest wgrane, a prawa do użycia w opublikowanej grze są do wyjaśnienia.

**Druga partia (18.11.2026):** pięć nowych utworów — walka, walka ze Strażnikiem krainy, mini-gry Training Center, drugi utwór Bagna i Dżungli — czeka na odsłuch. Opis w sekcji „Druga partia” niżej, po tabeli muzyki pierwszej partii.

## Najpierw przesłuchaj

1. `muzyka/muzyka_01_menu_a.mp3` (potem `_menu_b`): motyw przewodni, od niego zależy charakter całej ścieżki.
2. `muzyka/muzyka_02_bazar_targ.mp3` (potem `03_bazar_rzemieslnicy`, `04_bazar_wieczor`): w miasteczku gracz spędza najwięcej czasu.
3. `muzyka/muzyka_05_las_a.mp3` (potem `_las_b`): pierwsza kraina.

Pełne wersje `.mp3` są do oceny utworu. Wersje `_petla.ogg` są do gry: włącz je w odtwarzaczu z powtarzaniem jednego utworu (np. VLC) i posłuchaj miejsca, w którym koniec przechodzi w początek. MP3 nie nadaje się do pętli, bo koder dokleja ciszę na początku i końcu.

## Muzyka (ElevenLabs Music v2.5, instrumentalnie)

Model: `elevenlabs_music_v2_5`, najnowszy model muzyczny na liście Higgsfield (są jeszcze ElevenLabs Music v2 i Sonilo Music). Ma osobny przełącznik „tylko instrumenty” (`force_instrumental`) i pozwala ustawić dokładną długość. Wszystkie prompty mają ten sam opis wspólnej palety (mała bajkowa orkiestra: pizzicato, flet, klarnet, fagot, waltornia, dzwonki, marimba, ukulele), a różnią się nastrojem i tempem.

| Plik | Czego się spodziewać (tak zamówiono, nikt jeszcze nie słyszał) | Pełna / pętla | Uwagi techniczne |
|---|---|---|---|
| `muzyka_01_menu_a` | Zapraszający motyw na flecie i dzwonkach nad skocznym pizzicato, ok. 110 BPM | 90,0 s / 69,8 s | oryginał kończy się akordem i ciszą, więc w pętli jest 18 s mniej |
| `muzyka_01_menu_b` | Ten sam charakter, melodia na klarnecie i ukulele z lekkim werblem, ok. 104 BPM | 90,0 s / 80,8 s | oryginał urywa się w pełnym graniu |
| `muzyka_02_bazar_targ` | Gwarny, wesoły targ: ukulele, pizzicato, klarnet, tamburyn, ok. 112 BPM | 90,0 s / 85,7 s | urywa się w pełnym graniu |
| `muzyka_03_bazar_rzemieslnicy` | Spokojna uliczka warsztatów: fagot i marimba, stukanie jak młoteczki, ok. 96 BPM | 90,0 s / 75,0 s | urywa się w pełnym graniu |
| `muzyka_04_bazar_wieczor` | Ciepły walc na wieczór: celesta, harfa, cichy flet, ok. 80 BPM | 90,0 s / 81,0 s | urywa się w pełnym graniu |
| `muzyka_05_las_a` | Jasny, baśniowy las z nutą tajemnicy: flet, smyczki, harfa, ok. 92 BPM | 90,0 s / 78,2 s | ma zakończenie i ciszę |
| `muzyka_05_las_b` | Inne ujęcie lasu: duet klarnetu i fletu, marimba, ok. 98 BPM | 90,0 s / 78,3 s | ma zakończenie |
| `muzyka_06_bagno` | Leniwe, „upiorne na wesoło”: fagot, kontrabas, guiro jak żaby, ok. 84 BPM | 90,0 s / 68,6 s | najkrótsza pętla, dopasowanie miejsca cięcia 0,81 |
| `muzyka_07_dzungla` | Bębny ręczne, marimba, ksylofon, energicznie, ok. 120 BPM | 90,0 s / 80,0 s | urywa się w pełnym graniu |
| `muzyka_08_pustynia` | Ciepła wędrówka: szarpane struny, bębenek ramowy, lekko orientalna skala, ok. 100 BPM | 90,0 s / 86,4 s | najlepsze dopasowanie pętli (0,96) |
| `muzyka_09_gory_tundra` | Przestrzeń: waltornia, dzwoneczki sań, smyczki jak wiatr, ok. 90 BPM | 90,0 s / 84,0 s | ma zakończenie |
| `muzyka_10_lodowiec` | Chłodny spokój: celesta, pozytywka, wysokie smyczki, ok. 76 BPM | 90,0 s / 75,3 s | **uwaga:** koniec pętli o 6,8 dB głośniejszy niż początek, na szwie może być słychać spadek |
| `muzyka_11_wulkan` | Niskie bębny, napięcie, ale przygodowo, ok. 116 BPM | 90,0 s / 74,5 s | ma krótkie wyciszenie |
| `muzyka_12_krysztaly` | Magicznie, iskrząco, finałowo: dzwonki, celesta, harfa, waltornia, ok. 108 BPM | 90,0 s / 80,0 s | ma krótkie wyciszenie |

## Druga partia (18.11.2026) — pięć utworów do odsłuchu

**Status: do odsłuchu (18.11.2026).** Nikt jeszcze nie słyszał tych utworów — opisy niżej mówią, co zamówiono, a nie co wyszło. Każdy utwór można odrzucić; wtedy trzeba zbudować arkusz muzyki od nowa bez niego (polecenie niżej). Do Roblox nic z tej partii nie jest wgrane.

Ten sam model i te same ustawienia co w pierwszej partii (`elevenlabs_music_v2_5`, 90 s, „tylko instrumenty”), ten sam opis wspólnej palety w promptach. Pełne prompty, identyfikatory zleceń i pomiary: `manifest_audio.json` (pięć ostatnich wpisów listy `muzyka` i blok `partia_2`).

| Plik | Czego się spodziewać (tak zamówiono, nikt jeszcze nie słyszał) | Pełna / pętla | Uwagi techniczne |
|---|---|---|---|
| `muzyka_13_walka` | Walka ze zwykłym przeciwnikiem: szybko, skocznie, „bohatersko na wesoło” — smyczki staccato i pizzicato, werbel, tamburyn, ksylofon i flet piccolo, ok. 138 BPM | 90,0 s / 69,6 s | urywa się w pełnym graniu; oryginał najgłośniejszy z partii (-12,3 LUFS, szczyt +0,2 dBTP), ściszony o 3,7 dB; najwyższe dopasowanie pętli (0,99) |
| `muzyka_14_walka_straznik` | Walka ze Strażnikiem krainy: większa i bardziej dramatyczna, ale nadal bajkowa — niskie bębny i kotły w marszowym rytmie, fagot, niskie smyczki, waltornia, ok. 126 BPM | 90,0 s / 76,2 s | ma zakończenie (żywa muzyka do 88,0 s); najniższe dopasowanie pętli w partii (0,93) |
| `muzyka_15_trening` | Mini-gry Training Center: sportowo i motywująco — klaskanie, drewniane klocki, krowi dzwonek, marimba i ukulele, piccolo i klarnet, ok. 128 BPM | 90,0 s / 75,0 s | **uwaga:** oryginał ma cichszy wstęp — pierwsze ok. 7,5 s jest o ok. 7 dB cichsze niż reszta (zamawiany był start „od razu w rytmie”); pętla zaczyna się za wstępem (od 11,3 s), więc wstęp słychać tylko w pełnej wersji |
| `muzyka_06_bagno_b` | Bagno, drugie ujęcie: sennie i psotnie — waltornia z tłumikiem, niski klarnet, szarpany kontrabas, guiro, marimba „jak pękające bąbelki”, ok. 88 BPM | 90,0 s / 84,5 s | urywa się w pełnym graniu; szczyt nie pozwolił dojść do -16 LUFS (pełna -16,9, pętla -16,8) |
| `muzyka_07_dzungla_b` | Dżungla, spokojniejsze ujęcie: ciekawie i słonecznie — marimba jak kalimba, drewniane bębny, grzechotki, flet z trylami jak ptaki, bongosy, ok. 104 BPM | 90,0 s / 83,1 s | ma zakończenie i 0,3 s ciszy; koniec pętli o 3,2 dB głośniejszy niż początek (pierwsze i ostatnie 2 s) |

**Jak słuchać:** pełne wersje `muzyka/<nazwa>.mp3` do oceny utworu, wersje `muzyka/<nazwa>_petla.ogg` z powtarzaniem jednego utworu do oceny szwu (jak w pierwszej partii). W grze utwory tej partii mają grać z jednego pliku — arkusza muzyki (niżej).

**Kontrola techniczna drugiej partii** (liczby w manifeście):
- Oryginały: MP3 128 kb/s, 44,1 kHz, stereo, każdy 90,04 s, głośność od -17,0 do -12,3 LUFS. Po obróbce pełne wersje mają -16,0 LUFS (Bagno B -16,9, bo nie pozwolił szczyt), a true peak najwyżej -1,3 dBTP; pętle od -16,8 do -15,8 LUFS, true peak najwyżej -1,4 dBTP.
- Skrypt pierwszej partii się nie zachował, więc obróbkę robi nowe narzędzie `tools/audio_petla.py`, napisane według zasad z manifestu (te same wagi: 0,4 rytm + 0,4 harmonia + 0,2 barwa; 1 s liniowego przenikania końca w początek). Cechy są policzone od nowa, więc **wynik dopasowania nie jest ściśle porównywalny z pierwszą partią** (na utworach pierwszej partii nowe narzędzie daje liczby od 0,02 niższych do 0,12 wyższych niż zapisane wtedy). Sprawdzenie narzędzia na 14 oryginałach pierwszej partii (samo liczenie, pliki pierwszej partii zostały nietknięte): koniec żywej muzyki wyznaczyło tak samo w 13 utworach, w 7 wybrało pętlę tej samej długości co wtedy (różnica najwyżej 0,02 s), a w pozostałych 7 inne powtórzenie — pętlę o 2–11 s dłuższą albo krótszą.
- Pętle: dopasowanie 0,93–0,99; skok próbki na szwie od 0,0002 do 0,026 i w każdym utworze jest mniejszy niż zwykła różnica sąsiednich próbek w tym miejscu (pole `skok_sasiednich_probek_p95`), czyli szew nie daje trzasku. Różnica głośności między pierwszymi a ostatnimi 2 s pętli: od -0,5 do 1,5 dB, w Dżungli B 3,2 dB.
- Długość każdej pętli to niemal dokładnie całkowita liczba taktów przy zamówionym tempie (walka, Strażnik i trening po 160,0 uderzeń = 40 taktów; Bagno B 124,0 = 31 taktów; Dżungla B 144,0 = 36 taktów). To zgodność rachunkowa z zamówionym tempem, a nie odsłuch — czy szew jest płynny muzycznie, oceni dopiero ucho.
- Nowe w narzędziu względem opisu pierwszej partii: przy wyborze miejsca mała kara za różnicę głośności po obu stronach szwu i mała premia za dłuższą pętlę; gdy utwór ma cichszy wstęp, pętla zaczyna się za nim (tak jest w `muzyka_15_trening`).
- Bezstratne kopie pętli (`muzyka/oryginaly/<nazwa>_petla.flac`) i oryginały leżą tylko lokalnie (folder poza gitem). Służą do budowy arkusza bez drugiego kodowania stratnego.

**Arkusz muzyki** (`arkusz/muzyka_arkusz_b.ogg` + mapa `arkusz/muzyka_arkusz_b.json`) — propozycja, nic nie jest wgrane:
- Pięć pętli tej partii jedna po drugiej w jednym pliku: walka, Strażnik, trening, Bagno B, Dżungla B; 1,5 s ciszy między utworami, 0,5 s na brzegach. Razem **395,4 s (6 min 35 s) i 8,37 MB** — limit Roblox to 7 minut i 20 MB.
- Po co: konto ma limit wgrań audio na miesiąc (10 bez weryfikacji tożsamości; rejestr `wgrane.json` ma dziś 8 wpisów z tego miesiąca). Jeden arkusz to jedno wgranie zamiast pięciu; gra odtwarza utwór jako odcinek pliku (`Sound.PlaybackRegion`), tak jak efekty walki.
- Mapa podaje dla każdego utworu dokładne granice (`poczatek`, `koniec`) i odcinek do grania (`graj_od`, `graj_do`) zwężony o 0,05 s z każdej strony — na wypadek przesunięcia czasów po przekodowaniu w Roblox. Tego przesunięcia nikt jeszcze nie zmierzył; po wgraniu warto odsłuchać początek i koniec każdego utworu w grze.
- Budowa i kontrola (kontrola sprawdza długość, rozmiar, ciszę między utworami i zgodność odcinków z plikami pętli):

```
python -B tools/audio_arkusz_muzyki.py --nazwa muzyka_arkusz_b muzyka_13_walka_petla muzyka_14_walka_straznik_petla muzyka_15_trening_petla muzyka_06_bagno_b_petla muzyka_07_dzungla_b_petla
python -B tools/audio_arkusz_muzyki.py --nazwa muzyka_arkusz_b --sprawdz
```

- Po odrzuceniu utworu: to samo polecenie bez niego, potem `python -B swiat/dzwiek_gra/zbuduj.py --sucho` (katalog gry bierze odcinki z mapy). Utwór usunięty z arkusza trzeba też zdjąć z `swiat/dzwiek_gra/ustawienia.json`.

**Kredyty drugiej partii:** 5 × 13,08 = **65,40**. Saldo konta: 205,01 przed, **139,61 po**.

**Czego nie da się sprawdzić bez ucha** — to samo co w pierwszej partii (lista niżej), a dodatkowo: czy muzyka walki nie męczy przy wielu walkach z rzędu, czy utwór Strażnika nie jest za groźny dla młodszych graczy i czy cichszy wstęp treningu w pełnej wersji to wada, czy zamierzone wejście.

## Efekty dźwiękowe (22 efekty, po dwa warianty)

- **A = Seed Audio 1.0** (`seed_audio`, domyślny model audio w Higgsfield, WAV 48 kHz stereo). Daje jedno zdarzenie z naturalnym wybrzmieniem, więc jest wariantem głównym.
- **B = Mirelo Text to Audio** (`mirelo_text_to_audio`, 44,1 kHz mono). Kosztował razem ok. 10 kredytów. Wypełnia całą zamówioną długość, w 16 z 22 plików dźwięk trwa do samego końca, czyli jest pewnie ucięty (dodałem wtedy 120 ms wyciszenia), a przy ciosie dał dwa uderzenia zamiast jednego. Przesłuchaj go tylko wtedy, gdy A się nie sprawdzi.

Pliki: `dzwieki/<nazwa>.wav` (A) i `dzwieki/<nazwa>_b.wav` (B). Cisza na początku i końcu jest przycięta, a głośność wyrównana. Długość podana po przycięciu.

| Efekt | A | B | Czego się spodziewać | Uwagi |
|---|---|---|---|---|
| `sfx_cios_trafiony` | 2,3 s | 2,0 s | świst i mocne „łup” | A zaczyna się prawie sekundowym, narastającym świstem; B ma dwa uderzenia |
| `sfx_cios_krytyczny` | 2,7 s | 1,9 s | mocniejsze uderzenie z metalicznym błyskiem | oba dłuższe niż zamówione 1,6 s |
| `sfx_blok_tarcza` | 2,5 s | 1,5 s | brzęk miecza o tarczę | A dłuższy od zamówionego (1,2 s) |
| `sfx_unik` | 0,7 s | 1,1 s | szybki świst | — |
| `sfx_umiejetnosc_rzut` | 1,3 s | 1,3 s | narastający magiczny rozbłysk | A kończy się dość nagle |
| `sfx_kula_ognia` | 3,0 s | 2,1 s | wystrzał płomienia i miękki wybuch | — |
| `sfx_lodowy_pocisk` | 1,3 s | 1,8 s | lodowy świst i szklany trzask | — |
| `sfx_trucizna_tik` | 1,0 s | 0,7 s | krótki bulgot | — |
| `sfx_podpalenie_tik` | 0,9 s | 1,1 s | krótki syk ognia | — |
| `sfx_ogluszenie` | 0,9 s | 2,1 s | dzwoneczki „gwiazdek” nad głową | A krótszy od zamówionego (1,8 s) |
| `sfx_tarcza_magiczna` | 2,6 s | 1,8 s | narastający szum i dźwięk bańki | oba kończą się dość nagle |
| `sfx_fanfara_zwyciestwa` | 3,1 s | 3,1 s | radosna fanfara: blacha i dzwonki | B cichszy po wyrównaniu (szczyty) |
| `sfx_porazka` | 3,4 s | 2,9 s | łagodny, zabawny dżingiel w dół | A powtórzony z innym opisem, bo pierwszą próbę usługa odrzuciła |
| `sfx_awans_poziom` | 2,4 s | 2,3 s | wznoszące się arpeggio z dzwonkiem | B ucięty na końcu |
| `sfx_monety` | 1,7 s | 0,9 s | brzęk kilku monet | B wyraźnie cichszy (szczyty) |
| `sfx_klik_przycisk` | 0,24 s | 1,0 s | krótkie drewniane „pyk” | A ma właściwą długość, B jest za długi |
| `sfx_przejscie_chmury` | 3,2 s | 3,3 s | długi, miękki świst | — |
| `sfx_ryk_kolos` | 3,5 s | 2,8 s | niski ryk z kamiennym chrzęstem | sprawdzić, czy nie straszy za bardzo |
| `sfx_galareta_plusk` | 0,4 s | 1,1 s | mokre, sprężyste „plask” | B bardzo cichy (-30 LUFS) |
| `sfx_wilk_warkniecie` | 2,1 s | 1,5 s | krótkie warknięcie | — |
| `sfx_troll_chrzakniecie` | 1,7 s | 1,2 s | niskie, głupkowate chrząknięcie | sprawdzić, czy nie brzmi jak słowo |
| `sfx_zarodniki` | 1,2 s | 1,8 s | puf i rozsypany pył | — |

## Kredyty

- Limit paczki: 280. **Wydano 229,49** (muzyka 14 × 13,08 = 183,12; efekty A: 36,20; efekty B: 10,17). Saldo konta: 434,5 przed, **205,01 po**.
- Z budżetu nic nie odpadło: zrobiłem 12 utworów po 90 s, drugie wersje menu i lasu oraz wszystkie 22 efekty.
- Jedno zlecenie (`sfx_porazka`, wariant A) usługa odrzuciła jako „nsfw” mimo niewinnego opisu. Nie pobrała za nie kredytów. Ponowiłem je raz, z innym opisem.

## Kontrola techniczna (szczegóły w manifeście)

- **Muzyka:** oryginały to MP3 128 kb/s, 44,1 kHz, stereo, każdy ma 90,0 s (bagno 89,97 s). Głośność oryginałów wynosiła od -17,3 do -13,0 LUFS. Teraz wszystkie mają -16,0 LUFS (menu A -16,5, bo nie pozwolił szczyt), a true peak jest najwyżej -1,2 dBTP. Cisza na początku jest pomijalna (≤ 0,03 s). Sześć utworów urywa się w pełnym graniu, osiem ma zakończenie, a sześć z tych ośmiu kończy się ciszą od 0,2 do 1,2 s. W obu przypadkach do gry trzeba brać wersję `_petla`.
- **Pętle:** miejsce cięcia wybrał automat. Porównał rytm, harmonię i barwę okien przy początku z oknami w ostatnich ok. 16 s i dla każdego utworu wybrał najlepiej pasujące miejsce. Na szwie jest 1 s przenikania. Szew jest ciągły (skok próbki ≤ 0,015). Różnica głośności między pierwszymi a ostatnimi 2 s pętli wynosi ≤ 3,1 dB, z wyjątkiem lodowca (6,8 dB). Wynik dopasowania (0,79–0,96) to miara techniczna, a nie ocena muzyczna.
- **Efekty:** wszystkie mieszczą się w wymaganiach Roblox (≤ 48 kHz, mono lub stereo, małe pliki). Głośność: maksymalna głośność chwilowa wynosi -14 LUFS, a szczyt najwyżej -1 dBFS. Część plików nie osiągnęła -14 LUFS, bo wcześniej trafiła w limit szczytu, i w grze zabrzmi ciszej: najbardziej `galareta_plusk_b`, `monety_b`, `klik_przycisk_b`, `wilk_warkniecie_b`. Głośność można potem ustawić polem `Volume` dźwięku. Seed często daje dźwięk dłuższy, niż zamówiono. Przycinałem tylko ciszę, nie treść.

## Czego nie da się sprawdzić bez ucha

- Czy melodie są ładne i „do nucenia”, czy nie męczą po 20 minutach i czy wszystkie brzmią jak jedna ścieżka.
- Czy nie ma wokalu ani chóru. Przełącznik „tylko instrumenty” był włączony, ale nikt tego nie słyszał.
- Czy instrumenty i nastrój zgadzają się z opisem (np. czy wieczór jest walcem, a bagno nie straszy).
- **Czy pętle są płynne muzycznie** (rytm, takt, harmonia na szwie). Pomiar mówi tylko, że nie ma trzasku ani skoku głośności.
- Czy efekty brzmią tak, jak opisano, i czy w efektach Seed nie ma czegoś podobnego do mowy (troll, kolos, wilk).
- Czy coś nie przypomina istniejącego utworu.

## Nowa muzyka miasteczka (26.11.2026)
Karol 25.11: dotychczasowa muzyka miasteczka jest „dosyć słaba”. Trzy próbki po 60 s z Higgsfield (ElevenLabs Music v2.5, razem 26 kredytów) poszły do odsłuchu; 26.11 Karol wybrał: **A najlepsza, potem B** (C odpada).
- `muzyka/muzyka_16_bazar_targ_kotow` (A) i `muzyka/muzyka_17_bazar_psotny` (B): pełne wersje MP3 i pętle OGG (52,4 s i 52,8 s) z `tools/audio_petla.py`; wpisy w `manifest_audio.json`.
- Arkusz `arkusz/muzyka_arkusz_c.ogg` + mapa `.json`: obie pętle w jednym pliku (1 min 47 s, 2,27 MB) — jedno wgranie zamiast dwóch.
- **Wgrane 26.11.2026** za zgodą Karola (przez Studio, z zatwierdzonego folderu): zasób 106850257173626, moderacja w toku; to 9. wgranie audio w listopadzie (limit 10). Zgoda w `zgoda_wgrania.json`, wynik w `wgrane.json`.
- W grze (`swiat/dzwiek_gra/ustawienia.json`, strefa `bazar`): A i B to utwory miasteczka, trzy dotychczasowe zostają jako zastępcze — grają, dopóki nowy plik się nie wczyta (prawa gry do zasobu w Creator Hub nadaje człowiek, moderacja).
- To próbki 60-sekundowe: pętla jest krótsza niż w pierwszej partii (ok. 80 s). Dłuższe wersje wymagają nowego generowania.

## Zanim wgramy do Roblox

**Zasady Roblox dla wgrywanego audio** (stan na 16.11.2026):
- Formaty: `.mp3`, `.ogg`, `.wav`, `.flac`, jedna ścieżka. Plik musi mieć mniej niż 20 MB i najwyżej 7 minut, częstotliwość ≤ 48 kHz, kanały mono lub stereo (także 3.0 i 5.1). Nasze pliki to spełniają.
- Limity: 2000 darmowych plików audio na 30 dni dla konta ze zweryfikowanym dowodem, 100 bez weryfikacji. Wgrywanie jest darmowe, a strona nie podaje żadnej opłaty. Wgrać można przez Asset Manager, Creator Dashboard albo Open Cloud.
- Wymagania: trzeba mieć prawa do nagrania, a plik musi spełniać Community Rules i Terms of Use. Plik jest transkodowany i może zostać odrzucony przy imporcie.
- Moderacja i dostęp: audio jest najpierw prywatne. Po moderacji może go używać właściciel, a inne osoby i gry tylko po nadaniu uprawnień. **Uprawnienia dla gry nie da się cofnąć.** Jeśli gra należy do grupy, pewnie najprościej będzie wgrywać od razu jako grupa (strona nie opisuje tego wprost dla audio).
- Utwory muzyczne mogą być pokazane na stronie gry. Wymaga to zweryfikowanego konta, akceptacji Audio Terms of Use oraz przejścia moderacji i sprawdzenia praw autorskich. Efekty nie są pokazywane na stronie gry, ale mogą trafić do Creator Store.
- Treści z AI: według dokumentacji Roblox odpowiadamy za treść, którą dostarczamy graczom, nawet jeśli wygenerowało ją AI. Musi ona spełniać Community Standards i pasować do oceny wiekowej gry. Ta sama strona każe pokazywać graczom informację o elementach generatywnego AI w grze, ale jej przykłady dotyczą rozmów z AI. **Nie ustaliłem pewnie**, czy obowiązek obejmuje gotową muzykę z AI. Oficjalnego tekstu Terms of Use nie udało się pobrać (strona zwróciła błąd 403).

**Prawa do muzyki i efektów z Higgsfield** (plan konta: `starter`, płatny):
- Warunki Higgsfield (ostatnia zmiana 23.10.2026): pkt 4.4 mówi, że Higgsfield nie rości sobie praw do wyników i nie ogranicza ich użycia komercyjnego. Centrum pomocy dodaje, że prawo to nie zależy od planu, płatne plany nie mają znaku wodnego, a wyniki nie są gwarantowanie wyłączne. Ochronę prawną przy roszczeniach osób trzecich daje tylko plan Enterprise. Nie wolno przedstawiać wyniku jako dzieła człowieka (pkt 5.2(xi)) ani używać go do trenowania modeli (pkt 5.2(iv)).
- Pkt 8: część modeli dostarczają inne firmy. Obowiązują zasady dopuszczalnego użycia tych firm, a gdy są ostrzejsze, mają pierwszeństwo.
- Warunki ElevenLabs dla modelu muzycznego (ostatnia zmiana 09.10.2026) pozwalają na plany samoobsługowe ElevenLabs używać muzyki komercyjnie, **z wyjątkiem filmu, TV, radia i „Studio Games”**. „Studio Game” to publicznie dostępna, zarabiająca gra, która nie jest „Indie Game”. Indie Game to gra, która od premiery zarobiła mniej niż 500 tys. USD, wydana przez twórcę z przychodem z gier poniżej 1 mln USD w ostatnim roku obrotowym. Po przekroczeniu progów jest 60 dni na zmianę licencji albo usunięcie muzyki. **Nie ustaliłem pewnie**, czy te warunki wiążą kogoś, kto generuje przez Higgsfield: ElevenLabs pisze je dla własnych klientów, a Higgsfield odsyła tylko do „zasad dopuszczalnego użycia”. Jeśli wiążą, to nasza gra w obecnej skali mieści się w Indie Game. Najpewniej będzie zapytać na piśmie pomoc Higgsfield, zanim muzyka trafi do publicznej gry.
- Seed Audio (efekty A) i Mirelo (efekty B): nie znalazłem warunków tych dostawców, które dotyczyłyby wyników przez Higgsfield. Obowiązują warunki Higgsfield jak wyżej.

Źródła:
- https://create.roblox.com/docs/audio/assets
- https://create.roblox.com/docs/projects/assets/privacy
- https://create.roblox.com/docs/generative-AI
- https://higgsfield.ai/terms
- https://higgsfield.ai/creator-hub/help-center/account-and-privacy/who-owns-my-generations-and-can-i-use-them-commercially
- https://elevenlabs.io/eleven-music-model-specific-terms

To streszczenie ze stron, a nie porada prawna.
