---
status: propozycja
tags: [technika, blender, 3d, pipeline, wdrozenie]
---
# Start z Blenderem — prompt dla Pawła

> [!info] W skrócie
> Wiedza o modelach nie siedzi w Blenderze, tylko w repozytorium: postacie, pety, ekwipunek i mapy powstają **z kodu Pythona**, który Claude uruchamia w Blenderze. Żeby Paweł robił modele tak samo jak Karol, wystarczy zainstalować cztery rzeczy i wkleić poniższy prompt do Claude Code otwartego w folderze repozytorium. Prompt jest w **trybie oszczędnym**, bo Paweł ma niższy plan Claude niż Karol. Przygotował Claude na prośbę Karola 15.11.2026.

## Co zainstalować (Windows)
1. **Blender 5.0** — z blender.org, do domyślnego folderu `C:\Program Files\Blender Foundation\`. Skrypty biorą najnowszą wersję z tego folderu; inną ścieżkę podaje się w zmiennej `BLENDER_EXE`. U Karola działa dokładnie wersja 5.0.
2. **ffmpeg** — w terminalu: `winget install Gyan.FFmpeg`, potem nowe okno terminala i `ffmpeg -version` na próbę.
3. **Python 3.12 lub nowszy** (python.org, zaznaczyć „Add to PATH”), potem: `pip install pillow requests python-dotenv`.
4. **Roblox Studio jako serwer MCP** — w Studio: Assistant → Manage MCP Servers → Enable Studio as MCP server. Do wgrywania modeli dodatkowo: Assistant → Settings → MCP Permissions → zakresy asset:read i asset:write oraz zatwierdzony folder `swiat/postacie/wynik`.

Potem: `git pull` w repozytorium, Claude Code w tym folderze i wklejony prompt. Czego zabraknie, Claude Pawła sam wypisze.

## Ile to kosztuje tokenów
Blender, rendery, filmy i testy działają na komputerze i **nie kosztują tokenów**. Tokeny idą na trzy rzeczy: czytanie kodu i dokumentów, pisanie kodu i **oglądanie obrazów** przez Claude'a.

Pomiary z 15.11.2026 u Karola (plan Max 20x, praca kilkoma agentami naraz: wykonanie, wroga kontrola, poprawki):

| Praca | Zużycie agentów |
|---|---|
| Gołe modele trzech bohaterów ze strojem jako przedmiotami | ok. 1,6 mln tokenów |
| Biom Las w wersji 2 (faktury, detale, budowa w Studio) | ok. 1,2 mln |
| Kod chodzących potworów (projekt, dwóch programistów, przegląd) | ok. 1,5 mln |
| Porządki w kodzie stroju z niezależną kontrolą | ok. 0,6 mln |

To jest tryb „jakość za wszelką cenę” i **na niskim planie się nie zmieści** — jedna taka paczka potrafi zjeść cały limit albo więcej. Dokładny limit planu Pawła pokazuje polecenie `/usage` w Claude Code.

Gdzie tokeny uciekają najbardziej i co z tym zrobić:
- **Lista lektur na start.** Wszystkie dokumenty z dawnej wersji promptu to ok. 410 kB, czyli rząd 130 tys. tokenów w każdej nowej rozmowie. W trybie oszczędnym Claude czyta na start ok. 25 kB, a resztę dopiero, gdy zadanie jej dotyczy.
- **Duże moduły postaci.** `rycerz.py`, `kot_mag.py` i `zwiadowca.py` mają po ok. 80 kB (rząd 27 tys. tokenów za jedno przeczytanie całości). Trzeba szukać funkcji i czytać tylko jej fragment.
- **Kilku agentów naraz.** Każdy agent czyta to samo od nowa. Na niskim planie: jeden agent, a przegląd świeżym okiem jako krótka osobna rozmowa.
- **Obrazy.** Każdy obejrzany render to tokeny. Wystarczy plansza i jeden arkusz klatek na klip; pojedynczych klatek filmu nie trzeba oglądać, jeśli kontrola liczbowa przeszła.
- **Długie rozmowy.** Im dłuższa rozmowa, tym droższa każda kolejna wiadomość. Jedno zadanie = jedna rozmowa, potem `/clear`.

Jaki model: do codziennej pracy przy modelach **Sonnet** (zmiana poleceniem `/model`). Najmocniejszy model tylko na krótko: do zaplanowania nowej postaci albo mapy i do końcowej oceny obrazów. Najtańszy model (Haiku) wystarcza do zadań mechanicznych: uruchom przebudowę, odczytaj raport, zrób commit.

Podział pracy, który oszczędza najwięcej: duże nowe rzeczy (nowa postać z kompletem klipów, biom, przebudowa systemu) robi strona Karola na planie Max, a Paweł robi poprawki, warianty, kolory, przedmioty i nowe pomysły na bazie istniejących modułów. To zgadza się z decyzją D-065.

## Prompt (wkleić w całości)
```
Pracujesz w repozytorium gry Roblox BLOCKY & CRYCKET z Pawłem (Game Director). Działasz tak samo jak Claude Code Karola, który robi postacie, pety, ekwipunek i mapy w Blenderze: samodzielnie, bez pytania o każdy krok. Paweł ma niski plan Claude, więc pracujesz w TRYBIE OSZCZĘDNYM opisanym niżej — to jest ważniejsze niż tempo.

TRYB OSZCZĘDNY (zawsze)
- Model: Sonnet. Jeśli działasz na mocniejszym modelu, powiedz o tym Pawłowi na początku i zaproponuj /model. Mocniejszy model tylko na wyraźną prośbę Pawła: do planu nowej postaci albo mapy i do końcowej oceny obrazów.
- Jeden agent. Nie uruchamiaj wielu agentów, workflow ani równoległych zadań, chyba że Paweł wyraźnie o to poprosi i wie, że to kosztuje kilka razy więcej.
- Czytaj mało: nie czytaj całych dużych plików (rycerz.py, kot_mag.py, zwiadowca.py, PROJEKT.md, Rejestr decyzji mają po 50–85 kB). Najpierw szukaj (grep), potem czytaj tylko potrzebny fragment. Dokumentów z listy „na żądanie” nie czytaj z góry.
- Obrazy kosztują: oglądaj planszę postaci i jeden arkusz klatek na zmieniony klip. Nie oglądaj wszystkich renderów ani pojedynczych klatek filmu, jeśli kontrola liczbowa przeszła (python -B swiat/postacie/<moduł>.py --kontrola, swiat/biom_las/sprawdz.py).
- Najpierw sprawdzaj liczbami i testami (darmowe, lokalne), dopiero potem patrz na obraz.
- Do prób używaj szybkiego podglądu (podglad_postaci.py z --klip albo --tylko), a pełną przebudowę (przebuduj.py, wszystkie filmy) rób raz, na końcu.
- Wyniki poleceń skracaj (ostatnie wiersze), nie wypisuj całych logów i plików JSON.
- Jedno zadanie = jedna rozmowa. Po skończonym zadaniu przypomnij Pawłowi o /clear. Gdy rozmowa robi się długa, zaproponuj /compact.
- Zanim zaczniesz coś dużego (nowa postać z kompletem klipów, nowa mapa, przebudowa systemu), powiedz Pawłowi jednym zdaniem, że to duża praca, i zaproponuj, żeby zrobiła ją strona Karola (plan Max), a tu powstał sam pomysł albo wariant.
- Na prośbę Pawła pokaż zużycie (/usage).

NA START (sam, od razu, oszczędnie)
1. git pull na main.
2. Przeczytaj tylko: CLAUDE.md, B&C/00 Start.md, B&C/Technika/Postacie 3D — Blender i Roblox.md, B&C/Technika/Klocki — Blender i Roblox.md, B&C/Styl/Style Lock.md, B&C/Styl/Kierunek artystyczny.md.
3. Sprawdź środowisko: Blender 5.0 (C:\Program Files\Blender Foundation\ albo zmienna BLENDER_EXE), ffmpeg w PATH, Python z Pillow, Roblox Studio przez MCP (python tools/studio_mcp.py studios). Wypisz, czego brakuje; doinstaluj to, co da się z terminala.
4. Jedna próba działania, wynik do folderu poza repozytorium: python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rycerz.py --wyj <folder> --klip chod. Obejrzyj jeden obraz.
5. Zapisz zasady z tego promptu w swojej pamięci, żeby obowiązywały w kolejnych rozmowach.
6. Zgłoś Pawłowi w pięciu punktach: co działa, czego brakuje, co zrobiłeś.

DOKUMENTY NA ŻĄDANIE (czytaj dopiero, gdy zadanie ich dotyczy, i tylko potrzebny rozdział)
- Decyzje i pytania: B&C/Produkcja/Rejestr decyzji.md, B&C/Produkcja/Pytania otwarte.md (szukaj po numerze, np. D-071).
- Postacie i ekwipunek: swiat/postacie/README.md, swiat/postacie/EKWIPUNEK.md, swiat/postacie/biblioteka/README.md, wzór nowej postaci swiat/postacie/wzor_postaci.py.
- Mapy: swiat/krzywe_miasteczko/PROJEKT.md, swiat/biom_las/PROJEKT.md, swiat/biom_las/README.md.
- Panel i assety: .claude/skills/panel/SKILL.md, .claude/skills/asset/SKILL.md, B&C/Jak prowadzimy sejf.md.

JAK TU SIĘ PRACUJE
- Źródłem prawdy jest kod .py, nie plik .blend. Blender działa w tle i robi siatki (FBX/GLB), filmy, ikony i raport. Zmiana = edycja modułu, potem python -B swiat/postacie/przebuduj.py <moduł>. Jeden proces Blendera naraz.
- Dwie drogi do Robloxa: postać z klocków (części i Motor6D, roblox_postac.py, bez wgrywania) i siatka z Blendera (roblox_import.py, wgrywanie na konto). Postacie i pety głównie siatką (D-065), mapy i budynki z klocków (D-017, D-025).
- Mapy: swiat/<scena>/generuj.py → czesci.json → Blender, Studio (tools/studio_buduj.py) i podgląd w panelu. Faktury map tylko z wbudowanych materiałów Roblox.
- Ekwipunek jest widoczny na postaci, modele bazowe są bez stroju, a strój to przedmioty zakładane na model (D-071).
- Nowe rzeczy zaczynaj od istniejącego podobnego modułu albo od wzoru, nie od zera.
- Po wdrożeniu czegoś do oceny: raport w panelu z jednym–trzema obrazami (skill panel). Panel działa u Karola; Paweł wchodzi przez link, własnego nie uruchamiaj.

JAKOŚĆ (ten sam tor co u Karola, w wersji oszczędnej)
- Krótki opis zamiaru z liczbami → zmiana w kodzie → kontrola liczbowa → szybki podgląd → poprawki → pełna przebudowa raz → przegląd świeżym okiem → raport do akceptacji człowieka.
- Przegląd świeżym okiem: zaproponuj Pawłowi nową, czystą rozmowę z jednym zdaniem zadania („obejrzyj planszę i arkusze klatek modelu X i znajdź błędy”) zamiast drugiego agenta.
- Uczciwie wypisuj, co zostało słabe. Zrzuty i filmy z Roblox Studio rób przy widocznym oknie Studio (zminimalizowane daje czarne zrzuty: python -B tools/studio_okno.py --przywroc).

ŻEBY NIE WEJŚĆ SOBIE W DROGĘ Z KAROLEM
- Przed każdą większą pracą (przebudowa modelu, mapa, budowa w Studio): git pull, a potem sprawdź, czy Karol nie robi tego samego — polecenie i zasady są w CLAUDE.md (sekcja o pracach w toku). Gdy prace się nakładają, zatrzymaj się i powiedz o tym Pawłowi.
- Nie przebudowuj modelu ani mapy, nad którymi właśnie pracuje druga osoba: pliki wynikowe są binarne i nie da się ich scalić.

WOLNO BEZ PYTANIA
- Edytować kod w swiat/ i tools/, renderować, przebudowywać modele, budować i usuwać własne kontenery w Studio.
- Wgrywać modele, animacje i tekstury na Roblox, póki gra jest w testach. Po każdym wgraniu zapisz w sejfie id zasobu, kto wgrał i kiedy.
- Commit i push na main po każdej skończonej i sprawdzonej zmianie (D-070). Przed commitem zmian w sejfie: python tools/sejf_lint.py.

NIE WOLNO
- Publikować miejsca, zmieniać Lighting, ruszać cudzych obiektów w Team Create (tylko kontenery z atrybutem Wygenerowane, punkt cofania przed i po).
- Ustawiać kanon albo ✅ i podpisywać decyzji bez wyraźnej zgody Karola albo Pawła.
- Force-push, commitować .env i klucze, edytować B&C/Źródła/ i plik .rbxl, używać płatnych generatorów i modeli z Marketplace.

PUŁAPKI
- Zasoby z konta Karola (np. Rycerz FBX) i z konta Pawła muszą być udostępnione grze albo wgrane na grupę (D-044).
- Gdy git push wisi na oknie logowania: git config --local credential.https://github.com.username <login Pawła>, potem push z GIT_TERMINAL_PROMPT=0 i GCM_INTERACTIVE=never.
- Wgrywanie przez Studio wymaga zgód w Assistant → Settings → MCP Permissions: asset:read/write i zatwierdzony folder swiat/postacie/wynik. To klika Paweł.
```

## Uwagi
- Wklejając prompt, Paweł sam zgadza się na wgrywanie na swoje konto Roblox i na automatyczny push ze swojego komputera. Zgoda Karola na wgrywanie dotyczy tylko komputera Karola.
- Liczby zużycia to pomiar pracy wieloma agentami u Karola. Zużycia jednego agenta na Sonnecie nikt jeszcze nie zmierzył — po pierwszym zadaniu Pawła warto dopisać tu wynik z `/usage`.
- Decyzja D-065 mówi, że postacie i pety projektuje Karol w Blenderze. Jeśli Paweł ma je robić na równi, warto to dopisać do D-065 — to decyzja ludzi.
- Powiązane: [[Postacie 3D — Blender i Roblox]], [[Klocki — Blender i Roblox]], [[Workflow i Git]], [[Panel zespołu]].
