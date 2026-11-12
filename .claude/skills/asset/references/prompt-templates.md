# Szablony promptów (Higgsfield)

Każdy prompt = **[SZABLON KATEGORII]** + **[STYLE BLOCK]** + **[NEGATIVE]**.
Podmień `{...}`. Prompty po angielsku.

## STYLE BLOCK (zawsze)
```
cartoon game asset in the style of a cheerful Roblox fantasy RPG, thick uniform dark brown-black outline, cel shading with 2-3 tones, glossy white highlights on the top-left, saturated warm colors, chunky readable shapes, tiny pixel-art sparkles as accents, centered composition, single object filling about 80% of the frame, isolated on a pure flat white #FFFFFF background, no drop shadow on the background
```

## NEGATIVE (zawsze; jeśli model ma pole negative – tam, inaczej dopisz "Avoid: ...")
```
text, letters, numbers, words, logo, watermark, signature, frame border, photorealistic, 3D render, PBR, gradient background, colored background, thin lines, blurry edges, anime eyes, gore, blood
```

---

## icon – ikona HUD / menu
```
game UI icon of {subject}, {details}, viewed slightly from above, bold silhouette that reads clearly at small sizes
```
Przykład: `{subject}` = "a crossed sword and shield arena emblem", `{details}` = "steel sword, round wooden shield with gold rim, small flag".

## button – pełny przycisk HUD (bez napisu)
```
square game menu button with rounded corners (about 23% radius), thick dark outline, {color_name} glossy gradient fill from light top to darker bottom, subtle halftone dot pattern in the top-right corner, glassy shine on the top-left, centered icon of {subject} in the upper two-thirds, empty lower third reserved for a label
```
`{color_name}`: sky blue `#8FDDF4` / orange `#FFC06A` / green `#78D2A4` / red `#EC6E66` / slate blue `#5A6A92` / purple `#BE78F0` – albo nowy, spójny z paletą.

## item – broń / magia / zbroja / mikstura
```
RPG inventory item icon of {item}, {material} with {accent}, three-quarter view, slightly tilted diagonally, {rarity_glow}
```
`{rarity_glow}`: common = "no glow", rare = "soft blue glow around the item", epic = "soft purple magical glow and tiny sparkles", legendary = "warm golden glow and pixel sparkles".

## pet
```
cute chibi pet companion, {creature}, {color_scheme}, big friendly eyes with simple shine dots, chunky round body, three-quarter front view, happy expression, {accessory}
```

## currency
```
game currency icon, {currency_object}, chunky and shiny, strong rim highlight, slight 3/4 tilt
```
Referencje: `assets/refs/Coin.png`, `assets/refs/Gem.png`.

## frame – ramka / panel UI
```
empty game UI frame panel, {shape}, {material} border with {decoration}, dark navy #1E2740 inner area with glossy top reflection and subtle halftone dots, no content inside, no text, no numbers
```
Uwaga: **żadnych wypalonych pasków z liczbami** – paski i liczby robimy natywnie.

## background / keyart (bez wycinania tła → `--bg none`)
```
wide 16:9 cartoon fantasy game scene, {scene}, Roblox-like blocky characters, warm sunset to night sky gradient, readable foreground path, {key_elements}, leave the {free_area} area calmer for UI overlay
```
Dla tła NIE dodawaj „white background” ze STYLE BLOCK – podmień ostatnie zdanie na „full illustrated background”.
