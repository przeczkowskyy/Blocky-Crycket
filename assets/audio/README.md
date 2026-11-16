# Muzyka i dźwięki — pierwsza partia (do odsłuchu)

Wygenerowane 16.11.2026 w Higgsfield (zgoda Karola z 16.11.2026). **Status wszystkich plików: do odsłuchu** — nic nie jest wybrane ani wgrane do Roblox.
Same pliki audio są tylko na komputerze, na którym powstały (`.gitignore` je pomija do czasu wyboru i sprawdzenia praw). W repo są tylko ten opis i `manifest_audio.json` (prompty, identyfikatory zleceń, koszty, pomiary).

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
