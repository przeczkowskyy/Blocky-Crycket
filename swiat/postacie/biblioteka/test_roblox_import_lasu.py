# -*- coding: utf-8 -*-
"""Sprawdzian roblox_import_lasu.py bez Studio i bez Open Cloud (niczego nie wgrywa, z niczym się nie łączy).

    python -B swiat/postacie/biblioteka/test_roblox_import_lasu.py

1. Plan (domyślny tryb) na prawdziwych plikach z wynik/: sześć pełnych wierszy w stałej kolejności, kod 0, żadnego
   importu modułu studio_mcp i żadnego nowego ani zmienionego pliku w wynik/_roblox.
2. Ocena (ocen) na PRAWDZIWYM wyniku importu Rycerza z 13.11.2026 (wynik/_roblox/import_rycerz_fbx.json): ma wyjść
   „zgodny”, bo ten import obejrzał człowiek; zepsute kopie tego wyniku muszą wyjść „niezgodny”.
3. Ocena wariantów szkieletu na danych slime'a i trolla z GLB: kości Bone z rodzicami jak w GLB — zgodny; brak kości
   Gora — niezgodny; sztywne części ze stawami — troll zgodny, slime niezgodny (Cialo i Gora nie mają siatki).
4. Przebieg z --tak-wgraj na udawanym roblox_import.main (katalog stanu w folderze tymczasowym): model „zgodny” jest
   pomijany bez wywołania, model z gotowym plikiem wyniku jest oceniany z pliku bez wstawiania, przerwanie zatrzymuje
   całość z kodem błędu i zapisuje tabelę. --sprawdz-ponownie woła roblox_import z --sprawdz <nazwa> --napraw (bez
   --tak-wgraj), a bez numeru zasobu staje bez wywołania.
5. RootPart rigu z kości (Troll 15.11.2026): stary pomiar (z RootPart, osie świata) — niezgodny; pomiar siatek w układzie
   modelu — zgodny; stopy 0,91 nad ziemią, skala nieprzywrócona albo model na oparciu ławki — niezgodny; części miasta
   w obrysie — do obejrzenia.
"""
import contextlib
import copy
import io
import json
import math
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
os.environ["STUDIO_MCP_CMD"] = "nie-ma-takiego-polecenia-sprawdzian-roblox-import-lasu"

from swiat.postacie import roblox_import as ri  # noqa: E402
from swiat.postacie import roblox_import_lasu as rl  # noqa: E402

ZLE = []


def sprawdz(warunek, opis):
    if not warunek:
        ZLE.append(opis)


def uruchom(*argv):
    out = io.StringIO()
    kod = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            kod = rl.main(list(argv)) or 0
        except SystemExit as e:
            kod = 0 if e.code in (None, 0) else (e.code if isinstance(e.code, int) else 1)
            if isinstance(e.code, str):
                print("[exit] " + e.code)
    return kod, out.getvalue()


def spis_katalogu(p):
    if not os.path.isdir(p):
        return {}
    return {n: os.path.getmtime(os.path.join(p, n)) for n in os.listdir(p)}


def test_planu():
    przed = spis_katalogu(ri.STAN_DIR)
    kod, out = uruchom()
    po = spis_katalogu(ri.STAN_DIR)
    sprawdz(kod == 0, "plan: kod %s\n%s" % (kod, out[-2000:]))
    sprawdz("studio_mcp" not in sys.modules, "plan zaimportował studio_mcp")
    sprawdz(przed == po, "plan zmienił wynik/_roblox: %r" % (set(po.items()) ^ set(przed.items())))
    naglowki = [l for l in out.splitlines() if l.startswith("[")]
    sprawdz([l.split()[1] for l in naglowki] == rl.KOLEJNOSC, "plan: kolejność wierszy %r" % naglowki)
    for pole in ("plik:", "stan:", "wynik:", "szkielet:", "siatki:", "klipy", "przesunięcia:", "skóra:", "świecenie:",
                 "przód:", "miejsce:", "oczekiwane:"):
        sprawdz(out.count("  " + pole) == 6, "plan: pole %r nie jest w każdym z 6 wierszy (%d)" % (pole, out.count("  " + pole)))
    sprawdz("BRAK" not in out and "braków 0" in out, "plan: braki w plikach:\n%s" % out[-1500:])
    sprawdz("Dol_Geo: 1104 z 1136" in out, "plan: skóra slime'a z GLB")
    kod, out = uruchom("--tylko", "lesny_slime,zwiadowca")
    naglowki = [l.split()[1] for l in out.splitlines() if l.startswith("[")]
    sprawdz(kod == 0 and naglowki == ["zwiadowca", "lesny_slime"], "plan --tylko: %r" % naglowki)
    kod, out = uruchom("--tylko", "rycerz")
    sprawdz(kod != 0, "plan --tylko z nieznanym modelem przeszedł")
    # bezpieczniki (15.11, kontrola niezależna): sha256 przyjętej wersji, trójkąty w pliku, ROZMIESZCZENIE
    kod, out = uruchom()
    sprawdz(out.count("(wersja przyjęta 15.11)") == 6, "plan: nie każdy plik ma sha256 wersji przyjętej")
    zw = rl.oczekiwania("zwiadowca")
    sprawdz(zw["trojkaty"] == 3374 and zw["trojkaty_razem"] == 4198, "Zwiadowca: trójkąty w pliku %r" % zw["trojkaty"])
    stary = rl.PRZYJETE_SHA256["zwiadowca"]
    try:
        rl.PRZYJETE_SHA256["zwiadowca"] = "0" * 64
        e = rl.oczekiwania("zwiadowca")
        sprawdz(any("sha256" in b for b in e["braki"]), "inny sha256 nie dał braku")
        kod, out = uruchom("--tylko", "zwiadowca")
        sprawdz(kod != 0 and "INNY NIŻ PRZYJĘTY" in out, "plan z innym sha256: kod %s" % kod)
    finally:
        rl.PRZYJETE_SHA256["zwiadowca"] = stary
    # Rycerz jest w roblox_postac.ROZMIESZCZENIE, a przyjętego sha256 lasu nie ma: oba braki muszą wyjść
    br = oczek_rycerza()["braki"]
    sprawdz(any("ROZMIESZCZENIE" in b for b in br) and any("sha256" in b for b in br), "Rycerz: braki %r" % br)


def oczek_rycerza():
    """Oczekiwania Rycerza w układzie narzędzia lasu: miejsce i kierunek z roblox_postac.ROZMIESZCZENIE."""
    rl.PROFILE["rycerz"] = {"miejsce": (32.0, 17.5), "przod": None}
    rl.POWODY["rycerz"] = "sprawdzian"
    try:
        e = rl.oczekiwania("rycerz")
    finally:
        del rl.PROFILE["rycerz"], rl.POWODY["rycerz"]
    fx, fz = 21.4 - 32.0, 18.0 - 17.5                     # roblox_import liczy kierunek z „poz” na „patrz”
    d = (fx * fx + fz * fz) ** 0.5
    e["kierunek_celu"] = [fx / d, fz / d]
    return e


def test_oceny_rycerza():
    p = os.path.join(ri.STAN_DIR, "import_rycerz_fbx.json")
    if not os.path.isfile(p):
        print("  (pominięte: brak %s)" % p)
        return
    with open(p, encoding="utf-8") as f:
        wynik = json.load(f)
    e = oczek_rycerza()
    werdykt, spr, rodzaj = rl.ocen(e, wynik)
    zle = [x for x in spr if x["wynik"] == "nie"]
    sprawdz(werdykt == "zgodny" and rodzaj == "R15", "Rycerz 13.11: %s %s, niezgodne: %r" % (werdykt, rodzaj, zle))
    sprawdz(len(e["siatki"]) == 15 and e["poza_plikiem"] == ["rycerz_miecz_Akc"],
            "Rycerz: siatek w pliku 15 (miecza nie ma w FBX): %r" % e["poza_plikiem"])
    for opis, zmien in (
            ("jedna siatka mniej", lambda w: w["kontrola_po"]["klasy"].__setitem__("MeshPart", 14)),
            ("skala ×0,5", lambda w: w["kontrola_przed"].__setitem__("wymiary", [1.0, 2.855, 2.4])),
            ("lustro", lambda w: w["kontrola_po"].__setitem__("lewa_po_lewej", False)),
            ("tyłem", lambda w: w["kontrola_po"].__setitem__("przod", [0.9987, -0.0513])),
            ("bez zaczepu dłoni", lambda w: w["kontrola_po"].__setitem__(
                "zaczepy", [z for z in w["kontrola_po"]["zaczepy"] if not z.startswith("RightGripAttachment@")])),
            ("na dachu straganu", lambda w: w["naprawa"].__setitem__("kroki", ["postawiono w (32.3; 6.10; -676.0)"])),
            ("bez koloru", lambda w: w["kontrola_po"]["siatki"][0].__setitem__("colormap", "")),
            ("błąd kroku", lambda w: w.__setitem__("bledy", ["zrzut 0: brak obrazu"]))):
        w = copy.deepcopy(wynik)
        zmien(w)
        sprawdz(rl.ocen(e, w)[0] == "niezgodny", "Rycerz zepsuty (%s) wyszedł zgodny" % opis)


def wynik_kosci(e, bez=(), rodzic_zly=None):
    """Udawany wynik importu z kośćmi Bone ułożonymi jak w GLB."""
    g = e["glb"]
    drzewo = []
    gl = {}
    for k in g["kosci"]:
        r = g["rodzice"][k]
        gl[k] = gl.get(r, -1) + 1 if r else 0
    for k in g["kosci"]:
        if k in bez:
            continue
        drzewo.append({"n": k, "r": (rodzic_zly if k == "Glowa" and rodzic_zly else g["rodzice"][k]) or "RootPart",
                       "g": gl[k], "kr": bool(g["rodzice"][k])})
    siatki = [{"n": n, "tekstura": "", "colormap": "rbxassetid://1"} for n in e["siatki"]]
    zaczepy = ["%s@X" % z for z in e["zaczepy"]]
    wym = list(e["wymiary"])
    kontrola = {"klasy": {"MeshPart": len(siatki), "Bone": len(drzewo)}, "siatki": siatki, "zaczepy": zaczepy,
                "kosci_drzewo": drzewo, "wymiary": [wym[2], wym[1], wym[0]], "przod": e["kierunek_celu"], "lewa_po_lewej": True}
    return {"asset": "1", "model": {"nazwa": e["nazwa"] + " (import FBX)"}, "kontrola_przed": kontrola,
            "kontrola_po": copy.deepcopy(kontrola), "naprawa": {"kroki": ["postawiono w (1.0; 0.25; 2.0)"]}}


def czesci_rigu(wym, kat, y_stop):
    """Dane części (czesci_cf) rigu z kości: jedna siatka o wymiarach wym = [szer., wzrost, głęb.] stopami na y_stop,
    obrócona wokół pionu o kat, i niewidoczny RootPart 1,82 studa środkiem na wysokości stóp (jak Troll 15.11.2026)."""
    c, s = math.cos(kat), math.sin(kat)
    obrot = [c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c]
    return {"czesci_cf": [{"n": "Tulow_Geo", "k": "MeshPart", "cf": [0.0, y_stop + wym[1] / 2, 0.0] + obrot, "s": list(wym), "t": 0},
                          {"n": "RootPart", "k": "Part", "cf": [0.0, y_stop, 0.0] + obrot, "s": [1.82] * 3, "t": 1}],
            "przod": [s, c]}


def test_rootpart():
    """Leśny Troll 15.11.2026: RootPart pod stopami i skrzynka w osiach świata dały NIEZGODNY, choć siatki są 1:1."""
    tr = rl.oczekiwania("lesny_troll")
    w = wynik_kosci(tr)
    stara = [11.02, 10.94, 10.18]                         # tak zmierzyła stara kontrola (wszystkie części, osie świata)
    w["kontrola_przed"]["wymiary"] = stara
    sprawdz(rl.ocen(tr, w)[0] == "niezgodny", "troll ze starym pomiarem (z RootPart) wyszedł zgodny")
    kc = tr["kierunek_celu"]
    w["kontrola_przed"].update(czesci_rigu(tr["wymiary"], math.radians(40), 0.91))
    w["kontrola_po"].update(czesci_rigu(tr["wymiary"], math.atan2(kc[0], kc[1]), 0.25))
    werdykt, spr, rodzaj = rl.ocen(tr, w)
    po_n = {x["n"]: x for x in spr}
    sprawdz(werdykt == "zgodny" and rodzaj == "kości (Bone)" and po_n["stopy na podłożu (spód siatek po naprawie)"]["wynik"] == "tak",
            "troll z pomiarem siatek: %s %r" % (werdykt, [x for x in spr if x["wynik"] == "nie"]))
    # stara naprawa postawiła RootPart na podłożu: stopy 0,91 nad ziemią -> niezgodny
    w["kontrola_po"].update(czesci_rigu(tr["wymiary"], math.atan2(kc[0], kc[1]), 0.25 + 0.91))
    sprawdz(rl.ocen(tr, w)[0] == "niezgodny", "troll ze stopami nad ziemią wyszedł zgodny")
    # skala przywrócona do 1:1 to tylko informacja; skala inna niż 1 po przywróceniu -> niezgodny
    w["kontrola_po"].update(czesci_rigu(tr["wymiary"], math.atan2(kc[0], kc[1]), 0.25))
    w["przywrocenie_skali"] = {"przed": 0.9086, "po": 1}
    sprawdz(rl.ocen(tr, w)[0] == "zgodny", "troll po przywróceniu skali")
    w["przywrocenie_skali"] = {"przed": 0.9086, "po": 0.9086}
    sprawdz(rl.ocen(tr, w)[0] == "niezgodny", "troll z nieprzywróconą skalą wyszedł zgodny")
    del w["przywrocenie_skali"]
    # Muchomornik 15.11.2026: postawiony na oparciu ławki (podłoże y 3,8) -> niezgodny; części miasta w obrysie: obejrzyj
    w["naprawa"]["kolizje"] = ["Workspace.KrzyweMiasteczko.Rekwizyty.Ławka oparcie"]
    werdykt, spr, _r = rl.ocen(tr, w)
    po_n = {x["n"]: x["wynik"] for x in spr}
    sprawdz(werdykt == "zgodny" and po_n.get("części miasta w obrysie modelu") == "obejrzyj", "kolizje: %r" % po_n)
    w["naprawa"]["kolizje"] = []
    sprawdz({x["n"]: x["wynik"] for x in rl.ocen(tr, w)[1]}.get("części miasta w obrysie modelu") == "tak", "kolizje puste")
    w["naprawa"]["kroki"] = ["postawiono w (1.0; 3.80; 2.0)"]
    w["kontrola_po"].update(czesci_rigu(tr["wymiary"], math.atan2(kc[0], kc[1]), 3.8))
    sprawdz(rl.ocen(tr, w)[0] == "niezgodny", "model na oparciu ławki (y 3,8) wyszedł zgodny")


def test_wariantow():
    sl = rl.oczekiwania("lesny_slime")
    tr = rl.oczekiwania("lesny_troll")
    w = wynik_kosci(sl)
    werdykt, spr, rodzaj = rl.ocen(sl, w)
    sprawdz(werdykt == "zgodny" and rodzaj == "kości (Bone)", "slime z kośćmi: %s %r" % (werdykt, [x for x in spr if x["wynik"] == "nie"]))
    sprawdz(any(x["n"] == "skóra na dwóch kościach" and x["wynik"] == "obejrzyj" for x in spr), "slime: skóra do obejrzenia")
    sprawdz(rl.ocen(sl, wynik_kosci(sl, bez=("Gora",)))[0] == "niezgodny", "slime bez kości Gora wyszedł zgodny")
    # Root zamieniony na część (jak u Rycerza: HumanoidRootPart) — głębokość o 1 mniejsza, to też zgodny
    w = wynik_kosci(sl, bez=("Root",))
    for k in ("kontrola_przed", "kontrola_po"):
        for x in w[k]["kosci_drzewo"]:
            x["g"] -= 1
    sprawdz(rl.ocen(sl, w)[0] == "zgodny", "slime bez kości Root (głębokość −1): %r"
            % [x for x in rl.ocen(sl, w)[1] if x["wynik"] == "nie"])
    for k in ("kontrola_przed", "kontrola_po"):
        for x in w[k]["kosci_drzewo"]:
            x["g"] -= 1
    sprawdz(rl.ocen(sl, w)[0] == "niezgodny", "głębokość −2 wyszła zgodna")
    sprawdz(rl.ocen(tr, wynik_kosci(tr, rodzic_zly="Biodra"))[0] == "niezgodny", "troll z głową pod biodrami wyszedł zgodny")
    for e, ok in ((tr, "zgodny"), (sl, "niezgodny")):
        w = wynik_kosci(e)
        for k in ("kontrola_przed", "kontrola_po"):
            w[k]["kosci_drzewo"] = []
            w[k]["klasy"] = {"MeshPart": len(e["siatki"]), "AnimationConstraint": len(e["siatki"])}
        werdykt, spr, rodzaj = rl.ocen(e, w)
        sprawdz(werdykt == ok and rodzaj == "sztywne części ze stawami", "%s sztywny: %s (%s)" % (e["modul"], werdykt, rodzaj))
    # świecące siatki muchomornika muszą się odnaleźć po nazwach
    mu = rl.oczekiwania("muchomornik")
    w = wynik_kosci(mu)
    sprawdz(rl.ocen(mu, w)[0] == "zgodny", "muchomornik z kośćmi")
    w["kontrola_po"]["siatki"] = [x for x in w["kontrola_po"]["siatki"] if not x["n"].startswith("Zarodnik0")]
    w["kontrola_po"]["klasy"]["MeshPart"] -= 1
    sprawdz(rl.ocen(mu, w)[0] == "niezgodny", "muchomornik bez siatki zarodnika")
    # znaczniki _Att jako MeshPart: nie psują liczby siatek ani koloru, ale bez Attachment brakuje zaczepów
    w = wynik_kosci(tr)
    for k in ("kontrola_przed", "kontrola_po"):
        w[k]["siatki"] = w[k]["siatki"] + [{"n": z, "tekstura": "", "colormap": ""} for z in tr["znaczniki_att"]]
        w[k]["klasy"]["MeshPart"] += len(tr["znaczniki_att"])
    werdykt, spr, _r = rl.ocen(tr, w)
    po_n = {x["n"]: x["wynik"] for x in spr}
    sprawdz(po_n.get("siatki MeshPart (bez znaczników _Att)") == "tak" and po_n.get("kolor (tekstura albo SurfaceAppearance)") == "tak"
            and po_n.get("znaczniki _Att jako MeshPart (informacja)") == "obejrzyj" and werdykt == "zgodny",
            "troll ze znacznikami jako MeshPart: %r" % po_n)
    w["kontrola_po"]["zaczepy"] = []
    sprawdz(rl.ocen(tr, w)[0] == "niezgodny", "troll bez zaczepów wyszedł zgodny")
    # zaczepy jako znaczniki „_Att” też się liczą
    w = wynik_kosci(tr)
    w["kontrola_po"]["zaczepy"] = ["%s@X" % z.replace("Attachment", "_Att") for z in tr["zaczepy"]]
    sprawdz(rl.ocen(tr, w)[0] == "zgodny", "troll z zaczepami „_Att”")
    # sonda skóry
    sprawdz(rl.ocen_sonde(sl, {"wierzcholki": 1200, "dwa": 1160, "nazwy": ["Dol", "Gora"]})[0] == "tak", "sonda: skóra jest")
    sprawdz(rl.ocen_sonde(sl, {"wierzcholki": 1200, "dwa": 0, "nazwy": ["Dol"]})[0] == "nie", "sonda: skóra zgubiona")
    sprawdz(rl.ocen_sonde(sl, {"wierzcholki": 0, "dwa": 0, "bledy": ["x"]})[0] == "nieznany", "sonda: API nie odpowiada")
    sprawdz(rl.ocen_sonde(sl, {"blad": "to nie jest miejsce gry"})[0] == "błąd", "sonda: błąd miejsca to nie „skóra przepadła”")
    kod = rl.kod_sondy("Leśny Slime (import FBX)", "Dol")
    sprawdz("__" not in kod and '"Leśny Slime (import FBX)"' in kod and str(ri.PLACE_ID) in kod, "sonda: wstawienie parametrów")
    # miejsce: roblox_import odsuwa import o 6,5 studa w lewo od poz — po odsunięciu ma wyjść cel
    poz, f = rl.miejsce_dla_importu((13.0, -17.0))
    lewo = (f[1], -f[0])
    sprawdz(abs(poz[0] + lewo[0] * rl.ODSUNIECIE - 13.0) < 0.05 and abs(poz[1] + lewo[1] * rl.ODSUNIECIE + 17.0) < 0.05,
            "miejsce: odsunięcie nie trafia w cel: %r %r" % (poz, f))


def test_przebiegu():
    tmp = tempfile.mkdtemp(prefix="test_roblox_import_lasu_")
    stare = (ri.STAN_DIR, ri.main, rl.oczekiwania)
    wywolania = []
    try:
        ri.STAN_DIR = tmp
        gotowe = {m: stare[2](m) for m in ("zwiadowca", "lesny_troll")}
        rl.oczekiwania = lambda m, wynik_dir=None: copy.deepcopy(gotowe[m])

        def udawany(argv, profil=None):
            mid = argv[argv.index("--modul") + 1]
            wywolania.append(mid)
            if mid == "lesny_troll":
                raise SystemExit("NIE WIADOMO, CZY ZASÓB POWSTAŁ (sprawdzian)")
            w = wynik_kosci(gotowe[mid])
            w["kontrola_po"]["klasy"].update(Humanoid=1, AnimationConstraint=15)
            w["kontrola_przed"]["klasy"].update(Humanoid=1, AnimationConstraint=15)
            ri.zapisz_stan(ri.sciezka_stanu(mid, "fbx"), {"etap": "zasob", "asset": "77", "moderacja": "Approved"})
            with open(os.path.join(tmp, "import_%s_fbx.json" % mid), "w", encoding="utf-8") as f:
                json.dump(dict(w, asset="77"), f)
            return dict(w, asset="77")
        ri.main = udawany
        kod, out = uruchom("--tylko", "zwiadowca,lesny_troll", "--tak-wgraj")
        t = rl.wczytaj_tabele()
        sprawdz(kod != 0 and wywolania == ["zwiadowca", "lesny_troll"], "przebieg: kod %s, wywołania %r\n%s" % (kod, wywolania, out[-800:]))
        sprawdz(t.get("zwiadowca", {}).get("werdykt") == "zgodny" and t.get("lesny_troll", {}).get("werdykt") == "przerwany",
                "przebieg: tabela %r" % {k: v.get("werdykt") for k, v in t.items()})
        sprawdz(os.path.isfile(os.path.join(tmp, "import_lasu.txt")), "przebieg: brak import_lasu.txt")
        sprawdz("userId" not in json.dumps(t), "tabela nie może mieć numeru konta")
        # wznowienie: zgodny pominięty, przerwany próbuje ponownie (tu znowu przerwanie)
        del wywolania[:]
        kod, out = uruchom("--tylko", "zwiadowca,lesny_troll", "--tak-wgraj")
        sprawdz(wywolania == ["lesny_troll"] and "pomijam" in out, "wznowienie: wywołania %r" % wywolania)
        # wynik jest, tabela go nie zna (np. przerwanie po wstawieniu): ocena z pliku, bez wywołania main
        os.remove(os.path.join(tmp, "import_lasu.json"))
        del wywolania[:]
        kod, out = uruchom("--tylko", "zwiadowca", "--tak-wgraj")
        sprawdz(kod == 0 and wywolania == [] and "NIE wstawiam drugi raz" in out, "ocena z pliku: %r\n%s" % (wywolania, out[-600:]))
        # bezpieczniki wgrania (15.11, kontrola niezależna): bez --tylko, skrót opcji, kolejność
        for argv, opis in ((("--tak-wgraj",), "--tak-wgraj bez --tylko"), (("--tak", "--tylko", "zwiadowca"), "skrót --tak"),
                           (("--tylko", "zwiadowca", "--tak-wg"), "skrót --tak-wg"), (("--mimo-kolejnosci",), "--mimo-kolejnosci bez --tak-wgraj")):
            del wywolania[:]
            kod, out = uruchom(*argv)
            sprawdz(kod != 0 and wywolania == [], "%s: kod %s, wywołania %r" % (opis, kod, wywolania))
        os.remove(os.path.join(tmp, "import_lasu.json"))
        del wywolania[:]
        kod, out = uruchom("--tylko", "lesny_troll", "--tak-wgraj")
        sprawdz(kod != 0 and wywolania == [] and "STOP przed wgraniem" in out, "kolejność: troll przed Zwiadowcą: %r" % wywolania)
        kod, out = uruchom("--tylko", "lesny_troll", "--tak-wgraj", "--mimo-kolejnosci")
        sprawdz(wywolania == ["lesny_troll"], "--mimo-kolejnosci: wywołania %r" % wywolania)
        # --sprawdz-ponownie (15.11.2026): model już wstawiony -> roblox_import --sprawdz <nazwa> --napraw, bez --tak-wgraj;
        # bez numeru zasobu w pliku stanu -> stop bez wywołania
        argumenty = []

        def ponowny(argv, profil=None):
            argumenty.append(list(argv))
            w = wynik_kosci(gotowe["lesny_troll"])
            return dict(w, asset="88", przywrocenie_skali={"przed": 0.9086, "po": 1})
        ri.main = ponowny
        del wywolania[:]
        kod, out = uruchom("--tylko", "lesny_troll", "--sprawdz-ponownie")
        sprawdz(kod != 0 and not argumenty and "STOP" in out, "ponownie bez zasobu: kod %s, %r" % (kod, argumenty))
        ri.zapisz_stan(ri.sciezka_stanu("lesny_troll", "fbx"), {"etap": "zasob", "asset": "88", "moderacja": "Approved"})
        with open(os.path.join(tmp, "import_lesny_troll_fbx.json"), "w", encoding="utf-8") as f:
            json.dump({"asset": "88", "model": {"nazwa": "Leśny Troll (import FBX)"}}, f)
        kod, out = uruchom("--tylko", "lesny_troll", "--sprawdz-ponownie")
        t = rl.wczytaj_tabele()
        sprawdz(kod == 0 and len(argumenty) == 1 and "--napraw" in argumenty[0] and "--tak-wgraj" not in argumenty[0]
                and argumenty[0][argumenty[0].index("--sprawdz") + 1] == "Leśny Troll (import FBX)"
                and t.get("lesny_troll", {}).get("werdykt") == "zgodny" and t["lesny_troll"].get("asset") == "88",
                "ponownie: kod %s, %r, tabela %r\n%s" % (kod, argumenty, t.get("lesny_troll", {}).get("werdykt"), out[-500:]))
        kod, out = uruchom("--tylko", "lesny_troll", "--sprawdz-ponownie", "--tak-wgraj")
        sprawdz(kod != 0 and len(argumenty) == 1, "ponownie z --tak-wgraj powinno odmówić")
    finally:
        ri.STAN_DIR, ri.main, rl.oczekiwania = stare
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for nazwa, fn in (("plan", test_planu), ("ocena Rycerza", test_oceny_rycerza), ("warianty szkieletu", test_wariantow),
                      ("RootPart rigu z kości", test_rootpart), ("przebieg na udawanym imporcie", test_przebiegu)):
        n = len(ZLE)
        fn()
        print("%s: %s" % (nazwa, "zgodne" if len(ZLE) == n else "%d niezgodności" % (len(ZLE) - n)))
    for z in ZLE:
        print("  -", z)
    print("WYNIK:", "ZGODNE" if not ZLE else "NIEZGODNE")
    sys.exit(0 if not ZLE else 1)
