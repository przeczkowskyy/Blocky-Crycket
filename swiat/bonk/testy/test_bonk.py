#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy BONK bez Studio (D-112, etap 1).

    python -B swiat/bonk/testy/test_bonk.py

1. dane: generator aktualny i powtarzalny; krainy, zagrody, gatunki, bramy, starty, dźwięki z prawami gry
2. logika (zrodla/LogikaBonk.luau wykonana w interpreterze tools/walka/luau_mini.py): liczby, Moc, bramy, wiadro
   tempa, wędrówka, wybór celu, lot i HOME RUN, nagrody, profil
3. tempo: rachunek tempo.py w celach (pierwszy BONK ≤ 30 s, bramy 8–10 / 20–25 / ok. 40 min) i zgodny z Luau
4. źródła: kontrola Luau (swiat/las_potwory/sprawdz_luau.py), składnia (parser luau_mini), strażnik Studio, wersja
   --publikacja bez strażnika, zasady sieci (jedyny RemoteEvent od klienta bez argumentów, limit tempa)
5. zapis: znacznik próby z tools/zapis_prob.py trafia też na Workspace/BonkGra, a serwer BONK przy znaczniku nie
   otwiera prawdziwego magazynu (L.magazyn + jedyne GetDataStore w serwerze)
6. zbuduj.py --sucho
"""
import io
import json
import math
import os
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
ZR = os.path.join(PAKIET, "zrodla")
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import tempo as TP  # noqa: E402
import zbuduj as ZB  # noqa: E402
import luau_mini as LM  # noqa: E402
import zapis_prob as ZP  # noqa: E402

U, D, PLIKI = DN.wszystkie_pliki()


def czytaj(nazwa):
    with open(os.path.join(ZR, nazwa), encoding="utf-8") as f:
        return f.read()


def interpreter():
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    m = it.globalne.z["math"]
    m.set("log", lambda x, b=None: math.log(x) if b is None else math.log(x, b))
    for n in ("rad", "cos", "sin"):
        m.set(n, getattr(math, "radians" if n == "rad" else n))
    m.set("pi", math.pi)
    return it


IT = interpreter()
L = IT.wykonaj(czytaj("LogikaBonk.luau"), "LogikaBonk")[0]
DL = IT.wykonaj(PLIKI[DN.PLIK_DANYCH], "DaneBonk")[0]


def wolaj(nazwa, *argi):
    a = [LM.do_luau(x) if isinstance(x, (dict, list)) else (float(x) if isinstance(x, (int, float)) and not isinstance(x, bool)
                                                              else x) for x in argi]
    return IT.wywolaj(L.get(nazwa), a)


def jeden(nazwa, *argi):
    return wolaj(nazwa, *argi)[0]


def tab(t):
    return dict(t.d) if isinstance(t, LM.Tabela) else t


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_aktualne_i_powtarzalne(self):
        self.assertEqual(DN.nieaktualne(PLIKI), [], "uruchom python -B swiat/bonk/dane.py")
        self.assertEqual(DN.dane(DN.ustawienia())["skrot"], D["skrot"])
        self.assertTrue(PLIKI[DN.PLIK_DANYCH].split("]]\n", 1)[1].startswith(DN.STRAZNIK))

    def test_1b_krainy_po_kolei_wzdluz_x(self):
        K = D["krainy"]
        self.assertEqual([k["id"] for k in K], ["las", "bagno", "dzungla"])
        for a, b in zip(K, K[1:]):
            self.assertAlmostEqual(a["xDo"], b["xOd"], msg="krainy stykają się")
            self.assertAlmostEqual(a["brama"]["x"], a["xDo"], msg="brama na granicy krain")
        for k in K:
            self.assertTrue(k["xOd"] < k["start"][0] < k["brama"]["x"], k["id"])
            for z in k["zagrody"]:
                self.assertTrue(k["start"][0] < z["srodek"][0] < k["brama"]["x"], z["id"])
                self.assertGreaterEqual(len(z["wezly"]), z["ile"], "co najmniej tyle węzłów, ile potworów")
                for w in z["wezly"]:
                    self.assertLess(abs(w[2] - k["start"][2]), 34, "węzły w pasie (niewidzialne ściany |v| = 38)")

    def test_1c_coraz_ciezsze_i_bramy_rosna(self):
        hp = [D["gatunki"][z["gatunek"]]["hp"] for k in D["krainy"] for z in k["zagrody"]]
        moc = [D["gatunki"][z["gatunek"]]["moc"] for k in D["krainy"] for z in k["zagrody"]]
        self.assertEqual(hp, sorted(hp))
        self.assertEqual(moc, sorted(moc))
        bramy = [k["brama"]["wymagana"] for k in D["krainy"]]
        self.assertEqual(bramy, sorted(bramy))
        self.assertEqual(hp[0], 1, "pierwszy potwór pada od jednego ciosu przy Mocy 1")

    def test_1d_modele_i_gatunki(self):
        for g, G in D["gatunki"].items():
            w = DN.wzorzec(g)
            self.assertEqual(len(w["bryly"]), G["czesci"])
            self.assertGreater(G["promien"], 0.5)
            for b in w["bryly"]:
                self.assertIn(b[0], (0, 1, 2, 3, 4))
                self.assertTrue(re.fullmatch(r"[0-9A-Fa-f]{6}", b[10]), b[10])
        self.assertLess(sum(G["czesci"] for G in D["gatunki"].values()), 2600)

    def test_1e_dzwieki_z_prawami(self):
        Z = D["dzwieki"]
        self.assertGreater(Z["arkusz"], 0, "arkusz efektów wgrany")
        ident = DN.czytaj_json(DN.sciezka_repo("swiat/dzwiek_gra/identyfikatory.json"))
        zakazane = {ident["muzyka"]["muzyka_06_bagno_petla"], ident["muzyka"]["muzyka_07_dzungla_petla"]}
        for k, idn in Z["muzyka"].items():
            self.assertGreater(idn, 0, k)
            self.assertNotIn(idn, zakazane, "muzyka Bagna i Dżungli nie ma praw gry")
        for rola in ("cios", "bonk", "home_run", "monety", "plask"):
            e = Z["efekty"][rola]
            self.assertLess(e["od"], e["koniec"], rola)

    def test_1f_przesuniecie_daleko_od_gry(self):
        p = U["przesuniecie"]
        self.assertGreaterEqual(math.hypot(p[0], p[2]), 1000, "mapa BONK daleko od map pasów obecnej gry")


# ============================================================================================== 2. logika w Luau
class TestLogiki(unittest.TestCase):
    def test_2a_format(self):
        przypadki = {0: "0", 7: "7", 999: "999", 1000: "1K", 1234: "1.2K", 12345: "12.3K", 123456: "123K",
                     999999: "999K", 1e6: "1M", 3.4e6: "3.4M", 5.67e9: "5.6B", 2.5e12: "2.5T"}
        for n, t in przypadki.items():
            self.assertEqual(jeden("format", n), t, n)
            self.assertEqual(ZB.format_liczby(n), t, "lustro w zbuduj.py (napisy bram w Edit)")

    def test_2b_moc_i_mnozniki(self):
        self.assertEqual(jeden("moc", 10, 1, 1), 10)
        self.assertEqual(jeden("moc", 10, 1.5, 2), 30, "etap 2: pałka × pety")
        self.assertEqual(jeden("moc", 0.2, 1, 1), 1, "najmniej 1")

    def test_2c_krainy_i_bramy(self):
        K = D["krainy"]
        self.assertEqual(jeden("kraina", K[0]["start"][0], DL), 1)
        self.assertEqual(jeden("kraina", K[1]["start"][0], DL), 2)
        self.assertEqual(jeden("kraina", K[2]["brama"]["x"] + 50, DL), 3)
        b1, b2 = K[0]["brama"]["wymagana"], K[1]["brama"]["wymagana"]
        self.assertEqual(jeden("odblokowane", b1 - 1, DL, None, None), 1)
        self.assertEqual(jeden("odblokowane", b1, DL, None, None), 2)
        self.assertEqual(jeden("odblokowane", b2, DL, None, None), 3)
        self.assertEqual(jeden("odblokowane", 1e30, DL, None, None), 3, "za ostatnią bramą nie ma krainy")
        self.assertEqual(jeden("odblokowane", 1, DL, None, 2), 2, "otwartej bramy się nie zamyka")
        self.assertFalse(jeden("mozePrzejsc", 3, 1e30, DL, None))

    def test_2d_wiadro_5_na_sekunde(self):
        stan, przyjete = None, 0
        for i in range(100):                                  # 10 s klikania co 0,1 s (10/s)
            ok, stan = wolaj("wiadro", stan, i * 0.1, 5, 2)
            przyjete += 1 if ok else 0
        self.assertTrue(48 <= przyjete <= 53, przyjete)
        stan, przyjete = None, 0
        for i in range(20):                                   # wolniej niż limit: wszystko przechodzi
            ok, stan = wolaj("wiadro", stan, i * 0.25, 5, 2)
            przyjete += 1 if ok else 0
        self.assertEqual(przyjete, 20)

    def test_2e_wedrowka_i_cel(self):
        self.assertEqual(wolaj("pozycja", 0, 0, 10, 0, 100, 2, 101), [2.0, 0.0])
        self.assertEqual(wolaj("pozycja", 0, 0, 10, 0, 100, 2, 200), [10.0, 0.0])
        self.assertEqual(wolaj("pozycja", 0, 0, 10, 0, 100, 2, 90), [0.0, 0.0])
        lista = [{"x": 5, "z": 0, "promien": 1, "zywy": True}, {"x": 3, "z": 0, "promien": 1, "zywy": False},
                 {"x": 0, "z": 12, "promien": 5, "zywy": True}]
        self.assertEqual(jeden("wybierzCel", 0, 0, lista, 8), 1)
        lista[0]["x"] = 20
        self.assertEqual(jeden("wybierzCel", 0, 0, lista, 8), 3, "duży potwór: liczy się brzeg")
        lista[2]["zywy"] = False
        self.assertIsNone(jeden("wybierzCel", 0, 0, lista, 8))

    def test_2f_lot_i_home_run(self):
        P = DL.get("lot")
        odl = [tab(jeden("lot", m, 100, P))["odl"] for m in (10, 100, 1000, 10000, 1e9)]
        self.assertEqual(odl, sorted(odl), "dalej z nadwyżką Mocy")
        self.assertEqual(odl[-1], U["lot"]["max"])
        self.assertFalse(tab(jeden("lot", 100, 100, P))["homeRun"], "równa walka: bez HOME RUN")
        self.assertTrue(tab(jeden("lot", 1e6, 100, P))["homeRun"])
        x, z = wolaj("koniecLotu", 0, 0, 3, 4, 10, 0)
        self.assertAlmostEqual(x, 6)
        self.assertAlmostEqual(z, 8)
        a = wolaj("punktLotu", 0, 1, 0, 10, 1, 0, 5, 0)
        b = wolaj("punktLotu", 0, 1, 0, 10, 1, 0, 5, 0.5)
        c = wolaj("punktLotu", 0, 1, 0, 10, 1, 0, 5, 1)
        self.assertEqual((a, b, c), ([0.0, 1.0, 0.0], [5.0, 6.0, 0.0], [10.0, 1.0, 0.0]))

    def test_2g_nagroda_i_zycie(self):
        G = LM.do_luau({"hp": 30, "moc": 2, "monety": 2})
        self.assertEqual(wolaj("nagroda", G, False, False, DL), [2.0, 2.0])
        R = U["rzadki"]
        self.assertEqual(wolaj("nagroda", G, True, True, DL), [2.0 * R["monety_x"] * U["lot"]["home_run_monety_x"], 2.0 * R["moc_x"]])
        self.assertEqual(jeden("zycie", G, True, DL), 30 * R["hp_x"])

    def test_2h_profil(self):
        p = tab(jeden("profil", None, DL))
        self.assertEqual((p["moc"], p["monety"], p["odblokowane"], p["v"]), (1, 0, 1, U["zapis"]["wersja_profilu"]))
        zly = {"moc": "dużo", "monety": -5, "odblokowane": 99, "kraina": 7, "samouczek": 1, "obce": True, "najdalej": 1e400}
        p = tab(jeden("profil", zly, DL))
        self.assertEqual((p["moc"], p["monety"], p["odblokowane"], p["kraina"], p["samouczek"], p.get("obce")),
                         (1, 0, 3, 3, False, None))
        dobry = {"moc": 5000.0, "monety": 77.0, "odblokowane": 2.0, "kraina": 2.0, "samouczek": True, "bonki": 12.0}
        p = tab(jeden("profil", dobry, DL))
        self.assertEqual((p["moc"], p["monety"], p["odblokowane"], p["kraina"], p["samouczek"], p["bonki"]),
                         (5000, 77, 2, 2, True, 12))


# ============================================================================================== 3. tempo
class TestTempa(unittest.TestCase):
    def test_3a_w_celach(self):
        zdarzenia, czasy, pierwszy = TP.przebieg(U)
        self.assertEqual(TP.w_celach(U, czasy, pierwszy), [])
        self.assertLessEqual(pierwszy, 30)
        self.assertEqual(len(czasy), 3)

    def test_3b_python_jak_luau(self):
        """tempo.py liczy z tych samych liczb co gra: życie, Moc i nagrody z L.zycie / L.nagroda."""
        for k in D["krainy"]:
            for z in k["zagrody"]:
                G = D["gatunki"][z["gatunek"]]
                GL = LM.do_luau(G)
                self.assertEqual(jeden("zycie", GL, False, DL), U["gatunki"][z["gatunek"]]["hp"])
                self.assertEqual(wolaj("nagroda", GL, False, False, DL)[1], U["gatunki"][z["gatunek"]]["moc"])

    def test_3c_bez_dodatkow_wolniej_niz_z(self):
        """Haczyk etapu 2: mnożnik pałki/petów przyspiesza grę (ta sama symulacja z Mocą ×2)."""
        U2 = json.loads(json.dumps(U))
        for g in U2["gatunki"].values():
            g["hp"] = g["hp"] / 2                  # Moc ×2 ≡ życie / 2 przy tych samych nagrodach
        _, cz1, _ = TP.przebieg(U)
        _, cz2, _ = TP.przebieg(U2)
        self.assertLess(cz2[0], cz1[0])


# ============================================================================================== 4. źródła
class TestZrodel(unittest.TestCase):
    PLIKI = ["LogikaBonk.luau", "EfektyBonk.luau", "InterfejsBonk.luau", "SerwerBonk.server.luau", "KlientBonk.client.luau",
             "DaneBonk.luau"]

    def test_4a_kontrola_statyczna(self):
        self.assertEqual(ZB.sprawdz_zrodla(), [])

    def test_4b_skladnia_i_publikacja(self):
        Z = ZB.zrodla(PLIKI)
        Zp = ZB.zrodla(PLIKI, publikacja=True)
        self.assertEqual(len(Z), 6)
        for (_, n, _, _, t), (_, _, _, _, tp) in zip(Z, Zp):
            LM.Parser(t, n, LM.Interpreter()).program()
            LM.Parser(tp, n + " (publikacja)", LM.Interpreter()).program()
            self.assertTrue(t.split("]]\n", 1)[1].lstrip().startswith(DN.STRAZNIK), n)
            self.assertNotIn("IsStudio() then", tp.split("]]\n", 1)[1][:200], n + ": publikacja bez strażnika na początku")
            self.assertLess(len(t), U["limit_zrodla"])

    def test_4c_siec(self):
        s = czytaj("SerwerBonk.server.luau")
        k = czytaj("KlientBonk.client.luau")
        self.assertEqual(re.findall(r"(\w+)\.OnServerEvent", s), ["evBonk"], "jedyne zdalne wejście od klienta")
        self.assertIn("evBonk.OnServerEvent:Connect(function(gracz: Player)\n", s, "BONK bez argumentów od klienta")
        self.assertIn("L.wiadro(s.wiadro, os.clock(), D.bonk.uderzen_na_s, D.bonk.zapas_uderzen)", s, "limit tempa na serwerze")
        self.assertEqual(re.findall(r"(\w+):FireServer\(([^)]*)\)", k), [("evBonk", "")])
        self.assertNotIn("InvokeServer", k + s)
        for a in ("BonkMoc", "BonkMonety", "BonkOdblokowane"):
            self.assertNotIn('SetAttribute("%s"' % a, k, "klient nie ustawia stanu gracza")

    def test_4d_cudze_ekrany_i_bohater(self):
        k = czytaj("KlientBonk.client.luau")
        self.assertIn("g.Enabled = false", k)
        self.assertIn("przywrocCudze", k)
        self.assertIn('folderUI.Name = "BonkUI"', k, "własny ekran w folderze (wybór klasy wyłącza nowe ScreenGui)")
        s = czytaj("SerwerBonk.server.luau")
        self.assertIn('gracz:SetAttribute("BezBohatera", true)', s)
        with open(os.path.join(REPO, "swiat", "bohater_swiat", "zrodla", "KlientBohatera.client.luau"), encoding="utf-8") as f:
            b = f.read()
        self.assertIn('GetAttribute("BezBohatera")', b, "bohater klasy nie rysuje się graczowi w BONK")


# ============================================================================================== 5. zapis
class Atrapa:
    """Najmniejszy świat Edit dla kodu Luau z tools/zapis_prob.py: workspace z kontenerami, RunService, os.time."""

    def __init__(self, nazwy, czas=1000.0):
        self.it = LM.Interpreter()
        self.kontenery = {}
        ws = LM.Tabela()
        for n in nazwy:
            k = LM.Tabela()
            atr = {"Wygenerowane": True}
            k.set("atr", atr)
            k.set("GetAttribute", lambda _s, a, atr=atr: atr.get(a))
            k.set("SetAttribute", lambda _s, a, v, atr=atr: atr.__setitem__(a, v) if v is not None else atr.pop(a, None))
            self.kontenery[n] = atr
            ws.set(n, k)
        ws.set("FindFirstChild", lambda s, n: s.get(n) if n in self.kontenery else None)
        rs = LM.Tabela()
        rs.set("IsRunning", lambda _s: False)
        game = LM.Tabela()
        game.set("GetService", lambda _s, _n: rs)
        os_ = LM.Tabela()
        os_.set("time", lambda: czas)
        g = self.it.globalne.z
        g["workspace"], g["game"], g["os"] = ws, game, os_


class TestZapisu(unittest.TestCase):
    def test_5a_znacznik_na_bonk_i_stan_gracza(self):
        a = Atrapa(["StanGracza", "BonkGra"])
        w = a.it.wykonaj(ZP.LUAU_START, "start")[0]
        self.assertTrue(w.startswith("OK"), w)
        for n in ("StanGracza", "BonkGra"):
            self.assertEqual(a.kontenery[n][ZP.ATR_DO], 1000 + ZP.CZAS_S, n)
        self.assertEqual(a.it.wykonaj(ZP.LUAU_KONIEC, "koniec")[0], "OK")
        for n in ("StanGracza", "BonkGra"):
            self.assertNotIn(ZP.ATR_DO, a.kontenery[n])
        b = Atrapa(["BonkGra"])                               # sam BONK (np. miejsce bez stanu gracza)
        self.assertTrue(b.it.wykonaj(ZP.LUAU_START, "start")[0].startswith("OK"))
        self.assertEqual(Atrapa([]).it.wykonaj(ZP.LUAU_START, "start")[0], "BRAK")
        self.assertEqual(b.it.wykonaj(ZP.kod_magazynu(None, "BonkGra"), "magazyn")[0], "OK")
        self.assertTrue(b.kontenery["BonkGra"][ZP.ATR_MAGAZYNU])
        self.assertEqual((ZP.ATR_DO, ZP.ATR_MAGAZYNU), (U["zapis"]["znacznik_proby"], U["zapis"]["znacznik_magazynu"]))

    def test_5b_proba_nie_dotyka_prawdziwego_klucza(self):
        Z = DL.get("zapis")
        prawdziwy = U["zapis"]["magazyn"] + U["zapis"]["przyrostek_studio"]
        self.assertEqual(wolaj("magazyn", Z, True, None, 100, False), [prawdziwy, "włączony"])
        self.assertEqual(wolaj("magazyn", Z, True, 1000 + ZP.CZAS_S, 1000, False), [None, "wyłączony (próba gry)"])
        self.assertEqual(wolaj("magazyn", Z, True, 1000 + ZP.CZAS_S, 1000, True),
                         [prawdziwy + U["zapis"]["przyrostek_proby"], "włączony (magazyn próby)"])
        self.assertEqual(wolaj("magazyn", Z, True, 900, 1000, False), [prawdziwy, "włączony"], "znacznik wygasa sam")
        self.assertEqual(wolaj("magazyn", Z, False, 5000, 1000, True), [U["zapis"]["magazyn"], "włączony"], "poza Studio bez znaczenia")
        # serwer otwiera magazyn tylko tam: jedno GetDataStore, z nazwą od L.magazyn
        s = czytaj("SerwerBonk.server.luau")
        self.assertEqual(len(re.findall(r"GetDataStore\(", s)), 1)
        self.assertIn("GetDataStore(nazwa)", s)
        self.assertIn("local nazwa, stan = L.magazyn(Z, RunService:IsStudio(), kontener:GetAttribute(Z.znacznik_proby), os.time(),", s)
        self.assertNotIn("GetDataStore", czytaj("KlientBonk.client.luau"))

    def test_5c_od_edit_do_serwera(self):
        """Znacznik z „trybu Edit” (zapis_prob) → atrybut kontenera → L.magazyn w serwerze: brak magazynu."""
        a = Atrapa(["BonkGra"], czas=5000.0)
        a.it.wykonaj(ZP.LUAU_START, "start")
        atr = a.kontenery["BonkGra"]
        nazwa, stan = wolaj("magazyn", DL.get("zapis"), True, float(atr[ZP.ATR_DO]), 5000.0 + 30, atr.get(ZP.ATR_MAGAZYNU) is True)
        self.assertIsNone(nazwa)
        self.assertEqual(stan, "wyłączony (próba gry)")


# ============================================================================================== 6. zbuduj --sucho
class TestBudowy(unittest.TestCase):
    def test_6a_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True)
        wyj = r.stdout.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, wyj[-2000:])
        self.assertIn("źródła Luau: bez błędów", wyj)
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho", "--publikacja"], capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("PUBLIKACJA", r.stdout.decode("utf-8", "replace"))

    def test_6b_mapa_z_trzech_pasow(self):
        mapa = ZB.dane_mapy(U)
        self.assertEqual([m[0] for m in mapa], ["las", "bagno", "dzungla"])
        p = U["przesuniecie"]
        for nazwa, grupy, materialy, czesci in mapa:
            self.assertTrue(all(g.split("/")[0] in ("Las", "Bagno", "Dzungla") for g in grupy))
            self.assertTrue(all(0 <= c[12] < len(materialy) for c in czesci))
            zz = [c[4] for c in czesci]
            self.assertTrue(-700 + p[2] - 200 < min(zz) and max(zz) < -700 + p[2] + 200, nazwa)
        self.assertEqual(sum(len(m[3]) for m in mapa), 14907)


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
