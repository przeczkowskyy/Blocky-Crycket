#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plan Dżungli jako odcinka wąskiego pasa — PROPOZYCJA, nic tu nie jest kanonem.

    python -B swiat/dzungla_pas/plan.py          # → swiat/dzungla_pas/plan_dzungli.json + tabela czasów i potworów

Format jak plan Bagna (swiat/bagno_pas/plan_bagna.json) i lasu (swiat/biom_las/pas/plan_pasa.json): pas, swiat,
przegrody, przejscia, miejsca, strefy, straznik, przelot_kamery, punkty_przybycia, czas. Brama na końcu to
`brama_pustyni` (w Bagnie `brama_dzungli`), brama za plecami przybywającego to `brama_bagna` (brama do Dżungli Bagna).

UKŁAD = UKŁAD BAGNA PRZESUNIĘTY O +940 st WZDŁUŻ PASA (D = 940). Każda liczba u poniżej jest zapisana jako
„liczba Bagna + D”, żeby przycinarka (swiat/biomy/przycinarka.py, D-096) mogła zostawić z projektu Dżungli te same
odcinki co z Bagna, przesunięte o +940. Kontrola (sprawdz.py) porównuje plan z planem Bagna co do studa.
Położenie: ta sama oś i szerokość co las-pas i Bagno (świat = (1100 + u; y; −700 + v), bez obrotu). Dżungla zaczyna się
za bramą do Dżungli z planu Bagna (u 1874) i kończy na u 2820 (rezerwacja „kolejne_biomy” w planie Bagna); punkt
przybycia u 1894 — też z planu Bagna (punkty_przybycia → dzungla).
"""
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biom_las.pas.sprawdz_plan import obwod  # noqa: E402

PLAN_BAGNA = os.path.join(REPO, "swiat", "bagno_pas", "plan_bagna.json")
PLIK = os.path.join(TU, "plan_dzungli.json")
D = 940                                   # przesunięcie względem Bagna wzdłuż pasa (st)
STATUS_POZIOMOW = ("propozycja: `poziomy` = 17–23 rosnąco przez przegrody (zlecenie 18.11.2026; gra i tak nadpisuje "
                   "poziomy swoimi — Bagno ma POZIOMY_STREF w swiat/bagno_pas_gra/generuj_dane.py), `poziomy_rowny` = "
                   "tempo równe z swiat/biomy/PLAN_BIOMOW.md (Dżungla 25–35)")


def wczytaj_bagno(plik=PLAN_BAGNA):
    with open(plik, encoding="utf-8") as f:
        return json.load(f)


def petla_kojca(cu):
    """Pętla 8 węzłów jak w lesie i Bagnie: zaokrąglony prostokąt 36 × 44 wokół (cu; 0)."""
    return [[cu + 18.0, 0.0], [round(cu + 16.3, 1), 17.5], [cu, 22.0], [round(cu - 16.3, 1), 17.5], [cu - 18.0, 0.0],
            [round(cu - 16.3, 1), -17.5], [cu, -22.0], [round(cu + 16.3, 1), -17.5]]


def petla_leza(cu):
    return [[cu + 24.0, 0.0], [round(cu + 11.9, 1), 16.0], [round(cu - 11.9, 1), 16.0], [cu - 24.0, 0.0],
            [round(cu - 11.9, 1), -16.0], [round(cu + 11.9, 1), -16.0]]


# --------------------------------------------------------------------------- potwory Dżungli (modele już są)
# wymiary: z danych aktorów swiat/test_walki2/dane/<model>.json (wymiary.wysokosc / glebokosc / szerokosc), zaokrąglone
POTWORY = {
    "Zwijogon": {
        "klasa": "Zwiadowca", "ranga": "zwykły", "przegroda": "zwijogony", "wys": 3.5, "dl": 5.4, "model": "zwijogon",
        "ksztalt": "kameleon z liści na pazurzastych łapach: wąski, wysoki tułów jak liść na sztorc, grzebień z liściowych "
                   "ząbków, łeb z hełmem, oczy na wieżyczkach, ogon zwinięty w ślimak",
        "kolor": "zieleń 2FA34A / 6CCB4A, żółty pas wzdłuż boku i czerwona krawędź hełmu (E5392B / F2B030), turkusowy "
                 "pierścień oka 2EC4B6, jasne pazury",
        "walka": "szybki i zwinny: często unika; „rozszarpanie” (cięcie na krzyż) rani krwawieniem, „skupienie” — "
                 "kameleon wtapia się w liście i celuje",
        "dom": "szałas z dwóch olbrzymich liści pod ścianą (ciemne wejście, paproć)",
        "predkosc": 9, "odrodzenie_s": 12,
    },
    "Gębokwiat": {
        "klasa": "Mag", "ranga": "zwykły", "przegroda": "gebokwiaty", "wys": 5.1, "szer": 3.7, "model": "gebokwiat",
        "ksztalt": "wielki kwiat z paszczą na krótkich korzeniach-nóżkach: tarcza ośmiu czerwonych płatków na grubej "
                   "łodydze, w środku żółta tarcza z paszczą i oczami, dwa liście-ręce, cebulka",
        "kolor": "płatki E5392B z żółtymi czubkami, tarcza F2B030, łodyga i liście 2FA34A / 6CCB4A, korzenie 5C3A22",
        "walka": "kłapnięcie paszczą jest słabe, ale usypiający pyłek (umiejętność silnika `lodowy_pocisk` w szacie pyłku) "
                 "rani magią i spowalnia; mało życia",
        "dom": "grządka ze świecącym pąkiem i sadzonkami pod ścianą",
        "predkosc": 4, "odrodzenie_s": 15,
    },
    "Kokosowy Siłacz": {
        "klasa": "Wojownik", "ranga": "zwykły", "przegroda": "kokosy", "wys": 7.1, "szer": 6.4, "model": "kokosowy_silacz",
        "ksztalt": "krępa małpa-siłacz: ogromne barki, łeb nisko, długie ręce z kokosami w pięściach, pas z liany ze "
                   "złotą klamrą-kwiatem, opaska z liści",
        "kolor": "futro 5C3A22, pierś i twarz B07A44 / D9A066, kokosy brązowe, liście 2FA34A / 6CCB4A, kwiat E5392B",
        "walka": "ciężki i twardy: gruba skóra (Pancerz), sierp kokosem, „cięcie” oboma kokosami z góry; rzadko unika",
        "dom": "legowisko z liści pod ściętą palmą i stos kokosów",
        "predkosc": 6, "odrodzenie_s": 18,
    },
    "Pancernik Ruin": {
        "klasa": "Wojownik", "ranga": "rzadki", "przegroda": "ruiny", "wys": 4.4, "dl": 7.4, "model": "pancernik_ruin",
        "ksztalt": "pancernik obrośnięty płytami starego kamienia z rytami i mchem, świecące turkusowe szczeliny, ryj "
                   "w kamiennym hełmie, ogon z kamiennych pierścieni",
        "kolor": "kamień 8E8A7E w trzech odcieniach, mech 6CCB4A / 2FA34A, skóra B07A44, szczeliny turkus 2EC4B6 (Neon)",
        "walka": "rzadki i twardy: szarża kamiennym hełmem rani fizycznie, „kamienna skóra” zwija go w kulę (tarcza na "
                 "siebie) — dłuższa walka",
        "dom": "Zapadła Kaplica pod lewą ścianą (nora w gruzach obok)",
        "predkosc": 5, "odrodzenie_s": 150,
    },
    "Wąż Stu Lian": {
        "klasa": "strażnik (obrażenia pół na pół: fizyczne i magiczne)", "ranga": "strażnik", "przegroda": "krag",
        "wys": 17.3, "szer": 11.0, "model": "waz_stu_lian",
        "ksztalt": "ogromny wąż spleciony z lian i pnączy, zwinięty w spiralę, szyja łukiem, na głowie wachlarz siedmiu "
                   "czerwonych płatków jak kaptur",
        "kolor": "liany 2FA34A / 1F7A36 / 6CCB4A, pasma drewna 5C3A22, kaptur E5392B / F2B030, krople rosy 2EC4B6",
        "walka": "dużo życia; ukąszenie z szarpaniem (fizyczne, krwawienie), plucie jadem (magia, trucizna)",
        "dom": "kamienny krąg na wyspie w turkusowej sadzawce",
        "predkosc": 0, "odrodzenie_s": 120,
    },
}


def zbuduj(plan_bagna=None):
    B = plan_bagna or wczytaj_bagno()
    rez = {b["id"]: b for b in B["kolejne_biomy"]}
    dz_rez, pu_rez = rez["dzungla"], rez["pustynia"]
    przyb_b = {p["id"]: p for p in B["punkty_przybycia"]}["dzungla"]
    brama_b = {m["id"]: m for m in B["miejsca"]}["brama_dzungli"]
    u0 = float(brama_b["u"])                           # 1874 — brama Bagna = początek Dżungli
    u1 = float(dz_rez["u_do"])                         # 2820 — koniec rezerwacji Dżungli
    sw = B["swiat"]

    przegrody = [
        {"id": "wejscie", "nazwa": "Taras Przybycia", "u_od": 940 + D, "u_do": 1004 + D, "kolor": "8FC77A",
         "opis": "przybycie teleportem i z Bagna przez bramę; kamienny taras ze znakiem, stanowisko jajka, Kamień Powrotu; "
                 "strefa spokoju; tu startuje przelot",
         "pod": [], "strefy": []},
        {"id": "zwijogony", "nazwa": "Polana Zwijogonów", "u_od": 1016 + D, "u_do": 1208 + D, "kolor": "A6D77A",
         "opis": "trzy słoneczne polanki w paprociach pod liśćmi-parasolami, plamy światła; Zwijogony poziomów rosnących",
         "pod": [{"id": "polana_paproci", "nazwa": "Polana Paproci", "u_od": 1016 + D, "u_do": 1080 + D},
                 {"id": "polana_slonca", "nazwa": "Polana Słońca", "u_od": 1080 + D, "u_do": 1144 + D},
                 {"id": "polana_pnaczy", "nazwa": "Polana Pnączy", "u_od": 1144 + D, "u_do": 1208 + D}],
         "strefy": ["z1", "z2", "z3"]},
        {"id": "gebokwiaty", "nazwa": "Kwietnik Gębokwiatów", "u_od": 1228 + D, "u_do": 1420 + D, "kolor": "E7A07A",
         "opis": "ciemna, wilgotna ziemia z grządkami czerwonych i żółtych kwiatów, świecące kwiaty, niskie żywopłoty "
                 "kwiatowe 0,8 dzielą trzy kojce (przerwa 24 na środku); Gębokwiaty",
         "pod": [{"id": "czerwone_grzadki", "nazwa": "Czerwone Grządki", "u_od": 1228 + D, "u_do": 1292 + D},
                 {"id": "zlote_kielichy", "nazwa": "Złote Kielichy", "u_od": 1292 + D, "u_do": 1356 + D},
                 {"id": "swietlisty_kwietnik", "nazwa": "Świetlisty Kwietnik", "u_od": 1356 + D, "u_do": 1420 + D}],
         "strefy": ["g1", "g2", "g3"]},
        {"id": "kokosy", "nazwa": "Gaj Kokosów", "u_od": 1436 + D, "u_do": 1628 + D, "kolor": "D9B27E",
         "opis": "piaszczysta ziemia pod palmami, stosy kokosów, Kaskada Gaju pod prawą ścianą; Kokosowi Siłacze (ciężcy, "
                 "mniej naraz)",
         "pod": [{"id": "palmowy_zagajnik", "nazwa": "Palmowy Zagajnik", "u_od": 1436 + D, "u_do": 1500 + D},
                 {"id": "kokosowa_lacha", "nazwa": "Kokosowa Łacha", "u_od": 1500 + D, "u_do": 1564 + D},
                 {"id": "gaj_starych_palm", "nazwa": "Gaj Starych Palm", "u_od": 1564 + D, "u_do": 1628 + D}],
         "strefy": ["o1", "o2", "o3"]},
        {"id": "ruiny", "nazwa": "Ruiny Pancernika", "u_od": 1644 + D, "u_do": 1744 + D, "kolor": "B5BDA3",
         "opis": "spękana kamienna posadzka, złamane kolumny i głowa posągu, Zapadła Kaplica pod lewą ścianą; jeden "
                 "Pancernik Ruin (rzadki, twardy)",
         "pod": [], "strefy": ["t1"]},
        {"id": "krag", "nazwa": "Krąg Stu Lian", "u_od": 1760 + D, "u_do": 1880 + D, "kolor": "8ED3C9",
         "opis": "okrągła kamienna posadzka na wyspie w turkusowej sadzawce, krąg omszałych filarów z lianami, Świątynia "
                 "Stu Lian; Wąż Stu Lian; za nim brama do Pustyni",
         "pod": [], "strefy": ["straznik"]},
    ]
    przejscia = [
        {"id": "turkusowy_strumyk", "nazwa": "Turkusowy strumyk", "miedzy": ["wejscie", "zwijogony"], "u_od": 1004 + D,
         "u_do": 1016 + D, "otwarcie": [-36, 36], "wys_w_otwarciu": 1.6, "wys_reszty": 0, "blokuje": False,
         "woda": [1006 + D, 1014 + D], "kladka": [-6, 6],
         "opis": "płytki turkusowy strumyk w poprzek pasa (woda bez kolizji, przejdzie się wszędzie), mostek z desek 12 "
                 "szer. na osi, kamienie brzegu"},
        {"id": "mostek_nad_kaskada", "nazwa": "Mostek nad Kaskadą", "miedzy": ["zwijogony", "gebokwiaty"], "u_od": 1208 + D,
         "u_do": 1228 + D, "otwarcie": [-36, 36], "wys_w_otwarciu": 1.6, "wys_reszty": 0, "blokuje": False,
         "woda": [1211 + D, 1225 + D], "kladka": [-6, 6],
         "opis": "szerszy, głębszy strumień (bez kolizji) spływa kaskadami ze skalnych progów w kulisach; kamienny mostek "
                 "12 z balustradą do 1,4"},
        {"id": "bambusowa_przesieka", "nazwa": "Bambusowa przesieka", "miedzy": ["gebokwiaty", "kokosy"], "u_od": 1420 + D,
         "u_do": 1436 + D, "otwarcie": [-16, 16], "wys_w_otwarciu": 0, "wys_reszty": 6, "blokuje": False,
         "opis": "ściany bambusa 5–6 wys. od obu ścian zwężają przejście do 32"},
        {"id": "kamienne_schody", "nazwa": "Omszałe schody", "miedzy": ["kokosy", "ruiny"], "u_od": 1628 + D, "u_do": 1644 + D,
         "otwarcie": [-14, 14], "wys_w_otwarciu": 0.4, "wys_reszty": 9, "blokuje": False,
         "opis": "mur ruin z omszałych bloków 6–9 wys. od ścian, po murze pną się kamienne schody; przejście 28 z niskim "
                 "kamiennym progiem (0,4) i kamieniami z jarzącym się znakiem (ostrzeżenie)"},
        {"id": "brama_posagow", "nazwa": "Brama Posągów", "miedzy": ["ruiny", "krag"], "u_od": 1744 + D, "u_do": 1760 + D,
         "otwarcie": [-14, 14], "wys_w_otwarciu": 0, "wys_reszty": 1.2, "blokuje": False,
         "posagi": [[1752 + D, -16], [1752 + D, 16]],
         "opis": "dwa kamienne posągi strażników (12) z jarzącymi się oczami po bokach osi, reszta to niskie korzenie i "
                 "kamienie ≤ 1,2; widać Krąg"},
    ]
    miejsca = [
        {"id": "przybycie", "nazwa": "Przybycie (teleport i wejście z Bagna)", "u": przyb_b["u"], "v": przyb_b["v"], "y": 0,
         "patrz": list(przyb_b["patrz"]), "opis": "punkt przybycia „dzungla” z planu Bagna; twarzą wzdłuż pasa"},
        {"id": "jajko", "nazwa": "Stanowisko jajka (inkubator Dżungli)", "u": 972 + D, "v": 22, "y": 0, "r": 6, "e": True,
         "opis": "to samo stanowisko co w lesie i Bagnie (podest 12 × 12 z punktem E) na kamiennej posadzce — jajko "
                 "Dżungli zrobi agent petów (D-059, D-060)"},
        {"id": "kamien_powrotu", "nazwa": "Kamień Powrotu", "u": 948 + D, "v": -24, "y": 0, "r": 3, "e": True,
         "opis": "E → miasteczko (jak w lesie i Bagnie)"},
        {"id": "brama_bagna", "nazwa": "Brama do Dżungli (Bagno-pas)", "u": u0, "v": 0, "y": 0, "otwarcie": list(brama_b["otwarcie"]),
         "e": False, "opis": "palisada Bagna za plecami przybywającego (Workspace/BagnoPas/BramaDzungli) — Dżungla jej nie buduje"},
        {"id": "brama_pustyni", "nazwa": "Brama do Pustyni", "u": u1 - 6, "v": 0, "y": 0, "otwarcie": [-8, 8], "e": False,
         "opis": "mur ruin z omszałych bloków przez cały pas, wrota 16 szer. między filarami ze znakiem słońca; zamknięte "
                 "dla gracza, póki nie pokona Węża Stu Lian"},
        {"id": "odrodzenie", "nazwa": "Odrodzenie po przegranej", "u": przyb_b["u"], "v": 0, "y": 0,
         "opis": "jak w lesie i Bagnie: na razie walka wraca gracza w miejsce startu walki"},
    ]
    zn = [
        {"id": "chatka_na_drzewie", "nazwa": "Chatka na Drzewie", "u": 1144 + D, "v": 30, "r": 6, "wys": 25,
         "opis": "chatka z liściastym dachem na pomoście wokół pnia olbrzymiego drzewa, drabinka z lian, świecące okno — "
                 "widać ją z wejścia"},
        {"id": "wielki_kielich", "nazwa": "Wielki Kielich", "u": 1356 + D, "v": 32, "r": 5, "wys": 21, "korona": {"r": 8, "od": 13},
         "opis": "olbrzymi kwiat na grubej łodydze: kielich z ośmiu czerwonych płatków r 8 na wys. 13–21, złota tarcza, "
                 "jarzące się pręciki"},
        {"id": "kaskada_gaju", "nazwa": "Kaskada Gaju", "u": 1564 + D, "v": 30, "r": 7, "wys": 25,
         "opis": "omszałe urwisko w prawych kulisach, z którego spada wodospad do turkusowej sadzawki pod ścianą"},
        {"id": "zapadla_kaplica", "nazwa": "Zapadła Kaplica", "u": 1724 + D, "v": -30, "r": 7, "wys": 17,
         "opis": "ruina kamiennej kaplicy z zapadniętym dachem i drzewem na szczycie, ciemne wejście z jarzącym się znakiem — "
                 "dom Pancernika Ruin"},
        {"id": "posag_lewy", "nazwa": "Posąg Strażnika (lewy)", "u": 1752 + D, "v": -16, "r": 2.5, "wys": 13},
        {"id": "posag_prawy", "nazwa": "Posąg Strażnika (prawy)", "u": 1752 + D, "v": 16, "r": 2.5, "wys": 13},
        {"id": "swiatynia_stu_lian", "nazwa": "Świątynia Stu Lian", "u": 1848 + D, "v": 27, "r": 9, "wys": 34,
         "opis": "schodkowa świątynia z czterech tarasów (16 → 7 st) z kapliczką i jarzącym się znakiem na szczycie (ok. 34) — cel "
                 "widoczny wzdłuż całej Dżungli; stoi z boku osi"},
    ]
    # --- strefy: (id, przegroda, pod, potwór, środek u, poziomy rosnące, poziomy równe, naraz, max)
    S = [
        ("z1", "zwijogony", "polana_paproci", "Zwijogon", 1048 + D, [17, 17], [25, 26], 4, 5),
        ("z2", "zwijogony", "polana_slonca", "Zwijogon", 1112 + D, [17, 18], [26, 27], 4, 5),
        ("z3", "zwijogony", "polana_pnaczy", "Zwijogon", 1176 + D, [18, 18], [27, 28], 4, 5),
        ("g1", "gebokwiaty", "czerwone_grzadki", "Gębokwiat", 1260 + D, [19, 19], [28, 29], 4, 5),
        ("g2", "gebokwiaty", "zlote_kielichy", "Gębokwiat", 1324 + D, [19, 20], [29, 30], 4, 5),
        ("g3", "gebokwiaty", "swietlisty_kwietnik", "Gębokwiat", 1388 + D, [20, 20], [30, 31], 4, 5),
        ("o1", "kokosy", "palmowy_zagajnik", "Kokosowy Siłacz", 1468 + D, [21, 21], [31, 32], 3, 4),
        ("o2", "kokosy", "kokosowa_lacha", "Kokosowy Siłacz", 1532 + D, [21, 22], [32, 33], 3, 4),
        ("o3", "kokosy", "gaj_starych_palm", "Kokosowy Siłacz", 1596 + D, [22, 22], [33, 34], 3, 4),
    ]
    zach = {"Zwijogon": "przemyka susami po polanie, przywiera do ziemi i krąży oczami; odwraca się do gracza w promieniu 18",
            "Gębokwiat": "drepcze na korzeniach między grządkami, przystaje i kołysze płatkami",
            "Kokosowy Siłacz": "chodzi ciężko po gaju, przystaje i stuka kokosami"}
    strefy = []
    for sid, pb, pod, pot, cu, poz, poz_r, naraz, mx in S:
        tr = petla_kojca(float(cu))
        strefy.append({
            "id": sid, "podbiom": pb, "pod": pod, "potwor": pot, "klasa": POTWORY[pot]["klasa"], "wariant": None,
            "model": POTWORY[pot]["model"],
            "poziomy": poz, "poziomy_rowny": poz_r, "poziomy_status": STATUS_POZIOMOW, "naraz": naraz, "max": mx,
            "srodek": [float(cu), 0.0], "r": 28, "y": 0, "pole": [cu - 28, cu + 28, -34, 34],
            "dom": {"opis": POTWORY[pot]["dom"], "pts": [[cu - 6.0, -34.0], [cu + 6.0, 34.0]]},
            "trasa": tr, "liczba_wezlow": len(tr), "odrodzenie_s": POTWORY[pot]["odrodzenie_s"],
            "zachowanie": zach[pot], "grupa": None, "obwod": round(obwod(tr + [tr[0]]), 1),
            "pojemnosc": int(obwod(tr + [tr[0]]) // 25)})
    tr = petla_leza(1694.0 + D)
    strefy.append({
        "id": "t1", "podbiom": "ruiny", "pod": None, "potwor": "Pancernik Ruin", "klasa": POTWORY["Pancernik Ruin"]["klasa"],
        "wariant": None, "model": POTWORY["Pancernik Ruin"]["model"], "poziomy": [22, 22], "poziomy_rowny": [34, 34],
        "poziomy_status": STATUS_POZIOMOW, "naraz": 1, "max": 1,
        "srodek": [1694.0 + D, 0.0], "r": 29, "y": 0, "pole": [1648 + D, 1740 + D, -34, 34],
        "dom": {"opis": POTWORY["Pancernik Ruin"]["dom"], "pts": [[1700.0 + D, -34.0]]}, "trasa": tr, "liczba_wezlow": len(tr),
        "odrodzenie_s": 150, "zachowanie": "węszy ryjem między kolumnami, przysiada przy kaplicy; przy graczu w promieniu 25 "
                                           "zwija się w kulę i rozwija",
        "grupa": None, "obwod": round(obwod(tr + [tr[0]]), 1), "pojemnosc": int(obwod(tr + [tr[0]]) // 25),
        "odrodzenie_stale": True, "uwaga": "rzadki: jeden naraz, stałe odrodzenie (jak Leśny Troll i Ropucha); wspólny czy "
                                          "osobny — wybór"})

    straznik = {
        "potwor": "Wąż Stu Lian", "klasa": POTWORY["Wąż Stu Lian"]["klasa"], "model": POTWORY["Wąż Stu Lian"]["model"],
        "poziom": 23, "poziom_rowny": 35, "poziomy_status": STATUS_POZIOMOW, "miejsce": [1814 + D, 0], "y": 0.3,
        "yaw_swiat": 1.5708, "patrzy": "w stronę wejścia (−u, czyli −X świata)",
        "arena": {"srodek": [1820 + D, 0], "r": 26, "opis": "okrągła kamienna posadzka r 27 (wierzch 0,3) na wyspie w "
                                                             "turkusowej sadzawce, krąg 8 omszałych filarów z lianami na r 26, "
                                                             "Świątynia Stu Lian w (2788; 27), z boku osi"},
        "odrodzenie_s": 120, "odrodzenie_stale": True,
        "tryb": "do decyzji: wspólny dla serwera (jak Strażnik Gaju) albo osobny dla gracza",
        "ryk": {"klip": "ryk", "dl_s": 2.0, "zrodlo": "swiat/postacie/waz_stu_lian.py — klip „ryk” (60 klatek = 2,0 s)"},
        "otwiera": "brama_pustyni (osobno dla gracza)"}

    # przelot: punkty Bagna przesunięte o +940 (ten sam wzór: 13,4 s, zatrzymanie od 10,5 s, ryk 2,0 s od 10,7 s)
    kam = [
        {"t": 0.0, "poz": [946 + D, 0, 26], "patrz": [1010 + D, 0, 4], "pokazuje": "start nad plecami gracza, przed bramą Bagna"},
        {"t": 1.2, "poz": [992 + D, 12, 28], "patrz": [1090 + D, 0, 2], "pokazuje": "Taras Przybycia: jajko, turkusowy strumyk"},
        {"t": 2.7, "poz": [1100 + D, -16, 25], "patrz": [1170 + D, 0, 2], "pokazuje": "Polana Zwijogonów i Chatka na Drzewie"},
        {"t": 4.3, "poz": [1240 + D, 10, 25], "patrz": [1320 + D, 0, 3], "pokazuje": "Mostek nad Kaskadą i Kwietnik Gębokwiatów"},
        {"t": 6.1, "poz": [1410 + D, -12, 23], "patrz": [1500 + D, 0, 3], "pokazuje": "bambusowa przesieka i Gaj Kokosów"},
        {"t": 8.1, "poz": [1600 + D, 10, 21], "patrz": [1694 + D, -6, 6], "pokazuje": "omszałe schody i Ruiny Pancernika"},
        {"t": 9.6, "poz": [1740 + D, 0, 14], "patrz": [1814 + D, 0, 11], "pokazuje": "Brama Posągów, kamera zniża się"},
        {"t": 10.5, "poz": [1786 + D, 0, 11], "patrz": [1814 + D, 0, 11.5], "pokazuje": "Wąż Stu Lian w kadrze — zatrzymanie"},
        {"t": 13.4, "poz": [1786 + D, 0, 11], "patrz": [1814 + D, 0, 11.5], "pokazuje": "ryk Węża, potem cięcie do gracza"},
    ]
    przelot = {"kiedy": "pierwsze wejście gracza do Dżungli (D-077); flaga na gracza; przy kolejnych wejściach brak",
               "czas_s": 13.4, "punkty": kam, "ryk_od_s": 10.7, "zatrzymanie_od_s": 10.5,
               "potem": "zaciemnienie 0,5 s i powrót kamery za plecy gracza w punkcie przybycia",
               "ruch": "krzywa Catmull-Rom jak w lesie (swiat/biom_las/pas/sprawdz_plan.krzywa_kamery)",
               "streaming": "przed startem serwer prosi o wczytanie okolic u = %d, %d, %d, %d" % (1110 + D, 1390 + D, 1640 + D,
                                                                                                 1814 + D)}
    pp_b = {p["id"]: p for p in B["punkty_przybycia"]}
    punkty_przybycia = [
        dict(pp_b["miasteczko"]),
        {"id": "dzungla", "nazwa": "Dżungla — Taras Przybycia", "u": przyb_b["u"], "v": przyb_b["v"], "y": 0,
         "patrz": list(przyb_b["patrz"]), "kamera_opada_z_wys": 60, "od_poczatku": False,
         "odblokowanie": "po pokonaniu Strażnika Topieli (jak w planie Bagna)"},
        {"id": "dzungla_arena", "nazwa": "Dżungla — przed Kręgiem Stu Lian (opcja)", "u": 1752 + D, "v": 0, "y": 0,
         "patrz": [1814 + D, 0], "kamera_opada_z_wys": 60, "od_poczatku": False,
         "odblokowanie": "po pierwszym dojściu do Kręgu — wybór do decyzji"},
        {"id": "pustynia", "nazwa": "Pustynia — przybycie", "u": pu_rez["przybycie_u"], "v": 0, "y": 0,
         "patrz": [pu_rez["przybycie_u"] + 46, 0], "kamera_opada_z_wys": 60, "od_poczatku": False,
         "odblokowanie": "po pokonaniu Węża Stu Lian"},
    ]
    zal_b = B["czas"]["zalozenia"]
    czas = {
        "cel_min": 60, "pasmo_min": [45, 80], "cel_rowny_min": 95,
        "status": "propozycja: rozkład rosnący z PLAN_BIOMOW (Dżungla 60 min) albo równy (ok. 95 min)",
        "zalozenia": {
            "walka_s": {"Zwijogon": 19, "Gębokwiat": 18, "Kokosowy Siłacz": 23, "Pancernik Ruin": 28, "Wąż Stu Lian": 34},
            "walka_s_zrodlo": "SZACUNEK: potwory Dżungli nie mają jeszcze danych walki w silniku; wzięte z Bagna (Rechotek 18, "
                              "Bulgotnik 17, Kłodokłap 21, Ropucha 26, Strażnik 32) z poprawką na uniki i większe życie",
            "narzut_walki_s": zal_b["narzut_walki_s"], "dojscie_s": zal_b["dojscie_s"],
            "pominieta_walka_s": zal_b["pominieta_walka_s"], "przelot_s": 13.4, "jajko_s": zal_b["jajko_s"],
            "trening_i_decyzje_s": 600, "trening_opis": "jak w Bagnie (450 s na 45 min), przeskalowane do 60 min"},
        "walki_plan": {"zwijogony": 33, "gebokwiaty": 34, "kokosy": 34, "ruiny": 4, "arena": 5},
        "walki_plan_rowny": {"zwijogony": 52, "gebokwiaty": 55, "kokosy": 55, "ruiny": 5, "arena": 6},
        "walki_zrodlo": "swiat/biomy/PLAN_BIOMOW.md (model tools/walka/tempo.py, krzywa 11,71 × L^1,6): Dżungla 60 min ≈ 110 "
                        "walk, 95 min ≈ 173 walki",
    }
    gat = {"zwijogony": "Zwijogon", "gebokwiaty": "Gębokwiat", "kokosy": "Kokosowy Siłacz", "ruiny": "Pancernik Ruin",
           "arena": "Wąż Stu Lian"}
    plan = {
        "opis": "Dżungla jako odcinek wąskiego pasa — PROPOZYCJA (18.11.2026), bez budowy w Studio. Wzór: Bagno-pas "
                "(swiat/bagno_pas/plan_bagna.json) przesunięty o +940 st wzdłuż pasa (D-075, D-076, D-077, D-096). Układ "
                "pasa jak w lesie: u wzdłuż (ciągnie się od początku lasu), v w poprzek (v > 0 po prawej ręce idącego do "
                "bramy), y w górę. Generuje swiat/dzungla_pas/plan.py.",
        "wersja": 1, "status": "propozycja", "nazwa_robocza": "Gąszcz Pod Parasolem",
        "bieg": dict(B["bieg"]),
        "pas": {"szerokosc": B["pas"]["szerokosc"], "szerokosc_s": B["pas"]["szerokosc_s"], "kulisy": B["pas"]["kulisy"],
                "kulisy_opis": "pas 24 st z każdej strony: drzewa dżungli z koronami-parasolami, palmy, figowce, paprocie "
                               "drzewiaste, kępy liści-parasoli, bambus, liany i wiszące mosty z lian; kolizja tylko na "
                               "pierwszym rzędzie; niewidzialna ściana na |v| = 38",
                "u_od": u0, "u_do": u1, "przesuniecie_wzgledem_bagna_u": D,
                "u_tyl_opis": "u 1874: palisada bramy do Dżungli Bagna za plecami przybywającego (część Bagna-pasa)",
                "y": 0, "teren": "płasko (y = 0); woda to tafla bez kolizji 0,2 nad gruntem (brodzi się), dróżka i mostki ≤ 0,45",
                "sciezka": {"szer": 8, "pts": [[960 + D, 0], [1900 + D, 0]],
                            "opis": "Dróżka: ubita ziemia (wierzch 0,36–0,4) po osi pasa, w ruinach i w Kręgu z kamiennych płyt; "
                                    "nad nią tu i ówdzie liście-parasole (wyżej niż 7)"}},
        "swiat": {"X0": sw["X0"], "Z0": sw["Z0"], "obrot_y": 0, "wzor": sw["wzor"], "kontener": "Workspace/DzunglaPas",
                  "slonce": sw["slonce"], "miasteczko": sw["miasteczko"], "zajete_inne": sw["zajete_inne"],
                  "polowa_szerokosci_z_tlem": sw["polowa_szerokosci_z_tlem"],
                  "sasiad_bagno": "Workspace/BagnoPas: części do u 1906 (kulisy, tło, płyta, Krzywa Kładka do u 1902, palisada "
                                  "bramy u 1872–1877); grupa ZapowiedzDzungli (u 1876–1906, niewidzialna ściana u 1905) do "
                                  "usunięcia przed budową Dżungli"},
        "przegrody": przegrody, "przejscia": przejscia, "miejsca": miejsca,
        "strefy_spokoju": [{"id": "wejscie", "u": [936 + D, 1004 + D], "v": [-36, 36], "opis": "cały Taras Przybycia"},
                           {"id": "przedbramie", "u": [1848 + D, 1880 + D], "v": [-36, 36],
                            "opis": "za Kręgiem Stu Lian, przed bramą do Pustyni"}],
        "punkty_orientacyjne": zn,
        "zasady": dict(B["zasady"], predkosc={k: v["predkosc"] for k, v in POTWORY.items() if v["predkosc"]}),
        "rozmiary": {k: {kk: v[kk] for kk in ("wys", "szer", "dl") if kk in v} for k, v in POTWORY.items()},
        "rozmiary_zrodlo": "swiat/test_walki2/dane/<model>.json → wymiary (wysokosc, glebokosc = dl, szerokosc = szer)",
        "potwory_opis": POTWORY,
        "nacisk": "zwinni przeciwnicy, którzy często unikają i ranią krwawieniem — opłaca się Szczęście (krytyk skraca walkę) "
                  "i Kondycja; Kokosowy Siłacz i Pancernik są twardzi fizycznie, Gębokwiat rani magią (D-069)",
        "strefy": strefy, "straznik": straznik, "przelot_kamery": przelot, "punkty_przybycia": punkty_przybycia,
        "czas": czas, "gatunek_przegrody": gat,
        "budzet_czesci": {"cel": 9000, "limit": 12000, "porownanie": "Bagno-pas 9017, las-pas 8601"},
        "kolejne_biomy": [b for b in B["kolejne_biomy"] if b["id"] != "dzungla"],
    }
    return plan


# =========================================================================== liczby (czasy biegu, budżet czasu)
def czasy_biegu(p):
    v = p["bieg"]["walkspeed"]
    m = {x["id"]: x for x in p["miejsca"]}
    u0, u1 = m["przybycie"]["u"], m["brama_pustyni"]["u"]
    wiersze = [(q["nazwa"], q["u_od"], q["u_do"], max(q["u_od"], u0) - u0, (q["u_do"] - q["u_od"]) / v)
               for q in sorted(p["przegrody"], key=lambda q: q["u_od"])]
    srodki = sorted([st["srodek"][0] for st in p["strefy"]] + [p["straznik"]["miejsce"][0]])
    return (u1 - u0) / v, [(n, a, b, d / v, t) for n, a, b, d, t in wiersze], [(b - a) / v for a, b in zip(srodki, srodki[1:])]


def budzet_czasu(p, rowny=False):
    c = p["czas"]
    z = c["zalozenia"]
    walki = c["walki_plan_rowny" if rowny else "walki_plan"]
    t_prosto = czasy_biegu(p)[0]
    narzut = z["narzut_walki_s"] + z["dojscie_s"]
    trening = z["trening_i_decyzje_s"] * (c["cel_rowny_min"] / c["cel_min"] if rowny else 1.0)
    staly = t_prosto + z["przelot_s"] + z["jajko_s"] + trening
    x1, pom, n = staly, staly, 0
    for prz, ile in walki.items():
        t_w = z["walka_s"][p["gatunek_przegrody"][prz]]
        n += ile
        x1 += ile * (t_w + narzut)
        pom += (t_w + narzut) + max(0, ile - 1) * (z["pominieta_walka_s"] + narzut)
    chodzenie = t_prosto + n * z["dojscie_s"]
    return {"walk": n, "x1_s": x1, "pom_s": pom, "chodzenie_s": chodzenie, "bieg_s": t_prosto}


def zapisz(p, plik=PLIK):
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
        f.write("\n")


def l1(x):
    return ("%.1f" % x).replace(".", ",")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = zbuduj()
    zapisz(p)
    t, wiersze, miedzy = czasy_biegu(p)
    m = {x["id"]: x for x in p["miejsca"]}
    print("DŻUNGLA — plan (propozycja) → swiat/dzungla_pas/plan_dzungli.json")
    print("bieg od przybycia (u %g) do bramy do Pustyni (u %g): %s s" % (m["przybycie"]["u"], m["brama_pustyni"]["u"], l1(t)))
    for n, a, b, od, przez in wiersze:
        print("  %-24s u %4d–%4d  od przybycia %5s s, przez %4s s" % (n, a, b, l1(od), l1(przez)))
    print("  między sąsiednimi miejscami walki: %s–%s s" % (l1(min(miedzy)), l1(max(miedzy))))
    for rowny in (False, True):
        b = budzet_czasu(p, rowny)
        print("budżet (%s): %d walk, ×1 %s min, z pomijaniem %s min, chodzenie %s s = %s%%" % (
            "równy" if rowny else "rosnący", b["walk"], l1(b["x1_s"] / 60), l1(b["pom_s"] / 60), l1(b["chodzenie_s"]),
            l1(100 * b["chodzenie_s"] / b["x1_s"])))
    for st in p["strefy"]:
        print("  %-3s %-16s %-9s poz. %s / równe %s · naraz %d, max %d · pętla %s st (pojemność %d)" % (
            st["id"], st["potwor"], st["klasa"], st["poziomy"], st["poziomy_rowny"], st["naraz"], st["max"], l1(st["obwod"]),
            st["pojemnosc"]))
    s_ = p["straznik"]
    print("  Strażnik: %s, poziom %d / %d, w (%g; %g)" % (s_["potwor"], s_["poziom"], s_["poziom_rowny"], *s_["miejsce"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
