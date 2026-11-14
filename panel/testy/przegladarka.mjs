// Próba interfejsu Planu w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+, bez
// zależności). Uruchamia ją testy/test_przegladarka.py na serwerze testowym z tymczasowym sejfem — nie ręcznie.
//
//   node testy/przegladarka.mjs <port> <katalog danych lokalnych> <katalog Produkcja> <przeglądarka> [katalog zrzutów]
//
// Klucze (lokalny, zatwierdzania — plik klucz_gd.txt) czyta z plików danych lokalnych serwera testowego i nigdzie
// ich nie wypisuje.
// Scenariusze z wrogiego przeglądu zapisu do sejfu:
//   A. okno zatwierdzania decyzji wysyła wersję Rejestru z chwili otwarcia — gdy odpytywanie w tle przerysuje listę
//      nową treścią, „Zatwierdzam” nic nie zapisuje (409) i zamyka okno;
//   B. podwójny Ctrl+Enter w odpowiedzi = jedno żądanie, bez „ktoś zmienił plik” i bez przywróconego szkicu;
//   C. odhaczenie przeżywa cudzą zmianę Zadań w ciągu 5 s (jedno ponowienie z nową wersją);
//   D. podwójny klik w pole wyboru nie robi „odhacz i od razu cofnij”.
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
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly ? " — " + String(szczegoly).slice(0, 200) : ""));
};

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_"));
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
const statusDecyzji = (ident) => {
  const linie = czytaj("Rejestr decyzji.md").split("\n");
  return linie[linie.findIndex((l) => l.startsWith("### " + ident)) + 1] || "";
};

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
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await idz(PANEL + "/?l=" + encodeURIComponent(klucz) + "&gd=" + encodeURIComponent(kluczGd));   // klucze -> ciasteczka
  await sleep(1000);
  // imię przed startem aplikacji (inaczej otwiera się okno „Jak masz na imię?”), potem pełne przeładowanie
  await js(`localStorage.setItem('bc.kto', 'Paweł'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2000);
  await js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); true`);

  // ------------------------------------------------------------ A
  await idz(PANEL + "/#/plan?zakladka=decyzje");
  await czekajNa(`!!document.querySelector('.decyzja-akcje .przycisk.sukces')`);
  const ident = await js(`(() => { const b = document.querySelector('.decyzja-akcje .przycisk.sukces');
    const k = b.closest('.karta'); b.click(); return k.querySelector('.decyzja-id').textContent.trim(); })()`);
  await czekajNa(`!!document.querySelector('.arkusz form')`);
  await zrzut("A1_okno_decyzji");
  const rejestr = czytaj("Rejestr decyzji.md");
  const rx = new RegExp("(### " + ident + "[^\\n]*\\n[^\\n]*\\n)");
  pisz("Rejestr decyzji.md", rejestr.replace(rx, "$1PRZEPISANE PRZEZ AGENTA w trakcie czytania.\n"));
  await sleep(21000);                                                         // > 20 s: następne odpytanie czyta sejf
  await js(`document.dispatchEvent(new Event('visibilitychange')); true`);   // powrót do karty
  sprawdz("A: lista za oknem przerysowana nową treścią",
    await czekajNa(`document.querySelector('.plan-tresc').textContent.includes('PRZEPISANE PRZEZ AGENTA')`));
  const ja = await js(`fetch('/api/ja', { headers: { 'X-BC-Kto': encodeURIComponent('Paweł') } }).then(r => r.json()).then(j => j.game_director && j.decydent)`);
  sprawdz("A: przeglądarka ma klucz zatwierdzania (decydent)", ja === true);
  await js(`document.querySelector('.arkusz form button[type=submit]').click(); true`);
  let tA = "";
  for (let i = 0; i < 30 && !/zmienił się|zatwierdzona|imię/.test(tA); i++) {
    tA += " " + (await toasty());                                            // toast znika po kilku sekundach
    await sleep(200);
  }
  await zrzut("A2_po_zatwierdzam");
  sprawdz("A: decyzja nie zatwierdzona na nieprzeczytanej treści", !statusDecyzji(ident).startsWith("✅"), statusDecyzji(ident));
  sprawdz("A: komunikat o zmianie Rejestru", /zmienił się, odkąd otworzyłeś/.test(tA), tA);
  pisz("Rejestr decyzji.md", rejestr);

  // ------------------------------------------------------------ B
  await idz(PANEL + "/#/plan?zakladka=pytania");
  await czekajNa(`!!document.querySelector('.karta.pytanie.otwarte textarea')`);
  const tekst = "Odpowiedź z próby podwójnego Ctrl+Enter " + Date.now();
  await js(`(() => { const p = document.querySelector('.karta.pytanie.otwarte textarea');
    p.value = ${JSON.stringify(tekst)}; p.dispatchEvent(new Event('input'));
    const e = () => new KeyboardEvent('keydown', { key: 'Enter', ctrlKey: true, bubbles: true, cancelable: true });
    p.dispatchEvent(e()); p.dispatchEvent(e()); return true; })()`);
  await sleep(2500);
  const pytania = czytaj("Pytania otwarte.md");
  sprawdz("B: dokładnie jedna odpowiedź w sejfie", pytania.split(tekst).length - 1 === 1);
  const tB = await toasty();
  sprawdz("B: bez „Ktoś zmienił”", !/Ktoś zmienił/.test(tB), tB);
  sprawdz("B: szkic nie wraca do pola",
    !(await js(`[...document.querySelectorAll('.karta.pytanie textarea')].some(p => p.value.includes(${JSON.stringify(tekst)}))`)));
  sprawdz("B: znacznik klucza zatwierdzania w podpisie", pytania.includes("- Paweł (klucz zatwierdzania, "));

  // ------------------------------------------------------------ C / D
  await idz(PANEL + "/#/plan?zakladka=zadania");
  await czekajNa(`!!document.querySelector('.pole-wyboru-przycisk')`);
  const pierwsze = await js(`(() => { const b = document.querySelector('.pole-wyboru-przycisk');
    const t = b.closest('li').querySelector('.wiersz-tekst').textContent; b.click(); return t; })()`);
  await sleep(800);
  pisz("Zadania.md", czytaj("Zadania.md") + "\n");                          // cudza zmiana w ciągu 5 s
  await sleep(6500);
  const zrobione = () => czytaj("Zadania.md").split(/^## .*Zrobione.*$/m).slice(1).join("\n");
  sprawdz("C: odhaczenie zapisane mimo cudzej zmiany", zrobione().includes(pierwsze.trim()), pierwsze);
  const drugie = "Coś na później";                                           // zadanie z Backlogu w danych testowych
  const klik = `(() => { const b = [...document.querySelectorAll('.pole-wyboru-przycisk')].find(x =>
    x.closest('li').querySelector('.wiersz-tekst').textContent.trim() === ${JSON.stringify(drugie)}); b && b.click(); return !!b; })()`;
  sprawdz("D: zadanie do podwójnego kliku jest na liście", await js(klik));
  await sleep(120);
  await js(klik);
  await sleep(300);
  sprawdz("D: podwójny klik zostawia odhaczenie",
    await js(`[...document.querySelectorAll('.pole-wyboru-przycisk')].some(x => x.getAttribute('aria-checked') === 'true')`));
  await sleep(6000);
  sprawdz("D: zapisane w sejfie", zrobione().includes(drugie.trim()), drugie);
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
