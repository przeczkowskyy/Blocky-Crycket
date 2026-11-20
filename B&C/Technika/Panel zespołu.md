---
status: propozycja
tags: [technika, panel, workflow, narzędzia]
---
# Panel zespołu

> [!info] W skrócie
> Lokalna strona (`panel/`, port 8787) dla dwóch osób: **okno na ten sejf**, raporty z wdrożeń z akceptacją, podgląd 3D tego, co stoi w Roblox Studio, agent Claude Code na subskrypcji, głosówki, sieć notatek i analityka gry. Powstał na prośbę Karola 12.11.2026. **Nie zastępuje sejfu** (decyzja D-008): decyzje, zadania i roadmapę czyta z notatek, a własne dane to tylko raporty, komentarze i migawki. Czeka na zgodę (Karol albo Paweł, decyzja D-030) — [[Pytania otwarte]] #11, propozycja D-012 w [[Rejestr decyzji]].

## Po co, skoro jest sejf
| Potrzeba | Sejf w Obsidianie | Panel |
|---|---|---|
| Pytania, decyzje, zadania, roadmapa, dziennik | źródło prawdy | zakładka Pytania: jedna lista „Do odpowiedzi” (pytania, decyzje do zatwierdzenia, raporty do akceptacji), historia, wyszukiwarka, Plan; odpowiedzi, decyzje i zadania zapisywane w tych samych notatkach, też na telefonie |
| „Co zostało wdrożone i czy to akceptuję?” | wpis w dzienniku | karta raportu ze zrzutami i przyciskami Akceptuję / Do poprawy |
| Zobaczyć mapę bez uruchamiania Studio | — | podgląd 3D z migawki części + zrzuty ze Studio |
| Komentarz do konkretnego budynku | — | klik w element modelu → wątek komentarzy, także głosowy |
| Polecenie dla Claude'a bez otwierania edytora | — | zakładka Agent (ten sam Claude Code, to samo konto) |
| Graf notatek bez Obsidiana | widok grafu | zakładka Sieć |
| Kto teraz pracuje | — | lewy dolny róg: kto jest na panelu, w której zakładce, kto rozmawia w Sesji; na Pulpicie także Team Create i ostatnie commity |
| Rejestr grafik i ich etap w pipeline | plik `assets/manifest.json` | zakładka Assety: miniatury, etapy, numery Roblox, komentarze (tylko do odczytu) |
| Liczby z opublikowanej gry | — | Analityka → Telemetria gry (po włączeniu, zob. [[Telemetria gry]]) |
| Długa rozmowa głosowa z zapisem ustaleń | [[Sesje główne]] (tematy) | zakładka Sesja: rozmowa jak na Discordzie, agent słucha, spisuje i robi notatki |

## Uruchomienie
```
python panel/serwer.py              # http://127.0.0.1:8787
python panel/serwer.py --lan        # także telefon w tej samej sieci Wi-Fi (z kodem dostępu)
python panel/serwer.py --sprawdz    # kontrola środowiska
```
Bez instalowania zależności (sam Python 3.9+). Pełna instrukcja: `panel/INSTALACJA.md`, architektura i API: `panel/README.md`.

## Jak działa wspólna praca
- **Wspólne dane idą przez git**: raport, komentarz i migawka to osobne pliki w `panel/dane/`, więc dwie osoby mogą dopisywać naraz bez konfliktów. Przyciski Pobierz i Wyślij na Pulpicie robią `git pull` i commit samych danych panelu.
- **Samo się synchronizuje (D-070, od 14.11.2026)**: panel na komputerze z panelem co półtorej minuty sam pobiera z GitHuba to, co wysłała druga osoba (widoki się odświeżają, a w panelu i na Telegramie widać, kto wysłał i co), i sam wysyła zmiany zrobione w panelu — minutę po ostatniej zmianie. Przyciski Pobierz i Wyślij zostają. Panel nigdy nie rusza plików, nad którymi ktoś właśnie pracuje. Na Pulpicie, w karcie Synchronizacja, mały napis mówi, jak jest:
  - **Zsynchronizowano 17:42** — wszystko zgodne z GitHubem.
  - **Czeka: lokalne zmiany w 2 plikach** — na GitHubie są nowe zmiany w plikach, które ktoś (agent, Blender, człowiek) zmienia na komputerze z panelem i jeszcze ich nie zapisał commitem. Panel ich nie rusza i czeka; ruszy sam, gdy te pliki zostaną zacommitowane. Odmiana **Czeka: pliki dodane do commita (git add)** — ktoś dodał pliki do commita, ale commitu jeszcze nie zrobił; panel czeka, aż go dokończy.
  - **Konflikt — potrzebny człowiek** — zmiany z GitHuba i z komputera z panelem dotyczą tych samych miejsc w plikach. Panel niczego nie zmienił; trzeba scalić ręcznie (najprościej: poprosić agenta na komputerze z panelem). Kliknięcie napisu pokazuje pliki i co zrobić.
- **Agent** to `claude -p` uruchamiany w folderze projektu: czyta `CLAUDE.md`, ten sejf i skille, działa na subskrypcji osoby, na której komputerze stoi panel — także wtedy, gdy pisze do niego ktoś zdalnie (telefon, tunel). Dlatego lista wątków w zakładce Agent pokazuje przy każdym wątku, kto go założył i czy zdalnie, oraz kto jeszcze w nim pisał (od 14.11.2026; starsze wątki bez tej informacji). Tryby: Plan (tylko czyta), Praca (edytuje i używa dozwolonych narzędzi), Auto. Od 14.11.2026 zakładka ma pięć okien z osobnymi rolami i krótkie odpowiedzi — zob. niżej „Zakładka Agent: okna”.
- **Raport od Claude'a**: po wdrożeniu czegokolwiek Claude robi migawkę (`python panel/narzedzia/migawka.py`) i publikuje raport (`python panel/narzedzia/raport.py dodaj …`) z odwołaniem do elementów; odpowiedź człowieka czyta poleceniem `raport.py odpowiedzi`. Opis dla agentów: skill `.claude/skills/panel/`.
- **Podgląd 3D** rysuje części Roblox (bloki, kliny, walce, kule) w przeglądarce z pliku `czesci.json`; siatki z importu pokazuje jako ramki, a prawdziwy wygląd dają zrzuty ze Studio.

## Bezpieczeństwo i prywatność
- Domyślnie panel słucha tylko na tym komputerze. Wejście z telefonu wymaga kodu; agent z telefonu jest domyślnie wyłączony (włącza go osoba przy komputerze: Ustawienia → Telefon).
- Uprawnienia „osoby przy komputerze” (agent, git, nowa migawka) daje **klucz lokalny** zapamiętany w przeglądarce po uruchomieniu `panel\start.bat` — samo połączenie z tego samego komputera nie wystarcza. Wspólna konfiguracja z repozytorium nie może zmienić ustawień bezpieczeństwa.
- Kod przeszedł przegląd bezpieczeństwa 12.11.2026 (14 potwierdzonych uwag, wszystkie poprawione; lista w opisie commita).
- Rozmowy z agentem i nagrania głosowe zostają lokalnie. Do repozytorium trafia tylko tekst raportów i komentarzy.
- **Repozytorium jest publiczne** — wszystko w `panel/dane/` jest widoczne dla każdego. Zob. [[Workflow i Git]].

## Praca na sejfie z panelu (D-028)
Zakładka Pytania (dawniej Plan, potem Decyzje) potrafi zapisywać do sejfu: odpowiedź pod pytaniem otwartym, odhaczenie i dodanie zadania oraz zatwierdzenie albo odrzucenie decyzji. Każda zmiana to mały, czytelny wiersz w tym samym pliku Markdown co zawsze i ślad w [[Dziennik zmian]] (sekcja „Panel (ludzie)”); panel sprawdza, czy plik nie zmienił się w międzyczasie w Obsidianie. Odpowiedzi gości z samym kodem dostępu (bez klucza lokalnego i bez klucza zatwierdzania) są oznaczane „gość panelu” — samo imię nie daje uprawnień. Zapis jest włączony (D-028; odpowiedź Karola na [[Pytania otwarte]] #23); wyłączenie: `"zapis_sejfu": false` w konfiguracji. Szczegóły i API: `panel/README.md`.

### Zakładka Pytania (od 14.11.2026)
Na prośbę Karola z 13.11.2026 zakładki Plan i Raporty połączono w jedną (najpierw nazwaną Decyzje), a 14.11.2026, po jego uwagach, wszystko skondensowano do jednej kategorii — **Pytania**. Zakładka ma jedną listę **Do odpowiedzi**, bez podzakładek: każda pozycja jest pytaniem do człowieka — pytanie z [[Pytania otwarte]] (pole odpowiedzi), decyzja „propozycja” albo „do decyzji” z [[Rejestr decyzji]] jako „Czy zatwierdzamy: …?” z przyciskami **Tak** / **Nie** i raport czekający na akceptację jako „Czy akceptujesz: …?” (albo własne pytanie raportu) z **Akceptuję** / **Do poprawy**. Mała etykieta nad tytułem mówi, skąd pozycja pochodzi. Najnowsze i najważniejsze są na górze. Nad listą jest **wyszukiwarka** (tytuły i treść wszystkiego, także historii; szuka też po statusie, np. „do poprawy”, „odrzucona”), pod nią wspólna historia **Odpowiedziane** (pytania z odpowiedziami, decyzje zatwierdzone i odrzucone, raporty po decyzji — od najnowszych) i zwijany **Plan**: Zadania, Roadmapa, Dziennik zmian. Ta sama lista pytań stoi w zakładce **Sesja** (pod transkrypcją i notatkami, obok Agendy), żeby odpowiadać w trakcie rozmowy głosowej.
- **Pytanie i jego decyzje to jedna karta.** Powiązanie zapisuje się w notatce pytań wierszem `Rozstrzyga: D-019, D-020` w treści pytania (przed „**Odpowiedź:**”). Gdy Karol albo Paweł zatwierdzi lub odrzuci ostatnią otwartą decyzję z tej listy, panel w tej samej chwili dopisuje pod pytaniem odpowiedź z jego podpisem, np. `- Karol (2026-11-13): rozstrzygnięte decyzjami: D-019 zatwierdzona, D-020 odrzucona`, i ślad w [[Dziennik zmian]]. Sama wzmianka o decyzji w treści pytania (bez tego wiersza) jest tylko pokazywana jako „Powiązane decyzje”.
- **Na sesję główną** — przycisk przy pytaniu i decyzji dopisuje temat do [[Sesje główne]]; sprawa znika z listy do grupy „Odłożone na sesję główną”.
- **Nieaktualne** (prośba Karola z 14.11.2026) — trzecia możliwość obok odpowiedzi, Tak / Nie i Akceptuję / Do poprawy: jedno kliknięcie zdejmuje sprawę z listy (powód opcjonalny), a „Zaznacz kilka” zdejmuje wiele naraz. Pytanie dostaje odpowiedź `nieaktualne — powód`, decyzja status `🗃️ nieaktualna` w [[Rejestr decyzji]] (nie obowiązuje, nie czeka na drugi podpis, bez alertu na Telegramie; „Przywróć” w historii), raport — „nieaktualne”; wszystko widać w historii „Odpowiedziane” i po słowie „nieaktualne” w wyszukiwarce. **Ważne:** zanim ktoś oznaczy decyzję jako nieaktualną, obaj musicie mieć nowy kod i zrestartowany panel — panel sprzed tej zmiany bierze taką decyzję za propozycję i po „Tak” dopisuje drugi wiersz statusu. Nowy panel wtedy ostrzega w karcie i nic nie zmienia, dopóki w Obsidianie nie zostanie jeden wiersz.
- **Krótkie, lekkie karty** (uwagi Karola z 14.11.2026): bez kolorowego paska z lewej i bez ciężkich ramek, wyraźny tytuł, mała szara etykieta pochodzenia i statusu. Karta pokazuje tylko, czego sprawa dotyczy: przy pytaniu punkty z góry treści, przy decyzji i raporcie najwyżej dwa pierwsze zdania opisu. Wiersz `Szczegóły:` i wszystko pod nim, wiersze `Dopisek …` i `Sprostowanie …` oraz dalszy opis są zwinięte za małym „Pokaż szczegóły”. Dlatego w [[Pytania otwarte]] na górze pytania warto trzymać 2–4 krótkie punkty, a dłuższy opis pod `Szczegóły:`.
- Lista odświeża się sama (po każdej akcji, co kilkanaście sekund i po powrocie do karty), ale nie rusza karty, w której ktoś pisze.
- Pulpit pokazuje na górze liczbę pytań i trzy pierwsze z nich (lekkie wiersze, bez kolorowych znaczków), stan rozmowy w zakładce Sesja, „Co nowego” i przyciski Pobierz / Wyślij.
- **Prace w toku** (prośba Karola z 15.11.2026): na samej górze Pulpitu widać, co agenci właśnie robią, na jakim są etapie i o której mniej więcej skończą („koniec ok. 12:40 (za 35 min)”, „po czasie o 10 min”, „gotowe 11:52” z linkiem do raportu), a przy raporcie, pytaniu albo decyzji, nad którą trwa praca, mały znaczek „w pracy — koniec ok. 12:40”. Agenci zgłaszają każdą dłuższą pracę z szacowanym końcem i podają ten koniec w każdej wiadomości do ludzi; pliki prac leżą na komputerze, na którym powstały (same nie robią commitów; gdy wymiana prac jest włączona — niżej — ich krótki opis trafia na osobną gałąź na GitHubie).
- **Prace obu osób i nakładanie się pracy** (prośba Karola z 15.11.2026): przed ciężką pracą (przebudowa modelu, mapa, budowa w Studio, większa przeróbka) agent zgłasza też, czego ona dotyczy (np. „model rycerza”, „mapa lasu”, „kontener w Studio”). Gdy wymiana prac jest włączona (domyślnie wyłączona; włącza ją Karol — wpis `"prace": {"wymiana": true}` w `panel/konfiguracja.json`, po `git pull` działa na obu komputerach), każdy komputer — także Pawła, bez uruchomionego panelu — wysyła swoje trwające prace na osobną gałąź `stan/prace-<osoba>` na GitHubie (nie rusza plików ani gałęzi `main`). **Ta gałąź jest publiczna i jej historia zostaje na zawsze:** tytuły, etapy i godziny trwających prac widać na GitHubie — nie wpisujcie w nie niczego prywatnego (panel i tak wycina adresy, kody i ścieżki). Na Pulpicie widać wtedy prace obu osób, a gdy dwie prace dotyczą tego samego, przy obu stoi złoty napis „Nakłada się z pracą Pawła: … — wspólne: model rycerz. Poczekaj albo się umówcie.”. Panel ostrzega też, gdy druga osoba właśnie wysłała zmiany w plikach, nad którymi trwa praca na tym komputerze, i raz pisze o nowej kolizji na Telegramie. Przebudowa modelu sama sprawdza, czy druga osoba nie pracuje nad tym samym modelem, i wtedy zatrzymuje się, zanim ruszy Blender (pliki modeli są binarne i nie dadzą się połączyć). Stan starszy niż 12 godzin i praca bez żadnej zmiany od 12 godzin są pokazywane jako „możliwie nieaktualne”, bez alarmu.
- To zmiana wyglądu i działania panelu (narzędzia), nie kanonu gry; zasada D-008 (sejf jest jedynym źródłem prawdy) zostaje bez zmian.

### Kto zatwierdza decyzje w panelu (D-030)
Od 13.11.2026 Karol i Paweł mają równe prawa: wystarcza decyzja jednego z nich, a każda zostaje w logach z imieniem i datą. W panelu status decyzji zmienia:
- osoba **przy komputerze, na którym działa panel** (klucz lokalny) — bez dodatkowego klucza;
- przeglądarka z **kluczem zatwierdzania** (dawniej „klucz Game Directora”) — także z telefonu i przez tunel. Link z kluczem wypisuje `python panel/serwer.py --klucz-zatwierdzania` (dawna nazwa `--klucz-gd` działa dalej, link zapisany wcześniej w przeglądarce też).

Gość z samym kodem dostępu decyzji nie zmienia. Przed zatwierdzaniem trzeba wpisać imię w Ustawieniach — bez imienia panel decyzji nie zapisze, bo musi ją podpisać. Dotyczy to także komputera z panelem: imię, którym podpisuje się tam Git, decyzji nie podpisuje.

Jak panel podpisuje:
- w [[Rejestr decyzji]]: `zdecydował: Paweł 2026-11-13` (zatwierdzona albo odrzucona), `oznaczył: Karol 2026-11-13` („do decyzji”), wiersz `Uzasadnienie — Paweł, 2026-11-13: …`;
- w [[Dziennik zmian]]: `- Paweł (klucz zatwierdzania): decyzja D-019 zatwierdzona` (z kluczem zatwierdzania) albo `- Karol: decyzja D-019 zatwierdzona` (przy komputerze z panelem);
- w odpowiedziach w [[Pytania otwarte]]: `- Paweł (klucz zatwierdzania, 2026-11-13): …`, `- Karol (2026-11-13): …` albo `- Paweł (gość panelu, 2026-11-13): …`. Odpowiedź „gościa panelu” nie jest zgodą, nawet podpisana imieniem Karola albo Pawła.

Wpisy z 13.11.2026 sprzed tej zmiany mają jeszcze znacznik „Game Director” (np. `zdecydował: Game Director (Paweł) 2026-11-13` albo `- Paweł (Game Director): …`) — znaczy on dokładnie to samo co „klucz zatwierdzania”. Zapis podpisany imieniem „Game Director”, „klucz zatwierdzania” albo „gość panelu” panel odrzuca, bo takie imię udawałoby znacznik serwera.

### Potwierdzanie przez drugą osobę (D-043)
Zbudowane 14.11.2026 według D-043 (jedna osoba decyduje, druga dostaje alert i odpowiada). Po zatwierdzeniu albo odrzuceniu decyzji w panelu druga osoba dostaje pytanie: w zakładce Pytania („Karol zatwierdził: … — zgadzasz się?”) i — gdy działa bot — na Telegramie, w grupie „B&C decyzje”, z przyciskami **Zgoda**, **Brak zgody** i **Przedyskutuj**. Decyzja z jednym podpisem to **robocze ustalenie**; obowiązuje po dwóch podpisach. Wszystko zostaje w wierszu statusu w [[Rejestr decyzji]] (bez nowych statusów):
- czeka: `✅ zatwierdzona · … · zdecydował: Karol Balucki 2026-11-14`;
- zgoda: `… · zdecydował: Karol Balucki 2026-11-14 · potwierdził: Paweł 2026-11-14`;
- brak zgody: `🕓 do decyzji · … · sprzeciw: Paweł 2026-11-14 (wobec: zatwierdzona przez Karol Balucki 2026-11-14)`, opcjonalnie wiersz `Uzasadnienie sprzeciwu — Paweł, 2026-11-14: …`; sprawa wraca na listę „Do odpowiedzi”;
- przedyskutuj: jak brak zgody, ale `do rozmowy: …`, a temat trafia na agendę [[Sesje główne]].

Czekają decyzje z podpisem Karola albo Pawła od 13.11.2026 (pełne imię „Karol Balucki” to Karol); starsze i podpisy „Game Director” nie czekają. Własnej decyzji nie da się potwierdzić. Każda odpowiedź zostawia ślad w [[Dziennik zmian]] z dopiskiem „przez panel” albo „przez Telegram” (np. `- Paweł (Telegram): decyzja D-019 potwierdzona: zgoda (…), przez Telegram`). Ponowna decyzja zaczyna potwierdzanie od nowa. Agenci nigdy nie dopisują drugiego podpisu sami. Na Telegramie: `/czeka` pokazuje, co czeka na Twoje potwierdzenie, `/pomoc` — opis. Bot działa tylko wtedy, gdy włączony jest komputer z panelem; ustawienia bota (token, numery osób i grupy) leżą wyłącznie w danych lokalnych tego komputera, nigdy w repozytorium. Zakładanie bota: `panel/INSTALACJA.md`, szczegóły: `panel/README.md`. Dotyczy [[Pytania otwarte]] #29: technika jest gotowa i sprawdzona w testach, czeka na próbę na prawdziwym Telegramie; działanie bez włączonego komputera zostaje otwarte.

## Zakładka Agent: okna (od 14.11.2026)
Na prośbę Karola z 14.11.2026 zakładka Agent ma **pięć okien** zamiast jednej listy rozmów. Każde okno to ten sam Claude Code, ale z inną rolą i listą notatek, które czyta na start:

| Okno | Do czego | Co agent może |
|---|---|---|
| **Ogólny** | wszystko inne: pytania o grę, sejf, kod, Roblox Studio i panel; tu są też starsze rozmowy i rozmowy założone przez panel dla sesji głosowych | jak dotąd, zależnie od trybu (Plan / Praca / Auto), ale bez internetu |
| **Balans** | liczby: statystyki i rzadkość przedmiotów, koszty i nagrody, tempo progresji, ile trwa dojście do następnego biomu | czyta pliki i zapisuje tylko w sejfie (B&C); bez internetu, Roblox Studio i poleceń |
| **Świat** | biomy (nazwy, wygląd, co w nich jest), potwory i bossowie — np. kryształowe slimy i golem-boss w biomie kryształowym | jak Balans |
| **Modele** | postacie, potwory i budynki z klocków: jak wyglądają, z czego się składają, co zlecić (na razie tylko opis zlecenia w notatce-propozycji); później dojdzie kolejka pracy | jak Balans |
| **Wydanie** | publikacja gry, zasady Roblox (także losowość i hazard), grupa Roblox, marketing, koszty, media społecznościowe | jak Balans, a do tego szuka w internecie aktualnych zasad Roblox i podaje źródło |

- **Krótkie odpowiedzi.** W każdym oknie obowiązuje ta sama reguła: pierwsze zdanie to odpowiedź albo wniosek, potem najwyżej 5 punktów; bez wstępu i podsumowania; szczegóły dopiero po słowie „rozwiń”; gdy agent coś zapisał — jedno zdanie, co i gdzie. Długa odpowiedź jest w panelu zwinięta („Pokaż całość”), a kroki agenta (czytanie plików, szukanie) są zwinięte do jednego wiersza z licznikiem.
- **Agent w oknach zapisuje tylko propozycje**: notatki ze statusem `propozycja`, wpisy 💡 w [[Rejestr decyzji]] i krótkie pytania w [[Pytania otwarte]]. Niczego nie zatwierdza i nie zmienia kanonu.
- **Karty okien** (rola, notatki na start, jak odpowiadać, co zapisywać, narzędzia) leżą w repozytorium w `panel/agenci/` — to zwykłe pliki po polsku, które można poprawiać; zmiana działa od następnej wiadomości. Poprawiają je tylko ludzie: żaden agent panelu (ani w oknach, ani przy sesji głosowej) nie może ich zmienić.
- **Rozmowa dla dwóch osób.** Do rozmowy w każdym oknie może dopisać się druga osoba (Karol przy komputerze, Paweł przez tunel, gdy włączony jest „Agent z telefonu”). Przy każdej wiadomości widać imię autora, a na liście — kto rozmowę założył i kto pisał. Kto pisze zdalnie, widzi pod polem zdanie, że odpowiedź idzie na subskrypcji gospodarza panelu. Rozmowa dostaje krótki tytuł z pierwszego pytania; tytuł można zmienić, klikając go.
- **Usuwanie rozmów.** Ikona kosza przy rozmowie (z potwierdzeniem) albo „Zaznacz” i usunięcie kilku naraz. Usunąć może osoba przy komputerze z panelem albo osoba, która rozmowę założyła (to samo imię z Ustawień i też zdalnie); gość bez imienia nie usuwa cudzych rozmów. Nie da się usunąć rozmowy, w której agent właśnie pracuje. Rozmowy założone przez panel dla sesji głosowych (oznaczone „systemowa”) usuwa tylko osoba przy komputerze, po ostrzeżeniu. Usunięcie kasuje rozmowę z danych lokalnych komputera z panelem — sejfu i repozytorium nie dotyka.
- **Układ.** Na komputerze z lewej okna (z jednym zdaniem opisu), pod wybranym oknem jego rozmowy, z prawej rozmowa. Na telefonie najpierw wybór okna, potem lista rozmów, potem rozmowa — z przyciskiem powrotu.
- To zmiana narzędzia (panelu), nie kanonu gry.

## Zadania dla agenta osoby (od 16.11.2026, propozycja D-072)
Na prośbę Karola z 16.11.2026: to, na czyim koncie Claude wykona się zadanie, wynika z przypisania, a nie z tego, kto otworzył panel.
- **Przypisanie** to pole na końcu linii w [[Zadania]], przed priorytetem: `- [ ] Opis · agent: Paweł · #średni`. Ustawia je Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania) w zakładce **Pytania → Plan → Zadania**: ikona agenta przy zadaniu (nikt / Karol / Paweł) albo wybór w „Dodaj zadanie”. Gość z samym kodem dostępu nie przypisuje.
- **Słownie:** na koniec sesji głównej agent dopisuje pole, gdy w rozmowie ktoś wyraźnie powiedział, czyj agent ma zrobić zadanie („to zrobi Claude Pawła”, „na moim koncie”). Bez takiej wypowiedzi pola nie dopisuje.
- **Uruchamianie:** zadanie z „agent: Paweł” rusza tylko na komputerze Pawła — przyciskiem **Uruchom** albo samo, jeśli Paweł włączy u siebie Ustawienia → Telefon → „Zadania mojego agenta: uruchamiają się same” (domyślnie wyłączone; po jednym zadaniu naraz; raz uruchomione nie wraca samo). Na komputerze Karola przy takim zadaniu widać tylko znaczek „agent: Paweł”. Agent robi zadanie w trybie Praca według `CLAUDE.md` i sejfu, a postęp widać w „Prace w toku” (przy włączonej wymianie prac — także u drugiej osoby).
- **Warunki:** panel musi wiedzieć, czyj jest komputer — raz `git config bc.osoba "Paweł"` (albo „Karol”) w repozytorium. Żeby zadania Pawła się wykonywały, Paweł uruchamia własny panel (albo prosi swojego Claude Code o zadania z „agent: Paweł”).
- **Dla Pawła:** co ustawić raz (własny panel, samo uruchamianie, start z Windowsem) i jak ma się zachowywać jego Claude Code — [[Zadania z panelu — instrukcja dla Claude Code Pawła]].
- Szczegóły techniczne i API: `panel/README.md` (część „Zadania dla agenta osoby”).

## Assety na żywo i szybsze pobieranie z GitHuba (od 16.11.2026)
Zgłoszenie Karola z 16.11: zakładka Assety nie była aktualna na bieżąco. Tego wieczoru nowe grafiki Pawła, wypchnięte o 21:24, pojawiły się u Karola dopiero o 21:35 i dopiero po ręcznym odświeżeniu.
- **Przyczyna opóźnienia:** zastój w stałej synchronizacji. Przychodzący commit zmieniał też Dziennik zmian, w którym leżały niezapisane zmiany z kliknięć w panelu; pobieranie czekało na ich zapis, a zapis czekał na pobranie. Zastój przerywało dopiero ręczne „Wyślij”.
- **Pobieranie teraz:** gdy z cudzymi zmianami kolidują wyłącznie własne, niewysłane zmiany panelu, panel zapisuje je commitem tylko lokalnie i od razu pobiera; wysyłanie idzie dalej dotychczasową regułą spokoju. Co 30 s panel lekko sprawdza, czy na GitHubie jest nowy commit, i wtedy pobiera od razu. Cudza praca w toku nadal nie jest dotykana — wtedy panel czeka jak dotąd, a stan trafia do logu.
- **Zakładka Assety:** odświeża się sama (kilka sekund po zmianie rejestru albo obrazu), bez gubienia filtrów i otwartych szczegółów; pokazuje godzinę ostatniej zmiany, znaczek „nowe” przy grafikach dodanych od ostatniego oglądania i pasek, gdy na GitHubie czekają niepobrane zmiany.
- **Sprawdzone:** cały zestaw testów panelu (621, w tym 19 nowych) i próba w przeglądarce bez okna (29 kroków). **Niesprawdzone:** telefon przez tunel i pełny obieg z drugą osobą na żywo.
- Ustawienia i szczegóły: `panel/README.md` (stała synchronizacja, Assety).

## Podgląd: akceptacja kilku rzeczy naraz i podgląd prac (od 17.11.2026)
Zlecenie Karola z 14.11 („kolejka pracy i renderowania”): przy pracy w toku widać, jak wygląda to, co powstaje, a zakładka Podgląd pozwala przejrzeć i zaakceptować wiele rzeczy naraz.
- **Zakładka Podgląd** ma na górze przełącznik **Do przejrzenia** / **Model 3D**. „Do przejrzenia” pokazuje raporty czekające na Akceptuję / Do poprawy jako siatkę miniatur (pierwszy zrzut raportu albo zrzut jego migawki 3D; raporty bez obrazu na końcu). Zaznaczone można zaakceptować albo odesłać do poprawy jednym przyciskiem — „Do poprawy” pyta o jeden komentarz dla wszystkich. **Przeglądaj po kolei** pokazuje jeden raport na cały ekran: duży obraz, pytanie, dwa zdania opisu, Akceptuję / Do poprawy / Pomiń, po decyzji od razu następny, na końcu podsumowanie. To ta sama decyzja co w zakładce Pytania; pominięty raport czeka dalej. „Model 3D” to dotychczasowy podgląd migawek.
- **Podgląd przy pracy w toku:** agent dokłada do pracy zrzut (`praca.py zrzut --id … --plik …` albo `--zrzut` przy zmianie etapu), wskazuje folder z klatkami (`--podglad-z swiat/<scena>/klatki` — panel sam pokazuje najnowszą) albo migawkę 3D (`--migawka <id>`). Na Pulpicie przy pracy jest mała miniatura, w zakładce Podgląd w części „Powstaje teraz” — duży obraz. Zrzuty prac leżą tylko na komputerze, na którym powstała praca (6 ostatnich na pracę); nie trafiają do repozytorium ani na publiczną gałąź prac, więc druga osoba widzi u siebie tylko tytuł, etap i koniec cudzej pracy.
- **Na sesji padło:** gdy agent w roboczych notatkach sesji zapisze w części „Padły odpowiedzi na pytania” numer pytania albo decyzji, lista Pytania w zakładce Sesja pokazuje przy tej sprawie „Na sesji padło: …”. Przycisk **Wpisz do odpowiedzi** wstawia to zdanie do pola odpowiedzi; człowiek je poprawia i wysyła sam, swoim podpisem. Do sejfu nic nie idzie bez tego kliknięcia. Sprawdzone tylko na podstawionych notatkach, jeszcze nie na prawdziwej sesji.
- W karcie pytania decyzja z wiersza „Rozstrzyga:” jest oddzielona cienką linią, bez ciemnego pudełka w pudełku.
- Zlecenia Karola z 13.11 i z „drugiej fali” 14.11 (jedna zakładka Pytania zamiast Planu i Raportów, krótkie karty, aktywne osoby w lewym dolnym rogu, samo odświeżanie) były zrobione już 14.11 — potwierdzone próbą w przeglądarce 17.11.
- To zmiana narzędzia, nie kanonu gry; zasada D-008 bez zmian.
- **Sprawdzone:** cały zestaw testów panelu (635) i próba w przeglądarce bez okna przy szerokości telefonu i komputera. **Niesprawdzone:** prawdziwy telefon przez tunel, prawdziwa sesja głosowa, duże zrzuty ze Studio.
- Szczegóły: `panel/README.md`.

## Sesja — długa rozmowa głosowa z agentem
Zakładka **Sesja** (dodana 13.11.2026 na prośbę Karola, czeka na zgodę jak cały panel) służy do „sesji głównych”, czyli długich rozmów Karola i Pawła. Obaj wchodzą na ten sam panel (gospodarz przy komputerze, druga osoba przez link tunelu), klikają **Dołącz** i rozmawiają w przeglądarce — głos idzie wprost między nimi.
- **Układ (od 14.11.2026, uwagi Karola)**: u góry wąski pasek pokoju (kto jest, Dołącz / Rozłącz, Wycisz, „Agent słucha” z czerwonym znacznikiem). Pod nim na komputerze, bez przewijania, dwie kolumny obok siebie: **Transkrypcja na żywo** i **Notatki agenta**; Agenda i Pytania są niżej (skróty do nich w pasku pokoju). Na telefonie pod paskiem jest przełącznik **Transkrypcja / Notatki / Agenda / Pytania** — na start Transkrypcja.
- **Agenda**: tematy do omówienia czyta i zapisuje notatka [[Sesje główne]]. Temat można dopisać w zakładce, a agent na przycisk „Zaproponuj tematy” przegląda [[Pytania otwarte]], [[Rejestr decyzji]] i [[Dziennik zmian]] i dopisuje propozycje (z dopiskiem „propozycja agenta”). Gdy ktoś odkłada decyzję „na sesję długą”, temat ląduje właśnie tam.
- **Agent słucha**: włącza Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania). Wszyscy w pokoju widzą wtedy czerwony znacznik nagrywania. Każdy nagrywa swój mikrofon, panel spisuje to lokalnie (Whisper, jak głosówki) i pokazuje transkrypcję na żywo; dźwięk kasuje zaraz po spisaniu. Co kilka minut agent aktualizuje robocze notatki — **krótko, same punkty**: Ustalenia (do 7), Do zrobienia (do 5), Bez odpowiedzi (do 5) i Padły odpowiedzi na pytania („#N: jedno zdanie”), całość do ok. 150 słów. Szczegóły zostają w zapisie rozmowy i w końcowym zapisie ustaleń.
- **Zakończ sesję i spisz ustalenia**: agent zapisuje w sejfie notatkę z ustaleniami (status `propozycja`, wzór: [[Rozmowa 2026-11-12 — zapis ustaleń]]), dopisuje ustalenia jako propozycje do [[Rejestr decyzji]], pytania i zadania, **dopisuje odpowiedzi, które padły w rozmowie, pod otwartymi pytaniami** w [[Pytania otwarte]] (wiersz `- Claude Code (RRRR-MM-DD, z sesji głównej HH:MM): … Zapis agenta z rozmowy.`; gdy odpowiedź jest niepełna albo niepewna — tylko `Dopisek …` nad odpowiedzią), więc po sesji lista Pytania pokazuje, co ustalono; oznacza omówione tematy i wysyła raport z listą do zatwierdzenia. **Agent niczego nie zatwierdza** — robi to człowiek w panelu. Panel najpierw czeka na ostatnie wypowiedzi (także te z ostatnich sekund przed kliknięciem) i na ich spisanie; jeśli spisywanie nie nadąża, agent dostaje informację, że zapis jest niepełny, i zaznacza to w ustaleniach.
- **Agent nie słucha poleceń z rozmowy**: to, co ktoś powie do mikrofonu albo wpisze w agendzie, jest dla agenta treścią rozmowy, nie poleceniem. Przy notatkach agent może tylko czytać, a przy spisywaniu ustaleń ma wąski zestaw narzędzi (bez internetu, bez Roblox Studio).
- **Prywatność**: pełny zapis bieżącej rozmowy i notatki zostają tylko na komputerze z panelem (nie w repozytorium); widzą je osoby w pokoju. Dawne sesje widzi i pobiera tylko osoba przy komputerze. Gdy głos nie połączy się bezpośrednio, można rozmawiać przez Discord — nagrywanie i transkrypcja działają dalej.
- Kroki dla dwóch osób: `panel/INSTALACJA.md` (część „Sesja”), szczegóły techniczne: `panel/README.md`.

## Wytwórnia: gry i pomysły (od 20.11.2026, D-115)
Zakładka **Wytwórnia** (na telefonie w „Więcej”) czyta folder [[00 Wytwórnia pomysłów]]:
- **Portfel gier** — gry na etapie prototyp / test / publiczna z liczbami D1, D7, sesja, gracze naraz (pola `d1`, `d7`, `sesja_min`, `ccu` w notatce gry; puste = „brak danych”) i przyciskiem **Pulpit gry**: notatka, liczby, link do gry na Roblox (pole `miejsce`) oraz raporty, zadania i decyzje tej gry. Dopasowanie: raport, którego tytuł zaczyna się od nazwy gry; zadanie albo decyzja, która wspomina nazwę gry (pole `gra`, nazwa notatki albo `aliases`). Na Pulpicie jest też karta „Gry”.
- **Lejek pomysłów** — kolumny pomysł → ocena → prototyp → test → publiczna, werdykt agenta w kolorze (buduj / popraw / odrzuć), paski ocen Agenta, Karola i Pawła; wstrzymane i porzucone zwinięte.
- **Karta pomysłu** — 10 kryteriów [[Karta oceny pomysłu]] z kolumnami Agent / Karol / Paweł, „Krytyka agenta”, komentarze. **Oceń** wpisuje tylko własną kolumnę w tabeli notatki i sumę (`ocena_karol` / `ocena_pawel`); **Zmień etap** zmienia pole `etap`. Gość panelu nie ocenia i nie zmienia etapu.
- **Dodaj pomysł** — nowa notatka z szablonu „Pomysł gry” w `Wytwórnia/Pomysły/` (może też gość), wpis w Dzienniku jak przy innych zmianach z panelu.
- **Radar trendów** — tabela z [[Radar trendów]] z datą aktualizacji.
Szczegóły techniczne i API: `panel/README.md`.

**Temat sesji (od 20.11.2026):** w zakładce Sesja lista „Temat sesji” — Wytwórnia (nowe pomysły na gry), gra z portfela, pomysł z lejka, Pytania do odpowiedzi albo Inne (z tekstem). Wybiera Karol albo Paweł, widzą wszyscy w rozmowie; temat zapisuje się przy sesji, a agent sesji czyta pod niego notatki (Wytwórnia, notatka gry, karta pomysłu) i z niego proponuje agendę.

## Wejście z telefonu spoza domu (tunel)
Sprawdzone naprawdę 13.11.2026: przenośny `cloudflared` (bez instalatora i uprawnień administratora) wystawia panel pod losowym adresem https, a wejście wymaga kodu dostępu. Gość z tunelu nie dostaje uprawnień osoby przy komputerze — nie uruchomi agenta, gita ani nowej migawki — nawet jeśli zna klucz lokalny. Przed udostępnieniem adresu drugiej osobie trzeba wyjąć z konfiguracji lokalnej prywatne sejfy podpięte do panelu. Kroki: `panel/INSTALACJA.md`.

## Stosunek do starego `dashboard/`
Stary dashboard (porzucony decyzją D-008) miał własną bazę z kopią decyzji i zadań oraz agentów na płatnym kluczu API. Panel robi odwrotnie: nie ma własnej bazy wiedzy, a agent działa na subskrypcji. Kodu `dashboard/` nie używa i nie zmienia.

## Powiązane
[[Jak prowadzimy sejf]] · [[Workflow i Git]] · [[Narzędzia]] · [[Klocki — Blender i Roblox]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Sesje główne]]
