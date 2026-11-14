// Lista „Do odpowiedzi” — jeden komponent dla zakładki Pytania (pełne karty) i zakładki Sesja (karty zwarte).
//
//   const lista = listaPytan(ctx, { zwarta?, prefiks?, naDane?(dane), pokazSprawe?(klucz) });
//   lista.el                       — sekcja z nagłówkiem, licznikiem, listą i grupą „Odłożone na sesję główną”
//   lista.pokaz() / lista.ukryj()  — start i stop cichego odświeżania (co 15 s i po powrocie do karty)
//   lista.odswiez(wymus)           — pobranie planu, raportów i agendy
//   lista.karta(sprawa)            — karta tej samej postaci (np. do historii „Odpowiedziane”)
//   lista.uzgodnij(kontener, sprawy, mapa, pustyEl) — karty w kontenerze bez przerysowania tych, w których ktoś pisze
//   lista.ustawFiltr(tekst) → liczba pasujących; lista.idzDo(klucz) → czy karta jest na liście
//   lista.zapiszDoSejfu(trasa, cialo, wersja, opcje) / lista.ustawPlan(plan) / lista.dane()
//
// Każda pozycja to pytanie do człowieka (wspolne/kolejka.js: zbudujPytania): pytanie otwarte z polem odpowiedzi
// (z decyzjami z wiersza „Rozstrzyga:” i przyciskami Tak / Nie w tej samej karcie), decyzja „Czy zatwierdzamy: …?”
// z Tak / Nie (z uzasadnieniem) i „Na sesję główną”, raport „Czy akceptujesz: …?” z Akceptuję / Do poprawy,
// decyzja drugiej osoby czekająca na moje potwierdzenie (D-043) „Karol zatwierdził: … — zgadzasz się?” z Zgoda /
// Brak zgody (z powodem) / Przedyskutuj (POST /api/sejf/decyzje/<id>/potwierdzenie). Decyzje w historii mają
// dyskretny znacznik podpisów: „czeka na potwierdzenie: Imię” albo „dwa podpisy: …”.
//
// Wygląd karty: lekka (spokojne tło, bez kolorowego paska z lewej), wyraźny tytuł, mała szara etykieta pochodzenia
// i statusu, krótka treść — punkty z góry pytania albo dwa pierwsze zdania opisu decyzji (kolejka.js: podzielPytanie,
// skrotOpisu); reszta („Szczegóły:”, „Dopisek …”, „Sprostowanie …”, dalszy opis, meta decyzji) jest zwinięta za
// „Pokaż szczegóły”. Wiersz „Rozstrzyga:” nie jest pokazywany jako tekst (decyzje są w karcie osobno).
//
// Zapis do sejfu (bc/zapis.py): każdy zapis wysyła znacznik wersji pliku z chwili, gdy człowiek go zobaczył (karta
// pamięta wersje z chwili narysowania, okno decyzji — z chwili otwarcia); przy cudzej zmianie serwer odmawia (409),
// a lista odświeża dane. Zatwierdzenie decyzji, które zamyka ostatnią decyzję pytania, serwer od razu zapisuje też
// jako odpowiedź pod pytaniem (`rozstrzygniete` w odpowiedzi trasy) — karta pytania znika.
// Samo się odświeża: po każdej akcji i w tle — ale karta, w której ktoś pisze albo ma niewysłany tekst, nie jest
// przerysowywana; dostaje dyskretną informację, że sprawa się zmieniła. W lustrze tylko do odczytu przycisków zapisu nie ma.

import { el, dopisz, ikona, czasTemu, dataKrotka, stanBledu, ladowanie, toast, arkusz, skroc } from "./ui.js";
import { md } from "./markdown.js";
import { komentarze } from "./komentarze.js";
import { kartyRaportow } from "./raport_karta.js";
import {
  zbudujPytania, numerDecyzji, OTWARTE_DECYZJE, pytaniaZamknieteDecyzjami, pasuje, zwykly,
  pytanieDecyzji, kanoniczne, podzielPytanie, skrotOpisu,
} from "./kolejka.js";

const ARKUSZ_STYLOW = new URL("./lista_pytan.css", import.meta.url).href;
const ODSWIEZANIE_MS = 15000;

export const STATUSY_DECYZJI = {
  zatwierdzona: { tekst: "zatwierdzona", kolor: "zielen" },
  do_decyzji: { tekst: "do decyzji", kolor: "zloto" },
  propozycja: { tekst: "propozycja", kolor: "fiolet" },
  odrzucona: { tekst: "odrzucona", kolor: "czerwien" },
  zastapiona: { tekst: "zastąpiona", kolor: "szary" },
};

const html = (tekst) => el("div", { class: "md", html: md(tekst || "") });

function dzisiaj() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

/** „dziś” / „13 lis” dla samej daty. */
export function kiedy(t) {
  if (!t) return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(t)) return t === dzisiaj() ? "dziś" : dataKrotka(t);
  return czasTemu(t);
}

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

/** Czy w elemencie ktoś pisze (kursor w polu) albo zostawił niewysłany tekst — takiego nie przerysowujemy. */
export function zajety(w) {
  if (!w) return false;
  const a = document.activeElement;
  if (a && w.contains(a) && /^(TEXTAREA|INPUT|SELECT)$/.test(a.tagName) && !a.classList.contains("bez-blokady")) return true;
  return [...w.querySelectorAll("textarea, input:not([type]):not(.bez-blokady), input[type=text]:not(.bez-blokady)")].some((p) => p.value && p.value.trim());
}

export function podswietl(k) {
  if (!k) return;
  requestAnimationFrame(() => {
    k.scrollIntoView({ block: "center", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    k.classList.remove("podswietlony");
    void k.offsetWidth;
    k.classList.add("podswietlony");
    setTimeout(() => k.classList.remove("podswietlony"), 2600);
  });
}

/** Lista elementów w kontenerze w podanej kolejności, bez wyjmowania z drzewa tych, które już stoją na miejscu,
 * a elementu z kursorem — nigdy (przeniesienie węzła zabiera polu kursor): pozostałe układają się wokół niego. */
function ustawDzieci(kontener, lista) {
  const zbior = new Set(lista);
  for (const c of [...kontener.children]) if (!zbior.has(c)) c.remove();
  const a = document.activeElement;
  const p = a && a !== document.body ? lista.findIndex((e) => e.parentNode === kontener && e.contains(a)) : -1;
  const doIndeksu = p < 0 ? lista.length : p;
  for (let i = 0; i < doIndeksu; i++) {
    const tu = kontener.children[i];
    if (tu !== lista[i]) kontener.insertBefore(lista[i], tu || null);
  }
  if (p < 0) return;
  let po = lista[p];                                           // ten element zostaje, gdzie jest; reszta za nim
  for (let i = p + 1; i < lista.length; i++) {
    if (po.nextSibling !== lista[i]) kontener.insertBefore(lista[i], po.nextSibling);
    po = lista[i];
  }
}

export function listaPytan(ctx, opcje = {}) {
  dolaczCss(ARKUSZ_STYLOW);
  const zwarta = !!opcje.zwarta;
  const prefiks = opcje.prefiks || "sprawa-";

  let plan = null;
  let bladPlanu = null;
  let raporty = null;
  let bladRaportow = null;
  let agenda = null;
  let agendaDostepna = true;          // trasa /api/sesje/agenda (starszy serwer bez zakładki Sesja = 404)
  let sprawy = { czekajace: [], odlozone: [], odpowiedziane: [] };
  let gdzieDecyzja = new Map();       // numer decyzji -> klucz karty, w której jest (pytanie albo decyzja)
  let podpisDanych = "";
  let pierwszeDane = false;
  let kolejkaOdlozona = false;
  let ostatniBladZapisu = null;
  let zapytanie = "";
  const szkice = new Map();           // nr pytania -> niewysłany tekst odpowiedzi
  const otwarteKomentarze = new Set();
  const otwarteSzczegoly = new Set();
  const kartyKolejki = new Map();     // klucz sprawy -> {el, podpis}
  const kartyOdlozonych = new Map();
  let odlozoneOtwarte = false;

  const mozeZapisywac = () => !ctx.statyczny && ctx.ja.zapis_sejfu !== false;
  // decydent = klucz zatwierdzania albo osoba przy komputerze; stary serwer nie zna tego pola → game_director
  const decydent = () => mozeZapisywac() && !!("decydent" in ctx.ja ? ctx.ja.decydent : ctx.ja.game_director);
  const naSesjeMozna = () => !zwarta && mozeZapisywac() && agendaDostepna && ctx.jest("sesje");
  const plikPytan = () => (plan && plan.pliki && plan.pliki.pytania) || "B&C/Produkcja/Pytania otwarte.md";
  const plikRejestru = () => (plan && plan.pliki && plan.pliki.decyzje) || "B&C/Produkcja/Rejestr decyzji.md";

  const raportyUI = kartyRaportow(ctx, {
    naZmiane: (nowy) => {
      if (raporty) {
        const i = raporty.findIndex((x) => x.id === nowy.id);
        if (i >= 0) raporty[i] = nowy;
      }
      podpisDanych = "";
      przerysuj();
      pobierz(true);                                           // komentarze, liczniki i decyzje innych osób
    },
    // „Zmień decyzję” w karcie na liście albo w historii: nowa karta przez kartaSprawy (id, klasy, wpis w mapie),
    // a stan „zmienia decyzję” jest w podpisie karty, więc ciche odświeżenie go nie cofa
    naZmianeDecyzji: (r, stara) => {
      const s = stara && stara._sprawa;
      if (!s || s.typ !== "raport" || !stara.isConnected) return false;
      const e = nowaKarta(s, stara._mapa);
      stara.replaceWith(e);
      filtruj();
      return true;
    },
  });

  // ------------------------------------------------------------------ szkielet
  const licznikEl = el("span", { class: "kolejka-licznik zero", "aria-live": "polite" }, "0");
  const infoEl = el("div", { class: "kolejka-info", role: "status", hidden: true });
  const listaEl = el("div", { class: "kolumna kolejka-lista" }, ladowanie("Zbieram pytania…"));
  const brakWynikow = el("p", { class: "cichy-tekst kolejka-brak-wynikow", hidden: true }, "Tu nic nie pasuje do szukanego słowa.");
  const odlozoneEl = el("div", { class: "kolejka-odlozone" });
  const tytulId = prefiks + "lista-tytul";
  // w Sesji nagłówek listy jest tytułem karty (jak Agenda obok)
  const naglowek = zwarta
    ? el("h2", { class: "karta-tytul", id: tytulId }, ikona(opcje.ikona || "pytanie"), el("span", null, opcje.tytul || "Pytania"),
      el("div", { class: "karta-akcje" }, licznikEl, opcje.akcjeNaglowka || null))
    : el("div", { class: "kolejka-nagl" },
      el("h2", { id: tytulId }, opcje.tytul || "Do odpowiedzi"), licznikEl,
      el("span", { class: "rozpychacz" }), opcje.akcjeNaglowka || null);
  const korzen = el("section", { class: "kolejka lista-pytan" + (zwarta ? " zwarta" : ""), "aria-labelledby": tytulId },
    opcje.naglowek === false ? null : naglowek,
    opcje.opis ? el("p", { class: "cichy-tekst lista-pytan-opis" }, opcje.opis) : null,
    infoEl, listaEl, brakWynikow, odlozoneEl);

  // Odłożone przerysowanie wraca, gdy nikt już nie pisze: po wyjściu z pola albo chwilę po wyczyszczeniu tekstu.
  let zegarPisania = null;
  const sprawdzOdlozone = (ms) => {
    clearTimeout(zegarPisania);
    zegarPisania = setTimeout(() => {
      if (kolejkaOdlozona) rysuj();                            // karty, w których ktoś dalej pisze, i tak zostaną
      if (typeof opcje.poPisaniu === "function") opcje.poPisaniu();
    }, ms);
  };
  for (const w of [listaEl, odlozoneEl]) {
    w.addEventListener("focusout", () => sprawdzOdlozone(250));
    w.addEventListener("input", (e) => {
      if (e.target && !String(e.target.value || "").trim()) sprawdzOdlozone(1500);
    });
  }

  function pokazInfo(tekst) {
    infoEl.replaceChildren(ikona("ok"), el("span", null, tekst),
      el("button", { type: "button", class: "przycisk cichy maly ikonowy", "aria-label": "Zamknij", onclick: () => { infoEl.hidden = true; } }, ikona("zamknij")));
    infoEl.hidden = false;
    clearTimeout(pokazInfo.zegar);
    pokazInfo.zegar = setTimeout(() => { infoEl.hidden = true; }, 15000);
  }

  // ------------------------------------------------------------------ zapis do sejfu (wspólne)
  /**
   * POST z wersją pliku, którą człowiek widział. Zwraca odpowiedź albo null (błąd już pokazany toastem).
   * opcje.konflikt — własny komunikat przy 409 „ktoś zmienił plik”; opcje.przedRysowaniem — po udanym zapisie,
   * zanim widok się przerysuje (np. wyczyszczenie pola, żeby karta nie uchodziła za „w trakcie pisania”).
   */
  async function zapiszDoSejfu(trasa, cialo, wersja, o = {}) {
    ostatniBladZapisu = null;
    try {
      const w = await ctx.api(trasa, { metoda: "POST", cialo: Object.assign({}, cialo, { wersja: wersja || "" }) });
      if (typeof o.przedRysowaniem === "function") o.przedRysowaniem(w);
      if (w && w.plan) {
        plan = w.plan;
        bladPlanu = null;
      }
      podpisDanych = "";
      przerysuj();
      if (w && w.uwaga) toast(w.uwaga, "info", { czas: 6500 });
      return w;
    } catch (e) {
      ostatniBladZapisu = e;
      if (e.status === 409 && e.dane && e.dane.kod === "konflikt_wersji") {
        toast(o.konflikt || "Ktoś zmienił ten plik — odświeżam", "info", { czas: 6500 });
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
    const p = ((plan && plan.pytania) || []).find((x) => x.nr === nr);
    const plaski = String(tekst).replace(/[ \t]*[\r\n]+\s*/g, " / ").replace(/\s{2,}/g, " ").trim();
    return !!(p && plaski && String(p.odpowiedz_md || "").includes(plaski));
  }

  /** Jak serwer podpisze odpowiedź (bc/zapis.py: znacznik zależy od klucza, nie od imienia). */
  function podpisOdpowiedzi() {
    const nowy = "decydent" in ctx.ja;                         // stary serwer pisze jeszcze znacznik „Game Director”
    const kto = (ctx.ja.kto || "").trim() || (ctx.ja.game_director && !nowy ? "Game Director" : "gość");
    if (ctx.ja.game_director) return kto + " (" + (nowy ? "klucz zatwierdzania" : "Game Director") + ", " + dzisiaj() + ")";
    if (ctx.ja.lokalny) return kto + " (" + dzisiaj() + ")";
    return kto + " (gość panelu, " + dzisiaj() + ")";
  }

  function omowZAgentem(nr, tytul) {
    return el("button", {
      type: "button", class: "przycisk maly cichy",
      onclick: () => ctx.idz("agent", {
        kontekst: [{ typ: "notatka", cel: plikPytan(), etykieta: "Pytanie #" + nr }],
        tekst: "Pomóż mi odpowiedzieć na pytanie #" + nr + ": " + (tytul || ""),
      }),
    }, ikona("agent"), el("span", null, "Omów z agentem"));
  }

  /**
   * Pole odpowiedzi na pytanie. `wersja()` = znacznik pliku pytań, który widzi człowiek (z chwili narysowania karty).
   * `otwarteDecyzje` = decyzje z wiersza „Rozstrzyga:”, które jeszcze czekają — podpowiedź, żeby zdecydować o nich
   * przyciskami w tej samej karcie (odpowiedź tekstem ich nie zmienia).
   */
  function formularzOdpowiedzi(p, nr, wersja, o = {}) {
    const pole = el("textarea", { class: "pole", rows: zwarta ? 1 : 2, maxlength: "2000", placeholder: o.dopisek ? "Dopisz odpowiedź…" : "Twoja odpowiedź…", "aria-label": "Twoja odpowiedź na pytanie #" + nr });
    pole.value = szkice.get(nr) || "";
    pole.addEventListener("input", () => {
      if (pole.value) szkice.set(nr, pole.value);
      else szkice.delete(nr);
    });
    const wyslij = el("button", { type: "submit", class: "przycisk glowny maly" }, ikona("wyslij"), el("span", null, "Odpowiedz"));
    const otwarte = o.otwarteDecyzje || [];
    const podpowiedz = otwarte.length && !zwarta ? el("p", { class: "cichy-tekst sprawa-podpowiedz" }, ikona("info"),
      el("span", null, "Odpowiedź tekstem nie zmienia decyzji " + otwarte.map((d) => d.id).join(", ") + ". " +
        (decydent() ? "Odpowiedz na nie przyciskami Tak / Nie wyżej — pytanie samo się wtedy zamknie." : "Zatwierdza je Karol albo Paweł."))) : null;
    const form = el("form", { class: "odpowiedz-formularz" },
      zwarta ? null : el("label", { class: "etykieta" }, o.dopisek ? "Dopisz odpowiedź" : "Twoja odpowiedź"), pole,
      zwarta ? null : el("p", { class: "cichy-tekst podpis-odpowiedzi" }, "Podpis w sejfie: " + podpisOdpowiedzi()),
      podpowiedz,
      el("div", { class: "rzad-przyciskow" }, o.przyciski || null, el("span", { class: "rozpychacz" }), wyslij));
    pole.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        form.requestSubmit ? form.requestSubmit() : wyslij.click();
      }
    });
    let wToku = false;                                         // Ctrl+Enter dwa razy = jedno żądanie
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
      szkice.delete(nr);                                       // po udanym zapisie pole ma być puste po przerysowaniu
      try {
        const w = await zapiszDoSejfu("/api/sejf/pytania/" + encodeURIComponent(nr) + "/odpowiedz", { tekst }, wersja(), {
          przedRysowaniem: () => {
            pole.value = "";
            pole.blur();
          },
        });
        if (w) {
          toast("Zapisano odpowiedź na pytanie #" + nr + " w sejfie." +
            (otwarte.length ? " Decyzje " + otwarte.map((d) => d.id).join(", ") + " czekają dalej." : ""), "ok", { czas: otwarte.length ? 7000 : 3500 });
        } else if (odpowiedzJuzJest(nr, tekst) || (ostatniBladZapisu && ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod === "juz_zapisane")) {
          pole.value = "";                                     // ta odpowiedź już jest w sejfie — nie przywracaj szkicu
          przerysuj();
        } else {
          szkice.set(nr, tekst);
          if (pole.isConnected) wyslij.disabled = false;
          else przerysuj();
        }
      } finally {
        wToku = false;
      }
    });
    return form;
  }

  // ------------------------------------------------------------------ decyzje: okno Tak / Nie
  function oknoDecyzji(d, status, wersjaPrzeczytana) {
    const zatw = status === "zatwierdzona";
    // Wersja Rejestru z chwili otwarcia okna = treść, którą decydujący właśnie przeczytał (na karcie i w oknie).
    // Odświeżenie w tle może w tym czasie przerysować listę za oknem — wysłanie nowszej wersji zatwierdziłoby
    // treść, której nikt nie widział. Dlatego idzie wersja zapamiętana przy otwarciu.
    let zUstawien = "";
    try {
      zUstawien = localStorage.getItem("bc.kto") || "";
    } catch (e) { /* bez pamięci przeglądarki imienia nie ma */ }
    const imie = ("decydent" in ctx.ja ? zUstawien : ctx.ja.kto || "").trim();
    const bezImienia = !imie || imie.toLowerCase() === "gość" || imie.toLowerCase() === "gosc";
    const kto = "decydent" in ctx.ja
      ? (bezImienia ? "(wpisz imię w Ustawieniach)" : imie)
      : (!bezImienia && imie !== "Game Director" ? "Game Director (" + imie + ")" : "Game Director");
    const pole = el("textarea", { class: "pole", rows: 3, maxlength: "1000", placeholder: zatw ? "Dlaczego tak (opcjonalnie)" : "Dlaczego nie (opcjonalnie)", "aria-label": "Uzasadnienie" });
    const przycisk = el("button", { type: "submit", class: "przycisk " + (zatw ? "sukces" : "grozny") },
      ikona(zatw ? "ok" : "krzyzyk"), el("span", null, (zatw ? "Tak — zatwierdzam " : "Nie — odrzucam ") + d.id));
    const anuluj = el("button", { type: "button", class: "przycisk cichy" }, "Anuluj");
    const form = el("form", { class: "formularz" },
      el("p", null, el("strong", null, d.id + " "), d.tytul || ""),
      d.opis_md ? el("div", { class: "decyzja-podglad" }, html(d.opis_md)) : null,
      el("div", { class: "podpowiedz" }, ikona("info"), el("div", null,
        el("strong", null, "To zmiana kanonu"),
        el("p", null, "W Rejestrze decyzji wiersz statusu zmieni się na „" + (zatw ? "✅ zatwierdzona" : "❌ odrzucona") +
          " · … · zdecydował: " + kto + " " + dzisiaj() + "”, a ślad trafi do Dziennika zmian. Cofnąć można tylko ręcznie w Obsidianie." +
          ("decydent" in ctx.ja && bezImienia ? " Decyzja musi mieć podpis — bez imienia panel jej nie zapisze." : "")),
        el("p", { class: "cichy-tekst" }, "Druga osoba dostanie pytanie o zgodę (w panelu i na Telegramie). Do jej odpowiedzi to robocze ustalenie."),
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
          { status, uzasadnienie: pole.value.trim() }, wersjaPrzeczytana,
          { konflikt: "Rejestr decyzji zmienił się, odkąd otworzyłeś to okno — nic nie zapisano. Przeczytaj " + d.id + " jeszcze raz." });
        if (w) {
          ark.zamknij();
          poDecyzji(d, zatw, w);
        } else if (ostatniBladZapisu && ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod === "konflikt_wersji") {
          ark.zamknij();                                       // stara treść w oknie nie może zostać zatwierdzona
        } else {
          przycisk.disabled = false;
        }
      } finally {
        wToku = false;
      }
    });
  }

  function poDecyzji(d, zatw, w) {
    const tekst = d.id + (zatw ? " zatwierdzona." : " odrzucona.");
    const roz = w && w.rozstrzygniete;
    if (Array.isArray(roz) && roz.length) {
      const nry = roz.map((r) => "#" + r.nr).join(", ");
      const opis = (roz.length === 1 ? "Pytanie " : "Pytania ") + nry + " — rozstrzygnięte decyzjami, odpowiedź dopisana w sejfie.";
      pokazInfo(opis);
      toast(tekst + " " + opis, "ok", { czas: 7000 });
      return;
    }
    if (!Array.isArray(roz)) {                                 // serwer sprzed samo-rozstrzygania
      const zostaly = pytaniaZamknieteDecyzjami(w && w.plan, numerDecyzji(d.id));
      if (zostaly.length) {
        toast(tekst + " Pytanie " + zostaly.map((p) => "#" + p.nr).join(", ") + " ma już wszystkie decyzje zamknięte — " +
          "dopisz krótką odpowiedź. Samo zamykanie pytań ruszy po restarcie panelu.", "info", { czas: 10000 });
        return;
      }
    }
    toast(tekst, "ok");
  }

  /** Tak / Nie przy decyzji czekającej na zatwierdzenie (albo informacja, kto zatwierdza). */
  function przyciskiDecyzji(d, wersja, dodatkowe) {
    if (!mozeZapisywac() || !OTWARTE_DECYZJE.includes(d.status)) return dodatkowe && dodatkowe.some(Boolean) ? el("div", { class: "rzad-przyciskow" }, dodatkowe) : null;
    if (!decydent()) {
      return el("div", { class: "kolumna-mala" },
        el("p", { class: "decyzja-gd cichy-tekst" }, ikona("klodka"), "Zatwierdza Karol albo Paweł (klucz zatwierdzania) — możesz zostawić komentarz."),
        dodatkowe && dodatkowe.some(Boolean) ? el("div", { class: "rzad-przyciskow" }, dodatkowe) : null);
    }
    const male = zwarta ? " maly" : "";
    return el("div", { class: "rzad-przyciskow decyzja-akcje", dataset: { decyzja: d.id } },
      el("button", { type: "button", class: "przycisk sukces" + male, title: "Zatwierdź " + d.id, onclick: () => oknoDecyzji(d, "zatwierdzona", wersja()) }, ikona("ok"), el("span", null, "Tak")),
      el("button", { type: "button", class: "przycisk grozny" + male, title: "Odrzuć " + d.id, onclick: () => oknoDecyzji(d, "odrzucona", wersja()) }, ikona("krzyzyk"), el("span", null, "Nie")),
      dodatkowe || null);
  }

  // ------------------------------------------------------------------ potwierdzenie decyzji drugiej osoby (D-043)
  const ODPOWIEDZI = {
    zgoda: { tytul: "Zgoda", przycisk: "Zgoda — potwierdzam", klasa: "sukces", ikona: "ok", pole: null,
      opis: (d) => "Do wiersza statusu dojdzie „potwierdził: " + imieZUstawien() + " " + dzisiaj() + "” — " + d.id + " będzie mieć dwa podpisy i zacznie obowiązywać." },
    sprzeciw: { tytul: "Brak zgody", przycisk: "Nie zgadzam się", klasa: "grozny", ikona: "krzyzyk", pole: "Dlaczego nie (opcjonalnie, krótko)",
      opis: (d) => d.id + " wróci na „do decyzji”, a w Rejestrze zostanie ślad „sprzeciw: " + imieZUstawien() + " " + dzisiaj() + "”. Sprawa wróci na listę „Do odpowiedzi”." },
    rozmowa: { tytul: "Przedyskutujmy", przycisk: "Na sesję główną", klasa: "glowny", ikona: "kalendarz", pole: "Dopisek do tematu (opcjonalnie)",
      opis: (d) => d.id + " wróci na „do decyzji” ze śladem „do rozmowy”, a temat trafi na agendę sesji głównej." },
  };

  function imieZUstawien() {
    let t = "";
    try {
      t = localStorage.getItem("bc.kto") || "";
    } catch (e) { /* bez pamięci przeglądarki imienia nie ma */ }
    t = t.trim();
    return !t || /^go[sś][cć]$/i.test(t) ? "" : t;
  }

  function oknoPotwierdzenia(d, odpowiedz, wersjaPrzeczytana) {
    const o = ODPOWIEDZI[odpowiedz];
    const imie = imieZUstawien();
    const pole = o.pole ? el("textarea", { class: "pole", rows: 3, maxlength: "1000", placeholder: o.pole, "aria-label": o.pole }) : null;
    const przycisk = el("button", { type: "submit", class: "przycisk " + o.klasa }, ikona(o.ikona), el("span", null, o.przycisk));
    const anuluj = el("button", { type: "button", class: "przycisk cichy" }, "Anuluj");
    const zd = d.zdecydowal || {};
    const form = el("form", { class: "formularz" },
      el("p", null, el("strong", null, d.id + " "), d.tytul || ""),
      el("p", { class: "cichy-tekst" }, (zd.kto || "Ktoś") + (d.status === "odrzucona" ? " odrzucił" : " zatwierdził") + (zd.data ? " " + zd.data : "") + "."),
      d.opis_md ? el("div", { class: "decyzja-podglad" }, html(d.opis_md)) : null,
      el("div", { class: "podpowiedz" }, ikona("info"), el("div", null,
        el("p", null, o.opis(d)),
        imie ? null : el("p", null, el("strong", null, "Wpisz swoje imię w Ustawieniach — odpowiedź musi mieć podpis.")))),
      pole ? el("label", { class: "etykieta" }, o.pole) : null, pole,
      el("div", { class: "rzad-przyciskow decyzja-potwierdz" }, anuluj, el("span", { class: "rozpychacz" }), przycisk));
    const ark = arkusz({ tytul: o.tytul + ": " + d.id, tresc: form });
    anuluj.addEventListener("click", () => ark.zamknij());
    let wToku = false;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (wToku) return;
      wToku = true;
      przycisk.disabled = true;
      try {
        const cialo = { odpowiedz };
        if (pole && pole.value.trim()) cialo.uzasadnienie = pole.value.trim();
        const w = await zapiszDoSejfu("/api/sejf/decyzje/" + encodeURIComponent(d.id) + "/potwierdzenie", cialo, wersjaPrzeczytana,
          { konflikt: "Rejestr decyzji zmienił się, odkąd otworzyłeś to okno — nic nie zapisano. Przeczytaj " + d.id + " jeszcze raz." });
        const kod = ostatniBladZapisu && ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod;
        if (w) {
          ark.zamknij();
          toast(odpowiedz === "zgoda" ? d.id + " ma dwa podpisy." : odpowiedz === "sprzeciw" ? d.id + " wraca „do decyzji”." :
            d.id + " czeka na sesję główną.", "ok", odpowiedz === "rozmowa" ? { akcja: { tekst: "Sesja", fn: () => ctx.idz("sesja") } } : undefined);
          if (odpowiedz === "rozmowa") pobierz(true);           // agenda: sprawa przechodzi do „Odłożone”
        } else if (kod === "konflikt_wersji" || kod === "nic_nie_czeka") {
          ark.zamknij();
          if (kod === "nic_nie_czeka") pobierz(true);
        } else if (ostatniBladZapisu && ostatniBladZapisu.status === 404 && !(ostatniBladZapisu.dane && ostatniBladZapisu.dane.kod)) {
          ark.zamknij();                                       // stary serwer bez tej trasy
          toast("Potwierdzanie zacznie działać po restarcie panelu.", "info", { czas: 7000 });
        } else {
          przycisk.disabled = false;
        }
      } finally {
        wToku = false;
      }
    });
  }

  /** Zgoda / Brak zgody / Przedyskutuj — dla decydenta; reszta widzi, gdzie potwierdzić. */
  function przyciskiPotwierdzenia(d, wersja) {
    if (!mozeZapisywac()) return el("p", { class: "decyzja-gd cichy-tekst" }, ikona("klodka"), "Potwierdzisz w panelu na komputerze albo przyciskiem na Telegramie.");
    if (!decydent()) {
      return el("p", { class: "decyzja-gd cichy-tekst" }, ikona("klodka"),
        "Potwierdzasz przy komputerze z panelem, z kluczem zatwierdzania albo przyciskiem na Telegramie.");
    }
    const male = zwarta ? " maly" : "";
    return el("div", { class: "rzad-przyciskow decyzja-akcje potwierdzenie-akcje", dataset: { decyzja: d.id } },
      el("button", { type: "button", class: "przycisk sukces" + male, dataset: { odpowiedz: "zgoda" }, onclick: () => oknoPotwierdzenia(d, "zgoda", wersja()) }, ikona("ok"), el("span", null, "Zgoda")),
      el("button", { type: "button", class: "przycisk grozny" + male, dataset: { odpowiedz: "sprzeciw" }, onclick: () => oknoPotwierdzenia(d, "sprzeciw", wersja()) }, ikona("krzyzyk"), el("span", null, "Brak zgody")),
      el("button", { type: "button", class: "przycisk cichy" + male, dataset: { odpowiedz: "rozmowa" }, onclick: () => oknoPotwierdzenia(d, "rozmowa", wersja()) }, ikona("komentarz"), el("span", null, "Przedyskutuj")));
  }

  /** Dyskretny znacznik podpisów decyzji (D-043). */
  function znacznikPodpisow(d) {
    if (!d) return null;
    const p = (x) => (x && x.kto ? x.kto + (x.data ? " " + kiedy(x.data) : "") : "?");
    if (d.zdecydowal && d.potwierdzil) {
      return el("p", { class: "cichy-tekst decyzja-podpisy dwa" }, ikona("ok"), el("span", null, "Dwa podpisy: " + p(d.zdecydowal) + " i " + p(d.potwierdzil)));
    }
    if (d.czeka_na) {
      const moja = kanoniczne(ctx.ja.kto) && kanoniczne(ctx.ja.kto) === kanoniczne(d.zdecydowal && d.zdecydowal.kto);
      return el("p", { class: "cichy-tekst decyzja-podpisy czeka" }, ikona("zegar"),
        el("span", null, "Czeka na potwierdzenie: " + d.czeka_na + (moja ? " (Twoja decyzja — robocze ustalenie)" : " · podpis: " + p(d.zdecydowal))));
    }
    const slad = d.sprzeciw ? ["Brak zgody", d.sprzeciw] : d.do_rozmowy ? ["Do rozmowy", d.do_rozmowy] : null;
    if (slad) {
      const w = slad[1].wobec;
      return el("p", { class: "cichy-tekst decyzja-podpisy slad" }, ikona("info"),
        el("span", null, slad[0] + ": " + p(slad[1]) + (w ? " (wobec: " + (w.status || "") + " przez " + p(w) + ")" : "")));
    }
    return null;
  }

  function komentarzeCelu(klucz, cel, tekst) {
    const miejsce = el("div", { class: "decyzja-watek" });
    const det = el("details", { class: "zwijane decyzja-komentarze", open: otwarteKomentarze.has(klucz) },
      el("summary", null, ikona("dol"), ikona("komentarz"), tekst || "Komentarze"), miejsce);
    const zamontuj = () => {
      if (!miejsce.firstChild) miejsce.appendChild(komentarze(ctx, cel));
    };
    det.addEventListener("toggle", () => {
      if (det.open) {
        otwarteKomentarze.add(klucz);
        zamontuj();
      } else otwarteKomentarze.delete(klucz);
    });
    if (det.open) zamontuj();
    return det;
  }

  const komentarzeDecyzji = (d) => komentarzeCelu("d:" + d.id, { typ: "notatka", cel: plikRejestru() + "#" + d.id, etykieta: d.id + " " + (d.tytul || "") });
  const komentarzePytania = (p) => komentarzeCelu("p:" + p.nr, { typ: "notatka", cel: plikPytan() + "#pytanie-" + p.nr, etykieta: "Pytanie #" + p.nr });

  /** Mała szara etykieta w górnym wierszu karty (status, „czeka na Ciebie”) — zamiast kolorowych znaczków. */
  const etykieta = (tekst, klasa) => el("span", { class: "sprawa-meta" + (klasa ? " " + klasa : "") }, tekst);

  function chipDecyzji(d) {
    const s = d ? STATUSY_DECYZJI[d.status] || { tekst: d.status || "?" } : { tekst: "brak w Rejestrze" };
    return etykieta(s.tekst, "status-" + ((d && d.status) || "brak"));
  }

  /** Zwijane „Pokaż szczegóły” (pamięta, które są otwarte). */
  function szczegoly(klucz, ...tresc) {
    if (!tresc.flat().some(Boolean)) return null;
    const otwarte = otwarteSzczegoly.has(klucz);
    const napis = el("span", null, otwarte ? "Ukryj szczegóły" : "Pokaż szczegóły");
    const det = el("details", { class: "zwijane sprawa-szczegoly", open: otwarte },
      el("summary", null, ikona("dol"), napis), el("div", { class: "sprawa-szczegoly-tresc" }, ...tresc));
    det.addEventListener("toggle", () => {
      napis.textContent = det.open ? "Ukryj szczegóły" : "Pokaż szczegóły";
      if (det.open) otwarteSzczegoly.add(klucz);
      else otwarteSzczegoly.delete(klucz);
    });
    return det;
  }

  /** Krótka treść pytania: punkty z góry widoczne, reszta zwinięta (kolejka.js: podzielPytanie). */
  function trescPytania(s) {
    const { krotko, szczegoly: reszta } = podzielPytanie(s.p.tresc_md);
    return [krotko ? el("div", { class: "md sprawa-krotko", html: md(krotko) }) : null,
      reszta ? szczegoly(s.klucz, html(reszta)) : null];
  }

  /** Opis decyzji: dwa pierwsze zdania widoczne, reszta i meta (źródło, kategoria) zwinięte. */
  function opisDecyzji(s, d, ...dodatki) {
    const { krotko, reszta } = skrotOpisu(d.opis_md, 2);
    const meta = (d.meta || []).length ? el("p", { class: "cichy-tekst decyzja-meta" }, (d.meta || []).join(" · ")) : null;
    return [krotko ? el("div", { class: "md sprawa-krotko", html: md(krotko) }) : null,
      szczegoly(s.klucz, reszta ? html(reszta) : null, meta, ...dodatki)];
  }

  // ------------------------------------------------------------------ na sesję główną
  function oknoNaSesje(s) {
    const pole = el("textarea", { class: "pole", rows: 2, maxlength: "500", placeholder: "Np. „przegadać z Pawłem” (opcjonalnie)", "aria-label": "Dopisek" });
    const zapisz = el("button", { type: "submit", class: "przycisk glowny szeroki" }, ikona("kalendarz"), el("span", null, "Odłóż na sesję"));
    const form = el("form", { class: "formularz" },
      el("p", null, el("strong", null, s.zrodlo + ": "), zwykly(s.tytul)),
      el("p", { class: "cichy-tekst" }, "Temat trafi do agendy sesji głównej (zakładka Sesja) i zniknie z listy „Do odpowiedzi” do czasu omówienia."),
      el("label", { class: "etykieta" }, "Dopisek (opcjonalnie)"), pole, zapisz);
    const ark = arkusz({ tytul: "Na sesję główną", tresc: form });
    let wToku = false;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (wToku) return;
      wToku = true;
      zapisz.disabled = true;
      try {
        const cialo = { zrodlo: s.zrodlo, tytul: skroc(zwykly(s.tytul), 180) || s.zrodlo };
        if (pole.value.trim()) cialo.dopisek = pole.value.trim();
        const w = await ctx.api("/api/sesje/agenda/na-sesje", { metoda: "POST", cialo });
        if (w && w.agenda) agenda = w.agenda;
        ark.zamknij();
        podpisDanych = "";
        przerysuj();
        toast("Odłożono na sesję główną: " + s.zrodlo + ".", "ok", { akcja: { tekst: "Sesja", fn: () => ctx.idz("sesja") } });
        if (!w || !w.agenda) pobierz(true);
      } catch (err) {
        if (err.status === 409 && err.dane && err.dane.kod === "juz_zapisane") {
          ark.zamknij();
          toast(err.message || "Ta sprawa już czeka na sesję główną.", "info");
          pobierz(true);
        } else if (err.status === 404 && !(err.dane && err.dane.blad && /sesj/i.test(err.dane.blad))) {
          agendaDostepna = false;
          ark.zamknij();
          toast("Odkładanie na sesję zacznie działać po restarcie panelu.", "info", { czas: 7000 });
          przerysuj();
        } else {
          toast(err.message || "Nie udało się odłożyć na sesję.", "blad");
          zapisz.disabled = false;
        }
      } finally {
        wToku = false;
      }
    });
  }

  function przyciskNaSesje(s) {
    if (!naSesjeMozna() || s.odlozona || s.zamknieta || !s.zrodlo) return null;
    return el("button", { type: "button", class: "przycisk maly cichy", onclick: () => oknoNaSesje(s) }, ikona("kalendarz"), el("span", null, "Na sesję główną"));
  }

  // ------------------------------------------------------------------ karty
  function chipOdlozona() {
    if (zwarta) return etykieta("na agendzie");
    return el("button", { type: "button", class: "sprawa-meta sprawa-meta-klik", onclick: () => ctx.idz("sesja") }, "czeka na sesję");
  }

  function goraKarty(s, ...chipy) {
    return el("div", { class: "sprawa-gora" },
      el("span", { class: "sprawa-zrodlo" }, s.pochodzenie),
      s.dzien && !zwarta ? el("span", { class: "sprawa-kiedy", title: s.dzien }, kiedy(s.dzien)) : null,
      ...chipy, s.odlozona ? chipOdlozona() : null);
  }

  function pokazDecyzje(id) {
    const k = gdzieDecyzja.get(numerDecyzji(id));
    if (!k) {
      toast("Nie ma " + id + " w Rejestrze decyzji.", "info");
      return;
    }
    if (typeof opcje.pokazSprawe === "function") opcje.pokazSprawe(k);
    else idzDo(k);
  }

  function chipyPowiazanych(lista, tytul) {
    return el("div", { class: "sprawa-powiazane" },
      el("span", { class: "etykieta" }, tytul || "Powiązane decyzje"),
      el("div", { class: "chipy" }, lista.map(({ id, d }) => el("button", {
        type: "button", class: "chip klik", title: d ? d.tytul : "brak w Rejestrze", onclick: () => pokazDecyzje(id),
      }, el("strong", null, id), " ", d ? (STATUSY_DECYZJI[d.status] || { tekst: d.status }).tekst : "brak"))));
  }

  /** Decyzje z wiersza „Rozstrzyga:” w karcie pytania: czekające jako pytanie z Tak / Nie, zamknięte ze statusem. */
  function blokDecyzji(s, wersja) {
    return el("div", { class: "sprawa-decyzje" },
      s.decyzje.map(({ id, d }) => {
        if (!d) return el("div", { class: "sprawa-dec status-brak" }, el("span", { class: "decyzja-id" }, id), el("span", { class: "cichy-tekst" }, "Nie ma takiej decyzji w Rejestrze."));
        const otwarta = OTWARTE_DECYZJE.includes(d.status);
        return el("div", { class: "sprawa-dec status-" + (d.status || "brak"), dataset: { decyzja: d.id } },
          el("div", { class: "decyzja-gora" }, el("span", { class: "sprawa-zrodlo" }, "rozstrzyga decyzja " + d.id), chipDecyzji(d)),
          el("strong", { class: "sprawa-dec-tytul" }, otwarta ? pytanieDecyzji(d) : zwykly(d.tytul)),
          d.opis_md ? szczegoly(s.klucz + "~" + d.id, html(d.opis_md)) : null,
          s.zamknieta ? null : przyciskiDecyzji(d, wersja));
      }));
  }

  function kartaPytania(s, k) {
    const p = s.p;
    const nr = p.nr;
    const wersjaPytan = () => (k._wersje && k._wersje.pytania) || "";
    const wersjaRejestru = () => (k._wersje && k._wersje.decyzje) || "";
    k.classList.add("pytanie", s.zamknieta ? "zamkniete" : "otwarte");
    if (s.zamknieta) {                                         // historia: odpowiedź i „Dopisz odpowiedź”
      dopisz(k,
        goraKarty(s, etykieta("odpowiedziane")),
        el("h3", { class: "sprawa-tytul" }, s.pytanie),
        trescPytania(s),
        s.decyzje.length ? blokDecyzji(s, wersjaRejestru) : null,
        s.powiazane.length ? chipyPowiazanych(s.powiazane) : null,
        p.odpowiedz_md ? el("div", { class: "odpowiedz" }, el("span", { class: "etykieta" }, "Odpowiedź"), html(p.odpowiedz_md)) : null,
        mozeZapisywac() ? el("details", { class: "zwijane", open: szkice.has(nr) },
          el("summary", null, ikona("dol"), "Dopisz odpowiedź"), formularzOdpowiedzi(p, nr, wersjaPytan, { dopisek: true })) : null,
        !ctx.statyczny ? komentarzePytania(p) : null);
      return;
    }
    const otwarte = s.decyzje.filter((x) => x.d && OTWARTE_DECYZJE.includes(x.d.status)).map((x) => x.d);
    const dodatkowe = zwarta ? [] : [!ctx.statyczny ? omowZAgentem(nr, p.tytul) : null, przyciskNaSesje(s)];
    const formularz = mozeZapisywac() ? formularzOdpowiedzi(p, nr, wersjaPytan, { otwarteDecyzje: otwarte, przyciski: dodatkowe })
      : (dodatkowe.some(Boolean) ? el("div", { class: "rzad-przyciskow" }, dodatkowe) : null);
    if (zwarta) {
      dopisz(k, goraKarty(s), el("h3", { class: "sprawa-tytul" }, s.pytanie),
        trescPytania(s),
        s.decyzje.length ? blokDecyzji(s, wersjaRejestru) : null,
        formularz);
      return;
    }
    dopisz(k,
      goraKarty(s),
      el("h2", { class: "sprawa-tytul" }, s.pytanie),
      trescPytania(s),
      s.decyzje.length ? blokDecyzji(s, wersjaRejestru) : null,
      s.powiazane.length ? chipyPowiazanych(s.powiazane) : null,
      formularz,
      !ctx.statyczny ? komentarzePytania(p) : null);
  }

  function kartaDecyzji(s, k) {
    const d = s.d;
    const st = STATUSY_DECYZJI[d.status] || { tekst: d.status || "?", kolor: "" };
    const wersjaRejestru = () => (k._wersje && k._wersje.decyzje) || "";
    k.classList.add("decyzja", "status-" + (d.status || "brak"));
    k.dataset.decyzja = d.id;
    const powtorka = s.powtorzona ? el("p", { class: "cichy-tekst sprawa-podpowiedz" }, ikona("ostrzezenie"),
      el("span", null, "W Rejestrze są dwie decyzje " + d.id + " — panel zapisze status dopiero, gdy numery zostaną poprawione w Obsidianie.")) : null;
    if (zwarta) {
      dopisz(k, goraKarty(s, etykieta(st.tekst, "status-" + (d.status || "brak"))),
        el("h3", { class: "sprawa-tytul" }, s.pytanie),
        opisDecyzji(s, d), powtorka, znacznikPodpisow(d),
        przyciskiDecyzji(d, wersjaRejestru));
      return;
    }
    dopisz(k,
      goraKarty(s, etykieta(st.tekst, "status-" + (d.status || "brak")), d.kategoria ? etykieta(d.kategoria) : null),
      el("h2", { class: "sprawa-tytul" }, s.pytanie),
      znacznikPodpisow(d), opisDecyzji(s, d), powtorka,
      przyciskiDecyzji(d, wersjaRejestru, [przyciskNaSesje(s)]),
      !ctx.statyczny ? komentarzeDecyzji(d) : null);
  }

  /** Decyzja drugiej osoby, która czeka na moje potwierdzenie (D-043). */
  function kartaPotwierdzenia(s, k) {
    const d = s.d;
    const st = STATUSY_DECYZJI[d.status] || { tekst: d.status || "?", kolor: "" };
    const wersjaRejestru = () => (k._wersje && k._wersje.decyzje) || "";
    k.classList.add("decyzja", "potwierdzenie", "status-" + (d.status || "brak"));
    k.dataset.decyzja = d.id;
    const chipCzeka = etykieta("czeka na Ciebie", "wazne");
    if (zwarta) {
      dopisz(k, goraKarty(s, etykieta(st.tekst, "status-" + (d.status || "brak")), chipCzeka),
        el("h3", { class: "sprawa-tytul" }, s.pytanie),
        opisDecyzji(s, d),
        przyciskiPotwierdzenia(d, wersjaRejestru));
      return;
    }
    dopisz(k,
      goraKarty(s, etykieta(st.tekst, "status-" + (d.status || "brak")), chipCzeka),
      el("h2", { class: "sprawa-tytul" }, s.pytanie),
      el("p", { class: "cichy-tekst sprawa-podpowiedz" },
        el("span", null, "Z jednym podpisem to robocze ustalenie — obowiązuje po Twojej zgodzie.")),
      opisDecyzji(s, d),
      przyciskiPotwierdzenia(d, wersjaRejestru),
      !ctx.statyczny ? komentarzeDecyzji(d) : null);
  }

  function kartaSprawy(s) {
    if (s.typ === "raport") {
      const k = raportyUI.karta(s.r, { tryb: zwarta ? "zwarta" : "pytanie" });
      k.classList.add("sprawa", "sprawa-raport");
      k.id = prefiks + s.klucz;
      k.dataset.klucz = s.klucz;
      if (s.odlozona) k.querySelector(".sprawa-gora").append(chipOdlozona());
      k._sprawa = s;
      return k;
    }
    const k = el("article", { class: "karta sprawa sprawa-" + s.typ + (s.zamknieta ? " sprawa-zamknieta" : ""), id: prefiks + s.klucz, dataset: { klucz: s.klucz } });
    k._wersje = Object.assign({}, (plan && plan.wersje) || {});
    k._sprawa = s;
    if (s.typ === "pytanie") kartaPytania(s, k);
    else if (s.typ === "potwierdzenie") kartaPotwierdzenia(s, k);
    else kartaDecyzji(s, k);
    return k;
  }

  /** Karta sprawy zapisana w mapie kontenera (karta pamięta swoją mapę: „Zmień decyzję”, „Pokaż nową wersję”). */
  function nowaKarta(s, mapa) {
    const e = kartaSprawy(s);
    e._mapa = mapa || null;
    if (mapa) mapa.set(s.klucz, { el: e, podpis: podpisSprawy(s) });
    return e;
  }

  function podpisSprawy(s) {
    const flagi = [mozeZapisywac(), decydent(), naSesjeMozna(), s.zamknieta, s.odlozona];
    if (s.typ === "raport") return JSON.stringify([s.r, flagi, raportyUI.zmieniaDecyzje(s.r.id)]);
    if (s.typ === "pytanie") return JSON.stringify([s.p, s.decyzje.map((x) => x.d), s.powiazane.map((x) => x.d && x.d.status), flagi]);
    // potwierdzenie i decyzja zależą też od tego, kto patrzy (znacznik „Twoja decyzja”, czyja kolejka)
    return JSON.stringify([s.typ, s.d, s.powtorzona, flagi, kanoniczne(ctx.ja.kto)]);
  }

  function oznaczZmiane(k, tekst, s, mapa) {
    k._nowa = s;
    k._mapa = mapa;
    let b = k.querySelector(":scope > .sprawa-zmiana");
    if (!b) {
      const przycisk = el("button", { type: "button", class: "przycisk cichy maly" });
      b = el("div", { class: "sprawa-zmiana", role: "status" }, ikona("info"), el("span"), przycisk);
      przycisk.addEventListener("click", () => {
        const nowa = k._nowa;
        const m = k._mapa;
        if (nowa) {
          k.replaceWith(nowaKarta(nowa, m));
        } else {
          const nr = /^pytanie-(\d+)$/.exec(k.dataset.klucz || "");
          if (nr) szkice.delete(Number(nr[1]));
          m.delete(k.dataset.klucz);
          k.remove();
          rysuj();
        }
        filtruj();
      });
      k.prepend(b);
    }
    b.querySelector("span").textContent = tekst;
    b.querySelector("button").textContent = s ? "Pokaż nową wersję" : "Zamknij kartę";
  }

  /** Karty spraw w kontenerze: te same zostają (bez przerysowania), zmienione są podmieniane, a karty, w których
   * ktoś pisze, zostają z informacją o zmianie. Zwraca true, gdy któraś karta czeka na koniec pisania. */
  function uzgodnij(kontener, lista, mapa, pustyEl) {
    const wersje = Object.assign({}, (plan && plan.wersje) || {});
    const nowe = [];
    const widziane = new Set();
    const obecne = [...kontener.children];
    // Karta, w której ktoś pisze, zostaje na swoim dotychczasowym miejscu (nawet gdy nowa treść, np. dzisiejsza data,
    // przesuwa ją na liście) — przeskok pola pod palcami myli, a przeniesienie węzła zabiera kursor. Na nowe miejsce
    // trafia, gdy człowiek skończy pisać.
    const naMiejscu = [];
    const zatrzymaj = (k) => {
      const i = obecne.indexOf(k);
      if (i < 0) return false;
      naMiejscu.push({ k, i });
      return true;
    };
    let odlozono = false;
    for (const s of lista) {
      widziane.add(s.klucz);
      const podpis = podpisSprawy(s);
      const stara = mapa.get(s.klucz);
      if (stara && stara.podpis === podpis) {
        stara.el._wersje = wersje;                             // ta sama treść: wersja z tej chwili jest bezpieczna
        stara.el._sprawa = s;
        stara.el._mapa = mapa;
        const b = stara.el.querySelector(":scope > .sprawa-zmiana");
        if (b) b.remove();
        if (!(zajety(stara.el) && zatrzymaj(stara.el))) nowe.push(stara.el);
        continue;
      }
      if (stara && zajety(stara.el)) {
        oznaczZmiane(stara.el, "Ta sprawa zmieniła się w międzyczasie.", s, mapa);
        odlozono = true;
        if (!zatrzymaj(stara.el)) nowe.push(stara.el);
        continue;
      }
      nowe.push(nowaKarta(s, mapa));
    }
    for (const [klucz, w] of [...mapa]) {
      if (widziane.has(klucz)) continue;
      if (w.el.parentNode === kontener && zajety(w.el)) {     // zniknęła z listy, a ktoś w niej pisze — zostaje
        oznaczZmiane(w.el, "Tej sprawy nie ma już na liście (ktoś na nią odpowiedział albo ją odłożył).", null, mapa);
        odlozono = true;
        zatrzymaj(w.el);
      } else {
        mapa.delete(klucz);
      }
    }
    naMiejscu.sort((a, b) => a.i - b.i);
    for (const { k, i } of naMiejscu) nowe.splice(Math.min(i, nowe.length), 0, k);
    // zatrzymana karta stoi gdzie indziej niż w kolejności listy → po końcu pisania lista ułoży się od nowa
    if (naMiejscu.some(({ k }) => widziane.has(k.dataset.klucz))) {
      const wKolejnosci = lista.map((s) => (mapa.get(s.klucz) || {}).el);
      if (nowe.filter((k) => wKolejnosci.includes(k)).some((k, i) => k !== wKolejnosci[i])) odlozono = true;
    }
    ustawDzieci(kontener, nowe.length ? nowe : (pustyEl ? [pustyEl] : []));
    return odlozono;
  }

  // ------------------------------------------------------------------ wyszukiwanie
  /** Ukrywa karty, które nie pasują do zapytania. → liczba pasujących (czekające + odłożone). */
  function filtruj() {
    let ile = 0;
    let wOdlozonych = 0;
    for (const [kontener, odl] of [[listaEl, false], [odlozoneEl.querySelector(".kolejka-lista"), true]]) {
      if (!kontener) continue;
      for (const k of kontener.children) {
        if (!k._sprawa) continue;
        const ok = pasuje(k._sprawa, zapytanie);
        k.hidden = !ok;
        if (ok) {
          ile++;
          if (odl) wOdlozonych++;
        }
      }
    }
    const widoczne = [...listaEl.children].filter((k) => k._sprawa && !k.hidden).length;
    brakWynikow.hidden = !zapytanie || widoczne > 0 || !sprawy.czekajace.length;
    const det = odlozoneEl.querySelector("details");
    if (det && zapytanie && wOdlozonych && !det.open) det.open = true;
    return ile;
  }

  function ustawFiltr(tekst) {
    zapytanie = String(tekst || "").trim();
    return filtruj();
  }

  // ------------------------------------------------------------------ rysowanie listy
  function przebuduj() {
    sprawy = zbudujPytania(plan || {}, raporty || [], agenda, ctx.ja);
    gdzieDecyzja = new Map();
    for (const s of [...sprawy.czekajace, ...sprawy.odlozone, ...sprawy.odpowiedziane]) {
      if ((s.typ === "decyzja" || s.typ === "potwierdzenie") && !gdzieDecyzja.has(s.nr)) gdzieDecyzja.set(s.nr, s.klucz);
      if (s.typ === "pytanie" && !s.zamknieta) {
        for (const x of s.decyzje) if (x.d && OTWARTE_DECYZJE.includes(x.d.status)) gdzieDecyzja.set(numerDecyzji(x.id), s.klucz);
      }
    }
  }

  function rysuj() {
    if (!pierwszeDane) return;
    if (!plan && !raporty) {
      listaEl.replaceChildren(stanBledu(bladPlanu || bladRaportow || {}, "Pytania"));
      return;
    }
    const n = sprawy.czekajace.length;
    ctx.licznik("pytania", n);
    const pokazane = zwarta ? n + sprawy.odlozone.length : n;   // w Sesji lista ma też sprawy z agendy
    licznikEl.textContent = String(pokazane);
    licznikEl.classList.toggle("zero", !pokazane);
    if (typeof opcje.naLicznik === "function") opcje.naLicznik(pokazane);
    const pustyEl = el("div", { class: "pusty kolejka-pusta" }, el("div", { class: "pusty-ikona" }, ikona("ok")),
      el("strong", null, "Nic nie czeka na odpowiedź"),
      el("p", null, sprawy.odlozone.length && !zwarta ? "Reszta czeka na sesję główną." : "Wszystkie pytania, decyzje i raporty są rozpatrzone."));
    if (zwarta) {                                              // w Sesji: najpierw to, co jest na agendzie
      kolejkaOdlozona = uzgodnij(listaEl, [...sprawy.odlozone, ...sprawy.czekajace], kartyKolejki, pustyEl);
      filtruj();
      return;
    }
    let odl = uzgodnij(listaEl, sprawy.czekajace, kartyKolejki, pustyEl);
    if (!sprawy.odlozone.length) {
      odlozoneEl.replaceChildren();
      kartyOdlozonych.clear();
    } else {
      let det = odlozoneEl.querySelector("details");
      if (!det) {
        const lista = el("div", { class: "kolumna kolejka-lista" });
        det = el("details", { class: "zwijane kolejka-odlozone-grupa", open: odlozoneOtwarte },
          el("summary", null, ikona("dol"), ikona("kalendarz"), el("span", { class: "odlozone-tytul" }, "Odłożone na sesję główną"), el("span", { class: "chip-licznik" })),
          el("div", { class: "odlozone-tresc" },
            el("p", { class: "cichy-tekst" }, "Te sprawy omówicie na sesji głównej. Można na nie odpowiedzieć także tutaj."),
            el("div", { class: "rzad-przyciskow" }, el("button", { type: "button", class: "przycisk maly", onclick: () => ctx.idz("sesja") }, ikona("mikrofon"), el("span", null, "Przejdź do Sesji"))),
            lista));
        det.addEventListener("toggle", () => { odlozoneOtwarte = det.open; });
        odlozoneEl.replaceChildren(det);
      }
      det.querySelector(".chip-licznik").textContent = String(sprawy.odlozone.length);
      odl = uzgodnij(det.querySelector(".kolejka-lista"), sprawy.odlozone, kartyOdlozonych, null) || odl;
    }
    kolejkaOdlozona = odl;
    filtruj();
  }

  function przerysuj() {
    przebuduj();
    rysuj();
    if (typeof opcje.naDane === "function") {
      try {
        opcje.naDane(dane());
      } catch (e) {
        console.warn("lista pytań: naDane", e);
      }
    }
  }

  // ------------------------------------------------------------------ nawigacja
  /** Podświetla kartę na liście (także w zwiniętych „Odłożonych”). → czy karta jest na liście. */
  function idzDo(klucz) {
    const k = korzen.querySelector("#" + CSS.escape(prefiks + klucz));
    if (!k) return false;
    if (k.hidden) {                                            // ukryta przez wyszukiwanie: pokaż mimo to
      k.hidden = false;
    }
    const det = k.closest("details");
    if (det && !det.open) det.open = true;
    podswietl(k);
    return true;
  }

  // ------------------------------------------------------------------ dane
  let pobieranie = null;
  async function pobierz(wymus) {
    if (pobieranie) {                                          // jedno pobieranie naraz; wymuszone idzie zaraz po nim
      if (wymus) pobieranie.ponow = true;
      return pobieranie.obietnica;
    }
    const stan = { ponow: false };
    pobieranie = stan;
    stan.obietnica = (async () => {
      try {
        const bierz = (sciezka, modul) => (ctx.jest(modul) ? ctx.api(sciezka) : Promise.reject(Object.assign(new Error("Ta część panelu jest wyłączona."), { status: 404 })));
        const [p, r, a] = await Promise.allSettled([
          bierz("/api/sejf/plan", "sejf"), bierz("/api/raporty", "raporty"), bierz("/api/sesje/agenda", "sesje"),
        ]);
        if (p.status === "fulfilled") {
          plan = p.value || {};
          bladPlanu = null;
        } else {
          bladPlanu = p.reason;
        }
        if (r.status === "fulfilled") {
          raporty = (r.value && r.value.raporty) || [];
          bladRaportow = null;
        } else {
          bladRaportow = r.reason;
        }
        if (a.status === "fulfilled") {
          agenda = a.value || null;
          agendaDostepna = true;
        } else if (a.reason && a.reason.status === 404) {
          agenda = null;
          agendaDostepna = false;
        }
        pierwszeDane = true;
        const podpis = JSON.stringify([plan && plan.wersje, raporty, agenda && agenda.wersja, agendaDostepna,
          !!bladPlanu && !plan, !!bladRaportow && !raporty]);
        if (podpis !== podpisDanych || wymus) {
          podpisDanych = podpis;
          przerysuj();
        }
      } finally {
        pobieranie = null;
      }
      if (stan.ponow) await pobierz(true);
    })();
    return stan.obietnica;
  }

  function dane() {
    return { plan, raporty, agenda, sprawy, bladPlanu, bladRaportow, pierwszeDane, agendaDostepna, mozeZapisywac: mozeZapisywac() };
  }

  window.addEventListener("bc:kto", () => {
    podpisDanych = "";
    for (const m of [kartyKolejki, kartyOdlozonych]) for (const w of m.values()) w.podpis = "";   // nowy podpis odpowiedzi
    if (typeof opcje.naZmianeOsoby === "function") opcje.naZmianeOsoby();
    if (pierwszeDane) przerysuj();
  });

  let stop = null;
  return {
    el: korzen,
    pokaz() {
      const gotowe = pobierz(false);
      if (!stop) stop = ctx.odpytuj(() => pobierz(false), opcje.odswiezanieMs || ODSWIEZANIE_MS);
      return gotowe;
    },
    ukryj() {
      if (stop) stop();
      stop = null;
    },
    odswiez: pobierz,
    karta: kartaSprawy,
    uzgodnij,
    ustawFiltr,
    idzDo,
    zapiszDoSejfu,
    ustawPlan(p) {
      if (!p) return;
      plan = p;
      bladPlanu = null;
      podpisDanych = "";
      przerysuj();
    },
    pelnyRaport: (r) => raportyUI.pelny(r),
    dane,
    get odlozonaZmiana() {
      return kolejkaOdlozona;
    },
    liczbaCzekajacych: () => sprawy.czekajace.length,
  };
}
