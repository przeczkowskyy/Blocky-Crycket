// Agent: rozmowy z Claude Code (subskrypcja osoby przy komputerze). Wątki, odpowiedź na żywo (SSE), tryby, głosówki.

import { el, ikona, czasTemu, dataKrotka, toast, awatar, pusty, stanBledu, ladowanie, czasTrwania, skroc, odmiana } from "../wspolne/ui.js";
import { md } from "../wspolne/markdown.js";
import { dyktafon } from "../wspolne/dyktafon.js";

const enc = encodeURIComponent;

const TRYBY_DOMYSLNE = [
  { id: "plan", nazwa: "Plan", opis: "Tylko czyta i planuje — niczego nie zmienia." },
  { id: "praca", nazwa: "Praca", opis: "Edytuje pliki i używa dozwolonych narzędzi; resztę odmawia." },
  { id: "auto", nazwa: "Auto", opis: "Sam decyduje o narzędziach — największa swoboda." },
];
const IKONY_KONTEKSTU = { raport: "raporty", studio: "studio", notatka: "notatka", migawka: "migawka", plik: "notatka" };
const PODPOWIEDZI = [
  "Co zostało do zrobienia w aktywnej fazie?",
  "Podsumuj raporty, które czekają na akceptację.",
  "Jakie decyzje czekają na zatwierdzenie i co polecasz?",
];

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

export default {
  id: "agent",
  tytul: "Agent",
  ikona: "agent",
  kolejnosc: 50,
  utworz(ctx) {
    const s = {
      stan: null,            // /api/agent/stan
      bladStanu: null,
      watki: [],
      aktywny: czytaj("bc.agent.watek", null),
      trwa: false,
      strumien: null,
      ostatniN: -1,
      proby: 0,
      kontekst: [],
      tryb: czytaj("bc.agent.tryb", null),
      wyswietlone: new Set(),
      tekstNaZywo: "",
      ramka: 0,
      wysylanie: false,
    };

    // ------------------------------------------------------------------ szkielet
    const listaWatkow = el("ul", { class: "watki-lista" });
    const nowyBtn = el("button", { type: "button", class: "przycisk glowny maly" }, ikona("plus"), el("span", null, "Nowa"));
    const szuflada = el("aside", { class: "agent-watki", "aria-label": "Rozmowy" },
      el("div", { class: "agent-watki-nagl" }, el("h2", null, "Rozmowy"), nowyBtn,
        el("button", { type: "button", class: "przycisk cichy ikonowy tylko-telefon", "aria-label": "Zamknij listę", onclick: () => szufladaOtwarta(false) }, ikona("zamknij"))),
      listaWatkow);
    const zaslona = el("div", { class: "agent-zaslona", onclick: () => szufladaOtwarta(false) });

    const tytulWatku = el("h1", { class: "agent-tytul" }, "Nowa rozmowa");
    const statusWatku = el("span", { class: "agent-status" });
    const stopBtn = el("button", { type: "button", class: "przycisk grozny maly", hidden: true }, ikona("stop"), el("span", null, "Stop"));
    const nagl = el("header", { class: "agent-nagl" },
      el("button", { type: "button", class: "przycisk cichy ikonowy tylko-telefon", "aria-label": "Lista rozmów", onclick: () => szufladaOtwarta(true) }, ikona("menu")),
      el("div", { class: "agent-nagl-tekst" }, tytulWatku, statusWatku), stopBtn);

    const wiadomosci = el("div", { class: "agent-wiadomosci" });
    const naZywo = el("div", { class: "agent-na-zywo" });
    const przewijak = el("div", { class: "agent-przewijak", role: "log", "aria-live": "polite" }, wiadomosci, naZywo);

    const chipyKontekstu = el("div", { class: "chipy agent-kontekst" });
    const pole = el("textarea", { class: "pole agent-pole", rows: 1, placeholder: "Napisz do agenta…", "aria-label": "Wiadomość do agenta" });
    const wyslijBtn = el("button", { type: "button", class: "przycisk glowny ikonowy agent-wyslij", "aria-label": "Wyślij", title: "Wyślij (Enter)" }, ikona("wyslij"));
    const tryby = el("div", { class: "przelacznik maly agent-tryby", role: "radiogroup", "aria-label": "Tryb pracy agenta" });
    const opisTrybu = el("p", { class: "cichy-tekst agent-opis-trybu" });
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
      el("div", { class: "agent-tryby-rzad" }, tryby, opisTrybu));

    const czat = el("section", { class: "agent-czat" }, nagl, przewijak, pisz);
    const blokada = el("div", { class: "agent-blokada", hidden: true });
    const korzen = el("div", { class: "widok-pelny agent" }, szuflada, zaslona, czat, blokada);

    // ------------------------------------------------------------------ pomocnicze
    function szufladaOtwarta(tak) {
      korzen.classList.toggle("szuflada-otwarta", !!tak);
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

    function listaTrybow() {
      const t = (s.stan && Array.isArray(s.stan.tryby) && s.stan.tryby.length) ? s.stan.tryby : TRYBY_DOMYSLNE;
      return t;
    }
    function trybDozwolony(id) {
      return ctx.ja.lokalny || id !== "auto";
    }
    function rysujTryby() {
      const t = listaTrybow();
      if (!s.tryb || !t.some((x) => x.id === s.tryb) || !trybDozwolony(s.tryb)) {
        const dom = (s.stan && s.stan.tryb_domyslny) || (ctx.konfiguracja.agent && ctx.konfiguracja.agent.tryb_domyslny) || "praca";
        s.tryb = t.some((x) => x.id === dom) && trybDozwolony(dom) ? dom : (t.find((x) => trybDozwolony(x.id)) || t[0]).id;
      }
      tryby.replaceChildren(...t.map((x) => {
        const b = el("button", {
          type: "button", role: "radio", class: "przelacznik-opcja" + (x.id === s.tryb ? " aktywny" : ""),
          "aria-checked": x.id === s.tryb ? "true" : "false", disabled: !trybDozwolony(x.id),
          title: trybDozwolony(x.id) ? x.opis || "" : "Z telefonu najwyżej tryb Praca",
        }, x.nazwa || x.id);
        b.addEventListener("click", () => {
          s.tryb = x.id;
          zapisz("bc.agent.tryb", x.id);
          rysujTryby();
        });
        return b;
      }));
      const wybrany = t.find((x) => x.id === s.tryb);
      opisTrybu.textContent = wybrany ? wybrany.opis || "" : "";
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

    function ustawTrwa(tak) {
      s.trwa = !!tak;
      stopBtn.hidden = !s.trwa;
      wyslijBtn.disabled = s.trwa || s.wysylanie;
      statusWatku.replaceChildren(s.trwa ? el("span", { class: "pracuje" }, el("span", { class: "kropka-pulsujaca" }), "agent pracuje…") : "");
      korzen.classList.toggle("pracuje", s.trwa);
    }

    // ------------------------------------------------------------------ wiadomości
    function dymek(w) {
      const rola = w.rola || "system";
      if (rola === "narzedzie") {
        // zapisane jako „Nazwa: opis” — pokazujemy tak samo jak na żywo (pogrubiona nazwa · opis)
        const t = String(w.tekst || "");
        const dw = t.indexOf(": ");
        const nazwa = dw > 0 && dw < 60 ? t.slice(0, dw) : "";
        return el("div", { class: "wiad wiad-narzedzie", dataset: { nr: w.nr } },
          ikona("narzedzie"), el("span", { class: "narzedzie-tekst", title: t },
            nazwa ? el("strong", null, nazwa) : null, nazwa ? " · " + skroc(t.slice(dw + 2), 200) : skroc(t, 220)));
      }
      if (rola === "system") {
        return el("div", { class: "wiad wiad-system", dataset: { nr: w.nr } }, el("span", null, w.tekst || ""));
      }
      if (rola === "user") {
        return el("div", { class: "wiad wiad-user", dataset: { nr: w.nr } },
          el("div", { class: "wiad-meta" }, el("strong", null, w.kto || "Ty"), w.czas ? el("span", { title: dataKrotka(w.czas) }, czasTemu(w.czas)) : null),
          (w.kontekst || []).length ? el("div", { class: "chipy" }, w.kontekst.map((k) => el("span", { class: "chip niebieski" }, ikona(IKONY_KONTEKSTU[k.typ] || "link"), skroc(k.etykieta || k.cel, 36)))) : null,
          el("div", { class: "wiad-tekst" }, w.tekst || ""));
      }
      return el("div", { class: "wiad wiad-agent", dataset: { nr: w.nr } },
        el("div", { class: "wiad-meta" }, el("span", { class: "wiad-znak", "aria-hidden": "true" }, ikona("agent")), el("strong", null, "Agent"),
          w.czas ? el("span", { title: dataKrotka(w.czas) }, czasTemu(w.czas)) : null),
        el("div", { class: "md wiad-tekst", html: md(w.tekst || "") }));
    }

    function dodajWiadomosc(w) {
      if (w.nr !== undefined && w.nr !== null) {
        const klucz = String(w.nr);
        if (s.wyswietlone.has(klucz)) return false;
        s.wyswietlone.add(klucz);
      }
      wiadomosci.appendChild(dymek(w));
      return true;
    }

    function powitanie() {
      return el("div", { class: "agent-powitanie" },
        el("div", { class: "agent-powitanie-znak", "aria-hidden": "true" }, ikona("agent")),
        el("h2", null, "O co chcesz zapytać?"),
        el("p", { class: "cichy-tekst" }, "Agent to Claude Code na komputerze z panelem: zna sejf, kod gry i Roblox Studio. Pracuje na subskrypcji osoby przy tym komputerze."),
        el("div", { class: "agent-podpowiedzi" }, PODPOWIEDZI.map((p) => el("button", {
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
        case "narzedzie":
          naZywo.appendChild(el("div", { class: "wiad wiad-narzedzie na-zywo" }, ikona("narzedzie"),
            el("span", { class: "narzedzie-tekst" }, el("strong", null, z.nazwa || "narzędzie"), z.opis ? " · " + skroc(z.opis, 200) : "")));
          s.tekstNaZywo = "";
          naDol();
          break;
        case "wiadomosc": {
          const w = z.wiadomosc || {};
          if (w.rola === "assistant" || w.rola === "narzedzie") {
            if (s.ramka) cancelAnimationFrame(s.ramka);
            s.ramka = 0;
            wyczyscNaZywo();
          }
          const pow = wiadomosci.querySelector(".agent-powitanie");
          if (pow) pow.remove();
          if (w.rola === "user" && w.nr !== undefined) {
            // wiadomość dodana optymistycznie (bez numeru) — podmień zamiast dublować
            const tymczasowa = wiadomosci.querySelector(".wiad-user.tymczasowa");
            if (tymczasowa && !s.wyswietlone.has(String(w.nr))) {
              s.wyswietlone.add(String(w.nr));
              tymczasowa.replaceWith(dymek(w));
              break;
            }
          }
          dodajWiadomosc(w);
          naDol();
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
          // połączenie zerwane w trakcie pracy — wznawiamy od następnego zdarzenia
          if (s.proby++ < 6) {
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

    // ------------------------------------------------------------------ wątki
    function rysujListeWatkow() {
      if (!s.watki.length) {
        listaWatkow.replaceChildren(el("li", { class: "cichy-tekst watki-pusto" }, "Jeszcze nie ma rozmów."));
        return;
      }
      listaWatkow.replaceChildren(...s.watki.map((w) => el("li", null, el("button", {
        type: "button", class: "watek" + (w.id === s.aktywny ? " aktywny" : ""), "aria-current": w.id === s.aktywny ? "true" : null,
        onclick: () => {
          szufladaOtwarta(false);
          if (w.id !== s.aktywny) wybierzWatek(w.id);
        },
      },
      el("span", { class: "watek-tytul" }, w.trwa ? el("span", { class: "kropka-pulsujaca", title: "pracuje" }) : null, w.tytul || "Rozmowa"),
      el("span", { class: "cichy-tekst" }, czasTemu(w.ostatnio || w.utworzono) + " · " + (w.wiadomosci || 0) + " " + odmiana(w.wiadomosci || 0, ["wiadomość", "wiadomości", "wiadomości"]))))));
    }

    async function wczytajWatki() {
      try {
        const d = await ctx.api("/api/agent/watki");
        s.watki = (d && d.watki) || [];
        s.watki.sort((a, b) => String(b.ostatnio || b.utworzono || "").localeCompare(String(a.ostatnio || a.utworzono || "")));
      } catch (e) {
        s.watki = [];
      }
      rysujListeWatkow();
    }

    function nowaRozmowa() {
      zamknijStrumien();
      s.aktywny = null;
      zapisz("bc.agent.watek", null);
      s.wyswietlone.clear();
      wyczyscNaZywo();
      ustawTrwa(false);
      tytulWatku.textContent = "Nowa rozmowa";
      wiadomosci.replaceChildren(powitanie());
      rysujListeWatkow();
      szufladaOtwarta(false);
    }

    function wybierzWatek(id) {
      zamknijStrumien();
      s.aktywny = id;
      zapisz("bc.agent.watek", id);
      s.wyswietlone.clear();
      wyczyscNaZywo();
      ustawTrwa(false);
      wiadomosci.replaceChildren(ladowanie("Wczytuję rozmowę…"));
      rysujListeWatkow();
      wczytajWatek(id);
    }

    async function wczytajWatek(id, opcje = {}) {
      let w;
      try {
        w = await ctx.api("/api/agent/watki/" + enc(id));
      } catch (e) {
        if (id !== s.aktywny) return;
        if (e.status === 404) {
          nowaRozmowa();
          return;
        }
        wiadomosci.replaceChildren(stanBledu(e, "Rozmowa"));
        return;
      }
      if (id !== s.aktywny) return;
      tytulWatku.textContent = w.tytul || "Rozmowa";
      s.wyswietlone.clear();
      wiadomosci.replaceChildren();
      wyczyscNaZywo();
      const lista = w.wiadomosci || [];
      for (const m of lista) dodajWiadomosc(m);
      if (!lista.length) wiadomosci.appendChild(powitanie());
      if (opcje.poKoncu) wiadomosci.appendChild(el("div", { class: "wiad wiad-system" }, el("span", null, opcje.poKoncu)));
      ustawTrwa(!!w.trwa);
      naDol(true);
      if (w.trwa && !s.strumien) polacz(id, 0);
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
          const w = await ctx.api("/api/agent/watki", { metoda: "POST", cialo: { tytul: skroc(tekst.replace(/\s+/g, " "), 60) } });
          id = w && w.id;
          if (!id) throw new Error("Serwer nie utworzył rozmowy.");
          s.aktywny = id;
          zapisz("bc.agent.watek", id);
          tytulWatku.textContent = w.tytul || skroc(tekst, 60);
          s.wyswietlone.clear();
          wiadomosci.replaceChildren();
        }
        const pow = wiadomosci.querySelector(".agent-powitanie");
        if (pow) pow.remove();
        const tymczasowa = dymek({ rola: "user", tekst, kto: ctx.ja.kto, czas: new Date().toISOString(), kontekst });
        tymczasowa.classList.add("tymczasowa");
        wiadomosci.appendChild(tymczasowa);
        naDol(true);
        const cialo = { tekst, tryb: s.tryb };
        if (kontekst.length) cialo.kontekst = kontekst;
        const r = await ctx.api("/api/agent/watki/" + enc(id) + "/wiadomosc", { metoda: "POST", cialo });
        if (r && r.nr !== undefined && r.nr !== null) {
          if (s.wyswietlone.has(String(r.nr))) tymczasowa.remove();
          else {
            s.wyswietlone.add(String(r.nr));
            tymczasowa.dataset.nr = String(r.nr);
            tymczasowa.classList.remove("tymczasowa");
          }
        }
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
    wyslijBtn.addEventListener("click", wyslij);
    nowyBtn.addEventListener("click", nowaRozmowa);
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
      szuflada.hidden = true;
      korzen.classList.add("zablokowany");
    }
    function odblokuj() {
      blokada.hidden = true;
      czat.hidden = false;
      szuflada.hidden = false;
      korzen.classList.remove("zablokowany");
    }

    async function sprawdzStan() {
      if (ctx.statyczny) {
        zablokuj(pusty("W podglądzie agent nie działa", "To lustro tylko do odczytu. Z agentem porozmawiasz w panelu uruchomionym na komputerze.", "oko"));
        return false;
      }
      try {
        s.stan = await ctx.api("/api/agent/stan");
        s.bladStanu = null;
      } catch (e) {
        s.bladStanu = e;
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
      odblokuj();
      rysujTryby();
      return true;
    }

    rysujKontekst();
    rysujTryby();
    wiadomosci.replaceChildren(powitanie());
    let pierwszy = true;
    let stopOdpytywania = null;

    return {
      el: korzen,
      async pokaz(p) {
        p = p || {};
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
        if (p.watek && p.watek !== s.aktywny) {
          s.aktywny = p.watek;
          pierwszy = true;
        }
        if (pierwszy) {
          pierwszy = false;
          await wczytajWatki();
          if (s.aktywny) wybierzWatek(s.aktywny);
          else nowaRozmowa();
        } else {
          wczytajWatki();
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
        szufladaOtwarta(false);
      },
    };
  },
};
