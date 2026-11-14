# -*- coding: utf-8 -*-
"""MUCHOMORNIK — zwykły przeciwnik lasu: niski grzybowy ludek (ok. 3,5 studa z kapeluszem; gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/muchomornik.py --wyj <folder> --klip atak

Opis z danych walki (tools/walka/dane_walki.json, id „muchomornik”): mały szaman lasu — niski grzybowy ludek
z czerwonym kapeluszem w białe kropki, bródką z mchu i krzywą laską z korzenia, z której sypią się świecące
zarodniki. Bije laską, a umiejętność „chmura zarodników” truje magią. Troche śmieszny, trochę złośliwy.

Sylwetka (rozpoznawalna po samym kształcie): ogromny, schodkowy kapelusz (2,9 studa szerokości przy ciele
szerokim na 1,2) przekrzywiony zawadiacko na bok i lekko w tył, pod nim kremowa głowa-trzon z wielkim nosem,
krzaczasta broda z mchu do pasa, beczkowaty tułów z białym „pierścieniem” pod szyją (jak prawdziwy muchomor),
krótkie nóżki w drewnianych chodakach; w prawej dłoni krzywa laska z korzenia zakończona hakiem, w którym wisi
świecąca bulwa, a wokół niej krążą trzy zarodniki.
Twarz: brwi z mchu w złośliwym „V” (prawa niżej), oczy zezujące w bok, wielki nos-kartofel, krzywy uśmieszek
z jednym zębem, rumieńce.

Paleta (6 rodzin + akcent): czerwień kapelusza (dwa odcienie), biel kropek i pierścienia, krem trzonu (dwa
odcienie, blaszki), mech (dwie zielenie), drewno (dwa brązy), tusz; AKCENT: świecąca limonkowa zieleń zarodników.

Szkielet (własny, typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Biodra > {Tulow > {Glowa > {Kapelusz > Zarodnik0…9, Broda, Powieki},
                              RamieL > DlonL, RamieP > DlonP > Laska > ZarodekL0…2},
                     NogaL > StopaL, NogaP > StopaP}
- Kapelusz ma własną kość: chwieje się z opóźnieniem, potrząsa nim w umiejętności, spada z głowy przy upadku;
- Zarodnik0…9 siedzą w spoczynku schowane w środku kapelusza — w umiejętności wylatują w górę, opadają na ziemię
  i wsiąkają w nią; ZarodekL0…2 krążą wokół bulwy laski;
- Laska jest kością modelu; w klipach może się przesuwać w dłoni wzdłuż swojej osi (chwyt bliżej końca przy ciosie);
- Powieki chowają się w głowie pod kapeluszem (mrugnięcie, zmrużenie przy złośliwym śmiechu, zamknięte po upadku).

Klipy (30 kl./s; postać patrzy w +Z i w tę stronę atakuje):
  idle (pętla 2,4 s), ruch (drobny, kołyszący chód, pętla 0,8 s), atak (laska w górę z prawej strony i „rąbnięcie”
  z góry przed siebie, trafienie w kl. 12, 0,9 s), umiejetnosc (chmura zarodników: laska w bok, uderzenie
  laską w ziemię, potrząsanie kapeluszem, dziesięć zarodników wylatuje z kapelusza i opada wokół, 2 s),
  trafienie (szarpnięcie w tył, kapelusz podskakuje, 0,6 s), unik (podskok w lewo i powrót, 0,9 s),
  upadek (zawroty głowy — kapelusz kręci się na głowie — klapnięcie na pupę z obrotem w bok, przewrót na plecy,
  kapelusz spada z głowy i zsuwa mu się na twarz, przechylony kopułą do widza; leży bokiem do kamery gry,
  nóżki w górze; kończy się leżeniem, 2 s),
  wiwat (złośliwy śmiech z podskokami i laską w górze, pętla 2 s).
Klipy jednorazowe i wiwat są zapisane jako pozy kluczowe (_sekwencja) zamienione na klucz w każdej klatce:
stopy stoją płasko na ziemi, a ciało nigdy nie schodzi pod ziemię; laska przechodzi między pozami po łuku kierunku
(w świecie), więc nie przecina ciała. Zmiany rób w pozach kluczowych w tym pliku.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "muchomornik"

PALETA = {
    "kapelusz": "D8322A", "kapelusz_cien": "9C1E1A",
    "kropka": "FFFFFF",            # czysta biel: w cieniu kopuły kropki nie szarzeją
    "trzon": "F0DEBC", "trzon_cien": "CFB48A", "blaszki": "E3BC98",
    "nos": "E8A07E", "rumieniec": "F07E6E",
    "mech": "6DBA3C", "mech_ciemny": "3F7F2D",
    "drewno": "8C5A2B", "drewno_ciemne": "553419",
    "zarodnik": "62F23C",
}

SLABOSCI = [
    "Kości Muchomornika nie są R15 (własny szkielet: Root + 28 kości, w tym 13 kości zarodników) — klipy "
    "importuje się na własny rig; import do Roblox Studio nie był testowany.",
    "Bryły są sztywno przypięte do kości (jedna siatka na kość): ramiona lekko siedzą w tułowiu, broda dotyka "
    "brzucha, a laska przechodzi przez prawą dłoń-rękawicę (celowo — dłoń ją „obejmuje”).",
    "Zarodniki to dziesięć małych brył na własnych kościach — w spoczynku schowane w środku kapelusza. Po wylądowaniu "
    "wsiąkają w ziemię (schodzą pod nią w ostatnich klatkach umiejętności), więc w grze ziemia musi je zasłonić; "
    "prawdziwej chmury (dymu, poświaty, trucizny) nie ma — dorobić efektem cząsteczek na ChmuraAttachment.",
    "Świecenie bulwy i zarodników jest tylko w teksturze-palecie (emisja) — w grze trzeba je dać materiałem Neon "
    "albo PointLight.",
    "Laska przesuwa się w dłoni wzdłuż swojej osi (w ataku chwyt bliżej dolnego końca, przy uderzeniu w ziemię "
    "wyżej) — z daleka nie widać, ale z bliska laska „ślizga się” przez rękawicę.",
    "Przy upadku kapelusz spada z głowy i zsuwa się leżącemu na twarz (oparty o nos i brodę, przechylony kopułą "
    "do widza — miejsce liczone w module na skrzynkach brył, więc spód kopuły może o włos wisieć nad brodą); twarzy "
    "wtedy nie widać. Leży bokiem do kamery od przodu (obrót o 60° przy siadzie) — z kamery od drugiego boku "
    "kapelusz zasłoni więcej. Po przejściu z upadku do idle kapelusz wraca na głowę skokiem — w grze po upadku "
    "postać i tak znika.",
    "Kapelusz ma 19 kropek-brył (wystają 0,03 nad skośne ściany kopuły); kopuła to ośmiokątne ścięte "
    "stożki, więc z bliska widać kanty.",
    "Chód jest w miejscu (stopy ślizgają się względem ziemi); nóżki są bez kolan, więc krok to kołysanie całych "
    "nóg i bioder.",
    "Powieki przy mrugnięciu na 1–2 klatki wysuwają się spod kapelusza przez czoło (szybko, z daleka nie widać).",
    "Kolizje sprawdzane w przybliżeniu skryptem poza modułem (punkty skrzynek brył w każdej klatce, kopuła jako "
    "ośmiokąt): laska, zarodniki laski i dłonie nie wchodzą w głowę, kapelusz, brodę, tułów ani spodenki; zarodniki "
    "kapelusza po wylocie (kl. 23–25 wychodzą przez kopułę — celowo) nie przelatują przez kapelusz ani ciało; "
    "stopy, ciało i laska nie schodzą pod ziemię. Ramiona, nogi i broda względem siebie nie były sprawdzane liczbowo. "
    "Przegląd 14.11.2026 powtórzył kontrolę drugim skryptem (walec i stożek jako elipsa w przekroju): laska, "
    "zarodki laski i dłonie bez wejścia w głowę, kapelusz, brodę i tułów we wszystkich klatkach ośmiu klipów.",
    "Atak widziany od przodu: cios idzie w stronę kamery, więc laska w trafieniu jest skrócona perspektywą, a "
    "przechylony do przodu kapelusz na 3–4 klatki zasłania twarz (to celowe „dobicie” ciężkim kapeluszem). Z boku "
    "łuk ciosu czyta się najlepiej.",
    "Kadr filmów i arkuszy jest wspólny dla wszystkich klipów, a zarodniki wylatują do ok. 4,3 studa i lądują ok. "
    "2 studów od niego — w filmach postać zajmuje mniej niż połowę wysokości kadru; bliżej: plansza i kadr "
    "bohaterski.",
    "Klipy to szkice (0,6–2 s), nie gotowa animacja; mimika tylko z powiek i ruchu kapelusza.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
BIODRA = (0.0, 0.55, 0.0)
TULOW = (0.0, 0.78, 0.0)
SZYJA = (0.0, 1.5, 0.0)
KAP = (0.0, 2.4, -0.05)            # środek spodu kapelusza (oś chwiania)
KAP_POCHYL = (-6.0, 0.0, -6.0)     # zawadiacko: przód do góry, czubek w lewo (+X) — prawa strona z laską wyżej
BRODA = (0.0, 1.62, 0.52)
POWIEKI = (0.0, 2.06, 0.5)
X_BARK, Y_BARK, Y_LOKIEC = 0.66, 1.36, 1.0
X_NOGI, Y_KOSTKA = 0.3, 0.24
CHWYT = (-0.82, 0.8, 0.12)         # środek prawej dłoni = staw laski
L_DOL = 0.8                        # laska poniżej chwytu (w spoczynku dolny koniec na ziemi; powyżej ok. 1,2)
GLOWA_ROZ = (1.3, 0.96, 1.1)       # klocek głowy (od y = 1,5 do 2,46)

# zarodniki w kapeluszu: (x, y, z) w układzie pochylonego kapelusza (od KAP), rozmiar
ZARODNIKI = [((-0.8, 0.5, 0.45), 0.26), ((0.75, 0.55, 0.4), 0.24), ((-0.2, 0.6, 0.7), 0.28),
             ((0.3, 0.55, -0.65), 0.24), ((-0.75, 0.6, -0.35), 0.26), ((0.8, 0.5, -0.25), 0.24),
             ((0.15, 0.65, 0.15), 0.3), ((-0.3, 0.62, -0.2), 0.26), ((0.45, 0.6, 0.7), 0.24),
             ((-0.45, 0.65, -0.75), 0.22)]
# zarodniki przy lasce: pozycja względem chwytu (osie laski = osie modelu w spoczynku), rozmiar
ZARODKI_L = [((-0.5, 1.12, 0.12), 0.1), ((-0.56, 0.86, -0.12), 0.09), ((-0.3, 0.7, 0.14), 0.09)]
BULWA = (-0.27, 0.93, 0.0)         # świecąca bulwa w haku laski (względem chwytu)

ZAMKNIETE, PRZYMRUZ = (0.0, -0.4, 0.11), (0.0, -0.21, 0.11)     # przesunięcie powiek


def _kap_pkt(lok):
    """Punkt z układu pochylonego kapelusza -> układ modelu (spoczynek)."""
    q = razy_wektor(macierz_obrotu(*KAP_POCHYL), lok)
    return tuple(KAP[i] + q[i] for i in range(3))


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Muchomornik", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Biodra", "Root", staw=BIODRA, dl=0.3)
    p.kosc("Tulow", "Biodra", staw=TULOW, dl=0.5)
    p.kosc("Glowa", "Tulow", staw=SZYJA, dl=0.5)
    p.kosc("Kapelusz", "Glowa", staw=KAP, dl=0.5)
    for i, (lok, _) in enumerate(ZARODNIKI):
        p.kosc("Zarodnik%d" % i, "Kapelusz", staw=_kap_pkt(lok), dl=0.15)
    p.kosc("Broda", "Glowa", staw=BRODA, dl=0.25)
    p.kosc("Powieki", "Glowa", staw=POWIEKI, dl=0.15)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Ramie" + s, "Tulow", staw=(zn * X_BARK, Y_BARK, 0.0), dl=0.3)
        p.kosc("Dlon" + s, "Ramie" + s, staw=(zn * 0.78, Y_LOKIEC, 0.0), dl=0.3)
        p.kosc("Noga" + s, "Biodra", staw=(zn * X_NOGI, 0.5, 0.0), dl=0.25)
        p.kosc("Stopa" + s, "Noga" + s, staw=(zn * X_NOGI, Y_KOSTKA, 0.0), dl=0.2)
    p.kosc("Laska", "DlonP", staw=CHWYT, dl=0.6)
    for i, (lok, _) in enumerate(ZARODKI_L):
        p.kosc("ZarodekL%d" % i, "Laska", staw=tuple(CHWYT[j] + lok[j] for j in range(3)), dl=0.1)

    _nogi(p)
    _tulow(p)
    _glowa(p)
    _kapelusz(p)
    _rece(p)
    _laska(p)
    _zarodniki(p)

    # punkty zaczepienia dla gry: korzeń, tabliczka nad kapeluszem, chmura zarodników, bulwa laski
    p.zaczep("RootAttachment", "Biodra", (-BIODRA[0], -BIODRA[1], -BIODRA[2]))
    p.zaczep("GlowaAttachment", "Kapelusz", (0, 1.25, 0))
    p.zaczep("ChmuraAttachment", "Kapelusz", (0, 0.9, 0))
    p.zaczep("LaskaAttachment", "Laska", BULWA)

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        x = zn * X_NOGI
        with _model(p, "Noga" + s):
            p.blok("Noga", (x, 0.38, 0.0), (0.34, 0.32, 0.34), "trzon", faza=0.06)
        # chodaki z drewna z zadartym czubkiem
        with _model(p, "Stopa" + s):
            p.blok("Chodak", (x, 0.12, 0.08), (0.44, 0.24, 0.6), "drewno_ciemne", faza=0.08)
            p.blok("Chodak wierzch", (x, 0.245, 0.02), (0.34, 0.03, 0.36), "drewno", "matowy", faza=0.0)
            p.klin("Chodak czubek", (x, 0.2, 0.42), (0.34, 0.16, 0.16), "drewno_ciemne", rot=(0, 180, 0))
            p.blok("Chodak podeszwa", (x, 0.02, 0.08), (0.46, 0.04, 0.62), "drewno", "matowy", faza=0.0)


def _tulow(p):
    # biodra: krótkie spodenki z kory i kremowa bulwa trzonu u dołu (jak pochwa muchomora)
    with _model(p, "Biodra"):
        p.blok("Spodenki", (0, 0.63, 0.0), (1.12, 0.38, 0.95), "drewno", "matowy", faza=0.1)
        p.blok("Spodenki szew", (0, 0.6, 0.48), (0.05, 0.28, 0.03), "drewno_ciemne", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Nogawka", (zn * 0.3, 0.46, 0.0), (0.44, 0.08, 0.44), "drewno_ciemne", "matowy", faza=0.02)
    with _model(p, "Tulow"):
        p.blok("Brzuch", (0, 1.1, 0.02), (1.2, 0.66, 1.0), "trzon", faza=0.12)
        p.blok("Piers", (0, 1.4, 0.0), (1.08, 0.2, 0.92), "trzon", faza=0.06)
        # włókna trzonu (cienkie pionowe kreski, wystają 0,02)
        for i, (x, y, h) in enumerate(((-0.42, 1.08, 0.4), (0.4, 1.12, 0.36))):
            p.blok("Wlokno przod %d" % i, (x, y, 0.535), (0.05, h, 0.03), "trzon_cien", "matowy", faza=0.0)
        for i, (x, h) in enumerate(((-0.3, 0.44), (0.05, 0.5), (0.35, 0.4))):
            p.blok("Wlokno tyl %d" % i, (x, 1.12, -0.495), (0.05, h, 0.03), "trzon_cien", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Wlokno bok", (zn * 0.615, 1.1, 0.1), (0.03, 0.42, 0.05), "trzon_cien", "matowy", faza=0.0)
        # pas z korzonka ze sprzączką-żołędziem
        p.blok("Pas", (0, 0.84, 0.02), (1.24, 0.13, 1.04), "drewno_ciemne", "matowy", faza=0.03)
        p.blok("Zoladz", (0.28, 0.82, 0.56), (0.18, 0.2, 0.08), "drewno", faza=0.03)
        p.blok("Zoladz czapka", (0.28, 0.93, 0.565), (0.22, 0.07, 0.09), "drewno_ciemne", "matowy", faza=0.02)
        # pierścień pod szyją (biała falbanka jak u muchomora) z ząbkami
        p.blok("Pierscien", (0, 1.47, 0.0), (1.3, 0.1, 1.1), "kropka", "matowy", faza=0.03)
        for i, (x, z) in enumerate(((-0.62, 0.3), (-0.62, -0.25), (0.62, 0.3), (0.62, -0.25))):
            p.blok("Falbanka bok %d" % i, (x, 1.37, z), (0.06, 0.14, 0.3), "kropka", "matowy", faza=0.0)
        for i, x in enumerate((-0.4, 0.0, 0.4)):
            p.blok("Falbanka tyl %d" % i, (x, 1.37, -0.535), (0.3, 0.14, 0.06), "kropka", "matowy", faza=0.0)


def _glowa(p):
    w, h, d = GLOWA_ROZ
    yc = SZYJA[1] + h / 2
    z = d / 2
    with _model(p, "Glowa"):
        p.blok("Glowa", (0, yc, 0), GLOWA_ROZ, "trzon", faza=0.12)
        # oczy: białka, źrenice zezujące w bok (złośliwie), błyski
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.29
            p.blok("Bialko " + s, (x, 2.06, z + 0.015), (0.32, 0.36, 0.05), "bialy", "polysk", faza=0.03)
            p.blok("Zrenica " + s, (x + 0.06, 2.03, z + 0.045), (0.15, 0.22, 0.04), "tusz", "polysk", faza=0.02)
            p.blok("Blysk " + s, (x + 0.03, 2.1, z + 0.07), (0.06, 0.06, 0.02), "bialy", faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.47, 1.8, z + 0.01), (0.2, 0.1, 0.04), "rumieniec", "matowy", faza=0.0)
            p.blok("Bokobrod " + s, (zn * (w / 2 + 0.03), 1.7, 0.22), (0.08, 0.34, 0.4), "mech_ciemny", "matowy",
                   faza=0.03)
        # brwi z mchu: złośliwe V, prawa niżej i ostrzej
        p.blok("Brew L", (0.29, 2.29, z + 0.04), (0.42, 0.12, 0.09), "mech_ciemny", "matowy", rot=(0, 0, 14),
               faza=0.02)
        p.blok("Brew P", (-0.29, 2.26, z + 0.04), (0.42, 0.12, 0.09), "mech_ciemny", "matowy", rot=(0, 0, -24),
               faza=0.02)
        # wielki nos-kartofel
        p.kula("Nos", (0.02, 1.9, z + 0.12), (0.32, 0.26, 0.28), "nos", "zwykly", segm=8)
        # krzywy uśmieszek z jednym zębem
        p.blok("Usta", (0.03, 1.705, z + 0.015), (0.54, 0.1, 0.05), "tusz", rot=(0, 0, 9), faza=0.0)
        p.blok("Kacik", (0.29, 1.76, z + 0.015), (0.08, 0.12, 0.05), "tusz", rot=(0, 0, 20), faza=0.0)
        # ząb sterczy z ust nad wąsami (wcześniej chował się za nimi) — wystaje 0,03 przed usta
        p.blok("Zab", (-0.1, 1.69, z + 0.045), (0.1, 0.08, 0.03), "bialy", "polysk", rot=(0, 0, 9), faza=0.0)
        # kępka mchu na czubku głowy (widać ją, gdy kapelusz spadnie)
        p.blok("Lysina mech", (0.1, 2.48, -0.05), (0.62, 0.06, 0.55), "mech", "matowy", faza=0.02)
    # broda z mchu: gruba poducha pod ustami i trzy kosmyki w dół
    with _model(p, "Broda"):
        # trapez: szeroko pod ustami, wąsko u dołu (nie prostokątna „maska”)
        p.ostroslup("Broda", (0, 1.41, 0.66), (0.6, 0.42, 0.24), "mech", "matowy", gora=(0.98, 0.27))
        p.blok("Broda wasy", (0, 1.6, 0.6), (0.9, 0.08, 0.2), "mech", "matowy", faza=0.03)
        for i, (x, dl, sz, k) in enumerate(((-0.2, 0.3, 0.22, "mech_ciemny"), (0.02, 0.44, 0.26, "mech"),
                                            (0.21, 0.26, 0.2, "mech_ciemny"))):
            p.ostroslup("Kosmyk %d" % i, (x, 1.21 - dl / 2 + 0.02, 0.66), (sz, dl, 0.2), k, "matowy",
                        rot=(180, 0, 0), gora=(0.0, 0.0))
    # powieki: schowane w głowie pod kapeluszem; mrugnięcie = zjazd w dół i do przodu
    with _model(p, "Powieki"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Powieka " + s, (zn * 0.29, 2.46, z - 0.06), (0.36, 0.4, 0.04), "trzon_cien", "matowy", faza=0.0)


def _kropka(p, nazwa, pos, size, rot=(0, 0, 0)):
    p.blok(nazwa, pos, size, "kropka", "matowy", rot=rot, faza=0.02)


# kopuła kapelusza: ośmiokątne ścięte stożki (szer X, głęb Z = średnice dołu; y od, y do; góra = ułamek promienia)
KOPULA = (("Kopula dol", 2.95, 2.65, 0.2, 0.58, 0.82), ("Kopula gora", 2.42, 2.17, 0.58, 1.02, 0.55))


def _kropki_na_stozku(p, nazwa, kop, kropki):
    """Kropki leżące na skośnych ścianach ośmiokątnego ściętego stożka (segm=8: ściany prostopadłe do X, Z i
    przekątnych). kropki = [(numer ściany 0…7 od +Z w stronę +X, szer, wys wzdłuż skosu, przesunięcie w bok,
    przesunięcie wzdłuż skosu)]. Wystają 0,03 nad ścianę."""
    _, sx, sz, y0, y1, gora = kop
    a0, c0 = sx / 2, sz / 2
    a1, c1 = a0 * gora, c0 * gora
    h = y1 - y0
    for j, (sc, szer, wys, wbok, wskos) in enumerate(kropki):
        fi = math.radians(45 * sc)
        s, c = math.sin(fi), math.cos(fi)
        # ściana w przekroju na wysokości: punkty (x/a)·s + (z/c)·c = 1 (ośmiokąt foremny przeskalowany do elipsy)
        nx, nz = s / a0, c / c0
        nl = math.hypot(nx, nz)
        nx, nz = nx / nl, nz / nl                       # kierunek normalnej w poziomie (dół)
        d0 = (a0 * s * nx + c0 * c * nz)                # odległość ściany od osi u dołu i u góry
        d1 = (a1 * s * nx + c1 * c * nz)
        beta = math.atan2(d0 - d1, h)                   # nachylenie ściany od pionu
        t = 0.5 + wskos
        y = y0 + h * t
        d = d0 + (d1 - d0) * t
        styczna = (nz, -nx)                             # w poziomie wzdłuż ściany
        x = nx * d + styczna[0] * wbok
        z = nz * d + styczna[1] * wbok
        # wysunięcie 0,03 po normalnej ściany (z nachyleniem)
        ox, oy, oz = nx * math.cos(beta), math.sin(beta), nz * math.cos(beta)
        _kropka(p, "%s %d" % (nazwa, j), (x + ox * 0.015, y + oy * 0.015, z + oz * 0.015), (szer, wys, 0.04),
                rot=(-math.degrees(beta), math.degrees(math.atan2(nx, nz)), 0))


def _kapelusz(p):
    with _model(p, "Kapelusz"), p.uklad(pos=KAP, obrot=KAP_POCHYL):
        p.walec("Blaszki", (0, 0.0, 0), (2.62, 0.1, 2.36), "blaszki", "matowy", faza=0.02, segm=8)
        # blaszki: promieniste kreski na spodzie (widać je z dołu i gdy kapelusz spada)
        for i in range(8):
            a = math.radians(22.5 + 45 * i)
            r = 0.85
            p.blok("Blaszka %d" % i, (r * math.sin(a), -0.065, r * math.cos(a)), (0.05, 0.03, 0.75),
                   "trzon_cien", "matowy", rot=(0, math.degrees(a), 0), faza=0.0)
        # gruby brzeg (ciemniejszy spód) i kopuła z dwóch ściętych stożków
        p.walec("Rondo", (0, 0.06, 0), (2.95, 0.08, 2.65), "kapelusz_cien", "matowy", faza=0.0, segm=8)
        p.walec("Rondo brzeg", (0, 0.15, 0), (2.95, 0.1, 2.65), "kapelusz", faza=0.02, segm=8)
        for n, sx, sz, y0, y1, gora in KOPULA:
            p.stozek(n, (0, (y0 + y1) / 2, 0), (sx, y1 - y0, sz), "kapelusz", "zwykly", gora=gora, segm=8)
        p.walec("Kopula czubek", (0, 1.06, 0), (1.05, 0.08, 0.94), "kapelusz", faza=0.03, segm=8)
        # kropki: na dolnej kopule na zmianę z górną (nie w rzędach), różne rozmiary
        _kropki_na_stozku(p, "Kropka dol", KOPULA[0],
                          ((0, 0.5, 0.3, -0.15, 0.02), (1, 0.34, 0.24, 0.12, -0.08), (2, 0.46, 0.3, 0.18, 0.04),
                           (3, 0.3, 0.22, -0.1, -0.1), (4, 0.5, 0.3, 0.1, 0.0), (5, 0.36, 0.26, -0.2, -0.05),
                           (6, 0.44, 0.3, -0.05, 0.03), (7, 0.32, 0.24, 0.15, -0.08)))
        _kropki_na_stozku(p, "Kropka gora", KOPULA[1],
                          ((0, 0.3, 0.26, 0.2, 0.15), (1, 0.42, 0.34, -0.05, -0.05), (3, 0.36, 0.3, 0.08, 0.08),
                           (4, 0.28, 0.24, -0.15, 0.12), (5, 0.42, 0.34, 0.05, -0.08), (7, 0.36, 0.3, -0.1, 0.05),
                           (2, 0.24, 0.2, 0.0, 0.22), (6, 0.26, 0.22, 0.05, -0.2)))
        # na wierzchu: jedna duża kropka (widać ją z góry — kamera gry patrzy z góry) i dwie małe
        _kropka(p, "Kropka wierzch duza", (-0.1, 1.11, 0.05), (0.5, 0.04, 0.46))
        _kropka(p, "Kropka wierzch 1", (0.25, 1.11, -0.22), (0.14, 0.04, 0.14))
        _kropka(p, "Kropka wierzch 2", (0.22, 1.11, 0.28), (0.12, 0.04, 0.12))


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Ramie" + s):
            p.blok("Ramie", (zn * 0.76, 1.19, 0.0), (0.34, 0.42, 0.38), "trzon", faza=0.07)
            p.blok("Ramie lata", (zn * 0.76, 1.33, 0.0), (0.38, 0.12, 0.42), "kropka", "matowy", faza=0.03)
        with _model(p, "Dlon" + s):
            p.blok("Mankiet", (zn * 0.8, 0.98, 0.02), (0.4, 0.12, 0.42), "mech_ciemny", "matowy", faza=0.03)
            p.blok("Dlon", (zn * 0.82, 0.8, 0.04), (0.42, 0.38, 0.44), "trzon", faza=0.09)
            p.blok("Kciuk", (zn * 0.72, 0.86, 0.29), (0.14, 0.18, 0.12), "trzon", faza=0.03)


def _laska(p):
    """Krzywa laska z korzenia (oś +Y od chwytu): trzy wygięte odcinki, sęki, hak u góry ze świecącą bulwą,
    korzonki u dołu."""
    with p.na("Laska"):
        p.blok("Laska dol", (0.0, -0.44, 0.0), (0.18, 0.76, 0.18), "drewno", "matowy", rot=(0, 0, 4), faza=0.03)
        p.blok("Laska srodek", (0.02, 0.2, 0.0), (0.17, 0.62, 0.17), "drewno", "matowy", rot=(0, 0, -7), faza=0.03)
        p.blok("Laska gora", (-0.01, 0.76, 0.0), (0.16, 0.56, 0.16), "drewno", "matowy", rot=(3, 0, 6), faza=0.03)
        p.blok("Sek 1", (0.0, -0.1, 0.0), (0.23, 0.08, 0.23), "drewno_ciemne", "matowy", faza=0.02)
        p.blok("Sek 2", (0.03, 0.5, 0.0), (0.22, 0.08, 0.22), "drewno_ciemne", "matowy", faza=0.02)
        p.blok("Galazka", (0.0, 0.38, 0.12), (0.06, 0.2, 0.06), "drewno", "matowy", rot=(50, 0, 0), faza=0.0)
        p.blok("Listek", (0.0, 0.47, 0.22), (0.1, 0.04, 0.14), "mech", "matowy", rot=(20, 0, 0), faza=0.0)
        # hak: odcinek w bok (od ciała, −X) i krótki zawijas w dół
        p.blok("Hak", (-0.15, 1.1, 0.0), (0.15, 0.36, 0.15), "drewno", "matowy", rot=(0, 0, 50), faza=0.03)
        p.blok("Hak zawijas", (-0.33, 1.12, 0.0), (0.13, 0.22, 0.13), "drewno_ciemne", "matowy", rot=(0, 0, 160),
               faza=0.02)
        p.kula("Bulwa", BULWA, 0.26, "zarodnik", "swiecacy", segm=8)
        p.blok("Bulwa ogonek", (BULWA[0], BULWA[1] + 0.14, 0.0), (0.05, 0.08, 0.05), "drewno_ciemne", "matowy",
               faza=0.0)
        # korzonki u dołu (dotykają ziemi, nie wchodzą w nią)
        for i, (rx, rz) in enumerate(((0, 40), (0, -40), (40, 0))):
            with p.uklad(pos=(0, -0.66, 0), obrot=(rx, 0, rz)):
                p.ostroslup("Korzonek %d" % i, (0, -0.07, 0), (0.08, 0.14, 0.08), "drewno_ciemne", "matowy",
                            rot=(180, 0, 0), gora=(0.0, 0.0))


def _zarodnik(p, nazwa, r):
    """Zarodnik: świecący romb (sześcian postawiony na rogu) z małym jaśniejszym środkiem."""
    p.blok(nazwa, (0, 0, 0), (r, r, r), "zarodnik", "swiecacy", rot=(45, 0, 35), faza=r * 0.15)


def _zarodniki(p):
    for i, (_, r) in enumerate(ZARODNIKI):
        with p.na("Zarodnik%d" % i):
            _zarodnik(p, "Zarodnik %d" % i, r)
    for i, (_, r) in enumerate(ZARODKI_L):
        with p.na("ZarodekL%d" % i):
            _zarodnik(p, "Zarodek laski %d" % i, r)


# ---------------------------------------------------------------------------------------------------- animacje
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
SPORY = tuple("Zarodnik%d" % i for i in range(len(ZARODNIKI))) + tuple("ZarodekL%d" % i for i in range(len(ZARODKI_L)))
POZA_CIALEM = ("Root", "Laska", "Kapelusz") + SPORY      # kości pomijane przy dociąganiu ciała do ziemi


def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _T(R):
    return tuple(tuple(R[j][i] for j in range(3)) for i in range(3))


def _fk(p, poza):
    """Kinematyka wprost pozy {kość: {"obrot": …, "przes": …}}: {kość: (obrót w świecie, staw w świecie)}."""
    W = {}
    for n, k in p.kosci.items():
        v = poza.get(n, {})
        Rl = macierz_obrotu(*v.get("obrot", (0, 0, 0)))
        pr = v.get("przes", (0, 0, 0))
        if k["rodzic"] is None:
            W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
        else:
            Rp, tp = W[k["rodzic"]]
            st = p.kosci[k["rodzic"]]["staw"]
            d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
            W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))
    return W


def _punkty(c):
    """Punkty bryły w układzie jej kości (narożniki, środki krawędzi i ścian skrzynki; kula — na powierzchni)."""
    Rc = macierz_obrotu(*c["r"])
    h = [v / 2 for v in c["s"]]
    out = []
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            for e in (-1, 0, 1):
                n = math.sqrt(a * a + b * b + e * e) if (c["k"] == "kula" and (a or b or e)) else 1.0
                lok = razy_wektor(Rc, (a * h[0] / n, b * h[1] / n, e * h[2] / n))
                out.append(tuple(c["p"][i] + lok[i] for i in range(3)))
    return out


def _najnizej(p, W, kosci):
    mn = 1e9
    for c in p.czesci:
        if c["kosc"] not in kosci:
            continue
        R, t = W[c["kosc"]]
        for q in _punkty(c):
            mn = min(mn, razy_wektor(R, q)[1] + t[1])
    return mn


def _obrot_miedzy(a, b):
    """(rx, ry, rz) najkrótszego obrotu, który przenosi kierunek a na kierunek b."""
    a, b = _norm(a), _norm(b)
    os_ = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    s, c = math.sqrt(sum(x * x for x in os_)), sum(a[i] * b[i] for i in range(3))
    if s < 1e-9:
        return (0.0, 0.0, 0.0)
    x, y, z = (v / s for v in os_)
    kat = math.atan2(s, c)
    cs, sn, t = math.cos(kat), math.sin(kat), 1 - math.cos(kat)
    Q = ((t * x * x + cs, t * x * y - sn * z, t * x * z + sn * y),
         (t * x * y + sn * z, t * y * y + cs, t * y * z - sn * x),
         (t * x * z - sn * y, t * y * z + sn * x, t * z * z + cs))
    return tuple(katy_z_macierzy(Q))


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku przez ±180°)."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        d = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or d < najl[0] - 1e-6:
            najl = (d, c)
    return najl[1]


def _pelna(surowa):
    pz = {}
    for n, v in surowa.items():
        if n.startswith("_"):
            continue
        if isinstance(v, dict):
            pz[n] = {"obrot": tuple(v.get("obrot", (0, 0, 0))), "przes": tuple(v.get("przes", (0, 0, 0)))}
        else:
            pz[n] = {"obrot": tuple(v), "przes": (0.0, 0.0, 0.0)}
    for n in ("Biodra", "StopaL", "StopaP", "Laska"):
        pz.setdefault(n, {"obrot": (0.0, 0.0, 0.0), "przes": (0.0, 0.0, 0.0)})
    return pz


def _plaskie_stopy(p, pz):
    W = _fk(p, pz)
    for s in ("L", "P"):
        pz["Stopa" + s]["obrot"] = tuple(katy_z_macierzy(_T(W["Noga" + s][0])))


def _uziem(p, pz, tryb, h=0.0):
    """tryb True: stopy płasko, najniższy punkt stóp na wysokości h (h > 0 = podskok); "cialo": najniższy punkt
    ciała na ziemi (siad, leżenie); "nad": ciało tylko wypchnięte nad ziemię (przejścia)."""
    if tryb is True:
        _plaskie_stopy(p, pz)
        dno = _najnizej(p, _fk(p, pz), ("StopaL", "StopaP")) - h
    else:
        kosci = tuple(n for n in p.kosci if n not in POZA_CIALEM)
        dno = _najnizej(p, _fk(p, pz), kosci)
        if tryb == "nad":
            dno = min(0.0, dno)
    x, y, z = pz["Biodra"]["przes"]
    pz["Biodra"]["przes"] = (x, y - dno, z)


def _laska_kier(p, pz, u):
    """Laska (oś +Y) celuje w kierunek u (osie modelu)."""
    Rh = _fk(p, pz)["DlonP"][0]
    pz["Laska"]["obrot"] = _obrot_miedzy((0, 1, 0), razy_wektor(_T(Rh), u))


def _laska_przes(pz, s):
    """Przesunięcie laski w dłoni wzdłuż jej osi o s (s > 0: chwyt bliżej dolnego końca)."""
    pz["Laska"]["przes"] = razy_wektor(macierz_obrotu(*pz["Laska"]["obrot"]), (0, s, 0))


def _poza(p, surowa, ziemia=True, h=0.0, laska=None, s=0.0):
    """Poza kluczowa: surowa = {kość: (rx, ry, rz) albo {"obrot", "przes"}}; ziemia jak w _uziem;
    laska = kierunek osi laski (osie modelu) albo ("ziemia", kierunek) — wtedy laska stoi dolnym końcem na ziemi
    (przesunięcie w dłoni liczone samo); s = przesunięcie laski w dłoni."""
    pz = _pelna(surowa)
    _uziem(p, pz, ziemia, h)
    if laska is not None:
        if laska[0] == "ziemia":
            u = _norm(laska[1])
            _laska_kier(p, pz, u)
            grip = _fk(p, pz)["Laska"][1]
            s = L_DOL + 0.04 - grip[1] / u[1]       # 0,04 zapasu: narożniki dolnego klocka laski
        else:
            _laska_kier(p, pz, laska)
    _laska_przes(pz, s)
    pz["_z"], pz["_h"], pz["_s"] = ziemia, h, s
    pz["_u"] = _norm(razy_wektor(_fk(p, pz)["Laska"][0], (0, 1, 0)))       # kierunek laski w świecie
    return pz


def _slerp(a, b, t):
    c = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(3))))
    kat = math.acos(c)
    if kat < 1e-4:
        return a
    sa, sb = math.sin((1 - t) * kat) / math.sin(kat), math.sin(t * kat) / math.sin(kat)
    return _norm(tuple(sa * a[i] + sb * b[i] for i in range(3)))


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


def _sekwencja(k, czasy, pozy, wyg=None, domyslnie="s", po=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza; {} = spoczynek).
    wyg = {numer odcinka: "s" | "l" | "cr"}: s = łagodne wejście i wyjście, l = jednostajnie (uderzenie),
    cr = płynnie przez pozę (Catmull-Rom; w pętli zawija się). po(f, pz) — dopiski w klatce (zarodniki, kapelusz)."""
    p = k.postac
    pozy = [pz if "_z" in pz else _poza(p, pz) for pz in pozy]
    n_poz = len(pozy)
    kosci = sorted({n for pz in pozy for n in pz if not n.startswith("_")} | {"Biodra", "StopaL", "StopaP", "Laska"},
                   key=lambda n: list(p.kosci).index(n))
    ob, pr, poprz = [], [], {}
    for pz in pozy:
        d, e = {}, {}
        for n in kosci:
            v = pz.get(n, {"obrot": (0, 0, 0), "przes": (0, 0, 0)})
            d[n] = _ciaglosc(v["obrot"], poprz.get(n))
            poprz[n] = d[n]
            e[n] = v["przes"]
        ob.append(d)
        pr.append(e)
    petla = k.petla

    def sasiad(i):
        if petla:
            # pozy[0] == pozy[-1] w pętli: sąsiad przed pierwszą to przedostatnia
            if i < 0:
                return i + n_poz - 1
            if i > n_poz - 1:
                return i - n_poz + 1
            return i
        return max(0, min(n_poz - 1, i))

    def wart(tab, i, n, j, t, tryb):
        if tryb == "cr":
            a, b, c, d = (tab[sasiad(i - 1)][n][j], tab[i][n][j], tab[i + 1][n][j], tab[sasiad(i + 2)][n][j])
            if tab is ob:      # kąty sąsiadów zza szwu pętli mogą być zapisane inaczej (±360)
                a = b + ((a - b + 180.0) % 360.0 - 180.0)
                d = c + ((d - c + 180.0) % 360.0 - 180.0)
            return _cr(a, b, c, d, t)
        e = t if tryb == "l" else t * t * (3 - 2 * t)
        return tab[i][n][j] + (tab[i + 1][n][j] - tab[i][n][j]) * e

    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(n_poz - 1) if czasy[j] <= f) if f < czasy[-1] else n_poz - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        tryb = (wyg or {}).get(i, domyslnie)
        pz = {n: {"obrot": tuple(wart(ob, i, n, j, t, tryb) for j in range(3)),
                  "przes": tuple(wart(pr, i, n, j, t, tryb) for j in range(3))} for n in kosci}
        e = t if tryb == "l" else (t if tryb == "cr" else t * t * (3 - 2 * t))
        s = pozy[i]["_s"] + (pozy[i + 1]["_s"] - pozy[i]["_s"]) * e
        h = pozy[i]["_h"] + (pozy[i + 1]["_h"] - pozy[i]["_h"]) * e
        z0, z1 = pozy[i]["_z"], pozy[i + 1]["_z"]
        _uziem(p, pz, True if (z0 is True and z1 is True) else "nad", h)
        # laska idzie po łuku między kierunkami z póz (w świecie), a nie po kątach — nie przechodzi przez ciało
        _laska_kier(p, pz, _slerp(pozy[i]["_u"], pozy[i + 1]["_u"], e))
        _laska_przes(pz, s)
        if po:
            po(f, pz)
        for n, v in pz.items():
            if n == "Root":
                continue
            k.klucz(f, n, obrot=tuple(round(x, 2) for x in v["obrot"]),
                    przes=tuple(round(x, 4) for x in v["przes"]), wyg="liniowo")
    return k


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def _krazenie(k, amp=1.0, czestosc=1):
    """Zarodniki laski krążą wokół bulwy (cykl przesunięć, każdy w innej fazie)."""
    for i in range(len(ZARODKI_L)):
        n = "ZarodekL%d" % i
        k.cykl(n, "przes", (0.07 * amp, 0.06 * amp, 0.0), faza=i / 3.0, czestosc=czestosc)
        k.cykl(n, "przes", (0.0, 0.0, 0.07 * amp), faza=i / 3.0 + 0.25, czestosc=czestosc)
        k.cykl(n, "obrot", (0.0, 40.0, 0.0), faza=i / 3.0, czestosc=czestosc)


def idle(p, dl=72):
    """Spoczynek (2,4 s): oddech, rozgląda się z ukosa, kapelusz kołysze się z opóźnieniem, broda faluje, lewa
    dłoń zaciera się przy brzuchu (złośliwie), jedno mrugnięcie; zarodniki krążą wokół bulwy laski."""
    k = p.klip("idle", dl, petla=True)
    k.cykl("Tulow", "obrot", (2.5, 0, 0), faza=0.0)
    k.cykl("Glowa", "obrot", (0, 14, 0), faza=0.1)
    k.cykl("Glowa", "obrot", (-2, 0, 3), czestosc=2, faza=0.3)
    k.cykl("Kapelusz", "obrot", (2.5, 0, -3), czestosc=2, faza=0.45)
    k.cykl("Broda", "obrot", (4, 0, 3), czestosc=2, faza=0.5)
    k.cykl("RamieL", "obrot", (5, 0, 3), faza=0.2, srodek=(-22, 0, 14))
    k.cykl("DlonL", "obrot", (0, 0, 6), czestosc=4, srodek=(-22, 0, -4))
    # laska trzymana trochę przed sobą (widać ją w kadrze 3/4), pionowo: obrót laski znosi obrót ramienia
    k.cykl("RamieP", "obrot", (-1.5, 0, 0), faza=0.0, srodek=(-20, 0, -6))
    k.cykl("Laska", "obrot", (1.5, 0, 0), faza=0.0, srodek=(20, 0, 6))
    for kl, v in ((0, (0, 0, 0)), (44, (0, 0, 0)), (46, ZAMKNIETE), (49, (0, 0, 0)), (dl, (0, 0, 0))):
        k.klucz(kl, "Powieki", przes=v)
    _krazenie(k)
    return k


def ruch(p, dl=24):
    """Drobny, kołyszący chód (0,8 s na dwa kroki): krótkie nóżki machają, biodra kiwają się na boki, kapelusz
    podskakuje z opóźnieniem, laska idzie jak kij wędrowca, lewa ręka macha."""
    k = p.klip("ruch", dl, petla=True)
    for f in range(dl + 1):
        t = f / float(dl)
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        raw = {"Biodra": {"obrot": (0, 9 * a, 7 * c), "przes": (0.05 * c, 0, 0)},
               "NogaL": (-30 * a, 0, 0), "NogaP": (30 * a, 0, 0),
               "Tulow": (7 + 2 * math.sin(4 * math.pi * t), -6 * a, -4 * c),
               "Glowa": (-3, -3 * a, -3 * c),
               "Kapelusz": (4 * math.sin(4 * math.pi * t - 1.2), 0, 5 * math.cos(2 * math.pi * t - 1.0)),
               "Broda": (8 * math.sin(4 * math.pi * t - 1.0), 0, 0),
               "RamieL": (28 * a, 0, 10), "DlonL": (-15 + 10 * a, 0, 0),
               "RamieP": (-14 - 18 * a, 0, -6)}
        pz = _pelna(raw)
        _uziem(p, pz, True, 0.05 * abs(math.sin(2 * math.pi * t)))
        _laska_kier(p, pz, _norm((-0.08, 1.0, 0.28 * a + 0.1)))
        _laska_przes(pz, 0.0)
        for n, v in pz.items():
            k.klucz(f, n, obrot=tuple(round(x, 2) for x in v["obrot"]), przes=tuple(round(x, 4) for x in v["przes"]),
                    wyg="liniowo")
    _krazenie(k, czestosc=2, amp=1.3)
    return k


def atak(p, dl=27):
    """Zwykły cios (0,9 s): laska wzniesiona w prawo i w górę, z chwytem przy dolnym końcu (kl. 6), naciąg — odchyla
    się w tył, kapelusz przechyla się do tyłu, laska wysunięta w bok poza rondo (kl. 6–9) — i „rąbnięcie” z góry
    przed siebie z wypadem lewą nogą, kapelusz leci do przodu: trafienie w kl. 12 ok. 2 studów przed nim
    na wysokości kolan gracza, dobicie w dół, powrót. Pionowy łuk czyta się z każdej strony."""
    k = p.klip("atak", dl, petla=False)
    zamach = _poza(p, {"Biodra": (0, -14, 0), "Tulow": (-10, -14, 0), "Glowa": (-6, 14, 0), "Kapelusz": (-6, 0, -6),
                       "RamieP": (-30, 0, -95), "DlonP": (-25, 0, 0), "RamieL": (-20, 0, 40), "DlonL": (-20, 0, 0),
                       "NogaL": (-8, 0, 0), "NogaP": (8, 0, 0), "Powieki": {"przes": PRZYMRUZ}, "Broda": (-8, 0, 6)},
                   laska=(-0.55, 0.82, -0.12), s=0.55)
    # naciąg: chwila zawahania na szczycie zamachu — odchyla się w tył, kapelusz przechyla się do tyłu i odsłania
    # złośliwą minę, laska jeszcze trochę dalej w tył (wyraźne „wzięcie” przed ciosem)
    naciag = _poza(p, {"Biodra": (0, -18, 0), "Tulow": (-18, -18, 0), "Glowa": (-12, 16, 0),
                       "Kapelusz": (-14, 0, -8), "RamieP": (-34, 0, -98), "DlonP": (-28, 0, 0), "RamieL": (-24, 0, 46),
                       "DlonL": (-24, 0, 0), "NogaL": (-10, 0, 0), "NogaP": (10, 0, 0), "Powieki": {"przes": PRZYMRUZ},
                       "Broda": (-12, 0, 8)},
                   laska=(-0.68, 0.7, -0.22), s=0.55)
    trafia = _poza(p, {"Biodra": {"obrot": (0, 12, 0), "przes": (0, 0, 0.15)}, "Tulow": (16, 10, 0),
                       "Glowa": (6, -8, 4), "Kapelusz": (14, 0, 8), "Broda": (-14, 0, 0),
                       "RamieP": (-70, 0, -25), "DlonP": (-10, 0, 0), "RamieL": (25, 0, 35), "DlonL": (-10, 0, 0),
                       "NogaL": (-30, 0, 0), "NogaP": (18, 0, 0), "Powieki": {"przes": PRZYMRUZ}},
                   laska=(0.0, -0.2, 0.98), s=0.55)
    dobicie = _poza(p, {"Biodra": {"obrot": (0, 14, 0), "przes": (0, 0, 0.17)}, "Tulow": (20, 12, 0),
                        "Glowa": (6, -18, 0), "Kapelusz": (4, 0, 10), "Broda": (-6, 0, 0),
                        "RamieP": (-62, 0, -22), "DlonP": (-10, 0, 0), "RamieL": (28, 0, 38), "NogaL": (-30, 0, 0),
                        "NogaP": (18, 0, 0), "Powieki": {"przes": PRZYMRUZ}},
                    laska=(0.1, -0.42, 0.9), s=0.55)
    wraca = _poza(p, {"Biodra": (0, 6, 0), "Tulow": (6, 6, 0), "Glowa": (0, -8, 0), "Kapelusz": (-3, 0, 2),
                      "RamieP": (-25, 0, -10), "RamieL": (5, 0, 12), "NogaL": (-8, 0, 0), "NogaP": (5, 0, 0)},
                  laska=(-0.05, 1.0, 0.25), s=0.1)
    _sekwencja(k, (0, 6, 9, 12, 15, 21, dl), ({}, zamach, naciag, trafia, dobicie, wraca, {}), wyg={2: "l"})
    return k


def _spory_lot(fr, fs, fz, cele):
    """Tor zarodników kapelusza (świat): start w kl. fr (gdzie akurat są w kapeluszu), szczyt w fs, lądowanie
    w kl. cele[i][3], wsiąkanie do kl. fz. cele = [(x, z, wysokość szczytu, klatka lądowania)] — x, z = miejsce
    lądowania względem środka kapelusza w chwili wylotu (postać jest wtedy pochylona do przodu). Najpierw
    wystrzał pionowo ponad kapelusz, potem łuk na zewnątrz: szczyt jest już poza rondem, więc opadające
    zarodniki nie przelatują przez kapelusz ani przez ciało."""
    start = {}

    def tor(i, f, poz, kap):
        if f <= fr:
            start[i] = (poz, kap)
            return None
        (sx, sy, sz), (kx, _, kz) = start[i]
        gx, gz, hs, fl = cele[i]
        gx, gz = gx + kx, gz + kz
        px, pz = kx + (gx - kx) * 0.92, kz + (gz - kz) * 0.92        # szczyt: prawie nad miejscem lądowania
        r = ZARODNIKI[i][1] * 0.72          # półprzekątna rombu: najniższy róg na ziemi
        if f <= fs:
            t = (f - fr) / float(fs - fr)
            ey = 1 - (1 - t) ** 2           # w górę: szybko, potem zwalnia
            eh = t ** 1.6                   # na boki: dopiero gdy jest już nad kapeluszem
            return (sx + (px - sx) * eh, sy + (hs - sy) * ey, sz + (pz - sz) * eh)
        if f <= fl:
            t = (f - fs) / float(fl - fs)
            e = t * t                        # opadanie: powoli, potem szybciej
            ko = 0.08 * math.sin(t * math.pi * 3 + i) * (1 - t)      # lekkie kołysanie w locie
            return (px + (gx - px) * t + ko, hs + (r - hs) * e, pz + (gz - pz) * t - ko)
        t = min(1.0, max(0.0, (f - fl - 3) / float(fz - fl - 3)))    # chwilę leżą, potem wsiąkają
        return (gx, r - (r + 0.3) * t * t, gz)
    return tor


def umiejetnosc(p, dl=60):
    """Chmura zarodników (2 s): laska w bok i w górę (kl. 10–16), uderzenie laską w ziemię przed sobą (kl. 20),
    potrząsanie kapeluszem z zamkniętymi oczami (kl. 20–40) — dziesięć świecących zarodników wylatuje z kapelusza
    (kl. 22), wznosi się do ok. 4–4,3 studa (kl. 31), rozsypuje półkolem przed nim i opada na ziemię ok. 2 studów
    od niego (kl. 45–49),
    a potem wsiąka (kl. 56). Zarodniki laski rozbiegają się i wracają. Na koniec prostuje się z uśmieszkiem."""
    k = p.klip("umiejetnosc", dl, petla=False)
    gora_kier = (-0.55, 0.82, 0.15)
    zamach = _poza(p, {"Biodra": (0, -10, 0), "Tulow": (-8, -12, 0), "Glowa": (-8, 12, 0), "Kapelusz": (-5, 0, 5),
                       "RamieP": (-30, 0, -58), "DlonP": (-15, 0, 0), "RamieL": (-30, 0, 55), "DlonL": (-20, 0, 0),
                       "NogaL": (-6, 0, 6), "NogaP": (6, 0, -6), "Powieki": {"przes": PRZYMRUZ}},
                   laska=gora_kier, s=0.25)
    szczyt = _poza(p, {"Biodra": (0, -14, 0), "Tulow": (-12, -16, 0), "Glowa": (-12, 14, 0), "Kapelusz": (-8, 0, 7),
                       "RamieP": (-45, 0, -70), "DlonP": (-20, 0, 0), "RamieL": (-45, 0, 70), "DlonL": (-25, 0, 0),
                       "NogaL": (-8, 0, 8), "NogaP": (8, 0, -8), "Powieki": {"przes": PRZYMRUZ}, "Broda": (-10, 0, 0)},
                   laska=(-0.62, 0.76, 0.2), s=0.1)
    uderz = {"Biodra": {"obrot": (6, 4, 0), "przes": (0, 0, 0.08)}, "Tulow": (16, 4, 0), "Glowa": (12, -4, 0),
             "Kapelusz": (10, 0, 0), "RamieP": (-42, 0, -16), "DlonP": (-10, 0, 0), "RamieL": (-10, 0, 40),
             "NogaL": (-14, 0, 8), "NogaP": (8, 0, -8), "Broda": (10, 0, 0), "Powieki": {"przes": ZAMKNIETE}}
    pionowo = ("ziemia", (-0.1, 1.0, 0.12))
    pozy, czasy = [{}, zamach, szczyt, _poza(p, uderz, laska=pionowo)], [0, 10, 16, 20]
    # potrząsanie kapeluszem: na przemian w lewo i w prawo, kapelusz podskakuje na głowie
    for j, f in enumerate((23, 26, 29, 32, 35, 38)):
        zn = 1 if j % 2 == 0 else -1
        sila = 1.0 - 0.1 * j
        pz = dict(uderz, Glowa=(8, zn * 6 * sila, zn * 9 * sila),
                  Kapelusz={"obrot": (-4, zn * 14 * sila, -zn * 14 * sila), "przes": (0, 0.1 * sila, 0)},
                  Tulow=(14, 4, -zn * 4 * sila), Broda=(4, 0, -zn * 10), RamieL=(-25, 0, 50 + zn * 20))
        pozy.append(_poza(p, pz, laska=pionowo))
        czasy.append(f)
    spokoj = dict(uderz, Glowa=(4, 0, 0), Kapelusz=(0, 0, 0), Tulow=(10, 0, 0), Powieki={"przes": PRZYMRUZ},
                  RamieL=(-10, 0, 25))
    pozy.append(_poza(p, spokoj, laska=pionowo))
    czasy.append(42)
    wstaje = _poza(p, {"Tulow": (-4, 0, 0), "Glowa": (-8, -10, 4), "RamieP": (-20, 0, -8), "RamieL": (-30, 0, 15),
                       "DlonL": (-40, 0, -10), "Kapelusz": (-3, 0, -3), "Powieki": {"przes": PRZYMRUZ}},
                   laska=(-0.05, 1.0, 0.18), s=0.0)
    pozy += [wstaje, {}]
    czasy += [52, dl]

    # zarodniki: 8 z kapelusza lecą wachlarzem przed nim; 3 z laski odskakują i wracają
    cele = []
    for i in range(len(ZARODNIKI)):
        a = math.radians(-100 + 200 * i / (len(ZARODNIKI) - 1))
        r = 1.7 + 0.3 * ((i * 5) % 3) / 2.0
        cele.append((r * math.sin(a), r * math.cos(a), 3.95 + 0.3 * ((i * 3) % 4) / 3.0, 45 + (i * 3) % 5))
    tor = _spory_lot(22, 31, 57, cele)

    def po(f, pz):
        W = _fk(p, pz)
        Rc, tc = W["Kapelusz"]
        for i in range(len(ZARODNIKI)):
            n = "Zarodnik%d" % i
            st = p.kosci[n]["staw"]
            spocz = tuple(st[j] - KAP[j] for j in range(3))
            poz = tuple(tc[j] + razy_wektor(Rc, spocz)[j] for j in range(3))
            cel = tor(i, f, poz, tc)
            if cel is None:
                pz[n] = {"obrot": (0, 0, 0), "przes": (0, 0, 0)}
                continue
            lok = razy_wektor(_T(Rc), tuple(cel[j] - tc[j] for j in range(3)))
            pz[n] = {"obrot": (0, (f - 22) * 14.0 * (1 if i % 2 else -1), (f - 22) * 9.0),
                     "przes": tuple(lok[j] - spocz[j] for j in range(3))}
        for i in range(len(ZARODKI_L)):
            n = "ZarodekL%d" % i
            if 20 <= f <= 50:
                t = (f - 20) / 30.0
                e = math.sin(math.pi * t) * (1 - 0.3 * t)
                kier = ((-0.7, 0.3, 0.5), (-0.7, 0.1, -0.4), (-0.3, -0.2, 0.7))[i]
                pz[n] = {"obrot": (0, f * 20.0, 0), "przes": tuple(0.75 * e * c for c in kier)}
            else:
                pz[n] = {"obrot": (0, 0, 0), "przes": (0, 0, 0)}

    _sekwencja(k, czasy, pozy, wyg={2: "l"}, po=po)
    return k


def trafienie(p, dl=18):
    """Reakcja na cios (0,6 s): szarpnięcie w tył (kl. 4) — tułów i głowa odskakują, kapelusz podskakuje i
    przekrzywia się do przodu, ręce odlatują, oczy zaciśnięte; cofnięcie i powrót."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = _poza(p, {"Biodra": {"obrot": (-8, 6, 0), "przes": (0, 0, -0.3)}, "Tulow": (-14, 6, 4),
                      "Glowa": (-16, -10, 6), "Kapelusz": {"obrot": (14, 0, 10), "przes": (0, 0.14, 0.05)},
                      "Broda": (-25, 0, 0), "RamieL": (-30, 0, 45), "DlonL": (-25, 0, 0), "RamieP": (-25, 0, -32),
                      "NogaL": (-16, 0, 0), "NogaP": (-6, 0, 0), "Powieki": {"przes": ZAMKNIETE}},
                  laska=(-0.35, 0.9, -0.25), s=0.0)
    wraca = _poza(p, {"Biodra": {"obrot": (-3, 2, 0), "przes": (0, 0, -0.15)}, "Tulow": (-5, 2, 1),
                      "Glowa": (-4, -4, 2), "Kapelusz": {"obrot": (-6, 0, -4), "przes": (0, -0.0, 0)},
                      "Broda": (8, 0, 0), "RamieL": (-8, 0, 15), "RamieP": (-8, 0, -10), "NogaL": (-5, 0, 0),
                      "Powieki": {"przes": PRZYMRUZ}},
                  laska=(-0.12, 1.0, 0.0), s=0.0)
    _sekwencja(k, (0, 4, 10, dl), ({}, szarp, wraca, {}))
    return k


def unik(p, dl=27):
    """Unik (0,9 s): podskok w lewo (+X) z przechyłem w bok i podkulonymi nóżkami, lądowanie ok. 1,5 studa obok,
    chwila w bok i podskok z powrotem na linię ciosu. Kapelusz zostaje w tyle za ruchem."""
    k = p.klip("unik", dl, petla=False)
    lot = _poza(p, {"Biodra": {"obrot": (0, 8, -14), "przes": (0.8, 0, -0.1)}, "Tulow": (4, 0, -8),
                    "Glowa": (0, -12, 10), "Kapelusz": (0, 0, 14), "NogaL": (-25, 0, 18), "NogaP": (-15, 0, 10),
                    "RamieL": (-20, 0, 50), "RamieP": (-15, 0, -40), "Broda": (0, 0, 15)},
                ziemia=True, h=0.4, laska=(-0.32, 0.94, 0.05), s=0.3)
    laduje = _poza(p, {"Biodra": {"obrot": (0, 6, -8), "przes": (1.5, 0, -0.15)}, "Tulow": (8, 0, -6),
                       "Glowa": (2, -14, 6), "Kapelusz": (4, 0, -8), "NogaL": (-8, 0, 14), "NogaP": (6, 0, -6),
                       "RamieL": (-15, 0, 30), "RamieP": (-10, 0, -20), "Broda": (0, 0, -8)},
                   laska=(-0.25, 1.0, 0.05))
    stoi = _poza(p, {"Biodra": {"obrot": (0, 4, -5), "przes": (1.45, 0, -0.12)}, "Tulow": (4, 0, -4),
                     "Glowa": (0, -16, 4), "Kapelusz": (0, 0, 3), "NogaL": (-4, 0, 10), "NogaP": (4, 0, -4),
                     "RamieL": (-10, 0, 20), "RamieP": (-8, 0, -14), "Powieki": {"przes": PRZYMRUZ}},
                 laska=(-0.2, 1.0, 0.05))
    powrot = _poza(p, {"Biodra": {"obrot": (0, -6, 10), "przes": (0.7, 0, -0.05)}, "Tulow": (2, 0, 6),
                       "Glowa": (0, -6, -8), "Kapelusz": (0, 0, -10), "NogaL": (-15, 0, 6), "NogaP": (-20, 0, -10),
                       "RamieL": (-10, 0, 30), "RamieP": (-15, 0, -30)},
                   ziemia=True, h=0.3, laska=(-0.4, 0.9, 0.05))
    _sekwencja(k, (0, 6, 11, 16, 21, dl), ({}, lot, laduje, stoi, powrot, {}), domyslnie="cr")
    return k


def _skrzynka(c, R, t):
    """Skrzynka bryły c w świecie (kość o obrocie R i stawie t): (macierz świat->bryła, środek, połówki, promień)."""
    Rc = mnoz(R, macierz_obrotu(*c["r"]))
    sr = tuple(razy_wektor(R, c["p"])[i] + t[i] for i in range(3))
    pol = tuple(v / 2 for v in c["s"])
    return (_T(Rc), sr, pol, math.sqrt(sum(v * v for v in pol)))


def _w(sk, q):
    M, sr, pol, r = sk
    d = (q[0] - sr[0], q[1] - sr[1], q[2] - sr[2])
    if abs(d[0]) > r or abs(d[1]) > r or abs(d[2]) > r:
        return False
    return all(abs(M[i][0] * d[0] + M[i][1] * d[1] + M[i][2] * d[2]) < pol[i] for i in range(3))


def _oparcie(p, W, Rk, x, z):
    """Wysokość stawu kapelusza (obrót Rk, środek w x, z), przy której kapelusz leży na ciele w pozie W:
    opuszczany od góry, aż spód (blaszki, rondo, kopuła) dotknie ciała albo ziemi."""
    kap = [c for c in p.czesci if c["kosc"] == "Kapelusz" and c["n"].split()[0] in ("Blaszki", "Rondo", "Kopula")]
    cialo = [c for c in p.czesci if c["kosc"] not in POZA_CIALEM]
    sk_c = [_skrzynka(c, *W[c["kosc"]]) for c in cialo]
    pk = [razy_wektor(Rk, q) for c in kap for q in _punkty(c)]
    pc = [tuple(razy_wektor(W[c["kosc"]][0], q)[i] + W[c["kosc"]][1][i] for i in range(3))
          for c in cialo for q in _punkty(c)]
    dno = min(q[1] for q in pk)

    def styk(y):
        if y + dno < 0:
            return True
        sk_k = [_skrzynka(c, Rk, (x, y, z)) for c in kap]
        for q0 in pk:
            q = (q0[0] + x, q0[1] + y, q0[2] + z)
            if any(_w(sk, q) for sk in sk_c):
                return True
        return any(_w(sk, q) for q in pc for sk in sk_k)
    y = 3.0
    for krok in (0.1, 0.02):
        while not styk(y - krok):
            y -= krok
    return round(y, 3)


UPADEK_OBR = -60.0      # obrót wokół pionu przy siadzie w upadku: leży bokiem (nóżki w stronę −X, głowa ku +X)
PRZECHYL_KAP = 45.0     # przechył kapelusza leżącego na twarzy (stopnie, brzeg w dół w stronę przechyłu)
PRZES_KAP = 0.45        # środek kapelusza przesunięty od środka głowy w stronę przechyłu (studs)


def _ry(v, kat):
    """Wektor v obrócony o kat (stopnie) wokół pionu, jak obrót ry kości."""
    return razy_wektor(macierz_obrotu(0.0, kat, 0.0), v)


def upadek(p, dl=60):
    """Pokonanie (2 s): zawroty głowy — chwieje się na boki, a kapelusz kręci się na głowie jak bączek (kl. 0–28),
    klapnięcie na pupę z nóżkami do przodu (kl. 32), przewrót na plecy (kl. 42) — kapelusz spada z głowy, wylatuje
    w górę i opada mu na twarz (kl. 49), podskakuje i zastyga. Oczy zamknięte. Ostatnia klatka: leży na plecach,
    z kapeluszem na twarzy, laska obok."""
    k = p.klip("upadek", dl, petla=False)
    w1 = _poza(p, {"Biodra": {"obrot": (-6, 0, 7), "przes": (0, 0, -0.15)}, "Tulow": (-6, 0, 6),
                   "Glowa": (-8, 14, 10), "Kapelusz": (4, 90, 8), "RamieL": (-30, 0, 45), "RamieP": (-20, 0, -38),
                   "NogaL": (-6, 0, 4), "NogaP": (4, 0, -4), "Powieki": {"przes": PRZYMRUZ}, "Broda": (0, 0, 10)},
               laska=(-0.58, 0.79, 0.15), s=0.0)
    w2 = _poza(p, {"Biodra": {"obrot": (-4, 0, -8), "przes": (0, 0, -0.2)}, "Tulow": (-4, 0, -6),
                   "Glowa": (-6, -14, -12), "Kapelusz": (-4, 200, -8), "RamieL": (-20, 0, 30),
                   "RamieP": (-30, 0, -50), "NogaL": (-4, 0, 6), "NogaP": (8, 0, -2), "Powieki": {"przes": PRZYMRUZ},
                   "Broda": (0, 0, -10)},
               laska=(-0.65, 0.72, 0.2), s=0.25)
    w3 = _poza(p, {"Biodra": {"obrot": (-8, 0, 6), "przes": (0, 0, -0.25)}, "Tulow": (-6, 0, 5),
                   "Glowa": (-10, 10, 12), "Kapelusz": (4, 300, 6), "RamieL": (-35, 0, 50), "RamieP": (-25, 0, -45),
                   "NogaL": (-8, 0, 2), "NogaP": (2, 0, -6), "Powieki": {"przes": PRZYMRUZ}},
               laska=(-0.5, 0.85, 0.1), s=0.25)
    # siadając, obraca się o UPADEK_OBR wokół pionu (zawroty), więc leży BOKIEM do kamery gry (patrzącej od
    # przodu): widać nóżki w górze, brzuch i kapelusz na twarzy, a nie same podeszwy chodaków
    o = UPADEK_OBR
    siad = _poza(p, {"Biodra": {"obrot": (-30, o, 0), "przes": _ry((0, 0, -0.3), o)}, "Tulow": (18, 0, 0),
                     "Glowa": (8, 0, 0), "Kapelusz": (0, 360, 0), "NogaL": (-62, 0, 12), "NogaP": (-62, 0, -12),
                     "StopaL": (60, 0, 0), "StopaP": (60, 0, 0), "RamieL": (-10, 0, 35), "RamieP": (-10, 0, -35),
                     "Powieki": {"przes": PRZYMRUZ}, "Broda": (10, 0, 0)},
                 ziemia="cialo", laska=_ry((-0.5, 0.75, 0.45), o))
    lezy_raw = {"Biodra": {"obrot": (-90, o, 0), "przes": _ry((0, 0, -0.5), o)}, "Tulow": (0, 0, 0),
                "Glowa": (0, 0, 16),
                "Kapelusz": (0, 360, 0), "NogaL": (-55, 0, 14), "NogaP": (-55, 0, -14), "StopaL": (40, 0, 0),
                "StopaP": (40, 0, 0), "RamieL": (58, 0, 60), "DlonL": (0, 0, 10), "RamieP": (58, 0, -60),
                "DlonP": (0, 0, -10), "Powieki": {"przes": ZAMKNIETE}, "Broda": (-10, 0, 0)}
    na_ziemi = _ry((-0.72, -0.3, 0.62), o)        # laska leży obok niego, ukośnie w bok i ku nogom
    lezy = _poza(p, lezy_raw, ziemia="cialo", laska=na_ziemi, s=0.5)
    odbicie = _poza(p, dict(lezy_raw, Biodra={"obrot": (-84, o, 0), "przes": _ry((0, 0.1, -0.5), o)},
                            NogaL=(-75, 0, 18), NogaP=(-75, 0, -18), RamieL=(20, 0, 55), RamieP=(20, 0, -55)),
                    ziemia="cialo", laska=_ry((-0.75, 0.05, 0.65), o), s=0.5)
    lezy2 = _poza(p, dict(lezy_raw, NogaL=(-42, 0, 16), NogaP=(-42, 0, -16)), ziemia="cialo", laska=na_ziemi,
                  s=0.5)

    # kapelusz spada: od kl. 38 wylatuje w górę po łuku (świat), obraca się i opada mu na twarz (gag „kapelusz na
    # oczy”); podskok i spoczynek. Wysokość spoczynku liczona: kapelusz opuszczany, aż dotknie ciała (nos, broda).
    F_ODP, F_LAD, F_POD = 38, 49, 53
    W2 = _fk(p, lezy2)
    Rg2, tg2 = W2["Glowa"]
    # kapelusz przechylony brzegiem w bok, ku jego lewej stronie (tam patrzy kamera gry i kadr 3/4) i trochę ku
    # czubkowi głowy: opiera się o nos i brodę, kopuła zwrócona do widza, a brzeg schodzi do ziemi — wygląda na
    # zsunięty na twarz, a nie na zawieszony nad leżącym
    czubek = razy_wektor(Rg2, (0.0, 1.0, 0.0))
    bok = razy_wektor(Rg2, (1.0, 0.0, 0.0))
    d = _norm((bok[0] + 0.5 * czubek[0], 0.0, bok[2] + 0.5 * czubek[2]))
    kat = math.radians(PRZECHYL_KAP)
    cel_ob = _obrot_miedzy((0, 1, 0), (math.sin(kat) * d[0], math.cos(kat), math.sin(kat) * d[2]))
    srodek_glowy = razy_wektor(Rg2, (0.0, GLOWA_ROZ[1] / 2, 0.0))
    # środek kapelusza przesunięty w stronę przechyłu: kopuła nakrywa całą głowę, brzeg sięga ziemi
    cx, cz = (tg2[0] + srodek_glowy[0] + PRZES_KAP * d[0], tg2[2] + srodek_glowy[2] + PRZES_KAP * d[2])
    cel = (cx, _oparcie(p, W2, macierz_obrotu(*cel_ob), cx, cz), cz)
    kap = [c for c in p.czesci if c["kosc"] == "Kapelusz"]
    stan = {}

    def po(f, pz):
        if f < F_ODP:
            return
        W = _fk(p, pz)
        Rg, tg = W["Glowa"]
        if f == F_ODP:
            Rk, tk = W["Kapelusz"]
            stan["start"] = (katy_z_macierzy(Rk), tk)
        a0, t0 = stan["start"]
        if f <= F_LAD:
            t = (f - F_ODP) / float(F_LAD - F_ODP)
            ob = tuple(a0[j] + (_ciaglosc(cel_ob, a0)[j] - a0[j]) * t for j in range(3))
            poz = tuple(t0[j] + (cel[j] - t0[j]) * t for j in range(3))
            poz = (poz[0], poz[1] + 1.4 * math.sin(math.pi * t), poz[2])
        elif f <= F_POD:
            t = (f - F_LAD) / float(F_POD - F_LAD)
            ob = (cel_ob[0] - 8 * math.sin(math.pi * t), cel_ob[1], cel_ob[2] + 10 * math.sin(math.pi * t))
            poz = (cel[0], cel[1] + 0.25 * math.sin(math.pi * t), cel[2])
        else:
            ob, poz = cel_ob, cel
        Rw = macierz_obrotu(*ob)
        # dno kapelusza nigdy pod ziemią
        d = min(razy_wektor(Rw, q)[1] for c in kap for q in _punkty(c)) + poz[1]
        if d < 0:
            poz = (poz[0], poz[1] - d, poz[2])
        Rl = mnoz(_T(Rg), Rw)
        st = tuple(KAP[j] - SZYJA[j] for j in range(3))
        lok = razy_wektor(_T(Rg), tuple(poz[j] - tg[j] for j in range(3)))
        pz["Kapelusz"] = {"obrot": tuple(katy_z_macierzy(Rl)), "przes": tuple(lok[j] - st[j] for j in range(3))}

    _sekwencja(k, (0, 8, 16, 24, 32, 42, 47, 52, dl), ({}, w1, w2, w3, siad, lezy, odbicie, lezy2, lezy2),
               wyg={4: "s"}, po=po)
    return k


def wiwat(p, dl=60):
    """Wiwat po wygranej (pętla 2 s): złośliwy śmiech — dwa podskoki, laska wzniesiona w bok (z dala od
    kapelusza), lewa pięść wygraża przed sobą, głowa odchylona, oczy zmrużone od śmiechu, kapelusz podskakuje."""
    k = p.klip("wiwat", dl, petla=True)
    baza = {"Tulow": (-6, 0, 0), "Glowa": (-14, 0, 6), "RamieP": (-15, 0, -92), "DlonP": (0, 0, 10),
            "RamieL": (-70, 0, 35), "DlonL": (-40, 0, 0), "Powieki": {"przes": PRZYMRUZ}, "Broda": (-8, 0, 0)}
    laska_g = (-0.4, 0.9, 0.12)

    def odm(**z):
        d = dict(baza)
        d.update(z)
        return d
    dol = _poza(p, odm(Tulow=(6, 0, 0), Glowa=(-6, 0, -4), Kapelusz={"obrot": (-6, 0, 4), "przes": (0, -0.04, 0)},
                       RamieL=(-55, 0, 38), DlonL=(-60, 0, 0), Broda=(6, 0, 0)), laska=laska_g)
    skok = _poza(p, odm(Biodra=(0, 10, 0), Tulow=(-10, 6, 0), Glowa=(-18, -8, 8),
                        Kapelusz={"obrot": (8, 0, -6), "przes": (0, 0.08, 0)}, NogaL=(-28, 0, 10),
                        NogaP=(22, 0, -8), RamieL=(-85, 0, 42), DlonL=(-20, 0, 0), RamieP=(-15, 0, -100)),
                 ziemia=True, h=0.38, laska=(-0.35, 0.92, 0.15))
    skok2 = _poza(p, odm(Biodra=(0, -10, 0), Tulow=(-10, -6, 0), Glowa=(-18, 8, -6),
                         Kapelusz={"obrot": (8, 0, 6), "przes": (0, 0.08, 0)}, NogaL=(22, 0, 8),
                         NogaP=(-28, 0, -10), RamieL=(-85, 0, 42), DlonL=(-20, 0, 0), RamieP=(-15, 0, -100)),
                  ziemia=True, h=0.38, laska=(-0.35, 0.92, 0.15))
    _sekwencja(k, (0, 10, 20, 30, 40, 50, dl), (dol, skok, dol, _poza(p, odm(Glowa=(-16, 0, -8)), laska=laska_g),
                                                skok2, dol, dol), domyslnie="cr")
    _krazenie(k, czestosc=2, amp=1.4)
    return k
