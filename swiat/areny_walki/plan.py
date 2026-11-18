# -*- coding: utf-8 -*-
"""Plan aren walki zależnych od biomu (D-095) — SAME DANE. Generator (generuj.py) zamienia je na części.

Układ SCENY walki (jak odtwarzacz): X w prawo na ekranie, Y w górę od płyty placu, Z ku kamerze planu ogólnego.
Kąty `kat` / `luki` w stopniach od osi +X ku +Z:  90° = strona widowni (za kamerą planu ogólnego), 270° = tło za
plecami walczących (najczęściej w kadrze), 0° = za przeciwnikiem, 180° = za graczem.

Warstwy (od placu na zewnątrz): plac (r 22, jak dzisiejszy podest) → obręcz (≤ 1 wys.) → bliskie rekwizyty (niskie,
poza torami kamer) → kulisy boczne (wyższe rzeczy tylko w klinach ±X, gdzie kamery nie latają) → ściana biomu → korony /
dachy → dalekie sylwety zamykające horyzont. Wysokie rzeczy generator sam odsuwa poza wolną przestrzeń kamer
(profil_kamer.json z kamery.py), a kontrola (sprawdz.py) sprawdza to na punktach każdej części.

Nowa arena (Dżungla i dalej, swiat/biomy/PLAN_BIOMOW.md): nowy wpis w ARENY — nazwa, model, biom, źródła walk (nazwy
kontenerów albo atrybut BiomAreny kontenera), położenie w świecie, ziarno, grunt, plac, obręcz, warstwy z rodzinami
z rekwizyty.RODZINY, sylwety, nastrój i detale. Nowa rodzina = funkcja w rekwizyty.py + wpis w generuj.RODZINY.
Status: propozycja (D-095 zapisuje decyzję „arena zmienia się z biomem”; wygląd do akceptacji Karola).
"""

R_PLAC = 22.0              # = Ustawienia.PROMIEN_PODESTU (plac walki i wolna przestrzeń aktorów jak dziś)
R_GRUNT = 240.0
BUDZET = 1200              # części na arenę (uzasadnienie: PROJEKT.md, rozdz. „Budżet”)
BUDZET_TWARDY = 1500
# przeciwnicy, z którymi liczono wolną przestrzeń kamer trzech aren z 17.11 (las, Bagno, plac) — zestaw zamrożony,
# żeby nowi potwory innych biomów (Dżungla: Wąż Stu Lian 18 wys.) nie zmieniali tych aren; arena z wpisem
# „przeciwnicy” ma własny profil (<arena>/profil_kamer.json)
PRZECIWNICY_17_11 = ["lesny_slime", "cierniowy_wilk", "muchomornik", "lesny_troll", "straznik_lasu",
                     "rechotek", "bulgotnik", "klodoklap", "ropucha_z_chatka", "straznik_topieli"]

ARENY = {
    # ------------------------------------------------------------------------------------------------ LAS
    # Słoneczna polana w starym lesie: jasny, ubity plac i nasłoneczniona trawa wokół, za nimi ciemniejsze wnętrze lasu
    # (postacie czytają się na ciemniejszym tle), olbrzymie pnie z koronami wysoko nad polaną (dziura nieba nad placem),
    # smugi światła między pniami, wielkie muchomory jako kulisy po bokach walczących.
    "las": {
        "nazwa": "Polana Pod Koronami",
        "model": "Las",
        "biom": "las",
        "zrodla": ["LasPotwory", "LasPasGra"],
        "O": (-3000.0, 0.0, 1000.0),
        "ziarno": 1711,
        "grunt": {"y": -0.6, "kolor": "runo_ciemne", "mat": "Grass",
                  "laty": [{"r": 54.0, "kolor": "runo", "mat": "Grass"}, {"r": 34.0, "kolor": "arena_slonce", "mat": "Grass"}],
                  "plamy": {"n": 10, "r": (62, 190), "rozmiar": (10, 24), "kolory": ["runo_boru", "lisc_ciemny"]}},
        "plac": {"styl": "ziemia", "kolory": ["arena_ziemia", "arena_ziemia_jasna", "tusz"], "material": "Sand"},
        "obrecz": {"rodzina": "kamien_obreczy", "r": 23.6, "n": 24, "k": (0.75, 1.1)},
        "warstwy": [
            {"grupa": "Bliskie", "rodzina": "wysepka_lasu", "luki": [(205, 335)], "r": (31, 50), "n": 6, "k": (0.9, 1.15),
             "min_odstep": 12.0, "dosun": True},
            {"grupa": "Bliskie", "rodzina": "wysepka_lasu", "luki": [(35, 145)], "r": (36, 78), "n": 4, "k": (0.9, 1.1),
             "min_odstep": 16.0},
            {"grupa": "Bliskie", "rodzina": "kepa_grzybow", "luki": [(225, 315)], "r": (44, 58), "n": 3, "k": (1.0, 1.2),
             "min_odstep": 14.0, "dosun": True},
            {"grupa": "Bliskie", "rodzina": "paproc", "luki": [(195, 345)], "r": (27, 40), "n": 10, "k": (1.0, 1.3)},
            {"grupa": "Bliskie", "rodzina": "mech_plat", "luki": [(0, 360)], "r": (26, 70), "n": 12, "k": (1.6, 3.2)},
            # ściana lasu: ciemniejsze krzaki przed pniami, dwa rzędy drzew coraz ciemniejsze ku głębi
            {"grupa": "Sciana", "rodzina": "krzak", "luki": [(0, 360)], "r": (60, 92), "n": 16, "k": (1.1, 1.6), "dosun": True},
            {"grupa": "Sciana", "rodzina": "drzewo_lasu", "warianty": ["dab", "okraglak", "sosna", "smukly", "swierk", "jarzebina"],
             "luki": [(0, 360)], "r": (66, 98), "n": 26, "k": (1.25, 1.75), "dosun": True, "min_odstep": 12.0, "cien": (0.74, 0.9)},
            {"grupa": "Sciana", "rodzina": "drzewo_lasu", "warianty": ["dab", "okraglak", "sosna", "swierk"],
             "luki": [(0, 360)], "r": (100, 124), "n": 16, "k": (1.6, 2.1), "dosun": True, "min_odstep": 16.0, "cien": (0.62, 0.76)},
            {"grupa": "Sciana", "rodzina": "drzewo_lasu", "warianty": ["grzyb"], "luki": [(215, 325)], "r": (62, 76), "n": 3,
             "k": (1.8, 2.3), "dosun": True, "min_odstep": 18.0},
        ],
        "punkty": [
            # kulisy boczne: tuż za walczącymi, na brzegach kadru planu ogólnego (kliny ±X są wolne od kamer)
            {"grupa": "Kulisy", "rodzina": "grzyb", "kat": 2, "r": 40, "k": 1.75, "ry": 200},
            {"grupa": "Kulisy", "rodzina": "grzyb", "kat": 352, "r": 46, "k": 1.25, "ry": 40},
            {"grupa": "Kulisy", "rodzina": "glaz", "kat": 10, "r": 29, "k": 0.85, "ry": 15},
            {"grupa": "Kulisy", "rodzina": "krzak", "kat": 357, "r": 26, "k": 1.2},
            {"grupa": "Kulisy", "rodzina": "grzyb", "kat": 178, "r": 40, "k": 1.9, "ry": 20},
            {"grupa": "Kulisy", "rodzina": "grzyb", "kat": 188, "r": 46, "k": 1.35, "ry": 110},
            {"grupa": "Kulisy", "rodzina": "glaz", "kat": 170, "r": 30, "k": 0.95, "ry": 200},
            {"grupa": "Kulisy", "rodzina": "krzak", "kat": 184, "r": 26, "k": 1.1},
            # olbrzymie pnie — znak polany; korony wychodzą nad polanę (wysoko, nad kamerami)
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 238, "r": 68, "k": 1.2, "ry": 20, "korona_ku": 58},
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 283, "r": 72, "k": 1.35, "ry": 75, "korona_ku": 103},
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 322, "r": 66, "k": 1.15, "ry": 140, "korona_ku": 142},
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 12, "r": 56, "k": 1.05, "ry": 200, "korona_ku": 192},
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 168, "r": 56, "k": 1.1, "ry": 300, "korona_ku": 348},
            {"grupa": "Olbrzymy", "rodzina": "olbrzym", "kat": 100, "r": 96, "k": 1.3, "ry": 10, "korona_ku": 280},
            {"grupa": "Swiatlo", "rodzina": "promien_swiatla", "kat": 232, "r": 64, "h": 36, "szer": 4.5, "ry": 10, "pochyl": 16},
            {"grupa": "Swiatlo", "rodzina": "promien_swiatla", "kat": 308, "r": 65, "h": 34, "szer": 3.2, "ry": 40, "pochyl": 18},
            {"grupa": "Swiatlo", "rodzina": "promien_swiatla", "kat": 214, "r": 66, "h": 38, "szer": 3.8, "ry": -20, "pochyl": 14},
        ],
        "korony_nad": {"y": (31.0, 40.0), "r_wew": 34.0, "r_zew": 104.0, "n": 20, "dl": (26, 40), "szer": (18, 28),
                       "kolory": [["lisc_ciemny", "lisc"], ["igla", "lisc_ciemny"], ["lisc_ciemny", "lisc_jasny"]]},
        "sylwety": [
            {"rodzina": "korona_daleka", "r": (132, 160), "krok_kata": 9.0, "k": (1.5, 2.0), "kolor": "sylweta_1"},
            {"rodzina": "korona_daleka", "r": (165, 195), "krok_kata": 11.0, "k": (1.8, 2.4), "kolor": "sylweta_2"},
            {"rodzina": "wzgorze", "r": (205, 224), "krok_kata": 14.0, "szer": (90, 130), "wys": (46, 64), "kolor": "arena_wzgorze_las"},
            {"rodzina": "korona_daleka", "r": (198, 220), "krok_kata": 15.0, "k": (2.3, 2.9), "kolor": "sylweta_3"},
            {"rodzina": "wal", "r": 232.0, "wys": 26.0, "kolor": "arena_mgla_las", "n": 24},
        ],
        "nastroj": {"Density": 0.34, "Offset": 0.18, "Haze": 1.3, "Glare": 0.0, "Color": "CFE3C9", "Decay": "86A889"},
        "detale": [
            {"typ": "liscie", "n": 14, "r": [26, 60], "y": [6, 26], "kolory": ["E8782A", "F2B83A", "A8D84E", "72BF3A"]},
            {"typ": "pylki", "punkty": "Swiatlo", "kolor": "FFE9A0", "tempo": 4},
        ],
    },
    # ------------------------------------------------------------------------------------------------ BAGNO
    # Okrągły pomost z desek nad ciemną wodą: kładka prowadzi do krzywej chatki na palach (punkt w środku tła), wokół
    # kępy z trzciną i liście grzybieni, cypryśniki z brodą mchu i wierzby w mgle, wieża z zieloną latarnią, błędne ogniki.
    "bagno": {
        "nazwa": "Pomost Nad Topielą",
        "model": "Bagno",
        "biom": "bagno",
        "zrodla": ["BagnoPasGra"],
        "O": (-3000.0, 0.0, 1800.0),
        "ziarno": 2711,
        "grunt": {"y": -1.8, "kolor": "bagno_ton", "mat": "SmoothPlastic", "woda": True,
                  "laty": [{"r": 42.0, "kolor": "bagno_woda", "mat": "SmoothPlastic"}],
                  "plamy": {"n": 14, "r": (28, 180), "rozmiar": (4, 12), "kolory": ["bagno_rzesa", "bagno_woda"]}},
        "plac": {"styl": "pomost", "kolory": ["bagno_deska", "bagno_deska_ciemna", "tusz"]},
        "obrecz": {"rodzina": "pal_obreczy", "r": 22.9, "n": 16, "k": (0.9, 1.0), "przerwy": [(262, 278)]},
        "warstwy": [
            {"grupa": "Bliskie", "rodzina": "grzybien", "luki": [(0, 360)], "r": (24, 60), "n": 10, "k": (0.9, 1.4)},
            {"grupa": "Bliskie", "rodzina": "kepa_z_trzcina", "luki": [(200, 255), (285, 340)], "r": (34, 56), "n": 5, "k": (0.9, 1.2),
             "dosun": True, "min_odstep": 10.0},
            {"grupa": "Bliskie", "rodzina": "kepa_z_trzcina", "luki": [(30, 150)], "r": (40, 84), "n": 4, "k": (0.9, 1.2),
             "min_odstep": 14.0},
            {"grupa": "Bliskie", "rodzina": "zatopiony_pien", "luki": [(205, 335)], "r": (46, 60), "n": 3, "k": (0.9, 1.2),
             "dosun": True, "min_odstep": 10.0},
            # ściana Bagna: trzcina, cypryśniki z brodą, wierzby, suche drzewa
            {"grupa": "Sciana", "rodzina": "kepa_trzciny", "luki": [(0, 360)], "r": (60, 94), "n": 10, "k": (1.0, 1.0), "dosun": True},
            {"grupa": "Sciana", "rodzina": "drzewo_bagna", "warianty": ["cyprys", "cyprys", "wierzba", "korzeniak", "suchy_omszaly"],
             "luki": [(0, 360)], "r": (66, 102), "n": 20, "k": (1.15, 1.6), "dosun": True, "min_odstep": 13.0},
            {"grupa": "Sciana", "rodzina": "drzewo_bagna", "warianty": ["cyprys", "wierzba", "cyprys"],
             "luki": [(0, 360)], "r": (104, 128), "n": 14, "k": (1.4, 1.8), "dosun": True, "min_odstep": 16.0},
            {"grupa": "Sciana", "rodzina": "kepa", "luki": [(0, 360)], "r": (64, 120), "n": 10, "k": (4.0, 7.0), "dosun": True},
        ],
        "punkty": [
            # kulisy boczne (±X): korzeniaki, trzcina i pale z latarniami tuż za walczącymi
            {"grupa": "Kulisy", "rodzina": "korzeniak", "kat": 3, "r": 38, "k": 1.2, "ry": 30},
            {"grupa": "Kulisy", "rodzina": "kepa_trzciny", "kat": 354, "r": 27},
            {"grupa": "Kulisy", "rodzina": "kepa_trzciny", "kat": 9, "r": 29},
            {"grupa": "Kulisy", "rodzina": "latarnia_pal", "kat": 0, "r": 25.5, "h": 6.0, "ry": 90},
            {"grupa": "Kulisy", "rodzina": "korzeniak", "kat": 177, "r": 38, "k": 1.3, "ry": 200},
            {"grupa": "Kulisy", "rodzina": "kepa_trzciny", "kat": 186, "r": 27},
            {"grupa": "Kulisy", "rodzina": "kepa_trzciny", "kat": 171, "r": 29},
            {"grupa": "Kulisy", "rodzina": "latarnia_pal", "kat": 180, "r": 25.5, "h": 6.0, "ry": 270},
            # kładka do chaty w środku tła, chaty na palach, wieża, łódka
            {"grupa": "Chaty", "rodzina": "kladka", "kat": 270, "r_od": 22.0, "r_do": 61.0},
            {"grupa": "Chaty", "rodzina": "chata_na_palach", "kat": 270, "r": 68, "k": 1.15, "ry": 0, "h0": 4.6},
            {"grupa": "Chaty", "rodzina": "chata_na_palach", "kat": 222, "r": 74, "k": 1.0, "ry": 38, "h0": 6.0},
            {"grupa": "Chaty", "rodzina": "chata_na_palach", "kat": 326, "r": 72, "k": 0.95, "ry": -44, "h0": 5.4},
            {"grupa": "Chaty", "rodzina": "wieza_obserwacyjna", "kat": 300, "r": 92, "k": 1.0, "ry": 15},
            {"grupa": "Chaty", "rodzina": "lodka", "kat": 252, "r": 27.5, "ry": 85},
            {"grupa": "Chaty", "rodzina": "latarnia_pal", "kat": 263, "r": 60.5, "h": 6.5, "ry": 0},
            {"grupa": "Chaty", "rodzina": "latarnia_pal", "kat": 277, "r": 60.5, "h": 6.0, "ry": 180},
            {"grupa": "Chaty", "rodzina": "chata_na_palach", "kat": 112, "r": 98, "k": 1.05, "ry": 180, "h0": 5.0},
        ],
        "sylwety": [
            {"rodzina": "sylweta_cyprysu", "r": (136, 165), "krok_kata": 9.0, "k": (1.3, 1.8), "kolor": "bagno_sylweta_1"},
            {"rodzina": "sylweta_cyprysu", "r": (170, 200), "krok_kata": 10.5, "k": (1.6, 2.2), "kolor": "bagno_sylweta_2"},
            {"rodzina": "wzgorze", "r": (206, 224), "krok_kata": 15.0, "szer": (90, 130), "wys": (34, 48), "kolor": "arena_wzgorze_bagno"},
            {"rodzina": "sylweta_cyprysu", "r": (200, 222), "krok_kata": 13.0, "k": (2.0, 2.6), "kolor": "bagno_sylweta_3"},
            {"rodzina": "wal", "r": 232.0, "wys": 24.0, "kolor": "arena_mgla_bagno", "n": 24},
        ],
        "mgla_platy": {"n": 8, "r": (46, 130), "dl": (22, 40), "szer": (12, 22), "y": -1.45, "alfa": 0.8},
        "nastroj": {"Density": 0.44, "Offset": 0.1, "Haze": 2.2, "Glare": 0.0, "Color": "AAB68F", "Decay": "5B7046"},
        "detale": [
            {"typ": "ogniki", "n": 9, "r": [30, 84], "y": [0.5, 6.0], "kolor": "C8E05A", "swiatla": 3},
            {"typ": "babelki", "n": 10, "r": [25, 70], "kolor": "8FB548"},
        ],
    },
    # ------------------------------------------------------------------------------------------------ PRÓBA
    # Plac ćwiczeń pod murem miasteczka: piaszczysty krąg z kredowym pierścieniem i niską barierką, manekiny, stojaki
    # z drewnianą bronią i tarcze łucznicze po bokach walczących, w tle trybuna, namioty, chorągwie z girlandą, za nimi
    # mur z bramą i dachy domków, na wzgórzu w dali twierdza. Od strony widowni łąka i drzewa.
    "proba": {
        "nazwa": "Plac Ćwiczeń Pod Murem",
        "model": "Proba",
        "biom": "proba",
        "zrodla": ["TestWalki2"],
        "O": (-3000.0, 0.0, 2600.0),
        "ziarno": 3711,
        "grunt": {"y": -0.5, "kolor": "trawa", "mat": "Grass",
                  "laty": [{"r": 31.0, "kolor": "arena_piasek_ciemny", "mat": "Sand"}],
                  "plamy": {"n": 10, "r": (50, 190), "rozmiar": (8, 18), "kolory": ["lisc", "lisc_jasny", "bruk"]}},
        "plac": {"styl": "piasek", "kolory": ["arena_piasek", "arena_kreda", "tusz"]},
        "obrecz": {"rodzina": "barierka", "r": 24.4, "n": 30, "k": (1.0, 1.0), "przerwy": [(80, 100), (262, 278)]},
        "warstwy": [
            {"grupa": "Bliskie", "rodzina": "bela_siana", "luki": [(205, 255), (285, 335)], "r": (31, 46), "n": 5, "k": (0.9, 1.1),
             "min_odstep": 6.0},
            {"grupa": "Bliskie", "rodzina": "kwiaty", "luki": [(30, 150)], "r": (30, 80), "n": 10, "k": (1.0, 1.0)},
            {"grupa": "Bliskie", "rodzina": "kanciak", "luki": [(190, 350)], "r": (30, 56), "n": 4, "k": (0.8, 1.1)},
            {"grupa": "Sciana", "rodzina": "manekin", "luki": [(215, 250), (290, 325)], "r": (60, 72), "n": 4, "k": (1.0, 1.15),
             "dosun": True, "twarza": True, "min_odstep": 7.0},
            {"grupa": "Sciana", "rodzina": "drzewo_miasta", "luki": [(15, 165)], "r": (70, 104), "n": 12, "k": (1.15, 1.5),
             "dosun": True, "min_odstep": 14.0},
            {"grupa": "Sciana", "rodzina": "drzewo_miasta", "luki": [(170, 200), (340, 10)], "r": (60, 84), "n": 4, "k": (1.1, 1.4),
             "dosun": True, "min_odstep": 14.0},
            {"grupa": "Miasto", "rodzina": "domek_tla", "luki": [(205, 335)], "r": (104, 124), "n": 10, "k": (1.0, 1.0), "dosun": True,
             "twarza": True, "min_odstep": 15.0},
            {"grupa": "Miasto", "rodzina": "domek_tla", "luki": [(30, 150)], "r": (108, 126), "n": 4, "k": (1.0, 1.0), "dosun": True,
             "twarza": True, "min_odstep": 20.0},
        ],
        "punkty": [
            # kulisy boczne (±X): manekiny, stojaki z bronią, tarcze łucznicze, bele
            {"grupa": "Kulisy", "rodzina": "manekin", "kat": 354, "r": 28.5, "k": 1.05},
            {"grupa": "Kulisy", "rodzina": "manekin", "kat": 8, "r": 30.5, "k": 1.0, "ry": 20},
            {"grupa": "Kulisy", "rodzina": "stojak_broni", "kat": 1, "r": 35.5},
            {"grupa": "Kulisy", "rodzina": "bela_siana_dwie", "kat": 351, "r": 39, "k": 1.05},
            {"grupa": "Kulisy", "rodzina": "tarcza_lucznicza", "kat": 176, "r": 30, "k": 1.05},
            {"grupa": "Kulisy", "rodzina": "manekin", "kat": 188, "r": 29, "k": 1.05, "ry": -15},
            {"grupa": "Kulisy", "rodzina": "stojak_broni", "kat": 181, "r": 36},
            {"grupa": "Kulisy", "rodzina": "bela_siana_dwie", "kat": 170, "r": 39, "k": 1.0},
            # tło: trybuna, namioty, chorągwie z girlandą przed bramą
            {"grupa": "Tlo", "rodzina": "trybuna", "kat": 236, "r": 64, "dl": 16.0},
            {"grupa": "Tlo", "rodzina": "namiot", "kat": 304, "r": 66},
            {"grupa": "Tlo", "rodzina": "namiot", "kat": 210, "r": 74, "kolory": ["dach_twierdza", "biel"]},
            {"grupa": "Tlo", "rodzina": "choragiew", "kat": 256, "r": 66, "wys": 15.0, "kolor": "dach_karczma", "ry": 0},
            {"grupa": "Tlo", "rodzina": "choragiew", "kat": 284, "r": 66, "wys": 15.0, "kolor": "dach_twierdza", "ry": 0},
            {"grupa": "Tlo", "rodzina": "choragiew", "kat": 4, "r": 44, "wys": 13.0, "kolor": "zloto", "ry": 90},
            {"grupa": "Tlo", "rodzina": "choragiew", "kat": 176, "r": 44, "wys": 13.0, "kolor": "dach_gildia", "ry": 90},
            {"grupa": "Tlo", "rodzina": "girlanda", "kat1": 256, "r1": 66, "kat2": 284, "r2": 66, "y": 13.6},
            # od strony widowni: jarmark przy placu (za wolną przestrzenią kamer)
            {"grupa": "Tlo", "rodzina": "stragan", "kat": 68, "r": 96, "towar": "chleby", "kolory": ["dach_stajnia", "biel"]},
            {"grupa": "Tlo", "rodzina": "stragan", "kat": 92, "r": 98, "towar": "jablka", "kolory": ["dach_karczma", "biel"]},
            {"grupa": "Tlo", "rodzina": "stragan", "kat": 116, "r": 96, "towar": "tkaniny", "kolory": ["dach_sklep", "biel"]},
            # mur miasteczka z bramą na osi tła i basztami
            {"grupa": "Mur", "rodzina": "mur_luk", "luk": (205, 335), "r": 96, "wys": 10.0, "brama": 270,
             "wieze": [208, 238, 302, 332]},
        ],
        "sylwety": [
            {"rodzina": "dach_daleki", "r": (136, 160), "krok_kata": 7.0, "k": (1.0, 1.5), "kolor": "arena_dach_daleki",
             "luki": [(195, 345)]},
            {"rodzina": "korona_daleka", "r": (140, 170), "krok_kata": 9.0, "k": (1.4, 1.9), "kolor": "sylweta_1", "luki": [(350, 190)]},
            {"rodzina": "korona_daleka", "r": (174, 198), "krok_kata": 11.0, "k": (1.6, 2.1), "kolor": "sylweta_2"},
            {"rodzina": "wzgorze", "r": (204, 224), "krok_kata": 14.0, "szer": (90, 130), "wys": (40, 58), "kolor": "arena_wzgorze_miasto"},
            {"rodzina": "zamek_daleki", "kat": 266, "r": 196, "k": 1.25, "y": 30.0},
            {"rodzina": "wal", "r": 232.0, "wys": 24.0, "kolor": "arena_mgla_miasto", "n": 24},
        ],
        "nastroj": {"Density": 0.27, "Offset": 0.24, "Haze": 1.1, "Glare": 0.25, "Color": "EADBC2", "Decay": "C9A27A"},
        "detale": [
            {"typ": "choragiewki", "grupa": "Tlo"},
            {"typ": "kurz", "r": [24, 40], "kolor": "E6C489"},
            {"typ": "ptaki", "n": 3, "r": [70, 120], "y": [44, 60]},
        ],
    },
    # ------------------------------------------------------------------------------------------------ DŻUNGLA
    # Kamienny dziedziniec zarośniętej świątyni: na osi tła schodkowa świątynia z kapliczką, obok wodospad z omszałej
    # skały, po bokach walczących posągi strażników oplecione lianami, olbrzymie liście i świecące kwiaty, wokół drzewa
    # dżungli z koronami-parasolami domykającymi niebo; w walce opadają płatki i krążą świetliki. Tło za walczącymi to
    # stonowany kamień świątyni (zielony potwór nie ginie na zielonym tle — ryzyko z PLAN_BIOMOW).
    "dzungla": {
        "nazwa": "Dziedziniec Zarośniętej Świątyni",
        "model": "Dzungla",
        "biom": "dzungla",
        "zrodla": ["DzunglaPasGra"],
        "O": (-3000.0, 0.0, 3400.0),
        "ziarno": 4711,
        # potwory Dżungli (ostateczne klucze 18.11, wymiary z swiat/test_walki2/dane; pas DzunglaPasGra wystawia tylko je)
        "przeciwnicy": ["zwijogon", "gebokwiat", "kokosowy_silacz", "pancernik_ruin", "waz_stu_lian"],
        "grunt": {"y": -0.6, "kolor": "dzungla_grunt", "mat": "Grass",
                  "laty": [{"r": 50.0, "kolor": "dzungla_grunt_jasny", "mat": "Grass"}, {"r": 31.0, "kolor": "dzungla_kamien_ciemny",
                                                                                         "mat": "Slate"}],
                  "plamy": {"n": 10, "r": (58, 190), "rozmiar": (8, 20), "kolory": ["dzungla_ziemia", "lisc_ciemny", "dzungla_grunt_jasny"]}},
        "plac": {"styl": "kamien", "kolory": ["dzungla_kamien", "dzungla_kamien_jasny", "dzungla_kamien_ciemny"]},
        "obrecz": {"rodzina": "kamien_obreczy", "r": 23.6, "n": 22, "k": (0.8, 1.15), "kolor": "dzungla_kamien", "przerwy": [(262, 278)]},
        "warstwy": [
            {"grupa": "Bliskie", "rodzina": "kwiat_swiecacy", "luki": [(200, 250), (290, 340)], "r": (28, 46), "n": 4, "k": (0.9, 1.2),
             "min_odstep": 7.0},
            {"grupa": "Bliskie", "rodzina": "lisc_parasol", "luki": [(200, 252), (288, 340)], "r": (34, 54), "n": 5, "k": (0.5, 0.65), "dosun": True,
             "min_odstep": 8.0},
            {"grupa": "Bliskie", "rodzina": "kolumna_zlamana", "luki": [(210, 250), (290, 330)], "r": (40, 56), "n": 3, "k": (0.9, 1.1),
             "dosun": True, "min_odstep": 12.0},
            {"grupa": "Bliskie", "rodzina": "kanciak_dzungli", "luki": [(190, 350)], "r": (28, 52), "n": 5, "k": (0.9, 1.3)},
            {"grupa": "Bliskie", "rodzina": "mech_plat", "luki": [(0, 360)], "r": (26, 70), "n": 6, "k": (1.6, 3.0)},
            {"grupa": "Bliskie", "rodzina": "kepa_parasoli", "luki": [(30, 150)], "r": (40, 86), "n": 4, "k": (0.8, 1.0), "min_odstep": 14.0},
            {"grupa": "Bliskie", "rodzina": "kwiat_swiecacy", "luki": [(30, 150)], "r": (32, 80), "n": 3, "k": (0.9, 1.1), "min_odstep": 10.0},
            {"grupa": "Bliskie", "rodzina": "krzew_dzungli", "luki": [(40, 140)], "r": (36, 84), "n": 2, "k": (0.9, 1.2), "min_odstep": 12.0,
             "kwiat": "dz_kwiat_czerwony"},
            # ściana dżungli z roślin mapy (swiat/dzungla_pas/rosliny.py): kępy liści-parasoli przed drzewami, drzewa-olbrzymy
            # i figowce z koronami-parasolami, palmy
            {"grupa": "Sciana", "rodzina": "kepa_parasoli", "luki": [(288, 252)], "r": (60, 92), "n": 10, "k": (1.1, 1.4), "dosun": True,
             "min_odstep": 9.0},
            {"grupa": "Sciana", "rodzina": "drzewo_dzungli", "luki": [(286, 254)], "r": (66, 100), "n": 14, "k": (1.0, 1.3), "dosun": True,
             "min_odstep": 13.0, "cien": (0.85, 1.0)},
            {"grupa": "Sciana", "rodzina": "figowiec", "luki": [(286, 254)], "r": (70, 100), "n": 4, "k": (1.1, 1.35), "dosun": True,
             "min_odstep": 14.0, "cien": (0.85, 1.0)},
            {"grupa": "Sciana", "rodzina": "palma", "luki": [(286, 254)], "r": (70, 104), "n": 5, "k": (1.1, 1.4), "dosun": True,
             "min_odstep": 12.0},
            {"grupa": "Sciana", "rodzina": "drzewo_dzungli", "luki": [(0, 360)], "r": (102, 126), "n": 10, "k": (1.25, 1.55), "dosun": True,
             "min_odstep": 16.0, "cien": (0.7, 0.85)},
        ],
        "punkty": [
            # kulisy boczne (±X): posągi strażników, olbrzymie liście, świecące kwiaty
            {"grupa": "Kulisy", "rodzina": "posag_dzungli", "kat": 0, "r": 30, "k": 1.0},
            {"grupa": "Kulisy", "rodzina": "posag_dzungli", "kat": 180, "r": 30, "k": 1.0},
            {"grupa": "Kulisy", "rodzina": "kepa_parasoli", "kat": 352, "r": 37, "k": 1.2},
            {"grupa": "Kulisy", "rodzina": "kepa_parasoli", "kat": 9, "r": 39, "k": 1.0},
            {"grupa": "Kulisy", "rodzina": "kepa_parasoli", "kat": 171, "r": 38, "k": 1.1},
            {"grupa": "Kulisy", "rodzina": "kepa_parasoli", "kat": 189, "r": 37, "k": 1.2},
            {"grupa": "Kulisy", "rodzina": "kwiat_swiecacy", "kat": 6, "r": 26, "k": 1.1},
            {"grupa": "Kulisy", "rodzina": "kwiat_swiecacy", "kat": 354, "r": 27, "k": 1.0},
            {"grupa": "Kulisy", "rodzina": "kwiat_swiecacy", "kat": 174, "r": 26, "k": 1.0},
            {"grupa": "Kulisy", "rodzina": "kwiat_swiecacy", "kat": 186, "r": 27, "k": 1.1},
            # tło: świątynia na osi, posągi przy schodach, wodospad z boku, stojąca kolumna
            {"grupa": "Swiatynia", "rodzina": "swiatynia", "kat": 270, "r": 96, "k": 1.2},
            {"grupa": "Swiatynia", "rodzina": "posag_dzungli", "kat": 259, "r": 74, "k": 0.85},
            {"grupa": "Swiatynia", "rodzina": "posag_dzungli", "kat": 281, "r": 74, "k": 0.85},
            {"grupa": "Wodospad", "rodzina": "wodospad", "kat": 318, "r": 90, "k": 1.0},
            {"grupa": "Swiatynia", "rodzina": "kolumna_stojaca", "kat": 226, "r": 66, "k": 1.1},
            {"grupa": "Swiatynia", "rodzina": "kolumna_stojaca", "kat": 236, "r": 72, "k": 1.0},
            # od strony widowni: ruina bramy dziedzińca na osi (za wolną przestrzenią kamer) — znak tła w ujęciu z drugiej
            # strony; po obejrzeniu podglądów zamiast dwóch samotnych kolumn, które ginęły w mgle
            {"grupa": "Swiatynia", "rodzina": "brama_ruin", "kat": 90, "r": 102, "k": 1.25},
        ],
        "korony_nad": {"y": (34.0, 44.0), "r_wew": 34.0, "r_zew": 106.0, "n": 20, "dl": (26, 40), "szer": (18, 28),
                       "kolory": [["dzungla_lisc", "dzungla_lisc_jasny"], ["lisc_ciemny", "dzungla_lisc"], ["igla", "dzungla_lisc"]]},
        "sylwety": [
            {"rodzina": "korona_daleka", "r": (132, 160), "krok_kata": 9.0, "k": (1.5, 2.0), "kolor": "dzungla_sylweta_1"},
            {"rodzina": "korona_daleka", "r": (165, 195), "krok_kata": 11.0, "k": (1.8, 2.4), "kolor": "dzungla_sylweta_2"},
            {"rodzina": "wzgorze", "r": (205, 224), "krok_kata": 14.0, "szer": (90, 130), "wys": (46, 66), "kolor": "arena_wzgorze_dzungla"},
            {"rodzina": "korona_daleka", "r": (198, 220), "krok_kata": 15.0, "k": (2.3, 2.9), "kolor": "dzungla_sylweta_3"},
            {"rodzina": "wal", "r": 232.0, "wys": 26.0, "kolor": "arena_mgla_dzungla", "n": 24},
        ],
        "nastroj": {"Density": 0.34, "Offset": 0.16, "Haze": 1.5, "Glare": 0.0, "Color": "8FC79A", "Decay": "4E8A5A"},
        "detale": [
            {"typ": "liscie", "n": 16, "r": [26, 60], "y": [6, 26], "kolory": ["FF8FB8", "FFD84A", "E5392B", "FFF6E0"]},
            {"typ": "ogniki", "n": 10, "r": [30, 80], "y": [1.0, 7.0], "kolor": "D8FF6A", "swiatla": 2},
            {"typ": "pylki", "punkty": "Wodospad", "kolor": "E8FBFF", "tempo": 6},
        ],
    },
}

# źródło walki (nazwa kontenera) → arena; kontener może też mieć atrybut BiomAreny (np. "dzungla") — ma pierwszeństwo
ZRODLA = {zrodlo: klucz for klucz, a in ARENY.items() for zrodlo in a["zrodla"]}