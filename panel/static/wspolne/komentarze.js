// Wątek komentarzy do dowolnego celu: raportu, grupy w Studio, notatki, migawki.
// komentarze(ctx, cel, {naZmiane?}) → HTMLElement; cel = {typ, cel, etykieta?}.

import { el, ikona, czasTemu, dataKrotka, toast, awatar, ladowanie, odmiana } from "./ui.js";
import { mdEl } from "./markdown.js";
import { dyktafon } from "./dyktafon.js";

export function komentarze(ctx, cel, opcje = {}) {
  const lista = el("ul", { class: "lista komentarze-lista" });
  const stanEl = el("div", { class: "komentarze-stan" }, ladowanie("Ładuję komentarze…"));
  const w = el("div", { class: "komentarze" }, stanEl, lista);
  let liczba = 0;
  let zGlosu = false;

  function wiersz(k) {
    const glos = k.zrodlo === "glos";
    return el("li", { class: "komentarz" },
      awatar(k.kto, { maly: true }),
      el("div", { class: "komentarz-cialo" },
        el("div", { class: "komentarz-meta" },
          el("strong", null, k.kto || "ktoś"),
          el("span", { class: "cichy-tekst", title: dataKrotka(k.czas) }, czasTemu(k.czas)),
          glos ? el("span", { class: "chip maly-chip fiolet", title: "Spisane z głosówki" }, ikona("glos"), "głosówka") : null),
        mdEl(k.tekst || "", { klasa: "komentarz-tekst" })));
  }

  function rysuj(dane) {
    const kom = (dane && dane.komentarze) || [];
    kom.sort((a, b) => String(a.czas || "").localeCompare(String(b.czas || "")));
    liczba = kom.length;
    lista.replaceChildren(...kom.map(wiersz));
    stanEl.replaceChildren(kom.length ? "" : el("p", { class: "cichy-tekst komentarze-brak" }, "Jeszcze nikt nic nie napisał."));
    if (typeof opcje.naZmiane === "function") opcje.naZmiane(liczba);
  }

  async function odswiez() {
    try {
      const q = "/api/komentarze?typ=" + encodeURIComponent(cel.typ) + "&cel=" + encodeURIComponent(cel.cel);
      rysuj(await ctx.api(q));
    } catch (e) {
      lista.replaceChildren();
      stanEl.replaceChildren(el("p", { class: "cichy-tekst komentarze-brak" },
        e.status === 404 ? "Komentarze jeszcze nie działają na tym panelu." : "Nie udało się wczytać komentarzy: " + e.message));
    }
  }

  // --- pole dodawania
  if (!ctx.statyczny) {
    const pole = el("textarea", { class: "pole", rows: 2, placeholder: "Napisz komentarz…", "aria-label": "Treść komentarza" });
    const wyslij = el("button", { type: "button", class: "przycisk glowny" }, ikona("wyslij"), el("span", null, "Dodaj"));
    const dyk = dyktafon(ctx, {
      etykieta: "Nagraj komentarz głosem",
      naTekst: (t) => {
        pole.value = (pole.value.trim() ? pole.value.trim() + " " : "") + t;
        zGlosu = true;
        pole.focus();
      },
    });
    pole.addEventListener("input", () => {
      if (!pole.value.trim()) zGlosu = false;
    });
    pole.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        dodaj();
      }
    });
    async function dodaj() {
      const tekst = pole.value.trim();
      if (!tekst) {
        pole.focus();
        return;
      }
      wyslij.disabled = true;
      try {
        await ctx.api("/api/komentarze", { metoda: "POST", cialo: { cel, tekst, zrodlo: zGlosu ? "glos" : "tekst" } });
        pole.value = "";
        zGlosu = false;
        await odswiez();
      } catch (e) {
        toast("Nie udało się dodać komentarza: " + e.message, "blad");
      } finally {
        wyslij.disabled = false;
      }
    }
    wyslij.addEventListener("click", dodaj);
    w.appendChild(el("div", { class: "komentarze-pisz" }, pole, el("div", { class: "komentarze-przyciski" }, dyk, wyslij)));
  } else {
    w.appendChild(el("p", { class: "cichy-tekst" }, "Podgląd tylko do odczytu — komentarze dodaje się w panelu."));
  }

  w.odswiez = odswiez;
  w.liczba = () => liczba;
  w.opisLiczby = () => liczba + " " + odmiana(liczba, ["komentarz", "komentarze", "komentarzy"]);
  odswiez();
  return w;
}
