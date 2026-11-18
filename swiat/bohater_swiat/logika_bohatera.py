# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaBohatera.luau w Pythonie (testy: te same wyniki w interpreterze luau_mini i tutaj).

Zasady (PROJEKT.md, „przyjęte, do zmiany”):
- klasa bohatera z atrybutu gracza Class (mapa D["klasy_gracza"]); bez klasy bohatera nie ma;
- automat ruchu: martwy → upadek; klip wymuszony umową RuchBohatera ma pierwszeństwo przed ruchem postaci; lot
  (skok / spadanie) dopiero po R["min_czas_w_powietrzu_s"] w powietrzu (zejście ze schodka nie jest skokiem) albo od
  razu przy stanie Jumping; po locie krótkie lądowanie; na ziemi chód / spoczynek z histerezą prędkości;
- tempo klipu chodu = prędkość pozioma / prędkość naturalna klipu, w granicach tempo_min…tempo_max;
- wagi póz proceduralnych idą liniowo do celu w czasie z danych.
Słowniki `pam` i `wym` są zmieniane w miejscu, jak tabele w Luau.
"""
import math

W_POWIETRZU = ("Jumping", "Freefall")
BEZ_POWIETRZA = ("Climbing", "Swimming", "Seated")


def _ogranicz(x, a, b):
    return max(a, min(b, x))


def klasa(D, i):
    if not isinstance(i, str):
        return None
    k = D["klasy_gracza"].get(i)
    return k if k is not None and k in D["klasy"] else None


def klucz_stroju(napis):
    return napis if isinstance(napis, str) else "~"


def tempo(v, naturalna, R):
    if naturalna <= 0:
        return 1
    return _ogranicz(v / naturalna, R["tempo_min"], R["tempo_max"])


def pochylenie(v, R):
    return _ogranicz((v - R["pochylenie_od"]) / (R["pochylenie_do"] - R["pochylenie_od"]), 0, 1)


def nowa_pamiec():
    return {"tryb": "idle", "wPowietrzu": 0, "naZiemi": 0, "ladowanie": 0, "idzie": False, "lot": False, "biegnie": False,
            "spada": False}


def krok(pam, we, R, dt, B=None):
    """B = D["klasy"][klasa]["bieg"] (cykl biegu klasy) albo None — wtedy biegu nie ma, zostaje klip chodu."""
    if not we.get("zyje"):
        pam.update(tryb="upadek", wPowietrzu=0, naZiemi=0, ladowanie=0, idzie=False, lot=False, biegnie=False, spada=False)
        return {"tryb": "upadek", "baza": "upadek", "petla": False, "v": 0}
    w = we.get("wymuszony")
    if w is not None:
        pam.update(tryb=w, wPowietrzu=0, naZiemi=0, ladowanie=0, idzie=False, lot=False, biegnie=False, spada=False)
        if w == "bieg":
            if B is not None:
                return {"tryb": w, "baza": "spoczynek", "petla": True, "v": R["bieg_predkosc"], "bieg": True}
            return {"tryb": w, "baza": "ruch", "petla": True, "v": R["bieg_predkosc"]}
        if w == "radosc":
            return {"tryb": w, "baza": "radosc", "petla": False, "v": 0}
        return {"tryb": w, "baza": "spoczynek", "petla": True, "poza": w, "v": 0}
    stan = we.get("stan")
    if we.get("zdalny"):
        powietrze = stan in W_POWIETRZU or abs(we["vpion"]) > R["prog_pionu_zdalny"]
    else:
        powietrze = stan in W_POWIETRZU or (not we.get("naZiemi") and stan not in BEZ_POWIETRZA)
    if powietrze:
        pam["wPowietrzu"] += dt
        pam["naZiemi"] = 0
    else:
        pam["naZiemi"] += dt
        pam["wPowietrzu"] = 0
    if powietrze and (stan == "Jumping" or pam["wPowietrzu"] >= R["min_czas_w_powietrzu_s"]):
        pam["lot"] = True
    if pam["lot"] and not powietrze and pam["naZiemi"] >= R["min_czas_na_ziemi_s"]:
        pam["lot"] = False
        pam["ladowanie"] = R["czas_ladowania_s"]
    if pam["lot"]:
        pam["ladowanie"] = 0
        prog = R["prog_ponownego_wznoszenia"] if pam["spada"] else R["prog_wznoszenia"]
        tryb = "skok" if we["vpion"] > prog else "spadanie"
        pam["spada"] = tryb == "spadanie"
        pam["tryb"] = tryb
        return {"tryb": tryb, "baza": "spoczynek", "petla": True, "poza": tryb, "v": 0}
    pam["spada"] = False
    v = we["vpoz"]
    if stan == "Climbing":
        v = max(v, abs(we["vpion"]))
    elif stan == "Swimming":
        v = math.sqrt(we["vpoz"] * we["vpoz"] + we["vpion"] * we["vpion"])
    elif stan == "Seated":
        v = 0
    if pam["idzie"]:
        if v < R["prog_ruchu_stop"]:
            pam["idzie"] = False
    elif v > R["prog_ruchu_start"]:
        pam["idzie"] = True
    if B is None or not pam["idzie"]:
        pam["biegnie"] = False
    elif pam["biegnie"]:
        if v < B["vDo"]:
            pam["biegnie"] = False
    elif v > B["vOd"]:
        pam["biegnie"] = True
    baza = "ruch" if pam["idzie"] and not pam["biegnie"] else "spoczynek"
    wynik = {"baza": baza, "petla": True, "v": v}
    if pam["biegnie"]:
        wynik["bieg"] = True
    if pam["ladowanie"] > 0:
        pam["ladowanie"] = max(0, pam["ladowanie"] - dt)
        pam["tryb"] = "ladowanie"
        wynik.update(tryb="ladowanie", poza="ladowanie")
        return wynik
    pam["tryb"] = "bieg" if pam["biegnie"] else ("chod" if pam["idzie"] else "idle")
    wynik["tryb"] = pam["tryb"]
    return wynik


# ------------------------------------------------------------------ proceduralny cykl biegu (opis w LogikaBohatera.luau)
def kadencja(B, v):
    """(kadencja [cykli/s], udział podporu w cyklu) dla prędkości poziomej v."""
    f = _ogranicz(v * B["podpor"] / B["krok"], B["kadencjaMin"], B["kadencjaMaks"])
    d = B["podpor"]
    if v > 0:
        d = min(B["podpor"], B["krok"] * f / v)
    return f, max(B["podporMin"], d)


def czas_biegu(dt, droga, v, w_miejscu):
    """Czas, o który przesuwa się cykl biegu w tej klatce: z drogi postaci (w miejscu i przy v < 1 — z zegara)."""
    if w_miejscu or v < 1:
        return dt
    return min(droga / v, 3 * dt)


def faza_biegu(faza, f, dt):
    n = faza + f * dt
    return n - math.floor(n)


def _noga_ik(B, przod, wys):
    r = math.sqrt(przod * przod + wys * wys)
    maks = (B["udo"] + B["lydka"]) * 0.999
    if r > maks:
        przod = przod * maks / r
        wys = wys * maks / r
        r = maks
    kolano = math.acos(_ogranicz((B["udo"] * B["udo"] + B["lydka"] * B["lydka"] - r * r) / (2 * B["udo"] * B["lydka"]), -1, 1))
    do_kostki = math.atan2(przod, -wys)
    odchylenie = math.acos(_ogranicz((B["udo"] * B["udo"] + r * r - B["lydka"] * B["lydka"]) / (2 * B["udo"] * r), -1, 1))
    return do_kostki + odchylenie, kolano - math.pi


def tor_kostki(B, fz, d):
    """Tor kostki jednej nogi: (przód względem biodra, wysokość nad ziemią, pochylenie stopy)."""
    if fz < d:
        return B["krok"] / 2 - B["krok"] * (fz / d), B["kostka"], 0
    u = (fz - d) / (1 - d)
    s = math.sin(math.pi * u)
    return -(B["krok"] / 2) * math.cos(math.pi * u), B["kostka"] + B["unoszenie"] * s, B["stopaWymach"] * s


def bieg(B, faza, d):
    biodra = B["kostka"] + B["biodraPodpor"] - B["podskok"] * math.cos(4 * math.pi * (faza - d / 2))
    faza_p = faza + 0.5
    if faza_p >= 1:
        faza_p -= 1
    przod_l, wys_l, stopa_l = tor_kostki(B, faza, d)
    przod_p, wys_p, stopa_p = tor_kostki(B, faza_p, d)
    udo_l, lydka_l = _noga_ik(B, przod_l, wys_l - biodra)
    udo_p, lydka_p = _noga_ik(B, przod_p, wys_p - biodra)
    c = math.cos(2 * math.pi * faza)
    return {"biodraY": biodra - B["biodro"],
            "udoL": udo_l, "lydkaL": lydka_l, "stopaL": stopa_l - udo_l - lydka_l,
            "udoP": udo_p, "lydkaP": lydka_p, "stopaP": stopa_p - udo_p - lydka_p,
            "rekaL": -B["rekaL"] * c, "rekaP": B["rekaP"] * c,
            "skret": B["skret"] * math.sin(2 * math.pi * faza)}


def krok_wag(wagi, cele, dt, czasy, kolejnosc):
    for nazwa in kolejnosc:
        cel = cele.get(nazwa) or 0
        w = wagi.get(nazwa) or 0
        czas = czasy.get(nazwa) or 0
        k = dt / czas if czas > 0 else 1
        if w < cel:
            w = min(cel, w + k)
        elif w > cel:
            w = max(cel, w - k)
        if w <= 0:
            wagi.pop(nazwa, None)
        else:
            wagi[nazwa] = w
    return wagi


def pod_stopami(hip, wys_hrp, nogi):
    return hip + wys_hrp / 2 + nogi


def wysokosc_rigu(spod, podniesienie, waga):
    return podniesienie * waga - spod


def przesun(x, y, z, maks):
    for v in (x, y, z):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return 0, 0, 0
    if x != x or y != y or z != z:
        return 0, 0, 0
    try:
        d = math.sqrt(x * x + y * y + z * z)
    except OverflowError:
        d = math.inf
    if d > maks:
        if d == math.inf:
            return 0, 0, 0
        s = maks / d
        return x * s, y * s, z * s
    return x, y, z


def widoczny(odl, byl, W):
    if byl:
        return odl <= W["promien"] * W["histereza"]
    return odl <= W["promien"]


def okres(odl, W):
    return 1 if odl <= W["promien_pelnej_animacji"] else W["okres_daleko"]


def wybierz(kandydaci, maks):
    wynik = {}
    n = 0
    for k in kandydaci:
        if k.get("lokalny") and k["id"] not in wynik:
            wynik[k["id"]] = True
            n += 1
    while n < maks:
        najlepszy = None
        for k in kandydaci:
            if k["id"] not in wynik and (najlepszy is None or k["odl"] < najlepszy["odl"]):
                najlepszy = k
        if najlepszy is None:
            break
        wynik[najlepszy["id"]] = True
        n += 1
    return wynik


def nowy_ruch():
    return {"licznik": 0}


def polecenie_ruchu(D, wym, bohater, polecenie, a=None, x=None, y=None, z=None):
    if polecenie == "stan":
        if bohater is None:
            return None
        return {"aktywny": True, "klasa": bohater["klasa"], "klip": bohater["tryb"], "wymuszony": wym.get("klip")}
    if polecenie == "klip":
        if bohater is None:
            return False
        if a is None:
            wym.pop("klip", None)
            wym["licznik"] += 1
            return True
        if not isinstance(a, str) or a not in D["kontrakt"]["klipy"]:
            return False
        wym["klip"] = a
        wym["licznik"] += 1
        return True
    if polecenie == "przesun":
        if bohater is None:
            return False
        if a is not True:
            for k in ("px", "py", "pz"):
                wym.pop(k, None)
            return True
        wym["px"], wym["py"], wym["pz"] = przesun(x, y, z, D["kontrakt"]["przesun_maks"])
        return True
    return None


def zeruj_ruch(wym):
    for k in ("klip", "px", "py", "pz"):
        wym.pop(k, None)
    wym["licznik"] += 1
    return wym
