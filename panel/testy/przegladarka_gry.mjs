// Próba „pulpit per gra” (25.11.2026) w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_gry.py na serwerze testowym z kopią sejfu i rejestrem gier — nie ręcznie.
//
//   node testy/przegladarka_gry.mjs <port> <katalog danych lokalnych> <katalog Produkcja> <przeglądarka> [zrzuty]
//
// Klucze (lokalny, zatwierdzania) czyta z plików danych lokalnych serwera testowego i nigdzie ich nie wypisuje.
// Dane (testy/test_gry.py): bc — pytania 1, 4, 6, 7 i raport „Zwykły raport 2”; wspólne — D-004 i raport „Sesja główna”;
// smok — pytanie 3, D-003 i dwa raporty; Pet Arena — pytanie 2, D-002 i raport ze znacznikiem.
// Scenariusze (telefon 390 px, potem komputer 1280 px):
//   1. na start gra domyślna: przełącznik w górnym pasku, plakietka „+7” (tyle czeka w innych grach), lista tylko bc
//      i wspólne, plakietka Pytań = 7, bez przewijania w bok;
//   2. okno „Która gra?”: gry z liczbami, wstrzymane przygaszone, „Wszystkie gry”;
//   3. wybór „Gra o smoku”: lista smoka i wspólne, nazwa w nagłówku, wybór zapamiętany po przeładowaniu;
//   4. Zadania: tylko smok i wspólne, „Dodaj zadanie” w smoku zapisuje „· #gra/smok”;
//   5. „Wszystkie gry”: wszystkie sprawy z etykietą gry;
//   6. adres ?gra=bc ustawia wybór i znika z paska; adres do sprawy z innej gry przełącza na jej grę;
//   7. wyszukiwarka mówi o trafieniach w innych grach;
//   8. Pulpit „Czeka na Ciebie” i Podgląd „Do przejrzenia” liczą tylko wybraną grę;
//   9. komputer: przełącznik w bocznym pasku, okno, bez przewijania w bok.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, produkcja, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const czytaj = (n) => fs.readFileSync(path.join(produkcja, n), "utf8");
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 300) : ""));
};

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_g_"));
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
async function idz(url) {
  await wyslij("Page.navigate", { url });
  await sleep(1500);
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
  const r = await wyslij("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
const karta = (k) => `document.getElementById(${JSON.stringify("sprawa-" + k)})`;
const LISTA = ".pytania .lista-pytan:not(.zwarta) > .kolejka-lista";
const naLiscie = () => js(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].map(k => k.dataset.klucz).sort().join(',')`);
const bezPrzewijaniaWBok = () => js(`document.documentElement.scrollWidth <= window.innerWidth + 1`);
const odznakaPytan = () => js(`(document.querySelector('[data-odznaka="pytania"]:not([hidden])') || {}).textContent || ''`);
const R = { bc: "raport-r-20261125-100200-cccc", wsp: "raport-r-20261125-100400-eeee", smok1: "raport-r-20261125-100000-aaaa",
  smok2: "raport-r-20261125-100300-dddd", pet: "raport-r-20261125-100100-bbbb" };
const listaBC = ["D-004", "pytanie-1", "pytanie-4", "pytanie-6", "pytanie-7", R.bc, R.wsp].sort().join(",");
const listaSmok = ["D-003", "D-004", "pytanie-3", R.smok1, R.smok2, R.wsp].sort().join(",");
const zamknijArkusze = () => js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); document.documentElement.classList.remove('bez-przewijania'); true`);

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
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await idz(PANEL + "/?l=" + encodeURIComponent(klucz));
  await sleep(800);
  await js(`localStorage.setItem('bc.kto', 'Karol'); sessionStorage.setItem('bc.pytano', '1'); localStorage.removeItem('bc.gra'); true`);
  await idz(PANEL + "/#/pytania");
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2000);
  await zamknijArkusze();

  // ------------------------------------------------------------ 1. gra domyślna
  sprawdz("1: przełącznik w górnym pasku z nazwą gry domyślnej", await czekajNa(`(() => { const b = document.querySelector('.gora .przelacznik-gry');
    return !!b && b.offsetParent !== null && b.textContent.includes('Blocky & Crycket'); })()`, 10000));
  sprawdz("1: lista „Do odpowiedzi” — tylko bc i wspólne", await czekajNa(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].length === 7`, 10000)
    && (await naLiscie()) === listaBC, await naLiscie());
  sprawdz("1: plakietka „+7” (sprawy w innych grach)", await czekajNa(`(document.querySelector('.gora .przelacznik-gry-inne:not([hidden])') || {}).textContent === '+7'`),
    await js(`(document.querySelector('.gora .przelacznik-gry') || {}).getAttribute && document.querySelector('.gora .przelacznik-gry').getAttribute('aria-label')`));
  sprawdz("1: plakietka Pytań liczy tylko tę grę", (await odznakaPytan()) === "7", await odznakaPytan());
  sprawdz("1: bez etykiet gry przy jednej grze", await js(`!document.querySelector('.pytania .chip-gry')`));
  sprawdz("1: telefon bez przewijania w bok", await bezPrzewijaniaWBok());
  await zrzut("1_telefon_bc");

  // ------------------------------------------------------------ 2. okno „Która gra?”
  await js(`document.querySelector('.gora .przelacznik-gry').click(); true`);
  sprawdz("2: okno z grami i „Wszystkie gry”", await czekajNa(`document.querySelectorAll('.arkusz .gra-opcja').length === 4`));
  const opcje = await js(`[...document.querySelectorAll('.arkusz .gra-opcja')].map(b => [b.dataset.gra, (b.querySelector('.gra-opcja-liczba') || {}).textContent || '0',
    b.classList.contains('wstrzymana'), b.getAttribute('aria-pressed')].join(':')).join(' ')`);
  sprawdz("2: liczby spraw i wstrzymane przygaszone",
    opcje === "bc:5:false:true smok:4:true:false pet-arena:3:true:false wszystkie:14:false:false", opcje);
  sprawdz("2: przypis o sprawach wspólnych", await js(`/Wspólne.*w każdej grze.*czeka 2/.test(document.querySelector('.arkusz .gry-przypis').textContent)`));
  sprawdz("2: okno bez przewijania w bok", await bezPrzewijaniaWBok());
  await sleep(400);                                                        // koniec animacji okna (zrzut)
  await zrzut("2_okno_gier");

  // ------------------------------------------------------------ 3. wybór gry o smoku
  await js(`document.querySelector('.arkusz .gra-opcja[data-gra="smok"]').click(); true`);
  sprawdz("3: lista smoka i wspólne", await czekajNa(`!document.querySelector('.arkusz-tlo:not(.zamykanie)')`) &&
    await czekajNa(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].map(k => k.dataset.klucz).sort().join(',') === ${JSON.stringify(listaSmok)}`),
    await naLiscie());
  sprawdz("3: nazwa gry w nagłówku i plakietka Pytań", await js(`document.querySelector('.gora .przelacznik-gry').textContent.includes('Gra o smoku')`) &&
    (await czekajNa(`(document.querySelector('[data-odznaka="pytania"]:not([hidden])') || {}).textContent === '6'`)), await odznakaPytan());
  sprawdz("3: wybór w pamięci przeglądarki", (await js(`localStorage.getItem('bc.gra')`)) === "smok");
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2000);
  sprawdz("3: po przeładowaniu dalej smok", await czekajNa(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].map(k => k.dataset.klucz).sort().join(',') === ${JSON.stringify(listaSmok)}`, 10000),
    await naLiscie());
  sprawdz("3: karta pytania bez wiersza „Gra:”", await js(`!/Gra:/.test(${karta("pytanie-3")}.textContent)`));
  await zrzut("3_smok");

  // ------------------------------------------------------------ 4. zadania w grze
  await idz(PANEL + "/#/pytania?sekcja=zadania");
  sprawdz("4: Zadania — tylko smok (i wspólne)", await czekajNa(`(() => { const t = (document.querySelector('.pytania-plan-tresc') || {}).textContent || '';
    return t.includes('Zadanie ze znacznikiem') && !t.includes('Zwykłe zadanie') && !t.includes('Pet Arena: testy') && !t.includes('#gra/'); })()`, 10000),
    await js(`((document.querySelector('.pytania-plan-tresc') || {}).textContent || '').slice(0, 200)`));
  await js(`[...document.querySelectorAll('.plan-akcje button')].find(b => /Dodaj zadanie/.test(b.textContent)).click(); true`);
  sprawdz("4: w oknie zadania wybrana gra o smoku", await czekajNa(`(document.querySelector('.arkusz .pole-gry-zadania') || {}).value === 'smok'`));
  await js(`(() => { const p = document.querySelector('.arkusz textarea'); p.value = 'Zadanie z telefonu'; p.dispatchEvent(new Event('input')); return true; })()`);
  await zrzut("4_nowe_zadanie");
  await js(`document.querySelector('.arkusz form').requestSubmit(); true`);
  let ok4 = false;
  for (let i = 0; i < 40 && !ok4; i++) {
    ok4 = czytaj("Zadania.md").includes("- [ ] Zadanie z telefonu · #gra/smok · #średni");
    if (!ok4) await sleep(200);
  }
  sprawdz("4: zapis ze znacznikiem gry w Zadania.md", ok4, czytaj("Zadania.md").split("\n").filter((l) => l.includes("telefonu")).join(" | "));
  sprawdz("4: nowe zadanie widać w grze", await czekajNa(`((document.querySelector('.pytania-plan-tresc') || {}).textContent || '').includes('Zadanie z telefonu')`));

  // ------------------------------------------------------------ 5. wszystkie gry
  await zamknijArkusze();
  await js(`window.scrollTo(0, 0); document.querySelector('.gora .przelacznik-gry').click(); true`);
  await czekajNa(`!!document.querySelector('.arkusz .gra-opcja[data-gra="wszystkie"]')`);
  await js(`document.querySelector('.arkusz .gra-opcja[data-gra="wszystkie"]').click(); true`);
  sprawdz("5: „Wszystkie gry” — 14 spraw", await czekajNa(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].length === 14`), await naLiscie());
  sprawdz("5: każda sprawa ma etykietę gry", await js(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].every(k => !!k.querySelector('.sprawa-gora .chip-gry'))`));
  sprawdz("5: etykieta Pet Areny przy pytaniu 2", await js(`${karta("pytanie-2")}.querySelector('.chip-gry').textContent === 'Pet Arena'`));
  sprawdz("5: nagłówek „Wszystkie gry”, bez plakietki +N", await js(`document.querySelector('.gora .przelacznik-gry').textContent.includes('Wszystkie gry') &&
    !document.querySelector('.gora .przelacznik-gry-inne:not([hidden])')`));
  sprawdz("5: telefon bez przewijania w bok", await bezPrzewijaniaWBok());
  await sleep(400);
  await zrzut("5_wszystkie");

  // ------------------------------------------------------------ 6. adres ?gra= i sprawa z innej gry
  await idz(PANEL + "/?gra=bc#/pytania");
  sprawdz("6: ?gra=bc ustawia wybór", await czekajNa(`[...document.querySelectorAll(${JSON.stringify(LISTA + " > [data-klucz]")})].map(k => k.dataset.klucz).sort().join(',') === ${JSON.stringify(listaBC)}`, 10000)
    && (await js(`localStorage.getItem('bc.gra')`)) === "bc", await naLiscie());
  sprawdz("6: parametr znika z paska adresu", await js(`!location.search.includes('gra=') && location.hash.startsWith('#/pytania')`), await js(`location.href`));
  await idz(PANEL + "/#/pytania?sprawa=pytanie-3");
  sprawdz("6: adres do sprawy smoka przełącza na smoka", await czekajNa(`document.querySelector('.gora .przelacznik-gry').textContent.includes('Gra o smoku') && !!${karta("pytanie-3")}`, 10000),
    await js(`document.querySelector('.gora .przelacznik-gry').textContent`));

  // ------------------------------------------------------------ 7. wyszukiwarka
  await idz(PANEL + "/?gra=bc#/pytania");
  await czekajNa(`!!${karta("pytanie-1")}`, 10000);
  await js(`(() => { const p = document.querySelector('.pytania-szukaj-pole'); p.value = 'Pet Arena'; p.dispatchEvent(new Event('input')); return true; })()`);
  sprawdz("7: wyszukiwarka — trafienia w innych grach", await czekajNa(`/W innych grach: [1-9]/.test((document.querySelector('.szukaj-inne-gry') || {}).textContent || '')`),
    await js(`document.querySelector('.pytania-szukaj-wynik').textContent`));
  await js(`document.querySelector('.szukaj-inne-gry').click(); true`);
  sprawdz("7: „pokaż wszystkie gry” z wyszukiwarki", await czekajNa(`!!${karta("pytanie-2")} && !${karta("pytanie-2")}.hidden`));
  await js(`(() => { const p = document.querySelector('.pytania-szukaj-pole'); p.value = ''; p.dispatchEvent(new Event('input')); return true; })()`);

  // ------------------------------------------------------------ 8. Pulpit i Podgląd
  await idz(PANEL + "/?gra=bc#/pulpit");
  sprawdz("8: Pulpit „Czeka na Ciebie” = 7 w bc", await czekajNa(`(document.querySelector('.karta-czeka .czeka-liczba') || {}).textContent === '7'`, 10000),
    await js(`(document.querySelector('.karta-czeka') || {}).textContent`));
  sprawdz("8: Pulpit bez sprawy smoka", await js(`!/Gra o smoku: mapa|Pet Arena: kolor/.test(document.querySelector('.karta-czeka').textContent)`));
  await idz(PANEL + "/#/podglad?zakladka=przeglad");
  sprawdz("8: Podgląd „Do przejrzenia” — 2 raporty bc i wspólne", await czekajNa(`(document.querySelector('.przeglad-licznik') || {}).textContent === '2'`, 10000),
    await js(`(document.querySelector('.przeglad-licznik') || {}).textContent`));
  await zrzut("8_podglad");

  // ------------------------------------------------------------ 9. komputer
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
  await idz(PANEL + "/#/pytania");
  sprawdz("9: komputer — przełącznik w bocznym pasku", await czekajNa(`(() => { const b = document.querySelector('.bok .przelacznik-gry');
    return !!b && b.offsetParent !== null && b.textContent.includes('Blocky & Crycket') && document.querySelector('.gora').offsetParent === null; })()`, 10000));
  sprawdz("9: komputer — nazwa gry mieści się w bocznym pasku", await js(`(() => { const n = document.querySelector('.bok .przelacznik-gry .marka-nazwa');
    return n.scrollWidth <= n.clientWidth + 1; })()`), await js(`(() => { const n = document.querySelector('.bok .przelacznik-gry .marka-nazwa'); return n.scrollWidth + '/' + n.clientWidth; })()`));
  await zrzut("9_komputer_pasek");
  await js(`document.querySelector('.bok .przelacznik-gry').click(); true`);
  sprawdz("9: komputer — okno „Która gra?”", await czekajNa(`document.querySelectorAll('.arkusz .gra-opcja').length === 4`));
  sprawdz("9: komputer bez przewijania w bok", await bezPrzewijaniaWBok());
  await sleep(400);
  await zrzut("9_komputer");
} catch (e) {
  sprawdz("przebieg", false, e && e.stack || e);
} finally {
  try { await wyslij("Browser.close"); } catch (e) { /* nic */ }
  await sleep(1000);
  try { proc.kill(); } catch (e) { /* nic */ }
  await sleep(500);
  try { fs.rmSync(profil, { recursive: true, force: true }); } catch (e) { /* plik może być jeszcze zablokowany */ }
  process.exit(bledy ? 1 : 0);
}
