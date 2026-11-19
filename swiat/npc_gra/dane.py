#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane postaci niezależnych w grze (D-109) → zrodla/DaneNpc.luau i zrodla/rigi/Rig_<id>.luau (wygenerowane).

    python -B swiat/npc_gra/dane.py              # zapisuje pliki, które się zmieniły, i wypisuje tabelę obsady
    python -B swiat/npc_gra/dane.py --sprawdz    # kod 1, gdy któryś plik jest nieaktualny (nic nie zapisuje)
    python -B swiat/npc_gra/dane.py --tabela     # sama tabela obsady i rachunek kosztu (nic nie zapisuje)

Źródła (tylko odczyt): ustawienia.json; moduły postaci swiat/postacie/<moduł>.py (bryły, kości, klipy — rozkład na
części Roblox: swiat/postacie/biblioteka/roblox_klocki.rig, próbki klipów liniowo między kluczami, bez Blendera);
pakiet bazaru: swiat/miasteczko_bazar_gra/miejsca.json (pole „npc” miejsca = kto tam stoi; nazwa i rola do tabliczki),
swiat/miasteczko_bazar/znaczniki.json (Model figury), swiat/miasteczko_bazar/czesci.json (część „Korzeń” figury =
stopy i kierunek). Żadnych liczb położeń w kodzie. Status: propozycja.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ZRODLA = os.path.join(TU, "zrodla")
RIGI = os.path.join(ZRODLA, "rigi")
PLIK_DANYCH = "DaneNpc.luau"
LOGICZNE = ("spoczynek", "powitanie", "gest")


class BladDanych(Exception):
    pass


def czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return json.load(f)


def sciezka_repo(wzgledna):
    return os.path.join(REPO, *wzgledna.split("/"))


def ustawienia():
    return czytaj_json(os.path.join(TU, "ustawienia.json"))


def _r(v, n=3):
    x = round(float(v), n)
    return 0 if x == 0 else x


def wpis_npc(U, nid):
    w = next((x for x in U["npc"] if x["id"] == nid), None)
    if w is None:
        raise BladDanych("nieznany NPC %r (ustawienia.json → npc)" % nid)
    return w


def klipy_npc(U, wpis):
    k = dict(U["klipy_domyslne"])
    k.update(wpis.get("klipy") or {})
    return k


# ------------------------------------------------------------------------------------------------ rig z klocków
def postac_modulu(wpis):
    """Postać z modułu swiat/postacie/<moduł>.py (ta sama droga co swiat/postacie/roblox_postac.py)."""
    from swiat.postacie.roblox_postac import postacie_z_modulu
    sciezka = os.path.join(REPO, "swiat", "postacie", wpis["modul"] + ".py")
    p = next((x for x in postacie_z_modulu(sciezka) if x.id == wpis["postac"]), None)
    if p is None:
        raise BladDanych("brak postaci %s w swiat/postacie/%s.py" % (wpis["postac"], wpis["modul"]))
    bledy, _uwagi = p.sprawdz()
    if bledy:
        raise BladDanych("postać %s: %s" % (wpis["id"], "; ".join(bledy)))
    return p


def _macierz(rx, ry, rz):
    """Obrót jak CFrame.fromOrientation (R = Ry · Rx · Rz), kąty w radianach."""
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return ((cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx),
            (cx * sz, cx * cz, -sx),
            (-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx))


def obwiednia(czesci):
    """(min, max) rogów wszystkich brył rigu w spoczynku (układ rigu: początek = ziemia pod postacią)."""
    mn, mx = [math.inf] * 3, [-math.inf] * 3
    for c in czesci:
        R = _macierz(c[6], c[7], c[8])
        for zx in (-0.5, 0.5):
            for zy in (-0.5, 0.5):
                for zz in (-0.5, 0.5):
                    v = (c[9] * zx, c[10] * zy, c[11] * zz)
                    for i in range(3):
                        w = c[3 + i] + R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]
                        mn[i], mx[i] = min(mn[i], w), max(mx[i], w)
    return mn, mx


def rig_npc(U, wpis):
    """Moduł postaci → zwięzły rig dla gry (układ danych jak RigKowal / rigi petów): kosci {nazwa, rodzic, staw xyz,
    środek xyz, rozmiar xyz}; czesci {kość, kształt, nazwa, poz xyz, obrót xyz (rad), rozmiar xyz, kolor, materiał,
    siatka}; klipy {nazwa: {fps, petla, kosci, klatki}} — w wierszu po 6 liczb na kość (przes xyz, obrót xyz)."""
    from swiat.postacie.biblioteka.roblox_klocki import probki_liniowe, rig
    p = postac_modulu(wpis)
    if abs(p.skala - 1.0) > 1e-9:
        raise BladDanych("postać %s ma skalę %s — skala NPC jest daną stanowiska, moduł ma być w skali 1" % (wpis["id"], p.skala))
    d = rig(p, probki_liniowe(p))
    n = int(U["probkowanie"]["miejsca_po_przecinku"])
    krok_ust = int(U["probkowanie"]["co_ile_klatek"])
    kosci = [[k[0], k[1]] + [_r(v, n) for v in k[2:11]] for k in d["kosci"]]
    czesci = [[c[0], c[1], c[2]] + [_r(v, n) for v in c[3:6]] + [_r(v, 4) for v in c[6:9]] + [_r(v, n) for v in c[9:12]]
              + [c[12].upper(), c[13], c[15]] for c in d["czesci"]]
    potrzebne = klipy_npc(U, wpis)
    klipy = {}
    for kl in d["klipy"]:
        if kl["n"] not in potrzebne.values():
            continue
        krok = krok_ust if kl["dl"] % krok_ust == 0 else 1
        klatki = [[_r(v, n) for v in kl["klatki"][f]] for f in range(0, kl["dl"] + 1, krok)]
        klipy[kl["n"]] = {"fps": kl["fps"] / krok, "petla": kl["petla"], "kosci": kl["kosci"], "klatki": klatki}
    for rola, nazwa in potrzebne.items():
        if nazwa not in klipy:
            raise BladDanych("postać %s nie ma klipu %s (%s)" % (wpis["id"], nazwa, rola))
    nazwy = [k[0] for k in kosci]
    for wymagana in ("Head", "UpperTorso"):
        if wymagana not in nazwy:
            raise BladDanych("postać %s nie ma kości %s (wzrok)" % (wpis["id"], wymagana))
    mn, mx = obwiednia(d["czesci"])
    glowa = nazwy.index("Head") + 1
    _, mx_glowy = obwiednia([c for c in d["czesci"] if c[0] == glowa] or d["czesci"])
    return {"id": wpis["id"], "nazwa": p.nazwa, "skala": 1, "hrp": [_r(v, n) for v in d["hrp"]], "kosci": kosci,
            "czesci": czesci, "materialy": d["materialy"], "klipy": klipy, "wysokosc": _r(mx[1]), "spod": _r(mn[1]),
            "czubek_glowy": _r(mx_glowy[1]),
            "szerokosc": _r(mx[0] - mn[0]), "glebokosc": _r(mx[2] - mn[2]),
            "glowa": glowa, "tulow": nazwy.index("UpperTorso") + 1, "uwagi": d["uwagi"]}


def dlugosc_klipu(rig, nazwa):
    kl = rig["klipy"][nazwa]
    return (len(kl["klatki"]) - 1) / kl["fps"]


# ------------------------------------------------------------------------------------------------ bazar
def _znajdz(zn, sciezka):
    """Element znaczników bazaru po ścieżce „a/b”: w liście element o tym id, w słowniku klucz."""
    o = zn
    for kawalek in sciezka.split("/"):
        if isinstance(o, list):
            pas = [x for x in o if isinstance(x, dict) and x.get("id") == kawalek]
            if len(pas) != 1:
                raise BladDanych("znacznik %s: %d elementów o id %r" % (sciezka, len(pas), kawalek))
            o = pas[0]
        elif isinstance(o, dict) and kawalek in o:
            o = o[kawalek]
        else:
            raise BladDanych("znacznik %s: brak %r" % (sciezka, kawalek))
    return o


def stanowiska_bazaru(U):
    """Stanowiska NPC w bazarze: kto (pole „npc” miejsca bazaru), gdzie (część „Korzeń” figury z mapy), jak duży."""
    B = U["bazar"]
    M = czytaj_json(sciezka_repo(B["miejsca"]))
    ZN = czytaj_json(sciezka_repo(B["znaczniki"]))
    CZ = czytaj_json(sciezka_repo(B["czesci"]))
    grupy = CZ["grupy"]
    ustaw = {k: v for k, v in U["stanowiska_bazaru"].items() if k != "opis"}
    wynik = []
    for m in M["miejsca"]:
        if not m.get("npc"):
            continue
        mid = m["id"]
        wpis_npc(U, m["npc"])
        if mid not in ustaw:
            raise BladDanych("miejsce bazaru %s ma NPC %s, ale nie ma go w ustawienia.json → stanowiska_bazaru" % (mid, m["npc"]))
        z = _znajdz(ZN, m["znacznik"])
        model = z.get("model")
        if not model or model not in grupy:
            raise BladDanych("miejsce bazaru %s: brak Modelu figury w znacznikach albo w czesci.json" % mid)
        gi = grupy.index(model)
        figura = [c for c in CZ["czesci"] if grupy[c[1]] == model or grupy[c[1]].startswith(model + "/")]
        korzenie = [c for c in CZ["czesci"] if c[1] == gi and c[14] == B["czesc_korzenia"]]
        if len(korzenie) != 1:
            raise BladDanych("miejsce bazaru %s: %d części „%s” w %s" % (mid, len(korzenie), B["czesc_korzenia"], model))
        k = korzenie[0]
        sf = k[8] / B["korzen_bok"]
        kx, kz = math.sin(k[6]), math.cos(k[6])
        u = ustaw[mid]
        px, py, pz = u.get("przesun", [0, 0, 0])
        stopy = [k[2] + kz * px + kx * pz, k[3] - B["korzen_nad_stopami"] * sf + py, k[4] - kx * px + kz * pz]
        czubek = max(c[3] + c[9] / 2 for c in figura if c[13] < 1.0)        # z grubsza: bez obrotów części
        wynik.append({"klucz": mid, "npc": m["npc"], "poz": [_r(v) for v in stopy], "kier": [_r(kx, 4), _r(kz, 4)],
                      "skala": u["skala"], "zastepuje": model, "rola": "%s · %s" % (m["obiekt"], m["akcja_tekst"]),
                      "figura_czesci": len(figura), "figura_skala": _r(sf), "figura_czubek": _r(czubek - stopy[1], 2),
                      "podpowiedz": [_r(v) for v in z["podpowiedz"]], "stoisko": [_r(v) for v in z["stoisko"]]})
    brak = sorted(set(ustaw) - {s["klucz"] for s in wynik})
    if brak:
        raise BladDanych("stanowiska_bazaru bez pola „npc” w miejscach bazaru: %s" % ", ".join(brak))
    return wynik


def skale(U, stanowiska=None):
    """{id NPC: skala w grze} — bazar ze stanowisk, trenerzy mini-gier z ustawień (golem osobno), reszta 1."""
    w = {n["id"]: 1.0 for n in U["npc"]}
    for s in (stanowiska if stanowiska is not None else stanowiska_bazaru(U)):
        w[s["npc"]] = float(s["skala"])
    T = U["trenerzy"]
    for nid in T["gry"].values():
        w[nid] = float(T["skala_golema"] if nid == "golem" else T["skala"])
    return w


_CZYTAJ_TRENING = r"""
import importlib.util, json, os, sys
sys.dont_write_bytecode = True
sciezka = sys.argv[1]
sys.path.insert(0, os.path.dirname(sciezka))
spec = importlib.util.spec_from_file_location("dane_treningu", sciezka)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
D = m.dane_z_przypadkami()[-1]
sys.stdout.buffer.write(json.dumps({"kontener": D["kontener"], "skrot": D.get("skrot"),
    "trenerzy": {g: s["trener_npc"] for g, s in D["swiat"].items() if isinstance(s, dict) and "trener_npc" in s}},
    ensure_ascii=False).encode("utf-8"))
"""


def punkty_trenerow(U=None):
    """Punkty trenerów mini-gier z danych pakietu treningu (tylko odczyt, w osobnym procesie) → lista stanowisk:
    gra, npc, klucz, poz (stopy, świat), patrz (x, z), skala, zastepuje (pełna ścieżka figury albo None), zostaw
    (części figury, które zostają widoczne), kontener i skrót danych treningu."""
    import subprocess
    U = U or ustawienia()
    T = U["trenerzy"]
    r = subprocess.run([sys.executable, "-B", "-c", _CZYTAJ_TRENING, sciezka_repo(T["zrodlo"])], capture_output=True)
    if r.returncode != 0:
        raise BladDanych("nie udało się wczytać punktów trenerów z %s: %s" % (T["zrodlo"], r.stderr.decode("utf-8", "replace")[-300:]))
    Tr = json.loads(r.stdout.decode("utf-8"))
    brak = sorted(set(T["gry"]) - set(Tr["trenerzy"]))
    if brak:
        raise BladDanych("pakiet treningu nie ma punktu trenera dla gier: %s" % ", ".join(brak))
    S = skale(U, [])
    wynik = []
    for gra, nid in T["gry"].items():
        p = Tr["trenerzy"][gra]
        wpis_npc(U, nid)
        figura = p.get("figura")
        wynik.append({"gra": gra, "npc": nid, "klucz": T["klucz"] % gra, "poz": [_r(v) for v in p["miejsce"]],
                      "patrz": [_r(p["patrz"][0]), _r(p["patrz"][2])],
                      "skala": float(T.get("skale_gier", {}).get(gra, S[nid])),
                      "zastepuje": "Workspace/%s/%s" % (Tr["kontener"], figura) if figura else None,
                      "zostaw": list(T.get("zostaw", {}).get(gra, [])), "kontener": Tr["kontener"], "skrot": Tr.get("skrot")})
    return wynik


# ------------------------------------------------------------------------------------------------ dane całe
def wszystko():
    """→ (U, D, R): ustawienia, dane dla DaneNpc.luau, rigi {id: rig} tylko dla NPC budowanych w grze."""
    U = ustawienia()
    stan = stanowiska_bazaru(U)
    S = skale(U, stan)
    R, npc, kolejnosc = {}, {}, []
    for w in U["npc"]:
        nid = w["id"]
        if nid in npc:
            raise BladDanych("powtórzone id NPC %r" % nid)
        kl = klipy_npc(U, w)
        wpis = {"id": nid, "imie": w["imie"], "rola": w["rola"], "powitanie": w.get("powitanie", ""), "klipy": kl,
                "gest_razy": int(w.get("gest_razy", 1)), "skala": S[nid]}
        if w.get("rig_w_grze", True):
            r = rig_npc(U, w)
            R[nid] = r
            wpis.update({"rig": "Rig_" + nid, "wysokosc": r["wysokosc"], "czubek": r["czubek_glowy"],
                         "bryl": len(r["czesci"]),
                         "dlugosci": {rola: _r(dlugosc_klipu(r, kl[rola]) * (wpis["gest_razy"] if rola == "gest" else 1))
                                      for rola in LOGICZNE}})
        npc[nid] = wpis
        kolejnosc.append(nid)
    for s in stan:
        if s["npc"] not in R:
            raise BladDanych("stanowisko %s: NPC %s nie ma rigu w grze" % (s["klucz"], s["npc"]))
    T = U["trenerzy"]
    for gra, nid in T["gry"].items():
        if nid not in R:
            raise BladDanych("trener gry %s: NPC %s nie ma rigu" % (gra, nid))
    W = U["wzrok"]
    rad = math.radians
    D = {
        "wersja": 1,
        "kontener": U["kontener"], "prefiks": U["prefiks"], "wylacznik": U["wylacznik"],
        "folder_lokalny": U["folder_lokalny"], "tag_kotwicy": U["tag_kotwicy"],
        "zasiegi": {k: v for k, v in U["zasiegi"].items() if k != "opis"},
        "czasy": {k: v for k, v in U["czasy"].items() if k != "opis"},
        "wzrok": {"glowa_maks": _r(rad(W["glowa_maks"]), 4), "tulow_maks": _r(rad(W["tulow_maks"]), 4),
                  "tulow_udzial": W["tulow_udzial"], "pochyl_maks": _r(rad(W["pochyl_maks"]), 4),
                  "za_plecami": _r(rad(W["za_plecami"]), 4), "zasieg": W["zasieg"], "tempo": W["tempo"],
                  "wysokosc_oczu": W["wysokosc_oczu"]},
        "tabliczka": {k: v for k, v in U["tabliczka"].items() if k != "opis"},
        "npc": npc, "kolejnosc": kolejnosc,
        "stanowiska": [{k: s[k] for k in ("klucz", "npc", "poz", "kier", "skala", "zastepuje", "rola")} for s in stan],
        "obce": [{k: o[k] for k in ("klucz", "npc", "model", "dol", "przod") if k in o} for o in U["obce_modele"]],
        "trenerzy": {"skala": T["skala"], "skala_golema": T["skala_golema"], "gry": dict(T["gry"])},
    }
    for o in D["obce"]:
        wpis_npc(U, o["npc"])
    D["skrot"] = skrot(D, R)
    return U, D, R


def skrot(D, R):
    bez = {k: v for k, v in D.items() if k != "skrot"}
    tekst = json.dumps([bez, R], sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]


def czesci_w_studio(rig):
    """Ile części BasePart ma jeden NPC u klienta: bryły + niewidzialne części kości + korzeń + tabliczka."""
    return len(rig["czesci"]) + len(rig["kosci"]) + 2


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
          "or", "repeat", "return", "then", "true", "until", "while", "continue", "type", "export"}
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '


def _napis(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    r = repr(float(x))
    return r[:-2] if r.endswith(".0") else r


def luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        czesci = [luau(x, wciecie + 1) for x in v]
    elif isinstance(v, dict):
        czesci = ["%s = %s" % (k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k), luau(x, wciecie + 1))
                  for k, x in v.items() if x is not None]
    else:
        raise TypeError(repr(v))
    jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
    if len(jedna) <= 110 and "\n" not in jedna:
        return jedna
    if isinstance(v, (list, tuple)) and all(isinstance(x, (int, float, str)) for x in v):
        return jedna                                            # wiersz liczb (klatka, bryła) zawsze w jednej linii
    return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"


def tekst_danych(D):
    return ("--[[\n\tDaneNpc — WYGENEROWANE przez swiat/npc_gra/dane.py z ustawienia.json, modułów postaci (swiat/postacie)\n"
            "\ti pakietu bazaru (miejsca.json, znaczniki.json, czesci.json). NIE EDYTUJ RĘCZNIE: zmień źródło i uruchom\n"
            "\tpython -B swiat/npc_gra/dane.py. Kąty wzroku w radianach. Skrót danych: %s. Status: propozycja (D-109).\n]]\n"
            % D["skrot"]) + STRAZNIK + luau(D) + "\n"


def tekst_rigu(r):
    bez = {k: v for k, v in r.items() if k not in ("uwagi", "szerokosc", "glebokosc", "czubek_glowy", "spod")}
    return ("--[[\n\tRig_%s — rig z klocków postaci „%s” (skala 1), WYGENEROWANY przez swiat/npc_gra/dane.py z modułu\n"
            "\tswiat/postacie. Układ rigu Roblox (przód −Z, początek = ziemia pod postacią). kosci: {nazwa, rodzic, staw xyz,\n"
            "\tśrodek xyz, rozmiar xyz}; czesci: {kość, kształt, nazwa, poz xyz, obrót xyz (rad), rozmiar xyz, kolor,\n"
            "\tmateriał, siatka}; klipy: klatki co 1/fps s, w wierszu po 6 liczb na kość z listy kosci (przes xyz,\n"
            "\tobrót xyz). NIE EDYTUJ RĘCZNIE.\n]]\n" % (r["id"], r["nazwa"])) + STRAZNIK + luau(bez) + "\n"


def wszystkie_pliki():
    """→ (U, D, R, {ścieżka względna w zrodla/: tekst})."""
    U, D, R = wszystko()
    pliki = {PLIK_DANYCH: tekst_danych(D)}
    for nid, r in R.items():
        pliki["rigi/Rig_%s.luau" % nid] = tekst_rigu(r)
    return U, D, R, pliki


def _czytaj(sciezka):
    if not os.path.isfile(sciezka):
        return None
    with open(sciezka, encoding="utf-8") as f:
        return f.read()


def nieaktualne(pliki):
    zle = [n for n, t in pliki.items() if _czytaj(os.path.join(ZRODLA, *n.split("/"))) != t]
    if os.path.isdir(RIGI):
        zle += ["rigi/" + n + " (zbędny)" for n in sorted(os.listdir(RIGI)) if "rigi/" + n not in pliki]
    return zle


def zapisz(pliki):
    os.makedirs(RIGI, exist_ok=True)
    zmienione = []
    for n, t in pliki.items():
        sciezka = os.path.join(ZRODLA, *n.split("/"))
        if _czytaj(sciezka) != t:
            with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
                f.write(t)
            zmienione.append(n)
    for n in sorted(os.listdir(RIGI)):
        if "rigi/" + n not in pliki:
            os.remove(os.path.join(RIGI, n))
            zmienione.append("rigi/" + n + " (usunięty)")
    return zmienione


def tabela(U, D, R, pliki):
    linie = ["%-20s %-9s %-22s %5s %7s %6s  %s" % ("NPC", "imię", "rola", "bryły", "części", "czubek", "klipy (s)")]
    for nid in D["kolejnosc"]:
        n = D["npc"][nid]
        if nid not in R:
            linie.append("%-20s %-9s %-22s %5s %7s %6s  %s" % (nid, n["imie"], n["rola"], "—", "—", "—",
                                                              "rig i klipy w swoim pakiecie (tu tylko tabliczka)"))
            continue
        r = R[nid]
        linie.append("%-20s %-9s %-22s %5d %7d %6.2f  %s" % (
            nid, n["imie"], n["rola"], len(r["czesci"]), czesci_w_studio(r), r["czubek_glowy"],
            ", ".join("%s=%s %.2f" % (rola, n["klipy"][rola], n["dlugosci"][rola]) for rola in LOGICZNE)))
    linie.append("")
    linie.append("stanowiska w bazarze (miejsce → NPC, skala, stopy, zastępuje figurę):")
    figury = 0
    for s in stanowiska_bazaru(U):
        figury += s["figura_czesci"]
        r = R[s["npc"]]
        linie.append("  %-16s %-12s ×%.2f  czubek głowy %.2f (figura ok. %.2f)  stopy (%.1f; %.2f; %.1f)  %s [%d części figury]" % (
            s["klucz"], s["npc"], s["skala"], r["czubek_glowy"] * s["skala"], s["figura_czubek"], s["poz"][0], s["poz"][1],
            s["poz"][2], s["zastepuje"].split("/", 2)[-1], s["figura_czesci"]))
    w_bazarze = [R[s["npc"]] for s in stanowiska_bazaru(U)]
    linie.append("")
    linie.append("rachunek: bazar %d NPC = %d brył, %d części u klienta (figury z klocków, które zastępują: %d części); "
                 "wszystkie %d rigów = %d brył" % (len(w_bazarze), sum(len(r["czesci"]) for r in w_bazarze),
                                                    sum(czesci_w_studio(r) for r in w_bazarze), figury, len(R),
                                                    sum(len(r["czesci"]) for r in R.values())))
    rozmiary = {n: len(t) for n, t in pliki.items()}
    linie.append("źródła danych: %s %d znaków; rigi %d–%d znaków (limit jednego modułu %d), razem %d kB" % (
        PLIK_DANYCH, rozmiary[PLIK_DANYCH], min(v for k, v in rozmiary.items() if k != PLIK_DANYCH),
        max(v for k, v in rozmiary.items() if k != PLIK_DANYCH), U["limit_zrodla"], sum(rozmiary.values()) // 1000))
    return linie


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dane NPC w grze → zrodla/DaneNpc.luau i zrodla/rigi/")
    ap.add_argument("--sprawdz", action="store_true", help="kod 1, gdy pliki w zrodla/ są nieaktualne")
    ap.add_argument("--tabela", action="store_true", help="tylko tabela obsady i rachunek (nic nie zapisuje)")
    a = ap.parse_args()
    try:
        U, D, R, pliki = wszystkie_pliki()
    except BladDanych as e:
        print("BŁĄD danych: %s" % e)
        return 2
    za_duze = [n for n, t in pliki.items() if len(t) > U["limit_zrodla"]]
    if za_duze:
        print("BŁĄD: za duże źródła (limit %d znaków): %s" % (U["limit_zrodla"], ", ".join(za_duze)))
        return 2
    if a.sprawdz:
        zle = nieaktualne(pliki)
        print("dane NPC: %s (skrót %s, NPC %d, rigów %d, stanowisk w bazarze %d)" % (
            "aktualne" if not zle else "NIEAKTUALNE (%s) — uruchom python -B swiat/npc_gra/dane.py" % ", ".join(zle),
            D["skrot"], len(D["kolejnosc"]), len(R), len(D["stanowiska"])))
        return 1 if zle else 0
    if not a.tabela:
        zm = zapisz(pliki)
        print("dane NPC %s (skrót %s)" % ("zapisane: " + ", ".join(zm) if zm else "bez zmian", D["skrot"]))
    print("\n".join(tabela(U, D, R, pliki)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
