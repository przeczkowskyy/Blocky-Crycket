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

Opcjonalnie — bohater z ciałem bazowym i ekwipunkiem (D-071, EKWIPUNEK.md): gdy moduł ma cialo(), przedmioty(),
warianty() i STROJE, ten sam przebieg robi dodatkowo wynik/<moduł>/ekwipunek/:
  <id>_<strój>_plansza.jpg, <id>_<strój>_bohater.jpg     każdy strój z STROJE (golas = ciało bazowe)
  <id>_ekwipunek_plansza.jpg                             goły | pełny | dwa częściowe (PLANSZA_ZBIORCZA)
  <id>_<strój>_<klip>.mp4, …_klatki.jpg, …_z_filmu.jpg   filmy z FILMY_EKWIPUNKU (strój, klip)
  <id>_cialo.fbx, <id>_cialo.glb, <id>_cialo_tekstury/   gołe ciało z włosami i zaczepami Ekw<Kosc>Attachment
  przedmioty/<segment>.fbx/.glb/_tekstury/              każdy segment kostny osobno (broń: przedmioty/ wyżej)
  ikony/<przedmiot>_ikona.png, <id>_ekwipunek_ikony_arkusz.jpg   ikony całych przedmiotów
  ekwipunek.json                                         dane przedmiotów dla gry (moduł ekwipunek_json())
Opcjonalnie — moduł z funkcją po_przebudowie(cel) (rasy: rasa_<id>.py) dokłada po ułożeniu wyniku własne obrazy,
np. rasa_<id>_porownanie.jpg (rzut i model) i rasa_<id>_skala.jpg; zwraca ich nazwy do listy plików raportu.
Inne moduły przebudowują się jak dotąd.
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


def raport_txt(mod_nazwa, modul, rap, pliki, uwagi, kontrola, ekwipunek=None):
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
    if ekwipunek:
        L += ekwipunek
    if uwagi:
        L += ["UWAGI PODGLĄDU"] + ["- " + u for u in uwagi] + [""]
    L += ["KONTROLA EKSPORTÓW"] + ["- " + k for k in kontrola] + [""]
    L += ["PLIKI"] + ["- " + p for p in pliki] + [""]
    return "\n".join(L)


# --------------------------------------------------------------------------- opcjonalnie: ekwipunek bohatera (D-071)
OPAKOWANIE = '''# -*- coding: utf-8 -*-
# Plik roboczy przebuduj.py (katalog tymczasowy): zbuduj() = warianty(%(rodzaj)r) modułu bohatera.
import importlib.util, sys
if %(repo)r not in sys.path:
    sys.path.insert(0, %(repo)r)
_s = importlib.util.spec_from_file_location("bohater_%(nazwa)s", %(sciezka)r)
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)


def zbuduj():
    return _m.warianty(%(rodzaj)r)
'''


def ma_ekwipunek(modul):
    return all(hasattr(modul, n) for n in ("cialo", "przedmioty", "warianty", "STROJE"))


def ekwipunek_blender(mod_nazwa, modul, sciezka, robocze, a):
    """Rendery i eksporty wariantów (przed czyszczeniem wynik/<moduł>/): plansze strojów i ikony, filmy w strojach,
    eksport gołego ciała i segmentów. Zwraca słownik folderów roboczych."""
    r = {"plansze": os.path.join(robocze, "ekw_plansze"), "eksport": os.path.join(robocze, "ekw_eksport"),
         "filmy": []}
    opak = {}
    for rodzaj in ("plansze", "eksport"):
        opak[rodzaj] = os.path.join(robocze, "%s_ekw_%s.py" % (mod_nazwa, rodzaj))
        with open(opak[rodzaj], "w", encoding="utf-8", newline="\n") as f:
            f.write(OPAKOWANIE % {"rodzaj": rodzaj, "repo": REPO, "nazwa": mod_nazwa, "sciezka": sciezka})
    r["tekst_plansze"] = podglad(opak["plansze"], r["plansze"])
    r["tekst_eksport"] = podglad(opak["eksport"], r["eksport"], "--eksport", "--bez-renderu")
    if not a.bez_filmow:
        wybrane = a.filmy.split(",") if a.filmy else None
        for stroj, klip in getattr(modul, "FILMY_EKWIPUNKU", ()):
            if wybrane is None or klip in wybrane:
                pid = "%s_%s" % (modul.ID, stroj)
                wyj = os.path.join(robocze, "ekw_film_%s_%s" % (pid, klip))
                podglad(opak["plansze"], wyj, "--klip", klip, "--tylko", pid)
                r["filmy"].append((pid, klip, wyj))
    return r


def plansza_zbiorcza(obrazy, cel, tytul):
    """Kadry bohaterskie strojów obok siebie, podpisy pod spodem (na arkuszu, nie na modelach)."""
    from PIL import Image, ImageDraw, ImageFont
    if not obrazy:
        return False
    try:
        fn = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)
        fb = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
    except OSError:
        fn = fb = ImageFont.load_default()
    K = 450
    im = Image.new("RGB", (len(obrazy) * K, K + 100), "#1d1729")
    dr = ImageDraw.Draw(im)
    dr.text((14, 12), tytul, font=fb, fill="#ffffff")
    for i, (podpis, p) in enumerate(obrazy):
        ob = Image.open(p).convert("RGB")
        ob.thumbnail((K - 10, K - 10), Image.LANCZOS)
        x = i * K + (K - ob.width) // 2
        im.paste(ob, (x, 52))
        dr.text((i * K + (K - dr.textlength(podpis, font=fn)) // 2, K + 56), podpis, font=fn, fill="#d9d0ee")
    im.save(cel, quality=88)
    return True


def ekwipunek_uloz(mod_nazwa, modul, r, cel, rap_glowny=()):
    """Układa wynik/<moduł>/ekwipunek/ i pisze ekwipunek.json (rap_glowny: raporty głównego przebiegu — broń).
    Zwraca (pliki, kontrola, raport)."""
    from swiat.postacie.biblioteka.postac import Akcesorium as Akc
    ID = modul.ID
    ekw = os.path.join(cel, "ekwipunek")
    os.makedirs(ekw, exist_ok=True)
    pliki = []

    def wez(zrodlo, nazwa_cel):
        if kopiuj(zrodlo, os.path.join(ekw, nazwa_cel)):
            pliki.append("ekwipunek/" + nazwa_cel + ("/" if os.path.isdir(zrodlo) else ""))
            return True
        return False
    for s in modul.STROJE:
        for kon in ("_plansza.jpg", "_bohater.jpg"):
            wez(os.path.join(r["plansze"], "%s_%s%s" % (ID, s, kon)), "%s_%s%s" % (ID, s, kon))
    nazwy = getattr(modul, "NAZWY_STROJOW", {})
    zb = [(nazwy.get(s, s), os.path.join(ekw, "%s_%s_bohater.jpg" % (ID, s)))
          for s in getattr(modul, "PLANSZA_ZBIORCZA", list(modul.STROJE)[:4])]
    if plansza_zbiorcza([x for x in zb if os.path.isfile(x[1])], os.path.join(ekw, ID + "_ekwipunek_plansza.jpg"),
                        "%s — ciało bazowe i stroje z przedmiotów" % getattr(modul, "NAZWA", ID)):
        pliki.append("ekwipunek/%s_ekwipunek_plansza.jpg" % ID)
    for pid, klip, wyj in r["filmy"]:
        for kon in (".mp4", "_klatki.jpg", "_z_filmu.jpg"):
            n = "%s_%s%s" % (pid, klip, kon)
            wez(os.path.join(wyj, n), n)
    cid = ID + "_cialo"
    for kon in (".fbx", ".glb", "_tekstury"):
        wez(os.path.join(r["eksport"], cid + kon), cid + kon)
    raporty = {}
    for f in os.listdir(r["eksport"]):
        if f.endswith("_raport.json"):
            with open(os.path.join(r["eksport"], f), encoding="utf-8") as fh:
                d = json.load(fh)
            raporty[d["id"]] = d
    glowne = {d["id"]: d for d in rap_glowny if d.get("rodzaj") == "akcesorium" and d["id"] not in raporty}
    prz = modul.przedmioty()
    ikony = []
    for x in prz:
        for s in x.segmenty:
            if s["kosc"]:
                for kon in (".fbx", ".glb", "_tekstury"):
                    wez(os.path.join(r["eksport"], s["akc"].id + kon), "przedmioty/" + s["akc"].id + kon)
        ik = x.ikona()
        if isinstance(ik, Akc) and wez(os.path.join(r["plansze"], ik.id + "_ikona.png"), "ikony/%s_ikona.png" % x.id):
            ikony.append((x.nazwa, os.path.join(ekw, "ikony", "%s_ikona.png" % x.id)))
    if ikony:
        arkusz_ikon(ikony, os.path.join(ekw, ID + "_ekwipunek_ikony_arkusz.jpg"), "Przedmioty stroju — " + ID)
        pliki.append("ekwipunek/%s_ekwipunek_ikony_arkusz.jpg" % ID)
    # ekwipunek.json: dane modułu + pliki, trójkąty i attachment (minus środek skrzynki siatki od zaczepu)
    dane = modul.ekwipunek_json() if hasattr(modul, "ekwipunek_json") else {"przedmioty": [x.opis() for x in prz]}
    for wpis in dane["przedmioty"]:
        wpis["plik_ikony"] = "wynik/%s/ekwipunek/ikony/%s_ikona.png" % (mod_nazwa, wpis["id"])
        for c in wpis["czesci"]:
            folder = "ekwipunek/przedmioty" if c["zaczep"].startswith("Ekw") else "przedmioty"
            for kon in ("fbx", "glb"):
                c[kon] = "wynik/%s/%s/%s.%s" % (mod_nazwa, folder, c["id"], kon)
            rp = raporty.get(c["id"]) or glowne.get(c["id"])
            if rp:
                c["trojkaty"] = rp.get("trojkaty_razem")
                c["attachment_pos"] = [round(-v, 4) + 0.0 for v in (rp.get("srodek_skrzynki_od_zaczepu") or [0, 0, 0])]
    dane["cialo_pliki"] = {"fbx": "wynik/%s/ekwipunek/%s.fbx" % (mod_nazwa, cid),
                           "glb": "wynik/%s/ekwipunek/%s.glb" % (mod_nazwa, cid)}
    with open(os.path.join(ekw, "ekwipunek.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, indent=1)
    pliki.append("ekwipunek/ekwipunek.json")
    kontrola = ["ekwipunek: " + l.split("KONTROLA ", 1)[1].strip() for l in r["tekst_eksport"].splitlines()
                if "POSTAC | KONTROLA " in l]
    rap = {"stroje": {k: list(v) for k, v in modul.STROJE.items()}, "filmy": [[p, k] for p, k, _ in r["filmy"]],
           "modele": list(raporty.values())}
    return pliki, kontrola, rap


def raport_ekwipunku(modul, rap):
    """Sekcja raport.txt: stroje, przedmioty z segmentami i trójkątami."""
    L = ["EKWIPUNEK (D-071: ciało bazowe + strój z przedmiotów; pliki w ekwipunek/)"]
    nazwy = getattr(modul, "NAZWY_STROJOW", {})
    for s, ids in rap["stroje"].items():
        L.append("- strój %s (%s): %s" % (s, nazwy.get(s, s), ", ".join(ids) or "bez przedmiotów"))
    tr = {m["id"]: m.get("trojkaty_razem") for m in rap["modele"]}
    korekty = getattr(modul, "KOREKTY_CHWYTU", {})       # opcjonalnie: korekty chwytu bohatera (kot: kości nośne)
    for x in modul.przedmioty():
        seg = []
        for s in x.segmenty:
            if s["kosc"]:
                seg.append("%s %s%s %s tr." % (s["akc"].id, s["kosc"], " (powłoka)" if s["zakrywa"] else "",
                                               tr.get(s["akc"].id, "?")))
            else:
                seg.append("%s na %s" % (s["akc"].id, korekty.get(s["zaczep"], (s["zaczep"],))[0]))
        L.append("- %s „%s” [%s%s]: %s" % (x.id, x.nazwa, x.slot, ", część " + x.czesc_od if x.czesc_od else "",
                                          "; ".join(seg)))
    if rap["filmy"]:
        L.append("- filmy w strojach: " + ", ".join("%s %s" % (p, k) for p, k in rap["filmy"]))
    return L + [""]


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
    ekw_r = ekwipunek_blender(mod_nazwa, modul, sciezka, robocze, a) if ma_ekwipunek(modul) else None
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
    rap_ekw = None
    if ekw_r:
        p_e, k_e, rap_ekw = ekwipunek_uloz(mod_nazwa, modul, ekw_r, cel, rap)
        pliki += p_e
        kontrola = kontrola + k_e
    # opcjonalnie: moduł dokłada własne obrazy do świeżo ułożonego folderu (rasy: plansza porównawcza z rzutem
    # i plansza skali — rasy_plansze.py); po_przebudowie(cel) zwraca nazwy plików względem wynik/<moduł>/
    if hasattr(modul, "po_przebudowie"):
        pliki += list(modul.po_przebudowie(cel) or [])
    naprawione = 0
    for dp, _, fs in os.walk(cel):
        for f in fs:
            if f.endswith(".fbx"):
                naprawione += napraw_fbx(os.path.join(dp, f))
    pliki += ["raport.json", "raport.txt"]
    with open(os.path.join(cel, "raport.json"), "w", encoding="utf-8", newline="\n") as f:
        dane = {"modul": mod_nazwa, "modele": rap, "uwagi_podgladu": uwagi, "kontrola": kontrola}
        if rap_ekw:
            dane["ekwipunek"] = rap_ekw
        json.dump(dane, f, ensure_ascii=False, indent=1)
    with open(os.path.join(cel, "raport.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(raport_txt(mod_nazwa, modul, rap, pliki, uwagi, kontrola,
                           raport_ekwipunku(modul, rap_ekw) if rap_ekw else None))
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
    ap.add_argument("--mimo-kolizji", action="store_true",
                    help="przebuduj, choć inna osoba ma w panelu aktywną pracę nad tym modelem")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    # praca w toku w panelu (tools/praca_auto.py): stop przed Blenderem, gdy model ma w pracy INNA osoba
    pa, uchwyty = _praca_auto(), []
    for m in a.moduly if pa else ():
        uchwyty.append(pa.przed("przebudowa-" + m.lower(), "Przebudowa modelu " + m, ["model:" + m.lower()],
                                mimo_kolizji=a.mimo_kolizji, koniec="+%dm" % (20 if a.bez_filmow else 45)))
        if uchwyty[-1].zatrzymaj:
            log(uchwyty[-1].komunikat)
            for u in uchwyty[:-1]:
                pa.po(u, ok=False, komunikat="nie ruszyła: kolizja z pracą innej osoby")
            return pa.KOD_KOLIZJI
    ok, skonczone = True, False
    try:
        for m in a.moduly:
            ok = przebuduj(m, a) and ok
        skonczone = True
    finally:
        for u in uchwyty:
            pa.po(u, ok=skonczone, komunikat=None if skonczone and ok else
                  ("kontrola eksportów nie wszędzie zgodna" if skonczone else "przerwana błędem"))
    return 0 if ok else 1


def _praca_auto():
    """tools/praca_auto.py albo None (brak pliku albo błąd importu = przebudowa jak dawniej)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("praca_auto", os.path.join(REPO, "tools", "praca_auto.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("PRZEBUDUJ | uwaga: bez zgłaszania pracy w panelu (%s)" % type(e).__name__, flush=True)
        return None


if __name__ == "__main__":
    sys.exit(main())
