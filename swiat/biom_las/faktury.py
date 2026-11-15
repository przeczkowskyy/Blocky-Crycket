# -*- coding: utf-8 -*-
"""Faktury biomu Las (wersja 2 mapy): rola części → wbudowany materiał Roblox (Enum.Material) i korekta koloru.

Jedno miejsce na wszystkie materiały lasu. Moduły budowy nadają częściom nazwy (rolę widać w nazwie: „Ścieżka”, „Skała”,
„Igły”…), a `naloz(s)` po zbudowaniu mapy przypisuje każdej części materiał z tabeli i — dla materiałów z fakturą — mnoży
jej kolor przez korektę jasności (faktura Roblox przyciemnia kolor części; liczby to założenie do sprawdzenia na zrzutach
ze Studio — zmieniasz JEDNĄ liczbę w ROLE i przebudowujesz). Kontrakt: PROJEKT.md, rozdz. 14 „Faktury”.

Zasady:
- faktura tam, gdzie jest powierzchnia, po której się chodzi albo o którą się opiera wzrok z bliska: grunt, ścieżki,
  skały, drewno;
- GŁADKIE (SmoothPlastic) zostają: liście i korony, igły, krzaki, paprocie i kwiaty, kapelusze i trzony grzybów, woda,
  tusz (krawężniki, pierścienie, otwory), kolory-kody i rekwizyty-zabawki (złoty klocek, galareta, kości), tło i chmury.
  Powód: komiksowy walor trzech tonów korony czyta się tylko na gładkiej bryle; faktura na dużych bryłach liści i na
  dalekich sylwetkach migocze i robi z nich szum; kolor-kod musi być czysty;
- Neon zostaje Neonem (światło), części półprzezroczyste (mgła, tafla wody) zostają gładkie;
- kamień: Slate (łupek Ostępów, Grań, menhiry), Sandstone (ściany i półki Wąwozu, rampy), Limestone (uskoki Korony),
  Rock (głazy, kamienie, mur), Pebble (sekretna ścieżka, żwir przy wodzie); jawne Slate w kodzie zostaje Slate.

    from swiat.biom_las import faktury
    brak = faktury.naloz(s)          # lista nazw części bez roli (ma być pusta)
"""
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las.paleta import PALETA  # noqa: E402

# rola: (materiał Enum.Material, korekta koloru, opis). Korekta to liczba (jasność), trójka (mnożniki R, G, B — „ton”)
# albo słownik {"jasne": …, "ciemne": …} (osobno dla kolorów o L* > 60 i ciemniejszych). Liczby DOBRANE NA ZRZUTACH ZE
# STUDIO (15.11, próbka materiałów + 3 rundy ujęć): faktura Roblox ściera nasycenie, Sandstone/Limestone/Rock robią
# z jasnego ciepłego kamienia (`kamien_cieply` E3C3A8) prawie biały marmur, LeafyGrass rysuje na kolorze rude listki.
CIEPLY_KAMIEN = (0.88, 0.80, 0.62)                            # E3C3A8 → C89C68: ochra piaskowca zamiast różowej bieli
ROLE = {
    "trawa":      ("Grass", 1.06, "trawa Łąki, wydeptane podkładki stref, taras górny, wysepka"),
    "runo":       ("LeafyGrass", 1.08, "runo boru: płyta, plamy Kapeluszowa i Ostępów, tarasy Korony, Grań, garby terenu"),
    "igliwie":    ("Ground", 1.05, "płaty igliwia pod sosnami Ostępów"),
    "mech":       ("Grass", 1.0, "czapy mchu na kamieniach i pniach, polanki mchu (podkładki muchomorników)"),
    "ziemia":     ("Ground", 1.05, "dróżki, pierścień polany, korytarz labiryntu, dno rynien, krater, kretowiska"),
    "bruk":       ("Cobblestone", 1.06, "szlaki główne, posadzka Kamiennego Kręgu"),
    "piasek":     ("Sand", 1.0, "wysepka, płycizny pod wodą, łachy"),
    "polka":      ("Grass", (0.90, 1.02, 0.72), "wierzch półek Wąwozu i garby na nim: sucha trawa (Sand wyglądał jak plaża)"),
    "piaskowiec": ("Sandstone", {"jasne": CIEPLY_KAMIEN, "ciemne": 1.0},
                   "ściany i pryzmaty półek Wąwozu (z warstwami), rampy, głazy-stopnie, tama"),
    "wapien":     ("Limestone", {"jasne": (0.84, 0.81, 0.74), "ciemne": 1.0}, "uskoki tarasów Korony"),
    "lupek":      ("Slate", 1.0, "Grań, Wilcza Skała, menhiry, filar, głazy Ostępów"),
    "skala":      ("Rock", {"jasne": (0.80, 0.75, 0.68), "ciemne": 1.12}, "głazy, kamienie, kamyki, mur, kamienie brzegu"),
    "zwir":       ("Pebble", {"jasne": (0.84, 0.80, 0.72), "ciemne": 1.05}, "sekretna ścieżka, łachy żwiru przy strudze"),
    "bloto":      ("Mud", 1.15, "popękane błoto Wyschniętej Kałuży"),
    "drewno":     ("Wood", 1.0, "pnie, konary, korzenie, kłody, słupy, kije, poręcze"),
    "deski":      ("WoodPlanks", 1.0, "pomosty, deski, skrzynie, beczki, ramiona drogowskazów, płotki, tabliczki"),
    "metal":      ("Metal", 1.0, "łańcuchy, kocioł, luneta, obręcze"),
    "tkanina":    ("Fabric", 1.0, "chorągiewki, lina, siedzisko tronu"),
    "jezyny":     ("Fabric", 1.0, "ściany i kępy jeżyn, garby na licach labiryntu, kopce jam: drobny splot gęstych pędów "
                                  "(LeafyGrass dawał „granit z rudymi liśćmi”, Grass — fioletowy dywan w białe kropki)"),
    "gladkie":    ("SmoothPlastic", 1.0, "liście, igły, kwiaty, grzyby, woda, tusz, kody, rekwizyty-zabawki, tło"),
}
KAMIENNE = {"piaskowiec", "wapien", "skala", "zwir"}         # jawne Slate w kodzie → łupek

# kolor ma pierwszeństwo: tusz, biel, złoto, galareta, kody — zawsze gładkie (czysta plama koloru)
KOLORY_GLADKIE = {PALETA[k] for k in ("tusz", "biel", "zloto", "galareta", "pomarancz", "dach_sklep", "dach_brama",
                                      "czerwien", "woda", "woda_gleboka", "jezyna_kolec")}

_ROLE_NAZW = {
    "gladkie": """Igły|Krzak|Kulisa pień|Kulisa korona|Czubek|Paproć|Kwiat|Korona|Korona wierzch|Korona spód|Korona boczna|
        Pasek|Kropka|Jagoda|Kolec|Pień tusz|Kępka|Kapelusz|Kapelusz spód|Kapelusz czubek|Kapelusz szczyt|Trzon|Trzcina|
        Pałka|Wzgórze|Chmura|Chmura spód|Jeżyna liście|Galareta|Bąbel|Kałuża brzeg|Kałuża galarety|Kałuża woda|Woda|
        Brzeg wody|Jezioro|Staw|Staw głębia|Brzeg stawu|Blik|Tęcza|Czapa|Czapa spód|Czapa kępa|Czapa wierzch|Czapa czubek|
        Owoc|Świetlik|Grzybień|Grzybień kwiat|Mały Ukłon|Kapelusik|Wilcze ucho|Stopień-kapelusz|Stopień trzonek|Chatka|
        Chatka kapelusz|Chatka kapelusz spód|Chatka kapelusz czubek|Jama liście|Jama otwór|Szpara|Krawężnik|Kamień-kod|
        Rampa policzek|Punkt interakcji|Pęknięcie|Mgła bagna|Mgiełka|Wodospad|Wodospad pasmo|Woda na grani|Klocek w wodzie|
        Strużka|Strużka rozlewisko|Kaczka|Kaczka głowa|Kaczka dziób|Spławik|Żyłka|Wiaderko|Żaba|Żaba brzuch|Żaba łapa|
        Żaba oko|Żaba źrenica|Żaba pysk|Żaba warga|Żaba język|Jabłko|Słonecznik|Słonecznik łodyga|Słonecznik środek|
        Złoty klocek|Klocek wypustka|Klocek cień|Strzałka|Strzałka grot|Jajo|Jajo liść|Jajo kropka|Kapsel|Złote jajo|
        Jajo wypustka|Paszcza|Kłódka|Kłódka dziurka|Pnie tusz|Chorągiewka maszt|Lampion daszek|Dziupla otwór|Girlanda|
        Legowisko|Kocioł brzeg|Szyld|Szyld rama|Szyld bochenek|Sowa brzuch|Sowa oko|Sowa źrenica|Sowa dziób|Luneta szkło|
        Czaszka-klocek|Oczodół|Żebro|Kość|Kość-klocek|Niewidzialna ściana|Mur miasta|Wieża|Wieża dach|Karczma|Karczma dach|
        Sklep|Sklep kapelusz|Wieża twierdzy|Chorągiew|Chorągiew płat|Ślad bagna|Grzybek|Grzybek kapelusz|Kwiatek|Liść pnącza|
        Pnącze|Wysoka trawa|Lilia|Lilia kwiat|Fala|Piana|Tafla|Tafla jeziora|Tafla stawu|Głębia|Korona zwis|Igły zwis|
        Jarzębina owoc|Gałązka liście|Kępka sucha|Trawa rantu|Tabliczka znak|Jeżyna pęd|Szczelina|Rekwizyt|Ślimak|
        Muszla|Kosz jabłko|Beczka woda|Beczka jabłko|Lampion|Latarenka|Pióro|Płomień|Ogień|Zarodnik|Oko|
        Kryształ|Kryształ czubek|Kryształ odłamek|Blask|Kapsel światło|Chatka okienko|Kamień Powrotu romb|Kokarda|
        Płycizna jeziora|Jeżyna zwis""",
    "trawa": "Plama laka|Wysepka trawa",
    "runo": "Płyta|Plama kapeluszowo|Plama ostepy|Plama serce|Plama korona",
    "igliwie": "Igliwie",
    "mech": "Mech|Mech cień|Mech zwis|Menhir mech|Pal mech|Kładka mech|Dziupla mech|Mech głazu|Mech półki",
    "ziemia": "Plama wawoz|Krater|Bruzda|Kretowisko|Ziemia kretowiska",
    "bruk": "Krąg posadzka|Krąg posadzka środek",
    "piasek": "Wysepka|Płycizna|Łacha",
    "piaskowiec": "Rampa|Głaz-stopień|Półka skalna|Głaz tamy|Głaz szczytowy",
    "lupek": "Menhir|Menhir rant|Menhir czubek|Filar|Próg|Półka|Rant",
    "skala": """Głaz|Głaz wierzch|Kamień|Kamień brzegu|Kamień brodu|Skała muru|Skała muru wierzch|Legowisko węgar|
        Legowisko nadproże|Most łuk|Kamyk|Płyta kamienna|Stos kamieni""",
    "zwir": "Żwir",
    "drewno": """Pień|Konar|Korzeń|Polano|Pniak|Pniak słoje|Kładka pień|Kładka korzenie|Kładka słoje|Pal|Słup|
        Drogowskaz słup|Drogowskaz czapka|Lampion kij|Lampion ramię|Kora|Stopa|Przypora|Talerz korzeni|Zwalony pień|
        Dziupla pień|Dziupla słoje|Maczuga|Maczuga głowica|Maczuga w ziemi|Jama kij|Sowa|Sowa głowa|Sowa ucho|Szyszka|
        Trójnóg|Wędka|Pomost pal|Most słupek|Most poręcz|Wrota słup|Gniazdo belka|Gniazdo dno|Konar-stopień|Korzeń gniazda|
        Korzeń wierzch|Pień bramy|Pień bramy korzeń|Pień Ukłonu|Szyld słup|Wóz dyszel|Koło|Łódka stępka|Łódka żebro|Kłoda|
        Kłoda słoje|Gałązka|Patyk|Płot sztacheta|Płot żerdź|Tabliczka słup|Pień suchy|Konar suchy|Sęk|Stos drewna|
        Korzeń ścieżki|Kulisa pień dąb""",
    "deski": """Pomost deska|Ławka deska|Most pomost|Wóz skrzynia|Wóz burta|Skrzynia|Skrzynia wieko|Skrzynia listwa|Ramię|
        Ramię grot|Skrzynia ukos|Chatka drzwi|Wrota belka|Belka bramy|Tabliczka|Beczka|Beczka brzuch|Beczka wieko|Kosz|Ławka siedzisko|
        Ławka oparcie""",
    "metal": "Łańcuch|Kocioł|Luneta|Lampion łańcuch|Koło piasta|Kłódka kabłąk|Beczka obręcz|Ławka noga",
    "tkanina": "Chorągiewka|Lina|Tron siedzisko",
    "jezyny": "Jeżyna|Ściana jeżyn|Jama kopiec|Jeżyna garb",
}
NAZWY = {}
for _rola, _txt in _ROLE_NAZW.items():
    for _n in _txt.replace("\n", "|").split("|"):
        _m = _n.strip()
        if _m:
            assert _m not in NAZWY, "nazwa w dwóch rolach: " + _m
            NAZWY[_m] = _rola

# zależne od miejsca: (nazwa, fragment ścieżki grupy albo None, klucz koloru albo None) → rola; pierwsza pasująca wygrywa
ZALEZNE = [
    ("Ścieżka", None, "bruk", "bruk"),
    ("Ścieżka", None, "ziemia", "ziemia"),
    ("Ścieżka", None, "kamien_cieply", "zwir"),
    ("Skała", "/Urwiska/gran", None, "lupek"),
    ("Skała", "/Urwiska/korona_", None, "wapien"),
    ("Skała", "/Urwiska/polka_", None, "piaskowiec"),
    ("Skała", "Punkty/WilczaSkala", None, "lupek"),
    ("Skała wierzch", "/Urwiska/gran", None, "lupek"),
    ("Skała wierzch", "/Urwiska/korona_", None, "wapien"),
    ("Skała wierzch", "/Urwiska/polka_", None, "piaskowiec"),
    ("Warstwa", "/Urwiska/gran", None, "lupek"),
    ("Warstwa", "/Urwiska/korona_", None, "wapien"),
    ("Warstwa", "/Urwiska/polka_", None, "piaskowiec"),
    ("Warstwa", None, None, "piaskowiec"),
    ("Poziom", "/Poziomy/gran", None, "lupek"),
    ("Poziom", "/Poziomy/korona_", None, "wapien"),
    ("Poziom", "/Poziomy/polka_", None, "piaskowiec"),
    ("Poziom", "/Poziomy/tama", None, "skala"),
    ("Poziom", "/Poziomy/jezioro_dno", None, "gladkie"),
    ("Poziom wierzch", "/Poziomy/polka_", None, "polka"),
    ("Poziom wierzch", "/Poziomy/korona_t2", None, "trawa"),
    ("Poziom wierzch", None, None, "runo"),
    ("Kopiec", "/Kopce/polana_uklonu", None, "runo"),
    ("Kopiec", None, None, "trawa"),
    ("Zbocze", "/Kopce/polana_uklonu", None, "runo"),
    ("Zbocze", None, None, "trawa"),
    ("Podkładka strefy", None, "runo", "trawa"),
    ("Podkładka strefy", None, "mech", "mech"),
    ("Podkładka strefy", None, "kamien_cokol", "bloto"),
    ("Jeżyna", None, "lisc_ciemny", "gladkie"),                # zielone zwisy liści na licach labiryntu: jak liście
    ("Rant darń", "/Urwiska/polka_", None, "polka"),          # etap 3: darń na skałach rantu półek = wierzch półki
    ("Rant darń", "/Urwiska/korona_t2", None, "trawa"),
    ("Rant darń", None, None, "runo"),
    ("Jeżyna odrost", None, None, "jezyny"),                  # etap 3: ciemny pas pędów u stopy lica labiryntu
    ("Garb", None, "trawa", "trawa"),                          # garb ma fakturę gruntu, na którym leży (kolor = grunt)
    ("Garb", None, "ziemia", "ziemia"),
    ("Garb", None, "bruk_ciemny", "polka"),
    ("Garb", None, None, "runo"),
    ("Skała", None, None, "skala"),
    ("Skała wierzch", None, None, "skala"),
]


def _lstar_hex(hex6):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(hex6[i:i + 2], 16)) for i in (0, 2, 4))
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16


def jasniej(hex6, k):
    """Kolor × korekta: liczba, trójka (R, G, B) albo {"jasne": …, "ciemne": …} (próg L* 60)."""
    if isinstance(k, dict):
        k = k["jasne"] if _lstar_hex(hex6) > 60 else k["ciemne"]
    ks = tuple(k) if isinstance(k, (tuple, list)) else (k, k, k)
    if all(abs(x - 1.0) < 1e-6 for x in ks):
        return hex6
    return "%02X%02X%02X" % tuple(max(0, min(255, int(round(int(hex6[2 * i:2 * i + 2], 16) * ks[i])))) for i in range(3))


def rola(nazwa, grupa, kolor_hex, mat_obecny):
    """Rola części (klucz ROLE) albo None, gdy nazwa nie ma roli."""
    if mat_obecny == "Neon":
        return None
    if "/_Znaczniki" in grupa:                                 # zastępcze bryły podglądu (--znaczniki-widoczne)
        return "gladkie"
    if kolor_hex in KOLORY_GLADKIE:
        return "gladkie"
    for n, g, k, r in ZALEZNE:
        if n != nazwa:
            continue
        if g is not None and g not in grupa:
            continue
        if k is not None and PALETA[k] != kolor_hex:
            continue
        return r
    return NAZWY.get(nazwa)


def naloz(s):
    """Przypisz materiały wszystkim częściom sceny (poza Neonem i częściami półprzezroczystymi) i skoryguj kolory
    materiałów z fakturą. Zwraca posortowaną listę nazw części bez roli (powinna być pusta)."""
    brak = set()
    for c in s.czesci:
        obecny = s.materialy[c[12]]
        if obecny == "Neon":
            continue
        r = rola(c[14], s.grupy[c[1]], c[11], obecny)
        if r is None:
            brak.add(c[14])
            continue
        if 0 < c[13] < 1:                                      # mgła i tafle wody: gładkie, bez korekty
            r = "gladkie"
        if obecny == "Slate" and r in KAMIENNE:
            r = "lupek"
        if obecny == "Fabric":
            r = "tkanina"
        mat, k, _ = ROLE[r]
        c[12] = s._idx(s.materialy, mat)
        c[11] = jasniej(c[11], k)
    return sorted(brak)


def udzialy(s, poziom=0):
    """{grupa najwyższego poziomu (poziom=0) albo „razem”: {materiał: liczba}}."""
    pref = len(s.korzen) + 1
    wyn = {"razem": {}}
    for c in s.czesci:
        g = s.grupy[c[1]][pref:].split("/")[poziom]
        m = s.materialy[c[12]]
        wyn.setdefault(g, {})
        wyn[g][m] = wyn[g].get(m, 0) + 1
        wyn["razem"][m] = wyn["razem"].get(m, 0) + 1
    return wyn
