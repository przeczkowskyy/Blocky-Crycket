# -*- coding: utf-8 -*-
"""AKTORZY BAGNA — wpisy pięciu potworów Bagna w formacie tabeli AKTORZY z aktorzy.py (do dołączenia tam).

Modele: swiat/postacie/rechotek.py, bulgotnik.py, klodoklap.py, ropucha_z_chatka.py, straznik_topieli.py (status:
propozycja). Każdy moduł ma słownik CHWILE {klip: klatka} (trafienie / wypuszczenie efektu, szarpnięcie przy
trafieniu, największy odskok uniku), więc wpisy mają `chwile_modulu: True` i nie podają ręcznych `chwile`.

Punkty (Bron / Pocisk / Piers) siedzą dokładnie na zaczepach modeli — przesunięcie (0, 0, 0), więc nie ma kłopotu ze
znakami osi rigu Roblox (przód −Z).

Uwaga: NIE podawaj pola `skala` dla Ropuchy z Chatką — moduł buduje ją w jednostkach ok. 1/2,9 studa i sam ustawia
skala=2.9 (`skala: 1.0` z wpisu zmniejszyłoby ją prawie trzy razy). Pozostałe modele mają skalę 1,0 w module.

Klucze silnika: „rechotek”, „bulgotnik”, „klodoklap”, „ropucha_z_chatka”, „straznik_topieli” — takie jak nazwy
modułów. Dane walki tych przeciwników są w swiat/bagno_pas_gra/przeciwnicy.py (kopia silnika w kontenerze Bagna;
tools/walka/dane_walki.json bez zmian); umiejętności to istniejące id silnika, więc odtwarzacz zna ich choreografie.
Dołączone na końcu tabeli w aktorzy.py (galeria lasu i bohaterów zostaje na swoich miejscach).
"""

# Bez pola „ruch_w_klipie” (jak potwory lasu): ten znacznik dotyczy dziś bohaterów R15 (kość LowerTorso — pilnuje
# tego swiat/test_walki2/testy/test_aktorow.py), więc odtwarzacz dokłada przy uniku swój ślizg do odskoku z klipu.
AKTORZY_BAGNA = [
    # Rechotek (Rechotne Oczka): lepki język w ataku (koniuszek języka = PyskAttachment, w kl. 12 ok. 2,3 studa przed
    # pyskiem), uderzenie z góry = klip umiejetnosc (przyczajenie, wybicie, zwinięcie, plaśnięcie kl. 30; łuk skoku
    # robi odtwarzacz, styl „skok”). Unik = sus 1,6 studa w lewo i z powrotem (ruch w klipie, najdalej kl. 12).
    {"klucz": "rechotek", "rola": "przeciwnik", "nazwa": "Rechotek", "model": "rechotek", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"uderzenie_z_gory": "umiejetnosc"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Bulgotnik (Bulgotne Trzęsawisko): cios kijem z ognikiem (Bron = OgnikAttachment, kl. 13), bariera = klip
    # umiejetnosc (obrót z kijem nad głową, nadęta bańka, uderzenie kijem w ziemię kl. 40 = krąg; styl „na_siebie”).
    {"klucz": "bulgotnik", "rola": "przeciwnik", "nazwa": "Bulgotnik", "model": "bulgotnik", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     # bariera (bańka na siebie) i trucizna z ognika — jeden klip umiejętności, chmura leci z punktu Pocisk (ognik)
     "umiejetnosci": {"bariera": "umiejetnosc", "chmura_zarodnikow": "umiejetnosc"},
     "punkty": {"Bron": ("OgnikAttachment", (0, 0, 0)), "Pocisk": ("OgnikAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Kłodokłap (Kłapiące Kępy): kłapnięcie z wypadu 0,6 studa (Bron = PyskAttachment między kłami, kl. 14), miażdżący
    # cios = klip umiejetnosc (paszcza szeroko, szarpnięcie 1,3 studa do przodu i zatrzaśnięcie kl. 26, szarpanie na
    # boki, cofnięcie — ruch w klipie jak u Wojownika).
    {"klucz": "klodoklap", "rola": "przeciwnik", "nazwa": "Kłodokłap", "model": "klodoklap", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"miazdzacy_cios": "umiejetnosc"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Ropucha z Chatką (Leże Ropuchy, rzadka): plaśnięcie prawą łapą (Bron = LapaAttachment, kl. 16); chmura
    # zarodników = klip umiejetnosc (komin wyrzuca kłęby kl. 30; Pocisk = KominAttachment — stamtąd odtwarzacz puszcza
    # chmurę, styl „chmura”); uderzenie z góry = klip skok (plaśnięcie kl. 34, styl „skok”). Radość = ryk.
    {"klucz": "ropucha_z_chatka", "rola": "przeciwnik", "nazwa": "Ropucha z Chatką", "model": "ropucha_z_chatka",
     "przerobka": None, "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"chmura_zarodnikow": "umiejetnosc", "uderzenie_z_gory": "skok"},
     "punkty": {"Bron": ("LapaAttachment", (0, 0, 0)), "Pocisk": ("KominAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Strażnik Topieli (strażnik Bagna, kolos ok. 15,5 studa z łódką): cios prawą pięścią z korzeni (Bron =
    # PiescAttachment, kl. 18), ogłuszające uderzenie = klip umiejetnosc (obie pięści w taflę kl. 38; falę robi
    # odtwarzacz), Pocisk = świecący rdzeń latarni w piersi, Piers = środek piersi. Radość = ryk (dokładnie 60 klatek,
    # gra go przelot kamery).
    {"klucz": "straznik_topieli", "rola": "przeciwnik", "nazwa": "Strażnik Topieli", "model": "straznik_topieli",
     "przerobka": None, "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"ogluszajace_uderzenie": "umiejetnosc"},
     "punkty": {"Bron": ("PiescAttachment", (0, 0, 0)), "Pocisk": ("LatarniaAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
]
