#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Okna Roblox Studio w Windows: sprawdza, czy są zminimalizowane, i w razie potrzeby je przywraca.

    python -B tools/studio_okno.py            # pokaż stan okien Studio
    python -B tools/studio_okno.py --przywroc # przywróć zminimalizowane okna (bez zabierania klawiatury)

Po co: zminimalizowane okno Studio nie rysuje świata 3D, więc zrzuty ekranu (screen_capture) wychodzą czarne —
widać na nich tylko interfejs. Przed serią zrzutów albo nagraniem filmu uruchom to z --przywroc.
Kod wyjścia: 0 — wszystkie okna są widoczne (albo zostały przywrócone); 1 — nie ma okna Studio; 2 — inny system.
"""
import argparse
import ctypes
import sys

SW_SHOWNOACTIVATE = 4


def okna_studio():
    """Lista (uchwyt, tytuł, zminimalizowane) głównych okien procesu RobloxStudioBeta.exe."""
    u = ctypes.windll.user32
    k = ctypes.windll.kernel32
    wynik = []
    typ = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def jedno(h, _):
        if not u.IsWindowVisible(h) or u.GetWindow(h, 4):  # 4 = GW_OWNER: pomijamy okna podrzędne
            return True
        n = u.GetWindowTextLengthW(h)
        if n == 0:
            return True
        b = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, b, n + 1)
        pid = ctypes.c_ulong()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        p = k.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not p:
            return True
        try:
            sc = ctypes.create_unicode_buffer(1024)
            dl = ctypes.c_ulong(1024)
            if k.QueryFullProcessImageNameW(p, 0, sc, ctypes.byref(dl)) and sc.value.lower().endswith("robloxstudiobeta.exe"):
                wynik.append((h, b.value, bool(u.IsIconic(h))))
        finally:
            k.CloseHandle(p)
        return True

    u.EnumWindows(typ(jedno), 0)
    return wynik


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Stan okien Roblox Studio (Windows)")
    ap.add_argument("--przywroc", action="store_true", help="przywróć zminimalizowane okna")
    a = ap.parse_args()
    if sys.platform != "win32":
        print("To narzędzie działa tylko w Windows.")
        sys.exit(2)
    okna = okna_studio()
    if not okna:
        print("Nie ma okna Roblox Studio.")
        sys.exit(1)
    for h, tytul, zmin in okna:
        if zmin and a.przywroc:
            ctypes.windll.user32.ShowWindow(ctypes.c_void_p(h), SW_SHOWNOACTIVATE)
            print("przywrócone: %s" % tytul)
        else:
            print("%s: %s" % ("ZMINIMALIZOWANE" if zmin else "widoczne", tytul))


if __name__ == "__main__":
    main()
