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
4. „Upadek” (Paweł 26.11.2026: „poprawić, żeby nie były pod ziemią”): przedmioty w klipie upadku z KOREKTĄ UPADKU
   (chwyty.py, pula_wojownika.korekta_upadku) — poza przedmiotu w kadrze liczona tą samą funkcją co w kontroli
   (pula_wojownika.korekty_w_klatce_upadku), więc kadr pokazuje to, co zrobi gra. Pod postacią płyta ziemi (zielona;
   w widoku z boku to linia ziemi): pięć zestawów w ostatniej klatce (z boku i z góry-skosa), Giermek w 6 klatkach
   upadku (z boku i z góry-skosa), każdy rodzaj chwytu w ostatniej klatce (z boku i z góry-skosa). Widok z góry-skosa = kadr
   bohaterski postaci przechylonej razem z płytą (korzeń szkieletu obrócony i podniesiony, żeby podłoże renderu
   zostało poza kadrem); widok z boku = rzut prostokątny z tyłu postaci obróconej o 180° (czyli od przodu kota).

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
    "Lewa łapa kota nie ma kości nośnej (jak StaffPivot w prawej): łuk, tarcza i księga w upadku zostają przy łapie; "
    "łuk i tarcza kładą się płasko pod łapą (korekta upadku), księga i bez tego jest nad ziemią.",
    "Upadek: przedmioty w kadrach mają korektę upadku (chwyty.py) — w grze przejście robi skrypt (CFrame:Lerp spawu "
    "w klipie upadku), w eksporcie FBX/GLB jest tylko korekta chwytu.",
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


# --------------------------------------------------------------------------- upadek (Paweł 26.11.2026)
KLATKI_UPADKU_GIERMEK = (22, 27, 31, 33, 40, 60)   # wypuszczenie miecza, lot, hełm się zsuwa, miecz na ziemi,
#                                                   hełm na ziemi, koniec klipu
KONIEC_UPADKU = 60
PRZECHYL_GORA = 42.0          # stopnie: o tyle widok „z góry-skosa” patrzy z wyżej niż kadr bohaterski (ok. 8°)
WZNIES_GORA = 40.0            # studa: postać z płytą ziemi nad podłożem renderu (podłoże wypada z kadru)
GRUB_ZIEMI = 0.08             # grubość płyty ziemi kadru (w widoku z boku: pas ok. 4 px)
PALETA_ZIEMI = {"ziemia": "6E9A4A"}


def _ziemia_i_widok(k, widok):
    """Płyta ziemi pod całą postacią kadru k (górna ściana 0,002 pod ziemią y = 0, zapas 0,45 studa wokół) jako
    akcesorium na kości korzenia; widok „gora” — korzeń (a z nim postać i płyta) przechylony o PRZECHYL_GORA ku
    kamerze kadru bohaterskiego i podniesiony o WZNIES_GORA."""
    import numpy as np
    kl = k.klipy[0]
    W = PW.KM._fk(k, PW.KM._poza_klatki(k, kl, 0))
    pts = np.concatenate([np.asarray(b["pkt"]) @ np.asarray(W[b["kosc"]][0]).T + np.asarray(W[b["kosc"]][1])
                          for b in PW.KM._bryly(k)])
    lo, hi = pts.min(axis=0) - 0.45, pts.max(axis=0) + 0.45
    korzen = next(n for n, kk in k.kosci.items() if kk["rodzic"] is None)
    st = k.kosci[korzen]["staw"]
    a = Akcesorium("ziemia_kadru", "Ziemia (kadr planszy)", zaczep="ZiemiaAttachment", typ="Inne",
                   paleta=PALETA_ZIEMI, przymierz=False)
    a.blok("Ziemia", ((lo[0] + hi[0]) / 2 - st[0], -0.002 - GRUB_ZIEMI / 2 - st[1], (lo[2] + hi[2]) / 2 - st[2]),
           (hi[0] - lo[0], GRUB_ZIEMI, hi[2] - lo[2]), "ziemia", "matowy", faza=0.0)
    k.zaczep("ZiemiaAttachment", korzen, (0, 0, 0), (0, 0, 0))
    k.zaloz(a, "ZiemiaAttachment", eksport=False)
    if widok == "gora":
        # oś przechyłu: pozioma, prostopadła do kierunku kamery kadru bohaterskiego (KAT_KADRU od przodu)
        R = PW.macierz_obrotu(0, KAT_KADRU, 0)
        R = CH.mnoz(R, CH.mnoz(PW.macierz_obrotu(PRZECHYL_GORA, 0, 0), PW.macierz_obrotu(0, -KAT_KADRU, 0)))
        ob = tuple(round(v, 4) for v in CH.katy_z_macierzy(R))
        for f in (0, 1):
            kl.klucz(f, korzen, obrot=ob, przes=(0.0, WZNIES_GORA, 0.0))
    k._bryly = None
    k._pkt = None
    return k


def kadr_upadku(przedmioty, klatka, widok, id_kadru, nazwa):
    """Kot w przedmiotach `przedmioty` w klatce klipu upadku, z korektą upadku tej klatki (ta sama funkcja co
    kontrola: PW.korekty_w_klatce_upadku), jako kadr: widok „bok” — postać obrócona o 180° (rzut prostokątny z tyłu
    planszy = od przodu kota), „gora” — kadr bohaterski z góry-skosa (przechył i płyta ziemi)."""
    q = ubierz(PW.cialo(), przedmioty, id=id_kadru, nazwa=nazwa,
               korekty=PW.korekty_w_klatce_upadku(przedmioty, klatka))
    q.klipy = [k for k in q.klipy if k.nazwa == PW.KLIP_UPADKU]
    k = _kadr_klipu(q, PW.KLIP_UPADKU, klatka, 180.0 if widok == "bok" else 0.0, widok)
    k.id = id_kadru
    return _ziemia_i_widok(k, widok)


def _bron_przedmiot(r, a):
    prz = Przedmiot("chwyt_" + r, a.nazwa, "Weapon", "Weapons", PW.MIARA, cialo=PW.KM.CIALO_TYP)
    prz.na_zaczepie(a)
    return prz


def kadry_upadku():
    """Kadry plansz upadku: (a) pięć zestawów w ostatniej klatce, z boku i z góry-skosa; (b) Giermek w klatkach
    KLATKI_UPADKU_GIERMEK, z boku i z góry-skosa; (c) każdy rodzaj chwytu na gołym kocie w ostatniej klatce, z boku i z góry."""
    wynik = []
    for z in PW.zrobione():
        prz = PW.przedmioty(z)
        for widok in ("bok", "gora"):
            wynik.append(kadr_upadku(prz, KONIEC_UPADKU, widok, "%s_upadek_%s_%s" % (ID, z, widok),
                                     "%s — upadek, kl. %d" % (PW.ZESTAWY[z]["nazwa"], KONIEC_UPADKU)))
    prz = PW.przedmioty("giermek")
    for f in KLATKI_UPADKU_GIERMEK:
        for widok in ("bok", "gora"):
            wynik.append(kadr_upadku(prz, f, widok, "%s_upadek_giermek_kl%02d_%s" % (ID, f, widok),
                                     "Zestaw Giermka — upadek, kl. %d" % f))
    for r, a in sorted(bronie().items(), key=lambda kv: KOLEJNOSC.index(kv[0])):
        for widok in ("bok", "gora"):
            wynik.append(kadr_upadku([_bron_przedmiot(r, a)], KONIEC_UPADKU, widok,
                                     "%s_upadek_%s_%s" % (ID, r, widok), "Chwyt %s — upadek" % r))
    return wynik


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
    return wynik + kadry_upadku()


# --------------------------------------------------------------------------- plansze zbiorcze (PIL, po przebudowie)
CWIARTKI = {"bohater": (0, 0), "przod": (1, 0), "bok": (0, 1), "tyl": (1, 1)}   # układ <id>_plansza.jpg


def _kadr(cel, id_postaci, cwiartka="bohater"):
    """Kadr bohaterski postaci: <id>_bohater.jpg, a gdy go nie ma (przebudowa bez eksportu zostawia same plansze) —
    lewa górna ćwiartka <id>_plansza.jpg (tam jest kadr bohaterski). cwiartka = inny widok z planszy: „przod”
    (z manekinem skali), „bok” (rzut z prawego boku postaci), „tyl” (rzut z tyłu)."""
    from PIL import Image
    pl = os.path.join(cel, "%s_bohater.jpg" % id_postaci)
    if cwiartka == "bohater" and os.path.isfile(pl):
        return Image.open(pl).convert("RGB")
    pl = os.path.join(cel, "%s_plansza.jpg" % id_postaci)
    if not os.path.isfile(pl):
        return None
    im = Image.open(pl).convert("RGB")
    cx, cy = CWIARTKI[cwiartka]
    w, h = im.width // 2, im.height // 2
    return im.crop((cx * w, cy * h, (cx + 1) * w, (cy + 1) * h))


def _siatka(cel, kolumny, wiersze, tytul, stopka, plik, K=360):
    """Plansza: kolumny = (podpis, [id postaci w każdym wierszu — albo (id, ćwiartka planszy)]); wiersze = podpisy
    wierszy (lewy górny róg kafla)."""
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
            ob = _kadr(cel, *wid) if isinstance(wid, tuple) else _kadr(cel, wid)
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
    return ["../_pula_wojownika/" + os.path.basename(p) for p in [p1, p2, p3] + plansze_upadku(cel)]


def plansze_upadku(cel):
    """Trzy plansze upadku (wynik/_pula_wojownika/<prefiks>upadek_*.jpg): zestawy w ostatniej klatce, Giermek
    w klatkach upadku, rodzaje chwytu w ostatniej klatce; zwraca ścieżki."""
    ziemia = "Zielona płyta = ziemia (w widoku z boku jej pas to linia ziemi); nic, co kot nosi, nie schodzi pod nią."
    gra = ("W grze: w klipie upadku skrypt przestawia spaw przedmiotu z korekty chwytu na korektę upadku "
           "(CFrame:Lerp w oknie klatek z ekwipunek.json); kadr liczy pozę tą samą funkcją co kontrola --ruch.")
    kol = [("%s\n%s" % (PW.ZESTAWY[z]["nazwa"], PW.ZESTAWY[z]["przedmioty"]["miecz"]),
            [("%s_upadek_%s_bok" % (ID, z), "tyl"), "%s_upadek_%s_gora" % (ID, z)]) for z in PW.zrobione()]
    p1 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "upadek_zestawy.jpg")
    _siatka(cel, kol, ("z boku (od przodu kota)", "z góry, ze skosu"),
            "Upadek — koniec klipu (kl. %d): miecz i hełm leżą na ziemi (propozycja)" % KONIEC_UPADKU,
            ["Miecz w locie obraca się do ułożenia kostura Kota-Maga i leży płasko przed kotem; hełm zsuwa się "
             "z głowy, prostuje się i stoi obok niej.", ziemia, gra], p1, K=360)
    g = ID + "_upadek_giermek"
    opisy = {22: "miecz wypada z łapy", 27: "miecz w locie", 31: "hełm się zsuwa", 33: "miecz na ziemi",
             40: "hełm na ziemi", 60: "koniec klipu"}
    kol = [("kl. %d\n%s" % (f, opisy.get(f, "")), [("%s_kl%02d_bok" % (g, f), "tyl"), "%s_kl%02d_gora" % (g, f)])
           for f in KLATKI_UPADKU_GIERMEK]
    okna = {r: PW.korekta_upadku(PW.przedmioty("giermek")[PW.RZECZY.index(r)].segmenty[0]["akc"])
            for r in ("miecz", "helm")}
    p2 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "upadek_giermek.jpg")
    _siatka(cel, kol, ("z boku (od przodu kota)", "z góry, ze skosu"),
            "Upadek — Zestaw Giermka, klip upadek (%d klatek, 30 kl./s)" % KONIEC_UPADKU,
            [ziemia, "Przejście na korektę upadku: miecz kl. %d→%d, hełm kl. %d→%d (kości nośne lecą tym samym torem "
                     "co kostur i kapelusz Kota-Maga: miecz ląduje w kl. 33, hełm w kl. 40)."
             % (okna["miecz"]["od_klatki"], okna["miecz"]["do_klatki"], okna["helm"]["od_klatki"],
                okna["helm"]["do_klatki"])], p2, K=300)
    kol = []
    for r in KOLEJNOSC:
        a = bronie()[r]
        kor = PW.korekta_upadku(a)
        kol.append(("%s\n%s" % (PODPISY[r], ("korekta kl. %d→%d" % (kor["od_klatki"], kor["do_klatki"])) if kor
                                 else "bez korekty (nad ziemią)"),
                    [("%s_upadek_%s_bok" % (ID, r), "tyl"), "%s_upadek_%s_gora" % (ID, r)]))
    p3 = os.path.join(PW.PODGLADY, PW.PREFIKS_PLANSZ + "upadek_chwyty.jpg")
    _siatka(cel, kol, ("z boku (od przodu kota)", "z góry, ze skosu"),
            "Upadek — każdy rodzaj chwytu, koniec klipu (kl. %d), goły kot" % KONIEC_UPADKU,
            ["Prawa łapa (miecz, różdżka, drzewce, proca): broń wypada i leży płasko przed kotem. Lewa łapa nie ma "
             "kości nośnej: łuk i tarcza zostają przy łapie i kładą się płasko pod nią; księga i bez tego jest nad "
             "ziemią.", ziemia], p3, K=300)
    return [p1, p2, p3]


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
