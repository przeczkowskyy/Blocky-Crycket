# -*- coding: utf-8 -*-
"""EKWIPUNEK BOHATERÓW — wspólny kod „ciało bazowe + zakładany ekwipunek” (D-071, kontrakt swiat/postacie/EKWIPUNEK.md).

Nic tu nie zależy od konkretnego bohatera. Korzystają z tego rycerz.py, kot_mag.py i zwiadowca.py (każdy moduł
bohatera ma własne ciało, przedmioty, klipy i stroje); kod przeniesiony 1:1 z sekcji „ekwipunek: wspólne” dawnego
rycerz.py (15.11), bez zmiany zachowania i nazw:
  Przedmiot          przedmiot widoczny na postaci: segmenty kostne (sztywne akcesoria w układzie ŚRODKA KLOCKA kości,
                     zakrywa=True — powłoka) i segmenty na zaczepie (broń, kapelusz kota); opis() — wpis danych dla gry
                     (EKWIPUNEK.md pkt 5), ikona() — cały przedmiot jako jedno akcesorium do ikony;
  ubierz()           kopia ciała z założonymi przedmiotami (klipy ciała bez zmian);
  kopiuj_klipy()     klipy postaci odniesienia na inną postać (kanały = deepcopy);
  zaczep_ekwipunku() nazwa zaczepu segmentu kostnego: Ekw<Kosc>Attachment;
  SKROTY_KOSCI       kość R15 -> skrót w id segmentu (<przedmiot>_<skrót>), ZACZEPY_CHWYTU — zaczepy broni w dłoni.
Moduł biblioteczny, bez uruchamiania wprost (testy: --kontrola w modułach bohaterów).
"""
import copy
import re

from swiat.postacie.biblioteka.postac import I3, Akcesorium

SKROTY_KOSCI = {"Head": "glowa", "UpperTorso": "tulow", "LowerTorso": "biodra",
                "LeftUpperArm": "ramie_l", "RightUpperArm": "ramie_p", "LeftLowerArm": "przedramie_l",
                "RightLowerArm": "przedramie_p", "LeftHand": "dlon_l", "RightHand": "dlon_p",
                "LeftUpperLeg": "udo_l", "RightUpperLeg": "udo_p", "LeftLowerLeg": "golen_l", "RightLowerLeg": "golen_p",
                "LeftFoot": "stopa_l", "RightFoot": "stopa_p"}
_ID_OK = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ZACZEPY_CHWYTU = ("RightGripAttachment", "LeftGripAttachment")


def zaczep_ekwipunku(kosc):
    """Nazwa zaczepu segmentu kostnego: Ekw<Kosc>Attachment (środek klocka kości, obrót 0)."""
    return "Ekw%sAttachment" % kosc


class Przedmiot:
    """Przedmiot ekwipunku widoczny na postaci: lista segmentów. Segment kostny = sztywne Akcesorium modelowane
    w układzie ŚRODKA KLOCKA swojej kości (jak `with p.na(kosc, od="srodek")`); zakrywa=True — powłoka: zdejmuje
    gołe bryły tej kości. Segment na zaczepie = zwykłe akcesorium (broń) zakładane przez Postac.zaloz.
    miara = postać z klockami ciała (wymiary i środki kości)."""

    def __init__(self, id, nazwa, slot, kategoria, miara, cialo="czlowiek", klasy=(), czesc_od=None, ukrywa=(),
                 zestaw=None, paleta=None):
        if not _ID_OK.match(id) or "__" in id:
            raise ValueError("Id przedmiotu %r: litery ASCII, cyfry i „_” (bez „__”)" % id)
        self.id, self.nazwa, self.slot, self.kategoria = id, nazwa, slot, kategoria
        self.miara, self.cialo, self.klasy = miara, cialo, tuple(klasy)
        self.czesc_od, self.ukrywa, self.zestaw = czesc_od, tuple(ukrywa), zestaw
        self.paleta = paleta
        self.segmenty = []

    def segment(self, kosc, zakrywa=False, klocek=None):
        """Nowy segment na kości (Akcesorium w układzie środka klocka). klocek = kolor — powłoka zaczyna się od
        bryły o rozmiarze klocka kości (nazwa bryły = nazwa kości, jak Postac.klocek)."""
        if kosc not in SKROTY_KOSCI:
            raise ValueError("Przedmiot %s: nieznana kość %r" % (self.id, kosc))
        a = Akcesorium("%s_%s" % (self.id, SKROTY_KOSCI[kosc]), "%s (%s)" % (self.nazwa, SKROTY_KOSCI[kosc]),
                       zaczep=zaczep_ekwipunku(kosc), typ="Inne", paleta=self.paleta, przymierz=False)
        if klocek is not None:
            a.blok(kosc, (0, 0, 0), self.miara.wymiary(kosc), klocek, "zwykly")
        self.segmenty.append({"akc": a, "kosc": kosc, "zakrywa": bool(zakrywa), "zaczep": None,
                              "pos": (0.0, 0.0, 0.0), "obrot": (0.0, 0.0, 0.0)})
        return a

    def na_zaczepie(self, akc, zaczep=None, pos=(0, 0, 0), obrot=(0, 0, 0)):
        """Segment = gotowe akcesorium na punkcie zaczepienia (broń, kapelusz kota)."""
        self.segmenty.append({"akc": akc, "kosc": None, "zakrywa": False, "zaczep": zaczep or akc.zaczep,
                              "pos": tuple(pos), "obrot": tuple(obrot)})
        return akc

    def opis(self, korekty=None):
        """Wpis danych przedmiotu (EKWIPUNEK.md pkt 5; pliki, trójkąty i ikonę dopisuje przebuduj.py)."""
        czesci = []
        for s in self.segmenty:
            if s["kosc"]:
                czesci.append({"id": s["akc"].id, "kosc": s["kosc"], "zakrywa": s["zakrywa"],
                               "zaczep": zaczep_ekwipunku(s["kosc"]), "pos": [0, 0, 0], "rot": [0, 0, 0]})
            else:
                z, pos, obrot = (korekty or {}).get(s["zaczep"], (s["zaczep"], s["pos"], s["obrot"]))
                czesci.append({"id": s["akc"].id, "kosc": self.miara.zaczepy[z]["kosc"], "zakrywa": False,
                               "zaczep": z, "pos": [round(v, 4) for v in pos], "rot": [round(v, 3) for v in obrot]})
        # broń trzymana w dłoni (same segmenty na zaczepach chwytu) pasuje do każdego ciała (EKWIPUNEK.md pkt 1)
        w_dloni = all(s["kosc"] is None and s["zaczep"] in ZACZEPY_CHWYTU for s in self.segmenty)
        return {"id": self.id, "nazwa": self.nazwa, "slot": self.slot, "kategoria": self.kategoria,
                "cialo": "dowolne" if w_dloni else self.cialo, "klasy": list(self.klasy), "czesc_od": self.czesc_od,
                "ukrywa": list(self.ukrywa), "zestaw": self.zestaw, "czesci": czesci}

    def ikona(self):
        """Cały przedmiot jako jedno akcesorium do ikony (segmenty w pozie spoczynku, w układzie modelu);
        przedmiot z jednym segmentem na zaczepie — samo to akcesorium."""
        if len(self.segmenty) == 1 and self.segmenty[0]["kosc"] is None:
            return self.segmenty[0]["akc"]
        a = Akcesorium(self.id, self.nazwa, zaczep=zaczep_ekwipunku(self.segmenty[0]["kosc"] or "Ikona"), typ="Inne",
                       paleta=self.paleta, przymierz=False)
        # para rękawic: na postaci dłonie są ok. 3 studa od siebie, w ikonie wychodziły maleńkie — tylko w ikonie
        # kładziemy je obok siebie (odstęp 0,2 studa); dane segmentów i ubieranie bez zmian
        para_dloni = {s["kosc"] for s in self.segmenty} == {"LeftHand", "RightHand"}
        for s in self.segmenty:
            if s["kosc"]:
                st, sr = self.miara.staw(s["kosc"]), self.miara.srodek(s["kosc"])
                t0 = [st[i] + sr[i] for i in range(3)]
                if para_dloni:
                    t0[0] = (1 if t0[0] > 0 else -1) * (self.miara.wymiary(s["kosc"])[0] / 2 + 0.1)
                a.czesci.extend(Akcesorium._czesc_w(c, I3, tuple(t0)) for c in s["akc"].czesci)
        return a


def ubierz(cialo, przedmioty, id=None, nazwa=None, korekty=None):
    """Kopia ciała z założonymi przedmiotami (klipy ciała zostają bez zmian):
    1. hełm (ukrywa) zdejmuje akcesoria ciała o tym znaczniku (włosy);
    2. segment z zakrywa=True zdejmuje gołe bryły swojej kości (najwyżej jedna powłoka na kość — inaczej ValueError);
    3. bryły segmentów kostnych są wtapiane do brył kości (te same siatki <Kosc>_Geo co w dawnym modelu);
    4. segment na zaczepie — Postac.zaloz(..., eksport=False) z korektą chwytu bohatera (korekty = {zaczep:
       (zaczep, pos, obrot)});
    5. kasuje pamięć podręczną geometrii (_bryly, _pkt)."""
    p = copy.deepcopy(cialo)
    if id is not None:
        if not _ID_OK.match(id):
            raise ValueError("Id postaci %r: tylko ASCII" % id)
        p.id = id
    if nazwa is not None:
        p.nazwa = nazwa
    typ_ciala = getattr(p, "typ_ciala", None)
    wlasciciel = {}
    for prz in przedmioty:
        for s in prz.segmenty:
            if s["kosc"] and prz.cialo != typ_ciala:
                raise ValueError("Przedmiot %s jest dla ciała %r, a postać %s ma ciało %r"
                                 % (prz.id, prz.cialo, p.id, typ_ciala))
            if s["zakrywa"]:
                if s["kosc"] in wlasciciel:
                    raise ValueError("Dwie powłoki na kości %s: %s i %s" % (s["kosc"], wlasciciel[s["kosc"]], prz.id))
                wlasciciel[s["kosc"]] = prz.id
    ukryj = {u for prz in przedmioty for u in prz.ukrywa}
    p.zalozone = [z for z in p.zalozone if getattr(z[0], "znacznik", None) not in ukryj]
    p.czesci = [c for c in p.czesci if not (c.get("golas") and c["kosc"] in wlasciciel)]
    for prz in przedmioty:
        for s in prz.segmenty:
            if s["kosc"]:
                sr = p.srodek(s["kosc"])
                for c in s["akc"].czesci:
                    d = dict(c)
                    d["kosc"] = s["kosc"]
                    d["p"] = (sr[0] + c["p"][0], sr[1] + c["p"][1], sr[2] + c["p"][2])
                    p.czesci.append(d)
            else:
                z, pos, obrot = (korekty or {}).get(s["zaczep"], (s["zaczep"], s["pos"], s["obrot"]))
                p.zaloz(s["akc"], z, pos, obrot, eksport=False)
    p._bryly = None
    p._pkt = None
    p.przedmioty = [prz.id for prz in przedmioty]
    return p


def kopiuj_klipy(zrodlo, cel):
    """Klipy źródła na postać `cel` (nowe obiekty Klip, kanały = deepcopy, ta sama kolejność) i poza renderu."""
    for k in zrodlo.klipy:
        n = cel.klip(k.nazwa, k.dlugosc, k.fps, k.petla, k.probki)
        n.kanaly = copy.deepcopy(k.kanaly)
    cel.poza_renderu = zrodlo.poza_renderu
    return cel
