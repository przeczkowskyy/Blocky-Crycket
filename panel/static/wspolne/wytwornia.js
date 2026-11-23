// Wspólne klocki Wytwórni (zakładka Wytwórnia i karta „Gry” na Pulpicie): etapy, werdykty, metryki gier, paski ocen,
// karta gry z portfela. Dane: GET /api/wytwornia (bc/wytwornia.py). Styl: widoki/wytwornia.css (dołączany tu).

import { el, ikona } from "./ui.js";

const CSS = new URL("../widoki/wytwornia.css", import.meta.url).href;

export const ETAPY = ["pomysł", "ocena", "prototyp", "test", "publiczna", "wstrzymana", "porzucona"];
export const ETAPY_LEJKA = ["pomysł", "ocena", "prototyp", "test", "publiczna"];
export const ETAPY_GIER = ["prototyp", "test", "publiczna"];
export const NAZWY_ETAPOW = { "pomysł": "Pomysł", ocena: "Ocena", prototyp: "Prototyp", test: "Test", publiczna: "Publiczna", wstrzymana: "Wstrzymana", porzucona: "Porzucona" };
const KOLORY_ETAPOW = { "pomysł": "szary", ocena: "niebieski", prototyp: "fiolet", test: "zloto", publiczna: "zielen", wstrzymana: "szary", porzucona: "czerwien" };
export const WERDYKTY = { buduj: "zielen", popraw: "zloto", "odrzuć": "czerwien" };
export const METRYKI = [
  { id: "d1", tekst: "D1", opis: "powrót następnego dnia" },
  { id: "d7", tekst: "D7", opis: "powrót po tygodniu" },
  { id: "sesja_min", tekst: "Sesja", opis: "średnia sesja" },
  { id: "ccu", tekst: "Gracze naraz", opis: "CCU" },
];
export const MAKS_SUMY = 30;

export function dolaczStyl() {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === CSS)) {
    document.head.append(el("link", { rel: "stylesheet", href: CSS }));
  }
}

/** „karol” / „pawel” — pierwsze słowo imienia bez wielkości liter i polskich znaków (jak sejf.kanoniczne). */
export function kanon(imie) {
  const s = String(imie || "").trim().split(/\s+/)[0] || "";
  return s.toLowerCase().replace(/ł/g, "l").normalize("NFD").replace(/[̀-ͯ]/g, "");
}

export function chipEtapu(etap) {
  return el("span", { class: "chip " + (KOLORY_ETAPOW[etap] || "szary") }, NAZWY_ETAPOW[etap] || etap || "pomysł");
}

export function chipWerdyktu(w, { krotko } = {}) {
  if (!w) return null;
  return el("span", { class: "chip " + (WERDYKTY[w] || "szary"), title: "Werdykt agenta" }, krotko ? w : "agent: " + w);
}

/** Wartość metryki do pokazania albo null (brak danych). D1/D7 w procentach: 12 = 12 %, 0.12 = 12 %. */
export function wartoscMetryki(id, v) {
  if (v === null || v === undefined || v === "") return null;
  const s = String(v).trim();
  if (id === "d1" || id === "d7") {
    if (/%$/.test(s)) return s.replace(/\s*%$/, " %");
    const n = Number(s.replace(",", "."));
    if (!isFinite(n)) return s;
    const proc = n > 0 && n < 1 && !Number.isInteger(n) ? n * 100 : n;
    return (Math.round(proc * 10) / 10).toString().replace(".", ",") + " %";
  }
  if (id === "sesja_min") {
    const n = Number(s.replace(",", "."));
    return (isFinite(n) ? String(Math.round(n * 10) / 10).replace(".", ",") : s) + " min";
  }
  return s;
}

export function maMetryki(p) {
  return METRYKI.some((m) => wartoscMetryki(m.id, (p.metryki || {})[m.id]) !== null);
}

/** Kafelki metryk; puste = „brak danych”. */
export function metrykiEl(p, { duze } = {}) {
  return el("div", { class: "wyt-metryki" + (duze ? " duze" : "") }, METRYKI.map((m) => {
    const w = wartoscMetryki(m.id, (p.metryki || {})[m.id]);
    return el("div", { class: "wyt-metryka" + (w === null ? " brak" : ""), title: m.opis },
      el("span", { class: "wyt-metryka-nazwa" }, m.tekst),
      el("strong", { class: "wyt-metryka-wartosc" }, w === null ? "brak danych" : w));
  }));
}

/** Pasek 0–30 z podpisem: „Agent ▮▮▮▯ 17/30” (brak oceny = „—”). */
export function pasekOceny(kto, wartosc, maks = MAKS_SUMY, klasa = "") {
  const v = typeof wartosc === "number" && isFinite(wartosc) ? wartosc : null;
  const proc = v === null ? 0 : Math.max(0, Math.min(100, (v / maks) * 100));
  return el("div", { class: "wyt-ocena " + klasa + (v === null ? " brak" : "") },
    el("span", { class: "wyt-ocena-kto" }, kto),
    el("span", { class: "pasek wyt-pasek", role: "img", "aria-label": kto + ": " + (v === null ? "bez oceny" : v + " z " + maks) },
      el("span", { class: "pasek-wypelnienie", style: { width: proc + "%" } })),
    el("span", { class: "wyt-ocena-liczba" }, v === null ? "—" : v + "/" + maks));
}

export function paskiOcen(p) {
  return el("div", { class: "wyt-oceny" },
    pasekOceny("Agent", p.ocena_agenta, MAKS_SUMY, "wyt-ocena-agent"),
    pasekOceny("Karol", p.ocena_karol, MAKS_SUMY, "wyt-ocena-czlowiek"),
    pasekOceny("Paweł", p.ocena_pawel, MAKS_SUMY, "wyt-ocena-czlowiek"));
}

export const adresPomyslu = (id) => "#/wytwornia?pomysl=" + encodeURIComponent(id);
export const adresGry = (id) => "#/wytwornia?gra=" + encodeURIComponent(id);

/** Karta gry z portfela (etap prototyp / test / publiczna): nazwa, etap, zdanie, metryki, „Pulpit gry”. */
export function kartaGry(p, { zwarta } = {}) {
  dolaczStyl();
  return el("article", { class: "wyt-gra" + (zwarta ? " zwarta" : ""), dataset: { gra: p.id } },
    el("div", { class: "wyt-gra-gora" },
      el("h3", { class: "wyt-gra-nazwa" }, p.nazwa),
      chipEtapu(p.etap)),
    p.zdanie && !zwarta ? el("p", { class: "wyt-zdanie" }, p.zdanie) : null,
    metrykiEl(p),
    el("div", { class: "rzad-przyciskow wyt-gra-akcje" },
      el("a", { class: "przycisk glowny maly", href: adresGry(p.id) }, ikona("analityka"), el("span", null, "Pulpit gry")),
      zwarta ? null : el("a", { class: "przycisk maly", href: adresPomyslu(p.id) }, ikona("notatka"), el("span", null, "Karta pomysłu"))));
}
