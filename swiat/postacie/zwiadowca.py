# -*- coding: utf-8 -*-
"""ZWIADOWCA — druga klasa gracza (obok Wojownika-Rycerza i Maga): zwinny leśny zwiadowca z łukiem i sztyletem.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zwiadowca.py --wyj <folder> --klip unik

Opis klasy (tools/walka/dane_walki.json, id „zwiadowca”): styl „unik i krytyk”, umiejętności: uderzenie z góry,
zatruta strzała, skupienie. Wygląd to własny projekt (propozycja, nie kanon).

Bryła: szkielet R15 w tych samych wymiarach klocków co Rycerz (te same zaczepy ekwipunku), ok. 5,8 studa z kapturem.
Sylwetka do rozpoznania z daleka: spiczasty kaptur z końcem odchylonym do tyłu, krótka peleryna z brzegiem ciętym
w liście, kołczan na plecach z pomarańczowymi lotkami nad prawym barkiem, wysoki łuk w lewej dłoni, sztylet w prawej.
Lekki skórzany pancerz z pasem kołczanu na skos, tunika (jej poły siedzą na udach, więc nie przebijają nóg w biegu),
wysokie buty z wywiniętą cholewą. Twarz pogodna i bystra: duże oczy, jedna brew uniesiona, uśmiech z kącikiem
w górę, piegi.

Paleta (6 rodzin + akcent): zieleń lasu (kaptur, peleryna, tunika — dwa odcienie), skóra pancerza (trzy brązy),
drewno łuku, karnacja, tusz (oczy, usta), AKCENT: jasnopomarańczowa chusta i lotki strzał.

Broń: dwa osobne przedmioty, jak miecz Rycerza (w FBX postaci ich nie ma, w renderach i filmach są w dłoniach):
  zwiadowca_luk     — na LeftGripAttachment (uchwyt w (0,0,0), ramiona łuku wzdłuż ±Y, brzuch łuku +Z, cięciwa −Z),
  zwiadowca_sztylet — na RightGripAttachment (rękojeść w (0,0,0), ostrze w +Y, płaz do przodu +Z).

Klipy (30 kl./s; postać patrzy w +Z i w tę stronę atakuje):
  idle (pętla), ruch (lekki bieg, pętla), atak (pchnięcie sztyletem z wypadem), umiejetnosc (zatruta strzała:
  lewym barkiem do celu, łuk wyciągnięty na wysokości barku, naciąg z łokciem w tył, wypuszczenie z odrzutem),
  uderzenie_z_gory (drugi klip umiejętności: wyskok i cios sztyletem z góry), trafienie (szarpnięcie w tył), unik
  (znak klasy: boczne salto w lewo i powrót), upadek (pada na kolana i twarzą w dół, kończy się leżeniem), wiwat
  (pętla: łuk w górę, podskoki).
Klipy są zapisane jako pozy kluczowe (funkcja _sekwencja zamienia je na klucz w każdej klatce): stopy stoją płasko
na ziemi, w powietrzu nic nie schodzi pod ziemię. Zmiany rób w pozach kluczowych w tym pliku, nie w Blenderze.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium, Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "zwiadowca"

PALETA = {
    "lisc": "3F9B4A", "lisc_ciemny": "26633A",                       # kaptur, peleryna, tunika / podszewka, spodnie
    "skorzany": "8A5530", "skorzany_ciemny": "553319", "skorzany_jasny": "C49A62",
    "wlosy": "4A2C17", "piegi": "C7835A",
    "drewno": "A8692E",
    "akcent": "FF9F1C",                                               # chusta, lotki strzał
    "stal": "B9C3D0", "stal_cien": "7F8A9A",
}

# te same klocki co Rycerz (te same zaczepy ekwipunku, ten sam wzrost ciała)
WYMIARY = {"Head": (1.6, 1.5, 1.45),
           "UpperTorso": (2.2, 1.5, 1.2), "LowerTorso": (2.2, 0.4, 1.2),
           "UpperArm": (0.95, 0.95, 0.95), "LowerArm": (0.95, 0.75, 0.95), "Hand": (0.9, 0.35, 0.9),
           "UpperLeg": (1.05, 0.8, 1.05), "LowerLeg": (1.05, 0.75, 1.05), "Foot": (1.05, 0.35, 1.35)}


# --------------------------------------------------------------------------- broń (osobne przedmioty)
def luk():
    """Łuk: uchwyt w (0, 0, 0) (schowany w pięści), ramiona wzdłuż ±Y wygięte ku łucznikowi (−Z), cięciwa z tyłu."""
    a = Akcesorium("zwiadowca_luk", "Łuk Zwiadowcy", zaczep="LeftGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, -60, 0))
    a.blok("Majdan", (0, 0, 0.0), (0.24, 1.0, 0.3), "skorzany_ciemny", "matowy", faza=0.04)
    for y in (-0.28, 0.0, 0.28):
        a.blok("Owijka", (0, y, 0.0), (0.28, 0.07, 0.34), "skorzany_jasny", "matowy", faza=0.0)
    # ramię łuku: trzy odcinki (długość, przyrost odgięcia ku cięciwie −Z w stopniach, szerokość, grubość);
    # ostatni odcinek odgięty z powrotem do przodu (refleks) — kształt jak nawias „(”
    odcinki = ((0.55, 16, 0.2, 0.26), (0.45, 24, 0.17, 0.22), (0.25, -50, 0.14, 0.17))
    koniec = (0.0, 0.0)
    for zn, s in ((1, "gora"), (-1, "dol")):
        y, zz, kat = 0.48, 0.0, 0.0
        for i, (dl, dk, sz, gr) in enumerate(odcinki):
            kat += dk
            r = math.radians(kat)
            sy, sz_ = math.cos(r) * dl, -math.sin(r) * dl
            a.blok("Ramie %d %s" % (i, s), (0, zn * (y + sy / 2), zz + sz_ / 2), (sz, dl + 0.06, gr), "drewno",
                   "matowy", rot=(-zn * kat, 0, 0), faza=0.04)
            y, zz = y + sy, zz + sz_
        a.blok("Okucie " + s, (0, zn * y, zz), (0.17, 0.12, 0.2), "skorzany_jasny", "matowy", faza=0.02)
        a.blok("Pierscien " + s, (0, zn * 0.53, 0.0), (0.27, 0.08, 0.32), "skorzany_ciemny", "matowy", faza=0.0)
        koniec = (y, zz)
    # cięciwa: prosta, między końcami ramion (łuk w spoczynku; naciąg pokazuje tylko ręka — patrz SLABOSCI)
    a.blok("Cieciwa", (0, 0, koniec[1]), (0.04, 2 * koniec[0], 0.04), "skorzany_jasny", "matowy", faza=0.0)
    return a


def sztylet():
    """Długi sztylet w kształcie liścia: rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z)."""
    a = Akcesorium("zwiadowca_sztylet", "Sztylet Zwiadowcy", zaczep="RightGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, 0, -45))
    a.blok("Rekojesc", (0, 0, 0), (0.2, 1.0, 0.2), "skorzany_ciemny", "matowy", faza=0.04)
    for y in (-0.25, 0.05, 0.35):
        a.blok("Owijka", (0, y, 0), (0.24, 0.07, 0.24), "skorzany", "matowy", faza=0.0)
    a.blok("Glowica", (0, -0.57, 0), (0.3, 0.2, 0.3), "skorzany_jasny", "matowy", faza=0.06)
    a.blok("Glowica kamien", (0, -0.57, 0.16), (0.12, 0.1, 0.04), "akcent", "polysk", faza=0.0)
    a.blok("Jelec", (0, 0.56, 0), (0.62, 0.14, 0.24), "stal_cien", "metal", faza=0.04)
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.33, 0.62, 0), (0.12, 0.24, 0.24), "stal_cien", "metal", faza=0.03)
    # ostrze-liść: szerokie w połowie, zwężone przy jelcu i ku sztychowi
    a.ostroslup("Ostrze dol", (0, 0.86, 0), (0.42, 0.46, 0.1), "stal", "metal", rot=(180, 0, 0), gora=(0.24, 0.1))
    a.ostroslup("Ostrze gora", (0, 1.43, 0), (0.42, 0.68, 0.1), "stal", "metal", gora=(0.0, 0.06))
    a.blok("Zbrocze", (0, 1.05, 0), (0.07, 0.62, 0.12), "stal_cien", "metal", faza=0.0)
    return a


# --------------------------------------------------------------------------- zwiadowca
def zbuduj():
    p = Postac(ID, "Zwiadowca", typ="r15", faza=0.05, paleta=PALETA, wymiary=WYMIARY)
    _glowa(p)
    _tulow(p)
    _rece(p)
    _nogi(p)
    lk, sz = luk(), sztylet()
    p.zaloz(lk, eksport=False)
    p.zaloz(sz, eksport=False)
    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return [p, lk, sz]


SLABOSCI = [
    "Łuk i sztylet są osobnymi przedmiotami (przedmioty/zwiadowca_luk.fbx, zwiadowca_sztylet.fbx) — w FBX postaci ich "
    "nie ma; w grze trzeba je dać jako Tool albo akcesoria na LeftGripAttachment i RightGripAttachment.",
    "Strzał z łuku to sam ruch: łuk się nie ugina, cięciwa jest sztywna i nie dochodzi do dłoni, strzały ani zielonej "
    "smugi trucizny nie ma (efekt do dorobienia w grze). Z boku i z tyłu (kamera gracza) strzał czyta się dobrze; "
    "w kadrze 3/4 z przodu widać łuk wyciągnięty do kamery, a dłoń naciągającą zasłania tułów; od przodu pięść z łukiem "
    "jest przed dolną częścią twarzy (postać celuje w widza — tylko zasłanianie, bez przenikania).",
    "Sztylet zostaje w prawej dłoni także przy strzale — cięciwę „naciąga” pięść ze sztyletem ostrzem w dół i na "
    "zewnątrz. Barki R15 są szerokie (3,15 studa), a ręka krótka (1,45 studa do nadgarstka), więc dłoń nie sięga "
    "twarzy ani linii strzały: naciąg to pięść wysoko przy prawym barku z łokciem cofniętym w tył.",
    "Bryły są sztywno przypięte do kości: kaptur, peleryna i chusta nie falują; poły tuniki siedzą na udach (idą z "
    "nogą, nie przebijają jej). Upadek kończy się leżeniem na brzuchu (na plecach ciało wisiało na kołczanie); "
    "głowa w kapturze jest najniższym punktem, więc pierś jest ok. 0,15 studa nad ziemią.",
    "Twarz nie ma mimiki — ten sam pogodny uśmiech przy trafieniu i upadku.",
    "Unik i uderzenie z góry przesuwają postać w samym klipie (kość LowerTorso): salto ok. 3,25 studa w bok i odskok "
    "z powrotem, wypad ok. 0,5 studa do przodu; klip kończy się w punkcie startu. W salcie biodra obracają się o "
    "−360° (ostatnia klatka ma kąt −360 = ta sama orientacja co 0) — do sprawdzenia przy imporcie klipu do Roblox.",
    "Kolizje sprawdzone w przybliżeniu skryptem poza repozytorium (punkty skrzynek brył łuku, sztyletu, dłoni "
    "i przedramion w każdej klatce kontra skrzynki głowy z kapturem, tułowia i bioder; najniższy punkt ciała "
    "i broni): bez przecięć, najniżej −0,03 studa (chwila przy padaniu na kolana). Nie sprawdzano broni względem nóg "
    "ani łuku względem własnego przedramienia.",
    "Wspólny kadr filmów obejmuje salto w bok, więc w filmach i arkuszach klatek postać jest mniejsza niż na planszy.",
    "Klipy to szkice (0,67–2 s), nie gotowa animacja. Bieg jest w miejscu (stopy ślizgają się względem ziemi).",
    "LowerTorso i Root nie są w 0,0,0 (biodra na wysokości 1,9) — tak jak u Rycerza; dla postaci w grze bez "
    "znaczenia, ciało awatara może tego wymagać (sprawdzić przy pierwszym imporcie).",
]


# --------------------------------------------------------------------------- bryły
def _glowa(p):
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Twarz", (0, 0, 0), (w, h, d), "skora")
        # oczy: duże, czarne, z dwoma błyskami
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.3
            p.blok("Oko " + s, (x, 0.0, z + 0.02), (0.26, 0.4, 0.06), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.05, 0.1, z + 0.055), (0.1, 0.12, 0.03), "bialy", faza=0.0)
            p.blok("Blysk maly " + s, (x + 0.06, -0.1, z + 0.055), (0.05, 0.05, 0.03), "bialy", faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.5, -0.22, z + 0.01), (0.16, 0.08, 0.03), "rumieniec", "matowy", faza=0.0)
            for i, (dx, dy) in enumerate(((-0.06, 0.02), (0.06, -0.03))):
                p.blok("Pieg %s%d" % (s, i), (zn * (0.4 + dx), -0.1 + dy, z + 0.012), (0.06, 0.06, 0.03),
                       "piegi", "matowy", faza=0.0)
        # brwi: lewa (od postaci) wyżej, uniesiona łukiem — bystra, zaczepna mina; prawa niżej, prawie prosto
        p.blok("Brew L", (0.31, 0.31, z + 0.03), (0.34, 0.09, 0.07), "wlosy", "matowy", rot=(0, 0, -10), faza=0.02)
        p.blok("Brew P", (-0.31, 0.25, z + 0.03), (0.32, 0.09, 0.07), "wlosy", "matowy", rot=(0, 0, 5), faza=0.02)
        p.blok("Nos", (0, -0.15, z + 0.05), (0.16, 0.16, 0.1), "skora_cien", "matowy", faza=0.03)
        # uśmiech: otwarty, z zębami, lewy kącik wyżej (łobuzerski)
        # jedna bryła w kształcie „D” (szeroka u góry), pas zębów, różowy język; lewy kącik uniesiony
        p.ostroslup("Usta", (0.02, -0.37, z + 0.02), (0.52, 0.2, 0.05), "tusz", rot=(0, 0, 180),
                    gora=(0.3, 0.05), faza=0.0)
        p.blok("Zeby", (0.02, -0.305, z + 0.05), (0.44, 0.06, 0.03), "bialy", faza=0.0)
        p.blok("Jezyk", (0.02, -0.43, z + 0.05), (0.18, 0.05, 0.03), "D9534A", "matowy", faza=0.0)
        p.blok("Kacik L", (0.3, -0.29, z + 0.02), (0.07, 0.13, 0.05), "tusz", rot=(0, 0, 35), faza=0.0)
        # grzywka spod kaptura: trzy kanciaste kosmyki
        for i, (x, kat, dl) in enumerate(((-0.42, -14, 0.24), (-0.12, 8, 0.3), (0.2, -6, 0.22))):
            p.blok("Kosmyk %d" % i, (x, 0.58, z + 0.04), (0.32, dl, 0.08), "wlosy", "matowy", rot=(0, 0, kat),
                   faza=0.02)

        # kaptur: płaszcz wokół głowy (boki, tył, wierzch), ciemniejsza podszewka wokół twarzy, spiczasty koniec
        kd = d + 0.26                                   # głębokość kaptura
        kz = -0.08                                      # środek kaptura (przód 0,05 przed twarzą)
        kw = w + 0.24                                   # szerokość kaptura
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Kaptur bok " + s, (zn * (w / 2 + 0.06), -0.02, kz), (0.12, h + 0.02, kd), "lisc", "matowy",
                   faza=0.1)
            p.blok("Podszewka " + s, (zn * (w / 2 - 0.01), -0.08, z + 0.035), (0.1, h - 0.2, 0.08), "lisc_ciemny",
                   "matowy", faza=0.02)
        p.blok("Kaptur tyl", (0, -0.02, kz - kd / 2 + 0.06), (kw, h + 0.02, 0.12), "lisc", "matowy", faza=0.1)
        p.blok("Kaptur tyl szew", (0, 0.0, kz - kd / 2 - 0.015), (0.1, h - 0.1, 0.04), "lisc_ciemny", "matowy",
               faza=0.0)
        # czubek: ścięty ostrosłup zwężający się ku górze i cofnięty do tyłu, z niego wyrasta długi szpic
        p.ostroslup("Kaptur czubek", (0, h / 2 + 0.17, kz - 0.06), (kw, 0.38, kd + 0.1), "lisc", "matowy",
                    gora=(kw * 0.5, kd * 0.5), przes_gory=(0.0, -0.24))
        p.blok("Podszewka gora", (0, h / 2 - 0.06, z + 0.05), (w + 0.12, 0.2, 0.12), "lisc_ciemny", "matowy",
               faza=0.03)
        p.blok("Daszek", (0, h / 2 + 0.06, z + 0.06), (kw + 0.02, 0.16, 0.14), "lisc", "matowy", faza=0.05)
        # szpic daszka nad czołem (kaptur od przodu czyta się jak kaptur, a nie hełm)
        p.blok("Daszek szpic", (0, h / 2 - 0.02, z + 0.1), (0.34, 0.34, 0.08), "lisc", "matowy", rot=(0, 0, 45),
               faza=0.03)
        # spiczasty koniec kaptura: sterczy do tyłu, lekko w górę (znak sylwetki z boku i w kadrze 3/4); głowa
        # z kapturem mieści się w 2 studach wysokości (limit części ciała awatara)
        with p.uklad(pos=(0, h / 2 + 0.14, kz - 0.46), obrot=(-76, 0, 0)):
            p.ostroslup("Kaptur szpic", (0, 0.3, 0), (0.84, 0.64, 0.6), "lisc", "matowy", gora=(0.5, 0.36))
            with p.uklad(pos=(0, 0.6, -0.02), obrot=(4, 0, 0)):
                p.ostroslup("Kaptur szpic koniec", (0, 0.32, 0), (0.52, 0.66, 0.38), "lisc", "matowy",
                            gora=(0.0, 0.0), przes_gory=(0.0, -0.06))


def _tulow(p):
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Tunika", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc")
        # lekki skórzany pancerz: kirys z przeszyciem i sznurowaniem
        p.blok("Kirys", (0, -0.14, 0), (w + 0.02, h - 0.3, d + 0.04), "skorzany", "matowy")
        p.blok("Kirys brzeg", (0, -h / 2 + 0.2, 0), (w + 0.06, 0.1, d + 0.08), "skorzany_ciemny", "matowy", faza=0.02)
        p.blok("Przeszycie", (0.42, -0.1, z + 0.035), (0.05, 0.8, 0.04), "skorzany_ciemny", "matowy", faza=0.0)
        for i, y in enumerate((0.05, -0.2)):
            p.blok("Sznurowanie %d" % i, (0.42, y, z + 0.055), (0.22, 0.05, 0.03), "skorzany_jasny", "matowy",
                   rot=(0, 0, 25), faza=0.0)
        # pas kołczanu na skos: z prawego barku (−X) do lewego biodra (+X), z przodu i z tyłu
        for zk, s in ((1, ""), (-1, " tyl")):
            p.blok("Pas kolczanu" + s, (-0.05, -0.02, zk * (z + 0.05)), (2.0, 0.2, 0.05), "skorzany_ciemny", "matowy",
                   rot=(0, 0, -42), faza=0.0)
        p.blok("Sprzaczka pasa", (-0.32, 0.27, z + 0.085), (0.2, 0.2, 0.04), "skorzany_jasny", "matowy",
               rot=(0, 0, -42), faza=0.0)
        # chusta (akcent) wokół szyi z węzłem i końcem na piersi
        p.blok("Chusta", (0, h / 2 + 0.04, 0.1), (1.3, 0.28, 1.06), "akcent", "matowy", faza=0.06)
        p.blok("Chusta wezel", (0.3, h / 2 - 0.14, z + 0.07), (0.3, 0.24, 0.14), "akcent", "matowy", faza=0.05)
        with p.uklad(pos=(0.36, h / 2 - 0.24, z + 0.07), obrot=(0, 0, 14)):
            p.ostroslup("Chusta koniec", (0, -0.24, 0), (0.28, 0.5, 0.06), "akcent", "matowy", rot=(180, 0, 0),
                        gora=(0.08, 0.06), faza=0.0)
        # kołnierz kaptura: opada z karku na barki (kaptur „siedzi” na pelerynie, a nie na szyi jak hełm)
        p.ostroslup("Kaptur kolnierz", (0, h / 2 + 0.1, -0.04), (1.98, 0.3, 1.34), "lisc", "matowy",
                    gora=(1.62, 1.16))
        # krótka peleryna: na barkach, z tyłu do pasa, brzeg cięty w trzy liście
        p.blok("Peleryna barki", (0, h / 2 - 0.04, -0.04), (w + 0.1, 0.18, d + 0.14), "lisc", "matowy", faza=0.06)
        for zn in (1, -1):
            p.blok("Peleryna przod", (zn * 0.82, h / 2 - 0.3, z + 0.07), (0.44, 0.44, 0.06), "lisc", "matowy",
                   faza=0.02)
            p.blok("Peleryna przod lisc", (zn * 0.82, h / 2 - 0.52, z + 0.065), (0.31, 0.31, 0.05), "lisc", "matowy",
                   rot=(0, 0, 45), faza=0.0)
        p.blok("Peleryna plecy", (0, -0.05, -z - 0.06), (w + 0.04, h - 0.1, 0.08), "lisc", "matowy", faza=0.02)
        for i, x in enumerate((-0.72, 0.0, 0.72)):
            p.blok("Peleryna lisc %d" % i, (x, -h / 2 + 0.02, -z - 0.06), (0.52, 0.52, 0.08), "lisc", "matowy",
                   rot=(0, 0, 45), faza=0.0)
            p.blok("Peleryna zylka %d" % i, (x, -h / 2 + 0.06, -z - 0.11), (0.05, 0.4, 0.03), "lisc_ciemny",
                   "matowy", faza=0.0)
        # kołczan na plecach (na skos: dno przy lewym biodrze, wylot za prawym barkiem) i lotki strzał
        with p.uklad(pos=(-0.16, 0.08, -z - 0.36), obrot=(0, 0, 50)):
            p.blok("Kolczan", (0, 0, 0), (0.56, 1.8, 0.46), "skorzany", "matowy", faza=0.08)
            p.blok("Kolczan dno", (0, -0.86, 0), (0.6, 0.14, 0.5), "skorzany_ciemny", "matowy", faza=0.04)
            p.blok("Kolczan wylot", (0, 0.86, 0), (0.62, 0.14, 0.52), "skorzany_ciemny", "matowy", faza=0.04)
            p.blok("Kolczan pas", (0, 0.2, -0.24), (0.6, 0.12, 0.04), "skorzany_ciemny", "matowy", faza=0.0)
            for i, (x, zz, dl, kat) in enumerate(((-0.13, 0.08, 0.8, 8), (0.1, -0.08, 0.95, -6), (0.0, 0.12, 0.68, 0))):
                with p.uklad(pos=(x, 0.9, zz), obrot=(0, 0, kat)):
                    p.blok("Drzewce %d" % i, (0, dl / 2, 0), (0.06, dl, 0.06), "skorzany_jasny", "matowy", faza=0.0)
                    p.blok("Lotka %d" % i, (0, dl - 0.12, 0), (0.2, 0.3, 0.04), "akcent", "matowy", faza=0.0)
                    p.blok("Lotka %d b" % i, (0, dl - 0.12, 0), (0.04, 0.3, 0.2), "akcent", "matowy", faza=0.0)

    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Biodra", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc_ciemny")
        p.blok("Pas", (0, 0.04, 0), (w + 0.04, 0.26, d + 0.04), "skorzany_ciemny", "matowy", faza=0.03)
        p.blok("Klamra", (0, 0.04, z + 0.04), (0.34, 0.28, 0.06), "skorzany_jasny", "matowy", faza=0.03)
        p.blok("Klamra srodek", (0, 0.04, z + 0.075), (0.16, 0.12, 0.03), "skorzany_ciemny", faza=0.0)
        p.blok("Sakwa", (0.78, -0.12, -z - 0.12), (0.46, 0.42, 0.26), "skorzany", "matowy", faza=0.06)
        p.blok("Sakwa klapka", (0.78, 0.02, -z - 0.26), (0.48, 0.18, 0.04), "skorzany_ciemny", "matowy", faza=0.0)


def _rece(p):
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Rekaw", (0, -0.02, 0), (w - 0.06, h - 0.04, d - 0.06), "lisc")
            # mały skórzany naramiennik, lekko opadający na zewnątrz (nie „półka”)
            p.blok("Naramiennik", (zn * 0.05, h / 2 - 0.12, 0), (w + 0.02, 0.26, d + 0.06), "skorzany", "matowy",
                   rot=(0, 0, -zn * 8), faza=0.1)
            p.blok("Naramiennik brzeg", (zn * 0.08, h / 2 - 0.27, 0), (w - 0.04, 0.1, d + 0.02), "skorzany_ciemny",
                   "matowy", rot=(0, 0, -zn * 8), faza=0.03)
        with p.na(strona + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerArm")
            p.blok("Karwasz", (0, 0, 0), (w - 0.04, h, d - 0.04), "skorzany", "matowy")
            p.blok("Karwasz brzeg", (0, h / 2 - 0.06, 0), (w + 0.02, 0.12, d + 0.02), "skorzany_ciemny", "matowy",
                   faza=0.03)
            for i, y in enumerate((0.12, -0.12)):
                p.blok("Karwasz sznur %d" % i, (zn * (w / 2 - 0.0), y, 0), (0.04, 0.06, 0.5), "skorzany_jasny",
                       "matowy", faza=0.0)
        with p.na(strona + "Hand", od="srodek"):
            w, h, d = p.wymiary(strona + "Hand")
            p.blok("Dlon", (0, 0, 0), (w - 0.04, h, d - 0.04), "skora")
            p.blok("Rekawica", (0, h / 2 - 0.05, 0), (w, 0.12, d), "skorzany_ciemny", "matowy", faza=0.02)


def _nogi(p):
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperLeg")
            p.blok("Udo", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc_ciemny")
            # poła tuniki siedzą na udzie (idą z nogą — nie przebijają jej w biegu ani w wypadzie)
            p.blok("Pola", (0, h / 2 - 0.2, 0), (w + 0.04, 0.42, d + 0.04), "lisc", "matowy", faza=0.03)
            p.blok("Pola lisc", (zn * 0.12, h / 2 - 0.42, d / 2 + 0.01), (0.3, 0.3, 0.04), "lisc", "matowy",
                   rot=(0, 0, 45), faza=0.0)
            p.blok("Pola lisc tyl", (zn * 0.12, h / 2 - 0.42, -d / 2 - 0.01), (0.3, 0.3, 0.04), "lisc", "matowy",
                   rot=(0, 0, 45), faza=0.0)
        with p.na(strona + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerLeg")
            p.blok("Cholewa", (0, -0.04, 0), (w - 0.06, h - 0.08, d - 0.06), "skorzany", "matowy")
            p.blok("Cholewa wywiniecie", (0, h / 2 - 0.1, 0), (w + 0.06, 0.2, d + 0.06), "skorzany_jasny", "matowy",
                   faza=0.04)
            p.blok("Cholewa pasek", (0, -0.12, d / 2 - 0.01), (w - 0.2, 0.08, 0.06), "skorzany_ciemny", "matowy",
                   faza=0.0)
        with p.na(strona + "Foot", od="srodek"):
            w, h, d = p.wymiary(strona + "Foot")
            p.blok("But", (0, 0.02, 0), (w - 0.06, h - 0.04, d), "skorzany_ciemny")
            p.blok("Podeszwa", (0, -h / 2 + 0.04, 0.02), (w, 0.08, d + 0.04), "skorzany", "matowy", faza=0.0)
            p.blok("Czubek", (0, -0.02, d / 2 + 0.02), (w - 0.24, 0.24, 0.1), "skorzany_ciemny", "matowy", faza=0.03)


# ---------------------------------------------------------------------------------------------------- animacje
KOSCI = ("LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
         "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg",
         "RightFoot")
STOPY = ("LeftFoot", "RightFoot")


def _fk(p, poza):
    """Kinematyka wprost: {kość: (obrót w świecie, staw w świecie)} dla pozy {kość: {"obrot", "przes"}}."""
    W = {}
    for n, k in p.kosci.items():                          # rodzic zawsze przed dzieckiem
        v = poza.get(n, {})
        Rl = macierz_obrotu(*v.get("obrot", (0, 0, 0)))
        pr = v.get("przes", (0, 0, 0))
        if k["rodzic"] is None:
            W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
        else:
            Rp, tp = W[k["rodzic"]]
            st = p.kosci[k["rodzic"]]["staw"]
            dd = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
            W[n] = (mnoz(Rp, Rl), tuple(tp[i] + dd[i] for i in range(3)))
    return W


def _punkty(p):
    """Punkty kontrolne brył ciała (narożniki i środki ścian skrzynek) na kościach, w układzie stawu kości."""
    if getattr(p, "_pkt", None) is None:
        pk = {}
        for c in p.czesci:
            Rc = macierz_obrotu(*c["r"])
            h = [v / 2 for v in c["s"]]
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for e in (-1, 0, 1):
                        lok = razy_wektor(Rc, (a * h[0], b * h[1], e * h[2]))
                        pk.setdefault(c["kosc"], []).append(tuple(c["p"][i] + lok[i] for i in range(3)))
        p._pkt = pk
    return p._pkt


def _najnizej(p, W, kosci):
    pk, mn = _punkty(p), 1e9
    for n in kosci:
        R, t = W[n]
        for q in pk.get(n, ()):
            mn = min(mn, razy_wektor(R, q)[1] + t[1])
    return mn


def _stopy_plasko(p, pz):
    """Stopy, których poza nie ustawia: płasko na ziemi, palcami tam, gdzie patrzą biodra (z ewentualnym skrętem
    uda); kierunek z bioder, nie z goleni — goleń mocno zgięta w tył patrzy przodem w ziemię."""
    W = _fk(p, pz)
    for s in ("Left", "Right"):
        if s + "Foot" in pz.get("_wlasne", ()):
            continue
        Rg = W[s + "LowerLeg"][0]
        f = razy_wektor(mnoz(W["LowerTorso"][0], macierz_obrotu(0, pz[s + "UpperLeg"]["obrot"][1], 0)), (0, 0, 1))
        cel = macierz_obrotu(0, math.degrees(math.atan2(f[0], f[2])), 0)
        Rt = tuple(tuple(Rg[j][i] for j in range(3)) for i in range(3))
        pz[s + "Foot"] = {"obrot": tuple(round(v, 3) for v in katy_z_macierzy(mnoz(Rt, cel)))}




def _poza(p, poza, ziemia=True):
    """Poza kluczowa: {kość: (rx, ry, rz)} albo {kość: {"obrot":…, "przes":…}}; kość spoza słownika — spoczynek.
    ziemia=True: stopy (jeśli poza ich nie ustawia) płasko, a biodra jadą w pionie tak, by najniższy punkt stóp był
    na ziemi; ziemia="cialo": całe ciało dociągnięte do ziemi po najniższym punkcie (siad, leżenie); ziemia=False:
    lot (biodra jak w pozie, ale nic nie schodzi pod ziemię)."""
    pz = {"_wlasne": tuple(n for n in poza)}
    for n in KOSCI:
        v = poza.get(n, (0, 0, 0))
        pz[n] = dict(v) if isinstance(v, dict) else {"obrot": tuple(v)}
        pz[n].setdefault("obrot", (0, 0, 0))
    pz["LowerTorso"].setdefault("przes", (0, 0, 0))
    pz["_ziemia"] = ziemia
    _na_ziemi(p, pz)
    return pz


def _na_ziemi(p, pz):
    """Dociąga pozę do ziemi według pz["_ziemia"] (patrz _poza)."""
    z = pz["_ziemia"]
    if z is True:
        _stopy_plasko(p, pz)
        dno = _najnizej(p, _fk(p, pz), STOPY)
    elif z == "cialo":
        dno = _najnizej(p, _fk(p, pz), KOSCI)
    else:
        dno = min(0.0, _najnizej(p, _fk(p, pz), KOSCI))
    x, y, zz = pz["LowerTorso"]["przes"]
    pz["LowerTorso"]["przes"] = (x, round(y - dno, 4), zz)


# ------------------------------------------------------------------ ręka celuje: prosta odwrotna kinematyka (2 kości)
def _n(v):
    d = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / d for x in v)


def _kr(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _sk(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _tr(m):
    return tuple(tuple(m[j][i] for j in range(3)) for i in range(3))


def _kolumny(x, y, z):
    return ((x[0], y[0], z[0]), (x[1], y[1], z[1]), (x[2], y[2], z[2]))


def _reka(p, pz, strona, cel, biegun, os=None, przod=None, swiat=False):
    """Ustawia w pozie pz ramię, przedramię i dłoń strony („Left”/„Right”) tak, żeby nadgarstek trafił w cel.
    cel = przesunięcie od stawu barku, biegun = kierunek, w którą stronę wychodzi łokieć — w osiach tułowia
    (swiat=False) albo w osiach modelu (swiat=True). os / przod = kierunek broni w dłoni (oś broni = +Y przedmiotu:
    ostrze sztyletu, ramiona łuku; przód broni = +Z przedmiotu: płaz sztyletu, brzuch łuku) w tych samych osiach.
    Łokieć zgina się tylko w zawiasie (obrót przedramienia = sam rx), jak w klipach pisanych ręcznie."""
    W = _fk(p, pz)
    Rt = W["UpperTorso"][0]
    S = W[strona + "UpperArm"][1]
    do_sw = (lambda v: v) if swiat else (lambda v: razy_wektor(Rt, v))
    a = math.dist(p.staw(strona + "LowerArm"), p.staw(strona + "UpperArm"))
    b = math.dist(p.staw(strona + "Hand"), p.staw(strona + "LowerArm"))
    d = do_sw(cel)
    dl = max(abs(a - b) + 0.05, min(a + b - 0.02, math.sqrt(_sk(d, d))))
    dh = _n(d)
    bg = do_sw(biegun)
    n = _n(tuple(bg[i] - _sk(bg, dh) * dh[i] for i in range(3)))
    ca = (a * a + dl * dl - b * b) / (2 * a * dl)
    sa = math.sqrt(max(0.0, 1 - ca * ca))
    u = tuple(ca * dh[i] + sa * n[i] for i in range(3))                 # kierunek ramienia (bark -> łokieć)
    E = tuple(a * u[i] for i in range(3))
    v = _n(tuple(dh[i] * dl - E[i] for i in range(3)))                  # kierunek przedramienia
    zc = tuple(v[i] - _sk(v, u) * u[i] for i in range(3))
    if _sk(zc, zc) < 1e-6:
        zc = tuple(-x for x in n)
    Y = tuple(-x for x in u)
    Z = _n(zc)
    X = _kr(Y, Z)
    Rua = _kolumny(X, Y, Z)
    pz[strona + "UpperArm"] = {"obrot": katy_z_macierzy(mnoz(_tr(Rt), Rua))}
    th = -math.degrees(math.acos(max(-1.0, min(1.0, _sk(u, v)))))
    pz[strona + "LowerArm"] = {"obrot": (th, 0.0, 0.0)}
    if os is not None:
        Rla = mnoz(Rua, macierz_obrotu(th, 0, 0))
        A = _n(do_sw(os))
        F = do_sw(przod)
        F = _n(tuple(F[i] - _sk(F, A) * A[i] for i in range(3)))
        Yh = tuple(-x for x in F)
        Rh = _kolumny(_kr(Yh, A), Yh, A)
        pz[strona + "Hand"] = {"obrot": katy_z_macierzy(mnoz(_tr(Rla), Rh))}
    return pz


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku −170° → +170° przez zero):
    (rx, ry, rz) ≡ (180 − rx, ry + 180, rz + 180), każdy kąt także ± 360."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        dd = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or dd < najl[0] - 1e-6:
            najl = (dd, c)
    return najl[1]


def _sekwencja(k, czasy, pozy, wyg=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza albo słownik; {} = spoczynek). Kąty przechodzą
    z łagodnym wejściem i wyjściem (wyg = {numer pozy: "liniowo"} — odcinek od tej pozy jednostajnie); gdy obie
    sąsiednie pozy stoją na ziemi, stopy są w każdej klatce płasko na ziemi; przy siadzie i leżeniu ciało leży na
    ziemi; w pozostałych odcinkach nic nie schodzi pod ziemię."""
    p = k.postac
    pozy = [pz if "_ziemia" in pz else _poza(p, pz) for pz in pozy]
    poprz = {}
    for pz in pozy:                                       # kąty póz najbliżej poprzedniej pozy (krótsza droga)
        for n in KOSCI:
            pz[n]["obrot"] = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = pz[n]["obrot"]
    poprz = {}
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        e = t if (wyg or {}).get(i) == "liniowo" else t * t * (3 - 2 * t)
        a, b = pozy[i], pozy[i + 1]
        pz = {n: {"obrot": tuple(a[n]["obrot"][j] + (b[n]["obrot"][j] - a[n]["obrot"][j]) * e for j in range(3))}
              for n in KOSCI}
        p0, p1 = a["LowerTorso"]["przes"], b["LowerTorso"]["przes"]
        pz["LowerTorso"]["przes"] = tuple(p0[j] + (p1[j] - p0[j]) * e for j in range(3))
        z0, z1 = a["_ziemia"], b["_ziemia"]
        pz["_wlasne"] = tuple(set(a["_wlasne"]) | set(b["_wlasne"]))
        pz["_ziemia"] = z0 if z0 == z1 else False
        _na_ziemi(p, pz)
        for n in KOSCI:
            ob = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = ob
            k.klucz(f, n, obrot=tuple(round(v, 3) for v in ob), wyg="liniowo")
        k.klucz(f, "LowerTorso", przes=tuple(round(v, 4) for v in pz["LowerTorso"]["przes"]), wyg="liniowo")


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    uderzenie_z_gory(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


# poza gotowości: lekko ugięte kolana, łuk pionowo z boku (cięciwą do ciała), sztylet nisko przed prawym biodrem
GOTOWOSC = {"UpperTorso": (6, -8, 0), "Head": (-4, 8, 0),
            "LeftUpperArm": (-20, 0, 24), "LeftLowerArm": (-60, 0, 0), "LeftHand": (-2, 0, -30),
            "RightUpperArm": (-8, 0, -12), "RightLowerArm": (-52, 0, 0), "RightHand": (-10, 0, 0),
            "LeftUpperLeg": (-14, 0, 6), "LeftLowerLeg": (24, 0, 0),
            "RightUpperLeg": (-6, 0, -6), "RightLowerLeg": (16, 0, 0),
            "LowerTorso": {"obrot": (0, -10, 0)}}


def _z(baza, **zmiany):
    d = dict(baza)
    d.update(zmiany)
    return d


def idle(p, dl=60):
    """Spoczynek w gotowości (pętla 2 s): sprężysty oddech na ugiętych kolanach, głowa rozgląda się."""
    k = p.klip("idle", dl, petla=True)
    a = _poza(p, GOTOWOSC)
    b = _poza(p, _z(GOTOWOSC, UpperTorso=(9, -6, 1), Head=(-6, 2, 2), LeftUpperLeg=(-17, 0, 6),
                    LeftLowerLeg=(30, 0, 0), RightUpperLeg=(-9, 0, -6), RightLowerLeg=(22, 0, 0),
                    LeftLowerArm=(-63, 0, 0), RightLowerArm=(-56, 0, 0)))
    _sekwencja(k, (0, dl // 2, dl), (a, b, a))
    return k


def ruch(p, dl=20):
    """Lekki bieg w miejscu (pętla 0,67 s na dwa kroki): pochylony tułów, wysokie kolano, ręce z bronią pracują
    na przemian; biodra podskakują same (najniższa stopa zawsze na ziemi)."""
    k = p.klip("ruch", dl, petla=True)

    def krok(s):                       # s = 1: lewa noga z przodu; −1: prawa
        L, R = ("Left", "Right") if s > 0 else ("Right", "Left")
        return {"LowerTorso": {"obrot": (8, -s * 10, 0)}, "UpperTorso": (14, s * 14, 0), "Head": (-16, s * 4, 0),
                L + "UpperLeg": (-42, 0, 0), L + "LowerLeg": (22, 0, 0),
                R + "UpperLeg": (30, 0, 0), R + "LowerLeg": (62, 0, 0), R + "Foot": (40, 0, 0),
                # ręka przeciwna do nogi z przodu idzie do przodu
                "LeftUpperArm": (s * 38 - 6, 0, 16), "LeftLowerArm": (-62, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (-s * 40 - 8, 0, -14), "RightLowerArm": (-70, 0, 0), "RightHand": (-10, 0, 0)}

    def przejscie(s):                  # s = 1: lewa noga podporowa, prawa przechodzi wysoko do przodu
        L, R = ("Left", "Right") if s > 0 else ("Right", "Left")
        return {"LowerTorso": {"obrot": (8, 0, 0)}, "UpperTorso": (16, 0, 0), "Head": (-18, 0, 0),
                L + "UpperLeg": (-4, 0, 0), L + "LowerLeg": (14, 0, 0),
                R + "UpperLeg": (-46, 0, 0), R + "LowerLeg": (100, 0, 0), R + "Foot": (10, 0, 0),
                "LeftUpperArm": (-6, 0, 16), "LeftLowerArm": (-62, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (-8, 0, -14), "RightLowerArm": (-74, 0, 0), "RightHand": (-10, 0, 0)}

    pozy = (krok(1), przejscie(-1), krok(-1), przejscie(1), krok(1))
    _sekwencja(k, (0, 5, 10, 15, dl), pozy, wyg={i: "liniowo" for i in range(4)})
    return k


def atak(p, dl=28):
    """Pchnięcie sztyletem (0,93 s): skręt i przysiad z ostrzem cofniętym przy prawym biodrze (kl. 7) → szybki wypad
    prawą nogą i pchnięcie na wysokości piersi przeciwnika, trafienie w kl. 11, dwie klatki zatrzymania → powrót.
    Łuk w lewej ręce odchodzi do tyłu dla równowagi."""
    k = p.klip("atak", dl, petla=False)
    zamach = _poza(p, {"LowerTorso": {"obrot": (2, -30, 0), "przes": (0, 0, -0.2)}, "UpperTorso": (4, -28, 0),
                       "Head": (-6, 50, 0),
                       "LeftUpperLeg": (-32, 0, 8), "LeftLowerLeg": (48, 0, 0),
                       "RightUpperLeg": (-2, 0, -10), "RightLowerLeg": (40, 0, 0),
                       "LeftUpperArm": (-22, 0, 58), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                       # ostrze cofnięte daleko za prawe biodro, na zewnątrz od tułowia (wyraźny zamach z boku i 3/4)
                       "RightUpperArm": (40, 0, -30), "RightLowerArm": (-60, 0, 0), "RightHand": (-24, 0, 0)})
    pchniecie = _poza(p, {"LowerTorso": {"obrot": (8, 22, 0), "przes": (0, 0, 0.55)}, "UpperTorso": (12, 18, 0),
                          "Head": (-12, -34, 0),
                          "RightUpperLeg": (-58, 0, -4), "RightLowerLeg": (48, 0, 0),
                          "LeftUpperLeg": (30, 0, 6), "LeftLowerLeg": (34, 0, 0),
                          "LeftUpperArm": (28, 0, 40), "LeftLowerArm": (-36, 0, 0), "LeftHand": (-2, 0, -30)})
    _reka(p, pchniecie, "Right", cel=(0.25, -0.3, 1.42), biegun=(-0.6, -1, 0), os=(0.05, -0.12, 1), przod=(0, 1, 0),
          swiat=True)
    dobicie = _poza(p, _z({n: v["obrot"] for n, v in pchniecie.items() if n in KOSCI and n not in STOPY},
                          LowerTorso={"obrot": (9, 24, 0), "przes": (0, 0, 0.6)}))
    _reka(p, dobicie, "Right", cel=(0.22, -0.34, 1.45), biegun=(-0.6, -1, 0), os=(0.05, -0.16, 1), przod=(0, 1, 0),
          swiat=True)
    powrot = _poza(p, {"LowerTorso": {"obrot": (4, 8, 0), "przes": (0, 0, 0.25)}, "UpperTorso": (8, 4, 0),
                       "Head": (-6, -6, 0), "RightUpperLeg": (-28, 0, -6), "RightLowerLeg": (30, 0, 0),
                       "LeftUpperLeg": (10, 0, 6), "LeftLowerLeg": (24, 0, 0),
                       "LeftUpperArm": (-6, 0, 30), "LeftLowerArm": (-50, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (-40, 0, -14), "RightLowerArm": (-50, 0, 0), "RightHand": (-10, 0, 0)})
    _sekwencja(k, (0, 7, 11, 13, 20, dl), (GOTOWOSC, zamach, pchniecie, dobicie, powrot, GOTOWOSC),
               wyg={1: "liniowo"})
    return k


def _strzal(p, naciag, tulow=(0, -28, 0), biodra=(0, -46, 0), glowa=(-4, 64, 4), luk_cel=(-0.55, 0.2, 1.4),
            biegun=(-0.5, 0.9, -1), luk_os=(0.12, 1, 0), noz_os=(-0.6, -0.8, 0.05)):
    """Poza strzału: szeroki rozkrok, lewy bark do celu (biodra i tułów skręcone razem ok. 75°), głowa patrzy
    wzdłuż ręki z łukiem. Lewa ręka wyprostowana w stronę celu (+Z) na wysokości barku, łuk pionowo, brzuchem do
    celu (luk_cel = przesunięcie nadgarstka od lewego barku, osie modelu). Prawa dłoń (ze sztyletem ostrzem w dół
    i na zewnątrz, z dala od twarzy i tułowia) w miejscu `naciag` (od prawego barku, osie tułowia), łokieć wysoko i w tył (biegun)."""
    pz = _poza(p, {"LowerTorso": {"obrot": biodra}, "UpperTorso": tulow, "Head": glowa,
                   "LeftUpperLeg": (-18, 0, 20), "LeftLowerLeg": (22, 0, 0),
                   "RightUpperLeg": (10, 0, -20), "RightLowerLeg": (16, 0, 0)})
    _reka(p, pz, "Left", cel=luk_cel, biegun=(0.3, -1, -0.3), os=luk_os, przod=(0, 0, 1), swiat=True)
    _reka(p, pz, "Right", cel=naciag, biegun=biegun, os=noz_os, przod=(0, 0, 1))
    return pz


def umiejetnosc(p, dl=54):
    """Zatruta strzała (1,8 s), wyraźnie inna niż atak sztyletem: obrót lewym barkiem do celu i łuk wyrzucony
    przed siebie na wysokość barku (kl. 9), prawa dłoń sięga do cięciwy, naciąg z łokciem wysoko w tył (kl. 19),
    celowanie z lekkim drżeniem, wypuszczenie z odrzutem (kl. 31: prawa dłoń odskakuje w tył, łuk podbity w górę),
    zatrzymanie i powrót. Samej strzały i zielonej smugi trucizny nie ma (efekt w grze)."""
    k = p.klip("umiejetnosc", dl, petla=False)
    # barki R15 są szerokie, a ręce krótkie: dłoń naciągająca nie sięga twarzy, więc „naciąg” to pięść wysoko przy
    # prawym barku z łokciem cofniętym w tył (czytelny kształt z boku i z tyłu, nic nie wchodzi w tułów ani kaptur)
    # wyrzut: łuk idzie do celu, prawa dłoń ze sztyletem ostrzem naprzód wychodzi przed brzuch (ostrze nie
    # przechodzi przez tułów w drodze z gotowości do cięciwy)
    wyrzut = _strzal(p, naciag=(-0.3, -0.6, 0.8), tulow=(3, -10, 0), biodra=(0, -20, 0), glowa=(-3, 26, 0),
                     luk_cel=(0.4, -0.2, 1.2), biegun=(-1, -0.3, 0), noz_os=(-0.5, 0.2, 1))
    przyklad = _strzal(p, naciag=(0.15, 0.1, 1.15), tulow=(2, -18, 0), biodra=(0, -34, 0), glowa=(-2, 46, 2),
                       biegun=(-1, -0.3, -0.2))
    naciag = _strzal(p, naciag=(-0.4, 0.5, 0.2), biegun=(-0.3, 0.3, -1))
    celuje = _strzal(p, naciag=(-0.45, 0.45, 0.25), tulow=(1, -30, 0), luk_cel=(-0.53, 0.24, 1.4),
                     biegun=(-0.4, 0.4, -1))
    wypuszcza = _strzal(p, naciag=(-0.55, 0.5, -0.4), tulow=(-3, -32, 0), glowa=(-8, 68, 4),
                        luk_cel=(-0.55, 0.55, 1.3), biegun=(0.3, 0.2, -1), luk_os=(0.2, 1, -0.25))
    zostaje = _strzal(p, naciag=(-0.55, 0.45, -0.3), tulow=(-1, -31, 0), luk_cel=(-0.55, 0.4, 1.35),
                      biegun=(0.2, 0.2, -1))
    opuszcza = _strzal(p, naciag=(-0.35, -1.05, 0.5), tulow=(4, -14, 0), biodra=(0, -24, 0), glowa=(-4, 30, 0),
                       luk_cel=(0.5, -0.8, 1.0), biegun=(-1, 0, -0.3), noz_os=(-0.3, 0.3, 1))
    _sekwencja(k, (0, 4, 9, 13, 19, 30, 32, 40, 47, dl),
               (GOTOWOSC, wyrzut, przyklad, przyklad, naciag, celuje, wypuszcza, zostaje, opuszcza, GOTOWOSC),
               wyg={5: "liniowo"})
    return k


def uderzenie_z_gory(p, dl=46):
    """Uderzenie z góry (drugi klip umiejętności, 1,5 s): przysiad (kl. 7), wyskok z sztyletem uniesionym wysoko
    nad prawym barkiem (szczyt kl. 15), cios z góry w dół przed siebie przy lądowaniu w głębokim wypadzie (kl. 20),
    zatrzymanie i powrót."""
    k = p.klip("uderzenie_z_gory", dl, petla=False)
    przysiad = _poza(p, {"LowerTorso": {"obrot": (10, -6, 0)}, "UpperTorso": (18, -6, 0), "Head": (-20, 6, 0),
                         "LeftUpperLeg": (-60, 0, 8), "LeftLowerLeg": (92, 0, 0),
                         "RightUpperLeg": (-56, 0, -8), "RightLowerLeg": (88, 0, 0),
                         "LeftUpperArm": (30, 0, 30), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                         "RightUpperArm": (36, 0, -24), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    szczyt = _poza(p, {"LowerTorso": {"obrot": (-6, -10, 0), "przes": (0, 1.7, 0.2)}, "UpperTorso": (-10, -12, 0),
                       "Head": (4, 14, 0),
                       "LeftUpperLeg": (-70, 0, 10), "LeftLowerLeg": (110, 0, 0), "LeftFoot": (20, 0, 0),
                       "RightUpperLeg": (-30, 0, -8), "RightLowerLeg": (90, 0, 0), "RightFoot": (25, 0, 0),
                       "LeftUpperArm": (-40, 0, 70), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30)},
                   ziemia=False)
    # dłoń wysoko nad prawym barkiem, na zewnątrz od kaptura; ostrze w górę i na zewnątrz
    _reka(p, szczyt, "Right", cel=(-0.62, 1.3, 0.12), biegun=(-1, 0.1, -0.3), os=(-0.4, 1, 0.1), przod=(0, 0, 1))
    cios = _poza(p, {"LowerTorso": {"obrot": (18, 10, 0), "przes": (0, 0, 0.45)}, "UpperTorso": (24, 8, 0),
                     "Head": (-30, -14, 0),
                     "RightUpperLeg": (-74, 0, -6), "RightLowerLeg": (80, 0, 0),
                     "LeftUpperLeg": (10, 0, 10), "LeftLowerLeg": (64, 0, 0),
                     "LeftUpperArm": (-10, 0, 62), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30)})
    _reka(p, cios, "Right", cel=(0.15, -0.75, 1.25), biegun=(-1, -0.4, 0), os=(0, -0.62, 0.78), przod=(-1, 0, 0),
          swiat=True)
    trzyma = _poza(p, _z({n: v["obrot"] for n, v in cios.items() if n in KOSCI and n not in STOPY},
                         LowerTorso={"obrot": (20, 10, 0), "przes": (0, 0, 0.45)}, UpperTorso=(27, 8, 0)))
    _reka(p, trzyma, "Right", cel=(0.15, -0.82, 1.22), biegun=(-1, -0.4, 0), os=(0, -0.66, 0.75), przod=(-1, 0, 0),
          swiat=True)
    wstaje = _poza(p, {"LowerTorso": {"obrot": (6, 4, 0), "przes": (0, 0, 0.2)}, "UpperTorso": (8, 0, 0),
                       "Head": (-8, 0, 0), "RightUpperLeg": (-34, 0, -6), "RightLowerLeg": (40, 0, 0),
                       "LeftUpperLeg": (-6, 0, 8), "LeftLowerLeg": (30, 0, 0),
                       "LeftUpperArm": (-10, 0, 30), "LeftLowerArm": (-50, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (-30, 0, -14), "RightLowerArm": (-50, 0, 0), "RightHand": (-10, 0, 0)})
    _sekwencja(k, (0, 7, 15, 20, 27, 36, dl), (GOTOWOSC, przysiad, szczyt, cios, trzyma, wstaje, GOTOWOSC),
               wyg={2: "liniowo"})
    return k


def trafienie(p, dl=20):
    """Reakcja na cios (0,67 s): szarpnięcie tułowia i głowy w tył (kl. 4), ręce odlatują na boki, krok w tył,
    powrót do gotowości."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = _poza(p, {"LowerTorso": {"obrot": (-6, -4, 0), "przes": (0, 0, -0.4)}, "UpperTorso": (-18, 10, 4),
                      "Head": (-22, -14, 8),
                      "LeftUpperArm": (-34, 0, 48), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-24, 0, -46), "RightLowerArm": (-46, 0, 0), "RightHand": (-10, 0, 0),
                      "RightUpperLeg": (18, 0, -6), "RightLowerLeg": (26, 0, 0),
                      "LeftUpperLeg": (-16, 0, 6), "LeftLowerLeg": (18, 0, 0)})
    wraca = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (-2, -8, 0), "przes": (0, 0, -0.15)}, UpperTorso=(-4, -2, 1),
                        Head=(-8, 0, 2), RightUpperLeg=(6, 0, -6)))
    _sekwencja(k, (0, 4, 11, dl), (GOTOWOSC, szarp, wraca, GOTOWOSC), wyg={0: "liniowo"})
    return k


def unik(p, dl=40):
    """Unik — znak rozpoznawczy klasy (1,33 s): przysiad i wybicie w lewo (+X), boczne salto w powietrzu (pełny
    obrót w płaszczyźnie przodu, nogi podkulone, ręce z bronią rozłożone na zewnątrz — nic nie mija głowy),
    lądowanie w niskim przysiadzie ok. 3,2 studa w bok, krótki odskok z powrotem na linię ciosu."""
    k = p.klip("unik", dl, petla=False)
    rece_lot = {"LeftUpperArm": (0, 0, 110), "LeftLowerArm": (-20, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (0, 0, -110), "RightLowerArm": (-20, 0, 0), "RightHand": (-10, 0, 0)}
    nogi_lot = {"LeftUpperLeg": (-80, 0, 14), "LeftLowerLeg": (110, 0, 0), "LeftFoot": (20, 0, 0),
                "RightUpperLeg": (-74, 0, -14), "RightLowerLeg": (104, 0, 0), "RightFoot": (20, 0, 0)}
    przysiad = _poza(p, {"LowerTorso": {"obrot": (8, 0, -12), "przes": (0.25, 0, 0)}, "UpperTorso": (14, 0, -8),
                         "Head": (-12, 0, 10),
                         "LeftUpperLeg": (-50, 0, 18), "LeftLowerLeg": (84, 0, 0),
                         "RightUpperLeg": (-46, 0, -2), "RightLowerLeg": (80, 0, 0),
                         "LeftUpperArm": (10, 0, 40), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                         "RightUpperArm": (14, 0, -50), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    # lot: obrót bioder rz od 0 do −360 (głowa idzie w stronę +X), środek ciała po łuku w bok i w górę
    lot = []
    for kat, x, y in ((-50, 0.9, 1.05), (-130, 1.6, 2.45), (-215, 2.3, 2.7), (-295, 2.9, 1.7)):
        lot.append(_poza(p, dict(rece_lot, **nogi_lot, LowerTorso={"obrot": (0, 0, kat), "przes": (x, y, 0)},
                                 UpperTorso=(10, 0, 0), Head=(-10, 0, 0)), ziemia=False))
    ladowanie = _poza(p, {"LowerTorso": {"obrot": (10, 0, -366), "przes": (3.25, 0, 0)}, "UpperTorso": (16, 0, 6),
                          "Head": (-16, 0, -4),
                          "LeftUpperLeg": (-50, 0, 14), "LeftLowerLeg": (76, 0, 0),
                          "RightUpperLeg": (-44, 0, -6), "RightLowerLeg": (72, 0, 0),
                          "LeftUpperArm": (-30, 0, 80), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                          "RightUpperArm": (-30, 0, -60), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    odskok = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (2, -10, -360), "przes": (1.6, 0.75, 0)},
                         UpperTorso=(4, -8, -6), LeftUpperLeg=(-24, 0, 10), LeftLowerLeg=(40, 0, 0),
                         RightUpperLeg=(-20, 0, -10), RightLowerLeg=(36, 0, 0), LeftFoot=(18, 0, 0),
                         RightFoot=(18, 0, 0)), ziemia=False)
    koniec = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (0, -10, -360)}))
    _sekwencja(k, (0, 5, 9, 12, 15, 18, 21, 26, 31, 35, dl),
               (GOTOWOSC, przysiad, lot[0], lot[1], lot[2], lot[3], ladowanie, ladowanie, odskok,
                _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (4, -10, -360), "przes": (0.1, 0, 0)},
                            LeftUpperLeg=(-24, 0, 6), LeftLowerLeg=(40, 0, 0), RightUpperLeg=(-16, 0, -6),
                            RightLowerLeg=(32, 0, 0))), koniec),
               wyg={1: "liniowo", 2: "liniowo", 3: "liniowo", 4: "liniowo", 5: "liniowo"})
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): szarpnięcie, chwiejny krok w tył, kolana się uginają, pada na kolana i dalej twarzą w dół,
    z rękami rozrzuconymi na boki i podkulonymi łydkami (komiksowo); głowa odwrócona w bok, więc twarz widać.
    Ostatnia klatka: leży (do utrzymania w grze). Na brzuchu, nie na plecach — leżąc na plecach ciało opierało się
    na kołczanie i wisiało nad ziemią."""
    k = p.klip("upadek", dl, petla=False)
    szarp = _poza(p, {"LowerTorso": {"obrot": (-6, -4, 0), "przes": (0, 0, -0.35)}, "UpperTorso": (-16, 10, 4),
                      "Head": (-24, -10, 8),
                      "LeftUpperArm": (-30, 0, 50), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-22, 0, -48), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0),
                      "RightUpperLeg": (16, 0, -6), "RightLowerLeg": (24, 0, 0), "LeftUpperLeg": (-14, 0, 6)})
    chwiej = _poza(p, {"LowerTorso": {"obrot": (-4, 8, 6), "przes": (0, 0, -0.6)}, "UpperTorso": (14, -6, -8),
                       "Head": (24, 10, -12),
                       "LeftUpperArm": (0, 0, 20), "LeftLowerArm": (-20, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (6, 0, -16), "RightLowerArm": (-20, 0, 0), "RightHand": (-10, 0, 0),
                       "LeftUpperLeg": (8, 0, 4), "LeftLowerLeg": (20, 0, 0),
                       "RightUpperLeg": (-12, 0, -10), "RightLowerLeg": (26, 0, 0)})
    # kolana się uginają, głowa opada, ręce wiszą bezwładnie
    ugina = _poza(p, {"LowerTorso": {"obrot": (6, 4, 4), "przes": (0, 0, -0.6)}, "UpperTorso": (16, -4, -4),
                      "Head": (22, 6, -8),
                      "LeftUpperLeg": (-50, 0, 10), "LeftLowerLeg": (88, 0, 0),
                      "RightUpperLeg": (-44, 0, -10), "RightLowerLeg": (84, 0, 0),
                      "LeftUpperArm": (-14, 0, 22), "LeftLowerArm": (-24, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-10, 0, -22), "RightLowerArm": (-24, 0, 0), "RightHand": (-10, 0, 0)})
    # na kolanach, tułów leci do przodu jak ścięte drzewo, ręce rozrzucone na boki, broń wzdłuż rąk (przy padaniu
    # obraca się tylko wokół własnej osi, więc nie wchodzi w ziemię)
    kolana = _poza(p, {"LowerTorso": {"obrot": (40, 2, 2), "przes": (0, 0, -0.35)}, "UpperTorso": (14, -4, 0),
                       "Head": (-30, 24, 0),
                       "LeftUpperLeg": (-38, 0, 10), "LeftLowerLeg": (100, 0, 0),
                       "RightUpperLeg": (-34, 0, -10), "RightLowerLeg": (96, 0, 0),
                       "LeftUpperArm": (-20, 0, 76), "LeftLowerArm": (-14, 0, 0), "LeftHand": (90, 90, 0),
                       "RightUpperArm": (-20, 0, -78), "RightLowerArm": (-14, 0, 0), "RightHand": (90, 0, 0)},
                   ziemia="cialo")
    # leży twarzą w dół; głowa uniesiona i odwrócona w bok (do kamery 3/4), łydki podkulone w górę; dłonie obrócone
    # tak, że łuk i sztylet leżą płasko na ziemi (a nie sterczą w niebo ani nie wchodzą w ziemię)
    lezy = {"LowerTorso": {"obrot": (88, 0, 0), "przes": (0, 0, 0.3)}, "UpperTorso": (2, 0, 0), "Head": (-70, 50, 0),
            "LeftUpperLeg": (4, 0, 10), "LeftLowerLeg": (75, 0, 0),
            "RightUpperLeg": (0, 0, -12), "RightLowerLeg": (45, 0, 0),
            "LeftUpperArm": (-20, -4, 80), "LeftLowerArm": (-14, 0, 0), "LeftHand": (90, 90, 0),
            "RightUpperArm": (-20, 4, -82), "RightLowerArm": (-14, 0, 0), "RightHand": (90, 0, 0)}
    # ostatnie drgnięcie: łydki podskakują, głowa unosi się i opada (tułów i ręce leżą, broń nie wchodzi w ziemię)
    odbicie = _z(lezy, Head=(-62, 44, 0), LeftLowerLeg=(95, 0, 0), RightLowerLeg=(66, 0, 0))
    lezy = _poza(p, lezy, ziemia="cialo")
    odbicie = _poza(p, odbicie, ziemia="cialo")
    _sekwencja(k, (0, 4, 12, 22, 30, 38, 43, 50, dl),
               (GOTOWOSC, szarp, chwiej, ugina, kolana, lezy, odbicie, lezy, lezy), wyg={4: "liniowo"})
    return k


def wiwat(p, dl=48):
    """Radość po wygranej (pętla 1,6 s): dwa podskoki, lewa ręka wyrzucona w bok i w górę z łukiem pionowo
    (wygięciem na zewnątrz — od przodu widać kształt łuku), prawa pięść ze sztyletem pompuje w górę, na zewnątrz od
    głowy; uśmiech do kamery."""
    k = p.klip("wiwat", dl, petla=True)
    dol = _poza(p, {"LowerTorso": {"obrot": (4, 0, 0)}, "UpperTorso": (8, 0, 0), "Head": (2, 0, -5),
                    "LeftUpperLeg": (-26, 0, 8), "LeftLowerLeg": (48, 0, 0),
                    "RightUpperLeg": (-24, 0, -8), "RightLowerLeg": (44, 0, 0)})
    _reka(p, dol, "Left", cel=(1.28, 0.3, 0.35), biegun=(0.2, -1, 0), os=(0, 1, 0), przod=(1, 0, 0.25))
    _reka(p, dol, "Right", cel=(-0.55, -0.3, 0.75), biegun=(-1, -0.5, 0), os=(-0.45, 1, 0.3), przod=(0, 0, 1))
    gora = _poza(p, {"LowerTorso": {"obrot": (-4, 0, 0), "przes": (0, 0.5, 0)}, "UpperTorso": (-8, 0, 0),
                     "Head": (-16, 0, 6),
                     "LeftUpperLeg": (-12, 0, 6), "LeftLowerLeg": (26, 0, 0), "LeftFoot": (22, 0, 0),
                     "RightUpperLeg": (-8, 0, -6), "RightLowerLeg": (22, 0, 0), "RightFoot": (22, 0, 0)},
                 ziemia=False)
    _reka(p, gora, "Left", cel=(1.02, 1.0, 0.25), biegun=(0.4, -1, 0), os=(-0.18, 1, 0), przod=(1, 0.2, 0.25))
    _reka(p, gora, "Right", cel=(-0.85, 1.12, 0.3), biegun=(-1, -0.2, 0), os=(-0.35, 1, 0.2), przod=(0, 0, 1))
    _sekwencja(k, (0, 12, 24, 36, dl), (dol, gora, dol, gora, dol))
    return k
