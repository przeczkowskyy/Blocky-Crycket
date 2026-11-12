---
status: propozycja
tags: [badania, monetyzacja, retencja, zasady-roblox]
---
# Retencja i monetyzacja — co wolno i co działa

> [!info] W skrócie
> Algorytm Robloxa liczy retencję, zaangażowanie i monetyzację **na gracza**, więc gra, która trzyma jakością (krótka pętla, rosnące liczby, kolekcja, wspólna gra), zyskuje w rekomendacjach. Pieniądze robią wygoda, kosmetyka i subskrypcja, a nie hazard.
> Losowanie za Robuxy (koło, reroll sklepu, jajka) jest dozwolone tylko z ujawnionymi szansami i przez PolicyService. Symulowany hazard (stawiasz walutę, żeby wygrać więcej) jest zakazany.
> Projekt unijnego Digital Fairness Act zakłada zakaz płatnych loot boxów i pay-to-win dla nieletnich. Przychód gry nie może więc stać na płatnej losowości.
> Większość pomysłów z rozmowy się broni. Do przeróbki: płatny reroll sklepu, płatne tokeny koła i „legendarka co godzinę” liczona zegarem.

## Kto gra i co z tego wynika
- Wśród graczy po weryfikacji wieku 35% ma mniej niż 13 lat, 38% ma 13–17 lat, a 27% to dorośli (Q2 2026). [S1]
- Od 16.06.2026 konta dzielą się na Roblox Kids (5–8), Roblox Select (9–15) i Roblox (16+). Do Kids/Select trafia gra z oceną Minimal/Mild (Select także Moderate). Wymogi: weryfikacja wieku i 2FA twórcy, 2 miesiące Plus/Premium albo zwrotna opłata oraz 250 unikalnych odtworzeń (plays) od mocno zaangażowanych graczy w 60 dni (nie „sesji”). [S2][S3]
- Bez wypełnionego kwestionariusza dojrzałości treści gra jest ograniczona dla wszystkich graczy. [S4]
- **Wniosek:** nasz rdzeń to 9–15 lat, czyli Roblox Select. Celujemy w ocenę Mild (komiksowa przemoc) i projektujemy tak, jakby kupował rodzic.

## Co trzyma graczy
Teoria samodeterminacji wiąże przyjemność z gry i powroty z poczuciem **kompetencji, autonomii i więzi**. [S5] Rekomendacje Robloxa liczą na gracza qualified play sessions, retencję, monetyzację i wspólną grę; liczy się „wartość sesji”, nie jej długość. [S6][S7]

| Mechanika | Dlaczego działa | U nas |
|---|---|---|
| Krótka pętla (sekundy–minuty) | szybki sygnał kompetencji | quest 30–60 s na start, skracany przez rozgłos strefy ([[Karczma (Questy)]]) |
| Widoczne liczby | progres widać od razu | +DMG, +gold/s, skróty 1.2K/3.4M, „liczby lecą” po walce |
| Kolekcja | cel na długo, autonomia | pety, zestawy ekwipunku, księga potworów |
| Rebirth / prestiż | reset z trwałym mnożnikiem odnawia pętlę | prestiż twierdzy i strefy |
| Postęp offline | powód, żeby wrócić | twierdza i ekspedycje petów liczą offline, z limitem |
| Eventy i aktualizacje | odświeżają treść | Grow a Garden wydawał aktualizacje co 5–7 dni [S8] |
| Gra społeczna | więź; co-play to sygnał algorytmu [S6] | wspólne bossy strefy, party do lochów, gildie później |
| Cele dnia i serie | nawyk | 3 cele dzienne; seria bez kary za przerwę (opis niżej) |

**Uwaga do rozmowy [27:24–27:59]:** racja, 30 grzybów nudzi, a liczby wciągają. Ale gry na samym trendzie gasną: CCU Steal a Brainrot spadło o 80% w dwa tygodnie po szczycie. [S8] Liczby przyciągają, a zatrzymują kolekcja, wspólna gra i świeża treść.

## Monetyzacja — narzędzia
| Narzędzie | Ile trafia do nas | Uwagi |
|---|---|---|
| Gamepass / developer product | ok. 70% Robuxów (niezweryfikowane: strona S9 nie podaje procentu) [S9] | ceny regionalne i Managed pricing (testy cen) [S9] |
| Subskrypcja w grze | 70%; w walucie lokalnej 70% w 1. miesiącu, potem 100% [S10] | progi od $2.99 do $14.99 albo co najmniej 49 R$. Korzyści muszą działać przez cały okres i nie można ich warstwować (brak Bronze/Silver/Gold) [S10] |
| Creator Rewards | 5 R$ za aktywnie wydającego gracza (wydał ≥$9.99 w 60 dni; ≥10 min, jedna z 3 pierwszych gier dnia) + 35% z pierwszych $100 zakupów nowego/powracającego gracza w jego pierwszych 60 dniach [S11] | od 24.07.2025 zamiast Engagement Based Payouts [S11] |
| Reklama nagradzana | stawka EPM za 1000 wyświetleń [S12] | **tylko gracze 13+**, gra z ≥2000 unikalnych odwiedzających miesięcznie. Nagrodą jest developer product, nielosowy i bez Robuxów; reklama nie może blokować postępu [S12][S13] |
| DevEx | $0.0038 za 1 R$ od 5.09.2025 [S14] | od 8.06.2026 stawka wyższa o 42% dotyczy tylko wydatków graczy 18+ z USA po weryfikacji wieku, w kwalifikujących się grach (m.in. tylko awatary R15); nie naszej grupy [S14] |

**Benchmarki:** Roblox nie publikuje ogólnych progów D1/D7/D30. Panel Analytics porównuje grę z podobnymi tytułami w przedziale P50–P90. Roblox radzi najpierw dociągnąć D1/D7, a dopiero potem płacić za ruch. [S15] Według zewnętrznego serwisu typowy tycoon lub incremental ma D1 20–28% i D7 12–18% (metodologia nieopisana, niezweryfikowane). [S16]

## Granice — zasady Robloxa
| Zasada | Co to znaczy dla nas |
|---|---|
| Symulowany hazard zakazany: nie wolno stawiać Robuxów, przedmiotów ani waluty o wartości [S17] | żadnego „postaw 100 golda, wygraj 1000” ani ruletki z mnożnikiem stawki |
| Płatne przedmioty losowe (paid random items): szanse w procentach sumujące się do 100%, pokazane przed zakupem. Link musi mieć opis słowny, sama ikona (i) nie wystarcza. Dotyczy też tokenów, rerolli i biletów kupionych za Robuxy. Mikstury szczęścia i system litości (pity) to „modyfikatory prawdopodobieństwa”, które też trzeba ujawnić [S18] | koło, reroll sklepu, płatne jajka i mikstury szczęścia podlegają tym zasadom |
| Żaden wynik nie może oznaczać zwykłej straty zapłaty [S17] | każdy spin daje przedmiot |
| `ArePaidRandomItemsRestricted` = true oznacza, że trzeba dać darmową ścieżkę albo stałą kolejność, sprzedać konkretny przedmiot albo ukryć mechanikę. `IsPaidItemTradingAllowed` = false oznacza zakaz handlu płatnymi przedmiotami [S18] | jeden moduł polityk na serwerze, sprawdzany przy każdym zakupie i wymianie |
| Darmowe losowania bez waluty nie wymagają ujawnienia szans [S18] | i tak je pokazujemy, bo to tanie zaufanie |
| Zakaz wprowadzających w błąd treści używanych do monetyzacji lub zaangażowania [S17] | żadnych fałszywych liczników, fałszywej rzadkości ani „ostatniej szansy” |

## Granice — prawo 2024–2026
- **USA:** w 2022–2023 Epic zgodził się na $245 mln zwrotów za ciemne wzorce (nakaz FTC sfinalizowany w 03.2023; osobno $275 mln kary COPPA), czyli mylące przyciski i zakupy dzieci bez zgody rodziców. [S19] W 01.2025 HoYoverse zawarł ugodę na $20 mln za loot boxy sprzedawane dzieciom, ukryte koszty i mylące szanse; poniżej 16 lat obowiązuje teraz zgoda rodzica. [S20] Znowelizowana reguła COPPA weszła w życie 23.06.2025, a termin zgodności upłynął 22.04.2026. [S21] Stany pozywają Roblox; trzy z nich (Wirginia Zachodnia, Alabama, Nevada) zawarły ugody na łącznie $35,8 mln (04.2026). [S22]
- **UE:** zasady sieci CPC z 03.2025 wymagają ceny w prawdziwych pieniądzach, zakazują presji na kupowanie nadmiaru waluty i nakazują szczególną ochronę dzieci. [S23] Przeciek projektu Digital Fairness Act zakłada zakaz płatnych loot boxów i pay-to-win dla nieletnich, wyłączoną domyślnie walutę u dzieci (do zgody rodzica) i zakaz fałszywej rzadkości. Prezentację zapowiedziano na „środę” (czyli 11.11.2026; daty źródło nie podaje wprost); treść końcowa niezweryfikowana. [S24][S25]
- **Belgia:** od 2018 płatne loot boxy uznaje się za nielegalny hazard. **Holandia:** w 2022 sąd uznał, że loot boxy w FIFA nie naruszają prawa hazardowego. [S26][S27]
- **Wielka Brytania:** samoregulacja (zasady Ukie z 2023): nieletni nie kupują loot boxów bez zgody rodzica, a szanse muszą być jasno podane. [S28]

## Pomysły z rozmowy — werdykt
| Pomysł | Koszyk | Uzasadnienie i zamiennik |
|---|---|---|
| Koło fortuny („Doktor Labubu”): darmowy spin co godzinę + płatne tokeny | darmowe: **ROB**; tokeny za R$: **OSTROŻNIE** | Tokeny to paid random item, więc wymagają szans, PolicyService i nagród bez Robuxów. Pod DFA tokeny za R$ mogą zniknąć dla nieletnich, dlatego wolimy spiny zdobywane w grze, a VIP może dawać +1 darmowy spin dziennie (też z szansami). Nazwa Labubu to cudza marka, więc trzeba wymyślić własną postać. |
| Sklep odświeżany co 5 min + tokeny odświeżenia za R$ | odświeżanie: **ROB**; reroll za R$: **OSTROŻNIE → zamienić** | Płatny reroll to wprost wymieniony paid random item. Zamiast niego: tokeny tylko z gry, do tego płatne „przypięcie slotu” albo zakup konkretnego przedmiotu po stałej cenie. |
| Gwarantowany epik co 30 min, legendarka co godzinę | **ROB** po zmianie | Licznik według zegara uczy kampienia AFK i psuje ekonomię. Lepiej licznik litości liczony aktywnością („legendarka najpóźniej w 20. odświeżeniu”), widoczny w UI, oraz godzinny boss strefy dla całego serwera. Jeśli licznik działa przy płatnych losowaniach, trzeba go ujawnić. |
| Teleport za R$ albo od poziomu | **ROB** | Obie ścieżki: darmowo już w pierwszej sesji, pass daje wygodę i wierzchowiec. Nie utrudniać celowo chodzenia, żeby sprzedać teleport. |
| Najemnik automatyzujący questy | **ROB** | Zarabiany złotem na opanowanych strefach. Pass może dodać drugi slot, ale nie siłę w PvP ([[Arena (PvP)]]), bo pay-to-win dla nieletnich jest na celowniku DFA. Pogodzić z D-004 w [[Rejestr decyzji]]. |
| Jajka wylęgane czasowo | z gry: **ROB**; jajka/przyspieszenie za R$: **OSTROŻNIE** | Jajko za R$ to paid random item. Pierwsze wylęgi trwają sekundy, dłuższe idą offline; przyspieszenie bez wyskakujących okienek. |
| Eventy tygodniowe (środa, weekend −30% czasu, walki petów, globalne „admin abuse”) | **ROB** | Najtańsza retencja. Nagrody eventu zdobywa się grą, a pass tylko je przyspiesza. |
| Gra pod duże liczby | **ROB** | Przy tym rebirth z mnożnikiem i porządne formatowanie liczb. |
| „Kradnie kartę mamusi” [27:49] | **NIE RÓB** | Projektowanie pod nieautoryzowane zakupy dzieci to wprost sprawa Epic ($245 mln). [S19] |
| „Gambling w karczmie” [6:56] | stawka: **NIE RÓB**; losowanie za złoto: **ROB** | Losowanie za złoto zdobyte w grze nie jest paid random item, o ile złota nie da się kupić za R$. |

## Trzy koszyki
**ROB:** gamepassy wygody (teleport, drugi najemnik, większy plecak), kosmetyka (skórki petów, wierzchowce, aury), subskrypcja VIP (+1 spin, +10% golda; korzyści stałe), jednorazowy pakiet startowy bez licznika, mnożniki czasowe bez wpływu na PvP, eventy, cele dnia, rebirth, linki udostępniania (Creator Rewards). *Dlaczego:* brak zwrotów i ryzyka moderacji, model przetrwa DFA.

**OSTROŻNIE:** wszystko losowe za R$ albo za walutę kupioną za R$ (koło, jajka, mikstury szczęścia) wymaga panelu szans, PolicyService i nagród bez Robuxów. Reklama nagradzana: filtr 13+ i wyłącznie developer products. Handel petami: `IsPaidItemTradingAllowed` i ochrona przed oszustami. *Dlaczego:* jeden błąd to zgłoszenie, blokada w części krajów albo zdjęcie mechaniki.

**NIE RÓB:** zakładów walutą, fałszywych liczników i rzadkości, ofert wyskakujących po porażce, „przegraj albo zapłać”, ukrywania ceny w walutach pośrednich, utraty serii za brak zakupu, sprzedaży przewagi w PvP. *Dlaczego:* łamią zasady Robloxa [S17], zasady CPC [S23] i projekt DFA [S24], grożą usunięciem gry i zwrotami, a nieufność rodziców obniża konwersję, która sama jest sygnałem rekomendacji [S6].

## Plan retencji D1 / D7 / D30
| Moment | Co gracz dostaje |
|---|---|
| 0–60 s | wybór bohatera ([[Selektor bohatera]]), jedna walka z wielkimi liczbami, pierwszy przedmiot, strzałka do Karczmy |
| 10 min | 5–8 questów po 30 s, poziom 5, pierwsze jajko i pet, darmowy spin koła, teleport odblokowany, pierwszy darmowy cel dnia zaliczony |
| Dzień 1 | strefa 2, rozgłos skraca questy, 3 cele dzienne, pierwszy loch na Easy, start twierdzy offline („wróć jutro po plon”) |
| Tydzień 1 | najemnik w opanowanej strefie, 3–5 petów, pierwszy event tygodniowy, seria logowań z nagrodą 7. dnia (luka 1 dnia wybaczona), Arena, zaproszenie do party |
| Dzień 30 | prestiż strefy/twierdzy, kolekcja petów do ok. 50%, gildie (aktualizacja), ranking sezonowy z nagrodami kosmetycznymi |

KPI: D1 i D7 na poziomie co najmniej P50 podobnych gier przed płaceniem za reklamę. [S15]

## Weryfikacja
Sprawdzono 2026-11-12 w źródłach pierwotnych.
- Udział wiekowy 35/38/27 (Q2 2026) -> potwierdzone (dla 7 dni do 30.06.2026; te same wartości co w danych do 31.01.2026) -> S1 (przez wyszukiwanie wyników)
- Kids 5–8 / Select 9–15 / 16+, oceny, weryfikacja wieku, 2FA, Plus/Premium 2 mies. -> potwierdzone -> S3
- „250 unikalnych sesji w 60 dni” -> poprawione na „250 unikalnych odtworzeń (plays) od mocno zaangażowanych graczy” -> S3
- Subskrypcje: 70%, lokalna waluta 70% potem 100%, progi $2.99–$14.99, min. 49 R$, brak warstw -> potwierdzone -> S10
- Creator Rewards: 5 R$, 35% z pierwszych $100, start 24.07.2025, zastąpiło EBP -> potwierdzone; dopisano warunek Active Spender ($9.99/60 dni) i okno 60 dni -> S11
- Reklama nagradzana: 13+, ≥2000 odwiedzających/mies., developer product, nielosowy, bez Robuxów -> potwierdzone (strona mówi „Be 13+”, bez rozstrzygnięcia, czy chodzi o widza) -> S12
- Paid random items: 100%, (i) niewystarczające, pity/luck jako modyfikatory, flagi PolicyService -> potwierdzone -> S18
- Gamepass/dev product „ok. 70%” -> niezweryfikowane (strona nie podaje liczby) -> S9
- DevEx $0.0038 od 5.09.2025 -> potwierdzone; zastrzeżenie o 18+ US poprawione i uzupełnione (+42% od 8.06.2026, R15) -> S14
- Grow a Garden update co 5–7 dni; Steal a Brainrot CCU −80% w 2 tyg. -> potwierdzone -> S8
- Epic $245 mln -> potwierdzone, doprecyzowano daty i osobne $275 mln -> S19
- HoYoverse $20 mln, zgoda rodzica <16, styczeń 2025 -> potwierdzone (część źródeł pisze o braku zatwierdzenia sądowego w chwili ogłoszenia) -> S20
- COPPA „od 22.04.2026” -> poprawione: w życie 23.06.2025, termin zgodności 22.04.2026 -> S21
- Ugody stanów $35,8 mln -> potwierdzone (3 stany: WV $11,1 mln, AL $12,2 mln, NV $12,5 mln) -> S22
- DFA: zakaz płatnych loot boxów i pay-to-win dla nieletnich -> potwierdzone jako treść przecieku, nie prawo -> S24
- Benchmark D1 20–28% / D7 12–18% -> niezweryfikowane (już oznaczone; nie sprawdzano ponownie) -> S16

## Powiązane
[[Koncepcja i Core Loop]] · [[Karczma (Questy)]] · [[Twierdza (Tycoon)]] · [[Pety]] · [[System RPG]] · [[Arena (PvP)]] · [[HUD]] · [[Rejestr decyzji]] · [[Pytania otwarte]] · [[Rynek Roblox i konkurencja]] · [[Shakes & Fidget — rozbiór mechanik]] · [[Technika gry — serwery, światy, walki]]

## Źródła
Dostęp: 2026-11-12.
- [S1] https://s27.q4cdn.com/984876518/files/doc_financials/2026/q2/Roblox-Q2-2026-Earnings-Shareholder-Letter.pdf ; https://about.roblox.com/newsroom/2026/02/moving-beyond-self-reported-age
- [S2] https://about.roblox.com/newsroom/2026/06/age-based-roblox-kids-and-select-accounts-now-globally-available
- [S3] https://create.roblox.com/docs/production/publishing/kids-and-select
- [S4] https://create.roblox.com/docs/production/promotion/content-maturity
- [S5] https://link.springer.com/article/10.1007/s11031-006-9051-8 (Ryan, Rigby, Przybylski 2006)
- [S6] https://create.roblox.com/docs/discovery ; https://create.roblox.com/docs/discovery-faq.md
- [S7] https://www.deconstructoroffun.com/blog/how-to-build-a-real-business-on-roblox-in-2026
- [S8] https://rolearn.dev/insights/grow-a-garden-ccu-record-analysis
- [S9] https://create.roblox.com/docs/production/monetization ; https://devforum.roblox.com/t/introducing-regional-pricing-for-developer-products/3971235
- [S10] https://create.roblox.com/docs/production/monetization/subscriptions
- [S11] https://create.roblox.com/docs/en-us/creator-rewards.md
- [S12] https://create.roblox.com/docs/en-us/production/promotion/rewarded-video-ads.md
- [S13] https://devforum.roblox.com/t/new-advertising-policies-standards/4527365 ; https://create.roblox.com/docs/production/promotion/ad-integrations.md
- [S14] https://gam3s.gg/news/roblox-increases-creator-payouts ; https://about.roblox.com/newsroom/2026/04/roblox-fuels-high-fidelity-games-over-18-players-increases-qualifying-devex-rate-42
- [S15] https://create.roblox.com/docs/production/analytics/retention ; https://devforum.roblox.com/t/analytics-view-retention-by-acquisition-source-and-select-your-benchmark-set/4010157
- [S16] https://rowatcher.com/news/retention-benchmarks-by-roblox-genre-what-good-actually-looks-like
- [S17] https://about.roblox.com/community-standards
- [S18] https://create.roblox.com/docs/production/monetization/paid-random-items
- [S19] https://www.ftc.gov/node/80648 ; https://www.pbs.org/newshour/amp/nation/fortnite-maker-epic-games-to-settle-ftc-case-pay-520-million-in-penalties-and-refunds
- [S20] https://ftc.gov/business-guidance/blog/2025/01/level-tips-businesses-ftcs-settlement-genshin-impact-developer-hoyoverse
- [S21] https://www.davispolk.com/insights/client-update/ftc-prioritizes-coppa-enforcement-new-compliance-obligations-take-effect
- [S22] https://amp.insurancejournal.com/news/southeast/2026/04/23/866879.htm ; https://pluribusnews.com/news-and-events/more-than-a-dozen-states-target-roblox-over-child-safety-concerns/
- [S23] https://www.zwillgen.com/gaming/cpcn-announces-virtual-currency-consumer-protection-guidelines/ ; https://connectontech.bakermckenzie.com/?p=5083
- [S24] https://euronews.com/2026/11/09/eu-to-blacklist-ten-manipulative-online-design-traps-leaked-draft-shows
- [S25] https://www.pocketgamer.biz/leaked-eu-proposal-targets-loot-boxes-and-addictive-game-design
- [S26] https://www.pcgamer.com/belgiums-gambling-commission-rules-against-loot-boxes-in-overwatch-fifa-18-and-csgo/
- [S27] https://www.scl.org/12540-loot-boxes-are-not-gambling-under-dutch-law/
- [S28] https://www.gov.uk/guidance/loot-boxes-in-video-games-update-on-improvements-to-industry-led-protections
