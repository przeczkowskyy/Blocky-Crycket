# -*- coding: utf-8 -*-
"""Przeróbki modeli NA POTRZEBY PROTOTYPU WALKI v2 — tylko w pamięci, pliki modeli w swiat/postacie/ zostają bez zmian.

Każda funkcja dostaje gotową postać (Postac z modułu modelu) i dokłada to, czego aktorowi brakuje do walki:
- Zwiadowca: skupienie (jedyna umiejętność bez klipu w modelu).
Wojownik (Rycerz) i Mag (Kot-Mag) od 15.11 (etap 8) grają własne klipy walki z modułów rycerz.py i kot_mag.py —
szkice z tego pliku (tarcza prototypu na TarczaAttachment, blok, unik, trafienie, upadek, cięcie, miażdżący cios,
kamienna skóra; atak Maga, kula ognia, lodowy pocisk, bariera, radość) usunięte: każdy z tych klipów jest w module,
a tarcza jest przedmiotem modułu (strój „bojowy”, D-071). Leśny Slime i Strażnik Gaju (15.11) grają właściwe modele
z własnymi klipami — bez przeróbek (wcześniejsze modele zastępcze: przemalowany slime-pet i powiększony troll, usunięte).
Klipy zastępcze są szkicami (kilka póz kluczowych), oznaczone w tabeli aktorów polem „zastepcze_klipy”.

Konwencje biblioteki (swiat/postacie/biblioteka/README.md): postać patrzy w +Z, lewa strona +X; rx < 0 unosi rękę
do przodu, rz > 0 odchyla w stronę +X, ry > 0 skręca przód w stronę +X; przes w osiach modelu (mnożone przez skalę).
"""


def _poza_z(baza, **zmiany):
    w = dict(baza)
    w.update(zmiany)
    return w


def _idle0(p, klip="idle"):
    """Poza z klatki 0 klipu spoczynku modelu: {kość: {"obrot": …, "przes": …}} — klipy zastępcze zaczynają się
    i kończą w niej, więc przejście z i do spoczynku jest płynne (broń zostaje w tym samym chwycie)."""
    k = next(k for k in p.klipy if k.nazwa == klip)
    poza = {}
    for (kosc, kanal) in k.kanaly:
        if kanal != "skala":
            poza.setdefault(kosc, {})[kanal] = tuple(round(v, 3) for v in k.wartosc(kosc, kanal, 0))
    return poza


# --------------------------------------------------------------------------- Zwiadowca
def zwiadowca(p):
    # skupienie: przyklęk, łuk pionowo przed twarzą, głowa pochylona — chwila skupienia i powrót
    baza = _idle0(p)
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0),
            "LeftUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0), "RightLowerLeg": (0, 0, 0)}
    start = dict(zero, **baza)
    k = p.klip("skupienie", 44, petla=False)
    k.poza(0, start)
    skup = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, -0.45, 0)}, "UpperTorso": (12, 0, 0), "Head": (22, 0, 0),
            "LeftUpperArm": (-70, 0, -25), "LeftLowerArm": (-70, 0, 0), "LeftHand": (0, 0, 0),
            "RightUpperArm": (-40, 0, 30), "RightLowerArm": (-60, 0, 0),
            "LeftUpperLeg": (-60, 0, 0), "LeftLowerLeg": (70, 0, 0), "RightUpperLeg": (10, 0, 0), "RightLowerLeg": (70, 0, 0)}
    k.poza(10, skup)
    k.poza(32, _poza_z(skup, Head=(16, 0, 0), UpperTorso=(8, 0, 0)))
    k.poza(44, start)


PRZEROBKI = {"zwiadowca": zwiadowca}
