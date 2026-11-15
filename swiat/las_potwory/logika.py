# -*- coding: utf-8 -*-
"""Logika — czysta matematyka ruchu i odradzania potworów Lasu (lustro zrodla/Logika.luau, PROJEKT.md rozdz. 3.7).

Ten plik jest WIERNĄ KOPIĄ modułu Luau: te same funkcje (nazwy snake_case zamiast camelCase), ta sama kolejność
argumentów, te same wzory i te same przypadki brzegowe. Nie dotyka plików, zegara ani losowości. Używają go:
generuj_dane.py (przeliczenie las → świat, kontrola pojemności) i testy/test_logiki.py (przypadki wzorcowe 3.7a
i symulacja odstępów). Gdy zmieniasz wzór tutaj, zmień go też w zrodla/Logika.luau i w tabeli 3.7a.

Odczytania kontraktu (najprostsze, zapisane też w UWAGI_S.md):
  • yaw liczymy jako atan2(0 − dx, 0 − dz), a nie atan2(−dx, −dz): przy dx = 0 zapis „−dx” daje −0, a wtedy ruch w +Z
    wychodzi −π zamiast π (przypadek T1 przy s = 15 oczekuje 3,1416);
  • minal: „sNowy bliżej sCel niż 0,5” rozumiemy jako odległość ≤ 0,5 (przypadek minal(10, 12.5, 13, 100) = true
    wymaga równości: 13 − 12,5 = 0,5 dokładnie);
  • reszta z dzielenia po pętli wpada zawsze w [0; L) — gdy zaokrąglenie da dokładnie L, zwracamy 0.
"""
import math

INF = math.inf


def _mod(a, L):
    """Reszta z dzielenia w [0; L) — jak operator % w Luau (dzielenie z podłogą), z obcięciem wyniku równego L."""
    d = a % L
    if d >= L:
        d -= L
    if d < 0:
        d = 0.0
    return d


def cel(naraz, maks, gracze):
    """Ile potworów strefa ma mieć przy `gracze` graczach na serwerze (rozdz. 3.5); gracze < 1 liczymy jak 1."""
    g = max(1, gracze)
    pol = math.ceil(naraz / 2)
    if g <= 8:
        c = pol + (naraz - pol) * (g - 1) / 7
    else:
        c = naraz + (maks - naraz) * min(1, (g - 8) / 12)
    return math.floor(c + 0.5)


def czas_odrodzenia(baza, gracze_w_strefie):
    """Czas odrodzenia ze skracaniem 0,15 na każdego gracza ponad pierwszego, najmniej 10 s (rozdz. 3.5)."""
    g = max(1, gracze_w_strefie)
    return max(10, baza / (1 + 0.15 * (g - 1)))


def przod(a, b, L):
    """Odległość „do przodu” po pętli z a do b, w [0; L); L ≤ 0 → nieskończoność."""
    if L <= 0:
        return INF
    return _mod(b - a, L)


def yaw(dx, dz):
    """Kierunek (rad) taki, że CFrame.Angles(0, yaw, 0).LookVector = (dx; dz) znormalizowany (rozdz. 1.2)."""
    return math.atan2(0 - dx, 0 - dz)


def _odcinek(trasa, i, j, t, wstecz):
    x = trasa["x"][i] + (trasa["x"][j] - trasa["x"][i]) * t
    y = trasa["y"][i] + (trasa["y"][j] - trasa["y"][i]) * t
    z = trasa["z"][i] + (trasa["z"][j] - trasa["z"][i]) * t
    dx = trasa["x"][j] - trasa["x"][i]
    dz = trasa["z"][j] - trasa["z"][i]
    if wstecz:
        dx, dz = -dx, -dz
    return x, y, z, yaw(dx, dz)


def punkt_trasy(trasa, s):
    """Punkt (x, y, z) i kierunek yaw na trasie w parametrze s (rozdz. 3.7).

    Pętla (zamknieta = true): n punktów, dl ma n + 1 wpisów, odcinek n wraca z ostatniego punktu do pierwszego.
    Tam i z powrotem (zamknieta = false): dl ma n wpisów, Lp = dl[n], L = 2 × Lp; dla s > Lp punkt L − s i kierunek
    odwrócony. W wierzchołku obowiązuje odcinek, który się w nim KOŃCZY (w s = 0 — pierwszy odcinek).
    L = 0: pierwszy punkt i trasa["yaw"] (albo 0).
    """
    xs, dl, L = trasa["x"], trasa["dl"], trasa["L"]
    n = len(xs)
    if L <= 0 or n < 2:
        return trasa["x"][0], trasa["y"][0], trasa["z"][0], trasa.get("yaw", 0)
    s = _mod(s, L)
    if trasa["zamknieta"]:
        for i in range(n):
            if s <= dl[i + 1]:
                dlug = dl[i + 1] - dl[i]
                t = (s - dl[i]) / dlug if dlug > 0 else 0.0
                return _odcinek(trasa, i, (i + 1) % n, t, False)
        return _odcinek(trasa, n - 1, 0, 1.0, False)
    lp = dl[n - 1]
    if s <= lp:
        for i in range(n - 1):
            if s <= dl[i + 1]:
                dlug = dl[i + 1] - dl[i]
                t = (s - dl[i]) / dlug if dlug > 0 else 0.0
                return _odcinek(trasa, i, i + 1, t, False)
        return _odcinek(trasa, n - 2, n - 1, 1.0, False)
    sw = L - s  # droga powrotna: ten sam punkt co sw na drodze tam
    for i in range(n - 2, -1, -1):
        if sw >= dl[i]:
            dlug = dl[i + 1] - dl[i]
            t = (sw - dl[i]) / dlug if dlug > 0 else 0.0
            return _odcinek(trasa, i, i + 1, t, True)
    return _odcinek(trasa, 0, 1, 0.0, True)


def krok_grup(s, dlugosc, stoi, L, krok, odstep):
    """Nowe położenia czół grup po jednym kroku (rozdz. 3.7, „krokGrup dokładnie”).

    Grupa i przesuwa się o kr_i = min(krok, luka do ogona grupy przed nią + krok tamtej − odstęp), liczone
    jednocześnie (punkt stały, najwyżej 2n + 2 przejść). Stojące mają kr = 0. Brak zbieżności (tylko przy złych danych)
    → wszystkie kr = 0. Luau zwraca dodatkowo drugą wartość: czy obliczenie się zbiegło (serwer robi wtedy warn).
    """
    n = len(s)
    if L <= 0 or n == 0:
        return list(s)
    kr = [0.0 if stoi[i] else krok for i in range(n)]
    zbiezne = False
    for _ in range(2 * n + 2):
        zmiana = False
        for i in range(n):
            if stoi[i]:
                continue
            lim = L - dlugosc[i] - odstep
            for k in range(n):
                if k != i:
                    lim = min(lim, przod(s[i], s[k], L) - dlugosc[k] + kr[k] - odstep)
            nowy = min(max(lim, 0.0), krok)
            if nowy < kr[i]:
                kr[i] = nowy
                zmiana = True
        if not zmiana:
            zbiezne = True
            break
    if not zbiezne:
        kr = [0.0] * n
    return [_mod(s[i] + kr[i], L) for i in range(n)]


def przod_do(s_cel, s, dlugosc, L):
    """Najmniejsza odległość od s_cel do przodu do OGONA którejś grupy; brak grup → nieskończoność."""
    wynik = INF
    for k in range(len(s)):
        wynik = min(wynik, przod(s_cel, s[k], L) - dlugosc[k])
    return wynik


def tyl_do(s_cel, s, L):
    """Najmniejsza odległość od CZOŁA którejś grupy do przodu do s_cel (kto jest najbliżej z tyłu); brak → nieskończoność."""
    wynik = INF
    for k in range(len(s)):
        wynik = min(wynik, przod(s[k], s_cel, L))
    return wynik


def minal(s_stary, s_nowy, s_cel, L):
    """Czy ruch z s_stary do s_nowy przeszedł przez s_cel (albo s_nowy stoi najwyżej 0,5 od s_cel); L ≤ 0 → True."""
    if L <= 0:
        return True
    if przod(s_stary, s_cel, L) <= przod(s_stary, s_nowy, L) + 1e-9:
        return True
    return min(przod(s_nowy, s_cel, L), przod(s_cel, s_nowy, L)) <= 0.5


def w_grupie(s_grupy, miejsce, odstep_w_grupie, L):
    """Parametr pętli członka na miejscu `miejsce` (1 = czoło); L ≤ 0 → 0."""
    if L <= 0:
        return 0.0
    return _mod(s_grupy - (miejsce - 1) * odstep_w_grupie, L)


def rozdzial_startowy(cel_, grup, miejsc):
    """Lista par [grupa, miejsce] (od 1) dla `cel_` potworów przy starcie; cel_ obcięty do grup × miejsc."""
    c = min(cel_, grup * miejsc)
    wynik = []
    for i in range(c):
        if miejsc == 1:
            wynik.append([math.floor(i * grup / c) + 1, 1])
        else:
            wynik.append([i % grup + 1, math.floor(i / grup) + 1])
    return wynik


def poczatkowe_polozenia(n, L):
    """n równo rozstawionych parametrów na pętli: (i − 1) × L / n."""
    return [(i - 1) * L / n for i in range(1, n + 1)]


def wolny_dom(domy, gracze, ostatni, blokada):
    """Pierwszy wolny dom po ostatnio użytym (karuzela; numery od 1). Dom wolny, gdy każdy gracz jest ≥ blokada
    w poziomie. domy i gracze to listy par [x, z]. Brak wolnego → None."""
    n = len(domy)
    for k in range(1, n + 1):
        i = (ostatni + k - 1) % n + 1
        dx, dz = domy[i - 1][0], domy[i - 1][1]
        wolny = True
        for g in gracze:
            if math.hypot(g[0] - dx, g[1] - dz) < blokada:
                wolny = False
                break
        if wolny:
            return i
    return None


def krok_do(x, z, cx, cz, krok):
    """Krok po prostej z (x; z) do (cx; cz) o długości `krok`, bez przeskoczenia celu → (x2, z2, doszedl)."""
    dx, dz = cx - x, cz - z
    d = math.hypot(dx, dz)
    if d <= krok or d <= 0:
        return cx, cz, True
    return x + dx / d * krok, z + dz / d * krok, False


def swiat_z_lasu(x, y, z):
    """Układ lasu → świat Studio: kontener BiomLas w (0; 0; −2000), obrócony o 180° wokół pionu (rozdz. 1.2)."""
    return 0 - x, y, -2000 - z
