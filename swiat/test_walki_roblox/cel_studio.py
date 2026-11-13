# -*- coding: utf-8 -*-
"""Wybór okna Roblox Studio dla zbuduj.py i testów — tak, żeby nigdy nie trafić w cudze miejsce.

Zasady:
- bez --studio: musi być otwarte DOKŁADNIE jedno okno Studio, inaczej przerywamy i wypisujemy listę;
- z --studio: okno o tym id musi istnieć;
- w obu przypadkach otwarte miejsce musi mieć placeId gry (MIEJSCE); inne miejsce → przerywamy.
"""
import sys

MIEJSCE = 129485428021967  # placeId miejsca gry w Team Create


def _id(okno):
    for k in ("id", "studio_id", "studioId"):
        if okno.get(k):
            return okno[k]
    return None


def _opis(okno):
    return "  %s  %s" % (_id(okno), okno.get("name") or "?")


def wybierz_studio(sesja, studio_id=None, miejsce=MIEJSCE):
    """Zwraca studio_id właściwego okna albo kończy program (sys.exit) z wyjaśnieniem."""
    okna = [o for o in sesja.studios() if isinstance(o, dict) and _id(o)]
    if not okna:
        sys.exit("Roblox Studio nie jest podłączone (Assistant → Manage MCP Servers → Enable Studio as MCP server).")
    if studio_id:
        pasujace = [o for o in okna if _id(o) == studio_id]
        if not pasujace:
            sys.exit("Nie ma okna Studio o id %s. Otwarte okna:\n%s" % (studio_id, "\n".join(_opis(o) for o in okna)))
    else:
        if len(okna) > 1:
            sys.exit("Otwartych okien Studio: %d — wskaż właściwe przez --studio <id>:\n%s"
                     % (len(okna), "\n".join(_opis(o) for o in okna)))
        pasujace = okna
    okno = pasujace[0]
    try:
        place = int(okno.get("placeId"))
    except (TypeError, ValueError):
        place = None
    if place != miejsce:
        sys.exit("Okno %s to inne miejsce (%s, placeId %s), a nie miejsce gry (placeId %d) — przerywam."
                 % (_id(okno), okno.get("name") or "?", okno.get("placeId"), miejsce))
    return _id(okno)
