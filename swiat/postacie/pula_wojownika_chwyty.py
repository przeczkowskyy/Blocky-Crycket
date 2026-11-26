# -*- coding: utf-8 -*-
"""PULA WOJOWNIKA — plansze do oceny przez ludzi (26.11.2026). Status: propozycja.

1. „Chwyty” (Karol: „odróżniaj różdżkę od miecza i łuk itd.”): goły kot-wojownik trzyma po jednym przykładzie
   każdego rodzaju chwytu z swiat/postacie/chwyty.py — miecz (Miecz Giermka), różdżka (ATRAPA), drzewce (kostur
   Kota-Maga), proca (proca startowa w proporcjach kota), łuk (łuk Zwiadowcy w proporcjach kota), tarcza (tarcza
   Rycerza ×0,6), księga (ATRAPA). Każdy rodzaj z przodu i 3/4.
2. „Hełm z osłonami uszu” (wariant do porównania, Paweł: „hełmy mają zasłaniać kocie uszy”): kot w Zestawie
   Giermka z hełmem zestawu (duża kopuła mieści uszy) obok wariantu z dawną niską kopułą i dwiema stalowymi
   osłonami w kształcie kocich uszu (sylwetka kota zostaje). Wariant nie jest w zestawie.

    python -B swiat/postacie/przebuduj.py pula_wojownika_chwyty --bez-filmow

Same plansze (EKSPORT_MODELI = False): wynik/pula_wojownika_chwyty/<id>_plansza.jpg i _bohater.jpg każdej postaci,
a po przebudowie zbiorcze wynik/_pula_wojownika/<prefiks>chwyty.jpg i <prefiks>helm_uszy_porownanie.jpg.
Widok „przód” to ta sama postać obrócona o kąt kamery kadru bohaterskiego (blender_postac.BOHATER), tylko w kadrze.
"""
import copy
import math
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import chwyty as CH  # noqa: E402
from swiat.postacie import pula_wojownika as PW  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium  # noqa: E402
from swiat.postacie.ekwipunek import Przedmiot, ubierz  # noqa: E402

ID = "pula_wojownika_chwyty"
FILMY = []
EKSPORT_MODELI = False
# kąt kamery kadru bohaterskiego w poziomie: kierunek (0,5; 0,16; 1,0) z blender_postac.BOHATER
KAT_KADRU = math.degrees(math.atan2(0.5, 1.0))
KOLEJNOSC = ("miecz", "rozdzka", "drzewce", "proca", "luk", "tarcza", "ksiega")
PODPISY = {"miecz": "miecz — Miecz Giermka", "rozdzka": "różdżka — ATRAPA", "drzewce": "drzewce — kostur Kota-Maga",
           "proca": "proca — proca startowa (kot)", "luk": "łuk — łuk Zwiadowcy (kot)",
           "tarcza": "tarcza — tarcza Rycerza ×0,6", "ksiega": "księga — ATRAPA"}
SLABOSCI = [
    "Plansza propozycji: rodzaje chwytu i ich korekty kota (chwyty.py) czekają na ocenę ludzi.",
    "Różdżka i księga to atrapy (nie ma ich modeli); łuk, proca i tarcza to modele ludzkich bohaterów i broni "
    "startowej przeskalowane na kota tylko do tej planszy.",
    "Lewa łapa kota nie ma kości nośnej (jak StaffPivot w prawej): łuk, tarcza i księga w upadku zostają w łapie.",
    "Klipy kota są pisane pod kostur; inne rodzaje broni sprawdzone liczbowo tylko dla mieczy puli (--przenikanie).",
    "Widok z przodu to postać obrócona w kadrze (klip „kadr_przod”, jedna klatka), nie osobna kamera.",
]
PALETA_ATRAP = {"drewno": "6E4423", "drewno_jasne": "A9743F", "gwiazda": "F7D24A", "okladka": "8E2A2A",
                "okladka_ciemna": "5E1A1A", "kartki": "F2E6C8", "zloto": "E8B93A"}


def _rozdzka():
    """ATRAPA różdżki (nie ma modelu): rączka w pięści, cienki pręt, świecąca gwiazdka na czubku; oś +Y."""
    a = Akcesorium("atrapa_rozdzka", "Różdżka (atrapa)", zaczep="RightGripAttachment", typ="Bron",
                   paleta=PALETA_ATRAP, ikona_obrot=(0, 0, -40), chwyt="rozdzka")
    a.walec("Raczka", (0, 0.06, 0), (0.14, 0.44, 0.14), "drewno", "matowy")
    a.walec("Pret", (0, 0.6, 0), (0.08, 0.66, 0.08), "drewno_jasne", "matowy")
    a.blok("Gwiazdka", (0, 0.98, 0), (0.2, 0.2, 0.06), "gwiazda", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return a


def _ksiega():
    """ATRAPA księgi (nie ma modelu na kota): zamknięta, wisi pod lewą łapą trzymana za górną krawędź; osie dłoni
    jak tarcza Rycerza (blok uklad(−90, 0, 0)); okładka skręcona 35° ku przodowi."""
    a = Akcesorium("atrapa_ksiega", "Księga (atrapa)", zaczep="LeftGripAttachment", typ="Bron", paleta=PALETA_ATRAP,
                   ikona_obrot=(0, -60, 0), chwyt="ksiega")
    with a.uklad(obrot=(-90, 0, 0)):
        with a.uklad(obrot=(0, -35, 0)):
            a.blok("Okladka", (0.02, -0.4, 0), (0.18, 0.7, 0.56), "okladka", "matowy", faza=0.03)
            a.blok("Kartki", (0.02, -0.4, 0.27), (0.13, 0.64, 0.04), "kartki", "matowy", faza=0.0)
            a.blok("Grzbiet", (0.02, -0.4, -0.28), (0.21, 0.72, 0.05), "okladka_ciemna", "matowy", faza=0.0)
            a.blok("Godlo", (0.12, -0.4, 0.02), (0.03, 0.2, 0.2), "zloto", "metal", rot=(45, 0, 0), faza=0.0)
    return a


def bronie():
    """{rodzaj: Akcesorium} — po jednym przykładzie każdego rodzaju chwytu (świeże obiekty)."""
    from swiat.postacie import bronie_startowe as BS
    from swiat.postacie import rycerz, zwiadowca
    w = {"miecz": PW.przedmioty("giermek")[PW.RZECZY.index("miecz")].segmenty[0]["akc"],
         "rozdzka": _rozdzka()}
    k = PW.KM.kostur()
    k.chwyt = "drzewce"
    w["drzewce"] = k
    pr = BS.kocia(BS.proca())
    pr.chwyt = "proca"
    w["proca"] = pr
    lk = BS.kocia(zwiadowca.luk(), dl=0.55, gr=1.0)
    lk.chwyt = "luk"
    w["luk"] = lk
    tr = rycerz.tarcza()
    tr.id, tr.skala, tr.chwyt = "rycerz_tarcza_kot", 0.6, "tarcza"
    w["tarcza"] = tr
    w["ksiega"] = _ksiega()
    for r, a in w.items():
        if a.chwyt != r:
            raise ValueError("%s: rodzaj chwytu %r, a powinien być %r" % (a.id, a.chwyt, r))
    return w


def _tylko_idle(p):
    p.klipy = [k for k in p.klipy if k.nazwa == "idle"]
    return p


def _przod(p):
    """Kopia postaci do widoku z przodu: klip „kadr_przod” = klatka 0 idle z biodrami obróconymi o kąt kamery kadru
    bohaterskiego (postać patrzy prosto w kamerę), ustawiony jako poza renderu."""
    q = copy.deepcopy(p)
    q.id, q.nazwa = p.id + "_przod", p.nazwa + " (przód)"
    idle = next(k for k in q.klipy if k.nazwa == "idle")
    k = q.klip("kadr_przod", 1, petla=False)
    for n in q.kosci:
        ob = idle.wartosc(n, "obrot", 0)
        pr = idle.wartosc(n, "przes", 0)
        if n == "LowerTorso":
            ob = (ob or (0.0, 0.0, 0.0))
            ob = (ob[0], ob[1] + KAT_KADRU, ob[2])
        for f in (0, 1):
            if ob is not None or pr is not None:
                k.klucz(f, n, obrot=ob, przes=pr)
    q.ustaw_poze_renderu("kadr_przod", 0)
    return q


def postacie_chwytow():
    """Goły kot-wojownik z jedną bronią każdego rodzaju (przez ubierz() z korektami kota) — [(rodzaj, postać)]."""
    wynik = []
    for r, a in sorted(bronie().items(), key=lambda kv: KOLEJNOSC.index(kv[0])):
        prz = Przedmiot("chwyt_" + r, a.nazwa, "Weapon", "Weapons", PW.MIARA, cialo=PW.KM.CIALO_TYP)
        prz.na_zaczepie(a)
        p = ubierz(PW.cialo(), [prz], id="%s_%s" % (ID, r), nazwa="Kot-wojownik — chwyt: %s" % r,
                   korekty=PW.KOREKTY_CHWYTU)
        wynik.append((r, _tylko_idle(p)))
    return wynik


def postacie_helmow():
    """Kot w Zestawie Giermka: hełm zestawu (duża kopuła) i wariant z osłonami uszu — [(klucz, postać)]."""
    prz = PW.przedmioty("giermek")
    duzy = PW.postac("giermek", id=ID + "_helm_kopula", prz=prz, tylko_idle=True)
    inne = [x for x in PW.przedmioty("giermek") if not x.id.endswith("_helm")]
    uszy = ubierz(PW.cialo(), [PW.helm_giermka_z_uszami()] + inne, id=ID + "_helm_uszy",
                  nazwa="Kot-wojownik — Zestaw Giermka, hełm z osłonami uszu (wariant)", korekty=PW.KOREKTY_CHWYTU)
    return [("kopula", duzy), ("uszy", _tylko_idle(uszy))]


def zbuduj():
    wynik = []
    for _k, p in postacie_chwytow() + postacie_helmow():
        wynik += [p, _przod(p)]
    return wynik


# --------------------------------------------------------------------------- plansze zbiorcze (PIL, po przebudowie)
def _kadr(cel, id_postaci):
    """Kadr bohaterski postaci: <id>_bohater.jpg, a gdy go nie ma (przebudowa bez eksportu zostawia same plansze) —
    lewa górna ćwiartka <id>_plansza.jpg (tam jest kadr bohaterski)."""
    from PIL import Image
    pl = os.path.join(cel, "%s_bohater.jpg" % id_postaci)
    if os.path.isfile(pl):
        return Image.open(pl).convert("RGB")
    pl = os.path.join(cel, "%s_plansza.jpg" % id_postaci)
    if not os.path.isfile(pl):
        return None
    im = Image.open(pl).convert("RGB")
    return im.crop((0, 0, im.width // 2, im.height // 2))


def _kafle(cel, pary, tytul, stopka, plik, K=420):
    """Plansza: kolumny = pary (podpis, id postaci); w każdej kolumnie przód (góra) i 3/4 (dół)."""
    from PIL import Image, ImageDraw
    fn, fb, fm = PW._czcionki()
    im = Image.new("RGB", (len(pary) * K + 32, 90 + 2 * K + 110 + 26 * len(stopka) + 16), PW.TLO)
    dr = ImageDraw.Draw(im)
    dr.text((16, 14), tytul, font=fb, fill=PW.TEKST)
    for i, (podpis, ip) in enumerate(pary):
        x = 16 + i * K
        for j, (nazwa, wid) in enumerate((("przód", ip + "_przod"), ("3/4", ip))):
            y = 76 + j * K
            dr.rounded_rectangle((x + 4, y + 4, x + K - 4, y + K - 4), radius=14, fill=PW.KAFEL)
            ob = _kadr(cel, wid)
            if ob is not None:
                ob.thumbnail((K - 16, K - 16))
                im.paste(ob, (x + (K - ob.width) // 2, y + (K - ob.height) // 2))
            dr.text((x + 14, y + 10), nazwa, font=fm, fill=PW.SZARY)
        for n, linia in enumerate(podpis.split("\n")):
            f = fn if n == 0 else fm
            dr.text((x + (K - dr.textlength(linia, font=f)) // 2, 80 + 2 * K + 28 * n), linia, font=f,
                    fill=PW.TEKST if n == 0 else PW.SZARY)
    for n, linia in enumerate(stopka):
        dr.text((16, 90 + 2 * K + 100 + 26 * n), linia, font=fm, fill=PW.SZARY)
    os.makedirs(os.path.dirname(plik), exist_ok=True)
    im.save(plik, quality=88)
    return plik


def po_przebudowie(cel):
    """Dwie plansze zbiorcze w wynik/_pula_wojownika/; zwraca ich nazwy względem wynik/<moduł>/."""
    pary = []
    for r in KOLEJNOSC:
        o = CH.RODZAJE[r]
        z, _pos, ob = PW.KOREKTY_CHWYTU[r]
        rot = ", ".join("%d" % round(v) for v in ob)
        pary.append(("%s\n%s łapa · %s\nrot (%s)" % (PODPISY[r], o["lapa"], z, rot), "%s_%s" % (ID, r)))
    p1 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "chwyty.jpg")
    _kafle(cel, pary, "Chwyt broni według rodzaju — kot-wojownik (propozycja, chwyty.py)",
           ["Rodzaj chwytu deklaruje broń (Akcesorium.chwyt); korektę rodzaju ma ciało kota (KOREKTY_CHWYTU). "
            "Prawa łapa: kość nośna StaffPivot (w upadku broń wypada).",
            "Lewa łapa: LeftGripAttachment (bez kości nośnej). ATRAPA = kształt zastępczy, bo modelu tej broni "
            "jeszcze nie ma; łuk, proca i tarcza przeskalowane na kota tylko do planszy."], p1, K=360)
    p2 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "helm_uszy_porownanie.jpg")
    _kafle(cel, [("Hełm Giermka (zestaw)\nduża kopuła mieści uszy", ID + "_helm_kopula"),
                 ("Wariant: osłony uszu\nniska kopuła, sylwetka kota zostaje", ID + "_helm_uszy")],
           "Hełm Giermka: kopuła czy osłony uszu?",
           ["Propozycja do porównania. Oba hełmy mieszczą całe uszy kota",
            "i chowają je (ukrywa „Uszy”). W zestawie jest kopuła;",
            "wariant z osłonami uszu (29 części) nie jest w zestawie."], p2, K=460)
    return ["../_pula_wojownika/" + os.path.basename(p) for p in (p1, p2)]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for p in zbuduj():
        b, u = p.sprawdz()
        print("%-44s błędy %d, uwagi %d, założone: %s" % (p.id, len(b), len(u),
                                                         ", ".join("%s na %s" % (z[0].id, z[1]) for z in p.zalozone)))
        for x in b:
            print("   -", x)
