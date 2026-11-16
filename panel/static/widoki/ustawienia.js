// Ustawienia: kim jesteś, wejście z telefonu, stan systemu, informacje o panelu.

import { el, zamien, ikona, toast, karta, pusty, stanBledu, ladowanie, kopiuj, awatar } from "../wspolne/ui.js";

// Nazwy modułów serwera po ludzku + podpowiedź naprawy, gdy moduł nie działa.
const MODULY = {
  sejf: { nazwa: "Sejf Obsidiana (plan, sieć)", naprawa: "Sprawdź, czy folder B&C/ jest w repozytorium i czy konfiguracja.json wskazuje właściwy sejf." },
  gitsync: { nazwa: "Synchronizacja (git)", naprawa: "Zainstaluj Git for Windows i upewnij się, że panel działa w folderze repozytorium." },
  obecnosc: { nazwa: "Kto pracuje", naprawa: "Uruchom panel ponownie; jeśli nie pomoże — zajrzyj do logu panelu." },
  studio: { nazwa: "Roblox Studio (MCP)", naprawa: "Otwórz Roblox Studio z włączonym serwerem MCP (Assistant → MCP) i odśwież." },
  podglad: { nazwa: "Podgląd 3D (migawki)", naprawa: "Migawki wymagają połączenia ze Studio; podgląd istniejących działa bez niego." },
  analityka: { nazwa: "Analityka gry", naprawa: "Wpisz universeId i placeId gry w panel/konfiguracja.json." },
  telemetria: { nazwa: "Telemetria gry (Open Cloud)", naprawa: "Jak ją włączyć, pokazuje zakładka Analityka → Telemetria gry." },
  assety: { nazwa: "Assety (rejestr grafik)", naprawa: "Plik assets/manifest.json musi być poprawnym JSON-em — zapisuje go pipeline grafik (tools/manifest.py)." },
  raporty: { nazwa: "Raporty i komentarze", naprawa: "Sprawdź, czy folder panel/dane jest zapisywalny (OneDrive potrafi go blokować)." },
  agent: { nazwa: "Agent (Claude Code)", naprawa: "Zainstaluj Claude Code i zaloguj się: w terminalu „claude”, potem /login." },
  glos: { nazwa: "Głosówki (transkrypcja)", naprawa: "Opcjonalne: transkrypcja potrzebuje faster-whisper na komputerze z panelem (patrz INSTALACJA.md)." },
  statyczny: { nazwa: "Lustro tylko do odczytu", naprawa: "Opcjonalne: eksport dla podglądu z telefonu bez włączonego komputera." },
};

function znacznik(ok, ostrzezenie) {
  const klasa = ok ? "ok" : ostrzezenie ? "uwaga" : "zle";
  return el("span", { class: "znacznik " + klasa, role: "img", "aria-label": ok ? "działa" : ostrzezenie ? "uwaga" : "nie działa" },
    ikona(ok ? "ok" : ostrzezenie ? "ostrzezenie" : "krzyzyk"));
}

function wartosc(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "boolean") return v ? "tak" : "nie";
  if (typeof v === "object") {
    const s = JSON.stringify(v);
    return s.length > 140 ? s.slice(0, 139) + "…" : s;
  }
  return String(v);
}

export default {
  id: "ustawienia",
  tytul: "Ustawienia",
  ikona: "ustawienia",
  kolejnosc: 80,
  utworz(ctx) {
    const kKto = karta("Kim jesteś", "uzytkownik");
    const kTelefon = karta("Telefon", "telefon");
    const kZdrowie = karta("Stan systemu", "zdrowie", { klasa: "karta-zdrowie" });
    const kO = karta("O panelu", "info");
    const odswiezZdrowie = el("button", { class: "przycisk cichy ikonowy", type: "button", "aria-label": "Sprawdź ponownie", title: "Sprawdź ponownie" }, ikona("odswiez"));
    kZdrowie.akcje.appendChild(odswiezZdrowie);

    const korzen = el("div", { class: "widok ustawienia" },
      el("header", { class: "nagl-widoku" }, el("div", null, el("h1", null, "Ustawienia"),
        el("p", { class: "cichy-tekst" }, "Ustawienia tej przeglądarki i stan panelu na komputerze."))),
      el("div", { class: "siatka" }, kKto.el, kTelefon.el, kZdrowie.el, kO.el));

    // ------------------------------------------------------------------ kim jesteś
    /** Zatwierdzanie decyzji (Karol albo Paweł) = przeglądarka z kluczem zatwierdzania (ciasteczko z linku
     *  --klucz-zatwierdzania) albo osoba przy komputerze z panelem — nie wpisane imię. ctx.ja.decydent; stary serwer
     *  bez tego pola: ctx.ja.game_director. */
    function wierszGameDirectora() {
      const nowy = "decydent" in ctx.ja;
      const gd = !!(nowy ? ctx.ja.decydent : ctx.ja.game_director);
      const opisTak = ctx.ja.game_director
        ? "Ta przeglądarka ma klucz zatwierdzania: w Planie → Decyzje możesz zatwierdzać i odrzucać propozycje (to zmiana kanonu w Rejestrze decyzji). Panel podpisze decyzję imieniem zapisanym wyżej i datą — bez zapisanego imienia decyzji nie zapisze."
        : "Jesteś przy komputerze z panelem: w Planie → Decyzje możesz zatwierdzać i odrzucać propozycje (to zmiana kanonu w Rejestrze decyzji). Panel podpisze decyzję imieniem zapisanym wyżej i datą — bez zapisanego imienia decyzji nie zapisze (imię z gita nie wystarczy).";
      return el("div", { class: "wiersz gd-wiersz" },
        el("span", { class: "znacznik " + (gd ? "ok" : "uwaga") }, ikona("klodka")),
        el("span", { class: "wiersz-tekst" },
          el("strong", null, "Zatwierdzanie decyzji: " + (gd ? "tak" : "nie")),
          gd
            ? el("span", { class: "cichy-tekst" }, opisTak)
            : el("span", { class: "cichy-tekst" },
              "Decyzje zatwierdza Karol albo Paweł — w panelu przy komputerze z panelem albo z kluczem zatwierdzania; samo imię go nie daje. Na komputerze, na którym działa panel, uruchom ",
              el("code", null, "python panel/serwer.py --klucz-zatwierdzania"),
              " i otwórz wypisany link w tej przeglądarce (przez tunel: dopisz ", el("code", null, "&gd=…"), " do adresu z kodem dostępu). Odpowiadać na pytania i pracować na zadaniach może każdy.")));
    }

    function rysujKto() {
      let zapisane = "";
      try {
        zapisane = localStorage.getItem("bc.kto") || "";
      } catch (e) { /* nic */ }
      // Podpowiedź z gita tylko jako samo imię (pierwszy wyraz) — podpis trafia do publicznych plików sejfu.
      const podpowiedz = ctx.ja.lokalny ? String(ctx.ja.gospodarz || "").trim().split(/\s+/)[0] || "" : "";
      const pole = el("input", { class: "pole", value: zapisane || podpowiedz, maxlength: "40", placeholder: "np. Karol", autocomplete: "given-name", "aria-label": "Twoje imię" });
      const zapisz = el("button", { class: "przycisk glowny", type: "submit" }, ikona("ok"), el("span", null, "Zapisz"));
      const form = el("form", { class: "formularz" },
        el("div", { class: "kto-podglad" }, awatar(ctx.ja.kto || "?"), el("div", null,
          el("strong", null, ctx.ja.kto || "gość"),
          el("p", { class: "cichy-tekst" }, ctx.statyczny ? "Podgląd tylko do odczytu" : ctx.ja.lokalny ? "Na komputerze z panelem" : "Połączenie zdalne (np. telefon)"))),
        el("label", { class: "etykieta" }, "Imię widoczne dla zespołu"),
        el("div", { class: "pole-z-przyciskiem" }, pole, zapisz),
        ctx.ja.gospodarz && ctx.ja.lokalny ? el("p", { class: "cichy-tekst" }, "Na tym komputerze Git podpisuje się jako „" + ctx.ja.gospodarz + "”.") : null,
        el("p", { class: "cichy-tekst" }, "Imię zapamiętuje ta przeglądarka — na telefonie ustaw je osobno."),
        ctx.statyczny ? null : wierszGameDirectora());
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const v = pole.value.trim();
        if (!v) {
          toast("Wpisz imię.", "blad");
          pole.focus();
          return;
        }
        ctx.ustawKto(v);
        toast("Zapisano: " + v, "ok");
        rysujKto();
      });
      kKto.cialo.replaceChildren(form);
    }

    // ------------------------------------------------------------------ telefon
    async function rysujTelefon() {
      const c = kTelefon.cialo;
      if (ctx.statyczny) return c.replaceChildren(el("p", { class: "cichy-tekst" }, "To jest podgląd tylko do odczytu — działa bez włączonego komputera."));
      if (!ctx.ja.lokalny) {
        return c.replaceChildren(el("p", { class: "cichy-tekst" }, "Jesteś połączony zdalnie. Adresy i kod dostępu widać tylko na komputerze, na którym działa panel."));
      }
      c.replaceChildren(ladowanie());
      let d;
      try {
        d = await ctx.api("/api/dostep");
      } catch (e) {
        return c.replaceChildren(stanBledu(e, "Dostęp z telefonu"));
      }
      const czesci = [];
      if (d.lan && (d.adresy || []).length) {
        czesci.push(el("p", null, "Otwórz na telefonie (ta sama sieć Wi-Fi) jeden z adresów — kod dostępu jest już w linku:"));
        czesci.push(el("ul", { class: "lista adresy" }, d.adresy.map((a) => el("li", { class: "wiersz adres" },
          el("code", { class: "adres-tekst" }, a),
          el("button", {
            type: "button", class: "przycisk maly", "aria-label": "Kopiuj adres",
            onclick: async () => toast((await kopiuj(a)) ? "Skopiowano adres." : "Nie udało się skopiować — zaznacz adres ręcznie.", "ok"),
          }, ikona("kopiuj"), el("span", null, "Kopiuj"))))));
        czesci.push(el("p", { class: "cichy-tekst" }, "Kod działa jak hasło — nie wysyłaj go nikomu spoza zespołu. Telefon zapamięta dostęp na 30 dni."));
      } else {
        czesci.push(el("div", { class: "podpowiedz" }, ikona("info"),
          el("div", null, el("strong", null, "Wejście z telefonu jest wyłączone"),
            el("p", null, d.podpowiedz || "Uruchom panel z opcją --lan, żeby wejść z telefonu w tej samej sieci Wi-Fi."),
            el("p", { class: "cichy-tekst" }, "Polecenie: ", el("code", null, "python panel/serwer.py --lan")))));
      }
      // agent z telefonu = zdalne sterowanie komputerem, więc domyślnie wyłączony (agent.zdalnie w konfiguracji lokalnej)
      const zdalnie = !!(ctx.konfiguracja.agent && ctx.konfiguracja.agent.zdalnie);
      const przelacz = el("button", { type: "button", class: "przycisk maly" + (zdalnie ? "" : " glowny") },
        el("span", null, zdalnie ? "Wyłącz" : "Włącz"));
      przelacz.addEventListener("click", async () => {
        przelacz.disabled = true;
        try {
          const o = await ctx.api("/api/konfiguracja/lokalna", { metoda: "POST", cialo: { agent_zdalnie: !zdalnie } });
          ctx.konfiguracja.agent = Object.assign({}, ctx.konfiguracja.agent, o.agent);
          toast(o.agent.zdalnie ? "Agent z telefonu włączony." : "Agent z telefonu wyłączony.", "ok");
        } catch (e) {
          toast(e.message || "Nie udało się zmienić ustawienia.", "blad");
        }
        rysujTelefon();
      });
      czesci.push(el("div", { class: "wiersz telefon-agent" },
        el("span", { class: "znacznik " + (zdalnie ? "ok" : "uwaga") }, ikona("agent")),
        el("span", { class: "wiersz-tekst" },
          el("strong", null, zdalnie ? "Agent z telefonu: włączony" : "Agent z telefonu: wyłączony"),
          el("span", { class: "cichy-tekst" }, zdalnie
            ? "Każdy, kto ma kod dostępu, może z telefonu zlecać agentowi pracę na tym komputerze (najwyżej w trybie Praca)."
            : "Dla bezpieczeństwa z agentem rozmawia się tylko przy tym komputerze. Po włączeniu każdy, kto ma kod dostępu, będzie mógł zlecać mu pracę z telefonu.")),
        przelacz));
      const zadania = await wierszZadanAgenta();
      if (zadania) czesci.push(zadania);
      c.replaceChildren(...czesci);
    }

    // Zadania przypisane do agenta tej osoby (16.11.2026): samo uruchamianie wydaje JEJ tokeny Claude, więc włącza
    // je tylko osoba przy swoim komputerze (konfiguracja lokalna, domyślnie wyłączone).
    async function wierszZadanAgenta() {
      if (!ctx.jest("zadania_agenta")) return null;
      let za;
      try {
        za = await ctx.api("/api/zadania-agenta");
      } catch (e) {
        return null;
      }
      const auto = !!za.auto;
      const przelacz = el("button", { type: "button", class: "przycisk maly" + (auto ? "" : " glowny"), disabled: !za.ja },
        el("span", null, auto ? "Wyłącz" : "Włącz"));
      przelacz.addEventListener("click", async () => {
        przelacz.disabled = true;
        try {
          const o = await ctx.api("/api/zadania-agenta/auto", { metoda: "POST", cialo: { auto: !auto } });
          toast(o.auto ? "Zadania Twojego agenta będą się uruchamiać same." : "Zadania Twojego agenta uruchamiasz przyciskiem.", "ok");
        } catch (e) {
          toast(e.message || "Nie udało się zmienić ustawienia.", "blad");
        }
        rysujTelefon();
      });
      const kto = za.ja
        ? "Ten komputer należy do: " + za.ja + ". Zadania z „agent: " + za.ja + "” idą na jego koncie Claude."
        : "Panel nie wie, czyj to komputer (git podaje: „" + (za.ja_nazwa || "brak imienia") + "”). Ustaw raz: git config bc.osoba \"Imię\" i zrestartuj panel.";
      return el("div", { class: "wiersz telefon-agent" },
        el("span", { class: "znacznik " + (auto ? "ok" : "uwaga") }, ikona("agent")),
        el("span", { class: "wiersz-tekst" },
          el("strong", null, auto ? "Zadania mojego agenta: uruchamiają się same" : "Zadania mojego agenta: uruchamiam przyciskiem"),
          el("span", { class: "cichy-tekst" }, kto + (auto
            ? " Panel sam bierze kolejne zadanie przypisane do Ciebie (po jednym naraz), gdy jest włączony."
            : " Po włączeniu panel sam weźmie kolejne zadanie przypisane do Ciebie — to wydaje Twoje tokeny.")),
          za.auto_blad ? el("span", { class: "naprawa" }, za.auto_blad) : null),
        przelacz);
    }

    // ------------------------------------------------------------------ stan systemu
    async function rysujZdrowie() {
      const c = kZdrowie.cialo;
      c.replaceChildren(ladowanie("Sprawdzam…"));
      odswiezZdrowie.disabled = true;
      let z;
      try {
        z = await ctx.api("/api/zdrowie", { czas: 30000 });
      } catch (e) {
        odswiezZdrowie.disabled = false;
        return c.replaceChildren(stanBledu(e, "Stan systemu"));
      }
      odswiezZdrowie.disabled = false;
      const r = z.rdzen || {};
      const wiersze = [];
      wiersze.push(el("li", { class: "wiersz zdrowie-wiersz" }, znacznik(!!r.python_ok),
        el("span", { class: "wiersz-tekst" }, el("strong", null, "Python " + (r.python || "?")),
          !r.python_ok ? el("span", { class: "naprawa" }, "Potrzebny Python 3.9 albo nowszy.") : null)));
      wiersze.push(el("li", { class: "wiersz zdrowie-wiersz" }, znacznik(!!r.git),
        el("span", { class: "wiersz-tekst" }, el("strong", null, "Git"), el("span", { class: "cichy-tekst" }, r.git || "nie znaleziono"),
          !r.git ? el("span", { class: "naprawa" }, "Zainstaluj Git for Windows.") : null)));
      wiersze.push(el("li", { class: "wiersz zdrowie-wiersz" }, znacznik(!!r.repo_git, true),
        el("span", { class: "wiersz-tekst" }, el("strong", null, "Repozytorium"), el("span", { class: "cichy-tekst sciezka" }, r.repo || ""),
          !r.repo_git ? el("span", { class: "naprawa" }, "Folder panelu nie jest korzeniem repozytorium git — synchronizacja może nie działać.") : null)));
      if (typeof r.wolne_miejsce_gb === "number") {
        const malo = r.wolne_miejsce_gb < 2;
        wiersze.push(el("li", { class: "wiersz zdrowie-wiersz" }, znacznik(!malo, true),
          el("span", { class: "wiersz-tekst" }, el("strong", null, "Wolne miejsce: " + r.wolne_miejsce_gb.toLocaleString("pl-PL") + " GB"),
            malo ? el("span", { class: "naprawa" }, "Mało miejsca na dysku — migawki i nagrania mogą się nie zapisać.") : null)));
      }
      const moduly = z.moduly || {};
      const szczegoly = z.szczegoly || {};
      const nazwy = Object.keys(moduly);
      for (const n of Object.keys(MODULY)) if (!nazwy.includes(n) && szczegoly[n]) nazwy.push(n);
      const wierszeModulow = nazwy.map((n) => {
        const m = moduly[n] || {};
        const opis = MODULY[n] || { nazwa: n, naprawa: "" };
        const sz = szczegoly[n];
        const szOk = !(sz && (sz.ok === false || sz.blad));
        const ok = m.ok !== false && szOk;
        const wBudowie = m.blad === "moduł jeszcze nie istnieje";
        const uwaga = !ok && (wBudowie || n === "glos" || n === "statyczny" || (m.ok !== false && !szOk));
        const powod = m.ok === false ? (wBudowie ? "Ta część panelu jest jeszcze w budowie." : m.blad) : (sz && (sz.powod || sz.blad)) || "";
        return el("li", { class: "wiersz zdrowie-wiersz" }, znacznik(ok, uwaga),
          el("span", { class: "wiersz-tekst" },
            el("strong", null, opis.nazwa),
            !ok && powod ? el("span", { class: "cichy-tekst" }, String(powod)) : null,
            !ok && !wBudowie && opis.naprawa ? el("span", { class: "naprawa" }, ikona("zarowka"), opis.naprawa) : null,
            sz && typeof sz === "object" && Object.keys(sz).length ? el("details", { class: "zdrowie-szczegoly" },
              el("summary", null, "Szczegóły"),
              el("dl", null, Object.entries(sz).flatMap(([k, v]) => [el("dt", null, k), el("dd", null, wartosc(v))]))) : null));
      });
      const ileZle = nazwy.filter((n) => (moduly[n] || {}).ok === false).length;
      zamien(c,
        el("p", { class: "cichy-tekst" }, nazwy.length ? (ileZle ? ileZle + " z " + nazwy.length + " części panelu nie działa." : "Wszystkie części panelu działają.") : ""),
        el("ul", { class: "lista zdrowie" }, wiersze, wierszeModulow));
    }
    odswiezZdrowie.addEventListener("click", rysujZdrowie);

    // ------------------------------------------------------------------ o panelu
    function rysujO() {
      const gra = ctx.konfiguracja.gra || {};
      const pozycje = [
        ["Wersja panelu", ctx.ja.wersja || "?"],
        ["Gra", gra.nazwa || "BLOCKY & CRYCKET"],
        ["Tryb", ctx.statyczny ? "podgląd tylko do odczytu" : ctx.ja.lokalny ? "lokalny (ten komputer)" : "zdalny"],
      ];
      if (ctx.konfiguracja.port) pozycje.push(["Port", String(ctx.konfiguracja.port)]);
      if (gra.universeId) pozycje.push(["Universe ID", String(gra.universeId)]);
      if (gra.placeId) pozycje.push(["Place ID", String(gra.placeId)]);
      const sejfy = (ctx.konfiguracja.sejfy || []).map((s) => s.nazwa || s.id).join(", ");
      if (sejfy) pozycje.push(["Sejfy", sejfy]);
      zamien(kO.cialo,
        el("dl", { class: "opis-lista" }, pozycje.flatMap(([k, v]) => [el("dt", null, k), el("dd", null, v)])),
        gra.placeId ? el("a", { class: "przycisk", href: "https://www.roblox.com/games/" + encodeURIComponent(gra.placeId), target: "_blank", rel: "noopener noreferrer" },
          ikona("zewnetrzny"), el("span", null, "Strona gry na Roblox")) : null,
        el("p", { class: "cichy-tekst" }, "Mózgiem projektu jest sejf B&C/ — panel tylko go pokazuje. Raporty, komentarze i migawki leżą w panel/dane/ i trafiają do repozytorium (publicznego)."));
    }

    window.addEventListener("bc:kto", () => {
      if (korzen.isConnected) rysujKto();
    });

    return {
      el: korzen,
      pokaz() {
        rysujKto();
        rysujTelefon();
        rysujO();
        if (ctx.statyczny) kZdrowie.cialo.replaceChildren(pusty("Podgląd tylko do odczytu", "Stan systemu widać w panelu na komputerze.", "oko"));
        else rysujZdrowie();
      },
      ukryj() {},
    };
  },
};
