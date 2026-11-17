# -*- coding: utf-8 -*-
"""Pomiar przenikania broni w głowę i tułów: głębokość wejścia i najmniejsza odległość, klatka po klatce.

Miara dla pary (bryła broni W, bryła ciała B):  m = min po punktach p ∈ W odległości ze znakiem sdf_B(p).
  m < 0  → przenikanie, GŁĘBOKOŚĆ = −m: jak głęboko pod powierzchnią bryły ciała leży najgłębszy punkt broni;
  m ≥ 0  → ODLEGŁOŚĆ = m (najmniejsza odległość między bryłami).
Strefa (głowa, tułów) = najmniejsze m po wszystkich parach broń × bryła strefy. sdf_B jest wypukła (blok, walec, kula:
dokładna; klin, narożnik: max(blok, płaszczyzny)), a W wypukła — minimum jest jedno, więc wystarcza siatka punktów
co KROK_SIATKI studa i zagęszczanie wokół najlepszego punktu (6 poziomów, do ok. 0,0015 studa) dla par bliżej niż
ZAGESZCZAJ_PONIZEJ. Pary dalej niż ODCIECIE od siebie (kule opisane) nie są liczone: odległość ≥ ODCIECIE.
"""
import math
import os
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import bryly as B  # noqa: E402
from pozy import REPO, Aktor, kwat_z_macierzy  # noqa: E402

ZRODLA_WALKI = os.path.join(REPO, "swiat", "test_walki2", "zrodla")

KROK_SIATKI = 0.08          # studa — odstęp punktów próbnych w bryłach broni
ODCIECIE = 0.6              # studa — dalej nie liczymy dokładnie (wynik „≥ 0,6”)
ZAGESZCZAJ_PONIZEJ = 0.3    # studa — pary z m z siatki poniżej tego są zagęszczane
PROBKI_NA_S = 120           # próbki na sekundę czasu klipu (dane są co 1/30 s — 4 próbki na klatkę, z Lerp jak w grze)
SUMA_BRYL = True            # głębokość także w sumie brył strefy (B.glebokosc_w_sumie), nie tylko w jednej bryle

# PROGI (studa). Głowa: żadnego przenikania — tolerancja rzędu grubości krawędzi najcieńszych brył modeli
# (oczy, brwi, nity 0,03–0,06 studa wystają z twarzy o połowę grubości); 0,02 jest poniżej tego, co da się zobaczyć
# na ekranie walki (głowa bohatera ma ok. 1,5 studa, czyli ok. 40–90 pikseli na telefonie: 0,02 studa < 1 piksel).
PROG_GLOWA = 0.02
# Tułów: broń trzymana przy ciele (tarcza na przedramieniu przy boku, rękojeść przy pasie, łuk przy kołczanie,
# kostur przy szacie) DOTYKA ubrania z założenia — dozwolony dotyk to wejście do 0,10 studa (grubość tabardu, pasa,
# peleryny i szaty 0,05–0,12 studa: broń może „wgnieść” warstwę ubrania, ale nie wchodzi w ciało pod nią).
PROG_TULOW = 0.10

# Broń i strefy znanych aktorów (klucz z tabeli aktorów walki). Broń: grupy akcesoriów albo kości z bryłami broni.
# Strefy: kości (z potomkami tylko tam, gdzie podano „+”) — bryły ciała (grupa 0) i nie-broni na tych kościach.
SPEC = {
    "wojownik": {"bron_grupy": ["rycerz_miecz", "rycerz_tarcza"], "glowa": ["Head"],
                 "tulow": ["UpperTorso", "LowerTorso"]},
    "zwiadowca": {"bron_grupy": ["zwiadowca_luk", "zwiadowca_sztylet"], "glowa": ["Head"],
                  "tulow": ["UpperTorso", "LowerTorso"]},
    "mag": {"bron_grupy": ["kot_mag_kostur"], "glowa": ["Head", "LeftEar", "RightEar"],
            "nakrycie": ["HatPivot"], "tulow": ["UpperTorso", "LowerTorso"]},
    "lesny_troll": {"bron_kosci": ["Maczuga"], "glowa": ["Glowa", "Szczeka"], "tulow": ["Tulow", "Biodra"]},
    "muchomornik": {"bron_kosci": ["Laska"], "glowa": ["Glowa", "Kapelusz", "Broda", "Powieki"],
                    "tulow": ["Tulow", "Biodra"]},
    # Dżungla (17.11.2026): kokosy w pięściach (kości KokosL / KokosP) — nazwy nie mówią „broń”, więc wpis jawny
    "kokosowy_silacz": {"bron_kosci": ["KokosL", "KokosP"], "glowa": ["Glowa", "Szczeka"], "tulow": ["Tulow", "Biodra"]},
}
# aktor bez broni w ręku (uderza ciałem, pyskiem, pięścią) — nie ma czego mierzyć
BEZ_BRONI = {"lesny_slime", "cierniowy_wilk", "straznik_lasu"}
SLOWA_BRONI = ("miecz", "tarcz", "luk", "łuk", "sztylet", "kostur", "maczug", "lask", "topor", "topór", "wlocz",
               "włócz", "mlot", "młot", "bron", "broń", "dzid", "buzdygan", "kosa", "sierp", "berl", "różdż", "rozdz",
               "noz", "nóż", "palk", "pałk", "harpun", "trojzab", "trójząb", "kij", "sword", "shield", "bow", "staff",
               "axe", "club", "spear", "dagger", "wand")
GLOWY = ("Head", "Glowa", "Głowa", "Leb", "Łeb", "Twarz")
TULOWIE = ("UpperTorso", "LowerTorso", "Tulow", "Tułów", "Biodra", "Klatka", "Torso", "Brzuch", "Cialo", "Ciało")
NAZWA_BRONI = [("miecz", "miecz"), ("tarcz", "tarcza"), ("luk", "łuk"), ("sztylet", "sztylet"), ("kostur", "kostur"),
               ("maczug", "maczuga"), ("lask", "laska")]


def nazwa_broni(n):
    m = n.lower()
    for k, v in NAZWA_BRONI:
        if k in m:
            return v
    return n


def spec_aktora(klucz, d):
    """Spec z SPEC albo wykryty z nazw grup i kości (nowi aktorzy). None = bez broni."""
    if klucz in SPEC:
        return SPEC[klucz]
    if klucz in BEZ_BRONI:
        return None
    kosci = [k[0] for k in d["kosci"]]
    grupy = [g for g in d["grupy"][1:] if any(s in g.lower() for s in SLOWA_BRONI)]
    kb = [k for k in kosci if any(s in k.lower() for s in SLOWA_BRONI)]
    if not grupy and not kb:
        return None
    glowa = [k for k in kosci if k in GLOWY][:1]
    tulow = [k for k in kosci if k in TULOWIE]
    return {"bron_grupy": grupy, "bron_kosci": kb, "glowa": glowa, "tulow": tulow, "wykryty": True}


class Strefa:
    def __init__(self, nazwa, bryly, prog):
        self.nazwa, self.bryly, self.prog = nazwa, np.array(bryly, dtype=int), prog


class Pomiar:
    """Aktor + jego broń i strefy ciała. pomiar(tory) -> {strefa: (m, bryła broni, bryła ciała)}."""

    def __init__(self, dane, spec, krok=KROK_SIATKI):
        self.d = dane
        self.a = Aktor(dane)
        self.spec = spec
        cz = dane["czesci"]
        grupy = dane["grupy"]
        nazwy_kosci = [k[0] for k in dane["kosci"]]
        self.nazwy = ["%s/%s" % (nazwy_kosci[c[0] - 1], c[2]) for c in cz]
        self.rodzaj = np.array([B.rodzaj(c[1], c[15] if len(c) > 15 else "") for c in cz])
        self.pol = np.array([[c[9] / 2.0, c[10] / 2.0, c[11] / 2.0] for c in cz])
        self.promien = np.linalg.norm(self.pol, axis=1)
        gi_broni = {grupy.index(g) for g in spec.get("bron_grupy", []) if g in grupy}
        ki_broni = {self.a.indeks[k] for k in spec.get("bron_kosci", []) if k in self.a.indeks}
        self.bron = [b for b, c in enumerate(cz) if c[14] in gi_broni or c[0] in ki_broni]
        self.grupa_broni = {}
        for b in self.bron:
            c = cz[b]
            self.grupa_broni[b] = nazwa_broni(grupy[c[14]] if c[14] in gi_broni else nazwy_kosci[c[0] - 1])
        bron = set(self.bron)
        self.strefy = []
        for nazwa, prog in (("glowa", PROG_GLOWA), ("nakrycie", PROG_GLOWA), ("tulow", PROG_TULOW)):
            kosci = spec.get(nazwa)
            if not kosci:
                continue
            zb = {self.a.indeks[k] for k in kosci if k in self.a.indeks}
            if nazwa == "nakrycie":
                br = [b for b, c in enumerate(cz) if c[0] in zb and b not in bron]
            else:
                br = [b for b, c in enumerate(cz) if c[0] in zb and c[14] == 0 and b not in bron]
            if br:
                self.strefy.append(Strefa(nazwa, br, prog))
        # punkty próbne broni (układ lokalny bryły), sklejone; wlasciciel[i] = bryła punktu
        pk, wl, od = [], [], {}
        n = 0
        for b in self.bron:
            p = B.punkty_probne(self.rodzaj[b], self.pol[b], krok)
            pk.append(p)
            wl.append(np.full(len(p), b))
            od[b] = (n, n + len(p))
            n += len(p)
        self.pkt = np.concatenate(pk) if pk else np.zeros((0, 3))
        self.wl = np.concatenate(wl) if wl else np.zeros(0, dtype=int)
        self.zakres = od
        self.krok = krok

    # ------------------------------------------------------------------ jedna poza
    def pomiar_pozy(self, Wb):
        """Wb = CFrame'y brył (nb, 4, 4). Zwraca {strefa: (m, bryła broni, bryła ciała)} (m ≥ ODCIECIE = daleko)."""
        wynik = {}
        srodki = Wb[:, :3, 3]
        for s in self.strefy:
            wynik[s.nazwa] = self._strefa(Wb, srodki, s)
        return wynik

    def _strefa(self, Wb, srodki, s):
        J = np.array(self.bron)
        K = s.bryly
        if len(J) == 0:
            return (math.inf, -1, -1)
        odl = np.linalg.norm(srodki[J][:, None, :] - srodki[K][None, :, :], axis=2)
        dolna = odl - self.promien[J][:, None] - self.promien[K][None, :]
        if dolna.min() >= ODCIECIE:
            return (max(ODCIECIE, float(dolna.min())), -1, -1)
        jj, kk = np.nonzero(dolna < ODCIECIE)
        najlepsze = (math.inf, -1, -1)
        # pary pogrupowane po bryle broni: punkty tej bryły w świecie -> układy brył ciała
        kandydaci = []
        wewnatrz = []                                  # (głębokość w bryle, punkt świata, osie bryły ciała, bryła broni)
        for j in np.unique(jj):
            ks = kk[jj == j]
            a, b = self.zakres[J[j]]
            Rw, tw = Wb[J[j], :3, :3], Wb[J[j], :3, 3]
            P = self.pkt[a:b] @ Rw.T + tw                                   # (n, 3) świat
            for k in ks:
                kb = K[k]
                Rk, tk = Wb[kb, :3, :3], Wb[kb, :3, 3]
                L = (P - tk) @ Rk                                           # (n, 3) układ bryły ciała
                v = B.sdf(self.rodzaj[kb], self.pol[kb], L)
                i = int(np.argmin(v))
                m = float(v[i])
                kandydaci.append((m, int(J[j]), int(kb), self.pkt[a + i]))
                if m < 0:
                    sel = np.nonzero(v < 0)[0]
                    for q in sel[np.argsort(v[sel])][:60]:
                        wewnatrz.append((-float(v[q]), P[q], Rk, int(J[j]), int(kb)))
        kandydaci.sort(key=lambda x: x[0])
        for m, jb, kb, p0 in kandydaci[:4]:
            if m < ZAGESZCZAJ_PONIZEJ:
                m, p0 = self._zageszczaj(Wb, jb, kb, p0, m)
                if m < 0:
                    wewnatrz.append((-m, Wb[jb, :3, :3] @ p0 + Wb[jb, :3, 3], Wb[kb, :3, :3], jb, kb))
            if m < najlepsze[0]:
                najlepsze = (m, jb, kb)
        if najlepsze[1] < 0 and kandydaci:
            m, jb, kb, _ = kandydaci[0]
            najlepsze = (m, jb, kb)
        if wewnatrz and SUMA_BRYL:
            # głębokość w SUMIE brył strefy (stos cienkich warstw, np. dzwon szaty Maga, nie ogranicza jej do połowy
            # grubości warstwy) — tylko dla punktów, które w ogóle są w jakiejś bryle strefy
            wewnatrz.sort(key=lambda x: -x[0])
            wewnatrz = wewnatrz[:150]
            P = np.array([w[1] for w in wewnatrz])
            R = np.array([w[2] for w in wewnatrz])
            bs = [(self.rodzaj[kb], self.pol[kb], Wb[kb, :3, :3], Wb[kb, :3, 3]) for kb in K]
            g = B.glebokosc_w_sumie(P, R, bs)
            i = int(np.argmax(g))
            if g[i] > -najlepsze[0]:
                najlepsze = (-float(g[i]), wewnatrz[i][3], wewnatrz[i][4])
        return najlepsze

    def _zageszczaj(self, Wb, jb, kb, p0, m0):
        """Siatka 5×5×5 wokół najlepszego punktu, krok połowiony 6 razy (punkty tylko wewnątrz bryły broni)."""
        Rw, tw = Wb[jb, :3, :3], Wb[jb, :3, 3]
        Rk, tk = Wb[kb, :3, :3], Wb[kb, :3, 3]
        h = self.pol[jb]
        best, bp = m0, np.array(p0, dtype=float)
        krok = self.krok / 2.0
        u = np.linspace(-2, 2, 5)
        siatka = np.stack(np.meshgrid(u, u, u, indexing="ij"), axis=-1).reshape(-1, 3)
        for _ in range(6):
            c = np.clip(bp + siatka * krok, -h, h)
            if self.rodzaj[jb] != B.BLOK:
                c = c[B.sdf(self.rodzaj[jb], h, c) <= 1e-9]
                if len(c) == 0:
                    krok /= 2.0
                    continue
            P = c @ Rw.T + tw
            L = (P - tk) @ Rk
            v = B.sdf(self.rodzaj[kb], self.pol[kb], L)
            i = int(np.argmin(v))
            if v[i] < best:
                best, bp = float(v[i]), c[i]
            krok /= 2.0
        return best, bp


# --------------------------------------------------------------------------- model przejść z kodu gry
def _tekst_zrodla(nazwa):
    try:
        with open(os.path.join(ZRODLA_WALKI, nazwa), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def model_wskrzeszenia():
    """Jak odtwarzacz robi wstawanie przy wskrzeszeniu (czytane z Obsluga.wskrzeszenie w OdtwarzaczWalki2.luau):
    ("wstecz", przejście do spoczynku po upadku odegranym wstecz) albo ("mieszanie", przejście z ostatniej klatki
    upadku do spoczynku). Bez pliku gry — ("wstecz", 0,15)."""
    import re
    t = _tekst_zrodla("OdtwarzaczWalki2.luau")
    if t is None:
        return ("wstecz", 0.15)
    i = t.find("Obsluga.wskrzeszenie = function")
    cialo = t[i:t.find("\nend\n", i)] if i >= 0 else ""
    if re.search(r'self:klip\(A, "upadek", \{[^}]*predkosc = -', cialo):
        m = re.search(r'if wstecz then\s+self:klip\(A, "spoczynek", \{ przejscie = ([\d.]+)', cialo)
        return ("wstecz", float(m.group(1)) if m else 0.15)
    m = re.search(r'self:klip\(A, "spoczynek", \{ przejscie = ([\d.]+)', cialo)
    return ("mieszanie", float(m.group(1)) if m else 0.45)


# --------------------------------------------------------------------------- skręt broni wokół własnej osi
# Obrót broni wokół jej długiej osi na jedną klatkę danych (1/30 s), po drodze gry: klatka → pół klatki → klatka
# (Lerp jak w Klipy.luau — łapie też „przeskok” między klatkami, jak w upadku Maga). PRÓG 70°/klatkę: najszybszy
# zamierzony skręt w klipach to 54° (sztylet Zwiadowcy), maczuga 42°, laska 46°, miecz 32°; przy 30 kl./s skręt
# powyżej ok. 70° (2100°/s) nie czyta się już jako obrót, tylko jako mignięcie — kryształ kostura (4 jednakowe
# ściany) przy 90° wygląda jak bez ruchu, a przy 120–180° jak przeskok w drugą stronę (kostur Maga przed poprawką:
# 84–156°). Broń prawie kulista albo płaska (wydłużenie < 2, np. tarcza) nie ma „własnej osi” — pomijana.
PROG_SKRETU = 70.0
# zamierzone szybkie obroty broni {(klucz, klip): powód} — dziś żadnych
WYJATKI_SKRETU = {}


def skret_broni(pm, klipy=None):
    """{(broń, klip): (największy skręt °/klatkę, klatka)} dla broni o wydłużeniu ≥ 2."""
    import itertools
    grupy = {}
    for b in pm.bron:
        grupy.setdefault(pm.grupa_broni[b], []).append(b)
    wyn = {}
    for nazwa, br in grupy.items():
        kosci = {int(pm.a.kosc_bryly[b]) for b in br}
        if len(kosci) != 1:
            continue
        kosc = kosci.pop()
        pts = []
        for b in br:
            M, h = pm.a.M[b], pm.pol[b]
            for s in itertools.product((-1, 1), repeat=3):
                pts.append(M[:3, :3] @ (np.array(s) * h) + M[:3, 3])
        P = np.array(pts)
        P -= P.mean(axis=0)
        w, v = np.linalg.eigh(P.T @ P)
        if w[-2] <= 0 or math.sqrt(w[-1] / w[-2]) < 2.0:
            continue
        os_ = v[:, -1]
        for n, kl in pm.a.klipy.items():
            if klipy and n not in klipy:
                continue
            naj = (0.0, 0)
            R = [pm.a.poza([(n, f / (2 * kl["fps"]), 1.0)])[0][kosc, :3, :3] for f in range(2 * kl["dl"] + 1)]
            for f in range(kl["dl"]):
                s = 0.0
                for R0, R1 in ((R[2 * f], R[2 * f + 1]), (R[2 * f + 1], R[2 * f + 2])):
                    q = kwat_z_macierzy(R0.T @ R1)              # skręt (rozkład skręt–wychylenie), 0…180°
                    s += math.degrees(2 * math.atan2(abs(float(q[1:] @ os_)), abs(float(q[0]))))
                if s > naj[0]:
                    naj = (s, f)
            wyn[(nazwa, n)] = naj
    return wyn


# --------------------------------------------------------------------------- scenariusze (co gra naprawdę odtwarza)
def czasy(dlugosc, na_s=PROBKI_NA_S):
    n = max(1, int(math.ceil(dlugosc * na_s - 1e-9)))
    return [dlugosc * i / n for i in range(n + 1)]


def scenariusze(akt, wpis, gestosc=1.0):
    """Lista scenariuszy {nazwa, rodzaj, klip, próbki: [(t, tory)]} dla aktora (wpis z tabeli aktorów walki albo None).

    klip           każdy klip z danych osobno (także nieużywany w walce), 120 próbek na sekundę + koniec;
    wejscie        spoczynek (8 faz) → klip akcji, przejście 0,12 s (Sesja:klip), prędkość klipu ×1 i ×2;
    wyjscie        koniec klipu akcji → spoczynek, przejście 0,15 s (opcja „potem”, DOMYSLNE_PRZEJSCIE);
    upadek         spoczynek / trafienie → upadek, przejście 0,08 s (cios kończący, śmiertelne tyknięcie);
    wskrzeszenie   tak, jak robi to Obsluga.wskrzeszenie (model_wskrzeszenia czyta kod gry): upadek wstecz do klatki 0
                   i 0,15 s do spoczynku (do 17.11.2026: mieszanie ostatniej klatki upadku ze spoczynkiem 0,45 s);
    radosc         spoczynek → radość, przejście 0,2 s (finał).
    gestosc < 1 rzedzi tylko PRZEJŚCIA (mniej faz spoczynku i próbek, bez prędkości ×2) — klipy zawsze 120/s."""
    na_s = PROBKI_NA_S * gestosc
    sc = []
    for nazwa, k in akt.klipy.items():
        sc.append({"nazwa": nazwa, "rodzaj": "klip", "klip": nazwa,
                   "probki": [(t, [(nazwa, t, 1.0)]) for t in czasy(k["dlugosc"], PROBKI_NA_S)]})
    if not wpis:
        return sc
    kl = wpis["klipy"]
    spocz = kl.get("spoczynek")
    if not spocz or spocz not in akt.klipy:
        return sc
    akcje = []
    for a in ("atak", "krytyk", "unik", "blok", "trafienie"):
        if kl.get(a) and kl[a] in akt.klipy and kl[a] not in akcje:
            akcje.append(kl[a])
    for u in wpis.get("umiejetnosci", {}).values():
        if u and u in akt.klipy and u not in akcje:
            akcje.append(u)
    L0 = akt.klipy[spocz]["dlugosc"]
    nf = max(1, int(8 * min(1.0, gestosc)))                  # fazy spoczynku, z której wchodzi akcja
    fazy = [L0 * i / nf for i in range(nf)]

    def przejscie(stary, t_stary, v_stary, nowy, t_nowy, v_nowy, P):
        pr = []
        for tau in czasy(P, na_s)[1:]:
            w = min(1.0, tau / P)
            pr.append((tau, [(stary, akt.czas_toru(stary, t_stary + tau * v_stary), 1.0 - w),
                             (nowy, akt.czas_toru(nowy, t_nowy + tau * v_nowy), w)]))
        return pr

    for x in akcje:
        pr = []
        for f in fazy:
            for v in ((1.0, 2.0) if gestosc >= 1 else (1.0,)):
                pr += przejscie(spocz, f, 1.0, x, 0.0, v, 0.12)
        sc.append({"nazwa": "%s→%s" % (spocz, x), "rodzaj": "wejscie", "klip": x, "probki": pr})
        Lx = akt.klipy[x]["dlugosc"]
        sc.append({"nazwa": "%s→%s" % (x, spocz), "rodzaj": "wyjscie", "klip": x,
                   "probki": przejscie(x, Lx, 1.0, spocz, 0.0, 1.0, 0.15)})
    upadek = kl.get("upadek")
    if upadek and upadek in akt.klipy:
        # wskrzeszenie (v3, Obsluga.wskrzeszenie) jest tylko u klas: potwory nie mają go w danych silnika
        wskrzeszenie = wpis.get("rola", "klasa") == "klasa"
        pr = []
        for f in fazy:
            pr += przejscie(spocz, f, 1.0, upadek, 0.0, 1.0, 0.08)
        traf = kl.get("trafienie")
        if traf and traf in akt.klipy:
            for t in czasy(akt.klipy[traf]["dlugosc"], 15 * gestosc):
                pr += przejscie(traf, t, 1.0, upadek, 0.0, 1.0, 0.08)
        sc.append({"nazwa": "→%s" % upadek, "rodzaj": "upadek", "klip": upadek, "probki": pr})
        Lu = akt.klipy[upadek]["dlugosc"]
        if wskrzeszenie:
            rodzaj_wsk, P_wsk = model_wskrzeszenia()
            if rodzaj_wsk == "wstecz":
                # upadek wstecz od końca do klatki 0 (te same pozy co klip, gęsto po czasie klipu), potem P_wsk s do
                # spoczynku z klatki 0 upadku
                pr = [(Lu - t, [(upadek, Lu - t, 1.0)]) for t in czasy(Lu, PROBKI_NA_S)]
                pr += przejscie(upadek, 0.0, 0.0, spocz, 0.0, 1.0, P_wsk)
                nazwa = "%s wstecz→%s (wskrzeszenie)" % (upadek, spocz)
            else:
                pr = przejscie(upadek, Lu, 1.0, spocz, 0.0, 1.0, P_wsk)
                nazwa = "%s→%s (wskrzeszenie)" % (upadek, spocz)
            sc.append({"nazwa": nazwa, "rodzaj": "wskrzeszenie", "klip": upadek, "probki": pr})
    radosc = kl.get("radosc")
    if radosc and radosc in akt.klipy:
        # radość zaczyna się ≥ 1,48 s czasu sceny po trafieniu kończącym (tRadosc = tHit + 0,38 + 1,1…1,8), a klip
        # ataku kończy się najpóźniej ok. 1,33 s po trafieniu (cięcie przy prędkości 0,75) + 0,15 s przejścia do
        # spoczynku — zwycięzca wchodzi w radość ze spoczynku
        pr = []
        for f in fazy:
            pr += przejscie(spocz, f, 1.0, radosc, 0.0, 1.0, 0.2)
        sc.append({"nazwa": "%s→%s" % (spocz, radosc), "rodzaj": "radosc", "klip": radosc, "probki": pr})
    return sc


def zmierz(pm, scen, postep=None):
    """Mierzy wszystkie próbki scenariuszy. Zwraca listę wyników scenariuszy:
    {nazwa, rodzaj, klip, strefy: {strefa: {m, t, bron, cialo, zle: liczba próbek ponad próg, probki}}}."""
    wyniki = []
    for s in scen:
        st = {z.nazwa: {"m": math.inf, "t": None, "bron": "", "cialo": "", "zle": 0, "zle_t": []} for z in pm.strefy}
        for t, tory in s["probki"]:
            _, Wb = pm.a.poza(tory)
            r = pm.pomiar_pozy(Wb)
            for z in pm.strefy:
                m, jb, kb = r[z.nazwa]
                w = st[z.nazwa]
                if -m > z.prog:
                    w["zle"] += 1
                    w["zle_t"].append(round(t, 4))
                if m < w["m"]:
                    w["m"], w["t"] = m, t
                    w["bron"] = pm.nazwy[jb] if jb >= 0 else ""
                    w["cialo"] = pm.nazwy[kb] if kb >= 0 else ""
                    w["tory"] = tory
        wyniki.append({"nazwa": s["nazwa"], "rodzaj": s["rodzaj"], "klip": s["klip"], "strefy": st,
                       "probek": len(s["probki"])})
        if postep:
            postep(s, st)
    return wyniki
