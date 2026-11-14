# -*- coding: utf-8 -*-
"""LEŚNY TROLL — rzadki, ciężki przeciwnik lasu (ok. 10 studów wzrostu z grzybami; gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/lesny_troll.py --wyj <folder> --klip atak

Opis z danych walki (tools/walka/dane_walki.json, id „lesny_troll”): ogromny, przygarbiony troll o skórze jak kora,
z poduchami mchu i grzybami na plecach; wlecze maczugę z wyrwanego pnia z korzeniami. Umiejętność: ogłuszające
uderzenie (maczuga znad głowy w ziemię).

Wybór szkieletu: własne kości (typ „stwor”), a nie R15. R15 liczy stawy z wysokości klocków i stawia głowę na środku
górnej ściany tułowia — przygarbienia, głowy wysuniętej przed pierś i rąk do kolan nie da się tam ustawić w pozie
spoczynkowej (trzeba by je trzymać w każdym klipie). Własne kości mają te same zasady co R15 (osie równoległe do osi
modelu, rx < 0 unosi zwisającą rękę do przodu, rz > 0 odchyla ją w stronę +X).

Sylwetka (od przodu i z boku): krótkie, grube nogi szeroko; ogromny, pochylony do przodu tułów z garbem; mała głowa
nisko przed garbem, „wciśnięta” między barki z mchu; wielka żuchwa z dolnymi kłami opiera się na piersi; bardzo długie
ręce z pięściami na wysokości kolan; maczuga-pień w prawej dłoni: w spoczynku korzenie leżą na ziemi z prawej strony
(pień widać z przodu i w kadrze 3/4), w chodzie i przy upadku wlecze się za trollem.

Szkielet: Root > Biodra > {Tulow > {Glowa > Szczeka; RamieL > PrzedramieL > DlonL; RamieP > PrzedramieP > DlonP >
Maczuga}; UdoL > GolenL > StopaL; UdoP > GolenP > StopaP}. L = lewa = +X, P = prawa = −X. Maczuga jest kością
modelu (eksportuje się razem z trollem i ma własny obrót względem dłoni — dzięki temu korzenie leżą na ziemi w
spoczynku, a w zamachu pień celuje tam, gdzie trzeba).

Paleta (6 rodzin + akcent): kora (ciepła szarobrązowa, trzy odcienie), mech (dwa zielenie), drewno maczugi (ciepły brąz,
ciemne korzenie, jasny przełom), kość (kły, paznokcie), tusz (źrenice), AKCENT: czerwono-pomarańczowe kapelusze
grzybów z kremowymi kropkami.

Klipy (30 kl./s; postać patrzy w +Z i w tę stronę atakuje):
  idle (pętla 2,4 s), ruch (ciężki chód, pętla 1,6 s), atak (maczuga z barku płaskim łukiem przed sobą, 1,2 s),
  umiejetnosc (ogłuszające uderzenie: maczuga oburącz znad głowy w ziemię, 2 s), trafienie (szarpnięcie w tył,
  0,67 s), unik (odskok w lewo i powrót, 1 s), upadek (uginają się kolana, siada i pada na plecy — kończy się
  leżeniem, 2 s), ryk (po wygranej, pętla 2 s).
Klipy jednorazowe są zapisane jako pozy kluczowe (funkcja _poza) zamienione na klucz w każdej klatce (_sekwencja):
stopy stoją płasko na ziemi, pień maczugi idzie po łuku, a korzenie nie wchodzą w ziemię. Zmiany rób w pozach
kluczowych w tym pliku, nie w Blenderze.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "lesny_troll"

PALETA = {
    "kora": "86704F", "kora_ciemna": "52402C", "kora_jasna": "B49B72",
    "mech": "6DBA3C", "mech_ciemny": "3F7F2D",
    "drewno": "B8692B", "drewno_ciemne": "6A3A17", "przelom": "EBCB8E",
    "kosc": "F1E6C8", "bialko": "F6EBC4",
    "grzyb": "E5482F",
}

# ----------------------------------------------------------------------------------------------- wymiary (studs)
LEAN = 24.0                      # pochylenie tułowia do przodu (w bryłach, nie w klipach)
X_NOGI = 1.2
Y_BIODRO, Y_KOLANO, Y_KOSTKA = 3.4, 2.0, 0.75
TULOW_STAW = (0.0, 4.3, -0.3)    # staw w pasie
X_BARK = 2.95


def _pochyl(y, z, kat=LEAN):
    """Punkt (0, y, z) z układu pochylonego tułowia -> przesunięcie względem stawu tułowia."""
    a = math.radians(kat)
    return (y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a))


def _z_tulowia(x, y, z):
    dy, dz = _pochyl(y, z)
    return (x, TULOW_STAW[1] + dy, TULOW_STAW[2] + dz)


SZYJA = _z_tulowia(0.0, 3.7, 1.3)                # staw głowy (przód-góra piersi)
GLOWA_SR = (0.0, 0.45, 0.8)                      # środek głowy względem stawu
GLOWA = (1.75, 1.45, 1.5)
BARK_L = _z_tulowia(X_BARK, 3.25, 0.3)
RAMIE, PRZEDRAMIE, DLON = (1.3, 2.3, 1.35), (1.75, 2.05, 1.75), (1.8, 1.15, 1.65)   # przedramię i pięść grubsze
Y_LOKIEC = BARK_L[1] - 2.3
Y_NADGARSTEK = Y_LOKIEC - 2.05
CHWYT = (-X_BARK, Y_NADGARSTEK - 0.57, BARK_L[2])   # środek prawej pięści = staw maczugi


def _obrot_na(kier):
    """(rx, 0, rz): obrót, który kieruje oś +Y w stronę wektora kier (kolejność Ry·Rx·Rz, ry = 0)."""
    n = math.sqrt(sum(v * v for v in kier))
    x, y, z = (v / n for v in kier)
    c = math.asin(-x)
    a = math.atan2(z / math.cos(c), y / math.cos(c))
    return (math.degrees(a), 0.0, math.degrees(c))


# maczuga w swoim układzie: +Y wzdłuż pnia od chwytu ku korzeniom; obrót układu kieruje pień w dół i w bok
# (korzenie leżą na ziemi z prawej strony trolla — pień widać z przodu, z tyłu i w kadrze 3/4; wcześniej leżał
# prawie prosto za nogą i w kadrze bohaterskim oraz w filmach chował się za trollem)
MACZUGA_KIER = (-0.93, -0.27, -0.05)
MACZUGA_SKRET = -80.0                           # skręt pnia wokół osi: korzenie dotykają ziemi, nie wchodzą w nią
MACZUGA_OBROT = katy_z_macierzy(mnoz(macierz_obrotu(*_obrot_na(MACZUGA_KIER)), macierz_obrotu(0, MACZUGA_SKRET, 0)))
MACZUGA_DL = 4.1                                # od chwytu do środka bryły korzeni
SPOCZ_XZ = (MACZUGA_KIER[0], MACZUGA_KIER[2])   # kierunek pnia po ziemi w spoczynku (do póz „ziemia”)
WLECZ_KIER = (-0.5, -0.24, -0.82)               # w chodzie (i przy upadku) pień wlecze się za trollem
WLECZ_XZ = (WLECZ_KIER[0], WLECZ_KIER[2])


def zbuduj():
    p = Postac(ID, "Leśny Troll", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Biodra", "Root", staw=(0, Y_BIODRO, 0), czesc=(3.7, 1.4, 2.5), srodek=(0, 0.4, -0.1))
    p.kosc("Tulow", "Biodra", staw=TULOW_STAW, czesc=(4.3, 4.6, 3.0), srodek=(0, 2.2, 0.6), dl=1.2)
    p.kosc("Glowa", "Tulow", staw=SZYJA, czesc=GLOWA, srodek=GLOWA_SR)
    szczeka = (0.0, SZYJA[1] + GLOWA_SR[1] - 0.45, SZYJA[2] + GLOWA_SR[2] - 0.35)
    p.kosc("Szczeka", "Glowa", staw=szczeka, czesc=(2.0, 0.75, 1.9), srodek=(0, -0.55, 0.65), dl=0.4)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        bark = (zn * X_BARK, BARK_L[1], BARK_L[2])
        p.kosc("Ramie" + s, "Tulow", staw=bark, czesc=RAMIE, srodek=(0, -0.95, 0))
        p.kosc("Przedramie" + s, "Ramie" + s, staw=(bark[0], Y_LOKIEC, bark[2]), czesc=PRZEDRAMIE,
               srodek=(0, -1.0, 0))
        p.kosc("Dlon" + s, "Przedramie" + s, staw=(bark[0], Y_NADGARSTEK, bark[2]), czesc=DLON,
               srodek=(0, -0.57, 0))
        p.kosc("Udo" + s, "Biodra", staw=(zn * X_NOGI, Y_BIODRO, 0), czesc=(1.75, 1.55, 1.75),
               srodek=(0, -0.7, 0))
        p.kosc("Golen" + s, "Udo" + s, staw=(zn * X_NOGI, Y_KOLANO, 0), czesc=(1.5, 1.35, 1.5),
               srodek=(0, -0.6, 0))
        p.kosc("Stopa" + s, "Golen" + s, staw=(zn * X_NOGI, Y_KOSTKA, 0), czesc=(1.6, 0.75, 2.1),
               srodek=(0, -0.375, 0.35))
    p.kosc("Maczuga", "DlonP", staw=CHWYT, dl=0.6)

    _nogi(p)
    _biodra(p)
    _tulow(p)
    _glowa(p)
    _rece(p)
    _maczuga(p)

    # punkty zaczepienia dla gry: korzeń, tabliczka nad garbem, środek pyska (ryk), głowica maczugi (fala uderzenia)
    p.zaczep("RootAttachment", "Biodra", (0, -Y_BIODRO, 0))
    p.zaczep("GlowaAttachment", "Tulow", (0, 6.0, -0.6))
    p.zaczep("PyskAttachment", "Glowa", (0, GLOWA_SR[1] - 0.5, GLOWA_SR[2] + 0.9))
    p.zaczep("MaczugaAttachment", "Maczuga", razy_wektor(macierz_obrotu(*MACZUGA_OBROT), (0, MACZUGA_DL, 0)))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


SLABOSCI = [
    "Kości trolla nie są R15 (własny szkielet, 18 kości jak u petów) — klipy importuje się na własny rig; import "
    "do Roblox Studio nie był testowany.",
    "Bryły są sztywno przypięte do kości (jedna siatka na kość): w barkach ramię lekko wchodzi w pierś, przy rękach "
    "w górze poducha mchu na ramieniu wchodzi w garb, a w leżeniu grzyby na garbie dotykają ziemi.",
    "Maczuga jest kością modelu, a nie osobnym przedmiotem — w FBX jest razem z trollem i nie da się jej wymienić "
    "jak broni gracza.",
    "Ogłuszające uderzenie to sam ruch: fali uderzeniowej, kurzu i gwiazdek ogłuszenia nie ma (dorobić w grze na "
    "MaczugaAttachment).",
    "Klipy jednorazowe mają klucz w każdej klatce (tak liczone są stopy na ziemi i łuk maczugi) — pliki klipów są "
    "większe, a poprawki trzeba robić w pozach kluczowych w module, nie w Blenderze.",
    "Wspólny kadr filmów obejmuje zasięg maczugi ze wszystkich klipów (w umiejętności korzenie przechodzą przez "
    "ok. 16 studów wysokości, a uderzenie kładzie pień ok. 11 studów przed trollem), więc w filmach i arkuszach "
    "klatek troll zajmuje tylko ok. 1/3 wysokości kadru; bliższe ujęcia: plansza i kadr bohaterski.",
    "Chód jest w miejscu (stopy ślizgają się względem ziemi, w fazie przenoszenia obie stopy są do 0,2 studa nad "
    "ziemią), maczuga w chodzie nie podskakuje na nierównościach; w upadku troll leży lekko podparty na garbie.",
    "Spoczynek i chód mają różny kierunek pnia (w spoczynku korzenie leżą z boku, w chodzie za trollem) — przejście "
    "idle→ruch w grze obraca maczugę o ok. 55° (z boku za plecy); powinno to wyglądać jak zarzucenie pnia za "
    "siebie, ale wymaga obejrzenia w silniku.",
    "W kadrze 3/4 od lewej strony trolla bryłę korzeni widać częściowo od czoła — z daleka przypomina kolczastą kulę "
    "(z przodu i z tyłu pień z korzeniami czyta się dobrze).",
    "Kolizje sprawdzane w przybliżeniu (punkty skrzynek brył w każdej klatce, wartości kluczy liniowo): maczuga, "
    "pięści i przedramiona nie wchodzą w głowę, szczękę, tułów, garb ani biodra; ramiona sprawdzone tylko względem "
    "głowy.",
    "Klipy to szkice (0,7–2,4 s), nie gotowa animacja; twarz nie ma mimiki poza otwieraniem żuchwy.",
]


# ---------------------------------------------------------------------------------------------------- pomocnicze
def _grzyb(p, nazwa, pos, h, r, rot=(0, 0, 0)):
    """Grzyb: kremowa nóżka, czerwony stożkowy kapelusz z kremową kropką na szczycie."""
    with p.uklad(pos=pos, obrot=rot):
        p.walec(nazwa + " nozka", (0, h / 2, 0), (r * 0.55, h, r * 0.55), "kosc", "matowy", segm=8, faza=0.02)
        p.walec(nazwa + " blaszki", (0, h - 0.02, 0), (r * 1.7, 0.08, r * 1.7), "przelom", "matowy", segm=8,
                faza=0.0)
        p.stozek(nazwa + " kapelusz", (0, h + 0.27 * r, 0), (r * 2.0, 0.6 * r, r * 2.0), "grzyb", "zwykly",
                 gora=0.42, segm=8)
        p.walec(nazwa + " kropka", (0, h + 0.58 * r + 0.015, 0), (r * 0.5, 0.05, r * 0.5), "kosc", "matowy",
                segm=8, faza=0.0)


def _mech(p, nazwa, pos, size, rot=(0, 0, 0)):
    """Poducha mchu: płaski klocek i trzy jaśniejsze/ciemniejsze kępki na wierzchu."""
    w, h, d = size
    with p.uklad(pos=pos, obrot=rot):
        p.blok(nazwa, (0, 0, 0), size, "mech_ciemny", "matowy", faza=0.12)
        p.blok(nazwa + " kepa 1", (-w * 0.2, h / 2 + 0.05, d * 0.12), (w * 0.5, 0.2, d * 0.55), "mech", "matowy",
               faza=0.08)
        p.blok(nazwa + " kepa 2", (w * 0.24, h / 2 + 0.03, -d * 0.15), (w * 0.42, 0.16, d * 0.5), "mech",
               "matowy", faza=0.06)
        p.blok(nazwa + " kepa 3", (w * 0.05, h / 2 + 0.12, -d * 0.02), (w * 0.26, 0.16, d * 0.28), "mech",
               "matowy", faza=0.05)


# ---------------------------------------------------------------------------------------------------- bryły
def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with p.na("Udo" + s, od="srodek"):
            p.blok("Udo", (0, 0, 0), (1.75, 1.55, 1.75), "kora", faza=0.12)
            p.blok("Udo bruzda", (zn * 0.25, 0.0, 0.89), (0.12, 1.1, 0.04), "kora_ciemna", "matowy", faza=0.0)
        with p.na("Golen" + s, od="srodek"):
            p.blok("Golen", (0, 0, 0), (1.5, 1.35, 1.5), "kora", faza=0.1)
            p.blok("Kolano", (0, 0.5, 0.72), (1.1, 0.5, 0.2), "kora_jasna", "matowy", faza=0.06)
            p.blok("Golen bruzda", (-zn * 0.3, -0.15, 0.765), (0.1, 0.8, 0.04), "kora_ciemna", "matowy", faza=0.0)
        # stopy rozstawione palcami na zewnątrz (pałąkowate, ciężkie nogi)
        with p.na("Stopa" + s, od="srodek", obrot=(0, zn * 14, 0)):
            p.blok("Stopa", (0, 0, 0), (1.6, 0.75, 2.1), "kora_ciemna", faza=0.12)
            p.blok("Stopa wierzch", (0, 0.39, -0.1), (1.2, 0.04, 1.4), "kora", "matowy", faza=0.0)
            for i, dx in enumerate((-0.5, 0.0, 0.5)):
                p.blok("Palec %d" % i, (dx, -0.12, 1.12), (0.42, 0.5, 0.3), "kora_ciemna", faza=0.06)
                p.blok("Pazur %d" % i, (dx, -0.05, 1.3), (0.26, 0.22, 0.1), "kosc", "polysk", faza=0.03)


def _biodra(p):
    with p.na("Biodra", od="srodek"):
        w, h, d = 3.7, 1.4, 2.5
        p.blok("Biodra", (0, 0, 0), (w, h, d), "kora", faza=0.14)
        # pas z pnącza i przepaska z liści (przód i tył)
        p.blok("Pnacze", (0, 0.42, 0), (w + 0.1, 0.32, d + 0.1), "mech_ciemny", "matowy", faza=0.08)
        for i, x in enumerate((-1.2, -0.3, 0.6, 1.4)):
            p.blok("Pnacze wezel %d" % i, (x, 0.42, d / 2 + 0.08), (0.28, 0.4, 0.1), "kora_ciemna", "matowy",
                   rot=(0, 0, 25), faza=0.03)
        # liście przodem, tyłem i po bokach (z boku też widać spódnicę z liści, a nie cienkie patyki)
        for zk, s in ((1, ""), (-1, " tyl")):
            with p.uklad(pos=(0, 0.25, zk * (d / 2 + 0.1)), obrot=(-zk * 6, 0, 0)):
                # cztery nierówne liście, lekko rozchylone (trzy równe szpice układały się w literę „W”)
                for i, (x, dl, sz, rz, k) in enumerate(((-0.95, 1.1, 0.6, -14, "mech"),
                                                         (-0.33, 1.6, 0.72, -4, "mech_ciemny"),
                                                         (0.3, 1.3, 0.66, 7, "mech"),
                                                         (0.92, 1.0, 0.55, 16, "mech_ciemny"))):
                    p.ostroslup("Lisc%s %d" % (s, i), (x, -dl * 0.5 - 0.05, zk * 0.03 * (i % 2)), (sz, dl, 0.26), k,
                                "matowy", rot=(180, 0, rz), gora=(0.0, 0.14), faza=0.0)
        for xk, s in ((1, " L"), (-1, " P")):
            with p.uklad(pos=(xk * (w / 2 + 0.1), 0.25, 0), obrot=(0, 0, xk * 6)):
                for i, (z, dl, k) in enumerate(((-0.55, 0.85, "mech_ciemny"), (0.45, 0.95, "mech"))):
                    p.ostroslup("Lisc bok%s %d" % (s, i), (0, -dl, z), (0.26, dl, 0.75), k, "matowy",
                                rot=(180, 0, 0), gora=(0.14, 0.0), faza=0.0)


def _tulow(p):
    with p.na("Tulow", obrot=(LEAN, 0, 0)):
        # brzuch (wydatny, wysunięty), klatka (najszersza w barkach), garb — od pasa w górę, pochylone z układem
        p.blok("Brzuch", (0, 1.05, 0.1), (3.6, 2.4, 3.0), "kora", faza=0.2)
        p.kula("Brzuch wypukly", (0, 1.05, 1.25), (3.3, 2.5, 1.6), "kora_jasna", "matowy", segm=8)
        p.blok("Klatka", (0, 2.85, 0.1), (4.4, 2.2, 3.0), "kora", faza=0.22)
        p.blok("Garb", (0, 3.9, -0.55), (4.0, 1.3, 2.4), "kora", faza=0.25)
        p.blok("Garb szczyt", (0, 4.6, -0.75), (3.0, 0.5, 1.7), "kora", faza=0.18)
        # pierś: dwie płyty z rysą pośrodku; pęknięcia kory na brzuchu
        for zn in (1, -1):
            p.blok("Piers", (zn * 0.9, 2.95, 1.62), (1.5, 1.15, 0.2), "kora", "matowy", faza=0.1,
                   rot=(0, 0, -zn * 6))
        p.blok("Pepek", (0.1, 0.8, 2.04), (0.24, 0.2, 0.06), "kora_ciemna", "matowy", faza=0.0)
        # pionowe bruzdy kory na bokach i plecach (wystają 0,04 — czytają się jak kora, nie jak kamień)
        for zn in (1, -1):
            for i, (z, y, hh) in enumerate(((0.95, 2.7, 1.5), (0.3, 2.4, 2.4), (-0.4, 2.6, 2.0), (-1.05, 2.8, 1.4))):
                p.blok("Bruzda bok %d" % i, (zn * 2.21, y, z), (0.04, hh, 0.14), "kora_ciemna", "matowy", faza=0.0)
            for i, (z, y, hh) in enumerate(((0.6, 1.1, 1.4), (-0.5, 1.0, 1.6))):
                p.blok("Bruzda brzuch bok %d" % i, (zn * 1.81, y, z), (0.04, hh, 0.14), "kora_ciemna", "matowy",
                       faza=0.0)
        for i, (x, hh) in enumerate(((-1.5, 2.2), (-0.75, 3.0), (0.0, 2.4), (0.75, 3.0), (1.5, 2.0))):
            p.blok("Bruzda plecy %d" % i, (x, 1.7 + hh / 2 - 0.6, -1.42), (0.14, hh, 0.04), "kora_ciemna", "matowy",
                   faza=0.0)
        # mech: na garbie (duża poducha), na plecach i na karku
        _mech(p, "Mech garb", (0, 4.95, -0.7), (3.2, 0.36, 1.9))
        _mech(p, "Mech plecy", (0.6, 3.5, -1.83), (1.9, 1.0, 0.3), rot=(0, 0, 8))
        _mech(p, "Mech plecy 2", (-0.5, 2.75, -1.55), (1.4, 0.8, 0.3), rot=(0, 0, -12))
        _mech(p, "Mech plecy 3", (1.3, 1.6, -1.55), (0.9, 0.7, 0.25), rot=(0, 0, 20))
        _mech(p, "Mech kark", (0, 4.25, 0.75), (2.4, 0.3, 0.8))
        # grzyby na garbie i plecach (akcent koloru — widoczne z każdej strony)
        _grzyb(p, "Grzyb 1", (-0.9, 5.1, -0.75), 0.36, 0.5, rot=(0, 0, 10))
        _grzyb(p, "Grzyb 2", (-0.2, 5.1, -1.15), 0.24, 0.34, rot=(-14, 0, 0))
        _grzyb(p, "Grzyb 3", (0.95, 5.1, -0.35), 0.32, 0.42, rot=(0, 0, -14))
        _grzyb(p, "Grzyb 4", (1.4, 5.1, -1.2), 0.24, 0.28, rot=(-10, 0, -20))
        _grzyb(p, "Grzyb 5", (0.9, 3.5, -1.98), 0.25, 0.32, rot=(-80, 0, 0))
        _grzyb(p, "Grzyb 6", (-1.1, 2.4, -1.41), 0.22, 0.3, rot=(-90, 0, 0))


def _glowa(p):
    with p.na("Glowa", od="srodek"):
        w, h, d = GLOWA
        z = d / 2
        p.blok("Glowa", (0, 0, 0), GLOWA, "kora", faza=0.14)
        # ciężki łuk brwiowy (dwie bryły w „V” — groźna mina)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.43, 0.38, z + 0.13), (0.82, 0.3, 0.38), "kora_ciemna", faza=0.06,
                   rot=(0, 0, zn * 16))
            # głęboko osadzone oczy pod łukiem brwi: ciemny oczodół, kremowe białko, duża czarna źrenica, odblask
            p.blok("Oczodol " + s, (zn * 0.42, 0.06, z + 0.01), (0.56, 0.44, 0.06), "kora_ciemna", "matowy", faza=0.02)
            p.blok("Bialko " + s, (zn * 0.42, 0.06, z + 0.04), (0.46, 0.36, 0.04), "bialko", "polysk", faza=0.03)
            p.blok("Zrenica " + s, (zn * 0.36, 0.03, z + 0.07), (0.22, 0.26, 0.04), "tusz", "polysk", faza=0.0)
            p.blok("Blysk " + s, (zn * 0.36 + 0.05, 0.1, z + 0.095), (0.07, 0.07, 0.02), "bialy", faza=0.0)
            for i, (y, hh) in enumerate(((0.45, 0.5), (-0.1, 0.7))):
                p.blok("Glowa bruzda %d %s" % (i, s), (zn * (w / 2 + 0.02), y, 0.2 - 0.5 * i), (0.04, hh, 0.12),
                       "kora_ciemna", "matowy", faza=0.0)
            # uszy: małe, szpiczaste, odstające w bok
            with p.uklad(pos=(zn * (w / 2 + 0.02), 0.1, -0.1), obrot=(0, 0, -zn * 70)):
                p.ostroslup("Ucho " + s, (0, 0.25, 0), (0.42, 0.5, 0.3), "kora", gora=(0.0, 0.0),
                            przes_gory=(0.0, -0.08))
        # wielki kartoflany nos
        p.blok("Nos", (0, -0.15, z + 0.22), (0.62, 0.55, 0.5), "kora_jasna", faza=0.14)
        p.blok("Nos czubek", (0, -0.3, z + 0.42), (0.4, 0.3, 0.2), "kora_jasna", faza=0.08)
        for zn in (1, -1):
            p.blok("Nozdrze", (zn * 0.14, -0.43, z + 0.4), (0.1, 0.04, 0.12), "kora_ciemna", faza=0.0)
        p.blok("Gorna warga", (0, -0.6, z + 0.03), (1.3, 0.2, 0.1), "kora_ciemna", "matowy", faza=0.03)
        # mech i grzybek na czubku głowy
        _mech(p, "Mech glowa", (0.1, h / 2 + 0.1, -0.1), (1.3, 0.22, 1.1))
        _grzyb(p, "Grzyb glowa", (-0.35, h / 2 + 0.2, -0.25), 0.18, 0.2, rot=(0, 0, 12))

    # żuchwa: szersza niż głowa, wysunięta do przodu (przodozgryz), dolne zęby i dwa kły w górę
    with p.na("Szczeka", od="srodek"):
        jw, jh, jd = 2.0, 0.75, 1.9
        p.blok("Zuchwa", (0, 0, 0), (jw, jh, jd), "kora", faza=0.16)
        p.blok("Podbrodek", (0, -0.2, jd / 2 + 0.03), (1.3, 0.3, 0.08), "kora_jasna", "matowy", faza=0.03)
        p.blok("Usta", (0, jh / 2 - 0.08, jd / 2 - 0.25), (1.6, 0.06, 0.5), "kora_ciemna", "matowy", faza=0.0)
        for i, x in enumerate((-0.3, -0.1, 0.1, 0.3)):
            p.blok("Zab %d" % i, (x, jh / 2 + 0.05, jd / 2 - 0.12), (0.14, 0.14, 0.12), "kosc", "polysk", faza=0.02)
        for zn in (1, -1):
            p.ostroslup("Kiel", (zn * 0.68, jh / 2 - 0.02, jd / 2 - 0.2), (0.32, 0.6, 0.3), "kosc", "polysk",
                        gora=(0.0, 0.0), przes_gory=(-zn * 0.04, -0.05))
            p.blok("Policzek", (zn * (jw / 2 + 0.02), 0.0, -0.1), (0.04, 0.4, 1.0), "kora_ciemna", "matowy", faza=0.0)


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with p.na("Ramie" + s, od="srodek"):
            p.blok("Ramie", (0, 0, 0), RAMIE, "kora", faza=0.14)
            p.blok("Ramie bruzda", (zn * (RAMIE[0] / 2 + 0.02), -0.1, 0.2), (0.04, 1.5, 0.12), "kora_ciemna", "matowy",
                   faza=0.0)
            # mech na barku: poducha tylko trochę szersza od ramienia i zwis mchu po zewnętrznej stronie (wcześniej
            # płaska, szeroka płyta wyglądała jak półka, zwłaszcza przy rękach w górze)
            _mech(p, "Mech bark", (zn * 0.06, RAMIE[1] / 2 + 0.04, 0.0), (1.5, 0.4, 1.55))
            p.blok("Mech bark zwis", (zn * (RAMIE[0] / 2 + 0.07), RAMIE[1] / 2 - 0.42, 0.0), (0.16, 0.9, 1.3),
                   "mech_ciemny", "matowy", faza=0.06)
            for i, (z, hh) in enumerate(((-0.35, 0.5), (0.3, 0.75))):
                p.blok("Mech bark sopel %d" % i, (zn * (RAMIE[0] / 2 + 0.07), RAMIE[1] / 2 - 0.87 - hh / 2 + 0.1, z),
                       (0.14, hh, 0.36), "mech_ciemny", "matowy", faza=0.04)
        with p.na("Przedramie" + s, od="srodek"):
            w, h, d = PRZEDRAMIE
            p.blok("Przedramie", (0, 0, 0), PRZEDRAMIE, "kora", faza=0.16)
            p.blok("Lokiec", (0, 0.75, -d / 2 - 0.04), (1.0, 0.5, 0.1), "kora_jasna", "matowy", faza=0.04)
            for i, (x, y) in enumerate(((zn * (w / 2 + 0.02), 0.1), (zn * (w / 2 + 0.02), -0.45))):
                p.blok("Przedramie bruzda %d" % i, (x, y, 0.1 - i * 0.4), (0.04, 0.7, 0.1), "kora_ciemna", "matowy",
                       faza=0.0)
            p.blok("Przedramie bruzda przod", (-zn * 0.3, 0.2, d / 2 + 0.02), (0.12, 1.1, 0.04), "kora_ciemna",
                   "matowy", faza=0.0)
            p.blok("Mankiet mchu", (0, -0.85, 0), (w + 0.1, 0.3, d + 0.1), "mech_ciemny", "matowy", faza=0.08)
        with p.na("Dlon" + s, od="srodek"):
            p.blok("Piesc", (0, 0, 0), DLON, "kora_ciemna", faza=0.14)
            for i, x in enumerate((-0.54, -0.18, 0.18, 0.54)):
                p.blok("Kostka %d" % i, (x, -0.25, DLON[2] / 2 + 0.05), (0.3, 0.42, 0.14), "kora", faza=0.05)
                p.blok("Paznokiec %d" % i, (x, -0.52, DLON[2] / 2 - 0.05), (0.22, 0.1, 0.24), "kosc", "polysk",
                       faza=0.02)
            p.blok("Kciuk", (-zn * 0.92, 0.05, 0.25), (0.2, 0.55, 0.45), "kora", faza=0.05)


def _maczuga(p):
    """Pień z korzeniami: cienki koniec w pięści (jasny przełom wystaje nad pięść), gruby koniec z bryłą korzeni."""
    with p.na("Maczuga", obrot=MACZUGA_OBROT):
        p.walec("Trzon", (0, -0.2, 0), (0.6, 1.6, 0.6), "drewno", "matowy", segm=8, faza=0.04)
        p.walec("Przelom", (0, -1.02, 0), (0.66, 0.06, 0.66), "przelom", "matowy", segm=8, faza=0.0)
        p.stozek("Pien", (0, 1.9, 0), (1.3, 3.0, 1.3), "drewno", "matowy", rot=(180, 0, 0), gora=0.48, segm=8)
        # sęki, ułamane gałązki i ciemne pasy kory na pniu
        p.blok("Sek 1", (0.5, 1.6, 0.1), (0.24, 0.36, 0.36), "drewno_ciemne", "matowy", faza=0.04)
        p.blok("Sek 2", (-0.1, 2.6, 0.58), (0.36, 0.36, 0.24), "drewno_ciemne", "matowy", faza=0.04)
        with p.uklad(pos=(-0.45, 2.3, 0.0), obrot=(0, 0, 55)):
            p.walec("Galazka", (0, 0.35, 0), (0.26, 0.7, 0.26), "drewno", "matowy", segm=8, faza=0.03)
            p.walec("Galazka przelom", (0, 0.71, 0), (0.28, 0.04, 0.28), "przelom", "matowy", segm=8, faza=0.0)
        for i, (x, y, z) in enumerate(((0.0, 1.3, 0.47), (0.0, 2.9, -0.6), (0.6, 3.1, 0.0))):
            p.blok("Kora pasek %d" % i, (x, y, z), (0.3 if x == 0 else 0.04, 0.7, 0.04 if x == 0 else 0.3),
                   "drewno_ciemne", "matowy", faza=0.0)
        # bryła korzeni i rozczapierzone korzenie
        p.kula("Bryla korzeni", (0, MACZUGA_DL, 0), (2.0, 1.6, 2.0), "drewno_ciemne", "matowy", segm=8)
        p.blok("Ziemia", (0.15, MACZUGA_DL + 0.35, 0.3), (1.0, 0.6, 0.9), "kora_ciemna", "matowy", faza=0.1)
        p.blok("Kamyk", (-0.35, MACZUGA_DL + 0.5, -0.2), (0.4, 0.35, 0.4), "kora_jasna", "matowy", faza=0.08)
        # korzenie: wyrastają z końca bryły, rozchodzą się wachlarzem i zaginają na zewnątrz (dwa odcinki)
        for i, (th, fi, l1, zg, l2) in enumerate(KORZENIE):
            c, s = math.cos(math.radians(fi)), math.sin(math.radians(fi))
            with p.uklad(pos=(0, MACZUGA_DL + 0.2, 0), obrot=(th * c, 0, th * s)):
                p.ostroslup("Korzen %d" % i, (0, 0.5 + l1 / 2, 0), (0.42, l1, 0.42), "drewno_ciemne", "matowy",
                            gora=(0.26, 0.26))
                with p.uklad(pos=(0, 0.45 + l1, 0), obrot=(zg * c, 0, zg * s)):
                    p.ostroslup("Korzen %d koniec" % i, (0, l2 / 2 - 0.04, 0), (0.28, l2, 0.28), "drewno_ciemne",
                                "matowy", gora=(0.0, 0.0))


# korzenie maczugi: (odchylenie od osi pnia, kierunek odchylenia wokół osi, długość 1, zagięcie, długość 2) — w stopniach
# i studach, w układzie maczugi; dobrane tak, żeby w spoczynku żaden nie wchodził w ziemię (sprawdzane liczbowo)
KORZENIE = ((25, 90, 0.7, 30, 0.9), (25, 140, 0.6, -15, 0.8), (22, 220, 0.6, -20, 0.8), (35, 30, 0.6, 30, 0.8),
            (55, 120, 0.5, 30, 0.7), (50, 300, 0.5, 30, 0.7), (10, 0, 0.6, 25, 0.8))


# ---------------------------------------------------------------------------------------------------- animacje
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _fk(p, poza):
    """Kinematyka wprost pozy {kość: {"obrot": …, "przes": …}}: {kość: (obrót w świecie, staw w świecie)}."""
    W = {}
    for n, k in p.kosci.items():                     # rodzic zawsze jest dodany przed dzieckiem
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
    return tuple(round(v, 2) for v in katy_z_macierzy(Q))


def _najnizej(p, W, kosci):
    """Najniższy punkt brył na podanych kościach w pozie W (narożniki skrzynek; kule — punkty na powierzchni)."""
    mn = 1e9
    for c in p.czesci:
        if c["kosc"] not in kosci:
            continue
        R, t = W[c["kosc"]]
        Rc = macierz_obrotu(*c["r"])
        h = [v / 2 for v in c["s"]]
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                for e in (-1, 0, 1):
                    n = math.sqrt(a * a + b * b + e * e) if (c["k"] == "kula" and (a or b or e)) else 1.0
                    lok = razy_wektor(Rc, (a * h[0] / n, b * h[1] / n, e * h[2] / n))
                    q = razy_wektor(R, tuple(c["p"][i] + lok[i] for i in range(3)))
                    mn = min(mn, q[1] + t[1])
    return mn


def _poza(p, poza, maczuga=None, ziemia=True):
    """Poza kluczowa z dopowiedzeniami:
    - ziemia=True: stopy, których poza nie ustawia, stoją płasko (obrót stopy znosi obrót bioder, uda i goleni), a
      biodra jadą w pionie tak, żeby najniższy punkt stóp był na ziemi (y = 0) — przysiady, wypady i odskoki nie
      wbijają stóp w grunt i nie wiszą w powietrzu; ziemia="cialo": całe ciało (bez maczugi) dociągnięte do ziemi
      po najniższym punkcie brył (siad, leżenie); ziemia=False: bez zmian;
    - maczuga=("kier", (x, y, z)): pień celuje w ten kierunek (osie modelu);
      maczuga=("ziemia", (dx, dz), y): pień idzie od pięści w stronę (dx, dz), a środek bryły korzeni leży na
      wysokości y (wleczenie, oparcie o ziemię).
    Kość, której poza nie wymienia, jest w spoczynku."""
    pz = {}
    for n, v in poza.items():
        pz[n] = dict(v) if isinstance(v, dict) else {"obrot": tuple(v)}
    pz.setdefault("Biodra", {}).setdefault("obrot", (0, 0, 0))
    pz["Biodra"].setdefault("przes", (0, 0, 0))
    if ziemia:
        if ziemia is True:
            W = _fk(p, pz)
            for s in ("L", "P"):
                if "Stopa" + s not in pz:
                    Rg = W["Golen" + s][0]
                    pz["Stopa" + s] = {"obrot": tuple(round(v, 2) for v in katy_z_macierzy(
                        tuple(tuple(Rg[j][i] for j in range(3)) for i in range(3))))}
            kosci = ("StopaL", "StopaP")
        else:
            kosci = tuple(n for n in p.kosci if n != "Maczuga")
        dno = _najnizej(p, _fk(p, pz), kosci)
        x, y, z = pz["Biodra"]["przes"]
        pz["Biodra"]["przes"] = (x, round(y - dno, 3), z)
    if maczuga:
        W = _fk(p, pz)
        Rh, chwyt = W["DlonP"][0], W["Maczuga"][1]
        if maczuga[0] == "kier":
            kier = maczuga[1]
        else:
            (dx, dz), y = maczuga[1], maczuga[2]
            dy = y - chwyt[1]
            r = math.sqrt(max(0.0, MACZUGA_DL ** 2 - dy * dy))
            n = math.hypot(dx, dz)
            kier = (dx / n * r, dy, dz / n * r)
        Rt = tuple(tuple(Rh[j][i] for j in range(3)) for i in range(3))
        pz["Maczuga"] = {"obrot": _obrot_miedzy(MACZUGA_KIER, razy_wektor(Rt, kier))}
    pz["_ziemia"] = ziemia
    return pz


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku −170° → +170° przez zero):
    (rx, ry, rz) ≡ (180 − rx, ry + 180, rz + 180), każdy kąt także ± 360."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    kandydaci = [tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)]
    najl = None
    for c in kandydaci:
        c = tuple(round(blisko(c[i], poprz[i]), 2) for i in range(3))
        d = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or d < najl[0] - 1e-6:
            najl = (d, c)
    return najl[1]


NA_ZIEMI_MIN = 1.08      # środek bryły korzeni nigdy niżej (w spoczynku leży na 1,10)


def _slerp(a, b, t):
    a, b = _norm(a), _norm(b)
    c = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(3))))
    kat = math.acos(c)
    if kat < 1e-4:
        return a
    sa, sb = math.sin((1 - t) * kat) / math.sin(kat), math.sin(t * kat) / math.sin(kat)
    return _norm(tuple(sa * a[i] + sb * b[i] for i in range(3)))


def _sekwencja(k, czasy, pozy, wyg=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza; {} = spoczynek). Kości przechodzą między pozami
    z łagodnym wejściem i wyjściem (wyg = {numer pozy: "liniowo"} — odcinek od tej pozy jednostajnie, np. uderzenie);
    pień maczugi przechodzi po łuku między kierunkami z póz (a nie po kątach kości — te przy dużych zamachach
    prowadziłyby go dziwną drogą) i nigdy nie schodzi korzeniami pod ziemię; na odcinkach stania stopy są płasko
    i na ziemi w każdej klatce, a przy siadaniu i leżeniu ciało nie wchodzi w ziemię."""
    p = k.postac
    pozy = [pz if "_ziemia" in pz else _poza(p, pz) for pz in pozy]
    kosci = [n for n in p.kosci if n not in ("Root", "Maczuga")]
    ob, poprz = [], {}
    for pz in pozy:
        d = {}
        for n in kosci + ["Maczuga"]:
            d[n] = _ciaglosc(pz.get(n, {}).get("obrot", (0, 0, 0)), poprz.get(n))
            poprz[n] = d[n]
        ob.append(d)
    kier, wys = [], []
    for pz in pozy:
        W = _fk(p, pz)
        kier.append(_norm(razy_wektor(W["Maczuga"][0], MACZUGA_KIER)))
        wys.append(W["Maczuga"][1][1] + kier[-1][1] * MACZUGA_DL)      # wysokość środka bryły korzeni w pozie
    poprz_m = None
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        e = t if (wyg or {}).get(i) == "liniowo" else t * t * (3 - 2 * t)
        pz = {n: {"obrot": tuple(ob[i][n][j] + (ob[i + 1][n][j] - ob[i][n][j]) * e for j in range(3))} for n in kosci}
        p0, p1 = pozy[i]["Biodra"]["przes"], pozy[i + 1]["Biodra"]["przes"]
        pz["Biodra"]["przes"] = tuple(p0[j] + (p1[j] - p0[j]) * e for j in range(3))
        z0, z1 = pozy[i]["_ziemia"], pozy[i + 1]["_ziemia"]
        if z0 is True and z1 is True:
            W = _fk(p, pz)
            for s in ("L", "P"):
                Rg = W["Golen" + s][0]
                pz["Stopa" + s] = {"obrot": katy_z_macierzy(tuple(tuple(Rg[j][i2] for j in range(3))
                                                                  for i2 in range(3)))}
            dno = _najnizej(p, _fk(p, pz), ("StopaL", "StopaP"))
        else:
            dno = min(0.0, _najnizej(p, _fk(p, pz), tuple(n for n in kosci)))
        x, y, z = pz["Biodra"]["przes"]
        pz["Biodra"]["przes"] = (x, y - dno, z)
        W = _fk(p, pz)
        Rh, chwyt = W["DlonP"][0], W["Maczuga"][1]
        d = _slerp(kier[i], kier[i + 1], e)
        # korzenie nie schodzą niżej niż w niższej z dwóch póz kluczowych (i nigdy niżej niż NA_ZIEMI_MIN)
        dolna = max(NA_ZIEMI_MIN, min(wys[i], wys[i + 1]) - 0.05)
        if chwyt[1] + d[1] * MACZUGA_DL < dolna:
            dy = dolna - chwyt[1]
            r = math.sqrt(max(0.0, MACZUGA_DL ** 2 - dy * dy))
            n = math.hypot(d[0], d[2]) or 1.0
            d = (d[0] / n * r, dy, d[2] / n * r)
        Rt = tuple(tuple(Rh[j][i2] for j in range(3)) for i2 in range(3))
        poprz_m = _ciaglosc(_obrot_miedzy(MACZUGA_KIER, razy_wektor(Rt, d)), poprz_m)
        pz["Maczuga"] = {"obrot": poprz_m}
        for n, v in pz.items():
            k.klucz(f, n, obrot=tuple(round(x, 2) for x in v["obrot"]), wyg="liniowo")
        k.klucz(f, "Biodra", przes=tuple(round(x, 3) for x in pz["Biodra"]["przes"]), wyg="liniowo")


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    ryk(p)


NA_ZIEMI = 1.15          # wysokość środka bryły korzeni, gdy maczuga leży / wlecze się po ziemi


def idle(p):
    """Ciężki oddech (2,4 s): garb unosi się i opada, głowa rozgląda się, żuchwa żuje, lewa pięść lekko się kołysze.
    Prawa ręka stoi spokojnie — korzenie maczugi leżą na ziemi."""
    k = p.klip("idle", 72, petla=True)
    k.cykl("Tulow", "obrot", (2.0, 0, 0), faza=0.0)
    k.cykl("Glowa", "obrot", (-2, 8, 0), faza=0.1)
    k.cykl("Szczeka", "obrot", (4, 0, 0), czestosc=3, srodek=(4, 0, 0))
    k.cykl("RamieL", "obrot", (-3, 0, 2), faza=0.2, srodek=(0, 0, 3))
    k.cykl("PrzedramieL", "obrot", (-4, 0, 0), faza=0.3, srodek=(-6, 0, 0))
    # pochylenie tułowia przesuwa bark z maczugą — ramię oddaje ten ruch, żeby korzenie nie wbijały się w ziemię
    k.cykl("RamieP", "obrot", (-2.0, 0, 0), faza=0.0)
    return k


def ruch(p, dl=48):
    """Powolny, ciężki chód (1,6 s na dwa kroki): przechyły na nogę podporową, opadanie przy szerokim kroku, lewa
    pięść buja się nisko, prawa ręka wlecze maczugę (korzenie szurają po ziemi)."""
    k = p.klip("ruch", dl, petla=True)
    krok = 24.0
    k.cykl("UdoL", "obrot", (krok, 0, 0), faza=0.0)
    k.cykl("UdoP", "obrot", (krok, 0, 0), faza=0.5)
    for s, f in (("L", 0.0), ("P", 0.5)):
        for i in range(13):
            t = i / 12.0
            sn = math.sin(2 * math.pi * (t + f))
            # kolano ugina się, gdy noga idzie do przodu (przenoszenie); stopa trzyma się płasko
            kol = max(0.0, -math.sin(2 * math.pi * (t + f) - 0.6)) * 36
            k.klucz(dl * t, "Golen" + s, obrot=(kol, 0, 0))
            k.klucz(dl * t, "Stopa" + s, obrot=(-krok * sn - kol, 0, 0))
    k.cykl("Biodra", "obrot", (0, 0, 5), faza=0.0)
    k.cykl("Biodra", "obrot", (0, 6, 0), faza=0.0)
    k.cykl("Biodra", "przes", (0, 0.1, 0), czestosc=2, faza=0.25, srodek=(0, 0.1, 0))
    k.cykl("Tulow", "obrot", (0, -7, -3), faza=0.0, srodek=(4, 0, 0))
    k.cykl("Tulow", "obrot", (2, 0, 0), czestosc=2, faza=0.0)
    k.cykl("Glowa", "obrot", (0, 2, 3), faza=0.0, srodek=(-4, 0, 0))
    k.cykl("Szczeka", "obrot", (3, 0, 0), czestosc=2, srodek=(3, 0, 0))
    k.cykl("RamieL", "obrot", (24, 0, 0), faza=0.5, srodek=(0, 0, 4))
    k.cykl("PrzedramieL", "obrot", (-6, 0, 0), faza=0.4, srodek=(-10, 0, 0))
    k.cykl("RamieP", "obrot", (5, 0, 0), faza=0.0, srodek=(-3, 0, -2))
    # w chodzie pień nie leży z boku jak w spoczynku, tylko wlecze się za trollem (korzenie szurają po ziemi)
    k.cykl("Maczuga", "obrot", (-4, 0, 0), faza=0.0, srodek=_obrot_miedzy(MACZUGA_KIER, WLECZ_KIER))
    return k


def atak(p, dl=36):
    """Zwykły cios (1,2 s): skręt w prawo, maczuga zarzucona na prawy bark jak kij (kl. 10) → szeroki, płaski łuk przed
    sobą w lewo, trafienie na wysokości piersi gracza w kl. 15 → przelot, maczuga opada i wraca na ziemię. Prawa ręka
    pracuje na zewnątrz barku, więc ani ona, ani pień nie przechodzą przez głowę."""
    k = p.klip("atak", dl, petla=False)
    oderwanie = _poza(p, {"Tulow": (-3, -8, 0), "RamieP": (6, 0, -12)}, maczuga=("ziemia", SPOCZ_XZ, 1.9))
    wziecie = _poza(p, {"Biodra": (0, -8, 0), "Tulow": (-6, -22, 0), "Glowa": (-6, 16, 0), "Szczeka": (6, 0, 0),
                        "RamieP": (-55, 0, -38), "PrzedramieP": (-110, 0, 0),
                        "RamieL": (-25, 0, 22), "PrzedramieL": (-35, 0, 0), "UdoP": (6, 0, 0), "UdoL": (-6, 0, 0)},
                    maczuga=("kier", (-0.35, 0.3, -0.9)))
    uderzenie = {"Biodra": (0, 12, 0), "Tulow": (2, 24, 0), "Glowa": (-6, -18, 0), "Szczeka": (16, 0, 0),
                 "RamieP": (-52, 0, -12), "PrzedramieP": (-18, 0, 0),
                 "RamieL": (15, 0, 18), "PrzedramieL": (-15, 0, 0),
                 "UdoL": (-24, 0, 0), "GolenL": (18, 0, 0), "UdoP": (14, 0, 0)}
    przelot = dict(uderzenie, Tulow=(6, 34, 0), RamieP=(-42, 0, 0))
    opada = {"Biodra": (0, 6, 0), "Tulow": (8, 16, 0), "Glowa": (0, -8, 0), "Szczeka": (8, 0, 0),
             "RamieP": (-30, 0, -14), "PrzedramieP": (-15, 0, 0), "RamieL": (6, 0, 8),
             "UdoL": (-12, 0, 0), "GolenL": (8, 0, 0)}
    ladowanie = _poza(p, {"Tulow": (1, 3, 0), "RamieP": (-6, 0, -6), "PrzedramieP": (-5, 0, 0)},
                      maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 0.6))
    # w połowie zamachu pień idzie przez prawy bok (a nie za głową) — łuk: za barkiem → w bok → przed sobą → w lewo
    polowa = _poza(p, {"Biodra": (0, 0, 0), "Tulow": (4, 0, 0), "Glowa": (-2, 4, 0), "Szczeka": (12, 0, 0),
                       "RamieP": (-55, 0, -28), "PrzedramieP": (-55, 0, 0), "RamieL": (-5, 0, 20),
                       "PrzedramieL": (-25, 0, 0), "UdoL": (-14, 0, 0), "GolenL": (10, 0, 0), "UdoP": (10, 0, 0)},
                   maczuga=("kier", (-0.75, 0.2, 0.65)))
    pozy = ({}, oderwanie, wziecie, polowa, _poza(p, uderzenie, maczuga=("kier", (0.9, -0.12, 0.42))),
            _poza(p, przelot, maczuga=("kier", (0.92, -0.25, 0.1))),
            _poza(p, opada, maczuga=("ziemia", (0.1, 1.0), NA_ZIEMI + 0.9)), ladowanie, {})
    _sekwencja(k, (0, 4, 10, 13, 16, 20, 26, 32, dl), pozy, wyg={2: "liniowo", 3: "liniowo"})
    return k


def umiejetnosc(p, dl=60):
    """Ogłuszające uderzenie (2 s): troll unosi maczugę oburącz nad głowę (kl. 14), napina się z pniem leżącym
    poziomo za karkiem i ryczy (kl. 22), wali nią z góry w ziemię przed sobą z przysiadem — lewa pięść też uderza
    w ziemię (kl. 28) — drży w zatrzymaniu i powoli wstaje. Prawa ręka i pień idą w płaszczyźnie prawego barku,
    z dala od głowy."""
    k = p.klip("umiejetnosc", dl, petla=False)
    start = _poza(p, {"Tulow": (-4, 0, 0), "RamieP": (-40, 0, -14), "RamieL": (-30, 0, 10)},
                  maczuga=("ziemia", SPOCZ_XZ, 2.4))
    gora = _poza(p, {"Biodra": {"przes": (0, 0, -0.1)}, "Tulow": (-10, 0, 0), "Glowa": (-10, 0, 0),
                     "Szczeka": (14, 0, 0), "RamieP": (-135, 0, -15), "PrzedramieP": (-85, 0, 0),
                     "RamieL": (-135, 0, 15), "PrzedramieL": (-85, 0, 0)},
                 maczuga=("kier", (-0.1, 0.25, -0.96)))
    zamach = _poza(p, {"Biodra": {"przes": (0, 0, -0.15)}, "Tulow": (-16, 0, 0), "Glowa": (-16, 0, 0),
                       "Szczeka": (28, 0, 0), "RamieP": (-140, 0, -12), "PrzedramieP": (-120, 0, 0),
                       "RamieL": (-140, 0, 14), "PrzedramieL": (-115, 0, 0)},
                   maczuga=("kier", (-0.1, -0.1, -1.0)))
    # pień przechodzi pionowo nad głową (w płaszczyźnie prawego barku), nie bokiem
    nad_glowa = _poza(p, {"Tulow": (8, 0, 0), "Glowa": (-12, 0, 0), "Szczeka": (24, 0, 0),
                          "RamieP": (-100, 0, -12), "PrzedramieP": (-35, 0, 0),
                          "RamieL": (-100, 0, 14), "PrzedramieL": (-35, 0, 0)},
                      maczuga=("kier", (-0.1, 0.6, 0.8)))
    przysiad = {"Biodra": {"przes": (0, 0, 0.35)}, "Tulow": (32, 0, 0), "Glowa": (-14, 0, 0), "Szczeka": (12, 0, 0),
                "UdoL": (-40, 0, 8), "GolenL": (55, 0, 0), "UdoP": (-40, 0, -8), "GolenP": (55, 0, 0),
                "RamieP": (-30, 0, -8), "PrzedramieP": (-60, 0, 0), "RamieL": (-47, 0, 10), "PrzedramieL": (-10, 0, 0)}
    uderzenie = _poza(p, przysiad, maczuga=("ziemia", (0.0, 1.0), NA_ZIEMI + 0.2))
    odbicie = _poza(p, dict(przysiad, Tulow=(28, 0, 0)), maczuga=("ziemia", (0.0, 1.0), NA_ZIEMI + 0.5))
    trzymanie = _poza(p, dict(przysiad, Tulow=(30, 0, 0), Glowa=(-18, 0, 0), Szczeka=(20, 0, 0)),
                      maczuga=("ziemia", (0.0, 1.0), NA_ZIEMI + 0.3))
    unosi = _poza(p, dict(przysiad, Tulow=(20, 0, 0), RamieP=(-40, 0, -22), UdoL=(-25, 0, 6), GolenL=(35, 0, 0),
                          UdoP=(-25, 0, -6), GolenP=(35, 0, 0)), maczuga=("kier", (-0.3, 0.2, 0.93)))
    wstaje = _poza(p, {"Tulow": (10, 0, 0), "Glowa": (-4, 0, 0), "UdoL": (-10, 0, 0), "GolenL": (14, 0, 0),
                       "UdoP": (-10, 0, 0), "GolenP": (14, 0, 0), "RamieP": (-22, 0, -14),
                       "PrzedramieP": (-10, 0, 0), "RamieL": (-10, 0, 6)},
                   maczuga=("ziemia", (-0.35, 0.6), NA_ZIEMI + 0.9))
    ladowanie = _poza(p, {"Tulow": (2, 0, 0), "RamieP": (-6, 0, -6), "PrzedramieP": (-5, 0, 0)},
                      maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 0.35))
    _sekwencja(k, (0, 5, 14, 22, 25, 29, 32, 42, 47, 53, 57, dl),
               ({}, start, gora, zamach, nad_glowa, uderzenie, odbicie, trzymanie, unosi, wstaje, ladowanie, {}),
               wyg={3: "liniowo", 4: "liniowo"})
    return k


def trafienie(p, dl=20):
    """Reakcja na cios (0,67 s): szarpnięcie tułowia i głowy w tył (kl. 4), ręce odlatują, cofnięcie, powrót."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = _poza(p, {"Biodra": {"obrot": (-4, 0, 0), "przes": (0, 0, -0.45)}, "Tulow": (-16, 6, 0),
                      "Glowa": (-22, -8, 6), "Szczeka": (18, 0, 0), "RamieL": (-18, 0, 26), "RamieP": (-14, 0, -18),
                      "PrzedramieL": (-30, 0, 0), "PrzedramieP": (-20, 0, 0), "UdoP": (14, 0, 0),
                      "GolenP": (12, 0, 0), "UdoL": (-6, 0, 0)},
                  maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 1.0))
    wraca = _poza(p, {"Biodra": {"obrot": (-1, 0, 0), "przes": (0, 0, -0.2)}, "Tulow": (-6, 2, 0),
                      "Glowa": (-6, 0, 0), "Szczeka": (6, 0, 0), "RamieL": (-6, 0, 8), "RamieP": (-4, 0, -6),
                      "PrzedramieL": (-10, 0, 0), "PrzedramieP": (-8, 0, 0), "UdoP": (6, 0, 0), "GolenP": (4, 0, 0)},
                  maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 0.4))
    _sekwencja(k, (0, 4, 10, dl), ({}, szarp, wraca, {}))
    return k


def unik(p, dl=30):
    """Unik (1 s): ciężki odskok w lewo (+X) z przechyłem i ugiętymi nogami, chwila w bok, powrót na linię ciosu.
    Maczuga ciągnie się za nim po ziemi."""
    k = p.klip("unik", dl, petla=False)
    bok = {"Biodra": {"obrot": (0, 8, 8), "przes": (1.6, 0, -0.2)}, "Tulow": (6, 0, 12), "Glowa": (0, -10, -14),
           "UdoL": (-14, 0, 14), "GolenL": (26, 0, 0), "UdoP": (-10, 0, 14), "GolenP": (22, 0, 0),
           "RamieL": (-10, 0, 30), "RamieP": (-14, 0, -8), "PrzedramieP": (-10, 0, 0)}
    bok2 = dict(bok, Biodra={"obrot": (0, 6, 6), "przes": (1.5, 0, -0.2)}, Tulow=(5, 0, 10))
    _sekwencja(k, (0, 8, 16, dl), ({}, _poza(p, bok, maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 0.15)),
                                   _poza(p, bok2, maczuga=("ziemia", SPOCZ_XZ, NA_ZIEMI + 0.1)), {}))
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): chwieje się, kolana się uginają, siada ciężko i pada na plecy; maczuga wypada z dłoni i kładzie
    się obok. Ostatnia klatka: leży (do utrzymania w grze)."""
    k = p.klip("upadek", dl, petla=False)
    chwiej = _poza(p, {"Biodra": {"obrot": (-6, 0, 4), "przes": (0, 0, -0.2)}, "Tulow": (-8, 0, 6),
                       "Glowa": (-14, 10, 8), "Szczeka": (14, 0, 0), "UdoL": (-4, 0, 4), "GolenL": (6, 0, 0),
                       "UdoP": (4, 0, -4), "RamieL": (-20, 0, 30), "PrzedramieL": (-20, 0, 0),
                       "RamieP": (-15, 0, -30), "PrzedramieP": (-15, 0, 0)},
                   maczuga=("ziemia", WLECZ_XZ, NA_ZIEMI + 0.7))
    przysiad = _poza(p, {"Biodra": {"obrot": (-10, 0, -3), "przes": (0, 0, -0.4)}, "Tulow": (14, 0, -4),
                         "Glowa": (10, -6, 0), "Szczeka": (10, 0, 0),
                         "UdoL": (-60, 0, 10), "GolenL": (95, 0, 0), "UdoP": (-55, 0, -10), "GolenP": (90, 0, 0),
                         "RamieL": (-30, 0, 20), "PrzedramieL": (-10, 0, 0), "RamieP": (-25, 0, -20),
                         "PrzedramieP": (-10, 0, 0)},
                     maczuga=("ziemia", WLECZ_XZ, NA_ZIEMI + 0.6))
    siad = _poza(p, {"Biodra": {"obrot": (-45, 0, 0), "przes": (0, 0, -0.8)}, "Tulow": (6, 0, 0),
                     "Szczeka": (20, 0, 0), "UdoL": (-35, 0, 14), "GolenL": (40, 0, 0), "StopaL": (-10, 0, 0),
                     "UdoP": (-30, 0, -14), "GolenP": (40, 0, 0), "StopaP": (-10, 0, 0),
                     "RamieL": (-50, 0, 40), "PrzedramieL": (-20, 0, 0), "RamieP": (-45, 0, -40),
                     "PrzedramieP": (-20, 0, 0)}, ziemia="cialo",
                 maczuga=("ziemia", (-0.4, 0.9), NA_ZIEMI + 1.0))
    # leży na plecach: tułów płasko (pochylenie brył 24° znosi Tulow −30), twarz do nieba, głowa przekręcona w bok,
    # ręce i nogi rozrzucone i opuszczone na ziemię (stopy na ziemi, nie w powietrzu)
    lezy = {"Biodra": {"obrot": (-80, 0, 0), "przes": (0, 0, -1.0)}, "Tulow": (-30, 0, 0), "Glowa": (6, 24, 0),
            "Szczeka": (24, 0, 0), "UdoL": (26, 0, 16), "GolenL": (10, 0, 0), "UdoP": (26, 0, -16),
            "GolenP": (12, 0, 0), "RamieL": (60, 0, 45), "PrzedramieL": (-8, 0, 0), "RamieP": (60, 0, -45),
            "PrzedramieP": (-8, 0, 0)}
    odbicie = dict(lezy, Biodra={"obrot": (-76, 0, 0), "przes": (0, 0.12, -1.0)}, Tulow=(-34, 0, 0))
    lezy = _poza(p, lezy, ziemia="cialo", maczuga=("ziemia", (-0.3, 1.0), 1.95))
    odbicie = _poza(p, odbicie, ziemia="cialo", maczuga=("ziemia", (-0.3, 1.0), 2.2))
    polprzysiad = _poza(p, {"Biodra": {"obrot": (-8, 0, 0), "przes": (0, 0, -0.3)}, "Tulow": (4, 0, 0),
                            "Glowa": (0, 0, 4), "Szczeka": (12, 0, 0), "UdoL": (-30, 0, 8), "GolenL": (45, 0, 0),
                            "UdoP": (-28, 0, -8), "GolenP": (44, 0, 0), "RamieL": (-25, 0, 25),
                            "RamieP": (-20, 0, -25), "PrzedramieP": (-12, 0, 0)},
                        maczuga=("ziemia", WLECZ_XZ, NA_ZIEMI + 0.6))
    osuwa = _poza(p, {"Biodra": {"obrot": (-25, 0, 0), "przes": (0, 0, -0.6)}, "Tulow": (10, 0, 0),
                      "Szczeka": (16, 0, 0), "UdoL": (-55, 0, 12), "GolenL": (75, 0, 0), "UdoP": (-50, 0, -12),
                      "GolenP": (72, 0, 0), "RamieL": (-40, 0, 30), "PrzedramieL": (-15, 0, 0),
                      "RamieP": (-35, 0, -30), "PrzedramieP": (-15, 0, 0)}, ziemia="cialo",
                  maczuga=("ziemia", (-0.5, 0.85), NA_ZIEMI + 0.7))
    oderwanie = _poza(p, {"Tulow": (-3, 0, 2), "RamieP": (-4, 0, -14)}, maczuga=("ziemia", SPOCZ_XZ, 1.9))
    _sekwencja(k, (0, 4, 10, 17, 24, 30, 36, 46, 52, dl),
               ({}, oderwanie, chwiej, polprzysiad, przysiad, osuwa, siad, lezy, odbicie, lezy))
    return k


def ryk(p, dl=60):
    """Ryk po wygranej (pętla 2 s): odchylona głowa, szeroko otwarta paszcza, maczuga uniesiona w bok-w górę, lewa
    pięść w górze; dwa „pompnięcia” na pętlę."""
    k = p.klip("ryk", dl, petla=True)
    gora = _poza(p, {"Tulow": (-12, 0, 0), "Glowa": (-24, 0, 0), "Szczeka": (34, 0, 0),
                     "RamieP": (-70, 0, -70), "PrzedramieP": (-70, 0, 0),
                     "RamieL": (-140, 0, 40), "PrzedramieL": (-40, 0, 0)}, maczuga=("kier", (-0.85, 0.47, 0.2)))
    nizej = _poza(p, {"Tulow": (-2, 0, 0), "Glowa": (-12, 0, 0), "Szczeka": (18, 0, 0),
                      "UdoL": (-8, 0, 0), "GolenL": (14, 0, 0), "UdoP": (-8, 0, 0), "GolenP": (14, 0, 0),
                      "RamieP": (-55, 0, -60), "PrzedramieP": (-80, 0, 0),
                      "RamieL": (-110, 0, 50), "PrzedramieL": (-70, 0, 0)}, maczuga=("kier", (-0.88, 0.38, 0.12)))
    # pień wzniesiony w bok i w górę, prawie prostopadle do kamery — widać całą długość (wcześniej celował w górę
    # i do tyłu, a w kadrze 3/4 skracał się do „marchewki” nad pięścią)
    _sekwencja(k, (0, 15, 30, 45, dl), (nizej, gora, nizej, gora, nizej))
    return k
