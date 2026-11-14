// Rozmowa głosowa w panelu (zakładka Sesja): mikrofon, WebRTC każdy z każdym, sygnały przez serwer panelu,
// puls uczestnika, miernik poziomu i — gdy „Agent słucha” — nagrywanie WŁASNEGO mikrofonu odcinkami.
//
// Serwer: bc/sesje.py (trasy /api/sesje/*). Zasady:
// - sygnały (oferta, odpowiedź, kandydaci ICE) idą przez POST /api/sesje/sygnal, odbiór długim odpytywaniem
//   POST /api/sesje/odbierz (zwykłe HTTP — działa przez tunel Cloudflare); każde odpytanie to też znak życia;
// - ofertę składa uczestnik o MNIEJSZYM identyfikatorze (bez kolizji ofert); każda próba połączenia ma numer
//   (`proba`), stare sygnały są pomijane; po zerwaniu oferujący zaczyna nową próbę, a druga strona prosi o nią
//   sygnałem „zerwij”;
// - sygnały do jednej osoby idą PO KOLEI (łańcuch obietnic na adresata), więc serwer numeruje je w kolejności
//   powstania; kandydaci ICE, którzy mimo to przyjdą przed ofertą (albo dla nowszej próby), czekają w buforze;
// - nagrywanie: MediaRecorder zatrzymywany i uruchamiany na granicy odcinka, więc każdy odcinek to osobny,
//   samodzielnie dekodowalny plik; odcinki ciszy (i przy wyciszonym mikrofonie) nie są wysyłane — ale tylko gdy
//   miernik poziomu naprawdę działa (bez miernika odcinki idą bez bramki ciszy); po wyłączeniu słuchania, „Zakończ”
//   i „Rozłącz” ostatni kawałek też jest wysyłany (z identyfikatorem sesji — serwer ma na niego okno łaski).
//
// const r = new Rozmowa({ api, naStan, naKomunikat });  await r.dolacz();  r.wycisz(true);  await r.rozlacz();

const PULS_MS = 2500;
const CZEKANIE_ODBIORU_S = 8;
const PROG_CISZY = 0.012;          // RMS (0–1): odcinek z poziomem stale poniżej to cisza — nie wysyłamy
const PROG_MOWY = 0.03;            // RMS powyżej = „mówi”
const ZERWANE_PO_MS = 7000;        // „rozłączony” tak długo = nowa próba połączenia
const LACZENIE_MAX_MS = 25000;     // tak długo bez połączenia = próba nieudana
const PROBY_DO_NIEUDANEGO = 2;     // po tylu nieudanych próbach pokazujemy radę „rozmawiajcie przez Discord”
const MAX_BUFOR_ICE = 100;         // kandydaci ICE czekający na ofertę (na osobę)
const CZEKANIE_OSTATNIEGO_MS = 8000; // „Rozłącz”: tyle najwyżej czekamy na wysłanie ostatniego odcinka
const CISZA_Z_RZEDU = 3;           // tyle odcinków ciszy z rzędu (bez wyciszenia) = ostrzeżenie „agent cię nie słyszy”
const KANDYDACI_FORMATU = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];

const czekaj = (ms) => new Promise((r) => setTimeout(r, ms));

/** Czy ta strona może użyć mikrofonu i WebRTC. {mikrofon, rtc, nagrywanie, powod?} */
export function mozliwosci() {
  const bezpieczny = !!window.isSecureContext;
  const mikrofon = bezpieczny && !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  const rtc = typeof window.RTCPeerConnection === "function";
  const nagrywanie = typeof window.MediaRecorder === "function";
  let powod = null;
  if (!bezpieczny) {
    powod = "Mikrofon działa tylko przez bezpieczne połączenie: link tunelu (https) albo na komputerze z panelem " +
      "(adres 127.0.0.1). Ten adres to zwykłe http, więc możesz tylko słuchać.";
  } else if (!mikrofon) powod = "Ta przeglądarka nie daje dostępu do mikrofonu. Użyj Chrome, Edge, Firefoksa albo Safari.";
  else if (!rtc) powod = "Ta przeglądarka nie obsługuje rozmów głosowych (WebRTC).";
  return { mikrofon, rtc, nagrywanie, powod };
}

function formatNagrania() {
  if (typeof window.MediaRecorder !== "function") return null;
  for (const k of KANDYDACI_FORMATU) {
    try {
      if (!MediaRecorder.isTypeSupported || MediaRecorder.isTypeSupported(k)) return k;
    } catch (e) { /* dalej */ }
  }
  return "";
}

function komunikatMikrofonu(e) {
  const n = e && e.name;
  if (n === "NotAllowedError" || n === "SecurityError") {
    return "Przeglądarka nie pozwoliła użyć mikrofonu. Kliknij ikonę kłódki (albo mikrofonu) przy adresie strony, " +
      "zezwól na mikrofon i dołącz jeszcze raz. Na razie słuchasz bez mikrofonu.";
  }
  if (n === "NotFoundError" || n === "OverconstrainedError") return "Nie znaleziono mikrofonu. Podłącz go i dołącz jeszcze raz.";
  if (n === "NotReadableError") return "Mikrofon jest zajęty przez inny program (np. Discord albo Zoom). Zamknij go albo zmień urządzenie.";
  return "Nie udało się włączyć mikrofonu: " + ((e && e.message) || n || "nieznany błąd");
}

function imie() {
  try {
    return localStorage.getItem("bc.kto") || "";
  } catch (e) {
    return "";
  }
}

export class Rozmowa {
  constructor({ api, naStan, naKomunikat, kontenerAudio } = {}) {
    this.api = api;
    this.naStan = naStan || (() => {});
    this.naKomunikat = naKomunikat || (() => {});
    this.kontenerAudio = kontenerAudio || document.body;
    this.u = null;
    this.k = null;
    this.ice = [];
    this.stan = null;
    this.dolaczony = false;
    this.wyciszony = false;
    this.strumien = null;
    this.mikrofonBlad = null;
    this.peers = new Map();
    this.odSygnalu = 0;
    this.poziom = 0;
    this.ostatniaMowa = 0;
    this.odcinekS = 12;
    this.nagrywa = false;
    this.nagrywacz = null;
    this.nrOdcinka = 0;
    this.wyslane = 0;
    this.pominiete = 0;
    this.ciszaZRzedu = 0;
    this.bladWysylki = null;
    this.sesjaId = null;
    this._miernikZywy = false;
    this._kolejkiWysylki = new Map();
    this._buforIce = new Map();
    this._petle = 0;
    this._naZamkniecie = () => this._wyjdzCicho();
  }

  // ------------------------------------------------------------------ dołączanie i wychodzenie
  async dolacz() {
    if (this.dolaczony) return;
    this.mikrofonBlad = null;
    const m = mozliwosci();
    // kontekst dźwięku tworzymy JESZCZE w geście kliknięcia (przed pierwszym await) — inaczej np. Safari na iPhonie
    // zostawia go wstrzymanego i miernik pokazuje same zera
    let kontekst = null;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (m.mikrofon && AC) {
        kontekst = new AC();
        if (kontekst.state === "suspended") kontekst.resume().catch(() => {});
      }
    } catch (e) {
      kontekst = null;
    }
    if (m.mikrofon) {
      try {
        this.strumien = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
        });
      } catch (e) {
        this.strumien = null;
        this.mikrofonBlad = komunikatMikrofonu(e);
      }
    } else {
      this.mikrofonBlad = m.powod;
    }
    this._miernik(kontekst);
    await this._wejdz();
    window.addEventListener("pagehide", this._naZamkniecie);
    const petla = ++this._petle;
    this._petlaPulsu(petla);
    this._petlaOdbioru(petla);
  }

  async _wejdz() {
    const o = await this.api("/api/sesje/dolacz", { metoda: "POST", cialo: { mikrofon: !!this.strumien } });
    this.u = o.u;
    this.k = o.k;
    this.ice = Array.isArray(o.ice) ? o.ice : [];
    this.odSygnalu = 0;
    this.dolaczony = true;
    this._przyjmijStan(o);
  }

  _wejdzPonownie() {
    // serwer nas „zapomniał” (brak pulsu, restart panelu): zamknij połączenia i dołącz jeszcze raz — jedna próba
    // naraz, bo 410 może przyjść równocześnie z pętli pulsu i pętli odbioru
    if (this._ponownie) return this._ponownie;
    if (!this.dolaczony) return Promise.resolve();
    const petla = this._petle;
    this._ponownie = (async () => {
      for (const uid of [...this.peers.keys()]) this._zamknijPeer(uid);
      try {
        await this._wejdz();
        this.naKomunikat("Połączenie z panelem wróciło — dołączono ponownie.", "info");
      } catch (e) {
        this.naKomunikat("Nie udało się wrócić do rozmowy: " + e.message, "blad");
        await czekaj(3000);
      }
    })().finally(() => {
      this._ponownie = null;
      if (this._petle !== petla && this.dolaczony) {          // w międzyczasie kliknięto „Rozłącz”
        this._wyjdzCicho();
        this.dolaczony = false;
        this.u = this.k = null;
      }
    });
    return this._ponownie;
  }

  async rozlacz() {
    if (!this.dolaczony && !this.strumien) return;
    this._petle++;
    const ostatni = this._zatrzymajNagrywanie();
    window.removeEventListener("pagehide", this._naZamkniecie);
    for (const uid of [...this.peers.keys()]) this._zamknijPeer(uid);
    // ostatni kawałek nagrania (do chwili kliknięcia) wysyłamy, ZANIM wyjdziemy z pokoju — serwer przyjmuje odcinki
    // tylko od uczestników
    await Promise.race([ostatni, czekaj(CZEKANIE_OSTATNIEGO_MS)]);
    this._kolejkiWysylki.clear();
    this._buforIce.clear();
    const u = this.u;
    const k = this.k;
    this.dolaczony = false;
    this.u = this.k = null;
    if (this.strumien) this.strumien.getTracks().forEach((t) => t.stop());
    this.strumien = null;
    if (this._kontekst) {
      try { this._kontekst.close(); } catch (e) { /* nic */ }
      this._kontekst = null;
    }
    clearInterval(this._zegarMiernika);
    this.poziom = 0;
    if (u) {
      try {
        await this.api("/api/sesje/opusc", { metoda: "POST", cialo: { u, k }, czas: 5000 });
      } catch (e) { /* serwer i tak usunie nas po braku pulsu */ }
    }
    this.naStan(this.stan);
  }

  _wyjdzCicho() {
    if (!this.u) return;
    try {
      this.api("/api/sesje/opusc", { metoda: "POST", cialo: { u: this.u, k: this.k }, keepalive: true }).catch(() => {});
    } catch (e) { /* nic */ }
  }

  wycisz(tak) {
    this.wyciszony = !!tak;
    this._obudzMiernik();
    if (!this.wyciszony && this._odcinek) this._odcinek.caly_wyciszony = false;
    if (this.strumien) this.strumien.getAudioTracks().forEach((t) => { t.enabled = !this.wyciszony; });
    this._puls().catch(() => {});
  }

  get mowi() {
    return Date.now() - this.ostatniaMowa < 700;
  }

  // ------------------------------------------------------------------ miernik poziomu
  _miernik(kontekst) {
    clearInterval(this._zegarMiernika);
    this._miernikZywy = false;
    if (!this.strumien) {
      if (kontekst) try { kontekst.close(); } catch (e) { /* nic */ }
      return;
    }
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      this._kontekst = kontekst || new AC();
      const zrodlo = this._kontekst.createMediaStreamSource(this.strumien);
      const analizator = this._kontekst.createAnalyser();
      analizator.fftSize = 1024;
      zrodlo.connect(analizator);
      const bufor = new Float32Array(analizator.fftSize);
      this._zegarMiernika = setInterval(() => {
        if (!this._kontekst || this._kontekst.state !== "running") return;   // wstrzymany: brak pomiaru
        analizator.getFloatTimeDomainData(bufor);
        let suma = 0;
        for (let i = 0; i < bufor.length; i++) suma += bufor[i] * bufor[i];
        const rms = Math.sqrt(suma / bufor.length);
        if (rms > 0) this._miernikZywy = true;
        this.poziom = this.wyciszony ? 0 : rms;
        if (!this.wyciszony && rms > PROG_MOWY) this.ostatniaMowa = Date.now();
        if (this._odcinek && !this.wyciszony) {
          this._odcinek.max = Math.max(this._odcinek.max, rms);
          this._odcinek.pomiary++;
        }
      }, 100);
      if (this._kontekst.state === "suspended") this._kontekst.resume().catch(() => {});
    } catch (e) {
      this._kontekst = null;
    }
  }

  /** Czy miernik poziomu mikrofonu naprawdę mierzy (kontekst dźwięku działa i dał choć jeden niezerowy pomiar).
   *  Gdy nie — odcinki idą do agenta bez bramki ciszy. */
  get miernikDziala() {
    return !!(this._kontekst && this._kontekst.state === "running" && this._miernikZywy);
  }

  _obudzMiernik() {
    // wołane w geście (kliknięcie Wycisz / Włącz mikrofon): przeglądarka pozwala wtedy wznowić kontekst dźwięku
    if (this._kontekst && this._kontekst.state === "suspended") this._kontekst.resume().catch(() => {});
  }

  // ------------------------------------------------------------------ puls i stan
  async _puls() {
    if (!this.dolaczony) return;
    const polaczenia = {};
    for (const [uid, p] of this.peers) polaczenia[uid] = p.stan;
    const o = await this.api("/api/sesje/puls", {
      metoda: "POST", czas: 10000,
      cialo: { u: this.u, k: this.k, wyciszony: this.wyciszony, mowi: this.mowi, mikrofon: !!this.strumien, polaczenia },
    });
    this._przyjmijStan(o);
  }

  async _petlaPulsu(petla) {
    while (this._petle === petla && this.dolaczony) {
      try {
        await this._puls();
        this._bladPolaczenia = false;
      } catch (e) {
        if (this._petle !== petla) break;                      // już rozłączono — nie wracaj do pokoju
        if (e.status === 410) await this._wejdzPonownie();
        else if (!this._bladPolaczenia) {
          this._bladPolaczenia = true;
          this.naKomunikat("Brak połączenia z panelem — ponawiam…", "blad");
        }
      }
      await czekaj(PULS_MS);
    }
  }

  _przyjmijStan(o) {
    if (!o) return;
    this.stan = o;
    if (Array.isArray(o.ice) && o.ice.length) this.ice = o.ice;
    if (o.odcinek_s) this.odcinekS = Number(o.odcinek_s) || 12;
    if (o.sesja && o.sesja.id) this.sesjaId = o.sesja.id;     // ostatni odcinek po wyłączeniu idzie do tej sesji
    if (this.dolaczony) {
      this._zsynchronizujPeery(o);
      const slucha = !!(o.sluchanie && o.sluchanie.wlaczone);
      if (slucha && this.strumien && !this.nagrywa) this._zacznijNagrywanie();
      if (!slucha && this.nagrywa) this._zatrzymajNagrywanie();
    }
    this.naStan(o);
  }

  // ------------------------------------------------------------------ sygnały
  async _petlaOdbioru(petla) {
    while (this._petle === petla && this.dolaczony) {
      try {
        const o = await this.api("/api/sesje/odbierz", {
          metoda: "POST", czas: (CZEKANIE_ODBIORU_S + 10) * 1000,
          cialo: { u: this.u, k: this.k, od: this.odSygnalu, czekaj: CZEKANIE_ODBIORU_S },
        });
        for (const s of o.sygnaly || []) {
          this.odSygnalu = Math.max(this.odSygnalu, s.n + 1);
          try {
            await this._naSygnal(s);
          } catch (e) {
            console.warn("sesja: sygnał", s.typ, e);
          }
        }
      } catch (e) {
        if (this._petle !== petla) break;                      // już rozłączono — nie wracaj do pokoju
        if (e.status === 410) await this._wejdzPonownie();
        else await czekaj(1500);
      }
    }
  }

  _wyslijSygnal(doKogo, typ, dane) {
    // Do jednej osoby po kolei: równoległe żądania mogłyby dojść do serwera w innej kolejności (np. kandydat ICE
    // przed ofertą), a serwer numeruje sygnały w kolejności przyjścia.
    if (!this.dolaczony) return Promise.resolve();
    const u = this.u;
    const k = this.k;
    const poprzedni = this._kolejkiWysylki.get(doKogo) || Promise.resolve();
    const ten = poprzedni.then(() => {
      if (!this.dolaczony || this.u !== u) return null;       // w międzyczasie rozłączono albo dołączono od nowa
      return this.api("/api/sesje/sygnal", { metoda: "POST", cialo: { u, k, do: doKogo, typ, dane }, czas: 10000 })
        .catch((e) => { if (e.status !== 404) console.warn("sesja: wysyłka sygnału", e.message); });
    });
    this._kolejkiWysylki.set(doKogo, ten);
    ten.then(() => { if (this._kolejkiWysylki.get(doKogo) === ten) this._kolejkiWysylki.delete(doKogo); });
    return ten;
  }

  _doBuforaIce(uid, proba, kandydat) {
    // kandydat dla osoby, z którą połączenie jeszcze nie powstało (oferta w drodze) albo dla nowszej próby
    let b = this._buforIce.get(uid);
    if (!b || b.proba !== proba) {
      if (b && typeof proba === "number" && proba < b.proba) return;   // starsza próba niż ta w buforze — pomiń
      b = { proba, lista: [] };
      this._buforIce.set(uid, b);
    }
    if (b.lista.length < MAX_BUFOR_ICE) b.lista.push(kandydat);
  }

  async _naSygnal(s) {
    const uid = s.od;
    const d = s.dane || {};
    if (s.typ === "oferta") {
      let p = this.peers.get(uid);
      if (!p || p.proba !== d.proba || p.pc.signalingState !== "stable") {
        if (p) this._zamknijPeer(uid, true);
        p = this._nowyPeer(uid, false, d.proba);
      }
      await p.pc.setRemoteDescription({ type: "offer", sdp: d.sdp });
      await this._kandydaciZKolejki(p);
      const odp = await p.pc.createAnswer();
      await p.pc.setLocalDescription(odp);
      this._wyslijSygnal(uid, "odpowiedz", { sdp: p.pc.localDescription.sdp, proba: p.proba });
    } else if (s.typ === "odpowiedz") {
      const p = this.peers.get(uid);
      if (!p || p.proba !== d.proba || p.pc.signalingState !== "have-local-offer") return;
      await p.pc.setRemoteDescription({ type: "answer", sdp: d.sdp });
      await this._kandydaciZKolejki(p);
    } else if (s.typ === "ice") {
      if (!d.kandydat) return;
      const p = this.peers.get(uid);
      if (p && p.proba === d.proba) {
        if (p.pc.remoteDescription) await p.pc.addIceCandidate(d.kandydat).catch(() => {});
        else p.kolejka.push(d.kandydat);
      } else if (!p || (typeof d.proba === "number" && d.proba > p.proba)) {
        this._doBuforaIce(uid, d.proba, d.kandydat);           // dołączy do połączenia, gdy przyjdzie oferta
      }
    } else if (s.typ === "zerwij") {
      const p = this.peers.get(uid);
      if (p && p.oferujacy && (d.proba === undefined || d.proba === p.proba)) this._nowaProba(uid);
    }
  }

  async _kandydaciZKolejki(p) {
    const lista = p.kolejka.splice(0);
    for (const k of lista) await p.pc.addIceCandidate(k).catch(() => {});
  }

  // ------------------------------------------------------------------ połączenia (siatka każdy z każdym)
  _zsynchronizujPeery(o) {
    const lista = ((o.pokoj && o.pokoj.uczestnicy) || []).filter((x) => x.id && x.id !== this.u);
    const obecni = new Set(lista.map((x) => x.id));
    for (const uid of [...this.peers.keys()]) if (!obecni.has(uid)) this._zamknijPeer(uid);
    for (const x of lista) {
      if (this.peers.has(x.id)) continue;
      if (this.u < x.id) {
        this._nowyPeer(x.id, true, 1);
        this._ofertuj(x.id);
      }
      // większy identyfikator czeka na ofertę (sygnał „oferta” utworzy połączenie)
    }
    const teraz = Date.now();
    for (const [uid, p] of this.peers) {
      if (p.stan === "polaczony") continue;
      const dlugo = teraz - p.od > LACZENIE_MAX_MS;
      const zerwane = p.stan === "rozlaczony" && teraz - p.zmiana > ZERWANE_PO_MS;
      if ((dlugo || zerwane || p.pc.connectionState === "failed") && teraz - p.ostatniaProba > LACZENIE_MAX_MS / 2) {
        p.nieudane += dlugo || p.pc.connectionState === "failed" ? 1 : 0;
        if (p.nieudane >= PROBY_DO_NIEUDANEGO) p.stan = "nieudane";
        if (p.oferujacy) this._nowaProba(uid);
        else {
          p.ostatniaProba = teraz;
          this._wyslijSygnal(uid, "zerwij", { proba: p.proba });
        }
      }
    }
  }

  _nowyPeer(uid, oferujacy, proba) {
    const pc = new RTCPeerConnection({ iceServers: this.ice });
    const audio = document.createElement("audio");
    audio.autoplay = true;
    audio.hidden = true;
    audio.dataset.uczestnik = uid;
    this.kontenerAudio.appendChild(audio);
    const stary = this.peers.get(uid);
    const p = {
      pc, audio, oferujacy, proba: proba || 1, kolejka: [], stan: "laczenie", od: Date.now(), zmiana: Date.now(),
      ostatniaProba: Date.now(), nieudane: stary ? stary.nieudane : 0,
    };
    const bufor = this._buforIce.get(uid);
    if (bufor && bufor.proba === p.proba) {                    // kandydaci, którzy przyszli przed ofertą
      p.kolejka.push(...bufor.lista);
      this._buforIce.delete(uid);
    } else if (bufor && typeof bufor.proba === "number" && bufor.proba < p.proba) {
      this._buforIce.delete(uid);
    }
    if (this.strumien) {
      for (const t of this.strumien.getAudioTracks()) pc.addTrack(t, this.strumien);
    } else {
      pc.addTransceiver("audio", { direction: "recvonly" });
    }
    pc.onicecandidate = (e) => {
      if (e.candidate) this._wyslijSygnal(uid, "ice", { kandydat: e.candidate.toJSON(), proba: p.proba });
    };
    pc.ontrack = (e) => {
      const s = (e.streams && e.streams[0]) || new MediaStream([e.track]);
      if (audio.srcObject !== s) {
        audio.srcObject = s;
        audio.play().catch(() => {});
      }
    };
    pc.onconnectionstatechange = () => {
      const st = pc.connectionState;
      const nowy = st === "connected" ? "polaczony" : st === "failed" ? (p.nieudane + 1 >= PROBY_DO_NIEUDANEGO ? "nieudane" : "laczenie")
        : st === "disconnected" ? "rozlaczony" : st === "closed" ? "zamkniete" : "laczenie";
      if (st === "connected") p.nieudane = 0;
      if (nowy !== p.stan) {
        p.stan = nowy;
        p.zmiana = Date.now();
        this.naStan(this.stan);
      }
    };
    this.peers.set(uid, p);
    return p;
  }

  async _ofertuj(uid) {
    const p = this.peers.get(uid);
    if (!p) return;
    try {
      const oferta = await p.pc.createOffer();
      await p.pc.setLocalDescription(oferta);
      this._wyslijSygnal(uid, "oferta", { sdp: p.pc.localDescription.sdp, proba: p.proba });
    } catch (e) {
      console.warn("sesja: oferta", e);
    }
  }

  _nowaProba(uid) {
    const stary = this.peers.get(uid);
    const proba = (stary ? stary.proba : 0) + 1;
    const nieudane = stary ? stary.nieudane : 0;
    const stan = stary ? stary.stan : "laczenie";
    if (stary) this._zamknijPeer(uid, true);
    const p = this._nowyPeer(uid, true, proba);
    p.nieudane = nieudane;
    if (stan === "nieudane") p.stan = "nieudane";
    this._ofertuj(uid);
  }

  _zamknijPeer(uid, zostawWpis) {
    const p = this.peers.get(uid);
    if (!p) return;
    try { p.pc.onconnectionstatechange = null; p.pc.close(); } catch (e) { /* nic */ }
    try { p.audio.srcObject = null; p.audio.remove(); } catch (e) { /* nic */ }
    if (!zostawWpis) {
      this.peers.delete(uid);
      this._buforIce.delete(uid);
      this._kolejkiWysylki.delete(uid);
    }
  }

  /** Stany połączeń: Map uid -> "laczenie" | "polaczony" | "rozlaczony" | "nieudane". */
  stanyPolaczen() {
    const m = new Map();
    for (const [uid, p] of this.peers) m.set(uid, p.stan);
    return m;
  }

  /** Czy z kimś głos nie łączy się mimo kilku prób (wtedy rada: rozmawiajcie przez Discord). */
  czyNieudane() {
    for (const p of this.peers.values()) {
      if (p.stan !== "polaczony" && (p.stan === "nieudane" || p.nieudane >= PROBY_DO_NIEUDANEGO)) return true;
    }
    return false;
  }

  // ------------------------------------------------------------------ nagrywanie odcinkami (gdy agent słucha)
  _zacznijNagrywanie() {
    const format = formatNagrania();
    if (format === null || !this.strumien) return;
    this.nagrywa = true;
    this._format = format;
    this._nastepnyOdcinek();
    this.naStan(this.stan);
  }

  _nastepnyOdcinek() {
    if (!this.nagrywa || !this.strumien) return;
    let rec;
    try {
      rec = this._format ? new MediaRecorder(this.strumien, { mimeType: this._format }) : new MediaRecorder(this.strumien);
    } catch (e) {
      this.nagrywa = false;
      this.naKomunikat("Ta przeglądarka nie umie nagrywać dźwięku — agent nie usłyszy twojego mikrofonu.", "blad");
      return;
    }
    const odcinek = {
      start: Date.now(), max: 0, pomiary: 0, kawalki: [], nr: ++this.nrOdcinka, sesja: this.sesjaId,
      caly_wyciszony: this.wyciszony,
    };
    odcinek.gotowe = new Promise((r) => { odcinek.zakoncz = r; });
    this._odcinek = odcinek;
    this.nagrywacz = rec;
    rec.ondataavailable = (e) => { if (e.data && e.data.size) odcinek.kawalki.push(e.data); };
    rec.onstop = () => {
      const typ = rec.mimeType || this._format || "audio/webm";
      const blob = new Blob(odcinek.kawalki, { type: typ });
      if (this.nagrywa) this._nastepnyOdcinek();              // od razu następny odcinek (nowy, pełny plik)
      // Bramka ciszy tylko wtedy, gdy miernik naprawdę mierzył ten odcinek. Bez miernika (kontekst dźwięku się nie
      // utworzył albo jest wstrzymany) wysyłamy wszystko poza odcinkami wyciszonymi od początku do końca —
      // lepiej spisać ciszę (Whisper ją pominie), niż zgubić czyjś głos.
      const zmierzony = this._miernikZywy && odcinek.pomiary > 0;
      const glos = zmierzony ? odcinek.max >= PROG_CISZY : !odcinek.caly_wyciszony;
      let wysylka = Promise.resolve();
      if (glos && blob.size) {
        this.ciszaZRzedu = 0;
        wysylka = this._wyslijOdcinek(blob, odcinek);
      } else {
        this.pominiete++;
        if (!odcinek.caly_wyciszony && !this.wyciszony) this.ciszaZRzedu++;
      }
      Promise.resolve(wysylka).catch(() => {}).then(() => odcinek.zakoncz());
      this.naStan(this.stan);
    };
    rec.start();
    odcinek.zegar = setTimeout(() => { if (rec.state !== "inactive") rec.stop(); }, this.odcinekS * 1000);
  }

  /** Zatrzymuje nagrywanie; zwraca obietnicę, która się spełnia po wysłaniu ostatniego kawałka. */
  _zatrzymajNagrywanie() {
    this.nagrywa = false;
    const rec = this.nagrywacz;
    const odcinek = this._odcinek;
    this.nagrywacz = null;
    if (odcinek) clearTimeout(odcinek.zegar);
    let gotowe = Promise.resolve();
    if (rec && rec.state !== "inactive") {
      try {
        rec.stop();                                            // ostatni kawałek idzie z identyfikatorem sesji
        if (odcinek && odcinek.gotowe) gotowe = odcinek.gotowe;
      } catch (e) { /* nic */ }
    }
    this.naStan(this.stan);
    return gotowe;
  }

  async _wyslijOdcinek(blob, odcinek, proba = 0) {
    if (!this.u) return;
    const h = { "X-BC": "1", "Content-Type": (blob.type || "audio/webm").split(";")[0], "X-BC-Sesja": this.u + ":" + this.k };
    const kto = imie();
    if (kto) h["X-BC-Kto"] = encodeURIComponent(kto);
    try {
      const r = await fetch("/api/sesje/odcinek?nr=" + odcinek.nr + "&t=" + odcinek.start +
        (odcinek.sesja ? "&sesja=" + encodeURIComponent(odcinek.sesja) : ""), {
        method: "POST", headers: h, body: blob, credentials: "same-origin", cache: "no-store",
      });
      if (r.ok) {
        this.wyslane++;
        this.bladWysylki = null;
        return;
      }
      let d = null;
      try { d = await r.json(); } catch (e) { /* nic */ }
      if (r.status === 409 && d && d.kod === "nie_slucha") return;   // słuchanie właśnie wyłączone
      if (r.status === 410) return;
      this.bladWysylki = (d && d.blad) || "Odcinek nagrania nie został przyjęty (" + r.status + ").";
      if (r.status >= 500 && r.status !== 507 && proba < 1) {
        await czekaj(2000);
        return this._wyslijOdcinek(blob, odcinek, proba + 1);
      }
      this.naKomunikat(this.bladWysylki, "blad");
    } catch (e) {
      if (proba < 1) {
        await czekaj(2000);
        return this._wyslijOdcinek(blob, odcinek, proba + 1);
      }
      this.bladWysylki = "Nie udało się wysłać odcinka nagrania (brak połączenia z panelem).";
    }
  }
}
