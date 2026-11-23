// Próba zakładki Wytwórnia w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_wytwornia.py na serwerze testowym z tymczasowym sejfem — nie ręcznie.
//
//   node testy/przegladarka_wytwornia.mjs <port> <katalog danych lokalnych> <katalog sejfu> <przeglądarka> [zrzuty]
//
// Sprawdza (telefon 390 px, potem komputer 1280 px): zakładka w nawigacji, portfel gier (BONK z metrykami), lejek
// (kolumny, karta w kolumnie etapu, zwinięte porzucone), radar trendów, karta pomysłu (tabela 10 kryteriów, suma
// agenta, krytyka wyróżniona), „Oceń” zapisuje kolumnę Karola i sumę w notatce, „Zmień etap”, pulpit gry (metryki,
// „brak danych”, decyzja i zadanie o grze), „Dodaj pomysł” tworzy notatkę i wpis w Dzienniku, karta „Gry” na Pulpicie,
// pięć kolumn lejka na komputerze; wszystko bez przewijania w bok i bez błędów JS.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, sejf, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 300) : ""));
};
const czytaj = (...czesci) => {
  try {
    return fs.readFileSync(path.join(sejf, ...czesci), "utf8");
  } catch (e) {
    return "";
  }
};

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_wytwornia_"));
const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--window-size=390,844", "about:blank"], { stdio: "ignore" });

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
  await sleep(400);
  const r = await wyslij("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
async function ekran(szer, wys, telefon) {
  await wyslij("Emulation.setDeviceMetricsOverride", { width: szer, height: wys, deviceScaleFactor: telefon ? 2 : 1, mobile: telefon });
  await sleep(300);
}
const bezPrzewijaniaWBok = () => js(`document.documentElement.scrollWidth <= window.innerWidth + 1`);
const klik = (selektor) => js(`(() => { const e = document.querySelector(${JSON.stringify(selektor)}); if (!e) return false; e.click(); return true; })()`);
const klikTekst = (selektor, tekst) => js(`(() => { const e = [...document.querySelectorAll(${JSON.stringify(selektor)})].find(x => x.textContent.includes(${JSON.stringify(tekst)})); if (!e) return false; e.click(); return true; })()`);
const wpisz = (selektor, tekst) => js(`(() => { const e = document.querySelector(${JSON.stringify(selektor)}); if (!e) return false; e.value = ${JSON.stringify(tekst)}; e.dispatchEvent(new Event('input', {bubbles: true})); return true; })()`);
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
  await ekran(390, 844, true);
  await wyslij("Page.navigate", { url: PANEL + "/?l=" + encodeURIComponent(klucz) });
  await sleep(1500);
  await js(`localStorage.setItem('bc.kto', 'Karol'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(1500);

  // 1. nawigacja
  sprawdz("1. Wytwórnia w nawigacji (po Pytaniach)", await czekajNa(`[...document.querySelectorAll('.nav-bok .nav-link .nav-tekst')].map(e => e.textContent).join(',').startsWith('Pulpit,Pytania,Wytwórnia,')`),
    await js(`[...document.querySelectorAll('.nav-bok .nav-link .nav-tekst')].map(e => e.textContent).join(',')`));

  // 2. lista: portfel, lejek, radar
  await js(`location.hash = '#/wytwornia'; true`);
  sprawdz("2. portfel: karta gry BONK z metrykami", await czekajNa(`!!document.querySelector('.wyt-gry .wyt-gra[data-gra="BONK"] .wyt-metryki')`, 12000));
  sprawdz("2. portfel: D1 12 % i „brak danych” przy D7", await js(`(() => { const m = [...document.querySelectorAll('.wyt-gra[data-gra="BONK"] .wyt-metryka')].map(x => x.textContent); return m[0] === 'D112 %' && m[1] === 'D7brak danych'; })()`),
    await js(`[...document.querySelectorAll('.wyt-gra[data-gra="BONK"] .wyt-metryka')].map(x => x.textContent).join('|')`));
  sprawdz("2. lejek: pięć kolumn etapów", await js(`[...document.querySelectorAll('.wyt-lejek .wyt-kolumna')].map(k => k.dataset.etap).join(',') === 'pomysł,ocena,prototyp,test,publiczna'`));
  sprawdz("2. lejek: Ring Potworów w kolumnie „ocena” z werdyktem i paskami", await js(`(() => { const k = document.querySelector('.wyt-kolumna[data-etap="ocena"] .wyt-karta[data-pomysl="Ring Potworów"]'); return !!k && !!k.querySelector('.chip.zloto') && k.querySelectorAll('.wyt-ocena').length === 3; })()`));
  // regresja 20.11 (zakładka otwarta na wersji sprzed poprawki: klasa „agent” zderzała się z widokiem Agent i rozciągała
  // karty na wysokość ekranu, a „null” trafiał na stronę) — karty zwarte, kolumna „ocena” z obiema notatkami
  sprawdz("2. lejek: kolumna „ocena” ma obie karty (w tym prawdziwą notatkę Monster Evolution)", await js(`document.querySelectorAll('.wyt-kolumna[data-etap="ocena"] .wyt-karta').length === 2 && !!document.querySelector('.wyt-karta[data-pomysl="Monster Evolution"]')`));
  sprawdz("2. lejek: karty zwarte (każda niższa niż 420 px)", await js(`[...document.querySelectorAll('.wyt-lejek .wyt-karta')].every(k => k.getBoundingClientRect().height < 420)`),
    await js(`[...document.querySelectorAll('.wyt-lejek .wyt-karta')].map(k => Math.round(k.getBoundingClientRect().height)).join(',')`));
  sprawdz("2. porzucone zwinięte na dole", await js(`(() => { const d = document.querySelector('details.wyt-zwiniete'); return !!d && !d.open && d.textContent.includes('Stary pomysł'); })()`));
  sprawdz("2. radar (prawdziwa notatka): co najmniej 10 trendów, data, pogrubienie w komórce bez gwiazdek", await js(`document.querySelectorAll('.wyt-radar .wyt-trend').length >= 10 &&
    document.body.textContent.includes('Aktualizacja: 2026-11-20') && !document.querySelector('.wyt-radar').textContent.includes('**')`),
    await js(`document.querySelectorAll('.wyt-radar .wyt-trend').length`));
  sprawdz("2. telefon: bez przewijania w bok", await bezPrzewijaniaWBok(), await js(`document.documentElement.scrollWidth + ' > ' + window.innerWidth`));
  await zrzut("wytwornia_telefon_lista");

  // 3. karta pomysłu
  await klik('.wyt-karta[data-pomysl="BONK"]');
  sprawdz("3. karta pomysłu BONK", await czekajNa(`location.hash.includes('pomysl=BONK') && !!document.querySelector('.wyt-szczegol-nagl h1') && document.querySelector('.wyt-szczegol-nagl h1').textContent === 'BONK'`));
  sprawdz("3. tabela 10 kryteriów, suma agenta 17/30", await js(`document.querySelectorAll('.wyt-tabela tbody tr').length === 10 && document.querySelector('.wyt-tabela tfoot td').textContent === '17/30'`),
    await js(`(document.querySelector('.wyt-tabela tfoot') || {}).textContent`));
  sprawdz("3. krytyka agenta wyróżniona", await js(`!!document.querySelector('.wyt-krytyka') && document.querySelector('.wyt-krytyka').textContent.includes('Za mało powodu')`));
  sprawdz("3. telefon: bez przewijania w bok", await bezPrzewijaniaWBok(), await js(`document.documentElement.scrollWidth + ' > ' + window.innerWidth`));
  sprawdz("3. bez „null” na stronie, ramka karty oceny zwarta", await js(`!document.querySelector('.wytwornia').textContent.includes('null') && !document.querySelector('.wytwornia').textContent.includes('[object') &&document.querySelector('.wyt-oceny').getBoundingClientRect().height < 160`),
    await js(`Math.round(document.querySelector('.wyt-oceny').getBoundingClientRect().height)`));
  await zrzut("wytwornia_telefon_pomysl");
  // prawdziwa notatka z badania: tabela, krytyka i wszystkie sekcje
  await js(`location.hash = '#/wytwornia?pomysl=' + encodeURIComponent('Monster Evolution'); true`);
  sprawdz("3. Monster Evolution: tabela 10 kryteriów, suma 26/30, krytyka i sekcje", await czekajNa(`(document.querySelector('.wyt-szczegol-nagl h1') || {}).textContent === 'Monster Evolution' &&
    document.querySelectorAll('.wyt-tabela tbody tr').length === 10 && document.querySelector('.wyt-tabela tfoot td').textContent === '26/30' && !!document.querySelector('.wyt-krytyka') &&
    ['Monetyzacja', 'Najtańszy test', 'Hak ciekawości'].every(s => [...document.querySelectorAll('.wyt-sekcja-notatki h2')].some(h => h.textContent === s))`),
    await js(`[...document.querySelectorAll('.wyt-sekcja-notatki h2')].map(h => h.textContent).join('|')`));
  await zrzut("wytwornia_telefon_monster_evolution");
  await js(`location.hash = '#/wytwornia?pomysl=BONK'; true`);
  await czekajNa(`(document.querySelector('.wyt-szczegol-nagl h1') || {}).textContent === 'BONK'`);

  // 4. ocena Karola
  sprawdz("4. „Oceń (Karol)”", await klikTekst('.wyt-akcje button', 'Oceń (Karol)'));
  sprawdz("4. okno oceny z 10 kryteriami", await czekajNa(`document.querySelectorAll('.arkusz .wyt-kryterium').length === 10`));
  await js(`document.querySelectorAll('.arkusz .wyt-skala').forEach((s, i) => s.querySelector('[data-v="' + (i < 9 ? 3 : 2) + '"]').click()); true`);
  sprawdz("4. suma na żywo 29/30", await js(`document.querySelector('.arkusz .wyt-suma').textContent === 'Suma: 29/30'`), await js(`document.querySelector('.arkusz .wyt-suma').textContent`));
  await zrzut("wytwornia_telefon_ocena");
  await klik('.arkusz form button[type=submit]');
  sprawdz("4. po zapisie suma Karola 29/30 w tabeli", await czekajNa(`!document.querySelector('.arkusz-tlo') && document.querySelectorAll('.wyt-tabela tfoot td')[1].textContent === '29/30'`));
  const bonk = czytaj("Wytwórnia", "Pomysły", "BONK.md");
  sprawdz("4. notatka: ocena_karol: 29 i kolumna Karol", bonk.includes("ocena_karol: 29\n") && bonk.includes("| Jedno zdanie | 3 | 3 |  |") && bonk.includes("| Koszt dla nas | 1 | 2 |  |"), bonk.slice(0, 200));
  sprawdz("4. Dziennik: wpis o ocenie", czytaj("Produkcja", "Dziennik zmian.md").includes("- Karol: ocena pomysłu BONK (Karol): 29/30 ([[BONK]])"));

  // 5. etap
  sprawdz("5. „Zmień etap”", await klikTekst('.wyt-akcje button', 'Zmień etap'));
  await czekajNa(`!!document.querySelector('.arkusz .wyt-etapy')`);
  await klikTekst('.arkusz .wyt-etapy button', 'Test');
  sprawdz("5. etap „Test” w karcie i w notatce", await czekajNa(`!document.querySelector('.arkusz-tlo') && document.querySelector('.wyt-szczegol-nagl .chipy').textContent.includes('Test')`) &&
    czytaj("Wytwórnia", "Pomysły", "BONK.md").includes("\netap: test\n"));

  // 6. pulpit gry
  await klikTekst('.wyt-akcje a', 'Pulpit gry');
  sprawdz("6. pulpit gry: metryki i „brak danych”", await czekajNa(`location.hash.includes('gra=BONK') && document.querySelectorAll('.wyt-metryki.duze .wyt-metryka').length === 4 && document.querySelector('.wyt-metryki.duze').textContent.includes('brak danych')`));
  sprawdz("6. pulpit gry: decyzja D-112 i zadanie o grze", await js(`document.body.textContent.includes('D-112') && document.body.textContent.includes('poprawić zamach pałką')`));
  sprawdz("6. telefon: bez przewijania w bok", await bezPrzewijaniaWBok());
  await zrzut("wytwornia_telefon_pulpit_gry");

  // 7. dodaj pomysł
  await js(`location.hash = '#/wytwornia'; true`);
  await czekajNa(`!!document.querySelector('.wyt-nagl button')`);
  await klikTekst('.wyt-nagl button', 'Dodaj pomysł');
  await czekajNa(`!!document.querySelector('.arkusz form input')`);
  await wpisz('.arkusz form input', 'Nowa gra testowa');
  await wpisz('.arkusz form textarea', 'Skaczesz po chmurach i zbierasz gwiazdy.');
  await klik('.arkusz form button[type=submit]');
  sprawdz("7. po dodaniu karta nowego pomysłu", await czekajNa(`location.hash.includes('pomysl=Nowa') && (document.querySelector('.wyt-szczegol-nagl h1') || {}).textContent === 'Nowa gra testowa'`, 10000),
    await js(`location.hash`));
  const nowy = czytaj("Wytwórnia", "Pomysły", "Nowa gra testowa.md");
  sprawdz("7. notatka z szablonu: etap pomysł i zdanie", nowy.includes("\netap: pomysł\n") && nowy.includes("## W jednym zdaniu\nSkaczesz po chmurach i zbierasz gwiazdy."), nowy.slice(0, 300));
  sprawdz("7. Dziennik: nowy pomysł", czytaj("Produkcja", "Dziennik zmian.md").includes("- Karol: nowy pomysł w Wytwórni: Nowa gra testowa ([[Nowa gra testowa]])"));

  // 8. Pulpit: karta „Gry”
  await js(`location.hash = '#/pulpit'; true`);
  sprawdz("8. Pulpit: karta „Gry” z BONK i „Pulpit gry”", await czekajNa(`(() => { const k = document.querySelector('.karta-gry'); return !!k && !k.hidden && !!k.querySelector('.wyt-gra[data-gra="BONK"] a[href*="gra=BONK"]'); })()`, 10000));
  await zrzut("wytwornia_telefon_pulpit");

  // 9. komputer: pięć kolumn lejka obok siebie
  await ekran(1280, 900, false);
  await js(`location.hash = '#/wytwornia'; true`);
  await czekajNa(`!!document.querySelector('.wyt-lejek')`);
  await sleep(400);
  sprawdz("9. komputer: lejek w pięciu kolumnach", await js(`getComputedStyle(document.querySelector('.wyt-lejek')).gridTemplateColumns.split(' ').length === 5`),
    await js(`getComputedStyle(document.querySelector('.wyt-lejek')).gridTemplateColumns`));
  sprawdz("9. komputer: bez przewijania w bok", await bezPrzewijaniaWBok());
  await zrzut("wytwornia_komputer_lista");
  sprawdz("10. bez błędów JS na stronie", !bledyStrony.length, bledyStrony.join(" | "));
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
