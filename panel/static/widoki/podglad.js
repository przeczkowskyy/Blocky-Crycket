// Zakładka Podgląd: dwie części przełączane na górze (17.11.2026, zlecenie Karola z 14.11):
//   - „Do przejrzenia” (wspolne/przeglad.js): co właśnie powstaje (prace w toku z podglądem) i raporty do akceptacji —
//     siatka miniatur, zaznaczanie kilku naraz, „Przeglądaj po kolei”; domyślna część;
//   - „Model 3D” (ten plik): „mini Roblox Studio w przeglądarce” (także na telefonie). Migawka świata gry = części
//     (czesci.json) + zrzuty ekranu ze Studio. Geometria kształtów wg panel/luau/KSZTALTY.md.
// Adresy: #/podglad?migawka=<id>[&grupa=…] i #/podglad?zakladka=3d otwierają Model 3D, #/podglad?zakladka=przeglad —
// Do przejrzenia; bez parametrów — ostatnio wybrana część (pamięć przeglądarki).
// three.js ładujemy dopiero przy pierwszym pokazaniu części 3D (moduł widoku jest lekki dla powłoki).

import { ikona as ikonaWspolna, przelacznik, el as elWspolny } from "../wspolne/ui.js";
import { przegladAkceptacji } from "../wspolne/przeglad.js";

const KLUCZ_TRYBU = "bc.podglad.tryb";
function czytajTryb() {
  try {
    return localStorage.getItem(KLUCZ_TRYBU) === "3d" ? "3d" : "przeglad";
  } catch (e) {
    return "przeglad";
  }
}
function zapiszTryb(t) {
  try {
    localStorage.setItem(KLUCZ_TRYBU, t);
  } catch (e) { /* tryb prywatny */ }
}

const CSS = new URL("./podglad.css", import.meta.url).href;
const ZLOTO = 0xf5b82e;
const LIMIT_CIENI = 5000;

let T = null;          // moduł three.js
let Orbit = null;      // OrbitControls
let GEO = null;        // wspólne geometrie jednostkowe

// ------------------------------------------------------------------ drobne narzędzia DOM
function el(tag, at, ...dzieci) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(at || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const d of dzieci.flat()) if (d != null && d !== false) e.append(d.nodeType ? d : String(d));
  return e;
}

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

const IKONY = {
  izo: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
  gora: '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8v8M8 12h8"/>',
  gracz: '<circle cx="12" cy="6" r="3"/><path d="M7 21v-6l-2-1 2-5h10l2 5-2 1v6"/>',
  dopasuj: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/><rect x="9" y="9" width="6" height="6"/>',
  grupy: '<path d="M4 6h16M4 12h10M4 18h7"/><circle cx="18" cy="15" r="3"/>',
  aparat: '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
  zamknij: '<path d="M6 6l12 12M18 6L6 18"/>',
  oko: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  okoZ: '<path d="M3 3l18 18M10.6 5.1A10 10 0 0 1 12 5c6 0 10 7 10 7a17 17 0 0 1-3.2 3.9M6.2 6.2C3.6 8 2 12 2 12s4 7 10 7a9.6 9.6 0 0 0 4.3-1"/>',
  komentarz: '<path d="M4 5h16v11H9l-5 4z"/>',
  agent: '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01"/>',
  dol: '<path d="M6 9l6 6 6-6"/>',
  prawo: '<path d="M9 6l6 6-6 6"/>',
  lewo: '<path d="M15 6l-6 6 6 6"/>',
};
// te ikony bierzemy ze wspólnego zestawu (ui.js), żeby wyglądały tak samo jak w reszcie panelu
const IKONY_WSPOLNE = new Set(["zamknij", "oko", "komentarz", "agent", "dol", "prawo", "lewo"]);
function ikona(n) {
  const s = el("span", { class: "v3d-ik", "aria-hidden": "true" });
  if (IKONY_WSPOLNE.has(n)) {
    s.append(ikonaWspolna(n));
    return s;
  }
  s.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + (IKONY[n] || "") + "</svg>";
  return s;
}

function liczba(n) {
  return Number(n || 0).toLocaleString("pl-PL");
}

function czasTemu(iso) {
  const t = Date.parse(iso);
  if (!t) return "";
  const s = (Date.now() - t) / 1000;
  if (s < 60) return "przed chwilą";
  if (s < 3600) return Math.round(s / 60) + " min temu";
  if (s < 86400) return Math.round(s / 3600) + " h temu";
  if (s < 2 * 86400) return "wczoraj";
  if (s < 7 * 86400) return Math.round(s / 86400) + " dni temu";
  return new Date(t).toLocaleDateString("pl-PL", { day: "numeric", month: "short", year: "numeric" });
}

function czesciSlowo(n) {
  const j = n % 10, d = n % 100;
  if (n === 1) return "część";
  if (j >= 2 && j <= 4 && (d < 12 || d > 14)) return "części";
  return "części";
}

// ------------------------------------------------------------------ geometria kształtów (KSZTALTY.md)
// Bryła z listy trójkątów; kierunek ścian poprawiany automatycznie (normalna na zewnątrz bryły wypukłej).
function brylaZTrojkatow(wierzcholki, trojkaty) {
  const V = wierzcholki.map((w) => new T.Vector3(...w));
  const srodek = V.reduce((a, v) => a.add(v), new T.Vector3()).multiplyScalar(1 / V.length);
  const poz = [];
  const ab = new T.Vector3(), ac = new T.Vector3(), n = new T.Vector3(), sr = new T.Vector3();
  for (let [a, b, c] of trojkaty) {
    ab.subVectors(V[b], V[a]);
    ac.subVectors(V[c], V[a]);
    n.crossVectors(ab, ac);
    sr.copy(V[a]).add(V[b]).add(V[c]).multiplyScalar(1 / 3).sub(srodek);
    if (n.dot(sr) < 0) [b, c] = [c, b];
    for (const i of [a, b, c]) poz.push(V[i].x, V[i].y, V[i].z);
  }
  const g = new T.BufferGeometry();
  g.setAttribute("position", new T.Float32BufferAttribute(poz, 3));
  g.computeVertexNormals();          // geometria bez indeksów -> płaskie cieniowanie ścian
  g.computeBoundingSphere();
  return g;
}

function przygotujGeometrie() {
  if (GEO) return GEO;
  const h = 0.5;
  // Klin: podstawa (±hx, −hy, ±hz) + górna krawędź (±hx, +hy, +hz); wysoka ściana po +Z, skos opada ku −Z.
  const klin = brylaZTrojkatow(
    [[-h, -h, -h], [h, -h, -h], [h, -h, h], [-h, -h, h], [-h, h, h], [h, h, h]],
    [[0, 1, 2], [0, 2, 3], [3, 2, 5], [3, 5, 4], [0, 1, 5], [0, 5, 4], [0, 3, 4], [1, 2, 5]],
  );
  // Klin narożny: A(−,−,−) B(+,−,−) C(+,−,+) D(−,−,+) + wierzchołek P(+hx, +hy, −hz).
  const narozny = brylaZTrojkatow(
    [[-h, -h, -h], [h, -h, -h], [h, -h, h], [-h, -h, h], [h, h, -h]],
    [[0, 1, 2], [0, 2, 3], [0, 1, 4], [1, 2, 4], [0, 4, 3], [4, 2, 3]],
  );
  // Walec: oś X, długość 1, średnica 1 (skalowany do sx × min(sy,sz)).
  const walec = new T.CylinderGeometry(0.5, 0.5, 1, 20, 1, false);
  walec.rotateZ(Math.PI / 2);
  const walecL = new T.CylinderGeometry(0.5, 0.5, 1, 10, 1, false);
  walecL.rotateZ(Math.PI / 2);
  GEO = {
    blok: new T.BoxGeometry(1, 1, 1),
    kula: new T.SphereGeometry(0.5, 20, 14),
    kulaL: new T.SphereGeometry(0.5, 10, 7),     // lżejsza, gdy kul jest bardzo dużo (telefon)
    walec, walecL, klin, narozny,
  };
  return GEO;
}

// 12 krawędzi ramki jednostkowej
const KRAWEDZIE_RAMKI = (() => {
  const h = 0.5, w = [];
  for (const [a, b] of [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]]) w.push(a, b);
  const r = [[-h, -h, -h], [h, -h, -h], [h, -h, h], [-h, -h, h], [-h, h, -h], [h, h, -h], [h, h, h], [-h, h, h]];
  return w.map((i) => r[i]);
})();

// ------------------------------------------------------------------ zastępcze komentarze (gdy wspolne/komentarze.js jeszcze nie istnieje)
async function sekcjaKomentarzy(ctx, cel) {
  try {
    const m = await import("../wspolne/komentarze.js");
    const f = m.komentarze || m.default;
    if (typeof f === "function") return f(ctx, cel);
  } catch (e) { /* moduł wspólny jeszcze nie istnieje — prosty zastępnik niżej */ }
  const lista = el("div", { class: "lista v3d-kom-lista" }, el("p", { class: "cichy-tekst", text: "Wczytuję komentarze…" }));
  const wrap = el("div", { class: "v3d-kom" }, lista);
  const odswiez = async () => {
    try {
      const d = await ctx.api(`/api/komentarze?typ=${encodeURIComponent(cel.typ)}&cel=${encodeURIComponent(cel.cel)}`);
      lista.replaceChildren(...((d.komentarze || []).map((k) => el("div", { class: "wiersz" },
        el("div", {}, el("b", { text: k.kto || "ktoś" }), " ", el("span", { class: "cichy-tekst", text: czasTemu(k.czas) }),
          el("div", { text: k.tekst || "" }))))));
      if (!lista.children.length) lista.append(el("p", { class: "cichy-tekst", text: "Nikt jeszcze tego nie skomentował." }));
    } catch (e) {
      lista.replaceChildren(el("p", { class: "cichy-tekst", text: "Nie udało się wczytać komentarzy: " + e.message }));
    }
  };
  odswiez();
  if (!ctx.statyczny) {
    const pole = el("textarea", { class: "pole", rows: "2", placeholder: "Napisz komentarz…" });
    const wyslij = el("button", { class: "przycisk glowny maly", text: "Wyślij", onclick: async () => {
      const tekst = pole.value.trim();
      if (!tekst) return;
      wyslij.disabled = true;
      try {
        await ctx.api("/api/komentarze", { metoda: "POST", cialo: { cel, tekst } });
        pole.value = "";
        odswiez();
      } catch (e) {
        ctx.toast?.("Nie wysłano komentarza: " + e.message, "blad");
      } finally {
        wyslij.disabled = false;
      }
    } });
    wrap.append(pole, wyslij);
  }
  return wrap;
}

// ------------------------------------------------------------------ widok
export default {
  id: "podglad",
  tytul: "Podgląd 3D",
  ikona: "podglad",
  kolejnosc: 40,
  utworz(ctx) {
    dolaczCss(CSS);
    const S = {
      widoczny: false, gotowy: false, lista: null, meta: null, dane: null, model: null,
      wybor: null, ukryte: new Set(), rozwiniete: new Set(), raf: 0, anim: null, oczekujace: null, zadanie: 0,
      pule: [], wczytywanie: false, bladWebGL: null,
    };
    const lokalnieMoze = () => !!(ctx.ja && ctx.ja.lokalny) && !ctx.statyczny;
    const enc = encodeURIComponent;
    const urlPliku = (id, nazwa) => {
      const p = `/api/podglad/${enc(id)}/plik/${enc(nazwa)}`;
      return typeof ctx.plik === "function" ? ctx.plik(p) : p.slice(1);   // ścieżka względna działa też w lustrze statycznym
    };

    // ---------------- szkielet DOM
    const tytulEl = el("h2", { class: "v3d-tytul", text: "Podgląd 3D" });
    const metaEl = el("div", { class: "v3d-meta cichy-tekst" });
    const opisEl = el("p", { class: "v3d-opis cichy-tekst" });
    const listaMigawek = el("div", { class: "v3d-migawki karta", hidden: true });
    const przyciskMigawek = el("button", { class: "przycisk cichy maly", "aria-expanded": "false" }, "Migawki", ikona("dol"));
    const przyciskNowej = el("button", { class: "przycisk glowny maly", hidden: true }, ikona("aparat"), "Nowa migawka ze Studio");
    const formNowej = el("div", { class: "v3d-nowa karta", hidden: true });
    const gora = el("div", { class: "v3d-gora" },
      el("div", { class: "v3d-gora-tekst" }, tytulEl, metaEl),
      el("div", { class: "v3d-gora-akcje" }, przyciskMigawek, przyciskNowej));

    const scenaEl = el("div", { class: "v3d-scena" });
    const plotno = el("div", { class: "v3d-plotno" });
    const komunikat = el("div", { class: "v3d-komunikat", hidden: true });
    const statystyka = el("div", { class: "v3d-stat" });
    const pasekNarzedzi = el("div", { class: "v3d-narzedzia" });
    const panelGrup = el("aside", { class: "v3d-grupy", hidden: true });
    const arkusz = el("div", { class: "v3d-arkusz", hidden: true });
    scenaEl.append(plotno, pasekNarzedzi, statystyka, komunikat, panelGrup, arkusz);

    const zrzutyEl = el("div", { class: "v3d-zrzuty" });
    const pustyEl = el("div", { class: "pusty v3d-pusty", hidden: true });
    const root = el("section", { class: "v3d" }, gora, listaMigawek, formNowej, pustyEl, scenaEl, zrzutyEl, opisEl);

    const przyciskWidoku = (ik, tekst, fn, tytul) =>
      el("button", { class: "przycisk maly v3d-nb", title: tytul || tekst, "aria-label": tytul || tekst, onclick: fn }, ikona(ik), el("span", { text: tekst }));
    const przyciskGrup = przyciskWidoku("grupy", "Grupy", () => przelaczGrupy(), "Lista grup");
    pasekNarzedzi.append(
      przyciskWidoku("izo", "Izometria", () => ujecie("izo")),
      przyciskWidoku("gora", "Z góry", () => ujecie("gora")),
      przyciskWidoku("gracz", "Gracz", () => ujecie("gracz"), "Z poziomu gracza"),
      przyciskWidoku("dopasuj", "Dopasuj", () => dopasuj(), "Dopasuj kadr do całości albo zaznaczenia"),
      przyciskGrup,
    );

    przyciskMigawek.addEventListener("click", () => {
      listaMigawek.hidden = !listaMigawek.hidden;
      przyciskMigawek.setAttribute("aria-expanded", String(!listaMigawek.hidden));
    });
    przyciskNowej.addEventListener("click", () => {
      formNowej.hidden = !formNowej.hidden;
      if (!formNowej.hidden) formNowej.querySelector("input")?.focus();
    });

    // ---------------- formularz nowej migawki
    {
      const pole = el("input", { class: "pole", placeholder: "Tytuł, np. Karczma po zmianach", maxlength: "120" });
      const opis = el("input", { class: "pole", placeholder: "Opis (opcjonalnie)", maxlength: "400" });
      const stan = el("p", { class: "cichy-tekst v3d-nowa-stan" });
      const zrob = el("button", { class: "przycisk glowny", text: "Zrób migawkę" });
      const anuluj = el("button", { class: "przycisk cichy", text: "Anuluj", onclick: () => { formNowej.hidden = true; } });
      zrob.addEventListener("click", async () => {
        zrob.disabled = true;
        stan.textContent = "Robię migawkę z Roblox Studio… (zrzuty ekranu mogą potrwać do minuty)";
        stan.className = "cichy-tekst v3d-nowa-stan";
        try {
          const cialo = { zrzuty: true };
          if (pole.value.trim()) cialo.tytul = pole.value.trim();
          if (opis.value.trim()) cialo.opis = opis.value.trim();
          const meta = await ctx.api("/api/podglad/migawka", { metoda: "POST", cialo });
          stan.textContent = "";
          pole.value = "";
          opis.value = "";
          formNowej.hidden = true;
          ctx.toast?.("Migawka gotowa: " + (meta.tytul || meta.id), "ok");
          await wczytajListe(meta.id);
        } catch (e) {
          stan.className = "v3d-nowa-stan v3d-blad";
          stan.textContent = opisBleduStudio(e);
        } finally {
          zrob.disabled = false;
        }
      });
      formNowej.append(el("div", { class: "karta-tytul", text: "Nowa migawka ze Studio" }),
        el("p", { class: "cichy-tekst", text: "Zapisze to, co jest teraz w otwartym Roblox Studio (części i zrzuty ekranu). Studio niczego nie zmienia." }),
        pole, opis, el("div", { class: "v3d-wiersz-przyciskow" }, zrob, anuluj), stan);
    }

    function opisBleduStudio(e) {
      const t = (e && e.message) || "";
      if (e && (e.status === 503 || e.status === 502 || e.status === 504 || /studio|mcp|mostek|połącz/i.test(t))) {
        return "Nie udało się połączyć z Roblox Studio. Otwórz Studio z miejscem gry (i włączonym pluginem MCP), a potem spróbuj ponownie." + (t ? " Szczegóły: " + t : "");
      }
      if (e && e.status === 403) return "Migawkę można zrobić tylko na komputerze, na którym działa panel i otwarte jest Studio.";
      return "Nie udało się zrobić migawki. " + (t || "Spróbuj ponownie.");
    }

    // ---------------- three.js: scena
    let renderer, scena, kamera, kontrolki, swiatloKier, mgla, ziemia, siatka, modelGrupa, ramkaWyboru;
    const ray = { r: null, v: null };

    function przygotujScene() {
      if (S.gotowy || S.bladWebGL) return;
      try {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        renderer = new T.WebGLRenderer({ antialias: dpr < 1.5, alpha: true, powerPreference: "high-performance" });
        renderer.setPixelRatio(dpr);
        renderer.setClearColor(0x000000, 0);
      } catch (e) {
        S.bladWebGL = "Ta przeglądarka nie potrafi wyświetlić grafiki 3D (WebGL jest wyłączony albo niedostępny). Zrzuty ekranu niżej nadal działają.";
        pokazKomunikat(S.bladWebGL);
        return;
      }
      plotno.append(renderer.domElement);
      renderer.domElement.addEventListener("webglcontextlost", (e) => { e.preventDefault(); pokazKomunikat("Grafika 3D chwilowo niedostępna — odświeżam…"); });
      renderer.domElement.addEventListener("webglcontextrestored", () => { ukryjKomunikat(); if (S.dane) zbudujModel(); zaplanuj(); });

      scena = new T.Scene();
      mgla = new T.Fog(0xcfe2f3, 200, 2000);
      scena.fog = mgla;
      kamera = new T.PerspectiveCamera(50, 1, 0.1, 20000);
      kamera.position.set(60, 50, 60);

      scena.add(new T.HemisphereLight(0xe4f0ff, 0x5b4a36, 1.7));
      swiatloKier = new T.DirectionalLight(0xfff4e0, 2.1);
      swiatloKier.position.set(0.55, 1, 0.35);
      scena.add(swiatloKier, swiatloKier.target);

      modelGrupa = new T.Group();
      scena.add(modelGrupa);

      kontrolki = new Orbit(kamera, renderer.domElement);
      kontrolki.enableDamping = true;
      kontrolki.dampingFactor = 0.14;
      kontrolki.screenSpacePanning = true;
      kontrolki.maxPolarAngle = Math.PI * 0.495;
      kontrolki.addEventListener("change", zaplanuj);
      kontrolki.addEventListener("start", () => { S.anim = null; });

      ray.r = new T.Raycaster();
      ray.v = new T.Vector2();

      // tap / klik = wybór (bez przeciągania)
      let start = null;
      renderer.domElement.addEventListener("pointerdown", (e) => { start = { x: e.clientX, y: e.clientY, t: performance.now(), id: e.pointerId }; });
      renderer.domElement.addEventListener("pointerup", (e) => {
        if (!start || start.id !== e.pointerId) return;
        const d = Math.hypot(e.clientX - start.x, e.clientY - start.y);
        const t = performance.now() - start.t;
        start = null;
        if (d < 7 && t < 500) wybierzWPunkcie(e.clientX, e.clientY);
      });

      new ResizeObserver(() => { dopasujRozmiar(); }).observe(plotno);
      S.gotowy = true;
      dopasujRozmiar();
    }

    function dopasujRozmiar() {
      if (!renderer) return;
      const w = plotno.clientWidth, h = plotno.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h, false);
      kamera.aspect = w / h;
      kamera.updateProjectionMatrix();
      zaplanuj();
    }

    // ---------------- pętla renderowania na żądanie
    function zaplanuj() {
      if (!S.widoczny || S.raf || !renderer) return;
      S.raf = requestAnimationFrame(klatka);
    }

    function klatka(t) {
      S.raf = 0;
      let dalej = false;
      if (S.anim) dalej = krokAnimacji(t) || dalej;
      if (kontrolki.update()) dalej = true;
      ustawMgleIBliskosc();
      renderer.render(scena, kamera);
      if (dalej) zaplanuj();
    }

    function ustawMgleIBliskosc() {
      const d = kamera.position.distanceTo(kontrolki.target);
      const R = S.promien || 100;
      mgla.near = d + R * 1.2;
      mgla.far = d + R * 6 + 300;
      const near = Math.max(0.05, Math.min(d / 400, 5));
      const far = Math.max(d + R * 12, 3000);
      if (Math.abs(near - kamera.near) / kamera.near > 0.2 || Math.abs(far - kamera.far) / kamera.far > 0.2) {
        kamera.near = near;
        kamera.far = far;
        kamera.updateProjectionMatrix();
      }
    }

    function animujDo(poz, cel, ms = 480) {
      S.anim = { t0: null, ms, p0: kamera.position.clone(), c0: kontrolki.target.clone(), p1: poz.clone(), c1: cel.clone() };
      zaplanuj();
    }

    function krokAnimacji(t) {
      const a = S.anim;
      if (a.t0 == null) a.t0 = t;
      let u = Math.min(1, (t - a.t0) / a.ms);
      const e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
      kamera.position.lerpVectors(a.p0, a.p1, e);
      kontrolki.target.lerpVectors(a.c0, a.c1, e);
      if (u >= 1) S.anim = null;
      return u < 1;
    }

    // ---------------- ujęcia kamery
    function ramkaCelu() {
      if (S.wybor) {
        const b = ramkaGrupy(S.wybor);
        if (b && !b.isEmpty()) return b;
      }
      return S.ramka ? S.ramka.clone() : null;
    }

    function odleglosc(r) {
      const fov = (kamera.fov * Math.PI) / 180;
      const fovMin = kamera.aspect < 1 ? 2 * Math.atan(Math.tan(fov / 2) * kamera.aspect) : fov;
      // promień kuli opisanej jest ostrożny (prostopadłościan w rzucie jest mniejszy) — stąd 0,9
      return (Math.max(r, 2) / Math.sin(fovMin / 2)) * 0.9;
    }

    function dopasuj(natychmiast) {
      if (!kamera) return;
      const b = ramkaCelu();
      if (!b) return;
      const c = b.getCenter(new T.Vector3());
      const r = b.getSize(new T.Vector3()).length() / 2;
      const kier = kamera.position.clone().sub(kontrolki.target);
      if (kier.lengthSq() < 1e-6) kier.set(1, 0.75, 1);
      kier.normalize();
      // kadrowanie zawsze lekko z góry (z poziomu gracza grupę zasłaniałyby inne obiekty)
      if (kier.y < 0.35) { kier.y = 0.35; kier.normalize(); }
      let d = odleglosc(r);
      // telefon: dolny arkusz zasłania część płótna — oddal trochę i przesuń obiekt w widoczną górną część
      const f = !arkusz.hidden && matchMedia("(max-width: 720px)").matches ? Math.min(0.6, arkusz.offsetHeight / Math.max(plotno.clientHeight, 1)) : 0;
      if (f > 0) {
        d *= 1 + f * 0.8;
        const przod = kier.clone().negate();
        const prawo = new T.Vector3().crossVectors(przod, new T.Vector3(0, 1, 0));
        if (prawo.lengthSq() < 1e-6) prawo.set(1, 0, 0);
        const gora = new T.Vector3().crossVectors(prawo.normalize(), przod).normalize();
        const wys = 2 * d * Math.tan((kamera.fov * Math.PI) / 360);
        c.addScaledVector(gora, -wys * f / 2);
      }
      const poz = c.clone().addScaledVector(kier, d);
      const dno = (S.poziomZiemi != null ? S.poziomZiemi : b.min.y) + 1;
      if (poz.y < dno) { c.y += dno - poz.y; poz.y = dno; }        // kamera nigdy pod ziemią
      if (natychmiast) {
        kamera.position.copy(poz);
        kontrolki.target.copy(c);
        zaplanuj();
      } else animujDo(poz, c);
    }

    function ujecie(rodzaj) {
      const b = ramkaCelu();
      if (!b || !kamera) return;
      const c = b.getCenter(new T.Vector3());
      const rozm = b.getSize(new T.Vector3());
      const r = rozm.length() / 2;
      if (rodzaj === "izo") {
        animujDo(c.clone().addScaledVector(new T.Vector3(1, 0.8, 1).normalize(), odleglosc(r)), c);
      } else if (rodzaj === "gora") {
        animujDo(c.clone().addScaledVector(new T.Vector3(0, 1, 0.02).normalize(), odleglosc(Math.max(rozm.x, rozm.z) / 2 * 1.1)), c);
      } else {
        // oczy postaci ~5 studów nad „ziemią” (wierzch najniższej dużej powierzchni)
        const oczy = (S.poziomZiemi != null ? S.poziomZiemi : b.min.y) + 5;
        const kier = kamera.position.clone().sub(kontrolki.target);
        kier.y = 0;
        if (kier.lengthSq() < 1e-6) kier.set(0, 0, 1);
        kier.normalize();
        const promienPoziomy = Math.hypot(rozm.x, rozm.z) / 2;
        const dyst = Math.max(24, Math.min(promienPoziomy * 1.15, odleglosc(r)));
        const cel = new T.Vector3(c.x, oczy, c.z);
        animujDo(cel.clone().addScaledVector(kier, dyst), cel);
      }
    }

    // ---------------- budowanie modelu z czesci.json
    function wyczyscModel() {
      for (const p of S.pule) {
        p.mesh.dispose();
        if (p.linie) p.linie.geometry.dispose();
      }
      S.pule = [];
      while (modelGrupa.children.length) {
        const o = modelGrupa.children[0];
        modelGrupa.remove(o);
        if (o.userData.glb) o.traverse((x) => { x.geometry?.dispose?.(); if (x.material) [].concat(x.material).forEach((m) => { m.map?.dispose?.(); m.dispose?.(); }); });
      }
      if (ziemia) { scena.remove(ziemia); ziemia.geometry.dispose(); ziemia.material.dispose(); ziemia = null; }
      if (siatka) { scena.remove(siatka); siatka.geometry.dispose(); siatka.material.dispose(); siatka = null; }
      if (ramkaWyboru) { scena.remove(ramkaWyboru); ramkaWyboru.geometry.dispose(); ramkaWyboru = null; }
    }

    // materiały współdzielone w obrębie jednej migawki
    function material(rodzaj) {
      if (rodzaj === "neon") return new T.MeshBasicMaterial({ color: 0xffffff, toneMapped: false });
      if (rodzaj === "ramka") return new T.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.28, depthWrite: false });
      if (rodzaj.startsWith("t")) {
        const op = Number(rodzaj.slice(1)) / 10;
        return new T.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: op, depthWrite: false });
      }
      return new T.MeshLambertMaterial({ color: 0xffffff });
    }

    // Analiza danych: grupy, ramki, pule instancji. Wynik zostaje w S.dane (bez obiektów three — te robi zbudujModel).
    function przeanalizuj(j) {
      const grupy = (j.grupy || []).map((s) => ({ sciezka: String(s), liczba: 0, min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] }));
      const mats = j.materialy || [];
      const czesci = j.czesci || [];
      const pule = new Map();                       // klucz -> {ksztalt, rodzaj, idx:[]}
      let pominiete = 0;
      const sMin = [Infinity, Infinity, Infinity], sMax = [-Infinity, -Infinity, -Infinity];
      const cMin = [Infinity, Infinity, Infinity], cMax = [-Infinity, -Infinity, -Infinity];
      const m4 = new T.Matrix4(), q = new T.Quaternion(), eu = new T.Euler(0, 0, 0, "YXZ"), v = new T.Vector3(), sc = new T.Vector3(1, 1, 1);
      const macierze = new Float32Array(czesci.length * 16);
      const zakresy = new Float32Array(czesci.length * 3);
      let kul = 0, walcow = 0;
      for (let i = 0; i < czesci.length; i++) {
        const p = czesci[i];
        const k = p[0] | 0, g = p[1] | 0;
        const przez = Number(p[13]) || 0;
        // pełna macierz obrotu (bez skali) — do zakresu AABB
        eu.set(p[5], p[6], p[7], "YXZ");
        q.setFromEuler(eu);
        v.set(p[2], p[3], p[4]);
        m4.compose(v, q, sc);
        const e = m4.elements;
        const hx = p[8] / 2, hy = p[9] / 2, hz = p[10] / 2;
        const ex = Math.abs(e[0]) * hx + Math.abs(e[4]) * hy + Math.abs(e[8]) * hz;
        const ey = Math.abs(e[1]) * hx + Math.abs(e[5]) * hy + Math.abs(e[9]) * hz;
        const ez = Math.abs(e[2]) * hx + Math.abs(e[6]) * hy + Math.abs(e[10]) * hz;
        zakresy[i * 3] = ex; zakresy[i * 3 + 1] = ey; zakresy[i * 3 + 2] = ez;
        const gr = grupy[g];
        if (gr) gr.liczba++;
        if (przez >= 0.98) { pominiete++; continue; }   // niewidoczne w grze — nie rysujemy
        const ext = [ex, ey, ez];
        for (let a = 0; a < 3; a++) {
          const lo = p[2 + a] - ext[a], hi = p[2 + a] + ext[a];
          if (lo < cMin[a]) cMin[a] = lo;
          if (hi > cMax[a]) cMax[a] = hi;
          if (gr) { if (lo < gr.min[a]) gr.min[a] = lo; if (hi > gr.max[a]) gr.max[a] = hi; }
        }
        // ramka sceny bez gigantycznych płaskich podłóg (Baseplate 2048×16×2048 zasłoniłby budowle)
        const poziomo = Math.max(2 * ex, 2 * ez);
        if (!(poziomo > 256 && 2 * ey < poziomo / 20)) {
          for (let a = 0; a < 3; a++) {
            const lo = p[2 + a] - ext[a], hi = p[2 + a] + ext[a];
            if (lo < sMin[a]) sMin[a] = lo;
            if (hi > sMax[a]) sMax[a] = hi;
          }
        }
        // macierz instancji = pozycja · obrót · skala wg kształtu
        let skx = p[8], sky = p[9], skz = p[10];
        if (k === 1) { const d = Math.min(skx, sky, skz); skx = sky = skz = d; kul++; }
        else if (k === 2) { const d = Math.min(sky, skz); sky = skz = d; walcow++; }
        m4.compose(v, q, new T.Vector3(skx, sky, skz));
        macierze.set(m4.elements, i * 16);

        const mat = String(mats[p[12]] || "");
        let rodzaj;
        if (k >= 5) rodzaj = "ramka";
        else if (mat === "Neon" && przez < 0.5) rodzaj = "neon";
        else {
          let op = 1 - przez;
          if (mat === "Glass") op = Math.min(op, 0.55);
          if (mat === "ForceField") op = Math.min(op, 0.35);
          if (op < 0.97) rodzaj = "t" + Math.max(2, Math.min(8, Math.round(op * 5) * 2));
          else rodzaj = "pelny";
        }
        const klucz = rodzaj === "ramka" ? "ramka" : k + ":" + rodzaj;
        if (!pule.has(klucz)) pule.set(klucz, { ksztalt: rodzaj === "ramka" ? 0 : k, rodzaj, idx: [] });
        pule.get(klucz).idx.push(i);
      }
      let ramka = null, calosc = null;
      if (isFinite(cMin[0])) calosc = { min: cMin, max: cMax };
      if (isFinite(sMin[0])) ramka = { min: sMin, max: sMax };
      else ramka = calosc;
      // poziom ziemi: wierzch najniższej „podłogi” (płaskiej, szerokiej części), inaczej spód sceny
      let ziemiaY = null;
      for (let i = 0; i < czesci.length; i++) {
        const p = czesci[i];
        if ((Number(p[13]) || 0) >= 0.98) continue;
        const ex = zakresy[i * 3], ey = zakresy[i * 3 + 1], ez = zakresy[i * 3 + 2];
        if (Math.min(ex, ez) > 8 && ey < Math.min(ex, ez) / 3) {
          const wierzch = p[3] + ey;
          if (ziemiaY == null || wierzch < ziemiaY) ziemiaY = wierzch;
        }
      }
      return { grupy, czesci, pule: [...pule.values()], macierze, pominiete, ramka, calosc, ziemiaY, kul, walcow, mats };
    }

    function kolorCzesci(hex, neon) {
      const c = new T.Color();
      const n = parseInt(String(hex || "A3A2A5").replace("#", ""), 16);
      c.setHex(isNaN(n) ? 0xa3a2a5 : n);           // sRGB -> liniowy (zarządzanie kolorem three.js)
      if (neon) c.multiplyScalar(1.25);
      return c;
    }

    function zbudujModel() {
      wyczyscModel();
      const D = S.dane;
      const geo = przygotujGeometrie();
      const duzo = D.czesci.length > 6000;
      const z = new T.Matrix4();
      z.makeScale(0, 0, 0);
      const cienie = !!(matchMedia("(pointer: fine)").matches && D.czesci.length < LIMIT_CIENI && window.innerWidth >= 900);
      renderer.shadowMap.enabled = cienie;
      renderer.shadowMap.autoUpdate = false;
      renderer.shadowMap.type = T.PCFSoftShadowMap;
      swiatloKier.castShadow = cienie;

      for (const pd of D.pule) {
        const g = pd.rodzaj === "ramka" ? geo.blok
          : [geo.blok, (duzo || D.kul > 2000) ? geo.kulaL : geo.kula, (duzo || D.walcow > 2000) ? geo.walecL : geo.walec, geo.klin, geo.narozny][pd.ksztalt] || geo.blok;
        const n = pd.idx.length;
        const mesh = new T.InstancedMesh(g, material(pd.rodzaj), n);
        mesh.frustumCulled = false;
        const mac = new Float32Array(n * 16);
        const kol = new Float32Array(n * 3);
        const grupa = new Int32Array(n);
        const c = new T.Color();
        for (let i = 0; i < n; i++) {
          const ci = pd.idx[i];
          const p = D.czesci[ci];
          mac.set(D.macierze.subarray(ci * 16, ci * 16 + 16), i * 16);
          c.copy(kolorCzesci(p[11], pd.rodzaj === "neon"));
          kol[i * 3] = c.r; kol[i * 3 + 1] = c.g; kol[i * 3 + 2] = c.b;
          grupa[i] = p[1] | 0;
        }
        mesh.instanceMatrix.array.set(mac);
        mesh.instanceMatrix.needsUpdate = true;
        mesh.instanceColor = new T.InstancedBufferAttribute(new Float32Array(kol), 3);
        mesh.castShadow = cienie && pd.rodzaj !== "ramka" && !pd.rodzaj.startsWith("t");
        mesh.receiveShadow = cienie && pd.rodzaj !== "neon";
        if (pd.rodzaj !== "pelny" && pd.rodzaj !== "neon") mesh.renderOrder = 2;
        const pula = { mesh, idx: Int32Array.from(pd.idx), mac, kol, grupa, rodzaj: pd.rodzaj, zero: z };
        // ramki siatek i unii: krawędzie (scalone w jedną geometrię linii)
        if (pd.rodzaj === "ramka") {
          const poz = new Float32Array(n * 24 * 3);
          const lk = new Float32Array(n * 24 * 3);
          const m = new T.Matrix4(), w = new T.Vector3(), cc = new T.Color(), bialy = new T.Color(1, 1, 1);
          for (let i = 0; i < n; i++) {
            m.fromArray(mac, i * 16);
            cc.setRGB(kol[i * 3], kol[i * 3 + 1], kol[i * 3 + 2]).lerp(bialy, 0.35);
            for (let k = 0; k < 24; k++) {
              w.set(...KRAWEDZIE_RAMKI[k]).applyMatrix4(m);
              const o = (i * 24 + k) * 3;
              poz[o] = w.x; poz[o + 1] = w.y; poz[o + 2] = w.z;
              lk[o] = cc.r; lk[o + 1] = cc.g; lk[o + 2] = cc.b;
            }
          }
          const lg = new T.BufferGeometry();
          lg.setAttribute("position", new T.BufferAttribute(poz.slice(), 3));
          lg.setAttribute("color", new T.BufferAttribute(lk.slice(), 3));
          const linie = new T.LineSegments(lg, new T.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.9 }));
          linie.frustumCulled = false;
          pula.linie = linie;
          pula.liniePoz = poz;
          pula.linieKol = lk;
          modelGrupa.add(linie);
        }
        modelGrupa.add(mesh);
        S.pule.push(pula);
      }
      dodajZiemie(D.calosc || D.ramka, cienie);
      S.ramka = D.ramka ? new T.Box3(new T.Vector3(...D.ramka.min), new T.Vector3(...D.ramka.max)) : null;
      S.promien = S.ramka ? S.ramka.getSize(new T.Vector3()).length() / 2 : 100;
      S.poziomZiemi = D.ziemiaY;
      if (cienie && S.ramka) ustawCien(D.calosc || D.ramka);
      zastosujWidocznosc();
      zastosujWybor();
    }

    function dodajZiemie(zakres, cienie) {
      const mn = zakres ? zakres.min : [-50, 0, -50], mx = zakres ? zakres.max : [50, 10, 50];
      const cx = (mn[0] + mx[0]) / 2, cz = (mn[2] + mx[2]) / 2;
      const rozp = Math.max(mx[0] - mn[0], mx[2] - mn[2], 60);
      const bok = rozp * 4 + 200;
      const y = mn[1] - 0.05;
      ziemia = new T.Mesh(new T.PlaneGeometry(bok, bok), new T.MeshLambertMaterial({ color: 0x6d8a5c }));
      ziemia.rotation.x = -Math.PI / 2;
      ziemia.position.set(cx, y, cz);
      ziemia.receiveShadow = cienie;
      scena.add(ziemia);
      // krok siatki: „okrągła” liczba studów, ok. 60–120 kratek na całą ziemię
      let krok = 4;
      while (bok / krok > 120) krok *= 2;
      siatka = new T.GridHelper(krok * Math.round(bok / krok), Math.round(bok / krok), 0x3d5532, 0x55704a);
      siatka.material.transparent = true;
      siatka.material.opacity = 0.35;
      siatka.material.depthWrite = false;
      siatka.position.set(cx, y + 0.02, cz);
      scena.add(siatka);
    }

    function ustawCien(zakres) {
      const mn = new T.Vector3(...zakres.min), mx = new T.Vector3(...zakres.max);
      const c = mn.clone().add(mx).multiplyScalar(0.5);
      const r = mx.clone().sub(mn).length() / 2 + 2;
      const kier = new T.Vector3(0.55, 1, 0.35).normalize();
      swiatloKier.position.copy(c).addScaledVector(kier, r * 2);
      swiatloKier.target.position.copy(c);
      const cam = swiatloKier.shadow.camera;
      cam.left = -r; cam.right = r; cam.top = r; cam.bottom = -r;
      cam.near = 0.5; cam.far = r * 4;
      cam.updateProjectionMatrix();
      swiatloKier.shadow.mapSize.set(2048, 2048);
      swiatloKier.shadow.bias = -0.0005;
      swiatloKier.shadow.normalBias = 0.02;
      if (swiatloKier.shadow.map) { swiatloKier.shadow.map.dispose(); swiatloKier.shadow.map = null; }
    }

    // ---------------- grupy: dopasowanie ścieżek, widoczność, wybór
    // Klucz wyboru i ukrycia: "p:<ścieżka>" = grupa razem z podgrupami, "d:<ścieżka>" = dokładnie ta grupa
    // (np. luźne części leżące wprost w Workspace — inaczej klik w Baseplate zaznaczyłby cały świat).
    const klucz = (sciezka, dokladnie) => (dokladnie ? "d:" : "p:") + sciezka;
    const sciezkaKlucza = (k) => (k ? k.slice(2) : "");
    const pasuje = (sciezka, k) => {
      const s = k.slice(2);
      return k[0] === "d" ? sciezka === s : sciezka === s || sciezka.startsWith(s + "/");
    };

    function grupyDlaWyboru(prefiks) {
      const out = new Uint8Array(S.dane ? S.dane.grupy.length : 0);
      if (!prefiks || !S.dane) return out;
      S.dane.grupy.forEach((g, i) => { if (pasuje(g.sciezka, prefiks)) out[i] = 1; });
      return out;
    }

    function ramkaGrupy(prefiks) {
      if (!S.dane) return null;
      if (S.model) {
        const b = new T.Box3();
        for (const g of S.dane.grupy) if (pasuje(g.sciezka, prefiks) && g.obiekt) b.expandByObject(g.obiekt);
        return b;
      }
      const b = new T.Box3();
      for (const g of S.dane.grupy) {
        if (!pasuje(g.sciezka, prefiks) || !isFinite(g.min[0])) continue;
        b.expandByPoint(new T.Vector3(...g.min));
        b.expandByPoint(new T.Vector3(...g.max));
      }
      return b;
    }

    function liczbaWGrupie(prefiks) {
      if (!S.dane) return 0;
      return S.dane.grupy.reduce((s, g) => s + (pasuje(g.sciezka, prefiks) ? g.liczba : 0), 0);
    }

    function zastosujWidocznosc() {
      if (!S.dane) return;
      const ukryta = new Uint8Array(S.dane.grupy.length);
      S.dane.grupy.forEach((g, i) => { for (const u of S.ukryte) if (pasuje(g.sciezka, u)) { ukryta[i] = 1; break; } });
      if (S.model) {
        S.dane.grupy.forEach((g, i) => { if (g.obiekt) g.obiekt.visible = !ukryta[i]; });
      } else {
        for (const p of S.pule) {
          const a = p.mesh.instanceMatrix.array;
          const zero = p.zero.elements;
          for (let i = 0; i < p.idx.length; i++) {
            a.set(ukryta[p.grupa[i]] ? zero : p.mac.subarray(i * 16, i * 16 + 16), i * 16);
          }
          p.mesh.instanceMatrix.needsUpdate = true;
          if (p.linie) {
            const pa = p.linie.geometry.attributes.position;
            for (let i = 0; i < p.idx.length; i++) {
              const o = i * 72;
              if (ukryta[p.grupa[i]]) pa.array.fill(0, o, o + 72);
              else pa.array.set(p.liniePoz.subarray(o, o + 72), o);
            }
            pa.needsUpdate = true;
          }
        }
      }
      if (renderer) renderer.shadowMap.needsUpdate = true;
      zaplanuj();
    }

    function zastosujWybor() {
      if (!S.dane) return;
      const wyb = grupyDlaWyboru(S.wybor);
      const jest = !!S.wybor;
      const zl = new T.Color(ZLOTO);
      const c = new T.Color();
      if (!S.model) {
        for (const p of S.pule) {
          const a = p.mesh.instanceColor.array;
          for (let i = 0; i < p.idx.length; i++) {
            c.setRGB(p.kol[i * 3], p.kol[i * 3 + 1], p.kol[i * 3 + 2]);
            if (jest) {
              if (wyb[p.grupa[i]]) c.lerp(zl, 0.28);
              else c.multiplyScalar(0.55);
            }
            a[i * 3] = c.r; a[i * 3 + 1] = c.g; a[i * 3 + 2] = c.b;
          }
          p.mesh.instanceColor.needsUpdate = true;
          if (p.linie) {
            const ca = p.linie.geometry.attributes.color;
            for (let i = 0; i < p.idx.length; i++) {
              const o = i * 72;
              for (let k = 0; k < 72; k += 3) {
                let r = p.linieKol[o + k], g = p.linieKol[o + k + 1], b = p.linieKol[o + k + 2];
                if (jest) {
                  if (wyb[p.grupa[i]]) { r = r * 0.4 + zl.r * 0.6; g = g * 0.4 + zl.g * 0.6; b = b * 0.4 + zl.b * 0.6; }
                  else { r *= 0.4; g *= 0.4; b *= 0.4; }
                }
                ca.array[o + k] = r; ca.array[o + k + 1] = g; ca.array[o + k + 2] = b;
              }
            }
            ca.needsUpdate = true;
          }
        }
      }
      if (ramkaWyboru) { scena.remove(ramkaWyboru); ramkaWyboru.geometry.dispose(); ramkaWyboru = null; }
      if (jest) {
        const b = ramkaGrupy(S.wybor);
        if (b && !b.isEmpty()) {
          ramkaWyboru = new T.Box3Helper(b.expandByScalar(0.3), ZLOTO);
          ramkaWyboru.material.depthTest = false;
          ramkaWyboru.material.transparent = true;
          ramkaWyboru.renderOrder = 5;
          scena.add(ramkaWyboru);
        }
      }
      odswiezDrzewo();
      zaplanuj();
    }

    function wybierz(prefiks, kadruj) {
      S.wybor = prefiks || null;
      zastosujWybor();
      pokazArkusz();
      if (prefiks && kadruj) dopasuj();
    }

    function wybierzWPunkcie(x, y) {
      if (!S.dane || !renderer) return;
      const r = renderer.domElement.getBoundingClientRect();
      ray.v.set(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1);
      ray.r.setFromCamera(ray.v, kamera);
      if (S.model) {
        const hit = ray.r.intersectObject(S.model, true).find((h) => h.object.visible);
        if (!hit) return wybierz(null);
        let o = hit.object;
        while (o && !o.userData.grupaGlb && o.parent) o = o.parent;
        return wybierz(o && o.userData.grupaGlb ? klucz(o.userData.grupaGlb, false) : null);
      }
      const hits = ray.r.intersectObjects(S.pule.map((p) => p.mesh), false);
      for (const h of hits) {
        const p = S.pule.find((q) => q.mesh === h.object);
        if (!p || h.instanceId == null) continue;
        const g = S.dane.grupy[p.grupa[h.instanceId]];
        if (!g) continue;
        if (S.wybor && pasuje(g.sciezka, S.wybor)) return;   // tap w już zaznaczoną grupę — bez zmian
        return wybierz(klucz(g.sciezka, drzewo().luzne.has(g.sciezka)));
      }
      wybierz(null);
    }

    // ---------------- arkusz komponentu
    function pokazArkusz() {
      if (!S.wybor) { arkusz.hidden = true; arkusz.replaceChildren(); return; }
      const sciezka = sciezkaKlucza(S.wybor);
      const etykieta = sciezka.split("/").pop() || sciezka;
      const cel = { typ: "studio", cel: sciezka, etykieta };
      const ile = liczbaWGrupie(S.wybor);
      const tylkoLuzne = S.wybor[0] === "d" && S.dane.grupy.some((g) => g.sciezka.startsWith(sciezka + "/"));
      const miejsceKom = el("div", { class: "v3d-arkusz-kom" });
      const btnKom = el("button", { class: "przycisk maly" }, ikona("komentarz"), "Skomentuj");
      btnKom.addEventListener("click", async () => {
        btnKom.disabled = true;
        miejsceKom.replaceChildren(el("p", { class: "cichy-tekst", text: "Wczytuję komentarze…" }));
        try {
          miejsceKom.replaceChildren(await sekcjaKomentarzy(ctx, cel));
        } catch (e) {
          miejsceKom.replaceChildren(el("p", { class: "cichy-tekst", text: "Komentarze są chwilowo niedostępne." }));
        }
      });
      const btnAgent = el("button", { class: "przycisk maly", onclick: () => ctx.idz("agent", { kontekst: [cel] }) }, ikona("agent"), "Zapytaj agenta");
      if (ctx.statyczny) btnAgent.hidden = true;
      arkusz.replaceChildren(
        el("div", { class: "v3d-arkusz-uchwyt" }),
        el("div", { class: "v3d-arkusz-glowa" },
          el("div", {},
            el("div", { class: "karta-tytul", text: etykieta }),
            el("div", { class: "v3d-sciezka cichy-tekst", text: sciezka, title: sciezka })),
          el("button", { class: "przycisk cichy maly v3d-x", "aria-label": "Zamknij", onclick: () => wybierz(null) }, ikona("zamknij"))),
        el("div", { class: "v3d-arkusz-chipy" }, el("span", { class: "chip zloto", text: liczba(ile) + " " + czesciSlowo(ile) }),
          tylkoLuzne ? el("span", { class: "cichy-tekst v3d-sciezka", text: "tylko części leżące wprost w tej grupie" }) : null),
        el("div", { class: "v3d-wiersz-przyciskow" }, btnKom, btnAgent,
          el("button", { class: "przycisk maly", onclick: () => dopasuj() }, ikona("dopasuj"), "Dopasuj")),
        miejsceKom);
      arkusz.hidden = false;
    }

    // ---------------- drzewko grup
    function przelaczGrupy(pokaz) {
      panelGrup.hidden = pokaz === undefined ? !panelGrup.hidden : !pokaz;
      przyciskGrup.classList.toggle("aktywny", !panelGrup.hidden);
      if (!panelGrup.hidden) odswiezDrzewo();
    }

    // Drzewko 1–2 poziomów pod wspólnym przodkiem (np. Workspace/DemoLesnaBaza). Grupy leżące wyżej niż ten przodek
    // (np. „Workspace” z Baseplate) są osobnymi węzłami „luźne części” z wyborem dokładnym. Wynik w pamięci do zmiany danych.
    function drzewo() {
      if (S.drzewo && S.drzewo.dane === S.dane) return S.drzewo;
      const gr = S.dane ? S.dane.grupy.filter((g) => g.liczba > 0) : [];
      const wynik = { dane: S.dane, prefiks: "", wezly: [], luzne: new Set() };
      S.drzewo = wynik;
      if (!gr.length) return wynik;
      const podzielone = gr.map((g) => g.sciezka.split("/"));
      const glebokie = podzielone.filter((p) => p.length >= 2);
      const baza = glebokie.length ? glebokie : podzielone;
      let wsp = 0;
      const minDl = Math.min(...baza.map((p) => p.length));
      while (wsp < minDl - 1 && baza.every((p) => p[wsp] === baza[0][wsp])) wsp++;
      const C = baza[0].slice(0, wsp);
      wynik.prefiks = C.join("/");
      const mapa = new Map();
      const luzne = [];
      gr.forEach((g, i) => {
        const cz = podzielone[i];
        const podC = cz.length > wsp && C.every((s, j) => cz[j] === s);
        if (!podC) {
          wynik.luzne.add(g.sciezka);
          luzne.push({ sciezka: g.sciezka, klucz: klucz(g.sciezka, true), nazwa: (cz[cz.length - 1] || g.sciezka) + " — luźne części", liczba: g.liczba, dzieci: [] });
          return;
        }
        const sc = cz.slice(0, wsp + 1).join("/");
        if (!mapa.has(sc)) mapa.set(sc, { sciezka: sc, klucz: klucz(sc, false), nazwa: cz[wsp], liczba: 0, dzieci: new Map() });
        const w = mapa.get(sc);
        w.liczba += g.liczba;
        if (cz.length > wsp + 1) {
          const sc2 = cz.slice(0, wsp + 2).join("/");
          if (!w.dzieci.has(sc2)) w.dzieci.set(sc2, { sciezka: sc2, klucz: klucz(sc2, false), nazwa: cz.length > wsp + 2 ? cz[wsp + 1] + " /…" : cz[wsp + 1], liczba: 0 });
          w.dzieci.get(sc2).liczba += g.liczba;
        }
      });
      wynik.wezly = [...mapa.values()].sort((a, b) => b.liczba - a.liczba).concat(luzne);
      wynik.wezly.forEach((w) => { w.dzieci = [...w.dzieci.values()].sort((a, b) => b.liczba - a.liczba); });
      return wynik;
    }

    function wierszGrupy(w, poziom, rozwijalny) {
      const ukryta = [...S.ukryte].some((u) => pasuje(w.sciezka, u));
      const wybrana = S.wybor && pasuje(w.sciezka, S.wybor);
      const oko = el("button", { class: "v3d-g-oko", title: ukryta ? "Pokaż" : "Ukryj", "aria-label": (ukryta ? "Pokaż " : "Ukryj ") + w.nazwa,
        onclick: () => {
          if (S.ukryte.has(w.klucz)) S.ukryte.delete(w.klucz);
          else if (ukryta) { [...S.ukryte].forEach((u) => { if (pasuje(w.sciezka, u)) S.ukryte.delete(u); }); }
          else S.ukryte.add(w.klucz);
          zastosujWidocznosc();
          odswiezDrzewo();
        } }, ikona(ukryta ? "okoZ" : "oko"));
      const rozw = rozwijalny
        ? el("button", { class: "v3d-g-rozw" + (S.rozwiniete.has(w.sciezka) ? " otwarte" : ""), "aria-label": "Rozwiń", onclick: () => {
          if (S.rozwiniete.has(w.sciezka)) S.rozwiniete.delete(w.sciezka); else S.rozwiniete.add(w.sciezka);
          odswiezDrzewo();
        } }, ikona("prawo"))
        : el("span", { class: "v3d-g-rozw-pusty" });
      const nazwa = el("button", { class: "v3d-g-nazwa", title: w.sciezka, onclick: () => {
        if (matchMedia("(max-width: 720px)").matches) przelaczGrupy(false);   // telefon: zwolnij ekran dla arkusza
        wybierz(w.klucz, true);
      } },
        el("span", { class: "v3d-g-tekst", text: w.nazwa }), el("span", { class: "v3d-g-licz", text: liczba(w.liczba) }));
      return el("div", { class: "v3d-g-wiersz" + (ukryta ? " ukryta" : "") + (wybrana ? " wybrana" : "") + (poziom ? " dziecko" : "") }, rozw, nazwa, oko);
    }

    function odswiezDrzewo() {
      if (panelGrup.hidden) return;
      const { prefiks, wezly } = drzewo();
      const lista = el("div", { class: "v3d-g-lista" });
      for (const w of wezly) {
        lista.append(wierszGrupy(w, 0, w.dzieci.length > 0));
        if (w.dzieci.length && S.rozwiniete.has(w.sciezka)) for (const d of w.dzieci) lista.append(wierszGrupy(d, 1, false));
      }
      panelGrup.replaceChildren(
        el("div", { class: "v3d-grupy-glowa" },
          el("div", {}, el("div", { class: "karta-tytul", text: "Grupy" }), prefiks ? el("div", { class: "cichy-tekst v3d-sciezka", text: prefiks }) : null),
          el("button", { class: "przycisk cichy maly v3d-x", "aria-label": "Zamknij listę grup", onclick: () => przelaczGrupy(false) }, ikona("zamknij"))),
        wezly.length ? lista : el("p", { class: "cichy-tekst", text: "Ta migawka nie ma grup." }),
        S.ukryte.size ? el("button", { class: "przycisk cichy maly", text: "Pokaż wszystkie", onclick: () => { S.ukryte.clear(); zastosujWidocznosc(); odswiezDrzewo(); } }) : "");
    }

    // ---------------- komunikaty w scenie
    function pokazKomunikat(tekst, przycisk) {
      komunikat.replaceChildren(el("div", { class: "v3d-komunikat-tekst", text: tekst }), przycisk || "");
      komunikat.hidden = false;
    }
    function ukryjKomunikat() { komunikat.hidden = true; }

    // ---------------- zrzuty ekranu + powiększenie
    function pokazZrzuty(meta) {
      const lista = (meta && meta.zrzuty) || [];
      zrzutyEl.replaceChildren();
      zrzutyEl.hidden = !lista.length;
      if (!lista.length) return;
      const zBlendera = lista.every((nazwa) => /^blender_/i.test(nazwa));      // rendery dołączone zamiast zrzutów ze Studio
      zrzutyEl.append(el("div", { class: "v3d-zrzuty-tytul cichy-tekst",
        text: zBlendera ? "Rendery z Blendera — ta sama scena, którą zbudowano w Studio" : "Zrzuty ekranu ze Studio — tak to wygląda w grze" }));
      const pasek = el("div", { class: "v3d-zrzuty-pasek" });
      lista.forEach((nazwa, i) => {
        pasek.append(el("button", { class: "v3d-miniatura", "aria-label": "Powiększ zrzut " + (i + 1), onclick: () => powieksz(meta, i) },
          el("img", { src: urlPliku(meta.id, nazwa), alt: "Zrzut ekranu " + (i + 1), loading: "lazy", decoding: "async" })));
      });
      zrzutyEl.append(pasek);
    }

    function powieksz(meta, start) {
      const lista = meta.zrzuty || [];
      let i = start;
      const img = el("img", { class: "v3d-lightbox-img", alt: "" });
      const licznik = el("div", { class: "v3d-lightbox-licznik" });
      const ustaw = () => { img.src = urlPliku(meta.id, lista[i]); img.alt = "Zrzut ekranu " + (i + 1); licznik.textContent = (i + 1) + " / " + lista.length; };
      const zamknij = () => { box.remove(); document.removeEventListener("keydown", klaw); };
      const nast = (d) => { i = (i + d + lista.length) % lista.length; ustaw(); };
      const klaw = (e) => { if (e.key === "Escape") zamknij(); else if (e.key === "ArrowRight") nast(1); else if (e.key === "ArrowLeft") nast(-1); };
      const box = el("div", { class: "v3d-lightbox", role: "dialog", "aria-modal": "true", "aria-label": "Zrzut ekranu",
        onclick: (e) => { if (e.target === box || e.target === img) zamknij(); } },
        img, licznik,
        el("button", { class: "v3d-lightbox-x", "aria-label": "Zamknij", onclick: zamknij }, ikona("zamknij")),
        lista.length > 1 ? el("button", { class: "v3d-lightbox-nav lewo", "aria-label": "Poprzedni", onclick: (e) => { e.stopPropagation(); nast(-1); } }, ikona("lewo")) : null,
        lista.length > 1 ? el("button", { class: "v3d-lightbox-nav prawo", "aria-label": "Następny", onclick: (e) => { e.stopPropagation(); nast(1); } }, ikona("prawo")) : null);
      ustaw();
      document.addEventListener("keydown", klaw);
      document.body.append(box);
    }

    // ---------------- lista migawek
    function rysujListeMigawek() {
      const m = (S.lista && S.lista.migawki) || [];
      przyciskMigawek.hidden = m.length < 1;
      przyciskMigawek.firstChild.textContent = `Migawki (${m.length})`;
      listaMigawek.replaceChildren(el("div", { class: "lista" }, ...m.map((x) => el("button", {
        class: "wiersz v3d-mig" + (S.meta && S.meta.id === x.id ? " wybrana" : ""),
        onclick: () => { listaMigawek.hidden = true; przyciskMigawek.setAttribute("aria-expanded", "false"); otworzMigawke(x.id); },
      }, el("div", { class: "v3d-mig-tytul", text: x.tytul || x.id }),
      el("div", { class: "cichy-tekst", text: [x.kto, czasTemu(x.czas), liczba(x.czesci) + " " + czesciSlowo(x.czesci || 0), x.model ? "model GLB" : null].filter(Boolean).join(" · ") })))));
    }

    async function wczytajListe(otworzId) {
      try {
        S.lista = await ctx.api("/api/podglad");
      } catch (e) {
        if (e && e.status === 404) S.lista = { migawki: [] };
        else {
          pustyEl.hidden = false;
          scenaEl.hidden = true;
          pustyEl.replaceChildren(el("div", { class: "pusty-ikona" }, ikonaWspolna("ostrzezenie")),
            el("strong", { text: "Nie udało się wczytać listy migawek" }),
            el("p", { text: e.message || "Nieznany błąd." }),
            el("button", { class: "przycisk", text: "Spróbuj ponownie", onclick: () => wczytajListe(otworzId) }));
          return;
        }
      }
      const m = S.lista.migawki || [];
      // przy pustej liście jeden przycisk w stanie pustym zamiast dwóch (u góry i w środku)
      przyciskNowej.hidden = !lokalnieMoze() || !m.length;
      przyciskMigawek.hidden = !m.length;
      rysujListeMigawek();
      if (!m.length) {
        scenaEl.hidden = true;
        zrzutyEl.hidden = true;
        opisEl.textContent = "";
        tytulEl.textContent = "Podgląd 3D";
        metaEl.textContent = "";
        pustyEl.hidden = false;
        pustyEl.replaceChildren(
          el("div", { class: "pusty-ikona" }, ikonaWspolna("podglad")),
          el("strong", { text: "Nie ma jeszcze żadnej migawki świata gry" }),
          el("p", { class: "cichy-tekst", text: lokalnieMoze()
            ? "Otwórz miejsce gry w Roblox Studio i kliknij „Nowa migawka ze Studio” — albo uruchom w terminalu:"
            : "Migawkę robi się na komputerze z otwartym Roblox Studio przyciskiem „Nowa migawka ze Studio” albo poleceniem:" }),
          el("code", { class: "v3d-polecenie", text: 'python panel/narzedzia/migawka.py --tytul "Co pokazujemy"' }),
          lokalnieMoze() ? el("button", { class: "przycisk glowny", onclick: () => { formNowej.hidden = false; formNowej.querySelector("input")?.focus(); } }, ikona("aparat"), "Nowa migawka ze Studio") : "");
        return;
      }
      pustyEl.hidden = true;
      scenaEl.hidden = false;
      const docel = otworzId || (S.oczekujace && S.oczekujace.migawka) || (S.meta && S.meta.id) || S.lista.najnowsza || m[0].id;
      await otworzMigawke(docel);
    }

    async function otworzMigawke(id) {
      const m = (S.lista && S.lista.migawki) || [];
      const meta = m.find((x) => x.id === id) || m[0];
      if (!meta) return;
      if (S.meta && S.meta.id === meta.id && S.dane) { zastosujOczekujace(); return; }
      const nr = ++S.zadanie;
      S.meta = meta;
      S.wybor = null;
      S.ukryte.clear();
      S.rozwiniete.clear();
      arkusz.hidden = true;
      rysujListeMigawek();
      tytulEl.textContent = meta.tytul || "Migawka " + meta.id;
      metaEl.textContent = [meta.kto, czasTemu(meta.czas), liczba(meta.czesci) + " " + czesciSlowo(meta.czesci || 0),
        meta.miejsce && meta.miejsce.nazwa, meta.zrodlo === "blender" ? "z Blendera" : null].filter(Boolean).join(" · ");
      opisEl.textContent = meta.opis || "";
      pokazZrzuty(meta);
      if (S.bladWebGL) return;
      przygotujScene();
      if (!renderer) return;
      S.wczytywanie = true;
      pokazKomunikat(meta.czesci ? `Wczytuję ${liczba(meta.czesci)} ${czesciSlowo(meta.czesci)}…` : "Wczytuję…");
      statystyka.textContent = "";
      try {
        if (meta.model && /\.glb$/i.test(meta.model)) await wczytajGlb(meta, nr);
        else {
          const j = await ctx.api(`/api/podglad/${enc(meta.id)}/czesci`);
          if (nr !== S.zadanie) return;
          S.model = null;
          S.dane = przeanalizuj(j);
          zbudujModel();
        }
        if (nr !== S.zadanie) return;
        ukryjKomunikat();
        const D = S.dane;
        const rys = D.czesci ? D.czesci.length - D.pominiete : D.grupy.length;
        statystyka.textContent = S.model
          ? `model GLB · ${liczba(D.grupy.length)} obiektów`
          : `${liczba(rys)} ${czesciSlowo(rys)} · ${liczba(D.grupy.filter((g) => g.liczba).length)} grup` + (D.pominiete ? ` · ${liczba(D.pominiete)} niewidocznych pominięto` : "");
        odswiezDrzewo();
        ujecie("izo");
        if (S.anim) { S.anim.ms = 1; }
        zastosujOczekujace();
      } catch (e) {
        if (nr !== S.zadanie) return;
        S.dane = null;
        pokazKomunikat("Nie udało się wczytać migawki: " + (e.message || "błąd"),
          el("button", { class: "przycisk maly", text: "Spróbuj ponownie", onclick: () => { S.meta = null; otworzMigawke(id); } }));
      } finally {
        if (nr === S.zadanie) S.wczytywanie = false;
      }
    }

    async function wczytajGlb(meta, nr) {
      const { GLTFLoader } = await import("../vendor/GLTFLoader.js");
      const gltf = await new GLTFLoader().loadAsync(urlPliku(meta.id, meta.model));
      if (nr !== S.zadanie) return;
      wyczyscModel();
      const korzen = gltf.scene;
      korzen.userData.glb = true;
      let rodzice = korzen;
      while (rodzice.children.length === 1 && rodzice.children[0].children.length) rodzice = rodzice.children[0];
      const grupy = rodzice.children.map((o, i) => {
        const sciezka = "GLB/" + (o.name || "Obiekt " + (i + 1));
        o.userData.grupaGlb = sciezka;
        let n = 0;
        o.traverse((x) => { if (x.isMesh) { n++; x.castShadow = x.receiveShadow = false; } });
        return { sciezka, liczba: n || 1, obiekt: o, min: [0, 0, 0], max: [0, 0, 0] };
      });
      modelGrupa.add(korzen);
      S.model = korzen;
      const b = new T.Box3().setFromObject(korzen);
      S.dane = { grupy, czesci: null, pominiete: 0, ramka: { min: b.min.toArray(), max: b.max.toArray() }, calosc: null };
      renderer.shadowMap.enabled = false;
      dodajZiemie(S.dane.ramka, false);
      S.ramka = b.clone();
      S.promien = b.getSize(new T.Vector3()).length() / 2 || 50;
      S.poziomZiemi = b.min.y;
      zastosujWidocznosc();
      zastosujWybor();
    }

    function zastosujOczekujace() {
      const o = S.oczekujace;
      S.oczekujace = null;
      if (o && o.grupa && S.dane) {
        const k = klucz(String(o.grupa), false);
        const ist = S.dane.grupy.some((g) => pasuje(g.sciezka, k));
        if (ist) wybierz(k, true);
        else ctx.toast?.("W tej migawce nie ma grupy " + o.grupa, "blad");
      }
    }

    async function pokaz3d(parametry) {
      S.widoczny = true;
      const p = parametry || {};
      if (p.migawka || p.grupa) S.oczekujace = { migawka: p.migawka, grupa: p.grupa };
      try {
        if (!T) {
          pokazKomunikat("Wczytuję silnik 3D…");
          await zaladujThree();
          ukryjKomunikat();
        }
      } catch (e) {
        S.bladWebGL = "Nie udało się wczytać silnika 3D (three.js): " + e.message;
        pokazKomunikat(S.bladWebGL);
      }
      if (!S.lista) return wczytajListe(p.migawka);
      if (p.migawka && (!S.meta || S.meta.id !== p.migawka)) {
        if (!(S.lista.migawki || []).some((x) => x.id === p.migawka)) return wczytajListe(p.migawka);
        return otworzMigawke(p.migawka);
      }
      zastosujOczekujace();
      dopasujRozmiar();
      zaplanuj();
    }

    function ukryj3d() {
      S.widoczny = false;
      if (S.raf) cancelAnimationFrame(S.raf);
      S.raf = 0;
    }

    // ---------------- części zakładki: „Do przejrzenia” (wspolne/przeglad.js) i „Model 3D” (wyżej)
    let tryb = czytajTryb();
    const przel = przelacznik([
      { id: "przeglad", tekst: "Do przejrzenia", ikona: "obraz" },
      { id: "3d", tekst: "Model 3D", ikona: "podglad" },
    ], tryb, (id) => ustawTryb(id, {}), "Część podglądu");
    przel.classList.add("podglad-przelacznik");
    const przeglad = przegladAkceptacji(ctx, {
      naMigawke: (id) => ctx.idz("podglad", { migawka: id }),
      naLiczbe: (n) => przel.licznik("przeglad", n ? n : null),
    });
    const widok = elWspolny("div", { class: "podglad-widok" }, elWspolny("header", { class: "podglad-glowa" }, przel), przeglad.el, root);

    function ustawTryb(nowy, parametry) {
      tryb = nowy === "3d" ? "3d" : "przeglad";
      zapiszTryb(tryb);
      przel.ustaw(tryb);
      const trzyD = tryb === "3d";
      przeglad.el.hidden = trzyD;
      root.hidden = !trzyD;
      if (trzyD) {
        przeglad.ukryj();
        return pokaz3d(parametry || {});
      }
      ukryj3d();
      przeglad.pokaz();
      return undefined;
    }

    return {
      el: widok,
      pokaz(parametry) {
        const p = parametry || {};
        let t = tryb;
        if (p.migawka || p.grupa || p.zakladka === "3d") t = "3d";
        else if (p.zakladka === "przeglad") t = "przeglad";
        return ustawTryb(t, p);
      },
      ukryj() {
        przeglad.ukryj();
        ukryj3d();
      },
    };
  },
};

async function zaladujThree() {
  if (T) return;
  const [t, o] = await Promise.all([import("../vendor/three.module.min.js"), import("../vendor/OrbitControls.js")]);
  Orbit = o.OrbitControls;
  T = t;
}
