// Pulpit: najważniejsze na jednym ekranie, od góry: Czeka na Ciebie (liczba i trzy pierwsze sprawy), Rozmowa
// (zakładka Sesja: kto jest, czy agent słucha), Co nowego (raporty, decyzje, wpisy ludzi), Synchronizacja (Pobierz /
// Wyślij z podglądem zmian sejfu), a niżej reszta: Teraz (zadania), Kto pracuje, Napisz do agenta, Ostatnia migawka.

import { el, dopisz, zamien, ikona, czasTemu, dataKrotka, toast, arkusz, awatar, karta, pusty, stanBledu, ladowanie, odmiana, skroc } from "../wspolne/ui.js";
import { mdLinia } from "../wspolne/markdown.js";
import { zbudujKolejke } from "../wspolne/kolejka.js";

const enc = encodeURIComponent;

export function postepFazy(f) {
  if (!f) return 0;
  let p = Number(f.postep);
  if (!isFinite(p) || f.postep === null || f.postep === undefined) {
    const poz = f.pozycje || [];
    p = poz.length ? poz.filter((x) => x.zrobione).length / poz.length : 0;
  } else if (p > 1) p = p / 100;
  return Math.max(0, Math.min(1, p));
}

const PRIORYTETY = { wysoki: "czerwien", "średni": "zloto", sredni: "zloto", niski: "niebieski" };
const STANY_ROZMOWY = { mowi: "mówi", wyciszony: "wyciszony", bez_mikrofonu: "bez mikrofonu", polaczony: "połączony", laczenie: "łączy się" };
const STATUSY_DECYZJI = { zatwierdzona: "zatwierdzona", odrzucona: "odrzucona", do_decyzji: "do decyzji", propozycja: "propozycja", zastapiona: "zastąpiona" };

export function chipPriorytetu(p) {
  if (!p) return null;
  return el("span", { class: "chip " + (PRIORYTETY[p] || ""), title: "Priorytet" }, p);
}

function nazwaFazy(f) {
  return String(f.nazwa || "").replace(/^[▶►\s]+/, "");
}

function zwykly(t) {
  return String(t || "").replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2").replace(/\[\[([^\]]+)\]\]/g, "$1")
    .replace(/[`*_]/g, "").trim();
}

/** „dziś” / „13 lis” dla samej daty, „5 min temu” dla czasu. */
function kiedy(t) {
  if (!t) return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(t)) {
    const d = new Date();
    const dzis = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    return t === dzis ? "dziś" : dataKrotka(t);
  }
  return czasTemu(t);
}

export default {
  id: "pulpit",
  tytul: "Pulpit",
  ikona: "pulpit",
  kolejnosc: 10,
  utworz(ctx) {
    // Przejścia do zakładki Pytania: karta („pytanie-19”, „D-009”, „raport-<id>”) albo część (zadania, roadmapa, dziennik).
    const doSprawy = (klucz) => ctx.idz("pytania", { sprawa: klucz });
    const doSekcji = (sekcja) => ctx.idz("pytania", { sekcja });

    // --- nagłówek: powitanie i faza (krótko)
    const powitanie = el("h1", { class: "pulpit-powitanie" });
    const faza = el("div", { class: "pulpit-faza" });
    const gora = el("header", { class: "pulpit-gora" },
      el("div", { class: "pulpit-gora-tekst" }, powitanie),
      faza);

    const kCzeka = karta("Czeka na Ciebie", "pytanie", { klasa: "karta-czeka" });
    const kRozmowa = karta("Rozmowa", "mikrofon", { klasa: "karta-rozmowa" });
    const kNowe = karta("Co nowego", "zegar", { klasa: "karta-nowe" });
    const kSync = karta("Synchronizacja", "git", { klasa: "karta-sync" });
    const kTeraz = karta("Teraz", "ogien", { klasa: "karta-teraz" });
    const kKto = karta("Kto pracuje", "zespol", { klasa: "karta-kto" });
    const kAgent = karta("Napisz do agenta", "agent", { klasa: "karta-agent" });
    const kMigawka = karta("Ostatnia migawka", "migawka", { klasa: "karta-migawka" });

    for (const k of [kCzeka, kRozmowa, kNowe, kSync, kTeraz, kKto, kMigawka]) k.cialo.appendChild(ladowanie());

    // --- szybkie pole do agenta
    if (!ctx.statyczny) {
      const pole = el("textarea", { class: "pole", rows: 2, placeholder: "Np. „Podsumuj, co zostało w Fazie 1”", "aria-label": "Wiadomość do agenta" });
      const wyslij = () => {
        const t = pole.value.trim();
        if (!t) {
          pole.focus();
          return;
        }
        pole.value = "";
        ctx.idz("agent", { tekst: t });
      };
      pole.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
          e.preventDefault();
          wyslij();
        }
      });
      kAgent.cialo.append(pole, el("div", { class: "rzad-przyciskow" },
        el("span", { class: "cichy-tekst" }, "Enter — przejdź do rozmowy"),
        el("button", { class: "przycisk glowny", type: "button", onclick: wyslij }, ikona("strzalka"), el("span", null, "Do agenta"))));
    }

    // Najważniejsze na górze (telefon: jedna kolumna w tej kolejności); niżej reszta w siatce.
    const glowne = el("div", { class: "pulpit-glowne" }, kCzeka.el, kRozmowa.el, kNowe.el, kSync.el);
    const reszta = el("div", { class: "pulpit-reszta" }, kTeraz.el, kKto.el, ctx.statyczny ? null : kAgent.el, kMigawka.el);
    const korzen = el("div", { class: "widok pulpit" }, gora, glowne,
      el("h2", { class: "pulpit-naglowek" }, "Reszta"), reszta);

    let stop = null;
    let ostatnieDane = {};

    // ------------------------------------------------------------------ rysowanie kart
    function rysujGore(plan, blad) {
      const kto = ctx.ja.kto && ctx.ja.kto !== "gość" ? ctx.ja.kto : "";
      powitanie.textContent = kto ? "Cześć, " + kto + "!" : "Panel zespołu";
      faza.replaceChildren();
      if (blad || !plan) return;
      const fazy = (plan.roadmapa && plan.roadmapa.fazy) || [];
      const f = fazy.find((x) => x.aktywna) || fazy.find((x) => postepFazy(x) < 1) || fazy[0];
      if (!f) return;
      const p = Math.round(postepFazy(f) * 100);
      faza.append(el("button", { type: "button", class: "pulpit-faza-przycisk", onclick: () => doSekcji("roadmapa"), "aria-label": "Faza: " + nazwaFazy(f) + ", " + p + "% — pokaż roadmapę" },
        el("span", { class: "pulpit-faza-nazwa" }, ikona("flaga"), el("span", null, nazwaFazy(f))),
        el("span", { class: "pasek", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(p) },
          el("span", { class: "pasek-wypelnienie", style: { width: p + "%", display: "block" } })),
        el("strong", { class: "pulpit-faza-procent" }, p + "%")));
    }

    /** Wiersz „Czeka na Ciebie”: każda sprawa jako pytanie (tytuł karty z zakładki Pytania), z małą etykietą pochodzenia. */
    function opisSprawy(s) {
      if (s.typ === "raport") return { nad: s.pochodzenie || "z raportu", pod: (s.r.kto || "ktoś") + " · " + czasTemu(s.r.czas) };
      if (s.typ === "pytanie") {
        const otw = (s.decyzje || []).filter((x) => x.d && (x.d.status === "propozycja" || x.d.status === "do_decyzji")).length;
        return { nad: s.pochodzenie || "pytanie #" + s.p.nr, pod: otw ? "z " + otw + " " + odmiana(otw, ["decyzją", "decyzjami", "decyzjami"]) + " do zatwierdzenia" : "czeka na odpowiedź" };
      }
      if (s.typ === "potwierdzenie") return { nad: s.pochodzenie || "decyzja " + s.d.id, pod: "Zgoda, brak zgody czy rozmowa?" };
      return { nad: s.pochodzenie || "decyzja " + s.d.id, pod: "Tak czy nie? · " + (STATUSY_DECYZJI[s.d.status] || s.d.status) };
    }

    function rysujCzeka(dane) {
      const c = kCzeka.cialo;
      const { plan, raporty, agenda, bladPlanu, bladRaportow } = dane;
      if (!plan && !raporty) return c.replaceChildren(stanBledu(bladPlanu || bladRaportow || {}, "Sprawy"));
      const k = zbudujKolejke(plan || {}, raporty || [], agenda, ctx.ja);   // z potwierdzeniami decyzji (D-043)
      const n = k.aktywne.length;
      ctx.licznik("pytania", n);
      kCzeka.akcje.replaceChildren();
      if (!n) {
        return c.replaceChildren(el("div", { class: "czeka-zero" },
          el("span", { class: "czeka-liczba zero" }, ikona("ok")),
          el("div", null, el("strong", null, "Nic nie czeka"),
            el("p", { class: "cichy-tekst" }, k.odlozone.length ? k.odlozone.length + " " + odmiana(k.odlozone.length, ["pytanie czeka", "pytania czekają", "pytań czeka"]) + " na sesję główną." : "Na wszystkie pytania jest odpowiedź."))));
      }
      zamien(c,
        el("button", { type: "button", class: "czeka-gora", onclick: () => ctx.idz("pytania") },
          el("span", { class: "czeka-liczba" }, String(n)),
          el("span", { class: "czeka-opis" }, el("strong", null, odmiana(n, ["pytanie czeka", "pytania czekają", "pytań czeka"])),
            el("span", { class: "cichy-tekst" }, "na Twoją odpowiedź — zakładka Pytania"))),
        // lekkie wiersze jak karty w zakładce Pytania: mała szara etykieta, tytuł, krótki dopisek — bez kolorowych znaczków
        el("ul", { class: "lista czeka-lista" }, k.aktywne.slice(0, 3).map((s) => {
          const o = opisSprawy(s);
          return el("li", null, el("button", { type: "button", class: "wiersz wiersz-klik sprawa-wiersz", onclick: () => doSprawy(s.klucz) },
            el("span", { class: "wiersz-tekst" },
              el("span", { class: "sprawa-nad" }, o.nad),
              el("strong", null, skroc(zwykly(s.pytanie || s.tytul), 90) || "(bez tytułu)"),
              el("span", { class: "cichy-tekst" }, o.pod)),
            ikona("prawo", { klasa: "wiersz-strzalka" })));
        })),
        n > 3 ? el("button", { type: "button", class: "przycisk szeroki", onclick: () => ctx.idz("pytania") },
          el("span", null, "Wszystkie (" + n + ")"), ikona("strzalka")) : null);
    }

    function rysujRozmowe(ob, blad) {
      const c = kRozmowa.cialo;
      kRozmowa.akcje.replaceChildren();
      if (blad) return c.replaceChildren(stanBledu(blad, "Obecność"));
      const r = (ob && ob.rozmowa && typeof ob.rozmowa === "object") ? ob.rozmowa : null;
      const osoby = (r && r.osoby) || [];
      const przycisk = el("button", { type: "button", class: "przycisk" + (osoby.length ? " glowny" : ""), onclick: () => ctx.idz("sesja") },
        ikona("mikrofon"), el("span", null, osoby.length ? "Dołącz w Sesji" : "Otwórz Sesję"));
      if (ctx.statyczny) return c.replaceChildren(el("p", { class: "cichy-tekst" }, "Rozmowa działa tylko na żywym panelu."));
      if (!osoby.length) {
        return c.replaceChildren(el("p", { class: "cichy-tekst" }, r ? "Nikt teraz nie rozmawia." : "Stan rozmowy pokaże się po restarcie panelu."),
          el("div", { class: "rzad-przyciskow" }, przycisk));
      }
      if (r.slucha) kRozmowa.akcje.append(el("span", { class: "chip czerwien" }, el("span", { class: "kropka-nagrywania", "aria-hidden": "true" }), "agent słucha"));
      c.replaceChildren(
        el("ul", { class: "lista osoby" }, osoby.map((o) => el("li", { class: "wiersz" },
          awatar(o.kto, { maly: true }),
          el("span", { class: "wiersz-tekst" }, el("strong", null, o.kto || "ktoś"),
            el("span", { class: "cichy-tekst" }, (STANY_ROZMOWY[o.stan] || "w rozmowie") + (o.od ? " · od " + czasTemu(o.od).replace(/ temu$/, "") : "")))))),
        el("div", { class: "rzad-przyciskow" }, przycisk));
    }

    function rysujNowe(dane) {
      const c = kNowe.cialo;
      const { plan, raporty } = dane;
      if (!plan && !raporty) return c.replaceChildren(el("p", { class: "cichy-tekst" }, "Brak danych."));
      const wpisy = [];
      for (const r of (raporty || []).slice().sort((a, b) => String(b.czas || "").localeCompare(String(a.czas || ""))).slice(0, 3)) {
        wpisy.push({ ikona: "raporty", tekst: r.tytul || "(bez tytułu)", pod: "Raport · " + (r.kto || "ktoś"), czas: r.czas || "", akcja: () => doSprawy("raport-" + r.id) });
      }
      const decyzje = [];
      for (const d of (plan && plan.decyzje) || []) {
        if (d.status !== "zatwierdzona" && d.status !== "odrzucona") continue;
        for (const m of d.meta || []) {
          const mm = /^(?:zdecydował|zdecydowała)\S*:\s*(.+?)\s+(\d{4}-\d{2}-\d{2})$/.exec(String(m).trim());
          if (mm) decyzje.push({ ikona: "decyzja", tekst: d.id + " " + (d.tytul || ""), pod: "Decyzja " + STATUSY_DECYZJI[d.status] + " · " + mm[1], czas: mm[2], akcja: () => doSprawy(d.id) });
        }
      }
      decyzje.sort((a, b) => b.czas.localeCompare(a.czas));
      wpisy.push(...decyzje.slice(0, 3));
      const ludzie = [];
      for (const w of (plan && plan.dziennik) || []) {
        if (!/panel/i.test(w.kto || "") || !/ludzie/i.test(w.temat || "")) continue;
        for (const p of (w.punkty_md || []).slice().reverse()) {
          ludzie.push({ ikona: "uzytkownik", tekst: zwykly(p).replace(/\s*\((?:Pytania otwarte|Rejestr decyzji|Zadania|Sesje główne)\)\s*$/, ""), pod: "Wpis w Dzienniku", czas: w.data, akcja: () => doSekcji("dziennik") });
        }
      }
      wpisy.push(...ludzie.slice(0, 3));
      wpisy.sort((a, b) => String(b.czas).slice(0, 10).localeCompare(String(a.czas).slice(0, 10)));
      if (!wpisy.length) return c.replaceChildren(el("p", { class: "cichy-tekst" }, "Na razie nic nowego."));
      c.replaceChildren(el("ul", { class: "lista" }, wpisy.slice(0, 6).map((w) => el("li", null,
        el("button", { type: "button", class: "wiersz wiersz-klik nowe-wiersz", onclick: w.akcja },
          el("span", { class: "sprawa-znak" }, ikona(w.ikona)),
          el("span", { class: "wiersz-tekst" }, el("strong", null, skroc(w.tekst, 90)), el("span", { class: "cichy-tekst" }, w.pod)),
          el("span", { class: "cichy-tekst nowe-kiedy" }, kiedy(w.czas)))))));
    }

    function rysujTeraz(plan, blad) {
      const c = kTeraz.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Zadania"));
      const sekcje = (plan.zadania && plan.zadania.sekcje) || [];
      const pierwsza = sekcje.find((s) => (s.pozycje || []).some((p) => !p.zrobione)) || sekcje[0];
      if (!pierwsza) return c.replaceChildren(pusty("Brak zadań", "Lista zadań w sejfie jest pusta."));
      const otwarte = (pierwsza.pozycje || []).filter((p) => !p.zrobione);
      kTeraz.akcje.replaceChildren(el("button", { type: "button", class: "przycisk cichy maly", onclick: () => doSekcji("zadania") }, "Wszystkie"));
      if (!otwarte.length) return c.replaceChildren(pusty("Wszystko zrobione", "W sekcji „" + pierwsza.nazwa + "” nie ma otwartych zadań.", "ok"));
      zamien(c,
        el("p", { class: "cichy-tekst sekcja-nazwa" }, pierwsza.nazwa),
        el("ul", { class: "lista zadania-lista" }, otwarte.slice(0, 5).map((p) => el("li", { class: "wiersz zadanie-wiersz" },
          el("span", { class: "pole-wyboru", "aria-hidden": "true" }),
          el("span", { class: "md md-linia wiersz-tekst", html: mdLinia(p.tekst_md) }),
          chipPriorytetu(p.priorytet)))),
        otwarte.length > 5 ? el("p", { class: "cichy-tekst" }, "…i jeszcze " + (otwarte.length - 5) + " w tej sekcji.") : null);
    }

    function rysujKto(ob, blad) {
      const c = kKto.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Obecność"));
      const panel = ob.panel || [];
      const studio = ob.studio || {};
      const git = ob.git || [];
      const czesci = [];
      czesci.push(el("p", { class: "etykieta" }, "Na panelu"));
      if (panel.length) {
        czesci.push(el("ul", { class: "lista osoby" }, panel.map((o) => el("li", { class: "wiersz" },
          el("span", { class: "awatar-z-kropka" }, awatar(o.kto, { maly: true }), el("span", { class: "kropka-online" })),
          el("span", { class: "wiersz-tekst" }, el("strong", null, o.kto || "ktoś"),
            el("span", { class: "cichy-tekst" }, ctx.nazwaWidoku(o.widok || "pulpit") + (o.lokalny ? "" : " · zdalnie")))))));
      } else czesci.push(el("p", { class: "cichy-tekst" }, "Nikogo poza Tobą."));

      czesci.push(el("p", { class: "etykieta" }, "W Roblox Studio"));
      const osobyStudio = studio.osoby || [];
      if (!studio.dostepne) czesci.push(el("p", { class: "cichy-tekst" }, "Studio niepodłączone do panelu."));
      else if (!osobyStudio.length) czesci.push(el("p", { class: "cichy-tekst" }, "Nikt nie ma teraz otwartego miejsca."));
      else czesci.push(el("div", { class: "chipy" }, osobyStudio.map((o) => el("span", { class: "chip zielen" }, ikona("studio"), o.nazwa))));

      if (git.length) {
        czesci.push(el("p", { class: "etykieta" }, "Ostatnie zmiany w repozytorium"));
        czesci.push(el("ul", { class: "lista commity" }, git.slice(0, 3).map((g) => el("li", { class: "wiersz" },
          awatar(g.autor, { maly: true }),
          el("span", { class: "wiersz-tekst" }, el("span", { class: "commit-temat" }, g.temat || ""),
            el("span", { class: "cichy-tekst" }, (g.autor || "") + " · " + czasTemu(g.ostatnio)))))));
      }
      c.replaceChildren(...czesci);
    }

    function rysujSync(g, blad) {
      const c = kSync.cialo;
      kSync.akcje.replaceChildren();
      if (blad) return c.replaceChildren(stanBledu(blad, "Git"));
      const zmianyPanelu = Array.isArray(g.zmiany_panelu) ? g.zmiany_panelu.length : Number(g.zmiany_panelu) || 0;
      const doPobrania = Number(g.do_pobrania) || 0;
      const doWyslania = Number(g.do_wyslania) || 0;
      const kafel = (liczba, opis, kolor) => el("div", { class: "licznik-kafel " + (liczba ? kolor : "") },
        el("strong", null, String(liczba)), el("span", null, opis));
      const czesci = [
        el("div", { class: "liczniki-kafle" },
          kafel(doPobrania, "do pobrania", "niebieski"),
          kafel(zmianyPanelu, odmiana(zmianyPanelu, ["zmiana panelu", "zmiany panelu", "zmian panelu"]) + " do wysłania", "zloto"),
          doWyslania ? kafel(doWyslania, odmiana(doWyslania, ["commit", "commity", "commitów"]) + " nie wysłane", "fiolet") : null),
        el("p", { class: "cichy-tekst" }, "Gałąź ", el("code", null, g.galaz || "?"),
          g.ostatni_fetch ? " · sprawdzono " + czasTemu(g.ostatni_fetch) : "",
          g.czyste === false && !zmianyPanelu ? " · są inne niezapisane zmiany w repo" : ""),
      ];
      if (ctx.ja.lokalny && !ctx.statyczny) {
        const bPobierz = el("button", { class: "przycisk", type: "button" }, ikona("pobierz"), el("span", null, "Pobierz"));
        const bWyslij = el("button", { class: "przycisk glowny", type: "button", disabled: !zmianyPanelu && !doWyslania }, ikona("wypchnij"), el("span", null, "Wyślij"));
        bPobierz.addEventListener("click", async () => {
          bPobierz.disabled = true;
          try {
            const r = await ctx.api("/api/git/pobierz", { metoda: "POST", czas: 120000 });
            toast(r && r.ok === false ? "Pobieranie nie wyszło: " + skroc(r.wyjscie, 200) : "Pobrano najnowsze zmiany.", r && r.ok === false ? "blad" : "ok");
          } catch (e) {
            toast("Pobieranie nie wyszło: " + e.message, "blad");
          } finally {
            bPobierz.disabled = false;
            odswiez();
          }
        });
        bWyslij.addEventListener("click", () => oknoWysylania(g, zmianyPanelu));
        czesci.push(el("div", { class: "rzad-przyciskow sync-przyciski" }, bPobierz, bWyslij));
      } else if (!ctx.statyczny) {
        czesci.push(el("p", { class: "cichy-tekst" }, "Pobieranie i wysyłanie działa na komputerze z panelem."));
      }
      c.replaceChildren(...czesci);
    }

    /** Co dokładnie pójdzie do publicznego repozytorium z plików sejfu (wiersze dodane i usunięte, z git diff). */
    function podgladSejfu(lista) {
      if (!Array.isArray(lista) || !lista.length) return null;
      return el("div", { class: "kolumna" },
        el("span", { class: "etykieta" }, "Zmiany w sejfie (repozytorium jest publiczne — sprawdź, co wysyłasz)"),
        lista.map((p) => el("div", null,
          el("p", { class: "cichy-tekst" }, el("code", null, p.plik)),
          el("pre", { class: "podglad-sejfu" },
            (p.wiersze || []).map((w) => el("div", { class: w[0] === "+" ? "dodane" : "usuniete" }, w)),
            p.ucieto ? el("div", { class: "cichy-tekst" }, "… i " + p.ucieto + " " + odmiana(p.ucieto, ["wiersz", "wiersze", "wierszy"]) + " więcej") : null))));
    }

    function oknoWysylania(g, ile) {
      const lista = Array.isArray(g.zmiany_panelu) ? g.zmiany_panelu : [];
      const sejf = Array.isArray(g.zmiany_sejfu) ? g.zmiany_sejfu : [];
      const pole = el("input", { class: "pole", placeholder: sejf.length ? "puste = opis zmian z panelu" : "np. Raport z HUD i komentarze", maxlength: "120", "aria-label": "Opis zmian" });
      const przycisk = el("button", { class: "przycisk glowny szeroki", type: "submit" }, ikona("wypchnij"), el("span", null, "Wyślij do repozytorium"));
      const form = el("form", { class: "formularz" },
        el("p", { class: "cichy-tekst" }, "Wyślę tylko dane panelu (raporty, komentarze, migawki)" +
          (sejf.length ? " i pliki sejfu zmienione w panelu (odpowiedzi, zadania, decyzje)" : "") + " — " + ile + " " +
          odmiana(ile, ["plik", "pliki", "plików"]) + ". Kod gry i reszta sejfu zostają bez zmian."),
        lista.length ? el("ul", { class: "lista pliki-lista" }, lista.slice(0, 12).map((z) => el("li", { class: "cichy-tekst" }, el("code", null, z.plik || String(z)), z.stan ? " · " + z.stan : ""))) : null,
        sejf.length ? el("ul", { class: "lista pliki-lista" }, sejf.map((p) => el("li", { class: "cichy-tekst" }, el("code", null, p), " · zmiana z panelu"))) : null,
        podgladSejfu(g.podglad_sejfu),
        (g.uwagi_sejfu || []).length ? el("p", { class: "cichy-tekst" }, ikona("ostrzezenie"), " ", g.uwagi_sejfu.join(" ")) : null,
        el("label", { class: "etykieta" }, "Opis (opcjonalnie)"), pole, przycisk);
      const ark = arkusz({ tytul: "Wyślij zmiany panelu", tresc: form });
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        przycisk.disabled = true;
        try {
          const r = await ctx.api("/api/git/wyslij", { metoda: "POST", cialo: pole.value.trim() ? { opis: pole.value.trim() } : {}, czas: 120000 });
          if (r && r.ok === false) throw new Error(skroc(r.wyjscie || "nieznany błąd", 240));
          toast(r && r.commit ? "Wysłano (" + String(r.commit).slice(0, 7) + ")." : "Wysłano.", "ok");
          if (r && r.uwaga) toast(r.uwaga, "info", { czas: 8000 });
          ark.zamknij();
        } catch (err) {
          toast("Wysyłanie nie wyszło: " + err.message, "blad");
          przycisk.disabled = false;
        } finally {
          odswiez();
        }
      });
    }

    function rysujMigawke(d, blad) {
      const c = kMigawka.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Podgląd"));
      const migawki = d.migawki || [];
      let m = migawki[0];
      if (d.najnowsza && typeof d.najnowsza === "object") m = d.najnowsza;
      else if (typeof d.najnowsza === "string") m = migawki.find((x) => x.id === d.najnowsza) || m;
      if (!m) return c.replaceChildren(pusty("Brak migawek", "Migawkę świata gry robi się w widoku Podgląd albo poleceniem agenta.", "migawka"));
      const zrzut = (m.zrzuty || [])[0];
      const otworz = () => ctx.idz("podglad", { migawka: m.id });
      c.replaceChildren(el("button", { type: "button", class: "migawka-mini", onclick: otworz, "aria-label": "Otwórz migawkę w podglądzie 3D" },
        zrzut ? el("img", { src: ctx.plik("/api/podglad/" + enc(m.id) + "/plik/" + enc(zrzut)), alt: m.tytul || "migawka", loading: "lazy" })
          : el("span", { class: "migawka-zastepcza" }, ikona("podglad")),
        el("span", { class: "migawka-opis" },
          el("strong", null, m.tytul || "Migawka"),
          el("span", { class: "cichy-tekst" }, [(m.kto || ""), m.czas ? czasTemu(m.czas) : "", m.czesci ? m.czesci + " " + odmiana(m.czesci, ["część", "części", "części"]) : ""].filter(Boolean).join(" · ")),
          el("span", { class: "chip niebieski" }, ikona("oko"), "Otwórz w 3D"))));
    }

    // ------------------------------------------------------------------ pobieranie
    const bierz = (sciezka, modul) => (ctx.jest(modul) ? ctx.api(sciezka) : Promise.reject(Object.assign(new Error("moduł wyłączony"), { status: 404 })));

    async function odswiez() {
      const [plan, rap, ob, git, pod, ag] = await Promise.allSettled([
        bierz("/api/sejf/plan", "sejf"), bierz("/api/raporty", "raporty"), bierz("/api/obecnosc", "obecnosc"),
        bierz("/api/git/stan", "gitsync"), bierz("/api/podglad", "podglad"), bierz("/api/sesje/agenda", "sesje"),
      ]);
      const sygn = (r) => (r.status === "fulfilled" ? JSON.stringify(r.value) : "!" + (r.reason && r.reason.message));
      const rysuj = (klucz, s, fn) => {
        if (ostatnieDane[klucz] === s) return;
        ostatnieDane[klucz] = s;
        try {
          fn();
        } catch (e) {
          console.warn("pulpit: " + klucz, e);
        }
      };
      const wart = (r) => (r.status === "fulfilled" ? r.value || {} : null);
      const blad = (r) => (r.status === "rejected" ? r.reason : null);
      const dane = {
        plan: wart(plan), raporty: rap.status === "fulfilled" ? (rap.value && rap.value.raporty) || [] : null,
        agenda: wart(ag), bladPlanu: blad(plan), bladRaportow: blad(rap),
      };
      const sPlan = sygn(plan);
      const sRap = sygn(rap);
      rysuj("gora", sPlan, () => rysujGore(dane.plan, dane.bladPlanu));
      rysuj("czeka", sPlan + sRap + sygn(ag), () => rysujCzeka(dane));
      rysuj("rozmowa", sygn(ob), () => rysujRozmowe(wart(ob), blad(ob)));
      rysuj("nowe", sPlan + sRap, () => rysujNowe(dane));
      rysuj("sync", sygn(git), () => rysujSync(wart(git), blad(git)));
      rysuj("teraz", sPlan, () => rysujTeraz(wart(plan), blad(plan)));
      rysuj("kto", sygn(ob), () => rysujKto(wart(ob), blad(ob)));
      rysuj("migawka", sygn(pod), () => rysujMigawke(wart(pod), blad(pod)));
    }

    window.addEventListener("bc:kto", () => {
      ostatnieDane.gora = null;
      odswiez();
    });

    return {
      el: korzen,
      pokaz() {
        odswiez();
        if (!stop) stop = ctx.odpytuj(odswiez, 15000);
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
