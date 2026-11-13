# Geometria części Roblox — do podglądu 3D

Zmierzone w Roblox Studio 12.11.2026 (promienie rzucane z góry na części tymczasowe), nie z pamięci. Układ współrzędnych Roblox jest prawoskrętny, **Y w górę**, przód części to **−Z** — tak samo jak w three.js, więc pozycje i obroty przenosi się 1:1 bez odbić.

Oznaczenia: `Size = (sx, sy, sz)`, połówki `hx = sx/2`, `hy = sy/2`, `hz = sz/2`, współrzędne w układzie lokalnym części.

| Kształt | Geometria lokalna |
|---|---|
| **Blok** (`Part`, `Shape = Block`) | prostopadłościan `±hx, ±hy, ±hz` |
| **Kula** (`Shape = Ball`) | kula o średnicy `min(sx, sy, sz)` w środku części (reszta rozmiaru jest pusta) |
| **Walec** (`Shape = Cylinder`) | oś wzdłuż **X**, długość `sx`, średnica `min(sy, sz)` |
| **Klin** (`WedgePart`) | 6 wierzchołków: podstawa `(±hx, −hy, ±hz)` + górna krawędź `(±hx, +hy, +hz)`. Wysoka, pionowa ściana jest po stronie **+Z**, skos opada ku **−Z**: wysokość powierzchni `y = hy · z / hz` |
| **Klin narożny** (`CornerWedgePart`) | 5 wierzchołków: podstawa `A(−hx,−hy,−hz)`, `B(hx,−hy,−hz)`, `C(hx,−hy,hz)`, `D(−hx,−hy,hz)` + wierzchołek `P(hx, +hy, −hz)`. Ściany: podstawa `ABCD`, pionowy trójkąt `A B P` (strona −Z), pionowy trójkąt `B C P` (strona +X), skos `A P D` i skos `P C D`. Wysokość powierzchni `y = min(hy · x / hx, −hy · z / hz)` |
| **Siatka** (`MeshPart`), **unia** (`UnionOperation`) | geometrii nie da się odczytać z Luau — w podglądzie rysujemy ramkę `Size` |

Obrót: `rx, ry, rz = CFrame:ToOrientation()` (radiany) odpowiada `CFrame.fromOrientation(rx, ry, rz)` = obrót Y, potem X, potem Z. W three.js: `new THREE.Euler(rx, ry, rz, "YXZ")`.

Pomiary kontrolne (części 4×4×4, środek w 0):
- klin: `(x=0, z=−1,5) → y=−1,5`; `(0, 0) → 0`; `(0, 1,5) → 1,5`;
- klin narożny: `(1,5; −1,5) → 1,5`; `(0; −1,5) → 0`; `(1,5; 0) → 0`; `(0; 1,5) → −1,5`; `(−1,5; z) → −1,5`;
- walec `Size (6, 2, 2)`: `(±2,8; 0) → 1`; `(0; 0,9) → 0,43`; `(0; 1,5) → brak trafienia`;
- walec `Size (2, 6, 4)`: `(0; 0) → 2` — promień to `min(sy, sz)/2`, nie `sy/2`;
- kula `Size (6, 2, 4)`: `(0; 0) → 1`; `(1,5; 0) → brak trafienia`.
