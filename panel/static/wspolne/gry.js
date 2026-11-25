// Gry studia — pulpit per gra (25.11.2026, Karol: „Chcę, żeby dashboard był per gra robiony”).
//
// Rejestr gier przychodzi z GET /api/konfiguracja (pole `gry`: {lista:[{id, nazwa, stan, wspolne}], domyslna, aktywna};
// bc/gry.py). Każde pytanie, decyzja, zadanie i raport ma od serwera pole `gra`. Panel pokazuje jedną grę naraz:
//   - na start grę `aktywna` z rejestru; wybór osoby pamięta przeglądarka (localStorage „bc.gra”), a adres
//     `?gra=<id>` albo `?gra=wszystkie` (przed #) go ustawia;
//   - sprawy gry „wspólnej” (`wspolne: true` — panel, sesje główne, proces zespołu) widać pod każdą grą;
//   - „Wszystkie gry” = bez filtra, przy każdej sprawie mała etykieta gry.
// Bez rejestru (stary serwer, brak klucza „gry”) nic się nie filtruje i przełącznika nie ma — panel jak dawniej.
// Zmiana gry = zdarzenie „bc:gra” (widoki przerysowują listy), nowe liczby spraw w grach = „bc:gry-liczby”.

import { el } from "./ui.js";

export const WSZYSTKIE = "wszystkie";
const KLUCZ_LS = "bc.gra";

let rejestr = null;
let wybor = null;
let liczby = {};

function czytajLS() {
  try {
    return localStorage.getItem(KLUCZ_LS);
  } catch (e) {
    return null;
  }
}
function zapiszLS(v) {
  try {
    localStorage.setItem(KLUCZ_LS, v);
  } catch (e) { /* tryb prywatny — wybór działa do zamknięcia karty */ }
}

function poprawnyWybor(id) {
  return id === WSZYSTKIE || !!(rejestr && rejestr.lista.some((g) => g.id === id && !g.wspolne));
}

/** Rejestr z /api/konfiguracja (albo null). Wybór: parametr adresu ?gra=, potem localStorage, potem `aktywna`. */
export function ustawRejestr(r) {
  const lista = r && Array.isArray(r.lista) ? r.lista.filter((g) => g && typeof g.id === "string") : [];
  if (!lista.some((g) => !g.wspolne)) {
    rejestr = null;
    wybor = null;
    return null;
  }
  rejestr = {
    lista: lista.map((g) => ({ id: g.id, nazwa: String(g.nazwa || g.id), stan: g.stan === "wstrzymana" ? "wstrzymana" : "aktywna", wspolne: !!g.wspolne })),
    domyslna: r.domyslna, aktywna: r.aktywna,
  };
  if (!poprawnyWybor(rejestr.domyslna)) rejestr.domyslna = rejestr.lista.find((g) => !g.wspolne).id;
  if (!poprawnyWybor(rejestr.aktywna)) rejestr.aktywna = rejestr.domyslna;
  let zAdresu = null;
  try {
    const u = new URL(location.href);
    zAdresu = u.searchParams.get("gra");
    if (zAdresu !== null) {                                    // adres ustawia wybór i znika z paska (zostaje w pamięci)
      u.searchParams.delete("gra");
      history.replaceState(history.state, "", u.pathname + (u.search || "") + u.hash);
    }
  } catch (e) { /* stara przeglądarka */ }
  const zLS = czytajLS();
  if (zAdresu !== null && poprawnyWybor(zAdresu)) {
    wybor = zAdresu;
    zapiszLS(wybor);
  } else if (zLS && poprawnyWybor(zLS)) wybor = zLS;
  else wybor = rejestr.aktywna;
  return rejestr;
}

/** Czy panel ma rejestr gier (jest przełącznik i filtr). */
export function maRejestr() {
  return !!rejestr;
}

/** Gry do przełącznika (bez „wspólnej”). */
export function listaGier() {
  return rejestr ? rejestr.lista.filter((g) => !g.wspolne) : [];
}

export function gra(id) {
  return (rejestr && rejestr.lista.find((g) => g.id === id)) || null;
}

export function domyslna() {
  return rejestr ? rejestr.domyslna : null;
}

/** Wybrana gra: id albo WSZYSTKIE (bez rejestru zawsze WSZYSTKIE — bez filtra). */
export function wybranaGra() {
  return rejestr ? wybor : WSZYSTKIE;
}

/** Czy panel pokazuje wszystkie gry naraz (wtedy sprawy mają etykietę gry). */
export function wszystkieGry() {
  return !!rejestr && wybor === WSZYSTKIE;
}

export function wybierzGre(id) {
  if (!rejestr || !poprawnyWybor(id) || id === wybor) return false;
  wybor = id;
  zapiszLS(id);
  window.dispatchEvent(new CustomEvent("bc:gra", { detail: id }));
  return true;
}

/** Gra sprawy (pytania, decyzji, zadania, raportu): pole `gra` z serwera albo gra domyślna. */
export function graSprawy(o) {
  if (!rejestr) return null;
  const g = o && o.gra;
  return gra(g) ? g : rejestr.domyslna;
}

export function jestWspolna(id) {
  const g = gra(id);
  return !!(g && g.wspolne);
}

/** Czy sprawa jest w wybranej grze (wspólne — w każdej). */
export function wGrze(o, wybrana) {
  const w = wybrana === undefined ? wybranaGra() : wybrana;
  if (!rejestr || w === WSZYSTKIE) return true;
  const g = graSprawy(o);
  return g === w || jestWspolna(g);
}

function wyrazy(t) {
  return String(t || "").toLowerCase().replace(/ł/g, "l").normalize("NFD").replace(/[\u0300-\u036f]/g, "").match(/[0-9a-z]+/g) || [];
}

/** Id gry z wartości znacznika „Gra: …” (id albo nazwa z rejestru, jak bc/gry.py: rozpoznaj) albo null. */
export function rozpoznajGre(wartosc) {
  if (!rejestr) return null;
  const w = wyrazy(wartosc).join(" ");
  if (!w) return null;
  for (const g of rejestr.lista) if (w === wyrazy(g.id).join(" ") || w === wyrazy(g.nazwa).join(" ")) return g.id;
  const czesci = w.split(" ");
  for (let k = czesci.length - 1; k > 0; k--) {
    const poczatek = czesci.slice(0, k).join(" ");
    const g = rejestr.lista.find((x) => wyrazy(x.id).join(" ") === poczatek);
    if (g) return g.id;
  }
  return null;
}

export function nazwaGry(id) {
  if (id === WSZYSTKIE) return "Wszystkie gry";
  const g = gra(id);
  return g ? g.nazwa : String(id || "");
}

/** Mała etykieta gry przy sprawie — tylko w widoku „Wszystkie gry” (inaczej null). */
export function etykietaGry(o) {
  if (!wszystkieGry()) return null;
  const id = graSprawy(o);
  const g = gra(id);
  return el("span", { class: "chip-gry" + (g && g.stan === "wstrzymana" ? " wstrzymana" : "") + (g && g.wspolne ? " wspolna" : ""),
    title: "Gra: " + nazwaGry(id) + (g && g.stan === "wstrzymana" ? " (wstrzymana)" : "") }, nazwaGry(id));
}

/** Liczby spraw czekających na ludzi w każdej grze ({id: n}; wspólne pod własnym id) — z ostatniej listy
 * (wspolne/kolejka.js). Zmiana = zdarzenie „bc:gry-liczby” (przełącznik w powłoce). */
export function zapamietajLiczby(m) {
  const nowe = Object.assign({}, m || {});
  if (JSON.stringify(nowe) === JSON.stringify(liczby)) return;
  liczby = nowe;
  window.dispatchEvent(new CustomEvent("bc:gry-liczby", { detail: nowe }));
}

export function liczbyGier() {
  return liczby;
}

/** Ile spraw czeka poza wybraną grą (bez wspólnych — te i tak widać). */
export function czekaGdzieIndziej() {
  if (!rejestr || wybor === WSZYSTKIE) return 0;
  return listaGier().filter((g) => g.id !== wybor).reduce((s, g) => s + (liczby[g.id] || 0), 0);
}
