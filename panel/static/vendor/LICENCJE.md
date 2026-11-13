# Biblioteki zewnętrzne (vendor)

Panel nie pobiera niczego z sieci w czasie działania — poniższe pliki są skopiowane do repozytorium.

## three.js r170 (`three@0.170.0`)

Licencja: **MIT** — Copyright © 2010-2024 three.js authors. Pełny tekst niżej.

| Plik | Źródło | Zmiany |
|---|---|---|
| `three.module.min.js` | https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js | brak (w r170 rdzeń jest w jednym pliku, nie ma `three.core.min.js`) |
| `OrbitControls.js` | https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js | import `'three'` → `'./three.module.min.js'` |
| `GLTFLoader.js` | https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/loaders/GLTFLoader.js | import `'three'` → `'./three.module.min.js'`, `'../utils/BufferGeometryUtils.js'` → `'./BufferGeometryUtils.js'` |
| `BufferGeometryUtils.js` | https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/utils/BufferGeometryUtils.js | import `'three'` → `'./three.module.min.js'` |

SHA-256 plików źródłowych (przed zmianą importów):
- `three.module.min.js` 08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7
- `OrbitControls.js` 80efaadea4f8a636a65fb0bd08bfef62f3d93a0bb94e2e7500f23176c5c07f4e
- `GLTFLoader.js` 45139faddd5aaf48ed2d62203d976e5cbd703db1a592de40527f9f6cf58abd44
- `BufferGeometryUtils.js` c25b7930e570e9ec56173cd3b866ec8d2e10016630db3937efb439daf1cedbf6

Aktualizacja: pobierz te same cztery pliki dla nowej wersji, popraw importy jak w tabeli i zmień numer wersji tutaj.

```
The MIT License

Copyright © 2010-2024 three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
