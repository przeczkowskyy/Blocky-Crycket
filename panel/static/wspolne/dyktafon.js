// Dyktafon: przycisk mikrofonu → nagranie → /api/glos → transkrypcja → naTekst(tekst).
// W bezpiecznym kontekście (localhost / https) nagrywa w przeglądarce (MediaRecorder). Na telefonie po zwykłym http
// przeglądarka nie daje mikrofonu — wtedy przycisk otwiera dyktafon telefonu (input type=file accept=audio/* capture)
// i wysyła nagrany plik tą samą drogą.

import { el, ikona, toast } from "./ui.js";

const MAKS_NAGRANIA_S = 300;
const MAKS_CZEKANIA_S = 15 * 60;

function mozeNagrywac() {
  return !!(window.isSecureContext && navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
}

function wybierzFormat() {
  const kandydaci = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4", "audio/aac"];
  for (const k of kandydaci) {
    try {
      if (window.MediaRecorder.isTypeSupported && window.MediaRecorder.isTypeSupported(k)) return k;
    } catch (e) { /* dalej */ }
  }
  return "";
}

const czekaj = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * dyktafon(ctx, {naTekst, naStan?, etykieta?}) → HTMLElement.
 * naTekst(tekst) — gotowa transkrypcja; naStan(stan) — "nagrywa" | "wysyla" | "spisuje" | "gotowe" | "blad" | "bezczynny".
 */
export function dyktafon(ctx, { naTekst, naStan, etykieta } = {}) {
  const statyczny = ctx && ctx.statyczny;
  const opis = el("span", { class: "dyktafon-opis" });
  const przycisk = el("button", { type: "button", class: "przycisk ikonowy dyktafon-przycisk", title: etykieta || "Nagraj głosówkę", "aria-label": etykieta || "Nagraj głosówkę" }, ikona("mikrofon"));
  const plikWej = el("input", { type: "file", accept: "audio/*", capture: true, hidden: true, tabindex: "-1", "aria-hidden": "true" });
  const w = el("div", { class: "dyktafon" }, przycisk, opis, plikWej);

  if (statyczny) {
    przycisk.disabled = true;
    przycisk.title = "Głosówki nie działają w podglądzie tylko do odczytu";
    return w;
  }

  let stan = "bezczynny";
  let nagrywacz = null;
  let strumien = null;
  let kawalki = [];
  let start = 0;
  let zegar = null;
  let porzucone = false;

  function ustawStan(s, tekst) {
    stan = s;
    w.dataset.stan = s;
    opis.textContent = tekst || "";
    przycisk.classList.toggle("nagrywa", s === "nagrywa");
    przycisk.disabled = s === "wysyla" || s === "spisuje";
    przycisk.replaceChildren(ikona(s === "nagrywa" ? "stop" : "mikrofon"));
    const tytul = s === "nagrywa" ? "Zakończ nagrywanie" : etykieta || "Nagraj głosówkę";
    przycisk.title = tytul;
    przycisk.setAttribute("aria-label", tytul);
    if (typeof naStan === "function") {
      try {
        naStan(s);
      } catch (e) { /* nic */ }
    }
  }
  ustawStan("bezczynny");

  function zatrzymajZegar() {
    if (zegar) clearInterval(zegar);
    zegar = null;
  }

  async function wyslij(blob, mime) {
    if (!blob || !blob.size) {
      ustawStan("bezczynny");
      toast("Nagranie jest puste.", "blad");
      return;
    }
    ustawStan("wysyla", "Wysyłam…");
    let id;
    try {
      const r = await ctx.apiSurowe("/api/glos", blob, (mime || blob.type || "audio/webm"));
      id = r && r.id;
      if (!id) throw new Error("Serwer nie zwrócił numeru nagrania.");
      if (r.stan === "brak_whispera") return brakWhispera(r);
    } catch (e) {
      ustawStan("blad", "");
      toast(e.status === 404 ? "Głosówki jeszcze nie działają na tym panelu." : "Nie udało się wysłać nagrania: " + e.message, "blad");
      setTimeout(() => stan === "blad" && ustawStan("bezczynny"), 2500);
      return;
    }
    ustawStan("spisuje", "Spisuję…");
    const koniec = Date.now() + MAKS_CZEKANIA_S * 1000;
    while (Date.now() < koniec) {
      await czekaj(1500);
      let r;
      try {
        r = await ctx.api("/api/glos/" + encodeURIComponent(id));
      } catch (e) {
        if (e.status === 0) continue;                         // chwilowy brak połączenia — czekamy dalej
        ustawStan("blad");
        toast("Nie udało się sprawdzić transkrypcji: " + e.message, "blad");
        setTimeout(() => stan === "blad" && ustawStan("bezczynny"), 2500);
        return;
      }
      if (!r) continue;
      if (r.stan === "transkrybuje") opis.textContent = "Spisuję…";
      else if (r.stan === "czeka") opis.textContent = "W kolejce…";
      if (r.stan === "gotowe") {
        const tekst = String(r.tekst || "").trim();
        ustawStan("bezczynny");
        if (!tekst) {
          toast("W nagraniu nie było słychać słów.", "info");
          return;
        }
        if (typeof naTekst === "function") naTekst(tekst);
        return;
      }
      if (r.stan === "blad") {
        ustawStan("bezczynny");
        toast("Transkrypcja nie wyszła: " + (r.blad || "nieznany błąd"), "blad");
        return;
      }
      if (r.stan === "brak_whispera") return brakWhispera(r);
    }
    ustawStan("bezczynny");
    toast("Transkrypcja trwa za długo — spróbuj później.", "blad");
  }

  function brakWhispera(r) {
    ustawStan("bezczynny");
    toast("Nagranie zapisane, ale na komputerze z panelem nie ma programu do spisywania głosu (Whisper). " +
      "Zobacz Ustawienia → Stan systemu." + (r && r.blad ? " " + r.blad : ""), "blad");
  }

  async function zacznijNagrywanie() {
    try {
      strumien = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch (e) {
      const odmowa = e && (e.name === "NotAllowedError" || e.name === "SecurityError");
      toast(odmowa ? "Przeglądarka nie dała dostępu do mikrofonu. Zezwól na mikrofon dla tej strony." : "Nie mogę włączyć mikrofonu: " + (e.message || e.name), "blad");
      return;
    }
    const format = wybierzFormat();
    try {
      nagrywacz = format ? new MediaRecorder(strumien, { mimeType: format }) : new MediaRecorder(strumien);
    } catch (e) {
      nagrywacz = new MediaRecorder(strumien);
    }
    kawalki = [];
    nagrywacz.addEventListener("dataavailable", (e) => {
      if (e.data && e.data.size) kawalki.push(e.data);
    });
    nagrywacz.addEventListener("stop", () => {
      zatrzymajZegar();
      if (strumien) strumien.getTracks().forEach((t) => t.stop());
      strumien = null;
      const mime = (nagrywacz && nagrywacz.mimeType) || format || "audio/webm";
      const blob = new Blob(kawalki, { type: mime });
      nagrywacz = null;
      if (porzucone) {
        porzucone = false;
        ustawStan("bezczynny");
        return;
      }
      wyslij(blob, mime.split(";")[0]);
    });
    nagrywacz.start(1000);
    start = Date.now();
    ustawStan("nagrywa", "0:00");
    zegar = setInterval(() => {
      const s = Math.floor((Date.now() - start) / 1000);
      opis.textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
      if (s >= MAKS_NAGRANIA_S) zakonczNagrywanie();
    }, 250);
  }

  function zakonczNagrywanie() {
    if (nagrywacz && nagrywacz.state !== "inactive") {
      try {
        nagrywacz.stop();
      } catch (e) { /* nic */ }
    }
  }

  przycisk.addEventListener("click", () => {
    if (stan === "nagrywa") return zakonczNagrywanie();
    if (stan !== "bezczynny" && stan !== "blad") return;
    if (mozeNagrywac()) zacznijNagrywanie();
    else plikWej.click();
  });

  plikWej.addEventListener("change", () => {
    const f = plikWej.files && plikWej.files[0];
    plikWej.value = "";
    if (f) wyslij(f, f.type || "audio/mp4");
  });

  // sprzątanie, gdy element zniknie w trakcie nagrywania
  w.zatrzymaj = () => {
    zatrzymajZegar();
    if (nagrywacz && nagrywacz.state !== "inactive") {
      porzucone = true;
      try {
        nagrywacz.stop();
      } catch (e) { /* nic */ }
    }
    if (strumien) strumien.getTracks().forEach((t) => t.stop());
  };
  return w;
}
