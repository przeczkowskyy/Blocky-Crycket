# Dżungla w grze — trzeci grywalny biom (potwory, brama do Pustyni, przelot, mgła, teleport)

*Status: **propozycja** (18.11.2026, sesja nocna — zlecenie Karola „odpalaj resztę wszystkich tasków”). Nic tu nie jest
kanonem. Wszystko stoi w osobnych kontenerach (`Workspace/DzunglaPas` — mapa, `Workspace/DzunglaPasGra` — gra), więc
całość da się cofnąć (`--usun`).*

> **W skrócie.** Gracz, który pokonał Strażnika Topieli, przechodzi bramą Bagna prosto do Dżungli. Przy pierwszym
> wejściu ogląda przelot kamery zakończony rykiem Węża Stu Lian. W trzech zagrodach walczy z trzema gatunkami trzech
> klas, w Ruinach spotyka rzadkiego Pancernika, a na końcu, w Kręgu Stu Lian, czeka trudny strażnik. Po wygranej
> otwiera się brama do Pustyni („wkrótce”). Kod gry jest TEN SAM co w lesie-pasie i Bagnie
> (`swiat/las_pas_gra`, `swiat/las_potwory`); ten pakiet daje tylko dane i konfigurację.

## Skąd co jest
| Co | Gdzie |
|---|---|
| Mapa (projekt, układ Bagna + 940 st) | `swiat/dzungla_pas/` (`generuj.py`, `sprawdz.py`, README) |
| Mapa gry, krótka (D-096: 25 s × 4 s) | `swiat/dzungla_pas/krotki/` ← `python -B swiat/biomy/przycinarka.py` (wpis `dzungla` w `swiat/biomy/wymiary_pasa.json`) |
| Dane gry | `generuj_dane.py` → `zrodla/DanePotworowDzungli.luau`, `zrodla/DaneDzungli.luau`, `silnik/DaneWalkiDzungli.luau` |
| Przeciwnicy (silnik walki v3) | `przeciwnicy.py` — potwór lasu × k = 1,19 (kalkulator, Dżungla 17 → 23) + jedna cecha na gatunek |
| Modele i aktorzy | `swiat/postacie/{zwijogon,gebokwiat,kokosowy_silacz,pancernik_ruin,waz_stu_lian}.py`, `swiat/test_walki2/aktorzy_dzungli.py` |
| Budowa w Studio | `zbuduj.py` (budowniczy lasu-pasa na konfiguracji Dżungli) |
| Testy | `testy/test_dzungli.py` (offline), `testy/proba_play.py` (Play, J00–J14, `--sprawdz` bez Studio) |

## Strefy i potwory (krótki pas)
| Strefa | Gatunek | Klasa | Poziomy | Naraz / max | Cecha (inna niż w lesie i Bagnie) |
|---|---|---|---|---|---|
| z1 Polana Zwijogonów | Zwijogon | Zwiadowca | 17–19 | 3 / 4 | Skupienie + rozszarpanie, najczęstszy unik (+6 pp) |
| g1 Kwietnik Gębokwiatów | Gębokwiat | Mag | 19–21 | 3 / 4 | usypiający pyłek (lodowy pocisk: spowolnienie) |
| o1 Gaj Kokosów | Kokosowy Siłacz | Wojownik | 21–23 | 3 / 4 | Potężne cięcie (oba kokosy z góry) |
| t1 Ruiny Pancernika | Pancernik Ruin (rzadki) | Wojownik | 23 | 1 / 1 | Kamienna skóra i gruby Pancerz |
| strażnik, Krąg Stu Lian | Wąż Stu Lian | strażnik | 23 | 1 | jad (trucizna) i ukąszenie (krwawienie), częsty unik |

Razem ze strażnikiem: 8 / 11 / 14 potworów przy 1 / 8 / 20 graczach. W scalonych strefach poziomy są rozdawane po
miejscach (`poziomyPoMiejscach`, jak w lesie i Bagnie). Wygrane klas wzorcowych: `python -B swiat/dzungla_pas_gra/przeciwnicy.py`.

## Styki z innymi pakietami (dokładne podmiany)
- Bagno (`swiat/bagno_pas_gra`) już wskazywało następny biom `DzunglaPas` — przy stojącej Dżungli brama Bagna
  prowadzi dalej (ZaBrama Bagna znika); krótkie Bagno nie ma już grupy `ZapowiedzDzungli`.
- Teleport (`swiat/teleport_chmury/krainy.json`): kraina `dzungla` otwarta atrybutem `PokonalStraznikaBagna`,
  przybycie przez uchwyt `PrzeniesDoDzungli`.
- Dźwięk (`swiat/dzwiek_gra/ustawienia.json`): strefa `dzungla` (utwory lasu, ciszej) i odgłosy pięciu gatunków.
- Wskazówki (`swiat/wskazowki_gry`): biom `dzungla` i kroki Dżungli (logika w Luau i lustrze Pythona).
- Prototyp walki (`swiat/test_walki2/zrodla/SerwerWalki2.server.luau`): `DzunglaPasGra` na liście źródeł walk.
- Stan gracza (źródło łupu `DzunglaPasGra`) dopisuje agent stanu gracza; jajko Dżungli — agent petów (mapa ma
  stanowisko inkubatora: miejsce `jajko` i punkt E `Punkty/StanowiskoJajka`).

## Polecenia
```
python -B swiat/dzungla_pas_gra/generuj_dane.py            # dane (po zmianie mapy albo przeciwników)
python -B swiat/dzungla_pas_gra/testy/test_dzungli.py      # testy offline
python -B swiat/dzungla_pas_gra/zbuduj.py --sucho          # plan budowy bez Studio
python -B swiat/dzungla_pas_gra/zbuduj.py                  # buduje Workspace/DzunglaPasGra (Studio, tryb Edit)
python -B swiat/dzungla_pas_gra/testy/proba_play.py <folder poza repo>   # próba w Play (J00–J14)
python -B swiat/dzungla_pas_gra/testy/proba_widokow.py <folder poza repo> # bieg, szerokość, zrzuty miejsc (w_*.jpg)
```

## Co sprawdzone w grze (18.11.2026, 01:30–01:45, jeden gracz)
- `proba_play.py`: J00–J12 i J14 OK, J13 (koszt) do oceny: średnio 16,7 ms, p95 18,0 ms w Gaju Kokosów. Pierwszy
  przebieg padł, bo próba nie otwierała bramy lasu (serwer Bagna cofał gracza bez `PokonalStraznikaLasu` aż przed
  bramę lasu) — poprawione w próbie; panel testowy dostał poziom 30 (wygrana z Wężem w J10).
- `proba_widokow.py`: bieg z Tarasu do bramy **25,0 s** (398 st, 0 utknięć); szerokość pola na Tarasie **64,9 st =
  4,06 s**; przed bramą do Pustyni postać dochodzi tylko do v +15,8, bo stoi tam taras Świątyni Stu Lian (punkt
  orientacyjny areny strażnika) — to przeszkoda, nie węższe pole.
- Walki odbyły się na scenie zastępczej prototypu (arena Dżungli w `Workspace/ArenyWalki` jeszcze nie stała).
