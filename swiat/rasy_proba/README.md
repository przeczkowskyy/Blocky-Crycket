# Wystawa ras w grze (D-104, etap B) — `swiat/rasy_proba`

> **Sprzątanie mapy 26.11.2026 (zlecenie Karola):** kontener `Workspace/RasyProba` **usunięty z miejsca** (stał przy starym starcie). Źródła zostają. **Uwaga dla wdrożenia wyboru klasy Pawła:** `tools/studio/deploy_classselect.py` kopiuje figury ras z `Workspace/RasyProba` do `ReplicatedStorage/WyborKlasyModele/Race_*` — przed takim wdrożeniem trzeba postawić wystawę (`python -B swiat/rasy_proba/zbuduj.py`), a po nim można ją znów usunąć (`python -B tools/studio/sprzatanie_mapy.py --tylko RasyProba`). Już wdrożone kopie w `ReplicatedStorage` działają bez wystawy. Próba „rasy” wypadła z `swiat/przejscie_gry/regresja_calosci.py`.

> **Status: propozycja.** Figury do obejrzenia w grze — nic nie jest podpięte do walki, bohatera gracza ani ekranu
> wyboru (to czeka na decyzje ludzi: proporcje ras, Mag jest kotem). Modele i pytania: `swiat/postacie/RASY.md`.

## Co stoi w Studio
Własny kontener `Workspace/RasyProba` (atrybut `Wygenerowane = true`): siedem figur z części Roblox — człowiek
(goły Rycerz, dla porównania) i sześć ras: elf, mroczny elf, ork, demon, goblin, półbóg. Bez wgrywania czegokolwiek:
to te same dane, z których Blender robi siatki, rozłożone na części `Part` / `WedgePart` / `CornerWedgePart`
(`swiat/postacie/biblioteka/roblox_klocki.py`, ta sama droga co `swiat/postacie/roblox_postac.py`).

- **Miejsce:** plac przed płytą startu, szpaler po obu stronach drogi do gospody, 14–25 studów od startu, twarzami
  do płyty startu. Gracz po wejściu do gry patrzy w tę stronę. Po lewej stronie drogi (patrząc od startu) stoją
  człowiek, elf, mroczny elf i ork, po prawej demon, goblin i półbóg; środek (8,5 studa) zostaje wolny. Współrzędne
  są w `ustawienia.json` (`figury[].poz`), wysokość ziemi budowniczy mierzy promieniem w dół.
- **Figura:** `Model` o nazwie rasy (`elf`, `ork`…): zakotwiczony `HumanoidRootPart`, niewidzialna część na każdą
  z 15 kości R15, stawy `Motor6D`, bryły przyspawane do kości, `AnimationController` z `Animatorem`, część
  `Tabliczka` z nazwą rasy nad najwyższym punktem (`BillboardGui`). Żadna część nie ma kolizji, dotyku ani promieni
  (`CanCollide`, `CanTouch`, `CanQuery` = false), więc figury nie blokują przejścia ani podpowiedzi E.
- **Skala rasy** jest w geometrii figury (`rasy.w_skali`): ork 1,08, goblin 0,88, reszta 1,00. Stopy stoją na ziemi.
- **Świecenie:** oczy demona i półboga oraz aureola to części z materiałem `Neon`.
- **Spoczynek:** skrypt `SpoczynekRas` (zaczyna od strażnika `RunService:IsStudio()`) tworzy w Play jedną wspólną,
  trzyklatkową sekwencję oddechu (ok. 20 obiektów) i puszcza ją na Animatorze każdej figury. Kąty i okres:
  `ustawienia.json` → `spoczynek`. To nie są klipy z Blendera (te miałyby po kilkaset obiektów klatek na figurę).
  `RegisterKeyframeSequence` działa tylko w Studio — w opublikowanej grze figury stałyby nieruchomo.

| Figura | Skala | Wzrost (czubek głowy) | Bryły | Części w Studio | Świecące |
|---|---|---|---|---|---|
| człowiek (goły Rycerz) | 1,00 | 5,30 | 74 | 91 | 0 |
| elf | 1,00 | 5,30 | 143 | 160 | 0 |
| mroczny elf | 1,00 | 5,30 | 143 | 160 | 0 |
| ork | 1,08 | 5,72 | 93 | 110 | 0 |
| demon | 1,00 | 5,30 | 75 | 92 | 4 |
| goblin | 0,88 | 4,66 | 71 | 88 | 0 |
| półbóg | 1,00 | 5,30 | 78 | 95 | 16 |
| **razem** | | | 677 | **796** | 20 |

„Części w Studio” = bryły + 15 części kości + korzeń + tabliczka. Liczbę brył podnosi rozkład ostrosłupów (uszy,
szpice włosów) na kliny.

## Jak zbudować, sprawdzić i usunąć
```
python -B tools/studio_mcp.py studios                         # Studio musi być w trybie Edit
python -B swiat/rasy_proba/zbuduj.py --sucho                  # policz i sprawdź źródła, bez Studio
python -B swiat/rasy_proba/zbuduj.py                          # zbuduj od nowa Workspace/RasyProba (poniżej minuty)
python -B swiat/rasy_proba/zbuduj.py --stan                   # odczyt: co stoi w kontenerze
python -B swiat/rasy_proba/zbuduj.py --usun                   # usuń własny kontener
python -B swiat/rasy_proba/testy/test_rasy_proba.py           # test danych bez Studio (kilka sekund)
python -B swiat/rasy_proba/sprawdz_luau_ras.py                # kontrola statyczna źródeł Luau
python -B swiat/rasy_proba/testy/proba_play.py <folder poza repo> [--bez-zrzutow]   # próba w grze (ok. 40 s)
```

Budowniczy: sprawdza miejsce gry (numer z `swiat/test_walki_roblox/cel_studio.py`) i tryb Edit, przed budową
sprawdza, czy miejsca figur są wolne (pudło nad ziemią bez cudzych części — inaczej STOP i nic nie zmienia), rusza
wyłącznie własny kontener, stawia punkty historii przed budową i po niej, niczego nie zapisuje, nie publikuje i nie
dotyka `Lighting`. Cudzy obiekt o nazwie `RasyProba` (bez atrybutu `Wygenerowane`) zatrzymuje budowę i usuwanie.
Przed publikacją gry kontener trzeba usunąć (`--usun`).

## Pliki
| Plik | Co to |
|---|---|
| `ustawienia.json` | kontener, miejsca figur, tabliczka, kąty oddechu, progi i kamery próby |
| `dane.py` | figury jako rigi z części Roblox (rasa w skali rasy, człowiek = goły Rycerz) |
| `zbuduj.py` | budowniczy (`--sucho`, `--stan`, `--usun`) i odczyt stanu wystawy |
| `zrodla/SpoczynekRas.server.luau` | oddech figur w Play (tylko Studio) |
| `sprawdz_luau_ras.py` | kontrola statyczna Luau (reguły z `swiat/las_potwory/sprawdz_luau.py`) |
| `testy/test_rasy_proba.py` | test bez Studio: dane figur = dane ras, skala, miejsce, nazwy, źródła, budowniczy |
| `testy/proba_play.py` | próba w grze R00–R09; wynik i konsola idą do folderu poza repozytorium |
| `klatki/` | zrzuty z gry (bez interfejsu, listy graczy i nazwy nad postacią) |

## Wynik próby w grze (18.11.2026, 13:47, okno Studio na wierzchu)
| Punkt | Wynik | Co wyszło |
|---|---|---|
| R00 Edit: kontener, figury, części | OK | 7 figur, 796 części, skrypt spoczynku jest |
| R01 Play: skala, wzrost, stopy | OK | wzrost 5,30 / 5,72 (ork) / 4,66 (goblin); stopy 0,000 studa od ziemi |
| R02 brak kolizji z graczem | OK | żadna z 796 części nie ma kolizji, dotyku ani promieni; postać upuszczona na orka i półboga przelatuje i staje na ziemi |
| R03 tabliczki | OK | „Człowiek”, „Elf”, „Mroczny elf”, „Ork”, „Demon”, „Goblin”, „Półbóg” |
| R04 spoczynek | OK | oddech gra na 7 figurach; u klienta głowa rusza się o 0,04–0,06 studa |
| R05 świecenie | OK | części Neon: demon 4, półbóg 16 |
| R06 konsola | OK | bez błędów i ostrzeżeń pakietu |
| R07 czas klatki | OK | 16,7 ms z kamerą na wystawę (najdłuższa klatka 18,3 ms), 16,7 ms z kamerą odwróconą; próg 34 ms |
| R08 zrzuty | OK | cztery zrzuty w `klatki/` |
| R09 powrót do Edit | OK | Studio po próbie w trybie Edit |

Po ostatniej przebudowie (13:50) ta sama próba bez zrzutów: 9 OK, zrzuty pominięte, Studio w trybie Edit.
Próba całej drogi gracza z wystawą na placu (`swiat/przejscie_gry/regresja_calosci.py <folder> "proba dymna"`,
13:47–13:49): 13 z 13 punktów OK, bez błędów w konsoli.

Zrzuty: `klatki/wystawa_widok_gracza.jpg` (widok znad płyty startu), `wystawa_lewa_grupa.jpg` (człowiek, elf,
mroczny elf, ork), `wystawa_prawa_grupa.jpg` (demon, goblin, półbóg), `wystawa_z_boku.jpg`.

## Czego nie sprawdzono i co odbiega
- Figury są z klocków: ostre krawędzie, stożki schodkowe, bez obrysu z renderów Blendera; emisja z tekstur jest
  tu zastąpiona materiałem Neon.
- Czas klatki mierzony na komputerze autora przy limicie 60 kl./s; telefonu nie mierzono.
- Ławka z placu stoi między człowiekiem a płytą startu i częściowo go zasłania, gdy patrzy się z płyty startu.
- Oddech jest wspólny i umowny (tułów 2°, głowa 2°, ręce 4°); klipy idle, chód i wiwat z Blendera nie są wgrane.
- Wystawa nie zna strojów: figury stoją w stroju bazowym; przymiarek kompletów w grze nie ma.
- W opublikowanej grze nie sprawdzano niczego — skrypt i tak kończy się tam na strażniku, a kontener ma zniknąć.
