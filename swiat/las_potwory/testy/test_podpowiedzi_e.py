# -*- coding: utf-8 -*-
"""Testy poprawki M6 (17.11.2026, przejście gry: E przy chodzących potworach zaczęło walkę w 6 z 15 prób, bez
komunikatu). Bez Studio — czytają źródła jak tekst; pomiar prawdziwym E jest w swiat/stan_gracza/testy/proba_play.py.

    python -B swiat/las_potwory/testy/test_podpowiedzi_e.py

1. Podpowiedź: bez wymogu linii widzenia, zasięg aktywacji większy niż bramka klienta z zapasem histerezy, histereza
   mniejsza niż zapas serwera (serwer nie odrzuci tego, co klient pokazał).
2. Kotwica w kadrze: obie aktualizacje kotwicy idą przez punktPodpowiedzi (WorldToViewportPoint, kotwica nad postacią
   poza kadrem; atrybut testowy przywraca dawne zachowanie do porównania przed/po).
3. Brak ciszy: każdy powód odmowy serwera lasu i odmowy lokalnej odtwarzacza ma tekst; blokada po walce i brak
   odtwarzacza dają dymek; OstatniaOdmowa jest czyszczona przed prośbą o walkę.
"""
import os
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
import sprawdz_luau  # noqa: E402


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def bez_komentarzy(tekst):
    return sprawdz_luau.rozbierz(tekst)[0]


STALE = czytaj(PAKIET, "zrodla", "Stale.luau")
KLIENT = bez_komentarzy(czytaj(PAKIET, "zrodla", "KlientPotworow.client.luau"))
SERWER = bez_komentarzy(czytaj(PAKIET, "zrodla", "SerwerPotworow.server.luau"))
ODTW = bez_komentarzy(czytaj(REPO, "swiat", "test_walki2", "zrodla", "OdtwarzaczWalki2.luau"))
DANE_PASA = czytaj(REPO, "swiat", "las_pas_gra", "zrodla", "DanePotworowPasa.luau")
DANE_LASU = czytaj(PAKIET, "zrodla", "DanePotworow.luau")


def liczba(nazwa):
    m = re.search(r"^S\.%s = ([\d.]+)" % nazwa, STALE, re.M)
    assert m, nazwa
    return float(m.group(1))


class TestPodpowiedzi(unittest.TestCase):
    def test_1_zasiegi(self):
        self.assertIn("podpowiedz.RequiresLineOfSight = false", KLIENT)
        aktywacja = float(re.search(r"podpowiedz\.MaxActivationDistance = ([\d.]+)", KLIENT).group(1))
        promienie = [float(x) for x in re.findall(r"promien = ([\d.]+)", DANE_PASA + DANE_LASU)]
        bramka = liczba("ZASIEG_E") + max(promienie) + liczba("HISTEREZA_E")
        self.assertGreater(aktywacja, bramka + liczba("KOTWICA_KU_POTWOROWI"))
        self.assertLess(liczba("HISTEREZA_E"), liczba("ZAPAS_E_SERWER"))
        self.assertIn("if cfg.Name == kandydat and kontener:GetAttribute(Stale.ATRYBUT_KOTWICY_STAREJ) ~= true then\n"
                      "\t\t\tzasieg += Stale.HISTEREZA_E", KLIENT)
        # zapas na opóźnienie: bramka klienta z histerezą + 2 studs ruchu potwora ≤ bramka serwera
        self.assertLessEqual(liczba("HISTEREZA_E") + 2, liczba("ZAPAS_E_SERWER"))

    def test_2_kotwica_w_kadrze(self):
        cialo = KLIENT.split("local function naEkranie", 1)[1].split("\nend\n", 1)[0]
        self.assertIn("WorldToViewportPoint(p)", cialo)
        self.assertIn("v.Z > 0", cialo)
        pp = KLIENT.split("local function punktPodpowiedzi", 1)[1].split("\nend\n", 1)[0]
        for k in ("punktKotwicy(id)", "Stale.ATRYBUT_KOTWICY_STAREJ", "naEkranie(p)", "Stale.KOTWICA_NAD_POSTACIA"):
            self.assertIn(k, pp, k)
        # kotwica ustawiana w dwóch miejscach (co 0,1 s i co klatkę) — obie przez punktPodpowiedzi
        self.assertEqual(len(re.findall(r"punktPodpowiedzi\(kandydat", KLIENT)), 2)
        self.assertEqual(re.findall(r"punktKotwicy\(kandydat", KLIENT), [])

    def test_3_bez_ciszy(self):
        teksty = re.search(r"S\.KOMUNIKATY_ODMOWY = \{(.*?)\n\}", STALE, re.S).group(1)
        klucze = set(re.findall(r"^\s*(\w+) = \"", teksty, re.M))
        serwer = set(re.findall(r'odmowa\("(\w+)"', SERWER))
        lokalne = set(re.findall(r'"OstatniaOdmowa", "(\w+)"', ODTW))
        self.assertTrue(serwer and lokalne)
        self.assertEqual(sorted((serwer | lokalne | {"odpoczynek", "brak_odtwarzacza"}) - klucze), [])
        zw = KLIENT.split("local function zacznijWalke", 1)[1].split("\nend\n", 1)[0]
        i_odp = zw.find("Stale.KOMUNIKATY_ODMOWY.odpoczynek")
        self.assertTrue(0 < i_odp < zw.find("task.spawn(Odtwarzacz.uruchom"))
        self.assertIn("Stale.KOMUNIKATY_ODMOWY.brak_odtwarzacza", zw)
        self.assertLess(zw.find('kontener:SetAttribute("OstatniaOdmowa", nil)'), zw.find("task.spawn(Odtwarzacz.uruchom"))
        self.assertIn('kontener:GetAttributeChangedSignal("OstatniaOdmowa"):Connect', KLIENT)
        self.assertIn("pokazKomunikat(Stale.KOMUNIKATY_ODMOWY[powod] or Stale.KOMUNIKATY_ODMOWY.blad_silnika)", KLIENT)
        # odtwarzacz wpisuje powód do kontenera, z którego ruszyła walka (las), więc dymek lasu ma skąd go wziąć
        self.assertIn('self:atrybut("OstatniaOdmowa", powod)', ODTW)
        # E bez podpowiedzi przy potworze tuż poza bramką → dymek „Podejdź bliżej” (nie przy włączonej podpowiedzi)
        e = KLIENT.split('game:GetService("UserInputService").InputBegan:Connect', 1)[1].split("\nend)\n", 1)[0]
        for k in ("wejscie.KeyCode ~= Enum.KeyCode.E", "podpowiedz.Enabled", "walkaTrwa()", "Stale.ZASIEG_DYMKU_E",
                  "pokazKomunikat(Stale.KOMUNIKATY_ODMOWY.za_daleko)"):
            self.assertIn(k, e, k)


if __name__ == "__main__":
    unittest.main()
