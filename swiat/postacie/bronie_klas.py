# -*- coding: utf-8 -*-
"""BRONIE KLAS — Mag i Zwiadowca, pula Lv 1–10 (10 broni według ikon z 27.11.2026). Status: propozycja (nazwy
z notatki puli czekają na akceptację; statystyk, cen i szans tu nie ma).

Karol 27.11.2026: „Najpierw powstają modele UI tych broni, na podstawie których robimy modele 3D broni.” Wzór
wyglądu: ikony z Higgsfield (styl Glossy Ink, warianty „Mag A” i „Zwiadowca B”) — assets/processed/Item<…>.png,
wycinki z arkuszy w assets/raw/BronieKlas/ciete/ (poza gitem). Rejestr ikon w Roblox: ikony_broni.json.

Jak to jest zbudowane (kontrakt swiat/postacie/EKWIPUNEK.md, bez nowego systemu — jak miecze puli wojownika):
  - broń = Akcesorium na zaczepie dłoni (RightGripAttachment, łuki LeftGripAttachment): (0, 0, 0) = środek chwytu
    w pięści, oś główna w +Y (drzewce, klinga, widełki, ramiona łuku), lico do przodu (+Z); łuki jak łuk Zwiadowcy:
    ramiona wygięte ku łucznikowi (−Z), cięciwa z tyłu;
  - RODZAJ CHWYTU (Akcesorium.chwyt, chwyty.py, EKWIPUNEK.md pkt 15): różdżki — „rozdzka”, kostury — „drzewce”,
    wałek, nóż i sztylet — „miecz” (broń jednoręczna: miecz, tasak, pałka), proca — „proca” (prawa łapa), łuki — „luk”
    (lewa łapa); korekty kota z chwyty.KOREKTY_KOTA (przez pula_wojownika.KOREKTY_CHWYTU, bez zmian w tamtych plikach);
  - rozmiar pod kota (D-145; ciało Kota-Maga: łapa 0,4 × 0,22 × 0,4, chwyt ok. 0,96 nad ziemią): kostury od −0,85
    (jak kostur Kota-Maga), różdżki ok. 1,2–1,5 studa, sztylety ok. 1,5–1,9; broń na zaczepie dłoni pasuje do każdego
    ciała (EKWIPUNEK.md pkt 1) — człowiek trzyma ją tak samo na RightGripAttachment / LeftGripAttachment;
  - styl: klocki, walce, kliny i kule (bez ostrosłupów, jak pula wojownika), wyraźne kolory z ikon; przedmioty
    zestawu (Kostur Ucznia, Łuk Tropiciela) — delikatna poświata: materiał „poswiata”/„swiecacy” na krysztale,
    cięciwie i iskrach, bez dużej bryły aury; bez liter na modelach (runy wałka to proste rysy i znaki).
Id: mag_<…> / zwiad_<…> (ikony_broni.IKONY → model); kot z bronią do plansz: na_kocie_<id>.

    python -B swiat/postacie/bronie_klas.py                 # lista: rodzaj chwytu, bryły, części Roblox, wymiary
    python -B swiat/postacie/bronie_klas.py --ruch          # broń vs całe ciało kota i ziemia, klatka po klatce
                                                            # (pula_wojownika.bron_w_ruchu) + upadek z korektą
    python -B swiat/postacie/przebuduj.py bronie_klas --bez-filmow   # modele GLB/FBX, ikony, plansze, ekwipunek.json
    python -B swiat/postacie/bronie_klas.py --plansza <plik.png>      # plansza ikona → model (po przebudowie)
    python -B swiat/postacie/bronie_klas.py --ekwipunek               # ekwipunek.json od nowa (np. po wgraniu)
"""
import json
import math
import os
import struct
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if __package__ in (None, ""):
    sys.path.insert(0, REPO)

from swiat.postacie import chwyty as CH  # noqa: E402
from swiat.postacie import pula_wojownika as PW  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium  # noqa: E402
from swiat.postacie.ekwipunek import Przedmiot, ubierz  # noqa: E402

ID = "bronie_klas"
FILMY = []
EKSPORT_MODELI = False             # koty z bronią: tylko plansze; eksport (GLB/FBX) mają same bronie (przedmioty/)
KOREKTY_CHWYTU = PW.KOREKTY_CHWYTU  # korekty kota: dawne + rodzaje chwytu (chwyty.py)
IKONY_JSON = os.path.join(TU, "ikony_broni.json")
ZASOBY_JSON = os.path.join(TU, "bronie_klas_zasoby.json")    # zasoby Model w Roblox (bronie_klas_roblox.py)
WYNIK = os.path.join(TU, "wynik", ID)

# id modelu -> nazwa (propozycja z puli), klasa, rodzaj chwytu, plik ikony (assets/processed), przedmiot zestawu
BRONIE = [
    ("mag_rozdzka_z_patyka", "Różdżka z Patyka", "mag", "rozdzka", "ItemStickWand", False),
    ("mag_kostur_z_miotly", "Kostur z Miotły", "mag", "drzewce", "ItemBroomStaff", False),
    ("mag_walek_czarodziejski", "Wałek Czarodziejski", "mag", "miecz", "ItemMagicRollingPin", False),
    ("mag_rozdzka_ze_swieczki", "Różdżka ze Świeczki", "mag", "rozdzka", "ItemCandleWand", False),
    ("mag_kostur_ucznia", "Kostur Ucznia", "mag", "drzewce", "ItemApprenticeStaff", True),
    ("zwiad_proca_z_galezi", "Proca z Gałęzi", "zwiadowca", "proca", "ItemBranchSlingshot", False),
    ("zwiad_luk_z_wieszaka", "Łuk z Wieszaka", "zwiadowca", "luk", "ItemHangerBow", False),
    ("zwiad_noz_do_masla", "Nóż do Masła", "zwiadowca", "miecz", "ItemButterKnife", False),
    ("zwiad_sztylet_z_szyszki", "Sztylet z Szyszki", "zwiadowca", "miecz", "ItemPineconeDagger", False),
    ("zwiad_luk_tropiciela", "Łuk Tropiciela", "zwiadowca", "luk", "ItemTrackerBow", True),
]
ZESTAWY = {"mag": "kot_mag_uczen", "zwiadowca": "kot_zwiadowca_tropiciel"}   # premia za komplet (5. przedmiot slotu)

PALETA = {
    # drewno i kora
    "drewno": "8A5A2E", "drewno_jasne": "BE8A55", "drewno_ciemne": "5C3A1C", "kora": "7A4C26", "kora_ciemna": "4E2F15",
    "ciecie": "E0BC86", "drewno_czerwone": "8A3F22", "drewno_czerwone_ciemne": "5E2A16",
    # różdżka z patyka
    "iskra": "FFD84A", "iskra_srodek": "FFF6CC",
    # miotła
    "sloma": "DDB25E", "sloma_jasna": "F0D488", "sloma_cien": "A9843A",
    "sznur_nieb": "3F6DD0", "sznur_nieb_ciemny": "27479A", "klejnot_nieb": "3FA9FF", "klejnot_jasny": "CFF3FF",
    # wałek
    "walek": "B77B45", "walek_ciemny": "86542C", "runa": "EADFFF", "kula_fiolet": "9B4DFF", "kula_fiolet_jasna": "E2CCFF",
    # świeczka
    "wosk": "F7F0DE", "wosk_cien": "E3D7BA", "knot": "3A2A1E", "plomien": "FF9124", "plomien_srodek": "FFE56A",
    "skora": "7A4A28", "skora_ciemna": "4A2B15",
    "zloto": "E8B93A", "zloto_ciemne": "B98A22", "zloto_jasne": "F8DD7A",
    # kostur ucznia
    "krysztal": "4FB6FF", "krysztal_jasny": "D2F1FF", "poswiata_nieb": "8FDBFF",
    # proca
    "guma": "D9362C", "guma_ciemna": "A0241C", "kamien": "8E8984", "kamien_jasny": "B8B3AD",
    # wieszak
    "wieszak": "C58D52", "wieszak_ciemny": "93622F", "drut": "C9CFD9", "drut_cien": "8C94A2", "cieciwa": "F4F0E6",
    # nóż
    "stal": "C2CAD6", "stal_cien": "8D97A8", "stal_jasna": "EDF2F8", "sznurek": "D8B26A", "sznurek_cien": "A88645",
    "maslo": "F7DD72",
    # sztylet z szyszki
    "szyszka": "8C5A2C", "szyszka_ciemna": "5E3818", "szyszka_jasna": "B47A42", "lisc": "4FA83E",
    "lisc_ciemny": "2E7A2A", "lisc_jasny": "86CF5E", "krzemien": "A4AAB3", "krzemien_cien": "707783",
    # łuk tropiciela
    "pnacze": "3E8E3A", "pnacze_ciemne": "275E26", "pnacze_jasne": "74C24C", "pioro": "5DA9F2",
    "pioro_ciemne": "2C66BE", "cieciwa_nieb": "BDEBFF",
}


# --------------------------------------------------------------------------- pomocnicze
def _akc(id_, ikona_obrot):
    _i, nazwa, _k, chwyt, _ik, _z = next(b for b in BRONIE if b[0] == id_)
    zaczep = "LeftGripAttachment" if CH.RODZAJE[chwyt]["lapa"] == "lewa" else "RightGripAttachment"
    return Akcesorium(id_, nazwa, zaczep=zaczep, typ="Bron", paleta=PALETA, ikona_obrot=ikona_obrot, chwyt=chwyt)


def _kierunek(p0, p1):
    """(długość, obrót) bryły, której oś +Y biegnie od p0 do p1. W płaszczyźnie XY — sam obrót wokół Z (lokalne X
    zostaje w płaszczyźnie), w płaszczyźnie YZ — obrót (a, 0|180, 0) (lokalne X = ±X modelu)."""
    d = [p1[i] - p0[i] for i in range(3)]
    dl = math.sqrt(sum(v * v for v in d))
    if abs(d[2]) < 1e-9:
        return dl, (0.0, 0.0, -math.degrees(math.atan2(d[0], d[1])))
    a = math.degrees(math.acos(max(-1.0, min(1.0, d[1] / dl))))
    b = math.degrees(math.atan2(d[0], d[2]))
    return dl, (a, b, 0.0)


def _pret(a, nazwa, p0, p1, gr, kolor, mat="matowy", ksztalt="walec", glab=None, segm=6, staw=False, faza=0.0,
          zapas=0.0):
    """Walec (albo blok gr × dł × glab) od p0 do p1 (z zapasem `zapas` na obu końcach — bez szczelin na zgięciach);
    staw=True — kula w p1 (gładkie zgięcie gałęzi)."""
    dl, rot = _kierunek(p0, p1)
    s = [(p0[i] + p1[i]) / 2 for i in range(3)]
    if ksztalt == "walec":
        a.walec(nazwa, s, (gr, dl + 2 * zapas, gr), kolor, mat, rot=rot, segm=segm, faza=faza)
    else:
        a.blok(nazwa, s, (gr, dl + 2 * zapas, glab if glab is not None else gr), kolor, mat, rot=rot, faza=faza)
    if staw:
        a.kula(nazwa + " staw", p1, (gr, gr, gr), kolor, mat, segm=segm)


def _galaz(a, nazwa, pkt, gr0, gr1, kolor, mat="matowy", segm=6):
    """Krzywa gałąź z odcinków: grubość od gr0 do gr1, kule w zgięciach."""
    n = len(pkt) - 1
    for i in range(n):
        gr = gr0 + (gr1 - gr0) * i / max(1, n - 1)
        _pret(a, "%s %d" % (nazwa, i), pkt[i], pkt[i + 1], gr, kolor, mat, segm=segm, staw=i < n - 1)


def _grot(a, nazwa, pos, szer, h, grub, kolor, mat="metal", w_dol=False):
    """Płaski trójkąt z dwóch klinów (jak pula_wojownika._grot): podstawa w pos, wierzchołek o h wyżej (+Y; w_dol —
    niżej), szerokość w X, grubość w Z."""
    x, y, z = pos
    with a.uklad(pos=(x, y, z), obrot=(180, 0, 0) if w_dol else (0, 0, 0)):
        a.klin(nazwa, (szer / 4, h / 2, 0), (grub, h, szer / 2), kolor, mat, rot=(0, -90, 0), faza=0.0)
        a.klin(nazwa, (-szer / 4, h / 2, 0), (grub, h, szer / 2), kolor, mat, rot=(0, 90, 0), faza=0.0)


def _iskra(a, nazwa, pos, r, kolor, kolor_srodka, grub=0.035):
    """Gwiazdka-iskra: środek (kula) i cztery promienie w płaszczyźnie XY + dwa w głąb (Z), świecące."""
    a.kula(nazwa, pos, (r * 0.75, r * 0.75, r * 0.75), kolor_srodka, "swiecacy", segm=8)
    for i, kat in enumerate((0, 45, 90, 135)):
        dl = 2 * r * (1.0 if i % 2 == 0 else 0.62)
        a.blok("%s promien %d" % (nazwa, i), pos, (grub, dl, grub), kolor, "swiecacy", rot=(0, 0, kat), faza=0.0)
    a.blok(nazwa + " promien z", pos, (grub, grub, 2 * r * 0.62), kolor, "swiecacy", faza=0.0)


# --------------------------------------------------------------------------- MAG 1. Różdżka z Patyka
def rozdzka_z_patyka():
    """Krzywy brązowy patyk z sękami i dwiema gałązkami, ścięty koniec w pięści, na czubku żółta iskra. Długość jak
    atrapa różdżki z planszy chwytów (czubek ok. 1,2 nad chwytem) — dłuższa wbija się w ziemię w klipie kula_ognia."""
    a = _akc("mag_rozdzka_z_patyka", (0, 0, -40))
    pkt = [(0.02, -0.22, 0.0), (0.0, 0.06, 0.01), (-0.035, 0.34, -0.01), (0.03, 0.62, 0.01), (-0.01, 0.86, 0.0),
           (0.035, 1.04, 0.01)]
    _galaz(a, "Patyk", pkt, 0.15, 0.08, "kora")
    a.walec("Ciecie", (0.02, -0.23, 0.0), (0.12, 0.03, 0.12), "ciecie", "matowy", segm=6, faza=0.0)
    for i, (y, x) in enumerate(((-0.1, 0.01), (0.45, -0.01))):            # ciemne słoje kory
        a.walec("Kora %d" % i, (x, y, 0.0), (0.145 - 0.02 * i, 0.05, 0.145 - 0.02 * i), "kora_ciemna", "matowy",
                segm=6, faza=0.0)
    # gałązki: w lewo-w górę przy 0,4 i w prawo przy 0,74; ucięty sęk przy 0,18
    _pret(a, "Galazka 1", (-0.02, 0.4, 0.0), (0.17, 0.58, 0.03), 0.065, "kora", staw=True)
    _pret(a, "Galazka 1 koniec", (0.17, 0.58, 0.03), (0.23, 0.7, 0.03), 0.048, "kora")
    _pret(a, "Galazka 2", (0.0, 0.74, 0.0), (-0.15, 0.88, -0.02), 0.055, "kora")
    _pret(a, "Sek", (-0.03, 0.17, 0.0), (-0.12, 0.21, 0.0), 0.075, "kora_ciemna")
    a.walec("Sek ciecie", (-0.125, 0.212, 0.0), (0.055, 0.02, 0.055), "ciecie", "matowy", rot=(0, 0, 66), segm=6,
            faza=0.0)
    _iskra(a, "Iskra", (0.04, 1.11, 0.01), 0.15, "iskra", "iskra_srodek")
    for i, p in enumerate(((0.17, 1.17, 0.02), (-0.09, 1.23, 0.0))):      # drobinki iskier
        a.blok("Drobinka %d" % i, p, (0.045, 0.045, 0.045), "iskra", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return a


# --------------------------------------------------------------------------- MAG 2. Kostur z Miotły
def kostur_z_miotly():
    """Miotła do góry nogami jako kostur: krzywy jasny kij, niebieski sznur z niebieskim klejnotem, gęsty pęk słomy
    rozkładający się wachlarzem ku górze, krótkie postrzępione źdźbła pod wiązaniem."""
    a = _akc("mag_kostur_z_miotly", (0, 0, -35))
    pkt = [(0.0, -0.86, 0.0), (0.03, -0.3, 0.0), (-0.02, 0.36, 0.01), (0.02, 0.94, 0.0), (0.0, 1.3, 0.0)]
    _galaz(a, "Kij", pkt, 0.17, 0.15, "drewno_jasne")
    a.walec("Kij ciecie", (0.0, -0.87, 0.0), (0.15, 0.03, 0.15), "ciecie", "matowy", segm=6, faza=0.0)
    a.kula("Sek", (0.07, 0.6, 0.02), (0.1, 0.14, 0.1), "drewno", "matowy", segm=6)
    # krótkie źdźbła pod wiązaniem (postrzępione, w dół i na zewnątrz)
    for i in range(8):
        with a.uklad(pos=(0, 1.3, 0), obrot=(0, i * 45 + 20, 0)):
            a.blok("Zdzblo dol %d" % i, (0, -0.06, 0.12), (0.08, 0.2, 0.05), "sloma" if i % 2 else "sloma_cien",
                   "matowy", rot=(-35, 0, 0), faza=0.0)
    # wiązanie: niebieski sznur (trzy zwoje na ciemniejszym rdzeniu)
    a.walec("Wiazanie", (0, 1.44, 0), (0.3, 0.26, 0.3), "sznur_nieb_ciemny", "matowy", segm=8, faza=0.0)
    for i, y in enumerate((1.35, 1.44, 1.53)):
        a.walec("Zwoj %d" % i, (0, y, 0), (0.34, 0.06, 0.34), "sznur_nieb", "matowy", rot=(0, 0, 4 - 4 * i), segm=8,
                faza=0.0)
    # klejnot na przodzie wiązania (romb w ramce) i zwisające końce sznura
    a.blok("Klejnot ramka", (0, 1.44, 0.165), (0.2, 0.2, 0.04), "sznur_nieb_ciemny", "matowy", rot=(0, 0, 45), faza=0.0)
    a.blok("Klejnot", (0, 1.44, 0.19), (0.14, 0.14, 0.05), "klejnot_nieb", "polysk", rot=(0, 0, 45), faza=0.02)
    a.blok("Klejnot blysk", (-0.02, 1.47, 0.215), (0.04, 0.04, 0.02), "klejnot_jasny", "swiecacy", rot=(0, 0, 45),
           faza=0.0)
    for i, (x, kat) in enumerate(((0.1, 8), (0.16, -6))):
        a.blok("Koniec sznura %d" % i, (x, 1.24 - 0.03 * i, 0.12), (0.04, 0.28 - 0.04 * i, 0.04), "sznur_nieb",
               "matowy", rot=(0, 0, kat), faza=0.0)
    # pęk słomy: bryła rozszerzająca się ku górze (stos walców), na niej wieniec szerokich pasm słomy wachlarzem
    # i krótsze pasma w środku — postrzępiony, gęsty szczyt jak na ikonie
    for i, (y, sr, h) in enumerate(((1.63, 0.3, 0.14), (1.76, 0.4, 0.14), (1.9, 0.5, 0.16), (2.05, 0.58, 0.16))):
        a.walec("Pek %d" % i, (0, y, 0), (sr, h, sr), "sloma_cien" if i % 2 == 0 else "sloma", "matowy",
                rot=(0, 22 * i, 0), segm=8, faza=0.0)
    for i in range(14):
        dl = (0.62, 0.5, 0.7, 0.56)[i % 4]
        kat = (16, 26, 20, 30)[i % 4]
        with a.uklad(pos=(0, 1.95, 0), obrot=(0, i * 360.0 / 14 + 9 * (i % 3), 0)):
            with a.uklad(pos=(0, 0, 0.2), obrot=(kat, 0, 0)):
                a.blok("Pasmo %d" % i, (0, dl / 2, 0), (0.15, dl, 0.05),
                       ("sloma", "sloma_jasna", "sloma_cien")[i % 3], "matowy", faza=0.0)
    for i in range(7):
        dl = (0.55, 0.66, 0.5)[i % 3]
        with a.uklad(pos=(0, 2.0, 0), obrot=(0, i * 360.0 / 7 + 20, 0)):
            with a.uklad(pos=(0, 0, 0.08), obrot=(9, 0, 0)):
                a.blok("Pasmo srodek %d" % i, (0, dl / 2, 0), (0.13, dl, 0.05), "sloma_jasna" if i % 2 else "sloma",
                       "matowy", faza=0.0)
    return a


# --------------------------------------------------------------------------- MAG 3. Wałek Czarodziejski
R_WALKA = 0.165                                                         # promień wałka


def _runa(a, nazwa, wzor, y, kat):
    """Znak na powierzchni wałka — proste rysy, nie litery: romb, daszek, trzy kropki, dwie kreski."""
    with a.uklad(pos=(0, y, 0), obrot=(0, kat, 0)):
        z = R_WALKA - 0.004
        if wzor == "romb":
            a.blok(nazwa, (0, 0, z), (0.08, 0.08, 0.03), "runa", "swiecacy", rot=(0, 0, 45), faza=0.0)
        elif wzor == "daszek":
            for zn in (1, -1):
                a.blok(nazwa, (zn * 0.035, 0, z), (0.028, 0.11, 0.03), "runa", "swiecacy", rot=(0, 0, zn * 40),
                       faza=0.0)
        elif wzor == "kropki":
            for x, yy in ((-0.045, -0.035), (0.045, -0.035), (0.0, 0.045)):
                a.blok(nazwa, (x, yy, z), (0.04, 0.04, 0.03), "runa", "swiecacy", faza=0.0)
        else:                                                          # „kreski”: dwie równoległe ukośne
            for x in (-0.028, 0.028):
                a.blok(nazwa, (x, 0, z), (0.028, 0.12, 0.03), "runa", "swiecacy", rot=(0, 0, -25), faza=0.0)


def walek_czarodziejski():
    """Wałek do ciasta jako maczuga maga: rączka w pięści z kulką na końcu, gruby wałek z jasnymi znakami (proste
    rysy, bez liter), druga rączka, złota obrączka i fioletowa kula z poświatą. Wałek zaczyna się wyżej nad pięścią
    i jest cieńszy niż na ikonie — inaczej w chodzie ociera się o przedramię kota (--ruch)."""
    a = _akc("mag_walek_czarodziejski", (0, 0, -45))
    a.walec("Raczka", (0, 0.13, 0), (0.14, 0.68, 0.14), "drewno_jasne", "matowy", segm=8, faza=0.02)
    a.kula("Galka", (0, -0.25, 0), (0.2, 0.17, 0.2), "drewno_jasne", "matowy", segm=8)
    a.walec("Kolnierz", (0, 0.47, 0), (0.19, 0.05, 0.19), "walek_ciemny", "matowy", segm=8, faza=0.0)
    a.walec("Walek", (0, 0.88, 0), (2 * R_WALKA, 0.76, 2 * R_WALKA), "walek", "matowy", segm=8, faza=0.04)
    for i, y in enumerate((0.53, 1.23)):
        a.walec("Obrzeze %d" % i, (0, y, 0), (2 * R_WALKA, 0.04, 2 * R_WALKA), "walek_ciemny", "matowy", rot=(0, 22.5, 0),
                segm=8, faza=0.0)
    wzory = ("romb", "daszek", "kropki", "kreski")
    for i, y in enumerate((0.69, 0.89, 1.08)):
        for j, kat in enumerate((0, 120, 240)):
            _runa(a, "Runa %d%d" % (i, j), wzory[(i + j) % 4], y, kat + 60 * (i % 2))
    a.walec("Raczka gorna", (0, 1.38, 0), (0.14, 0.26, 0.14), "drewno_jasne", "matowy", segm=8, faza=0.02)
    a.walec("Obraczka", (0, 1.53, 0), (0.21, 0.07, 0.21), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Oprawa", (0, 1.58, 0), (0.17, 0.05, 0.17), "zloto_ciemne", "metal", segm=8, faza=0.0)
    a.kula("Kula", (0, 1.74, 0), (0.32, 0.32, 0.32), "kula_fiolet", "poswiata", segm=8)
    a.kula("Kula blysk", (-0.06, 1.81, 0.1), (0.09, 0.09, 0.09), "kula_fiolet_jasna", "swiecacy", segm=8)
    return a


# --------------------------------------------------------------------------- MAG 4. Różdżka ze Świeczki
def rozdzka_ze_swieczki():
    """Świeczka wetknięta w rękojeść sztyletu: owijana skórą rączka, złote okucia, biała świeca z zaciekami wosku
    spływającymi na złotą tulejkę, knot i płomyk. Długość jak różdżka (płomyk ok. 1,3 nad chwytem)."""
    a = _akc("mag_rozdzka_ze_swieczki", (0, 0, -40))
    a.kula("Glowica", (0, -0.28, 0), (0.13, 0.1, 0.13), "zloto", "metal", segm=8)
    a.walec("Glowica pierscien", (0, -0.23, 0), (0.2, 0.06, 0.2), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Rekojesc", (0, 0.0, 0), (0.15, 0.42, 0.15), "skora", "matowy", segm=8, faza=0.02)
    for i, y in enumerate((-0.13, -0.02, 0.09, 0.18)):
        a.blok("Owijka %d" % i, (0, y, 0), (0.17, 0.035, 0.17), "skora_ciemna", "matowy", rot=(0, 0, 14), faza=0.0)
    a.walec("Tulejka", (0, 0.25, 0), (0.27, 0.08, 0.27), "zloto", "metal", segm=8, faza=0.02)
    a.walec("Kielich", (0, 0.33, 0), (0.23, 0.1, 0.23), "zloto_ciemne", "metal", segm=8, faza=0.02)
    a.walec("Swieca", (0, 0.66, 0), (0.2, 0.6, 0.2), "wosk", "matowy", segm=8, faza=0.02)
    a.walec("Swieca brzeg", (0, 0.97, 0), (0.215, 0.04, 0.215), "wosk_cien", "matowy", segm=8, faza=0.0)
    # zacieki: z brzegu w dół po bokach świecy, z kroplą na końcu; wosk zalany na kielichu i kropla z tulejki
    for i, (kat, dl) in enumerate(((20, 0.3), (110, 0.18), (200, 0.38), (290, 0.24))):
        with a.uklad(obrot=(0, kat, 0)):
            a.blok("Zaciek %d" % i, (0, 0.96 - dl / 2, 0.1), (0.07, dl, 0.04), "wosk", "matowy", faza=0.0)
            a.kula("Kropla %d" % i, (0, 0.96 - dl, 0.105), (0.08, 0.09, 0.07), "wosk", "matowy", segm=6)
    for i, kat in enumerate((40, 160, 280)):
        with a.uklad(obrot=(0, kat, 0)):
            a.kula("Wosk na kielichu %d" % i, (0, 0.39, 0.1), (0.12, 0.07, 0.1), "wosk", "matowy", segm=6)
    with a.uklad(obrot=(0, 70, 0)):
        a.blok("Zaciek tulejki", (0, 0.26, 0.145), (0.05, 0.16, 0.035), "wosk", "matowy", faza=0.0)
        a.kula("Kropla tulejki", (0, 0.17, 0.148), (0.07, 0.08, 0.06), "wosk", "matowy", segm=6)
    a.blok("Knot", (0, 1.03, 0), (0.035, 0.1, 0.035), "knot", "matowy", rot=(0, 0, -8), faza=0.0)
    a.kula("Plomien", (0, 1.16, 0), (0.15, 0.28, 0.15), "plomien", "swiecacy", segm=8)
    a.kula("Plomien srodek", (0, 1.12, 0.035), (0.08, 0.15, 0.08), "plomien_srodek", "swiecacy", segm=8)
    a.kula("Plomien czubek", (0.015, 1.31, 0), (0.06, 0.11, 0.06), "plomien", "swiecacy", rot=(0, 0, -12), segm=6)
    return a


# --------------------------------------------------------------------------- MAG 5. Kostur Ucznia (zestaw)
def kostur_ucznia():
    """Smukły czerwonawo-brązowy kostur ze złotą głowicą: duży złoty sierp księżyca otwarty w górę i w bok (z przodu
    w prawy górny róg, jak na ikonie), w środku niebieski kryształ z delikatną poświatą i trzy drobne iskry
    (przedmiot zestawu)."""
    a = _akc("mag_kostur_ucznia", (0, 0, -35))
    a.walec("Drzewce", (0, 0.33, 0), (0.13, 2.36, 0.13), "drewno_czerwone", "matowy", segm=8, faza=0.02)
    a.walec("Okucie", (0, -0.86, 0), (0.16, 0.08, 0.16), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Owijka", (0, 0.0, 0), (0.165, 0.4, 0.165), "skora_ciemna", "matowy", segm=8, faza=0.02)
    for i, y in enumerate((-0.21, 0.21, 0.95)):
        a.walec("Pierscien %d" % i, (0, y, 0), (0.18, 0.04, 0.18), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Tuleja", (0, 1.53, 0), (0.19, 0.1, 0.19), "zloto", "metal", segm=8, faza=0.02)
    a.walec("Tuleja kolnierz", (0, 1.6, 0), (0.24, 0.05, 0.24), "zloto_ciemne", "metal", segm=8, faza=0.0)
    a.kula("Galka", (0, 1.68, 0), (0.18, 0.16, 0.18), "zloto", "metal", segm=8)
    # sierp: łuk z 11 odcinków wokół środka (0,03; 2,1) w płaszczyźnie XY, przerwa ku +X+Y; gruby środek, cienkie rogi
    sx, sy, r = 0.03, 2.1, 0.42
    n = 11
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        f0, f1 = math.radians(100 + 250 * t0), math.radians(100 + 250 * t1)
        p0 = (sx + r * math.cos(f0), sy + r * math.sin(f0), 0.0)
        p1 = (sx + r * math.cos(f1), sy + r * math.sin(f1), 0.0)
        tm = (t0 + t1) / 2
        gr = 0.05 + 0.13 * math.sin(math.pi * tm)
        dl, rot = _kierunek(p0, p1)
        sr = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0.0)
        a.blok("Sierp %d" % k, sr, (gr, dl + 0.035, 0.1), "zloto", "metal", rot=rot, faza=0.0)
        if 3 <= k <= 7:                                                # jaśniejszy wewnętrzny brzeg grzbietu
            wew = (sx + (sr[0] - sx) * (1 - gr / 2 / r), sy + (sr[1] - sy) * (1 - gr / 2 / r), 0.0)
            a.blok("Sierp brzeg %d" % k, wew, (0.03, dl, 0.11), "zloto_jasne", "metal", rot=rot, faza=0.0)
    # łącznik sierpa z gałką i wspornik kryształu
    a.blok("Lacznik", (-0.05, 1.79, 0.0), (0.08, 0.2, 0.08), "zloto_ciemne", "metal", rot=(0, 0, 25), faza=0.0)
    a.blok("Wspornik", (-0.1, 1.95, 0.0), (0.06, 0.24, 0.06), "zloto_ciemne", "metal", rot=(0, 0, 50), faza=0.0)
    # kryształ: romb z dwóch płaskich trójkątów (góra wyższa), poświata; blask świecący
    _grot(a, "Krysztal gora", (sx, sy, 0.0), 0.26, 0.32, 0.16, "krysztal", "poswiata")
    _grot(a, "Krysztal dol", (sx, sy, 0.0), 0.26, 0.2, 0.16, "krysztal", "poswiata", w_dol=True)
    a.blok("Krysztal blask", (sx - 0.03, sy + 0.05, 0.085), (0.045, 0.16, 0.02), "krysztal_jasny", "swiecacy",
           faza=0.0)
    for i, p in enumerate(((0.3, 2.42, 0.0), (0.4, 2.2, 0.02), (0.05, 2.5, -0.02))):
        a.blok("Iskra %d" % i, p, (0.055, 0.055, 0.055), "poswiata_nieb", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return a


# --------------------------------------------------------------------------- ZWIADOWCA 1. Proca z Gałęzi
def proca_z_galezi():
    """Proca z rozwidlonej gałęzi: kora, ścięte końce ramion (jasne słoje), czerwona guma owinięta pod końcami,
    gumki do skórzanej sakiewki z szarym kamykiem przed licem; prawe ramię grubsze (jak na ikonie)."""
    a = _akc("zwiad_proca_z_galezi", (0, 0, -30))
    a.walec("Uchwyt", (0, 0.0, 0), (0.2, 0.86, 0.2), "kora", "matowy", segm=6, faza=0.0)
    a.walec("Uchwyt ciecie", (0, -0.44, 0), (0.17, 0.03, 0.17), "ciecie", "matowy", segm=6, faza=0.0)
    for i, (y, kat) in enumerate(((-0.2, 12), (0.16, -10))):
        a.blok("Kora %d" % i, (0.0, y, 0.0), (0.215, 0.05, 0.215), "kora_ciemna", "matowy", rot=(0, 30, kat),
               faza=0.0)
    a.kula("Rozwidlenie", (0, 0.47, 0), (0.26, 0.3, 0.24), "kora", "matowy", segm=6)
    konce = []
    for zn, gr, kon in ((1, 0.16, (0.42, 1.2, 0.0)), (-1, 0.2, (-0.44, 1.24, 0.0))):
        s = "l" if zn > 0 else "p"
        p0 = (zn * 0.05, 0.5, 0.0)
        _pret(a, "Ramie " + s, p0, kon, gr, "kora", segm=6, zapas=0.02)
        dl, rot = _kierunek(p0, kon)
        u = [(kon[i] - p0[i]) / dl for i in range(3)]
        a.walec("Ramie ciecie " + s, [kon[i] + u[i] * 0.02 for i in range(3)], (gr - 0.03, 0.03, gr - 0.03),
                "ciecie", "matowy", rot=rot, segm=6, faza=0.0)
        for j, t in enumerate((0.78, 0.86)):
            a.walec("Guma owijka %s%d" % (s, j), [p0[i] + (kon[i] - p0[i]) * t for i in range(3)],
                    (gr + 0.05, 0.05, gr + 0.05), "guma", "polysk", rot=rot, segm=6, faza=0.0)
        konce.append([p0[i] + (kon[i] - p0[i]) * 0.82 for i in range(3)])
    sk = (0.0, 0.86, 0.32)                                              # skórka z kamykiem przed licem
    for i, k in enumerate(konce):
        k = (k[0], k[1], 0.1)
        _pret(a, "Guma %d" % i, k, sk, 0.05, "guma", "polysk", ksztalt="blok", glab=0.04)
    a.blok("Sakiewka", sk, (0.3, 0.17, 0.1), "skora_ciemna", "matowy", faza=0.03)
    a.blok("Sakiewka szew", (0.0, sk[1], sk[2] - 0.055), (0.32, 0.04, 0.03), "skora", "matowy", faza=0.0)
    a.kula("Kamyk", (0.0, sk[1] + 0.01, sk[2] + 0.07), (0.17, 0.15, 0.15), "kamien", "matowy", segm=6)
    a.blok("Kamyk blask", (-0.03, sk[1] + 0.05, sk[2] + 0.135), (0.05, 0.03, 0.02), "kamien_jasny", "matowy",
           faza=0.0)
    return a


# --------------------------------------------------------------------------- ZWIADOWCA 2. Łuk z Wieszaka
def luk_z_wieszaka():
    """Drewniany wieszak jako łuk: środek wieszaka w pięści, ramiona wieszaka to ramiona łuku (wygięte ku łucznikowi,
    −Z), zamiast dolnej poprzeczki cięciwa; metalowy haczyk sterczy do przodu (+Z) i zawija się w górę."""
    a = _akc("zwiad_luk_z_wieszaka", (-75, 15, 90))                # ikona: wieszak poziomo, haczyk do góry
    a.blok("Srodek", (0, 0, 0.0), (0.15, 0.36, 0.21), "wieszak", "matowy", faza=0.05)
    koniec = None
    for zn, s in ((1, "gora"), (-1, "dol")):
        # rozpiętość ±0,76: dłuższy górny koniec (±0,86 i więcej) trafiał w chodzie w głowę kota (--ruch)
        pk = [(0.0, zn * 0.12, 0.02), (0.0, zn * 0.41, -0.07), (0.0, zn * 0.69, -0.23)]
        for i in range(2):
            _pret(a, "Ramie %s %d" % (s, i), pk[i], pk[i + 1], 0.12, "wieszak", ksztalt="blok", glab=0.15,
                  faza=0.03, zapas=0.03)
        # koniec ramienia: lekko podwinięty „ramiączek” z wcięciem (tu zaczepia cięciwa)
        _pret(a, "Koniec " + s, pk[2], (0.0, zn * 0.76, -0.19), 0.12, "wieszak", ksztalt="blok", glab=0.14,
              faza=0.03, zapas=0.02)
        a.blok("Wciecie " + s, (0.0, zn * 0.71, -0.31), (0.125, 0.05, 0.05), "wieszak_ciemny", "matowy", faza=0.0)
        a.blok("Slad " + s, (0.0, zn * 0.41, -0.07), (0.125, 0.05, 0.155), "wieszak_ciemny", "matowy",
               rot=(-zn * 13, 0, 0), faza=0.0)
        koniec = (0.71, -0.31)
    a.blok("Cieciwa", (0, 0, koniec[1]), (0.035, 2 * koniec[0], 0.035), "cieciwa", "matowy", faza=0.0)
    # haczyk: szyjka do przodu z tulejką, potem zawinięcie w górę i do tyłu (otwarte w dół, jak w wieszaku)
    a.walec("Tulejka", (0, 0.0, 0.12), (0.09, 0.05, 0.09), "drut_cien", "metal", rot=(90, 0, 0), segm=8, faza=0.0)
    a.walec("Szyjka", (0, 0.0, 0.22), (0.05, 0.2, 0.05), "drut", "metal", rot=(90, 0, 0), segm=6, faza=0.0)
    sr, r = (0.0, 0.13, 0.32), 0.13
    poprz = (0.0, 0.0, 0.32)
    for k, fi in enumerate((-45, 0, 45, 90, 135, 180, 215)):
        f = math.radians(fi)
        p = (0.0, sr[1] + r * math.sin(f), sr[2] + r * math.cos(f))
        _pret(a, "Hak %d" % k, poprz, p, 0.05, "drut", "metal", staw=True)
        poprz = p
    return a


# --------------------------------------------------------------------------- ZWIADOWCA 3. Nóż do Masła
def noz_do_masla():
    """Nóż do masła: drewniany trzonek owinięty sznurkiem, złoty pierścień, płaska klinga z zaokrąglonym końcem,
    jasna krawędź — i resztka masła na płazie."""
    a = _akc("zwiad_noz_do_masla", (0, 0, -45))
    a.blok("Trzonek", (0, -0.02, 0), (0.17, 0.52, 0.13), "drewno", "matowy", faza=0.04)
    a.kula("Trzonek koniec", (0, -0.29, 0), (0.18, 0.12, 0.14), "drewno_ciemne", "matowy", segm=6)
    for i, (y, kat) in enumerate(((-0.17, 18), (-0.05, -18), (0.07, 18), (0.17, -18))):
        a.blok("Sznurek %d" % i, (0, y, 0), (0.19, 0.035, 0.15), "sznurek" if i % 2 else "sznurek_cien", "matowy",
               rot=(0, 0, kat), faza=0.0)
    a.walec("Pierscien", (0, 0.27, 0), (0.25, 0.07, 0.2), "zloto", "metal", segm=8, faza=0.0)
    a.blok("Szyjka", (0, 0.34, 0), (0.12, 0.08, 0.07), "stal_cien", "metal", faza=0.0)
    # klinga: grzbiet po −X prosty, ostrze po +X; zaokrąglony koniec = płaski walec (oś w Z)
    a.blok("Klinga", (0.0, 0.76, 0), (0.3, 0.8, 0.05), "stal", "metal", faza=0.0)
    a.walec("Klinga koniec", (0.0, 1.16, 0), (0.3, 0.05, 0.3), "stal", "metal", rot=(90, 0, 0), segm=12, faza=0.0)
    a.blok("Ostrze", (0.14, 0.77, 0), (0.035, 0.76, 0.055), "stal_jasna", "metal", faza=0.0)
    a.blok("Grzbiet", (-0.14, 0.75, 0), (0.035, 0.78, 0.06), "stal_cien", "metal", faza=0.0)
    for i, y in enumerate((0.52, 0.66)):                                # wyszczerbienia na ostrzu
        a.blok("Szczerba %d" % i, (0.155, y, 0), (0.04, 0.03, 0.06), "stal_cien", "metal", rot=(0, 0, 30), faza=0.0)
    a.kula("Maslo", (0.03, 1.02, 0.03), (0.16, 0.11, 0.035), "maslo", "polysk", rot=(0, 0, -20), segm=6)
    return a


# --------------------------------------------------------------------------- ZWIADOWCA 4. Sztylet z Szyszki
def sztylet_z_szyszki():
    """Szyszka jako głowica, drewniany krążek, rękojeść owinięta liśćmi (liście zachodzą na nasadę klingi),
    klinga z szarego krzemienia z grzbietem i odpryskami."""
    a = _akc("zwiad_sztylet_z_szyszki", (0, 0, -45))
    a.walec("Rekojesc", (0, 0.0, 0), (0.15, 0.48, 0.15), "drewno", "matowy", segm=8, faza=0.0)
    for i, (y, kat) in enumerate(((-0.15, 14), (-0.03, -16), (0.09, 14), (0.2, -12))):
        a.walec("Lisc owijka %d" % i, (0, y, 0), (0.2, 0.11, 0.2), "lisc" if i % 2 else "lisc_ciemny", "matowy",
                rot=(0, 25 * i, kat), segm=8, faza=0.0)
    for zn in (1, -1):                                                  # liście na nasadzie klingi (przód i tył)
        a.kula("Lisc nasada", (0, 0.32, zn * 0.06), (0.16, 0.3, 0.04), "lisc_jasny", "matowy", rot=(zn * 8, 0, 0),
               segm=8)
    a.walec("Krazek", (0, -0.28, 0), (0.34, 0.07, 0.34), "drewno_jasne", "matowy", segm=8, faza=0.0)
    a.walec("Krazek brzeg", (0, -0.28, 0), (0.36, 0.03, 0.36), "drewno_ciemne", "matowy", segm=8, faza=0.0)
    # szyszka: rdzeń i cztery wieńce łusek (spirala), czubek na dole
    sy = -0.53
    a.kula("Szyszka", (0, sy, 0), (0.26, 0.43, 0.26), "szyszka_ciemna", "matowy", segm=8)
    for w, (dy, r, n) in enumerate(((0.14, 0.09, 6), (0.045, 0.122, 7), (-0.055, 0.118, 7), (-0.15, 0.082, 6))):
        for k in range(n):
            with a.uklad(pos=(0, sy + dy, 0), obrot=(0, k * 360.0 / n + w * 22, 0)):
                a.blok("Luska %d%d" % (w, k), (0, 0, r), (0.11, 0.065, 0.085),
                       ("szyszka", "szyszka_jasna", "szyszka")[(k + w) % 3], "matowy", rot=(-30, 0, 0), faza=0.0)
    a.kula("Szyszka czubek", (0, sy - 0.22, 0), (0.09, 0.08, 0.09), "szyszka_ciemna", "matowy", segm=6)
    # klinga z krzemienia: korpus, ostry czubek, grzbiet, odpryski
    a.blok("Klinga", (0, 0.55, 0), (0.25, 0.5, 0.07), "krzemien", "matowy", faza=0.03)
    _grot(a, "Sztych", (0, 0.8, 0), 0.25, 0.32, 0.07, "krzemien", "matowy")
    a.blok("Grzbiet klingi", (0, 0.62, 0), (0.05, 0.62, 0.085), "krzemien_cien", "matowy", faza=0.0)
    for i, (x, y, kat) in enumerate(((0.1, 0.45, 30), (-0.1, 0.66, -25), (0.07, 0.84, 35))):
        a.blok("Odprysk %d" % i, (x, y, 0), (0.06, 0.05, 0.08), "krzemien_cien", "matowy", rot=(0, 0, kat),
               faza=0.0)
    return a


# --------------------------------------------------------------------------- ZWIADOWCA 5. Łuk Tropiciela (zestaw)
def luk_tropiciela():
    """Łuk z zielonych pnączy: dwa pnącza splecione w ramiona (wygięte ku łucznikowi, −Z), listki, zawinięte końce,
    skórzany majdan, świecąca błękitna cięciwa i niebieskie piórko na sznurku (przedmiot zestawu — delikatna
    poświata: cięciwa, czubek pióra i drobne iskry)."""
    a = _akc("zwiad_luk_tropiciela", (-75, 15, 90))                # ikona: łuk poziomo, cięciwa na dole
    a.blok("Majdan", (0, 0, 0), (0.15, 0.38, 0.18), "skora", "matowy", faza=0.04)
    for y in (-0.13, 0.13):
        a.blok("Owijka", (0, y, 0), (0.17, 0.05, 0.2), "skora_ciemna", "matowy", faza=0.0)
    odcinki = ((0.3, 14, 0.12), (0.27, 22, 0.1), (0.18, -42, 0.08))   # długość, przyrost odgięcia ku −Z, grubość
    koniec = (0.0, 0.0)
    for zn, s in ((1, "gora"), (-1, "dol")):
        y, z, kat = 0.17, 0.0, 0.0
        for i, (dl, dk, gr) in enumerate(odcinki):
            kat += dk
            r = math.radians(kat)
            p0, p1 = (0.0, zn * y, z), (0.0, zn * (y + math.cos(r) * dl), z - math.sin(r) * dl)
            _pret(a, "Pnacze %s %d" % (s, i), p0, p1, gr, "pnacze", zapas=0.03)
            # drugie, cieńsze pnącze owinięte wokół (na przemian po bokach) — splot
            q0 = (0.04 * (1 if i % 2 else -1), p0[1], p0[2] + 0.02)
            q1 = (0.04 * (-1 if i % 2 else 1), p1[1], p1[2] + 0.02)
            _pret(a, "Splot %s %d" % (s, i), q0, q1, gr * 0.55, "pnacze_ciemne")
            if i < 2:                                                  # listek na zewnątrz ramienia
                xs = 0.09 if (i + (zn > 0)) % 2 else -0.09
                sr = [(p0[j] + p1[j]) / 2 for j in range(3)]
                a.kula("Listek %s %d" % (s, i), (xs, sr[1], sr[2]), (0.06, 0.2, 0.11), "pnacze_jasne", "matowy",
                       rot=(0, 0, -60 if xs > 0 else 60), segm=6)
            y, z = y + math.cos(r) * dl, z - math.sin(r) * dl
        # zawinięty koniec pnącza (mały lok)
        _pret(a, "Lok %s 0" % s, (0.0, zn * y, z), (0.0, zn * (y + 0.06), z + 0.08), 0.05, "pnacze_jasne", staw=True)
        _pret(a, "Lok %s 1" % s, (0.0, zn * (y + 0.06), z + 0.08), (0.0, zn * (y - 0.02), z + 0.12), 0.045,
              "pnacze_jasne")
        koniec = (y, z)
    a.blok("Cieciwa", (0, 0, koniec[1] - 0.02), (0.03, 2 * koniec[0], 0.03), "cieciwa_nieb", "poswiata", faza=0.0)
    # piórko na sznurku pod górnym końcem (na zewnątrz łuku, +X)
    yk, zk = koniec[0] - 0.1, koniec[1] + 0.02
    a.blok("Sznurek piora", (0.09, yk - 0.06, zk), (0.025, 0.14, 0.025), "sznurek", "matowy", rot=(0, 0, 25),
           faza=0.0)
    with a.uklad(pos=(0.13, yk - 0.13, zk), obrot=(0, 0, 18)):
        a.kula("Pioro", (0, -0.18, 0), (0.05, 0.38, 0.15), "pioro", "matowy", segm=6)
        a.blok("Pioro stosina", (0, -0.17, 0), (0.06, 0.4, 0.025), "pioro_ciemne", "matowy", faza=0.0)
        a.kula("Pioro czubek", (0, -0.34, 0), (0.045, 0.1, 0.09), "poswiata_nieb", "swiecacy", segm=6)
    for i, p in enumerate(((0.0, 0.5, -0.2), (0.0, -0.55, -0.22), (0.1, 0.05, -0.12))):
        a.blok("Iskra %d" % i, p, (0.045, 0.045, 0.045), "poswiata_nieb", "swiecacy", rot=(45, 0, 45), faza=0.0)
    return a


BUDOWNICZE = {"mag_rozdzka_z_patyka": rozdzka_z_patyka, "mag_kostur_z_miotly": kostur_z_miotly,
              "mag_walek_czarodziejski": walek_czarodziejski, "mag_rozdzka_ze_swieczki": rozdzka_ze_swieczki,
              "mag_kostur_ucznia": kostur_ucznia, "zwiad_proca_z_galezi": proca_z_galezi,
              "zwiad_luk_z_wieszaka": luk_z_wieszaka, "zwiad_noz_do_masla": noz_do_masla,
              "zwiad_sztylet_z_szyszki": sztylet_z_szyszki, "zwiad_luk_tropiciela": luk_tropiciela}


# --------------------------------------------------------------------------- API
def akcesoria():
    """Dziesięć broni (świeże obiekty Akcesorium) w kolejności BRONIE."""
    return [BUDOWNICZE[b[0]]() for b in BRONIE]


def przedmiot(id_, akc=None):
    """Przedmiot ekwipunku (ekwipunek.Przedmiot): jedna część na zaczepie dłoni; cialo w danych = „dowolne”."""
    _i, nazwa, klasa, _ch, _ik, zestaw = next(b for b in BRONIE if b[0] == id_)
    prz = Przedmiot(id_, nazwa, "Weapon", "Weapons", PW.MIARA, cialo=PW.KM.CIALO_TYP, klasy=(klasa,),
                    zestaw=ZESTAWY[klasa] if zestaw else None, paleta=PALETA)
    prz.na_zaczepie(akc or BUDOWNICZE[id_]())
    return prz


def przedmioty():
    return [przedmiot(b[0]) for b in BRONIE]


def postac(id_, akc=None, klipy=("idle",)):
    """Goły kot (ciało Kota-Maga, jak w puli wojownika) z jedną bronią — korekty kota według rodzaju chwytu."""
    p = ubierz(PW.cialo(), [przedmiot(id_, akc)], id="na_kocie_" + id_,
               nazwa="Kot — %s" % next(b[1] for b in BRONIE if b[0] == id_), korekty=KOREKTY_CHWYTU)
    if klipy:
        p.klipy = [k for k in p.klipy if k.nazwa in klipy]
        p.ustaw_poze_renderu("idle", 0)
    return p


def zbuduj():
    """Dla przebuduj.py: dziesięć kotów z bronią (tylko plansze) i dziesięć broni (GLB/FBX, ikony)."""
    akc = akcesoria()
    return [postac(a.id, a) for a in akc] + akc


def ikony_roblox():
    """{id modelu: rbxassetid ikony} z ikony_broni.json (po wgraniu ikon)."""
    if not os.path.isfile(IKONY_JSON):
        return {}
    with open(IKONY_JSON, encoding="utf-8") as f:
        d = json.load(f)
    wynik = {}
    for klucz, e in (d.get("ikony") or {}).items():
        if e.get("model") and e.get("obraz"):
            wynik[e["model"]] = {"klucz": klucz, "obraz": "rbxassetid://" + e["obraz"],
                                 "moderacja": e.get("moderacja")}
    return wynik


def glb_dane(sciezka):
    """Skrzynka (min, max) i liczba trójkątów siatki z pliku GLB (bez Blendera)."""
    with open(sciezka, "rb") as f:
        b = f.read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    mn, mx, tr = [9e9] * 3, [-9e9] * 3, 0
    for m in j["meshes"]:
        for pr in m["primitives"]:
            acc = j["accessors"][pr["attributes"]["POSITION"]]
            mn = [min(mn[i], acc["min"][i]) for i in range(3)]
            mx = [max(mx[i], acc["max"][i]) for i in range(3)]
            if "indices" in pr:
                tr += j["accessors"][pr["indices"]]["count"] // 3
    return mn, mx, tr


def ekwipunek_json(cel=None):
    """Dane broni dla gry (format jak ekwipunek.json puli wojownika, EKWIPUNEK.md pkt 5 i 15): każda broń ma jedną
    część na zaczepie dłoni z korektą kota według rodzaju chwytu (zaczep, pos, rot), korektę upadku, ikonę w Roblox,
    pliki modelu i attachment_pos (minus środek skrzynki siatki od punktu chwytu — Attachment w Handle)."""
    ik = ikony_roblox()
    zasoby = {}
    if os.path.isfile(ZASOBY_JSON):
        with open(ZASOBY_JSON, encoding="utf-8") as f:
            zasoby = json.load(f)
    opisy = []
    for prz in przedmioty():
        o = prz.opis(KOREKTY_CHWYTU)
        akc = prz.segmenty[0]["akc"]
        cz = o["czesci"][0]
        cz["zaczep_standardowy"] = akc.zaczep          # człowiek / Accessory w Roblox (RightGrip / LeftGrip)
        kor = PW.korekta_upadku(akc)
        cz["korekta_upadku"] = None if kor is None else {k: kor[k] for k in ("grupa", "od_klatki", "do_klatki", "pos",
                                                                              "rot")}
        for kon in ("fbx", "glb"):
            cz[kon] = "wynik/%s/przedmioty/%s.%s" % (ID, akc.id, kon)
        glb = os.path.join(cel or WYNIK, "przedmioty", akc.id + ".glb")
        if os.path.isfile(glb):
            mn, mx, tr = glb_dane(glb)
            cz["trojkaty"] = tr
            cz["attachment_pos"] = [round(-(mn[i] + mx[i]) / 2, 4) + 0.0 for i in range(3)]
            cz["wymiary"] = [round(mx[i] - mn[i], 3) for i in range(3)]
        o["plik_ikony"] = "wynik/%s/ikony/%s_ikona.png" % (ID, akc.id)
        if akc.id in ik:
            o["ikona"] = ik[akc.id]["obraz"]
            o["ikona_klucz"] = ik[akc.id]["klucz"]
        z = zasoby.get(akc.id) or {}
        if z.get("asset"):                 # po bronie_klas_roblox.py: zasób Model i akcesorium w Studio
            o["roblox"] = {"model": "rbxassetid://" + z["asset"], "moderacja": z.get("moderacja"),
                           "akcesorium": z.get("kontener"), "zaczep_w_handle": z.get("zaczep"),
                           "obrot_importu": (zasoby.get("_import") or {}).get("obrot")}
        opisy.append(o)
    return {"modul": ID, "pula": "Lv 1-10", "klasy": ["mag", "zwiadowca"], "status": "propozycja",
            "korekty_chwytu": {k: {"zaczep": zz, "pos": list(pos), "rot": list(ob)}
                               for k, (zz, pos, ob) in KOREKTY_CHWYTU.items()},
            "rodzaje_chwytu": CH.dla_gry(KOREKTY_CHWYTU), "upadek": CH.upadek_dla_gry(), "przedmioty": opisy}


# --------------------------------------------------------------------------- plansze (po przebudowie, bez Blendera)
def _czcionki():
    from PIL import ImageFont
    try:
        return (ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 19),
                ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26))
    except OSError:
        f = ImageFont.load_default()
        return f, f


def plansza_porownania(cel_png, wynik=None, szer=2000):
    """Siatka 5 × 2: w każdej kratce ikona z Higgsfield → render modelu (ikona z Blendera), podpis pod spodem."""
    from PIL import Image, ImageDraw
    wynik = wynik or WYNIK
    fn, fb = _czcionki()
    kol, K = 5, szer // 5
    B = (K - 46) // 2                                                   # bok jednego obrazka w kratce
    H = B + 70
    im = Image.new("RGB", (kol * K, 2 * H + 60), "#1d1729")
    dr = ImageDraw.Draw(im)
    dr.text((14, 14), "Bronie Maga i Zwiadowcy — ikona (Higgsfield) → model 3D (Blender), pula Lv 1–10, propozycja",
            font=fb, fill="#ffffff")
    for i, (id_, nazwa, klasa, chwyt, klucz, zestaw) in enumerate(BRONIE):
        x0, y0 = (i % kol) * K, 56 + (i // kol) * H
        dr.rounded_rectangle((x0 + 6, y0 + 4, x0 + K - 6, y0 + H - 6), radius=12, fill="#2c2540")
        for j, p in enumerate((os.path.join(REPO, "assets", "processed", klucz + ".png"),
                               os.path.join(wynik, "ikony", id_ + "_ikona.png"))):
            if not os.path.isfile(p):
                continue
            ob = Image.open(p).convert("RGBA")
            ob.thumbnail((B, B), Image.LANCZOS)
            px = x0 + 12 + j * (B + 22)
            im.paste(ob, (px + (B - ob.width) // 2, y0 + 10 + (B - ob.height) // 2), ob)
        dr.text((x0 + 12 + B + 2, y0 + 10 + B // 2 - 14), "→", font=fb, fill="#d9d0ee")
        t = "%s%s" % (nazwa, " (zestaw)" if zestaw else "")
        dr.text((x0 + (K - dr.textlength(t, font=fn)) // 2, y0 + B + 16), t, font=fn, fill="#ffffff")
        t2 = "%s · chwyt „%s”" % (klasa, chwyt)
        dr.text((x0 + (K - dr.textlength(t2, font=fn)) // 2, y0 + B + 38), t2, font=fn, fill="#b8aed6")
    im.save(cel_png)
    return cel_png


def plansza_na_kocie(cel, wynik=None, szer=2000):
    """Siatka 5 × 2 kadrów 3/4 (lewa górna ćwiartka planszy) kota z każdą bronią w spoczynku."""
    from PIL import Image, ImageDraw
    wynik = wynik or WYNIK
    fn, fb = _czcionki()
    kol, K = 5, szer // 5
    H = K + 40
    im = Image.new("RGB", (kol * K, 2 * H + 60), "#1d1729")
    dr = ImageDraw.Draw(im)
    dr.text((14, 14), "Bronie Maga i Zwiadowcy na gołym kocie (spoczynek, korekta chwytu według rodzaju)", font=fb,
            fill="#ffffff")
    for i, (id_, nazwa, _k, chwyt, _ik, _z) in enumerate(BRONIE):
        p = os.path.join(wynik, "na_kocie_%s_plansza.jpg" % id_)
        if not os.path.isfile(p):
            continue
        ob = Image.open(p).convert("RGB")
        ob = ob.crop((0, 0, ob.width // 2, ob.height // 2))
        ob.thumbnail((K - 12, K - 12), Image.LANCZOS)
        x0, y0 = (i % kol) * K, 56 + (i // kol) * H
        im.paste(ob, (x0 + (K - ob.width) // 2, y0))
        t = "%s · „%s”" % (nazwa, chwyt)
        dr.text((x0 + (K - dr.textlength(t, font=fn)) // 2, y0 + K - 6), t, font=fn, fill="#ffffff")
    im.save(cel, quality=90)
    return cel


def po_przebudowie(cel):
    """przebuduj.py: ekwipunek.json (z attachment_pos z GLB) i dwie plansze do oceny w wynik/bronie_klas/."""
    with open(os.path.join(cel, "ekwipunek.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(ekwipunek_json(cel), f, ensure_ascii=False, indent=1)
    plansza_porownania(os.path.join(cel, ID + "_porownanie.png"), cel)
    plansza_na_kocie(os.path.join(cel, ID + "_na_kocie.jpg"), cel)
    return ["ekwipunek.json", ID + "_porownanie.png", ID + "_na_kocie.jpg"]


SLABOSCI = [
    "Propozycja: nazwy z notatki puli Lv 1–10 (niekanoniczne); wygląd według ikon Higgsfield z 27.11.2026.",
    "Rodzaje chwytu wybrane przy budowie (chwyty.py): różdżki „rozdzka”, kostury „drzewce”, Wałek Czarodziejski, "
    "Nóż do Masła i Sztylet z Szyszki „miecz” (broń jednoręczna), proca „proca” w prawej łapie, łuki „luk” w lewej "
    "łapie (kontrakt EKWIPUNEK.md pkt 15). Łuk w slocie Weapon trzymany w LEWEJ łapie zostawia prawą pustą — "
    "do decyzji przy integracji.",
    "Korekty kota liczone tabelą chwyty.py dla atrap i broni puli wojownika; dla tych broni sprawdza je "
    "`bronie_klas.py --ruch` (całe ciało i ziemia, klatka po klatce). Klipy kota są pisane pod kostur: w klipach "
    "walki lewa łapa idzie przed tułów (łuk wchodzi w ciało), a pod pięścią prawej łapy przy barku to, co wystaje "
    "(głowica, szyszka, stopka) wchodzi w ramię — jak w puli wojownika.",
    "Poświata przedmiotów zestawu to materiał (emisja) kryształu, cięciwy i iskier; w Roblox emisja z GLB może nie "
    "przejść — w Studio przedmiot zestawu dostaje słabe PointLight.",
    "Runy na wałku to proste rysy (romb, daszek, kropki, kreski) — bez liter, mimo że ikona ma znaki podobne do liter.",
]


# --------------------------------------------------------------------------- CLI
def _wymiary(a):
    from swiat.postacie.biblioteka.postac import pudelko
    pud = pudelko(a.czesci_w())
    return pud


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--ekwipunek" in sys.argv:          # ekwipunek.json od nowa (np. po wgraniu do Roblox), bez Blendera
        with open(os.path.join(WYNIK, "ekwipunek.json"), "w", encoding="utf-8", newline="\n") as _f:
            json.dump(ekwipunek_json(WYNIK), _f, ensure_ascii=False, indent=1)
        print(os.path.relpath(os.path.join(WYNIK, "ekwipunek.json"), REPO))
        raise SystemExit(0)
    if "--plansza" in sys.argv:
        _cel = sys.argv[sys.argv.index("--plansza") + 1]
        print(plansza_porownania(_cel))
        raise SystemExit(0)
    if "--ruch" in sys.argv:
        _zle = 0
        print("RUCH — broń względem całego gołego kota i ziemi, klatka po klatce (pula_wojownika.bron_w_ruchu); "
              "kryterium chodu i spoczynku: zapas ≥ %.2f studa (łuki w lewej łapie — informacyjnie, znana usterka "
              "klipu: lewa łapa przy ogonie)" % PW.ZAPAS_RUCHU)
        for _id_, _n, _k, _ch, _ik, _z in BRONIE:
            _p = postac(_id_, klipy=None)
            _dlon = "LeftHand" if CH.RODZAJE[_ch]["lapa"] == "lewa" else "RightHand"
            _w = PW.bron_w_ruchu(_p, _id_, _dlon)
            PW.wypisz_ruch("%s (%s, chwyt „%s”)" % (_n, _id_, _ch), _w)
            if _dlon == "RightHand":
                _zle += sum(1 for _kl in PW.KLIPY_RUCHU if min(_w[_kl]["cialo"][0], _w[_kl]["ziemia"][0])
                            < PW.ZAPAS_RUCHU)
        print("\nUPADEK — broń z korektą upadku (chwyty.py) względem ziemi co pół klatki, próg %.2f" % CH.PROG_UPADKU)
        _zle_up = 0
        for _id_, _n, _k, _ch, _ik, _z in BRONIE:
            _p = postac(_id_, klipy=None)
            _zle_up += PW.wypisz_upadek(_n, PW.upadek_na_postaci(_p))
        print("broń prawej łapy: klipów chodu/spoczynku poniżej zapasu %.2f: %d; upadek pod progiem: %d"
              % (PW.ZAPAS_RUCHU, _zle, _zle_up))
        raise SystemExit(1 if _zle or _zle_up else 0)
    from swiat.postacie.biblioteka.roblox_klocki import rozloz  # noqa: E402
    print("%-26s %-22s %-9s %-8s %5s %6s  %s" % ("id", "nazwa", "klasa", "chwyt", "bryły", "części", "skrzynka "
                                                  "(min … max, studa)"))
    for _a, (_id_, _n, _k, _ch, _ik, _z) in zip(akcesoria(), BRONIE):
        _pud = _wymiary(_a)
        _b, _u = _a.sprawdz()
        print("%-26s %-22s %-9s %-8s %5d %6d  %s … %s%s" % (
            _id_, _n, _k, _ch, len(_a.czesci), sum(len(rozloz(c)) for c in _a.czesci),
            [round(v, 2) for v in _pud[0]], [round(v, 2) for v in _pud[1]],
            ("  BŁĘDY: %s" % _b) if _b else ""))
        for _x in _u[:3]:
            print("    uwaga:", _x)
