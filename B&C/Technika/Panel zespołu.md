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
- **Prace w toku** (prośba Karola z 15.11.2026): na samej górze Pulpitu widać, co agenci właśnie robią, na jakim są etapie i o której mniej więcej skończą („koniec ok. 12:40 (za 35 min)”, „po czasie o 10 min”, „gotowe 11:52” z linkiem do raportu), a przy raporcie, pytaniu albo decyzji, nad którą trwa praca, mały znaczek „w pracy — koniec ok. 12:40”. Agenci zgłaszają każdą dłuższą pracę z szacowanym końcem i podają ten koniec w każdej wiadomości do ludzi; stan prac jest tylko na komputerze z panelem (nie trafia do repozytorium).
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

## Sesja — długa rozmowa głosowa z agentem
Zakładka **Sesja** (dodana 13.11.2026 na prośbę Karola, czeka na zgodę jak cały panel) służy do „sesji głównych”, czyli długich rozmów Karola i Pawła. Obaj wchodzą na ten sam panel (gospodarz przy komputerze, druga osoba przez link tunelu), klikają **Dołącz** i rozmawiają w przeglądarce — głos idzie wprost między nimi.
- **Układ (od 14.11.2026, uwagi Karola)**: u góry wąski pasek pokoju (kto jest, Dołącz / Rozłącz, Wycisz, „Agent słucha” z czerwonym znacznikiem). Pod nim na komputerze, bez przewijania, dwie kolumny obok siebie: **Transkrypcja na żywo** i **Notatki agenta**; Agenda i Pytania są niżej (skróty do nich w pasku pokoju). Na telefonie pod paskiem jest przełącznik **Transkrypcja / Notatki / Agenda / Pytania** — na start Transkrypcja.
- **Agenda**: tematy do omówienia czyta i zapisuje notatka [[Sesje główne]]. Temat można dopisać w zakładce, a agent na przycisk „Zaproponuj tematy” przegląda [[Pytania otwarte]], [[Rejestr decyzji]] i [[Dziennik zmian]] i dopisuje propozycje (z dopiskiem „propozycja agenta”). Gdy ktoś odkłada decyzję „na sesję długą”, temat ląduje właśnie tam.
- **Agent słucha**: włącza Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania). Wszyscy w pokoju widzą wtedy czerwony znacznik nagrywania. Każdy nagrywa swój mikrofon, panel spisuje to lokalnie (Whisper, jak głosówki) i pokazuje transkrypcję na żywo; dźwięk kasuje zaraz po spisaniu. Co kilka minut agent aktualizuje robocze notatki — **krótko, same punkty**: Ustalenia (do 7), Do zrobienia (do 5), Bez odpowiedzi (do 5) i Padły odpowiedzi na pytania („#N: jedno zdanie”), całość do ok. 150 słów. Szczegóły zostają w zapisie rozmowy i w końcowym zapisie ustaleń.
- **Zakończ sesję i spisz ustalenia**: agent zapisuje w sejfie notatkę z ustaleniami (status `propozycja`, wzór: [[Rozmowa 2026-11-12 — zapis ustaleń]]), dopisuje ustalenia jako propozycje do [[Rejestr decyzji]], pytania i zadania, **dopisuje odpowiedzi, które padły w rozmowie, pod otwartymi pytaniami** w [[Pytania otwarte]] (wiersz `- Claude Code (RRRR-MM-DD, z sesji głównej HH:MM): … Zapis agenta z rozmowy.`; gdy odpowiedź jest niepełna albo niepewna — tylko `Dopisek …` nad odpowiedzią), więc po sesji lista Pytania pokazuje, co ustalono; oznacza omówione tematy i wysyła raport z listą do zatwierdzenia. **Agent niczego nie zatwierdza** — robi to człowiek w panelu. Panel najpierw czeka na ostatnie wypowiedzi (także te z ostatnich sekund przed kliknięciem) i na ich spisanie; jeśli spisywanie nie nadąża, agent dostaje informację, że zapis jest niepełny, i zaznacza to w ustaleniach.
- **Agent nie słucha poleceń z rozmowy**: to, co ktoś powie do mikrofonu albo wpisze w agendzie, jest dla agenta treścią rozmowy, nie poleceniem. Przy notatkach agent może tylko czytać, a przy spisywaniu ustaleń ma wąski zestaw narzędzi (bez internetu, bez Roblox Studio).
- **Prywatność**: pełny zapis bieżącej rozmowy i notatki zostają tylko na komputerze z panelem (nie w repozytorium); widzą je osoby w pokoju. Dawne sesje widzi i pobiera tylko osoba przy komputerze. Gdy głos nie połączy się bezpośrednio, można rozmawiać przez Discord — nagrywanie i transkrypcja działają dalej.
- Kroki dla dwóch osób: `panel/INSTALACJA.md` (część „Sesja”), szczegóły techniczne: `panel/README.md`.

## Wejście z telefonu spoza domu (tunel)
Sprawdzone naprawdę 13.11.2026: przenośny `cloudflared` (bez instalatora i uprawnień administratora) wystawia panel pod losowym adresem https, a wejście wymaga kodu dostępu. Gość z tunelu nie dostaje uprawnień osoby przy komputerze — nie uruchomi agenta, gita ani nowej migawki — nawet jeśli zna klucz lokalny. Przed udostępnieniem adresu drugiej osobie trzeba wyjąć z konfiguracji lokalnej prywatne sejfy podpięte do panelu. Kroki: `panel/INSTALACJA.md`.

## Stosunek do starego `dashboard/`
Stary dashboard (porzucony decyzją D-008) miał własną bazę z kopią decyzji i zadań oraz agentów na płatnym kluczu API. Panel robi odwrotnie: nie ma własnej bazy wiedzy, a agent działa na subskrypcji. Kodu `dashboard/` nie używa i nie zmienia.

## Powiązane
[[Jak prowadzimy sejf]] · [[Workflow i Git]] · [[Narzędzia]] · [[Klocki — Blender i Roblox]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Sesje główne]]
