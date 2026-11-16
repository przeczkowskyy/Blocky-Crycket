// Próba zakładki Assety „na żywo” (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_assety.py na serwerze testowym — nie ręcznie.
//
//   node testy/przegladarka_assety.mjs <port> <katalog danych lokalnych> <przeglądarka> [zrzuty]
//
// Serwer testowy działa w katalogu prawdziwego repozytorium, więc prawdziwego assets/manifest.json nie wolno tu
// zmieniać: GET /api/assety, strumień GET /api/assety/zdarzenia, /api/komentarze i /api/git/auto podmienia strona
// (fetch podstawiony przed startem aplikacji), a test steruje strumieniem z zewnątrz (window.__asPchnij, __asZerwij).
// Sprawdza: pierwsze otwarcie bez znaczków „nowe”, „Zaktualizowano HH:MM.”, nowa wersja ze strumienia = sam pobiera
// i przerysowuje (przewinięcie, fokus i szukanie zostają), znaczki „nowe” i licznik, pasek „Na GitHubie są nowsze
// zmiany”, obejrzenie w szczegółach, wyjście z zakładki = obejrzane, ponowne połączenie po zerwaniu.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 300) : ""));
};

// podmiana fetch przed startem aplikacji (funkcja zamieniana na tekst — bez ucieczek w napisie)
function podmiana() {
  const prawdziwy = window.fetch.bind(window);
  const as = { rejestr: null, wywolania: 0, polaczenia: 0, kontroler: null, gitAuto: null };
  window.__as = as;
  const json = (status, obj) => Promise.resolve(new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } }));
  window.__asPchnij = (obj) => {
    if (!as.kontroler) return false;
    as.kontroler.enqueue(new TextEncoder().encode("data: " + JSON.stringify(obj) + "\n\n"));
    return true;
  };
  window.__asZerwij = () => {
    const k = as.kontroler;
    as.kontroler = null;
    if (k) k.error(new TypeError("łącze zerwane (test)"));
    return !!k;
  };
  window.fetch = (url, init) => {
    const u = String((url && url.url) || url);
    const sciezka = u.replace(/^https?:\/\/[^/]+/, "").split("?")[0];
    if (sciezka === "/api/assety") {
      as.wywolania++;
      return json(200, as.rejestr || { zrodlo: "assets/manifest.json", wersja: "0", brak_manifestu: true, assety: [], liczniki: {}, etapy: [], statusy: [], czeka: 0 });
    }
    if (sciezka === "/api/assety/zdarzenia") {
      as.polaczenia++;
      let kontroler = null;
      const strumien = new ReadableStream({ start(k) { kontroler = k; as.kontroler = k; } });
      const sygnal = init && init.signal;
      if (sygnal) {
        sygnal.addEventListener("abort", () => {
          if (as.kontroler === kontroler) as.kontroler = null;
          try { kontroler.error(new DOMException("przerwane", "AbortError")); } catch (e) { /* już zamknięty */ }
        });
      }
      return Promise.resolve(new Response(strumien, { status: 200, headers: { "Content-Type": "text/event-stream" } }));
    }
    if (sciezka === "/api/komentarze") return json(200, { komentarze: [] });
    if (sciezka === "/api/git/auto") return json(200, as.gitAuto || { wlaczona: true, stan: "ok", do_pobrania: 0, pobranie: null });
    return prawdziwy(url, init);
  };
}
const PODMIANA = "(" + podmiana.toString() + ")();";

// rejestr testowy: dwie grafiki sali wyboru klasy, Teleport i 30 ikon (żeby strona się przewijała)
const ETAPY = [["generowanie", "Generowanie"], ["obrobka", "Obróbka"], ["figma", "Figma"], ["zgoda", "Zgoda człowieka"], ["roblox", "Roblox"]];
const teraz = new Date();
const HM = String(teraz.getHours()).padStart(2, "0") + ":" + String(teraz.getMinutes()).padStart(2, "0");
function asset(nazwa, wersja, kategoria = "background") {
  return { nazwa, kategoria, kategoria_opis: kategoria === "icon" ? "ikona" : "tło", status: "processed", status_opis: "obrobiony",
    status_wyjasnienie: "Obrobiony.", etap: 1, uzycie: "Sala wyboru klasy", notatki: "", obraz: null, miniatura: null, historia: [],
    czeka_na_zgode: false, cel_komentarzy: "assets/processed/" + nazwa + ".png", wersja };
}
function rejestr(wersja, assety) {
  return { zrodlo: "assets/manifest.json", wersja, zaktualizowano: teraz.toISOString(), na_dysku: teraz.toISOString(), assety,
    liczniki: { processed: assety.length }, czeka: 0,
    etapy: ETAPY.map(([id, nazwa], i) => ({ id, nazwa, skrot: nazwa, opis: nazwa, bramka: id === "zgoda" || undefined, liczba: i === 1 ? assety.length : 0 })),
    statusy: [{ id: "processed", nazwa: "obrobiony", etap: 1, opis: "", liczba: assety.length }] };
}
const ikony = (zmieniona) => Array.from({ length: 30 }, (_, i) => asset("Ikona" + String(i + 1).padStart(2, "0"), "i" + i + (zmieniona === i ? "b" : ""), "icon"));
const V1 = rejestr("v1", [asset("CsBg1", "c1"), asset("CsBg2", "c2"), asset("Teleport", "t1"), ...ikony()]);
const V2 = rejestr("v2", [asset("CsBg1", "c1-nowa"), asset("CsBg2", "c2"), asset("Teleport", "t1"), asset("CsBg5", "c5"), ...ikony()]);
const V3 = rejestr("v3", [asset("CsBg1", "c1-nowa"), asset("CsBg2", "c2"), asset("Teleport", "t1"), asset("CsBg5", "c5"), ...ikony(6)]);
const V4 = rejestr("v4", [asset("CsBg1", "c1-nowa"), asset("CsBg2", "c2"), asset("Teleport", "t1"), asset("CsBg5", "c5"), ...ikony(7)]);

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_assety_"));
const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--window-size=412,915", "about:blank"], { stdio: "ignore" });

let ws;
let nr = 0;
const oczek = new Map();
function wyslij(metoda, params = {}) {
  return new Promise((res, rej) => {
    const n = ++nr;
    oczek.set(n, { res, rej });
    ws.send(JSON.stringify({ id: n, method: metoda, params }));
  });
}
async function js(wyrazenie) {
  const r = await wyslij("Runtime.evaluate", { expression: wyrazenie, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error("JS: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
}
async function czekajNa(wyr, ms = 8000) {
  const koniec = Date.now() + ms;
  while (Date.now() < koniec) {
    if (await js(wyr)) return true;
    await sleep(150);
  }
  return false;
}
async function zrzut(nazwa) {
  if (!zrzuty) return;
  await sleep(300);
  const r = await wyslij("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
const ustawRejestr = (r) => js(`window.__as.rejestr = ${JSON.stringify(r)}; true`);
const pchnij = (z) => js(`window.__asPchnij(${JSON.stringify(z)})`);
const kart = () => js(`document.querySelectorAll('.as-siatka .as-karta').length`);
const nowych = () => js(`[...document.querySelectorAll('.as-siatka .as-karta.nowy')].map(k => k.querySelector('.as-nazwa').textContent).sort().join(',')`);
const bledyStrony = [];

try {
  let adres = null;
  for (let i = 0; i < 75 && !adres; i++) {
    try {
      const lista = await (await fetch("http://127.0.0.1:" + portDT + "/json/list")).json();
      adres = (lista.find((x) => x.type === "page") || {}).webSocketDebuggerUrl || null;
    } catch (e) { /* przeglądarka jeszcze wstaje */ }
    if (!adres) await sleep(200);
  }
  if (!adres) throw new Error("przeglądarka nie wystartowała");
  ws = new WebSocket(adres);
  await new Promise((r, j) => { ws.addEventListener("open", r); ws.addEventListener("error", j); });
  ws.addEventListener("message", (m) => {
    const d = JSON.parse(m.data);
    if (d.id && oczek.has(d.id)) {
      const o = oczek.get(d.id);
      oczek.delete(d.id);
      if (d.error) o.rej(new Error(JSON.stringify(d.error)));
      else o.res(d.result);
    } else if (d.method === "Runtime.exceptionThrown") {
      bledyStrony.push(JSON.stringify(d.params.exceptionDetails).slice(0, 300));
    }
  });
  await wyslij("Page.enable");
  await wyslij("Runtime.enable");
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await wyslij("Page.addScriptToEvaluateOnNewDocument", { source: PODMIANA });
  await wyslij("Page.navigate", { url: PANEL + "/?l=" + encodeURIComponent(klucz) });
  await sleep(1500);
  await js(`localStorage.setItem('bc.kto', 'Karol'); localStorage.removeItem('bc.assety.widziane'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(1200);

  // 1. pierwsze otwarcie: strumień, „Zaktualizowano HH:MM.”, bez znaczków „nowe”
  await ustawRejestr(V1);
  await js(`location.hash = '#/assety'; true`);
  sprawdz("1. siatka 33 kart", await czekajNa(`document.querySelectorAll('.as-siatka .as-karta').length === 33`, 12000), await kart());
  sprawdz("1. strumień zdarzeń połączony", await czekajNa(`window.__as.polaczenia >= 1 && !!window.__as.kontroler`));
  sprawdz("1. „Zaktualizowano " + HM + ".”", await js(`(document.querySelector('.as-aktualizacja') || {}).textContent === ${JSON.stringify("Zaktualizowano " + HM + ".")}`),
    await js(`(document.querySelector('.as-aktualizacja') || {}).textContent`));
  await pchnij({ typ: "assety", wersja: "v1", git: null });
  await sleep(400);
  sprawdz("1. ta sama wersja — bez ponownego pobrania", await js(`window.__as.wywolania === 1`), await js(`window.__as.wywolania`));
  sprawdz("1. pierwsze otwarcie bez znaczków „nowe”", (await nowych()) === "" && await js(`!document.querySelector('.as-nowe')`));
  sprawdz("1. obejrzane zapamiętane w localStorage", await js(`(() => { const v = JSON.parse(localStorage.getItem('bc.assety.widziane') || 'null'); return !!v && v.assety.CsBg1 === 'c1' && Object.keys(v.assety).length === 33; })()`));
  sprawdz("1. bez paska GitHuba", await js(`document.querySelector('.as-sync').hidden`));
  await zrzut("assety_1_start");

  // 2. nowa wersja ze strumienia: sam pobiera, znaczki na nowej i zmienionej grafice, przewinięcie zostaje
  await js(`window.scrollTo(0, 1500); true`);
  await sleep(300);
  const y0 = await js(`window.scrollY`);
  await ustawRejestr(V2);
  await pchnij({ typ: "assety", wersja: "v2", git: null });
  sprawdz("2. sam pobrał nowy rejestr (34 karty)", await czekajNa(`document.querySelectorAll('.as-siatka .as-karta').length === 34`), await kart());
  sprawdz("2. znaczki „nowe”: CsBg1 (zmieniona) i CsBg5 (nowa)", (await nowych()) === "CsBg1,CsBg5", await nowych());
  sprawdz("2. licznik „2 nowe” w podsumowaniu", await js(`(document.querySelector('.as-nowe-pokaz') || {}).textContent === '2nowe'`),
    await js(`(document.querySelector('.as-nowe-pokaz') || {}).textContent`));
  const y1 = await js(`window.scrollY`);
  sprawdz("2. przewinięcie zostało (" + y0 + " px)", y0 > 0 && Math.abs(y1 - y0) <= 2, "przed " + y0 + ", po " + y1);
  sprawdz("2. karta nowa ma opis dla czytnika", await js(`document.querySelector('[data-klucz="karta:CsBg5"]').getAttribute('aria-label').includes('nowe od ostatniego obejrzenia')`));

  // 3. fokus na karcie wraca po przerysowaniu
  await js(`document.querySelector('[data-klucz="karta:Teleport"]').focus({ preventScroll: true }); true`);
  await ustawRejestr(V3);
  await pchnij({ typ: "assety", wersja: "v3", git: null });
  await czekajNa(`window.__as.wywolania >= 3`);
  sprawdz("3. przerysowane (Ikona07 nowa)", await czekajNa(`!!document.querySelector('.as-karta.nowy [data-klucz="karta:Ikona07"], .as-karta.nowy')
    && [...document.querySelectorAll('.as-karta.nowy .as-nazwa')].some(n => n.textContent === 'Ikona07')`), await nowych());
  sprawdz("3. fokus nadal na karcie Teleport", await js(`(document.activeElement && document.activeElement.dataset.klucz) === 'karta:Teleport'`),
    await js(`document.activeElement && (document.activeElement.dataset.klucz || document.activeElement.tagName)`));

  // 4. szukanie zostaje przy odświeżeniu w tle
  await js(`window.scrollTo(0, 0); const p = document.querySelector('.as-szukaj input'); p.value = 'Cs'; p.dispatchEvent(new Event('input', { bubbles: true })); true`);
  sprawdz("4. szukanie „Cs” — 3 karty", await czekajNa(`document.querySelectorAll('.as-siatka .as-karta').length === 3`), await kart());
  await ustawRejestr(V4);
  await pchnij({ typ: "assety", wersja: "v4", git: null });
  await czekajNa(`window.__as.wywolania >= 4`);
  await sleep(300);
  sprawdz("4. po odświeżeniu dalej 3 karty i „Cs” w polu", (await kart()) === 3 && await js(`document.querySelector('.as-szukaj input').value === 'Cs'`), await kart());

  // 5. pasek „Na GitHubie są nowsze zmiany”
  await pchnij({ typ: "assety", wersja: "v4", git: { ile: 2, assety: true, od: teraz.toISOString(), stan: "czeka", krotko: "lokalne zmiany w 1 pliku" } });
  sprawdz("5. pasek widoczny", await czekajNa(`!document.querySelector('.as-sync').hidden`));
  const pasek = await js(`document.querySelector('.as-sync').textContent`);
  sprawdz("5. treść paska", pasek.includes("Na GitHubie są nowsze zmiany (2), także w rejestrze grafik") && pasek.includes("lokalne zmiany w 1 pliku"), pasek);
  sprawdz("5. pasek ma rolę status", await js(`document.querySelector('.as-sync').getAttribute('role') === 'status'`));
  await zrzut("assety_5_pasek");
  await pchnij({ typ: "assety", wersja: "v4", git: null });
  sprawdz("5. po pobraniu pasek znika", await czekajNa(`document.querySelector('.as-sync').hidden`));
  sprawdz("5. stan gita bez ponownego pobierania rejestru", await js(`window.__as.wywolania === 4`), await js(`window.__as.wywolania`));

  // 6. szczegóły nowej grafiki = obejrzana; druga zostaje „nowa”
  await js(`document.querySelector('[data-klucz="karta:CsBg5"]').click(); true`);
  sprawdz("6. arkusz szczegółów otwarty", await czekajNa(`!!document.querySelector('.arkusz')`));
  await sleep(300);
  await js(`document.querySelector('.arkusz [aria-label="Zamknij"]').click(); true`);
  await sleep(500);
  sprawdz("6. CsBg5 obejrzana, CsBg1 dalej nowa", (await nowych()) === "CsBg1", await nowych());
  sprawdz("6. fokus wrócił na kartę CsBg5", await js(`(document.activeElement && document.activeElement.dataset.klucz) === 'karta:CsBg5'`),
    await js(`document.activeElement && (document.activeElement.dataset.klucz || document.activeElement.tagName)`));

  // 7. wyjście z zakładki = wszystko obejrzane; powrót = nowe połączenie
  const polPrzed = await js(`window.__as.polaczenia`);
  await js(`location.hash = '#/pulpit'; true`);
  sprawdz("7. po wyjściu strumień zamknięty", await czekajNa(`!window.__as.kontroler`));
  await js(`location.hash = '#/assety'; true`);
  sprawdz("7. po powrocie nowe połączenie", await czekajNa(`window.__as.polaczenia > ${polPrzed} && !!window.__as.kontroler`));
  await sleep(500);
  sprawdz("7. bez znaczków „nowe” po powrocie", (await nowych()) === "", await nowych());

  // 8. zerwane łącze: ponowne połączenie (po ok. 5 s)
  const pol = await js(`window.__as.polaczenia`);
  await js(`window.__asZerwij()`);
  sprawdz("8. po zerwaniu łączy się znowu", await czekajNa(`window.__as.polaczenia > ${pol} && !!window.__as.kontroler`, 12000));
  sprawdz("8. bez błędów JS na stronie", !bledyStrony.length, bledyStrony.join(" | "));
} catch (e) {
  sprawdz("przebieg testu", false, e && e.stack);
} finally {
  try {
    ws && ws.close();
  } catch (e) { /* nic */ }
  proc.kill();
  await sleep(500);
  try {
    fs.rmSync(profil, { recursive: true, force: true });
  } catch (e) { /* przeglądarka trzyma pliki */ }
}
console.log(bledy ? "WYNIK: " + bledy + " BŁĘDÓW" : "WYNIK: wszystko OK");
process.exit(bledy ? 1 : 0);
