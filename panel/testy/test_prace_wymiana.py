# -*- coding: utf-8 -*-
"""Prace obu osób (bc/prace_wymiana.py, narzedzia/praca.py, tools/praca_auto.py) — bez sieci i bez GitHuba.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_prace_wymiana

Wymiana przez gita działa WYŁĄCZNIE na repozytoriach próbnych w katalogu tymczasowym: repozytorium bare (jak GitHub)
+ klony „karol”, „karol2” (ta sama osoba na drugim komputerze) i „pawel”. Globalna konfiguracja gita jest odcięta
(GIT_CONFIG_GLOBAL = pusty plik). Dane lokalne panelu (rdzen.RUNTIME) to katalog testu. Telegram jest atrapą
(gitsync._telegram podmienione), a prawdziwe repozytorium chroni bezpiecznik `prace_wymiana.powod_bez_sieci`.
"""
import datetime
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from testy import test_api  # noqa: F401  (bez importu klas: discover uruchomiłby je drugi raz)
from bc import gitsync, obszary, prace, prace_wymiana as pw, rdzen  # noqa: E402

PANEL = test_api.PANEL
REPO = os.path.dirname(PANEL)
PRACA = os.path.join(PANEL, "narzedzia", "praca.py")
STREFA = datetime.timezone(datetime.timedelta(hours=1))
BEZ_OKNA = 0x08000000 if os.name == "nt" else 0


def T(g, m=0, dzien=15):
    return datetime.datetime(2026, 11, dzien, g, m, tzinfo=STREFA)


def teraz_iso(**przesuniecie):
    return (datetime.datetime.now().astimezone() + datetime.timedelta(**przesuniecie)).isoformat(timespec="seconds")


def praca(pid, obszary_=None, stan="w_toku", tytul=None, koniec=None, **inne):
    # start = teraz: praca świeża bez względu na dzień uruchomienia testów (data z przyszłości względem `teraz` testu
    # liczy się jak brak daty, więc też nie robi pracy nieaktualnej)
    p = {"id": pid, "tytul": tytul or pid, "stan": stan, "obszary": obszary_ or [], "start": teraz_iso()}
    if koniec:
        p["koniec_szacowany"] = koniec
    p.update(inne)
    return p


def osoba(slug, prace_, aktualizacja=None, nazwa=None):
    return {"osoba": slug, "nazwa": nazwa or slug.capitalize(), "aktualizacja": aktualizacja or T(11).isoformat(),
            "prace": prace_}


def _srodowisko_gita(tmp):
    pusty = os.path.join(tmp, "pusty.gitconfig")
    if not os.path.exists(pusty):
        open(pusty, "w").close()
    return {"GIT_CONFIG_GLOBAL": pusty, "GIT_CONFIG_NOSYSTEM": "1"}


# =========================================================================== bez gita
class TestOsoba(unittest.TestCase):
    def test_slug_i_nazwa(self):
        self.assertEqual(pw.osoba_z_imienia("Karol Balucki"), {"osoba": "karol", "nazwa": "Karol"})
        self.assertEqual(pw.osoba_z_imienia("Paweł Przeczkowski"), {"osoba": "pawel", "nazwa": "Paweł"})
        self.assertEqual(pw.osoba_z_imienia("pawel"), {"osoba": "pawel", "nazwa": "Paweł"})
        self.assertEqual(pw.osoba_z_imienia("Żaneta Ślęzak"), {"osoba": "zaneta", "nazwa": "Żaneta"})
        self.assertEqual(pw.osoba_z_imienia(""), {"osoba": "osoba", "nazwa": "osoba"})
        self.assertEqual(pw.osoba_z_imienia(None)["osoba"], "osoba")

    def test_nigdy_email(self):
        for imie in ("ktos@example.com", "Ola ola@example.com", "ola@example.com Ola"):
            with self.subTest(imie=imie):
                o = pw.osoba_z_imienia(imie)
                self.assertNotIn("@", json.dumps(o))
                self.assertNotIn("example", json.dumps(o))
                self.assertRegex(o["osoba"], pw.RX_SLUG)

    def test_nazwa_osoby_z_galezi(self):
        self.assertEqual(pw.nazwa_osoby("pawel", "Ktoś inny"), "Paweł")      # osoba z zespołu wygrywa
        self.assertEqual(pw.nazwa_osoby("ola", "Paweł"), "ola")              # regresja: nazwa z pliku nie podszywa się
        self.assertEqual(pw.nazwa_osoby("ola", "x@example.com"), "ola")
        self.assertEqual(pw.nazwa_osoby("ola", None), "ola")

    def test_dopelniacz(self):
        self.assertEqual(pw.dopelniacz("Paweł"), "Pawła")
        self.assertEqual(pw.dopelniacz("Karol"), "Karola")
        self.assertEqual(pw.dopelniacz("przeczytaj"), "osoby przeczytaj")


class TestLadunek(unittest.TestCase):
    def test_tylko_aktywne_i_dozwolone_pola(self):
        lista = [praca("a", ["model:rycerz"], etap="Budowa", kto="Claude (Karol)", opis="tajny opis",
                       komunikat="x", raport="r-1", dotyczy={"typ": "pytanie", "id": "3"}, token="abc123"),
                 praca("b", stan="wstrzymane"), praca("c", stan="gotowe"), praca("d", stan="blad"), praca("a")]
        d = pw.ladunek(lista, {"osoba": "karol", "nazwa": "Karol"}, teraz=T(12))
        self.assertEqual((d["wersja"], d["osoba"], d["nazwa"]), (1, "karol", "Karol"))
        self.assertEqual(d["aktualizacja"], T(12).astimezone().isoformat(timespec="seconds"))
        self.assertEqual([p["id"] for p in d["prace"]], ["a", "b"])        # bez zakończonych i bez powtórzeń
        self.assertEqual(set(d["prace"][0]), {"id", "tytul", "stan", "etap", "start", "obszary", "kto"})
        tekst = json.dumps(d, ensure_ascii=False)
        for zakazane in ("tajny", "abc123", "token", "r-1", "komunikat", "dotyczy"):
            self.assertNotIn(zakazane, tekst)

    def test_bez_sciezek_i_emaili(self):
        lista = [praca("a", ["model:x", "C:\\Users\\tester\\a", "../x"], tytul="Pliki w C:\\Users\\tester\\Desktop",
                       etap="ola@example.com pisze", kto="/home/tester")]
        d = pw.ladunek(lista, {"osoba": "karol", "nazwa": "Karol"})
        tekst = json.dumps(d, ensure_ascii=False)
        self.assertNotIn("tester", tekst)
        self.assertNotIn("@", tekst)
        self.assertEqual(d["prace"][0]["obszary"], ["model:x"])

    def test_filtr_publiczny_adresy_tokeny_kody(self):
        """Regresja (wroga kontrola): adres tunelu, kod, tokeny, ścieżka względna z nazwą użytkownika i „@” w obszarze
        nie mogą pójść na publiczną gałąź."""
        lista = [praca("a", ["model:x", "studio:karol@gmail.com", "Users/tester/AppData", "swiat/las"],
                       tytul="Link https://a-b.trycloudflare.com/?kod=482913 i a-b.trycloudflare.com kod 1234 "
                             "token ghp_ABCDEFGHIJKLMNOP1234 bot 123456789:AAAAAAAAAAAAAAAAAAAAAAAAAA",
                       etap="w Users/tester/Desktop, hasło: tajne123", kto="Claude (sk-abcdefghijklmnop)")]
        d = pw.ladunek(lista, {"osoba": "karol", "nazwa": "Karol"})
        tekst = json.dumps(d, ensure_ascii=False)
        for zakazane in ("trycloudflare", "482913", "1234", "ghp_", "AAAAAAAA", "tester", "tajne123", "sk-abc", "@",
                         "https"):
            self.assertNotIn(zakazane, tekst, zakazane)
        self.assertEqual(d["prace"][0]["obszary"], ["model:x", "swiat/las"])
        self.assertIn("kod …", d["prace"][0]["tytul"])
        # zwykłe słowa zostają
        d = pw.ladunek([praca("b", tytul="Kod walki i klucz do mapy v2", etap="Pin postaci")],
                       {"osoba": "karol", "nazwa": "Karol"})
        self.assertEqual((d["prace"][0]["tytul"], d["prace"][0]["etap"]), ("Kod walki i klucz do mapy v2", "Pin postaci"))

    def test_komputer_i_scalanie_list(self):
        ja_ = {"osoba": "karol", "nazwa": "Karol"}
        inne = [dict(praca("z-drugiego"), komputer="bbbbbbbb"), dict(praca("moja"), komputer="aaaaaaaa"),
                dict(praca("bez-komputera"))]
        d = pw.ladunek([praca("moja"), dict(praca("x"), komputer="ffffffff")], ja_, komputer="aaaaaaaa", inne=inne)
        self.assertEqual([(p["id"], p["komputer"]) for p in d["prace"]],
                         [("moja", "aaaaaaaa"), ("x", "aaaaaaaa"), ("z-drugiego", "bbbbbbbb")])

    def test_limity(self):
        lista = [praca("p%d" % i, tytul="T" * 500) for i in range(80)]
        d = pw.ladunek(lista, {"osoba": "karol", "nazwa": "K" * 100})
        self.assertEqual(len(d["prace"]), pw.MAKS_PRAC)
        self.assertLessEqual(len(d["prace"][0]["tytul"]), prace.MAX_TYTUL)
        self.assertLessEqual(len(d["nazwa"]), pw.MAKS_NAZWA)


class TestObceDane(unittest.TestCase):
    """Plik prace.json z cudzej gałęzi publicznego repozytorium — dane wrogie."""

    def poprawny(self, **zmiany):
        d = {"wersja": 1, "osoba": "pawel", "nazwa": "Paweł", "aktualizacja": T(11).isoformat(),
             "prace": [praca("rycerz-helm", ["model:rycerz"], etap="Budowa", kto="Claude (Paweł)",
                             koniec=T(13).isoformat())]}
        d.update(zmiany)
        return json.dumps(d)

    def test_poprawny(self):
        o, uwaga = pw.czytaj_obcy(self.poprawny(), "pawel")
        self.assertIsNone(uwaga)
        self.assertEqual((o["osoba"], o["nazwa"], len(o["prace"])), ("pawel", "Paweł", 1))
        self.assertEqual(o["prace"][0]["obszary"], ["model:rycerz"])

    def test_osoba_z_nazwy_galezi(self):
        o, _ = pw.czytaj_obcy(self.poprawny(osoba="karol", nazwa="Karol"), "pawel")
        self.assertEqual((o["osoba"], o["nazwa"]), ("pawel", "Paweł"))      # gałąź mówi, czyj to stan

    def test_za_duzy_plik(self):
        o, uwaga = pw.czytaj_obcy(b"{" + b" " * (pw.MAKS_BAJTOW + 10) + b"}", "pawel")
        self.assertIsNone(o)
        self.assertIn("za duży", uwaga)

    def test_zle_typy(self):
        for zle in (b"", b"nie json", b"[]", b"123", b'"tekst"', b"null", b'{"wersja": 2, "prace": []}',
                    b'{"wersja": true, "prace": []}', b'{"wersja": "1", "prace": []}', b'{"wersja": 1}',
                    b'{"wersja": 1, "prace": {}}', b'{"wersja": 1, "prace": "x"}', b"\xff\xfe\x00",
                    b"[" * 5000 + b"]" * 5000, 12, None):
            with self.subTest(zle=str(zle)[:40]):
                o, uwaga = pw.czytaj_obcy(zle, "pawel")
                self.assertIsNone(o)
                self.assertTrue(uwaga)

    def test_zle_prace_pomijane(self):
        d = {"wersja": 1, "aktualizacja": "jutro", "nazwa": ["lista"], "nieznane": {"x": 1},
             "prace": [None, 5, "x", [], {"id": "../../etc", "stan": "w_toku"}, {"id": "ok-1", "stan": "gotowe"},
                       {"id": "Z wielkiej", "stan": "w_toku"}, {"stan": "w_toku"},
                       {"id": "ok-2", "stan": "w_toku", "tytul": 5, "etap": {"x": 1}, "kto": ["a"],
                        "start": "0001-01-01T00:00", "koniec_szacowany": "x" * 1000,
                        "obszary": ["../../etc/passwd", "C:\\Windows", "/root", "model:ok", 7, "x" * 500, "~/.ssh"],
                        "polecenie": "rm -rf /", "sciezka": "C:\\Users\\tester"},
                       {"id": "ok-2", "stan": "w_toku", "tytul": "duplikat"}]}
        o, uwaga = pw.czytaj_obcy(json.dumps(d), "pawel")
        self.assertIsNone(uwaga)
        self.assertIsNone(o["aktualizacja"])
        self.assertEqual(o["nazwa"], "Paweł")
        self.assertEqual([p["id"] for p in o["prace"]], ["ok-2"])
        self.assertEqual(o["prace"][0], {"id": "ok-2", "tytul": "ok-2", "stan": "w_toku", "obszary": ["model:ok"]})
        tekst = json.dumps(o)
        for zakazane in ("rm -rf", "tester", "passwd", "Windows", "polecenie", "sciezka", "nieznane"):
            self.assertNotIn(zakazane, tekst)

    def test_html_zostaje_zwyklym_tekstem(self):
        d = json.loads(self.poprawny())
        d["prace"][0]["tytul"] = "<img src=x onerror=alert(1)> Rycerz"
        d["nazwa"] = "<script>alert(1)</script>"
        o, _ = pw.czytaj_obcy(json.dumps(d), "ola")
        self.assertEqual(o["prace"][0]["tytul"], "<img src=x onerror=alert(1)> Rycerz")   # interfejs: węzły tekstu
        self.assertEqual(o["nazwa"], "ola")                                   # nazwa z nazwy gałęzi, nie z pliku
        self.assertNotIn("\n", o["prace"][0]["tytul"])

    def test_c1_kierunek_i_zerowa_szerokosc(self):
        """Regresja: \\x9b (CSI), U+202E, U+2066, U+200B nie przechodzą z cudzego pliku (ani w obszarze studio:)."""
        d = json.loads(self.poprawny())
        d["prace"][0].update(tytul="ok\u009b2J\u009b31mRED abc‮GPJ.exe", etap="​⁦x", kto="a‮b",
                             obszary=["studio:‮Kontener", "studio:ok\u009b2J", "model:rycerz"])
        o, _ = pw.czytaj_obcy(json.dumps(d), "pawel")
        p = o["prace"][0]
        tekst = p["tytul"] + p["etap"] + p["kto"] + "".join(p["obszary"])
        self.assertNotRegex(tekst, "[\u0080-\u009f​-‏‪-‮⁠-⁩]")
        self.assertEqual(p["tytul"], "ok2J31mRED abcGPJ.exe")
        self.assertEqual(p["obszary"], ["model:rycerz"])

    def test_dane_z_przyszlosci_i_praca_bez_zmian(self):
        """Regresja: praca bez --koniec, której nikt nie zamknął, staje się nieaktualna po 12 h bez zmian; data
        z dalekiej przyszłości (zły zegar, złośliwe dane) nie robi pracy ani stanu „wiecznie aktualnym”."""
        moje = [praca("m", ["model:rycerz"])]
        stara = praca("a", ["model:rycerz"], start=T(9, dzien=12).isoformat())                 # 3 dni temu
        swieza = praca("b", ["model:rycerz"], start=T(9, dzien=12).isoformat(), aktualizacja=T(11).isoformat())
        z_przyszlosci = praca("c", ["model:rycerz"], start=T(9, dzien=12).isoformat(),
                              aktualizacja=T(12, dzien=25).isoformat())
        k = pw.kolizje(moje, [osoba("pawel", [stara, swieza, z_przyszlosci], aktualizacja=T(11).isoformat())],
                       teraz=T(12))
        stan = {x["ich"]["id"]: x["nieaktualne"] for x in k}
        self.assertEqual(stan, {"a": True, "b": False, "c": True})
        self.assertIn("bez zmian od 75 h", [x for x in k if x["ich"]["id"] == "a"][0]["powod"])
        przyszly_stan = osoba("pawel", [swieza], aktualizacja=T(12, dzien=25).isoformat())
        self.assertTrue(pw.nieaktualny_stan(przyszly_stan, teraz=T(12)))
        self.assertTrue(pw.kolizje(moje, [przyszly_stan], teraz=T(12))[0]["nieaktualne"])
        # do 10 min naprzód (różnica zegarów) = teraz
        self.assertFalse(pw.nieaktualny_stan(osoba("pawel", [], aktualizacja=T(12, 9).isoformat()), teraz=T(12)))

    def test_znaki_sterujace_i_dlugosci(self):
        d = json.loads(self.poprawny())
        d["prace"][0]["tytul"] = "a\x00b\x1b[31mc\r\nd" + "x" * 400
        o, _ = pw.czytaj_obcy(json.dumps(d), "pawel")
        t = o["prace"][0]["tytul"]
        self.assertLessEqual(len(t), prace.MAX_TYTUL)
        self.assertNotRegex(t, r"[\x00-\x1f]")

    def test_za_duzo_prac(self):
        d = json.loads(self.poprawny())
        d["prace"] = [praca("p%d" % i) for i in range(70)]
        o, _ = pw.czytaj_obcy(json.dumps(d), "pawel")
        self.assertEqual(len(o["prace"]), pw.MAKS_PRAC)
        self.assertTrue(o["ucieto"])


class TestKolizje(unittest.TestCase):
    def test_zgloszone(self):
        moje = [praca("przebudowa-rycerz", ["model:rycerz"]), praca("las", ["mapa:las"]), praca("bez-obszarow"),
                praca("stara", ["model:rycerz"], stan="gotowe")]
        inni = [osoba("pawel", [praca("rycerz-helm", ["swiat/postacie/wynik/rycerz"], etap="Budowa",
                                      koniec=T(13).isoformat()), praca("ui", ["src/gui"])])]
        k = pw.kolizje(moje, inni, teraz=T(12))
        self.assertEqual(len(k), 1)
        self.assertEqual((k[0]["osoba"], k[0]["nazwa"], k[0]["moja"]["id"], k[0]["ich"]["id"]),
                         ("pawel", "Pawel", "przebudowa-rycerz", "rycerz-helm"))
        self.assertEqual(k[0]["wspolne"], ["model:rycerz ~ swiat/postacie/wynik/rycerz"])
        self.assertFalse(k[0]["nieaktualne"])
        self.assertEqual(k[0]["ich"]["etap"], "Budowa")

    def test_nieaktualne(self):
        moje = [praca("m", ["model:rycerz"])]
        inni = [osoba("stary", [praca("a", ["model:rycerz"])], aktualizacja=T(0).isoformat()),           # 12 h + 1 min
                osoba("bezdaty", [praca("b", ["model:rycerz"])], aktualizacja="nie data"),
                osoba("pawel", [praca("c", ["model:rycerz"], koniec=T(5, 59).isoformat()),               # 6 h 1 min po
                                praca("d", ["model:rycerz"], koniec=T(6, 1).isoformat()),                # 5 h 59 min po
                                praca("e", ["model:rycerz"])])]
        k = pw.kolizje(moje, inni, teraz=T(12, 1))
        stan = {x["ich"]["id"]: x["nieaktualne"] for x in k}
        self.assertEqual(stan, {"a": True, "b": True, "c": True, "d": False, "e": False})
        self.assertEqual([x["nieaktualne"] for x in k], [False, False, True, True, True])     # aktualne pierwsze
        powody = {x["ich"]["id"]: x.get("powod") for x in k}
        self.assertIn("sprzed 12 h", powody["a"])
        self.assertIn("bez daty", powody["b"])
        self.assertIn("minął 6 h", powody["c"])
        self.assertIsNone(powody["d"])

    def test_granice_staleness(self):
        self.assertFalse(pw.nieaktualny_stan({"aktualizacja": T(0).isoformat()}, teraz=T(12)))
        self.assertTrue(pw.nieaktualny_stan({"aktualizacja": T(0).isoformat()}, teraz=T(12, 1)))
        self.assertTrue(pw.nieaktualny_stan({"aktualizacja": T(20).isoformat()}, teraz=T(12)))    # przyszłość = brak
        self.assertFalse(pw.nieaktualna_praca({}, teraz=T(12)))
        self.assertFalse(pw.nieaktualna_praca({"koniec_szacowany": T(6).isoformat()}, teraz=T(12)))
        self.assertTrue(pw.nieaktualna_praca({"koniec_szacowany": T(6).isoformat()}, teraz=T(12, 1)))

    def test_studio_tylko_z_tym_samym_kontenerem(self):
        moje = [praca("m", ["studio:DemoLesnaBaza"])]
        inni = [osoba("pawel", [praca("a", ["studio:demolesnabaza"]), praca("b", ["studio:Inny"]),
                                praca("c", ["swiat"])])]
        self.assertEqual([x["ich"]["id"] for x in pw.kolizje(moje, inni, teraz=T(12))], ["a"])


class TestTelegram(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_pw_tg_")
        self.rt = mock.patch.object(rdzen, "RUNTIME", self.tmp)
        self.rt.start()
        self.wyslane = []
        self.tg = mock.patch.object(gitsync, "_telegram", lambda t: self.wyslane.append(t) or 1)
        self.tg.start()

    def tearDown(self):
        self.tg.stop()
        self.rt.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_jedna_wiadomosc_na_nowa_kolizje(self):
        ja_ = {"osoba": "karol", "nazwa": "Karol"}
        moje = [praca("m", ["model:rycerz"], tytul="Przebudowa rycerza")]
        inni = [osoba("pawel", [praca("a", ["model:rycerz"], tytul="Hełm <b>")], nazwa="Paweł")]
        k = pw.kolizje(moje, inni, teraz=T(12))
        self.assertEqual(pw.powiadom(k, ja_), 1)
        self.assertEqual(len(self.wyslane), 1)
        self.assertIn("Karol — „Przebudowa rycerza”", self.wyslane[0])
        self.assertIn("Paweł — „Hełm <b>”", self.wyslane[0])
        self.assertIn("model:rycerz", self.wyslane[0])
        t0 = time.time()
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0), 0)                  # ta sama kolizja — bez drugiej wiadomości
        self.assertEqual(pw.powiadom([], ja_, teraz_s=t0 + 60), 0)            # zniknęła na chwilę…
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + 120), 0)            # …i wróciła: regresja — bez powtórki
        self.assertEqual(len(self.wyslane), 1)
        self.assertEqual(pw.powiadom([], ja_, teraz_s=t0 + 200), 0)
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + pw.OKNO_POWIADOMIEN_S + 300), 1)   # po 12 h — znowu nowa
        self.assertEqual(len(self.wyslane), 2)

    def test_nieudana_wysylka_czeka_na_kolejny_obieg(self):
        """Regresja: klucz zapisany jako zgłoszony tylko po udanej wysyłce; błąd bota = ponowna próba po 15 min."""
        wyniki = [0, 1]
        self.tg.stop()
        self.tg = mock.patch.object(gitsync, "_telegram", lambda t: self.wyslane.append(t) or wyniki.pop(0))
        self.tg.start()
        ja_ = {"osoba": "karol", "nazwa": "Karol"}
        k = pw.kolizje([praca("m", ["model:rycerz"])], [osoba("pawel", [praca("a", ["model:rycerz"])])], teraz=T(12))
        t0 = time.time()
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0), 0)                  # bot nie odpowiedział
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + 60), 0)             # za wcześnie na ponowną próbę
        self.assertEqual(len(self.wyslane), 1)
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + pw.PONOW_TELEGRAM_S + 1), 1)
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + pw.PONOW_TELEGRAM_S + 100), 0)
        self.assertEqual(len(self.wyslane), 2)

    def test_nieaktualne_i_wylaczony_telegram(self):
        ja_ = {"osoba": "karol", "nazwa": "Karol"}
        moje = [praca("m", ["model:rycerz"])]
        stare = pw.kolizje(moje, [osoba("pawel", [praca("a", ["model:rycerz"])], aktualizacja=T(0).isoformat())],
                           teraz=T(23))
        self.assertEqual(pw.powiadom(stare, ja_), 0)
        nowe = pw.kolizje(moje, [osoba("pawel", [praca("b", ["model:rycerz"])])], teraz=T(12))
        self.assertEqual(pw.powiadom(nowe, ja_, wysylaj=False), 0)            # git.auto_telegram = false
        self.assertEqual(pw.powiadom(nowe, ja_), 0)                           # już zapisana jako znana
        self.assertEqual(self.wyslane, [])

    def test_najwyzej_trzy_naraz(self):
        moje = [praca("m", ["model:rycerz"])]
        inni = [osoba("pawel", [praca("p%d" % i, ["model:rycerz"]) for i in range(8)])]
        k, ja_, t0 = pw.kolizje(moje, inni, teraz=T(12)), {"osoba": "karol", "nazwa": "Karol"}, time.time()
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0), 3)
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + 90), 0)            # regresja: najwyżej 3 na godzinę…
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + 3700), 3)          # …a reszta nie ginie: idzie w kolejnej
        self.assertEqual(pw.powiadom(k, ja_, teraz_s=t0 + 7400), 2)
        self.assertEqual(len(set(self.wyslane)), 8)

    def test_brak_bota_nic(self):
        self.tg.stop()
        try:
            with mock.patch("bc.telegram.wyslij_do_zespolu", return_value=0) as w:
                n = pw.powiadom(pw.kolizje([praca("m", ["a"])], [osoba("pawel", [praca("x", ["a"])])], teraz=T(12)),
                                {"osoba": "karol", "nazwa": "Karol"})
            self.assertEqual(n, 0)
            self.assertEqual(w.call_count, 1)
        finally:
            self.tg.start()


class TestBezpiecznik(unittest.TestCase):
    def test_prawdziwe_repozytorium_bez_sieci_w_testach(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("BC_PRACE_BEZ_SIECI", None)
            self.assertIn("bezpiecznik", pw.powod_bez_sieci(rdzen.REPO))
            w = pw.publikuj(rdzen.REPO, [praca("x")], {"osoba": "test", "nazwa": "Test"})
        self.assertEqual(w["wynik"], "wylaczone")

    def test_zmienna_i_opcja(self):
        tmp = tempfile.mkdtemp(prefix="bc_test_pw_bez_")
        try:
            with mock.patch.dict(os.environ, {"BC_PRACE_BEZ_SIECI": "1", "BC_PRACE_WYMIANA": "1"}):
                self.assertIn("BC_PRACE_BEZ_SIECI", pw.powod_bez_sieci(tmp))
            with mock.patch.dict(os.environ, {"BC_PRACE_WYMIANA": "1"}):
                os.environ.pop("BC_PRACE_BEZ_SIECI", None)
                self.assertIsNone(pw.powod_bez_sieci(tmp))
                self.assertIn("--bez-sieci", pw.powod_bez_sieci(tmp, bez_sieci=True))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_wymiana_domyslnie_wylaczona(self):
        """Regresja (wysoka): bez zgody właściciela nic nie idzie na GitHuba — `prace.wymiana` domyślnie wyłączona."""
        tmp = tempfile.mkdtemp(prefix="bc_test_pw_wl_")
        try:
            with mock.patch.dict(os.environ):
                for z in ("BC_PRACE_BEZ_SIECI", "BC_PRACE_WYMIANA"):
                    os.environ.pop(z, None)
                with mock.patch.object(rdzen, "konfiguracja", return_value={}):
                    self.assertFalse(pw.wymiana_wlaczona())
                    self.assertIn("prace.wymiana", pw.powod_bez_sieci(tmp))
                    self.assertEqual(pw.publikuj(tmp, [praca("x")], {"osoba": "t", "nazwa": "T"})["wynik"], "wylaczone")
                for zle in ({"prace": {"wymiana": "true"}}, {"prace": True}, {"prace": {"wymiana": 1}}):
                    with mock.patch.object(rdzen, "konfiguracja", return_value=zle):
                        self.assertFalse(pw.wymiana_wlaczona(), zle)
                with mock.patch.object(rdzen, "konfiguracja", return_value={"prace": {"wymiana": True}}):
                    self.assertTrue(pw.wymiana_wlaczona())
                    self.assertIsNone(pw.powod_bez_sieci(tmp))
                    with mock.patch.dict(os.environ, {"BC_PRACE_WYMIANA": "0"}):
                        self.assertFalse(pw.wymiana_wlaczona())               # awaryjne wyłączenie
                with mock.patch.object(rdzen, "konfiguracja", side_effect=ValueError("zły plik")):
                    self.assertFalse(pw.wymiana_wlaczona())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# =========================================================================== git: repozytoria próbne
class BazaGita(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_pw_git_")
        self.env = mock.patch.dict(os.environ, dict(_srodowisko_gita(self.tmp), BC_PRACE_WYMIANA="1"))
        self.env.start()
        os.environ.pop("BC_PRACE_BEZ_SIECI", None)                     # tylko repozytoria próbne poniżej
        os.environ.pop("BC_PRACE_OSOBA", None)
        self.rt = mock.patch.object(rdzen, "RUNTIME", os.path.join(self.tmp, "runtime"))
        self.rt.start()
        self.logi = []
        self.log = mock.patch.object(rdzen, "log", lambda *a: self.logi.append(" ".join(str(x) for x in a)))
        self.log.start()
        pw._ja_pamiec.clear()
        self.zdalne = os.path.join(self.tmp, "zdalne.git")
        self.g(["init", "-q", "--bare", "-b", "main", self.zdalne], self.tmp)
        self.karol = self.klon("karol", "Karol Balucki")
        self.pisz(self.karol, "README.md", "repo próbne\n")
        self.pisz(self.karol, "swiat/las/czesci.json", "{}\n")
        self.g(["add", "-A"], self.karol)
        self.g(["commit", "-q", "-m", "start"], self.karol)
        self.g(["push", "-q", "-u", "origin", "main"], self.karol)
        self.pawel = self.klon("pawel", "Paweł")
        self.karol2 = self.klon("karol2", "Karol")
        self.polecenia = []
        prawdziwy = pw._git

        def zapisujacy(argumenty, repo, *a, **kw):
            self.polecenia.append(list(argumenty))
            return prawdziwy(argumenty, repo, *a, **kw)
        self.zapis = mock.patch.object(pw, "_git", zapisujacy)
        self.zapis.start()

    def tearDown(self):
        self.zapis.stop()
        self.log.stop()
        self.rt.stop()
        self.env.stop()
        pw._ja_pamiec.clear()

        def zdejmij(fn, sciezka, _):
            os.chmod(sciezka, 0o700)
            fn(sciezka)
        for _ in range(10):
            try:
                shutil.rmtree(self.tmp, onerror=zdejmij)
                break
            except OSError:
                time.sleep(0.3)

    def g(self, args, cwd):
        # GIT_OPTIONAL_LOCKS=0: `git status` testu nie odświeża indeksu (inaczej migawka „przed” sama by go zmieniła)
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0"), creationflags=BEZ_OKNA)
        if r.returncode != 0:
            raise RuntimeError("git %s: %s %s" % (" ".join(args), r.stdout, r.stderr))
        return r.stdout

    def klon(self, nazwa, imie):
        cel = os.path.join(self.tmp, nazwa)
        self.g(["clone", "-q", "-c", "core.autocrlf=false", self.zdalne, cel], self.tmp)
        self.g(["config", "user.name", imie], cel)
        self.g(["config", "user.email", "%s@example.invalid" % nazwa], cel)
        try:
            self.g(["checkout", "-q", "-B", "main", "--track", "origin/main"], cel)
        except RuntimeError:
            self.g(["checkout", "-q", "-B", "main"], cel)
        return cel

    def pisz(self, repo, rel, tekst):
        p = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(tekst)

    def migawka(self, repo):
        """Wszystko, czego wymiana NIE może ruszyć: HEAD, main, lista gałęzi, indeks, status, pliki, stash."""
        pliki = {}
        for dp, dn, fs in os.walk(repo):
            dn[:] = [d for d in dn if d != ".git"]
            for f in fs:
                p = os.path.join(dp, f)
                with open(p, "rb") as h:
                    pliki[os.path.relpath(p, repo)] = (h.read(), os.stat(p).st_mtime_ns)
        indeks = os.path.join(repo, ".git", "index")
        with open(indeks, "rb") as h:
            ind = (h.read(), os.stat(indeks).st_mtime_ns)
        return {"head": self.g(["rev-parse", "HEAD"], repo), "symref": self.g(["symbolic-ref", "HEAD"], repo),
                "galezie": self.g(["for-each-ref", "--format=%(refname) %(objectname)", "refs/heads"], repo),
                "status": self.g(["status", "--porcelain=v1", "-uall"], repo), "indeks": ind, "pliki": pliki,
                "stash": self.g(["stash", "list"], repo)}

    def galaz_zdalna(self, slug):
        try:
            return self.g(["rev-parse", "refs/heads/stan/prace-" + slug], self.zdalne).strip()
        except RuntimeError:
            return None

    def plik_zdalny(self, slug):
        return json.loads(self.g(["show", "refs/heads/stan/prace-%s:prace.json" % slug], self.zdalne))

    def bez_force(self):
        for c in self.polecenia:
            if c and c[0] == "push":
                self.assertFalse(any(x in ("-f", "--force", "--force-with-lease", "--mirror") or x.startswith("+")
                                     or x.startswith("--force") for x in c[1:]), c)


class TestWymianaGit(BazaGita):
    def test_publikacja_i_odczyt_bez_dotykania_pracy(self):
        self.pisz(self.karol, "README.md", "zmiana w toku\n")                 # niezapisana praca w katalogu roboczym
        self.pisz(self.karol, "nowy.txt", "nieśledzony\n")
        self.g(["add", "nowy.txt"], self.karol)                               # i coś w indeksie
        przed, main_przed = self.migawka(self.karol), self.g(["rev-parse", "main"], self.zdalne)
        w = pw.publikuj(self.karol, [praca("biom-las", ["mapa:las"], tytul="Biom Las", kto="Claude (Karol)")])
        self.assertEqual(w["wynik"], "wyslano", w)
        self.assertEqual(self.migawka(self.karol), przed)
        self.assertEqual(self.g(["rev-parse", "main"], self.zdalne), main_przed)
        self.assertEqual(self.g(["for-each-ref", "--format=%(refname)", "refs/heads"], self.zdalne).split(),
                         ["refs/heads/main", "refs/heads/stan/prace-karol"])
        d = self.plik_zdalny("karol")
        self.assertEqual((d["wersja"], d["osoba"], d["nazwa"]), (1, "karol", "Karol"))
        self.assertEqual(d["prace"][0]["obszary"], ["mapa:las"])
        drzewo = self.g(["ls-tree", "-r", "--name-only", "refs/heads/stan/prace-karol"], self.zdalne).split()
        self.assertEqual(drzewo, ["prace.json"])                               # tylko ten jeden plik
        autor = self.g(["log", "-1", "--format=%an|%ae|%cn|%ce", "refs/heads/stan/prace-karol"], self.zdalne).strip()
        self.assertEqual(autor, "Panel BC (Karol)|%s|Panel BC (Karol)|%s" % (pw.EMAIL_PANELU, pw.EMAIL_PANELU))
        self.assertNotIn("karol@example.invalid",                             # adres osoby nie idzie na gałąź stanu
                         self.g(["log", "--format=%ae %ce", "refs/heads/stan/prace-karol"], self.zdalne))
        # Paweł czyta (bez dotykania swojej pracy)
        przed_p = self.migawka(self.pawel)
        p = pw.odswiez_innych(self.pawel)
        self.assertEqual(self.migawka(self.pawel), przed_p)
        self.assertEqual([(o["osoba"], o["nazwa"], [x["id"] for x in o["prace"]]) for o in p["osoby"]],
                         [("karol", "Karol", ["biom-las"])])
        self.assertIsNone(p["uwaga"])
        self.assertEqual(pw.pamiec_innych(self.pawel)["osoby"], p["osoby"])  # pamięć podręczna
        # własna gałąź nie jest „innym”
        self.assertEqual(pw.odswiez_innych(self.karol)["osoby"], [])
        self.bez_force()
        self.assertFalse([c for c in self.polecenia if c and c[0] in ("checkout", "reset", "merge", "rebase", "stash",
                                                                         "add", "commit", "pull", "switch")])

    def test_bez_zmian_nic_i_pusta_lista(self):
        self.assertEqual(pw.publikuj(self.karol, [])["wynik"], "nic")         # bez prac — gałąź nie powstaje
        self.assertIsNone(self.galaz_zdalna("karol"))
        lista = [praca("a", ["model:x"])]
        self.assertEqual(pw.publikuj(self.karol, lista)["wynik"], "wyslano")
        tip = self.galaz_zdalna("karol")
        self.assertEqual(pw.publikuj(self.karol, lista)["wynik"], "bez_zmian")
        self.assertEqual(self.galaz_zdalna("karol"), tip)
        self.assertEqual(pw.publikuj(self.karol, lista, wymus=True)["wynik"], "wyslano")
        tip2 = self.galaz_zdalna("karol")
        self.g(["merge-base", "--is-ancestor", tip, tip2], self.zdalne)       # historia rośnie, bez nadpisania
        self.assertEqual(pw.publikuj(self.karol, [])["wynik"], "wyslano")     # koniec prac = pusta lista
        self.assertEqual(self.plik_zdalny("karol")["prace"], [])
        self.assertEqual(pw.publikuj(self.karol, [])["wynik"], "bez_zmian")
        self.bez_force()

    def test_bicie_serca(self):
        lista = [praca("a", ["model:x"])]
        pw.publikuj(self.karol, lista)
        tip = self.galaz_zdalna("karol")
        pozniej = datetime.datetime.now().astimezone() + datetime.timedelta(seconds=pw.BICIE_S + 5)
        self.assertEqual(pw.publikuj(self.karol, lista, teraz=pozniej - datetime.timedelta(hours=1))["wynik"],
                         "bez_zmian")
        self.assertEqual(pw.publikuj(self.karol, lista, teraz=pozniej)["wynik"], "wyslano")
        self.assertNotEqual(self.galaz_zdalna("karol"), tip)

    def test_drobne_zmiany_najwyzej_raz_na_10_min(self):
        """Regresja: każda zmiana etapu nie robi osobnego commita na publicznej gałęzi."""
        t0 = datetime.datetime.now().astimezone()
        self.assertEqual(pw.publikuj(self.karol, [praca("a", ["model:x"], etap="Plan")], teraz=t0)["wynik"], "wyslano")
        tip = self.galaz_zdalna("karol")
        for i, etap in enumerate(("Budowa", "Kontrola", "Raport")):
            w = pw.publikuj(self.karol, [praca("a", ["model:x"], etap=etap, tytul="Nowy tytuł %d" % i)],
                            teraz=t0 + datetime.timedelta(minutes=2 + i))
            self.assertEqual(w["wynik"], "odlozone", w)
        self.assertEqual(self.galaz_zdalna("karol"), tip)
        # zmiana tego, od czego zależą kolizje (obszar, stan, koniec, nowa praca) — od razu
        w = pw.publikuj(self.karol, [praca("a", ["model:x", "mapa:las"], etap="Raport")],
                        teraz=t0 + datetime.timedelta(minutes=6))
        self.assertEqual(w["wynik"], "wyslano")
        self.assertEqual(pw.publikuj(self.karol, [praca("a", ["model:x", "mapa:las"], etap="Raport", stan="wstrzymane")],
                                     teraz=t0 + datetime.timedelta(minutes=7))["wynik"], "wyslano")
        # po 10 min od ostatniej publikacji drobna zmiana też idzie
        w = pw.publikuj(self.karol, [praca("a", ["model:x", "mapa:las"], etap="Koniec", stan="wstrzymane")],
                        teraz=t0 + datetime.timedelta(minutes=18))
        self.assertEqual(w["wynik"], "wyslano")
        self.assertEqual(self.plik_zdalny("karol")["prace"][0]["etap"], "Koniec")
        self.assertEqual(len(self.g(["rev-list", "refs/heads/stan/prace-karol"], self.zdalne).split()), 4)

    def test_odrzucony_push_raz_jeszcze_na_czubku(self):
        # ta sama osoba na drugim komputerze wysłała wcześniej — karol ma nieaktualny ref śledzący
        self.assertEqual(pw.publikuj(self.karol, [praca("a")])["wynik"], "wyslano")
        self.assertEqual(pw.publikuj(self.karol2, [praca("z-drugiego")])["wynik"], "wyslano")
        tip_drugiego = self.galaz_zdalna("karol")
        self.polecenia.clear()
        przed = self.migawka(self.karol)
        w = pw.publikuj(self.karol, [praca("b")])
        self.assertEqual(w["wynik"], "wyslano", w)
        tip = self.galaz_zdalna("karol")
        self.assertEqual(self.g(["rev-parse", tip + "^"], self.zdalne).strip(), tip_drugiego)   # na czubku, bez force
        # prace drugiego komputera tej samej osoby zostają (scalenie list), własne „a” zastąpione przez „b”
        self.assertEqual([x["id"] for x in self.plik_zdalny("karol")["prace"]], ["b", "z-drugiego"])
        pushe = [c for c in self.polecenia if c[0] == "push"]
        self.assertEqual(len(pushe), 2)
        self.assertTrue(any(c[0] == "fetch" for c in self.polecenia))
        self.assertEqual(self.migawka(self.karol), przed)
        self.bez_force()

    def test_ta_sama_osoba_na_dwoch_komputerach_bez_znikania(self):
        """Regresja (średnia): publikacja jednego komputera nie ukrywa prac drugiego na 6 h."""
        a, b = praca("a", ["model:rycerz"]), praca("b", ["mapa:las"])
        self.assertEqual(pw.publikuj(self.karol, [a])["wynik"], "wyslano")
        self.assertEqual(pw.publikuj(self.karol2, [b])["wynik"], "wyslano")
        self.assertEqual(pw.publikuj(self.karol, [a])["wynik"], "bez_zmian")    # dawniej: „b” znikało na 6 h
        p = pw.odswiez_innych(self.pawel)
        self.assertEqual(sorted(x["id"] for x in p["osoby"][0]["prace"]), ["a", "b"])
        # stała synchronizacja u Karola (świeży fetch) nie nadpisuje „b” i nie robi pustych commitów
        self.g(["fetch", "-q"], self.karol)
        tip = self.galaz_zdalna("karol")
        self.assertEqual(pw.publikuj(self.karol, [a])["wynik"], "bez_zmian")
        self.assertEqual(pw.publikuj(self.karol2, [b])["wynik"], "bez_zmian")
        self.assertEqual(self.galaz_zdalna("karol"), tip)
        # koniec „a” na pierwszym komputerze — „b” zostaje
        self.assertEqual(pw.publikuj(self.karol, [])["wynik"], "wyslano")
        self.assertEqual([x["id"] for x in self.plik_zdalny("karol")["prace"]], ["b"])
        self.bez_force()

    def test_zapomniana_praca_innego_komputera_znika(self):
        """Praca drugiego komputera bez zmian od ponad 12 h nie jest przenoszona przy scaleniu."""
        stara = praca("stara", ["model:x"], start=teraz_iso(hours=-30), aktualizacja=teraz_iso(hours=-20))
        self.assertEqual(pw.publikuj(self.karol2, [stara])["wynik"], "wyslano")
        self.g(["fetch", "-q"], self.karol)
        self.assertEqual(pw.publikuj(self.karol, [praca("nowa")])["wynik"], "wyslano")
        self.assertEqual([x["id"] for x in self.plik_zdalny("karol")["prace"]], ["nowa"])

    def test_imie_z_bc_osoba(self):
        """`git config bc.osoba` (gdy user.name to login) daje osobę i nazwę z zespołu; własne commity z loginu nie są
        „cudze” w sprawdzeniu (b)."""
        self.g(["config", "user.name", "login123"], self.karol2)
        self.assertEqual(pw.ja(self.karol2), {"osoba": "login123", "nazwa": "login123"})
        pw._ja_pamiec.clear()
        self.g(["config", "bc.osoba", "Paweł"], self.karol2)
        self.assertEqual(pw.ja(self.karol2), {"osoba": "pawel", "nazwa": "Paweł"})
        self.assertEqual(pw._moje_slugi(self.karol2), {"pawel", "login123"})

    def test_brak_galezi_sledzonej_nie_psuje_odczytu(self):
        """Regresja: gałąź śledzona skasowana na GitHubie (np. po scaleniu PR) — stan prac i tak się pobiera."""
        self.assertEqual(pw.publikuj(self.pawel, [praca("helm", ["model:rycerz"])])["wynik"], "wyslano")
        self.g(["checkout", "-q", "-b", "funkcja"], self.karol)
        self.g(["push", "-q", "-u", "origin", "funkcja"], self.karol)
        self.g(["update-ref", "-d", "refs/heads/funkcja"], self.zdalne)       # skasowana „na GitHubie”; ref lokalny został
        p = pw.odswiez_innych(self.karol)
        self.assertEqual([o["osoba"] for o in p["osoby"]], ["pawel"])
        self.assertIsNone(p["uwaga"])
        self.assertTrue(any("funkcja" in l for l in self.logi), self.logi)        # pierwszy fetch naprawdę padł
        self.assertEqual([len(c) for c in self.polecenia if c and c[0] == "fetch"][-1:],
                         [len(["fetch", "--quiet", "--no-tags", "--no-write-fetch-head", "--prune", "origin", "x"])])

    def test_fetch_bez_fetch_head(self):
        """Regresja: odczyt nie nadpisuje FETCH_HEAD (np. w trakcie scalania)."""
        self.g(["fetch", "-q"], self.karol)
        fh = os.path.join(self.karol, ".git", "FETCH_HEAD")
        with open(fh, "rb") as f:
            przed = f.read()
        pw.publikuj(self.pawel, [praca("helm", ["model:rycerz"])])
        self.assertEqual([o["osoba"] for o in pw.odswiez_innych(self.karol)["osoby"]], ["pawel"])
        with open(fh, "rb") as f:
            self.assertEqual(f.read(), przed)
        self.assertTrue(all("--no-write-fetch-head" in c for c in self.polecenia if c and c[0] == "fetch"))

    def test_brak_sieci_tylko_uwaga(self):
        self.g(["remote", "set-url", "origin", os.path.join(self.tmp, "nie-ma-takiego.git")], self.karol)
        t0 = time.time()
        w = pw.publikuj(self.karol, [praca("a")])
        self.assertEqual(w["wynik"], "blad")
        self.assertTrue(w["uwaga"])
        self.assertNotIn(self.tmp, w["uwaga"])
        self.assertLess(time.time() - t0, 60)
        p = pw.odswiez_innych(self.karol)
        self.assertEqual(p["osoby"], [])
        self.assertTrue(p["uwaga"])
        # następna próba nie jest „bez zmian” — poprzednia się nie udała
        self.g(["remote", "set-url", "origin", self.zdalne], self.karol)
        self.assertEqual(pw.publikuj(self.karol, [praca("a")])["wynik"], "wyslano")

    def test_wylaczona_siec(self):
        with mock.patch.dict(os.environ, {"BC_PRACE_BEZ_SIECI": "1"}):
            self.assertEqual(pw.publikuj(self.karol, [praca("a")])["wynik"], "wylaczone")
            p = pw.odswiez_innych(self.karol)
        self.assertIsNone(self.galaz_zdalna("karol"))
        self.assertFalse([c for c in self.polecenia if c and c[0] in ("push", "fetch")])
        self.assertIn("BC_PRACE_BEZ_SIECI", p["uwaga"])

    def test_wrogie_galezie(self):
        def galaz(nazwa, tresc):
            """Gałąź w repozytorium bare zbudowana „ręcznie” (jak zrobiłby to ktoś z prawem push)."""
            blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=self.zdalne, input=tresc,
                                  capture_output=True, creationflags=BEZ_OKNA).stdout.decode().strip()
            drzewo = subprocess.run(["git", "mktree"], cwd=self.zdalne, input=("100644 blob %s\tprace.json\n" % blob)
                                    .encode(), capture_output=True, creationflags=BEZ_OKNA).stdout.decode().strip()
            c = self.g(["-c", "user.name=Ktoś", "-c", "user.email=ktos@example.invalid", "commit-tree", drzewo,
                        "-m", "x"], self.zdalne).strip()
            self.g(["update-ref", "refs/heads/" + nazwa, c], self.zdalne)
        dobry = {"wersja": 1, "aktualizacja": datetime.datetime.now().astimezone().isoformat(),
                 "prace": [praca("helm", ["model:rycerz", "../../x"], tytul="<script>x</script>")]}
        galaz("stan/prace-pawel", json.dumps(dobry).encode())
        galaz("stan/prace-duzy", b'{"wersja":1,"prace":[]' + b" " * (pw.MAKS_BAJTOW + 1) + b"}")
        galaz("stan/prace-zly", b"\x00\x01nie json")
        galaz("stan/prace-Wielkie_Litery", json.dumps(dobry).encode())
        galaz("stan/inne", json.dumps(dobry).encode())
        galaz("stan/prace-karol", json.dumps(dobry).encode())                # „mój” stan od kogoś — pomijany
        p = pw.odswiez_innych(self.karol)
        self.assertEqual([o["osoba"] for o in p["osoby"]], ["pawel"])
        self.assertEqual(p["osoby"][0]["prace"][0]["obszary"], ["model:rycerz"])
        self.assertEqual(p["osoby"][0]["prace"][0]["tytul"], "<script>x</script>")
        self.assertIn("duzy: plik prac za duży", p["uwaga"])
        self.assertIn("zly:", p["uwaga"])
        # duży plik nie był czytany w całości (tylko rozmiar)
        self.assertFalse([c for c in self.polecenia if c[:2] == ["cat-file", "blob"] and "duzy" in c[2]])

    def test_zmiany_z_main(self):
        # Paweł wysyła zmiany; Karol ma niezapisaną zmianę README.md i pracę nad mapą lasu
        self.pisz(self.pawel, "README.md", "od Pawła\n")
        self.pisz(self.pawel, "swiat/las/czesci.json", '{"a": 1}\n')
        self.pisz(self.pawel, "inne.txt", "x\n")
        self.g(["add", "-A"], self.pawel)
        self.g(["commit", "-q", "-m", "zmiany Pawła"], self.pawel)
        self.g(["push", "-q"], self.pawel)
        self.pisz(self.karol2, "swiat/las/drugi.json", "{}\n")              # własny commit z drugiego komputera
        self.g(["pull", "-q", "--no-rebase"], self.karol2)
        self.g(["add", "-A"], self.karol2)
        self.g(["commit", "-q", "-m", "z drugiego komputera"], self.karol2)
        self.g(["push", "-q"], self.karol2)
        self.pisz(self.karol, "README.md", "moja zmiana\n")
        self.g(["fetch", "-q"], self.karol)
        przed = self.migawka(self.karol)
        z = pw.zmiany_z_main(self.karol, moje=[praca("las", ["mapa:las"], tytul="Las"), praca("x", ["inne.txt"],
                                                                                              stan="gotowe")])
        self.assertEqual(self.migawka(self.karol), przed)                     # tylko odczyt
        po_pliku = {w["plik"]: w for w in z}
        self.assertEqual(set(po_pliku), {"README.md", "swiat/las/czesci.json"})
        self.assertTrue(po_pliku["README.md"]["niezapisane"])
        self.assertEqual(po_pliku["README.md"]["autorzy"], ["Paweł"])
        self.assertEqual(po_pliku["swiat/las/czesci.json"]["prace"], [{"id": "las", "tytul": "Las"}])
        self.assertFalse(po_pliku["swiat/las/czesci.json"]["niezapisane"])
        # pamięć 2 h i filtr przy odczycie (praca zakończona, a plik bez lokalnych zmian — znika)
        pw._zapisz_z_main(self.karol, z)
        self.assertEqual(len(pw.z_main_z_pamieci(self.karol, [praca("las", ["mapa:las"])])), 2)
        self.assertEqual([w["plik"] for w in pw.z_main_z_pamieci(self.karol, [])], ["README.md"])
        with mock.patch.object(pw.time, "time", return_value=time.time() + pw.Z_MAIN_ZYCIE_S + 1):
            self.assertEqual(pw.z_main_z_pamieci(self.karol, [praca("las", ["mapa:las"])]), [])

    def test_petla_synchronizacji(self):
        """Zaczep w gitsync._obieg: odczyt innych, (b) przed pobraniem, publikacja i Telegram (atrapa)."""
        pw.publikuj(self.pawel, [praca("helm", ["mapa:las"], tytul="Las Pawła")])
        self.pisz(self.pawel, "swiat/las/czesci.json", '{"b": 2}\n')
        self.g(["add", "-A"], self.pawel)
        self.g(["commit", "-q", "-m", "las"], self.pawel)
        self.g(["push", "-q"], self.pawel)
        prace.rozpocznij("moj-las", "Mój las", obszary=["mapa:las"], kto="Claude (Karol)")
        wyslane, blokada_przy = [], []
        gitsync._auto.clear()
        prawdziwa = pw.publikuj

        def publikuj_patrzac(*a, **kw):
            blokada_przy.append(gitsync._zapis_blokada.locked())
            return prawdziwa(*a, **kw)

        def telegram(t):
            blokada_przy.append(gitsync._zapis_blokada.locked())
            wyslane.append(t)
            return 1
        with mock.patch.object(gitsync, "_telegram", telegram), mock.patch.object(pw, "publikuj", publikuj_patrzac):
            gitsync.obieg(self.karol, ["panel/dane"], {"co_s": 90.0, "wyslij_po_s": 60.0, "telegram": True,
                                                       "auto": True})
        gitsync._auto.clear()
        # regresja: push stanu i Telegram po zwolnieniu blokady gita (przyciski Pobierz/Wyślij nie czekają)
        self.assertTrue(blokada_przy)
        self.assertEqual(set(blokada_przy), {False})
        self.assertEqual(self.plik_zdalny("karol")["prace"][0]["id"], "moj-las")
        api = pw.dla_api(prace.aktywne(), repo=self.karol)
        self.assertEqual([(p["osoba"], p["id"]) for p in api["inni"]], [("pawel", "helm")])
        self.assertEqual([(k["moja"]["id"], k["ich"]["id"]) for k in api["kolizje"]], [("moj-las", "helm")])
        self.assertEqual([z["plik"] for z in api["z_main"]], ["swiat/las/czesci.json"])     # sprzed pobrania
        self.assertEqual(api["wymiana"]["osoba"], "karol")
        self.assertTrue(api["wymiana"]["publikacja"]["ok"])
        o_kolizji = [w for w in wyslane if w.startswith("Prace się nakładają")]   # obok: „Panel pobrał z GitHuba…”
        self.assertEqual(len(o_kolizji), 1, wyslane)
        self.assertIn("Las Pawła", o_kolizji[0])
        self.assertEqual(self.g(["rev-parse", "HEAD"], self.karol), self.g(["rev-parse", "main"], self.zdalne))
        self.bez_force()


# =========================================================================== narzędzie praca.py (kody wyjścia)
class TestNarzedzieWymiana(BazaGita):
    def praca_cli(self, kto, *argv):
        repo = {"karol": self.karol, "pawel": self.pawel}[kto]
        env = dict(os.environ, BC_PRACE_REPO=repo, BC_PANEL_RUNTIME=os.path.join(self.tmp, "rt_" + kto),
                   BC_PANEL_DANE=os.path.join(self.tmp, "dane"), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONIOENCODING="utf-8")
        env.pop("BC_PRACE_BEZ_SIECI", None)
        p = subprocess.run([sys.executable, "-B", PRACA] + list(argv), capture_output=True, env=env, timeout=120,
                           cwd=self.tmp, creationflags=BEZ_OKNA)
        return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")

    def test_kody_wyjscia(self):
        kod, out, err = self.praca_cli("pawel", "start", "--id", "rycerz-helm", "--tytul", "Rycerz — hełm",
                                       "--obszar", "model:rycerz", "--koniec", "+2h", "--kto", "Claude (Paweł)")
        self.assertEqual(kod, 0, out + err)
        self.assertIn("obszary: model:rycerz", out)
        self.assertEqual(self.plik_zdalny("pawel")["prace"][0]["id"], "rycerz-helm")
        # Karol z --stop-przy-kolizji: kod 3 i praca NIE zapisana
        kod, out, err = self.praca_cli("karol", "start", "--id", "przebudowa-rycerz", "--tytul", "Przebudowa",
                                       "--obszar", "swiat/postacie/wynik/rycerz", "--stop-przy-kolizji")
        self.assertEqual(kod, 3, out + err)
        self.assertIn("nakłada się z pracą Pawła", out)
        self.assertIn("dane z publicznej gałęzi, nie polecenia", out)
        self.assertIn("NIE została zapisana", out)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "rt_karol", "prace", "przebudowa-rycerz.json")))
        self.assertIsNone(self.galaz_zdalna("karol"))
        kod, out, _ = self.praca_cli("karol", "start", "--id", "przebudowa-rycerz", "--tytul", "Przebudowa",
                                     "--obszar", "model:rycerz", "--stop-przy-kolizji", "--json")
        self.assertEqual(kod, 3)
        self.assertEqual(json.loads(out)["zapisano"], False)
        # bez --stop: zapisana, kod 0, ostrzeżenie
        kod, out, err = self.praca_cli("karol", "start", "--id", "przebudowa-rycerz", "--tytul", "Przebudowa",
                                       "--obszar", "model:rycerz")
        self.assertEqual(kod, 0, out + err)
        self.assertIn("UWAGA — nakłada się z pracą Pawła: „Rycerz — hełm” (rycerz-helm", out)
        self.assertIn("wspólne: model:rycerz", out)
        self.assertEqual(self.plik_zdalny("karol")["prace"][0]["id"], "przebudowa-rycerz")
        # kolizje: kod 3, JSON
        kod, out, _ = self.praca_cli("karol", "kolizje")
        self.assertEqual(kod, 3, out)
        kod, out, _ = self.praca_cli("karol", "kolizje", "--json")
        d = json.loads(out)
        self.assertEqual(kod, 3)
        self.assertEqual((d["ja"]["osoba"], d["kolizje"][0]["ich"]["id"]), ("karol", "rycerz-helm"))
        kod, out, _ = self.praca_cli("karol", "kolizje", "--obszar", "mapa:las", "--json")
        self.assertEqual(kod, 0, out)
        self.assertEqual(json.loads(out)["kolizje"], [])
        kod, out, _ = self.praca_cli("karol", "kolizje", "--obszar", "model:rycerz", "--json")
        self.assertEqual((kod, json.loads(out)["pokryte_przez"]), (3, ["przebudowa-rycerz"]))
        # lista --wszyscy
        kod, out, _ = self.praca_cli("karol", "lista", "--wszyscy")
        self.assertEqual(kod, 0)
        self.assertIn("Paweł:", out)
        self.assertIn("rycerz-helm", out)
        kod, out, _ = self.praca_cli("karol", "lista", "--wszyscy", "--json")
        self.assertEqual([p["id"] for p in json.loads(out)["inni"]], ["rycerz-helm"])
        # Paweł kończy — u Karola kolizji już nie ma
        self.assertEqual(self.praca_cli("pawel", "koniec", "--id", "rycerz-helm")[0], 0)
        self.assertEqual(self.plik_zdalny("pawel")["prace"], [])
        time.sleep(0.01)
        with open(os.path.join(self.tmp, "rt_karol", "prace_wymiana", "inni.json"), "r+", encoding="utf-8") as f:
            d = json.load(f)                                                  # pamięć starsza niż minuta
            d["ts"] = 0
            f.seek(0)
            f.truncate()
            json.dump(d, f)
        kod, out, _ = self.praca_cli("karol", "kolizje")
        self.assertEqual(kod, 0, out)
        self.assertIn("Brak kolizji.", out)

    def test_kolizje_zawsze_swiezo(self):
        """Regresja: `kolizje` (i start --stop-przy-kolizji, droga przebuduj.py) nie korzysta z minutowej pamięci —
        praca drugiej osoby zgłoszona przed chwilą zatrzymuje."""
        kod, out, err = self.praca_cli("karol", "kolizje", "--obszar", "model:kot", "--json")
        self.assertEqual(kod, 0, out + err)                                   # pamięć zapisana teraz
        self.assertEqual(self.praca_cli("pawel", "start", "--id", "kot", "--tytul", "Kot", "--obszar", "model:kot")[0], 0)
        kod, out, err = self.praca_cli("karol", "kolizje", "--obszar", "model:kot", "--json")
        self.assertEqual(kod, 3, out + err)
        self.assertIsNone(json.loads(out)["odczyt"]["uwaga"])
        kod, out, err = self.praca_cli("karol", "start", "--id", "moj-kot", "--tytul", "K", "--obszar", "model:kot",
                                       "--stop-przy-kolizji")
        self.assertEqual(kod, 3, out + err)

    def test_wylaczona_wymiana_nic_nie_wysyla(self):
        """Regresja (wysoka): przy wyłączonej `prace.wymiana` narzędzie nie robi pusha ani fetch.
        Test nie zależy od wspólnego panel/konfiguracja.json (tam wymiana może być włączona): wyłącza ją w konfiguracji
        lokalnej zastępczego komputera, która ma pierwszeństwo."""
        os.environ.pop("BC_PRACE_WYMIANA", None)
        rdzen.zapisz_json(os.path.join(self.tmp, "rt_karol", "konfiguracja.lokalna.json"), {"prace": {"wymiana": False}})
        kod, out, err = self.praca_cli("karol", "start", "--id", "a", "--tytul", "A", "--obszar", "model:x")
        self.assertEqual(kod, 0, out + err)
        self.assertIsNone(self.galaz_zdalna("karol"))
        self.assertNotIn("Uwaga: stan prac nie poszedł", err)
        kod, out, err = self.praca_cli("karol", "kolizje")
        self.assertEqual(kod, 0, out + err)
        self.assertIn("Wymiana prac przez GitHuba jest wyłączona", out)
        # włączona w konfiguracji lokalnej tego komputera (w repozytorium: panel/konfiguracja.json)
        rdzen.zapisz_json(os.path.join(self.tmp, "rt_karol", "konfiguracja.lokalna.json"), {"prace": {"wymiana": True}})
        self.assertEqual(self.praca_cli("karol", "etap", "--id", "a", "--etap", "B")[0], 0)
        self.assertEqual(self.plik_zdalny("karol")["prace"][0]["id"], "a")

    def test_bez_sieci_i_zle_obszary(self):
        kod, out, err = self.praca_cli("karol", "start", "--id", "a", "--tytul", "A", "--obszar", "model:x",
                                       "--bez-sieci")
        self.assertEqual(kod, 0, out + err)
        self.assertIsNone(self.galaz_zdalna("karol"))
        kod, out, err = self.praca_cli("karol", "start", "--id", "b", "--tytul", "B", "--obszar", "../x")
        self.assertEqual(kod, 1)
        self.assertIn("Niepoprawny obszar", err)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "rt_karol", "prace", "b.json")))
        kod, out, err = self.praca_cli("karol", "start", "--id", "c", "--tytul", "C",
                                       *sum([["--obszar", "a%d" % i] for i in range(13)], []))
        self.assertEqual(kod, 1)
        self.assertIn("Za dużo obszarów", err)

    def test_brak_sieci_praca_zapisana(self):
        self.g(["remote", "set-url", "origin", os.path.join(self.tmp, "nie-ma.git")], self.karol)
        kod, out, err = self.praca_cli("karol", "start", "--id", "a", "--tytul", "A", "--obszar", "model:x")
        self.assertEqual(kod, 0, out + err)
        self.assertIn("Uwaga:", err)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "rt_karol", "prace", "a.json")))
        self.assertNotIn("Traceback", err)
        self.assertEqual(self.praca_cli("karol", "etap", "--id", "a", "--etap", "B")[0], 0)


# =========================================================================== API (prawdziwy serwer, dane z pamięci)
class TestPraceWymianaAPI(test_api.SerwerTestowy):
    @classmethod
    def przygotuj(cls, runtime):
        stare = rdzen.RUNTIME, rdzen.log
        rdzen.RUNTIME, rdzen.log = runtime, (lambda *a: None)
        try:
            prace.rozpocznij("przebudowa-rycerz", "Przebudowa rycerza", obszary=["model:rycerz"], kto="Claude (test)")
            prace.rozpocznij("bez-kolizji", "Inna praca", obszary=["mapa:las"], kto="Claude (test)")
            teraz = datetime.datetime.now().astimezone()
            osoby = [{"osoba": "testowa", "nazwa": "Testowa", "aktualizacja": teraz.isoformat(),
                      "prace": [praca("helm", ["swiat/postacie/wynik/rycerz"], tytul="<img src=x onerror=alert(1)>",
                                      kto="C:\\Users\\tester"), praca("ui", ["src/gui"])]},
                     {"osoba": "dawna", "nazwa": "Dawna", "aktualizacja": (teraz - datetime.timedelta(hours=20)).isoformat(),
                      "prace": [praca("stara", ["model:rycerz"])]},
                     {"osoba": "../zla", "prace": [praca("x", ["model:rycerz"])]}]
            rdzen.zapisz_json(os.path.join(runtime, "prace_wymiana", "inni.json"),
                              {"wersja": 1, "repo": pw._klucz_repo(rdzen.REPO), "ts": time.time(),
                               "kiedy": teraz.isoformat(timespec="seconds"), "osoby": osoby, "uwaga": None})
            rdzen.zapisz_json(os.path.join(runtime, "prace_wymiana", "z_main.json"),
                              {"repo": pw._klucz_repo(rdzen.REPO), "wpisy": [
                                  {"plik": "swiat/postacie/rycerz.py", "autorzy": ["Paweł"], "niezapisane": False,
                                   "prace": [{"id": "przebudowa-rycerz", "tytul": "Przebudowa rycerza"}],
                                   "ts": time.time(), "kiedy": teraz.isoformat(timespec="seconds")}]})
        finally:
            rdzen.RUNTIME, rdzen.log = stare

    def test_ksztalt(self):
        s, o, _ = self.get("/api/prace", zdalny=True)
        self.assertEqual(s, 200, o)
        self.assertPola(o, ["prace", "teraz", "w_toku", "najblizszy_koniec", "inni", "kolizje", "z_main", "wymiana"])
        self.assertEqual(o["w_toku"], 2)
        self.assertEqual(sorted((p["osoba"], p["id"], p["nieaktualna"]) for p in o["inni"]),
                         [("dawna", "stara", True), ("testowa", "helm", False), ("testowa", "ui", False)])
        for p in o["inni"]:
            self.assertPola(p, ["osoba", "nazwa", "id", "tytul", "stan", "obszary", "nieaktualna"])
        kol = {(k["osoba"], k["moja"]["id"], k["ich"]["id"]): k for k in o["kolizje"]}
        self.assertEqual(set(kol), {("testowa", "przebudowa-rycerz", "helm"), ("dawna", "przebudowa-rycerz", "stara")})
        self.assertFalse(kol[("testowa", "przebudowa-rycerz", "helm")]["nieaktualne"])
        self.assertTrue(kol[("dawna", "przebudowa-rycerz", "stara")]["nieaktualne"])
        self.assertEqual(o["kolizje"][0]["osoba"], "testowa")                 # aktualne pierwsze
        self.assertEqual(o["z_main"][0]["plik"], "swiat/postacie/rycerz.py")
        self.assertPola(o["wymiana"], ["osoba", "nazwa", "odczyt", "uwaga", "publikacja"])
        self.assertEqual(kol[("testowa", "przebudowa-rycerz", "helm")]["ich"]["tytul"], "<img src=x onerror=alert(1)>")
        tekst = json.dumps(o, ensure_ascii=False)
        self.assertNotIn("tester", tekst)
        self.assertNotIn("../zla", tekst)
        self.assertNotIn(":\\\\", tekst)

    def test_zdrowie_bez_zmian(self):
        s, o, _ = self.get("/api/zdrowie", timeout=60)
        self.assertTrue(o["moduly"]["prace"]["ok"], o["moduly"].get("prace"))


# =========================================================================== tools/praca_auto.py z atrapą praca.py
ATRAPA = r'''
import json, os, sys, time
argv = sys.argv[1:]
with open(os.environ["ATRAPA_LOG"], "a", encoding="utf-8") as f:
    f.write(json.dumps(argv) + "\n")
tryb = os.environ.get("ATRAPA_TRYB", "czysto")
if tryb == "spi":
    time.sleep(30)
if tryb == "smieci":
    print("to nie json"); sys.exit(1)
if argv[0] == "kolizje":
    k = {"osoba": "pawel", "nazwa": "Paweł", "moja": {"id": None}, "wspolne": ["model:rycerz"],
         "ich": {"id": "rycerz-helm", "tytul": "Rycerz — hełm", "koniec_szacowany": "2026-11-15T16:40:00+01:00"},
         "nieaktualne": tryb == "stara"}
    d = {"kolizje": [k] if tryb in ("kolizja", "stara") else [], "z_main": [],
         "pokryte_przez": ["moja-praca"] if tryb == "pokryte" else (["przebudowa-rycerz"] if tryb == "ta_sama" else [])}
    if tryb == "bez_odczytu":
        d["odczyt"] = {"kiedy": None, "uwaga": "nie udało się pobrać stanu prac z GitHuba:\nfatal: brak sieci"}
    print(json.dumps(d)); sys.exit(3 if tryb == "kolizja" else 0)
print(json.dumps({"id": argv[2] if len(argv) > 2 else None})); sys.exit(0)
'''


class TestPracaAuto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("praca_auto_test", os.path.join(REPO, "tools", "praca_auto.py"))
        cls.pa = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.pa)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_praca_auto_")
        atrapa = os.path.join(self.tmp, "atrapa_praca.py")
        with open(atrapa, "w", encoding="utf-8") as f:
            f.write(ATRAPA)
        self.log = os.path.join(self.tmp, "log.txt")
        self.env = mock.patch.dict(os.environ, {"BC_PRACA_SKRYPT": atrapa, "ATRAPA_LOG": self.log})
        self.env.start()
        os.environ.pop("BC_PRACE_BEZ_SIECI", None)
        self.ostrzezenia = []
        self.cicho = mock.patch.object(self.pa, "_ostrzez", self.ostrzezenia.append)
        self.cicho.start()

    def tearDown(self):
        self.cicho.stop()
        self.env.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def wywolania(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def tryb(self, t):
        os.environ["ATRAPA_TRYB"] = t

    def test_bez_kolizji_start_i_koniec(self):
        self.tryb("czysto")
        u = self.pa.przed("przebudowa-rycerz", "Przebudowa modelu rycerz", ["model:rycerz"])
        self.assertFalse(u.zatrzymaj)
        self.assertEqual(u.wlasne, ["przebudowa-rycerz"])
        self.pa.po(u, ok=True)
        w = self.wywolania()
        self.assertEqual([x[0] for x in w], ["kolizje", "start", "koniec"])
        self.assertEqual(w[0], ["kolizje", "--obszar", "model:rycerz", "--json"])
        self.assertIn("--obszar", w[1])
        self.assertEqual(w[2], ["koniec", "--id", "przebudowa-rycerz", "--json"])

    def test_kolizja_zatrzymuje_przed_praca(self):
        self.tryb("kolizja")
        u = self.pa.przed("przebudowa-rycerz", "Przebudowa", ["model:rycerz"])
        self.assertTrue(u.zatrzymaj)
        self.assertIn("Paweł", u.komunikat)
        self.assertIn("rycerz-helm", u.komunikat)
        self.assertIn("Rycerz — hełm", u.komunikat)
        self.assertIn("--mimo-kolizji", u.komunikat)
        self.assertEqual([x[0] for x in self.wywolania()], ["kolizje"])     # nic nie zapisane
        self.assertEqual(self.pa.KOD_KOLIZJI, 3)

    def test_mimo_kolizji_i_nieaktualna(self):
        self.tryb("kolizja")
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"], mimo_kolizji=True)
        self.assertFalse(u.zatrzymaj)
        self.assertEqual(u.wlasne, ["przebudowa-rycerz"])
        self.tryb("stara")
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"])
        self.assertFalse(u.zatrzymaj)

    def test_moja_praca_juz_obejmuje(self):
        self.tryb("pokryte")
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"])
        self.assertEqual((u.zatrzymaj, u.wlasne), (False, []))
        self.pa.po(u)
        self.assertEqual([x[0] for x in self.wywolania()], ["kolizje"])
        self.tryb("ta_sama")                                                  # ta sama praca po przerwanej przebudowie
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"])
        self.assertEqual(u.wlasne, ["przebudowa-rycerz"])

    def test_blad_konczy_jako_blad(self):
        self.tryb("czysto")
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"])
        self.pa.po(u, ok=False, komunikat="przerwana błędem")
        self.assertEqual(self.wywolania()[-1], ["blad", "--id", "przebudowa-rycerz", "--komunikat", "przerwana błędem",
                                                "--json"])
        self.pa.po(u)                                                         # drugi raz — nic
        self.assertEqual(len(self.wywolania()), 3)

    def test_kazdy_problem_tylko_ostrzezenie(self):
        self.tryb("smieci")
        u = self.pa.przed("x", "X", ["model:x"])
        self.assertEqual((u.zatrzymaj, u.wlasne), (False, []))
        self.tryb("spi")
        with mock.patch.object(self.pa, "LIMIT_SPRAWDZENIA_S", 1):
            t0 = time.time()
            u = self.pa.przed("x", "X", ["model:x"])
        self.assertLess(time.time() - t0, 20)
        self.assertEqual((u.zatrzymaj, u.wlasne), (False, []))
        with mock.patch.dict(os.environ, {"BC_PRACA_SKRYPT": os.path.join(self.tmp, "nie-ma.py")}):
            self.tryb("czysto")
            u = self.pa.przed("x", "X", ["model:x"])
        self.assertFalse(u.zatrzymaj)
        self.pa.po(None)                                                      # nie rzuca
        self.pa.po(object())
        self.assertEqual(len(self.ostrzezenia), 3)                            # każdy problem: jedna linijka
        self.assertTrue(all(chr(10) not in o and "dalej" in o for o in self.ostrzezenia), self.ostrzezenia)

    def test_bez_swiezego_stanu_ostrzega(self):
        """Regresja: nieudany odczyt stanu drugiej osoby nie jest cichym „brak kolizji” — jedna linijka ostrzeżenia."""
        self.tryb("bez_odczytu")
        u = self.pa.przed("przebudowa-rycerz", "P", ["model:rycerz"])
        self.assertFalse(u.zatrzymaj)
        self.assertEqual(len(self.ostrzezenia), 1, self.ostrzezenia)
        self.assertIn("bez świeżego stanu", self.ostrzezenia[0])
        self.assertIn("brak sieci", self.ostrzezenia[0])
        self.assertNotIn("\n", self.ostrzezenia[0])
        self.assertEqual(u.wlasne, ["przebudowa-rycerz"])                     # praca i tak zgłoszona

    def test_wylaczony_zmienna(self):
        with mock.patch.dict(os.environ, {"BC_PRACE_BEZ_SIECI": "1"}):
            self.tryb("kolizja")
            u = self.pa.przed("x", "X", ["model:x"])
        self.assertEqual((u.zatrzymaj, u.wlasne), (False, []))
        self.assertEqual(self.wywolania(), [])


if __name__ == "__main__":
    unittest.main()
