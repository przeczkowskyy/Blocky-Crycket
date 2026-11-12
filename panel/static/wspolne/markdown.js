// Bezpieczny renderer Markdownu (odmiana Obsidiana) → HTML.
// Zasada bezpieczeństwa: cały tekst przechodzi przez ucieczkę HTML, a generujemy wyłącznie znane znaczniki;
// linki tylko http/https/mailto i względne. Surowy HTML z notatek jest pokazywany jako tekst.
//
// md(tekst, {naWikilink?}) → HTML (bloki); mdLinia(tekst, opcje) → HTML jednej linii (bez <p>).
// Wikilinki [[Nazwa]], [[Nazwa|alias]], [[Nazwa#Nagłówek]] → <a class="wikilink" data-wikilink="Nazwa" href="#/siec?notatka=…">.
// opcje.naWikilink(nazwa, naglowek) może zwrócić własny adres (href); kliknięcia obsługuje powłoka (app.js) albo mdEl().

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

/** Ucieczka znaków HTML. */
export function ucieczka(s) {
  return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, (c) => ESC[c]);
}

/** Adres dozwolony w linku albo null. */
export function bezpiecznyUrl(url) {
  const u = String(url || "").trim();
  const czysty = u.replace(/[\u0000- \u007f]/g, "");
  if (!czysty) return null;
  if (/^(https?:|mailto:)/i.test(czysty)) return u;
  if (/^[a-z][a-z0-9+.\-]*:/i.test(czysty)) return null;          // javascript:, data:, vbscript:, file: …
  if (czysty.startsWith("//") || czysty.startsWith("\\")) return null;
  return u;                                                         // względny albo #kotwica
}

const TYTULY_CALLOUTOW = {
  note: "Notatka", info: "Informacja", tip: "Wskazówka", hint: "Wskazówka", important: "Ważne", success: "Zrobione",
  check: "Zrobione", done: "Zrobione", question: "Pytanie", help: "Pytanie", faq: "Pytanie", warning: "Uwaga",
  caution: "Uwaga", attention: "Uwaga", failure: "Niepowodzenie", fail: "Niepowodzenie", missing: "Brak",
  danger: "Niebezpieczeństwo", error: "Błąd", bug: "Błąd", example: "Przykład", quote: "Cytat", cite: "Cytat",
  abstract: "Podsumowanie", summary: "Podsumowanie", tldr: "W skrócie", todo: "Do zrobienia",
};
const KOLORY_CALLOUTOW = {
  note: "niebieski", info: "niebieski", todo: "niebieski", tip: "zielen", hint: "zielen", important: "zielen",
  success: "zielen", check: "zielen", done: "zielen", question: "zloto", help: "zloto", faq: "zloto",
  warning: "zloto", caution: "zloto", attention: "zloto", failure: "czerwien", fail: "czerwien", missing: "czerwien",
  danger: "czerwien", error: "czerwien", bug: "czerwien", example: "fiolet", abstract: "fiolet", summary: "fiolet",
  tldr: "fiolet", quote: "szary", cite: "szary",
};

// --------------------------------------------------------------------------- elementy w linii
function wikilink(wnetrze, opcje, osadzenie) {
  let cel = wnetrze;
  let alias = "";
  const kreska = wnetrze.indexOf("|");
  if (kreska >= 0) {
    cel = wnetrze.slice(0, kreska);
    alias = wnetrze.slice(kreska + 1).trim();
  }
  cel = cel.replace(/\\$/, "").trim();
  const hash = cel.indexOf("#");
  const nazwa = (hash >= 0 ? cel.slice(0, hash) : cel).trim();
  const naglowek = hash >= 0 ? cel.slice(hash + 1).replace(/^\^/, "").trim() : "";
  const krotka = nazwa.split("/").pop().replace(/\.md$/i, "");
  const tekst = alias || (naglowek ? (krotka ? krotka + " › " : "") + naglowek : krotka);
  if (!nazwa) return '<span class="wikilink pusty-link">' + ucieczka(tekst) + "</span>";
  let href = null;
  if (opcje && typeof opcje.naWikilink === "function") {
    try {
      href = opcje.naWikilink(nazwa, naglowek);
    } catch (e) {
      href = null;
    }
  }
  if (typeof href !== "string" || !bezpiecznyUrl(href)) href = "#/siec?notatka=" + encodeURIComponent(nazwa);
  return '<a class="wikilink' + (osadzenie ? " osadzenie" : "") + '" href="' + ucieczka(href) + '" data-wikilink="' +
    ucieczka(nazwa) + '"' + (naglowek ? ' data-naglowek="' + ucieczka(naglowek) + '"' : "") + ">" +
    (osadzenie ? "📎 " : "") + ucieczka(tekst) + "</a>";
}

function akcenty(s) {
  s = s.replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^\p{L}\p{N}_])__(?=\S)([\s\S]*?\S)__(?![\p{L}\p{N}_])/gu, "$1<strong>$2</strong>");
  s = s.replace(/(^|[^*\\])\*(?=[^\s*])([^*\n]*?[^\s*])?\*(?!\*)/g, (m, przed, srodek, off, cale) => {
    // pojedyncza gwiazdka: kursywa (także jednoznakowa: *a*)
    const tresc = m.slice(przed.length + 1, -1);
    return przed + "<em>" + tresc + "</em>";
  });
  s = s.replace(/(^|[^\p{L}\p{N}_])_(?=\S)([^_\n]*?\S)_(?![\p{L}\p{N}_])/gu, "$1<em>$2</em>");
  s = s.replace(/~~(?=\S)([\s\S]*?\S)~~/g, "<del>$1</del>");
  s = s.replace(/==(?=\S)([^=\n]*?\S)==/g, "<mark>$1</mark>");
  return s;
}

/** HTML jednej linii (albo kilku linii akapitu — nowe linie stają się <br>). */
export function mdLinia(tekst, opcje = {}) {
  const schowek = [];
  const schowaj = (html) => "\u0000" + (schowek.push(html) - 1) + "\u0000";
  let s = String(tekst === null || tekst === undefined ? "" : tekst).replace(/\u0000/g, "");

  // kod w linii (najpierw — w środku nic nie jest interpretowane)
  s = s.replace(/``([^`\n](?:[^\n]*?[^`\n])?)``|`([^`\n]+)`/g, (_, a, b) => schowaj("<code>" + ucieczka(a !== undefined ? a : b) + "</code>"));
  // znaki poprzedzone ukośnikiem
  s = s.replace(/\\([\\`*_{}\[\]()#+\-.!|~=>])/g, (_, c) => schowaj(ucieczka(c)));
  // wikilinki i osadzenia
  s = s.replace(/(!?)\[\[([^\[\]\n]+?)\]\]/g, (_, wykrzyknik, wnetrze) => schowaj(wikilink(wnetrze, opcje, !!wykrzyknik)));
  // obrazy ![opis](adres) — tylko względne (CSP i tak blokuje obce), inne jako link
  s = s.replace(/!\[([^\]\n]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"\n]*")?\s*\)/g, (_, opis, url) => {
    const u = bezpiecznyUrl(url);
    if (!u) return schowaj(ucieczka(opis));
    if (/^(https?:|mailto:)/i.test(u)) return schowaj('<a href="' + ucieczka(u) + '" target="_blank" rel="noopener noreferrer">🖼 ' + ucieczka(opis || u) + "</a>");
    return schowaj('<img src="' + ucieczka(u) + '" alt="' + ucieczka(opis) + '" loading="lazy">');
  });
  // linki [tekst](adres "tytuł")
  s = s.replace(/\[([^\]\n]+)\]\(\s*<?([^)\s>]+)>?(?:\s+"([^"\n]*)")?\s*\)/g, (_, txt, url, tytul) => {
    const u = bezpiecznyUrl(url);
    const wnetrze = akcenty(ucieczka(txt));
    if (!u) return schowaj(wnetrze);
    const zewn = /^https?:/i.test(u);
    return schowaj('<a href="' + ucieczka(u) + '"' + (tytul ? ' title="' + ucieczka(tytul) + '"' : "") +
      (zewn ? ' target="_blank" rel="noopener noreferrer"' : "") + ">" + wnetrze + "</a>");
  });
  // gołe adresy
  s = s.replace(/\bhttps?:\/\/[^\s<>"'`\u0000]+/g, (url) => {
    const m = /[.,;:!?)\]]+$/.exec(url);
    const ogon = m ? m[0] : "";
    const czysty = ogon ? url.slice(0, -ogon.length) : url;
    return schowaj('<a href="' + ucieczka(czysty) + '" target="_blank" rel="noopener noreferrer">' + ucieczka(czysty) + "</a>") + ogon;
  });

  s = ucieczka(s);
  s = akcenty(s);
  // tagi Obsidiana (#tag; same cyfry to nie tag)
  s = s.replace(/(^|[\s(])#([\p{L}_][\p{L}\p{N}_\/-]*)/gu, (_, przed, tag) => przed + '<span class="md-tag">#' + tag + "</span>");
  s = s.replace(/\n/g, "<br>");
  // przywrócenie schowanych fragmentów (mogą być zagnieżdżone)
  for (let proba = 0; proba < 5 && s.indexOf("\u0000") >= 0; proba++) {
    s = s.replace(/\u0000(\d+)\u0000/g, (_, n) => schowek[+n]);
  }
  return s;
}

// --------------------------------------------------------------------------- bloki
const RE_LISTA = /^(\s*)([-*+]|\d{1,9}[.)])(?:\s+(.*))?$/;
const RE_PLOT = /^\s{0,3}(`{3,}|~{3,})\s*([\w+#.\-]*)/;
const RE_NAGLOWEK = /^\s{0,3}(#{1,6})\s+(.*?)(?:\s+#+)?\s*$/;
const RE_LINIA = /^\s{0,3}([-*_])(?:\s*\1){2,}\s*$/;
const RE_CYTAT = /^\s{0,3}>/;
const RE_SEPARATOR = /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/;

const pusta = (l) => /^\s*$/.test(l);

function szerokosc(wc) {
  let n = 0;
  for (const c of wc) n += c === "\t" ? 4 : 1;
  return n;
}

function komorki(linia) {
  let t = linia.trim();
  if (t.startsWith("|")) t = t.slice(1);
  if (t.endsWith("|") && !t.endsWith("\\|")) t = t.slice(0, -1);
  const out = [];
  let biezaca = "";
  let wKodzie = false;
  let wLinku = 0;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (c === "\\" && t[i + 1] === "|") {
      biezaca += "|";
      i++;
      continue;
    }
    if (c === "`") wKodzie = !wKodzie;
    if (!wKodzie && c === "[" && t[i + 1] === "[") wLinku++;
    if (!wKodzie && c === "]" && t[i + 1] === "]" && wLinku) wLinku--;
    if (c === "|" && !wKodzie && !wLinku) {
      out.push(biezaca.trim());
      biezaca = "";
    } else biezaca += c;
  }
  out.push(biezaca.trim());
  return out;
}

function czyTabela(linie, i) {
  return linie[i].includes("|") && i + 1 < linie.length && linie[i + 1].includes("|") && RE_SEPARATOR.test(linie[i + 1]) &&
    linie[i + 1].includes("-");
}

function poczatekBloku(linie, i) {
  const l = linie[i];
  return RE_PLOT.test(l) || RE_NAGLOWEK.test(l) || RE_LINIA.test(l) || RE_CYTAT.test(l) || RE_LISTA.test(l) || czyTabela(linie, i);
}

function tabela(linie, i, opcje) {
  const naglowki = komorki(linie[i]);
  const wyrownanie = komorki(linie[i + 1]).map((k) => {
    const lewo = k.startsWith(":");
    const prawo = k.endsWith(":");
    return lewo && prawo ? "srodek" : prawo ? "prawo" : "";
  });
  const klasa = (j) => (wyrownanie[j] ? ' class="w-' + wyrownanie[j] + '"' : "");
  let h = '<div class="md-tabela"><table><thead><tr>' +
    naglowki.map((k, j) => "<th" + klasa(j) + ">" + mdLinia(k, opcje) + "</th>").join("") + "</tr></thead><tbody>";
  i += 2;
  while (i < linie.length && !pusta(linie[i]) && linie[i].includes("|")) {
    const k = komorki(linie[i]);
    h += "<tr>" + naglowki.map((_, j) => "<td" + klasa(j) + ">" + mdLinia(k[j] || "", opcje) + "</td>").join("") + "</tr>";
    i++;
  }
  return [h + "</tbody></table></div>", i];
}

function cytat(wnetrze, opcje) {
  const m = /^\s*\[!([\w-]+)\]([+-]?)\s*(.*)$/.exec(wnetrze[0] || "");
  if (!m) return "<blockquote>" + bloki(wnetrze, opcje) + "</blockquote>";
  const typ = m[1].toLowerCase();
  const tytul = m[3] ? mdLinia(m[3], opcje) : ucieczka(TYTULY_CALLOUTOW[typ] || (typ.charAt(0).toUpperCase() + typ.slice(1)));
  const tresc = bloki(wnetrze.slice(1), opcje);
  const kolor = KOLORY_CALLOUTOW[typ] || "niebieski";
  if (m[2]) {
    return '<details class="callout callout-' + kolor + '" data-callout="' + ucieczka(typ) + '"' + (m[2] === "+" ? " open" : "") +
      '><summary class="callout-tytul">' + tytul + '</summary><div class="callout-tresc">' + tresc + "</div></details>";
  }
  return '<div class="callout callout-' + kolor + '" data-callout="' + ucieczka(typ) + '"><div class="callout-tytul">' + tytul +
    "</div>" + (tresc ? '<div class="callout-tresc">' + tresc + "</div>" : "") + "</div>";
}

function lista(linie, i, opcje) {
  const elementy = [];
  while (i < linie.length) {
    const l = linie[i];
    const m = RE_LISTA.exec(l);
    if (m && !RE_LINIA.test(l)) {
      elementy.push({ wc: szerokosc(m[1]), ol: /\d/.test(m[2]), nr: parseInt(m[2], 10), tresc: [m[3] || ""] });
      i++;
      continue;
    }
    if (pusta(l)) {
      let j = i + 1;
      while (j < linie.length && pusta(linie[j])) j++;
      if (j < linie.length && (RE_LISTA.test(linie[j]) && !RE_LINIA.test(linie[j]) || /^\s{2,}\S/.test(linie[j]))) {
        i = j;
        continue;
      }
      break;
    }
    if (/^\s+\S/.test(l) || !poczatekBloku(linie, i)) {
      elementy[elementy.length - 1].tresc.push(l.trim());
      i++;
      continue;
    }
    break;
  }
  let k = 0;
  function poziom(wcPoziomu) {
    const pierwszy = elementy[k];
    let h = "";
    while (k < elementy.length && elementy[k].wc >= wcPoziomu) {
      const e = elementy[k];
      k++;
      let tresc = e.tresc.join("\n");
      let pole = "";
      let klasa = "";
      const z = /^\[([ xX\/\-])\](?:\s+|$)/.exec(tresc);
      if (z) {
        const zrobione = z[1] !== " ";
        pole = '<input type="checkbox" disabled' + (zrobione ? " checked" : "") + "> ";
        klasa = ' class="zadanie' + (zrobione ? " zrobione" : "") + '"';
        tresc = tresc.slice(z[0].length);
      }
      let wn = mdLinia(tresc, opcje);
      if (k < elementy.length && elementy[k].wc > e.wc) wn += poziom(elementy[k].wc);
      h += "<li" + klasa + ">" + pole + wn + "</li>";
    }
    if (pierwszy.ol) return "<ol" + (pierwszy.nr !== 1 ? ' start="' + pierwszy.nr + '"' : "") + ">" + h + "</ol>";
    return "<ul>" + h + "</ul>";
  }
  let html = "";
  while (k < elementy.length) html += poziom(elementy[k].wc);
  return [html, i];
}

function bloki(linie, opcje) {
  const out = [];
  let i = 0;
  while (i < linie.length) {
    const l = linie[i];
    if (pusta(l)) {
      i++;
      continue;
    }
    let m = RE_PLOT.exec(l);
    if (m) {
      const plot = m[1];
      const kod = [];
      i++;
      while (i < linie.length && !linie[i].trim().startsWith(plot)) {
        kod.push(linie[i]);
        i++;
      }
      i++;
      out.push("<pre><code" + (m[2] ? ' class="jezyk-' + ucieczka(m[2]) + '"' : "") + ">" + ucieczka(kod.join("\n")) + "</code></pre>");
      continue;
    }
    m = RE_NAGLOWEK.exec(l);
    if (m) {
      const p = m[1].length;
      out.push("<h" + p + ">" + mdLinia(m[2], opcje) + "</h" + p + ">");
      i++;
      continue;
    }
    if (RE_LINIA.test(l)) {
      out.push("<hr>");
      i++;
      continue;
    }
    if (RE_CYTAT.test(l)) {
      const wn = [];
      while (i < linie.length && RE_CYTAT.test(linie[i])) {
        wn.push(linie[i].replace(/^\s{0,3}>\s?/, ""));
        i++;
      }
      out.push(cytat(wn, opcje));
      continue;
    }
    if (czyTabela(linie, i)) {
      const [h, j] = tabela(linie, i, opcje);
      out.push(h);
      i = j;
      continue;
    }
    if (RE_LISTA.test(l)) {
      const [h, j] = lista(linie, i, opcje);
      out.push(h);
      i = j;
      continue;
    }
    const akapit = [l.trim()];
    i++;
    while (i < linie.length && !pusta(linie[i]) && !poczatekBloku(linie, i)) {
      akapit.push(linie[i].trim());
      i++;
    }
    out.push("<p>" + mdLinia(akapit.join("\n"), opcje) + "</p>");
  }
  return out.join("\n");
}

/** md(tekst, {naWikilink?}) → bezpieczny HTML. */
export function md(tekst, opcje = {}) {
  let s = String(tekst === null || tekst === undefined ? "" : tekst).replace(/\r\n?/g, "\n").replace(/\u0000/g, "");
  s = s.replace(/%%[\s\S]*?%%/g, "").replace(/<!--[\s\S]*?-->/g, "");
  s = s.replace(/^---\n([\s\S]*?)\n---[ \t]*(\n|$)/, (cale, srodek) => (/^[\w-]+\s*:/m.test(srodek) ? "" : cale));
  return bloki(s.split("\n"), opcje || {});
}

/**
 * mdEl(tekst, {linia?, klasa?, znacznik?, naWikilink?, naKlikWikilinka?}) → element .md z wyrenderowaną treścią.
 * naKlikWikilinka(nazwa, naglowek) — własna obsługa kliknięcia w wikilink (bez niej działa adres #/siec?notatka=…).
 */
export function mdEl(tekst, opcje = {}) {
  const w = document.createElement(opcje.znacznik || (opcje.linia ? "span" : "div"));
  w.className = "md" + (opcje.linia ? " md-linia" : "") + (opcje.klasa ? " " + opcje.klasa : "");
  w.innerHTML = opcje.linia ? mdLinia(tekst, opcje) : md(tekst, opcje);
  if (typeof opcje.naKlikWikilinka === "function") {
    w.addEventListener("click", (e) => {
      const a = e.target.closest && e.target.closest("a[data-wikilink]");
      if (!a || !w.contains(a)) return;
      e.preventDefault();
      e.stopPropagation();
      opcje.naKlikWikilinka(a.dataset.wikilink, a.dataset.naglowek || "");
    });
  }
  return w;
}
