// Wytwórnia: wszystkie gry i pomysły zespołu w jednym miejscu (dane z notatek B&C/Wytwórnia — bc/wytwornia.py).
//
// Trzy widoki w jednej zakładce (adres #/wytwornia[?pomysl=<id>|?gra=<id>]):
// - lista: portfel gier (etap prototyp / test / publiczna, z metrykami), lejek pomysłów (kolumny wg etapu, wstrzymane
//   i porzucone zwinięte na dole), radar trendów; przycisk „Dodaj pomysł” (nowa notatka z szablonu);
// - karta pomysłu (?pomysl=): zdanie, oceny (paski 0–30), karta oceny 10 kryteriów × Agent / Karol / Paweł,
//   „Krytyka agenta” wyróżniona, reszta notatki sekcjami, komentarze; „Oceń” i „Zmień etap” dla decydenta;
// - pulpit gry (?gra=): metryki, raporty panelu z tytułem zaczynającym się od nazwy gry, zadania i decyzje, które ją
//   wspominają (reguła w bc/wytwornia.py i README).
// Ocenę i etap zmienia tylko decydent (Karol albo Paweł przy komputerze z panelem albo z kluczem zatwierdzania); gość
// może dodać pomysł. Lista odświeża się w tle co 30 s.

import { el, zamien, ikona, czasTemu, pusty, stanBledu, ladowanie, toast, arkusz, odmiana } from "../wspolne/ui.js";
import { mdEl } from "../wspolne/markdown.js";
import { komentarze } from "../wspolne/komentarze.js";
import { ETAPY, ETAPY_LEJKA, ETAPY_GIER, NAZWY_ETAPOW, MAKS_SUMY, dolaczStyl, kanon, chipEtapu, chipWerdyktu,
  wartoscMetryki, maMetryki, metrykiEl, paskiOcen, kartaGry, adresPomyslu, adresGry, METRYKI } from "../wspolne/wytwornia.js";

const enc = encodeURIComponent;
const ODSWIEZ_MS = 30000;
const OSOBY = { karol: { nazwa: "Karol", pole: "karol" }, pawel: { nazwa: "Paweł", pole: "pawel" } };
const STATUSY_RAPORTU = { czeka: ["zloto", "czeka"], zaakceptowane: ["zielen", "zaakceptowany"], do_poprawy: ["czerwien", "do poprawy"],
  informacja: ["niebieski", "informacja"], nieaktualne: ["szary", "nieaktualny"] };
const STATUSY_DECYZJI = { zatwierdzona: ["zielen", "zatwierdzona"], odrzucona: ["czerwien", "odrzucona"], do_decyzji: ["zloto", "do decyzji"],
  propozycja: ["fiolet", "propozycja"], zastapiona: ["szary", "zastąpiona"], nieaktualna: ["szary", "nieaktualna"] };
const POMIJANE_SEKCJE = ["karta oceny", "krytyka agenta"];

const proste = (s) => String(s || "").toLowerCase().replace(/ł/g, "l").normalize("NFD").replace(/[̀-ͯ]/g, "").trim();

export default {
  id: "wytwornia",
  tytul: "Wytwórnia",
  ikona: "zarowka",
  kolejnosc: 25,
  utworz(ctx) {
    dolaczStyl();
    const korzen = el("div", { class: "widok wytwornia" });
    let tryb = null;                 // "lista" | "pomysl" | "gra"
    let dane = null;                 // ostatnia odpowiedź GET /api/wytwornia
    let sygnatura = "";
    let stop = null;
    let biezacy = null;              // id pomysłu / gry na ekranie szczegółów

    const mozeZapisac = () => !ctx.statyczny && ctx.ja.zapis_sejfu !== false;
    const decydent = () => !ctx.statyczny && !!(ctx.ja.decydent !== undefined ? ctx.ja.decydent : ctx.ja.game_director || ctx.ja.lokalny);
    const osoba = () => OSOBY[kanon(ctx.ja.kto)] || null;

    // ------------------------------------------------------------------ lista
    function naglowek() {
      const dodaj = mozeZapisac() ? el("button", { class: "przycisk glowny", type: "button", onclick: oknoDodawania }, ikona("plus"), el("span", null, "Dodaj pomysł")) : null;
      return el("header", { class: "nagl-widoku wyt-nagl" },
        el("div", null, el("h1", null, "Wytwórnia"),
          el("p", { class: "cichy-tekst" }, "Gry i pomysły zespołu: etap, ocena, krytyka agenta, trendy i liczby graczy. Dane z notatek sejfu B&C/Wytwórnia.")),
        dodaj);
    }

    function kartaPomyslu(p) {
      const metryki = maMetryki(p) ? METRYKI.map((m) => {
        const w = wartoscMetryki(m.id, (p.metryki || {})[m.id]);
        return w === null ? null : m.tekst + " " + w;
      }).filter(Boolean).join(" · ") : "";
      return el("a", { class: "wyt-karta", href: adresPomyslu(p.id), dataset: { pomysl: p.id } },
        el("div", { class: "wyt-karta-gora" }, el("strong", { class: "wyt-karta-nazwa" }, p.nazwa), chipWerdyktu(p.werdykt_agenta, { krotko: true })),
        p.zdanie ? el("p", { class: "wyt-zdanie" }, p.zdanie) : el("p", { class: "wyt-zdanie cichy-tekst" }, "Bez zdania — uzupełnij w notatce."),
        paskiOcen(p),
        metryki ? el("p", { class: "cichy-tekst wyt-karta-metryki" }, metryki) : null);
    }

    function rysujListe() {
      const d = dane || {};
      const pomysly = d.pomysly || [];
      const po = new Map(pomysly.map((p) => [p.id, p]));
      const czesci = [naglowek()];
      if (d.jest === false) {
        czesci.push(el("p", { class: "wyt-info" }, ikona("info"), el("span", null,
          "Folderu B&C/Wytwórnia jeszcze nie ma w sejfie. Pomysł dodany tutaj założy go sam (B&C/Wytwórnia/Pomysły/).")));
      }
      // --- portfel gier
      const gry = (d.gry || []).map((id) => po.get(id)).filter(Boolean)
        .sort((a, b) => ETAPY_GIER.indexOf(b.etap) - ETAPY_GIER.indexOf(a.etap));
      czesci.push(el("section", { class: "wyt-sekcja", "aria-labelledby": "wyt-gry" },
        el("h2", { class: "wyt-h2", id: "wyt-gry" }, ikona("rakieta"), el("span", null, "Portfel gier"), el("span", { class: "chip-licznik" }, String(gry.length))),
        gry.length ? el("div", { class: "wyt-gry" }, gry.map((p) => kartaGry(p)))
          : el("p", { class: "cichy-tekst" }, "Żadna gra nie jest jeszcze na etapie prototypu, testu ani publicznym. Etap ustawia się w karcie pomysłu.")));
      // --- lejek
      const lejek = d.lejek || {};
      const kolumny = ETAPY_LEJKA.map((e) => {
        const lista = (lejek[e] || []).map((id) => po.get(id)).filter(Boolean);
        return el("section", { class: "wyt-kolumna", dataset: { etap: e }, "aria-label": "Etap: " + NAZWY_ETAPOW[e] },
          el("h3", { class: "wyt-kolumna-nagl" }, chipEtapu(e), el("span", { class: "cichy-tekst" }, lista.length + " " + odmiana(lista.length, ["pozycja", "pozycje", "pozycji"]))),
          lista.length ? el("div", { class: "wyt-kolumna-lista" }, lista.map(kartaPomyslu)) : el("p", { class: "cichy-tekst wyt-pusto" }, "—"));
      });
      const zwiniete = ["wstrzymana", "porzucona"].flatMap((e) => (lejek[e] || []).map((id) => po.get(id)).filter(Boolean));
      czesci.push(el("section", { class: "wyt-sekcja", "aria-labelledby": "wyt-lejek" },
        el("h2", { class: "wyt-h2", id: "wyt-lejek" }, ikona("zarowka"), el("span", null, "Lejek pomysłów"), el("span", { class: "chip-licznik" }, String(pomysly.length))),
        pomysly.length ? el("div", { class: "wyt-lejek" }, kolumny)
          : pusty("Brak pomysłów", mozeZapisac() ? "Dodaj pierwszy przyciskiem „Dodaj pomysł” — powstanie notatka w B&C/Wytwórnia/Pomysły." : "Pomysły to notatki w B&C/Wytwórnia/Pomysły.", "zarowka"),
        zwiniete.length ? el("details", { class: "wyt-zwiniete" },
          el("summary", null, ikona("dol"), el("span", null, "Wstrzymane i porzucone (" + zwiniete.length + ")")),
          el("div", { class: "wyt-kolumna-lista siatka-kart" }, zwiniete.map((p) => {
            const k = kartaPomyslu(p);
            k.querySelector(".wyt-karta-gora").append(chipEtapu(p.etap));
            return k;
          }))) : null));
      // --- radar trendów
      czesci.push(sekcjaRadaru(d.radar || {}));
      zamien(korzen, czesci);
    }

    function sekcjaRadaru(r) {
      const naglowekR = el("h2", { class: "wyt-h2", id: "wyt-radar" }, ikona("zdrowie"), el("span", null, "Radar trendów"));
      if (!r.jest) {
        return el("section", { class: "wyt-sekcja", "aria-labelledby": "wyt-radar" }, naglowekR,
          el("p", { class: "cichy-tekst" }, "Notatki „Radar trendów” jeszcze nie ma w B&C/Wytwórnia."));
      }
      const pozycje = r.pozycje || [];
      return el("section", { class: "wyt-sekcja", "aria-labelledby": "wyt-radar" }, naglowekR,
        el("p", { class: "cichy-tekst" }, "Aktualizacja: " + (r.aktualizacja || "brak daty") + " · ",
          el("a", { href: "#", onclick: (e) => { e.preventDefault(); ctx.idz("siec", { notatka: "Radar trendów" }); } }, "notatka w sejfie")),
        pozycje.length ? el("div", { class: "wyt-radar" }, pozycje.map((t) => el("article", { class: "wyt-trend" },
          el("div", { class: "wyt-trend-gora" },
            mdEl(t.trend, { linia: true, klasa: "wyt-trend-nazwa" }),
            t.sila ? mdEl(t.sila, { linia: true, klasa: "chip zloto wyt-chip-md" }) : null,
            t.kierunek ? mdEl(t.kierunek, { linia: true, klasa: "chip wyt-chip-md " + kolorKierunku(t.kierunek) }) : null),
          t.przyklady ? el("div", { class: "wyt-trend-wiersz" }, el("span", { class: "etykieta" }, "Przykłady"), mdEl(t.przyklady, { linia: true })) : null,
          t.zrodlo ? el("div", { class: "wyt-trend-wiersz" }, el("span", { class: "etykieta" }, "Źródło"), mdEl(t.zrodlo, { linia: true, klasa: "cichy-tekst" })) : null)))
          : el("p", { class: "cichy-tekst" }, "Tabela trendów jest pusta."));
    }

    function kolorKierunku(k) {
      const p = proste(k);
      if (/(rosn|w gore|↑|wzrost|rosnie)/.test(p)) return "zielen";
      if (/(spad|w dol|↓|maleje)/.test(p)) return "czerwien";
      return "szary";
    }

    async function odswiezListe(cicho) {
      try {
        const d = await ctx.api("/api/wytwornia");
        const s = JSON.stringify(d);
        dane = d;
        if (tryb !== "lista") return;
        if (s === sygnatura && cicho) return;
        sygnatura = s;
        rysujListe();
      } catch (e) {
        if (tryb === "lista" && !cicho) zamien(korzen, naglowek(), stanBledu(e, "Wytwórnia"));
      }
    }

    // ------------------------------------------------------------------ karta pomysłu
    function powrot() {
      return el("a", { class: "przycisk cichy maly wyt-powrot", href: "#/wytwornia" }, ikona("wstecz"), el("span", null, "Wytwórnia"));
    }

    function kropki(v) {
      if (v === null || v === undefined) return el("span", { class: "wyt-kropki brak", "aria-label": "bez oceny" }, "—");
      return el("span", { class: "wyt-kropki", "aria-label": v + " z 3", title: v + " z 3" },
        [0, 1, 2].map((i) => el("span", { class: "wyt-kropka" + (i < v ? " pelna" : ""), "aria-hidden": "true" })),
        el("span", { class: "wyt-kropki-liczba" }, String(v)));
    }

    function tabelaKarty(p, kryteria) {
      const opisy = new Map((kryteria || []).map((k) => [k.nazwa, k.opis]));
      const sumy = p.sumy || {};
      return el("div", { class: "wyt-tabela-ramka" }, el("table", { class: "wyt-tabela" },
        el("thead", null, el("tr", null, el("th", { scope: "col" }, "Kryterium"), el("th", { scope: "col" }, "Agent"), el("th", { scope: "col" }, "Karol"), el("th", { scope: "col" }, "Paweł"))),
        el("tbody", null, (p.karta || []).map((w) => el("tr", null,
          el("th", { scope: "row", title: opisy.get(w.kryterium) || "" }, w.kryterium,
            opisy.get(w.kryterium) ? el("span", { class: "wyt-opis-kryterium" }, opisy.get(w.kryterium)) : null),
          el("td", null, kropki(w.agent)), el("td", null, kropki(w.karol)), el("td", null, kropki(w.pawel))))),
        el("tfoot", null, el("tr", null, el("th", { scope: "row" }, "Suma"),
          ["agent", "karol", "pawel"].map((k) => el("td", null, sumy[k] === null || sumy[k] === undefined ? "—" : sumy[k] + "/" + MAKS_SUMY))))));
    }

    function rysujPomysl(p) {
      const kryteria = (dane && dane.kryteria) || [];
      const ja = osoba();
      const akcje = [];
      if (decydent() && mozeZapisac()) {
        akcje.push(el("button", { class: "przycisk glowny", type: "button", disabled: !ja, onclick: () => oknoOceny(p, kryteria) },
          ikona("ok"), el("span", null, ja ? "Oceń (" + ja.nazwa + ")" : "Oceń")));
        akcje.push(el("button", { class: "przycisk", type: "button", onclick: () => oknoEtapu(p) }, ikona("flaga"), el("span", null, "Zmień etap")));
      }
      if (ETAPY_GIER.includes(p.etap)) akcje.push(el("a", { class: "przycisk", href: adresGry(p.id) }, ikona("analityka"), el("span", null, "Pulpit gry")));
      akcje.push(el("button", { class: "przycisk cichy", type: "button", onclick: () => ctx.idz("siec", { notatka: p.tytul }) }, ikona("siec"), el("span", null, "W sieci")));
      const uwagaPraw = !decydent() && !ctx.statyczny
        ? el("p", { class: "cichy-tekst" }, ikona("klodka"), " Ocenę i etap zmienia Karol albo Paweł — przy komputerze z panelem albo z kluczem zatwierdzania.")
        : decydent() && !ja && mozeZapisac() ? el("p", { class: "cichy-tekst" }, ikona("info"), " Ocena trafia do kolumny osoby: wpisz w Ustawieniach imię Karol albo Paweł.") : null;

      const sekcje = (p.sekcje || []).filter((s) => !POMIJANE_SEKCJE.some((x) => proste(s.tytul).startsWith(x)));
      const pelne = sekcje.filter((s) => s.tresc_md && !(proste(s.tytul).startsWith("w jednym zdaniu") && s.tresc_md.trim() === (p.zdanie || "").trim()));
      const puste = sekcje.filter((s) => !s.tresc_md).map((s) => s.tytul);

      zamien(korzen, 
        powrot(),
        el("header", { class: "wyt-szczegol-nagl" },
          el("h1", null, p.nazwa),
          el("div", { class: "chipy" }, chipEtapu(p.etap), chipWerdyktu(p.werdykt_agenta), p.status ? el("span", { class: "chip szary" }, p.status) : null),
          p.zdanie ? el("p", { class: "wyt-zdanie-duze" }, p.zdanie) : null),
        el("div", { class: "rzad-przyciskow wyt-akcje" }, akcje), uwagaPraw,
        maMetryki(p) || ETAPY_GIER.includes(p.etap) ? metrykiEl(p) : null,
        el("section", { class: "wyt-sekcja karta" },
          el("h2", { class: "wyt-h2" }, ikona("decyzja"), el("span", null, "Karta oceny")),
          paskiOcen(p),
          tabelaKarty(p, kryteria),
          el("p", { class: "cichy-tekst" }, "Każde kryterium 0–3, razem najwyżej " + MAKS_SUMY + ". Kolumnę Agent wypełnia agent, Karol i Paweł — przyciskiem „Oceń”.")),
        p.krytyka_md ? el("section", { class: "wyt-krytyka" },
          el("h2", { class: "wyt-h2" }, ikona("ostrzezenie"), el("span", null, "Krytyka agenta")),
          mdEl(p.krytyka_md)) : null,
        pelne.map((s) => el("section", { class: "wyt-sekcja wyt-sekcja-notatki" }, el("h2", { class: "wyt-h3" }, s.tytul), mdEl(s.tresc_md))),
        puste.length ? el("p", { class: "cichy-tekst" }, "Do uzupełnienia w notatce: " + puste.join(", ") + ".") : null,
        el("p", { class: "cichy-tekst wyt-sciezka" }, ikona("notatka"), " ", el("code", null, p.sciezka || ""), p.zmieniono ? " · zmieniono " + czasTemu(p.zmieniono) : ""),
        ctx.statyczny ? null : el("section", { class: "wyt-sekcja" }, el("h2", { class: "wyt-h3" }, "Komentarze"),
          komentarze(ctx, { typ: "notatka", cel: p.sciezka, etykieta: "Pomysł: " + p.nazwa })));
    }

    async function pokazPomysl(id, cicho) {
      biezacy = id;
      if (!cicho) zamien(korzen, powrot(), ladowanie("Wczytuję pomysł…"));
      try {
        if (!dane) dane = await ctx.api("/api/wytwornia").catch(() => null);
        const p = await ctx.api("/api/wytwornia/pomysly/" + enc(id));
        if (tryb !== "pomysl" || biezacy !== id) return p;
        rysujPomysl(p);
        return p;
      } catch (e) {
        if (tryb === "pomysl" && biezacy === id) zamien(korzen, powrot(), stanBledu(e, "Pomysł"));
        return null;
      }
    }

    // ------------------------------------------------------------------ okna: dodaj, oceń, etap
    function oknoDodawania() {
      const nazwa = el("input", { class: "pole", maxlength: "60", placeholder: "np. Ring Potworów", autocomplete: "off", "aria-label": "Nazwa gry" });
      const zdanie = el("textarea", { class: "pole", rows: 2, maxlength: "300", placeholder: "Kto, co robi i dlaczego to fajne — jednym zdaniem", "aria-label": "Jedno zdanie" });
      const hak = el("textarea", { class: "pole", rows: 2, maxlength: "600", placeholder: "Co sprawia, że gracz chce zobaczyć więcej? (opcjonalnie)", "aria-label": "Hak ciekawości" });
      const przycisk = el("button", { class: "przycisk glowny szeroki", type: "submit" }, ikona("plus"), el("span", null, "Dodaj do Wytwórni"));
      const kto = ctx.ja.kto && ctx.ja.kto !== "gość" ? ctx.ja.kto : "gość";
      const podpis = kto + (ctx.ja.lokalny ? "" : ctx.ja.game_director ? " (klucz zatwierdzania)" : " (gość panelu)");
      const form = el("form", { class: "formularz" },
        el("label", { class: "etykieta" }, "Nazwa gry"), nazwa,
        el("label", { class: "etykieta" }, "Jedno zdanie"), zdanie,
        el("label", { class: "etykieta" }, "Hak ciekawości"), hak,
        el("p", { class: "cichy-tekst" }, "Powstanie notatka B&C/Wytwórnia/Pomysły/<nazwa>.md z szablonu „Pomysł gry”, etap: pomysł. Ślad w Dzienniku zmian: " + podpis + "."),
        przycisk);
      const ark = arkusz({ tytul: "Nowy pomysł", tresc: form });
      let wToku = false;
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (wToku) return;
        if (!nazwa.value.trim()) return nazwa.focus();
        if (!zdanie.value.trim()) return zdanie.focus();
        wToku = true;
        przycisk.disabled = true;
        try {
          const w = await ctx.api("/api/wytwornia/pomysly", { metoda: "POST", cialo: { nazwa: nazwa.value.trim(), zdanie: zdanie.value.trim(), hak: hak.value.trim() } });
          ark.zamknij();
          toast("Dodano pomysł „" + w.id + "” — notatka jest w sejfie.", "ok");
          if (w.uwaga) toast(w.uwaga, "info", { czas: 8000 });
          dane = null;
          ctx.idz("wytwornia", { pomysl: w.id });
        } catch (err) {
          toast("Nie dodano: " + err.message, "blad");
          przycisk.disabled = false;
          wToku = false;
        }
      });
    }

    function oknoOceny(p, kryteria) {
      const ja = osoba();
      if (!ja) return;
      const opisy = new Map((kryteria || []).map((k) => [k.nazwa, k.opis]));
      const skale = new Map((kryteria || []).filter((k) => k.skala).map((k) => [k.nazwa, k.skala]));
      const wartosci = (p.karta || []).map((w) => (w[ja.pole] === undefined ? null : w[ja.pole]));
      let wersja = p.wersja;
      const sumaEl = el("strong", { class: "wyt-suma" });
      const odswiezSume = () => {
        const v = wartosci.filter((x) => x !== null);
        sumaEl.textContent = "Suma: " + (v.length ? v.reduce((a, b) => a + b, 0) : "—") + "/" + MAKS_SUMY + (v.length < wartosci.length ? " (" + v.length + " z " + wartosci.length + " kryteriów)" : "");
      };
      const wiersze = (p.karta || []).map((w, i) => {
        const przyciski = [null, 0, 1, 2, 3].map((v) => {
          const b = el("button", { type: "button", class: "wyt-skala-opcja", "aria-pressed": String(wartosci[i] === v), dataset: { v: v === null ? "" : String(v) } }, v === null ? "—" : String(v));
          b.addEventListener("click", () => {
            wartosci[i] = v;
            for (const x of skala.children) x.setAttribute("aria-pressed", String(x === b));
            odswiezSume();
          });
          return b;
        });
        const skala = el("div", { class: "wyt-skala", role: "group", "aria-label": w.kryterium }, przyciski);
        return el("div", { class: "wyt-kryterium" },
          el("div", { class: "wyt-kryterium-tekst" }, el("strong", null, (i + 1) + ". " + w.kryterium),
            opisy.get(w.kryterium) ? el("span", { class: "cichy-tekst" }, opisy.get(w.kryterium)) : null,
            skale.get(w.kryterium) ? el("span", { class: "cichy-tekst wyt-skala-opis" }, "0 — " + skale.get(w.kryterium)["0"] + " · 3 — " + skale.get(w.kryterium)["3"]) : null,
            w.agent !== null && w.agent !== undefined ? el("span", { class: "cichy-tekst" }, "Agent: " + w.agent) : null),
          skala);
      });
      odswiezSume();
      const przycisk = el("button", { class: "przycisk glowny szeroki", type: "submit" }, ikona("ok"), el("span", null, "Zapisz ocenę"));
      const form = el("form", { class: "formularz wyt-ocena-form" },
        el("p", { class: "cichy-tekst" }, "Twoja kolumna: " + ja.nazwa + ". 0 — słabo, 3 — świetnie, „—” — bez oceny. Zapis idzie do tabeli „Karta oceny” w notatce i do pola ocena_" + ja.pole + "."),
        wiersze, sumaEl, przycisk);
      const ark = arkusz({ tytul: "Ocena: " + p.nazwa, tresc: form, szeroki: true });
      let wToku = false;
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (wToku) return;
        wToku = true;
        przycisk.disabled = true;
        try {
          const w = await ctx.api("/api/wytwornia/pomysly/" + enc(p.id) + "/ocena", { metoda: "POST", cialo: { oceny: wartosci, wersja } });
          ark.zamknij();
          toast("Zapisano ocenę: " + (w.pomysl[("ocena_" + ja.pole)] ?? "—") + "/" + MAKS_SUMY + ".", "ok");
          if (w.uwaga) toast(w.uwaga, "info", { czas: 8000 });
          dane = null;
          if (tryb === "pomysl") rysujPomysl(w.pomysl);
        } catch (err) {
          if (err.status === 409 && err.dane && err.dane.kod === "konflikt_wersji") {
            const nowy = await ctx.api("/api/wytwornia/pomysly/" + enc(p.id)).catch(() => null);
            if (nowy) wersja = nowy.wersja;
            toast("Ktoś zmienił tę notatkę w międzyczasie — wczytałem nową wersję. Twoje oceny zostały w oknie: zapisz jeszcze raz.", "info", { czas: 8000 });
          } else toast("Nie zapisano oceny: " + err.message, "blad");
          przycisk.disabled = false;
          wToku = false;
        }
      });
    }

    function oknoEtapu(p) {
      const lista = el("div", { class: "wyt-etapy" }, ETAPY.map((e) => {
        const b = el("button", { type: "button", class: "przycisk" + (e === p.etap ? " wcisniety" : ""), "aria-pressed": String(e === p.etap), disabled: e === p.etap },
          chipEtapu(e), e === p.etap ? el("span", { class: "cichy-tekst" }, "teraz") : null);
        b.addEventListener("click", async () => {
          for (const x of lista.querySelectorAll("button")) x.disabled = true;
          try {
            const w = await ctx.api("/api/wytwornia/pomysly/" + enc(p.id) + "/etap", { metoda: "POST", cialo: { etap: e, wersja: p.wersja } });
            ark.zamknij();
            toast("Etap „" + p.nazwa + "”: " + NAZWY_ETAPOW[e] + ".", "ok");
            dane = null;
            if (tryb === "pomysl") rysujPomysl(w.pomysl);
          } catch (err) {
            toast("Nie zmieniono etapu: " + err.message, "blad");
            ark.zamknij();
            if (tryb === "pomysl") pokazPomysl(p.id, true);
          }
        });
        return b;
      }));
      const ark = arkusz({ tytul: "Etap: " + p.nazwa, tresc: el("div", { class: "formularz" },
        el("p", { class: "cichy-tekst" }, "Pomysł → ocena → prototyp → test → publiczna. Wstrzymane i porzucone są zwinięte na dole lejka. Zmiana trafia do pola „etap” notatki i do Dziennika zmian."), lista) });
    }

    // ------------------------------------------------------------------ pulpit gry
    function wierszRaportu(r) {
      const [kolor, tekst] = STATUSY_RAPORTU[r.status] || ["szary", r.status || ""];
      return el("li", null, el("a", { class: "wyt-wiersz", href: "#/pytania?raport=" + enc(r.id) },
        el("span", { class: "wyt-wiersz-tytul" }, r.tytul),
        el("span", { class: "wyt-wiersz-meta" }, el("span", { class: "chip " + kolor }, tekst), r.czas ? el("span", { class: "cichy-tekst" }, czasTemu(r.czas)) : null)));
    }

    function wierszZadania(z) {
      return el("li", { class: "wyt-wiersz" + (z.zrobione ? " zrobione" : "") },
        el("span", { class: "wyt-pole", "aria-label": z.zrobione ? "zrobione" : "do zrobienia" }, z.zrobione ? ikona("ok") : null),
        el("span", { class: "wyt-wiersz-tytul" }, mdEl(z.tekst_md, { linia: true })),
        el("span", { class: "wyt-wiersz-meta cichy-tekst" }, [z.sekcja, z.data, z.priorytet].filter(Boolean).join(" · ")));
    }

    function wierszDecyzji(d) {
      const [kolor, tekst] = STATUSY_DECYZJI[d.status] || ["szary", d.status || ""];
      return el("li", null, el("a", { class: "wyt-wiersz", href: "#/pytania?sprawa=" + enc(d.id) },
        el("span", { class: "wyt-wiersz-tytul" }, el("strong", null, d.id), " ", d.tytul),
        el("span", { class: "wyt-wiersz-meta" }, el("span", { class: "chip " + kolor }, tekst))));
    }

    function sekcjaListy(tytul, ikonaN, lista, wiersz, pusto, dodatek) {
      return el("section", { class: "wyt-sekcja karta" },
        el("h2", { class: "wyt-h2" }, ikona(ikonaN), el("span", null, tytul), el("span", { class: "chip-licznik" }, String(lista.length))),
        lista.length ? el("ul", { class: "lista wyt-lista" }, lista.map(wiersz)) : el("p", { class: "cichy-tekst" }, pusto), dodatek || null);
    }

    function rysujGre(g) {
      const p = g.pomysl;
      const otwarte = (g.zadania || []).filter((z) => !z.zrobione);
      const zrobione = (g.zadania || []).filter((z) => z.zrobione);
      zamien(korzen, 
        powrot(),
        el("header", { class: "wyt-szczegol-nagl" },
          el("p", { class: "etykieta" }, ikona("analityka"), "Pulpit gry"),
          el("h1", null, p.nazwa),
          el("div", { class: "chipy" }, chipEtapu(p.etap), chipWerdyktu(p.werdykt_agenta)),
          p.zdanie ? el("p", { class: "wyt-zdanie-duze" }, p.zdanie) : null),
        metrykiEl(p, { duze: true }),
        el("div", { class: "rzad-przyciskow wyt-akcje" },
          el("a", { class: "przycisk", href: adresPomyslu(p.id) }, ikona("notatka"), el("span", null, "Karta pomysłu")),
          p.miejsce ? el("a", { class: "przycisk cichy", href: "https://www.roblox.com/games/" + enc(p.miejsce), target: "_blank", rel: "noopener noreferrer" },
            ikona("zewnetrzny"), el("span", null, "Gra na Roblox")) : null),
        el("div", { class: "wyt-pulpit-siatka" },
          sekcjaListy("Raporty", "raporty", g.raporty || [], wierszRaportu, "Brak raportów, których tytuł zaczyna się od „" + (g.nazwy || [p.nazwa])[0] + "”."),
          sekcjaListy("Zadania", "plan", otwarte.concat(zrobione.slice(0, 10)), wierszZadania, "Brak zadań, które wspominają tę grę.",
            el("a", { class: "przycisk cichy maly", href: "#/pytania?sekcja=zadania" }, el("span", null, "Wszystkie zadania"), ikona("prawo"))),
          sekcjaListy("Decyzje", "decyzja", g.decyzje || [], wierszDecyzji, "Brak decyzji, które wspominają tę grę.")),
        el("p", { class: "cichy-tekst wyt-regula" }, ikona("info"), " Dopasowanie (do czasu tagów): " + (g.regula || "") +
          " Nazwy tej gry: " + (g.nazwy || []).map((n) => "„" + n + "”").join(", ") + "."));
    }

    async function pokazGre(id) {
      biezacy = id;
      zamien(korzen, powrot(), ladowanie("Wczytuję pulpit gry…"));
      try {
        const g = await ctx.api("/api/wytwornia/gry/" + enc(id));
        if (tryb === "gra" && biezacy === id) rysujGre(g);
      } catch (e) {
        if (tryb === "gra" && biezacy === id) zamien(korzen, powrot(), stanBledu(e, "Pulpit gry"));
      }
    }

    // ------------------------------------------------------------------ cykl życia
    return {
      el: korzen,
      pokaz(parametry = {}) {
        const poprzedni = tryb;
        if (parametry.pomysl) {
          tryb = "pomysl";
          pokazPomysl(String(parametry.pomysl));
        } else if (parametry.gra) {
          tryb = "gra";
          pokazGre(String(parametry.gra));
        } else {
          tryb = "lista";
          biezacy = null;
          if (poprzedni !== "lista" || !dane) {
            sygnatura = "";
            if (dane) rysujListe();
            else zamien(korzen, naglowek(), ladowanie("Wczytuję Wytwórnię…"));
          }
          odswiezListe(false);
        }
        if (!stop) stop = ctx.odpytuj(() => (tryb === "lista" ? odswiezListe(true) : null), ODSWIEZ_MS);
        if (poprzedni !== tryb || tryb !== "lista") window.scrollTo(0, 0);
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
