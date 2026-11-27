# -*- coding: utf-8 -*-
"""Próba zapisu postępu w Roblox Studio (D-110, 19.11.2026) — na MAGAZYNIE PRÓBY, nigdy na prawdziwym zapisie człowieka.

    python -B swiat/stan_gracza/testy/proba_zapisu.py <folder wyników POZA repo> [--studio <id>] [--bez-z00]
    python -B swiat/stan_gracza/testy/proba_zapisu.py --sprawdz      # bez Studio: parsuje każdy kawałek Luau (luau_mini)

Jak to działa: Play idzie przez tools/studio_mcp.py → tools/zapis_prob.py (znacznik próby). Przed Play próba ustawia
w trybie Edit ZapisProbaMagazyn = true (kod_magazynu) — serwer stanu pracuje wtedy na magazynie
BC_StanGracza_v1_Studio_Proba; po Stop znaczniki zdejmuje zapis_prob. Rekord próby jest kasowany na początku i na końcu
(zbuduj.kod_zapisu(..., proba=True)). Prawdziwego magazynu Studio próba nie otwiera.
Warunki (tryb Edit): zbudowane StanGracza, KowalProba, SklepProba, StrojeProba, PetyProba, TreningProba, LasPasGra,
CutscenkaBiomu (każdy pakiet: zbuduj.py; po zmianach 19.11 co najmniej --skrypty stanu, kowala, petów i treningu).
Wyniki (wyniki.json, lista.txt) — z nazwą konta i identyfikatorem gracza — idą do podanego folderu poza repo.

LISTA KONTROLNA (OK / BŁĄD / ?):
  Z00 zwykła próba gry (bez magazynu próby): ZapisStan „wyłączony (próba gry)”, ZapisAktywny false, gracz bez wczytywania
  Z01 Play 1 (magazyn próby, rekord skasowany): ZapisStan „włączony (magazyn próby)”, ZapisMagazyn …_Studio_Proba,
      StanGraczaZapis „aktywny”, LicznikWczytan 1, nowy gracz: poziom 1, Złoto 0, Gemy = D.zapis.start
  Z02 gra: klasa (ChooseClass), łup z walki haczykiem „przyznaj” (awans), „+” ×2, kupno w sklepie, ulepszenie u kowala,
      przymierzalnia (zdjęty slot), jajko peta, mini-gra Siły (autogra), Strażnik (łup strażnika + brama), przelot (oznacz),
      sklep trenera (27.11.2026: przy trenerze ulepszenie Siły i wzmacniacz Siły zdalnym zdarzeniem TreningAFK →
      w profilu pakiety.TreningAFK = { u = { Sila = 1 }, w = { Strength = koniec } }; Z04 porównuje całe pakiety)
  Z03 Stop → rekord w magazynie próby: poziom, Złoto, Gemy i klasa jak przed Stop
  Z04 Play 2: wszystko wróciło co do wartości (atrybuty gracza, profil: pakiety kowala i treningu, pety, punkty,
      strażnicy…); czas wczytania (StanGraczaWczytanieMs)
  Z05 błąd usługi przy zapisie wyjścia (2 wywołania padają) → ponowienie w BindToClose, rekord ma nowe Złoto
  Z06 Play 3 z usługą padającą cały czas → „bez_zapisu”, gra w pamięci (łup dochodzi), po Stop rekord NIETKNIĘTY
  Z07 sprzątanie: rekord próby skasowany, znaczniki zdjęte
  Z08 konsola: bez błędów skryptów (StanGracza, KowalProba, PetyProba, TreningProba, StrojeProba, SklepProba)
"""
import json
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "swiat", "test_walki_roblox"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "tools"), PAKIET):  # PAKIET na początku: jego dane.py i zbuduj.py przed innymi o tej nazwie
    if _s in sys.path:
        sys.path.remove(_s)
    sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import zbuduj as ZB  # noqa: E402
import zapis_prob as ZP  # noqa: E402

D = DANE.aktualny()[1]
G = D["zapis"]
MAGAZYN_PROBY = G["magazyn"] + G["przyrostek_studio"] + G["proba"]["przyrostek"]
KLASA = "Warrior"          # Class Pawła
KLASA_STROJU = "wojownik"  # klasa przymierzalni i kowala
JAJKO = "jajko_lesne"
# atrybuty gracza, które MUSZĄ wrócić (reszta różnic idzie do wyników jako informacja)
TRWALE = ["Level", "XP", "XPMax", "Gold", "Gems", "Class", "PunktyDoRozdania", "Strength", "Constitution", "Intelligence",
          "Dexterity", "Luck", "Armor", "ShardyEwolucji", "PetAktywny", "PetyLiczba"]
TRWALE_PRZEDROSTKI = ["TokenyKrainy_", "StrojProba_", "WidzialPrzelot", "PokonalStraznika", "Kowal", "Trening"]
ULOTNE = {"TreningGra", "TreningSeria", "BlokadaWalki"}
POLA_PROFILU = ["poziom", "xp", "zloto", "gemy", "idKlasy", "wytrenowane", "punkty", "pety", "wydatki", "straznicy",
                "pakiety", "tokeny", "shardy", "walki", "awanse"]

H = 'local H = game:GetService("HttpService") '
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
KS = 'local s = workspace:FindFirstChild("StanGracza") '
KOD = {
    "edit": H + ('local o = {} for _, n in { "StanGracza", "KowalProba", "SklepProba", "StrojeProba", "PetyProba", '
                 '"TreningProba", "LasPasGra", "CutscenkaBiomu" } do local k = workspace:FindFirstChild(n) '
                 'o[n] = k ~= nil and k:GetAttribute("Wygenerowane") == true end '
                 'local s = workspace:FindFirstChild("StanGracza") o.ZapisPostepu = s and s:GetAttribute("ZapisPostepu") '
                 'local t = workspace:FindFirstChild("TreningProba") o.MiniGry = if t then t:GetAttribute("MiniGry") ~= false else false '
                 'return H:JSONEncode(o)'),
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "wczytany": H + GR + KS + ('if not gracz or not s then return H:JSONEncode({ brak = true }) end '
                               'return H:JSONEncode({ w = gracz:GetAttribute("StanGraczaWczytany"), z = gracz:GetAttribute("StanGraczaZapis"), '
                               'ms = gracz:GetAttribute("StanGraczaWczytanieMs"), gotowy = s:GetAttribute("SerwerStanuGotowy") })'),
    "migawka": H + GR + KS + (
        'if not gracz or not s then return H:JSONEncode({ brak = true }) end '
        'local A = {} for n, v in gracz:GetAttributes() do local t = type(v) '
        'if t == "number" or t == "string" or t == "boolean" then A[n] = v end end '
        'local K = {} for _, n in { "ZapisAktywny", "ZapisStan", "ZapisMagazyn", "LicznikWczytan", "LicznikZapisow", '
        '"LicznikBledowZapisu", "LicznikBezZapisu", "OstatniZapis", "ZapisProbaBledy" } do K[n] = s:GetAttribute(n) end '
        'local P = {} local ok, p = pcall(function() return s.Sygnaly.SterowanieSerwera:Invoke("stan", gracz) end) '
        'if ok and type(p) == "table" then for _, n in { %s } do P[n] = p[n] end end '
        'return H:JSONEncode({ a = A, k = K, p = P })'),
    "klasa": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"',
    "przyznaj": H + GR + KS + ('local w = s.Sygnaly.SterowanieSerwera:Invoke("przyznaj", gracz, { zloto = %d, doswiadczenie = %d }) '
                               'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, powod = type(w) == "table" and w.powod or false })'),
    "plus": 'game:GetService("ReplicatedStorage"):WaitForChild("AddStatPoint"):FireServer("%s") return "ok"',
    "sklep": H + GR + (
        'local sk = workspace.KowalProba.Sygnaly.Sklep local of = sk:Invoke("oferta", gracz) '
        'local lista = {} for _, o in (of and of.oferta) or {} do if o.stan == "kup" and o.stopien ~= "start" then table.insert(lista, o) end end '
        'table.sort(lista, function(a, b) return a.cena < b.cena end) '
        'for _, o in lista do local w = sk:Invoke("kup", gracz, o.id) if type(w) == "table" and w.ok then '
        'return H:JSONEncode({ ok = true, id = o.id, slot = o.slot, cena = o.cena, stopien = o.stopien, nazwa = o.nazwa, zalozony = w.zalozony == true }) end end '
        'return H:JSONEncode({ ok = false, ofert = #lista })'),
    "do_kowala": GR + ('local k = workspace.KowalProba k.Sygnaly.SterowanieSerwera:Invoke("materialy", gracz, 50) '
                       'local e = require(k.Moduly.DaneKowala).kuznia.e '
                       'gracz.Character:PivotTo(CFrame.new(e[1] + 1, e[2] + 3, e[3] + 1)) return "ok"'),
    "ulepsz": H + ('local w = workspace.KowalProba.Zdalne.Kuznia:InvokeServer("ulepsz", "%s") '
                   'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, powod = type(w) == "table" and w.powod or false })'),
    "stroj": H + ('local w = workspace.StrojeProba.Zdalne.ZmienStroj:InvokeServer("zdejmij", "%s", "%s") '
                  'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, powod = type(w) == "table" and w.powod or false, '
                  'stroj = type(w) == "table" and w.stroj or false })'),
    "pet": H + GR + ('local w = workspace.PetyProba.Sygnaly.SterowanieSerwera:Invoke("kup", gracz, "%s") '
                     'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, pet = type(w) == "table" and w.pet or false, '
                     'powod = type(w) == "table" and w.powod or false })'),
    "trening_wejdz": H + GR + ('local t = workspace.TreningProba local w = t.Sygnaly.SterowanieSerwera:Invoke("wejdz", "sila", gracz) '
                               'local R = require(t.Moduly.DaneTreningu).runda '
                               'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, dlugosc = R.dlugosc_s, odliczanie = R.odliczanie_s })'),
    "trening_klient": 'workspace.TreningProba.Sygnaly.SterowanieKlienta:Invoke("%s", %s) return "ok"',
    "trening_wyjdz": GR + 'workspace.TreningProba.Sygnaly.SterowanieSerwera:Invoke("wyjdz", gracz) return "ok"',
    "straznik": H + GR + KS + (
        'local w = s.Sygnaly.PrzyznajLup:Invoke(gracz, { lup = { zloto = 50, doswiadczenie = 10 }, wynik = "wygrana", czas = 0, '
        'zrodlo = "LasPasGra", gatunek = "%sgaju", poziom = 10 }) s.Sygnaly.SterowanieSerwera:Invoke("publikuj", gracz) '
        'local las = workspace:FindFirstChild("LasPasGra") local ev = las and las.Sygnaly:FindFirstChild("WynikWalki") '
        'if ev then ev:Fire(gracz, { straznik = true, wynik = "wygrana" }) end '
        'return H:JSONEncode({ ok = type(w) == "table" and w.ok == true, powod = type(w) == "table" and w.powod or false, brama = ev ~= nil })'),
    "przelot": GR + ('local c = workspace:FindFirstChild("CutscenkaBiomu") '
                     'if not c then return "brak" end c.Sygnaly.SterowanieCutscenki:Invoke("oznacz", gracz, "las") '
                     'return tostring(gracz:GetAttribute("WidzialPrzelotLasu"))'),
    # stan oferty sklepu dla jednego przedmiotu (zalozone / masz / kup…) i inny założony slot (przymierzalnia)
    "oferta": H + GR + ('local of = workspace.KowalProba.Sygnaly.Sklep:Invoke("oferta", gracz) local w = { inny = false } '
                        'for _, o in (of and of.oferta) or {} do if o.id == "%s" then w.stan = o.stan w.ulepszenie = o.ulepszenie '
                        'elseif o.stan == "zalozone" and o.slot ~= "%s" and not w.inny then w.inny = o.slot end end '
                        'return H:JSONEncode(w)'),
    "bledy": KS + 's:SetAttribute("%s", %d) return "ok"',
    # sklep trenera (27.11.2026): postać przed trenerem (punkt E bazaru), zakupy zdalnym zdarzeniem jak z okna trenera
    "do_trenera": GR + ('local e = workspace.MiasteczkoBazarGra.Punkty:FindFirstChild("E training_center") '
                        'gracz.Character:PivotTo(CFrame.new(e.Position.X, 3.6, e.Position.Z + 3)) return "ok"'),
    "sklep_trenera": H + ('local Z = game:GetService("ReplicatedStorage"):WaitForChild("TreningAFK") '
                          'Z:FireServer("kup", "ulepszenie", "Sila") task.wait(0.7) Z:FireServer("kup", "wzmacniacz", "Sila") '
                          'task.wait(1.0) return H:JSONEncode({ ok = true })'),
    # strój, w który klient ubiera bohatera walki (Ubieranie przymierzalni — ten sam kod co aktor walki)
    "stroj_klienta": H + ('local U = require(workspace.StrojeProba.Moduly.Ubieranie) '
                          'return H:JSONEncode(U.strojGracza(game:GetService("Players").LocalPlayer, "%s") or {})'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy kawałek Luau (po podstawieniu zer) i kod z zapis_prob / zbuduj parsuje się w luau_mini."""
    import luau_mini as LM
    kody = {n: re.sub(r"%[sd]", "0", k) for n, k in KOD.items()}
    kody.update({"zp_start": ZP.LUAU_START, "zp_koniec": ZP.LUAU_KONIEC, "zp_stan": ZP.LUAU_STAN, "zp_po": ZP.LUAU_PO_STARCIE,
                 "zp_magazyn": ZP.kod_magazynu(2), "zapis_proby": ZB.kod_zapisu(D, kasuj=True, proba=True)})
    bledy = []
    for nazwa, kod in kody.items():
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(kody), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def porownaj(przed, po):
    """→ (różnice w trwałych atrybutach i profilu, inne różnice atrybutów)."""
    zle, inne = [], []
    a1, a2 = przed.get("a", {}), po.get("a", {})
    for n in sorted(set(a1) | set(a2)):
        if n.startswith("StanGracza") or n in ULOTNE:
            continue
        if a1.get(n) != a2.get(n):
            trwaly = n in TRWALE or any(n.startswith(p) for p in TRWALE_PRZEDROSTKI)
            (zle if trwaly else inne).append("%s: %r → %r" % (n, a1.get(n), a2.get(n)))
    for n in POLA_PROFILU:
        if json.dumps(przed.get("p", {}).get(n), sort_keys=True) != json.dumps(po.get("p", {}).get(n), sort_keys=True):
            zle.append("profil.%s: %s → %s" % (n, json.dumps(przed.get("p", {}).get(n))[:200],
                                                json.dumps(po.get("p", {}).get(n))[:200]))
    return zle, inne


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium (wyniki mają nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    os.makedirs(wyj, exist_ok=True)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False

    WYNIKI, LISTA = {}, []

    def zapisz(k, v):
        WYNIKI[k] = v
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(5)

        def js(kod, dm="Server"):
            w = json.loads(luau(kod, dm))
            return {} if w == [] else w

        def tryb():
            return call("get_studio_state")["text"]

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                try:
                    w = warunek()
                except Exception:  # noqa: BLE001
                    w = None
                if w:
                    return w
                time.sleep(co)
            return None

        def rekord_proby(kasuj=False):
            return luau(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(ZB.MIEJSCE)) + ZB.kod_zapisu(D, kasuj=kasuj, proba=True), "Edit")

        def rekord_po_stop(limit=45):
            """Rekord po Stop: zapis wyjścia (BindToClose, z ponowieniami) kończy się już po powrocie Studio do Edit —
            czekamy, aż zwolni sesję. Odczyt co 5 s (GetAsync trzyma wynik 4 s w pamięci podręcznej)."""
            t0, r = time.time(), ""
            while time.time() - t0 < limit:
                r = rekord_proby()
                if "świeża sesja" not in r:
                    return r
                time.sleep(5)
            return r

        def play(magazyn, bledy=None):
            """Edit → (znacznik magazynu próby) → Play (znacznik próby stawia zapis_prob) → gracz wczytany."""
            if magazyn:
                w = luau(ZP.kod_magazynu(bledy), "Edit")
                if w != "OK":
                    sys.exit("STOP: nie ustawiłem magazynu próby (%s)" % w)
            log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
            czekaj_na(lambda: "Client" in tryb() and luau(KOD["gotowy_klient"], "Client") == "true", 90, 1.0)
            return czekaj_na(lambda: (lambda w: w if w.get("gotowy") and w.get("w") is not False else None)(
                js(KOD["wczytany"])), 90, 0.5) or {}

        def stop():
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            czekaj_na(lambda: "Current Studio Mode: Edit" in tryb(), 60, 1.0)
            time.sleep(1.0)

        def migawka():
            return js(KOD["migawka"] % ", ".join('"%s"' % n for n in POLA_PROFILU))

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in tryb():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = js(KOD["edit"], "Edit")
        zapisz("edit", edit)
        if not edit.get("StanGracza"):
            sys.exit("STOP: brak Workspace/StanGracza — zbuduj.py")
        log("kontenery:", edit)
        zapisz("rekord_na_start", rekord_proby(kasuj=True))

        # ============================================================ Z00 zwykła próba gry
        if "--bez-z00" not in argv:
            w = play(magazyn=False)
            m = migawka()
            k = m.get("k", {})
            punkt("Z00", k.get("ZapisAktywny") is False and k.get("ZapisStan") == "wyłączony (próba gry)" and w.get("w") is None,
                  "zwykła próba: ZapisStan %r, ZapisAktywny %r, StanGraczaWczytany %r" % (k.get("ZapisStan"), k.get("ZapisAktywny"), w.get("w")))
            zapisz("Z00", {"wczytany": w, "kontener": k})
            stop()

        # ============================================================ Z01 Play 1: nowy gracz w magazynie próby
        przed, item, kroki = {}, None, {}
        w1 = play(magazyn=True)
        m1 = migawka()
        k1, a1 = m1.get("k", {}), m1.get("a", {})
        punkt("Z01", k1.get("ZapisStan") == "włączony (magazyn próby)" and k1.get("ZapisMagazyn") == MAGAZYN_PROBY
              and w1.get("z") == "aktywny" and k1.get("LicznikWczytan") == 1 and a1.get("Level") == 1 and a1.get("Gold") == 0
              and a1.get("Gems") == G["start"]["gemy"],
              "ZapisStan %r, magazyn %r, StanGraczaZapis %r, wczytań %r, poziom %r, Złoto %r, Gemy %r, wczytanie %r ms"
              % (k1.get("ZapisStan"), k1.get("ZapisMagazyn"), w1.get("z"), k1.get("LicznikWczytan"), a1.get("Level"),
                 a1.get("Gold"), a1.get("Gems"), w1.get("ms")))
        zapisz("Z01", {"wczytany": w1, "migawka": m1})
        try:
            # ======================================================== Z02 gra
            kroki = {}

            def krok(nazwa, fn):
                try:
                    kroki[nazwa] = fn()
                except Exception as e:  # noqa: BLE001 — krok nieudany: zapisujemy powód, próba idzie dalej
                    kroki[nazwa] = {"ok": False, "blad": str(e)[-300:]}
                zapisz("Z02_kroki", kroki)
                return kroki[nazwa]
            luau(KOD["klasa"] % KLASA, "Client")
            krok("klasa", lambda: bool(czekaj_na(lambda: migawka()["a"].get("Class") == KLASA, 15, 0.5)))
            krok("lup", lambda: js(KOD["przyznaj"] % (4000, 400)))
            time.sleep(1.0)
            for _ in range(2):
                luau(KOD["plus"] % "Luck", "Client")
                time.sleep(0.6)
            krok("sklep", lambda: js(KOD["sklep"]))
            item = kroki["sklep"].get("id")
            if item:
                luau(KOD["do_kowala"], "Server")
                time.sleep(1.5)
                krok("ulepsz", lambda: js(KOD["ulepsz"] % item, "Client"))
                time.sleep(1.2)
                inny = krok("oferta_przed_strojem", lambda: js(KOD["oferta"] % (item, kroki["sklep"].get("slot") or ""))).get("inny")
                if inny:
                    krok("stroj", lambda: js(KOD["stroj"] % (KLASA_STROJU, inny), "Client"))
                time.sleep(1.2)
                krok("oferta_po_stroju", lambda: js(KOD["oferta"] % (item, "")))
            krok("pet", lambda: js(KOD["pet"] % JAJKO))
            # 26.11.2026: kontener treningu bez mini-gier (MiniGry = false) — rundy mini-gry nie ma, krok „nie dotyczy”
            mini = edit.get("MiniGry") is not False
            tw = (krok("trening_wejdz", lambda: js(KOD["trening_wejdz"])) if mini else
                  {"ok": False, "nie_dotyczy": "mini-gry wyłączone (TreningProba: MiniGry = false)"})
            if tw.get("ok"):
                time.sleep(2.0)
                luau(KOD["trening_klient"] % ("start", "nil"), "Client")
                luau(KOD["trening_klient"] % ("autograj", "1.0, false"), "Client")
                time.sleep((tw.get("dlugosc") or 30) + (tw.get("odliczanie") or 3) + 3)
                luau(KOD["trening_wyjdz"], "Server")
                time.sleep(1.0)
            krok("straznik", lambda: js(KOD["straznik"] % D["gemy"]["prefiks_straznika"]))
            krok("przelot", lambda: luau(KOD["przelot"], "Server"))
            # 27.11.2026: sklep trenera — Rybki na zakup (łup czeka na pokazanie, WydajZloto go najpierw dopisuje)
            krok("lup_sklep", lambda: js(KOD["przyznaj"] % (1000, 0)))
            time.sleep(3.0)
            luau(KOD["do_trenera"], "Server")
            time.sleep(1.0)
            krok("sklep_trenera", lambda: js(KOD["sklep_trenera"], "Client"))
            time.sleep(2.0)
            przed = migawka()
            a = przed.get("a", {})
            kroki["po_grze"] = {n: a.get(n) for n in ("Class", "Level", "Gold", "Gems", "PunktyDoRozdania", "Luck", "PetAktywny",
                                                      "TreningSila", "PokonalStraznikaLasu", "WidzialPrzelotLasu", "KowalDostepne",
                                                      "StrojProba_" + KLASA_STROJU)}
            pak = przed.get("p", {}).get("pakiety") or {}
            stroj = a.get("StrojProba_" + KLASA_STROJU) or ""
            braki = [n for n, ok in (
                ("klasa", kroki.get("klasa") is True), ("łup", kroki["lup"].get("ok")), ("awans", (a.get("Level") or 1) > 1),
                ("sklep", kroki["sklep"].get("ok") and kroki["sklep"].get("stopien") not in (None, "start")),
                ("ulepszenie", (kroki.get("ulepsz") or {}).get("ok")), ("strój", (kroki.get("stroj") or {}).get("ok")),
                ("kupiony założony", (kroki.get("oferta_po_stroju") or {}).get("stan") == "zalozone" and item in stroj.split(",")),
                ("pet", kroki["pet"].get("ok") and a.get("PetAktywny")), ("mini-gra", not mini or ((a.get("TreningSila") or 0) > 0 and "trening" in pak)),
                ("Strażnik", kroki["straznik"].get("ok") and a.get("PokonalStraznikaLasu") is True),
                ("przelot", a.get("WidzialPrzelotLasu") is True), ("kowal w profilu", "kowal" in pak),
                ("sklep trenera w profilu", ((pak.get("TreningAFK") or {}).get("u") or {}).get("Sila") == 1
                 and "Strength" in ((pak.get("TreningAFK") or {}).get("w") or {}))) if not ok]
            punkt("Z02", True if not braki else None, "braki: %s; kroki: %s" % (braki or "brak", json.dumps(kroki, ensure_ascii=False)[:1200]))
            zapisz("Z02", {"kroki": kroki, "przed": przed, "braki": braki})
        finally:
            stop()

        # ============================================================ Z03 rekord po Stop
        r3 = rekord_po_stop()
        a = przed.get("a", {})
        oczek = "poziom %s, doświadczenie %s, Złoto %s, Gemy %s, klasa %s" % (a.get("Level"), a.get("XP"), a.get("Gold"),
                                                                              a.get("Gems"), przed.get("p", {}).get("idKlasy"))
        punkt("Z03", oczek in r3 and "świeża sesja" not in r3, "rekord: %s | oczekiwane: %s" % (r3, oczek))
        zapisz("Z03", r3)

        # ============================================================ Z04 Play 2: stan wrócił
        w4 = play(magazyn=True)
        po = migawka()
        zle, inne = porownaj(przed, po)
        k4 = po.get("k", {})
        punkt("Z04", not zle and w4.get("z") == "aktywny" and k4.get("LicznikWczytan") == 1,
              "wróciło %s; wczytanie %s ms; różnice trwałe: %s; inne: %s" % ("WSZYSTKO" if not zle else "NIE WSZYSTKO", w4.get("ms"),
                                                                          zle[:8] or "brak", inne[:6] or "brak"))
        zapisz("Z04", {"wczytany": w4, "po": po, "zle": zle, "inne": inne})
        if item:
            of4 = js(KOD["oferta"] % (item, ""))
            kow = ((po.get("p", {}).get("pakiety") or {}).get("kowal") or {}).get("przedmioty") or {}
            stroj4 = po.get("a", {}).get("StrojProba_" + KLASA_STROJU) or ""
            try:
                klient4 = js(KOD["stroj_klienta"] % KLASA_STROJU, "Client")
            except Exception as e:  # noqa: BLE001
                klient4 = {"blad": str(e)[-200:]}
            punkt("Z04b", of4.get("stan") == "zalozone" and item in kow and item in stroj4.split(",")
                  and isinstance(klient4, list) and item in klient4
                  and of4.get("ulepszenie") == (kroki.get("oferta_po_stroju") or {}).get("ulepszenie"),
                  "kupiony %s (%s, stopień %s): po ponownym wejściu stan oferty %r, ulepszenie %r, w profilu kowala %s, "
                  "w stroju %s, na bohaterze u klienta %s" % (item, kroki["sklep"].get("nazwa"), kroki["sklep"].get("stopien"),
                                   of4.get("stan"), of4.get("ulepszenie"), item in kow, item in stroj4.split(","),
                                   isinstance(klient4, list) and item in klient4))
            zapisz("Z04b", {"oferta": of4, "kowal": kow.get(item), "stroj": stroj4, "klient": klient4})
        try:
            # ======================================================== Z05 błąd usługi przy zapisie wyjścia
            zl = (po.get("a", {}).get("Gold") or 0)
            js(KOD["przyznaj"] % (11, 0))
            time.sleep(0.5)
            zl5 = migawka().get("a", {}).get("Gold")
            luau(KOD["bledy"] % (G["proba"]["atrybut_bledow"], 2), "Server")
        finally:
            stop()
        r5 = rekord_po_stop()
        punkt("Z05", ("Złoto %s," % zl5) in r5 and (zl5 or 0) > zl,
              "po 2 błędach przy zamknięciu: %s (Złoto %s → %s przed Stop; łup z premią peta)" % (r5, zl, zl5))
        zapisz("Z05", r5)

        # ============================================================ Z06 Play 3: usługa pada cały czas
        w6 = play(magazyn=True, bledy=1000)
        try:
            m6 = migawka()
            g0 = m6.get("a", {}).get("Gold") or 0
            js(KOD["przyznaj"] % (5, 0))
            time.sleep(0.5)
            g1 = migawka().get("a", {}).get("Gold")
        finally:
            stop()
        r6 = rekord_po_stop()
        punkt("Z06", w6.get("z") == "bez_zapisu" and w6.get("w") is True and (g1 or 0) > g0 and r6 == r5,
              "StanGraczaZapis %r po %s ms, Złoto w pamięci %s → %s, rekord przed %r, po %r"
              % (w6.get("z"), w6.get("ms"), g0, g1, r5, r6))
        zapisz("Z06", {"wczytany": w6, "migawka": m6, "rekord": r6})

        # ============================================================ Z07 sprzątanie
        r7 = rekord_proby(kasuj=True)
        st = luau(ZP.LUAU_STAN, "Edit")
        punkt("Z07", r7.startswith("SKASOWANO") and "znacznik nil" in st, "%s | %s" % (r7, st))

        # ============================================================ Z08 konsola
        kon = call("get_console_output")["text"]
        zapisz("konsola", kon[-20000:])
        zle_k = [l for l in kon.splitlines() if re.search(r"(StanGracza|KowalProba|PetyProba|TreningProba|StrojeProba|SklepProba)"
                                                          r".*(error|Error|attempt to|Stack Begin)", l)]
        punkt("Z08", not zle_k, "błędy skryptów: %s" % (zle_k[:5] or "brak"))
    log("lista:", os.path.join(wyj, "lista.txt"))
    return 0


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    sys.exit(main())
