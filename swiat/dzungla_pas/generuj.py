#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator mapy „Dżungla jako wąski pas” (PROPOZYCJA, bez Studio) — składa Dżunglę z klocków z planu
swiat/dzungla_pas/plan.py.

    python -B swiat/dzungla_pas/generuj.py              # → plan_dzungli.json, czesci.json, znaczniki.json + raport (kod 1 = błąd)
    python -B swiat/dzungla_pas/generuj.py --wyj X.json # części do innego pliku

Kontener w Studio: Workspace/DzunglaPas. Układ pasa jak w lesie-pasie i Bagnie: świat = (1100 + u; y; −700 + v), bez
obrotu; Dżungla zajmuje u 1876…2846 (za bramą do Dżungli Bagna-pasa, u 1874) — dokładnie układ Bagna przesunięty o +940,
żeby swiat/biomy/przycinarka.py mogła ją przyciąć jak Bagno. Wynik deterministyczny (random.Random(ziarno)).

Z lasu-pasa i Bagna (import, bez kopiowania): Scena i kontrola biblioteki, paleta i faktury starego lasu (`faktury.naloz`
+ nazwy dodatkowe lasu-pasa i Bagna), skały i detale lasu, `las_pas.kontekst.Pas`, `las_pas.zasady` (Zasady, postaw),
`las_pas.punkty` (Kamień Powrotu, stanowisko jajka), `las_pas.kulisy` (_losuj, bez_kolizji), układ znaczników Bagna.
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
from swiat.dzungla_pas import kulisy, miejsca, plan as plan_dzungli, teren  # noqa: E402
from swiat.dzungla_pas.kontekst import D, KONTENER, PALETA, U_MAX, U_MIN, Dzungla, ZasadyDzungli  # noqa: E402
from swiat.bagno_pas.generuj import FAKTURY_DODATKOWE as FAKTURY_LASU_I_BAGNA  # noqa: E402

LIMIT = 12000
CEL = 9000
PRZEZROCZYSTE_MAX = 30
# nowe nazwy części Dżungli (nie ma ich w faktury.py starego lasu ani w lesie-pasie i Bagnie) → rola z faktury.ROLE
FAKTURY_DZUNGLI = {
    # grunt i woda
    "Plama trawy": "trawa", "Plama runa": "runo", "Plama ziemi": "ziemia", "Plama piasku": "piasek", "Polanka": "trawa",
    "Polanka brzeg": "mech", "Posadzka": "lupek", "Grządka": "ziemia", "Plama światła": "gladkie", "Dróżka": "ziemia",
    "Dróżka kamienna": "lupek", "Koleina": "ziemia", "Płyta ścieżki": "lupek", "Sadzawka": "gladkie", "Kaskada": "gladkie",
    "Mostek kamień": "lupek", "Mostek balustrada": "lupek", "Mostek słupek": "lupek",
    "Wydma": "piasek", "Skała kaskady": "lupek", "Urwisko": "lupek", "Urwisko mech": "mech",
    # rośliny
    "Liść żyłka": "gladkie", "Liść u nasady": "gladkie", "Liana liść": "gladkie", "Korzeń skrzydło": "drewno",
    "Kokos": "drewno", "Kokos skorupa": "drewno", "Kokos miąższ": "gladkie", "Bambus": "drewno", "Bambus kolanko": "gladkie",
    "Bambus liście": "gladkie", "Kwiat łodyga": "gladkie", "Kwiat liść": "gladkie", "Kwiat kielich": "gladkie",
    "Łodyga kielicha": "gladkie", "Płatek": "gladkie", "Tarcza kwiatu": "gladkie", "Pręcik": "gladkie", "Pąk": "gladkie",
    "Kaktus": "gladkie", "Wiszący most deska": "deski", "Dach z liści": "gladkie",
    # ruiny, posągi, budowle
    "Taras płyta": "lupek", "Taras fuga": "lupek", "Słupek": "lupek", "Posąg głaz": "lupek", "Posąg brwi": "lupek",
    "Posąg nos": "lupek", "Posąg usta": "gladkie", "Posąg głowa": "lupek", "Posąg maska": "lupek", "Posąg oczodół": "gladkie",
    "Posąg kaptur": "lupek", "Posąg cokół": "lupek", "Posąg tułów": "lupek", "Posąg tarcza": "lupek", "Posąg ręka": "lupek",
    "Kolumna baza": "lupek", "Kolumna trzon": "lupek", "Kolumna mech": "mech", "Kolumna bęben": "lupek", "Stela": "lupek",
    "Mur ruin": "lupek", "Schody stopień": "lupek", "Schody próg": "lupek", "Schody rampa": "lupek", "Płyta ruin": "lupek",
    "Kaplica cokół": "lupek", "Kaplica ściana": "lupek", "Kaplica dach": "lupek", "Kaplica wejście": "gladkie",
    "Nadproże": "lupek", "Świątynia taras": "lupek", "Świątynia gzyms": "lupek", "Świątynia schody": "lupek",
    "Kapliczka": "lupek", "Kapliczka dach": "lupek", "Kapliczka szczyt": "metal", "Kapliczka wejście": "gladkie",
    "Posadzka okrągła": "lupek", "Fuga": "lupek", "Filar kręgu": "lupek", "Mur bramy": "lupek", "Filar bramy": "lupek",
    "Pochodnia kij": "drewno", "Pochodnia misa": "lupek",
}
FAKTURY_DODATKOWE = dict(FAKTURY_LASU_I_BAGNA, **FAKTURY_DZUNGLI)
# nazwy, które w faktury.py mają rolę lasu, a w Dżungli inną (nazwy zostają): Płyta = ziemia (podłoże 5C3A22)
NADPISZ_ROLE = {"Płyta": "ziemia"}
ODCINKI_RAPORTU = [
    (-1e9, 940.0 + D, "za bramą Bagna (u 1876–1880)"),
    (940.0 + D, 1004.0 + D, "Taras Przybycia"),
    (1004.0 + D, 1016.0 + D, "Turkusowy strumyk"),
    (1016.0 + D, 1208.0 + D, "Polana Zwijogonów"),
    (1208.0 + D, 1228.0 + D, "Mostek nad Kaskadą"),
    (1228.0 + D, 1420.0 + D, "Kwietnik Gębokwiatów"),
    (1420.0 + D, 1436.0 + D, "bambusowa przesieka"),
    (1436.0 + D, 1628.0 + D, "Gaj Kokosów"),
    (1628.0 + D, 1644.0 + D, "omszałe schody"),
    (1644.0 + D, 1744.0 + D, "Ruiny Pancernika"),
    (1744.0 + D, 1760.0 + D, "Brama Posągów"),
    (1760.0 + D, 1848.0 + D, "Krąg Stu Lian"),
    (1848.0 + D, 1876.0 + D, "przedbramie i Brama do Pustyni"),
    (1876.0 + D, 1e9, "zapowiedź Pustyni (u 2816–2846)"),
]


def naloz_faktury(s):
    """faktury.naloz starego lasu, potem nazwy dodatkowe (las-pas + Bagno + Dżungla) i nadpisane role. Zwraca nazwy bez
    roli."""
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
    """znaczniki.json w tym samym układzie co las-pas i Bagno (punkty pasa [u, y, v] i od razu świat [X, Y, Z] w polach
    *_swiat). Różnica rodzaju: brama na końcu to `brama_pustyni` (w Bagnie `brama_dzungli`)."""
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
    stale = sorted({"/".join(g.split("/")[:2]) for g in grupy if g.startswith(("Punkty/", "BramaPustyni/"))})
    niski = sorted({"/".join(g.split("/")[:3]) for g in grupy if g.startswith(("Kulisy/Lewa/", "Kulisy/Prawa/", "Tlo/"))})
    m = K.miejsca
    pr = m["przybycie"]
    bp = m["brama_pustyni"]
    st_ = P["straznik"]
    d = {
        "opis": "Znaczniki Dżungli-pasa (PROPOZYCJA) dla następnych etapów: potwory w przegrodach, teleport, przelot kamery, "
                "brama do Pustyni, mgła, streaming. Generuje swiat/dzungla_pas/generuj.py z swiat/dzungla_pas/plan.py. Punkty w "
                "UKŁADZIE PASA [u, y, v] (ten sam co las-pas i Bagno); pola *_swiat = świat Studio [X, Y, Z]. Układ = Bagno + 940.",
        "kontener": {"nazwa": KONTENER, "uklad": "pas: u wzdłuż (od początku lasu), v w poprzek (v > 0 po prawej ręce idącego "
                                                 "do bramy), y w górę",
                     "wzor": "swiat = (%g + u; y; %g + v), bez obrotu" % (X0, Z0), "X0": X0, "Z0": Z0, "obrot_y": 0},
        "plan": "swiat/dzungla_pas/plan_dzungli.json",
        "pas": {"szerokosc": P["pas"]["szerokosc"], "kulisy": P["pas"]["kulisy"], "u_od": P["pas"]["u_od"], "u_do": P["pas"]["u_do"],
                "niewidzialna_sciana_v": 38, "zakres_czesci_u": [U_MIN, U_MAX], "zakres_czesci_v": [-88, 88],
                "przesuniecie_wzgledem_bagna_u": D},
        "sasiad_bagno": {"kontener": "Workspace/BagnoPas", "usun_przed_budowa": "Workspace/BagnoPas/ZapowiedzDzungli",
                         "dlaczego": "zapowiedź Dżungli Bagna-pasa (u 1876–1906, niewidzialna ściana u 1905) stoi tam, gdzie Taras "
                                     "Przybycia; reszta Bagna-pasa zostaje (kulisy i płyta do u 1906, Krzywa Kładka do u 1902, "
                                     "palisada bramy u 1872–1877)"},
        "przegrody": [{"id": q["id"], "nazwa": q["nazwa"], "u": [q["u_od"], q["u_do"]],
                       "pod": [{"id": p["id"], "nazwa": p["nazwa"], "u": [p["u_od"], p["u_do"]]} for p in q.get("pod", [])]}
                      for q in P["przegrody"]],
        "przejscia": [{"id": t["id"], "nazwa": t["nazwa"], "u": [t["u_od"], t["u_do"]], "otwarcie_v": t["otwarcie"],
                       "wys_w_otwarciu": t["wys_w_otwarciu"]} for t in P["przejscia"]],
        "start": {"opis": "start biomu = punkt przybycia (teleport i wejście z Bagna przez bramę)",
                  "punkt": [pr["u"], 0.0, pr["v"]], "punkt_swiat": sw(pr["u"], 0.0, pr["v"])},
        "przybycie": {"punkt": [pr["u"], 0.0, pr["v"]], "punkt_swiat": sw(pr["u"], 0.0, pr["v"]),
                      "patrz_na": [pr["patrz"][0], 0.0, pr["patrz"][1]], "patrz_na_swiat": sw(pr["patrz"][0], 0.0, pr["patrz"][1]),
                      "uwaga": "punkt stoi na Tarasie Przybycia (wierzch 0,5)"},
        "inkubator": {"opis": "stanowisko jajka (inkubator Dżungli, D-060) — punkt E w grupie Punkty/StanowiskoJajka; jajko "
                              "Dżungli zrobi agent petów",
                      "punkt": [m["jajko"]["u"], 0.0, m["jajko"]["v"]], "punkt_swiat": sw(m["jajko"]["u"], 0.0, m["jajko"]["v"]),
                      "grupa": KONTENER + "/Punkty/StanowiskoJajka"},
        "miejsca": [dict(x, punkt=[x["u"], x.get("y", 0.0), x["v"]], punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) for x in P["miejsca"]],
        "punkty_przybycia": [dict(x, punkt_swiat=sw(x["u"], x.get("y", 0.0), x["v"])) if "u" in x else dict(x) for x in P["punkty_przybycia"]],
        "strefy_spokoju": [dict(z_, prostokat_swiat={"x": [X0 + z_["u"][0], X0 + z_["u"][1]], "z": [Z0 + z_["v"][0], Z0 + z_["v"][1]]})
                           for z_ in P["strefy_spokoju"]],
        "strefy": [{"id": st["id"], "podbiom": st["podbiom"], "pod": st["pod"], "potwor": st["potwor"], "klasa": st["klasa"],
                    "model": st.get("model"), "wariant": st.get("wariant"), "poziomy": st["poziomy"],
                    "poziomy_rowny": st["poziomy_rowny"], "poziomy_status": st.get("poziomy_status"), "naraz": st["naraz"],
                    "max": st["max"], "srodek": [st["srodek"][0], 0.0, st["srodek"][1]], "r": st["r"],
                    "wezly": [[u, 0.0, v] for u, v in st["trasa"]], "wezly_swiat": [sw(u, 0.0, v) for u, v in st["trasa"]],
                    "domy": [[u, 0.0, v] for u, v in st["dom"]["pts"]], "domy_swiat": [sw(u, 0.0, v) for u, v in st["dom"]["pts"]],
                    "dom_opis": st["dom"]["opis"], "odrodzenie_s": st["odrodzenie_s"], "odrodzenie_stale": st.get("odrodzenie_stale", False),
                    "grupa": st.get("grupa"), "zachowanie": st["zachowanie"], "pole": st["pole"]} for st in P["strefy"]],
        "straznik": dict(st_, miejsce_swiat=sw(st_["miejsce"][0], 0.3, st_["miejsce"][1]),
                         arena_srodek_swiat=sw(st_["arena"]["srodek"][0], 0.3, st_["arena"]["srodek"][1]),
                         uwaga="Wąż stoi na okrągłej kamiennej posadzce (wierzch 0,3)"),
        "zasady": P["zasady"], "rozmiary": P["rozmiary"],
        "przelot_kamery": dict(P["przelot_kamery"], punkty_swiat=[
            {"t": p["t"], "poz": sw(p["poz"][0], p["poz"][2], p["poz"][1]), "patrz": sw(p["patrz"][0], p["patrz"][2], p["patrz"][1])}
            for p in P["przelot_kamery"]["punkty"]],
            uwaga="w planie poz/patrz = [u, v, wysokość]; w punkty_swiat = [X, Y, Z]; krzywa: sprawdz_plan.krzywa_kamery"),
        "brama_pustyni": {"rodzaj": "brama do następnego biomu (w lesie-pasie pole nazywa się brama_bagna, w Bagnie brama_dzungli)",
                          "grupa_wrot": KONTENER + "/BramaPustyni/Wrota", "grupa_palisady": KONTENER + "/BramaPustyni/Palisada",
                          "u": bp["u"], "otwarcie_v": bp["otwarcie"],
                          "jak_otwierac": "jak brama do Bagna i do Dżungli: u klienta gracza, który pokonał Węża Stu Lian, części "
                                          "grupy Wrota CanCollide = false i LocalTransparencyModifier = 1; serwer pilnuje atrybutu "
                                          "gracza",
                          "za_brama": "ZapowiedzPustyni (u 2816–2846) z niewidzialną ścianą na u 2845 — do usunięcia, gdy powstanie "
                                      "Pustynia; tabliczkę „PUSTYNIA — WKRÓTCE” wypisuje gra"},
        "punkty_e": punkty_e,
        "punkty_orientacyjne": [dict(z_, punkt_swiat=sw(z_["u"], 0.0, z_["v"])) for z_ in P["punkty_orientacyjne"]],
        "niewidzialne_sciany": "Kulisy/Niewidzialne (|v| = 38 od u 1904 do 2844), ZapowiedzPustyni (u 2845); za plecami — "
                               "palisada bramy do Dżungli Bagna-pasa (u 1874)",
        "mgla": {"opis": "mgiełka z części tylko nad wodą (grupa Mgla: strumienie, kaskady, wodospad, sadzawka Kręgu) + ciepła "
                         "zielona mgła lokalna u gracza (skrypt klienta jak w lesie-pasie i Bagnie), wspólnego Lighting nie "
                         "zmieniamy",
                 "prostokat_swiat": {"x": [X0 + 936 + D, X0 + 1880 + D], "z": [Z0 - 60, Z0 + 60]},
                 "propozycja": {"FogColor": "7FBF8A", "FogStart": 40, "FogEnd": 380, "przejscie_od_bagna_st": 40,
                                "Atmosphere_jak_arena": {"Density": 0.34, "Offset": 0.16, "Haze": 1.5, "Glare": 0.0,
                                                         "Color": "8FC79A", "Decay": "4E8A5A"}}},
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
    P = plan_dzungli.zbuduj()
    s = Scena(KONTENER, paleta=PALETA)
    K = Dzungla(ziarno, P)
    Z = ZasadyDzungli(K)
    stat = {}
    with s.uklad(pos=(K.X0, 0.0, K.Z0)):
        teren.plyta_i_plamy(s, K)
        teren.wody(s, K)
        teren.polanki(s, K)
        teren.kwietnik(s, K)
        teren.tropy(s, K)
        miejsca.taras_przybycia(s, K)
        miejsca.chatka_na_drzewie(s, K)
        miejsca.wielki_kielich(s, K)
        miejsca.kaskada_gaju(s, K)
        miejsca.zapadla_kaplica(s, K)
        miejsca.posagi_straznikow(s, K)
        miejsca.krag_stu_lian(s, K)
        miejsca.swiatynia_stu_lian(s, K)
        miejsca.brama_pustyni(s, K)
        stat["drozka_odcinkow"] = teren.drozka(s, K, Z)
        miejsca.strumyk(s, K)
        miejsca.kaskady(s, K)
        miejsca.bambusowa_przesieka(s, K)
        miejsca.kamienne_schody(s, K)
        miejsca.domy(s, K, Z)
        miejsca.przedbramie(s, K)
        miejsca.zapowiedz_pustyni(s, K, Z)
        stat["parasole"] = miejsca.parasole_nad_sciezka(s, K, Z)
        stat["ozdoby"] = miejsca.ozdoby(s, K, Z)
        stat["mosty"] = kulisy.mosty_z_lian(s, K, Z)
        stat["ruiny_kulis"] = kulisy.ruiny_w_kulisach(s, K, Z)
        stat["kulisy"] = kulisy.kulisy(s, K, Z)
        stat["tlo"] = kulisy.tlo(s, K, Z)
        kulisy.niewidzialne_sciany(s, K)
        stat["swiatlo"] = teren.plamy_swiatla(s, K)
        stat["lilie"] = teren.lilie(s, K, Z)
        stat["mgla"] = teren.mgla(s, K, Z)
        stat["detale_drozki"] = kulisy.detale_drozki(s, K, Z)
        stat["runo"] = kulisy.runo(s, K, Z)
    return s, K, Z, P, stat


def main():
    ap = argparse.ArgumentParser(description="Generator Dżungli-pasa (Workspace/DzunglaPas)")
    ap.add_argument("--ziarno", type=int, default=11)
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    s, K, Z, P, stat = generuj(a.ziarno)
    plan_dzungli.zapisz(P)
    brak_roli = naloz_faktury(s)
    s.zapisz(a.wyj)
    gl, od = raport(s, K)
    ks = stat["kulisy"]
    print("KULISY: przód %d (nie zmieściło się %d), skraj %d, drugi rząd %d, głąb %d, liany %d; tło %d sylwetek; mosty z lian %d, "
          "ruiny %d" % (ks["przod"], ks["przod_odrzucone"], ks["skraj"], ks["srodek"], ks["glab"], ks["liany"], stat["tlo"],
                        stat["mosty"], stat["ruiny_kulis"]))
    print("DETALE: Dróżka %d odcinków, parasole nad Dróżką %d, przy Dróżce %d, runo %d, liście na wodzie %d, plamy światła %d, "
          "mgiełka %d" % (stat["drozka_odcinkow"], stat["parasole"], stat["detale_drozki"], stat["runo"], stat["lilie"],
                          stat["swiatlo"], stat["mgla"]))
    print("OZDOBY PRZEGRÓD: " + ", ".join("%s %d" % kv for kv in stat["ozdoby"].items()))
    print("FAKTURY: %s" % ("każda część ma rolę" if not brak_roli else "BEZ ROLI: " + ", ".join(brak_roli)))
    znaczniki(s, K, os.path.join(TU, "znaczniki.json"), {"czesci": len(s.czesci), "na_odcinek": od, "na_grupe": gl})
    uwagi = s.sprawdz(min_y=-3.0, limit_czesci=LIMIT)
    print("SPRAWDZ (biblioteka): %d ostrzeżeń" % len(uwagi))
    for u in uwagi[:30]:
        print("  UWAGA:", u)
    print("ZAPISANO:", os.path.relpath(a.wyj, REPO).replace(os.sep, "/"), "+ swiat/dzungla_pas/znaczniki.json, plan_dzungli.json")
    print("Kontrola: python -B swiat/dzungla_pas/sprawdz.py")
    return 1 if brak_roli or len(s.czesci) > LIMIT else 0


if __name__ == "__main__":
    sys.exit(main())
