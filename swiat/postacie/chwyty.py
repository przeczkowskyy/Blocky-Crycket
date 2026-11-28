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
import math
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie.biblioteka.postac import katy_z_macierzy, macierz_obrotu, mnoz  # noqa: E402

# rodzaj -> łapa, zaczep standardowy (człowiek / ekran wyboru), opis ułożenia (dla ludzi i dla gry)
RODZAJE = {
    "miecz": {"lapa": "prawa", "zaczep": "RightGripAttachment",
              "opis": "broń jednoręczna (miecz, tasak, pałka, pogrzebacz): pięść na rękojeści, ostrze w górę, "
                      "pochylone 20° do przodu i 10° na zewnątrz, obrócone o 45° wokół własnej osi (wewnętrzna "
                      "krawędź z dala od przedramienia), rękojeść nisko i z przodu łapy"},
    "rozdzka": {"lapa": "prawa", "zaczep": "RightGripAttachment",
                "opis": "różdżka: lekki chwyt przy końcu, czubek do przodu i w górę"},
    "drzewce": {"lapa": "prawa", "zaczep": "RightGripAttachment",
                "opis": "kostur, włócznia, chorągiew: drzewce pionowo wzdłuż łapy, dół przy ziemi (chwyt kostura "
                        "Kota-Maga, odsunięty o 0,04 na zewnątrz i 5° od rękawa; nazwa „drzewce” jak w bibliotece)"},
    "proca": {"lapa": "prawa", "zaczep": "RightGripAttachment",
              "opis": "proca: rękojeść w pięści, widełki w górę, skórka z kamykiem do przodu"},
    "luk": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
            "opis": "łuk: majdan w lewej łapie, górne ramię pochylone do przodu i na zewnątrz (z dala od "
                    "przedramienia), łuk obrócony bokiem do patrzącego z przodu — widać jego wygięcie"},
    "tarcza": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
               "opis": "tarcza: na lewym przedramieniu (pasy na łapie), lico na zewnątrz — jak tarcza Rycerza",
               "przedramie_w_chwycie": True},      # pasy obejmują przedramię: styk z nim to chwyt (--ruch)
    "ksiega": {"lapa": "lewa", "zaczep": "LeftGripAttachment",
               "opis": "księga: mała, zamknięta, trzymana za górną krawędź w lewej łapie, wisi przed bokiem "
                       "(odsunięta do przodu i na zewnątrz, z dala od ogona), okładką do przodu i na zewnątrz"},
}

# Kot (ciało Kota-Maga i kotów z tym samym szkieletem): pochylenie broni w ramce dłoni w stopniach
# (do_przodu, na_zewnatrz, skret[, wlasny]) i przesunięcie w ramce zaczepu (x — bok łapy, y — przód łapy,
# z — w dół łapy). Prawa łapa — kość nośna StaffPivot (KosturAttachment: w upadku broń wypada z łapy), lewa łapa —
# zwykły LeftGripAttachment (kot nie ma kości nośnej lewej łapy: łuk, tarcza i księga zostają przy łapie w upadku —
# korekta upadku kładzie je płasko pod łapą, niżej).
# Liczby dobrane 26.11.2026 kontrolą `pula_wojownika.py --ruch` (broń względem WSZYSTKICH brył ciała i ziemi,
# klatka po klatce): kryterium — chód i spoczynek czyste z zapasem ≥ 0,05 studa (Karol: „miecz ma być tak
# wychylony, że podczas animacji chodzenia się nie bugował”), ziemia w klipach walki czysta. Miecz: więcej niż 20° do
# przodu wbija długie ostrza (pogrzebacz) w ziemię w klipie kula_ognia (25° → −0,06), mniej niż 15° — ostrze dotyka
# przedramienia w chodzie. W klipie upadku każdy stopień do przodu wbija czubek w ziemię (oś dłoni „do przodu” leży
# wtedy pionowo w dół); poprawka tylko dla upadku — KOREKTA UPADKU niżej (EKWIPUNEK.md pkt 15).
POCHYLENIE_KOTA = {
    "miecz": ("KosturAttachment", (-0.08, 0.08, 0.03), (20.0, 10.0, 0.0, -45.0)),
    "rozdzka": ("KosturAttachment", (-0.08, 0.0, 0.0), (60.0, 10.0, 0.0)),
    "drzewce": ("KosturAttachment", (-0.12, 0.03, 0.0), (0.0, 5.0, 0.0)),
    "proca": ("KosturAttachment", (-0.12, 0.03, 0.0), (5.0, 30.0, 0.0)),
    "luk": ("LeftGripAttachment", (0.2, 0.25, 0.0), (50.0, 30.0, -55.0)),
    "tarcza": ("LeftGripAttachment", (0.0, 0.0, 0.08), None),         # None: model ma własny obrót (jak u człowieka)
    "ksiega": ("LeftGripAttachment", (0.2, 0.4, -0.2), None),
}


def _zaokr(v, n=3):
    return tuple(0.0 if abs(round(x, n)) == 0 else round(x, n) for x in v)


def obrot_korekty(do_przodu=0.0, na_zewnatrz=0.0, skret=0.0, wlasny=0.0, lapa="prawa"):
    """Obrót korekty w ramce zaczepu chwytu dla pochylenia broni w ramce dłoni (stopnie). „Na zewnątrz” = od ciała:
    dla prawej łapy ku −X, dla lewej ku +X; „skręt” = obrót wokół osi pionowej (dodatni: lico ku lewej stronie
    postaci, +X); „własny” = obrót broni wokół jej własnej osi (+Y broni) przed pochyleniem."""
    zn = 1.0 if lapa == "prawa" else -1.0
    R = mnoz(macierz_obrotu(0, skret, 0), mnoz(macierz_obrotu(0, 0, zn * na_zewnatrz),
                                               mnoz(macierz_obrotu(do_przodu, 0, 0), macierz_obrotu(0, wlasny, 0))))
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
    rot}, upadek}} — ta sama tabela, której używa budowa modeli; „upadek” = grupa korekty upadku (UPADEK_KOTA;
    liczby korekty ma każda część broni w polu „korekta_upadku”)."""
    return {r: {"lapa": o["lapa"], "zaczep_standardowy": o["zaczep"], "opis": o["opis"],
                "kot": ({"zaczep": korekty[r][0], "pos": list(korekty[r][1]), "rot": list(korekty[r][2])}
                        if r in korekty else None),
                "upadek": grupa_upadku(korekty[r][0]) if r in korekty else None}
            for r, o in RODZAJE.items()}


# ------------------------------------------------------------------------------------- KOREKTA UPADKU (26.11.2026)
# Paweł 26.11.2026 po planszach przedmiotów kota-wojownika: „poprawić, żeby nie były pod ziemią”. Klip `upadek` kota
# jest wspólny dla każdego stroju (Kot-Mag, koty klas, kot-wojownik): kości nośne StaffPivot (broń w prawej łapie)
# i HatPivot (nakrycie głowy) lecą w nim po torach policzonych dla kostura i kapelusza Kota-Maga
# (kot_mag.UPADEK_LOT), a lewa łapa kości nośnej nie ma. Broń o innym chwycie i kształcie, hełm z osłonami poniżej
# obręczy i łuk albo tarcza w lewej łapie kończyły więc upadek pod ziemią (do 0,79 studa).
# Poprawka jest DANĄ PRZEDMIOTU, nie nowym klipem: KOREKTA UPADKU — druga korekta (pos, rot) w ramce TEGO SAMEGO
# zaczepu co korekta chwytu; w klipie upadku gra przechodzi z jednej na drugą:
#     a = clamp((klatka − od_klatki) / (do_klatki − od_klatki), 0, 1)        klatka = czas klipu × 30 (fps klipu)
#     C0 = C0_chwytu:Lerp(C0_upadku, a)          (CFrame:Lerp: pozycja liniowo, obrót po najkrótszym łuku)
# gdzie C0_x = CFrame zaczepu kości · CFrame.new(pos) · CFrame.fromOrientation(rot) (rot w stopniach, kolejność
# Y·X·Z jak macierz_obrotu); przed od_klatki i po wyjściu z klipu (wstawanie, odrodzenie) — korekta chwytu.
# Liczby liczy budowa z geometrii przedmiotu (pula_wojownika.korekta_upadku): ułożenie z tabeli niżej, najniższy
# punkt ZAPAS_UPADKU nad ziemią po lądowaniu; kontrola (pula_wojownika.py --ruch) sprawdza KAŻDĄ klatkę i pół
# klatki klipu: nic, co kot nosi na zaczepie, nie schodzi niżej niż PROG_UPADKU. Rendery plansz upadku liczą pozę
# przedmiotu tą samą funkcją (miesz_korekte), więc pokazują to samo, co zrobi gra.
ZAPAS_UPADKU = 0.02        # studa: najniższy punkt leżącego przedmiotu nad ziemią (leży, nie wisi)
PROG_UPADKU = 0.01         # studa: kontrola — w żadnej klatce (ani pół klatce) upadku nic nie jest niżej
UPADEK_KOTA = {
    "prawa": {"zaczep": "KosturAttachment", "kosc": "StaffPivot", "od_klatki": 22, "do_klatki": 33,
              "ulozenie": "broń wypada z łapy w kl. 22 (jak kostur Kota-Maga) i w locie obraca się do ułożenia "
                          "kostura: leży płasko przed kotem, oś broni poziomo wzdłuż leżącego kota, lico (+Z) do "
                          "ziemi, rękojeść w miejscu lądowania kostura (kl. 33), podniesiona tak, żeby najniższy "
                          "punkt był 0,02 nad ziemią"},
    "helm": {"zaczep": "KapeluszAttachment", "kosc": "HatPivot", "od_klatki": 30, "do_klatki": 40,
             "ulozenie": "hełm zsuwa się z głowy w kl. 30 (jak kapelusz Kota-Maga) i w locie prostuje się: stoi "
                         "na ziemi obok głowy kopułą do góry (obrót wokół pionu jak kapelusz, −30°), odsunięty od "
                         "głowy, najniższy punkt 0,02 nad ziemią; okno przejścia (domyślnie kl. 30→40) dobiera "
                         "budowa dla każdego hełmu — krótsze, gdy hełm szybciej schodzi z głowy"},
    "lewa": {"zaczep": "LeftGripAttachment", "kosc": "LeftHand", "od_klatki": 20, "do_klatki": 32,
             "ulozenie": "lewa łapa nie ma kości nośnej: przedmiot zostaje przy łapie i w czasie upadania "
                         "(domyślnie kl. 20, kolana miękną, → kl. 32, kot leży; okno dobiera budowa tak, żeby w "
                         "żadnej klatce nie zszedł pod ziemię) kładzie się płasko na ziemi pod łapą (najcieńszą "
                         "osią pionowo), skręcony wokół pionu tak, żeby jak najmniej wchodził w leżącego kota; "
                         "tylko przedmiot, który w stałym chwycie schodzi pod ziemię"},
}


def grupa_upadku(zaczep):
    """Grupa korekty upadku dla zaczepu kota („prawa”, „helm”, „lewa”) albo None."""
    return next((g for g, d in UPADEK_KOTA.items() if d["zaczep"] == zaczep), None)


def alfa_upadku(klatka, od_klatki, do_klatki):
    """Postęp przejścia z korekty chwytu na korektę upadku w klatce klipu upadku (0…1, liniowo)."""
    return min(1.0, max(0.0, (float(klatka) - od_klatki) / float(do_klatki - od_klatki)))


def _kwaternion(R):
    """Macierz obrotu 3×3 -> kwaternion (w, x, y, z)."""
    t = R[0][0] + R[1][1] + R[2][2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        return (0.25 * s, (R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s)
    if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        return ((R[2][1] - R[1][2]) / s, 0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s)
    if R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        return ((R[0][2] - R[2][0]) / s, (R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s)
    s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
    return ((R[1][0] - R[0][1]) / s, (R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s)


def _macierz_kwaternionu(q):
    w, x, y, z = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def miesz_obrot(R0, R1, a):
    """Obrót pośredni (jak CFrame:Lerp): po najkrótszym łuku między R0 i R1, a = 0…1."""
    q0, q1 = _kwaternion(R0), _kwaternion(R1)
    d = sum(q0[i] * q1[i] for i in range(4))
    if d < 0:
        q1, d = tuple(-v for v in q1), -d
    if d > 0.9995:
        q = tuple(q0[i] + (q1[i] - q0[i]) * a for i in range(4))
    else:
        th = math.acos(min(1.0, d))
        s0, s1 = math.sin((1 - a) * th) / math.sin(th), math.sin(a * th) / math.sin(th)
        q = tuple(s0 * q0[i] + s1 * q1[i] for i in range(4))
    n = math.sqrt(sum(v * v for v in q))
    return _macierz_kwaternionu(tuple(v / n for v in q))


def miesz_korekte(k0, k1, a):
    """Korekta (pos, rot) pośrednia między korektą chwytu k0 i korektą upadku k1 (a = alfa_upadku): pozycja
    liniowo, obrót po najkrótszym łuku — to samo, co CFrame:Lerp w grze. Zwraca (pos, rot w stopniach)."""
    if a <= 0.0:
        return tuple(k0[0]), tuple(k0[1])
    if a >= 1.0:
        return tuple(k1[0]), tuple(k1[1])
    pos = tuple(k0[0][i] + (k1[0][i] - k0[0][i]) * a for i in range(3))
    R = miesz_obrot(macierz_obrotu(*k0[1]), macierz_obrotu(*k1[1]), a)
    return pos, tuple(katy_z_macierzy(R))


def upadek_dla_gry():
    """Zasada korekty upadku do danych gry (ekwipunek.json, pole „upadek”): grupy (łapa / hełm) z zaczepem, kością,
    domyślnymi klatkami przejścia i opisem ułożenia; liczby (pos, rot, klatki) ma każda część w „korekta_upadku”."""
    return {"klip": "upadek", "fps": 30, "zapas": ZAPAS_UPADKU,
            "przejscie": "a = clamp((klatka - od_klatki) / (do_klatki - od_klatki), 0, 1); "
                         "C0 = C0_chwytu:Lerp(C0_upadku, a); C0_x = zaczep * CFrame.new(pos) * "
                         "CFrame.fromOrientation(rot w radianach); po klipie z powrotem korekta chwytu",
            "grupy": {g: {"zaczep": d["zaczep"], "kosc": d["kosc"], "od_klatki": d["od_klatki"],
                          "do_klatki": d["do_klatki"], "ulozenie": d["ulozenie"]} for g, d in UPADEK_KOTA.items()}}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for r, (z, pos, ob) in KOREKTY_KOTA.items():
        print("%-8s %-5s %-19s pos %-22s rot %s" % (r, RODZAJE[r]["lapa"], z, pos, ob))
