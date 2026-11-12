---
status: propozycja
tags: [badania, technika, serwery, walki]
---
# Technika gry — serwery, światy, walki

> [!info] W skrócie
> Serwer na 1000 osób jest niemożliwy: publiczny limit to 200 graczy (700 tylko w becie), a gry z plotami trzymają 4–8 osób. Proponujemy hub z działkami na 16–20 graczy, a tłum na eventach zrobić przez wspólny stan wszystkich serwerów (MemoryStore + MessagingService). Walki liczy serwer jako „log walki”, a klient tylko go odtwarza: najpierw w 2D, potem w ViewportFrame albo jako lokalna cutscenka 3D, bez przenoszenia gracza. Wojny gildii między światami powinny działać asynchronicznie, jak w S&F, a eventy cykliczne konfigurujemy przez Experience Configs bez publikowania nowej wersji. Zapis przez ProfileStore, liczby jako mantysa i wykładnik.

## 1. Ilu graczy na serwer [20:13–21:13]
| Fakt | Wartość | Źródło |
|---|---|---|
| Maks. rozmiar serwera | 200 dla wszystkich twórców; 700 było wcześniej tylko w becie (ogłoszenie z 2023, stan obecny niezweryfikowany) | DevForum 2294621 |
| Sloty dla znajomych | do 20 przy ≤100 graczach, 20% przy >100 | DevForum 2294621 |
| Steal a Brainrot | 8 baz na serwer (źródło nie podaje limitu graczy; 8 graczy to wniosek, niezweryfikowane) | allthings.how |
| Grow a Garden | 4 graczy według poradnika (limit mógł się zmieniać; inne źródła podają 6, niezweryfikowane) | allthings.how |

- **Rekomendacja:** hub z działkami na **16–20** graczy, każda działka przypisana do slotu. Dla Twierdzy to zgodne z pomysłem z [21:29].
- **Tłum przy pecie lub bossie:** wspólny pasek HP bossa dla wszystkich serwerów (sorted map w MemoryStore) i ogłoszenie przez MessagingService. Gracz widzi licznik „4 312 graczy bije bossa” zamiast 1000 awatarów, którego żaden telefon by nie udźwignął.
- **Alternatywa:** hub bez działek na 30–40 graczy, a Twierdza w osobnym miejscu (pkt 5).
- **Ryzyko:** przy 20 graczach z działkami rośnie liczba części i pamięć na telefonie (pkt 9). Przy 4–8 graczach miasteczko wydaje się puste.

## 2. Gildie, wojny między serwerami, eventy globalne [23:59–25:49]
**Limity (wspólne dla silnika i Open Cloud):**
| Usługa | Limit | Źródło |
|---|---|---|
| MessagingService wysyłka | 600 + 240 × gracze serwera / min | usage-messaging |
| MessagingService odbiór na temat | 40 + 80 × liczba serwerów / min | usage-messaging |
| MessagingService wiadomość / temat | 1 KiB / 80 znaków; subskrypcje 20 + 8 × gracze | usage-messaging |
| MemoryStore pamięć | 64 KB + 1,2 KB × użytkownicy (cała gra) | memory-stores |
| MemoryStore zapytania | 1000 + 120 × CCU jednostek / min; wartość ≤ 32 KB; TTL ≤ 45 dni | memory-stores |
| Sorted map | klucz i klucz sortowania ≤ 128 znaków; wartość ≤ 32 KB; ≤ 1 mln elementów i 100 MB (limit elementów jest na stronie memory-stores, nie sorted-map) | sorted-map, memory-stores |
| Kolejka | ≤ 1 mln elementów i 100 MB na strukturę (memory-stores); limit 100 elementów w ReadAsync i niewidoczność 30 s: niezweryfikowane (nie ma ich na stronie MemoryStoreQueue) | memory-stores |
| DataStore | 4 194 304 znaków na klucz; klucz ≤ 50 znaków; limit serwera: odczyt 60 + 40 × gracze / min (limit całej gry: 300 + 40 × CCU) | error-codes-and-limits |
| OrderedDataStore | tylko liczby całkowite; strona ≤ 100; domyślny limit serwera: zapis 30 + 5 × gracze / min | OrderedDataStore |

**Architektura (rekomendacja):**
1. **Gildia** to klucz `Guild_<id>` w DataStore: członkowie, skarbiec, drzewko. Zapis przez `UpdateAsync`, bo pisze wiele serwerów naraz (best-practices).
2. **„Świat”** to logiczny shard, czyli pole `worldId` w gildii, a nie osobny serwer. Gracze z różnych światów mogą dzielić hub.
3. **Ranking miesiąca:** jedna sorted map na świat (`prestige_<world>_<YYYYMM>`), w której klucz sortowania to punkty. Serwery buforują przyrosty i wysyłają je co 30–60 s. Raz na godzinę wynik trafia do OrderedDataStore jako archiwum.
4. **Wojna międzyświatowa:** robimy ją **asynchronicznie**, jak walki gildii w S&F. O ustalonej godzinie UTC zadanie trafia do kolejki MemoryStore. Pierwszy serwer, który je odczyta, symuluje walkę z zapisanych statystyk członków (deterministycznie, z ziarnem losowania), zapisuje wynik do DataStore i ogłasza go przez MessagingService.
5. **„Admin abuse” / event na żywo:** `PublishAsync` z komendy admina albo Open Cloud `POST /cloud/v2/universes/{id}:publishMessage` z dashboardu. Klucz API ma zakres `universe-messaging-service:publish` i nie może trafić do repozytorium.
- **Alternatywa:** wojna na żywo w serwerze zarezerwowanym: `TeleportOptions.ReservedServerId` = GUID, a pierwszy teleport tworzy serwer (teleport-private-servers).
- **Ryzyko:** dokumentacja nie gwarantuje dostarczenia wiadomości (traktujemy je jako best-effort, niezweryfikowane), więc stan trzymamy w MemoryStore lub DataStore, a wiadomość służy tylko jako sygnał. Przy małym CCU limit pamięci MemoryStore jest mały, dlatego wpisy w rankingu muszą być krótkie.

## 3. Auto-walki: 2D, ViewportFrame czy cutscenka 3D [7:06–8:54, 16:17–17:17]
**Zasada nadrzędna:** walkę liczy **serwer** i wysyła klientowi log (`{tura, kto, akcja, obrażenia, krytyk}`). Klient go tylko odtwarza. Renderer można wtedy wymieniać bez zmian w balansie, a exploit nie zmieni wyniku (security-tactics).

| Wariant | Jak | Koszt | Uwagi |
|---|---|---|---|
| A. Ekran 2D | ScreenGui, portrety, tweeny, liczby obrażeń | najniższy | wierny S&F |
| B. ViewportFrame | modele w WorldModel; animacje działają, fizyka nie | średni | 3D „w okienku”, bez ruszania kamery świata |
| C. Lokalna cutscenka 3D | klient klonuje arenę z ReplicatedStorage, kamera `Scriptable` + tween CFrame, animacje przez Animator | najwyższy | inni gracze jej nie widzą, nie trzeba przenosić gracza |

- **Rekomendacja:** w MVP wariant A, a od razu po nim test C. Pojedynek PvP z [16:34] działa tak samo: serwer liczy jeden log, a obaj klienci odtwarzają go lokalnie w biomie, w którym stoją.
- **Koszt C:** na klasę około 6 animacji (idle, atak, czar, trafienie, śmierć, wygrana) plus 2–3 ujęcia kamery. Rig R15 pozwala użyć gotowych animacji, a Kot-Mag z własnym rigiem potrzebuje AnimationController + Animator (animation/using). Animacje są powiązane z doświadczeniami swojego właściciela (transfer-animations), choć Creator Hub pozwala je udostępniać współpracownikom i doświadczeniom (https://devforum.roblox.com/t/sharing-animation-assets-with-connections-and-groups/3892540). Gra i animacje powinny więc należeć do jednej grupy Roblox, bo jest nas dwóch.
- **Ryzyko:** cutscenka 30 razy dziennie męczy. Potrzebne są przyciski „pomiń” i „×2”, a przy auto-questach tryb samego wyniku.

**Plan testu (1–2 dni):** 1) model `CombatArena` w ReplicatedStorage; 2) dwa manekiny R15 i 3 animacje (atak, trafienie, śmierć); 3) LocalScript klonuje arenę daleko od miasta, ustawia `CameraType = Scriptable`, odtwarza ustalony log w 8–10 s w 3 ujęciach, a potem przywraca kamerę `Custom`; 4) ta sama walka w wariancie B; 5) pomiar na tanim Androidzie (FPS, pamięć w Developer Console) i decyzja obu twórców.

## 4. Strefy i biomy przez portale [25:53–26:46]
- **Rekomendacja:** dopóki biomy są małe, hub i pierwszy biom (las) trzymamy w **jednym miejscu** z StreamingEnabled (domyślnie: MinRadius 64, TargetRadius 1024; na telefony `StreamOutBehavior = Opportunistic`). Portal przenosi postać w obrębie miejsca.
- **Kolejne biomy jako osobne places** w tym samym universe, z teleportem `TeleportAsync` wywoływanym tylko z serwera. Dostęp ustawiamy na „Secure within universe only”.
- **Lochy:** przy auto-walce nie potrzebują osobnych serwerów. Mapa lochu jest wspólna, a stan pokonanych przeciwników jest per gracz: serwer go podaje, klient ukrywa pokonanych. Lochy grupowe później zrobimy w serwerach zarezerwowanych.
- **Ryzyko:** każdy teleport wydłuża czas wejścia (performance/design), dane teleportu są jawne dla klienta, a postęp trzeba zapisać przed przejściem.

## 5. Działki w hubie a osobne miejsce na Twierdzę [21:29–22:48]
| | Działki w hubie (rekomendacja) | Osobne miejsce |
|---|---|---|
| Społeczność | sąsiedzi widzą twierdze, efekt „pochwal się” | wizyty tylko przez teleport |
| Wydajność | 20 działek naraz w pamięci | jedna działka |
| Implementacja | slot przy wejściu, budowa z zapisu, czyszczenie przy wyjściu | serwer zarezerwowany per gracz (GUID w profilu) |

- Każda działka to Model w trybie `Atomic` (streaming), a budynki to te same meshe w kolejnych poziomach.
- **Rajdy na wioski** robimy asynchronicznie z zapisanego stanu, więc obrońca nie musi być online.
- **Ryzyko:** skok liczby części przy maksymalnie rozbudowanych twierdzach, dlatego potrzebny jest limit części na działkę (pkt 9).

## 6. Teleport z mapy 2D, sprint, wierzchowce [2:22–4:55]
- **Mapa 2D:** przycisk wysyła RemoteEvent, a serwer sprawdza cel z białej listy, cooldown oraz warunek „poziom ≥ X **albo** gamepass” (`UserOwnsGamePassAsync`). Potem przenosi postać przez `PivotTo`. W obrębie jednego miejsca nie potrzeba TeleportService.
- **Sprint:** Shift zmienia `WalkSpeed` (domyślnie 16, niezweryfikowane na stronie Humanoid). To właściwość replikowana z klienta, którą da się zmienić lokalnie (Humanoid), więc serwer tylko zgrubnie sprawdza prędkość i nie bierze jej pod uwagę w nagrodach.
- **Wierzchowce:** mnożnik prędkości, model przyspawany do postaci i animacja siedzenia, bez fizycznych pojazdów. Wierzchowiec może też skracać czas questów, jak stajnia w S&F (zob. [[Karczma (Questy)]]).

## 7. Zapis, exploity, duże liczby, postęp offline
- **Zapis:** ProfileStore (loleris, Apache-2.0) daje blokadę sesji (chroni przed duplikacją przy przejściu między serwerami), autozapis co 300 s i przyspiesza konflikty przez MessagingService. Jeden profil na gracza, czyli jeden klucz (limit 4 194 304 znaków na klucz, error-codes-and-limits). Każdy zakup w `ProcessReceipt` trafia do profilu z identyfikatorem paragonu, żeby nie zaliczyć go dwa razy.
- **Exploity:** serwer jest jedynym źródłem prawdy (złoto, drop, czasy questów, wyniki walk). Każdy argument RemoteEvent sprawdzamy (typ, zakres, NaN) i ograniczamy częstotliwość. Engine'owy model „server authority” jest przeznaczony dla gier akcji, my go nie potrzebujemy.
- **Liczby:** `number` to double z około 15 cyframi precyzji, a liczby całkowite są dokładne do ±2^53 (numbers, configs). Waluty inkrementalne zapisujemy jako `{m, e}` (mantysa i wykładnik) i formatujemy jako K, M, B, T, aa…. OrderedDataStore przyjmuje tylko liczby całkowite, więc do rankingu zapisujemy `floor(log10(x) × 1000)`.
- **Offline:** przy wejściu `Δ = os.time() − lastSeen` (czas serwera), z limitem 8–12 h i mnożnikiem do zwiększenia za płatnością. `DateTime.now()` na kliencie korzysta z zegara urządzenia, który gracz może przestawić.

## 8. Eventy cykliczne (weekend, środa)
- **Rekomendacja:** Experience Configs. Wartość JSON (do 100 000 znaków), np. `{"weekend":{"questTimeMult":0.7}, "sroda":{"epicEvery":2}}`. „Publish now” rozsyła ją w 15 s – 1 min, bez nowej wersji gry. Serwer subskrybuje `ConfigSnapshot.UpdateAvailable` i wywołuje `Refresh()`.
- **Kalendarz:** okna liczymy w UTC na serwerze (`DateTime:FormatUniversalTime("d", ...)` daje dzień tygodnia 0–6). Granice podajemy w UTC, np. „sobota 00:00 – niedziela 23:59 UTC”.
- **Limity:** 1000 aktywnych configów oraz 100 warunków na grę i 20 na klucz. ConfigService działa tylko na serwerze, a `GetConfigAsync` rzuca błąd, gdy nie ma żadnej konfiguracji, więc w kodzie trzymamy wartości domyślne. Status beta jest niezweryfikowany (strona configs go nie podaje). Zachowanie `GetConfigAsync` bez konfiguracji też nie jest potwierdzone w dokumentacji klas (niezweryfikowane).
- **Alternatywa:** ręczny przełącznik przez MessagingService albo Open Cloud (pkt 2).

## 9. Budżet wydajności: leśna baza z karczmą na telefon
**Oficjalne:** budżet klatki to 16,67 ms przy 60 FPS. W przykładzie urządzenia bazowego mieszczą się poniżej 1000 draw calli i 1 mln trójkątów (to przykład, nie limit). Jeden mesh może mieć najwyżej 20 000 trójkątów. Tekstury zwykle do 512×512, drobne do 256×256 (1024² zajmuje 4 razy więcej pamięci niż 512²). Wbudowane materiały są tańsze niż własne tekstury. Kolizja `Box`, a części dekoracyjne z `CanCollide/CanTouch/CanQuery = false`. Wszystko statyczne kotwiczymy, a statyczni NPC nie potrzebują Humanoida. Emulator w Studio nie odzwierciedla pamięci telefonu. Dokumentacja nie podaje progów liczby części ani pamięci. Limity tekstur 512/256 px nie występują na stronach specifications ani design (niezweryfikowane); to samo dotyczy rad o kolizji `Box` i `CanCollide/CanTouch/CanQuery` (niezweryfikowane na stronie design).

**Nasza propozycja do zmierzenia (to nie są limity platformy):** widoczna scena do około 300 tys. trójkątów i około 500 draw calli. Drzewa jako 3–5 meshy powielanych setki razy. Karczma jako jeden zestaw modułów. Działka do około 1500 części przy maksymalnym poziomie. Mierzymy na najtańszym dostępnym Androidzie w Developer Console (LuaHeap, InstanceCount) przy 20 graczach.

## Powiązane
[[Koncepcja i Core Loop]] · [[Karczma (Questy)]] · [[Twierdza (Tycoon)]] · [[Arena (PvP)]] · [[Pety]] · [[System RPG]] · [[Kot-Mag]] · [[Rojo i struktura projektu]] · [[Pipeline assetów]] · [[Roadmapa]] · [[Pytania otwarte]] · [[Shakes & Fidget — rozbiór mechanik]] · [[Retencja i monetyzacja — co wolno i co działa]] · [[Rynek Roblox i konkurencja]]

## Weryfikacja
Sprawdzono 2026-11-12 w dokumentacji Roblox i na stronach źródłowych.
- Serwer 200 graczy, sloty ≤100 -> 20, >100 -> 20% -> potwierdzone -> https://devforum.roblox.com/t/experience-join-improvements-server-size-join-queues-and-social-slots-reservations/2294621
- 700 graczy tylko w becie -> poprawione (było, teraz 200 dla wszystkich; stan obecny niezweryfikowany) -> ten sam wątek
- Limity MessagingService (600+240, 40+80, 80 znaków, 1 KiB, 20+8) -> potwierdzone -> https://create.roblox.com/docs/cloud/guides/usage-messaging
- MemoryStore 64 KB + 1,2 KB, 1000 + 120 × CCU, 32 KB, TTL 45 dni -> potwierdzone -> https://create.roblox.com/docs/cloud-services/memory-stores
- Sorted map 128 znaków, 1 mln elementów -> potwierdzone (limit elementów na stronie memory-stores) -> https://create.roblox.com/docs/cloud-services/memory-stores/sorted-map
- Kolejka: ReadAsync ≤ 100, niewidoczność 30 s -> niezweryfikowane (nie ma na stronach docs) -> https://create.roblox.com/docs/reference/engine/classes/MemoryStoreQueue
- DataStore 4 194 304 znaków, klucz 50, 60+40, OrderedDataStore 30+5, strona ≤100 -> potwierdzone (doprecyzowano: serwer vs gra) -> https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
- Experience Configs 100 000 znaków, 1000 configów, 100/20 warunków, 15 s – 1 min, UpdateAvailable/Refresh -> potwierdzone -> https://create.roblox.com/docs/production/configs
- Steal a Brainrot „8 graczy” -> poprawione (źródło mówi tylko o 8 bazach) -> https://allthings.how/steal-a-brainrot-roblox-efficient-stealing-events-and-rebirths
- Grow a Garden 4 graczy -> potwierdzone wg poradnika -> https://allthings.how/grow-a-garden-player-count-server-limit-and-record-highs/
- StreamingMinRadius 64, TargetRadius 1024, Opportunistic, Atomic -> potwierdzone -> https://create.roblox.com/docs/workspace/streaming
- ProfileStore: Apache-2.0, autozapis 300 s, blokada sesji, MessagingService -> potwierdzone -> https://github.com/MadStudioRoblox/ProfileStore , https://madstudioroblox.github.io/ProfileStore/
- ReservedServerId = GUID, pierwszy teleport tworzy serwer -> potwierdzone -> https://create.roblox.com/docs/projects/teleport-private-servers
- Mesh ≤ 20 000 trójkątów -> potwierdzone -> https://create.roblox.com/docs/art/modeling/specifications
- 16,67 ms, <1000 draw calli, 1 mln trójkątów (przykład) -> potwierdzone -> https://create.roblox.com/docs/performance-optimization/design
- Tekstury 512/256 oraz zalecenia kolizji -> niezweryfikowane (brak na sprawdzonych stronach)
- Animacje tylko u właściciela doświadczenia -> poprawione (są też udostępnianie i transfer) -> https://create.roblox.com/docs/projects/transfer-animations
- AnimationController + Animator dla rigów bez Humanoida -> potwierdzone -> https://create.roblox.com/docs/animation/using
- Brak gwarancji dostarczenia MessagingService -> niezweryfikowane (dokumentacja milczy) -> https://create.roblox.com/docs/reference/engine/classes/MessagingService
- WalkSpeed domyślnie 16 -> niezweryfikowane na stronie Humanoid

## Źródła
Dostęp 2026-11-12.
- https://create.roblox.com/docs/cloud/guides/usage-messaging
- https://create.roblox.com/docs/reference/engine/classes/MessagingService
- https://create.roblox.com/docs/cloud-services/memory-stores
- https://create.roblox.com/docs/cloud-services/memory-stores/sorted-map
- https://create.roblox.com/docs/reference/engine/classes/MemoryStoreQueue
- https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
- https://create.roblox.com/docs/cloud-services/data-stores/best-practices
- https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore
- https://create.roblox.com/docs/projects/teleport
- https://create.roblox.com/docs/projects/teleport-private-servers
- https://create.roblox.com/docs/workspace/streaming
- https://create.roblox.com/docs/workspace/camera
- https://create.roblox.com/docs/ui/viewport-frames
- https://create.roblox.com/docs/reference/engine/classes/WorldModel
- https://create.roblox.com/docs/animation/using
- https://create.roblox.com/docs/animation/editor
- https://create.roblox.com/docs/projects/transfer-animations
- https://create.roblox.com/docs/production/configs
- https://create.roblox.com/docs/reference/engine/classes/ConfigService
- https://create.roblox.com/docs/reference/engine/datatypes/DateTime
- https://create.roblox.com/docs/luau/numbers
- https://create.roblox.com/docs/scripting/security/security-tactics
- https://create.roblox.com/docs/projects/server-authority
- https://create.roblox.com/docs/reference/engine/classes/Humanoid
- https://create.roblox.com/docs/performance-optimization/design
- https://create.roblox.com/docs/performance-optimization/improve
- https://create.roblox.com/docs/art/modeling/specifications
- https://madstudioroblox.github.io/ProfileStore/
- https://github.com/MadStudioRoblox/ProfileStore
- https://devforum.roblox.com/t/experience-join-improvements-server-size-join-queues-and-social-slots-reservations/2294621
- https://allthings.how/steal-a-brainrot-roblox-efficient-stealing-events-and-rebirths
- https://allthings.how/grow-a-garden-player-count-server-limit-and-record-highs/
