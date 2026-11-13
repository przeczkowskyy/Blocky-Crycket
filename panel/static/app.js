// Powłoka panelu: nawigacja (#/<id>), ładowanie widoków, odznaki, puls obecności, imię osoby, tryb statyczny.

import { api, apiSurowe, sse, STATYCZNY, plik } from "./wspolne/api.js";
import { el, ikona, maIkone, toast, arkusz, awatar } from "./wspolne/ui.js";

// Kolejność i opisy na wypadek, gdyby moduł widoku nie wstał (wtedy pokazujemy komunikat zamiast niego).
const WIDOKI = [
  { id: "pulpit", tytul: "Pulpit", ikona: "pulpit", kolejnosc: 10 },
  { id: "plan", tytul: "Plan", ikona: "plan", kolejnosc: 20 },
  { id: "raporty", tytul: "Raporty", ikona: "raporty", kolejnosc: 30 },
  { id: "podglad", tytul: "Podgląd", ikona: "podglad", kolejnosc: 40 },
  { id: "agent", tytul: "Agent", ikona: "agent", kolejnosc: 50 },
  { id: "siec", tytul: "Sieć", ikona: "siec", kolejnosc: 60 },
  { id: "assety", tytul: "Assety", ikona: "assety", kolejnosc: 65 },
  { id: "analityka", tytul: "Analityka", ikona: "analityka", kolejnosc: 70 },
  { id: "ustawienia", tytul: "Ustawienia", ikona: "ustawienia", kolejnosc: 80 },
];
const NA_DOLE = ["pulpit", "raporty", "podglad", "agent"];
const PARAMETRY_W_ADRESIE = ["raport", "notatka", "migawka", "grupa", "zakladka", "watek"];

const stan = {
  widoki: new Map(),          // id -> {meta, def, inst, kontener, blad}
  aktywny: null,
  oczekujace: null,
  liczniki: {},
  moduly: null,
};

function czytajLS(k) {
  try {
    return localStorage.getItem(k);
  } catch (e) {
    return null;
  }
}
function zapiszLS(k, v) {
  try {
    if (v === null || v === undefined) localStorage.removeItem(k);
    else localStorage.setItem(k, v);
  } catch (e) { /* tryb prywatny */ }
}

function idKlienta() {
  try {
    let k = sessionStorage.getItem("bc.klient");
    if (!k) {
      const los = new Uint8Array(8);
      crypto.getRandomValues(los);
      k = Array.from(los, (b) => b.toString(16).padStart(2, "0")).join("");
      sessionStorage.setItem("bc.klient", k);
    }
    return k;
  } catch (e) {
    return "k" + Math.random().toString(16).slice(2, 14);
  }
}

// --------------------------------------------------------------------------- odpytywanie tylko przy widocznej karcie
function odpytuj(fn, ms) {
  const tik = () => {
    if (document.visibilityState !== "visible") return;
    try {
      Promise.resolve(fn()).catch(() => {});
    } catch (e) { /* nic */ }
  };
  const t = setInterval(tik, ms);
  const naWidocznosc = () => {
    if (document.visibilityState === "visible") tik();
  };
  document.addEventListener("visibilitychange", naWidocznosc);
  return () => {
    clearInterval(t);
    document.removeEventListener("visibilitychange", naWidocznosc);
  };
}

// --------------------------------------------------------------------------- kontekst dla widoków
const ctx = {
  api,
  apiSurowe,
  sse,
  plik,
  statyczny: STATYCZNY,
  ja: { kto: czytajLS("bc.kto") || "", lokalny: false, gospodarz: null, wersja: "" },
  konfiguracja: { gra: { nazwa: "BLOCKY & CRYCKET" }, sejfy: [], agent: {}, glos: {} },
  idz,
  toast,
  licznik,
  odpytuj,
  /** Czy moduł serwera działa (true, gdy jeszcze nie wiadomo). */
  jest: (nazwa) => !stan.moduly || !stan.moduly[nazwa] || stan.moduly[nazwa].ok !== false,
  nazwaWidoku: (id) => (stan.widoki.get(id) ? stan.widoki.get(id).meta.tytul : id),
  ustawKto,
  get aktywnyWidok() {
    return stan.aktywny;
  },
};

// --------------------------------------------------------------------------- szkielet strony
const elementy = {};

function zbudujPowloke() {
  const navBok = el("nav", { class: "nav-bok", "aria-label": "Widoki" });
  const navDol = el("nav", { class: "nav-dol", "aria-label": "Widoki" });
  for (const w of stan.widoki.values()) {
    const { meta } = w;
    const ik = maIkone(meta.ikona) ? meta.ikona : meta.id;
    w.linkBok = el("a", { class: "nav-link", href: "#/" + meta.id, dataset: { widok: meta.id } },
      el("span", { class: "nav-ikona" }, ikona(ik), el("span", { class: "odznaka", dataset: { odznaka: meta.id }, hidden: true })),
      el("span", { class: "nav-tekst" }, meta.tytul));
    navBok.appendChild(w.linkBok);
    if (NA_DOLE.includes(meta.id)) {
      w.linkDol = el("a", { class: "nav-link", href: "#/" + meta.id, dataset: { widok: meta.id } },
        el("span", { class: "nav-ikona" }, ikona(ik), el("span", { class: "odznaka", dataset: { odznaka: meta.id }, hidden: true })),
        el("span", { class: "nav-tekst" }, meta.tytul));
      navDol.appendChild(w.linkDol);
    }
  }
  elementy.wiecej = el("button", { class: "nav-link", type: "button", "aria-haspopup": "dialog" },
    el("span", { class: "nav-ikona" }, ikona("wiecej"), el("span", { class: "odznaka", dataset: { odznaka: "_wiecej" }, hidden: true })),
    el("span", { class: "nav-tekst" }, "Więcej"));
  elementy.wiecej.addEventListener("click", otworzWiecej);
  navDol.appendChild(elementy.wiecej);

  for (const n of [navBok, navDol]) {
    n.addEventListener("click", (e) => {
      const a = e.target.closest("a.nav-link");
      if (a && a.dataset.widok === stan.aktywny) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }

  elementy.ktoBok = el("a", { class: "bok-osoba", href: "#/ustawienia", title: "Ustawienia — kim jesteś" });
  elementy.ktoGora = el("a", { class: "gora-osoba", href: "#/ustawienia", "aria-label": "Ustawienia — kim jesteś" });
  elementy.tytulGora = el("span", { class: "gora-widok" });
  elementy.nazwaGry = el("span", { class: "marka-nazwa" }, ctx.konfiguracja.gra.nazwa || "BLOCKY & CRYCKET");

  const marka = () => el("a", { class: "marka", href: "#/pulpit", "aria-label": "Pulpit" },
    el("span", { class: "logo-znak", "aria-hidden": "true" }, "B&C"));

  const bok = el("aside", { class: "bok" },
    el("div", { class: "bok-marka" }, marka(), el("div", { class: "bok-marka-tekst" }, elementy.nazwaGry, el("span", { class: "marka-pod" }, "Panel zespołu"))),
    navBok,
    el("div", { class: "bok-stopka" }, elementy.ktoBok));

  const gora = el("header", { class: "gora" }, marka(), el("div", { class: "gora-tytuly" },
    el("span", { class: "gora-gra" }, ctx.konfiguracja.gra.nazwa || "BLOCKY & CRYCKET"), elementy.tytulGora), elementy.ktoGora);

  elementy.tresc = el("main", { class: "tresc", id: "tresc", tabindex: "-1" });
  const korzen = el("div", { class: "powloka" + (STATYCZNY ? " statyczna" : "") },
    STATYCZNY ? el("div", { class: "pasek-ro", role: "note" }, ikona("oko"),
      el("span", null, el("strong", null, "Podgląd tylko do odczytu"), " — dane z ostatniego eksportu. Zmiany robi się w panelu na komputerze.")) : null,
    gora, bok, elementy.tresc, navDol);

  for (const w of stan.widoki.values()) {
    w.kontener = el("section", { class: "widok-kontener", dataset: { widok: w.meta.id }, hidden: true, "aria-label": w.meta.tytul });
    elementy.tresc.appendChild(w.kontener);
  }
  const app = document.getElementById("aplikacja");
  app.replaceChildren(korzen);
  odswiezOsobe();
}

function odswiezOsobe() {
  const kto = ctx.ja.kto || "gość";
  if (elementy.ktoBok) {
    elementy.ktoBok.replaceChildren(awatar(kto), el("span", { class: "bok-osoba-tekst" },
      el("strong", null, kto), el("span", null, STATYCZNY ? "podgląd" : ctx.ja.lokalny ? "na tym komputerze" : "zdalnie")));
    elementy.ktoGora.replaceChildren(awatar(kto, { maly: true }));
  }
}

function otworzWiecej() {
  const kafelki = [...stan.widoki.values()].filter((w) => !NA_DOLE.includes(w.meta.id)).map((w) => {
    const n = stan.liczniki[w.meta.id];
    const a = el("a", { class: "kafelek" + (w.meta.id === stan.aktywny ? " aktywny" : ""), href: "#/" + w.meta.id },
      el("span", { class: "kafelek-ikona" }, ikona(maIkone(w.meta.ikona) ? w.meta.ikona : w.meta.id)),
      el("span", { class: "kafelek-tekst" }, w.meta.tytul),
      n ? el("span", { class: "odznaka widoczna" }, String(n)) : null);
    a.addEventListener("click", () => setTimeout(() => ark.zamknij(), 0));
    return a;
  });
  const ark = arkusz({ tytul: "Więcej", tresc: el("div", { class: "kafelki" }, kafelki) });
}

// --------------------------------------------------------------------------- liczniki (odznaki)
function licznik(id, n) {
  n = Number(n) || 0;
  stan.liczniki[id] = n;
  for (const o of document.querySelectorAll('[data-odznaka="' + CSS.escape(id) + '"]')) {
    o.hidden = !n;
    o.textContent = n > 99 ? "99+" : String(n);
  }
  const reszta = Object.entries(stan.liczniki).filter(([k]) => !NA_DOLE.includes(k)).reduce((s, [, v]) => s + (v || 0), 0);
  for (const o of document.querySelectorAll('[data-odznaka="_wiecej"]')) {
    o.hidden = !reszta;
    o.textContent = String(reszta);
  }
  ustawTytulStrony();
}

function ustawTytulStrony() {
  const w = stan.widoki.get(stan.aktywny);
  const czeka = stan.liczniki.raporty || 0;
  document.title = (czeka ? "(" + czeka + ") " : "") + (w ? w.meta.tytul + " · " : "") + "Panel B&C";
}

// --------------------------------------------------------------------------- nawigacja
function parsujHash() {
  const h = (location.hash || "").replace(/^#\/?/, "");
  const znak = h.indexOf("?");
  const id = decodeURIComponent(znak >= 0 ? h.slice(0, znak) : h);
  const p = {};
  if (znak >= 0) {
    for (const [k, v] of new URLSearchParams(h.slice(znak + 1))) p[k] = v;
  }
  return { id: id || "pulpit", p };
}

function idz(id, parametry) {
  parametry = parametry || {};
  if (!stan.widoki.has(id)) id = "pulpit";
  stan.oczekujace = { id, p: parametry };
  const proste = {};
  for (const k of PARAMETRY_W_ADRESIE) {
    const v = parametry[k];
    if (typeof v === "string" || typeof v === "number") proste[k] = String(v);
  }
  const qs = new URLSearchParams(proste).toString();
  const hash = "#/" + id + (qs ? "?" + qs : "");
  if (location.hash === hash) naZmianeAdresu();
  else location.hash = hash;
}

function naZmianeAdresu() {
  let { id, p } = parsujHash();
  if (!stan.widoki.has(id)) id = "pulpit";
  let parametry = p;
  if (stan.oczekujace && stan.oczekujace.id === id) {
    parametry = Object.assign({}, p, stan.oczekujace.p);
  }
  stan.oczekujace = null;
  pokazWidok(id, parametry);
}

function komunikatNiedostepny(w) {
  return el("div", { class: "widok-niedostepny" },
    el("div", { class: "pusty" },
      el("div", { class: "pusty-ikona" }, ikona(maIkone(w.meta.ikona) ? w.meta.ikona : w.meta.id)),
      el("strong", null, "Ten widok jest jeszcze niedostępny"),
      el("p", null, w.meta.tytul + " — ta część panelu jest w budowie albo nie wczytała się poprawnie."),
      w.blad ? el("p", { class: "cichy-tekst blad-techniczny" }, String(w.blad)) : null));
}

function utworzInstancje(w) {
  if (w.inst || w.niedostepny) return;
  if (!w.def) {
    w.niedostepny = true;
    w.kontener.replaceChildren(komunikatNiedostepny(w));
    return;
  }
  try {
    const inst = w.def.utworz(ctx);
    if (!inst || !(inst.el instanceof Node)) throw new Error("utworz() nie zwróciło {el}");
    w.inst = inst;
    if (inst.el.classList && inst.el.classList.contains("widok-pelny")) w.kontener.classList.add("pelny");
    w.kontener.replaceChildren(inst.el);
  } catch (e) {
    console.warn("Widok " + w.meta.id + " nie wstał:", e);
    w.blad = (e && e.message) || String(e);
    w.niedostepny = true;
    w.kontener.replaceChildren(komunikatNiedostepny(w));
  }
}

function pokazWidok(id, parametry) {
  const w = stan.widoki.get(id);
  if (!w) return;
  const poprzedni = stan.aktywny ? stan.widoki.get(stan.aktywny) : null;
  const zmiana = stan.aktywny !== id;
  if (poprzedni && zmiana) {
    poprzedni.kontener.hidden = true;
    if (poprzedni.inst && typeof poprzedni.inst.ukryj === "function") {
      try {
        poprzedni.inst.ukryj();
      } catch (e) {
        console.warn("ukryj()", e);
      }
    }
  }
  stan.aktywny = id;
  document.documentElement.dataset.widok = id;
  utworzInstancje(w);
  w.kontener.hidden = false;
  elementy.tresc.classList.toggle("tresc-pelna", w.kontener.classList.contains("pelny"));
  for (const x of stan.widoki.values()) {
    for (const link of [x.linkBok, x.linkDol]) {
      if (!link) continue;
      link.classList.toggle("aktywny", x.meta.id === id);
      if (x.meta.id === id) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    }
  }
  if (elementy.wiecej) elementy.wiecej.classList.toggle("aktywny", !NA_DOLE.includes(id));
  elementy.tytulGora.textContent = w.meta.tytul;
  ustawTytulStrony();
  if (zmiana) window.scrollTo(0, 0);
  if (w.inst && typeof w.inst.pokaz === "function") {
    try {
      const wynik = w.inst.pokaz(parametry || {});
      if (wynik && typeof wynik.catch === "function") wynik.catch((e) => console.warn("pokaz()", e));
    } catch (e) {
      console.warn("pokaz()", e);
      toast("Widok „" + w.meta.tytul + "” zgłosił błąd: " + (e.message || e), "blad");
    }
  }
  if (zmiana) puls();
}

// --------------------------------------------------------------------------- obecność i liczniki w tle
let ostatniPuls = 0;
function puls() {
  if (STATYCZNY || !ctx.jest("obecnosc")) return;
  if (Date.now() - ostatniPuls < 2000) return;
  ostatniPuls = Date.now();
  api("/api/obecnosc/puls", { metoda: "POST", cialo: { klient: idKlienta(), widok: stan.aktywny }, czas: 10000 }).catch(() => {});
}

async function odswiezLicznikRaportow() {
  if (!ctx.jest("raporty")) return;
  try {
    const d = await api("/api/raporty", { czas: 15000 });
    const n = typeof d.czeka === "number" ? d.czeka : (d.raporty || []).filter((r) => r.status === "czeka").length;
    licznik("raporty", n);
  } catch (e) { /* moduł może jeszcze nie istnieć */ }
}

// --------------------------------------------------------------------------- imię
function ustawKto(imie) {
  imie = String(imie || "").replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, 40);
  zapiszLS("bc.kto", imie || null);
  ctx.ja.kto = imie || ctx.ja.gospodarz || "gość";
  odswiezOsobe();
  window.dispatchEvent(new CustomEvent("bc:kto", { detail: ctx.ja.kto }));
  puls();
}

function zapytajOImie() {
  if (STATYCZNY || czytajLS("bc.kto")) return;
  try {
    if (sessionStorage.getItem("bc.pytano")) return;
    sessionStorage.setItem("bc.pytano", "1");
  } catch (e) { /* nic */ }
  const domyslne = ctx.ja.lokalny ? ctx.ja.gospodarz || "" : "";
  const pole = el("input", { class: "pole", value: domyslne, placeholder: "np. Karol", autocomplete: "given-name", maxlength: "40", "aria-label": "Imię" });
  const zapisz = el("button", { class: "przycisk glowny szeroki", type: "submit" }, "Zapisz");
  const form = el("form", { class: "formularz-imie" },
    el("p", { class: "cichy-tekst" }, "Imię widać przy raportach, komentarzach i w „Kto pracuje”. Zmienisz je w Ustawieniach."),
    el("label", { class: "etykieta" }, "Twoje imię"), pole, zapisz);
  const ark = arkusz({ tytul: "Jak masz na imię?", tresc: form });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = pole.value.trim();
    if (!v) {
      pole.focus();
      return;
    }
    ustawKto(v);
    ark.zamknij();
    toast("Cześć, " + v + "!", "ok");
  });
}

// --------------------------------------------------------------------------- start
async function zaladujWidok(meta) {
  try {
    const m = await import("./widoki/" + meta.id + ".js");
    const def = m && m.default;
    if (!def || typeof def.utworz !== "function") throw new Error("moduł nie eksportuje { utworz(ctx) }");
    return { def };
  } catch (e) {
    return { blad: (e && e.message) || String(e) };
  }
}

async function zaCzas(obietnica, ms) {
  return Promise.race([obietnica, new Promise((r) => setTimeout(() => r(undefined), ms))]);
}

async function start() {
  const zdrowie = STATYCZNY ? Promise.resolve(null) : api("/api/zdrowie", { czas: 20000 }).catch(() => null);
  const [ja, cfg, ...moduly] = await Promise.all([
    api("/api/ja", { czas: 10000 }).catch(() => null),
    api("/api/konfiguracja", { czas: 10000 }).catch(() => null),
    ...WIDOKI.map(zaladujWidok),
  ]);
  if (ja) Object.assign(ctx.ja, ja);
  else ctx.ja = Object.assign(ctx.ja, { kto: czytajLS("bc.kto") || "gość", lokalny: false, tryb_statyczny: STATYCZNY });
  const zapisane = czytajLS("bc.kto");
  if (zapisane) ctx.ja.kto = zapisane;
  if (cfg) ctx.konfiguracja = Object.assign(ctx.konfiguracja, cfg, { gra: Object.assign({}, ctx.konfiguracja.gra, cfg.gra || {}) });

  WIDOKI.forEach((meta, i) => {
    const m = moduly[i];
    const def = m.def || null;
    const pelnaMeta = Object.assign({}, meta);
    if (def) {
      if (def.tytul) pelnaMeta.tytul = String(def.tytul);
      if (def.ikona) pelnaMeta.ikona = String(def.ikona);
    }
    stan.widoki.set(meta.id, { meta: pelnaMeta, def, blad: m.blad || null });
  });

  zbudujPowloke();

  // wikilinki w całym panelu → widok sieci z notatką
  document.addEventListener("click", (e) => {
    const a = e.target.closest && e.target.closest("a[data-wikilink]");
    if (!a || e.defaultPrevented || e.ctrlKey || e.metaKey || e.shiftKey) return;
    e.preventDefault();
    idz("siec", { notatka: a.dataset.wikilink, naglowek: a.dataset.naglowek || undefined });
  });

  window.addEventListener("hashchange", naZmianeAdresu);
  naZmianeAdresu();

  const d = await zaCzas(zdrowie, 1500);
  const ustawModuly = (z) => {
    if (z && z.moduly) stan.moduly = z.moduly;
  };
  if (d !== undefined) ustawModuly(d);
  else zdrowie.then(ustawModuly);

  zapytajOImie();
  if (!STATYCZNY) {
    puls();
    odpytuj(puls, 20000);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") puls();
    });
  }
  odswiezLicznikRaportow();
  odpytuj(odswiezLicznikRaportow, 60000);
}

start().catch((e) => {
  console.warn("Panel nie wystartował", e);
  const app = document.getElementById("aplikacja");
  if (app) {
    app.replaceChildren(el("div", { class: "start-ekran" },
      el("div", { class: "logo-znak duze" }, "B&C"),
      el("p", { class: "start-tekst" }, "Panel nie wystartował: " + ((e && e.message) || e)),
      el("button", { class: "przycisk glowny", onclick: () => location.reload() }, "Spróbuj ponownie")));
  }
});
