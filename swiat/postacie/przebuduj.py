#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przebudowa jednego albo kilku modułów do folderu swiat/postacie/wynik/<moduł>/ — zawsze w tym samym układzie.

    # z głównego folderu repozytorium (Blender 5.0, ffmpeg i Pillow muszą być dostępne)
    python -B swiat/postacie/przebuduj.py rycerz
    python -B swiat/postacie/przebuduj.py zestaw_mag zestaw_rycerz --bez-filmow
    python -B swiat/postacie/przebuduj.py kot_mag --filmy czar,wiwat --zostaw-robocze

Co robi (pod wspólną blokadą Blendera, przez biblioteka/podglad_postaci.py):
  1. raz: eksport (FBX, FBX na klip, GLB, .blend, tekstury-palety) + kontrola eksportów + plansze i ikony,
  2. dla każdego klipu postaci (albo listy FILMY z modułu): film MP4, arkusz _klatki.jpg i _z_filmu.jpg,
  3. czyści wynik/<moduł>/ i układa pliki według jednego wzoru (niżej), zamienia lokalne ścieżki w FBX na względne,
     sprawdza, czy w plikach nie została ścieżka z dysku autora, pisze raport.json i raport.txt (jeden szablon).

Układ wynik/<moduł>/ (taki sam dla postaci, petów i zestawów):
  <model>.fbx, <model>__<klip>.fbx, <model>.glb, <model>.blend, <model>_tekstury/   model z kośćmi (postać, pet
                                                       albo przymiarka zestawu: <moduł>_przymiarka na manekinie R15)
  <model>_plansza.jpg, <model>_bohater.jpg, <model>_ikona.png (nie dla przymiarki)
  <model>_<klip>.mp4, <model>_<klip>_klatki.jpg, <model>_<klip>_z_filmu.jpg
  przedmioty/<id>.fbx, przedmioty/<id>.glb, przedmioty/<id>_tekstury/              każde akcesorium osobno
  ikony/<id>_ikona.png, <moduł>_ikony_arkusz.jpg                                   ikony przedmiotów
  raport.json (dane z Blendera), raport.txt (to samo dla człowieka + znane słabości z listy SLABOSCI modułu)
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie.biblioteka.podglad_postaci import wczytaj_modul  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium, Postac  # noqa: E402

PODGLAD = os.path.join(TU, "biblioteka", "podglad_postaci.py")
WYNIK = os.path.join(TU, "wynik")
# ślady dysku autora, których nie może być w plikach repozytorium
ZAKAZANE = [rb"[A-Za-z]:\\Users\\", rb"[A-Za-z]:/Users/", rb"AppData", rb"\\Temp\\"]


def log(*a):
    print("PRZEBUDUJ |", *a, flush=True)


def lista(w):
    return list(w) if isinstance(w, (list, tuple)) else [w]


def podglad(modul, wyj, *dodatkowe):
    polecenie = [sys.executable, "-B", PODGLAD, "--modul", modul, "--wyj", wyj] + list(dodatkowe)
    t0 = time.time()
    r = subprocess.run(polecenie, capture_output=True, cwd=REPO)
    tekst = (r.stdout + r.stderr).decode("utf-8", "replace")
    if r.returncode != 0:
        print(tekst[-4000:])
        raise SystemExit("podglad_postaci.py %s: błąd (kod %d)" % (" ".join(dodatkowe), r.returncode))
    log("  %s %s: %.0f s" % (os.path.basename(modul), " ".join(dodatkowe) or "", time.time() - t0))
    return tekst


def napraw_fbx(sciezka):
    """Bezwzględne ścieżki tekstur w binarnym FBX -> względne tej samej długości (.\\.\\…\\folder\\plik.png).
    Tekstury i tak są osadzone w pliku; chodzi o to, żeby nie zostawiać ścieżek z dysku autora."""
    b = open(sciezka, "rb").read()
    wzor = re.compile(rb"[A-Za-z]:\\[ -~]*?\\(?=[A-Za-z0-9_.]+\\[A-Za-z0-9_]+\.png)")
    licz = [0]

    def zamien(m):
        licz[0] += 1
        n = len(m.group())
        if n % 2 == 0:
            return b".\\" * (n // 2)
        return b".\\\\" + b".\\" * ((n - 3) // 2)

    nb = wzor.sub(zamien, b)
    if licz[0]:
        assert len(nb) == len(b)
        with open(sciezka, "wb") as f:
            f.write(nb)
    return licz[0]


def slady_dysku(folder):
    zle = []
    for dp, _, fs in os.walk(folder):
        for f in fs:
            p = os.path.join(dp, f)
            if f.endswith((".png", ".jpg", ".mp4", ".blend")):
                continue                                         # obrazy/filmy bez metadanych ścieżek; .blend skompresowany
            b = open(p, "rb").read()
            if any(re.search(w, b) for w in ZAKAZANE):
                zle.append(os.path.relpath(p, folder))
    return zle


def kopiuj(zrodlo, cel):
    if not os.path.exists(zrodlo):
        return False
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    if os.path.isdir(zrodlo):
        shutil.copytree(zrodlo, cel)
    else:
        shutil.copy2(zrodlo, cel)
    return True


def arkusz_ikon(ikony, cel, tytul):
    """Ikony przedmiotów w siatce z nazwami pod spodem (nazwy na arkuszu, nie na modelach)."""
    from PIL import Image, ImageDraw, ImageFont
    if not ikony:
        return
    try:
        fn = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
        fb = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 24)
    except OSError:
        fn = fb = ImageFont.load_default()
    kol, K = 6, 180
    wier = (len(ikony) + kol - 1) // kol
    im = Image.new("RGB", (kol * K + 24, wier * (K + 34) + 64), "#1d1729")
    dr = ImageDraw.Draw(im)
    dr.text((14, 14), tytul, font=fb, fill="#ffffff")
    for i, (nazwa, p) in enumerate(ikony):
        x, y = 12 + (i % kol) * K, 56 + (i // kol) * (K + 34)
        dr.rounded_rectangle((x + 4, y + 4, x + K - 4, y + K - 4), radius=12, fill="#3a3152")
        ik = Image.open(p).convert("RGBA")
        ik.thumbnail((K - 20, K - 20), Image.LANCZOS)
        im.paste(ik, (x + (K - ik.width) // 2, y + (K - ik.height) // 2), ik)
        t = nazwa if dr.textlength(nazwa, font=fn) <= K - 4 else nazwa[:24] + "…"
        dr.text((x + (K - dr.textlength(t, font=fn)) // 2, y + K + 4), t, font=fn, fill="#d9d0ee")
    im.save(cel, quality=88)


def f2(v):
    return ("%.2f" % v).replace(".", ",")


def wek(v):
    return "(" + "; ".join(f2(x) for x in v) + ")"


def raport_txt(mod_nazwa, modul, rap, pliki, uwagi, kontrola):
    L = []
    data = datetime.date.today().strftime("%d.%m.%Y")
    opis = (modul.__doc__ or "").strip().splitlines()[0] if modul.__doc__ else mod_nazwa
    L += ["RAPORT — %s" % mod_nazwa, opis, "",
          "Status: propozycja, nie kanon. Import do Roblox Studio nie był testowany.",
          "Źródło: swiat/postacie/%s.py · wygenerowano %s poleceniem:" % (mod_nazwa, data),
          "  python -B swiat/postacie/przebuduj.py %s" % mod_nazwa,
          "Jednostka = 1 stud; wymiary = szer X × wys Y × głęb Z; postać patrzy w +Z, jej lewa strona to +X.", ""]
    postacie = [r for r in rap if r["rodzaj"] == "postac"]
    akc = [r for r in rap if r["rodzaj"] == "akcesorium"]
    ost = sum(len(r.get("ostrzezenia", [])) for r in rap)
    zgodne = sum(1 for k in kontrola if k.endswith("ZGODNE"))
    L += ["PODSUMOWANIE",
          "- modele z kośćmi: %s" % (", ".join(r["id"] for r in postacie) or "brak"),
          "- przedmioty (akcesoria): %d" % len(akc),
          "- kontrola eksportów (plik wczytany z powrotem do pustego Blendera): %d plików, zgodnych %d"
          % (len(kontrola), zgodne),
          "- ostrzeżenia z raportu: %d; uwagi podglądu: %d" % (ost, len(uwagi)), ""]
    sl = list(getattr(modul, "SLABOSCI", []))
    L += ["ZNANE SŁABOŚCI"] + (["- " + s for s in sl] if sl else ["- (moduł nie podaje listy SLABOSCI)"]) + [""]
    for r in postacie:
        L += ["MODEL %s „%s” (%s)" % (r["id"], r["nazwa"], r.get("typ")),
              "  wymiary ciała: %s × %s × %s; z akcesoriami: %s × %s × %s"
              % tuple(f2(x) for x in r["wymiary_ciala"] + r["wymiary_z_akcesoriami"]),
              "  trójkąty: %d (siatek: %d)" % (r["trojkaty_razem"], len(r["siatki"]))]
        if r.get("grupy_ciala"):
            L.append("  budżety ciała R15: " + ", ".join("%s %d/%d" % (g, v["trojkaty"], v["limit"])
                                                          for g, v in r["grupy_ciala"].items()))
        L.append("  kości (%d): %s" % (len(r["kosci"]), ", ".join(r["kosci"])))
        L.append("  klipy: " + (", ".join("%s %d kl. %s s%s" % (k["n"], k["dlugosc"], f2(k["sekundy"]),
                                                              " pętla" if k["petla"] else " jednorazowy")
                                         for k in r["klipy"]) or "brak"))
        L.append("  punkty zaczepienia: " + (", ".join(r["zaczepy"]) or "brak"))
        if r.get("akcesoria"):
            L.append("  założone: " + ", ".join("%s na %s%s" % (a["id"], a["zaczep"], "" if a["eksport"] else
                                                                 " (tylko podgląd, bez eksportu)")
                                                for a in r["akcesoria"]))
        for o in r.get("ostrzezenia", []):
            L.append("  OSTRZEŻENIE: " + o)
        L.append("")
    if akc:
        L += ["PRZEDMIOTY (każdy = jedna sztywna siatka; (0,0,0) = punkt zaczepienia)",
              "%-22s %-26s %-9s %6s  %-20s %-22s" % ("id", "zaczep", "typ", "trójk.", "wymiary", "attachment_pos")]
        for r in akc:
            sr = r.get("srodek_skrzynki_od_zaczepu") or [0, 0, 0]
            L.append("%-22s %-26s %-9s %6d  %-20s %-22s" % (r["id"], r["zaczep"], r["typ_roblox"], r["trojkaty_razem"],
                                                           " × ".join(f2(x) for x in r["siatki"][0]["wymiary"]),
                                                           wek([-x for x in sr])))
        L += ["attachment_pos = minus środek skrzynki siatki od punktu zaczepienia (w ramce zaczepu, przód +Z);",
              "importer stawia środek MeshPart w środku skrzynki, więc tak trzeba ustawić Attachment w Handle.", ""]
        for r in akc:
            for o in r.get("ostrzezenia", []):
                L.append("OSTRZEŻENIE %s: %s" % (r["id"], o))
        L.append("")
    if uwagi:
        L += ["UWAGI PODGLĄDU"] + ["- " + u for u in uwagi] + [""]
    L += ["KONTROLA EKSPORTÓW"] + ["- " + k for k in kontrola] + [""]
    L += ["PLIKI"] + ["- " + p for p in pliki] + [""]
    return "\n".join(L)


def przebuduj(mod_nazwa, a):
    sciezka = os.path.join(TU, mod_nazwa + ".py")
    modul = wczytaj_modul(sciezka)
    obiekty = lista(modul.zbuduj())
    postacie = [o for o in obiekty if isinstance(o, Postac)]
    akcesoria = [o for o in obiekty if isinstance(o, Akcesorium)]
    if akcesoria and not postacie:                           # tak samo jak podglad_postaci.py
        from swiat.postacie.biblioteka.postac import przymiarka
        postacie = [przymiarka(mod_nazwa + "_przymiarka", akcesoria)]
    robocze = a.robocze or tempfile.mkdtemp(prefix="przebuduj_%s_" % mod_nazwa)
    log("%s -> robocze %s" % (mod_nazwa, robocze))
    baza = os.path.join(robocze, "baza")
    tekst = podglad(sciezka, baza, "--eksport", "--ikony")
    uwagi = sorted({l.split("UWAGA:", 1)[1].strip() for l in tekst.splitlines() if "PODGLAD | UWAGA:" in l})
    kontrola = [l.split("KONTROLA ", 1)[1].strip() for l in tekst.splitlines() if "POSTAC | KONTROLA " in l]
    filmy = {}
    if not a.bez_filmow:
        wybrane = a.filmy.split(",") if a.filmy else getattr(modul, "FILMY", None)
        for p in postacie:
            for k in p.klipy:
                if wybrane is None or k.nazwa in wybrane:
                    wyj = os.path.join(robocze, "film_%s_%s" % (p.id, k.nazwa))
                    podglad(sciezka, wyj, "--klip", k.nazwa, "--tylko", p.id)
                    filmy.setdefault(p.id, []).append((k.nazwa, wyj))
    # --- układanie wyniku
    cel = os.path.join(WYNIK, mod_nazwa)
    if os.path.isdir(cel):
        shutil.rmtree(cel)
    os.makedirs(cel)
    pliki, rap = [], []
    eksport_modeli = getattr(modul, "EKSPORT_MODELI", True)    # False: z modeli z kośćmi tylko plansze (np. bronie)
    for p in postacie:
        for nazwa in sorted(os.listdir(baza)):
            if not eksport_modeli:
                if nazwa == p.id + "_plansza.jpg":
                    kopiuj(os.path.join(baza, nazwa), os.path.join(cel, nazwa))
                    pliki.append(nazwa)
                continue
            if (nazwa.startswith(p.id + "__") and nazwa.endswith(".fbx")) or nazwa in (
                    p.id + ".fbx", p.id + ".glb", p.id + ".blend", p.id + "_tekstury", p.id + "_plansza.jpg",
                    p.id + "_bohater.jpg") or (nazwa == p.id + "_ikona.png" and not p.id.endswith("_przymiarka")):
                kopiuj(os.path.join(baza, nazwa), os.path.join(cel, nazwa))
                pliki.append(nazwa + ("/" if os.path.isdir(os.path.join(baza, nazwa)) else ""))
        for klip, wyj in filmy.get(p.id, []):
            for kon in (".mp4", "_klatki.jpg", "_z_filmu.jpg"):
                n = "%s_%s%s" % (p.id, klip, kon)
                if kopiuj(os.path.join(wyj, n), os.path.join(cel, n)):
                    pliki.append(n)
        with open(os.path.join(baza, p.id + "_raport.json"), encoding="utf-8") as f:
            rap.append(json.load(f))
    ikony = []
    for akc in akcesoria:
        for kon in (".fbx", ".glb", "_tekstury"):
            if kopiuj(os.path.join(baza, akc.id + kon), os.path.join(cel, "przedmioty", akc.id + kon)):
                pliki.append("przedmioty/" + akc.id + kon + ("/" if kon == "_tekstury" else ""))
        ik = os.path.join(cel, "ikony", akc.id + "_ikona.png")
        if kopiuj(os.path.join(baza, akc.id + "_ikona.png"), ik):
            pliki.append("ikony/" + akc.id + "_ikona.png")
            ikony.append((akc.nazwa, ik))
        with open(os.path.join(baza, akc.id + "_raport.json"), encoding="utf-8") as f:
            rap.append(json.load(f))
    if ikony:
        arkusz_ikon(ikony, os.path.join(cel, mod_nazwa + "_ikony_arkusz.jpg"), "Ikony przedmiotów — " + mod_nazwa)
        pliki.append(mod_nazwa + "_ikony_arkusz.jpg")
    naprawione = 0
    for dp, _, fs in os.walk(cel):
        for f in fs:
            if f.endswith(".fbx"):
                naprawione += napraw_fbx(os.path.join(dp, f))
    pliki += ["raport.json", "raport.txt"]
    with open(os.path.join(cel, "raport.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"modul": mod_nazwa, "modele": rap, "uwagi_podgladu": uwagi, "kontrola": kontrola}, f,
                  ensure_ascii=False, indent=1)
    with open(os.path.join(cel, "raport.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(raport_txt(mod_nazwa, modul, rap, pliki, uwagi, kontrola))
    zle = slady_dysku(cel)
    log("%s: %d plików, %d ścieżek w FBX zamienionych, kontrola %d/%d zgodnych%s"
        % (mod_nazwa, len(pliki), naprawione, sum(k.endswith("ZGODNE") for k in kontrola), len(kontrola),
           "" if not zle else "; ŚLADY DYSKU: %s" % zle))
    if not a.zostaw_robocze and not a.robocze:
        shutil.rmtree(robocze, ignore_errors=True)
    return not zle and all(k.endswith("ZGODNE") for k in kontrola)


def main():
    ap = argparse.ArgumentParser(description="Przebudowa modułów do swiat/postacie/wynik/<moduł>/")
    ap.add_argument("moduly", nargs="+", help="nazwy modułów bez .py, np. rycerz zestaw_mag")
    ap.add_argument("--filmy", default="", help="tylko te klipy (po przecinku); domyślnie FILMY z modułu albo wszystkie")
    ap.add_argument("--bez-filmow", action="store_true")
    ap.add_argument("--robocze", default="", help="folder roboczy (domyślnie tymczasowy, usuwany na końcu)")
    ap.add_argument("--zostaw-robocze", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ok = True
    for m in a.moduly:
        ok = przebuduj(m, a) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
