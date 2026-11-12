---
name: figma-to-roblox
description: Convert a Figma frame (figma.com URL or selection) into a Roblox ScreenGui saved as a Rojo .model.json in src/gui, so it syncs live into StarterGui in Roblox Studio. Use whenever the user wants UI/GUI/menu/HUD/button/panel from Figma moved into the Roblox project ("przenieś z Figmy", "zrób GUI z Figmy", figma.com link + Roblox).
---

# Figma → Roblox GUI (via Rojo)

Target: one Figma top-level frame = one `ScreenGui` file `src/gui/<FrameName>.model.json`.
`src/gui` is mapped to `StarterGui` in `default.project.json` (with `$ignoreUnknownInstances: true`),
so the running `rojo serve` pushes it into Studio immediately.

## Workflow

1. Parse the Figma URL → `fileKey` + `nodeId` (`-` → `:`). Call `create_session` first (Figma MCP rule).
2. Read the frame:
   - `get_metadata` (fileKey, nodeId) → layer tree with x/y/width/height (primary source for layout).
   - `get_design_context` (load the `/figma-design-to-code` skill first, as the Figma server requires) → colors, fonts, radii, strokes, text, auto-layout.
   - `get_screenshot` → visual reference to check the result against.
3. Convert the layer tree using the mapping below and write the `.model.json`.
4. Images/icons: `download_assets` into `assets/figma/<FrameName>/` (see "Images").
5. Validate: `rojo build default.project.json -o <scratchpad>/check.rbxlx` must succeed. Fix any `UnresolvedValue` error (almost always a missing explicit type).
6. Tell the user: GUI is in StarterGui as `<FrameName>`; which images they need to upload; anything that could not be represented.
7. Update the Obsidian brain (`B&C/`): tick the "Stan implementacji" checklist in the matching `B&C/UI/*.md` note (create a `status: propozycja` note if the screen has none), and add an entry to `B&C/Produkcja/Dziennik zmian.md`.

Never edit the `.rbxl` file. Never remove existing user GUIs. Ask before overwriting an existing `src/gui/*.model.json` the user may have changed.

## Layer mapping

| Figma | Roblox |
|---|---|
| Top-level frame | `ScreenGui` (`ResetOnSpawn: false`, `ZIndexBehavior: "Sibling"`, `IgnoreGuiInset: true` if the frame is a full screen) |
| Frame / Group / Rectangle with fill | `Frame` |
| Group without fill | `Frame` with `BackgroundTransparency: 1` |
| Text | `TextLabel` (or `TextBox` if it is clearly an input field) |
| Layer named like `Button`, `Btn`, `*Button*`, or a component instance of a button | `TextButton` (text inside) or `ImageButton` (image only) |
| Image fill / vector / icon | `ImageLabel` (`ImageButton` if a button) |
| Scroll container (clips content, overflow scroll) | `ScrollingFrame` |
| Corner radius | child `UICorner` `CornerRadius: { "UDim": [0, r] }` (circle/ellipse → `[0.5, 0]`) |
| Stroke | child `UIStroke` (`Color`, `Thickness`, `Transparency`; for text use `ApplyStrokeMode: "Contextual"`) |
| Linear gradient fill | child `UIGradient` with `Color` ColorSequence and `Rotation` |
| Auto layout | child `UIListLayout` (`FillDirection`, `Padding` UDim, `HorizontalAlignment`, `VerticalAlignment`, `SortOrder: "LayoutOrder"`) + `UIPadding`; set `LayoutOrder` on children in Figma order |
| Grid auto layout | `UIGridLayout` |
| Layer opacity | `BackgroundTransparency` / `TextTransparency` / `ImageTransparency` = `1 - opacity` (also multiply fill alpha) |
| Drop shadow | not native: add a dark `ImageLabel`/`Frame` behind with offset, or skip and mention it |
| Blur, blend modes, masks except clip | not supported → mention to user |

Layer names: keep the Figma name (sanitize to letters/digits/underscore, unique among siblings) so scripts can find them.
Hidden layers: include with `Visible: false`.
Z-order: later Figma layers draw on top → increasing `ZIndex` (or rely on sibling order with `ZIndexBehavior: Sibling` and set `LayoutOrder`).
Always set `BorderSizePixel: 0`.

## Layout / sizing

- Positions in Roblox are relative to the parent → use child x/y minus parent x/y.
- Default for the top-level content: make it scale with the screen. The root frame (Figma frame size, e.g. 1920×1080) → children use **Scale** values: `x / parentWidth`, `y / parentHeight`, `w / parentWidth`, `h / parentHeight`, offset 0. Add `UIAspectRatioConstraint` to elements that must keep their shape (buttons, icons, panels).
- Figma constraints: Center → `AnchorPoint [0.5,0.5]` + center position; Right/Bottom → `AnchorPoint [1,…]` / `[…,1]`; Left/Right stretch → width in Scale.
- Text: `TextScaled: true` + child `UITextSizeConstraint` (`MaxTextSize` = Figma font size) when using Scale layout; otherwise `TextSize` = Figma font size. Map alignment to `TextXAlignment`/`TextYAlignment`, `TextWrapped: true` for multi-line.
- Mobile safety: put HUD elements at least ~5% from the edges.

## Fonts

`FontFace: { "Font": { "family": "rbxasset://fonts/families/<Family>.json", "weight": "<Weight>", "style": "Normal" } }`
Weights: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Heavy.
Common families available: `GothamSSm`, `BuilderSans`, `Montserrat`, `Roboto`, `SourceSansPro`, `Ubuntu`, `Nunito`, `Oswald`, `FredokaOne`, `LuckiestGuy`, `PressStart2P`, `Bangers`, `Arial`, `Inconsolata`, `TitilliumWeb`, `AmaticSC`, `Balthazar`, `DenkOne`, `PatrickHand`, `PermanentMarker`, `SpecialElite`.
If the Figma font is not one of them, pick the closest (Inter → BuilderSans/GothamSSm, Poppins → Montserrat) and tell the user. Google Fonts can also be used in Roblox via the Creator Store font id: `rbxassetid://<id>` as family.

## Images

Rojo cannot upload images. Process:
1. `download_assets` → `assets/figma/<FrameName>/<layer>.png` (export at 2× for crispness).
2. In the model, set `"Image": "rbxassetid://0"` placeholder and add an attribute so it is easy to find:
   `"Attributes": { "FigmaAsset": "assets/figma/<FrameName>/<layer>.png" }`.
3. Tell the user: in Studio → View → Asset Manager → Bulk Import → select the PNG files, then right-click each → Copy ID, and send the IDs (or paste a list). Then replace the placeholders with the real `rbxassetid://<id>`.
4. Prefer recreating simple shapes (rectangles, circles, gradients) natively instead of images.

## .model.json value formats (verified with Rojo 7.6.1)

Implicit (plain JSON) works for: numbers, booleans, strings, enums as string (`"TextXAlignment": "Left"`), `Vector2` `[x, y]`, `Color3` `[r, g, b]` (0–1 floats, convert hex: `ff8800` → `[1, 0.533, 0]`).

**Must be explicit:**
- UDim2: `"Size": { "UDim2": [[xScale, xOffset], [yScale, yOffset]] }` (implicit `[[..],[..]]` FAILS)
- UDim: `"CornerRadius": { "UDim": [scale, offset] }`
- Font: `{ "Font": { "family": ..., "weight": ..., "style": ... } }`
- ColorSequence: `{ "ColorSequence": { "keypoints": [ { "time": 0, "color": [r,g,b] }, { "time": 1, "color": [r,g,b] } ] } }`
- NumberSequence: `{ "NumberSequence": { "keypoints": [ { "time": 0, "value": 0, "envelope": 0 }, { "time": 1, "value": 0, "envelope": 0 } ] } }`

Children order in the file = sibling order. Root object has no `Name` (the file name is the name).

## Example

```json
{
  "ClassName": "ScreenGui",
  "Properties": { "ResetOnSpawn": false, "ZIndexBehavior": "Sibling" },
  "Children": [
    {
      "Name": "PlayButton",
      "ClassName": "TextButton",
      "Properties": {
        "AnchorPoint": [0.5, 0.5],
        "Position": { "UDim2": [[0.5, 0], [0.8, 0]] },
        "Size": { "UDim2": [[0.2, 0], [0.09, 0]] },
        "BackgroundColor3": [0.18, 0.8, 0.44],
        "BorderSizePixel": 0,
        "Text": "GRAJ",
        "TextColor3": [1, 1, 1],
        "TextScaled": true,
        "FontFace": { "Font": { "family": "rbxasset://fonts/families/FredokaOne.json", "weight": "Regular", "style": "Normal" } }
      },
      "Children": [
        { "Name": "UICorner", "ClassName": "UICorner", "Properties": { "CornerRadius": { "UDim": [0, 16] } } },
        { "Name": "UIAspectRatioConstraint", "ClassName": "UIAspectRatioConstraint", "Properties": { "AspectRatio": 4 } },
        { "Name": "UITextSizeConstraint", "ClassName": "UITextSizeConstraint", "Properties": { "MaxTextSize": 48 } }
      ]
    }
  ]
}
```

Interactivity (button clicks, opening/closing panels) goes in a separate `LocalScript` in `src/client/` that finds the GUI via `Players.LocalPlayer.PlayerGui:WaitForChild("<FrameName>")`. Do not put scripts inside the model file.
