// Rozmowa z serwerem panelu: api(), apiSurowe(), sse() oraz tryb statyczny (lustro tylko do odczytu).
//
// Tryb statyczny: eksporter (bc/statyczny.py) zapisuje odpowiedzi GET jako pliki dane/<klucz>.json, gdzie
// klucz(ścieżka z zapytaniem) = 8 znaków hex FNV-1a 32-bit + 8 znaków hex djb2 32-bit, liczone po bajtach UTF-8.
// Kluczem jest dokładnie ten napis, który widok podaje do api(), np. "/api/sejf/plan" albo "/api/komentarze?typ=raport&cel=X".

export const STATYCZNY = typeof window !== "undefined" && window.BC_STATYCZNY === true;

const KOMUNIKAT_RO = "Podgląd tylko do odczytu — tu nie da się nic zmienić.";

/** Klucz pliku w trybie statycznym: FNV-1a 32-bit (hex 8) + djb2 32-bit (hex 8), po bajtach UTF-8. */
export function klucz(tekst) {
  const bajty = new TextEncoder().encode(String(tekst));
  let f = 0x811c9dc5;
  let d = 5381;
  for (let i = 0; i < bajty.length; i++) {
    const b = bajty[i];
    f = Math.imul(f ^ b, 0x01000193) >>> 0;
    d = (Math.imul(d, 33) + b) >>> 0;
  }
  return f.toString(16).padStart(8, "0") + d.toString(16).padStart(8, "0");
}

function imie() {
  try {
    return localStorage.getItem("bc.kto") || "";
  } catch (e) {
    return "";
  }
}

function naglowki(post, mime) {
  const h = {};
  const kto = imie();
  if (kto) h["X-BC-Kto"] = encodeURIComponent(kto);
  if (post) {
    h["X-BC"] = "1";
    if (mime) h["Content-Type"] = mime;
  }
  return h;
}

function komunikatStatusu(status) {
  if (status === 404) return "Tej części panelu jeszcze nie ma (404).";
  if (status === 403) return "Brak uprawnień do tej operacji.";
  if (status === 409) return "Ktoś albo coś już to robi — spróbuj za chwilę.";
  if (status === 413) return "Plik jest za duży.";
  if (status >= 500) return "Błąd serwera panelu (" + status + ").";
  return "Nie udało się (" + status + ").";
}

function blad(komunikat, status, dane) {
  const e = new Error(komunikat);
  e.status = status;
  e.dane = dane || null;
  return e;
}

let przekierowano = false;
function przekierujDoKodu() {
  if (przekierowano) return;
  przekierowano = true;
  try {
    window.location.href = "/";
  } catch (e) { /* nic */ }
}

async function odpowiedz(r) {
  let dane = null;
  if (r.status !== 204) {
    const tekst = await r.text();
    if (tekst) {
      try {
        dane = JSON.parse(tekst);
      } catch (e) {
        dane = r.ok ? tekst : null;
      }
    }
  }
  if (!r.ok) {
    if (r.status === 401 && dane && dane.kod === "brak_dostepu" && !STATYCZNY) przekierujDoKodu();
    throw blad((dane && typeof dane === "object" && dane.blad) || komunikatStatusu(r.status), r.status, dane);
  }
  return dane;
}

async function pobierz(url, init, czasMs) {
  const ctrl = new AbortController();
  const zegar = czasMs ? setTimeout(() => ctrl.abort(), czasMs) : null;
  try {
    return await fetch(url, Object.assign({ cache: "no-store", credentials: "same-origin", signal: ctrl.signal }, init));
  } catch (e) {
    if (e && e.name === "AbortError") throw blad("Serwer panelu nie odpowiada (przekroczony czas).", 0);
    throw blad("Brak połączenia z panelem. Czy serwer działa?", 0);
  } finally {
    if (zegar) clearTimeout(zegar);
  }
}

/**
 * api(sciezka, {metoda?, cialo?, czas?, keepalive?}) → Promise<obiekt>.
 * Rzuca Error z polami .status (0 = brak połączenia) i .message (pole `blad` z serwera albo opis po polsku).
 * keepalive: true — żądanie dokończy się także po zamknięciu karty (np. odhaczenie przy blokadzie ekranu telefonu).
 */
export async function api(sciezka, opcje = {}) {
  const metoda = (opcje.metoda || "GET").toUpperCase();
  if (STATYCZNY) {
    if (metoda !== "GET") throw blad(KOMUNIKAT_RO, 403, { statyczny: true });
    const r = await pobierz("dane/" + klucz(sciezka) + ".json", { headers: {} }, opcje.czas || 20000);
    if (r.status === 404) throw blad("Tych danych nie ma w podglądzie tylko do odczytu.", 404);
    return odpowiedz(r);
  }
  const init = { method: metoda, headers: naglowki(metoda !== "GET") };
  if (opcje.keepalive) init.keepalive = true;
  if (metoda !== "GET" && metoda !== "HEAD") {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(opcje.cialo === undefined ? {} : opcje.cialo);
  }
  const r = await pobierz(sciezka, init, opcje.czas === undefined ? 30000 : opcje.czas);
  return odpowiedz(r);
}

/** apiSurowe(sciezka, blob, mime) → Promise<obiekt>: POST surowych bajtów (np. nagrania audio). */
export async function apiSurowe(sciezka, blob, mime) {
  if (STATYCZNY) throw blad(KOMUNIKAT_RO, 403, { statyczny: true });
  const typ = mime || (blob && blob.type) || "application/octet-stream";
  const r = await pobierz(sciezka, { method: "POST", headers: naglowki(true, typ), body: blob }, 120000);
  return odpowiedz(r);
}

/**
 * sse(sciezka, naZdarzenie, {naKoniec?}) → {zamknij()}.
 * Strumień Server-Sent Events przez fetch (bez automatycznego ponawiania — o tym decyduje widok).
 * naKoniec(blad|null) wywoływane raz, gdy serwer zamknie strumień albo połączenie padnie (nie po zamknij()).
 */
export function sse(sciezka, naZdarzenie, opcje = {}) {
  let zamkniety = false;
  const ctrl = new AbortController();
  const koniec = (b) => {
    if (zamkniety) return;
    zamkniety = true;
    if (typeof opcje.naKoniec === "function") {
      try {
        opcje.naKoniec(b || null);
      } catch (e) { /* nic */ }
    }
  };
  if (STATYCZNY) {
    setTimeout(() => koniec(blad(KOMUNIKAT_RO, 403, { statyczny: true })), 0);
    return { zamknij() { zamkniety = true; } };
  }
  (async () => {
    try {
      let r;
      try {
        r = await fetch(sciezka, {
          headers: Object.assign({ Accept: "text/event-stream" }, naglowki(false)),
          cache: "no-store", credentials: "same-origin", signal: ctrl.signal,
        });
      } catch (e) {
        throw blad("Brak połączenia z panelem.", 0);
      }
      if (!r.ok) await odpowiedz(r);
      if (!r.body || !r.body.getReader) throw blad("Ta przeglądarka nie obsługuje strumienia.", 0);
      const czytnik = r.body.getReader();
      const dekoder = new TextDecoder();
      let bufor = "";
      for (;;) {
        const { value, done } = await czytnik.read();
        if (done) break;
        bufor += dekoder.decode(value, { stream: true }).replace(/\r\n?/g, "\n");
        let idx;
        while ((idx = bufor.indexOf("\n\n")) >= 0) {
          const blok = bufor.slice(0, idx);
          bufor = bufor.slice(idx + 2);
          const dane = blok.split("\n").filter((l) => l.startsWith("data:")).map((l) => l.slice(5).replace(/^ /, "")).join("\n");
          if (!dane || zamkniety) continue;
          let obj;
          try {
            obj = JSON.parse(dane);
          } catch (e) {
            continue;
          }
          try {
            naZdarzenie(obj);
          } catch (e) {
            console.warn("sse: błąd obsługi zdarzenia", e);
          }
        }
      }
      koniec(null);
    } catch (e) {
      if (zamkniety || (e && e.name === "AbortError")) return;
      koniec(e);
    }
  })();
  return {
    zamknij() {
      zamkniety = true;
      try {
        ctrl.abort();
      } catch (e) { /* nic */ }
    },
  };
}

/**
 * Adres pliku binarnego (zrzut, obraz migawki) do użycia w <img src>.
 * Tryb normalny: ta sama ścieżka API. Tryb statyczny: ścieżka względna (eksporter kopiuje pliki pod tę samą ścieżkę).
 */
export function plik(sciezka) {
  if (!sciezka) return "";
  return STATYCZNY ? String(sciezka).replace(/^\/+/, "") : sciezka;
}

/** Bezpieczne kodowanie fragmentu ścieżki (id, nazwa pliku). */
export function enc(s) {
  return encodeURIComponent(String(s == null ? "" : s));
}
