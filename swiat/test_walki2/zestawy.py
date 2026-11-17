# -*- coding: utf-8 -*-
"""Zestawy postaci na tablicy prototypu walki (v3) — WZORZEC w Pythonie dla zrodla/Wzorcowe.luau (W.zestaw).

Tablica pozwala obejrzeć nowości silnika v3 (tools/walka/ZMIANY_SESJA_1611.md): gracz wybiera klasę, przeciwnika,
poziom i ZESTAW postaci. Zestawy biorą się z tools/walka/wzorcowe.py i z dokumentu silnika — bez nowych liczb:

  wzorcowa      wzorcowe.postac (jak dotąd)
  mana          wzorcowe.build("mana") — build pod manę: premie many z przedmiotów, broń many, pasywka many w slocie,
                pula pomniejszona o koszt przedmiotów (KOSZT_MANY)
  pasywki       1 aktywna + 2 pasywne ze slotów jak w tabeli (g) dokumentu (Wojownik: Potężne cięcie, Kolos, Rozdzieracz;
                Zwiadowca: Uderzenie z góry, Oko łowcy, Zwinność; Mag: Kula ognia, Skupiona magia, Magiczny pocisk)
                + pasywka broni (BRON_ZESTAWU — wybór prototypu, żeby było widać pasywkę broni: Topór rzeźnika, Łuk
                wiatru, Ognista różdżka — ta ostatnia to przykład z sesji, podpalenie +2 tury); sloty jak wzorcowa
                (1 / 2 / 3 na poziomach 1 / 5 / 10), więc na 1. poziomie zostaje sama aktywna i pasywka broni
  wskrzeszenie  postać wzorcowa ze wskrzeszeniem (legendarna pasywka, propozycja D-094) w ostatnim slocie — tak
                jak tabela (k) w tools/walka/balans.py (na 1.–4. poziomie to jedyny slot)

Przeciwnik „lustro” = postać tej samej klasy i z tym samym zestawem (pojedynek; jedyny sposób, żeby na tablicy
zobaczyć wskrzeszenie PRZECIWNIKA — potwory lasu nie mają wskrzeszenia w danych). Nazwa: NAZWY_LUSTRA.
"""
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
_W = os.path.join(REPO, "tools", "walka")
if _W not in sys.path:
    sys.path.insert(0, _W)
import wzorcowe as WZ  # noqa: E402

ZESTAWY = ["wzorcowa", "mana", "pasywki", "wskrzeszenie"]
NAZWY = {"wzorcowa": "WZORCOWA", "mana": "POD MANĘ", "pasywki": "PASYWKI", "wskrzeszenie": "WSKRZESZENIE"}
PASYWKI_ZESTAWU = {"wojownik": ["kolos", "rozdzieracz"], "zwiadowca": ["oko_lowcy", "zwinnosc"],
                   "mag": ["skupiona_magia", "magiczny_pocisk"]}
BRON_ZESTAWU = {"wojownik": "topor_rzeznika", "zwiadowca": "luk_wiatru", "mag": "ognista_rozdzka"}
LUSTRO = "lustro"
NAZWY_LUSTRA = {"wojownik": "Lustrzany Wojownik", "zwiadowca": "Lustrzany Zwiadowca", "mag": "Lustrzany Mag"}


def postac(zestaw, klasa, poziom):
    """Opis postaci (wejście silnika) dla zestawu; None = nieznany zestaw."""
    if zestaw == "wzorcowa":
        return WZ.postac(klasa, poziom)
    if zestaw == "mana":
        return WZ.build("mana", klasa, poziom)
    if zestaw == "pasywki":
        um = [WZ.UMIEJETNOSCI[klasa][0]] + PASYWKI_ZESTAWU[klasa]
        return WZ.postac(klasa, poziom, umiejetnosci=um[:WZ.sloty(poziom)], pasywka_broni=BRON_ZESTAWU[klasa])
    if zestaw == "wskrzeszenie":
        n = WZ.sloty(poziom)
        return WZ.postac(klasa, poziom, umiejetnosci=WZ.UMIEJETNOSCI[klasa][:n - 1] + ["wskrzeszenie"])
    return None


def przeciwnik(zestaw, klasa, wrog, poziom):
    """Wejście silnika dla przeciwnika: potwór lasu albo lustro (postać tej samej klasy i zestawu)."""
    if wrog == LUSTRO:
        p = postac(zestaw, klasa, poziom)
        p["nazwa"] = NAZWY_LUSTRA[klasa]
        return {"postac": p}
    return {"potwor": wrog, "poziom": poziom}


def pasywki_strony(opis):
    """To, co serwer prototypu wysyła klientowi do zapowiedzi: {sloty: [pasywne ze slotów], bron: id | ""}."""
    import silnik as S
    return {"sloty": [u for u in opis.get("umiejetnosci") or [] if u in S.PASYWNE],
            "bron": (opis.get("bron") or {}).get("pasywka") or ""}
