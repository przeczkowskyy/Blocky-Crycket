---
status: propozycja
tags: [produkcja, sesja, game-design]
źródło: "sesja główna Karola i Pawła 2026-11-16, 20:05–20:53 (ok. 48 min), zakładka Sesja panelu; zapis rozmowy lokalnie u gospodarza (transkrypcja automatyczna)"
---
# Sesja główna 2026-11-16 — zapis ustaleń

> [!info] Co to jest
> Zapis rozmowy Karola i Pawła z 16.11 (20:05–20:53). To **materiał źródłowy, nie kanon**: nic z tej notatki nie obowiązuje, dopóki nie trafi do [[Rejestr decyzji]] jako ✅ z podpisami. Propozycje z tej sesji mają numery **D-073–D-093**. Zatwierdza je Karol albo Paweł w panelu (zakładka Pytania), a druga osoba potwierdza (D-043). Zapis jest **pełny**: spisały się wszystkie odcinki nagrania. Każda osoba nagrywała własny mikrofon, więc wiadomo, kto mówi. Transkrypcja jest automatyczna i miejscami niewyraźna (zwłaszcza szybkie wypowiedzi Pawła), więc liczby i nazwy traktuj ostrożnie. Znaczniki `[20:05]` to godzina z zapisu. Pełny zapis rozmowy leży lokalnie u gospodarza i nie trafia do repozytorium.
>
> **Co już się stało w panelu w trakcie sesji:** Karol oznaczył jako nieaktualne pytania 5, 27, 39 i 45, decyzję D-064 i raport „Silnik walki v2 — wyniki i wybory” (20:48), bo odpowiedzi padły w rozmowie. Ich treść jest niżej i w nowych propozycjach. Karol zatwierdził D-061, D-062, D-063, D-067 i D-072, a Paweł potwierdził przez Telegram D-062, D-063, D-067, D-072 i odrzucenie D-066. **D-061 (osiem biomów) czeka na podpis Pawła**: na sesji powiedział „tak, tak” (20:52), ale w rejestrze jest tylko podpis Karola.

Karol prowadził po agendzie z [[Sesje główne]] (Pancerz, przegląd decyzji, mapa i HUD, sklep za Robuxy). Potem opowiedział o nowych ustaleniach z ostatnich dni (nowa mapa, podział pracy, rasy), przeszedł po pytaniach z panelu (45, 39, 27, 5), czytał na głos raport o pięciu wyborach silnika walki v2 i na koniec zapytał o otwarte decyzje (D-064, D-063, D-061).

## 1. Blok, unik i Pancerz (D-062, D-063, pytania 39 i 40) [20:05–20:08, 20:48] → D-073, D-074
- Karol [20:05–20:06]: żeby Wojownik z tarczą i unikiem nie był nie do zabicia, blok i unik ma **każda klasa**, także Mag i Zwiadowca, tylko z mniejszą szansą. Tarcza daje Wojownikowi większą szansę na blok. „Nie musimy kopiować S&F.”
- Paweł [20:06]: nie dawałby bloku wszystkim, a Mag w ogóle bez uniku; w S&F szansa innych klas jest „malutka”. Rzucił też, że tarcza mogłaby zatrzymywać cały cios, a Zwiadowca np. tylko połowę [20:06:52] (niewyraźne, bez odpowiedzi).
- Paweł [20:07]: Wojownik nie powinien blokować czaru Maga („bez sensu blokować fireballa”). Karol: czemu nie, nawet uniknąć się da przy dobrym losowaniu. Paweł: „może faktycznie nie musimy”, czyli zgoda.
- Pancerz w Training Center [20:07–20:08]: Karol: „dopuszczamy mini-grę na Pancerz”, każda statystyka ma swoją mini-grę. Paweł: „ja dopuszczam”. Przy pytaniu 39 [20:48] Paweł dodał: „dalej nie rozumiem… możemy dopuścić; jak zobaczymy, jak działa, zastanowimy się, czy ma być”. Karol oznaczył pytanie 39 jako nieaktualne.
- Prośba Karola do agenta [20:08]: zbalansować trening tak, żeby nie dało się nadużywać jednej mini-gry.
- Uwaga protokolanta: zatwierdzona z dwoma podpisami D-062 mówi: „blok to cecha tarczy… slot tarczy ma tylko Wojownik”. Blok dla każdej klasy to zmiana tego punktu (D-073). Pytanie 40 ma już odpowiedź Karola („zostawiam to Claude'owi”), a D-073 jest częścią rozwiązania.

## 2. Przegląd decyzji Karola przez Pawła (pytanie 27) [20:08, 20:48]
- Karol [20:08]: temat odhaczony, przegląd idzie przez Telegram, który już działa. Przy pytaniu 27 [20:48]: „Ja i Ty mamy takie same prawa… nieaktualne”. Pytanie zamknięte w panelu, Paweł nie zaprzeczył.

## 3. Nowa mapa i teleport (pytania 5 i 28, D-064) [20:08–20:10, 20:13–20:17, 20:49–20:50] → D-075, D-076, D-077, D-092
### Teleport
- Paweł [20:08–20:09]: skoro mapa ma być ciągłą linią z podziałem na strefy, teleport przenosi między strefami: klikasz strzałkę w górę i przechodzisz do następnej. Po teleporcie kamera opada z góry na gracza.
- Karol [20:09–20:10]: miasto główne to pierwszy blok, strzałka w górę prowadzi do pierwszej lokacji (las), potem do kolejnych biomów (dał przykład pustyni). [20:49–20:50]: „ma to być troszkę z lotu ptaka”, z cutscenkami przy pierwszym wejściu do biomu. D-064 (widok miasta z pinami) Karol oznaczył jako nieaktualną, bo „to już lepiej sobie opowiedzieliśmy”.
- Karol [20:16–20:17]: dziś stoi mały, zastępczy teleport. Przycisk Teleport w HUD ma otwierać właśnie tę mapę stref. „To jest bardzo ważna decyzja.”
### Kształt mapy
- Karol [20:13–20:14]: „robimy w 100% przebudowę logiki mapy i teleportu”. Mapa to prostokąt: bardzo wąski (4–5 sekund biegu postaci) i bardzo długi, przez wszystkie biomy.
- Karol [20:09]: biomy nie mogą być wielkie, bo samo chodzenie nudzi gracza. „Maksymalizujemy dopaminę.”
### Układ biomu
- Karol [20:13–20:14]: z Krzywego Miasteczka teleport do biomu leśnego. Przy teleporcie stoi jajko do kupowania (inkubator). Za nim pierwszy mini-biom, np. zagroda ze slime'ami poziomów 1–3. W kolejnej przegrodzie lasek muchomorkowy z trochę silniejszymi potworami, potem wilki, a na końcu troll albo golem jako strażnik. Jego pokonanie odblokowuje następny biom. Na potworach można farmić cały czas.
- Tempo [20:14–20:15]: statystyki i poziomy liczone tak, żeby na biom (np. leśny) gracz poświęcał średnio ok. **15 minut**. Ma myśleć, jakie statystyki rozwijać, trenować w Training Center, używać jajek i petów, budować buildy i wybierać drogę klasy. Gra „nie może być dziecinnie prosta”, ma się dać przegrać.
- Potwory też mają klasy [20:38–20:39]: slime to Zwiadowca, muchomorek Mag, golem Wojownik. Biom może wymagać konkretnego buildu, np. biom magów nie do przejścia bez odporności na magię. Karol [20:46]: biomy pod różne buildy, np. przeciwnicy z potężnymi autoatakami wymagają inwestycji w unik albo Pancerz. Paweł: mechanika adaptacji do przeciwników.
### Cutscenka biomu
- Karol [20:15–20:16]: przy pierwszym wejściu do każdego biomu odpala się cutscenka. Kamera przelatuje przez cały biom od przodu i pokazuje mini-biomy i potwory, a na końcu strażnika biomu, który robi emotkę albo krzyczy.
- Karol [20:16]: „to jest jedno zadanie” i przebudową biomu zajmuje się on, bo budowa biomów i modeli w Blenderze zużywa dużo tokenów, a Paweł ma niższy plan.
### Przyciski HUD (pytanie 5)
- Paweł [20:49]: przyciski według Figmy. Kanon miał pięć z pierwszego projektu gry (gildie pod jednym przyciskiem albo bez teleportu, z Twierdzą jako tycoonem), a potem wyszło, że ma być więcej. Karol: „czyli na Figmę”. Pytanie 5 Karol oznaczył jako nieaktualne.
- Nie padło: gdzie trafiają Twierdza (Tycoon) i Arena. Lista lokacji z pytania 28 przy mapie stref wygląda inaczej: miasto plus biomy (D-075).

## 4. Sklep za Robuxy i waluty (D-066, pytania 43 i 44) [20:10–20:11] → D-086
- Karol: jajka kupuje się **wyłącznie za Złoto**. Za Robuxy można kupić bundle Złota, Diamentów albo Złotych Rybek. Za Rybki bundle, startery (np. podwójne statystyki, podwójna Siła na start), paczki zasobów i szybszy poziom.
- Paweł [20:10]: myślał, że waluta premium (Rybki) jest na game passy, „coś, co normalnie za Robuxy”. Karol: „Game Passów, ok… tutaj mamy też zgodę”.
- Uwaga protokolanta: zgodne z odrzuceniem D-066 („za Robuxy waluta oraz bundle oraz Pass startowe”) i z odpowiedzią Karola na pytanie 44. W rozmowie „walutą premium” nazwano Rybki, a D-031 i D-038 nazywają tak Diamenty (Gemy). Nazwy do uporządkowania (pytanie 6).

## 5. Podział pracy i przydział zadań (D-072) [20:12–20:13, 20:16, 20:24–20:25, 20:47–20:48] → D-093
- Karol [20:12]: każde nowe ustalenie o budowie od razu dostaje osobę: Karol albo Paweł. Jeśli agent nie wyłapie z zapisu rozmowy, czyj Claude ma to zrobić, musi zapytać (na Telegramie albo na Pulpicie). Potem zadanie przejmuje sesja Claude Code tej osoby. To rozwija zatwierdzoną D-072.
- Paweł [20:24–20:25]: jego Claude powiedział, że modele i duże sceny powinien robić Karol, bo zjadają dużo tokenów. Paweł może robić wszystko w 2D: przyciski, menu. Karol: „takie rzeczy mogą przejść na mnie… od razu zapisujemy to w decyzjach”.
- [20:47–20:48] Paweł: frontend 2D i skrypty do niego. Karol: zadania lżejsze dla tokenów może robić Paweł.

## 6. Rasy i scena wyboru postaci [20:16–20:19, 20:20–20:26, 20:32–20:33, 20:47] → D-079, D-080, D-081
### Rasy
- Karol [20:16–20:17]: sesja Pawła robi teraz logikę ras: oprócz klasy będzie rasa.
- Paweł [20:17–20:18]: po ekranie wyboru klasy gracz przechodzi do kolejnego ekranu z sześcioma przyciskami ras. Każda rasa ma pasywną cechę, np. demon ma większe premie do Życia i Siły, a mniejsze do Inteligencji, więc demon-Mag mniej się opłaca. Karol: to może być kompromis, ktoś zechce tak balansować.
- Paweł: w selektorze model 3D postaci w podstawowym stroju (przepaska albo koszulka i spodenki) zmienia się z rasą. Sześć ras: człowiek, demon, mroczny elf, elf, ork, goblin.
- Karol [20:18]: rasa premium, np. Półbóg, płatna za Robuxy, z lepszymi statystykami. Paweł: „no można, ale…” i „pay to win” [20:18:52]. **Nierozstrzygnięte.**
- Karol [20:24]: Paweł robi w Blenderze wszystkie rasy, niech zaprojektuje też Półboga. Minutę później (punkt 5) modele i duże sceny przeszły na Karola, więc kto robi modele ras, nie jest pewne (pytanie 49).
### Scena wyboru (podest)
- Paweł robi w 3D koło (podest) wyboru klasy i wypchnie je na GitHub [20:20, 20:23–20:24]. Karol: „elegancko to wygląda”. Paweł chce jeszcze poprawić, bo „za mało nasz styl”. Karol [20:10]: światło trzeba zoptymalizować.
- Karol [20:25]: podest robimy u Karola, a Paweł ma wypchnąć, co zrobił, żeby został wzór. Przewijanie klas zmienia tło: Wojownik ma zamek, Zwiadowca las, Mag kryształy, księgi albo bibliotekę.
- Paweł [20:32–20:33]: ma jeszcze jedno odnowienie limitu i spróbuje sam poprawić halę z tyłu. Jeśli wyjdzie niezadowalająco, przejmuje Karol. Karol: „ładuj, próbuj… decyzja jest podjęta”.
- Ścieżka gracza [20:20–20:21]: ekran ładowania → menu główne (z własną muzyką) → wybór postaci → gra.
- Paweł [20:47]: okna sklepów w 2D, a 3D tylko selektor bohatera. Karol: „tak, to już 2D okno”.

## 7. Walka: więcej „dopaminy”, dźwięk i muzyka [20:19–20:20] → D-082, D-083
- Karol, za uwagą Pawła: walki wyglądają dobrze, ale potrzebują więcej nagrody: wyskakujących efektów (pop-upów) i efektów dźwiękowych. Pop-upy może zaprojektować Claude Pawła w osobnej sesji, a dźwięki do nich robi sesja Karola w Higgsfield.
- Muzyka z Higgsfield: każdy biom ma własną, Krzywe Miasteczko 2–3 utwory w tle, menu główne własną. Karol bierze to na siebie jako osobne zadanie.

## 8. Krzywe Miasteczko i sklepy [20:21–20:23, 20:47] → D-084, D-085
- Sklepy [20:21]: do budynku się wchodzi, nie ma „podchodzisz do budynku, klikasz E i masz sklep”. Budynki są małe w środku, stoi tam sprzedawca (gruby barman, mag-sklepikarz) i dopiero E na nim otwiera sklep. Okno sklepu jest 2D, może je zaprojektować Paweł [20:47].
- Miasto do przebudowy [20:21–20:23]: bardzo ciasno, budynek za budynkiem: sklep zbrojeniowy, zaraz obok magiczny itd. Są tam też: portal do biomów (np. po lewej), drugi portal albo przejście na działkę gracza (kopalnie złota, kamienia) i miejsce na pety (chodzą za bohaterem, można je odstawić do zagrody, do tego okno w HUD). Do tego mała tablica ogłoszeń z rankingiem serwera (najwyższy poziom, największe zdolności), a w przyszłości w niej panel gildii (podgląd członków, zaproszenia). Sklepy nie muszą stać obok siebie, ale blisko, mogą być naprzeciw, jak na bazarze. Mini-gry do wyboru z jednego panelu w jednym miejscu.
- Cel: gracz nie skupia się na chodzeniu i ma wszystko pod ręką.

## 9. Drzewko: Timer i premia do Diamentów (pytanie 45) [20:23, 20:26–20:29] → D-087
- Karol [20:23]: Paweł kończy drzewko.
- Timer: Paweł dodał tę gałąź, „żeby coś było”, i można ją zmienić przy lepszym pomyśle. Karol: zgoda, gałąź Twierdzy przyspiesza też budowę i ulepszanie budynków.
- Premia do Diamentów w gałęzi gracza: Paweł pytał, czy nie mnoży się z kopalnią diamentów w Twierdzy. Karol najpierw chciał ją usunąć, potem ustalili: dochód z kopalni wzmacnia tylko gałąź Twierdzy, a procent z gałęzi gracza działa tylko na Diamenty z zabitych potworów (łup). Paweł: „ten income będzie tylko do upgrade'ów Twierdzy”.
- Karol oznaczył pytanie 45 jako nieaktualne. Zaraz potem w zapisie jest „nie” Pawła [20:29:03]; z zapisu nie wiadomo, do czego się odnosi.

## 10. Silnik walki v2: pięć wyborów (raport z 14.11) [20:29–20:48] → D-088, D-089, D-090, D-091
Karol czytał raport na głos punkt po punkcie. Po rozmowie oznaczył go w panelu jako nieaktualny [20:48].
### Umiejętności i sloty
- Paweł [20:30]: trzy sloty, a umiejętności aktywne albo pasywne. Przykład: raz na walkę „Kolos”, czyli +50% maks. HP i obrażeń na początku walki, albo +20% Pancerza. Karol zaproponował jedną aktywną i dwie pasywki. Paweł: bez sztywnego podziału, dowolność, np. trzy pasywki albo trzy aktywne. Karol: „zgadzam się”, a sloty odkrywa się w drzewku.
- Paweł [20:31]: czwarty slot za Robuxy? Karol: nie, „to już by było za pay-to-win”, zostają trzy.
- Wskrzeszenie (Paweł [20:31–20:32]): raz na walkę powrót ze 100% HP albo 50% szansy na powrót z HP malejącym przy każdym kolejnym (50%, 25%…; potem mówił o 25%). Karol: „przeopa”, najwyżej jako legendarne. **Nierozstrzygnięte.**
- Bronie [20:31, 20:33–20:34]: każda broń epicka i legendarna ma własną pasywkę, np. różdżka ognia przedłuża podpalenie o dwie tury.
### Mana
- Problem [20:34–20:35]: Karol nie chce losowej szansy na umiejętność, żeby losowanie się nie rozjechało. Paweł: Inteligencja jest w teorii bezużyteczna dla Wojownika i Zwiadowcy.
- Karol [20:35–20:36]: pasek many (energii), jak w LoL: rośnie, gdy atakujesz i gdy dostajesz obrażenia (proporcjonalnie). Pełny pasek odpala umiejętność. Do tego nowe węzły w drzewku i amulety albo pierścienie zmniejszające koszt many, więc build pod manę pozwala np. dwa razy użyć ulta w walce. Paweł: „można było tak zrobić”. Karol: „to jest bardzo ważne… zaimplementuj to”.
- Mana a Inteligencja [20:36–20:38]: Karol uważa, że Inteligencja nie może być naraz obrażeniami, maną i odpornością na magię, więc dodałby osobną statystykę many. Paweł: wtedy trzeba wszystko przebudować, a logiczne jest, że Mag z dużą Inteligencją ma dużo many. Karol [20:41–20:42]: zostaje przy manie „definitywnie”, ale agent ma to zoptymalizować tak, żeby korzystały wszystkie klasy. Paweł zapytał, czy będzie musiał dorabiać nowe okno, a Karol: agent ma to zrobić **bez nowego okna statystyk**.
- Buildy [20:40–20:41]: Mag pod manę (zbroja, pierścień), Wojownik i Zwiadowca pod autoataki. Paweł: Inteligencja Maga ma podnosić też jego autoataki, w mniejszym procencie, żeby bez czaru nie był bezużyteczny. Karol: zależy od buildu, np. różdżka z mocnymi autoatakami i karą do many (+50% potrzebnej puli).
- Zręczność u Wojownika [20:39–20:40]: Paweł: skoro Wojownik rzadko unika, Zręczność jest dla niego bezużyteczna. Karol: może mnożnik obrażeń krytycznych? Prośba obu do agenta: każdy punkt każdej statystyki ma się przydawać.
### Statusy i tarcza
- Karol [20:32–20:33]: agent ma zbalansować i stworzyć unikalny system statusów: otrucie, podpalenie, spowolnienie, zdarcie pancerza, tarcza, ogłuszenie. Dziś podpalenie działa tak samo jak trucizna (obrażenia co turę).
- Trucizna i podpalenie są nieblokowalne i nie zmniejsza ich też odporność na magię (Karol [20:43], na pytanie Pawła). Paweł: wtedy da się złożyć build na kumulowaniu trucizny. Runy na broń zmniejszające obrażenia od trucizny to sprawa na przyszłość (wzór: Arena Manager z S&F).
- Tarcza [20:44–20:45]: Karol pytał, czy rzucanie tarczy nie powinno kosztować tury. Paweł: tarcza to umiejętność do wyboru, trzyma się np. trzy tury i zmniejsza obrażenia o procent. Rzucenie kosztuje turę, jak każdy czar. Karol: „masz rację”.
### Pancerz
- Z raportu: Pancerz nigdy nie zeruje ciosu, co najmniej 25% przechodzi. Obaj za. Paweł: limit np. 75%, a Wojownik ma lepsze przeliczniki i dochodzi do niego szybciej niż Mag i Zwiadowca. Karol: liczby to sprawa agenta. Przedmioty bywają tylko dla jednej klasy, ale buildy mają być różne: pod manę, pod autoataki albo pod maksymalny unik Zwiadowcy.
### Reszta raportu
- Długość walki tylko ze statystyk i losowości: zgoda (D-068). Równość klas: „bardzo mi się podoba” (D-069).
- Wybór 1 (zwykły atak Maga bije Siłą): wprost nie padło, jest tylko uwaga Pawła o autoatakach z Inteligencji. Wybór 2 (umiejętności co kilka akcji) zastępuje pasek many. Wybór 3: czary da się uniknąć i zablokować (Paweł przyjął to już w temacie 1), a trucizna i podpalenie omijają obronę. Wybór 5 (sloty od poziomów 1, 5 i 10): padło tylko, że sloty odkrywa się w drzewku.

## 11. Training Center i pomijanie walk (D-063) [20:50–20:52] → D-078
- D-063 (jeden budynek, od pierwszego poziomu): obaj „tak”. Training Center daje tylko statystyki. Złoto, komponenty i Diamenty (na drzewko i budowę) zdobywa się, zabijając ręcznie potwory, które się odradzają.
- Paweł [20:51]: cutscenka walki bez pomijania tylko przy pierwszym podejściu do danego potwora, potem można ją pomijać, bo inaczej farmienie zmęczy. Karol: jak w grze z rzucaniem jedzenia: walkę z potworem, którego już spotkałeś, pomijasz, a z nowym nie, ale masz przyspieszenie ×1/×2/×4. Za drugim razem np. spacja pomija walkę. „Super, mamy to.”

## 12. Biomy (D-061) [20:52]
- Karol: osiem biomów w kolejności jak w D-061, „akceptujemy”. Paweł: „tak, tak, to na razie”, zobaczymy w grze i ewentualnie poprawimy. Karol poprosił Pawła o potwierdzenie na Telegramie.

## Propozycje do rejestru
| Nr | Temat | Zastępuje / dotyka |
|---|---|---|
| D-073 | Blok i unik ma każda klasa; tarcza daje Wojownikowi większą szansę na blok; czary też da się uniknąć | **D-062 (dwa podpisy)**: blok tylko z tarczy; pytania 40, 46 |
| D-074 | Pancerz z własną mini-grą w Training Center, na próbę | D-063, D-050, pytanie 39 |
| D-075 | Mapa jako wąski, długi pas biomów; Teleport w HUD przenosi między strefami | D-064 (nieaktualna), [[Mapa teleportacji]], teleport do lasu z 15.11 |
| D-076 | Biom: inkubator przy wejściu, zagrody coraz silniejszych potworów, strażnik otwiera następny; ok. 15 min na biom | D-061, D-059, D-060, [[Biom Las]] |
| D-077 | Cutscenka przelotu przez biom przy pierwszym wejściu | D-042 (cutscenka dungeonu) |
| D-078 | Walka z nowym typem potwora bez pomijania, z poznanym można pominąć | D-068, prototyp walki v2 |
| D-079 | Sześć ras z pasywną cechą, wybór rasy po klasie | [[Selektor bohatera]], D-069, D-071 |
| D-080 | Półbóg jako płatna rasa premium z lepszymi statystykami (sporne) | D-036, D-069; pytanie 47 |
| D-081 | Start gry: ładowanie → menu → podest z tłem klasy → gra; 3D tylko selektor | [[Selektor bohatera]], [[Ekran ładowania]] |
| D-082 | Walka: wyskakujące efekty i dźwięki | walka v2, odpowiedź na pytanie 25 |
| D-083 | Muzyka: każdy biom, miasto i menu główne | [[Pipeline assetów]] |
| D-084 | Sklepy z wnętrzem: E na sprzedawcy otwiera okno 2D | Krzywe Miasteczko |
| D-085 | Krzywe Miasteczko ciasne jak bazar: portale, działka, zagroda petów, tablica | D-041, D-049, D-052, D-067 |
| D-086 | Jajka tylko za Złoto; za Robuxy bundle walut; Rybki na game passy, bundle i startery | D-031, D-036, D-040, D-066, pytania 6 i 44 |
| D-087 | Drzewko: Timer zostaje; premia do Diamentów w gałęzi gracza tylko z łupu | D-056, D-057, pytanie 45 |
| D-088 | Trzy dowolne sloty umiejętności z drzewka, bez płatnego czwartego; pasywki broni | **D-055 (dwa podpisy)**: sloty na umiejętności aktywne; D-051 |
| D-089 | Pasek many odpala umiejętności; buildy pod manę; bez nowego okna statystyk | D-062, D-048, raport: wybór 2 |
| D-090 | Statusy działają każdy inaczej; trucizna i podpalenie nieblokowalne; tarcza jako czar | raport: wybór 3 |
| D-091 | Pancerz przepuszcza zawsze co najmniej 25%; Wojownik szybciej dochodzi do limitu | D-062, raport: wybór 4 |
| D-092 | Przyciski HUD według Figmy: sześć, z Teleportem | kanon [[HUD]], pytanie 5 |
| D-093 | Podział pracy: Paweł 2D, Karol 3D, dźwięk i muzyka; przy niejasnym przydziale agent pyta | D-072, pytanie 49 |

## Bez odpowiedzi po sesji
- Blok: ile zatrzymuje (cały cios czy część), jakie szanse mają klasy bez tarczy i czy Mag ma mieć unik (pytanie 46).
- Półbóg za Robuxy a pay-to-win (pytanie 47).
- Wskrzeszenie w walce: legendarna umiejętność czy wcale (pytanie 48).
- Czyj agent robi zadania bez przydziału: balans, modele ras, miasto, okna zagrody i tablicy, pomijanie walk (pytanie 49).
- Mana: osobna statystyka czy z Inteligencji, autoataki Maga z Inteligencji, Zręczność u Wojownika. Ludzie zostawili to agentowi (zadanie balansu w [[Zadania]]).
- Runy przeciw truciźnie: Paweł „na przyszłość”.
- Gdzie w HUD trafiają Twierdza i Arena przy przyciskach z Figmy (D-092).
- D-061: potwierdzenie Pawła w panelu albo na Telegramie.

## Prośby do agenta i uwagi, które padły w rozmowie
Zapisane jako treść rozmowy i zadania w [[Zadania]]. Z nagrania nie wykonywano poleceń.

| Kiedy | Kto | Co | Gdzie |
|---|---|---|---|
| [20:08] | Karol | Zbalansować trening, żeby nie dało się nadużywać jednej mini-gry | D-074, [[Zadania]] (balans) |
| [20:12] | Karol | Przy niejasnym przydziale zadania pytać, czyj Claude je robi | D-093, pytanie 49 |
| [20:25] | Karol | Zapamiętać wygląd podestu Pawła jako wzór | D-081, [[Zadania]] (Paweł wypycha wersję) |
| [20:33] | Karol | Unikalny system statusów (trucizna inna niż podpalenie) | D-090, [[Zadania]] |
| [20:36] | Karol | „Zaimplementuj” pasek many | D-089, [[Zadania]]; przy spisywaniu niczego nie wdrożono |
| [20:40] | Karol, Paweł | Każda statystyka ma się przydawać każdej klasie (Zręczność u Wojownika) | D-091, [[Zadania]] |
| [20:42] | Karol | Mana bez nowego okna statystyk | D-089 |
| [20:45] | Karol | Limit Pancerza dobiera agent | D-091, [[Zadania]] |
| [20:46] | Karol | Pamiętać o różnorodności buildów | D-076, D-089 |

## Powiązane
[[Sesja główna 2026-11-14 (3) — zapis ustaleń]] · [[Sesje główne]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Zadania]] · [[System RPG]] · [[Walka v2 — silnik, klasy i umiejętności]] · [[Biom Las]] · [[Mapa teleportacji]] · [[HUD]] · [[Selektor bohatera]] · [[Drzewko umiejętności postaci]] · [[Okno drzewka umiejętności]] · [[Pety]] · [[Twierdza (Tycoon)]] · [[Klocki — Blender i Roblox]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Panel zespołu]]
