// Sesja: długa rozmowa głosowa w panelu (jak na Discordzie) z agentem, który słucha, spisuje i robi notatki.
// Na górze wąski pasek pokoju (uczestnicy, Dołącz/Rozłącz, wyciszenie, miernik, „Agent słucha” ze znacznikiem
// nagrywania). Pod nim na komputerze dwie główne kolumny na wysokość okna, każda z własnym przewijaniem:
// Transkrypcja na żywo i Notatki agenta (krótkie punkty); niżej Agenda (tematy z notatki sejfu „Sesje główne”)
// i Pytania (lista „Do odpowiedzi” z zakładki Pytania, wspolne/lista_pytan.js). Na telefonie pod paskiem pokoju
// przełącznik Transkrypcja / Notatki / Agenda / Pytania (domyślnie Transkrypcja). Serwer: bc/sesje.py.
// Rozmowa trwa także po przejściu do innej zakładki panelu (obiekt rozmowy żyje w tym module).

import { el, zamien, ikona, toast, arkusz, pusty, awatar, kopiuj, odmiana, dataKrotka, przelacznik } from "../wspolne/ui.js";
import { md, mdLinia } from "../wspolne/markdown.js";
import { Rozmowa, mozliwosci } from "../wspolne/rozmowa.js";
import { listaPytan } from "../wspolne/lista_pytan.js";
import { padlyOdpowiedzi } from "../wspolne/kolejka.js";

const CSS = new URL("./sesja.css", import.meta.url).href;
const STAN_MS = 5000;
const ZAPIS_MS = 4000;
const AGENDA_MS = 30000;

const NAZWY_STANOW = {
  mowi: { tekst: "mówi", klasa: "zielen" },
  wyciszony: { tekst: "wyciszony", klasa: "" },
  bez_mikrofonu: { tekst: "bez mikrofonu", klasa: "" },
  polaczony: { tekst: "połączony", klasa: "niebieski" },
  laczenie: { tekst: "łączenie…", klasa: "zloto" },
};
const NAZWY_POLACZEN = {
  polaczony: "głos połączony", laczenie: "łączę głos…", rozlaczony: "głos zerwany — łączę ponownie",
  nieudane: "głos się nie łączy", zamkniete: "rozłączony", nowe: "łączę głos…",
};

let rozmowa = null;                                            // jedna rozmowa na kartę przeglądarki

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

function godzina(iso) {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0") + ":" +
    String(d.getSeconds()).padStart(2, "0");
}

export default {
  id: "sesja",
  tytul: "Sesja",
  ikona: "mikrofon",
  kolejnosc: 55,
  utworz(ctx) {
    dolaczCss(CSS);
    const S = {
      widoczny: false, stan: null, niedostepne: false, statyczny: !!ctx.statyczny, agenda: null, bladAgendy: null,
      wpisy: [], odWpisu: 0, sesjaZapisu: null, notatki: null, czeka: 0, trwaAkcja: false, komunikat: null,
    };

    // ------------------------------------------------------------------ szkielet
    const baner = el("div", { class: "sesja-baner", role: "status", hidden: true });
    const komunikaty = el("div", { class: "sesja-komunikaty" });
    const osoby = el("ul", { class: "lista sesja-osoby", "aria-label": "Uczestnicy rozmowy" });
    const licznikOsob = el("span", { class: "sesja-licznik-osob cichy-tekst" });
    const przyciskDolacz = el("button", { type: "button", class: "przycisk glowny sesja-dolacz" });
    const przyciskWycisz = el("button", { type: "button", class: "przycisk sesja-wycisz", hidden: true });
    const miernikWyp = el("span", { class: "sesja-miernik-wyp" });
    const miernik = el("span", { class: "sesja-miernik", hidden: true, role: "meter", "aria-label": "Poziom twojego mikrofonu",
      "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": "0" }, miernikWyp);
    const przelacznikSluchania = el("button", { type: "button", class: "sesja-slucha", role: "switch", "aria-checked": "false" });
    const opisSluchania = el("p", { class: "cichy-tekst sesja-slucha-opis" });
    // na komputerze: skróty do Agendy i Pytań (są pod dwiema głównymi kolumnami); na telefonie zastępuje je przełącznik
    const skrotAgenda = el("button", { type: "button", class: "przycisk cichy maly sesja-skrot", onclick: () => przewinDo(kAgenda) }, ikona("plan"), el("span", null, "Agenda"));
    const skrotPytania = el("button", { type: "button", class: "przycisk cichy maly sesja-skrot", onclick: () => przewinDo(kPytania) }, ikona("pytanie"), el("span", null, "Pytania"));
    const kPokoj = el("section", { class: "karta sesja-pokoj", "aria-label": "Pokój rozmowy" },
      el("div", { class: "sesja-pokoj-rzad" },
        el("h2", { class: "sesja-pokoj-tytul" }, ikona("zespol"), el("span", null, "Pokój"), licznikOsob),
        osoby,
        el("div", { class: "sesja-sterowanie" }, przyciskDolacz, przyciskWycisz, miernik, przelacznikSluchania)),
      el("div", { class: "sesja-pokoj-dol" }, opisSluchania, el("span", { class: "sesja-skroty" }, skrotAgenda, skrotPytania)));

    const agendaLista = el("div", { class: "sesja-agenda" });
    const przyciskPropozycji = el("button", { type: "button", class: "przycisk cichy maly", hidden: true }, ikona("zarowka"), "Zaproponuj tematy");
    const kAgenda = el("section", { class: "karta sesja-czesc sesja-agenda-karta" },
      el("h2", { class: "karta-tytul" }, ikona("plan"), el("span", null, "Agenda"), el("div", { class: "karta-akcje" }, przyciskPropozycji)),
      agendaLista);

    // Pytania: ta sama lista „Do odpowiedzi” co w zakładce Pytania (wspolne/lista_pytan.js), w zwartej formie —
    // żeby odpowiadać w trakcie rozmowy.
    const listaP = listaPytan(ctx, {
      zwarta: true, prefiks: "sesja-sprawa-", tytul: "Pytania",
      opis: "Te same pytania co w zakładce Pytania — odpowiadajcie w trakcie rozmowy.",
      akcjeNaglowka: el("button", { type: "button", class: "przycisk cichy maly", onclick: () => ctx.idz("pytania") }, "Wszystkie"),
      naLicznik: (n) => {
        przelacznikCzesci.licznik("pytania", n || null);
        ustawLicznikSkrotu(skrotPytania, n);
      },
    });
    const kPytania = el("section", { class: "karta sesja-czesc sesja-pytania" }, listaP.el);

    const zapisLista = el("div", { class: "sesja-zapis", role: "log", "aria-live": "polite", "aria-label": "Transkrypcja na żywo" });
    const zapisStan = el("p", { class: "cichy-tekst sesja-zapis-stan" });
    const zapisAkcje = el("div", { class: "karta-akcje" });
    const kZapis = el("section", { class: "karta sesja-czesc sesja-glowna sesja-zapis-karta" },
      el("h2", { class: "karta-tytul" }, ikona("glos"), el("span", null, "Transkrypcja na żywo"), zapisAkcje),
      zapisStan, zapisLista);

    const notatkiTresc = el("div", { class: "sesja-notatki" });
    const notatkiCzas = el("span", { class: "cichy-tekst sesja-notatki-czas" });
    const notatkiAkcje = el("div", { class: "sesja-notatki-akcje" });
    const kNotatki = el("section", { class: "karta sesja-czesc sesja-glowna sesja-notatki-karta" },
      el("h2", { class: "karta-tytul" }, ikona("notatka"), el("span", null, "Notatki agenta"), el("div", { class: "karta-akcje" }, notatkiCzas)),
      notatkiTresc, notatkiAkcje);

    // Telefon: jedna część naraz (domyślnie Transkrypcja); komputer: Transkrypcja | Notatki, pod nimi Agenda | Pytania.
    const czesci = el("div", { class: "sesja-czesci", dataset: { pokaz: "zapis" } }, kZapis, kNotatki, kAgenda, kPytania);
    const przelacznikCzesci = przelacznik([
      { id: "zapis", tekst: "Transkrypcja", ikona: "glos" }, { id: "notatki", tekst: "Notatki", ikona: "notatka" },
      { id: "agenda", tekst: "Agenda", ikona: "plan" }, { id: "pytania", tekst: "Pytania", ikona: "pytanie" },
    ], "zapis", (id) => {
      czesci.dataset.pokaz = id;
      dopasujWysokosc();
    }, "Część sesji");
    const pasekCzesci = el("div", { class: "sesja-przelacznik" }, przelacznikCzesci);

    const naglowek = el("header", { class: "nagl-widoku" }, el("div", null, el("h1", null, "Sesja"),
      el("p", { class: "cichy-tekst" }, "Rozmowa głosowa w panelu. Agent słucha, spisuje i robi krótkie notatki.")));
    const audio = el("div", { class: "sesja-audio", hidden: true });
    // Temat sesji (20.11): wybór z listy pod nagłówkiem — widzą go wszyscy, zapis przy sesji (bc/sesje.py), agent
    // sesji dostaje go jako kontekst. Stary serwer (bez pola `tematy` w stanie) — pasek ukryty.
    const tematPasek = el("section", { class: "karta sesja-temat", hidden: true, "aria-label": "Temat sesji" });
    const korzen = el("div", { class: "widok sesja" }, naglowek, tematPasek, baner, komunikaty, kPokoj, pasekCzesci, czesci, audio);

    function przewinDo(k) {
      k.scrollIntoView({ block: "start", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    }
    function ustawLicznikSkrotu(b, n) {
      let l = b.querySelector(".przelacznik-licznik");
      if (!n) {
        if (l) l.remove();
        return;
      }
      if (!l) b.append(l = el("span", { class: "przelacznik-licznik" }));
      l.textContent = String(n);
    }

    // Transkrypcja i Notatki mają wysokość do dołu okna (komputer: obie obok siebie bez przewijania strony; telefon:
    // wybrana część do dolnego paska). Wysokość liczymy z położenia kolumn, bo pasek pokoju i komunikaty zmieniają się.
    function dopasujWysokosc() {
      if (!S.widoczny || !czesci.isConnected) return;
      const nav = document.querySelector(".nav-dol");
      const dol = nav && getComputedStyle(nav).display !== "none" ? nav.getBoundingClientRect().height : 0;
      const gora = czesci.getBoundingClientRect().top + window.scrollY;
      const wys = Math.max(300, Math.floor(window.innerHeight - gora - dol - 16));
      if (czesci.style.getPropertyValue("--sesja-wys") !== wys + "px") czesci.style.setProperty("--sesja-wys", wys + "px");
    }
    window.addEventListener("resize", () => dopasujWysokosc());
    if (typeof ResizeObserver === "function") {
      const obs = new ResizeObserver(() => dopasujWysokosc());
      for (const e of [naglowek, tematPasek, baner, komunikaty, kPokoj, pasekCzesci]) obs.observe(e);
    }

    // ------------------------------------------------------------------ pomocnicze
    const ja = () => (S.stan && S.stan.ja) || { decydent: !!ctx.ja.decydent, lokalny: !!ctx.ja.lokalny, agent: false };
    const wRozmowie = () => !!(rozmowa && rozmowa.dolaczony);
    const widziZapis = () => wRozmowie() || !!ctx.ja.lokalny;
    const sluchanie = () => !!(S.stan && S.stan.sluchanie && S.stan.sluchanie.wlaczone);

    function bladTekst(e) {
      return (e && e.message) || "Nie udało się.";
    }

    // ------------------------------------------------------------------ niedostępne (stary serwer, lustro)
    function rysujNiedostepne() {
      kPokoj.classList.add("niedostepny");
      kPokoj.replaceChildren(
        el("h2", { class: "karta-tytul" }, ikona("zespol"), el("span", null, "Pokój")),
        S.statyczny
          ? pusty("Rozmowa działa tylko na żywym panelu", "To jest podgląd tylko do odczytu. Rozmowa głosowa, nagrywanie i notatki działają w panelu uruchomionym na komputerze (albo przez link tunelu).", "oko")
          : pusty("Rozmowa zacznie działać po restarcie panelu", "Serwer panelu działa jeszcze w starej wersji, która nie zna zakładki Sesja. Na komputerze z panelem zamknij okno panelu i uruchom panel\\start.bat jeszcze raz.", "info"));
      pasekCzesci.hidden = true;
      czesci.classList.add("pojedyncze");
      if (S.statyczny) {
        czesci.replaceChildren(kAgenda, kPytania);               // lustro: Agenda i Pytania jedna pod drugą
        czesci.dataset.pokaz = "wszystko";                       // żadna reguła „jedna część naraz” tego nie ukrywa
        rysujAgende();
      } else {
        czesci.replaceChildren(kPytania);                        // pytania działają też na starym serwerze
        czesci.dataset.pokaz = "pytania";
      }
    }

    // ------------------------------------------------------------------ baner nagrywania i komunikaty
    function rysujBaner() {
      const slucha = sluchanie();
      baner.hidden = !slucha;
      if (slucha) {
        const s = S.stan.sluchanie;
        zamien(baner, el("span", { class: "sesja-kropka-rec", "aria-hidden": "true" }),
          el("span", null, el("strong", null, "Agent słucha — rozmowa jest nagrywana i spisywana. "),
            el("span", { class: "sesja-baner-kto" }, "Nagrania zostają na komputerze z panelem; do sejfu trafią tylko ustalenia do zatwierdzenia." +
              (s.kto ? " Włączył(a): " + s.kto + (s.od ? ", " + dataKrotka(s.od) : "") + "." : ""))));
      }
      korzen.classList.toggle("nagrywa", slucha);
    }

    function rysujKomunikaty() {
      const lista = [];
      const m = mozliwosci();
      if (!wRozmowie() && m.powod) lista.push({ typ: "info", tekst: m.powod });
      if (rozmowa && rozmowa.mikrofonBlad && wRozmowie()) lista.push({ typ: "blad", tekst: rozmowa.mikrofonBlad });
      if (rozmowa && wRozmowie() && rozmowa.czyNieudane()) {
        lista.push({ typ: "blad", tekst: "Głosu nie udało się połączyć bezpośrednio — rozmawiajcie przez Discord, a nagrywanie i transkrypcja działają dalej (każdy wysyła własny mikrofon)." });
      }
      if (rozmowa && wRozmowie() && sluchanie() && !rozmowa.strumien) {
        lista.push({ typ: "info", tekst: "Agent nie słyszy ciebie — nie masz włączonego mikrofonu. Słyszy tylko osoby z mikrofonem." });
      }
      if (rozmowa && wRozmowie() && rozmowa.bladWysylki) lista.push({ typ: "blad", tekst: rozmowa.bladWysylki });
      if (rozmowa && wRozmowie() && rozmowa.nagrywa && !rozmowa.wyciszony && rozmowa.ciszaZRzedu >= 3) {
        lista.push({ typ: "blad", tekst: "Agent może cię nie słyszeć: od dłuższej chwili twój mikrofon jest cichy. Sprawdź, czy mówisz do właściwego mikrofonu i czy nie jest wyciszony w systemie." });
      }
      if (rozmowa && wRozmowie() && rozmowa.nagrywa && !rozmowa.miernikDziala) {
        lista.push({ typ: "info", tekst: "Miernik mikrofonu nie działa w tej przeglądarce — wysyłam agentowi całe nagranie, także ciszę." });
      }
      if (zaleglosc()) {
        lista.push({ typ: "blad", tekst: "Transkrypcja nie nadąża — czeka " + S.czeka + " " + odmiana(S.czeka, ["odcinek", "odcinki", "odcinków"]) + " i przybywa. Tekst pojawi się później; nic nie ginie, ale ustalenia na końcu mogą poczekać." });
      }
      if (S.komunikat) lista.push(S.komunikat);
      zamien(komunikaty, lista.map((k) => el("div", { class: "sesja-komunikat " + k.typ, role: k.typ === "blad" ? "alert" : "note" },
        ikona(k.typ === "blad" ? "ostrzezenie" : "info"), el("span", null, k.tekst))));
    }

    // ------------------------------------------------------------------ temat sesji
    let podpisTematu = "";
    let wybranyTemat = null;                                   // wybór w liście przed zapisem („Inne” czeka na tekst)
    function rysujTemat() {
      const st = S.stan;
      if (!st || !Array.isArray(st.tematy)) {
        tematPasek.hidden = true;
        return;
      }
      tematPasek.hidden = false;
      const t = st.temat || null;
      const moze = !!ja().decydent && !S.statyczny;
      const podpis = JSON.stringify([t, st.tematy, moze, wybranyTemat]);
      if (podpis === podpisTematu || tematPasek.contains(document.activeElement)) return;
      podpisTematu = podpis;
      const kto = t && t.kto ? "wybrał(a) " + t.kto + (t.czas ? ", " + godzina(t.czas) : "") : "";
      const otworz = t && t.adres ? el("a", { class: "przycisk cichy maly", href: t.adres }, el("span", null, "Otwórz"), ikona("prawo")) : null;
      const etykieta = el("span", { class: "etykieta sesja-temat-etykieta" }, ikona("flaga"), "Temat sesji");
      if (!moze) {
        zamien(tematPasek, etykieta, el("div", { class: "sesja-temat-rzad" },
          el("strong", { class: "sesja-temat-nazwa" }, t ? t.nazwa + (t.tekst ? ": " + t.tekst : "") : "nie wybrany"), otworz),
          el("p", { class: "cichy-tekst" }, (kto ? kto + " · " : "") + "Temat wybiera Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania)."));
        return;
      }
      const wybor = wybranyTemat !== null ? wybranyTemat : t ? t.id : "";
      // kolejność z serwera (Wytwórnia, gry, pomysły, Pytania, Inne); gry i pomysły w podpisanych grupach
      const NAZWY_GRUP = { gry: "Gry z portfela Wytwórni", "pomysły": "Pomysły z lejka Wytwórni" };
      const elementy = [];
      for (const o of st.tematy) {
        const opcja = el("option", { value: o.id, selected: o.id === wybor }, o.nazwa);
        const ostatni = elementy[elementy.length - 1];
        if (!NAZWY_GRUP[o.grupa]) elementy.push(opcja);
        else if (ostatni && ostatni.tagName === "OPTGROUP" && ostatni.dataset.grupa === o.grupa) ostatni.append(opcja);
        else elementy.push(el("optgroup", { label: NAZWY_GRUP[o.grupa], dataset: { grupa: o.grupa } }, opcja));
      }
      const lista = el("select", { class: "pole sesja-temat-lista", "aria-label": "Temat sesji" },
        el("option", { value: "" }, "— bez tematu —"), elementy);
      lista.value = wybor;
      const pole = el("input", { class: "pole sesja-temat-tekst", maxlength: "200", placeholder: "O czym rozmawiacie?", value: t && t.id === "inne" ? t.tekst || "" : "", "aria-label": "Temat — własny opis" });
      const zapiszInne = el("button", { type: "button", class: "przycisk glowny maly" }, "Zapisz");
      const inne = el("div", { class: "sesja-temat-inne", hidden: wybor !== "inne" }, pole, zapiszInne);
      lista.addEventListener("change", () => {
        if (lista.value === "inne") {
          wybranyTemat = "inne";
          inne.hidden = false;
          pole.focus();
          return;
        }
        wybranyTemat = null;
        zapiszTemat(lista.value, "");
      });
      zapiszInne.addEventListener("click", () => {
        if (!pole.value.trim()) return pole.focus();
        zapiszTemat("inne", pole.value.trim());
      });
      pole.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.isComposing) {
          e.preventDefault();
          zapiszInne.click();
        }
      });
      zamien(tematPasek, etykieta, el("div", { class: "sesja-temat-rzad" }, lista, otworz), inne,
        kto ? el("p", { class: "cichy-tekst" }, kto + " — widzą wszyscy w sesji, agent dostaje go jako kontekst.")
          : el("p", { class: "cichy-tekst" }, "Wybierz, o czym jest sesja — agent przeczyta właściwe notatki i podpowie agendę z tego tematu."));
    }

    async function zapiszTemat(id, tekst) {
      try {
        const st = await ctx.api("/api/sesje/temat", { metoda: "POST", cialo: id ? { id, tekst } : { id: "" } });
        wybranyTemat = null;
        if (st && typeof st === "object" && st.pokoj) S.stan = Object.assign({}, S.stan || {}, st, { ja: (S.stan && S.stan.ja) || st.ja });
        podpisTematu = "";
        if (document.activeElement && tematPasek.contains(document.activeElement)) document.activeElement.blur();
        rysujTemat();
        toast(id ? "Temat sesji: " + ((st.temat && st.temat.nazwa) || id) + "." : "Sesja bez tematu.", "ok");
      } catch (e) {
        toast(e.status === 404 ? "Temat sesji zadziała po restarcie panelu." : bladTekst(e), "blad");
      }
    }

    // ------------------------------------------------------------------ pokój
    function rysujPokoj() {
      const st = S.stan;
      const lista = (st && st.pokoj && st.pokoj.uczestnicy) || [];
      const max = (st && st.pokoj && st.pokoj.max_osob) || 6;
      licznikOsob.textContent = lista.length + "/" + max;
      const moje = rozmowa && wRozmowie() ? rozmowa.stanyPolaczen() : new Map();
      const mojId = rozmowa && wRozmowie() ? rozmowa.u : null;
      if (!lista.length) {
        zamien(osoby, el("li", { class: "sesja-osoba-pusto cichy-tekst" }, "Nikogo nie ma w rozmowie. Dołącz — druga osoba wejdzie przez swój link do panelu."));
      } else {
        zamien(osoby, lista.map((o) => {
          const ty = o.id && o.id === mojId;
          const stanOsoby = ty && rozmowa ? (rozmowa.wyciszony ? "wyciszony" : !rozmowa.strumien ? "bez_mikrofonu" : rozmowa.mowi ? "mowi" : o.stan) : o.stan;
          const opis = NAZWY_STANOW[stanOsoby] || { tekst: stanOsoby, klasa: "" };
          const pol = o.id && !ty ? moje.get(o.id) : null;
          const rola = o.rola === "gość" ? "gość" : o.rola === "przy komputerze" ? "przy komputerze z panelem" : "klucz zatwierdzania";
          return el("li", { class: "wiersz sesja-osoba" + (stanOsoby === "mowi" ? " mowi" : ""), title: o.kto + " — " + rola,
            dataset: { uczestnik: o.id || "", stan: stanOsoby, polaczenie: pol || "" } },
            awatar(o.kto, { maly: true }),
            el("span", { class: "wiersz-tekst" },
              el("strong", null, o.kto + (ty ? " (ty)" : "")),
              el("span", { class: "cichy-tekst" }, opis.tekst, pol ? " · " + (NAZWY_POLACZEN[pol] || pol) : "")));
        }));
      }
      // przyciski
      const pelny = lista.length >= max && !wRozmowie();
      przyciskDolacz.replaceChildren(ikona(wRozmowie() ? "zamknij" : "mikrofon"), el("span", null, wRozmowie() ? "Rozłącz" : "Dołącz"));
      przyciskDolacz.classList.toggle("glowny", !wRozmowie());
      przyciskDolacz.classList.toggle("grozny", wRozmowie());
      przyciskDolacz.disabled = S.trwaAkcja || pelny;
      przyciskDolacz.title = pelny ? "Pokój jest pełny" : "";
      const zMikrofonem = wRozmowie() && rozmowa.strumien;
      przyciskWycisz.hidden = !zMikrofonem;
      miernik.hidden = !zMikrofonem;
      if (zMikrofonem) {
        przyciskWycisz.replaceChildren(ikona(rozmowa.wyciszony ? "mikrofon" : "stop"), el("span", null, rozmowa.wyciszony ? "Włącz mikrofon" : "Wycisz"));
        przyciskWycisz.setAttribute("aria-pressed", rozmowa.wyciszony ? "true" : "false");
        przyciskWycisz.classList.toggle("wyciszony", rozmowa.wyciszony);
      }
      // agent słucha
      const slucha = sluchanie();
      const moze = !!ja().decydent && !S.statyczny;
      przelacznikSluchania.setAttribute("aria-checked", slucha ? "true" : "false");
      przelacznikSluchania.disabled = !moze || S.trwaAkcja;
      przelacznikSluchania.replaceChildren(el("span", { class: "sesja-slucha-suwak", "aria-hidden": "true" }),
        el("span", null, "Agent słucha"));
      opisSluchania.textContent = moze
        ? (slucha ? "Każdy nagrywa swój mikrofon; serwer spisuje to lokalnie i usuwa dźwięk po transkrypcji."
          : "Włącz „Agent słucha”, żeby agent spisywał rozmowę i robił notatki. Wszyscy zobaczą czerwony znacznik.")
        : "„Agent słucha” włącza Karol albo Paweł (przy komputerze z panelem albo z kluczem zatwierdzania).";
      rysujBaner();
      rysujKomunikaty();
      rysujTemat();
      dopasujWysokosc();
    }

    function rysujMiernik() {
      if (!rozmowa || !wRozmowie() || miernik.hidden) return;
      const p = Math.min(100, Math.round(Math.sqrt(rozmowa.poziom) * 220));
      miernikWyp.style.width = p + "%";
      miernik.setAttribute("aria-valuenow", String(p));
      miernik.classList.toggle("mowi", rozmowa.mowi);
    }
    setInterval(() => { if (S.widoczny) rysujMiernik(); }, 120);

    async function dolaczAlboRozlacz() {
      if (S.trwaAkcja) return;
      S.trwaAkcja = true;
      rysujPokoj();
      try {
        if (wRozmowie()) {
          await rozmowa.rozlacz();
          toast("Rozłączono.", "info");
          await odswiezStan();
        } else {
          if (!rozmowa) {
            rozmowa = new Rozmowa({
              api: ctx.api, kontenerAudio: document.body,
              naStan: (st) => {
                if (st) S.stan = st;
                rysujPokoj();
              },
              naKomunikat: (t, typ) => toast(t, typ),
            });
          }
          await rozmowa.dolacz();
          toast(rozmowa.strumien ? "Jesteś w rozmowie." : "Jesteś w rozmowie (bez mikrofonu).", rozmowa.strumien ? "ok" : "info");
          odswiezZapis();
        }
      } catch (e) {
        if (rozmowa && !rozmowa.dolaczony) {
          try { await rozmowa.rozlacz(); } catch (e2) { /* nic */ }
        }
        toast(e.status === 404 ? "Rozmowa zacznie działać po restarcie panelu." : "Nie udało się dołączyć: " + bladTekst(e), "blad");
      } finally {
        S.trwaAkcja = false;
        rysujPokoj();
        rysujZapis();
        rysujNotatki();
      }
    }
    przyciskDolacz.addEventListener("click", dolaczAlboRozlacz);
    przyciskWycisz.addEventListener("click", () => {
      if (!rozmowa) return;
      rozmowa.wycisz(!rozmowa.wyciszony);
      rysujPokoj();
    });

    przelacznikSluchania.addEventListener("click", async () => {
      if (S.trwaAkcja || !ja().decydent) return;
      const wlacz = !sluchanie();
      S.trwaAkcja = true;
      rysujPokoj();
      try {
        const st = await ctx.api("/api/sesje/sluchanie", { metoda: "POST", cialo: { wlacz } });
        // w rozmowie: nowy stan słuchania od razu do obiektu rozmowy (zacznie albo przestanie nagrywać);
        // lista uczestników z adresami zostaje z ostatniego pulsu
        if (rozmowa && wRozmowie()) rozmowa._przyjmijStan(Object.assign({}, rozmowa.stan || {}, { sluchanie: st.sluchanie, sesja: st.sesja }));
        else S.stan = st;
        toast(wlacz ? "Agent słucha — rozmowa jest spisywana." : "Agent przestał słuchać.", "ok");
      } catch (e) {
        toast(bladTekst(e), "blad");
      } finally {
        S.trwaAkcja = false;
        rysujPokoj();
        rysujNotatki();
      }
    });

    // ------------------------------------------------------------------ agenda
    function rysujAgende() {
      const a = S.agenda;
      przyciskPropozycji.hidden = !(ja().agent && !S.statyczny);
      if (S.bladAgendy) {
        zamien(agendaLista, pusty(S.bladAgendy.status === 404 ? "Agenda zacznie działać po restarcie panelu" : "Nie udało się wczytać agendy",
          S.bladAgendy.status === 404 ? "Tematy są w notatce sejfu Sesje główne (Produkcja)." : bladTekst(S.bladAgendy), "info"));
        return;
      }
      if (!a) {
        zamien(agendaLista, el("p", { class: "cichy-tekst" }, "Wczytuję tematy…"));
        return;
      }
      const moznaPisac = !S.statyczny && ja().zapis_sejfu !== false && ctx.ja.zapis_sejfu !== false;
      const tematy = a.do_omowienia || [];
      przelacznikCzesci.licznik("agenda", tematy.length || null);
      ustawLicznikSkrotu(skrotAgenda, tematy.length);
      const lista = tematy.length
        ? el("ul", { class: "lista sesja-lista-tematow" }, tematy.map((t) => el("li", { class: "sesja-temat", dataset: { temat: t.id } },
          el("div", { class: "sesja-temat-tresc" },
            el("strong", { class: "md-linia", html: mdLinia(t.temat || t.tekst_md) }),
            t.kontekst ? el("span", { class: "cichy-tekst md-linia", html: mdLinia(t.kontekst) }) : null,
            el("span", { class: "sesja-temat-meta" },
              t.propozycja_agenta ? el("span", { class: "chip fiolet maly-chip" }, "propozycja agenta") : null,
              t.dodal ? el("span", { class: "cichy-tekst" }, "dodał: " + t.dodal + (t.data ? ", " + t.data : "")) : null)),
          moznaPisac ? el("button", { type: "button", class: "przycisk cichy maly", onclick: () => oknoOmowienia(t) }, ikona("ok"), "Omówione") : null)))
        : pusty("Nie ma tematów do omówienia", "Dodaj temat albo poproś agenta o propozycje.", "plan");
      const omowione = a.omowione || [];
      const zwinieteOmowione = omowione.length ? el("details", { class: "sesja-omowione" },
        el("summary", null, "Omówione (" + omowione.length + ")"),
        el("ul", { class: "lista" }, omowione.map((t) => el("li", { class: "sesja-temat omowiony" },
          el("div", { class: "sesja-temat-tresc" },
            el("span", { class: "md-linia", html: mdLinia(t.temat || t.tekst_md) }),
            t.omowione ? el("span", { class: "cichy-tekst" }, t.omowione.data + (t.omowione.wynik ? " — " + t.omowione.wynik : "")) : null))))) : null;
      zamien(agendaLista, lista, moznaPisac ? formularzTematu() : null, zwinieteOmowione,
        el("p", { class: "cichy-tekst sesja-zrodlo" }, "Źródło: ", el("a", { href: "#/siec", "data-wikilink": "Sesje główne" }, "Sesje główne"), " w sejfie."));
    }

    let szkicTematu = "";
    function formularzTematu() {
      const pole = el("input", { class: "pole", placeholder: "Nowy temat na sesję", maxlength: "200", "aria-label": "Nowy temat", value: szkicTematu });
      const kontekst = el("input", { class: "pole", placeholder: "Dlaczego warto o tym pogadać (opcjonalnie)", maxlength: "500", "aria-label": "Kontekst tematu" });
      const przycisk = el("button", { type: "submit", class: "przycisk maly" }, ikona("plus"), "Dodaj");
      pole.addEventListener("input", () => { szkicTematu = pole.value; });
      const f = el("form", { class: "sesja-nowy-temat" }, pole, kontekst, przycisk);
      f.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!pole.value.trim() || przycisk.disabled) return;
        przycisk.disabled = true;
        try {
          const w = await ctx.api("/api/sesje/agenda/dodaj", { metoda: "POST", cialo: { temat: pole.value, kontekst: kontekst.value, wersja: S.agenda && S.agenda.wersja } });
          szkicTematu = "";
          S.agenda = w.agenda;
          toast("Temat dopisany do agendy.", "ok");
          rysujAgende();
        } catch (er) {
          toast(bladTekst(er), "blad");
          if (er.status === 409) odswiezAgende();
          przycisk.disabled = false;
        }
      });
      return f;
    }

    function oknoOmowienia(t) {
      const wynik = el("textarea", { class: "pole", rows: "3", maxlength: "500", placeholder: "Krótki wynik rozmowy (opcjonalnie), np. „trzy poziomy trudności”" });
      const zapisz = el("button", { type: "submit", class: "przycisk glowny szeroki" }, "Oznacz jako omówiony");
      const wersja = S.agenda && S.agenda.wersja;
      const form = el("form", { class: "formularz" },
        el("p", null, el("strong", { class: "md-linia", html: mdLinia(t.temat || t.tekst_md) })),
        el("p", { class: "cichy-tekst" }, "Temat przejdzie do sekcji „Omówione” w notatce Sesje główne, z dzisiejszą datą i twoim podpisem."),
        el("label", { class: "etykieta" }, "Wynik"), wynik, zapisz);
      const ark = arkusz({ tytul: "Temat omówiony", tresc: form });
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (zapisz.disabled) return;
        zapisz.disabled = true;
        try {
          const w = await ctx.api("/api/sesje/agenda/omowione", { metoda: "POST", cialo: { id: t.id, wynik: wynik.value, wersja } });
          S.agenda = w.agenda;
          ark.zamknij();
          toast("Oznaczono jako omówiony.", "ok");
          rysujAgende();
        } catch (er) {
          zapisz.disabled = false;
          if (er.status === 409 && er.dane && er.dane.kod === "konflikt_wersji") {
            ark.zamknij();
            toast("Ktoś zmienił agendę — odświeżam. Spróbuj jeszcze raz.", "blad");
            odswiezAgende();
          } else toast(bladTekst(er), "blad");
        }
      });
    }

    przyciskPropozycji.addEventListener("click", async () => {
      if (przyciskPropozycji.disabled) return;
      przyciskPropozycji.disabled = true;
      try {
        const r = await ctx.api("/api/sesje/agenda/zaproponuj", { metoda: "POST", cialo: {} });
        toast("Agent przegląda pytania, decyzje i dziennik — nowe tematy pojawią się na liście za kilka minut.", "ok",
          r.watek && ctx.ja.lokalny ? { akcja: { tekst: "Zobacz", fn: () => ctx.idz("agent", { watek: r.watek }) }, czas: 8000 } : {});
      } catch (e) {
        toast(bladTekst(e), "blad");
      } finally {
        setTimeout(() => { przyciskPropozycji.disabled = false; }, 4000);
      }
    });

    // ------------------------------------------------------------------ transkrypcja
    function rysujZapis() {
      zapisAkcje.replaceChildren();
      if (!widziZapis()) {
        zapisStan.textContent = "";
        zamien(zapisLista, pusty("Zapis rozmowy widzą osoby w pokoju", "Dołącz do rozmowy, żeby zobaczyć transkrypcję na żywo.", "klodka"));
        return;
      }
      const sesja = S.stan && S.stan.sesja;
      if (ctx.ja.lokalny && (S.wpisy.length || sesja)) {
        zapisAkcje.append(
          el("a", { class: "przycisk cichy maly", href: "/api/sesje/pobierz", download: "", title: "Pobierz pełny zapis (tylko na tym komputerze)" }, ikona("pobierz"), "Pobierz"),
          el("button", { type: "button", class: "przycisk cichy maly", onclick: async () => {
            const tekst = S.wpisy.map((w) => "[" + godzina(w.t) + "] " + w.kto + ": " + w.tekst).join("\n");
            toast((await kopiuj(tekst)) ? "Skopiowano zapis rozmowy." : "Nie udało się skopiować.", "info");
          } }, ikona("kopiuj"), "Kopiuj"));
      }
      const opis = [];
      if (sluchanie()) opis.push("Agent słucha. Tekst pojawia się z opóźnieniem kilkunastu sekund.");
      else opis.push(sesja ? "Agent nie słucha — nic nowego nie jest zapisywane." : "Agent nie słucha. Włącz „Agent słucha”, żeby zacząć zapis.");
      if (S.czeka) opis.push("Czeka na spisanie: " + S.czeka + " " + odmiana(S.czeka, ["odcinek", "odcinki", "odcinków"]) + ".");
      if (rozmowa && rozmowa.nagrywa) opis.push("Nagrywam twój mikrofon (wysłane odcinki: " + rozmowa.wyslane + ", pominięte jako cisza: " + rozmowa.pominiete + ").");
      zapisStan.textContent = opis.join(" ");
      if (!S.wpisy.length) {
        zamien(zapisLista, el("p", { class: "cichy-tekst sesja-zapis-pusto" }, "Jeszcze nic nie zostało spisane."));
        return;
      }
      const naDole = zapisLista.scrollHeight - zapisLista.scrollTop - zapisLista.clientHeight < 60;
      zamien(zapisLista, S.wpisy.map((w) => el("div", { class: "sesja-wpis", dataset: { n: String(w.n) } },
        el("span", { class: "sesja-wpis-czas" }, godzina(w.t)),
        el("strong", { class: "sesja-wpis-kto" }, w.kto + ":"),
        el("span", { class: "sesja-wpis-tekst" }, w.tekst))));
      if (naDole || S.przewin) zapisLista.scrollTop = zapisLista.scrollHeight;
      S.przewin = false;
    }

    // Zaległość transkrypcji: ostrzegamy, gdy kolejka „czeka na spisanie” jest spora i przez ostatnią minutę rosła.
    const historiaCzeka = [];
    function zapamietajZaleglosc(n) {
      const teraz = Date.now();
      historiaCzeka.push({ t: teraz, n });
      while (historiaCzeka.length && teraz - historiaCzeka[0].t > 150000) historiaCzeka.shift();
    }
    function zaleglosc() {
      if (!sluchanie() || S.czeka < 4 || historiaCzeka.length < 3) return false;
      const teraz = Date.now();
      const sprzed = historiaCzeka.filter((x) => teraz - x.t >= 60000);
      if (!sprzed.length) return false;
      return S.czeka >= sprzed[sprzed.length - 1].n + 2;
    }

    async function odswiezZapis() {
      if (S.niedostepne || S.statyczny || !widziZapis()) {
        rysujZapis();
        rysujNotatki();
        return;
      }
      try {
        const cialo = { od: S.odWpisu };
        if (wRozmowie()) Object.assign(cialo, { u: rozmowa.u, k: rozmowa.k });
        const o = await ctx.api("/api/sesje/transkrypcja", { metoda: "POST", cialo, czas: 15000 });
        if (o.sesja !== S.sesjaZapisu) {
          S.sesjaZapisu = o.sesja;
          S.wpisy = [];
          S.odWpisu = 0;
          S.przewin = true;
          if (o.sesja && cialo.od) return odswiezZapis();      // nowa sesja: wczytaj od początku
        }
        if (o.wpisy && o.wpisy.length) {
          S.wpisy = S.wpisy.concat(o.wpisy).sort((a, b) => (a.t < b.t ? -1 : a.t > b.t ? 1 : a.n - b.n));
          S.odWpisu = Math.max(S.odWpisu, ...o.wpisy.map((w) => w.n));
        }
        S.czeka = o.czeka || 0;
        zapamietajZaleglosc(S.czeka);
        S.notatki = o.notatki || null;
      } catch (e) {
        if (e.status === 410 || e.status === 400) { /* poza pokojem: pokaż zachętę */ }
      }
      rysujZapis();
      rysujNotatki();
    }

    // ------------------------------------------------------------------ notatki i koniec sesji
    function rysujNotatki() {
      const sesja = S.stan && S.stan.sesja;
      const nt = S.notatki;
      notatkiCzas.textContent = widziZapis() && nt ? (nt.trwa ? "aktualizuję…" : nt.czas && nt.tekst_md ? godzina(nt.czas).slice(0, 5) : "") : "";
      notatkiCzas.title = widziZapis() && nt && nt.czas ? "Zaktualizowane: " + dataKrotka(nt.czas) : "";
      if (!widziZapis()) {
        zamien(notatkiTresc, el("p", { class: "cichy-tekst sesja-notatki-pusto" }, "Notatki agenta widzą osoby w pokoju — dołącz do rozmowy."));
      } else if (nt && nt.tekst_md) {
        // krótkie punkty w sekcjach (bc/sesje.py: polecenie_notatek); starsze, dłuższe notatki też się pokażą
        zamien(notatkiTresc, el("div", { class: "md sesja-notatki-md", html: md(nt.tekst_md) }));
      } else {
        const co = (S.stan && S.stan.notatki_co_min) || 0;
        zamien(notatkiTresc, el("p", { class: "cichy-tekst sesja-notatki-pusto" }, nt && nt.trwa ? "Agent pisze pierwsze notatki — pojawią się tu za kilka minut."
          : co ? "Pierwsze notatki pojawią się ok. " + co + " min po włączeniu „Agent słucha”, potem co " + co + " min."
            : "Notatki robi agent na przycisk „Notatki teraz” — pojawi się, gdy agent słucha."));
      }
      if (nt && nt.blad && widziZapis()) notatkiTresc.append(el("p", { class: "cichy-tekst sesja-blad-notatek" }, "Ostatnia próba notatek: " + nt.blad));
      // „Padły odpowiedzi na pytania” z notatek → podpowiedź „Na sesji padło: …” przy kartach na liście Pytania obok
      // (wspolne/lista_pytan.js: ustawPodpowiedzi; widzą ją tylko osoby, które widzą notatki)
      listaP.ustawPodpowiedzi(widziZapis() && nt && nt.tekst_md ? padlyOdpowiedzi(nt.tekst_md) : new Map(), nt && nt.czas);
      const zak = S.stan && S.stan.zakonczenie;
      const akcje = [];
      if (sesja && ja().agent) {
        akcje.push(el("button", { type: "button", class: "przycisk maly", disabled: !!(nt && nt.trwa), onclick: notatkiTeraz }, ikona("odswiez"), "Notatki teraz"));
      }
      if (sesja && ja().decydent) {
        akcje.push(el("button", { type: "button", class: "przycisk grozny maly", onclick: oknoKonca }, ikona("flaga"), "Zakończ sesję i spisz ustalenia"));
      }
      if (!sesja && zak) {
        const opis = zak.stan === "czeka_na_transkrypcje" ? "Sesja zakończona — czekam na ostatnie odcinki" + (zak.czeka ? " (do spisania: " + zak.czeka + ")" : "") + ", potem agent spisze ustalenia."
          : zak.stan === "agent" ? "Sesja zakończona — agent spisuje ustalenia do sejfu jako propozycje i dopisuje odpowiedzi, które padły. Lista do zatwierdzenia pojawi się w zakładce Pytania." +
            (zak.brakujace ? " Uwaga: transkrypcja nie nadążyła — " + zak.brakujace + " " + odmiana(zak.brakujace, ["odcinek", "odcinki", "odcinków"]) + " nie trafiło do ustaleń (agent zaznaczy, że zapis jest niepełny)." : "")
            : zak.stan === "bez_spisywania" ? "Sesja zakończona bez spisywania ustaleń."
              : "Sesja zakończona, ale spisanie się nie udało: " + (zak.blad || "nieznany błąd") + ".";
        akcje.push(el("p", { class: "cichy-tekst" }, opis),
          zak.stan === "agent" ? el("button", { type: "button", class: "przycisk cichy maly", onclick: () => ctx.idz("pytania") }, ikona("pytanie"), "Pytania") : null,
          zak.watek && ctx.ja.lokalny ? el("button", { type: "button", class: "przycisk cichy maly", onclick: () => ctx.idz("agent", { watek: zak.watek }) }, ikona("agent"), "Zobacz pracę agenta") : null);
      }
      zamien(notatkiAkcje, akcje);
    }

    async function notatkiTeraz() {
      try {
        await ctx.api("/api/sesje/notatki", { metoda: "POST", cialo: {} });
        toast("Agent aktualizuje notatki — to potrwa kilka minut.", "ok");
        S.notatki = Object.assign({}, S.notatki || {}, { trwa: true });
        rysujNotatki();
      } catch (e) {
        toast(bladTekst(e), "blad");
      }
    }

    function oknoKonca() {
      const zAgentem = !!ja().agent;
      const spisz = el("button", { type: "button", class: "przycisk glowny szeroki", disabled: !zAgentem }, "Zakończ i spisz ustalenia");
      const bez = el("button", { type: "button", class: "przycisk cichy szeroki" }, "Zakończ bez spisywania");
      const tresc = el("div", { class: "formularz" },
        el("p", null, "Agent przestanie słuchać. Po spisaniu ostatnich odcinków zapisze w sejfie notatkę z ustaleniami (status: propozycja), dopisze ustalenia jako propozycje do Rejestru decyzji, odpowiedzi, które padły w rozmowie, pod pytaniami, nowe pytania do Pytań otwartych i zadania do Zadań, oznaczy omówione tematy i wyśle raport z listą rzeczy do zatwierdzenia."),
        el("p", { class: "cichy-tekst" }, "Agent niczego nie zatwierdza — zatwierdza Karol albo Paweł jednym kliknięciem w panelu."),
        zAgentem ? null : el("p", { class: "cichy-tekst" }, "Spisanie uruchamia agenta na komputerze z panelem — zrób to przy tym komputerze albo włącz tam „Agent z telefonu”."),
        spisz, bez);
      const ark = arkusz({ tytul: "Zakończyć sesję?", tresc });
      const zakoncz = async (czySpisac) => {
        spisz.disabled = bez.disabled = true;
        try {
          await ctx.api("/api/sesje/zakoncz", { metoda: "POST", cialo: { spisz: czySpisac } });
          ark.zamknij();
          toast(czySpisac ? "Sesja zakończona — agent spisze ustalenia." : "Sesja zakończona.", "ok");
          S.wpisy = [];
          S.odWpisu = 0;
          S.notatki = null;
          await odswiezStan();
        } catch (e) {
          spisz.disabled = !zAgentem;
          bez.disabled = false;
          toast(bladTekst(e), "blad");
        }
      };
      spisz.addEventListener("click", () => zakoncz(true));
      bez.addEventListener("click", () => zakoncz(false));
    }

    // ------------------------------------------------------------------ odświeżanie
    async function odswiezStan() {
      if (S.statyczny) return;
      if (wRozmowie()) {                                       // w rozmowie stan przychodzi z pulsu
        rysujPokoj();
        return;
      }
      try {
        S.stan = await ctx.api("/api/sesje/stan", { czas: 10000 });
        if (S.niedostepne) {
          S.niedostepne = false;
          location.reload();                                   // serwer już zna Sesję (po restarcie panelu)
          return;
        }
      } catch (e) {
        if (e.status === 404 && !S.niedostepne) {
          S.niedostepne = true;
          rysujNiedostepne();
        }
        return;
      }
      rysujPokoj();
    }

    async function odswiezAgende() {
      try {
        S.agenda = await ctx.api("/api/sesje/agenda", { czas: 15000 });
        S.bladAgendy = null;
      } catch (e) {
        S.bladAgendy = e;
      }
      rysujAgende();
    }

    ctx.odpytuj(() => { if (S.widoczny) odswiezStan(); }, STAN_MS);   // także po 404: wykryje restart panelu
    ctx.odpytuj(() => { if (S.widoczny && !S.niedostepne) odswiezZapis(); }, ZAPIS_MS);
    ctx.odpytuj(() => { if (S.widoczny) odswiezAgende(); }, AGENDA_MS);

    return {
      el: korzen,
      async pokaz() {
        S.widoczny = true;
        listaP.pokaz();
        if (S.statyczny) {
          rysujNiedostepne();
          await odswiezAgende();
          return;
        }
        rysujPokoj();
        rysujAgende();
        rysujZapis();
        rysujNotatki();
        requestAnimationFrame(() => dopasujWysokosc());
        await odswiezStan();
        if (S.niedostepne) return;
        await Promise.all([odswiezAgende(), odswiezZapis()]);
        dopasujWysokosc();
      },
      ukryj() {
        S.widoczny = false;                                    // rozmowa trwa dalej w tle (jak na Discordzie)
        listaP.ukryj();
      },
    };
  },
};
