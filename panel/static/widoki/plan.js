// Plan: okno na sejf — harmonogram (roadmapa), zadania, decyzje, pytania otwarte, dziennik zmian.

import { el, ikona, czasTemu, dataKrotka, pusty, stanBledu, ladowanie, przelacznik, odmiana } from "../wspolne/ui.js";
import { md, mdLinia } from "../wspolne/markdown.js";

const ZAKLADKI = [
  { id: "harmonogram", tekst: "Harmonogram", ikona: "flaga" },
  { id: "zadania", tekst: "Zadania", ikona: "plan" },
  { id: "decyzje", tekst: "Decyzje", ikona: "decyzja" },
  { id: "pytania", tekst: "Pytania", ikona: "pytanie" },
  { id: "dziennik", tekst: "Dziennik", ikona: "dziennik" },
];

const STATUSY_DECYZJI = {
  zatwierdzona: { tekst: "zatwierdzona", kolor: "zielen", filtr: "Zatwierdzone" },
  do_decyzji: { tekst: "do decyzji", kolor: "zloto", filtr: "Do decyzji" },
  propozycja: { tekst: "propozycja", kolor: "fiolet", filtr: "Propozycje" },
  odrzucona: { tekst: "odrzucona", kolor: "czerwien", filtr: "Odrzucone" },
  zastapiona: { tekst: "zastąpiona", kolor: "szary", filtr: "Zastąpione" },
};
const PRIORYTETY = { wysoki: "czerwien", "średni": "zloto", sredni: "zloto", niski: "niebieski" };

const html = (tekst) => el("div", { class: "md", html: md(tekst || "") });
const linia = (tekst, klasa) => el("span", { class: "md md-linia" + (klasa ? " " + klasa : ""), html: mdLinia(tekst || "") });

function postep(f) {
  let p = Number(f.postep);
  if (f.postep === null || f.postep === undefined || !isFinite(p)) {
    const poz = f.pozycje || [];
    p = poz.length ? poz.filter((x) => x.zrobione).length / poz.length : 0;
  } else if (p > 1) p /= 100;
  return Math.max(0, Math.min(1, p));
}

function pozycjaZadania(p) {
  return el("li", { class: "wiersz zadanie-wiersz" + (p.zrobione ? " zrobione" : "") },
    el("span", { class: "pole-wyboru" + (p.zrobione ? " zaznaczone" : ""), "aria-label": p.zrobione ? "zrobione" : "do zrobienia", role: "img" },
      p.zrobione ? ikona("ok") : null),
    linia(p.tekst_md, "wiersz-tekst"),
    p.data ? el("span", { class: "cichy-tekst data-zadania" }, dataKrotka(p.data)) : null,
    p.priorytet ? el("span", { class: "chip " + (PRIORYTETY[p.priorytet] || "") }, p.priorytet) : null);
}

export default {
  id: "plan",
  tytul: "Plan",
  ikona: "plan",
  kolejnosc: 20,
  utworz(ctx) {
    let zakladka = "harmonogram";
    try {
      zakladka = localStorage.getItem("bc.plan.zakladka") || zakladka;
    } catch (e) { /* nic */ }
    if (!ZAKLADKI.some((z) => z.id === zakladka)) zakladka = "harmonogram";
    let filtrDecyzji = "wszystkie";
    let dane = null;
    let blad = null;
    let pobrano = 0;

    const tresc = el("div", { class: "plan-tresc" }, ladowanie("Czytam sejf…"));
    const zrodla = el("p", { class: "cichy-tekst plan-zrodla" });
    const segment = przelacznik(ZAKLADKI, zakladka, (id) => {
      zakladka = id;
      try {
        localStorage.setItem("bc.plan.zakladka", id);
      } catch (e) { /* nic */ }
      rysuj();
    }, "Część planu");
    const odswiezBtn = el("button", { class: "przycisk cichy ikonowy", type: "button", title: "Odśwież z sejfu", "aria-label": "Odśwież z sejfu", onclick: () => pobierz(true) }, ikona("odswiez"));
    const korzen = el("div", { class: "widok plan" },
      el("header", { class: "nagl-widoku" },
        el("div", null, el("h1", null, "Plan"), el("p", { class: "cichy-tekst" }, "Na żywo z sejfu Obsidiana (B&C/Produkcja).")),
        odswiezBtn),
      el("div", { class: "przelacznik-przewijany" }, segment),
      tresc, zrodla);

    // ------------------------------------------------------------------ harmonogram
    function harmonogram() {
      const r = dane.roadmapa || {};
      const fazy = r.fazy || [];
      const propozycje = r.propozycje || [];
      if (!fazy.length && !propozycje.length) return pusty("Roadmapa jest pusta", "Fazy opisuje notatka B&C/Produkcja/Roadmapa.md.", "flaga");
      const karty = fazy.map((f, i) => {
        const p = postep(f);
        const poz = f.pozycje || [];
        const zrob = poz.filter((x) => x.zrobione).length;
        return el("article", { class: "karta faza" + (f.aktywna ? " aktywna" : ""), style: { "--i": i } },
          el("div", { class: "faza-gora" },
            el("h2", { class: "faza-nazwa" }, String(f.nazwa || "").replace(/^[▶►\s]+/, "")),
            f.aktywna ? el("span", { class: "chip zloto" }, ikona("flaga"), "aktywna") : p >= 1 ? el("span", { class: "chip zielen" }, ikona("ok"), "gotowa") : null),
          f.status_tekst ? el("p", { class: "cichy-tekst" }, f.status_tekst) : null,
          f.opis ? html(f.opis) : null,
          el("div", { class: "faza-postep" },
            el("div", { class: "pasek" }, el("div", { class: "pasek-wypelnienie", style: { width: Math.round(p * 100) + "%" } })),
            el("span", { class: "faza-procent" }, Math.round(p * 100) + "%"),
            poz.length ? el("span", { class: "cichy-tekst" }, zrob + "/" + poz.length) : null),
          poz.length ? el("ul", { class: "lista" }, poz.map(pozycjaZadania)) : null);
      });
      const kartyProp = propozycje.map((p, i) => el("article", { class: "karta faza propozycja", style: { "--i": fazy.length + i } },
        el("div", { class: "faza-gora" },
          el("h2", { class: "faza-nazwa" }, (p.nr ? "Faza " + p.nr + " — " : "") + (p.nazwa || "")),
          el("span", { class: "chip fiolet" }, "propozycja")),
        p.opis_md ? html(p.opis_md) : null));
      return el("div", { class: "kolumna" }, karty,
        kartyProp.length ? el("h2", { class: "sekcja-naglowek" }, "Kolejne fazy (do zatwierdzenia)") : null, kartyProp);
    }

    // ------------------------------------------------------------------ zadania
    function zadania() {
      const z = dane.zadania || {};
      const sekcje = z.sekcje || [];
      if (!sekcje.length) return pusty("Brak zadań", "Zadania opisuje notatka B&C/Produkcja/Zadania.md.", "plan");
      const otwarte = typeof z.otwarte === "number" ? z.otwarte : sekcje.reduce((s, x) => s + (x.pozycje || []).filter((p) => !p.zrobione).length, 0);
      const zrobione = typeof z.zrobione === "number" ? z.zrobione : sekcje.reduce((s, x) => s + (x.pozycje || []).filter((p) => p.zrobione).length, 0);
      const naglowek = el("div", { class: "liczniki-kafle" },
        el("div", { class: "licznik-kafel zloto" }, el("strong", null, String(otwarte)), el("span", null, "otwarte")),
        el("div", { class: "licznik-kafel zielen" }, el("strong", null, String(zrobione)), el("span", null, "zrobione")));
      const karty = sekcje.map((s, i) => {
        const poz = s.pozycje || [];
        const otw = poz.filter((p) => !p.zrobione);
        const zrob = poz.filter((p) => p.zrobione);
        const tylkoZrobione = !otw.length && zrob.length;
        return el("article", { class: "karta sekcja-zadan", style: { "--i": i } },
          el("h2", { class: "karta-tytul" }, el("span", null, s.nazwa || "Zadania"),
            el("span", { class: "karta-akcje" }, el("span", { class: "chip" }, otw.length + " / " + poz.length))),
          otw.length ? el("ul", { class: "lista" }, otw.map(pozycjaZadania)) : null,
          zrob.length ? el("details", { class: "zwijane", open: false },
            el("summary", null, ikona("dol"), tylkoZrobione ? "Pokaż " + zrob.length + " " + odmiana(zrob.length, ["pozycję", "pozycje", "pozycji"]) : "Zrobione (" + zrob.length + ")"),
            el("ul", { class: "lista" }, zrob.map(pozycjaZadania))) : null,
          !poz.length ? el("p", { class: "cichy-tekst" }, "Pusta sekcja.") : null);
      });
      return el("div", { class: "kolumna" }, naglowek, karty);
    }

    // ------------------------------------------------------------------ decyzje
    function decyzje() {
      const lista = dane.decyzje || [];
      if (!lista.length) return pusty("Brak decyzji", "Decyzje opisuje notatka B&C/Produkcja/Rejestr decyzji.md.", "decyzja");
      const liczby = {};
      for (const d of lista) liczby[d.status] = (liczby[d.status] || 0) + 1;
      const filtry = [{ id: "wszystkie", tekst: "Wszystkie", licznik: lista.length }];
      for (const [id, s] of Object.entries(STATUSY_DECYZJI)) if (liczby[id]) filtry.push({ id, tekst: s.filtr, licznik: liczby[id] });
      if (!filtry.some((f) => f.id === filtrDecyzji)) filtrDecyzji = "wszystkie";
      const pasekFiltrow = el("div", { class: "chipy filtry", role: "group", "aria-label": "Filtr statusu" }, filtry.map((f) => {
        const s = STATUSY_DECYZJI[f.id];
        return el("button", {
          type: "button", class: "chip klik " + (s ? s.kolor : "") + (filtrDecyzji === f.id ? " wybrany" : ""), "aria-pressed": filtrDecyzji === f.id ? "true" : "false",
          onclick: () => {
            filtrDecyzji = f.id;
            rysuj();
          },
        }, f.tekst, el("span", { class: "chip-licznik" }, String(f.licznik)));
      }));
      const widoczne = lista.filter((d) => filtrDecyzji === "wszystkie" || d.status === filtrDecyzji);
      const karty = widoczne.map((d, i) => {
        const s = STATUSY_DECYZJI[d.status] || { tekst: d.status || "?", kolor: "" };
        return el("article", { class: "karta decyzja status-" + (d.status || "brak"), style: { "--i": i } },
          el("div", { class: "decyzja-gora" },
            el("span", { class: "decyzja-id" }, d.id || "D-?"),
            el("span", { class: "chip " + s.kolor }, d.emoji ? el("span", { "aria-hidden": "true" }, d.emoji) : null, s.tekst),
            d.kategoria ? el("span", { class: "chip" }, d.kategoria) : null),
          el("h2", { class: "decyzja-tytul" }, d.tytul || ""),
          (d.meta || []).length ? el("p", { class: "cichy-tekst decyzja-meta" }, (d.meta || []).join(" · ")) : null,
          d.opis_md ? html(d.opis_md) : null);
      });
      return el("div", { class: "kolumna" }, pasekFiltrow,
        karty.length ? karty : pusty("Nic w tym filtrze", "Wybierz inny status."));
    }

    // ------------------------------------------------------------------ pytania
    function pytania() {
      const lista = (dane.pytania || []).slice();
      if (!lista.length) return pusty("Brak pytań", "Pytania otwarte opisuje notatka B&C/Produkcja/Pytania otwarte.md.", "pytanie");
      lista.sort((a, b) => (b.otwarte ? 1 : 0) - (a.otwarte ? 1 : 0));
      const otwarte = lista.filter((p) => p.otwarte).length;
      return el("div", { class: "kolumna" },
        el("p", { class: "cichy-tekst" }, otwarte ? otwarte + " " + odmiana(otwarte, ["pytanie czeka", "pytania czekają", "pytań czeka"]) + " na odpowiedź." : "Wszystkie pytania mają odpowiedź."),
        lista.map((p, i) => el("article", { class: "karta pytanie" + (p.otwarte ? " otwarte" : ""), style: { "--i": i } },
          el("div", { class: "decyzja-gora" },
            el("span", { class: "decyzja-id" }, "#" + (p.nr || i + 1)),
            p.otwarte ? el("span", { class: "chip zloto" }, ikona("pytanie"), "czeka na odpowiedź") : el("span", { class: "chip zielen" }, ikona("ok"), "odpowiedziane")),
          el("h2", { class: "decyzja-tytul" }, p.tytul || ""),
          p.tresc_md ? html(p.tresc_md) : null,
          p.odpowiedz_md ? el("div", { class: "odpowiedz" }, el("span", { class: "etykieta" }, "Odpowiedź"), html(p.odpowiedz_md)) : null,
          p.otwarte && !ctx.statyczny ? el("div", { class: "rzad-przyciskow" },
            el("button", {
              type: "button", class: "przycisk maly",
              onclick: () => ctx.idz("agent", {
                kontekst: [{ typ: "notatka", cel: "B&C/Produkcja/Pytania otwarte.md", etykieta: "Pytanie #" + (p.nr || i + 1) }],
                tekst: "Pomóż mi odpowiedzieć na pytanie #" + (p.nr || i + 1) + ": " + (p.tytul || ""),
              }),
            }, ikona("agent"), el("span", null, "Omów z agentem"))) : null)));
    }

    // ------------------------------------------------------------------ dziennik
    function dziennik() {
      const wpisy = dane.dziennik || [];
      if (!wpisy.length) return pusty("Dziennik jest pusty", "Wpisy pochodzą z notatki B&C/Produkcja/Dziennik zmian.md.", "dziennik");
      return el("ol", { class: "os-czasu" }, wpisy.map((w, i) => el("li", { class: "os-wpis", style: { "--i": i } },
        el("span", { class: "os-kropka", "aria-hidden": "true" }),
        el("div", { class: "os-karta karta" },
          el("div", { class: "os-gora" },
            el("time", { class: "os-data", datetime: w.data || "" }, dataKrotka(w.data)),
            w.kto ? el("span", { class: "chip" }, ikona("uzytkownik"), w.kto) : null),
          w.temat ? el("h3", { class: "os-temat" }, w.temat) : null,
          (w.punkty_md || []).length ? el("ul", { class: "os-punkty md" }, (w.punkty_md || []).map((p) => el("li", { html: mdLinia(p) }))) : null))));
    }

    // ------------------------------------------------------------------ rysowanie i dane
    function rysuj() {
      segment.ustaw(zakladka);
      if (blad) {
        tresc.replaceChildren(stanBledu(blad, "Plan z sejfu"));
        return;
      }
      if (!dane) return;
      const czeka = (dane.pytania || []).filter((p) => p.otwarte).length;
      segment.licznik("pytania", czeka || null);
      const doDecyzji = (dane.decyzje || []).filter((d) => d.status === "do_decyzji").length;
      segment.licznik("decyzje", doDecyzji || null);
      let w;
      try {
        w = { harmonogram, zadania, decyzje, pytania, dziennik }[zakladka]();
      } catch (e) {
        console.warn("plan: rysowanie", e);
        w = pusty("Nie udało się pokazać tej części", e.message, "ostrzezenie");
      }
      tresc.replaceChildren(w);
      const z = dane.zrodla || {};
      const wpisy = Object.entries(z);
      zrodla.textContent = wpisy.length
        ? "Źródła: " + wpisy.map(([p, t]) => p.split("/").pop().replace(/\.md$/, "") + " (" + czasTemu(t) + ")").join(" · ")
        : "";
    }

    async function pobierz(wymus) {
      if (!wymus && dane && Date.now() - pobrano < 20000) return rysuj();
      if (!dane && !blad) tresc.replaceChildren(ladowanie("Czytam sejf…"));
      odswiezBtn.disabled = true;
      try {
        const d = await ctx.api("/api/sejf/plan");
        const nowe = JSON.stringify(d);
        const zmiana = !dane || JSON.stringify(dane) !== nowe || blad;
        dane = d || {};
        blad = null;
        pobrano = Date.now();
        if (zmiana || wymus) rysuj();
      } catch (e) {
        blad = e;
        dane = null;
        rysuj();
      } finally {
        odswiezBtn.disabled = false;
      }
    }

    let stop = null;
    return {
      el: korzen,
      pokaz(p) {
        if (p && p.zakladka && ZAKLADKI.some((z) => z.id === p.zakladka)) zakladka = p.zakladka;
        segment.ustaw(zakladka);
        pobierz(false);
        if (!stop) stop = ctx.odpytuj(() => pobierz(false), 60000);
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
