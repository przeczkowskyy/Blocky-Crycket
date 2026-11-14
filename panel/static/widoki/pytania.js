// Pytania: jedna zakładka na wszystko, co czeka na człowieka (dawniej Plan i Raporty, potem Decyzje).
//
// Od góry: wyszukiwarka (szuka w tytułach i treści wszystkiego: czekające i historia), lista „Do odpowiedzi”
// (wspolne/lista_pytan.js — ten sam komponent jest w zakładce Sesja), jedna wspólna historia „Odpowiedziane”
// (pytania z odpowiedziami, decyzje zamknięte, raporty po decyzji — razem, od najnowszych, w tej samej formie karty)
// i zwijana część „Plan”: Zadania (odhaczanie i dodawanie), Roadmapa, Dziennik zmian.
// Adresy: #/pytania?sprawa=<klucz> (karta na liście albo w historii), #/pytania?raport=<id> (pełny raport),
// #/pytania?sekcja=zadania|roadmapa|dziennik|historia, #/pytania?szukaj=<słowo>. Stare adresy (#/decyzje, #/plan,
// #/raporty, #/raporty/<id>) przekierowuje powłoka (app.js).

import { el, ikona, czasTemu, dataKrotka, pusty, stanBledu, ladowanie, przelacznik, odmiana, toast, arkusz, skroc } from "../wspolne/ui.js";
import { md, mdLinia } from "../wspolne/markdown.js";
import { listaPytan, zajety, podswietl } from "../wspolne/lista_pytan.js";
import { pasuje, zwykly } from "../wspolne/kolejka.js";

const ARKUSZ_STYLOW = new URL("./pytania.css", import.meta.url).href;
const CZAS_COFNIECIA_MS = 5000;
const HISTORIA_NA_START = 12;

const CZESCI_PLANU = [
  { id: "zadania", tekst: "Zadania", ikona: "plan" },
  { id: "roadmapa", tekst: "Roadmapa", ikona: "flaga" },
  { id: "dziennik", tekst: "Dziennik", ikona: "dziennik" },
];
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

function czytajLS(k, domyslne) {
  try {
    return localStorage.getItem(k) || domyslne;
  } catch (e) {
    return domyslne;
  }
}
function zapiszLS(k, v) {
  try {
    localStorage.setItem(k, v);
  } catch (e) { /* tryb prywatny */ }
}

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

export default {
  id: "pytania",
  tytul: "Pytania",
  ikona: "pytanie",
  kolejnosc: 20,
  utworz(ctx) {
    dolaczCss(ARKUSZ_STYLOW);
    let czescPlanu = czytajLS("bc.pytania.plan", "zadania");
    if (!CZESCI_PLANU.some((s) => s.id === czescPlanu)) czescPlanu = "zadania";
    let planOtwarty = czytajLS("bc.pytania.plan_otwarty", "") === "1";
    let zapytanie = "";
    let limitHistorii = HISTORIA_NA_START;
    let D = null;                                              // ostatnie dane listy (plan, raporty, agenda, sprawy)
    let wersjeZadan = "";                                      // wersja Zadań z chwili narysowania części Plan
    let planOdlozony = false;
    let historiaOdlozona = false;
    const oczekujace = new Map();       // id zadania -> {p, zegar, toast} — odhaczenie czeka 5 s na „Cofnij”
    const ostatnieKlikniecia = new Map();
    let kolejkaOdhaczen = Promise.resolve();
    const kartyHistorii = new Map();

    // ------------------------------------------------------------------ szkielet
    const lista = listaPytan(ctx, {
      naDane: (d) => {
        D = d;
        rysujReszte();
      },
      pokazSprawe: (klucz) => idzDoSprawy(klucz),
      poPisaniu: () => {
        if (historiaOdlozona) rysujHistorie();
        if (planOdlozony && !zajety(trescPlanu)) rysujPlan();
      },
    });

    const poleSzukania = el("input", {
      type: "search", class: "pole pytania-szukaj-pole", placeholder: "Szukaj w pytaniach, decyzjach i raportach…",
      "aria-label": "Szukaj w pytaniach, decyzjach i raportach", autocomplete: "off", enterkeyhint: "search",
    });
    const wynikSzukania = el("p", { class: "cichy-tekst pytania-szukaj-wynik", role: "status", "aria-live": "polite" });
    const wyczysc = el("button", { type: "button", class: "przycisk cichy ikonowy maly", "aria-label": "Wyczyść szukanie", hidden: true,
      onclick: () => { poleSzukania.value = ""; szukaj(); poleSzukania.focus(); } }, ikona("zamknij"));
    const szukajka = el("div", { class: "pytania-szukaj", role: "search" },
      el("span", { class: "pytania-szukaj-ikona", "aria-hidden": "true" }, ikona("lupa")), poleSzukania, wyczysc);

    const historiaLista = el("div", { class: "kolumna historia-lista" });
    const historiaWiecej = el("div", { class: "rzad-przyciskow historia-wiecej" });
    const historiaLicznik = el("span", { class: "chip" });
    const historia = el("section", { class: "pytania-historia", id: "pytania-historia", "aria-labelledby": "pytania-historia-tytul" },
      el("div", { class: "kolejka-nagl" }, el("h2", { id: "pytania-historia-tytul" }, "Odpowiedziane"), historiaLicznik),
      el("p", { class: "cichy-tekst" }, "Pytania z odpowiedziami, decyzje zatwierdzone i odrzucone, raporty po decyzji — od najnowszych."),
      historiaLista, historiaWiecej);

    const segment = przelacznik(CZESCI_PLANU, czescPlanu, (id) => {
      czescPlanu = id;
      zapiszLS("bc.pytania.plan", id);
      rysujPlan(true);
    }, "Część planu");
    const zmianaPlanu = el("div", { class: "sprawa-zmiana", role: "status", hidden: true }, ikona("info"),
      el("span", null, "Są nowe zmiany — pokażę je, gdy skończysz pisać."),
      el("button", { type: "button", class: "przycisk cichy maly", onclick: () => rysujPlan(true) }, "Pokaż teraz"));
    const trescPlanu = el("div", { class: "plan-tresc pytania-plan-tresc" });
    const zrodla = el("p", { class: "cichy-tekst plan-zrodla" });
    const planDet = el("details", { class: "zwijane pytania-plan", id: "pytania-plan", open: planOtwarty },
      el("summary", null, ikona("dol"), ikona("plan"), el("span", { class: "pytania-plan-tytul" }, "Plan"),
        el("span", { class: "cichy-tekst" }, "zadania, roadmapa, dziennik")),
      el("div", { class: "pytania-plan-wnetrze" }, el("div", { class: "przelacznik-przewijany" }, segment), zmianaPlanu, trescPlanu, zrodla));
    planDet.addEventListener("toggle", () => {
      planOtwarty = planDet.open;
      zapiszLS("bc.pytania.plan_otwarty", planOtwarty ? "1" : "0");
      if (planOtwarty) rysujPlan();
    });

    const odswiezBtn = el("button", { class: "przycisk cichy ikonowy", type: "button", title: "Odśwież", "aria-label": "Odśwież", onclick: () => lista.odswiez(true) }, ikona("odswiez"));
    const podtytul = el("p", { class: "cichy-tekst" }, "Wszystko, co czeka na Twoją odpowiedź — pytania, decyzje i raporty.");
    const korzen = el("div", { class: "widok pytania" },
      el("header", { class: "nagl-widoku" }, el("div", null, el("h1", null, "Pytania"), podtytul), odswiezBtn),
      szukajka, wynikSzukania, lista.el, historia, planDet);

    for (const w of [historiaLista, trescPlanu]) {
      w.addEventListener("focusout", () => setTimeout(() => {
        if (historiaOdlozona) rysujHistorie();
        if (planOdlozony && !zajety(trescPlanu)) rysujPlan();
      }, 250));
    }

    // ------------------------------------------------------------------ wyszukiwarka
    let zegarSzukania = null;
    poleSzukania.addEventListener("input", () => {
      clearTimeout(zegarSzukania);
      zegarSzukania = setTimeout(szukaj, 120);
    });
    // podpowiedź przy pustym polu: szukać można też po statusie (dawne filtry Planu i Raportów)
    const PODPOWIEDZ_SZUKANIA = "Szuka też po statusie, np. „do poprawy”, „odrzucona”, „zatwierdzona”.";
    poleSzukania.addEventListener("focus", () => {
      if (!poleSzukania.value.trim()) wynikSzukania.textContent = PODPOWIEDZ_SZUKANIA;
    });
    poleSzukania.addEventListener("blur", () => {
      if (!poleSzukania.value.trim() && wynikSzukania.textContent === PODPOWIEDZ_SZUKANIA) wynikSzukania.textContent = "";
    });
    poleSzukania.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && poleSzukania.value) {
        e.preventDefault();
        poleSzukania.value = "";
        szukaj();
      }
    });

    function szukaj() {
      zapytanie = poleSzukania.value.trim();
      wyczysc.hidden = !zapytanie;
      korzen.classList.toggle("szuka", !!zapytanie);
      const naLiscie = lista.ustawFiltr(zapytanie);
      const wHistorii = rysujHistorie();
      if (!zapytanie) {
        wynikSzukania.textContent = document.activeElement === poleSzukania ? PODPOWIEDZ_SZUKANIA : "";
        return;
      }
      wynikSzukania.textContent = !naLiscie && !wHistorii ? "Nic nie znaleziono dla „" + zapytanie + "”."
        : "Znaleziono: " + naLiscie + " do odpowiedzi, " + wHistorii + " w historii.";
    }

    // ------------------------------------------------------------------ historia „Odpowiedziane”
    /** → liczba pasujących do zapytania (wszystkie, gdy pusto). */
    function rysujHistorie() {
      if (!D || !D.pierwszeDane) {
        historiaLista.replaceChildren(ladowanie("Wczytuję historię…"));
        return 0;
      }
      const wszystkie = (D.sprawy && D.sprawy.odpowiedziane) || [];
      const pasujace = zapytanie ? wszystkie.filter((s) => pasuje(s, zapytanie)) : wszystkie;
      const widoczne = zapytanie ? pasujace : pasujace.slice(0, limitHistorii);
      historiaLicznik.textContent = String(wszystkie.length);
      const pustyEl = zapytanie ? el("p", { class: "cichy-tekst" }, "W historii nic nie pasuje.")
        : pusty("Jeszcze nic nie ma odpowiedzi", "Tu trafią pytania z odpowiedziami, rozstrzygnięte decyzje i przyjęte raporty.", "pytanie");
      historiaOdlozona = lista.uzgodnij(historiaLista, widoczne, kartyHistorii, pustyEl);
      const przyciski = [];
      if (!zapytanie && pasujace.length > widoczne.length) {
        const ile = Math.min(20, pasujace.length - widoczne.length);
        przyciski.push(el("button", { type: "button", class: "przycisk", onclick: () => { limitHistorii += 20; rysujHistorie(); } },
          ikona("dol"), el("span", null, "Pokaż więcej (" + ile + " z " + (pasujace.length - widoczne.length) + ")")));
      }
      if (!zapytanie && limitHistorii > HISTORIA_NA_START && widoczne.length > HISTORIA_NA_START) {
        przyciski.push(el("button", { type: "button", class: "przycisk cichy", onclick: () => {
          limitHistorii = HISTORIA_NA_START;
          rysujHistorie();
          historia.scrollIntoView({ block: "start" });
        } }, el("span", null, "Pokaż mniej")));
      }
      historiaWiecej.replaceChildren(...przyciski);
      return pasujace.length;
    }

    // ------------------------------------------------------------------ plan: zadania
    function pozycjaZadania(p, o = {}) {
      const czeka = oczekujace.has(p.id);
      const zrobione = p.zrobione || czeka;
      let pole;
      if (o.odhaczalne && !p.zrobione) {
        pole = el("button", {
          type: "button", class: "pole-wyboru-przycisk", role: "checkbox", "aria-checked": czeka ? "true" : "false",
          "aria-label": (czeka ? "Cofnij odhaczenie: " : "Odhacz: ") + zwykly(p.tekst_md),
          title: czeka ? "Cofnij" : "Odhacz w sejfie",
          onclick: () => {
            const teraz = Date.now();                          // podwójny klik ≠ „odhacz i od razu cofnij”
            if (teraz - (ostatnieKlikniecia.get(p.id) || 0) < 400) return;
            ostatnieKlikniecia.set(p.id, teraz);
            if (czeka) cofnij(p.id);
            else odhaczZOpoznieniem(p);
          },
        }, el("span", { class: "pole-wyboru" + (czeka ? " zaznaczone oczekuje" : "") }, czeka ? ikona("ok") : null));
      } else {
        pole = el("span", { class: "pole-wyboru" + (zrobione ? " zaznaczone" : ""), "aria-label": zrobione ? "zrobione" : "do zrobienia", role: "img" },
          zrobione ? ikona("ok") : null);
      }
      return el("li", { class: "wiersz zadanie-wiersz" + (zrobione ? " zrobione" : "") + (czeka ? " oczekuje" : "") },
        pole,
        linia(p.tekst_md, "wiersz-tekst"),
        p.data ? el("span", { class: "cichy-tekst data-zadania" }, dataKrotka(p.data)) : null,
        p.priorytet ? el("span", { class: "chip " + (PRIORYTETY[p.priorytet] || "") }, p.priorytet) : null);
    }

    function odhaczZOpoznieniem(p) {
      if (!p.id || oczekujace.has(p.id)) return;
      const wpis = { p, zegar: null, toast: null };
      oczekujace.set(p.id, wpis);
      wpis.toast = toast("Odhaczono: " + skroc(zwykly(p.tekst_md), 70), "ok",
        { czas: CZAS_COFNIECIA_MS, akcja: { tekst: "Cofnij", fn: () => cofnij(p.id) } });
      wpis.zegar = setTimeout(() => wyslijOdhaczenie(p.id), CZAS_COFNIECIA_MS);
      rysujPlan();
    }

    function cofnij(id) {
      const w = oczekujace.get(id);
      if (!w) return;
      if (w.wTrakcie) {
        toast("To odhaczenie już idzie do sejfu — cofnąć je można w Obsidianie.", "info");
        return;
      }
      clearTimeout(w.zegar);
      oczekujace.delete(id);
      if (w.toast && w.toast.zamknij) w.toast.zamknij();
      toast("Cofnięto — zadanie zostaje otwarte.");
      rysujPlan();
    }

    function wyslijOdhaczenie(id, wTle) {
      const w = oczekujace.get(id);
      if (!w) return kolejkaOdhaczen;
      clearTimeout(w.zegar);
      if (w.wyslane) return kolejkaOdhaczen;                   // już w kolejce (np. ukrycie karty i pagehide)
      w.wyslane = true;
      kolejkaOdhaczen = kolejkaOdhaczen.then(async () => {
        if (!oczekujace.has(id)) return;
        w.wTrakcie = true;
        const wynik = await odhaczWSejfie(id, w.p, wTle);
        oczekujace.delete(id);
        rysujPlan();
        if (wynik) toast("Zapisano w Zadaniach: " + skroc(zwykly(w.p.tekst_md), 60), "ok");
      });
      return kolejkaOdhaczen;
    }

    /**
     * Odhaczenie po id (skrót treści zadania) — bezpieczne do powtórzenia: gdy ktoś w tym czasie zmienił inną część
     * Zadań (409 „konflikt wersji”), ponawia raz z aktualną wersją. Zadanie o zmienionej treści ma inne id, więc
     * ponowienie go nie odhaczy (404). `wTle` = karta znika (keepalive).
     */
    async function odhaczWSejfie(id, p, wTle) {
      let wersja = wersjeZadan || "";
      for (let proba = 0; proba < 2; proba++) {
        try {
          const w = await ctx.api("/api/sejf/zadania/odhacz", { metoda: "POST", cialo: { id, wersja }, keepalive: !!wTle });
          if (w && w.plan) {
            if (w.plan.wersje) wersjeZadan = w.plan.wersje.zadania || "";
            lista.ustawPlan(w.plan);
          }
          if (w && w.uwaga) toast(w.uwaga, "info", { czas: 6500 });
          return w;
        } catch (e) {
          if (proba === 0 && e.status === 409 && e.dane && e.dane.kod === "konflikt_wersji" && e.dane.wersja) {
            wersja = e.dane.wersja;                            // ktoś zmienił plik: ta sama operacja na nowej wersji
            continue;
          }
          toast("Nie odhaczono: " + skroc(zwykly(p.tekst_md), 60) + " — " + (e.message || "błąd"), "blad", { czas: 8000 });
          await lista.odswiez(true);
          return null;
        }
      }
      return null;
    }

    function wyslijWszystkieOczekujace(wTle) {
      for (const id of [...oczekujace.keys()]) wyslijOdhaczenie(id, wTle);
    }

    function oknoDodawania() {
      let sekcjaZadania = "teraz";
      let priorytet = "średni";
      const pole = el("textarea", { class: "pole", rows: 2, maxlength: "300", placeholder: "np. Test HUD na telefonie", "aria-label": "Treść zadania" });
      const segSekcja = przelacznik([{ id: "teraz", tekst: "Teraz" }, { id: "backlog", tekst: "Backlog" }], sekcjaZadania, (id) => { sekcjaZadania = id; }, "Sekcja");
      const segPriorytet = przelacznik([{ id: "wysoki", tekst: "wysoki" }, { id: "średni", tekst: "średni" }, { id: "niski", tekst: "niski" }],
        priorytet, (id) => { priorytet = id; }, "Priorytet");
      segSekcja.classList.add("maly");
      segPriorytet.classList.add("maly");
      const zapisz = el("button", { class: "przycisk glowny szeroki", type: "submit" }, ikona("plus"), el("span", null, "Dodaj do Zadań"));
      const form = el("form", { class: "formularz" },
        el("label", { class: "etykieta" }, "Zadanie"), pole,
        el("span", { class: "etykieta" }, "Sekcja"), segSekcja,
        el("span", { class: "etykieta" }, "Priorytet"), segPriorytet,
        el("p", { class: "cichy-tekst" }, "Trafi na koniec wybranej sekcji w B&C/Produkcja/Zadania.md jako „- [ ] … · #priorytet”, z wpisem w Dzienniku zmian."),
        zapisz);
      const ark = arkusz({ tytul: "Nowe zadanie", tresc: form });
      pole.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          form.requestSubmit ? form.requestSubmit() : zapisz.click();
        }
      });
      let wToku = false;                                       // Enter wciśnięty dwa razy = jedno żądanie
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (wToku) return;
        const tekst = pole.value.trim();
        if (!tekst) {
          pole.focus();
          return;
        }
        wToku = true;
        zapisz.disabled = true;
        try {
          const w = await lista.zapiszDoSejfu("/api/sejf/zadania/dodaj", { tekst, sekcja: sekcjaZadania, priorytet }, wersjeZadan);
          if (w) {
            ark.zamknij();
            toast("Dodano zadanie (" + (sekcjaZadania === "teraz" ? "Teraz" : "Backlog") + ").", "ok");
          } else {
            zapisz.disabled = false;
          }
        } finally {
          wToku = false;
        }
      });
    }

    function czescZadan(plan) {
      const z = plan.zadania || {};
      const sekcje = z.sekcje || [];
      const moze = D && D.mozeZapisywac;
      const akcje = moze ? el("div", { class: "plan-akcje" },
        el("p", { class: "cichy-tekst" }, "Pole wyboru odhacza zadanie w sejfie (5 s na cofnięcie)."),
        el("button", { type: "button", class: "przycisk glowny", onclick: oknoDodawania }, ikona("plus"), el("span", null, "Dodaj zadanie"))) : null;
      if (!sekcje.length) return el("div", { class: "kolumna" }, akcje, pusty("Brak zadań", "Zadania opisuje notatka B&C/Produkcja/Zadania.md.", "plan"));
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
        const wiersz = (p) => pozycjaZadania(p, { odhaczalne: moze });
        return el("article", { class: "karta sekcja-zadan", style: { "--i": i } },
          el("h3", { class: "karta-tytul" }, el("span", null, s.nazwa || "Zadania"),
            el("span", { class: "karta-akcje" }, el("span", { class: "chip" }, otw.length + " / " + poz.length))),
          otw.length ? el("ul", { class: "lista" }, otw.map(wiersz)) : null,
          zrob.length ? el("details", { class: "zwijane", open: false },
            el("summary", null, ikona("dol"), tylkoZrobione ? "Pokaż " + zrob.length + " " + odmiana(zrob.length, ["pozycję", "pozycje", "pozycji"]) : "Zrobione (" + zrob.length + ")"),
            el("ul", { class: "lista" }, zrob.map(wiersz))) : null,
          !poz.length ? el("p", { class: "cichy-tekst" }, "Pusta sekcja.") : null);
      });
      return el("div", { class: "kolumna" }, naglowek, akcje, karty);
    }

    function czescRoadmapy(plan) {
      const r = plan.roadmapa || {};
      const fazy = r.fazy || [];
      const propozycje = r.propozycje || [];
      if (!fazy.length && !propozycje.length) return pusty("Roadmapa jest pusta", "Fazy opisuje notatka B&C/Produkcja/Roadmapa.md.", "flaga");
      const karty = fazy.map((f, i) => {
        const p = postep(f);
        const poz = f.pozycje || [];
        const zrob = poz.filter((x) => x.zrobione).length;
        return el("article", { class: "karta faza" + (f.aktywna ? " aktywna" : ""), style: { "--i": i } },
          el("div", { class: "faza-gora" },
            el("h3", { class: "faza-nazwa" }, String(f.nazwa || "").replace(/^[▶►\s]+/, "")),
            f.aktywna ? el("span", { class: "chip zloto" }, ikona("flaga"), "aktywna") : p >= 1 ? el("span", { class: "chip zielen" }, ikona("ok"), "gotowa") : null),
          f.status_tekst ? el("p", { class: "cichy-tekst" }, f.status_tekst) : null,
          f.opis ? html(f.opis) : null,
          el("div", { class: "faza-postep" },
            el("div", { class: "pasek" }, el("div", { class: "pasek-wypelnienie", style: { width: Math.round(p * 100) + "%" } })),
            el("span", { class: "faza-procent" }, Math.round(p * 100) + "%"),
            poz.length ? el("span", { class: "cichy-tekst" }, zrob + "/" + poz.length) : null),
          poz.length ? el("ul", { class: "lista" }, poz.map((x) => pozycjaZadania(x))) : null);
      });
      const kartyProp = propozycje.map((p, i) => el("article", { class: "karta faza propozycja", style: { "--i": fazy.length + i } },
        el("div", { class: "faza-gora" },
          el("h3", { class: "faza-nazwa" }, (p.nr ? "Faza " + p.nr + " — " : "") + (p.nazwa || "")),
          el("span", { class: "chip fiolet" }, "propozycja")),
        p.opis_md ? html(p.opis_md) : null));
      return el("div", { class: "kolumna" }, karty,
        kartyProp.length ? el("h3", { class: "sekcja-naglowek" }, "Kolejne fazy (do zatwierdzenia)") : null, kartyProp);
    }

    function czescDziennika(plan) {
      const wpisy = plan.dziennik || [];
      if (!wpisy.length) return pusty("Dziennik jest pusty", "Wpisy pochodzą z notatki B&C/Produkcja/Dziennik zmian.md.", "dziennik");
      return el("ol", { class: "os-czasu" }, wpisy.map((w, i) => el("li", { class: "os-wpis", style: { "--i": Math.min(i, 10) } },
        el("span", { class: "os-kropka", "aria-hidden": "true" }),
        el("div", { class: "os-karta karta" },
          el("div", { class: "os-gora" },
            el("time", { class: "os-data", datetime: w.data || "" }, dataKrotka(w.data)),
            w.kto ? el("span", { class: "chip" }, ikona("uzytkownik"), w.kto) : null),
          w.temat ? el("h3", { class: "os-temat" }, w.temat) : null,
          (w.punkty_md || []).length ? el("ul", { class: "os-punkty md" }, (w.punkty_md || []).map((p) => el("li", { html: mdLinia(p) }))) : null))));
    }

    function rysujPlan(wymus) {
      segment.ustaw(czescPlanu);
      const plan = D && D.plan;
      if (plan) {
        const z = plan.zadania || {};
        segment.licznik("zadania", typeof z.otwarte === "number" ? z.otwarte || null : null);
      }
      if (!planDet.open) return;                               // zwinięty: narysuje się przy rozwinięciu
      if (!D || !D.pierwszeDane) {
        trescPlanu.replaceChildren(ladowanie("Czytam sejf…"));
        return;
      }
      if (!wymus && zajety(trescPlanu)) {                      // nie wyrywaj nikomu pola spod palców
        planOdlozony = true;
        zmianaPlanu.hidden = false;
        return;
      }
      planOdlozony = false;
      zmianaPlanu.hidden = true;
      let w;
      if (!plan) {
        w = D.bladPlanu ? stanBledu(D.bladPlanu, "Plan z sejfu") : ladowanie("Czytam sejf…");
      } else {
        wersjeZadan = (plan.wersje && plan.wersje.zadania) || "";
        try {
          w = { zadania: czescZadan, roadmapa: czescRoadmapy, dziennik: czescDziennika }[czescPlanu](plan);
        } catch (e) {
          console.warn("pytania: plan", e);
          w = pusty("Nie udało się pokazać tej części", e.message, "ostrzezenie");
        }
      }
      const przewiniecie = window.scrollY;
      trescPlanu.replaceChildren(w);
      if (Math.abs(window.scrollY - przewiniecie) > 2) window.scrollTo(0, przewiniecie);   // zapis nie skacze na górę
      const z = (plan && plan.zrodla) || {};
      const wpisy = Object.entries(z);
      zrodla.textContent = wpisy.length
        ? "Źródła: " + wpisy.map(([p, t]) => p.split("/").pop().replace(/\.md$/, "") + " (" + czasTemu(t) + ")").join(" · ")
        : "";
    }

    function rysujReszte() {
      podtytul.textContent = D && D.mozeZapisywac
        ? "Wszystko, co czeka na Twoją odpowiedź — pytania, decyzje i raporty. Odpowiedzi zapisują się w sejfie."
        : "Wszystko, co czeka na odpowiedź — pytania, decyzje i raporty.";
      if (zapytanie) szukaj();
      else rysujHistorie();
      rysujPlan();
    }

    // ------------------------------------------------------------------ nawigacja w widoku
    function otworzPlan(czesc) {
      if (czesc && CZESCI_PLANU.some((s) => s.id === czesc)) {
        czescPlanu = czesc;
        zapiszLS("bc.pytania.plan", czesc);
      }
      if (!planDet.open) planDet.open = true;                  // „toggle” narysuje część
      rysujPlan(true);
      requestAnimationFrame(() => planDet.scrollIntoView({ block: "start", behavior: "smooth" }));
    }

    /** Karta sprawy: na liście „Do odpowiedzi”, a jeśli jej tam nie ma — w historii. */
    function idzDoSprawy(klucz) {
      if (lista.idzDo(klucz)) return true;
      const wszystkie = (D && D.sprawy && D.sprawy.odpowiedziane) || [];
      const i = wszystkie.findIndex((s) => s.klucz === klucz);
      if (i < 0) {
        toast(/^raport-/.test(klucz) ? "Nie ma takiego raportu (może został usunięty)." : "Nie ma tej sprawy ani na liście, ani w historii.", "info");
        return false;
      }
      if (zapytanie) {                                         // szukanie mogło ją ukryć
        poleSzukania.value = "";
        szukaj();
      }
      if (i >= limitHistorii) {
        limitHistorii = i + 1;
        rysujHistorie();
      }
      const k = historiaLista.querySelector("#" + CSS.escape("sprawa-" + klucz));
      if (k) podswietl(k);
      return !!k;
    }

    // Telefon: zablokowanie ekranu albo przejście do innej aplikacji wstrzymuje zegar 5 s, a karta bywa potem
    // wyrzucona z pamięci — oczekujące odhaczenia idą od razu, z keepalive (żądanie przeżyje zamknięcie karty).
    window.addEventListener("pagehide", () => wyslijWszystkieOczekujace(true));
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") wyslijWszystkieOczekujace(true);
    });
    window.addEventListener("bc:kto", () => {
      for (const w of kartyHistorii.values()) w.podpis = "";   // nowy podpis odpowiedzi w „Dopisz odpowiedź”
    });

    return {
      el: korzen,
      pokaz(p) {
        p = p || {};
        if (typeof p.szukaj === "string" && p.szukaj !== poleSzukania.value) {
          poleSzukania.value = p.szukaj;
        }
        const gotowe = lista.pokaz();
        gotowe.then(() => {
          if (poleSzukania.value.trim() !== zapytanie) szukaj();
          if (p.sekcja && CZESCI_PLANU.some((s) => s.id === p.sekcja)) otworzPlan(p.sekcja);
          else if (p.sekcja === "historia") requestAnimationFrame(() => historia.scrollIntoView({ block: "start", behavior: "smooth" }));
          const cel = p.sprawa || (p.raport ? "raport-" + p.raport : null);
          if (cel) idzDoSprawy(String(cel));
          if (p.raport) {
            const r = ((D && D.raporty) || []).find((x) => x.id === p.raport);
            if (r) lista.pelnyRaport(r);
          }
        });
      },
      ukryj() {
        wyslijWszystkieOczekujace();                           // odhaczenie nie ginie przy przejściu do innego widoku
        lista.ukryj();
      },
    };
  },
};
