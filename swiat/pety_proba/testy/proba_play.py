# -*- coding: utf-8 -*-
"""Próba „jajek i petów” w Roblox Studio (tryb Play) — część B zlecenia z 17.11.2026. Nie zmienia miejsca: sama włącza
i wyłącza Play, niczego nie zapisuje i nie publikuje.

    python -B swiat/pety_proba/testy/proba_play.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow] [--bez-walki]
    python -B swiat/pety_proba/testy/proba_play.py <folder wyników POZA repo> --bagno   # tylko jajko Bagna (B00–B09)
    python -B swiat/pety_proba/testy/proba_play.py <folder wyników POZA repo> --dzungla # jajko Dżungli (te same B00–B09)
    python -B swiat/pety_proba/testy/proba_play.py <folder wyników POZA repo> --zagroda # zagroda daje Rybki (Z01–Z09)
    python -B swiat/pety_proba/testy/proba_play.py --sprawdz      # bez Studio: parsuje każdy kawałek Luau (luau_mini)

Warunki (tryb Edit): Workspace/PetyProba (swiat/pety_proba/zbuduj.py), Workspace/StanGracza (z sygnałami WydajZloto
i Pety — swiat/stan_gracza/zbuduj.py), Workspace/LasPas + LasPasGra (inkubator stoi na mapie lasu-pasa),
Workspace/MiasteczkoBazar + MiasteczkoBazarGra (zagroda i E opiekunki), Workspace/TestWalki2 (walka z petem).
Wyniki (wyniki.json, lista.txt) idą do podanego folderu — mogą zawierać nazwę konta, dlatego folder nie może leżeć
w repozytorium. Zrzuty (lista graczy i czat schowane) → swiat/pety_proba/klatki/.

Złoto do zakupów próba ustawia wprost w atrybucie Gold (przygotowanie testu — w grze daje je łup z walk). Wszystko
inne idzie drogą gracza: prawdziwe E (przytrzymanie), prawdziwe chodzenie postacią, E opiekunki w bazarze.

LISTA KONTROLNA (OK / BŁĄD / ?):
  P00 w Edit: kontenery na miejscu; script_grep po innych piszących PetAktywny / PetyLiczba (i)
  P01 gotowość: SerwerPetowGotowy, ZgodnoscLogikiPetow „OK n/n”, KlientPetowGotowy, StanGracza gotowy, jajko lokalne
  P02 klasa wybrana (ekran wyboru zamknięty — HUD widać)
  P03 brak Złota: Gold = 0, prawdziwe E przy inkubatorze → odmowa „Brakuje ci … Złota”, Gold bez zmian, bez peta
  P04 kupno prawdziwym E (Gold = 2000): Złoto − cena, PetyLiczba 1, PetAktywny, napis ceny „Kup za N Złota”; zrzuty
      wyklucia: trzęsienie, pęknięcie, wyskok, napis
  P05 drugi E w trakcie wyklucia → odmowa „trwa wyklucie”, Złoto bez zmian
  P06 pet za graczem: marsz postacią ~40 st (character_navigation) — odległość peta ≤ 12 st w marszu, ≤ 6 po
      zatrzymaniu; klip chód / spoczynek; zrzut
  P07 każdy pet w świecie: pięć petów obok siebie przy inkubatorze (haczyk "pokaz"), zrzut całości i każdego z bliska
  P07b każdy z pięciu petów IDZIE ZA GRACZEM (pety kupione haczykiem "kup" z wymuszonym losem, aktywny wybrany
      haczykiem "wybierz" bez zasięgu — zaznaczone w opisie), marsz postacią, zrzut z kamery za plecami
  P08 wyklucie każdego peta (haczyk "wyklucie" — sama animacja u klienta), zrzut napisu każdego
  P09 zagroda: pety stojące w zagrodzie (od 25.11 tyle, ile miejsc ma poziom) na miejscach i tablica (lista z kopiami),
      prawdziwe E opiekunki → okno „PRÓBA”; zrzuty
  P10 wybór aktywnego peta z okna (jak przycisk „Wybierz”: Jelonek Gaju) → PetAktywny, pet za graczem zmienia się; zrzut
  P11 premia peta przy łupie (StanGracza "przyznaj") → Złoto + premia (+5%), napis „+N … od peta”; skill peta
      w StanGracza/Sygnaly/Modyfikatory (źródło "pety": +20% Siły, pasywki Kryształu) — gdy stan gracza ma sygnał; zrzut
  P12 reset postaci w trakcie wyklucia → pet jest u gracza, po odrodzeniu idzie za nim, konsola czysta
  P13 walka z petem przy boku (las-pas, slime): w walce pet znika (u siebie i PetCzeka dla innych), po walce wraca;
      łup z premią; zrzut w walce
  P14 bez sygnału StanGracza/Sygnaly/Pety (zmiana nazwy) → E daje „Inkubator nieczynny…”, bez błędów; nazwa wraca
  P15 konsola: bez błędów naszych skryptów ([PetyProba], „Script …PetyProba”)

LISTA --bagno (17.11 wieczór, jajko Bagna; warunki jak wyżej + Workspace/BagnoPas, BagnoPasGra, WskazowkiGry):
  B00 gładkie jajko leśne przy inkubatorze lasu (zrzut „po” do pary „przed / po”)
  B01 dwa inkubatory u klienta (jajka lokalne), ceny obu jajek z serwera (Bagno od ceny startowej)
  B02 inkubator Bagna: zrzut z daleka i tablicy szans z bliska; Gold = 0, prawdziwe E → odmowa z kwotą braku
  B03 wskazówka celu: Złota tyle co jajko Bagna, gracz przy Pomoście Przybycia → krok „f_jajko_bagno”; zrzut
  B04 kupno prawdziwym E (Gold = 3000): Złoto − cena, licznik jajek Bagna 1, cena jajka leśnego bez zmian; zrzuty
      wyklucia: trzęsienie, pęknięcie, wyskok, napis
  B05 pięć petów Bagna obok siebie przy inkubatorze (haczyk "pokaz"), zrzut całości i każdego z bliska
  B06 każdy z pięciu petów Bagna IDZIE ZA GRACZEM (kupione haczykiem "kup" z wymuszonym losem, aktywny wybrany
      haczykiem bez zasięgu — zaznaczone w opisie), zrzut z kamery za plecami
  B07 wyklucie każdego peta Bagna (haczyk "wyklucie" z jajkiem Bagna), zrzut napisu każdego
  B08 zagroda z dziesięcioma petami (pięć leśnych dokupionych haczykiem): tablica w dwóch kolumnach, prawdziwe E
      opiekunki → okno „PRÓBA” podzielone na jajka, przewinięte do końca; zrzuty
  B09 wybór peta Bagna z okna → PetAktywny, pet za graczem

--dzungla (18.11, jajko Dżungli): te same punkty B00–B09 dla jajka Dżungli (Workspace/DzunglaPas, DzunglaPasGra,
WskazowkiGry; krok wskazówki „f_jajko_dzungla”; gracz dostaje PokonalStraznikaBagna jak po Strażniku Topieli),
zrzuty z przedrostkiem „dz” zamiast „b”.

LISTA --zagroda (25.11.2026, zagroda daje Rybki — PRZYGOTOWANE, jeszcze nieuruchomione; warunki jak wyżej, StanGracza
z poleceniem Pety("przychod") — swiat/stan_gracza/zbuduj.py --skrypty; zrzuty „z…”):
  Z01 trzy pety lasu (haczyk "kup" z wymuszonym losem): Żołędziak za graczem, Świetlikówka i Jelonek Gaju w zagrodzie
      (2 miejsca) — serwer "zagroda": stoja, miejsc, wczytany, Rybki/s
  Z02 naliczanie: Gold rośnie o Rybki/s × czas (co tik_s; ± jeden tik), LicznikPrzychodow > 0 (pety i stan gracza)
  Z03 napis „+N Rybek” nad zagrodą (gracz przy zagrodzie) — licznik plusów klienta rośnie; zrzut
  Z04 pety stojące w zagrodzie na znacznikach mapy (tyle modeli, ile stoi, najwyżej tyle, ile znaczników — 6 albo 8)
  Z05 E opiekunki → okno z wierszem zagrody („ZAGRODA: 2/2 miejsc · +N Rybek/min”, „Więcej miejsc …”); zrzut
  Z06 „Więcej miejsc” bez Rybek (Gold = 0) → odmowa „Brakuje ci … Rybek”, Gold bez zmian
  Z07 „Więcej miejsc” z Rybkami (Gold = cena + 50) → 4 miejsca, Gold = 50, napis „Miejsca w zagrodzie: 4”; zrzut okna
  Z08 „Z zagrody” (Świetlikówka) → nie stoi, wybór ręczny; „Najrzadsze” → wraca wybór domyślny
  Z09 pet za graczem nie stoi w zagrodzie: „Wybierz” Jelonka → Jelonek poza zagrodą, Żołędziak w zagrodzie
  (P15) konsola: bez błędów naszych skryptów — jak w każdej próbie
"""
import io
import json
import math
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (PAKIET, os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki_roblox"), os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane_petow as DP  # noqa: E402
import logika_petow as LP  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
U = DP.ustawienia()
ZNANE_W_KONSOLI = ("Requester does not have permission for Asset",)

GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
KP = 'local k = workspace:FindFirstChild("LasPasGra") local H = game:GetService("HttpService") '
J = ('local H = game:GetService("HttpService") local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu zer (tools/walka/luau_mini.py).
KOD = {
    "edit": ('local H = game:GetService("HttpService") local function jest(n) local o = workspace:FindFirstChild(n) '
             'return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
             'return H:JSONEncode({ pety = jest("PetyProba"), stan = jest("StanGracza"), pas = jest("LasPasGra"), '
             'mapa = workspace:FindFirstChild("LasPas") ~= nil, bazar = jest("MiasteczkoBazarGra"), '
             'mapaBazaru = workspace:FindFirstChild("MiasteczkoBazar") ~= nil, walka = workspace:FindFirstChild("TestWalki2") ~= nil, '
             'syg = workspace:FindFirstChild("StanGracza") ~= nil and workspace.StanGracza.Sygnaly:FindFirstChild("Pety") ~= nil })'),
    "gracz_atr": GR + 'local o = {} for _, n in { %s } do o[n] = J(gracz:GetAttribute(n)) end return H:JSONEncode(o)',
    "kont_atr": 'local o = {} local f = workspace:FindFirstChild("%s") if not f then return H:JSONEncode({ brak = true }) end '
                'for _, n in { %s } do o[n] = J(f:GetAttribute(n)) end return H:JSONEncode(o)',
    "ustaw_atr": GR + 'gracz:SetAttribute("%s", %s) return "ok"',
    "przestaw": HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) '
                      'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"',
    "pozycja": HRP + 'return H:JSONEncode(J(hrp.Position))',
    "klient": 'return H:JSONEncode(J(workspace.PetyProba.Sygnaly.SterowanieKlienta:Invoke(%s)))',
    "serwer": 'return H:JSONEncode(J(workspace.PetyProba.Sygnaly.SterowanieSerwera:Invoke(%s)))',
    "kamera": ('local cam = workspace.CurrentCamera cam.CameraType = Enum.CameraType.Scriptable '
               'cam.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) return "ok"'),
    "kamera_za": ('local cam = workspace.CurrentCamera local h = game:GetService("Players").LocalPlayer.Character.HumanoidRootPart '
                  'cam.CameraType = Enum.CameraType.Scriptable local f = h.CFrame.LookVector '
                  'cam.CFrame = CFrame.lookAt(h.Position - f * %f + Vector3.new(0, %f, 0), h.Position + f * 3) return "ok"'),
    "kamera_zwykla": 'workspace.CurrentCamera.CameraType = Enum.CameraType.Custom return "ok"',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "wybor_klasy": ('local H = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
                    'local g = p.PlayerGui:FindFirstChild("ClassSelect") local hud = p.PlayerGui:FindFirstChild("HUD") '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, hud = hud ~= nil and hud.Enabled, '
                    'klasa = p:GetAttribute("Class") or false })'),
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"',
    "reset": GR + 'local h = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid") if h then h.Health = 0 end return "ok"',
    "przemianuj": ('local s = workspace:FindFirstChild("StanGracza") local f = s and s.Sygnaly:FindFirstChild("%s") '
                   'if f then f.Name = "%s" end return tostring(f ~= nil)'),
    "przyznaj": ('local s = workspace.StanGracza return H:JSONEncode(J(s.Sygnaly.SterowanieSerwera:Invoke("przyznaj", '
                 'game:GetService("Players"):GetPlayers()[1], { zloto = %d, doswiadczenie = %d, tokeny_krainy = 0, gemy = 0, '
                 'shard_ewolucji = 0, kraina = "las" })))'),
    "potwor_w_strefie": KP + ('local najlepszy for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" '
                              'and c:GetAttribute("Stan") ~= "zajety" then najlepszy = c break end end '
                              'if not najlepszy then return H:JSONEncode({}) end '
                              'return H:JSONEncode({ id = najlepszy.Name, p = J(najlepszy:GetAttribute("Pozycja")) })'),
    "walcz": KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))',
    "klient_potworow": KP + 'return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "odtw": 'return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))',
    "test_bohater": 'local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("TestBohater", %s) end return "ok"',
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "test_kamera": 'workspace.PetyProba:SetAttribute("TestKameraProby", %s) return "ok"',
    "przelot": ('local k = workspace:FindFirstChild("%s") local lp = game:GetService("Players").LocalPlayer '
                'local h = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") '
                'local p = k and (k.Sygnaly.SterowaniePasaKlienta:Invoke("stan") or {}).przelot '
                'return tostring((p ~= nil and p ~= false) or (h ~= nil and h.Anchored) or '
                'workspace.CurrentCamera.CameraType ~= Enum.CameraType.Custom)'),
    "okno_otwarte": ('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("PetyProbaOkno") '
                     'return tostring(g ~= nil and g.Enabled)'),
    "wskazowka": ('local w = workspace:FindFirstChild("WskazowkiGry") if not w then return H:JSONEncode({ brak = true }) end '
                  'return H:JSONEncode(J(w.Sygnaly.SterowanieKlienta:Invoke("stan")))'),
    "otworz_brame": 'return tostring(workspace.LasPasGra.Sygnaly.SterowaniePasa:Invoke("otworzBrame"))',
    "otworz_brame_bagna": 'return tostring(workspace.BagnoPasGra.Sygnaly.SterowaniePasa:Invoke("otworzBrame"))',
    "przewin_okno": ('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("PetyProbaOkno") '
                     'local l = g and g.Ramka:FindFirstChild("Lista") if l then l.CanvasPosition = Vector2.new(0, %d) end '
                     'return tostring(l ~= nil)'),
    "edit_dzungla": ('local H = game:GetService("HttpService") local function jest(n) local o = workspace:FindFirstChild(n) '
                     'return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
                     'return H:JSONEncode({ bagno = jest("DzunglaPasGra"), mapa = workspace:FindFirstChild("DzunglaPas") ~= nil, '
                     'wskazowki = jest("WskazowkiGry"), inkubator = workspace:FindFirstChild("PetyProba") ~= nil and '
                     'workspace.PetyProba:FindFirstChild("%s") ~= nil })'),
    "edit_bagno": ('local H = game:GetService("HttpService") local function jest(n) local o = workspace:FindFirstChild(n) '
                   'return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
                   'return H:JSONEncode({ bagno = jest("BagnoPasGra"), mapa = workspace:FindFirstChild("BagnoPas") ~= nil, '
                   'wskazowki = jest("WskazowkiGry"), inkubator = workspace:FindFirstChild("PetyProba") ~= nil and '
                   'workspace.PetyProba:FindFirstChild("%s") ~= nil })'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy szablon z KOD (po podstawieniu zer) parsuje się w luau_mini."""
    import luau_mini as LM
    bledy = []
    for nazwa, szablon in KOD.items():
        kod = re.sub(r"%[sdf]", "0", szablon)
        if ("J(" in kod or "H:" in kod) and "local function J" not in kod:
            kod = J + kod
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def stoisko_zagrody(G):
    """Gdzie próba stawia gracza przed E Jagody (środek HumanoidRootPart). 26.11.2026: 2,5 st przed podpowiedzią Jagody,
    przodem do niej. Po przebudowie miasta 25.11 ok. 3 st od stoiska stoi jajko Pawła (Workspace/JajkoKorowePodglad,
    własna podpowiedź E „Kup jajko”, zasięg 12 st). Gdy podpowiedź Jagody stała jeszcze w starym miejscu (kontener
    MiasteczkoBazarGra zbudowany przed przebudową), E przed Jagodą kupowało jajko; przodem do Jagody jej podpowiedź
    wygrywa, z boku (1,5–3,5 st obok) — podpowiedź jajka."""
    ez, kz, pz = G["zagroda_e"], G["zagroda_kier"], G["zagroda_podpowiedz"]
    return (pz[0] + kz[0] * 2.5, ez[1] + 3.0, pz[2] + kz[2] * 2.5)


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
        sys.exit("Folder wyników leży w repozytorium (wyniki mogą zawierać nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    bez_walki = "--bez-walki" in argv
    tylko_bagno = "--bagno" in argv or "--dzungla" in argv
    tylko_zagroda = "--zagroda" in argv                            # 25.11.2026: zagroda daje Rybki (Z01–Z10)
    kraina_b = "dzungla" if "--dzungla" in argv else "bagno"      # biom próby jajka spoza lasu
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
    D = DP.dane_z_przypadkami()
    G = D["polozenia"]
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None

    WYNIKI, LISTA = {}, []

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = wartosc
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
                except Exception as e:  # noqa: BLE001 — Studio czasem nie odpowiada chwilę
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(8)

        def js(kod, dm):
            w = json.loads(luau(J + kod, dm))
            return {} if w == [] else w

        ujecie = [None]   # (oko, cel) ostatniej kamery testu — zrzut ustawia je narzędziem (skrypty gry wracają do Custom)

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            a = {"capture_id": "pety_" + nazwa}
            if ujecie[0]:
                a["camera_position"] = list(ujecie[0][0])
                a["look_at_position"] = list(ujecie[0][1])
            r = call("screen_capture", a, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(KLATKI, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(KLATKI, nazwa + ".png"), "wb") as f:
                    f.write(dane)
            log("zrzut", nazwa)

        def lua_lista(nazwy):
            return ", ".join('"%s"' % n for n in nazwy)

        def atr(*nazwy):
            return js(KOD["gracz_atr"] % lua_lista(nazwy), "Server")

        def kont(nazwa, atrybuty, dm="Server"):
            return js(KOD["kont_atr"] % (nazwa, lua_lista(atrybuty)), dm)

        def klient(argi):
            return js(KOD["klient"] % argi, "Client")

        def serwer(argi):
            return js(KOD["serwer"] % argi, "Server")

        def przestaw(p, patrz):
            luau(KOD["przestaw"] % (p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def przytrzymaj_e():
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "E"},
                {"action": "wait", "wait_time_ms": int(1000 * (D["inkubator"]["przytrzymaj_s"] + 0.35))},
                {"action": "keyUp", "key_code": "E"}]})

        def nacisnij(klawisz):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def kamera(oko, cel):
            # tylko ujęcie zrzutu (narzędzie screen_capture) — kamera gracza zostaje zwykła (E działa, pety widać)
            ujecie[0] = (tuple(oko), tuple(cel))

        def za_graczem(dal=9.0, wys=4.0, bok=3.0):
            p = js(KOD["pozycja"], "Server")
            kamera((p[0] - dal, p[1] + wys, p[2] + bok), (p[0] + 2.0, p[1] - 0.5, p[2]))

        def kamera_zwykla():
            ujecie[0] = None
            luau(KOD["kamera_zwykla"], "Client")

        JL = D["jajka"][0]
        gniazdo, e = JL["polozenie"]["gniazdo"], JL["polozenie"]["e"]
        # stanowisko gracza przy E: krok dalej od gniazda niż punkt E, twarzą do jajka
        kier = (e[0] - gniazdo[0], e[2] - gniazdo[2])
        dl = math.hypot(*kier)
        kier = (kier[0] / dl, kier[1] / dl)
        stoi = (gniazdo[0] + kier[0] * 6.0, e[1] + 3.0, gniazdo[2] + kier[1] * 6.0)

        def do_inkubatora():
            przestaw(stoi, gniazdo)
            time.sleep(1.2)

        def oko_inkubatora(dal=11.0, wys=5.5, gn=None, kr=None, dy=0.0):
            # z boku (po stronie, na którą ląduje pet) — postać przy E nie zasłania jajka
            gn, kr = gn or gniazdo, kr or kier
            bok = (-kr[1], kr[0])
            return ((gn[0] + kr[0] * dal + bok[0] * 8.0, gn[1] + wys + dy, gn[2] + kr[1] * dal + bok[1] * 8.0),
                    (gn[0] + kr[0] * 2.0 + bok[0] * 1.5, gn[1] + 2.4 + dy, gn[2] + kr[1] * 2.0 + bok[1] * 1.5))

        # ---------------------------------------------------------------- jajko Bagna (--bagno)
        JB = next(j for j in D["jajka"] if j["kraina"] == kraina_b)
        KONT_B = {"bagno": "BagnoPasGra", "dzungla": "DzunglaPasGra"}[kraina_b]   # przelot kamery biomu
        PX = "b" if kraina_b == "bagno" else "dz"                                     # przedrostek zrzutów
        gn_b, e_b = JB["polozenie"]["gniazdo"], JB["polozenie"]["e"]
        kier_b = (e_b[0] - gn_b[0], e_b[2] - gn_b[2])
        dl_b = math.hypot(*kier_b)
        kier_b = (kier_b[0] / dl_b, kier_b[1] / dl_b)
        stoi_b = (gn_b[0] + kier_b[0] * 6.0, e_b[1] + 3.0, gn_b[2] + kier_b[1] * 6.0)
        dy_b = JB["y_jajka"] - JL["y_jajka"]          # jajko Bagna leży wyżej (gniazdo na palach)

        def do_inkubatora_bagna():
            przestaw(stoi_b, gn_b)
            time.sleep(1.2)

        def swiat_stanowiska(J, x, y, z):
            """Punkt z układu stanowiska (rig: przód −Z) w świecie — jak zbuduj.py: CFrame(gniazdo) * obrót Y."""
            a = math.radians(J["polozenie"]["obrot"])
            g = J["polozenie"]["gniazdo"]
            return (g[0] + x * math.cos(a) + z * math.sin(a), g[1] + y, g[2] - x * math.sin(a) + z * math.cos(a))

        def proba_bagna():
            CB, KB, CL = JB["atrybuty"]["cena"], JB["atrybuty"]["kupione"], JL["atrybuty"]["cena"]
            eb = json.loads(luau(KOD["edit_" + kraina_b] % JB["folder"], "Server"))
            zapisz("B_edit", eb)
            # ============================================================ B00 gładkie jajko leśne (para „przed / po”)
            do_inkubatora()
            czekaj_na(lambda: luau(KOD["przelot"] % "LasPasGra", "Client") == "true", 6, 0.4)
            czekaj_na(lambda: luau(KOD["przelot"] % "LasPasGra", "Client") == "false", 40, 1.0)
            do_inkubatora()
            kamera(*oko_inkubatora(dal=6.5, wys=3.2))
            zrzut(PX + "00_jajko_lesne_gladkie")
            punkt("B00", None, "gładkie jajko leśne — zrzut b00 (para z klatkami „przed” w raporcie)")
            # ============================================================ B01 dwa inkubatory, ceny
            kl = klient('"stan"')
            st = serwer('"stan"')
            zapisz("B01", {"klient": kl, "serwer": st, "edit": eb})
            punkt("B01", kl.get("jajekLokalnych") == len(D["jajka"]) and (st.get("ceny") or {}).get(JB["id"]) == LP.cena(D, JB, 0)
                  and eb.get("inkubator") is True, "jajek lokalnych %s, ceny %s, Bagno w miejscu %s"
                  % (kl.get("jajekLokalnych"), st.get("ceny"), eb))
            # ============================================================ B02 inkubator Bagna, brak Złota
            # wejście do Bagna wymaga pokonanego Strażnika lasu (serwer pasa cofa przed bramę) — haczyk jak w próbach
            # swiat/bagno_pas_gra/testy (otworzBrame); potem przelot kamery Bagna (podpowiedzi E w tym czasie nie działają)
            zapisz("B_brama", luau(KOD["otworz_brame"], "Server"))
            if kraina_b == "dzungla":   # Dżungla wpuszcza za Strażnikiem Topieli (DaneDzungli.wymaganie)
                zapisz("B_brama_bagna", luau(KOD["otworz_brame_bagna"], "Server"))
                luau(KOD["ustaw_atr"] % ("PokonalStraznikaBagna", "true"), "Server")
            luau(KOD["ustaw_atr"] % ("Gold", "0"), "Server")
            do_inkubatora_bagna()
            czekaj_na(lambda: luau(KOD["przelot"] % KONT_B, "Client") == "true", 6, 0.4)
            czekaj_na(lambda: luau(KOD["przelot"] % KONT_B, "Client") == "false", 40, 1.0)
            do_inkubatora_bagna()
            bok_b = (-kier_b[1], kier_b[0])
            kamera((gn_b[0] + kier_b[0] * 26.0 + bok_b[0] * 14.0, gn_b[1] + 13.0, gn_b[2] + kier_b[1] * 26.0 + bok_b[1] * 14.0),
                   (gn_b[0], gn_b[1] + 3.5, gn_b[2]))
            zrzut(PX + "01_inkubator_bagna_z_daleka")
            papier = next(c for c in JB["stale"]["czesci"] if c[2] == D["modele"]["papier"])
            pp = swiat_stanowiska(JB, papier[3], papier[4], papier[5])
            kamera((pp[0] + kier_b[0] * 5.5 + bok_b[0] * 1.0, pp[1] + 0.4, pp[2] + kier_b[1] * 5.5 + bok_b[1] * 1.0), pp)
            zrzut(PX + "02_tablica_szans_bagna")
            kamera(*oko_inkubatora(dal=10.0, wys=9.0, gn=gn_b, kr=kier_b, dy=dy_b))
            przytrzymaj_e()
            time.sleep(0.8)
            kl = klient('"stan"')
            odm = kont("PetyProba", ["OstatniaOdmowa"])
            po = atr("Gold", KB)
            zrzut(PX + "03_brak_zlota_bagno")
            zapisz("B02", {"klient": kl, "odmowa": odm, "po": po})
            punkt("B02", odm.get("OstatniaOdmowa") == "za_malo" and ("kosztuje %d" % LP.cena(D, JB, 0)) in str(kl.get("komunikat"))
                  and po.get("Gold") == 0, "komunikat %r, Gold %s" % (kl.get("komunikat"), po.get("Gold")))
            # ============================================================ B03 wskazówka „stać cię na jajko Bagna”
            luau(KOD["ustaw_atr"] % ("Gold", str(LP.cena(D, JB, 0))), "Server")
            kamera_zwykla()
            w3 = czekaj_na(lambda: (lambda w: w if w.get("krok") == "f_jajko_" + kraina_b else None)(
                js(KOD["wskazowka"], "Client")), 6, 0.5) or js(KOD["wskazowka"], "Client")
            zrzut(PX + "04_wskazowka_jajko_bagna")
            zapisz("B03", w3)
            punkt("B03", w3.get("krok") == "f_jajko_" + kraina_b and w3.get("cel") == "jajko",
                  "krok %s (%r), kraina %s, jajko %s, kupione %s" % (w3.get("krok"), w3.get("tekst"), w3.get("kraina"),
                                                                    w3.get("jajko"), w3.get("kupione")))
            # ============================================================ B04 kupno prawdziwym E + wyklucie
            luau(KOD["ustaw_atr"] % ("Gold", "3000"), "Server")
            do_inkubatora_bagna()
            kamera(*oko_inkubatora(dal=10.0, wys=9.0, gn=gn_b, kr=kier_b, dy=dy_b))
            time.sleep(0.6)
            kl0 = klient('"stan"')
            przytrzymaj_e()
            t0 = time.time()
            for t, nazwa in ((0.8, PX + "05_wyklucie_trzesienie"), (1.75, PX + "06_wyklucie_pekniecie"),
                             (2.45, PX + "07_wyklucie_wyskok"), (4.0, PX + "08_wyklucie_napis")):
                while time.time() - t0 < t:
                    time.sleep(0.05)
                zrzut(nazwa)
            po4 = atr("Gold", "PetyLiczba", "PetAktywny", CB, KB, CL)
            mod4 = (serwer('"stan"') or {}).get("modyfikatory") or {}
            zapisz("B04", {"przed": kl0, "po": po4, "modyfikatory": mod4})
            punkt("B04", po4.get("Gold") == 3000 - LP.cena(D, JB, 0) and po4.get(KB) == 1 and po4.get(CB) == LP.cena(D, JB, 1)
                  and po4.get(CL) == LP.cena(D, JL, 0) and po4.get("PetAktywny") in JB["pula"]
                  and "Kup za %d" % LP.cena(D, JB, 0) in str((kl0.get("akcjeE") or {}).get(JB["id"])),
                  "E %r → Gold %s, pet %s, cena Bagna %s, cena lasu %s (bez zmian)" % (
                      (kl0.get("akcjeE") or {}).get(JB["id"]), po4.get("Gold"), po4.get("PetAktywny"), po4.get(CB),
                      po4.get(CL)))
            time.sleep(2.5)
            kamera_zwykla()
            # ============================================================ zakupy: komplet petów Bagna (haczyk)
            pety_b = list(JB["pula"])
            luau(KOD["ustaw_atr"] % ("Gold", "20000"), "Server")
            for r in (0.1, 0.6, 0.8, 0.9, 0.995):             # wymuszony los: każdy pet raz (test, nie gra)
                serwer('"zwolnij"')
                serwer('"kup", nil, "%s", %f' % (JB["id"], r))
                time.sleep(4.8)
            serwer('"zwolnij"')
            # ============================================================ B05 pięć petów Bagna w świecie
            baza = (gn_b[0] + kier_b[0] * 9.0, gn_b[1] + 0.6, gn_b[2] + kier_b[1] * 9.0)
            miejsca = {}
            for i, pid in enumerate(pety_b):
                o = (i - 2) * 3.6
                miejsca[pid] = (baza[0] + bok_b[0] * o, baza[1], baza[2] + bok_b[1] * o)
                klient('"pokaz", "%s", Vector3.new(%f, %f, %f)' % (pid, miejsca[pid][0], miejsca[pid][1], miejsca[pid][2]))
            time.sleep(1.0)
            kamera((baza[0] + kier_b[0] * 11.0, baza[1] + 4.0, baza[2] + kier_b[1] * 11.0), (baza[0], baza[1] + 1.2, baza[2]))
            zrzut(PX + "09_piec_petow_bagna")
            for pid in pety_b:
                m = miejsca[pid]
                kamera((m[0] + kier_b[0] * 4.6 + bok_b[0] * 1.2, m[1] + 2.0, m[2] + kier_b[1] * 4.6 + bok_b[1] * 1.2),
                       (m[0], m[1] + 1.0, m[2]))
                time.sleep(0.4)
                zrzut(PX + "10_pet_%s" % pid)
            klient('"pokaz_usun"')
            punkt("B05", None, "pięć petów Bagna — zrzuty b09_piec_petow_bagna i b10_pet_<id> do obejrzenia")
            # ============================================================ B06 każdy pet Bagna idzie za graczem
            kamera_zwykla()
            idzie = {}
            for i, pid in enumerate(pety_b):
                serwer('"wybierz", nil, "%s", true' % pid)    # haczyk: wybór bez podchodzenia do zagrody
                do_inkubatora_bagna()
                p0 = js(KOD["pozycja"], "Server")
                cel = (p0[0] + kier_b[0] * 8.0 + bok_b[0] * (6.0 - 3.0 * i), p0[1], p0[2] + kier_b[1] * 8.0 + bok_b[1] * (6.0 - 3.0 * i))
                call("character_navigation", {"datamodel_type": "Client", "x": cel[0], "y": cel[1], "z": cel[2]}, timeout=60)
                time.sleep(0.8)
                za_graczem()
                k6 = klient('"stan"')
                zrzut(PX + "11_idzie_za_graczem_%s" % pid)
                kamera_zwykla()
                idzie[pid] = {"mojPet": k6.get("mojPet"), "odleglosc": k6.get("odleglosc"), "klip": k6.get("klip")}
            zapisz("B06", idzie)
            punkt("B06", all(v["mojPet"] == k for k, v in idzie.items()),
                  "za graczem (pet wymuszony haczykiem): %s" % ", ".join(
                      "%s %s st %s" % (k, v["odleglosc"] and round(v["odleglosc"], 1), v["klip"]) for k, v in idzie.items()))
            # ============================================================ B07 wyklucie każdego peta Bagna
            do_inkubatora_bagna()
            kamera(*oko_inkubatora(dal=11.0, wys=8.5, gn=gn_b, kr=kier_b, dy=dy_b))
            for pid in pety_b:
                klient('"wyklucie", "%s", true, "%s"' % (pid, JB["id"]))
                time.sleep(3.9)
                zrzut(PX + "12_wyklucie_%s" % pid)
                czekaj_na(lambda: not klient('"stan"').get("wylegaSie"), 8, 0.5)
            kamera_zwykla()
            punkt("B07", None, "wyklucie każdego peta Bagna — zrzuty b12_wyklucie_<id>")
            # ============================================================ B08 zagroda z dziesięcioma petami
            luau(KOD["ustaw_atr"] % ("Gold", "20000"), "Server")
            for r in (0.1, 0.6, 0.8, 0.9, 0.995):             # pięć leśnych (haczyk) — razem dziesięć petów
                serwer('"zwolnij"')
                serwer('"kup", nil, "%s", %f' % (JL["id"], r))
                time.sleep(4.8)
            serwer('"zwolnij"')
            serwer('"wybierz", nil, "%s", true' % JB["pula"][0])
            ez, kz = G["zagroda_e"], G["zagroda_kier"]
            stoi_z = stoisko_zagrody(G)
            przestaw(stoi_z, (ez[0] - kz[0] * 5, 0, ez[2] - kz[2] * 5))
            # lista mogła przyjść wcześniej (wybór peta) — czekamy też, aż pety staną na miejscach zagrody
            # od 25.11 (zagroda daje Rybki) na miejscach stoją tylko pety W ZAGRODZIE (na starcie 2 miejsca), nie ≥ 5
            def stoi8(k):
                n = len((k.get("zagroda") or {}).get("stoja") or [])
                return n >= 1 and k.get("petyWZagrodzie") == min(n, k.get("miejscNaMapie") or 0)
            k8 = czekaj_na(lambda: (lambda k: k if (k.get("wiersze") or 0) >= 10 and stoi8(k)
                                    else None)(klient('"stan"')), 15, 0.5) or klient('"stan"')
            kamera((ez[0] + kz[0] * 14.0, ez[1] + 9.0, ez[2] + kz[2] * 14.0), (ez[0] - kz[0] * 3.0, ez[1], ez[2] - kz[2] * 3.0))
            zrzut(PX + "13_zagroda_dziesiec")
            tb = G["zagroda_tablica"]
            kamera((tb[0] + kz[0] * 7.0, tb[1] + 3.6, tb[2] + kz[2] * 7.0), (tb[0], tb[1] + 3.4, tb[2]))
            zrzut(PX + "14_tablica_zagrody_dwa_jajka")
            kamera_zwykla()
            przestaw(stoi_z, (ez[0] - kz[0] * 5, 0, ez[2] - kz[2] * 5))
            time.sleep(1.0)
            przytrzymaj_e()                                   # E opiekunki → OknoMiejsca
            okno = czekaj_na(lambda: luau(KOD["okno_otwarte"], "Client") == "true", 5, 0.4)
            time.sleep(0.8)
            zrzut(PX + "15_okno_dziesiec_petow")
            luau(KOD["przewin_okno"] % 5000, "Client")
            time.sleep(0.5)
            zrzut(PX + "16_okno_przewiniete")
            zapisz("B08", {"klient": k8, "okno": bool(okno)})
            punkt("B08", bool(okno) and (k8.get("wiersze") or 0) == 10 and stoi8(k8),
                  "wierszy %s, pety na miejscach %s (w zagrodzie %s), okno po E %s" % (
                      k8.get("wiersze"), k8.get("petyWZagrodzie"), len((k8.get("zagroda") or {}).get("stoja") or []), bool(okno)))
            # ============================================================ B09 wybór peta Bagna z okna
            klient('"wybierz", "%s"' % JB["pula"][-1])
            time.sleep(1.5)
            a9 = atr("PetAktywny")
            zrzut(PX + "17_okno_po_wyborze_bagna")
            klient('"zamknij"')
            time.sleep(1.5)
            k9 = klient('"stan"')
            punkt("B09", a9.get("PetAktywny") == JB["pula"][-1] and k9.get("mojPet") == JB["pula"][-1],
                  "aktywny %s, za graczem %s" % (a9.get("PetAktywny"), k9.get("mojPet")))

        # ---------------------------------------------------------------- zagroda daje Rybki (--zagroda, 25.11.2026)
        def proba_zagrody():
            Z = D["zagroda"]
            ez, kz = G["zagroda_e"], G["zagroda_kier"]
            stoi_z = stoisko_zagrody(G)

            def przy_zagrodzie():
                przestaw(stoi_z, (ez[0] - kz[0] * 5, 0, ez[2] - kz[2] * 5))
                time.sleep(1.0)

            def zagroda():
                return serwer('"zagroda"')

            # ================================================================ Z01
            luau(KOD["ustaw_atr"] % ("Gold", "5000"), "Server")
            for r in (0.0, 0.95, 0.99):                       # Żołędziak (za graczem), Świetlikówka, Jelonek Gaju
                serwer('"zwolnij"')
                serwer('"kup", nil, "%s", %f' % (JL["id"], r))
                time.sleep(4.8)
            serwer('"zwolnij"')
            z1 = zagroda()
            st1 = z1.get("stan") or {}
            zapisz("Z01", z1)
            punkt("Z01", st1.get("stoja") == ["jelonek_gaju", "swietlikowka"] and st1.get("miejsc") == Z["poziomy"][0]["miejsc"]
                  and z1.get("wczytany") is True, "w zagrodzie %s, miejsc %s, %s" % (st1.get("stoja"), st1.get("miejsc"),
                                                                                    st1.get("opis")))
            # ================================================================ Z02 naliczanie
            s = st1.get("stawka_s") or 0
            przed, t0 = atr("Gold").get("Gold") or 0, time.time()
            time.sleep(Z["tik_s"] * 4 + 2)
            po, t1 = atr("Gold").get("Gold") or 0, time.time()
            dl = (t1 - t0)
            lo, hi = int(s * (dl - 2 * Z["tik_s"])), int(s * (dl + Z["tik_s"])) + 1
            licz = kont("PetyProba", ["LicznikPrzychodow", "OstatniPrzychod"])
            zapisz("Z02", {"przed": przed, "po": po, "sekund": dl, "stawka_s": s, "licznik": licz})
            punkt("Z02", lo <= po - przed <= hi and (licz.get("LicznikPrzychodow") or 0) > 0,
                  "Gold %s → %s (+%s w %.0f s, oczekiwane %d…%d), licznik %s" % (przed, po, po - przed, dl, lo, hi,
                                                                                licz.get("LicznikPrzychodow")))
            # ================================================================ Z03 „+N” przy zagrodzie
            przy_zagrodzie()
            k0 = klient('"stan"')
            k3 = czekaj_na(lambda: (lambda k: k if (k.get("plusow") or 0) > (k0.get("plusow") or 0) else None)(
                klient('"stan"')), Z["tik_s"] * 4, 0.3) or {}
            kamera((ez[0] + kz[0] * 14.0, ez[1] + 9.0, ez[2] + kz[2] * 14.0), (ez[0] - kz[0] * 3.0, ez[1], ez[2] - kz[2] * 3.0))
            zrzut("z03_plus_przy_zagrodzie")
            punkt("Z03", bool(k3) and k3.get("bliskoZagrody") is True, "plusów %s → %s, ostatni +%s" % (
                k0.get("plusow"), k3.get("plusow"), k3.get("ostatniPlus")))
            # ================================================================ Z04 pety na znacznikach
            k4 = klient('"stan"')
            n_st = len((k4.get("zagroda") or {}).get("stoja") or [])
            zapisz("Z04", k4)
            punkt("Z04", k4.get("petyWZagrodzie") == min(n_st, k4.get("miejscNaMapie") or 0) and n_st > 0,
                  "modeli w zagrodzie %s, stoi %s, znaczników na mapie %s" % (k4.get("petyWZagrodzie"), n_st,
                                                                             k4.get("miejscNaMapie")))
            zrzut("z04_pety_w_zagrodzie")
            kamera_zwykla()
            # ================================================================ Z05 okno z wierszem zagrody
            przy_zagrodzie()
            przytrzymaj_e()                                   # E opiekunki → OknoMiejsca
            okno = czekaj_na(lambda: luau(KOD["okno_otwarte"], "Client") == "true", 5, 0.4)
            time.sleep(0.8)
            k5 = klient('"stan"')
            zrzut("z05_okno_zagrody")
            punkt("Z05", bool(okno) and k5.get("wierszZagrodyWOknie") is True, "okno %s, wiersz zagrody %s" % (
                bool(okno), k5.get("wierszZagrodyWOknie")))
            # ================================================================ Z06 ulepszenie bez Rybek
            luau(KOD["ustaw_atr"] % ("Gold", "0"), "Server")
            time.sleep(0.4)
            klient('"ulepsz"')
            time.sleep(1.0)
            odm = kont("PetyProba", ["OstatniaOdmowa"])
            k6 = klient('"stan"')
            g6 = atr("Gold").get("Gold")
            punkt("Z06", odm.get("OstatniaOdmowa") == "za_malo" and "Brakuje" in str(k6.get("komunikat")) and g6 == 0,
                  "odmowa %s, napis %r, Gold %s" % (odm.get("OstatniaOdmowa"), k6.get("komunikat"), g6))
            # ================================================================ Z07 ulepszenie za Rybki
            cena = Z["poziomy"][1]["cena"]
            luau(KOD["ustaw_atr"] % ("Gold", str(cena + 50)), "Server")
            t7 = time.time()
            time.sleep(0.6)
            klient('"ulepsz"')
            time.sleep(1.2)
            z7 = (zagroda().get("stan") or {})
            g7 = atr("Gold").get("Gold")
            # zagroda nalicza dalej w trakcie punktu (26.11: raz było 51) — dopuszczalne Rybki z tików od ustawienia Gold
            g7_hi = 50 + int((z7.get("stawka_s") or 0) * (time.time() - t7 + Z["tik_s"])) + 1
            k7 = klient('"stan"')
            zrzut("z07_okno_po_ulepszeniu")
            zapisz("Z07", {"stan": z7, "gold": g7, "komunikat": k7.get("komunikat")})
            punkt("Z07", z7.get("miejsc") == Z["poziomy"][1]["miejsc"] and isinstance(g7, (int, float)) and 50 <= g7 <= g7_hi,
                  "miejsc %s, Gold %s (oczekiwane 50…%d), napis %r" % (z7.get("miejsc"), g7, g7_hi, k7.get("komunikat")))
            # ================================================================ Z08 „Z zagrody” i „Najrzadsze”
            time.sleep(0.4)
            klient('"z_zagrody", "swietlikowka"')
            time.sleep(1.0)
            z8 = (zagroda().get("stan") or {})
            time.sleep(0.4)
            klient('"najrzadsze"')
            time.sleep(1.0)
            z8b = (zagroda().get("stan") or {})
            punkt("Z08", "swietlikowka" not in (z8.get("stoja") or []) and z8.get("reczny") is True
                  and "swietlikowka" in (z8b.get("stoja") or []) and z8b.get("reczny") is False,
                  "po „Z zagrody” %s (ręczny %s), po „Najrzadsze” %s" % (z8.get("stoja"), z8.get("reczny"), z8b.get("stoja")))
            # ================================================================ Z09 pet za graczem nie stoi w zagrodzie
            time.sleep(0.4)
            klient('"wybierz", "jelonek_gaju"')
            time.sleep(1.5)
            z9 = (zagroda().get("stan") or {})
            a9 = atr("PetAktywny")
            klient('"zamknij"')
            punkt("Z09", a9.get("PetAktywny") == "jelonek_gaju" and "jelonek_gaju" not in (z9.get("stoja") or [])
                  and "zoledziak" in (z9.get("stoja") or []), "aktywny %s, w zagrodzie %s" % (a9.get("PetAktywny"),
                                                                                             z9.get("stoja")))

        # ================================================================ P00 Edit
        nie_usypiaj()
        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau(KOD["edit"], "Edit"))
        zapisz("P00_edit", edit)
        grep = {}
        for q in ('"PetAktywny"', '"PetyLiczba"', 'SetAttribute%("Gold"'):
            grep[q] = call("script_grep", {"query": q}, timeout=120)["text"][:3000]
        zapisz("P00_script_grep", grep)
        if not (edit["pety"] and edit["stan"] and edit["syg"] and edit["mapa"]):
            punkt("P00", False, "brak kontenerów albo sygnału StanGracza/Sygnaly/Pety: %s" % edit)
            sys.exit(2)
        punkt("P00", None, "kontenery: %s; script_grep w wyniki.json (P00_script_grep)" % edit)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(KOD["gotowy_klient"], "Client") == "true",
                      90, 1.0)
            luau(KOD["bez_nazwy"], "Client")
            luau(KOD["test_kamera"] % "true", "Client")   # kamera do zrzutów nie chowa petów (wyłączane przed walką)
            time.sleep(3)
            # ================================================================ P01
            n = sum(len(v) for v in D["przypadki"].values())
            sa = czekaj_na(lambda: (lambda a: a if a.get("SerwerPetowGotowy") else None)(
                kont("PetyProba", ["SerwerPetowGotowy", "ZgodnoscLogikiPetow", "ZapasoweEZagrody"])), 40, 1.0) or {}
            ka = czekaj_na(lambda: (lambda a: a if a.get("KlientPetowGotowy") else None)(
                kont("PetyProba", ["KlientPetowGotowy"], "Client")), 40, 1.0) or {}
            st = kont("StanGracza", ["SerwerStanuGotowy"])
            kl = klient('"stan"')
            zapisz("P01", {"serwer": sa, "klient": ka, "stan": st, "klient_stan": kl})
            punkt("P01", sa.get("ZgodnoscLogikiPetow") == "OK %d/%d" % (n, n) and ka.get("KlientPetowGotowy") is True
                  and st.get("SerwerStanuGotowy") is True and kl.get("jajkoLokalne") is True,
                  "serwer %s | klient %s | stan %s | jajko lokalne %s" % (sa, ka, st, kl.get("jajkoLokalne")))
            # ================================================================ P02 klasa
            czekaj_na(lambda: js(KOD["wybor_klasy"], "Client").get("ekran"), 30, 1.0)
            wk = js(KOD["wybor_klasy"], "Client")
            for _ in range(10):                               # jak próba dymna: Enter, aż ekran wyboru zniknie
                if not wk.get("ekran") and wk.get("klasa") and wk.get("hud"):
                    break
                nacisnij("Return")
                time.sleep(1.5)
                wk = js(KOD["wybor_klasy"], "Client")
            if not wk.get("klasa"):
                luau(KOD["zmien_klase"] % "Warrior", "Client")
                time.sleep(2)
                wk = js(KOD["wybor_klasy"], "Client")
            punkt("P02", bool(wk.get("klasa")) and not wk.get("ekran"), "wybór klasy: %s" % wk)
            if tylko_bagno:
                proba_bagna()
            elif tylko_zagroda:
                proba_zagrody()
            else:
                # ================================================================ P03 brak Złota
                luau(KOD["ustaw_atr"] % ("Gold", "0"), "Server")
                do_inkubatora()
                # pierwsze wejście do lasu: przelot kamery (podpowiedzi E w tym czasie nie działają) — czekamy na koniec
                czekaj_na(lambda: luau(KOD["przelot"] % "LasPasGra", "Client") == "true", 6, 0.4)
                czekaj_na(lambda: luau(KOD["przelot"] % "LasPasGra", "Client") == "false", 40, 1.0)
                do_inkubatora()
                kamera(*oko_inkubatora())
                przed = atr("Gold", "PetyLiczba", "PetAktywny")
                przytrzymaj_e()
                time.sleep(0.8)
                kl = klient('"stan"')
                po = atr("Gold", "PetyLiczba", "PetAktywny")
                odm = kont("PetyProba", ["OstatniaOdmowa", "LicznikOdmow"])
                zrzut("01_brak_zlota")
                zapisz("P03", {"przed": przed, "po": po, "klient": kl, "odmowa": odm})
                punkt("P03", odm.get("OstatniaOdmowa") == "za_malo" and "Brakuje" in str(kl.get("komunikat"))
                      and po.get("Gold") == 0 and not po.get("PetyLiczba"), "komunikat %r, Gold %s, pety %s"
                      % (kl.get("komunikat"), po.get("Gold"), po.get("PetyLiczba")))
                # ================================================================ P04 kupno prawdziwym E + wyklucie
                luau(KOD["ustaw_atr"] % ("Gold", "2000"), "Server")
                time.sleep(0.6)
                kl0 = klient('"stan"')
                przytrzymaj_e()
                t0 = time.time()
                klatki = [(0.8, "02_wyklucie_trzesienie"), (1.75, "03_wyklucie_pekniecie"), (2.45, "04_wyklucie_wyskok"),
                          (4.0, "05_wyklucie_napis")]
                # ================================================================ P05 drugi E w trakcie wyklucia
                przytrzymaj_e()
                odm5 = kont("PetyProba", ["OstatniaOdmowa"])
                for t, nazwa in klatki:
                    while time.time() - t0 < t:
                        time.sleep(0.05)
                    zrzut(nazwa)
                po4 = atr("Gold", "PetyLiczba", "PetAktywny", JL["atrybuty"]["cena"])
                zak = kont("PetyProba", ["OstatniZakup", "LicznikZakupow"])
                cena0 = LP.cena(D, JL, 0)
                zapisz("P04", {"akcja_przed": kl0.get("akcjaE"), "napis": kl0.get("napisCeny"), "po": po4, "zakup": zak})
                punkt("P04", po4.get("Gold") == 2000 - cena0 and po4.get("PetyLiczba") == 1 and bool(po4.get("PetAktywny"))
                      and "Kup za %d" % cena0 in str(kl0.get("akcjaE")),
                      "E %r, napis %r → Gold %s, pet %s, następna cena %s" % (kl0.get("akcjaE"), kl0.get("napisCeny"),
                                                                           po4.get("Gold"), po4.get("PetAktywny"),
                                                                           po4.get(JL["atrybuty"]["cena"])))
                punkt("P05", odm5.get("OstatniaOdmowa") == "trwa_wyklucie" and po4.get("Gold") == 2000 - cena0,
                      "odmowa %s, Gold %s" % (odm5, po4.get("Gold")))
                time.sleep(2.5)
                kamera_zwykla()
                # ================================================================ P06 pet za graczem
                czekaj_na(lambda: klient('"stan"').get("mojPet"), 10, 0.5)
                start = js(KOD["pozycja"], "Server")
                cel = (start[0] + 40.0, start[1], start[2] - 6.0)
                call("character_navigation", {"datamodel_type": "Client", "x": cel[0], "y": cel[1], "z": cel[2]}, timeout=60)
                probki = []
                t1 = time.time()
                while time.time() - t1 < 5.0:
                    k6 = klient('"stan"')
                    probki.append((round(time.time() - t1, 1), k6.get("odleglosc"), k6.get("klip")))
                    time.sleep(0.4)
                time.sleep(2.0)
                za_graczem(11.0, 5.0, 4.0)
                koniec = klient('"stan"')
                zrzut("06_pet_za_graczem")
                kamera_zwykla()
                odl = [p[1] for p in probki if isinstance(p[1], (int, float))]
                zapisz("P06", {"probki": probki, "koniec": koniec})
                punkt("P06", bool(odl) and max(odl) <= 12 and isinstance(koniec.get("odleglosc"), (int, float))
                      and koniec["odleglosc"] <= 6 and "chod" in [p[2] for p in probki],
                      "odległość w marszu maks. %s, po zatrzymaniu %s, klipy %s" % (max(odl) if odl else None,
                                                                                  koniec.get("odleglosc"),
                                                                                  sorted({p[2] for p in probki if p[2]})))
                # ================================================================ zakupy: komplet pięciu petów (haczyk)
                pety = list(JL["pula"])
                luau(KOD["ustaw_atr"] % ("Gold", "20000"), "Server")
                for r in (0.1, 0.6, 0.8, 0.9, 0.995):             # wymuszony los: każdy pet raz (test, nie gra)
                    serwer('"zwolnij"')
                    serwer('"kup", nil, "jajko_lesne", %f' % r)
                    time.sleep(4.8)                               # klient gra wyklucie (czeka, aż się skończy)
                serwer('"zwolnij"')
                zapisz("zakupy", serwer('"stan"'))
                # ================================================================ P07 każdy pet w świecie
                baza = (gniazdo[0] + kier[0] * 9.0, gniazdo[1] + 0.5, gniazdo[2] + kier[1] * 9.0)
                bok = (-kier[1], kier[0])
                miejsca = {}
                for i, pid in enumerate(pety):
                    o = (i - 2) * 3.6
                    miejsca[pid] = (baza[0] + bok[0] * o, baza[1], baza[2] + bok[1] * o)
                    klient('"pokaz", "%s", Vector3.new(%f, %f, %f)' % (pid, miejsca[pid][0], miejsca[pid][1], miejsca[pid][2]))
                time.sleep(1.0)
                kamera((baza[0] + kier[0] * 11.0, baza[1] + 4.0, baza[2] + kier[1] * 11.0), (baza[0], baza[1] + 1.2, baza[2]))
                zrzut("07_piec_petow")
                for pid in pety:
                    m = miejsca[pid]
                    kamera((m[0] + kier[0] * 4.6 + bok[0] * 1.2, m[1] + 2.0, m[2] + kier[1] * 4.6 + bok[1] * 1.2),
                           (m[0], m[1] + 1.0, m[2]))
                    time.sleep(0.4)
                    zrzut("08_pet_%s" % pid)
                klient('"pokaz_usun"')
                punkt("P07", None, "pięć petów w świecie — zrzuty 07_piec_petow i 08_pet_<id> do obejrzenia")
                # ================================================================ P07b każdy pet idzie za graczem
                kamera_zwykla()
                idzie = {}
                for i, pid in enumerate(pety):
                    serwer('"wybierz", nil, "%s", true' % pid)    # haczyk: wybór bez podchodzenia do zagrody
                    przestaw((stoi[0] + 4, stoi[1], stoi[2] - 14 + i * 0.5), (stoi[0] + 60, 0, stoi[2] - 14))
                    time.sleep(1.5)
                    p0 = js(KOD["pozycja"], "Server")
                    call("character_navigation", {"datamodel_type": "Client", "x": p0[0] + 26, "y": p0[1], "z": p0[2]},
                         timeout=60)
                    time.sleep(0.5)
                    za_graczem()
                    k7 = klient('"stan"')
                    zrzut("08b_idzie_za_graczem_%s" % pid)
                    kamera_zwykla()
                    idzie[pid] = {"mojPet": k7.get("mojPet"), "odleglosc": k7.get("odleglosc"), "klip": k7.get("klip")}
                zapisz("P07b", idzie)
                punkt("P07b", all(v["mojPet"] == k for k, v in idzie.items()),
                      "za graczem (pet wymuszony haczykiem): %s" % ", ".join("%s %s st %s" % (k, v["odleglosc"] and round(v["odleglosc"], 1),
                                                                                          v["klip"]) for k, v in idzie.items()))
                # ================================================================ P08 wyklucie każdego peta
                kamera(*oko_inkubatora(dal=12.0, wys=5.0))
                for pid in pety:
                    klient('"wyklucie", "%s", true' % pid)
                    time.sleep(3.9)
                    zrzut("09_wyklucie_%s" % pid)
                    czekaj_na(lambda: not klient('"stan"').get("wylegaSie"), 8, 0.5)
                kamera_zwykla()
                punkt("P08", None, "wyklucie każdego peta — zrzuty 09_wyklucie_<id>")
                # ================================================================ P09 zagroda
                serwer('"wybierz", nil, "zoledziak", true')
                ez = G["zagroda_e"]
                kz = G["zagroda_kier"]
                stoi_z = stoisko_zagrody(G)
                przestaw(stoi_z, (ez[0] - kz[0] * 5, 0, ez[2] - kz[2] * 5))
                k9 = czekaj_na(lambda: (lambda k: k if k.get("petyWZagrodzie") else None)(klient('"stan"')), 15, 0.5) or {}
                kamera((ez[0] + kz[0] * 14.0, ez[1] + 9.0, ez[2] + kz[2] * 14.0), (ez[0] - kz[0] * 3.0, ez[1], ez[2] - kz[2] * 3.0))
                zrzut("10_zagroda")
                tb = G["zagroda_tablica"]
                kamera((tb[0] + kz[0] * 7.0, tb[1] + 3.6, tb[2] + kz[2] * 7.0), (tb[0], tb[1] + 3.4, tb[2]))
                zrzut("11_tablica_zagrody")
                kamera_zwykla()
                przestaw(stoi_z, (ez[0] - kz[0] * 5, 0, ez[2] - kz[2] * 5))
                time.sleep(1.0)
                przytrzymaj_e()                                   # E opiekunki (MiasteczkoBazarGra) → OknoMiejsca
                okno = czekaj_na(lambda: luau(KOD["okno_otwarte"], "Client") == "true", 5, 0.4)
                time.sleep(0.8)
                zrzut("12_okno_proba")
                zapisz("P09", {"klient": k9, "okno": bool(okno)})
                # od 25.11 (zagroda daje Rybki) na miejscach stoją tylko pety W ZAGRODZIE: tyle, ile miejsc ma poziom (na
                # starcie 2), a nie wszystkie posiadane poza aktywnym (wcześniej warunek ≥ 3)
                n9 = len((k9.get("zagroda") or {}).get("stoja") or [])
                punkt("P09", bool(okno) and n9 >= 1 and k9.get("petyWZagrodzie") == min(n9, k9.get("miejscNaMapie") or 0)
                      and (k9.get("wiersze") or 0) >= 4,
                      "pety na miejscach %s (w zagrodzie %s), wierszy %s, okno po E %s" % (
                          k9.get("petyWZagrodzie"), n9, k9.get("wiersze"), bool(okno)))
                # ================================================================ P10 wybór z okna
                # pet z premią do Złota i statystyką (D-101): Jelonek Gaju — Kryształ, +20% Siły, +5% Złota i dośw.
                PET10 = "jelonek_gaju"
                klient('"wybierz", "%s"' % PET10)
                time.sleep(1.5)
                a10 = atr("PetAktywny")
                zrzut("13_okno_po_wyborze")
                klient('"zamknij"')
                time.sleep(1.5)
                k10 = klient('"stan"')
                punkt("P10", a10.get("PetAktywny") == PET10 and k10.get("mojPet") == PET10,
                      "aktywny %s, za graczem %s" % (a10.get("PetAktywny"), k10.get("mojPet")))
                # ================================================================ P11 premia przy łupie
                przed, t11 = atr("Gold"), time.time()
                w11 = js(KOD["przyznaj"] % (100, 40), "Server")
                time.sleep(0.4)
                k11 = klient('"stan"')
                zrzut("14_premia_przy_lupie")
                po = atr("Gold")
                premia = int(math.floor(100 * LP.premia_peta(D, PET10)["zloto"] + 0.5))
                # od 25.11 zagroda nalicza Rybki także w trakcie punktu (26.11: raz +106 zamiast +105) — dopuszczalne tiki
                s11 = ((serwer('"zagroda"') or {}).get("stan") or {}).get("stawka_s") or 0
                zapas11 = int(s11 * (time.time() - t11 + D["zagroda"]["tik_s"])) + 1
                roznica11 = (po.get("Gold") or 0) - (przed.get("Gold") or 0) - 100 - premia
                # skill peta w stanie gracza (Sygnaly/Modyfikatory, źródło "pety") — gdy stan gracza ma ten sygnał
                mod11 = (serwer('"stan"') or {}).get("modyfikatory") or {}
                oczek = LP.mod_peta(D, PET10)
                mod_ok = (not mod11) or ("pety" in (mod11.get("zrodla") or []) and mod11.get("procent") == oczek.get("procent")
                                         and list(mod11.get("pasywki") or []) == oczek.get("pasywki"))
                zapisz("P11", {"wynik": w11, "przed": przed, "po": po, "klient": k11, "modyfikatory": mod11})
                punkt("P11", 0 <= roznica11 <= zapas11 and "od peta" in str(k11.get("komunikat"))
                      and mod_ok,
                      "Gold %s → %s (łup 100 + premia %d + zagroda 0…%d), napis %r, modyfikator %s" % (
                          przed.get("Gold"), po.get("Gold"), premia, zapas11, k11.get("komunikat"),
                          {k: mod11.get(k) for k in ("zrodla", "procent", "pasywki", "lup")} if mod11 else "brak sygnału"))
                # ================================================================ P12 reset w trakcie wyklucia
                do_inkubatora()
                przed = atr("Gold", "PetyLiczba")
                przytrzymaj_e()
                time.sleep(1.0)
                luau(KOD["reset"], "Server")
                time.sleep(9.0)
                czekaj_na(lambda: luau(KOD["gotowy_klient"], "Client") == "true", 20, 1.0)
                time.sleep(3.0)
                po = atr("Gold", "PetyLiczba", "PetAktywny")
                k12 = klient('"stan"')
                zapisz("P12", {"przed": przed, "po": po, "klient": k12})
                punkt("P12", po.get("PetyLiczba") == (przed.get("PetyLiczba") or 0) + 1 and not k12.get("wylegaSie")
                      and k12.get("mojPet") == po.get("PetAktywny"),
                      "pety %s → %s, wyklucie skończone %s, za graczem %s" % (przed.get("PetyLiczba"), po.get("PetyLiczba"),
                                                                             not k12.get("wylegaSie"), k12.get("mojPet")))
                # ================================================================ P13 walka z petem przy boku
                if not bez_walki:
                    luau(KOD["test_kamera"] % "false", "Client")    # walka: pet ma zniknąć jak u gracza
                    luau(KOD["test_bohater"] % ("LasPasGra", "false"), "Server")
                    pot = js(KOD["potwor_w_strefie"] % "s1", "Server")
                    if pot.get("id"):
                        p = pot["p"]
                        przestaw((p[0] - 4.0, p[1] + 3.2, p[2]), p)
                        time.sleep(1.0)
                        przed = atr("Gold")
                        luau(KOD["walcz"] % pot["id"], "Client")
                        w = czekaj_na(lambda: (lambda k: k if k.get("ukryte") else None)(klient('"stan"')), 10, 0.3) or {}
                        czeka = atr(D["atrybuty_gracza"]["czeka"])
                        time.sleep(1.5)
                        zrzut("15_walka_bez_peta")
                        czekaj_na(lambda: js(KOD["odtw"] % '"stan"', "Client").get("faza") == "odtwarzanie", 10, 0.4)
                        js(KOD["odtw"] % '"przewinDo", 1000', "Client")
                        time.sleep(2.5)
                        js(KOD["odtw"] % '"zamknij"', "Client")
                        czekaj_na(lambda: not js(KOD["klient_potworow"], "Client").get("walka"), 30, 1.0)
                        time.sleep(2.0)
                        kamera_zwykla()
                        k13 = czekaj_na(lambda: (lambda k: k if k.get("mojPet") else None)(klient('"stan"')), 10, 0.5) or {}
                        po = atr("Gold", D["atrybuty_gracza"]["czeka"])
                        zrzut("16_po_walce_pet_wraca")
                        zapisz("P13", {"w_walce": w, "czeka": czeka, "po": po, "klient_po": k13, "przed": przed})
                        punkt("P13", w.get("towarzysze") == 0 and czeka.get(D["atrybuty_gracza"]["czeka"]) is True
                              and bool(k13.get("mojPet")) and not po.get(D["atrybuty_gracza"]["czeka"]),
                              "w walce: petów %s, PetCzeka %s; po walce za graczem %s, Gold %s → %s"
                              % (w.get("towarzysze"), czeka, k13.get("mojPet"), przed.get("Gold"), po.get("Gold")))
                    else:
                        punkt("P13", None, "brak wolnego slime'a w s1 — pominięte")
                # ================================================================ P14 bez sygnału StanGracza
                do_inkubatora()
                luau(KOD["przemianuj"] % ("Pety", "PetyWylaczone"), "Server")
                time.sleep(0.3)
                przed = atr("Gold")
                serwer('"zwolnij"')
                przytrzymaj_e()
                time.sleep(0.8)
                k14 = klient('"stan"')
                odm = kont("PetyProba", ["OstatniaOdmowa"])
                po = atr("Gold")
                luau(KOD["przemianuj"] % ("PetyWylaczone", "Pety"), "Server")
                zrzut("17_bez_stanu_gracza")
                punkt("P14", odm.get("OstatniaOdmowa") == "brak_stanu" and po.get("Gold") == przed.get("Gold")
                      and "nieczynny" in str(k14.get("komunikat")), "odmowa %s, napis %r" % (odm, k14.get("komunikat")))
            # ================================================================ P15 konsola
            out = call("get_console_output")["text"]
            zle = [l for l in out.splitlines() if ("PetyProba" in l and ("Error" in l or "error" in l or "Script '" in l))
                   and not any(z in l for z in ZNANE_W_KONSOLI)]
            ostrz = [l for l in out.splitlines() if "[PetyProba]" in l]
            zapisz("P15", {"bledy": zle[:40], "nasze": ostrz[:40]})
            punkt("P15", not zle, "błędów naszych skryptów: %d, wierszy [PetyProba]: %d" % (len(zle), len(ostrz)))
        finally:
            try:
                kamera_zwykla()
            except Exception:  # noqa: BLE001
                pass
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    zle = [x for x in LISTA if x[1] == "BŁĄD"]
    log("KONIEC: %d punktów, błędów %d — %s" % (len(LISTA), len(zle), os.path.join(wyj, "lista.txt")))
    return 1 if zle else 0


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    sys.exit(main() or 0)
