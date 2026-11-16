#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zaciemnienie ekranu na czas pracy agentów w Roblox Studio (tylko Windows).

    python -B tools/ekran_zaciemnienie.py                 # do 07:00 rano
    python -B tools/ekran_zaciemnienie.py --do 06:30      # do podanej godziny
    python -B tools/ekran_zaciemnienie.py --godziny 3     # przez 3 godziny
    python -B tools/ekran_zaciemnienie.py --stop          # zdejmij zaciemnienie (z innego okna albo zdalnie)

Po co: przy uśpionym monitorze Studio przestaje rysować — zrzuty ekranu MCP czekają bez końca, a w trybie Play nie
przychodzi RenderStepped (sprawdzone 14.11.2026). W nocy monitor ma jednak nie świecić. Ten skrypt zostawia ekran
włączony dla systemu, ale przykrywa wszystkie monitory prawie nieprzezroczystym czarnym oknem „zawsze na wierzchu”:
- okno przepuszcza kliknięcia i nie zabiera klawiatury (testy sterujące Studio działają pod spodem),
- Studio dalej rysuje, bo nie jest zminimalizowane, a okno nad nim jest warstwowe (nie liczy się jako zasłonięcie),
- proces trzyma też ekran i komputer przed uśpieniem (SetThreadExecutionState), dopóki działa.

Jak zdjąć zaciemnienie przy komputerze: przytrzymaj klawisz Esc przez 2 sekundy. Samo znika o ustawionej godzinie.
Podświetlenie matrycy zostaje włączone (czerń świeci słabo) — pełną ciemność daje tylko wyłącznik monitora.
"""
import argparse
import ctypes
import datetime
import os
import sys
import tempfile
import time

sys.dont_write_bytecode = True
PLIK_STOP = os.path.join(tempfile.gettempdir(), "bc_ekran_zaciemnienie.stop")
ESC_SEKUND = 2.0


def _koniec_z_argumentow(a):
    teraz = datetime.datetime.now()
    if a.godziny:
        return teraz + datetime.timedelta(hours=a.godziny)
    g, m = (int(x) for x in a.do.split(":"))
    cel = teraz.replace(hour=g, minute=m, second=0, microsecond=0)
    if cel <= teraz:
        cel += datetime.timedelta(days=1)
    return cel


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Czarne okno na wszystkie monitory; Studio rysuje pod spodem")
    ap.add_argument("--do", default="07:00", help="godzina zdjęcia zaciemnienia (GG:MM), domyślnie 07:00")
    ap.add_argument("--godziny", type=float, default=0.0, help="zamiast --do: ile godzin ma trwać")
    ap.add_argument("--krycie", type=float, default=0.985, help="krycie okna 0–0,995 (poniżej 1, żeby nie było zasłonięciem)")
    ap.add_argument("--stop", action="store_true", help="zdejmij działające zaciemnienie")
    a = ap.parse_args()
    if a.stop:
        open(PLIK_STOP, "w").close()
        print("Wysłano sygnał zdjęcia zaciemnienia.")
        return
    if os.name != "nt":
        sys.exit("Tylko Windows.")
    try:
        os.remove(PLIK_STOP)
    except OSError:
        pass
    koniec = _koniec_z_argumentow(a)
    import tkinter

    u, k = ctypes.windll.user32, ctypes.windll.kernel32
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)        # rozmiary w prawdziwych pikselach
    except Exception:  # noqa: BLE001
        pass
    k.SetThreadExecutionState(0x80000000 | 0x00000002 | 0x00000001)   # ekran i system nie zasypiają
    x, y = u.GetSystemMetrics(76), u.GetSystemMetrics(77)             # początek pulpitu wirtualnego
    w, h = u.GetSystemMetrics(78), u.GetSystemMetrics(79)             # rozmiar wszystkich monitorów razem
    okno = tkinter.Tk()
    okno.overrideredirect(True)
    okno.configure(background="black", cursor="none")
    okno.geometry("%dx%d+%d+%d" % (w, h, x, y))                # „+-1920” = ujemna współrzędna (monitor po lewej)
    okno.attributes("-topmost", True)
    okno.attributes("-alpha", max(0.0, min(0.995, a.krycie)))
    okno.update_idletasks()
    hwnd = u.GetParent(okno.winfo_id()) or okno.winfo_id()
    GWL_EXSTYLE = -20
    styl = u.GetWindowLongW(hwnd, GWL_EXSTYLE)
    # warstwowe + przepuszcza mysz + nie aktywuje się + bez przycisku na pasku zadań
    u.SetWindowLongW(hwnd, GWL_EXSTYLE, styl | 0x00080000 | 0x00000020 | 0x08000000 | 0x00000080)
    stan = {"esc_od": None}

    def tyk():
        teraz = time.time()
        if os.path.exists(PLIK_STOP) or datetime.datetime.now() >= koniec:
            okno.destroy()
            return
        if u.GetAsyncKeyState(0x1B) & 0x8000:                   # Esc trzymany
            stan["esc_od"] = stan["esc_od"] or teraz
            if teraz - stan["esc_od"] >= ESC_SEKUND:
                okno.destroy()
                return
        else:
            stan["esc_od"] = None
        okno.attributes("-topmost", True)                       # gdyby coś wskoczyło nad okno
        okno.after(200, tyk)

    print("Zaciemnienie włączone do %s. Zdjęcie: przytrzymaj Esc 2 s albo `--stop`." % koniec.strftime("%H:%M"), flush=True)
    okno.after(200, tyk)
    okno.mainloop()
    k.SetThreadExecutionState(0x80000000)
    # pliku sygnału nie usuwamy tutaj (mogą działać dwa okna naraz) — czyści go następne uruchomienie
    print("Zaciemnienie zdjęte.", flush=True)


if __name__ == "__main__":
    main()
