# -*- coding: utf-8 -*-
"""Regresja całości w Roblox Studio (tryb Play): puszcza po kolei próby wszystkich pakietów gry i zapisuje podsumowanie.

    python -B swiat/przejscie_gry/regresja_calosci.py <folder wyników POZA repo> [nazwa,nazwa,…] [plik podsumowania]

Warunki: Studio otwarte w trybie Edit, wszystkie kontenery zbudowane (każdy pakiet: swiat/<pakiet>/zbuduj.py), nikt nie
gra w tym oknie. Okno Studio jest wysuwane na wierzch (pomiary czasu klatki), więc nie puszczać, gdy ktoś pracuje przy
komputerze. Całość trwa ok. godziny. Próby idą bez zrzutów do repozytorium (--bez-zrzutow tam, gdzie próba to umie);
logi i wyniki z nazwą konta trafiają do podanego folderu — dlatego musi on leżeć poza repozytorium.

Zapis postępu (D-110): każda próba włącza Play przez tools/studio_mcp.py, więc przez znacznik próby z tools/zapis_prob.py —
serwer stanu gracza nie czyta i nie pisze wtedy prawdziwego zapisu człowieka (gracz zaczyna świeży); próba „zapis” pracuje
na osobnym magazynie próby.

Drugi argument ogranicza listę do podanych nazw (np. "proba dymna,dzungla,kowal"); pusty = wszystkie.
Po każdej próbie do podsumowania idzie ogon jej wyjścia; pełny log jest w <folder>/<nazwa>.log. Kod wyjścia próby
0 nie znaczy „wszystko OK” — czytaj wiersze z „BŁĄD” i „?”.
"""
import datetime
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# 26.11.2026 (sprzątanie mapy): bez prób „stary las” (Workspace/LasPotwory, BiomLas) i „rasy” (Workspace/RasyProba) —
# tych kontenerów nie ma już w miejscu (tools/studio/sprzatanie_mapy.py); ich próby zostają w pakietach na wypadek powrotu
PROBY = [
    ("okno na wierzch", ["tools/studio_okno.py", "--na-wierzch"], 60),
    ("proba dymna", ["swiat/przejscie_gry/proba_dymna.py", "{w}/dymna"], 900),
    ("las-pas", ["swiat/las_pas_gra/testy/proba_play.py", "{w}/las_pas", "--bez-zrzutow"], 1500),
    ("bagno", ["swiat/bagno_pas_gra/testy/proba_play.py", "{w}/bagno", "--bez-zrzutow"], 1800),
    ("dzungla", ["swiat/dzungla_pas_gra/testy/proba_play.py", "{w}/dzungla", "--bez-zrzutow"], 1800),
    ("stan gracza", ["swiat/stan_gracza/testy/proba_play.py", "{w}/stan", "--bez-m6", "--bez-zrzutow"], 1500),
    ("pety", ["swiat/pety_proba/testy/proba_play.py", "{w}/pety", "--bez-zrzutow"], 1500),
    ("pety bagno", ["swiat/pety_proba/testy/proba_play.py", "{w}/pety_bagno", "--bagno", "--bez-zrzutow"], 1500),
    ("pety dzungla", ["swiat/pety_proba/testy/proba_play.py", "{w}/pety_dzungla", "--dzungla", "--bez-zrzutow"], 1500),
    ("kowal", ["swiat/kowal_proba/testy/proba_play.py", "--bez-zrzutow"], 1200),
    ("stroje", ["swiat/stroje_proba/testy/proba_play.py", "--bez-zrzutow"], 1500),
    ("trening", ["swiat/trening_proba/testy/proba_play.py", "{w}/trening", "--bez-zrzutow"], 1200),
    ("bohater", ["swiat/bohater_swiat/testy/proba_play.py", "{w}/bohater", "--bez-zrzutow"], 1200),
    ("cutscenka", ["swiat/cutscenka_biomu/testy/proba_play.py", "{w}/cutscenka", "--bez-zrzutow"], 900),
    ("npc", ["swiat/npc_gra/testy/proba_play.py", "{w}/npc", "--bez-zrzutow"], 600),
    ("sklep", ["swiat/sklep_proba/testy/proba_play.py", "--bez-zrzutow", "--wynik", "{w}/sklep/wynik_play.json"], 1200),
    ("bazar", ["swiat/miasteczko_bazar_gra/testy/proba_play.py", "{w}/bazar", "--bez-zrzutow"], 1200),
    ("chmury", ["swiat/teleport_chmury/testy/proba_play.py", "{w}/chmury"], 1200),
    ("dzwiek", ["swiat/dzwiek_gra/testy/proba_play.py", "{w}/dzwiek"], 900),
    ("walka szybko", ["swiat/test_walki2/testy/test_walki_play.py", "--szybko"], 1500),
    ("walka v3", ["swiat/test_walki2/testy/test_v3_play.py", "--bez-zrzutow"], 1800),
    ("walka poprawki", ["swiat/test_walki2/testy/test_poprawek_play.py"], 1500),
    # 19.11.2026 (D-110): zapis postępu — na magazynie próby (…_Studio_Proba), nie na zapisie człowieka
    ("zapis", ["swiat/stan_gracza/testy/proba_zapisu.py", "{w}/zapis"], 1200),
]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    wyj = os.path.abspath(argv[0])
    if os.path.commonpath([wyj, REPO]) == REPO:
        print("BŁĄD: folder wyników musi leżeć poza repozytorium (logi mogą zawierać nazwę konta).")
        return 2
    tylko = set(argv[1].split(",")) if len(argv) > 1 and argv[1] else None
    plik = os.path.join(wyj, argv[2] if len(argv) > 2 else "podsumowanie.txt")
    os.makedirs(wyj, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    with open(plik, "w", encoding="utf-8") as f:
        f.write("Regresja całości — start %s\n" % datetime.datetime.now().strftime("%H:%M"))
    w = wyj.replace("\\", "/")
    for nazwa, arg, limit in PROBY:
        if tylko and nazwa not in tylko and nazwa != "okno na wierzch":
            continue
        arg = [a.replace("{w}", w) for a in arg]
        for a in arg:
            if a.startswith(w):
                # plik wyniku (np. --wynik …/wynik_play.json): tworzymy tylko jego folder, nie folder o nazwie pliku
                os.makedirs(os.path.dirname(a) if a.lower().endswith(".json") else a, exist_ok=True)
        t0 = datetime.datetime.now()
        try:
            r = subprocess.run([sys.executable, "-B"] + arg, cwd=REPO, env=env, capture_output=True, timeout=limit)
            kod, tekst = r.returncode, (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            kod, tekst = "LIMIT", ((e.stdout or b"") + b"\n" + (e.stderr or b"")).decode("utf-8", "replace")
        with open(os.path.join(wyj, nazwa.replace(" ", "_") + ".log"), "w", encoding="utf-8") as f:
            f.write(tekst)
        linie = [l for l in tekst.splitlines() if l.strip()]
        with open(plik, "a", encoding="utf-8") as f:
            f.write("\n=== %s · kod %s · %s–%s\n" % (nazwa, kod, t0.strftime("%H:%M"), datetime.datetime.now().strftime("%H:%M")))
            for l in linie[-14:]:
                f.write("  " + l[:230] + "\n")
    # na koniec: Studio ma być w trybie Edit
    try:
        r = subprocess.run([sys.executable, "-B", "tools/studio_mcp.py", "studios"], cwd=REPO, env=env, capture_output=True, timeout=60)
        tryb = [l.strip() for l in r.stdout.decode("utf-8", "replace").splitlines() if '"mode"' in l]
    except Exception as e:  # noqa: BLE001
        tryb = ["błąd: %s" % e]
    with open(plik, "a", encoding="utf-8") as f:
        f.write("\nKoniec %s · Studio: %s\n" % (datetime.datetime.now().strftime("%H:%M"), " ".join(tryb)))
    print("regresja skończona: %s" % plik)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
