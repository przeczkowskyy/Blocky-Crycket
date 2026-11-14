# Testy panelu: z katalogu panel/ uruchom  python -m unittest discover -s testy -t .
#
# Ten plik importuje się PRZED modułami testów, więc tu (a nie w pojedynczych testach) ustawiamy katalogi zastępcze:
# bc/rdzen.py czyta BC_PANEL_RUNTIME i BC_PANEL_DANE raz, przy pierwszym imporcie. Bez tego pierwszy test, który
# zaimportuje bc.rdzen, ustaliłby dane lokalne na prawdziwe %LOCALAPPDATA%\BlockyCrycket\panel (i prawdziwą
# konfigurację lokalną), a dane wspólne na prawdziwe panel/dane. Katalog tymczasowy znika po testach.
import atexit
import os
import shutil
import tempfile

if not os.environ.get("BC_PANEL_RUNTIME") or not os.environ.get("BC_PANEL_DANE"):
    _TMP = tempfile.mkdtemp(prefix="bc_panel_testy_")
    os.environ.setdefault("BC_PANEL_RUNTIME", os.path.join(_TMP, "runtime"))
    os.environ.setdefault("BC_PANEL_DANE", os.path.join(_TMP, "dane"))
    atexit.register(shutil.rmtree, _TMP, True)

# Git w testach: serwery testowe startują w katalogu PRAWDZIWEGO repozytorium (cwd=REPO), a zmienne środowiskowe
# przechodzą do ich procesów. BC_GIT_AUTO=0 — stała synchronizacja (bc/gitsync.py) nie startuje; BC_GIT_BEZ_SIECI=1 —
# GET /api/git/stan nie robi `git fetch` w tle. Testy synchronizacji wołają funkcje jawnie z repo= z katalogu
# tymczasowego (testy/test_gitsync_auto.py), a gitsync ma dodatkowo bezpiecznik na prawdziwe repozytorium.
os.environ["BC_GIT_AUTO"] = "0"
os.environ["BC_GIT_BEZ_SIECI"] = "1"
