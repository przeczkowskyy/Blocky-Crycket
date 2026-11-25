---
status: propozycja
tags: [ui, pety]
implementacja: w Studio na próbę, 2026-11-25 (polecenie Pawła, czeka na Karola)
---
# Okno petów (propozycja)

Okno otwierane przyciskiem **Pets** w [[HUD]]. Zamówił je Paweł 25.11.2026; układ wzorowany na oknach petów z gier Roblox. Dane petów i ich premie pochodzą z próby petów Karola (`swiat/pety_proba`), bez zmian w jego plikach.

## Opis
- **Góra:** 4 sloty założonych petów. Dwa są otwarte, dwa mają kłódkę — do odblokowania w późniejszym etapie gry (warunek nieustalony). Obok licznik „założone / dostępne sloty” (np. 1/2).
- **Dół:** wszystkie posiadane pety, siatka 8 × 3. Jeden kafelek na gatunek, z licznikiem kopii, podobizną 3D, nazwą i obwódką w kolorze rzadkości; nad siatką łączna liczba petów.
- **Klik** w peta na dole zakłada go, klik w założonego zdejmuje.
- **Przyciski:** EQUIP BEST (zakłada najrzadsze), UNEQUIP ALL, DELETE.
- **Podpowiedź** po najechaniu: nazwa, rzadkość, co pet daje graczowi (premie i pasywy z danych Karola), liczba kopii.

## Czego dziś nie ma (ograniczenia próby)
- Stan gracza Karola zna **jednego** aktywnego peta. Slot 1 to ten pet i tylko on daje premię. Slot 2 istnieje wyłącznie w oknie: premii nie daje i znika po wyjściu z gry.
- Peta ze slotu 1 nie da się zdjąć poza zagrodą (haczyk Karola pozwala tylko wybrać innego) — można go zamienić.
- DELETE odpowiada „coming soon”: w stanie gracza nie ma usuwania petów.
- Podobizny 3D buduje moduł Karola, który działa tylko w Studio (zob. [[Pytania otwarte]] 90).
- Opisy premii są po polsku (z danych Karola), reszta okna po angielsku.

## Stan implementacji
- [x] 2026-11-25: grafika okna i podpowiedzi z jednej generacji (`assets/raw/HudPety/arkusz_v1.png`, `tools/hud_pety_ui.py`), wgrana po „tak” Pawła (OknoPetow1–4, PodpowiedzPeta).
- [x] 2026-11-25: `src/gui/OknoPetow.model.json` (`tools/hud_pety_build_gui.py`), `src/client/OknoPetowClient.client.luau`, `src/server/OknoPetow.server.luau`; w Play sprawdzone: otwieranie, lista petów, zakładanie, zamiana, EQUIP BEST, odmowy, podpowiedź.
- [ ] Podobizny 3D w kafelkach obejrzane na ekranie (zrzuty z 25.11 nie łapały widoku 3D).
- [ ] Telefon (dotyk zamiast najechania).
- [ ] Arkusz w Figmie.

## Do ustalenia
- Drugi slot z premią, zdejmowanie poza zagrodą, usuwanie petów — [[Pytania otwarte]] 103.
- Warunek odblokowania slotów 3 i 4; limit liczby petów w plecaku.

## Powiązane
- [[HUD]] · [[Pytania otwarte]] · [[Dziennik zmian]]
