// Próba zakładki Podgląd („Do przejrzenia”), obrazu przy pracy na Pulpicie, lekkich kart Pytań i podpowiedzi
// „Na sesji padło” w przeglądarce (Edge/Chrome bez okna, protokół DevTools; sam Node 22+).
// Uruchamia ją testy/test_przegladarka_przeglad.py na serwerze testowym — nie ręcznie.
//
//   node testy/przegladarka_przeglad.mjs <port> <katalog danych lokalnych> <przeglądarka> <raporty JSON> [zrzuty]
//
// Kroki (najpierw bez żadnej decyzji — zrzuty ekranu na telefonie 390 px i na komputerze 1280 px — potem decyzje):
//   1. Podgląd: domyślnie „Do przejrzenia”; „Powstaje teraz” (praca ze zrzutem, praca z migawką 3D, bez pracy bez
//      podglądu); „Do akceptacji (4)”: miniatury się wczytały (także z migawki 3D), raport bez obrazu, bez raportu po
//      decyzji i bez informacji; bez przewijania w bok;
//   2. „Przeglądaj po kolei”: okno na cały ekran, licznik, obraz, pytanie, Akceptuję / Do poprawy / Pomiń;
//   3. Pulpit: obraz przy pracy w toku z podpisem, „W 3D” przy pracy z migawką, powiększenie, przycisk „Podglądy”;
//   4. Pytania: karty bez kolorowego paska z lewej i bez cienia, punkty na górze, „Szczegóły” zwinięte, decyzja z wiersza
//      „Rozstrzyga:” w karcie pytania (bez osobnej karty), każda sprawa raz, przycisk „Na sesję główną”;
//   5. Sesja: notatki z sekcją „Padły odpowiedzi na pytania” → „Na sesji padło: …” przy pytaniu #2 i decyzji D-003,
//      „Wpisz do odpowiedzi” wpisuje zdanie do pola (bez wysyłania);
//   6. decyzje: zaznaczenie dwóch raportów → „Akceptuję (2)”; po kolei: Do poprawy z komentarzem, Pomiń, podsumowanie;
//      „Model 3D” i adres z migawką otwierają część 3D.
// Wynik: wiersze „OK …” / „BŁĄD …”, kod wyjścia 0 = wszystko przeszło.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const [port, runtime, przegladarka, raportyJson, zrzuty] = process.argv.slice(2);
const R = JSON.parse(raportyJson);
const PANEL = "http://127.0.0.1:" + port;
const klucz = fs.readFileSync(path.join(runtime, "klucz_lokalny.txt"), "utf8").trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bledy = 0;
const sprawdz = (nazwa, ok, szczegoly) => {
  if (!ok) bledy++;
  console.log((ok ? "OK   " : "BŁĄD ") + nazwa + (szczegoly && !ok ? " — " + String(szczegoly).slice(0, 400) : ""));
};

// notatki sesji podstawiane w odpowiedzi /api/sesje/transkrypcja (agenta i rozmowy w teście nie ma)
const NOTATKI = "## Ustalenia\n- Mgła tylko w lesie.\n\n## Padły odpowiedzi na pytania\n- #2: rezygnujemy z Energii, zostaje sam czas.\n" +
  "- D-003: zatwierdzamy po teście na telefonie.\n";
const PODMIANA = `(() => {
  const prawdziwy = window.fetch.bind(window);
  window.fetch = async (url, init) => {
    const u = String((url && url.url) || url);
    const sciezka = u.replace(/^https?:\\/\\/[^/]+/, '').split('?')[0];
    const odp = await prawdziwy(url, init);
    if (sciezka === '/api/sesje/transkrypcja' && odp.ok && sessionStorage.getItem('bc.test.notatki')) {
      const d = await odp.json();
      d.notatki = { tekst_md: sessionStorage.getItem('bc.test.notatki'), czas: new Date().toISOString(), trwa: false };
      return new Response(JSON.stringify(d), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return odp;
  };
})();`;

const profil = fs.mkdtempSync(path.join(os.tmpdir(), "bc_przegladarka_przeglad_"));
const portDT = 9300 + Math.floor(Math.random() * 600);
const proc = spawn(przegladarka, ["--headless=new", "--remote-debugging-port=" + portDT, "--user-data-dir=" + profil,
  "--no-first-run", "--disable-extensions", "--window-size=1280,900", "about:blank"], { stdio: "ignore" });

let ws;
let nr = 0;
const oczek = new Map();
const konsola = [];
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
  if (selektor) await js(`(() => { const k = document.querySelector(${JSON.stringify(selektor)}); if (k) k.scrollIntoView({ block: 'start' }); window.scrollBy(0, -70); return true; })()`);
  await sleep(450);
  const r = await wyslij("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(zrzuty, { recursive: true });
  fs.writeFileSync(path.join(zrzuty, nazwa + ".png"), Buffer.from(r.data, "base64"));
}
const tekst = (sel) => js(`(document.querySelector(${JSON.stringify(sel)}) || {}).textContent || ''`);
const bezPrzewijaniaWBok = () => js(`document.documentElement.scrollWidth <= window.innerWidth + 1`);
const szerokoscStrony = () => js(`document.documentElement.scrollWidth + ' > ' + window.innerWidth`);
const kafle = `[...document.querySelectorAll('.przeglad-siatka .przeglad-kafel')].map(k => k.dataset.raport)`;
const obrazOk = (sel) => `(() => { const i = document.querySelector(${JSON.stringify(sel)}); return !!i && i.complete && i.naturalWidth > 0; })()`;

async function telefon() {
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await sleep(300);
}
async function komputer() {
  await wyslij("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
  await sleep(300);
}
async function idz(hash) {
  await js(`location.hash = ${JSON.stringify(hash)}; true`);
  await sleep(300);
}

// ---------------------------------------------------------------- kroki bez decyzji (powtarzane na dwóch szerokościach)
async function obejrzyj(ekran) {
  const n = (s) => ekran + ": " + s;
  // 1. Podgląd — Do przejrzenia
  await idz("#/podglad?zakladka=przeglad");
  sprawdz(n("1. Podgląd: część „Do przejrzenia” z czterema raportami"), await czekajNa(`${kafle}.length === 4`, 15000), await js(`JSON.stringify(${kafle})`));
  sprawdz(n("1. przełącznik: „Do przejrzenia” aktywne, licznik 4, obok „Model 3D”"), await js(`(() => {
    const o = [...document.querySelectorAll('.podglad-przelacznik .przelacznik-opcja')];
    return o.length === 2 && o[0].classList.contains('aktywny') && o[0].textContent === 'Do przejrzenia4' && o[1].textContent === 'Model 3D' &&
      document.querySelector('.v3d').hidden && !document.querySelector('.przeglad').hidden; })()`),
  await js(`[...document.querySelectorAll('.podglad-przelacznik .przelacznik-opcja')].map(b => b.textContent + (b.classList.contains('aktywny') ? '*' : '')).join(',')`));
  const lista = await js(`JSON.stringify(${kafle})`);
  sprawdz(n("1. bez raportu po decyzji i bez informacji; raporty z obrazami przed raportem bez obrazu"),
    lista === JSON.stringify([R.ekran, R.polana, R.troll, R.tempo]), lista);
  const zObrazem = JSON.stringify([R.troll, R.polana, R.ekran]);
  sprawdz(n("1. miniatury się wczytały (zrzuty raportów i zrzut migawki 3D)"),
    await czekajNa(`${zObrazem}.every(id => { const i = document.querySelector('.przeglad-kafel[data-raport="' + id + '"] img'); return !!i && i.complete && i.naturalWidth > 0; })`, 10000));
  sprawdz(n("1. licznik obrazów „2” przy trollu, „3D” przy raporcie z migawką, „bez obrazu” przy raporcie bez obrazu"), await js(`(() => {
    const k = (id) => document.querySelector('.przeglad-kafel[data-raport="' + id + '"]');
    return k(${JSON.stringify(R.troll)}).querySelector('.przeglad-ile').textContent === '2' && !!k(${JSON.stringify(R.ekran)}).querySelector('.przeglad-3d') &&
      !!k(${JSON.stringify(R.tempo)}).querySelector('.przeglad-bez-obrazu') && !k(${JSON.stringify(R.tempo)}).querySelector('img'); })()`));
  sprawdz(n("1. „Powstaje teraz”: dwie prace z podglądem (zrzut, migawka 3D), bez pracy bez podglądu"), await czekajNa(`(() => {
    const p = [...document.querySelectorAll('.przeglad-powstaje .przeglad-praca')].map(e => e.dataset.praca);
    return p.length === 2 && p.includes('las-pas') && p.includes('render-modeli'); })()`, 10000),
  await js(`[...document.querySelectorAll('.przeglad-powstaje .przeglad-praca')].map(e => e.dataset.praca).join(',')`));
  sprawdz(n("1. obraz pracy „las-pas” wczytany, podpis z godziną i „Polana od wschodu”"),
    await czekajNa(obrazOk(".przeglad-praca[data-praca='las-pas'] .praca-podglad img"), 8000) &&
    /^podgląd \d{1,2}:\d{2} — Polana od wschodu/.test(await tekst(".przeglad-praca[data-praca='las-pas'] .praca-podglad-podpis")),
    await tekst(".przeglad-praca[data-praca='las-pas'] .praca-podglad-podpis"));
  sprawdz(n("1. praca z samą migawką: zrzut migawki jako obraz i przycisk „W 3D”"), await js(`!!document.querySelector(".przeglad-praca[data-praca='render-modeli'] .praca-3d")`) &&
    await czekajNa(obrazOk(".przeglad-praca[data-praca='render-modeli'] .praca-podglad img"), 8000) &&
    /^migawka 3D/.test(await tekst(".przeglad-praca[data-praca='render-modeli'] .praca-podglad-podpis")), await tekst(".przeglad-praca[data-praca='render-modeli']"));
  sprawdz(n("1. najpierw „Do akceptacji”, niżej „Powstaje teraz”"), await js(`!!(document.querySelector('.przeglad-akceptacja').compareDocumentPosition(document.querySelector('.przeglad-powstaje')) & Node.DOCUMENT_POSITION_FOLLOWING)`));
  sprawdz(n("1. bez przewijania w bok"), await bezPrzewijaniaWBok(), await szerokoscStrony());
  sprawdz(n("1. tytuły kafli nie wychodzą poza kafel"), await js(`[...document.querySelectorAll('.przeglad-kafel')].every(k => {
    const t = k.querySelector('.przeglad-kafel-tytul'); return t.scrollWidth <= k.clientWidth + 1; })`));
  await js(`window.scrollTo(0, 0); true`);
  await zrzut(ekran + "_1_podglad_do_przejrzenia");
  await zrzut(ekran + "_1b_podglad_powstaje", ".przeglad-powstaje");

  // 2. Przeglądaj po kolei (bez decyzji)
  await js(`[...document.querySelectorAll('.przeglad-narzedzia .przycisk')].find(b => b.textContent.includes('Przeglądaj po kolei')).click(); true`);
  sprawdz(n("2. okno „Przeglądaj po kolei” na cały ekran"), await czekajNa(`(() => { const o = document.querySelector('.przeglad-okno');
    if (!o) return false; const r = o.getBoundingClientRect(); return r.width >= innerWidth - 1 && r.height >= innerHeight - 1; })()`, 5000));
  sprawdz(n("2. licznik „1 z 4”, pytanie raportu, obraz"), await czekajNa(`document.querySelector('.przeglad-okno-licznik').textContent === '1 z 4' &&
    document.querySelector('.przeglad-okno-pytanie').textContent === 'Czy akceptujesz: Ekran walki — wersja 2?' && ${obrazOk(".przeglad-okno-img")}`, 6000),
  await js(`document.querySelector('.przeglad-okno-licznik').textContent + ' | ' + document.querySelector('.przeglad-okno-pytanie').textContent`));
  sprawdz(n("2. przyciski Akceptuję / Do poprawy / Pomiń widoczne w oknie"), await js(`(() => {
    const b = [...document.querySelectorAll('.przeglad-okno-akcje .przycisk')]; if (b.length !== 3) return false;
    return b.every(x => { const r = x.getBoundingClientRect(); return r.height >= 44 && r.bottom <= innerHeight + 1 && r.right <= innerWidth + 1; }); })()`),
  await js(`JSON.stringify([...document.querySelectorAll('.przeglad-okno-akcje .przycisk')].map(x => x.getBoundingClientRect()))`));
  await zrzut(ekran + "_2_po_kolei");
  const poprzedni = `[...document.querySelectorAll('.przeglad-okno-drugie .przycisk')].find(b => b.textContent.includes('Poprzedni'))`;
  sprawdz(n("2. „Poprzedni” wyłączony przy pierwszym raporcie"), await js(`${poprzedni}.disabled === true`));
  await js(`document.querySelector('.przeglad-okno-akcje .przycisk:last-child').click(); true`);      // Pomiń (bez decyzji)
  sprawdz(n("2. „Pomiń” → następny raport („2 z 4”), „Poprzedni” działa"), await czekajNa(`document.querySelector('.przeglad-okno-licznik').textContent === '2 z 4' &&
    document.querySelector('.przeglad-okno-tytul').textContent === 'Mapa: polana przy bramie' && ${poprzedni}.disabled === false`, 3000),
  await js(`document.querySelector('.przeglad-okno-licznik').textContent + ' | ' + document.querySelector('.przeglad-okno-tytul').textContent`));
  await js(`${poprzedni}.click(); true`);
  sprawdz(n("2. „Poprzedni” wraca do pierwszego (pominiętego) raportu"), await czekajNa(`document.querySelector('.przeglad-okno-licznik').textContent === '1 z 4' &&
    document.querySelector('.przeglad-okno-stan').textContent.startsWith('Pominięty')`, 3000));
  await js(`document.querySelector('.przeglad-okno-x').click(); true`);
  sprawdz(n("2. zamknięcie okna — bez decyzji, cztery raporty dalej czekają"), await czekajNa(`!document.querySelector('.przeglad-okno') && ${kafle}.length === 4`, 4000));

  // 3. Pulpit
  await idz("#/pulpit");
  sprawdz(n("3. Pulpit: obraz przy pracy w toku"), await czekajNa(obrazOk(".karta-prace [data-praca='las-pas'] .praca-podglad img"), 15000));
  sprawdz(n("3. Pulpit: podpis „podgląd HH:MM — Polana od wschodu”"), /^podgląd \d{1,2}:\d{2} — Polana od wschodu$/.test(await tekst(".karta-prace [data-praca='las-pas'] .praca-podglad-podpis")),
    await tekst(".karta-prace [data-praca='las-pas'] .praca-podglad-podpis"));
  sprawdz(n("3. Pulpit: przy pracy z migawką jej zrzut i „W 3D”, bez obrazu przy pracy bez podglądu"), await js(`!!document.querySelector(".karta-prace [data-praca='render-modeli'] .praca-3d") &&
    !document.querySelector(".karta-prace [data-praca='biom-bagno'] .praca-podglad")`) && await czekajNa(obrazOk(".karta-prace [data-praca='render-modeli'] .praca-podglad img"), 8000));
  sprawdz(n("3. Pulpit: miniatura z prawej obok tekstu (nie pod nim)"), await js(`(() => { const r = document.querySelector(".karta-prace [data-praca='las-pas']");
    const i = r.querySelector('.praca-podglad').getBoundingClientRect(), t = r.querySelector('.praca-tytul').getBoundingClientRect();
    return i.left >= t.right - 1 && i.top < t.bottom + 4 && i.width <= (innerWidth < 720 ? 110 : 190); })()`));
  sprawdz(n("3. Pulpit: przycisk „Podglądy” w karcie Prace w toku"), await js(`[...document.querySelectorAll('.karta-prace .karta-akcje .przycisk')].some(b => b.textContent === 'Podglądy')`));
  sprawdz(n("3. Pulpit: aktywne osoby (komputer: lewy dolny róg, telefon: górny pasek)"), await czekajNa(ekran === "komputer"
    ? `(() => { const b = document.querySelector('.bok-obecni'); if (!b || b.hidden) return false; const r = b.getBoundingClientRect(); return r.left < 260 && r.bottom > innerHeight - 260 && b.textContent.includes('Karol'); })()`
    : `(() => { const g = document.querySelector('.gora-obecni'); return !!g && !g.hidden && g.getBoundingClientRect().top < 70; })()`, 8000));
  sprawdz(n("3. Pulpit: bez przewijania w bok"), await bezPrzewijaniaWBok(), await szerokoscStrony());
  await zrzut(ekran + "_3_pulpit", ".karta-prace");

  // 4. Pytania: lekkie karty, bez dubli
  await idz("#/pytania");
  sprawdz(n("4. Pytania: lista „Do odpowiedzi”"), await czekajNa(`!!document.getElementById('sprawa-pytanie-6') && !!document.getElementById('sprawa-pytanie-2')`, 15000));
  sprawdz(n("4. karty bez kolorowego paska z lewej i bez cienia"), await js(`[...document.querySelectorAll('.kolejka-lista > .sprawa')].every(k => {
    const s = getComputedStyle(k), p = getComputedStyle(k, '::before');
    return parseFloat(s.borderLeftWidth) <= 1 && s.boxShadow === 'none' && (p.display === 'none' || p.content === 'none' || p.content === 'normal'); })`),
  await js(`(() => { const k = document.querySelector('.kolejka-lista > .sprawa'); const s = getComputedStyle(k); return s.borderLeftWidth + ' ' + s.boxShadow; })()`));
  sprawdz(n("4. pytanie #6: punkty na górze, „Szczegóły” zwinięte"), await js(`(() => {
    const k = document.getElementById('sprawa-pytanie-6'); const ul = k.querySelector('.md ul');
    const d = [...k.querySelectorAll('details.sprawa-szczegoly')];
    return !!ul && ul.querySelectorAll('li').length === 2 && d.length >= 1 && d.every(x => !x.open) && !k.textContent.includes('Rozstrzyga:') &&
      d[0].textContent.includes('dłuższy opis'); })()`), await js(`document.getElementById('sprawa-pytanie-6').innerText.slice(0, 400)`));
  sprawdz(n("4. decyzja D-005 z wiersza „Rozstrzyga:” w karcie pytania #6, bez osobnej karty"), await js(`!!document.querySelector('#sprawa-pytanie-6 [data-decyzja="D-005"]') &&
    !document.getElementById('sprawa-D-005')`));
  sprawdz(n("4. każda sprawa na liście raz"), await js(`(() => { const k = [...document.querySelectorAll('section.widok-kontener[data-widok="pytania"] .kolejka-lista > .sprawa')].map(e => e.dataset.klucz); return k.length > 4 && new Set(k).size === k.length; })()`),
    await js(`[...document.querySelectorAll('.kolejka-lista > .sprawa')].map(e => (e.closest('[data-widok]') || {}).dataset.widok + ':' + e.dataset.klucz).join(', ')`));
  sprawdz(n("4. „Na sesję główną” przy pytaniu"), await js(`[...document.querySelectorAll('#sprawa-pytanie-2 .przycisk')].some(b => b.textContent.includes('Na sesję'))`));
  sprawdz(n("4. Pytania: bez przewijania w bok"), await bezPrzewijaniaWBok(), await szerokoscStrony());
  await zrzut(ekran + "_4_pytania", "#sprawa-pytanie-6");

  // 5. Sesja: „Na sesji padło”
  await js(`sessionStorage.setItem('bc.test.notatki', ${JSON.stringify(NOTATKI)}); true`);
  await idz("#/sesja");
  if (ekran === "telefon") await js(`[...document.querySelectorAll('.sesja-przelacznik .przelacznik-opcja')].find(b => b.textContent.startsWith('Pytania')).click(); true`);
  sprawdz(n("5. Sesja: „Na sesji padło” przy pytaniu #2"), await czekajNa(`(document.querySelector('#sesja-sprawa-pytanie-2 .sesja-padlo') || {}).textContent === undefined ? false :
    /Na sesji padło \\(notatki \\d{2}:\\d{2}\\): rezygnujemy z Energii, zostaje sam czas\\./.test(document.querySelector('#sesja-sprawa-pytanie-2 .sesja-padlo').textContent)`, 15000),
  await tekst("#sesja-sprawa-pytanie-2 .sesja-padlo"));
  sprawdz(n("5. Sesja: „Na sesji padło” przy decyzji D-003 (bez przycisku wpisywania)"), await czekajNa(`(() => { const p = document.querySelector('#sesja-sprawa-D-003 .sesja-padlo');
    return !!p && p.textContent.includes('zatwierdzamy po teście') && !p.querySelector('button'); })()`, 5000), await tekst("#sesja-sprawa-D-003"));
  sprawdz(n("5. Sesja: bez podpowiedzi przy innych pytaniach"), await js(`!document.querySelector('#sesja-sprawa-pytanie-4 .sesja-padlo')`));
  await zrzut(ekran + "_5_sesja_padlo", "#sesja-sprawa-pytanie-2");
  await js(`sessionStorage.removeItem('bc.test.notatki'); true`);
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
    if (d.id && oczek.has(d.id)) {
      const o = oczek.get(d.id);
      oczek.delete(d.id);
      if (d.error) o.rej(new Error(JSON.stringify(d.error)));
      else o.res(d.result);
      return;
    }
    if (d.method === "Runtime.exceptionThrown") konsola.push("wyjątek: " + JSON.stringify(d.params.exceptionDetails).slice(0, 400));
    if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") {
      konsola.push("error: " + (d.params.args || []).map((a) => a.value || a.description || "").join(" ").slice(0, 400));
    }
  });
  await wyslij("Page.enable");
  await wyslij("Runtime.enable");
  await wyslij("Emulation.setFocusEmulationEnabled", { enabled: true });
  await telefon();
  await wyslij("Page.addScriptToEvaluateOnNewDocument", { source: PODMIANA });
  await wyslij("Page.navigate", { url: PANEL + "/?l=" + encodeURIComponent(klucz) });
  await sleep(1500);
  await js(`localStorage.setItem('bc.kto', 'Karol'); localStorage.removeItem('bc.podglad.tryb'); sessionStorage.setItem('bc.pytano', '1'); true`);
  await wyslij("Page.reload", { ignoreCache: true });
  await czekajNa(`!!document.querySelector('.karta-czeka')`, 15000);

  await obejrzyj("telefon");
  await komputer();
  await obejrzyj("komputer");

  // ---------------------------------------------------------------- 6. decyzje (komputer)
  await idz("#/podglad");
  sprawdz("6. bez parametrów: ostatnio wybrana część („Do przejrzenia”)", await czekajNa(`${kafle}.length === 4 && !document.querySelector('.przeglad').hidden`, 10000));
  for (const id of [R.troll, R.polana]) {
    await js(`document.querySelector('.przeglad-kafel[data-raport="${id}"] .przeglad-wybor input').click(); true`);
  }
  sprawdz("6. pasek zaznaczonych: „Zaznaczone: 2”, „Akceptuję (2)”", await czekajNa(`(() => { const p = document.querySelector('.przeglad-pasek-wyboru');
    return !!p && !p.hidden && p.textContent.includes('Zaznaczone: 2') && p.textContent.includes('Akceptuję (2)'); })()`, 3000),
  await tekst(".przeglad-pasek-wyboru"));
  await zrzut("komputer_6_zaznaczone", ".przeglad-akceptacja");
  await js(`[...document.querySelectorAll('.przeglad-pasek-wyboru .przycisk')].find(b => b.textContent.includes('Akceptuję')).click(); true`);
  sprawdz("6. po „Akceptuję (2)”: oba raporty znikają z siatki, licznik 2", await czekajNa(`JSON.stringify(${kafle}) === JSON.stringify([${JSON.stringify(R.ekran)}, ${JSON.stringify(R.tempo)}]) &&
    document.querySelector('.podglad-przelacznik .przelacznik-opcja').textContent === 'Do przejrzenia2'`, 8000), await js(`JSON.stringify(${kafle})`));
  const statusy = await js(`fetch('/api/raporty').then(r => r.json()).then(d => JSON.stringify(Object.fromEntries(d.raporty.map(r => [r.id, r.status]))))`);
  const st = JSON.parse(statusy);
  sprawdz("6. na serwerze: troll i polana zaakceptowane", st[R.troll] === "zaakceptowane" && st[R.polana] === "zaakceptowane", statusy);

  await js(`document.querySelector('.przeglad-kafel[data-raport="${R.ekran}"] .przeglad-kafel-obraz').click(); true`);
  sprawdz("6. klik w kafel otwiera okno na tym raporcie („1 z 2”)", await czekajNa(`(document.querySelector('.przeglad-okno-licznik') || {}).textContent === '1 z 2'`, 4000));
  await js(`[...document.querySelectorAll('.przeglad-okno-akcje .przycisk')].find(b => b.textContent.includes('Do poprawy')).click(); true`);
  sprawdz("6. „Do poprawy” pokazuje pole komentarza", await czekajNa(`!document.querySelector('.przeglad-okno-poprawa').hidden && document.activeElement === document.querySelector('.przeglad-okno-poprawa textarea')`, 3000));
  await js(`(() => { const t = document.querySelector('.przeglad-okno-poprawa textarea'); t.value = 'Ciemniejsze tło'; t.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
  await js(`[...document.querySelectorAll('.przeglad-okno-poprawa .przycisk')].find(b => b.textContent.includes('Odeślij')).click(); true`);
  sprawdz("6. po odesłaniu: następny raport (bez obrazu) z własnym pytaniem", await czekajNa(`document.querySelector('.przeglad-okno-licznik').textContent === '2 z 2' &&
    document.querySelector('.przeglad-okno-pytanie').textContent === 'Czy 57 s na bieg od wejścia do bramy to dobre tempo?' && !document.querySelector('.przeglad-okno-bez').hidden`, 6000),
  await js(`document.querySelector('.przeglad-okno-licznik').textContent + ' | ' + document.querySelector('.przeglad-okno-pytanie').textContent`));
  await zrzut("komputer_6b_po_kolei_bez_obrazu");
  await js(`document.querySelector('.przeglad-okno-akcje .przycisk:last-child').click(); true`);                // Pomiń
  sprawdz("6. podsumowanie: do poprawy 1, pominięte 1, czeka jeszcze 1", await czekajNa(`(() => { const k = document.querySelector('.przeglad-okno-koniec');
    return !!k && !k.hidden && k.textContent.includes('Do poprawy: 1') && k.textContent.includes('Pominięte: 1') && k.textContent.includes('Czeka jeszcze: 1 raport'); })()`, 4000),
  await tekst(".przeglad-okno-koniec"));
  await zrzut("komputer_6c_podsumowanie");
  await js(`document.querySelector('.przeglad-okno-koniec .przycisk').click(); true`);
  sprawdz("6. po zamknięciu w siatce zostaje tylko pominięty raport", await czekajNa(`JSON.stringify(${kafle}) === JSON.stringify([${JSON.stringify(R.tempo)}])`, 6000), await js(`JSON.stringify(${kafle})`));

  await js(`[...document.querySelectorAll('.podglad-przelacznik .przelacznik-opcja')][1].click(); true`);
  sprawdz("6. „Model 3D”: widać część 3D, siatka ukryta", await czekajNa(`!document.querySelector('.v3d').hidden && document.querySelector('.przeglad').hidden &&
    (document.querySelector('.v3d-tytul') || {}).textContent === 'Migawka testowa'`, 15000), await tekst(".v3d-tytul"));
  await zrzut("komputer_7_model_3d");
  await idz("#/pulpit");
  await idz("#/podglad");
  sprawdz("6. powrót bez parametrów: zapamiętany „Model 3D”", await czekajNa(`!document.querySelector('.v3d').hidden && document.querySelector('.przeglad').hidden`, 5000));
  await idz("#/podglad?zakladka=przeglad");
  sprawdz("6. adres ?zakladka=przeglad: „Do przejrzenia”", await czekajNa(`document.querySelector('.v3d').hidden && !document.querySelector('.przeglad').hidden`, 5000));
  await js(`document.querySelector(".przeglad-praca[data-praca='render-modeli'] .praca-3d").click(); true`);
  sprawdz("6. „W 3D” przy pracy otwiera migawkę w części 3D", await czekajNa(`location.hash.includes('migawka=') && !document.querySelector('.v3d').hidden`, 8000), await js(`location.hash`));

  // Pulpit: powiększenie obrazu pracy i „Podglądy”
  await idz("#/pulpit");
  await czekajNa(obrazOk(".karta-prace [data-praca='las-pas'] .praca-podglad img"), 10000);
  await js(`document.querySelector(".karta-prace [data-praca='las-pas'] .praca-podglad-obraz").click(); true`);
  sprawdz("Pulpit: klik w obraz pracy powiększa go na cały ekran", await czekajNa(`!!document.querySelector('.lightbox .lb-obraz') && document.querySelector('.lightbox .lb-podpis').textContent.includes('Polana od wschodu')`, 4000));
  await js(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); true`);
  sprawdz("Pulpit: Esc zamyka powiększenie", await czekajNa(`!document.querySelector('.lightbox')`, 3000));
  await js(`[...document.querySelectorAll('.karta-prace .karta-akcje .przycisk')].find(b => b.textContent === 'Podglądy').click(); true`);
  sprawdz("Pulpit: „Podglądy” prowadzi do „Do przejrzenia”", await czekajNa(`location.hash.startsWith('#/podglad') && !document.querySelector('.przeglad').hidden`, 5000), await js(`location.hash`));

  // Sesja: „Wpisz do odpowiedzi” (bez wysyłania)
  await js(`sessionStorage.setItem('bc.test.notatki', ${JSON.stringify(NOTATKI)}); true`);
  await idz("#/sesja");
  await czekajNa(`!!document.querySelector('#sesja-sprawa-pytanie-2 .sesja-padlo button')`, 15000);
  await js(`document.querySelector('#sesja-sprawa-pytanie-2 .sesja-padlo button').click(); true`);
  sprawdz("Sesja: „Wpisz do odpowiedzi” wpisuje zdanie do pola odpowiedzi pytania #2",
    await czekajNa(`(document.querySelector('#sesja-sprawa-pytanie-2 form.odpowiedz-formularz textarea') || {}).value === 'rezygnujemy z Energii, zostaje sam czas.'`, 3000),
    await js(`(document.querySelector('#sesja-sprawa-pytanie-2 form.odpowiedz-formularz textarea') || {}).value`));
  await sleep(5000);                                                         // ciche odświeżenie listy i notatek
  sprawdz("Sesja: po odświeżeniu zdanie zostaje w polu i podpowiedź dalej jest", await js(`(document.querySelector('#sesja-sprawa-pytanie-2 form.odpowiedz-formularz textarea') || {}).value === 'rezygnujemy z Energii, zostaje sam czas.' &&
    !!document.querySelector('#sesja-sprawa-pytanie-2 .sesja-padlo')`));
  const plan = await js(`fetch('/api/sejf/plan').then(r => r.json()).then(d => JSON.stringify(d.pytania.find(p => p.nr === 2)))`);
  sprawdz("Sesja: nic nie poszło do sejfu bez kliknięcia „Odpowiedz”", JSON.parse(plan).otwarte === true, plan);
  await js(`sessionStorage.removeItem('bc.test.notatki'); true`);

  sprawdz("całość: bez błędów w konsoli", !konsola.length, konsola.join(" | "));
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
