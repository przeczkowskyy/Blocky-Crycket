#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator mapy „Las jako wąski pas” — składa las z klocków z planu swiat/biom_las/pas/plan_pasa.json.

    python -B swiat/las_pas/generuj.py              # → czesci.json, znaczniki.json + raport części (kod 1 = błąd)
    python -B swiat/las_pas/generuj.py --wyj X.json # części do innego pliku (znaczniki.json zawsze obok generatora)

Kontener w Studio: Workspace/LasPas (osobny od starego Workspace/BiomLas). Układ pasa: u wzdłuż, v w poprzek; świat
Studio = (1100 + u; y; −700 + v), bez obrotu — w pliku części wszystko stoi już tam, gdzie ma stanąć w Studio.
Wynik deterministyczny (random.Random(ziarno)).

Kolejność: grunt (płyta, plamy, strzępy) → ścieżka → strumyk z mostkiem → wydeptane pętle i polanki stref → punkty
orientacyjne i miejsca (Brama Pniaków, Kamień Powrotu, stanowisko jajka, krąg przybycia, paśnik, Wielki Kapelusz, Wilcza
Skała, głazy legowiska z kotłem, menhiry, arena z filarem, Brama do Bagna, zapowiedź Bagna) → przejścia → domy potworów
→ rekwizyty przegród → kulisy (przód, skraj, głąb) → ściana zamykająca, niewidzialne ściany, tło → detale → FAKTURY
(faktury.naloz ze starego lasu + kilka nowych nazw części, tabela FAKTURY_DODATKOWE) → zapis i raport.
"""
import argparse
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import Scena, KULA, WALEC  # noqa: E402
from swiat.biom_las import faktury  # noqa: E402
from swiat.biom_las.paleta import PALETA  # noqa: E402
from swiat.las_pas import detale_pasa, grunt, kulisy, przegrody, punkty  # noqa: E402
from swiat.las_pas.kontekst import KONTENER, Pas, PLIK_PLANU  # noqa: E402
from swiat.las_pas.zasady import Zasady  # noqa: E402

LIMIT = 12000                 # twardy limit z zamówienia (cel ok. 9 000)
CEL = 9000
PRZEZROCZYSTE_MAX = 20
# nowe nazwy części (nie ma ich w faktury.py starego lasu, którego nie zmieniamy) → rola z faktury.ROLE
FAKTURY_DODATKOWE = {
    "Żywopłot": "gladkie",        # niskie przegródki kojców
    "Furtka": "deski",            # skrzydło furtki
    "Dym": "gladkie",             # dym z kotła (zestaw.dym)
}
# odcinki pasa do raportu części (u od, u do, nazwa) — część liczy się do odcinka, w którym leży jej środek
ODCINKI_RAPORTU = [
    (-1e9, 0.0, "ściana zamykająca (u −34…0)"),
    (0.0, 64.0, "Polana Przybycia"),
    (64.0, 76.0, "płot z furtką"),
    (76.0, 268.0, "Zagroda Slime'ów"),
    (268.0, 288.0, "strumyk z mostkiem"),
    (288.0, 480.0, "Lasek Muchomorowy"),
    (480.0, 496.0, "jeżynowe zwężenie"),
    (496.0, 688.0, "Wilcze Zarośla"),
    (688.0, 704.0, "kamienny próg"),
    (704.0, 804.0, "Leże Trolla"),
    (804.0, 820.0, "brama menhirów"),
    (820.0, 908.0, "Arena Strażnika Gaju"),
    (908.0, 940.0, "przedbramie i Brama do Bagna"),
    (940.0, 1e9, "zapowiedź Bagna (u 940–966)"),
]


def naloz_faktury(s):
    """faktury.naloz ze starego lasu (rola z nazwy części → materiał i korekta koloru), potem dodatkowe nazwy tego
    generatora. Zwraca nazwy części, które nadal nie mają roli (ma być pusto)."""
    for n in FAKTURY_DODATKOWE:
        assert n not in faktury.NAZWY, "nazwa %s jest już w faktury.py — usuń ją z FAKTURY_DODATKOWE" % n
    brak = set(faktury.naloz(s))
    for c in s.czesci:
        if c[14] not in brak or s.materialy[c[12]] == "Neon":
            continue
        r = FAKTURY_DODATKOWE.get(c[14])
        if r is None:
            continue
        if 0 < c[13] < 1:
            r = "gladkie"
        mat, k, _ = faktury.ROLE[r]
        c[12] = s._idx(s.materialy, mat)
        c[11] = faktury.jasniej(c[11], k)
    return sorted(b for b in brak if b not in FAKTURY_DODATKOWE)


def odcinek_raportu(u):
    for a, b, n in ODCINKI_RAPORTU:
        if a <= u < b:
            return n
    return ODCINKI_RAPORTU[-1][2]


def raport(s, K):
    X0 = K.X0
    pref = len(s.korzen) + 1
    gl, od = {}, {}
    for c in s.czesci:
        g = s.grupy[c[1]][pref:].split("/")[0]
        gl[g] = gl.get(g, 0) + 1
        n = odcinek_raportu(c[2] - X0)
        od[n] = od.get(n, 0) + 1
    print("CZĘŚCI: %d (cel ok. %d, twardy limit %d)" % (len(s.czesci), CEL, LIMIT))
    print("  na odcinek pasa (z kulisami i tłem w tym pasie u; płyta gruntu liczy się do odcinka swojego środka):")
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
    przezr = sum(1 for c in s.czesci if 0 < c[13] < 1)
    bez_kol = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 1)
    bez_cien = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 2)
    print("SUFITY: Neon %d (≤300), kule %d (≤300), walce %d (≤3000), półprzezroczyste %d (≤%d), z kolizją %.0f%% (≤25%%), "
          "bez cienia %.0f%%" % (neon, kule, walce, przezr, PRZEZROCZYSTE_MAX, 100 * (n - bez_kol) / n, 100 * bez_cien / n))
    ud = faktury.udzialy(s)["razem"]
    print("MATERIAŁY: " + ", ".join("%s %.1f%%" % (m, 100 * v / n) for m, v in sorted(ud.items(), key=lambda kv: -kv[1])))
    return gl, od


# =========================================================================== znaczniki dla następnego etapu
def znaczniki(s, K, plik, statystyka):
    """znaczniki.json: wszystko, czego potrzebuje następny etap (potwory, teleport, przelot, brama, streaming) — w układzie
    PASA [u, y, v] i od razu w świecie Studio [X, Y, Z] (pola *_swiat)."""
    P = K.P
    X0, Z0 = K.X0, K.Z0

    def sw(u, y, v):
        return [round(X0 + u, 2), round(y, 2), round(Z0 + v, 2)]

    pref = len(KONTENER) + 1
    uzyte = sorted({s.grupy[c[1]] for c in s.czesci})
    punkty_e = []
    for c in s.czesci:
        g = s.grupy[c[1]]
        if g.endswith("/_Interakcja"):
            u, y, v = c[2] - X0, c[3], c[4] - Z0
            punkty_e.append({"grupa": g[pref:].rsplit("/_Interakcja", 1)[0], "punkt": [round(u, 2), round(y, 2), round(v, 2)],
                             "punkt_swiat": [c[2], c[3], c[4]]})
    grupy = [g[pref:] for g in uzyte]
    stale = sorted({"/".join(g.split("/")[:2]) for g in grupy if g.startswith(("Punkty/", "BramaBagna/"))})
    niski = sorted({"/".join(g.split("/")[:3]) for g in grupy if g.startswith(("Kulisy/Lewa/", "Kulisy/Prawa/", "Tlo/"))})
    m = K.miejsca
    pr = m["przybycie"]
    d = {
        "opis": "Znaczniki lasu-pasa dla następnych etapów (potwory w przegrodach, teleport, przelot kamery, brama dla "
                "gracza, mgła, streaming). Generuje swiat/las_pas/generuj.py z swiat/biom_las/pas/plan_pasa.json. "
                "Punkty w UKŁADZIE PASA [u, y, v]; pola *_swiat = to samo w świecie Studio [X, Y, Z].",
        "kontener": {"nazwa": KONTENER, "uklad": "pas: u wzdłuż, v w poprzek (v > 0 po prawej ręce idącego do bramy), y w górę",
                     "wzor": "swiat = (%g + u; y; %g + v), bez obrotu" % (X0, Z0), "X0": X0, "Z0": Z0, "obrot_y": 0},
        "plan": os.path.relpath(PLIK_PLANU, REPO).replace(os.sep, "/"),
        "pas": {"szerokosc": P["pas"]["szerokosc"], "kulisy": P["pas"]["kulisy"], "u_od": P["pas"]["u_od"], "u_do": P["pas"]["u_do"],
                "niewidzialna_sciana_v": 38, "zakres_czesci_u": [-34, 966], "zakres_czesci_v": [-88, 88]},
        "przegrody": [{"id": q["id"], "nazwa": q["nazwa"], "u": [q["u_od"], q["u_do"]],
                       "pod": [{"id": p["id"], "nazwa": p["nazwa"], "u": [p["u_od"], p["u_do"]]} for p in q.get("pod", [])]}
                      for q in P["przegrody"]],
        "przejscia": [{"id": t["id"], "nazwa": t["nazwa"], "u": [t["u_od"], t["u_do"]], "otwarcie_v": t["otwarcie"],
                       "wys_w_otwarciu": t["wys_w_otwarciu"]} for t in P["przejscia"]],
        "przybycie": {"punkt": [pr["u"], 0.0, pr["v"]], "punkt_swiat": sw(pr["u"], 0.0, pr["v"]), "patrz_na": [pr["patrz"][0], 0.0, pr["patrz"][1]],
                      "patrz_na_swiat": sw(pr["patrz"][0], 0.0, pr["patrz"][1])},
        "miejsca": [dict(x, punkt=[x["u"], x.get("y", 0.0), x["v"]], punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) for x in P["miejsca"]],
        "punkty_przybycia": [dict(x, punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) if "u" in x else dict(x) for x in P["punkty_przybycia"]],
        "strefy_spokoju": [dict(z_, prostokat_swiat={"x": [X0 + z_["u"][0], X0 + z_["u"][1]], "z": [Z0 + z_["v"][0], Z0 + z_["v"][1]]})
                           for z_ in P["strefy_spokoju"]],
        "strefy": [{"id": st["id"], "podbiom": st["podbiom"], "pod": st["pod"], "potwor": st["potwor"], "wariant": st.get("wariant"),
                    "poziomy": st["poziomy"], "poziomy_status": st.get("poziomy_status"), "naraz": st["naraz"], "max": st["max"],
                    "srodek": [st["srodek"][0], 0.0, st["srodek"][1]], "r": st["r"],
                    "wezly": [[u, 0.0, v] for u, v in st["trasa"]], "wezly_swiat": [sw(u, 0.0, v) for u, v in st["trasa"]],
                    "domy": [[u, 0.0, v] for u, v in st["dom"]["pts"]], "domy_swiat": [sw(u, 0.0, v) for u, v in st["dom"]["pts"]],
                    "dom_opis": st["dom"]["opis"], "odrodzenie_s": st["odrodzenie_s"], "odrodzenie_stale": st.get("odrodzenie_stale", False),
                    "grupa": st.get("grupa"), "zachowanie": st["zachowanie"], "pole": st["pole"]} for st in P["strefy"]],
        "straznik": dict(P["straznik"], miejsce_swiat=sw(P["straznik"]["miejsce"][0], 0.0, P["straznik"]["miejsce"][1]),
                         arena_srodek_swiat=sw(P["straznik"]["arena"]["srodek"][0], 0.3, P["straznik"]["arena"]["srodek"][1]),
                         uwaga="Strażnik stoi na posadzce kręgu (wierzch 0,3)"),
        "zasady": P["zasady"],
        "rozmiary": P["rozmiary"],
        "przelot_kamery": dict(P["przelot_kamery"], punkty_swiat=[
            {"t": p["t"], "poz": sw(p["poz"][0], p["poz"][2], p["poz"][1]), "patrz": sw(p["patrz"][0], p["patrz"][2], p["patrz"][1])}
            for p in P["przelot_kamery"]["punkty"]],
            uwaga="w planie poz/patrz = [u, v, wysokość]; w punkty_swiat = [X, Y, Z]; krzywa: sprawdz_plan.krzywa_kamery"),
        "brama_bagna": {"grupa_wrot": KONTENER + "/BramaBagna/Wrota", "grupa_palisady": KONTENER + "/BramaBagna/Palisada",
                        "u": m["brama_bagna"]["u"], "otwarcie_v": m["brama_bagna"]["otwarcie"],
                        "jak_otwierac": "u klienta gracza, który pokonał Strażnika: części grupy Wrota CanCollide = false "
                                        "i LocalTransparencyModifier = 1 (albo przesunięcie wrót), serwer pilnuje atrybutu gracza",
                        "za_brama": "ZapowiedzBagna (u 934–966) z niewidzialną ścianą na u 965 — do usunięcia, gdy powstanie Bagno"},
        "punkty_e": punkty_e,
        "punkty_orientacyjne": [dict(z_, punkt_swiat=sw(z_["u"], 0.0, z_["v"])) for z_ in P["punkty_orientacyjne"]],
        "niewidzialne_sciany": "Kulisy/Niewidzialne (|v| = 38 od u −4 do 964, u −5 w poprzek), ZapowiedzBagna (u 965)",
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
def generuj(ziarno=7, plik_planu=PLIK_PLANU):
    s = Scena(KONTENER, paleta=PALETA)
    K = Pas(ziarno, plik_planu)
    Z = Zasady(K)
    stat = {}
    with s.uklad(pos=(K.X0, 0.0, K.Z0)):
        grunt.plyta_i_plamy(s, K)
        stat["sciezka_odcinkow"] = grunt.sciezka(s, K)
        grunt.strumyk(s, K)
        grunt.tropy_i_polanki(s, K)
        punkty.brama_pniakow(s, K)
        punkty.kamien_powrotu(s, K)
        punkty.stanowisko_jajka(s, K)
        punkty.krag_przybycia(s, K)
        punkty.pasnik(s, K)
        punkty.wielki_kapelusz(s, K)
        punkty.wilcza_skala(s, K)
        punkty.glazy_legowiska(s, K)
        punkty.menhiry_bramy(s, K)
        punkty.arena(s, K)
        punkty.brama_bagna(s, K)
        punkty.zapowiedz_bagna(s, K)
        przegrody.plot_z_furtka(s, K)
        przegrody.jezynowe_zwezenie(s, K)
        przegrody.kamienny_prog(s, K)
        przegrody.brama_menhirow_kamienie(s, K)
        przegrody.domy(s, K)
        przegrody.polana(s, K, Z)
        przegrody.zagroda(s, K, Z)
        przegrody.lasek(s, K, Z)
        przegrody.zarosla(s, K, Z)
        przegrody.leze(s, K, Z)
        przegrody.przedbramie(s, K, Z)
        stat["ozdoby"] = przegrody.ozdoby(s, K, Z)
        stat["kulisy"] = kulisy.kulisy(s, K, Z)
        kulisy.sciana_zamykajaca(s, K, Z)
        kulisy.niewidzialne_sciany(s, K)
        stat["tlo"] = kulisy.tlo(s, K, Z)
        stat["brzegi_sciezki"] = detale_pasa.brzegi_sciezki(s, K, Z)
        stat["runo"] = detale_pasa.runo(s, K, Z)
        stat["kwiaty"] = detale_pasa.kwiaty(s, K, Z)
    return s, K, Z, stat


def main():
    ap = argparse.ArgumentParser(description="Generator lasu-pasa (Workspace/LasPas)")
    ap.add_argument("--ziarno", type=int, default=7)
    ap.add_argument("--plan", default=PLIK_PLANU)
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    s, K, Z, stat = generuj(a.ziarno, a.plan)
    brak_roli = naloz_faktury(s)
    s.zapisz(a.wyj)
    gl, od = raport(s, K)
    ks = stat["kulisy"]
    print("KULISY: drzewa w przednim rzędzie %d (nie zmieściło się %d), skraj %d, drugi rząd %d, głąb %d; tło %d sylwetek"
          % (ks["przod"], ks["przod_odrzucone"], ks["skraj"], ks.get("srodek", 0), ks["glab"], stat["tlo"]))
    print("DETALE: przy ścieżce %d, kwiaty %d, kępy runa i kłody: %s" % (
        stat["brzegi_sciezki"], stat["kwiaty"],
        ", ".join("%s %d/%d + %d/%d" % ((k,) + v) for k, v in stat["runo"].items())))
    print("OZDOBY PRZEGRÓD: " + ", ".join("%s %d" % kv for kv in stat["ozdoby"].items()))
    print("FAKTURY: %s" % ("każda część ma rolę" if not brak_roli else "BEZ ROLI: " + ", ".join(brak_roli)))
    statystyka = {"czesci": len(s.czesci), "na_odcinek": od, "na_grupe": gl}
    znaczniki(s, K, os.path.join(TU, "znaczniki.json"), statystyka)
    uwagi = s.sprawdz(min_y=-3.0, limit_czesci=LIMIT)
    print("SPRAWDZ (biblioteka): %d ostrzeżeń" % len(uwagi))
    for u in uwagi[:30]:
        print("  UWAGA:", u)
    print("ZAPISANO:", os.path.relpath(a.wyj, REPO).replace(os.sep, "/"), "i swiat/las_pas/znaczniki.json")
    print("Kontrola: python -B swiat/las_pas/sprawdz.py")
    return 1 if brak_roli or len(s.czesci) > LIMIT else 0


if __name__ == "__main__":
    sys.exit(main())
