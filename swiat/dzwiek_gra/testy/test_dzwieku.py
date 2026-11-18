#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy pakietu „dźwięk gry” BEZ Studio:  python -B swiat/dzwiek_gra/testy/test_dzwieku.py

Pilnują: katalog w repozytorium = to, co budowniczy wygeneruje dziś (mapa arkusza + ustawienia + identyfikatory),
odcinki = mapa arkusza co do sekundy, zdarzenia używane przez odtwarzacz walki są w katalogu (i odwrotnie),
wpisywanie identyfikatorów (dwie postaci pliku, odmowa złych), strefy muzyki z gruntu map, strażniki i kontrola Luau.
Od 18.11.2026 także: arkusz muzyki (utwór jako odcinek pliku), utwory zastępcze Bagna i Dżungli, konteksty muzyki
(walka, walka ze Strażnikiem, mini-gry) i to, po czym skrypt muzyki je wykrywa (atrybuty, które naprawdę ustawiają
odtwarzacz walki, serwer potworów i serwer mini-gier — tylko odczyt cudzych źródeł).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
import zbuduj as ZB  # noqa: E402


def czytaj(*c):
    with open(os.path.join(REPO, *c), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


UST = ZB.wczytaj_json(ZB.USTAWIENIA)
IDENT = ZB.wczytaj_json(ZB.IDENTYFIKATORY)
MAPA = json.loads(czytaj("assets", "audio", "arkusz", "sfx_arkusz_a.json"))
MAPA_M = json.loads(czytaj("assets", "audio", "arkusz", "muzyka_arkusz_b.json"))
ODTW = czytaj("swiat", "test_walki2", "zrodla", "OdtwarzaczWalki2.luau")
MUZ = czytaj("swiat", "dzwiek_gra", "zrodla", "MuzykaStref.client.luau")
MUZ_KOD = re.sub(r"--\[\[.*?\]\]", "", MUZ, flags=re.S)          # bez komentarzy blokowych
MUZ_KOD = re.sub(r"--[^\n]*", "", MUZ_KOD)                       # i liniowych
Z_ARKUSZA = ["muzyka_13_walka_petla", "muzyka_14_walka_straznik_petla", "muzyka_15_trening_petla",
             "muzyka_06_bagno_b_petla", "muzyka_07_dzungla_b_petla"]
LAS = ["muzyka_05_las_a_petla", "muzyka_05_las_b_petla"]


def kopia(d):
    return json.loads(json.dumps(d))


class TestKatalogu(unittest.TestCase):
    def test_katalog_aktualny(self):
        tekst, _ = ZB.zrodlo_katalogu(ZB.katalog(UST, IDENT))
        self.assertEqual(tekst, czytaj("swiat", "dzwiek_gra", "zrodla", "KatalogDzwiekow.luau"),
                         "zrodla/KatalogDzwiekow.luau nieaktualny — python -B swiat/dzwiek_gra/zbuduj.py --sucho")

    def test_odcinki_z_mapy(self):
        k = ZB.katalog(UST, IDENT)
        self.assertEqual(sorted(k["efekty"]), sorted(MAPA["efekty"]))
        for n, e in MAPA["efekty"].items():
            for pole in ("poczatek", "koniec", "atak", "szczyt"):
                self.assertEqual(k["efekty"][n][pole], e[pole], (n, pole))

    def test_identyfikatory_zgodne_z_rejestrem_wgran(self):
        # identyfikator 0 = plik niewgrany; niezerowy musi pochodzić z rejestru wgrań (assets/audio/wgrane.json),
        # żeby w katalogu nie znalazł się zasób, którego nikt świadomie nie wgrał
        import json
        import os
        rejestr = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "audio", "wgrane.json")
        wgrane = {}
        if os.path.exists(rejestr):
            with open(rejestr, encoding="utf-8") as f:
                for w in json.load(f).get("wgrane", []):
                    if w.get("gotowe") and w.get("assetId"):
                        wgrane[os.path.splitext(os.path.basename(w["plik"]))[0]] = int(w["assetId"])
        self.assertIsInstance(IDENT["arkusz"], int)
        self.assertGreaterEqual(IDENT["arkusz"], 0)
        if IDENT["arkusz"]:
            self.assertIn(IDENT["arkusz"], wgrane.values(), "arkusz spoza rejestru wgrań")
        for nazwa, v in IDENT["arkusze_muzyki"].items():
            self.assertGreaterEqual(v, 0, nazwa)
            if v:
                self.assertEqual(wgrane.get(nazwa), v, nazwa)
        for nazwa, v in IDENT["muzyka"].items():
            self.assertGreaterEqual(v, 0, nazwa)
            if v:
                self.assertEqual(wgrane.get(nazwa), v, nazwa)

    def test_strefy_z_gruntu_map(self):
        k = ZB.katalog(UST, IDENT)
        self.assertEqual(k["muzyka"]["strefy"]["bazar"]["prostokaty"], [[882.0, 1066.0, -790.0, -610.0]])
        # krótki pas (D-096, swiat/biomy/wymiary_pasa.json): las od X 1066 do styku z Bagnem, z kulisami |v| ≤ 84
        las, bagno = k["muzyka"]["strefy"]["las"]["prostokaty"], k["muzyka"]["strefy"]["bagno"]["prostokaty"]
        self.assertEqual([las[0][0], las[0][2], las[0][3]], [1066.0, -784.0, -616.0])
        self.assertEqual(las[0][1], bagno[0][0])
        self.assertGreater(bagno[0][1], bagno[0][0] + 300)
        self.assertEqual(len(k["muzyka"]["strefy"]["bazar"]["utwory"]), 3)
        self.assertEqual(len(k["muzyka"]["strefy"]["las"]["utwory"]), 2)
        self.assertFalse(k["muzyka"]["strefy"]["menu"]["podpiete"])

    def test_zdarzenia_odtwarzacza_w_katalogu(self):
        # zdarzenia, które odtwarzacz gra (lista jawna; każde musi wystąpić w kodzie jako napis w wywołaniu)
        gra = {"cios", "krytyk", "blok", "unik", "kula_ognia", "lodowy_pocisk", "galareta", "rzut", "tarcza",
               "tik_trucizna", "tik_podpalenie", "ogluszenie", "zwyciestwo", "porazka", "awans", "monety", "przycisk",
               "zarodniki"}
        for zd in gra - {"kula_ognia", "lodowy_pocisk"}:
            self.assertRegex(ODTW, r'(dzwiekZdarzenia\(|odcinekZdarzenia\(|then |else |kand = )"%s"' % zd, zd)
        uzyte = gra | set(UST["glosy_potworow"].values())
        self.assertEqual(sorted(uzyte - set(UST["zdarzenia"])), [], "zdarzenia odtwarzacza bez wpisu w ustawieniach")
        # „chmury” to przejście przez chmury (inny pakiet) — w katalogu na później
        self.assertEqual(sorted(set(UST["zdarzenia"]) - uzyte - {"chmury"}), [], "wpisy, których odtwarzacz nie gra")
        self.assertIn('workspace:FindFirstChild("DzwiekGra")', ODTW)
        self.assertIn("PlaybackRegion = NumberRange.new(p0, p1)", ODTW)

    def test_uderzenia_maja_szczyt_w_odcinku(self):
        for z, w in UST["zdarzenia"].items():
            e = MAPA["efekty"][w["efekt"]]
            self.assertLessEqual(e["atak"], e["szczyt"], z)
            self.assertLess(e["szczyt"], e["koniec"] - e["poczatek"], z)


class TestMuzykiArkuszaIKontekstow(unittest.TestCase):
    def test_mapa_arkusza_muzyki(self):
        # mapa = plik (skrót), limity Roblox (7 min, 20 MB), odcinki po kolei z ciszą między nimi i marginesem do środka
        sciezka = os.path.join(REPO, "assets", "audio", "arkusz", MAPA_M["plik"])
        with open(sciezka, "rb") as f:
            dane = f.read()
        self.assertEqual(hashlib.sha256(dane).hexdigest(), MAPA_M["sha256"])
        self.assertEqual(len(dane), MAPA_M["rozmiar_bajtow"])
        self.assertLess(len(dane), 20 * 1024 * 1024)
        self.assertLess(MAPA_M["dlugosc_s"], 7 * 60)
        self.assertEqual(sorted(MAPA_M["kolejnosc"]), sorted(Z_ARKUSZA))
        poprzedni, margines = 0.0, MAPA_M["margines_s"]
        self.assertGreaterEqual(margines, 0.03)
        for n in MAPA_M["kolejnosc"]:
            u = MAPA_M["utwory"][n]
            self.assertGreaterEqual(u["poczatek"] - poprzedni, 0.45, n)          # cisza przed utworem
            self.assertAlmostEqual(u["graj_od"], u["poczatek"] + margines, places=3, msg=n)
            self.assertAlmostEqual(u["graj_do"], u["koniec"] - margines, places=3, msg=n)
            self.assertAlmostEqual(u["koniec"] - u["poczatek"], u["dlugosc"], places=3, msg=n)
            with open(os.path.join(REPO, "assets", "audio", u["plik"]), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), u["sha256_pliku"], "%s: pętla zmieniona po zbudowaniu arkusza" % n)
            poprzedni = u["koniec"]
        self.assertGreaterEqual(MAPA_M["dlugosc_s"] - poprzedni, 0.45)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "bez ffmpeg / ffprobe w PATH")
    def test_arkusz_muzyki_kontrola_narzedzia(self):
        # pełna kontrola narzędzia: długość pliku, cisza między utworami, odcinki = pliki pętli
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "audio_arkusz_muzyki.py"),
                            "--nazwa", "muzyka_arkusz_b", "--sprawdz"], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace")[-600:])

    def test_utwory_z_arkusza_w_katalogu(self):
        k = ZB.katalog(UST, IDENT)
        ark = k["muzyka"]["arkusze"]["muzyka_arkusz_b"]
        self.assertEqual((ark["id"], ark["sha256"], ark["dlugosc"]),
                         (IDENT["arkusze_muzyki"]["muzyka_arkusz_b"], MAPA_M["sha256"], MAPA_M["dlugosc_s"]))
        znalezione = {}
        for zr in list(k["muzyka"]["strefy"].values()) + list(k["muzyka"]["konteksty"].values()):
            for u in zr["utwory"] + (zr.get("zastepcze") or {}).get("utwory", []):
                if "arkusz" in u:
                    znalezione[u["nazwa"]] = u
                else:
                    self.assertEqual(sorted(u), ["id", "nazwa"], u)                # osobny plik: bez odcinka
                    self.assertEqual(u["id"], IDENT["muzyka"][u["nazwa"]])
        self.assertEqual(sorted(znalezione), sorted(Z_ARKUSZA))
        for n, u in znalezione.items():
            e = MAPA_M["utwory"][n]
            self.assertEqual((u["arkusz"], u["poczatek"], u["koniec"], u["id"]),
                             ("muzyka_arkusz_b", e["graj_od"], e["graj_do"], IDENT["arkusze_muzyki"]["muzyka_arkusz_b"]), n)

    def test_bagno_i_dzungla_wlasne_i_zastepcze(self):
        k = ZB.katalog(UST, IDENT)
        las = {u["nazwa"]: u["id"] for u in k["muzyka"]["strefy"]["las"]["utwory"]}
        for strefa, wlasny, drugi in (("bagno", "muzyka_06_bagno_petla", "muzyka_06_bagno_b_petla"),
                                      ("dzungla", "muzyka_07_dzungla_petla", "muzyka_07_dzungla_b_petla")):
            s = k["muzyka"]["strefy"][strefa]
            self.assertEqual([u["nazwa"] for u in s["utwory"]], [wlasny, drugi])
            self.assertIn(wlasny, IDENT["muzyka"])                                 # osobny plik: miejsce na identyfikator
            self.assertNotIn("arkusz", s["utwory"][0])
            self.assertEqual(s["utwory"][1]["arkusz"], "muzyka_arkusz_b")
            # zastępcze = utwory lasu z ich identyfikatorami, ciszej niż własne (jak do 18.11.2026)
            self.assertEqual({u["nazwa"]: u["id"] for u in s["zastepcze"]["utwory"]}, las)
            self.assertEqual(sorted(las), LAS)
            self.assertEqual(s["zastepcze"]["glosnosc"], 0.7)
            self.assertGreater(s["glosnosc"], s["zastepcze"]["glosnosc"])
        # po wpisaniu identyfikatora własnego utworu katalog go niesie (skrypt gra wtedy własne zamiast zastępczych)
        ident = kopia(IDENT)
        ident["muzyka"]["muzyka_06_bagno_petla"] = 4242
        ident["arkusze_muzyki"]["muzyka_arkusz_b"] = 4343
        k2 = ZB.katalog(UST, ident)
        self.assertEqual([u["id"] for u in k2["muzyka"]["strefy"]["bagno"]["utwory"]], [4242, 4343])
        self.assertEqual([u["id"] for u in k2["muzyka"]["strefy"]["dzungla"]["utwory"]], [0, 4343])
        self.assertEqual(k2["muzyka"]["konteksty"]["walka"]["utwory"][0]["id"], 4343)

    def test_konteksty_w_katalogu(self):
        kon = ZB.katalog(UST, IDENT)["muzyka"]["konteksty"]
        self.assertEqual(sorted(kon), sorted(ZB.KONTEKSTY))
        self.assertEqual([u["nazwa"] for u in kon["walka"]["utwory"]], ["muzyka_13_walka_petla"])
        self.assertEqual([u["nazwa"] for u in kon["walka_straznik"]["utwory"]], ["muzyka_14_walka_straznik_petla"])
        self.assertEqual([u["nazwa"] for u in kon["trening"]["utwory"]], ["muzyka_15_trening_petla"])
        self.assertEqual(kon["trening"]["atrybutGracza"], "TreningGra")
        for nazwa in ZB.KONTEKSTY:                                                 # skrypt muzyki zna każdy kontekst
            self.assertIn('"%s"' % nazwa if nazwa != "trening" else "KONTEKSTY.trening", MUZ_KOD, nazwa)
        zly = kopia(UST)
        zly["muzyka"]["konteksty"]["sklep"] = {"glosnosc": 0.5, "utwory": ["muzyka_13_walka_petla"]}
        with self.assertRaises(SystemExit):
            ZB.katalog(zly, IDENT)
        zly = kopia(UST)
        zly["muzyka"]["konteksty"]["walka"]["utwory"] = ["muzyka_08_pustynia_petla"]   # ani osobny plik, ani arkusz
        with self.assertRaises(SystemExit):
            ZB.katalog(zly, IDENT)

    def test_wykrywanie_straznika_zgodne_z_cudzymi_zrodlami(self):
        # gatunki Strażników = gatunek strażnika w danych każdej krainy (tylko odczyt cudzych pakietów)
        gatunki = set(ZB.katalog(UST, IDENT)["muzyka"]["konteksty"]["walka_straznik"]["gatunki"])
        z_krain = set()
        for plik in (("las_pas_gra", "DanePasa.luau"), ("bagno_pas_gra", "DaneBagna.luau"), ("dzungla_pas_gra", "DaneDzungli.luau")):
            m = re.search(r'straznik = \{ poz = \{[^}]*\}, gatunek = "(\w+)" \}', czytaj("swiat", plik[0], "zrodla", plik[1]))
            self.assertIsNotNone(m, plik)
            z_krain.add(m.group(1))
        self.assertEqual(gatunki, z_krain)
        for g in gatunki:                                                          # i każdy jest aktorem prototypu walki
            self.assertTrue(os.path.isfile(os.path.join(REPO, "swiat", "test_walki2", "dane", g + ".json")), g)
        # odtwarzacz walki zapisuje na kontenerze walki stan i wybór „klasa/przeciwnik/poziom” (to czyta skrypt muzyki)
        self.assertIn('self:atrybut("OstatniStan", "odtwarzanie")', ODTW)
        self.assertIn('self:atrybut("OstatniStan", "wynik")', ODTW)
        self.assertIn('self:atrybut("OstatniWybor", string.format("%s/%s/%s", self.wybor.klasa, self.wybor.przeciwnik, self.wybor.poziom))', ODTW)
        self.assertIn('self:atrybut("OstatniStan", powod)', ODTW)                  # po walce stan przestaje być „wynik”
        self.assertIn('GetAttribute("OstatniStan")', MUZ_KOD)
        self.assertIn('GetAttribute("OstatniWybor")', MUZ_KOD)
        # walka w krainie: przeciwnik = identyfikator potwora, a jego opis leży w <kontener>/Stan z atrybutami
        klient = czytaj("swiat", "las_potwory", "zrodla", "KlientPotworow.client.luau")
        serwer = czytaj("swiat", "las_potwory", "zrodla", "SerwerPotworow.server.luau")
        self.assertIn('task.spawn(Odtwarzacz.uruchom, kontener, { klasa = bohater.klasa, przeciwnik = id, poziom = bohater.poziom }', klient)
        self.assertIn('local folderStanu = kontener:WaitForChild("Stan")', klient)
        self.assertIn('c.Name = p.id', serwer)
        self.assertIn('c:SetAttribute("Straznik", p.strefa.d.straznik == true)', serwer)
        self.assertIn('c:SetAttribute("Gatunek", p.gatunek)', serwer)
        self.assertIn('kont:FindFirstChild("Stan")', MUZ_KOD)
        self.assertIn('GetAttribute("Straznik") == true', MUZ_KOD)

    def test_wykrywanie_mini_gry_zgodne_z_serwerem_treningu(self):
        atr = ZB.katalog(UST, IDENT)["muzyka"]["konteksty"]["trening"]["atrybutGracza"]
        serwer = czytaj("swiat", "trening_proba", "zrodla", "SerwerTreningu.server.luau")
        self.assertIn('gracz:SetAttribute("%s", gra)' % atr, serwer)               # wejście na stanowisko
        self.assertGreaterEqual(serwer.count('gracz:SetAttribute("%s", nil)' % atr), 1)   # wyjście
        self.assertIn("gracz:GetAttribute(kt.atrybutGracza) ~= nil", MUZ_KOD)

    def test_manifest_ma_utwory_katalogu(self):
        manifest = json.loads(czytaj("assets", "audio", "manifest_audio.json"))
        petle = {u["pliki"]["petla"] for u in manifest["muzyka"]}
        k = ZB.katalog(UST, IDENT)
        for zr in list(k["muzyka"]["strefy"].values()) + list(k["muzyka"]["konteksty"].values()):
            for u in zr["utwory"]:
                self.assertIn("muzyka/%s.ogg" % u["nazwa"], petle, u["nazwa"])


class TestIdentyfikatorow(unittest.TestCase):
    def _plik(self, dane):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(dane, f)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_postac_prosta(self):
        ident = json.loads(json.dumps(IDENT))
        zm = ZB.wpisz_identyfikatory(self._plik({"arkusz": 123, "muzyka": {"muzyka_05_las_a_petla": "456"}}), ident)
        self.assertEqual(ident["arkusz"], 123)
        self.assertEqual(ident["muzyka"]["muzyka_05_las_a_petla"], 456)
        self.assertEqual(len(zm), 2)
        k = ZB.katalog(UST, ident)
        tekst, _ = ZB.zrodlo_katalogu(k)
        self.assertIn("id = 123,", tekst)

    def test_postac_rejestru_wgranych(self):
        ident = json.loads(json.dumps(IDENT))
        ZB.wpisz_identyfikatory(self._plik({"wgrane": [
            {"plik": "assets/audio/arkusz/sfx_arkusz_a.ogg", "assetId": "777"},
            {"plik": "assets/audio/muzyka/muzyka_02_bazar_targ_petla.ogg", "assetId": "888"},
            {"plik": "assets/audio/dzwieki/sfx_unik.wav", "assetId": "999"}]}), ident)
        self.assertEqual(ident["arkusz"], 777)
        self.assertEqual(ident["muzyka"]["muzyka_02_bazar_targ_petla"], 888)

    def test_odmowa_zlych(self):
        for zle in ({"arkusz": 0}, {"arkusz": -5}, {"muzyka": {"nie_ma_takiego": 5}}, {"arkusz": "abc"}, {},
                    {"arkusze_muzyki": {"nie_ma_takiego": 5}}, {"arkusze_muzyki": {"muzyka_arkusz_b": 0}},
                    {"muzyka": {"muzyka_13_walka_petla": 5}}):   # utwór z arkusza nie ma osobnej pozycji
            with self.assertRaises(SystemExit, msg=str(zle)):
                ZB.wpisz_identyfikatory(self._plik(zle), json.loads(json.dumps(IDENT)))

    def test_nowe_pozycje_postac_prosta(self):
        ident = kopia(IDENT)
        zm = ZB.wpisz_identyfikatory(self._plik({"arkusze_muzyki": {"muzyka_arkusz_b": "901"},
                                                 "muzyka": {"muzyka_06_bagno_petla": 902, "muzyka_07_dzungla_petla": 903}}), ident)
        self.assertEqual(ident["arkusze_muzyki"]["muzyka_arkusz_b"], 901)
        self.assertEqual((ident["muzyka"]["muzyka_06_bagno_petla"], ident["muzyka"]["muzyka_07_dzungla_petla"]), (902, 903))
        self.assertEqual(len(zm), 3)
        for n, v in IDENT["muzyka"].items():                       # istniejące identyfikatory nietknięte
            if n not in ("muzyka_06_bagno_petla", "muzyka_07_dzungla_petla"):
                self.assertEqual(ident["muzyka"][n], v, n)
        self.assertEqual(ident["arkusz"], IDENT["arkusz"])
        tekst, _ = ZB.zrodlo_katalogu(ZB.katalog(UST, ident))
        self.assertEqual(tekst.count("id = 901,"), 1 + len(Z_ARKUSZA))   # wpis arkusza + pięć utworów z niego
        self.assertIn("id = 902,", tekst)

    def test_nowe_pozycje_postac_rejestru(self):
        ident = kopia(IDENT)
        ZB.wpisz_identyfikatory(self._plik({"wgrane": [
            {"plik": "assets/audio/arkusz/muzyka_arkusz_b.ogg", "assetId": "911"},
            {"plik": "assets/audio/muzyka/muzyka_06_bagno_petla.ogg", "assetId": "912"},
            {"plik": "assets/audio/muzyka/muzyka_07_dzungla_petla.ogg", "assetId": "913"},
            {"plik": "assets/audio/muzyka/muzyka_08_pustynia_petla.ogg", "assetId": "914"}]}), ident)   # nieznany: pominięty
        self.assertEqual(ident["arkusze_muzyki"], {"muzyka_arkusz_b": 911})
        self.assertEqual((ident["muzyka"]["muzyka_06_bagno_petla"], ident["muzyka"]["muzyka_07_dzungla_petla"]), (912, 913))
        self.assertEqual(ident["arkusz"], IDENT["arkusz"])         # arkusz efektów nie pomylony z arkuszem muzyki
        self.assertNotIn("muzyka_08_pustynia_petla", ident["muzyka"])

    def test_rejestr_wgranych_z_repozytorium_nadal_przyjmowany(self):
        # dzisiejszy assets/audio/wgrane.json: polecenie go przyjmuje; wpisane już identyfikatory zostają bez zmian,
        # a zmienić się mogą tylko pozycje, które w identyfikatory.json są jeszcze zerem (plik wgrany, nie wpisany)
        rejestr = os.path.join(REPO, "assets", "audio", "wgrane.json")
        if not os.path.exists(rejestr):
            self.skipTest("brak assets/audio/wgrane.json")
        ident = kopia(IDENT)
        ZB.wpisz_identyfikatory(rejestr, ident)
        self.assertEqual(sorted(ident["muzyka"]), sorted(IDENT["muzyka"]))
        self.assertEqual(sorted(ident["arkusze_muzyki"]), sorted(IDENT["arkusze_muzyki"]))
        if IDENT["arkusz"]:
            self.assertEqual(ident["arkusz"], IDENT["arkusz"])
        for grupa in ("muzyka", "arkusze_muzyki"):
            for n, v in IDENT[grupa].items():
                if v:
                    self.assertEqual(ident[grupa][n], v, n)
        ZB.katalog(UST, ident)                                     # katalog z tymi identyfikatorami da się zbudować


class TestZrodel(unittest.TestCase):
    def test_straznik_i_luau(self):
        tekst, _ = ZB.zrodlo_katalogu(ZB.katalog(UST, IDENT))
        zrodla = ZB.zrodla_pakietu(tekst)
        self.assertEqual([z[0] for z in zrodla], ["Moduly/KatalogDzwiekow", "MuzykaStref"])
        self.assertEqual(ZB.SL.sprawdz_pliki([ZB.KATALOG, ZB.MUZYKA]), [])

    def test_muzyka_tylko_czyta_cudze(self):
        m = czytaj("swiat", "dzwiek_gra", "zrodla", "MuzykaStref.client.luau")
        self.assertNotIn("Lighting", m)
        for cudzy in ("MiasteczkoBazar", "LasPas", "TestWalki2"):
            # cudze kontenery tylko przez FindFirstChild / WaitForChild (bez zmian)
            self.assertNotRegex(m, r'%s"\)\s*[:.]\s*(Destroy|SetAttribute|ClearAllChildren)' % cudzy)
        self.assertIn('folder.Parent = kontener', m)  # dźwięki muzyki tylko we własnym kontenerze (u klienta)
        self.assertNotIn("menu", re.sub(r"--.*", "", m).lower().replace("menu główne", ""))

    def test_muzyka_konteksty_tylko_odczyt(self):
        # atrybuty ustawiamy wyłącznie na własnym kontenerze; cudzych kontenerów, gracza i potworów tylko czytamy
        for m in re.finditer(r"(\w+)\s*:\s*SetAttribute\(", MUZ_KOD):
            self.assertEqual(m.group(1), "kontener", "SetAttribute na obcym obiekcie: %s" % m.group(0))
        for zakazane in ("FireServer", "InvokeServer", ":Fire(", "TreningProba", "LasPotwory", "BagnoPasGra",
                         "DzunglaPasGra", "LasPasGra", ":Destroy(", "ClearAllChildren"):
            self.assertNotIn(zakazane, MUZ_KOD, zakazane)
        # jedyne Invoke / require cudzego: odtwarzacz walki prototypu (czyTrwa) — bez wywołań jego haczyków
        self.assertNotIn(":Invoke(", MUZ_KOD)
        self.assertEqual(re.findall(r"Odtwarzacz\.(\w+)", MUZ_KOD), ["czyTrwa"])

    def test_muzyka_gra_odcinki_i_zastepcze(self):
        # utwór z arkusza: odcinek przez PlaybackRegion; zastępcze tylko wtedy, gdy własna lista jest pusta;
        # kontekst tylko z wczytanym plikiem; Strażnik bez utworu → utwór zwykłej walki
        self.assertIn("d.PlaybackRegionsEnabled = odcinek", MUZ_KOD)
        self.assertIn("d.PlaybackRegion = NumberRange.new(u.od, u.do_)", MUZ_KOD)
        self.assertIn('if #lista == 0 and type(s.zastepcze) == "table" then', MUZ_KOD)
        self.assertIn("if wczytany(u.adres) then", MUZ_KOD)
        self.assertRegex(MUZ_KOD, r'if k == "walka_straznik" then\s+lista = utworyKontekstu\(k\)\s+if #lista == 0 then\s+k = "walka"')
        self.assertEqual(MUZ_KOD.count("Looped = false"), 1)       # bez pętli silnika: koniec utworu = przejście
        self.assertNotIn("Looped = true", MUZ_KOD)


if __name__ == "__main__":
    unittest.main(verbosity=1)
