// Karta raportu z wdrożenia (wspólna dla listy Pytania, historii, listy Pytania w zakładce Sesja i pełnego raportu):
// pytanie raportu jako tytuł („Czy akceptujesz: …?” albo własne pole `pytanie`), opis (na liście najwyżej dwa pierwsze
// zdania, reszta za „Pokaż szczegóły”; w pełnym raporcie zwinięty długi opis z „Pokaż więcej”), miniatury zrzutów,
// komponenty (Studio, notatki, migawki — w pełnym raporcie), decyzja ludzi, „Akceptuję” / „Do poprawy” z komentarzem
// (także głosem), komentarze, „Pełny raport”, „Do agenta”, „Zmień decyzję”.
//
//   const karty = kartyRaportow(ctx, { naZmiane(raport), naZmianeDecyzji(raport, kartaEl) → true, gdy przerysowała });
//   karty.zmieniaDecyzje(id) → czy przy raporcie otwarto „Zmień decyzję”
//   karty.karta(raport, { tryb: "pytanie" | "zwarta" | "pelna" })  → <article>
//     pytanie = karta na liście Pytania i w historii; zwarta = lista w zakładce Sesja; pelna = cały raport
//     (dawne `kompakt: true` = tryb „pytanie”)
//   karty.pelny(raport)  → okno z pełnym raportem (zrzuty, komponenty, migawki, komentarze)
//   karty.decyduj(raport, "zaakceptowane" | "do_poprawy" | "nieaktualne", komentarz?) → Promise<raport po zmianie>
//   opcje.przyciskNieaktualne(raport, kartaEl, o) → element obok Akceptuję / Do poprawy (albo null)

import { el, dopisz, ikona, czasTemu, dataKrotka, toast, arkusz, awatar, powiekszenie } from "./ui.js";
import { md } from "./markdown.js";
import { komentarze } from "./komentarze.js";
import { dyktafon } from "./dyktafon.js";
import { pytanieRaportu, skrotOpisu } from "./kolejka.js";

const enc = encodeURIComponent;

export const STATUSY_RAPORTU = {
  czeka: { tekst: "czeka", kolor: "zloto", ikona: "zegar" },
  zaakceptowane: { tekst: "zaakceptowany", kolor: "zielen", ikona: "ok" },
  do_poprawy: { tekst: "do poprawy", kolor: "czerwien", ikona: "krzyzyk" },
  informacja: { tekst: "informacja", kolor: "niebieski", ikona: "info" },
  nieaktualne: { tekst: "nieaktualne", kolor: "szary", ikona: null },   // zdjęty z kolejki (14.11): nie poprawiać
};
const RODZAJE = { wdrozenie: "wdrożenie", pytanie: "pytanie", informacja: "informacja" };
const IKONY_KOMPONENTOW = { studio: "studio", notatka: "notatka", plik: "notatka", migawka: "migawka" };

export function kartyRaportow(ctx, opcje = {}) {
  const rozwinieteOpisy = new Set();
  const otwarteKomentarze = new Set();
  const zmienDecyzje = new Set();

  function chipStatusu(r) {
    const s = STATUSY_RAPORTU[r.status] || { tekst: r.status || "?", kolor: "" };
    return el("span", { class: "chip " + s.kolor }, s.ikona ? ikona(s.ikona) : null, s.tekst);
  }

  function zrzuty(r, male) {
    const nazwy = r.zrzuty || [];
    if (!nazwy.length) return null;
    const obrazy = nazwy.map((n) => ({ src: ctx.plik("/api/raporty/" + enc(r.id) + "/plik/" + enc(n)), podpis: r.tytul + " — " + n }));
    return el("div", { class: "galeria" + (male ? " male" : ""), role: "list" }, obrazy.map((o, i) => el("button", {
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
        ? el("button", { type: "button", class: "chip klik komponent typ-" + c.typ, title: c.typ + ": " + c.cel, onclick: zamknijIPrzejdz(akcja) }, zawartosc)
        : el("span", { class: "chip komponent typ-" + c.typ, title: c.typ + ": " + c.cel }, zawartosc);
    });
    if (r.migawka && !k.some((c) => c.typ === "migawka")) {
      chipy.push(el("button", { type: "button", class: "chip klik niebieski", onclick: zamknijIPrzejdz(() => ctx.idz("podglad", { migawka: r.migawka })) },
        ikona("podglad"), el("span", null, "Migawka 3D")));
    }
    return chipy.length ? el("div", { class: "chipy komponenty" }, chipy) : null;
  }

  /** Przejście do innej zakładki z okna pełnego raportu zamyka okno. */
  let otwarteOkno = null;
  function zamknijIPrzejdz(fn) {
    return () => {
      if (otwarteOkno) otwarteOkno.zamknij();
      fn();
    };
  }

  /** Długi opis jest zwinięty; „Pokaż więcej” rozwija go w miejscu (klasa „rozwiniety”, styl w styl.css). */
  function opis(r, krotki) {
    if (!r.opis_md) return null;
    const tresc = el("div", { class: "md raport-opis", html: md(r.opis_md) });
    const granica = krotki ? 260 : 520;
    const dlugi = r.opis_md.length > granica || (r.opis_md.match(/\n/g) || []).length > (krotki ? 6 : 12);
    if (!dlugi) return tresc;
    const klucz = (krotki ? "k:" : "") + r.id;
    const otwarty = rozwinieteOpisy.has(klucz);
    const opakowanie = el("div", { class: "zwijany-opis" + (krotki ? " krotki" : "") + (otwarty ? " rozwiniety" : "") }, tresc);
    const przycisk = el("button", { type: "button", class: "przycisk cichy maly pokaz-wiecej", "aria-expanded": otwarty ? "true" : "false" },
      otwarty ? "Pokaż mniej" : "Pokaż więcej");
    przycisk.addEventListener("click", () => {
      const teraz = !opakowanie.classList.contains("rozwiniety");
      opakowanie.classList.toggle("rozwiniety", teraz);
      przycisk.textContent = teraz ? "Pokaż mniej" : "Pokaż więcej";
      przycisk.setAttribute("aria-expanded", teraz ? "true" : "false");
      if (teraz) rozwinieteOpisy.add(klucz);
      else rozwinieteOpisy.delete(klucz);
    });
    return el("div", { class: "zwijany-blok" }, opakowanie, przycisk);
  }

  function decyzjaInfo(r) {
    const d = r.decyzja;
    if (!d) return null;
    const s = STATUSY_RAPORTU[d.wartosc] || { tekst: d.wartosc, kolor: "" };
    const czasownik = d.wartosc === "zaakceptowane" ? "zaakceptował(a)" : d.wartosc === "do_poprawy" ? "odesłał(a) do poprawy"
      : d.wartosc === "nieaktualne" ? "oznaczył(a) jako nieaktualne" : "zdecydował(a)";
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
    const wynik = Object.assign({}, r, nowy && nowy.id ? nowy
      : { status: wartosc, decyzja: { kto: ctx.ja.kto, czas: new Date().toISOString(), wartosc, komentarz } });
    if (typeof opcje.naZmiane === "function") opcje.naZmiane(wynik);
    if (otwarteOkno && otwarteOkno.raport === r.id && otwarteOkno.el.isConnected) {
      otwarteOkno.cialo.replaceChildren(karta(wynik, { tryb: "pelna" }));   // okno pokazuje raport po zmianie
    }
    return wynik;
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
    let wToku = false;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (wToku) return;
      wToku = true;
      wyslij.disabled = true;
      try {
        await decyduj(r, "do_poprawy", pole.value.trim());
        ark.zamknij();
        toast("Odesłano do poprawy.", "ok");
      } catch (err) {
        toast("Nie udało się: " + err.message, "blad");
        wyslij.disabled = false;
      } finally {
        wToku = false;
      }
    });
  }

  /** Okno z pełnym raportem (zrzuty, komponenty, migawki, decyzja, komentarze). */
  function pelny(r) {
    if (otwarteOkno) otwarteOkno.zamknij();
    const ark = arkusz({ tytul: "Raport", tresc: karta(r, { tryb: "pelna" }), szeroki: true, naZamkniecie: () => { if (otwarteOkno === ark) otwarteOkno = null; } });
    ark.raport = r.id;
    otwarteOkno = ark;
    return ark;
  }

  function przyciski(r, kartaEl, o) {
    const tryb = o.tryb;
    const rzad = el("div", { class: "rzad-przyciskow raport-akcje" });
    const mozeDecydowac = !ctx.statyczny && (r.rodzaj === "wdrozenie" || r.rodzaj === "pytanie" || r.status === "czeka" || r.decyzja);
    const pokazDecyzje = mozeDecydowac && (r.status === "czeka" || zmienDecyzje.has(r.id));
    if (pokazDecyzje) {
      const ok = el("button", { type: "button", class: "przycisk sukces" + (tryb === "zwarta" ? " maly" : "") }, ikona("ok"), el("span", null, "Akceptuję"));
      ok.addEventListener("click", async () => {
        if (ok.disabled) return;
        ok.disabled = true;
        try {
          await decyduj(r, "zaakceptowane");
          toast("Zaakceptowano: " + (r.tytul || "raport") + ".", "ok");
        } catch (e) {
          toast("Nie udało się: " + e.message, "blad");
          ok.disabled = false;
        }
      });
      rzad.append(ok, el("button", { type: "button", class: "przycisk grozny" + (tryb === "zwarta" ? " maly" : ""), onclick: () => oknoPoprawy(r) },
        ikona("krzyzyk"), el("span", null, "Do poprawy")));
      // „Nieaktualne” (trzecia możliwość) — kontrolkę daje lista pytań (wspolne/lista_pytan.js)
      if (typeof opcje.przyciskNieaktualne === "function") {
        const n = opcje.przyciskNieaktualne(r, kartaEl, o);
        if (n) rzad.append(n);
      }
    }
    if (tryb !== "pelna") {
      rzad.appendChild(el("button", { type: "button", class: "przycisk cichy" + (tryb === "zwarta" ? " maly" : ""), onclick: () => pelny(r) },
        ikona("raporty"), el("span", null, "Pełny raport")));
    }
    let watek = null;
    if (tryb !== "zwarta") {
      const kluczWatku = tryb + ":" + r.id;
      const liczba = Number(r.komentarzy) || 0;
      const otwarty = otwarteKomentarze.has(kluczWatku);
      const bKom = el("button", { type: "button", class: "przycisk cichy" + (otwarty ? " wcisniety" : ""), "aria-expanded": otwarty ? "true" : "false" },
        ikona("komentarz"), el("span", null, "Komentarze"), el("span", { class: "licznik-przycisku" }, String(liczba)));
      watek = el("div", { class: "raport-watek", hidden: !otwarty });
      const zaladujWatek = () => {
        if (watek.firstChild) return;
        watek.appendChild(komentarze(ctx, { typ: "raport", cel: r.id, etykieta: r.tytul }, {
          naZmiane: (n) => {
            bKom.querySelector(".licznik-przycisku").textContent = String(n);
            r.komentarzy = n;
          },
        }));
      };
      if (otwarty) zaladujWatek();
      bKom.addEventListener("click", () => {
        const otworz = watek.hidden;
        watek.hidden = !otworz;
        bKom.classList.toggle("wcisniety", otworz);
        bKom.setAttribute("aria-expanded", otworz ? "true" : "false");
        if (otworz) {
          otwarteKomentarze.add(kluczWatku);
          zaladujWatek();
        } else otwarteKomentarze.delete(kluczWatku);
      });
      rzad.appendChild(bKom);
      if (!ctx.statyczny) {
        rzad.appendChild(el("button", {
          type: "button", class: "przycisk cichy",
          onclick: zamknijIPrzejdz(() => ctx.idz("agent", { kontekst: [{ typ: "raport", cel: r.id, etykieta: r.tytul }] })),
        }, ikona("agent"), el("span", null, "Do agenta")));
      }
    }
    if (mozeDecydowac && !pokazDecyzje && r.decyzja && tryb !== "zwarta") {
      rzad.appendChild(el("button", {
        type: "button", class: "przycisk cichy maly zmien-decyzje",
        onclick: () => {
          zmienDecyzje.add(r.id);
          // karta na liście albo w historii należy do listy pytań (id, klasy „sprawa”, mapa kart) — przerysowuje ją lista
          if (tryb !== "pelna" && typeof opcje.naZmianeDecyzji === "function" && opcje.naZmianeDecyzji(r, kartaEl)) return;
          kartaEl.replaceWith(karta(r, o));
        },
      }, "Zmień decyzję"));
    }
    return [rzad, watek];
  }

  function karta(r, o = {}) {
    o = Object.assign({}, o, { tryb: o.tryb || (o.kompakt ? "pytanie" : "pelna") });
    const tryb = o.tryb;
    const k = el("article", {
      class: "karta raport status-" + (r.status || "brak") + " tryb-" + tryb + (tryb !== "pelna" ? " kompakt" : ""),
      id: tryb === "pelna" ? "raport-" + r.id : null, dataset: { id: r.id },
    });
    const [akcje, watek] = przyciski(r, k, o);
    const meta = [el("strong", null, r.kto || "ktoś"), " · ",
      el("time", { datetime: r.czas || "", title: dataKrotka(r.czas) }, czasTemu(r.czas)),
      r.rodzaj && r.rodzaj !== "wdrozenie" ? " · " + (RODZAJE[r.rodzaj] || r.rodzaj) : ""];
    if (tryb === "pelna") {
      dopisz(k,
        el("div", { class: "raport-gora" },
          awatar(r.kto),
          el("div", { class: "raport-meta" },
            el("h2", { class: "raport-tytul" }, r.tytul || "(bez tytułu)"),
            el("p", { class: "cichy-tekst" }, ...meta)),
          chipStatusu(r)),
        opis(r, false),
        r.pytanie ? el("div", { class: "raport-pytanie" }, el("span", { class: "etykieta" }, ikona("pytanie"), "Pytanie"), el("div", { class: "md", html: md(r.pytanie) })) : null,
        zrzuty(r),
        komponenty(r),
        decyzjaInfo(r),
        akcje,
        watek);
      return k;
    }
    // karta-pytanie (lista Pytania, historia) i karta zwarta (Sesja): tytuł, kto i kiedy, najwyżej dwa pierwsze
    // zdania opisu; reszta opisu i pytanie agenta zwinięte za „Pokaż szczegóły”
    const pyt = pytanieRaportu(r);
    const zwarta = tryb === "zwarta";
    const { krotko, reszta } = skrotOpisu(r.opis_md, 2);
    const pytanieAgenta = !pyt.wlasne && r.pytanie
      ? el("div", { class: "raport-pytanie" }, el("span", { class: "etykieta" }, "Pytanie agenta"), el("div", { class: "md", html: md(r.pytanie) })) : null;
    const s = STATUSY_RAPORTU[r.status] || { tekst: r.status || "" };
    dopisz(k,
      el("div", { class: "sprawa-gora" },
        el("span", { class: "sprawa-zrodlo" }, "z raportu"),
        r.status !== "czeka" ? el("span", { class: "sprawa-meta status-" + (r.status || "brak") }, s.tekst) : null),
      el(zwarta ? "h3" : "h2", { class: "sprawa-tytul" }, pyt.tekst),
      el("p", { class: "cichy-tekst raport-podtytul" }, el("span", null, r.tytul || "(bez tytułu)"), " · ", ...meta),
      krotko ? el("div", { class: "md raport-opis sprawa-krotko", html: md(krotko) }) : null,
      szczegolyRaportu(r, reszta ? el("div", { class: "md raport-opis", html: md(reszta) }) : null, pytanieAgenta),
      zrzuty(r, zwarta),
      zwarta ? null : decyzjaInfo(r),
      akcje,
      watek);
    return k;
  }

  /** „Pokaż szczegóły” w karcie raportu na liście (pamięta otwarte). */
  function szczegolyRaportu(r, ...tresc) {
    if (!tresc.some(Boolean)) return null;
    const otwarte = rozwinieteOpisy.has("s:" + r.id);
    const napis = el("span", null, otwarte ? "Ukryj szczegóły" : "Pokaż szczegóły");
    const det = el("details", { class: "zwijane sprawa-szczegoly", open: otwarte },
      el("summary", null, ikona("dol"), napis), el("div", { class: "sprawa-szczegoly-tresc" }, ...tresc));
    det.addEventListener("toggle", () => {
      napis.textContent = det.open ? "Ukryj szczegóły" : "Pokaż szczegóły";
      if (det.open) rozwinieteOpisy.add("s:" + r.id);
      else rozwinieteOpisy.delete("s:" + r.id);
    });
    return det;
  }

  /** Czy przy raporcie otwarto „Zmień decyzję” (lista pytań dolicza to do podpisu karty). */
  const zmieniaDecyzje = (id) => zmienDecyzje.has(id);

  return { karta, pelny, decyduj, chipStatusu, zmieniaDecyzje };
}
