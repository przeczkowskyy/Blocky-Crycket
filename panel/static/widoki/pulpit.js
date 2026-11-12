// Pulpit: stan gry na jednym ekranie — faza, kto pracuje, co czeka, co teraz, synchronizacja, ostatnia migawka.

import { el, dopisz, zamien, ikona, czasTemu, toast, arkusz, awatar, karta, pusty, stanBledu, ladowanie, odmiana, skroc } from "../wspolne/ui.js";
import { mdLinia } from "../wspolne/markdown.js";

const enc = encodeURIComponent;

export function postepFazy(f) {
  if (!f) return 0;
  let p = Number(f.postep);
  if (!isFinite(p) || f.postep === null || f.postep === undefined) {
    const poz = f.pozycje || [];
    p = poz.length ? poz.filter((x) => x.zrobione).length / poz.length : 0;
  } else if (p > 1) p = p / 100;
  return Math.max(0, Math.min(1, p));
}

const PRIORYTETY = { wysoki: "czerwien", "średni": "zloto", sredni: "zloto", niski: "niebieski" };

export function chipPriorytetu(p) {
  if (!p) return null;
  return el("span", { class: "chip " + (PRIORYTETY[p] || ""), title: "Priorytet" }, p);
}

function nazwaFazy(f) {
  return String(f.nazwa || "").replace(/^[▶►\s]+/, "");
}

export default {
  id: "pulpit",
  tytul: "Pulpit",
  ikona: "pulpit",
  kolejnosc: 10,
  utworz(ctx) {
    // --- nagłówek (bohater)
    const powitanie = el("span", { class: "hero-powitanie" });
    const heroFaza = el("div", { class: "hero-faza" });
    const hero = el("section", { class: "karta hero" },
      el("div", { class: "hero-tlo", "aria-hidden": "true" }),
      powitanie,
      el("h1", { class: "hero-tytul" }, (ctx.konfiguracja.gra && ctx.konfiguracja.gra.nazwa) || "BLOCKY & CRYCKET"),
      heroFaza);

    const kCzeka = karta("Czeka na Ciebie", "raporty", { klasa: "karta-czeka" });
    const kTeraz = karta("Teraz", "ogien", { klasa: "karta-teraz" });
    const kKto = karta("Kto pracuje", "zespol", { klasa: "karta-kto" });
    const kSync = karta("Synchronizacja", "git", { klasa: "karta-sync" });
    const kAgent = karta("Napisz do agenta", "agent", { klasa: "karta-agent" });
    const kMigawka = karta("Ostatnia migawka", "migawka", { klasa: "karta-migawka" });

    for (const k of [kCzeka, kTeraz, kKto, kSync, kMigawka]) k.cialo.appendChild(ladowanie());

    // --- szybkie pole do agenta
    if (!ctx.statyczny) {
      const pole = el("textarea", { class: "pole", rows: 2, placeholder: "Np. „Podsumuj, co zostało w Fazie 1”", "aria-label": "Wiadomość do agenta" });
      const wyslij = () => {
        const t = pole.value.trim();
        if (!t) {
          pole.focus();
          return;
        }
        pole.value = "";
        ctx.idz("agent", { tekst: t });
      };
      pole.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
          e.preventDefault();
          wyslij();
        }
      });
      kAgent.cialo.append(pole, el("div", { class: "rzad-przyciskow" },
        el("span", { class: "cichy-tekst" }, "Enter — przejdź do rozmowy"),
        el("button", { class: "przycisk glowny", type: "button", onclick: wyslij }, ikona("strzalka"), el("span", null, "Do agenta"))));
    }

    // Trzy kolumny na szerokim ekranie (bez dziur pod niskimi kartami); na telefonie kolumny „znikają”
    // (display: contents) i karty układają się jedna pod drugą w kolejności z CSS (order).
    const siatka = el("div", { class: "pulpit-kolumny" },
      el("div", { class: "kolumna" }, kCzeka.el, kKto.el),
      el("div", { class: "kolumna" }, ctx.statyczny ? null : kAgent.el, kSync.el, kMigawka.el),
      el("div", { class: "kolumna" }, kTeraz.el));
    const korzen = el("div", { class: "widok pulpit" }, hero, siatka);

    let stop = null;
    let ostatnieDane = {};

    // ------------------------------------------------------------------ rysowanie kart
    function rysujHero(plan, blad) {
      const kto = ctx.ja.kto && ctx.ja.kto !== "gość" ? ctx.ja.kto : "";
      powitanie.textContent = kto ? "Cześć, " + kto + "!" : "Panel zespołu";
      heroFaza.replaceChildren();
      if (blad || !plan) {
        heroFaza.append(el("span", { class: "cichy-tekst" }, blad ? "Plan z sejfu jeszcze niedostępny." : ""));
        return;
      }
      const fazy = (plan.roadmapa && plan.roadmapa.fazy) || [];
      const f = fazy.find((x) => x.aktywna) || fazy.find((x) => postepFazy(x) < 1) || fazy[0];
      if (!f) {
        heroFaza.append(el("span", { class: "cichy-tekst" }, "Roadmapa jest jeszcze pusta."));
        return;
      }
      const p = postepFazy(f);
      const poz = f.pozycje || [];
      const zrob = poz.filter((x) => x.zrobione).length;
      dopisz(heroFaza,
        el("a", { class: "hero-faza-nazwa", href: "#/plan?zakladka=harmonogram" },
          el("span", { class: "chip zloto" }, ikona("flaga"), f.aktywna ? "aktywna faza" : "faza"),
          el("strong", null, nazwaFazy(f))),
        f.status_tekst ? el("span", { class: "cichy-tekst" }, f.status_tekst) : null,
        el("div", { class: "pasek duzy", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(Math.round(p * 100)) },
          el("div", { class: "pasek-wypelnienie", style: { width: Math.round(p * 100) + "%" } })),
        el("div", { class: "hero-postep" },
          el("strong", null, Math.round(p * 100) + "%"),
          el("span", { class: "cichy-tekst" }, poz.length ? zrob + " z " + poz.length + " " + odmiana(poz.length, ["pozycji", "pozycji", "pozycji"]) + " gotowe" : "")));
    }

    function rysujCzeka(d, blad) {
      const c = kCzeka.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Raporty"));
      const czekajace = (d.raporty || []).filter((r) => r.status === "czeka");
      const n = typeof d.czeka === "number" ? d.czeka : czekajace.length;
      ctx.licznik("raporty", n);
      if (!n) {
        return c.replaceChildren(el("div", { class: "czeka-zero" },
          el("span", { class: "czeka-liczba zero" }, ikona("ok")),
          el("div", null, el("strong", null, "Nic nie czeka"), el("p", { class: "cichy-tekst" }, "Wszystkie raporty z wdrożeń są rozpatrzone."))));
      }
      c.replaceChildren(
        el("a", { class: "czeka-gora", href: "#/raporty" },
          el("span", { class: "czeka-liczba" }, String(n)),
          el("div", null, el("strong", null, odmiana(n, ["raport czeka", "raporty czekają", "raportów czeka"])),
            el("p", { class: "cichy-tekst" }, "na akceptację albo odpowiedź"))),
        el("ul", { class: "lista" }, czekajace.slice(0, 3).map((r) => el("li", null,
          el("button", { type: "button", class: "wiersz wiersz-klik", onclick: () => ctx.idz("raporty", { raport: r.id }) },
            awatar(r.kto, { maly: true }),
            el("span", { class: "wiersz-tekst" }, el("strong", null, r.tytul || "(bez tytułu)"),
              el("span", { class: "cichy-tekst" }, (r.kto || "ktoś") + " · " + czasTemu(r.czas))),
            r.rodzaj === "pytanie" ? el("span", { class: "chip zloto" }, "pytanie") : null,
            ikona("prawo", { klasa: "wiersz-strzalka" }))))));
    }

    function rysujTeraz(plan, blad) {
      const c = kTeraz.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Zadania"));
      const sekcje = (plan.zadania && plan.zadania.sekcje) || [];
      const pierwsza = sekcje.find((s) => (s.pozycje || []).some((p) => !p.zrobione)) || sekcje[0];
      if (!pierwsza) return c.replaceChildren(pusty("Brak zadań", "Lista zadań w sejfie jest pusta."));
      const otwarte = (pierwsza.pozycje || []).filter((p) => !p.zrobione);
      kTeraz.akcje.replaceChildren(el("a", { class: "przycisk cichy maly", href: "#/plan?zakladka=zadania" }, "Wszystkie"));
      if (!otwarte.length) return c.replaceChildren(pusty("Wszystko zrobione", "W sekcji „" + pierwsza.nazwa + "” nie ma otwartych zadań.", "ok"));
      zamien(c,
        el("p", { class: "cichy-tekst sekcja-nazwa" }, pierwsza.nazwa),
        el("ul", { class: "lista zadania-lista" }, otwarte.slice(0, 6).map((p) => el("li", { class: "wiersz zadanie-wiersz" },
          el("span", { class: "pole-wyboru", "aria-hidden": "true" }),
          el("span", { class: "md md-linia wiersz-tekst", html: mdLinia(p.tekst_md) }),
          chipPriorytetu(p.priorytet)))),
        otwarte.length > 6 ? el("p", { class: "cichy-tekst" }, "…i jeszcze " + (otwarte.length - 6) + " w tej sekcji.") : null);
    }

    function rysujKto(ob, blad) {
      const c = kKto.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Obecność"));
      const panel = ob.panel || [];
      const studio = ob.studio || {};
      const git = ob.git || [];
      const czesci = [];
      czesci.push(el("p", { class: "etykieta" }, "Na panelu"));
      if (panel.length) {
        czesci.push(el("ul", { class: "lista osoby" }, panel.map((o) => el("li", { class: "wiersz" },
          el("span", { class: "awatar-z-kropka" }, awatar(o.kto), el("span", { class: "kropka-online" })),
          el("span", { class: "wiersz-tekst" }, el("strong", null, o.kto || "ktoś"),
            el("span", { class: "cichy-tekst" }, "ogląda: " + ctx.nazwaWidoku(o.widok || "pulpit") + (o.lokalny ? "" : " · zdalnie"))),
          el("span", { class: "cichy-tekst" }, czasTemu(o.od || o.ostatnio))))));
      } else czesci.push(el("p", { class: "cichy-tekst" }, "Nikogo poza Tobą."));

      czesci.push(el("p", { class: "etykieta" }, "W Roblox Studio"));
      const osobyStudio = studio.osoby || [];
      if (!studio.dostepne) czesci.push(el("p", { class: "cichy-tekst" }, "Studio niepodłączone do panelu."));
      else if (!osobyStudio.length) czesci.push(el("p", { class: "cichy-tekst" }, "Nikt nie ma teraz otwartego miejsca."));
      else czesci.push(el("div", { class: "chipy" }, osobyStudio.map((o) => el("span", { class: "chip zielen" }, ikona("studio"), o.nazwa))));

      if (git.length) {
        czesci.push(el("p", { class: "etykieta" }, "Ostatnie zmiany w repozytorium"));
        czesci.push(el("ul", { class: "lista commity" }, git.slice(0, 4).map((g) => el("li", { class: "wiersz" },
          awatar(g.autor, { maly: true }),
          el("span", { class: "wiersz-tekst" }, el("span", { class: "commit-temat" }, g.temat || ""),
            el("span", { class: "cichy-tekst" }, (g.autor || "") + " · " + czasTemu(g.ostatnio)))))));
      }
      c.replaceChildren(...czesci);
    }

    function rysujSync(g, blad) {
      const c = kSync.cialo;
      kSync.akcje.replaceChildren();
      if (blad) return c.replaceChildren(stanBledu(blad, "Git"));
      const zmianyPanelu = Array.isArray(g.zmiany_panelu) ? g.zmiany_panelu.length : Number(g.zmiany_panelu) || 0;
      const doPobrania = Number(g.do_pobrania) || 0;
      const doWyslania = Number(g.do_wyslania) || 0;
      const kafel = (liczba, opis, kolor) => el("div", { class: "licznik-kafel " + (liczba ? kolor : "") },
        el("strong", null, String(liczba)), el("span", null, opis));
      const czesci = [
        el("div", { class: "liczniki-kafle" },
          kafel(doPobrania, "do pobrania", "niebieski"),
          kafel(zmianyPanelu, odmiana(zmianyPanelu, ["zmiana panelu", "zmiany panelu", "zmian panelu"]) + " do wysłania", "zloto"),
          doWyslania ? kafel(doWyslania, odmiana(doWyslania, ["commit", "commity", "commitów"]) + " nie wysłane", "fiolet") : null),
        el("p", { class: "cichy-tekst" }, "Gałąź ", el("code", null, g.galaz || "?"),
          g.ostatni_fetch ? " · sprawdzono " + czasTemu(g.ostatni_fetch) : "",
          g.czyste === false && !zmianyPanelu ? " · są inne niezapisane zmiany w repo" : ""),
      ];
      if (ctx.ja.lokalny && !ctx.statyczny) {
        const bPobierz = el("button", { class: "przycisk", type: "button" }, ikona("pobierz"), el("span", null, "Pobierz"));
        const bWyslij = el("button", { class: "przycisk glowny", type: "button", disabled: !zmianyPanelu && !doWyslania }, ikona("wypchnij"), el("span", null, "Wyślij"));
        bPobierz.addEventListener("click", async () => {
          bPobierz.disabled = true;
          try {
            const r = await ctx.api("/api/git/pobierz", { metoda: "POST", czas: 120000 });
            toast(r && r.ok === false ? "Pobieranie nie wyszło: " + skroc(r.wyjscie, 200) : "Pobrano najnowsze zmiany.", r && r.ok === false ? "blad" : "ok");
          } catch (e) {
            toast("Pobieranie nie wyszło: " + e.message, "blad");
          } finally {
            bPobierz.disabled = false;
            odswiez();
          }
        });
        bWyslij.addEventListener("click", () => oknoWysylania(g, zmianyPanelu));
        czesci.push(el("div", { class: "rzad-przyciskow" }, bPobierz, bWyslij));
      } else if (!ctx.statyczny) {
        czesci.push(el("p", { class: "cichy-tekst" }, "Pobieranie i wysyłanie działa na komputerze z panelem."));
      }
      c.replaceChildren(...czesci);
    }

    function oknoWysylania(g, ile) {
      const lista = Array.isArray(g.zmiany_panelu) ? g.zmiany_panelu : [];
      const pole = el("input", { class: "pole", placeholder: "np. Raport z HUD i komentarze", maxlength: "120", "aria-label": "Opis zmian" });
      const przycisk = el("button", { class: "przycisk glowny szeroki", type: "submit" }, ikona("wypchnij"), el("span", null, "Wyślij do repozytorium"));
      const form = el("form", { class: "formularz" },
        el("p", { class: "cichy-tekst" }, "Wyślę tylko dane panelu (raporty, komentarze, migawki) — " + ile + " " + odmiana(ile, ["plik", "pliki", "plików"]) + ". Kod gry i sejf zostają bez zmian."),
        lista.length ? el("ul", { class: "lista pliki-lista" }, lista.slice(0, 12).map((z) => el("li", { class: "cichy-tekst" }, el("code", null, z.plik || String(z)), z.stan ? " · " + z.stan : ""))) : null,
        el("label", { class: "etykieta" }, "Opis (opcjonalnie)"), pole, przycisk);
      const ark = arkusz({ tytul: "Wyślij zmiany panelu", tresc: form });
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        przycisk.disabled = true;
        try {
          const r = await ctx.api("/api/git/wyslij", { metoda: "POST", cialo: pole.value.trim() ? { opis: pole.value.trim() } : {}, czas: 120000 });
          if (r && r.ok === false) throw new Error(skroc(r.wyjscie || "nieznany błąd", 240));
          toast(r && r.commit ? "Wysłano (" + String(r.commit).slice(0, 7) + ")." : "Wysłano.", "ok");
          ark.zamknij();
        } catch (err) {
          toast("Wysyłanie nie wyszło: " + err.message, "blad");
          przycisk.disabled = false;
        } finally {
          odswiez();
        }
      });
    }

    function rysujMigawke(d, blad) {
      const c = kMigawka.cialo;
      if (blad) return c.replaceChildren(stanBledu(blad, "Podgląd"));
      const migawki = d.migawki || [];
      let m = migawki[0];
      if (d.najnowsza && typeof d.najnowsza === "object") m = d.najnowsza;
      else if (typeof d.najnowsza === "string") m = migawki.find((x) => x.id === d.najnowsza) || m;
      if (!m) return c.replaceChildren(pusty("Brak migawek", "Migawkę świata gry robi się w widoku Podgląd albo poleceniem agenta.", "migawka"));
      const zrzut = (m.zrzuty || [])[0];
      const otworz = () => ctx.idz("podglad", { migawka: m.id });
      c.replaceChildren(el("button", { type: "button", class: "migawka-mini", onclick: otworz, "aria-label": "Otwórz migawkę w podglądzie 3D" },
        zrzut ? el("img", { src: ctx.plik("/api/podglad/" + enc(m.id) + "/plik/" + enc(zrzut)), alt: m.tytul || "migawka", loading: "lazy" })
          : el("span", { class: "migawka-zastepcza" }, ikona("podglad")),
        el("span", { class: "migawka-opis" },
          el("strong", null, m.tytul || "Migawka"),
          el("span", { class: "cichy-tekst" }, [(m.kto || ""), m.czas ? czasTemu(m.czas) : "", m.czesci ? m.czesci + " " + odmiana(m.czesci, ["część", "części", "części"]) : ""].filter(Boolean).join(" · ")),
          el("span", { class: "chip niebieski" }, ikona("oko"), "Otwórz w 3D"))));
    }

    // ------------------------------------------------------------------ pobieranie
    const bierz = (sciezka, modul) => (ctx.jest(modul) ? ctx.api(sciezka) : Promise.reject(Object.assign(new Error("moduł wyłączony"), { status: 404 })));

    async function odswiez() {
      const [plan, rap, ob, git, pod] = await Promise.allSettled([
        bierz("/api/sejf/plan", "sejf"), bierz("/api/raporty", "raporty"), bierz("/api/obecnosc", "obecnosc"),
        bierz("/api/git/stan", "gitsync"), bierz("/api/podglad", "podglad"),
      ]);
      const sygn = (r) => (r.status === "fulfilled" ? JSON.stringify(r.value) : "!" + (r.reason && r.reason.message));
      const rysuj = (klucz, r, fn) => {
        const s = sygn(r);
        if (ostatnieDane[klucz] === s) return;
        ostatnieDane[klucz] = s;
        try {
          fn(r.status === "fulfilled" ? r.value || {} : null, r.status === "rejected" ? r.reason : null);
        } catch (e) {
          console.warn("pulpit: " + klucz, e);
        }
      };
      rysuj("hero", plan, rysujHero);
      rysuj("teraz", plan, rysujTeraz);
      rysuj("czeka", rap, rysujCzeka);
      rysuj("kto", ob, rysujKto);
      rysuj("sync", git, rysujSync);
      rysuj("migawka", pod, rysujMigawke);
    }

    window.addEventListener("bc:kto", () => {
      ostatnieDane.hero = null;
      odswiez();
    });

    return {
      el: korzen,
      pokaz() {
        odswiez();
        if (!stop) stop = ctx.odpytuj(odswiez, 15000);
      },
      ukryj() {
        if (stop) stop();
        stop = null;
      },
    };
  },
};
