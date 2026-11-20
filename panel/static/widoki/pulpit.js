// Pulpit: najważniejsze na jednym ekranie, od góry: Czeka na Ciebie (liczba i trzy pierwsze sprawy), Rozmowa
// (zakładka Sesja: kto jest, czy agent słucha), Co nowego (raporty, decyzje, wpisy ludzi), Synchronizacja (stan stałej
// synchronizacji z GitHubem, Pobierz / Wyślij z podglądem zmian sejfu), Gry (portfel z Wytwórni: gry w prototypie,
// testach i publiczne z metrykami i „Pulpit gry”), a niżej reszta: Teraz (zadania), Kto pracuje, Napisz do agenta,
// Ostatnia migawka.

import { el, dopisz, zamien, ikona, czasTemu, dataKrotka, toast, arkusz, awatar, karta, pusty, stanBledu, ladowanie, odmiana, skroc } from "../wspolne/ui.js";
import { mdLinia } from "../wspolne/markdown.js";
import { zbudujKolejke } from "../wspolne/kolejka.js";
import { pobierzPrace, ostatniePrace, napisKonca, etapPracy, postep as postepPracy, kluczPozycji, inni as praceInnych,
  zMain, kolizjeMojej, kolizjeCudzej, tekstKolizji, dopelniacz, miniaturaPracy } from "../wspolne/prace.js";
import { kartaGry } from "../wspolne/wytwornia.js";

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
// „Czeka na Ciebie” liczy tylko sprawy czekające (wspolne/kolejka.js) — nieaktualne są w historii, więc się nie liczą
const STATUSY_DECYZJI = { zatwierdzona: "zatwierdzona", odrzucona: "odrzucona", do_decyzji: "do decyzji", propozycja: "propozycja", zastapiona: "zastąpiona", nieaktualna: "nieaktualna" };

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

    // Prace w toku (bc/prace.py): na samej górze, widoczna tylko, gdy są jakieś prace; stary serwer — wcale.
    // Przy pracy z podglądem — miniatura tego, co powstaje; przycisk „Podglądy” prowadzi do zakładki Podgląd.
    const kPrace = karta("Prace w toku", "zegar", { klasa: "karta-prace" });
    kPrace.el.hidden = true;
    const kCzeka = karta("Czeka na Ciebie", "pytanie", { klasa: "karta-czeka" });
    const kRozmowa = karta("Rozmowa", "mikrofon", { klasa: "karta-rozmowa" });
    const kNowe = karta("Co nowego", "zegar", { klasa: "karta-nowe" });
    const kSync = karta("Synchronizacja", "git", { klasa: "karta-sync" });
    const kTeraz = karta("Teraz", "ogien", { klasa: "karta-teraz" });
    const kKto = karta("Kto pracuje", "zespol", { klasa: "karta-kto" });
    const kAgent = karta("Napisz do agenta", "agent", { klasa: "karta-agent" });
    const kMigawka = karta("Ostatnia migawka", "migawka", { klasa: "karta-migawka" });
    // Portfel gier z Wytwórni (bc/wytwornia.py): gry na etapie prototyp / test / publiczna z metrykami i przyciskiem
    // „Pulpit gry”; stary serwer bez Wytwórni — karta ukryta.
    const kGry = karta("Gry", "rakieta", { klasa: "karta-gry" });
    kGry.el.hidden = true;

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
    const glowne = el("div", { class: "pulpit-glowne" }, kCzeka.el, kRozmowa.el, kNowe.el, kSync.el, kGry.el);
    const reszta = el("div", { class: "pulpit-reszta" }, kTeraz.el, kKto.el, ctx.statyczny ? null : kAgent.el, kMigawka.el);
    const korzen = el("div", { class: "widok pulpit" }, gora, kPrace.el, glowne,
      el("h2", { class: "pulpit-naglowek" }, "Reszta"), reszta);

    let stop = null;
    let stopPrac = null;
    let ostatnieDane = {};
    let zakonczoneOtwarte = false;
    let raportyPulpitu = [];            // do tytułów raportów przy pracach
    let migawkiPulpitu = new Map();     // id migawki -> meta (praca z samą migawką 3D pokazuje jej pierwszy zrzut)

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

    // ------------------------------------------------------------------ prace w toku
    let podpisPrac = "";
    const tytulRaportu = (id) => ((raportyPulpitu.find((r) => r.id === id) || {}).tytul || "");

    function opisDotyczy(p) {
      const d = p.dotyczy;
      if (d.typ === "raport") return "raport" + (tytulRaportu(d.id) ? " „" + skroc(tytulRaportu(d.id), 60) + "”" : "");
      if (d.typ === "pytanie") return "pytanie #" + d.id;
      return "decyzja " + d.id;
    }

    // Kolizje z pracami innych osób (bc/prace_wymiana.py): dane z publicznego repozytorium — tylko węzły tekstu (el)
    let danePrac = null;
    const nazwaTu = () => (danePrac && danePrac.wymiana && typeof danePrac.wymiana.nazwa === "string" ? danePrac.wymiana.nazwa : "");

    function linieKolizji(lista, o) {
      return lista.map((k) => el("p", { class: "praca-kolizja" + (k.nieaktualne ? " nieaktualne" : "") },
        ikona(k.nieaktualne ? "info" : "ostrzezenie"), el("span", null, tekstKolizji(k, o))));
    }

    function wierszInnej(p) {
      const n = napisKonca(p);
      const pod = [etapPracy(p), p.kto].filter(Boolean).join(" · ");
      return el("li", { class: "praca praca-inna stan-" + p.stan + (p.nieaktualna ? " nieaktualna" : ""), dataset: { praca: p.osoba + "/" + p.id } },
        el("div", { class: "praca-gora" },
          el("strong", { class: "praca-tytul" }, p.tytul || p.id),
          el("span", { class: "praca-koniec" + (p.nieaktualna ? " wstrzymane" : n.klasa ? " " + n.klasa : "") },
            p.nieaktualna ? "możliwie nieaktualne" : n.tekst)),
        pod ? el("p", { class: "cichy-tekst praca-pod" }, pod) : null,
        linieKolizji(kolizjeCudzej(danePrac, p.osoba, p.id), { przyCudzej: true, nazwaTu: nazwaTu() }));
    }

    function sekcjaInnych(lista) {
      const osoby = [];
      for (const p of lista) if (!osoby.includes(p.nazwa || p.osoba)) osoby.push(p.nazwa || p.osoba);
      return osoby.map((nazwa) => el("div", { class: "prace-osoba" },
        el("p", { class: "prace-osoba-nazwa" }, ikona("uzytkownik"), el("span", null, String(nazwa || "ktoś").slice(0, 40))),
        el("ul", { class: "lista prace-lista" }, lista.filter((p) => (p.nazwa || p.osoba) === nazwa).map(wierszInnej))));
    }

    function linieZMain(lista) {
      if (!lista.length) return null;
      const autorzy = [...new Set(lista.flatMap((z) => (Array.isArray(z.autorzy) ? z.autorzy : []).map((a) => String(a).slice(0, 40))))];
      const pliki = lista.slice(0, 4).map((z) => z.plik.slice(0, 120) + (z.niezapisane ? " (niezapisane zmiany)" : "")).join(", ");
      const t = Date.parse(typeof lista[0].kiedy === "string" ? lista[0].kiedy : "");
      const kiedy = isFinite(t) ? " o " + new Date(t).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" }) : "";
      const gdzie = nazwaTu() ? "na komputerze " + dopelniacz(nazwaTu()) : "na komputerze z panelem";
      return el("p", { class: "praca-kolizja" }, ikona("ostrzezenie"), el("span", null,
        (autorzy.join(", ") || "Ktoś") + kiedy + " wysłał(a) na GitHuba zmiany w plikach, nad którymi trwa praca " + gdzie + ": " + pliki +
        (lista.length > 4 ? " i " + (lista.length - 4) + " więcej" : "") + ". Zanim ktoś zapisze swoje zmiany, umówcie się, czyja wersja zostaje."));
    }

    function wierszPracy(p) {
      const n = napisKonca(p);
      const etap = etapPracy(p);
      const pp = p.stan === "gotowe" ? null : postepPracy(p);
      const klucz = kluczPozycji(p);
      const pod = [etap, p.kto].filter(Boolean).join(" · ");
      // podgląd tego, co powstaje (ostatni zrzut, klatka z folderu albo zrzut migawki 3D) — mała miniatura z prawej
      // obok tekstu, klik = powiększenie (styl.css: .praca.z-podgladem)
      const podglad = miniaturaPracy(ctx, p, { naMigawke: (id) => ctx.idz("podglad", { migawka: id }), migawki: migawkiPulpitu });
      return el("li", { class: "praca stan-" + p.stan + (n.klasa ? " " + n.klasa : "") + (podglad ? " z-podgladem" : ""), dataset: { praca: p.id } },
        podglad,
        el("div", { class: "praca-gora" },
          el("strong", { class: "praca-tytul" }, p.tytul || p.id),
          el("span", { class: "praca-koniec" + (n.klasa ? " " + n.klasa : "") }, n.tekst)),
        p.opis && p.stan !== "gotowe" ? el("p", { class: "cichy-tekst praca-opis" }, p.opis) : null,
        pod ? el("p", { class: "cichy-tekst praca-pod" }, pod) : null,
        pp !== null ? el("span", { class: "pasek praca-pasek", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(Math.round(pp * 100)), "aria-label": "Postęp: " + (p.tytul || "") },
          el("span", { class: "pasek-wypelnienie", style: { width: Math.round(pp * 100) + "%", display: "block" } })) : null,
        p.komunikat && p.stan !== "w_toku" ? el("p", { class: "cichy-tekst praca-komunikat" }, p.komunikat) : null,
        p.stan === "gotowe" || p.stan === "blad" ? null : linieKolizji(kolizjeMojej(danePrac, p.id), {}),
        (p.raport || klucz) ? el("div", { class: "praca-linki" },
          p.raport ? el("button", { type: "button", class: "praca-link", onclick: () => doSprawy("raport-" + p.raport) },
            "Zobacz raport" + (tytulRaportu(p.raport) ? " „" + skroc(tytulRaportu(p.raport), 60) + "”" : "")) : null,
          klucz && !(p.raport && klucz === "raport-" + p.raport) ? el("button", { type: "button", class: "praca-link", onclick: () => doSprawy(klucz) }, "Dotyczy: " + opisDotyczy(p)) : null) : null);
    }

    function rysujPrace(d) {
      const prace = (d && Array.isArray(d.prace)) ? d.prace : [];
      const inni = praceInnych(d);                                 // stary serwer bez pól inni/kolizje/z_main: puste
      const zm = zMain(d);
      const tytuly = prace.map((p) => tytulRaportu(p.raport) + "|" + (p.dotyczy && p.dotyczy.typ === "raport" ? tytulRaportu(p.dotyczy.id) : ""));
      const podpis = JSON.stringify([prace, tytuly, d && d.inni, d && d.kolizje, d && d.z_main, Math.floor(Date.now() / 60000)]);
      if (podpis === podpisPrac) return;
      podpisPrac = podpis;
      danePrac = d || null;
      kPrace.el.hidden = !prace.length && !inni.length && !zm.length;
      kPrace.akcje.replaceChildren();
      if (kPrace.el.hidden) return kPrace.cialo.replaceChildren();
      const aktywne = prace.filter((p) => p.stan !== "gotowe");
      const gotowe = prace.filter((p) => p.stan === "gotowe");
      const wToku = aktywne.filter((p) => p.stan === "w_toku").length;
      if (wToku) kPrace.akcje.append(el("span", { class: "cichy-tekst" }, String(wToku) + " " + odmiana(wToku, ["trwa", "trwają", "trwa"])));
      if (ctx.maWidok("podglad") && aktywne.some((p) => p.podglad || p.migawka)) {
        kPrace.akcje.append(el("button", { type: "button", class: "przycisk cichy maly", onclick: () => ctx.idz("podglad", { zakladka: "przeglad" }) },
          ikona("obraz"), el("span", null, "Podglądy")));
      }
      const dzis = new Date().toDateString();
      const wszystkieDzis = gotowe.every((p) => new Date(p.zakonczono || p.aktualizacja).toDateString() === dzis);
      let det = null;
      if (gotowe.length) {
        det = el("details", { class: "zwijane prace-zakonczone", open: zakonczoneOtwarte || !aktywne.length },
          el("summary", null, ikona("dol"), el("span", null, (wszystkieDzis ? "Zakończone dziś" : "Zakończone ostatnio") + " (" + gotowe.length + ")")),
          el("ul", { class: "lista prace-lista" }, gotowe.map(wierszPracy)));
        det.addEventListener("toggle", () => { if (aktywne.length) zakonczoneOtwarte = det.open; });
      }
      kPrace.cialo.replaceChildren(
        linieZMain(zm) || "",
        inni.length ? el("p", { class: "prace-osoba-nazwa" }, ikona("uzytkownik"), el("span", null, nazwaTu() || "Ten komputer")) : "",
        aktywne.length ? el("ul", { class: "lista prace-lista" }, aktywne.map(wierszPracy))
          : el("p", { class: "cichy-tekst" }, "Teraz nic nie trwa."),
        det || "",
        ...(inni.length ? sekcjaInnych(inni) : []));
    }

    async function odswiezPrace() {
      const d = await pobierzPrace(ctx);
      try {
        rysujPrace(d);
      } catch (e) {
        console.warn("pulpit: prace", e);
      }
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
      // stała synchronizacja (D-070): mały stan obok przycisków; stary serwer bez pola `auto` — widok jak dotąd
      if (g.auto && typeof g.auto === "object" && !ctx.statyczny) {
        czesci.push(stanSynchronizacji(g.auto));
        const p = g.auto.pobranie;
        if (p && p.kiedy && Date.now() - Date.parse(p.kiedy) < 30 * 60000) czesci.push(wierszPobrania(p));
      }
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

    /** Krótki napis i kolor stanu stałej synchronizacji (pole `auto` z GET /api/git/stan). */
    function napisAuto(a) {
      const n = Number(a.plikow) || 0;
      switch (a.stan) {
        case "ok": return { tekst: (a.zgodne ? "Zsynchronizowano " + godzina(a.zgodne) : "Synchronizacja włączona") + (a.krotko ? " · " + a.krotko : ""), kolor: "zielen" };
        case "pobieram": return { tekst: "Pobieram zmiany…", kolor: "niebieski" };
        case "wysylam": return { tekst: "Wysyłam zmiany…", kolor: "niebieski" };
        case "czeka": return { tekst: "Czeka: " + (a.krotko || (n ? "lokalne zmiany w " + n + " " + odmiana(n, ["pliku", "plikach", "plikach"]) : "na człowieka")), kolor: "zloto" };
        case "konflikt": return { tekst: "Konflikt — potrzebny człowiek", kolor: "czerwien" };
        case "brak_logowania": return { tekst: "Brak logowania do GitHuba", kolor: "czerwien" };
        case "blad": return { tekst: "Błąd synchronizacji" + (a.krotko ? " (" + a.krotko + ")" : ""), kolor: "czerwien" };
        case "wylaczona": return { tekst: "Synchronizacja ręczna", kolor: "szary" };
        default: return { tekst: "Synchronizacja", kolor: "szary" };
      }
    }

    /** „17:42” dziś, „13 lis 17:42” innego dnia. */
    function godzina(t) {
      const d = new Date(t);
      if (isNaN(d)) return "";
      const hm = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
      const dzis = new Date();
      return d.toDateString() === dzis.toDateString() ? hm : dataKrotka(t) + " " + hm;
    }

    function stanSynchronizacji(a) {
      const n = napisAuto(a);
      return el("button", { type: "button", class: "sync-auto " + n.kolor, dataset: { stan: String(a.stan || "") }, onclick: () => oknoAuto(a), "aria-label": n.tekst + " — szczegóły" },
        el("span", { class: "sync-auto-kropka", "aria-hidden": "true" }), el("span", { class: "sync-auto-tekst" }, n.tekst), ikona("prawo"));
    }

    /** „Pobrano 14:03 · Paweł: 2 zmiany — temat; temat” (autorzy i tematy to tekst od ludzi — zawsze jako tekst). */
    function wierszPobrania(p) {
      const tematy = (p.commity || []).slice(0, 3).map((c) => "„" + skroc(c.temat || "", 70) + "”").join("; ");
      return el("p", { class: "cichy-tekst sync-pobranie" }, ikona("pobierz"), " ",
        "Pobrano " + godzina(p.kiedy) + " · " + (p.autorzy || []).join(", ") + ": " + p.ile + " " + odmiana(Number(p.ile) || 0, ["zmiana", "zmiany", "zmian"]) + (tematy ? " — " + tematy : ""));
    }

    function oknoAuto(a) {
      const n = napisAuto(a);
      const p = a.pobranie;
      const w = a.wyslanie;
      const pliki = Array.isArray(a.pliki) ? a.pliki : [];
      const tresc = el("div", { class: "kolumna sync-szczegoly" },
        el("p", null, el("span", { class: "chip " + n.kolor }, n.tekst)),
        a.opis ? el("p", null, a.opis) : null,
        pliki.length ? el("div", null, el("span", { class: "etykieta" }, "Pliki"),
          el("ul", { class: "lista pliki-lista" }, pliki.map((f) => el("li", { class: "cichy-tekst" }, el("code", null, f)))),
          Number(a.plikow) > pliki.length ? el("p", { class: "cichy-tekst" }, "… i " + (a.plikow - pliki.length) + " więcej") : null) : null,
        a.co_zrobic ? el("div", null, el("span", { class: "etykieta" }, "Co zrobić"), el("p", null, a.co_zrobic)) : null,
        el("span", { class: "etykieta" }, "Ostatnio"),
        el("ul", { class: "lista" },
          el("li", { class: "cichy-tekst" }, "Wszystko zgodne: " + (a.zgodne ? godzina(a.zgodne) + " (" + czasTemu(a.zgodne) + ")" : "jeszcze nie")),
          el("li", { class: "cichy-tekst" }, "Pobrane: " + (p ? godzina(p.kiedy) + " · " + p.ile + " " + odmiana(Number(p.ile) || 0, ["zmiana", "zmiany", "zmian"]) + " (" + (p.autorzy || []).join(", ") + ")" : "—")),
          p && (p.commity || []).length ? el("li", null, el("ul", { class: "lista commity" }, p.commity.map((c) => el("li", { class: "cichy-tekst" }, el("strong", null, c.autor || ""), ": " + (c.temat || ""))))) : null,
          el("li", { class: "cichy-tekst" }, "Wysłane: " + (w ? godzina(w.kiedy) + (w.temat ? " · " + w.temat : "") + (w.recznie ? " (przyciskiem)" : "") : "—"))),
        el("p", { class: "cichy-tekst" }, a.wlaczona === false
          ? "Samo pobieranie i wysyłanie nie działa — zostają przyciski Pobierz i Wyślij."
          : "Panel sam sprawdza GitHuba co " + (a.co_s || 90) + " s, pobiera cudze zmiany i wysyła zmiany z panelu po " + (a.wyslij_po_s || 60) + " s spokoju. Nigdy nie rusza plików, nad którymi ktoś pracuje."));
      arkusz({ tytul: "Synchronizacja z GitHubem", tresc });
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

    function rysujGry(d, blad) {
      if (blad || !d || !Array.isArray(d.pomysly)) {
        kGry.el.hidden = true;
        return;
      }
      kGry.el.hidden = false;
      const po = new Map(d.pomysly.map((p) => [p.id, p]));
      const gry = (d.gry || []).map((id) => po.get(id)).filter(Boolean);
      const n = d.pomysly.length;
      kGry.akcje.replaceChildren(el("a", { class: "przycisk cichy maly", href: "#/wytwornia" }, el("span", null, "Wytwórnia"), ikona("prawo")));
      kGry.cialo.replaceChildren(
        gry.length ? el("div", { class: "wyt-gry" }, gry.map((p) => kartaGry(p, { zwarta: true })))
          : el("p", { class: "cichy-tekst" }, "Żadna gra nie jest jeszcze na etapie prototypu, testu ani publicznym."),
        el("p", { class: "cichy-tekst" }, "W Wytwórni: " + n + " " + odmiana(n, ["pomysł", "pomysły", "pomysłów"]) + " (lejek, oceny, radar trendów)."));
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
      const [plan, rap, ob, git, pod, ag, wyt] = await Promise.allSettled([
        bierz("/api/sejf/plan", "sejf"), bierz("/api/raporty", "raporty"), bierz("/api/obecnosc", "obecnosc"),
        bierz("/api/git/stan", "gitsync"), bierz("/api/podglad", "podglad"), bierz("/api/sesje/agenda", "sesje"),
        bierz("/api/wytwornia", "wytwornia"),
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
      if (dane.raporty) raportyPulpitu = dane.raporty;
      if (pod.status === "fulfilled") migawkiPulpitu = new Map(((pod.value && pod.value.migawki) || []).map((m) => [m.id, m]));
      rysuj("prace-tytuly", JSON.stringify([(dane.raporty || []).map((r) => [r.id, r.tytul]), [...migawkiPulpitu.keys()]]), () => {
        podpisPrac = "";                                           // tytuły raportów i migawki przy pracach
        rysujPrace(ostatniePrace());
      });
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
      rysuj("gry", sygn(wyt), () => rysujGry(wart(wyt), blad(wyt)));
    }

    window.addEventListener("bc:kto", () => {
      ostatnieDane.gora = null;
      odswiez();
    });
    // panel sam pobrał zmiany z GitHuba (powłoka, app.js) — od razu nowe dane, bez czekania na odpytywanie
    window.addEventListener("bc:git-pobrano", () => odswiez());
    // prace w toku: nowa treść z dowolnego miejsca panelu (powłoka pyta co 30 s) i moduły znane po starcie
    window.addEventListener("bc:prace", (e) => {
      try {
        rysujPrace(e.detail);
      } catch (err) {
        console.warn("pulpit: prace", err);
      }
    });
    window.addEventListener("bc:moduly", () => odswiezPrace());

    return {
      el: korzen,
      pokaz() {
        odswiez();
        odswiezPrace();
        if (!stop) stop = ctx.odpytuj(odswiez, 15000);
        if (!stopPrac) stopPrac = ctx.odpytuj(odswiezPrace, 30000);   // także przy powrocie do karty
      },
      ukryj() {
        if (stop) stop();
        stop = null;
        if (stopPrac) stopPrac();
        stopPrac = null;
      },
    };
  },
};
