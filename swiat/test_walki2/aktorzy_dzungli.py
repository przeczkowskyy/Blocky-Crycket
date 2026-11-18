# -*- coding: utf-8 -*-
"""AKTORZY DŻUNGLI — wpisy pięciu potworów Dżungli w formacie tabeli AKTORZY z aktorzy.py (do dołączenia tam).

Modele: swiat/postacie/zwijogon.py, gebokwiat.py, kokosowy_silacz.py, pancernik_ruin.py, waz_stu_lian.py (status:
propozycja). Każdy moduł ma słownik CHWILE {klip: klatka} (trafienie / wypuszczenie efektu, szarpnięcie przy
trafieniu, największy odskok uniku), więc wpisy mają `chwile_modulu: True` i nie podają ręcznych `chwile`.

Punkty (Bron / Pocisk / Piers) siedzą dokładnie na zaczepach modeli — przesunięcie (0, 0, 0), więc nie ma kłopotu ze
znakami osi rigu Roblox (przód −Z). Wszystkie modele mają skalę 1,0 w module (pole `skala` niepotrzebne).

Klucze silnika: „zwijogon”, „gebokwiat”, „kokosowy_silacz”, „pancernik_ruin”, „waz_stu_lian” — takie jak nazwy
modułów. Umiejętności to istniejące id silnika (tools/walka/dane_walki.json), więc odtwarzacz zna ich choreografie
(swiat/test_walki2/zrodla/Choreografie.luau): skupienie i kamienna_skora = „na_siebie”, rozszarpanie i ciecie =
„wrecz”, lodowy_pocisk i zatruta_strzala = „pocisk” (leci od punktu Pocisk). Dane walki tych przeciwników (id
w silniku, poziomy, liczby) jeszcze nie istnieją — tools/walka/dane_walki.json bez zmian.
Dołączone na końcu tabeli w aktorzy.py, za Bagnem (galeria lasu, bohaterów i Bagna zostaje na swoich miejscach).
"""

# Bez pola „ruch_w_klipie” (jak potwory lasu i Bagna): odtwarzacz dokłada przy uniku swój ślizg do odskoku z klipu.
AKTORZY_DZUNGLI = [
    # Zwijogon (Polana Zwijogonów, Zwiadowca): cięcie prawą łapą (Bron = PazurAttachment na pazurach, kl. 12);
    # rozszarpanie = klip umiejetnosc (słupek podparty ogonem, cięcie lewą i prawą łapą na krzyż, trafienie kl. 28);
    # skupienie = osobny klip (przywiera do liści, oczy na wieżyczkach zatrzymują się na celu kl. 22 — aura).
    {"klucz": "zwijogon", "rola": "przeciwnik", "nazwa": "Zwijogon", "model": "zwijogon", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"skupienie": "skupienie", "rozszarpanie": "umiejetnosc"},
     "punkty": {"Bron": ("PazurAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Gębokwiat (Kwietnik Gębokwiatów, Mag): kłapnięcie paszczą (Bron = PaszczaAttachment przed zębami, kl. 13);
    # lodowy_pocisk = w grze usypiający pyłek: klip umiejetnosc (płatki w pąk, rozkwit, wyrzut z paszczy kl. 30 —
    # Pocisk = PaszczaAttachment, stamtąd odtwarzacz puszcza pocisk).
    {"klucz": "gebokwiat", "rola": "przeciwnik", "nazwa": "Gębokwiat", "model": "gebokwiat", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"lodowy_pocisk": "umiejetnosc"},
     "punkty": {"Bron": ("PaszczaAttachment", (0, 0, 0)), "Pocisk": ("PaszczaAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Kokosowy Siłacz (Gaj Kokosów, Wojownik): sierp prawym kokosem (Bron = KokosPAttachment w środku kokosa, kl. 15);
    # ciecie = klip umiejetnosc (oba kokosy znad głowy przed siebie kl. 26; punkt Bron na prawym kokosie, lewy uderza
    # symetrycznie po drugiej stronie celu — bez „celowanie”).
    {"klucz": "kokosowy_silacz", "rola": "przeciwnik", "nazwa": "Kokosowy Siłacz", "model": "kokosowy_silacz",
     "przerobka": None, "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"ciecie": "umiejetnosc"},
     "punkty": {"Bron": ("KokosPAttachment", (0, 0, 0)), "Pocisk": ("KokosPAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Pancernik Ruin (leże w ruinach, rzadki, Wojownik): szarża kamiennym hełmem (Bron = HelmAttachment na czole,
    # kl. 13); kamienna_skora = klip umiejetnosc (zwija się w kulę, kl. 22 płyty zamknięte i świecą szwy — aura
    # „kamien” robi odtwarzacz). Radość = ryk (60 klatek).
    {"klucz": "pancernik_ruin", "rola": "przeciwnik", "nazwa": "Pancernik Ruin", "model": "pancernik_ruin",
     "przerobka": None, "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"kamienna_skora": "umiejetnosc"},
     "punkty": {"Bron": ("HelmAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
    # Wąż Stu Lian (strażnik Dżungli, ok. 17 studów w zwoju z kwiatem-kapturem): ukąszenie (Bron = PyskAttachment
    # między kłami, kl. 18); zatruta_strzala = klip umiejetnosc (kaptur rozłożony, wyrzut łba i jad z paszczy kl. 28 —
    # Pocisk = PyskAttachment); rozszarpanie = klip ukaszenie (ukąszenie kl. 16 i szarpanie łbem). Piers = przód szyi
    # na wysokości ok. 8 studów. Radość = ryk (dokładnie 60 klatek, gra go przelot kamery).
    {"klucz": "waz_stu_lian", "rola": "przeciwnik", "nazwa": "Wąż Stu Lian", "model": "waz_stu_lian",
     "przerobka": None, "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"zatruta_strzala": "umiejetnosc", "rozszarpanie": "ukaszenie"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "zastepcze_klipy": []},
]
