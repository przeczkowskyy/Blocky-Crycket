// Raporty z wdrożeń: lista z filtrem, akceptacja / do poprawy, komentarze, zrzuty, komponenty.

import { el, dopisz, ikona, czasTemu, dataKrotka, toast, arkusz, awatar, pusty, stanBledu, ladowanie, przelacznik, powiekszenie, odmiana } from "../wspolne/ui.js";
import { md } from "../wspolne/markdown.js";
import { komentarze } from "../wspolne/komentarze.js";
import { dyktafon } from "../wspolne/dyktafon.js";

const enc = encodeURIComponent;

const STATUSY = {
  czeka: { tekst: "Czeka", kolor: "zloto", ikona: "zegar" },
  zaakceptowane: { tekst: "Zaakceptowane", kolor: "zielen", ikona: "ok" },
  do_poprawy: { tekst: "Do poprawy", kolor: "czerwien", ikona: "krzyzyk" },
  informacja: { tekst: "Informacja", kolor: "niebieski", ikona: "info" },
};
const RODZAJE = { wdrozenie: "wdrożenie", pytanie: "pytanie", informacja: "informacja" };
const FILTRY = [
  { id: "wszystkie", tekst: "Wszystkie" },
  { id: "czeka", tekst: "Czekają" },
  { id: "zaakceptowane", tekst: "Zaakceptowane" },
  { id: "do_poprawy", tekst: "Do poprawy" },
];
const IKONY_KOMPONENTOW = { studio: "studio", notatka: "notatka", plik: "notatka", migawka: "migawka" };

export default {
  id: "raporty",
  tytul: "Raporty",
  ikona: "raporty",
  kolejnosc: 30,
  utworz(ctx) {
    let filtr = "wszystkie";
    try {
      filtr = localStorage.getItem("bc.raporty.filtr") || filtr;
    } catch (e) { /* nic */ }
    let raporty = null;
    let blad = null;
    let sygnatura = "";
    const rozwinieteOpisy = new Set();
    const otwarteKomentarze = new Set();
    const zmienDecyzje = new Set();
    const karty = new Map();

    const lista = el("div", { class: "kolumna raporty-lista" }, ladowanie("Wczytuję raporty…"));
    const segment = przelacznik(FILTRY, filtr, (id) => {
      filtr = id;
      try {
        localStorage.setItem("bc.raporty.filtr", id);
      } catch (e) { /* nic */ }
      rysuj();
    }, "Filtr raportów");
    const korzen = el("div", { class: "widok raporty" },
      el("header", { class: "nagl-widoku" },
        el("div", null, el("h1", null, "Raporty"), el("p", { class: "cichy-tekst" }, "Co agenci i ludzie wdrożyli — akceptuj albo odeślij do poprawy.")),
        el("button", { class: "przycisk cichy ikonowy", type: "button", title: "Odśwież", "aria-label": "Odśwież", onclick: () => pobierz(true) }, ikona("odswiez"))),
      el("div", { class: "przelacznik-przewijany" }, segment),
      lista);

    // ------------------------------------------------------------------ karta raportu
    function chipStatusu(r) {
      const s = STATUSY[r.status] || { tekst: r.status || "?", kolor: "" };
      return el("span", { class: "chip " + s.kolor }, s.ikona ? ikona(s.ikona) : null, s.tekst);
    }

    function zrzuty(r) {
      const nazwy = r.zrzuty || [];
      if (!nazwy.length) return null;
      const obrazy = nazwy.map((n) => ({ src: ctx.plik("/api/raporty/" + enc(r.id) + "/plik/" + enc(n)), podpis: r.tytul + " — " + n }));
      return el("div", { class: "galeria", role: "list" }, obrazy.map((o, i) => el("button", {
        type: "button", class: "galeria-miniatura", role: "listitem", "aria-label": "Powiększ zrzut " + (i + 1),
        onclick: () => powiekszenie(obrazy, i),
      }, el("img", { src: o.src, alt: "", loading: "lazy" }))));
    }

    function komponenty(r) {
      const k = r.komponenty || [];
      const chipy = k.map((c) => {
        const tekst = c.etykieta || String(c.cel || "").split("/").pop() || c.typ;
        let akcja = null;
        if (c.typ === "studio") akcja = () => ctx.idz("podglad", { migawka: r.migawka, grupa: c.cel });
        else if (c.typ === "notatka") akcja = () => ctx.idz("siec", { notatka: c.cel });
        else if (c.typ === "migawka") akcja = () => ctx.idz("podglad", { migawka: c.cel });
        const zawartosc = [ikona(IKONY_KOMPONENTOW[c.typ] || "info"), el("span", null, tekst)];
        return akcja
          ? el("button", { type: "button", class: "chip klik komponent typ-" + c.typ, title: c.typ + ": " + c.cel, onclick: akcja }, zawartosc)
          : el("span", { class: "chip komponent typ-" + c.typ, title: c.typ + ": " + c.cel }, zawartosc);
      });
      if (r.migawka && !k.some((c) => c.typ === "migawka")) {
        chipy.push(el("button", { type: "button", class: "chip klik niebieski", onclick: () => ctx.idz("podglad", { migawka: r.migawka }) }, ikona("podglad"), el("span", null, "Migawka 3D")));
      }
      return chipy.length ? el("div", { class: "chipy komponenty" }, chipy) : null;
    }

    function opis(r) {
      if (!r.opis_md) return null;
      const tresc = el("div", { class: "md raport-opis", html: md(r.opis_md) });
      const dlugi = r.opis_md.length > 520 || (r.opis_md.match(/\n/g) || []).length > 12;
      if (!dlugi) return tresc;
      const otwarty = rozwinieteOpisy.has(r.id);
      const opakowanie = el("div", { class: "zwijany-opis" + (otwarty ? " rozwiniety" : "") }, tresc);
      const przycisk = el("button", { type: "button", class: "przycisk cichy maly pokaz-wiecej" }, otwarty ? "Pokaż mniej" : "Pokaż więcej");
      przycisk.addEventListener("click", () => {
        const teraz = !opakowanie.classList.contains("rozwiniety");
        opakowanie.classList.toggle("rozwiniety", teraz);
        przycisk.textContent = teraz ? "Pokaż mniej" : "Pokaż więcej";
        if (teraz) rozwinieteOpisy.add(r.id);
        else rozwinieteOpisy.delete(r.id);
      });
      return el("div", null, opakowanie, przycisk);
    }

    function decyzjaInfo(r) {
      const d = r.decyzja;
      if (!d) return null;
      const s = STATUSY[d.wartosc] || { tekst: d.wartosc, kolor: "" };
      const czasownik = d.wartosc === "zaakceptowane" ? "zaakceptował(a)" : d.wartosc === "do_poprawy" ? "odesłał(a) do poprawy" : "zdecydował(a)";
      return el("div", { class: "decyzja-info " + s.kolor },
        ikona(s.ikona || "info"),
        el("div", null,
          el("p", null, el("strong", null, d.kto || "ktoś"), " " + czasownik + " · ", el("span", { title: dataKrotka(d.czas) }, czasTemu(d.czas))),
          d.komentarz ? el("blockquote", { class: "decyzja-komentarz" }, d.komentarz) : null));
    }

    async function decyduj(r, wartosc, komentarz) {
      const cialo = { wartosc };
      if (komentarz) cialo.komentarz = komentarz;
      const nowy = await ctx.api("/api/raporty/" + enc(r.id) + "/decyzja", { metoda: "POST", cialo });
      zmienDecyzje.delete(r.id);
      const i = raporty.findIndex((x) => x.id === r.id);
      if (i >= 0) raporty[i] = Object.assign({}, raporty[i], nowy && nowy.id ? nowy : { status: wartosc, decyzja: { kto: ctx.ja.kto, czas: new Date().toISOString(), wartosc, komentarz } });
      sygnatura = "";
      ctx.licznik("raporty", raporty.filter((x) => x.status === "czeka").length);
      rysuj();
    }

    function oknoPoprawy(r) {
      const pole = el("textarea", { class: "pole", rows: 4, placeholder: "Co trzeba poprawić? (agent przeczyta to przy następnej pracy)", "aria-label": "Komentarz do poprawy" });
      const dyk = dyktafon(ctx, {
        etykieta: "Nagraj uwagi głosem",
        naTekst: (t) => {
          pole.value = (pole.value.trim() ? pole.value.trim() + " " : "") + t;
          pole.focus();
        },
      });
      const wyslij = el("button", { type: "submit", class: "przycisk grozny" }, ikona("krzyzyk"), el("span", null, "Odeślij do poprawy"));
      const form = el("form", { class: "formularz" },
        el("p", { class: "cichy-tekst" }, "„" + (r.tytul || "raport") + "”"),
        el("label", { class: "etykieta" }, "Komentarz"), pole,
        el("div", { class: "rzad-przyciskow" }, dyk, el("span", { class: "rozpychacz" }), wyslij));
      const ark = arkusz({ tytul: "Do poprawy", tresc: form });
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        wyslij.disabled = true;
        try {
          await decyduj(r, "do_poprawy", pole.value.trim());
          ark.zamknij();
          toast("Odesłano do poprawy.", "ok");
        } catch (err) {
          toast("Nie udało się: " + err.message, "blad");
          wyslij.disabled = false;
        }
      });
    }

    function przyciski(r, kartaEl) {
      const rzad = el("div", { class: "rzad-przyciskow raport-akcje" });
      const mozeDecydowac = !ctx.statyczny && (r.rodzaj === "wdrozenie" || r.rodzaj === "pytanie" || r.status === "czeka" || r.decyzja);
      const pokazDecyzje = mozeDecydowac && (r.status === "czeka" || zmienDecyzje.has(r.id));
      if (pokazDecyzje) {
        const ok = el("button", { type: "button", class: "przycisk sukces" }, ikona("ok"), el("span", null, "Akceptuję"));
        ok.addEventListener("click", async () => {
          ok.disabled = true;
          try {
            await decyduj(r, "zaakceptowane");
            toast("Zaakceptowano.", "ok");
          } catch (e) {
            toast("Nie udało się: " + e.message, "blad");
            ok.disabled = false;
          }
        });
        rzad.append(ok, el("button", { type: "button", class: "przycisk grozny", onclick: () => oknoPoprawy(r) }, ikona("krzyzyk"), el("span", null, "Do poprawy")));
      }
      const liczba = Number(r.komentarzy) || 0;
      const bKom = el("button", { type: "button", class: "przycisk" + (otwarteKomentarze.has(r.id) ? " wcisniety" : ""), "aria-expanded": otwarteKomentarze.has(r.id) ? "true" : "false" },
        ikona("komentarz"), el("span", null, "Komentarze"), el("span", { class: "licznik-przycisku" }, String(liczba)));
      const watek = el("div", { class: "raport-watek", hidden: !otwarteKomentarze.has(r.id) });
      const zaladujWatek = () => {
        if (watek.firstChild) return;
        watek.appendChild(komentarze(ctx, { typ: "raport", cel: r.id, etykieta: r.tytul }, {
          naZmiane: (n) => {
            bKom.querySelector(".licznik-przycisku").textContent = String(n);
            r.komentarzy = n;
          },
        }));
      };
      if (otwarteKomentarze.has(r.id)) zaladujWatek();
      bKom.addEventListener("click", () => {
        const otworz = watek.hidden;
        watek.hidden = !otworz;
        bKom.classList.toggle("wcisniety", otworz);
        bKom.setAttribute("aria-expanded", otworz ? "true" : "false");
        if (otworz) {
          otwarteKomentarze.add(r.id);
          zaladujWatek();
        } else otwarteKomentarze.delete(r.id);
      });
      rzad.appendChild(bKom);
      if (!ctx.statyczny) {
        rzad.appendChild(el("button", {
          type: "button", class: "przycisk cichy",
          onclick: () => ctx.idz("agent", { kontekst: [{ typ: "raport", cel: r.id, etykieta: r.tytul }] }),
        }, ikona("agent"), el("span", null, "Do agenta")));
      }
      if (mozeDecydowac && !pokazDecyzje && r.decyzja) {
        rzad.appendChild(el("button", {
          type: "button", class: "przycisk cichy maly zmien-decyzje",
          onclick: () => {
            zmienDecyzje.add(r.id);
            const nowa = kartaRaportu(r);
            kartaEl.replaceWith(nowa);
            karty.set(r.id, nowa);
          },
        }, "Zmień decyzję"));
      }
      return [rzad, watek];
    }

    function kartaRaportu(r) {
      const k = el("article", { class: "karta raport status-" + (r.status || "brak"), id: "raport-" + r.id, dataset: { id: r.id } });
      const [akcje, watek] = przyciski(r, k);
      dopisz(k,
        el("div", { class: "raport-gora" },
          awatar(r.kto),
          el("div", { class: "raport-meta" },
            el("h2", { class: "raport-tytul" }, r.tytul || "(bez tytułu)"),
            el("p", { class: "cichy-tekst" }, el("strong", null, r.kto || "ktoś"), " · ",
              el("time", { datetime: r.czas || "", title: dataKrotka(r.czas) }, czasTemu(r.czas)),
              r.rodzaj && r.rodzaj !== "wdrozenie" ? " · " + (RODZAJE[r.rodzaj] || r.rodzaj) : "")),
          chipStatusu(r)),
        opis(r),
        r.pytanie ? el("div", { class: "raport-pytanie" }, el("span", { class: "etykieta" }, ikona("pytanie"), "Pytanie"), el("div", { class: "md", html: md(r.pytanie) })) : null,
        zrzuty(r),
        komponenty(r),
        decyzjaInfo(r),
        akcje,
        watek);
      return k;
    }

    // ------------------------------------------------------------------ lista
    function rysuj() {
      segment.ustaw(filtr);
      if (blad) {
        lista.replaceChildren(stanBledu(blad, "Raporty"));
        return;
      }
      if (!raporty) return;
      const liczby = { wszystkie: raporty.length, czeka: 0, zaakceptowane: 0, do_poprawy: 0 };
      for (const r of raporty) if (liczby[r.status] !== undefined) liczby[r.status]++;
      for (const f of FILTRY) segment.licznik(f.id, liczby[f.id]);
      const widoczne = raporty.filter((r) => filtr === "wszystkie" || r.status === filtr);
      karty.clear();
      if (!raporty.length) {
        lista.replaceChildren(pusty("Jeszcze nie ma raportów", el("p", null, "Agent dodaje raport po każdym wdrożeniu: ",
          el("code", null, "python panel/narzedzia/raport.py dodaj --tytul …")), "raporty"));
        return;
      }
      if (!widoczne.length) {
        const opisy = { czeka: "Nic nie czeka na decyzję. 🎉", zaakceptowane: "Nic jeszcze nie zaakceptowano.", do_poprawy: "Nic nie wróciło do poprawy." };
        lista.replaceChildren(pusty("Pusto w tym filtrze", opisy[filtr] || "", filtr === "czeka" ? "ok" : "raporty"));
        return;
      }
      lista.replaceChildren(...widoczne.map((r, i) => {
        const k = kartaRaportu(r);
        k.style.setProperty("--i", Math.min(i, 8));
        karty.set(r.id, k);
        return k;
      }));
    }

    function podswietl(id) {
      if (!raporty) return;
      const r = raporty.find((x) => x.id === id);
      if (!r) {
        toast("Nie ma takiego raportu (może został usunięty).", "info");
        return;
      }
      if (filtr !== "wszystkie" && r.status !== filtr) {
        filtr = "wszystkie";
        rysuj();
      }
      const k = karty.get(id);
      if (!k) return;
      requestAnimationFrame(() => {
        k.scrollIntoView({ block: "center", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
        k.classList.remove("podswietlony");
        void k.offsetWidth;
        k.classList.add("podswietlony");
        setTimeout(() => k.classList.remove("podswietlony"), 2600);
      });
    }

    async function pobierz(wymus) {
      try {
        const d = await ctx.api("/api/raporty");
        const lista2 = (d && d.raporty) || [];
        const s = JSON.stringify(lista2);
        blad = null;
        if (s !== sygnatura || wymus) {
          sygnatura = s;
          raporty = lista2;
          rysuj();
        }
        const n = typeof d.czeka === "number" ? d.czeka : lista2.filter((r) => r.status === "czeka").length;
        ctx.licznik("raporty", n);
      } catch (e) {
        blad = e;
        sygnatura = "";
        raporty = null;
        rysuj();
      }
    }

    let stop = null;
    return {
      el: korzen,
      async pokaz(p) {
        const cel = p && p.raport;
        await pobierz(false);
        if (cel) podswietl(cel);
        if (!stop) stop = ctx.odpytuj(() => pobierz(false), 30000);
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
