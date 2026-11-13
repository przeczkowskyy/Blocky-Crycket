# Krzywe Miasteczko — projekt mapy v2 (kontrakt dla budowniczych)

*Status: **propozycja** (noc 13.11.2026), nie kanon — kanonem może go uczynić tylko Game Director. Źródła wiedzy: opracowania `styl.md`, `rzemioslo.md`, `uklad.md`, `przepisy.md`, `ocena.md` (folder roboczy `noc/mapa/wiedza/`), notatka sejfu `B&C/Gra/Propozycje z rozmowy 2026-11-12.md` i kanon `B&C/Styl/Kierunek artystyczny.md`.*

> **W skrócie.** Hub gry to komiksowe, krzywe miasteczko fantasy z samych prymitywów Roblox, ułożone promieniście wokół rynku ze studnią-pomnikiem. Słońce stoi na północnym zachodzie, więc wszystkie miejsca pętli (karczma, zbrojownia, wylęgarnia, brama lochów) stoją po słonecznej, wschodniej i południowej stronie rynku, a gracz zaczyna na rynku plecami do słońca i od pierwszej klatki widzi ich oświetlone fronty. Najdalsze miejsce jest 8,8 s marszu od punktu wejścia; całość mieści się w 244 × 248 studach muru (kwadrat gry 300 × 300), budżet 6160 z 6500 części. Każdy z 12 budynków ma tu kartę z wymiarami — budowniczy buduje swój w osobnym pliku, generator miasta stawia je w miejscach z tabeli.

Pliki obok: `paleta.py` (45 kolorów + funkcja `cien`), `uklad.json` (wszystkie współrzędne z rozdz. 4 do odczytu maszynowego), `ujecia.json` (ujęcia kontrolne z rozdz. 7). Geometria układu sprawdzona skryptem `noc/mapa/sprawdz_uklad.py` (folder roboczy sesji): 0 kolizji obrysów, 0 kolizji z ulicami, każdy front patrzy na rynek albo ulicę, dojścia ≤ 8,8 s. Makieta z prostopadłościanów wyrenderowana z ujęć z rozdz. 7 — kadry są takie, jak opisano.

---

## 1. Idea i przykazania stylu

**Idea w trzech zdaniach.** Miasteczko wygląda, jakby zbudowało je wesołe dziecko z klocków, które nie do końca pasują: każdy dom się kłania, przechyla albo puchnie, a mimo to wszystko stoi — i to jest żart, na którym opiera się cały świat. Bryłę rysuje kolor i gruby „tusz” z ciemnych klocków, a nie światło, bo w Roblox Studio cień bywa płaski albo go nie ma. Zamiast napisów każde miejsce mówi wielkim rekwizytem: kocioł z parą to gospoda, miecz w dachu to zbrojownia, wykluwające się jajo to wylęgarnia.

**Konwencje.** 1 jednostka = 1 stud; Y w górę; północ = −Z. Obrót części `(rx, ry, rz)` jak w `scena.py`: **rz > 0 = góra ucieka w lewo** patrząc na front (ku −X), **rz < 0 = w prawo**; rx > 0 = góra ucieka do przodu (ku +Z); ry = skręt wokół pionu. „Pochylenie +” w kartach = rz > 0.

| # | Przykazanie | Liczby |
|---|---|---|
| 1 | **Zero kąta prostego w sylwetce.** Każda kondygnacja nad parterem jest pochylona albo skręcona. | ściany i kondygnacje 5–8°; kominy, wieżyczki, słupy ozdobne 8–12°; jeden akcent na budynek do 15°; skręt pięter (ry) 4–8°. **Zakaz 1–3°** (wygląda jak błąd) |
| 2 | **Kontra.** Sąsiednie kondygnacje w przeciwne strony, skręty naprzemiennie. | np. piętro rz +6°, dach rz −4°; wierzchołek ≤ 3 od osi podstawy |
| 3 | **Prosty dół.** Dolne 10 studów ściany przy ziemi jest pionowe — po ścianie odchylonej do tyłu postać wejdzie (zbocze do 89°). Krzywiznę parteru robi tylko skręt ry, schodek i przewieszenie (klin „nawis”). | parter 0–12 bez rx/rz; podłogi, progi, schody, podesty 0° (±0,2) |
| 4 | **Głowa większa od nóg.** Piętro szersze od parteru, wysunięte nierówno. | nawis z frontu 2–3,5, z boków 0,5–2; parter 11–12, piętro 0,7–0,8 parteru, poddasze 0,5–0,6 |
| 5 | **Dach jak czapa.** | 45–60% wysokości budynku (przysadziste od 40%); okap 2,5–3,5 poza lico; wysunięcie nad szczytem 2–3; grubość połaci 1,5–2; kalenica przesunięta 60/40 → połacie różnią się o ≥ 10°; zwykły 45–55°, przysadzisty 30–40°, smukły 60–70° |
| 6 | **Kolor dachu = kod funkcji.** Każdy typ ma własny klucz `dach_*` (rozdz. 2), powtórzony na szyldzie i chorągiewce. Ciemne dachy (`dach_zbrojownia`, `dach_twierdza`, `dach_gildia`, `dach_sklep`, `dach_arena`, `dach_dom_lupek`) dostają **jasną** kalenicę i deski czołowe (`zloto` albo `biel`). | żadnego niebieskiego bez jasnego obrysu |
| 7 | **Rekwizyt-szyld zamiast napisu.** Jeden żart + najwyżej 2 małe echa. Zero liter, cyfr, logotypów. | wysokość 8–12 (kiosk ≥ 6); szerokość 35–55% fasady; środek 12–20 nad ziemią, dół ≥ 9; pochylony 10–15° ku rynkowi i 5–10° w bok; ≥ 25% poza obrysem bryły |
| 8 | **Tusz trzech grubości (4 : 2 : 1)**, kolor `tusz`, SmoothPlastic. Tylko sylwetka i granice kolorów, nie każda krawędź. | sylwetka 1,2–1,5 (narożniki, cokół, deski czołowe, kalenica); średnie 0,6–0,8 (ramy otworów, belka stropowa, płetwa szyldu); detal 0,3; wysunięcie 0,3–0,5 poza lico, **nigdy w tej samej płaszczyźnie** (min. 0,05, zalecane 0,1); tusz + ciemne drewno = 12–20% widoku frontu |
| 9 | **Podkładka pod jasną formę** (szyld, klocek, tarcza): kopia kształtu w tuszu za formą. | większa o 0,5 z każdej strony, grub. 0,4, cofnięta 0,2–0,3; koło → walec Ø +1 |
| 10 | **3 barwy + akcent + tusz** na budynek. | ściana ≈ 60%, dach ≈ 30%, akcent ≤ 10%; najwyżej 5–6 kolorów; SmoothPlastic ≥ 80% części |
| 11 | **Trzy walory zamiast cienia.** Ciemny cokół, jasna ściana, nasycony dach. | cokół L\* 30–45; ściana jasna L\* ≥ 78 (wyjątki z ciemną ścianą i jasnym dachem: stajnia, brama lochów); dach nasycony; ściana i dach różnią się o ≥ 30 L\*; stykające się duże płaszczyzny ≥ 3 : 1; pas „cienia z klocka” pod okapem i nawisem: `cien(ściana)` (×0,82), wys. 1–1,5 |
| 12 | **Asymetria.** Żadnej lustrzanej fasady, żadnych dwóch takich samych okien. | połowy fasady różnią się ≥ 3 cechami; drzwi przesunięte o 15–25% szerokości fasady od osi; 3–5 okien frontu (4 × 5, 3 × 4, okrągłe Ø 3), każde obrócone o 4–8°; jedna okiennica zwisa 10–15° |
| 13 | **Detal tam, gdzie stoi gracz.** | ≥ 60% fasady gładkie; 60% detalu w pasie 0–14 nad ziemią przy wejściu; rekwizyty ×1,25–1,5 wielkości realnej, w trójkach duży–średni–mały, przechył 5–12°; nic cieńszego niż 0,3 (poza szwami łat) |
| 14 | **Światło z Neonu, nie z lamp.** | Neon tylko w oknach, latarniach, magii i żarze: 3–10 części na budynek, ≤ 3% powierzchni, wyłącznie klucze `neon_*`; szyba = Neon w ramie, nie szkło |
| 15 | **Znaki miasteczka na każdym budynku.** | 1–3 „wypadnięte klocki” (wnęka 2 × 2 × 0,5 w tuszu + ten sam klocek na ziemi obok, obrót 15–30°); 2–4 łaty z fastrygą (prostokąt 2–3 w kolorze akcentu + 4–6 szwów `tusz` 0,3 × 0,8); 1–2 chorągiewki duetu (kliny 2 × 3: `dach_twierdza` = Rycerz, `pomarancz` z `dach_sklep` = Kot-Mag), przechył 10–15° |

**Kolejność pracy nad bryłą:** bryły w jednym kolorze (test czarnej sylwetki: rozpoznasz ze 100 studów?) → kolory ról → krzywizna → tusz → otwory → rekwizyt → znaki miasteczka.

---

## 2. Paleta

Plik `paleta.py` w tym folderze: słownik `PALETA` (45 kluczy) i funkcja `cien(s, klucz, f=0.82)` → ciemniejszy wariant jako `RRGGBB` (pas pod okapem, połać odwrócona od rynku, ton „co drugi segment”). **Innych kolorów nie używamy.** L\* = walor (jasność postrzegana 0–100).

| Klucz | RRGGBB | L\* | Zastosowanie |
|---|---|---|---|
| `tusz` | `1D1916` | 9 | obrys sylwetki i granic kolorów, ramy otworów, kalenice jasnych dachów, krawężniki, źrenice |
| `tynk_krem` | `FFE6A8` | 92 | ściany karczmy, domy; najjaśniejsza ściana miasta |
| `tynk_brzoskwinia` | `FFCBA8` | 85 | domy, wnętrza łuków i podcieni |
| `tynk_mieta` | `BDF0CB` | 91 | domy |
| `tynk_lawenda` | `DCCBFF` | 85 | ściany sklepu magicznego, domy |
| `tynk_blekit` | `C5D3F7` | 85 | ściany gildii, domy; ostrza i stal (zamiast materiału Metal); spód chmur |
| `drewno_ciemne` | `5C3A22` | 28 | ściany stajni, słupy, skrzydła drzwi, kakao |
| `drewno` | `8B5A2E` | 43 | deski, beczki, skrzynie, płoty, pnie, dachy domów z gontu |
| `drewno_jasne` | `D49A5A` | 68 | tablica zleceń, lady, pomosty, pieczone jedzenie; jasny obrys na ciemnym drewnie |
| `kamien_cieply` | `D6C6AC` | 81 | mur miejski, zbrojownia, arena, twierdza, brama miejska, studnia; jasny obrys na kamieniu lochów |
| `kamien_cokol` | `6B5848` | 39 | cokoły, podium karczmy, schody (ciemny walor przy ziemi) |
| `kamien_lochu` | `4A4560` | 31 | brama lochów, niecka, skały przy niej |
| `dach_karczma` | `D8452E` | 51 | dach karczmy i jej akcenty (kod: gospoda) |
| `dach_zbrojownia` | `3F4E6E` | 33 | dach zbrojowni, tarcza; zawsze z jasną kalenicą `zloto` (kod: oręż) |
| `dach_sklep` | `7B4FB5` | 43 | kapelusz-dach sklepu, szata Kota-Maga (kod: magia) |
| `dach_wylegarnia` | `1C9886` | 57 | kapsel i kropki jaja, drzwi wylęgarni (kod: pety) |
| `dach_stajnia` | `E2A93A` | 73 | strzecha stajni, słoma, siano (kod: wierzchowce) |
| `dach_arena` | `B8283A` | 41 | kolce, pasy i pióropusz areny, z `biel` (kod: walka) |
| `dach_gildia` | `1E6E43` | 41 | dach i sztandar gildii, z kalenicą `zloto` (kod: gildia) |
| `dach_lochy` | `7FBF3F` | 71 | mech i matowe kryształy bramy lochów (kod: lochy) |
| `dach_kolo` | `D93A8C` | 51 | koło fortuny, markiza kiosku, język paszczy (kod: koło) |
| `dach_twierdza` | `2659B3` | 39 | chorągwie i pasy bramy twierdzy = tabard Rycerza; z jasnym obrysem (kod: twierdza) |
| `dach_brama` | `B84A18` | 46 | dachy wież i ganku bramy miejskiej (kod: brama) |
| `dach_dom_ceglasty` | `A04E2C` | 43 | dachy domów — nie przy bramie miejskiej |
| `dach_dom_lupek` | `5E5A78` | 40 | dachy domów, z jasną kalenicą |
| `trawa` | `6DB33F` | 66 | grunt i trawniki (≤ 30% planu wewnątrz muru) |
| `lisc_jasny` | `A8D84E` | 81 | górna część koron, krzaki w słońcu, nać, sałata |
| `lisc` | `72BF3A` | 70 | środek koron, krzaki |
| `lisc_ciemny` | `3F8F35` | 53 | dół koron, żywopłoty |
| `igla` | `2F8A55` | 51 | drzewa iglaste w tle |
| `bruk` | `E0C48E` | 80 | rynek, ulica Bramna, wierzch podium |
| `bruk_ciemny` | `C9A66A` | 70 | drugi ton bruku, ulice boczne, wzór rynku |
| `ziemia` | `C08A55` | 62 | Podmurna, podwórka, grządki, padok |
| `woda` | `2389D0` | 55 | tafla stawu i studni |
| `woda_gleboka` | `17589A` | 37 | toń i brzeg wewnętrzny wody |
| `zloto` | `F2B030` | 76 | okucia, klucze, gwiazdy, klocek pomnika, jasna kalenica ciemnych dachów |
| `czerwien` | `E5392B` | 52 | pinezki, jabłka, drobne akcenty (nie duże płaszczyzny) |
| `pomarancz` | `F08A24` | 67 | ogon Kota, marchew, dynie, łapka wylęgarni, chorągiewka duetu |
| `biel` | `FFF6E0` | 97 | skorupa jaja, para i dym, chmury, bliki, zęby, kości, pasy areny |
| `metal_ciemny` | `4A5368` | 35 | kowadło, kocioł, łańcuchy, ciężkie okucia |
| `neon_okno` | `FFB030` | 78 | okna, latarnie, złoty portal twierdzy (Neon) |
| `neon_ogien` | `FF6A1A` | 63 | palenisko kuźni, iskry (Neon) |
| `neon_magia` | `B85CFF` | 57 | okna i kryształ sklepu magicznego (Neon) |
| `neon_portal` | `6CFF3A` | 89 | gardziel bramy lochów, największy kryształ (Neon) |
| `neon_slime` | `2FF0E0` | 86 | pet-slime, okna wylęgarni (Neon) |

Zasady przyjęte przy doborze: kolory o 10–20 pkt bardziej nasycone niż docelowe (Studio zjada 20–38% nasycenia i przesuwa ku błękitowi); zielenie przesunięte w ciepłą stronę (odcień 81–113°, nasycenie ≥ 63%) i jaśniejsze niż w v1; żadnej dużej płaszczyzny szarej (nasycenie ≥ 20%); niebieskie i ciemne dachy wyłącznie z jasnym obrysem.

**Kontrast stykających się dużych płaszczyzn** (WCAG, wymagane ≥ 3 : 1):

| Para | Gdzie | Kontrast |
|---|---|---|
| `tynk_krem` / `dach_karczma` | karczma | 3,6 : 1 |
| `kamien_cieply` / `dach_zbrojownia` | zbrojownia | 5,0 : 1 |
| `tynk_lawenda` / `dach_sklep` | sklep magiczny | 3,9 : 1 |
| `biel` / `dach_wylegarnia` | wylęgarnia | 3,3 : 1 |
| `drewno_ciemne` / `dach_stajnia` | stajnia | 4,8 : 1 |
| `kamien_cieply` / `dach_arena` | arena | 3,7 : 1 |
| `tynk_blekit` / `dach_gildia` | gildia | 4,2 : 1 |
| `kamien_lochu` / `dach_lochy` | brama lochów | 4,1 : 1 |
| `biel` / `dach_kolo` | koło fortuny | 4,0 : 1 |
| `kamien_cieply` / `dach_twierdza` | brama twierdzy | 4,0 : 1 |
| `kamien_cieply` / `dach_brama`; `tynk_krem` / `dach_brama` | brama miejska | 3,1 : 1; 4,3 : 1 |
| `tynk_lawenda`, `tynk_blekit`, `tynk_mieta` / `dach_dom_ceglasty` | domy | 3,9; 3,9; 4,6 : 1 |
| `tynk_brzoskwinia`, `tynk_krem` / `dach_dom_lupek`; `tynk_brzoskwinia` / `drewno` | domy | 4,5; 5,3; 4,0 : 1 |
| `tynk_krem` / `kamien_cokol`; `kamien_cieply` / `kamien_cokol`; `bruk` / `kamien_cokol` | ściana–cokół–bruk | 5,5; 4,0; 4,0 : 1 |
| `dach_zbrojownia` / `zloto`; `dach_gildia` / `zloto`; `dach_twierdza` / `zloto` | jasna kalenica | 4,4; 3,3; 3,5 : 1 |
| `kamien_lochu` / `kamien_cieply`; `drewno_ciemne` / `drewno_jasne` | jasny obrys | 5,4; 4,1 : 1 |

**Pary za słabe — obowiązkowe obejścia:** `bruk` / `trawa` 1,5 : 1 → krawężnik `tusz` 0,6 × 0,35 na każdej granicy; `trawa` / `woda` 1,5 : 1 → brzeg `kamien_cieply` + pas `woda_gleboka` (4,3 : 1); `kamien_lochu` / `tusz` 1,9 : 1, `drewno_ciemne` / `tusz` 1,7 : 1, `dach_zbrojownia` / `tusz` 2,1 : 1 → na tych kolorach obrys robimy **jasny** (`kamien_cieply`, `drewno_jasne`, `zloto`); `pomarancz` / `tynk_lawenda` 1,7 : 1 → ogon kota z podkładką `tusz`. Jasne dachy (`dach_stajnia`, `dach_lochy`) na tle bladego horyzontu (1,4 : 1) → kalenica i spód okapu w `tusz`.

**Materiały dozwolone** (na całej mapie najwyżej 7):

| Materiał | Gdzie | Limit |
|---|---|---|
| SmoothPlastic | wszystko domyślnie, także tusz, liście, trawa, bruk, woda | ≥ 80% części budynku |
| WoodPlanks | skrzydła drzwi, podesty, skrzynie, tablica zleceń, ściany stajni | ≤ 10% części |
| Wood | pnie, słupy i belki w kolorach `drewno*` (nigdy na tuszu) | ≤ 10% |
| Brick | tylko kominy | ≤ 10 części na budynek |
| Cobblestone | cokoły, cembrowina studni, ściany podium | ≤ 10% |
| Fabric | markizy, chorągwie, sztandary, pasy areny | — |
| Neon | tylko klucze `neon_*` | ≤ 10 części i ≤ 3% powierzchni budynku |
| Slate | tylko skały i głazy (generator, skała za bramą lochów) | — |

**Zakazane:** Metal, Glass, Plastic, Ground, Grass na czymkolwiek poza próbą gruntu w Studio, Foil, Ice, siatki, unie, tekstury, naklejki, `Highlight` w budynkach. Przezroczystość: tylko para i dym, najwyżej 3 części na budynek, alfa ≤ 0,3 (lepiej 0 — pełne białe kule też czytają się jak para).

---

## 3. Skala i wymiary

| Element | Wartość |
|---|---|
| Postać gracza | 5 (R15 ok. 5,3; awatary 5–6,5); szerokość z rękami ok. 4 |
| Chód / skok | 16 studs/s / 7,2 (zasięg w poziomie ok. 8,7) |
| Kamera | 12,5 za postacią, pole widzenia 70° w pionie (≈ 102° w poziomie przy 16 : 9) |
| Wejście budynku głównego | otwór ≥ 8 × 10 (zalecane 8 × 11); dom 6 × 8 |
| Miejsce na interakcję | prostokąt 8 × 8 przed wejściem bez przeszkód wyższych niż 0,5; w nim część „Punkt interakcji” |
| Parter | 11–12 wys., ściany 0–10 pionowe (przykazanie 3) |
| Piętro / poddasze | 0,7–0,8 / 0,5–0,6 wysokości parteru |
| Okno | 3 × 4 do 4 × 5, okrągłe Ø 3; rama 0,7; parapet 0,6 wysunięty 0,8 |
| Stopień schodów | wys. 0,5–1, głęb. 1,5–2, szer. ≥ 6 |
| Rampa | zalecane 1 : 4 (14°), najwyżej 1 : 2 (26,6°) |
| Ulica główna (Bramna) / boczne (5 szprych) / Podmurna / zaułek | 16 / 12 / 10 / ≥ 8 |
| Prześwit nad drogą | ≥ 14 w bramie miejskiej; ≥ 12 w pozostałych bramach; łuk najwyżej 6 głęboki |
| Rynek | 5870 studs² (obwiednia 97 × 87) na 16–20 graczy |
| Hierarchia wysokości (nad bruk rynku) | dominanta: karczma 50 + 4 podium = 54; rząd 2: sklep 42, gildia 40, brama lochów 36, brama twierdzy 36; rząd 3: arena 34, zbrojownia 30, wylęgarnia 28, brama miejska 27, koło 25, studnia 22, stajnia 20; domy 22–28; drzewa w mieście ≤ 15; stragany 10 |
| Sąsiedzi | różnica wysokości ≥ 20%, inny kształt bazowy, przeciwne pochylenie |
| Przeszkody | ≤ 6 (do przeskoczenia) albo ≥ 10 (bariera); **nic 6,5–9** („prawie się da” frustruje); rekwizyt z kolizją na ścieżce albo ≥ 2,5, albo bez kolizji |
| Rekwizyty | ×1,25–1,5 wielkości realnej; szyld 8–12 |
| Detal | najmniejsza część 0,3 (szwy łat 0,3 × 0,8 to wyjątek, min. 0,2); obrys sylwetki 1,2–1,5 |
| Odstęp płaszczyzn różnych kolorów | ≥ 0,1 (minimum 0,05 — liczone po skalowaniu) |

---

## 4. Układ miasta — układ A (promienisty rynek) dopasowany do słońca

### 4.1 Zasada

Słońce świeci z północnego zachodu (wektor ku słońcu −0,558; 0,728; −0,399), więc oświetlone są ściany zwrócone na −X i −Z. Budynek, którego front patrzy na środek rynku, ma front w słońcu, gdy stoi na wschód lub południe od rynku. Tam stoją wszystkie miejsca pętli i dominanta, a ich cienie padają **poza** rynek (cień = 0,94 × wysokość, ku południowemu wschodowi). Po zachodniej i północnej stronie stoją miejsca rzadziej odwiedzane: stajnia, gildia, arena, brama miejska — niskie albo daleko (ich cień nie sięga rynku), o jasnych ścianach.

Gracz pojawia się na rynku, 28 studów na południowy wschód od studni-pomnika, **plecami do studni i do słońca**, i patrzy na wschód-południowy wschód (`obrot_y` spojrzenia 58°). W pierwszym kadrze ma na wprost karczmę z tablicą zleceń, po lewej w głębi ulicy świecącą bramę lochów i zbrojownię z kuźnią, po prawej wylęgarnię — wszystkie fronty w słońcu. Szprychy (5 ulic) kończą się „kamieniami milowymi” i miejscami „wkrótce”; półpierścień Podmurnej spina końce szprych i biegnie za karczmą.

Rynek w cieniu budynków: 19% pola (głównie cień studni i koła). Plan: `noc/mapa/projekt/plan.png`, makieta: `noc/mapa/projekt/render_makieta/` (folder roboczy sesji).

### 4.2 Obiekty główne (12 budowniczych)

Współrzędne w układzie miasta: środek rynku (0; 0), poziom bruku y = 0. **Obrys = działka maksymalna** (szer. wzdłuż lokalnego X × głęb. wzdłuż lokalnego Z, środek na (0; 0) lokalnie, front +Z). `y podstawy` = poziom, na którym generator stawia lokalne y = 0 budynku. Światło frontu: 0,69 = pełne słońce, 0 = światło ślizgowe, < 0 = cień. Dojście = najkrótsza droga piesza z punktu wejścia (Dijkstra na siatce 1 stud, z omijaniem działek) do punktu interakcji.

| id | nazwa_grupy | Tytuł | Rola w pętli (propozycja) | (x; z) | obrot_y | szer × gł | wys. | y podstawy | budżet | punkt interakcji (x; z) | światło frontu | dojście |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `karczma` | Karczma | Gospoda Pod Pękatym Kotłem | serce pętli: tablica zleceń → wybór strefy → walka; powrót z łupem | (70,5; 59,1) | −130 | 46 × 38 | 50 | +4 (podium) | 470 | przed drzwiami (59,7; 57,9) i przed tablicą (64,5; 39,7), na podium | 0,68 | 4,2 s |
| `zbrojownia` | Zbrojownia | Zbrojownia z kuźnią | wydawanie łupu: broń, zbroja, ulepszenia | (57,7; −6,1) | −74 | 32 × 26 | 30 | 0 | 320 | (42,5; 2,4) | 0,43 | 2,2 s |
| `sklep_magiczny` | SklepMagiczny | Sklep magiczny | sklep 6 slotów, odświeżanie co 5 min | (38,9; −40,3) | −56 | 24 × 24 | 42 | 0 | 290 | (24,0; −33,8) | 0,24 | 4,0 s |
| `wylegarnia` | Wylegarnia | Wylęgarnia petów | jaja i pety (slot równoległy); pierwsze jajo w samouczku | (16,0; 55,8) | −172 | 30 × 28 | 28 | 0 | 300 | (18,4; 37,3) | 0,47 | 1,7 s |
| `brama_lochow` | BramaLochow | Brama lochów | loch: 10 przeciwników + boss — kamień milowy | (109,6; 23,3) | −102 | 30 × 20 | 36 | −4 (niecka) | 290 | (95,9; 20,4) | 0,63 | 5,1 s |
| `stajnia` | Stajnia | Stajnia wierzchowców | wierzchowce: kolekcja i prestiż | (−45,7; 35,7) | 128 | 38 × 22 | 20 | 0 | 270 | (−29,0; 32,8) | −0,19 | 4,1 s |
| `brama_twierdzy` | BramaTwierdzy | Brama do twierdzy gracza | wejście na własną działkę (dochód na sekundę) | (−34,0; 104,6) | 162 | 32 × 18 | 36 | 0 | 280 | (−30,0; 92,2) | 0,21 | 6,3 s |
| `gildia` | Gildia | Siedziba gildii (wkrótce) | zapowiedź gildii i rajdów — zamknięta | (−105,4; −11,1) | 84 | 28 × 28 | 40 | 0 | 280 | (−87,3; −11,2) | −0,60 | 8,1 s |
| `arena` | Arena | Arena (wkrótce) | zapowiedź pojedynków — zamknięta | (18,4; −104,4) | −10 | 48 × 32 | 34 | 0 | 330 | (14,9; −84,7) | −0,30 | 7,2 s |
| `brama_miejska` | BramaMiejska | Brama miejska z murem | krawędź świata; w przyszłości wyjście do krain | (−74,9; −83,2) | 42 | 46 × 14 | 27 | 0 | 250 | (−67,5; −75,0) | −0,67 | 8,8 s |
| `studnia_pomnik` | StudniaPomnik | Studnia-pomnik Pierwszego Klocka | środek i punkt orientacyjny; codzienna nagroda | (0,0; 0,0) | 50 | 18 × 18 | 22 | 0 | 150 | (10,0; 8,4) | (bez znaczenia) | 1,2 s |
| `kolo_fortuny` | KoloFortuny | Koło fortuny | darmowe spiny (czas, aktywność), bez płatnej losowości | (−12,6; 28,3) | 156 | 18 × 14 | 25 | 0 | 170 | (−8,1; 18,3) | 0,14 | 1,9 s |

Budżet budynków głównych: **3400** (limit 3600; 200 rezerwy). Punkty interakcji leżą 4 study przed krawędzią działki (karczma: przed drzwiami i przed tablicą, na podium); lokalne współrzędne podają karty. Najdłuższe dojście: brama miejska 8,8 s (limit 12 s).

**Pochylenia sąsiadów** (rz głównych pięter, naprzemiennie dookoła rynku): wylęgarnia −, karczma +, zbrojownia −, sklep +, gildia −, stajnia +, koło −. Bramy (lochy, arena, brama miejska, twierdza) mają dwa filary/baszty pochylone w przeciwne strony.

### 4.3 Obiekty generatora miasta

Generator (`generuj.py`, osobne zadanie) stawia budynki główne przez `with s.uklad(pos=(x, y_podstawy, z), obrot=(0, obrot_y, 0), grupa=nazwa_grupy): modul.buduj(s, rnd)` i dobudowuje wszystko z tej tabeli.

| id | nazwa_grupy | Co | Położenie (x; z) | obrot_y | Wymiary | Wys. | Budżet |
|---|---|---|---|---|---|---|---|
| `teren` | Teren | płyta gruntu `trawa` 440 × 440, wierzch y = 0, rozcięta wokół niecki lochów; podwórka `ziemia` | środek (0; 0) | 0 | 440 × 440 × 2 | 0 | 6 |
| `rynek` | Rynek | bruk w 3 tonach (`bruk`, `bruk_ciemny`, `cien(bruk)`) z płyt 4–8, wierzch y = 0,2; krawężnik `tusz`; „ścieżki-kody” | wielokąt 4.4 | — | 5870 studs² | 0,2 | 170 |
| `ulice` | Ulice | 6 łamanych z 4.5, wierzch y = 0,15 (Podmurna 0,1); krawężnik `tusz`; co 8 studów kamień 1 × 0,4 × 1 w kolorze kodu celu | 4.5 | — | szer. 16 / 12 / 10 | 0,15 | 120 |
| `podium_karczmy` | Teren/Podium | podium całej działki karczmy, ściany `kamien_cokol` (Cobblestone) z rantem `tusz`, wierzch `bruk`; schody 28 szer., 5 stopni 0,8 × 2, lokalnie z +19…+29, środek x = −3 (świat: środek schodów (54,0; 41,4)) | jak karczma | −130 | 46 × 38 + schody 28 × 10 | 4 | 25 |
| `niecka_lochow` | Teren/Niecka | dno y = −4 (`kamien_lochu`, 3 pęknięcia `neon_portal` 0,3), lokalnie w układzie bramy lochów x ±16, z −10…+18; ściany oporowe z rantem `kamien_cieply`; rampa 12 szer. z lokalnego z +18 (−4) do +34 (0) = świat (92,0; 19,6) → (76,3; 16,2); skała za murem: 6 brył `kamien_lochu` (Slate) 20–30 wys. | (105,7; 22,5) | −102 | 32 × 28 + rampa 12 × 16 | −4 | 35 |
| `staw` | Staw | Staw Kaczy: warstwy wg `przepisy.md` 4.8 (brzeg `woda_gleboka` → tafla `woda` → bliki `biel`), 8 kamieni `kamien_cieply`, pomost 2 × 6, 3 kaczki z klocków | (−9,1; 74,4) | 0 | Ø 15 | 0,4 | 15 |
| `mur` | Mur | wzorzec: korpus 4 grub. × 14 wys. `kamien_cieply`, skarpa-klin u stopy 1,2 × 3 `kamien_cokol`, rant `tusz` 0,6 na 14, blanki 2 × 2 co 2 (co drugi +0,3 i `cien`) → razem 16; przerwy tylko w obiektach wbudowanych (brama miejska, gildia, arena, brama twierdzy, brama lochów — ich tył stoi przy murze) | wielokąt 4.6 | — | obwód 778, ok. 580 do zbudowania | 16 | 220 |
| `baszty` | Mur/Baszty | 8 baszt Ø 12 (3 walce zwężane, gzymsy `tusz`), blanki, bez dachu, chorągiewka duetu, przechył ±4° naprzemiennie | (−17; −121), (−97; −70), (−118; 21), (−67; 100), (31; 126), (97; 101), (122; −4), (88; −79) | — | Ø 12 | 24 | 110 |
| `domy` | Domy | 9 domów z wzorca (rozdz. 6), tabela 4.7 | 4.7 | 4.7 | 14–16 × 12–16 | 22–28 | 720 |
| `stragany` | Stragany | 5 straganów (rozdz. 6), lada ku środkowi rynku | 4.7 | 4.7 | 10 × 7 | 10 | 120 |
| `zielen` | Zielen | 6 stref (4.8): ≤ 14 drzew w mieście (≤ 15 wys.), 24 krzaki, ogródki, kwiaty tylko przy wejściach | 4.8 | — | — | ≤ 15 | 260 |
| `tlo` | Tlo | pierścień zasłaniający horyzont: 16 wzgórz-kul (R 45–60, środki r 165–200, wierzchołki 24–45 nad y = 0, kolory `lisc_ciemny`/`igla`/`trawa`, 4 z jaśniejszą czapą `lisc_jasny`), 36 iglaków i 12 drzew w pasie r 130–165; bez kolizji | pierścień r 130–200 | — | — | 24–45 | 380 |
| `chmury` | Chmury | 10 chmur (rozdz. 6), bez kolizji i cienia | r 60–200, y 110–150 | — | 24 × 15 | — | 50 |
| `rekwizyty` | Rekwizyty | 22 latarnie (co 14 studów wzdłuż szprych, naprzemiennie; 8 na brzegu rynku), 30 beczek/skrzyń/siana w trójkach, 8 ławek przy studni i stawie, 10 chorągwi w kolorach kodów u wylotów szprych, 16 przęseł płotu, 12 kamieni, 10 „wypadniętych klocków” | wg reguł 4.9 | — | — | ≤ 10 | 530 |
| `spawn` | Spawn | `SpawnLocation` 6 × 1 × 6 bez naklejki, `Orientation` (0; −122; 0) — postać patrzy w kierunku (0,848; 0,530) = `obrot_y` 58° | (21,4; 18,0) | spojrzenie 58 | 6 × 6 | 1 | 1 |

**Budżet całości:** budynki główne 3400 + generator 2762 = **6162** (limit 6500). Sufity: kule ≤ 150, walce ≤ 600, Neon ≤ 150, części przezroczyste ≤ 10, części z kolizją ≤ 40%, części bez cienia ≥ 40%.

**W świecie Studio** całe miasto jest przesunięte o (0; 0; −700): punkt wejścia = (21,4; 0; −682,0). Czy wyłączyć dotychczasowy `SpawnLocation` — decyzja człowieka (to cudza instancja).

### 4.4 Rynek

Wielokąt bruku (x; z), kolejno od południa przez wschód, północ i zachód: (−7; 39), (3; 41), (15; 38), (25; 35), (33; 45), (41; 49), (50; 42), (55; 32), (50; 24), (39; 18), (41; 10), (44; 5), (44; −5), (40; −14), (35; −24), (30; −31), (24; −36), (16; −36), (8; −38), (−4; −38), (−16; −36), (−25; −28), (−34; −20), (−39; −8), (−42; 4), (−40; 18), (−34; 28), (−30; 33), (−24; 35), (−15; 38). Wypustka (33; 45)–(55; 32) to przedpole karczmy aż do stóp jej schodów.

**Ścieżki-kody** (orientacja bez napisów): od cembrowiny studni (r = 10) do wylotu każdej szprychy biegnie przerywany pas 2 szer. (odcinki 4, przerwy 2, wierzch y = 0,3) w kolorze kodu celu: Lochowa `dach_lochy`, Twierdzowa `dach_twierdza`, Gildyjna `dach_gildia`, Arenowa `dach_arena`, Bramna `dach_brama`, do schodów karczmy `dach_karczma`. W 3-studowym promieniu od punktu wejścia nic poza płytą `SpawnLocation`.

### 4.5 Ulice

| id | Nazwa | Szer. | Łamana (x; z) | Nawierzchnia | Długość |
|---|---|---|---|---|---|
| `bramna` | Bramna (główna) | 16 | (−25; −28) → (−43; −42) → (−54; −62) → (−70; −77) | `bruk` | 67 |
| `lochowa` | Lochowa | 12 | (37; 15) → (57; 20) → (76,3; 16,2) — dalej **rampa** w dół do (92,0; 19,6) na y = −4 i dno niecki do (99,8; 21,2) | `bruk_ciemny`, niecka `kamien_lochu` | 64 |
| `twierdzowa` | Twierdzowa | 12 | (−14; 38) → (−24; 57) → (−27; 78) → (−31; 95) | `bruk_ciemny` | 61 |
| `gildyjna` | Gildyjna | 12 | (−38; −5) → (−62; −4) → (−79; −10) → (−90; −10) | `bruk_ciemny` | 54 |
| `arenowa` | Arenowa | 12 | (7; −37) → (16; −58) → (13; −75) → (16; −88) | `bruk_ciemny` | 52 |
| `podmurna` | Podmurna (półpierścień) | 10 | (78; 10) → (86; −3) → (78; −32) → (63; −57) → (39; −73) → (14; −81) → (−15; −83) → (−43; −74) → (−60; −67) → (−71; −44) → (−80; −26) → (−86; −9) → (−81; 11) → (−74; 39) → (−57; 67) → (−40; 83) → (−29; 89) → (−9; 88) → (15; 87) → (35; 87) → (58; 100) → (82; 91) → (100; 72) → (112; 52) → (97; 43) → (78; 25) | `ziemia` | 597 (37 s) |

Podmurna łączy końce szprych (pętla bez ślepych zaułków) i obchodzi karczmę od tyłu, między nią a murem; oba jej końce dochodzą do Lochowej przy górnym końcu rampy (76; 16), więc nigdzie nie trzeba zeskakiwać do niecki.

### 4.6 Teren, woda, mur

- **Poziomy:** rynek i ulice 0 (bruk 0,15–0,2 nad gruntem); podium karczmy +4 (schody 5 × 0,8); niecka bramy lochów −4 (rampa 1 : 4). Główna pętla rynek → tablica → zbrojownia → wylęgarnia jest płaska poza schodami karczmy.
- **Zieleń ≤ 30%** powierzchni wewnątrz muru (kontrola w ujęciu `u03_mapa_gora`): reszta to bruk, ziemia podwórek i ogródków, dachy.
- **Mur** (linia środka, zamknięta): (−62; −107), (−81; −90), (−97; −70), (−111; −40), (−121; −13), (−118; 21), (−98; 66), (−67; 100), (−37; 115), (−8; 122), (31; 126), (68; 118), (97; 101), (120; 69), (122; 40), (122; 22), (122; −4), (109; −44), (88; −79), (61; −106), (22; −122), (−17; −121). Obwiednia 243 × 248. Mur zasłania płytę bazową; poza nim tylko tło (4.3 `tlo`).
- **Woda:** Staw Kaczy (4.3). Woda w studni (karta studni). Bez strumieni.

### 4.7 Domy i stragany

| id | (x; z) | obrot_y | szer × gł | wys. | ściana | dach | front na |
|---|---|---|---|---|---|---|---|
| `dom_1` | (100,5; −17,7) | −80 | 16 × 14 | 26 | `tynk_brzoskwinia` | `dach_dom_lupek` | Podmurna |
| `dom_2` | (84,8; −53,0) | −58 | 16 × 14 | 24 | `tynk_mieta` | `dach_dom_ceglasty` | Podmurna |
| `dom_3` | (60,2; −79,9) | −37 | 16 × 14 | 28 | `tynk_krem` | `dach_dom_lupek` | Podmurna |
| `dom_4` | (−25,9; −96,6) | 15 | 16 × 14 | 26 | `tynk_lawenda` | `drewno` | Podmurna |
| `dom_5` | (−89,1; −45,4) | 63 | 14 × 14 | 22 | `tynk_mieta` | `dach_dom_lupek` | Podmurna |
| `dom_6` | (−95,1; 30,9) | 108 | 16 × 14 | 24 | `tynk_blekit` | `dach_dom_ceglasty` | Podmurna |
| `dom_7` | (−70,7; 70,7) | 135 | 16 × 14 | 26 | `tynk_lawenda` | `dach_dom_ceglasty` | Podmurna |
| `dom_8` | (10,5; 99,5) | −174 | 16 × 16 | 24 | `tynk_brzoskwinia` | `drewno` | Podmurna |
| `dom_9` | (−67,5; 8,3) | 180 | 14 × 12 | 22 | `tynk_krem` | `dach_dom_ceglasty` | Gildyjna |

Domy są pastelowe, bez Neonu poza 1–2 oknami, pochylenia naprzemiennie (dom_1 +, dom_2 −, …), żadne dwa z tymi samymi parametrami (skręt, nawis, strona komina, wysokość).

| id | (x; z) | obrot_y | Towar (kolor markizy) |
|---|---|---|---|
| `stragan_1` | (−26,7; −19,4) | 54 | jabłka i dynie (`dach_karczma` / `biel`) |
| `stragan_2` | (5,9; −33,5) | −10 | chleby i ser (`dach_stajnia` / `biel`) |
| `stragan_3` | (21,5; −27,6) | −38 | kryształki i gwiazdki (`dach_sklep` / `biel`) |
| `stragan_4` | (−34,2; 7,3) | 102 | tkaniny i chorągiewki (`dach_twierdza` / `biel`) |
| `stragan_5` | (−17,0; −29,4) | 30 | zabawki-klocki (`dach_kolo` / `biel`) |

Wszystkie stragany stoją w północno-zachodniej połowie rynku — **za plecami gracza**, poza pierwszym kadrem.

### 4.8 Strefy zieleni i korytarze widoku

| Strefa | Środek (x; z) | Zawartość |
|---|---|---|
| Z1 Podwórko kuźni | (67,5; −39,0) | ziemia, sągi drewna, 2 drzewa, 4 krzaki, skrzynie |
| Z2 Sad | (−18,6; −69,5) | 3 drzewa owocowe (jabłka `czerwien`), ławka |
| Z3 Łąka przy bramie | (−62,4; −31,8) | 2 drzewa, siano, płotek |
| Z4 Padok | (−70,6; 37,6) | ogrodzony padok `ziemia` 20 × 14 za stajnią, koryto, 2 drzewa |
| Z5 Ogród przy stawie | (31,5; 77,9) | grządki (dynie `pomarancz`, sałata `lisc_jasny`), 2 drzewa, kwiaty |
| Z6 Zaplecze karczmy | (89,2; 80,3) | sekret: piramida beczek i skrzyń (stopnie ≤ 6) na tylną połać karczmy → skrzynia przy kotle; 2 drzewa |

**Korytarze widoku — w nich nic wyższego niż 6** (drzewa, stragany, sągi; latarnie wolno, jeśli przekrój ≤ 1 × 1 i co ≥ 12): (a) trójkąt punkt wejścia (21,4; 18,0) – narożniki frontu podium karczmy (41,2; 64,5) i (70,7; 29,3); (b) pasy 8 szer. od punktu wejścia do punktów interakcji wylęgarni, zbrojowni i bramy lochów; (c) każda szprycha + 4 study z każdej strony; (d) stożek 60° × 20 przed każdą fasadą budynku głównego.

### 4.9 Reguły rozrzutu rekwizytów

Latarnie i chorągwie to „okruszki” co 12–16 studów wzdłuż szprych, chorągwie w kolorze kodu celu. Beczki (woda albo jabłka — **nigdy trunek**), skrzynie i siano w trójkach duży–średni–mały, przechył 5–12°, przy ścianach i na podwórkach, nie na środku dróg. Rekwizyty z kolizją na ścieżce ≥ 2,5 albo bez kolizji. 10 „wypadniętych klocków” (2 × 2 × 1 w kolorach dachów) rozsypanych przy murze i w trawie.

### 4.10 Pierwszy kadr (sprawdzony geometrią i renderem makiety)

Kamera gracza 12,5 za punktem wejścia, 8 nad ziemią, spojrzenie 58°; kadr 16 : 9 = ±51° (telefon ±56°). Kąty dodatnie = lewa strona kadru.

| Miejsce | Zasięg w kadrze | Odległość | Wejście |
|---|---|---|---|
| Wylęgarnia | −78°…−26° (połowa w kadrze) | 45 | drzwi −44°, widoczne |
| Karczma + tablica | −28°…+15° (cała) | 76 | drzwi −11°, tablica ok. +5°, widoczne |
| Brama lochów (w głębi Lochowej) | +16°…+35° (cała) | 100 | gardziel +25°, widoczna |
| Zbrojownia z kuźnią | +30°…+76° (połowa w kadrze) | 50 | drzwi +48°, kuźnia +42°…+47°, widoczne |

Żaden cel nie zasłania wejścia innego. Szczyt karczmy jest 31° nad poziomem kamery: w ujęciu z oczu (`u01`) mieści się cały, w domyślnej kamerze gracza (`u02`, kamera patrzy 14° w dół) kocioł na dachu jest przycięty — dlatego szyld karczmy wisi nisko (środek 15), a kocioł jest tylko echem sylwetki.

---

## 5. Karty budynków

### 5.0 Zasady pracy budowniczego (kontrakt techniczny)

1. **Plik:** `swiat/krzywe_miasteczko/budynki/<id>.py` z `NAZWA = "<nazwa_grupy>"` i funkcją `buduj(s, rnd)`. Wszystko w układzie lokalnym budynku: środek działki na ziemi = (0; 0; 0), front z wejściem po stronie +Z, działka x ∈ [−szer/2; szer/2], z ∈ [−gł/2; gł/2], y od 0 do `wys.`. Okapy i szyldy mogą wystawać poza działkę najwyżej 2,5 i tylko powyżej 10 nad ziemią. Nie przesuwaj i nie obracaj całego budynku — robi to generator. `rnd` tylko do drobnej losowości (wynik powtarzalny).
2. **Kolory** tylko kluczami z `paleta.py`; wariant ciemniejszy: `from swiat.krzywe_miasteczko.paleta import cien` → `cien(s, "tynk_krem")`. Najwyżej 2 dodatkowe kolory `RRGGBB` na rekwizyt, zgłoszone w raporcie.
3. **Podgrupy** zawsze z prefiksem: `s.grupa("Karczma/Tablica")` (biblioteka nie zagnieżdża nazw — „Tablica” bez prefiksu zderzy się z cudzą).
4. **Cechy:** dekoracje w `with s.cechy(kolizja=False):`; części mniejsze niż 2 w każdym wymiarze i płaskie łaty także `cien=False`. Kolizję mają tylko: ściany parteru, cokół, podłogi, schody, filary, lady (≤ 40% części budynku). Nie wołaj `s.obrys_sylwetki()`.
5. **Interakcja:** w podanym punkcie lokalnym część „Punkt interakcji” — blok 2 × 0,2 × 2, `alfa=1.0`, bez kolizji i cienia (zaczep dla ProximityPrompt), w podgrupie `"<NazwaGrupy>/_Interakcja"` — podkreślnik sprawia, że podgląd nie wlicza jej do zakresu wymiarów (punkt leży przed działką).
6. **Wnętrz nie budujemy.** Drzwi to wnęka 1 studa (skrzydło cofnięte), okna to Neon w ramie.
7. **Limity na budynek:** budżet z karty (twardy), walce ≤ 30 (wylęgarnia ≤ 40), kule ≤ 6, Neon ≤ 10 części, przezroczyste ≤ 3.
8. **Podgląd i odbiór:** `python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/<id>.py --wyj <scratchpad>/noc/mapa/rendery/<id> --szer 1000` oraz drugi raz z `--swiatlo studio --tylko a_,d_`. **Obejrzyj kadry narzędziem Read.** Gotowe, gdy: 0 ostrzeżeń „migotanie”, liczba części ≤ budżet, zakres z wiersza `PODGLAD` mieści się w działce i wysokości, przejdzie test czarnej sylwetki (rozdz. 8).
9. **Raport:** liczba części (ile Neon / walców / kul / z kolizją), zakres wymiarów, co odbiega od karty i dlaczego.

Wymiary w kartach są lokalne. „Lewo/prawo” = jak widzi patrzący na front.

### 5.1 Karczma — „Gospoda Pod Pękatym Kotłem” (`karczma`, Karczma)

(70,5; 59,1), obrót −130°, działka 46 × 38, wys. ≤ 50, budżet 470, pochylenie +, front w pełnym słońcu, na wprost punktu wejścia.

Stoisz na podium (y = 0 to jego wierzch); podium i schody 28 szer. w osi x = −3 buduje generator. Parter 38 × 22 (x ±19, z −17…+5), wys. 12, pionowy, ry −4°, cokół 1,2 `kamien_cokol`. Piętro 41 × 25, wys. 9: nawis z frontu 3, z lewej 2, z prawej 1; rz +6°, ry +4°. Dach dwuspadowy, kalenica wzdłuż X przesunięta 3 ku tyłowi: połać frontowa 48°, tylna 59°, wysokość 18, okap 3, nad szczytami 2,5; całość rz −4° (kontra). Żart: komin-kocioł Ø 9 × 7 (`metal_ciemny`, rant `tusz`) na tylnej połaci po lewej, przechył 10°, z chochlą 12 pod 30° i trzema kłębami pary `biel` Ø 3/4/5 — wierzch ≤ 50. Szyld: pieczony udziec 10 × 5 (`drewno_jasne`, kość `biel`, płetwa `tusz`) na wysięgniku z prawego narożnika, środek na 15, przechył 12°. Tablica zleceń: środek (−12; 13), ry +12°, deska 16 × 10 (`drewno_jasne`, rama `tusz` 0,8) na krzywych słupach ±5°, spód na 4, daszek `dach_karczma`; trzy kartki 3 × 4 (`biel`, `zloto`, `tynk_blekit`) z kształtem w tuszu (koło, X, trójkąt), jedna wisi na jednej pinezce pod 25°. Echo: parujący kubek kakao na daszku tablicy. Drzwi 8 × 11 w x = +6; okna `neon_okno`; ściany `tynk_krem`, pas `cien` pod nawisem. Interakcja: (6; 9) i (−11; 17). Unikaj: kufli, beczek z kranem, butelek, tablicy zasłaniającej drzwi.

### 5.2 Zbrojownia z kuźnią (`zbrojownia`, Zbrojownia)

(57,7; −6,1), obrót −74°, działka 32 × 26, wys. ≤ 30, budżet 320, pochylenie −, front w słońcu; w pierwszym kadrze przy lewej krawędzi — strona +X (kuźnia, drzwi) jest zwrócona ku środkowi kadru.

Ciężka, przysadzista bryła (k 0,75). Korpus 24 × 18 (x −15…+9, z −11…+7), wys. 13, ściany pionowe `kamien_cieply`, cokół 1,5 `kamien_cokol` (Cobblestone). Dach czterospadowy 37°, wysokość 9, okap 3, „wgnieciony”: kalenica z 3 odcinków, środkowy niżej o 1,5; dach rz −6°, ry +5°; kolor `dach_zbrojownia`, kalenica i deski czołowe `zloto` 1,2 (jasny obrys). Komin z tyłu po lewej: 3 segmenty 4 × 4 (Brick, `kamien_cokol`), każdy +4° w prawo, wierzch na 30, czapa `tusz`, 3 iskry `neon_ogien`, 2 kłęby dymu `cien(kamien_cokol)`. Kuźnia: otwarta przybudówka po prawej (x +9…+16, z −8…+7), daszek pulpitowy na dwóch krzywych słupach, palenisko 4 × 3 `neon_ogien`, kowadło 6 × 3 × 3 `metal_ciemny` na pniu, świecąca sztaba. Szyld: miecz 14 wbity w połać frontową po prawej, 15° od pionu, środek na 19; ostrze `tynk_blekit` z płetwą `tusz`, jelec i głowica `zloto`; wokół 4 odstające dachówki. Żart: pod okapem na lewo od drzwi tarcza Ø 8 (`dach_zbrojownia`, rant `zloto`) z trzema strzałami wbitymi pod różnymi kątami, środek na 12 — „przetestowana”. Drzwi 8 × 10 w x = +4 (`drewno_ciemne`, okucia `metal_ciemny`); 3 okna, jedno okrągłe. Interakcja: (4; 17). Unikaj: materiału Metal, symetrii, broni dłuższej niż 16.

### 5.3 Sklep magiczny (`sklep_magiczny`, SklepMagiczny)

(38,9; −40,3), obrót −56°, działka 24 × 24, wys. ≤ 42, budżet 290, pochylenie +, front w świetle ślizgowym (0,24) — drugi punkt orientacyjny miasta.

Smukła iglica (k 1,6). Parter 14 × 14 (środek (0; −1), front z = +6), wys. 12, pionowy, `tynk_lawenda`, cokół 1,2. Piętro 1: 15,5 × 15,5, wys. 7, nawis z frontu 1,5, ry +6°, rz +5°. Piętro 2: 12 × 12, wys. 6, względem piętra 1 ry −5° i rz +4° (łamany trzon). Dach-kapelusz na wysokości 25: rondo — walec Ø 22 × 0,8 `dach_sklep` z podkładką `tusz` Ø 22,8 pod spodem; stożek z 3 ostrosłupów (podstawy 13 → 8,2 → 5,2; wysokości 9 → 8 → 7; każdy następny wyrasta z 45% wysokości poprzedniego, zgięty o 13° do tyłu i skręcony o 20°), czubek złamany łącznie o ok. 25°; na czubku gwiazdka `zloto` 2,5 na trzech zygzakach-sprężynce; wierzch ≤ 42. Opaska `zloto` 1,5 z klamrą 3 × 3. Szyld: kostur 16 oparty o lewy narożnik pod 10°, nad nim kryształ z dwóch ostrosłupów `neon_magia` unoszący się 1 nad końcem; środek na 14. Żart: z okna piętra 1 wystaje pomarańczowy koci ogon z 5 segmentów (razem 8, z podkładką `tusz`) zakręcony w znak zapytania. Echo: jedna rama okna oderwana 1,5 od ściany i obrócona 12°. Drzwi łukowe 8 × 10 w x = −3 (`drewno_ciemne`, gwiazda `zloto`); okna `neon_magia`. Interakcja: (−3; 16). Unikaj: grzybów (symbol gry-inspiracji), butelek i flaszek, kotła (ma go karczma).

### 5.4 Wylęgarnia petów (`wylegarnia`, Wylegarnia)

(16,0; 55,8), obrót −172°, działka 30 × 28, wys. ≤ 28, budżet 300, pochylenie −, front w słońcu; w pierwszym kadrze przy prawej krawędzi — drzwi po lewej (−X) stronie, bliżej środka kadru.

Budynek-jajo, które właśnie się wykluwa. Skorupa `biel` z 4 walców o pionowej osi, środek (0; −2): Ø 16 (y 0–4), Ø 20 (4–10), Ø 21 (10–15), Ø 19 (15–19); co drugi przesunięty o 0,6 w bok. Na wysokości 19 zygzak pęknięcia z 10 belek `tusz` 0,6. Kapsel `dach_wylegarnia`: walce Ø 15 × 3,5 i Ø 10 × 2,5 plus kula Ø 8 na wierzchu, uniesiony o 2 i przechylony rz −20° — spod niego wygląda pet-slime: kostka 4 × 4 × 4 `neon_slime` z oczami `tusz`. Kropki: 6 płaskich walców Ø 2,5–4 `dach_wylegarnia` na skorupie. U podstawy gniazdo: 16 belek `drewno`/`drewno_jasne` w pierścieniu Ø 24, wys. 2–3, każda inaczej obrócona, z przerwą 10 przed drzwiami. Szyld: łapa Ø 9 (poduszka Ø 6 i cztery palce Ø 2, `pomarancz`, płetwa `tusz`) na wysięgniku po lewej, środek na 15, przechył 12°. Żart: wykluwający się budynek — kapsel i slime. Echo: miska Ø 7 `dach_wylegarnia` z kością `biel` przy prawym boku. Drzwi łukowe 8 × 10 w x = −5 na skorupie (z ≈ +7), `dach_wylegarnia` w ramie `tusz`; 2 okrągłe okna `neon_slime`. Ściany walców są pionowe, więc dolne 10 studów jest bezpieczne. Interakcja: (−5; 18). Unikaj: przezroczystej skorupy, więcej niż 40 walców i 6 kul, petów spoza kanonu (pies, slime, smok).

### 5.5 Brama lochów (`brama_lochow`, BramaLochow)

(109,6; 23,3), obrót −102°, działka 30 × 20, wys. ≤ 36, budżet 290, front w słońcu, na dnie niecki: y = 0 to dno (świat −4). Niecka, rampa i skała za murem — generator.

Paszcza w skale. Masyw z bloków `kamien_lochu`, nierówny: lewa część do 34, prawa do 26, każdy blok obrócony o 4–10°, front ok. z = +6. Gardziel: przejście 12 × 14 w x = 0, łuk z 11 klińców (co drugi głębszy o 0,2), krawędzie łuku z jasnym obrysem `kamien_cieply` 0,8 — tusz na tym kamieniu nie działa. W głębi 3 płyta `neon_portal` 12 × 14. Zęby: 7 górnych klinów 1,5–3, każdy inny (`biel`), 2 dolne tylko po bokach progu — przejście wolne. Oczy: kule Ø 4 `biel` na 24 i 27, źrenice `tusz` patrzą w różne strony. Na górnych blokach czapy mchu `dach_lochy`; kryształy po bokach: ostrosłupy 2–7, tylko największy `neon_portal`, reszta `dach_lochy`. Język: płyta 8 × 0,3 × 4 (`dach_kolo`) od progu do krawędzi działki. Filary: lewy rz −6°, prawy rz +5°. Szyld: krzywy trójkąt ostrzegawczy 8 (`zloto`, rama `tusz`) na jednym gwoździu, obrót 25°, z czaszką z klocków `biel`/`tusz`, środek na 16, po lewej. Żart: zerwany łańcuch z 8 ogniw zwisa z łuku, otwarta kłódka `zloto` leży na ziemi — ktoś już wszedł. Interakcja: (0; 14). Unikaj: dolnych zębów na środku przejścia, przezroczystego portalu, wszystkiego ciemnego bez jasnej krawędzi.

### 5.6 Stajnia wierzchowców (`stajnia`, Stajnia)

(−45,7; 35,7), obrót 128°, działka 38 × 22, wys. ≤ 20, budżet 270, pochylenie +, front w cieniu — dlatego jasne obramowania.

Długa i niska (k 0,6). Korpus 32 × 16 (środek (0; −1), front z = +7), wys. 9, ściany `drewno_ciemne` (WoodPlanks), narożniki i ramy `drewno_jasne` 1,2 — jasny obrys zamiast tuszu; cokół 1 `kamien_cokol`. Dach-strzecha `dach_stajnia`: dwuspadowy 42°, grubość 1,8, okap z frontu 3,5, z tyłu 2, z boków 3; kalenica „w siodło” z 3 odcinków, środkowy niżej o 1,5; krawędź okapu poszarpana (co drugi blok 0,3 niżej); spód okapu i kalenica `tusz`; dach rz +4°, ry −4°. Na kalenicy wiatrowskaz-konik 3. Lukarna nad lewą częścią: skrzynka 6 × 5 z otworem strychu, w nim zaklinowana bela siana Ø 6 × 5 z wbitymi widłami 8. Szyld: podkowa-brama wokół drzwi głównych — łuk 240° z 9 bloków `zloto` (pas 1,8), 12 × 13, z 7 „dziurami” `tusz`; drzwi 8 × 10 w x = −8. Obok trzy boksy z połówkowymi drzwiczkami (`biel` w ramie `drewno_jasne`); z jednego wygląda koński łeb z klocków (`drewno`, grzywa `tusz`). Żart: z okna strychu wysuwa się wędka 12, na żyłce marchewka (`pomarancz` 5 + nać `lisc_jasny`) wisi 1,5 przed pyskiem konia. Echo: koryto z wodą przy prawym boku, wys. 2. Interakcja: (−8; 15). Unikaj: tuszu na ciemnym drewnie, siodeł z logotypami, przeszkód 6,5–9 przy wejściu.

### 5.7 Brama do twierdzy gracza (`brama_twierdzy`, BramaTwierdzy)

(−34,0; 104,6), obrót 162°, działka 32 × 18, wys. ≤ 36, budżet 280, front w świetle ślizgowym, wbudowana w mur (tył przy z = −9).

Brama do własnej twierdzy, z rozłożonymi „ramionami” — dwie baszty nie do pary pochylone na zewnątrz. Lewa okrągła, środek (−10,5; −2): walce Ø 11 / 9,5 / 8,2 o wysokościach 14 / 11 / 8, gzymsy `tusz` Ø +0,9, całość rz +5°. Prawa kwadratowa 10 × 10, środek (11; −2), wys. 23, zwężana ku górze (ostrosłup ścięty 10 → 8), rz −7°. Obie z blankami (zęby 1,6, co drugi wyższy o 0,25), bez dachów; `kamien_cieply`, cokół `kamien_cokol`. Między nimi przejście 10 × 12 (x −5…+5) z łukiem z 9 klińców; w głębi 2 płyta `neon_okno` 10 × 12 — złoty portal do twierdzy. Krata podniesiona krzywo: prawa strona niżej o 1,5, dolna krawędź ≥ 12,5. Szyld: drewniany żuraw na prawej baszcie — wysięgnik 12 nad przejściem, lina `tusz` 0,3, na niej blok 4 × 4 × 4 `kamien_cieply` (zapowiedź budowania), dół bloku na 14. Sztandar `dach_twierdza` 5 × 12 z 3 segmentów (±8°) na lewej baszcie, z kwadratową łatą `zloto` i 4 szwami `tusz`. Żart: wycieraczka 8 × 4 × 0,3 (`dach_twierdza`, rant `zloto`) przed przejściem. Echo: złoty klucz 12 na haku przy lewej baszcie. Interakcja: (0; 13). Unikaj: dachów na basztach, kraty niżej niż 12,5, symetrii baszt.

### 5.8 Siedziba gildii — „wkrótce” (`gildia`, Gildia)

(−105,4; −11,1), obrót 84°, działka 28 × 28, wys. ≤ 40, budżet 280, pochylenie −, front w cieniu, wbudowana w mur na końcu ulicy Gildyjnej.

Zamknięta, ale kusząca wieża (k 1,4). Parter 16 × 16 (środek (0; −2), front z = +6), wys. 12, pionowy, `tynk_blekit`, cokół `kamien_cokol`. Piętro 2: 17,5 × 17,5, wys. 8, ry +6°. Piętro 3: 16 × 16, wys. 7, ry −6° i rz −4°. Korona 18 × 18 × 4 z blankami, rz +3° (kontra). Dach-ostrosłup 20 × 20 × 9 `dach_gildia`, krawędzie i gałka `zloto`. Balkon na piętrze 2 od frontu (6 × 3, balustrada `tusz`) z rogiem z 5 walców Ø 1,5 → 5 łamanych co 12° (razem 10, `zloto`). Szyld: sztandar 6 × 14 z 3 segmentów (±8°) zwisający z korony, `dach_gildia` z herbem z trzech kształtów (koło `zloto`, kwadrat `biel`, trójkąt `czerwien`), środek na 18. „Wkrótce” bez liter: drzwi 8 × 10 w x = +2 zabite trzema deskami na krzyż (`drewno_jasne`, ±20°) z kłódką `zloto` 4 × 5; na deskach klepsydra 4 (dwa ostrosłupy `zloto`, piasek `bruk`). Żart: rusztowanie z lewej (4 słupy `drewno`, 3 pomosty), wiszące wiadro i niebieski zaciek farby `tynk_blekit` na ścianie `cien(tynk_blekit)` — ktoś odnawia siedzibę. Kuszenie: w najwyższym oknie pali się `neon_okno`. Interakcja: (2; 18). Unikaj: liter „wkrótce”, ciemnych ścian (front stoi w cieniu), symetrycznych pięter.

### 5.9 Arena — „wkrótce” (`arena`, Arena)

(18,4; −104,4), obrót −10°, działka 48 × 32, wys. ≤ 34, budżet 330, front w cieniu, wbudowana w mur — reszta areny jest „za murem”.

Wycinek wielkiego pierścienia. Mur areny z 6 segmentów 7 × 18 × 4 (`kamien_cieply`, co drugi 20 wys. i `cien`) na okręgu o promieniu 30 ze środkiem w (0; −22), wypukły ku rynkowi, na kątach ±13°, ±26°, ±39°; w środku (0°) brama. Na koronie kolce: ostrosłupy 2 × 3 `dach_arena` co 3,5. Między segmentami proporce 3 × 10 (Fabric) na przemian `dach_arena` i `biel`. Brama: dwa filary — lewy 24 wys. rz +5°, prawy 18 wys. rz −7° — i przejście 12 × 14. Szyld: hełm-olbrzym 14 × 12 nad przejściem (`tynk_blekit`, szpara przyłbicy `tusz` 1,0, płetwa `tusz`) z pióropuszem z 5 płyt `dach_arena`, środek na 20, przechył 10°. „Wkrótce”: przejście zabite deskami na krzyż, dwa łańcuchy z kłódką `zloto`; w szparze między deskami ciepłe światło `neon_okno`. Żart: w murze obok bramy wklęsły odcisk ludzika 6 × 7,5 (`tusz`, głębokość 0,5) — jakby ktoś wyleciał przez ścianę. Echo: gong Ø 10 (`zloto`, podkładka `tusz`) na dwóch krzywych słupach po prawej. Kuszenie: zza muru wystaje złoty puchar 6 z plastrem na krzyż (`biel`). Interakcja: (0; 20). Unikaj: pełnego pierścienia (wyjdzie poza mur), symetrycznych filarów, krwi i broni wbitej w ludzi.

### 5.10 Brama miejska z murem (`brama_miejska`, BramaMiejska)

(−74,9; −83,2), obrót 42°, działka 46 × 14, wys. ≤ 27, budżet 250, front (ku miastu) w cieniu, w osi ulicy Bramnej.

Krawędź świata i rama ulicy głównej. Przejście 16 × 14 (x −8…+8) — prześwit ≥ 14 na całej szerokości, bo przechodzą tędy wszyscy. Lewa wieża kwadratowa 9 × 9 (środek x = −13), wys. 21 + dach-ostrosłup 6 `dach_brama`, rz +6°; prawa okrągła Ø 9 (środek x = +13), wys. 18 + stożek „gwiazda” 5, rz −5°. Nad przejściem ganek straży: podłoga na 14, ściany `tynk_krem` z belkami `drewno_ciemne`, wys. 6, nawis 1,5 w stronę miasta, dach `dach_brama` 30°. Po bokach odcinki muru do krawędzi działki według wzorca z 4.3 (korpus 4 × 14, rant `tusz`, blanki 2 × 2 co 2). Ściany `kamien_cieply`, cokół `kamien_cokol`. Szyld: dzwon alarmowy Ø 8 × 8 (`zloto`, podkładka `tusz`) w ganku nad przejściem, środek na 17, spód ≥ 14. Żart: z okna prawej wieży wystają dwa wielkie buty śpiącego strażnika (`drewno_ciemne`, 3 × 2 × 4), a na parapecie leży jego hełm z piórem (`tynk_blekit`, pióro `dach_brama`). Echo: krata podniesiona krzywo, lewa strona niżej o 1,5, dół ≥ 14. Front stoi w cieniu — jasne ściany i 2 okna `neon_okno`. Interakcja: (0; 11) — zapas na przyszłe wyjście do krain. Unikaj: zamykania przejścia, prześwitu niższego niż 14, symetrii wież, chorągwi z literami.

### 5.11 Studnia-pomnik Pierwszego Klocka (`studnia_pomnik`, StudniaPomnik)

(0,0; 0,0), obrót 50° (front ku punktowi wejścia), działka 18 × 18, wys. ≤ 22, budżet 150. Gracz pojawia się lokalnie w (0; 28), a kamera startuje ok. (0; 15) — nic poza działką.

Środek rynku i podpis świata: miasto zaczęło się od jednego klocka, który do dziś stoi krzywo. Cembrowina: 12 kamieni 3,6 × 2,6 × 1,6 na okręgu r = 7 (co drugi wyższy o 0,25, `kamien_cieply` i `cien`), rant `tusz`. Woda warstwami: pas `woda_gleboka` na 1,5, tafla `woda` Ø 13 na 1,6, trzy bliki `biel` 0,4 × 2 na 1,7. Z wody rośnie krzywa kolumna: 3 segmenty walców Ø 3 → 2,4 (`kamien_cieply`, gzymsy `tusz`), przechyły +8°, −11°, +7°, wierzch na 14. Pomnik: klocek-olbrzym 8 × 4 × 4 `zloto` z 8 wypustkami (walce Ø 1,6 × 0,8) i płetwą `tusz`, postawiony na krawędzi, przechył 25° w bok i 15° w przód, środek na 17. Żart: cały klocek podpiera jedna cieniutka podpórka `drewno` 0,4 × 6 — miasto trzyma się na patyku. Funkcja studni: od frontu krzywy kołowrót — dwa słupy `drewno_ciemne` ±4°, wałek, wiadro (`drewno`, obręcz `metal_ciemny`), korba. Echo: mały klocek 2 × 2 × 1 `zloto` wypadł na cembrowinę. Interakcja: (0; 13). Unikaj: postaci-pomnika (kopie bohaterów), kul, monet w wodzie, napisów na cokole.

### 5.12 Koło fortuny (`kolo_fortuny`, KoloFortuny)

(−12,6; 28,3), obrót 156°, działka 18 × 14, wys. ≤ 25, budżet 170, pochylenie −, na rynku 1,9 s od punktu wejścia.

Kiosk z darmowym kołem — prezenty, nie stawki. Stojak: odwrócone V z dwóch nóg 1,5 × 13 (`drewno`, ±12°), poprzeczka, cokół 1 `kamien_cokol`. Koło Ø 14, środek na 11 w z = −2, odchylone 8° do tyłu: tarcza — walec Ø 14 × 0,8 `biel`; na niej 8 szprych-segmentów 2,8 × 6,4 na przemian `dach_kolo`, `zloto`, `tynk_blekit`, `pomarancz`; pod spodem walec Ø 15 × 0,6 `tusz`; dookoła 8 promieni-klinów 2–3 `dach_kolo`; piasta Ø 3 `zloto`. Słup koła rz −6°. Wskaźnik: dłoń z wyciągniętym palcem 4 (`tynk_krem`, płetwa `tusz`) nad kołem. Lada 12 × 3 × 3,5 (`drewno_jasne`, rama `tusz`) przy froncie (z +4…+7) z markizą w pasy `dach_kolo` / `biel` (7 pasów pod 11°, na dwóch krzywych słupkach, spód na 9). Żart: na ladzie przewrócone pudełko-prezent 3 × 3 × 3 (`dach_kolo`, wstążka `zloto`) z uchylonym wieczkiem, a w środku jajko `biel` Ø 2,5. Echo: chorągiewka `dach_kolo` na czubku stojaka. Interakcja: (0; 11). Zakaz: kości, kart, żetonów, monet, dźwigni automatu i wszystkiego, co wygląda na stawianie waluty.

---

## 6. Elementy wspólne zestawu

Generator buduje je z jednej funkcji na typ (warianty parametrami), budowniczowie mogą z nich korzystać przy swoich budynkach. Kolory tylko z palety.

| Element | Wygląd | Części |
|---|---|---|
| Okno | rama-podkładka `tusz` (szer+1,2) × (wys+1,2) × 0,4 na licu +0,4; szyba Neon `neon_okno` na +0,5 (bez cienia); szpros `tusz` 0,35 na +0,6; parapet `drewno_jasne` (szer+2,1) × 0,55 × 1,2; okiennica z podkładką, odchylona 10–15° (jedna na fasadę); wymiary 3 × 4, 4 × 5 albo okrągłe Ø 3; każde obrócone 4–8° | 2 (tanie) – 6 |
| Drzwi | otwór 8 × 10 (dom 6 × 8); rama `tusz` 1,0 wysunięta 0,4; skrzydło `drewno_ciemne` (WoodPlanks) cofnięte o 1; 3 deski; 2 okucia `metal_ciemny`; gałka `zloto`; nadproże 1,2, szersze o 1 z każdej strony, przechylone 4–6° | 8 |
| Latarnia | słup łamany z 3 segmentów (+5°, −9°, wysięgnik −38°) `tusz`; klatka: daszek-romb `tusz`, światło Neon `neon_okno` 1,3 × 1,7, 2 pręty, spód; wys. 9; pod nią płaska plama Ø 8 × 0,1 `tynk_krem` (bez kolizji i cienia) | 8 |
| Skrzynia | blok 4 × 3,5 × 3,5 `drewno` (WoodPlanks), 4 listwy `drewno_ciemne` 0,5, wieko większe o 0,5, przechył 5–12° | 6 |
| Beczka (woda albo jabłka) | walec Ø 3,6 × 4,4 `drewno`; brzuch Ø +0,4 na 42% wysokości; 2 obręcze `metal_ciemny` Ø +0,6; w środku tafla `woda` albo 3 jabłka `czerwien` Ø 1,2 — **nigdy kran ani korek** | 5–7 |
| Stragan | 4 słupy odchylone 3–4° `drewno`; lada 10 × 3,4 × 3 `drewno_jasne`; markiza z 7 pasów pod 11° w dwóch kolorach (tabela 4.7) z ząbkami i rantem `tusz`; 3–4 bryły towaru ×1,5; wys. 10, obrys 10 × 7 | 13–25 |
| Chorągiew | maszt Ø 0,6 × 14 `tusz`; płat z 3 pasów skręconych +14° / −26° / +22° (Fabric) w kolorze kodu albo duetu; ogon z 2 klinów | 7 |
| Ławka | siedzisko 6 × 0,6 × 1,6 `drewno_jasne`, 2 nogi `tusz`, oparcie odchylone 10° | 4 |
| Drzewo liściaste (klockowe) | pień z 2 bloków `drewno` (Wood) 1,8 → 1,4, przechył +6° / −10°; korona z 4 bloków 8,5 / 6 / 4,2 / 3,8 obróconych do ±12°: dół `lisc_ciemny`, środek `lisc`, góra `lisc_jasny`; wys. 12–15; bez kolizji poza pniem | 6 |
| Drzewo iglaste (klockowe) | pień 1,6 `drewno`; 3 bloki 8 × 4 × 8 / 6 × 4 × 6 / 4 × 4 × 4 `igla`, skręcone naprzemiennie o 45°, każdy wyżej o 3,2; czubek — klin narożny `lisc_ciemny`; wys. 14–18 (tylko tło) | 5 |
| Krzak | 3 bloki 3,6 / 2,8 / 2,4 (`lisc_ciemny`, `lisc`, `lisc_jasny`) obrócone o 15–40° + 2 jagody 0,8 `czerwien`/`zloto`; bez kolizji | 5 |
| Kwiaty | skrzynka-grządka 4 × 0,6 × 2 `ziemia` + 4 kostki 1 × 1 × 1 w 2 kolorach (`czerwien`, `zloto`, `biel`, `dach_sklep`); tylko przy wejściach, ≤ 2 na budynek | 5 |
| Chmura | kule Ø 11 / 15 / 13 / 9 `biel` + płaski spód 24 × 3,2 × 8 `tynk_blekit`; y 110–150; bez kolizji i cienia | 5 |
| Płot (przęsło 6) | 3 sztachety `drewno_jasne` 0,6 × 3 (wys. ±0,3, przechył ±4°) + 2 żerdzie `drewno`; wys. 3 | 5 |
| Kamień | 1–2 bloki lub kliny 2–5 (`kamien_cieply`; przy lochach `kamien_lochu`, Slate), obrót dowolny | 1–2 |
| Dom mieszkalny wzorcowy | wg `przepisy.md` 4.1, wariant tani: cokół `kamien_cokol` 1,2; parter szer × gł z tabeli 4.7 minus 2, wys. 10, pionowy, ry ±4°; piętro wys. 8 z nawisem z frontu 2 i z jednego boku 1, rz ±5° (znak naprzemiennie), ry ±5°; dach pełny z 2 klinów 50° + kalenica (`tusz`, przy `dach_dom_lupek` — `zloto`), okap 2,5; komin łamany z 2–3 segmentów po stronie przeciwnej do nawisu; drzwi 6 × 8 przesunięte od osi; 3 okna różne; 1 znak miasteczka (klocek albo łata); wys. z tabeli 4.7 | 70–90 |

---

## 7. Ujęcia kontrolne

W układzie miasta (do renderu całej mapy: `--ujecia swiat/krzywe_miasteczko/ujecia.json --przesun 0,0,0`; w Studio dodać −700 do z). Ogniskowa 14,5 mm = pole widzenia kamery Roblox (70° w pionie przy 16 : 9). Każde ujęcie przechodzi testy T1–T4 (rozdz. 8) — najpierw w Blenderze (`--swiatlo slonce` i `--swiatlo studio`), potem zrzut ze Studio.

| Nazwa | Kamera (x, y, z) | Cel (x, y, z) | Ogniskowa | Rzut | Co sprawdza |
|---|---|---|---|---|---|
| `u01_oczy_spawn` | (21,4; 5,5; 18,0) | (89,2; 9,0; 60,4) | 14,5 | perspektywa | oczy gracza w punkcie wejścia: ≥ 4 miejsca rozpoznane, karczma 30–60% wysokości kadru, wejścia widoczne |
| `u02_kamera_gracza` | (10,8; 8,0; 11,4) | (21,4; 5,0; 18,0) | 14,5 | perspektywa | domyślna kamera 12,5 za postacią: tablica, drzwi, kuźnia, gardziel lochów w kadrze |
| `u03_mapa_gora` | (0; 400; 0,01) | (0; 0; 0) | 35 | prostokątny, skala 300 | 60/30/10, zieleń ≤ 30% wewnątrz muru, brak osi symetrii, kody dachów |
| `u04_panorama_nw` | (−150; 120; −100) | (10; 5; 10) | 24 | perspektywa | miniatura 3/4 od strony słońca: 3 duże plamy barwne, dominanta, sylwetki |
| `u05_panorama_se` | (160; 110; 140) | (−5; 5; −5) | 24 | perspektywa | najgorszy przypadek — pod słońce: miejsca różne od tła o ΔL\* ≥ 20 |
| `u06_karczma` | (20,0; 7,0; 27,5) | (60; 16; 50) | 20 | perspektywa | zbliżenie karczmy: tablica nie zasłania drzwi, szyld czytelny, krzywizny ≥ 5° |
| `u07_lochy_zbrojownia` | (26,5; 6,0; 14,1) | (100; 12; 26) | 18 | perspektywa | wylot Lochowej: zbrojownia z kuźnią, gardziel na końcu ulicy, karczma z boku |
| `u08_spawn_polnoc` | (21,4; 5,5; 18,0) | (21,4; 7,0; −120,0) | 14,5 | perspektywa | z punktu wejścia na północ: sklep, arena, stragany |
| `u09_spawn_wschod` | (21,4; 5,5; 18,0) | (140,0; 7,0; 18,0) | 14,5 | perspektywa | na wschód: zbrojownia, lochy, karczma |
| `u10_spawn_poludnie` | (21,4; 5,5; 18,0) | (21,4; 7,0; 140,0) | 14,5 | perspektywa | na południe: wylęgarnia, brama twierdzy, staw |
| `u11_spawn_zachod` | (21,4; 5,5; 18,0) | (−120,0; 7,0; 18,0) | 14,5 | perspektywa | na zachód, pod słońce: studnia, koło, stajnia, gildia |

Ujęcia `u08`–`u11` razem to panorama z punktu wejścia: w każdym ≥ 2 punkty orientacyjne, budynki ≥ 50% linii horyzontu, 0% płyty bazowej. Wartości w `ujecia.json` (format `[nazwa, [x,y,z] kamery, [x,y,z] celu, ogniskowa, skala rzutu albo null]`).

---

## 8. Lista kontrolna jakości dla krytyków

Na podstawie `ocena.md`. Liczy się zrzut ze Studio z oczu gracza; Blender jest podglądem roboczym.

**Cztery testy każdego kadru:**

| Test | Jak | Zaliczony, gdy |
|---|---|---|
| T1 miniatura | pomniejsz do 256 × 144 (ikona: środek 150 × 150), patrz 3 s | nazwiesz temat i dominantę; najwyżej 3 duże plamy barwne |
| T2 telefon | pomniejsz do 640 × 360, oglądaj w 100% | każde miejsce rozpoznane po kształcie i kolorze; symbole ≥ 24 px |
| T3 szarość | usuń kolor | trzy grupy waloru; miejsce różni się od tła o ΔL\* ≥ 20 |
| T4 zmrużenie | rozmycie o promieniu 1,2% szerokości | najmocniejszy kontrast na celu gracza; najwyżej 3 ogniska |

**Bramki (pułap wyniku):** brak zrzutu ze Studio z oczu gracza → najwyżej 7,0; w `u02` mniej niż 4 rozpoznane miejsca → 6,0; dominanta w szarości bliżej tła niż ΔL\* 20 → 6,0; widoczna płyta bazowa lub krawędź mapy z poziomu gracza → 7,0; skopiowany budynek, postać, logo albo żart gry-inspiracji → kryterium 11 = 0 i wynik ≤ 5,0.

**Rubryka (wagi = 100; ocena 0–10, każda z pomiarem i jedną poprawką z liczbą):**

| Kryterium (waga) | 10/10, gdy |
|---|---|
| 1. Miniatura i telefon (12) | dominanta 15–30% kadru; ≤ 3 duże plamy; każde miejsce ≥ 24 px i własny kolor dachu; symbol szyldu ≥ d/10 |
| 2. Hierarchia (12) | rzędy wysokości co ≥ 30% (54 → 36–42 → 20–34); dominanta ≥ 2× najwyższe drzewo; zewsząd widać ≥ 2 punkty |
| 3. Sylwetki (10) | z punktu wejścia ≥ 50% linii horyzontu to budynki, ≤ 25% drzewa, 0% pustki; każde miejsce ma inny kształt bazowy; obrys łamie się co 8–15 |
| 4. Walor (12) | ściany i bruk L\* ≥ 78, dachy i zieleń średnie, tusz i otwory ≤ 20; ściana–dach ≥ 30 L\*; droga–trawa ≥ 15 albo krawężnik tuszem |
| 5. Paleta (8) | ≈ 60/30/10; zieleń ≤ 30%; akcent tylko na celach; duże płaszczyzny bez szarości; sąsiedzi bez powtórzeń koloru dachu |
| 6. Rytm brył (8) | trzy klasy wielkości; sąsiedzi różnią się wysokością ≥ 20%, kształtem i kierunkiem przechyłu; fronty odchylone od osi rynku o 5–10°; ≥ 4 typy dachów; plan bez osi symetrii |
| 7. Prowadzenie (10) | z punktu wejścia ≥ 4 miejsca, każde ≥ 10% wysokości ekranu; drogi jaśniejsze od otoczenia; wejście najbardziej kontrastowe na fasadzie; fronty w słońcu |
| 8. Gęstość detalu (8) | ≥ 55% części w miejscach i na rynku, ≤ 25% w zieleni; ≥ 60% fasady gładkie; części < 1 stud ≤ 5% |
| 9. Skala (6) | drzwi ≥ 8 × 10; ulice 16 / 12 / 10; parter 11–12; stopień ≤ 1; manekin 5 w kadrze |
| 10. Spójność stylu (8) | tusz ≥ 3 px na telefonie, wysunięty 0,3–0,5; przechył kondygnacji 5–8°; SmoothPlastic ≥ 80%; jedna paleta |
| 11. Charakter i humor (6) | jeden własny gag na miejsce czytelny z 30 studów; budynek ma „postawę”; zero kopii |

**Błędy v1 (wynik 3,6/10), których nie wolno powtórzyć:**

1. Zieleń zalewała kadr (80% planu, 65% części to drzewa i runo) → zieleń ≤ 30% planu, ≤ 14 drzew w mieście, ≤ 25% części.
2. Drzewa wyższe od budynków (mediana 22,9), jedna dominanta → drzewa ≤ 15, każde miejsce ≥ 20, rzędy co ≥ 30%.
3. Zlane walory (trawa, bruk, woda, dachy w L\* 60–67) → bruk L\* 80 z krawężnikiem tuszem, ściana–dach ≥ 30 L\*.
4. Studio zgasiło kolory (nasycenie −20…−54%) → zapas nasycenia, zielenie ciepłe, liście i grunt ze SmoothPlastic, nie z Grass/Ground.
5. Front dominanty w cieniu, gracz patrzył pod słońce → miejsca pętli na wschodzie i południu, punkt wejścia plecami do słońca.
6. Brak stylu z kanonu: proste bryły, lustrzana fasada, dach 39% wysokości, przechył tylko komina 3,5° → przykazania 1–5 i 12.
7. Mapa na szarej płycie z widoczną krawędzią → mur 16 + pierścień wzgórz 24–45 i płyta 440 × 440.
8. Brama zasłaniała cel → prześwity ≥ 14, szyldy obok osi drogi.
9. Budżet w runie (258 kwiatów po 0,5; 17,6% części poniżej 1 studa) → nic poniżej 1 studa poza szwami i detalami szyldów.
10. Ten sam czerwony na czterech obiektach → jeden kolor-kod na miejsce.
11. Układ „krzyż na polanie”, lustrzane pary, płasko → plan bez osi symetrii, trzy poziomy (−4, 0, +4), łamane ulice.
12. Wzrok uciekał od celu (koło przed szyldem karczmy, latarnia w osi portalu) → korytarze widoku z 4.8.
13. Symbole za małe, Neon wypalony (jajo na szyldzie 1,5) → szyldy 8–12, Neon ≤ 3% i tylko nasycone `neon_*`.

**Do każdego budynku osobno:** test czarnej sylwetki (rozpoznawalny ze 100 studów); kąty pochyleń zmierzone (0° albo ≥ 4°; nic 1–3°); dolne 10 studów pionowe; wejście ≥ 8 szer. i wolne 8 × 8; Neon ≤ 10; 0 ostrzeżeń „migotanie”; budżet dotrzymany.

---

## 9. Co robimy po swojemu

Od gry-inspiracji bierzemy tylko zasady: przerysowanie, krzywizny, asymetrię, ciepły humor w rekwizytach. Wszystko inne jest nasze:

- **Świat z klocków, który się nie domyka.** Krzywizna ma wytłumaczenie w świecie: miasto zbudowano z klocków, które nie do końca pasują. Stąd pomnik Pierwszego Klocka podparty patykiem, „wypadnięte klocki” przy każdym budynku, łaty z fastrygą i żuraw z klockiem nad bramą twierdzy. Gra-inspiracja jest malowanym 2D; my mamy chodzony 3D z prymitywów Roblox.
- **Własny duet zamiast cudzych bohaterów.** Barwy Rycerza (błękit tabardu) i Kota-Maga (pomarańcz i purpura) wracają w chorągiewkach, w sztandarze twierdzy, w kocim ogonie z okna sklepu i w kapeluszu-dachu. Żadnych postaci, sprzedawców, nazw ani ikon z gry-inspiracji; pomnik to klocek, nie bohater.
- **Gospoda z jedzeniem, nie z trunkiem.** Kocioł z parą, chochla, udziec i kakao — gra jest dla młodszych graczy.
- **Własny układ.** Promienisty rynek ustawiony pod słońce tego miejsca, szprychy z „kamieniami milowymi” i ścieżki-kody w kolorach dachów — nie panorama ulicy ani kolejność budynków z gry-inspiracji.
- **Zapowiedzi zamiast pustki.** Arena i gildia są zamknięte deskami, z klepsydrą, światłem w szparze i odciskiem ludzika w murze — obiecują, ale nie udają, że działają.
- **Koło bez hazardu.** Koło rozdaje prezenty za czas i aktywność: żadnych kości, kart, żetonów ani stawiania waluty.
- **Zero liter.** Wszystkie znaczenia niosą kształty, kolory i rekwizyty — działa na każdym języku i na małym ekranie.
- **Nie przejmujemy:** grzyba jako symbolu waluty ani ozdoby sklepów, toalety jako magicznego urządzenia, cudzych marek (maskotki-zabawki z rozmowy 12.11), nazw lochów, potworów i petów, wyglądu konkretnych budynków i ekranów.

**Do sprawdzenia przez człowieka:** pomysły rekwizytów nie zostały porównane z ekranami gry-inspiracji (zakaz użycia jej nazwy w wyszukiwaniu) — przegląd Game Directora przed kanonem.
