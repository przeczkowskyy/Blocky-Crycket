// Sieć neuronowa — graf sejfu Obsidiana w przeglądarce (druga osoba nie musi mieć Obsidiana).
// Canvas 2D + własna symulacja sił (Barnes–Hut). Symulacja zasypia po ustabilizowaniu i budzi się przy interakcji.

import { ikona as ikonaWspolna } from "../wspolne/ui.js";

const CSS = new URL("./siec.css", import.meta.url).href;
const PALETA = ["#f5b82e", "#8b5cf6", "#3ecf8e", "#4ea8ff", "#ef5a5a", "#f08bd0", "#5fd4d0", "#c9a37a", "#9aa3b8"];
const DOBA48 = 48 * 3600 * 1000;

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
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  dopasuj: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
  zamknij: '<path d="M6 6l12 12M18 6L6 18"/>',
  szukaj: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
  komentarz: '<path d="M4 5h16v11H9l-5 4z"/>',
  agent: '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01"/>',
  wstecz: '<path d="M15 6l-6 6 6 6"/>',
};
// te ikony bierzemy ze wspólnego zestawu (ui.js), żeby wyglądały tak samo jak w reszcie panelu
const IKONY_WSPOLNE = new Set(["plus", "zamknij", "komentarz", "agent"]);
function ikona(n) {
  const s = el("span", { class: "sn-ik", "aria-hidden": "true" });
  if (IKONY_WSPOLNE.has(n)) {
    s.append(ikonaWspolna(n));
    return s;
  }
  s.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + (IKONY[n] || "") + "</svg>";
  return s;
}

function czasTemu(iso) {
  const t = Date.parse(iso);
  if (!t) return "";
  const s = (Date.now() - t) / 1000;
  if (s < 60) return "przed chwilą";
  if (s < 3600) return Math.round(s / 60) + " min temu";
  if (s < 86400) return Math.round(s / 3600) + " h temu";
  if (s < 2 * 86400) return "wczoraj";
  if (s < 30 * 86400) return Math.round(s / 86400) + " dni temu";
  return new Date(t).toLocaleDateString("pl-PL", { day: "numeric", month: "short", year: "numeric" });
}

const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
const baza = (sc) => String(sc || "").split("/").pop().replace(/\.md$/i, "");

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Zastępczy Markdown (gdy wspolne/markdown.js jeszcze nie istnieje): bezpieczny tekst + wikilinki + akapity.
function mdZastepczy(tekst) {
  return esc(tekst || "")
    .replace(/\[\[([^\]|#]+)(#[^\]|]*)?(\|([^\]]+))?\]\]/g, (_, n, h, __, alias) => `<a href="#" data-wikilink="${n.trim()}">${alias || n}</a>`)
    .replace(/^#{1,6} (.*)$/gm, "<strong>$1</strong>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .split(/\n{2,}/).map((p) => "<p>" + p.replace(/\n/g, "<br>") + "</p>").join("");
}

let mdFn = null;
async function renderujMd(tekst) {
  if (!mdFn) {
    try {
      const m = await import("../wspolne/markdown.js");
      mdFn = m.md || m.default;
    } catch (e) { /* jeszcze nie ma modułu wspólnego — zastępnik do przeładowania strony */ }
    if (typeof mdFn !== "function") mdFn = mdZastepczy;
  }
  return mdFn(tekst);
}

async function sekcjaKomentarzy(ctx, cel) {
  try {
    const m = await import("../wspolne/komentarze.js");
    const f = m.komentarze || m.default;
    if (typeof f === "function") return f(ctx, cel);
  } catch (e) { /* zastępnik niżej */ }
  const lista = el("div", { class: "sn-kom-lista" }, el("p", { class: "cichy-tekst", text: "Wczytuję komentarze…" }));
  const wrap = el("div", { class: "sn-kom" }, lista);
  const odswiez = async () => {
    try {
      const d = await ctx.api(`/api/komentarze?typ=${encodeURIComponent(cel.typ)}&cel=${encodeURIComponent(cel.cel)}`);
      lista.replaceChildren(...(d.komentarze || []).map((k) => el("div", { class: "wiersz" },
        el("b", { text: k.kto || "ktoś" }), " ", el("span", { class: "cichy-tekst", text: czasTemu(k.czas) }), el("div", { text: k.tekst || "" }))));
      if (!lista.children.length) lista.append(el("p", { class: "cichy-tekst", text: "Nikt jeszcze tego nie skomentował." }));
    } catch (e) {
      lista.replaceChildren(el("p", { class: "cichy-tekst", text: "Nie udało się wczytać komentarzy: " + e.message }));
    }
  };
  odswiez();
  if (!ctx.statyczny) {
    const pole = el("textarea", { class: "pole", rows: "2", placeholder: "Napisz komentarz…" });
    const b = el("button", { class: "przycisk glowny maly", text: "Wyślij", onclick: async () => {
      if (!pole.value.trim()) return;
      b.disabled = true;
      try { await ctx.api("/api/komentarze", { metoda: "POST", cialo: { cel, tekst: pole.value.trim() } }); pole.value = ""; odswiez(); }
      catch (e) { ctx.toast?.("Nie wysłano komentarza: " + e.message, "blad"); }
      finally { b.disabled = false; }
    } });
    wrap.append(pole, b);
  }
  return wrap;
}

// ------------------------------------------------------------------ symulacja sił
function utworzSymulacje() {
  const sim = {
    n: 0, x: null, y: null, vx: null, vy: null, staly: null, kx: null, ky: null,
    zr: null, cel: null, sila: null, bias: null, dl: null,
    alfa: 1, alfaCel: 0, alfaMin: 0.003, rozpad: 0.0228, tarcie: 0.42, ladunek: -38, teta2: 0.81,
  };

  sim.ustaw = (wezly, krawedzie, pozycje) => {
    const n = wezly.length;
    sim.n = n;
    sim.x = new Float64Array(n); sim.y = new Float64Array(n);
    sim.vx = new Float64Array(n); sim.vy = new Float64Array(n);
    sim.staly = new Uint8Array(n);
    sim.kx = new Float64Array(n); sim.ky = new Float64Array(n);
    // kotwice kategorii na okręgu — lekkie skupianie
    const kat = [...new Set(wezly.map((w) => w._kat))];
    const R = 60 + Math.sqrt(n) * 14;
    const kot = new Map(kat.map((k, i) => [k, [Math.cos((i / kat.length) * 2 * Math.PI) * R, Math.sin((i / kat.length) * 2 * Math.PI) * R]]));
    const liczba = new Int32Array(n);
    for (const [a, b] of krawedzie) { liczba[a]++; liczba[b]++; }
    sim.zr = Int32Array.from(krawedzie.map((k) => k[0]));
    sim.cel = Int32Array.from(krawedzie.map((k) => k[1]));
    sim.sila = Float64Array.from(krawedzie.map(([a, b]) => 1 / Math.min(Math.max(liczba[a], 1), Math.max(liczba[b], 1))));
    sim.bias = Float64Array.from(krawedzie.map(([a, b]) => liczba[a] / ((liczba[a] + liczba[b]) || 1)));
    sim.dl = Float64Array.from(krawedzie.map(([a, b]) => 36 + 3 * Math.sqrt(liczba[a] + liczba[b])));
    // gęsty sejf (dużo linków na notatkę) potrzebuje mocniejszego odpychania, inaczej węzły się sklejają
    const sredniStopien = n ? (2 * krawedzie.length) / n : 0;
    sim.ladunek = -40 - 4 * Math.min(sredniStopien, 20);
    sim.r = Float64Array.from(wezly.map((w) => w._r));
    let noweN = 0;
    wezly.forEach((w, i) => {
      const [ax, ay] = kot.get(w._kat);
      sim.kx[i] = ax; sim.ky[i] = ay;
      const p = pozycje && pozycje.get(w.sciezka);
      if (p) { sim.x[i] = p[0]; sim.y[i] = p[1]; return; }
      noweN++;
      // stabilny „losowy” start (spirala wokół kotwicy) — ten sam układ po każdym wczytaniu
      const r = 10 * Math.sqrt(0.5 + i), a = i * Math.PI * (3 - Math.sqrt(5));
      sim.x[i] = ax * 0.6 + r * Math.cos(a);
      sim.y[i] = ay * 0.6 + r * Math.sin(a);
    });
    sim.alfa = noweN > n * 0.3 ? 1 : 0.3;
  };

  // drzewo czwórkowe dla odpychania
  function drzewo() {
    const { n, x, y } = sim;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (let i = 0; i < n; i++) {
      if (x[i] < x0) x0 = x[i]; if (x[i] > x1) x1 = x[i];
      if (y[i] < y0) y0 = y[i]; if (y[i] > y1) y1 = y[i];
    }
    const s = Math.max(x1 - x0, y1 - y0, 1) + 1;
    const kor = { x0, y0, s, m: 0, cx: 0, cy: 0, i: -1, d: null };
    for (let i = 0; i < n; i++) wstaw(kor, i, 0);
    return kor;
  }
  function wstaw(w, i, gl) {
    const x = sim.x[i], y = sim.y[i];
    if (w.m === 0 && !w.d) { w.i = i; w.m = 1; w.cx = x; w.cy = y; return; }
    w.cx = (w.cx * w.m + x) / (w.m + 1);
    w.cy = (w.cy * w.m + y) / (w.m + 1);
    w.m++;
    if (gl > 24) return;                                   // pokrywające się punkty: agregat w liściu
    if (!w.d) {
      w.d = [null, null, null, null];
      const st = w.i;
      w.i = -1;
      if (st >= 0) wstawDoDziecka(w, st, gl);
    }
    wstawDoDziecka(w, i, gl);
  }
  function wstawDoDziecka(w, i, gl) {
    const h = w.s / 2;
    const p = (sim.x[i] >= w.x0 + h ? 1 : 0) + (sim.y[i] >= w.y0 + h ? 2 : 0);
    if (!w.d[p]) w.d[p] = { x0: w.x0 + (p & 1 ? h : 0), y0: w.y0 + (p & 2 ? h : 0), s: h, m: 0, cx: 0, cy: 0, i: -1, d: null };
    wstaw(w.d[p], i, gl + 1);
  }
  function odpychaj(w, i, alfa) {
    if (!w || w.m === 0) return;
    if (!w.d && w.i === i) return;
    let dx = w.cx - sim.x[i], dy = w.cy - sim.y[i];
    let d2 = dx * dx + dy * dy;
    if (!w.d || (w.s * w.s) / d2 < sim.teta2) {
      if (d2 < 1) { dx = (i % 7) * 0.1 - 0.3 || 0.1; dy = (i % 5) * 0.1 - 0.2 || 0.1; d2 = Math.max(d2, 1); }
      const m = w.d ? w.m : (w.i === i ? w.m - 1 : w.m);
      const f = (sim.ladunek * m * alfa) / d2;
      sim.vx[i] += dx * f;
      sim.vy[i] += dy * f;
      return;
    }
    for (const c of w.d) odpychaj(c, i, alfa);
  }

  sim.krok = () => {
    const { n, x, y, vx, vy } = sim;
    const alfa = (sim.alfa += (sim.alfaCel - sim.alfa) * sim.rozpad);
    const kor = drzewo();
    for (let i = 0; i < n; i++) odpychaj(kor, i, alfa);
    // sprężyny krawędzi
    for (let e = 0; e < sim.zr.length; e++) {
      const a = sim.zr[e], b = sim.cel[e];
      let dx = x[b] + vx[b] - x[a] - vx[a] || 0.01, dy = y[b] + vy[b] - y[a] - vy[a] || 0.01;
      let l = Math.sqrt(dx * dx + dy * dy);
      l = ((l - sim.dl[e]) / l) * alfa * sim.sila[e];
      dx *= l; dy *= l;
      const bb = sim.bias[e];
      vx[b] -= dx * bb; vy[b] -= dy * bb;
      vx[a] += dx * (1 - bb); vy[a] += dy * (1 - bb);
    }
    // przyciąganie do kotwicy kategorii i do środka
    for (let i = 0; i < n; i++) {
      vx[i] += ((sim.kx[i] - x[i]) * 0.035 - x[i] * 0.012) * alfa;
      vy[i] += ((sim.ky[i] - y[i]) * 0.035 - y[i] * 0.012) * alfa;
    }
    // lekkie zderzenia (tylko dla mniejszych sejfów — koszt n²)
    if (n <= 600) {
      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          const dx = x[j] + vx[j] - x[i] - vx[i], dy = y[j] + vy[j] - y[i] - vy[i];
          const min = sim.r[i] + sim.r[j] + 3;
          const d2 = dx * dx + dy * dy;
          if (d2 >= min * min) continue;
          const d = Math.sqrt(d2) || 0.01;
          const f = ((min - d) / d) * 0.35;
          vx[i] -= dx * f; vy[i] -= dy * f;
          vx[j] += dx * f; vy[j] += dy * f;
        }
      }
    }
    for (let i = 0; i < n; i++) {
      if (sim.staly[i]) { vx[i] = vy[i] = 0; continue; }
      vx[i] *= 1 - sim.tarcie; vy[i] *= 1 - sim.tarcie;
      x[i] += vx[i]; y[i] += vy[i];
    }
  };
  sim.dziala = () => sim.alfa >= sim.alfaMin || sim.alfaCel > 0;
  sim.obudz = (a = 0.3) => { sim.alfa = Math.max(sim.alfa, a); };
  return sim;
}

// ------------------------------------------------------------------ widok
export default {
  id: "siec",
  tytul: "Sieć neuronowa",
  ikona: "siec",
  kolejnosc: 60,
  utworz(ctx) {
    dolaczCss(CSS);
    const sim = utworzSymulacje();
    const S = {
      widoczny: false, dane: null, wczytano: 0, wezly: [], krawedzie: [], sasiedzi: [], kategorie: [], kolor: new Map(),
      ukryteKat: new Set(), sejf: null, wybrany: -1, trafienia: null, szukaj: "", oczekujaca: null,
      k: 1, tx: 0, ty: 0, w: 0, h: 0, dpr: 1, raf: 0, timer: 0, anim: null, dotkniete: false, hubPrag: 3,
      ostatnio: 0, historia: [],
    };
    const enc = encodeURIComponent;

    // ---------------- DOM
    const statEl = el("div", { class: "sn-stat cichy-tekst" });
    const poleSzukaj = el("input", { class: "pole sn-szukaj", type: "search", placeholder: "Szukaj notatki…", "aria-label": "Szukaj notatki", enterkeyhint: "search" });
    const trafieniaEl = el("span", { class: "sn-trafienia cichy-tekst" });
    const sejfyEl = el("div", { class: "sn-sejfy" });
    const legendaEl = el("div", { class: "sn-legenda" });
    const gora = el("div", { class: "sn-gora" },
      el("div", { class: "sn-gora-tekst" }, el("h2", { class: "sn-tytul", text: "Sieć neuronowa" }), statEl),
      el("div", { class: "sn-szukaj-wrap" }, ikona("szukaj"), poleSzukaj, trafieniaEl));
    const plotno = el("canvas", { class: "sn-plotno", "aria-label": "Graf powiązań notatek sejfu" });
    const komunikat = el("div", { class: "sn-komunikat", hidden: true });
    const szuflada = el("aside", { class: "sn-szuflada", hidden: true, "aria-label": "Notatka" });
    const sterowanie = el("div", { class: "sn-sterowanie" },
      el("button", { class: "sn-btn", "aria-label": "Przybliż", title: "Przybliż", onclick: () => zoomO(1.4) }, ikona("plus")),
      el("button", { class: "sn-btn", "aria-label": "Oddal", title: "Oddal", onclick: () => zoomO(1 / 1.4) }, ikona("minus")),
      el("button", { class: "sn-btn", "aria-label": "Pokaż całość", title: "Pokaż całość", onclick: () => dopasuj(true) }, ikona("dopasuj")));
    const scena = el("div", { class: "sn-scena" }, plotno, sterowanie, komunikat, szuflada);
    const pustyEl = el("div", { class: "pusty", hidden: true });
    const root = el("section", { class: "sn" }, gora, sejfyEl, legendaEl, pustyEl, scena);
    const g2 = plotno.getContext("2d");

    // ---------------- dane
    function kolorKategorii(w) {
      return S.kolor.get(w._kat) || "#9aa3b8";
    }

    function przygotuj(d, stare) {
      const kat = d.kategorie || [];
      S.kolor = new Map();
      S.kategorie = kat.map((k, i) => {
        const id = k.id != null ? String(k.id) : (k.sejf || "") + "|" + k.nazwa;
        const kol = k.kolor || PALETA[i % PALETA.length];
        S.kolor.set(id, kol);
        return { id, nazwa: k.nazwa || String(k.id), sejf: k.sejf, kolor: kol, liczba: k.liczba || 0 };
      });
      const poNazwie = new Map(S.kategorie.map((k) => [(k.sejf || "") + "|" + k.nazwa, k.id]));
      const poId = new Set(S.kategorie.map((k) => k.id));
      S.wezly = (d.wezly || []).map((w, i) => {
        let kk = String(w.kategoria ?? "(korzeń)");
        if (!poId.has(kk)) kk = poNazwie.get((w.sejf || "") + "|" + kk) || poNazwie.get("|" + kk) || kk;
        if (!S.kolor.has(kk)) {
          S.kolor.set(kk, PALETA[S.kategorie.length % PALETA.length]);
          S.kategorie.push({ id: kk, nazwa: String(w.kategoria ?? kk), sejf: w.sejf, kolor: S.kolor.get(kk), liczba: 0 });
        }
        const zm = Date.parse(w.zmieniono) || 0;
        return Object.assign({}, w, { _i: i, _kat: kk, _r: 3.5 + Math.sqrt(w.stopien || 0) * 1.25, _swiezy: zm && Date.now() - zm < DOBA48,
          _szuk: norm([w.tytul, baza(w.sciezka), (w.tagi || []).join(" ")].join(" ")) });
      });
      for (const k of S.kategorie) if (!k.liczba) k.liczba = S.wezly.filter((w) => w._kat === k.id).length;
      const n = S.wezly.length;
      S.krawedzie = (d.krawedzie || []).filter(([a, b]) => a >= 0 && b >= 0 && a < n && b < n && a !== b);
      S.sasiedzi = S.wezly.map(() => []);
      for (const [a, b] of S.krawedzie) { S.sasiedzi[a].push(b); S.sasiedzi[b].push(a); }
      const st = S.wezly.map((w) => S.sasiedzi[w._i].length).sort((a, b) => b - a);
      S.hubPrag = Math.max(3, st[Math.min(st.length - 1, Math.floor(st.length * 0.08))] || 3, st[Math.min(st.length - 1, 24)] || 0);
      sim.ustaw(S.wezly, S.krawedzie, stare);
      S.dane = d;
    }

    async function wczytaj(cicho) {
      if (!cicho) pokazKomunikat("Wczytuję sieć notatek…");
      try {
        const d = await ctx.api("/api/sejf/siec");
        let stare = null;
        if (S.wezly.length) {
          stare = new Map(S.wezly.map((w) => [w.sciezka, [sim.x[w._i], sim.y[w._i]]]));
        }
        const wybranaSc = S.wybrany >= 0 ? S.wezly[S.wybrany].sciezka : null;
        przygotuj(d, stare);
        S.wybrany = wybranaSc ? S.wezly.findIndex((w) => w.sciezka === wybranaSc) : -1;
        S.wczytano = Date.now();
        ukryjKomunikat();
        rysujPasy();
        if (!S.wezly.length) {
          scena.hidden = true;
          pustyEl.hidden = false;
          pustyEl.replaceChildren(el("p", { text: "W sejfie nie ma jeszcze notatek do pokazania." }),
            el("p", { class: "cichy-tekst", text: "Sprawdź, czy folder sejfu istnieje (konfiguracja panelu → sejfy) i czy są w nim pliki .md." }));
          return;
        }
        scena.hidden = false;
        pustyEl.hidden = true;
        rozmiar();
        if (!stare) {
          // rozgrzewka: kilkadziesiąt kroków przed pierwszym rysunkiem, żeby nie było „wybuchu”
          const kroki = S.wezly.length > 1500 ? 50 : S.wezly.length > 500 ? 120 : 220;
          for (let i = 0; i < kroki; i++) sim.krok();
          dopasuj(false);
        }
        szukaj(poleSzukaj.value);
        zastosujOczekujaca();
        zaplanuj();
      } catch (e) {
        if (cicho) return;
        pokazKomunikat("Nie udało się wczytać sieci: " + (e.message || "błąd"),
          el("button", { class: "przycisk maly", text: "Spróbuj ponownie", onclick: () => wczytaj() }));
      }
    }

    // ---------------- pasy: sejfy i legenda kategorii
    function rysujPasy() {
      const sejfy = [...new Set(S.wezly.map((w) => w.sejf).filter(Boolean))];
      const nazwaSejfu = (id) => ((ctx.konfiguracja && ctx.konfiguracja.sejfy) || []).find((s) => s.id === id)?.nazwa || id;
      sejfyEl.replaceChildren();
      sejfyEl.hidden = sejfy.length < 2;
      if (sejfy.length >= 2) {
        const chip = (id, tekst) => el("button", { class: "chip sn-chip" + (S.sejf === id ? " aktywny" : ""), "aria-pressed": String(S.sejf === id),
          onclick: () => { S.sejf = id; rysujPasy(); sim.obudz(0.2); zaplanuj(); dopasuj(true); } }, tekst);
        sejfyEl.append(chip(null, "Wszystkie sejfy"), ...sejfy.map((s) => chip(s, nazwaSejfu(s))));
      }
      const kat = S.kategorie.filter((k) => k.liczba > 0 && (!S.sejf || !k.sejf || k.sejf === S.sejf));
      legendaEl.replaceChildren(...kat.map((k) => {
        const wyl = S.ukryteKat.has(k.id);
        return el("button", { class: "chip sn-chip" + (wyl ? " wylaczony" : ""), "aria-pressed": String(!wyl), title: wyl ? "Pokaż kategorię" : "Ukryj kategorię",
          onclick: () => { if (wyl) S.ukryteKat.delete(k.id); else S.ukryteKat.add(k.id); rysujPasy(); zaplanuj(); } },
        el("span", { class: "sn-kropka", style: `background:${k.kolor}` }), k.nazwa, el("span", { class: "sn-licz", text: String(k.liczba) }));
      }));
      const st = (S.dane && S.dane.statystyki) || {};
      const nier = (S.dane && S.dane.nierozwiazane) || [];
      statEl.textContent = [`${st.notatki ?? S.wezly.length} notatek`, `${st.powiazania ?? S.krawedzie.length} powiązań`,
        nier.length ? `${nier.length} linków bez celu` : null].filter(Boolean).join(" · ");
    }

    const widoczny = (w) => !S.ukryteKat.has(w._kat) && (!S.sejf || w.sejf === S.sejf);

    // ---------------- kamera
    function rozmiar() {
      const r = plotno.getBoundingClientRect();
      if (!r.width || !r.height) return;
      S.dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.round(r.width), h = Math.round(r.height);
      if (w !== S.w || h !== S.h || plotno.width !== Math.round(w * S.dpr)) {
        const cx = (S.w / 2 - S.tx) / S.k, cy = (S.h / 2 - S.ty) / S.k;
        const bylo = S.w > 0;
        S.w = w; S.h = h;
        plotno.width = Math.round(w * S.dpr);
        plotno.height = Math.round(h * S.dpr);
        if (bylo) { S.tx = w / 2 - cx * S.k; S.ty = h / 2 - cy * S.k; }
      }
      zaplanuj();
    }

    function animujKamere(k, tx, ty, ms = 420) {
      S.anim = { t0: null, ms, k0: S.k, tx0: S.tx, ty0: S.ty, k, tx, ty };
      zaplanuj();
    }

    function dopasuj(anim) {
      const w = S.wezly.filter(widoczny);
      if (!w.length || !S.w) return;
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const n of w) {
        const x = sim.x[n._i], y = sim.y[n._i];
        x0 = Math.min(x0, x - n._r); x1 = Math.max(x1, x + n._r);
        y0 = Math.min(y0, y - n._r); y1 = Math.max(y1, y + n._r);
      }
      const pad = 40;
      const k = Math.max(0.08, Math.min(3, Math.min((S.w - pad * 2) / Math.max(x1 - x0, 1), (S.h - pad * 2) / Math.max(y1 - y0, 1))));
      const tx = S.w / 2 - ((x0 + x1) / 2) * k, ty = S.h / 2 - ((y0 + y1) / 2) * k;
      if (anim) animujKamere(k, tx, ty); else { S.k = k; S.tx = tx; S.ty = ty; zaplanuj(); }
    }

    function wysrodkuj(i, k) {
      const kk = Math.max(S.k, k || 1.2);
      // na telefonie szuflada zakrywa dół — węzeł w górnej części ekranu
      const telefon = matchMedia("(max-width: 720px)").matches;
      const szer = !telefon && !szuflada.hidden ? S.w - Math.min(420, S.w * 0.45) : S.w;
      const cy = telefon ? S.h * 0.22 : S.h / 2;
      animujKamere(kk, szer / 2 - sim.x[i] * kk, cy - sim.y[i] * kk);
    }

    function zoomO(f, sx, sy) {
      S.dotkniete = true;
      const px = sx ?? S.w / 2, py = sy ?? S.h / 2;
      const k = Math.max(0.05, Math.min(8, S.k * f));
      const wx = (px - S.tx) / S.k, wy = (py - S.ty) / S.k;
      S.k = k;
      S.tx = px - wx * k;
      S.ty = py - wy * k;
      S.anim = null;
      zaplanuj();
    }

    // ---------------- pętla: symulacja + rysowanie (śpi, gdy nic się nie dzieje)
    function zaplanuj() {
      if (!S.widoczny || S.raf) return;
      if (S.timer) { clearTimeout(S.timer); S.timer = 0; }
      S.raf = requestAnimationFrame(klatka);
    }

    function klatka(t) {
      S.raf = 0;
      let dalej = false;
      if (sim.dziala() && S.wezly.length) {
        sim.krok();
        dalej = true;
        if (!sim.dziala() && !S.dotkniete) dopasuj(true);
      }
      if (S.anim) {
        const a = S.anim;
        if (a.t0 == null) a.t0 = t;
        const u = Math.min(1, (t - a.t0) / a.ms);
        const e = 1 - Math.pow(1 - u, 3);
        S.k = a.k0 + (a.k - a.k0) * e;
        S.tx = a.tx0 + (a.tx - a.tx0) * e;
        S.ty = a.ty0 + (a.ty - a.ty0) * e;
        if (u >= 1) S.anim = null; else dalej = true;
      }
      rysuj(t);
      if (dalej) zaplanuj();
      else if (S.pulsuje && S.widoczny) {
        // tylko pulsowanie świeżych notatek: ok. 12 klatek/s zamiast 60 — oszczędza baterię
        S.timer = setTimeout(() => { S.timer = 0; zaplanuj(); }, 80);
      }
    }

    const sprite = new Map();
    function poswiata(kolor) {
      if (sprite.has(kolor)) return sprite.get(kolor);
      const c = document.createElement("canvas");
      c.width = c.height = 64;
      const g = c.getContext("2d");
      const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      gr.addColorStop(0, kolor + "88");
      gr.addColorStop(0.45, kolor + "33");
      gr.addColorStop(1, kolor + "00");
      g.fillStyle = gr;
      g.fillRect(0, 0, 64, 64);
      sprite.set(kolor, c);
      return c;
    }

    function rysuj(t) {
      const g = g2, n = S.wezly.length;
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.clearRect(0, 0, plotno.width, plotno.height);
      if (!n) return;
      const d = S.dpr, k = S.k;
      g.setTransform(d * k, 0, 0, d * k, d * S.tx, d * S.ty);
      const wyb = S.wybrany;
      const sas = wyb >= 0 ? new Set(S.sasiedzi[wyb]) : null;
      const traf = S.trafienia;
      const vis = S.wezly.map(widoczny);
      // krawędzie
      g.lineWidth = 1 / k;
      g.strokeStyle = wyb >= 0 || traf ? "rgba(154,163,184,0.07)" : "rgba(154,163,184,0.28)";
      g.beginPath();
      for (const [a, b] of S.krawedzie) {
        if (!vis[a] || !vis[b]) continue;
        if (wyb >= 0 && (a === wyb || b === wyb)) continue;
        g.moveTo(sim.x[a], sim.y[a]);
        g.lineTo(sim.x[b], sim.y[b]);
      }
      g.stroke();
      if (wyb >= 0) {
        g.lineWidth = 1.6 / k;
        g.strokeStyle = "rgba(245,184,46,0.85)";
        g.beginPath();
        for (const b of S.sasiedzi[wyb]) {
          if (!vis[b]) continue;
          g.moveTo(sim.x[wyb], sim.y[wyb]);
          g.lineTo(sim.x[b], sim.y[b]);
        }
        g.stroke();
      }
      // węzły
      const faza = (t || 0) / 1000;
      S.pulsuje = false;
      for (let i = 0; i < n; i++) {
        if (!vis[i]) continue;
        const w = S.wezly[i];
        const x = sim.x[i], y = sim.y[i], r = w._r;
        const aktywny = (wyb < 0 && !traf) || i === wyb || (sas && sas.has(i)) || (traf && traf.has(i));
        const kol = kolorKategorii(w);
        g.globalAlpha = aktywny ? 1 : 0.16;
        if (w._swiezy) {
          S.pulsuje = true;
          const p = 0.5 + 0.5 * Math.sin(faza * 2.4 + i);
          const rr = r * (2.6 + 0.9 * p);
          g.globalAlpha = (aktywny ? 0.55 + 0.45 * p : 0.12);
          g.drawImage(poswiata(kol), x - rr, y - rr, rr * 2, rr * 2);
          g.globalAlpha = aktywny ? 1 : 0.16;
        } else if (aktywny) {
          const rr = r * 2.3;
          g.drawImage(poswiata(kol), x - rr, y - rr, rr * 2, rr * 2);
        }
        g.fillStyle = kol;
        g.beginPath();
        g.arc(x, y, r, 0, Math.PI * 2);
        g.fill();
        if (i === wyb || (traf && traf.has(i))) {
          g.lineWidth = 2.2 / k;
          g.strokeStyle = "#fff6dc";
          g.stroke();
        }
      }
      g.globalAlpha = 1;
      // etykiety (w pikselach ekranu, stała wielkość)
      g.setTransform(d, 0, 0, d, 0, 0);
      g.font = "600 12px system-ui, 'Segoe UI', sans-serif";
      g.textAlign = "center";
      g.textBaseline = "top";
      g.lineJoin = "round";
      const zblizenie = k >= 1.5;
      // kandydaci na etykiety w kolejności ważności; etykieta, która nachodzi na już narysowaną, jest pomijana
      const kandydaci = [];
      for (let i = 0; i < n; i++) {
        if (!vis[i]) continue;
        const wazny = i === wyb || (sas && sas.has(i)) || (traf && traf.has(i) && traf.size <= 40);
        const hub = S.sasiedzi[i].length >= S.hubPrag;
        if (!(wazny || (hub && !(wyb >= 0 || traf)) || (zblizenie && !(wyb >= 0 || traf)))) continue;
        const sx = sim.x[i] * k + S.tx, sy = sim.y[i] * k + S.ty + S.wezly[i]._r * k + 3;
        if (sx < -80 || sx > S.w + 80 || sy < -20 || sy > S.h + 20) continue;
        kandydaci.push({ i, sx, sy, hub, wazny, waga: (i === wyb ? 1e6 : 0) + (wazny ? 1e4 : 0) + S.sasiedzi[i].length });
      }
      kandydaci.sort((a, b) => b.waga - a.waga);
      const zajete = [];
      for (const c of kandydaci.slice(0, 160)) {
        const w = S.wezly[c.i];
        let tekst = w.tytul || baza(w.sciezka);
        if (tekst.length > 34) tekst = tekst.slice(0, 32) + "…";
        const sz = g.measureText(tekst).width;
        const r = [c.sx - sz / 2 - 2, c.sy - 1, c.sx + sz / 2 + 2, c.sy + 15];
        if (c.i !== wyb && zajete.some((z) => r[0] < z[2] && r[2] > z[0] && r[1] < z[3] && r[3] > z[1])) continue;
        zajete.push(r);
        g.lineWidth = 3.5;
        g.strokeStyle = "rgba(18,20,28,0.92)";
        g.strokeText(tekst, c.sx, c.sy);
        g.fillStyle = c.i === wyb ? "#f5b82e" : (c.hub || c.wazny ? "#e8eaf2" : "#c3c9d8");
        g.fillText(tekst, c.sx, c.sy);
      }
    }

    // ---------------- interakcja: przesuwanie, zoom, przeciąganie węzłów
    const wskazniki = new Map();
    let gest = null;

    function wezelPod(sx, sy) {
      const wx = (sx - S.tx) / S.k, wy = (sy - S.ty) / S.k;
      let best = -1, bd = Infinity;
      for (let i = 0; i < S.wezly.length; i++) {
        if (!widoczny(S.wezly[i])) continue;
        const dx = sim.x[i] - wx, dy = sim.y[i] - wy;
        const d2 = dx * dx + dy * dy;
        const lim = S.wezly[i]._r + 8 / S.k;
        if (d2 < lim * lim && d2 < bd) { bd = d2; best = i; }
      }
      return best;
    }

    const pozycja = (e) => { const r = plotno.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };

    plotno.addEventListener("pointerdown", (e) => {
      plotno.setPointerCapture(e.pointerId);
      const [x, y] = pozycja(e);
      wskazniki.set(e.pointerId, { x, y });
      S.anim = null;
      if (wskazniki.size === 1) {
        const i = wezelPod(x, y);
        gest = { typ: i >= 0 ? "wezel" : "przesun", i, x0: x, y0: y, lx: x, ly: y, t0: performance.now(), ruch: 0 };
      } else if (wskazniki.size === 2) {
        if (gest && gest.typ === "wezel") { sim.staly[gest.i] = 0; sim.alfaCel = 0; }
        const [a, b] = [...wskazniki.values()];
        gest = { typ: "szczypanie", d0: Math.hypot(a.x - b.x, a.y - b.y), k0: S.k, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2, ruch: 99 };
      }
    });
    plotno.addEventListener("pointermove", (e) => {
      if (!wskazniki.has(e.pointerId)) {
        if (e.pointerType === "mouse") plotno.style.cursor = wezelPod(...pozycja(e)) >= 0 ? "pointer" : "grab";
        return;
      }
      const [x, y] = pozycja(e);
      wskazniki.set(e.pointerId, { x, y });
      if (!gest) return;
      if (gest.typ === "szczypanie" && wskazniki.size >= 2) {
        const [a, b] = [...wskazniki.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
        S.tx += mx - gest.mx; S.ty += my - gest.my;
        gest.mx = mx; gest.my = my;
        zoomO((gest.k0 * d) / Math.max(gest.d0, 1) / S.k, mx, my);
        return;
      }
      gest.ruch = Math.max(gest.ruch, Math.hypot(x - gest.x0, y - gest.y0));
      if (gest.ruch < 5) return;
      S.dotkniete = true;
      if (gest.typ === "przesun") {
        S.tx += x - gest.lx; S.ty += y - gest.ly;
        plotno.style.cursor = "grabbing";
      } else if (gest.typ === "wezel") {
        const i = gest.i;
        sim.staly[i] = 1;
        sim.x[i] = (x - S.tx) / S.k;
        sim.y[i] = (y - S.ty) / S.k;
        sim.alfaCel = 0.25;
        sim.obudz(0.25);
      }
      gest.lx = x; gest.ly = y;
      zaplanuj();
    });
    const koniec = (e) => {
      if (!wskazniki.has(e.pointerId)) return;
      wskazniki.delete(e.pointerId);
      if (gest && gest.typ === "wezel") { sim.staly[gest.i] = 0; sim.alfaCel = 0; zaplanuj(); }
      if (gest && e.type === "pointerup" && gest.ruch < 5 && performance.now() - gest.t0 < 600) {
        if (gest.typ === "wezel") otworz(gest.i, false);
        else if (gest.typ === "przesun") zamknijSzuflade();
      }
      if (wskazniki.size === 0) { gest = null; plotno.style.cursor = ""; }
      else if (wskazniki.size === 1) {
        const [p] = [...wskazniki.values()];
        gest = { typ: "przesun", i: -1, x0: p.x, y0: p.y, lx: p.x, ly: p.y, t0: 0, ruch: 99 };
      }
    };
    plotno.addEventListener("pointerup", koniec);
    plotno.addEventListener("pointercancel", koniec);
    plotno.addEventListener("wheel", (e) => {
      e.preventDefault();
      const [x, y] = pozycja(e);
      zoomO(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0018)), x, y);
    }, { passive: false });
    new ResizeObserver(() => rozmiar()).observe(scena);

    // ---------------- wyszukiwarka
    function szukaj(tekst) {
      S.szukaj = tekst;
      const q = norm(tekst).trim();
      if (!q) { S.trafienia = null; trafieniaEl.textContent = ""; zaplanuj(); return; }
      const lista = S.wezly.filter((w) => widoczny(w) && w._szuk.includes(q));
      const ranga = (w) => (norm(w.tytul) === q ? 0 : norm(w.tytul).startsWith(q) ? 1 : 2);
      lista.sort((a, b) => ranga(a) - ranga(b) || (b.stopien || 0) - (a.stopien || 0));
      S.trafienia = new Set(lista.map((w) => w._i));
      S.trafieniaLista = lista;
      trafieniaEl.textContent = lista.length ? `${lista.length} ${lista.length === 1 ? "trafienie" : lista.length < 5 ? "trafienia" : "trafień"}` : "brak";
      zaplanuj();
    }
    poleSzukaj.addEventListener("input", () => szukaj(poleSzukaj.value));
    poleSzukaj.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const p = S.trafieniaLista && S.trafienia && S.trafieniaLista[0];
        if (p) { otworz(p._i, true); poleSzukaj.blur(); }
      } else if (e.key === "Escape") { poleSzukaj.value = ""; szukaj(""); }
    });

    // ---------------- szuflada notatki
    function znajdz(nazwa) {
      const s = String(nazwa || "").replace(/\\/g, "/").trim();
      if (!s) return -1;
      const ls = norm(s), lb = norm(baza(s));
      let i = S.wezly.findIndex((w) => w.sciezka === s);
      if (i < 0) i = S.wezly.findIndex((w) => norm(w.sciezka) === ls || norm(w.sciezka).endsWith("/" + ls) || norm(w.sciezka) === ls + ".md" || norm(w.sciezka).endsWith("/" + ls + ".md"));
      if (i < 0) i = S.wezly.findIndex((w) => norm(baza(w.sciezka)) === lb);
      if (i < 0) i = S.wezly.findIndex((w) => norm(w.tytul) === ls);
      return i;
    }

    function zamknijSzuflade() {
      szuflada.hidden = true;
      szuflada.replaceChildren();
      S.wybrany = -1;
      S.historia = [];
      zaplanuj();
    }

    let nrNotatki = 0;
    async function otworz(i, centruj, sciezkaBezWezla, zHistorii) {
      const w = i >= 0 ? S.wezly[i] : null;
      const sciezka = w ? w.sciezka : sciezkaBezWezla;
      if (!sciezka) return;
      if (!zHistorii && !szuflada.hidden && S.biezaca && S.biezaca !== sciezka) S.historia.push(S.biezaca);
      S.biezaca = sciezka;
      S.wybrany = i;
      if (w && S.ukryteKat.has(w._kat)) { S.ukryteKat.delete(w._kat); rysujPasy(); }
      szuflada.hidden = false;
      const nr = ++nrNotatki;
      const tytul = w ? w.tytul : baza(sciezka);
      const tresc = el("div", { class: "md sn-tresc" }, el("p", { class: "cichy-tekst", text: "Wczytuję notatkę…" }));
      const wstecz = S.historia.length
        ? el("button", { class: "przycisk cichy maly sn-x", "aria-label": "Wstecz", title: "Poprzednia notatka", onclick: () => {
          const p = S.historia.pop();
          const j = znajdz(p);
          otworz(j, true, j < 0 ? p : null, true);
        } }, ikona("wstecz"))
        : null;
      const glowa = el("div", { class: "sn-sz-glowa" }, wstecz,
        el("div", { class: "sn-sz-tytul" }, el("div", { class: "karta-tytul", text: tytul }), el("div", { class: "cichy-tekst sn-sciezka", text: sciezka })),
        el("button", { class: "przycisk cichy maly sn-x", "aria-label": "Zamknij notatkę", onclick: zamknijSzuflade }, ikona("zamknij")));
      const chipy = el("div", { class: "sn-chipy" });
      const miejsceKom = el("div", { class: "sn-sz-kom" });
      const cel = { typ: "notatka", cel: sciezka, etykieta: tytul };
      const btnKom = el("button", { class: "przycisk maly" }, ikona("komentarz"), "Skomentuj");
      btnKom.addEventListener("click", async () => {
        btnKom.disabled = true;
        try { miejsceKom.replaceChildren(await sekcjaKomentarzy(ctx, cel)); }
        catch (e) { miejsceKom.replaceChildren(el("p", { class: "cichy-tekst", text: "Komentarze są chwilowo niedostępne." })); }
      });
      const akcje = el("div", { class: "sn-akcje" }, btnKom,
        ctx.statyczny ? null : el("button", { class: "przycisk maly", onclick: () => ctx.idz("agent", { kontekst: [cel] }) }, ikona("agent"), "Zapytaj agenta"));
      const we = el("div", { class: "sn-we" });
      szuflada.replaceChildren(el("div", { class: "sn-uchwyt" }), glowa, chipy, akcje, miejsceKom, tresc, we);
      szuflada.scrollTop = 0;
      if (w) {
        chipyNotatki(chipy, w, null);
        if (centruj) wysrodkuj(i);
      }
      zaplanuj();
      try {
        const n = await ctx.api("/api/sejf/notatka?sciezka=" + enc(sciezka));
        if (nr !== nrNotatki) return;
        chipyNotatki(chipy, w, n);
        tresc.innerHTML = await renderujMd(n.tresc_md || "");
        if (!String(n.tresc_md || "").trim()) tresc.replaceChildren(el("p", { class: "cichy-tekst", text: "Notatka jest pusta." }));
        const lw = n.linki_we || [];
        we.replaceChildren(el("div", { class: "karta-tytul sn-we-tytul", text: `Linkują tutaj (${lw.length})` }),
          lw.length ? el("div", { class: "sn-we-lista" }, ...lw.map((l) => el("button", { class: "sn-link", onclick: () => {
            const j = znajdz(l.sciezka);
            otworz(j, true, j < 0 ? l.sciezka : null);
          } }, l.tytul || baza(l.sciezka)))) : el("p", { class: "cichy-tekst", text: "Żadna notatka nie linkuje do tej." }));
      } catch (e) {
        if (nr !== nrNotatki) return;
        tresc.replaceChildren(el("p", { class: "cichy-tekst", text: "Nie udało się wczytać treści: " + (e.message || "błąd") }));
      }
    }

    function chipyNotatki(chipy, w, n) {
      const fm = (n && n.frontmatter) || {};
      const status = (w && w.status) || fm.status;
      const tagi = (w && w.tagi && w.tagi.length ? w.tagi : null) || [].concat(fm.tags || fm.tagi || []);
      const zm = (n && n.zmieniono) || (w && w.zmieniono);
      const kolorStatusu = /zatw|gotow|zrobion|done/i.test(status || "") ? "zielen" : /odrzu|porzuc|blok/i.test(status || "") ? "czerwien" : /trakc|robo|szkic|draft/i.test(status || "") ? "zloto" : "fiolet";
      chipy.replaceChildren(...[
        status ? el("span", { class: "chip " + kolorStatusu, text: String(status) }) : null,
        w ? el("span", { class: "chip" }, el("span", { class: "sn-kropka", style: `background:${kolorKategorii(w)}` }),
          (S.kategorie.find((k) => k.id === w._kat) || {}).nazwa || w.kategoria) : null,
        ...tagi.slice(0, 8).map((t) => el("span", { class: "chip niebieski", text: "#" + String(t).replace(/^#/, "") })),
        zm ? el("span", { class: "cichy-tekst sn-zm", text: "zmieniono " + czasTemu(zm) }) : null].filter(Boolean));
    }

    szuflada.addEventListener("click", (e) => {
      const a = e.target.closest("[data-wikilink]");
      if (!a) return;
      e.preventDefault();
      const nazwa = a.getAttribute("data-wikilink");
      const j = znajdz(nazwa);
      if (j >= 0) otworz(j, true);
      else ctx.toast?.("Nie ma notatki „" + nazwa + "” w sejfie.", "blad");
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && S.widoczny && !szuflada.hidden && document.activeElement !== poleSzukaj) zamknijSzuflade();
    });

    function zastosujOczekujaca() {
      const o = S.oczekujaca;
      if (!o || !S.wezly.length) return;
      S.oczekujaca = null;
      const i = znajdz(o);
      if (i >= 0) otworz(i, true);
      else if (/\.md$/i.test(o) || o.includes("/")) otworz(-1, false, o);
      else ctx.toast?.("Nie znalazłem notatki „" + o + "”.", "blad");
    }

    function pokazKomunikat(tekst, przycisk) {
      komunikat.replaceChildren(el("div", { text: tekst }), przycisk || "");
      komunikat.hidden = false;
    }
    function ukryjKomunikat() { komunikat.hidden = true; }

    return {
      el: root,
      async pokaz(parametry) {
        S.widoczny = true;
        if (parametry && parametry.notatka) S.oczekujaca = String(parametry.notatka);
        rozmiar();
        if (!S.dane) await wczytaj();
        else {
          if (Date.now() - S.wczytano > 60000) wczytaj(true);
          zastosujOczekujaca();
          zaplanuj();
        }
      },
      ukryj() {
        S.widoczny = false;
        if (S.raf) cancelAnimationFrame(S.raf);
        if (S.timer) clearTimeout(S.timer);
        S.raf = 0;
        S.timer = 0;
      },
    };
  },
};
