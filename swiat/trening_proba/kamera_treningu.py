# -*- coding: utf-8 -*-
"""Lustro zrodla/KameraTreningu.luau w Pythonie — rachunek kamery stanowisk Training Center w stylu ekranu walki.

Ten sam rachunek co w grze: podglad.py rysuje nim ujęcia (gra, początek odliczania, zbliżenie po rundzie), a testy
offline rzutują nim pole gry na ekrany (5e) i sprawdzają zbliżenie na postać (5g). Zgodność z Luau pilnuje test 3f
(luau_mini z funkcjami trygonometrycznymi Pythona).

Punkt to lista [x, y, z], kąt widzenia w stopniach (pionowy, jak Camera.FieldOfView w Roblox), ujęcie to słownik
{"oko": punkt, "cel": punkt, "kat": liczba}.
"""
import math


def gladko(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1
    return x * x * (3 - 2 * x)


def wyjscie(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1
    q = 1 - x
    return 1 - q * q * q


def _mieszaj(a, b, u):
    return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]


def gra(D, gra_):
    W = D["swiat"][gra_]
    return {"oko": W["oko"], "cel": W["cel"], "kat": W["kat"]}


def przejscie(a, b, u):
    g = gladko(u)
    return {"oko": _mieszaj(a["oko"], b["oko"], g), "cel": _mieszaj(a["cel"], b["cel"], g),
            "kat": a["kat"] + (b["kat"] - a["kat"]) * g}


def stanowisko(D, gra_, czas):
    W = D["swiat"][gra_]
    kol = D["ui"]["kamera"]["kolysanie"]
    a = math.radians(kol["stopnie"]) * math.sin(2 * math.pi * czas / kol["okres_s"])
    dx, dz = W["oko"][0] - W["cel"][0], W["oko"][2] - W["cel"][2]
    c, s = math.cos(a), math.sin(a)
    return {"oko": [W["cel"][0] + dx * c + dz * s, W["oko"][1], W["cel"][2] - dx * s + dz * c], "cel": W["cel"],
            "kat": W["kat"]}


def odliczanie(D, gra_, do_startu):
    W = D["swiat"][gra_]
    koniec = D["ui"]["kamera"]["odliczanie_koniec_s"]
    u = 1 - (do_startu - koniec) / (D["runda"]["odliczanie_s"] - koniec)
    return przejscie(W["start"], gra(D, gra_), u)


def kierunek_finalu(D, gra_, czas):
    F = D["swiat"][gra_]["final"]
    O = D["ui"]["kamera"]["final"]
    znak = -1 if F["azymut"] < 0 else 1
    dryf = min(O["dryf_max"], O["dryf_stopnie_s"] * max(0, czas))
    az = math.radians(F["azymut"] - znak * dryf)
    return [math.sin(az), 0, math.cos(az)]


def final(D, gra_, korzen, fx, aspekt, czas):
    F = D["swiat"][gra_]["final"]
    O = D["ui"]["kamera"]["final"]
    gx, gy, gz = korzen[0], korzen[1] - O["korzen_nad_ziemia"], korzen[2]
    kier = kierunek_finalu(D, gra_, czas)
    d = F["dystans"] * (1 + O["dojazd"] * (1 - wyjscie(czas / O["dojazd_s"])))
    oko = [gx + kier[0] * d, gy + F["wysokosc"], gz + kier[2] * d]
    c0 = [gx, gy + F["cel_wysokosc"], gz]
    vx, vy, vz = c0[0] - oko[0], c0[1] - oko[1], c0[2] - oko[2]
    d0 = math.sqrt(vx * vx + vy * vy + vz * vz)
    h = math.sqrt(vx * vx + vz * vz)
    rx, rz = -vz / h, vx / h
    t = (1 - 2 * fx) * math.tan(math.radians(F["kat"]) / 2) * aspekt
    return {"oko": oko, "cel": [c0[0] + rx * d0 * t, c0[1], c0[2] + rz * d0 * t], "kat": F["kat"]}


def zawezenie(D, rodzaj, wiek):
    p = D["ui"]["kamera"].get(rodzaj)
    if p is None or wiek < 0 or wiek >= p["czas_s"]:
        return 0
    u = 1 - wiek / p["czas_s"]
    return p["kat"] * u * u


def wstrzas(D, sila, wiek):
    amp = sila * math.exp(-wiek * D["ui"]["kamera"]["wstrzas_zanik"])
    if amp < 0.004:
        return 0
    return amp


def kat_okna(kat, wsp):
    return math.degrees(2 * math.atan(math.tan(math.radians(kat) / 2) * wsp))


# ------------------------------------------------------------------------------------------------ tylko Python
def najwieksze_zawezenie(D):
    """Największe zawężenie kąta widzenia w czasie gry (stopnie) — test 5e rzutuje pole gry także z nim."""
    KA = D["ui"]["kamera"]
    return max(KA[k]["kat"] for k in ("uderzenie", "mocne", "seria"))


def rzut(u, p, vw, vh, kat=None):
    """Punkt świata → piksel ekranu vw × vh dla ujęcia u (CFrame.lookAt(oko, cel), kąt pionowy); None = za kamerą."""
    oko, cel = u["oko"], u["cel"]
    kat = u["kat"] if kat is None else kat
    f = [cel[i] - oko[i] for i in range(3)]
    d = math.sqrt(sum(x * x for x in f))
    f = [x / d for x in f]
    r = [-f[2], 0.0, f[0]]
    d = math.sqrt(sum(x * x for x in r))
    r = [x / d for x in r]
    g = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    q = [p[i] - oko[i] for i in range(3)]
    z = sum(q[i] * f[i] for i in range(3))
    if z <= 0.1:
        return None
    k = (vh / 2) / math.tan(math.radians(kat / 2))
    return vw / 2 + sum(q[i] * r[i] for i in range(3)) / z * k, vh / 2 - sum(q[i] * g[i] for i in range(3)) / z * k


def miejsca_postaci(D, gra_):
    """Punkty na ziemi, w których może stać postać gracza na stanowisku (Koniczyny: trzy tory; Bieżnia: na taśmie)."""
    W = D["swiat"][gra_]
    pd = W["podest"]
    if gra_ == "kondycja":
        return [[pd[0], W["tasma_srodek"][1] + W["tasma_rozmiar"][1] / 2, pd[2]]]
    if gra_ == "szczescie":
        return [list(p) for p in W["tory"].values()]
    return [list(pd)]


def karta_podsumowania(D, gw, gh, s, panel=(400, 244)):
    """Prostokąt karty podsumowania w obszarze GUI (x0, y0, x1, y1): przy prawej krawędzi, w połowie wysokości —
    tak ustawia ją klient (odswiezSkale), żeby lewa część ekranu została dla postaci."""
    m = D["ui"]["komiks"]["karta"]["margines_px"]
    w, h = panel[0] * s, panel[1] * s
    return [gw - m - w, gh / 2 - h / 2, gw - m, gh / 2 + h / 2]


def ulamek_postaci(D, gx0, gw, vw, s, panel=(400, 244)):
    """Ułamek szerokości widoku, w którym ma stać postać w zbliżeniu: środek wolnego pasa na lewo od karty."""
    lewa = karta_podsumowania(D, gw, 100, s, panel)[0]
    return (gx0 + lewa * D["ui"]["kamera"]["final"]["postac_w_wolnym"]) / vw
