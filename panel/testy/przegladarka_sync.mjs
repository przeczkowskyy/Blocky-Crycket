// Próba stanu stałej synchronizacji z GitHubem na Pulpicie (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_sync.py na serwerze testowym — nie ręcznie.
//
//   node testy/przegladarka_sync.mjs <port> <katalog danych lokalnych> <przeglądarka> [zrzuty]
//
// GET /api/git/stan i GET /api/git/auto podmienia strona (fetch podstawiony przed startem aplikacji): serwer testowy
// działa w katalogu prawdziwego repozytorium, więc te trasy nie są wołane wcale. Scenariusz w sessionStorage
// („bc.test.sync”) przeżywa przeładowanie strony.
// Scenariusze:
//   1. stary serwer (stan bez pola `auto`, /api/git/auto = 404): karta jak dotąd — Pobierz i Wyślij, bez stanu;
//   2. „Zsynchronizowano HH:MM”;
//   3. „Czeka: lokalne zmiany w 2 plikach”, klik = szczegóły z plikami i „Co zrobić”;
//   4. „Konflikt — potrzebny człowiek”;
//   5. panel sam pobrał cudze zmiany: krótka informacja „kto i co” (zwykły tekst, bez HTML) i wiersz na Pulpicie.
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

// podmiana fetch przed startem aplikacji: trasy gita biorą odpowiedź ze scenariusza (sessionStorage) albo 404
const PODMIANA = `(() => {
  const prawdziwy = window.fetch.bind(window);
  const sc = () => { try { return JSON.parse(sessionStorage.getItem('bc.test.sync') || '{}'); } catch (e) { return {}; } };
  window.__bcSyncWywolania = [];
  window.fetch = (url, init) => {
    const u = String((url && url.url) || url);
    const sciezka = u.replace(/^https?:\\/\\/[^/]+/, '').split('?')[0];
    if (sciezka === '/api/git/stan' || sciezka === '/api/git/auto') {
      window.__bcSyncWywolania.push(sciezka);
      const s = sc();
      const d = sciezka === '/api/git/stan' ? s.stan : s.auto;
      const odp = (status, obj) => Promise.resolve(new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json' } }));
      return d ? odp(200, d) : odp(404, { blad: 'Nie ma takiej trasy: ' + sciezka });
    }
    return prawdziwy(url, init);
  };
})();`;

const STAN = {
  galaz: "main", czyste: true, zmienione: [], zmiany_panelu: 0, zmiany_sejfu: [], do_wyslania: 0, do_pobrania: 0,
  ostatni_fetch: null, ostatnie_commity: [], zdalne: { nazwa: "origin", url: "https://example.invalid/repo.git", galaz: "origin/main" },
};
const teraz = new Date();
const HM = String(teraz.getHours()).padStart(2, "0") + ":" + String(teraz.getMinutes()).padStart(2, "0");
const AUTO = { wlaczona: true, stan: "ok", opis: "Wszystko zgodne z GitHubem.", krotko: null, co_zrobic: null, pliki: [], plikow: 0,
  zgodne: teraz.toISOString(), pobranie: null, wyslanie: null, co_s: 90, wyslij_po_s: 60, czeka_na_wyslanie: 0 };

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_sync_"));
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
  await js(`(() => { const k = document.querySelector('.karta-sync'); if (k && !document.querySelector('.arkusz')) k.scrollIntoView({ block: 'center' }); return true; })()`);
  await sleep(300);
  const r = await wyslij("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
const scenariusz = (stan, auto) => js(`sessionStorage.setItem('bc.test.sync', ${JSON.stringify(JSON.stringify({ stan, auto }))}); true`);
const odswiezWTle = () => js(`document.dispatchEvent(new Event('visibilitychange')); true`);
const tekstStanu = () => js(`(document.querySelector('.karta-sync .sync-auto') || {}).textContent || ''`);

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
    }
  });
  await wyslij("Page.enable");
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await wyslij("Page.addScriptToEvaluateOnNewDocument", { source: PODMIANA });
  await wyslij("Page.navigate", { url: PANEL + "/?l=" + encodeURIComponent(klucz) });
  await sleep(1500);
  await js(`localStorage.setItem('bc.kto', 'Karol'); sessionStorage.setItem('bc.pytano', '1'); true`);

  // 1. stary serwer: stan bez `auto`, /api/git/auto = 404
  await scenariusz(STAN, null);
  await wyslij("Page.reload", { ignoreCache: true });
  sprawdz("1. karta Synchronizacja z przyciskami (stary serwer)", await czekajNa(`!!document.querySelector('.karta-sync .sync-przyciski')`, 12000));
  await sleep(800);
  sprawdz("1. bez stanu synchronizacji (widok jak dotąd)", await js(`!document.querySelector('.karta-sync .sync-auto')`));
  sprawdz("1. powłoka zapytała o /api/git/auto i nic nie pokazała", await js(`window.__bcSyncWywolania.includes('/api/git/auto') &&
    ![...document.querySelectorAll('.toast')].some(t => /GitHub|404|trasy/.test(t.textContent))`));
  sprawdz("1. przyciski Pobierz i Wyślij", await js(`(() => { const t = document.querySelector('.karta-sync .sync-przyciski').textContent; return t.includes('Pobierz') && t.includes('Wyślij'); })()`));
  await zrzut("sync_1_stary");

  // 2. zsynchronizowano
  await scenariusz(Object.assign({}, STAN, { auto: AUTO }), AUTO);
  await odswiezWTle();
  sprawdz("2. „Zsynchronizowano HH:MM”", await czekajNa(`((document.querySelector('.karta-sync .sync-auto') || {}).textContent || '') === ${JSON.stringify("Zsynchronizowano " + HM)}`), await tekstStanu());
  sprawdz("2. przyciski dalej są", await js(`!!document.querySelector('.karta-sync .sync-przyciski')`));
  await zrzut("sync_2_ok");

  // 3. czeka: lokalne zmiany w 2 plikach, szczegóły po kliknięciu
  const czeka = Object.assign({}, AUTO, { stan: "czeka", krotko: "lokalne zmiany w 2 plikach", plikow: 2, pliki: ["B&C/Gra/Notatka.md", "src/x.lua"],
    opis: "Na GitHubie są nowe zmiany (1), ale dotyczą plików, które ktoś zmienia na tym komputerze.", co_zrobic: "Zapisz te pliki commitem — panel scali resztę sam." });
  await scenariusz(Object.assign({}, STAN, { auto: czeka }), czeka);
  await odswiezWTle();
  sprawdz("3. „Czeka: lokalne zmiany w 2 plikach”", await czekajNa(`((document.querySelector('.karta-sync .sync-auto') || {}).textContent || '') === 'Czeka: lokalne zmiany w 2 plikach'`), await tekstStanu());
  await js(`document.querySelector('.karta-sync .sync-auto').click(); true`);
  sprawdz("3. szczegóły: pliki i „Co zrobić”", await czekajNa(`(() => { const a = document.querySelector('.arkusz'); return !!a && a.textContent.includes('src/x.lua') && a.textContent.includes('Co zrobić') && a.textContent.includes('Zapisz te pliki commitem'); })()`));
  await zrzut("sync_3_czeka");
  await js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); document.documentElement.classList.remove('bez-przewijania'); true`);

  // 4. konflikt
  const konflikt = Object.assign({}, AUTO, { stan: "konflikt", krotko: "potrzebny człowiek", plikow: 1, pliki: ["a.txt"], opis: "Konflikt.", co_zrobic: "Poproś agenta." });
  await scenariusz(Object.assign({}, STAN, { auto: konflikt }), konflikt);
  await odswiezWTle();
  sprawdz("4. „Konflikt — potrzebny człowiek”", await czekajNa(`((document.querySelector('.karta-sync .sync-auto') || {}).textContent || '') === 'Konflikt — potrzebny człowiek'`), await tekstStanu());
  await zrzut("sync_4_konflikt");

  // 5. informacja po pobraniu: pierwsze sprawdzenie zapamiętuje, nowe pobranie = toast z autorem i tematem (zwykły tekst)
  const p1 = { id: "t-1", kiedy: new Date(Date.now() - 3600000).toISOString(), ile: 1, autorzy: ["Karol"], commity: [{ hash: "a1", autor: "Karol", temat: "stare" }] };
  const a1 = Object.assign({}, AUTO, { pobranie: p1 });
  await scenariusz(Object.assign({}, STAN, { auto: a1 }), a1);
  await wyslij("Page.reload", { ignoreCache: true });                      // powłoka zaczyna od nowa (przerwa po 404 znika)
  await czekajNa(`window.__bcSyncWywolania && window.__bcSyncWywolania.includes('/api/git/auto')`, 12000);
  await sleep(800);
  sprawdz("5. pierwsze sprawdzenie bez informacji", await js(`![...document.querySelectorAll('.toast')].some(t => t.textContent.includes('Z GitHuba'))`));
  const p2 = { id: "t-2", kiedy: new Date().toISOString(), ile: 2, autorzy: ["Paweł"],
    commity: [{ hash: "b1", autor: "Paweł", temat: "<b>Nowy HUD</b> & rybki" }, { hash: "b2", autor: "Paweł", temat: "Okno ekwipunku" }] };
  const a2 = Object.assign({}, AUTO, { pobranie: p2 });
  await scenariusz(Object.assign({}, STAN, { auto: a2 }), a2);
  await js(`window.__bcPobrano = 0; window.addEventListener('bc:git-pobrano', () => { window.__bcPobrano++; }); true`);
  await odswiezWTle();
  const jest = await czekajNa(`[...document.querySelectorAll('.toast')].some(t => t.textContent.includes('Z GitHuba: Paweł — 2 zmiany'))`, 8000);
  const toast = await js(`([...document.querySelectorAll('.toast')].find(t => t.textContent.includes('Z GitHuba')) || {}).textContent || ''`);
  sprawdz("5. informacja „Z GitHuba: Paweł — 2 zmiany: …”", jest, toast);
  sprawdz("5. temat jako zwykły tekst (bez HTML)", toast.includes("„<b>Nowy HUD</b> & rybki”") &&
    await js(`![...document.querySelectorAll('.toast')].some(t => t.querySelector('b'))`), toast);
  sprawdz("5. zdarzenie bc:git-pobrano dla widoków", await js(`window.__bcPobrano === 1`));
  sprawdz("5. wiersz „Pobrano …” na Pulpicie", await czekajNa(`(() => { const w = document.querySelector('.karta-sync .sync-pobranie'); return !!w && w.textContent.includes('Paweł') && w.textContent.includes('<b>Nowy HUD</b>') && !w.querySelector('b'); })()`),
    await js(`(document.querySelector('.karta-sync .sync-pobranie') || {}).textContent || ''`));
  await zrzut("sync_5_pobrano");
  sprawdz("5. to samo pobranie drugi raz — bez nowej informacji", await (async () => {
    await odswiezWTle();
    await sleep(800);
    return js(`window.__bcPobrano === 1`);
  })());
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
