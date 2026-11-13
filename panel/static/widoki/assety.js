// Assety — okno na rejestr grafik gry (assets/manifest.json): siatka kart, pasek etapów pipeline'u, filtry, szczegóły.
// Tylko do odczytu: widok niczego nie zmienia, nie wgrywa i nie zatwierdza. Zgodę na upload do Roblox daje człowiek
// w rozmowie z agentem — tu widać jedynie, co na nią czeka.

import { el, zamien, ikona, toast, arkusz, pusty, stanBledu, ladowanie, kopiuj, czasTemu, dataKrotka, odmiana, powiekszenie } from "../wspolne/ui.js";
import { komentarze } from "../wspolne/komentarze.js";

const CSS = new URL("./assety.css", import.meta.url).href;
const ODSWIEZ_MS = 30000;
const DUZY_PLIK = 700 * 1024;          // większe obrazy w arkuszu pokazujemy z miniatury (pełny plik dopiero w powiększeniu)

// Wygląd statusów: kolor znacznika (klasy .chip ze styl.css) i ikona. Nazwy i opisy przychodzą z serwera.
const WYGLAD = {
  planned: { kolor: "szary", ikona: "zarowka" },
  generated: { kolor: "fiolet", ikona: "agent" },
  processed: { kolor: "niebieski", ikona: "narzedzie" },
  in_figma: { kolor: "niebieski", ikona: "obraz" },
  awaiting_approval: { kolor: "zloto", ikona: "klodka" },
  approved: { kolor: "zielen", ikona: "decyzja" },
  pending_studio: { kolor: "zloto", ikona: "studio" },
  in_roblox: { kolor: "zielen", ikona: "podglad" },
  done: { kolor: "zielen", ikona: "ok" },
  rejected: { kolor: "czerwien", ikona: "krzyzyk" },
};
const WYGLAD_NIEZNANY = { kolor: "", ikona: "pytanie" };
const NA_MECIE = new Set(["in_roblox", "done"]);

// status przychodzi z manifestu — „constructor” albo „toString” nie mogą trafić we właściwości Object.prototype
const wyglad = (a) => (Object.prototype.hasOwnProperty.call(WYGLAD, a.status) ? WYGLAD[a.status] : WYGLAD_NIEZNANY);

/** Dołącza arkusz stylów widoku (raz) i mówi, kiedy jest gotowy — do tego czasu widok czeka z pokazaniem się. */
function dolaczCss(href) {
  const jest = [...document.querySelectorAll("link[rel=stylesheet]")].find((l) => l.href === href);
  if (jest) return jest.sheet ? Promise.resolve() : new Promise((r) => jest.addEventListener("load", r, { once: true }));
  return new Promise((gotowe) => {
    const link = el("link", { rel: "stylesheet", href });
    link.addEventListener("load", gotowe, { once: true });
    link.addEventListener("error", gotowe, { once: true });
    document.head.append(link);
    setTimeout(gotowe, 1500);
  });
}

/** Tekst do porównań przy szukaniu: małe litery, bez polskich ogonków. */
function prosty(t) {
  return String(t == null ? "" : t).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l");
}

function rozmiarPliku(b) {
  b = Number(b) || 0;
  if (b < 1024) return b + " B";
  if (b < 1024 * 1024) return Math.round(b / 1024).toLocaleString("pl-PL") + " KB";
  return (b / 1048576).toLocaleString("pl-PL", { maximumFractionDigits: 1 }) + " MB";
}

function opisObrazu(a) {
  const czesci = [];
  if (a.wymiary && a.wymiary.length === 2) czesci.push(a.wymiary[0] + " × " + a.wymiary[1] + " px");
  if (a.rozmiar) czesci.push(rozmiarPliku(a.rozmiar));
  return czesci.join(" · ");
}

/** Link do Figmy tylko wtedy, gdy na pewno prowadzi do Figmy (adres buduje serwer, tu sprawdzamy go drugi raz). */
function adresFigmy(a) {
  return typeof a.figma_adres === "string" && a.figma_adres.startsWith("https://www.figma.com/") ? a.figma_adres : null;
}

/** Kolejność kart: najpierw to, co czeka na człowieka, potem prace w toku, gotowe, na końcu odrzucone. */
function ranga(a) {
  if (a.czeka_na_zgode) return 0;
  if (a.status === "rejected") return 3;
  return NA_MECIE.has(a.status) ? 2 : 1;
}

export default {
  id: "assety",
  tytul: "Assety",
  ikona: "assety",
  kolejnosc: 65,
  utworz(ctx) {
    const S = {
      dane: null,                 // ostatnia poprawna odpowiedź /api/assety
      blad: null,                 // błąd połączenia (obiekt Error) — gdy nie ma czego pokazać
      uwaga: "",                  // ostrzeżenie nad siatką (np. manifest chwilowo nieczytelny)
      sygnatura: "",
      filtr: { q: "", kategoria: "", status: "", etap: null, czeka: false },
      komentarzy: {},             // ścieżka obrazu -> liczba komentarzy
      przyciskiEtapow: [],
      narysowano: false,
      trwa: false,
    };

    // ------------------------------------------------------------------ szkielet widoku
    const odswiezBtn = el("button", { class: "przycisk cichy ikonowy", type: "button", title: "Odśwież z manifestu", "aria-label": "Odśwież z manifestu", onclick: () => pobierz(true) }, ikona("odswiez"));
    const baner = el("div", { class: "as-baner", hidden: true });
    const etapyEl = el("div", { class: "as-etapy", role: "group", "aria-label": "Etapy pipeline'u grafik — kliknij, żeby filtrować" });
    const zasada = el("div", { class: "as-zasada", role: "note" }, ikona("klodka"),
      el("p", null, el("strong", null, "Tylko do odczytu. "),
        "Do Roblox nic nie trafia bez wyraźnego „tak” człowieka w rozmowie z agentem — ta zakładka niczego nie wgrywa i nie zatwierdza."));
    const szukaj = el("input", {
      class: "pole", type: "search", placeholder: "Szukaj: nazwa, użycie, numer Roblox…", "aria-label": "Szukaj assetu", autocomplete: "off", spellcheck: "false", enterkeyhint: "search",
      oninput: () => ustawFiltr({ q: szukaj.value }),
      onkeydown: (e) => {
        if (e.key === "Enter") szukaj.blur();                // telefon: Enter chowa klawiaturę, wyniki są już pod spodem
      },
    });
    const wyborKategorii = el("select", { class: "pole as-wybor", "aria-label": "Kategoria", onchange: () => ustawFiltr({ kategoria: wyborKategorii.value }) });
    const wyborStatusu = el("select", { class: "pole as-wybor", "aria-label": "Status", onchange: () => ustawFiltr({ status: wyborStatusu.value, etap: null, czeka: false }) });
    const narzedzia = el("div", { class: "as-narzedzia" }, el("label", { class: "as-szukaj" }, ikona("lupa"), szukaj), wyborKategorii, wyborStatusu);
    const podsumowanie = el("div", { class: "as-podsumowanie", "aria-live": "polite" });
    const uwagaEl = el("div", { class: "as-uwaga", hidden: true });
    const siatka = el("div", { class: "as-siatka" });
    const tresc = el("div", { class: "as-tresc" }, ladowanie("Czytam rejestr grafik…"));
    const korzen = el("div", { class: "widok assety as" },
      el("header", { class: "nagl-widoku" },
        el("div", null, el("h1", null, "Assety"), el("p", { class: "cichy-tekst" },
          ctx.statyczny ? "Rejestr grafik z chwili eksportu (assets/manifest.json)." : "Na żywo z rejestru grafik (assets/manifest.json).")),
        odswiezBtn),
      baner, etapyEl, zasada, narzedzia, podsumowanie, uwagaEl, tresc);
    korzen.style.visibility = "hidden";                      // bez mignięcia nieostylowanej treści
    dolaczCss(CSS).then(() => { korzen.style.visibility = ""; });

    // ------------------------------------------------------------------ drobne klocki
    async function skopiuj(tekst, co) {
      const ok = await kopiuj(tekst);
      toast(ok ? "Skopiowano: " + co + "." : "Nie udało się skopiować — zaznacz tekst ręcznie.", ok ? "ok" : "blad");
    }

    function chipStatusu(a) {
      const w = wyglad(a);
      return el("span", { class: "chip as-status " + w.kolor, title: a.status_wyjasnienie || "" }, ikona(w.ikona), a.status_opis || a.status || "?");
    }

    /** Kratka przezroczystości z obrazem (albo zastępnik, gdy obrazu nie ma lub się nie wczytał). */
    function miniatura(a) {
      const pudelko = el("span", { class: "as-mini as-kratka" });
      const brak = (tekst) => {
        pudelko.classList.remove("as-kratka");
        pudelko.classList.add("brak");
        zamien(pudelko, ikona("obraz"), el("span", { class: "as-mini-brak" }, tekst));
      };
      const adres = a.miniatura || a.obraz;
      if (!adres) brak("brak obrazu");
      else {
        const img = el("img", { src: ctx.plik(adres), alt: "", loading: "lazy", decoding: "async", draggable: "false" });
        img.addEventListener("error", () => brak("obraz się nie wczytał"), { once: true });
        pudelko.append(img);
      }
      return pudelko;
    }

    /** Pasek postępu assetu: tyle kresek, ile etapów; bieżąca w kolorze statusu. */
    function tor(a) {
      const etapy = (S.dane && S.dane.etapy) || [];
      const w = wyglad(a);
      const meta = a.etap === etapy.length - 1 && NA_MECIE.has(a.status);
      const bezZgody = zaBramka(a) && !zgodaZapisana(a);       // za bramką, ale manifest nie ma zapisanej zgody
      const opis = (a.status === "rejected" ? "Odrzucony — poza pipeline'em"
        : a.etap == null ? "Etap nieznany"
        : "Etap " + (a.etap + 1) + " z " + etapy.length + ": " + ((etapy[a.etap] || {}).nazwa || ""))
        + (bezZgody ? " (zgoda człowieka bez zapisu w manifeście)" : "");
      return el("span", { class: ["as-tor", meta && "gotowy", a.status === "rejected" && "odrzucony"], role: "img", "aria-label": opis, title: opis },
        etapy.map((e, i) => el("span", {
          class: ["as-tor-krok", a.etap != null && i < a.etap && "zrobiony", a.etap === i && "biezacy", a.etap === i && w.kolor, bezZgody && e.bramka && "bez-zapisu"],
        })));
    }

    // ------------------------------------------------------------------ karta
    function karta(a, i) {
      const figma = adresFigmy(a);
      const liczbaKom = S.komentarzy[a.cel_komentarzy] || 0;
      const uwagi = a.uwagi || [];
      const opisKom = liczbaKom ? liczbaKom + " " + odmiana(liczbaKom, ["komentarz", "komentarze", "komentarzy"]) : "";
      const glowny = el("button", {
        type: "button", class: "as-otworz", "aria-haspopup": "dialog",
        "aria-label": a.nazwa + " — " + (a.kategoria_opis || "") + ", " + (a.status_opis || "") + (opisKom ? ", " + opisKom : "")
          + (uwagi.length ? ", uwaga: " + uwagi[0] : "") + ". Pokaż szczegóły",
        onclick: () => otworz(a),
      },
        el("span", { class: "as-mini-ramka" }, miniatura(a),
          // znaczki na rogu miniatury: ostrzeżenie (lewy) i liczba komentarzy (prawy)
          el("span", { class: "as-mini-znaki", "aria-hidden": "true" },
            uwagi.length ? el("span", { class: "as-znak as-znak-uwaga", title: uwagi.join(" ") }, ikona("ostrzezenie")) : null,
            liczbaKom ? el("span", { class: "as-znak as-znak-kom", title: opisKom }, ikona("komentarz"), String(liczbaKom)) : null)),
        el("span", { class: "as-opis" },
          el("strong", { class: "as-nazwa", title: a.nazwa }, a.nazwa),
          tor(a),
          el("span", { class: "as-meta" }, chipStatusu(a), el("span", { class: "chip" }, a.kategoria_opis || "bez kategorii")),
          el("span", { class: "as-uzycie" + (a.uzycie ? "" : " brak") }, a.uzycie || "Nie zapisano, gdzie jest użyty.")));
      const stopka = el("div", { class: "as-stopka" },
        a.roblox_id
          ? el("button", {
            type: "button", class: "przycisk cichy maly as-kopiuj", title: "Kopiuj numer obrazu Roblox", "aria-label": "Kopiuj numer obrazu Roblox " + a.roblox_id,
            onclick: () => skopiuj(a.roblox_id, "numer Roblox " + a.roblox_id),
          }, ikona("kopiuj"), el("span", { class: "as-numer" }, a.roblox_id))
          : el("span", { class: "cichy-tekst as-brak-numeru", title: a.roblox_decal ? "Jest numer decala, nie ma jeszcze numeru obrazu" : null },
            a.roblox_decal ? "tylko decal" : "bez numeru Roblox"),
        figma ? el("a", { class: "przycisk cichy maly as-figma", href: figma, target: "_blank", rel: "noopener noreferrer", title: "Otwórz w Figmie (nowa karta)" },
          ikona("zewnetrzny"), el("span", null, "Figma")) : null);
      return el("article", { class: ["karta", "as-karta", a.czeka_na_zgode && "czeka"], style: { "--i": Math.min(i, 10) } }, glowny, stopka);
    }

    // ------------------------------------------------------------------ arkusz szczegółów
    function powieksz(a) {
      const lb = powiekszenie([{ src: ctx.plik(a.obraz), podpis: [a.nazwa, opisObrazu(a)].filter(Boolean).join(" — ") }], 0);
      const okno = [...document.querySelectorAll(".lightbox")].pop();
      if (!lb || !okno) return;
      const obraz = okno.querySelector(".lb-obraz");
      if (obraz) obraz.classList.add("as-lb-obraz");         // kratka pod przezroczystym obrazem
      // Esc ma zamknąć samo powiększenie, a nie arkusz pod spodem (oba słuchają na document) — łapiemy klawisz wcześniej.
      const naEsc = (e) => {
        if (e.key !== "Escape") return;
        e.stopPropagation();
        e.preventDefault();
        lb.zamknij();
      };
      const obserwator = new MutationObserver(() => {
        if (okno.isConnected) return;
        window.removeEventListener("keydown", naEsc, true);
        obserwator.disconnect();
      });
      window.addEventListener("keydown", naEsc, true);
      obserwator.observe(document.body, { childList: true });
    }

    function wartoscZKopia(tekst, co) {
      return el("span", { class: "as-wartosc" }, el("code", null, tekst),
        el("button", { type: "button", class: "przycisk cichy maly ikonowy", title: "Kopiuj", "aria-label": "Kopiuj: " + co, onclick: () => skopiuj(tekst, co) }, ikona("kopiuj")));
    }

    function czas(iso) {
      return el("span", { title: iso }, dataKrotka(iso), el("span", { class: "cichy-tekst" }, " · " + czasTemu(iso)));
    }

    function kroki(a) {
      const etapy = (S.dane && S.dane.etapy) || [];
      if (!etapy.length || a.etap == null) return null;
      const w = wyglad(a);
      const meta = a.etap === etapy.length - 1 && NA_MECIE.has(a.status);
      return el("ol", { class: "as-kroki", "aria-label": "Droga assetu przez pipeline" }, etapy.map((e, i) => {
        const miniety = i < a.etap || meta;
        const biezacy = i === a.etap && !meta;
        // Bramkę odhaczamy tylko wtedy, gdy manifest naprawdę ma zapisaną zgodę — status „w Roblox” jej nie dowodzi
        // (np. grafiki wgrane, zanim powstał pipeline).
        const bezZapisu = !!e.bramka && miniety && !zgodaZapisana(a);
        const zrobiony = miniety && !bezZapisu;
        return el("li", { class: ["as-krok", zrobiony && "zrobiony", biezacy && "biezacy", biezacy && w.kolor, e.bramka && "bramka", bezZapisu && "bez-zapisu"] },
          el("span", { class: "as-krok-znak", "aria-hidden": "true" }, zrobiony ? ikona("ok") : e.bramka ? ikona("klodka") : null),
          el("span", { class: "as-krok-nazwa" }, e.nazwa),
          biezacy ? el("span", { class: "as-krok-stan" }, "— " + (a.status_opis || ""))
            : bezZapisu ? el("span", { class: "as-krok-stan", title: "W manifeście nie ma zapisanej zgody człowieka na ten plik" }, "— bez zapisu zgody") : null);
      }));
    }

    /** Czy manifest ma zapisaną i wciąż ważną zgodę człowieka na ten plik. */
    function zgodaZapisana(a) {
      return !!(a.zgoda && a.zgoda.jest && a.zgoda.aktualna !== false);
    }

    /** Czy asset jest już za bramką (dalej niż etap zgody). */
    function zaBramka(a) {
      const ib = ((S.dane && S.dane.etapy) || []).findIndex((e) => e.bramka);
      return ib >= 0 && a.etap != null && a.etap > ib;
    }

    function otworz(a) {
      const cel = { typ: "plik", cel: a.cel_komentarzy, etykieta: a.nazwa };
      const figma = adresFigmy(a);
      const duzy = a.rozmiar && a.rozmiar > DUZY_PLIK;
      const adresPodgladu = a.obraz ? ctx.plik(duzy ? a.miniatura || a.obraz : a.obraz) : null;
      const podglad = adresPodgladu
        ? el("button", { type: "button", class: "as-sz-podglad as-kratka", "aria-label": "Powiększ obraz " + a.nazwa, title: "Powiększ", onclick: () => powieksz(a) },
          el("img", { src: adresPodgladu, alt: a.nazwa, decoding: "async", draggable: "false" }), el("span", { class: "as-sz-lupa", "aria-hidden": "true" }, ikona("powieksz")))
        : el("div", { class: "as-sz-podglad brak" }, ikona("obraz"), el("span", null,
          a.plik ? "Pliku obrazu nie ma na komputerze z panelem."
            : (a.uwagi || []).length ? "Panel nie może pokazać tego obrazu — powód jest niżej."
            : "Ten asset nie ma jeszcze gotowego obrazu."));

      const wiersze = [];
      const wiersz = (etykieta, ...wartosci) => wiersze.push(el("dt", null, etykieta), el("dd", null, wartosci));
      const brak = (tekst) => el("span", { class: "cichy-tekst as-brak" }, tekst);
      wiersz("Gdzie użyty", a.uzycie || brak("nie zapisano"));
      wiersz("Kategoria", a.kategoria_opis + (a.kategoria && a.kategoria !== a.kategoria_opis ? " (" + a.kategoria + ")" : ""));
      if (a.roblox_id) wiersz("Numer Roblox", wartoscZKopia(a.roblox_id, "numer Roblox"), wartoscZKopia("rbxassetid://" + a.roblox_id, "adres rbxassetid"));
      else wiersz("Numer Roblox", brak(a.roblox_decal ? "jeszcze nie ma — jest tylko numer decala" : "jeszcze nie ma — asset nie jest wgrany"));
      if (a.roblox_cel) wiersz("Miejsce w grze", wartoscZKopia(a.roblox_cel, "miejsce w grze"));
      if (a.roblox_decal) wiersz("Decal Roblox", wartoscZKopia(a.roblox_decal, "numer decala"));
      if (a.moderacja) wiersz("Moderacja", a.moderacja);
      if (a.figma_wezel || figma) {
        wiersz("Figma", a.figma_wezel ? el("span", null, "węzeł ", el("code", null, a.figma_wezel)) : null,
          figma ? el("a", { class: "as-link", href: figma, target: "_blank", rel: "noopener noreferrer" }, ikona("zewnetrzny"), "Otwórz w Figmie") : null);
      }
      if (a.plik) wiersz("Plik", wartoscZKopia(a.plik, "ścieżkę pliku"));
      else wiersz("Plik", brak("jeszcze nie ma gotowego obrazu"));
      if (a.surowe) wiersz("Warianty", el("code", null, a.surowe), el("span", { class: "cichy-tekst" }, "surowe pliki zostają na komputerze, który je generował"));
      if (a.zgoda) {
        const z = a.zgoda;
        wiersz("Zgoda człowieka", !z.jest ? brak("jeszcze jej nie ma")
          : el("span", null, "jest", z.kiedy ? " · " + dataKrotka(z.kiedy) : "",
            z.aktualna === true ? " · dotyczy tego pliku" : z.aktualna === false ? " · wygasła (plik zmienił się po akceptacji)" : ""));
      } else if (zaBramka(a)) {
        wiersz("Zgoda człowieka", brak("bez zapisu w manifeście"));
      }
      if (a.utworzono) wiersz("Utworzono", czas(a.utworzono));
      if (a.zmieniono) wiersz("Zmieniono", czas(a.zmieniono));

      const historia = a.historia || [];
      const inne = Object.entries(a.inne || {});
      const miejsceKom = el("div", { class: "as-sz-kom" }, ladowanie("Ładuję komentarze…"));
      let ark = null;
      const korzenArkusza = el("div", { class: "as-szczegoly" },
        el("div", { class: "as-sz-gora" },
          el("div", { class: "as-sz-lewa" }, podglad, opisObrazu(a) ? el("p", { class: "cichy-tekst as-sz-podpis" }, opisObrazu(a)) : null),
          el("div", { class: "as-sz-prawa" },
            el("div", { class: "chipy" }, chipStatusu(a), el("span", { class: "chip" }, a.kategoria_opis || "bez kategorii")),
            a.status_wyjasnienie && !a.czeka_na_zgode ? el("p", { class: "as-sz-wyjasnienie" }, a.status_wyjasnienie) : null,   // o czekaniu mówi ramka niżej
            kroki(a))),
        a.czeka_na_zgode ? el("div", { class: "as-bramka-info", role: "note" }, ikona("klodka"),
          el("div", null,
            el("strong", null, "Czeka na zgodę człowieka"),
            el("p", null, "Agent pokazuje gotowy obraz i pyta o zgodę w rozmowie. Odpowiedź „tak”, „popraw: …” albo „odrzuć” pada tam — panel niczego nie zatwierdza i nie wgrywa."),
            el("p", { class: "as-komenda" }, "Polecenie dla agenta: ", wartoscZKopia("/asset approve " + a.nazwa, "polecenie dla agenta")))) : null,
        (a.uwagi || []).map((u) => el("div", { class: "as-uwaga" }, ikona("ostrzezenie"), el("p", null, u))),
        el("dl", { class: "opis-lista as-dane" }, wiersze),
        a.notatki ? el("section", { class: "as-sekcja" }, el("h3", { class: "etykieta" }, ikona("notatka"), "Notatki"), el("p", { class: "as-notatki" }, a.notatki)) : null,
        a.prompt ? el("details", { class: "zwijane as-prompt" },
          el("summary", null, ikona("dol"), "Prompt, z którego powstała grafika"),
          el("p", { class: "as-notatki" }, a.prompt),
          el("button", { type: "button", class: "przycisk maly", onclick: () => skopiuj(a.prompt, "prompt") }, ikona("kopiuj"), el("span", null, "Kopiuj prompt"))) : null,
        el("section", { class: "as-sekcja" }, el("h3", { class: "etykieta" }, ikona("zegar"), "Historia"),
          historia.length
            ? el("ul", { class: "lista as-historia" }, historia.map((h) => el("li", { class: "wiersz" },
              el("span", { class: "wiersz-tekst" }, el("span", null, h.opis || "Zmiana"), h.wartosc ? el("code", null, h.wartosc) : null),
              h.kiedy ? el("span", { class: "cichy-tekst", title: h.kiedy }, dataKrotka(h.kiedy)) : null)))
            : el("p", { class: "cichy-tekst" }, "Bez wcześniejszych wersji — w tym assecie nic jeszcze nie było podmieniane.")),
        inne.length ? el("section", { class: "as-sekcja" }, el("h3", { class: "etykieta" }, ikona("info"), "Pozostałe pola z manifestu"),
          el("dl", { class: "opis-lista as-dane" }, inne.flatMap(([k, v]) => [el("dt", null, k), el("dd", null, v)]))) : null,
        ctx.statyczny ? null : el("div", { class: "rzad-przyciskow" },
          el("button", {
            type: "button", class: "przycisk",
            onclick: () => {
              if (ark) ark.zamknij();
              ctx.idz("agent", { kontekst: [cel] });
            },
          }, ikona("agent"), el("span", null, "Zapytaj agenta"))),
        el("section", { class: "as-sekcja" }, el("h3", { class: "etykieta" }, ikona("komentarz"), "Komentarze"), miejsceKom));

      const liczbaPrzed = S.komentarzy[cel.cel] || 0;
      ark = arkusz({
        tytul: a.nazwa, tresc: korzenArkusza, szeroki: true,
        naZamkniecie: () => {
          if ((S.komentarzy[cel.cel] || 0) !== liczbaPrzed) rysujSiatke();   // licznik komentarzy na karcie
        },
      });
      // Wątek dokładamy po otwarciu arkusza: jego pole tekstowe nie przechwyci wtedy fokusu i arkusz nie zjedzie na dół.
      requestAnimationFrame(() => {
        zamien(miejsceKom, komentarze(ctx, cel, {
          naZmiane: (n) => {
            if (n) S.komentarzy[cel.cel] = n;
            else delete S.komentarzy[cel.cel];
          },
        }));
      });
    }

    // ------------------------------------------------------------------ filtry
    function aktywneFiltry() {
      const f = S.filtr;
      return !!(f.q.trim() || f.kategoria || f.status || f.etap != null || f.czeka);
    }

    function pasuje(a) {
      const f = S.filtr;
      if (f.czeka && !a.czeka_na_zgode) return false;
      if (f.etap != null && a.etap !== f.etap) return false;
      if (f.status && a.status !== f.status) return false;
      if (f.kategoria && (a.kategoria || "") !== (f.kategoria === "-" ? "" : f.kategoria)) return false;
      const slowa = prosty(f.q).split(/\s+/).filter(Boolean);
      if (!slowa.length) return true;
      if (!a._szukaj) {
        a._szukaj = prosty([a.nazwa, a.kategoria, a.kategoria_opis, a.status, a.status_opis, a.uzycie, a.notatki, a.roblox_id, a.roblox_cel,
          a.roblox_decal, a.figma_wezel, a.plik, a.prompt].filter(Boolean).join(" \n "));
      }
      return slowa.every((s) => a._szukaj.includes(s));
    }

    function ustawFiltr(zmiany) {
      Object.assign(S.filtr, zmiany);
      odswiezKontrolki();
      rysujSiatke();
    }

    function wyczyscFiltry() {
      szukaj.value = "";
      ustawFiltr({ q: "", kategoria: "", status: "", etap: null, czeka: false });
    }

    /** Ustawia pola filtrów i wciśnięcie kafli etapów według S.filtr (bez przebudowy — fokus zostaje na miejscu). */
    function odswiezKontrolki() {
      const f = S.filtr;
      wyborKategorii.value = f.kategoria;
      wyborStatusu.value = f.status;
      S.przyciskiEtapow.forEach((b, i) => {
        b.classList.toggle("wybrany", f.etap === i);
        b.setAttribute("aria-pressed", f.etap === i ? "true" : "false");
      });
    }

    // ------------------------------------------------------------------ rysowanie
    function rysujEtapy(d) {
      const czeka = d.czeka || 0;
      S.przyciskiEtapow = (d.etapy || []).map((e, i) => {
        const czekaTu = e.bramka ? czeka : 0;
        const liczba = e.liczba || 0;
        return el("button", {
          type: "button", class: ["as-etap", e.bramka && "bramka", !liczba && "zero", czekaTu && "czeka"], "aria-pressed": "false",
          title: e.opis || "",
          "aria-label": e.nazwa + ": " + liczba + " " + odmiana(liczba, ["asset", "assety", "assetów"]) + (czekaTu ? ", w tym " + czekaTu + " czeka na zgodę" : "") + ". " + (e.opis || ""),
          onclick: () => ustawFiltr({ etap: S.filtr.etap === i ? null : i, status: "", czeka: false }),
        },
          el("span", { class: "as-etap-gora" },
            e.bramka ? ikona("klodka") : el("span", { class: "as-etap-nr" }, String(i + 1)),
            el("span", { class: "as-etap-nazwa" }, el("span", { class: "as-pelna" }, e.nazwa), el("span", { class: "as-skrot" }, e.skrot || e.nazwa))),
          el("strong", { class: "as-etap-liczba" }, String(liczba)),
          el("span", { class: "as-etap-opis" }, czekaTu ? czekaTu + " " + odmiana(czekaTu, ["czeka", "czekają", "czeka"]) + " na „tak” człowieka" : e.opis || ""));
      });
      zamien(etapyEl, S.przyciskiEtapow);
    }

    function rysujBaner(d) {
      const czeka = d.czeka || 0;
      baner.hidden = !czeka;
      if (!czeka) return;
      zamien(baner, ikona("klodka"),
        el("p", null, czeka + " " + odmiana(czeka, ["asset czeka", "assety czekają", "assetów czeka"]) + " na zgodę człowieka przed Roblox."),
        el("button", { type: "button", class: "przycisk maly glowny", onclick: () => ustawFiltr({ czeka: true, etap: null, status: "" }) }, "Pokaż"));
    }

    function rysujWybory(d) {
      const assety = d.assety || [];
      const kategorie = new Map();
      for (const a of assety) {
        const k = a.kategoria || "-";
        const w = kategorie.get(k) || { nazwa: a.kategoria_opis || "bez kategorii", n: 0 };
        w.n++;
        kategorie.set(k, w);
      }
      zamien(wyborKategorii, el("option", { value: "" }, "Każda kategoria"),
        [...kategorie.entries()].sort((x, y) => x[1].nazwa.localeCompare(y[1].nazwa, "pl")).map(([id, w]) => el("option", { value: id }, w.nazwa + " (" + w.n + ")")));
      zamien(wyborStatusu, el("option", { value: "" }, "Każdy status"),
        (d.statusy || []).filter((s) => s.liczba).map((s) => el("option", { value: s.id }, s.nazwa + " (" + s.liczba + ")")));
      // filtr, którego wartość zniknęła z rejestru, przestaje obowiązywać
      if (S.filtr.kategoria && !kategorie.has(S.filtr.kategoria)) S.filtr.kategoria = "";
      if (S.filtr.status && !(d.liczniki || {})[S.filtr.status]) S.filtr.status = "";
      if (S.filtr.etap != null && S.filtr.etap >= (d.etapy || []).length) S.filtr.etap = null;
      if (S.filtr.czeka && !d.czeka) S.filtr.czeka = false;
      odswiezKontrolki();
    }

    function rysujPodsumowanie(widoczne, wszystkie) {
      const d = S.dane;
      const f = S.filtr;
      const czesci = [];
      if (aktywneFiltry()) {
        czesci.push(el("span", { class: "as-ile" }, widoczne + " z " + wszystkie + " " + odmiana(wszystkie, ["assetu", "assetów", "assetów"])));
        const etap = f.etap != null ? (d.etapy || [])[f.etap] : null;
        const status = f.status ? (d.statusy || []).find((s) => s.id === f.status) : null;
        const opisy = [
          f.czeka ? "czekają na zgodę" : null,
          etap ? "etap: " + etap.nazwa : null,
          status ? "status: " + status.nazwa : null,
          f.kategoria ? "kategoria: " + (wyborKategorii.selectedOptions[0] ? wyborKategorii.selectedOptions[0].textContent.replace(/ \(\d+\)$/, "") : f.kategoria) : null,
          f.q.trim() ? "szukane: „" + f.q.trim() + "”" : null,
        ].filter(Boolean);
        czesci.push(el("span", null, opisy.join(" · ")));
        czesci.push(el("button", { type: "button", class: "przycisk cichy maly as-wyczysc", onclick: wyczyscFiltry }, ikona("zamknij"), el("span", null, "Wyczyść filtry")));
      } else if (wszystkie) {
        czesci.push(el("span", { class: "as-ile" }, wszystkie + " " + odmiana(wszystkie, ["asset", "assety", "assetów"])));
      }
      if (d.zaktualizowano) czesci.push(el("span", { class: "as-kiedy", title: dataKrotka(d.zaktualizowano) }, "manifest zmieniony " + czasTemu(d.zaktualizowano)));
      zamien(podsumowanie, czesci);
    }

    function rysujSiatke() {
      const d = S.dane;
      if (!d) return;
      const wszystkie = d.assety || [];
      if (!wszystkie.length) {
        rysujPodsumowanie(0, 0);
        zamien(tresc, d.brak_manifestu
          ? pusty("Nie ma jeszcze rejestru grafik", el("p", null, "Plik ", el("code", null, d.zrodlo || "assets/manifest.json"),
            " powstanie, gdy agent pierwszy raz przeprowadzi grafikę przez pipeline. Napisz mu: ", el("code", null, "/asset"), " i opis grafiki."), "assety")
          : pusty("Rejestr grafik jest pusty", el("p", null, "W manifeście nie ma jeszcze żadnego assetu. Nową grafikę zamawia się u agenta poleceniem ",
            el("code", null, "/asset"), "."), "assety"));
        return;
      }
      const widoczne = wszystkie.map((a, i) => [a, i]).filter(([a]) => pasuje(a))
        .sort((x, y) => ranga(x[0]) - ranga(y[0]) || x[1] - y[1]).map(([a]) => a);
      rysujPodsumowanie(widoczne.length, wszystkie.length);
      if (!widoczne.length) {
        zamien(tresc, pusty("Nic nie pasuje do filtrów", el("div", { class: "as-pusty-akcja" },
          el("p", null, "Żaden z " + wszystkie.length + " " + odmiana(wszystkie.length, ["assetu", "assetów", "assetów"]) + " nie spełnia wybranych warunków."),
          el("button", { type: "button", class: "przycisk", onclick: wyczyscFiltry }, ikona("zamknij"), el("span", null, "Wyczyść filtry"))), "lupa"));
        return;
      }
      siatka.classList.toggle("as-bez-wejscia", S.narysowano);   // animacja wejścia tylko przy pierwszym pokazaniu
      zamien(siatka, widoczne.map(karta));
      if (siatka.parentNode !== tresc || tresc.children.length !== 1) zamien(tresc, siatka);
      S.narysowano = true;
    }

    function rysuj() {
      const d = S.dane;
      const jestTresc = !!d && !d.blad;
      for (const e of [etapyEl, zasada, podsumowanie]) e.hidden = !jestTresc;
      narzedzia.hidden = !jestTresc || !(d.assety || []).length;   // nie ma czego szukać ani filtrować w pustym rejestrze
      uwagaEl.hidden = !(jestTresc && S.uwaga);
      if (!uwagaEl.hidden) zamien(uwagaEl, ikona("ostrzezenie"), el("p", null, S.uwaga));
      if (!d) {
        baner.hidden = true;
        zamien(tresc, S.blad
          ? el("div", { class: "as-blad" }, stanBledu(S.blad, "Assety"),
            el("button", { type: "button", class: "przycisk", onclick: () => pobierz(true) }, ikona("odswiez"), el("span", null, "Spróbuj ponownie")))
          : ladowanie("Czytam rejestr grafik…"));
        return;
      }
      if (d.blad) {
        baner.hidden = true;
        zamien(tresc, pusty("Nie mogę odczytać rejestru grafik", el("div", { class: "as-pusty-akcja" }, el("p", null, d.blad),
          el("button", { type: "button", class: "przycisk", onclick: () => pobierz(true) }, ikona("odswiez"), el("span", null, "Spróbuj ponownie"))), "ostrzezenie"));
        return;
      }
      rysujBaner(d);
      rysujEtapy(d);
      rysujWybory(d);
      rysujSiatke();
    }

    // ------------------------------------------------------------------ dane
    async function pobierzLicznikiKomentarzy() {
      try {
        const d = await ctx.api("/api/komentarze?typ=plik", { czas: 15000 });
        const licz = {};
        for (const k of (d && d.komentarze) || []) {
          const c = k && k.cel && k.cel.cel;
          if (c) licz[c] = (licz[c] || 0) + 1;
        }
        if (JSON.stringify(licz) === JSON.stringify(S.komentarzy)) return;
        S.komentarzy = licz;
        rysujSiatke();
      } catch (e) { /* liczniki komentarzy są dodatkiem — bez nich karty działają dalej */ }
    }

    async function pobierz(recznie) {
      if (S.trwa) return;
      S.trwa = true;
      if (recznie) odswiezBtn.disabled = true;
      try {
        const d = (await ctx.api("/api/assety")) || {};
        S.blad = null;
        if (d.blad && S.dane && !S.dane.blad) {
          // manifest bywa chwilowo nieczytelny (agent właśnie go zapisuje) — zostawiamy poprzedni odczyt i mówimy o tym
          const zmiana = S.uwaga !== d.blad;
          S.uwaga = d.blad + " Pokazuję poprzedni odczyt.";
          if (zmiana) rysuj();
        } else {
          const s = JSON.stringify(d);
          const zmiana = s !== S.sygnatura || !!S.uwaga;
          S.sygnatura = s;
          S.uwaga = "";
          S.dane = d;
          if (zmiana || recznie) rysuj();
          ctx.licznik("assety", d.czeka || 0);
        }
      } catch (e) {
        if (S.dane && !S.dane.blad) {
          S.uwaga = "Nie udało się odświeżyć rejestru (" + (e.message || "błąd") + "). Pokazuję poprzedni odczyt.";
        } else {
          S.blad = e;
          S.dane = null;
          S.sygnatura = "";
        }
        rysuj();
      } finally {
        S.trwa = false;
        odswiezBtn.disabled = false;
      }
      if (S.dane && !S.dane.blad && (S.dane.assety || []).length) pobierzLicznikiKomentarzy();
    }

    let stop = null;
    return {
      el: korzen,
      async pokaz(p) {
        if (!stop) stop = ctx.odpytuj(() => pobierz(false), ODSWIEZ_MS);
        await pobierz(false);
        const nazwa = p && p.asset;
        if (!nazwa || !S.dane) return;
        const a = (S.dane.assety || []).find((x) => x.nazwa === nazwa);
        if (a) otworz(a);
        else toast("W rejestrze nie ma assetu „" + nazwa + "”.", "info");
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
