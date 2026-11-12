---
status: kanon
tags: [technika, rojo]
---
# Rojo i struktura projektu

Rojo **7.6.1**. Plik projektu: `default.project.json`. Synchronizacja na żywo: `rojo serve` w folderze gry, a w Studio Plugins → Rojo → Connect (port 34872).

| Folder na dysku | Miejsce w Roblox | Pliki |
|---|---|---|
| `src/server` | ServerScriptService.Server | `*.server.luau` (Script), `*.luau` (ModuleScript) |
| `src/client` | StarterPlayer.StarterPlayerScripts.Client | `*.client.luau` (LocalScript) |
| `src/shared` | ReplicatedStorage.Shared | `*.luau` (ModuleScript) |
| `src/gui` | StarterGui | `*.model.json` (jeden ScreenGui na plik) |

## Ważne zasady
- Każdy węzeł ma `$ignoreUnknownInstances: true`. Rojo **nie usuwa** niczego, co istnieje tylko w pliku `.rbxl`, ale takiej zawartości **nie widać w plikach**, więc Claude jej nie zna. Żeby to zmienić, wyeksportuj skrypty w Studio (prawy przycisk → *Save to File*) do `src/`.
- Plik `Blocky&Crycket.rbxl` jest binarny i nigdy nie jest edytowany automatycznie.
- Zmiany z Rojo trafiają do pliku miejsca dopiero po zapisaniu w Studio (Ctrl+S).
- Grafik nie da się wgrać przez Rojo. Wgrywa się je przez Asset Manager w Studio, a w plikach zostaje `rbxassetid://…`.

## Format .model.json (sprawdzony na Rojo 7.6.1)
- UDim2 **musi** mieć jawny typ: `{"UDim2": [[xs, xo], [ys, yo]]}`
- UDim: `{"UDim": [s, o]}`
- Font: `{"Font": {"family": "rbxasset://fonts/families/<Nazwa>.json", "weight": "Bold", "style": "Normal"}}`
- Color3 `[r,g,b]` (0–1), Vector2 `[x,y]`, enumy jako tekst.

## Pliki testowe do usunięcia
`src/server/Hello.server.luau`, `src/client/Hello.client.luau`, `src/gui/FigmaTest.model.json` (zob. [[Zadania]]).

## Proponowana docelowa struktura (`propozycja`)
ReplicatedStorage/{Modules, Remotes, Assets, Config} · ServerScriptService/{Services, Systems, Data} · StarterGui/{HUD, MainMenu, TavernUI, PetUI, InventoryUI, LoadingScreen} · ServerStorage/{Templates, Models}
