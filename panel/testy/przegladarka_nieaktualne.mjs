// Próba „Nieaktualne” w zakładce Pytania (Edge/Chrome bez okna, protokół DevTools; sam Node 22+, bez zależności).
// Uruchamia ją testy/test_przegladarka_nieaktualne.py na serwerze testowym z kopią sejfu — nie ręcznie.
//
//   node testy/przegladarka_nieaktualne.mjs <port> <katalog danych lokalnych> <katalog Produkcja> <przeglądarka> [zrzuty]
//
// Klucze (lokalny, zatwierdzania) czyta z plików danych lokalnych serwera testowego i nigdzie ich nie wypisuje.
// Scenariusze:
//   1. pytanie: „Powód” odsłania pole, „Nieaktualne” zapisuje „nieaktualne — powód”, karta przechodzi do historii
//      z etykietą „nieaktualne”;
//   2. decyzja: jedno kliknięcie = „🗃️ nieaktualna · … · oznaczył: Paweł <data>”, w historii etykieta i „Przywróć”;
//   3. raport: decyzja „nieaktualne”, w historii etykieta;
//   4. pytanie z decyzją z wiersza „Rozstrzyga:” — zdejmuje też tę decyzję;
//   5. karta potwierdzenia nie ma „Nieaktualne” ani pola wyboru;
//   6. „Zaznacz kilka”: trzy sprawy (pytanie, decyzja, raport) naraz z jednym powodem;
//   7. konflikt wersji w trybie zaznaczania: sprawa zostaje zaznaczona z powodem w karcie, druga próba się udaje;
//   8. wyszukiwarka znajduje po słowie „nieaktualne”;
//   9. „Przywróć” wraca decyzję na listę „Do odpowiedzi”;
//  10. serwer bez tej funkcji (plan bez pola `funkcje`): przycisk przy decyzji mówi, że zadziała po restarcie panelu.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, produkcja, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const kluczGd = fs.readFileSync(path.join(runtime, "klucz_gd.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const czytaj = (n) => fs.readFileSync(path.join(produkcja, n), "utf8");
const pisz = (n, t) => fs.writeFileSync(path.join(produkcja, n), t, "utf8");
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 240) : ""));
};
const t = new Date();
const DZIS = t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0");
const E = "\u{1F5C3}️";

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_n_"));
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
const toasty = () => js(`[...document.querySelectorAll('.toast')].map(t => t.textContent).join(' | ')`);
async function zbierzToasty(wzor, ms = 6000) {
  let tt = "";
  const koniec = Date.now() + ms;
  while (Date.now() < koniec && !wzor.test(tt)) {
    tt += " " + (await toasty());
    await sleep(200);
  }
  return tt;
}
const statusDecyzji = (ident) => {
  const linie = czytaj("Rejestr decyzji.md").split("\n");
  return linie[linie.findIndex((l) => l.startsWith("### " + ident)) + 1] || "";
};
const odswiezWTle = () => js(`document.dispatchEvent(new Event('visibilitychange')); true`);
const karta = (k) => `document.getElementById(${JSON.stringify("sprawa-" + k)})`;
const LISTA = ".pytania .lista-pytan:not(.zwarta) > .kolejka-lista";
const wHistorii = (k) => `!!(${karta(k)} && ${karta(k)}.closest('#pytania-historia'))`;
const wLiscie = (k) => `!!(${karta(k)} && ${karta(k)}.closest(${JSON.stringify(LISTA)}))`;
const etykiety = (k) => `[...(${karta(k)} || document.createElement('i')).querySelectorAll('.sprawa-gora .sprawa-meta')].map(e => e.textContent).join(',')`;
const klik = (k, sel) => js(`(() => { const b = ${karta(k)} && ${karta(k)}.querySelector(${JSON.stringify(sel)}); b && b.click(); return !!b; })()`);
const statusRaportu = (id) => js(`fetch('/api/raporty/${id}').then(r => r.json()).then(j => j.status)`);

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
  await idz(PANEL + "/?l=" + encodeURIComponent(klucz) + "&gd=" + encodeURIComponent(kluczGd));
  await sleep(1000);
  await js(`localStorage.setItem('bc.kto', 'Paweł'); sessionStorage.setItem('bc.pytano', '1'); true`);
  const nowyRaport = (tytul) => js(`fetch('/api/raporty', { method: 'POST', headers: { 'X-BC': '1', 'Content-Type': 'application/json',
    'X-BC-Kto': encodeURIComponent('Paweł') }, body: JSON.stringify({ tytul: ${JSON.stringify(tytul)}, opis_md: 'Opis raportu.',
    rodzaj: 'wdrozenie', kto: 'Claude (test)' }) }).then(r => r.json()).then(j => j.id)`);
  const r1 = await nowyRaport("Stary most");
  const r2 = await nowyRaport("Stara brama");
  sprawdz("przygotowanie: dwa raporty czekają", !!r1 && !!r2, r1 + " " + r2);
  await idz(PANEL + "/#/pytania");
  await wyslij("Page.reload", { ignoreCache: true });                      // aplikacja startuje już z imieniem
  await sleep(2000);
  await js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); document.documentElement.classList.remove('bez-przewijania'); true`);
  sprawdz("lista gotowa (pytania, decyzje, raporty, potwierdzenie)", await czekajNa(`${wLiscie("pytanie-2")} && ${wLiscie("D-003")} &&
    ${wLiscie("raport-" + r1)} && ${wLiscie("D-009")}`, 12000));

  // ------------------------------------------------------------ 1. pytanie z powodem
  sprawdz("1: przycisk „Nieaktualne” w karcie pytania", await js(`!!${karta("pytanie-2")}.querySelector('.nieaktualne-przycisk')`));
  await klik("pytanie-2", ".nieaktualne-powod-przycisk");
  sprawdz("1: „Powód” odsłania pole w karcie (bez okna)", await czekajNa(`(() => { const p = ${karta("pytanie-2")}.querySelector('.nieaktualne-powod');
    return !!p && !p.hidden && document.activeElement === p && !document.querySelector('.arkusz-tlo'); })()`));
  await js(`(() => { const p = ${karta("pytanie-2")}.querySelector('.nieaktualne-powod'); p.value = 'omówione na sesji';
    p.dispatchEvent(new Event('input')); return true; })()`);
  await zrzut("1_powod");
  await klik("pytanie-2", ".nieaktualne-przycisk");
  sprawdz("1: karta zniknęła z listy i jest w historii z etykietą „nieaktualne”", await czekajNa(`!${wLiscie("pytanie-2")} && ${wHistorii("pytanie-2")} &&
    ${etykiety("pytanie-2")}.includes('nieaktualne')`), await js(etykiety("pytanie-2")));
  sprawdz("1: wiersz odpowiedzi w sejfie", czytaj("Pytania otwarte.md").includes("- Paweł (klucz zatwierdzania, " + DZIS + "): nieaktualne — omówione na sesji"),
    czytaj("Pytania otwarte.md").split("## 2.")[1]);

  // ------------------------------------------------------------ 2. decyzja jednym kliknięciem
  sprawdz("2: przycisk „Nieaktualne” przy decyzji", await js(`!!${karta("D-003")}.querySelector('.decyzja-akcje .nieaktualne-przycisk')`));
  await klik("D-003", ".nieaktualne-przycisk");
  for (let i = 0; i < 40 && !statusDecyzji("D-003").startsWith(E); i++) await sleep(150);
  sprawdz("2: status w Rejestrze", statusDecyzji("D-003") === E + " nieaktualna · technika · zaproponował: Claude Code · oznaczył: Paweł " + DZIS,
    statusDecyzji("D-003"));
  sprawdz("2: w historii z etykietą „nieaktualna” i „Przywróć”", await czekajNa(`!${wLiscie("D-003")} && ${wHistorii("D-003")} &&
    ${etykiety("D-003")}.includes('nieaktualna') && !!${karta("D-003")}.querySelector('.przywroc-decyzje')`), await js(etykiety("D-003")));
  sprawdz("2: ślad w Dzienniku", czytaj("Dziennik zmian.md").includes("- Paweł (klucz zatwierdzania): decyzja D-003 oznaczona jako nieaktualna ([[Rejestr decyzji]])"));

  // ------------------------------------------------------------ 3. raport
  sprawdz("3: przycisk „Nieaktualne” przy raporcie", await js(`!!${karta("raport-" + r1)}.querySelector('.raport-akcje .nieaktualne-przycisk')`));
  await klik("raport-" + r1, ".raport-akcje .nieaktualne-przycisk");
  sprawdz("3: raport w historii z etykietą „nieaktualne”", await czekajNa(`!${wLiscie("raport-" + r1)} && ${wHistorii("raport-" + r1)} &&
    ${etykiety("raport-" + r1)}.includes('nieaktualne')`), await js(etykiety("raport-" + r1)));
  sprawdz("3: status raportu", (await statusRaportu(r1)) === "nieaktualne");

  // ------------------------------------------------------------ 4. pytanie z decyzją z „Rozstrzyga:”
  await klik("pytanie-1", ".nieaktualne-przycisk");
  for (let i = 0; i < 40 && !statusDecyzji("D-002").startsWith(E); i++) await sleep(150);
  sprawdz("4: pytanie w historii, decyzja D-002 też nieaktualna i nie wyskoczyła na listę", await czekajNa(`${wHistorii("pytanie-1")} &&
    ${etykiety("pytanie-1")}.includes('nieaktualne') && !${wLiscie("D-002")}`) && statusDecyzji("D-002").startsWith(E + " nieaktualna"),
    statusDecyzji("D-002"));
  sprawdz("4: uzasadnienie decyzji wskazuje pytanie", czytaj("Rejestr decyzji.md").includes("Uzasadnienie — Paweł, " + DZIS + ": pytanie #1 oznaczone jako nieaktualne"));

  // ------------------------------------------------------------ 5. karta potwierdzenia
  sprawdz("5: karta potwierdzenia bez „Nieaktualne”", await js(`${wLiscie("D-009")} && !${karta("D-009")}.querySelector('.nieaktualne-przycisk')`));

  // ------------------------------------------------------------ 6. tryb zaznaczania
  await js(`document.querySelector('.pytania .zaznacz-kilka').click(); true`);
  sprawdz("6: „Zaznacz kilka” pokazuje pola wyboru i pasek", await czekajNa(`!document.querySelector('.pytania .zaznaczanie-pasek').hidden &&
    !!${karta("pytanie-3")}.querySelector('.sprawa-zaznacz input') && !!${karta("D-005")}.querySelector('.sprawa-zaznacz input') &&
    !!${karta("raport-" + r2)}.querySelector('.sprawa-zaznacz input')`));
  sprawdz("6: karta potwierdzenia nie daje się zaznaczyć", await js(`!${karta("D-009")}.querySelector('.sprawa-zaznacz')`));
  for (const k of ["pytanie-3", "D-005", "raport-" + r2]) await klik(k, ".sprawa-zaznacz input");
  sprawdz("6: pasek liczy zaznaczone", await czekajNa(`document.querySelector('.pytania .zaznaczanie-liczba strong').textContent === '3' &&
    !document.querySelector('.pytania .zaznaczanie-oznacz').disabled`), await js(`document.querySelector('.pytania .zaznaczanie-liczba').textContent`));
  await js(`(() => { const p = document.querySelector('.pytania .zaznaczanie-powod'); p.value = 'po sesji 14.11'; return true; })()`);
  await zrzut("6_zaznaczone");
  await js(`document.querySelector('.pytania .zaznaczanie-oznacz').click(); true`);
  const t6 = await zbierzToasty(/Oznaczono jako nieaktualne: \d/, 12000);
  sprawdz("6: komunikat „3 z 3”", /Oznaczono jako nieaktualne: 3 z 3/.test(t6), t6);
  sprawdz("6: trzy sprawy w historii", await czekajNa(`${wHistorii("pytanie-3")} && ${wHistorii("D-005")} && ${wHistorii("raport-" + r2)}`),
    await js(`[${["pytanie-3", "D-005", "raport-" + r2].map(wHistorii).join(",")}].join(',')`));
  sprawdz("6: wspólny powód zapisany", czytaj("Pytania otwarte.md").includes("): nieaktualne — po sesji 14.11") &&
    czytaj("Rejestr decyzji.md").includes("Uzasadnienie — Paweł, " + DZIS + ": po sesji 14.11") && statusDecyzji("D-005").startsWith(E));
  const r2d = await js(`fetch('/api/raporty/${r2}').then(r => r.json()).then(j => j.status + '|' + (j.decyzja && j.decyzja.komentarz))`);
  sprawdz("6: raport z komentarzem", r2d === "nieaktualne|po sesji 14.11", r2d);
  await zrzut("6_po");

  // ------------------------------------------------------------ 7. konflikt wersji: zostaje zaznaczone z powodem
  await czekajNa(`!!${karta("pytanie-4")} && !!${karta("pytanie-4")}.querySelector('.sprawa-zaznacz input')`);
  await klik("pytanie-4", ".sprawa-zaznacz input");
  pisz("Pytania otwarte.md", czytaj("Pytania otwarte.md").replace("Treść czwartego.", "Treść czwartego (agent coś dopisał)."));
  await js(`document.querySelectorAll('.toast').forEach(t => t.remove()); document.querySelector('.pytania .zaznaczanie-oznacz').click(); true`);
  const t7 = await zbierzToasty(/Oznaczono jako nieaktualne: \d+ z 1/, 12000);
  sprawdz("7: komunikat „0 z 1”, sprawa zostaje zaznaczona", /0 z 1/.test(t7), t7);
  sprawdz("7: w karcie powód (konflikt wersji) i zaznaczone pole", await czekajNa(`${wLiscie("pytanie-4")} &&
    (${karta("pytanie-4")}.querySelector('.sprawa-blad-zbiorczy') || {}).textContent?.includes('konflikt wersji') &&
    ${karta("pytanie-4")}.querySelector('.sprawa-zaznacz input').checked`), await js(`(${karta("pytanie-4")} || {}).textContent`));
  await zrzut("7_konflikt");
  await js(`document.querySelector('.pytania .zaznaczanie-oznacz').click(); true`);
  sprawdz("7: druga próba się udaje", await czekajNa(`${wHistorii("pytanie-4")}`, 10000));
  await js(`document.querySelector('.pytania .zaznacz-kilka').click(); true`);
  sprawdz("7: „Zakończ zaznaczanie” chowa pasek i pola", await czekajNa(`document.querySelector('.pytania .zaznaczanie-pasek').hidden &&
    !document.querySelector('.pytania .sprawa-zaznacz')`));

  // ------------------------------------------------------------ 8. wyszukiwarka
  await js(`(() => { const p = document.querySelector('.pytania-szukaj-pole'); p.value = 'nieaktualne'; p.dispatchEvent(new Event('input')); return true; })()`);
  const kl = ["pytanie-1", "pytanie-2", "pytanie-3", "pytanie-4", "D-002", "D-003", "D-005", "raport-" + r1, "raport-" + r2];
  sprawdz("8: „nieaktualne” znajduje pytania, decyzje i raporty w historii (bez zatwierdzonej i zastąpionej)", await czekajNa(`(() => {
    if (!document.querySelector('.pytania-szukaj-wynik').textContent.includes('Znaleziono')) return false;
    const h = [...document.querySelectorAll('#pytania-historia .historia-lista > .sprawa')].map(k => k.id.replace('sprawa-', ''));
    return ${JSON.stringify(kl)}.every(k => h.includes(k)) && !h.includes('D-001') && !h.includes('D-004'); })()`),
    await js(`[...document.querySelectorAll('#pytania-historia .historia-lista > .sprawa')].map(k => k.id).join(',')`));
  sprawdz("8: karta potwierdzenia na liście ukryta (nie pasuje)", await czekajNa(`${karta("D-009")}.hidden`, 3000),
    await js(`(() => { const k = ${karta("D-009")}; return [k.hidden, k.parentNode && k.parentNode.className, k._sprawa && k._sprawa.szukaj].join(' | '); })()`));
  await zrzut("8_szukaj");
  await js(`(() => { const p = document.querySelector('.pytania-szukaj-pole'); p.value = ''; p.dispatchEvent(new Event('input')); return true; })()`);

  // ------------------------------------------------------------ 9. „Przywróć”
  await czekajNa(`!!${karta("D-003")} && !!${karta("D-003")}.querySelector('.przywroc-decyzje')`);
  await klik("D-003", ".przywroc-decyzje");
  sprawdz("9: D-003 wraca na listę „Do odpowiedzi”", await czekajNa(`${wLiscie("D-003")}`) && statusDecyzji("D-003").startsWith("🕓 do decyzji"),
    statusDecyzji("D-003"));

  // ------------------------------------------------------------ 10. serwer bez tej funkcji
  await js(`(() => {
    const oryginal = window.fetch;
    window.fetch = async (...a) => {
      const r = await oryginal(...a);
      if (!String(a[0]).includes('/api/sejf/plan')) return r;
      const j = await r.clone().json();
      delete j.funkcje;
      return new Response(JSON.stringify(j), { status: r.status, headers: r.headers });
    };
    return true; })()`);
  await odswiezWTle();
  await sleep(1500);
  const przed = statusDecyzji("D-003");
  await czekajNa(`!!(${karta("D-003")} && ${karta("D-003")}.querySelector('.nieaktualne-przycisk'))`);
  await klik("D-003", ".nieaktualne-przycisk");
  const t10 = await zbierzToasty(/po restarcie panelu/, 6000);
  sprawdz("10: stary serwer — przycisk mówi, że zadziała po restarcie", /po restarcie panelu/.test(t10), t10);
  await sleep(500);
  sprawdz("10: nic nie zapisano, karta zostaje", statusDecyzji("D-003") === przed && (await js(wLiscie("D-003"))), statusDecyzji("D-003"));
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
