# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaWskazowek.luau w Pythonie — ta sama logika wyboru kroku wskazówki (testy i przypadki
wzorcowe w dane.py). Działanie musi być identyczne z Luau (sprawdza testy/test_wskazowek.py w interpreterze luau_mini).

Stan gracza (słownik, wszystkie pola opcjonalne):
  klasa (bool)            — gracz wybrał klasę (atrybut Class)
  ukryte (bool)           — trwa walka, przelot, chmury, mini-gra, wybór klasy albo HUD jest schowany
  wylaczone (bool)        — gracz zamknął wskazówki krzyżykiem
  kraina                  — "las" | "bagno" | None (biom, w którym stoi gracz; None = miasto)
  miejsce                 — "las" | "za_brama" | "miasto" (w biomie: przed / za jego bramą; poza biomami: miasto)
  wygrane, przegrane (int)— walki w tym biomie w tej sesji (w mieście: wszystkie)
  ostatni                 — "wygrana" | "przegrana" | None (wynik ostatniej walki w tym biomie / w ogóle)
  trenowal (bool)         — po ostatniej przegranej gracz był na stanowisku Training Center
  straznik (bool)         — pokonał Strażnika Gaju (atrybut PokonalStraznikaLasu)
  straznik_bagna (bool)   — pokonał Strażnika Topieli (atrybut PokonalStraznikaBagna)
  stan_gracza (bool)      — działa pakiet swiat/stan_gracza (łup, poziomy); bez niego kroki o poziomach się nie pokazują
  trening_wzmacnia (bool) — stan gracza słucha treningu (TreningPodlaczony)
  poziom (int | None)     — atrybut Level
  bagno (bool)            — Bagno stoi w miejscu (kontener BagnoPasGra)
  jajko (bool)            — stoi inkubator biomu, w którym jest gracz (w mieście: lasu; swiat/pety_proba), i Złoto
                            gracza ≥ cena jajka tego biomu (17.11.2026)
  kupione (int)           — ile jajek tego biomu gracz już kupił; krok o jajku tylko do pierwszego jajka biomu
  kowal (bool)            — działa kowal na próbę (kontener KowalProba, gracz ma atrybut KowalDostepne; 18.11.2026)
  kowal_zapas (bool)      — gracz ma zapasowy przedmiot do rozbiórki (KowalZapasy > 0)
  kowal_ulepsz (bool)     — gracz ma Złoto i materiały na ulepszenie (KowalMoznaUlepszyc)
  kowal_ulepszen (int)    — suma poziomów ulepszeń (KowalUlepszen); krok „kowal” tylko do pierwszego ulepszenia
Wynik: None (nic nie pokazujemy) albo {"id": klucz z D["kroki"], "tekst": gotowy napis, "cel": rodzaj celu | None}.
"""


def _krok(D, kid, poziom=None):
    k = D["kroki"][kid]
    tekst = k["tekst"]
    if "%d" in tekst:
        tekst = tekst.replace("%d", str(int(poziom)) if isinstance(poziom, (int, float)) and not isinstance(poziom, bool) else "?")
    return {"id": kid, "tekst": tekst, "cel": k["cel"]}


# kroki „zdobywaj poziomy / Strażnik czeka” każdego biomu (las bez przyrostka)
C_POZIOMY = {"las": "c_poziomy", "bagno": "c_poziomy_bagno", "dzungla": "c_poziomy_dzungla"}
C_STRAZNIK = {"las": "c_straznik", "bagno": "c_straznik_bagno", "dzungla": "c_straznik_dzungla"}


def _postep(D, s, kraina):
    """W biomie przed jego Strażnikiem: przegrana → trening / słabszy potwór; po wygranej → poziomy / Strażnik; inaczej
    potwór. Liczniki walk (wygrane, ostatni, trenowal) są liczone osobno dla każdego biomu."""
    if s.get("ostatni") == "przegrana" and not s.get("trenowal"):
        if s.get("stan_gracza") and s.get("trening_wzmacnia"):
            return _krok(D, "d_trening")
        return _krok(D, "d_slabszy")
    if (s.get("wygrane") or 0) > 0:
        if s.get("stan_gracza"):
            return _krok(D, C_POZIOMY.get(kraina, "c_poziomy"), s.get("poziom"))
        return _krok(D, C_STRAZNIK.get(kraina, "c_straznik"))
    return _krok(D, "b_potwor")


def _miasto(D, s):
    if s.get("straznik"):
        if s.get("straznik_bagna") and s.get("dzungla"):
            return _krok(D, "e_dzungla_miasto")
        return _krok(D, "e_bagno_miasto" if s.get("bagno") else "e_brama_miasto")
    if s.get("ostatni") == "przegrana" and not s.get("trenowal"):
        if s.get("stan_gracza") and s.get("trening_wzmacnia"):
            return _krok(D, "d_trening_miasto")
        return _krok(D, "a_teleport")
    if (s.get("wygrane") or 0) > 0:
        return _krok(D, "c_poziomy_miasto" if s.get("stan_gracza") else "c_straznik_miasto")
    return _krok(D, "a_teleport")


def krok(D, s):
    """Krok główny, a na jego miejscu krok „kowal” — tylko zamiast „zdobywaj poziomy / Strażnik czeka” (c_*), czyli po
    pierwszej wygranej, bez przegranej do odrobienia, poza jajkiem i bramą: nigdy nie przykrywa TELEPORT, pierwszej
    walki, jajka, treningu po przegranej ani drogi do następnego biomu."""
    w = _krok_glowny(D, s)
    if w is None or not w["id"].startswith("c_") or not s.get("kowal") or (s.get("kowal_ulepszen") or 0) > 0:
        return w
    if not (s.get("kowal_zapas") or s.get("kowal_ulepsz")):
        return w
    miasto = (s.get("miejsce") or "miasto") == "miasto"
    kid = "g_kowal_zapas" if s.get("kowal_zapas") else "g_kowal_ulepsz"
    return _krok(D, kid if miasto else kid + "_las")


def _krok_glowny(D, s):
    if s.get("wylaczone") or not s.get("klasa") or s.get("ukryte"):
        return None
    miejsce = s.get("miejsce") or "miasto"
    kraina = s.get("kraina") or ("las" if miejsce in ("las", "za_brama") else None)
    # pierwsze jajko biomu: gdy Złota wystarcza na jajko biomu, w którym jest gracz (w mieście: lasu), a gracz nie kupił
    # jeszcze żadnego jajka tego biomu (nie za bramą — inkubator daleko)
    if s.get("jajko") and not s.get("kupione") and miejsce != "za_brama":
        if miejsce == "miasto" or kraina is None:
            return _krok(D, "f_jajko_miasto")
        return _krok(D, {"bagno": "f_jajko_bagno", "dzungla": "f_jajko_dzungla"}.get(kraina, "f_jajko"))
    if miejsce == "miasto" or kraina is None:
        return _miasto(D, s)
    if kraina == "dzungla":
        if s.get("straznik_dzungli"):
            return _krok(D, "e_koniec_dzungla" if miejsce == "za_brama" else "e_brama_pustynia")
        return _postep(D, s, "dzungla")  # za bramą Dżungli bez Węża serwer cofa — jak w Bagnie
    if kraina == "bagno":
        if s.get("straznik_bagna"):
            if miejsce == "za_brama":
                return _krok(D, "e_dalej_dzungla" if s.get("dzungla") else "e_koniec_bagno")
            return _krok(D, "e_brama_do_dzungli" if s.get("dzungla") else "e_brama_dzungla")
        return _postep(D, s, "bagno")  # za bramą Bagna bez Strażnika serwer cofa — jak w Bagnie
    if s.get("straznik"):
        if miejsce == "za_brama":
            return _krok(D, "e_dalej" if s.get("bagno") else "e_koniec")
        return _krok(D, "e_brama_bagno" if s.get("bagno") else "e_brama")
    return _postep(D, s, "las")  # za bramą lasu bez Strażnika serwer cofa — jak w lesie


def miejsce(x, z, prostokat, brama_x):
    """prostokat = {x1, x2, z1, z2} wejścia lasu (DanePasa.wejscie) albo None; brama_x = DanePasa.brama.x albo None."""
    if not prostokat:
        return "miasto"
    if not (prostokat["x1"] <= x <= prostokat["x2"] and prostokat["z1"] <= z <= prostokat["z2"]):
        return "miasto"
    if brama_x is not None and x > brama_x:
        return "za_brama"
    return "las"


def wynik_walki(napis):
    """Atrybut odtwarzacza OstatniWynik → "wygrana" | "przegrana" | None (remis, przerwana, nieznany)."""
    return napis if napis in ("wygrana", "przegrana") else None


# ------------------------------------------------------------------------------------------------ przypadki
def przypadki(D):
    """Przypadki wzorcowe (sprawdza je też Luau: LogikaWskazowek.sprawdzPrzypadki)."""
    P = {"kroki": [], "miejsca": []}
    baza = {"klasa": True, "miejsce": "miasto", "wygrane": 0, "przegrane": 0}

    def k(opis, **zmiany):
        s = dict(baza)
        s.update(zmiany)
        w = krok(D, s)
        P["kroki"].append({"opis": opis, "stan": s, "id": w and w["id"], "tekst": w and w["tekst"], "cel": w and w["cel"]})

    k("przed wyborem klasy nic", klasa=False)
    k("po wyborze klasy w mieście: teleport")
    k("ukryte (walka, chmury, przelot)", ukryte=True)
    k("wyłączone krzyżykiem", wylaczone=True)
    k("w lesie bez walki: potwór", miejsce="las")
    k("po wygranej w lesie bez stanu gracza: Strażnik", miejsce="las", wygrane=1, ostatni="wygrana")
    k("po wygranej w lesie ze stanem gracza: poziomy", miejsce="las", wygrane=2, ostatni="wygrana", stan_gracza=True, poziom=3)
    k("po wygranej w mieście ze stanem gracza", wygrane=1, ostatni="wygrana", stan_gracza=True, poziom=2)
    k("po wygranej w mieście bez stanu gracza", wygrane=1, ostatni="wygrana")
    k("poziom nieznany", miejsce="las", wygrane=1, ostatni="wygrana", stan_gracza=True)
    k("po przegranej w lesie, trening wzmacnia: do miasta", miejsce="las", przegrane=1, ostatni="przegrana",
      stan_gracza=True, trening_wzmacnia=True)
    k("po przegranej w mieście, trening wzmacnia: trener", przegrane=1, ostatni="przegrana", stan_gracza=True,
      trening_wzmacnia=True)
    k("po przegranej bez stanu gracza w lesie: słabszy potwór", miejsce="las", przegrane=1, ostatni="przegrana")
    k("po przegranej bez stanu gracza w mieście: teleport", przegrane=1, ostatni="przegrana")
    k("po przegranej i treningu: dalej po wygranych", miejsce="las", wygrane=1, przegrane=1, ostatni="przegrana",
      trenowal=True, stan_gracza=True, trening_wzmacnia=True, poziom=4)
    k("po przegranej i treningu bez wygranych: potwór", miejsce="las", przegrane=1, ostatni="przegrana", trenowal=True)
    k("stan gracza bez treningu: przegrana → słabszy", miejsce="las", przegrane=1, ostatni="przegrana", stan_gracza=True)
    k("Strażnik pokonany, w lesie: brama", miejsce="las", wygrane=5, ostatni="wygrana", straznik=True)
    k("Strażnik pokonany, w mieście", straznik=True, wygrane=5, ostatni="wygrana")
    k("Strażnik pokonany, przegrana później — brama wygrywa", miejsce="las", straznik=True, ostatni="przegrana")
    k("za bramą bez Bagna", miejsce="za_brama", straznik=True)
    k("za bramą z Bagnem", miejsce="za_brama", straznik=True, bagno=True)
    k("za bramą bez Strażnika (cofany) jak las", miejsce="za_brama")
    k("Strażnik pokonany, ale ukryte", miejsce="las", straznik=True, ukryte=True)
    k("Strażnik lasu pokonany, jest Bagno: brama do Bagna", miejsce="las", kraina="las", straznik=True, bagno=True)
    k("Strażnik lasu pokonany, jest Bagno, w mieście: TELEPORT → Bagno", straznik=True, bagno=True)
    k("w Bagnie bez walki: potwór", kraina="bagno", miejsce="las", straznik=True, bagno=True)
    k("w Bagnie po wygranej ze stanem gracza: poziomy, Strażnik Topieli", kraina="bagno", miejsce="las", straznik=True,
      bagno=True, wygrane=1, ostatni="wygrana", stan_gracza=True, poziom=12)
    k("w Bagnie po wygranej bez stanu gracza", kraina="bagno", miejsce="las", straznik=True, bagno=True, wygrane=2,
      ostatni="wygrana")
    k("w Bagnie po przegranej, trening wzmacnia: do miasta", kraina="bagno", miejsce="las", straznik=True, bagno=True,
      przegrane=1, ostatni="przegrana", stan_gracza=True, trening_wzmacnia=True)
    k("Strażnik Topieli pokonany: brama do Dżungli", kraina="bagno", miejsce="las", straznik=True, straznik_bagna=True,
      bagno=True)
    k("za bramą Bagna", kraina="bagno", miejsce="za_brama", straznik=True, straznik_bagna=True, bagno=True)
    k("za bramą Bagna bez Strażnika Topieli (cofany)", kraina="bagno", miejsce="za_brama", straznik=True, bagno=True)
    k("Złoto na jajko w lesie: inkubator", miejsce="las", kraina="las", wygrane=3, ostatni="wygrana", jajko=True,
      kupione=0)
    k("Złoto na jajko w mieście: TELEPORT", wygrane=3, ostatni="wygrana", jajko=True)
    k("Złoto na jajko po przegranej — jajko wygrywa", miejsce="las", przegrane=1, ostatni="przegrana", jajko=True,
      stan_gracza=True, trening_wzmacnia=True)
    k("Złoto na jajko, ale kupił już jajko lasu", miejsce="las", wygrane=3, ostatni="wygrana", jajko=True, kupione=1)
    k("Złoto na jajko Bagna w Bagnie: inkubator przy pomoście", kraina="bagno", miejsce="las", straznik=True, bagno=True,
      jajko=True, kupione=0)
    k("Złoto na jajko Bagna, ale kupił już jajko Bagna", kraina="bagno", miejsce="las", straznik=True, bagno=True,
      jajko=True, kupione=2)
    k("Złoto na jajko za bramą: bez kroku o jajku", miejsce="za_brama", straznik=True, jajko=True)
    k("Złoto na jajko za bramą Bagna: bez kroku o jajku", kraina="bagno", miejsce="za_brama", straznik=True,
      straznik_bagna=True, bagno=True, jajko=True)
    k("Złoto na jajko, ale ukryte", miejsce="las", jajko=True, ukryte=True)
    # Dżungla (trzeci biom, 18.11.2026)
    dz = {"straznik": True, "straznik_bagna": True, "bagno": True, "dzungla": True}
    k("Strażnik Topieli pokonany, jest Dżungla: brama do Dżungli", kraina="bagno", miejsce="las", **dz)
    k("za bramą Bagna, jest Dżungla", kraina="bagno", miejsce="za_brama", **dz)
    k("Strażnik Topieli pokonany, jest Dżungla, w mieście: TELEPORT → Dżungla", **dz)
    k("w Dżungli bez walki: potwór", kraina="dzungla", miejsce="las", **dz)
    k("Złoto na jajko Dżungli w Dżungli: inkubator na tarasie", kraina="dzungla", miejsce="las", jajko=True, kupione=0,
      **dz)
    k("Złoto na jajko Dżungli, ale kupił już jajko Dżungli", kraina="dzungla", miejsce="las", jajko=True, kupione=1, **dz)
    k("w Dżungli po wygranej ze stanem gracza: poziomy, Wąż Stu Lian", kraina="dzungla", miejsce="las", wygrane=1,
      ostatni="wygrana", stan_gracza=True, poziom=18, **dz)
    k("w Dżungli po wygranej bez stanu gracza", kraina="dzungla", miejsce="las", wygrane=2, ostatni="wygrana", **dz)
    k("Wąż Stu Lian pokonany: brama do Pustyni", kraina="dzungla", miejsce="las", straznik_dzungli=True, **dz)
    k("za bramą Dżungli", kraina="dzungla", miejsce="za_brama", straznik_dzungli=True, **dz)
    # kowal na próbę (18.11.2026): tylko zamiast c_*, do pierwszego ulepszenia
    kow = {"kowal": True, "kowal_zapas": True, "kowal_ulepszen": 0}
    k("kowal: zapas w mieście po wygranej", wygrane=2, ostatni="wygrana", stan_gracza=True, poziom=3, **kow)
    k("kowal: zapas w lesie po wygranej → Kamień Powrotu", miejsce="las", kraina="las", wygrane=2, ostatni="wygrana",
      stan_gracza=True, poziom=3, **kow)
    k("kowal: ulepszenie w Bagnie", kraina="bagno", miejsce="las", straznik=True, bagno=True, wygrane=1,
      ostatni="wygrana", stan_gracza=True, poziom=12, kowal=True, kowal_ulepsz=True)
    k("kowal: przed pierwszą walką — potwór", miejsce="las", **kow)
    k("kowal: w mieście przed walką — TELEPORT", **kow)
    k("kowal: jajko ważniejsze", miejsce="las", wygrane=2, ostatni="wygrana", jajko=True, kupione=0, **kow)
    k("kowal: po przegranej — trening ważniejszy", miejsce="las", wygrane=1, przegrane=1, ostatni="przegrana",
      stan_gracza=True, trening_wzmacnia=True, **kow)
    k("kowal: po Strażniku — brama ważniejsza", miejsce="las", wygrane=5, ostatni="wygrana", straznik=True, **kow)
    k("kowal: po pierwszym ulepszeniu — nic", miejsce="las", wygrane=2, ostatni="wygrana", stan_gracza=True,
      kowal=True, kowal_zapas=True, kowal_ulepszen=1)
    k("kowal: bez kontenera KowalProba — nic", miejsce="las", wygrane=2, ostatni="wygrana", stan_gracza=True,
      kowal_zapas=True, kowal_ulepsz=True)
    k("kowal: nic do rozbiórki ani ulepszenia", miejsce="las", wygrane=2, ostatni="wygrana", kowal=True)
    pr = {"x1": 1056, "x2": 2076, "z1": -760, "z2": -640}
    for x, z, br in [(1114, -700, 2034), (2034, -700, 2034), (2046, -700, 2034), (990, -697, 2034), (1500, -800, 2034),
                     (1056, -760, 2034), (2076, -640, 2034), (1500, -700, None), (0, 0, 2034)]:
        P["miejsca"].append({"x": x, "z": z, "prostokat": pr, "brama": br, "wynik": miejsce(x, z, pr, br)})
    P["miejsca"].append({"x": 1500, "z": -700, "prostokat": None, "brama": 2034, "wynik": miejsce(1500, -700, None, 2034)})
    return P
