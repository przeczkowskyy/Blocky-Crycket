# -*- coding: utf-8 -*-
"""Czuwanie ekranu na czas testów w Studio (tylko Windows, tylko na czas życia procesu testu).

Zrzuty ekranu i RenderStepped w trybie Play działają tylko wtedy, gdy Studio naprawdę rysuje obraz. Gdy komputer
stoi bez człowieka, system wygasza monitor i Studio przestaje rysować: narzędzie zrzutu MCP czeka bez końca, a w Play
RenderStepped nie przychodzi (sprawdzone 14.11.2026). `nie_usypiaj()` ustawia SetThreadExecutionState
(ES_CONTINUOUS | ES_DISPLAY_REQUIRED) — ważne tylko, dopóki działa ten proces — i budzi ekran ruchem myszy
o 1 piksel tam i z powrotem. Nic nie zostaje po zakończeniu testu.
"""
import os
import sys


def nie_usypiaj():
    if os.name != "nt":
        return False
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000002 | 0x00000001)
        u = ctypes.windll.user32
        u.mouse_event(0x0001, 1, 0, 0, 0)          # ruch o 1 piksel w prawo…
        u.mouse_event(0x0001, -1, 0, 0, 0)          # …i z powrotem
        return True
    except Exception as e:  # noqa: BLE001
        print("czuwanie: %s" % e, file=sys.stderr)
        return False
