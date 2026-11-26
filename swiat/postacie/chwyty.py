# -*- coding: utf-8 -*-
"""RODZAJE CHWYTU BRONI — jak postać trzyma broń zależnie od jej rodzaju (Karol 26.11.2026: „odróżniaj różdżkę od
miecza i łuk itd.”). Status: propozycja. Kontrakt: swiat/postacie/EKWIPUNEK.md pkt 15.

Broń deklaruje rodzaj polem `Akcesorium.chwyt` (to samo pole, którego biblioteka używa od dawna dla „drzewce” —
broń długa w przymiarce). Ciało bohatera ma tabelę korekt {rodzaj: (zaczep ciała, pos, obrot)}; ekwipunek.korekta()
bierze najpierw wpis rodzaju, a gdy broń rodzaju nie ma albo ciało nie ma dla niego wpisu — korektę zaczepu, jak
dotąd. Broń bez rodzaju i bohaterowie bez tabeli rodzajów (Rycerz, Zwiadowca, Kot-Mag, koty ras) budują się więc
dokładnie tak jak przed tą zmianą.

Konwencja modelu broni (ta sama co w bibliotece, biblioteka/postac.py → Akcesorium): (0, 0, 0) = środek chwytu
w pięści, oś główna broni w +Y (ostrze, drzewce, ramiona łuku, widełki procy), lico do przodu (+Z). Wyjątek:
tarcza i księga modelowane jak tarcza Rycerza — w bloku `uklad(obrot=(-90, 0, 0))` (osie dłoni: +Y ku łokciowi,
+X na zewnątrz lewej łapy, +Z przód).

Korekta kota liczy się z POCHYLENIA broni w ramce dłoni (dłoń kota w pozie spoczynku klipu idle ≈ osie świata:
+Y w górę, +Z przód, +X lewa strona): R_broni_w_dłoni = Ry(skręt) · Rz(na zewnątrz) · Rx(do przodu), a obrót korekty
w ramce zaczepu chwytu (który sam ma obrót (90, 0, 0)) to Rx(−90) · R_broni_w_dłoni. Dzisiejszy chwyt kostura
Kota-Maga (−90, 0, 0) to pochylenie (0, 0, 0).

    python -B swiat/postacie/chwyty.py        # tabela rodzajów i korekt kota (bez Blendera)
"""
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie.biblioteka.postac import katy_z_macierzy, macierz_obrotu, mnoz  # noqa: E402

# rodzaj -> łapa, zaczep standardowy (człowiek / ekran wyboru), opis ułożenia (dla ludzi i dla gry)
RODZAJE = {
    "miecz": {"lapa": "prawa", "zaczep": "RightGripAttachment",
              "opis": "broń jednoręczna (miecz, tasak, pałka, pogrzebacz): pięść na rękojeści, ostrze w górę, "
                      "odchylone na zewnątrz (z dala od twarzy) i lekko do przodu, płaz widać z przodu"},
    "rozdzka": {"lapa": "prawa", "zaczep": "RightGripAttachment",
                "opis": "różdżka: lekki chwyt przy końcu, czubek do przodu i w górę"},
    "drzewce": {"lapa": "prawa", "zaczep": "RightGripAttachment",
                "opis": "kostur, włócznia, chorągiew: drzewce pionowo wzdłuż łapy, dół przy ziemi (dzisiejszy chwyt "
                        "kostura Kota-Maga; nazwa „drzewce” jak w bibliotece)"},
    "proca": {"lapa": "prawa", "zaczep": "RightGripAttachment",
              "opis": "proca: rękojeść w pięści, widełki w górę, skórka z kamykiem do przodu"},
    "luk": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
            "opis": "łuk: majdan w lewej łapie, górne ramię pochylone do przodu i na zewnątrz (z dala od "
                    "przedramienia), łuk obrócony bokiem do patrzącego z przodu — widać jego wygięcie"},
    "tarcza": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
               "opis": "tarcza: na lewym przedramieniu (pasy na łapie), lico na zewnątrz — jak tarcza Rycerza"},
    "ksiega": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
               "opis": "księga: zamknięta, trzymana za górną krawędź w lewej łapie, wisi wzdłuż boku, okładką do "
                       "przodu i na zewnątrz"},
}

# Kot (ciało Kota-Maga i kotów z tym samym szkieletem): pochylenie broni w ramce dłoni w stopniach
# (do_przodu, na_zewnatrz, skret) i przesunięcie w ramce zaczepu. Prawa łapa — kość nośna StaffPivot
# (KosturAttachment: w upadku broń wypada z łapy), lewa łapa — zwykły LeftGripAttachment (kot nie ma kości nośnej
# lewej łapy: łuk, tarcza i księga zostają w łapie także w upadku).
# Pochylenie DO PRZODU prawej łapy jest małe z konieczności: w klipie upadku kość StaffPivot kładzie broń na ziemi
# tak, że oś dłoni „do przodu” patrzy w dół — każdy stopień pochylenia do przodu wbija czubek w ziemię (miecz 2 studa:
# 30° → 0,74–0,84 studa pod ziemią, 10° → do 0,19; pomiar 26.11.2026). Odchylenie na zewnątrz leży w płaszczyźnie
# ziemi i nic nie wbija, więc miecz i proca odchylają się głównie na zewnątrz. Różdżka (60° do przodu) w upadku
# wchodzi w ziemię — do decyzji, jeśli różdżki trafią do gry na kocie.
POCHYLENIE_KOTA = {
    "miecz": ("KosturAttachment", (-0.08, 0.0, 0.0), (10.0, 20.0, 0.0)),
    "rozdzka": ("KosturAttachment", (-0.08, 0.0, 0.0), (60.0, 10.0, 0.0)),
    "drzewce": ("KosturAttachment", (-0.08, 0.0, 0.0), (0.0, 0.0, 0.0)),
    "proca": ("KosturAttachment", (-0.08, 0.0, 0.0), (5.0, 30.0, 0.0)),
    "luk": ("LeftGripAttachment", (0.15, 0.2, 0.0), (45.0, 30.0, -55.0)),
    "tarcza": ("LeftGripAttachment", (-0.12, 0.0, 0.0), None),        # None: model ma własny obrót (jak u człowieka)
    "ksiega": ("LeftGripAttachment", (0.0, 0.0, 0.0), None),
}


def _zaokr(v, n=3):
    return tuple(0.0 if abs(round(x, n)) == 0 else round(x, n) for x in v)


def obrot_korekty(do_przodu=0.0, na_zewnatrz=0.0, skret=0.0, lapa="prawa"):
    """Obrót korekty w ramce zaczepu chwytu dla pochylenia broni w ramce dłoni (stopnie). „Na zewnątrz” = od ciała:
    dla prawej łapy ku −X, dla lewej ku +X; „skręt” = obrót wokół osi pionowej (dodatni: lico ku lewej stronie
    postaci, +X)."""
    zn = 1.0 if lapa == "prawa" else -1.0
    R = mnoz(macierz_obrotu(0, skret, 0), mnoz(macierz_obrotu(0, 0, zn * na_zewnatrz), macierz_obrotu(do_przodu, 0, 0)))
    return _zaokr(katy_z_macierzy(mnoz(macierz_obrotu(-90, 0, 0), R)))


def korekty_kota():
    """{rodzaj: (zaczep kota, pos, obrot)} — klucze do dołożenia do KOREKTY_CHWYTU ciała kota."""
    wynik = {}
    for rodzaj, (zaczep, pos, poch) in POCHYLENIE_KOTA.items():
        ob = (0.0, 0.0, 0.0) if poch is None else obrot_korekty(*poch, lapa=RODZAJE[rodzaj]["lapa"])
        wynik[rodzaj] = (zaczep, tuple(pos), ob)
    return wynik


KOREKTY_KOTA = korekty_kota()


def dla_gry(korekty):
    """Rodzaje chwytu do danych gry (ekwipunek.json): {rodzaj: {lapa, zaczep_standardowy, opis, kot: {zaczep, pos,
    rot}}} — ta sama tabela, której używa budowa modeli."""
    return {r: {"lapa": o["lapa"], "zaczep_standardowy": o["zaczep"], "opis": o["opis"],
                "kot": ({"zaczep": korekty[r][0], "pos": list(korekty[r][1]), "rot": list(korekty[r][2])}
                        if r in korekty else None)}
            for r, o in RODZAJE.items()}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for r, (z, pos, ob) in KOREKTY_KOTA.items():
        print("%-8s %-5s %-19s pos %-22s rot %s" % (r, RODZAJE[r]["lapa"], z, pos, ob))
