# Próba techniczna: jedna małpa na szkielecie R15 (22.11.2026, propozycja)

Pytanie: czy jedna dwunożna małpa (mała małpka → goryl → olbrzymia małpa) może zagrać wszystkie 8 form na standardowym
szkielecie Roblox ze standardowymi animacjami chodu, biegu i spoczynku — bez riga z Blendera?
Skrypt: `swiat/ewolucja/proba_malpy.py --studio <id>` (buduje, próbuje w Play, mierzy, sprząta). Tymczasowe obiekty
(`Workspace/EwolucjaProbaMalpy`, `ServerStorage/EwolucjaProbaMalpy`) zostały usunięte; EwolucjaGra wyłączona tylko na
czas Play i przywrócona (włączona, wydanie do publikacji, atrybut `Wydanie` bez zmian).

## Wynik: tak, działa — z zastrzeżeniami
- **Rig**: 16 części ciała z klocków + pysk i oczy, nazwy i 15 stawów Motor6D jak w R15 (stawy tworzone wprost;
  `BuildRigFromAttachments` w trybie Edit nie zrobił żadnego). Proporcje małpy: krótkie nogi, ręce do kolan, duża głowa.
- **Animacje standardowe grają**: gracz (skrypt Animate skopiowany z jego domyślnej postaci) — WalkAnim i RunAnim przy
  skali 0,5×, 2× i 6×; boty (te same identyfikatory klipów przez Animator na serwerze) — wszystkie żywe boty miały
  grający klip.
- **Skala 0,5×–6× przez `Model:ScaleTo`**: HipHeight skaluje się sam (1,02 / 4,61 / 12,3), większość botów stoi na
  ziemi (20–21 z 22–23), bot 6× biegnie ze swoją prędkością (ok. 21 st/s). Prędkość chodu i skok trzeba ustawiać
  dla etapu samemu.
- **Etapy z jednego riga**: rozmiar, kolor futra i przyspawane dodatki — brwi, srebrny grzbiet, pancerz z naramiennikami,
  korona (zrzut `klatki/proba_malpy_etapy.jpg`: BABY MONKEY 0,6×, GORILLA 2×, GIANT APE 5×).
- **Klatka**: 16,7 ms (limit 60 kl./s) przy emulacji telefonu (Galaxy A06, 705 × 338) z graczem i 25 botami —
  na tym komputerze, nie na procesorze telefonu.

## Granice znalezione
1. Gdy serwer podmienia `Player.Character`, domyślna kamera zostaje przy starym ciele (ok. 1000 st dalej) — potrzebna
   linia u klienta (`CameraSubject`). Domyślna kamera nie rośnie z postacią: przy 2× i 6× jest w środku ciała.
   W grze i tak mamy własną kamerę z góry, która rośnie ze skalą.
2. **Fizyka postaci**: w każdej próbie 2–3 z 25 botów spadło z podłogi albo zostało z niej zepchniętych. Postacie
   różnej wielkości spychają się i piętrzą (zrzut `proba_malpy_skala6.jpg`). Ruch gracza w tłumie był blokowany:
   1,9–13,4 st/s przy WalkSpeed 16–24.
3. Klipy standardowe to chód człowieka (wyprostowany, ręce wahadłem), nie chód małpy na kłykciach. Własne klipy
   oznaczają wgranie animacji (zgoda ludzi).
4. Postać z Humanoidem porusza się po stronie klienta (właściciel sieciowy). Bez sprawdzania serwer przyjmie przyspieszony
   ruch — dziś pozycja jest sprawdzana prędkością.

## Jak to wpiąć w obecną logikę
- **Wersja pełna** (postać gracza = Humanoid): ruch, skoki i animacje za darmo; serwer czyta pozycję HRP zamiast
  przewidywania. Gryzienie, wzrost, złoto i boss zostają w logice, bo liczą odległości w 2D. Ewolucja to `ScaleTo` +
  dodatki etapu. Gorzej: kolizje i piętrzenie przy dużych skalach, hitboxy olbrzymów, ruch należący do klienta (trzeba
  sprawdzać prędkość), więcej pracy fizyki na serwerze przy 35 botach z Humanoidem.
- **Wersja mieszana (zalecana)**: logika i przewidywanie zostają jak są, a ta sama małpa jest tylko **wyglądem** —
  model u klienta z Animatorem gra standardowe klipy według prędkości z naszej symulacji. Bez fizyki postaci, bez
  piętrzenia, ta sama odpowiedź na wejście. Tej wersji ta próba nie sprawdziła (sprawdziła Animate gracza i Animator
  botów na serwerze), ale korzysta z tych samych klipów i tego samego riga.
- Wymiana form: tabela form jest już danymi, ale wymaga małej zmiany źródła modeli w `dane.py` / `zbuduj.py`:
  zamiast wzorców Pet Areny jeden rig + skala, kolor i lista dodatków na etap.
