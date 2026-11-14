// Próba zakładki Agent w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+, bez
// zależności). Uruchamia ją testy/test_przegladarka_agent.py na serwerze testowym z ATRAPĄ agenta
// (testy/atrapa_agenta.cjs) — nie ręcznie i nigdy z prawdziwym programem Claude Code.
//
//   node testy/przegladarka_agent.mjs <port> <katalog danych lokalnych> <przeglądarka> [katalog zrzutów]
//
// Scenariusze (komputer 1280×900, potem telefon 412×915):
//   W. pięć okien z jednym zdaniem opisu; stare rozmowy i rozmowa systemowa w oknie Ogólny;
//   B. okno Balans: nowa rozmowa, pytanie, odpowiedź atrapy na żywo; tytuł z pierwszego pytania i autor przy wiadomości;
//   L. po końcu przebiegu wiersz „gotowe w …” zostaje (lista nie wczytuje rozmowy drugi raz); długa odpowiedź
//      zwinięta, „Pokaż całość” rozwija, „Zwiń” zwija;
//   K. kroki narzędzi zwinięte do jednego wiersza z licznikiem, rozwijane kliknięciem;
//   D. usunięcie rozmowy z potwierdzeniem (Anuluj nic nie robi, Usuń kasuje plik wątku);
//   Y. rozmowa systemowa: okno potwierdzenia z ostrzeżeniem;
//   Z. zaznaczenie dwóch rozmów w oknie Świat i usunięcie ich naraz;
//   T. telefon: najpierw okna, potem rozmowy okna, potem rozmowa — z powrotem; bez przewijania w bok;
//   S. nowy widok ze starym serwerem (odpowiedzi API bez okien, podmienione przez Fetch): jedno okno Ogólny, zdanie
//      o restarcie panelu, bez usuwania, rozmowa działa jak dotąd.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const KAT_WATKOW = path.join(runtime, "agent", "watki");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly !== undefined && szczegoly !== "" ? " — " + String(szczegoly).slice(0, 220) : ""));
};

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_agent_"));
const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--window-size=1280,900", "about:blank"], { stdio: "ignore" });

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
const q = (sel) => `document.querySelector(${JSON.stringify(sel)})`;
const widoczny = (sel) => `(() => { const e = ${q(sel)}; return !!e && e.getClientRects().length > 0; })()`;
const tekst = (sel) => js(`(${q(sel)} || {}).textContent || ''`);
const klik = (sel) => js(`(() => { const e = ${q(sel)}; if (!e) return false; e.click(); return true; })()`);
const OKNO = ".arkusz-tlo:not(.zamykanie) .arkusz";
const plikWatku = (id) => fs.existsSync(path.join(KAT_WATKOW, id + ".json"));
async function napiszIWyslij(t) {
  await js(`(() => { const p = ${q(".agent-pole")}; p.value = ${JSON.stringify(t)}; p.dispatchEvent(new Event('input')); return true; })()`);
  return klik(".agent-wyslij");
}
/** Scenariusz S: odpowiedzi API jak ze starego serwera (sprzed okien) — bez okien, funkcji i nowych pól wątków. */
async function jakStarySerwer(p) {
  const b = await wyslij("Fetch.getResponseBody", { requestId: p.requestId });
  let tresc = b.base64Encoded ? Buffer.from(b.body, "base64").toString("utf8") : b.body;
  try {
    const o = JSON.parse(tresc);
    for (const k of ["okna", "funkcje", "okno_domyslne"]) delete o[k];
    for (const w of o.watki || []) for (const k of ["okno", "systemowy", "mozna_usunac"]) delete w[k];
    tresc = JSON.stringify(o);
  } catch (e) { /* nie JSON — bez zmian */ }
  await wyslij("Fetch.fulfillRequest", { requestId: p.requestId, responseCode: p.responseStatusCode || 200,
    responseHeaders: [{ name: "Content-Type", value: "application/json; charset=utf-8" }],
    body: Buffer.from(tresc, "utf8").toString("base64") });
}
async function przyciskWOknie(napis) {
  return js(`(() => { const b = [...document.querySelectorAll('${OKNO} button')].find(x => x.textContent.trim() === ${JSON.stringify(napis)});
    if (!b) return false; b.click(); return true; })()`);
}

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
    if (d.method === "Fetch.requestPaused") {
      jakStarySerwer(d.params).catch((e) => sprawdz("S: podmiana odpowiedzi", false, e && e.message));
      return;
    }
    if (d.id && oczek.has(d.id)) {
      const o = oczek.get(d.id);
      oczek.delete(d.id);
      if (d.error) o.rej(new Error(JSON.stringify(d.error)));
      else o.res(d.result);
    }
  });
  await wyslij("Page.enable");
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await idz(PANEL + "/?l=" + encodeURIComponent(klucz));                    // klucz lokalny -> ciasteczko
  await sleep(800);
  await js(`localStorage.setItem('bc.kto', 'Karol'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await idz(PANEL + "/#/agent");
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2000);
  await js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); document.documentElement.classList.remove('bez-przewijania'); true`);

  // ------------------------------------------------------------ W: okna i stare rozmowy
  sprawdz("W: pięć okien", await czekajNa(`document.querySelectorAll('.ag-okna > .ag-okno').length === 5`, 15000),
    await js(`document.querySelectorAll('.ag-okna > .ag-okno').length`));
  const nazwy = await js(`[...document.querySelectorAll('.ag-okno-nazwa')].map(e => e.textContent).join(',')`);
  sprawdz("W: nazwy okien", nazwy === "Ogólny,Balans,Świat,Modele,Wydanie", nazwy);
  sprawdz("W: każde okno ma jedno zdanie opisu", await js(`[...document.querySelectorAll('.ag-okno-opis')].every(e => e.textContent.trim().length > 15)`));
  sprawdz("W: stara rozmowa w oknie Ogólny", await czekajNa(`[...document.querySelectorAll('.ag-okno.wybrane[data-okno="ogolny"] .ag-watek')].some(w => w.textContent.includes('Rozmowa sprzed okien'))`),
    await tekst(".ag-watki"));
  sprawdz("Y: rozmowa systemowa oznaczona", await js(`[...document.querySelectorAll('.ag-watek')].some(w => w.textContent.includes('Sesja główna — notatki') && w.querySelector('.ag-systemowa'))`));
  await zrzut("W_okna_komputer");

  // ------------------------------------------------------------ B: nowa rozmowa w oknie Balans
  await klik('.ag-okno-btn[data-okno="balans"]');
  sprawdz("B: wybrane okno Balans", await czekajNa(`!!document.querySelector('.ag-okno.wybrane[data-okno="balans"] .ag-rozmowy')`));
  sprawdz("B: Balans bez rozmów", (await tekst(".ag-watki")).includes("Jeszcze nie ma rozmów"), await tekst(".ag-watki"));
  await klik(".ag-nowa");
  sprawdz("B: powitanie okna Balans", await czekajNa(`(${q(".agent-powitanie h2")} || {}).textContent === 'Okno: Balans'`), await tekst(".agent-powitanie h2"));
  await napiszIWyslij("Policz krzywą kosztów długo");
  sprawdz("B: odpowiedź atrapy", await czekajNa(`[...document.querySelectorAll('.agent-wiadomosci .wiad-agent')].some(w => w.textContent.includes('Wniosek atrapy'))`, 20000),
    await tekst(".agent-wiadomosci"));
  sprawdz("B: agent skończył", await czekajNa(`!document.querySelector('.ag.pracuje')`, 15000));
  sprawdz("B: autor przy wiadomości", (await tekst(".agent-wiadomosci .wiad-user .wiad-autor")) === "Karol", await tekst(".agent-wiadomosci .wiad-user .wiad-autor"));
  sprawdz("B: tytuł z pierwszego pytania", await czekajNa(`[...document.querySelectorAll('.ag-okno[data-okno="balans"] .ag-watek-tytul')].some(t => t.textContent === 'Policz krzywą kosztów długo')`, 10000),
    await tekst(".ag-watki"));
  sprawdz("B: kto założył na liście", (await tekst('.ag-okno[data-okno="balans"] .ag-watek-kto')).includes("założył(a): Karol"), await tekst(".ag-watek-kto"));
  sprawdz("B: tytuł w nagłówku rozmowy", (await tekst(".ag-tytul")) === "Policz krzywą kosztów długo", await tekst(".ag-tytul"));

  // ------------------------------------------------------------ L: długa odpowiedź zwinięta
  // Po „koniec” widok wczytuje rozmowę na nowo i dokłada za dymkiem agenta wiersz „gotowe w …” — dopiero wtedy
  // lista wiadomości jest ostateczna. Ostatni dymek agenta szukany po klasie (nie :last-of-type, które patrzy na
  // typ elementu, a za dymkiem stoi div wiersza systemowego).
  sprawdz("L: rozmowa wczytana po końcu", await czekajNa(`[...document.querySelectorAll('.agent-wiadomosci .wiad-system')].some(w => w.textContent.includes('gotowe w'))`, 10000),
    await tekst(".agent-wiadomosci"));
  const ODP = `[...document.querySelectorAll('.agent-wiadomosci .wiad-agent')].pop()`;
  const wOdp = (sel) => `((${ODP}) || document.createElement('div')).querySelector(${JSON.stringify(sel)})`;
  const tekstOdp = (sel) => js(`(${wOdp(sel)} || {}).textContent || ''`);
  const wysokoscOdp = () => js(`(() => { const e = ${wOdp(".wiad-tekst")}; return e ? e.getBoundingClientRect().height : -1; })()`);
  const klikOdp = (sel) => js(`(() => { const e = ${wOdp(sel)}; if (!e) return false; e.click(); return true; })()`);
  sprawdz("L: długa odpowiedź zwinięta", await js(`!!${wOdp(".wiad-tekst.ag-zwinieta")}`));
  const h0 = await wysokoscOdp();
  sprawdz("L: przycisk Pokaż całość", (await tekstOdp(".ag-pokaz-calosc")) === "Pokaż całość", await tekstOdp(".ag-pokaz-calosc"));
  sprawdz("L: klik Pokaż całość", await klikOdp(".ag-pokaz-calosc"));
  sprawdz("L: Pokaż całość rozwija", await czekajNa(`(${wOdp(".ag-pokaz-calosc")} || {}).textContent === 'Zwiń'`, 3000));
  const h1 = await wysokoscOdp();
  sprawdz("L: odpowiedź wyższa po rozwinięciu", h0 > 0 && h1 > h0 + 60, h0 + " -> " + h1);
  sprawdz("L: klik Zwiń", await klikOdp(".ag-pokaz-calosc"));
  sprawdz("L: Zwiń zwija", await czekajNa(`!!${wOdp(".wiad-tekst.ag-zwinieta")}`, 3000));

  // ------------------------------------------------------------ K: kroki narzędzi
  sprawdz("K: kroki w jednym wierszu", await js(`document.querySelectorAll('.agent-wiadomosci .ag-kroki').length === 1`),
    await js(`document.querySelectorAll('.agent-wiadomosci .ag-kroki').length`));
  sprawdz("K: licznik kroków", (await tekst(".agent-wiadomosci .ag-kroki-licznik")) === "Kroki agenta: 3", await tekst(".ag-kroki-licznik"));
  sprawdz("K: lista kroków zwinięta", !(await js(widoczny(".agent-wiadomosci .ag-kroki-lista"))));
  await klik(".agent-wiadomosci .ag-kroki-nagl");
  sprawdz("K: kliknięcie rozwija kroki", await czekajNa(`document.querySelectorAll('.agent-wiadomosci .ag-kroki-lista:not([hidden]) .ag-krok').length === 3`));
  await zrzut("B_balans_odpowiedz");

  // ------------------------------------------------------------ D: usunięcie z potwierdzeniem
  const idBalans = await js(`(document.querySelector('.ag-okno[data-okno="balans"] .ag-watek') || {dataset: {}}).dataset.id || ''`);
  sprawdz("D: plik rozmowy istnieje", !!idBalans && plikWatku(idBalans), idBalans);
  await klik(`.ag-watek[data-id="${idBalans}"] .ag-watek-usun`);
  sprawdz("D: okno potwierdzenia", await czekajNa(`!!document.querySelector('${OKNO} .ag-potwierdz') && document.querySelector('${OKNO}').textContent.includes('Usunąć rozmowę?')`));
  await przyciskWOknie("Anuluj");
  await czekajNa(`!document.querySelector('.arkusz-tlo')`);
  sprawdz("D: Anuluj nic nie usuwa", plikWatku(idBalans) && await js(`!!document.querySelector('.ag-watek[data-id="${idBalans}"]')`));
  await klik(`.ag-watek[data-id="${idBalans}"] .ag-watek-usun`);
  await czekajNa(`!!document.querySelector('${OKNO} .ag-potwierdz')`);
  await przyciskWOknie("Usuń");
  sprawdz("D: rozmowa znika z listy", await czekajNa(`!document.querySelector('.ag-watek[data-id="${idBalans}"]')`));
  await sleep(300);
  sprawdz("D: plik wątku usunięty", !plikWatku(idBalans));
  sprawdz("D: rozmowa po prawej wraca do powitania", await czekajNa(`!!document.querySelector('.agent-wiadomosci .agent-powitanie')`));

  // ------------------------------------------------------------ Y: rozmowa systemowa — ostrzeżenie
  await klik('.ag-okno-btn[data-okno="ogolny"]');
  await czekajNa(`!!document.querySelector('.ag-okno.wybrane[data-okno="ogolny"] .ag-watek')`);
  await js(`(() => { const w = [...document.querySelectorAll('.ag-watek')].find(x => x.querySelector('.ag-systemowa'));
    w && w.querySelector('.ag-watek-usun').click(); return !!w; })()`);
  sprawdz("Y: ostrzeżenie przy rozmowie systemowej", await czekajNa(`!!document.querySelector('${OKNO} .ag-ostrzezenie')`),
    await js(`(document.querySelector('${OKNO}') || {}).textContent || ''`));
  await zrzut("Y_systemowa");
  await przyciskWOknie("Anuluj");
  await czekajNa(`!document.querySelector('.arkusz-tlo')`);

  // ------------------------------------------------------------ Z: kilka naraz
  const nowe = await js(`Promise.all([1, 2].map(() => fetch('/api/agent/watki', { method: 'POST', headers: { 'X-BC': '1',
    'Content-Type': 'application/json', 'X-BC-Kto': 'Karol' }, body: JSON.stringify({ okno: 'swiat' }) }).then(r => r.json()).then(j => j.id)))`);
  await klik('.ag-okno-btn[data-okno="swiat"]');
  sprawdz("Z: dwie rozmowy w oknie Świat", await czekajNa(`document.querySelectorAll('.ag-okno[data-okno="swiat"] .ag-watek').length === 2`, 20000),
    await js(`document.querySelectorAll('.ag-okno[data-okno="swiat"] .ag-watek').length`));
  await klik(".ag-zaznacz");
  await czekajNa(`document.querySelectorAll('.ag-watek-pole').length === 2`);
  for (const i of [0, 1]) {                                     // lista rysuje się na nowo po każdym kliknięciu
    await js(`document.querySelectorAll('.ag-watek-pole')[${i}].click(); true`);
    await sleep(100);
  }
  sprawdz("Z: licznik zaznaczonych", await czekajNa(`(${q(".ag-zazn-licznik")} || {}).textContent === 'Zaznaczono: 2'`), await tekst(".ag-zazn-licznik"));
  await klik(".ag-usun-zaznaczone");
  sprawdz("Z: potwierdzenie dla dwóch", await czekajNa(`(document.querySelector('${OKNO}') || {textContent: ''}).textContent.includes('Usunąć 2 rozmowy?')`));
  await przyciskWOknie("Usuń");
  sprawdz("Z: obie usunięte", await czekajNa(`document.querySelectorAll('.ag-okno[data-okno="swiat"] .ag-watek').length === 0`) &&
    nowe.every((id) => !plikWatku(id)), JSON.stringify(nowe));

  // ------------------------------------------------------------ T: telefon
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await js(`localStorage.removeItem('bc.agent.watek'); true`);
  await idz(PANEL + "/#/pulpit");
  await idz(PANEL + "/#/agent");
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2000);
  sprawdz("T: telefon zaczyna od okien", await czekajNa(`!!document.querySelector('.ag.krok-okna')`, 10000) && await js(widoczny('.ag-okno-btn[data-okno="wydanie"]')));
  sprawdz("T: rozmowa ukryta na kroku okien", !(await js(widoczny(".ag-czat"))));
  await zrzut("T_telefon_okna");
  await klik('.ag-okno-btn[data-okno="balans"]');
  sprawdz("T: lista rozmów okna", await czekajNa(`!!document.querySelector('.ag.krok-rozmowy')`) && await js(widoczny(".ag-nowa")) &&
    !(await js(widoczny('.ag-okno-btn[data-okno="wydanie"]'))) && (await tekst(".ag-rozmowy-tytul")) === "Balans");
  sprawdz("T: powrót do okien widoczny", await js(widoczny(".ag-rozmowy .ag-wstecz")));
  await zrzut("T_telefon_rozmowy");
  await klik(".ag-nowa");
  sprawdz("T: rozmowa na całym ekranie", await czekajNa(`!!document.querySelector('.ag.krok-rozmowa')`) && await js(widoczny(".agent-pole")) &&
    !(await js(widoczny(".ag-bok"))));
  sprawdz("T: bez przewijania w bok", await js(`document.documentElement.scrollWidth <= window.innerWidth + 1`),
    await js(`document.documentElement.scrollWidth + ' / ' + window.innerWidth`));
  await zrzut("T_telefon_rozmowa");
  await klik(".ag-czat-nagl .ag-wstecz");
  sprawdz("T: powrót do rozmów", await czekajNa(`!!document.querySelector('.ag.krok-rozmowy')`));
  await klik(".ag-rozmowy .ag-wstecz");
  sprawdz("T: powrót do okien", await czekajNa(`!!document.querySelector('.ag.krok-okna')`));

  // ------------------------------------------------------------ S: nowy widok ze starym serwerem (przed restartem)
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await wyslij("Fetch.enable", { patterns: [{ urlPattern: "*/api/agent/stan*", requestStage: "Response" },
    { urlPattern: "*/api/agent/watki", requestStage: "Response" }] });
  await js(`localStorage.setItem('bc.agent.okno', 'balans'); localStorage.removeItem('bc.agent.watek'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await sleep(2500);
  sprawdz("S: jedno okno Ogólny", await czekajNa(`document.querySelectorAll('.ag-okna > .ag-okno').length === 1`, 10000) &&
    (await tekst(".ag-okno-nazwa")) === "Ogólny", await js(`document.querySelectorAll('.ag-okna > .ag-okno').length`));
  sprawdz("S: zdanie o restarcie panelu", (await tekst(".ag-uwaga")).includes("po restarcie panelu"), await tekst(".ag-uwaga"));
  sprawdz("S: wszystkie rozmowy na liście", await czekajNa(`[...document.querySelectorAll('.ag-watek')].some(w => w.textContent.includes('Rozmowa sprzed okien'))`));
  sprawdz("S: bez usuwania", await js(`!document.querySelector('.ag-watek-usun') && document.querySelector('.ag-zaznacz').hidden`));
  await klik(".ag-nowa");
  await napiszIWyslij("Krótko: test starego serwera");
  sprawdz("S: rozmowa działa jak dotąd", await czekajNa(`[...document.querySelectorAll('.agent-wiadomosci .wiad-agent')].some(w => w.textContent.includes('Krótka odpowiedź atrapy'))`, 20000),
    await tekst(".agent-wiadomosci"));
  await wyslij("Fetch.disable");
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
