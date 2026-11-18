#!/usr/bin/env python3
"""Placeholdery slotów broni zależne od klasy (Paweł 18.11) z jednego arkusza Higgsfield.

Arkusz: assets/raw/SlotPlaceholders/v1_3.png (wariant 3 wybrany przez Pawła) — miecz, tarcza, kostur, proca na białym
tle. Narzędzie:
1. tnie arkusz na cztery sylwetki (kolumny z treścią) i przekolorowuje je na dokładny odcień wypalonych sylwetek
   z tła ekwipunku (mierzony w slocie broni), żeby nie odstawały od hełmu i rękawic -> SlotPh<Nazwa>.png,
2. robi PUSTY SLOT z prawdziwego wycinka tła (slot broni z EqBg1): namalowany miecz jest wymazany, a wnętrze
   uzupełnione od brzegów (wypełnianie „warstwami” średnią sąsiadów + wygładzenie), rogi poza ramką przezroczyste,
3. składa pełne obrazki slotów (ramka + wnętrze + sylwetka), które w grze leżą co do piksela na slocie z tła:
   SlotWeaponMage (kostur), SlotWeaponScout (proca) — w miejscu slotu broni; SlotOffHandShield (tarcza) — nowy slot
   Wojownika obok slotu broni. Wojownik w slocie broni ma dalej miecz z tła.

    python tools/slot_placeholders.py   ->  assets/processed/SlotPlaceholders/*.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/raw/SlotPlaceholders/v1_3.png"
DST = ROOT / "assets/processed/SlotPlaceholders"
NAZWY = ["Sword", "Shield", "Staff", "Slingshot"]       # kolejność na arkuszu, od lewej
PANEL = (2048, 1166)                                     # pełne tło okna (EqBg1..4 po 1024 × 583)
# ramka slotu broni w pikselach pełnego tła (zmierzona: zewnętrzny czarny obrys) i jej wnętrze (bez złotego rantu);
# przycisk Slot_Weapon (482, 462, 116 × 116) leży w środku ramki — klient przelicza położenie obrazka względem niego
RAMKA = (470, 455, 606, 590)
WNETRZE = (487, 470, 590, 572)
SKALA = 4                                                # obrazek slotu w 4 × rozdzielczości tła
WYPELNIENIE = 0.70                                       # część slotu zajęta przez sylwetkę (jak miecz w tle)
PROMIEN = 0.17                                           # zaokrąglenie rogów ramki (ułamek boku)


def tlo_panelu():
    full = Image.new("RGB", PANEL)
    for i, (x, y) in enumerate([(0, 0), (1024, 0), (0, 583), (1024, 583)]):
        full.paste(Image.open(ROOT / f"assets/processed/EquipmentPanel/EqBg{i + 1}.png").convert("RGB"), (x, y))
    return full


def wycinek_slotu(full):
    return full.crop(RAMKA)


def kolor_sylwetek(slot):
    w, h = slot.size
    c = slot.crop((int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.8)))
    px = [p for p in c.getdata() if sum(p) < 230]
    return tuple(sum(p[i] for p in px) // len(px) for i in range(3))


def pusty_slot(slot):
    """Wymaż wypaloną sylwetkę z wnętrza slotu: maska = ciemne piksele we wnętrzu (+ 2 px), wypełnianie warstwami."""
    a = np.asarray(slot, dtype=np.float32).copy()
    h, w, _ = a.shape
    jas = a.sum(axis=2)
    wn = np.zeros((h, w), bool)
    wn[WNETRZE[1] - RAMKA[1]:WNETRZE[3] - RAMKA[1], WNETRZE[0] - RAMKA[0]:WNETRZE[2] - RAMKA[0]] = True
    maska = wn & (jas < 225)                                   # sylwetka ok. 166, wnętrze ok. 283
    for _ in range(2):                                          # poszerz o miękką krawędź sylwetki
        p = np.pad(maska, 1)
        maska = wn & (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    znane = ~maska
    while not znane.all():
        suma = np.zeros_like(a)
        ile = np.zeros((h, w), np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            zs = np.roll(znane, (dy, dx), axis=(0, 1))
            suma += np.roll(a, (dy, dx), axis=(0, 1)) * zs[..., None]
            ile += zs
        nowe = (~znane) & (ile > 0)
        a[nowe] = suma[nowe] / ile[nowe][:, None]
        znane |= nowe
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    gladkie = out.filter(ImageFilter.GaussianBlur(2.5))         # wygładź tylko wymazane miejsce
    mk = Image.fromarray((maska * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    return Image.composite(gladkie, out, mk)


def kolumny(im):
    w, h = im.size
    g = im.convert("L")
    jest = [any(g.getpixel((x, y)) < 170 for y in range(0, h, 6)) for x in range(w)]
    runs, s = [], None
    for i, v in enumerate(jest + [False]):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s > 20:
                runs.append((s, i))
            s = None
    return runs


def sylwetka(im, kol):
    """Kawałek arkusza -> RGBA w kolorze sylwetek, alfa z jasności (białe tło = przezroczyste)."""
    a = im.convert("L").point(lambda v: 0 if v > 235 else min(255, int((235 - v) * 255 / 120)))
    out = Image.new("RGBA", im.size, kol + (255,))
    out.putalpha(a)
    return out.crop(out.getbbox())


def wpasuj(syl, bok):
    s = bok * WYPELNIENIE / max(syl.size)
    syl = syl.resize((max(1, int(syl.width * s)), max(1, int(syl.height * s))), Image.LANCZOS)
    out = Image.new("RGBA", (bok, bok), (0, 0, 0, 0))
    out.alpha_composite(syl, ((bok - syl.width) // 2, (bok - syl.height) // 2))
    return out


def main():
    DST.mkdir(parents=True, exist_ok=True)
    slot = wycinek_slotu(tlo_panelu())
    kol = kolor_sylwetek(slot)
    pusty = pusty_slot(slot)
    W, H = pusty.width * SKALA, pusty.height * SKALA
    pusty = pusty.resize((W, H), Image.LANCZOS).convert("RGBA")
    rogi = Image.new("L", (W * 2, H * 2), 0)                    # maska ramki z wygładzonymi rogami
    ImageDraw.Draw(rogi).rounded_rectangle((0, 0, W * 2 - 1, H * 2 - 1), radius=int(PROMIEN * W * 2), fill=255)
    pusty.putalpha(rogi.resize((W, H), Image.LANCZOS))
    pusty.save(DST / "SlotEmpty.png")

    ark = Image.open(SRC).convert("RGB")
    runs = kolumny(ark)
    assert len(runs) == 4, runs
    syl = {n: sylwetka(ark.crop((x0, 0, x1, ark.height)), kol) for n, (x0, x1) in zip(NAZWY, runs)}
    for n, s in syl.items():
        wpasuj(s, 512).save(DST / f"SlotPh{n}.png")
    for plik, n in (("SlotWeaponMage", "Staff"), ("SlotWeaponScout", "Slingshot"), ("SlotOffHandShield", "Shield")):
        im = pusty.copy()
        warstwa = wpasuj(syl[n], min(W, H))
        im.alpha_composite(warstwa, ((W - warstwa.width) // 2, (H - warstwa.height) // 2))
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(pusty.getchannel("A")))))
        im.save(DST / f"{plik}.png")
    para_wojownika(slot, Image.open(DST / "SlotOffHandShield.png"))
    print("kolor sylwetek", kol, "slot", slot.size, "->", W, "x", H, "| para Wojownika", PARA)


# Wojownik (Paweł 18.11): miecz i tarcza jako para na środku pod paskiem poziomu — slot z tła przesunięty w lewo,
# tarcza obok. Jedna nakładka na obszar PARA: ściana z desek w miejscu starego slotu (wiersz ściany tuż nad slotem
# rozciągnięty w pionie — deski są pionowe), na niej dwie ramki co ODSTEP px.
ODSTEP = 10
SZER = RAMKA[2] - RAMKA[0]
LEWA = (RAMKA[0] + RAMKA[2]) // 2 - SZER - ODSTEP // 2           # lewa krawędź ramki miecza (para wyśrodkowana)
PARA = (LEWA, RAMKA[1], LEWA + 2 * SZER + ODSTEP, RAMKA[3])


def para_wojownika(slot, tarcza):
    full = tlo_panelu()
    # deski są pionowe: jeden wiersz ściany tuż nad slotem rozciągnięty w dół (bez poziomych prążków)
    wiersz = full.crop((RAMKA[0] - 4, RAMKA[1] - 10, RAMKA[2] + 4, RAMKA[1] - 9))
    sciana = wiersz.resize((wiersz.width, RAMKA[3] - RAMKA[1] + 8), Image.NEAREST)
    full.paste(sciana, (RAMKA[0] - 4, RAMKA[1] - 4))
    baza = full.crop(PARA).convert("RGBA")
    W, H = baza.size
    rogi = Image.new("L", (SZER * 2, (RAMKA[3] - RAMKA[1]) * 2), 0)
    ImageDraw.Draw(rogi).rounded_rectangle((0, 0, rogi.width - 1, rogi.height - 1), radius=int(PROMIEN * rogi.width),
                                           fill=255)
    rogi = rogi.resize((SZER, RAMKA[3] - RAMKA[1]), Image.LANCZOS)
    miecz = slot.convert("RGBA")
    miecz.putalpha(rogi)
    baza.alpha_composite(miecz, (0, 0))
    baza.alpha_composite(tarcza.resize(miecz.size, Image.LANCZOS), (SZER + ODSTEP, 0))
    baza = baza.resize((W * SKALA, H * SKALA), Image.LANCZOS)
    baza.save(DST / "SlotPairWarrior.png")


if __name__ == "__main__":
    main()
