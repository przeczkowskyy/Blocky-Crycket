#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator mapy „Bagno jako wąski pas” (PROPOZYCJA, bez Studio) — składa Bagno z klocków z planu swiat/bagno_pas/plan.py.

    python -B swiat/bagno_pas/generuj.py              # → plan_bagna.json, czesci.json, znaczniki.json + raport (kod 1 = błąd)
    python -B swiat/bagno_pas/generuj.py --wyj X.json # części do innego pliku

Kontener w Studio: Workspace/BagnoPas. Układ pasa jak w lesie-pasie: świat = (1100 + u; y; −700 + v), bez obrotu; Bagno
zajmuje u 936…1906 (za bramą do Bagna lasu-pasa, u 934). Wynik deterministyczny (random.Random(ziarno)).

Z lasu-pasa (import, bez kopiowania): Scena i kontrola biblioteki, paleta i faktury starego lasu (`faktury.naloz` +
nazwy dodatkowe lasu-pasa), rodziny roślin, skał i detali, `las_pas.kontekst.Pas`, `las_pas.zasady` (Zasady, postaw),
`las_pas.punkty` (Kamień Powrotu, stanowisko jajka), `las_pas.kulisy` (drzewo, drobne, bez_kolizji), układ znaczników.
"""
import argparse
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import KULA, WALEC, Scena  # noqa: E402
from swiat.biom_las import faktury  # noqa: E402
from swiat.bagno_pas import kulisy, miejsca, plan as plan_bagna, teren  # noqa: E402
from swiat.bagno_pas.kontekst import KONTENER, PALETA, U_MAX, U_MIN, Bagno, ZasadyBagna  # noqa: E402
from swiat.las_pas.generuj import FAKTURY_DODATKOWE as FAKTURY_LASU_PASA  # noqa: E402

LIMIT = 12000
CEL = 9000
PRZEZROCZYSTE_MAX = 30
# nowe nazwy części Bagna (nie ma ich w faktury.py starego lasu ani w lesie-pasie) → rola z faktury.ROLE
FAKTURY_BAGNA = {
    "Kładka deska": "deski", "Kładka pal": "drewno", "Kładka poręcz": "drewno", "Pomost okrągły": "deski",
    "Kępa": "trawa", "Kępa brzeg": "mech", "Plama kępy": "trawa", "Plama błota": "bloto", "Błoto": "bloto",
    "Kopiec błota": "bloto", "Toń": "gladkie", "Rzęsa": "gladkie",
    "Chata pal": "drewno", "Chata ściana": "deski", "Strzecha": "gladkie", "Komin": "skala", "Drabina": "drewno",
    "Sieć": "tkanina", "Wrak burta": "deski", "Maszt": "drewno", "Żagiel": "tkanina", "Latarnia słup": "drewno",
    "Latarnia klosz": "gladkie", "Wieża pal": "drewno", "Wieża pomost": "deski", "Pal bramy": "drewno",
    "Liana": "gladkie", "Liść olbrzym": "gladkie", "Liść łodyga": "gladkie", "Palma pień": "drewno", "Palma liść": "gladkie",
}
FAKTURY_DODATKOWE = dict(FAKTURY_LASU_PASA, **FAKTURY_BAGNA)
# nazwy, które w faktury.py mają rolę lasu, a w Bagnie inną (nazwy zostają, bo czytają je skrypty gry): Płyta = błoto
NADPISZ_ROLE = {"Płyta": "bloto"}
ODCINKI_RAPORTU = [
    (-1e9, 940.0, "za bramą lasu (u 936–940)"),
    (940.0, 1004.0, "Pomost Przybycia"),
    (1004.0, 1016.0, "rów z kładką"),
    (1016.0, 1208.0, "Rechotne Oczka"),
    (1208.0, 1228.0, "Kładka nad Topielą"),
    (1228.0, 1420.0, "Bulgotne Trzęsawisko"),
    (1420.0, 1436.0, "trzcinowa przesieka"),
    (1436.0, 1628.0, "Kłapiące Kępy"),
    (1628.0, 1644.0, "zatopione pnie"),
    (1644.0, 1744.0, "Leże Ropuchy"),
    (1744.0, 1760.0, "Latarnie Topieli"),
    (1760.0, 1848.0, "Topiel Strażnika"),
    (1848.0, 1876.0, "przedbramie i Brama do Dżungli"),
    (1876.0, 1e9, "zapowiedź Dżungli (u 1876–1906)"),
]


def naloz_faktury(s):
    """faktury.naloz starego lasu, potem nazwy dodatkowe (las-pas + Bagno) i nadpisane role. Zwraca nazwy bez roli."""
    for n in FAKTURY_DODATKOWE:
        assert n not in faktury.NAZWY, "nazwa %s jest już w faktury.py — usuń ją z FAKTURY_DODATKOWE" % n
    pierwotne = [c[11] for c in s.czesci]
    brak = set(faktury.naloz(s))
    for i, c in enumerate(s.czesci):
        if s.materialy[c[12]] == "Neon" and c[14] not in NADPISZ_ROLE:
            continue
        r = NADPISZ_ROLE.get(c[14]) if c[14] in NADPISZ_ROLE else (FAKTURY_DODATKOWE.get(c[14]) if c[14] in brak else None)
        if r is None:
            continue
        if 0 < c[13] < 1:
            r = "gladkie"
        mat, k, _ = faktury.ROLE[r]
        c[12] = s._idx(s.materialy, mat)
        c[11] = faktury.jasniej(pierwotne[i], k)
    return sorted(b for b in brak if b not in FAKTURY_DODATKOWE)


def odcinek_raportu(u):
    for a, b, n in ODCINKI_RAPORTU:
        if a <= u < b:
            return n
    return ODCINKI_RAPORTU[-1][2]


def raport(s, K):
    pref = len(s.korzen) + 1
    gl, od = {}, {}
    for c in s.czesci:
        g = s.grupy[c[1]][pref:].split("/")[0]
        gl[g] = gl.get(g, 0) + 1
        n = odcinek_raportu(c[2] - K.X0)
        od[n] = od.get(n, 0) + 1
    print("CZĘŚCI: %d (cel ok. %d, twardy limit %d)" % (len(s.czesci), CEL, LIMIT))
    print("  na odcinek pasa (z kulisami i tłem; płyta liczy się do odcinka swojego środka):")
    for _, _, n in ODCINKI_RAPORTU:
        print("    %-34s %5d" % (n, od.get(n, 0)))
    print("  na grupę główną:")
    for g in sorted(gl, key=lambda k: -gl[k]):
        print("    %-34s %5d" % (g, gl[g]))
    mats = s.materialy
    n = float(len(s.czesci))
    neon = sum(1 for c in s.czesci if mats[c[12]] == "Neon")
    kule = sum(1 for c in s.czesci if c[0] == KULA)
    walce = sum(1 for c in s.czesci if c[0] == WALEC)
    przezr = sum(1 for c in s.czesci if 0 < c[13] < 0.98)
    bez_kol = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 1)
    print("SUFITY: Neon %d (≤300), kule %d (≤300), walce %d (≤3000), półprzezroczyste %d (≤%d), z kolizją %.0f%% (≤25%%)"
          % (neon, kule, walce, przezr, PRZEZROCZYSTE_MAX, 100 * (n - bez_kol) / n))
    ud = faktury.udzialy(s)["razem"]
    print("MATERIAŁY: " + ", ".join("%s %.1f%%" % (m, 100 * v / n) for m, v in sorted(ud.items(), key=lambda kv: -kv[1])))
    return gl, od


# =========================================================================== znaczniki dla następnych etapów
def znaczniki(s, K, plik, statystyka):
    """znaczniki.json w tym samym układzie co las-pas (punkty pasa [u, y, v] i od razu świat [X, Y, Z] w polach *_swiat).
    Jedyna różnica rodzaju: zamiast `brama_bagna` jest `brama_dzungli` (brama do następnego biomu)."""
    P = K.P
    X0, Z0 = K.X0, K.Z0

    def sw(u, y, v):
        return [round(X0 + u, 2), round(y, 2), round(Z0 + v, 2)]

    pref = len(KONTENER) + 1
    grupy = sorted({s.grupy[c[1]][pref:] for c in s.czesci})
    punkty_e = []
    for c in s.czesci:
        g = s.grupy[c[1]]
        if g.endswith("/_Interakcja"):
            punkty_e.append({"grupa": g[pref:].rsplit("/_Interakcja", 1)[0],
                             "punkt": [round(c[2] - X0, 2), round(c[3], 2), round(c[4] - Z0, 2)], "punkt_swiat": [c[2], c[3], c[4]]})
    stale = sorted({"/".join(g.split("/")[:2]) for g in grupy if g.startswith(("Punkty/", "BramaDzungli/"))})
    niski = sorted({"/".join(g.split("/")[:3]) for g in grupy if g.startswith(("Kulisy/Lewa/", "Kulisy/Prawa/", "Tlo/"))})
    m = K.miejsca
    pr = m["przybycie"]
    bd = m["brama_dzungli"]
    st_ = P["straznik"]
    d = {
        "opis": "Znaczniki Bagna-pasa (PROPOZYCJA) dla następnych etapów: potwory w przegrodach, teleport, przelot kamery, "
                "brama do Dżungli, mgła, streaming. Generuje swiat/bagno_pas/generuj.py z swiat/bagno_pas/plan.py. Punkty w "
                "UKŁADZIE PASA [u, y, v] (ten sam co las-pas); pola *_swiat = świat Studio [X, Y, Z].",
        "kontener": {"nazwa": KONTENER, "uklad": "pas: u wzdłuż (od początku lasu), v w poprzek (v > 0 po prawej ręce idącego "
                                                 "do bramy), y w górę",
                     "wzor": "swiat = (%g + u; y; %g + v), bez obrotu" % (X0, Z0), "X0": X0, "Z0": Z0, "obrot_y": 0},
        "plan": "swiat/bagno_pas/plan_bagna.json",
        "pas": {"szerokosc": P["pas"]["szerokosc"], "kulisy": P["pas"]["kulisy"], "u_od": P["pas"]["u_od"], "u_do": P["pas"]["u_do"],
                "niewidzialna_sciana_v": 38, "zakres_czesci_u": [U_MIN, U_MAX], "zakres_czesci_v": [-88, 88]},
        "sasiad_las": {"kontener": "Workspace/LasPas", "usun_przed_budowa": "Workspace/LasPas/ZapowiedzBagna",
                       "dlaczego": "zapowiedź Bagna lasu-pasa (u 934–966, niewidzialna ściana u 965) stoi tam, gdzie Pomost "
                                   "Przybycia; reszta lasu-pasa zostaje (kulisy i płyta do u 966, palisada bramy u 932–936)"},
        "przegrody": [{"id": q["id"], "nazwa": q["nazwa"], "u": [q["u_od"], q["u_do"]],
                       "pod": [{"id": p["id"], "nazwa": p["nazwa"], "u": [p["u_od"], p["u_do"]]} for p in q.get("pod", [])]}
                      for q in P["przegrody"]],
        "przejscia": [{"id": t["id"], "nazwa": t["nazwa"], "u": [t["u_od"], t["u_do"]], "otwarcie_v": t["otwarcie"],
                       "wys_w_otwarciu": t["wys_w_otwarciu"]} for t in P["przejscia"]],
        "start": {"opis": "start biomu = punkt przybycia (teleport i wejście z lasu przez bramę)",
                  "punkt": [pr["u"], 0.0, pr["v"]], "punkt_swiat": sw(pr["u"], 0.0, pr["v"])},
        "przybycie": {"punkt": [pr["u"], 0.0, pr["v"]], "punkt_swiat": sw(pr["u"], 0.0, pr["v"]),
                      "patrz_na": [pr["patrz"][0], 0.0, pr["patrz"][1]], "patrz_na_swiat": sw(pr["patrz"][0], 0.0, pr["patrz"][1])},
        "inkubator": {"opis": "stanowisko jajka (inkubator Bagna, D-060) — punkt E w grupie Punkty/StanowiskoJajka",
                      "punkt": [m["jajko"]["u"], 0.0, m["jajko"]["v"]], "punkt_swiat": sw(m["jajko"]["u"], 0.0, m["jajko"]["v"]),
                      "grupa": KONTENER + "/Punkty/StanowiskoJajka"},
        "miejsca": [dict(x, punkt=[x["u"], x.get("y", 0.0), x["v"]], punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) for x in P["miejsca"]],
        "punkty_przybycia": [dict(x, punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) if "u" in x else dict(x) for x in P["punkty_przybycia"]],
        "strefy_spokoju": [dict(z_, prostokat_swiat={"x": [X0 + z_["u"][0], X0 + z_["u"][1]], "z": [Z0 + z_["v"][0], Z0 + z_["v"][1]]})
                           for z_ in P["strefy_spokoju"]],
        "strefy": [{"id": st["id"], "podbiom": st["podbiom"], "pod": st["pod"], "potwor": st["potwor"], "klasa": st["klasa"],
                    "wariant": st.get("wariant"), "poziomy": st["poziomy"], "poziomy_rowny": st["poziomy_rowny"],
                    "poziomy_status": st.get("poziomy_status"), "naraz": st["naraz"], "max": st["max"],
                    "srodek": [st["srodek"][0], 0.0, st["srodek"][1]], "r": st["r"],
                    "wezly": [[u, 0.0, v] for u, v in st["trasa"]], "wezly_swiat": [sw(u, 0.0, v) for u, v in st["trasa"]],
                    "domy": [[u, 0.0, v] for u, v in st["dom"]["pts"]], "domy_swiat": [sw(u, 0.0, v) for u, v in st["dom"]["pts"]],
                    "dom_opis": st["dom"]["opis"], "odrodzenie_s": st["odrodzenie_s"], "odrodzenie_stale": st.get("odrodzenie_stale", False),
                    "grupa": st.get("grupa"), "zachowanie": st["zachowanie"], "pole": st["pole"]} for st in P["strefy"]],
        "straznik": dict(st_, miejsce_swiat=sw(st_["miejsce"][0], 0.3, st_["miejsce"][1]),
                         arena_srodek_swiat=sw(st_["arena"]["srodek"][0], 0.3, st_["arena"]["srodek"][1]),
                         uwaga="Strażnik stoi na okrągłym pomoście (wierzch 0,3)"),
        "zasady": P["zasady"], "rozmiary": P["rozmiary"],
        "przelot_kamery": dict(P["przelot_kamery"], punkty_swiat=[
            {"t": p["t"], "poz": sw(p["poz"][0], p["poz"][2], p["poz"][1]), "patrz": sw(p["patrz"][0], p["patrz"][2], p["patrz"][1])}
            for p in P["przelot_kamery"]["punkty"]],
            uwaga="w planie poz/patrz = [u, v, wysokość]; w punkty_swiat = [X, Y, Z]; krzywa: sprawdz_plan.krzywa_kamery"),
        "brama_dzungli": {"rodzaj": "brama do następnego biomu (w lesie-pasie pole nazywa się brama_bagna)",
                          "grupa_wrot": KONTENER + "/BramaDzungli/Wrota", "grupa_palisady": KONTENER + "/BramaDzungli/Palisada",
                          "u": bd["u"], "otwarcie_v": bd["otwarcie"],
                          "jak_otwierac": "jak brama do Bagna: u klienta gracza, który pokonał Strażnika Topieli, części grupy "
                                          "Wrota CanCollide = false i LocalTransparencyModifier = 1; serwer pilnuje atrybutu gracza",
                          "za_brama": "ZapowiedzDzungli (u 1876–1906) z niewidzialną ścianą na u 1905 — do usunięcia, gdy powstanie Dżungla"},
        "punkty_e": punkty_e,
        "punkty_orientacyjne": [dict(z_, punkt_swiat=sw(z_["u"], 0.0, z_["v"])) for z_ in P["punkty_orientacyjne"]],
        "niewidzialne_sciany": "Kulisy/Niewidzialne (|v| = 38 od u 964 do 1904), ZapowiedzDzungli (u 1905); za plecami — "
                               "palisada bramy lasu-pasa (u 934)",
        "mgla": {"opis": "niska mgła z części (grupa Mgla, półprzezroczyste ławice 0,75–1,25 i w kulisach) + mgła lokalna u "
                         "gracza (skrypt klienta jak w lesie-pasie), wspólnego Lighting nie zmieniamy",
                 "prostokat_swiat": {"x": [X0 + 936, X0 + 1880], "z": [Z0 - 60, Z0 + 60]},
                 "propozycja": {"FogColor": "9AA58E", "FogStart": 30, "FogEnd": 260, "przejscie_od_lasu_st": 40}},
        "grupy_stale_wczytane": {"ModelStreamingMode": "Persistent", "grupy": stale,
                                 "dlaczego": "punkty orientacyjne widać z daleka; wrota bramy musi znaleźć skrypt gracza"},
        "grupy_niski_detal": {"LevelOfDetail": "StreamingMesh", "grupy": niski,
                              "dlaczego": "kulisy i tło widać z daleka jako uproszczoną bryłę poza promieniem streamingu"},
        "statystyka": statystyka,
    }
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


# =========================================================================== całość
def generuj(ziarno=11):
    P = plan_bagna.zbuduj()
    s = Scena(KONTENER, paleta=PALETA)
    K = Bagno(ziarno, P)
    Z = ZasadyBagna(K)
    stat = {}
    with s.uklad(pos=(K.X0, 0.0, K.Z0)):
        teren.plyta_i_plamy(s, K)
        teren.wody(s, K)
        teren.kepy(s, K)
        teren.trzesawisko(s, K)
        teren.tropy(s, K)
        miejsca.pomost_przybycia(s, K)
        miejsca.chata_na_palach(s, K)
        miejsca.stary_cyprys(s, K)
        miejsca.wrak_lodzi(s, K)
        miejsca.ropusza_chata(s, K)
        miejsca.latarnie_topieli(s, K)
        miejsca.topiel_arena(s, K)
        miejsca.brama_dzungli(s, K)
        stat["kladka_odcinkow"] = teren.kladka(s, K, Z)
        miejsca.trzcinowa_przesieka(s, K)
        miejsca.zatopione_pnie(s, K)
        miejsca.ozdoby_rowow(s, K)
        miejsca.domy(s, K)
        miejsca.przedbramie(s, K)
        miejsca.zapowiedz_dzungli(s, K, Z)
        stat["ozdoby"] = miejsca.ozdoby(s, K, Z)
        stat["kulisy"] = kulisy.kulisy(s, K, Z)
        stat["tlo"] = kulisy.tlo(s, K, Z)
        kulisy.niewidzialne_sciany(s, K)
        stat["lilie"] = teren.lilie(s, K, Z)
        stat["mgla"] = teren.mgla(s, K, Z)
        stat["detale_kladki"] = kulisy.detale_kladki(s, K, Z)
        stat["runo"] = kulisy.runo(s, K, Z)
    return s, K, Z, P, stat


def main():
    ap = argparse.ArgumentParser(description="Generator Bagna-pasa (Workspace/BagnoPas)")
    ap.add_argument("--ziarno", type=int, default=11)
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    s, K, Z, P, stat = generuj(a.ziarno)
    plan_bagna.zapisz(P)
    brak_roli = naloz_faktury(s)
    s.zapisz(a.wyj)
    gl, od = raport(s, K)
    ks = stat["kulisy"]
    print("KULISY: przód %d (nie zmieściło się %d), skraj %d, drugi rząd %d, głąb %d; tło %d sylwetek"
          % (ks["przod"], ks["przod_odrzucone"], ks["skraj"], ks["srodek"], ks["glab"], stat["tlo"]))
    print("DETALE: kładka %d odcinków, przy kładce %d, runo %d, lilie %d, ławice mgły %d"
          % (stat["kladka_odcinkow"], stat["detale_kladki"], stat["runo"], stat["lilie"], stat["mgla"]))
    print("OZDOBY PRZEGRÓD: " + ", ".join("%s %d" % kv for kv in stat["ozdoby"].items()))
    print("FAKTURY: %s" % ("każda część ma rolę" if not brak_roli else "BEZ ROLI: " + ", ".join(brak_roli)))
    znaczniki(s, K, os.path.join(TU, "znaczniki.json"), {"czesci": len(s.czesci), "na_odcinek": od, "na_grupe": gl})
    uwagi = s.sprawdz(min_y=-3.0, limit_czesci=LIMIT)
    print("SPRAWDZ (biblioteka): %d ostrzeżeń" % len(uwagi))
    for u in uwagi[:30]:
        print("  UWAGA:", u)
    print("ZAPISANO:", os.path.relpath(a.wyj, REPO).replace(os.sep, "/"), "+ swiat/bagno_pas/znaczniki.json, plan_bagna.json")
    print("Kontrola: python -B swiat/bagno_pas/sprawdz.py")
    return 1 if brak_roli or len(s.czesci) > LIMIT else 0


if __name__ == "__main__":
    sys.exit(main())
