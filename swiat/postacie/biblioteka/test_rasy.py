# -*- coding: utf-8 -*-
"""Sprawdzian ras postaci (bez Blendera i bez Studio; ok. 5 s).

    python -B swiat/postacie/biblioteka/test_rasy.py            # wszystkie próby, kod wyjścia 0 = ZGODNE
    python -B swiat/postacie/biblioteka/test_rasy.py --odciski  # wypisz dzisiejsze odciski bohaterów (do ODCISKI)

Co sprawdza (założenia z swiat/postacie/RASY.md):
  1. dane: sześć ras ma komplet pól, palety i cech głowy, pliki rzutów i ikon istnieją, ścieżki są względne;
  2. ciało: każda z sześciu ras ma kości, stawy, klocki i 18 zaczepów równe ciału człowieka (goły Rycerz
     i goły Zwiadowca), typ ciała „czlowiek”, a skala rasy NIE jest wypieczona w klocki (Postac.skala = 1);
  3. klipy: idle, chod i wiwat rasy mają te same długości, pętle i klucze co do wartości co klipy ciała
     odniesienia człowieka (rycerz.cialo());
  4. ekwipunek: każdy przedmiot „czlowiek” Rycerza i Zwiadowcy daje się założyć na każdą rasę; pełne komplety
     zdejmują strój bazowy (koszulę, spodenki, buty) i włosy, a cechy rasy (twarz, uszy, kły, rogi, ogon) zostają;
  5. moduły rasa_elf i rasa_ork: zbuduj() ma kształt modułu postaci (jedna Postac „rasa_<id>”, bez błędów
     w sprawdz(), pakiet dla Blendera daje się zapisać), warianty() i ekwipunek_json() działają;
  6. istniejący bohaterowie bez zmian: pakiety zbuduj() i cialo() Rycerza, Zwiadowcy i Kota-Maga mają odciski
     sprzed dodania ras (18.11.2026). Po ZAMIERZONEJ zmianie bohatera odśwież słownik ODCISKI (opcja --odciski).
"""
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie import kot_mag, rasa_elf, rasa_ork, rasy, rycerz, zwiadowca  # noqa: E402
from swiat.postacie.biblioteka.postac import Postac, pakiet  # noqa: E402
from swiat.postacie.ekwipunek import ubierz  # noqa: E402

# SHA-256 pakietu dla Blendera: (zbuduj(), cialo()) — stan z 18.11.2026 sprzed dodania ras
ODCISKI = {
    "rycerz": ("3d32919a49d139b8ee967d0a1a13254f713b05af368e1bfe37cf115bf1890767",
               "bc3b6bb0100c8897e7aaaef95cd8e882aafff4c14f59c4c5baec27f2a97f3eab"),
    "zwiadowca": ("4e49e5cd5957f1a3019e7e4cb65a4e45c2a581dc0f6ffd6695c2050bbe053a3e",
                  "023828496354a45f28aa7c792f8353d37139c022d961c02af40a00753a15aaae"),
    "kot_mag": ("223a1b9d82862412d5c051435d34c3f4e13775e75d4b2d782171d7bf4be510fe",
                "0222787feb9a189845091f77963bff4561d722734c702e0a3dec68c80569ed52"),
}
LICZBY = {"rycerz": (17, 18, 11, 97), "zwiadowca": (17, 18, 9, 117), "kot_mag": (23, 20, 11, 85)}  # kości, zaczepy, klipy, bryły
BOHATEROWIE = {"rycerz": rycerz, "zwiadowca": zwiadowca, "kot_mag": kot_mag}
HEX = re.compile(r"^[0-9A-Fa-f]{6}$")
CECHY = ("Ucho", "Kiel", "Szczeka", "Wal brwiowy", "Rog ", "Ogon", "Aureola", "Brew", "Usta")   # początki nazw brył cech


def odcisk(modele):
    return hashlib.sha256(json.dumps(pakiet(list(modele)), sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def odciski_dzis():
    wynik = {}
    for nazwa, m in BOHATEROWIE.items():
        ob = m.zbuduj()
        wynik[nazwa] = (odcisk(ob if isinstance(ob, (list, tuple)) else [ob]), odcisk([m.cialo()]))
    return wynik


def test_dane():
    zle = []
    if tuple(rasy.RASY) != ("elf", "ork", "mroczny_elf", "demon", "goblin", "polbog"):
        zle.append("lista ras: %r" % (tuple(rasy.RASY),))
    for rasa, r in rasy.RASY.items():
        for pole in rasy.POLA_RASY:
            if pole not in r:
                zle.append("%s: brak pola %r" % (rasa, pole))
        for pole in rasy.POLA_GLOWY:
            if pole not in r.get("glowa", {}):
                zle.append("%s: brak cechy głowy %r" % (rasa, pole))
        for pole in rasy.POLA_PALETY:
            if pole not in r.get("paleta", {}):
                zle.append("%s: brak koloru %r" % (rasa, pole))
        for klucz, kolor in r.get("paleta", {}).items():
            if not HEX.match(kolor):
                zle.append("%s: kolor %s = %r nie jest RRGGBB" % (rasa, klucz, kolor))
        if not 0.5 <= float(r.get("skala", 0)) <= 1.5:
            zle.append("%s: skala %r poza 0,5…1,5" % (rasa, r.get("skala")))
        for pole in ("rzut", "ikona", "rzut_wariant2"):
            sc = r.get(pole)
            if sc is None:
                continue
            if os.path.isabs(sc) or ":" in sc or "\\" in sc:
                zle.append("%s: %s nie jest ścieżką względną z ukośnikami „/”: %r" % (rasa, pole, sc))
            elif not os.path.isfile(os.path.join(REPO, sc)):
                zle.append("%s: brak pliku %s" % (rasa, sc))
        g = r.get("glowa", {})
        if g.get("twarz") not in rasy.TWARZE:
            zle.append("%s: nieznana twarz %r" % (rasa, g.get("twarz")))
        if g.get("uszy") and g["uszy"] not in rasy.USZY:
            zle.append("%s: nieznane uszy %r" % (rasa, g["uszy"]))
        if g.get("wlosy") and g["wlosy"] not in rasy.WLOSY:
            zle.append("%s: nieznane włosy %r" % (rasa, g["wlosy"]))
    if rasy.ZBUDOWANE != ("elf", "ork"):
        zle.append("zbudowane rasy: %r (pilotaż: elf i ork)" % (rasy.ZBUDOWANE,))
    if rasy.RASY["ork"]["skala"] <= 1.0 or rasy.RASY["goblin"]["skala"] >= 1.0:
        zle.append("skala: ork ma być większy od 1, goblin mniejszy")
    return zle


def _klipy(p):
    return {k.nazwa: (k.dlugosc, k.fps, k.petla, k.probki, k.kanaly) for k in p.klipy}


def test_cialo_i_klipy():
    zle = []
    wzor, wzor2 = rycerz.cialo(), zwiadowca.cialo()
    if wzor.kosci != wzor2.kosci or wzor.zaczepy != wzor2.zaczepy:
        zle.append("goły Rycerz i goły Zwiadowca mają różne kości albo zaczepy — test zakłada jedno ciało „czlowiek”")
    klipy_wzoru = _klipy(wzor)
    for rasa, r in rasy.RASY.items():
        c = rasy.cialo(rasa)
        if c.id != "rasa_%s_cialo" % rasa or getattr(c, "typ_ciala", None) != "czlowiek":
            zle.append("%s: id %r, typ ciała %r" % (rasa, c.id, getattr(c, "typ_ciala", None)))
        if c.kosci != wzor.kosci:
            zle.append("%s: kości (stawy, klocki, środki) różnią się od ciała człowieka" % rasa)
        if list(c.kosci) != list(wzor.kosci):
            zle.append("%s: inna kolejność kości" % rasa)
        if c.zaczepy != wzor.zaczepy or len(c.zaczepy) != 18:
            zle.append("%s: zaczepy różnią się od ciała człowieka (%d)" % (rasa, len(c.zaczepy)))
        if c.skala != 1.0 or c.skala_rasy != r["skala"]:
            zle.append("%s: skala postaci %r (ma być 1), skala rasy %r (dane: %r)" % (rasa, c.skala, c.skala_rasy,
                                                                                       r["skala"]))
        kl = _klipy(c)
        if tuple(kl) != rasy.KLIPY:
            zle.append("%s: klipy %r, oczekiwane %r" % (rasa, tuple(kl), rasy.KLIPY))
        for n in kl:
            if kl[n] != klipy_wzoru.get(n):
                zle.append("%s: klip %s różni się od klipu ciała odniesienia człowieka" % (rasa, n))
            if kl[n][4] is klipy_wzoru[n][4]:
                zle.append("%s: klip %s dzieli kanały z Rycerzem (ma być kopia)" % (rasa, n))
        if c.poza_renderu is not None:
            zle.append("%s: ciało ma pozę renderu %r (ma stać w spoczynku)" % (rasa, c.poza_renderu))
        e = rasy.cialo(rasa, zaczepy_ekwipunku=True)
        if len(e.zaczepy) != 33 or e.kosci != wzor.kosci:
            zle.append("%s: ciało z zaczepami Ekw… ma %d zaczepów (ma być 33)" % (rasa, len(e.zaczepy)))
        b, _ = c.sprawdz()
        if b:
            zle.append("%s: sprawdz(): %s" % (rasa, "; ".join(b)))
        wl = [a for a, *_ in c.zalozone]
        if bool(wl) != bool(r["glowa"]["wlosy"]) or any(getattr(a, "znacznik", None) != "Wlosy" for a in wl):
            zle.append("%s: włosy jako akcesorium ze znacznikiem „Wlosy”: %r" % (rasa, [a.id for a in wl]))
        k = rasy.w_skali(rasy.model(rasa))
        if k.skala != r["skala"] or any(a.skala != r["skala"] for a, *_ in k.zalozone):
            zle.append("%s: w_skali() nie mnoży modelu albo włosów przez skalę rasy" % rasa)
    return zle


def test_ekwipunek():
    zle = []
    prz = rasy.przedmioty_klas()
    for rasa in rasy.RASY:
        c = rasy.cialo(rasa)
        cechy = sorted(x["n"] for x in c.czesci if x.get("cecha"))
        if not cechy or any(x.get("golas") for x in c.czesci if x.get("cecha")):
            zle.append("%s: cechy rasy muszą mieć znacznik „cecha” i nie mogą mieć „golas”" % rasa)
        bez = sorted(x["n"] for x in c.czesci if x["n"].startswith(CECHY) and not x.get("cecha"))
        if bez or sum(1 for x in c.czesci if x.get("cecha")) + sum(1 for x in c.czesci if x.get("golas")) != len(c.czesci):
            zle.append("%s: bryły bez znacznika „cecha” albo „golas”: %r" % (rasa, bez))
        for pid, x in prz.items():                                # każdy przedmiot osobno
            try:
                ubierz(c, [x])
            except ValueError as e:
                zle.append("%s: przedmiot %s nie pasuje: %s" % (rasa, pid, e))
        for nazwa, ids in rasy.STROJE.items():
            if not ids:
                continue
            p = rasy.stroj(rasa, nazwa, prz)
            zostalo = sorted(x["n"] for x in p.czesci if x.get("cecha"))
            if zostalo != cechy:
                zle.append("%s w stroju %s: zniknęły cechy rasy %r" % (rasa, nazwa, sorted(set(cechy) - set(zostalo))))
            # komplety obu bohaterów mają powłoki na wszystkich kościach poza głową: strój bazowy znika cały
            gole = sorted({x["kosc"] for x in p.czesci if x.get("golas") and x["kosc"] != "Head"})
            if gole:
                zle.append("%s w stroju %s: strój bazowy został na kościach %r" % (rasa, nazwa, gole))
            if any(getattr(a, "znacznik", None) == "Wlosy" for a, *_ in p.zalozone):
                zle.append("%s w stroju %s: hełm albo kaptur nie schował włosów" % (rasa, nazwa))
            if p.kosci != c.kosci or _klipy(p) != _klipy(c):
                zle.append("%s w stroju %s: zmieniły się kości albo klipy" % (rasa, nazwa))
            if p.sprawdz()[0]:
                zle.append("%s w stroju %s: sprawdz(): %s" % (rasa, nazwa, "; ".join(p.sprawdz()[0])))
        buty = [x["n"] for x in c.czesci if x["kosc"] == "LeftFoot" and x.get("golas")]
        if "Podeszwa" not in buty:
            zle.append("%s: brązowe buty nie są warstwą ciała (golas) na stopie: %r" % (rasa, buty))
        if "Podeszwa" in [x["n"] for x in rasy.cialo(rasa, buty=False).czesci]:
            zle.append("%s: buty=False nadal daje buty" % rasa)
    return zle


def test_moduly():
    zle = []
    for mod, rasa in ((rasa_elf, "elf"), (rasa_ork, "ork")):
        ob = mod.zbuduj()
        if not (isinstance(ob, list) and len(ob) == 1 and isinstance(ob[0], Postac)):
            zle.append("%s.zbuduj(): oczekiwana lista z jedną postacią" % mod.ID)
            continue
        p = ob[0]
        if (p.id, mod.ID, mod.RASA) != ("rasa_" + rasa,) * 2 + (rasa,):
            zle.append("%s: id %r / ID %r / RASA %r" % (rasa, p.id, mod.ID, mod.RASA))
        if p.sprawdz()[0]:
            zle.append("%s: sprawdz(): %s" % (mod.ID, "; ".join(p.sprawdz()[0])))
        json.dumps(pakiet(ob))                                     # pakiet dla Blendera daje się zapisać
        if [x.id for x in mod.warianty("plansze")] != ["%s_%s" % (mod.ID, s) for s in mod.STROJE]:
            zle.append("%s: warianty(plansze) nie odpowiadają STROJE" % mod.ID)
        eks = mod.warianty("eksport")
        if [x.id for x in eks] != [mod.ID + "_cialo"] or [k.nazwa for k in eks[0].klipy] != ["idle"]:
            zle.append("%s: warianty(eksport) = %r" % (mod.ID, [x.id for x in eks]))
        d = json.loads(json.dumps(mod.ekwipunek_json()))
        if d.get("przedmioty") != [] or d.get("cialo") != "czlowiek" or d.get("skala") != rasy.RASY[rasa]["skala"]:
            zle.append("%s: ekwipunek_json(): %r" % (mod.ID, {k: d.get(k) for k in ("przedmioty", "cialo", "skala")}))
        if mod.przedmioty() != [] or not getattr(mod, "SLABOSCI", None):
            zle.append("%s: przedmioty() albo SLABOSCI" % mod.ID)
        for nazwa in mod.STROJE:
            for i in set(mod.STROJE[nazwa]):
                if "%s_%s" % (mod.ID, nazwa) == i:
                    zle.append("%s: nazwa stroju %s daje id przedmiotu" % (mod.ID, nazwa))
    return zle


def test_bohaterowie():
    zle = []
    dzis = odciski_dzis()
    for nazwa, m in BOHATEROWIE.items():
        if dzis[nazwa] != ODCISKI[nazwa]:
            zle.append("%s: pakiet zbuduj() albo cialo() zmienił się względem stanu sprzed ras" % nazwa)
        p = m.zbuduj()[0]
        liczby = (len(p.kosci), len(p.zaczepy), len(p.klipy), len(p.czesci))
        if liczby != LICZBY[nazwa]:
            zle.append("%s: kości/zaczepy/klipy/bryły %r, oczekiwane %r" % (nazwa, liczby, LICZBY[nazwa]))
    return zle


PROBY = (("dane sześciu ras", test_dane), ("ciało i klipy ras = ciało człowieka", test_cialo_i_klipy),
         ("przedmioty „czlowiek” na rasach", test_ekwipunek), ("moduły rasa_elf i rasa_ork", test_moduly),
         ("istniejący bohaterowie bez zmian", test_bohaterowie))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if "--odciski" in sys.argv:
        for nazwa, (a, b) in odciski_dzis().items():
            print('    "%s": ("%s",\n        "%s"),' % (nazwa, a, b))
        sys.exit(0)
    ok = True
    for opis, proba in PROBY:
        zle = proba()
        ok = ok and not zle
        print("%s: %s" % (opis, "zgodne" if not zle else "NIEZGODNE (%d)" % len(zle)))
        for z in zle[:20]:
            print("   -", z)
    print("WYNIK:", "ZGODNE" if ok else "NIEZGODNE")
    sys.exit(0 if ok else 1)
