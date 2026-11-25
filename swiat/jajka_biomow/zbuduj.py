# -*- coding: utf-8 -*-
"""Jajka biomów (Bagno, Dżungla) na wzór leśnego jaja Pawła — całość jednym poleceniem:

    python -B swiat/jajka_biomow/zbuduj.py [--bez-tekstur] [--bez-renderu] [--klatki <folder roboczy>]

1. tekstury.py      -> tekstury/<biom>_jajo_kolor.png, _jajo_blask.png, _ozdoby.png
2. blender_jajko.py -> modele/jajko_<biom>.glb, .fbx, _statystyki.json (Blender bez okna, jedna instancja naraz:
                       blokada z swiat/biblioteka/podglad.py)
3. plansze          -> podglad/jajko_<biom>_4strony.jpg, podglad/jajka_wyklucie.jpg, podglad/jajka_zestawienie.jpg
Rendery pośrednie idą do folderu tymczasowego (poza repo).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, REPO)
from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402

BIOMY = ("bagno", "dzungla")
NAZWY = {"bagno": "Jajko Bagna", "dzungla": "Jajko Dżungli"}


def log(*a):
    print("JAJKA BIOMÓW |", *a, flush=True)


def blender(*arg):
    blok = zajmij_blender()
    try:
        t0 = time.time()
        r = subprocess.run([blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python",
                            os.path.join(TU, "blender_jajko.py"), "--"] + list(arg), capture_output=True, cwd=REPO)
        tekst = (r.stdout + r.stderr).decode("utf-8", "replace")
        if r.returncode != 0:
            print(tekst[-3000:])
            raise SystemExit("blender_jajko.py: błąd")
        log("blender %s: %.0f s" % (" ".join(a for a in arg if not os.path.isabs(a)), time.time() - t0))
    finally:
        zwolnij_blender(blok)


ZAKAZANE = [rb"[A-Za-z]:\\Users\\", rb"[A-Za-z]:/Users/", rb"AppData", rb"\\Temp\\"]


def napraw_fbx(sciezka):
    """Bezwzględne ścieżki tekstur w binarnym FBX -> względne tej samej długości (jak napraw_fbx
    w swiat/postacie/przebuduj.py). Tekstury są osadzone w pliku; repo jest publiczne."""
    b = open(sciezka, "rb").read()
    wzor = re.compile(rb"[A-Za-z]:\\[ -~]*?\\(?=[A-Za-z0-9_.]+\\[A-Za-z0-9_]+\.png)")

    def zamien(m):
        n = len(m.group())
        return b".\\" * (n // 2) if n % 2 == 0 else b".\\\\" + b".\\" * ((n - 3) // 2)
    nb = wzor.sub(zamien, b)
    assert len(nb) == len(b)
    if nb != b:
        open(sciezka, "wb").write(nb)


def slady_dysku():
    zle = []
    for dp, _, fs in os.walk(TU):
        for f in fs:
            if f.endswith((".png", ".jpg", ".pyc")) or f == "zbuduj.py":   # zbuduj.py ma wzorce w ZAKAZANE
                continue
            b = open(os.path.join(dp, f), "rb").read()
            if any(re.search(w, b) for w in ZAKAZANE):
                zle.append(os.path.relpath(os.path.join(dp, f), REPO))
    return zle


def czcionka(rozmiar, gruba=False):
    from PIL import ImageFont
    for n in (("arialbd.ttf" if gruba else "arial.ttf"), "DejaVuSans-Bold.ttf" if gruba else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(n, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def plansza(obrazy, podpisy, tytul, plik, kol=4, szer=480):
    from PIL import Image, ImageDraw
    ims = [Image.open(o).convert("RGB") for o in obrazy]
    w0, h0 = ims[0].size
    h = int(szer * h0 / w0)
    rzedy = (len(ims) + kol - 1) // kol
    pas, pod = 70, 34
    c = Image.new("RGB", (kol * szer, pas + rzedy * (h + pod)), (24, 28, 24))
    d = ImageDraw.Draw(c)
    d.text((18, 16), tytul, fill=(240, 240, 230), font=czcionka(30, True))
    for i, (im, p) in enumerate(zip(ims, podpisy)):
        x, y = (i % kol) * szer, pas + (i // kol) * (h + pod)
        c.paste(im.resize((szer, h)), (x, y))
        d.text((x + 10, y + h + 6), p, fill=(220, 225, 210), font=czcionka(19))
    c.save(plik, quality=88)
    log("plansza", os.path.relpath(plik, REPO))


def main():
    a = sys.argv[1:]
    klatki = a[a.index("--klatki") + 1] if "--klatki" in a else os.path.join(tempfile.gettempdir(), "jajka_biomow_klatki")
    os.makedirs(klatki, exist_ok=True)
    if "--bez-tekstur" not in a:
        subprocess.run([sys.executable, "-B", os.path.join(TU, "tekstury.py")], check=True, cwd=REPO)
    for b in BIOMY:
        arg = ["--biom", b, "--wyj", os.path.join(TU, "modele")]
        if "--bez-renderu" not in a:
            arg += ["--klatki", klatki]
        blender(*arg)
        napraw_fbx(os.path.join(TU, "modele", "jajko_%s.fbx" % b))
    zle = slady_dysku()
    if zle:
        raise SystemExit("ślady dysku autora w plikach pakietu: %s" % zle)
    if "--bez-renderu" in a:
        return
    blender("--zestawienie", "--klatki", klatki)
    pod = os.path.join(TU, "podglad")
    os.makedirs(pod, exist_ok=True)
    for b in BIOMY:
        st = json.load(open(os.path.join(TU, "modele", "jajko_%s_statystyki.json" % b), encoding="utf-8"))["calosc"]
        plansza([os.path.join(klatki, "%s_%d.jpg" % (b, i)) for i in range(4)],
                 ["przód (+Z, kamera scenki)", "prawy bok (+X)", "tył", "lewy bok"],
                 "%s — %d trójkątów w spoczynku (%d z kawałkami skorupy); szer. × głęb. × wys. %.1f × %.1f × %.1f studa (skala ×1,5)"
                 % (NAZWY[b], st["trojkaty_w_spoczynku"], st["trojkaty_razem"], st["rozmiar_m"][0] * 1.5,
                    st["rozmiar_m"][2] * 1.5, st["rozmiar_m"][1] * 1.5),
                 os.path.join(pod, "jajko_%s_4strony.jpg" % b))
    plansza([os.path.join(klatki, n) for n in ("bagno_zblizenie.jpg", "bagno_wyklucie.jpg", "dzungla_zblizenie.jpg",
                                               "dzungla_wyklucie.jpg")],
            ["Bagno: skorupa z bliska", "Bagno: wyklucie (Egg ukryte, 3 kawałki)", "Dżungla: skorupa z bliska",
             "Dżungla: wyklucie (Egg ukryte, 3 kawałki)"],
            "Skorupa i rozpad — pęknięcia świecą dokładnie na liniach podziału kawałków",
            os.path.join(pod, "jajka_wyklucie.jpg"))
    from PIL import Image, ImageDraw
    im = Image.open(os.path.join(klatki, "zestawienie.jpg")).convert("RGB")
    d = ImageDraw.Draw(im)
    f = czcionka(26, True)
    W, H = im.size
    for x, t in ((0.13, "Jajko Bagna"), (0.40, "leśne — PRZYBLIŻENIE"), (0.66, "Jajko Dżungli"), (0.90, "gracz 5,3 studa")):
        d.text((int(W * x) - 90, 18), t, fill=(30, 34, 28), font=f)
    d.text((20, H - 40), "Jedna skala, rzut prostokątny z przodu. Leśne: tekstura Pawła na bryle tej samej wielkości — jego modelu "
           "(GLB) nie ma w repo, więc podstawa i ozdoby leśnego nie są pokazane.", fill=(30, 34, 28), font=czcionka(18))
    im.save(os.path.join(pod, "jajka_zestawienie.jpg"), quality=88)
    log("plansza swiat/jajka_biomow/podglad/jajka_zestawienie.jpg")


if __name__ == "__main__":
    main()
