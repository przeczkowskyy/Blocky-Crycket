---
name: marketing
description: Sesja marketingowa gier studia (Pet Arena i kolejne) — konta w mediach społecznościowych, klipy z wirtualnymi streamerami z Higgsfield, wideo i grafiki na stronę gry, twórcy, reklama. Użyj ZAWSZE, gdy Karol albo Paweł mówi „marketing”, „/marketing”, „TikTok”, „Instagram”, „Shorts”, „klipy”, „streamer AI”, „influencer”, „konto”, „promocja”, „reklama gry”, „miniatura”, „zwiastun” — także na początku nowej rozmowy poświęconej marketingowi.
---

# Marketing — sesja robocza

Osobna sesja, żeby nie mieszać marketingu z budową gry (prośba Karola z 21.11.2026). Odpowiadaj po polsku, krótko; koszty podawaj z góry.

## Na start (zawsze)
1. Przeczytaj `B&C/Marketing/00 Marketing.md` i `B&C/Marketing/Konto klipów z wirtualnymi streamerami — pomysł.md`.
2. Wiedza o rynku: `B&C/Wytwórnia/Algorytm Roblox 2026 — nowe zasady.md`, `B&C/Wytwórnia/Radar trendów.md`, `B&C/Wytwórnia/TizzyRBLX — zasady twórcy.md`; stan gry: `B&C/Gra/Pet Arena — projekt prototypu.md`.
3. Sprawdź `B&C/Produkcja/Pytania otwarte.md` (pytanie o wersję konta klipów) i `Rejestr decyzji.md` — co jest zdecydowane, a co tylko propozycją.
4. Przywitaj się jednym akapitem: co już ustalone, co jest pierwszym krokiem, ile to kosztuje.

## Zasady (twarde)
- **Jawność.** Realistyczne postacie AI oznaczamy jako AI (etykiety platform, opis konta); promocję własnej gry — jako naszą. Nie budujemy treści, które udają prawdziwych ludzi, cudze streamy, niezależne opinie, fałszywe recenzje ani sztuczny ruch (boty, kupione obserwacje). Jeśli prośba idzie w tę stronę — powiedz to wprost, zaproponuj jawną wersję (skill `krytyczne-myslenie`, D-114).
- **Żadnych prawdziwych osób i marek:** postacie nie mogą przypominać realnych streamerów, celebrytów ani cudzych bohaterów; bez cudzych klipów i muzyki. Cudze gry pokazujemy tylko z własnych nagrań rozgrywki.
- **Dzieci jako widzowie:** bez zachęt do wydawania pieniędzy, bez presji i straszenia, bez treści nieodpowiednich dla młodszych.
- **Higgsfield:** dźwięk i muzyka bez pytania; **obrazy i wideo dopiero po zgodzie Karola na koszt** — najpierw `higgsfield generate cost …`, podaj kredyty i ile zostanie. Skille: `higgsfield-generate`, `higgsfield-soul-id` (stała postać), `higgsfield-youtube-thumbnail`. W promptach do usług zewnętrznych bez danych osób z zespołu.
- **Publikuje człowiek.** Agent przygotowuje pliki, opisy i harmonogram; kont nie zakłada i nic nie wrzuca bez wyraźnego polecenia.
- **Pliki:** media poza repozytorium (repo jest publiczne): `%LOCALAPPDATA%\BlockyCrycket\marketing\`; w sejfie tylko plany, scenariusze i wyniki. Sekretów i danych kont nie zapisuj nigdzie w repo.
- **Sejf:** ustalenia zapisuj w `B&C/Marketing/` (status propozycja, dopóki człowiek nie zatwierdzi), decyzje w `Rejestr decyzji.md` z podpisem, wpis w `Dziennik zmian.md`; przed commitem `python tools/sejf_lint.py`; push od razu (D-070).

## Typowe prace
- Obsada wirtualnych streamerów (3–4 postacie: wygląd, charakter, sposób mówienia) i próbny klip — najpierw wycena w kredytach.
- Szablon klipu (rozgrywka + okienko postaci + napisy), scenariusze na tydzień, opis konta i etykiety.
- Wideo z czystej rozgrywki na kafelek gry w Roblox i obraz 16:9 (z demo pakietu gry: `swiat/pet_arena/testy/demo_wideo.py`).
- Plan próby i progi (ile klipów, jakie liczby oznaczają „skalujemy / poprawiamy / porzucamy”).
- Lista małych twórców do wczesnego dostępu.

## Źródło
Własny skill projektu (2026-11-21).
