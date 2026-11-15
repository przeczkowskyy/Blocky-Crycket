# -*- coding: utf-8 -*-
"""Paleta biomu Las „Bór Pod Ukłonem” — paleta miasteczka bez zmian plus 15 kolorów lasu.

Kontrakt: swiat/biom_las/PROJEKT.md, rozdz. 9. Kolory wpisujesz kluczem (s.blok(..., "runo")).
Klucze miasteczka (tusz, trawa, lisc, bruk, woda, neon_* …) znaczą to samo co w miasteczku — nie zmieniamy ich.
Pomocnicze: cien(s, klucz) jak w miasteczku, lstar(klucz) = walor 0–100, kontrast(a, b) = WCAG (1–21).
Status: propozycja (15.11.2026), nie kanon.
"""
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko.paleta import PALETA as PALETA_MIASTECZKA, cien  # noqa: E402,F401

KOLORY_LASU = {
    # grunt i runo
    "runo": "4E9A3A",            # grunt boru (Serce, Ostępy); ścieżka bruk na nim ΔL* ≈ 23
    "runo_ciemne": "2F6E35",     # wilgotny grunt Kapeluszowa i pod jeżynami; tło dla czerwonych kapeluszy
    "mech": "8CC63F",            # czapy mchu na głazach (zawsze z podkładką cien pod spodem)
    "galareta": "7FE04A",        # kałuże galarety, z których wyskakują slime'y (nie Neon)
    # korona Starego Ukłonu (jedyna ciepła plama na mapie z góry)
    "lisc_rudy": "E8782A",
    "lisc_miodowy": "F2B83A",
    "lisc_rdza": "B8502A",
    # Cierniste Ostępy
    "jezyna": "4B3A6B",          # pędy i ściany jeżyn (ciemny walor)
    "jezyna_kolec": "F3E6C8",    # kolce — jasne na ciemnym, czyta się jak odwrócony tusz
    # woda i brzegi
    "trzcina": "9CC24A",
    # kulisy na obrzeżach: trzy rzędy jaśniejące ku horyzontowi (perspektywa powietrzna), bez tuszu
    "sylweta_1": "3F7F4A",
    "sylweta_2": "6FA77A",
    "sylweta_3": "A9CDB0",
    # światło (tylko materiał Neon)
    "neon_zarodnik": "C8FF3A",   # zarodniki Kapeluszowa
    "neon_swietlik": "FFE36A",   # świetliki w koronie Ukłonu
}

PALETA = dict(PALETA_MIASTECZKA)
for _k, _v in KOLORY_LASU.items():
    assert _k not in PALETA, "klucz lasu zderza się z kluczem miasteczka: " + _k
    PALETA[_k] = _v

# kod koloru podbiomu: kamienie-kody przy ścieżkach, chorągiewki, ramiona drogowskazów (rozdz. 5 i 8)
KOD_PODBIOMU = {
    "laka": "zloto",
    "kapeluszowo": "czerwien",
    "serce": "pomarancz",
    "ostepy": "dach_sklep",
    "wawoz": "dach_brama",
    "korona": "biel",
}


def _rgb(h):
    h = PALETA.get(h, h)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancja(klucz):
    r, g, b = (_lin(c) for c in _rgb(klucz))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lstar(klucz):
    """Walor L* (CIELAB, 0–100) koloru z palety albo RRGGBB."""
    y = luminancja(klucz)
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16


def kontrast(a, b):
    """Kontrast WCAG dwóch kolorów (1–21); stykające się duże płaszczyzny wymagają ≥ 3."""
    la, lb = luminancja(a), luminancja(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for k, v in KOLORY_LASU.items():
        print("%-14s %s  L* %5.1f" % (k, v, lstar(k)))
