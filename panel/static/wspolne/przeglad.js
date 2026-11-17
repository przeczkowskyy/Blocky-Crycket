// Przegląd do akceptacji — część „Do przejrzenia” zakładki Podgląd (17.11.2026, zlecenie Karola z 14.11: przejrzeć
// i zaakceptować wiele rzeczy naraz, widzieć, jak wygląda to, co właśnie powstaje). Dwie części:
//   - „Powstaje teraz”: prace w toku z podglądem (ostatni zrzut, najnowsza klatka z folderu, migawka 3D; bc/prace.py);
//   - „Do akceptacji”: raporty czekające na Akceptuję / Do poprawy jako siatka miniatur z polami wyboru. Zaznaczone
//     raporty da się zaakceptować albo odesłać do poprawy jednym przyciskiem (jeden komentarz dla wszystkich), a
//     „Przeglądaj po kolei” otwiera okno na cały ekran: duży obraz, pytanie i krótki opis, Akceptuję / Do poprawy /
//     Pomiń — po decyzji od razu następny raport, na końcu podsumowanie.
// Decyzje idą tą samą drogą co karty raportów (wspolne/raport_karta.js: decyduj → POST /api/raporty/<id>/decyzja),
// więc zakładka Pytania, Pulpit i historia „Odpowiedziane” widzą je od razu. Panel nie trzyma tu żadnych własnych
// danych — tylko zaznaczenie w pamięci strony.
//
//   const p = przegladAkceptacji(ctx, { naMigawke(id), naLiczbe(n) });
//   p.el, p.pokaz(), p.ukryj(), p.odswiez(wymus?), p.otworzOkno(idRaportu?)

import { el, ikona, czasTemu, dataKrotka, toast, arkusz, odmiana, skroc, powiekszenie, pusty, ladowanie, stanBledu } from "./ui.js";
import { md } from "./markdown.js";
import { kartyRaportow } from "./raport_karta.js";
import { pytanieRaportu, skrotOpisu, zwykly } from "./kolejka.js";
import { pobierzPrace, ostatniePrace, miniaturaPracy, napisKonca, etapPracy, maPodglad } from "./prace.js";
import { dyktafon } from "./dyktafon.js";

const ARKUSZ_STYLOW = new URL("./przeglad.css", import.meta.url).href;
const ODSWIEZANIE_MS = 20000;
const enc = encodeURIComponent;

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

/** Raport czeka na decyzję człowieka (jak w zakładce Pytania: status „czeka”, bez informacji). */
export function czekaNaAkceptacje(r) {
  return !!(r && r.id && r.status === "czeka" && r.rodzaj !== "informacja");
}

export function przegladAkceptacji(ctx, opcje = {}) {
  dolaczCss(ARKUSZ_STYLOW);
  const mozeDecydowac = () => !ctx.statyczny;
  const naMigawke = (id) => (typeof opcje.naMigawke === "function" ? opcje.naMigawke(id) : ctx.idz("podglad", { migawka: id }));

  let raporty = null;                 // ostatnia lista z serwera (wszystkie raporty)
  let migawki = new Map();            // id migawki -> {tytul, zrzuty}
  let blad = null;
  let podpis = "";
  let stop = null;
  let okno = null;                    // otwarte okno „Przeglądaj po kolei”
  const wybrane = new Set();          // zaznaczone raporty (id)
  let trwaHurt = false;

  const karty = kartyRaportow(ctx, {
    naZmiane: (r) => {                 // decyzja z okna pełnego raportu albo z tego widoku
      if (raporty) raporty = raporty.map((x) => (x.id === r.id ? r : x));
      if (!czekaNaAkceptacje(r)) wybrane.delete(r.id);
      if (okno) okno.poZmianie(r);
      rysuj();
    },
  });

  // ------------------------------------------------------------------ szkielet
  const praceEl = el("section", { class: "przeglad-sekcja przeglad-powstaje", hidden: true, "aria-label": "Powstaje teraz" });
  const licznikEl = el("span", { class: "przeglad-licznik" });
  const bPoKolei = el("button", { type: "button", class: "przycisk glowny", onclick: () => otworzOkno() },
    ikona("oko"), el("span", null, "Przeglądaj po kolei"));
  const bWszystkie = el("button", { type: "button", class: "przycisk cichy maly przeglad-wszystkie", onclick: () => zaznaczWszystkie() }, "Zaznacz wszystkie");
  const narzedzia = el("div", { class: "przeglad-narzedzia" }, bPoKolei);
  const siatka = el("div", { class: "przeglad-siatka", role: "list" });
  const pustyEl = el("div", { class: "przeglad-pusty" });
  const pasekWyboru = el("div", { class: "przeglad-pasek-wyboru", hidden: true, role: "region", "aria-label": "Zaznaczone raporty" });
  const doAkceptacji = el("section", { class: "przeglad-sekcja przeglad-akceptacja", "aria-label": "Do akceptacji" },
    el("h2", { class: "przeglad-naglowek" }, ikona("raporty"), el("span", null, "Do akceptacji"), licznikEl, bWszystkie),
    el("p", { class: "cichy-tekst przeglad-podpowiedz" }, "Zaznacz kilka i zdecyduj naraz albo przeglądaj po kolei."),
    narzedzia, siatka, pustyEl, pasekWyboru);
  // najpierw to, co czeka na decyzję; niżej to, co dopiero powstaje
  const korzen = el("div", { class: "przeglad" }, doAkceptacji, praceEl);
  siatka.append(ladowanie());

  // ------------------------------------------------------------------ obrazy raportu
  function obrazyRaportu(r) {
    const wynik = (r.zrzuty || []).map((n, i) => ({
      src: ctx.plik("/api/raporty/" + enc(r.id) + "/plik/" + enc(n)), podpis: (r.tytul || "raport") + " — zrzut " + (i + 1),
    }));
    const mid = r.migawka || ((r.komponenty || []).find((k) => k.typ === "migawka") || {}).cel;
    const m = mid ? migawki.get(mid) : null;
    if (m) {
      for (const n of (m.zrzuty || []).slice(0, 4)) {
        wynik.push({ src: ctx.plik("/api/podglad/" + enc(mid) + "/plik/" + enc(n)), podpis: (m.tytul || "migawka") + " — migawka 3D" });
      }
    }
    return wynik;
  }
  const migawkaRaportu = (r) => r.migawka || ((r.komponenty || []).find((k) => k.typ === "migawka") || {}).cel || null;
  const czekajace = () => (raporty || []).filter(czekaNaAkceptacje);

  // ------------------------------------------------------------------ powstaje teraz (prace w toku z podglądem)
  function rysujPrace(d) {
    const lista = ((d && d.prace) || []).filter((p) => (p.stan === "w_toku" || p.stan === "wstrzymane") && maPodglad(p));
    praceEl.hidden = !lista.length;
    if (!lista.length) return praceEl.replaceChildren();
    praceEl.replaceChildren(
      el("h2", { class: "przeglad-naglowek" }, ikona("zegar"), el("span", null, "Powstaje teraz"), el("span", { class: "przeglad-licznik" }, String(lista.length))),
      el("div", { class: "przeglad-prace" }, lista.map((p) => {
        const n = napisKonca(p);
        return el("article", { class: "przeglad-praca", dataset: { praca: p.id } },
          el("strong", { class: "przeglad-praca-tytul" }, p.tytul || p.id),
          el("span", { class: "cichy-tekst" }, [etapPracy(p), n.tekst].filter(Boolean).join(" · ")),
          miniaturaPracy(ctx, p, { duza: true, naMigawke, migawki }));
      })));
  }

  // ------------------------------------------------------------------ siatka do akceptacji
  function kafel(r) {
    const obrazy = obrazyRaportu(r);
    const tytul = zwykly(r.tytul || "(bez tytułu)");
    const zaznaczony = wybrane.has(r.id);
    const pole = el("input", { type: "checkbox", class: "bez-blokady", checked: zaznaczony, "aria-label": "Zaznacz: " + tytul });
    pole.addEventListener("change", () => {
      if (pole.checked) wybrane.add(r.id);
      else wybrane.delete(r.id);
      k.classList.toggle("wybrany", pole.checked);
      rysujPasek();
    });
    const k = el("article", { class: "przeglad-kafel" + (zaznaczony ? " wybrany" : ""), role: "listitem", dataset: { raport: r.id } },
      el("button", { type: "button", class: "przeglad-kafel-obraz", onclick: () => otworzOkno(r.id), "aria-label": "Przejrzyj: " + tytul },
        obrazy.length ? el("img", { src: obrazy[0].src, alt: "", loading: "lazy", decoding: "async" })
          : el("span", { class: "przeglad-bez-obrazu" }, ikona("raporty"), el("span", null, "bez obrazu")),
        obrazy.length > 1 ? el("span", { class: "przeglad-ile" }, ikona("obraz"), String(obrazy.length)) : null,
        migawkaRaportu(r) ? el("span", { class: "przeglad-3d" }, "3D") : null),
      mozeDecydowac() ? el("label", { class: "przeglad-wybor", title: "Zaznacz" }, pole) : null,
      el("div", { class: "przeglad-kafel-tekst" },
        el("strong", { class: "przeglad-kafel-tytul" }, tytul),
        el("span", { class: "cichy-tekst przeglad-kafel-meta" }, (r.kto || "ktoś") + " · ", el("time", { datetime: r.czas || "", title: dataKrotka(r.czas) }, czasTemu(r.czas)))));
    return k;
  }

  function rysujPasek() {
    for (const id of [...wybrane]) if (!czekajace().some((r) => r.id === id)) wybrane.delete(id);
    const n = wybrane.size;
    pasekWyboru.hidden = !n || !mozeDecydowac();
    bWszystkie.textContent = n && n === czekajace().length ? "Odznacz wszystkie" : "Zaznacz wszystkie";
    if (!n) return pasekWyboru.replaceChildren();
    pasekWyboru.replaceChildren(
      el("span", { class: "przeglad-pasek-tekst" }, "Zaznaczone: " + n),
      el("button", { type: "button", class: "przycisk sukces", disabled: trwaHurt, onclick: () => hurtem("zaakceptowane") },
        ikona("ok"), el("span", null, "Akceptuję (" + n + ")")),
      el("button", { type: "button", class: "przycisk grozny", disabled: trwaHurt, onclick: () => oknoPoprawyHurtem() },
        ikona("krzyzyk"), el("span", null, "Do poprawy")),
      el("button", { type: "button", class: "przycisk cichy ikonowy", "aria-label": "Odznacz wszystkie", onclick: () => { wybrane.clear(); rysuj(true); } }, ikona("zamknij")));
  }

  function zaznaczWszystkie() {
    const lista = czekajace();
    if (wybrane.size && wybrane.size === lista.length) wybrane.clear();
    else for (const r of lista) wybrane.add(r.id);
    rysuj(true);
  }

  function rysuj(wymus) {
    const lista = czekajace();
    if (opcje.naLiczbe) opcje.naLiczbe(raporty ? lista.length : null);
    licznikEl.textContent = raporty ? String(lista.length) : "";
    const s = JSON.stringify([lista.map((r) => [r.id, r.tytul, r.kto, r.czas, r.zrzuty, migawkaRaportu(r)]), [...migawki.keys()], blad && blad.message]);
    rysujPasek();
    if (s === podpis && !wymus) return;
    podpis = s;
    if (!raporty) {
      siatka.replaceChildren();
      pustyEl.replaceChildren(blad ? stanBledu(blad, "Raporty") : ladowanie());
      narzedzia.hidden = true;
      bWszystkie.hidden = true;
      return;
    }
    narzedzia.hidden = !lista.length;
    bWszystkie.hidden = !mozeDecydowac() || !lista.length;
    pustyEl.replaceChildren(lista.length ? "" : pusty("Nic nie czeka na akceptację",
      "Nowe raporty z obrazami (modele, mapy, ekrany) pojawią się tutaj. Pytania i decyzje są w zakładce Pytania.", "ok"));
    // raporty z obrazami najpierw (to je da się ocenić wzrokiem), w każdej grupie od najnowszego
    const posortowane = lista.slice().sort((a, b) => (obrazyRaportu(b).length ? 1 : 0) - (obrazyRaportu(a).length ? 1 : 0) ||
      String(b.czas || "").localeCompare(String(a.czas || "")));
    siatka.replaceChildren(...posortowane.map(kafel));
  }

  // ------------------------------------------------------------------ decyzje hurtem
  async function hurtem(wartosc, komentarz) {
    if (trwaHurt) return;
    const lista = czekajace().filter((r) => wybrane.has(r.id));
    if (!lista.length) return;
    trwaHurt = true;
    rysujPasek();
    let ok = 0;
    const bledy = [];
    for (const r of lista) {
      try {
        await karty.decyduj(r, wartosc, komentarz);
        wybrane.delete(r.id);
        ok++;
      } catch (e) {
        bledy.push("„" + skroc(r.tytul || r.id, 40) + "”: " + e.message);
      }
    }
    trwaHurt = false;
    const co = wartosc === "zaakceptowane" ? "Zaakceptowano" : "Odesłano do poprawy";
    if (ok) toast(co + ": " + ok + " " + odmiana(ok, ["raport", "raporty", "raportów"]) + ".", "ok");
    if (bledy.length) toast("Nie udało się: " + bledy.join("; "), "blad", { czas: 9000 });
    rysuj(true);
    odswiez(true);
  }

  function oknoPoprawyHurtem() {
    const n = wybrane.size;
    const pole = el("textarea", { class: "pole", rows: 4, placeholder: "Co trzeba poprawić? Ten sam komentarz trafi do każdego zaznaczonego raportu.", "aria-label": "Komentarz do poprawy" });
    const dyk = dyktafon(ctx, {
      etykieta: "Nagraj uwagi głosem",
      naTekst: (t) => { pole.value = (pole.value.trim() ? pole.value.trim() + " " : "") + t; pole.focus(); },
    });
    const wyslij = el("button", { type: "submit", class: "przycisk grozny" }, ikona("krzyzyk"), el("span", null, "Odeślij " + n + " do poprawy"));
    const form = el("form", { class: "formularz" },
      el("ul", { class: "lista przeglad-lista-hurt" }, czekajace().filter((r) => wybrane.has(r.id)).map((r) => el("li", { class: "cichy-tekst" }, "„" + skroc(zwykly(r.tytul), 80) + "”"))),
      el("label", { class: "etykieta" }, "Komentarz"), pole,
      el("div", { class: "rzad-przyciskow" }, dyk, el("span", { class: "rozpychacz" }), wyslij));
    const ark = arkusz({ tytul: "Do poprawy (" + n + ")", tresc: form });
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      wyslij.disabled = true;
      await hurtem("do_poprawy", pole.value.trim());
      ark.zamknij();
    });
  }

  // ------------------------------------------------------------------ okno „Przeglądaj po kolei”
  function otworzOkno(odId) {
    const lista = czekajace();
    if (!lista.length) return toast("Nic nie czeka na akceptację.", "info");
    if (okno) okno.zamknij();
    const posortowane = [...siatka.querySelectorAll(".przeglad-kafel")].map((k) => k.dataset.raport)
      .map((id) => lista.find((r) => r.id === id)).filter(Boolean);
    const kolejka = (posortowane.length === lista.length ? posortowane : lista).map((r) => r.id);
    const stanRaportow = new Map();                         // id -> zaakceptowane | do_poprawy | pominiete
    let i = Math.max(0, odId ? kolejka.indexOf(odId) : 0);
    let nrObrazu = 0;
    let wToku = false;
    const poprzedniFokus = document.activeElement;
    const raport = (id) => (raporty || []).find((r) => r.id === id) || null;

    const licznik = el("span", { class: "przeglad-okno-licznik" });
    const zamknijB = el("button", { type: "button", class: "przycisk cichy ikonowy przeglad-okno-x", "aria-label": "Zamknij przegląd" }, ikona("zamknij"));
    const obraz = el("img", { class: "przeglad-okno-img", alt: "" });
    const bezObrazu = el("div", { class: "przeglad-okno-bez" }, ikona("raporty"), el("span", null, "Ten raport nie ma obrazów — oceń go po opisie."));
    const wLewo = el("button", { type: "button", class: "przeglad-okno-nav lewo", "aria-label": "Poprzedni obraz" }, ikona("lewo"));
    const wPrawo = el("button", { type: "button", class: "przeglad-okno-nav prawo", "aria-label": "Następny obraz" }, ikona("prawo"));
    const kropki = el("div", { class: "przeglad-okno-kropki" });
    const scena = el("div", { class: "przeglad-okno-scena" }, obraz, bezObrazu, wLewo, wPrawo, kropki);
    const nad = el("p", { class: "przeglad-okno-nad" });
    const pytanie = el("h2", { class: "przeglad-okno-pytanie" });
    const opis = el("div", { class: "md przeglad-okno-opis" });
    const stanEl = el("p", { class: "przeglad-okno-stan", hidden: true });
    const bOk = el("button", { type: "button", class: "przycisk sukces" }, ikona("ok"), el("span", null, "Akceptuję"));
    const bPopraw = el("button", { type: "button", class: "przycisk grozny" }, ikona("krzyzyk"), el("span", null, "Do poprawy"));
    const bPomin = el("button", { type: "button", class: "przycisk" }, el("span", null, "Pomiń"), ikona("prawo"));
    const akcje = el("div", { class: "przeglad-okno-akcje" }, bOk, bPopraw, bPomin);
    const polePoprawy = el("textarea", { class: "pole", rows: 3, placeholder: "Co trzeba poprawić? (agent przeczyta to przy następnej pracy)", "aria-label": "Komentarz do poprawy" });
    const bOdeslij = el("button", { type: "button", class: "przycisk grozny" }, ikona("krzyzyk"), el("span", null, "Odeślij do poprawy"));
    const bAnuluj = el("button", { type: "button", class: "przycisk cichy" }, "Anuluj");
    const poprawa = el("div", { class: "przeglad-okno-poprawa", hidden: true }, polePoprawy,
      el("div", { class: "rzad-przyciskow" }, dyktafon(ctx, { etykieta: "Nagraj uwagi głosem", naTekst: (t) => { polePoprawy.value = (polePoprawy.value.trim() ? polePoprawy.value.trim() + " " : "") + t; } }),
        el("span", { class: "rozpychacz" }), bAnuluj, bOdeslij));
    const bPoprzedni = el("button", { type: "button", class: "przycisk cichy maly" }, ikona("lewo"), el("span", null, "Poprzedni"));
    const bPelny = el("button", { type: "button", class: "przycisk cichy maly" }, ikona("raporty"), el("span", null, "Pełny raport"));
    const b3d = el("button", { type: "button", class: "przycisk cichy maly" }, ikona("podglad"), el("span", null, "W 3D"));
    const drugie = el("div", { class: "przeglad-okno-drugie" }, bPoprzedni, bPelny, b3d);
    if (!mozeDecydowac()) {                                   // lustro tylko do odczytu: samo przeglądanie (Pomiń = dalej)
      bOk.hidden = true;
      bPopraw.hidden = true;
    }
    const dol = el("div", { class: "przeglad-okno-dol" }, nad, pytanie, opis, stanEl, akcje, poprawa, drugie);
    const podsumowanie = el("div", { class: "przeglad-okno-koniec", hidden: true });
    const tresc = el("div", { class: "przeglad-okno-tresc" }, scena, dol);
    const w = el("div", { class: "przeglad-okno", role: "dialog", "aria-modal": "true", "aria-label": "Przegląd po kolei", tabindex: "-1" },
      el("header", { class: "przeglad-okno-gora" }, licznik, el("strong", { class: "przeglad-okno-tytul" }), zamknijB), tresc, podsumowanie);
    const tytulEl = w.querySelector(".przeglad-okno-tytul");

    function obrazy() {
      const r = raport(kolejka[i]);
      return r ? obrazyRaportu(r) : [];
    }
    function pokazObraz() {
      const o = obrazy();
      const jest = o.length > 0;
      nrObrazu = Math.min(Math.max(0, nrObrazu), Math.max(0, o.length - 1));
      obraz.hidden = !jest;
      bezObrazu.hidden = jest;
      if (jest && obraz.getAttribute("src") !== o[nrObrazu].src) obraz.src = o[nrObrazu].src;
      obraz.alt = jest ? o[nrObrazu].podpis : "";
      wLewo.hidden = wPrawo.hidden = o.length < 2;
      kropki.replaceChildren(...(o.length > 1 ? o.map((_, j) => el("button", {
        type: "button", class: "przeglad-kropka" + (j === nrObrazu ? " aktywna" : ""), "aria-label": "Obraz " + (j + 1) + " z " + o.length,
        onclick: (e) => { e.stopPropagation(); nrObrazu = j; pokazObraz(); },
      })) : []));
    }
    function pokazRaport() {
      const r = raport(kolejka[i]);
      if (!r) return dalej();
      nrObrazu = 0;
      licznik.textContent = (i + 1) + " z " + kolejka.length;
      tytulEl.textContent = zwykly(r.tytul || "(bez tytułu)");
      nad.replaceChildren("z raportu · " + (r.kto || "ktoś") + " · ", el("time", { datetime: r.czas || "", title: dataKrotka(r.czas) }, czasTemu(r.czas)));
      pytanie.textContent = pytanieRaportu(r).tekst;
      const { krotko } = skrotOpisu(r.opis_md, 2);
      opis.innerHTML = krotko ? md(krotko) : "";
      const st = stanRaportow.get(r.id) || (r.status !== "czeka" ? r.status : null);
      stanEl.hidden = !st;
      stanEl.textContent = st === "zaakceptowane" ? "Zaakceptowany — możesz zmienić decyzję." : st === "do_poprawy" ? "Odesłany do poprawy — możesz zmienić decyzję."
        : st === "pominiete" ? "Pominięty — wróci przy następnym przeglądzie." : st ? "Ten raport ma już decyzję (" + st + ")." : "";
      poprawa.hidden = true;
      akcje.hidden = false;
      polePoprawy.value = "";
      bPoprzedni.disabled = i === 0;
      b3d.hidden = !migawkaRaportu(r);
      pokazObraz();
    }
    function dalej() {
      for (let j = i + 1; j < kolejka.length; j++) {
        if (!stanRaportow.has(kolejka[j]) && czekaNaAkceptacje(raport(kolejka[j]))) { i = j; return pokazRaport(); }
      }
      for (let j = 0; j < i; j++) {                              // od początku: co jeszcze czeka i nie było pominięte
        if (!stanRaportow.has(kolejka[j]) && czekaNaAkceptacje(raport(kolejka[j]))) { i = j; return pokazRaport(); }
      }
      pokazKoniec();
    }
    function pokazKoniec() {
      const ile = (wartosc) => [...stanRaportow.values()].filter((v) => v === wartosc).length;
      tresc.hidden = true;
      licznik.textContent = "";
      tytulEl.textContent = "Przejrzane";
      const zostalo = czekajace().filter((r) => !stanRaportow.has(r.id) || stanRaportow.get(r.id) === "pominiete").length;
      podsumowanie.hidden = false;
      podsumowanie.replaceChildren(
        el("div", { class: "pusty-ikona" }, ikona("ok")),
        el("strong", null, "Wszystko przejrzane"),
        el("ul", { class: "lista przeglad-okno-wynik" },
          el("li", null, "Zaakceptowane: " + ile("zaakceptowane")),
          el("li", null, "Do poprawy: " + ile("do_poprawy")),
          el("li", null, "Pominięte: " + ile("pominiete"))),
        zostalo ? el("p", { class: "cichy-tekst" }, "Czeka jeszcze: " + zostalo + " " + odmiana(zostalo, ["raport", "raporty", "raportów"]) + ".") : null,
        el("button", { type: "button", class: "przycisk glowny", onclick: zamknij }, "Zamknij"));
      podsumowanie.querySelector("button").focus({ preventScroll: true });
    }
    async function decyzja(wartosc, komentarz) {
      const r = raport(kolejka[i]);
      if (!r || wToku) return;
      wToku = true;
      for (const b of [bOk, bPopraw, bPomin, bOdeslij]) b.disabled = true;
      try {
        await karty.decyduj(r, wartosc, komentarz);
        stanRaportow.set(r.id, wartosc);
        toast((wartosc === "zaakceptowane" ? "Zaakceptowano: " : "Do poprawy: ") + skroc(zwykly(r.tytul), 60), "ok", { czas: 2500 });
        dalej();
      } catch (e) {
        toast("Nie udało się: " + e.message, "blad");
      } finally {
        wToku = false;
        for (const b of [bOk, bPopraw, bPomin, bOdeslij]) b.disabled = false;
      }
    }
    function zamknij() {
      document.removeEventListener("keydown", naKlawisz, true);
      document.documentElement.classList.remove("bez-przewijania-przeglad");
      w.remove();
      okno = null;
      if (poprzedniFokus && poprzedniFokus.isConnected && poprzedniFokus.focus) {
        try { poprzedniFokus.focus({ preventScroll: true }); } catch (e) { /* nic */ }
      }
      rysuj(true);
    }
    function naKlawisz(e) {
      if (!w.isConnected || document.querySelector(".arkusz-tlo, .lightbox")) return;   // okno nad przeglądem ma pierwszeństwo
      const wPolu = /^(TEXTAREA|INPUT)$/.test((document.activeElement || {}).tagName || "");
      if (e.key === "Escape") {
        e.preventDefault();
        if (!poprawa.hidden) { poprawa.hidden = true; akcje.hidden = false; return; }
        zamknij();
      } else if (!wPolu && (e.key === "ArrowRight" || e.key === "ArrowLeft") && !tresc.hidden) {
        e.preventDefault();
        const o = obrazy();
        if (o.length > 1) { nrObrazu = (nrObrazu + (e.key === "ArrowRight" ? 1 : -1) + o.length) % o.length; pokazObraz(); }
      }
    }
    // przesuwanie palcem po obrazie: następny / poprzedni obraz raportu
    let x0 = null;
    scena.addEventListener("pointerdown", (e) => { x0 = e.clientX; });
    scena.addEventListener("pointerup", (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0;
      x0 = null;
      const o = obrazy();
      if (Math.abs(dx) > 50 && o.length > 1) { nrObrazu = (nrObrazu + (dx < 0 ? 1 : -1) + o.length) % o.length; pokazObraz(); }
    });
    obraz.addEventListener("click", () => {
      const o = obrazy();
      if (o.length) powiekszenie(o, nrObrazu);
    });
    wLewo.addEventListener("click", (e) => { e.stopPropagation(); const o = obrazy(); nrObrazu = (nrObrazu - 1 + o.length) % o.length; pokazObraz(); });
    wPrawo.addEventListener("click", (e) => { e.stopPropagation(); const o = obrazy(); nrObrazu = (nrObrazu + 1) % o.length; pokazObraz(); });
    zamknijB.addEventListener("click", zamknij);
    bOk.addEventListener("click", () => decyzja("zaakceptowane"));
    bPopraw.addEventListener("click", () => { akcje.hidden = true; poprawa.hidden = false; polePoprawy.focus(); });
    bAnuluj.addEventListener("click", () => { poprawa.hidden = true; akcje.hidden = false; });
    bOdeslij.addEventListener("click", () => decyzja("do_poprawy", polePoprawy.value.trim()));
    bPomin.addEventListener("click", () => { stanRaportow.set(kolejka[i], "pominiete"); dalej(); });
    bPoprzedni.addEventListener("click", () => { if (i > 0) { i--; pokazRaport(); } });
    bPelny.addEventListener("click", () => { const r = raport(kolejka[i]); if (r) karty.pelny(r); });
    b3d.addEventListener("click", () => { const r = raport(kolejka[i]); const m = r && migawkaRaportu(r); if (m) { zamknij(); naMigawke(m); } });
    document.addEventListener("keydown", naKlawisz, true);
    document.documentElement.classList.add("bez-przewijania-przeglad");
    document.body.appendChild(w);
    okno = {
      zamknij,
      el: w,
      /** Raport zmieniony gdzie indziej (np. w oknie pełnego raportu) — odśwież widok bieżącego. */
      poZmianie(r) {
        if (r.id === kolejka[i] && !tresc.hidden) {
          if (r.status !== "czeka") stanRaportow.set(r.id, r.status);
          pokazRaport();
        }
      },
    };
    if (i < 0 || !czekaNaAkceptacje(raport(kolejka[i]))) i = 0;
    pokazRaport();
    w.focus({ preventScroll: true });                        // fokus w oknie (Esc, strzałki), bez obwódki na przycisku
    return okno;
  }

  // ------------------------------------------------------------------ dane
  async function odswiez(wymus) {
    const [rap, pod] = await Promise.allSettled([
      ctx.jest("raporty") ? ctx.api("/api/raporty", { czas: 20000 }) : Promise.reject(Object.assign(new Error("moduł raportów wyłączony"), { status: 404 })),
      ctx.jest("podglad") ? ctx.api("/api/podglad", { czas: 20000 }) : Promise.resolve({ migawki: [] }),
    ]);
    if (rap.status === "fulfilled") {
      raporty = (rap.value && rap.value.raporty) || [];
      blad = null;
    } else if (!raporty) blad = rap.reason;
    if (pod.status === "fulfilled") {
      migawki = new Map(((pod.value && pod.value.migawki) || []).map((m) => [m.id, m]));
    }
    rysuj(wymus);
    rysujPrace(ostatniePrace());
    pobierzPrace(ctx).then(rysujPrace).catch(() => {});
  }

  window.addEventListener("bc:prace", (e) => {
    if (korzen.isConnected) rysujPrace(e.detail);
  });
  window.addEventListener("bc:git-pobrano", () => {
    if (stop) odswiez();
  });

  return {
    el: korzen,
    pokaz() {
      odswiez();
      if (!stop) stop = ctx.odpytuj(() => odswiez(), ODSWIEZANIE_MS);
    },
    ukryj() {
      if (stop) stop();
      stop = null;
    },
    odswiez,
    otworzOkno,
  };
}
