# Dokumentacja Projektu: "Blocky n Crycket" (Gra Roblox)

## 1. Główne Założenia Projektu
* **Platforma:** Roblox
* **Gatunek:** RPG / Incremental / Tycoon / Pet Collector
* **Koncepcja (Core Loop):** Połączenie angażujących, powtarzalnych pętli znanych z Robloxa (ciągły progres, zbieranie petów, rozbudowa bazy) z rozbudowanym systemem RPG i przerysowanym humorem inspirowanym przeglądarkową grą *Shakes & Fidget*. 
* **Różnica względem inspiracji:** Zamiast biernego czekania (odliczanie czasu misji), gra stawia na akcję dostosowaną do graczy Robloxa – instancjonowane mini-dungeony, mechaniki clicker/incremental oraz poruszanie się w środowisku 3D.

## 2. Kierunek Artystyczny (Art Direction)
Styl gry to unikalna hybryda trzech estetyk:
1. **Komiks i Pop-art (Shakes & Fidget):** Grube, czarne obrysy (outlines 3-4px, cel-shading), przerysowane proporcje, wygięta i asymetryczna architektura, subtelny wzór z kropek rastrowych (halftone pattern) w tłach i cieniach.
2. **Roblox Voxel/Low-Poly:** Żywa, mocno nasycona paleta barw. Postacie, pety i otoczenie 3D oparte na kanciastych, blokowych bryłach.
3. **Pixel-Art:** Wszystkie ikony w interfejsie (przedmioty, waluty, loot, ikony zakładek) są wykonane w wyrazistym, ostrym pixel-arcie zamkniętym w komiksowych ramkach.

### Główni Bohaterowie (Wizytówka gry):
* **Rycerz:** Kanciasty ludzik Roblox w stalowej zbroi i niebieskim tabardzie z wielkim mieczem.
* **Kot-Mag:** Mały, kanciasty pomarańczowy kot w purpurowej, za dużej (ciągnącej się po ziemi) szacie czarodzieja, z magicznym kosturem.
* **Pety:** Brązowy pies, świecący niebieski slime, mały czerwony smok (wszystko w blokowym stylu voxel).

## 3. Główne Mechaniki
* **Karczma (Questy/Misje):** Zamiast paska czasu, gracz wybiera jedną z trzech misji z drewnianej tablicy u Karczmarza i teleportuje się do mini-dungeonu. Może tam pokonać określoną liczbę wrogów (walka 3D) lub użyć mechaniki clickera na obiekcie (np. uderzanie w beczkę), by przyspieszyć ukończenie questa i zdobyć Złoto, EXP oraz Loot.
* **Twierdza (Tycoon):** Każdy gracz posiada własną działkę (plot). Za zdobyte na misjach surowce buduje klockowe budynki ("droppery"), które pasywnie generują Złoto i Magiczne Kryształy.
* **Pety:** Zwierzaki wykluwają się z jaj (mechanika Pet Simulator). Towarzyszą postaci w świecie 3D, modyfikują statystyki i mogą być wysyłane na pasywne ekspedycje.

## 4. Architektura UI i Frontend
Cały interfejs jest płaski (Flat Design), czytelny na urządzeniach mobilnych, oparty na asymetrycznych ramkach, lekko nachylonych przyciskach i komiksowych fontach z dymkami ("BAM!", "POW!").

* **HUD (Główny Ekran):**
  * *Lewa góra:* Okrągły awatar bohatera, Level, ukośne paski HP (czerwony), Many/Energii (niebieski) oraz postępu EXP.
  * *Prawa góra:* Liczniki ekonomii (Złoto, Magiczne Kryształy) z pixel-artowymi ikonami.
  * *Krawędzie boczne:* Nachylone, komiksowe zakładki: Karczma (kufel), Pety (jajko), Tycoon (zamek), Arena (miecze), Ekwipunek (plecak).
  * *Dół:* Hotbar umiejętności i wielki przycisk akcji/ataku.
* **Ekran Ładowania (Loading Screen):** Przerysowana scena przedstawiająca głównych bohaterów biegnących na rozwidleniu dróg (pomiędzy krzywą Karczmą, świecącym Lochem a Zamkiem na wzgórzu). Na dole znajduje się gruby, malarski pasek postępu stylizowany na pociągnięcie pędzla. Posiada dedykowane logo z koroną i napisami "BLOCKY & CRYCKET".

## 5. Pipeline Narzędziowy i "Style Lock" dla AI
Do automatyzacji tworzenia assetów (2D i 3D) używamy protokołu MCP (Model Context Protocol) oraz określonych promptów.
* **Silnik i Kod:** Roblox Studio, Rojo, VS Code (Cursor/Copilot dla skryptów Luau).
* **UI i Grafika 2D:** Figma (Design System), Aseprite (Pixel Art), Midjourney / DALL-E 3 / Higgsfield AI.
* **Modele 3D:** Blockbench (low-poly z malowanymi teksturami), Meshy AI.

### Blokada Stylu (Style Prompt do generowania grafik 2D/UI)
Każdy prompt generujący elementy UI dla tej gry musi zaczynać się od tej formuły:
> "Game UI component, hybrid of Shakes & Fidget comic book ink style and vibrant Roblox aesthetic, thick 4px solid black outlines, subtle pop-art halftone dot texture, painterly shading, vibrant saturated colors..."

## 6. Faza Rozwoju (Aktualny Status)
Obecnie znajdujemy się w **Fazie 1 (Frontend)**. Posiadamy wypracowany kierunek artystyczny, strukturę interfejsu (drzewo obiektów dla Karczmy w Roblox Gui) oraz kompozycję ekranu ładowania. Kolejne kroki to programowanie logiki UI, implementacja modeli postaci (Viewports) i ożywienie HUD-u w środowisku Roblox.
