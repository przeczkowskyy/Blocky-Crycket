# -*- coding: utf-8 -*-
"""WĄŻ STU LIAN — strażnik Dżungli: ogromny wąż spleciony z lian i pnączy, z wielkim czerwono-żółtym kwiatem na
głowie jak kaptur, zwinięty w spiralę; ok. 16,5 studa w zwoju i ok. 11 szerokości (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/waz_stu_lian.py --wyj <folder> --klip ryk

Opis z zarysu biomów (swiat/biomy/PLAN_BIOMOW.md, rozdz. „2. Dżungla”): ogromny wąż spleciony z lian, z kwiatem na
głowie, zwinięty w spiralę (18 w zwoju). Strażnik biomu. Umiejętności silnika: `zatruta_strzala` (plucie jadem
z paszczy — punkt Pocisk w paszczy) i `rozszarpanie` (ukąszenie z szarpaniem łbem).

Sylwetka (z daleka): szeroki, niski zwój z grubego ciała (półtora pierścienia leży na ziemi, węższy pierścień na
nim), z jego środka wznosi się szyja łukiem w przód; na szczycie trójkątny łeb z żółtymi oczami, a za nim wachlarz
siedmiu wielkich czerwonych płatków z żółtą nasadą — jak kaptur kobry. Ciało to splot zielonych i brązowych lian
(spiralne pasma), z liśćmi, drobnymi kwiatami i kroplami rosy; od przodu szyi jasne łuski brzucha.

Paleta (Dżungla): liany 2FA34A / 1F7A36 / 6CCB4A, drewniane pasma pnie 5C3A22, łuski brzucha jasna zieleń, kwiaty
E5392B / F2B030 (kaptur, drobne kwiaty, oczy), turkus 2EC4B6 (krople rosy, środek kwiatu), paszcza i kły.

Szkielet (typ „stwor”):
    Root > Zwoj > {Ogon, Szyja1 > Szyja2 > Szyja3 > Glowa > {Szczeka > Jezyk, KapturL, KapturP, KapturG}}
- `Zwoj` niesie cały zwój (leży na ziemi); `Ogon` = koniec ogona po zewnętrznej stronie zwoju (drga);
- szyja na trzech kościach (fala w kształt litery S), `Glowa` z kłami, `Szczeka` z rozwidlonym językiem (`Jezyk`);
- kaptur z płatków na trzech kościach (lewa, prawa, góra) — rozkłada się w ataku, pluciu i ryku.

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: szyja faluje, język drga, kaptur oddycha), ruch (pętla 1,6 s: zwój kołysze się, szyja wije się
  na boki), atak (ukąszenie: szyja cofa się w S i wystrzela w przód, kły zatrzaskują się kl. 18, 1,2 s),
  umiejetnosc (plucie jadem: odchyla się, kaptur rozkłada się szeroko, paszcza otwarta — wyrzut łba w przód kl. 28,
  1,8 s), ukaszenie (rozszarpanie: wypad, ukąszenie kl. 16 i szarpanie łbem na boki, 1,6 s), trafienie (0,67 s),
  unik (szyja i łeb uchylają się w lewo o ok. 1,5 studa i wracają, 1,0 s), upadek (szyja chwieje się i pada
  w przód na ziemię, kaptur opada; 2,2 s, leży w ostatniej klatce), ryk (dokładnie 60 klatek = 2,0 s, pętla —
  gra go przelot kamery: prostuje szyję, kaptur rozłożony, paszcza otwarta, łeb drży).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "waz_stu_lian"

PALETA = {
    "liana": "2FA34A", "liana_ciemna": "1F7A36", "liana_jasna": "6CCB4A", "drewno": "5C3A22",
    "luska": "B9E68A", "lisc": "3DB04E", "platek": "E5392B", "platek_ciemny": "B32424",
    "platek_nasada": "F2B030", "kwiat": "E5392B", "kwiat_zolty": "F2B030", "rosa": "2EC4B6",
    "oko": "F2B030", "tusz": "17121F", "bialy": "FFFFFF", "kiel": "F4EEDC", "paszcza": "6E1420",
    "jezyk": "D9334A",
}

# chwile: ukąszenie (atak), wyrzut jadu (umiejetnosc), ukąszenie przy rozszarpaniu, szarpnięcie, największy unik
CHWILE = {"atak": 18, "umiejetnosc": 28, "ukaszenie": 16, "trafienie": 4, "unik": 14}

SLABOSCI = [
    "Kości Węża nie są R15 (własny szkielet: Root + 11 kości) — import do Roblox Studio nie był testowany.",
    "Zwój jest sztywny (jedna kość): wąż nie pełznie — ruch w miejscu to kołysanie zwoju i falowanie szyi.",
    "Szyja ma trzy sztywne odcinki: przy mocnym wygięciu na stykach widać schodki między klockami.",
    "Jadu nie ma w klipie: pocisk umiejętności zatruta_strzala rysuje odtwarzacz (dziś jako strzała z trucizną — "
    "wygląd plucia wymaga osobnego wpisu w Choreografie/Efekty3D, poza tym modułem).",
    "Kaptur z płatków to trzy sztywne grupy (bez wygięcia płatków); w upadku płatki lekko wchodzą w ziemię "
    "(leżą płasko).",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
ZC = -0.8                            # środek zwoju (z)
ZWOJ = (0.0, 1.05, ZC)
KAT_ZWOJU = 630.0                    # półtora obrotu + ćwierć (od czubka ogona do nasady szyi)
KONIEC_OGONA = 100.0                 # kąt, do którego sięga kość Ogon
SZYJA = [(0.0, 3.0, -3.3), (0.0, 6.3, -2.85), (0.0, 9.3, -1.25), (0.0, 11.6, 0.55)]
GLOWA = (0.0, 12.55, 1.45)
SKALA_LBA = 1.25                     # łeb modelowany w mniejszej skali i powiększony wokół stawu GLOWA


def _lb(v):
    """Punkt łba (modelowany w skali 1) -> model (powiększenie SKALA_LBA wokół stawu GLOWA)."""
    return tuple(GLOWA[i] + SKALA_LBA * (v[i] - GLOWA[i]) for i in range(3))


SZCZEKA = _lb((0.0, 12.45, 1.9))
JEZYK = _lb((0.0, 12.5, 3.9))
KAPTUR = (0.0, 13.45, 1.2)           # środek wachlarza płatków (za łbem)

GLOWNA = "Zwoj"
PLASKIE = ()
POMIN_ZIEMIA = ("Jezyk",)


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _zwoj(kat):
    """Oś ciała w zwoju: kat od czubka ogona (0) do nasady szyi (KAT_ZWOJU); zwraca (punkt, grubość)."""
    t = kat / KAT_ZWOJU
    r = 4.8 - 2.2 * t
    gr = 0.45 + 1.65 * min(1.0, kat / 150.0)
    w = min(1.0, max(0.0, (kat - 300.0) / 200.0))
    y = gr / 2.0 + 1.15 * w * w * (3 - 2 * w)       # zewnętrzny pierścień leży na ziemi, wewnętrzny na nim
    a = math.radians(-90.0 + kat)
    return (r * math.sin(a), y, ZC + r * math.cos(a)), gr


OS = {}


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Wąż Stu Lian", typ="stwor", skala=1.0, faza=0.08, paleta=PALETA)

    p.kosc("Zwoj", "Root", staw=ZWOJ, dl=1.0)
    p.kosc("Ogon", "Zwoj", staw=_zwoj(KONIEC_OGONA)[0], dl=0.6)
    p.kosc("Szyja1", "Zwoj", staw=SZYJA[0], dl=1.2)
    p.kosc("Szyja2", "Szyja1", staw=SZYJA[1], dl=1.2)
    p.kosc("Szyja3", "Szyja2", staw=SZYJA[2], dl=1.2)
    p.kosc("Glowa", "Szyja3", staw=GLOWA, dl=1.0)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.8)
    p.kosc("Jezyk", "Szczeka", staw=JEZYK, dl=0.4)
    p.kosc("KapturL", "Glowa", staw=(0.7, 13.45, 1.1), dl=0.6)
    p.kosc("KapturP", "Glowa", staw=(-0.7, 13.45, 1.1), dl=0.6)
    p.kosc("KapturG", "Glowa", staw=(0.0, 14.1, 1.1), dl=0.6)

    _cialo(p)
    _szyja(p)
    _glowa(p)
    _kaptur(p)

    p.zaczep("RootAttachment", "Zwoj", (-ZWOJ[0], -ZWOJ[1], -ZWOJ[2]))
    # cel trafienia: przód szyi na wysokości ok. 8 studów (łuski brzucha)
    p.zaczep("GlowaAttachment", "Szyja2", _roznica(SZYJA[1], (0.0, 8.0, -1.05)))
    # paszcza między kłami (Bron przy ukąszeniu, Pocisk = skąd leci jad)
    p.zaczep("PyskAttachment", "Glowa", _roznica(GLOWA, _lb((0.0, 12.55, 4.75))))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _odcinek(p, nazwa, a, b, gr, i, kolor_glowny, pasma=True, nad=0.18):
    """Odcinek ciała z lian: gruby klocek wzdłuż a→b (przekrój stoi prosto: oś X klocka zawsze poziomo, więc spód
    zwoju leży płasko na ziemi) i cieńsze pasma owinięte wokół niego pod zmiennym kątem. Zwraca (środek, obrót) —
    układ odcinka: oś Z wzdłuż ciała, X w bok (poziomo), −Y od przodu szyi."""
    d = tuple(b[j] - a[j] for j in range(3))
    L = math.sqrt(sum(x * x for x in d))
    sr = tuple((a[j] + b[j]) / 2.0 for j in range(3))
    rot = (math.degrees(math.asin(max(-1.0, min(1.0, -d[1] / L)))), math.degrees(math.atan2(d[0], d[2])), 0.0)
    with p.uklad(pos=sr, obrot=rot):
        p.blok(nazwa, (0, 0, 0), (gr, gr, L + 2 * nad), kolor_glowny, "matowy", faza=None)
        if pasma:
            pasy = (("liana_jasna", 0.0),) + ((("drewno", 180.0),) if i % 2 else ())
            for k, (kol, przes) in enumerate(pasy):
                al = i * 47.0 + przes
                if math.sin(math.radians(al)) < -0.3:
                    al += 180.0                                  # pasma tylko na wierzchu i bokach (nie pod ziemią)
                r = math.radians(al)
                off = gr * 0.44
                p.blok("%s pasmo %d" % (nazwa, k), (off * math.cos(r), off * math.sin(r), 0),
                       (gr * 0.26, gr * 0.26, L + 2 * nad * 0.8), kol, "matowy", rot=(10, 0, al), faza=0.0)
    return sr, rot


def _cialo(p):
    """Zwój z odcinków co 18°; co kilka odcinków liść, kwiatek albo kropla rosy na zewnętrznej stronie."""
    krok = 18.0
    n = int(KAT_ZWOJU / krok)
    for i in range(n):
        k0, k1 = i * krok, (i + 1) * krok
        a, gra = _zwoj(k0)
        b, grb = _zwoj(k1)
        gr = (gra + grb) / 2.0
        kosc = "Ogon" if k1 <= KONIEC_OGONA + 1e-6 else "Zwoj"
        kol = "liana" if i % 2 else "liana_ciemna"
        with _model(p, kosc):
            sr, rot = _odcinek(p, "Zwoj %d" % i, a, b, gr, i, kol, pasma=gr > 0.9, nad=0.1 + 0.12 * (gr > 1.5))
            if i % 4 == 2 and gr > 1.5:
                # liść na zewnątrz zwoju (w górę i na zewnątrz)
                kat = math.radians(-90.0 + (k0 + k1) / 2.0)
                naz = (math.sin(kat), 0.0, math.cos(kat))
                c = (sr[0] + naz[0] * gr * 0.5, sr[1] + gr * 0.42, sr[2] + naz[2] * gr * 0.5)
                with p.uklad(pos=c, obrot=(0, math.degrees(kat), 0)):
                    p.blok("Lisc zwoju %d" % i, (0, 0.25, 0.35), (0.7, 0.06, 1.0), "lisc", "matowy",
                           rot=(-35, 0, 0), faza=0.0)
                    p.blok("Zylka liscia zwoju %d" % i, (0, 0.27, 0.35), (0.07, 0.08, 0.9), "liana_jasna", "matowy",
                           rot=(-35, 0, 0), faza=0.0)
            if i % 7 == 4 and gr > 1.5:
                c = (sr[0], sr[1] + gr * 0.52, sr[2])
                with p.uklad(pos=c):
                    for j in range(5):
                        al = math.radians(j * 72)
                        p.blok("Kwiatek %d %d" % (i, j), (0.17 * math.cos(al), 0, 0.17 * math.sin(al)),
                               (0.22, 0.08, 0.22), "kwiat" if i % 2 else "kwiat_zolty", "matowy", rot=(0, j * 72, 0),
                               faza=0.0)
                    p.blok("Kwiatek %d srodek" % i, (0, 0.05, 0), (0.12, 0.06, 0.12), "kwiat_zolty" if i % 2 else "kwiat",
                           "matowy", faza=0.0)
            if i % 9 == 6 and gr > 1.5:
                p.kula("Rosa %d" % i, (sr[0], sr[1] + gr * 0.5, sr[2] + 0.3), 0.22, "rosa", "polysk", segm=6)
    # czubek ogona: pęk listków
    with _model(p, "Ogon"):
        c, _ = _zwoj(0.0)
        for j, (rx, ry) in enumerate(((-30, 60), (10, 100), (-60, 130))):
            with p.uklad(pos=c, obrot=(rx, ry, 0)):
                p.blok("Listek ogona %d" % j, (0, 0, 0.35), (0.4, 0.05, 0.75), "liana_jasna", "matowy", faza=0.0)


def _szyja(p):
    kosci = ("Szyja1", "Szyja2", "Szyja3")
    punkty = SZYJA + [GLOWA]
    licz = 0
    for k, kosc in enumerate(kosci):
        a, b = punkty[k], punkty[k + 1]
        g0 = 2.45 - 0.2 * k
        with _model(p, kosc):
            for s in range(3):
                t0, t1 = s / 3.0, (s + 1) / 3.0
                pa = tuple(a[j] + (b[j] - a[j]) * t0 for j in range(3))
                pb = tuple(a[j] + (b[j] - a[j]) * t1 for j in range(3))
                gr = g0 - 0.2 * (s / 3.0)
                kol = "liana" if licz % 2 else "liana_ciemna"
                sr, rot = _odcinek(p, "Szyja %d" % licz, pa, pb, gr, licz + 3, kol, nad=0.16)
                # łuski brzucha od przodu szyi
                with p.uklad(pos=sr, obrot=rot):
                    p.blok("Luska %d" % licz, (0, -gr * 0.5, 0), (gr * 0.62, 0.1, 0.95), "luska", "matowy",
                           faza=0.02)
                licz += 1
            if k == 1:
                p.blok("Lisc szyi", (1.05, 7.6, -2.0), (0.06, 0.6, 1.0), "lisc", "matowy", rot=(20, 0, -20),
                       faza=0.0)
                p.kula("Rosa szyi", (1.15, 7.9, -1.6), 0.2, "rosa", "polysk", segm=6)


def _lba(p, kosc):
    """Układ modelu na kości łba, powiększony o SKALA_LBA wokół stawu GLOWA (bryły łba podaje się w skali 1)."""
    return _model(p, kosc, pos=GLOWA)


def _glowa(p):
    with _lba(p, "Glowa"), p.uklad(skala=SKALA_LBA), p.uklad(pos=tuple(-v for v in GLOWA)):
        p.blok("Kark", (0, 12.75, 1.55), (2.0, 1.3, 1.2), "liana_ciemna", "matowy", faza=0.12)
        p.blok("Leb", (0, 13.0, 2.65), (2.4, 1.15, 2.0), "liana", "matowy", faza=0.15)
        p.blok("Pysk", (0, 12.9, 4.05), (1.8, 0.95, 1.3), "liana", "matowy", faza=0.12)
        p.blok("Czubek pyska", (0, 12.88, 4.75), (1.2, 0.75, 0.3), "liana_ciemna", "matowy", faza=0.06)
        p.blok("Grzbiet glowy", (0, 13.6, 2.7), (1.3, 0.12, 2.2), "liana_ciemna", "matowy", faza=0.03)
        p.blok("Pasmo glowy", (0.25, 13.62, 2.4), (0.25, 0.12, 2.4), "drewno", "matowy", rot=(0, 12, 0), faza=0.0)
        for zn in (1, -1):
            p.blok("Luk brwiowy", (zn * 0.82, 13.55, 3.15), (0.7, 0.22, 0.75), "liana_ciemna", "matowy",
                   rot=(0, zn * 12, -zn * 8), faza=0.04)
            p.blok("Oko", (zn * 1.08, 13.25, 3.25), (0.3, 0.42, 0.62), "oko", "polysk", faza=0.03)
            p.blok("Zrenica", (zn * 1.24, 13.25, 3.32), (0.04, 0.38, 0.12), "tusz", "polysk", faza=0.0)
            p.blok("Nozdrze", (zn * 0.32, 13.12, 4.9), (0.16, 0.1, 0.05), "tusz", faza=0.0)
            # kły (z przodu górnej szczęki, w dół)
            p.blok("Kiel", (zn * 0.48, 12.25, 4.55), (0.16, 0.6, 0.16), "kiel", "polysk", rot=(10, 0, 0), faza=0.02)
            p.blok("Liscie policzka", (zn * 1.2, 12.75, 2.2), (0.06, 0.55, 0.9), "lisc", "matowy",
                   rot=(-15, 0, zn * 15), faza=0.0)
        p.blok("Podniebienie", (0, 12.42, 3.3), (1.55, 0.06, 2.6), "paszcza", "matowy", faza=0.0)
    with _lba(p, "Szczeka"), p.uklad(skala=SKALA_LBA), p.uklad(pos=tuple(-v for v in GLOWA)):
        p.blok("Zuchwa", (0, 12.15, 3.2), (1.85, 0.5, 2.9), "liana", "matowy", faza=0.1)
        p.blok("Podgardle", (0, 11.95, 2.6), (1.5, 0.2, 2.0), "luska", "matowy", faza=0.04)
        p.blok("Wnetrze", (0, 12.42, 3.25), (1.5, 0.06, 2.5), "paszcza", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kiel dolny", (zn * 0.55, 12.5, 4.35), (0.12, 0.3, 0.12), "kiel", "polysk", faza=0.02)
    with _lba(p, "Jezyk"), p.uklad(skala=SKALA_LBA), p.uklad(pos=tuple(-v for v in GLOWA)):
        p.blok("Jezyk", (0, 12.48, 3.6), (0.18, 0.06, 1.3), "jezyk", "polysk", faza=0.0)
        for zn in (1, -1):
            p.blok("Widelec", (zn * 0.1, 12.48, 4.35), (0.08, 0.05, 0.4), "jezyk", "polysk", rot=(0, zn * 20, 0),
                   faza=0.0)


def _platek(p, nazwa, kat, dl=2.6, szer=1.45):
    """Płatek kaptura w płaszczyźnie prostopadłej do Z (przodem do kamery), kat od lewej przez górę do prawej."""
    with p.uklad(pos=KAPTUR, obrot=(0, 0, kat - 90)):
        with p.uklad(pos=(0, 0.75, 0), obrot=(-10, 0, 0)):
            p.blok(nazwa, (0, dl / 2, 0), (szer, dl, 0.2), "platek", "matowy", faza=0.06)
            p.blok(nazwa + " nasada", (0, 0.4, 0.03), (szer * 0.85, 0.8, 0.22), "platek_nasada", "matowy", faza=0.04)
            p.ostroslup(nazwa + " czubek", (0, dl + 0.25, 0), (szer * 0.85, 0.5, 0.2), "platek_ciemny", "matowy",
                        gora=(0.0, 0.2), faza=0.0)
            p.blok(nazwa + " zylka", (0, dl * 0.6, 0.11), (0.12, dl * 0.7, 0.02), "platek_ciemny", "matowy", faza=0.0)


def _kaptur(p):
    grupy = {"KapturL": (-28, 8, 42), "KapturG": (72, 108), "KapturP": (138, 172, 208)}
    for kosc, katy in grupy.items():
        with _model(p, kosc):
            for kat in katy:
                _platek(p, "Platek %d" % (kat % 360), kat)
    with _model(p, "Glowa"):
        p.walec("Srodek kwiatu", (KAPTUR[0], KAPTUR[1], KAPTUR[2] - 0.15), (1.5, 0.3, 1.5), "kwiat_zolty", "matowy",
                rot=(90, 0, 0), segm=12)
        p.walec("Rosa kwiatu", (KAPTUR[0], KAPTUR[1] + 0.35, KAPTUR[2] - 0.32), (0.4, 0.1, 0.4), "rosa", "polysk",
                rot=(90, 0, 0), faza=0.0, segm=8)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _kaptur_poz(roz=0.0):
    """Kaptur: roz > 0 rozkłada płatki szerzej i lekko do przodu (stopnie), < 0 składa do tyłu."""
    return {"KapturL": (-roz * 0.4, -roz * 0.5, -roz), "KapturP": (-roz * 0.4, roz * 0.5, roz), "KapturG": (-roz * 0.7, 0, 0)}


def _szyja_poz(s1, s2, s3, gl=None, ry=(0, 0, 0), rz=(0, 0, 0)):
    """Szyja: kąty rx trzech odcinków (> 0 w przód) i łba; gl = None — łeb wyrównany (poziomo)."""
    gl = -(s1 + s2 + s3) if gl is None else gl
    return {"Szyja1": (s1, ry[0], rz[0]), "Szyja2": (s2, ry[1], rz[1]), "Szyja3": (s3, ry[2], rz[2]), "Glowa": (gl, 0, 0)}


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    ukaszenie(p)
    trafienie(p)
    unik(p)
    upadek(p)
    ryk(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): szyja faluje (fala w górę szyi), łeb zostaje poziomo, język drga dwa razy, kaptur oddycha,
    czubek ogona drga."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        w = 2 * math.pi * t
        jez = max(0.0, math.sin(4 * w)) ** 2 if (t % 0.5) < 0.25 else 0.0
        pz = _szyja_poz(2.5 * math.sin(w), -3 * math.sin(w - 0.8), 2.5 * math.sin(w - 1.6),
                        ry=(3 * math.sin(w + 0.4), 3 * math.sin(w - 0.4), 4 * math.sin(w - 1.2)),
                        rz=(2 * math.sin(w), 2 * math.sin(w - 0.9), 2 * math.sin(w - 1.8)))
        pz.update(_kaptur_poz(3 * math.sin(w + 1.0)))
        pz.update({"Szczeka": (3 * jez, 0, 0), "Jezyk": {"p": (0, 0, 0.9 * jez)},
                   "Ogon": (0, 8 * math.sin(2 * w), 0), "Zwoj": (0, 0.6 * math.sin(w), 0)})
        return pz
    _petla(k, poza)
    return k


def ruch(p, dl=48):
    """Ruch w miejscu (1,6 s): zwój kołysze się na boki, szyja wije się falą z boku na bok, łeb patrzy przed siebie,
    ogon zamiata."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        w = 2 * math.pi * t
        pz = _szyja_poz(3 + 2 * math.sin(2 * w), -2, 2 * math.sin(2 * w - 1.0),
                        ry=(8 * math.sin(w), -10 * math.sin(w - 0.7), 8 * math.sin(w - 1.4)),
                        rz=(6 * math.sin(w), -8 * math.sin(w - 0.7), 6 * math.sin(w - 1.4)))
        pz["Glowa"] = (pz["Glowa"][0], -6 * math.sin(w - 2.0), -4 * math.sin(w - 2.0))
        pz.update(_kaptur_poz(2 * math.sin(2 * w)))
        pz.update({"Zwoj": (0, 5 * math.sin(w), 2 * math.sin(w)), "Ogon": (0, 18 * math.sin(w - 1.0), 0)})
        return pz
    _petla(k, poza)
    return k


def atak(p, dl=36):
    """Ukąszenie (1,2 s): szyja cofa się w literę S, paszcza się otwiera, kaptur rozkłada (kl. 0–12), łeb wystrzela
    w przód i w dół, kły zatrzaskują się (kl. 18 = trafienie), cofnięcie."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_szyja_poz(-8, -16, 22, gl=-8), _kaptur_poz(18), Szczeka=(32, 0, 0), Zwoj=(-2, 0, 0))
    wypad = _z(_szyja_poz(16, 22, 16, gl=-26), _kaptur_poz(10), Szczeka=(40, 0, 0), Zwoj=(3, 0, 0))
    traf = _z(_szyja_poz(18, 26, 18, gl=-34), _kaptur_poz(6), Szczeka=(0, 0, 0), Zwoj=(4, 0, 0))
    cofa = _z(_szyja_poz(4, 6, 4), _kaptur_poz(2), Szczeka=(6, 0, 0))
    _sekwencja(k, (0, 12, 16, 18, 26, 36), (spocz, zamach, wypad, traf, cofa, spocz),
               wyg={0: "s", 1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=54):
    """Plucie jadem (1,8 s): wąż odchyla się i unosi wyżej, kaptur rozkłada się szeroko, paszcza otwiera się
    (kl. 0–22), wyrzut łba w przód — jad leci z paszczy (kl. 28), chwila z otwartą paszczą, powrót."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    unies = _z(_szyja_poz(-6, -10, 6, gl=-4), _kaptur_poz(26), Szczeka=(30, 0, 0), Zwoj=(-2, 0, 0))
    unies2 = _z(_szyja_poz(-7, -12, 4, gl=-2), _kaptur_poz(28), Szczeka=(34, 0, 0), Zwoj=(-2, 0, 0))
    wyrzut = _z(_szyja_poz(8, 14, 10, gl=-30), _kaptur_poz(20), Szczeka=(42, 0, 0), Zwoj=(2, 0, 0))
    trzyma = _z(_szyja_poz(6, 10, 8, gl=-24), _kaptur_poz(16), Szczeka=(30, 0, 0))
    _sekwencja(k, (0, 16, 22, 28, 38, 54), (spocz, unies, unies2, wyrzut, trzyma, spocz),
               wyg={0: "s", 2: "we", 3: "wy"})
    return k


def ukaszenie(p, dl=48):
    """Rozszarpanie (1,6 s): szyja cofa się (kl. 0–10), wypad i ukąszenie (kl. 16 = trafienie), szarpanie łbem na
    boki z zaciśniętymi kłami (kl. 18–34), puszcza i wraca."""
    k = p.klip("ukaszenie", dl, petla=False)
    spocz = {}
    zamach = _z(_szyja_poz(-6, -14, 20, gl=-6), _kaptur_poz(20), Szczeka=(36, 0, 0))
    gryzie = _z(_szyja_poz(18, 24, 16, gl=-32), _kaptur_poz(12), Szczeka=(0, 0, 0), Zwoj=(4, 0, 0))
    lewo = _z(_szyja_poz(18, 24, 16, gl=-30, ry=(6, 8, 14), rz=(0, 0, -10)), _kaptur_poz(16), Zwoj=(4, 6, 0))
    prawo = _z(_szyja_poz(18, 24, 16, gl=-30, ry=(-6, -8, -14), rz=(0, 0, 10)), _kaptur_poz(16), Zwoj=(4, -6, 0))
    puszcza = _z(_szyja_poz(6, 8, 4), _kaptur_poz(4), Szczeka=(18, 0, 0))
    _sekwencja(k, (0, 10, 16, 21, 26, 31, 36, 48), (spocz, zamach, gryzie, lewo, prawo, lewo, puszcza, spocz),
               wyg={1: "we", 2: "wy"})
    return k


def trafienie(p, dl=20):
    """Szarpnięcie w tył (0,67 s, najdalej kl. 4): szyja odgięta w tył, łeb w górę, kaptur się trzęsie."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_szyja_poz(-6, -8, -6, gl=-6), _kaptur_poz(-10), Szczeka=(16, 0, 0), Zwoj=(-2, 0, 0))
    odb = _z(_szyja_poz(2, 3, 2), _kaptur_poz(6), Szczeka=(4, 0, 0))
    _sekwencja(k, (0, 4, 12, 20), (spocz, szarp, odb, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=30):
    """Unik (1,0 s): zwój przesuwa się o 0,6 studa w lewo, a szyja odchyla łeb dalej w lewo (razem ok. 1,5 studa,
    najdalej kl. 14) i wraca."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    zbiera = _z(_szyja_poz(0, 0, 0, rz=(-4, -4, -2)), Zwoj={"o": (0, 0, -2), "p": (-0.1, 0, 0)})
    odskok = _z(_szyja_poz(-2, 0, 0, rz=(-6, -6, -4)), _kaptur_poz(-6), Zwoj={"o": (0, -6, 3), "p": (0.6, 0, 0)})
    stoi = _z(_szyja_poz(-2, 0, 0, ry=(0, 0, -10), rz=(-5, -5, -3)), Zwoj={"o": (0, -8, 2), "p": (0.6, 0, 0)})
    wraca = _z(_szyja_poz(0, 0, 0, rz=(3, 3, 2)), Zwoj={"o": (0, -2, -1), "p": (0.25, 0, 0)})
    _sekwencja(k, (0, 5, 10, 14, 21, 30), (spocz, zbiera, odskok, stoi, wraca, spocz), wyg={1: "we", 2: "wy"})
    return k


def upadek(p, dl=66):
    """Upadek (2,2 s): szyja chwieje się na boki, potem łeb pada w przód i na bok aż na ziemię, kaptur opada,
    zwój osiada (kl. 66 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_szyja_poz(-6, -6, -4, rz=(5, 6, 6)), _kaptur_poz(-8), Szczeka=(14, 0, 0))
    chwiej2 = _z(_szyja_poz(4, 6, 6, rz=(-6, -8, -6)), _kaptur_poz(-6), Szczeka=(8, 0, 0))
    pada = _z(_szyja_poz(24, 26, 20, gl=-10, rz=(8, 10, 6)), _kaptur_poz(-16), Szczeka=(20, 0, 0))
    lezy = _z(_szyja_poz(40, 38, 20, gl=-8, rz=(10, 12, 8)), _kaptur_poz(-26), Szczeka=(24, 0, 0),
              Jezyk={"p": (0, 0, 0.6)}, Zwoj=(0, 0, 2))
    osiada = _z(lezy, _h=-0.25)
    _sekwencja(k, (0, 10, 22, 38, 48, 66), (spocz, chwiej, chwiej2, pada, lezy, osiada),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def ryk(p, dl=60):
    """Ryk (dokładnie 60 klatek = 2,0 s, pętla — gra go przelot kamery): szyja prostuje się i odchyla, kaptur
    rozłożony najszerzej, paszcza otwarta, łeb i płatki drżą."""
    k = p.klip("ryk", dl, petla=True)

    def poza(t):
        s = min(1.0, max(0.0, (t - 0.08) / 0.22)) * min(1.0, max(0.0, (0.95 - t) / 0.2))
        s = s * s * (3 - 2 * s)
        drz = math.sin(14 * math.pi * t) * s
        pz = _szyja_poz(-5 * s, -8 * s, -4 * s + 1.5 * drz, gl=-6 * s + 2 * drz,
                        rz=(0, 0, 1.5 * drz))
        pz.update(_kaptur_poz(30 * s + 3 * drz))
        pz.update({"Szczeka": (40 * s, 0, 0), "Jezyk": {"p": (0, 0, 0.5 * s)}, "Zwoj": (-1.5 * s, 0, 0),
                   "Ogon": (0, 20 * drz, 0)})
        return pz
    _petla(k, poza)
    return k


# =============================================================== animacja: pozy kluczowe -> klucz w każdej klatce
# (ten sam zestaw pomocników co w modułach potworów Bagna — rechotek, bulgotnik, klodoklap, ropucha_z_chatka,
#  straznik_topieli — i Dżungli: zwijogon, gebokwiat, kokosowy_silacz, pancernik_ruin, waz_stu_lian). Poza = {kość: (rx, ry, rz) | {"o": obrót, "p": przesunięcie, "k": kierunek osi OS[kość] w
#  świecie}}; "_h" = wysokość najniższego punktu ciała nad ziemią (domyślnie 0), "_wolne" = kości PLASKIE nie są
#  trzymane poziomo (lot, przewrót); w Dżungli "_wolne" może też być krotką nazw kości — wtedy tylko one idą za
#  rodzicem (np. łapa uniesiona do ciosu), a reszta zostaje płasko. Brak kości w pozie = spoczynek tej kości.
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
ZERO = (0.0, 0.0, 0.0)


def _T(R):
    return tuple(tuple(R[j][i] for j in range(3)) for i in range(3))


def _norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / n for x in v)


def _obrot_miedzy(a, b):
    """Macierz najkrótszego obrotu, który przenosi kierunek a na kierunek b."""
    a, b = _norm(a), _norm(b)
    o = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    s, c = math.sqrt(sum(x * x for x in o)), sum(a[i] * b[i] for i in range(3))
    if s < 1e-9:
        return I3
    x, y, z = (v / s for v in o)
    t = 1.0 - c
    return ((t * x * x + c, t * x * y - s * z, t * x * z + s * y),
            (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
            (t * x * z - s * y, t * y * z + s * x, t * z * z + c))


def _belka(p, nazwa, a, b, szer, gleb, kolor, mat="zwykly", nad=0.0, faza=None, ksztalt="blok"):
    """Klocek (albo elipsoida: ksztalt="kula", walec: "walec") od punktu a do punktu b (bieżący układ; oś Y bryły
    wzdłuż a→b, nad = wydłużenie z obu końców). Zwraca (środek, obrót) — układ do dokładania brył wzdłuż belki."""
    d = tuple(b[i] - a[i] for i in range(3))
    L = math.sqrt(sum(x * x for x in d))
    sr = tuple((a[i] + b[i]) / 2.0 for i in range(3))
    rot = katy_z_macierzy(_obrot_miedzy((0.0, 1.0, 0.0), d))
    if ksztalt == "kula":
        p.kula(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot)
    elif ksztalt == "walec":
        p.walec(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    else:
        p.blok(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    return sr, rot


def _krok(p, W, n, o, pr):
    k = p.kosci[n]
    Rl = macierz_obrotu(*o)
    if k["rodzic"] is None:
        W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
    else:
        Rp, tp = W[k["rodzic"]]
        st = p.kosci[k["rodzic"]]["staw"]
        d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
        W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))


def _fk(p, lok):
    W = {}
    for n in p.kosci:
        o, pr = lok.get(n, (ZERO, ZERO))
        _krok(p, W, n, o, pr)
    return W


def _naroza(p):
    """Narożniki brył względem stawu ich kości (do dociągania do ziemi), liczone raz."""
    if getattr(p, "_bagno_naroza", None) is None:
        out = {}
        for c in p.czesci:
            R = macierz_obrotu(*c["r"])
            h = [v / 2.0 for v in c["s"]]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        q = razy_wektor(R, (sx * h[0], sy * h[1], sz * h[2]))
                        out.setdefault(c["kosc"], []).append(tuple(c["p"][i] + q[i] for i in range(3)))
        p._bagno_naroza = out
    return p._bagno_naroza


def _najnizej(p, W, pomin=()):
    mn = 1e9
    for kosc, pkt in _naroza(p).items():
        if kosc in pomin:
            continue
        R, t = W[kosc]
        for q in pkt:
            y = R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1]
            if y < mn:
                mn = y
    return mn


def _rozwiaz(p, poza):
    """Poza kluczowa -> {kość: (obrót lokalny, przesunięcie)}; kierunki "k" zamienione na obroty lokalne."""
    lok, W = {}, {}
    for n, k in p.kosci.items():
        v = poza.get(n)
        o, pr, kier = ZERO, ZERO, None
        if isinstance(v, dict):
            o, pr, kier = tuple(v.get("o", ZERO)), tuple(v.get("p", ZERO)), v.get("k")
        elif v is not None:
            o = tuple(v)
        if kier is not None:
            Rp = W[k["rodzic"]][0] if k["rodzic"] else I3
            o = katy_z_macierzy(mnoz(_T(Rp), _obrot_miedzy(OS[n], kier)))
        lok[n] = (tuple(o), tuple(pr))
        _krok(p, W, n, lok[n][0], lok[n][1])
    return lok


def _plasko(p, lok, wolne=()):
    """Kości PLASKIE (bez `wolne`): poziomo w świecie, z odchyleniem (yaw) rodzica."""
    W = {}
    for n, k in p.kosci.items():
        o, pr = lok.get(n, (ZERO, ZERO))
        if n in PLASKIE and n not in wolne:
            Rp = W[k["rodzic"]][0]
            f = razy_wektor(Rp, (0.0, 0.0, 1.0))
            yaw = math.degrees(math.atan2(f[0], f[2])) if abs(f[0]) + abs(f[2]) > 1e-6 else 0.0
            o = katy_z_macierzy(mnoz(_T(Rp), macierz_obrotu(0.0, yaw, 0.0)))
            lok[n] = (o, pr)
        _krok(p, W, n, o, pr)
    return W


def _wolne(*pozy):
    """(płasko?, wolne kości) z pól "_wolne" póz: True = żadna kość PLASKIE nie jest trzymana poziomo."""
    wolne = set()
    for pz in pozy:
        w = pz.get("_wolne")
        if w is True:
            return False, ()
        if w:
            wolne.update(w)
    return True, tuple(wolne)


def _uziem(p, lok, h, plasko=True, wolne=()):
    W = _plasko(p, lok, wolne) if plasko else _fk(p, lok)
    dno = _najnizej(p, W, POMIN_ZIEMIA)
    o, pr = lok[GLOWNA]
    lok[GLOWNA] = (o, (pr[0], pr[1] + h - dno, pr[2]))


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku przez ±180°)."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        d = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or d < najl[0] - 1e-6:
            najl = (d, c)
    return najl[1]


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


def _kw(R):
    """Macierz obrotu -> kwaternion (w, x, y, z)."""
    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = (0.25 * s, (R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s)
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        q = ((R[2][1] - R[1][2]) / s, 0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s)
    elif R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        q = ((R[0][2] - R[2][0]) / s, (R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s)
    else:
        s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        q = ((R[1][0] - R[0][1]) / s, (R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s)
    return _norm(q)


def _z_kw(q):
    w, x, y, z = _norm(q)
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def _bliski(q, wzor):
    return q if sum(q[i] * wzor[i] for i in range(4)) >= 0 else tuple(-v for v in q)


def _slerp(a, b, t):
    b = _bliski(b, a)
    c = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(4))))
    kat = math.acos(c)
    if kat < 1e-5:
        return _norm(tuple(a[i] + (b[i] - a[i]) * t for i in range(4)))
    sa, sb = math.sin((1 - t) * kat) / math.sin(kat), math.sin(t * kat) / math.sin(kat)
    return tuple(sa * a[i] + sb * b[i] for i in range(4))


def _wygladz(t, tryb):
    if tryb == "l":
        return t
    if tryb == "we":
        return t * t
    if tryb == "wy":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t * t * (3.0 - 2.0 * t)


def _zapisz(k, f, lok):
    for n, (o, pr) in lok.items():
        if n == "Root":
            continue
        k.klucz(f, n, obrot=tuple(round(x, 3) for x in o), przes=tuple(round(x, 4) for x in pr), wyg="liniowo")


def _ciagle_katy(lok, poprz):
    """Kąty każdej kości zapisane najbliżej poprzedniej klatki (Euler bez skoków)."""
    for n, (o, pr) in lok.items():
        o = _ciaglosc(o, poprz.get(n))
        poprz[n] = o
        lok[n] = (o, pr)


def _sekwencja(k, czasy, pozy, wyg=None, domyslnie="s", ziemia=True, po=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (obroty kości przez kwaterniony, więc duże obroty łap nie
    kręcą się po kątach). wyg = {numer odcinka: "s" | "l" | "we" | "wy" | "cr"}: s = łagodnie, l = jednostajnie,
    we = przyspiesza (w uderzenie), wy = hamuje (po wybiciu), cr = płynnie przez pozy. ziemia = najniższy punkt
    brył (bez POMIN_ZIEMIA) na wysokości "_h" pozy. po(f, lok) — dopiski w klatce. Klip zapętlony: ostatnia klatka
    = pierwsza."""
    p = k.postac
    n_poz = len(pozy)
    kosci = [n for n in p.kosci if n != "Root"]
    tab = []
    for pz in pozy:
        lok = _rozwiaz(p, pz)
        tab.append({n: (_kw(macierz_obrotu(*lok[n][0])), lok[n][1]) for n in kosci})
    for i in range(1, n_poz):
        for n in kosci:
            tab[i][n] = (_bliski(tab[i][n][0], tab[i - 1][n][0]), tab[i][n][1])

    def sasiad(i):
        if k.petla:
            if i < 0:
                return i + n_poz - 1
            if i > n_poz - 1:
                return i - n_poz + 1
            return i
        return max(0, min(n_poz - 1, i))

    poprz, pierwsza = {}, None
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        if k.petla and f == k.dlugosc and pierwsza is not None:
            _zapisz(k, f, pierwsza)
            continue
        i = max(j for j in range(n_poz - 1) if czasy[j] <= f) if f < czasy[-1] else n_poz - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        tryb = (wyg or {}).get(i, domyslnie)
        e = _wygladz(t, tryb)
        lok = {}
        for n in kosci:
            if tryb == "cr":
                ia, id_ = sasiad(i - 1), sasiad(i + 2)
                qb = tab[i][n][0]
                qa, qc, qd = (_bliski(tab[ia][n][0], qb), _bliski(tab[i + 1][n][0], qb),
                              _bliski(tab[id_][n][0], qb))
                q = _norm(tuple(_cr(qa[j], qb[j], qc[j], qd[j], t) for j in range(4)))
                pa, pb, pc, pd = (tab[ia][n][1], tab[i][n][1], tab[i + 1][n][1], tab[id_][n][1])
                pr = tuple(_cr(pa[j], pb[j], pc[j], pd[j], t) for j in range(3))
            else:
                q = _slerp(tab[i][n][0], tab[i + 1][n][0], e)
                a, b = tab[i][n][1], tab[i + 1][n][1]
                pr = tuple(a[j] + (b[j] - a[j]) * e for j in range(3))
            lok[n] = (katy_z_macierzy(_z_kw(q)), pr)
        h0, h1 = pozy[i].get("_h", 0.0), pozy[i + 1].get("_h", 0.0)
        plasko, wolne = _wolne(pozy[i], pozy[i + 1])
        if ziemia:
            _uziem(p, lok, h0 + (h1 - h0) * e, plasko, wolne)
        elif plasko:
            _plasko(p, lok, wolne)
        if po:
            po(f, lok)
        _ciagle_katy(lok, poprz)
        if pierwsza is None:
            pierwsza = dict(lok)
        _zapisz(k, f, lok)
    return k


def _petla(k, poza, ziemia=True):
    """Klip zapętlony z funkcji poza(t), t = 0…1 (okresowa); ostatnia klatka = pierwsza (bez szwu)."""
    p = k.postac
    pierwsza, poprz = None, {}
    for f in range(k.dlugosc):
        pz = poza(f / float(k.dlugosc))
        lok = _rozwiaz(p, pz)
        if ziemia:
            plasko, wolne = _wolne(pz)
            _uziem(p, lok, pz.get("_h", 0.0), plasko, wolne)
        _ciagle_katy(lok, poprz)
        _zapisz(k, f, lok)
        if pierwsza is None:
            pierwsza = dict(lok)
    _zapisz(k, k.dlugosc, pierwsza)
    return k
