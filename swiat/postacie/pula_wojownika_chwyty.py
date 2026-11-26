# -*- coding: utf-8 -*-
"""PULA WOJOWNIKA — plansze do oceny przez ludzi (26.11.2026). Status: propozycja.

1. „Chwyty” (Karol: „odróżniaj różdżkę od miecza i łuk itd.”): goły kot-wojownik trzyma po jednym przykładzie
   każdego rodzaju chwytu z swiat/postacie/chwyty.py — miecz (Miecz Giermka), różdżka (ATRAPA), drzewce (kostur
   Kota-Maga), proca (proca startowa w proporcjach kota), łuk (łuk Zwiadowcy w proporcjach kota), tarcza (tarcza
   Rycerza ×0,6), księga (ATRAPA). Każdy rodzaj z przodu i 3/4.
2. „Chód z mieczem” (Karol: „miecz ma być tak wychylony, że podczas animacji chodzenia się nie bugował”): kot
   w Zestawie Giermka w 8 równo rozłożonych klatkach klipu chod, z przodu i z prawego boku (łapa z mieczem).
3. „Chód z każdym rodzajem”: goły kot z każdą bronią z planszy chwytów w 4 klatkach chodu, z boku łapy z bronią.
   Liczby (odstęp broni od ciała i ziemi w każdej klatce): python -B swiat/postacie/pula_wojownika.py --ruch.

    python -B swiat/postacie/przebuduj.py pula_wojownika_chwyty          # plansze + krótki film chodu Giermka

Same plansze (EKSPORT_MODELI = False): wynik/pula_wojownika_chwyty/<id>_plansza.jpg każdego kadru, film chodu
<ID>_film_giermek_chod.mp4, a po przebudowie zbiorcze wynik/_pula_wojownika/<prefiks>chwyty.jpg,
<prefiks>chod_miecz.jpg i <prefiks>chod_chwyty.jpg. Kadr to ta sama postać w jednej klatce klipu, obrócona w pionie
o kąt kamery kadru bohaterskiego (blender_postac.BOHATER): przód, prawy albo lewy bok.
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
FILMY = ["chod"]                     # tylko postać filmu ma klip chod (kadry mają jeden klip „kadr”)
EKSPORT_MODELI = False
# kąt kamery kadru bohaterskiego w poziomie: kierunek (0,5; 0,16; 1,0) z blender_postac.BOHATER
KAT_KADRU = math.degrees(math.atan2(0.5, 1.0))
KOLEJNOSC = ("miecz", "rozdzka", "drzewce", "proca", "luk", "tarcza", "ksiega")
DLUGOSC_CHODU = 20                              # klip chod kota: pętla 20 klatek (kot_mag.chod)
KLATKI_CHODU_MIECZ = (0, 3, 5, 8, 10, 13, 15, 18)
KLATKI_CHODU_RODZAJE = (0, 5, 10, 15)
PODPISY = {"miecz": "miecz — Miecz Giermka", "rozdzka": "różdżka — ATRAPA", "drzewce": "drzewce — kostur Kota-Maga",
           "proca": "proca — proca startowa (kot)", "luk": "łuk — łuk Zwiadowcy (kot)",
           "tarcza": "tarcza — tarcza Rycerza ×0,6", "ksiega": "księga — ATRAPA"}
SLABOSCI = [
    "Plansza propozycji: rodzaje chwytu i ich korekty kota (chwyty.py) czekają na ocenę ludzi.",
    "Różdżka i księga to atrapy (nie ma ich modeli); łuk, proca i tarcza to modele ludzkich bohaterów i broni "
    "startowej przeskalowane na kota tylko do tej planszy.",
    "Lewa łapa kota nie ma kości nośnej (jak StaffPivot w prawej): łuk, tarcza i księga w upadku zostają w łapie.",
    "Klipy kota są pisane pod kostur; wszystkie rodzaje sprawdza liczbowo pula_wojownika.py --ruch (całe ciało "
    "i ziemia, klatka po klatce); w klipach walki lewa łapa zbliża się do tułowia i głowy, więc łuk, tarcza "
    "i księga wchodzą w ciało — jedna stała korekta tego nie naprawi.",
    "Widoki to postać obrócona w kadrze (klip „kadr”, jedna klatka), nie osobna kamera.",
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
    """ATRAPA księgi (nie ma modelu na kota): mała zamknięta księga na miarę kota (0,44 × 0,56 × 0,16), trzymana za
    górną krawędź, wisi pod lewą łapą, okładka skręcona 35° ku przodowi; osie dłoni jak tarcza Rycerza (blok
    uklad(−90, 0, 0)). Mała i odsunięta do przodu (korekta rodzaju), żeby w chodzie nie zahaczał jej ogon (--ruch)."""
    a = Akcesorium("atrapa_ksiega", "Księga (atrapa)", zaczep="LeftGripAttachment", typ="Bron", paleta=PALETA_ATRAP,
                   ikona_obrot=(0, -60, 0), chwyt="ksiega")
    with a.uklad(obrot=(-90, 0, 0)):
        with a.uklad(obrot=(0, -35, 0)):                 # lokalne +X = okładka, skręcona 35° ku przodowi
            a.blok("Okladka", (0.0, -0.3, 0), (0.16, 0.56, 0.44), "okladka", "matowy", faza=0.03)
            a.blok("Kartki", (0.0, -0.3, 0.21), (0.12, 0.5, 0.04), "kartki", "matowy", faza=0.0)
            a.blok("Grzbiet", (0.0, -0.3, -0.22), (0.19, 0.58, 0.05), "okladka_ciemna", "matowy", faza=0.0)
            a.blok("Godlo", (0.09, -0.3, 0.0), (0.03, 0.16, 0.16), "zloto", "metal", rot=(45, 0, 0), faza=0.0)
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


def _kadr_klipu(p, klip, klatka, kat, sufiks):
    """Kopia postaci do jednego kadru: klip „kadr” = poza z (klip, klatka) z biodrami obróconymi wokół pionu o `kat`
    (kadr bohaterski patrzy z kierunku KAT_KADRU od przodu: kat = KAT_KADRU — przód, KAT_KADRU + 90 — prawy bok,
    KAT_KADRU − 90 — lewy bok); inne klipy usunięte (żadnych filmów), poza renderu = ten kadr."""
    q = copy.deepcopy(p)
    q.id, q.nazwa = "%s_%s" % (p.id, sufiks), "%s (%s %s, kl. %s)" % (p.nazwa, sufiks, klip, klatka)
    zr = next(k for k in q.klipy if k.nazwa == klip)
    q.klipy = []
    k = q.klip("kadr", 1, petla=False)
    Rk = PW.macierz_obrotu(0, kat, 0)
    for n in q.kosci:
        ob = zr.wartosc(n, "obrot", klatka)
        pr = zr.wartosc(n, "przes", klatka)
        if n == "LowerTorso":
            ob = ob or (0.0, 0.0, 0.0)
            ob = (ob[0], ob[1] + kat, ob[2])
            if pr is not None:
                pr = tuple(PW.razy_wektor(Rk, pr))
        for f in (0, 1):
            if ob is not None or pr is not None:
                k.klucz(f, n, obrot=ob, przes=pr)
    q.ustaw_poze_renderu("kadr", 0)
    return q


def postacie_chwytow():
    """Goły kot-wojownik z jedną bronią każdego rodzaju (przez ubierz() z korektami kota) — [(rodzaj, postać)];
    postać ma klipy idle i chod (kadry planszy chodu)."""
    wynik = []
    for r, a in sorted(bronie().items(), key=lambda kv: KOLEJNOSC.index(kv[0])):
        prz = Przedmiot("chwyt_" + r, a.nazwa, "Weapon", "Weapons", PW.MIARA, cialo=PW.KM.CIALO_TYP)
        prz.na_zaczepie(a)
        p = ubierz(PW.cialo(), [prz], id="%s_%s" % (ID, r), nazwa="Kot-wojownik — chwyt: %s" % r,
                   korekty=PW.KOREKTY_CHWYTU)
        p.klipy = [k for k in p.klipy if k.nazwa in ("idle", "chod")]
        wynik.append((r, p))
    return wynik


def postacie_kontroli():
    """Dla pula_wojownika.py --ruch: (opis, postać, id broni, kość łapy, strefa chwytu) — każdy rodzaj z planszy
    na gołym kocie i na kocie w Zestawie Giermka (bez miecza); tarcza: całe przedramię to chwyt (pasy)."""
    giermek = [x for x in PW.przedmioty("giermek") if not x.id.endswith("_miecz")]
    for r in KOLEJNOSC:
        lapa = "RightHand" if CH.RODZAJE[r]["lapa"] == "prawa" else "LeftHand"
        strefa = 9.0 if CH.RODZAJE[r].get("przedramie_w_chwycie") else PW.STREFA_CHWYTU
        for cialo, inne in (("goły kot", []), ("kot w Zestawie Giermka", giermek)):
            a = bronie()[r]
            prz = Przedmiot("chwyt_" + r, a.nazwa, "Weapon", "Weapons", PW.MIARA, cialo=PW.KM.CIALO_TYP)
            prz.na_zaczepie(a)
            p = ubierz(PW.cialo(), inne + [prz], id="kontrola_" + r, korekty=PW.KOREKTY_CHWYTU)
            yield "%s — %s (%s)" % (PODPISY[r], cialo, a.id), p, a.id, lapa, strefa


def postac_chodu_mieczem():
    """Kot w Zestawie Giermka z klipami idle i chod (kadry planszy chodu z mieczem i film chodu)."""
    p = PW.postac("giermek", id=ID + "_giermek")
    p.klipy = [k for k in p.klipy if k.nazwa in ("idle", "chod")]
    return p


def zbuduj():
    wynik = []
    for r, p in postacie_chwytow():
        wynik.append(_kadr_klipu(p, "idle", 0, KAT_KADRU, "przod"))
        wynik.append(_kadr_klipu(p, "idle", 0, 0.0, "34"))
        bok = KAT_KADRU + 90 if CH.RODZAJE[r]["lapa"] == "prawa" else KAT_KADRU - 90
        for f in KLATKI_CHODU_RODZAJE:
            wynik.append(_kadr_klipu(p, "chod", f, bok, "chod%02d" % f))
    g = postac_chodu_mieczem()
    for f in KLATKI_CHODU_MIECZ:
        wynik.append(_kadr_klipu(g, "chod", f, KAT_KADRU, "chod%02d_przod" % f))
        wynik.append(_kadr_klipu(g, "chod", f, KAT_KADRU + 90, "chod%02d_bok" % f))
    film = copy.deepcopy(g)
    film.id, film.nazwa = ID + "_film_giermek", g.nazwa + " (film chodu)"
    wynik.append(film)
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


def _siatka(cel, kolumny, wiersze, tytul, stopka, plik, K=360):
    """Plansza: kolumny = (podpis, [id postaci w każdym wierszu]); wiersze = podpisy wierszy (lewy górny róg kafla)."""
    from PIL import Image, ImageDraw
    fn, fb, fm = PW._czcionki()
    n = len(wiersze)
    im = Image.new("RGB", (len(kolumny) * K + 32, 90 + n * K + 110 + 26 * len(stopka) + 16), PW.TLO)
    dr = ImageDraw.Draw(im)
    dr.text((16, 14), tytul, font=fb, fill=PW.TEKST)
    for i, (podpis, ids) in enumerate(kolumny):
        x = 16 + i * K
        for j, (nazwa, wid) in enumerate(zip(wiersze, ids)):
            y = 76 + j * K
            dr.rounded_rectangle((x + 4, y + 4, x + K - 4, y + K - 4), radius=14, fill=PW.KAFEL)
            ob = _kadr(cel, wid)
            if ob is not None:
                ob.thumbnail((K - 16, K - 16))
                im.paste(ob, (x + (K - ob.width) // 2, y + (K - ob.height) // 2))
            dr.text((x + 14, y + 10), nazwa, font=fm, fill=PW.SZARY)
        for m, linia in enumerate(podpis.split("\n")):
            f = fn if m == 0 else fm
            dr.text((x + (K - dr.textlength(linia, font=f)) // 2, 80 + n * K + 28 * m), linia, font=f,
                    fill=PW.TEKST if m == 0 else PW.SZARY)
    for m, linia in enumerate(stopka):
        dr.text((16, 90 + n * K + 100 + 26 * m), linia, font=fm, fill=PW.SZARY)
    os.makedirs(os.path.dirname(plik), exist_ok=True)
    im.save(plik, quality=88)
    return plik


def po_przebudowie(cel):
    """Trzy plansze zbiorcze w wynik/_pula_wojownika/: chwyty (przód, 3/4), chód z mieczem (Giermek, przód i bok),
    chód z każdym rodzajem (bok łapy z bronią); zwraca ich nazwy względem wynik/<moduł>/."""
    pary = []
    for r in KOLEJNOSC:
        o = CH.RODZAJE[r]
        z, _pos, ob = PW.KOREKTY_CHWYTU[r]
        rot = ", ".join("%d" % round(v) for v in ob)
        pary.append(("%s\n%s łapa · %s\nrot (%s)" % (PODPISY[r], o["lapa"], z, rot),
                     ["%s_%s_przod" % (ID, r), "%s_%s_34" % (ID, r)]))
    p1 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "chwyty.jpg")
    _siatka(cel, pary, ("przód", "3/4"), "Chwyt broni według rodzaju — kot-wojownik (propozycja, chwyty.py)",
            ["Rodzaj chwytu deklaruje broń (Akcesorium.chwyt); korektę rodzaju ma ciało kota (KOREKTY_CHWYTU). "
             "Liczby dobrane kontrolą --ruch (broń vs całe ciało i ziemia).",
             "Prawa łapa: kość nośna StaffPivot (w upadku broń wypada); lewa: LeftGripAttachment. ATRAPA = kształt "
             "zastępczy; łuk, proca i tarcza przeskalowane na kota tylko do planszy."], p1)
    g = ID + "_giermek"
    kol = [("klatka %d z %d" % (f, DLUGOSC_CHODU), ["%s_chod%02d_przod" % (g, f), "%s_chod%02d_bok" % (g, f)])
           for f in KLATKI_CHODU_MIECZ]
    p2 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "chod_miecz.jpg")
    _siatka(cel, kol, ("przód", "prawy bok (łapa z mieczem)"),
            "Chód z mieczem — Zestaw Giermka, klip chod (pętla %d klatek)" % DLUGOSC_CHODU,
            ["Miecz w chwycie „miecz” (chwyty.py). Kontrola --ruch: w chodzie i spoczynku miecz nie wchodzi w żadną "
             "bryłę ciała, stroju, hełmu ani w ziemię (zapas ≥ 0,05 studa, 5 zestawów)."], p2, K=300)
    kol = [(PODPISY[r], ["%s_%s_chod%02d" % (ID, r, f) for f in KLATKI_CHODU_RODZAJE]) for r in KOLEJNOSC]
    p3 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "chod_chwyty.jpg")
    _siatka(cel, kol, tuple("chód, kl. %d" % f for f in KLATKI_CHODU_RODZAJE),
            "Chód z każdym rodzajem chwytu — goły kot, bok łapy z bronią",
            ["Prawa łapa: widok z prawego boku; lewa (łuk, tarcza, księga): z lewego. Lewa łapa w chodzie sama "
             "zahacza o ogon (klip ciała), więc to, co w niej, też bywa przy ogonie — szczegóły w raporcie --ruch."],
            p3, K=260)
    return ["../_pula_wojownika/" + os.path.basename(p) for p in (p1, p2, p3)]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for p in zbuduj():
        b, u = p.sprawdz()
        print("%-48s błędy %d, uwagi %d, klipy %s, założone: %s" % (
            p.id, len(b), len(u), ",".join(k.nazwa for k in p.klipy),
            ", ".join("%s na %s" % (z[0].id, z[1]) for z in p.zalozone)))
        for x in b:
            print("   -", x)
