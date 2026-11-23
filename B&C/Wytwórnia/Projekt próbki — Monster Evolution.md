---
status: propozycja
tags: [wytwórnia, projekt, próbka]
źródło: "projekt agenta z 2026-11-22 po walidacji kierunku; budowa zlecona przez Karola (D-129)"
---
# Projekt próbki — Monster Evolution

> [!info] W skrócie
> Najmniejsza pełna pętla gry o ewolucji potwora: jesz, rośniesz po drabinie ośmiu form do Olbrzyma, zdobyte formy zarabiają w legowisku, złoto ulepsza bohatera. Budowa w czterech etapach, progi dla prawdziwych graczy zapisane przed próbą, warunek z rynku na 29.11. Kod: `swiat/ewolucja/`, kontener w Studio `EwolucjaGra`.

Stan na 22.11.2026. Wszystkie liczby to wartości startowe do strojenia, nie wyniki pomiarów.

## Jedno zdanie
Zaczynasz jako najmniejszy potwór, jesz i rośniesz po czytelnej drabinie ośmiu form aż do Olbrzyma, a każda zdobyta forma zostaje w twoim legowisku i zarabia złoto.

## Skąd ten kształt (dowody z walidacji)
| Decyzja projektu | Dowód |
|---|---|
| Stała, czytelna drabina form, a nie losowanie formy | filmy niesie „ostatnia forma” i „od słabego do najsilniejszego” (931 tys. wyświetleń); gra z całą ewolucją losowaną ma 0 graczy |
| Legowisko: zdobyte formy zarabiają | gatunkowi brakuje powodu powrotu (hity gasną w tygodnie, lider ma 3 ulubione na 1000 wizyt); tego elementu nikt tu nie sprawdził — to nasz wyróżnik i największa niewiadoma |
| Łagodna strata i ochrona najmniejszych | bycie zjadanym odstrasza nowych graczy (kilka gier poleca prywatne serwery, lider sprzedaje „nie tracisz mocy”) |
| Następna forma jako ciemna sylwetka, szczyt drabiny jako wielki cień | ciekawość „w co się zmienię” bez odbierania czytelnego celu |
| Odmiana barwna jako dodatek przy ewolucji (później) | losowanie jako premia działa u lidera; jako rdzeń nie działa |

## Pętla (pełna, w najmniejszej postaci)
1. **Jesz:** kulki małe (+1) i duże (+5) oraz mniejsze stworki sterowane przez grę (boty). Pasek wzrostu się zapełnia.
2. **Ewoluujesz:** przycisk „Evolve” → odsłona 3–4 s (kokon, kamera odjeżdża tym dalej, im większa forma, tabliczka z nazwą) → nowa forma z własną umiejętnością.
3. **Legowisko:** każda forma zdobyta choć raz zostaje w legowisku jako trofeum i daje złoto na sekundę. W etapie 1 legowisko to panel na ekranie.
4. **Ulepszasz bohatera za złoto:** Szczęka (zasięg i tempo gryzienia), Szybkość, Apetyt (mnożnik wzrostu). To zostaje na zawsze.
5. **Ryzyko:** większy może cię zjeść. Tracisz jedną formę, ale legowisko, złoto i ulepszenia zostają.
6. **Cel:** szczyt drabiny — Olbrzym. Kto nim zostanie, dostaje koronę i ogłoszenie na serwerze.

## Sterowanie (telefon najpierw)
Ruch gałką, przycisk Gryź, przycisk Zryw (krótki sprint z odnowieniem), przycisk Evolve pojawia się po zapełnieniu paska. Umiejętność formy pod jednym przyciskiem.

## Drabina (8 form)
- Osiem istniejących modeli potworów ułożonych od najmniejszego do największego; ostatnia forma jest wyraźnie ogromna.
- Panel drabiny z boku: zdobyte formy w kolorze, następna jako ciemna sylwetka, dalsze jako „?”, na szczycie wielki cień.
- Każda forma ma jedną umiejętność z gotowej puli.

## Zasady jedzenia
- Zjadasz kulki, boty i graczy co najmniej o jedną formę mniejszych.
- Formy 1 i 2 są chronione przed graczami (zagrażają im tylko boty).
- Zjedzony: spada o jedną formę (nigdy poniżej pierwszej), odradza się po 2 s z 5-sekundową tarczą.
- Boty: 20–30 stworków w formach 1–6, jedzą kulki, uciekają przed większymi, gonią mniejszych, nie stoją przy miejscu startu.

## Złoto i ulepszenia (startowo)
- Trofea w legowisku dają kolejno 1, 2, 4, 7, 12, 20, 35, 60 złota na sekundę.
- Szczęka, Szybkość (16 → 19 → 22) i Apetyt (×1,25, ×1,5) po trzy poziomy; pierwszy zakup możliwy ok. 1:30–2:00 gry.

## Tempo (cele do sprawdzenia symulacją i próbą)
| Zdarzenie | Kiedy |
|---|---|
| Pierwsza ewolucja z odsłoną | 20–30 s |
| Druga ewolucja | do 1:30 |
| Pierwsze ulepszenie | 1:30–2:00 |
| Pierwsze realne zagrożenie | ok. 2:00 |
| Forma 5 | 6–7 min |
| Olbrzym | ok. 15 min dla sprawnego gracza |

## Pierwsze 60 sekund
Start jako forma 1 obok kulek → strzałka do kulek → pasek pełny ok. 25. sekundy → Evolve z odsłoną → dymek „Legowisko: +1 złota/s” → sylwetka następnej formy na drabinie → większe kulki i pierwszy mały bot do zjedzenia.

## Etapy budowy
1. **Etap 1 (ten):** pole, jedzenie, boty, drabina 8 form z odsłoną i panelem, zasady jedzenia i straty, legowisko jako panel ze złotem, trzy ulepszenia, sterowanie na telefon, zapis miar w grze. Bez zapisu między sesjami.
2. **Etap 2 (zakres zmieniony 22.11 po etapie 1):** pierwsze dziesięć minut — wygląd pola i ruch stworów, odczucie jedzenia, nowa strefa i mały boss między formą 3 a 5, późniejsze pierwsze zagrożenie, krótki film demo ze skryptu.
3. **Etap 3:** legowisko jako miejsce w świecie ze stałym ujściem złota, złoto także pod nieobecność gracza, odmiany barwne przy ewolucji (jawne szanse, tylko waluta z gry), zapis postępu, Olbrzym jako boss serwera z nagrodą dla atakujących, wydarzenia z zegara, wersja do prywatnej publikacji.
4. **Etap 4:** próba z 8–12 graczami spoza zespołu.

## Czego w próbce nie robimy
Sklepu i płatności, odrodzeń, zwierzaków z jaj, handlu, gildii, drugiej mapy, rankingów poza koroną Olbrzyma, muzyki poza kilkoma dźwiękami.

## Miary sukcesu u prawdziwych graczy (zapisane przed próbą)
Próba: 8–12 osób spoza zespołu, 9–15 lat, telefon, bez instrukcji, przerwanie po 20 minutach.

| Decyzja | Próg |
|---|---|
| Budujemy dalej | mediana gry co najmniej 12 min z 20; co najmniej 70% dochodzi do formy 5; co najmniej połowa umie nazwać następny cel; co najmniej połowa prosi o więcej albo wraca w ciągu dwóch dni |
| Poprawiamy raz | mediana 7–12 min albo 40–70% dochodzi do formy 5 |
| Porzucamy | mediana poniżej 7 min albo mniej niż 40% dochodzi do formy 5 |

Gra zapisuje: czas sesji, czas dojścia do każdej formy, liczbę śmierci i to, czy gracz po śmierci grał dalej, kupione ulepszenia.

## Warunek z rynku
Jeśli do 29.11 średnia 7-dniowa lidera fali (Ant Evolution) zacznie spadać o ponad 30% tygodniowo, wstrzymujemy budowę przed etapem 3 i oceniamy ponownie.

## Uczciwa skala
Dobrze zrobiona druga generacja w tej fali ma zwykle szczyt 0,5–5 tys. graczy naraz; 10 tys. i więcej mniej więcej raz na dziesięć. Hity tego gatunku gasną w 4–8 tygodni, jeśli nie mają powodu powrotu — dlatego legowisko jest najważniejszą rzeczą do sprawdzenia.

## Po etapie 1 (2026-11-22)
- **Co stoi:** pole z 216 kulkami i 25 botami, drabina SLIME → ACORNLING → CROAKER → SHROOMLING → LEAF FOX → THORN WOLF → FOREST TROLL → GIANT (po jednej umiejętności), pasek wzrostu, ewolucja z odsłoną, panel drabiny, panel legowiska z trzema ulepszeniami, łagodna strata, miary gracza w pamięci. Kod `swiat/ewolucja/`, kontener `EwolucjaGra`; zrzuty w `swiat/ewolucja/klatki/`.
- **Tempo z symulacji:** forma 2 po 0:29, forma 3 po 1:14, pierwsze ulepszenie 1:34, forma 5 po 6:30, Olbrzym po ok. 14 min.
- **Słabe miejsca (ocena agenta budującego):** między formą 3 a 5 przez ok. pięć minut nie ma nic nowego; legowisko jest tylko panelem; po 18 minutach zostaje ok. 47 tys. złota bez celu; pierwszy bot goni już po 1:22; dotyk nie był sprawdzony na prawdziwym telefonie.
- **Największa luka wobec lidera:** żaden z naszych modeli nie ma szkieletu, więc wszystkie formy ruszają się proceduralnie (podskok, ściskanie, pochylenie, wypad przy gryzieniu), a pole jest proste. Karol po zagraniu w Ant Evolution wskazał właśnie grafikę, responsywność i animacje chodzenia jako jej mocne strony — dlatego etap 2 dostał ten zakres, a legowisko w świecie przeszło do etapu 3. Pytanie o prawdziwe animacje: pytanie 83.

## Po etapie 2 (2026-11-22)
- **Co doszło:** strefa Deep Woods za płotkiem (tablica z sylwetkami, otwiera się od formy 4), mały boss VINE SERPENT z paskiem życia i skrzynią 1500 złota, ładniejsze pole (stawy, kamienny krąg, grzyby, drzewa), wspólny system ruchu dla wszystkich stworów (skok, kłus, machanie ogonem, kurz), „+N” nad kulkami, błysk i wstrząs przy ewolucji, kamera dalej dla większych form, boty ignorują nowego gracza przez pierwsze 110 s, poziomy 4–5 ulepszeń, skrypt filmu demo.
- **Tempo z symulacji:** forma 2 po 0:20, forma 3 po 1:09, pierwsze ulepszenie 1:33, pierwszy pościg 1:59, forma 4 i las 2:49, boss spotkany 4:29 i pokonany 5:26, forma 5 po 6:47, Olbrzym po ok. 13:30. Najdłuższa przerwa bez nowości w pierwszych 10 minutach: 3:02 (cel 2:30 — niespełniony, luka między formą 6 a 7).
- **Ocena agenta budującego:** pierwsze minuty mają już ruch, ale po bossie gra wraca do czekania na pasek; legowisko nadal jest tylko panelem, a złoto znów się piętrzy po ok. 10 minutach. Etap 3 potrzebuje powtarzalnego celu w środku gry (kolejne stopnie bossa albo legowisko widoczne w świecie).
- **Prywatna publikacja:** Karol 22.11 („Tak puścimy”); wersja etapu 2 opublikowana na prywatnym miejscu testowym (https://www.roblox.com/games/93704244631419), potwierdzona zmianą znacznika czasu wersji. Dotyk na prawdziwym telefonie sprawdzi dopiero to granie.
- **Formy są w tabeli danych** (nazwa, model, skala, umiejętność, ustawienia ruchu, opcjonalne animacje); nowy model spoza Pet Areny wymaga drobnej zmiany w wyszukiwaniu modelu.

## Po etapie 3 (2026-11-22)
- **Legowisko w świecie:** 12 działek na brzegu łąki, gracz startuje we własnej. Na ośmiu postumentach stoją zdobyte formy, widoczne dla wszystkich; złoto z trofeów rośnie jako widoczna kupka i zbiera się je, wchodząc do środka. Własne legowisko to strefa bezpieczna. W grze nazywa się LAIR, a złoto w nim HOARD.
- **Ujście złota:** pięć poziomów każdego trofeum (kupowane tylko w legowisku), poziomy 4–5 ulepszeń.
- **Odmiany** losuje serwer przy każdej ewolucji: GOLD 8%, CRYSTAL 3%, RUBY 1%, RAINBOW 0,2% (szanse widoczne w panelu); kokon świeci kolorem odmiany przed odsłoną; trofeum odmiany mnoży dochód formy razy 2, 4, 8 albo 20. Nic nie da się kupić.
- **Zapis:** złoto, skarb, ulepszenia, zdobyte formy, odmiany, poziomy trofeów, stopień bossa; po wejściu gracz zaczyna od formy 1, reszta zostaje. Legowisko zarabia pod nieobecność do 2 godzin. Blokada sesji chroni przed nadpisaniem; w Studio i w próbach zawsze magazyn w pamięci.
- **Boss** wraca w pięciu stopniach (życie 220 → 980, skrzynia 1500 → 20 000), pierwszy raz na każdym stopniu daje trofeum bossa. **Olbrzym** od dwóch graczy staje się celem serwera.
- **Tempo z symulacji:** forma 2 po 0:20, forma 3 po 1:18, pierwsze ulepszenie 1:38, pierwszy pościg 1:52, forma 5 po ok. 5:30–6:00 (przy sześciu przebiegach 27 s szybciej niż okno 6–7 min), Olbrzym po ok. 13:15, najdłuższa przerwa bez nowości 2:27.
- **Znane wady:** z legowiska na brzegu do pierwszej kulki bywa ponad 10 s; odmiany widać tylko na własnym stworze i trofeach; tryb Olbrzyma-bossa sprawdzony tylko w testach bez Studio (w próbie jest jeden gracz).
- **Ocena agenta budującego:** minuty 5–15 są lepsze (co 1–2 minuty jest powód do działania), ale to głównie rosnące liczby; powroty do legowiska mogą nużyć, a odmiany przy łącznie 12% będą rzadkie w krótkiej sesji.
- **Opublikowany prywatnie** (https://www.roblox.com/games/93704244631419), potwierdzony zmianą znacznika czasu wersji.

## Po przeróbce na smoka (2026-11-22)
- **Osiem stadiów jednego smoka** z generatora klocków (bez wgrywania modeli): HATCHLING, WHELP, DRAKE, FIRE DRAKE, DRAGON, WAR DRAGON, ELDER DRAGON, ANCIENT DRAGON; od 31 do 60 części na stadium. Ruch w naszym systemie: nogi kłusują parami po przekątnej, ogon faluje, szczęka kłapie, skrzydła złożone i rozkładane przy zrywie i ślizgu.
- **Zdolności:** NIBBLE, TAIL WHIP, EMBER SPIT, WING GUST (odpycha), FIRE BREATH (stożek ognia), ROAR, WING GLIDE (krótki niski ślizg — jedyne „latanie”), INFERNO.
- **Odmiany** jako wygląd smoka (złoty, kryształowy, rubinowy, tęczowy), widoczne także u innych graczy. Sześć kulek stoi tuż przy wyjściu z każdego legowiska. Dzikie smoki zamiast dawnych botów; mały boss bez zmian; bossem serwera jest ANCIENT DRAGON. Napis na łące: „DRAGON LAIR EVOLUTION” (tytuł roboczy). Dawny zestaw ośmiu potworów wraca jednym ustawieniem (`"zestaw": "potwory"`).
- **Tempo z symulacji:** dwa cele wypadają za wcześnie (druga forma po 0:17 zamiast 0:20–0:30, piąta po 5:12 zamiast 6–7 min) — nie strojone celowo; reszta w normie, najdłuższa przerwa bez nowości 2:18.
- **Ocena wyglądu (agent budujący i agent prowadzący):** do próby wystarczy — stadia 4–8 czyta się jako smoki, a ostatnie robi wrażenie; na ikonę i reklamę nie wystarczy. Najsłabsze są dwa pierwsze stadia (wyglądają jak małe jaszczurki) i skrzydła, których z kamery od góry prawie nie widać. DRAKE i FIRE DRAKE różnią się głównie kolorem.
- **Czego potrzebuje ręcznie zrobiony model, żeby wejść bez przeróbek kodu:** model z częścią główną „Korzen” na poziomie ziemi pod środkiem ciała, zwrócony w stronę −Z; na każdej części atrybut `Grupa` (1 lewa przednia noga, 2 prawa przednia, 3 lewa tylna, 4 prawa tylna, 6 głowa, 7 szczęka, 8 lewe skrzydło, 9 prawe skrzydło, 11 i dalej segmenty ogona od nasady); atrybuty `Pivot<k>` z położeniem stawu każdej grupy przy skali 1. Potrzebna drobna zmiana: źródło modelu jako pole danych. Przebarwianie odmian nie zadziała na częściach z teksturą.
- **Opublikowana prywatnie** (https://www.roblox.com/games/93704244631419), potwierdzona zmianą znacznika czasu wersji.

## Pomiar do próby z graczami (2026-11-22)
- **Analityka Roblox** (tylko serwer opublikowanej gry; Studio pomija wywołania): lejek pierwszej minuty (wejście → pierwsza kulka → pierwsza ewolucja → pierwszy zbiór skarbu → pierwsze ulepszenie), lejek ośmiu stadiów, gospodarka złota (źródła i ujścia), zdarzenia: śmierć, pokonany stopień bossa, wylosowana odmiana. Dane w panelu twórcy do 24 godzin. **Ograniczenie z dokumentacji Roblox:** pełne wskaźniki panelu dostępne dopiero przy ponad 10 graczach dziennie i 10 godzinach gry przez 7 dni z rzędu — przy próbie z ok. dziesięcioma osobami pewnym źródłem jest nasz własny zapis.
- **Własny anonimowy zapis:** po każdej sesji serwer zapisuje jedno podsumowanie w osobnym magazynie (`Ewolucja_Proby_v1`, klucz: data i losowy identyfikator; bez identyfikatora i nazwy gracza): długość sesji, najwyższe stadium i czas dojścia do każdego, śmierci i czy gracz grał dalej po pierwszej, wizyty w legowisku, zbiory skarbu, ulepszenia, poziomy trofeów, stopień bossa, odmiany, pierwsza sesja czy powrót i ile dni od pierwszej gry. W Studio i w próbach — tylko magazyn w pamięci.
- **Odczyt:** `python -B swiat/ewolucja/testy/odczyt_prob.py` wypisuje tabelę z progami D-128 (sesje, mediana długości, odsetek dochodzących do stadium 3 i 5, gra po pierwszej śmierci, powroty innego dnia). Sprawdzony tylko na danych próbnych; odczyt z prawdziwej gry wymaga włączenia przez człowieka w Studio: Ustawienia gry → Bezpieczeństwo → „Enable Studio Access to API Services” (Studio pracuje wtedy na tych samych magazynach co gra; skrypt tylko czyta). Można włączyć na czas odczytu i wyłączyć.
- Testy logiki 25/25, próba w Studio 22/22 (w tym sprawdzenie, że podsumowanie trafia tylko do magazynu w pamięci). Opublikowane prywatnie razem z wersją ze smokiem.

## Droga do wydania 24–25.11 (D-137, D-138) — stan z nocy 22/23.11
Tytuł: „Dragon Lair Evolution”. Gra ma wyjść publicznie we wtorek–środę; kolejność prac: smoki z animacjami w grze → świat i oświetlenie → interfejs → powody powrotu (odrodzenie w nowej linii smoka, wydarzenie z zegara) → szlify i test z ludźmi → wydanie.
- **Modele smoka z Blendera** (`swiat/ewolucja/modele/`, biblioteka postaci z `swiat/postacie/biblioteka` tylko do odczytu): styl „Żarołuska” (klockowa bryła, pasy ciemnych łusek, żar w szczelinach rosnący z wiekiem, kryształowe rogi); osiem stadiów z jednego modułu, 26 stawów, 23 klipy animacji na stadium (chód, bieg, trzy ugryzienia, ogień, ogon, ryk, ślizg, uderzenie z nieba, koziołek, pożarcie, wyklucie, radość, poza na postument) ze znacznikami zdarzeń; nogi z kolanem i stopą sadzone na ziemi; wersje uproszczone po 35 części; jajo, owca, rycerz-golem w pięciu stopniach (także groźniejsza wersja), rekwizyty legowiska. Dane dla gry: rig z części Roblox i klipy odtwarzane kodem — bez wgrywania czegokolwiek; siatki do ewentualnego wgrania przygotowane. Nie sprawdzone jeszcze w Studio (wpięcie w toku).
- **Świat:** 42 elementy w tym samym stylu (łąka, las, legowisko, wyspa z lawą, woda, czaszka smoka, posąg Pradawnego, zapieczętowana brama, kule), propozycja mapy (ok. 3,8 tys. części) i oświetlenia (późne popołudnie, poświata dla żaru).
- **Strona gry i interfejs:** ikona i trzy miniatury z czarną sylwetką i znakiem zapytania; 24 ikony, portrety i sylwetki stadiów, wzory ekranu na telefon, panelu legowiska i ewolucji, przewodnik stylu. Podglądy: `swiat/ewolucja/modele/podglad/`.
- **Walka przebudowana** (w grze, na razie na starych smokach z klocków): życie i obrażenia dla wszystkich starć (równe stadia ok. 5 s, o dwa stadia większy zabija dwoma ugryzieniami), łańcuch trzech ugryzień z wybiciem, linie FIRE (splunięcie → zionięcie → pożoga) i POWER (ogon → ślizg → ryk → uderzenie z nieba) rosnące ze stadium, zapowiedź następnej zdolności w interfejsie, wyspa dostępna tylko ślizgiem, boty na tych samych zasadach, balans z symulacji (`swiat/ewolucja/testy/walka_sim.py`). Testy logiki 28/28. Znane słabości: zionięcie słabo widać z kamery od góry; o jedno stadium większy wygrywa 85% starć zamiast 75%; symulacja tempa nie zna jeszcze nowej walki.
- **Stan gry rano 23.11 (opublikowana prywatnie, wersja „odrodzenie1”):** smoki z Blendera z 25 klipami w grze (rigi z części, klipy odtwarzane kodem, wersje uproszczone dla dalekich smoków); świat z propozycji mapy (łąka, las, wyspa z lawą, stawy, czaszka, posąg, brama, dwanaście legowisk, przeszkody, owce, światło i niebo ustawiane w grze); interfejs według wzorów (żywe portrety, przyciski z odliczaniem i blokadą, panel legowiska, moment ewolucji, tabela ikon z zastępstwami — prawdziwe ikony po wgraniu); odrodzenie z liniami Ember, Frost, Storm, Shadow i mnożnikiem ×1,25 (do ×3), wydarzenia Dragon Rain co 20 min i Golem Rampage co 45 min, dzienne jajo. Tempo z symulacji: pierwsze odrodzenie ok. 19:30. Testy logiki 38/39 (1 pominięty), próba w Studio 48/48, telefon i tablet 8/8, czas klatki 16,7 ms. Filmy demo: wyklucie i walka, świat, interfejs, odrodzenie.
- **Znane wady przed wydaniem:** stopy pisklęcia ślizgają się (za krótki krok w danych klipu — poprawka w Blenderze); stadium 5 przychodzi po ok. 8:40 i najdłuższa przerwa bez nowości to 3:48; trofea na postumentach i boty zawsze w kolorach Ember; każda linia ma jedną paletę na osiem stadiów; zegary wydarzeń liczą od startu serwera; brak serii logowań i zadań dziennych, brak rankingu; nikt jeszcze nie grał na prawdziwym telefonie.
- **Do decyzji ludzi:** uwagi do wyglądu smoków (oczy pisklęcia, kolory stadiów, ikona); folder z ikonami interfejsu do zatwierdzonych folderów wgrywania w Studio (bez tego ikon nie da się wgrać); dźwięki smoka (jedno wgranie arkusza — osobna zgoda).
- **W budowie od 23.11 rano (krok „retencja1”, agent budujący, koniec ok. 11:45):** poprawka stóp pisklęcia w danych klipów, seria logowań (7 dni), trzy zadania dzienne, ranking (stadium i odrodzenia na serwerze, tablica najwięcej odrodzeń w świecie), kolory trofeów i botów według linii, tempo (stadium 5 do 7:00, przerwa bez nowości do 2:30), zegary wydarzeń według czasu UTC, wspólne dla wszystkich serwerów. Karol 23.11: „Gra wygląda nieźle, ale będziemy jeszcze musieli inwestować… pracuj dalej”.

### Strona gry — szkic (propozycja agenta, do akceptacji przed wydaniem)
- **Tytuł:** Dragon Lair Evolution (D-138).
- **Opis** (po angielsku, ok. 600 z 1000 znaków; wiersze z linkami lub prośbą o Robux odpadają):
  > 🐉 Hatch a tiny dragon and EVOLVE through 8 stages — from Hatchling to Ancient Dragon!
  > 🔥 Unlock new powers as you grow: Ember Spit, Fire Breath, Inferno, Tail Sweep, Wing Glide, Roar, Meteor Dive.
  > 🏰 Build your Lair — every trophy you win earns gold, even while you fight.
  > ✨ Rare dragon variants: Gold, Crystal, Ruby… and Rainbow (0.2%)!
  > 🔁 Rebirth into a new dragon line: Frost, Storm and Shadow.
  > ⛈️ Dragon Rain every 20 min · 🗿 Golem Rampage every 45 min — team up and smash him!
  > 🎁 Free daily egg, login rewards and daily quests.
  > 👍 Like and favorite to get the next update first!
- **Ustawienia:** gatunek Simulation; serwer na 12 graczy (dwanaście legowisk); urządzenia: telefon, tablet, komputer — konsola dopiero po próbie z padem; kwestionariusz dojrzałości: łagodna przemoc fantasy (gryzienie, ogień, bez krwi).
- **Grafiki:** ikona i trzy miniatury z `swiat/ewolucja/modele/podglad/` (13–16). Zostaną wgrane razem z ustawieniami strony, w ramach zgody na wgrywanie modeli smoka. Przełączenie gry na publiczną tylko po wyraźnym „wydajemy” Karola albo Pawła.
- Opis trzeba poprawić, jeśli zmienią się nazwy zdolności, szanse odmian albo zegary wydarzeń. Nazwy zgodne z `swiat/ewolucja/ustawienia.json` na 23.11.

## Propozycja: jedno zwierzę zamiast ośmiu różnych potworów (2026-11-22)
Karol zapytał, czy nie zrobić jednego zwierzęcia. Agent się zgadza: rosnące gry tej fali mają jednego rozpoznawalnego stwora w tytule, ogólne tytuły nie żyją, filmy niesie jedna historia („od słabego do króla”), a jedno zwierzę to jeden szkielet i jeden chód na osiem form. Wybór z liczb: [[Wybór zwierzęcia do gry o ewolucji (2026-11-22)]] — agent proponuje małpę (małpka → goryl → olbrzymi goryl), bo dwunożną postać da się najpewniej oprzeć na standardowym szkielecie postaci Roblox z gotowym chodem, co zamyka największą lukę wobec lidera bez pracy w Blenderze. Do sprawdzenia przez budującego na początku przeróbki. Kod etapu 1 ma formy w tabeli danych, więc zmiana nie rusza pętli. Decyzja: pytanie 84.

### Próba techniczna (2026-11-22)
- **Działa:** jedna dwunożna małpa z klocków na standardowym szkielecie postaci Roblox odtwarza gotowy chód, bieg i postój — jako gracz i jako boty — w skali od 0,5 do 6 razy, bez szkieletu z Blendera. Trzy przykładowe stadia z jednego modelu: wielkość, kolor futra i doczepiane dodatki (łuk brwiowy, srebrny grzbiet, płyty, korona). 25 botów i gracz: 16,7 ms na klatkę w emulacji telefonu (na procesorze komputera, nie telefonu).
- **Ograniczenia:** gotowe animacje to wyprostowany ludzki chód, nie chód na knykciach (własne animacje wymagałyby wgrania, czyli zgody); przy ruchu standardowych postaci boty różnej wielkości piętrzą się i blokują; próbny model jest surowy — żeby wyglądał jak nasze potwory, potrzebne są części ciała w stylu klocków (16 elementów), ale już bez szkieletu i bez animacji.
- **Zalecenie agenta budującego:** zostawić nasz ruch i przewidywanie, a małpę pokazywać jako model po stronie klienta, którego animacje idą za naszym ruchem. Ten wariant nie był jeszcze sprawdzony wprost. Szacunek przeróbki: 150–200 tys. tokenów; pełne przejście na standardowe postacie 350–450 tys.
- Szczegóły w repozytorium: `swiat/ewolucja/PROBA_MALPY.md`, zrzuty `swiat/ewolucja/klatki/proba_malpy_*.jpg`.

## Stan implementacji
- [x] Etap 1 — pełna pętla w najmniejszej postaci (2026-11-22: testy logiki 12/12, próba w Studio 13/13 bez błędów konsoli, układ telefonu 6/6, tempo z symulacji zgodne z celami)
- [x] Etap 2 — pierwsze dziesięć minut (2026-11-22: testy logiki 15/15, próba w Studio 15/15 bez błędów konsoli, układ telefonu 6/6; jeden cel tempa niespełniony — najdłuższa przerwa bez nowości 3:02 wobec 2:30); wersja opublikowana prywatnie
- [x] Etap 3 — legowisko w świecie, skarb, poziomy trofeów, odmiany, zapis z zarobkiem pod nieobecność, boss w pięciu stopniach, Olbrzym jako boss serwera (2026-11-22: testy logiki 21/21, próba w Studio 21/21, układ telefonu 7/7; opublikowany prywatnie; wydarzenia z zegara odłożone)
- [x] Przeróbka na smoka — osiem stadiów jednego zwierzęcia, model z klocków (2026-11-22: testy logiki 23/23, próba w Studio 21/21, układ telefonu 7/7; opublikowana prywatnie; pytanie 84)
- [ ] Etap 4 — próba z 8–12 graczami

## Powiązane
- [[Monster Evolution]] · [[Walidacja kierunku jesteś potworem (2026-11-22)]] · [[Kierunki z rynku 2026-11-22]] · [[00 Wytwórnia pomysłów]] · [[Lekcje z prototypów]] · [[Karta oceny pomysłu]]
