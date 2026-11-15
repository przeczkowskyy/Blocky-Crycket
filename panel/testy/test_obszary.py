# -*- coding: utf-8 -*-
"""Obszary pracy (bc/obszary.py): poprawne i złe wpisy, nakładanie się, pokrywanie, pliki w obszarze. Czysta logika."""
import unittest

from bc import obszary as o
from bc.rdzen import BladHTTP


class TestNormalizacja(unittest.TestCase):
    def test_sciezki(self):
        self.assertEqual(o.normalizuj("swiat/las/czesci.json"), "swiat/las/czesci.json")
        self.assertEqual(o.normalizuj("  swiat\\las\\  "), "swiat/las")
        self.assertEqual(o.normalizuj("./panel//bc/"), "panel/bc")
        self.assertEqual(o.normalizuj("swiat/*/czesci.json"), "swiat/*/czesci.json")
        self.assertEqual(o.normalizuj("src/**"), "src/**")
        self.assertEqual(o.normalizuj("Swiat/Las"), "Swiat/Las")                  # wielkość liter zostaje

    def test_znaczniki(self):
        self.assertEqual(o.normalizuj("model:Rycerz"), "model:rycerz")
        self.assertEqual(o.normalizuj("MODEL:zestaw_mag"), "model:zestaw_mag")
        self.assertEqual(o.normalizuj("mapa: las_potwory "), "mapa:las_potwory")
        self.assertEqual(o.normalizuj("studio:DemoLesnaBaza"), "studio:DemoLesnaBaza")
        self.assertEqual(o.normalizuj("studio:Las Główny"), "studio:Las Główny")

    def test_zle_wpisy(self):
        zle = ["", "   ", "/etc/passwd", "\\\\serwer\\udzial", "C:\\Users\\x", "c:/x", "D:plik", "~/x", "../x",
               "swiat/../../x", "swiat/..", "a\x00b", "a\nb", "model:", "model:../x", "model:a/b", "model:a b",
               "mapa:x:y", "studio:", "studio:a/b", "studio:a\\b", "studio:*", "foo:bar", "http://x", "x" * 121,
               "swiat/ las", None, 5, ["x"], {"a": 1}]
        for w in zle:
            with self.subTest(w=w):
                with self.assertRaises(BladHTTP) as kon:
                    o.normalizuj(w)
                self.assertEqual(kon.exception.status, 400)

    def test_zle_wpisy_po_kontroli(self):
        """Regresja (wroga kontrola): „@” (e-mail na publiczny GitHub), wzorzec na samym początku (nakładałby się ze
        wszystkim i blokował każdą przebudowę), znaki C1, kierunku tekstu i zerowej szerokości."""
        zle = ["studio:karol@gmail.com", "x@example.com/a", "node/@scope", "*", "**", "*/**", "?", "**/*.luau",
               "*.py", "[a-z]*/x", "studio:‮Kontener", "studio:ok\u009b2J", "swiat/​las", "a⁦b"]
        for w in zle:
            with self.subTest(w=w):
                with self.assertRaises(BladHTTP):
                    o.normalizuj(w)
        self.assertEqual(o.normalizuj("swiat/*/czesci.json"), "swiat/*/czesci.json")   # wzorzec dalej — w porządku
        self.assertEqual(o.normalizuj("src/**/*.luau"), "src/**/*.luau")

    def test_lista(self):
        self.assertEqual(o.lista(None), [])
        self.assertEqual(o.lista("model:rycerz"), ["model:rycerz"])
        self.assertEqual(o.lista(["model:Rycerz", "model:rycerz", "a/b"]), ["model:rycerz", "a/b"])
        with self.assertRaises(BladHTTP):
            o.lista(["a%d" % i for i in range(13)])
        self.assertEqual(len(o.lista(["a%d" % i for i in range(12)])), 12)
        with self.assertRaises(BladHTTP):
            o.lista({"a": 1})
        with self.assertRaises(BladHTTP):
            o.lista(["ok", "../zle"])

    def test_lista_bez_bledow(self):
        self.assertEqual(o.lista_bez_bledow(["../zle", "model:x", 5, None, "model:x", "C:\\a"]), ["model:x"])
        self.assertEqual(o.lista_bez_bledow("model:x"), [])
        self.assertEqual(o.lista_bez_bledow(None), [])
        self.assertEqual(len(o.lista_bez_bledow(["a%d" % i for i in range(500)])), 12)

    def test_sciezki_znacznikow(self):
        self.assertEqual(o.sciezki("model:rycerz"), ["swiat/postacie/rycerz.py", "swiat/postacie/wynik/rycerz/**"])
        self.assertEqual(o.sciezki("mapa:las"), ["swiat/las/**"])
        self.assertEqual(o.sciezki("studio:X"), [])
        self.assertEqual(o.sciezki("a/b"), ["a/b"])


class TestNakladanie(unittest.TestCase):
    def tak(self, a, b):
        self.assertTrue(o.nakladaja_sie(a, b), (a, b))
        self.assertTrue(o.nakladaja_sie(b, a), (b, a))                        # zawsze symetrycznie

    def nie(self, a, b):
        self.assertFalse(o.nakladaja_sie(a, b), (a, b))
        self.assertFalse(o.nakladaja_sie(b, a), (b, a))

    def test_te_same_znaczniki(self):
        self.tak("model:rycerz", "model:rycerz")
        self.tak("mapa:las", "mapa:las")
        self.tak("studio:DemoLesnaBaza", "studio:demolesnabaza")
        self.nie("model:rycerz", "model:kot_mag")
        self.nie("model:rycerz", "model:rycerz2")
        self.nie("mapa:las", "mapa:las2")
        self.nie("studio:A", "studio:B")

    def test_studio_tylko_ze_studio(self):
        self.nie("studio:swiat", "swiat")
        self.nie("studio:postacie", "model:postacie")
        self.nie("studio:las", "mapa:las")
        self.nie("studio:X", "*")
        self.nie("studio:X", "**")

    def test_sciezki_rowne_i_katalogi(self):
        self.tak("a/b.py", "a/b.py")
        self.tak("A/B.py", "a/b.py")                                          # Windows: bez wielkości liter
        self.tak("swiat", "swiat/las/czesci.json")
        self.tak("swiat/las", "swiat/las/czesci.json")
        self.nie("swiat/las", "swiat/las2/czesci.json")                       # przedrostek tekstu to nie katalog
        self.nie("a/b.py", "a/b.pyc")
        self.nie("panel/bc", "panel/static")

    def test_model_i_sciezki(self):
        self.tak("model:rycerz", "swiat/postacie/rycerz.py")
        self.tak("model:rycerz", "swiat/postacie/wynik/rycerz/rycerz.fbx")
        self.tak("model:rycerz", "swiat/postacie/wynik/rycerz")
        self.tak("model:rycerz", "swiat/postacie")
        self.tak("model:rycerz", "swiat")
        self.tak("model:rycerz", "mapa:postacie")                             # swiat/postacie/** obejmuje model
        self.nie("model:rycerz", "swiat/postacie/rycerz_mag.py")
        self.nie("model:rycerz", "swiat/postacie/wynik/rycerz_mag/x.fbx")
        self.nie("model:rycerz", "swiat/postacie/biblioteka/postac.py")
        self.nie("model:rycerz", "mapa:las")

    def test_mapa(self):
        self.tak("mapa:las", "swiat/las/czesci.json")
        self.tak("mapa:las", "swiat/*/czesci.json")
        self.nie("mapa:las", "swiat/biom/czesci.json")
        self.nie("mapa:las", "panel/dane")

    def test_wzorce(self):
        self.tak("swiat/*/czesci.json", "swiat/las/czesci.json")
        self.tak("swiat/*/czesci.json", "swiat/las")                          # katalog może zawierać pasujący plik
        self.tak("swiat/*/czesci.json", "swiat")
        self.nie("swiat/*/czesci.json", "swiat/las/inne.json")
        self.tak("swiat/*", "swiat/las/czesci.json")                          # wzorzec pasuje do katalogu nadrzędnego
        self.tak("*.py", "x.py")
        self.nie("*.py", "x.json")
        self.tak("swiat/l?s", "swiat/las/x")
        self.tak("swiat/[lb]as", "swiat/bas")
        self.nie("swiat/[lb]as", "swiat/kas")
        self.tak("src/**", "src/a/b/c.lua")
        self.tak("**", "cokolwiek/tu")
        self.tak("a/**/x.py", "a/b/c.txt")                                    # „**” — ostrożnie: tak
        self.nie("b/**", "a/x")
        self.tak("swiat/*/czesci.json", "swiat/l*/czesci.json")              # dwa wzorce w tym samym miejscu: tak
        self.nie("swiat/*/czesci.json", "panel/*/czesci.json")

    def test_wspolne(self):
        self.assertEqual(o.wspolne(["model:rycerz", "a/b"], ["model:rycerz"]), ["model:rycerz"])
        self.assertEqual(o.wspolne(["swiat/postacie"], ["model:rycerz"]), ["swiat/postacie ~ model:rycerz"])
        self.assertEqual(o.wspolne(["studio:X"], ["studio:x"]), ["studio:X"])
        self.assertEqual(o.wspolne(["a"], ["b"]), [])
        self.assertEqual(o.wspolne([], ["a"]), [])
        self.assertEqual(o.wspolne(None, None), [])


class TestPokrywanie(unittest.TestCase):
    def test_pokrywa(self):
        self.assertTrue(o.pokrywa("model:rycerz", "model:rycerz"))
        self.assertTrue(o.pokrywa("swiat/postacie", "model:rycerz"))
        self.assertTrue(o.pokrywa("swiat", "model:rycerz"))
        self.assertTrue(o.pokrywa("mapa:postacie", "model:rycerz"))
        self.assertTrue(o.pokrywa("swiat/las", "swiat/las/czesci.json"))
        self.assertTrue(o.pokrywa("swiat/las/**", "swiat/las/czesci.json"))
        self.assertTrue(o.pokrywa("studio:A", "studio:a"))
        self.assertFalse(o.pokrywa("swiat/postacie/rycerz.py", "model:rycerz"))   # tylko źródło, bez wyniku
        self.assertFalse(o.pokrywa("swiat/postacie/wynik", "model:rycerz"))
        self.assertFalse(o.pokrywa("swiat/las/czesci.json", "swiat/las"))
        self.assertFalse(o.pokrywa("swiat/*", "swiat/las/x"))                 # wzorzec pokrywa tylko równy wzorzec
        self.assertTrue(o.pokrywa("swiat/*", "swiat/*"))
        self.assertFalse(o.pokrywa("model:rycerz", "studio:rycerz"))
        self.assertFalse(o.pokrywa("swiat", "studio:swiat"))

    def test_pokrywaja(self):
        self.assertTrue(o.pokrywaja(["model:rycerz", "x"], ["model:rycerz"]))
        self.assertTrue(o.pokrywaja(["swiat"], ["model:rycerz", "mapa:las"]))
        self.assertFalse(o.pokrywaja(["model:rycerz"], ["model:rycerz", "mapa:las"]))
        self.assertFalse(o.pokrywaja(["x"], []))
        self.assertFalse(o.pokrywaja(None, ["x"]))

    def test_dotyczy_pliku(self):
        ob = ["model:rycerz", "mapa:las", "studio:X", "panel/bc/*.py"]
        self.assertEqual(o.dotyczy_pliku(ob, "swiat/postacie/wynik/rycerz/rycerz.glb"), ["model:rycerz"])
        self.assertEqual(o.dotyczy_pliku(ob, "swiat/las/czesci.json"), ["mapa:las"])
        self.assertEqual(o.dotyczy_pliku(ob, "panel/bc/prace.py"), ["panel/bc/*.py"])
        self.assertEqual(o.dotyczy_pliku(ob, "panel/bc/x.js"), [])
        self.assertEqual(o.dotyczy_pliku(ob, "README.md"), [])
        self.assertEqual(o.dotyczy_pliku(ob, ""), [])
        self.assertEqual(o.dotyczy_pliku(None, "a"), [])


if __name__ == "__main__":
    unittest.main()
