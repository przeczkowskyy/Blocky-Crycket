---
status: propozycja
tags: [gra, miasteczko, mapa]
---
# Miasteczko — większy plac i Brama Leśna z kłódką (propozycja)

Źródło: polecenie Pawła w Claude Code, 2026-11-28. Nic z tej notatki nie jest zbudowane ani zatwierdzone. Miasteczko
buduje generator Karola (`swiat/miasteczko_bazar/`), więc budowa należy do jego strony — to jest plan i makieta do rozmowy.

## Makieta
- Obraz: `assets/raw/MiasteczkoMakieta/makieta_miasteczka.jpg` (Higgsfield, nano_banana_2_1, 1 wariant, na wzór referencji Pawła `ref_pawla_1–3.png` w tym samym folderze).
- Co pokazuje: szeroki plac ze studnią, wokół karczma, zbrojownia, sklep magiczny, Training Center ze szklanym dachem, tablica questów, portal krain, zagroda petów; mur miejski z basztami; Brama Leśna z kłódką wstawiona w mur, tuż za nią ścieżka do lasu.
- Styl: low poly jak na referencjach Pawła (proste bryły, mur pruski, kolorowe dachy, świecące okna). To zmiana wyglądu wobec dzisiejszej kreski miasteczka — do decyzji, patrz „Do ustalenia”.

## Podgląd stylu w Studio (28.11)
- Kontener `Workspace/MiasteczkoLowPolyPodglad` w wolnym miejscu mapy (976; 0; −500), obok miasteczka Karola: Karczma, Sklep magiczny, Zbrojownia, dom mieszczan, studnia, stragan, drzewa, latarnie — 638 części.
- Styl: kamienny parter pusty w środku (drzwi 5 × 7), piętro z muru pruskiego wysunięte nad parter, strome kolorowe dachy, świecące okna, gładkie kolory bez tekstur.
- To wycinek do oceny, nie przebudowa: wnętrza i NPC nie były przenoszone, plac ma rozmiar poglądowy.
- Źródło: `tools/studio/miasteczko_lowpoly_podglad.luau` (ponowne uruchomienie odbudowuje, usunięcie kontenera cofa). Propozycja D-168, pytanie 122 w [[Pytania otwarte]].

## 1. Plac większy o ok. 50%
- Plac szerszy mniej więcej o połowę; budynki zostają te same i stoją wokół niego frontem do środka.
- Do dopracowania modele: tablica questów, portal krain, zagroda petów.
- Budynki w stylu low poly z referencji, w układzie zbliżonym do dzisiejszego.

## 2. Brama Leśna z kłódką (pierwsze otwarcie)
1. Przy pierwszym wejściu na bramie wisi kłódka.
2. Gracz podchodzi i przytrzymuje E.
3. Kamera kinowa najeżdża na bramę; pojawia się klucz, wchodzi w kłódkę i przekręca się; kłódka spada.
4. Wrota otwierają się animacją; kamera wraca do gracza.
5. Brama zostaje otwarta na stałe dla tego gracza (zapis w profilu).

## 3. Przejście do lasu bez teleportu
- Las przysunięty do muru miasteczka i połączony z bramą: gracz przechodzi przez otwartą bramę pieszo.
- Dziś Brama Leśna stoi w (1052,5; −700), a przybycie do lasu jest w (1114; −700) — tych kilkudziesięciu studów gracz nie przechodzi, tylko jest przenoszony.

## Do ustalenia (Paweł i Karol)
- Czy całe miasteczko przechodzi na low poly, czy tylko bryły budynków zostają uproszczone w dzisiejszej kresce (D-147)?
- Czy przejście pieszo dotyczy tylko lasu, czy także bagna i dżungli (dziś przez portal krain i teleport)?
- Co z niewidzialnymi ścianami i ładowaniem lasu, gdy pas lasu styka się z murem (dziś każdy pas ładuje się osobno)?
- Kto buduje: generator miasteczka i pas lasu są po stronie Karola.

Powiązane: [[Dziennik zmian]], [[Zadania]].
