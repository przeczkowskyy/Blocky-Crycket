// Agent: rozmowy z Claude Code (subskrypcja osoby przy komputerze z panelem) w pięciu oknach z kartami
// (panel/agenci/<id>.md): Ogólny, Balans, Świat, Modele, Wydanie. Na komputerze z lewej okna (z jednym zdaniem opisu)
// i pod wybranym oknem jego rozmowy, z prawej rozmowa. Na telefonie trzy kroki: okno → rozmowy → rozmowa, z powrotem.
// Odpowiedź na żywo (SSE), tryby, głosówki, długie odpowiedzi i kroki narzędzi zwinięte, usuwanie rozmów (jednej albo
// kilku zaznaczonych), zmiana tytułu. Starszy serwer (bez okien) = jedno okno Ogólny i dotychczasowe zachowanie.

import { el, ikona, czasTemu, dataKrotka, toast, pusty, stanBledu, ladowanie, czasTrwania, skroc, odmiana, arkusz } from "../wspolne/ui.js";
import { md } from "../wspolne/markdown.js";
import { dyktafon } from "../wspolne/dyktafon.js";

const enc = encodeURIComponent;
const ARKUSZ_STYLOW = new URL("./agent.css", import.meta.url).href;
const MAX_WIERSZY = 12;                                        // dłuższa odpowiedź jest zwinięta („Pokaż całość”)

const TRYBY_DOMYSLNE = [
  { id: "plan", nazwa: "Plan", opis: "Tylko czyta i planuje — niczego nie zmienia." },
  { id: "praca", nazwa: "Praca", opis: "Edytuje pliki i używa dozwolonych narzędzi; resztę odmawia." },
  { id: "auto", nazwa: "Auto", opis: "Sam decyduje o narzędziach — największa swoboda." },
];
const OKNO_ZAPAS = { id: "ogolny", nazwa: "Ogólny", opis: "Wszystkie rozmowy z agentem.", tryby: null };
const IKONY_KONTEKSTU = { raport: "raporty", studio: "studio", notatka: "notatka", migawka: "migawka", plik: "notatka" };
const PODPOWIEDZI = {
  ogolny: ["Co zostało do zrobienia w aktywnej fazie?", "Podsumuj raporty, które czekają na akceptację.",
    "Jakie decyzje czekają na zatwierdzenie i co polecasz?"],
  balans: ["Ile czasu zajmie dojście z lasu do bagna?", "Zaproponuj szanse rzadkości przedmiotów.",
    "Jak powinien rosnąć koszt budynków Twierdzy?"],
  swiat: ["Jakie potwory pasują do bagna?", "Opisz golema-bossa biomu kryształowego.", "Czym różnią się biomy na start?"],
  modele: ["Z jakich klocków zbudować kryształowego slima?", "Który budynek zlecić jako pierwszy?",
    "Opisz wygląd strażnika lasu."],
  wydanie: ["Czy wolno sprzedawać jajka za Robuxy?", "Ile kosztuje założenie grupy Roblox?",
    "Od czego zacząć marketing gry?"],
};

function czytaj(k, d) {
  try {
    return localStorage.getItem(k) || d;
  } catch (e) {
    return d;
  }
}
function zapisz(k, v) {
  try {
    if (v) localStorage.setItem(k, v);
    else localStorage.removeItem(k);
  } catch (e) { /* nic */ }
}
function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

/** Ile wierszy zajmie tekst na wąskim ekranie (zgrubnie): długi wiersz liczy się jak kilka. */
export function liczWiersze(tekst) {
  return String(tekst || "").split("\n").reduce((n, l) => n + (l.trim() ? Math.max(1, Math.ceil(l.length / 90)) : 0), 0);
}

/** „Read ×2 · Grep · Bash” — krótkie podsumowanie kroków narzędzi. */
function podsumowanieNarzedzi(nazwy) {
  const ile = new Map();
  for (const n of nazwy) ile.set(n, (ile.get(n) || 0) + 1);
  const czesci = [...ile.entries()].map(([n, k]) => (k > 1 ? n + " ×" + k : n));
  return czesci.slice(0, 4).join(" · ") + (czesci.length > 4 ? " · …" : "");
}

/** Okno potwierdzenia → Promise<boolean>. */
function potwierdz({ tytul, tresc, tak = "Usuń", grozny = true }) {
  return new Promise((rozwiaz) => {
    let wynik = false;
    const nie = el("button", { type: "button", class: "przycisk" }, "Anuluj");
    const ok = el("button", { type: "button", class: "przycisk " + (grozny ? "grozny" : "glowny") }, tak);
    const a = arkusz({
      tytul,
      tresc: el("div", { class: "ag-potwierdz" }, tresc, el("div", { class: "rzad-przyciskow ag-potwierdz-akcje" }, nie, ok)),
      naZamkniecie: () => rozwiaz(wynik),
    });
    nie.addEventListener("click", () => a.zamknij());
    ok.addEventListener("click", () => {
      wynik = true;
      a.zamknij();
    });
  });
}

export default {
  id: "agent",
  tytul: "Agent",
  ikona: "agent",
  kolejnosc: 50,
  utworz(ctx) {
    dolaczCss(ARKUSZ_STYLOW);
    const s = {
      stan: null,            // /api/agent/stan
      maOkna: false,         // serwer zna okna (po restarcie panelu)
      funkcje: [],
      okna: [OKNO_ZAPAS],
      okno: czytaj("bc.agent.okno", "ogolny"),
      watki: [],
      znane: null,           // identyfikatory z ostatniej listy (wykrycie rozmowy usuniętej przez kogoś innego)
      aktywny: czytaj("bc.agent.watek", null),
      widok: null,           // ostatnio wczytany wątek (mozna_usunac, osoby)
      liczbaWiad: -1,
      wczytuje: null,        // id rozmowy, którą właśnie wczytujemy (lista nie wczytuje jej drugi raz)
      nrWczyt: 0,            // numer ostatniego wczytania rozmowy — starsza odpowiedź nie nadpisuje nowszej
      trwa: false,
      strumien: null,
      ostatniN: -1,
      proby: 0,
      kontekst: [],
      tryb: czytaj("bc.agent.tryb", null),
      tekstNaZywo: "",
      ramka: 0,
      wysylanie: false,
      krok: "okna",          // telefon: okna → rozmowy → rozmowa
      zaznaczanie: false,
      zaznaczone: new Set(),
    };

    // ------------------------------------------------------------------ szkielet: okna i rozmowy (lewa kolumna)
    const listaOkien = el("ul", { class: "ag-okna", "aria-label": "Okna agenta" });
    const uwagaOkien = el("p", { class: "cichy-tekst ag-uwaga", hidden: true });
    const naglOkna = el("h2", { class: "ag-rozmowy-tytul" });
    const opisOkna = el("p", { class: "cichy-tekst ag-rozmowy-opis" });
    const nowyBtn = el("button", { type: "button", class: "przycisk glowny maly ag-nowa" }, ikona("plus"), el("span", null, "Nowa rozmowa"));
    const zaznaczBtn = el("button", { type: "button", class: "przycisk cichy maly ag-zaznacz", hidden: true }, "Zaznacz");
    const licznikZazn = el("span", { class: "ag-zazn-licznik" });
    const usunZaznBtn = el("button", { type: "button", class: "przycisk grozny maly ag-usun-zaznaczone" }, ikona("kosz"), el("span", null, "Usuń"));
    const anulujZaznBtn = el("button", { type: "button", class: "przycisk cichy maly" }, "Anuluj");
    const pasekZazn = el("div", { class: "ag-zazn", hidden: true }, licznikZazn, usunZaznBtn, anulujZaznBtn);
    const listaWatkow = el("ul", { class: "ag-watki", "aria-label": "Rozmowy" });
    const rozmowy = el("section", { class: "ag-rozmowy", "aria-label": "Rozmowy w oknie" },
      el("div", { class: "ag-rozmowy-nagl" },
        el("button", { type: "button", class: "przycisk cichy maly ag-tel ag-wstecz", onclick: () => ustawKrok("okna") }, ikona("wstecz"), el("span", null, "Okna")),
        el("div", { class: "ag-tel" }, naglOkna, opisOkna)),
      el("div", { class: "ag-rozmowy-akcje" }, nowyBtn, zaznaczBtn),
      pasekZazn,
      listaWatkow);
    const bok = el("aside", { class: "ag-bok", "aria-label": "Okna i rozmowy" },
      el("h2", { class: "ag-bok-tytul" }, "Okna agenta"), uwagaOkien, listaOkien);

    // ------------------------------------------------------------------ szkielet: rozmowa (prawa kolumna)
    const oknoCzatu = el("span", { class: "ag-czat-okno" });
    const tytulWatku = el("h1", { class: "agent-tytul ag-tytul" }, "Nowa rozmowa");
    const tytulBtn = el("button", { type: "button", class: "ag-tytul-btn", title: "Zmień tytuł", disabled: true }, tytulWatku);
    const statusWatku = el("span", { class: "agent-status" });
    const stopBtn = el("button", { type: "button", class: "przycisk grozny maly", hidden: true }, ikona("stop"), el("span", null, "Stop"));
    const usunBtn = el("button", { type: "button", class: "przycisk cichy ikonowy ag-usun-czat", hidden: true, "aria-label": "Usuń rozmowę", title: "Usuń rozmowę" }, ikona("kosz"));
    const nagl = el("header", { class: "agent-nagl ag-czat-nagl" },
      el("button", { type: "button", class: "przycisk cichy maly ag-tel ag-wstecz", onclick: () => { ustawKrok("rozmowy"); rysujOkna(); } }, ikona("wstecz"), el("span", null, "Rozmowy")),
      el("div", { class: "agent-nagl-tekst" }, oknoCzatu, tytulBtn, statusWatku), stopBtn, usunBtn);

    const wiadomosci = el("div", { class: "agent-wiadomosci" });
    const naZywo = el("div", { class: "agent-na-zywo" });
    const przewijak = el("div", { class: "agent-przewijak", role: "log", "aria-live": "polite" }, wiadomosci, naZywo);

    const chipyKontekstu = el("div", { class: "chipy agent-kontekst" });
    const pole = el("textarea", { class: "pole agent-pole", rows: 1, placeholder: "Napisz do agenta…", "aria-label": "Wiadomość do agenta" });
    const wyslijBtn = el("button", { type: "button", class: "przycisk glowny ikonowy agent-wyslij", "aria-label": "Wyślij", title: "Wyślij (Enter)" }, ikona("wyslij"));
    const tryby = el("div", { class: "przelacznik maly agent-tryby", role: "radiogroup", "aria-label": "Tryb pracy agenta" });
    const opisTrybu = el("p", { class: "cichy-tekst agent-opis-trybu" });
    const notaSubskrypcji = el("p", { class: "cichy-tekst ag-subskrypcja", hidden: true });
    const dyk = dyktafon(ctx, {
      etykieta: "Podyktuj wiadomość",
      naTekst: (t) => {
        pole.value = (pole.value.trim() ? pole.value.trim() + " " : "") + t;
        dopasujPole();
        pole.focus();
      },
    });
    const pisz = el("footer", { class: "agent-pisz" },
      chipyKontekstu,
      el("div", { class: "agent-pole-rzad" }, pole, dyk, wyslijBtn),
      notaSubskrypcji,
      el("div", { class: "agent-tryby-rzad" }, tryby, opisTrybu));

    const czat = el("section", { class: "agent-czat ag-czat" }, nagl, przewijak, pisz);
    const blokada = el("div", { class: "agent-blokada", hidden: true });
    const korzen = el("div", { class: "widok-pelny ag krok-okna" }, bok, czat, blokada);

    // ------------------------------------------------------------------ pomocnicze
    function ustawKrok(k) {
      s.krok = k;
      korzen.classList.remove("krok-okna", "krok-rozmowy", "krok-rozmowa");
      korzen.classList.add("krok-" + k);
      if (k === "rozmowa") naDol(true);
    }
    function blisko() {
      return przewijak.scrollHeight - przewijak.scrollTop - przewijak.clientHeight < 120;
    }
    function naDol(wymus) {
      if (wymus || blisko()) requestAnimationFrame(() => { przewijak.scrollTop = przewijak.scrollHeight; });
    }
    function dopasujPole() {
      pole.style.height = "auto";
      pole.style.height = Math.min(pole.scrollHeight + 4, Math.max(120, window.innerHeight * 0.35)) + "px";
    }
    function oknoBiezace() {
      return s.okna.find((o) => o.id === s.okno) || s.okna[0];
    }
    function oknoWatku(w) {
      return s.maOkna ? (w && w.okno) || "ogolny" : s.okna[0].id;
    }
    function watkiOkna() {
      return s.watki.filter((w) => oknoWatku(w) === s.okno);
    }
    function moznaZmieniac(w) {
      return !!(w && w.mozna_usunac === true);
    }

    // ------------------------------------------------------------------ tryby
    function listaTrybow() {
      const t = (s.stan && Array.isArray(s.stan.tryby) && s.stan.tryby.length) ? s.stan.tryby : TRYBY_DOMYSLNE;
      const o = oknoBiezace();
      return Array.isArray(o.tryby) && o.tryby.length ? t.filter((x) => o.tryby.includes(x.id)) : t;
    }
    function trybDozwolony(id) {
      return ctx.ja.lokalny || id !== "auto";
    }
    function rysujTryby() {
      const t = listaTrybow();
      let wybrany = s.tryb;
      if (!wybrany || !t.some((x) => x.id === wybrany) || !trybDozwolony(wybrany)) {
        const dom = (s.stan && s.stan.tryb_domyslny) || (ctx.konfiguracja.agent && ctx.konfiguracja.agent.tryb_domyslny) || "praca";
        wybrany = t.some((x) => x.id === dom) && trybDozwolony(dom) ? dom : ((t.find((x) => trybDozwolony(x.id)) || t[0] || {}).id || "praca");
      }
      tryby.replaceChildren(...t.map((x) => {
        const b = el("button", {
          type: "button", role: "radio", class: "przelacznik-opcja" + (x.id === wybrany ? " aktywny" : ""),
          "aria-checked": x.id === wybrany ? "true" : "false", disabled: !trybDozwolony(x.id),
          title: trybDozwolony(x.id) ? x.opis || "" : "Z telefonu najwyżej tryb Praca",
        }, x.nazwa || x.id);
        b.addEventListener("click", () => {
          s.tryb = x.id;
          zapisz("bc.agent.tryb", x.id);
          rysujTryby();
        });
        return b;
      }));
      s.trybWyslany = wybrany;
      const opis = t.find((x) => x.id === wybrany);
      opisTrybu.textContent = opis ? opis.opis || "" : "";
    }

    function rysujKontekst() {
      chipyKontekstu.replaceChildren(...s.kontekst.map((k, i) => el("span", { class: "chip niebieski chip-kontekst", title: k.typ + ": " + k.cel },
        ikona(IKONY_KONTEKSTU[k.typ] || "link"), el("span", null, skroc(k.etykieta || k.cel, 40)),
        el("button", {
          type: "button", class: "chip-usun", "aria-label": "Usuń kontekst " + (k.etykieta || k.cel),
          onclick: () => {
            s.kontekst.splice(i, 1);
            rysujKontekst();
          },
        }, ikona("zamknij")))));
      chipyKontekstu.hidden = !s.kontekst.length;
    }

    /** Jedno zdanie pod polem: zdalnie odpowiedź idzie na subskrypcji gospodarza panelu. */
    function rysujNoteSubskrypcji() {
      let t = "";
      if (!ctx.ja.lokalny) t = "Piszesz zdalnie: odpowiedź idzie na subskrypcji Claude gospodarza panelu.";
      else if (s.widok && (s.widok.osoby || []).some((o) => o && o.zdalnie === true)) {
        t = "W tej rozmowie pisze też ktoś zdalnie: odpowiedzi idą na Twojej subskrypcji Claude.";
      }
      notaSubskrypcji.textContent = t;
      notaSubskrypcji.hidden = !t;
    }

    function ustawTrwa(tak) {
      s.trwa = !!tak;
      stopBtn.hidden = !s.trwa;
      wyslijBtn.disabled = s.trwa || s.wysylanie;
      statusWatku.replaceChildren(s.trwa ? el("span", { class: "pracuje" }, el("span", { class: "kropka-pulsujaca" }), "agent pracuje…") : "");
      korzen.classList.toggle("pracuje", s.trwa);
      rysujPrzyciskiCzatu();
    }

    function rysujPrzyciskiCzatu() {
      const w = s.widok && s.widok.id === s.aktywny ? s.widok : null;
      usunBtn.hidden = !(w && moznaZmieniac(w) && s.funkcje.includes("usuwanie"));
      usunBtn.disabled = s.trwa;
      usunBtn.title = s.trwa ? "Nie można usunąć, gdy agent pracuje" : "Usuń rozmowę";
      tytulBtn.disabled = !(w && moznaZmieniac(w) && s.funkcje.includes("tytul"));
      oknoCzatu.textContent = s.maOkna ? oknoBiezace().nazwa : "";
      oknoCzatu.hidden = !s.maOkna;
    }

    // ------------------------------------------------------------------ wiadomości
    function grupaNarzedzi() {
      const nazwy = [];
      const lista = el("div", { class: "ag-kroki-lista", hidden: true });
      const licznik = el("strong", { class: "ag-kroki-licznik" });
      const podsum = el("span", { class: "ag-kroki-podsum" });
      const przycisk = el("button", { type: "button", class: "ag-kroki-nagl", "aria-expanded": "false" },
        ikona("narzedzie"), licznik, podsum, ikona("dol"));
      const box = el("div", { class: "wiad ag-kroki" }, przycisk, lista);
      przycisk.addEventListener("click", () => {
        const otworz = lista.hidden;
        lista.hidden = !otworz;
        przycisk.setAttribute("aria-expanded", otworz ? "true" : "false");
        box.classList.toggle("otwarte", otworz);
      });
      const g = {
        el: box,
        dodaj(nazwa, opis) {
          nazwy.push(nazwa || "narzędzie");
          lista.appendChild(el("div", { class: "ag-krok", title: (nazwa || "") + (opis ? ": " + opis : "") },
            el("strong", null, nazwa || "narzędzie"), opis ? " · " + skroc(opis, 200) : ""));
          licznik.textContent = "Kroki agenta: " + nazwy.length;
          podsum.textContent = podsumowanieNarzedzi(nazwy);
        },
      };
      box._grupa = g;
      return g;
    }
    function rozbierzNarzedzie(tekst) {
      const t = String(tekst || "");
      const dw = t.indexOf(": ");
      return dw > 0 && dw < 60 ? [t.slice(0, dw), t.slice(dw + 2)] : [t, ""];
    }

    function metaCzasu(czas) {
      return czas ? el("span", { title: dataKrotka(czas) }, czasTemu(czas)) : null;
    }

    function dymek(w) {
      const rola = w.rola || "system";
      if (rola === "system") {
        return el("div", { class: "wiad wiad-system", dataset: { nr: w.nr } }, el("span", null, w.tekst || ""));
      }
      if (rola === "user") {
        return el("div", { class: "wiad wiad-user", dataset: { nr: w.nr } },
          el("div", { class: "wiad-meta" }, el("strong", { class: "wiad-autor" }, w.kto || ctx.ja.kto || "Ty"),
            w.zdalnie === true ? el("span", { class: "wiad-zdalnie" }, "zdalnie") : null, metaCzasu(w.czas)),
          (w.kontekst || []).length ? el("div", { class: "chipy" }, w.kontekst.map((k) => el("span", { class: "chip niebieski" }, ikona(IKONY_KONTEKSTU[k.typ] || "link"), skroc(k.etykieta || k.cel, 36)))) : null,
          el("div", { class: "wiad-tekst" }, w.tekst || ""));
      }
      const tresc = el("div", { class: "md wiad-tekst", html: md(w.tekst || "") });
      const box = el("div", { class: "wiad wiad-agent", dataset: { nr: w.nr } },
        el("div", { class: "wiad-meta" }, el("span", { class: "wiad-znak", "aria-hidden": "true" }, ikona("agent")), el("strong", null, "Agent"), metaCzasu(w.czas)),
        tresc);
      if (liczWiersze(w.tekst) > MAX_WIERSZY) {
        tresc.classList.add("ag-zwinieta");
        const przycisk = el("button", { type: "button", class: "ag-pokaz-calosc", "aria-expanded": "false" }, "Pokaż całość");
        przycisk.addEventListener("click", () => {
          const zwin = !tresc.classList.contains("ag-zwinieta");
          tresc.classList.toggle("ag-zwinieta", zwin);
          przycisk.textContent = zwin ? "Pokaż całość" : "Zwiń";
          przycisk.setAttribute("aria-expanded", zwin ? "false" : "true");
          if (zwin) box.scrollIntoView({ block: "nearest" });
        });
        box.appendChild(przycisk);
      }
      return box;
    }

    /** Wiadomości wątku: kolejne kroki narzędzi zwinięte w jeden wiersz z licznikiem. */
    function rysujWiadomosci(lista) {
      const out = [];
      let grupa = null;
      for (const m of lista) {
        if (m.rola === "narzedzie") {
          if (!grupa) {
            grupa = grupaNarzedzi();
            out.push(grupa.el);
          }
          const [n, o] = rozbierzNarzedzie(m.tekst);
          grupa.dodaj(n, o);
        } else {
          grupa = null;
          out.push(dymek(m));
        }
      }
      wiadomosci.replaceChildren(...out);
    }

    function powitanie() {
      const o = oknoBiezace();
      const podp = PODPOWIEDZI[o.id] || PODPOWIEDZI.ogolny;
      return el("div", { class: "agent-powitanie ag-powitanie" },
        el("div", { class: "agent-powitanie-znak", "aria-hidden": "true" }, ikona("agent")),
        el("h2", null, s.maOkna ? "Okno: " + o.nazwa : "O co chcesz zapytać?"),
        el("p", { class: "cichy-tekst" }, s.maOkna ? o.opis : "Agent to Claude Code na komputerze z panelem: zna sejf, kod gry i Roblox Studio."),
        s.maOkna && o.narzedzia ? el("p", { class: "cichy-tekst ag-powitanie-narzedzia" }, o.narzedzia) : null,
        el("p", { class: "cichy-tekst ag-powitanie-styl" }, "Agent odpowiada krótko. Napisz „rozwiń”, gdy chcesz szczegółów."),
        el("div", { class: "agent-podpowiedzi" }, podp.map((p) => el("button", {
          type: "button", class: "przycisk podpowiedz",
          onclick: () => {
            pole.value = p;
            dopasujPole();
            pole.focus();
          },
        }, p))));
    }

    // ------------------------------------------------------------------ na żywo (strumień)
    function wyczyscNaZywo() {
      naZywo.replaceChildren();
      s.tekstNaZywo = "";
    }
    function segmentTekstu() {
      let ost = naZywo.lastElementChild;
      if (!ost || !ost.classList.contains("wiad-agent")) {
        ost = el("div", { class: "wiad wiad-agent na-zywo" },
          el("div", { class: "wiad-meta" }, el("span", { class: "wiad-znak", "aria-hidden": "true" }, ikona("agent")), el("strong", null, "Agent"), el("span", null, "pisze…")),
          el("div", { class: "md wiad-tekst" }));
        naZywo.appendChild(ost);
        s.tekstNaZywo = "";
      }
      return ost;
    }
    function rysujTekstNaZywo() {
      s.ramka = 0;
      const seg = segmentTekstu();
      seg.querySelector(".wiad-tekst").innerHTML = md(s.tekstNaZywo) + '<span class="kursor" aria-hidden="true"></span>';
      naDol();
    }

    function naZdarzenie(id, z) {
      if (id !== s.aktywny || !z) return;
      if (typeof z.n === "number") {
        if (z.n <= s.ostatniN) return;                         // powtórka po wznowieniu strumienia
        s.ostatniN = z.n;
      }
      s.proby = 0;
      switch (z.typ) {
        case "tekst":
          segmentTekstu();
          s.tekstNaZywo += z.delta || "";
          if (!s.ramka) s.ramka = requestAnimationFrame(rysujTekstNaZywo);
          break;
        case "narzedzie": {
          const ost = naZywo.lastElementChild;
          const g = ost && ost._grupa ? ost._grupa : grupaNarzedzi();
          if (g.el !== ost) naZywo.appendChild(g.el);
          g.dodaj(z.nazwa, z.opis);
          s.tekstNaZywo = "";
          naDol();
          break;
        }
        case "wiadomosc": {
          const w = z.wiadomosc || {};
          if (w.rola === "assistant") {
            if (s.ramka) cancelAnimationFrame(s.ramka);
            s.ramka = 0;
            wyczyscNaZywo();
            const pow = wiadomosci.querySelector(".agent-powitanie");
            if (pow) pow.remove();
            wiadomosci.appendChild(dymek(w));
            naDol();
          }
          break;
        }
        case "blad":
          naZywo.appendChild(el("div", { class: "wiad wiad-blad" }, ikona("ostrzezenie"), el("span", null, z.tekst || "Błąd agenta")));
          naDol();
          break;
        case "koniec": {
          zamknijStrumien();
          ustawTrwa(false);
          const czesci = [];
          if (z.czas_s) czesci.push("gotowe w " + czasTrwania(z.czas_s));
          if (typeof z.koszt_usd === "number") czesci.push("≈ $" + z.koszt_usd.toFixed(2) + " (wg Claude Code; w subskrypcji)");
          wczytajWatek(id, { poKoncu: czesci.join(" · ") });
          wczytajWatki();
          break;
        }
        default:
          break;
      }
    }

    function zamknijStrumien() {
      if (s.strumien) s.strumien.zamknij();
      s.strumien = null;
    }

    function polacz(id, od) {
      zamknijStrumien();
      s.ostatniN = od - 1;
      s.strumien = ctx.sse("/api/agent/watki/" + enc(id) + "/strumien?od=" + od, (z) => naZdarzenie(id, z), {
        naKoniec: (b) => {
          s.strumien = null;
          if (id !== s.aktywny || !s.trwa) return;
          if (s.proby++ < 6) {                                 // połączenie zerwane w trakcie pracy — wznawiamy
            setTimeout(() => {
              if (id === s.aktywny && s.trwa && !s.strumien) polacz(id, s.ostatniN + 1);
            }, 1500 * s.proby);
          } else {
            toast("Straciłem połączenie z agentem. Odśwież rozmowę.", "blad");
            wczytajWatek(id);
          }
          if (b && b.status && b.status !== 0) console.warn("strumień agenta:", b.message);
        },
      });
    }

    // ------------------------------------------------------------------ okna i lista rozmów
    function rysujOkna() {
      listaOkien.replaceChildren(...s.okna.map((o) => {
        const watki = s.watki.filter((w) => oknoWatku(w) === o.id);
        const pracuje = watki.some((w) => w.trwa);
        const wybrane = o.id === s.okno;
        const przycisk = el("button", {
          type: "button", class: "ag-okno-btn", "aria-current": wybrane ? "true" : null, dataset: { okno: o.id },
          onclick: () => wybierzOkno(o.id, true),
        },
        el("span", { class: "ag-okno-gora" },
          el("strong", { class: "ag-okno-nazwa" }, o.nazwa),
          pracuje ? el("span", { class: "kropka-pulsujaca", title: "agent pracuje" }) : null,
          el("span", { class: "ag-okno-licznik", title: watki.length + " " + odmiana(watki.length, ["rozmowa", "rozmowy", "rozmów"]) }, watki.length ? String(watki.length) : ""),
          el("span", { class: "ag-okno-strzalka ag-tel", "aria-hidden": "true" }, ikona("prawo"))),
        el("span", { class: "ag-okno-opis" }, o.opis || ""));
        return el("li", { class: "ag-okno" + (wybrane ? " wybrane" : ""), dataset: { okno: o.id } }, przycisk, wybrane ? rozmowy : null);
      }));
      const o = oknoBiezace();
      naglOkna.textContent = o.nazwa;
      opisOkna.textContent = o.opis || "";
    }

    function wybierzOkno(id, zKlikniecia) {
      const zmiana = id !== s.okno;
      if (zmiana) {
        s.okno = id;
        zapisz("bc.agent.okno", id);
        s.zaznaczanie = false;
        s.zaznaczone.clear();
        rysujTryby();
        const akt = s.watki.find((w) => w.id === s.aktywny);
        if (!akt || oknoWatku(akt) !== id) nowaRozmowa(false);
      }
      if (zKlikniecia) ustawKrok("rozmowy");
      rysujOkna();
      rysujListeWatkow();
      rysujPrzyciskiCzatu();
    }

    /** Kto założył wątek i czy zdalnie (agent zawsze idzie na subskrypcji osoby przy komputerze z panelem) oraz kto
     * jeszcze w nim pisał. Starszy serwer tych pól nie zwraca — wtedy nic. */
    function kimWatek(w) {
      const zal = String(w.utworzyl || "").trim();
      const inni = (Array.isArray(w.osoby) ? w.osoby : []).filter((o) => o && o.kto && o.kto !== zal);
      if (!zal && !inni.length) return null;
      const gdzie = (z) => (z === true ? " (zdalnie)" : "");
      const tekst = (zal ? "założył(a): " + zal + gdzie(w.zdalnie) : "") +
        (inni.length ? (zal ? " · " : "") + "pisze też: " + inni.map((o) => o.kto + gdzie(o.zdalnie)).join(", ") : "");
      return el("span", { class: "cichy-tekst watek-kto ag-watek-kto", title: "Agent pracuje na subskrypcji osoby przy komputerze z panelem — także dla osób zdalnych." },
        ikona("uzytkownik"), el("span", null, tekst));
    }

    function rysujListeWatkow() {
      const lista = watkiOkna();
      const moznaUsuwac = s.funkcje.includes("usuwanie") && lista.some((w) => moznaZmieniac(w));
      zaznaczBtn.hidden = !moznaUsuwac || s.zaznaczanie;
      pasekZazn.hidden = !s.zaznaczanie;
      for (const id of [...s.zaznaczone]) if (!lista.some((w) => w.id === id)) s.zaznaczone.delete(id);
      licznikZazn.textContent = "Zaznaczono: " + s.zaznaczone.size;
      usunZaznBtn.disabled = !s.zaznaczone.size;
      korzen.classList.toggle("zaznaczanie", s.zaznaczanie);
      if (!lista.length) {
        listaWatkow.replaceChildren(el("li", { class: "cichy-tekst ag-watki-pusto" }, "Jeszcze nie ma rozmów w tym oknie."));
        return;
      }
      listaWatkow.replaceChildren(...lista.map((w) => {
        const moze = moznaZmieniac(w) && s.funkcje.includes("usuwanie");
        const zazn = s.zaznaczone.has(w.id);
        const poleZazn = s.zaznaczanie && moze ? el("input", {
          type: "checkbox", class: "ag-watek-pole", checked: zazn, "aria-label": "Zaznacz: " + (w.tytul || "Rozmowa"),
          disabled: !!w.trwa,
          onchange: (e) => {
            if (e.target.checked) s.zaznaczone.add(w.id);
            else s.zaznaczone.delete(w.id);
            rysujListeWatkow();
          },
        }) : null;
        const ile = w.wiadomosci || 0;
        const przycisk = el("button", {
          type: "button", class: "ag-watek-btn", "aria-current": w.id === s.aktywny ? "true" : null,
          onclick: () => {
            if (s.zaznaczanie) {
              if (!moze || w.trwa) return;
              if (zazn) s.zaznaczone.delete(w.id);
              else s.zaznaczone.add(w.id);
              rysujListeWatkow();
              return;
            }
            ustawKrok("rozmowa");
            if (w.id !== s.aktywny) wybierzWatek(w.id);
          },
        },
        el("span", { class: "ag-watek-tytul" }, w.trwa ? el("span", { class: "kropka-pulsujaca", title: "pracuje" }) : null, el("span", null, w.tytul || "Rozmowa")),
        el("span", { class: "cichy-tekst ag-watek-meta" }, czasTemu(w.ostatnio || w.utworzono) + " · " + ile + " " + odmiana(ile, ["wiadomość", "wiadomości", "wiadomości"]),
          w.systemowy ? el("span", { class: "ag-systemowa", title: "Rozmowę założył panel dla sesji głosowej" }, "systemowa") : null),
        kimWatek(w));
        const kosz = !s.zaznaczanie && moze ? el("button", {
          type: "button", class: "przycisk cichy ikonowy ag-watek-usun", disabled: !!w.trwa,
          "aria-label": "Usuń rozmowę: " + (w.tytul || "Rozmowa"), title: w.trwa ? "Agent pracuje — usuniesz po końcu" : "Usuń rozmowę",
          onclick: () => usunJedna(w),
        }, ikona("kosz")) : null;
        return el("li", { class: "ag-watek" + (w.id === s.aktywny ? " aktywny" : "") + (zazn ? " zaznaczony" : ""), dataset: { id: w.id } }, poleZazn, przycisk, kosz);
      }));
    }

    async function wczytajWatki() {
      let ok = true;
      try {
        const d = await ctx.api("/api/agent/watki");
        s.watki = (d && d.watki) || [];
        s.watki.sort((a, b) => String(b.ostatnio || b.utworzono || "").localeCompare(String(a.ostatnio || a.utworzono || "")));
      } catch (e) {
        ok = false;
      }
      if (ok) {
        const poprzednie = s.znane;
        s.znane = new Set(s.watki.map((w) => w.id));
        // wspólna rozmowa: druga osoba dopisała się albo agent ruszył — dociągnij widok; ktoś usunął — powiedz
        if (s.aktywny && !s.trwa && !s.wysylanie && s.wczytuje !== s.aktywny) {
          const w = s.watki.find((x) => x.id === s.aktywny);
          if (!w && poprzednie && poprzednie.has(s.aktywny)) {
            toast("Tę rozmowę ktoś usunął.", "info");
            nowaRozmowa(false);
          } else if (w && s.widok && s.widok.id === w.id && (w.trwa || w.wiadomosci !== s.liczbaWiad)) {
            wczytajWatek(w.id);
          }
        }
      }
      rysujOkna();
      rysujListeWatkow();
    }

    function nowaRozmowa(doCzatu) {
      zamknijStrumien();
      s.aktywny = null;
      s.widok = null;
      s.liczbaWiad = -1;
      zapisz("bc.agent.watek", null);
      wyczyscNaZywo();
      ustawTrwa(false);
      tytulWatku.textContent = "Nowa rozmowa";
      wiadomosci.replaceChildren(powitanie());
      rysujNoteSubskrypcji();
      rysujListeWatkow();
      if (doCzatu) {
        ustawKrok("rozmowa");
        if (window.matchMedia("(pointer: fine)").matches) pole.focus();
      }
    }

    function wybierzWatek(id) {
      zamknijStrumien();
      s.aktywny = id;
      s.widok = null;
      zapisz("bc.agent.watek", id);
      wyczyscNaZywo();
      ustawTrwa(false);
      wiadomosci.replaceChildren(ladowanie("Wczytuję rozmowę…"));
      rysujListeWatkow();
      wczytajWatek(id);
    }

    async function wczytajWatek(id, opcje = {}) {
      // Po końcu przebiegu rozmowa i lista wczytują się naraz; bez tego lista dociągała rozmowę drugi raz i nowszy
      // rysunek gubił wiersz „gotowe w …” (albo podmieniał dymki pod palcem).
      const nr = ++s.nrWczyt;
      s.wczytuje = id;
      let w;
      try {
        w = await ctx.api("/api/agent/watki/" + enc(id));
      } catch (e) {
        if (nr !== s.nrWczyt) return;
        s.wczytuje = null;
        if (id !== s.aktywny) return;
        if (e.status === 404) {
          nowaRozmowa(false);
          return;
        }
        wiadomosci.replaceChildren(stanBledu(e, "Rozmowa"));
        return;
      }
      if (nr !== s.nrWczyt) return;                          // w międzyczasie ruszyło nowsze wczytanie
      s.wczytuje = null;
      if (id !== s.aktywny) return;
      s.widok = w;
      if (s.maOkna && oknoWatku(w) !== s.okno) {             // rozmowa z innego okna (np. link z innej zakładki)
        s.okno = oknoWatku(w);
        zapisz("bc.agent.okno", s.okno);
        rysujTryby();
        rysujOkna();
      }
      tytulWatku.textContent = w.tytul || "Rozmowa";
      wyczyscNaZywo();
      const lista = w.wiadomosci || [];
      s.liczbaWiad = lista.length;
      rysujWiadomosci(lista);
      if (!lista.length) wiadomosci.appendChild(powitanie());
      if (opcje.poKoncu) wiadomosci.appendChild(el("div", { class: "wiad wiad-system" }, el("span", null, opcje.poKoncu)));
      ustawTrwa(!!w.trwa);
      rysujNoteSubskrypcji();
      rysujListeWatkow();
      naDol(true);
      if (w.trwa && !s.strumien) polacz(id, 0);
    }

    // ------------------------------------------------------------------ usuwanie i tytuł
    const OSTRZEZENIE_SYSTEMOWE = "To rozmowa założona przez panel dla sesji głosowej (notatki, ustalenia albo propozycje tematów). " +
      "Jeśli sesja jeszcze trwa, panel zacznie notatki w nowej rozmowie. Sejfu i zapisu rozmowy to nie usuwa.";

    function poUsunieciu(ids) {
      if (ids.includes(s.aktywny)) nowaRozmowa(false);
      s.watki = s.watki.filter((w) => !ids.includes(w.id));
      for (const id of ids) s.zaznaczone.delete(id);
      rysujOkna();
      rysujListeWatkow();
      wczytajWatki();
    }

    async function usunJedna(w) {
      if (!w) return;
      if (w.trwa || (w.id === s.aktywny && s.trwa)) {
        toast("Agent jeszcze pracuje w tej rozmowie — zatrzymaj go albo poczekaj na koniec.", "blad");
        return;
      }
      const tak = await potwierdz({
        tytul: "Usunąć rozmowę?",
        tresc: el("div", null,
          el("p", null, "„" + (w.tytul || "Rozmowa") + "” zniknie z panelu dla obu osób. Tego nie da się cofnąć."),
          w.systemowy ? el("p", { class: "ag-ostrzezenie" }, ikona("ostrzezenie"), el("span", null, OSTRZEZENIE_SYSTEMOWE)) : null),
      });
      if (!tak) return;
      try {
        await ctx.api("/api/agent/watki/" + enc(w.id) + "/usun", { metoda: "POST", cialo: w.systemowy ? { systemowe: true } : {} });
        toast("Usunięto rozmowę.", "ok");
        poUsunieciu([w.id]);
      } catch (e) {
        if (e.status === 404) {
          toast("Tej rozmowy już nie ma.", "info");
          poUsunieciu([w.id]);
        } else toast("Nie udało się usunąć: " + e.message, "blad");
      }
    }

    async function usunZaznaczone() {
      const ids = [...s.zaznaczone];
      if (!ids.length) return;
      const wybrane = s.watki.filter((w) => ids.includes(w.id));
      const systemowe = wybrane.filter((w) => w.systemowy).length;
      const tak = await potwierdz({
        tytul: "Usunąć " + ids.length + " " + odmiana(ids.length, ["rozmowę", "rozmowy", "rozmów"]) + "?",
        tresc: el("div", null,
          el("p", null, "Zaznaczone rozmowy znikną z panelu dla obu osób. Tego nie da się cofnąć."),
          el("ul", { class: "ag-potwierdz-lista" }, wybrane.slice(0, 8).map((w) => el("li", null, w.tytul || "Rozmowa")),
            wybrane.length > 8 ? el("li", null, "… i " + (wybrane.length - 8) + " więcej") : null),
          systemowe ? el("p", { class: "ag-ostrzezenie" }, ikona("ostrzezenie"), el("span", null, OSTRZEZENIE_SYSTEMOWE)) : null),
      });
      if (!tak) return;
      try {
        const r = await ctx.api("/api/agent/usun", { metoda: "POST", cialo: { watki: ids, systemowe: systemowe > 0 } });
        const usuniete = (r && r.usuniete) || [];
        const pominiete = (r && r.pominiete) || [];
        if (usuniete.length) toast("Usunięto: " + usuniete.length, "ok");
        if (pominiete.length) toast("Nie usunięto " + pominiete.length + ": " + (pominiete[0].blad || ""), "blad");
        s.zaznaczanie = !!pominiete.length;
        poUsunieciu(usuniete);
      } catch (e) {
        toast("Nie udało się usunąć: " + e.message, "blad");
      }
    }

    async function zmienTytul() {
      const w = s.widok;
      if (!w || tytulBtn.disabled) return;
      const poleTytulu = el("input", { class: "pole", value: w.tytul || "", maxlength: "120", "aria-label": "Tytuł rozmowy" });
      const zapiszBtn = el("button", { type: "button", class: "przycisk glowny" }, "Zapisz");
      const a = arkusz({ tytul: "Tytuł rozmowy", tresc: el("div", { class: "ag-potwierdz" }, poleTytulu, el("div", { class: "rzad-przyciskow ag-potwierdz-akcje" }, zapiszBtn)) });
      const wykonaj = async () => {
        const t = poleTytulu.value.trim();
        if (!t) return poleTytulu.focus();
        zapiszBtn.disabled = true;
        try {
          const nowy = await ctx.api("/api/agent/watki/" + enc(w.id) + "/tytul", { metoda: "POST", cialo: { tytul: t } });
          if (s.widok && s.widok.id === w.id) s.widok.tytul = nowy.tytul;
          if (s.aktywny === w.id) tytulWatku.textContent = nowy.tytul;
          a.zamknij();
          wczytajWatki();
        } catch (e) {
          toast("Nie udało się zmienić tytułu: " + e.message, "blad");
          zapiszBtn.disabled = false;
        }
      };
      zapiszBtn.addEventListener("click", wykonaj);
      poleTytulu.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          wykonaj();
        }
      });
    }

    // ------------------------------------------------------------------ wysyłanie
    async function wyslij() {
      const tekst = pole.value.trim();
      if (!tekst || s.trwa || s.wysylanie) {
        if (!tekst) pole.focus();
        return;
      }
      s.wysylanie = true;
      wyslijBtn.disabled = true;
      const kontekst = s.kontekst.slice();
      try {
        let id = s.aktywny;
        if (!id) {
          // nowy serwer: okno, a krótki tytuł nada serwer z pierwszego pytania; stary serwer: tytuł z przeglądarki
          const cialo = s.maOkna ? { okno: s.okno } : { tytul: skroc(tekst.replace(/\s+/g, " "), 60) };
          const w = await ctx.api("/api/agent/watki", { metoda: "POST", cialo });
          id = w && w.id;
          if (!id) throw new Error("Serwer nie utworzył rozmowy.");
          s.aktywny = id;
          s.widok = w;
          s.liczbaWiad = 0;
          zapisz("bc.agent.watek", id);
          tytulWatku.textContent = skroc(tekst.split("\n")[0], 48);
          wiadomosci.replaceChildren();
        }
        const pow = wiadomosci.querySelector(".agent-powitanie");
        if (pow) pow.remove();
        const tymczasowa = dymek({ rola: "user", tekst, kto: ctx.ja.kto, zdalnie: !ctx.ja.lokalny, czas: new Date().toISOString(), kontekst });
        tymczasowa.classList.add("tymczasowa");
        wiadomosci.appendChild(tymczasowa);
        naDol(true);
        const cialo = { tekst, tryb: s.trybWyslany || s.tryb || "praca" };
        if (kontekst.length) cialo.kontekst = kontekst;
        const r = await ctx.api("/api/agent/watki/" + enc(id) + "/wiadomosc", { metoda: "POST", cialo });
        tymczasowa.classList.remove("tymczasowa");
        if (r && r.nr !== undefined && r.nr !== null) tymczasowa.dataset.nr = String(r.nr);
        pole.value = "";
        dopasujPole();
        s.kontekst = [];
        rysujKontekst();
        wyczyscNaZywo();
        ustawTrwa(true);
        s.proby = 0;
        polacz(id, 0);
        wczytajWatki();
      } catch (e) {
        const tymczasowa = wiadomosci.querySelector(".wiad-user.tymczasowa");
        if (tymczasowa) tymczasowa.remove();
        if (e.status === 409) toast("Agent jeszcze pracuje w tej rozmowie — poczekaj albo kliknij Stop.", "blad");
        else if (e.status === 403) toast(e.message || "Agent jest wyłączony dla połączeń zdalnych.", "blad");
        else toast("Nie udało się wysłać: " + e.message, "blad");
      } finally {
        s.wysylanie = false;
        wyslijBtn.disabled = s.trwa;
      }
    }

    stopBtn.addEventListener("click", async () => {
      if (!s.aktywny) return;
      stopBtn.disabled = true;
      try {
        await ctx.api("/api/agent/watki/" + enc(s.aktywny) + "/stop", { metoda: "POST" });
        toast("Zatrzymuję agenta…", "info");
      } catch (e) {
        toast("Nie udało się zatrzymać: " + e.message, "blad");
      } finally {
        stopBtn.disabled = false;
      }
    });
    usunBtn.addEventListener("click", () => usunJedna(Object.assign({}, s.watki.find((w) => w.id === s.aktywny) || {}, s.widok || {}, { trwa: s.trwa })));
    tytulBtn.addEventListener("click", zmienTytul);
    wyslijBtn.addEventListener("click", wyslij);
    nowyBtn.addEventListener("click", () => nowaRozmowa(true));
    zaznaczBtn.addEventListener("click", () => {
      s.zaznaczanie = true;
      s.zaznaczone.clear();
      rysujListeWatkow();
    });
    anulujZaznBtn.addEventListener("click", () => {
      s.zaznaczanie = false;
      s.zaznaczone.clear();
      rysujListeWatkow();
    });
    usunZaznBtn.addEventListener("click", usunZaznaczone);
    pole.addEventListener("input", dopasujPole);
    pole.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
        e.preventDefault();
        wyslij();
      }
    });

    // ------------------------------------------------------------------ stan agenta (dostępność)
    function zablokuj(element) {
      blokada.replaceChildren(element);
      blokada.hidden = false;
      czat.hidden = true;
      bok.hidden = true;
      korzen.classList.add("zablokowany");
    }
    function odblokuj() {
      blokada.hidden = true;
      czat.hidden = false;
      bok.hidden = false;
      korzen.classList.remove("zablokowany");
    }

    async function sprawdzStan() {
      if (ctx.statyczny) {
        zablokuj(pusty("W podglądzie agent nie działa", "To lustro tylko do odczytu. Z agentem porozmawiasz w panelu uruchomionym na komputerze.", "oko"));
        return false;
      }
      try {
        s.stan = await ctx.api("/api/agent/stan");
      } catch (e) {
        zablokuj(e.status === 404
          ? pusty("Agent jeszcze nie jest podłączony", "Ta część serwera panelu nie wstała. Sprawdź Ustawienia → Stan systemu.", "agent")
          : stanBledu(e, "Agent"));
        return false;
      }
      const st = s.stan || {};
      if (!ctx.ja.lokalny && !st.zdalnie) {
        zablokuj(pusty("Agent z telefonu jest wyłączony",
          el("div", null,
            el("p", null, "Agent steruje komputerem, na którym działa panel, więc z innych urządzeń jest domyślnie zablokowany."),
            el("p", { class: "cichy-tekst" }, "Żeby go włączyć, na komputerze z panelem otwórz Ustawienia → Telefon i kliknij „Włącz” przy „Agent z telefonu”. Z telefonu agent pracuje najwyżej w trybie Praca.")),
          "klodka"));
        return false;
      }
      if (st.dostepny === false) {
        zablokuj(pusty("Agent jest niedostępny",
          el("div", null,
            el("p", null, st.powod || "Na komputerze z panelem nie znaleziono Claude Code."),
            el("p", { class: "cichy-tekst" }, st.podpowiedz || "Zainstaluj Claude Code i zaloguj się na swoją subskrypcję (w terminalu: claude, potem /login). Potem odśwież tę stronę.")),
          "ostrzezenie"));
        return false;
      }
      s.maOkna = Array.isArray(st.okna) && st.okna.length > 0;
      s.okna = s.maOkna ? st.okna : [OKNO_ZAPAS];
      s.funkcje = Array.isArray(st.funkcje) ? st.funkcje : [];
      if (!s.okna.some((o) => o.id === s.okno)) s.okno = s.okna[0].id;
      uwagaOkien.hidden = s.maOkna;
      uwagaOkien.textContent = s.maOkna ? "" : "Okna Balans, Świat, Modele i Wydanie oraz usuwanie rozmów ruszą po restarcie panelu na komputerze.";
      odblokuj();
      rysujTryby();
      rysujOkna();
      return true;
    }

    rysujKontekst();
    rysujTryby();
    rysujOkna();
    rysujNoteSubskrypcji();
    wiadomosci.replaceChildren(powitanie());
    let pierwszy = true;
    let stopOdpytywania = null;

    return {
      el: korzen,
      async pokaz(p) {
        p = p || {};
        const doRozmowy = !!(p.watek || (typeof p.tekst === "string" && p.tekst.trim()) || (Array.isArray(p.kontekst) && p.kontekst.length));
        if (Array.isArray(p.kontekst) && p.kontekst.length) {
          for (const k of p.kontekst) {
            if (k && k.cel && !s.kontekst.some((x) => x.typ === k.typ && x.cel === k.cel)) s.kontekst.push({ typ: k.typ, cel: k.cel, etykieta: k.etykieta || k.cel });
          }
          rysujKontekst();
        }
        if (typeof p.tekst === "string" && p.tekst.trim()) {
          pole.value = p.tekst;
          dopasujPole();
        }
        const ok = await sprawdzStan();
        if (!ok) return;
        if (p.okno && s.okna.some((o) => o.id === p.okno) && p.okno !== s.okno) {
          s.okno = p.okno;
          zapisz("bc.agent.okno", s.okno);
          rysujTryby();
          if (!p.watek) s.aktywny = null;
          pierwszy = true;
        }
        if (p.watek && p.watek !== s.aktywny) {
          s.aktywny = p.watek;
          pierwszy = true;
        }
        if (pierwszy) {
          pierwszy = false;
          await wczytajWatki();
          if (s.aktywny) wybierzWatek(s.aktywny);
          else nowaRozmowa(false);
          ustawKrok(doRozmowy ? "rozmowa" : p.okno ? "rozmowy" : "okna");
        } else {
          wczytajWatki();
          if (doRozmowy) ustawKrok("rozmowa");
          if (s.aktywny && s.trwa && !s.strumien) polacz(s.aktywny, s.ostatniN + 1);
        }
        if (!stopOdpytywania) stopOdpytywania = ctx.odpytuj(wczytajWatki, 15000);
        if ((p.tekst || (p.kontekst && p.kontekst.length)) && window.matchMedia("(pointer: fine)").matches) {
          pole.focus();
          pole.setSelectionRange(pole.value.length, pole.value.length);
        }
      },
      ukryj() {
        if (stopOdpytywania) stopOdpytywania();
        stopOdpytywania = null;
        zamknijStrumien();
      },
    };
  },
};
