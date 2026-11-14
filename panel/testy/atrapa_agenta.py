# -*- coding: utf-8 -*-
"""Atrapa programu Claude Code dla serwerów testowych panelu (nie test — pomocnik).

`przygotuj(katalog)` tworzy w katalogu tymczasowym:
    claude.cmd                                         (skrót jak z npm; sam wypisuje tylko wersję atrapy)
    node_modules/@anthropic-ai/claude-code/cli.js      (kopia testy/atrapa_agenta.cjs)
i zwraca ścieżkę do claude.cmd. Serwer testowy dostaje ją w konfiguracji lokalnej jako `agent.sciezka`, więc panel
nigdy nie znajdzie prawdziwego programu `claude` (subskrypcja właściciela). Panel zamienia skrót .cmd na
`node cli.js` (bc/agent.py, _program_argv) — przebieg wymaga Node; bez Node przebieg kończy się błędem, ale nadal nie
uruchamia prawdziwego agenta.
"""
import os
import shutil

TUTAJ = os.path.dirname(os.path.abspath(__file__))


def przygotuj(katalog):
    cli = os.path.join(katalog, "node_modules", "@anthropic-ai", "claude-code")
    os.makedirs(cli, exist_ok=True)
    shutil.copyfile(os.path.join(TUTAJ, "atrapa_agenta.cjs"), os.path.join(cli, "cli.js"))
    sciezka = os.path.join(katalog, "claude.cmd")
    with open(sciezka, "w", encoding="ascii", newline="\r\n") as f:
        f.write("@echo off\necho 0.0.0-atrapa (atrapa testowa)\n")
    return sciezka
