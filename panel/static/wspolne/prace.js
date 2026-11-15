// Prace w toku (GET /api/prace, bc/prace.py): wspólne pobieranie i napisy dla Pulpitu, plakietki w powłoce i znaczków
// przy pozycjach w zakładkach Pytania i Sesja.
//
//   pobierzPrace(ctx, {wymus?}) → Promise<{prace, teraz, w_toku, najblizszy_koniec} | null>
//       null = serwer nie zna prac (stary serwer, lustro, moduł wyłączony) — wtedy nic nowego się nie pokazuje.
//       Pyta serwer tylko, gdy /api/zdrowie wymienia moduł „prace” (ctx.znaModul), więc stary serwer nie dostaje
//       żadnego żądania (bez 404 w konsoli). Wynik pamiętany 10 s; nowa treść = zdarzenie „bc:prace” na window.
//   ostatniePrace() → ostatni wynik albo null
//   teraz() → czas serwera w ms (poprawka o różnicę zegarów telefonu i komputera)
//   napisKonca(p) → {tekst, klasa}   „koniec ok. 12:40 (za 35 min)”, „po czasie o 10 min”, „gotowe 11:52”…
//   kluczPozycji(p) → klucz karty w zakładce Pytania („raport-<id>”, „pytanie-19”, „D-071”) albo null
//   znaczekPracy(p, {tytulRaportu?, naRaport?}) → <span class="praca-znaczek"> albo null

import { el, ikona, dataKrotka } from "./ui.js";

const PAMIEC_MS = 10000;
const PRZERWA_PO_BLEDZIE_MS = 5 * 60000;

const stan = { dane: null, czas: 0, roznica: 0, obietnica: null, przerwaDo: 0, podpis: "" };

/** Czy serwer ma moduł prac (znany z /api/zdrowie). Lustro i stary serwer — nie. */
export function obslugiwane(ctx) {
  if (!ctx || ctx.statyczny) return false;
  return typeof ctx.znaModul === "function" && ctx.znaModul("prace");
}

export function ostatniePrace() {
  return stan.dane;
}

export function teraz() {
  return Date.now() + stan.roznica;
}

export async function pobierzPrace(ctx, o = {}) {
  if (!obslugiwane(ctx) || Date.now() < stan.przerwaDo) return null;
  if (!o.wymus && stan.dane && Date.now() - stan.czas < PAMIEC_MS) return stan.dane;
  if (stan.obietnica) return stan.obietnica;
  stan.obietnica = (async () => {
    try {
      const d = await ctx.api("/api/prace", { czas: 10000 });
      if (!d || !Array.isArray(d.prace)) return stan.dane;
      stan.czas = Date.now();
      const t = Date.parse(d.teraz);
      stan.roznica = isFinite(t) ? t - Date.now() : 0;
      stan.dane = d;
      const podpis = JSON.stringify(d.prace);
      if (podpis !== stan.podpis) {
        stan.podpis = podpis;
        window.dispatchEvent(new CustomEvent("bc:prace", { detail: d }));
      }
      return d;
    } catch (e) {
      if (e && (e.status === 404 || e.status === 405)) {        // serwer nie zna trasy: spróbuj znów za 5 min
        stan.przerwaDo = Date.now() + PRZERWA_PO_BLEDZIE_MS;
        stan.dane = null;
      }
      return stan.dane;
    } finally {
      stan.obietnica = null;
    }
  })();
  return stan.obietnica;
}

// ------------------------------------------------------------------ napisy
const pad = (n) => String(n).padStart(2, "0");

/** „12:40” dziś, „jutro 12:40”, „16 lis, 12:40” innego dnia. */
export function godzina(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const hm = d.getHours() + ":" + pad(d.getMinutes());
  const dzis = new Date(teraz());
  const jutro = new Date(dzis.getTime() + 86400000);
  if (d.toDateString() === dzis.toDateString()) return hm;
  if (d.toDateString() === jutro.toDateString()) return "jutro " + hm;
  return dataKrotka(iso);
}

/** 35 → „35 min”, 80 → „1 h 20 min”, 120 → „2 h”, 1600 → „1 d 2 h”. */
export function ileCzasu(minuty) {
  const m = Math.max(0, Math.round(Number(minuty) || 0));
  if (m < 60) return m + " min";
  if (m < 1440) return Math.floor(m / 60) + " h" + (m % 60 ? " " + (m % 60) + " min" : "");
  const h = Math.floor((m % 1440) / 60);
  return Math.floor(m / 1440) + " d" + (h ? " " + h + " h" : "");
}

/** Minuty do szacowanego końca liczone teraz (ujemne = po czasie) albo null. */
export function minutyDoKonca(p) {
  const k = Date.parse(p && p.koniec_szacowany);
  if (!isFinite(k)) return null;
  const s = (k - teraz()) / 1000;
  return s >= 0 ? Math.ceil(s / 60) : -Math.floor(-s / 60);
}

export function poCzasie(p) {
  if (!p || p.stan !== "w_toku") return false;
  const m = minutyDoKonca(p);
  return m === null ? !!p.przeterminowana : (m < 0 || (m === 0 && Date.parse(p.koniec_szacowany) < teraz()));
}

/** Postęp 0–1 liczony teraz (z czasu albo z serwera) albo null. */
export function postep(p) {
  if (!p) return null;
  if (p.stan === "gotowe") return 1;
  const s = Date.parse(p.start);
  const k = Date.parse(p.koniec_szacowany);
  if (isFinite(s) && isFinite(k) && k > s) return Math.max(0, Math.min(0.99, (teraz() - s) / (k - s)));
  const v = Number(p.postep);
  return p.postep === null || p.postep === undefined || !isFinite(v) ? null : Math.max(0, Math.min(1, v));
}

/** Etap z numerem: „Kontrola (3 z 5)”. */
export function etapPracy(p) {
  const etapy = Array.isArray(p.etapy) ? p.etapy : [];
  const n = Number(p.numer) || 0;
  const nazwa = p.etap || (n && etapy[n - 1]) || "";
  return etapy.length && n ? (nazwa ? nazwa + " " : "") + "(" + n + " z " + etapy.length + ")" : nazwa;
}

export function napisKonca(p) {
  if (p.stan === "gotowe") return { tekst: "gotowe " + godzina(p.zakonczono || p.aktualizacja), klasa: "gotowe" };
  if (p.stan === "blad") return { tekst: "przerwana " + godzina(p.zakonczono || p.aktualizacja), klasa: "blad" };
  if (p.stan === "wstrzymane") return { tekst: "wstrzymana", klasa: "wstrzymane" };
  if (!p.koniec_szacowany) return { tekst: "bez szacowanego końca", klasa: "" };
  const m = minutyDoKonca(p);
  if (poCzasie(p)) return { tekst: "po czasie o " + ileCzasu(Math.max(0, -m)), klasa: "po-czasie" };
  return { tekst: "koniec ok. " + godzina(p.koniec_szacowany) + " (za " + ileCzasu(m) + ")", klasa: "" };
}

/** Klucz karty w zakładce Pytania (wspolne/kolejka.js), której dotyczy praca. */
export function kluczPozycji(p) {
  const d = p && p.dotyczy;
  if (!d || typeof d !== "object" || !d.id) return null;
  if (d.typ === "raport") return "raport-" + d.id;
  if (d.typ === "pytanie") return "pytanie-" + Number(d.id);
  if (d.typ === "decyzja") {
    const m = /^D-?(\d{1,4})$/i.exec(String(d.id));
    return m ? "D-" + String(Number(m[1])).padStart(3, "0") : null;
  }
  return null;
}

/** Mały znaczek przy karcie: „w pracy — koniec ok. 12:40”, „w pracy — po czasie o 10 min”, „praca wstrzymana”,
 * „praca przerwana”, po końcu z raportem „poprawione — zobacz raport „…”” (klik = raport). Bez raportu po końcu — null. */
export function znaczekPracy(p, o = {}) {
  if (!p) return null;
  let tekst;
  let klasa = "";
  if (p.stan === "w_toku") {
    const n = napisKonca(p);
    tekst = poCzasie(p) ? "w pracy — " + n.tekst : p.koniec_szacowany ? "w pracy — koniec ok. " + godzina(p.koniec_szacowany) : "w pracy";
    klasa = n.klasa;
  } else if (p.stan === "wstrzymane") {
    tekst = "praca wstrzymana";
    klasa = "wstrzymane";
  } else if (p.stan === "blad") {
    tekst = "praca przerwana";
    klasa = "blad";
  } else if (p.stan === "gotowe" && p.raport) {
    const t = o.tytulRaportu ? o.tytulRaportu(p.raport) : "";
    tekst = "poprawione — zobacz raport" + (t ? " „" + t + "”" : "");
    klasa = "gotowe";
  } else return null;
  const tytul = p.tytul + (etapPracy(p) ? " · " + etapPracy(p) : "") + (p.komunikat ? " · " + p.komunikat : "");
  const tresc = [ikona(p.stan === "gotowe" ? "ok" : "zegar"), el("span", null, tekst)];
  const e = p.stan === "gotowe" && typeof o.naRaport === "function"
    ? el("button", { type: "button", class: "praca-znaczek klik " + klasa, title: tytul, onclick: () => o.naRaport(p.raport) }, tresc)
    : el("span", { class: "praca-znaczek " + klasa, title: tytul }, tresc);
  e.dataset.tekst = tekst + "|" + klasa;
  return e;
}

/** Mapa klucz karty → praca (pierwsza na liście wygrywa: w toku przed wstrzymaną i gotową). */
export function pracePoKluczu(dane) {
  const m = new Map();
  for (const p of (dane && dane.prace) || []) {
    const k = kluczPozycji(p);
    if (k && !m.has(k)) m.set(k, p);
  }
  return m;
}
