# Uwagi programisty K (klient) — etap A

*15.11.2026. Kontrakt: `PROJEKT.md`. Ten plik opisuje tylko połowę kliencką, odczytania kontraktu i rzeczy do
uzgodnienia z połową serwerową. Wszystko napisane offline, bez Studio i bez uruchamiania Luau.*

## Co napisałem

| Plik | Co to jest |
|---|---|
| `zrodla/Stale.luau` | Stałe wspólne, przepisane z rozdz. 8.4 bez zmian (wycięte skryptem z bloku kodu kontraktu). |
| `sprawdz_luau.py` | Kontrola statyczna z rozdz. 8.8 (reguły 1–5) i samosprawdzenie `--test`. Można go też zaimportować (`sprawdz_pliki`). |
| `zrodla/KlientPotworow.client.luau` | Klient z rozdz. 4: tryb, wybór i budowa widoków, wygładzanie, grunt, obrót, klipy, tabliczka i miecze, podpowiedź E, panel bohatera, start walki w odtwarzaczu prototypu, odczyt wyniku, baner, haczyk `SterowanieKlienta`. |
| `zbuduj.py` | Budowa kontenera wg rozdz. 8.7; sprawdzony tylko tryb `--sucho`. |

## Odczytania kontraktu (najprostsze)

1. **Walka a wybór widoków.** W czasie walki (`Odtwarzacz.czyTrwa()`) wybór widoków i budowa stoją, a klipy nie są
   liczone. Kamera stoi wtedy przy arenie prototypu, ponad 2000 studów od lasu, więc reguła „najbliższe kamerze”
   zniszczyłaby wszystkie widoki, a po walce las budowałby się od nowa. Położenia widoków dalej idą za serwerem.
2. **Tabliczka.** Etykieta ma 76 × 30 px, ale `BillboardGui` ma 140 × 30 px: etykieta stoi na środku, a miecze 28 × 28
   obok niej w tym samym `BillboardGui`. Nie zakładam, że `BillboardGui` nie przycina potomków wystających poza brzeg.
3. **Tryb** wybrany po czekaniu na serwer już się nie zmienia (recenzja 15.11 wydłużyła czekanie z 15 do 40 s, bo serwer
   potrzebuje do 35 s, zanim powie, że lasu albo prototypu nie ma; w zwykłym przypadku czekanie trwa ok. 1 s). Gdy szablony przyjdą później, trzeba zatrzymać i uruchomić Play.
4. **Zły las.** Przy `StanBiomu = "brak_biomu"` albo `"zle_polozenie"` klient pokazuje jeden dymek (w ScreenGui
   `LasPotworyBaner`), ustawia `KlientTryb = "brak_biomu"` (wartość spoza listy z rozdz. 8.3) i nic więcej nie robi.
5. **Odtwarzacz wczytuję w osobnym wątku.** Jego zależności czekają `WaitForChild` bez limitu. Przy niepełnym
   prototypie `require` zawiesiłby cały klient; tak widoki działają, a podpowiedź mówi „Walka niedostępna”.
6. **Kamera po walce.** Odtwarzacz sam przywraca kamerę i sterowanie. Klient ma tylko zabezpieczenie: gdy 0,5 s po
   końcu sesji kamera jest nadal `Scriptable`, ustawia `Custom` i `CameraSubject` = Humanoid postaci.
7. **Podpowiedź** słucha `ProximityPrompt.Triggered` naszej podpowiedzi (kontrakt mówi `PromptTriggered`; skutek ten
   sam: tylko nasza podpowiedź, tylko `LocalPlayer`).
8. **Opcje odtwarzacza:** `OPCJE_WALKI = nil` (rozdz. 4.6). Po poprawce P2 wystarczy wpisać tam `{ bezPowtorki = true }`.
9. **Baner** po Strażniku ma stały tekst „Wróci za 2 min” (jak w kontrakcie; `odrodzenieS = 120` jest wartością testową).
10. **Dodatkowe atrybuty lokalne** (do testów, tylko u klienta): `KlientBledy` (liczba błędów w pętlach) i
    `KlientOstatniaWalka` (`"<id>/<wynik>"`). Haczyk `"stan"` zwraca dodatkowo `ukryte` i `bledy`.
11. **`zbuduj.py` przenosi atrybuty testowe** (`ZiarnoTestowe`, `TestBezSesji`, `TestGraczy`, `TestBezBiomu`) ze
    starego kontenera na odbudowany, żeby odbudowa nie kasowała ustawień testera. W trybie Studio wypisuje też
    zmierzone `Position`, `Size` i `Orientation.Y` Płyty (tylko odczyt).

## Do uzgodnienia z połową serwerową (S) i z recenzentem

- **Reguła 5 `sprawdz_luau.py`** szuka dosłownych napisów `SetAttribute("Gatunek", …)` itd. w
  `SerwerPotworow.server.luau`. Jeśli serwer ustawia atrybuty w pętli po tabeli nazw (`cfg:SetAttribute(nazwa, v)`),
  reguła zgłosi błąd, choć kod jest dobry. Kontrakt (8.8 p. 5) mówi o `SetAttribute("…")`, więc zostawiłem dosłowne
  dopasowanie; serwer powinien wołać `SetAttribute` z nazwą w cudzysłowie dla każdego z 9 atrybutów.
- **`zbuduj.py --sucho` przerywa (kod 2), dopóki nie ma `zrodla/SerwerPotworow.server.luau`.** Sprawdziłem go na kopii
  pakietu w notatniku z zaślepką serwera: przechodzi (`generuj_dane.py --sprawdz` kod 0, `sprawdz_luau` 5 plików OK,
  12 modułów i skryptów, skrót danych z `DanePotworow`). Negatywna próba (serwer bez `Pozycja`) daje 2 błędy reguły 5.
- **Wymiary wilka w `DanePotworow`** to `{ 7.7, 4.4, 7.7 }` (generator bierze brakujący wymiar poziomy z drugiego).
  Klient używa ich tylko dla bryły zastępczej, więc wilk w trybie zastępczym jest kwadratowym klockiem 7,7 × 7,7.
  To kosmetyka; bramka E używa `promien` = 3,85 i zgadza się z kontraktem.
- **Odczyt `OstatniWynik`.** Klient czyści go lokalnie przed walką i czyta, gdy `czyTrwa()` zwróci `false`. Po
  JESZCZE RAZ po wygranej (odmowa `zly_wybor`) atrybut nadal ma „wygrana” z pierwszej walki, więc potwór i tak zostaje
  ukryty — to zgodne z intencją rozdz. 4.6.

## Czego nie jestem pewien (sprawdzić w Studio)

- Czy dwa `UIStroke` na jednym `TextButton` (ramka `Border` i litery `Contextual`, przycisk GOTOWE) działają naraz.
  Gdy nie, zostaje jeden z obrysów — tylko wygląd.
- Czy dzieci obróconej ramki `Frame` (jelec miecza) obracają się razem z nią. Gdy nie, jelce będą poziome — tylko wygląd.
- Czy lokalna `ProximityPrompt` na lokalnej części działa z E i stuknięciem na telefonie (ryzyko z rozdz. 10).
- Czy `Klipy.nowy` na klonie z `ReplicatedStorage` znajduje wszystkie kości (klon w ReplicatedStorage robi serwer;
  zakładam pełną kopię). Błąd budowy gatunku → ten gatunek pokazuje się jako bryła i jeden `warn`.
- Kolejność replikacji: zakładam, że `SzablonyGotowe = true` przychodzi do klienta po folderze szablonów (klient i
  tak czeka na każdy model do 5 s).
