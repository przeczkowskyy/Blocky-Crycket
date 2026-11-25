// Powłoka panelu: nawigacja (#/<id>), ładowanie widoków, odznaki, puls obecności, aktywne osoby, imię osoby, tryb statyczny.

import { api, apiSurowe, sse, STATYCZNY, plik } from "./wspolne/api.js";
import { el, ikona, maIkone, toast, arkusz, awatar } from "./wspolne/ui.js";
import { pobierzKolejke } from "./wspolne/kolejka.js";
import { pobierzPrace, godzina as godzinaPracy } from "./wspolne/prace.js";
import { ustawRejestr, maRejestr, wybranaGra, nazwaGry, listaGier, liczbyGier, czekaGdzieIndziej, wybierzGre, gra as graRejestru,
  WSZYSTKIE } from "./wspolne/gry.js";

// Kolejność i opisy na wypadek, gdyby moduł widoku nie wstał (wtedy pokazujemy komunikat zamiast niego).
// Zakładka Pytania łączy dawne Plan, Raporty i Decyzje; stare adresy (#/decyzje, #/plan, #/raporty,
// #/raporty/<id>) przekierowują.
const WIDOKI = [
  { id: "pulpit", tytul: "Pulpit", ikona: "pulpit", kolejnosc: 10 },
  { id: "pytania", tytul: "Pytania", ikona: "pytanie", kolejnosc: 20 },
  { id: "wytwornia", tytul: "Wytwórnia", ikona: "zarowka", kolejnosc: 25 },
  { id: "sesja", tytul: "Sesja", ikona: "mikrofon", kolejnosc: 30 },
  { id: "podglad", tytul: "Podgląd", ikona: "podglad", kolejnosc: 40 },
  { id: "agent", tytul: "Agent", ikona: "agent", kolejnosc: 50 },
  { id: "siec", tytul: "Sieć", ikona: "siec", kolejnosc: 60 },
  { id: "assety", tytul: "Assety", ikona: "assety", kolejnosc: 65 },
  { id: "analityka", tytul: "Analityka", ikona: "analityka", kolejnosc: 70 },
  { id: "ustawienia", tytul: "Ustawienia", ikona: "ustawienia", kolejnosc: 80 },
];
const NA_DOLE = ["pulpit", "pytania", "sesja", "podglad"];
const PARAMETRY_W_ADRESIE = ["raport", "notatka", "migawka", "grupa", "zakladka", "watek", "sekcja", "sprawa", "szukaj", "pomysl", "gra"];
// dawne zakładki Planu i sekcje zakładki Decyzje -> części zakładki Pytania (Plan albo historia „Odpowiedziane”)
const SEKCJE_PLANU = { harmonogram: "roadmapa", zadania: "zadania", decyzje: "historia", pytania: "historia", dziennik: "dziennik" };
const SEKCJE_DECYZJI = { zadania: "zadania", roadmapa: "roadmapa", dziennik: "dziennik", raporty: "historia", rejestr: "historia", pytania: "historia" };
// nazwy dawnych zakładek w „Teraz na panelu” (przeglądarka ze starą wersją panelu zgłasza stary identyfikator)
const DAWNE_WIDOKI = { plan: "Pytania", raporty: "Pytania", decyzje: "Pytania" };
const STANY_ROZMOWY = { mowi: "mówi", wyciszony: "wyciszony", bez_mikrofonu: "bez mikrofonu", polaczony: "w rozmowie", laczenie: "łączy się" };

const stan = {
  widoki: new Map(),          // id -> {meta, def, inst, kontener, blad}
  aktywny: null,
  oczekujace: null,
  liczniki: {},
  moduly: null,
  obecnosc: null,             // ostatnia odpowiedź pulsu / GET /api/obecnosc
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
  /** Czy serwer NA PEWNO ma działający moduł (wymieniony w /api/zdrowie) — dla nowych tras, których stary serwer nie zna. */
  znaModul: (nazwa) => !!(stan.moduly && stan.moduly[nazwa] && stan.moduly[nazwa].ok === true),
  /** Czy panel ma taką zakładkę. */
  maWidok: (id) => stan.widoki.has(id),
  nazwaWidoku: (id) => (stan.widoki.get(id) ? stan.widoki.get(id).meta.tytul : DAWNE_WIDOKI[id] || id),
  /** Ostatnia znana obecność (odpowiedź pulsu): {panel, studio, git, rozmowa?} albo null. */
  get obecnosc() {
    return stan.obecnosc;
  },
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
  elementy.obecniBok = el("div", { class: "bok-obecni", hidden: true, "aria-label": "Kto jest teraz na panelu" });
  elementy.obecniGora = el("button", { type: "button", class: "gora-obecni", hidden: true, "aria-haspopup": "dialog", onclick: otworzObecnych });
  // prace w toku (wspolne/prace.js): mały napis „Prace: 3 · najbliższy koniec 11:45”, klik = Pulpit
  elementy.praceBok = el("a", { class: "bok-prace", href: "#/pulpit", hidden: true });
  elementy.praceGora = el("a", { class: "gora-prace", href: "#/pulpit", hidden: true });

  const marka = () => el("a", { class: "marka", href: "#/pulpit", "aria-label": "Pulpit" },
    el("span", { class: "logo-znak", "aria-hidden": "true" }, "B&C"));

  // Przełącznik gier (wspolne/gry.js): z rejestrem gier nazwa gry w nagłówku jest przyciskiem — telefon: górny pasek,
  // komputer: nagłówek bocznego paska. Bez rejestru — sama nazwa gry, jak dawniej.
  const gry = maRejestr();
  elementy.graGora = el("span", { class: "gora-gra" }, ctx.konfiguracja.gra.nazwa || "BLOCKY & CRYCKET");
  const tekstBoku = gry
    ? el("button", { type: "button", class: "bok-marka-tekst przelacznik-gry", "aria-haspopup": "dialog", onclick: otworzWyborGry },
      el("span", { class: "przelacznik-gry-nazwa" }, elementy.nazwaGry, ikona("dol")), el("span", { class: "marka-pod" }, "Panel zespołu"))
    : el("div", { class: "bok-marka-tekst" }, elementy.nazwaGry, el("span", { class: "marka-pod" }, "Panel zespołu"));
  const tytulyGory = gry
    ? el("button", { type: "button", class: "gora-tytuly przelacznik-gry", "aria-haspopup": "dialog", onclick: otworzWyborGry },
      el("span", { class: "przelacznik-gry-nazwa" }, elementy.graGora, ikona("dol")), elementy.tytulGora)
    : el("div", { class: "gora-tytuly" }, elementy.graGora, elementy.tytulGora);
  elementy.przelaczniki = gry ? [tekstBoku, tytulyGory] : [];

  const bok = el("aside", { class: "bok" },
    el("div", { class: "bok-marka" }, marka(), tekstBoku),
    navBok,
    el("div", { class: "bok-stopka" }, elementy.praceBok, elementy.obecniBok, elementy.ktoBok));

  const gora = el("header", { class: "gora" }, marka(), tytulyGory, elementy.praceGora, elementy.obecniGora, elementy.ktoGora);

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
  odswiezPrzelacznikGier();
}

// --------------------------------------------------------------------------- przełącznik gier (pulpit per gra, 25.11)
/** Nazwa wybranej gry w nagłówku i plakietka „+N”: ile spraw czeka na ludzi w innych grach (wstrzymane też). */
function odswiezPrzelacznikGier() {
  if (!elementy.przelaczniki || !elementy.przelaczniki.length) return;
  const nazwa = nazwaGry(wybranaGra());
  elementy.nazwaGry.textContent = nazwa;
  elementy.graGora.textContent = nazwa;
  const inne = czekaGdzieIndziej();
  for (const b of elementy.przelaczniki) {
    // boczny pasek komputera jest wąski: plakietka w drugim wierszu („Panel zespołu +7”), na telefonie obok nazwy
    const miejsce = b.querySelector(".marka-pod") || b.querySelector(".przelacznik-gry-nazwa");
    let plak = miejsce.querySelector(".przelacznik-gry-inne");
    if (inne && !plak) {
      plak = el("span", { class: "przelacznik-gry-inne" });
      miejsce.append(plak);
    }
    if (plak) {
      plak.hidden = !inne;
      plak.textContent = "+" + inne;
    }
    b.setAttribute("aria-label", "Gra: " + nazwa + (inne ? ". W innych grach czeka: " + inne : "") + ". Zmień grę");
    b.title = inne ? "W innych grach czeka: " + inne + " — zmień grę" : "Zmień grę";
  }
  if (elementy.arkuszGier && elementy.arkuszGier.el.isConnected) elementy.arkuszGier.cialo.replaceChildren(listaWyboruGry());
}

/** Lista w oknie „Która gra?”: każda gra (wstrzymane przygaszone) z liczbą spraw czekających na ludzi i „Wszystkie gry”. */
function listaWyboruGry() {
  const liczby = liczbyGier();
  const wybrana = wybranaGra();
  const opcja = (id, nazwa, n, wstrzymana) => el("button", {
    type: "button", class: "gra-opcja" + (id === wybrana ? " wybrana" : "") + (wstrzymana ? " wstrzymana" : ""),
    "aria-pressed": id === wybrana ? "true" : "false", dataset: { gra: id },
    onclick: () => {
      wybierzGre(id);
      if (elementy.arkuszGier) elementy.arkuszGier.zamknij();
    },
  },
  el("span", { class: "gra-opcja-znak", "aria-hidden": "true" }, id === wybrana ? ikona("ok") : null),
  el("span", { class: "gra-opcja-nazwa" }, nazwa, wstrzymana ? el("span", { class: "gra-opcja-stan" }, "wstrzymana") : null),
  n ? el("span", { class: "gra-opcja-liczba", title: "Czeka na ludzi: " + n }, String(n)) : null);
  const wspolne = Object.keys(liczby).filter((id) => graRejestru(id) && graRejestru(id).wspolne);
  const nWspolne = wspolne.reduce((s, id) => s + (liczby[id] || 0), 0);
  const razem = Object.values(liczby).reduce((s, v) => s + (v || 0), 0);
  const nazwaWspolnych = graRejestru("wspolne") ? graRejestru("wspolne").nazwa : "Wspólne";
  return el("div", { class: "gry-wybor" },
    el("div", { class: "gry-lista" },
      listaGier().map((g) => opcja(g.id, g.nazwa, liczby[g.id] || 0, g.stan === "wstrzymana")),
      opcja(WSZYSTKIE, "Wszystkie gry", razem, false)),
    el("p", { class: "cichy-tekst gry-przypis" }, nazwaWspolnych + " (panel, sesje główne) widać w każdej grze" +
      (nWspolne ? " — czeka " + nWspolne : "") + ". Liczba = sprawy czekające na ludzi."));
}

function otworzWyborGry() {
  const ark = arkusz({ tytul: "Która gra?", tresc: listaWyboruGry(), naZamkniecie: () => { elementy.arkuszGier = null; } });
  elementy.arkuszGier = ark;
  pobierzKolejke(ctx).catch(() => {});                         // świeże liczby (zdarzenie bc:gry-liczby przerysuje listę)
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

// --------------------------------------------------------------------------- aktywne osoby (lewy dolny róg / górny pasek)
/** Osoby z pulsów, bez powtórzeń (dwie karty tej samej osoby = jedna osoba), z ich stanem w rozmowie z zakładki Sesja. */
function osobyObecne(d) {
  const rozmowa = (d && d.rozmowa && typeof d.rozmowa === "object") ? d.rozmowa : { aktywna: false, slucha: false, osoby: [] };
  const wRozmowie = new Map();
  for (const o of rozmowa.osoby || []) {
    const k = String(o.kto || "").trim().toLowerCase();
    if (k && !wRozmowie.has(k)) wRozmowie.set(k, o);
  }
  const osoby = new Map();
  for (const p of (d && d.panel) || []) {
    const kto = String(p.kto || "").trim() || "gość";
    const k = kto.toLowerCase();
    if (osoby.has(k)) continue;                                // lista idzie od najświeższego pulsu
    osoby.set(k, { kto, widok: p.widok || "", lokalny: !!p.lokalny, rozmowa: wRozmowie.get(k) || null });
  }
  for (const [k, o] of wRozmowie) {                            // w rozmowie, ale bez otwartego panelu w tej chwili
    if (!osoby.has(k)) osoby.set(k, { kto: o.kto, widok: "sesja", lokalny: false, rozmowa: o });
  }
  return { osoby: [...osoby.values()], slucha: !!rozmowa.slucha, aktywna: !!rozmowa.aktywna };
}

function wierszOsoby(o) {
  const ja = (ctx.ja.kto || "").trim().toLowerCase() === o.kto.toLowerCase();
  const stanMik = o.rozmowa ? STANY_ROZMOWY[o.rozmowa.stan] || "w rozmowie" : "";
  return el("li", { class: "obecny" + (o.rozmowa ? " w-rozmowie" : "") },
    el("span", { class: "obecny-kropka" + (o.rozmowa && o.rozmowa.stan === "mowi" ? " mowi" : ""), "aria-hidden": "true" }),
    el("span", { class: "obecny-tekst" },
      el("strong", null, o.kto + (ja ? " (Ty)" : "")),
      el("span", null, o.widok ? ctx.nazwaWidoku(o.widok) : "panel")),
    o.rozmowa ? el("span", { class: "obecny-rozmowa", title: "W rozmowie (zakładka Sesja): " + stanMik },
      ikona(o.rozmowa.stan === "wyciszony" || o.rozmowa.stan === "bez_mikrofonu" ? "zamknij" : "mikrofon"), stanMik) : null);
}

function listaObecnych(dane) {
  return [
    dane.slucha ? el("p", { class: "obecni-slucha", role: "status" }, el("span", { class: "kropka-nagrywania", "aria-hidden": "true" }), "Agent słucha rozmowy") : null,
    el("ul", { class: "obecni-lista" }, dane.osoby.map(wierszOsoby)),
  ];
}

function odswiezObecnych() {
  if (!elementy.obecniBok || STATYCZNY) return;
  const dane = osobyObecne(stan.obecnosc);
  const n = dane.osoby.length;
  elementy.obecniBok.hidden = !n;
  elementy.obecniGora.hidden = !n;
  if (!n) return;
  elementy.obecniBok.replaceChildren(el("p", { class: "obecni-tytul" }, "Teraz na panelu"), ...listaObecnych(dane).filter(Boolean));
  elementy.obecniGora.replaceChildren(...[ikona("zespol"), el("span", null, String(n)),
    dane.slucha ? el("span", { class: "kropka-nagrywania", "aria-hidden": "true" }) : null].filter(Boolean));
  elementy.obecniGora.setAttribute("aria-label", "Na panelu: " + n + (dane.slucha ? ", agent słucha rozmowy" : "") + " — pokaż kto");
  if (elementy.arkuszObecnych && elementy.arkuszObecnych.el.isConnected) {
    elementy.arkuszObecnych.cialo.replaceChildren(el("div", { class: "obecni-arkusz" }, ...listaObecnych(dane).filter(Boolean)));
  }
}

function otworzObecnych() {
  const dane = osobyObecne(stan.obecnosc);
  const tresc = el("div", { class: "obecni-arkusz" }, ...listaObecnych(dane).filter(Boolean),
    el("div", { class: "rzad-przyciskow" }, el("a", { class: "przycisk maly", href: "#/sesja", onclick: () => setTimeout(() => ark.zamknij(), 0) }, ikona("mikrofon"), el("span", null, "Sesja"))));
  const ark = arkusz({ tytul: "Teraz na panelu", tresc, naZamkniecie: () => { elementy.arkuszObecnych = null; } });
  elementy.arkuszObecnych = ark;
}

// --------------------------------------------------------------------------- liczniki (odznaki)
function licznik(id, n) {
  n = Number(n) || 0;
  stan.liczniki[id] = n;
  for (const o of document.querySelectorAll('[data-odznaka="' + CSS.escape(id) + '"]')) {
    o.hidden = !n;
    o.textContent = n > 99 ? "99+" : String(n);
  }
  const reszta = Object.entries(stan.liczniki).filter(([k]) => stan.widoki.has(k) && !NA_DOLE.includes(k)).reduce((s, [, v]) => s + (v || 0), 0);
  for (const o of document.querySelectorAll('[data-odznaka="_wiecej"]')) {
    o.hidden = !reszta;
    o.textContent = String(reszta);
  }
  ustawTytulStrony();
}

function ustawTytulStrony() {
  const w = stan.widoki.get(stan.aktywny);
  const czeka = stan.liczniki.pytania || 0;
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

/** Dawne adresy Planu, Raportów i Decyzji → zakładka Pytania (właściwa część albo karta). */
function przekieruj(id, p) {
  p = Object.assign({}, p || {});
  const m = /^raporty\/(.+)$/.exec(id || "");
  if (m) {
    p.raport = m[1];
    id = "raporty";
  }
  if (id === "raporty") return { id: "pytania", p: p.raport ? { raport: String(p.raport) } : {} };
  if (id === "plan") {
    const sekcja = SEKCJE_PLANU[p.zakladka];
    return { id: "pytania", p: sekcja ? { sekcja } : {} };
  }
  if (id === "decyzje") {
    const q = {};
    for (const k of ["sprawa", "raport", "szukaj"]) if (p[k]) q[k] = String(p[k]);
    if (SEKCJE_DECYZJI[p.sekcja]) q.sekcja = SEKCJE_DECYZJI[p.sekcja];
    return { id: "pytania", p: q };
  }
  return { id, p };
}

function adres(id, parametry) {
  const proste = {};
  for (const k of PARAMETRY_W_ADRESIE) {
    const v = parametry[k];
    if (typeof v === "string" || typeof v === "number") proste[k] = String(v);
  }
  const qs = new URLSearchParams(proste).toString();
  return "#/" + id + (qs ? "?" + qs : "");
}

function idz(id, parametry) {
  ({ id, p: parametry } = przekieruj(id, parametry || {}));
  if (!stan.widoki.has(id)) id = "pulpit";
  stan.oczekujace = { id, p: parametry };
  const hash = adres(id, parametry);
  if (location.hash === hash) naZmianeAdresu();
  else location.hash = hash;
}

function naZmianeAdresu() {
  let { id, p } = parsujHash();
  const po = przekieruj(id, p);
  if (po.id !== id) {                                          // stary adres: podmień w pasku bez nowego wpisu w historii
    id = po.id;
    p = po.p;
    try {
      history.replaceState(null, "", adres(id, p));
    } catch (e) { /* nic */ }
  }
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
let pulsZaplanowany = null;
function puls() {
  if (STATYCZNY || !ctx.jest("obecnosc")) return;
  const czekaj = 2000 - (Date.now() - ostatniPuls);
  if (czekaj > 0) {                                            // najwyżej jeden puls na 2 s, ale ostatnia zakładka dochodzi
    if (!pulsZaplanowany) pulsZaplanowany = setTimeout(() => { pulsZaplanowany = null; puls(); }, czekaj);
    return;
  }
  ostatniPuls = Date.now();
  api("/api/obecnosc/puls", { metoda: "POST", cialo: { klient: idKlienta(), widok: stan.aktywny }, czas: 10000 })
    .then((d) => {
      if (d && typeof d === "object" && Array.isArray(d.panel)) {
        stan.obecnosc = d;
        odswiezObecnych();
        window.dispatchEvent(new CustomEvent("bc:obecnosc", { detail: d }));
      }
    })
    .catch(() => {});
}

/** Plakietka zakładki Pytania: cała lista „Do odpowiedzi” (bez odłożonych na sesję). Widoki Pytania, Sesja i Pulpit
 * liczą ją same, gdy są otwarte. */
async function odswiezLicznikSpraw() {
  if (stan.aktywny === "pytania" || stan.aktywny === "sesja" || stan.aktywny === "pulpit") return;
  try {
    const { kolejka } = await pobierzKolejke(ctx);
    licznik("pytania", kolejka.aktywne.length);
  } catch (e) { /* moduł może jeszcze nie istnieć */ }
}

// --------------------------------------------------------------------------- stała synchronizacja z GitHubem (D-070)
// Co 30 s GET /api/git/auto (sam stan, serwer nie uruchamia gita) — każda odpowiedź idzie do widoków zdarzeniem
// bc:git-auto. Gdy panel sam pobrał nowe zmiany — krótka informacja „kto i co” (zwykły tekst) i zdarzenie
// bc:git-pobrano dla widoków. Pierwsze sprawdzenie tylko zapamiętuje stan.
// Stary serwer bez tej trasy (404) — nic się nie zmienia; kolejna próba za 5 min (po restarcie panelu ruszy sama).
const sync = { ostatnie: null, przerwaDo: 0 };
async function sprawdzSynchronizacje() {
  if (STATYCZNY || Date.now() < sync.przerwaDo || !ctx.jest("gitsync")) return;
  let a;
  try {
    a = await api("/api/git/auto", { czas: 10000 });
  } catch (e) {
    if (e && (e.status === 404 || e.status === 405)) sync.przerwaDo = Date.now() + 5 * 60000;
    return;
  }
  if (a && typeof a === "object") window.dispatchEvent(new CustomEvent("bc:git-auto", { detail: a }));   // np. pasek w Assetach
  const p = a && typeof a === "object" ? a.pobranie : null;
  const id = p && p.id ? String(p.id) : "";
  if (sync.ostatnie !== null && id && id !== sync.ostatnie) {
    const n = Number(p.ile) || 0;
    const tematy = (p.commity || []).slice(0, 2).map((c) => "„" + String(c.temat || "").slice(0, 60) + "”").join("; ");
    toast("Z GitHuba: " + (p.autorzy || []).join(", ") + " — " + n + " " + (n === 1 ? "zmiana" : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? "zmiany" : "zmian") +
      (tematy ? ": " + tematy : "") + ". Panel już je pobrał.", "info", { czas: 9000 });
    window.dispatchEvent(new CustomEvent("bc:git-pobrano", { detail: p }));
  }
  sync.ostatnie = id;
}

// --------------------------------------------------------------------------- prace w toku (plakietka)
// „Prace: 3 · najbliższy koniec 11:45” na dole bocznego paska (komputer) i krótko „3 · 11:45” w górnym pasku
// (telefon); klik = Pulpit z kartą „Prace w toku”. Stary serwer i lustro: bez plakietki i bez żądań.
function odswiezPlakietkePrac(d) {
  if (!elementy.praceBok) return;
  const wToku = ((d && d.prace) || []).filter((p) => p.stan === "w_toku");
  const n = wToku.length;
  elementy.praceBok.hidden = !n;
  elementy.praceGora.hidden = !n;
  if (!n) return;
  const konce = wToku.map((p) => Date.parse(p.koniec_szacowany)).filter(isFinite);
  const najblizszy = konce.length ? godzinaPracy(new Date(Math.min(...konce)).toISOString()) : "";
  const opis = "Prace: " + n + (najblizszy ? " · najbliższy koniec " + najblizszy : "");
  elementy.praceBok.replaceChildren(ikona("zegar"), el("span", null, opis));
  elementy.praceBok.setAttribute("aria-label", opis + " — Pulpit");
  elementy.praceGora.replaceChildren(ikona("zegar"), el("span", null, String(n) + (najblizszy ? " · " + najblizszy : "")));
  elementy.praceGora.setAttribute("aria-label", opis + " — Pulpit");
}

async function sprawdzPrace() {
  odswiezPlakietkePrac(await pobierzPrace(ctx));
}

// --------------------------------------------------------------------------- moduły serwera (/api/zdrowie)
// Lista modułów z /api/zdrowie mówi, o które nowe trasy wolno pytać (ctx.znaModul). Gdy serwer nie zna jeszcze prac
// (strona otwarta przed restartem panelu albo pierwsze /api/zdrowie bez odpowiedzi), co 3 min lekki GET /api/ping:
// inny numer procesu (pid) = panel po restarcie — wtedy znowu /api/zdrowie i zdarzenie bc:moduly, więc karta „Prace
// w toku”, plakietka i znaczki pojawiają się bez przeładowania strony. Testy przeglądarkowe skracają przerwę
// (window.BC_TEST_MODULY_MS).
const modulySerwera = { pid: null, ostatnio: 0, trwa: false };
const CO_ILE_MODULY_MS = Math.max(500, Number(window.BC_TEST_MODULY_MS) || 3 * 60000);

function ustawModuly(z, pid) {
  if (!z || !z.moduly) return false;
  stan.moduly = z.moduly;
  if (pid !== undefined) modulySerwera.pid = pid;
  window.dispatchEvent(new CustomEvent("bc:moduly"));          // widoki mogą już pytać o nowe trasy (np. /api/prace)
  return true;
}

async function sprawdzModuly() {
  if (STATYCZNY || ctx.znaModul("prace") || modulySerwera.trwa) return;
  if (Date.now() - modulySerwera.ostatnio < CO_ILE_MODULY_MS) return;
  modulySerwera.trwa = true;
  modulySerwera.ostatnio = Date.now();
  try {
    const p = await api("/api/ping", { czas: 8000 }).catch(() => null);
    if (!p || p.pid === undefined) return;                     // panel nie odpowiada — spróbujemy za 3 min
    if (stan.moduly && p.pid === modulySerwera.pid) return;    // ten sam serwer — nic nowego
    const z = await api("/api/zdrowie", { czas: 30000 }).catch(() => null);
    ustawModuly(z, p.pid);
  } finally {
    modulySerwera.trwa = false;
  }
}

// --------------------------------------------------------------------------- imię
function ustawKto(imie) {
  imie = String(imie || "").replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, 40);
  zapiszLS("bc.kto", imie || null);
  ctx.ja.kto = imie || ctx.ja.gospodarz || "gość";
  odswiezOsobe();
  odswiezObecnych();
  window.dispatchEvent(new CustomEvent("bc:kto", { detail: ctx.ja.kto }));
  ostatniPuls = 0;
  puls();
}

function zapytajOImie() {
  if (STATYCZNY || czytajLS("bc.kto")) return;
  try {
    if (sessionStorage.getItem("bc.pytano")) return;
    sessionStorage.setItem("bc.pytano", "1");
  } catch (e) { /* nic */ }
  // Podpowiedź z gita tylko jako samo imię (pierwszy wyraz): podpis trafia do publicznych plików sejfu.
  const domyslne = ctx.ja.lokalny ? String(ctx.ja.gospodarz || "").trim().split(/\s+/)[0] || "" : "";
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
  const ping = STATYCZNY ? Promise.resolve(null) : api("/api/ping", { czas: 10000 }).catch(() => null);
  modulySerwera.ostatnio = Date.now();
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
  ustawRejestr(cfg && cfg.gry);                                // rejestr gier (wspolne/gry.js); bez niego — jedna gra

  WIDOKI.forEach((meta, i) => {
    const m = moduly[i];
    const def = m.def || null;
    const pelnaMeta = Object.assign({}, meta);
    if (def) {                                                 // nazwy w nawigacji są krótkie i stałe (WIDOKI wyżej)
      if (def.tytul && !pelnaMeta.tytul) pelnaMeta.tytul = String(def.tytul);
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
  window.addEventListener("bc:gra", () => {                    // inna gra: nagłówek i plakietka Pytań (widoki przerysowują się same)
    odswiezPrzelacznikGier();
    odswiezLicznikSpraw();
  });
  window.addEventListener("bc:gry-liczby", odswiezPrzelacznikGier);
  naZmianeAdresu();

  const d = await zaCzas(zdrowie, 1500);
  const naZdrowie = (z) => ping.then((p) => ustawModuly(z, p && p.pid !== undefined ? p.pid : null));
  if (d !== undefined) naZdrowie(d);
  else zdrowie.then(naZdrowie);

  zapytajOImie();
  if (!STATYCZNY) {
    puls();
    odpytuj(puls, 20000);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") puls();
    });
  }
  odswiezLicznikSpraw();
  odpytuj(odswiezLicznikSpraw, 60000);
  if (!STATYCZNY) {
    sprawdzSynchronizacje();
    odpytuj(sprawdzSynchronizacje, 30000);
    window.addEventListener("bc:prace", (e) => odswiezPlakietkePrac(e.detail));
    window.addEventListener("bc:moduly", () => sprawdzPrace());
    sprawdzPrace();
    odpytuj(sprawdzPrace, 30000);
    odpytuj(sprawdzModuly, Math.min(60000, CO_ILE_MODULY_MS));
  }
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
