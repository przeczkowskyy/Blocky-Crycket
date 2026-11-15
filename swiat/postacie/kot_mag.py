# -*- coding: utf-8 -*-
"""KOT-MAG „Crycket” — drugi bohater-maskotka: mały kanciasty pomarańczowy kot w za dużej fioletowej szacie,
z kosturem zakończonym fioletowym kryształem i spiczastym kapeluszem (kapelusz i kryształ to w kanonie wciąż
propozycja — dlatego kapelusz jest OSOBNYM przedmiotem i można go zdjąć).

CIAŁO BAZOWE + STRÓJ Z PRZEDMIOTÓW (D-071, kontrakt swiat/postacie/EKWIPUNEK.md):
  cialo()      goły kot („kot_mag_cialo”): te same klocki, kości, zaczepy i klipy; pomarańczowe futro z ciemnymi
               pręgami (dwie na plecach i bokach, po jednej na ramieniu i przedramieniu), jasny brzuszek z kępką
               futra pod brodą, cała dzisiejsza głowa z mordką i wąsami, uszy, łapki, ogon (u nasady ogona futro
               schodzi z bioder do stawu ogona, bo ogon wychodzi nisko, spod dawnej szaty);
  przedmioty() kapelusz (Helmet, na KapeluszAttachment), szata z kołnierzem, rękawami i dzwonem (Chest, powłoka
               na tułowiu, ramionach, przedramionach i biodrach), szarfa z klamrą (Belt), kostur (Weapon, na
               KosturAttachment) — segmenty kostne w układzie środka klocka kości albo akcesorium na zaczepie;
  ubierz()     zakłada przedmioty na ciało (powłoka zastępuje gołe futro kości); nakrycie głowy i broń w prawej łapie
               idą przez KOREKTY_CHWYTU na kości nośne HatPivot / StaffPivot (w upadku spadają);
  zbuduj()     jak dotąd: [Kot-Mag w pełnym stroju kanonicznym (KANON), kapelusz, kostur];
  warianty()   stroje z STROJE, segmenty i ikony całych przedmiotów dla przebuduj.py (wynik/kot_mag/ekwipunek/).
Wspólny kod ekwipunku (Przedmiot, ubierz, kopiuj_klipy, zaczep_ekwipunku) jest w swiat/postacie/ekwipunek.py
(do 15.11 w sekcji „ekwipunek: wspólne” w rycerz.py).
Klipy liczą się RAZ na postaci odniesienia (ODNIESIENIE_KLIPOW = pełny strój = dawny model: stopy na ziemi, tor
upadku kapelusza i kostura) i są kopiowane bez zmian na ciało i każdy strój — ten sam ruch niezależnie od ubrania.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/kot_mag.py --wyj <folder> --klip idle
    python -B swiat/postacie/kot_mag.py --kontrola             # kontrola przenikania we wszystkich strojach (bez Blendera)
    python -B swiat/postacie/kot_mag.py --kontrola --stroj golas upadek    # jeden strój, wybrane klipy
    python -B swiat/postacie/kot_mag.py --kontrola --blender   # to samo na próbkach krzywych z Blendera

Status: propozycja (kanon wyglądu: B&C/Postacie/Kot-Mag.md, obraz referencyjny assets/processed/KeyArt.png).

Budowa:
- szkielet R15 z przerysowanymi proporcjami (duża głowa, krótkie łapy): ok. 3,15 studa do czubka głowy,
  ok. 3,45 z uszami, bez kapelusza;
- kości spoza standardu R15: `Tail` (dziecko LowerTorso) i `TailTip` (dziecko Tail) — ogon; `LeftEar` i `RightEar`
  (dzieci Head) — uszy strzygą i kładą się po sobie; `HatPivot` (dziecko Head, w HatAttachment) i `StaffPivot`
  (dziecko RightHand, w RightGripAttachment) — bez własnych brył, niosą kapelusz i kostur (i każde inne nakrycie
  głowy i broń kota), żeby w upadku kapelusz mógł zsunąć się z głowy, a kostur wypaść z łapy. W spoczynku wszystko
  leży dokładnie tam, gdzie wcześniej (wygląd bez zmian). W Roblox to już nie „czysty” R15 — do NPC i postaci
  w grze wystarczy; klipy kości standardowych działają tak samo;
- dół szaty to jeden ośmiokątny dzwon na LowerTorso do samej ziemi (za duża szata) z trenem leżącym z tyłu;
  nogi chodzą w środku (wymach uda ≤ 15°), spod rąbka wystają łapy;
- akcesoria: `kot_mag_kapelusz` (Hat; na kocie na `KapeluszAttachment` kości HatPivot = ta sama ramka co
  HatAttachment) i `kot_mag_kostur` (Bron, konwencja broni: uchwyt w (0,0,0), drzewce w +Y; na kocie na
  `KosturAttachment` kości StaffPivot = ta sama ramka co RightGripAttachment). Kostur jest założony z korektą
  obrot=(−90, 0, 0): oś drzewca = oś +Y kości dłoni (przy zwisającej łapie stoi pionowo, jak na obrazie
  referencyjnym), przód kryształu = +Z dłoni;
- klipy bez kanału skali (Roblox przenosi tylko pozycję i obrót kości): „pulsowanie” kryształu w klipie czar to
  potrząśnięcie kosturem; prawdziwe świecenie / błyski w grze dorobić skryptem (PointLight, ParticleEmitter);
- to rig NPC / postaci w grze, NIE ciało awatara na Marketplace (kości spoza R15, 3,7 studa wzrostu).

Klipy (30 kl./s; kot patrzy w +Z i w tę stronę rzuca czary):
  idle (pętla 2 s), chod (pętla), czar (kostur w górę z boku głowy, pulsowanie), wiwat (pętla podskoków) — szkice
  pisane kluczami co kilka klatek (czar i wiwat 15.11 przepisane pozami kluczowymi: kostur nie wchodzi już w głowę);
  klipy walki (pozy kluczowe zamieniane na klucz w KAŻDEJ klatce, jak w zwiadowca.py):
    atak           szybki błysk z kostura: krótki zamach i wyrzut kryształu do przodu, wypuszczenie kl. 9;
    kula_ognia     zamach kosturem w górę i w tył z prawej strony głowy (kryształ ponad rondem kapelusza, za głową)
                   i rzut do przodu, wolna łapa wyciągnięta do celu, wypuszczenie kl. 27;
    lodowy_pocisk  cofnięcie i pchnięcie kostura poziomo do przodu z wypadem, obie łapy pchają do celu,
                   wypuszczenie kl. 21;
    bariera        przyczajenie (kl. 4), potem kostur wzniesiony pionowo w górę z prawej (kryształ obok szpica
                   kapelusza), lewa łapa wypchnięta dłonią do przodu, szeroki przysiad; krąg kl. 10, poza trzymana
                   do kl. 30;
    unik           koci odskok w tył i w lewo (ogon w górę, uszy po sobie), lądowanie i powrót na miejsce startu;
    trafienie      szarpnięcie w tył kl. 4 (uszy po sobie, ogon nastroszony) i powrót;
    upadek         szarpnięcie, chwiejny krok, kolana miękną, pada na lewy bok; kostur wypada z łapy (kl. 22) i ląduje
                   przed nim, kapelusz zsuwa się z głowy (kl. 30) i staje obok; kończy się leżeniem (ostatnia klatka
                   do zatrzymania).
  Klatki trafienia / wypuszczenia są też w słowniku CHWILE. Każdy klip walki zaczyna się i kończy w pozie z klatki 0
  klipu idle (płynne przejście do spoczynku). Bez kostura prawa łapa robi ten sam ruch pustą łapką, bez kapelusza
  widać całe uszy.
"""
import math
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie.biblioteka.postac import (R15_KOSCI, Akcesorium, Postac, katy_z_macierzy, macierz_obrotu, mnoz,
                                              razy_wektor)
# wspólny kod ekwipunku (EKWIPUNEK.md pkt 4)
from swiat.postacie.ekwipunek import Przedmiot, kopiuj_klipy, ubierz, zaczep_ekwipunku

ID = "kot_mag"
NAZWA = "Kot-Mag Crycket"

# klatki trafienia / wypuszczenia pocisku / chwili efektu w klipach walki (dla odtwarzacza walki; 30 kl./s)
CHWILE = {"atak": 9, "kula_ognia": 27, "lodowy_pocisk": 21, "bariera": 10, "trafienie": 4}

SLABOSCI = [
    "Rig NPC, nie ciało awatara: kości Tail, TailTip, LeftEar, RightEar, HatPivot i StaffPivot spoza R15, wzrost "
    "ok. 3,7 studa z kapeluszem.",
    "D-071: zbuduj() (kot_mag.fbx, plansza, filmy) to pełny strój kanoniczny — wygląd bez zmian. Szata i szarfa są "
    "wtapiane w bryły kości (te same siatki <Kosc>_Geo), więc w kot_mag.fbx strój nadal jest częścią ciała. "
    "Ubieranie w grze ma iść przez gołe ciało (ekwipunek/kot_mag_cialo.fbx z zaczepami Ekw<Kosc>Attachment) "
    "i segmenty z ekwipunek/przedmioty/ — ta droga nie była sprawdzana w Studio (przezroczystość gołego futra pod "
    "szatą, AddAccessory z własnymi nazwami zaczepów, przedmioty na częściach HatPivot / StaffPivot).",
    "Kapelusz i kostur są osobnymi przedmiotami (przedmioty/kot_mag_*.fbx); w FBX kota ich nie ma. W renderach i "
    "klipach siedzą na kościach HatPivot i StaffPivot (te same ramki co HatAttachment i RightGripAttachment; "
    "korekty chwytu kota w KOREKTY_CHWYTU dostaje każde nakrycie głowy i każda broń w prawej łapie). W grze, gdy "
    "kostur jest Toolem na RightGripAttachment, a kapelusz akcesorium na HatAttachment, upadek ich nie zrzuci — "
    "trzeba je wtedy przypiąć do części HatPivot / StaffPivot albo zrzucić skryptem.",
    "Goły kot (ciało bazowe): futro, pręgi, jasny brzuszek z kępką pod brodą i kolory to propozycja do oceny "
    "(plansza ekwipunek/kot_mag_ekwipunek_plansza.jpg). Ogon wychodzi nisko (staw na wysokości łydek, pod dawną "
    "szatą), więc goły kot ma u nasady ogona pas futra schodzący z tyłu bioder do stawu ogona (bryła bioder, znika "
    "pod szatą). Nogi pod szatą były cienkie (udo 0,42, łydka 0,40 przy klockach 0,5 i 0,45) — bez szaty widać "
    "krótkie, cienkie nóżki na dużych łapach; zostały bez zmian, bo w pełnym stroju są te same.",
    "Upadek bez szaty: klip liczony na postaci odniesienia kładzie kota na lewym boku dzwonu szaty i na lewym "
    "rękawie (pełny strój i każdy strój z szatą: najniższy punkt w ostatniej klatce 0,000, tułów 0,28 nad ziemią). "
    "Goły kot i strój „kapelusz_i_kostur” leżą ok. 0,20 studa nad ziemią (najniżej lewa łapka 0,198, tułów 0,73), "
    "bo dzwon szaty jest szerszy niż goły tułów; kapelusz i kostur leżą na ziemi. Klipy są wspólne (kontrakt), więc "
    "poprawka wymaga decyzji: osobny upadek dla ciała albo przesunięcie korzenia w grze zależne od stroju.",
    "Szarfa (kot_mag_pas) w pełnym stroju jest prawie cała schowana w górnej części dzwonu szaty (tak jak dotąd); "
    "widać ją dopiero na samym futrze albo przy innej szacie.",
    "Łapy są bardzo krótkie (bark → nadgarstek 0,64 studa, bark poniżej spodu głowy): łapa nie sięga nad głowę ani do "
    "drugiej łapy. „Zamach nad głową” w kuli ognia to kostur uniesiony w górę i w tył z prawej strony głowy, "
    "kryształ ponad rondem kapelusza (ok. 3,8 studa; rondo 3,2), za głową; w lodowym pocisku drzewce trzyma tylko "
    "prawa łapa — lewa pcha powietrze obok (nie sięga).",
    "Rękawy są długie (mankiet zakrywa łapkę), więc drzewce zawsze wychodzi z mankietu, a przy kosturze trzymanym "
    "poprzecznie przechodzi przez brzeg rękawa — to chwyt w rękawie, nie przenikanie przez głowę czy tułów.",
    "Dzwon szaty jest sztywny (idzie za biodrami): w chodzie nogi są schowane, ruch widać po łapach i kołysaniu; "
    "w upadku na bok dzwon leży jak sztywny stożek.",
    "Tren leży na ziemi tylko w spoczynku; przy podskokach (wiwat, unik) unosi się razem z biodrami.",
    "Czary nie mają efektów cząsteczkowych (kula ognia, lodowy pocisk, krąg bariery, błysk ataku — do zrobienia "
    "w grze w klatkach z CHWILE); kryształ świeci tylko w renderze.",
    "Twarz nie ma mimiki — ten sam uśmiech przy trafieniu i upadku; emocje grają uszy (po sobie) i ogon. Uszy żyją "
    "w klipach walki, w czarze i wiwacie; idle i chod są sprzed kości uszu i zostały bez zmian (uszy stoją).",
    "Bariera: kostur wzniesiony pionowo z prawej strony głowy (łapa nie sięga nad głowę ani do ziemi, więc nie ma "
    "ani kostura nad środkiem głowy, ani stuknięcia okuciem w ziemię); poza bliska klipowi czar. Krąg bariery to "
    "efekt w grze (kl. 10).",
    "Atak, kula ognia i lodowy pocisk w chwili wypuszczenia mają podobną sylwetkę (kostur do przodu); różnią się "
    "zamachem (krótki w tył / wysoko za głowę / poziomo przy boku jak lanca) i dobiciem (kula kończy nisko). "
    "Z kamery zza pleców kostur skierowany do przodu chowa się za głową i kapeluszem — czytelność da efekt czaru.",
    "Klip chod (sprzed 15.11, nieruszany): palce łap schodzą w nim do 0,22 studa pod ziemię (kl. 8), a lewy rękaw "
    "zachodzi na dzwon szaty na 0,23 studa (w spoczynku 0,17) — do poprawy, jeśli chod ma zostać.",
    "Unik i lodowy pocisk przesuwają kota w samym klipie (kość LowerTorso): odskok ok. 1,6 studa w tył i w bok, "
    "wypad ok. 0,35 studa do przodu; oba klipy kończą się w punkcie startu.",
    "Kontrola przenikania (python -B swiat/postacie/kot_mag.py --kontrola) liczy bryły jako skrzynki, stożki i "
    "ostrosłupy (dzwon szaty, uszy, kapelusz zwężają się jak w modelu); wąsy (cienkie kreski) i ramię z rękawem przy "
    "barku nie są liczone. Rękaw ramienia (UpperArm) i kostur względem własnej łapy — tylko na arkuszach. Działa na "
    "każdym stroju z STROJE.",
    "kot_mag_cialo.fbx/.glb ma tylko klip idle (reszta klipów: kot_mag__<klip>.fbx, te same kości i nazwy).",
]

PALETA = {
    "kot": "F28A2E", "kot_jasny": "FFD9A6", "kot_ciemny": "C8601C",
    "szata": "7B45CC", "szata_ciemna": "4F2A93", "szata_jasna": "9F72E6",
    "wstazka": "F7C531", "nos": "F5879F", "krysztal": "9B4DFF", "krysztal_jasny": "C49BFF",
    "drewno": "7A4A26", "drewno_ciemne": "4E2D15",
}


# --------------------------------------------------------------------------- akcesoria
def kapelusz():
    """Spiczasty fioletowy kapelusz z żółtą wstążką; (0,0,0) = HatAttachment (środek góry głowy)."""
    a = Akcesorium("kot_mag_kapelusz", "Kapelusz Kota-Maga", zaczep="HatAttachment", typ="Hat",
                   paleta=PALETA, ikona_obrot=(0, 20, 0))
    a.walec("Rondo", (0, 0.06, 0), (2.25, 0.12, 2.05), "szata", "matowy", segm=8)
    a.walec("Rondo spod", (0, 0.0, 0), (2.05, 0.03, 1.85), "szata_ciemna", "matowy", segm=8, faza=0.0)
    a.ostroslup("Glowa kapelusza", (0, 0.58, 0), (1.25, 0.95, 1.15), "szata", "matowy", gora=(0.78, 0.72))
    a.blok("Wstazka", (0, 0.26, 0), (1.31, 0.24, 1.21), "wstazka", "matowy", faza=0.03)
    a.blok("Klamra", (0, 0.26, 0.6), (0.34, 0.3, 0.08), "zloto", "metal", faza=0.03)
    a.blok("Klamra srodek", (0, 0.26, 0.64), (0.14, 0.12, 0.04), "szata_ciemna", faza=0.0)
    # górna część przełamana do tyłu — krzywy, komiksowy szpic
    with a.uklad(pos=(0, 1.04, -0.02), obrot=(-22, 0, 6)):
        a.ostroslup("Szpic", (0, 0.42, 0), (0.8, 0.84, 0.75), "szata", "matowy", gora=(0.0, 0.0),
                    przes_gory=(0.0, -0.12))
    a.blok("Gwiazdka", (0.38, 0.62, 0.44), (0.16, 0.16, 0.06), "wstazka", "swiecacy", rot=(10, 0, 45), faza=0.0)
    return a


def kostur():
    """Drewniany kostur z fioletowym kryształem; uchwyt w (0,0,0), drzewce w +Y (konwencja broni)."""
    a = Akcesorium("kot_mag_kostur", "Kostur Kota-Maga", zaczep="RightGripAttachment", typ="Bron",
                   paleta=PALETA, ikona_obrot=(0, 0, -35))
    a.walec("Drzewce", (0, 0.42, 0), (0.17, 2.55, 0.17), "drewno", "matowy", segm=8)
    a.blok("Okucie", (0, -0.83, 0), (0.22, 0.12, 0.22), "zloto", "metal", faza=0.03)
    a.blok("Owijka", (0, 0.0, 0), (0.23, 0.42, 0.23), "szata_ciemna", "matowy", faza=0.04)
    for i, y in enumerate((0.5, 0.85, 1.2)):
        a.blok("Spirala %d" % i, (0, y, 0), (0.24, 0.06, 0.24), "szata_jasna", "matowy", rot=(0, 30 * i, 18),
               faza=0.0)
    a.blok("Pierscien", (0, 1.62, 0), (0.3, 0.1, 0.3), "zloto", "metal", faza=0.03)
    a.blok("Oprawa", (0, 1.73, 0), (0.36, 0.12, 0.36), "zloto", "metal", rot=(0, 45, 0), faza=0.03)
    for i in range(4):
        with a.uklad(pos=(0, 1.78, 0), obrot=(0, 45 + 90 * i, 0)):
            a.blok("Pazur %d" % i, (0, 0.17, 0.17), (0.07, 0.34, 0.07), "zloto", "metal", rot=(28, 0, 0), faza=0.0)
    # kryształ: dwa ostrosłupy (dolny odwrócony), obrócone o 45° — romb
    with a.uklad(pos=(0, 2.02, 0), obrot=(0, 45, 0)):
        a.ostroslup("Krysztal gora", (0, 0.27, 0), (0.42, 0.54, 0.42), "krysztal", "polysk", gora=(0, 0))
        a.ostroslup("Krysztal dol", (0, -0.12, 0), (0.42, 0.24, 0.42), "krysztal", "polysk", rot=(180, 0, 0),
                    gora=(0, 0))
        a.blok("Blysk", (0.0, 0.14, 0.215), (0.1, 0.2, 0.03), "krysztal_jasny", "swiecacy", faza=0.0)   # kryształ: fiolet z połyskiem, świeci tylko blask
    for zn in (1, -1):
        a.blok("Odlamek", (zn * 0.36, 2.2 + zn * 0.06, 0), (0.1, 0.16, 0.1), "krysztal", "swiecacy",
               rot=(0, 45, zn * 20), faza=0.0)
    return a


# --------------------------------------------------------------------------- ciało bazowe („goły” kot)
CIALO_TYP = "kot"
KLASY = ("mag",)
WYMIARY = {"Head": (1.65, 1.3, 1.4),
           "UpperTorso": (1.3, 0.85, 0.95), "LowerTorso": (1.3, 0.25, 0.95),
           "UpperArm": (0.42, 0.42, 0.42), "LowerArm": (0.42, 0.36, 0.42), "Hand": (0.4, 0.22, 0.4),
           "UpperLeg": (0.5, 0.3, 0.5), "LowerLeg": (0.45, 0.27, 0.45), "Foot": (0.5, 0.18, 0.62)}
# korekty chwytu kota (dane bohatera, nie przedmiotu): nakrycie głowy na kości nośnej HatPivot, broń w prawej łapie
# na StaffPivot — {zaczep przedmiotu: (zaczep kota, pos, obrot)}; dzięki temu w upadku przedmiot spada
KOREKTY_CHWYTU = {"HatAttachment": ("KapeluszAttachment", (0, 0.02, 0), (0, 0, 0)),
                  "RightGripAttachment": ("KosturAttachment", (-0.08, 0, 0), (-90, 0, 0))}
# przedmioty pełnego stroju kanonicznego (zbuduj()) — dawny model
KANON = ("kot_mag_kapelusz", "kot_mag_szata", "kot_mag_pas", "kot_mag_kostur")
ODNIESIENIE_KLIPOW = KANON                     # geometria, na której liczą się klipy (= dawny model)
# stroje do plansz i kontroli (przebuduj.py -> wynik/kot_mag/ekwipunek/)
STROJE = {"golas": (),
          "pelny": KANON,
          "bez_kapelusza": ("kot_mag_szata", "kot_mag_pas", "kot_mag_kostur"),
          "kapelusz_i_kostur": ("kot_mag_kapelusz", "kot_mag_kostur"),
          "sama_szata": ("kot_mag_szata", "kot_mag_pas")}     # nie „szata”: id kot_mag_szata ma przedmiot
NAZWY_STROJOW = {"golas": "goły (ciało bazowe)", "pelny": "pełny strój", "bez_kapelusza": "bez kapelusza",
                 "kapelusz_i_kostur": "sam kapelusz i kostur", "sama_szata": "sama szata z szarfą"}
PLANSZA_ZBIORCZA = ("golas", "pelny", "kapelusz_i_kostur", "sama_szata")      # goły | pełny | dwa częściowe
# filmy w stroju (strój, klip): dowód, że przedmioty idą za kośćmi, a goły kot rusza się dobrze bez szaty
FILMY_EKWIPUNKU = (("golas", "idle"), ("golas", "chod"), ("golas", "kula_ognia"), ("golas", "upadek"),
                   ("kapelusz_i_kostur", "upadek"), ("sama_szata", "bariera"), ("bez_kapelusza", "atak"))


def _postac(id, nazwa):
    """Postać R15 o klockach kota z kośćmi uszu, ogona i kośćmi nośnymi kapelusza i kostura (20 zaczepów), bez
    brył. Kolejność kości i zaczepów jak w dawnym zbuduj()."""
    p = Postac(id, nazwa, typ="r15", skala=1.0, faza=0.05, paleta=PALETA, rozstaw_nog=0.3, wymiary=WYMIARY)
    w, h, d = p.wymiary("Head")
    srodek_glowy = tuple(p.staw("Head")[i] + p.srodek("Head")[i] for i in range(3))
    # uszy na własnych kościach LeftEar / RightEar ze stawem u nasady ucha
    for zn, kosc in ((1, "LeftEar"), (-1, "RightEar")):
        nasada = (srodek_glowy[0] + zn * 0.6, srodek_glowy[1] + h / 2 + 0.09, srodek_glowy[2] - 0.05)
        p.kosc(kosc, "Head", staw=nasada, czesc=(0.56, 0.72, 0.32), srodek=(zn * 0.17, 0.32, 0.0))
    # ogon: nasada idzie spod szaty do tyłu i w lewo (+X), końcówka wznosi się obok szaty
    p.kosc("Tail", "LowerTorso", staw=(0.1, 0.3, -0.5), czesc=(0.28, 0.28, 0.86), srodek=(0.33, -0.06, -0.28))
    p.kosc("TailTip", "Tail", staw=(0.75, 0.24, -1.05), czesc=(0.28, 1.15, 0.28), srodek=(0, 0.52, 0))
    # kości nośne kapelusza i kostura (bez brył): w spoczynku w ramkach HatAttachment i RightGripAttachment
    zh, zg = p.zaczepy["HatAttachment"], p.zaczepy["RightGripAttachment"]
    p.kosc("HatPivot", "Head", staw=tuple(p.staw("Head")[i] + zh["p"][i] for i in range(3)))
    p.kosc("StaffPivot", "RightHand", staw=tuple(p.staw("RightHand")[i] + zg["p"][i] for i in range(3)))
    p.zaczep("KapeluszAttachment", "HatPivot", (0, 0, 0), zh["r"])
    p.zaczep("KosturAttachment", "StaffPivot", (0, 0, 0), zg["r"])
    return p


def _golas(id, nazwa, zaczepy_ekwipunku=False):
    """Goły kot bez klipów: głowa, uszy, nogi, łapy i ogon jak w dawnym modelu, a tam, gdzie dawniej była szata —
    pomarańczowe futro w pełnym rozmiarze klocka z pręgami i jasnym brzuszkiem (detale wystają 0,02–0,04)."""
    p = _postac(id, nazwa)
    p.typ_ciala = CIALO_TYP

    # ---------------- głowa (układ: środek klocka głowy) — bez zmian
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "kot")
        # policzki-kępki: schodki po bokach — kocia sylwetka głowy
        for zn in (1, -1):
            p.blok("Kepka", (zn * (w / 2 + 0.07), -0.3, 0.0), (0.16, 0.42, 0.95), "kot")
            p.blok("Kepka mala", (zn * (w / 2 + 0.17), -0.38, 0.05), (0.1, 0.22, 0.6), "kot", faza=0.02)
        # paski na czole i z tyłu
        for i, x in enumerate((-0.22, 0.0, 0.22)):
            p.blok("Pasek czolo %d" % i, (x, h / 2 - 0.13 - (0.03 if x == 0 else 0), z + 0.015),
                   (0.1, 0.24 + (0.06 if x == 0 else 0), 0.05), "kot_ciemny", "matowy", faza=0.0)
        for i, y in enumerate((0.25, -0.05)):
            p.blok("Pasek tyl %d" % i, (0, y, -z - 0.015), (1.1 - 0.25 * i, 0.12, 0.05), "kot_ciemny", "matowy",
                   faza=0.0)
        # oczy: duże, czarne, z dwoma błyskami
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.38
            p.blok("Oko " + s, (x, 0.12, z + 0.02), (0.32, 0.46, 0.06), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.05, 0.23, z + 0.055), (0.11, 0.13, 0.03), "bialy", faza=0.0)
            p.blok("Blysk maly " + s, (x + 0.07, 0.0, z + 0.055), (0.05, 0.06, 0.03), "bialy", faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.62, -0.17, z + 0.012), (0.22, 0.1, 0.03), "rumieniec", "matowy",
                   faza=0.0)
            # wąsy: dwa z każdej strony, wystają poza obrys głowy
            for i, (dy, kat) in enumerate(((-0.2, 8), (-0.32, -6))):
                p.blok("Was %s%d" % (s, i), (zn * 0.78, dy, z + 0.03), (0.6, 0.04, 0.04), "tusz", "matowy",
                       rot=(0, 0, zn * kat), faza=0.0)
        # pyszczek: jasna mordka, różowy nos, uśmiech „w”
        p.blok("Mordka", (0, -0.36, z + 0.025), (0.8, 0.44, 0.08), "kot_jasny", "matowy", faza=0.03)
        p.blok("Broda", (0, -0.58, z - 0.12), (0.52, 0.12, 0.3), "kot_jasny", "matowy", faza=0.02)
        p.blok("Nos", (0, -0.2, z + 0.09), (0.24, 0.13, 0.07), "nos", "polysk", faza=0.03)
        p.blok("Nos dol", (0, -0.27, z + 0.085), (0.1, 0.05, 0.06), "nos", "polysk", faza=0.0)
        # kocie usta „ω”: same kreski tuszu (bez czarnego wypełnienia) — dwie małe litery v obok siebie
        for zn in (1, -1):
            p.blok("Usta a", (zn * 0.06, -0.37, z + 0.075), (0.12, 0.035, 0.04), "tusz", rot=(0, 0, -zn * 30),
                   faza=0.0)
            p.blok("Usta b", (zn * 0.165, -0.37, z + 0.075), (0.12, 0.035, 0.04), "tusz", rot=(0, 0, zn * 30),
                   faza=0.0)

    # uszy (trójkątne, odchylone na zewnątrz; przebijają rondo kapelusza z obu stron) — bez zmian
    for zn, s, kosc in ((1, "L", "LeftEar"), (-1, "P", "RightEar")):
        with p.na(kosc, obrot=(0, 0, -zn * 28)):
            p.ostroslup("Ucho " + s, (0, 0.36, 0), (0.56, 0.72, 0.32), "kot", gora=(0.0, 0.12),
                        przes_gory=(zn * 0.05, 0))
            p.ostroslup("Ucho srodek " + s, (0, 0.3, 0.17), (0.32, 0.5, 0.04), "nos", "matowy",
                        gora=(0.0, 0.03), przes_gory=(zn * 0.03, 0), faza=0.0)

    # ---------------- tułów: futro, jasny brzuszek z kępką pod brodą, pręgi na plecach i bokach (dawniej szata)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Futro tulow", (0, 0, 0), (w, h, d), "kot")
        p.blok("Brzuszek", (0, -0.13, z), (0.8, 0.56, 0.04), "kot_jasny", "matowy", faza=0.03)
        p.blok("Brzuszek gora", (0, 0.22, z), (0.56, 0.16, 0.04), "kot_jasny", "matowy", faza=0.03)
        for i, x in enumerate((-0.15, 0.0, 0.15)):                # kępka futra pod brodą: trzy ząbki
            p.ostroslup("Kepka piersi %d" % i, (x, 0.35, z), (0.17, 0.13 + (0.02 if x == 0 else 0), 0.04),
                        "kot_jasny", "matowy", gora=(0.0, 0.04), faza=0.0)
        for i, (y, szer, bok) in enumerate(((0.2, 0.9, 0.5), (-0.1, 0.7, 0.36))):
            p.blok("Prega plecy %d" % i, (0, y, -z - 0.005), (szer, 0.1, 0.05), "kot_ciemny", "matowy", faza=0.0)
            for zn, s in ((1, "L"), (-1, "P")):
                p.blok("Prega bok %s%d" % (s, i), (zn * (w / 2 + 0.005), y, -z + bok / 2), (0.05, 0.1, bok),
                       "kot_ciemny", "matowy", faza=0.0)

    # ---------------- biodra: futro, dół brzuszka, futro u nasady ogona (ogon wychodzi nisko, spod dawnej szaty)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        sr = p.staw("LowerTorso")[1] + p.srodek("LowerTorso")[1]      # wysokość środka klocka bioder w modelu
        p.blok("Futro biodra", (0, 0, 0), (w, h, d), "kot")
        p.blok("Brzuszek dol", (0, 0.015, z), (0.66, 0.2, 0.04), "kot_jasny", "matowy", faza=0.03)
        # pas futra od tyłu bioder (y = 0,84) do stawu ogona (0,1; 0,3; −0,5), z jedną pręgą
        p.blok("Ogon u nasady", (0.1, 0.48 - sr, -0.5), (0.28, 0.72, 0.28), "kot", faza=0.04)
        p.blok("Ogon u nasady pasek", (0.1, 0.52 - sr, -0.5), (0.32, 0.08, 0.32), "kot_ciemny", "matowy", faza=0.02)

    # ---------------- nogi i łapy — bez zmian (dawniej w środku dzwonu szaty)
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperLeg"):                             # staw biodra (x = ±0,3, y = 0,75)
            p.blok("Udo", (0, -0.15, 0), (0.42, 0.3, 0.42), "kot", faza=0.03)
        with p.na(s + "LowerLeg", od="srodek"):
            p.blok("Lydka", (0, 0, 0), (0.4, 0.3, 0.4), "kot", faza=0.03)
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Lapa", (0, 0, 0), (w, h, d), "kot")
            # łapa wysunięta do przodu — wystaje spod rąbka szaty
            p.blok("Lapa przod", (0, -0.01, d / 2 + 0.2), (w, h - 0.02, 0.42), "kot", faza=0.04)
            p.blok("Palce", (0, -0.01, d / 2 + 0.33), (w + 0.04, h - 0.02, 0.2), "kot_jasny", "matowy", faza=0.03)
            for i, x in enumerate((-0.12, 0.12)):
                p.blok("Szpara %d" % i, (x, 0.02, d / 2 + 0.442), (0.03, 0.1, 0.04), "kot_ciemny", faza=0.0)

    # ---------------- ręce: futro z pręgą na ramieniu i przedramieniu (dawniej rękawy), łapki bez zmian
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Futro ramie", (0, 0, 0), (w, h, d), "kot")
            p.blok("Prega ramie", (0, -0.05, 0), (w + 0.04, 0.07, d + 0.04), "kot_ciemny", "matowy", faza=0.02)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Futro przedramie", (0, 0, 0), (w, h, d), "kot")
            p.blok("Prega przedramie", (0, 0.04, 0), (w + 0.04, 0.07, d + 0.04), "kot_ciemny", "matowy", faza=0.02)
        with p.na(s + "Hand"):                                 # staw nadgarstka
            p.blok("Lapka", (0, -0.19, 0), (0.38, 0.32, 0.38), "kot", faza=0.05)
            p.blok("Lapka palce", (0, -0.31, 0.13), (0.3, 0.08, 0.14), "kot_jasny", "matowy", faza=0.02)

    # ---------------- ogon: dwie dodatkowe kości (kołysanie) — bez zmian
    with p.na("Tail", obrot=(0, -50, 0)):
        p.blok("Ogon nasada", (0, -0.06, -0.47), (0.28, 0.28, 1.0), "kot", faza=0.04)     # zachodzi na końcówkę
        p.blok("Ogon pasek", (0, -0.06, -0.62), (0.32, 0.32, 0.08), "kot_ciemny", "matowy", faza=0.02)
    with p.na("TailTip", obrot=(0, -50, -10)):
        p.blok("Ogon srodek", (0, 0.45, 0), (0.28, 1.24, 0.28), "kot", faza=0.04)
        p.blok("Ogon zawijas", (0, 1.12, 0.12), (0.28, 0.26, 0.52), "kot", faza=0.04)
        p.blok("Ogon koncowka", (0, 1.05, 0.4), (0.28, 0.22, 0.14), "kot_jasny", "matowy", faza=0.03)
        for k, y in enumerate((0.2, 0.5, 0.8)):
            p.blok("Ogon pasek %d" % k, (0, y, 0), (0.32, 0.08, 0.32), "kot_ciemny", "matowy", faza=0.02)

    for c in p.czesci:
        c["golas"] = True                                     # gołe bryły (zdejmuje je powłoka na tej kości)
    if zaczepy_ekwipunku:
        for kosc in R15_KOSCI:
            p.zaczep(zaczep_ekwipunku(kosc), kosc, p.srodek(kosc))
    return p


# --------------------------------------------------------------------------- przedmioty stroju
def przedmioty():
    """Wszystkie przedmioty Kota-Maga — rozbiór dawnego modelu z EKWIPUNEK.md pkt 3. Bryły są te same co w dawnym
    zbuduj() (te same liczby), tylko pogrupowane w segmenty po kościach; bryły modelowane dawniej od stawu kości
    (biodra, przedramiona) są przesunięte o środek klocka (układ segmentu = środek klocka)."""
    m = _postac(ID + "_miara", NAZWA)
    W = m.wymiary

    def nowy(id, nazwa, slot, kategoria, **k):
        return Przedmiot(id, nazwa, slot, kategoria, m, cialo=CIALO_TYP, klasy=KLASY, zestaw=ID, paleta=PALETA, **k)

    def od_stawu(kosc):                       # układ stawu kości w segmencie (środek klocka): przesunięcie −środek
        return tuple(-v for v in m.srodek(kosc))

    # --- kapelusz (Helmet): na zaczepie; korekta na HatPivot w KOREKTY_CHWYTU; uszy przechodzą przez rondo
    kap = nowy("kot_mag_kapelusz", "Kapelusz Kota-Maga", "Helmet", "Armor")
    kap.na_zaczepie(kapelusz())

    # --- szata (Chest): kołnierz w szpic, zapinka z klejnotem, kaptur na plecach, za długie rękawy, dzwon z trenem
    sz = nowy("kot_mag_szata", "Szata Kota-Maga", "Chest", "Armor")
    a = sz.segment("UpperTorso", zakrywa=True)
    w, h, d = W("UpperTorso")
    z = d / 2 + 0.05
    a.blok("Szata gora", (0, 0, 0), (w + 0.1, h + 0.02, d + 0.1), "szata", "matowy")
    a.blok("Piers", (0, h / 2 - 0.2, z + 0.012), (0.36, 0.36, 0.04), "kot_jasny", "matowy", faza=0.0)
    for zn in (1, -1):
        a.blok("Kolnierz", (zn * 0.17, h / 2 - 0.2, z + 0.03), (0.15, 0.52, 0.06), "szata_ciemna", "matowy",
               rot=(0, 0, zn * 28), faza=0.02)
    a.blok("Listwa", (0, -0.12, z + 0.02), (0.16, 0.6, 0.05), "szata_ciemna", "matowy", faza=0.0)
    a.blok("Zapinka", (0, 0.04, z + 0.05), (0.26, 0.26, 0.06), "zloto", "metal", rot=(0, 0, 45), faza=0.03)
    a.blok("Klejnot", (0, 0.04, z + 0.09), (0.13, 0.13, 0.04), "krysztal", "swiecacy", rot=(0, 0, 45), faza=0.0)
    a.blok("Ramiona", (0, h / 2 - 0.03, 0), (w + 0.26, 0.16, d + 0.22), "szata_ciemna", "matowy")
    a.blok("Kaptur", (0, h / 2 - 0.12, -d / 2 - 0.12), (1.0, 0.5, 0.26), "szata_ciemna", "matowy")
    a.klin("Kaptur szpic", (0, h / 2 - 0.5, -d / 2 - 0.14), (0.5, 0.3, 0.2), "szata_ciemna", "matowy",
           rot=(180, 180, 0))
    for s in ("Left", "Right"):
        a = sz.segment(s + "UpperArm", zakrywa=True)
        a.blok("Rekaw", (0, 0, 0), (0.5, 0.48, 0.5), "szata", "matowy")
        a = sz.segment(s + "LowerArm", zakrywa=True)
        with a.uklad(pos=od_stawu(s + "LowerArm")):          # staw łokcia
            a.ostroslup("Mankiet", (0, -0.24, 0), (0.76, 0.48, 0.76), "szata", "matowy", rot=(180, 0, 0),
                        gora=(0.5, 0.5))
            a.blok("Obszycie rekawa", (0, -0.43, 0), (0.79, 0.1, 0.79), "szata_ciemna", "matowy", faza=0.03)
            a.blok("Wnetrze rekawa", (0, -0.485, 0), (0.62, 0.02, 0.62), "tusz", "matowy", faza=0.0)
    # za duża szata: jeden ośmiokątny dzwon od pasa (y ≈ 1,0) do ziemi (y ≈ 0,1), szerszy u dołu o 0,25 z każdej
    # strony; nogi chodzą w środku, spod rąbka wystają tylko łapy. Z tyłu tren leżący na ziemi.
    a = sz.segment("LowerTorso", zakrywa=True)
    with a.uklad(pos=od_stawu("LowerTorso")):                 # (0,0,0) = staw bioder (y = 0,75 w modelu)
        a.stozek("Szata dzwon", (0, -0.2, -0.04), (2.1, 0.9, 1.75), "szata", "matowy", gora=0.72, segm=8)
        a.stozek("Szata rabek", (0, -0.61, -0.04), (2.16, 0.1, 1.8), "szata_ciemna", "matowy", gora=0.97, segm=8,
                 faza=0.0)
        a.stozek("Szata lamowka", (0, -0.53, -0.04), (2.07, 0.05, 1.73), "wstazka", "matowy", gora=0.99, segm=8,
                 faza=0.0)
        a.blok("Szata pola", (0, -0.2, 0.62), (0.16, 0.8, 0.06), "szata_ciemna", "matowy", rot=(-14, 0, 0), faza=0.0)
        # tren: klin 1,6 × 0,15 × 0,7 leży na ziemi za piętami (wysoka ściana przy szacie, skos ku tyłowi)
        a.klin("Tren", (0, -0.665, -1.12), (1.6, 0.15, 0.7), "szata", "matowy", faza=0.03)

    # --- szarfa z klamrą (Belt): nakładka na biodrach (na gołym futrze +0,07 z boku, w pełnym stroju w dzwonie)
    pas = nowy("kot_mag_pas", "Szarfa z klamrą", "Belt", "Armor")
    a = pas.segment("LowerTorso")
    with a.uklad(pos=od_stawu("LowerTorso")):
        a.blok("Pas", (0, 0.13, 0), (1.44, 0.2, 1.1), "szata_ciemna", "matowy")
        a.blok("Pas klamra", (0, 0.13, 0.57), (0.26, 0.22, 0.06), "wstazka", "metal", faza=0.02)

    # --- kostur (Weapon): na zaczepie; korekta chwytu kota (StaffPivot) w KOREKTY_CHWYTU
    kos = nowy("kot_mag_kostur", "Kostur Kota-Maga", "Weapon", "Weapons")
    kos.na_zaczepie(kostur())
    return [kap, sz, pas, kos]


def wybierz(ids, wszystkie=None):
    """Przedmioty o podanych id (w tej kolejności) z listy `wszystkie` (domyślnie świeże przedmioty())."""
    wszystkie = {x.id: x for x in (wszystkie or przedmioty())}
    return [wszystkie[i] for i in ids]


# --------------------------------------------------------------------------- klipy, ciało, stroje
_ODNIESIENIE = []


def postac_odniesienia():
    """Dawny model (pełny strój z kapeluszem i kosturem) z klipami policzonymi tak jak przed D-071 — źródło klipów
    każdego stroju. Liczona raz na proces (klipy zależą od geometrii: stopy na ziemi, tor upadku kapelusza
    i kostura)."""
    if not _ODNIESIENIE:
        p = ubierz(_golas(ID, NAZWA), wybierz(ODNIESIENIE_KLIPOW), id=ID, nazwa=NAZWA, korekty=KOREKTY_CHWYTU)
        klipy(p)
        p.ustaw_poze_renderu("idle", 0)
        _ODNIESIENIE.append(p)
    return _ODNIESIENIE[0]


def cialo(zaczepy_ekwipunku=False):
    """Goły kot „kot_mag_cialo” z klipami postaci odniesienia. zaczepy_ekwipunku=True — dodatkowo 15 zaczepów
    Ekw<Kosc>Attachment (środek klocka kości) dla eksportu ciała do gry; w zbuduj() ich nie ma."""
    return kopiuj_klipy(postac_odniesienia(), _golas(ID + "_cialo", NAZWA + " (ciało bazowe)", zaczepy_ekwipunku))


def stroj(nazwa, wszystkie=None):
    """Kot-Mag w stroju z STROJE: postać „kot_mag_<nazwa>”."""
    return ubierz(cialo(), wybierz(STROJE[nazwa], wszystkie), id="%s_%s" % (ID, nazwa),
                  nazwa="%s — %s" % (NAZWA, NAZWY_STROJOW[nazwa]), korekty=KOREKTY_CHWYTU)


def zbuduj():
    """[Kot-Mag w pełnym stroju kanonicznym (id „kot_mag”), kapelusz, kostur] — jak przed D-071."""
    prz = przedmioty()
    p = ubierz(cialo(), wybierz(KANON, prz), id=ID, nazwa=NAZWA, korekty=KOREKTY_CHWYTU)
    po_id = {x.id: x for x in prz}
    # kapelusz i kostur: osobne przedmioty (przedmioty/kot_mag_*.fbx); w FBX kota ich nie ma (eksport=False),
    # w renderach i klipach są na kościach HatPivot / StaffPivot
    return [p, po_id["kot_mag_kapelusz"].segmenty[0]["akc"], po_id["kot_mag_kostur"].segmenty[0]["akc"]]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/kot_mag/ekwipunek/): „plansze” — postacie ze STROJE (id kot_mag_<strój>)
    i ikony całych przedmiotów; „eksport” — gołe ciało z zaczepami Ekw… (tylko klip idle: pozostałe klipy są
    w kot_mag__<klip>.fbx, te same kości) i każdy segment kostny osobno."""
    prz = przedmioty()
    if rodzaj == "plansze":
        return [stroj(n, prz) for n in STROJE] + [x.ikona() for x in prz]
    if rodzaj == "eksport":
        c = cialo(zaczepy_ekwipunku=True)
        c.klipy = [k for k in c.klipy if k.nazwa == "idle"]
        return [c] + [s["akc"] for x in prz for s in x.segmenty if s["kosc"]]
    raise ValueError("rodzaj: plansze albo eksport")


def ekwipunek_json():
    """Dane ekwipunku bohatera (EKWIPUNEK.md pkt 5); ścieżki plików i trójkąty dopisuje przebuduj.py. Przedmioty na
    zaczepie mają już korektę chwytu kota (zaczep KapeluszAttachment / KosturAttachment, kość HatPivot /
    StaffPivot)."""
    return {"bohater": ID, "cialo": CIALO_TYP, "klasy": list(KLASY), "kanon": list(KANON),
            "odniesienie_klipow": list(ODNIESIENIE_KLIPOW), "stroje": {k: list(v) for k, v in STROJE.items()},
            "wlosy": None,
            "korekty_chwytu": {z: {"zaczep": zz, "pos": list(pos), "rot": list(ob)}
                               for z, (zz, pos, ob) in KOREKTY_CHWYTU.items()},
            "przedmioty": [x.opis(KOREKTY_CHWYTU) for x in przedmioty()]}


# --------------------------------------------------------------------------- klipy-szkice (klucze co kilka klatek)
# poza bazowa: prawa łapa trzyma kostur lekko z przodu i na zewnątrz (kostur nie wchodzi w szatę)
BAZA = {"RightUpperArm": (-14, 0, -36), "RightLowerArm": (-8, 0, 0), "RightHand": (22, 0, 44),
        "LeftUpperArm": (4, 0, 9), "LeftLowerArm": (-10, 0, 0),
        "Tail": (20, 0, 0), "TailTip": (15, 0, 0)}           # ogon uniesiony od ziemi, końcówka zawinięta ku plecom


def klipy(p):
    idle(p)
    chod(p)
    czar(p)
    wiwat(p)
    atak(p)
    kula_ognia(p)
    lodowy_pocisk(p)
    bariera(p)
    unik(p)
    trafienie(p)
    upadek(p)


def idle(p):
    """Oddech, przechył głowy, ogon kołysze się na boki (końcówka z opóźnieniem) — pętla 2 s. Klip sprzed 15.11
    bez zmian (uszy stoją: kości uszu doszły później, a istniejących klipów bez potrzeby nie ruszamy)."""
    k = p.klip("idle", 60, petla=True)
    k.poza(0, BAZA)
    k.cykl("Tail", "obrot", (0, 12, 3))
    k.cykl("TailTip", "obrot", (0, 12, 8), faza=0.3)
    k.cykl("UpperTorso", "obrot", (2.5, 0, 0), faza=0.25)
    k.cykl("Head", "obrot", (2, 0, 5), faza=0.1)
    k.cykl("LeftUpperArm", "obrot", (0, 0, 3), faza=0.25)
    k.cykl("RightUpperArm", "obrot", (-2, 0, 0), faza=0.25)
    return k


def chod(p):
    """Drobne, szybkie kroki; płaty szaty na udach falują; ogon i głowa w rytmie (pętla). Klip sprzed 15.11 bez
    zmian (znane: palce łap schodzą do 0,22 studa pod ziemię, lewy rękaw zachodzi na szatę — patrz SLABOSCI)."""
    k = p.klip("chod", 20, petla=True)
    k.poza(0, BAZA)
    k.cykl("LeftUpperLeg", "obrot", (14, 0, 0))                # ≤ 15°: nogi zostają w dzwonie szaty
    k.cykl("RightUpperLeg", "obrot", (14, 0, 0), faza=0.5)
    k.cykl("LeftLowerLeg", "obrot", (12, 0, 0), faza=0.25, srodek=(12, 0, 0))
    k.cykl("RightLowerLeg", "obrot", (12, 0, 0), faza=0.75, srodek=(12, 0, 0))
    k.cykl("LeftFoot", "obrot", (-10, 0, 0), faza=0.1)
    k.cykl("RightFoot", "obrot", (-10, 0, 0), faza=0.6)
    k.cykl("LowerTorso", "przes", (0, 0.06, 0), faza=0.0, czestosc=2, srodek=(0, 0.03, 0))
    k.cykl("LowerTorso", "obrot", (0, 7, 3))
    k.cykl("UpperTorso", "obrot", (0, -9, -2))
    k.cykl("UpperTorso", "obrot", (4, 0, 0), czestosc=2, faza=0.1, srodek=(5, 0, 0))   # lekki skłon w marszu
    k.cykl("LeftUpperArm", "obrot", (-24, 0, 0))
    k.cykl("RightUpperArm", "obrot", (-7, 0, 0), faza=0.5)
    k.cykl("Head", "obrot", (3, 0, 0), czestosc=2, faza=0.35)
    k.cykl("Head", "obrot", (0, 4, 3), faza=0.5)
    k.cykl("Tail", "obrot", (0, 16, 4), faza=0.2)
    k.cykl("TailTip", "obrot", (0, 22, 10), faza=0.05)
    return k


# ---------------------------------------------------------------------------------------- pozy kluczowe co klatkę
KOSCI = ("LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
         "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg",
         "RightFoot", "Tail", "TailTip", "LeftEar", "RightEar")
NOSNE = ("HatPivot", "StaffPivot")                        # kości nośne kapelusza i kostura (obrót i przesunięcie)
STOPY = ("LeftFoot", "RightFoot")
CIALO = ("Head", "UpperTorso", "LowerTorso", "LeftEar", "RightEar")   # tu kostur ani łapa nie może wejść
KONCZYNY = ("LeftLowerArm", "LeftHand", "RightLowerArm", "RightHand")


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


def _bryly(p):
    """Wszystkie bryły (ciało i założone akcesoria) w układzie stawu swojej kości: lista słowników
    {kosc, c, R, h, k (kształt), g (zwężenie ku górze: (fx, fz) albo None), pg, n, zrodlo, pkt (27 punktów)}."""
    if getattr(p, "_bryly", None) is None:
        d = p.json()
        wynik = []

        def dodaj(c, zrodlo):
            st = p.kosci[c["kosc"]]["staw"]
            h = tuple(v / 2.0 for v in c["s"])
            g, pg = None, (0.0, 0.0)
            if c["k"] == "stozek":
                g = (c["gora"], c["gora"])
            elif c["k"] == "ostroslup":
                g = (c["gora"][0] / c["s"][0], c["gora"][1] / c["s"][2])
                pg = tuple(c.get("pg", (0.0, 0.0)))
            b = {"kosc": c["kosc"], "c": tuple(c["p"][i] - st[i] for i in range(3)), "R": macierz_obrotu(*c["r"]),
                 "h": h, "k": c["k"], "g": g, "pg": pg, "n": c["n"], "zrodlo": zrodlo}
            b["pkt"] = _siatka(b, None)
            wynik.append(b)
        for c in d["czesci"]:
            dodaj(c, "cialo")
        for a in d["akcesoria"]:
            for c in a["czesci"]:
                dodaj(c, a["id"])
        p._bryly = wynik
    return p._bryly


def _siatka(b, krok):
    """Punkty skrzynki bryły w układzie stawu: krok=None — 3×3×3, inaczej gęsto (co najwyżej `krok` studa)."""
    osie = []
    for i in range(3):
        n = 2 if krok is None else max(2, int(math.ceil(2 * b["h"][i] / krok)))
        osie.append([(-1 + 2.0 * j / n) * b["h"][i] for j in range(n + 1)])
    pk = []
    for x in osie[0]:
        for y in osie[1]:
            for z in osie[2]:
                lok = razy_wektor(b["R"], (x, y, z))
                pk.append(tuple(b["c"][i] + lok[i] for i in range(3)))
    return pk


def _glebokosc_bryly(b, q):
    """Jak głęboko punkt q (układ stawu kości bryły) siedzi w bryle: odległość do najbliższej ściany (≤ 0 = poza).
    Stożek i ostrosłup zwężają się ku górze (+Y bryły), klin opada ku −Z; reszta to skrzynka."""
    d = (q[0] - b["c"][0], q[1] - b["c"][1], q[2] - b["c"][2])
    R = b["R"]
    x = R[0][0] * d[0] + R[1][0] * d[1] + R[2][0] * d[2]
    y = R[0][1] * d[0] + R[1][1] * d[1] + R[2][1] * d[2]
    z = R[0][2] * d[0] + R[1][2] * d[1] + R[2][2] * d[2]
    hx, hy, hz = b["h"]
    gy = hy - abs(y)
    if gy <= 0:
        return gy
    if b["g"] is not None:
        t = (y + hy) / (2 * hy)
        x -= b["pg"][0] * t
        z -= b["pg"][1] * t
        hx *= 1 - t * (1 - b["g"][0])
        hz *= 1 - t * (1 - b["g"][1])
    elif b["k"] == "klin":                                # wysoka ściana +Z, skos ku −Z
        gy = min(gy, (z + hz) / (2 * hz) * 2 * hy - (y + hy))
    return min(gy, hx - abs(x), hz - abs(z))


def _najnizej(p, W, kosci, akcesoria=False):
    mn = 1e9
    for b in _bryly(p):
        if b["kosc"] not in kosci or (b["zrodlo"] != "cialo" and not akcesoria):
            continue
        R, t = W[b["kosc"]]
        for q in b["pkt"]:
            mn = min(mn, R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1])
    return mn


def _stopy_plasko(p, pz):
    """Stopy, których poza nie ustawia: płasko na ziemi, palcami tam, gdzie patrzą biodra."""
    W = _fk(p, pz)
    for s in ("Left", "Right"):
        if s + "Foot" in pz.get("_wlasne", ()):
            continue
        Rg = W[s + "LowerLeg"][0]
        f = razy_wektor(mnoz(W["LowerTorso"][0], macierz_obrotu(0, pz[s + "UpperLeg"]["obrot"][1], 0)), (0, 0, 1))
        cel = macierz_obrotu(0, math.degrees(math.atan2(f[0], f[2])), 0)
        pz[s + "Foot"] = {"obrot": tuple(round(v, 3) for v in katy_z_macierzy(mnoz(_tr(Rg), cel)))}


def _poza(p, poza, ziemia=True):
    """Poza kluczowa: {kość: (rx, ry, rz)} albo {kość: {"obrot":…, "przes":…}}; kość spoza słownika — spoczynek.
    ziemia=True: stopy (jeśli poza ich nie ustawia) płasko, biodra w pionie tak, by najniższy punkt stóp był na
    ziemi; ziemia="cialo": całe ciało dociągnięte do ziemi po najniższym punkcie (leżenie); ziemia=False: lot."""
    pz = {"_wlasne": tuple(n for n in poza)}
    for n in KOSCI + NOSNE:
        v = poza.get(n, (0, 0, 0))
        pz[n] = dict(v) if isinstance(v, dict) else {"obrot": tuple(v)}
        pz[n].setdefault("obrot", (0, 0, 0))
    pz["LowerTorso"].setdefault("przes", (0, 0, 0))
    pz["_ziemia"] = ziemia
    _na_ziemi(p, pz)
    return pz


def _na_ziemi(p, pz):
    z = pz["_ziemia"]
    if z is True:
        _stopy_plasko(p, pz)
        dno = _najnizej(p, _fk(p, pz), STOPY)
    elif z == "cialo":
        dno = _najnizej(p, _fk(p, pz), tuple(p.kosci))
    else:
        dno = min(0.0, _najnizej(p, _fk(p, pz), tuple(p.kosci)))
    x, y, zz = pz["LowerTorso"]["przes"]
    pz["LowerTorso"]["przes"] = (x, round(y - dno, 4), zz)


# ------------------------------------------------------------------ łapa celuje: prosta odwrotna kinematyka (2 kości)
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


def _reka(p, pz, strona, cel, biegun, os=None, przod=None, swiat=True):
    """Ustawia w pozie pz ramię, przedramię i dłoń strony („Left”/„Right”) tak, żeby nadgarstek trafił w cel.
    cel = przesunięcie od stawu barku, biegun = kierunek łokcia — w osiach modelu (swiat=True) albo tułowia.
    os / przod = kierunek osi +Y i +Z dłoni: dla prawej łapy to oś drzewca kostura (ku kryształowi) i przód
    kryształu; dla łapki bez kostura +Y dłoni wskazuje łokieć (palce są w −Y), +Z = wnętrze łapki."""
    W = _fk(p, pz)
    Rt = W["UpperTorso"][0]
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
        Rh = _kolumny(_kr(A, F), A, F)
        pz[strona + "Hand"] = {"obrot": katy_z_macierzy(mnoz(_tr(Rla), Rh))}
    return pz


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku −170° → +170° przez zero)."""
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


def _chwyt(p, pz, strona):
    """Ułożenie łapy w pozie jako cel dla _reka (osie modelu): nadgarstek od barku, kierunek łokcia, osie dłoni."""
    W = _fk(p, pz)
    bark, lokiec, nadg = W[strona + "UpperArm"][1], W[strona + "LowerArm"][1], W[strona + "Hand"][1]
    Rh = W[strona + "Hand"][0]
    cel = tuple(nadg[i] - bark[i] for i in range(3))
    dh = _n(cel)
    e = tuple(lokiec[i] - bark[i] for i in range(3))
    biegun = _n(tuple(e[i] - _sk(e, dh) * dh[i] for i in range(3)))
    return {"cel": cel, "biegun": biegun, "os": (Rh[0][1], Rh[1][1], Rh[2][1]), "przod": (Rh[0][2], Rh[1][2], Rh[2][2])}


def _miesz(a, b, e):
    return tuple(a[i] + (b[i] - a[i]) * e for i in range(3))


def _sekwencja(k, czasy, pozy, wyg=None, zycie=None, swobodne=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza albo słownik). Kąty przechodzą z łagodnym wejściem
    i wyjściem (wyg = {numer pozy: "liniowo"} — odcinek od tej pozy jednostajnie). Łapy NIE idą po kątach stawów:
    między pozami przesuwa się nadgarstek, kierunek łokcia i osie dłoni (z nimi oś kostura), a stawy liczy w każdej
    klatce odwrotna kinematyka — kostur obraca się po najkrótszej drodze i nie zatacza łuku przez głowę.
    zycie(f) -> {kość: (drx, dry, drz)} dokłada drgania (ogon, uszy, potrząśnięcia) przed dociągnięciem do ziemi.
    swobodne(f, pz) ustawia w pozie kości nośne (kapelusz, kostur) po dociągnięciu do ziemi."""
    p = k.postac
    pozy = [pz if "_ziemia" in pz else _poza(p, pz) for pz in pozy]
    chwyty = [{s: _chwyt(p, pz, s) for s in ("Left", "Right")} for pz in pozy]
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
              for n in KOSCI + NOSNE}
        p0, p1 = a["LowerTorso"]["przes"], b["LowerTorso"]["przes"]
        pz["LowerTorso"]["przes"] = tuple(p0[j] + (p1[j] - p0[j]) * e for j in range(3))
        if 0.0 < e < 1.0:
            for s in ("Left", "Right"):
                ca, cb = chwyty[i][s], chwyty[i + 1][s]
                _reka(p, pz, s, cel=_miesz(ca["cel"], cb["cel"], e), biegun=_miesz(ca["biegun"], cb["biegun"], e),
                      os=_n(_miesz(ca["os"], cb["os"], e)), przod=_n(_miesz(ca["przod"], cb["przod"], e)))
        if zycie:
            for n, dv in zycie(f).items():
                pz[n]["obrot"] = tuple(pz[n]["obrot"][j] + dv[j] for j in range(3))
        z0, z1 = a["_ziemia"], b["_ziemia"]
        pz["_wlasne"] = tuple(set(a["_wlasne"]) | set(b["_wlasne"]))
        pz["_ziemia"] = z0 if z0 == z1 else False
        _na_ziemi(p, pz)
        if swobodne:
            swobodne(f, pz)
        for n in KOSCI:
            ob = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = ob
            k.klucz(f, n, obrot=tuple(round(v, 3) for v in ob), wyg="liniowo")
        k.klucz(f, "LowerTorso", przes=tuple(round(v, 4) for v in pz["LowerTorso"]["przes"]), wyg="liniowo")
        if swobodne:
            for n in NOSNE:
                ob = _ciaglosc(pz[n]["obrot"], poprz.get(n))
                poprz[n] = ob
                k.klucz(f, n, obrot=tuple(round(v, 3) for v in ob), przes=tuple(
                    round(v, 4) for v in pz[n].get("przes", (0, 0, 0))), wyg="liniowo")


def _z(baza, **zmiany):
    d = dict(baza)
    d.update(zmiany)
    return d


def _fala(f, okres, faza=0.0):
    return math.sin(2 * math.pi * (f / float(okres) + faza))


def _okno(f, f0, f1, wejscie=3):
    """1 w środku przedziału f0…f1, łagodnie 0 na brzegach (wejście / wyjście w `wejscie` klatkach)."""
    if f <= f0 or f >= f1:
        return 0.0
    return min(1.0, (f - f0) / float(wejscie), (f1 - f) / float(wejscie))


def _baza(p):
    """Poza z klatki 0 klipu idle: {kość: (rx, ry, rz)} — klipy walki zaczynają się i kończą w niej."""
    k = next(k for k in p.klipy if k.nazwa == "idle")
    return {n: tuple(round(v, 3) for v in (k.wartosc(n, "obrot", 0) or (0, 0, 0))) for n in KOSCI}


# kierunki w osiach modelu (kot patrzy w +Z, jego lewa strona to +X)
PRZOD, GORA = (0, 0, 1), (0, 1, 0)


def _kostur(p, pz, cel, os, przod=PRZOD, biegun=(-1, -1, 0)):
    """Prawa łapa z kosturem: nadgarstek w `cel` (od prawego barku, osie modelu), drzewce wzdłuż `os` (ku
    kryształowi), przód kryształu `przod`. Łokieć domyślnie na zewnątrz i w dół (biegun)."""
    return _reka(p, pz, "Right", cel=cel, biegun=biegun, os=os, przod=przod)


def _lapka(p, pz, cel, palce=(0, -1, 0), wnetrze=PRZOD, biegun=(1, -1, 0)):
    """Lewa (wolna) łapka: nadgarstek w `cel` (od lewego barku), palce w stronę `palce`, wnętrze łapki `wnetrze`."""
    return _reka(p, pz, "Left", cel=cel, biegun=biegun, os=tuple(-v for v in palce), przod=wnetrze)


def _koniec(p, B):
    return _poza(p, dict(B))


def _bez_stop(pz, **zmiany):
    """Kopia pozy (same kąty, bez stóp — te ustawi _poza płasko) ze zmianami."""
    return _z({n: v["obrot"] for n, v in pz.items() if n in KOSCI and n not in STOPY}, **zmiany)


# Łapy są krótkie (bark → nadgarstek 0,64 studa), a barki siedzą tuż pod szeroką głową z kępkami policzków:
# uniesiona łapa nie wchodzi w głowę tylko odchylona mocno na zewnątrz (nadgarstek ≥ 0,58 w bok, ≤ 0,2 nad barkiem,
# łokieć na zewnątrz i w dół), a łapa wyciągnięta do przodu — poniżej brody (pozycje sprawdzone liczbowo, kontrola).
KOSTUR_W_GORZE = dict(cel=(-0.58, 0.2, 0.1), os=(-0.12, 1, 0.12))
LAPKA_W_GORZE = dict(cel=(0.58, 0.2, 0.1), palce=(1, 0.6, 0.2), wnetrze=(0, 0, 1))


# ------------------------------------------------------------------------------------------------- czar i wiwat
def czar(p, dl=54):
    """Czar (1,8 s): przygarbienie i nabranie powietrza (kl. 9), łapa z kosturem w górę i na zewnątrz — kostur stoi
    pionowo z prawej strony głowy, kryształ obok ronda kapelusza (kl. 17), kryształ „pulsuje” (potrząśnięcia
    kosturem kl. 21–37), wolna łapka uniesiona w bok, powrót. 15.11: przepisany pozami kluczowymi — wcześniej kostur
    przechodził przez głowę."""
    k = p.klip("czar", dl, petla=False)
    B = _baza(p)
    skulony = _poza(p, _z(B, UpperTorso=(10, -12, 0), Head=(8, 0, 0), Tail=(-10, 0, 0), TailTip=(5, 0, 0),
                          LeftEar=(-12, 0, -6), RightEar=(-12, 0, 6),
                          LeftUpperLeg=(-10, 0, 0), RightUpperLeg=(-10, 0, 0), LeftLowerLeg=(20, 0, 0),
                          RightLowerLeg=(20, 0, 0)))
    _kostur(p, skulony, cel=(-0.42, -0.42, 0.22), os=(-0.12, 1, 0.12))
    _lapka(p, skulony, cel=(0.38, -0.42, 0.3), palce=(0.2, -0.3, 1), wnetrze=(-0.3, 1, 0))
    gora = _poza(p, _z(B, UpperTorso=(-8, 10, 0), Head=(-12, 0, 0), Tail=(32, 0, 0), TailTip=(20, 0, 0),
                       LeftEar=(6, 0, 4), RightEar=(6, 0, -4)))
    _kostur(p, gora, **KOSTUR_W_GORZE)
    _lapka(p, gora, **LAPKA_W_GORZE)

    def zycie(f):
        w = _okno(f, 19, 39, 2)
        return {"RightHand": (6 * w * _fala(f - 19, 4), 0, 0),
                "TailTip": (0, 14 * _fala(f, 27), 0), "Tail": (0, 6 * _fala(f, 27, 0.25), 0),
                "LeftEar": (0, 0, -6 * w * _fala(f, 8)), "RightEar": (0, 0, 6 * w * _fala(f, 8))}
    opuszcza = _poza(p, _bez_stop(gora, UpperTorso=(-2, 4, 0), Head=(-4, 0, 0)))
    _kostur(p, opuszcza, cel=(-0.62, -0.15, 0.1), os=(-0.12, 1, 0.12))
    _lapka(p, opuszcza, cel=(0.6, -0.2, 0.1), palce=(1, 0.2, 0.2), wnetrze=(0, 0, 1))
    _sekwencja(k, (0, 9, 17, 40, 46, dl), (_koniec(p, B), skulony, gora, gora, opuszcza, _koniec(p, B)), zycie=zycie)
    return k


def wiwat(p, dl=30):
    """Radość (pętla 1 s): przysiad, podskok z łapkami w górze — kostur pionowo z prawej strony, z dala od głowy,
    lewa łapka wysoko w bok — lądowanie. Ogon i uszy podskakują. 15.11: przepisany pozami kluczowymi (wcześniej
    kostur wchodził w głowę)."""
    k = p.klip("wiwat", dl, petla=True)
    B = _baza(p)
    przysiad = _poza(p, _z(B, LeftUpperLeg=(-16, 0, 0), RightUpperLeg=(-16, 0, 0),
                           LeftLowerLeg=(32, 0, 0), RightLowerLeg=(32, 0, 0),
                           UpperTorso=(8, 0, 0), Head=(5, 0, 0), Tail=(5, 0, 0), TailTip=(0, 0, 0),
                           LeftEar=(-8, 0, -4), RightEar=(-8, 0, 4)))
    _kostur(p, przysiad, cel=(-0.42, -0.42, 0.22), os=(-0.12, 1, 0.12))
    _lapka(p, przysiad, cel=(0.38, -0.42, 0.3), palce=(0.2, -0.6, 1), wnetrze=(-0.4, 1, 0))
    lot = _poza(p, _z(B, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0.8, 0)},
                      LeftUpperLeg=(-12, 0, 6), RightUpperLeg=(-12, 0, -6),
                      LeftLowerLeg=(34, 0, 0), RightLowerLeg=(34, 0, 0),
                      LeftFoot=(16, 0, 0), RightFoot=(16, 0, 0),
                      UpperTorso=(-8, 0, 0), Head=(-12, 0, 0), Tail=(40, 0, 0), TailTip=(25, 0, 0),
                      LeftEar=(8, 0, 6), RightEar=(8, 0, -6)), ziemia=False)
    _kostur(p, lot, **KOSTUR_W_GORZE)
    _lapka(p, lot, cel=(0.6, 0.14, 0.1), palce=(1, 0.6, 0.2), wnetrze=(0, 0, 1))
    laduje = _poza(p, _z(B, LeftUpperLeg=(-6, 0, 0), RightUpperLeg=(-6, 0, 0), LeftLowerLeg=(10, 0, 0),
                         RightLowerLeg=(10, 0, 0), Tail=(12, 0, 0), TailTip=(10, 0, 0)))
    _kostur(p, laduje, cel=(-0.55, -0.1, 0.15), os=(-0.12, 1, 0.12))
    _lapka(p, laduje, cel=(0.55, -0.1, 0.15), palce=(1, 0.3, 0.2), wnetrze=(0, 0, 1))

    def zycie(f):
        return {"TailTip": (0, 26 * _fala(f, 15), 0), "Head": (0, 0, 6 * _fala(f, 30, 0.25))}
    _sekwencja(k, (0, 10, 14, 22, dl), (przysiad, lot, lot, laduje, przysiad), wyg={0: "liniowo"}, zycie=zycie)
    return k


# ------------------------------------------------------------------------------------------------- klipy walki
def atak(p, dl=26):
    """Zwykły atak (0,87 s): szybki błysk z kostura. Krótki zamach — kostur odchylony w tył, kryształ za prawym
    barkiem (kl. 5) — i wyrzut kryształu do przodu na wysokość głowy przeciwnika z lekkim wypadem i skrętem tułowia:
    WYPUSZCZENIE iskry w kl. 9 (kryształ najdalej z przodu), dobicie do kl. 13, powrót."""
    k = p.klip("atak", dl, petla=False)
    B = _baza(p)
    zamach = _poza(p, _z(B, LowerTorso={"obrot": (0, -12, 0)}, UpperTorso=(-6, -14, 0), Head=(-4, 10, 0),
                         Tail=(30, -10, 0), TailTip=(20, 0, 0), LeftEar=(-10, 0, -8), RightEar=(-10, 0, 8),
                         LeftUpperLeg=(-8, 0, 0), LeftLowerLeg=(14, 0, 0)))
    _kostur(p, zamach, cel=(-0.5, -0.1, -0.3), os=(-0.15, 0.7, -0.7))
    _lapka(p, zamach, cel=(0.4, -0.3, 0.4), palce=(0, -0.3, 1), wnetrze=(-0.5, 1, 0))
    blysk = _poza(p, _z(B, LowerTorso={"obrot": (3, 12, 0), "przes": (0, 0, 0.18)}, UpperTorso=(8, 14, 0),
                        Head=(-6, -8, 0), Tail=(-6, 10, 0), TailTip=(-4, 0, 0), LeftEar=(6, 0, 4),
                        RightEar=(6, 0, -4), RightUpperLeg=(-12, 0, 0), RightLowerLeg=(16, 0, 0),
                        LeftUpperLeg=(8, 0, 0)))
    _kostur(p, blysk, cel=(-0.3, -0.05, 0.55), os=(0.0, 0.35, 1), przod=GORA)
    _lapka(p, blysk, cel=(0.42, -0.4, -0.15), palce=(0.3, -1, -0.4), wnetrze=(-1, 0, 0))
    dobicie = _poza(p, _bez_stop(blysk, LowerTorso={"obrot": (4, 13, 0), "przes": (0, 0, 0.2)},
                                 UpperTorso=(10, 15, 0)))
    _kostur(p, dobicie, cel=(-0.3, -0.1, 0.55), os=(0.0, 0.28, 1), przod=GORA)
    wraca = _poza(p, _z(B, UpperTorso=(3, 4, 0)))
    _kostur(p, wraca, cel=(-0.4, -0.38, 0.3), os=(-0.12, 1, 0.3))

    def zycie(f):
        return {"TailTip": (0, 10 * _fala(f, 26), 0)}
    _sekwencja(k, (0, 5, 9, 13, 20, dl), (_koniec(p, B), zamach, blysk, dobicie, wraca, _koniec(p, B)),
               wyg={1: "liniowo"}, zycie=zycie)
    return k


def kula_ognia(p, dl=54):
    """Kula ognia (1,8 s): przysiad i zebranie mocy (kostur nisko przed sobą, kl. 8), wielki zamach — łapa
    z kosturem w górę i w tył, kryształ wysoko z prawej strony głowy i za nią, tułów odchylony i skręcony, ogon
    w górę (kl. 18–22), rzut: kostur przelatuje łukiem z prawej strony głowy do przodu, WYPUSZCZENIE kuli w kl. 27
    (kryształ celuje w przeciwnika), wolna łapa wyciągnięta do celu; dobicie w dół, kryształ nisko przed kotem
    (kl. 33 — rzut „zza głowy” kończy się niżej niż atak), powrót."""
    k = p.klip("kula_ognia", dl, petla=False)
    B = _baza(p)
    zbiera = _poza(p, _z(B, UpperTorso=(14, -6, 0), Head=(4, 4, 0), Tail=(-8, 0, 0), TailTip=(4, 0, 0),
                         LeftEar=(-14, 0, -8), RightEar=(-14, 0, 8),
                         LeftUpperLeg=(-16, 0, 0), RightUpperLeg=(-16, 0, 0), LeftLowerLeg=(30, 0, 0),
                         RightLowerLeg=(30, 0, 0)))
    _kostur(p, zbiera, cel=(-0.42, -0.42, 0.25), os=(-0.1, 0.8, 0.6))
    _lapka(p, zbiera, cel=(0.4, -0.4, 0.35), palce=(-0.3, -0.2, 1), wnetrze=(-1, 0, 0))
    zamach = _poza(p, _z(B, LowerTorso={"obrot": (0, -16, 0)}, UpperTorso=(-10, -14, 0), Head=(-10, 12, 0),
                         Tail=(40, -8, 0), TailTip=(30, 0, 0), LeftEar=(10, 0, 6), RightEar=(10, 0, -6),
                         LeftUpperLeg=(-10, 0, 0), LeftLowerLeg=(16, 0, 0)))
    _kostur(p, zamach, cel=(-0.58, 0.15, -0.15), os=(-0.18, 0.88, -0.45))
    _lapka(p, zamach, cel=(0.42, -0.2, 0.4), palce=(0.3, 0.1, 1), wnetrze=(-1, 0, 0))
    zamach2 = _poza(p, _bez_stop(zamach, UpperTorso=(-12, -16, 0), Head=(-12, 14, 0),
                                 LowerTorso={"obrot": (0, -18, 0)}))
    _kostur(p, zamach2, cel=(-0.58, 0.15, -0.2), os=(-0.2, 0.82, -0.55))
    rzut = _poza(p, _z(B, LowerTorso={"obrot": (4, 16, 0), "przes": (0, 0, 0.25)}, UpperTorso=(10, 16, 0),
                       Head=(-8, -10, 0), Tail=(-10, 12, 0), TailTip=(-6, 0, 0), LeftEar=(-4, 0, -2),
                       RightEar=(-4, 0, 2), RightUpperLeg=(-14, 0, 0), RightLowerLeg=(18, 0, 0),
                       LeftUpperLeg=(10, 0, 0)))
    _kostur(p, rzut, cel=(-0.3, -0.05, 0.55), os=(0.0, 0.12, 1), przod=GORA)
    _lapka(p, rzut, cel=(0.5, -0.25, 0.36), palce=(0.2, 0.1, 1), wnetrze=(-1, 0, 0))
    dobicie = _poza(p, _bez_stop(rzut, LowerTorso={"obrot": (6, 18, 0), "przes": (0, 0, 0.3)},
                                 UpperTorso=(14, 18, 0)))
    _kostur(p, dobicie, cel=(-0.32, -0.3, 0.48), os=(0.0, -0.28, 1), przod=GORA)
    _lapka(p, dobicie, cel=(0.5, -0.28, 0.35), palce=(0.2, 0.0, 1), wnetrze=(-1, 0, 0))
    wraca = _poza(p, _z(B, UpperTorso=(4, 4, 0), Tail=(10, 0, 0)))
    _kostur(p, wraca, cel=(-0.4, -0.38, 0.3), os=(-0.12, 1, 0.3))
    _lapka(p, wraca, cel=(0.4, -0.45, 0.2), palce=(0.2, -1, 0.3), wnetrze=(-1, 0, 0))

    def zycie(f):
        w = _okno(f, 18, 23, 2)
        return {"RightHand": (5 * w * _fala(f - 18, 4), 0, 0), "TailTip": (0, 12 * _fala(f, 27), 0)}
    _sekwencja(k, (0, 8, 18, 22, 27, 33, 40, dl), (_koniec(p, B), zbiera, zamach, zamach2, rzut, dobicie, wraca,
                                                   _koniec(p, B)), wyg={3: "liniowo"}, zycie=zycie)
    return k


def lodowy_pocisk(p, dl=46):
    """Lodowy pocisk (1,53 s), inna sylwetka niż kula ognia: kostur poziomo, nisko jak lanca, kryształem do celu,
    cofnięty przy prawym boku (kl. 8), lewa łapka z przodu dłonią do celu, przysiad i drżenie ładowania (kl. 8–16),
    potem pchnięcie — obie łapy do przodu, wypad całym ciałem, WYPUSZCZENIE pocisku w kl. 21; zatrzymanie, powrót."""
    k = p.klip("lodowy_pocisk", dl, petla=False)
    B = _baza(p)
    podnosi = _poza(p, _z(B, UpperTorso=(4, -6, 0), Tail=(20, 0, 0), LeftEar=(-8, 0, -4), RightEar=(-8, 0, 4)))
    _kostur(p, podnosi, cel=(-0.5, -0.38, 0.0), os=(-0.1, 0.6, 0.8))
    cofa = _poza(p, _z(B, LowerTorso={"obrot": (0, -10, 0), "przes": (0, 0, -0.1)}, UpperTorso=(-2, -10, 0),
                       Head=(-4, 10, 0), Tail=(24, 0, 0), TailTip=(30, 0, 0), LeftEar=(-16, 0, -10),
                       RightEar=(-16, 0, 10), LeftUpperLeg=(-20, 0, 0), RightUpperLeg=(-14, 0, 0),
                       LeftLowerLeg=(36, 0, 0), RightLowerLeg=(28, 0, 0)))
    _kostur(p, cofa, cel=(-0.42, -0.45, -0.1), os=(0.05, 0.05, 1), przod=GORA)
    _lapka(p, cofa, cel=(0.38, -0.25, 0.45), palce=(0, 1, 0.2), wnetrze=(0, 0, 1))
    pchniecie = _poza(p, _z(B, LowerTorso={"obrot": (5, 10, 0), "przes": (0, 0, 0.35)}, UpperTorso=(8, 12, 0),
                            Head=(-10, -8, 0), Tail=(-12, 0, 0), TailTip=(-8, 0, 0), LeftEar=(-6, 0, -4),
                            RightEar=(-6, 0, 4), RightUpperLeg=(-22, 0, 0), RightLowerLeg=(26, 0, 0),
                            LeftUpperLeg=(12, 0, 0)))
    _kostur(p, pchniecie, cel=(-0.3, -0.3, 0.5), os=(0.05, 0.05, 1), przod=GORA)
    _lapka(p, pchniecie, cel=(0.4, -0.25, 0.45), palce=(-0.1, 1, 0.2), wnetrze=(0, 0, 1))
    trzyma = _poza(p, _bez_stop(pchniecie, LowerTorso={"obrot": (6, 10, 0), "przes": (0, 0, 0.38)},
                                UpperTorso=(10, 12, 0)))
    wraca = _poza(p, _z(B, LowerTorso={"obrot": (2, 2, 0), "przes": (0, 0, 0.12)}, UpperTorso=(4, 2, 0)))
    _kostur(p, wraca, cel=(-0.5, -0.38, 0.1), os=(-0.1, 0.7, 0.7))
    _lapka(p, wraca, cel=(0.4, -0.45, 0.2), palce=(0.2, -1, 0.3), wnetrze=(-1, 0, 0))

    def zycie(f):
        w = _okno(f, 8, 17, 2)
        return {"UpperTorso": (0, 0, 2.5 * w * _fala(f, 3)), "RightHand": (0, 3 * w * _fala(f, 3, 0.25), 0),
                "TailTip": (0, 8 * _fala(f, 23), 14 * w * _fala(f, 4))}
    _sekwencja(k, (0, 4, 8, 17, 21, 28, 36, dl),
               (_koniec(p, B), podnosi, cofa, cofa, pchniecie, trzyma, wraca, _koniec(p, B)),
               wyg={3: "liniowo"}, zycie=zycie)
    return k


def bariera(p, dl=42):
    """Bariera (1,4 s): przyczajenie — kostur nisko przed sobą, uszy po sobie (kl. 4), potem szybkie wzniesienie:
    kostur pionowo w górę z prawej strony, kryształ wysoko obok szpica kapelusza, lewa łapka wypchnięta dłonią do
    przodu, szeroki przysiad, uszy czujnie w górę, ogon wysoko (kl. 10 — KRĄG bariery); poza trzymana do kl. 30
    (kostur lekko drży, oddech, ogon zawija się), powrót. 15.11 (przegląd): wcześniej kostur stał nisko z prawej,
    a poza trzymana prawie nie różniła się sylwetką od spoczynku."""
    k = p.klip("bariera", dl, petla=False)
    B = _baza(p)
    nogi = dict(LeftUpperLeg=(-16, 0, 6), RightUpperLeg=(-16, 0, -6), LeftLowerLeg=(30, 0, 0),
                RightLowerLeg=(30, 0, 0))
    czai = _poza(p, _z(B, UpperTorso=(12, -8, 0), Head=(8, 4, 0), Tail=(-8, 0, 0), TailTip=(6, 0, 0),
                       LeftEar=(-20, 0, -10), RightEar=(-20, 0, 10), LeftUpperLeg=(-12, 0, 0),
                       RightUpperLeg=(-12, 0, 0), LeftLowerLeg=(24, 0, 0), RightLowerLeg=(24, 0, 0)))
    _kostur(p, czai, cel=(-0.42, -0.42, 0.22), os=(-0.12, 1, 0.12))
    _lapka(p, czai, cel=(0.38, -0.42, 0.3), palce=(0.2, -0.3, 1), wnetrze=(-0.3, 1, 0))
    wznosi = _poza(p, _z(B, UpperTorso=(-6, 8, 0), Head=(-10, -6, 0), Tail=(36, 0, 0), TailTip=(24, 0, 0),
                         LeftEar=(10, 0, 4), RightEar=(10, 0, -4), **nogi))
    _kostur(p, wznosi, cel=(-0.58, 0.2, 0.1), os=(-0.1, 1, 0.22))
    _lapka(p, wznosi, cel=(0.35, -0.2, 0.48), palce=(0, 1, 0.1), wnetrze=(0, 0, 1))
    trzyma = _poza(p, _bez_stop(wznosi, UpperTorso=(-4, 8, 0), Head=(-8, -6, 0)))

    def zycie(f):
        w = _okno(f, 11, 30, 2)
        return {"TailTip": (0, 16 * _fala(f, 21), 0), "UpperTorso": (1.5 * w * _fala(f, 18), 0, 0),
                "RightHand": (2.5 * w * _fala(f, 5), 0, 0),
                "LeftEar": (0, 0, -5 * w * _fala(f, 10)), "RightEar": (0, 0, 5 * w * _fala(f, 10))}
    _sekwencja(k, (0, 4, 10, 30, dl), (_koniec(p, B), czai, wznosi, trzyma, _koniec(p, B)), zycie=zycie)
    return k


def unik(p, dl=28):
    """Koci unik (0,93 s): przysiad z uszami po sobie (kl. 3), zwinny odskok w tył i w lewo — grzbiet wygięty, ogon
    wysoko w górę (szczyt kl. 7), miękkie lądowanie ok. 1,6 studa dalej (kl. 11), krótki podskok z powrotem i
    lądowanie w punkcie startu (kl. 24)."""
    k = p.klip("unik", dl, petla=False)
    B = _baza(p)
    nogi_lot = {"LeftUpperLeg": (-14, 0, 6), "RightUpperLeg": (-14, 0, -6), "LeftLowerLeg": (34, 0, 0),
                "RightLowerLeg": (34, 0, 0), "LeftFoot": (14, 0, 0), "RightFoot": (14, 0, 0)}
    nogi_przysiad = {"LeftUpperLeg": (-18, 0, 0), "RightUpperLeg": (-18, 0, 0), "LeftLowerLeg": (36, 0, 0),
                     "RightLowerLeg": (36, 0, 0)}
    przysiad = _poza(p, _z(B, UpperTorso=(14, 0, 4), Head=(6, 0, 0), Tail=(-6, 0, 0), TailTip=(10, 0, 0),
                           LeftEar=(-30, 0, -14), RightEar=(-30, 0, 14), **nogi_przysiad))
    _kostur(p, przysiad, cel=(-0.45, -0.42, 0.15), os=(-0.15, 1, 0.1))
    _lapka(p, przysiad, cel=(0.4, -0.45, 0.2), palce=(0.2, -1, 0.2), wnetrze=(-1, 0, 0))
    lot = _poza(p, _z(B, LowerTorso={"obrot": (-4, 16, -6), "przes": (0.75, 0.75, -0.75)}, UpperTorso=(-10, 4, -4),
                      Head=(4, -10, 4), Tail=(55, 0, 0), TailTip=(35, 0, 0), LeftEar=(-36, 0, -16),
                      RightEar=(-36, 0, 16), **nogi_lot), ziemia=False)
    _kostur(p, lot, cel=(-0.58, 0.05, 0.1), os=(-0.3, 1, 0.1))
    _lapka(p, lot, cel=(0.58, 0.05, 0.1), palce=(1, 0.2, 0), wnetrze=(0, 0, 1))
    laduje = _poza(p, _z(B, LowerTorso={"obrot": (0, 14, 0), "przes": (1.15, 0, -1.15)}, UpperTorso=(16, 4, 0),
                         Head=(-4, -6, 0), Tail=(20, 0, 0), TailTip=(30, 0, 0), LeftEar=(-20, 0, -10),
                         RightEar=(-20, 0, 10), **nogi_przysiad))
    _kostur(p, laduje, cel=(-0.45, -0.42, 0.2), os=(-0.2, 1, 0.15))
    _lapka(p, laduje, cel=(0.4, -0.45, 0.25), palce=(0, -1, 0.3), wnetrze=(-1, 0, 0))
    podskok = _poza(p, _z(B, LowerTorso={"obrot": (4, 6, 0), "przes": (0.55, 0.35, -0.55)}, UpperTorso=(4, 2, 0),
                          Head=(-2, -2, 0), Tail=(30, 0, 0), TailTip=(20, 0, 0), **nogi_lot), ziemia=False)
    _kostur(p, podskok, cel=(-0.45, -0.25, 0.15), os=(-0.2, 1, 0.1))
    ostatni = _poza(p, _z(B, UpperTorso=(6, 0, 0), Tail=(14, 0, 0), LeftUpperLeg=(-8, 0, 0),
                          RightUpperLeg=(-8, 0, 0), LeftLowerLeg=(16, 0, 0), RightLowerLeg=(16, 0, 0)))

    def zycie(f):
        return {"TailTip": (0, 18 * _fala(f, 14), 0)}
    _sekwencja(k, (0, 3, 7, 11, 15, 19, 24, dl), (_koniec(p, B), przysiad, lot, laduje, laduje, podskok, ostatni,
                                                  _koniec(p, B)), wyg={1: "liniowo", 2: "liniowo"}, zycie=zycie)
    return k


def trafienie(p, dl=20):
    """Trafienie (0,67 s): krótkie szarpnięcie w tył w kl. 4 — tułów i głowa odrzucone, uszy po sobie, ogon
    nastroszony w górę, pół kroku w tył — i powrót do pozy wyjściowej."""
    k = p.klip("trafienie", dl, petla=False)
    B = _baza(p)
    szarp = _poza(p, _z(B, LowerTorso={"obrot": (-2, 6, 0), "przes": (0, 0, -0.3)}, UpperTorso=(-16, 8, 4),
                        Head=(-16, -10, 8), Tail=(50, 0, 0), TailTip=(-20, 0, 0), LeftEar=(-40, 0, -18),
                        RightEar=(-40, 0, 18), RightUpperLeg=(10, 0, 0), LeftUpperLeg=(-10, 0, 0),
                        LeftLowerLeg=(16, 0, 0)))
    _kostur(p, szarp, cel=(-0.5, -0.3, 0.1), os=(-0.35, 1, -0.1))
    _lapka(p, szarp, cel=(0.5, -0.25, 0.2), palce=(0.6, -0.5, 0.3), wnetrze=(-1, 0, 0))
    wraca = _poza(p, _z(B, LowerTorso={"obrot": (0, 2, 0), "przes": (0, 0, -0.12)}, UpperTorso=(-4, 2, 1),
                        Head=(-6, -2, 2), Tail=(30, 0, 0), LeftEar=(-12, 0, -6), RightEar=(-12, 0, 6)))
    _sekwencja(k, (0, 4, 11, dl), (_koniec(p, B), szarp, wraca, _koniec(p, B)), wyg={0: "liniowo"})
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): szarpnięcie (kl. 4), chwiejny krok w tył (kl. 12), kolana miękną (kl. 20), kot przewraca
    się na lewy bok (kl. 32) z odbiciem (kl. 37) i leży od kl. 44 (ostatnią klatkę zatrzymać). Kostur wypada z łapy
    w kl. 22 i ląduje płasko przed kotem (kl. 33); kapelusz zsuwa się z głowy w kl. 30 i staje obok niej (kl. 40)."""
    k = p.klip("upadek", dl, petla=False)
    B = _baza(p)
    szarp = _poza(p, _z(B, LowerTorso={"obrot": (-2, 4, 0), "przes": (0, 0, -0.3)}, UpperTorso=(-14, 8, 4),
                        Head=(-16, -8, 8), Tail=(45, 0, 0), TailTip=(-10, 0, 0), LeftEar=(-38, 0, -16),
                        RightEar=(-38, 0, 16), RightUpperLeg=(10, 0, 0), LeftUpperLeg=(-10, 0, 0)))
    _kostur(p, szarp, cel=(-0.5, -0.3, 0.1), os=(-0.35, 1, -0.1))
    _lapka(p, szarp, cel=(0.5, -0.25, 0.2), palce=(0.6, -0.5, 0.3), wnetrze=(-1, 0, 0))
    chwiej = _poza(p, _z(B, LowerTorso={"obrot": (0, -6, 8), "przes": (0, 0, -0.55)}, UpperTorso=(10, -6, -10),
                         Head=(16, 8, -12), Tail=(10, 0, 0), TailTip=(10, 0, 0), LeftEar=(-30, 0, -20),
                         RightEar=(-20, 0, 24), LeftUpperLeg=(8, 0, 4), RightUpperLeg=(-12, 0, -6),
                         LeftLowerLeg=(14, 0, 0), RightLowerLeg=(20, 0, 0)))
    _kostur(p, chwiej, cel=(-0.58, -0.15, 0.1), os=(-0.3, 0.6, -0.7))
    _lapka(p, chwiej, cel=(0.6, -0.22, 0.05), palce=(0.8, -0.3, 0), wnetrze=(0, 0, 1))
    ugina = _poza(p, _z(B, LowerTorso={"obrot": (0, -4, -10), "przes": (0, 0, -0.55)}, UpperTorso=(14, -4, -6),
                        Head=(18, 6, -10), Tail=(0, 0, 0), TailTip=(5, 0, 0), LeftEar=(-35, 0, -24),
                        RightEar=(-35, 0, 24), LeftUpperLeg=(-20, 0, 6), RightUpperLeg=(-16, 0, -4),
                        LeftLowerLeg=(40, 0, 0), RightLowerLeg=(36, 0, 0)))
    _kostur(p, ugina, cel=(-0.6, -0.1, 0.05), os=(-0.6, 0.5, -0.6))
    _lapka(p, ugina, cel=(0.55, -0.4, 0.1), palce=(0.4, -1, 0), wnetrze=(0, 0, 1))
    leci = _poza(p, _z(B, LowerTorso={"obrot": (0, -6, -48), "przes": (0.5, 0, -0.5)}, UpperTorso=(8, -4, -8),
                       Head=(10, 4, -4), Tail=(0, 0, 0), TailTip=(10, 0, 0), LeftEar=(-35, 0, -24),
                       RightEar=(-35, 0, 24), LeftUpperLeg=(-24, 0, 10), RightUpperLeg=(-20, 0, -6),
                       LeftLowerLeg=(44, 0, 0), RightLowerLeg=(40, 0, 0),
                       RightUpperArm=(-50, 0, -80), RightLowerArm=(-20, 0, 0), RightHand=(0, 0, 0),
                       LeftUpperArm=(-55, 0, 70), LeftLowerArm=(-15, 0, 0)), ziemia=False)
    lezy_d = _z(B, LowerTorso={"obrot": (0, -4, -88), "przes": (0.9, 0, -0.5)}, UpperTorso=(4, 0, 4),
                Head=(-6, 16, 10), Tail=(-20, 10, 0), TailTip=(-10, 30, 0), LeftEar=(-40, 0, -10),
                RightEar=(-40, 0, 26), LeftUpperLeg=(-30, 0, 6), RightUpperLeg=(-22, 0, -4),
                LeftLowerLeg=(50, 0, 0), RightLowerLeg=(46, 0, 0), LeftFoot=(10, 0, 0), RightFoot=(10, 0, 0),
                RightUpperArm=(-50, 0, -40), RightLowerArm=(-30, 0, 0), RightHand=(0, 0, 0),
                LeftUpperArm=(-50, 0, 10), LeftLowerArm=(-30, 0, 0))
    lezy = _poza(p, lezy_d, ziemia="cialo")
    odbicie = _poza(p, _z(lezy_d, LowerTorso={"obrot": (0, -4, -80), "przes": (0.85, 0, -0.5)}, Head=(-10, 20, 4),
                          RightUpperArm=(-60, 0, -55), TailTip=(10, 20, 0)), ziemia="cialo")
    drga = _poza(p, _z(lezy_d, Head=(-8, 20, 8), RightLowerLeg=(56, 0, 0), TailTip=(-20, 40, 0)), ziemia="cialo")

    # kostur i kapelusz: do chwili oderwania jadą z łapą / głową, potem po łuku w świecie na miejsce na ziemi
    stan = {}

    def swobodne(f, pz):
        W = _fk(p, pz)
        for kosc, f0, f1, cel_obrot, cel_xz, luk in UPADEK_LOT:
            if f <= f0:
                pz[kosc] = {"obrot": (0, 0, 0), "przes": (0, 0, 0)}
                if f == f0:
                    stan[kosc] = (katy_z_macierzy(W[kosc][0]), W[kosc][1])
                continue
            if kosc + "_cel" not in stan:
                Rc = macierz_obrotu(*cel_obrot)
                y0 = _dno_akcesorium(p, kosc, Rc)
                stan[kosc + "_cel"] = (cel_obrot, (cel_xz[0], -y0, cel_xz[1]))
            (a0, t0), (a1, t1) = stan[kosc], stan[kosc + "_cel"]
            a1 = _ciaglosc(a1, a0)
            u = min(1.0, (f - f0) / float(f1 - f0))
            e = u * u                                        # spada coraz szybciej
            ob = tuple(a0[i] + (a1[i] - a0[i]) * (u * (2 - u)) for i in range(3))
            T = [t0[0] + (t1[0] - t0[0]) * e, 0.0, t0[2] + (t1[2] - t0[2]) * (u * (2 - u))]
            T[1] = t0[1] + (t1[1] - t0[1]) * e + luk * 4 * u * (1 - u)
            _ustaw_w_swiecie(p, pz, W, kosc, macierz_obrotu(*ob), tuple(T))

    _sekwencja(k, (0, 4, 12, 20, 27, 32, 37, 44, 52, dl),
               (_koniec(p, B), szarp, chwiej, ugina, leci, lezy, odbicie, lezy, drga, lezy),
               wyg={4: "liniowo"}, swobodne=swobodne)
    return k


# kostur i kapelusz w upadku: (kość nośna, klatka oderwania, klatka na ziemi, obrót na ziemi w świecie, (x, z) na
# ziemi, wysokość łuku lotu)
UPADEK_LOT = (("StaffPivot", 22, 33, (90, 70, 0), (1.3, 1.5), 0.9),
              ("HatPivot", 30, 40, (0, -30, -12), (4.2, 0.5), 0.5))


def _dno_akcesorium(p, kosc, R):
    """Najniższy punkt brył akcesorium na kości nośnej `kosc` obróconej o R (względem stawu kości)."""
    mn = 1e9
    for b in _bryly(p):
        if b["kosc"] == kosc:
            for q in b["pkt"]:
                mn = min(mn, R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2])
    return mn


def _ustaw_w_swiecie(p, pz, W, kosc, Rw, Tw):
    """Kość nośna ma mieć w świecie obrót Rw i staw w Tw: lokalny obrót i przesunięcie względem rodzica."""
    rodzic = p.kosci[kosc]["rodzic"]
    Rp, tp = W[rodzic]
    Rl = mnoz(_tr(Rp), Rw)
    lok = razy_wektor(_tr(Rp), tuple(Tw[i] - tp[i] for i in range(3)))
    st, sr = p.kosci[kosc]["staw"], p.kosci[rodzic]["staw"]
    pz[kosc] = {"obrot": katy_z_macierzy(Rl), "przes": tuple(lok[i] - (st[i] - sr[i]) for i in range(3))}


# ---------------------------------------------------------------------------------------------------- kontrola
def _poza_klatki(p, kl, f, probki=None):
    poza = {}
    pr = (probki or {}).get(kl.nazwa)
    for n in p.kosci:
        for kanal in ("obrot", "przes"):
            if pr is not None:
                v = pr.get(n, {}).get(kanal)
                v = v[min(f, len(v) - 1)] if v else None
            else:
                v = kl.wartosc(n, kanal, f)
            if v is not None:
                poza.setdefault(n, {})[kanal] = tuple(v)
    return poza


def kontrola(p, probki=None, margines=0.06, krok=0.1, klipy_=None):
    """Liczbowa kontrola klipów: czy kostur, kapelusz albo przedramię / łapka wchodzi w głowę, uszy, tułów, dzwon
    szaty (każda bryła osobno, stożki i ostrosłupy zwężają się jak w modelu) albo kapelusz głębiej niż `margines`;
    najniższy punkt ciała i akcesoriów w każdej klatce; pętle domknięte. probki = {klip: {kość: {"obrot": [...],
    "przes": [...]}}} (z Blendera) — inaczej wartości kluczy modułu (klipy walki mają klucz w każdej klatce)."""
    br = _bryly(p)
    cele = [b for b in br if (b["zrodlo"] == "cialo" and b["kosc"] in CIALO and not b["n"].startswith("Was"))
            or b["zrodlo"] == "kot_mag_kapelusz"]
    ruchome = []
    for b in br:
        if b["zrodlo"] in ("kot_mag_kostur", "kot_mag_kapelusz"):
            ruchome.append((b["zrodlo"], b["kosc"], _siatka(b, krok)))
        elif b["zrodlo"] == "cialo" and b["kosc"] in KONCZYNY:
            ruchome.append((b["kosc"], b["kosc"], _siatka(b, krok)))
    # wstępny odsiew: skrzynka wszystkich brył-celów danej kości (w układzie jej stawu)
    pudla = {}
    for b in cele:
        mn, mx = pudla.setdefault(b["kosc"], ([1e9] * 3, [-1e9] * 3))
        for q in b["pkt"]:
            for i in range(3):
                mn[i], mx[i] = min(mn[i], q[i]), max(mx[i], q[i])
    wynik = {}
    for kl in p.klipy:
        if klipy_ and kl.nazwa not in klipy_:
            continue
        w = {"klatki": kl.dlugosc + 1, "petla": kl.petla, "twarde": [], "rekaw": [], "najnizej": (1e9, -1),
             "najnizej_cialo": (1e9, -1)}
        pierwsza = ostatnia = None
        for f in range(kl.dlugosc + 1):
            poza = _poza_klatki(p, kl, f, probki)
            if f == 0:
                pierwsza = poza
            ostatnia = poza
            W = _fk(p, poza)
            odw = {n: (_tr(W[n][0]), W[n][1]) for n in pudla}
            licz = {}
            for co, kosc, pkt in ruchome:
                R, t = W[kosc]
                for q in pkt:
                    s = razy_wektor(R, q)
                    s = (s[0] + t[0], s[1] + t[1], s[2] + t[2])
                    if s[1] < w["najnizej"][0]:
                        w["najnizej"] = (round(s[1], 3), f)
                    for n, (mn, mx) in pudla.items():
                        if co == "kot_mag_kapelusz" and n in ("Head", "LeftEar", "RightEar"):
                            continue                          # kapelusz siedzi na głowie, uszy go przebijają
                        Rt, tn = odw[n]
                        l = razy_wektor(Rt, (s[0] - tn[0], s[1] - tn[1], s[2] - tn[2]))
                        if any(l[i] < mn[i] - 0.01 or l[i] > mx[i] + 0.01 for i in range(3)):
                            continue
                        for b in cele:
                            if b["kosc"] != n or b["zrodlo"] == co:
                                continue
                            g = _glebokosc_bryly(b, l)
                            if g > margines:
                                cel = b["n"] if b["zrodlo"] == "cialo" else "kapelusz"
                                ile, gm = licz.get((co, cel, n), (0, 0.0))
                                licz[(co, cel, n)] = (ile + 1, max(gm, g))
            for (co, cel, n), (ile, gm) in sorted(licz.items()):
                # twarde: kostur albo kapelusz w czymkolwiek, łapa / rękaw w głowie, uszach, kapeluszu;
                # miękkie: rękaw albo łapka przy tułowiu i szacie (długi rękaw zachodzi na szatę już w spoczynku)
                twarde = co.startswith("kot_mag") or n in ("Head", "LeftEar", "RightEar", "HatPivot")
                w["twarde" if twarde else "rekaw"].append((f, co, cel, ile, round(gm, 3)))
            for b in br:                                   # najniższy punkt samego ciała
                if b["zrodlo"] == "cialo":
                    R, t = W[b["kosc"]]
                    for q in b["pkt"]:
                        y = R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1]
                        if y < w["najnizej_cialo"][0]:
                            w["najnizej_cialo"] = (round(y, 3), f)
                        if y < w["najnizej"][0]:
                            w["najnizej"] = (round(y, 3), f)
        if kl.petla:
            roz = 0.0
            for n in pierwsza:
                for kanal in pierwsza[n]:
                    a = pierwsza[n][kanal]
                    b = ostatnia.get(n, {}).get(kanal, a)
                    roz = max(roz, max(abs(a[i] - b[i]) for i in range(3)))
            w["szew_petli"] = round(roz, 3)
        wynik[kl.nazwa] = w
    return wynik


REKAW_SPOCZYNEK = 0.17    # o tyle lewy rękaw zachodzi na szatę już w pozie spoczynku (klatka 0 klipu idle)


def _wypisz_kontrole(wynik):
    """Wypisuje wynik kontroli; zwraca liczbę klatek z błędem (twarde przenikanie albo rękaw głębiej niż w spoczynku
    o więcej niż 0,05 studa)."""
    zle = 0
    for nazwa, w in wynik.items():
        klatki = sorted({x[0] for x in w["twarde"]})
        zle += len(klatki)
        print("%-14s %3d kl.  kostur / kapelusz w ciele, łapa w głowie, uszach, kapeluszu: %s" % (
            nazwa, w["klatki"], "BRAK" if not klatki else "%d kl., najgłębiej %.2f studa, np. %s" % (
                len(klatki), max(x[4] for x in w["twarde"]), w["twarde"][:4])))
        gl = max([x[4] for x in w["rekaw"]] or [0.0])
        zle += len({x[0] for x in w["rekaw"] if x[4] > REKAW_SPOCZYNEK + 0.05})
        print("%-14s          rękaw / łapka przy tułowiu i szacie: najgłębiej %.2f studa (w spoczynku %.2f)%s"
              % ("", gl, REKAW_SPOCZYNEK, "" if gl <= REKAW_SPOCZYNEK + 0.05 else "  <-- ZA GŁĘBOKO: %s" % (
                  [x for x in w["rekaw"] if x[4] > REKAW_SPOCZYNEK + 0.05][:4])))
        print("%-14s          najniższy punkt: ciało y = %.3f (kl. %d), z kosturem i kapeluszem y = %.3f (kl. %d)%s"
              % ("", w["najnizej_cialo"][0], w["najnizej_cialo"][1], w["najnizej"][0], w["najnizej"][1],
                 ("; szew pętli %.3f" % w["szew_petli"]) if "szew_petli" in w else ""))
    return zle


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--kontrola" in sys.argv:
        # --stroj <nazwa> — jeden strój z STROJE (domyślnie wszystkie); pozostałe argumenty bez „--” — wybrane klipy
        argumenty = sys.argv[1:]
        stroje = list(STROJE)
        if "--stroj" in argumenty:
            i = argumenty.index("--stroj")
            stroje = [argumenty[i + 1]]
            del argumenty[i:i + 2]
        wybrane = [a for a in argumenty if not a.startswith("--")]
        zle = 0
        for s in stroje:
            postac = stroj(s)
            print("=== strój „%s” (%s): %s" % (s, NAZWY_STROJOW[s], ", ".join(STROJE[s]) or "bez przedmiotów"))
            probki = None
            if "--blender" in argumenty:
                from swiat.postacie.roblox_postac import probki_z_blendera
                probki = probki_z_blendera([postac])[postac.id]
            zle += _wypisz_kontrole(kontrola(postac, probki, klipy_=wybrane or None))
        sys.exit(1 if zle else 0)
    zbuduj()
