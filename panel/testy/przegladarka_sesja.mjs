// Próba zakładki Sesja w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+, bez
// zależności). Uruchamia ją testy/test_przegladarka_sesja.py na serwerze testowym — nie ręcznie.
//
//   node testy/przegladarka_sesja.mjs <port> <katalog danych lokalnych> <przeglądarka> [katalog zrzutów]
//
// Dwie OSOBNE sesje przeglądarki (osobne konteksty: osobne ciasteczka i pamięć) z atrapami urządzeń
// (--use-fake-device-for-media-stream, --use-fake-ui-for-media-stream, mikrofon = ciągły ton z pliku WAV):
//   A = Karol przy komputerze z panelem (klucz lokalny), B = Paweł jako gość z kodem dostępu (jak przez tunel).
// Sprawdza: obie osoby dołączają, połączenie WebRTC dochodzi do stanu „połączony” na pętli zwrotnej, gość nie
// włącza słuchania, po włączeniu „Agent słucha” obie strony widzą czerwony znacznik, odcinek dźwięku dochodzi do
// serwera i w widoku pojawia się wiersz transkrypcji (atrapa robotnika — BC_GLOS_ATRAPA=1 w serwerze testowym),
// obecność pokazuje dwie osoby, po rozłączeniu B znika z listy u A. Do tego układ: na telefonie przełącznik
// Transkrypcja / Notatki / Agenda / Pytania (domyślnie Transkrypcja, każda część jednym dotknięciem), na komputerze
// Transkrypcja i Notatki obok siebie w pierwszym ekranie (bez przewijania strony, także w rozmowie ze znacznikiem
// nagrywania), a Agenda i Pytania niżej; notatki agenta jako sekcje z punktami; odpowiedź na pytanie z listy w Sesji;
// stary serwer (404) i lustro tylko do odczytu (Agenda i Pytania jedna pod drugą).
// Klucze czyta z plików danych lokalnych serwera testowego i nigdzie ich nie wypisuje.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const kluczLokalny = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const token = fs.readFileSync(path.join(runtime, "token.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 300) : ""));
};

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_sesja_"));

/** Ciągły ton 440 Hz (WAV, 2 s, odtwarzany w pętli) jako atrapa mikrofonu. Domyślna atrapa Chromium to krótkie
 *  piknięcia co sekundę — miernik (próbka co 100 ms) czasem ich nie trafia i krótki odcinek wychodzi jako „cisza”. */
function plikTonu() {
  const czestotliwosc = 48000;
  const probki = czestotliwosc * 2;
  const b = Buffer.alloc(44 + probki * 2);
  b.write("RIFF", 0); b.writeUInt32LE(36 + probki * 2, 4); b.write("WAVE", 8);
  b.write("fmt ", 12); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(czestotliwosc, 24); b.writeUInt32LE(czestotliwosc * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34);
  b.write("data", 36); b.writeUInt32LE(probki * 2, 40);
  for (let i = 0; i < probki; i++) b.writeInt16LE(Math.round(Math.sin(2 * Math.PI * 440 * i / czestotliwosc) * 9000), 44 + i * 2);
  const plik = path.join(profil, "ton.wav");
  fs.writeFileSync(plik, b);
  return plik;
}

const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream",
  "--use-file-for-fake-audio-capture=" + plikTonu(),
  "--autoplay-policy=no-user-gesture-required", "--disable-features=WebRtcHideLocalIpsWithMdns",
  "--window-size=412,915", "about:blank"], { stdio: "ignore" });

let ws;
let nr = 0;
const oczek = new Map();
function wyslij(metoda, params = {}, sessionId) {
  return new Promise((res, rej) => {
    const n = ++nr;
    oczek.set(n, { res, rej });
    ws.send(JSON.stringify(Object.assign({ id: n, method: metoda, params }, sessionId ? { sessionId } : {})));
  });
}

class Karta {
  constructor(nazwa, sesja) {
    this.nazwa = nazwa;
    this.sesja = sesja;
  }
  async js(wyrazenie) {
    const r = await wyslij("Runtime.evaluate", { expression: wyrazenie, awaitPromise: true, returnByValue: true }, this.sesja);
    if (r.exceptionDetails) throw new Error(this.nazwa + " JS: " + JSON.stringify(r.exceptionDetails).slice(0, 400));
    return r.result.value;
  }
  async idz(url) {
    await wyslij("Page.navigate", { url }, this.sesja);
    await sleep(1500);
  }
  async czekajNa(wyr, ms = 10000) {
    const koniec = Date.now() + ms;
    while (Date.now() < koniec) {
      try {
        if (await this.js(wyr)) return true;
      } catch (e) { /* strona się przeładowuje */ }
      await sleep(250);
    }
    return false;
  }
  async zrzut(nazwa) {
    if (!zrzuty) return;
    const r = await wyslij("Page.captureScreenshot", { format: "png" }, this.sesja);
    fs.mkdirSync(zrzuty, { recursive: true });
    fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
  }
}

async function nowaKarta(nazwa) {
  const { browserContextId } = await wyslij("Target.createBrowserContext", { disposeOnDetach: true });
  await wyslij("Browser.grantPermissions", { permissions: ["audioCapture"], origin: PANEL, browserContextId }).catch(() => {});
  const { targetId } = await wyslij("Target.createTarget", { url: "about:blank", browserContextId });
  const { sessionId } = await wyslij("Target.attachToTarget", { targetId, flatten: true });
  const k = new Karta(nazwa, sessionId);
  await wyslij("Page.enable", {}, sessionId);
  await wyslij("Runtime.enable", {}, sessionId);
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 1, mobile: true }, sessionId);
  return k;
}

// Widok Sesja: przez zakładkę panelu (#/sesja), a gdy app.js jeszcze jej nie ma — zamontowany ręcznie z modułu.
async function otworzSesje(k) {
  await k.idz(PANEL + "/#/sesja");
  if (await k.czekajNa(`!!document.querySelector('[data-widok="sesja"] .sesja')`, 4000)) return "zakładka";
  await k.js(`(async () => {
    const { api } = await import('/wspolne/api.js');
    const ui = await import('/wspolne/ui.js');
    const ja = await api('/api/ja');
    const ctx = { api, ja, statyczny: false, konfiguracja: {}, idz() {}, toast: ui.toast, licznik() {}, jest: () => true,
      odpytuj: (fn, ms) => { const t = setInterval(fn, ms); return () => clearInterval(t); } };
    const m = await import('/widoki/sesja.js');
    const v = m.default.utworz(ctx);
    const kont = document.createElement('section');
    kont.dataset.widok = 'sesja';
    kont.append(v.el);
    document.getElementById('aplikacja').replaceChildren(kont);
    await v.pokaz({});
    return true; })()`);
  return "moduł";
}

/** Ile odcinków nagrania przyjął serwer (suma pola „odcinki” we wszystkich sesjach w danych lokalnych testu). */
function odcinkiNaSerwerze() {
  let suma = 0;
  const kat = path.join(runtime, "sesje");
  for (const sid of fs.existsSync(kat) ? fs.readdirSync(kat) : []) {
    for (let proba = 0; proba < 5; proba++) {
      try {
        const s = JSON.parse(fs.readFileSync(path.join(kat, sid, "sesja.json"), "utf8"));
        suma += Number(s.odcinki) || 0;
        break;
      } catch (e) { /* plik właśnie podmieniany albo to nie sesja — jeszcze raz */ }
    }
  }
  return suma;
}

const przycisk = (tekst) => `[...document.querySelectorAll('.sesja button')].find(b => b.textContent.trim() === ${JSON.stringify(tekst)})`;

try {
  let adres = null;
  for (let i = 0; i < 75 && !adres; i++) {
    try {
      adres = (await (await fetch("http://127.0.0.1:" + portDT + "/json/version")).json()).webSocketDebuggerUrl || null;
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

  const A = await nowaKarta("A");
  const B = await nowaKarta("B");
  await A.idz(PANEL + "/?l=" + encodeURIComponent(kluczLokalny));      // klucz lokalny -> ciasteczko
  await B.idz(PANEL + "/?k=" + encodeURIComponent(token));              // kod dostępu -> ciasteczko gościa
  for (const [k, imie] of [[A, "Karol"], [B, "Paweł"]]) {
    await k.js(`localStorage.setItem('bc.kto', ${JSON.stringify(imie)}); sessionStorage.setItem('bc.pytano', '1'); true`);
    await wyslij("Page.reload", { ignoreCache: true }, k.sesja);       // bez okna „Jak masz na imię?”
    await sleep(1500);
  }
  const jaA = await A.js(`fetch('/api/ja').then(r => r.json())`);
  const jaB = await B.js(`fetch('/api/ja').then(r => r.json())`);
  sprawdz("A jest przy komputerze, B jest gościem", jaA.lokalny === true && jaB.lokalny === false && jaB.decydent === false,
    JSON.stringify([jaA.lokalny, jaB.lokalny, jaB.decydent]));

  // ------------------------------------------------------------ stary serwer (jeszcze bez tras /api/sesje): 404
  await A.idz(PANEL + "/#/pulpit");
  await A.js(`(() => { const f = window.fetch.bind(window);
    window.fetch = (u, o) => String(u).startsWith('/api/sesje') ? Promise.resolve(new Response(
      JSON.stringify({ blad: 'Nie ma takiej trasy: ' + u }), { status: 404, headers: { 'Content-Type': 'application/json' } })) : f(u, o);
    location.hash = '#/sesja'; return true; })()`);
  if (await A.czekajNa(`!!document.querySelector('[data-widok="sesja"] .sesja')`, 4000)) {
    sprawdz("stary serwer (404): widok mówi o restarcie panelu",
      await A.czekajNa(`document.querySelector('.sesja').textContent.includes('zacznie działać po restarcie panelu')`, 6000));
    await A.zrzut("sesja_A_stary_serwer");
  } else console.log("info zakładki Sesja jeszcze nie ma w app.js — pomijam próbę starego serwera");
  await wyslij("Page.reload", { ignoreCache: true }, A.sesja);          // bez podmienionego fetch
  await sleep(1500);

  // ------------------------------------------------------------ lustro tylko do odczytu: Agenda i Pytania (bez rozmowy)
  await A.js(`(async () => {
    const { api } = await import('/wspolne/api.js');
    const ui = await import('/wspolne/ui.js');
    const ja = await api('/api/ja');
    const ctx = { api, ja, statyczny: true, konfiguracja: {}, idz() {}, toast: ui.toast, licznik() {}, jest: () => true,
      odpytuj: () => () => {} };
    const m = await import('/widoki/sesja.js');
    const v = m.default.utworz(ctx);
    const kont = document.createElement('section');
    kont.dataset.widok = 'sesja-lustro';
    kont.append(v.el);
    document.getElementById('aplikacja').replaceChildren(kont);
    await v.pokaz({});
    return true; })()`);
  const wLustrze = (sel) => `(() => { const e = document.querySelector('[data-widok="sesja-lustro"] ' + ${JSON.stringify(sel)});
    return !!(e && e.getClientRects().length && e.getBoundingClientRect().height > 0); })()`;
  sprawdz("lustro (telefon): widać i Agendę, i listę Pytania, a rozmowa jest opisana jako niedostępna",
    await A.czekajNa(`${wLustrze(".sesja-agenda-karta")} && ${wLustrze(".sesja-pytania")} &&
      document.querySelector('[data-widok="sesja-lustro"]').textContent.includes('tylko na żywym panelu')`, 8000),
    await A.js(`(document.querySelector('[data-widok="sesja-lustro"] .sesja-czesci') || {}).innerHTML`));
  await A.zrzut("sesja_A_lustro");
  await wyslij("Page.reload", { ignoreCache: true }, A.sesja);
  await sleep(1500);

  const tryb = await otworzSesje(A);
  await otworzSesje(B);
  console.log("info widok otwarty przez: " + tryb);
  sprawdz("A: widok Sesja wstał z agendą", await A.czekajNa(`document.querySelectorAll('.sesja-temat').length >= 2`));
  sprawdz("B: przełącznik „Agent słucha” zablokowany dla gościa", await B.czekajNa(`document.querySelector('.sesja-slucha').disabled === true`));
  sprawdz("A: przełącznik „Agent słucha” dostępny", await A.czekajNa(`document.querySelector('.sesja-slucha').disabled === false`));

  // ------------------------------------------------------------ układ: telefon — przełącznik części (domyślnie Transkrypcja)
  const widoczny = (sel) => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); return !!(e && e.getClientRects().length && e.getBoundingClientRect().height > 0); })()`;
  const opcja = (t) => `[...document.querySelectorAll('.sesja-przelacznik .przelacznik-opcja')].find(b => b.textContent.startsWith(${JSON.stringify(t)}))`;
  const naEkranie = (sel) => `(() => { const r = document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect();
    return r.height > 0 && r.top >= 0 && r.bottom <= innerHeight + 1; })()`;
  sprawdz("A (telefon): przełącznik Transkrypcja / Notatki / Agenda / Pytania, na start widać Transkrypcję",
    await A.czekajNa(`${widoczny(".sesja-przelacznik")} && ${widoczny(".sesja-zapis-karta")} && !${widoczny(".sesja-notatki-karta")} &&
      !${widoczny(".sesja-agenda")} && !${widoczny(".sesja-pytania")} &&
      [...document.querySelectorAll('.sesja-przelacznik .przelacznik-opcja')].map(b => b.textContent.replace(/\\d+$/, '')).join(',') === 'Transkrypcja,Notatki,Agenda,Pytania'`),
    await A.js(`[...document.querySelectorAll('.sesja-przelacznik .przelacznik-opcja')].map(b => b.textContent).join(',')`));
  sprawdz("A (telefon): Transkrypcja mieści się na ekranie (bez przewijania strony)", await A.czekajNa(`(window.scrollTo(0, 0), ${naEkranie(".sesja-zapis-karta")})`),
    await A.js(`JSON.stringify(document.querySelector('.sesja-zapis-karta').getBoundingClientRect()) + ' / ' + innerHeight`));
  await A.zrzut("sesja_A_telefon_transkrypcja");
  await A.js(`${opcja("Notatki")}.click(); true`);
  sprawdz("A (telefon): Notatki jednym dotknięciem", await A.czekajNa(`${widoczny(".sesja-notatki-karta")} && !${widoczny(".sesja-zapis-karta")}`));
  await A.js(`${opcja("Agenda")}.click(); true`);
  sprawdz("A (telefon): Agenda jednym dotknięciem", await A.czekajNa(`${widoczny(".sesja-agenda")} && !${widoczny(".sesja-notatki-karta")}`));
  await A.js(`${opcja("Pytania")}.click(); true`);
  sprawdz("A (telefon): po przełączeniu widać listę Pytania z pytaniem #2",
    await A.czekajNa(`${widoczny(".sesja-pytania")} && !!document.getElementById('sesja-sprawa-pytanie-2')`, 8000),
    await A.js(`(document.querySelector('.sesja-pytania') || {}).textContent`));
  await A.zrzut("sesja_A_pytania_telefon");
  const odpSesja = "Odpowiedź z listy w Sesji " + Date.now();
  await A.js(`(() => { const k = document.getElementById('sesja-sprawa-pytanie-2'); const p = k.querySelector('textarea');
    p.value = ${JSON.stringify(odpSesja)}; p.dispatchEvent(new Event('input')); k.querySelector('form button[type=submit]').click(); return true; })()`);
  sprawdz("A: odpowiedź z listy w Sesji zapisana w sejfie i karta znika", await A.czekajNa(`fetch('/api/sejf/plan').then(r => r.json()).then(p =>
    (p.pytania.find(x => x.nr === 2) || {}).odpowiedz_md.includes(${JSON.stringify(odpSesja)}) && !document.getElementById('sesja-sprawa-pytanie-2'))`, 10000));

  // ------------------------------------------------------------ układ: komputer — Transkrypcja | Notatki w pierwszym ekranie
  const naKomputerze = () => wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false }, A.sesja);
  const naTelefonie = () => wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 1, mobile: true }, A.sesja);
  const pierwszyEkran = `(() => { window.scrollTo(0, 0);
    const z = document.querySelector('.sesja-zapis-karta').getBoundingClientRect();
    const n = document.querySelector('.sesja-notatki-karta').getBoundingClientRect();
    return z.width > 300 && n.width > 300 && z.height >= 300 && Math.abs(z.top - n.top) < 4 && n.left >= z.right - 1 &&
      z.top >= 0 && z.bottom <= innerHeight && n.bottom <= innerHeight; })()`;
  const opisEkranu = `JSON.stringify(['.sesja-pokoj', '.sesja-zapis-karta', '.sesja-notatki-karta'].map(s => {
    const r = document.querySelector(s).getBoundingClientRect(); return [s, Math.round(r.top), Math.round(r.bottom), Math.round(r.width)]; })) + ' / ' + innerHeight`;
  await naKomputerze();
  sprawdz("A (komputer): Transkrypcja i Notatki obok siebie w pierwszym ekranie, bez przewijania", await A.czekajNa(pierwszyEkran, 5000),
    await A.js(opisEkranu));
  sprawdz("A (komputer): Agenda i Pytania obok siebie, niżej", await A.czekajNa(`(() => {
    const a = document.querySelector('.sesja-agenda').closest('.sesja-czesc').getBoundingClientRect();
    const p = document.querySelector('.sesja-pytania').getBoundingClientRect();
    const z = document.querySelector('.sesja-zapis-karta').getBoundingClientRect();
    return a.width > 0 && p.width > 0 && Math.abs(a.top - p.top) < 4 && p.left > a.right - 1 && a.top >= z.bottom; })()`, 5000));
  sprawdz("A (komputer): skróty Agenda i Pytania w pasku pokoju", await A.js(`[...document.querySelectorAll('.sesja-skrot')].filter(b => b.getClientRects().length).length === 2`));
  await A.zrzut("sesja_A_komputer");
  await naTelefonie();
  await A.js(`${opcja("Transkrypcja")}.click(); true`);

  // ------------------------------------------------------------ dołączenie i WebRTC
  await A.js(`${przycisk("Dołącz")}.click(); true`);
  sprawdz("A dołączył", await A.czekajNa(`!!${przycisk("Rozłącz")}`, 10000));
  await B.js(`${przycisk("Dołącz")}.click(); true`);
  sprawdz("B dołączył", await B.czekajNa(`!!${przycisk("Rozłącz")}`, 10000));
  const polaczonyA = await A.czekajNa(`!!document.querySelector('.sesja-osoba[data-polaczenie="polaczony"]')`, 40000);
  const polaczonyB = await B.czekajNa(`!!document.querySelector('.sesja-osoba[data-polaczenie="polaczony"]')`, 10000);
  await A.zrzut("sesja_A_polaczeni");
  sprawdz("WebRTC: A widzi połączony głos z B", polaczonyA,
    await A.js(`[...document.querySelectorAll('.sesja-osoba')].map(o => o.dataset.polaczenie + '/' + o.dataset.stan).join(', ')`));
  sprawdz("WebRTC: B widzi połączony głos z A", polaczonyB);
  sprawdz("A: miernik mikrofonu widoczny", await A.js(`!document.querySelector('.sesja-miernik').hidden`));
  const ob = await A.js(`fetch('/api/obecnosc').then(r => r.json())`);
  sprawdz("obecność: dwie osoby w rozmowie", ob.rozmowa && ob.rozmowa.osoby.length === 2, JSON.stringify(ob.rozmowa));

  // ------------------------------------------------------------ gość nie włącza słuchania
  const statusB = await B.js(`fetch('/api/sesje/sluchanie', { method: 'POST', headers: { 'X-BC': '1', 'Content-Type': 'application/json' }, body: JSON.stringify({ wlacz: true }) }).then(r => r.status)`);
  sprawdz("B (gość): włączenie słuchania odrzucone 403", statusB === 403, statusB);

  // ------------------------------------------------------------ agent słucha -> odcinek -> transkrypcja (atrapa)
  for (const X of [A, B]) {                                    // dziennik wysyłek odcinków (do diagnostyki)
    await X.js(`(() => { const f = window.fetch.bind(window); window.__odcinki = [];
      window.fetch = (u, o) => { const p = f(u, o); if (String(u).includes('/api/sesje/odcinek')) {
        const t0 = Date.now(); p.then((r) => window.__odcinki.push(String(u).replace(/^.*[?]/, '') + ' -> ' + r.status + ' (' + (Date.now() - t0) + ' ms)'),
          (e) => window.__odcinki.push(String(u).replace(/^.*[?]/, '') + ' -> ' + e)); } return p; }; return true; })()`);
  }
  await A.js(`document.querySelector('.sesja-slucha').click(); true`);
  sprawdz("A: czerwony znacznik nagrywania", await A.czekajNa(`!document.querySelector('.sesja-baner').hidden`, 8000));
  sprawdz("B: czerwony znacznik nagrywania", await B.czekajNa(`!document.querySelector('.sesja-baner').hidden`, 8000));
  const wpis = await A.czekajNa(`[...document.querySelectorAll('.sesja-wpis')].some(w => w.textContent.includes('Atrapa transkrypcji'))`, 90000);
  await A.zrzut("sesja_A_transkrypcja");
  await B.zrzut("sesja_B_transkrypcja");
  sprawdz("A: wiersz transkrypcji w widoku", wpis,
    await A.js(`document.querySelector('.sesja-zapis-stan').textContent + ' | ' + document.querySelector('.sesja-zapis').textContent`));
  sprawdz("B: wiersz transkrypcji w widoku (gość w pokoju)",
    await B.czekajNa(`[...document.querySelectorAll('.sesja-wpis')].some(w => w.textContent.includes('Atrapa transkrypcji'))`, 20000));
  const kto = await A.js(`[...document.querySelectorAll('.sesja-wpis-kto')].map(e => e.textContent).join(',')`);
  sprawdz("transkrypcja podpisana imieniem mówiącego", /Karol:|Paweł:/.test(kto), kto);

  // ------------------------------------------------------------ notatki agenta: krótkie punkty w sekcjach
  // (agenta w teście nie ma — notatki w nowym formacie kładziemy do katalogu bieżącej sesji jak panel po przebiegu)
  const katSesji = path.join(runtime, "sesje");
  const biezaca = fs.readdirSync(katSesji).filter((n) => /^\d{8}-\d{6}-[0-9a-f]{4}$/.test(n)).sort().pop();
  fs.writeFileSync(path.join(katSesji, biezaca, "notatki.md"), "## Ustalenia\n- Energia znika z gry (D-048).\n" +
    "- Trzy poziomy trudności lokalne dla biomu.\n\n## Do zrobienia\n- Paweł: ikona licznika zadań w HUD.\n\n" +
    "## Padły odpowiedzi na pytania\n- #8: rezygnujemy z Energii.\n", "utf8");
  const notatkiOk = `(() => { const m = document.querySelector('.sesja-notatki-md'); return !!m && m.querySelectorAll('h2').length === 3 &&
    m.querySelectorAll('li').length === 4 && !m.querySelector('p'); })()`;
  sprawdz("A: notatki agenta jako nagłówki sekcji i punkty", await A.czekajNa(notatkiOk, 15000),
    await A.js(`(document.querySelector('.sesja-notatki') || {}).innerHTML`));
  await A.js(`${opcja("Notatki")}.click(); true`);
  sprawdz("A (telefon): notatki widoczne po przełączeniu", await A.czekajNa(`${widoczny(".sesja-notatki-md")}`));
  await A.zrzut("sesja_A_telefon_notatki");
  await naKomputerze();
  sprawdz("A (komputer, w rozmowie i ze znacznikiem nagrywania): Transkrypcja i Notatki w pierwszym ekranie",
    await A.czekajNa(`!document.querySelector('.sesja-baner').hidden && ${pierwszyEkran}`, 5000), await A.js(opisEkranu));
  await A.zrzut("sesja_A_komputer_rozmowa");
  await naTelefonie();
  await A.js(`${opcja("Transkrypcja")}.click(); true`);

  // ------------------------------------------------------------ wyłączenie i rozłączenie
  // Ostatni kawałek nagrania po wyłączeniu słuchania: przeglądarka wysyła go dopiero po wyłączeniu (A od razu,
  // B po pulsie), a serwer przyjmuje go w oknie łaski. Liczymy odcinki przyjęte przez serwer (sesja.json).
  const odcinkiPrzed = odcinkiNaSerwerze();
  await A.js(`document.querySelector('.sesja-slucha').click(); true`);
  sprawdz("A: znacznik nagrywania znika po wyłączeniu", await A.czekajNa(`document.querySelector('.sesja-baner').hidden`, 8000));
  await sleep(3500);
  const odcinkiPo = odcinkiNaSerwerze();
  for (const [kto, X] of [["A", A], ["B", B]]) {
    console.log("info " + kto + ": wysyłki odcinków " + await X.js(`(window.__odcinki || []).join('; ')`));
  }
  sprawdz("ostatni kawałek nagrania po wyłączeniu słuchania dotarł do serwera", odcinkiPo > odcinkiPrzed,
    odcinkiPrzed + " -> " + odcinkiPo);
  await B.js(`${przycisk("Rozłącz")}.click(); true`);
  sprawdz("B rozłączony", await B.czekajNa(`!!${przycisk("Dołącz")}`, 8000));
  sprawdz("A: B znika z listy po rozłączeniu", await A.czekajNa(`document.querySelectorAll('.sesja-osoba').length === 1`, 10000));
  await A.js(`${przycisk("Rozłącz")}.click(); true`);
  await sleep(1000);
} catch (e) {
  sprawdz("przebieg", false, (e && e.stack) || e);
} finally {
  try { await wyslij("Browser.close"); } catch (e) { /* nic */ }
  await sleep(1000);
  try { proc.kill(); } catch (e) { /* nic */ }
  await sleep(500);
  try { fs.rmSync(profil, { recursive: true, force: true }); } catch (e) { /* plik może być jeszcze zablokowany */ }
  process.exit(bledy ? 1 : 0);
}
