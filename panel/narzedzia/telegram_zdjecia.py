#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Raport ze zdjęciami na grupę zespołu na Telegramie — narzędzie dla agentów (działa bez serwera panelu).

Bot panelu (bc/telegram.py) wysyła sam tekst; to narzędzie dokłada zdjęcia z podpisami. Ustawienia bota (token, grupy)
czyta tak samo jak panel — z danych lokalnych poza repozytorium. Token i numery czatów nigdy nie trafiają na ekran.

    python -B panel/narzedzia/telegram_zdjecia.py --plan plan.json [--sucho]

plan.json:
    {"tekst": "wstęp zwykłym tekstem (do 3500 znaków, może być pusty)",
     "grupy": [{"podpis": "1. Miasto: …", "zdjecia": ["a.jpg", "b.jpg"]}, …],
     "koniec": "opcjonalna wiadomość na koniec"}

Ścieżki zdjęć: bezwzględne albo względem folderu z planem. Każda grupa zdjęć idzie jako jedna wiadomość: jedno zdjęcie
z podpisem albo album (2–10 zdjęć) z podpisem przy pierwszym zdjęciu. Podpis do 1000 znaków.
`--sucho` sprawdza plan i pliki i niczego nie wysyła.

Wysyłać tylko na prośbę człowieka. Zdjęcia bez nazw kont, tekst bez linków z kodami, kluczy i ścieżek z komputera.
"""
import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bc import telegram  # noqa: E402

MAKS_TEKST = 3500
MAKS_PODPIS = 1000
MAKS_ZDJEC_W_GRUPIE = 10
MAKS_PLIK_B = 9 * 1024 * 1024
TYPY = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
PRZERWA_S = 1.5
KONIEC_WIERSZA = b"\r\n"


class Blad(Exception):
    pass


def wczytaj_plan(sciezka):
    """→ {"tekst", "grupy": [{"podpis", "zdjecia": [ścieżki bezwzględne]}], "koniec"}; Blad przy złym planie."""
    try:
        with open(sciezka, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        raise Blad("Nie da się wczytać planu (plik JSON).") from None
    if not isinstance(d, dict):
        raise Blad("Plan ma być obiektem JSON.")
    baza = os.path.dirname(os.path.abspath(sciezka))
    plan = {"tekst": str(d.get("tekst") or "").strip(), "koniec": str(d.get("koniec") or "").strip(), "grupy": []}
    for nazwa in ("tekst", "koniec"):
        if len(plan[nazwa]) > MAKS_TEKST:
            raise Blad("Pole „%s” ma %d znaków, najwyżej %d." % (nazwa, len(plan[nazwa]), MAKS_TEKST))
    grupy = d.get("grupy") or []
    if not isinstance(grupy, list):
        raise Blad("Pole „grupy” ma być listą.")
    for nr, g in enumerate(grupy, 1):
        if not isinstance(g, dict):
            raise Blad("Grupa %d ma być obiektem." % nr)
        podpis = str(g.get("podpis") or "").strip()
        if len(podpis) > MAKS_PODPIS:
            raise Blad("Podpis grupy %d ma %d znaków, najwyżej %d." % (nr, len(podpis), MAKS_PODPIS))
        zdjecia = g.get("zdjecia") or []
        if not isinstance(zdjecia, list) or not 1 <= len(zdjecia) <= MAKS_ZDJEC_W_GRUPIE:
            raise Blad("Grupa %d: od 1 do %d zdjęć." % (nr, MAKS_ZDJEC_W_GRUPIE))
        pliki = []
        for z in zdjecia:
            p = str(z)
            if not os.path.isabs(p):
                p = os.path.join(baza, p)
            if os.path.splitext(p)[1].lower() not in TYPY:
                raise Blad("Grupa %d: zdjęcie musi być plikiem JPG albo PNG (%s)." % (nr, os.path.basename(p)))
            if not os.path.isfile(p):
                raise Blad("Grupa %d: brak pliku %s." % (nr, os.path.basename(p)))
            if os.path.getsize(p) > MAKS_PLIK_B:
                raise Blad("Grupa %d: plik %s jest większy niż 9 MB." % (nr, os.path.basename(p)))
            pliki.append(p)
        plan["grupy"].append({"podpis": podpis, "zdjecia": pliki})
    if not plan["tekst"] and not plan["grupy"] and not plan["koniec"]:
        raise Blad("Plan jest pusty.")
    return plan


def wieloczesciowe(pola, pliki):
    """Treść żądania multipart/form-data. pola: {nazwa: tekst}; pliki: {nazwa: (nazwa pliku ASCII, bajty, typ)}.
    → (bajty, nagłówek Content-Type)."""
    granica = "----bc" + uuid.uuid4().hex
    b = io.BytesIO()
    for k, v in pola.items():
        b.write(("--" + granica).encode("ascii") + KONIEC_WIERSZA)
        b.write(("Content-Disposition: form-data; name=\"%s\"" % k).encode("ascii") + KONIEC_WIERSZA + KONIEC_WIERSZA)
        b.write(str(v).encode("utf-8") + KONIEC_WIERSZA)
    for k, (nazwa, dane, typ) in pliki.items():
        b.write(("--" + granica).encode("ascii") + KONIEC_WIERSZA)
        b.write(("Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" % (k, nazwa)).encode("ascii") + KONIEC_WIERSZA)
        b.write(("Content-Type: " + typ).encode("ascii") + KONIEC_WIERSZA + KONIEC_WIERSZA)
        b.write(dane + KONIEC_WIERSZA)
    b.write(("--" + granica + "--").encode("ascii") + KONIEC_WIERSZA)
    return b.getvalue(), "multipart/form-data; boundary=" + granica


def _wywolaj(token, metoda, pola, pliki=None, czas=90, ponow=True):
    # adres z tokenem powstaje tylko tutaj; wyjątki bez łańcucha (from None), żeby adres nie trafił do śladu błędu
    adres = "%s/bot%s/%s" % (telegram.adres_api(), token, metoda)
    if pliki:
        dane, typ = wieloczesciowe(pola, pliki)
    else:
        dane, typ = json.dumps(pola, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8"
    req = urllib.request.Request(adres, data=dane, method="POST", headers={"Content-Type": typ})
    try:
        with urllib.request.urlopen(req, timeout=czas) as r:
            odp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        kod = e.code
        try:
            cialo = json.loads(e.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            cialo = {}
        if not isinstance(cialo, dict):
            cialo = {}
        czekaj = (cialo.get("parameters") or {}).get("retry_after")
        if kod == 429 and ponow and isinstance(czekaj, int) and czekaj <= 60:
            time.sleep(czekaj + 1)
            return _wywolaj(token, metoda, pola, pliki, czas, ponow=False)
        opis = telegram._bez_tokenu(cialo.get("description") or "", token)[:160]
        raise Blad("Telegram odrzucił „%s” (kod %d%s)." % (metoda, kod, (": " + opis) if opis else "")) from None
    except (urllib.error.URLError, OSError, ValueError):
        raise Blad("Brak połączenia z Telegramem.") from None
    if not isinstance(odp, dict) or not odp.get("ok"):
        raise Blad("Telegram nie przyjął „%s”." % metoda)
    return odp.get("result")


def _plik(sciezka, nr):
    roz = os.path.splitext(sciezka)[1].lower()
    with open(sciezka, "rb") as f:
        return ("zdjecie_%d%s" % (nr, roz), f.read(), TYPY[roz])


def wyslij(plan, ustaw=None, pisz=print):
    """Wysyła plan do każdej grupy z ustawień bota. → {"grupy", "wiadomosci", "zdjecia"}; Blad, gdy bot wyłączony."""
    ustaw = ustaw or telegram.ustawienia()
    if not ustaw.get("wlaczony") or not ustaw.get("grupy"):
        raise Blad("Telegram jest wyłączony albo bot nie ma zapisanej grupy zespołu.")
    token = ustaw["token"]
    wynik = {"grupy": 0, "wiadomosci": 0, "zdjecia": 0}
    for czat in ustaw["grupy"]:
        wynik["grupy"] += 1
        if plan["tekst"]:
            _wywolaj(token, "sendMessage", {"chat_id": czat, "text": plan["tekst"], "disable_web_page_preview": True})
            wynik["wiadomosci"] += 1
            time.sleep(PRZERWA_S)
        for nr, g in enumerate(plan["grupy"], 1):
            if len(g["zdjecia"]) == 1:
                pola = {"chat_id": czat}
                if g["podpis"]:
                    pola["caption"] = g["podpis"]
                _wywolaj(token, "sendPhoto", pola, {"photo": _plik(g["zdjecia"][0], 1)})
            else:
                media, pliki = [], {}
                for i, p in enumerate(g["zdjecia"]):
                    klucz = "f%d" % i
                    pliki[klucz] = _plik(p, i + 1)
                    m = {"type": "photo", "media": "attach://" + klucz}
                    if i == 0 and g["podpis"]:
                        m["caption"] = g["podpis"]
                    media.append(m)
                _wywolaj(token, "sendMediaGroup", {"chat_id": czat, "media": json.dumps(media, ensure_ascii=False)}, pliki)
            wynik["wiadomosci"] += 1
            wynik["zdjecia"] += len(g["zdjecia"])
            pisz("  grupa zdjęć %d z %d wysłana (%d zdj.)" % (nr, len(plan["grupy"]), len(g["zdjecia"])))
            time.sleep(PRZERWA_S * max(1, len(g["zdjecia"])))
        if plan["koniec"]:
            _wywolaj(token, "sendMessage", {"chat_id": czat, "text": plan["koniec"], "disable_web_page_preview": True})
            wynik["wiadomosci"] += 1
    return wynik


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Raport ze zdjęciami na grupę zespołu na Telegramie")
    ap.add_argument("--plan", required=True, help="plik JSON: tekst, grupy zdjęć z podpisami, koniec")
    ap.add_argument("--sucho", action="store_true", help="sprawdź plan i pliki, niczego nie wysyłaj")
    a = ap.parse_args(argv)
    try:
        plan = wczytaj_plan(a.plan)
        zdjec = sum(len(g["zdjecia"]) for g in plan["grupy"])
        print("Plan: tekst %d znaków, grup zdjęć %d, zdjęć %d, koniec %d znaków"
              % (len(plan["tekst"]), len(plan["grupy"]), zdjec, len(plan["koniec"])))
        if a.sucho:
            u = telegram.ustawienia()
            print("Na sucho — nic nie wysłano. Bot włączony: %s, grup zespołu: %d"
                  % (bool(u.get("wlaczony")), len(u.get("grupy") or {})))
            return 0
        w = wyslij(plan)
        print("Wysłano: wiadomości %d, zdjęć %d, grup zespołu %d" % (w["wiadomosci"], w["zdjecia"], w["grupy"]))
        return 0
    except Blad as e:
        print("BŁĄD: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
