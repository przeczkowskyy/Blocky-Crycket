#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plan Bagna jako odcinka wąskiego pasa — PROPOZYCJA, nic tu nie jest kanonem.

    python -B swiat/bagno_pas/plan.py          # → swiat/bagno_pas/plan_bagna.json + tabela czasów i potworów

Format jak swiat/biom_las/pas/plan_pasa.json (pas, swiat, przegrody, przejscia, miejsca, strefy, straznik, przelot_kamery,
punkty_przybycia, czas), żeby skrypty gry z swiat/las_pas_gra mogły czytać plan Bagna tak jak plan lasu. Różnice:
brama na końcu to `brama_dzungli` (w lesie `brama_bagna`), strefy mają też `klasa` i `poziomy_rowny`.

Położenie: ta sama oś i szerokość co las-pas (świat = (1100 + u; y; −700 + v), bez obrotu). Bagno zaczyna się za bramą do
Bagna z planu lasu (u 934) i kończy na u 1880 (rezerwacja „kolejne_biomy” w planie lasu); punkt przybycia u 954 — też z
planu lasu. Pętle potworów i domy: te same kształty co w lesie (pętla 8 węzłów 36 × 44 st, obwód 138; leże — 6 węzłów).
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biom_las.pas.sprawdz_plan import obwod  # noqa: E402

PLAN_LASU = os.path.join(REPO, "swiat", "biom_las", "pas", "plan_pasa.json")
PLIK = os.path.join(TU, "plan_bagna.json")
STATUS_POZIOMOW = ("propozycja: `poziomy` = tempo rosnące (Bagno 45 min, poziomy 11–19), `poziomy_rowny` = tempo równe po "
                   "lesie (Bagno ok. 95 min, poziomy 11–25); model tools/walka/tempo.py, do uzgodnienia z krzywą")


def wczytaj_las(plik=PLAN_LASU):
    with open(plik, encoding="utf-8") as f:
        return json.load(f)


def petla_kojca(cu):
    """Pętla 8 węzłów jak w lesie: zaokrąglony prostokąt 36 × 44 wokół (cu; 0)."""
    return [[cu + 18.0, 0.0], [round(cu + 16.3, 1), 17.5], [cu, 22.0], [round(cu - 16.3, 1), 17.5], [cu - 18.0, 0.0],
            [round(cu - 16.3, 1), -17.5], [cu, -22.0], [round(cu + 16.3, 1), -17.5]]


def petla_leza(cu):
    return [[cu + 24.0, 0.0], [round(cu + 11.9, 1), 16.0], [round(cu - 11.9, 1), 16.0], [cu - 24.0, 0.0],
            [round(cu - 11.9, 1), -16.0], [round(cu + 11.9, 1), -16.0]]


# --------------------------------------------------------------------------- potwory Bagna (opis — modeli jeszcze nie ma)
POTWORY = {
    "Rechotek": {
        "klasa": "Zwiadowca", "ranga": "zwykły", "przegroda": "oczka", "wys": 3.0, "dl": 3.6,
        "ksztalt": "przysadzista ropucha z klocków: szeroki płaski łeb jak skrzynka, oczy-kulki na czubku, krótkie tylne "
                   "łapy w kolanach (skacze susami), gruby język z rozdwojonym końcem chowany w pysku",
        "kolor": "oliwkowa zieleń 7E8C3E z ciemnymi plamami 4F5A2A, żółty brzuch E8C85A, pomarańczowe oczy F08A24",
        "walka": "szybki i zwinny: często unika; „lepki język” spowalnia gracza (efekt Spowolnienie z silnika)",
        "dom": "oczko wodne z liściem grzybienia i kępą pałek pod ścianą",
        "predkosc": 8, "odrodzenie_s": 12,
    },
    "Bulgotnik": {
        "klasa": "Mag", "ranga": "zwykły", "przegroda": "trzesawisko", "wys": 4.2, "szer": 3.0,
        "ksztalt": "mały błotny szaman: korpus-kopczyk z błota na dwóch krótkich nóżkach, głowa to bańka gazu (kula) z dwojgiem "
                   "oczu, w ręce kij z latarenką-ognikiem; z pleców uchodzą bąble",
        "kolor": "błoto 5B4A34, bańka mlecznozielona B9D49A, ognik żółtozielony C8E05A (Neon), kij ciemne drewno",
        "walka": "bije kijem słabo, ale „bańka gazu” rani magią i spowalnia; mało życia",
        "dom": "bąblujący kopiec błota z dziurą",
        "predkosc": 5, "odrodzenie_s": 15,
    },
    "Kłodokłap": {
        "klasa": "Wojownik", "ranga": "zwykły", "przegroda": "kepy", "wys": 3.2, "dl": 8.6,
        "ksztalt": "żywa kłoda z paszczą: omszały pień leżący poziomo na czterech krótkich łapach-korzeniach, przód rozcięty w "
                   "paszczę z kołkami-zębami, na grzbiecie kępa mchu i grzybek, ogon z korzeni",
        "kolor": "kora 6B5A44, mech 6F7A3A, wnętrze paszczy E5392B, zęby kość F3E6C8",
        "walka": "ciężki i twardy: gruba kora (dużo Pancerza), mocne ugryzienie, czasem ogłusza; nie unika",
        "dom": "na wpół zatopiona kłoda z korzeniami",
        "predkosc": 6, "odrodzenie_s": 18,
    },
    "Ropucha z Chatką": {
        "klasa": "Mag", "ranga": "rzadki", "przegroda": "chatka", "wys": 11.0, "szer": 12.0,
        "ksztalt": "ogromna stara ropucha, która nosi na grzbiecie krzywą chatkę na palach z kominem; sapie, a z komina idzie dym",
        "kolor": "ciało szarozielone 6F7A5A, brzuch B5A46A, chatka z desek 8B5A2E i strzechy B59A52, dym biały",
        "walka": "rzadka i ciężka: dym z komina truje i spowalnia (magia), skok całym ciałem rani fizycznie",
        "dom": "Ropusza Chata pod lewą ścianą (stoi pusta, gdy ropucha chodzi po leżu)",
        "predkosc": 4, "odrodzenie_s": 150,
    },
    "Strażnik Topieli": {
        "klasa": "strażnik (obrażenia pół na pół: fizyczne i magiczne)", "ranga": "strażnik", "przegroda": "topiel",
        "wys": 16.0, "szer": 10.0,
        "ksztalt": "olbrzym z błota i korzeni cypryśnika, wynurzony do pasa z kręgu wody; na głowie przewrócona łódka jak kapelusz, "
                   "w piersi latarnia z zielonym światłem (jak kryształ Strażnika Gaju), z ramion zwisa mech",
        "kolor": "błoto 4A3F2A, korzenie 6B5A44, mech 6F7A3A, światło C8E05A (Neon), łódka 8B5A2E",
        "walka": "dużo życia i Pancerza; „wciągnięcie w topiel” unieruchamia (jak Uścisk korzeni), uderzenie błotem rani magią",
        "dom": "krąg wody za pomostem areny",
        "predkosc": 0, "odrodzenie_s": 120,
    },
}


def zbuduj(plan_lasu=None):
    L = plan_lasu or wczytaj_las()
    rez = {b["id"]: b for b in L["kolejne_biomy"]}
    bagno_rez, dzungla_rez = rez["bagno"], rez["dzungla"]
    przyb_las = {p["id"]: p for p in L["punkty_przybycia"]}["bagno"]
    brama_lasu = {m["id"]: m for m in L["miejsca"]}["brama_bagna"]
    u0 = float(brama_lasu["u"])                        # 934 — brama lasu = początek Bagna
    u1 = float(bagno_rez["u_do"])                      # 1880 — koniec rezerwacji Bagna
    sw = L["swiat"]

    przegrody = [
        {"id": "wejscie", "nazwa": "Pomost Przybycia", "u_od": 940, "u_do": 1004, "kolor": "C9C08A",
         "opis": "przybycie teleportem i z lasu przez bramę; stanowisko jajka, Kamień Powrotu; strefa spokoju; tu startuje przelot",
         "pod": [], "strefy": []},
        {"id": "oczka", "nazwa": "Rechotne Oczka", "u_od": 1016, "u_do": 1208, "kolor": "A9C47A",
         "opis": "trzy trawiaste kępy na płytkiej wodzie, między nimi rowy z kładkami; Rechotki poziomów rosnących",
         "pod": [{"id": "oczko_1", "nazwa": "Oczko Liści", "u_od": 1016, "u_do": 1080},
                 {"id": "oczko_2", "nazwa": "Oczko Pałek", "u_od": 1080, "u_do": 1144},
                 {"id": "oczko_3", "nazwa": "Oczko Rzęsy", "u_od": 1144, "u_do": 1208}],
         "strefy": ["r1", "r2", "r3"]},
        {"id": "trzesawisko", "nazwa": "Bulgotne Trzęsawisko", "u_od": 1228, "u_do": 1420, "kolor": "B7A27E",
         "opis": "ciemne błoto z bąblującymi kałużami, niska trzcina dzieli trzy kojce (przerwa 24 na środku); Bulgotniki",
         "pod": [{"id": "bablowisko", "nazwa": "Bąblowisko", "u_od": 1228, "u_do": 1292},
                 {"id": "kopce_gazu", "nazwa": "Kopce Gazu", "u_od": 1292, "u_do": 1356},
                 {"id": "mglista_lacha", "nazwa": "Mglista Łacha", "u_od": 1356, "u_do": 1420}],
         "strefy": ["b1", "b2", "b3"]},
        {"id": "kepy", "nazwa": "Kłapiące Kępy", "u_od": 1436, "u_do": 1628, "kolor": "8FA88E",
         "opis": "kępy z korzeniami na ciemnej toni, między nimi kładki; Kłodokłapy (ciężkie, mniej naraz)",
         "pod": [{"id": "zatoka_klod", "nazwa": "Zatoka Kłód", "u_od": 1436, "u_do": 1500},
                 {"id": "kepy_korzeni", "nazwa": "Kępy Korzeni", "u_od": 1500, "u_do": 1564},
                 {"id": "czarna_ton", "nazwa": "Czarna Toń", "u_od": 1564, "u_do": 1628}],
         "strefy": ["k1", "k2", "k3"]},
        {"id": "chatka", "nazwa": "Leże Ropuchy", "u_od": 1644, "u_do": 1744, "kolor": "C4AE82",
         "opis": "błotna łacha z Ropuszą Chatą pod lewą ścianą; jedna Ropucha z Chatką (rzadka, ciężka)",
         "pod": [], "strefy": ["t1"]},
        {"id": "topiel", "nazwa": "Topiel Strażnika", "u_od": 1760, "u_do": 1880, "kolor": "9FB4B0",
         "opis": "okrągły pomost na ciemnej wodzie, krąg pni z latarniami, Latarnia Topieli; Strażnik Topieli; za nim brama do "
                 "Dżungli",
         "pod": [], "strefy": ["straznik"]},
    ]
    przejscia = [
        {"id": "row_z_kladka", "nazwa": "Rów z kładką", "miedzy": ["wejscie", "oczka"], "u_od": 1004, "u_do": 1016,
         "otwarcie": [-36, 36], "wys_w_otwarciu": 1.6, "wys_reszty": 0, "blokuje": False, "woda": [1006, 1014], "kladka": [-6, 6],
         "opis": "płytki rów w poprzek pasa (woda bez kolizji, przejdzie się wszędzie), szeroka kładka 12 na osi"},
        {"id": "kladka_nad_topiela", "nazwa": "Kładka nad Topielą", "miedzy": ["oczka", "trzesawisko"], "u_od": 1208, "u_do": 1228,
         "otwarcie": [-36, 36], "wys_w_otwarciu": 1.6, "wys_reszty": 0, "blokuje": False, "woda": [1211, 1225], "kladka": [-6, 6],
         "opis": "ciemna, szersza woda (bez kolizji) i kładka 12 z poręczami do 1,4; przez nią widać brązowe trzęsawisko"},
        {"id": "trzcinowa_przesieka", "nazwa": "Trzcinowa przesieka", "miedzy": ["trzesawisko", "kepy"], "u_od": 1420,
         "u_do": 1436, "otwarcie": [-16, 16], "wys_w_otwarciu": 0, "wys_reszty": 6, "blokuje": False,
         "opis": "ściany wysokiej trzciny i pałek 6 wys. od obu ścian zwężają przejście do 32"},
        {"id": "zatopione_pnie", "nazwa": "Zatopione pnie", "miedzy": ["kepy", "chatka"], "u_od": 1628, "u_do": 1644,
         "otwarcie": [-14, 14], "wys_w_otwarciu": 0.4, "wys_reszty": 9, "blokuje": False,
         "opis": "zwalone, omszałe pnie i karpy 6–9 wys. od ścian, przejście 28; wbite pale z czaszką ropuchy (ostrzeżenie)"},
        {"id": "latarnie_topieli", "nazwa": "Latarnie Topieli", "miedzy": ["chatka", "topiel"], "u_od": 1744, "u_do": 1760,
         "otwarcie": [-14, 14], "wys_w_otwarciu": 0, "wys_reszty": 1.2, "blokuje": False, "latarnie": [[1752, -16], [1752, 16]],
         "opis": "dwa wysokie słupy z zielonymi latarniami (14) po bokach osi, reszta to niskie korzenie ≤ 1,2; widać arenę"},
    ]
    miejsca = [
        {"id": "przybycie", "nazwa": "Przybycie (teleport i wejście z lasu)", "u": przyb_las["u"], "v": przyb_las["v"], "y": 0,
         "patrz": list(przyb_las["patrz"]), "opis": "punkt przybycia „bagno” z planu lasu; twarzą wzdłuż pasa"},
        {"id": "jajko", "nazwa": "Stanowisko jajka (inkubator Bagna)", "u": 972, "v": 22, "y": 0, "r": 6, "e": True,
         "opis": "to samo stanowisko co w lesie (podest 12 × 12 z punktem E), na drewnianym pomoście — jajka Bagna (D-059, D-060)"},
        {"id": "kamien_powrotu", "nazwa": "Kamień Powrotu", "u": 948, "v": -24, "y": 0, "r": 3, "e": True,
         "opis": "E → miasteczko (jak w lesie)"},
        {"id": "brama_lasu", "nazwa": "Brama do Bagna (las-pas)", "u": u0, "v": 0, "y": 0, "otwarcie": list(brama_lasu["otwarcie"]),
         "e": False, "opis": "palisada lasu-pasa za plecami przybywającego (Workspace/LasPas/BramaBagna) — Bagno jej nie buduje"},
        {"id": "brama_dzungli", "nazwa": "Brama do Dżungli", "u": u1 - 6, "v": 0, "y": 0, "otwarcie": [-8, 8], "e": False,
         "opis": "palisada z pni cypryśnika przez cały pas, wrota 16 szer.; zamknięte dla gracza, póki nie pokona Strażnika Topieli"},
        {"id": "odrodzenie", "nazwa": "Odrodzenie po przegranej", "u": przyb_las["u"], "v": 0, "y": 0,
         "opis": "jak w lesie: na razie walka wraca gracza w miejsce startu walki"},
    ]
    zn = [
        {"id": "chata_na_palach", "nazwa": "Chata na Palach", "u": 1144, "v": 30, "r": 6, "wys": 17,
         "opis": "krzywa chatka rybaka na wysokich palach z kładką i świecącym oknem — widać ją z wejścia"},
        {"id": "stary_cyprys", "nazwa": "Stary Cypryś", "u": 1356, "v": 32, "r": 5, "wys": 31, "korona": {"r": 11, "od": 19},
         "opis": "olbrzymi cypryśnik z „kolanami” i brodą mchu; płaska korona r 11 na wys. 19–31"},
        {"id": "wrak_lodzi", "nazwa": "Wrak Łodzi", "u": 1564, "v": 30, "r": 7, "wys": 19,
         "opis": "rufa zatopionej łodzi sterczy ukosem z wody, złamany maszt z podartym żaglem"},
        {"id": "ropusza_chata", "nazwa": "Ropusza Chata", "u": 1724, "v": -30, "r": 7, "wys": 18,
         "opis": "chata na palach z kominem i kotłem — dom Ropuchy z Chatką"},
        {"id": "latarnia_lewa", "nazwa": "Latarnia Topieli (lewa)", "u": 1752, "v": -16, "r": 2, "wys": 14},
        {"id": "latarnia_prawa", "nazwa": "Latarnia Topieli (prawa)", "u": 1752, "v": 16, "r": 2, "wys": 14},
        {"id": "wieza_topieli", "nazwa": "Wieża Topieli", "u": 1848, "v": 27, "r": 5, "wys": 40,
         "opis": "krzywa wieża z pali z zielonym światłem na szczycie (ok. 40) — cel widoczny wzdłuż całego Bagna; stoi z boku osi"},
    ]
    # --- strefy: (id, przegroda, pod, potwór, środek u, poziomy rosnące, poziomy równe, naraz, max, dom opis)
    S = [
        ("r1", "oczka", "oczko_1", "Rechotek", 1048, [11, 11], [11, 12], 4, 5),
        ("r2", "oczka", "oczko_2", "Rechotek", 1112, [11, 12], [12, 13], 4, 5),
        ("r3", "oczka", "oczko_3", "Rechotek", 1176, [12, 13], [13, 14], 4, 5),
        ("b1", "trzesawisko", "bablowisko", "Bulgotnik", 1260, [13, 14], [15, 16], 4, 5),
        ("b2", "trzesawisko", "kopce_gazu", "Bulgotnik", 1324, [14, 14], [16, 17], 4, 5),
        ("b3", "trzesawisko", "mglista_lacha", "Bulgotnik", 1388, [14, 15], [17, 18], 4, 5),
        ("k1", "kepy", "zatoka_klod", "Kłodokłap", 1468, [15, 16], [19, 20], 3, 4),
        ("k2", "kepy", "kepy_korzeni", "Kłodokłap", 1532, [16, 17], [20, 21], 3, 4),
        ("k3", "kepy", "czarna_ton", "Kłodokłap", 1596, [17, 17], [21, 22], 3, 4),
    ]
    zach = {"Rechotek": "skacze susami po kępie, przystaje przy oczkach; odwraca się do gracza w promieniu 18",
            "Bulgotnik": "drepcze po trzęsawisku, przystaje przy kałużach i puszcza bańki",
            "Kłodokłap": "pełznie powoli po kępie, czasem zamiera jak zwykła kłoda"}
    strefy = []
    for sid, pb, pod, pot, cu, poz, poz_r, naraz, mx in S:
        tr = petla_kojca(float(cu))
        strefy.append({
            "id": sid, "podbiom": pb, "pod": pod, "potwor": pot, "klasa": POTWORY[pot]["klasa"], "wariant": None,
            "poziomy": poz, "poziomy_rowny": poz_r, "poziomy_status": STATUS_POZIOMOW, "naraz": naraz, "max": mx,
            "srodek": [float(cu), 0.0], "r": 28, "y": 0, "pole": [cu - 28, cu + 28, -34, 34],
            "dom": {"opis": POTWORY[pot]["dom"], "pts": [[cu - 6.0, -34.0], [cu + 6.0, 34.0]]},
            "trasa": tr, "liczba_wezlow": len(tr), "odrodzenie_s": POTWORY[pot]["odrodzenie_s"],
            "zachowanie": zach[pot], "grupa": None, "obwod": round(obwod(tr + [tr[0]]), 1),
            "pojemnosc": int(obwod(tr + [tr[0]]) // 25)})
    tr = petla_leza(1694.0)
    strefy.append({
        "id": "t1", "podbiom": "chatka", "pod": None, "potwor": "Ropucha z Chatką", "klasa": POTWORY["Ropucha z Chatką"]["klasa"],
        "wariant": None, "poziomy": [18, 18], "poziomy_rowny": [23, 24], "poziomy_status": STATUS_POZIOMOW, "naraz": 1, "max": 1,
        "srodek": [1694.0, 0.0], "r": 29, "y": 0, "pole": [1648, 1740, -34, 34],
        "dom": {"opis": POTWORY["Ropucha z Chatką"]["dom"], "pts": [[1700.0, -34.0]]}, "trasa": tr, "liczba_wezlow": len(tr),
        "odrodzenie_s": 150, "zachowanie": "człapie po łasze, przysiada i sapie dymem; przy graczu w promieniu 25 rechocze",
        "grupa": None, "obwod": round(obwod(tr + [tr[0]]), 1), "pojemnosc": int(obwod(tr + [tr[0]]) // 25),
        "odrodzenie_stale": True, "uwaga": "rzadka: jedna naraz, stałe odrodzenie (jak Leśny Troll); wspólna czy osobna — wybór"})

    straznik = {
        "potwor": "Strażnik Topieli", "klasa": POTWORY["Strażnik Topieli"]["klasa"], "poziom": 19, "poziom_rowny": 25,
        "poziomy_status": STATUS_POZIOMOW, "miejsce": [1814, 0], "y": 0.3, "yaw_swiat": 1.5708,
        "patrzy": "w stronę wejścia (−u, czyli −X świata)",
        "arena": {"srodek": [1820, 0], "r": 26, "opis": "okrągły pomost z desek r 27 (wierzch 0,3), krąg pni z latarniami r 26, "
                                                          "Wieża Topieli w (1848; 27), z boku osi"},
        "odrodzenie_s": 120, "odrodzenie_stale": True,
        "tryb": "do decyzji: wspólny dla serwera (jak Strażnik Gaju) albo osobny dla gracza",
        "ryk": {"klip": "ryk", "dl_s": 2.0, "zrodlo": "do zrobienia z modelem Strażnika Topieli (po akceptacji planu)"},
        "otwiera": "brama_dzungli (osobno dla gracza)"}

    kam = [
        {"t": 0.0, "poz": [946, 0, 26], "patrz": [1010, 0, 4], "pokazuje": "start nad plecami gracza, przed palisadą lasu"},
        {"t": 1.2, "poz": [992, 12, 28], "patrz": [1090, 0, 2], "pokazuje": "Pomost Przybycia: jajko, rów z kładką"},
        {"t": 2.7, "poz": [1100, -16, 25], "patrz": [1170, 0, 2], "pokazuje": "Rechotne Oczka i Chata na Palach"},
        {"t": 4.3, "poz": [1240, 10, 25], "patrz": [1320, 0, 3], "pokazuje": "Kładka nad Topielą i Bulgotne Trzęsawisko"},
        {"t": 6.1, "poz": [1410, -12, 23], "patrz": [1500, 0, 3], "pokazuje": "trzcinowa przesieka i Kłapiące Kępy"},
        {"t": 8.1, "poz": [1600, 10, 21], "patrz": [1694, -6, 6], "pokazuje": "zatopione pnie i Leże Ropuchy"},
        {"t": 9.6, "poz": [1740, 0, 14], "patrz": [1814, 0, 11], "pokazuje": "Latarnie Topieli, kamera zniża się"},
        {"t": 10.5, "poz": [1786, 0, 11], "patrz": [1814, 0, 11.5], "pokazuje": "Strażnik Topieli w kadrze — zatrzymanie"},
        {"t": 13.4, "poz": [1786, 0, 11], "patrz": [1814, 0, 11.5], "pokazuje": "ryk Strażnika, potem cięcie do gracza"},
    ]
    przelot = {"kiedy": "pierwsze wejście gracza do Bagna (D-077); flaga na gracza; przy kolejnych wejściach brak",
               "czas_s": 13.4, "punkty": kam, "ryk_od_s": 10.7, "zatrzymanie_od_s": 10.5,
               "potem": "zaciemnienie 0,5 s i powrót kamery za plecy gracza w punkcie przybycia",
               "ruch": "krzywa Catmull-Rom jak w lesie (swiat/biom_las/pas/sprawdz_plan.krzywa_kamery)",
               "streaming": "przed startem serwer prosi o wczytanie okolic u = 1110, 1390, 1640, 1814"}
    pp_las = {p["id"]: p for p in L["punkty_przybycia"]}
    punkty_przybycia = [
        dict(pp_las["miasteczko"]),
        {"id": "bagno", "nazwa": "Bagno — Pomost Przybycia", "u": przyb_las["u"], "v": przyb_las["v"], "y": 0,
         "patrz": list(przyb_las["patrz"]), "kamera_opada_z_wys": 60, "od_poczatku": False,
         "odblokowanie": "po pokonaniu Strażnika Gaju (jak w planie lasu)"},
        {"id": "bagno_arena", "nazwa": "Bagno — przed Topielą (opcja)", "u": 1752, "v": 0, "y": 0, "patrz": [1814, 0],
         "kamera_opada_z_wys": 60, "od_poczatku": False, "odblokowanie": "po pierwszym dojściu do Topieli — wybór do decyzji"},
        {"id": "dzungla", "nazwa": "Dżungla — przybycie", "u": dzungla_rez["przybycie_u"], "v": 0, "y": 0,
         "patrz": [dzungla_rez["przybycie_u"] + 46, 0], "kamera_opada_z_wys": 60, "od_poczatku": False,
         "odblokowanie": "po pokonaniu Strażnika Topieli"},
    ]
    zal_las = L["czas"]["zalozenia"]
    czas = {
        "cel_min": 45, "pasmo_min": [35, 60], "cel_rowny_min": 95,
        "status": "propozycja: rozkład rosnący 30/45/60/75/95/125/170 albo równy (ok. 85, a przy lesie 30 — ok. 95 na resztę)",
        "zalozenia": {
            "walka_s": {"Rechotek": 18, "Bulgotnik": 17, "Kłodokłap": 21, "Ropucha z Chatką": 26, "Strażnik Topieli": 32},
            "walka_s_zrodlo": "SZACUNEK: potwory Bagna nie mają jeszcze danych walki; wzięte z lasu (slime 20, muchomornik 15, "
                              "wilk 16, troll 23, Strażnik 29) z poprawką na klasę",
            "narzut_walki_s": zal_las["narzut_walki_s"], "dojscie_s": zal_las["dojscie_s"],
            "pominieta_walka_s": zal_las["pominieta_walka_s"], "przelot_s": 13.4, "jajko_s": zal_las["jajko_s"],
            "trening_i_decyzje_s": 450, "trening_opis": "jak w lesie, przeskalowane do 45 min"},
        "walki_plan": {"oczka": 25, "trzesawisko": 26, "kepy": 25, "chatka": 3, "arena": 4},
        "walki_plan_rowny": {"oczka": 52, "trzesawisko": 55, "kepy": 55, "chatka": 6, "arena": 6},
        "walki_zrodlo": "tools/walka/tempo.py (krzywa 11,71 × L^1,6): Bagno 45 min ≈ 83 walki (poziomy 11–19), "
                        "95 min ≈ 174 walki (poziomy 11–25)",
    }
    gat = {"oczka": "Rechotek", "trzesawisko": "Bulgotnik", "kepy": "Kłodokłap", "chatka": "Ropucha z Chatką",
           "arena": "Strażnik Topieli"}
    plan = {
        "opis": "Bagno jako odcinek wąskiego pasa — PROPOZYCJA (17.11.2026), bez budowy w Studio. Wzór: las-pas "
                "(swiat/biom_las/pas/plan_pasa.json, D-075, D-076, D-077). Układ pasa jak w lesie: u wzdłuż (ciągnie się od "
                "początku lasu), v w poprzek (v > 0 po prawej ręce idącego do bramy), y w górę. Generuje swiat/bagno_pas/plan.py.",
        "wersja": 1, "status": "propozycja",
        "bieg": dict(L["bieg"]),
        "pas": {"szerokosc": L["pas"]["szerokosc"], "szerokosc_s": L["pas"]["szerokosc_s"], "kulisy": L["pas"]["kulisy"],
                "kulisy_opis": "pas 24 st z każdej strony: cypryśniki, wierzby, suche drzewa, trzcina; kolizja tylko na "
                               "pierwszym rzędzie; niewidzialna ściana na |v| = 38",
                "u_od": u0, "u_do": u1, "u_tyl_opis": "u 934: palisada bramy lasu za plecami przybywającego (część lasu-pasa)",
                "y": 0, "teren": "płasko (y = 0); woda to tafla bez kolizji 0,2 nad gruntem (brodzi się), kępy i kładki ≤ 0,45",
                "sciezka": {"szer": 8, "pts": [[960, 0], [1900, 0]],
                            "opis": "Krzywa Kładka: pomost z desek (wierzch 0,45) po osi pasa, mocniej falujący niż ścieżka lasu"}},
        "swiat": {"X0": sw["X0"], "Z0": sw["Z0"], "obrot_y": 0, "wzor": sw["wzor"], "kontener": "Workspace/BagnoPas",
                  "slonce": sw["slonce"], "miasteczko": sw["miasteczko"], "zajete_inne": sw["zajete_inne"],
                  "polowa_szerokosci_z_tlem": sw["polowa_szerokosci_z_tlem"],
                  "sasiad_las": "Workspace/LasPas: części do u 966 (kulisy, tło, płyta, ścieżka, palisada u 932–936); grupa "
                                "ZapowiedzBagna (u 934–966, niewidzialna ściana u 965) do usunięcia przed budową Bagna"},
        "przegrody": przegrody, "przejscia": przejscia, "miejsca": miejsca,
        "strefy_spokoju": [{"id": "wejscie", "u": [936, 1004], "v": [-36, 36], "opis": "cały Pomost Przybycia"},
                           {"id": "przedbramie", "u": [1848, 1880], "v": [-36, 36], "opis": "za Topielą, przed bramą do Dżungli"}],
        "punkty_orientacyjne": zn,
        "zasady": dict(L["zasady"], predkosc={k: v["predkosc"] for k, v in POTWORY.items() if v["predkosc"]}),
        "rozmiary": {k: {kk: v[kk] for kk in ("wys", "szer", "dl") if kk in v} for k, v in POTWORY.items()},
        "potwory_opis": POTWORY,
        "strefy": strefy, "straznik": straznik, "przelot_kamery": przelot, "punkty_przybycia": punkty_przybycia,
        "czas": czas, "gatunek_przegrody": gat,
        "budzet_czesci": {"cel": 9000, "limit": 12000, "porownanie": "las-pas 8601"},
        "kolejne_biomy": [b for b in L["kolejne_biomy"] if b["id"] != "bagno"],
    }
    return plan


# =========================================================================== liczby (czasy biegu, budżet czasu)
def czasy_biegu(p):
    v = p["bieg"]["walkspeed"]
    m = {x["id"]: x for x in p["miejsca"]}
    u0, u1 = m["przybycie"]["u"], m["brama_dzungli"]["u"]
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
    print("BAGNO — plan (propozycja) → swiat/bagno_pas/plan_bagna.json")
    print("bieg od przybycia (u %g) do bramy do Dżungli (u %g): %s s" % (p["miejsca"][0]["u"], p["miejsca"][4]["u"], l1(t)))
    for n, a, b, od, przez in wiersze:
        print("  %-24s u %4d–%4d  od przybycia %5s s, przez %4s s" % (n, a, b, l1(od), l1(przez)))
    print("  między sąsiednimi miejscami walki: %s–%s s" % (l1(min(miedzy)), l1(max(miedzy))))
    for rowny in (False, True):
        b = budzet_czasu(p, rowny)
        print("budżet (%s): %d walk, ×1 %s min, z pomijaniem %s min, chodzenie %s s = %s%%" % (
            "równy" if rowny else "rosnący", b["walk"], l1(b["x1_s"] / 60), l1(b["pom_s"] / 60), l1(b["chodzenie_s"]),
            l1(100 * b["chodzenie_s"] / b["x1_s"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
