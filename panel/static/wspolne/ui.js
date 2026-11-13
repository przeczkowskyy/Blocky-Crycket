// Wspólne klocki interfejsu: el(), ikony SVG, czas po polsku, toast, arkusz (dolny arkusz / okno), powiększenie zdjęć.

// --------------------------------------------------------------------------- el()
const WLASCIWOSCI = new Set(["value", "checked", "disabled", "hidden", "selected", "indeterminate", "readOnly", "multiple"]);

/**
 * el("div", {class: "karta", onclick: fn, dataset: {id: 1}, style: {...}}, "tekst", innyElement, [lista], null)
 * Atrybuty: class/klasa, style (tekst albo obiekt), on<zdarzenie> (funkcja), dataset, html (zaufany HTML!), tekst,
 * wartości logiczne (true = pusty atrybut, false/null = pomiń), reszta przez setAttribute.
 */
export function el(znacznik, atrybuty, ...dzieci) {
  const w = document.createElement(znacznik);
  if (atrybuty && (typeof atrybuty !== "object" || atrybuty instanceof Node || Array.isArray(atrybuty))) {
    dzieci.unshift(atrybuty);
    atrybuty = null;
  }
  if (atrybuty) {
    for (const k of Object.keys(atrybuty)) {
      const v = atrybuty[k];
      if (v === undefined || v === null || v === false) continue;
      if (k === "class" || k === "klasa") w.className = Array.isArray(v) ? v.filter(Boolean).join(" ") : v;
      else if (k === "style") {
        if (typeof v === "string") w.style.cssText = v;
        else for (const s of Object.keys(v)) {
          if (s.startsWith("--")) w.style.setProperty(s, v[s]);
          else w.style[s] = v[s];
        }
      } else if (k === "dataset") Object.assign(w.dataset, v);
      else if (k === "html") w.innerHTML = v;
      else if (k === "tekst") w.textContent = v;
      else if (k.startsWith("on") && typeof v === "function") w.addEventListener(k.slice(2).toLowerCase(), v);
      else if (WLASCIWOSCI.has(k)) w[k] = v;
      else if (v === true) w.setAttribute(k, "");
      else w.setAttribute(k, String(v));
    }
  }
  dodaj(w, dzieci);
  return w;
}

/** Dopisuje dzieci jak el() (pomija null/false, spłaszcza tablice). Uwaga: natywne append() wypisałoby "null". */
export function dopisz(rodzic, ...dzieci) {
  dodaj(rodzic, dzieci);
  return rodzic;
}

/** Podmienia zawartość elementu (null/false pomijane). */
export function zamien(rodzic, ...dzieci) {
  rodzic.replaceChildren();
  dodaj(rodzic, dzieci);
  return rodzic;
}

function dodaj(rodzic, dzieci) {
  for (const d of dzieci) {
    if (d === null || d === undefined || d === false || d === true) continue;
    if (Array.isArray(d)) dodaj(rodzic, d);
    else if (d instanceof Node) rodzic.appendChild(d);
    else rodzic.appendChild(document.createTextNode(String(d)));
  }
}

// --------------------------------------------------------------------------- ikony (24×24, obrys currentColor)
const IKONY = {
  pulpit: '<rect x="3" y="3" width="7.5" height="9" rx="1.8"/><rect x="13.5" y="3" width="7.5" height="5.5" rx="1.8"/><rect x="13.5" y="11.5" width="7.5" height="9.5" rx="1.8"/><rect x="3" y="15" width="7.5" height="6" rx="1.8"/>',
  plan: '<path d="M10 6.5h10M10 12h10M10 17.5h10"/><path d="M3.5 6.5l1.5 1.5 2.5-3M3.5 12l1.5 1.5 2.5-3"/><circle cx="5.3" cy="17.5" r="1.4"/>',
  raporty: '<path d="M9 3h6a1 1 0 0 1 1 1v1.5H8V4a1 1 0 0 1 1-1z"/><path d="M8 5H6.2A1.2 1.2 0 0 0 5 6.2v13.6A1.2 1.2 0 0 0 6.2 21h11.6a1.2 1.2 0 0 0 1.2-1.2V6.2A1.2 1.2 0 0 0 17.8 5H16"/><path d="M8.8 13.2l2.2 2.2 4.2-4.6"/>',
  podglad: '<path d="M12 2.8l8 4.6v9.2l-8 4.6-8-4.6V7.4z"/><path d="M4 7.4l8 4.6 8-4.6M12 12v9.2"/>',
  agent: '<path d="M11 3.5l1.9 5 5 1.9-5 1.9-1.9 5-1.9-5-5-1.9 5-1.9z"/><path d="M18.5 14.5l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9z"/>',
  siec: '<circle cx="6" cy="6.5" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><circle cx="19" cy="15.5" r="1.6"/><path d="M8.5 6.4l7-.3M7.2 8.7l3.7 7.1M16.9 8.3l-3.7 7.4M14.4 17.3l3.2-1.2"/>',
  analityka: '<path d="M3.5 20.5h17"/><rect x="5" y="11" width="3.2" height="7" rx="1"/><rect x="10.4" y="5.5" width="3.2" height="12.5" rx="1"/><rect x="15.8" y="13" width="3.2" height="5" rx="1"/>',
  ustawienia: '<path d="M4 6.5h9M17 6.5h3M4 12h3M11 12h9M4 17.5h11M19 17.5h1"/><circle cx="15" cy="6.5" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="17.5" r="2"/>',
  wiecej: '<circle cx="5" cy="12" r="1.7" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.7" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1.7" fill="currentColor" stroke="none"/>',
  mikrofon: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>',
  stop: '<rect x="6.5" y="6.5" width="11" height="11" rx="2" fill="currentColor"/>',
  wyslij: '<path d="M20.5 3.5L10 14"/><path d="M20.5 3.5l-6.5 17-4-6.5-6.5-4z"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  zamknij: '<path d="M6 6l12 12M18 6L6 18"/>',
  strzalka: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  wstecz: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  prawo: '<path d="M9 6l6 6-6 6"/>',
  lewo: '<path d="M15 6l-6 6 6 6"/>',
  dol: '<path d="M6 9l6 6 6-6"/>',
  kopiuj: '<rect x="8.5" y="8.5" width="12" height="12" rx="2"/><path d="M15.5 8.5V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v7.5a2 2 0 0 0 2 2h2.5"/>',
  odswiez: '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3.5V8h4.5"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20.5V16h-4.5"/>',
  pobierz: '<path d="M12 3.5v12M7 10.5l5 5 5-5M4.5 20.5h15"/>',
  wypchnij: '<path d="M12 20.5v-12M7 13.5l5-5 5 5M4.5 3.5h15"/>',
  komentarz: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-5 4v-4h0.5A1.5 1.5 0 0 1 4 14.5z"/>',
  ok: '<path d="M4.5 12.5l5 5L19.5 7"/>',
  krzyzyk: '<path d="M6 6l12 12M18 6L6 18"/>',
  ostrzezenie: '<path d="M12 3.5L2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.1"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.6v.1"/>',
  notatka: '<path d="M6 3h8.5L19 7.5V21H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
  studio: '<rect x="3.5" y="9" width="17" height="11" rx="1.5"/><path d="M7 9V6h4v3M13 9V6h4v3"/>',
  obraz: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.8"/><path d="M21 16l-5-5-9 8"/>',
  assety: '<rect x="3" y="7.5" width="14" height="12.5" rx="2"/><path d="M7.5 4H19a2 2 0 0 1 2 2v10"/><circle cx="7.8" cy="12" r="1.5"/><path d="M17 16.5l-3.8-3.8L6.5 20"/>',
  uzytkownik: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
  zegar: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
  narzedzie: '<path d="M14.7 6.3a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3z"/><path d="M14.7 6.3L17 4l3 3-2.3 2.3"/>',
  telefon: '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18h2"/>',
  zdrowie: '<path d="M3 12h4l2.5-6.5 5 13 2.5-6.5h4"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h10"/>',
  git: '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="7" r="2"/><path d="M6 7v10M18 9c0 5-7 3-11 8.5"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  oko: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  flaga: '<path d="M5 21V4M5 4h12l-2.5 4.5L17 13H5"/>',
  dziennik: '<path d="M4 4.5h5.5A2.5 2.5 0 0 1 12 7v13.5A2 2 0 0 0 10 18.5H4zM20 4.5h-5.5A2.5 2.5 0 0 0 12 7v13.5a2 2 0 0 1 2-2h6z"/>',
  pytanie: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.6 2.2c-.7.4-1.1 1-1.1 1.8v.5M12 17.2v.1"/>',
  decyzja: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
  kalendarz: '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
  ogien: '<path d="M12 3c1 3.5 5.5 5.5 5.5 10.5a5.5 5.5 0 0 1-11 0c0-2.7 1.5-4.3 2.6-5.3.3 2 1.3 3.2 2.6 3.3-1-3.2-.2-6.2.3-8.5z"/>',
  lupa: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  glos: '<path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2"/>',
  migawka: '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
  zarowka: '<path d="M9 18h6M10 21h4M8.5 14.5a6 6 0 1 1 7 0c-.8.6-1.5 1.5-1.5 2.5h-4c0-1-.7-1.9-1.5-2.5z"/>',
  kosz: '<path d="M4 7h16M10 7V4.5h4V7M6.5 7l1 13h9l1-13"/>',
  powieksz: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
  zewnetrzny: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  klodka: '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
  zespol: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c1-3.5 3.5-5.5 6.5-5.5s5.5 2 6.5 5.5"/><circle cx="17" cy="9" r="2.6"/><path d="M16.5 14.3c2.5 0 4.3 1.6 5 4.4"/>',
  rakieta: '<path d="M14 4c3-1 6-1 6-1s0 3-1 6l-6 6-4-4z"/><path d="M10 11l-4 .5L4 14l4 1M13 14l-.5 4L10 20l-1-4"/><circle cx="15.5" cy="8.5" r="1.3"/>',
};

const ALIASY = { home: "pulpit", raport: "raporty", "3d": "podglad", kostka: "podglad", graf: "siec", wykres: "analityka", ustaw: "ustawienia" };

/** Czy istnieje ikona o tej nazwie. */
export function maIkone(nazwa) {
  return !!(IKONY[nazwa] || IKONY[ALIASY[nazwa]]);
}

/** ikona("raporty") → <svg>. Nieznana nazwa = kółko. */
export function ikona(nazwa, opcje = {}) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", String(opcje.grubosc || 2));
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.setAttribute("class", "ikona" + (opcje.klasa ? " " + opcje.klasa : ""));
  if (opcje.rozmiar) {
    svg.setAttribute("width", String(opcje.rozmiar));
    svg.setAttribute("height", String(opcje.rozmiar));
  }
  svg.innerHTML = IKONY[nazwa] || IKONY[ALIASY[nazwa]] || '<circle cx="12" cy="12" r="8"/>';
  return svg;
}

// --------------------------------------------------------------------------- czas
const MIESIACE = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"];
const pad = (n) => String(n).padStart(2, "0");

function naDate(iso) {
  if (!iso) return null;
  if (iso instanceof Date) return iso;
  if (typeof iso === "number") return new Date(iso < 1e12 ? iso * 1000 : iso);
  const s = String(iso);
  const tylkoData = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (tylkoData) return new Date(+tylkoData[1], +tylkoData[2] - 1, +tylkoData[3]);
  const d = new Date(s);
  return isNaN(d.getTime()) ? null : d;
}

/** dataKrotka("2026-11-12T21:40:05+01:00") → "12 lis, 21:40" (rok, gdy inny niż bieżący). */
export function dataKrotka(iso) {
  const d = naDate(iso);
  if (!d) return iso ? String(iso) : "";
  const rok = d.getFullYear() !== new Date().getFullYear() ? " " + d.getFullYear() : "";
  const bezGodziny = typeof iso === "string" && /^\d{4}-\d{2}-\d{2}$/.test(iso);
  return d.getDate() + " " + MIESIACE[d.getMonth()] + rok + (bezGodziny ? "" : ", " + d.getHours() + ":" + pad(d.getMinutes()));
}

/** czasTemu(iso) → "przed chwilą", "5 min temu", "3 godz. temu", "wczoraj, 21:40", "4 dni temu", "12 lis". */
export function czasTemu(iso) {
  const d = naDate(iso);
  if (!d) return iso ? String(iso) : "";
  const s = (Date.now() - d.getTime()) / 1000;
  if (s < -90) return dataKrotka(iso);
  if (s < 45) return "przed chwilą";
  if (s < 90) return "minutę temu";
  if (s < 3600) return Math.round(s / 60) + " min temu";
  if (s < 6 * 3600) return Math.floor(s / 3600) + " godz. temu";
  const dzis = new Date();
  dzis.setHours(0, 0, 0, 0);
  const godz = d.getHours() + ":" + pad(d.getMinutes());
  if (d >= dzis) return "dziś, " + godz;
  const wczoraj = new Date(dzis.getTime() - 86400000);
  if (d >= wczoraj) return "wczoraj, " + godz;
  const dni = Math.round((dzis - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 86400000);
  if (dni < 7) return dni + " dni temu";
  return dataKrotka(iso);
}

/** Czas trwania w sekundach → "42 s", "3 min 5 s". */
export function czasTrwania(s) {
  s = Math.max(0, Math.round(Number(s) || 0));
  if (s < 60) return s + " s";
  const m = Math.floor(s / 60);
  if (m < 60) return m + " min" + (s % 60 ? " " + (s % 60) + " s" : "");
  return Math.floor(m / 60) + " godz. " + (m % 60) + " min";
}

// --------------------------------------------------------------------------- liczebniki
/** odmiana(5, ["raport", "raporty", "raportów"]) → "raportów". */
export function odmiana(n, formy) {
  n = Math.abs(n);
  if (n === 1) return formy[0];
  const j = n % 10;
  const d = n % 100;
  if (j >= 2 && j <= 4 && (d < 12 || d > 14)) return formy[1];
  return formy[2];
}

// --------------------------------------------------------------------------- toast
let kontenerToastow = null;

/** toast(tekst, typ?) — typ: "ok" | "blad" | "info" (domyślnie). */
export function toast(tekst, typ = "info") {
  if (!kontenerToastow || !kontenerToastow.isConnected) {
    kontenerToastow = el("div", { class: "toasty", role: "status", "aria-live": "polite" });
    document.body.appendChild(kontenerToastow);
  }
  const nazwaIkony = typ === "ok" ? "ok" : typ === "blad" ? "ostrzezenie" : "info";
  const t = el("div", { class: "toast toast-" + typ }, ikona(nazwaIkony), el("span", null, String(tekst)));
  const zamknij = () => {
    if (!t.isConnected) return;
    t.classList.add("znika");
    setTimeout(() => t.remove(), 220);
  };
  t.addEventListener("click", zamknij);
  kontenerToastow.appendChild(t);
  while (kontenerToastow.children.length > 3) kontenerToastow.firstChild.remove();
  setTimeout(zamknij, typ === "blad" ? 6500 : 3500);
  return t;
}

// --------------------------------------------------------------------------- arkusz
let otwarteArkusze = 0;

/**
 * arkusz({tytul, tresc, naZamkniecie?, szeroki?}) → {el, zamknij()}.
 * Na telefonie dolny arkusz, na komputerze okno na środku. Esc i klik w tło zamykają.
 */
export function arkusz({ tytul, tresc, naZamkniecie, szeroki } = {}) {
  const poprzedniFokus = document.activeElement;
  const przyciskZamknij = el("button", { class: "przycisk cichy ikonowy", type: "button", "aria-label": "Zamknij" }, ikona("zamknij"));
  const cialo = el("div", { class: "arkusz-tresc" }, tresc);
  const panel = el("div", { class: "arkusz" + (szeroki ? " szeroki" : ""), role: "dialog", "aria-modal": "true", "aria-label": tytul || "Okno", tabindex: "-1" },
    el("div", { class: "arkusz-uchwyt", "aria-hidden": "true" }),
    el("header", { class: "arkusz-nagl" }, el("h2", null, tytul || ""), przyciskZamknij),
    cialo);
  const tlo = el("div", { class: "arkusz-tlo" }, panel);
  let zamkniety = false;
  const naKlawisz = (e) => {
    if (e.key === "Escape") {
      e.stopPropagation();
      zamknij();
    }
  };
  function zamknij() {
    if (zamkniety) return;
    zamkniety = true;
    document.removeEventListener("keydown", naKlawisz, true);
    tlo.classList.add("zamykanie");
    otwarteArkusze = Math.max(0, otwarteArkusze - 1);
    if (!otwarteArkusze) document.documentElement.classList.remove("bez-przewijania");
    setTimeout(() => tlo.remove(), bezRuchu() ? 0 : 200);
    if (poprzedniFokus && poprzedniFokus.focus && poprzedniFokus.isConnected) {
      try {
        poprzedniFokus.focus({ preventScroll: true });
      } catch (e) { /* nic */ }
    }
    if (typeof naZamkniecie === "function") naZamkniecie();
  }
  przyciskZamknij.addEventListener("click", zamknij);
  tlo.addEventListener("mousedown", (e) => {
    if (e.target === tlo) zamknij();
  });
  document.addEventListener("keydown", naKlawisz, true);
  document.body.appendChild(tlo);
  otwarteArkusze++;
  document.documentElement.classList.add("bez-przewijania");
  requestAnimationFrame(() => {
    const pierwszy = cialo.querySelector("textarea, input:not([type=hidden]):not([type=file]), select");
    if (pierwszy && window.matchMedia("(pointer: fine)").matches) pierwszy.focus();
    else panel.focus({ preventScroll: true });
  });
  return { el: panel, zamknij, cialo };
}

// --------------------------------------------------------------------------- powiększenie zdjęć
/** powiekszenie([{src, podpis?}], indeks) — zdjęcia na cały ekran: strzałki, przesuwanie palcem, Esc. */
export function powiekszenie(obrazy, start = 0) {
  if (!obrazy || !obrazy.length) return;
  let i = Math.min(Math.max(0, start), obrazy.length - 1);
  const img = el("img", { class: "lb-obraz", alt: "" });
  const podpis = el("div", { class: "lb-podpis" });
  const licznikEl = el("div", { class: "lb-licznik" });
  const poprz = el("button", { class: "lb-strzalka lewo", type: "button", "aria-label": "Poprzednie" }, ikona("lewo"));
  const nast = el("button", { class: "lb-strzalka prawo", type: "button", "aria-label": "Następne" }, ikona("prawo"));
  const zamk = el("button", { class: "lb-zamknij", type: "button", "aria-label": "Zamknij" }, ikona("zamknij"));
  const scena = el("div", { class: "lb-scena" }, img);
  const lb = el("div", { class: "lightbox", role: "dialog", "aria-modal": "true", "aria-label": "Powiększenie" },
    scena, zamk, poprz, nast, el("div", { class: "lb-dol" }, licznikEl, podpis));
  function pokaz() {
    const o = obrazy[i];
    img.src = o.src;
    img.alt = o.podpis || "zrzut ekranu";
    podpis.textContent = o.podpis || "";
    licznikEl.textContent = obrazy.length > 1 ? (i + 1) + " / " + obrazy.length : "";
    poprz.hidden = nast.hidden = obrazy.length < 2;
  }
  const krok = (d) => {
    i = (i + d + obrazy.length) % obrazy.length;
    pokaz();
  };
  const naKlawisz = (e) => {
    if (e.key === "Escape") zamknij();
    else if (e.key === "ArrowLeft") krok(-1);
    else if (e.key === "ArrowRight") krok(1);
    else return;
    e.preventDefault();
    e.stopPropagation();
  };
  function zamknij() {
    document.removeEventListener("keydown", naKlawisz, true);
    document.documentElement.classList.remove("bez-przewijania-lb");
    lb.remove();
  }
  poprz.addEventListener("click", (e) => { e.stopPropagation(); krok(-1); });
  nast.addEventListener("click", (e) => { e.stopPropagation(); krok(1); });
  zamk.addEventListener("click", zamknij);
  scena.addEventListener("click", (e) => { if (e.target === scena) zamknij(); });
  // przesuwanie palcem
  let x0 = null;
  let y0 = 0;
  scena.addEventListener("pointerdown", (e) => { x0 = e.clientX; y0 = e.clientY; });
  scena.addEventListener("pointermove", (e) => {
    if (x0 === null) return;
    img.style.transform = "translateX(" + (e.clientX - x0) + "px)";
  });
  const puszczenie = (e) => {
    if (x0 === null) return;
    const dx = e.clientX - x0;
    const dy = e.clientY - y0;
    x0 = null;
    img.style.transform = "";
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) krok(dx < 0 ? 1 : -1);
    else if (dy > 120 && Math.abs(dy) > Math.abs(dx)) zamknij();
  };
  scena.addEventListener("pointerup", puszczenie);
  scena.addEventListener("pointercancel", () => { x0 = null; img.style.transform = ""; });
  document.addEventListener("keydown", naKlawisz, true);
  document.documentElement.classList.add("bez-przewijania-lb");
  document.body.appendChild(lb);
  pokaz();
  zamk.focus({ preventScroll: true });
  return { zamknij };
}

// --------------------------------------------------------------------------- drobne klocki
/** Stan pusty z podpowiedzią. */
export function pusty(tytul, podpowiedz, nazwaIkony) {
  return el("div", { class: "pusty" },
    nazwaIkony ? el("div", { class: "pusty-ikona" }, ikona(nazwaIkony)) : null,
    el("strong", null, tytul),
    podpowiedz ? (podpowiedz instanceof Node ? podpowiedz : el("p", null, podpowiedz)) : null);
}

/** Stan pusty dla błędu z api() — po ludzku. */
export function stanBledu(e, coTo) {
  const status = e && e.status;
  if (status === 404 && !(e.dane && e.dane.blad && !/trasy/i.test(e.dane.blad))) {
    return pusty((coTo || "Ta część") + " — jeszcze niedostępne", "Ta część serwera panelu nie jest jeszcze gotowa albo nie wstała. Sprawdź Ustawienia → Stan systemu.", "info");
  }
  if (status === 0) return pusty("Brak połączenia z panelem", "Serwer panelu nie odpowiada. Sprawdź, czy działa na komputerze.", "ostrzezenie");
  if (e && e.dane && e.dane.statyczny) return pusty("Podgląd tylko do odczytu", e.message, "oko");
  return pusty((coTo ? coTo + ": " : "") + "coś poszło nie tak", (e && e.message) || "Nieznany błąd.", "ostrzezenie");
}

/** Wskaźnik ładowania (szkielet). */
export function ladowanie(tekst = "Ładuję…") {
  return el("div", { class: "ladowanie", role: "status" }, el("span", { class: "kreciolek", "aria-hidden": "true" }), el("span", null, tekst));
}

const KOLORY_AWATAROW = ["#f5b82e", "#8b5cf6", "#3ecf8e", "#4ea8ff", "#ef5a5a", "#ff8a3d", "#2ec4c4", "#e66bd1"];

/** Kolor przypisany do imienia (stały). */
export function kolorOsoby(imie) {
  let h = 0;
  const s = String(imie || "?").toLowerCase();
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return KOLORY_AWATAROW[h % KOLORY_AWATAROW.length];
}

/** Awatar z inicjałem. */
export function awatar(imie, opcje = {}) {
  const tekst = String(imie || "?").trim();
  const slowa = tekst.replace(/[()]/g, " ").split(/\s+/).filter(Boolean);
  const inicjaly = (slowa[0] ? slowa[0][0] : "?") + (slowa.length > 1 && /^[A-ZŁŚŻŹĆŃÓĘĄ]/.test(slowa[1]) ? slowa[1][0] : "");
  return el("span", {
    class: "awatar" + (opcje.maly ? " maly" : ""), title: tekst,
    style: { "--kolor-osoby": kolorOsoby(tekst) }, "aria-hidden": opcje.ozdobny ? "true" : null,
  }, inicjaly.toUpperCase());
}

/** Kopiowanie do schowka z zapasowym sposobem dla stron po http. */
export async function kopiuj(tekst) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(tekst);
      return true;
    }
  } catch (e) { /* zapas niżej */ }
  const t = el("textarea", { style: "position:fixed;left:-9999px;top:0;opacity:0", readonly: true }, tekst);
  document.body.appendChild(t);
  t.select();
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch (e) {
    ok = false;
  }
  t.remove();
  return ok;
}

/** Przełącznik segmentowy: opcje [{id, tekst, licznik?}] → element z .ustaw(id). */
export function przelacznik(opcje, wybrana, naZmiane, etykieta) {
  const w = el("div", { class: "przelacznik", role: "tablist", "aria-label": etykieta || "Wybór" });
  const przyciski = new Map();
  for (const o of opcje) {
    const b = el("button", { type: "button", role: "tab", class: "przelacznik-opcja", dataset: { id: o.id } },
      o.ikona ? ikona(o.ikona) : null, el("span", null, o.tekst),
      o.licznik !== undefined && o.licznik !== null ? el("span", { class: "przelacznik-licznik" }, String(o.licznik)) : null);
    b.addEventListener("click", () => {
      ustaw(o.id);
      try {
        b.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
      } catch (e) { /* stare przeglądarki */ }
      naZmiane(o.id);
    });
    przyciski.set(o.id, b);
    w.appendChild(b);
  }
  function ustaw(id) {
    for (const [k, b] of przyciski) {
      b.classList.toggle("aktywny", k === id);
      b.setAttribute("aria-selected", k === id ? "true" : "false");
    }
  }
  ustaw(wybrana);
  w.ustaw = ustaw;
  w.licznik = (id, n) => {
    const b = przyciski.get(id);
    if (!b) return;
    let l = b.querySelector(".przelacznik-licznik");
    if (n === null || n === undefined) { if (l) l.remove(); return; }
    if (!l) { l = el("span", { class: "przelacznik-licznik" }); b.appendChild(l); }
    l.textContent = String(n);
  };
  return w;
}

/** Karta z tytułem: zwraca {el, cialo, akcje}. */
export function karta(tytul, nazwaIkony, opcje = {}) {
  const akcje = el("div", { class: "karta-akcje" });
  const cialo = el("div", { class: "karta-cialo" });
  const w = el("section", { class: "karta" + (opcje.klasa ? " " + opcje.klasa : "") },
    el("h2", { class: "karta-tytul" }, nazwaIkony ? ikona(nazwaIkony) : null, el("span", null, tytul), akcje),
    cialo);
  return { el: w, cialo, akcje };
}

/** Czy użytkownik prosi o ograniczenie animacji. */
export function bezRuchu() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Skraca tekst do n znaków. */
export function skroc(t, n) {
  t = String(t || "");
  return t.length > n ? t.slice(0, n - 1).trimEnd() + "…" : t;
}
