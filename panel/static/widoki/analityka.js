// Analityka — gracze, wizyty, oceny (publiczne API Roblox), telemetria gry (sesje, Robuxy, błędy, serwery na żywo
// z modułu w grze przez Open Cloud), stan Roblox Studio i konsola.
// Odświeżanie co 30 s (telemetria co 5 min — tyle serwer pamięta odpowiedź), tylko gdy widok jest widoczny.

import { ikona, ladowanie, pusty, przelacznik, czasTrwania } from "../wspolne/ui.js";

const CSS = new URL("./analityka.css", import.meta.url).href;
const ODSWIEZ_MS = 30000;
// Dokładnie ten napis jest kluczem pliku w lustrze tylko do odczytu (bc/statyczny.py) — zmieniaj w obu miejscach.
const TELEMETRIA = "/api/telemetria?godzin=24";
const ODSWIEZ_TELEMETRIE_MS = 5 * 60 * 1000;
// Co pokazuje wykres godzinowy: pole z /api/telemetria → godziny[], podpis i odmiana jednostki.
const METRYKI = [
  { id: "sesje", tekst: "Sesje", opis: "sesje rozpoczęte w godzinie", jednostka: ["sesja", "sesje", "sesji"], pusto: "W tym okresie nikt nie wszedł do gry." },
  { id: "ccu_max", tekst: "Gracze", opis: "najwięcej graczy naraz w godzinie", jednostka: ["gracz naraz", "graczy naraz", "graczy naraz"], pusto: "W tym okresie na serwerach nie było graczy." },
  { id: "robuxy", tekst: "Robuxy", opis: "Robuxy wydane w godzinie", jednostka: ["R$", "R$", "R$"], pusto: "W tym okresie nikt nic nie kupił." },
  { id: "bledy", tekst: "Błędy", opis: "błędy skryptów w godzinie", jednostka: ["błąd", "błędy", "błędów"], pusto: "W tym okresie nie było błędów skryptów." },
];
// Przedziały długości sesji — te same nazwy co w grze (Agregator.luau: przedzial_sesji).
const PRZEDZIALY_SESJI = [
  { id: "do_1", tekst: "do 1 min" }, { id: "do_5", tekst: "1–5 min" }, { id: "do_15", tekst: "5–15 min" },
  { id: "do_30", tekst: "15–30 min" }, { id: "do_60", tekst: "30–60 min" }, { id: "ponad_60", tekst: "ponad 1 godz." },
];

function el(tag, at, ...dzieci) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(at || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const d of dzieci.flat()) if (d != null && d !== false) e.append(d.nodeType ? d : String(d));
  return e;
}
const SVGNS = "http://www.w3.org/2000/svg";
function s(tag, at) {
  const e = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(at || {})) if (v != null) e.setAttribute(k, v);
  return e;
}

function dolaczCss(href) {
  if (![...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) {
    document.head.append(el("link", { rel: "stylesheet", href }));
  }
}

const liczba = (n) => (n == null || isNaN(n) ? "—" : Number(n).toLocaleString("pl-PL"));
function krotko(n) {
  if (n == null || isNaN(n)) return "—";
  if (n >= 1e6) return (n / 1e6).toLocaleString("pl-PL", { maximumFractionDigits: 1 }) + " mln";
  if (n >= 1e4) return (n / 1e3).toLocaleString("pl-PL", { maximumFractionDigits: 1 }) + " tys.";
  return liczba(n);
}
function czasTemu(iso) {
  const t = typeof iso === "number" ? iso : Date.parse(iso);
  if (!t) return "";
  const s = (Date.now() - t) / 1000;
  if (s < 45) return "przed chwilą";
  if (s < 3600) return Math.max(1, Math.round(s / 60)) + " min temu";
  if (s < 86400) return Math.round(s / 3600) + " h temu";
  return new Date(t).toLocaleString("pl-PL", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}
// odmiana polska: 1 błąd, 2–4 błędy, 5+ błędów (12–14 też „błędów”)
function odmiana(n, jeden, kilka, wiele) {
  n = Math.abs(Number(n) || 0);
  if (n === 1) return jeden;
  const j = n % 10, d = n % 100;
  return j >= 2 && j <= 4 && (d < 12 || d > 14) ? kilka : wiele;
}
function czasPunktu(t) {
  if (typeof t === "number") return t < 1e12 ? t * 1000 : t;
  return Date.parse(t) || 0;
}

export default {
  id: "analityka",
  tytul: "Analityka",
  ikona: "analityka",
  kolejnosc: 70,
  utworz(ctx) {
    dolaczCss(CSS);
    const S = { widoczny: false, dane: null, timer: 0, trwa: false, blad: null };
    // telemetria gry: osobne żądanie i osobny rytm odświeżania
    const T = { dane: null, blad: null, trwa: false, kiedy: 0, probka: false, metryka: "sesje", tabela: false, wykres: null, ro: null, schowajDymek: null };

    const aktualizacja = el("span", { class: "cichy-tekst an-akt" });
    const odswiezBtn = el("button", { class: "przycisk cichy ikonowy", type: "button", "aria-label": "Odśwież", title: "Odśwież", onclick: () => { wczytaj(true); wczytajTelemetrie(true); } }, ikona("odswiez"));
    const gra = el("div", { class: "an-gra" });
    const wykres = el("div", { class: "karta an-wykres-karta" });
    const telemetria = el("section", { class: "an-tel", "aria-label": "Telemetria gry" });
    const studio = el("div", { class: "karta an-studio" });
    const root = el("section", { class: "an" },
      el("header", { class: "an-gora" }, el("div", {}, el("h1", { class: "an-tytul", text: "Analityka" }), aktualizacja), odswiezBtn),
      gra, wykres, telemetria, studio);

    async function wczytaj(recznie) {
      if (S.trwa) return;
      S.trwa = true;
      if (recznie) odswiezBtn.disabled = true;
      try {
        S.dane = await ctx.api("/api/analityka");
        S.blad = null;
      } catch (e) {
        S.blad = e.message || "błąd";
      } finally {
        S.trwa = false;
        odswiezBtn.disabled = false;
      }
      rysuj();
    }

    function kafel(tytul, wartosc, pod, klasa) {
      return el("div", { class: "karta an-kafel" + (klasa ? " " + klasa : "") },
        el("div", { class: "an-kafel-tytul cichy-tekst", text: tytul }),
        el("div", { class: "an-kafel-wartosc", text: wartosc }),
        pod ? (pod.nodeType ? pod : el("div", { class: "an-kafel-pod cichy-tekst", text: pod })) : null);
    }

    function rysuj() {
      const d = S.dane;
      if (!d) {
        gra.replaceChildren(S.blad
          ? pusty("Nie udało się pobrać analityki", el("div", { class: "an-blad" },
            el("p", { text: S.blad }),
            el("button", { class: "przycisk", type: "button", onclick: () => wczytaj(true) }, ikona("odswiez"), "Spróbuj ponownie")), "ostrzezenie")
          : ladowanie("Wczytuję analitykę…"));
        wykres.hidden = studio.hidden = true;
        return;
      }
      wykres.hidden = studio.hidden = false;
      const g = d.gra || {};
      aktualizacja.textContent = (g.nazwa ? g.nazwa + " · " : "") + (g.zaktualizowano ? "dane z Roblox " + czasTemu(g.zaktualizowano) : "") +
        (S.blad ? " · ostatnie odświeżenie nie wyszło" : "");

      // ---- gra: kafle albo czytelny stan, gdy statystyk nie ma
      const niedostepna = g.publiczna === false || (g.blad && !g.wizyty && !g.gracze);
      if (niedostepna) {
        gra.replaceChildren(el("div", { class: "karta an-stan" },
          el("div", { class: "pusty-ikona an-stan-ikona" }, ikona("klodka")),
          el("div", {},
            el("h2", { class: "karta-tytul", text: g.publiczna === false ? (g.opis ? "Brak publicznych statystyk gry" : "Gra jest prywatna albo jeszcze nieopublikowana") : "Statystyki gry są chwilowo niedostępne" }),
            el("p", { class: "cichy-tekst", text: g.opis || (g.publiczna === false
              ? "Roblox pokazuje liczby graczy, wizyt i ocen dopiero dla gry publicznej. Gdy ją udostępnicie, kafle pojawią się tutaj same."
              : "Roblox nie odpowiedział — panel spróbuje ponownie za chwilę.") }),
            g.blad ? el("p", { class: "cichy-tekst an-szczegol", text: "Szczegóły: " + g.blad } ) : null,
            g.placeId ? el("p", { class: "cichy-tekst an-szczegol", text: "Miejsce: " + g.placeId + (g.universeId ? " · uniwersum: " + g.universeId : "") }) : null,
            g.publiczna === false ? el("p", { class: "cichy-tekst an-szczegol", text: "Wykres graczy w czasie też pojawi się dopiero po publikacji." }) : null)));
      } else {
        const glosy = g.glosy || null;
        let oceny = "—", pasek = null;
        if (glosy && (glosy.za || glosy.przeciw)) {
          const suma = (glosy.za || 0) + (glosy.przeciw || 0);
          const proc = Math.round(((glosy.za || 0) / suma) * 100);
          oceny = proc + "%";
          pasek = el("div", {},
            el("div", { class: "an-oceny-pasek", role: "img", "aria-label": `${glosy.za} za, ${glosy.przeciw} przeciw` },
              el("span", { class: "an-za", style: `width:${proc}%` }), el("span", { class: "an-przeciw", style: `width:${100 - proc}%` })),
            el("div", { class: "an-kafel-pod cichy-tekst", text: `👍 ${liczba(glosy.za)} · 👎 ${liczba(glosy.przeciw)}` }));
        } else pasek = "jeszcze nikt nie ocenił";
        gra.replaceChildren(el("div", { class: "siatka an-kafle" },
          kafel("Gracze teraz", liczba(g.gracze), g.max_graczy ? `do ${liczba(g.max_graczy)} na serwer` : "online w tej chwili", (g.gracze || 0) > 0 ? "an-zywe" : ""),
          kafel("Wizyty", krotko(g.wizyty), g.wizyty >= 1e4 ? liczba(g.wizyty) + " łącznie" : "łącznie"),
          kafel("Ulubione", krotko(g.ulubione), "dodali grę do ulubionych"),
          kafel("Oceny", oceny, pasek)));
      }

      rysujWykres(d.historia || [], niedostepna);
      rysujStudio(d.studio || {});
    }

    // ------------------------------------------------------------------ telemetria gry
    async function wczytajTelemetrie(recznie) {
      if (T.trwa) return;
      T.trwa = true;
      let sciezka = TELEMETRIA;
      if (T.probka) sciezka += "&probka=1";
      else if (recznie && ctx.ja.lokalny && !ctx.statyczny) sciezka += "&odswiez=1";
      let bezProbki = false;
      try {
        T.dane = await ctx.api(sciezka, { czas: 45000 });
        T.blad = null;
      } catch (e) {
        if (T.probka) bezProbki = true;                        // dane przykładowe są tylko dla osoby przy komputerze
        else T.blad = e.message || "błąd";
      } finally {
        T.trwa = false;
      }
      if (bezProbki) {
        T.probka = false;
        return wczytajTelemetrie(false);
      }
      T.kiedy = Date.now();
      rysujTelemetrie();
    }

    function ustawProbke(wlacz) {
      T.probka = !!wlacz;
      T.dane = null;
      T.blad = null;
      rysujTelemetrie();
      wczytajTelemetrie(false);
    }

    function naglowekTelemetrii(...dodatki) {
      return el("div", { class: "an-tel-gora" },
        el("h2", { class: "an-tel-tytul" }, ikona("zdrowie"), el("span", { text: "Telemetria gry" })), ...dodatki);
    }

    function rysujTelemetrie() {
      if (T.ro) { T.ro.disconnect(); T.ro = null; }
      T.wykres = null;
      T.schowajDymek = null;
      telemetria.classList.remove("przykladowe");
      const t = T.dane;
      if (!t) {
        telemetria.replaceChildren(naglowekTelemetrii(), T.blad
          ? el("div", { class: "karta an-stan" }, el("div", { class: "pusty-ikona an-stan-ikona" }, ikona("ostrzezenie")),
            el("div", {}, el("h3", { class: "karta-tytul", text: "Nie udało się pobrać telemetrii" }),
              el("p", { class: "cichy-tekst", text: T.blad }),
              el("p", {}, el("button", { class: "przycisk maly", type: "button", onclick: () => wczytajTelemetrie(true) }, ikona("odswiez"), "Spróbuj ponownie"))))
          : ladowanie("Wczytuję telemetrię gry…"));
        return;
      }
      if (!t.zrodlo) {
        telemetria.replaceChildren(naglowekTelemetrii(el("span", { class: "chip", text: t.chwilowe ? "chwilowo niedostępna" : "wyłączona" })),
          ctx.statyczny ? kartaPodgladu() : t.chwilowe ? kartaAwarii(t) : kartaJakWlaczyc(t));
        return;
      }
      const przykladowe = t.zrodlo === "probka";
      telemetria.classList.toggle("przykladowe", przykladowe);
      const okres = t.okres || {};
      // filter(Boolean): natywne replaceChildren() wypisałoby brakujący element jako napis „null”
      telemetria.replaceChildren(...[
        naglowekTelemetrii(
          przykladowe ? el("span", { class: "chip zloto", text: "dane przykładowe" }) : el("span", { class: "chip zielen", text: "dane z gry" }),
          el("span", { class: "cichy-tekst an-tel-okres", text: "ostatnie " + (okres.godzin || 24) + " h" + (t.zaktualizowano && !przykladowe ? " · odczyt " + czasTemu(t.zaktualizowano) : "") })),
        przykladowe ? el("div", { class: "an-tel-baner", role: "note" }, ikona("info"),
          el("div", {}, el("strong", { text: "To są dane przykładowe." }), " Pokazują, jak będzie wyglądać telemetria po włączeniu — nie pochodzą z gry."),
          el("button", { class: "przycisk maly", type: "button", onclick: () => ustawProbke(false) }, "Ukryj")) : null,
        t.blad ? el("div", { class: "an-tel-baner blad", role: "note" }, ikona("ostrzezenie"), el("div", { text: t.blad })) : null,
        kartyTelemetrii(t),
        kartaGodzin(t),
        (t.uwagi || []).length ? el("ul", { class: "an-tel-uwagi cichy-tekst" }, ...t.uwagi.map((u) => el("li", { text: u }))) : null,
      ].filter(Boolean));
      rysujGodziny();
      const pole = T.wykres && T.wykres.pole;
      if (pole) {
        let szer = pole.clientWidth;
        T.ro = new ResizeObserver(() => { if (pole.clientWidth !== szer) { szer = pole.clientWidth; rysujGodziny(); } });
        T.ro.observe(pole);
      }
    }

    // ---- telemetria wyłączona: jedna karta z trzema krokami zamiast pustych kafli
    function kartaJakWlaczyc(t) {
      const kroki = t.kroki || {};
      const jestKlucz = !!kroki.klucz;
      // klucz jest wpisany, ale Roblox go nie przyjął albo brakuje mu uprawnień: krok 2 wymaga poprawki
      const kluczZly = jestKlucz && (t.kod === "klucz_odrzucony" || t.kod === "brak_uprawnien");
      const OPISY = { ok: "zrobione", zle: "do poprawy", uwaga: "do zrobienia" };
      const IKONY_KROKU = { ok: "ok", zle: "krzyzyk", uwaga: "zegar" };
      const krok = (stan, tytul, ...opis) => el("li", { class: "an-krok" },
        el("span", { class: "znacznik " + stan, role: "img", "aria-label": OPISY[stan] }, ikona(IKONY_KROKU[stan])),
        el("div", { class: "an-krok-tresc" }, el("strong", { text: tytul }), el("p", { class: "cichy-tekst" }, ...opis)));
      return el("div", { class: "karta an-tel-jak" },
        el("h3", { class: "karta-tytul" }, ikona("zarowka"), el("span", { text: "Jak włączyć telemetrię" })),
        el("p", { class: "an-tel-powod", text: t.powod || "Telemetria gry nie jest jeszcze włączona." }),
        t.szczegoly ? el("p", { class: "cichy-tekst an-szczegol", text: "Odpowiedź Roblox: " + t.szczegoly }) : null,
        el("ol", { class: "an-kroki" },
          krok(kroki.modul === true ? "ok" : "uwaga", "Game Director włącza moduł w grze",
            "Dodaje skrypt serwera, który woła ", el("code", { text: "Telemetria.start()" }), ", i publikuje grę. Bez tego gra niczego nie zapisuje. Instrukcja: notatka ",
            el("a", { href: "#/siec", "data-wikilink": "Telemetria gry", text: "Telemetria gry" }), " w sejfie."),
          krok(kluczZly ? "zle" : jestKlucz ? "ok" : "uwaga", "Tworzy klucz Open Cloud tylko do odczytu",
            "Creator Dashboard → API Keys: dla tej gry operacja ", el("code", { text: "universe-datastores.objects:read" }),
            " (odczyt wpisów Data Store), a do listy serwerów na żywo także ", el("code", { text: "memory-store.sorted-map:read" }), "."),
          krok(jestKlucz ? "ok" : "uwaga", "Wpisuje klucz lokalnie, na komputerze z panelem",
            "Zmienna środowiskowa ", el("code", { text: "BC_OPEN_CLOUD_KEY" }), " albo pole ", el("code", { text: "analityka.klucz_open_cloud" }), " w pliku ",
            el("code", { text: t.plik_konfiguracji || "konfiguracja.lokalna.json" }), ". Klucz nigdy nie trafia do repozytorium.")),
        el("div", { class: "an-tel-stopka" },
          el("span", { class: "cichy-tekst", text: "Do tego czasu liczby graczy pochodzą tylko z publicznego API Roblox (kafle wyżej)." }),
          ctx.ja.lokalny ? el("button", { class: "przycisk maly", type: "button", onclick: () => ustawProbke(true) }, ikona("oko"), "Pokaż przykładowe dane") : null));
    }

    function kartaAwarii(t) {
      return el("div", { class: "karta an-stan" }, el("div", { class: "pusty-ikona an-stan-ikona" }, ikona("ostrzezenie")),
        el("div", {}, el("h3", { class: "karta-tytul", text: "Telemetria jest chwilowo niedostępna" }),
          el("p", { class: "cichy-tekst", text: t.powod || "Roblox nie odpowiedział." }),
          t.szczegoly ? el("p", { class: "cichy-tekst an-szczegol", text: "Odpowiedź Roblox: " + t.szczegoly }) : null,
          el("p", {}, el("button", { class: "przycisk maly", type: "button", onclick: () => wczytajTelemetrie(true) }, ikona("odswiez"), "Spróbuj ponownie"))));
    }

    function kartaPodgladu() {
      return el("div", { class: "karta an-stan" }, el("div", { class: "pusty-ikona an-stan-ikona" }, ikona("oko")),
        el("div", {}, el("h3", { class: "karta-tytul", text: "Niedostępne w podglądzie" }),
          el("p", { class: "cichy-tekst", text: "Sesje, Robuxy, błędy i serwery na żywo widać tylko w panelu uruchomionym na komputerze — do podglądu tylko do odczytu nie trafiają żadne dane z gry." })));
    }

    // ---- cztery karty: sesje, Robuxy, błędy, serwery
    function kartaTel(tytul, nazwaIkony, wartosc, podpisy, tresc) {
      return el("div", { class: "karta an-tel-karta" },
        el("h3", { class: "karta-tytul" }, ikona(nazwaIkony), el("span", { text: tytul })),
        el("div", { class: "an-tel-wartosc", text: wartosc }),
        ...podpisy.filter(Boolean).map((p) => el("div", { class: "an-tel-pod cichy-tekst", text: p })),
        tresc || null);
    }
    const listaTel = (pozycje, pusta) => (pozycje.length
      ? el("ul", { class: "an-tel-lista" }, ...pozycje)
      : el("p", { class: "an-tel-pusta cichy-tekst", text: pusta }));

    function kartyTelemetrii(t) {
      const su = t.suma || {};
      const robux = (n) => liczba(n) + " R$";
      // sesje: liczba, średni czas i rozkład długości (ile sesji kończy się w każdym przedziale)
      const dl = t.dlugosci_sesji || {};
      const razemDl = PRZEDZIALY_SESJI.reduce((a, p) => a + (Number(dl[p.id]) || 0), 0);
      const rozklad = razemDl ? el("ul", { class: "an-tel-rozklad", "aria-label": "Długość sesji" }, ...PRZEDZIALY_SESJI.map((p) => {
        const ile = Number(dl[p.id]) || 0, proc = Math.round((ile / razemDl) * 100);
        const ileSesji = liczba(ile) + " " + odmiana(ile, "sesja", "sesje", "sesji");
        return el("li", {},
          el("span", { class: "an-tel-rozklad-nazwa", text: p.tekst }),
          el("span", { class: "an-tel-rozklad-tor", title: ileSesji }, ile ? el("span", { class: "an-tel-rozklad-pasek", style: `width:${(ile / razemDl) * 100}%` }) : null),
          el("span", { class: "an-tel-liczba", title: ileSesji, text: proc + "%" }));
      })) : null;
      const sesje = kartaTel("Sesje", "zespol", liczba(su.sesje), [
        su.sredni_czas_sesji_s != null ? "średni czas sesji: " + czasTrwania(su.sredni_czas_sesji_s) : "średni czas sesji: brak zakończonych sesji",
        "najwięcej graczy naraz: " + liczba(su.ccu_max)], rozklad);
      // Robuxy
      const zakupy = (t.zakupy || []).slice(0, 5);
      const robuxy = kartaTel("Wydane Robuxy", "rakieta", robux(su.robuxy), [
        liczba(su.zakupy) + " " + odmiana(su.zakupy, "zakup", "zakupy", "zakupów")],
      listaTel(zakupy.map((z) => el("li", {},
        el("span", { class: "an-tel-nazwa", text: z.nazwa || z.id, title: z.nazwa || z.id }),
        el("span", { class: "an-tel-liczba cichy-tekst", text: liczba(z.n) + "×" }),
        el("span", { class: "an-tel-liczba", text: robux(z.robuxy) }))), "Brak zakupów w tym okresie."));
      // błędy i crashe
      const awarie = (su.niedomkniete || 0) + (su.brak_pamieci || 0);
      const bledy = kartaTel("Błędy i crashe", "ostrzezenie", liczba(su.bledy), [
        odmiana(su.bledy, "błąd skryptu", "błędy skryptów", "błędów skryptów") + " na serwerach",
        su.niedomkniete == null && !su.brak_pamieci ? null
          : awarie ? "możliwe awarie serwerów: " + liczba(awarie) + (su.brak_pamieci ? " (z braku pamięci: " + liczba(su.brak_pamieci) + ")" : "")
            : "bez awarii serwerów"],
      listaTel((t.bledy || []).slice(0, 5).map((b) => el("li", {},
        el("span", { class: "an-tel-komunikat", text: b.komunikat, title: b.komunikat }),
        el("span", { class: "an-tel-liczba", text: liczba(b.n) + "×" }))), "Brak błędów w tym okresie."));
      // serwery na żywo
      const znane = su.serwery_teraz != null;
      const lista = (t.serwery || []).slice(0, 5);
      const serwery = kartaTel("Serwery na żywo", "siec", znane ? liczba(su.serwery_teraz) : "—", [
        znane ? liczba(su.gracze_teraz) + " " + odmiana(su.gracze_teraz, "gracz", "graczy", "graczy") + " teraz" : "lista serwerów jest niedostępna (szczegóły niżej)"],
      znane ? listaTel(lista.map((s) => {
        const od = Date.parse(s.od);
        const dodatki = [od ? "działa " + czasTrwania((Date.now() - od) / 1000).replace(/ \d+ s$/, "") : null,
          s.pamiec_mb ? liczba(s.pamiec_mb) + " MB" : null, s.fps ? liczba(s.fps) + " kl./s" : null,
          s.bledy ? liczba(s.bledy) + " " + odmiana(s.bledy, "błąd", "błędy", "błędów") : null].filter(Boolean).join(" · ");
        return el("li", {},
          el("span", { class: "an-tel-serwer" }, el("code", { text: s.id }), el("span", { class: "cichy-tekst", text: dodatki })),
          el("span", { class: "an-tel-liczba", text: liczba(s.gracze) + " " + odmiana(s.gracze, "gracz", "graczy", "graczy") }));
      }), "Żaden serwer teraz nie działa.") : null);
      if (znane && (t.serwery || []).length > lista.length) {
        serwery.append(el("div", { class: "an-tel-pod cichy-tekst", text: "…i " + ((su.serwery_teraz || 0) - lista.length) + " więcej" }));
      }
      return el("div", { class: "siatka an-tel-karty" }, sesje, robuxy, bledy, serwery);
    }

    // ---- wykres godzinowy: słupki jednej serii (wybór przełącznikiem), siatka w tle, podpowiedź po najechaniu
    function kartaGodzin(t) {
      const godziny = (t.godziny || []).map((g) => Object.assign({}, g, { t: czasPunktu(g.t) })).filter((g) => g.t).sort((a, b) => a.t - b.t);
      const pole = el("div", { class: "an-wykres an-tel-pole" });
      const opis = el("span", { class: "cichy-tekst an-zakres" });
      const wybor = przelacznik(METRYKI.map((m) => ({ id: m.id, tekst: m.tekst })), T.metryka, (id) => { T.metryka = id; rysujGodziny(); }, "Co pokazuje wykres");
      wybor.classList.add("maly");
      const godzina = (ms) => new Date(ms).toLocaleString("pl-PL", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
      const tabela = el("details", { class: "an-tabela", open: T.tabela },
        el("summary", { text: "Liczby godzina po godzinie" }),
        el("table", {},
          el("thead", {}, el("tr", {}, el("th", { scope: "col", text: "Godzina" }), ...METRYKI.map((m) => el("th", { scope: "col", text: m.tekst })))),
          el("tbody", {}, ...godziny.slice().reverse().map((g) => el("tr", {}, el("th", { scope: "row", text: godzina(g.t) }),
            ...METRYKI.map((m) => el("td", { text: liczba(g[m.id]) })))))));
      tabela.addEventListener("toggle", () => { T.tabela = tabela.open; });
      T.wykres = { pole, opis, godziny };
      return el("div", { class: "karta an-tel-wykres" },
        el("div", { class: "an-naglowek" }, el("h3", { class: "karta-tytul" }, ikona("analityka"), el("span", { text: "Godzina po godzinie" })), wybor),
        opis, pole, tabela);
    }

    function rysujGodziny() {
      if (!T.wykres) return;
      const { pole, opis, godziny } = T.wykres;
      const m = METRYKI.find((x) => x.id === T.metryka) || METRYKI[0];
      const pkt = godziny.map((g) => ({ t: g.t, v: Math.max(0, Number(g[m.id]) || 0) }));
      const n = pkt.length;
      const maxV = Math.max(0, ...pkt.map((p) => p.v));
      opis.textContent = m.opis.charAt(0).toUpperCase() + m.opis.slice(1) + (maxV ? " · ostatni słupek to godzina w toku" : "");
      T.schowajDymek = null;
      if (!n || !maxV) {
        pole.replaceChildren(el("p", { class: "an-tel-pusta cichy-tekst", text: m.pusto }));
        return;
      }
      const dymek = el("div", { class: "an-dymek", hidden: true });
      const W = Math.max(260, pole.clientWidth || 600), H = 176;
      const L = 40, R = 8, G = 10, D = 24;
      const krok = ladnyKrok(maxV);
      const yMax = Math.max(krok, Math.ceil(maxV / krok) * krok);
      const pasmo = (W - L - R) / n;
      const szer = Math.max(2, Math.min(24, pasmo - 2));          // słupek najwyżej 24 px, między słupkami 2 px tła
      const dno = H - D;
      const Y = (v) => G + (1 - v / yMax) * (dno - G);
      const srodek = (i) => L + i * pasmo + pasmo / 2;
      const najwiecej = pkt.reduce((a, p) => (p.v > a.v ? p : a), pkt[0]);
      const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "an-svg", role: "img",
        "aria-label": `Wykres: ${m.opis}, ostatnie ${n} h. Razem ${liczba(pkt.reduce((a, p) => a + p.v, 0))}, najwięcej ${liczba(najwiecej.v)} o ${new Date(najwiecej.t).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}. Wszystkie liczby są w tabeli pod wykresem.` });
      for (let v = 0; v <= yMax + krok / 2; v += krok) {
        svg.append(s("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: "an-siatka" }));
        const tx = s("text", { x: L - 6, y: Y(v) + 4, class: "an-os", "text-anchor": "end" });
        tx.textContent = krotko(v);
        svg.append(tx);
      }
      // podpisy godzin: co kilka słupków, licząc od najnowszego, tyle ile się zmieści
      const coIle = Math.max(1, Math.ceil(n / Math.max(2, Math.floor((W - L - R) / 54))));
      pkt.forEach((p, i) => {
        if ((n - 1 - i) % coIle) return;
        const tx = s("text", { x: Math.min(srodek(i), W - R), y: H - 7, class: "an-os", "text-anchor": i === n - 1 ? "end" : "middle" });
        tx.textContent = new Date(p.t).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
        svg.append(tx);
      });
      const slupki = pkt.map((p, i) => {
        if (!p.v) return null;
        const h = Math.max(2, dno - Y(p.v)), x = srodek(i) - szer / 2, y = dno - h, r = Math.min(4, szer / 2, h);
        const sl = s("path", { class: "an-slupek" + (i === n - 1 ? " w-toku" : ""),
          d: `M${x} ${dno}V${y + r}Q${x} ${y} ${x + r} ${y}H${x + szer - r}Q${x + szer} ${y} ${x + szer} ${y + r}V${dno}Z` });
        svg.append(sl);
        return sl;
      });
      const strefa = s("rect", { x: L, y: 0, width: W - L - R, height: H, fill: "transparent" });
      svg.append(strefa);
      let aktywny = -1;
      const pokaz = (e) => {
        const r = svg.getBoundingClientRect();
        const x = ((e.clientX - r.left) / r.width) * W;
        const i = Math.max(0, Math.min(n - 1, Math.floor((x - L) / pasmo)));
        if (i !== aktywny) {
          if (slupki[aktywny]) slupki[aktywny].classList.remove("aktywny");
          if (slupki[i]) slupki[i].classList.add("aktywny");
          aktywny = i;
          const p = pkt[i];
          const od = new Date(p.t), doG = new Date(p.t + 3600000);
          const hm = (d) => d.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
          dymek.replaceChildren(el("b", { text: `${liczba(p.v)} ${odmiana(p.v, ...m.jednostka)}` }),
            el("span", { class: "cichy-tekst", text: `${od.toLocaleDateString("pl-PL", { day: "numeric", month: "short" })}, ${hm(od)}–${hm(doG)}${i === n - 1 ? " · w toku" : ""}` }));
        }
        dymek.hidden = false;
        const sx = (srodek(i) / W) * r.width;
        dymek.style.left = Math.max(4, Math.min(r.width - dymek.offsetWidth - 4, sx - dymek.offsetWidth / 2)) + "px";
        dymek.style.top = Math.max(0, (Y(pkt[i].v) / H) * r.height - 54) + "px";
      };
      const schowaj = () => {
        if (slupki[aktywny]) slupki[aktywny].classList.remove("aktywny");
        aktywny = -1;
        dymek.hidden = true;
      };
      strefa.addEventListener("pointermove", pokaz);
      strefa.addEventListener("pointerdown", pokaz);
      // mysz: podpowiedź znika po zjechaniu z wykresu; palec: zostaje po dotknięciu, aż dotkniesz obok wykresu
      strefa.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") schowaj(); });
      T.schowajDymek = schowaj;
      pole.replaceChildren(svg, dymek);
    }
    document.addEventListener("pointerdown", (e) => {
      if (T.wykres && T.schowajDymek && !T.wykres.pole.contains(e.target)) T.schowajDymek();
    });

    // ---- wykres historii graczy (SVG, bez bibliotek): jedna seria, siatka w tle, celownik z podpowiedzią
    function rysujWykres(historia, niedostepna) {
      const pkt = historia.map((p) => ({ t: czasPunktu(p.t), v: Number(p.gracze) || 0 })).filter((p) => p.t).sort((a, b) => a.t - b.t);
      // gra prywatna: bez pustej karty wykresu (informacja jest już w karcie stanu gry)
      wykres.hidden = !!niedostepna && pkt.length < 2;
      wykres.replaceChildren(el("div", { class: "an-naglowek" }, el("h2", { class: "karta-tytul" }, ikona("analityka"), el("span", { text: "Gracze w czasie" })),
        pkt.length ? el("span", { class: "cichy-tekst an-zakres", text: zakresCzasu(pkt) }) : null));
      if (pkt.length < 2) {
        wykres.append(el("p", { class: "cichy-tekst", text: niedostepna
          ? "Wykres pojawi się, gdy gra będzie publiczna."
          : "Historia zbiera się, gdy panel jest włączony — wykres pojawi się po kilku odczytach (co minutę)." }));
        return;
      }
      const pole = el("div", { class: "an-wykres" });
      const dymek = el("div", { class: "an-dymek", hidden: true });
      pole.append(dymek);
      wykres.append(pole);
      const narysuj = () => {
        const W = Math.max(260, pole.clientWidth || 600), H = 210;
        const L = 34, R = 12, G = 10, D = 26;
        const t0 = pkt[0].t, t1 = pkt[pkt.length - 1].t;
        const maxV = Math.max(...pkt.map((p) => p.v), 0);
        const krok = ladnyKrok(maxV);
        const yMax = Math.max(krok, Math.ceil(maxV / krok) * krok);
        const X = (t) => L + ((t - t0) / Math.max(t1 - t0, 1)) * (W - L - R);
        const Y = (v) => G + (1 - v / yMax) * (H - G - D);
        const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "an-svg", role: "img",
          "aria-label": `Wykres liczby graczy: od ${pkt[0].v} do ${pkt[pkt.length - 1].v}, maksimum ${maxV}` });
        for (let v = 0; v <= yMax; v += krok) {
          svg.append(s("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: "an-siatka" }));
          const tx = s("text", { x: L - 6, y: Y(v) + 4, class: "an-os", "text-anchor": "end" });
          tx.textContent = v;
          svg.append(tx);
        }
        const etyk = [t0, t0 + (t1 - t0) / 2, t1];
        etyk.forEach((t, i) => {
          const tx = s("text", { x: X(t), y: H - 7, class: "an-os", "text-anchor": i === 0 ? "start" : i === 2 ? "end" : "middle" });
          tx.textContent = formatCzasu(t, t1 - t0);
          svg.append(tx);
        });
        const linia = pkt.map((p, i) => (i ? "L" : "M") + X(p.t).toFixed(1) + " " + Y(p.v).toFixed(1)).join(" ");
        const defs = s("defs");
        const gr = s("linearGradient", { id: "an-gradient", x1: 0, x2: 0, y1: 0, y2: 1 });
        gr.append(s("stop", { offset: "0", "stop-color": "var(--niebieski, #4ea8ff)", "stop-opacity": ".28" }),
          s("stop", { offset: "1", "stop-color": "var(--niebieski, #4ea8ff)", "stop-opacity": "0" }));
        defs.append(gr);
        svg.append(defs,
          s("path", { d: `${linia} L${X(t1).toFixed(1)} ${Y(0)} L${X(t0).toFixed(1)} ${Y(0)} Z`, fill: "url(#an-gradient)" }),
          s("path", { d: linia, class: "an-linia" }));
        const ost = pkt[pkt.length - 1];
        svg.append(s("circle", { cx: X(ost.t), cy: Y(ost.v), r: 4, class: "an-kropka" }));
        const celownik = s("line", { y1: G, y2: H - D, class: "an-celownik", visibility: "hidden" });
        const punkt = s("circle", { r: 5, class: "an-kropka an-punkt", visibility: "hidden" });
        const strefa = s("rect", { x: L, y: 0, width: W - L - R, height: H, fill: "transparent" });
        svg.append(celownik, punkt, strefa);
        const pokazPunkt = (e) => {
          const r = svg.getBoundingClientRect();
          const x = ((e.clientX - r.left) / r.width) * W;
          const t = t0 + ((x - L) / (W - L - R)) * (t1 - t0);
          let best = pkt[0];
          for (const p of pkt) if (Math.abs(p.t - t) < Math.abs(best.t - t)) best = p;
          const px = X(best.t), py = Y(best.v);
          celownik.setAttribute("x1", px); celownik.setAttribute("x2", px);
          celownik.setAttribute("visibility", "visible");
          punkt.setAttribute("cx", px); punkt.setAttribute("cy", py);
          punkt.setAttribute("visibility", "visible");
          dymek.hidden = false;
          dymek.replaceChildren(el("b", { text: `${liczba(best.v)} ${odmiana(best.v, "gracz", "graczy", "graczy")}` }),
            el("span", { class: "cichy-tekst", text: new Date(best.t).toLocaleString("pl-PL", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) }));
          const sx = (px / W) * r.width;
          dymek.style.left = Math.max(4, Math.min(r.width - dymek.offsetWidth - 4, sx - dymek.offsetWidth / 2)) + "px";
          dymek.style.top = Math.max(0, (py / H) * r.height - 58) + "px";
        };
        const schowaj = () => { celownik.setAttribute("visibility", "hidden"); punkt.setAttribute("visibility", "hidden"); dymek.hidden = true; };
        strefa.addEventListener("pointermove", pokazPunkt);
        strefa.addEventListener("pointerdown", pokazPunkt);
        strefa.addEventListener("pointerleave", schowaj);
        pole.replaceChildren(svg, dymek);
      };
      narysuj();
      if (S.ro) S.ro.disconnect();
      let szer = pole.clientWidth;
      S.ro = new ResizeObserver(() => { if (pole.clientWidth !== szer) { szer = pole.clientWidth; narysuj(); } });
      S.ro.observe(pole);
    }

    function ladnyKrok(max) {
      if (max <= 5) return 1;
      const surowy = max / 4;
      const p = Math.pow(10, Math.floor(Math.log10(surowy)));
      for (const m of [1, 2, 5, 10]) if (m * p >= surowy) return m * p;
      return 10 * p;
    }
    function formatCzasu(t, rozpietosc) {
      const d = new Date(t);
      if (rozpietosc > 36 * 3600 * 1000) return d.toLocaleDateString("pl-PL", { day: "numeric", month: "short" });
      return d.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
    }
    function zakresCzasu(pkt) {
      const h = (pkt[pkt.length - 1].t - pkt[0].t) / 3600000;
      if (h < 1) return "ostatnie " + Math.max(1, Math.round(h * 60)) + " min";
      if (h < 48) return "ostatnie " + Math.round(h) + " h";
      return "ostatnie " + Math.round(h / 24) + " dni";
    }

    // ---- Roblox Studio: połączenie, tryb, błędy, końcówka konsoli
    function rysujStudio(st) {
      const pol = !!st.polaczone;
      const linie = (st.konsola || []).slice(-60).map((l) => (typeof l === "string" ? { poziom: "info", tekst: l } : l));
      const tryb = st.tryb ? String(st.tryb) : null;
      const nazwaTrybu = tryb ? ({ edycja: "edycja", edit: "edycja", gra: "test gry", play: "test gry", run: "symulacja", serwer: "serwer", klient: "klient" }[tryb.toLowerCase()] || tryb) : null;
      const konsola = el("div", { class: "an-konsola", role: "log", "aria-label": "Konsola Roblox Studio" },
        ...linie.map((l) => el("div", { class: "an-linia-k " + (l.poziom === "blad" ? "blad" : l.poziom === "ostrzezenie" ? "ostrz" : "info") },
          el("span", { class: "an-poziom", text: l.poziom === "blad" ? "BŁĄD" : l.poziom === "ostrzezenie" ? "UWAGA" : "info" }), " ", l.tekst || "")));
      studio.replaceChildren(
        el("div", { class: "an-naglowek" }, el("h2", { class: "karta-tytul" }, ikona("studio"), el("span", { text: "Roblox Studio" })),
          el("span", { class: "chip " + (pol ? "zielen" : ""), text: pol ? "połączone" : "niepołączone" })),
        el("div", { class: "an-studio-chipy" },
          nazwaTrybu ? el("span", { class: "chip niebieski", text: "tryb: " + nazwaTrybu }) : null,
          el("span", { class: "chip " + (st.bledy ? "czerwien" : ""), text: `${liczba(st.bledy || 0)} ${odmiana(st.bledy || 0, "błąd", "błędy", "błędów")}` }),
          el("span", { class: "chip " + (st.ostrzezenia ? "zloto" : ""), text: `${liczba(st.ostrzezenia || 0)} ${odmiana(st.ostrzezenia || 0, "ostrzeżenie", "ostrzeżenia", "ostrzeżeń")}` })),
        linie.length ? konsola : el("p", { class: "cichy-tekst", text: pol
          ? "Konsola jest pusta."
          : "Otwórz grę w Roblox Studio (z włączonym pluginem MCP), żeby zobaczyć tu konsolę, błędy i ostrzeżenia." }));
      if (linie.length) requestAnimationFrame(() => { konsola.scrollTop = konsola.scrollHeight; });
    }

    rysuj();
    rysujTelemetrie();
    return {
      el: root,
      async pokaz(parametry) {
        S.widoczny = true;
        // #/analityka?probka=1 — od razu dane przykładowe (tylko osoba przy komputerze; serwer i tak to sprawdza)
        if (parametry && parametry.probka && ctx.ja.lokalny && !ctx.statyczny) T.probka = true;
        clearInterval(S.timer);
        S.timer = setInterval(() => {
          if (!S.widoczny || document.visibilityState !== "visible") return;
          wczytaj();
          if (Date.now() - T.kiedy >= ODSWIEZ_TELEMETRIE_MS) wczytajTelemetrie(false);
        }, ODSWIEZ_MS);
        wczytajTelemetrie(false);
        await wczytaj();
      },
      ukryj() {
        S.widoczny = false;
        clearInterval(S.timer);
        S.timer = 0;
      },
    };
  },
};
