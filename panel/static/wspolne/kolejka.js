// Pytania do ludzi — wszystko, co czeka na odpowiedź albo decyzję człowieka, jako JEDNA lista bez dubli:
//   - pytania otwarte bez odpowiedzi (z decyzjami z wiersza „Rozstrzyga: D-0XX, …” w tej samej karcie),
//   - decyzje „propozycja” / „do decyzji”, które nie są przypięte do żadnego czekającego pytania — jako pytanie
//     „Czy zatwierdzamy: <tytuł>?”,
//   - raporty czekające na „Akceptuję” / „Do poprawy” — ich własne pytanie (pole `pytanie`) albo „Czy akceptujesz: …?”,
//   - decyzje z jednym podpisem, które czekają na MOJE potwierdzenie (D-043, pole `czeka_na`) — jako pytanie
//     „Karol zatwierdził: <tytuł> — zgadzasz się?” (typ „potwierdzenie”, klucz jak decyzji: „D-019”). Decyzje, które
//     sam podjąłem, nie są w mojej kolejce (w historii mają znacznik „czeka na potwierdzenie: Imię”).
// Sprawa, której źródło („D-009”, „pytanie 19”) jest na agendzie sesji głównej, trafia do grupy „Odłożone”.
// Historia „Odpowiedziane”: pytania z odpowiedzią, decyzje zamknięte (zatwierdzone, odrzucone, zastąpione) i raporty
// po decyzji albo informacyjne — razem, od najnowszych.
// Używają tego: zakładka Pytania, lista Pytania w zakładce Sesja, Pulpit (trzy pierwsze sprawy) i powłoka (plakietka).
// Starszy serwer nie zwraca pól `rozstrzyga` / `powiazane` — wtedy wiersz „Rozstrzyga:” czytamy z treści pytania.

export const OTWARTE_DECYZJE = ["propozycja", "do_decyzji"];
export const ZAMKNIETE_DECYZJE = ["zatwierdzona", "odrzucona", "zastapiona"];

const RX_ROZSTRZYGA = /^\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*Rozstrzyga\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?(.*)$/i;

/** "D-19" / "D-019" → 19; coś innego → null. */
export function numerDecyzji(id) {
  const m = /^\s*D-(\d{1,4})\s*$/i.exec(String(id || ""));
  return m ? Number(m[1]) : null;
}

/** 19 → "D-019" (jak w Rejestrze decyzji). */
export function idDecyzji(n) {
  return "D-" + String(Number(n)).padStart(3, "0");
}

function identyfikatory(tekst) {
  const wynik = [];
  for (const m of String(tekst || "").matchAll(/\bD-(\d{1,4})\b/g)) {
    const id = idDecyzji(m[1]);
    if (!wynik.includes(id)) wynik.push(id);
  }
  return wynik;
}

/** Decyzje z wiersza „Rozstrzyga:” pytania (pole serwera albo odczyt z treści przy starszym serwerze). */
export function rozstrzyga(p) {
  if (p && Array.isArray(p.rozstrzyga)) return p.rozstrzyga.map(numerDecyzji).filter((n) => n !== null).map(idDecyzji);
  const wynik = [];
  for (const linia of String((p && p.tresc_md) || "").split("\n")) {
    const m = RX_ROZSTRZYGA.exec(linia);
    if (m) for (const id of identyfikatory(m[1])) if (!wynik.includes(id)) wynik.push(id);
  }
  return wynik;
}

/** Pozostałe wzmianki „D-0XX” w tytule i treści pytania (bez automatyki). */
export function powiazane(p) {
  if (p && Array.isArray(p.powiazane)) return p.powiazane;
  const r = rozstrzyga(p);
  return identyfikatory(((p && p.tytul) || "") + "\n" + ((p && p.tresc_md) || "")).filter((i) => !r.includes(i));
}

/** Treść pytania bez wiersza „Rozstrzyga:” (decyzje pokazuje karta osobno). */
export function bezWierszaRozstrzyga(md) {
  return String(md || "").split("\n").filter((l) => !RX_ROZSTRZYGA.test(l)).join("\n").trim();
}

// ----------------------------------------------------------------------------- krótka treść karty
// Karta pokazuje krótko, czego sprawa dotyczy; reszta jest zwinięta za „Pokaż szczegóły”.
// Pytania w sejfie mają na górze 2–4 punkty, a dłuższy opis pod wierszem „Szczegóły:” i w wierszach „Dopisek …”
// i „Sprostowanie …”. Bez lookbehind w wyrażeniach (starsze Safari na telefonach go nie zna).
const RX_SZCZEGOLY = /^\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*Szczeg[oó][lł]y\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*/i;
const RX_DOPISEK = /^\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*(?:Dopisek|Sprostowanie)\b/i;
const RX_PUNKT = /^\s*(?:[-*+]|\d+[.)])\s+/;
const SKROTY = new Set(["np", "ok", "tzw", "itp", "itd", "zob", "tj", "godz", "nr", "dr", "ul", "wg", "pkt", "ds", "m.in", "r", "w", "s", "por", "jw", "ang"]);

/** Tekst → lista zdań (bez dzielenia na „np.”, „12.11”, „ok. 25”). */
export function zdania(tekst) {
  const t = String(tekst || "").trim();
  const rx = /[.!?…]+["”»)\]]*\s+/g;
  const wynik = [];
  let od = 0;
  let m;
  while ((m = rx.exec(t))) {
    const dalej = t.slice(m.index + m[0].length, m.index + m[0].length + 1);
    if (!/[A-ZĄĆĘŁŃÓŚŹŻ„"(]/.test(dalej)) continue;           // po kropce małe litery albo cyfra: to nie koniec zdania
    const slowo = (/([\p{L}.]+)$/u.exec(t.slice(0, m.index)) || ["", ""])[1].toLowerCase();
    if (/[.]$/.test(m[0].trim()) && SKROTY.has(slowo)) continue;
    const koniec = m.index + m[0].trimEnd().length;
    wynik.push(t.slice(od, koniec).trim());
    od = koniec;
  }
  if (t.slice(od).trim()) wynik.push(t.slice(od).trim());
  return wynik;
}

/** Pierwsze `n` zdań tekstu → {krotko, reszta} (reszta pusta, gdy tekst jest krótki). */
export function pierwszeZdania(tekst, n = 2) {
  const z = zdania(tekst);
  return { krotko: z.slice(0, n).join(" "), reszta: z.slice(n).join(" ") };
}

/** Akapit pytania bez punktów → {krotko, reszta}: pierwsze zdanie (kontekst) i najwyżej dwa zdania-pytania („…?”),
 * żeby samo pytanie nie schowało się w szczegółach; bez zdań-pytań — dwa pierwsze zdania. */
function akapitPytania(tekst) {
  const z = zdania(tekst);
  const pytajace = z.map((x, i) => (i > 0 && /\?["”»)]*$/.test(x) ? i : -1)).filter((i) => i > 0).slice(0, 2);
  const pokaz = new Set(pytajace.length ? [0, ...pytajace] : [0, 1]);
  return { krotko: z.filter((_, i) => pokaz.has(i)).join(" "), reszta: z.filter((_, i) => !pokaz.has(i)).join(" ") };
}

/**
 * Treść pytania (bez wiersza „Rozstrzyga:”) → {krotko, szczegoly} w Markdownie. Krótko = punkty i krótkie wiersze
 * z góry treści (starsze pytania bez punktów: pierwsze zdanie i zdania-pytania); szczegóły = wiersz „Szczegóły:” i wszystko pod nim
 * (bez samej etykiety), wiersze „Dopisek …” i „Sprostowanie …” oraz reszta długiego akapitu.
 */
export function podzielPytanie(md) {
  const linie = bezWierszaRozstrzyga(String(md || "").replace(/\r\n?/g, "\n")).split("\n");
  const gora = [];
  const szczegoly = [];
  let wSzczegolach = false;
  for (const l of linie) {
    if (!wSzczegolach && RX_SZCZEGOLY.test(l)) {
      wSzczegolach = true;
      const reszta = l.replace(RX_SZCZEGOLY, "").trim();
      if (reszta) szczegoly.push(reszta);
      continue;
    }
    if (wSzczegolach || RX_DOPISEK.test(l)) szczegoly.push(l);
    else gora.push(l);
  }
  let krotko = gora.join("\n").trim();
  if (krotko && !gora.some((l) => RX_PUNKT.test(l))) {          // sam akapit: kontekst i pytanie, reszta zwinięta
    const z = akapitPytania(krotko);
    krotko = z.krotko;
    if (z.reszta) szczegoly.unshift(z.reszta);
  }
  return { krotko, szczegoly: szczegoly.join("\n").trim() };
}

/** Opis decyzji albo raportu → {krotko, reszta}: najwyżej dwa pierwsze zdania (albo dwa pierwsze punkty) pierwszego
 * akapitu, reszta zwinięta. */
export function skrotOpisu(md, n = 2) {
  const linie = String(md || "").replace(/\r\n/g, "\n").split("\n");
  let i = 0;
  while (i < linie.length && !linie[i].trim()) i++;
  if (i >= linie.length) return { krotko: "", reszta: "" };
  const reszta = (od) => linie.slice(od).join("\n").trim();
  if (RX_PUNKT.test(linie[i])) {                              // lista: dwa pierwsze punkty
    let j = i;
    let punkty = 0;
    while (j < linie.length && punkty < n && linie[j].trim() && (RX_PUNKT.test(linie[j]) || /^\s{2,}\S/.test(linie[j]))) {
      if (RX_PUNKT.test(linie[j])) punkty++;
      j++;
    }
    while (j < linie.length && /^\s{2,}\S/.test(linie[j])) j++;   // wcięte dalsze wiersze ostatniego punktu
    return { krotko: linie.slice(i, j).join("\n").trim(), reszta: reszta(j) };
  }
  let j = i;
  while (j < linie.length && linie[j].trim() && !RX_PUNKT.test(linie[j]) && !/^\s*#/.test(linie[j])) j++;
  const z = pierwszeZdania(linie.slice(i, j).join("\n"), n);
  return { krotko: z.krotko, reszta: [z.reszta, reszta(j)].filter(Boolean).join("\n\n") };
}

/** Tekst bez znaczników Markdown (do tytułów i etykiet): [[a|b]] → b, [[a]] → a, `kod` → kod. */
export function zwykly(t) {
  return String(t || "").replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2").replace(/\[\[([^\]]+)\]\]/g, "$1")
    .replace(/[`*_]/g, "").replace(/\s+/g, " ").trim();
}

/** Do wyszukiwania: małe litery, bez polskich znaków i znaczników. */
export function doSzukania(t) {
  return zwykly(t).toLowerCase().replace(/ł/g, "l").normalize("NFD").replace(/[̀-ͯ]/g, "");
}

/** Czy tekst sprawy pasuje do zapytania (wszystkie słowa zapytania muszą wystąpić). */
export function pasuje(s, zapytanie) {
  const slowa = doSzukania(zapytanie).split(" ").filter(Boolean);
  if (!slowa.length) return true;
  const t = s.szukaj || "";
  return slowa.every((w) => t.includes(w));
}

/** Źródła tematów „Do omówienia” z agendy sesji głównych: Set("D-009", "pytanie 19"). */
export function zrodlaAgendy(agenda) {
  const wynik = new Set();
  for (const t of (agenda && agenda.do_omowienia) || []) {
    for (const z of t.zrodla || []) {
      const n = numerDecyzji(z);
      if (n !== null) wynik.add(idDecyzji(n));
      const mp = /^\s*pytani[ea]\s+(?:nr\s+)?(\d{1,4})\s*$/i.exec(String(z));
      if (mp) wynik.add("pytanie " + Number(mp[1]));
    }
  }
  return wynik;
}

/** Mapa numer → decyzja (pierwsza o danym numerze). */
export function mapaDecyzji(plan) {
  const m = new Map();
  for (const d of (plan && plan.decyzje) || []) {
    const n = numerDecyzji(d.id);
    if (n !== null && !m.has(n)) m.set(n, d);
  }
  return m;
}

// ----------------------------------------------------------------------------- daty (do kolejności)
function dzisiaj() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

/** Najpóźniejsza data w tekście: 2026-11-14, 14.11.2026 albo 14.11 (bieżący rok); daty z przyszłości pomija. */
export function ostatniaData(tekst) {
  const t = String(tekst || "");
  const dzis = dzisiaj();
  const rok = dzis.slice(0, 4);
  let max = "";
  const dodaj = (r, m, d) => {
    const mm = Number(m);
    const dd = Number(d);
    if (mm < 1 || mm > 12 || dd < 1 || dd > 31) return;
    const s = r + "-" + String(mm).padStart(2, "0") + "-" + String(dd).padStart(2, "0");
    if (s <= dzis && s > max) max = s;
  };
  for (const m of t.matchAll(/\b(20\d\d)-(\d\d)-(\d\d)\b/g)) dodaj(m[1], m[2], m[3]);
  // bez „lookbehind” w wyrażeniach: starsze Safari na telefonach go nie zna (moduł by się nie wczytał)
  for (const m of t.matchAll(/(^|[^\d.])(\d{1,2})\.(\d{1,2})\.(20\d\d)\b/g)) dodaj(m[4], m[3], m[2]);
  // krótka forma „14.11” tylko z dwucyfrowym miesiącem (inaczej „wersja 1.5” byłaby datą)
  for (const m of t.matchAll(/(^|[^\d.])(\d{1,2})\.(\d{2})(?=$|[^\d.]|\.(?!\d))/g)) dodaj(rok, m[3], m[2]);
  return max;
}

const KOLEJNOSC_TYPOW = { raport: 0, pytanie: 1, decyzja: 2, potwierdzenie: 2 };

function porownaj(a, b) {
  return String(b.dzien).localeCompare(String(a.dzien)) || (b.waga || 0) - (a.waga || 0) ||
    String(b.czas || "").localeCompare(String(a.czas || "")) || KOLEJNOSC_TYPOW[a.typ] - KOLEJNOSC_TYPOW[b.typ] ||
    (b.nr || 0) - (a.nr || 0);
}

// ----------------------------------------------------------------------------- budowa listy
// Słowa statusu w tekście do szukania: „odrzucona”, „do poprawy”, „zaakceptowany” znajdują sprawy o tym statusie
// (dawne filtry Planu i Raportów). Kilka form, bo ludzie wpisują i „odrzucona”, i „odrzucone”.
export const SLOWA_STATUSU_DECYZJI = {
  zatwierdzona: "zatwierdzona zatwierdzone", odrzucona: "odrzucona odrzucone", zastapiona: "zastąpiona zastąpione",
  propozycja: "propozycja propozycje", do_decyzji: "do decyzji",
};
export const SLOWA_STATUSU_RAPORTU = {
  czeka: "czeka czekające", zaakceptowane: "zaakceptowany zaakceptowane", do_poprawy: "do poprawy", informacja: "informacja",
};

function tekstDecyzji(d) {
  return [d.id, d.tytul, (d.meta || []).join(" "), d.opis_md, d.kategoria, SLOWA_STATUSU_DECYZJI[d.status] || d.status,
    d.czeka_na ? "czeka na potwierdzenie " + d.czeka_na : "", d.potwierdzil ? "potwierdzona dwa podpisy" : "",
    d.sprzeciw ? "sprzeciw brak zgody" : "", d.do_rozmowy ? "do rozmowy" : ""].join(" ");
}

/** Pytanie raportu jako tytuł karty: własne pole `pytanie` (krótkie, jedna linia) albo „Czy akceptujesz: …?”. */
export function pytanieRaportu(r) {
  const wl = zwykly(r && r.pytanie);
  if (wl && wl.length <= 180 && !/\n/.test(String(r.pytanie).trim())) return { tekst: wl, wlasne: true };
  return { tekst: "Czy akceptujesz: " + zwykly((r && r.tytul) || "raport") + "?", wlasne: false };
}

export function pytanieDecyzji(d) {
  return "Czy zatwierdzamy: " + zwykly((d && d.tytul) || (d && d.id) || "decyzję") + "?";
}

// ----------------------------------------------------------------------------- potwierdzanie decyzji (D-043)
// Serwer (bc/sejf.py) podaje przy decyzji: zdecydowal {kto, data}, potwierdzil, sprzeciw, do_rozmowy i czeka_na
// (imię drugiej osoby albo null). Starszy serwer tych pól nie ma — wtedy nic nie czeka na potwierdzenie.

/** Osoba kanoniczna jak na serwerze: pierwsze słowo imienia, małe litery, bez polskich znaków. */
export function kanoniczne(imie) {
  const s = String(imie || "").trim().split(/\s+/)[0] || "";
  return s.toLowerCase().replace(/ł/g, "l").normalize("NFD").replace(/[̀-ͯ]/g, "");
}

/** Czy ta decyzja czeka na potwierdzenie osoby `kto` (imię z panelu). */
export function czekaNaMnie(d, kto) {
  const ja = kanoniczne(kto);
  return !!(d && d.czeka_na && ja && ja !== "gosc" && kanoniczne(d.czeka_na) === ja);
}

/** „Karol zatwierdził: Tytuł — zgadzasz się?” */
export function pytaniePotwierdzenia(d) {
  const kto = (d && d.zdecydowal && d.zdecydowal.kto) || "Ktoś";
  const czyn = d && d.status === "odrzucona" ? "odrzucił" : "zatwierdził";
  return kto + " " + czyn + ": " + zwykly((d && d.tytul) || (d && d.id) || "decyzję") + " — zgadzasz się?";
}

/**
 * zbudujPytania(plan, raporty, agenda, ja?) → {czekajace, odlozone, odpowiedziane}   (ja = ctx.ja: imię do potwierdzeń)
 * sprawa: {typ:"pytanie"|"decyzja"|"raport"|"potwierdzenie", klucz, zrodlo?, pytanie (tytuł karty), pochodzenie (mała etykieta),
 *          dzien, czas, waga, nr, szukaj, p?, d?, r?, decyzje?:[{id, d}], powiazane?:[{id, d}], odlozona, zamknieta}
 * klucz: "pytanie-19", "D-009" (powtórzony numer: "D-031~2"), "raport-<id>" (adres #/pytania?sprawa=<klucz>).
 */
export function zbudujPytania(plan, raporty, agenda, ja) {
  const kto = ja && ja.kto;                                    // potwierdzenia: tylko te, które czekają na MNIE
  const decyzje = mapaDecyzji(plan);
  const decyzja = (id) => decyzje.get(numerDecyzji(id)) || null;
  const odlozoneZrodla = zrodlaAgendy(agenda);
  const czekajace = [];
  const odpowiedziane = [];
  const przypiete = new Set();

  for (const r of raporty || []) {
    if (!r || !r.id) continue;
    const pyt = pytanieRaportu(r);
    const czeka = r.status === "czeka";
    const czas = czeka ? r.czas || "" : (r.decyzja && r.decyzja.czas) || r.czas || "";
    const s = {
      typ: "raport", klucz: "raport-" + r.id, pytanie: pyt.tekst, tytul: r.tytul || "(bez tytułu)", pochodzenie: "z raportu",
      dzien: String(czas).slice(0, 10), czas, waga: 1, nr: 0, r, odlozona: false, zamknieta: !czeka,
      szukaj: doSzukania([pyt.tekst, r.tytul, r.opis_md, r.pytanie, r.kto, r.id, "raport",
        r.decyzja && r.decyzja.komentarz, SLOWA_STATUSU_RAPORTU[r.status] || r.status].join(" ")),
    };
    (czeka ? czekajace : odpowiedziane).push(s);
  }

  const pytania = ((plan && plan.pytania) || []).filter(Boolean);
  for (const p of pytania) {
    const roz = rozstrzyga(p).map((id) => ({ id, d: decyzja(id) }));
    const pow = powiazane(p).map((id) => ({ id, d: decyzja(id) }));
    const zrodlo = "pytanie " + p.nr;
    const otwarteDec = roz.filter((x) => x.d && OTWARTE_DECYZJE.includes(x.d.status));
    let dzien = ostatniaData(p.otwarte ? p.tytul + "\n" + p.tresc_md : p.odpowiedz_md) ||
      ostatniaData(p.tytul + "\n" + p.tresc_md);
    if (!dzien) {
      for (const x of [...roz, ...pow]) {
        const dd = x.d ? ostatniaData((x.d.meta || []).join(" ")) : "";
        if (dd > dzien) dzien = dd;
      }
    }
    const s = {
      typ: "pytanie", klucz: "pytanie-" + p.nr, zrodlo, pytanie: zwykly(p.tytul) || "Pytanie #" + p.nr, tytul: p.tytul || "",
      pochodzenie: "pytanie #" + p.nr, dzien, czas: "", waga: otwarteDec.length ? 2 : 1, nr: p.nr || 0, p,
      decyzje: roz, powiazane: pow, odlozona: p.otwarte && odlozoneZrodla.has(zrodlo), zamknieta: !p.otwarte,
      szukaj: doSzukania([p.tytul, p.tresc_md, p.odpowiedz_md, "pytanie #" + p.nr, p.otwarte ? "bez odpowiedzi" : "odpowiedziane",
        ...roz.map((x) => x.d ? tekstDecyzji(x.d) : x.id)].join(" ")),
    };
    if (p.otwarte) {
      for (const x of roz) if (x.d) przypiete.add(numerDecyzji(x.id));
      czekajace.push(s);
    } else odpowiedziane.push(s);
  }

  const widziane = new Map();
  for (const d of (plan && plan.decyzje) || []) {
    const n = numerDecyzji(d.id);
    if (n === null) continue;
    const ile = (widziane.get(n) || 0) + 1;                    // ten sam numer drugi raz (błąd w Rejestrze): osobna karta
    widziane.set(n, ile);
    const otwarta = OTWARTE_DECYZJE.includes(d.status);
    if (otwarta && przypiete.has(n) && ile === 1) continue;    // ta decyzja jest już w karcie swojego pytania
    const zrodlo = idDecyzji(n);
    const meta = (d.meta || []).join(" ");
    if (ile === 1 && czekaNaMnie(d, kto)) {                    // druga osoba zdecydowała — pytanie do mnie (D-043)
      const p = pytaniePotwierdzenia(d);
      czekajace.push({
        typ: "potwierdzenie", klucz: d.id, zrodlo, pytanie: p, tytul: d.tytul || "",
        pochodzenie: "decyzja " + d.id + " · potwierdzenie",
        dzien: (d.zdecydowal && d.zdecydowal.data) || ostatniaData(meta), czas: "", waga: 2, nr: n, d,
        odlozona: odlozoneZrodla.has(zrodlo), zamknieta: false,
        szukaj: doSzukania([p, tekstDecyzji(d), "decyzja", "potwierdzenie czeka na potwierdzenie"].join(" ")),
      });
      continue;
    }
    const s = {
      // w historii też jako pytanie — odpowiedzią jest status (zatwierdzona / odrzucona / zastąpiona)
      typ: "decyzja", klucz: d.id + (ile > 1 ? "~" + ile : ""), zrodlo, pytanie: pytanieDecyzji(d),
      tytul: d.tytul || "",
      pochodzenie: "decyzja " + d.id, dzien: ostatniaData(meta), czas: "", waga: d.status === "do_decyzji" ? 2 : 1, nr: n, d,
      powtorzona: ile > 1, odlozona: otwarta && odlozoneZrodla.has(zrodlo), zamknieta: !otwarta,
      szukaj: doSzukania([pytanieDecyzji(d), tekstDecyzji(d), "decyzja"].join(" ")),
    };
    if (otwarta) czekajace.push(s);
    else if (ZAMKNIETE_DECYZJE.includes(d.status)) odpowiedziane.push(s);
  }

  czekajace.sort(porownaj);
  odpowiedziane.sort((a, b) => String(b.dzien).localeCompare(String(a.dzien)) ||
    String(b.czas || "").localeCompare(String(a.czas || "")) || (b.nr || 0) - (a.nr || 0));
  return {
    czekajace: czekajace.filter((s) => !s.odlozona), odlozone: czekajace.filter((s) => s.odlozona), odpowiedziane,
  };
}

/** Zgodność wstecz (Pulpit, powłoka): {aktywne, odlozone, wszystkie} — tylko sprawy czekające. */
export function zbudujKolejke(plan, raporty, agenda, ja) {
  const k = zbudujPytania(plan, raporty, agenda, ja);
  return { aktywne: k.czekajace, odlozone: k.odlozone, wszystkie: [...k.czekajace, ...k.odlozone], odpowiedziane: k.odpowiedziane };
}

/** Pytania otwarte, których wszystkie decyzje z wiersza „Rozstrzyga:” są już zamknięte (do podpowiedzi). */
export function pytaniaZamknieteDecyzjami(plan, numerZmienionej) {
  const decyzje = mapaDecyzji(plan);
  return ((plan && plan.pytania) || []).filter((p) => {
    const lista = rozstrzyga(p).map(numerDecyzji);
    if (!p.otwarte || !lista.length || (numerZmienionej != null && !lista.includes(numerZmienionej))) return false;
    return lista.every((n) => decyzje.get(n) && ZAMKNIETE_DECYZJE.includes(decyzje.get(n).status));
  });
}

/**
 * Pobiera plan, raporty i agendę i składa listę (dla Pulpitu i plakietki). Brak modułu albo trasy = pusta część.
 * → {kolejka, plan, raporty, agenda, bledy:{plan?, raporty?}}
 */
export async function pobierzKolejke(ctx) {
  const bierz = (sciezka, modul) => (ctx.jest(modul) ? ctx.api(sciezka, { czas: 20000 }) : Promise.reject(Object.assign(new Error("moduł wyłączony"), { status: 404 })));
  const [plan, rap, agenda] = await Promise.allSettled([
    bierz("/api/sejf/plan", "sejf"), bierz("/api/raporty", "raporty"), bierz("/api/sesje/agenda", "sesje"),
  ]);
  const p = plan.status === "fulfilled" ? plan.value || {} : null;
  const r = rap.status === "fulfilled" ? (rap.value && rap.value.raporty) || [] : null;
  const a = agenda.status === "fulfilled" ? agenda.value || null : null;
  return {
    kolejka: zbudujKolejke(p || {}, r || [], a, ctx.ja), plan: p, raporty: r, agenda: a,
    bledy: { plan: plan.status === "rejected" ? plan.reason : null, raporty: rap.status === "rejected" ? rap.reason : null },
  };
}
