# Karty okien agenta

Zakładka **Agent** w panelu ma pięć okien. Każde okno ma tu swoją kartę — plik po polsku, który można zmieniać jak zwykłą notatkę:

| Plik | Okno | Do czego |
|---|---|---|
| `ogolny.md` | Ogólny | wszystko inne; tu są też starsze rozmowy i rozmowy założone przez panel dla sesji głosowych |
| `balans.md` | Balans | statystyki, rzadkość, koszty, nagrody, tempo progresji |
| `swiat.md` | Świat | biomy, potwory, bossowie |
| `modele.md` | Modele | postacie, potwory i budynki z klocków |
| `wydanie.md` | Wydanie | publikacja, zasady Roblox, grupa, marketing, koszty (jedyne okno z wyszukiwaniem w sieci) |

## Jak zbudowana jest karta
```
---
nazwa: Balans                      ← nazwa okna w panelu
opis: Jedno zdanie dla człowieka.  ← widać je pod nazwą okna
narzedzia: sejf                    ← zestaw narzędzi: ogolny, sejf albo sejf_siec
---

# Okno agenta: Balans
## Rola                            ← kim agent jest w tym oknie
## Na start przeczytaj             ← notatki sejfu (ścieżki w `B&C/…` muszą istnieć — sprawdza to test)
## Jak odpowiadać                  ← krótko: pierwsze zdanie = odpowiedź, potem do 5 punktów
## Co i gdzie zapisywać            ← tylko propozycje, nigdy kanon ani ✅
## Narzędzia                       ← opis zestawu dla człowieka
```

- Wszystko pod nagłówkiem z kreskami trafia do **polecenia systemowego** każdej rozmowy w tym oknie, razem ze stałą regułą krótkich odpowiedzi z `panel/bc/agent.py` (`REGULA_STYLU`). Zmiana karty działa od następnej wiadomości, bez restartu panelu.
- Zestawy narzędzi (`ZESTAWY_OKIEN` w `panel/bc/agent.py`): `ogolny` — jak dotąd, zależnie od trybu (Plan / Praca / Auto), ale bez sieci; `sejf` — czytanie i zapis plików tylko w sejfie `B&C/` (Read, Glob, Grep, Edit i Write w `B&C/`), bez sieci, bez Roblox Studio i bez poleceń; `sejf_siec` — to samo plus WebSearch i WebFetch. Nieznana wartość = domyślny zestaw okna.
- Żaden agent panelu (ani okna, ani agent sesji głosowej) nie może zmieniać tych kart (zakaz `Edit(./panel/agenci/**)`), ani `.env`, `.claude/`, `CLAUDE.md`, `.mcp.json`, `.git/`, konfiguracji panelu, `B&C/.obsidian/` i `B&C/Źródła/`.
- Nowego okna nie doda się samym plikiem — lista okien jest w `panel/bc/agent.py` (`OKNA`).
- Szczegóły techniczne: `panel/README.md`, część „Agent”.
