# -*- coding: utf-8 -*-
"""STRAŻNIK GAJU — strażnik biomu lasu, najważniejszy przeciwnik lasu (ok. 14,5 studa z koroną, 12,8 bez niej; gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/straznik_gaju.py --wyj <folder> --klip umiejetnosc

Opis z danych walki (tools/walka/dane_walki.json, tam pod id „straznik_lasu”): wysoki kolos z kamienia i splecionego
drewna, z koroną z gałęzi, korzeniami zamiast stóp i świecącym zielonym kryształem w piersi. Umiejętność: uścisk
korzeni (magiczne korzenie unieruchamiają).

Wybór szkieletu: własne kości (typ „stwor”), jak Leśny Troll. Zasady obrotów jak w R15 (osie kości równoległe do osi
modelu, rx < 0 unosi zwisającą rękę do przodu, rz > 0 odchyla ją w stronę +X, dla tułowia i głowy rx > 0 = skłon).

Sylwetka: wyprostowany, dostojny kolos. Wąskie biodra i szeroki tułów w kształcie odwróconego klina, wielkie głazy
na barkach, długie ręce z kamiennymi przedramionami i pięściami przy kolanach, nogi z kamiennych ud i plecionych
pni, które u dołu rozchodzą się w korzenie leżące na ziemi. Kanciasta głowa (2,8 studa szerokości) z ciężkimi
brwiami, świecącymi oczami i kamienną szczęką z brodą z korzonków; na głowie korona z gałęzi z liśćmi. W piersi zielony kryształ
w kamiennej oprawie, od którego biegną cztery świecące żyłki (pulsują: wysuwają się z rowków i chowają).

Szkielet: Root > Biodra > {Tulow > {Glowa > {Szczeka, Powieki, Korona}; Krysztal; Zgasly; Blask;
RamieL > PrzedramieL > DlonL; RamieP > …; K1A > K1B > K1C … K5A > K5B > K5C}; UdoL > GolenL > StopaL; UdoP > …}.
L = lewa = +X, P = prawa = −X.
- Krysztal: świecący kryształ (pulsuje przesunięciem i obrotem — bez kanału skali). Zgasly: ten sam kryształ
  w szarym kolorze, schowany w tułowiu za świecącym; w upadku zamieniają się miejscami (kryształ „gaśnie”).
- Blask: cztery świecące żyłki w rowkach piersi; cofnięte o 0,08 chowają się pod powierzchnią (pulsowanie).
- Powieki: kamienne płytki schowane w głowie nad oczami; zjeżdżają na oczy (mrugnięcie, oczy gasną w upadku).
- K1A…K5C: pięć korzeni umiejętności, każdy z trzech członów jak teleskop (A gruby, B środkowy, C szpic). Poza
  umiejętnością cały teleskop jest schowany w kamiennym tułowiu (rodzic: Tulow), więc nie widać go w żadnym
  ujęciu ani klipie. W umiejętności, gdy pięści wbijają się w ziemię, korzenie w jednej klatce przenoszą się pod
  ziemię przed strażnikiem (wtedy ich klucze są liczone tak, żeby stały w miejscu w świecie, mimo ruchu tułowia),
  wyrastają człon po członie, zaciskają się, chowają z powrotem pod ziemię i wracają do tułowia.

Paleta (5 rodzin + akcent): kamień (trzy odcienie ciepłej szarości), drewno (dwa brązy), mech (dwie zielenie),
ciemna szczelina (oczodoły, rowki, usta), AKCENT: świecąca zieleń kryształu, oczu i żyłek (z jasnym odblaskiem);
zgaszony kryształ jest szarozielony.

Klipy (30 kl./s; patrzy w +Z i w tę stronę atakuje):
  idle (pętla 2,4 s), ruch (powolny ciężki chód, pętla 2 s), atak (cios młotem z pięści z prawego barku, 1,4 s),
  umiejetnosc (uścisk korzeni, 3 s), trafienie (0,67 s), unik (1 s), upadek (rozsypuje się na głazy, 2,67 s),
  ryk (po wygranej, pętla 2 s).
Klipy poza idle mają klucz w każdej klatce (funkcje _sekwencja, ruch, _upadek): stopy stoją płasko na ziemi,
korzenie umiejętności stoją w miejscu, a głazy upadku nie wchodzą w ziemię. Zmiany rób w pozach kluczowych w tym
pliku, nie w Blenderze.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import contextlib
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "straznik_gaju"

PALETA = {
    "kamien": "858074", "kamien_jasny": "ADA593", "kamien_ciemny": "57524C",
    "drewno": "8E5B32", "drewno_ciemne": "573620",
    "mech": "7DAE3C", "mech_ciemny": "4B7B2C",
    "szczelina": "2B2428",
    "krysztal": "36EE4E", "krysztal_jasny": "D2FFC8", "krysztal_zgasly": "4A5D54",
}

# ------------------------------------------------------------------------------------------- wymiary (studs, spoczynek)
X_NOGI, Y_KOSTKA, Y_KOLANO, Y_BIODRO = 1.35, 1.0, 3.0, 5.0
TULOW_Y = 6.4
TUL_DOL, TUL_GORA, TUL_D = 6.2, 10.5, 3.0          # tułów: od pasa do barków, głębokość
TUL_SZ_DOL, TUL_SZ_GORA = 3.9, 5.4                 # szerokość w pasie i w barkach (odwrócony klin)
X_BARK, Y_BARK, Y_LOKIEC, Y_NADG = 3.3, 9.7, 7.2, 4.9
SZYJA = (0.0, 10.35, 0.25)
GLOWA = (2.4, 2.1, 2.2)
GLOWA_SR = (0.0, 1.05, 0.2)
GL_C = (0.0, SZYJA[1] + GLOWA_SR[1], SZYJA[2] + GLOWA_SR[2])     # środek głowy (0, 11,4, 0,45)
Z_TWARZ = GL_C[2] + GLOWA[2] / 2                                  # przód twarzy 1,55
Y_OCZY = 11.45
SZCZEKA = (0.0, 10.62, 0.8)                                       # zawias szczęki
KORONA = (0.0, GL_C[1] + GLOWA[1] / 2, GL_C[2])                   # środek czubka głowy
KRYSZTAL = (0.0, 8.4, 1.8)
ZGASLY_Z = -1.3                                                   # zgaszony kryształ siedzi 1,3 za świecącym
MIEDNICA = ((0.0, 5.7, 0.0), (3.9, 1.8, 2.8))                     # środek i rozmiar miednicy
GNIAZDO = (0.0, 6.9, -0.15)                                        # staw korzeni schowanych w tułowiu

# Głowa i korona są powiększone o SG względem szyi (przegląd: przy 2,4 studa twarz była za mała na telefon i jak
# na komiksowy styl gry). Bryły głowy zostają opisane w „starych” liczbach powyżej, a skalę daje układ lokalny;
# stawy szczęki, powiek i korony liczy _sg().
SG = 1.15


def _sg(v):
    """Punkt głowy po powiększeniu o SG względem stawu szyi."""
    return tuple(SZYJA[i] + SG * (v[i] - SZYJA[i]) for i in range(3))


ZAMKNIETE = (0.0, -0.45 * SG, 0.4 * SG)                           # przesunięcie powiek: oczy zamknięte
PRZYMKNIETE = (0.0, -0.25 * SG, 0.4 * SG)                         # oczy zmrużone (trafienie, osiadanie)

# korzenie umiejętności: kąt wokół środka uścisku (0 = dalej od strażnika), odległość, mnożnik wysokości.
# Pierścień jest szeroki (2,4 studa), żeby korzenie stały osobno i zaginały się nad środkiem jak palce dłoni
# (przy 1,7 studa zlewały się w „płot” z brązowych słupków).
UCISK = (0.0, 6.6)                                                 # środek uścisku (x, z) przed strażnikiem
KORZENIE_U = ((0, 2.4, 1.0), (72, 2.35, 0.9), (144, 2.45, 0.95), (216, 2.45, 0.92), (288, 2.35, 0.88))
KA, KB, KC = 2.0, 1.9, 2.0                                        # wysokości członów A, B, C
KB_WYS, KC_WYS = 1.75, 1.75                                       # o ile wysuwa się B z A i C z B
POD_ZIEMIA = -2.5        # staw A pod ziemią: szpic C na −0,47 (obrys komiksowy szpica w renderze sięga ok. 0,3 wyżej)
NAD_ZIEMIA = -0.45                                                # staw A po wyrośnięciu (kołnierz ziemi leży na ziemi)


def _minus(v):
    return (-v[0], -v[1], -v[2])


def _obrot_na(kier):
    """(rx, 0, rz): obrót, który kieruje oś +Y w stronę wektora kier (kolejność Ry·Rx·Rz, ry = 0)."""
    n = math.sqrt(sum(v * v for v in kier))
    x, y, z = (v / n for v in kier)
    c = math.asin(max(-1.0, min(1.0, -x)))
    a = math.atan2(z / math.cos(c), y / math.cos(c))
    return (math.degrees(a), 0.0, math.degrees(c))


def _belka(p, nazwa, a, b, w0, w1, kolor, mat="matowy", faza=0.0):
    """Zwężająca się belka (ostrosłup o kwadratowym przekroju) od punktu a (szerokość w0) do b (szerokość w1)."""
    d = tuple(b[i] - a[i] for i in range(3))
    dl = math.sqrt(sum(v * v for v in d))
    sr = tuple((a[i] + b[i]) / 2 for i in range(3))
    p.ostroslup(nazwa, sr, (w0, dl, w0), kolor, mat, rot=_obrot_na(d), gora=(w1, w1), faza=faza)


def _galaz(p, nazwa, punkty, szer, kolor="drewno"):
    """Gałąź z odcinków; każdy następny zaczyna się trochę wcześniej (zakładka), żeby załamania nie miały szczelin."""
    for i in range(len(punkty) - 1):
        a, b = punkty[i], punkty[i + 1]
        if i:
            pa = punkty[i - 1]
            a = tuple(a[j] + (pa[j] - a[j]) * 0.12 for j in range(3))
        _belka(p, "%s %d" % (nazwa, i), a, b, szer[i], szer[i + 1], kolor)


def _mech(p, nazwa, pos, size, rot=(0, 0, 0)):
    """Poducha mchu: płaski ciemny klocek i dwie jaśniejsze kępki na wierzchu."""
    w, h, d = size
    with p.uklad(pos=pos, obrot=rot):
        p.blok(nazwa, (0, 0, 0), size, "mech_ciemny", "matowy", faza=min(0.1, h * 0.3))
        p.blok(nazwa + " kepa 1", (-w * 0.18, h / 2 + 0.04, d * 0.1), (w * 0.5, 0.12, d * 0.55), "mech", "matowy",
               faza=0.04)
        p.blok(nazwa + " kepa 2", (w * 0.22, h / 2 + 0.03, -d * 0.15), (w * 0.4, 0.1, d * 0.45), "mech", "matowy",
               faza=0.03)


def _liscie(p, nazwa, pos, n=3, r=0.32, obrot=(0, 0, 0)):
    """Kępka liści jak w klockowym drzewie: kilka grubych, lekko obróconych kostek listowia wokół punktu (cienkie
    listki z obrysem komiksowym zamieniały się w czarne kreski)."""
    with p.uklad(pos=pos, obrot=obrot):
        for i in range(n):
            a = 360.0 * i / n + 20
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            p.blok("%s %d" % (nazwa, i), (s * r * 0.45, 0.08 * (i % 2), c * r * 0.45), (r * 0.9, r * 0.6, r * 0.9),
                   "mech" if i % 2 == 0 else "mech_ciemny", "matowy", rot=(8 * (i % 2), a, 10), faza=r * 0.12)


def _klejnot(p, nazwa, pos, w, h, kolor, mat):
    """Kryształ: dwa ostrosłupy złożone podstawami (romb z przodu, krawędź skierowana do widza)."""
    with p.uklad(pos=pos, obrot=(0, 45, 0)):
        p.ostroslup(nazwa + " gora", (0, h / 4, 0), (w, h / 2, w), kolor, mat, gora=(0.0, 0.0), faza=0.0)
        p.ostroslup(nazwa + " dol", (0, -h / 4, 0), (w, h / 2, w), kolor, mat, rot=(180, 0, 0), gora=(0.0, 0.0),
                    faza=0.0)


# =========================================================================================================== model
def zbuduj():
    p = Postac(ID, "Strażnik Gaju", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Biodra", "Root", staw=(0, Y_BIODRO, 0), czesc=MIEDNICA[1], srodek=(0, MIEDNICA[0][1] - Y_BIODRO, 0))
    p.kosc("Tulow", "Biodra", staw=(0, TULOW_Y, 0), czesc=(TUL_SZ_GORA, TUL_GORA - TUL_DOL, TUL_D),
           srodek=(0, (TUL_DOL + TUL_GORA) / 2 - TULOW_Y, 0), dl=1.6)
    p.kosc("Glowa", "Tulow", staw=SZYJA, czesc=tuple(v * SG for v in GLOWA), srodek=tuple(v * SG for v in GLOWA_SR))
    p.kosc("Szczeka", "Glowa", staw=_sg(SZCZEKA), czesc=(1.9 * SG, 0.55 * SG, 1.0 * SG),
           srodek=(0, -0.17 * SG, 0.45 * SG), dl=0.4)
    p.kosc("Powieki", "Glowa", staw=_sg((0, Y_OCZY, Z_TWARZ)), dl=0.3)
    p.kosc("Korona", "Glowa", staw=_sg(KORONA), dl=0.7)
    p.kosc("Krysztal", "Tulow", staw=KRYSZTAL, dl=0.5)
    p.kosc("Zgasly", "Tulow", staw=(0, KRYSZTAL[1], KRYSZTAL[2] + ZGASLY_Z), dl=0.5)
    p.kosc("Blask", "Tulow", staw=(0, KRYSZTAL[1], TUL_D / 2), dl=0.3)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        x = zn * X_BARK
        p.kosc("Ramie" + s, "Tulow", staw=(x, Y_BARK, 0), czesc=(1.35, 2.5, 1.35), srodek=(0, -1.25, 0))
        p.kosc("Przedramie" + s, "Ramie" + s, staw=(x, Y_LOKIEC, 0), czesc=(2.0, 2.3, 1.9), srodek=(0, -1.15, 0))
        p.kosc("Dlon" + s, "Przedramie" + s, staw=(x, Y_NADG, 0), czesc=(2.1, 1.5, 2.0), srodek=(0, -0.8, 0.05))
    for s, zn in (("L", 1.0), ("P", -1.0)):
        x = zn * X_NOGI
        p.kosc("Udo" + s, "Biodra", staw=(x, Y_BIODRO, 0), czesc=(2.1, 2.2, 2.1), srodek=(0, -0.85, 0))
        p.kosc("Golen" + s, "Udo" + s, staw=(x, Y_KOLANO, 0), czesc=(1.85, 2.3, 1.85), srodek=(0, -0.98, 0))
        p.kosc("Stopa" + s, "Golen" + s, staw=(x, Y_KOSTKA, 0), czesc=(2.0, 1.0, 2.0), srodek=(0, -0.5, 0))
    for i in range(len(KORZENIE_U)):
        n = "K%d" % (i + 1)
        p.kosc(n + "A", "Tulow", staw=GNIAZDO, dl=0.5)
        p.kosc(n + "B", n + "A", staw=GNIAZDO, dl=0.4)
        p.kosc(n + "C", n + "B", staw=GNIAZDO, dl=0.3)

    _stopy(p)
    _nogi(p)
    _miednica(p)
    _tulow(p)
    _krysztal(p)
    _glowa(p)
    _korona(p)
    _rece(p)
    _korzenie(p)
    _przygotuj_punkty(p)

    # punkty zaczepienia dla gry: korzeń (ziemia pod środkiem), tabliczka nad koroną, kryształ (poświata, cel
    # trafień), pięści (fala uderzenia w umiejętności), środek uścisku korzeni (efekt unieruchomienia)
    p.zaczep("RootAttachment", "Biodra", (0, -Y_BIODRO, 0))
    p.zaczep("GlowaAttachment", "Korona", (0, 2.2, 0))
    p.zaczep("KrysztalAttachment", "Krysztal", (0, 0, 0.75))
    p.zaczep("PiescLAttachment", "DlonL", (0, -1.55, 0.05))
    p.zaczep("PiescPAttachment", "DlonP", (0, -1.55, 0.05))
    p.zaczep("KorzenieAttachment", "Biodra", (UCISK[0], -Y_BIODRO, UCISK[1]))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


SLABOSCI = [
    "Kości strażnika nie są R15 (własny szkielet, 37 kości razem z 15 kośćmi korzeni umiejętności) — klipy "
    "importuje się na własny rig; import do Roblox Studio nie był testowany.",
    "Korzenie umiejętności poza klipem siedzą schowane w kamiennym tułowiu i w jednej klatce przenoszą się pod "
    "ziemię przed strażnikiem (i z powrotem). Roblox odtwarza klip 30 kl./s z przejściami między klatkami, więc "
    "w grze w 60 kl./s przez jedną klatkę obrazu korzenie mogą mignąć w połowie drogi; przerwanie umiejętności "
    "innym klipem (np. trafienie z wyższym priorytetem) przeciągnie je przez nogi w czasie przejścia. Dla "
    "pewności w grze: umiejętności nie przerywać albo efekt korzeni zrobić osobnym modelem.",
    "Świecenie (kryształ, oczy, żyłki) to materiał świecący w Blenderze — w Roblox trzeba je dorobić (Neon, "
    "PointLight albo SurfaceAppearance z mapą emisji z tekstury-palety). Gaśnięcie kryształu w upadku to zamiana "
    "dwóch kryształów (świecący chowa się w tułów, szary wysuwa) i kamienne powieki na oczach, a nie zmiana "
    "materiału.",
    "Pulsowanie kryształu to tylko przesunięcie i obrót (bez skali): kryształ wysuwa się o 0,1 i obraca, żyłki "
    "chowają się w rowki i wysuwają. Z daleka to subtelne — mocniejszy puls najlepiej dodać w grze światłem.",
    "Bryły są sztywno przypięte do kości (jedna siatka na kość): głazy na barkach są kulami ze środkiem w stawie "
    "barku i stale lekko wchodzą w tułów; w głębokim przysiadzie umiejętności brzuch dotyka ud.",
    "Upadek: głazy (głowa, korona, ręce, tułów, miednica, uda) spadają po prostych torach z przyspieszeniem i "
    "lekkim odbiciem, bez toczenia; pnie goleni z korzeniami-stopami zostają na miejscu jak dwa pniaki. Głazy "
    "częściowo się przenikają w stosie.",
    "Chód jest w miejscu (stopy ślizgają się względem ziemi); w uniku całe ciało przesuwa się w bok razem ze "
    "stopami (ciężki odskok bez kroku).",
    "Wspólny kadr filmów obejmuje korzenie umiejętności przed strażnikiem i stos głazów z upadku, więc w filmach "
    "strażnik zajmuje ok. 2/3 wysokości kadru; bliższe ujęcia: plansza i kadr bohaterski.",
    "Kolizje sprawdzane w przybliżeniu (wierzchołki i środki krawędzi brył w każdej klatce każdego klipu): ręce, "
    "pięści i przedramiona nie wchodzą w głowę, tułów ani miednicę (oprócz głazu barku osadzonego na stałe), "
    "korzenie umiejętności nie wchodzą w ciało ani pięści. Uda i brzuch, korona i dłonie w ryku oraz korzenie "
    "między sobą nie były sprawdzane — zaciśnięte szpice korzeni stykają się nad środkiem uścisku.",
    "Wzrost z koroną to ok. 14,5 studa (głowa powiększona przy przeglądzie o 15% dla czytelności twarzy) — "
    "odrobinę ponad zakładane 13–14 studów.",
    "Atak: z kamery 3/4 trafienie (kl. 17) widać jako pięść wysuniętą ku widzowi na wysokości piersi gracza; "
    "w zamachu lewa pięść jest przed brzuchem (bez przenikania).",
    "Klipy to szkice (0,7–3 s), nie gotowa animacja; twarz nie ma mimiki poza szczęką i powiekami.",
]


# ---------------------------------------------------------------------------------------------------------- bryły
def _stopy(p):
    """Stopy z korzeni: rozszerzony pniak i sześć korzeni, które schodzą łukiem na ziemię."""
    for s, zn in (("L", 1.0), ("P", -1.0)):
        X = zn * X_NOGI
        with p.na("Stopa" + s, pos=_minus(p.staw("Stopa" + s))):
            p.stozek("Pniak", (X, 0.66, 0), (2.05, 0.9, 2.05), "drewno", "matowy", gora=0.74, segm=8)
            p.walec("Pniak pas", (X, 0.98, 0), (1.62, 0.16, 1.62), "drewno_ciemne", "matowy", segm=8, faza=0.0)
            # kąt (0 = do przodu, + na zewnątrz), długość
            for i, (a, dl) in enumerate(((-28, 1.95), (12, 2.15), (55, 1.95), (100, 1.8), (150, 1.75), (205, 1.6))):
                c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
                kier = (zn * sn, c)
                p0 = (X + 0.6 * kier[0], 0.52, 0.6 * kier[1])
                p1 = (X + 1.12 * kier[0], 0.27, 1.12 * kier[1])
                p2 = (X + dl * kier[0], 0.065, dl * kier[1])
                _belka(p, "Korzen %d" % i, p0, p1, 0.56, 0.38, "drewno_ciemne")
                _belka(p, "Korzen %d koniec" % i, p1, p2, 0.38, 0.1, "drewno_ciemne")
            _mech(p, "Mech stopa", (X + zn * 0.35, 1.12, -0.35), (0.8, 0.14, 0.7))


def _srednica_pnia(y):
    """Średnica goleni (pień zwężający się do góry) na wysokości y."""
    return 1.85 - 0.48 * (y - 0.87) / 2.3


def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        X = zn * X_NOGI
        with p.na("Golen" + s, pos=_minus(p.staw("Golen" + s))):
            p.stozek("Pien", (X, 2.02, 0), (1.85, 2.3, 1.85), "drewno", "matowy", gora=0.74, segm=8)
            for i, y in enumerate((1.45, 2.55)):
                d = _srednica_pnia(y) + 0.07
                p.walec("Splot %d" % i, (X, y, 0), (d, 0.22, d), "drewno_ciemne", "matowy", segm=8, faza=0.0)
            # ukośne pędy oplatające pień (z przodu i z tyłu)
            for zk in (1, -1):
                for j, (y, rz) in enumerate(((1.95, 32), (2.95, -30))):
                    d = _srednica_pnia(y)
                    p.blok("Ped %d %d" % (zk, j), (X, y, zk * (d / 2 + 0.01)), (0.75, 0.13, 0.08), "drewno_ciemne",
                           "matowy", rot=(0, 0, rz * zk), faza=0.0)
            p.kula("Kolano", (X, 3.08, 0.5), (1.2, 1.0, 0.95), "kamien_jasny", "matowy", segm=8)
        with p.na("Udo" + s, pos=_minus(p.staw("Udo" + s))):
            p.blok("Udo", (X, 4.15, 0), (2.1, 2.2, 2.1), "kamien", faza=0.2)
            p.blok("Udo plyta", (X + zn * 0.15, 4.4, 1.03), (1.25, 1.1, 0.1), "kamien_jasny", "matowy", faza=0.04)
            p.blok("Udo rysa", (X - zn * 0.55, 3.95, 1.07), (0.07, 0.9, 0.05), "szczelina", "matowy", faza=0.0)
            p.blok("Udo rysa bok", (X + zn * 1.07, 4.1, 0.2), (0.05, 1.0, 0.07), "szczelina", "matowy", faza=0.0)
            p.blok("Udo pas", (X, 3.45, 0), (2.16, 0.24, 2.16), "drewno_ciemne", "matowy", faza=0.03)
            _mech(p, "Mech udo", (X + zn * 0.85, 5.0, 0.2), (0.6, 0.2, 1.2), rot=(0, 0, -zn * 20))


def _miednica(p):
    (cx, cy, cz), (w, h, d) = MIEDNICA
    with p.na("Biodra", pos=_minus(p.staw("Biodra"))):
        p.blok("Miednica", (cx, cy, cz), (w, h, d), "kamien", faza=0.2)
        p.blok("Pas", (0, 6.28, 0), (w + 0.06, 0.42, d + 0.06), "drewno", "matowy", faza=0.04)
        # splot pasa: trzy ciemniejsze sploty z przodu i z tyłu (wystają 0,04)
        for zk in (1, -1):
            for i, x in enumerate((-1.2, 0.0, 1.2)):
                p.blok("Splot pasa %d %d" % (zk, i), (x, 6.28, zk * (d / 2 + 0.05)), (0.5, 0.3, 0.06),
                       "drewno_ciemne", "matowy", rot=(0, 0, 25 if i % 2 else -25), faza=0.03)
        p.blok("Miednica plyta", (0, 5.35, d / 2 + 0.02), (1.6, 0.8, 0.08), "kamien_jasny", "matowy", faza=0.03)
        p.blok("Miednica rysa", (0.9, 5.45, d / 2 + 0.025), (0.06, 0.7, 0.05), "szczelina", "matowy", faza=0.0)
        _mech(p, "Mech pas", (-1.2, 6.55, 1.0), (1.1, 0.16, 0.9))
        _mech(p, "Mech miednica tyl", (0.6, 5.55, -d / 2 - 0.06), (1.4, 0.8, 0.16))


def _tulow(p):
    def pol_szer(y):
        return (TUL_SZ_DOL + (TUL_SZ_GORA - TUL_SZ_DOL) * (y - TUL_DOL) / (TUL_GORA - TUL_DOL)) / 2

    zf = TUL_D / 2
    with p.na("Tulow", pos=_minus(p.staw("Tulow"))):
        p.ostroslup("Tulow", (0, (TUL_DOL + TUL_GORA) / 2, 0), (TUL_SZ_DOL, TUL_GORA - TUL_DOL, TUL_D), "kamien",
                    gora=(TUL_SZ_GORA, TUL_D), faza=0.2)
        # pierś: dwie płyty kamienia (jaśniejsze) i rysa pośrodku nad kryształem
        for zn in (1, -1):
            p.blok("Piers", (zn * 1.62, 9.85, zf + 0.06), (1.55, 1.05, 0.2), "kamien_jasny", faza=0.06,
                   rot=(0, 0, -zn * 5))
            p.blok("Piers rysa", (zn * 1.3, 9.75, zf + 0.175), (0.05, 0.55, 0.05), "szczelina", "matowy", faza=0.0,
                   rot=(0, 0, zn * 20))
        # splecione drewno w pasie: szeroka opaska z ukośnym splotem
        y_op = 6.68
        sz = 2 * pol_szer(y_op) + 0.06
        p.blok("Opaska", (0, y_op, 0), (sz, 0.48, TUL_D + 0.06), "drewno", "matowy", faza=0.04)
        for zk in (1, -1):
            for i, x in enumerate((-1.45, -0.5, 0.5, 1.45)):
                p.blok("Splot opaski %d %d" % (zk, i), (x, y_op, zk * (zf + 0.06)), (0.6, 0.34, 0.06),
                       "drewno_ciemne", "matowy", rot=(0, 0, 25 if i % 2 else -25), faza=0.03)
        # rysa na brzuchu
        p.blok("Rysa", (-1.3, 7.5, zf + 0.02), (0.07, 0.75, 0.05), "szczelina", "matowy", rot=(0, 0, 14), faza=0.0)
        # pnącze z prawego barku w dół po piersi (obok kryształu) — z liśćmi; łamie symetrię „robota”
        _galaz(p, "Pnacze piers", [(-2.55, 10.45, 0.9), (-2.0, 10.0, 1.86), (-1.45, 9.05, 1.66), (-1.6, 7.9, 1.6),
                                   (-1.3, 6.95, 1.6)], [0.3, 0.27, 0.24, 0.2, 0.14], "drewno")
        _liscie(p, "Pnacze liscie", (-1.75, 9.4, 1.82), n=3, r=0.3, obrot=(80, 0, 0))
        _liscie(p, "Pnacze liscie 2", (-1.45, 7.6, 1.72), n=2, r=0.26, obrot=(80, 0, 0))
        for zn in (1, -1):
            for i, (y, z) in enumerate(((8.2, 0.6), (9.2, -0.5))):
                pw = pol_szer(y)
                p.blok("Rysa bok %d" % i, (zn * (pw + 0.01), y, z), (0.05, 0.9, 0.07), "szczelina", "matowy",
                       rot=(0, 0, -zn * 10), faza=0.0)
        # plecy: splecione pnącza na krzyż, płyty kamienia, mech i młody pęd
        _belka(p, "Pnacze plecy 1", (-2.2, 10.2, -zf - 0.06), (1.5, 6.9, -zf - 0.06), 0.3, 0.24, "drewno")
        _belka(p, "Pnacze plecy 2", (2.2, 10.2, -zf - 0.08), (-1.5, 6.9, -zf - 0.08), 0.3, 0.24, "drewno_ciemne")
        p.blok("Plecy plyta", (-1.0, 8.0, -zf - 0.03), (1.3, 1.2, 0.1), "kamien_jasny", "matowy", faza=0.04)
        p.blok("Plecy plyta 2", (1.15, 9.45, -zf - 0.03), (1.2, 0.9, 0.1), "kamien_jasny", "matowy", faza=0.04)
        _mech(p, "Mech plecy", (0.9, 7.6, -zf - 0.1), (1.3, 1.1, 0.2))
        _mech(p, "Mech plecy 2", (-1.3, 9.9, -zf - 0.08), (1.1, 0.7, 0.18))
        _galaz(p, "Ped plecy", [(1.0, 9.9, -zf - 0.1), (1.3, 10.6, -zf - 0.55), (1.2, 11.1, -zf - 0.75)],
               [0.22, 0.14, 0.06])
        _liscie(p, "Ped liscie", (1.25, 10.95, -zf - 0.7), n=3, r=0.3)
        # mech na barkach (na tułowiu, nad głazami barków — głazy obracają się pod nim)
        for zn in (1, -1):
            _mech(p, "Mech bark", (zn * 3.25, 10.82, 0.05), (1.15, 0.2, 1.35), rot=(0, 0, -zn * 8))
        _mech(p, "Mech kark", (0, 10.55, -0.95), (2.6, 0.2, 0.9))
        # rama kryształu: ciemne gniazdo w kształcie rombu, kamienne krawędzie, rowki pod żyłkami blasku
        kx, ky = KRYSZTAL[0], KRYSZTAL[1]
        p.blok("Gniazdo", (kx, ky, zf + 0.015), (1.6, 1.6, 0.03), "szczelina", "matowy", rot=(0, 0, 45), faza=0.0)
        for sx in (1, -1):
            for sy in (1, -1):
                m = 0.5
                p.blok("Rama %d %d" % (sx, sy), (kx + sx * m, ky + sy * m, zf + 0.15), (1.75, 0.3, 0.3),
                       "kamien_jasny", rot=(0, 0, -45 * sx * sy), faza=0.06)
                r0, r1 = 1.02, 1.62
                dx, dy = sx * 0.7071, sy * 0.7071
                p.blok("Rowek %d %d" % (sx, sy), (kx + dx * (r0 + r1) / 2, ky + dy * (r0 + r1) / 2, zf + 0.015),
                       (0.24, r1 - r0 + 0.1, 0.03), "szczelina", "matowy", rot=(0, 0, -45 * sx * sy), faza=0.0)


def _krysztal(p):
    with p.na("Krysztal"):
        _klejnot(p, "Krysztal", (0, 0, 0), 0.95, 1.7, "krysztal", "swiecacy")
        # odblask: mały jasny klejnot wtopiony w lewą górną ściankę
        _klejnot(p, "Krysztal odblask", (-0.17, 0.34, 0.18), 0.3, 0.42, "krysztal_jasny", "swiecacy")
    with p.na("Zgasly"):
        _klejnot(p, "Zgasly", (0, 0, 0), 0.95, 1.7, "krysztal_zgasly", "zwykly")
    with p.na("Blask"):
        for sx in (1, -1):
            for sy in (1, -1):
                r0, r1 = 1.05, 1.6
                dx, dy = sx * 0.7071, sy * 0.7071
                p.ostroslup("Zylka %d %d" % (sx, sy), (dx * (r0 + r1) / 2, dy * (r0 + r1) / 2, 0.0),
                            (0.16, r1 - r0, 0.1), "krysztal", "swiecacy", rot=(0, 0, -45 * sx * sy + (0 if sy > 0 else 180)),
                            gora=(0.05, 0.1), faza=0.0)


@contextlib.contextmanager
def _na_glowie(p, kosc, staw_przed):
    """Układ kości głowy (Glowa, Szczeka, Powieki) powiększony o SG: bryły podaje się w liczbach sprzed
    powiększenia — staw_przed to staw tej kości przed powiększeniem (None = bryły względem stawu)."""
    with p.na(kosc), p.uklad(skala=SG), p.uklad(pos=_minus(staw_przed) if staw_przed else (0, 0, 0)):
        yield


def _glowa(p):
    zf = Z_TWARZ
    with _na_glowie(p, "Glowa", SZYJA):
        p.blok("Glowa", GL_C, GLOWA, "kamien", faza=0.18)
        # ciężkie brwi w „V” (srogi, dostojny wyraz), czoło z rysą
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.58, 11.86, zf + 0.12), (1.15, 0.4, 0.42), "kamien_jasny", faza=0.08,
                   rot=(0, 0, zn * 13))
            # oczodół, świecące oko (akcent), jasny odblask
            p.blok("Oczodol " + s, (zn * 0.55, Y_OCZY, zf + 0.012), (0.66, 0.44, 0.04), "szczelina", "matowy",
                   faza=0.0, rot=(0, 0, zn * 9))
            p.blok("Oko " + s, (zn * 0.55, Y_OCZY - 0.02, zf + 0.04), (0.5, 0.26, 0.04), "krysztal", "swiecacy",
                   faza=0.0, rot=(0, 0, zn * 9))
            p.blok("Oko blysk " + s, (zn * 0.48, Y_OCZY + 0.0, zf + 0.065), (0.13, 0.09, 0.02), "krysztal_jasny",
                   "swiecacy", faza=0.0)
            # policzki: kamienne płyty po bokach nosa
            p.blok("Policzek " + s, (zn * 0.78, 10.95, zf + 0.03), (0.6, 0.45, 0.1), "kamien_jasny", "matowy",
                   faza=0.04)
            p.blok("Glowa rysa " + s, (zn * 1.215, 11.6, 0.6), (0.04, 0.8, 0.07), "szczelina", "matowy", faza=0.0)
        p.blok("Czolo rysa", (0.3, 12.2, zf + 0.02), (0.06, 0.4, 0.05), "szczelina", "matowy", rot=(0, 0, -20),
               faza=0.0)
        # kanciasty nos
        p.blok("Nos", (0, 11.0, zf + 0.2), (0.52, 0.5, 0.42), "kamien_jasny", faza=0.1)
        p.blok("Nos grzbiet", (0, 11.32, zf + 0.1), (0.34, 0.3, 0.22), "kamien_jasny", faza=0.06)
        # usta (widać je, gdy szczęka opada): ciemne wnętrze i rząd kamiennych zębów — schowane w szczęce
        p.blok("Usta", (0, 10.5, 1.22), (1.5, 0.36, 0.7), "szczelina", "matowy", faza=0.0)
        for i, x in enumerate((-0.45, -0.15, 0.15, 0.45)):
            p.blok("Zab %d" % i, (x, 10.6, 1.5), (0.22, 0.18, 0.14), "kamien_jasny", "matowy", faza=0.03)
        p.blok("Gardlo", (0, 10.4, 1.585), (0.8, 0.1, 0.03), "krysztal", "swiecacy", faza=0.0)

    # powieki: kamienne płytki schowane w głowie nad oczami; ZAMKNIETE przesuwa je na oczy (przód 1,65 > oko 1,63)
    with _na_glowie(p, "Powieki", None):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Powieka " + s, (zn * 0.55, 0.45, -0.33), (0.76, 0.54, 0.06), "kamien", "matowy",
                   rot=(0, 0, zn * 9), faza=0.0)

    with _na_glowie(p, "Szczeka", SZCZEKA):
        p.blok("Szczeka", (0, 10.45, 1.25), (1.9, 0.55, 1.0), "kamien", faza=0.12)
        p.blok("Usta linia", (0, 10.6, 1.765), (1.15, 0.07, 0.04), "szczelina", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kacik", (zn * 0.62, 10.56, 1.765), (0.18, 0.07, 0.04), "szczelina", "matowy",
                   rot=(0, 0, zn * 30), faza=0.0)
        p.blok("Podbrodek", (0, 10.32, 1.77), (0.9, 0.2, 0.06), "kamien_jasny", "matowy", faza=0.02)
        # broda z korzonków: pięć zwężających się pasm nad piersią (nie dotykają kryształu)
        for i, (x, dl, kol) in enumerate(((-0.62, 0.55, "drewno_ciemne"), (-0.32, 0.72, "drewno"),
                                          (0.0, 0.62, "drewno_ciemne"), (0.32, 0.75, "drewno"),
                                          (0.62, 0.5, "drewno_ciemne"))):
            _belka(p, "Broda %d" % i, (x, 10.24, 1.6), (x * 1.12, 10.24 - dl, 1.82), 0.26, 0.08, kol)
        _mech(p, "Mech broda", (0.25, 10.17, 1.55), (0.9, 0.12, 0.35))


def _korona(p):
    """Korona z gałęzi: splecione drewno wokół czubka głowy i siedem gałęzi (dwa duże „poroża” po bokach) z liśćmi.
    Z przodu mały świecący kryształ — ten sam akcent co w piersi."""
    # korona nie rośnie w górę razem z głową (wzrost zostaje ok. 14,5 studa): obręcz obejmuje powiększoną głowę,
    # a gałęzie rozchodzą się o SG szerzej (x, z), przy tej samej wysokości
    cx, cy, cz = KORONA
    w, d = GLOWA[0] * SG, GLOWA[2] * SG
    def liscie(p, nazwa, pos, n=3, r=0.32):
        _liscie(p, nazwa, (cx + (pos[0] - cx) * SG, pos[1], cz + (pos[2] - cz) * SG), n, r)

    with p.na("Korona", pos=_minus(KORONA)):
        _mech(p, "Mech glowa", (cx, cy + 0.02, cz - 0.05), (1.9 * SG, 0.14, 1.7 * SG))
        yb = cy - 0.12
        p.blok("Obrecz przod", (cx, yb, cz + d / 2 + 0.1), (w + 0.4, 0.36, 0.22), "drewno", "matowy", faza=0.05)
        p.blok("Obrecz tyl", (cx, yb, cz - d / 2 - 0.1), (w + 0.4, 0.36, 0.22), "drewno", "matowy", faza=0.05)
        for zn in (1, -1):
            p.blok("Obrecz bok", (zn * (w / 2 + 0.1), yb, cz), (0.22, 0.36, d + 0.2), "drewno", "matowy", faza=0.05)
        for i, x in enumerate((-0.8, 0.0, 0.8)):
            p.blok("Obrecz splot %d" % i, (x, yb, cz + d / 2 + 0.23), (0.4, 0.12, 0.04), "drewno_ciemne", "matowy",
                   rot=(0, 0, 35 if i % 2 else -35), faza=0.0)
        _klejnot(p, "Klejnot korony", (cx, yb + 0.12, cz + d / 2 + 0.32), 0.3, 0.5, "krysztal", "swiecacy")

        def g(nazwa, pkt, szer):
            _galaz(p, nazwa, [(cx + a * SG, cy + b, cz + c * SG) for a, b, c in pkt], szer)

        for zn, s in ((1, "L"), (-1, "P")):
            # duże poroże w bok i w górę, z odnogą
            g("Galaz duza " + s, [(zn * 0.8, -0.05, 0.05), (zn * 1.4, 0.65, 0.0), (zn * 1.95, 1.2, -0.08),
                                   (zn * 2.6, 1.36, -0.15)], [0.52, 0.42, 0.3, 0.12])
            g("Odnoga " + s, [(zn * 1.95, 1.2, -0.08), (zn * 1.8, 1.55, 0.0)], [0.26, 0.1])
            g("Odnoga dolna " + s, [(zn * 1.4, 0.65, 0.0), (zn * 2.1, 0.75, 0.45)], [0.26, 0.1])
            # mała gałązka z przodu i z tyłu
            g("Galaz przod " + s, [(zn * 0.5, -0.05, 0.72), (zn * 0.8, 0.6, 0.95), (zn * 0.9, 1.05, 1.1)],
              [0.32, 0.24, 0.1])
            g("Galaz tyl " + s, [(zn * 0.7, -0.05, -0.55), (zn * 1.15, 0.6, -1.0), (zn * 1.4, 1.0, -1.35)],
              [0.34, 0.25, 0.1])
            liscie(p, "Liscie duze " + s, (cx + zn * 2.45, cy + 1.33, cz - 0.12), n=3, r=0.58)
            liscie(p, "Liscie odnoga " + s, (cx + zn * 1.8, cy + 1.5, cz), n=2, r=0.48)
            liscie(p, "Liscie przod " + s, (cx + zn * 0.88, cy + 1.02, cz + 1.08), n=2, r=0.42)
            liscie(p, "Liscie tyl " + s, (cx + zn * 1.38, cy + 0.98, cz - 1.32), n=2, r=0.42)
        g("Galaz srodek", [(0.0, -0.05, -0.5), (0.12, 0.8, -0.8), (-0.1, 1.28, -1.05)], [0.36, 0.26, 0.1])
        liscie(p, "Liscie srodek", (cx - 0.08, cy + 1.26, cz - 1.02), n=3, r=0.48)


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        X = zn * X_BARK
        with p.na("Ramie" + s, pos=_minus(p.staw("Ramie" + s))):
            # głaz barku: środek w stawie — przy obrocie ręki obraca się w miejscu i nie wjeżdża w tułów ani głowę
            p.kula("Glaz barku", (X, Y_BARK, 0), (2.3, 2.1, 2.4), "kamien", "zwykly", segm=8)
            p.blok("Glaz rysa", (X + zn * 0.7, Y_BARK + 0.2, 0.92), (0.06, 0.6, 0.05), "szczelina", "matowy",
                   rot=(0, 0, 25), faza=0.0)
            p.walec("Ramie", (X, Y_BARK - 1.4, 0), (1.35, 2.3, 1.35), "drewno", "matowy", segm=8, faza=0.04)
            for i, y in enumerate((8.15, 7.5)):
                p.walec("Ramie splot %d" % i, (X, y, 0), (1.43, 0.2, 1.43), "drewno_ciemne", "matowy", segm=8,
                        faza=0.0)
            p.blok("Ramie ped", (X, 8.0, 0.69), (0.6, 0.12, 0.06), "drewno_ciemne", "matowy", rot=(0, 0, 35),
                   faza=0.0)
        with p.na("Przedramie" + s, pos=_minus(p.staw("Przedramie" + s))):
            # kamienne przedramię rozszerzone ku pięści (ostrosłup odwrócony)
            p.ostroslup("Przedramie", (X, Y_LOKIEC - 1.15, 0.05), (2.0, 2.3, 1.9), "kamien", rot=(180, 0, 0),
                        gora=(1.5, 1.45), faza=0.14)
            p.kula("Lokiec", (X, Y_LOKIEC - 0.05, -0.15), (1.3, 1.0, 1.2), "kamien_jasny", "matowy", segm=8)
            for i, y in enumerate((5.55, 6.2)):
                t = (Y_LOKIEC - y) / 2.3
                sw, sd = 1.5 + 0.5 * t + 0.07, 1.45 + 0.45 * t + 0.07
                p.blok("Przedramie splot %d" % i, (X, y, 0.05), (sw, 0.22, sd), "drewno", "matowy", faza=0.03)
            p.blok("Przedramie plyta", (X + zn * 0.95, 5.95, 0.05), (0.1, 0.9, 1.1), "kamien_jasny", "matowy",
                   rot=(0, 0, zn * 6), faza=0.03)
            _mech(p, "Mech przedramie", (X + zn * 0.3, 6.35, -0.75), (1.0, 0.7, 0.16), rot=(-8, 0, 0))
        with p.na("Dlon" + s, pos=_minus(p.staw("Dlon" + s))):
            p.blok("Piesc", (X, 4.1, 0.05), (2.1, 1.5, 2.0), "kamien_ciemny", faza=0.16)
            for i, x in enumerate((-0.66, -0.22, 0.22, 0.66)):
                p.blok("Kostka %d" % i, (X + x, 3.75, 1.09), (0.4, 0.5, 0.14), "kamien", "matowy", faza=0.05)
            p.blok("Kciuk", (X - zn * 1.1, 4.2, 0.55), (0.18, 0.75, 0.62), "kamien", "matowy", faza=0.05)
            p.blok("Piesc pas", (X, 4.68, 0.05), (2.16, 0.2, 2.06), "drewno_ciemne", "matowy", faza=0.03)


def _korzenie(p):
    """Korzenie umiejętności (teleskop A > B > C). Układ każdej kości: (0, 0, 0) = staw, człon rośnie w +Y."""
    for i in range(len(KORZENIE_U)):
        n = "K%d" % (i + 1)
        with p.na(n + "A"):
            p.ostroslup("Korzen A", (0, KA / 2, 0), (1.3, KA, 1.3), "drewno", "matowy", gora=(1.0, 1.0),
                        faza=0.06)
            _zylki(p, "Korzen A", 1.3, 1.0, KA, 0.0)
            p.blok("Korzen A sek", (0.55, 1.3, 0.1), (0.2, 0.4, 0.34), "drewno_ciemne", "matowy", faza=0.04)
            # kołnierz rozrytej ziemi u podstawy — po wyrośnięciu leży na ziemi
            for j in range(4):
                a = math.radians(45 + 90 * j + 17 * i)
                p.blok("Ziemia %d" % j, (0.78 * math.sin(a), 0.42, 0.78 * math.cos(a)), (0.62, 0.28, 0.44),
                       "kamien_ciemny" if j % 2 else "drewno_ciemne", "matowy", rot=(0, math.degrees(a), 8),
                       faza=0.06)
        with p.na(n + "B"):
            p.ostroslup("Korzen B", (0, KB / 2 + 0.02, 0), (0.95, KB, 0.95), "drewno", "matowy", gora=(0.7, 0.7),
                        faza=0.05)
            _zylki(p, "Korzen B", 0.95, 0.7, KB, 0.02, os="x")
            _belka(p, "Korzen B pęd", (0.35, 1.1, 0.0), (0.8, 1.5, 0.1), 0.18, 0.06, "drewno")
            _liscie(p, "Korzen B lisc", (0.82, 1.52, 0.1), n=2, r=0.26)
        with p.na(n + "C"):
            p.ostroslup("Korzen C", (0, KC / 2 + 0.03, 0), (0.7, KC, 0.7), "drewno", "matowy", gora=(0.12, 0.12),
                        faza=0.0)
            _belka(p, "Korzen C cierń", (-0.22, 0.6, 0.0), (-0.58, 0.92, 0.0), 0.15, 0.05, "drewno_ciemne")
            _belka(p, "Korzen C cierń 2", (0.16, 1.05, 0.1), (0.42, 1.3, 0.2), 0.12, 0.04, "drewno_ciemne")


def _zylki(p, nazwa, w0, w1, h, y0, os="z"):
    """Dwie świecące żyłki na przeciwnych ścianach członu korzenia (ostrosłup w0 → w1, wysokość h, podstawa na y0):
    magia strażnika, ten sam akcent co kryształ. Żyłka leży na pochyłej ścianie i wystaje ok. 0,04."""
    nach = math.degrees(math.atan((w0 - w1) / 2.0 / h))
    r = (w0 + w1) / 4 + 0.015
    for zn in (1, -1):
        if os == "z":
            p.blok("%s zylka %d" % (nazwa, zn), (0, y0 + h / 2, zn * r), (0.16, h * 0.72, 0.06), "krysztal",
                   "swiecacy", rot=(-zn * nach, 0, 0), faza=0.0)
        else:
            p.blok("%s zylka %d" % (nazwa, zn), (zn * r, y0 + h / 2, 0), (0.06, h * 0.72, 0.16), "krysztal",
                   "swiecacy", rot=(0, 0, zn * nach), faza=0.0)


# ---------------------------------------------------------------------------------------- geometria do animacji
ZERO = (0.0, 0.0, 0.0)
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
_PKT = {}           # kość -> punkty brył (wierzchołki) względem stawu, w osiach modelu (spoczynek)


def _T(R):
    return tuple(tuple(R[j][i] for j in range(3)) for i in range(3))


def _wierzcholki(c):
    """Wierzchołki bryły w jej własnym układzie (bez fazowania)."""
    sx, sy, sz = (v / 2 for v in c["s"])
    k = c["k"]
    if k in ("walec", "stozek"):
        g = c.get("gora", 1.0) if k == "stozek" else 1.0
        n = int(c.get("seg", 8))
        pkt = []
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            q = math.cos(math.pi / n)
            for y, f in ((-sy, 1.0), (sy, g)):
                pkt.append((sx * f * math.cos(a) / q, y, sz * f * math.sin(a) / q))
        return pkt
    if k == "kula":
        pkt = []
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                for e in (-1, 0, 1):
                    if a or b or e:
                        n = math.sqrt(a * a + b * b + e * e)
                        pkt.append((a * sx / n, b * sy / n, e * sz / n))
        return pkt
    if k == "ostroslup":
        gx, gz = (v / 2 for v in c["gora"])
        px, pz = c["pg"]
        return [(a * sx, -sy, b * sz) for a in (-1, 1) for b in (-1, 1)] + \
               [(px + a * gx, sy, pz + b * gz) for a in (-1, 1) for b in (-1, 1)]
    return [(a * sx, b * sy, e * sz) for a in (-1, 1) for b in (-1, 1) for e in (-1, 1)]


def _przygotuj_punkty(p):
    _PKT.clear()
    for c in p.czesci:
        R = macierz_obrotu(*c["r"])
        lst = _PKT.setdefault(c["kosc"], [])
        for v in _wierzcholki(c):
            q = razy_wektor(R, v)
            lst.append((c["p"][0] + q[0], c["p"][1] + q[1], c["p"][2] + q[2]))


def _fk(p, pz):
    """Kinematyka wprost pozy {kość: (obrót, przesunięcie)}: {kość: (obrót w świecie, staw w świecie)}."""
    W = {}
    for n, k in p.kosci.items():
        ob, pr = pz.get(n, (ZERO, ZERO))
        Rl = macierz_obrotu(*ob)
        if k["rodzic"] is None:
            W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
        else:
            Rp, tp = W[k["rodzic"]]
            st = p.kosci[k["rodzic"]]["staw"]
            d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
            W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))
    return W


def _punkty_w(W, kosc):
    R, t = W[kosc]
    for v in _PKT.get(kosc, ()):
        q = razy_wektor(R, v)
        yield (q[0] + t[0], q[1] + t[1], q[2] + t[2])


def _najnizej(W, kosci):
    return min(q[1] for n in kosci for q in _punkty_w(W, n))


def _lokalnie(p, W, n, Rw, tw):
    """(obrót, przesunięcie) kości n, przy którym ma w świecie obrót Rw i staw w tw (rodzic z W)."""
    k = p.kosci[n]
    Rp, tp = W[k["rodzic"]]
    st = p.kosci[k["rodzic"]]["staw"]
    RpT = _T(Rp)
    d = razy_wektor(RpT, tuple(tw[i] - tp[i] for i in range(3)))
    pr = tuple(d[i] - (k["staw"][i] - st[i]) for i in range(3))
    return katy_z_macierzy(mnoz(RpT, Rw)), pr


# kwaterniony (do spadania głazów w upadku)
def _kw(R):
    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        return ((R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s, 0.25 * s)
    if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        return (0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s, (R[2][1] - R[1][2]) / s)
    if R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        return ((R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s, (R[0][2] - R[2][0]) / s)
    s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
    return ((R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s, (R[1][0] - R[0][1]) / s)


def _z_kw(q):
    x, y, z, w = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def _slerp_R(Ra, Rb, t):
    a, b = _kw(Ra), _kw(Rb)
    c = sum(a[i] * b[i] for i in range(4))
    if c < 0:
        b, c = tuple(-v for v in b), -c
    if c > 0.9995:
        q = tuple(a[i] + (b[i] - a[i]) * t for i in range(4))
    else:
        th = math.acos(c)
        sa, sb = math.sin((1 - t) * th) / math.sin(th), math.sin(t * th) / math.sin(th)
        q = tuple(sa * a[i] + sb * b[i] for i in range(4))
    n = math.sqrt(sum(v * v for v in q))
    return _z_kw(tuple(v / n for v in q))


# ------------------------------------------------------------------------------------------- pozy i sekwencje
CIALO = None        # kości ciała (bez Root i bez korzeni umiejętności) — ustawiane w _klipy


def _pelna(pz):
    """Poza: {kość: (rx, ry, rz) albo {"obrot":…, "przes":…}} -> {kość: (obrót, przesunięcie)} dla całego ciała."""
    w = {n: (ZERO, ZERO) for n in CIALO}
    for n, v in pz.items():
        if isinstance(v, dict):
            w[n] = (tuple(v.get("obrot", ZERO)), tuple(v.get("przes", ZERO)))
        else:
            w[n] = (tuple(v), ZERO)
    return w


def _mieszaj(a, b, e):
    return {n: (tuple(a[n][0][i] + (b[n][0][i] - a[n][0][i]) * e for i in range(3)),
                tuple(a[n][1][i] + (b[n][1][i] - a[n][1][i]) * e for i in range(3))) for n in a}


def _postaw(p, pz, tryb="stopy", przypnij=False):
    """Stopy płasko (obrót stopy znosi obroty nóg), przypięcie stóp w miejscu (miednica przesuwa się w poziomie)
    i ziemia: tryb "stopy" — najniższy punkt stóp na y = 0; "min" — tylko nic nie schodzi pod ziemię."""
    if tryb == "brak":
        return pz
    W = _fk(p, pz)
    for s in ("L", "P"):
        Rg = W["Golen" + s][0]
        pz["Stopa" + s] = (katy_z_macierzy(_T(Rg)), pz["Stopa" + s][1])
    ob, pr = pz["Biodra"]
    if przypnij:
        W = _fk(p, pz)
        dx = sum(W["Stopa" + s][1][0] - p.kosci["Stopa" + s]["staw"][0] for s in ("L", "P")) / 2
        dz = sum(W["Stopa" + s][1][2] - p.kosci["Stopa" + s]["staw"][2] for s in ("L", "P")) / 2
        pr = (pr[0] - dx, pr[1], pr[2] - dz)
        pz["Biodra"] = (ob, pr)
    W = _fk(p, pz)
    if tryb == "stopy":
        dno = _najnizej(W, ("StopaL", "StopaP"))
    else:
        dno = min(0.0, _najnizej(W, CIALO))
    pz["Biodra"] = (ob, (pr[0], pr[1] - dno, pr[2]))
    return pz


def _klucze(k, f, pz, wyg="liniowo"):
    for n, (ob, pr) in pz.items():
        k.klucz(f, n, obrot=tuple(round(v, 3) for v in ob), przes=tuple(round(v, 4) for v in pr), wyg=wyg)


def _wygladz(t):
    return t * t * (3 - 2 * t)


def _sekwencja(k, czasy, pozy, wyg=None, tryb="stopy", przypnij=False, dodatek=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (łagodne wejście i wyjście; wyg={i: "liniowo"} — odcinek od
    pozy i jednostajnie, np. uderzenie). Po interpolacji: stopy płasko i na ziemi (_postaw), potem dodatek(f, pz)
    (np. korzenie umiejętności)."""
    p = k.postac
    pelne = [_pelna(pz) for pz in pozy]
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        e = t if (wyg or {}).get(i) == "liniowo" else _wygladz(t)
        pz = _postaw(p, _mieszaj(pelne[i], pelne[i + 1], e), tryb, przypnij)
        if dodatek:
            dodatek(f, pz)
        _klucze(k, f, pz)


def _puls(t, sila=1.0, faza=0.25, czestosc=2):
    """Pulsowanie kryształu i żyłek w chwili t (0…1 klipu): (przesunięcie kryształu z, obrót y, żyłki z)."""
    s = math.sin(2 * math.pi * (czestosc * t + faza))
    return 0.04 + 0.06 * s * sila, 14 * math.sin(2 * math.pi * t) * sila, -0.035 + 0.045 * s


def _z_pulsem(pz, t, sila=1.0, czestosc=2):
    kz, ky, bz = _puls(t, sila, czestosc=czestosc)
    pz["Krysztal"] = ((0.0, ky, 0.0), (0.0, 0.0, kz))
    pz["Blask"] = (ZERO, (0.0, 0.0, bz))
    return pz


# =============================================================================================== klipy
def _klipy(p):
    global CIALO
    CIALO = [n for n in p.kosci if n != "Root" and not (n.startswith("K") and n[1:-1].isdigit())]
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    ryk(p)


def idle(p, dl=72):
    """Spokojny, dostojny oddech (2,4 s): pierś unosi się, głowa powoli się rozgląda, korona lekko się kołysze,
    kryształ pulsuje dwa razy na pętlę (wysuwa się i obraca, żyłki wysuwają się z rowków), w połowie mrugnięcie."""
    k = p.klip("idle", dl, petla=True)
    k.cykl("Tulow", "obrot", (1.5, 0, 0), faza=0.0)
    k.cykl("Glowa", "obrot", (-1.5, 7, 0), faza=0.15)
    k.cykl("Szczeka", "obrot", (2, 0, 0), faza=0.4, srodek=(2, 0, 0))
    k.cykl("Korona", "obrot", (0, 0, 2.5), faza=0.35)
    k.cykl("RamieL", "obrot", (-2.5, 0, 1.5), faza=0.2, srodek=(0, 0, 2))
    k.cykl("RamieP", "obrot", (-2.5, 0, -1.5), faza=0.25, srodek=(0, 0, -2))
    k.cykl("PrzedramieL", "obrot", (-3, 0, 0), faza=0.3, srodek=(-4, 0, 0))
    k.cykl("PrzedramieP", "obrot", (-3, 0, 0), faza=0.35, srodek=(-4, 0, 0))
    k.cykl("Krysztal", "przes", (0, 0, 0.06), czestosc=2, faza=0.25, srodek=(0, 0, 0.04))
    k.cykl("Krysztal", "obrot", (0, 14, 0), faza=0.0)
    k.cykl("Blask", "przes", (0, 0, 0.045), czestosc=2, faza=0.25, srodek=(0, 0, -0.035))
    for f, v in ((0, ZERO), (44, ZERO), (47, ZAMKNIETE), (49, ZAMKNIETE), (53, ZERO), (dl, ZERO)):
        k.klucz(f, "Powieki", przes=v)
    return k


def ruch(p, dl=60):
    """Powolny, ciężki chód (2 s na dwa kroki): długie wahnięcia nóg, miednica skręca się i przenosi ciężar na nogę
    podporową, barki skręcają się odwrotnie, ręce wahają się nisko, głowa trzyma kierunek. Stopy płasko, stopa
    podporowa zawsze na ziemi (miednica opada przy szerokim kroku)."""
    k = p.klip("ruch", dl, petla=True)
    for f in range(dl + 1):
        t = f / float(dl)
        a = 2 * math.pi * t
        pz = _pelna({})
        for s, fs in (("L", 0.0), ("P", 0.5)):
            b = a + 2 * math.pi * fs
            kol = max(0.0, -math.sin(b - 0.6)) * 40
            pz["Udo" + s] = ((20 * math.sin(b), 0, 0), ZERO)
            pz["Golen" + s] = ((kol, 0, 0), ZERO)
        pz["Biodra"] = ((0, 6 * math.sin(a), 0), (0.14 * math.sin(a), 0, 0))
        pz["Tulow"] = ((5 + 1.5 * math.sin(2 * a), -9 * math.sin(a), -2.5 * math.sin(a)), ZERO)
        pz["Glowa"] = ((-4 - 1.5 * math.sin(2 * a), 4 * math.sin(a), 2 * math.sin(a)), ZERO)
        pz["Korona"] = ((1.5 * math.sin(2 * a + 1.0), 0, 2.5 * math.sin(a + 1.2)), ZERO)
        pz["Szczeka"] = ((2 + 1.5 * math.sin(2 * a), 0, 0), ZERO)
        pz["RamieL"] = ((-16 * math.sin(a), 0, 4), ZERO)
        pz["RamieP"] = ((16 * math.sin(a), 0, -4), ZERO)
        pz["PrzedramieL"] = ((-10 - 6 * math.sin(a), 0, 0), ZERO)
        pz["PrzedramieP"] = ((-10 + 6 * math.sin(a), 0, 0), ZERO)
        _z_pulsem(pz, t)
        _klucze(k, f, _postaw(p, pz, "stopy"))
    return k


def atak(p, dl=42):
    """Zwykły cios (1,4 s): odchylenie i skręt w prawo, prawa pięść zgięta wysoko za prawym barkiem (kl. 9–13,
    chwila zawieszenia), potem szybki młot z góry przed siebie z wykrokiem lewej nogi — trafienie na wysokości
    piersi gracza ok. 5 studów przed strażnikiem (kl. 17), krótkie dociśnięcie i zatrzymanie (kl. 17–21, czytelny
    moment trafienia), odbicie, powrót. Lewa ręka idzie w bok i w tył (przeciwwaga), nie zasłania kryształu.
    (Przegląd: wcześniej pięść kończyła nisko przy nodze i trafienie ginęło.)"""
    k = p.klip("atak", dl, petla=False)
    # pięść w górze NA ZEWNĄTRZ prawego barku (za głową przedramię z kamery 3/4 zasłaniało twarz)
    wziecie = {"Biodra": (0, -6, 0), "Tulow": (-8, -16, 4), "Glowa": (-5, 12, -2), "Szczeka": (12, 0, 0),
               "Korona": (-3, 0, 2),
               "RamieP": (-135, 0, -60), "PrzedramieP": (-40, 0, 0), "DlonP": (-10, 0, 0),
               "RamieL": (12, 0, 34), "PrzedramieL": (-22, 0, 0),
               "UdoL": (-10, 0, 0), "GolenL": (8, 0, 0), "UdoP": (6, 0, 0), "Krysztal": {"przes": (0, 0, 0.12)},
               "Blask": {"przes": (0, 0, 0.01)}}
    szczyt = dict(wziecie, Tulow=(-11, -20, 5), Glowa=(-7, 14, -2), RamieP=(-145, 0, -55), PrzedramieP=(-50, 0, 0),
                  Szczeka=(16, 0, 0))
    uderzenie = {"Biodra": (0, 12, 0), "Tulow": (34, 24, -4), "Glowa": (-26, -16, 2), "Szczeka": (22, 0, 0),
                 "Korona": (8, 0, -2),
                 "RamieP": (-80, 0, -1), "PrzedramieP": (-10, 0, 0), "DlonP": (10, 0, 0),
                 "RamieL": (22, 0, 24), "PrzedramieL": (-20, 0, 0),
                 "UdoL": (-30, 0, 0), "GolenL": (24, 0, 0), "UdoP": (14, 0, 0), "GolenP": (6, 0, 0),
                 "Krysztal": {"przes": (0, 0, 0.16)}, "Blask": {"przes": (0, 0, 0.012)}}
    docisk = dict(uderzenie, Tulow=(38, 26, -4), Glowa=(-28, -17, 2), RamieP=(-70, 0, -1), PrzedramieP=(-6, 0, 0),
                  Korona=(11, 0, -3))
    odbicie = dict(uderzenie, Tulow=(24, 14, -3), RamieP=(-55, 0, -3), PrzedramieP=(-16, 0, 0), Glowa=(-18, -10, 1),
                   Korona=(2, 0, 0), Krysztal={"przes": (0, 0, 0.08)})
    powrot = {"Biodra": (0, 4, 0), "Tulow": (8, 8, -1), "Glowa": (-5, -5, 0), "Szczeka": (6, 0, 0),
              "RamieP": (-20, 0, -2), "PrzedramieP": (-14, 0, 0), "RamieL": (6, 0, 8), "UdoL": (-8, 0, 0),
              "GolenL": (6, 0, 0), "Krysztal": {"przes": (0, 0, 0.05)}}
    _sekwencja(k, (0, 9, 13, 17, 21, 28, 35, dl), ({}, wziecie, szczyt, uderzenie, docisk, odbicie, powrot, {}),
               wyg={2: "liniowo"}, przypnij=True)
    return k


def _korzen_swiat(i, wzrost, uscisk, t):
    """Pozy członów korzenia i w świecie: lista (kość, obrót w świecie, staw w świecie) dla A, B, C.
    wzrost 0…1 (0 = schowany pod ziemią, 1 = wyrośnięty), uscisk 0…1 (zaciśnięcie nad środkiem)."""
    kat, r, wys = KORZENIE_U[i]
    a = math.radians(kat)
    na_zew = (math.sin(a), math.cos(a))                 # od środka uścisku na zewnątrz (x, z)
    x, z = UCISK[0] + r * na_zew[0], UCISK[1] + r * na_zew[1]
    g3 = wzrost * 3
    c_wys = _wygladz(max(0.0, min(1.0, g3)))
    b_wys = _wygladz(max(0.0, min(1.0, g3 - 1)))
    a_wys = _wygladz(max(0.0, min(1.0, g3 - 2)))
    drg = math.sin(2 * math.pi * (2 * t + i * 0.23)) * 4 * wzrost       # drganie korzeni

    def pochyl(stopnie):
        s = math.radians(stopnie)
        return _obrot_na((na_zew[0] * math.sin(s), math.cos(s), na_zew[1] * math.sin(s)))

    RA = macierz_obrotu(*pochyl(12 * a_wys + 2 * drg / 4))
    tA = (x, POD_ZIEMIA + (NAD_ZIEMIA - POD_ZIEMIA) * a_wys, z)
    # B i C zaginają się do środka (−kąt = do środka) jak palce: otwarte ok. 45°, zaciśnięte ok. 95° (szpice
    # poziomo nad środkiem uścisku)
    RB = mnoz(RA, macierz_obrotu(*pochyl(-(22 + 18 * uscisk) * b_wys - drg)))
    tB = tuple(tA[j] + razy_wektor(RA, (0, KB_WYS * wys * b_wys, 0))[j] for j in range(3))
    RC = mnoz(RB, macierz_obrotu(*pochyl(-(36 + 34 * uscisk) * c_wys - drg)))
    tC = tuple(tB[j] + razy_wektor(RB, (0, KC_WYS * wys * c_wys, 0))[j] for j in range(3))
    n = "K%d" % (i + 1)
    return [(n + "A", RA, tA), (n + "B", RB, tB), (n + "C", RC, tC)]


def _korzenie_klatka(p, pz, f, okno, rosnij, scisk, cofnij):
    """Dopisuje do pozy pz klucze korzeni w klatce f. okno = (pierwsza klatka pod ziemią, ostatnia); poza oknem
    teleskop siedzi w tułowiu (zera)."""
    p0, p1 = okno
    kos = [n for n in p.kosci if n.startswith("K") and n[1:-1].isdigit()]
    if f < p0 or f > p1:
        for n in kos:
            pz[n] = (ZERO, ZERO)
        return
    W = _fk(p, pz)
    for i in range(len(KORZENIE_U)):
        opozn = i * 1.2                                  # korzenie wyrastają jeden po drugim
        if f <= rosnij[1] + opozn:
            wz = max(0.0, min(1.0, (f - rosnij[0] - opozn) / float(rosnij[1] - rosnij[0])))
        elif f < cofnij[0]:
            wz = 1.0
        else:
            wz = 1.0 - max(0.0, min(1.0, (f - cofnij[0] - opozn * 0.5) / float(cofnij[1] - cofnij[0])))
        # uścisk: szybkie zamknięcie (5 kl.), trzymanie z dwoma dociśnięciami w rytm pięści, otwarcie (5 kl.)
        us = 0.0
        if scisk[0] <= f <= scisk[1]:
            wej = _wygladz(min(1.0, (f - scisk[0]) / 5.0))
            wyj = _wygladz(min(1.0, (scisk[1] - f) / 5.0))
            us = wej * wyj * (0.88 + 0.12 * math.cos(2 * math.pi * (f - scisk[0] - 5) / 6.0))
        for n, Rw, tw in _korzen_swiat(i, wz, us, f / 30.0):
            W[n] = (Rw, tw)                                  # A, B, C po kolei: rodzic już jest w W
            pz[n] = _lokalnie(p, W, n, Rw, tw)


def umiejetnosc(p, dl=90):
    """Uścisk korzeni (3 s): strażnik unosi obie pięści wysoko nad głowę i ryczy (kl. 16), kryształ jaśnieje,
    potem z przysiadem wbija pięści w ziemię przed sobą (kl. 30). Z ziemi przed nim wyrastają kolejno pięć korzeni
    (kl. 32–50) i zaciskają się nad środkiem uścisku ok. 6,6 studa przed strażnikiem (kl. 50–66, pięści w ziemi
    obracają się w rytm zaciskania), cofają się pod ziemię (kl. 66–78), a strażnik wyciąga pięści i wstaje."""
    k = p.klip("umiejetnosc", dl, petla=False)
    gora = {"Tulow": (-10, 0, 0), "Glowa": (-16, 0, 0), "Szczeka": (24, 0, 0), "Korona": (-4, 0, 0),
            "RamieL": (-145, 0, 22), "RamieP": (-145, 0, -22), "PrzedramieL": (-20, 0, 0),
            "PrzedramieP": (-20, 0, 0), "UdoL": (-6, 0, 4), "GolenL": (8, 0, 0), "UdoP": (-6, 0, -4),
            "GolenP": (8, 0, 0), "Krysztal": {"obrot": (0, 0, 0), "przes": (0, 0, 0.14)},
            "Blask": {"przes": (0, 0, 0.012)}}
    szczyt = dict(gora, Tulow=(-12, 0, 0), Glowa=(-20, 0, 0), Szczeka=(30, 0, 0), RamieL=(-155, 0, 18),
                  RamieP=(-155, 0, -18), PrzedramieL=(-30, 0, 0), PrzedramieP=(-30, 0, 0))
    przysiad = {"UdoL": (-78, 0, 10), "GolenL": (78, 0, 0), "UdoP": (-78, 0, -10), "GolenP": (78, 0, 0),
                "Tulow": (68, 0, 0), "Glowa": (-50, 0, 0), "Szczeka": (16, 0, 0), "Korona": (6, 0, 0),
                "RamieL": (-80, 0, 6), "RamieP": (-80, 0, -6), "PrzedramieL": (-6, 0, 0),
                "PrzedramieP": (-6, 0, 0), "DlonL": (6, 0, 0), "DlonP": (6, 0, 0),
                "Krysztal": {"przes": (0, 0, 0.12)}, "Blask": {"przes": (0, 0, 0.012)}}
    uderzenie = dict(przysiad, Tulow=(72, 0, 0), RamieL=(-80, 0, 6), RamieP=(-80, 0, -6))
    odbicie = dict(przysiad, Tulow=(66, 0, 0), Glowa=(-48, 0, 0))
    scisk_l = dict(przysiad, DlonL=(6, 22, 0), DlonP=(6, -22, 0), Szczeka=(26, 0, 0), Tulow=(70, 0, 0),
                   Glowa=(-54, 0, 0))
    scisk_p = dict(przysiad, DlonL=(6, -8, 0), DlonP=(6, 8, 0))
    wyciaga = dict(przysiad, Tulow=(40, 0, 0), Glowa=(-30, 0, 0), RamieL=(-60, 0, 10), RamieP=(-60, 0, -10),
                   PrzedramieL=(-40, 0, 0), PrzedramieP=(-40, 0, 0), UdoL=(-50, 0, 8), GolenL=(50, 0, 0),
                   UdoP=(-50, 0, -8), GolenP=(50, 0, 0), Krysztal={"przes": (0, 0, 0.06)})
    wstaje = {"Tulow": (10, 0, 0), "Glowa": (-6, 0, 0), "RamieL": (-14, 0, 6), "RamieP": (-14, 0, -6),
              "PrzedramieL": (-14, 0, 0), "PrzedramieP": (-14, 0, 0), "UdoL": (-14, 0, 2), "GolenL": (14, 0, 0),
              "UdoP": (-14, 0, -2), "GolenP": (14, 0, 0)}
    czasy = (0, 10, 18, 26, 30, 33, 44, 52, 58, 64, 70, 80, dl)
    pozy = ({}, gora, szczyt, uderzenie, uderzenie, odbicie, przysiad, scisk_l, scisk_p, scisk_l, wyciaga, wstaje, {})
    okno = (31, 79)

    def korzenie(f, pz):
        if 18 <= f <= 66:                                    # kryształ pulsuje mocno, póki trwa uścisk
            kz, ky, bz = _puls(f / 30.0 * 0.5, 1.6, czestosc=4)
            pz["Krysztal"] = ((0, ky, 0), (0, 0, kz + 0.04))
            pz["Blask"] = (ZERO, (0, 0, bz))
        _korzenie_klatka(p, pz, f, okno, (32, 46), (50, 66), (66, 74))

    _sekwencja(k, czasy, pozy, wyg={3: "liniowo"}, przypnij=True, dodatek=korzenie)
    # skok korzeni do tułowia i z powrotem: klatka przed skokiem trzyma wartość („stale”), a nie przejście
    for f in (okno[0] - 1, okno[1]):
        for n in p.kosci:
            if n.startswith("K") and n[1:-1].isdigit():
                for kanal in ("obrot", "przes"):
                    kl = k.kanaly[(n, kanal)]
                    kl[float(f)][3] = "stale"
    return k


def trafienie(p, dl=20):
    """Reakcja na cios (0,67 s): szarpnięcie tułowia i głowy w tył (kl. 4), ręce odlatują na boki, kryształ cofa
    się w gniazdo, korona podskakuje; stopy zostają w miejscu, potem powrót."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = {"UdoL": (10, 0, 0), "UdoP": (10, 0, 0), "GolenL": (-2, 0, 0), "GolenP": (-2, 0, 0),
             "Biodra": (-4, 0, 0), "Tulow": (-15, 6, 3), "Glowa": (-20, -10, 6), "Szczeka": (16, 0, 0),
             "Korona": (-10, 0, 6),
             "RamieL": (-20, 0, 26), "RamieP": (-16, 0, -24), "PrzedramieL": (-30, 0, 0), "PrzedramieP": (-24, 0, 0),
             "Krysztal": {"obrot": (0, 18, 0), "przes": (0, 0, -0.35)}, "Blask": {"przes": (0, 0, -0.08)},
             "Powieki": {"przes": PRZYMKNIETE}}
    wraca ={"UdoL": (3, 0, 0), "UdoP": (3, 0, 0), "Biodra": (-1, 0, 0), "Tulow": (-5, 2, 1), "Glowa": (-6, 0, 2),
             "Szczeka": (6, 0, 0), "Korona": (4, 0, -2), "RamieL": (-6, 0, 8), "RamieP": (-5, 0, -8),
             "PrzedramieL": (-10, 0, 0), "PrzedramieP": (-8, 0, 0), "Krysztal": {"przes": (0, 0, -0.1)}}
    _sekwencja(k, (0, 4, 11, dl), ({}, szarp, wraca, {}), wyg={0: "liniowo"}, przypnij=True)
    return k


def unik(p, dl=30):
    """Unik (1 s): ciężki odskok w lewo (+X) z przechyłem i ugiętymi kolanami, prawa ręka zasłania pierś, chwila
    w bok, powrót na linię ciosu. Całe ciało razem ze stopami przesuwa się o 1,8 studa."""
    k = p.klip("unik", dl, petla=False)
    zbior = {"UdoL": (-14, 0, 0), "GolenL": (24, 0, 0), "UdoP": (-14, 0, 0), "GolenP": (24, 0, 0),
             "Tulow": (8, 0, -6), "Glowa": (-4, 0, 4), "RamieL": (-8, 0, 10), "RamieP": (-14, 0, -8)}
    bok = {"Biodra": {"obrot": (0, 10, -4), "przes": (1.8, 0, -0.25)}, "Tulow": (6, 4, -14),
           "Glowa": (-2, -14, 12), "Korona": (0, 0, 6),
           "UdoL": (-16, 0, 12), "GolenL": (26, 0, 0), "UdoP": (-12, 0, 10), "GolenP": (22, 0, 0),
           "RamieL": (-14, 0, 34), "PrzedramieL": (-20, 0, 0), "RamieP": (-40, 0, -6), "PrzedramieP": (-70, 0, 0),
           "Krysztal": {"przes": (0, 0, -0.1)}}
    bok2 = dict(bok, Biodra={"obrot": (0, 8, -3), "przes": (1.75, 0, -0.2)}, Tulow=(5, 3, -11))
    _sekwencja(k, (0, 4, 10, 17, dl), ({}, zbior, bok, bok2, {}))
    return k


def ryk(p, dl=60):
    """Ryk po wygranej (pętla 2 s): pięści wzniesione szeroko w górę, głowa odchylona, szczęka szeroko otwarta,
    kryształ pulsuje mocno; dwa „pompnięcia” na pętlę (pięści wyżej, lekkie ugięcie kolan)."""
    k = p.klip("ryk", dl, petla=True)
    a = {"Tulow": (-10, 0, 0), "Glowa": (-20, 0, 0), "Szczeka": (28, 0, 0), "Korona": (-3, 0, 0),
         "RamieL": (-148, 0, 38), "RamieP": (-148, 0, -38), "PrzedramieL": (-30, 0, 0), "PrzedramieP": (-30, 0, 0),
         "UdoL": (-5, 0, 4), "GolenL": (6, 0, 0), "UdoP": (-5, 0, -4), "GolenP": (6, 0, 0)}
    b = dict(a, Tulow=(-15, 0, 0), Glowa=(-27, 0, 0), Szczeka=(38, 0, 0), Korona=(-6, 0, 0),
             RamieL=(-162, 0, 30), RamieP=(-162, 0, -30), PrzedramieL=(-50, 0, 0), PrzedramieP=(-50, 0, 0),
             UdoL=(-14, 0, 5), GolenL=(18, 0, 0), UdoP=(-14, 0, -5), GolenP=(18, 0, 0))

    def puls(f, pz):
        _z_pulsem(pz, f / float(dl), 1.6, czestosc=4)

    _sekwencja(k, (0, 15, 30, 45, dl), (a, b, a, b, a), przypnij=True, dodatek=puls)
    return k


# ------------------------------------------------------------------------------------------------- upadek
# stos głazów: kość -> (środek klocka kości x, z w świecie, obrót w świecie); y liczy się sam (leży na ziemi)
STOS = {
    "Korona": ((1.5, 3.6), (72, 28, 6)),
    "Glowa": ((-0.7, 2.6), (-62, -22, 10)),
    "RamieL": ((4.3, -0.4), (6, 22, 86)),
    "RamieP": ((-4.4, -0.2), (-6, -18, -88)),
    "PrzedramieL": ((4.4, 2.0), (-86, 38, 0)),
    "PrzedramieP": ((-4.3, 2.3), (-82, -30, 4)),
    "DlonL": ((2.9, 3.6), (88, 18, 0)),
    "DlonP": ((-2.6, 4.0), (10, -34, 92)),
    "Tulow": ((0.2, -4.4), (-74, 8, 0)),
    "Biodra": ((0.0, -1.9), (-10, 6, 3)),
    "UdoL": ((2.7, -2.3), (12, 28, -86)),
    "UdoP": ((-2.8, -2.0), (-8, -24, 86)),
}
# kiedy który głaz odpada i spada (klatki): korona i głowa pierwsze, potem ręce, tułów, miednica, uda
SPADA = {"Korona": (33, 44), "Glowa": (35, 48), "RamieL": (37, 50), "RamieP": (39, 52),
         "PrzedramieL": (40, 52), "PrzedramieP": (42, 54), "DlonL": (41, 52), "DlonP": (43, 54),
         "Tulow": (41, 57), "Biodra": (45, 58), "UdoL": (47, 60), "UdoP": (48, 61)}


def _cel_stosu(p, n):
    """(obrót, staw) kości n w stosie: klocek kości ma środek w (x, z) ze STOS i leży na ziemi."""
    (x, z), ob = STOS[n]
    R = macierz_obrotu(*ob)
    sr = razy_wektor(R, p.kosci[n]["srodek"])
    t0 = (x - sr[0], 0.0, z - sr[2])
    dno = _najnizej({n: (R, t0)}, (n,))
    return R, (t0[0], -dno, t0[2])


def upadek(p, dl=80):
    """Pokonanie (2,67 s): szarpnięcie w tył, kryształ migocze (cofa się i wraca), strażnik chwieje się i osiada
    w ciężkim przysiadzie (goleni pionowo, jak pnie), kryształ gaśnie (świecący chowa się w pierś, wysuwa się szary)
    i kamienne powieki zasłaniają oczy (kl. 24–32). Potem rozsypuje się na głazy: korona, głowa, ręce, tułów,
    miednica i uda odpadają po kolei i spadają na ziemię (kl. 33–61) z małym odbiciem; zostają dwa pniaki
    z korzeniami. Ostatnia klatka: stos głazów (do utrzymania w grze)."""
    k = p.klip("upadek", dl, petla=False)
    szarp = {"UdoL": (10, 0, 0), "UdoP": (10, 0, 0), "Tulow": (-14, 4, 4), "Glowa": (-18, 10, 0),
             "Szczeka": (18, 0, 0), "Korona": (-8, 0, 4), "RamieL": (-20, 0, 25), "RamieP": (-15, 0, -25),
             "PrzedramieL": (-20, 0, 0), "PrzedramieP": (-20, 0, 0), "Krysztal": {"przes": (0, 0, -0.55)},
             "Blask": {"przes": (0, 0, -0.08)}}
    chwiej = {"UdoL": (-6, 0, 0), "GolenL": (6, 0, 0), "UdoP": (-4, 0, 0), "GolenP": (4, 0, 0),
              "Tulow": (12, -6, -6), "Glowa": (14, -8, 4), "Szczeka": (12, 0, 0), "Korona": (6, 0, -4),
              "RamieL": (-8, 0, 6), "RamieP": (-14, 0, -4), "PrzedramieP": (-10, 0, 0),
              "Krysztal": {"przes": (0, 0, -0.05)}, "Blask": {"przes": (0, 0, -0.02)}}
    migot = dict(chwiej, Tulow=(16, -4, -4), Krysztal={"przes": (0, 0, -0.6)}, Blask={"przes": (0, 0, -0.08)})
    osiada = {"UdoL": (-58, 0, 10), "GolenL": (58, 0, 0), "UdoP": (-58, 0, -10), "GolenP": (58, 0, 0),
              "Tulow": (30, 0, 4), "Glowa": (22, 6, -4), "Szczeka": (10, 0, 0), "Korona": (6, 0, 4),
              "RamieL": (6, 0, 12), "RamieP": (8, 0, -12), "PrzedramieL": (-6, 0, 0), "PrzedramieP": (-6, 0, 0),
              "Krysztal": {"przes": (0, 0, -0.2)}, "Blask": {"przes": (0, 0, -0.08)},
              "Powieki": {"przes": PRZYMKNIETE}}
    zgasl = dict(osiada, Tulow=(34, 0, 5), Glowa=(28, 8, -6), Szczeka=(3, 0, 0),
                 Krysztal={"przes": (0, 0, ZGASLY_Z)}, Zgasly={"przes": (0, 0, -ZGASLY_Z)},
                 Blask={"przes": (0, 0, -0.08)}, Powieki={"przes": ZAMKNIETE})
    czasy = (0, 5, 11, 15, 24, 32)
    pozy = [_pelna(x) for x in ({}, szarp, chwiej, migot, osiada, zgasl)]
    koniec = None
    for f in range(0, czasy[-1] + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        pz = _postaw(p, _mieszaj(pozy[i], pozy[i + 1], _wygladz(t)), "stopy", True)
        _klucze(k, f, pz)
        koniec = pz
    # --- rozpad: każda kość z STOS najpierw jedzie z rodzicem (poza z kl. 32), potem spada do swojego miejsca
    # w stosie (tor prosty, przyspieszenie, małe odbicie); goleni i stopy zostają tam, gdzie były
    W0 = _fk(p, koniec)
    cele = {n: _cel_stosu(p, n) for n in STOS}
    stale = {n: W0[n] for n in ("GolenL", "GolenP", "StopaL", "StopaP")}
    for f in range(czasy[-1] + 1, dl + 1):
        W = {}
        pz = {}
        for n, kk in p.kosci.items():
            if n == "Root":
                W[n] = (I3, (0.0, 0.0, 0.0))
                continue
            ob, pr = koniec.get(n, (ZERO, ZERO))
            Rp, tp = W[kk["rodzic"]]
            st = p.kosci[kk["rodzic"]]["staw"]
            Rj = mnoz(Rp, macierz_obrotu(*ob))
            tj = tuple(tp[i] + razy_wektor(Rp, tuple(kk["staw"][i2] - st[i2] + pr[i2] for i2 in range(3)))[i]
                       for i in range(3))
            if n in stale:
                Rj, tj = stale[n]
            elif n in STOS:
                f0, f1 = SPADA[n]
                u = (f - f0) / float(f1 - f0)
                if u > 0:
                    e = min(1.0, u) ** 2
                    Rc, tc = cele[n]
                    Rj = _slerp_R(Rj, Rc, e)
                    tj = tuple(tj[i] + (tc[i] - tj[i]) * e for i in range(3))
                    if 1.0 < u < 1.0 + 6.0 / (f1 - f0):          # odbicie po upadku (ok. 6 klatek)
                        tj = (tj[0], tj[1] + 0.18 * math.sin(math.pi * (u - 1.0) * (f1 - f0) / 6.0), tj[2])
            W[n] = (Rj, tj)
            if n in CIALO and n not in ("Krysztal", "Zgasly", "Blask", "Powieki", "Szczeka"):
                dno = _najnizej(W, (n,)) if n in _PKT else 0.0
                if dno < 0:
                    W[n] = (Rj, (tj[0], tj[1] - dno, tj[2]))
            if n in CIALO or n.startswith("K"):
                if n in CIALO:
                    pz[n] = _lokalnie(p, W, n, *W[n])
        _klucze(k, f, pz)
    return k
