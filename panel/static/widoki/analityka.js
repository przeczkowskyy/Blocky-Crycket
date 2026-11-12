// Analityka — gracze, wizyty, oceny (publiczne API Roblox), stan Roblox Studio i konsola.
// Odświeżanie co 30 s, tylko gdy widok jest widoczny.

import { ikona, ladowanie, pusty } from "../wspolne/ui.js";

const CSS = new URL("./analityka.css", import.meta.url).href;
const ODSWIEZ_MS = 30000;

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

    const aktualizacja = el("span", { class: "cichy-tekst an-akt" });
    const odswiezBtn = el("button", { class: "przycisk cichy ikonowy", type: "button", "aria-label": "Odśwież", title: "Odśwież", onclick: () => wczytaj(true) }, ikona("odswiez"));
    const gra = el("div", { class: "an-gra" });
    const wykres = el("div", { class: "karta an-wykres-karta" });
    const studio = el("div", { class: "karta an-studio" });
    const dodatki = el("div", { class: "siatka an-dodatki" });
    const root = el("section", { class: "an" },
      el("header", { class: "an-gora" }, el("div", {}, el("h1", { class: "an-tytul", text: "Analityka" }), aktualizacja), odswiezBtn),
      gra, wykres, studio, dodatki);

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
        wykres.hidden = studio.hidden = dodatki.hidden = true;
        return;
      }
      wykres.hidden = studio.hidden = dodatki.hidden = false;
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
      const t = d.telemetria || {}, r = d.robuxy || {};
      dodatki.replaceChildren(
        el("div", { class: "karta an-dodatek" },
          el("div", { class: "an-naglowek" }, el("h2", { class: "karta-tytul" }, ikona("zdrowie"), el("span", { text: "Telemetria gry" })),
            el("span", { class: "chip " + (t.podlaczona ? "zielen" : ""), text: t.podlaczona ? "podłączona" : "niepodłączona" })),
          el("p", { class: "cichy-tekst", text: t.opis || (t.podlaczona ? "Dane z gry spływają do panelu." : "Gra nie wysyła jeszcze danych do panelu.") })),
        el("div", { class: "karta an-dodatek" },
          el("div", { class: "an-naglowek" }, el("h2", { class: "karta-tytul" }, ikona("rakieta"), el("span", { text: "Robuxy" })),
            el("span", { class: "chip " + (r.dostepne ? "zielen" : ""), text: r.dostepne ? "podłączone" : "niepodłączone" })),
          el("p", { class: "cichy-tekst", text: r.opis || (r.dostepne ? "" : "Zarobki nie są jeszcze podłączone.") })));
    }

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
    return {
      el: root,
      async pokaz() {
        S.widoczny = true;
        clearInterval(S.timer);
        S.timer = setInterval(() => { if (S.widoczny && document.visibilityState === "visible") wczytaj(); }, ODSWIEZ_MS);
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
