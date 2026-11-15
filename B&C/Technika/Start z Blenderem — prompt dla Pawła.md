---
status: propozycja
tags: [technika, blender, 3d, pipeline, wdrozenie]
---
# Start z Blenderem — prompt dla Pawła

> [!info] W skrócie
> Wiedza o modelach nie siedzi w Blenderze, tylko w repozytorium: postacie, pety, ekwipunek i mapy powstają **z kodu Pythona**, który Claude uruchamia w Blenderze. Żeby Paweł robił modele tak samo jak Karol, wystarczy zainstalować cztery rzeczy i wkleić poniższy prompt do Claude Code otwartego w folderze repozytorium. Przygotował Claude na prośbę Karola 15.11.2026 (rozmowa w panelu, okno Modele).

## Co zainstalować (Windows)
1. **Blender 5.0** — z blender.org, do domyślnego folderu `C:\Program Files\Blender Foundation\`. Skrypty biorą najnowszą wersję z tego folderu; inną ścieżkę podaje się w zmiennej `BLENDER_EXE`. U Karola działa dokładnie wersja 5.0.
2. **ffmpeg** — w terminalu: `winget install Gyan.FFmpeg`, potem nowe okno terminala i `ffmpeg -version` na próbę.
3. **Python 3.12 lub nowszy** (python.org, zaznaczyć „Add to PATH”), potem: `pip install pillow requests python-dotenv`.
4. **Roblox Studio jako serwer MCP** — w Studio: Assistant → Manage MCP Servers → Enable Studio as MCP server. Do wgrywania modeli dodatkowo: Assistant → Settings → MCP Permissions → zakresy asset:read i asset:write oraz zatwierdzony folder `swiat/postacie/wynik`.

Potem: `git pull` w repozytorium, Claude Code w tym folderze i wklejony prompt. Czego zabraknie, Claude Pawła sam wypisze i doinstaluje.

## Skąd bierze się jakość
- **Kod zamiast ręcznego modelowania.** Każda postać to jeden plik w `swiat/postacie/`, każda mapa to `generuj.py`. Te same pliki dają u Pawła te same modele co u Karola.
- **Stały proces.** Projekt z liczbami → budowa → rendery i filmy → **niezależny przegląd świeżym okiem** (osobny agent ogląda obrazy i szuka błędów) → poprawki → raport w panelu do akceptacji.
- **Wspólny styl.** Style Lock, kierunek artystyczny i biblioteka brył w repozytorium.
- Czego prompt nie przeniesie: pamięci Claude'a Karola, pliku `.env` z kluczami, zgód w Studio i trybu uprawnień Claude Code — to Paweł ustawia u siebie.

## Prompt (wkleić w całości)
```
Pracujesz w repozytorium gry Roblox BLOCKY & CRYCKET z Pawłem (Game Director). Działasz tak samo jak Claude Code Karola, który robi postacie, pety, ekwipunek i mapy w Blenderze: samodzielnie, bez pytania o każdy krok i bez czekania na potwierdzenie.

NA START (sam, od razu)
1. git pull na main.
2. Przeczytaj i stosuj: CLAUDE.md, B&C/00 Start.md, B&C/Jak prowadzimy sejf.md, B&C/Produkcja/Rejestr decyzji.md, B&C/Produkcja/Pytania otwarte.md, B&C/Technika/Postacie 3D — Blender i Roblox.md, B&C/Technika/Klocki — Blender i Roblox.md, B&C/Styl/Style Lock.md, B&C/Styl/Kierunek artystyczny.md, swiat/postacie/README.md, swiat/postacie/EKWIPUNEK.md, swiat/postacie/biblioteka/README.md, swiat/krzywe_miasteczko/PROJEKT.md, swiat/biom_las/PROJEKT.md, swiat/biom_las/README.md, .claude/skills/panel/SKILL.md, .claude/skills/asset/SKILL.md.
3. Sprawdź środowisko: Blender 5.0 (C:\Program Files\Blender Foundation\ albo zmienna BLENDER_EXE), ffmpeg w PATH, Python z Pillow, Roblox Studio przez MCP (python tools/studio_mcp.py studios). Czego brakuje, doinstaluj sam. Czego nie da się zrobić z terminala, podaj Pawłowi w najwyżej trzech krokach.
4. Próba działania, wyniki do folderu poza repozytorium: python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rycerz.py --wyj <folder> --klip chod oraz python swiat/biblioteka/podglad.py --json swiat/biom_las/czesci.json --ujecia swiat/biom_las/ujecia_swiat.json --wyj <folder> --tylko l03. Obejrzyj wyniki sam, zanim powiesz, że działa.
5. Zapisz zasady z tego promptu w swojej pamięci, żeby obowiązywały w kolejnych rozmowach.
6. Zgłoś Pawłowi w pięciu punktach: co działa, czego brakuje, co zrobiłeś.

JAK TU SIĘ PRACUJE
- Źródłem prawdy jest kod .py, nie plik .blend. Blender działa w tle i robi siatki (FBX/GLB), filmy, ikony i raport. Zmiana = edycja modułu, potem python -B swiat/postacie/przebuduj.py <moduł> i zestawienie.py. Jeden proces Blendera naraz.
- Dwie drogi do Robloxa: postać z klocków (części i Motor6D, roblox_postac.py, bez wgrywania) i siatka z Blendera (roblox_import.py, wgrywanie na konto). Postacie i pety głównie siatką (D-065; pytanie 24 jeszcze otwarte), mapy i budynki z klocków (D-017, D-025).
- Mapy: swiat/<scena>/generuj.py → czesci.json → Blender (tools/blender/klocki.py), Studio (tools/studio_buduj.py) i podgląd w panelu. Faktury map tylko z wbudowanych materiałów Roblox (wzór: swiat/biom_las/faktury.py).
- Ekwipunek jest widoczny na postaci, modele bazowe są bez stroju, a strój to przedmioty zakładane na model (D-071, swiat/postacie/EKWIPUNEK.md, wspólny kod w swiat/postacie/ekwipunek.py).
- Po wdrożeniu czegoś do oceny: migawka i raport w panelu (skill panel), z obrazami. Panel działa u Karola; Paweł wchodzi przez link, własnego nie uruchamiaj.

JAKOŚĆ (tak samo jak u Karola)
- Każdy model i każda mapa przechodzą ten sam tor: projekt z liczbami (PROJEKT.md albo opis w module) → budowa → rendery, plansza, filmy klipów → niezależny przegląd świeżym okiem na obrazach (osobny agent, który ma znaleźć błędy, nie potwierdzić sukces) → poprawki → raport do akceptacji człowieka.
- Sam oglądaj obrazy i klatki filmów; liczby z testów nie zastępują patrzenia. Uczciwie wypisuj, co zostało słabe.
- Przy większych pracach używaj kilku agentów (wykonanie, wroga kontrola, poprawki), jeśli Paweł włączył taką możliwość.
- Zrzuty i filmy z Roblox Studio rób przy widocznym oknie Studio: zminimalizowane okno daje czarne zrzuty (python -B tools/studio_okno.py --przywroc).

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
- Decyzja D-065 mówi, że postacie i pety projektuje Karol w Blenderze. Jeśli Paweł ma je robić na równi, warto to dopisać do D-065 — to decyzja ludzi.
- Powiązane: [[Postacie 3D — Blender i Roblox]], [[Klocki — Blender i Roblox]], [[Workflow i Git]], [[Panel zespołu]].
