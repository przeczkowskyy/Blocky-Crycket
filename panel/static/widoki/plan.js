// Plan: okno na sejf — harmonogram (roadmapa), zadania, decyzje, pytania otwarte, dziennik zmian.
//
// Praca na sejfie (bc/zapis.py): odpowiedzi na pytania, odhaczanie i dodawanie zadań, statusy decyzji. Zmiany idą
// do tych samych plików B&C/Produkcja/*.md, których używa Obsidian. Każdy zapis odsyła znacznik wersji pliku z chwili,
// gdy człowiek go zobaczył (`wersjeWidoczne`) — jeśli ktoś w tym czasie zmienił plik, serwer odmawia (409), a widok
// pokazuje „Ktoś zmienił ten plik — odświeżam”. Statusy decyzji (zmiana kanonu) zmienia tylko Game Director
// (ctx.ja.game_director = klucz Game Directora, nie imię); okno zatwierdzania wysyła wersję Rejestru z chwili
// otwarcia (to, co Game Director przeczytał), a nie z odświeżenia w tle. Formularze mają flagę „w toku” (podwójny
// Ctrl+Enter / Enter = jedno żądanie), odhaczenie przy konflikcie wersji ponawia się raz, a przy ukryciu karty idzie
// od razu (keepalive). W lustrze tylko do odczytu przycisków zapisu nie ma.

import { el, ikona, czasTemu, dataKrotka, pusty, stanBledu, ladowanie, przelacznik, odmiana, toast, arkusz, skroc } from "../wspolne/ui.js";
import { md, mdLinia } from "../wspolne/markdown.js";
import { komentarze } from "../wspolne/komentarze.js";

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
const CZAS_COFNIECIA_MS = 5000;

const html = (tekst) => el("div", { class: "md", html: md(tekst || "") });
const linia = (tekst, klasa) => el("span", { class: "md md-linia" + (klasa ? " " + klasa : ""), html: mdLinia(tekst || "") });

/** Tekst bez znaczników Markdown (do toastów i etykiet): [[a|b]] → b, [[a]] → a, `kod` → kod. */
function zwykly(t) {
  return String(t || "").replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2").replace(/\[\[([^\]]+)\]\]/g, "$1")
    .replace(/[`*_]/g, "").trim();
}

function dzisiaj() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

function postep(f) {
  let p = Number(f.postep);
  if (f.postep === null || f.postep === undefined || !isFinite(p)) {
    const poz = f.pozycje || [];
    p = poz.length ? poz.filter((x) => x.zrobione).length / poz.length : 0;
  } else if (p > 1) p /= 100;
  return Math.max(0, Math.min(1, p));
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
    let wersjeWidoczne = {};          // znaczniki wersji plików z ostatniego narysowania (to, co widzi człowiek)
    let odlozone = false;             // nowe dane przyszły, gdy ktoś pisał — narysuj po wyjściu z pola
    const szkice = new Map();         // nr pytania -> niewysłany tekst odpowiedzi
    const oczekujace = new Map();     // id zadania -> {p, zegar, toast} — odhaczenie czeka 5 s na „Cofnij”
    const otwarteKomentarze = new Set();
    const ostatnieKlikniecia = new Map(); // id zadania -> czas kliknięcia (drugi klik < 400 ms = przypadkowy podwójny)
    let kolejka = Promise.resolve();  // odhaczenia idą do serwera po kolei
    let ostatniBladZapisu = null;     // błąd ostatniego nieudanego zapisu (formularze sprawdzają jego `kod`)

    const mozeZapisywac = () => !ctx.statyczny && ctx.ja.zapis_sejfu !== false;

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
    const podtytul = el("p", { class: "cichy-tekst" }, "Na żywo z sejfu Obsidiana (B&C/Produkcja).");
    const korzen = el("div", { class: "widok plan" },
      el("header", { class: "nagl-widoku" },
        el("div", null, el("h1", null, "Plan"), podtytul),
        odswiezBtn),
      el("div", { class: "przelacznik-przewijany" }, segment),
      tresc, zrodla);

    const piszeTeraz = () => {
      const a = document.activeElement;
      return !!(a && tresc.contains(a) && /^(TEXTAREA|INPUT|SELECT)$/.test(a.tagName));
    };
    tresc.addEventListener("focusout", () => setTimeout(() => {
      if (odlozone && !piszeTeraz()) {
        odlozone = false;
        rysuj();
      }
    }, 250));

    // ------------------------------------------------------------------ zapis do sejfu (wspólne)
    /**
     * POST z wersją pliku, którą człowiek widział. Zwraca odpowiedź albo null (błąd już pokazany toastem).
     * opcje.wersja — wersja zapamiętana wcześniej (np. w chwili otwarcia arkusza decyzji), zamiast tej z ostatniego
     * narysowania; opcje.konflikt — własny komunikat przy 409 „ktoś zmienił plik”.
     */
    async function zapiszDoSejfu(trasa, cialo, klucz, opcje = {}) {
      const wersja = opcje.wersja !== undefined ? opcje.wersja : wersjeWidoczne[klucz];
      ostatniBladZapisu = null;
      try {
        const w = await ctx.api(trasa, { metoda: "POST", cialo: Object.assign({}, cialo, { wersja: wersja || "" }) });
        if (w && w.plan) {
          dane = w.plan;
          blad = null;
          pobrano = Date.now();
        }
        rysuj();
        if (w && w.uwaga) toast(w.uwaga, "info", { czas: 6500 });
        return w;
      } catch (e) {
        ostatniBladZapisu = e;
        if (e.status === 409 && e.dane && e.dane.kod === "konflikt_wersji") {
          toast(opcje.konflikt || "Ktoś zmienił ten plik — odświeżam", "info", { czas: 6500 });
          await pobierz(true);
        } else if (e.status === 409 && e.dane && e.dane.kod === "juz_zapisane") {
          toast(e.message, "info");
          await pobierz(true);
        } else {
          toast(e.message || "Nie udało się zapisać w sejfie.", "blad");
        }
        return null;
      }
    }

    /** Czy odpowiedź o tej treści już widać pod pytaniem (np. pierwszy z dwóch Ctrl+Enter się zapisał). */
    function odpowiedzJuzJest(nr, tekst) {
      const p = ((dane && dane.pytania) || []).find((x) => x.nr === nr);
      const plaski = String(tekst).replace(/[ \t]*[\r\n]+\s*/g, " / ").replace(/\s{2,}/g, " ").trim();
      return !!(p && plaski && String(p.odpowiedz_md || "").includes(plaski));
    }

    // ------------------------------------------------------------------ harmonogram
    function pozycjaZadania(p, opcje = {}) {
      const czeka = oczekujace.has(p.id);
      const zrobione = p.zrobione || czeka;
      let pole;
      if (opcje.odhaczalne && !p.zrobione) {
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
          poz.length ? el("ul", { class: "lista" }, poz.map((x) => pozycjaZadania(x))) : null);
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
    function odhaczZOpoznieniem(p) {
      if (!p.id || oczekujace.has(p.id)) return;
      const wpis = { p, zegar: null, toast: null };
      oczekujace.set(p.id, wpis);
      wpis.toast = toast("Odhaczono: " + skroc(zwykly(p.tekst_md), 70), "ok",
        { czas: CZAS_COFNIECIA_MS, akcja: { tekst: "Cofnij", fn: () => cofnij(p.id) } });
      wpis.zegar = setTimeout(() => wyslijOdhaczenie(p.id), CZAS_COFNIECIA_MS);
      rysuj();
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
      rysuj();
    }

    function wyslijOdhaczenie(id, wTle) {
      const w = oczekujace.get(id);
      if (!w) return kolejka;
      clearTimeout(w.zegar);
      if (w.wyslane) return kolejka;                           // już w kolejce (np. ukrycie karty i pagehide)
      w.wyslane = true;
      kolejka = kolejka.then(async () => {
        if (!oczekujace.has(id)) return;
        w.wTrakcie = true;
        // wersja z chwili wysłania: wcześniejsze odhaczenie z tej kolejki zmieniło plik, a człowiek to widział
        const wynik = await odhaczWSejfie(id, w.p, wTle);
        oczekujace.delete(id);
        rysuj();
        if (wynik) toast("Zapisano w Zadaniach: " + skroc(zwykly(w.p.tekst_md), 60), "ok");
      });
      return kolejka;
    }

    /**
     * Odhaczenie po id (skrót treści zadania) — bezpieczne do powtórzenia: gdy ktoś w tym czasie zmienił inną część
     * Zadań (409 „konflikt wersji”), ponawia raz z aktualną wersją. Zadanie o zmienionej treści ma inne id, więc
     * ponowienie go nie odhaczy (404). Niepowodzenie = wyraźny błąd, a nie ciche zniknięcie odhaczenia.
     * Rysuje dopiero po zdjęciu z kolejki (żeby wiersz nie mignął jako otwarty). `wTle` = karta znika (keepalive).
     */
    async function odhaczWSejfie(id, p, wTle) {
      let wersja = wersjeWidoczne.zadania || "";
      for (let proba = 0; proba < 2; proba++) {
        try {
          const w = await ctx.api("/api/sejf/zadania/odhacz", { metoda: "POST", cialo: { id, wersja }, keepalive: !!wTle });
          if (w && w.plan) {
            dane = w.plan;
            blad = null;
            pobrano = Date.now();
            if (w.plan.wersje) wersjeWidoczne = Object.assign({}, w.plan.wersje);
          }
          if (w && w.uwaga) toast(w.uwaga, "info", { czas: 6500 });
          return w;
        } catch (e) {
          if (proba === 0 && e.status === 409 && e.dane && e.dane.kod === "konflikt_wersji" && e.dane.wersja) {
            wersja = e.dane.wersja;                            // ktoś zmienił plik: ta sama operacja na nowej wersji
            continue;
          }
          toast("Nie odhaczono: " + skroc(zwykly(p.tekst_md), 60) + " — " + (e.message || "błąd"), "blad", { czas: 8000 });
          await pobierz(true);
          return null;
        }
      }
      return null;
    }

    function wyslijWszystkieOczekujace(wTle) {
      for (const id of [...oczekujace.keys()]) wyslijOdhaczenie(id, wTle);
    }

    function oknoDodawania() {
      let sekcja = "teraz";
      let priorytet = "średni";
      const pole = el("textarea", { class: "pole", rows: 2, maxlength: "300", placeholder: "np. Test HUD na telefonie", "aria-label": "Treść zadania" });
      const segSekcja = przelacznik([{ id: "teraz", tekst: "Teraz" }, { id: "backlog", tekst: "Backlog" }], sekcja, (id) => { sekcja = id; }, "Sekcja");
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
          const w = await zapiszDoSejfu("/api/sejf/zadania/dodaj", { tekst, sekcja, priorytet }, "zadania");
          if (w) {
            ark.zamknij();
            toast("Dodano zadanie (" + (sekcja === "teraz" ? "Teraz" : "Backlog") + ").", "ok");
          } else {
            zapisz.disabled = false;
          }
        } finally {
          wToku = false;
        }
      });
    }

    function zadania() {
      const z = dane.zadania || {};
      const sekcje = z.sekcje || [];
      if (!sekcje.length) return pusty("Brak zadań", "Zadania opisuje notatka B&C/Produkcja/Zadania.md.", "plan");
      const moze = mozeZapisywac();
      const otwarte = typeof z.otwarte === "number" ? z.otwarte : sekcje.reduce((s, x) => s + (x.pozycje || []).filter((p) => !p.zrobione).length, 0);
      const zrobione = typeof z.zrobione === "number" ? z.zrobione : sekcje.reduce((s, x) => s + (x.pozycje || []).filter((p) => p.zrobione).length, 0);
      const naglowek = el("div", { class: "liczniki-kafle" },
        el("div", { class: "licznik-kafel zloto" }, el("strong", null, String(otwarte)), el("span", null, "otwarte")),
        el("div", { class: "licznik-kafel zielen" }, el("strong", null, String(zrobione)), el("span", null, "zrobione")));
      const akcje = moze ? el("div", { class: "plan-akcje" },
        el("p", { class: "cichy-tekst" }, "Pole wyboru odhacza zadanie w sejfie (5 s na cofnięcie)."),
        el("button", { type: "button", class: "przycisk glowny", onclick: oknoDodawania }, ikona("plus"), el("span", null, "Dodaj zadanie"))) : null;
      const karty = sekcje.map((s, i) => {
        const poz = s.pozycje || [];
        const otw = poz.filter((p) => !p.zrobione);
        const zrob = poz.filter((p) => p.zrobione);
        const tylkoZrobione = !otw.length && zrob.length;
        const wiersz = (p) => pozycjaZadania(p, { odhaczalne: moze });
        return el("article", { class: "karta sekcja-zadan", style: { "--i": i } },
          el("h2", { class: "karta-tytul" }, el("span", null, s.nazwa || "Zadania"),
            el("span", { class: "karta-akcje" }, el("span", { class: "chip" }, otw.length + " / " + poz.length))),
          otw.length ? el("ul", { class: "lista" }, otw.map(wiersz)) : null,
          zrob.length ? el("details", { class: "zwijane", open: false },
            el("summary", null, ikona("dol"), tylkoZrobione ? "Pokaż " + zrob.length + " " + odmiana(zrob.length, ["pozycję", "pozycje", "pozycji"]) : "Zrobione (" + zrob.length + ")"),
            el("ul", { class: "lista" }, zrob.map(wiersz))) : null,
          !poz.length ? el("p", { class: "cichy-tekst" }, "Pusta sekcja.") : null);
      });
      return el("div", { class: "kolumna" }, naglowek, akcje, karty);
    }

    // ------------------------------------------------------------------ decyzje
    function oknoDecyzji(d, status) {
      const zatw = status === "zatwierdzona";
      // Wersja Rejestru z chwili otwarcia okna = treść, którą Game Director właśnie przeczytał (na karcie i w oknie).
      // Odpytywanie w tle może w tym czasie przerysować listę za oknem i podmienić `wersjeWidoczne` — wysłanie tej
      // nowszej wersji zatwierdziłoby treść, której nikt nie widział. Dlatego idzie wersja zapamiętana tutaj.
      const wersjaPrzeczytana = wersjeWidoczne.decyzje || "";
      const imie = (ctx.ja.kto || "").trim();
      const kto = imie && imie !== "gość" && imie !== "Game Director" ? "Game Director (" + imie + ")" : "Game Director";
      const pole = el("textarea", { class: "pole", rows: 3, maxlength: "1000", placeholder: zatw ? "Dlaczego tak (opcjonalnie)" : "Dlaczego nie (opcjonalnie)", "aria-label": "Uzasadnienie" });
      const przycisk = el("button", { type: "submit", class: "przycisk " + (zatw ? "sukces" : "grozny") },
        ikona(zatw ? "ok" : "krzyzyk"), el("span", null, (zatw ? "Zatwierdzam " : "Odrzucam ") + d.id));
      const anuluj = el("button", { type: "button", class: "przycisk cichy" }, "Anuluj");
      const form = el("form", { class: "formularz" },
        el("p", null, el("strong", null, d.id + " "), d.tytul || ""),
        d.opis_md ? el("div", { class: "decyzja-podglad" }, html(d.opis_md)) : null,
        el("div", { class: "podpowiedz" }, ikona("info"), el("div", null,
          el("strong", null, "To zmiana kanonu"),
          el("p", null, "W Rejestrze decyzji wiersz statusu zmieni się na „" + (zatw ? "✅ zatwierdzona" : "❌ odrzucona") +
            " · … · zdecydował: " + kto + " " + dzisiaj() + "”, a ślad trafi do Dziennika zmian. Cofnąć można tylko ręcznie w Obsidianie."),
          el("p", { class: "cichy-tekst" }, "Zatwierdzasz dokładnie tę treść. Jeśli ktoś zmieni Rejestr, zanim klikniesz, panel nic nie zapisze i pokaże nową wersję."))),
        el("label", { class: "etykieta" }, "Uzasadnienie (opcjonalnie)"), pole,
        el("div", { class: "rzad-przyciskow decyzja-potwierdz" }, anuluj, el("span", { class: "rozpychacz" }), przycisk));
      const ark = arkusz({ tytul: (zatw ? "Zatwierdzić " : "Odrzucić ") + d.id + "?", tresc: form });
      anuluj.addEventListener("click", () => ark.zamknij());
      let wToku = false;
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (wToku) return;
        wToku = true;
        przycisk.disabled = true;
        try {
          const w = await zapiszDoSejfu("/api/sejf/decyzje/" + encodeURIComponent(d.id) + "/status",
            { status, uzasadnienie: pole.value.trim() }, "decyzje",
            { wersja: wersjaPrzeczytana, konflikt: "Rejestr decyzji zmienił się, odkąd otworzyłeś to okno — nic nie zapisano. Przeczytaj " + d.id + " jeszcze raz." });
          if (w) {
            ark.zamknij();
            toast(d.id + (zatw ? " zatwierdzona." : " odrzucona."), "ok");
          } else if (ostatniBladZapisu && ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod === "konflikt_wersji") {
            ark.zamknij();                                     // stara treść w oknie nie może zostać zatwierdzona
          } else {
            przycisk.disabled = false;
          }
        } finally {
          wToku = false;
        }
      });
    }

    function komentarzeDecyzji(d) {
      const plik = (dane.pliki && dane.pliki.decyzje) || "B&C/Produkcja/Rejestr decyzji.md";
      const cel = { typ: "notatka", cel: plik + "#" + d.id, etykieta: d.id + " " + (d.tytul || "") };
      const miejsce = el("div", { class: "decyzja-watek" });
      const det = el("details", { class: "zwijane decyzja-komentarze", open: otwarteKomentarze.has(d.id) },
        el("summary", null, ikona("dol"), ikona("komentarz"), "Komentarze"), miejsce);
      const zamontuj = () => {
        if (!miejsce.firstChild) miejsce.appendChild(komentarze(ctx, cel));
      };
      det.addEventListener("toggle", () => {
        if (det.open) {
          otwarteKomentarze.add(d.id);
          zamontuj();
        } else otwarteKomentarze.delete(d.id);
      });
      if (det.open) zamontuj();
      return det;
    }

    function decyzje() {
      const lista = dane.decyzje || [];
      if (!lista.length) return pusty("Brak decyzji", "Decyzje opisuje notatka B&C/Produkcja/Rejestr decyzji.md.", "decyzja");
      const moze = mozeZapisywac();
      const gd = moze && !!ctx.ja.game_director;
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
        const otwarta = d.status === "propozycja" || d.status === "do_decyzji";
        let akcje = null;
        if (moze && otwarta) {
          akcje = gd
            ? el("div", { class: "rzad-przyciskow decyzja-akcje" },
              el("button", { type: "button", class: "przycisk sukces maly", onclick: () => oknoDecyzji(d, "zatwierdzona") }, ikona("ok"), el("span", null, "Zatwierdź")),
              el("button", { type: "button", class: "przycisk grozny maly", onclick: () => oknoDecyzji(d, "odrzucona") }, ikona("krzyzyk"), el("span", null, "Odrzuć")))
            : el("p", { class: "decyzja-gd cichy-tekst" }, ikona("klodka"), "Zatwierdza Game Director — możesz zostawić komentarz.");
        }
        return el("article", { class: "karta decyzja status-" + (d.status || "brak"), style: { "--i": i } },
          el("div", { class: "decyzja-gora" },
            el("span", { class: "decyzja-id" }, d.id || "D-?"),
            el("span", { class: "chip " + s.kolor }, d.emoji ? el("span", { "aria-hidden": "true" }, d.emoji) : null, s.tekst),
            d.kategoria ? el("span", { class: "chip" }, d.kategoria) : null),
          el("h2", { class: "decyzja-tytul" }, d.tytul || ""),
          (d.meta || []).length ? el("p", { class: "cichy-tekst decyzja-meta" }, (d.meta || []).join(" · ")) : null,
          d.opis_md ? html(d.opis_md) : null,
          akcje,
          !ctx.statyczny && d.id ? komentarzeDecyzji(d) : null);
      });
      return el("div", { class: "kolumna" }, pasekFiltrow,
        karty.length ? karty : pusty("Nic w tym filtrze", "Wybierz inny status."));
    }

    // ------------------------------------------------------------------ pytania
    /** Jak serwer podpisze odpowiedź (bc/zapis.py: znacznik zależy od klucza, nie od imienia). */
    function podpisOdpowiedzi() {
      const kto = (ctx.ja.kto || "").trim() || (ctx.ja.game_director ? "Game Director" : "gość");
      if (ctx.ja.game_director) return kto + " (Game Director, " + dzisiaj() + ") — znacznik zgody Game Directora";
      if (ctx.ja.lokalny) return kto + " (" + dzisiaj() + ")";
      return kto + " (gość panelu, " + dzisiaj() + ")";
    }

    function formularzOdpowiedzi(p, nr) {
      const pole = el("textarea", { class: "pole", rows: 2, maxlength: "2000", placeholder: "Twoja odpowiedź…", "aria-label": "Twoja odpowiedź na pytanie #" + nr });
      pole.value = szkice.get(nr) || "";
      pole.addEventListener("input", () => {
        if (pole.value) szkice.set(nr, pole.value);
        else szkice.delete(nr);
      });
      const wyslij = el("button", { type: "submit", class: "przycisk glowny maly" }, ikona("wyslij"), el("span", null, "Odpowiedz"));
      const agent = p.otwarte ? el("button", {
        type: "button", class: "przycisk maly cichy",
        onclick: () => ctx.idz("agent", {
          kontekst: [{ typ: "notatka", cel: "B&C/Produkcja/Pytania otwarte.md", etykieta: "Pytanie #" + nr }],
          tekst: "Pomóż mi odpowiedzieć na pytanie #" + nr + ": " + (p.tytul || ""),
        }),
      }, ikona("agent"), el("span", null, "Omów z agentem")) : null;
      const form = el("form", { class: "odpowiedz-formularz" },
        el("label", { class: "etykieta" }, "Twoja odpowiedź"), pole,
        el("p", { class: "cichy-tekst podpis-odpowiedzi" }, "Podpis w sejfie: " + podpisOdpowiedzi()),
        el("div", { class: "rzad-przyciskow" }, agent, el("span", { class: "rozpychacz" }), wyslij));
      pole.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          form.requestSubmit ? form.requestSubmit() : wyslij.click();
        }
      });
      let wToku = false;                                       // Ctrl+Enter dwa razy = jedno żądanie
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (wToku) return;
        const tekst = pole.value.trim();
        if (!tekst) {
          pole.focus();
          return;
        }
        wToku = true;
        wyslij.disabled = true;
        szkice.delete(nr);                                     // po udanym zapisie pole ma być puste po przerysowaniu
        try {
          const w = await zapiszDoSejfu("/api/sejf/pytania/" + encodeURIComponent(nr) + "/odpowiedz", { tekst }, "pytania");
          if (w) {
            toast("Zapisano odpowiedź na pytanie #" + nr + " w sejfie.", "ok");
          } else if (odpowiedzJuzJest(nr, tekst) || (ostatniBladZapisu && ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod === "juz_zapisane")) {
            rysuj();                                           // ta odpowiedź już jest w sejfie — nie przywracaj szkicu
          } else {
            szkice.set(nr, tekst);
            if (pole.isConnected) wyslij.disabled = false;
            else rysuj();
          }
        } finally {
          wToku = false;
        }
      });
      return form;
    }

    function pytania() {
      const lista = (dane.pytania || []).slice();
      if (!lista.length) return pusty("Brak pytań", "Pytania otwarte opisuje notatka B&C/Produkcja/Pytania otwarte.md.", "pytanie");
      const moze = mozeZapisywac();
      lista.sort((a, b) => (b.otwarte ? 1 : 0) - (a.otwarte ? 1 : 0));
      const otwarte = lista.filter((p) => p.otwarte).length;
      return el("div", { class: "kolumna" },
        el("p", { class: "cichy-tekst" }, otwarte ? otwarte + " " + odmiana(otwarte, ["pytanie czeka", "pytania czekają", "pytań czeka"]) + " na odpowiedź." : "Wszystkie pytania mają odpowiedź."),
        lista.map((p, i) => {
          const nr = p.nr || i + 1;
          let dolna = null;
          if (moze) {
            dolna = p.otwarte ? formularzOdpowiedzi(p, nr)
              : el("details", { class: "zwijane", open: szkice.has(nr) },
                el("summary", null, ikona("dol"), "Dopisz odpowiedź"), formularzOdpowiedzi(p, nr));
          } else if (p.otwarte && !ctx.statyczny) {
            dolna = el("div", { class: "rzad-przyciskow" },
              el("button", {
                type: "button", class: "przycisk maly",
                onclick: () => ctx.idz("agent", {
                  kontekst: [{ typ: "notatka", cel: "B&C/Produkcja/Pytania otwarte.md", etykieta: "Pytanie #" + nr }],
                  tekst: "Pomóż mi odpowiedzieć na pytanie #" + nr + ": " + (p.tytul || ""),
                }),
              }, ikona("agent"), el("span", null, "Omów z agentem")));
          }
          return el("article", { class: "karta pytanie" + (p.otwarte ? " otwarte" : ""), style: { "--i": i } },
            el("div", { class: "decyzja-gora" },
              el("span", { class: "decyzja-id" }, "#" + nr),
              p.otwarte ? el("span", { class: "chip zloto" }, ikona("pytanie"), "czeka na odpowiedź") : el("span", { class: "chip zielen" }, ikona("ok"), "odpowiedziane")),
            el("h2", { class: "decyzja-tytul" }, p.tytul || ""),
            p.tresc_md ? html(p.tresc_md) : null,
            p.odpowiedz_md ? el("div", { class: "odpowiedz" }, el("span", { class: "etykieta" }, "Odpowiedź"), html(p.odpowiedz_md)) : null,
            dolna);
        }));
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
      podtytul.textContent = mozeZapisywac()
        ? "Na żywo z sejfu Obsidiana (B&C/Produkcja). Odpowiedzi, zadania i decyzje z panelu zapisują się w tych samych plikach."
        : "Na żywo z sejfu Obsidiana (B&C/Produkcja).";
      if (blad) {
        tresc.replaceChildren(stanBledu(blad, "Plan z sejfu"));
        return;
      }
      if (!dane) return;
      odlozone = false;
      wersjeWidoczne = Object.assign({}, dane.wersje || {});
      const czeka = (dane.pytania || []).filter((p) => p.otwarte).length;
      segment.licznik("pytania", czeka || null);
      const doDecyzji = (dane.decyzje || []).filter((d) => d.status === "do_decyzji").length;
      segment.licznik("decyzje", doDecyzji || null);
      const przewiniecie = window.scrollY;
      let w;
      try {
        w = { harmonogram, zadania, decyzje, pytania, dziennik }[zakladka]();
      } catch (e) {
        console.warn("plan: rysowanie", e);
        w = pusty("Nie udało się pokazać tej części", e.message, "ostrzezenie");
      }
      tresc.replaceChildren(w);
      if (Math.abs(window.scrollY - przewiniecie) > 2) window.scrollTo(0, przewiniecie);   // zapis nie skacze na górę
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
        if (zmiana || wymus) {
          if (!wymus && piszeTeraz()) odlozone = true;         // nie wyrywaj nikomu pola spod palców
          else rysuj();
        }
      } catch (e) {
        blad = e;
        dane = null;
        rysuj();
      } finally {
        odswiezBtn.disabled = false;
      }
    }

    // Telefon: zablokowanie ekranu albo przejście do innej aplikacji wstrzymuje zegar 5 s, a karta bywa potem
    // wyrzucona z pamięci — oczekujące odhaczenia idą od razu, z keepalive (żądanie przeżyje zamknięcie karty).
    window.addEventListener("pagehide", () => wyslijWszystkieOczekujace(true));
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") wyslijWszystkieOczekujace(true);
    });

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
        wyslijWszystkieOczekujace();                           // odhaczenie nie ginie przy przejściu do innego widoku
        if (stop) stop();
        stop = null;
      },
    };
  },
};
