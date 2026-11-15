// Próba „Prac w toku” w przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_prace.py na serwerze testowym — nie ręcznie.
//
//   node testy/przegladarka_prace.mjs <port> <katalog danych lokalnych> <przeglądarka> <raporty JSON> [zrzuty]
//
// Prace leżą w <katalog danych lokalnych>/prace (przygotował je test). Kroki:
//   1. Pulpit (telefon 412 px): karta „Prace w toku” nad „Czeka na Ciebie” — praca po czasie, praca w toku z etapem
//      i szacowanym końcem, paski postępu, zwinięte „Zakończone dziś (1)” z linkiem do raportu; plakietka w górnym
//      pasku; bez przewijania w bok;
//   2. zakładka Pytania: znaczek „w pracy — koniec ok. HH:MM” przy raporcie, „poprawione — zobacz raport „…”” przy
//      raporcie odesłanym do poprawy (historia), bez znaczka przy raporcie z wynikiem; zakładka Sesja: ten sam znaczek;
//   3. pusta lista prac: brak karty i plakietki;
//   4. stary serwer (/api/zdrowie bez modułu „prace”, podstawiony w stronie): brak karty, plakietki i znaczków,
//      żadnego żądania /api/prace i żadnego błędu w konsoli;
//   5. restart panelu przy otwartej stronie (stary → nowy serwer, inny pid): karta i plakietka pojawiają się same.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, przegladarka, raportyJson, zrzuty] = process.argv.slice(2);
const R = JSON.parse(raportyJson);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const katPrac = path.join(runtime, "prace");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 300) : ""));
};

// podmiana fetch przed startem aplikacji: liczy żądania /api/prace; w trybie „stary serwer” (sessionStorage)
// /api/zdrowie traci moduł „prace”, a /api/prace odpowiada 404 (jak serwer sprzed tej funkcji)
// (stary serwer ma też inny numer procesu w /api/ping — zdjęcie „stary” bez przeładowania strony udaje restart panelu;
// sprawdzanie modułów co 1,5 s zamiast co 3 min)
const PODMIANA = `(() => {
  const prawdziwy = window.fetch.bind(window);
  window.__bcPrace = 0;
  window.BC_TEST_MODULY_MS = 1500;
  window.fetch = async (url, init) => {
    const u = String((url && url.url) || url);
    const sciezka = u.replace(/^https?:\\/\\/[^/]+/, '').split('?')[0];
    const stary = sessionStorage.getItem('bc.test.stary') === '1';
    if (sciezka === '/api/prace') {
      window.__bcPrace++;
      if (stary) return new Response(JSON.stringify({ blad: 'Nie ma takiej trasy' }), { status: 404, headers: { 'Content-Type': 'application/json' } });
    }
    const odp = await prawdziwy(url, init);
    if (stary && sciezka === '/api/ping' && odp.ok) {
      const d = await odp.json();
      d.pid = Number(d.pid) + 1000000;
      return new Response(JSON.stringify(d), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    if (stary && sciezka === '/api/zdrowie' && odp.ok) {
      const d = await odp.json();
      if (d.moduly) delete d.moduly.prace;
      if (d.szczegoly) delete d.szczegoly.prace;
      return new Response(JSON.stringify(d), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return odp;
  };
})();`;

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_prace_"));
const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--window-size=412,915", "about:blank"], { stdio: "ignore" });

let ws;
let nr = 0;
const oczek = new Map();
const konsola = [];                                            // błędy z konsoli (wyjątki, console.error, sieć)
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
async function czekajNa(wyr, ms = 10000) {
  const koniec = Date.now() + ms;
  while (Date.now() < koniec) {
    try {
      if (await js(wyr)) return true;
    } catch (e) { /* strona się przeładowuje */ }
    await sleep(150);
  }
  return false;
}
async function zrzut(nazwa, selektor) {
  if (!zrzuty) return;
  if (selektor) await js(`(() => { const k = document.querySelector(${JSON.stringify(selektor)}); if (k) k.scrollIntoView({ block: 'center' }); return true; })()`);
  await sleep(300);
  const r = await wyslij("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
const tekst = (sel) => js(`(document.querySelector(${JSON.stringify(sel)}) || {}).textContent || ''`);
const HM = "\\d{1,2}:\\d{2}";

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
      return;
    }
    if (d.method === "Runtime.exceptionThrown") konsola.push("wyjątek: " + JSON.stringify(d.params.exceptionDetails).slice(0, 400));
    if (d.method === "Runtime.consoleAPICalled" && (d.params.type === "error" || d.params.type === "warning")) {
      konsola.push(d.params.type + ": " + (d.params.args || []).map((a) => a.value || a.description || "").join(" ").slice(0, 400));
    }
    if (d.method === "Log.entryAdded" && d.params.entry.level === "error") konsola.push("log: " + d.params.entry.text + " " + (d.params.entry.url || ""));
  });
  await wyslij("Page.enable");
  await wyslij("Runtime.enable");
  await wyslij("Log.enable");
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await wyslij("Page.addScriptToEvaluateOnNewDocument", { source: PODMIANA });
  await wyslij("Page.navigate", { url: PANEL + "/?l=" + encodeURIComponent(klucz) });
  await sleep(1500);
  await js(`localStorage.setItem('bc.kto', 'Karol'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });

  // ---------------------------------------------------------------- 1. Pulpit
  const jestKarta = await czekajNa(`(() => { const k = document.querySelector('.karta-prace'); return !!k && !k.hidden && k.querySelectorAll('.praca').length >= 3; })()`, 15000);
  sprawdz("1. karta „Prace w toku” na Pulpicie", jestKarta);
  sprawdz("1. karta nad „Czeka na Ciebie”", await js(`(() => { const a = document.querySelector('.karta-prace'), b = document.querySelector('.karta-czeka');
    return !!a && !!b && !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING); })()`));
  const kolejnosc = await js(`[...document.querySelectorAll('.karta-prace .prace-lista')][0] ? [...document.querySelectorAll('.karta-prace .prace-lista')][0].querySelectorAll(':scope > .praca').length + ':' + [...document.querySelectorAll('.karta-prace .prace-lista')][0].querySelector(':scope > .praca').dataset.praca : ''`);
  sprawdz("1. najpierw praca po czasie (wg szacowanego końca)", kolejnosc === "2:modele", kolejnosc);
  const modele = await tekst(`.karta-prace [data-praca="modele"] .praca-koniec`);
  sprawdz("1. „po czasie o 10 min” (kolor ostrzegawczy)", /^po czasie o (9|10|11) min$/.test(modele) &&
    await js(`document.querySelector('.karta-prace [data-praca="modele"] .praca-koniec').classList.contains('po-czasie')`), modele);
  const walka = await tekst(`.karta-prace [data-praca="walka-v2"] .praca-koniec`);
  sprawdz("1. „koniec ok. HH:MM (za 35 min)”", new RegExp("^koniec ok\\. " + HM + " \\(za (33|34|35) min\\)$").test(walka), walka);
  const etap = await tekst(`.karta-prace [data-praca="walka-v2"] .praca-pod`);
  sprawdz("1. etap „Poprawki (2 z 3)”", etap.includes("Poprawki (2 z 3)"), etap);
  sprawdz("1. paski postępu przy pracach w toku", await js(`!!document.querySelector('.karta-prace [data-praca="walka-v2"] .praca-pasek [style*="width"]') && !!document.querySelector('.karta-prace [data-praca="modele"] .praca-pasek')`));
  sprawdz("1. link „Dotyczy: raport …” przy pracy w toku", (await tekst(`.karta-prace [data-praca="walka-v2"] .praca-linki`)).includes("Walka v2: poprawki ataku"));
  const det = await js(`(() => { const d = document.querySelector('.karta-prace .prace-zakonczone'); return d ? (d.open ? 'otwarte:' : 'zwiniete:') + d.querySelector('summary').textContent : ''; })()`);
  sprawdz("1. „Zakończone dziś (1)” zwinięte", det === "zwiniete:Zakończone dziś (1)", det);
  await js(`document.querySelector('.karta-prace .prace-zakonczone summary').click(); true`);
  const gotowa = await tekst(`.karta-prace [data-praca="biom-las"]`);
  sprawdz("1. gotowa praca: „gotowe HH:MM” i „Zobacz raport „Mapa lasu — poprawki””",
    new RegExp("gotowe " + HM).test(gotowa) && gotowa.includes("Zobacz raport „Mapa lasu — poprawki”"), gotowa);
  const plakietka = await js(`(() => { const p = document.querySelector('.gora-prace'); return p && !p.hidden ? p.textContent : ''; })()`);
  sprawdz("1. plakietka w górnym pasku „2 · HH:MM”", new RegExp("^2 · " + HM + "$").test(plakietka), plakietka);
  sprawdz("1. bez przewijania w bok", await js(`document.documentElement.scrollWidth <= window.innerWidth + 1`),
    await js(`document.documentElement.scrollWidth + ' > ' + window.innerWidth`));
  await zrzut("prace_1_pulpit", ".karta-prace");
  await js(`[...document.querySelectorAll('.karta-prace [data-praca="biom-las"] .praca-link')].find(b => b.textContent.startsWith('Zobacz raport')).click(); true`);
  sprawdz("1. „Zobacz raport” prowadzi do raportu w zakładce Pytania", await czekajNa(`location.hash.includes('pytania') && location.hash.includes(${JSON.stringify(R.wynik)})`, 5000),
    await js(`location.hash`));

  // ---------------------------------------------------------------- 2. Pytania i Sesja
  await js(`location.hash = '#/pytania'; true`);
  const selCzeka = `#sprawa-raport-${R.czeka} .praca-znaczek`;
  sprawdz("2. znaczek przy raporcie, którego dotyczy praca", await czekajNa(`!!document.querySelector(${JSON.stringify(selCzeka)})`, 15000));
  const zn = await tekst(selCzeka);
  sprawdz("2. „w pracy — koniec ok. HH:MM”", new RegExp("^w pracy — koniec ok\\. " + HM + "$").test(zn), zn);
  const selPoprawa = `#sprawa-raport-${R.poprawa} .praca-znaczek`;
  sprawdz("2. historia: „poprawione — zobacz raport „Mapa lasu — poprawki””", await czekajNa(`(document.querySelector(${JSON.stringify(selPoprawa)}) || {}).textContent === 'poprawione — zobacz raport „Mapa lasu — poprawki”'`, 8000),
    await tekst(selPoprawa));
  sprawdz("2. bez znaczka przy raporcie z wynikiem", await js(`!!document.querySelector('#sprawa-raport-${R.wynik}') && !document.querySelector('#sprawa-raport-${R.wynik} .praca-znaczek')`));
  await zrzut("prace_2_pytania", selCzeka);
  await js(`document.querySelector(${JSON.stringify(selPoprawa)}).click(); true`);
  sprawdz("2. klik w „poprawione — zobacz raport” podświetla raport z wynikiem", await czekajNa(`!!document.querySelector('#sprawa-raport-${R.wynik}.podswietlony')`, 5000));
  await js(`location.hash = '#/sesja'; true`);
  sprawdz("2. zakładka Sesja: ten sam znaczek na liście pytań", await czekajNa(`[...document.querySelectorAll('[data-widok="sesja"] .praca-znaczek')].some(z => /^w pracy — koniec ok\\. ${HM}$/.test(z.textContent))`, 15000));

  // ---------------------------------------------------------------- 3. pusta lista
  const pliki = fs.readdirSync(katPrac).filter((n) => n.endsWith(".json"));
  const kopia = pliki.map((n) => [n, fs.readFileSync(path.join(katPrac, n))]);
  for (const n of pliki) fs.rmSync(path.join(katPrac, n));
  await js(`location.hash = '#/pulpit'; true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await czekajNa(`!!document.querySelector('.karta-czeka') && window.__bcPrace > 0`, 15000);
  await sleep(1500);
  sprawdz("3. pusta lista: serwer zapytany, karty nie ma", await js(`window.__bcPrace > 0 && !!document.querySelector('.karta-prace') && document.querySelector('.karta-prace').hidden`));
  sprawdz("3. pusta lista: bez plakietki", await js(`!document.querySelector('.gora-prace') || document.querySelector('.gora-prace').hidden`));

  // ---------------------------------------------------------------- 4. stary serwer
  for (const [n, b] of kopia) fs.writeFileSync(path.join(katPrac, n), b);
  const odBledu = konsola.length;
  await js(`sessionStorage.setItem('bc.test.stary', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await czekajNa(`!!document.querySelector('.karta-czeka .czeka-gora, .karta-czeka .czeka-zero')`, 15000);
  await sleep(3500);
  sprawdz("4. stary serwer: brak karty „Prace w toku”", await js(`!document.querySelector('.karta-prace') || document.querySelector('.karta-prace').hidden`));
  sprawdz("4. stary serwer: brak plakietki", await js(`!document.querySelector('.gora-prace') || document.querySelector('.gora-prace').hidden`));
  sprawdz("4. stary serwer: żadnego żądania /api/prace", await js(`window.__bcPrace === 0`), await js(`String(window.__bcPrace)`));
  await js(`location.hash = '#/pytania'; true`);
  await czekajNa(`!!document.querySelector('#sprawa-raport-${R.czeka}')`, 15000);
  await sleep(1000);
  sprawdz("4. stary serwer: brak znaczków w zakładce Pytania", await js(`!document.querySelector('.praca-znaczek')`));
  sprawdz("4. stary serwer: żadnego żądania /api/prace (także w Pytaniach)", await js(`window.__bcPrace === 0`));
  const nowe = konsola.slice(odBledu);
  sprawdz("4. stary serwer: bez błędów w konsoli", !nowe.length, nowe.join(" | "));

  // ---------------------------------------------------------------- 5. restart panelu przy otwartej stronie
  await js(`location.hash = '#/pulpit'; true`);
  await czekajNa(`!!document.querySelector('.karta-czeka')`, 10000);
  await sleep(2000);
  sprawdz("5. przed restartem: dalej bez karty i bez żądań /api/prace", await js(`(!document.querySelector('.karta-prace') || document.querySelector('.karta-prace').hidden) && window.__bcPrace === 0`));
  await js(`sessionStorage.setItem('bc.test.stary', '0'); true`);          // „restart”: nowy pid, moduł „prace” w /api/zdrowie
  sprawdz("5. po restarcie panelu karta pojawia się bez przeładowania strony",
    await czekajNa(`(() => { const k = document.querySelector('.karta-prace'); return !!k && !k.hidden && k.querySelectorAll('.praca').length >= 3; })()`, 15000));
  sprawdz("5. po restarcie: plakietka w górnym pasku", await czekajNa(`(() => { const p = document.querySelector('.gora-prace'); return !!p && !p.hidden; })()`, 5000));
  const oPracach = konsola.filter((t) => /prace/i.test(t));
  sprawdz("całość: żadnego błędu w konsoli o pracach", !oPracach.length, oPracach.join(" | "));
  if (konsola.length) console.log("(uwaga) inne wpisy konsoli: " + konsola.slice(0, 5).join(" | ").slice(0, 600));
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
