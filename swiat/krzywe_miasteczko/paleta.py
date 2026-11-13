# -*- coding: utf-8 -*-
"""Paleta mapy v2 „Krzywe Miasteczko” — jedyne źródło kolorów dla budynków i generatora miasta.

Kontrakt: swiat/krzywe_miasteczko/PROJEKT.md, rozdz. 2. Kolory wpisujesz kluczem (s.blok(..., "tynk_krem")).
Pas „cienia z klocka” (R23) = kolor ×0,82 — policz funkcją cien(): s.blok(..., cien(s, "tynk_krem")).
Status: propozycja (noc 13.11.2026), nie kanon.
"""

PALETA = {
    # tusz i tynki
    "tusz": "1D1916",
    "tynk_krem": "FFE6A8",
    "tynk_brzoskwinia": "FFCBA8",
    "tynk_mieta": "BDF0CB",
    "tynk_lawenda": "DCCBFF",
    "tynk_blekit": "C5D3F7",
    # drewno i kamień
    "drewno_ciemne": "5C3A22",
    "drewno": "8B5A2E",
    "drewno_jasne": "D49A5A",
    "kamien_cieply": "D6C6AC",
    "kamien_cokol": "6B5848",
    "kamien_lochu": "4A4560",
    # dachy = kod funkcji (jeden kolor na typ budynku)
    "dach_karczma": "D8452E",
    "dach_zbrojownia": "3F4E6E",
    "dach_sklep": "7B4FB5",
    "dach_wylegarnia": "1C9886",
    "dach_stajnia": "E2A93A",
    "dach_arena": "B8283A",
    "dach_gildia": "1E6E43",
    "dach_lochy": "7FBF3F",
    "dach_kolo": "D93A8C",
    "dach_twierdza": "2659B3",
    "dach_brama": "B84A18",
    "dach_dom_ceglasty": "A04E2C",
    "dach_dom_lupek": "5E5A78",
    # zieleń
    "trawa": "6DB33F",
    "lisc_jasny": "A8D84E",
    "lisc": "72BF3A",
    "lisc_ciemny": "3F8F35",
    "igla": "2F8A55",
    # grunt i woda
    "bruk": "E0C48E",
    "bruk_ciemny": "C9A66A",
    "ziemia": "C08A55",
    "woda": "2389D0",
    "woda_gleboka": "17589A",
    # akcenty i rekwizyty
    "zloto": "F2B030",
    "czerwien": "E5392B",
    "pomarancz": "F08A24",
    "biel": "FFF6E0",
    "metal_ciemny": "4A5368",
    # światło (tylko materiał Neon)
    "neon_okno": "FFB030",
    "neon_ogien": "FF6A1A",
    "neon_magia": "B85CFF",
    "neon_portal": "6CFF3A",
    "neon_slime": "2FF0E0",
}


def cien(s_albo_paleta, klucz, f=0.82):
    """Ciemniejsza wersja koloru (pas pod okapem, połać odwrócona od rynku): RRGGBB × f."""
    pal = getattr(s_albo_paleta, "paleta", s_albo_paleta)
    h = pal.get(klucz, klucz)
    return "%02X%02X%02X" % tuple(int(int(h[i:i + 2], 16) * f) for i in (0, 2, 4))
