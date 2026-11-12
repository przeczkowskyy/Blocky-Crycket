---
status: do-decyzji
tags: [ui]
---
# Okno Karczmy (TavernQuestGui)

> [!question] Gdzie jest istniejące drzewo?
> Dokumentacja mówi, że **struktura interfejsu Karczmy jest już zaprojektowana**, ale nie ma jej w plikach projektu (`src/gui`). Może istnieć tylko w pliku `.rbxl` albo w Figmie. Zob. [[Pytania otwarte]].

## Proponowana hierarchia (z wcześniejszej specyfikacji)
```
StarterGui
└── TavernQuestGui (ScreenGui)
    └── MainBoardFrame (Frame, UIStroke 4px #000, UICorner)
        ├── HalftoneOverlay (ImageLabel)
        ├── InnkeeperSection
        │   ├── InnkeeperViewport (ViewportFrame)
        │   └── DialogueBubble (komiksowy dymek)
        ├── QuestCards (UIListLayout poziomo)
        │   ├── QuestCard_Easy   (Rotation -2)
        │   ├── QuestCard_Medium (Rotation 1)
        │   └── QuestCard_Boss   (Rotation 2)
        └── BottomBar
            ├── EnergyBar (ukośny)
            ├── MugButton (napitek odnawia Energię)
            └── StartQuestButton ("START QUEST!")
```

Mechanika: [[Karczma (Questy)]] · Postać: [[Karczmarz]]
