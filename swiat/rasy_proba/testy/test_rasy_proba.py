# -*- coding: utf-8 -*-
"""Sprawdzian danych wystawy ras (bez Studio i bez Blendera; kilka sekund).

    python -B swiat/rasy_proba/testy/test_rasy_proba.py

  1. figury: człowiek + sześć ras z swiat/postacie/rasy.py, każda raz, w kolejności z ustawień;
  2. skala i wzrost: skala figury = skala rasy z danych (ork 1,08, goblin 0,88), czubek głowy rigu = 5,30 × skala,
     najniższa bryła stoi na ziemi (y = 0 ± 0,03), kości i stawy R15 (15 kości, każda ze stawem Motor6D);
  3. człowiek = goły Rycerz (te same bryły co rig rycerz.cialo());
  4. świecenie: oczy demona i półboga oraz aureola wychodzą jako materiał Neon;
  5. miejsce: figury nie nachodzą na siebie, środkowa droga jest wolna, wszystkie w zasięgu 40 studów od startu;
  6. nazwy: kontener nie koliduje z kontenerami innych pakietów swiat/, nazwy modeli są różne i ASCII;
  7. źródła Luau: strażnik Studio, po wpisaniu ustawień nie zostaje żadne pole __…__, kontrola statyczna bez błędów;
  8. budowniczy: każdy kod wysyłany do Studio zaczyna od sprawdzenia miejsca gry i trybu Edit, nie dotyka Lighting,
     nie zapisuje i nie publikuje.
"""
import glob
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, PAKIET):
    if _s in sys.path:
        sys.path.remove(_s)
    sys.path.insert(0, _s)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402
from swiat.postacie import rasy, rycerz  # noqa: E402
from swiat.postacie.biblioteka.roblox_klocki import rig  # noqa: E402

U = DN.ustawienia()
F = DN.figury(U)


def test_figury():
    zle = []
    ids = [f["id"] for f in F]
    if ids != [w["id"] for w in U["figury"]] or sorted(ids) != sorted(["czlowiek"] + list(rasy.RASY)):
        zle.append("figury %r — oczekiwany człowiek i sześć ras, każda raz" % ids)
    for f in F:
        if f["id"] != "czlowiek" and f["nazwa"] != rasy.RASY[f["id"]]["nazwa"]:
            zle.append("%s: nazwa %r" % (f["id"], f["nazwa"]))
        if not re.match(r"^[a-z_]+$", f["id"]):
            zle.append("%s: nazwa modelu nie jest ASCII" % f["id"])
    return zle


def test_skala_i_wzrost():
    zle = []
    for f in F:
        skala = 1.0 if f["id"] == "czlowiek" else rasy.RASY[f["id"]]["skala"]
        if f["skala"] != skala or abs(f["wzrost"] - 5.3 * skala) > 1e-6:
            zle.append("%s: skala %r, wzrost %r (dane rasy: %r)" % (f["id"], f["skala"], f["wzrost"], skala))
        glowa = next(k for k in f["kosci"] if k[0] == "Head")
        if abs(glowa[6] + glowa[9] / 2 - f["wzrost"]) > 0.005:
            zle.append("%s: czubek głowy rigu %.3f, oczekiwane %.3f" % (f["id"], glowa[6] + glowa[9] / 2, f["wzrost"]))
        if len(f["kosci"]) != 15 or any(not k[11] for k in f["kosci"]):
            zle.append("%s: kości %d (ma być 15 ze stawami)" % (f["id"], len(f["kosci"])))
        proste = [c for c in f["czesci"] if abs(c[6]) < 1e-6 and abs(c[8]) < 1e-6]      # bez przechyłu
        dol = min(c[4] - c[10] / 2 for c in proste)
        if abs(dol) > 0.03:
            zle.append("%s: najniższa bryła %.3f nad ziemią" % (f["id"], dol))
        if f["uwagi"]:
            zle.append("%s: uwagi rozkładu brył: %s" % (f["id"], "; ".join(f["uwagi"])))
    ork, gob = (next(f for f in F if f["id"] == n) for n in ("ork", "goblin"))
    if not (ork["skala"] == 1.08 and gob["skala"] == 0.88):
        zle.append("skala orka %r i goblina %r" % (ork["skala"], gob["skala"]))
    return zle


def test_czlowiek():
    c = next(f for f in F if f["id"] == "czlowiek")
    wzor = rig(rycerz.cialo())
    return [] if c["czesci"] == wzor["czesci"] and c["kosci"] == wzor["kosci"] else ["człowiek różni się od gołego Rycerza"]


def test_swiecenie():
    zle = []
    for f in F:
        neon = [c[2] for c in f["czesci"] if f["materialy"][c[13]][0] == "Neon"]
        if f["id"] == "demon":
            if len(neon) != 4 or not all(n.startswith(("Oko", "Blysk")) for n in neon):
                zle.append("demon: części Neon %r" % neon)
        elif f["id"] == "polbog":
            if sum(n.startswith("Aureola") for n in neon) != 12 or sum(n.startswith(("Oko", "Blysk")) for n in neon) != 4:
                zle.append("półbóg: części Neon %r" % neon)
        elif neon:
            zle.append("%s: nieoczekiwane części Neon %r" % (f["id"], neon))
        if len(neon) != f["swiecace"]:
            zle.append("%s: licznik świecących %d ≠ %d" % (f["id"], f["swiecace"], len(neon)))
    return zle


def test_miejsce():
    zle = []
    for i, a in enumerate(F):
        d = math.hypot(a["poz"][0] - a["patrz"][0], a["poz"][1] - a["patrz"][1])
        if not 10 <= d <= 40:
            zle.append("%s: %.1f studa od startu (ma być 10–40)" % (a["id"], d))
        if abs(a["poz"][0]) < 4.5:
            zle.append("%s: stoi na środkowej drodze (x = %.1f)" % (a["id"], a["poz"][0]))
        for b in F[i + 1:]:
            if math.hypot(a["poz"][0] - b["poz"][0], a["poz"][1] - b["poz"][1]) < 4.9:
                zle.append("%s i %s stoją bliżej niż 4,9 studa" % (a["id"], b["id"]))
    p = U["wolne_miejsce"]["pudlo"]
    if p[0] < 4.5 or p[1] < 7.0 or p[2] < 4.5:
        zle.append("pudło wolnego miejsca %r jest mniejsze od figury" % p)
    return zle


def test_nazwy():
    zle = []
    for sc in glob.glob(os.path.join(REPO, "swiat", "*", "ustawienia.json")):
        if os.path.dirname(sc) == PAKIET:
            continue
        try:
            with open(sc, encoding="utf-8") as f:
                inny = json.load(f).get("kontener")
        except (ValueError, OSError):
            continue
        if inny == U["kontener"]:
            zle.append("kontener %s ma też pakiet %s" % (inny, os.path.basename(os.path.dirname(sc))))
    if len({f["id"] for f in F}) != len(F) or U["skrypt_spoczynku"] in {f["id"] for f in F}:
        zle.append("nazwy modeli w kontenerze nie są różne")
    return zle


def test_zrodla():
    zle = list(ZB.sprawdz_zrodla())
    tekst = ZB.zrodlo_skryptu(U)
    if re.search(r"__[A-Z]+__", tekst):
        zle.append("w skrypcie spoczynku zostało niewypełnione pole __…__")
    if not tekst.lstrip().startswith("--") or 'if not game:GetService("RunService"):IsStudio() then' not in tekst:
        zle.append("skrypt spoczynku bez strażnika Studio")
    if len(tekst) > 190000:
        zle.append("skrypt spoczynku za długi")
    katy = DN.spoczynek(U)
    if set(katy) != {"UpperTorso", "Head", "LeftUpperArm", "RightUpperArm"} or any(abs(v) > 0.2 for k in katy.values() for v in k):
        zle.append("kąty spoczynku %r" % katy)
    return zle


def test_budowniczy():
    zle = []
    for nazwa in ("START", "FIGURA", "SKRYPT", "USUN"):
        kod = getattr(ZB, nazwa)
        if "game.PlaceId ~= __MIEJSCE__" not in kod.split("local KONTENER")[0] or ":IsRunning()" not in kod.split("local KONTENER")[0]:
            zle.append("%s: brak sprawdzenia miejsca gry albo trybu Edit na początku" % nazwa)
    wszystko = ZB.START + ZB.FIGURA + ZB.SKRYPT + ZB.USUN + ZB.STAN + ZB.zrodlo_skryptu(U)
    for zakazane in ("Lighting", "SavePlace", "PublishToRoblox", "InsertService", "rbxassetid", "MarketplaceService",
                     "TeleportService", "DataStore"):
        if zakazane in wszystko:
            zle.append("w kodzie dla Studio jest „%s”" % zakazane)
    if "SetWaypoint" not in ZB.START or "SetWaypoint" not in ZB.SKRYPT:
        zle.append("brak punktów historii przed budową i po niej")
    if "SetAttribute" in ZB.STAN or "Destroy" in ZB.STAN or "Instance.new" in ZB.STAN:
        zle.append("odczyt stanu coś zmienia")
    return zle


PROBY = (("figury = człowiek i sześć ras", test_figury), ("skala, wzrost, stopy, kości", test_skala_i_wzrost),
         ("człowiek = goły Rycerz", test_czlowiek), ("świecenie jako Neon", test_swiecenie),
         ("miejsce wystawy", test_miejsce), ("nazwy bez kolizji", test_nazwy), ("źródła Luau", test_zrodla),
         ("budowniczy: miejsce gry, tryb Edit, tylko własny kontener", test_budowniczy))

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ok = True
    for opis, proba in PROBY:
        zle = proba()
        ok = ok and not zle
        print("%s: %s" % (opis, "zgodne" if not zle else "NIEZGODNE (%d)" % len(zle)))
        for z in zle[:12]:
            print("   -", z)
    print("WYNIK:", "ZGODNE" if ok else "NIEZGODNE")
    sys.exit(0 if ok else 1)
