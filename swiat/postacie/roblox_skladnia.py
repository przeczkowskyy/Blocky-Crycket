#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprawdzian składni Luau dla postaci z klocków — sama kompilacja w Roblox Studio (loadstring), nic nie jest wykonywane.

    python -B swiat/postacie/roblox_skladnia.py

Sprawdza: skrypty `swiat/postacie/roblox/*.luau` oraz szablony Luau osadzone w plikach Pythona `roblox_*.py`
(stałe pisane wielkimi literami, np. BUDOWA, KLIP, POZA, NAPRAWA). Znaczniki `__NAZWA__` w szablonach są dla Luau
zwykłymi nazwami, więc szablon kompiluje się bez podstawiania danych. Kod wyjścia 1, gdy coś się nie kompiluje.
Studio nie jest zmieniane: skrypt tylko prosi je o skompilowanie tekstu.
"""
import ast
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU)) if os.path.basename(TU) == "postacie" else None


def szablony_z_pythona(sciezka):
    """Stałe modułu wyglądające na Luau: NAZWA = r'''…''' albo sklejenie stałych (np. WSTEP + r'''…''')."""
    with open(sciezka, encoding="utf-8") as f:
        drzewo = ast.parse(f.read())
    stale, wynik = {}, []

    def wartosc(w):
        if isinstance(w, ast.Constant) and isinstance(w.value, str):
            return w.value
        if isinstance(w, ast.Name) and w.id in stale:
            return stale[w.id]
        if isinstance(w, ast.BinOp) and isinstance(w.op, ast.Add):
            lewa, prawa = wartosc(w.left), wartosc(w.right)
            if lewa is not None and prawa is not None:
                return lewa + prawa
        return None

    for wezel in drzewo.body:
        if isinstance(wezel, ast.Assign) and len(wezel.targets) == 1 and isinstance(wezel.targets[0], ast.Name):
            nazwa = wezel.targets[0].id
            tekst = wartosc(wezel.value) if nazwa.isupper() else None
            if tekst is not None:
                stale[nazwa] = tekst
                if chr(10) in tekst and ("local " in tekst or "return " in tekst):
                    wynik.append(("%s:%s" % (os.path.basename(sciezka), nazwa), tekst))
    return wynik


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    katalog = sys.argv[1] if len(sys.argv) > 1 else TU
    repo = sys.argv[2] if len(sys.argv) > 2 else REPO
    sys.path.insert(0, os.path.join(repo, "tools"))
    from studio_mcp import StudioMCP, first_studio_id

    zrodla = []
    for p in sorted(glob.glob(os.path.join(katalog, "roblox", "*.luau"))):
        with open(p, encoding="utf-8") as f:
            zrodla.append((os.path.basename(p), f.read()))
    for p in sorted(glob.glob(os.path.join(katalog, "roblox_*.py"))):
        if os.path.basename(p) == os.path.basename(__file__):
            continue
        zrodla += szablony_z_pythona(p)
    if not zrodla:
        sys.exit("Nie znaleziono niczego do sprawdzenia w %s" % katalog)
    kod = ("local Z = {" + ",".join("{%s,%s}" % (json.dumps(n, ensure_ascii=False), json.dumps(s, ensure_ascii=False))
                                   for n, s in zrodla) + "}\n" + '''
local out = {}
for _, z in Z do
	local fn, err = loadstring(z[2], z[1])
	table.insert(out, (fn and "OK    " or "BŁĄD  ") .. z[1] .. (fn and "" or (" — " .. tostring(err))))
end
return table.concat(out, "\\n")
''')
    with StudioMCP() as s:
        sid = first_studio_id(s)
        if not sid:
            sys.exit("Roblox Studio nie jest podłączone.")
        r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
    tekst = r["text"] or ""
    print(tekst)
    if r["is_error"] or "BŁĄD" in tekst:
        sys.exit(1)
    print("składnia: %d z %d bez błędów" % (tekst.count("OK    "), len(zrodla)))


if __name__ == "__main__":
    main()
