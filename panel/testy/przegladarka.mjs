// Próba zakładki Pytania w prawdziwej przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+, bez
// zależności). Uruchamia ją testy/test_przegladarka.py na serwerze testowym z tymczasowym sejfem — nie ręcznie.
//
//   node testy/przegladarka.mjs <port> <katalog danych lokalnych> <katalog Produkcja> <przeglądarka> [katalog zrzutów]
//
// Klucze (lokalny, zatwierdzania — plik klucz_gd.txt) czyta z plików danych lokalnych serwera testowego i nigdzie
// ich nie wypisuje. Strona: zmienna BC_TEST_STRONA (domyślnie „/”).
// Scenariusze:
//   N. nawigacja: Pulpit, Pytania, Sesja, Podgląd, Agent, Sieć, Assety, Analityka, Ustawienia; na dole telefonu
//      Pulpit, Pytania, Sesja, Podgląd, Więcej;
//   R. stare adresy #/decyzje, #/plan?zakladka=…, #/raporty i #/raporty/<id> prowadzą do zakładki Pytania
//      (właściwa część, karta albo pełny raport); plakietka liczy listę „Do odpowiedzi”;
//   O. lista aktywnych osób pokazuje osobę (znaczek w górnym pasku telefonu i lewy dolny róg);
//   U. „Pokaż więcej” rozwija opis w pełnym raporcie (błąd z 14.11); na liście raport ma dwa pierwsze zdania opisu,
//      a resztę za „Pokaż szczegóły” / „Ukryj szczegóły”;
//   K. karta pytania jest krótka i lekka: punkty z góry treści widoczne, „Szczegóły:” i dopisek zwinięte za
//      „Pokaż szczegóły”, wiersza „Rozstrzyga:” nie ma w tekście, karty bez kolorowego paska z lewej;
//   Z. historia „Odpowiedziane” pokazuje 12 pozycji, „Pokaż więcej” dokłada, „Pokaż mniej” wraca do 12;
//   A. okno zatwierdzania decyzji wysyła wersję Rejestru z chwili otwarcia — gdy odświeżanie w tle przerysuje kartę
//      nową treścią, „Tak” nic nie zapisuje (409) i zamyka okno;
//   T. decyzja pokazana jako pytanie „Czy zatwierdzamy: …?” i zatwierdzona przyciskiem Tak — przechodzi do historii;
//   P. potwierdzanie przez drugą osobę (D-043): moja decyzja czeka w historii ze znacznikiem „czeka na potwierdzenie:
//      Karol”, a decyzja Karola jest w MOJEJ kolejce jako „Karol … zatwierdził: … — zgadzasz się?”; „Zgoda”
//      dopisuje drugi podpis w Rejestrze i karta przechodzi do historii z dwoma podpisami;
//   B. podwójny Ctrl+Enter w odpowiedzi = jedno żądanie, bez „ktoś zmienił plik” i bez przywróconego szkicu; karta
//      pytania znika z listy i jest w historii „Odpowiedziane”;
//   S. ciche odświeżanie nie kasuje wpisanego tekstu (karta zostaje, z informacją o zmianie); gdy nowa treść (data)
//      przesuwa kartę na liście, karta z kursorem stoi w miejscu i nie traci fokusu, a przeskakuje po końcu pisania;
//   G. „Na sesję główną” przenosi kartę do grupy „Odłożone”;
//   E. zatwierdzenie decyzji z wiersza „Rozstrzyga:” — pytanie samo znika z listy, odpowiedź jest w sejfie;
//   F. „Akceptuję” przy raporcie na liście;
//   H. „Zmień decyzję” przy raporcie w historii — przyciski zostają po cichym odświeżeniu, „Do poprawy” zapisuje;
//   W. wyszukiwarka znajduje raport po słowie z tytułu (na liście i w historii) i ukrywa resztę; słowa statusu
//      („do poprawy”, „zatwierdzona”) znajdują sprawy o tym statusie;
//   C. odhaczenie przeżywa cudzą zmianę Zadań w ciągu 5 s (jedno ponowienie z nową wersją);
//   D. podwójny klik w pole wyboru nie robi „odhacz i od razu cofnij”.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, produkcja, przegladarka, zrzuty] = process.argv.slice(2);
const PANEL = "http://127.0.0.1:" + port;
const STRONA = PANEL + "/" + String(process.env.BC_TEST_STRONA || "").replace(/^\/+/, "");
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
async function zbierzToasty(wzor, ms = 6000) {
  let t = "";
  const koniec = Date.now() + ms;
  while (Date.now() < koniec && !wzor.test(t)) {
    t += " " + (await toasty());                                // toast znika po kilku sekundach
    await sleep(200);
  }
  return t;
}
const statusDecyzji = (ident) => {
  const linie = czytaj("Rejestr decyzji.md").split("\n");
  return linie[linie.findIndex((l) => l.startsWith("### " + ident)) + 1] || "";
};
const odswiezWTle = () => js(`document.dispatchEvent(new Event('visibilitychange')); true`);   // jak powrót do karty
const karta = (klucz) => `document.getElementById(${JSON.stringify("sprawa-" + klucz)})`;
const OKNO = ".arkusz-tlo:not(.zamykanie) .arkusz";                          // otwarte okno (nie to, które się zamyka)
const LISTA = ".pytania .lista-pytan:not(.zwarta) > .kolejka-lista";           // „Do odpowiedzi” (bez odłożonych)
const wHistorii = (klucz) => `!!(${karta(klucz)} && ${karta(klucz)}.closest('#pytania-historia'))`;
const wLiscie = (klucz) => `!!(${karta(klucz)} && ${karta(klucz)}.closest(${JSON.stringify(LISTA)}))`;
const zamknijOkno = () => js(`(() => { const b = document.querySelector('${OKNO} .arkusz-nagl button'); b && b.click(); return !!b; })()`);

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
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });   // zdarzenia focus/blur jak w oknie z fokusem
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 412, height: 915, deviceScaleFactor: 2, mobile: true });
  await idz(PANEL + "/?l=" + encodeURIComponent(klucz) + "&gd=" + encodeURIComponent(kluczGd));   // klucze -> ciasteczka
  await sleep(1000);
  // imię przed startem aplikacji (inaczej otwiera się okno „Jak masz na imię?”), raporty czekające na akceptację
  await js(`localStorage.setItem('bc.kto', 'Paweł'); sessionStorage.setItem('bc.pytano', '1'); true`);
  const nowyRaport = (tytul, opis) => js(`fetch('/api/raporty', { method: 'POST', headers: { 'X-BC': '1', 'Content-Type': 'application/json',
    'X-BC-Kto': encodeURIComponent('Paweł') }, body: JSON.stringify({ tytul: ${JSON.stringify(tytul)}, opis_md: ${JSON.stringify(opis)},
    rodzaj: 'wdrozenie', kto: 'Claude (test)' }) }).then(r => r.json()).then(j => j.id)`);
  const raport = await nowyRaport("Raport do akceptacji", "Nowy most w wiosce.");
  const dlugi = await nowyRaport("Porównanie rycerzy w trzech wersjach",
    Array.from({ length: 14 }, (_, i) => "Akapit " + (i + 1) + " opisu porównania.").join("\n\n"));
  sprawdz("przygotowanie: dwa raporty czekają", !!raport && !!dlugi, raport + " " + dlugi);
  await wyslij("Page.reload", { ignoreCache: true });                      // aplikacja startuje już z imieniem
  await sleep(2000);
  await js(`document.querySelectorAll('.arkusz-tlo').forEach(a => a.remove()); document.documentElement.classList.remove('bez-przewijania'); true`);

  // ------------------------------------------------------------ N: nazwy w nawigacji
  const nawBok = await js(`[...document.querySelectorAll('.nav-bok .nav-link .nav-tekst')].map(e => e.textContent).join(',')`);
  sprawdz("N: nawigacja boczna", nawBok === "Pulpit,Pytania,Sesja,Podgląd,Agent,Sieć,Assety,Analityka,Ustawienia", nawBok);
  const nawDol = await js(`[...document.querySelectorAll('.nav-dol .nav-link .nav-tekst')].map(e => e.textContent).join(',')`);
  sprawdz("N: dolny pasek telefonu", nawDol === "Pulpit,Pytania,Sesja,Podgląd,Więcej", nawDol);

  // ------------------------------------------------------------ R: stare adresy
  await idz(STRONA + "#/plan?zakladka=zadania");
  sprawdz("R: #/plan?zakladka=zadania → Pytania, Plan otwarty na Zadaniach", await czekajNa(`location.hash === '#/pytania?sekcja=zadania' &&
    !!document.querySelector('.pytania-plan[open] .pytania-plan-tresc .sekcja-zadan')`), await js(`location.hash`));
  await idz(STRONA + "#/decyzje?sekcja=rejestr");
  sprawdz("R: #/decyzje?sekcja=rejestr → Pytania, historia", await czekajNa(`location.hash === '#/pytania?sekcja=historia' &&
    !!document.querySelector('#pytania-historia')`), await js(`location.hash`));
  await idz(STRONA + "#/decyzje");
  sprawdz("R: #/decyzje → Pytania", await czekajNa(`location.hash === '#/pytania' && !!document.querySelector('${LISTA} .sprawa')`), await js(`location.hash`));
  await idz(STRONA + "#/raporty");
  sprawdz("R: #/raporty → Pytania z raportami na liście", await czekajNa(`location.hash === '#/pytania' && !!${karta("raport-" + raport)}`),
    await js(`location.hash`));
  await idz(STRONA + "#/raporty/" + dlugi);
  sprawdz("R: #/raporty/<id> → karta na liście i pełny raport w oknie", await czekajNa(`location.hash.startsWith('#/pytania?raport=') &&
    ${wLiscie("raport-" + dlugi)} && !!document.querySelector('${OKNO} .raport.tryb-pelna[data-id="${dlugi}"]')`), await js(`location.hash`));
  await zrzut("R_pelny_raport");
  // U (pełny raport): „Pokaż więcej” w oknie
  const wOknie = `document.querySelector('${OKNO} .raport.tryb-pelna')`;
  const hOkno0 = await js(`${wOknie}.querySelector('.zwijany-opis').getBoundingClientRect().height`);
  await js(`${wOknie}.querySelector('.pokaz-wiecej').click(); true`);
  await sleep(250);
  const hOkno1 = await js(`${wOknie}.querySelector('.zwijany-opis').getBoundingClientRect().height`);
  sprawdz("U: Pokaż więcej rozwija opis w pełnym raporcie", hOkno1 > hOkno0 + 40, hOkno0 + " -> " + hOkno1);
  await zamknijOkno();
  await czekajNa(`!document.querySelector('.arkusz-tlo')`);
  sprawdz("R: plakietka Pytania liczy listę „Do odpowiedzi”", await czekajNa(`(() => { const o = document.querySelector('.nav-dol [data-odznaka="pytania"]');
    return o && !o.hidden && Number(o.textContent) === document.querySelectorAll('${LISTA} > .sprawa').length; })()`),
    await js(`(document.querySelector('.nav-dol [data-odznaka="pytania"]') || {}).textContent + ' / ' + document.querySelectorAll('${LISTA} > .sprawa').length`));

  // ------------------------------------------------------------ O: aktywne osoby
  sprawdz("O: znaczek osób w górnym pasku", await czekajNa(`(() => { const z = document.querySelector('.gora-obecni'); return z && !z.hidden && Number(z.textContent) >= 1; })()`, 25000));
  sprawdz("O: lewy dolny róg ma osobę i zakładkę", await czekajNa(`[...document.querySelectorAll('.bok-obecni .obecny')].some(o => o.textContent.includes('Paweł (Ty)') && o.textContent.includes('Pytania'))`, 8000),
    await js(`(document.querySelector('.bok-obecni') || {}).textContent`));
  await js(`document.querySelector('.gora-obecni').click(); true`);
  sprawdz("O: arkusz z listą osób", await czekajNa(`!!document.querySelector('.arkusz .obecni-arkusz .obecny')`));
  await zrzut("O_obecni");
  await zamknijOkno();
  await czekajNa(`!document.querySelector('.arkusz-tlo')`);

  // ------------------------------------------------------------ U: raport na liście — dwa pierwsze zdania, reszta zwinięta
  const kD = karta("raport-" + dlugi);
  await czekajNa(`!!(${kD} && ${kD}.querySelector('details.sprawa-szczegoly'))`);
  sprawdz("U: raport na liście pokazuje początek opisu, resztę zwiniętą", await js(`(() => { const k = ${kD};
    const kr = k.querySelector('.sprawa-krotko'); const d = k.querySelector('details.sprawa-szczegoly');
    return !!kr && kr.textContent.includes('Akapit 1') && !kr.textContent.includes('Akapit 3') && !d.open &&
      d.textContent.includes('Akapit 14') && d.querySelector('summary').textContent.trim() === 'Pokaż szczegóły'; })()`),
    await js(`(${kD} || {}).textContent`));
  const trescD = `${kD}.querySelector('.sprawa-szczegoly-tresc').getBoundingClientRect().height`;
  await js(`${kD}.querySelector('details.sprawa-szczegoly > summary').click(); true`);
  await sleep(250);
  sprawdz("U: „Pokaż szczegóły” rozwija opis raportu na liście", (await js(trescD)) > 100 &&
    (await js(`${kD}.querySelector('details.sprawa-szczegoly > summary').textContent.trim()`)) === "Ukryj szczegóły", await js(trescD));
  await zrzut("U_rozwiniety");
  await js(`${kD}.querySelector('details.sprawa-szczegoly > summary').click(); true`);
  await sleep(250);
  sprawdz("U: „Ukryj szczegóły” zwija opis", await js(`!${kD}.querySelector('details.sprawa-szczegoly').open`));

  // ------------------------------------------------------------ K: krótka, lekka karta pytania
  const k4 = karta("pytanie-4");
  await czekajNa(`!!${k4}`);
  sprawdz("K: karta pytania pokazuje punkty z góry treści", await js(`(() => { const kr = ${k4}.querySelector('.sprawa-krotko');
    return !!kr && kr.querySelectorAll('li').length === 2 && !kr.textContent.includes('Długi opis') && !kr.textContent.includes('dopisek'); })()`),
    await js(`(${k4} || {}).textContent`));
  sprawdz("K: „Szczegóły:” i dopisek zwinięte za „Pokaż szczegóły”", await js(`(() => { const d = ${k4}.querySelector('details.sprawa-szczegoly');
    return !!d && !d.open && d.textContent.includes('Długi opis') && d.textContent.includes('dopisek zwinięty') &&
      !d.textContent.includes('Szczegóły:') && d.querySelector('summary').textContent.trim() === 'Pokaż szczegóły' &&
      !d.querySelector('.sprawa-szczegoly-tresc').checkVisibility(); })()`),
    await js(`(() => { const d = ${k4}.querySelector('details.sprawa-szczegoly'); return d ? [d.open, d.textContent, d.querySelector('.sprawa-szczegoly-tresc').checkVisibility()].join(' | ') : 'brak'; })()`));
  await js(`${k4}.querySelector('details.sprawa-szczegoly > summary').click(); true`);
  sprawdz("K: przycisk rozwija szczegóły", await czekajNa(`(() => { const d = ${k4}.querySelector('details.sprawa-szczegoly'); const t = d.querySelector('.sprawa-szczegoly-tresc');
    return d.open && t.checkVisibility() && t.getBoundingClientRect().height > 10 && d.querySelector('summary').textContent.trim() === 'Ukryj szczegóły'; })()`));
  sprawdz("K: wiersz „Rozstrzyga:” nie jest pokazywany jako tekst", await js(`!${karta("pytanie-1")}.querySelector('.sprawa-krotko').textContent.includes('Rozstrzyga')`));
  sprawdz("K: karty bez kolorowego paska z lewej", await js(`[...document.querySelectorAll('${LISTA} > .sprawa')].every(k => {
    const s = getComputedStyle(k); return parseFloat(s.borderLeftWidth) <= 1 && s.borderLeftColor === s.borderRightColor; })`),
    await js(`[...document.querySelectorAll('${LISTA} > .sprawa')].map(k => k.id + ':' + getComputedStyle(k).borderLeftWidth).join(',')`));
  await js(`${karta("pytanie-1")}.scrollIntoView({ block: 'start' }); true`);
  await zrzut("K_karta_pytania");
  await js(`window.scrollTo(0, 0); true`);

  // ------------------------------------------------------------ A: okno decyzji a odświeżenie w tle
  await czekajNa(`!!(${karta("D-003")} && ${karta("D-003")}.querySelector('.decyzja-akcje .przycisk.sukces'))`);
  await zrzut("A0_lista");
  await js(`${karta("D-003")}.querySelector('.decyzja-akcje .przycisk.sukces').click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form')`);
  await zrzut("A1_okno_decyzji");
  const rejestr = czytaj("Rejestr decyzji.md");
  pisz("Rejestr decyzji.md", rejestr.replace(/(### D-003[^\n]*\n[^\n]*\n)/, "$1PRZEPISANE PRZEZ AGENTA w trakcie czytania.\n"));
  await sleep(300);
  await odswiezWTle();
  sprawdz("A: karta za oknem przerysowana nową treścią",
    await czekajNa(`${karta("D-003")} && ${karta("D-003")}.textContent.includes('PRZEPISANE PRZEZ AGENTA')`));
  const ja = await js(`fetch('/api/ja', { headers: { 'X-BC-Kto': encodeURIComponent('Paweł') } }).then(r => r.json()).then(j => j.game_director && j.decydent)`);
  sprawdz("A: przeglądarka ma klucz zatwierdzania (decydent)", ja === true);
  await js(`document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  const tA = await zbierzToasty(/zmienił się|zatwierdzona|imię/);
  await zrzut("A2_po_tak");
  sprawdz("A: decyzja nie zatwierdzona na nieprzeczytanej treści", !statusDecyzji("D-003").startsWith("✅"), statusDecyzji("D-003"));
  sprawdz("A: komunikat o zmianie Rejestru", /zmienił się, odkąd otworzyłeś/.test(tA), tA);
  pisz("Rejestr decyzji.md", rejestr);
  await sleep(300);
  await odswiezWTle();
  // lista musi już znać przywrócony Rejestr — inaczej „Tak” słusznie odmówi (wersja sprzed przywrócenia)
  await czekajNa(`!!${karta("D-003")} && !${karta("D-003")}.textContent.includes('PRZEPISANE PRZEZ AGENTA')`);

  // ------------------------------------------------------------ T: decyzja jako pytanie, „Tak”
  await czekajNa(`!document.querySelector('.arkusz-tlo') && !!(${karta("D-005")} && ${karta("D-005")}.querySelector('.decyzja-akcje .przycisk.sukces'))`);
  const tytulT = await js(`${karta("D-005")}.querySelector('.sprawa-tytul').textContent`);
  const przyciskiT = await js(`[...${karta("D-005")}.querySelectorAll('.decyzja-akcje .przycisk')].map(b => b.textContent.trim()).join(',')`);
  sprawdz("T: decyzja pokazana jako pytanie z Tak / Nie", tytulT === "Czy zatwierdzamy: Ostatnia?" && /^Tak,Nie/.test(przyciskiT) &&
    (await js(`${karta("D-005")}.querySelector('.sprawa-zrodlo').textContent`)) === "decyzja D-005", tytulT + " / " + przyciskiT);
  await js(`${karta("D-005")}.querySelector('.decyzja-akcje .przycisk.sukces').click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form')`);
  await js(`document.querySelector('${OKNO} textarea').value = 'Tak, bierzemy'; document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  sprawdz("T: po „Tak” karta zniknęła z listy i jest w historii", await czekajNa(`!${wLiscie("D-005")} && ${wHistorii("D-005")}`),
    await js(`(${karta("D-005")} || {}).className`));
  sprawdz("T: decyzja zatwierdzona w Rejestrze", statusDecyzji("D-005").startsWith("✅"), statusDecyzji("D-005"));

  // ------------------------------------------------------------ P: potwierdzenie decyzji drugiej osoby (D-043)
  const tp = new Date();
  const dzisP = tp.getFullYear() + "-" + String(tp.getMonth() + 1).padStart(2, "0") + "-" + String(tp.getDate()).padStart(2, "0");
  sprawdz("P: moja decyzja (D-005) w historii ze znacznikiem „czeka na potwierdzenie: Karol”, nie w mojej kolejce",
    await czekajNa(`${wHistorii("D-005")} && ${karta("D-005")}.textContent.includes('Czeka na potwierdzenie: Karol')`),
    await js(`(${karta("D-005")} || {}).textContent`));
  pisz("Rejestr decyzji.md", czytaj("Rejestr decyzji.md").replace("---\n*Stopka rejestru.*",
    "### D-009 Decyzja Karola\n✅ zatwierdzona · test · zdecydował: Karol Balucki " + dzisP + "\nOpis decyzji Karola.\n\n---\n*Stopka rejestru.*"));
  await sleep(300);
  await odswiezWTle();
  sprawdz("P: decyzja Karola jest w mojej kolejce jako pytanie z Zgoda / Brak zgody / Przedyskutuj", await czekajNa(`${wLiscie("D-009")} &&
    ${karta("D-009")}.querySelector('.sprawa-tytul').textContent === 'Karol Balucki zatwierdził: Decyzja Karola — zgadzasz się?' &&
    [...${karta("D-009")}.querySelectorAll('.potwierdzenie-akcje .przycisk')].map(b => b.textContent.trim()).join(',') === 'Zgoda,Brak zgody,Przedyskutuj'`),
    await js(`(${karta("D-009")} || {}).textContent`));
  await zrzut("P0_potwierdzenie");
  await js(`${karta("D-009")}.querySelector('.potwierdzenie-akcje [data-odpowiedz="zgoda"]').click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form')`);
  await js(`document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  const dwaPodpisy = "zdecydował: Karol Balucki " + dzisP + " · potwierdził: Paweł " + dzisP;
  for (let i = 0; i < 50 && !statusDecyzji("D-009").includes(dwaPodpisy); i++) await sleep(150);
  sprawdz("P: po „Zgoda” drugi podpis w Rejestrze", statusDecyzji("D-009").endsWith(dwaPodpisy), statusDecyzji("D-009"));
  sprawdz("P: karta zniknęła z kolejki i jest w historii z dwoma podpisami", await czekajNa(`!${wLiscie("D-009")} && ${wHistorii("D-009")} &&
    ${karta("D-009")}.textContent.includes('Dwa podpisy: Karol Balucki')`), await js(`(${karta("D-009")} || {}).textContent`));
  await zrzut("P1_dwa_podpisy");

  // ------------------------------------------------------------ B: podwójny Ctrl+Enter
  await czekajNa(`!document.querySelector('.arkusz-tlo') && !!(${karta("pytanie-2")} && ${karta("pytanie-2")}.querySelector('textarea'))`);
  const tekst = "Odpowiedź z próby podwójnego Ctrl+Enter " + Date.now();
  await js(`(() => { const p = ${karta("pytanie-2")}.querySelector('textarea');
    p.focus(); p.value = ${JSON.stringify(tekst)}; p.dispatchEvent(new Event('input'));
    const e = () => new KeyboardEvent('keydown', { key: 'Enter', ctrlKey: true, bubbles: true, cancelable: true });
    p.dispatchEvent(e()); p.dispatchEvent(e()); return true; })()`);
  await sleep(2500);
  const pytania = czytaj("Pytania otwarte.md");
  sprawdz("B: dokładnie jedna odpowiedź w sejfie", pytania.split(tekst).length - 1 === 1);
  const tB = await toasty();
  sprawdz("B: bez „Ktoś zmienił”", !/Ktoś zmienił/.test(tB), tB);
  sprawdz("B: szkic nie wraca do pola",
    !(await js(`[...document.querySelectorAll('textarea')].some(p => p.value.includes(${JSON.stringify(tekst)}))`)));
  sprawdz("B: znacznik klucza zatwierdzania w podpisie", pytania.includes("- Paweł (klucz zatwierdzania, "));
  sprawdz("B: odpowiedziane pytanie zniknęło z listy i jest w historii z odpowiedzią",
    await czekajNa(`!${wLiscie("pytanie-2")} && ${wHistorii("pytanie-2")} && ${karta("pytanie-2")}.textContent.includes(${JSON.stringify(tekst)})`));

  // ------------------------------------------------------------ S: ciche odświeżanie a wpisany tekst
  // Agent dopisuje do treści dzisiejszą datę — w danych karta przeskakuje wyżej, ale ta, w której ktoś pisze, stoi
  // w miejscu i nie traci kursora (błąd z przeglądu 14.11: przeniesienie węzła zdejmowało fokus).
  const kolejnosc = () => js(`[...document.querySelectorAll('${LISTA} > .sprawa')].map(k => k.id.replace('sprawa-', '')).join(',')`);
  const przed = await kolejnosc();
  const ind = (lista, k) => lista.split(",").indexOf(k);
  sprawdz("S: przygotowanie — pytanie 3 jest pod pytaniem 1", ind(przed, "pytanie-3") > ind(przed, "pytanie-1") && ind(przed, "pytanie-1") >= 0, przed);
  const teraz = new Date();
  const dzis = teraz.getFullYear() + "-" + String(teraz.getMonth() + 1).padStart(2, "0") + "-" + String(teraz.getDate()).padStart(2, "0");
  const szkic = "Szkic, którego nie wolno zgubić";
  await js(`(() => { const p = ${karta("pytanie-3")}.querySelector('textarea'); p.focus(); p.value = ${JSON.stringify(szkic)};
    p.dispatchEvent(new Event('input')); return true; })()`);
  pisz("Pytania otwarte.md", czytaj("Pytania otwarte.md").replace("Treść trzeciego.", "Treść trzeciego, zmieniona przez agenta " + dzis + "."));
  await sleep(300);
  await odswiezWTle();
  sprawdz("S: karta dostaje informację o zmianie", await czekajNa(`!!${karta("pytanie-3")}.querySelector('.sprawa-zmiana')`));
  sprawdz("S: wpisany tekst i kursor zostają", await js(`(() => { const p = ${karta("pytanie-3")}.querySelector('textarea');
    return p.value === ${JSON.stringify(szkic)} && document.activeElement === p; })()`),
    await js(`(() => { const a = document.activeElement; return a ? a.tagName + ' / ' + ((a.closest && a.closest('.sprawa')) || {}).id : 'brak'; })()`));
  const wTrakcie = await kolejnosc();
  sprawdz("S: karta z kursorem stoi na swoim miejscu", ind(wTrakcie, "pytanie-3") === ind(przed, "pytanie-3"), przed + " → " + wTrakcie);
  await zrzut("S_zmiana_w_trakcie_pisania");
  await js(`(() => { const p = ${karta("pytanie-3")}.querySelector('textarea'); p.focus(); p.value = ''; p.dispatchEvent(new Event('input'));
    p.blur(); return true; })()`);
  sprawdz("S: po wyjściu z pustego pola karta pokazuje nową treść",
    await czekajNa(`${karta("pytanie-3")} && ${karta("pytanie-3")}.textContent.includes('zmieniona przez agenta') && !${karta("pytanie-3")}.querySelector('.sprawa-zmiana')`),
    await js(`(() => { const k = ${karta("pytanie-3")}; return [k && k.textContent.slice(0, 160), document.activeElement && document.activeElement.tagName].join(' / '); })()`));
  sprawdz("S: po końcu pisania karta z dzisiejszą datą przeskakuje nad pytanie 1", await czekajNa(`(() => {
    const l = [...document.querySelectorAll('${LISTA} > .sprawa')].map(k => k.id);
    return l.indexOf('sprawa-pytanie-3') >= 0 && l.indexOf('sprawa-pytanie-3') < l.indexOf('sprawa-pytanie-1'); })()`), await kolejnosc());

  // ------------------------------------------------------------ G: na sesję główną
  await js(`[...${karta("pytanie-3")}.querySelectorAll('button')].find(b => b.textContent.includes('Na sesję')).click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form')`);
  await js(`document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  sprawdz("G: karta przeszła do „Odłożone na sesję główną”",
    await czekajNa(`!!(${karta("pytanie-3")} && ${karta("pytanie-3")}.closest('.kolejka-odlozone')) && !${wLiscie("pytanie-3")}`));
  sprawdz("G: temat w agendzie sesji", /\(pytanie 3\)/.test(czytaj("Sesje główne.md")));
  await zrzut("G_odlozone");

  // ------------------------------------------------------------ E: decyzja rozstrzyga pytanie
  await czekajNa(`!document.querySelector('.arkusz-tlo')`);                  // poprzednie okno już zamknięte
  await czekajNa(`!!(${karta("pytanie-1")} && ${karta("pytanie-1")}.querySelector('.decyzja-akcje .przycisk.sukces'))`);
  sprawdz("E: decyzja z wiersza „Rozstrzyga” w karcie pytania jako pytanie Tak / Nie",
    await js(`${karta("pytanie-1")}.querySelector('.sprawa-dec-tytul').textContent === 'Czy zatwierdzamy: Propozycja z linkiem?' && !${karta("D-002")}`));
  await js(`${karta("pytanie-1")}.querySelector('.decyzja-akcje .przycisk.sukces').click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form')`);
  await js(`document.querySelector('${OKNO} textarea').value = 'Krótko'; document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  sprawdz("E: pytanie samo zniknęło z listy", await czekajNa(`!${wLiscie("pytanie-1")}`));
  sprawdz("E: decyzja zatwierdzona w Rejestrze", statusDecyzji("D-002").startsWith("✅"), statusDecyzji("D-002"));
  sprawdz("E: odpowiedź pod pytaniem w sejfie", czytaj("Pytania otwarte.md").includes("): rozstrzygnięte decyzjami: D-002 zatwierdzona („Krótko”)"));
  sprawdz("E: informacja nad listą", await czekajNa(`(() => { const i = document.querySelector('.pytania .kolejka-info'); return i && !i.hidden && i.textContent.includes('#1'); })()`));
  sprawdz("E: pytanie w historii z automatyczną odpowiedzią", await czekajNa(`${wHistorii("pytanie-1")} && ${karta("pytanie-1")}.textContent.includes('rozstrzygnięte decyzjami')`));
  await zrzut("E_samo_rozstrzygniete");

  // ------------------------------------------------------------ F: akceptacja raportu
  sprawdz("F: raport jako pytanie „Czy akceptujesz: …?”", (await js(`${karta("raport-" + raport)}.querySelector('.sprawa-tytul').textContent`)) === "Czy akceptujesz: Raport do akceptacji?");
  await js(`${karta("raport-" + raport)}.querySelector('.raport-akcje .przycisk.sukces').click(); true`);
  sprawdz("F: raport zaakceptowany, zniknął z listy i jest w historii", await czekajNa(`!${wLiscie("raport-" + raport)} && ${wHistorii("raport-" + raport)}`));
  const st = await js(`fetch('/api/raporty/${raport}').then(r => r.json()).then(j => j.status)`);
  sprawdz("F: status raportu w panelu", st === "zaakceptowane", st);

  // ------------------------------------------------------------ H: „Zmień decyzję” w historii a ciche odświeżenie
  const kR = karta("raport-" + raport);
  await czekajNa(`${wHistorii("raport-" + raport)} && !!${kR}.querySelector('.zmien-decyzje')`);
  await js(`${kR}.querySelector('.zmien-decyzje').click(); true`);
  sprawdz("H: „Zmień decyzję” pokazuje Akceptuję / Do poprawy w karcie listy (id, klasy „sprawa”)", await czekajNa(`${wHistorii("raport-" + raport)} &&
    ${kR}.classList.contains('sprawa') && !!${kR}.querySelector('.raport-akcje .przycisk.sukces') && !${kR}.querySelector('.zmien-decyzje')`),
    await js(`(${kR} || {}).className`));
  pisz("Pytania otwarte.md", czytaj("Pytania otwarte.md").replace("Treść drugiego.", "Treść drugiego, uzupełniona w tle."));
  await sleep(300);
  await odswiezWTle();
  await czekajNa(`!!${karta("pytanie-2")} && ${karta("pytanie-2")}.textContent.includes('uzupełniona w tle')`);   // odświeżenie przyszło
  sprawdz("H: po cichym odświeżeniu przyciski Akceptuję / Do poprawy dalej są", await js(`!!${kR} && ${wHistorii("raport-" + raport)} &&
    !!${kR}.querySelector('.raport-akcje .przycisk.sukces') && !${kR}.querySelector('.zmien-decyzje')`),
    await js(`(${kR} || {}).textContent`));
  await js(`[...${kR}.querySelectorAll('.raport-akcje .przycisk.grozny')].find(b => b.textContent.includes('Do poprawy')).click(); true`);
  await czekajNa(`!!document.querySelector('${OKNO} form textarea')`);
  await js(`document.querySelector('${OKNO} textarea').value = 'Most jest za wąski'; document.querySelector('${OKNO} form button[type=submit]').click(); true`);
  sprawdz("H: zmiana na „do poprawy” z historii", await czekajNa(`!document.querySelector('.arkusz-tlo') && ${wHistorii("raport-" + raport)} &&
    !!${kR}.querySelector('.zmien-decyzje') && ${kR}.textContent.includes('do poprawy')`), await js(`(${kR} || {}).textContent`));
  const stH = await js(`fetch('/api/raporty/${raport}').then(r => r.json()).then(j => j.status)`);
  sprawdz("H: status raportu po zmianie decyzji", stH === "do_poprawy", stH);

  // ------------------------------------------------------------ W: wyszukiwarka
  const szukaj = (t) => js(`(() => { const p = document.querySelector('.pytania-szukaj-pole'); p.value = ${JSON.stringify(t)};
    p.dispatchEvent(new Event('input')); return true; })()`);
  await szukaj("akceptacji");
  sprawdz("W: słowo z tytułu znajduje przyjęty raport w historii, resztę historii chowa", await czekajNa(`(() => {
    const h = [...document.querySelectorAll('#pytania-historia .historia-lista > .sprawa')];
    return h.length === 1 && h[0].id === ${JSON.stringify("sprawa-raport-" + raport)}; })()`),
    await js(`[...document.querySelectorAll('#pytania-historia .historia-lista > .sprawa')].map(k => k.id).join(',')`));
  await szukaj("rycerzy");
  sprawdz("W: słowo z tytułu znajduje czekający raport, inne karty na liście są ukryte", await czekajNa(`(() => {
    const widoczne = [...document.querySelectorAll('${LISTA} > .sprawa')].filter(k => !k.hidden);
    return widoczne.length === 1 && widoczne[0].id === ${JSON.stringify("sprawa-raport-" + dlugi)} &&
      document.querySelector('.pytania-szukaj-wynik').textContent.includes('1 do odpowiedzi'); })()`),
    await js(`document.querySelector('.pytania-szukaj-wynik').textContent`));
  await zrzut("W_szukanie");
  const wHist = `[...document.querySelectorAll('#pytania-historia .historia-lista > .sprawa')].map(k => k.id)`;
  await szukaj("do poprawy");
  sprawdz("W: słowo statusu „do poprawy” znajduje raport odesłany do poprawy", await czekajNa(`(() => { const h = ${wHist};
    return h.length === 1 && h[0] === ${JSON.stringify("sprawa-raport-" + raport)}; })()`), await js(`${wHist}.join(',')`));
  await szukaj("zatwierdzona");
  sprawdz("W: słowo statusu „zatwierdzona” znajduje zatwierdzone decyzje, bez zastąpionej", await czekajNa(`(() => { const h = ${wHist};
    return h.includes('sprawa-D-005') && h.includes('sprawa-D-002') && !h.includes('sprawa-D-004') && !h.some(k => k.startsWith('sprawa-raport-')); })()`),
    await js(`${wHist}.join(',')`));
  await szukaj("");
  sprawdz("W: puste pole pokazuje znów wszystko", await czekajNa(`[...document.querySelectorAll('${LISTA} > .sprawa')].every(k => !k.hidden) &&
    document.querySelectorAll('#pytania-historia .historia-lista > .sprawa').length >= 4`));

  // ------------------------------------------------------------ Z: historia „Odpowiedziane” — Pokaż więcej / Pokaż mniej
  pisz("Pytania otwarte.md", czytaj("Pytania otwarte.md") + Array.from({ length: 16 }, (_, i) =>
    "\n## " + (40 + i) + ". Dawne pytanie " + (40 + i) + "\nTreść dawnego pytania.\n**Odpowiedź:**\n- Karol (2026-11-01): tak.\n").join(""));
  await sleep(300);
  await odswiezWTle();
  const kartyHist = `document.querySelectorAll('#pytania-historia .historia-lista > .sprawa').length`;
  const przyciskHist = (t) => `[...document.querySelectorAll('#pytania-historia .historia-wiecej button')].find(b => b.textContent.startsWith(${JSON.stringify(t)}))`;
  sprawdz("Z: historia pokazuje 12 pozycji i „Pokaż więcej”", await czekajNa(`Number(document.querySelector('#pytania-historia .kolejka-nagl .chip').textContent) >= 16 &&
    ${kartyHist} === 12 && !!${przyciskHist("Pokaż więcej")} && !${przyciskHist("Pokaż mniej")}`, 10000),
    await js(`${kartyHist} + ' / ' + document.querySelector('#pytania-historia .kolejka-nagl .chip').textContent`));
  const wszystkieHist = await js(`Number(document.querySelector('#pytania-historia .kolejka-nagl .chip').textContent)`);
  await js(`${przyciskHist("Pokaż więcej")}.click(); true`);
  sprawdz("Z: „Pokaż więcej” dokłada pozycje i daje „Pokaż mniej”", await czekajNa(`${kartyHist} === ${Math.min(wszystkieHist, 32)} && !!${przyciskHist("Pokaż mniej")}`),
    await js(kartyHist) + " z " + wszystkieHist);
  await js(`document.getElementById('pytania-historia').scrollIntoView({ block: 'start' }); true`);
  await zrzut("Z_historia_wiecej");
  await js(`${przyciskHist("Pokaż mniej")}.click(); true`);
  sprawdz("Z: „Pokaż mniej” wraca do 12 pozycji", await czekajNa(`${kartyHist} === 12 && !!${przyciskHist("Pokaż więcej")} && !${przyciskHist("Pokaż mniej")}`),
    await js(kartyHist));

  // ------------------------------------------------------------ C / D: zadania (zwijany Plan)
  await idz(STRONA + "#/pytania?sekcja=zadania");
  await czekajNa(`!!document.querySelector('.pytania-plan-tresc .pole-wyboru-przycisk')`);
  const pierwsze = await js(`(() => { const b = document.querySelector('.pytania-plan-tresc .pole-wyboru-przycisk');
    const t = b.closest('li').querySelector('.wiersz-tekst').textContent; b.click(); return t; })()`);
  await sleep(800);
  pisz("Zadania.md", czytaj("Zadania.md") + "\n");                          // cudza zmiana w ciągu 5 s
  await sleep(6500);
  const zrobione = () => czytaj("Zadania.md").split(/^## .*Zrobione.*$/m).slice(1).join("\n");
  sprawdz("C: odhaczenie zapisane mimo cudzej zmiany", zrobione().includes(pierwsze.trim()), pierwsze);
  const drugie = "Coś na później";                                           // zadanie z Backlogu w danych testowych
  const klik = `(() => { const b = [...document.querySelectorAll('.pytania-plan-tresc .pole-wyboru-przycisk')].find(x =>
    x.closest('li').querySelector('.wiersz-tekst').textContent.trim() === ${JSON.stringify(drugie)}); b && b.click(); return !!b; })()`;
  sprawdz("D: zadanie do podwójnego kliku jest na liście", await js(klik));
  await sleep(120);
  await js(klik);
  await sleep(300);
  sprawdz("D: podwójny klik zostawia odhaczenie",
    await js(`[...document.querySelectorAll('.pytania-plan-tresc .pole-wyboru-przycisk')].some(x => x.getAttribute('aria-checked') === 'true')`));
  await sleep(6000);
  sprawdz("D: zapisane w sejfie", zrobione().includes(drugie.trim()), drugie);

  // ------------------------------------------------------------ Pulpit: Czeka na Ciebie i przejście do karty
  await idz(STRONA + "#/pulpit");
  sprawdz("Pulpit: Czeka na Ciebie z przejściem do karty", await czekajNa(`!!document.querySelector('.karta-czeka .sprawa-wiersz') &&
    !document.querySelector('.karta-czeka').textContent.includes('Raport do akceptacji')`));   // już po odświeżeniu (raport przyjęty w F)
  await zrzut("P_pulpit");
  await js(`document.querySelector('.karta-czeka .sprawa-wiersz').click(); true`);
  sprawdz("Pulpit: klik prowadzi do karty w Pytaniach", await czekajNa(`location.hash.startsWith('#/pytania?sprawa=') && !!document.querySelector('${LISTA} > .sprawa.podswietlony')`),
    await js(`location.hash + ' / ' + [...document.querySelectorAll('${LISTA} > .sprawa')].map(k => k.id).join(',')`));

  // ------------------------------------------------------------ O: szeroki ekran — lista w lewym dolnym rogu
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 860, deviceScaleFactor: 1, mobile: false });
  await sleep(600);
  sprawdz("O: na szerokim ekranie lista osób widoczna w bocznym pasku", await czekajNa(`(() => { const b = document.querySelector('.bok-obecni');
    const r = b && b.getBoundingClientRect(); return !!(r && r.width > 0 && r.height > 0 && r.left < 260 && b.textContent.includes('Paweł')); })()`));
  await zrzut("O_komputer");
  // osoba w rozmowie (zakładka Sesja): znacznik rozmowy ze stanem mikrofonu przy imieniu
  const uczestnik = await js(`fetch('/api/sesje/dolacz', { method: 'POST', headers: { 'X-BC': '1', 'Content-Type': 'application/json',
    'X-BC-Kto': encodeURIComponent('Paweł') }, body: JSON.stringify({ mikrofon: false }) }).then(r => r.json()).then(j => j.u ? { u: j.u, k: j.k } : null)`);
  await sleep(2200);
  await js(`location.hash = '#/podglad'; true`);                              // zmiana zakładki = puls z nową obecnością
  sprawdz("O: osoba w rozmowie ma znacznik ze stanem mikrofonu", !!uczestnik && await czekajNa(`[...document.querySelectorAll('.bok-obecni .obecny.w-rozmowie')]
    .some(o => o.textContent.includes('Paweł') && o.querySelector('.obecny-rozmowa') && o.textContent.includes('bez mikrofonu'))`),
    await js(`(document.querySelector('.bok-obecni') || {}).textContent`));
  if (uczestnik) await js(`fetch('/api/sesje/opusc', { method: 'POST', headers: { 'X-BC': '1', 'Content-Type': 'application/json' },
    body: JSON.stringify(${JSON.stringify(uczestnik)}) }).then(r => r.status)`);
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
