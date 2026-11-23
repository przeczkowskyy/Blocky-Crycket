# -*- coding: utf-8 -*-
"""Klipy smoka ewolucji — te same nazwy i stawy we wszystkich stadiach, liczby z danych stadium.

    from swiat.ewolucja.modele.smok_klipy import dodaj_klipy
    dodaj_klipy(p)            # p = zbuduj_stadium(nr); klipy trafiają do p.klipy, zdarzenia do klip.zdarzenia

„waga” stadium (0 pisklę … 1 prastary) steruje długością i charakterem: pisklę człapie i podskakuje, dorosły kroczy,
prastary jest ciężki. Klipy są „w miejscu” (grę przesuwa kod gry); kość Tulow niesie podskok, przysiad, obrót ciała.
Obroty to odchylenia od pozy spoczynkowej wokół osi modelu w stawie (konwencja biblioteki): rx < 0 unosi przód kości
(głowa w górę, noga do przodu), szczęka rx > 0 = otwarta, ogon rx > 0 = koniec w górę, lewe skrzydło rz > 0 = w górę.
Zdarzenia (klatka przy 30 kl./s) — ZDARZENIA_OPIS.
"""
import math

from swiat.postacie.biblioteka.postac import macierz_obrotu

NOGI = ("NogaPL", "NogaPP", "NogaTL", "NogaTP")
GRUPY = {"Skrz1": ("SkrzydloL1", "SkrzydloP1"), "Skrz2": ("SkrzydloL2", "SkrzydloP2"),
         "NogiP1": ("NogaPL1", "NogaPP1"), "NogiP2": ("NogaPL2", "NogaPP2"),
         "NogiT1": ("NogaTL1", "NogaTP1"), "NogiT2": ("NogaTL2", "NogaTP2")}
OGON = ("Ogon1", "Ogon2", "Ogon3", "Ogon4")
KLIPY_PODSTAWOWE = ("spoczynek", "chod", "bieg", "gryz1", "gryz2", "gryz3", "ogien_start", "ogien_petla",
                    "ogien_koniec", "trafienie", "wyklucie")
KLIPY_DODATKOWE = ("splun", "ogon_zamach", "ryk", "szybowanie_start", "szybowanie_petla", "szybowanie_ladowanie",
                   "nurkowanie_skok", "nurkowanie_ladowanie", "koziolek", "koziolek_dlugi", "pozarcie", "radosc", "cokol", "portret")
ZDARZENIA_OPIS = {
    "ugryzienie": "szczęki się zatrzaskują — policz trafienie",
    "ogien_start": "pysk otwarty i wycelowany — włącz strumień ognia",
    "ogien_stop": "pysk się zamyka — wyłącz strumień ognia",
    "strzal": "wypuść kulę ognia z PyskAttachment",
    "uderzenie_start": "ogon zaczyna zamiatać — okno trafienia otwarte",
    "uderzenie_stop": "koniec okna trafienia ogonem",
    "ryk_start": "paszcza otwarta — fala ryku, dźwięk",
    "ryk_stop": "koniec ryku",
    "odbicie": "łapy odrywają się od ziemi",
    "ladowanie": "łapy dotykają ziemi — kurz, dźwięk",
    "szczyt": "najwyższy punkt skoku",
    "uderzenie": "ciało uderza w ziemię — fala, wstrząs kamery",
    "upadek": "ciało pada na ziemię po koziołku",
    "polkniecie": "przełknięcie — dolicz zjedzone",
    "pekniecie": "skorupa pęka — odłamki, błysk",
}


def _lustro(v):
    return (v[0], -v[1], -v[2])


def _rozwin(d):
    """{kość | grupa: (rx, ry, rz) | {"obrot": …, "przes": …}} -> {kość: {"obrot": …, "przes": …}} (prawa strona lustrzanie)."""
    wyn = {}
    for klucz, w in d.items():
        w = dict(w) if isinstance(w, dict) else {"obrot": tuple(w)}
        if klucz == "Ogon":
            for n in OGON:
                wyn[n] = dict(w)
        elif klucz in GRUPY:
            lewa, prawa = GRUPY[klucz]
            wyn[lewa] = dict(w)
            wyn[prawa] = {k: (_lustro(v) if k == "obrot" else (-v[0], v[1], v[2])) for k, v in w.items()}
        else:
            wyn[klucz] = w
    return wyn


def sekwencja(p, nazwa, n, klatki, zdarzenia=None):
    """Klip jednorazowy z póz: klatki = [(t 0…1, poza, [wygładzanie]), …]. Kanały użyte gdziekolwiek dostają klucz
    zerowy na początku i na końcu, chyba że poza w t = 0 / t = 1 mówi inaczej (klipy łączone w łańcuch)."""
    k = p.klip(nazwa, int(n), petla=False)
    rozw = [(float(x[0]), _rozwin(x[1]), x[2] if len(x) > 2 else "gladko") for x in klatki]
    uzyte = {(b, ch) for _, d, _ in rozw for b, v in d.items() for ch in v}
    for t in (0.0, 1.0):
        if not any(abs(x[0] - t) < 1e-9 for x in rozw):
            rozw.append((t, {}, "gladko"))
    for t, d, wyg in rozw:
        if t in (0.0, 1.0):
            for b, ch in uzyte:
                d.setdefault(b, {}).setdefault(ch, (0.0, 0.0, 0.0))
        for b, v in d.items():
            k.klucz(round(t * n), b, wyg=wyg, **v)
    k.zdarzenia = {z: int(round(t * n)) for z, t in (zdarzenia or {}).items()}
    return k


def petla(p, nazwa, n, poza, cykle, zdarzenia=None):
    """Klip zapętlony wokół pozy: cykle = [(kość | grupa, kanał, amplituda, częstość, faza), …] (sumują się)."""
    k = p.klip(nazwa, int(n), petla=True)
    for b, v in _rozwin(poza).items():
        for ch, w in v.items():
            k.cykl(b, ch, (0, 0, 0), srodek=w)
    for kosc, kanal, amp, czest, faza in cykle:
        for b, v in _rozwin({kosc: {kanal: tuple(amp)}}).items():
            k.cykl(b, kanal, v[kanal], faza=faza, czestosc=czest)
    k.zdarzenia = dict(zdarzenia or {})
    return k


def _klipy_surowe(p, dodatkowe=True):
    P = p.dane_stadium
    w = P["waga"]
    b = 1.0 - w
    W, H, L = P["T"]
    nog = P["nog"]
    a1, a2 = P["szyja"][2], P["szyja"][3]
    pit, swp, dih, fold = P["skrz_spocz"]

    def F(maly, duzy):                                         # długość klipu: parzysta liczba klatek
        return max(4, int(round((maly + (duzy - maly) * w) / 2.0)) * 2)

    def S(otw, m1=0.0, m2=None):
        """Skrzydła: otw 0 (spoczynek) … 1 (rozłożone), m1 / m2 = uniesienie ramienia / dłoni w stopniach."""
        return {"Skrz1": (0, -swp * 0.8 * otw, -(dih - 12) * otw + m1),
                "Skrz2": (0, -fold * otw, m1 * 0.6 if m2 is None else m2)}

    def T(x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0):
        return {"Tulow": {"przes": (x, y, z), "obrot": (rx, ry, rz)}}

    def zl(*slowniki):
        wyn = {}
        for s in slowniki:
            wyn.update(s)
        return wyn

    # ------------------------------------------------------------------ spoczynek
    petla(p, "spoczynek", F(60, 110), {}, [
        ("Tulow", "przes", (0, 0.025 + 0.01 * w, 0), 1, 0.0), ("Tulow", "obrot", (1.2, 0, 0), 1, 0.25),
        ("Szyja1", "obrot", (2 + 2 * b, 0, 0), 1, 0.1), ("Szyja2", "obrot", (1.5, 3 + 6 * b, 0), 1, 0.3),
        ("Glowa", "obrot", (-(1.5 + 2 * b), 3 + 6 * b, 1.5 + 6 * b), 1, 0.36),
        ("Skrz1", "obrot", (0, 0, 2 + 4 * b), 2 if b > 0.6 else 1, 0.0), ("Skrz2", "obrot", (0, 0, 3 + 3 * b), 2 if b > 0.6 else 1, -0.1),
        ("Ogon1", "obrot", (1.5, 5 + 4 * b, 0), 1, 0.0), ("Ogon2", "obrot", (1.5, 7 + 5 * b, 0), 1, -0.12),
        ("Ogon3", "obrot", (2, 9 + 6 * b, 0), 1, -0.24), ("Ogon4", "obrot", (3, 11 + 7 * b, 0), 1, -0.36)])

    if P["oczy"][0] == "dziecko":                              # mrugnięcie: powieki wysuwają się na przód i górę oczu
        ks = p.klipy[-1]
        for f0 in (round(ks.dlugosc * 0.3), round(ks.dlugosc * 0.78)):
            for df, v in ((-3, 0.0), (0, 0.2), (2, 0.2), (5, 0.0)):
                ks.klucz(f0 + df, "Powieki", przes=(0, v, v), wyg="liniowo")
        ks.klucz(0, "Powieki", przes=(0, 0, 0), wyg="liniowo")
        ks.klucz(ks.dlugosc, "Powieki", przes=(0, 0, 0), wyg="liniowo")

    # ------------------------------------------------------------------ chód i bieg
    def nogi(k, fazy, A, B):
        n = k.dlugosc
        for noga, fz in zip(NOGI, fazy):
            k.cykl(noga + "1", "obrot", (A, 0, 0), faza=fz, probki=12)
            for i in range(13):                                 # „kolano” ugina się, gdy noga wraca do przodu
                t = i / 12.0
                k.klucz(n * t, noga + "2", obrot=(max(0.0, -math.cos(2 * math.pi * (t + fz))) * B, 0, 0))

    # Gra porusza każde stadium z tą samą prędkością (16–26 studs/s), więc klipy są pisane pod prędkość po ziemi:
    # chód 7 studs/s, bieg 18 studs/s. Maluchy drepczą i kicają długimi susami, średnie galopują, wielkie stawiają
    # długie kroki. Liczby: (klatki cyklu, klatki podporu jednej stopy) — parzyste, bo dane gry mają próbkę co 2 klatki.
    N = P["nr"]
    D0 = p.geometria["NogaPL1"][1] - p.geometria["NogaPL3"][1]
    ogon = [("Ogon1", "obrot", (2, 7 + 3 * b, 0), 1, 0.5), ("Ogon2", "obrot", (2, 9 + 4 * b, 0), 1, 0.38),
            ("Ogon3", "obrot", (3, 11 + 5 * b, 0), 1, 0.26), ("Ogon4", "obrot", (3, 13 + 6 * b, 0), 1, 0.14)]
    n_, s_ = ((8, 4), (8, 4), (12, 6), (12, 6), (16, 8), (18, 10), (22, 12), (30, 16))[N - 1]
    k = petla(p, "chod", n_, {}, [
        ("Tulow", "obrot", (0, 2 + 5 * b, 1.5 + 6 * b), 1, 0.0),
        ("Szyja1", "obrot", (3, 0, 0), 2, 0.15), ("Glowa", "obrot", (2, 0, 0), 2, 0.3),
        ("Glowa", "obrot", (0, -(1.5 + 4 * b), -(1 + 5 * b)), 1, 0.0),
        ("Skrz1", "obrot", (0, 0, 3 + 3 * b), 2, 0.3), ("Skrz2", "obrot", (0, 0, 4 + 2 * b), 2, 0.2)] + ogon)
    k.chod = {"v": 7.0, "podpor": s_, "start": (0, n_ // 2, n_ // 2, 0), "kappa": 0.0, "unies": 0.24 - 0.06 * w,
              "podskok": (0.02 + 0.03 * b, 2, s_ / 2.0 / n_), "pochyl": (0.0, 0.0)}             # kłus po przekątnej

    n_, s_, kappa = ((10, 2, 0.6), (10, 2, 0.5), (12, 2, 0.15), (12, 2, 0.0), (16, 4, 0.0), (16, 4, 0.0), (20, 6, 0.0),
                     (24, 8, 0.0))[N - 1]
    k = petla(p, "bieg", n_, zl(T(rx=5 + 3 * w), S(0.3, 6), {"Szyja1": (10 + 6 * w, 0, 0), "Glowa": (-10 - 5 * w, 0, 0),
                                                              "Ogon": (4, 0, 0)}), [
        ("Szyja1", "obrot", (4, 0, 0), 1, 0.55), ("Glowa", "obrot", (4 + 3 * b, 0, 0), 1, 0.0),
        ("Skrz1", "obrot", (0, 0, 9), 1, 0.2), ("Skrz2", "obrot", (0, 0, 8), 1, 0.1),
        ("Ogon1", "obrot", (5, 0, 0), 1, 0.6), ("Ogon2", "obrot", (6, 0, 0), 1, 0.48),
        ("Ogon3", "obrot", (7, 0, 0), 1, 0.36), ("Ogon4", "obrot", (8, 0, 0), 1, 0.24)])
    if N <= 2:                                                  # kicanie: przednie razem, tylne tuż po nich, potem długi sus
        k.chod = {"v": 18.0, "podpor": s_, "start": (0, 0, s_, s_), "kappa": kappa, "unies": 0.5,
                  "podskok": (0.34 * D0, 1, s_ / float(n_)), "pochyl": (9.0, 1.0 / n_)}
    else:                                                       # galop: przednie jedna po drugiej, potem tylne
        k.chod = {"v": 18.0, "podpor": s_, "start": (0, 2, n_ // 2, n_ // 2 + 2), "kappa": kappa, "unies": 0.42 - 0.1 * w,
                  "podskok": (0.07 * D0 * (1 + b), 2, (1 + s_ / 2.0) / n_), "pochyl": (3.0, (1 + s_ / 2.0) / n_)}

    # ------------------------------------------------------------------ gryzienie
    def kasniecie(nazwa, zn, n, moc=1.0):
        sekwencja(p, nazwa, n, [
            (0.32, zl(T(z=-0.03 * L, rx=-2), {"Szyja1": (-9 * moc, 0, 0), "Glowa": (-4, zn * 6, zn * 8),
                                              "Szczeka": (30 + 8 * b, 0, 0)}), "liniowo"),
            (0.5, zl(T(z=0.09 * L, rx=3), {"Szyja1": (15 * moc, 0, 0), "Szyja2": (8 * moc, 0, 0),
                                           "Glowa": (-12 * moc, -zn * 9, -zn * 10), "Szczeka": (0, 0, 0), "Ogon": (4, 0, 0)})),
            (0.68, zl(T(z=0.04 * L), {"Szyja1": (8, 0, 0), "Glowa": (-4, -zn * 3, -zn * 4), "Szczeka": (5, 0, 0)}))],
            {"ugryzienie": 0.5})

    kasniecie("gryz1", 1, F(10, 16))
    kasniecie("gryz2", -1, F(10, 16), 1.15)
    sekwencja(p, "gryz3", F(22, 34), [
        (0.3, zl(T(y=-0.1 * nog, z=-0.18 * L, rx=-6), S(0.3, 12), {
            "Szyja1": (-18, 0, 0), "Szyja2": (-8, 0, 0), "Szczeka": (22, 0, 0), "Ogon": (9, 0, 0),
            "NogiP1": (10, 0, 0), "NogiP2": (16, 0, 0), "NogiT1": (-12, 0, 0), "NogiT2": (22, 0, 0)})),
        (0.5, zl(T(y=0.05, z=0.42 * L, rx=10), S(0.45, -8), {
            "Szyja1": (24, 0, 0), "Szyja2": (12, 0, 0), "Glowa": (-24, 0, 0), "Szczeka": (54, 0, 0), "Ogon": (-5, 0, 0),
            "NogiP1": (-24, 0, 0), "NogiP2": (4, 0, 0), "NogiT1": (22, 0, 0), "NogiT2": (6, 0, 0)}), "liniowo"),
        (0.56, zl(T(y=0.0, z=0.44 * L, rx=11), {"Szyja1": (26, 0, 0), "Glowa": (-20, 0, 0), "Szczeka": (0, 0, 0)})),
        (0.68, zl(T(z=0.3 * L, rx=6), S(0.2, 4), {"Glowa": (-14, 14, 0), "Szyja1": (16, 0, 0), "Szczeka": (3, 0, 0)})),
        (0.8, zl(T(z=0.14 * L, rx=2), {"Glowa": (-8, -12, 0), "Szyja1": (8, 0, 0)}))],
        {"ugryzienie": 0.56})

    # ------------------------------------------------------------------ zionięcie (start / pętla / koniec)
    A = zl(T(z=0.06 * L, rx=5), S(0.45, 8), {
        "Szyja1": (a1 * 0.42, 0, 0), "Szyja2": (a2 * 0.3, 0, 0), "Glowa": (-(a1 * 0.42 + a2 * 0.3) + 2, 0, 0),
        "Szczeka": (36, 0, 0), "Ogon": (5, 0, 0), "NogiP1": (-10, 0, 0), "NogiP2": (5, 0, 0)})
    n = F(16, 30)
    sekwencja(p, "ogien_start", n, [
        (0.5, zl(T(z=-0.1 * L, rx=-8), S(0.25, 14), {"Szyja1": (-18, 0, 0), "Szyja2": (-9, 0, 0), "Glowa": (-6, 0, 0),
                                                     "Szczeka": (8, 0, 0), "Ogon": (8, 0, 0)})),
        (1.0, A)], {"ogien_start": (n - 2.0) / n})
    petla(p, "ogien_petla", F(20, 24), A, [
        ("Glowa", "obrot", (1.5, 3.5, 0), 2, 0.0), ("Szczeka", "obrot", (3, 0, 0), 4, 0.1),
        ("Tulow", "przes", (0, 0, 0.012 * L), 2, 0.2), ("Skrz1", "obrot", (0, 0, 3), 2, 0.0), ("Skrz2", "obrot", (0, 0, 3), 2, 0.2),
        ("Ogon3", "obrot", (0, 5, 0), 1, 0.0), ("Ogon4", "obrot", (0, 8, 0), 1, -0.2)])
    sekwencja(p, "ogien_koniec", F(12, 22), [
        (0.0, A, "liniowo"),
        (0.3, zl(T(z=0.02 * L, rx=1), S(0.25, 2), {"Szyja1": (a1 * 0.2, 0, 0), "Glowa": (-8, 0, 0), "Szczeka": (4, 0, 0)})),
        (0.6, zl(T(rx=-2), {"Szyja1": (-4, 0, 0), "Szczeka": (0, 0, 0)}))], {"ogien_stop": 2.0 / F(12, 22)})

    # ------------------------------------------------------------------ trafienie (wzdrygnięcie)
    sekwencja(p, "trafienie", F(10, 16), [
        (0.25, zl(T(y=0.05 * b, z=-0.14 * L, rx=-7, rz=5), S(0.3, 16), {
            "Szyja1": (-14, 0, 0), "Glowa": (10, 12, 0), "Szczeka": (16, 0, 0), "Ogon": (10, 0, 0),
            "NogiP1": (12, 0, 0), "NogiT1": (10, 0, 0)}), "gladko"),
        (0.6, zl(T(z=0.03 * L, rx=2, rz=-2), S(0.1, -4), {"Szyja1": (4, 0, 0), "Glowa": (-2, -4, 0)}))])

    # ------------------------------------------------------------------ wyklucie (smok; jajo ma własny klip)
    zwin = zl(T(y=-0.7 * nog, z=-0.75, rx=8), {
        "Szyja1": (34, 0, 0), "Szyja2": (22, 0, 0), "Glowa": (26, 0, 0), "Skrz1": (0, 0, -dih * 0.7), "Skrz2": (0, 14, 0),
        "Ogon": (0, 34, 0), "NogiP1": (-34, 0, 0), "NogiP2": (62, 0, 0), "NogiT1": (-38, 0, 0), "NogiT2": (70, 0, 0)})
    sekwencja(p, "wyklucie", F(66, 90), [
        (0.0, zwin),
        (0.14, zl(zwin, T(y=-0.7 * nog, z=-0.75, rx=8, rz=6))), (0.27, zl(zwin, T(y=-0.7 * nog, z=-0.75, rx=8, rz=-7))),
        (0.38, zl(zwin, T(y=-0.62 * nog, z=-0.7, rx=6, rz=4)), "liniowo"),
        (0.46, zl(T(y=-0.35 * nog, z=-0.45, rx=2), {"Szyja1": (10, 0, 0), "Szyja2": (6, 0, 0), "Glowa": (-10, 0, 0),
                                            "Skrz1": (0, 0, -dih * 0.3), "Ogon": (4, 20, 0), "NogiP1": (-16, 0, 0),
                                            "NogiP2": (30, 0, 0), "NogiT1": (-18, 0, 0), "NogiT2": (34, 0, 0)})),
        (0.56, zl(T(y=0.3 + 0.2 * b, rx=-9), S(0.95, 24), {"Szyja1": (-12, 0, 0), "Szyja2": (-6, 0, 0), "Glowa": (-14, 0, 0),
                                                           "Szczeka": (34, 0, 0), "Ogon": (14, 0, 0),
                                                           "NogiP1": (-12, 0, 0), "NogiT1": (14, 0, 0)})),
        (0.68, zl(T(y=-0.07, rx=3), S(0.5, -12), {"Glowa": (4, 0, 0), "Szczeka": (6, 0, 0), "NogiP2": (10, 0, 0),
                                                  "NogiT2": (10, 0, 0)})),
        (0.79, zl(T(rz=8, ry=5), S(0.2, 8), {"Glowa": (-4, 14, 10), "Ogon": (6, -14, 0)})),
        (0.88, zl(T(rz=-7, ry=-5), S(0.1, 2), {"Glowa": (-2, -12, -9), "Ogon": (4, 12, 0)}))],
        {"pekniecie": 0.46})
    if not dodatkowe:
        return p

    # ------------------------------------------------------------------ splunięcie ogniem
    sekwencja(p, "splun", F(14, 22), [
        (0.32, zl(T(z=-0.05 * L, rx=-4), {"Szyja1": (-15, 0, 0), "Szyja2": (-7, 0, 0), "Glowa": (-6, 0, 0),
                                           "Szczeka": (10, 0, 0), "Skrz1": (0, 0, 8)}), "liniowo"),
        (0.5, zl(T(z=0.07 * L, rx=4), {"Szyja1": (15, 0, 0), "Szyja2": (7, 0, 0), "Glowa": (-16, 0, 0),
                                        "Szczeka": (42, 0, 0), "Ogon": (6, 0, 0)})),
        (0.66, zl(T(z=-0.04 * L, rx=-2), {"Szyja1": (6, 0, 0), "Glowa": (-10, 0, 0), "Szczeka": (22, 0, 0)}))],
        {"strzal": 0.5})

    # ------------------------------------------------------------------ zamach ogonem (obrót o 360°)
    def obr(kat, y=0.0, rz=0.0, rx=0.0):
        return T(y=y, rx=rx, ry=kat, rz=rz)

    sekwencja(p, "ogon_zamach", F(20, 34), [
        (0.16, zl(obr(28, -0.12 * nog, -4), S(0.2, 6), {"Ogon": (2, -12, 0), "Szyja1": (6, -10, 0), "NogiP2": (14, 0, 0),
                                                         "NogiT2": (14, 0, 0)})),
        (0.4, zl(obr(-120, -0.2 * nog, 9), S(0.35, 10), {"Ogon": (1, 13, 0), "Szyja1": (8, 14, 0), "Glowa": (0, 10, 0)})),
        (0.62, zl(obr(-255, -0.2 * nog, 9), S(0.35, 10), {"Ogon": (1, 13, 0), "Szyja1": (8, 14, 0), "Glowa": (0, 10, 0)})),
        (0.84, zl(obr(-372, -0.08 * nog, -3), S(0.15, 2), {"Ogon": (2, -15, 0), "Szyja1": (2, -6, 0)})),
        (1.0, obr(-360))], {"uderzenie_start": 0.22, "uderzenie_stop": 0.8})

    # ------------------------------------------------------------------ ryk
    ryk = zl(T(y=0.04, z=0.05 * L, rx=-12), S(1.0, 24), {
        "Szyja1": (-4, 0, 0), "Szyja2": (6, 0, 0), "Glowa": (-10, 0, 0), "Szczeka": (56, 0, 0), "Ogon": (7, 0, 0),
        "NogiP1": (12, 0, 0), "NogiT1": (10, 0, 0), "NogiT2": (8, 0, 0)})
    sekwencja(p, "ryk", F(40, 64), [
        (0.18, zl(T(y=-0.1 * nog, z=-0.08 * L, rx=-4), S(0.35, 10), {"Szyja1": (-14, 0, 0), "Szyja2": (-6, 0, 0),
                                                                     "Glowa": (12, 0, 0), "Szczeka": (4, 0, 0)})),
        (0.32, ryk), (0.44, zl(ryk, {"Glowa": (-12, 6, 4)})), (0.56, zl(ryk, {"Glowa": (-9, -6, -4)})),
        (0.68, zl(ryk, {"Glowa": (-12, 5, 3)})), (0.8, zl(ryk, {"Glowa": (-10, 0, 0), "Szczeka": (50, 0, 0)})),
        (0.9, zl(T(rx=-3), S(0.3, 4), {"Szczeka": (8, 0, 0), "Glowa": (-2, 0, 0)}))],
        {"ryk_start": 0.32, "ryk_stop": 0.8})

    # ------------------------------------------------------------------ szybowanie (start / pętla / lądowanie)
    lot_y = nog + H * 1.1
    podkul = {"NogiP1": (46, 0, 0), "NogiP2": (34, 0, 0), "NogiT1": (40, 0, 0), "NogiT2": (36, 0, 0)}
    szyb = zl(T(y=lot_y, rx=6), S(1.0, 2, 4), podkul, {
        "Szyja1": (a1 * 0.5, 0, 0), "Szyja2": (a2 * 0.4, 0, 0), "Glowa": (-(a1 * 0.5 + a2 * 0.4) + 4, 0, 0), "Ogon": (4, 0, 0)})
    przysiad = zl(T(y=-0.3 * nog, rx=5), S(0.5, 30), {"Szyja1": (8, 0, 0), "NogiP1": (-14, 0, 0), "NogiP2": (36, 0, 0),
                                                      "NogiT1": (-18, 0, 0), "NogiT2": (42, 0, 0), "Ogon": (-4, 0, 0)})
    sekwencja(p, "szybowanie_start", F(14, 24), [
        (0.3, przysiad),
        (0.62, zl(T(y=lot_y * 0.7, rx=-10), S(0.9, -26), {"Szyja1": (4, 0, 0), "NogiP1": (20, 0, 0), "NogiT1": (30, 0, 0),
                                                          "Ogon": (8, 0, 0)})),
        (1.0, szyb)], {"odbicie": 0.36})
    petla(p, "szybowanie_petla", F(24, 40), szyb, [
        ("Tulow", "przes", (0, 0.07 + 0.05 * b, 0), 1, 0.3), ("Tulow", "obrot", (1.5, 0, 0), 1, 0.0),
        ("Skrz1", "obrot", (0, 0, 9), 1, 0.0), ("Skrz2", "obrot", (0, 0, 9), 1, -0.14),
        ("Ogon1", "obrot", (2, 0, 0), 1, 0.4), ("Ogon2", "obrot", (3, 0, 0), 1, 0.28),
        ("Ogon3", "obrot", (3, 0, 0), 1, 0.16), ("Ogon4", "obrot", (4, 0, 0), 1, 0.04), ("Glowa", "obrot", (1.5, 0, 0), 1, 0.5)])
    sekwencja(p, "szybowanie_ladowanie", F(16, 28), [
        (0.0, szyb),
        (0.36, zl(T(y=lot_y * 0.42, rx=-15), S(1.0, 30), {"Szyja1": (10, 0, 0), "Glowa": (6, 0, 0), "NogiP1": (-22, 0, 0),
                                                          "NogiP2": (8, 0, 0), "NogiT1": (-26, 0, 0), "NogiT2": (14, 0, 0),
                                                          "Ogon": (-6, 0, 0)}), "liniowo"),
        (0.56, zl(T(y=-0.24 * nog, rx=5), S(0.6, -12), {"Szyja1": (10, 0, 0), "NogiP1": (-10, 0, 0), "NogiP2": (30, 0, 0),
                                                        "NogiT1": (-14, 0, 0), "NogiT2": (36, 0, 0), "Ogon": (6, 0, 0)})),
        (0.8, zl(T(y=0.03, rx=-1), S(0.2, 6), {"Szyja1": (-3, 0, 0)}))], {"ladowanie": 0.56})

    # ------------------------------------------------------------------ nurkowanie (skok / uderzenie w ziemię)
    nurek = zl(T(y=lot_y * 0.9, z=0.15 * L, rx=48), {"Skrz1": (0, 6, -dih * 0.5), "Skrz2": (0, 16, -6)}, podkul, {
        "Szyja1": (a1 * 0.6, 0, 0), "Szyja2": (a2 * 0.5, 0, 0), "Glowa": (-20, 0, 0), "Szczeka": (14, 0, 0), "Ogon": (-3, 0, 0)})
    sekwencja(p, "nurkowanie_skok", F(14, 24), [
        (0.24, przysiad),
        (0.62, zl(T(y=lot_y * 1.7, rx=-20), S(1.0, 34), {"Szyja1": (-8, 0, 0), "NogiP1": (24, 0, 0), "NogiT1": (30, 0, 0),
                                                         "NogiP2": (20, 0, 0), "NogiT2": (24, 0, 0), "Ogon": (10, 0, 0)})),
        (1.0, nurek)], {"odbicie": 0.28, "szczyt": 0.62})
    sekwencja(p, "nurkowanie_ladowanie", F(18, 30), [
        (0.0, nurek, "liniowo"),
        (0.16, zl(T(y=-0.34 * nog, z=0.08 * L, rx=11), S(0.75, -24), {
            "Szyja1": (16, 0, 0), "Glowa": (8, 0, 0), "Szczeka": (20, 0, 0), "Ogon": (12, 0, 0),
            "NogiP1": (-20, 0, 12), "NogiP2": (40, 0, 0), "NogiT1": (-16, 0, 10), "NogiT2": (44, 0, 0)})),
        (0.4, zl(T(y=0.1 + 0.1 * b, rx=-6), S(0.5, 16), {"Szyja1": (-8, 0, 0), "Glowa": (-6, 0, 0), "Ogon": (-4, 0, 0)})),
        (0.68, zl(T(y=-0.06 * nog, rx=2), S(0.2, -2), {"Szyja1": (3, 0, 0)}))], {"uderzenie": 0.16})

    # ------------------------------------------------------------------ koziołek (bezwładny po mocnym ciosie)
    def bezwl(f):
        return {"Szyja1": (22 * f, 0, 6 * f), "Szyja2": (14 * f, 0, 0), "Glowa": (18 * f, 8 * f, 0), "Szczeka": (22, 0, 0),
                "Ogon": (-14 * f, 6 * f, 0), "Skrz1": (0, 0, -22 * f), "Skrz2": (0, 10 * f, -14 * f),
                "NogiP1": (-36 * f, 0, 14), "NogiP2": (20, 0, 0), "NogiT1": (34 * f, 0, 14), "NogiT2": (24, 0, 0)}

    sekwencja(p, "koziolek_dlugi", F(36, 54), [
        (0.1, zl(T(y=0.3 * H, rx=-40, rz=6), bezwl(0.6))),
        (0.24, zl(T(y=0.9 * H + 0.4 * nog, rx=-150, rz=-8), bezwl(1.0))),
        (0.4, zl(T(y=0.6 * H, rx=-275, rz=8), bezwl(-0.8))),
        (0.52, zl(T(y=-0.3 * nog, rx=-352, rz=-3), bezwl(0.7)), "gladko"),
        (0.62, zl(T(y=-0.36 * nog, rx=-358, rz=2), bezwl(0.45))),
        (0.8, zl(T(y=-0.2 * nog, rx=-362, rz=-2), {"Szyja1": (10, 0, 0), "Glowa": (4, -12, 6), "Szczeka": (8, 0, 0),
                                                 "NogiP2": (30, 0, 0), "NogiT2": (34, 0, 0), "Ogon": (-6, 0, 0)})),
        (0.9, zl(T(y=-0.05 * nog, rx=-360), {"Glowa": (-3, 10, -5)})),
        (1.0, T(rx=-360))], {"upadek": 0.52})

    sekwencja(p, "koziolek", 14, [                              # koziołek gry trwa 0,5 s: jeden czysty obrót w tył
        (2 / 14.0, zl(T(y=0.35 * H, rx=-50), bezwl(0.5))),
        (6 / 14.0, zl(T(y=0.8 * H + 0.3 * nog, rx=-180), bezwl(1.0))),
        (10 / 14.0, zl(T(y=0.45 * H, rx=-310), bezwl(0.6))),
        (12 / 14.0, zl(T(y=-0.15 * nog, rx=-356), bezwl(0.2))),
        (1.0, T(rx=-360))], {"upadek": 12 / 14.0})

    # ------------------------------------------------------------------ poza do portretu (drabina, panel): jedna klatka
    petla(p, "portret", 2, zl(T(rx=-5), S(0.5, 12), {
        "Szyja1": (-6, 14, 0), "Szyja2": (-2, 14, 0), "Glowa": (4, 22, 0), "Szczeka": (7, 0, 0),
        "Ogon1": (2, -10, 0), "Ogon2": (3, -14, 0), "Ogon3": (4, -18, 0), "Ogon4": (6, -22, 0)}), [])

    # ------------------------------------------------------------------ pożarcie (finisher)
    sekwencja(p, "pozarcie", F(36, 56), [
        (0.12, zl(T(z=0.1 * L, rx=7), {"Szyja1": (22, 0, 0), "Szyja2": (10, 0, 0), "Glowa": (-6, 0, 0), "Szczeka": (46, 0, 0)}),
         "liniowo"),
        (0.18, zl(T(z=0.1 * L, rx=7), {"Szyja1": (24, 0, 0), "Szyja2": (10, 0, 0), "Glowa": (-4, 0, 0), "Szczeka": (4, 0, 0)})),
        (0.36, zl(T(z=-0.04 * L, rx=-8), S(0.3, 12), {"Szyja1": (-24, 0, 0), "Szyja2": (-14, 0, 0), "Glowa": (-28, 0, 0),
                                                      "Szczeka": (38, 0, 0), "Ogon": (8, 0, 0)}), "liniowo"),
        (0.46, zl(T(z=-0.04 * L, rx=-9, y=-0.04), {"Szyja1": (-20, 0, 0), "Szyja2": (-12, 0, 0), "Glowa": (-22, 0, 0),
                                                   "Szczeka": (0, 0, 0)})),
        (0.56, zl(T(rx=-5, y=0.03), {"Szyja1": (-24, 0, 0), "Szyja2": (-8, 0, 0), "Glowa": (-14, 0, 0), "Szczeka": (10, 0, 0)})),
        (0.66, zl(T(rx=-2, y=-0.03), {"Szyja1": (-8, 0, 0), "Glowa": (-4, 0, 0), "Szczeka": (0, 0, 0)})),
        (0.78, zl(T(rz=4), S(0.2, 8), {"Glowa": (-4, 10, 8), "Ogon": (6, 16, 0), "Szczeka": (12, 0, 0)})),
        (0.9, zl(T(rz=-3), S(0.1, 2), {"Glowa": (-2, -8, -6), "Ogon": (4, -14, 0), "Szczeka": (2, 0, 0)}))],
        {"ugryzienie": 0.18, "polkniecie": 0.46})

    # ------------------------------------------------------------------ radość po ewolucji
    sekwencja(p, "radosc", F(44, 70), [
        (0.16, przysiad),
        (0.36, zl(T(y=0.5 * H + 0.5 * H * b, rx=-22), S(1.0, 34), {
            "Szyja1": (-12, 0, 0), "Szyja2": (-6, 0, 0), "Glowa": (-16, 0, 0), "Szczeka": (48, 0, 0), "Ogon": (12, 0, 0),
            "NogiP1": (-42, 0, 0), "NogiP2": (30, 0, 0), "NogiT1": (16, 0, 0)})),
        (0.5, zl(T(y=0.3 * H, rx=-14), S(1.0, -16), {"Szyja1": (-8, 0, 0), "Glowa": (-12, 0, 0), "Szczeka": (40, 0, 0),
                                                    "NogiP1": (-30, 0, 0), "NogiP2": (20, 0, 0), "Ogon": (6, 0, 0)})),
        (0.64, zl(T(y=-0.16 * nog, rx=4), S(0.6, 10), {"Szyja1": (6, 0, 0), "Szczeka": (10, 0, 0), "NogiP2": (24, 0, 0),
                                                      "NogiT2": (26, 0, 0)})),
        (0.78, zl(T(y=0.04, rz=5, ry=6), S(0.35, 14), {"Glowa": (-8, 10, 6), "Ogon": (6, -18, 0)})),
        (0.9, zl(T(rz=-4, ry=-5), S(0.15, 4), {"Glowa": (-4, -8, -5), "Ogon": (4, 16, 0)}))], {"szczyt": 0.36})

    # ------------------------------------------------------------------ poza na cokół (trofeum)
    petla(p, "cokol", F(60, 90), zl(T(rx=-6), S(0.72, 14), {
        "Szyja1": (-8, 0, 0), "Szyja2": (-2, 8, 0), "Glowa": (6, 12, 0), "NogaPL1": (-16, 0, 0), "NogaPL2": (10, 0, 0),
        "Ogon1": (2, 12, 0), "Ogon2": (3, 16, 0), "Ogon3": (4, 20, 0), "Ogon4": (6, 24, 0)}), [
        ("Tulow", "przes", (0, 0.02 + 0.01 * w, 0), 1, 0.0), ("Skrz1", "obrot", (0, 0, 2.5), 1, 0.1),
        ("Skrz2", "obrot", (0, 0, 2.5), 1, 0.0), ("Glowa", "obrot", (1.2, 0, 0), 1, 0.3), ("Ogon4", "obrot", (0, 4, 0), 1, 0.2)])
    return p


# --------------------------------------------------------------------------- nogi na ziemi (wypiekanie kluczy)
def _gladko(k, kosc, kanal, f):
    """Wartość kanału w klatce f: krzywa Catmulla-Roma po kluczach (odcinki „liniowo” — liniowo), pętla zawinięta."""
    kl = k.kanaly.get((kosc, kanal))
    if not kl:
        return (0.0, 0.0, 0.0)
    pts = [(x, kl[x]) for x in sorted(kl)]
    n = float(k.dlugosc)
    if k.petla:
        baza = [(x, v) for x, v in pts if x < n - 1e-6] or pts
        pts = [(x - n, v) for x, v in baza] + baza + [(x + n, v) for x, v in baza]
    if f <= pts[0][0]:
        return tuple(pts[0][1][:3])
    if f >= pts[-1][0]:
        return tuple(pts[-1][1][:3])
    i = max(j for j in range(len(pts) - 1) if pts[j][0] <= f)
    (f1, v1), (f2, v2) = pts[i], pts[i + 1]
    u = (f - f1) / (f2 - f1)
    if v1[3] == "liniowo":
        return tuple(v1[c] + (v2[c] - v1[c]) * u for c in range(3))
    f0, v0 = pts[i - 1] if i > 0 else (f1, v1)
    f3, v3 = pts[i + 2] if i + 2 < len(pts) else (f2, v2)
    wyn = []
    for c in range(3):
        m1 = (v2[c] - v0[c]) / (f2 - f0) * (f2 - f1) if (f2 > f0 and i > 0) else 0.0
        m2 = (v3[c] - v1[c]) / (f3 - f1) * (f2 - f1) if (f3 > f1 and i + 2 < len(pts)) else 0.0
        wyn.append((2 * u ** 3 - 3 * u ** 2 + 1) * v1[c] + (u ** 3 - 2 * u ** 2 + u) * m1
                   + (-2 * u ** 3 + 3 * u ** 2) * v2[c] + (u ** 3 - u ** 2) * m2)
    return tuple(wyn)


def _posadz(p, k, krok_kl=2):
    """Zastąp klucze nóg kluczami z odwrotnej kinematyki: stopa (kostka) trzyma się celu na ziemi mimo ruchu tułowia,
    w chodzie i biegu idzie po torze kroku, stopa zostaje płaska. Gdy cel jest poza zasięgiem nogi (skok, lot),
    noga płynnie przechodzi do pozy ręcznej z klipu. Klucze tułowia są zagęszczane tą samą krzywą, żeby Blender
    i ten rachunek widziały ten sam ruch. Zwraca nic; ustawia k.predkosc (jednostki projektu na sekundę) dla chodu."""
    P, G = p.dane_stadium, p.geometria
    n = k.dlugosc
    Tj = G["Tulow"]
    klatki = list(range(0, n + 1, krok_kl))
    tor = {f: (_gladko(k, "Tulow", "przes", f), _gladko(k, "Tulow", "obrot", f)) for f in klatki}
    chod = getattr(k, "chod", None)
    za_obrotem = k.nazwa == "ogon_zamach"                      # stopy idą za obrotem ciała wokół pionu
    nowe = {}
    for nr, noga in enumerate(NOGI):
        H0, K0, A0 = G[noga + "1"], G[noga + "2"], G[noga + "3"]
        l1 = math.hypot(K0[1] - H0[1], K0[2] - H0[2])
        l2 = math.hypot(A0[1] - K0[1], A0[2] - K0[2])
        a10 = math.atan2(K0[2] - H0[2], -(K0[1] - H0[1]))
        a20 = math.atan2(A0[2] - K0[2], -(A0[1] - K0[1]))
        przod = noga.startswith("NogaP")
        D = H0[1] - A0[1]
        for f in klatki:
            tp, tr = tor[f]
            R = macierz_obrotu(tr[0], 0.0 if za_obrotem else tr[1], tr[2])
            cel = [A0[0], A0[1], A0[2]]
            mach = 0.0
            if chod:
                u = (f / float(n) + chod["fazy"][nr]) % 1.0
                S, b_ = chod["krok"] * D, chod["podpor"]
                if u < b_:                                      # podpór: stopa jedzie w tył ze stałą prędkością
                    cel[2] += S * (0.5 - u / b_)
                else:                                           # przenoszenie: łuk do przodu
                    mach = (u - b_) / (1.0 - b_)
                    cel[2] += S * (-0.5 * math.cos(math.pi * mach))
                    cel[1] += chod["unies"] * D * math.sin(math.pi * mach)
            else:
                zas = 0.4 * D                                   # tułów może odjechać o tyle, zanim stopa się przesunie
                cel[2] += tp[2] - max(-zas, min(zas, tp[2]))
                cel[0] += tp[0] - max(-zas, min(zas, tp[0]))
            d = (cel[0] - Tj[0] - tp[0], cel[1] - Tj[1] - tp[1], cel[2] - Tj[2] - tp[2])
            loc = tuple(R[0][i] * d[0] + R[1][i] * d[1] + R[2][i] * d[2] for i in range(3))   # Rᵀ · d
            v = (loc[0] + Tj[0] - H0[0], loc[1] + Tj[1] - H0[1], loc[2] + Tj[2] - H0[2])
            vy = -math.hypot(v[0], v[1])
            odl, zasieg = math.hypot(vy, v[2]), l1 + l2
            lot = max(0.0, min(1.0, (odl / zasieg - 0.97) / 0.2))  # 0 = stopa na ziemi, 1 = noga w powietrzu
            dd = min(max(odl, abs(l1 - l2) + 1e-3), zasieg * 0.999)
            gam = math.atan2(v[2], -vy)
            kat = math.acos(max(-1.0, min(1.0, (l1 * l1 + dd * dd - l2 * l2) / (2 * l1 * dd))))
            a1 = gam - kat if przod else gam + kat
            a2 = math.atan2(dd * math.sin(gam) - l1 * math.sin(a1), dd * math.cos(gam) - l1 * math.cos(a1))
            rx1 = -math.degrees(a1 - a10)
            rx2 = -math.degrees((a2 - a20) - (a1 - a10))
            rz1 = math.degrees(math.atan2(v[0], max(1e-6, -v[1]))) if v[1] < 0 else 0.0
            m1, m2 = _gladko(k, noga + "1", "obrot", f), _gladko(k, noga + "2", "obrot", f)
            o1 = (rx1 + (m1[0] - rx1) * lot, m1[1] * lot, rz1 + (m1[2] - rz1) * lot)
            o2 = (rx2 + (m2[0] - rx2) * lot, 0.0, 0.0)
            stopa = -(tr[0] + o1[0] + o2[0]) * (1.0 - lot) + 18.0 * lot + (20.0 * math.sin(math.pi * mach) if mach else 0.0)
            nowe[(noga + "1", f)], nowe[(noga + "2", f)], nowe[(noga + "3", f)] = o1, o2, (stopa, 0.0, 0.0)
    for noga in NOGI:
        for c in "123":
            k.kanaly[(noga + c, "obrot")] = {float(f): [nowe[(noga + c, f)][0], nowe[(noga + c, f)][1],
                                                        nowe[(noga + c, f)][2], "gladko"] for f in klatki}
    for i, kanal in enumerate(("przes", "obrot")):
        if ("Tulow", kanal) in k.kanaly:
            k.kanaly[("Tulow", kanal)] = {float(f): [tor[f][i][0], tor[f][i][1], tor[f][i][2], "gladko"] for f in klatki}
    if chod:
        D = G["NogaPL1"][1] - G["NogaPL3"][1]
        k.predkosc = chod["krok"] * D * 30.0 / (chod["podpor"] * n)


def _ik(G, noga, tp, tr, cel):
    """Kąty nogi dla kostki w punkcie `cel` przy tułowiu przesuniętym o tp i obróconym o tr:
    (udo rx, podudzie rx, udo rz, odległość / zasięg nogi)."""
    Tj = G["Tulow"]
    H0, K0, A0 = G[noga + "1"], G[noga + "2"], G[noga + "3"]
    l1 = math.hypot(K0[1] - H0[1], K0[2] - H0[2])
    l2 = math.hypot(A0[1] - K0[1], A0[2] - K0[2])
    a10 = math.atan2(K0[2] - H0[2], -(K0[1] - H0[1]))
    a20 = math.atan2(A0[2] - K0[2], -(A0[1] - K0[1]))
    R = macierz_obrotu(*tr)
    d = (cel[0] - Tj[0] - tp[0], cel[1] - Tj[1] - tp[1], cel[2] - Tj[2] - tp[2])
    loc = tuple(R[0][i] * d[0] + R[1][i] * d[1] + R[2][i] * d[2] for i in range(3))
    v = (loc[0] + Tj[0] - H0[0], loc[1] + Tj[1] - H0[1], loc[2] + Tj[2] - H0[2])
    vy = -math.hypot(v[0], v[1])
    odl, zasieg = math.hypot(vy, v[2]), l1 + l2
    dd = min(max(odl, abs(l1 - l2) + 1e-3), zasieg * 0.999)
    gam = math.atan2(v[2], -vy)
    kat = math.acos(max(-1.0, min(1.0, (l1 * l1 + dd * dd - l2 * l2) / (2 * l1 * dd))))
    a1 = gam - kat if noga.startswith("NogaP") else gam + kat
    a2 = math.atan2(dd * math.sin(gam) - l1 * math.sin(a1), dd * math.cos(gam) - l1 * math.cos(a1))
    rz1 = math.degrees(math.atan2(v[0], max(1e-6, -v[1]))) if v[1] < 0 else 0.0
    return -math.degrees(a1 - a10), -math.degrees((a2 - a20) - (a1 - a10)), rz1, odl / zasieg


def _posadz_chod(p, k):
    """Chód i bieg pod prędkość gry. Stopa w podporze cofa się względem korzenia dokładnie z prędkością `v` (studs/s),
    więc gdy gra przesuwa smoka z tą prędkością, stopa stoi na ziemi. Maluchy mają za krótkie nogi na taki krok,
    dlatego w susie tułów zostaje w tyle nad stopami (kappa) i nadrabia w locie, a w chodzie przysiada tyle, ile trzeba,
    żeby noga sięgnęła końców kroku. Klucze co klatkę; k.predkosc = v w jednostkach projektu na sekundę."""
    G, ch, n, sk = p.geometria, k.chod, k.dlugosc, p.skala
    s = ch["podpor"]
    beta = s / float(n)
    Sd = ch["v"] * s / 30.0 / sk                                # droga stopy w podporze (jednostki projektu)
    g0, g1 = min(ch["start"]), max(ch["start"]) + s             # faza naziemna (klatki)
    c = ch["kappa"] * ch["v"] * (g1 - g0) / 30.0 / sk           # o tyle tułów cofa się nad stopami w fazie naziemnej
    A, czest, umin = ch["podskok"]
    pa, upa = ch["pochyl"]

    def tz(f):
        if c == 0.0:
            return 0.0
        ff = (f - g0) % n
        if ff <= g1 - g0:
            return c * (0.5 - ff / float(g1 - g0))
        return -c / 2.0 * math.cos(math.pi * (ff - (g1 - g0)) / float(n - (g1 - g0)))

    baza = {f: (_gladko(k, "Tulow", "przes", f), _gladko(k, "Tulow", "obrot", f)) for f in range(n + 1)}

    def tulow(f, przysiad):
        tp, tr = baza[f]
        u = f / float(n)
        return ((tp[0], tp[1] - A * math.cos(2 * math.pi * czest * (u - umin)) - przysiad, tp[2] + tz(f)),
                (tr[0] + pa * math.cos(2 * math.pi * (u - upa)), tr[1], tr[2]))

    def cel(nr, f):
        A0, H0 = G[NOGI[nr] + "3"], G[NOGI[nr] + "1"]
        st = ch["start"][nr]
        u = ((f - st) % n) / float(n)
        sr = tz(st + s / 2.0)                                   # w połowie podporu stopa jest pod biodrem
        if u < beta - 1e-9:
            return (A0[0], A0[1], A0[2] + sr + Sd * (0.5 - u / beta)), 0.0
        m = (u - beta) / (1.0 - beta)
        return (A0[0], A0[1] + ch["unies"] * (H0[1] - A0[1]) * math.sin(math.pi * m), A0[2] + sr - Sd / 2.0 * math.cos(math.pi * m)), m

    dmin = min(G[x + "1"][1] - G[x + "3"][1] for x in NOGI)
    przysiad = 0.0
    while przysiad < 0.5 * dmin:                                # najmniejszy przysiad, przy którym stopy w podporze sięgają ziemi
        ok = True
        for f in range(n):
            tp, tr = tulow(f, przysiad)
            for nr, noga in enumerate(NOGI):
                c_, m = cel(nr, f)
                if m == 0.0 and _ik(G, noga, tp, tr, c_)[3] > 0.985:
                    ok = False
        if ok:
            break
        przysiad += 0.02 * dmin
    nowe = {}
    for f in range(n + 1):
        tp, tr = tulow(f, przysiad)
        nowe[("Tulow", f)] = (tp, tr)
        for nr, noga in enumerate(NOGI):
            c_, m = cel(nr, f)
            rx1, rx2, rz1, _ = _ik(G, noga, tp, tr, c_)
            nowe[(noga + "1", f)] = (rx1, 0.0, rz1)
            nowe[(noga + "2", f)] = (rx2, 0.0, 0.0)
            nowe[(noga + "3", f)] = (-(tr[0] + rx1 + rx2) + (26.0 * math.sin(math.pi * m) if m else 0.0), 0.0, 0.0)
    for noga in NOGI:
        for x in "123":
            k.kanaly[(noga + x, "obrot")] = {float(f): list(nowe[(noga + x, f)]) + ["gladko"] for f in range(n + 1)}
    k.kanaly[("Tulow", "przes")] = {float(f): list(nowe[("Tulow", f)][0]) + ["gladko"] for f in range(n + 1)}
    k.kanaly[("Tulow", "obrot")] = {float(f): list(nowe[("Tulow", f)][1]) + ["gladko"] for f in range(n + 1)}
    k.predkosc = ch["v"] / sk
    k.przysiad = przysiad


def dodaj_klipy(p, dodatkowe=True):
    """Komplet klipów stadium: pozy i cykle z _klipy_surowe, potem nogi posadzone na ziemi (_posadz)."""
    _klipy_surowe(p, dodatkowe)
    for k in p.klipy:
        (_posadz_chod if hasattr(k, "chod") else _posadz)(p, k)
    return p


def klipy_jaja(j, n):
    """Klip „wyklucie” jaja (ta sama długość co klip smoka): kołysanie, pęknięcie, czapka odlatuje, odłamki opadają."""
    sekwencja(j, "wyklucie", n, [
        (0.14, {"Dol": (0, 0, 6)}), (0.27, {"Dol": (0, 0, -7)}), (0.38, {"Dol": (0, 0, 4), "Gora": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}},
                                                                 "liniowo"),
        (0.46, {"Dol": (0, 0, 0), "Gora": {"obrot": (-8, 0, 6), "przes": (0, 0.35, 0)},
                "OdlamekL": {"obrot": (0, 0, -20), "przes": (0.3, 0.3, 0.2)},
                "OdlamekP": {"obrot": (0, 0, 20), "przes": (-0.3, 0.3, -0.1)}}),
        (0.58, {"Gora": {"obrot": (-70, 10, 40), "przes": (-0.7, 2.3, -1.8)},
                "OdlamekL": {"obrot": (40, 0, -120), "przes": (1.5, 0.9, 0.8)},
                "OdlamekP": {"obrot": (-30, 0, 130), "przes": (-1.6, 0.8, -0.3)}}, "gladko"),
        (0.74, {"Gora": {"obrot": (-165, 20, 12), "przes": (-1.0, -1.0, -3.9)},
                "OdlamekL": {"obrot": (90, 0, -200), "przes": (2.6, -1.25, 1.6)},
                "OdlamekP": {"obrot": (-80, 0, 220), "przes": (-2.7, -1.25, -0.7)}}),
        (1.0, {"Dol": (0, 0, 0), "Gora": {"obrot": (-172, 20, 0), "przes": (-1.0, -1.1, -4.0)},
               "OdlamekL": {"obrot": (90, 0, -200), "przes": (2.6, -1.25, 1.6)},
               "OdlamekP": {"obrot": (-80, 0, 220), "przes": (-2.7, -1.25, -0.7)}})],
        {"pekniecie": 0.46})
    return j
