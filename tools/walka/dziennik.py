# -*- coding: utf-8 -*-
"""Niezmienniki dziennika walki v3 — port src/shared/Walka/Dziennik.luau (ta sama funkcja sprawdz)."""
import math

WERSJA = 3
TYPY = ["cios", "krytyk", "blok", "unik", "umiejetnosc", "efekt_tick", "efekt_nalozony", "efekt_koniec", "utrata_tury",
        "wskrzeszenie"]
RANGI = ["gracz", "zwykly", "rzadki", "straznik"]
POLA_LUPU = ["zloto", "doswiadczenie", "tokeny_krainy", "gemy", "shard_ewolucji"]


def _liczba(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _calkowita(v):
    return _liczba(v) and v == v and v not in (float("inf"), float("-inf")) and math.floor(v) == v


def _setne(x):
    return int(math.floor(x * 100 + 0.5))


def _inna(strona):
    return "wrog" if strona == "gracz" else "gracz"


def sprawdz(walka):
    """-> (True, None) albo (False, opis bledu)."""
    if not isinstance(walka, dict) or walka.get("wersja") != WERSJA:
        return False, "brak walki albo zla wersja"
    if not isinstance(walka.get("strony"), dict) or not isinstance(walka.get("dziennik"), list) \
            or not isinstance(walka.get("lup"), dict):
        return False, "brak stron, dziennika albo lupu"
    hp, mana, mana_maks = {}, {}, {}
    for strona in ("gracz", "wrog"):
        s = walka["strony"].get(strona)
        if not isinstance(s, dict) or not _calkowita(s.get("zycie")) or s["zycie"] < 1:
            return False, "zla strona " + strona
        if s.get("ranga") not in RANGI or s.get("rodzaj") not in ("postac", "potwor"):
            return False, "zla ranga albo rodzaj strony " + strona
        if not _calkowita(s.get("mana_maks")) or s["mana_maks"] < 1 or not _calkowita(s.get("mana")) \
                or s["mana"] < 0 or s["mana"] > s["mana_maks"]:
            return False, "zla mana strony " + strona
        hp[strona] = s["zycie"]
        mana[strona] = s["mana"]
        mana_maks[strona] = s["mana_maks"]
    if walka["strony"]["gracz"]["rodzaj"] != "postac":
        return False, "gracz musi byc postacia"
    if not all(_liczba(walka.get(k)) for k in ("czas_wstepu", "czas_finalu", "czas")):
        return False, "brak czasow"
    blok_przepuszcza = walka.get("czesc_przez_blok")
    if not _liczba(blok_przepuszcza) or blok_przepuszcza < 0 or blok_przepuszcza > 1:
        return False, "brak czesci przechodzacej przez blok"
    d = walka["dziennik"]
    n = len(d)
    if n < 1:
        return False, "pusty dziennik"
    aktywne = {"gracz": {}, "wrog": {}}
    wskrzeszony = {"gracz": False, "wrog": False}
    t = _setne(walka["czas_wstepu"])
    for i in range(1, n + 1):
        z = d[i - 1]
        gdzie = "zdarzenie %d: " % i
        if not isinstance(z, dict) or z.get("typ") not in TYPY:
            return False, gdzie + "nieznany typ"
        if z.get("kto") not in ("gracz", "wrog") or z.get("cel") not in ("gracz", "wrog"):
            return False, gdzie + "zla strona"
        if not _calkowita(z.get("obrazenia")) or z["obrazenia"] < 0 or not _calkowita(z.get("pochloniete")) \
                or z["pochloniete"] < 0:
            return False, gdzie + "zle obrazenia"
        if not all(isinstance(z.get(k), str) for k in ("rodzaj", "umiejetnosc", "efekt")):
            return False, gdzie + "brak pol opisu"
        if not isinstance(z.get("krytyk"), bool) or not _liczba(z.get("wartosc")) or z["wartosc"] < 0 \
                or not _calkowita(z.get("tury")) or z["tury"] < 0 or not _calkowita(z.get("stosy")) or z["stosy"] < 0:
            return False, gdzie + "zle pola krytyk / wartosc / tury / stosy"
        typ = z["typ"]
        zwykly = typ in ("cios", "krytyk", "blok", "unik")
        if zwykly and z["cel"] != _inna(z["kto"]):
            return False, gdzie + "zwykly cios musi trafiac w druga strone"
        if zwykly and z["krytyk"] != (typ == "krytyk"):
            return False, gdzie + "znacznik krytyka niezgodny z typem"
        if typ == "unik" and (z["obrazenia"] != 0 or z["pochloniete"] != 0):
            return False, gdzie + "unik z obrazeniami"
        if typ in ("cios", "krytyk") and z["umiejetnosc"] != "":
            return False, gdzie + "cios i krytyk nie niosa umiejetnosci (krytyczna umiejetnosc ma typ umiejetnosc)"
        if typ in ("cios", "krytyk") and z["obrazenia"] < 1:
            return False, gdzie + "trafienie bez obrazen (dolna granica to 1)"
        if typ == "blok":
            if blok_przepuszcza > 0 and z["obrazenia"] < 1:
                return False, gdzie + "blok przepuszcza czesc ciosu, a obrazen nie ma"
            if blok_przepuszcza == 0 and (z["obrazenia"] != 0 or z["pochloniete"] != 0):
                return False, gdzie + "blok zatrzymuje caly cios, a sa obrazenia"
        if typ in ("efekt_nalozony", "efekt_koniec", "utrata_tury", "wskrzeszenie") \
                and (z["obrazenia"] != 0 or z["pochloniete"] != 0):
            return False, gdzie + "zdarzenie bez obrazen ma obrazenia"
        if typ in ("efekt_tick", "efekt_koniec", "utrata_tury", "wskrzeszenie") and z["kto"] != z["cel"]:
            return False, gdzie + "tykniecie, koniec efektu i utrata tury dotycza nosiciela"
        if typ == "efekt_tick" and (z["obrazenia"] < 1 or z["pochloniete"] != 0 or z["stosy"] < 1):
            return False, gdzie + "tykniecie: obrazenia >= 1, bez tarczy, co najmniej jeden stos"
        if z["obrazenia"] + z["pochloniete"] > 0 and z["rodzaj"] not in ("fizyczne", "magiczne"):
            return False, gdzie + "obrazenia bez rodzaju"
        if typ == "umiejetnosc" and z["umiejetnosc"] == "":
            return False, gdzie + "umiejetnosc bez identyfikatora"
        if typ.startswith("efekt_"):
            if z["efekt"] == "":
                return False, gdzie + "efekt bez identyfikatora"
            if typ == "efekt_nalozony":
                aktywne[z["cel"]][z["efekt"]] = True
            elif not aktywne[z["cel"]].get(z["efekt"]):
                return False, gdzie + "tykniecie albo koniec efektu, ktorego nie nalozono"
            elif typ == "efekt_koniec":
                del aktywne[z["cel"]][z["efekt"]]
        if typ == "utrata_tury" and not aktywne[z["kto"]]:
            return False, gdzie + "utrata tury bez efektu"
        if not _liczba(z.get("t")) or _setne(z["t"]) != t:
            return False, gdzie + "zly czas t (oczekiwano %s)" % (t / 100)
        if not _liczba(z.get("trwa")) or _setne(z["trwa"]) <= 0:
            return False, gdzie + "zly czas trwania"
        t = t + _setne(z["trwa"])
        if typ == "wskrzeszenie":
            # raz na walke, tylko zaraz po smiertelnej stracie zycia; wartosc = zycie po powrocie
            if hp[z["kto"]] != 0 or wskrzeszony[z["kto"]]:
                return False, gdzie + "wskrzeszenie bez nokautu albo drugi raz"
            if not _calkowita(z["wartosc"]) or z["wartosc"] < 1 or z["wartosc"] > walka["strony"][z["kto"]]["zycie"]:
                return False, gdzie + "wskrzeszenie: zle zycie po powrocie"
            hp[z["kto"]] = z["wartosc"]
            wskrzeszony[z["kto"]] = True
        else:
            hp[z["cel"]] = max(0, hp[z["cel"]] - z["obrazenia"])
        if z.get("hp_gracz") != hp["gracz"] or z.get("hp_wrog") != hp["wrog"]:
            return False, gdzie + "zycie po zdarzeniu niezgodne (oczekiwano %s / %s)" % (hp["gracz"], hp["wrog"])
        # mana: maleje TYLKO przy uzyciu umiejetnosci (o jej koszt w polu wartosc), poza tym tylko rosnie, do limitu
        uzycie = z["umiejetnosc"] != "" and typ in ("umiejetnosc", "unik", "blok")
        for strona in ("gracz", "wrog"):
            m = z.get("mana_" + strona)
            if not _calkowita(m) or m < 0 or m > mana_maks[strona]:
                return False, gdzie + "zla mana strony " + strona
            if uzycie and strona == z["kto"]:
                if not _calkowita(z["wartosc"]) or z["wartosc"] < 1 or m != mana[strona] - z["wartosc"]:
                    return False, gdzie + "uzycie umiejetnosci: mana musi spasc dokladnie o koszt"
            elif m < mana[strona]:
                return False, gdzie + "mana spadla bez uzycia umiejetnosci"
            mana[strona] = m
        if (hp["gracz"] == 0 or hp["wrog"] == 0) and i != n:
            nast = d[i]
            padl = "gracz" if hp["gracz"] == 0 else "wrog"
            if not (isinstance(nast, dict) and nast.get("typ") == "wskrzeszenie" and nast.get("kto") == padl
                    and hp[_inna(padl)] > 0):
                return False, gdzie + "walka trwa po nokaucie"
    if _setne(walka["czas"]) != t + _setne(walka["czas_finalu"]):
        return False, "czas calosci rozny od sumy czasow zdarzen"
    if not _calkowita(walka.get("tury")) or walka["tury"] < 1:
        return False, "zla liczba tur"
    G, W = walka["strony"]["gracz"]["zycie"], walka["strony"]["wrog"]["zycie"]
    if walka.get("bezpiecznik") is True:
        if hp["gracz"] == 0 or hp["wrog"] == 0:
            return False, "bezpiecznik przy walce zakonczonej nokautem"
        # float(): tak jak w Luau (liczby double) — dokladne int Pythona daloby przy ogromnym zyciu inny znak
        oczekiwany = "wygrana" if float(hp["gracz"]) * W >= float(hp["wrog"]) * G else "przegrana"
        if walka.get("wynik") != oczekiwany:
            return False, "wynik po bezpieczniku niezgodny z procentem zycia"
    elif walka.get("bezpiecznik") is False:
        if (hp["gracz"] == 0) == (hp["wrog"] == 0):
            return False, "walka bez bezpiecznika musi skonczyc sie nokautem dokladnie jednej strony"
        oczekiwany = "wygrana" if hp["wrog"] == 0 else "przegrana"
        if walka.get("wynik") != oczekiwany:
            return False, "wynik niezgodny z dziennikiem"
    else:
        return False, "brak pola bezpiecznik"
    lup = walka["lup"]
    for klucz in lup:
        if "jaj" in str(klucz).lower():
            return False, "lup z jajkiem — jajka nie wypadaja z potworow (D-060)"
    for pole in POLA_LUPU:
        if not _calkowita(lup.get(pole)) or lup[pole] < 0:
            return False, "zle pole lupu " + pole
    if not isinstance(lup.get("kraina"), str):
        return False, "lup bez krainy"
    if lup["shard_ewolucji"] > 0 and (walka["strony"]["wrog"]["ranga"] != "straznik" or walka["wynik"] != "wygrana"):
        return False, "Shard Ewolucji spoza wygranej ze straznikiem biomu"
    if walka["wynik"] == "przegrana" and (lup["zloto"] != 0 or lup["tokeny_krainy"] != 0 or lup["gemy"] != 0
                                         or lup["shard_ewolucji"] != 0):
        return False, "lup za przegrana"
    return True, None
