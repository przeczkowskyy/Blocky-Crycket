# -*- coding: utf-8 -*-
"""LEŚNY SLIME — zwykły przeciwnik lasu: mchowozielona kostka galarety z liściem i grzybkiem zatopionymi w środku.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/lesny_slime.py --wyj <folder> --klip umiejetnosc

Opis z danych walki (tools/walka/dane_walki.json, id „lesny_slime”): półprzezroczysty, mchowozielony sześcian galarety
z liściem i małym grzybkiem zatopionymi w środku; podskakuje i zostawia lepkie ślady. Dużo życia, słabe ciosy;
umiejętność „kwaśny plusk” zdziera pancerz.

Wzór: pet `slime.py` (ta sama technika, inny charakter). Leśny Slime jest większy od peta (2,6 studa wysokości przy
2,25 u peta; gracz ma 5,7), ma złośliwą minę (oczy jak odwrócone, przechylone trapezy pod grubymi brwiami w „V”,
krzywy uśmieszek z dwoma kłami i kroplą kwasu pod kącikiem) i mech zamiast błękitu.

Wygląd (bez prawdziwej przezroczystości — jeden materiał na model): jasna, lekko świecąca skorupka (mech jasny) na
ściętych krawędziach i ciemniejszy rdzeń galarety na płaskich ścianach. Liść i grzybek „widać przez galaretę”:
na wierzchu, bokach i tyle leży ich rzut w przygaszonych kolorach, policzony z JEDNEGO położenia w środku kostki —
z każdej strony liść i grzybek są w tym samym miejscu, jak w szkle (przód zostaje dla twarzy).
Prawdziwy liść i grzybek (kości Lisc i Grzybek) siedzą schowane w środku i wychodzą na wierzch dopiero, gdy slime
rozleje się w kałużę (upadek).

Paleta: trzy odcienie mchu (skorupka, rdzeń, cień rdzenia), tusz (oczy, usta), biały odblask, bursztynowy liść,
czerwony kapelusz grzybka z kremowym trzonem; AKCENT: kwaśna limonka (kula kwasu, kałuża plusku, kropla w kąciku).

Szkielet (własny, typ „stwor”; L = lewa = +X):
    Root
    ├── Cialo          staw na ziemi pod środkiem — skok (przes) i przechył (obrót) całej galarety
    │   ├── Dol        cała galareta z twarzą i rzutami liścia/grzybka (siatka Dol_Geo, wagi Dol/Gora)
    │   ├── Gora       góra galarety (bez siatki) — zgniatanie, rozciąganie, nadymanie i rozlanie
    │   ├── Oczy, Powieki                oczy (chowają się w galaretę) / kreski zamkniętych oczu (wychodzą)
    │   ├── UstaO                        szeroko otwarta paszcza (schowana za ustami)
    │   ├── BokL, BokP, Przod, Tyl       brzuszki (poszerzenie przy zgnieceniu, płaty kałuży przy upadku)
    │   ├── Lisc, Grzybek                prawdziwy liść i grzybek w środku (widać je po rozlaniu)
    │   ├── Kula                         kula kwasu (umiejętność): w spoczynku schowana za ustami
    │   └── Plusk                        kałuża kwasu po trafieniu kuli: w spoczynku schowana w podstawie
    └── KroplaL, KroplaP, KroplaT        lepkie krople przy podstawie
Bryły nie mają kanału skali — zgniatanie robi przesunięcie kości Gora (siatka skórowana na dwóch kościach).

Klipy (30 kl./s; patrzy w +Z i w tę stronę atakuje). Wszystkie klipy są zapisane jako pozy kluczowe zamienione na
klucz w każdej klatce (_sekwencja): kości twarzy i schowane w środku bryły jadą z galaretą proporcjonalnie do wysokości,
a galareta nigdy nie wchodzi pod ziemię (przechył podnosi ją na krawędzi).
  idle (pętla 2 s), ruch (podskok naprzód w miejscu, pętla 0,8 s), atak (przysiad, wybicie i uderzenie całym ciałem
  przed siebie, trafienie w kl. 13, 1 s), umiejetnosc (kwaśny plusk: nadyma się, w otwartej paszczy pokazuje się
  świecąca kula kwasu, pluje nią po łuku na ok. 4,3 studa przed siebie; kula rozpryskuje się w kałużę, która potem
  wsiąka w ziemię, 2,2 s), trafienie (szarpnięcie w tył ze zgnieceniem i zaciśniętymi oczami, 0,6 s), unik (odskok
  w lewo i powrót ślizgiem, 0,9 s), upadek (szarpnięcie, chwieje się z zamkniętymi oczami i rozlewa w płaską kałużę
  z czterema płatami; na wierzch wypływają grzybek, liść i kula kwasu; kończy się leżeniem, 2 s),
  wiwat (dwa podskoki z otwartą paszczą i kołysaniem, pętla 1,33 s).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, macierz_obrotu, razy_wektor
from swiat.postacie.slime import _kropla

ID = "lesny_slime"

# ------------------------------------------------------------------------------------------- wymiary (studs)
W, H, D = 2.9, 2.6, 2.8          # kostka: szer X, wys Y, głęb Z (pet: 2,4 × 2,25 × 2,35)
FAZA = 0.3                       # mocne ścięcie krawędzi = „miękka” kostka
YO, YU = H / 2 + 0.26, H / 2 - 0.36  # wysokość oczu i ust od ziemi (spoczynek)
XO = 0.56                        # oczy: odległość od środka
ZF = D / 2                       # przednia ściana

OCZY = (0.0, YO, ZF)                     # staw oczu (oczy chowają się w galaretę przy mrugnięciu)
POWIEKI = (0.0, YO, ZF - 0.1)            # staw zamkniętych oczu (kreski schowane tuż pod przednią ścianą)
USTA_O = (0.0, YU - 0.14, ZF - 0.2)      # staw otwartej paszczy = środek płytki
KULA = (0.0, YU, ZF - 0.62)              # staw kuli kwasu = jej środek (schowana za ustami)
R_KULA = 0.31
LISC = (0.3, 1.5, -0.25)                 # środek liścia w kostce
GRZYB = (-0.72, 0.3, -0.45)              # podstawa grzybka (stoi na „dnie” galarety)
GRZYB_H = (0.42, 0.36)                   # wysokość trzonu i kapelusza grzybka
GRZYB_SZ = (0.26, 0.84)                  # szerokość trzonu i kapelusza
PLUSK_STAW = (0.0, 0.1, 0.0)              # schowek kałuży w podstawie galarety (nad dnem)
PLUSK_Z = 4.3                            # gdzie spada kula kwasu (od środka slime'a, w +Z)

T_BRZ = 0.5                      # grubość brzuszka (w kierunku wysuwania)
H_BRZ = 0.75                     # wysokość brzuszka (soczewka: niska i szeroka, galareta „siada” u dołu)
Y_BRZ = 0.62                     # środek brzuszka od ziemi (niżej niż środek kostki — nie wygląda jak uchwyt)
_G = T_BRZ / 2 + 0.03            # brzuszek w spoczynku: zewnętrzna ściana 0,03 pod ścianą galarety
BOKI = {  # kość: (staw = środek schowanego brzuszka, kierunek wysuwania)
    "BokL": ((W / 2 - _G, Y_BRZ, 0.0), (1, 0, 0)),
    "BokP": ((-W / 2 + _G, Y_BRZ, 0.0), (-1, 0, 0)),
    "Przod": ((0.0, 0.5, ZF - _G), (0, 0, 1)),
    "Tyl": ((0.0, Y_BRZ, -ZF + _G), (0, 0, -1)),
}
KROPLE = {"KroplaL": (1.85, 0.95, 0.32), "KroplaP": (-1.75, 1.15, 0.26), "KroplaT": (1.05, -1.7, 0.24)}

PALETA = {
    "skorupka": "9ED67A",      # jasna, lekko świecąca skorupka (krawędzie) — mech jasny
    "rdzen": "58A443",         # rdzeń galarety na przodzie i wierzchu
    "rdzen_cien": "3F8436",    # boki i tył rdzenia
    "tusz": "18230F",          # oczy, usta, brwi
    "odblask": "F2FFE4",       # białe odblaski, kły
    "lisc": "E2A431",          # bursztynowy liść (prawdziwy, po rozlaniu)
    "lisc_w": "C4AE3C",        # liść widziany przez zieloną galaretę
    "grzyb": "D9493A",         # kapelusz grzybka
    "grzyb_w": "BA5E3A",       # kapelusz widziany przez galaretę
    "trzon": "F2E7C4",         # trzon grzybka i kropki
    "trzon_w": "CFD99C",       # trzon widziany przez galaretę
    "kwas": "EEFF2E",          # AKCENT: kwas (kula, kałuża, kropla w kąciku)
}

SLABOSCI = [
    "Brak prawdziwej przezroczystości (jeden materiał na model): szkło udają jasna skorupka i ciemniejszy rdzeń, "
    "a liść i grzybek „w środku” to płaskie rzuty na wierzchu, bokach i tyle (policzone z jednego położenia, więc "
    "z każdej strony są w tym samym miejscu). Z bliska widać, że to naklejki, a od przodu ich nie widać (przód to "
    "twarz) — w kadrze 3/4 widać je tylko na boku. W grze można dać galarecie materiał Glass i zostawić same "
    "prawdziwe bryły liścia i grzybka (kości Lisc i Grzybek).",
    "Galareta jest skórowana na dwóch kościach (Dol, Gora) — import wag do Roblox nie był testowany. Oczy, kreski "
    "zamkniętych oczu, paszcza, brzuszki, kula i kałuża to sztywne bryły na własnych kościach: oczy nie zgniatają się "
    "razem z galaretą (brwi i usta tak).",
    "Rozlanie (upadek) to spłaszczona kostka (0,45 studa) z czterema płaskimi płatami-soczewkami dookoła — z daleka "
    "czyta się jako kałuża, z bliska środek dalej ma prostokątny obrys spłaszczonej kostki. Brwi i usta spłaszczają "
    "się do krzywych pasków na przedniej krawędzi. Kula kwasu leży na ziemi i wystaje z kałuży jak świecące „żółtko”.",
    "Kałuża kwasu z umiejętności wsiąka na końcu w ziemię (schodzi pod nią) i w ostatniej klatce wraca skokiem do "
    "schowka w podstawie slime'a; prawdziwy rozprysk (cząsteczki, dym) dorobić efektem na PluskAttachment.",
    "Brzuszki przy zgnieceniu (atak, ruch, umiejętność, trafienie, unik, wiwat) wysuwają się nisko z boków i tyłu jako "
    "spłaszczone soczewki (galareta „siada” u dołu) — w kadrze 3/4 wyglądają trochę jak policzek przy dolnej krawędzi "
    "i na chwilę zasłaniają rzut grzybka na boku. Przód zostaje gładki, bo pod twarzą brzuszek wyglądał jak listwa.",
    "Kości nie są R15 (własny szkielet: Root + 17 kości) — klipy importuje się na własny rig; Studio nie testowane.",
    "Świecenie skorupki i kwasu jest tylko w teksturze-palecie (emisja) — w grze dać Neon albo PointLight.",
    "Ruch to podskok w miejscu (bez przesuwania korzenia); szybkość przesuwania ustawia gra.",
    "Kadr filmów jest wspólny dla wszystkich klipów i obejmuje lot kuli i kałużę ok. 4,3 studa przed slime'em, więc "
    "w filmach slime jest mały; bliżej: plansza i kadr bohaterski.",
    "Klipy to szkice (0,6–2,2 s), nie gotowa animacja; mimika tylko z oczu (otwarte/zamknięte) i paszczy.",
]


# ---------------------------------------------------------------------------------------------- pomocnicze
def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _krzyz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _skal(a, b):
    return sum(a[i] * b[i] for i in range(3))


# ściany kostki: (nazwa, obrót układu ściany: lokalne +Z = normalna, oś u, oś v, odległość od środka)
SCIANY = {
    "przod": ((0, 0, 0), (1, 0, 0), (0, 1, 0), D / 2),
    "bokL": ((0, 90, 0), (0, 0, -1), (0, 1, 0), W / 2),
    "bokP": ((0, -90, 0), (0, 0, 1), (0, 1, 0), W / 2),
    "tyl": ((0, 180, 0), (-1, 0, 0), (0, 1, 0), D / 2),
    "wierzch": ((-90, 0, 0), (1, 0, 0), (0, 0, -1), H / 2),
}
NORMALNE = {"przod": (0, 0, 1), "bokL": (1, 0, 0), "bokP": (-1, 0, 0), "tyl": (0, 0, -1), "wierzch": (0, 1, 0)}

# liść w środku: oś długa a, oś szeroka b (w kostce, ukośnie, żeby czytał się z każdej strony)
_LN = _norm((0.6, 1.0, 0.7))
_LA = _norm(_krzyz(_LN, _norm((0.3, 0.0, 1.0))))
_LB = _krzyz(_LN, _LA)
LISC_DL, LISC_SZ = 1.5, 0.74


def _rzut_lisc(p, sc):
    """Rzut liścia (elipsa + żyłka + ogonek) na ścianę sc, w przygaszonym kolorze."""
    obr, eu, ev, odl = SCIANY[sc]
    c = (LISC[0], LISC[1] - H / 2, LISC[2])          # układ środka kostki
    u, v = _skal(c, eu), _skal(c, ev)
    au, av = _skal(_LA, eu), _skal(_LA, ev)
    bu, bv = _skal(_LB, eu), _skal(_LB, ev)
    dl = LISC_DL * math.hypot(au, av)
    kat = math.degrees(math.atan2(av, au))
    # szerokość: składowa b prostopadła do rzutu a
    if math.hypot(au, av) > 1e-6:
        nu, nv = -av / math.hypot(au, av), au / math.hypot(au, av)
    else:
        nu, nv = 0.0, 1.0
    sz = max(0.14, LISC_SZ * abs(bu * nu + bv * nv))
    dl = max(dl, 0.3)
    with p.uklad(pos=tuple(NORMALNE[sc][i] * (odl + 0.02) for i in range(3)), obrot=obr):
        with p.uklad(pos=(u, v, 0.0), obrot=(0, 0, kat)):
            p.kula("Lisc w galarecie " + sc, (0, 0, 0.015), (dl, sz, 0.03), "lisc_w", "matowy", segm=8)
            p.blok("Zylka " + sc, (0.04 * dl, 0, 0.035), (dl * 0.82, 0.04, 0.02), "rdzen_cien", "matowy", faza=0.0)
            p.blok("Ogonek " + sc, (-dl / 2 - 0.09, 0, 0.025), (0.2, 0.05, 0.03), "lisc_w", "matowy", faza=0.0)


def _rzut_grzyb(p, sc):
    """Rzut grzybka na ścianę sc: z boku trzon + kapelusz z kropką, z góry okrągły kapelusz."""
    obr, eu, ev, odl = SCIANY[sc]
    th, kh = GRZYB_H
    with p.uklad(pos=tuple(NORMALNE[sc][i] * (odl + 0.02) for i in range(3)), obrot=obr):
        if sc == "wierzch":
            c = (GRZYB[0], 0.0, GRZYB[2])
            u, v = _skal(c, eu), _skal(c, ev)
            p.walec("Kapelusz w galarecie " + sc, (u, v, 0.015), (GRZYB_SZ[1], 0.03, GRZYB_SZ[1]), "grzyb_w", "matowy",
                    rot=(90, 0, 0), faza=0.0, segm=8)
            p.walec("Kropka w galarecie " + sc, (u + 0.1, v + 0.08, 0.035), (0.16, 0.02, 0.16), "trzon_w",
                    "matowy", rot=(90, 0, 0), faza=0.0, segm=8)
            return
        c = (GRZYB[0], GRZYB[1] - H / 2, GRZYB[2])
        u, v = _skal(c, eu), _skal(c, ev)
        p.blok("Trzon w galarecie " + sc, (u, v + th / 2, 0.015), (GRZYB_SZ[0], th, 0.03), "trzon_w", "matowy", faza=0.0)
        # kapelusz: kopułka (ścięty ostrosłup w płaszczyźnie ściany: podstawa na dole)
        p.ostroslup("Kapelusz w galarecie " + sc, (u, v + th + kh / 2 - 0.04, 0.015), (GRZYB_SZ[1], kh, 0.03),
                    "grzyb_w", "matowy", gora=(0.4, 0.03), faza=0.0)
        p.blok("Kropka w galarecie " + sc, (u + 0.13 * (1 if eu[0] + eu[2] > 0 else -1), v + th + 0.12, 0.035),
               (0.16, 0.11, 0.02), "trzon_w", "matowy", faza=0.0)


# ------------------------------------------------------------------------------------------------- model
def zbuduj():
    p = Postac(ID, "Leśny Slime", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # --- szkielet
    p.kosc("Cialo", "Root", staw=(0, 0, 0), dl=0.6)
    p.kosc("Dol", "Cialo", staw=(0, 0, 0), czesc=(W, H, D), srodek=(0, H / 2, 0), dl=0.8)
    p.kosc("Gora", "Cialo", staw=(0, H, 0), dl=0.5)
    p.kosc("Oczy", "Cialo", staw=OCZY, dl=0.3)
    p.kosc("Powieki", "Cialo", staw=POWIEKI, dl=0.3)
    p.kosc("UstaO", "Cialo", staw=USTA_O, dl=0.3)
    for n, (st, _) in BOKI.items():
        p.kosc(n, "Cialo", staw=st, dl=0.3)
    p.kosc("Lisc", "Cialo", staw=LISC, dl=0.3)
    p.kosc("Grzybek", "Cialo", staw=GRZYB, dl=0.3)
    p.kosc("Kula", "Cialo", staw=KULA, dl=0.3)
    p.kosc("Plusk", "Cialo", staw=PLUSK_STAW, dl=0.3)
    for n, (x, z, r) in KROPLE.items():
        p.kosc(n, "Root", staw=(x, 0, z), dl=0.25)
    p.skoruj("Dol", "Gora", 0.0, H)

    _galareta(p)
    _twarz(p)
    _ruchome(p)

    # punkty zaczepienia dla gry: podążanie, tabliczka z imieniem, pysk (start kuli), kałuża (efekt rozprysku)
    p.zaczep("RootAttachment", "Cialo", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Gora", (0, 0.05, 0))
    p.zaczep("PyskAttachment", "UstaO", (0, 0, 0.3))
    p.zaczep("PluskAttachment", "Plusk", (0, 0.05, 0))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


def _galareta(p):
    with p.na("Dol", od="srodek"):
        p.blok("Galareta", (0, 0, 0), (W, H, D), "skorupka", "poswiata", faza=FAZA)
        sx, sy, sz = W - 2 * FAZA + 0.06, H - 2 * FAZA + 0.06, D - 2 * FAZA + 0.06
        p.blok("Rdzen przod", (0, 0, D / 2 + 0.01), (sx, sy, 0.02), "rdzen", "poswiata", faza=0.0)
        p.blok("Rdzen tyl", (0, 0, -D / 2 - 0.01), (sx, sy, 0.02), "rdzen_cien", "poswiata", faza=0.0)
        for zn in (1, -1):
            p.blok("Rdzen bok", (zn * (W / 2 + 0.01), 0, 0), (0.02, sy, sz), "rdzen_cien", "poswiata", faza=0.0)
        p.blok("Wierzch", (0, H / 2 + 0.01, 0), (sx, 0.02, sz), "rdzen", "poswiata", faza=0.0)
        # liść i grzybek „widziane przez galaretę” — rzuty z jednego położenia w środku
        for sc in ("bokL", "bokP", "tyl", "wierzch"):
            _rzut_lisc(p, sc)
        for sc in ("bokL", "bokP", "tyl", "wierzch"):
            _rzut_grzyb(p, sc)
        # pęcherzyki powietrza i odblask w lewym górnym rogu przodu (od widza)
        zf = D / 2 + 0.03
        p.blok("Odblask", (-W / 2 + FAZA + 0.26, H / 2 - FAZA - 0.14, zf), (0.5, 0.13, 0.03), "odblask",
               "swiecacy", rot=(0, 0, 40), faza=0.0)
        p.blok("Odblask kropka", (-W / 2 + FAZA + 0.62, H / 2 - FAZA - 0.02, zf), (0.13, 0.13, 0.03), "odblask",
               "swiecacy", faza=0.0)
        for i, (sc, u, v, r) in enumerate((("bokL", 0.75, -0.55, 0.16), ("bokL", 0.45, -0.25, 0.09),
                                            ("bokP", -0.2, 0.75, 0.14), ("tyl", -0.75, 0.7, 0.15),
                                            ("wierzch", -0.75, 0.7, 0.13))):
            obr, eu, ev, odl = SCIANY[sc]
            with p.uklad(pos=tuple(NORMALNE[sc][i2] * (odl + 0.02) for i2 in range(3)), obrot=obr):
                p.walec("Babel %d" % i, (u, v, 0.015), (r, 0.03, r), "odblask", "poswiata", rot=(90, 0, 0),
                        faza=0.0, segm=8)


def _twarz(p):
    """Złośliwa mina: oczy jak u peta, ale przycięte skośnymi powiekami w „V” z grubą kreską; krzywy uśmieszek
    z dwoma kłami i kroplą kwasu w kąciku."""
    with p.na("Dol", od="srodek"):
        yo, yu, zp = YO - H / 2, YU - H / 2, D / 2 + 0.02
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * XO
            # gruba brew wzdłuż skośnej góry oka
            c, sn = math.cos(math.radians(zn * 16)), math.sin(math.radians(zn * 16))
            p.blok("Brew " + s, (x - 0.31 * sn, yo + 0.31 * c, zp + 0.05), (0.86, 0.15, 0.03), "tusz", "polysk",
                   rot=(0, 0, zn * 16), faza=0.0)
        # krzywy uśmieszek: kącik po stronie +X wyżej
        p.ostroslup("Usta", (0.02, yu - 0.08, zp + 0.01), (1.06, 0.36, 0.03), "tusz", "polysk",
                    rot=(0, 0, 187), gora=(0.56, 0.03), faza=0.02)
        for zn in (1, -1):
            p.ostroslup("Kiel", (zn * 0.26 + 0.02, yu + 0.0 + zn * 0.03, zp + 0.035), (0.13, 0.15, 0.02),
                        "odblask", "polysk", rot=(0, 0, 187), gora=(0.0, 0.02), faza=0.0)
        # kropla kwasu w kąciku (po stronie −X, niższym)
        p.kula("Slina", (-0.2, yu - 0.33, zp + 0.035), (0.13, 0.17, 0.04), "kwas", "swiecacy", segm=8)
        p.ostroslup("Slina szpic", (-0.2, yu - 0.23, zp + 0.035), (0.09, 0.08, 0.03), "kwas", "swiecacy",
                    gora=(0.0, 0.03), faza=0.0)


def _ruchome(p):
    # --- oczy (sztywne, na własnej kości): przy mrugnięciu chowają się w galaretę, a na ich miejsce wychodzą
    #     kreski zamkniętych oczu. Brwi zostają na galarecie.
    with p.na("Oczy"):
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * XO
            kat = 180 + zn * 16          # wewnętrzny koniec niżej = złośliwe „V”
            # oko: odwrócony, przechylony trapez (szeroka skośna góra, węższy dół), wystaje 0,035 przed ścianę
            p.ostroslup("Oko " + s, (x, 0, 0.035), (0.7, 0.54, 0.03), "tusz", "polysk", rot=(0, 0, kat),
                        gora=(0.4, 0.03), faza=0.02)
            # błyski: większy pod zewnętrzną częścią brwi, mały niżej przy środku
            p.walec("Blysk " + s, (x + zn * 0.12, 0.03, 0.06), (0.19, 0.02, 0.21), "odblask", "swiecacy",
                    rot=(90, 0, 0), faza=0.0, segm=8)
            p.walec("Blysk maly " + s, (x - zn * 0.06, -0.15, 0.06), (0.08, 0.02, 0.08), "odblask",
                    "swiecacy", rot=(90, 0, 0), faza=0.0, segm=8)
    # --- zamknięte oczy: gruba kreska wygięta w dół na zewnętrznym końcu (schowane tuż pod przednią ścianą)
    with p.na("Powieki"):
        for zn, s in ((1, "L"), (-1, "P")):
            kat = zn * 16
            sn, c = math.sin(math.radians(kat)), math.cos(math.radians(kat))
            p.blok("Zamkniete oko " + s, (zn * XO, 0.0, 0.0), (0.56, 0.1, 0.03), "tusz", "polysk",
                   rot=(0, 0, kat), faza=0.0)
            p.blok("Zamkniete oko koniec " + s, (zn * XO + 0.3 * c + 0.03 * zn, 0.3 * sn - 0.06, 0.0),
                   (0.18, 0.1, 0.03), "tusz", "polysk", rot=(0, 0, kat - zn * 50), faza=0.0)
    # --- szeroko otwarta paszcza (schowana za ustami)
    with p.na("UstaO"):
        p.ostroslup("Paszcza", (0, 0, 0), (1.0, 0.7, 0.04), "tusz", "polysk", rot=(0, 0, 180), gora=(0.56, 0.04),
                    faza=0.02)
        for zn in (1, -1):
            p.ostroslup("Kiel duzy", (zn * 0.27, 0.24, 0.03), (0.14, 0.18, 0.02), "odblask", "polysk",
                        rot=(0, 0, 180), gora=(0.0, 0.02), faza=0.0)
        p.walec("Kwas w paszczy", (0.0, -0.17, 0.03), (0.42, 0.02, 0.22), "kwas", "swiecacy", rot=(90, 0, 0),
                faza=0.0, segm=8)
    # --- brzuszki (schowane tuż pod ścianą; wysuwają się przy zgnieceniu, przy upadku robią płaty kałuży)
    #     Kształt: spłaszczona soczewka (elipsoida) — z boku czyta się jak miękkie wybrzuszenie, nie jak uchwyt.
    for n, (st, (nx, _, nz)) in BOKI.items():
        with p.na(n):
            hb = 0.6 if n == "Przod" else H_BRZ
            if nx:
                p.kula("Brzuszek " + n, (0, 0, 0), (T_BRZ, hb, D - 0.9), "skorupka", "poswiata", segm=12)
            else:
                dl = W - 1.4 if n == "Przod" else W - 0.9      # przedni płat krótszy: nie zasłania twarzy w kałuży
                p.kula("Brzuszek " + n, (0, 0, 0), (dl, hb, T_BRZ), "skorupka", "poswiata", segm=12)
    # --- prawdziwy liść (płaski; w środku galarety, widać go po rozlaniu)
    with p.na("Lisc"):
        p.kula("Lisc", (0, 0, 0), (LISC_DL, 0.05, LISC_SZ), "lisc", "matowy", rot=(0, 25, 0), segm=8)
        p.blok("Lisc zylka", (0, 0.03, 0), (LISC_DL * 0.8, 0.02, 0.05), "lisc_w", "matowy", rot=(0, 25, 0),
               faza=0.0)
        p.blok("Lisc ogonek", (-0.62 * math.cos(math.radians(25)), 0.0, 0.62 * math.sin(math.radians(25))),
               (0.22, 0.05, 0.05), "lisc_w", "matowy", rot=(0, 25, 0), faza=0.0)
    # --- prawdziwy grzybek
    th, kh = GRZYB_H
    with p.na("Grzybek"):
        p.walec("Trzon", (0, th / 2, 0), (GRZYB_SZ[0], th, GRZYB_SZ[0]), "trzon", "matowy", faza=0.02, segm=8)
        p.stozek("Kapelusz", (0, th + kh / 2 - 0.04, 0), (GRZYB_SZ[1], kh, GRZYB_SZ[1]), "grzyb", "zwykly", gora=0.45, segm=8)
        p.blok("Kropka 1", (0.2, th + 0.13, 0.23), (0.13, 0.09, 0.04), "trzon", "matowy", rot=(-30, 40, 0),
               faza=0.0)
        p.blok("Kropka 2", (-0.06, th + kh - 0.03, 0.0), (0.14, 0.04, 0.14), "trzon", "matowy", faza=0.0)
    # --- kula kwasu
    with p.na("Kula"):
        p.kula("Kula kwasu", (0, 0, 0), R_KULA * 2, "kwas", "swiecacy", segm=8)
        p.stozek("Kula ogonek", (0, R_KULA * 0.75, -0.08), (0.24, 0.3, 0.24), "kwas", "swiecacy", rot=(-35, 0, 0),
                 gora=0.0, segm=8)
        p.walec("Kula blysk", (-0.1, 0.12, R_KULA - 0.005), (0.13, 0.02, 0.15), "odblask", "swiecacy",
                rot=(90, 0, 0), faza=0.0, segm=8)
    # --- kałuża kwasu z koroną rozprysku (schowana w podstawie galarety)
    with p.na("Plusk"):
        p.walec("Kaluza", (0, 0.025, 0), (1.3, 0.05, 1.0), "kwas", "swiecacy", faza=0.0, segm=12)
        p.walec("Kaluza 2", (0.42, 0.02, 0.3), (0.62, 0.04, 0.52), "kwas", "swiecacy", faza=0.0, segm=8)
        p.walec("Kaluza 3", (-0.45, 0.02, -0.25), (0.5, 0.04, 0.44), "kwas", "swiecacy", faza=0.0, segm=8)
        for i in range(6):
            a = math.radians(30 + 60 * i)
            p.stozek("Korona %d" % i, (0.5 * math.sin(a), 0.1, 0.4 * math.cos(a)), (0.12, 0.16, 0.12), "kwas",
                     "swiecacy", gora=0.0, segm=4)
        p.walec("Kaluza blysk", (-0.15, 0.055, 0.12), (0.22, 0.02, 0.12), "odblask", "swiecacy", faza=0.0, segm=8)
    # --- lepkie krople przy podstawie
    for n, (x, z, r) in KROPLE.items():
        with p.na(n):
            _kropla(p, n, (0, r * 0.5, 0), r)


# ------------------------------------------------------------------------------------------------- animacje
BRAK, MRUG = 0.0, 1.0                  # oczy: otwarte / zamknięte
OCZY_DZ, POW_DZ = -0.12, 0.165        # zamknięcie: oczy w głąb, kreski do przodu (0,065 przed ścianą)
ANIM = ("Cialo", "Gora", "Oczy", "Powieki", "UstaO", "BokL", "BokP", "Przod", "Tyl", "Lisc", "Grzybek", "Kula", "Plusk",
        "KroplaL", "KroplaP", "KroplaT")
KR_OTW = 0.28           # wysunięcie paszczy (otwarta)
# wysokość (od ziemi), według której schowane bryły jadą z galaretą
Y_REF = {"Oczy": OCZY[1], "Powieki": POWIEKI[1], "UstaO": USTA_O[1], "Lisc": LISC[1], "Grzybek": GRZYB[1] + 0.3, "Kula": KULA[1],
         "Plusk": 0.12}
for _n, (_st, _) in BOKI.items():
    Y_REF[_n] = _st[1]


def poza(g=0.0, b=0.0, pw=BRAK, kr=0.0, cp=(0, 0, 0), cr=(0, 0, 0), dod=None, krople=None):
    """Poza kluczowa. g = przesunięcie góry galarety (− zgniecenie, + rozciągnięcie); b = wysunięcie brzuszków;
    pw = zamknięcie oczu (0 otwarte … 1 zamknięte); kr = wysunięcie paszczy; cp/cr = przesunięcie i obrót całego ciała; dod = {kość:
    {"przes": …, "obrot": …}} dokładane do wyliczonego; krople = {kość: przes}."""
    out = {n: [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)] for n in ANIM}       # [obrot, przes]
    out["Cialo"] = [tuple(cr), tuple(cp)]
    out["Gora"][1] = (0.0, g, 0.0)
    for n, y in Y_REF.items():
        out[n][1] = (0.0, g * y / H, 0.0)
    for n, (st, (nx, _, nz)) in BOKI.items():
        bb = 0.0 if n == "Przod" else b          # pod twarzą brzuszek wyglądał jak listwa — zostaje schowany
        out[n][1] = (nx * bb, g * st[1] / H, nz * bb)
    out["Oczy"][1] = (0.0, out["Oczy"][1][1], OCZY_DZ * pw)
    out["Powieki"][1] = (0.0, out["Powieki"][1][1], POW_DZ * pw)
    out["UstaO"][1] = (0.0, out["UstaO"][1][1], kr)
    for n, v in (dod or {}).items():
        if "przes" in v:
            out[n][1] = tuple(out[n][1][i] + v["przes"][i] for i in range(3))
        if "obrot" in v:
            out[n][0] = tuple(out[n][0][i] + v["obrot"][i] for i in range(3))
    for n, v in (krople or {}).items():
        out[n][1] = tuple(v)
    return out


def _podnies(out):
    """Galareta nie wchodzi pod ziemię: przy przechyle ciało unosi się na krawędzi podstawy."""
    R = macierz_obrotu(*out["Cialo"][0])
    cp = out["Cialo"][1]
    mn = 0.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            for q in ((sx * (W / 2 - FAZA), 0.0, sz * (D / 2 - FAZA)), (sx * W / 2, FAZA, sz * (D / 2 - FAZA)),
                      (sx * (W / 2 - FAZA), FAZA, sz * D / 2)):
                mn = min(mn, razy_wektor(R, q)[1] + cp[1])
    if mn < 0:
        out["Cialo"][1] = (cp[0], cp[1] - mn, cp[2])


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


def _sekwencja(k, klucze, po=None, stale=None):
    """Klucz w KAŻDEJ klatce. klucze = [(klatka, poza, tryb odcinka do następnej)]: "s" = łagodne wejście i wyjście,
    "l" = jednostajnie (uderzenie), "cr" = płynnie przez pozę (w pętli zawija się). po(f, out) — dopiski w klatce.
    stale = {kość: [klatki]} — w tych klatkach klucz „stale” (skok bez przejścia, np. schowek → miejsce plusku)."""
    n = len(klucze)
    petla = k.petla

    def sasiad(i):
        if petla:
            if i < 0:
                return i + n - 1
            if i > n - 1:
                return i - n + 1
            return i
        return max(0, min(n - 1, i))

    f0, f1 = int(klucze[0][0]), int(klucze[-1][0])
    for f in range(f0, f1 + 1):
        i = max(j for j in range(n - 1) if klucze[j][0] <= f) if f < f1 else n - 2
        t = (f - klucze[i][0]) / float(klucze[i + 1][0] - klucze[i][0])
        tryb = klucze[i][2]
        out = {}
        for nb in ANIM:
            war = []
            for ch in (0, 1):
                v = []
                for j in range(3):
                    if tryb == "cr":
                        a, b_, c, d = (klucze[sasiad(i - 1)][1][nb][ch][j], klucze[i][1][nb][ch][j],
                                       klucze[i + 1][1][nb][ch][j], klucze[sasiad(i + 2)][1][nb][ch][j])
                        v.append(_cr(a, b_, c, d, t))
                    else:
                        e = t if tryb == "l" else t * t * (3 - 2 * t)
                        a, c = klucze[i][1][nb][ch][j], klucze[i + 1][1][nb][ch][j]
                        v.append(a + (c - a) * e)
                war.append(tuple(v))
            out[nb] = war
        _podnies(out)
        if po:
            po(f, out)
        for nb, (ob, pr) in out.items():
            wyg = "stale" if stale and f in stale.get(nb, ()) else "liniowo"
            k.klucz(f, nb, obrot=tuple(round(x, 2) for x in ob), przes=tuple(round(x, 4) for x in pr), wyg=wyg)
    return k


def _lokalnie(out, kosc_staw, cel):
    """Przesunięcie kości-dziecka Ciała, które stawia jej staw w punkcie `cel` (świat)."""
    R = macierz_obrotu(*out["Cialo"][0])
    cp = out["Cialo"][1]
    d = tuple(cel[i] - cp[i] for i in range(3))
    RT = tuple(tuple(R[j][i] for j in range(3)) for i in range(3))
    q = razy_wektor(RT, d)
    return tuple(q[i] - kosc_staw[i] for i in range(3))


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def _krople_cykl(k, amp=1.0, czestosc=2):
    for i, (n, (x, z, r)) in enumerate(KROPLE.items()):
        k.cykl(n, "przes", (0, 0.09 * amp, 0), czestosc=czestosc, faza=i / 3.0, srodek=(0, 0.09 * amp, 0))


def idle(p, dl=60):
    """Spoczynek (2 s): ciężki oddech galarety (niżej-szerzej / wyżej-węziej), lekki przechył w przód jak przed
    skokiem, jedno mrugnięcie, krople podskakują na zmianę."""
    k = p.klip("idle", dl, petla=True)
    klucze = [
        (0, poza(0.0, 0.0, cr=(2, 0, 0)), "cr"),
        (15, poza(-0.14, 0.03, cr=(4, 0, 1.5)), "cr"),
        (30, poza(0.0, 0.0, cr=(2, 0, 0)), "cr"),
        (42, poza(0.06, -0.02, cr=(1, 0, -1.5)), "s"),
        (44, poza(0.065, -0.02, MRUG, cr=(1, 0, -1.5)), "s"),
        (47, poza(0.06, -0.02, cr=(1, 0, -1.5)), "cr"),
        (dl, poza(0.0, 0.0, cr=(2, 0, 0)), "cr"),
    ]
    _sekwencja(k, klucze)
    k.kanaly = {kk: v for kk, v in k.kanaly.items() if not kk[0].startswith("Kropla")}
    _krople_cykl(k)
    return k


def ruch(p, dl=24):
    """Podskok naprzód (0,8 s): przysiad, wybicie z pochyleniem w przód, lot, lądowanie ze zgnieceniem."""
    k = p.klip("ruch", dl, petla=True)
    klucze = [
        (0, poza(-0.35, 0.14, BRAK, cr=(-3, 0, 0)), "s"),
        (5, poza(0.32, -0.05, cp=(0, 0.35, 0), cr=(8, 0, 0)), "cr"),
        (11, poza(0.12, 0.0, cp=(0, 1.05, 0), cr=(4, 0, 0)), "cr"),
        (16, poza(0.22, -0.03, cp=(0, 0.45, 0), cr=(-4, 0, 0)), "l"),
        (19, poza(-0.5, 0.2, BRAK, cr=(-2, 0, 0)), "s"),
        (dl, poza(-0.35, 0.14, BRAK, cr=(-3, 0, 0)), "s"),
    ]
    _sekwencja(k, klucze)
    k.kanaly = {kk: v for kk, v in k.kanaly.items() if not kk[0].startswith("Kropla")}
    _krople_cykl(k, 0.8, 2)              # krople zostają na ziemi (lepkie ślady), tylko drgają
    return k


def atak(p, dl=30):
    """Uderzenie całym ciałem (1 s): przysiad z odchyleniem w tył, wybicie, trafienie w kl. 13 (rozpłaszczenie
    na celu z otwartą paszczą), powrót."""
    k = p.klip("atak", dl, petla=False)
    klucze = [
        (0, poza(), "s"),
        (8, poza(-0.6, 0.2, BRAK, cp=(0, 0, -0.4), cr=(-9, 0, 0)), "l"),
        (11, poza(0.38, -0.06, BRAK, KR_OTW, cp=(0, 0.45, 1.1), cr=(12, 0, 0)), "l"),
        (13, poza(-0.4, 0.18, BRAK, KR_OTW, cp=(0, 0.1, 1.9), cr=(6, 0, 0)), "s"),
        (18, poza(0.08, 0.0, BRAK, KR_OTW, cp=(0, 0.0, 1.65), cr=(1, 0, 0)), "s"),
        (25, poza(0.05, 0.0, cp=(0, 0, 0.25)), "s"),
        (dl, poza(), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def umiejetnosc(p, dl=66):
    """Kwaśny plusk (2,2 s): nadyma się (wyżej i szerzej), otwiera paszczę z świecącą kulą kwasu (kl. 14–18), pluje (gwałtowne zgniecenie
    w przód, paszcza otwarta), kula leci łukiem i w kl. 31 rozpryskuje się w kałużę ok. 4,3 studa przed nim; slime
    odskakuje w tył i wraca; kałuża wsiąka w ziemię."""
    k = p.klip("umiejetnosc", dl, petla=False)
    # kula najpierw podchodzi w środku, potem staje w otwartej paszczy (świecąca kula kwasu w pysku = czytelna
    # zapowiedź plunięcia, inna niż atak)
    w_srodku = {"Kula": {"przes": (0, 0.0, 0.2)}}
    w_paszczy = {"Kula": {"przes": (0, USTA_O[1] - KULA[1], ZF - 0.05 - KULA[2])}}
    kr_n = KR_OTW * 0.8
    klucze = [
        (0, poza(), "s"),
        (9, poza(0.5, 0.22, BRAK, cr=(-6, 0, 0), dod=w_srodku), "s"),
        (14, poza(0.72, 0.32, BRAK, kr_n, cr=(-9, 0, 0), dod=w_paszczy), "s"),
        (18, poza(0.66, 0.3, BRAK, kr_n, cr=(-8, 0, 0), dod=w_paszczy), "l"),
        (21, poza(-0.45, 0.2, BRAK, KR_OTW, cp=(0, 0, 0.3), cr=(10, 0, 0)), "s"),
        (26, poza(0.15, 0.0, BRAK, KR_OTW, cp=(0, 0, -0.3), cr=(-3, 0, 0)), "s"),
        (31, poza(-0.08, 0.04, cr=(0, 0, 0)), "s"),
        (38, poza(0.0, 0.0), "s"),
        (dl, poza(0.0, 0.0), "s"),
    ]
    F_WYLOT, F_PLUSK = 21, 31
    z0 = ZF + 0.65                     # kula wylatuje tuż przed paszczą (ciało jest wtedy wysunięte o 0,3)
    stale = {"Plusk": [F_PLUSK - 1, dl - 1], "Kula": [F_PLUSK]}

    def po(f, out):
        if F_WYLOT <= f < F_PLUSK:
            t = (f - F_WYLOT) / float(F_PLUSK - F_WYLOT)
            y = YU * (1 - t) + R_KULA * t + 4 * t * (1 - t) * 1.3       # łuk: ok. 1,3 studa nad prostą
            z = z0 + (PLUSK_Z - z0) * t
            out["Kula"][1] = _lokalnie(out, KULA, (0.0, y, z))
        elif f == F_PLUSK:
            out["Kula"][1] = _lokalnie(out, KULA, (0.0, -0.4, PLUSK_Z))     # wpada w kałużę (pod ziemię)
        if F_PLUSK <= f < dl:
            # kałuża: w kl. 31 skok ze schowka; w kl. 46–56 wsiąka w ziemię (cała, z koroną), potem czeka pod ziemią
            zejscie = 0.0 if f < 46 else -0.36 * min(1.0, (f - 46) / 10.0)
            out["Plusk"][1] = _lokalnie(out, PLUSK_STAW, (0.0, zejscie, PLUSK_Z))
    _sekwencja(k, klucze, po=po, stale=stale)
    return k


def trafienie(p, dl=18):
    """Reakcja na cios (0,6 s): szarpnięcie w tył z przechyłem i zgnieceniem, zaciśnięte oczy, odbicie."""
    k = p.klip("trafienie", dl, petla=False)
    klucze = [
        (0, poza(), "l"),
        (3, poza(-0.32, 0.14, MRUG, 0.0, cp=(0, 0, -0.5), cr=(-13, 0, 0)), "s"),
        (8, poza(0.2, -0.04, BRAK, cp=(0, 0, -0.38), cr=(4, 0, 0)), "s"),
        (13, poza(-0.06, 0.03, cp=(0, 0, -0.12), cr=(-1, 0, 0)), "s"),
        (dl, poza(), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def unik(p, dl=27):
    """Unik (0,9 s): przysiad, odskok w lewo (+X) z przechyłem, lądowanie, powrót ślizgiem na miejsce."""
    k = p.klip("unik", dl, petla=False)
    klucze = [
        (0, poza(), "s"),
        (4, poza(-0.35, 0.14, BRAK, cr=(0, 0, 6)), "l"),
        (7, poza(0.3, -0.04, cp=(0.8, 0.55, 0), cr=(0, 0, -10)), "s"),
        (10, poza(0.1, 0.0, cp=(1.5, 0.45, 0), cr=(0, 0, -6)), "l"),
        (13, poza(-0.35, 0.14, BRAK, cp=(1.7, 0, 0), cr=(0, 0, 4)), "s"),
        (21, poza(0.05, 0.0, cp=(0.25, 0, 0), cr=(0, 0, 5)), "s"),
        (dl, poza(), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): szarpnięcie, chwianie, zamknięte oczy, rozlanie w płaską kałużę z płatami (brzuszki);
    liść kładzie się na kałuży, grzybek wypływa i staje na niej krzywo. Kończy się leżeniem."""
    k = p.klip("upadek", dl, petla=False)
    G_KON = -(H - 0.45)                # galareta: 0,45 studa wysokości
    yk = H + G_KON                     # wierzch kałuży
    tyl = (0, 0, -0.4)

    def pod(g):
        """Kula kwasu opada na dno (spód na ziemi, środek na y = R_KULA): po rozlaniu wystaje z kałuży jak
        świecące kwaśne „żółtko” z ogonkiem — nic nie schodzi pod ziemię."""
        return {"przes": (0, R_KULA + 0.005 - KULA[1] - g * KULA[1] / H, -0.1), "obrot": (-10, 0, 0)}

    lisc_kon = {"przes": (0.1, yk + 0.06 - LISC[1] - G_KON * LISC[1] / H, 0.1), "obrot": (10, 30, 6)}
    yg = Y_REF["Grzybek"]
    grzyb_kon = {"przes": (0.1, yk - 0.02 - GRZYB[1] - G_KON * yg / H, 0.35), "obrot": (0, 0, -14)}

    def pol(v):
        return {"przes": tuple(x * 0.5 for x in v["przes"]), "obrot": tuple(x * 0.5 for x in v["obrot"])}

    def plat(n, dx, dz, obr):
        """Brzuszek położony płasko jako płat kałuży: środek na y = 0,25 (soczewka 0,5 grubości leży na ziemi)."""
        sy = BOKI[n][0][1]
        return {"przes": (dx, T_BRZ / 2 - sy * (1 + G_KON / H), dz), "obrot": obr}

    platy = {"BokL": plat("BokL", 0.0, 0.35, (0, 35, 90)),       # rz = 90: cienka oś soczewki pionowo
             "BokP": plat("BokP", 0.0, -0.3, (0, -25, 90)),
             "Przod": plat("Przod", 0.95, 0.5, (90, -35, 0)),    # rx = 90: cienka oś pionowo; z boku twarzy
             "Tyl": plat("Tyl", -0.3, 0.0, (90, 20, 0))}

    def lezy(b):
        """Kałuża: oczy schowane i położone płasko w środku (zostają kreski zamkniętych oczu), paszcza leży płasko,
        brzuszki rozjechane na boki i położone jako płaskie płaty, liść i grzybek na wierzchu."""
        d = {"Kula": pod(G_KON),
             "Oczy": {"przes": (0, 0.25 - OCZY[1] * (1 + G_KON / H), -0.55), "obrot": (90, 0, 0)},
             "UstaO": {"obrot": (90, 0, 0)}, "Lisc": lisc_kon, "Grzybek": grzyb_kon}
        d.update(platy)
        return d

    kropl_kon = {"KroplaL": (0.5, 0, 0.3), "KroplaP": (-0.45, 0, 0.35), "KroplaT": (0.3, 0, -0.45)}
    klucze = [
        (0, poza(), "l"),
        (4, poza(-0.3, 0.12, MRUG, cp=(0, 0, -0.45), cr=(-12, 0, 0)), "s"),
        (11, poza(0.25, -0.04, MRUG, cp=tyl, cr=(0, 0, 7)), "s"),
        (17, poza(-0.2, 0.08, MRUG, cp=tyl, cr=(0, 0, -6)), "s"),
        (22, poza(0.1, 0.0, MRUG, cp=tyl, cr=(0, 0, 3), dod={"Kula": pod(0.1)}), "s"),
        (27, poza(-0.5, 0.15, MRUG, -0.25, cp=tyl, dod={"Kula": pod(-0.5)}), "s"),
        (36, poza(-1.5, 0.3, MRUG, -0.25, cp=tyl, dod=dict({"Kula": pod(-1.5), "Lisc": pol(lisc_kon),
                                                          "Grzybek": pol(grzyb_kon),
                                                          "Oczy": {"przes": (0, 0, -0.2)},
                                                          "UstaO": {"obrot": (90, 0, 0)}},
                                                         **{n: pol(v) for n, v in platy.items()})), "s"),
        (46, poza(G_KON, 0.5, MRUG, -0.25, cp=tyl, dod=lezy(0.5), krople=kropl_kon), "s"),
        (dl, poza(G_KON, 0.52, MRUG, -0.25, cp=tyl, dod=lezy(0.52), krople=kropl_kon), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def wiwat(p, dl=40):
    """Wiwat po wygranej (pętla 1,33 s): dwa podskoki z otwartą paszczą, kołysanie na boki."""
    k = p.klip("wiwat", dl, petla=True)
    klucze = [
        (0, poza(-0.4, 0.16, BRAK, KR_OTW, cr=(-4, 0, 0)), "s"),
        (5, poza(0.35, -0.05, BRAK, KR_OTW, cp=(0, 0.5, 0), cr=(-6, 12, 5)), "cr"),
        (10, poza(0.12, 0.0, BRAK, KR_OTW, cp=(0, 1.0, 0), cr=(-8, 15, 6)), "cr"),
        (15, poza(0.25, -0.03, BRAK, KR_OTW, cp=(0, 0.35, 0), cr=(-4, 8, 3)), "l"),
        (20, poza(-0.4, 0.16, BRAK, KR_OTW, cr=(-4, 0, 0)), "s"),
        (25, poza(0.35, -0.05, BRAK, KR_OTW, cp=(0, 0.5, 0), cr=(-6, -12, -5)), "cr"),
        (30, poza(0.12, 0.0, BRAK, KR_OTW, cp=(0, 1.0, 0), cr=(-8, -15, -6)), "cr"),
        (35, poza(0.25, -0.03, BRAK, KR_OTW, cp=(0, 0.35, 0), cr=(-4, -8, -3)), "l"),
        (dl, poza(-0.4, 0.16, BRAK, KR_OTW, cr=(-4, 0, 0)), "s"),
    ]

    _sekwencja(k, klucze)
    k.kanaly = {kk: v for kk, v in k.kanaly.items() if not kk[0].startswith("Kropla")}
    _krople_cykl(k, 0.8, 2)              # krople zostają na ziemi (lepkie ślady), tylko drgają
    return k
