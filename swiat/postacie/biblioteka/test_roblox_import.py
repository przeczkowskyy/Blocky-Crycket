# -*- coding: utf-8 -*-
"""Sprawdzian roblox_import.py bez Studio i bez Open Cloud (niczego nie wgrywa, z niczym się nie łączy).

    python -B swiat/postacie/biblioteka/test_roblox_import.py

Część 1: czyste funkcje — odczyt odpowiedzi open_cloud_invoke, klasy moderacji, decyzje z pliku stanu wgrania,
wybór wolnej nazwy i odszukanie nowego modelu ze spisów „przed” i „po”.
Część 2: cały przebieg main() na UDAWANYM Studio (moduły `studio_mcp` i `roblox_postac` są podmienione w sys.modules,
a STUDIO_MCP_CMD wskazuje nieistniejące polecenie na wypadek, gdyby podmiana zawiodła). Pliki tymczasowe idą do
katalogu tymczasowego systemu i są usuwane. Sprawdza: zapis stanu przed POST, brak drugiego POST przy wznowieniu,
„nie wiadomo” przy przerwanym/nieczytelnym POST, czekanie na moderację (także nieczytelną), wstawienie pod wolną
nazwą, przeniesienie z Workspace, to, że kontrola trafia w nowy model, a nie w starszy o tej samej nazwie ani w cudzą
rzecz dodaną w tej chwili do kontenera, niezatwierdzony folder zgłoszony wyjątkiem MCP, ostrzeżenie o pliku zmienionym
od wgrania i komunikat po nieudanym wstawieniu przy --asset.
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import types

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
os.environ["STUDIO_MCP_CMD"] = "nie-ma-takiego-polecenia-sprawdzian-roblox-import"

from swiat.postacie import roblox_import as ri  # noqa: E402

ZLE = []


def sprawdz(warunek, opis):
    if not warunek:
        ZLE.append(opis)


# ---------------------------------------------------------------- część 1: czyste funkcje

def test_czystych():
    kod, dane = ri.rozbierz_odpowiedz('POST https://apis.roblox.com/assets/v1/assets -> 200 OK\n\n{"operationId": "abc-1", "done": false}')
    sprawdz(kod == 200 and dane == {"operationId": "abc-1", "done": False}, "odczyt 200 + JSON: %r %r" % (kod, dane))
    kod, dane = ri.rozbierz_odpowiedz("GET /assets/v1/operations/x -> 404 Not Found\r\n\r\n{\"code\": \"NOT_FOUND\"}")
    sprawdz(kod == 404 and dane == {"code": "NOT_FOUND"}, "odczyt 404 z CRLF: %r %r" % (kod, dane))
    kod, dane = ri.rozbierz_odpowiedz("cos poszło nie tak")
    sprawdz(kod == 0 and dane is None, "nieczytelna odpowiedź: %r %r" % (kod, dane))
    kod, dane = ri.rozbierz_odpowiedz("POST /x -> 200 OK\n\n[1, 2]")
    sprawdz(kod == 200 and dane is None, "treść niebędąca obiektem")
    kod, dane = ri.rozbierz_odpowiedz('POST /x -> 200 OK\n\n{"a": "-> 500"}')
    sprawdz(kod == 200, "kod nie może pochodzić z treści JSON")
    kod, dane = ri.rozbierz_odpowiedz(None)
    sprawdz(kod == 0 and dane is None, "pusta odpowiedź")

    sprawdz(ri.id_operacji({"operationId": "op-9"}) == "op-9", "operationId")
    sprawdz(ri.id_operacji({"path": "operations/op-7"}) == "op-7", "operacja z path")
    sprawdz(ri.id_operacji({"path": "assets/123"}) == "", "path zasobu to nie operacja")
    sprawdz(ri.id_operacji({"operationId": "../../x y"}) == "", "podejrzany numer operacji")
    sprawdz(ri.id_operacji(None) == "", "operacja z None")
    sprawdz(ri.id_zasobu({"assetId": 123}) == "123" and ri.id_zasobu({"path": "assets/77"}) == "77", "assetId")
    sprawdz(ri.id_zasobu({"assetId": "12a"}) == "", "assetId z literą")

    for stan, klasa in (("Approved", "zatwierdzony"), ("MODERATION_STATE_APPROVED", "zatwierdzony"),
                        ("approved", "zatwierdzony"), ("Rejected", "odrzucony"), ("MODERATION_STATE_REJECTED", "odrzucony"),
                        ("NOT_APPROVED", "odrzucony"), ("Not Approved", "odrzucony"), ("not-approved", "odrzucony"),
                        ("Reviewing", "oczekuje"), ("MODERATION_STATE_REVIEWING", "oczekuje"),
                        ("PENDING", "oczekuje"), ("PendingApproval", "oczekuje"), ("AWAITING_APPROVAL", "oczekuje"),
                        ("Approval pending", "oczekuje"), ("MODERATION_STATE_UNSPECIFIED", "nieznany"), ("", "nieznany"),
                        (None, "nieznany"), ("?", "nieznany")):
        sprawdz(ri.klasa_moderacji(stan) == klasa, "moderacja %r -> %r, a jest %r" % (stan, klasa, ri.klasa_moderacji(stan)))

    wo = ri.wynik_operacji({"done": True, "response": {"assetId": "555", "moderationResult": {"moderationState": "Reviewing"}}})
    sprawdz(wo == {"gotowe": True, "asset": "555", "moderacja": "Reviewing", "blad": None}, "wynik operacji: %r" % wo)
    wo = ri.wynik_operacji({"done": True, "error": {"code": 3}})
    sprawdz(wo["gotowe"] and wo["blad"] and not wo["asset"], "operacja z błędem")
    sprawdz(not ri.wynik_operacji(None)["gotowe"], "operacja z None")

    sprawdz(ri.ocen_wyslanie(200, {"operationId": "o1"}, "x")[:2] == ("operacja", "o1"), "POST 200 z operacją")
    sprawdz(ri.ocen_wyslanie(0, {"operationId": "o1"}, "x")[:2] == ("operacja", "o1"), "operacja przy nieczytelnym kodzie")
    sprawdz(ri.ocen_wyslanie(0, None, "", RuntimeError("timeout"))[0] == "nieznane", "przerwany POST")
    sprawdz(ri.ocen_wyslanie(0, None, "garbage")[0] == "nieznane", "nieczytelny POST")
    sprawdz(ri.ocen_wyslanie(200, {}, "POST -> 200")[0] == "nieznane", "200 bez operacji")
    sprawdz(ri.ocen_wyslanie(503, None, "x")[0] == "nieznane", "5xx")
    sprawdz(ri.ocen_wyslanie(400, {"code": "INVALID_ARGUMENT"}, "x")[0] == "odrzucone_zadanie", "4xx")
    FOLDER = "Path is not in the approved upload directories"
    sprawdz(ri.ocen_wyslanie(0, None, FOLDER, blad=True)[0] == "nie_wyslano", "folder (is_error, bez kodu)")
    sprawdz(ri.ocen_wyslanie(403, None, FOLDER)[0] == "nie_wyslano", "folder przy 4xx")
    sprawdz(ri.ocen_wyslanie(0, None, FOLDER)[0] == "nieznane", "folder bez is_error i bez kodu -> nie wiadomo")
    t = 'POST https://apis.roblox.com/assets/v1/assets (file from approved upload directory) -> 200 OK\n{"operationId": "x"}'
    sprawdz(ri.ocen_wyslanie(*ri.rozbierz_odpowiedz(t), tekst=t, blad=False)[0] == "nieznane",
            "2xx ze słowami „approved/director” nigdy nie znaczy „nie wysłano”")
    sprawdz(ri.ocen_wyslanie(200, None, FOLDER, blad=True)[0] == "nieznane", "2xx + is_error + folder -> nie wiadomo")
    sprawdz(ri.ocen_wyslanie(0, None, "", RuntimeError('MCP tools/call: {"message": "%s"}' % FOLDER))[0] == "nie_wyslano",
            "folder zgłoszony wyjątkiem MCP")
    sprawdz(ri.ocen_wyslanie(0, None, "", RuntimeError("Brak odpowiedzi w 300 s."))[0] == "nieznane", "wyjątek: limit czasu")

    D = ri.decyzja_wgrania
    sprawdz(D(None)[0] == "wgraj", "brak stanu")
    sprawdz(D({"etap": "wysylanie"})[0] == "stop", "wysylanie -> stop")
    sprawdz(D({"etap": "nieznane"})[0] == "stop", "nieznane -> stop")
    sprawdz(D({"etap": "uszkodzony"})[0] == "stop", "uszkodzony -> stop")
    sprawdz(D({"etap": "operacja", "operacja": "o1"})[0] == "wznow_operacje", "operacja -> wznów")
    sprawdz(D({"etap": "nieznane", "operacja": "o1"})[0] == "wznow_operacje", "nieznane z operacją -> wznów")
    sprawdz(D({"etap": "operacja_blad", "operacja": "o1"})[0] == "stop", "błąd operacji -> stop")
    sprawdz(D({"etap": "zasob", "asset": "1", "moderacja": "Reviewing"})[0] == "wznow_zasob", "zasób -> wznów")
    sprawdz(D({"etap": "zasob", "asset": "1", "moderacja": "MODERATION_STATE_REJECTED"})[0] == "stop", "odrzucony -> stop")
    sprawdz(D({"etap": "nie_wyslano"})[0] == "wgraj", "nie wysłano -> wolno")
    sprawdz(D({"etap": "odrzucone_zadanie"})[0] == "wgraj", "4xx -> wolno")
    a, k = D({"etap": "zasob", "asset": "1"}, nowy_mimo=True)
    sprawdz(a == "wgraj" and "KOLEJNY" in k and ri.NOWY_MIMO in k, "nowe wgranie mimo poprzedniego — ostrzeżenie: %r" % k)
    a, k = D({"etap": "wysylanie"})
    sprawdz("Creator Dashboard" in k and "NIE" in k, "komunikat stanu nieznanego: %r" % k)

    sprawdz(ri.wybierz_nazwe("A", ["B"]) == "A", "wolna nazwa")
    sprawdz(ri.wybierz_nazwe("A", ["A", "A #2"]) == "A #3", "kolejny numer")

    K = ri.KONTENER
    przed = {"kontener": [{"n": "A", "k": "Model", "id": "1"}], "workspace": [{"n": K, "k": "Model", "id": "0"}]}
    po = {"kontener": [{"n": "A", "k": "Model", "id": "1"}, {"n": "A", "k": "Model", "id": "2"}],
          "workspace": [{"n": K, "k": "Model", "id": "0"}]}
    w, b = ri.wybierz_nowa(przed, po, {"A #2"})
    sprawdz(w == {"rodzic": "kontener", "n": "A", "k": "Model", "id": "2"} and b is None, "DebugId rozróżnia: %r %r" % (w, b))
    bez = lambda d: {k: [{"n": e["n"], "k": e["k"]} for e in v] for k, v in d.items()}   # noqa: E731
    w, b = ri.wybierz_nowa(bez(przed), bez(po), {"A #2"})
    sprawdz(w is None and "taką samą nazwę" in b, "bez DebugId ta sama nazwa -> stop: %r" % b)
    po2 = {"kontener": [{"n": "A"}, {"n": "A #2"}], "workspace": [{"n": K}]}
    w, b = ri.wybierz_nowa({"kontener": [{"n": "A"}], "workspace": [{"n": K}]}, po2, {"A #2"})
    sprawdz(w and w["n"] == "A #2" and w["id"] == "", "bez DebugId nowa nazwa: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]}, {"kontener": [], "workspace": [{"n": K}, {"n": "A #2"}]}, {"A #2"})
    sprawdz(w and w["rodzic"] == "workspace", "nowy w Workspace o naszej nazwie: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]}, {"kontener": [], "workspace": [{"n": K}, {"n": "Cudzy"}]}, {"A"})
    sprawdz(w is None and "Cudzy" in b, "cudzego nowego obiektu z Workspace nie bierzemy: %r" % b)
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": []}, {"kontener": [{"n": "X"}, {"n": "Y"}], "workspace": []}, {"A"})
    sprawdz(w is None and "Więcej niż jeden" in b, "dwóch kandydatów -> stop: %r" % b)
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": []}, {"kontener": [{"n": "X"}, {"n": "A"}], "workspace": []}, {"A"})
    sprawdz(w and w["n"] == "A", "dwóch kandydatów, jeden o naszej nazwie: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": []}, {"kontener": [{"n": "X"}, {"n": "Y"}], "workspace": []}, {"A"},
                           "Inserted Y into game.Workspace.TestPostaci")
    sprawdz(w and w["n"] == "Y", "podpowiedź z odpowiedzi insert_asset: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [{"n": "A"}], "workspace": []}, {"kontener": [{"n": "A"}], "workspace": []}, {"A"})
    sprawdz(w is None and "nie widać" in b, "nic nowego -> stop: %r" % b)
    # cudza nowa rzecz w kontenerze (Team Create) + nasz import w Workspace (narzędzie pominęło parentPath)
    w, b = ri.wybierz_nowa({"kontener": [{"n": "A"}], "workspace": [{"n": K}]},
                           {"kontener": [{"n": "A"}, {"n": "Cudzy"}], "workspace": [{"n": K}, {"n": "A #2"}]}, {"A #2", "A"})
    sprawdz(w and w["rodzic"] == "workspace" and w["n"] == "A #2", "cudzy w kontenerze, nasz w Workspace: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]},
                           {"kontener": [{"n": "Cudzy"}], "workspace": [{"n": K}, {"n": "A #2"}]}, {"A #2"})
    sprawdz(w and w["n"] == "A #2", "jedyny w kontenerze spoza nazw nie wygrywa z naszym w Workspace: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]},
                           {"kontener": [{"n": "Cudzy"}], "workspace": [{"n": K}, {"n": "Inny"}]}, {"A"})
    sprawdz(w is None and "nieoczekiwaną nazwę" in b, "nieoczekiwana nazwa + inne nowe w Workspace -> stop: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]},
                           {"kontener": [{"n": "Model"}], "workspace": [{"n": K}, {"n": "Inny"}]}, {"A"},
                           "Inserted Model into game.Workspace.TestPostaci")
    sprawdz(w is None and "nieoczekiwaną nazwę" in b,
            "wzmianka w odpowiedzi insert_asset nie wystarcza przy innych nowych w Workspace: %r %r" % (w, b))
    w, b = ri.wybierz_nowa({"kontener": [], "workspace": [{"n": K}]}, {"kontener": [{"n": "Model"}], "workspace": [{"n": K}]}, {"A"})
    sprawdz(w and w["n"] == "Model", "jedyny nowy obiekt, inna nazwa, nic więcej nowego -> bierzemy: %r %r" % (w, b))

    tmp = tempfile.mkdtemp(prefix="test_roblox_import_")
    try:
        p = ri.sciezka_stanu("m", "fbx", tmp)
        sprawdz(ri.wczytaj_stan(p) is None, "brak pliku stanu")
        ri.zapisz_stan(p, {"etap": "wysylanie", "nazwa": "Rycerz ó"})
        sprawdz(ri.wczytaj_stan(p) == {"etap": "wysylanie", "nazwa": "Rycerz ó"}, "zapis i odczyt stanu")
        sprawdz(not os.path.exists(p + ".tmp"), "plik tymczasowy stanu po zapisie")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{nie json")
        sprawdz(ri.wczytaj_stan(p).get("etap") == "uszkodzony", "uszkodzony stan")
        sprawdz(ri.decyzja_wgrania(ri.wczytaj_stan(p))[0] == "stop", "uszkodzony stan -> stop")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- część 2: przebieg na udawanym Studio

class BladStudio(RuntimeError):
    pass


class Udawane:
    """Udawany świat Studio + Open Cloud. `chmura(arg)` -> (tekst, is_error) albo wyjątek BladStudio."""

    def __init__(self, debug_id=True, nazwa_wst="assetName", rodzic_wst="kontener", starsze=(), display=None):
        self._id = 100
        self.debug_id, self.nazwa_wst, self.rodzic_wst, self.display = debug_id, nazwa_wst, rodzic_wst, display
        self.kontener = [self._nowy(n) for n in starsze]
        self.workspace = [self._nowy("Camera", "Camera"), self._nowy(ri.KONTENER)]
        self.chmura = lambda arg: ("", True)
        self.wywolania = []
        self.wejscia = 0
        self.wstaw_blad = False
        self.cudze_przy_wstawieniu = None          # nazwa rzeczy, którą „współpracownik” dodaje do kontenera w tej chwili
        self.kontrolowane, self.naprawiane = [], []

    def _nowy(self, n, k="Model"):
        self._id += 1
        return {"n": n, "k": k, "id": "dbg_%d" % self._id}

    def _spis(self, lista):
        return [dict(n=e["n"], k=e["k"], **({"id": e["id"]} if self.debug_id else {})) for e in lista]

    def _jedyny(self, nazwa):
        z = [e for e in self.kontener if e["n"] == nazwa]
        return z

    def call(self, nazwa, arg=None, timeout=None):
        arg = arg or {}
        self.wywolania.append((nazwa, arg))
        if nazwa == "execute_luau":
            return self._luau(arg["code"])
        if nazwa == "open_cloud_invoke":
            tekst, blad = self.chmura(arg)
            return {"text": tekst, "images": [], "is_error": blad, "raw": None}
        if nazwa == "insert_asset":
            if self.wstaw_blad:
                return {"text": "Failed to insert asset", "images": [], "is_error": True, "raw": None}
            n = arg["assetName"] if self.nazwa_wst == "assetName" else self.display
            e = self._nowy(n)
            e["asset"] = arg["assetId"]
            (self.kontener if self.rodzic_wst == "kontener" else self.workspace).append(e)
            if self.cudze_przy_wstawieniu:
                self.kontener.append(dict(self._nowy(self.cudze_przy_wstawieniu), cudze=True))
            return {"text": "Inserted asset %s" % arg["assetId"], "images": [], "is_error": False, "raw": None}
        if nazwa == "screen_capture":
            return {"text": "", "images": [b"PNG"], "is_error": False, "raw": None}
        raise AssertionError("nieoczekiwane narzędzie %s" % nazwa)

    def _odp(self, w):
        return {"text": json.dumps(w, ensure_ascii=False), "images": [], "is_error": False, "raw": None}

    def _luau(self, kod):
        if "GetUserId" in kod:
            return self._odp({"placeId": ri.PLACE_ID, "creatorType": "Enum.CreatorType.User", "creatorId": 1,
                              "userId": 42, "kontener": True})
        if "-- roblox_import: SPIS" in kod:
            return self._odp({"kontener": self._spis(self.kontener), "workspace": self._spis(self.workspace)})
        if "-- roblox_import: PRZENIES" in kod:
            P = json.loads(json.loads(re.search(r"HS:JSONDecode\((\".*?\")\)\n", kod).group(1)))
            lista = self.kontener if P["rodzic"] == "kontener" else self.workspace
            traf = [e for e in lista if e["n"] == P["n"] and e["k"] == P["k"] and (P["id"] == "" or e["id"] == P["id"])]
            if len(traf) != 1:
                return self._odp({"blad": "pasujących %d" % len(traf)})
            m, kroki = traf[0], []
            if lista is not self.kontener:
                lista.remove(m)
                self.kontener.append(m)
                kroki.append("przeniesiono")
            if m["n"] != P["cel"]:
                m["n"] = P["cel"]
                kroki.append("zmieniono nazwę")
            if len(self._jedyny(P["cel"])) != 1:
                return self._odp({"blad": "duplikat"})
            return self._odp({"kroki": kroki, "nazwa": m["n"], "klasa": m["k"], "sciezka": "Workspace.%s.%s" % (ri.KONTENER, m["n"])})
        if "-- roblox_import: KONTROLA" in kod or "-- roblox_import: NAPRAWA" in kod:
            nazwa = json.loads(re.search(r"if c\.Name == (\".*?\") then", kod).group(1))
            z = self._jedyny(nazwa)
            if len(z) != 1:
                return self._odp({"blad": "instancji: %d" % len(z)})
            if "KONTROLA" in kod:
                self.kontrolowane.append(z[0]["id"])
                return self._odp({"nazwa": nazwa, "klasa": "Model", "klasy": {"MeshPart": 2, "Bone": 3}, "siatki": [],
                                  "wymiary": [2.0, 5.0, 1.0]})
            self.naprawiane.append(z[0]["id"])
            return self._odp({"kroki": ["zakotwiczono części: 2"]})
        raise AssertionError("nieznany kod Luau: %s" % kod[:80])


AKTYWNE = {}


class _Sesja:
    def __enter__(self):
        AKTYWNE["swiat"].wejscia += 1
        return AKTYWNE["swiat"]

    def __exit__(self, *a):
        return False


def _podmien_moduly():
    sm = types.ModuleType("studio_mcp")
    sm.StudioError = BladStudio
    sm.StudioMCP = _Sesja
    sm.first_studio_id = lambda s: "sid-udawane"
    sys.modules["studio_mcp"] = sm
    rp = types.ModuleType("swiat.postacie.roblox_postac")
    rp.ROZMIESZCZENIE = {"testowy": {"poz": [0.0, 0.0], "patrz": [0.0, 1.0]}}
    rp.PRZESUNIECIE = (0.0, 0.0)
    rp.luau = lambda v: json.dumps(v)
    sys.modules["swiat.postacie.roblox_postac"] = rp
    return sm


def uruchom(swiat, *argumenty):
    """main() na udawanym Studio -> (kod wyjścia, wypisane)."""
    assert sys.modules["studio_mcp"].StudioMCP is _Sesja, "podmiana studio_mcp nie działa — przerywam"
    AKTYWNE["swiat"] = swiat
    out = io.StringIO()
    kod = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            ri.main(["--modul", "testowy"] + list(argumenty))
        except SystemExit as e:
            kod = 0 if e.code in (None, 0) else (e.code if isinstance(e.code, int) else 1)
            if isinstance(e.code, str):
                print("[exit] " + e.code)
    return kod, out.getvalue()


def odp(kod, dane):
    """Odpowiedź w formacie open_cloud_invoke: „METHOD url -> 200 OK”, pusta linia, JSON."""
    return "POST https://apis.roblox.com/assets/v1/x -> %d %s\n\n%s" % (kod, "OK" if kod < 400 else "Error", json.dumps(dane))


def ile_post(swiat):
    return sum(1 for n, a in swiat.wywolania if n == "open_cloud_invoke" and a["method"] == "POST")


def test_przebiegu():
    tmp = tempfile.mkdtemp(prefix="test_roblox_import_")
    stare = (ri.WYNIK, ri.STAN_DIR, ri.OPERACJA_MAX, ri.OPERACJA_CO, ri.MODERACJA_MAX, ri.MODERACJA_CO)
    try:
        _podmien_moduly()
        ri.WYNIK = os.path.join(tmp, "wynik")
        ri.STAN_DIR = os.path.join(tmp, "wynik", "_roblox")
        ri.OPERACJA_CO = ri.MODERACJA_CO = 0
        ri.OPERACJA_MAX, ri.MODERACJA_MAX = 5, 5
        os.makedirs(os.path.join(ri.WYNIK, "testowy"))
        with open(os.path.join(ri.WYNIK, "testowy", "testowy.fbx"), "wb") as f:
            f.write(b"FBX" * 100)
        with open(os.path.join(ri.WYNIK, "testowy", "raport.json"), "w", encoding="utf-8") as f:
            json.dump({"modele": [{"rodzaj": "postac", "nazwa": "Testowy", "wymiary_ciala": [2.0, 5.0, 1.0],
                                   "siatki": [1, 2], "kosci": [1, 2, 3], "trojkaty_razem": 10}]}, f)
        plik_stanu = ri.sciezka_stanu("testowy", "fbx")
        NAZWA = "Testowy (import FBX)"

        def stan():
            return ri.wczytaj_stan(plik_stanu)

        def wyczysc():
            if os.path.exists(plik_stanu):
                os.remove(plik_stanu)

        # A) plan bez --tak-wgraj: nic nie wysyła
        s = Udawane()
        kod, out = uruchom(s)
        sprawdz(kod == 0 and ile_post(s) == 0 and stan() is None, "A: plan wysłał coś albo zapisał stan: %s" % out)

        # B) udane wgranie: stan „wysylanie” na dysku PRZED POST, potem operacja -> zasób -> wstawienie
        s = Udawane()
        widziany = {}

        def chmura_b(arg):
            if arg["method"] == "POST":
                widziany["przed_post"] = stan()
                return odp(200, {"path": "operations/op-1", "operationId": "op-1", "done": False}), False
            if "/operations/" in arg["endpoint"]:
                return odp(200, {"done": True, "response": {"assetId": "111", "moderationResult": {"moderationState": "MODERATION_STATE_APPROVED"}}}), False
            raise AssertionError(arg)
        s.chmura = chmura_b
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 0, "B: udane wgranie zakończone kodem %s: %s" % (kod, out))
        sprawdz((widziany.get("przed_post") or {}).get("etap") == "wysylanie", "B: przed POST brak stanu „wysylanie”: %r" % widziany)
        st = stan() or {}
        sprawdz(st.get("etap") == "zasob" and st.get("asset") == "111" and st.get("operacja") == "op-1",
                "B: stan po wgraniu: %r" % st)
        sprawdz([e["n"] for e in s.kontener] == [NAZWA] and s.kontrolowane == [s.kontener[0]["id"]] * 2
                and s.naprawiane == [s.kontener[0]["id"]], "B: kontrola/naprawa nie na nowym modelu")
        sprawdz(os.path.isfile(os.path.join(ri.STAN_DIR, "import_testowy_fbx.json")), "B: brak pliku wyniku")

        # C) ponowne uruchomienie: ZERO POST, wstawienie pod wolną nazwą, kontrola na nowym (nie na starszym)
        s2 = Udawane(starsze=[NAZWA])
        s2.chmura = lambda arg: (_ for _ in ()).throw(AssertionError("C: zapytanie do chmury przy zatwierdzonym zasobie"))
        kod, out = uruchom(s2, "--tak-wgraj")
        nowy = [e for e in s2.kontener if e.get("asset") == "111"]
        sprawdz(kod == 0 and ile_post(s2) == 0, "C: wznowienie z zasobem: kod %s, POST %d: %s" % (kod, ile_post(s2), out))
        sprawdz(len(nowy) == 1 and nowy[0]["n"] == NAZWA + " #2" and set(s2.kontrolowane) == {nowy[0]["id"]},
                "C: nowy model nie dostał wolnej nazwy albo kontrola trafiła w starszy: %r" % s2.kontener)

        # D) POST przerwany (limit czasu): stan „nieznane”, kod != 0; ponowne uruchomienie zatrzymuje się bez Studio
        wyczysc()
        s = Udawane()

        def chmura_timeout(arg):
            raise BladStudio("Brak odpowiedzi z Roblox Studio na „tools/call” w 300 s.")
        s.chmura = chmura_timeout
        kod, out = uruchom(s, "--tak-wgraj")
        st = stan() or {}
        sprawdz(kod != 0 and st.get("etap") == "nieznane" and "300 s" in st.get("odpowiedz", "") and "NIE WIADOMO" in out,
                "D: przerwany POST: kod %s, stan %r, %s" % (kod, st, out))
        s = Udawane()
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and s.wejscia == 0 and "Creator Dashboard" in out, "D: stan nieznany nie zatrzymał przed Studio: %s" % out)
        # świadome drugie wgranie: osobna opcja, ostrzeżenie, poprzedni stan zachowany w „poprzednie”
        s = Udawane()
        s.chmura = chmura_b
        kod, out = uruchom(s, "--tak-wgraj", ri.NOWY_MIMO)
        st = stan() or {}
        sprawdz(kod == 0 and ile_post(s) == 1 and "KOLEJNY" in out and st.get("poprzednie", [{}])[-1].get("etap") == "nieznane",
                "D: %s: kod %s, stan %r" % (ri.NOWY_MIMO, kod, st))
        kod, out = uruchom(Udawane(), ri.NOWY_MIMO)
        sprawdz(kod != 0, "D: %s bez --tak-wgraj powinno być błędem" % ri.NOWY_MIMO)

        # E) POST z nieczytelną odpowiedzią: „nie wiadomo”, surowa odpowiedź w stanie
        wyczysc()
        s = Udawane()
        s.chmura = lambda arg: ("coś dziwnego bez nagłówka", False)
        kod, out = uruchom(s, "--tak-wgraj")
        st = stan() or {}
        sprawdz(kod != 0 and st.get("etap") == "nieznane" and st.get("odpowiedz") == "coś dziwnego bez nagłówka"
                and "Wgranie nie powiodło się" not in out, "E: nieczytelny POST: %r %s" % (st, out))

        # F) operacja nie kończy się: kod != 0, stan „operacja”; potem wznowienie bez POST
        wyczysc()
        ri.OPERACJA_MAX = 0
        s = Udawane()
        s.chmura = lambda arg: (odp(200, {"operationId": "op-2", "done": False}), False)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and (stan() or {}).get("etap") == "operacja" and (stan() or {}).get("operacja") == "op-2",
                "F: niedokończona operacja: %s" % out)
        ri.OPERACJA_MAX = 5
        s = Udawane()

        def chmura_f(arg):
            assert arg["method"] == "GET", "F: drugi POST!"
            if arg["endpoint"].endswith("/operations/op-2"):
                return odp(200, {"done": True, "response": {"assetId": "222", "moderationResult": {"moderationState": "MODERATION_STATE_REVIEWING"}}}), False
            if arg["endpoint"].endswith("/assets/222"):
                return odp(200, {"assetId": "222", "moderationResult": {"moderationState": "MODERATION_STATE_APPROVED"}}), False
            raise AssertionError(arg)
        s.chmura = chmura_f
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 0 and ile_post(s) == 0 and (stan() or {}).get("moderacja") == "MODERATION_STATE_APPROVED"
                and [e.get("asset") for e in s.kontener] == ["222"], "F: wznowienie operacji + moderacja: %s" % out)

        # G) moderacja wciąż trwa: kod != 0, bez wstawiania, numer w stanie
        wyczysc()
        ri.MODERACJA_MAX = 0.01
        s = Udawane()
        s.chmura = lambda arg: (odp(200, {"operationId": "op-3", "done": True, "response": {"assetId": "333", "moderationResult": {"moderationState": "Reviewing"}}}), False)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and not s.kontener and (stan() or {}).get("asset") == "333" and "czeka na moderację" in out,
                "G: moderacja w toku: %s" % out)
        ri.MODERACJA_MAX = 5

        # H) moderacja odrzuciła (forma MODERATION_STATE_REJECTED): bez wstawiania; ponownie -> stop bez Studio
        wyczysc()
        s = Udawane()
        s.chmura = lambda arg: (odp(200, {"operationId": "op-4", "done": True, "response": {"assetId": "444", "moderationResult": {"moderationState": "MODERATION_STATE_REJECTED"}}}), False)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and not s.kontener and "ODRZUCONY" in out, "H: odrzucony: %s" % out)
        s = Udawane()
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and s.wejscia == 0, "H: po odrzuceniu ponowne uruchomienie nie zatrzymało się")

        # I) insert_asset zawodzi: kod != 0, zasób zostaje w stanie; ponownie: bez POST
        wyczysc()
        s = Udawane()
        s.wstaw_blad = True
        s.chmura = chmura_b
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and (stan() or {}).get("asset") == "111" and "NIE wgrywaj" in out, "I: błąd wstawiania: %s" % out)
        s = Udawane()
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 0 and ile_post(s) == 0 and len(s.kontener) == 1, "I: wznowienie po błędzie wstawiania: %s" % out)

        # J) 4xx i niezatwierdzony folder: zasób nie powstał -> wolno ponowić bez dodatkowej opcji
        wyczysc()
        s = Udawane()
        s.chmura = lambda arg: (odp(400, {"code": "INVALID_ARGUMENT"}), True)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and (stan() or {}).get("etap") == "odrzucone_zadanie", "J: 4xx: %s" % out)
        s = Udawane()
        s.chmura = lambda arg: ("Path is not in the approved upload directories", True)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 3 and ile_post(s) == 1 and (stan() or {}).get("etap") == "nie_wyslano", "J: folder: kod %s %s" % (kod, out))

        # K) --asset przy starszym modelu o tej samej nazwie, narzędzie nazywa model po displayName
        wyczysc()
        s = Udawane(starsze=[NAZWA], nazwa_wst="display", display=NAZWA, debug_id=False)
        kod, out = uruchom(s, "--asset", "999")
        sprawdz(kod != 0 and not s.kontrolowane, "K: bez DebugId dwa modele o tej samej nazwie -> musi stanąć: %s" % out)
        s = Udawane(starsze=[NAZWA], nazwa_wst="display", display=NAZWA, debug_id=True)
        kod, out = uruchom(s, "--asset", "999")
        nowy = [e for e in s.kontener if e.get("asset") == "999"]
        sprawdz(kod == 0 and len(nowy) == 1 and nowy[0]["n"] == NAZWA + " #2" and s.kontener[0]["n"] == NAZWA
                and set(s.kontrolowane) == {nowy[0]["id"]} and set(s.naprawiane) == {nowy[0]["id"]},
                "K: z DebugId nowy model przemianowany, starszy nietknięty: %r %s" % (s.kontener, out))

        # L) narzędzie zignorowało parentPath: model w Workspace -> przeniesiony do kontenera
        s = Udawane(rodzic_wst="workspace")
        kod, out = uruchom(s, "--asset", "999")
        sprawdz(kod == 0 and [e["n"] for e in s.kontener] == [NAZWA] and set(s.kontrolowane) == {s.kontener[0]["id"]},
                "L: przeniesienie z Workspace: %r %s" % (s.kontener, out))
        sprawdz(stan() is None, "L: --asset nie powinno zapisywać stanu wgrania")

        # M) narzędzie pominęło parentPath, a współpracownik w tej samej chwili dodał coś do kontenera:
        #    cudzej rzeczy nie ruszamy, import z Workspace trafia do kontenera
        s = Udawane(rodzic_wst="workspace")
        s.cudze_przy_wstawieniu = "Cudza postać"
        kod, out = uruchom(s, "--asset", "999")
        cudze = [e for e in s.kontener if e.get("cudze")]
        nasz = [e for e in s.kontener if e.get("asset") == "999"]
        sprawdz(kod == 0 and len(cudze) == 1 and cudze[0]["n"] == "Cudza postać" and cudze[0]["id"] not in s.kontrolowane
                and cudze[0]["id"] not in s.naprawiane and len(nasz) == 1 and nasz[0]["n"] == NAZWA
                and set(s.kontrolowane) == {nasz[0]["id"]}, "M: cudza rzecz w kontenerze: %r %s" % (s.kontener, out))

        # N) insert_asset zawodzi przy --asset: komunikat każe powtórzyć --asset, nie --tak-wgraj
        s = Udawane()
        s.wstaw_blad = True
        kod, out = uruchom(s, "--asset", "777")
        sprawdz(kod != 0 and "--asset 777" in out and "polecenie z --tak-wgraj" not in out and ile_post(s) == 0,
                "N: komunikat po błędzie wstawiania przy --asset: %s" % out)

        # O) niezatwierdzony folder zgłoszony WYJĄTKIEM MCP: „nie wysłano” (kod 3), potem wolno ponowić bez opcji
        wyczysc()
        s = Udawane()

        def chmura_folder(arg):
            raise BladStudio('MCP tools/call: {"message": "Path is not in the approved upload directories"}')
        s.chmura = chmura_folder
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 3 and (stan() or {}).get("etap") == "nie_wyslano", "O: folder jako wyjątek: kod %s %s" % (kod, out))
        s = Udawane()
        s.chmura = chmura_b
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 0 and ile_post(s) == 1, "O: po zatwierdzeniu folderu ponowne wgranie: kod %s %s" % (kod, out))

        # P) zmieniony plik po udanym wgraniu: ostrzeżenie mówi, że to stara wersja i jak wgrać nową
        with open(os.path.join(ri.WYNIK, "testowy", "testowy.fbx"), "wb") as f:
            f.write(b"FBX2" * 100)
        s = Udawane()
        s.chmura = lambda arg: (_ for _ in ()).throw(AssertionError("P: zapytanie do chmury"))
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod == 0 and ile_post(s) == 0 and "STARĄ" in out and ri.NOWY_MIMO in out and "KOLEJNY" in out,
                "P: zmieniony plik: %s" % out)
        kod, out = uruchom(Udawane())
        sprawdz(kod == 0 and "STARĄ" in out, "P: ostrzeżenie o zmienionym pliku także w planie: %s" % out)

        # Q) stanu moderacji nie da się odczytać: kod != 0, komunikat wskazuje --asset, bez obietnicy wstawienia
        wyczysc()
        ri.MODERACJA_MAX = 0.01
        s = Udawane()
        s.chmura = lambda arg: (odp(200, {"operationId": "op-5", "done": True, "response": {"assetId": "555"}}), False)
        kod, out = uruchom(s, "--tak-wgraj")
        sprawdz(kod != 0 and not s.kontener and "--asset 555" in out and "nie da się odczytać" in out
                and "od razu go wstawi" not in out and (stan() or {}).get("asset") == "555", "Q: moderacja nieznana: %s" % out)
        ri.MODERACJA_MAX = 5
    finally:
        (ri.WYNIK, ri.STAN_DIR, ri.OPERACJA_MAX, ri.OPERACJA_CO, ri.MODERACJA_MAX, ri.MODERACJA_CO) = stare
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_czystych()
    n1 = len(ZLE)
    print("czyste funkcje:", "zgodne" if not n1 else "%d niezgodności" % n1)
    test_przebiegu()
    print("przebieg na udawanym Studio:", "zgodny" if len(ZLE) == n1 else "%d niezgodności" % (len(ZLE) - n1))
    for z in ZLE:
        print("  -", z)
    print("WYNIK:", "ZGODNE" if not ZLE else "NIEZGODNE")
    sys.exit(0 if not ZLE else 1)
