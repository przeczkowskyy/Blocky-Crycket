# -*- coding: utf-8 -*-
"""Testy podglądu 3D, sesji Studio (bez Studio) i analityki.

Uruchomienie (z katalogu panel/):  python -m unittest testy.test_podglad
Nie potrzebują Roblox Studio ani sieci: Studio jest podmieniane atrapą, dane lądują w katalogu tymczasowym.
"""
import io
import json
import math
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bc import analityka, podglad, rdzen, studio  # noqa: E402
from bc.http import Odp, Zadanie  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

try:
    from PIL import Image
except Exception:                                          # Pillow jest opcjonalny
    Image = None


def zadanie(sciezka="/", params=None, json_cialo=None, lokalny=True, metoda="GET"):
    cialo = json.dumps(json_cialo).encode("utf-8") if json_cialo is not None else b""
    z = Zadanie(metoda, sciezka, {}, {}, cialo, lokalny, "Tester", "127.0.0.1", "127.0.0.1:8787")
    z.params = params or {}
    return z


def odkoduj_luau(literal):
    """Odwrotność literal_luau (tylko to, czego używa): \\", \\\\ i \\ddd."""
    assert literal[0] == literal[-1] == '"'
    s, out, i = literal[1:-1], bytearray(), 0
    while i < len(s):
        if s[i] == "\\":
            if s[i + 1].isdigit():
                out.append(int(s[i + 1:i + 4]))
                i += 4
            else:
                out += s[i + 1].encode()
                i += 2
        else:
            out += s[i].encode()
            i += 1
    return out.decode("utf-8")


def wiersz(ksztalt=0, grupa=0, poz=(0, 0, 0), obr=(0, 0, 0), rozm=(4, 1, 2), kolor="A3A2A5", mat=0, przezr=0,
           nazwa="Part"):
    return [ksztalt, grupa, *poz, *obr, *rozm, kolor, mat, przezr, nazwa]


class Baza(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_podglad_")
        self._dane, self._runtime, self._log = rdzen.DANE, rdzen.RUNTIME, rdzen.PLIK_LOGU
        rdzen.DANE = os.path.join(self.tmp, "dane")
        rdzen.RUNTIME = os.path.join(self.tmp, "runtime")
        rdzen.PLIK_LOGU = os.path.join(rdzen.RUNTIME, "panel.log")
        self.katalog = podglad.katalog_podgladu()

    def tearDown(self):
        rdzen.DANE, rdzen.RUNTIME, rdzen.PLIK_LOGU = self._dane, self._runtime, self._log
        shutil.rmtree(self.tmp, ignore_errors=True)

    def migawka(self, mid, czas, czesci=None, zrzuty=(), meta_dodatkowe=None):
        dane = {"wersja": 1, "grupy": ["Workspace", "Workspace/Baza/Karczma"], "materialy": ["Plastic", "Wood"],
                "czesci": czesci if czesci is not None else [wiersz(), wiersz(grupa=1, mat=1, nazwa="Ściana")]}
        meta = podglad.zbuduj_meta(mid, dane, "Tytuł " + mid, "opis", "Tester", list(zrzuty), "Workspace",
                                   miejsce={"placeId": 1, "nazwa": "Miejsce"})
        meta["czas"] = czas
        meta.update(meta_dodatkowe or {})
        folder = os.path.join(self.katalog, mid)
        os.makedirs(folder, exist_ok=True)
        podglad.zapisz_migawke(folder, meta, dane)
        return folder, meta


# --------------------------------------------------------------------------- format czesci.json / meta.json
class TestFormat(Baza):
    def test_czesci_json_zwarty_i_zgodny_z_readme(self):
        folder, meta = self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00")
        with open(os.path.join(folder, "czesci.json"), encoding="utf-8") as f:
            tekst = f.read()
        self.assertNotIn("\n", tekst.strip(), "czesci.json ma być w jednej linii")
        self.assertNotIn(", ", tekst)
        self.assertNotIn('": ', tekst)
        d = json.loads(tekst)
        self.assertEqual(d["wersja"], 1)
        self.assertEqual(set(d), {"wersja", "grupy", "materialy", "czesci"})
        for w in d["czesci"]:
            self.assertEqual(len(w), 15)
            self.assertIn(w[0], range(8))
            self.assertLess(w[1], len(d["grupy"]))
            self.assertLess(w[12], len(d["materialy"]))
            self.assertRegex(w[11], r"^[0-9A-F]{6}$")
            self.assertIsInstance(w[14], str)
        self.assertIn("Ściana", tekst)                    # UTF-8, nie Ś

    def test_meta_ma_pola_z_kontraktu(self):
        _, meta = self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00", zrzuty=["zrzut_1.jpg"])
        for pole in ("id", "tytul", "opis", "kto", "czas", "zrodlo", "czesci", "grupy", "zrzuty", "zakres", "miejsce"):
            self.assertIn(pole, meta)
        self.assertEqual(meta["zrodlo"], "studio")
        self.assertEqual(meta["czesci"], 2)
        self.assertEqual(meta["grupy"], [{"sciezka": "Workspace", "czesci": 1},
                                         {"sciezka": "Workspace/Baza/Karczma", "czesci": 1}])
        self.assertEqual(set(meta["zakres"]), {"min", "max"})
        self.assertEqual(meta["miejsce"], {"placeId": 1, "nazwa": "Miejsce"})

    def test_sklejanie_stron_przelicza_indeksy(self):
        s1 = {"grupy": ["Workspace", "Workspace/A"], "materialy": ["Plastic"],
              "czesci": [wiersz(grupa=1, mat=0), wiersz(grupa=0, mat=0)]}
        s2 = {"grupy": ["Workspace/B", "Workspace"], "materialy": ["Wood", "Plastic"],
              "czesci": [wiersz(grupa=0, mat=0), wiersz(grupa=1, mat=1)]}
        d = podglad.sklej_strony([s1, s2])
        self.assertEqual(d["grupy"], ["Workspace", "Workspace/A", "Workspace/B"])
        self.assertEqual(d["materialy"], ["Plastic", "Wood"])
        self.assertEqual([(w[1], w[12]) for w in d["czesci"]], [(1, 0), (0, 0), (2, 1), (0, 0)])

    def test_zakres_uwzglednia_obrot(self):
        # klocek 10×2×4 obrócony o 90° wokół Y: w świecie ma 4 w X i 10 w Z
        z = podglad.zakres([wiersz(poz=(100, 5, -20), obr=(0, math.pi / 2, 0), rozm=(10, 2, 4))])
        self.assertAlmostEqual(z["min"][0], 98, places=2)
        self.assertAlmostEqual(z["max"][0], 102, places=2)
        self.assertAlmostEqual(z["min"][2], -25, places=2)
        self.assertAlmostEqual(z["max"][2], -15, places=2)
        self.assertEqual(podglad.zakres([]), {"min": [0, 0, 0], "max": [0, 0, 0]})

    def test_ujecia_ignoruja_wielka_plyte(self):
        czesci = [wiersz(poz=(0, -8, 0), rozm=(2048, 16, 2048), nazwa="Baseplate"),
                  wiersz(poz=(300, 3, 300), rozm=(10, 6, 10), nazwa="Dom")]
        uj = podglad.ujecia(czesci)
        self.assertEqual([u[0] for u in uj], ["izometria", "front", "gracz"])
        for _, poz, cel in uj:
            self.assertEqual(len(poz), 3)
            self.assertEqual(len(cel), 3)
            self.assertLess(math.dist(poz, (300, 3, 300)), 120, "kamera ma patrzeć na dom, nie na środek płyty")
        gracz = uj[2][1]
        self.assertAlmostEqual(gracz[1], 5.0, places=1)    # wierzch płyty (0) + wysokość oczu


# --------------------------------------------------------------------------- składowanie i lista
class TestSkladowanie(Baza):
    def test_lista_najnowsza_pierwsza_i_pomija_niekompletne(self):
        self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00")
        self.migawka("20261112-120000-bbbb", "2026-11-12T12:00:00+01:00")
        os.makedirs(os.path.join(self.katalog, "20261112-130000-cccc"))   # w trakcie zapisu: bez meta.json
        lista = podglad.lista_migawek()
        self.assertEqual([m["id"] for m in lista], ["20261112-120000-bbbb", "20261112-100000-aaaa"])
        wynik = podglad._lista(zadanie())
        self.assertEqual(wynik["najnowsza"]["id"], "20261112-120000-bbbb")

    def test_lista_nie_czyta_czesci(self):
        folder, _ = self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00")
        with open(os.path.join(folder, "czesci.json"), "w", encoding="utf-8") as f:
            f.write("to nie jest JSON")
        czytane = []
        oryginal = rdzen.czytaj_json

        def szpieg(sciezka, domyslnie=None):
            czytane.append(os.path.basename(sciezka))
            return oryginal(sciezka, domyslnie)
        rdzen.czytaj_json = szpieg
        try:
            self.assertEqual(len(podglad.lista_migawek()), 1)
        finally:
            rdzen.czytaj_json = oryginal
        self.assertEqual(set(czytane), {"meta.json"})

    def test_pusta_lista_bez_folderu(self):
        self.assertEqual(podglad._lista(zadanie()), {"migawki": [], "najnowsza": None})

    def test_migawka_z_blendera_bez_czesci(self):
        folder, _ = self.migawka("20261112-140000-dddd", "2026-11-12T14:00:00+01:00",
                                 meta_dodatkowe={"zrodlo": "blender", "model": "scena.glb"})
        os.remove(os.path.join(folder, "czesci.json"))
        with open(os.path.join(folder, "scena.glb"), "wb") as f:
            f.write(b"glTF\x02\x00\x00\x00")
        with self.assertRaises(BladHTTP) as e:
            podglad._czesci(zadanie(params={"id": "20261112-140000-dddd"}))
        self.assertEqual(e.exception.status, 404)
        odp = podglad._plik(zadanie(params={"id": "20261112-140000-dddd", "nazwa": "scena.glb"}))
        self.assertIsInstance(odp, Odp)
        self.assertEqual(odp.mime, "model/gltf-binary")
        self.assertEqual(podglad.lista_migawek()[0]["model"], "scena.glb")

    def test_serwowanie_czesci_i_zrzutu(self):
        folder, _ = self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00", zrzuty=["zrzut_1.jpg"])
        with open(os.path.join(folder, "zrzut_1.jpg"), "wb") as f:
            f.write(b"\xff\xd8\xff\xe0test")
        odp = podglad._czesci(zadanie(params={"id": "20261112-100000-aaaa"}))
        self.assertTrue(odp.plik_sciezka.endswith("czesci.json"))
        self.assertTrue(odp.mime.startswith("application/json"))
        odp = podglad._plik(zadanie(params={"id": "20261112-100000-aaaa", "nazwa": "zrzut_1.jpg"}))
        self.assertEqual(odp.mime, "image/jpeg")

    def test_zrzuty_ponawiaja_i_poddaja_sie(self):
        stary = studio.zrzut
        wywolania = []

        def raz_zajete(poz, cel, timeout=60):
            wywolania.append(timeout)
            if len(wywolania) == 1:
                raise BladHTTP(503, "Brak odpowiedzi")
            return b"\x89PNG\r\n\x1a\n" + b"x" * 50          # nie-obraz: zapisany bez zmian jako .png
        folder = os.path.join(self.katalog, "f")
        try:
            studio.zrzut = raz_zajete
            uwagi = []
            self.assertEqual(podglad._zrob_zrzuty(folder, [wiersz()], uwagi),
                             ["zrzut_1.png", "zrzut_2.png", "zrzut_3.png"])
            self.assertEqual((len(wywolania), uwagi), (4, []))
            wywolania.clear()

            def zawsze_zajete(poz, cel, timeout=60):
                wywolania.append(timeout)
                raise BladHTTP(503, "Brak odpowiedzi")
            studio.zrzut = zawsze_zajete
            uwagi = []
            self.assertEqual(podglad._zrob_zrzuty(folder, [wiersz()], uwagi), [])
            self.assertEqual(len(wywolania), 4)             # 2 ujęcia × 2 próby, trzecie pominięte
            self.assertIn("Pominięto", uwagi[-1])
        finally:
            studio.zrzut = stary

    def test_niedokonczona_migawka_jest_sprzatana(self):
        stare = (studio.stan, podglad.pobierz_czesci, podglad._zrob_zrzuty)
        studio.stan = lambda odswiez=False: {"polaczone": True, "studio": {"nazwa": "X", "placeId": 1}}
        podglad.pobierz_czesci = lambda korzen: ({"wersja": 1, "grupy": ["Workspace"], "materialy": ["Plastic"],
                                                  "czesci": [wiersz()]}, {"miejsce": {}}, [])

        def awaria(folder, czesci, uwagi):
            raise RuntimeError("awaria w trakcie zrzutów")
        podglad._zrob_zrzuty = awaria
        try:
            with self.assertRaises(RuntimeError):
                podglad.zrob_migawke("t", "", "Tester")
            self.assertEqual(os.listdir(self.katalog), [])
            podglad._zrob_zrzuty = lambda folder, czesci, uwagi: []
            meta = podglad.zrob_migawke("Bez zrzutów", "", "Tester", zrzuty=True)
            self.assertEqual(meta["czesci"], 1)
            self.assertTrue(os.path.isfile(os.path.join(self.katalog, meta["id"], "meta.json")))
        finally:
            studio.stan, podglad.pobierz_czesci, podglad._zrob_zrzuty = stare


# --------------------------------------------------------------------------- bezpieczne nazwy
class TestBezpieczenstwo(Baza):
    ZLE_NAZWY = ["../meta.json", "..\\meta.json", "a/b.jpg", "a\\b.jpg", "C:x.jpg", ".ukryty.jpg", "meta.json",
                 "czesci.json", "zrzut.exe", "zrzut.jpg:strumien", "", "zrzut..jpg", "zrzut_1.jpg.tmp", "zrzut 1.jpg",
                 "\x00.jpg", None, 5]
    ZLE_ID = ["..", ".", "../dane", "a/b", "a\\b", "", "C:", ".git", "x" * 200, None, "a b"]

    def test_bezpieczne_nazwy_plikow(self):
        for n in ("zrzut_1.jpg", "zrzut_2.PNG", "scena.glb", "ujecie-3.webp"):
            self.assertTrue(podglad.bezpieczna_nazwa(n), n)
        for n in self.ZLE_NAZWY:
            self.assertFalse(podglad.bezpieczna_nazwa(n), repr(n))

    def test_bezpieczne_id(self):
        self.assertTrue(podglad.bezpieczne_id("20261112-221024-a715"))
        for mid in self.ZLE_ID:
            self.assertFalse(podglad.bezpieczne_id(mid), repr(mid))

    def test_trasy_odrzucaja_wyjscie_z_folderu(self):
        self.migawka("20261112-100000-aaaa", "2026-11-12T10:00:00+01:00")
        with open(os.path.join(self.katalog, "tajne.jpg"), "wb") as f:
            f.write(b"x")
        for nazwa in self.ZLE_NAZWY[:-2] + ["..%2Ftajne.jpg"]:
            with self.assertRaises(BladHTTP, msg=repr(nazwa)) as e:
                podglad._plik(zadanie(params={"id": "20261112-100000-aaaa", "nazwa": nazwa}))
            self.assertEqual(e.exception.status, 404)
        for mid in self.ZLE_ID:
            with self.assertRaises(BladHTTP, msg=repr(mid)):
                podglad._czesci(zadanie(params={"id": mid}))
            with self.assertRaises(BladHTTP, msg=repr(mid)):
                podglad._plik(zadanie(params={"id": mid, "nazwa": "tajne.jpg"}))

    def test_migawka_tylko_lokalnie(self):
        with self.assertRaises(BladHTTP) as e:
            podglad._nowa(zadanie(metoda="POST", json_cialo={}, lokalny=False))
        self.assertEqual(e.exception.status, 403)

    def test_zly_korzen(self):
        for k in ("Workspace/\x00", "x" * 400):
            with self.assertRaises(BladHTTP):
                podglad.sprawdz_korzen(k)
        self.assertEqual(podglad.sprawdz_korzen(None), "Workspace")
        self.assertEqual(podglad.sprawdz_korzen("\\Workspace\\Baza\\"), "Workspace/Baza")

    def test_literal_luau_nie_da_sie_wyrwac(self):
        for t in ('Workspace/"; game:Destroy() --', "a\\b", "Zażółć gęślą jaźń", "linia\nnowa\r\t", "]]--[["):
            lit = podglad.literal_luau(t)
            self.assertEqual(odkoduj_luau(lit), t)
            srodek = lit[1:-1].replace("\\\\", "").replace('\\"', "")
            self.assertNotIn('"', srodek)
            self.assertTrue(all(0x20 <= ord(c) < 0x7F for c in lit))

    def test_kod_strony_podstawia_znaczniki(self):
        kod = podglad.kod_strony('Workspace/Baza "X"', od=1600, ile=800, limit=90000)
        for znacznik in ('"__KORZEN__"', "__OD__", "__ILE__", "__LIMIT__"):
            self.assertNotIn(znacznik, kod)
        self.assertIn('local KORZEN: string = "Workspace/Baza \\"X\\""', kod)
        self.assertIn('tonumber("1600")', kod)
        self.assertIn('"__KORZ" .. "EN__"', kod)          # rozpoznanie niepodstawionego szablonu zostaje


# --------------------------------------------------------------------------- stronicowanie (atrapa Studio)
class TestStronicowanie(Baza):
    def setUp(self):
        super().setUp()
        self._luau = studio.luau

    def tearDown(self):
        studio.luau = self._luau
        super().tearDown()

    def atrapa(self, wszystkie, zmiana=None):
        """Udaje migawka.luau: strony po 3 części, lokalne indeksy grup. zmiana="raz": liczba części rośnie po
        pierwszym wywołaniu; zmiana="ciagle": rośnie przy każdym (ktoś stale dokłada części)."""
        wywolania = []

        def luau(kod, dm="Edit", timeout=60):
            od = int(kod.split('local OD: number = tonumber("')[1].split('"')[0])
            wywolania.append(od)
            razem = len(wszystkie) + {None: 0, "raz": min(1, len(wywolania) - 1), "ciagle": len(wywolania)}[zmiana]
            strona = wszystkie[od:od + 3]
            grupy = sorted({g for g, _ in strona})
            d = {"wersja": 1, "razem": razem, "od": od, "grupy": grupy, "materialy": ["Plastic"],
                 "miejsce": {"placeId": 7, "nazwa": "M"},
                 "czesci": [wiersz(grupa=grupy.index(g), nazwa=n) for g, n in strona]}
            if od + 3 < len(wszystkie):
                d["nastepny"] = od + 3
            return json.dumps(d)
        studio.luau = luau
        return wywolania

    def test_sklejanie_wielu_stron(self):
        wszystkie = [("Workspace/G%d" % (i % 4), "P%d" % i) for i in range(10)]
        wyw = self.atrapa(wszystkie)
        dane, pierwsza, uwagi = podglad.pobierz_czesci("Workspace")
        self.assertEqual(wyw, [0, 3, 6, 9])
        self.assertEqual([w[14] for w in dane["czesci"]], ["P%d" % i for i in range(10)])
        for w, (g, _) in zip(dane["czesci"], wszystkie):
            self.assertEqual(dane["grupy"][w[1]], g)
        self.assertEqual(uwagi, [])
        self.assertEqual(pierwsza["miejsce"]["placeId"], 7)

    def test_zmiana_swiata_w_trakcie(self):
        wyw = self.atrapa([("Workspace", "P%d" % i) for i in range(7)], zmiana="raz")
        dane, _, uwagi = podglad.pobierz_czesci("Workspace")
        self.assertEqual(wyw, [0, 3, 6, 0, 3, 6])          # jedna zmiana = jedno ponowienie od zera, bez uwagi
        self.assertEqual((len(dane["czesci"]), uwagi), (7, []))
        self.atrapa([("Workspace", "P%d" % i) for i in range(7)], zmiana="ciagle")
        _, _, uwagi = podglad.pobierz_czesci("Workspace")
        self.assertTrue(uwagi and "zmieniał" in uwagi[0])

    def test_blad_z_luau(self):
        studio.luau = lambda kod, dm="Edit", timeout=60: json.dumps({"blad": "Nie ma takiego miejsca"})
        with self.assertRaises(BladHTTP) as e:
            podglad.pobierz_czesci("Workspace/Nie")
        self.assertEqual(e.exception.status, 400)

    def test_ucieta_odpowiedz(self):
        studio.luau = lambda kod, dm="Edit", timeout=60: '{"wersja":1,"czesci":[[0,0,1'
        with self.assertRaises(BladHTTP) as e:
            podglad.pobierz_czesci("Workspace")
        self.assertEqual(e.exception.status, 502)


# --------------------------------------------------------------------------- zrzuty
@unittest.skipIf(Image is None, "brak Pillow")
class TestZrzuty(unittest.TestCase):
    def png(self, w, h, kolor=(30, 30, 30), wzor=False):
        im = Image.new("RGB", (w, h), kolor)
        if wzor:                                           # „scena”: jasny dom na ciemnym tle
            im.paste((200, 120, 40), (w // 4, h // 3, w // 2, h - 20))
            im.paste((90, 160, 60), (0, h - h // 5, w, h))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        return buf.getvalue()

    def test_zmniejsza_i_zapisuje_jpg(self):
        bajty, ext, pusty = podglad.przygotuj_zrzut(self.png(1920, 1010, wzor=True))
        self.assertEqual(ext, ".jpg")
        self.assertFalse(pusty)
        im = Image.open(io.BytesIO(bajty))
        self.assertEqual(im.format, "JPEG")
        self.assertEqual(im.size, (1600, 842))

    def test_rozpoznaje_pusty_widok(self):
        _, _, pusty = podglad.przygotuj_zrzut(self.png(800, 400))
        self.assertTrue(pusty)

    def test_maly_obraz_bez_zmiany_rozmiaru(self):
        bajty, _, _ = podglad.przygotuj_zrzut(self.png(640, 360, wzor=True))
        self.assertEqual(Image.open(io.BytesIO(bajty)).size, (640, 360))


# --------------------------------------------------------------------------- Studio bez Studio
class TestStudio(unittest.TestCase):
    def test_konsola_poziomy_i_stos(self):
        tekst = ("Gracz1 joined live editing session.\n"
                 "Workspace.Skrypt:12: attempt to index nil with 'x'\nStack Begin\nScript 'Workspace.Skrypt', Line 12\n"
                 "Stack End\nInfinite yield possible on 'ReplicatedStorage:WaitForChild(\"X\")'\nzwykły print\n"
                 "Warning: coś jest deprecated\n")
        k = studio.parsuj_konsole(tekst)
        self.assertEqual([l["poziom"] for l in k["linie"]], ["info", "blad", "ostrzezenie", "info", "ostrzezenie"])
        self.assertIn("Line 12", k["linie"][1]["tekst"])
        self.assertEqual((k["bledy"], k["ostrzezenia"]), (1, 2))
        self.assertEqual(len(studio.parsuj_konsole("\n".join("l%d" % i for i in range(1000)), maks=50)["linie"]), 50)

    def test_stan_nie_czeka_na_zajete_studio(self):
        stare = (os.environ.get("STUDIO_MCP_CMD"), studio.LIMIT_STANU_S, dict(studio._pamiec_stanu))
        os.environ["STUDIO_MCP_CMD"] = "nieistniejacy-mostek"
        studio.LIMIT_STANU_S = 2.0
        studio._pamiec_stanu.update(t=0.0, v=None)
        gotowe = threading.Event()

        def trzymaj():
            with studio._blokada:
                gotowe.set()
                time.sleep(3)
        threading.Thread(target=trzymaj, daemon=True).start()
        gotowe.wait(2)
        try:
            t = time.time()
            s = studio.stan(odswiez=True)
            self.assertLess(time.time() - t, 2.0)
            self.assertFalse(s["polaczone"])
            self.assertTrue(s.get("zajete"))
            self.assertIn("zajęte", s["blad"])
        finally:
            if stare[0] is None:
                os.environ.pop("STUDIO_MCP_CMD", None)
            else:
                os.environ["STUDIO_MCP_CMD"] = stare[0]
            studio.LIMIT_STANU_S = stare[1]
            studio._pamiec_stanu.clear()
            studio._pamiec_stanu.update(stare[2])


# --------------------------------------------------------------------------- analityka (bez sieci)
class TestAnalityka(Baza):
    PRYWATNA = {"data": [{"id": 0, "rootPlaceId": 0, "name": "[TITLE UNAVAILABLE]", "playing": 0, "visits": 0}]}

    def test_gra_prywatna(self):
        g = analityka.interpretuj(123, 456, "B&C", self.PRYWATNA)
        self.assertFalse(g["publiczna"])
        self.assertIn("prywatna", g["opis"])
        self.assertNotIn("blad", g)
        self.assertEqual((g["gracze"], g["wizyty"], g["ulubione"]), (0, 0, 0))
        self.assertFalse(analityka.interpretuj(123, 456, "B&C", {"data": []})["publiczna"])

    def test_gra_publiczna(self):
        dg = {"data": [{"id": 123, "rootPlaceId": 456, "name": "BLOCKY", "playing": 7, "visits": 1500,
                        "favoritedCount": 30, "maxPlayers": 12}]}
        g = analityka.interpretuj(123, None, "B&C", dg, {"data": [{"id": 123, "upVotes": 9, "downVotes": 1}]})
        self.assertTrue(g["publiczna"])
        self.assertEqual((g["gracze"], g["wizyty"], g["ulubione"], g["max_graczy"]), (7, 1500, 30, 12))
        self.assertEqual(g["glosy"], {"za": 9, "przeciw": 1})
        self.assertEqual(g["placeId"], 456)

    def test_historia_co_5_min_i_24_h(self):
        teraz = time.time()
        self.assertTrue(analityka.dopisz_probke(1, teraz - 30 * 3600))     # starsza niż doba
        self.assertTrue(analityka.dopisz_probke(2, teraz - 600))
        self.assertFalse(analityka.dopisz_probke(3, teraz - 400))          # < 5 min od poprzedniej
        self.assertTrue(analityka.dopisz_probke(4, teraz))
        self.assertTrue(analityka.plik_historii().startswith(rdzen.RUNTIME))
        self.assertEqual([h["gracze"] for h in analityka.historia()], [2, 4])


if __name__ == "__main__":
    unittest.main()
