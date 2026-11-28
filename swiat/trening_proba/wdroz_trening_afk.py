# -*- coding: utf-8 -*-
"""Wdrożenie trzech skryptów treningu AFK Pawła do otwartego Studio (bez Rojo) — z kontrolą, że w Studio stoi wersja
sprzed zmiany z 27.11.2026 (duża sala, sklep trenera; wcześniej 26.11: okno trenera, bez tabliczek). Inna wersja
w Studio = STOP: ktoś zmienił skrypt w Studio
i zmiany trzeba najpierw zebrać, nie nadpisywać.

    python -B swiat/trening_proba/wdroz_trening_afk.py --sucho      # tylko porównanie (niczego nie zmienia)
    python -B swiat/trening_proba/wdroz_trening_afk.py              # porównanie, a gdy wszystkie trzy = wersja sprzed
                                                                     # zmiany: podmiana Source, odczyt kontrolny
    [--studio <id>]

Skrypty (istniejące instancje — narzędzie ich nie tworzy, nie usuwa i nie przenosi; zmienia tylko Source):
    src/server/TreningAFK.server.luau        → ServerScriptService.Server.TreningAFK          (Script)
    src/client/TreningAFKClient.client.luau  → StarterPlayer.StarterPlayerScripts.Client.TreningAFKClient (LocalScript)
    src/shared/TreningAFKDane.luau           → ReplicatedStorage.Shared.TreningAFKDane          (ModuleScript)
Wersja sprzed zmiany = bloby git zapisane niżej (PRZED). Porównanie bez różnic końców wierszy i końcowych spacji.
Wynik: 0 = wdrożone (albo przy --sucho: można wdrażać / już wdrożone), 3 = STOP (inna wersja w Studio albo brak
instancji), 1 = błąd Studio. Jedna zmiana w historii („Trening AFK: kości Szczęścia, bieżnia i sztanga”, Ctrl+Z ją cofa).
Tylko tryb Edit.
"""
import json
import os
import subprocess
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

SKRYPTY = [
    # (plik w repo, ścieżka w Studio, klasa, blob sprzed zmiany 27.11.2026 ok. 20:00 (kości Szczęścia, bieżnia i sztanga
    # na awatarze AnimationConstraint) = main 567ba18; wcześniej 27.11 wieczorem (limit treningu, BALANS_2711.md) = main
    # 12f2445: eed1fe4…, 16802ca…, 88c983b…; 27.11 rano (duża sala, sklep): 87cda65…, c123413…, 7cc45dd…; 26.11:
    # 6c8c2b4…, c3a0a35…, 4a5e13f…)
    ("src/server/TreningAFK.server.luau", ("ServerScriptService", "Server", "TreningAFK"), "Script",
     "992bb1293e5feb4bc864040a4810eed5acbf7ae6"),
    ("src/client/TreningAFKClient.client.luau", ("StarterPlayer", "StarterPlayerScripts", "Client", "TreningAFKClient"),
     "LocalScript", "2b28635985ae62c950d052eea54b9628e6581552"),
    ("src/shared/TreningAFKDane.luau", ("ReplicatedStorage", "Shared", "TreningAFKDane"), "ModuleScript",
     "538832adb2f18fe69f0bae0cbf5e7971aaf2ac98"),
]
KONIEC = "]======]"


def norm(t):
    return "\n".join(w.rstrip() for w in t.replace("\r\n", "\n").replace("\r", "\n").split("\n")).rstrip() + "\n"


def blob(h):
    r = subprocess.run(["git", "cat-file", "-p", h], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        sys.exit("brak blobu %s w repozytorium (git cat-file)" % h)
    return r.stdout.decode("utf-8")


def sciezka_lua(czesci):
    s = 'game:GetService("%s")' % czesci[0]
    for c in czesci[1:]:
        s = "(%s and %s:FindFirstChild(\"%s\"))" % (s, s, c)
    return s


def pierwsza_roznica(a, b):
    la, lb = a.split("\n"), b.split("\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else "<koniec>"
        y = lb[i] if i < len(lb) else "<koniec>"
        if x != y:
            return "wiersz %d: Studio „%s” ≠ „%s”" % (i + 1, x.strip()[:70], y.strip()[:70])
    return "bez różnic"


def main(argv):
    sucho = "--sucho" in argv
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP  # noqa: E402

    nowe = {p: open(os.path.join(REPO, p), encoding="utf-8").read() for p, _, _, _ in SKRYPTY}
    stare = {p: blob(b) for p, _, _, b in SKRYPTY}
    for p in nowe:
        if KONIEC in nowe[p]:
            sys.exit("%s zawiera %s — zmień ogranicznik napisu w narzędziu" % (p, KONIEC))
    # 27.11.2026: każdy skrypt osobnym odczytem — razem (ok. 103 tys. znaków) przekraczały limit odpowiedzi execute_luau
    odczyty = [('local H = game:GetService("HttpService") local o = {} '
                'do local s = %s o["%s"] = s and { klasa = s.ClassName, zrodlo = s.Source } or false end '
                'return H:JSONEncode(o)') % (sciezka_lua(sc), p) for p, sc, _, _ in SKRYPTY]
    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def luau(kod):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=180)
            if r["is_error"]:
                print("BŁĄD Studio:", r["text"][:400])
                sys.exit(1)
            return r["text"].strip()

        def czytaj():
            w_ = {}
            for kod_ in odczyty:
                w_.update(json.loads(luau(kod_)))
            return w_

        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            sys.exit("Studio nie jest w trybie Edit — wdrożenie tylko w Edit")
        w = czytaj()
        stan, stop = {}, False
        for p, sc, klasa, _ in SKRYPTY:
            x = w.get(p)
            if not x:
                stan[p] = "BRAK instancji %s" % ".".join(sc)
                stop = True
            elif x["klasa"] != klasa:
                stan[p] = "zła klasa %s (oczekiwana %s)" % (x["klasa"], klasa)
                stop = True
            elif norm(x["zrodlo"]) == norm(nowe[p]):
                stan[p] = "już wdrożone (Studio = repo)"
            elif norm(x["zrodlo"]) == norm(stare[p]):
                stan[p] = "wersja sprzed zmiany — do podmiany"
            else:
                stan[p] = "INNA wersja niż sprzed zmiany (%s)" % pierwsza_roznica(norm(x["zrodlo"]), norm(stare[p]))
                stop = True
            print("  %-42s %s" % (p, stan[p]))
        if stop:
            print("STOP: w Studio nie ma wersji sprzed zmiany — niczego nie podmieniam (zbierz zmiany ze Studio i porównaj)")
            return 3
        do_podmiany = [x for x in SKRYPTY if stan[x[0]].startswith("wersja sprzed")]
        if not do_podmiany:
            print("WYNIK: wszystkie trzy już wdrożone")
            return 0
        if sucho:
            print("WYNIK (--sucho): można wdrażać %d skrypt(y)" % len(do_podmiany))
            return 0
        kod = ['local CHS = game:GetService("ChangeHistoryService")',
               'local rec = CHS:TryBeginRecording("Trening AFK: kości Szczęścia, bieżnia i sztanga")', "local n = 0"]
        for p, sc, _, _ in do_podmiany:
            kod.append("do local s = %s if s then s.Source = [======[%s%s n += 1 end end" % (
                sciezka_lua(sc), "\n" + nowe[p] if nowe[p].startswith("\n") else nowe[p], KONIEC))
        kod.append("if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end return tostring(n)")
        print("podmienione:", luau("\n".join(kod)))
        w = czytaj()
        zle = [p for p, _, _, _ in SKRYPTY if not w.get(p) or norm(w[p]["zrodlo"]) != norm(nowe[p])]
        if zle:
            print("BŁĄD: po podmianie Studio ≠ repo:", zle)
            return 1
        print("WYNIK: wdrożone — Studio = repo dla trzech skryptów (zapis miejsca: Ctrl+S w Studio)")
        return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
