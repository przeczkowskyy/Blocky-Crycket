# -*- coding: utf-8 -*-
"""LEŚNY SLIME — zwykły przeciwnik lasu: pulchna, soczyście zielona kostka galarety z uroczą buzią i kiełkiem na czubku.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/lesny_slime.py --wyj <folder> --klip umiejetnosc

Opis z danych walki (tools/walka/dane_walki.json, id „lesny_slime”): półprzezroczysty, zielony sześcian galarety
z liściem i małym grzybkiem zatopionymi w środku; podskakuje i zostawia lepkie ślady. Dużo życia, słabe ciosy;
umiejętność „kwaśny plusk” zdziera pancerz.

Wersja 2 (14.11.2026, uwaga właściciela: „ma być bardziej cute”): przeciwnik, ale uroczy, nie groźny.
- Bryła: sześcian 2,7 × 2,7 × 2,7 studa (uwaga Karola z 15.11; pet 2,4 × 2,25 × 2,35, gracz 5,7) ze ścięciem
  krawędzi — przysadzista jak galaretka. Na czubku kiełek z dwoma listkami, który kiwa się sprężyście przy każdym
  ruchu (liczone symulacją sprężyny z ruchu ciała).
- Twarz: duże, okrągłe, błyszczące oczy (czarne, z jaśniejszą zielenią u dołu i dwoma białymi błyskami) osadzone
  nisko i szeroko, malutki uśmiech tuż pod nimi, różowe rumieńce. Dużo „czoła” nad oczami.
- Mimika: pięć wersji oczu (otwarte, zamknięte przy mrugnięciu, szczęśliwe „łuki”, zaciśnięte „> <”, wielkie
  zaskoczone) i cztery wersje ust (uśmiech, „o”, otwarty uśmiech z języczkiem, falka). Każda wersja to sztywna
  bryła na własnej kości schowana tuż pod przednią ścianą; klip wysuwa tę, którą trzeba. Policzki nadymają się
  (kość Policzki).
- Kolor: jasna, soczysta zieleń (odróżnia od niebieskiego peta), ciepłe akcenty: rumieńce, języczek, czerwony
  grzybek w środku. Kwas (kula, kałuża) to limonkowa żółć.
- Galareta jest jednolicie zielona: bez płytek „rdzenia” na ścianach (płytki dostawały własny obrys i z przodu
  wyglądały jak ekran telewizorka w ramce). Miękkość dają mocne ścięcia, światło i odblask.
- Liść i grzybek „widać przez galaretę” z tyłu i na prawym boku (rzuty z jednego położenia w środku);
  prawdziwy liść i grzybek (kości Lisc i Grzybek) wychodzą na wierzch, gdy slime rozleje się w kałużę (upadek).

Szkielet (własny, typ „stwor”; L = lewa = +X):
    Root
    ├── Cialo          staw na ziemi pod środkiem — skok (przes) i przechył (obrót) całej galarety
    │   ├── Dol        cała galareta z rumieńcami i rzutami liścia/grzybka (siatka Dol_Geo, wagi Dol/Gora)
    │   ├── Gora       góra galarety — zgniatanie, rozciąganie, nadymanie i rozlanie
    │   │   └── Kielek             kiełek na czubku (kiwa się)
    │   │       └── ListekL, ListekP   listki kiełka (machają przy skokach)
    │   ├── Oczy, Powieki, OczyRad, OczyZac, OczyWiel   wersje oczu (otwarte / mrug / szczęśliwe / zaciśnięte / wielkie)
    │   ├── Usta, UstaO, UstaRad, UstaFala              wersje ust (uśmiech / „o” / otwarty uśmiech / falka)
    │   ├── Policzki                     nadęte policzki (kwaśny plusk)
    │   ├── BokL, BokP, Przod, Tyl       brzuszki (poszerzenie przy zgnieceniu, płaty kałuży przy upadku)
    │   ├── Lisc, Grzybek                prawdziwy liść i grzybek w środku (widać je po rozlaniu)
    │   ├── Kula                         bańka kwasu (umiejętność): w spoczynku schowana za ustami
    │   └── Plusk                        kałuża kwasu po trafieniu bańki: w spoczynku schowana w podstawie
    └── KroplaL, KroplaP, KroplaT        okrągłe kropelki galarety przy podstawie
Bryły nie mają kanału skali — zgniatanie robi przesunięcie kości Gora (siatka skórowana na dwóch kościach).

Klipy (30 kl./s; patrzy w +Z i w tę stronę atakuje). Klucz w każdej klatce (_sekwencja): twarz i schowane bryły
jadą z galaretą proporcjonalnie do wysokości, galareta nie wchodzi pod ziemię, a kiełek dostaje sprężyste kiwanie
z symulacji. Długości i nazwy klipów jak w wersji 1 (odtwarzacz walki).
  idle (pętla 2 s): radosne bujanie na boki z oddechem, mrugnięcie, kiełek się kiwa.
  ruch (pętla 0,8 s): mały hopek z otwartym uśmiechem w locie.
  atak (1 s): rozpęd z zaciśniętymi oczami, niezdarne pacnięcie brzuszkiem w kl. 13 ok. 1,85 studa przed sobą,
    odbicie ze zdziwioną minką.
  umiejetnosc (kwaśny plusk, 2,2 s): nadyma policzki, z buzi „o” wychodzi świecąca bańka kwasu, pluje nią
    (kl. 21), bańka leci łukiem i w kl. 31 rozpryskuje się w kałużę ok. 4,3 studa przed nim; potem zadowolona
    minka (szczęśliwe oczy, otwarty uśmiech), kałuża wsiąka.
  trafienie (0,6 s): wielkie zaskoczone oczy, buzia „o”, odskok w tył z podskokiem.
  unik (0,9 s): hopek w lewo z piruetem (pełny obrót), szczęśliwe oczy w locie, powrót ślizgiem.
  upadek (2 s): zaskoczenie, chwianie z zaciśniętymi oczami, rozpływa się w płaską kałużę; oczka kładą się na
    wierzchu kałuży, otwierają się i mrugają, buzia „o” („ojej”), kiełek więdnie w tył. Kończy się leżeniem.
  wiwat (pętla 1,33 s): dwa podskoki z szczęśliwymi oczami i otwartym uśmiechem, kołysanie na boki.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, macierz_obrotu, razy_wektor

ID = "lesny_slime"

# ------------------------------------------------------------------------------------------- wymiary (studs)
W, H, D = 2.7, 2.7, 2.7          # SZEŚCIAN (uwaga Karola z 15.11: „powinien być sześcianowy”); pet: 2,4 × 2,25 × 2,35
FAZA = 0.32                      # ścięcie krawędzi: miękko, ale bryła ma czytać się jako sześcian
ZF = D / 2                       # przednia ściana

# twarz (wysokości od ziemi w spoczynku)
YO, XO = 1.32, 0.62              # środek oczu, odległość oka od środka (nisko i szeroko)
OKO = (0.56, 0.68)               # oko: szer, wys
YU = 0.86                        # środek ust (tuż pod oczami)
YP, XP = 0.82, 0.84              # rumieńce / policzki (na wysokości ust, z boku pod oczami)
Z_TW = 0.045                     # bryły twarzy: środek 0,045 przed przednią ścianą (wystają 0,03–0,06)
POKAZ = 0.1                      # o ile wysuwa się schowana wersja oczu/ust (schowana: przód 0,04 pod ścianą)

OCZY = (0.0, YO, ZF)             # wspólny staw wszystkich wersji oczu
USTA = (0.0, YU, ZF)             # wspólny staw wszystkich wersji ust
POLICZKI = (0.0, YP, ZF)
KULA = (0.0, YU, ZF - 0.45)      # staw bańki kwasu = jej środek (schowana za ustami)
R_KULA = 0.28
LISC = (0.3, 1.62, -0.25)        # środek liścia w kostce
GRZYB = (-0.72, 0.42, -0.45)     # podstawa grzybka
GRZYB_H = (0.36, 0.32)           # wysokość trzonu i kapelusza grzybka
GRZYB_SZ = (0.24, 0.76)          # szerokość trzonu i kapelusza
PLUSK_STAW = (0.0, 0.1, 0.0)     # schowek kałuży w podstawie galarety
PLUSK_Z = 4.3                    # gdzie spada bańka kwasu (od środka slime'a, w +Z)
KIELEK = (0.0, H, -0.2)          # podstawa kiełka na wierzchu (lekko z tyłu, żeby nie zasłaniał twarzy z góry)
KIELEK_H = 0.4                   # wysokość łodyżki (tu siedzą listki)

T_BRZ = 0.5                      # grubość brzuszka (w kierunku wysuwania)
H_BRZ = 0.7                      # wysokość brzuszka
Y_BRZ = 0.55                     # środek brzuszka od ziemi
_G = T_BRZ / 2 + 0.03            # brzuszek w spoczynku: zewnętrzna ściana 0,03 pod ścianą galarety
BOKI = {  # kość: (staw = środek schowanego brzuszka, kierunek wysuwania)
    "BokL": ((W / 2 - _G, Y_BRZ, 0.0), (1, 0, 0)),
    "BokP": ((-W / 2 + _G, Y_BRZ, 0.0), (-1, 0, 0)),
    "Przod": ((0.0, 0.45, ZF - _G - 0.3), (0, 0, 1)),   # głębiej: inaczej przebijał dolne ścięcie („drugi uśmiech”)
    "Tyl": ((0.0, Y_BRZ, -ZF + _G), (0, 0, -1)),
}
KROPLE = {"KroplaL": (1.75, 0.85, 0.2), "KroplaP": (-1.7, 1.05, 0.17), "KroplaT": (1.2, -1.7, 0.16)}  # x, z, promień

PALETA = {
    "skorupka": "7EDB57",      # galareta: jednolita, soczysta jasna zieleń, lekko świecąca
    "kropla": "B4F07F",        # kropelki przy podstawie (jaśniejsze, jak odrobina galarety)
    "rdzen": "7EDB57",         # nadęte policzki (ten sam kolor co galareta)
    "rdzen_cien": "5CB842",    # żyłka liścia w galarecie
    "tusz": "17220F",          # oczy, usta
    "oko_dol": "3F8A3A",       # jaśniejsza zieleń w dole oka (szklisty połysk)
    "bialko": "FAFFF4",        # białka wielkich, zaskoczonych oczu
    "odblask": "FAFFF0",       # białe błyski i odblaski
    "rumieniec": "FF8DA1",     # rumieńce (ciepły akcent)
    "jezyk": "FF6F8E",         # języczek
    "kielek": "A6E34F",        # listki kiełka
    "kielek_cien": "6DB536",   # żyłka listka, łodyżka
    "lisc": "E2A431",          # bursztynowy liść (prawdziwy, po rozlaniu)
    "lisc_w": "C9B840",        # liść widziany przez zieloną galaretę
    "grzyb": "E04A3C",         # kapelusz grzybka
    "grzyb_w": "C9673F",       # kapelusz widziany przez galaretę
    "trzon": "F5EBC8",         # trzon grzybka i kropki
    "trzon_w": "D8E3A6",       # trzon widziany przez galaretę
    "kwas": "EEFF2E",          # AKCENT: kwas (bańka, kałuża)
}

SLABOSCI = [
    "Brak prawdziwej przezroczystości (jeden materiał na model): galareta jest jednolicie zielona (bez płytek "
    "„rdzenia”, które robiły z przodu ekran w ramce), a liść i grzybek „w środku” to płaskie rzuty tylko z tyłu "
    "i na prawym boku (−X). Z przodu, z lewego boku i z góry ich nie widać. Gdy slime obraca się w uniku, obrys "
    "renderu rysuje wokół tych naklejek ciemny cień (w grze obrysu nie ma). W grze można dać galarecie materiał "
    "Glass i zostawić same prawdziwe bryły liścia i grzybka (kości Lisc, Grzybek).",
    "Mimika to podmiana sztywnych brył: pięć wersji oczu i cztery wersje ust siedzą na własnych kościach (schowane "
    "0,1 studa głębiej, przód 0,04 pod przednią ścianą), a klip wysuwa jedną z nich. Zmiana miny trwa ok. jednej "
    "klatki (waga wyostrzona w środku odcinka) — bez klatki pośredniej, jak w kreskówce. Oczy i usta nie zgniatają "
    "się razem z galaretą (jadą z nią w górę i w dół), rumieńce na ścianie tak. W Roblox obrys (Highlight) obejmie "
    "tylko sylwetkę — kreski oczu i ust nie będą miały obwódki z renderu.",
    "Galareta jest skórowana na dwóch kościach (Dol, Gora) — import wag do Roblox nie był testowany.",
    "Kiełek kiwa się z prostej symulacji sprężyny liczonej z ruchu ciała (wypalonej w klucze), nie z fizyki gry; "
    "w pętlach symulacja biegnie trzy razy, żeby szew pętli był gładki, ale może zostać drobny skok kąta. "
    "W ostrym ataku łodyżka kładzie się płasko (ograniczenie 38°), a listki mogą wtedy na chwilę wchodzić w wierzch galarety.",
    "Rozlanie (upadek) to spłaszczona kostka (0,5 studa) z czterema płaskimi płatami dookoła — z bliska środek "
    "ma prostokątny obrys. Oczka leżą na wierzchu odchylone o 40° (dolny brzeg lekko zanurzony), buzia przed nimi; "
    "w klatkach ok. 36–40 oczy przechodzą przez przednią krawędź i na 1–2 klatki chowają się do połowy, a przedni "
    "płat przejeżdża przed buzią. Rumieńce na ścianie spłaszczają się z galaretą do różowych kresek.",
    "Unik ma pełny piruet (obrót Y od 0 do 360°): ostatnia klatka ma Y = 360°, czyli tę samą pozę co 0° — "
    "odtwarzacz, który miesza kąty Eulera zamiast obrotów (CFrame/kwaternion), mógłby zakręcić slime'em z powrotem.",
    "Kałuża kwasu z umiejętności wsiąka na końcu w ziemię i w ostatniej klatce wraca skokiem do schowka w podstawie "
    "slime'a; prawdziwy rozprysk (cząsteczki) dorobić efektem na PluskAttachment.",
    "Kości nie są R15 (własny szkielet: Root + 27 kości) — klipy importuje się na własny rig; Studio nie testowane.",
    "Świecenie galarety i kwasu jest tylko w teksturze-palecie (emisja) — w grze dać Neon albo PointLight.",
    "Ruch to podskok w miejscu (bez przesuwania korzenia); szybkość przesuwania ustawia gra.",
    "Kadr filmów jest wspólny dla wszystkich klipów i obejmuje lot bańki i kałużę ok. 4,3 studa przed slime'em, "
    "więc w filmach slime jest mały; bliżej: plansza i kadr bohaterski.",
    "Klipy to szkice (0,6–2,2 s), nie gotowa animacja.",
]


# ---------------------------------------------------------------------------------------------- pomocnicze
def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _krzyz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _skal(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _kreska(p, nazwa, pkt, grub, z, kolor="tusz", mat="polysk"):
    """Gruba linia łamana przez punkty (x, y) na płaszczyźnie twarzy, z okrągłymi stawami (krążki) — łuki oczu,
    uśmiech, falka."""
    for i in range(len(pkt) - 1):
        (x0, y0), (x1, y1) = pkt[i], pkt[i + 1]
        dl = math.hypot(x1 - x0, y1 - y0)
        kat = math.degrees(math.atan2(y1 - y0, x1 - x0))
        p.blok("%s %d" % (nazwa, i), ((x0 + x1) / 2, (y0 + y1) / 2, z), (dl, grub, 0.03), kolor, mat,
               rot=(0, 0, kat), faza=0.0)
    for i, (x, y) in enumerate(pkt[1:-1]):       # tylko stawy w środku (każda bryła dostaje własny obrys)
        p.walec("%s staw %d" % (nazwa, i), (x, y, z), (grub, 0.03, grub), kolor, mat, rot=(90, 0, 0), faza=0.0,
                segm=8)


def _luk(cx, cy, a, b, t0, t1, n=6):
    """Punkty łuku elipsy (kąty w stopniach)."""
    return [(cx + a * math.cos(math.radians(t0 + (t1 - t0) * i / n)),
             cy + b * math.sin(math.radians(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]


def _kropelka(p, nazwa, r):
    """Okrągła kropelka galarety z białym błyskiem (leży na ziemi)."""
    p.kula(nazwa + " kulka", (0, r * 0.82, 0), (2 * r, 1.64 * r, 2 * r), "kropla", "poswiata", segm=12)
    p.walec(nazwa + " blysk", (-r * 0.35, r * 1.15, r * 0.62), (r * 0.36, 0.02, r * 0.36), "odblask", "swiecacy",
            rot=(55, 0, 0), faza=0.0, segm=8)


# ściany kostki: (obrót układu ściany: lokalne +Z = normalna, oś u, oś v, odległość od środka)
SCIANY = {
    "przod": ((0, 0, 0), (1, 0, 0), (0, 1, 0), D / 2),
    "bokL": ((0, 90, 0), (0, 0, -1), (0, 1, 0), W / 2),
    "bokP": ((0, -90, 0), (0, 0, 1), (0, 1, 0), W / 2),
    "tyl": ((0, 180, 0), (-1, 0, 0), (0, 1, 0), D / 2),
    "wierzch": ((-90, 0, 0), (1, 0, 0), (0, 0, -1), H / 2),
}
NORMALNE = {"przod": (0, 0, 1), "bokL": (1, 0, 0), "bokP": (-1, 0, 0), "tyl": (0, 0, -1), "wierzch": (0, 1, 0)}

# liść w środku: oś długa a, oś szeroka b (w kostce, ukośnie, żeby czytał się z każdej strony)
_LN = _norm((0.6, 1.0, 0.7))
_LA = _norm(_krzyz(_LN, _norm((0.3, 0.0, 1.0))))
_LB = _krzyz(_LN, _LA)
LISC_DL, LISC_SZ = 1.3, 0.66


def _rzut_lisc(p, sc):
    """Rzut liścia (elipsa + żyłka + ogonek) na ścianę sc, w przygaszonym kolorze."""
    obr, eu, ev, odl = SCIANY[sc]
    c = (LISC[0], LISC[1] - H / 2, LISC[2])          # układ środka kostki
    u, v = _skal(c, eu), _skal(c, ev)
    au, av = _skal(_LA, eu), _skal(_LA, ev)
    bu, bv = _skal(_LB, eu), _skal(_LB, ev)
    dl = LISC_DL * math.hypot(au, av)
    kat = math.degrees(math.atan2(av, au))
    if math.hypot(au, av) > 1e-6:
        nu, nv = -av / math.hypot(au, av), au / math.hypot(au, av)
    else:
        nu, nv = 0.0, 1.0
    sz = max(0.14, LISC_SZ * abs(bu * nu + bv * nv))
    dl = max(dl, 0.3)
    with p.uklad(pos=tuple(NORMALNE[sc][i] * (odl + 0.02) for i in range(3)), obrot=obr):
        with p.uklad(pos=(u, v, 0.0), obrot=(0, 0, kat)):
            p.kula("Lisc w galarecie " + sc, (0, 0, 0.015), (dl, sz, 0.03), "lisc_w", "matowy", segm=8)
            p.blok("Zylka " + sc, (0.04 * dl, 0, 0.035), (dl * 0.82, 0.04, 0.02), "rdzen_cien", "matowy", faza=0.0)
            p.blok("Ogonek " + sc, (-dl / 2 - 0.09, 0, 0.025), (0.2, 0.05, 0.03), "lisc_w", "matowy", faza=0.0)


def _rzut_grzyb(p, sc):
    """Rzut grzybka na ścianę sc: z boku trzon + kapelusz z kropką, z góry okrągły kapelusz."""
    obr, eu, ev, odl = SCIANY[sc]
    th, kh = GRZYB_H
    with p.uklad(pos=tuple(NORMALNE[sc][i] * (odl + 0.02) for i in range(3)), obrot=obr):
        if sc == "wierzch":
            c = (GRZYB[0], 0.0, GRZYB[2])
            u, v = _skal(c, eu), _skal(c, ev)
            p.walec("Kapelusz w galarecie " + sc, (u, v, 0.015), (GRZYB_SZ[1], 0.03, GRZYB_SZ[1]), "grzyb_w", "matowy",
                    rot=(90, 0, 0), faza=0.0, segm=12)
            p.walec("Kropka w galarecie " + sc, (u + 0.1, v + 0.08, 0.035), (0.16, 0.02, 0.16), "trzon_w",
                    "matowy", rot=(90, 0, 0), faza=0.0, segm=8)
            return
        c = (GRZYB[0], GRZYB[1] - H / 2, GRZYB[2])
        u, v = _skal(c, eu), _skal(c, ev)
        p.blok("Trzon w galarecie " + sc, (u, v + th / 2, 0.015), (GRZYB_SZ[0], th, 0.03), "trzon_w", "matowy",
               faza=0.0)
        # kapelusz: kopułka (ścięty ostrosłup w płaszczyźnie ściany: podstawa na dole)
        p.ostroslup("Kapelusz w galarecie " + sc, (u, v + th + kh / 2 - 0.04, 0.015), (GRZYB_SZ[1], kh, 0.03),
                    "grzyb_w", "matowy", gora=(0.36, 0.03), faza=0.0)
        p.walec("Kropka w galarecie " + sc, (u + 0.13 * (1 if eu[0] + eu[2] > 0 else -1), v + th + 0.11, 0.035),
                (0.13, 0.02, 0.11), "trzon_w", "matowy", rot=(90, 0, 0), faza=0.0, segm=8)


# ------------------------------------------------------------------------------------------------- model
OCZY_KOSCI = ("Oczy", "Powieki", "OczyRad", "OczyZac", "OczyWiel")
USTA_KOSCI = ("Usta", "UstaO", "UstaRad", "UstaFala")
WIDOCZNE = ("Oczy", "Usta")             # te wersje są widoczne w spoczynku (reszta schowana)
SKROT_OCZU = {"otw": "Oczy", "mrug": "Powieki", "rad": "OczyRad", "zac": "OczyZac", "wiel": "OczyWiel"}
SKROT_UST = {"usm": "Usta", "o": "UstaO", "rad": "UstaRad", "fala": "UstaFala"}


def zbuduj():
    p = Postac(ID, "Leśny Slime", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # --- szkielet
    p.kosc("Cialo", "Root", staw=(0, 0, 0), dl=0.6)
    p.kosc("Dol", "Cialo", staw=(0, 0, 0), czesc=(W, H, D), srodek=(0, H / 2, 0), dl=0.8)
    p.kosc("Gora", "Cialo", staw=(0, H, 0), dl=0.5)
    p.kosc("Kielek", "Gora", staw=KIELEK, dl=0.25)
    p.kosc("ListekL", "Kielek", staw=(KIELEK[0] + 0.03, KIELEK[1] + KIELEK_H, KIELEK[2]), dl=0.2)
    p.kosc("ListekP", "Kielek", staw=(KIELEK[0] - 0.03, KIELEK[1] + KIELEK_H, KIELEK[2]), dl=0.2)
    for n in OCZY_KOSCI:
        p.kosc(n, "Cialo", staw=OCZY, dl=0.3)
    for n in USTA_KOSCI:
        p.kosc(n, "Cialo", staw=USTA, dl=0.3)
    p.kosc("Policzki", "Cialo", staw=POLICZKI, dl=0.3)
    for n, (st, _) in BOKI.items():
        p.kosc(n, "Cialo", staw=st, dl=0.3)
    p.kosc("Lisc", "Cialo", staw=LISC, dl=0.3)
    p.kosc("Grzybek", "Cialo", staw=GRZYB, dl=0.3)
    p.kosc("Kula", "Cialo", staw=KULA, dl=0.3)
    p.kosc("Plusk", "Cialo", staw=PLUSK_STAW, dl=0.3)
    for n, (x, z, r) in KROPLE.items():
        p.kosc(n, "Root", staw=(x, 0, z), dl=0.25)
    p.skoruj("Dol", "Gora", 0.0, H)

    _galareta(p)
    _kielek(p)
    _oczy(p)
    _usta(p)
    _ruchome(p)

    # punkty zaczepienia dla gry: podążanie, tabliczka z imieniem, pysk (start bańki), kałuża (efekt rozprysku)
    p.zaczep("RootAttachment", "Cialo", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Gora", (0, 0.05, 0))
    p.zaczep("PyskAttachment", "UstaO", (0, 0, 0.2))
    p.zaczep("PluskAttachment", "Plusk", (0, 0.05, 0))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 15)
    return p


def _galareta(p):
    with p.na("Dol", od="srodek"):
        # jednolita galareta bez płytek „rdzenia” (płytki dostawały własny obrys i robiły z przodu ekran
        # telewizorka w ramce); miękkość dają mocne ścięcia i światło
        p.blok("Galareta", (0, 0, 0), (W, H, D), "skorupka", "poswiata", faza=FAZA)
        # liść i grzybek „widziane przez galaretę” — rzuty z jednego położenia w środku, tylko z tyłu i na prawym
        # boku (−X). Bez wierzchu (z przodu wyglądały jak brud na górnej krawędzi) i bez lewego boku (+X): ten bok
        # widać ukosem w kadrze 3/4 i na ikonie, a obrys płaskiej naklejki robił tam ciemny kwadrat
        for sc in ("bokP", "tyl"):
            _rzut_lisc(p, sc)
        for sc in ("bokP", "tyl"):
            _rzut_grzyb(p, sc)
        zf = D / 2 + 0.03
        # odblask w lewym górnym rogu przodu (od widza): zaokrąglona kreska i kropka
        p.kula("Odblask", (-W / 2 + FAZA + 0.32, H / 2 - FAZA - 0.16, zf), (0.5, 0.13, 0.03), "odblask",
               "swiecacy", rot=(0, 0, 38), segm=8)
        p.walec("Odblask kropka", (-W / 2 + FAZA + 0.7, H / 2 - FAZA - 0.02, zf), (0.12, 0.03, 0.12), "odblask",
                "swiecacy", rot=(90, 0, 0), faza=0.0, segm=8)
        # rumieńce (na ścianie — spłaszczają się z galaretą)
        for zn in (1, -1):
            p.walec("Rumieniec", (zn * XP, YP - H / 2, D / 2 + 0.035), (0.34, 0.03, 0.19), "rumieniec", "zwykly",
                    rot=(90, 0, 0), faza=0.0, segm=12)
        # pęcherzyki powietrza na prawym boku i z tyłu (na lewym boku z ukosa wyglądały jak odpryski)
        for i, (sc, u, v, r) in enumerate((("bokP", -0.2, 0.55, 0.14), ("tyl", -0.75, 0.5, 0.15))):
            obr, eu, ev, odl = SCIANY[sc]
            with p.uklad(pos=tuple(NORMALNE[sc][i2] * (odl + 0.02) for i2 in range(3)), obrot=obr):
                p.walec("Babel %d" % i, (u, v, 0.015), (r, 0.03, r), "odblask", "poswiata", rot=(90, 0, 0),
                        faza=0.0, segm=8)


def _kielek(p):
    """Kiełek na czubku: łodyżka i dwa listki (każdy na własnej kości — machają)."""
    with p.na("Kielek"):
        p.walec("Lodyzka", (0, KIELEK_H / 2 - 0.02, 0), (0.1, KIELEK_H + 0.04, 0.1), "kielek_cien", "zwykly",
                faza=0.0, segm=8)
        p.kula("Paczek", (0, KIELEK_H + 0.03, 0), (0.13, 0.13, 0.13), "kielek", "zwykly", segm=8)
    for n, zn in (("ListekL", 1), ("ListekP", -1)):
        with p.na(n):
            kat = zn * 28
            c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
            d = 0.29
            p.kula("Listek " + n, (zn * d * c, zn * d * s, 0), (0.6, 0.08, 0.38), "kielek", "zwykly",
                   rot=(0, 0, kat), segm=12)
            p.blok("Listek zylka " + n, (zn * d * c * 0.9, zn * d * s * 0.9 + 0.04, 0), (0.42, 0.02, 0.035),
                   "kielek_cien", "zwykly", rot=(0, 0, kat), faza=0.0)


def _oczy(p):
    """Pięć wersji oczu na wspólnym stawie (środek między oczami na przedniej ścianie). Otwarte oczy stoją na
    ścianie, pozostałe wersje są schowane POKAZ głębiej (w galarecie) i wysuwają się w klipach."""
    zs = Z_TW - POKAZ                  # głębokość schowanej wersji
    ow, oh = OKO
    with p.na("Oczy"):                 # duże, okrągłe, błyszczące
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * XO
            p.walec("Oko " + s, (x, 0, Z_TW), (ow, 0.03, oh), "tusz", "polysk", rot=(90, 0, 0), faza=0.0, segm=16)
            p.walec("Oko dol " + s, (x + 0.02, -oh * 0.26, Z_TW + 0.01), (ow * 0.56, 0.02, oh * 0.27), "oko_dol",
                    "polysk", rot=(90, 0, 0), faza=0.0, segm=12)
            p.walec("Blysk " + s, (x - 0.1, oh * 0.18, Z_TW + 0.02), (0.22, 0.02, 0.26), "odblask", "swiecacy",
                    rot=(90, 0, 0), faza=0.0, segm=12)
            p.walec("Blysk maly " + s, (x + 0.13, -oh * 0.17, Z_TW + 0.02), (0.1, 0.02, 0.1), "odblask",
                    "swiecacy", rot=(90, 0, 0), faza=0.0, segm=8)
    with p.na("Powieki"):              # zamknięte (mrugnięcie): łuk wygięty w dół
        for zn, s in ((1, "L"), (-1, "P")):
            _kreska(p, "Zamkniete oko " + s, _luk(zn * XO, 0.03, 0.24, 0.13, 200, 340, n=2), 0.1, zs)
    with p.na("OczyRad"):              # szczęśliwe: łuk wygięty w górę
        for zn, s in ((1, "L"), (-1, "P")):
            _kreska(p, "Wesole oko " + s, _luk(zn * XO, -0.08, 0.23, 0.2, 15, 165, n=2), 0.11, zs)
    with p.na("OczyZac"):              # zaciśnięte „> <”: grot w stronę środka twarzy
        for zn, s in ((1, "L"), (-1, "P")):
            xg = zn * (XO - 0.18)          # grot
            xr = zn * (XO + 0.2)           # ramiona
            _kreska(p, "Zacisniete oko " + s, [(xr, 0.17), (xg, 0.0), (xr, -0.17)], 0.1, zs)
    with p.na("OczyWiel"):             # wielkie, zaskoczone: białko w czarnej obwódce, mała źrenica
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * XO
            p.walec("Obwodka " + s, (x, 0.03, zs), (ow + 0.14, 0.03, oh + 0.14), "tusz", "polysk", rot=(90, 0, 0),
                    faza=0.0, segm=16)
            p.walec("Bialko " + s, (x, 0.03, zs + 0.01), (ow + 0.02, 0.02, oh + 0.02), "bialko", "swiecacy",
                    rot=(90, 0, 0), faza=0.0, segm=16)
            p.walec("Zrenica " + s, (x - zn * 0.03, 0.0, zs + 0.02), (0.22, 0.02, 0.26), "tusz", "polysk",
                    rot=(90, 0, 0), faza=0.0, segm=12)
            p.walec("Zrenica blysk " + s, (x - zn * 0.03 - 0.05, 0.06, zs + 0.03), (0.07, 0.02, 0.07), "odblask",
                    "swiecacy", rot=(90, 0, 0), faza=0.0, segm=8)


def _usta(p):
    """Cztery wersje ust na wspólnym stawie (środek ust). Uśmiech stoi na ścianie, reszta schowana."""
    zs = Z_TW - POKAZ
    with p.na("Usta"):                 # malutki uśmiech: mała otwarta „łódeczka” (cienka kreska z obrysem psuła się)
        p.ostroslup("Usmiech", (0, 0.0, Z_TW), (0.32, 0.13, 0.03), "tusz", "polysk", rot=(0, 0, 180),
                    gora=(0.17, 0.03), faza=0.04)
        p.walec("Usmiech jezyk", (0.0, -0.035, Z_TW + 0.012), (0.12, 0.02, 0.05), "jezyk", "zwykly",
                rot=(90, 0, 0), faza=0.0, segm=8)
    with p.na("UstaO"):                # buzia „o” (zdziwienie, dmuchanie bańki)
        p.walec("Buzia o", (0, 0, zs), (0.24, 0.03, 0.28), "tusz", "polysk", rot=(90, 0, 0), faza=0.0, segm=12)
        p.walec("Buzia o jezyk", (0.0, -0.07, zs + 0.012), (0.13, 0.02, 0.08), "jezyk", "zwykly", rot=(90, 0, 0),
                faza=0.0, segm=8)
    with p.na("UstaRad"):              # otwarty uśmiech z języczkiem
        p.ostroslup("Buzia rad", (0, -0.03, zs), (0.42, 0.26, 0.03), "tusz", "polysk", rot=(0, 0, 180),
                    gora=(0.16, 0.03), faza=0.03)
        p.walec("Buzia rad jezyk", (0.0, -0.1, zs + 0.012), (0.18, 0.02, 0.09), "jezyk", "zwykly", rot=(90, 0, 0),
                faza=0.0, segm=8)
    with p.na("UstaFala"):             # falka (wysiłek, smutno-śmiesznie)
        pkt = [(-0.2 + 0.4 * i / 4, 0.05 * (1 if i % 2 else -1)) for i in range(5)]
        _kreska(p, "Falka", pkt, 0.065, zs)


def _ruchome(p):
    # --- nadęte policzki: soczewki z rumieńcem, schowane tuż pod ścianą
    with p.na("Policzki"):
        for zn in (1, -1):
            p.kula("Policzek", (zn * (XP - 0.04), 0, -0.19), (0.48, 0.4, 0.3), "rdzen", "poswiata", segm=12)
            p.walec("Policzek rumieniec", (zn * (XP - 0.04), -0.01, -0.037), (0.32, 0.02, 0.18), "rumieniec",
                    "zwykly", rot=(90, 0, 0), faza=0.0, segm=12)
    # --- brzuszki (schowane tuż pod ścianą; wysuwają się przy zgnieceniu, przy upadku robią płaty kałuży)
    for n, (st, (nx, _, nz)) in BOKI.items():
        with p.na(n):
            hb = 0.55 if n == "Przod" else H_BRZ
            if nx:
                p.kula("Brzuszek " + n, (0, 0, 0), (T_BRZ, hb, D - 1.0), "skorupka", "poswiata", segm=12)
            else:
                dl = W - 1.5 if n == "Przod" else W - 1.0
                p.kula("Brzuszek " + n, (0, 0, 0), (dl, hb, T_BRZ), "skorupka", "poswiata", segm=12)
    # --- prawdziwy liść (płaski; w środku galarety, widać go po rozlaniu)
    with p.na("Lisc"):
        p.kula("Lisc", (0, 0, 0), (LISC_DL, 0.05, LISC_SZ), "lisc", "matowy", rot=(0, 25, 0), segm=8)
        p.blok("Lisc zylka", (0, 0.03, 0), (LISC_DL * 0.8, 0.02, 0.05), "lisc_w", "matowy", rot=(0, 25, 0),
               faza=0.0)
        p.blok("Lisc ogonek", (-0.55 * math.cos(math.radians(25)), 0.0, 0.55 * math.sin(math.radians(25))),
               (0.22, 0.05, 0.05), "lisc_w", "matowy", rot=(0, 25, 0), faza=0.0)
    # --- prawdziwy grzybek
    th, kh = GRZYB_H
    with p.na("Grzybek"):
        p.walec("Trzon", (0, th / 2, 0), (GRZYB_SZ[0], th, GRZYB_SZ[0]), "trzon", "matowy", faza=0.02, segm=8)
        p.stozek("Kapelusz", (0, th + kh / 2 - 0.04, 0), (GRZYB_SZ[1], kh, GRZYB_SZ[1]), "grzyb", "zwykly", gora=0.45,
                 segm=12)
        p.walec("Kropka 1", (0.19, th + 0.1, 0.19), (0.12, 0.03, 0.12), "trzon", "matowy", rot=(-35, 0, -30),
                faza=0.0, segm=8)
        p.walec("Kropka 2", (-0.04, th + kh - 0.03, 0.0), (0.13, 0.03, 0.13), "trzon", "matowy", faza=0.0, segm=8)
    # --- bańka kwasu
    with p.na("Kula"):
        p.kula("Banka kwasu", (0, 0, 0), R_KULA * 2, "kwas", "swiecacy", segm=12)
        p.walec("Banka blysk", (-0.1, 0.11, R_KULA - 0.03), (0.13, 0.02, 0.15), "odblask", "swiecacy",
                rot=(70, 0, 0), faza=0.0, segm=8)
        p.walec("Banka blysk maly", (0.08, -0.1, R_KULA - 0.02), (0.06, 0.02, 0.06), "odblask", "swiecacy",
                rot=(100, 0, 0), faza=0.0, segm=8)
    # --- kałuża kwasu z koroną kropelek (schowana w podstawie galarety)
    with p.na("Plusk"):
        p.walec("Kaluza", (0, 0.025, 0), (1.3, 0.05, 1.0), "kwas", "swiecacy", faza=0.0, segm=16)
        p.walec("Kaluza 2", (0.42, 0.02, 0.3), (0.62, 0.04, 0.52), "kwas", "swiecacy", faza=0.0, segm=12)
        p.walec("Kaluza 3", (-0.45, 0.02, -0.25), (0.5, 0.04, 0.44), "kwas", "swiecacy", faza=0.0, segm=12)
        for i in range(6):
            a = math.radians(30 + 60 * i)
            r = 0.13 if i % 2 else 0.1
            p.kula("Korona %d" % i, (0.55 * math.sin(a), 0.1 + r * 0.6, 0.45 * math.cos(a)), r * 2, "kwas",
                   "swiecacy", segm=8)
        p.walec("Kaluza blysk", (-0.15, 0.055, 0.12), (0.22, 0.02, 0.12), "odblask", "swiecacy", faza=0.0, segm=8)
    # --- okrągłe kropelki przy podstawie
    for n, (x, z, r) in KROPLE.items():
        with p.na(n):
            _kropelka(p, n, r)


# ------------------------------------------------------------------------------------------------- animacje
ANIM = ("Cialo", "Gora", "Kielek", "ListekL", "ListekP") + OCZY_KOSCI + USTA_KOSCI + (
    "Policzki", "BokL", "BokP", "Przod", "Tyl", "Lisc", "Grzybek", "Kula", "Plusk", "KroplaL", "KroplaP", "KroplaT")
POL_DZ = 0.25           # o ile wysuwają się nadęte policzki
# wysokość (od ziemi), według której schowane bryły jadą z galaretą
Y_REF = {"Policzki": YP, "Lisc": LISC[1], "Grzybek": GRZYB[1] + 0.3, "Kula": KULA[1], "Plusk": 0.12}
for _n in OCZY_KOSCI:
    Y_REF[_n] = YO
for _n in USTA_KOSCI:
    Y_REF[_n] = YU
for _n, (_st, _) in BOKI.items():
    Y_REF[_n] = _st[1]
STAWY_TWARZY = dict([(n, OCZY) for n in OCZY_KOSCI] + [(n, USTA) for n in USTA_KOSCI] + [("Policzki", POLICZKI)])


def _wagi(w, skrot):
    if isinstance(w, str):
        return {skrot[w]: 1.0}
    return {skrot.get(k, k): v for k, v in w.items()}


def poza(g=0.0, b=0.0, oczy="otw", usta="usm", pol=0.0, cp=(0, 0, 0), cr=(0, 0, 0), dod=None, krople=None,
         twarz=None):
    """Poza kluczowa. g = przesunięcie góry galarety (− zgniecenie, + rozciągnięcie); b = wysunięcie brzuszków;
    oczy / usta = wersja ("otw", "mrug", "rad", "zac", "wiel" / "usm", "o", "rad", "fala") albo {wersja: waga};
    pol = nadęcie policzków (0…1); cp/cr = przesunięcie i obrót całego ciała; dod = {kość: {"przes", "obrot"}}
    dokładane do wyliczonego; krople = {kość: przes}; twarz = {"oczy": (cel, rx), "usta": (cel, rx)} — oczy
    (z policzkami) i usta przeniesione sztywno tak, że ich staw staje w punkcie cel (układ ciała) i odchyla się
    o rx (upadek: twarz leży na kałuży)."""
    out = {n: [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)] for n in ANIM}       # [obrot, przes]
    out["Cialo"] = [tuple(cr), tuple(cp)]
    out["Gora"][1] = (0.0, g, 0.0)
    for n, y in Y_REF.items():
        out[n][1] = (0.0, g * y / H, 0.0)
    for n, (st, (nx, _, nz)) in BOKI.items():
        bb = 0.0 if n == "Przod" else b          # pod twarzą brzuszek wyglądał jak listwa — zostaje schowany
        out[n][1] = (nx * bb, g * st[1] / H, nz * bb)
    # twarz: wersje oczu i ust wysuwają się wzdłuż normalnej twarzy (położenie liczy _twarz_koniec)
    wo, wu = _wagi(oczy, SKROT_OCZU), _wagi(usta, SKROT_UST)
    out["_tw"] = {}
    for n, st in STAWY_TWARZY.items():
        if n == "Policzki":
            w = pol
        else:
            w = wo.get(n, 0.0) if n in OCZY_KOSCI else wu.get(n, 0.0)
        grupa = "usta" if n in USTA_KOSCI else "oczy"
        if twarz is not None:
            cel, rx = twarz[grupa]
            R = macierz_obrotu(rx, 0, 0)
            zrodlo = USTA if grupa == "usta" else OCZY
            d = razy_wektor(R, tuple(st[i] - zrodlo[i] for i in range(3)))
            baza = tuple(cel[i] + d[i] - st[i] for i in range(3))
            out[n][0] = (rx, 0.0, 0.0)
            nrm = razy_wektor(R, (0, 0, 1))
            spad = 0.8                 # nieużywane wersje chowają się głębiej w galaretę (zza odchylonej twarzy)
        else:
            baza = out[n][1]
            nrm = (0.0, 0.0, 1.0)
            spad = 0.0
        out["_tw"][n] = list(baza) + list(nrm) + [w, spad]
    _twarz_koniec(out, ostro=False)
    for n, v in (dod or {}).items():
        if "przes" in v:
            out[n][1] = tuple(out[n][1][i] + v["przes"][i] for i in range(3))
        if "obrot" in v:
            out[n][0] = tuple(out[n][0][i] + v["obrot"][i] for i in range(3))
    for n, v in (krople or {}).items():
        out[n][1] = tuple(v)
    return out


def _twarz_koniec(out, ostro=True):
    """Położenie wersji oczu/ust/policzków z wag w out["_tw"]. ostro = waga wyostrzona (zmiana miny trwa ok. 1–2
    klatki w środku odcinka między pozami, a nie cały odcinek — inaczej twarz byłaby przez chwilę pusta)."""
    for n, v in out["_tw"].items():
        baza, nrm, w, spad = v[0:3], v[3:6], v[6], v[7]
        if ostro and n != "Policzki":
            w = max(0.0, min(1.0, 0.5 + (w - 0.5) * 3.0))
        if n == "Policzki":
            s = POL_DZ * w
        else:
            s = -(1.0 - w) * POKAZ if n in WIDOCZNE else w * POKAZ
        out[n][1] = tuple(baza[i] + nrm[i] * (s - spad * (1.0 - w)) for i in range(3))


def _podnies(out):
    """Galareta nie wchodzi pod ziemię: przy przechyle ciało unosi się na krawędzi podstawy."""
    R = macierz_obrotu(*out["Cialo"][0])
    cp = out["Cialo"][1]
    mn = 0.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            for q in ((sx * (W / 2 - FAZA), 0.0, sz * (D / 2 - FAZA)), (sx * W / 2, FAZA, sz * (D / 2 - FAZA)),
                      (sx * (W / 2 - FAZA), FAZA, sz * D / 2)):
                mn = min(mn, razy_wektor(R, q)[1] + cp[1])
    if mn < 0:
        out["Cialo"][1] = (cp[0], cp[1] - mn, cp[2])


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


# sprężyna kiełka: łodyżka (przechył) i listki (machanie)
K_LOD, C_LOD, G_LOD = 480.0, 7.0, 230.0      # 1/s², 1/s, stopnie na (stud/s²) × k
K_LIS, C_LIS, G_LIS = 800.0, 11.0, 520.0
MAX_LOD, MAX_LIS = 38.0, 48.0


def _sprezyna(outs, petla):
    """Kiełek kiwa się z bezwładnością: przyspieszenie czubka (z ruchu ciała) napędza dwie sprężyny z tłumieniem —
    przechył łodyżki (rx, rz) i machanie listków (z pionowego przyspieszenia). W pętli trzy przebiegi."""
    n = len(outs)
    pts = []
    for o in outs:
        R = macierz_obrotu(*o["Cialo"][0])
        cp = o["Cialo"][1]
        v = razy_wektor(R, (KIELEK[0], H + o["Gora"][1][1] + KIELEK_H, KIELEK[2]))
        pts.append((tuple(cp[i] + v[i] for i in range(3)), R))
    N = n - 1 if petla else n

    def pkt(i):
        if petla:
            return pts[i % N][0]
        return pts[max(0, min(n - 1, i))][0]

    acc = []
    for i in range(N):
        a = tuple((pkt(i + 1)[j] - 2 * pkt(i)[j] + pkt(i - 1)[j]) * 900.0 for j in range(3))
        R = pts[i][1]
        acc.append(tuple(sum(R[k][j] * a[k] for k in range(3)) for j in range(3)))   # w układzie ciała
    st = [0.0] * 6                  # rx, v, rz, v, listki, v
    wyn = [None] * n
    dt = 1.0 / 120.0

    def ogr(x, m):
        return max(-m, min(m, x))

    for _ in range(3 if petla else 1):
        for i in range(N):
            ax, ay, az = acc[i]
            for _k in range(4):
                st[1] += dt * (-K_LOD * st[0] - C_LOD * st[1] - G_LOD * az)
                st[0] += dt * st[1]
                st[3] += dt * (-K_LOD * st[2] - C_LOD * st[3] + G_LOD * ax)
                st[2] += dt * st[3]
                st[5] += dt * (-K_LIS * st[4] - C_LIS * st[5] - G_LIS * ay)
                st[4] += dt * st[5]
            wyn[i] = (ogr(st[0], MAX_LOD), ogr(st[2], MAX_LOD), ogr(st[4], MAX_LIS))
    if petla:
        wyn[n - 1] = wyn[0]
    for i, o in enumerate(outs):
        tx, tz, f = wyn[i]
        o["Kielek"][0] = (o["Kielek"][0][0] + tx, o["Kielek"][0][1], o["Kielek"][0][2] + tz)
        o["ListekL"][0] = (o["ListekL"][0][0], o["ListekL"][0][1], o["ListekL"][0][2] + f)
        o["ListekP"][0] = (o["ListekP"][0][0], o["ListekP"][0][1], o["ListekP"][0][2] - f)


def _sekwencja(k, klucze, po=None, stale=None, kielek=True):
    """Klucz w KAŻDEJ klatce. klucze = [(klatka, poza, tryb odcinka do następnej)]: "s" = łagodne wejście i wyjście,
    "l" = jednostajnie (uderzenie), "cr" = płynnie przez pozę (w pętli zawija się). po(f, out) — dopiski w klatce.
    stale = {kość: [klatki]} — w tych klatkach klucz „stale” (skok bez przejścia, np. schowek → miejsce plusku).
    kielek = sprężyste kiwanie kiełka (symulacja)."""
    n = len(klucze)
    petla = k.petla

    def sasiad(i):
        if petla:
            if i < 0:
                return i + n - 1
            if i > n - 1:
                return i - n + 1
            return i
        return max(0, min(n - 1, i))

    f0, f1 = int(klucze[0][0]), int(klucze[-1][0])
    outs = []
    for f in range(f0, f1 + 1):
        i = max(j for j in range(n - 1) if klucze[j][0] <= f) if f < f1 else n - 2
        t = (f - klucze[i][0]) / float(klucze[i + 1][0] - klucze[i][0])
        tryb = klucze[i][2]
        out = {}
        for nb in ANIM:
            war = []
            for ch in (0, 1):
                v = []
                for j in range(3):
                    if tryb == "cr":
                        a, b_, c, d = (klucze[sasiad(i - 1)][1][nb][ch][j], klucze[i][1][nb][ch][j],
                                       klucze[i + 1][1][nb][ch][j], klucze[sasiad(i + 2)][1][nb][ch][j])
                        v.append(_cr(a, b_, c, d, t))
                    else:
                        e = t if tryb == "l" else t * t * (3 - 2 * t)
                        a, c = klucze[i][1][nb][ch][j], klucze[i + 1][1][nb][ch][j]
                        v.append(a + (c - a) * e)
                war.append(tuple(v))
            out[nb] = war
        out["_tw"] = {}
        for nb in STAWY_TWARZY:
            v = []
            for j in range(8):
                if tryb == "cr":
                    a, b_, c, d = (klucze[sasiad(i - 1)][1]["_tw"][nb][j], klucze[i][1]["_tw"][nb][j],
                                   klucze[i + 1][1]["_tw"][nb][j], klucze[sasiad(i + 2)][1]["_tw"][nb][j])
                    v.append(_cr(a, b_, c, d, t))
                else:
                    e = t if tryb == "l" else t * t * (3 - 2 * t)
                    a, c = klucze[i][1]["_tw"][nb][j], klucze[i + 1][1]["_tw"][nb][j]
                    v.append(a + (c - a) * e)
            out["_tw"][nb] = v
        _twarz_koniec(out)
        _podnies(out)
        if po:
            po(f, out)
        outs.append(out)
    if kielek:
        _sprezyna(outs, petla)
    for idx, out in enumerate(outs):
        f = f0 + idx
        for nb in ANIM:
            ob, pr = out[nb]
            wyg = "stale" if stale and f in stale.get(nb, ()) else "liniowo"
            k.klucz(f, nb, obrot=tuple(round(x, 2) for x in ob), przes=tuple(round(x, 4) for x in pr), wyg=wyg)
    return k


def _lokalnie(out, kosc_staw, cel):
    """Przesunięcie kości-dziecka Ciała, które stawia jej staw w punkcie `cel` (świat)."""
    R = macierz_obrotu(*out["Cialo"][0])
    cp = out["Cialo"][1]
    d = tuple(cel[i] - cp[i] for i in range(3))
    RT = tuple(tuple(R[j][i] for j in range(3)) for i in range(3))
    q = razy_wektor(RT, d)
    return tuple(q[i] - kosc_staw[i] for i in range(3))


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def _krople_cykl(k, amp=1.0, czestosc=2):
    for i, (n, (x, z, r)) in enumerate(KROPLE.items()):
        k.cykl(n, "przes", (0, 0.07 * amp, 0), czestosc=czestosc, faza=i / 3.0, srodek=(0, 0.07 * amp, 0))


def _bez_kropel(k):
    k.kanaly = {kk: v for kk, v in k.kanaly.items() if not kk[0].startswith("Kropla")}


def idle(p, dl=60):
    """Spoczynek (2 s): radosne bujanie — dwa przysiady z przechyłem raz w lewo, raz w prawo, między nimi
    wyprostowanie; mrugnięcie; kiełek kiwa się z bujania; kropelki podskakują na zmianę."""
    k = p.klip("idle", dl, petla=True)
    klucze = [
        (0, poza(-0.12, 0.05, cr=(1, 0, 5)), "cr"),
        (15, poza(0.1, -0.02, cp=(0, 0.02, 0), cr=(-1, 0, 0)), "cr"),
        (30, poza(-0.12, 0.05, cr=(1, 0, -5)), "cr"),
        (38, poza(0.04, -0.01, cr=(-0.5, 0, -2)), "s"),
        (40, poza(0.06, -0.015, "mrug", cr=(-0.7, 0, -1.4)), "s"),
        (43, poza(0.09, -0.02, cp=(0, 0.02, 0), cr=(-1, 0, -0.4)), "cr"),
        (dl, poza(-0.12, 0.05, cr=(1, 0, 5)), "cr"),
    ]
    _sekwencja(k, klucze)
    _bez_kropel(k)
    _krople_cykl(k)
    return k


def ruch(p, dl=24):
    """Mały hopek naprzód (0,8 s): przysiad, wybicie z pochyleniem w przód, lot z otwartym uśmiechem, lądowanie
    ze zgnieceniem."""
    k = p.klip("ruch", dl, petla=True)
    klucze = [
        (0, poza(-0.3, 0.12, cr=(-2, 0, 0)), "s"),
        (4, poza(0.24, -0.04, "otw", "rad", cp=(0, 0.25, 0), cr=(6, 0, 0)), "cr"),
        (10, poza(0.1, 0.0, "otw", "rad", cp=(0, 0.62, 0), cr=(3, 0, 0)), "cr"),
        (15, poza(0.16, -0.02, "otw", "rad", cp=(0, 0.3, 0), cr=(-3, 0, 0)), "l"),
        (18, poza(-0.4, 0.16, cr=(-2, 0, 0)), "s"),
        (dl, poza(-0.3, 0.12, cr=(-2, 0, 0)), "s"),
    ]
    _sekwencja(k, klucze)
    _bez_kropel(k)
    _krople_cykl(k, 0.8, 2)              # kropelki zostają na ziemi (lepkie ślady), tylko drgają
    return k


def atak(p, dl=30):
    """Pacnięcie brzuszkiem (1 s): rozpęd z odchyleniem w tył i zaciśniętymi oczami, hop do przodu, pacnięcie
    całym przodem w kl. 13 (ok. 1,85 studa przed nim), odbicie ze zdziwioną minką „o”, chwiejny powrót."""
    k = p.klip("atak", dl, petla=False)
    klucze = [
        (0, poza(), "s"),
        (7, poza(-0.45, 0.18, "zac", "fala", cp=(0, 0, -0.35), cr=(-10, 0, 0)), "l"),
        (10, poza(0.3, -0.05, "zac", "fala", cp=(0, 0.55, 0.95), cr=(14, 0, 0)), "l"),
        (13, poza(-0.38, 0.18, "zac", "fala", cp=(0, 0.05, 1.85), cr=(22, 0, 0)), "s"),
        (17, poza(0.12, 0.0, "otw", "o", cp=(0, 0.25, 1.5), cr=(-6, 0, 0)), "s"),
        (23, poza(-0.08, 0.03, "otw", "o", cp=(0, 0.0, 0.5), cr=(2, 0, -4)), "s"),
        (dl, poza(), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def umiejetnosc(p, dl=66):
    """Kwaśny plusk (2,2 s): nadyma się z policzkami i zaciśniętymi oczami, z buzi „o” wychodzi świecąca bańka
    kwasu (kl. 13–18), pluje (kl. 21: gwałtowne zgniecenie w przód), bańka leci łukiem i w kl. 31 rozpryskuje się
    w kałużę ok. 4,3 studa przed nim; slime odbija się w tył, potem zadowolona minka; kałuża wsiąka w ziemię."""
    k = p.klip("umiejetnosc", dl, petla=False)
    w_srodku = {"Kula": {"przes": (0, 0.0, 0.1)}}
    wychodzi = {"Kula": {"przes": (0, 0.0, 0.32)}}
    w_buzi = {"Kula": {"przes": (0, 0.0, 0.62)}}         # bańka sterczy przed buzią „o”
    klucze = [
        (0, poza(), "s"),
        (8, poza(0.32, 0.18, "zac", "o", pol=1.0, cr=(-5, 0, 0), dod=w_srodku), "s"),
        (13, poza(0.45, 0.24, "otw", "o", pol=1.0, cr=(-8, 0, 0), dod=wychodzi), "s"),
        (18, poza(0.42, 0.22, "otw", "o", pol=0.7, cr=(-9, 0, 0), dod=w_buzi), "l"),
        (21, poza(-0.42, 0.18, "zac", "o", cp=(0, 0, 0.3), cr=(10, 0, 0)), "s"),
        (26, poza(0.14, 0.0, "otw", "o", cp=(0, 0, -0.25), cr=(-4, 0, 0)), "s"),
        (31, poza(-0.08, 0.04, "rad", "rad"), "s"),
        (38, poza(0.04, 0.0, "rad", "rad", cr=(0, 0, 4)), "s"),
        (46, poza(-0.04, 0.02, "rad", "rad", cr=(0, 0, -4)), "s"),
        (54, poza(0.0, 0.0, "otw", "usm"), "s"),
        (dl, poza(), "s"),
    ]
    F_WYLOT, F_PLUSK = 21, 31
    z0 = ZF + 0.55                     # bańka wylatuje tuż przed buzią (ciało jest wtedy wysunięte o 0,3)
    stale = {"Plusk": [F_PLUSK - 1, dl - 1], "Kula": [F_PLUSK]}

    def po(f, out):
        if F_WYLOT <= f < F_PLUSK:
            t = (f - F_WYLOT) / float(F_PLUSK - F_WYLOT)
            y = YU * (1 - t) + R_KULA * t + 4 * t * (1 - t) * 1.3       # łuk: ok. 1,3 studa nad prostą
            z = z0 + (PLUSK_Z - z0) * t
            out["Kula"][1] = _lokalnie(out, KULA, (0.0, y, z))
        elif f == F_PLUSK:
            out["Kula"][1] = _lokalnie(out, KULA, (0.0, -0.4, PLUSK_Z))     # wpada w kałużę (pod ziemię)
        if F_PLUSK <= f < dl:
            zejscie = 0.0 if f < 46 else -0.36 * min(1.0, (f - 46) / 10.0)
            out["Plusk"][1] = _lokalnie(out, PLUSK_STAW, (0.0, zejscie, PLUSK_Z))
    _sekwencja(k, klucze, po=po, stale=stale)
    return k


def trafienie(p, dl=18):
    """Reakcja na cios (0,6 s): wielkie zaskoczone oczy i buzia „o”, odskok w tył z podskokiem, odbicie."""
    k = p.klip("trafienie", dl, petla=False)
    klucze = [
        (0, poza(), "l"),
        (3, poza(-0.25, 0.1, "wiel", "o", cp=(0, 0.35, -0.55), cr=(-14, 0, 0)), "s"),
        (8, poza(0.16, -0.03, "wiel", "o", cp=(0, 0.08, -0.45), cr=(5, 0, 0)), "s"),
        (13, poza(-0.08, 0.03, "otw", "o", cp=(0, 0, -0.15), cr=(-1, 0, 0)), "s"),
        (dl, poza(), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def unik(p, dl=27):
    """Unik (0,9 s): przysiad, hopek w lewo (+X) z piruetem (pełny obrót), szczęśliwe oczy w locie, lądowanie,
    powrót ślizgiem na miejsce."""
    k = p.klip("unik", dl, petla=False)
    klucze = [
        (0, poza(), "s"),
        (4, poza(-0.32, 0.13, cr=(0, 0, 5)), "l"),
        (7, poza(0.25, -0.04, "rad", "o", cp=(0.7, 0.5, 0), cr=(0, 110, -6)), "l"),
        (10, poza(0.1, 0.0, "rad", "o", cp=(1.4, 0.7, 0), cr=(0, 250, -4)), "l"),
        (13, poza(-0.35, 0.14, "otw", "usm", cp=(1.7, 0, 0), cr=(0, 360, 4)), "s"),
        (21, poza(0.05, 0.0, cp=(0.25, 0, 0), cr=(0, 360, -3)), "s"),
        (dl, poza(cr=(0, 360, 0)), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): zaskoczenie, chwianie z zaciśniętymi oczami, rozpływa się w płaską kałużę z płatami
    (brzuszki); w połowie twarz jest jeszcze na przodzie, potem oczka kładą się na wierzchu kałuży, otwierają się
    i mrugają, buzia „o”; grzybek wypływa i przewraca się na bok, liść zostaje w środku, kiełek więdnie.
    Kończy się leżeniem."""
    k = p.klip("upadek", dl, petla=False)
    G_KON = -(H - 0.5)                 # galareta: 0,5 studa wysokości
    yk = H + G_KON                     # wierzch kałuży
    tyl = (0, 0, -0.4)
    # oczka „pływają” na wierzchu kałuży (dolny brzeg lekko zanurzony), odchylone o 40°; buzia przed nimi
    TW = {"oczy": ((0.0, yk + 0.2, ZF - 0.5), -40), "usta": ((0.0, yk + 0.04, ZF - 0.1), -40)}
    # w połowie rozlewania twarz zostaje na przodzie (inaczej oczy na chwilę znikałyby w galarecie)
    TW_POL = {"oczy": ((0.0, 0.58, ZF), -15), "usta": ((0.0, 0.3, ZF), -15)}

    yg = Y_REF["Grzybek"]
    # grzybek wypływa i przewraca się na bok na wierzchu kałuży, z tyłu po lewej stronie slime'a (+X)
    grzyb_kon = {"przes": (1.55, yk + 0.18 - GRZYB[1] - G_KON * yg / H, -0.2), "obrot": (0, 30, 80)}
    # kiełek więdnie w tył i w prawo (−X), żeby nie leżał między oczkami
    wiedniecie = {"Kielek": {"obrot": (-30, 0, -45)}, "ListekL": {"obrot": (0, 0, -30)},
                  "ListekP": {"obrot": (0, 0, 40)}}
    # bańka kwasu schowana w podstawie wystawała spod przodu płaskiej kałuży — chowa się głębiej
    banka = {"przes": (0.0, -0.03, -0.55)}

    def pol(v):
        return {kan: tuple(x * 0.5 for x in w) for kan, w in v.items()}

    def plat(n, dx, dz, obr):
        """Brzuszek położony płasko jako płat kałuży: środek na y = 0,25 (soczewka 0,5 grubości leży na ziemi)."""
        sy = BOKI[n][0][1]
        return {"przes": (dx, T_BRZ / 2 - sy * (1 + G_KON / H), dz), "obrot": obr}

    platy = {"BokL": plat("BokL", 0.0, 0.35, (0, 35, 90)),       # rz = 90: cienka oś soczewki pionowo
             "BokP": plat("BokP", 0.0, -0.3, (0, -25, 90)),
             "Przod": plat("Przod", 0.95, 0.75, (90, -35, 0)),   # rx = 90: cienka oś pionowo; z boku twarzy
             "Tyl": plat("Tyl", -0.3, 0.0, (90, 20, 0))}

    def lezy():
        """Kałuża: brzuszki rozjechane na boki jako płaskie płaty, grzybek wypływa i staje krzywo z tyłu, liść
        zostaje płasko w środku (schowany), kiełek więdnie."""
        d = {"Grzybek": grzyb_kon, "Kula": banka}
        d.update(platy)
        d.update(wiedniecie)
        return d

    def pol_lezy():
        d = {"Grzybek": pol(grzyb_kon), "Kula": pol(banka)}
        d.update({n: pol(v) for n, v in platy.items() if n != "Przod"})    # przedni płat nie zasłania buzi
        d.update({n: pol(v) for n, v in wiedniecie.items()})
        return d

    kropl_kon = {"KroplaL": (0.5, 0, 0.3), "KroplaP": (-0.45, 0, 0.35), "KroplaT": (0.3, 0, -0.45)}
    klucze = [
        (0, poza(), "l"),
        (4, poza(-0.25, 0.1, "wiel", "o", cp=(0, 0.15, -0.4), cr=(-12, 0, 0)), "s"),
        (10, poza(0.2, -0.04, "zac", "fala", cp=tyl, cr=(0, 0, 7)), "s"),
        (16, poza(-0.15, 0.06, "zac", "fala", cp=tyl, cr=(0, 0, -6)), "s"),
        (22, poza(0.08, 0.0, "mrug", "fala", cp=tyl, cr=(0, 0, 3)), "s"),
        (31, poza(-1.0, 0.28, "mrug", "fala", cp=tyl, dod=pol_lezy()), "s"),
        (36, poza(-1.45, 0.4, "mrug", "fala", cp=tyl, twarz=TW_POL, dod=pol_lezy()), "s"),
        (40, poza(G_KON, 0.5, "mrug", "fala", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
        # na kałuży buzia „o” („ojej”) — falka leżąca między oczkami czytała się jak czarny szew
        (46, poza(G_KON, 0.5, "otw", "o", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
        (51, poza(G_KON, 0.51, "otw", "o", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
        (53, poza(G_KON, 0.51, "mrug", "o", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
        (55, poza(G_KON, 0.52, "otw", "o", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
        (dl, poza(G_KON, 0.52, "otw", "o", cp=tyl, twarz=TW, dod=lezy(), krople=kropl_kon), "s"),
    ]
    _sekwencja(k, klucze)
    return k


def wiwat(p, dl=40):
    """Wiwat po wygranej (pętla 1,33 s): dwa podskoki ze szczęśliwymi oczami i otwartym uśmiechem, kołysanie."""
    k = p.klip("wiwat", dl, petla=True)
    R_ = ("rad", "rad")
    klucze = [
        (0, poza(-0.38, 0.15, *R_, cr=(-3, 0, 0)), "s"),
        (5, poza(0.32, -0.05, *R_, cp=(0, 0.5, 0), cr=(-5, 12, 5)), "cr"),
        (10, poza(0.12, 0.0, *R_, cp=(0, 0.95, 0), cr=(-7, 15, 7)), "cr"),
        (15, poza(0.24, -0.03, *R_, cp=(0, 0.35, 0), cr=(-3, 8, 3)), "l"),
        (20, poza(-0.38, 0.15, *R_, cr=(-3, 0, 0)), "s"),
        (25, poza(0.32, -0.05, *R_, cp=(0, 0.5, 0), cr=(-5, -12, -5)), "cr"),
        (30, poza(0.12, 0.0, *R_, cp=(0, 0.95, 0), cr=(-7, -15, -7)), "cr"),
        (35, poza(0.24, -0.03, *R_, cp=(0, 0.35, 0), cr=(-3, -8, -3)), "l"),
        (dl, poza(-0.38, 0.15, *R_, cr=(-3, 0, 0)), "s"),
    ]
    _sekwencja(k, klucze)
    _bez_kropel(k)
    _krople_cykl(k, 0.8, 2)
    return k
