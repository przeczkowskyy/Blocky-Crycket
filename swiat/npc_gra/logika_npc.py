# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaNpc.luau w Pythonie (D-109; swiat/npc_gra) — te same funkcje, te same działania w tej samej
kolejności. Test bez Studio (testy/test_npc.py) wykonuje plik Luau interpreterem tools/walka/luau_mini.py i porównuje
wyniki z tym modułem na losowych wywołaniach; na lustrze liczone są też scenariusze (podejście gracza, powitanie,
gesty, usypianie). Stan NPC to słownik o tych samych polach co tabela w Luau.
"""
import math


def _ogranicz(x, a, b):
    return max(a, min(b, x))


def tryb(odl, obecny, Z):
    if odl is None:
        return "brak" if obecny == "brak" else "uspiony"
    if obecny == "brak":
        if odl > Z["budowa"]:
            return "brak"
    elif odl > Z["usuniecie"]:
        return "brak"
    rusza = obecny in ("daleko", "blisko")
    if rusza:
        if odl > Z["uspienie"]:
            return "uspiony"
    elif odl > Z["animacja"]:
        return "uspiony"
    return "blisko" if odl <= Z["blisko"] else "daleko"


def co_ile(t):
    return 1 if t == "blisko" else 2 if t == "daleko" else 0


def nowy_stan(los, C):
    return {"klip": "spoczynek", "zostalo": 0, "do_gestu": C["gest_min_s"] + los * (C["gest_max_s"] - C["gest_min_s"]),
            "powitany": False, "od_powitania": C["powitanie_odstep_s"]}


def krok(stan, odl, dt, los, D, n):
    Z, C = D["zasiegi"], D["czasy"]
    stan["od_powitania"] = min(stan["od_powitania"] + dt, C["powitanie_odstep_s"])
    if stan["klip"] != "spoczynek":
        stan["zostalo"] -= dt
        if stan["zostalo"] <= 0:
            stan["klip"] = "spoczynek"
            stan["zostalo"] = 0
            return "spoczynek"
        return None
    if odl is None:
        return None
    if odl > Z["pozegnanie"]:
        stan["powitany"] = False
    elif odl <= Z["powitanie"] and not stan["powitany"]:
        stan["powitany"] = True
        if stan["od_powitania"] >= C["powitanie_odstep_s"]:
            stan["od_powitania"] = 0
            stan["klip"] = "powitanie"
            stan["zostalo"] = n["dlugosci"]["powitanie"]
            return "powitanie"
    if odl <= Z["gest"]:
        stan["do_gestu"] -= dt
        if stan["do_gestu"] <= 0:
            stan["do_gestu"] = C["gest_min_s"] + los * (C["gest_max_s"] - C["gest_min_s"])
            stan["klip"] = "gest"
            stan["zostalo"] = n["dlugosci"]["gest"]
            return "gest"
    return None


def wymus(stan, rola, n):
    if rola == "spoczynek":
        stan["klip"] = "spoczynek"
        stan["zostalo"] = 0
        return True
    if rola in ("gest", "powitanie") or (rola == "akcja" and n["dlugosci"].get("akcja") is not None):
        stan["klip"] = rola
        stan["zostalo"] = n["dlugosci"][rola]
        return True
    return False


def wzrok(kat, pochyl, poziom, W):
    if poziom > W["zasieg"] or poziom < 0.05 or abs(kat) > W["za_plecami"]:
        return 0, 0, 0
    tulow = _ogranicz(kat * W["tulow_udzial"], -W["tulow_maks"], W["tulow_maks"])
    glowa = _ogranicz(kat - tulow, -W["glowa_maks"], W["glowa_maks"])
    return tulow, glowa, _ogranicz(pochyl, -W["pochyl_maks"], W["pochyl_maks"])


def wygladz(a, cel, dt, tempo):
    return a + (cel - a) * min(1, tempo * dt)


def klatka(t, fps, n, petla):
    ost = n - 1
    if ost <= 0:
        return 0, 0, 0
    f = t * fps
    if petla:
        f = f - math.floor(f / ost) * ost
    elif f >= ost:
        return ost, ost, 0
    if f < 0:
        f = 0
    i0 = math.floor(f)
    return i0, min(i0 + 1, ost), f - i0
