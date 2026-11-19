# -*- coding: utf-8 -*-
"""STOPNIE EKWIPUNKU — przedmioty do kupienia dla trzech klas (D-106; kontrakt swiat/postacie/EKWIPUNEK.md).

Status: propozycja (własne projekty, do oceny). Trzy stopnie odpowiadają krainom: las (skóra, drewno, futro, poroże),
Bagno (łuski, kość, mosiądz), Dżungla (złoto, jadeit, pióra). Stopień startowy to dzisiejsze przedmioty bohaterów
(rycerz.py, zwiadowca.py, kot_mag.py) — ten moduł ich NIE zmienia i niczego do nich nie dopisuje.

Jak powstaje przedmiot stopnia:
  - części zbroi na kościach: dzisiejsze bryły segmentu (te same liczby, te same warstwy i powłoki) przemalowane na
    materiały krainy, bez wybranych brył (np. grzebień hełmu, tabard) i z dołożonymi bryłami zmieniającymi sylwetkę
    (poroże, kościany grzebień, pióropusz, kolce i skrzydła naramienników, futrzany kołnierz, pektorał…);
  - broń, tarcza i nakrycie głowy kota: nowe bryły w tej samej ramce chwytu co dzisiejsze (rękojeść w (0,0,0),
    ostrze w +Y), więc siedzą w dłoni tak samo i idą za tymi samymi klipami.
Id: <bohater>_<stopień>_<rzecz>, np. rycerz_las_helm, kot_mag_dzungla_kostur; segment: <id>_<skrót kości>.

    python -B swiat/postacie/stopnie.py            # lista przedmiotów (bez Blendera)
Plansze, ikony i modele GLB: moduły stopnie_wojownik.py, stopnie_zwiadowca.py, stopnie_mag.py przez przebuduj.py.
Katalog z cenami i statystykami: sklep_katalog.py -> sklep_przedmioty.json; opis: SKLEP_PRZEDMIOTY.md.
"""
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import kot_mag, rycerz, zwiadowca  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium, kolor_hex  # noqa: E402
from swiat.postacie.ekwipunek import Przedmiot, ubierz  # noqa: E402

STOPNIE = ("las", "bagno", "dzungla")
WSZYSTKIE_STOPNIE = ("start",) + STOPNIE
NAZWY_STOPNI = {"start": "startowy", "las": "leśny", "bagno": "bagienny", "dzungla": "Dżungli"}
MODULY = {"wojownik": rycerz, "zwiadowca": zwiadowca, "mag": kot_mag}
BOHATER = {"wojownik": "rycerz", "zwiadowca": "zwiadowca", "mag": "kot_mag"}
# komplet startowy klasy (dzisiejsze przedmioty, kolejność zakładania jak w module bohatera); Wojownik z tarczą
KOMPLET_START = {"wojownik": rycerz.KANON + ("rycerz_tarcza",), "zwiadowca": zwiadowca.KANON, "mag": kot_mag.KANON}

# te same nazwy kolorów w każdym stopniu: główny materiał (trzy tony), tkanina (trzy tony), ozdoba, akcent, pióra, blask
PALETY = {
    "las": {"glowny": "8E5A32", "glowny_cien": "6B4124", "glowny_ciemny": "4A2C17",          # utwardzana skóra
            "tkanina": "4F9A3C", "tkanina_ciemna": "2F6B2A", "tkanina_jasna": "86C95C",       # liść
            "ozdoba": "C9A066", "ozdoba_ciemna": "8A6A3A",                                    # jasne i ciemne drewno
            "akcent": "E6D8B8", "akcent_cien": "BFAE86",                                      # poroże, futro
            "piora1": "D9642B", "piora2": "F2C230", "blask": "A6F06A",
            "zelazo": "9AA0A6", "zelazo_cien": "6E747B"},
    "bagno": {"glowny": "3F8A7C", "glowny_cien": "2C665C", "glowny_ciemny": "1D4640",        # łuska
              "tkanina": "4A4460", "tkanina_ciemna": "2F2B40", "tkanina_jasna": "7A6FA0",     # mroczne sukno
              "ozdoba": "C9A23A", "ozdoba_ciemna": "8C6D1F",                                  # mosiądz
              "akcent": "E9E0C6", "akcent_cien": "B9AD8D",                                    # kość
              "piora1": "9BD14A", "piora2": "6FB3A5", "blask": "B6FF5A",
              "zelazo": "3F8A7C", "zelazo_cien": "2C665C"},
    "dzungla": {"glowny": "F0BE2E", "glowny_cien": "C99416", "glowny_ciemny": "8F6508",      # złoto
                "tkanina": "2FB57C", "tkanina_ciemna": "1B7D58", "tkanina_jasna": "8FE8BC",   # jadeit
                "ozdoba": "2FB57C", "ozdoba_ciemna": "1B7D58",
                "akcent": "E23B2E", "akcent_cien": "A8241B",                                  # czerwone pióra
                "piora1": "1FB6C9", "piora2": "FF8A1E", "blask": "FFE86B",
                "zelazo": "F0BE2E", "zelazo_cien": "C99416"},
}
PIORA = ("akcent", "piora1", "piora2")

# przemalowanie dzisiejszych brył: nazwa koloru bohatera -> nazwa koloru stopnia (klasa, stopień)
MAPY = {
    ("wojownik", "las"): {"stal": "glowny", "stal_cien": "glowny_cien", "stal_ciemna": "glowny_ciemny",
                          "niebieski": "tkanina", "niebieski_ciemny": "tkanina_ciemna", "zloto": "ozdoba"},
    ("wojownik", "bagno"): {"stal": "glowny", "stal_cien": "glowny_cien", "stal_ciemna": "glowny_ciemny",
                            "niebieski": "tkanina", "niebieski_ciemny": "tkanina_ciemna", "zloto": "ozdoba"},
    ("wojownik", "dzungla"): {"stal": "glowny", "stal_cien": "glowny_cien", "stal_ciemna": "tkanina_ciemna",
                              "niebieski": "tkanina", "niebieski_ciemny": "tkanina_ciemna", "zloto": "tkanina_jasna",
                              "brazowy": "glowny_ciemny"},
    ("zwiadowca", "las"): {"lisc": "glowny", "lisc_ciemny": "glowny_ciemny", "skorzany": "tkanina_ciemna",
                           "skorzany_ciemny": "glowny_ciemny", "skorzany_jasny": "ozdoba", "akcent": "tkanina_jasna",
                           "drewno": "ozdoba_ciemna"},
    ("zwiadowca", "bagno"): {"lisc": "tkanina", "lisc_ciemny": "tkanina_ciemna", "skorzany": "glowny",
                             "skorzany_ciemny": "glowny_ciemny", "skorzany_jasny": "ozdoba", "akcent": "akcent",
                             "drewno": "akcent_cien"},
    ("zwiadowca", "dzungla"): {"lisc": "tkanina", "lisc_ciemny": "tkanina_ciemna", "skorzany": "glowny",
                               "skorzany_ciemny": "glowny_cien", "skorzany_jasny": "tkanina_jasna", "akcent": "akcent",
                               "drewno": "glowny"},
    ("mag", "las"): {"szata": "glowny", "szata_ciemna": "tkanina_ciemna", "szata_jasna": "tkanina_jasna",
                     "wstazka": "ozdoba", "zloto": "ozdoba", "krysztal": "blask"},
    ("mag", "bagno"): {"szata": "glowny", "szata_ciemna": "glowny_ciemny", "szata_jasna": "glowny_cien",
                       "wstazka": "ozdoba", "zloto": "ozdoba", "krysztal": "blask"},
    ("mag", "dzungla"): {"szata": "tkanina", "szata_ciemna": "tkanina_ciemna", "szata_jasna": "tkanina_jasna",
                         "wstazka": "glowny", "zloto": "glowny", "krysztal": "akcent"},
}
# stopień lasu to skóra i drewno: nic nie błyszczy jak stal
MATERIALY = {"las": {"metal": "matowy", "polysk": "matowy"}, "bagno": {}, "dzungla": {}}

# nazwa i krótki opis wyglądu każdego przedmiotu: (klasa, stopień) -> {rzecz: (nazwa, opis)}
OPISY = {
    ("wojownik", "las"): {
        "helm": ("Hełm Leśnego Strażnika", "skórzany hełm z jasnym porożem po bokach i futrem na karku"),
        "zbroja": ("Zbroja Leśnego Strażnika", "utwardzana skóra, futrzany kołnierz, naramienniki z płatów kory, "
                                               "zielony tabard z drewnianą lamówką"),
        "nogawice": ("Nogawice Leśnego Strażnika", "skórzane uda z ciemną płytą, część zbroi"),
        "pas": ("Pas Leśnika z Sakiewką", "szeroki ciemny pas z drewnianą klamrą i sakiewką przy biodrze"),
        "rekawice": ("Rękawice z Futrem", "skórzane rękawice z futrzanym mankietem"),
        "buty": ("Buty Leśnika z Futrem", "skórzane buty z futrzanym wywinięciem pod kolanem"),
        "miecz": ("Liściasty Miecz Gaju", "żelazna klinga w kształcie liścia z zieloną żyłką, jelec z gałązek"),
        "tarcza": ("Dębowa Tarcza", "okrągła tarcza z jasnych desek z ciemną obręczą, żelaznym umbem i listkiem"),
    },
    ("wojownik", "bagno"): {
        "helm": ("Hełm Topielca", "łuskowy hełm z kościanym grzebieniem i dwoma kłami przy policzkach"),
        "zbroja": ("Łuskowa Zbroja Topieli", "napierśnik z rombów łusek, kościane żebra i mostek, po trzy kolce na "
                                              "naramiennikach, mosiężne okucia"),
        "nogawice": ("Łuskowe Nogawice Topieli", "łuskowe uda z ciemniejszą płytą, część zbroi"),
        "pas": ("Pas z Kłami", "ciemny pas z mosiężną klamrą i dwoma wiszącymi kłami"),
        "rekawice": ("Kolczaste Rękawice Topieli", "łuskowe rękawice z kościanymi kolcami na kostkach"),
        "buty": ("Łuskowe Buty z Kolcem", "łuskowe buty z kościanym kolcem na kolanie"),
        "miecz": ("Kościany Tasak Topieli", "szeroki tasak rozszerzający się ku górze, zęby z kości na ostrzu, "
                                              "mosiężny jelec"),
        "tarcza": ("Tarcza ze Skorupy", "owalna skorupa z płytkami, mosiężny brzeg, cztery kościane kolce i guz"),
    },
    ("wojownik", "dzungla"): {
        "helm": ("Hełm Słońca z Pióropuszem", "złoty hełm z wachlarzem pięciu piór i słonecznym dyskiem na czole"),
        "zbroja": ("Złota Zbroja Słońca", "złoty napierśnik z jadeitowym dyskiem i promieniami, uniesione skrzydła "
                                           "naramienników, trzy pióra na plecach"),
        "nogawice": ("Złote Nogawice Słońca", "złote uda z płytą, część zbroi"),
        "pas": ("Pas z Jadeitowym Dyskiem", "ciemnozłoty pas z jadeitowym dyskiem i piórami przy biodrach"),
        "rekawice": ("Rękawice z Jadeitem", "złote rękawice z jadeitową bransoletą"),
        "buty": ("Złote Buty z Jadeitem", "złote buty z jadeitowym dyskiem na kolanie i opaską z piór przy kostce"),
        "miecz": ("Zębaty Miecz Słońca", "płaska złota klinga z jadeitowymi zębami po obu stronach, dysk słońca "
                                          "zamiast jelca, pióra przy głowicy"),
        "tarcza": ("Tarcza Słońca", "złoty dysk z jadeitowym pierścieniem, promienie u góry i pióra u dołu"),
    },
    ("zwiadowca", "las"): {
        "kaptur": ("Kaptur Tropiciela z Futrem", "brązowy skórzany kaptur z rudym piórem i futrem na barkach"),
        "kurtka": ("Kirys Tropiciela", "ciemnozielony kirys na brązowej tunice, drewniane płytki na ramionach, "
                                       "jasnozielona chusta"),
        "spodnie": ("Spodnie Tropiciela", "ciemnobrązowe spodnie, część kirysu"),
        "pas": ("Pas Tropiciela", "ciemny pas z drewnianą klamrą i sakwą"),
        "rekawice": ("Rękawice Tropiciela", "rękawice bez palców z futrzanym mankietem"),
        "buty": ("Buty Tropiciela", "buty z futrzanym wywinięciem"),
        "sztylet": ("Nóż Myśliwski", "szeroki nóż ze ściętym czubkiem i ząbkami na grzbiecie, rękojeść z poroża"),
        "luk": ("Łuk Gaju z Kołczanem", "ciemny drewniany łuk z listkami na końcach, zielone lotki"),
    },
    ("zwiadowca", "bagno"): {
        "kaptur": ("Kaptur z Wężowej Łuski", "ciemny kaptur z kościanymi kolcami na grzbiecie, kłami nad czołem "
                                              "i kolcami na barkach"),
        "kurtka": ("Łuskowy Kirys Topieli", "łuskowy kirys z rombami łusek, kościane kolce na ramionach, kościana "
                                             "chusta"),
        "spodnie": ("Spodnie z Wężowej Skóry", "ciemne spodnie, część kirysu"),
        "pas": ("Pas z Mosiężną Klamrą", "łuskowy pas z mosiężną klamrą i sakwą"),
        "rekawice": ("Rękawice z Kolcami", "rękawice bez palców z kościanymi kolcami na kostkach"),
        "buty": ("Buty Brodzące", "łuskowe buty z mosiężnym wywinięciem i kolcem na kolanie"),
        "sztylet": ("Kieł Topielca", "zakrzywiony kościany kieł na mosiężnym jelcu"),
        "luk": ("Kościany Łuk z Kołczanem", "łuk z kości z rogowymi końcami, kościane lotki"),
    },
    ("zwiadowca", "dzungla"): {
        "kaptur": ("Pióropusz Jaguara", "jadeitowy kaptur bez szpica, złota opaska z klejnotem i wachlarz pięciu "
                                         "piór z tyłu głowy"),
        "kurtka": ("Kirys ze Złotym Pektorałem", "złoty kirys na jadeitowej tunice, szeroki pektorał z klejnotem, "
                                                  "pióra na ramionach"),
        "spodnie": ("Jadeitowe Spodnie", "ciemnojadeitowe spodnie, część kirysu"),
        "pas": ("Pas Jaguara", "złoty pas z jadeitową klamrą i sakwą"),
        "rekawice": ("Rękawice z Jadeitową Bransoletą", "rękawice bez palców z jadeitową bransoletą"),
        "buty": ("Złote Buty Jaguara", "złote buty z jadeitowym dyskiem na kolanie i piórami przy kostce"),
        "sztylet": ("Jadeitowy Sierp", "szerokie jadeitowe ostrze z zagiętym czubkiem, złote skrzydełka jelca, "
                                        "czerwony klejnot w głowicy"),
        "luk": ("Łuk Słońca z Kołczanem", "złoty łuk z piórami na końcach, czerwone lotki"),
    },
    ("mag", "las"): {
        "kapelusz": ("Kapelusz Zielarza", "szeroki skórzany kapelusz z płaską główką, zieloną wstążką, grzybkiem "
                                          "na rondzie i piórem"),
        "szata": ("Szata z Liści", "brązowa szata z zielonymi obszyciami i peleryną z liści na ramionach"),
        "pas": ("Szarfa Zielarza", "zielona szarfa z drewnianą klamrą i sakiewką"),
        "kostur": ("Kostur z Korzenia", "ciemny kostur zakręcony u góry jak pastorał, w zakręcie świecący kryształ"),
    },
    ("mag", "bagno"): {
        "kapelusz": ("Rogaty Czepiec Szamana", "łuskowy czepiec bez ronda z dwoma rogami, kościaną czaszką nad "
                                                "czołem i grzebieniem"),
        "szata": ("Szata Szamana Topieli", "łuskowa szata z kapturem, naramienniki z kolcami i naszyjnik z kłów"),
        "pas": ("Szarfa z Kłem", "ciemna szarfa z mosiężną klamrą i kłem"),
        "kostur": ("Kostur z Czaszką", "kościany kostur z rogatą czaszką o świecących oczach i mosiężnymi obręczami"),
    },
    ("mag", "dzungla"): {
        "kapelusz": ("Tiara Słońca", "złota tiara z jadeitowym klejnotem, dyskiem słońca i wachlarzem piór"),
        "szata": ("Szata Kapłana Słońca", "jadeitowa szata ze złotym pektorałem, wachlarze piór na ramionach "
                                           "i dysk słońca na plecach"),
        "pas": ("Szarfa z Jadeitem", "jadeitowa szarfa ze złotą klamrą i dyskiem"),
        "kostur": ("Berło Słońca", "złote berło z dyskiem słońca, promieniami, jadeitowym klejnotem i piórami"),
    },
}


# --------------------------------------------------------------------------- narzędzia
def _mapa(klasa, st):
    """{dzisiejszy kolor hex: nowy kolor hex} dla klasy i stopnia."""
    mod = MODULY[klasa]
    return {kolor_hex(z, mod.PALETA): kolor_hex(na, PALETY[st]) for z, na in MAPY[(klasa, st)].items()}


def _przemaluj(czesci, mapa, st, bez=(), po_nazwie=None):
    """Kopie dzisiejszych brył w kolorach stopnia: bez brył o nazwach zaczynających się od `bez`, z kolorem wybranym
    po nazwie bryły (po_nazwie = {początek nazwy: nazwa koloru stopnia})."""
    wynik = []
    for c in czesci:
        if any(c["n"].startswith(b) for b in bez):
            continue
        d = dict(c)
        klucz = next((k for k in (po_nazwie or {}) if c["n"].startswith(k)), None)
        if klucz is not None:
            d["c"] = kolor_hex(po_nazwie[klucz], PALETY[st])
        else:
            d["c"] = mapa.get(c["c"], c["c"])
        d["m"] = MATERIALY[st].get(c["m"], c["m"])
        wynik.append(d)
    return wynik


def _z_bazy(baza, id, klasa, st, rzecz, bez=(), po_nazwie=None, typ=Przedmiot):
    """Przedmiot stopnia z dzisiejszego przedmiotu: te same segmenty kostne (kość, powłoka), bryły przemalowane."""
    nazwa = OPISY[(klasa, st)][rzecz][0]
    czesc_od = None
    if baza.czesc_od:
        czesc_od = baza.czesc_od.replace(BOHATER[klasa] + "_", "%s_%s_" % (BOHATER[klasa], st), 1)
    n = typ(id, nazwa, baza.slot, baza.kategoria, baza.miara, cialo=baza.cialo, klasy=baza.klasy, czesc_od=czesc_od,
            ukrywa=baza.ukrywa, zestaw="%s_%s" % (BOHATER[klasa], st), paleta=PALETY[st])
    mapa = _mapa(klasa, st)
    for s in baza.segmenty:
        if s["kosc"]:
            a = n.segment(s["kosc"], zakrywa=s["zakrywa"])
            a.czesci = _przemaluj(s["akc"].czesci, mapa, st, bez, po_nazwie)
    return n


def _seg(prz, kosc):
    """Akcesorium segmentu przedmiotu na danej kości."""
    return next(s["akc"] for s in prz.segmenty if s["kosc"] == kosc)


def _bron(id, klasa, st, rzecz, zaczep="RightGripAttachment", ikona_obrot=(0, 0, -45), typ="Bron"):
    return Akcesorium(id, OPISY[(klasa, st)][rzecz][0], zaczep=zaczep, typ=typ, paleta=PALETY[st],
                      ikona_obrot=ikona_obrot)


def _trojkat(a, nazwa, h, szer, grub, kolor, mat="matowy", plaszczyzna="XY"):
    """Płaski trójkąt z dwóch klinów w układzie bieżącym: podstawa w (0,0,0), wierzchołek w +Y. Płaszczyzna „XY” —
    szerokość w osi X, grubość w Z; „YZ” — szerokość w Z, grubość w X. Dwie części Roblox (ostrosłup to cztery,
    ścięty ostrosłup dziewięć) — bohater w świecie ma limit brył."""
    if plaszczyzna == "XY":
        a.klin(nazwa, (szer / 4, h / 2, 0), (grub, h, szer / 2), kolor, mat, rot=(0, -90, 0), faza=0.0)
        a.klin(nazwa, (-szer / 4, h / 2, 0), (grub, h, szer / 2), kolor, mat, rot=(0, 90, 0), faza=0.0)
    else:
        a.klin(nazwa, (0, h / 2, szer / 4), (grub, h, szer / 2), kolor, mat, rot=(0, 180, 0), faza=0.0)
        a.klin(nazwa, (0, h / 2, -szer / 4), (grub, h, szer / 2), kolor, mat, faza=0.0)


def _plaski(a, nazwa, srodek, rozmiar, kolor, mat="matowy", rot=(0, 0, 0), faza=None):
    """Płaski kolec (kieł, ząb, płetwa grzebienia) w miejscu ostrosłupa o tym samym środku, rozmiarze i obrocie:
    trójkąt w płaszczyźnie szerszego z wymiarów X / Z, grubość = węższy."""
    x, h, z = rozmiar
    with a.uklad(pos=srodek, obrot=rot):
        with a.uklad(pos=(0, -h / 2, 0)):
            if x <= z:
                _trojkat(a, nazwa, h, z, x, kolor, mat, "YZ")
            else:
                _trojkat(a, nazwa, h, x, z, kolor, mat, "XY")


def _pioro(a, nazwa, kolor, dl=1.0, szer=0.3):
    """Pióro w układzie bieżącym: nasada w (0,0,0), rośnie w +Y, płaskie w osi Z (trójkąt z dwóch klinów)."""
    _trojkat(a, nazwa, dl, szer, 0.06, kolor, "matowy", "XY")


def _wachlarz(a, nazwa, pos, katy, dl, szer=0.3, pochyl=-10):
    """Wachlarz piór w płaszczyźnie XY: pióra rozchodzą się z punktu `pos` pod kątami `katy` (0 = w górę)."""
    for i, kat in enumerate(katy):
        with a.uklad(pos=pos, obrot=(pochyl, 0, -kat)):
            _pioro(a, "%s %d" % (nazwa, i), PIORA[i % 3], dl, szer)


# --------------------------------------------------------------------------- wspólne ozdoby ciała „czlowiek”
def _ozdoby_dloni(a, st, W):
    w, h, d = W
    if st == "las":
        a.blok("Futro mankietu", (0, h / 2 + 0.05, 0), (w + 0.22, 0.14, d + 0.22), "akcent_cien", "matowy", faza=0.05)
    elif st == "bagno":
        for x in (-0.24, 0.24):
            _plaski(a, "Kolec kostki", (x, -0.02, d / 2 + 0.13), (0.18, 0.3, 0.18), "akcent", "matowy",
                        rot=(90, 0, 0), faza=0.0)
    else:
        a.blok("Bransoleta", (0, h / 2 + 0.06, 0), (w + 0.24, 0.12, d + 0.24), "ozdoba", "polysk", faza=0.04)
        a.blok("Bransoleta klejnot", (0, h / 2 + 0.06, d / 2 + 0.13), (0.2, 0.2, 0.06), "akcent", "polysk",
               rot=(0, 0, 45), faza=0.0)


def _ozdoby_goleni(a, st, W, przod):
    """przod = o ile przed klocek goleni wystaje dzisiejszy nakolannik albo wywinięcie cholewy."""
    w, h, d = W
    if st == "las":
        a.blok("Futro cholewy", (0, h / 2 - 0.07, 0), (w + 0.16, 0.16, d + 0.16), "akcent_cien", "matowy", faza=0.05)
    elif st == "bagno":
        _plaski(a, "Kolec kolana", (0, h / 2 - 0.1, d / 2 + przod + 0.14), (0.24, 0.3, 0.24), "akcent", "matowy",
                    rot=(90, 0, 0), faza=0.0)
    else:
        a.walec("Dysk kolana", (0, h / 2 - 0.1, d / 2 + przod + 0.03), (0.4, 0.06, 0.4), "ozdoba", "polysk",
                rot=(90, 0, 0), faza=0.0)
        a.blok("Opaska z pior", (0, -h / 2 + 0.1, 0), (w + 0.12, 0.12, d + 0.12), "akcent", "matowy", faza=0.03)


# --------------------------------------------------------------------------- Wojownik
def _miecz(id, st):
    a = _bron(id, "wojownik", st, "miecz")
    if st == "las":
        a.blok("Rekojesc", (0, 0, 0), (0.24, 1.05, 0.24), "ozdoba_ciemna", "matowy", faza=0.04)
        for y in (-0.3, 0.0, 0.3):
            a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), "glowny", "matowy", faza=0.0)
        a.blok("Glowica", (0, -0.66, 0), (0.38, 0.3, 0.38), "ozdoba", "matowy", rot=(0, 45, 0), faza=0.08)
        a.blok("Jelec", (0, 0.64, 0), (1.0, 0.2, 0.3), "ozdoba_ciemna", "matowy", faza=0.06)
        for zn in (1, -1):
            a.blok("Jelec galazka", (zn * 0.5, 0.84, 0), (0.18, 0.44, 0.26), "ozdoba", "matowy",
                   rot=(0, 0, -zn * 20), faza=0.05)
            a.blok("Jelec listek", (zn * 0.64, 1.1, 0), (0.24, 0.24, 0.08), "tkanina_jasna", "matowy",
                   rot=(0, 0, 45), faza=0.0)
        a.ostroslup("Klinga dol", (0, 1.35, 0), (0.9, 1.2, 0.16), "zelazo", "metal", rot=(180, 0, 0),
                    gora=(0.4, 0.12))
        a.ostroslup("Klinga gora", (0, 3.0, 0), (0.9, 2.1, 0.16), "zelazo", "metal", gora=(0.0, 0.1))
        a.blok("Zylka", (0, 2.1, 0), (0.12, 2.3, 0.2), "tkanina_ciemna", "matowy", faza=0.0)
    elif st == "bagno":
        a.blok("Rekojesc", (0, 0, 0), (0.24, 1.05, 0.24), "akcent_cien", "matowy", faza=0.04)
        for y in (-0.3, 0.0, 0.3):
            a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), "glowny_ciemny", "matowy", faza=0.0)
        a.blok("Glowica", (0, -0.66, 0), (0.36, 0.26, 0.36), "ozdoba", "metal", faza=0.08)
        _plaski(a, "Glowica pazur", (0, -0.92, 0), (0.2, 0.3, 0.2), "akcent", "matowy", rot=(180, 0, 0), faza=0.0)
        a.blok("Jelec", (0, 0.64, 0), (0.9, 0.22, 0.34), "ozdoba", "metal", faza=0.06)
        a.ostroslup("Klinga", (0, 2.1, 0), (1.0, 2.6, 0.16), "glowny", "metal", rot=(180, 0, 0), gora=(0.5, 0.14))
        a.ostroslup("Sztych", (0, 3.7, 0), (1.0, 0.6, 0.16), "glowny", "metal", gora=(0.0, 0.1),
                    przes_gory=(-0.4, 0.0))
        a.blok("Grzbiet", (-0.3, 2.1, 0), (0.12, 2.3, 0.2), "glowny_ciemny", "metal", rot=(0, 0, 5.5), faza=0.0)
        for y in (1.2, 1.8, 2.4, 3.0):                             # zęby z kości na ostrzu (+X)
            pol = 0.25 + 0.25 * (y - 0.8) / 2.6
            _plaski(a, "Zab", (pol + 0.12, y, 0), (0.26, 0.34, 0.1), "akcent", "matowy", rot=(0, 0, -90), faza=0.0)
    else:
        a.blok("Rekojesc", (0, 0, 0), (0.24, 1.05, 0.24), "glowny_ciemny", "metal", faza=0.04)
        for y in (-0.3, 0.0, 0.3):
            a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), "tkanina", "matowy", faza=0.0)
        a.blok("Glowica", (0, -0.66, 0), (0.38, 0.32, 0.38), "ozdoba", "polysk", rot=(0, 45, 0), faza=0.08)
        for zn, kolor in ((1, "akcent"), (-1, "piora1")):
            with a.uklad(pos=(zn * 0.08, -0.8, 0), obrot=(0, 0, 180 - zn * 18)):
                _pioro(a, "Pioro glowicy", kolor, 0.55, 0.18)
        a.walec("Dysk slonca", (0, 0.72, 0), (0.8, 0.3, 0.8), "glowny", "metal", rot=(90, 0, 0))
        for zk in (1, -1):
            a.blok("Dysk klejnot", (0, 0.72, zk * 0.17), (0.24, 0.24, 0.06), "ozdoba", "polysk", rot=(0, 0, 45),
                   faza=0.0)
        a.blok("Klinga", (0, 2.3, 0), (0.6, 2.6, 0.2), "glowny", "metal", faza=0.04)
        a.blok("Zbrocze", (0, 2.3, 0), (0.16, 2.3, 0.24), "glowny_cien", "metal", faza=0.0)
        a.ostroslup("Grot", (0, 3.85, 0), (0.6, 0.5, 0.2), "glowny", "metal", gora=(0.2, 0.1))
        for y in (1.3, 1.8, 2.3, 2.8, 3.3):                        # jadeitowe zęby po obu stronach
            for zn in (1, -1):
                a.blok("Zab", (zn * 0.34, y, 0), (0.26, 0.26, 0.12), "ozdoba", "polysk", rot=(0, 0, 45), faza=0.0)
    return a


def _tarcza(id, st):
    """Tarcza w ramce dzisiejszej tarczy Rycerza (rycerz.tarcza): lico = lokalne +Z, środek ok. (0, −0,05, 0)."""
    a = _bron(id, "wojownik", st, "tarcza", zaczep="LeftGripAttachment", ikona_obrot=(90, -80, 0))
    with a.uklad(obrot=(-90, 0, 0)):
        for y in (0.3, 0.7):
            a.blok("Pas", (0.6, y, 0), (0.24, 0.12, 0.44), "glowny_ciemny", "matowy", faza=0.0)
        with a.uklad(pos=(0.78, 0.4, 0), obrot=(0, 80, 0)):
            a.blok("Tyl", (0, 0.25, -0.08), (0.9, 0.8, 0.06), "glowny_ciemny", "matowy", faza=0.0)
            if st == "las":
                a.walec("Obrecz", (0, -0.05, -0.02), (1.76, 0.1, 1.76), "glowny_ciemny", "matowy", rot=(90, 0, 0))
                a.walec("Deski", (0, -0.05, 0.02), (1.6, 0.1, 1.6), "ozdoba", "matowy", rot=(90, 0, 0), faza=0.0)
                for x in (-0.4, 0.0, 0.4):
                    a.blok("Szpara", (x, -0.05, 0.075), (0.04, 1.36 if x else 1.5, 0.02), "ozdoba_ciemna",
                           "matowy", faza=0.0)
                a.walec("Umbo", (0, -0.05, 0.11), (0.5, 0.14, 0.5), "zelazo", "metal", rot=(90, 0, 0))
                a.blok("Listek", (0, -0.05, 0.2), (0.2, 0.2, 0.04), "tkanina_jasna", "matowy", rot=(0, 0, 45),
                       faza=0.0)
            elif st == "bagno":
                a.walec("Brzeg", (0, -0.05, -0.02), (1.62, 0.1, 1.92), "ozdoba", "metal", rot=(90, 0, 0))
                a.walec("Skorupa", (0, -0.05, 0.02), (1.46, 0.12, 1.76), "glowny", "polysk", rot=(90, 0, 0),
                        faza=0.0)
                for x, y in ((0, 0.45), (-0.36, 0.08), (0.36, 0.08), (0, -0.3), (-0.3, -0.62), (0.3, -0.62)):
                    a.blok("Plytka", (x, y - 0.05, 0.09), (0.4, 0.4, 0.05), "glowny_cien", "polysk",
                           rot=(0, 0, 45), faza=0.0)
                for x, y, kat in ((0, 0.95, 0), (0, -1.05, 180), (0.84, -0.05, -90), (-0.84, -0.05, 90)):
                    _plaski(a, "Kolec", (x, y, 0.0), (0.22, 0.26, 0.1), "akcent", "matowy", rot=(0, 0, kat))
                a.ostroslup("Guz", (0, -0.05, 0.22), (0.3, 0.3, 0.3), "akcent", "matowy", rot=(90, 0, 0), faza=0.0)
            else:
                a.walec("Dysk", (0, -0.05, 0.0), (1.4, 0.12, 1.4), "glowny", "metal", rot=(90, 0, 0))
                a.walec("Pierscien", (0, -0.05, 0.05), (1.0, 0.08, 1.0), "ozdoba", "polysk", rot=(90, 0, 0),
                        faza=0.0)
                a.walec("Twarz slonca", (0, -0.05, 0.1), (0.56, 0.08, 0.56), "glowny_cien", "metal",
                        rot=(90, 0, 0), faza=0.0)
                for kat in (-90, -45, 0, 45, 90):                  # promienie u góry i po bokach
                    with a.uklad(pos=(0, -0.05, 0), obrot=(0, 0, kat)):
                        _plaski(a, "Promien", (0, 0.82, 0), (0.3, 0.26, 0.1), "glowny_cien", "metal")
                for i, kat in enumerate((150, 180, 210)):          # pióra u dołu
                    with a.uklad(pos=(0, -0.05, -0.02), obrot=(0, 0, kat)):
                        with a.uklad(pos=(0, 0.6, 0)):
                            _pioro(a, "Pioro %d" % i, PIORA[i], 0.5, 0.22)
    return a


def _wojownik(st):
    baza = {x.id: x for x in rycerz.przedmioty()}
    W = baza["rycerz_helm"].miara.wymiary

    def z(rzecz, **k):
        return _z_bazy(baza["rycerz_" + rzecz], "rycerz_%s_%s" % (st, rzecz), "wojownik", st, rzecz, **k)

    # --- hełm: bez grzebienia; poroże / kościany grzebień z kłami / pióropusz z dyskiem słońca
    helm = z("helm", bez=("Grzebien",), po_nazwie={"Obrecz": "ozdoba", "Czolo obrecz": "ozdoba", "Nit": "ozdoba_ciemna",
                                                    "Helm tyl listwa": "ozdoba"})
    a = _seg(helm, "Head")
    w, h, d = W("Head")
    zf = d / 2
    if st == "las":
        for zn in (1, -1):
            with a.uklad(pos=(zn * 0.98, 0.42, -0.1), obrot=(0, 0, -zn * 28)):
                a.blok("Poroze pien", (0, 0.36, 0), (0.17, 0.78, 0.17), "akcent", "matowy", faza=0.04)
                a.blok("Poroze odnoga", (zn * 0.2, 0.42, 0), (0.13, 0.42, 0.13), "akcent", "matowy",
                       rot=(0, 0, -zn * 55), faza=0.03)
                a.blok("Poroze czubek", (-zn * 0.1, 0.84, 0), (0.13, 0.36, 0.13), "akcent_cien", "matowy",
                       rot=(0, 0, zn * 30), faza=0.03)
        a.blok("Futro karku", (0, -0.5, -zf - 0.2), (1.76, 0.44, 0.16), "akcent_cien", "matowy", faza=0.06)
        a.blok("Listek czola", (0, h / 2 + 0.06, zf + 0.23), (0.3, 0.3, 0.05), "tkanina_jasna", "matowy",
               rot=(0, 0, 45), faza=0.0)
    elif st == "bagno":
        for i, zz in enumerate((0.55, 0.15, -0.25, -0.65)):
            _plaski(a, "Grzebien kolec", (0, h / 2 + 0.5 - 0.03 * i, zz), (0.2, 0.46 - 0.04 * i, 0.34), "akcent",
                        "matowy", rot=(-14, 0, 0), faza=0.0)
        for zn in (1, -1):
            _plaski(a, "Kiel", (zn * 0.74, -0.42, zf + 0.34), (0.2, 0.5, 0.2), "akcent", "matowy",
                        rot=(108, 0, -zn * 8), faza=0.0)
    else:
        _wachlarz(a, "Pioro", (0, h / 2 + 0.28, -0.12), (-44, -22, 0, 22, 44), 1.0, 0.3)
        a.walec("Dysk slonca", (0, h / 2 + 0.02, zf + 0.23), (0.5, 0.06, 0.5), "glowny_cien", "metal",
                rot=(90, 0, 0), faza=0.0)
        a.blok("Dysk klejnot", (0, h / 2 + 0.02, zf + 0.28), (0.2, 0.2, 0.05), "ozdoba", "polysk", rot=(0, 0, 45),
               faza=0.0)

    # --- zbroja: futrzany kołnierz i kora / łuski, żebra i kolce / dysk słońca, skrzydła i pióra
    bez = {"las": ("Naramiennik lama", "Naramiennik nit"),
           "bagno": ("Tabard", "Lamowka", "Godlo"),
           "dzungla": ("Tabard", "Lamowka", "Godlo", "Naramiennik lama", "Naramiennik nit")}[st]
    zbr = z("zbroja", bez=bez, po_nazwie={"Obojczyk": "ozdoba"} if st == "bagno" else None)
    a = _seg(zbr, "UpperTorso")
    w, h, d = W("UpperTorso")
    zf = d / 2
    if st == "las":
        a.blok("Futro kolnierza", (0, h / 2 - 0.02, -0.03), (1.86, 0.34, d + 0.3), "akcent_cien", "matowy",
               faza=0.1)
    elif st == "bagno":
        for r, y in enumerate((0.38, 0.03, -0.32)):
            for k in range(4 if r % 2 == 0 else 3):
                x = (-0.63 + 0.42 * k) if r % 2 == 0 else (-0.42 + 0.42 * k)
                a.blok("Luska", (x, y, zf + 0.03), (0.4, 0.4, 0.06), "glowny_cien" if (r + k) % 2 else "glowny",
                       "metal", rot=(0, 0, 45), faza=0.0)
        for zn in (1, -1):
            for y in (0.22, -0.12):
                a.blok("Zebro", (zn * 0.52, y, zf + 0.085), (0.72, 0.09, 0.05), "akcent", "matowy",
                       rot=(0, 0, -zn * 12), faza=0.0)
        a.blok("Mostek", (0, 0.06, zf + 0.09), (0.14, 0.78, 0.06), "akcent", "matowy", faza=0.02)
        a.blok("Luska plecy", (0, -0.05, -zf - 0.03), (1.3, h - 0.3, 0.06), "glowny_cien", "metal", faza=0.0)
    else:
        a.walec("Dysk piersi", (0, 0.06, zf + 0.04), (0.9, 0.08, 0.9), "ozdoba", "polysk", rot=(90, 0, 0),
                faza=0.0)
        a.walec("Dysk srodek", (0, 0.06, zf + 0.09), (0.46, 0.06, 0.46), "glowny_cien", "metal", rot=(90, 0, 0),
                faza=0.0)
        for k in range(8):
            with a.uklad(pos=(0, 0.06, zf + 0.04), obrot=(0, 0, 45 * k)):
                a.blok("Promien", (0, 0.55, 0), (0.14, 0.22, 0.06), "glowny_cien", "metal", faza=0.0)
        for i, x in enumerate((-0.5, 0.0, 0.5)):
            with a.uklad(pos=(x, h / 2 - 0.2, -zf - 0.06), obrot=(0, 0, 180 + x * 16)):
                _pioro(a, "Pioro plecow %d" % i, PIORA[i], 1.05, 0.4)
    for strona, zn in (("Left", 1), ("Right", -1)):
        a = _seg(zbr, strona + "UpperArm")
        w, h, d = W(strona + "UpperArm")
        if st == "las":
            a.blok("Kora", (zn * 0.14, h / 2 + 0.14, 0), (1.12, 0.14, 1.12), "ozdoba", "matowy",
                   rot=(0, 0, -zn * 10), faza=0.05)
            a.blok("Kora 2", (zn * 0.3, h / 2 + 0.25, 0), (0.7, 0.12, 0.8), "ozdoba_ciemna", "matowy",
                   rot=(0, 0, -zn * 14), faza=0.04)
        elif st == "bagno":
            for i in range(3):
                a.ostroslup("Kolec naramiennika", (zn * (-0.18 + 0.36 * i), h / 2 + 0.3 - 0.05 * i, 0),
                            (0.24, 0.42, 0.24), "akcent", "matowy", rot=(0, 0, -zn * (8 + 18 * i)), faza=0.0)
        else:
            with a.uklad(pos=(zn * 0.2, h / 2 + 0.14, 0), obrot=(0, 0, zn * 26)):
                a.blok("Skrzydlo", (zn * 0.3, 0.06, 0), (1.0, 0.14, 1.26), "glowny", "metal", faza=0.05)
                a.blok("Skrzydlo brzeg", (zn * 0.82, 0.1, 0), (0.14, 0.22, 1.3), "ozdoba", "polysk", faza=0.04)

    nog = z("nogawice")

    # --- pas: do dzisiejszej klamry dochodzi szeroki pas i ozdoba krainy
    pas = z("pas", po_nazwie={"Klamra srodek": "glowny_ciemny", "Klamra": "ozdoba"})
    a = _seg(pas, "LowerTorso")
    w, h, d = W("LowerTorso")
    zf = d / 2
    a.blok("Pas", (0, 0, 0), (w + 0.06, 0.24, d + 0.06), "glowny_ciemny", "matowy", faza=0.03)
    if st == "las":
        a.blok("Sakiewka", (0.78, -0.14, zf + 0.15), (0.36, 0.36, 0.22), "glowny", "matowy", faza=0.07)
        a.blok("Sakiewka klapka", (0.78, -0.02, zf + 0.27), (0.38, 0.14, 0.03), "ozdoba_ciemna", "matowy", faza=0.0)
    elif st == "bagno":
        for x in (-0.86, 0.86):
            _plaski(a, "Kiel pasa", (x, -0.26, zf + 0.09), (0.14, 0.34, 0.08), "akcent", "matowy",
                        rot=(180, 0, 0), faza=0.0)
    else:
        a.walec("Dysk pasa", (0, 0, zf + 0.12), (0.52, 0.06, 0.52), "ozdoba", "polysk", rot=(90, 0, 0), faza=0.0)
        for i, x in enumerate((-0.88, 0.88)):
            with a.uklad(pos=(x, -0.08, zf + 0.09), obrot=(0, 0, 180)):
                _pioro(a, "Pioro pasa %d" % i, PIORA[i], 0.5, 0.2)

    rek = z("rekawice")
    but = z("buty")
    for strona in ("Left", "Right"):
        _ozdoby_dloni(_seg(rek, strona + "Hand"), st, W(strona + "Hand"))
        _ozdoby_goleni(_seg(but, strona + "LowerLeg"), st, W(strona + "LowerLeg"), 0.16)

    def bron(rzecz, slot, akc):
        p = Przedmiot(akc.id, akc.nazwa, slot, "Weapons", baza["rycerz_helm"].miara, cialo=rycerz.CIALO_TYP,
                      klasy=rycerz.KLASY, zestaw="rycerz_" + st, paleta=PALETY[st])
        p.na_zaczepie(akc)
        return p

    return [helm, zbr, nog, pas, rek, but, bron("miecz", "Weapon", _miecz("rycerz_%s_miecz" % st, st)),
            bron("tarcza", "OffHand", _tarcza("rycerz_%s_tarcza" % st, st))]


# --------------------------------------------------------------------------- Zwiadowca
class _PrzedmiotZwiadowcy(zwiadowca._Przedmiot):
    """Ikona łuku z kołczanem jak u dzisiejszego łuku Zwiadowcy (łuk dołożony obok kołczanu, widok od tyłu)."""
    IKONA_ZACZEPIONYCH = {"zwiadowca_%s_luk" % s: zwiadowca._Przedmiot.IKONA_ZACZEPIONYCH["zwiadowca_luk"]
                          for s in STOPNIE}


def _sztylet(id, st):
    a = _bron(id, "zwiadowca", st, "sztylet")
    if st == "las":
        a.blok("Rekojesc", (0, 0, 0), (0.22, 1.0, 0.22), "akcent_cien", "matowy", faza=0.05)
        for y in (-0.25, 0.05, 0.35):
            a.blok("Pierscien", (0, y, 0), (0.26, 0.07, 0.26), "ozdoba_ciemna", "matowy", faza=0.0)
        a.blok("Glowica", (0, -0.57, 0), (0.32, 0.2, 0.32), "akcent", "matowy", faza=0.06)
        a.blok("Jelec", (0, 0.56, 0), (0.5, 0.12, 0.26), "ozdoba_ciemna", "matowy", faza=0.04)
        a.blok("Ostrze", (0.03, 1.08, 0), (0.42, 0.92, 0.1), "zelazo", "metal", faza=0.03)
        a.ostroslup("Czubek", (0.03, 1.79, 0), (0.42, 0.5, 0.1), "zelazo", "metal", gora=(0.0, 0.06),
                    przes_gory=(0.21, 0.0))
        for y in (0.82, 1.06, 1.3):                                # ząbki na grzbiecie
            a.blok("Zabek", (-0.19, y, 0), (0.13, 0.13, 0.08), "zelazo_cien", "metal", rot=(0, 0, 45), faza=0.0)
    elif st == "bagno":
        a.blok("Rekojesc", (0, 0, 0), (0.2, 1.0, 0.2), "glowny_ciemny", "matowy", faza=0.04)
        for y in (-0.25, 0.05, 0.35):
            a.blok("Pierscien", (0, y, 0), (0.24, 0.07, 0.24), "ozdoba", "metal", faza=0.0)
        a.blok("Glowica", (0, -0.6, 0), (0.32, 0.26, 0.32), "akcent", "matowy", faza=0.08)
        a.blok("Jelec", (0, 0.56, 0), (0.7, 0.14, 0.26), "ozdoba", "metal", faza=0.04)
        with a.uklad(pos=(0, 0.62, 0)):                            # zakrzywiony kieł z trzech odcinków
            a.blok("Kiel 1", (0, 0.3, 0), (0.38, 0.62, 0.14), "akcent", "matowy", faza=0.04)
            with a.uklad(pos=(0, 0.56, 0), obrot=(0, 0, 16)):
                a.blok("Kiel 2", (0, 0.28, 0), (0.32, 0.6, 0.13), "akcent", "matowy", faza=0.04)
                with a.uklad(pos=(0, 0.52, 0), obrot=(0, 0, 18)):
                    a.ostroslup("Kiel 3", (0, 0.3, 0), (0.28, 0.6, 0.12), "akcent_cien", "matowy",
                                gora=(0.0, 0.05))
    else:
        a.blok("Rekojesc", (0, 0, 0), (0.2, 1.0, 0.2), "glowny_cien", "metal", faza=0.04)
        for y in (-0.25, 0.05, 0.35):
            a.blok("Owijka", (0, y, 0), (0.24, 0.07, 0.24), "akcent", "matowy", faza=0.0)
        a.walec("Glowica", (0, -0.6, 0), (0.36, 0.14, 0.36), "glowny", "metal", rot=(90, 0, 0))
        a.blok("Glowica klejnot", (0, -0.6, 0), (0.18, 0.18, 0.2), "akcent", "polysk", rot=(0, 0, 45), faza=0.0)
        a.blok("Jelec", (0, 0.56, 0), (0.76, 0.16, 0.26), "glowny", "metal", faza=0.04)
        for zn in (1, -1):
            a.ostroslup("Jelec skrzydlo", (zn * 0.34, 0.76, 0), (0.16, 0.3, 0.2), "glowny", "metal", faza=0.0)
        a.ostroslup("Ostrze dol", (0, 0.9, 0), (0.62, 0.5, 0.1), "ozdoba", "polysk", rot=(180, 0, 0),
                    gora=(0.24, 0.1))
        a.ostroslup("Ostrze gora", (0, 1.55, 0), (0.62, 0.8, 0.1), "ozdoba", "polysk", gora=(0.0, 0.05),
                    przes_gory=(0.26, 0.0))
        a.blok("Grzbiet", (0, 1.05, 0), (0.08, 0.8, 0.14), "glowny", "metal", faza=0.0)
    return a


def _luk(id, st):
    """Dzisiejszy łuk przemalowany, z ozdobami na końcach ramion."""
    a = _bron(id, "zwiadowca", st, "luk", zaczep="LeftGripAttachment", ikona_obrot=(0, -60, 0))
    wzor = zwiadowca.luk()
    a.czesci = _przemaluj(wzor.czesci, _mapa("zwiadowca", st), st)
    for c in wzor.czesci:
        if not c["n"].startswith("Okucie"):
            continue
        zn = 1 if c["p"][1] > 0 else -1
        y, zz = c["p"][1], c["p"][2]
        if st == "las":
            a.blok("Listek konca", (0, y + zn * 0.16, zz), (0.05, 0.3, 0.3), "tkanina_jasna", "matowy",
                   rot=(45, 0, 0), faza=0.0)
        elif st == "bagno":
            _plaski(a, "Rog konca", (0, y + zn * 0.16, zz), (0.16, 0.28, 0.16), "akcent", "matowy",
                        rot=(0 if zn > 0 else 180, 0, 0), faza=0.0)
        else:
            with a.uklad(pos=(0, y + zn * 0.04, zz), obrot=(-20 if zn > 0 else 200, 90, 0)):
                _pioro(a, "Pioro konca", "akcent" if zn > 0 else "piora1", 0.3, 0.18)
    return a


def _zwiadowca(st):
    baza = {x.id: x for x in zwiadowca.przedmioty()}
    W = baza["zwiadowca_kaptur"].miara.wymiary

    def z(rzecz, **k):
        return _z_bazy(baza["zwiadowca_" + rzecz], "zwiadowca_%s_%s" % (st, rzecz), "zwiadowca", st, rzecz,
                       typ=_PrzedmiotZwiadowcy, **k)

    # --- kaptur: futro i pióro / kolce i kły / bez szpica, złota opaska i wachlarz piór
    kap = z("kaptur", bez=("Kaptur szpic",) if st == "dzungla" else (),
            po_nazwie={"Daszek": "glowny"} if st == "dzungla" else None)
    a = _seg(kap, "Head")
    w, h, d = W("Head")
    zf = d / 2
    t = _seg(kap, "UpperTorso")
    tw, th, td = W("UpperTorso")
    if st == "las":
        with a.uklad(pos=(1.0, 0.3, -0.25), obrot=(-24, 0, -10)):
            _pioro(a, "Pioro kaptura", "piora1", 0.95, 0.3)
        t.blok("Futro barkow", (0, th / 2 + 0.03, -0.04), (tw + 0.3, 0.24, td + 0.34), "akcent_cien", "matowy",
               faza=0.1)
    elif st == "bagno":
        for i, (y, zz) in enumerate(((h / 2 + 0.5, 0.1), (h / 2 + 0.5, -0.36), (h / 2 + 0.36, -0.8))):
            _plaski(a, "Kolec kaptura %d" % i, (0, y, zz), (0.2, 0.42, 0.32), "akcent", "matowy",
                        rot=(-18 - 14 * i, 0, 0), faza=0.0)
        for zn in (1, -1):
            _plaski(a, "Kiel kaptura", (zn * 0.52, h / 2 - 0.2, zf + 0.12), (0.14, 0.34, 0.1), "akcent", "matowy",
                        rot=(180, 0, 0), faza=0.0)
            _plaski(t, "Kolec barku", (zn * 1.04, th / 2 + 0.22, -0.04), (0.26, 0.38, 0.26), "akcent", "matowy",
                        rot=(0, 0, -zn * 24), faza=0.0)
    else:
        _wachlarz(a, "Pioro", (0, h / 2 + 0.22, -0.4), (-52, -26, 0, 26, 52), 1.0, 0.32, pochyl=-14)
        a.blok("Klejnot opaski", (0, h / 2 + 0.07, zf + 0.19), (0.24, 0.24, 0.06), "ozdoba", "polysk",
               rot=(0, 0, 45), faza=0.0)

    # --- kirys: drewniane płytki / łuski i kolce / pektorał i pióra
    kur = z("kurtka", bez=("Chusta wezel", "Chusta koniec") if st == "dzungla" else ())
    a = _seg(kur, "UpperTorso")
    w, h, d = W("UpperTorso")
    zf = d / 2
    if st == "bagno":
        for x, y in ((-0.56, -0.02), (-0.14, -0.02), (-0.77, -0.38), (-0.35, -0.38), (0.07, -0.38)):
            a.blok("Luska", (x, y, zf + 0.045), (0.38, 0.38, 0.04), "glowny_cien", "polysk", rot=(0, 0, 45),
                   faza=0.0)
    elif st == "dzungla":
        a.ostroslup("Pektoral", (0, h / 2 - 0.34, zf + 0.07), (1.6, 0.56, 0.06), "glowny_cien", "metal",
                    rot=(180, 0, 0), gora=(0.5, 0.06), faza=0.0)
        a.blok("Pektoral klejnot", (0, h / 2 - 0.34, zf + 0.115), (0.28, 0.28, 0.05), "ozdoba", "polysk",
               rot=(0, 0, 45), faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        a = _seg(kur, strona + "UpperArm")
        w, h, d = W(strona + "UpperArm")
        if st == "las":
            a.blok("Plytka drewna", (zn * 0.08, h / 2 + 0.05, 0), (w + 0.16, 0.12, d + 0.2), "ozdoba", "matowy",
                   rot=(0, 0, -zn * 8), faza=0.05)
        elif st == "bagno":
            _plaski(a, "Kolec ramienia", (zn * 0.2, h / 2 + 0.2, 0), (0.28, 0.42, 0.28), "akcent", "matowy",
                        rot=(0, 0, -zn * 22), faza=0.0)
        else:
            for i, kat in enumerate((30, 60, 90)):
                with a.uklad(pos=(zn * 0.3, h / 2 + 0.02, 0), obrot=(0, 0, -zn * kat)):
                    _pioro(a, "Pioro ramienia %d" % i, PIORA[i], 0.6, 0.26)

    spo = z("spodnie")
    pas = z("pas", po_nazwie={"Klamra srodek": "glowny_ciemny", "Klamra": "ozdoba"})
    rek = z("rekawice")
    but = z("buty")
    for strona in ("Left", "Right"):
        _ozdoby_dloni(_seg(rek, strona + "Hand"), st, W(strona + "Hand"))
        _ozdoby_goleni(_seg(but, strona + "LowerLeg"), st, W(strona + "LowerLeg"), 0.03)

    # --- łuk z kołczanem: kołczan przemalowany (segment kostny pierwszy), łuk z ozdobami
    luk = z("luk")
    luk.na_zaczepie(_luk("zwiadowca_%s_luk" % st, st))
    szt = _PrzedmiotZwiadowcy("zwiadowca_%s_sztylet" % st, OPISY[("zwiadowca", st)]["sztylet"][0], "Weapon",
                              "Weapons", baza["zwiadowca_kaptur"].miara, cialo=zwiadowca.CIALO_TYP,
                              klasy=zwiadowca.KLASY, zestaw="zwiadowca_" + st, paleta=PALETY[st])
    szt.na_zaczepie(_sztylet(szt.id, st))
    return [kap, kur, spo, pas, rek, but, luk, szt]


# --------------------------------------------------------------------------- Mag (kot)
def _kapelusz(id, st):
    """Nakrycie głowy kota: (0,0,0) = HatAttachment (środek góry głowy); uszy przechodzą przez nie jak dziś."""
    a = _bron(id, "mag", st, "kapelusz", zaczep="HatAttachment", ikona_obrot=(0, 20, 0), typ="Hat")
    if st == "las":
        a.walec("Rondo", (0, 0.06, 0), (2.5, 0.12, 2.3), "glowny", "matowy", segm=8)
        a.walec("Rondo spod", (0, 0.0, 0), (2.3, 0.03, 2.1), "glowny_ciemny", "matowy", segm=8, faza=0.0)
        a.ostroslup("Glowka", (0, 0.42, 0), (1.3, 0.62, 1.2), "glowny", "matowy", gora=(0.96, 0.88))
        a.blok("Wierzch", (0, 0.74, 0), (0.86, 0.05, 0.78), "glowny_cien", "matowy", faza=0.0)
        a.blok("Wstazka", (0, 0.24, 0), (1.34, 0.2, 1.24), "tkanina", "matowy", faza=0.03)
        a.walec("Grzyb trzon", (0.8, 0.26, 0.42), (0.14, 0.3, 0.14), "akcent", "matowy", segm=8)
        a.ostroslup("Grzyb kapelusz", (0.8, 0.48, 0.42), (0.42, 0.2, 0.42), "piora1", "matowy", gora=(0.16, 0.16))
        with a.uklad(pos=(-0.6, 0.3, 0.52), obrot=(8, 0, 24)):
            _pioro(a, "Pioro", "tkanina_jasna", 0.95, 0.24)
    elif st == "bagno":
        a.blok("Czepiec", (0, 0.13, -0.02), (1.75, 0.3, 1.5), "glowny", "polysk", faza=0.1)
        a.blok("Obrecz", (0, 0.0, -0.02), (1.82, 0.08, 1.56), "ozdoba", "metal", faza=0.02)
        for zz in (0.3, -0.05, -0.4):
            _plaski(a, "Grzebien", (0, 0.42, zz), (0.16, 0.3, 0.28), "glowny_cien", "polysk", rot=(-12, 0, 0),
                        faza=0.0)
        a.blok("Czaszka", (0, 0.2, 0.76), (0.5, 0.4, 0.1), "akcent", "matowy", faza=0.04)
        for x in (-0.12, 0.12):
            a.blok("Oko czaszki", (x, 0.25, 0.82), (0.12, 0.12, 0.04), "blask", "swiecacy", faza=0.0)
        for zn in (1, -1):
            with a.uklad(pos=(zn * 0.84, 0.16, -0.42), obrot=(0, 0, -zn * 38)):
                a.blok("Rog", (0, 0.3, 0), (0.26, 0.62, 0.26), "akcent", "matowy", faza=0.06)
                with a.uklad(pos=(0, 0.56, 0), obrot=(0, 0, zn * 34)):
                    a.ostroslup("Rog koniec", (0, 0.3, 0), (0.22, 0.62, 0.22), "akcent_cien", "matowy")
    else:
        a.blok("Tiara", (0, 0.11, -0.02), (1.78, 0.26, 1.52), "glowny", "metal", faza=0.06)
        a.blok("Tiara klejnot", (0, 0.14, 0.77), (0.3, 0.3, 0.08), "ozdoba", "polysk", rot=(0, 0, 45), faza=0.0)
        a.walec("Slonce", (0, 0.86, -0.32), (1.1, 0.08, 1.1), "glowny_cien", "metal", rot=(90, 0, 0))
        a.walec("Slonce srodek", (0, 0.86, -0.27), (0.5, 0.06, 0.5), "ozdoba", "polysk", rot=(90, 0, 0), faza=0.0)
        _wachlarz(a, "Pioro", (0, 0.5, -0.4), (-60, -30, 0, 30, 60), 1.15, 0.34, pochyl=-6)
    return a


def _kostur(id, st):
    """Kostur: uchwyt w (0,0,0), drzewce w +Y od −0,86 do 1,7 jak dziś; głowica krainy na górze. W pozie wyjściowej
    kostur stoi tuż przy boku głowy kota (lokalne +X = ku głowie), więc głowice nie rozrastają się w +X na wysokości
    głowy: zakręt kostura z lasu idzie w −X, dysk berła jest nad głową."""
    a = _bron(id, "mag", st, "kostur", ikona_obrot=(0, 0, -35))
    drzewce = {"las": "ozdoba_ciemna", "bagno": "akcent_cien", "dzungla": "glowny_cien"}[st]
    a.walec("Drzewce", (0, 0.42, 0), (0.18, 2.55, 0.18), drzewce, "matowy" if st != "dzungla" else "metal", segm=8)
    a.blok("Owijka", (0, 0.0, 0), (0.24, 0.42, 0.24), "glowny_ciemny" if st != "dzungla" else "tkanina", "matowy",
           faza=0.04)
    if st == "las":
        a.blok("Okucie", (0, -0.83, 0), (0.24, 0.12, 0.24), "glowny", "matowy", faza=0.03)
        for i, y in enumerate((0.6, 1.1)):
            a.blok("Sek %d" % i, (0, y, 0), (0.27, 0.12, 0.27), "ozdoba", "matowy", rot=(0, 25 * i, 0), faza=0.04)
        a.blok("Listek drzewca", (-0.16, 1.32, 0), (0.24, 0.24, 0.05), "tkanina_jasna", "matowy", rot=(0, 0, 45),
               faza=0.0)
        with a.uklad(pos=(0, 1.62, 0), obrot=(0, 0, 25)):          # pastorał: trzy odcinki zakręcone ku −X (od głowy)
            a.blok("Zakret 1", (0, 0.25, 0), (0.19, 0.56, 0.19), "ozdoba_ciemna", "matowy", faza=0.05)
            with a.uklad(pos=(0, 0.48, 0), obrot=(0, 0, 55)):
                a.blok("Zakret 2", (0, 0.2, 0), (0.18, 0.48, 0.18), "ozdoba_ciemna", "matowy", faza=0.05)
                with a.uklad(pos=(0, 0.4, 0), obrot=(0, 0, 70)):
                    a.blok("Zakret 3", (0, 0.15, 0), (0.16, 0.38, 0.16), "ozdoba", "matowy", faza=0.05)
        with a.uklad(pos=(-0.42, 1.84, 0), obrot=(0, 45, 0)):
            a.ostroslup("Krysztal gora", (0, 0.13, 0), (0.28, 0.28, 0.28), "blask", "swiecacy", gora=(0, 0))
            a.ostroslup("Krysztal dol", (0, -0.1, 0), (0.28, 0.2, 0.28), "blask", "swiecacy", rot=(180, 0, 0),
                        gora=(0, 0))
    elif st == "bagno":
        a.ostroslup("Grot dolny", (0, -0.97, 0), (0.18, 0.26, 0.18), "ozdoba", "metal", rot=(180, 0, 0), faza=0.0)
        for i, y in enumerate((0.5, 0.95, 1.4)):
            a.blok("Obrecz %d" % i, (0, y, 0), (0.26, 0.08, 0.26), "ozdoba", "metal", faza=0.02)
        a.blok("Szczeka", (0, 1.72, 0.03), (0.36, 0.14, 0.36), "akcent_cien", "matowy", faza=0.04)
        a.blok("Czaszka", (0, 2.0, 0), (0.52, 0.46, 0.48), "akcent", "matowy", faza=0.1)
        for x in (-0.13, 0.13):
            a.blok("Oko", (x, 2.03, 0.25), (0.13, 0.15, 0.04), "blask", "swiecacy", faza=0.0)
        for zn in (1, -1):
            with a.uklad(pos=(zn * 0.2, 2.14, 0), obrot=(0, 0, -zn * 26)):
                a.ostroslup("Rog", (0, 0.22, 0), (0.18, 0.46, 0.18), "akcent_cien", "matowy")
    else:
        a.blok("Okucie", (0, -0.83, 0), (0.24, 0.12, 0.24), "ozdoba", "polysk", faza=0.03)
        for i, y in enumerate((0.55, 1.0)):
            a.blok("Pierscien %d" % i, (0, y, 0), (0.27, 0.1, 0.27), "ozdoba", "polysk", faza=0.03)
        a.blok("Szyjka", (0, 1.9, 0), (0.2, 0.5, 0.2), "glowny", "metal", faza=0.04)
        a.walec("Dysk slonca", (0, 2.5, 0), (0.8, 0.1, 0.8), "glowny", "metal", rot=(90, 0, 0))
        for zk in (1, -1):
            a.blok("Klejnot", (0, 2.5, zk * 0.07), (0.3, 0.3, 0.06), "ozdoba", "polysk", rot=(0, 0, 45), faza=0.0)
        for kat in (-45, 0, 45):
            with a.uklad(pos=(0, 2.5, 0), obrot=(0, 0, kat)):
                _plaski(a, "Promien", (0, 0.53, 0), (0.18, 0.28, 0.08), "glowny_cien", "metal")
        for zn, kolor in ((1, "akcent"), (-1, "piora1")):
            with a.uklad(pos=(zn * 0.12, 1.66, 0), obrot=(0, 0, 180 - zn * 20)):
                _pioro(a, "Pioro berla", kolor, 0.5, 0.18)
    return a


def _mag(st):
    baza = {x.id: x for x in kot_mag.przedmioty()}
    m = baza["kot_mag_szata"].miara
    W = m.wymiary

    def z(rzecz, **k):
        return _z_bazy(baza["kot_mag_" + rzecz], "kot_mag_%s_%s" % (st, rzecz), "mag", st, rzecz, **k)

    def na_zaczepie(slot, kategoria, akc):
        p = Przedmiot(akc.id, akc.nazwa, slot, kategoria, m, cialo=kot_mag.CIALO_TYP, klasy=kot_mag.KLASY,
                      zestaw="kot_mag_" + st, paleta=PALETY[st])
        p.na_zaczepie(akc)
        return p

    # --- szata: peleryna z liści / naramienniki z kolcami i naszyjnik z kłów / pektorał, pióra i dysk na plecach
    bez = {"las": ("Kaptur",), "bagno": ("Zapinka", "Klejnot"), "dzungla": ("Kaptur",)}[st]
    sz = z("szata", bez=bez, po_nazwie={"Piers": "akcent" if st == "bagno" else "ozdoba"} if st != "las" else None)
    a = _seg(sz, "UpperTorso")
    w, h, d = W("UpperTorso")
    zf = d / 2
    if st == "las":
        a.blok("Narzutka", (0, h / 2 + 0.02, 0), (w + 0.42, 0.14, d + 0.36), "tkanina_ciemna", "matowy", faza=0.05)
        for x in (-0.5, 0.5):
            a.blok("Lisc przod", (x, h / 2 - 0.2, zf + 0.15), (0.4, 0.4, 0.05), "tkanina", "matowy",
                   rot=(0, 0, 45), faza=0.0)
        for x in (-0.48, 0.0, 0.48):
            a.blok("Lisc tyl", (x, h / 2 - 0.24, -zf - 0.15), (0.44, 0.44, 0.05), "tkanina", "matowy",
                   rot=(0, 0, 45), faza=0.0)
        for zn in (1, -1):
            a.blok("Lisc bok", (zn * (w / 2 + 0.18), h / 2 - 0.2, 0), (0.05, 0.4, 0.4), "tkanina", "matowy",
                   rot=(45, 0, 0), faza=0.0)
    elif st == "bagno":
        for zn in (1, -1):
            a.blok("Naramiennik", (zn * 0.74, h / 2 + 0.07, 0), (0.52, 0.16, d + 0.32), "glowny_cien", "polysk",
                   rot=(0, 0, -zn * 14), faza=0.05)
            a.ostroslup("Kolec", (zn * 0.88, h / 2 + 0.32, 0), (0.22, 0.38, 0.22), "akcent", "matowy",
                        rot=(0, 0, -zn * 24), faza=0.0)
        for x in (-0.22, 0.0, 0.22):
            _plaski(a, "Kiel naszyjnika", (x, h / 2 - 0.4 + abs(x) * 0.3, zf + 0.12), (0.11, 0.24, 0.06), "akcent",
                        "matowy", rot=(180, 0, 0), faza=0.0)
    else:
        a.blok("Pektoral", (0, h / 2 - 0.01, 0), (w + 0.5, 0.14, d + 0.4), "glowny", "metal", faza=0.05)
        a.blok("Pektoral dol", (0, h / 2 - 0.13, 0.02), (w + 0.3, 0.12, d + 0.3), "glowny_cien", "metal", faza=0.04)
        a.walec("Slonce plecow", (0, -0.02, -zf - 0.1), (0.7, 0.06, 0.7), "glowny_cien", "metal", rot=(90, 0, 0),
                faza=0.0)
        for zn in (1, -1):
            for i, kat in enumerate((35, 65, 95)):
                with a.uklad(pos=(zn * 0.78, h / 2 + 0.04, 0), obrot=(0, 0, -zn * kat)):
                    _pioro(a, "Pioro ramienia %d" % i, PIORA[i], 0.56, 0.24)

    # --- szarfa: do dzisiejszej szarfy dochodzi drobiazg przy klamrze
    pas = z("pas", po_nazwie={"Pas klamra": "ozdoba" if st != "dzungla" else "glowny"})
    a = _seg(pas, "LowerTorso")
    with a.uklad(pos=tuple(-v for v in m.srodek("LowerTorso"))):
        if st == "las":
            a.blok("Sakiewka", (0.44, 0.04, 0.6), (0.24, 0.26, 0.14), "glowny_cien", "matowy", faza=0.05)
        elif st == "bagno":
            _plaski(a, "Kiel", (0.4, 0.02, 0.6), (0.12, 0.3, 0.08), "akcent", "matowy", rot=(180, 0, 0), faza=0.0)
        else:
            a.walec("Dysk", (0.42, 0.1, 0.6), (0.3, 0.06, 0.3), "glowny_cien", "metal", rot=(90, 0, 0), faza=0.0)

    return [na_zaczepie("Helmet", "Armor", _kapelusz("kot_mag_%s_kapelusz" % st, st)), sz, pas,
            na_zaczepie("Weapon", "Weapons", _kostur("kot_mag_%s_kostur" % st, st))]


# --------------------------------------------------------------------------- API
_BUDOWA = {"wojownik": _wojownik, "zwiadowca": _zwiadowca, "mag": _mag}
# kolejność zakładania kompletu = kolejność dzisiejszego kanonu (łuk przed sztyletem, EKWIPUNEK.md pkt 11)
_RZECZY = {klasa: tuple(i[len(BOHATER[klasa]) + 1:] for i in ids) for klasa, ids in KOMPLET_START.items()}


def przedmioty(klasa, stopien):
    """Nowe przedmioty klasy w stopniu (las, bagno, dzungla) — obiekty Przedmiot (świeże przy każdym wywołaniu)."""
    if stopien not in STOPNIE:
        raise ValueError("stopień: %s" % ", ".join(STOPNIE))
    return _BUDOWA[klasa](stopien)


def komplet(klasa, stopien):
    """Id przedmiotów kompletu w kolejności zakładania („start” = dzisiejszy komplet klasy)."""
    if stopien == "start":
        return tuple(KOMPLET_START[klasa])
    return tuple("%s_%s_%s" % (BOHATER[klasa], stopien, r) for r in _RZECZY[klasa])


def rzecz(id):
    """(klasa, stopień, rzecz) z id przedmiotu — także dzisiejszego (stopień „start”)."""
    for klasa, boh in BOHATER.items():
        if id.startswith(boh + "_"):
            reszta = id[len(boh) + 1:]
            for st in STOPNIE:
                if reszta.startswith(st + "_"):
                    return klasa, st, reszta[len(st) + 1:]
            return klasa, "start", reszta
    raise ValueError("nieznany przedmiot %r" % id)


def opis(id):
    """(nazwa, opis wyglądu) nowego przedmiotu."""
    klasa, st, r = rzecz(id)
    return OPISY[(klasa, st)][r]


def wszystkie(klasa):
    """{id: Przedmiot} — dzisiejsze przedmioty klasy i trzy stopnie."""
    wynik = {x.id: x for x in MODULY[klasa].przedmioty()}
    for st in STOPNIE:
        wynik.update((x.id, x) for x in przedmioty(klasa, st))
    return wynik


def postac(klasa, stopien, po_id=None, id=None):
    """Bohater klasy w komplecie stopnia: ciało bazowe bohatera z jego klipami + przedmioty (ubierz)."""
    mod = MODULY[klasa]
    po_id = po_id or wszystkie(klasa)
    return ubierz(mod.cialo(), [po_id[i] for i in komplet(klasa, stopien)],
                  id=id or "stopnie_%s_%s" % (klasa, stopien),
                  nazwa="%s — komplet %s" % (mod.NAZWA, NAZWY_STOPNI[stopien]),
                  korekty=getattr(mod, "KOREKTY_CHWYTU", None))


def modele(klasa):
    """Dla przebuduj.py: bohater w czterech kompletach (tylko klip idle — ruch jest wspólny z bohaterem) i ikony
    wszystkich nowych przedmiotów klasy."""
    po_id = wszystkie(klasa)
    wynik = []
    for st in WSZYSTKIE_STOPNIE:
        p = postac(klasa, st, po_id)
        p.klipy = [k for k in p.klipy if k.nazwa == "idle"]
        wynik.append(p)
    for st in STOPNIE:
        wynik += [po_id[i].ikona() for i in komplet(klasa, st)]
    return wynik


def plansza_stopni(cel, klasa):
    """Po przebudowie: cztery komplety obok siebie (kadry bohaterskie z wynik/<moduł>/) -> jedna plansza."""
    from swiat.postacie.przebuduj import plansza_zbiorcza
    obrazy = [("komplet " + NAZWY_STOPNI[st], os.path.join(cel, "stopnie_%s_%s_bohater.jpg" % (klasa, st)))
              for st in WSZYSTKIE_STOPNIE]
    nazwa = "stopnie_%s_cztery_stopnie.jpg" % klasa
    ok = plansza_zbiorcza([x for x in obrazy if os.path.isfile(x[1])], os.path.join(cel, nazwa),
                          "%s — komplet startowy i trzy stopnie do kupienia (propozycja)" % MODULY[klasa].NAZWA)
    return [nazwa] if ok else []


SLABOSCI = [
    "Przedmioty stopni to propozycja wyglądu; statystyki i ceny są w sklep_przedmioty.json (też propozycja).",
    "Zbroje stopni to dzisiejsze bryły w nowych materiałach z dołożonymi ozdobami — pod spodem ta sama bryła "
    "hełmu, napierśnika i butów; całkiem nowe są broń, tarcze, nakrycia głowy kota i kostury.",
    "Kontrola przenikania stopni obejmuje pozę spoczynku (test_stopnie.py); klipy walki w nowych kompletach nie "
    "były liczone klatka po klatce — poroże, pióropusze i skrzydła naramienników mogą wchodzić w ręce uniesione "
    "nad głowę.",
    "Kot ma w każdym stopniu cztery przedmioty (nakrycie głowy, szata, szarfa, kostur) — tyle slotów ma dziś.",
    "W Roblox Studio nic z tego nie było budowane ani oglądane.",
]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for _klasa in MODULY:
        for _st in STOPNIE:
            for _x in przedmioty(_klasa, _st):
                _bryl = sum(len(s["akc"].czesci) for s in _x.segmenty)
                print("%-10s %-8s %-28s %-8s %3d brył  %s" % (_klasa, _st, _x.id, _x.slot, _bryl, _x.nazwa))
