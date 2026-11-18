#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Muzyka do gry: wyrównanie głośności i wersja do pętli — zasady z assets/audio/manifest_audio.json (zasady_obrobki).

    python -B tools/audio_petla.py przetworz <oryginał.mp3> […] --wyjscie assets/audio/muzyka --raport <plik.json>
                                             [--bezstratne assets/audio/muzyka/oryginaly]   # + pętle FLAC (poza gitem)
    python -B tools/audio_petla.py analiza <plik> […] [--raport <plik.json>]     # tylko wybór miejsca cięcia, nic nie zapisuje
    python -B tools/audio_petla.py pomiary <plik> […] [--raport <plik.json>]     # pomiary gotowego pliku (mp3 / ogg / wav)

Co robi „przetworz” dla każdego oryginału <id>.mp3:
  1. pomiary oryginału (ffprobe, ffmpeg ebur128, numpy);
  2. stałe wzmocnienie do -16 LUFS (zintegrowana), ale tak, żeby true peak został co najmniej 1,3 dB poniżej zera
     (gdy szczyt nie pozwala, głośność zostaje nieco niższa; po zakodowaniu sprawdzamy szczyt jeszcze raz i w razie
     potrzeby obniżamy wzmocnienie o 0,1 dB — najwyżej kilka razy);
  3. pełna wersja: <wyjscie>/<id>.mp3 (MP3 VBR V0);
  4. wersja do pętli: <wyjscie>/<id>_petla.ogg (OGG Vorbis q6). Miejsce cięcia wybiera automat: porównuje okno wokół
     kandydata na początek pętli (1–3 s od startu) z oknami wokół kandydatów na koniec (ostatnie ok. 20 s „żywej”
     muzyki) — rytm (korelacja obwiedni uderzeń), harmonia (chroma klatka po klatce), barwa (średnie widmo mel);
     wynik = 0,4 · rytm + 0,4 · harmonia + 0,2 · barwa (te same wagi co w pierwszej partii). O wyborze decyduje wynik
     minus mała kara za różnicę głośności po obu stronach szwu (0,01 za każdy dB ponad 2 dB) plus mała premia za
     dłuższą pętlę (do 0,03). Gdy utwór ma cichszy wstęp (najlepsze miejsce w pierwszych 3 s ma karę głośności
     ponad 0,03), początek pętli jest szukany do 12. sekundy — pętla zaczyna się wtedy za wstępem, a wstęp zostaje
     tylko w pełnej wersji. Potem dosunięcie co do próbki (±15 ms, korelacja fali) i 1 s liniowego
     przenikania końca w początek: ostatnia sekunda pętli to koniec utworu wyciszany + sekunda SPRZED początku pętli
     narastająca, więc ostatnia próbka pętli przechodzi dokładnie w pierwszą;
  5. pomiary obu gotowych plików i raport JSON w układzie pól manifestu (wzmocnienie_db, pomiary.oryginal /
     pelna_wyrownana / petla z wybor_miejsca i budowa).

Wynik dopasowania to miara techniczna (czy okna przy szwie są do siebie podobne), a nie ocena muzyczna. Skrypt
pierwszej partii (16.11.2026) nie zachował się — to narzędzie jest napisane od nowa według opisu w manifeście, więc
liczby dopasowania nie są ściśle porównywalne z pierwszą partią (ta sama idea i wagi, inne szczegóły cech).

Wymaga: ffmpeg i ffprobe w PATH, numpy, scipy. Niczego nie wgrywa i nie generuje.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import resample_poly

FS = 44100
KANALY = 2
CEL_LUFS = -16.0
SZCZYT_MAX_DBTP = -1.3
PRZENIKANIE_S = 1.0
START_OD_S, START_DO_S = 1.02, 3.0     # kandydaci na początek pętli (przed nim musi być 1 s na przenikanie)
START_DO_WSTEP_S = 12.0                # …a gdy utwór ma cichszy wstęp (kara głośności > KARA_WSTEPU) — aż dotąd
KARA_WSTEPU = 0.03
OKNO_KONCA_S = 20.0                    # kandydaci na koniec: ostatnie tyle sekund żywej muzyki
PRZED_S, PO_S = 1.0, 3.0               # porównywane okno: 1 s przed i 3 s po punkcie
WAGI = (0.4, 0.4, 0.2)                 # rytm, harmonia, barwa
PREMIA_DLUGOSCI = 0.03                 # o tyle najwyżej późniejszy koniec (dłuższa pętla) wygrywa z lepiej dopasowanym
DOSUNIECIE_S = 0.015                   # dosunięcie co do próbki: ±15 ms
FS_A = 22050                           # analiza cech: mono, połowa częstotliwości
HOP = 256                              # klatka cech: 11,6 ms
PROG_CISZY_DB = -50.0


# --------------------------------------------------------------------------- ffmpeg
def _uruchom(arg: list[str], wejscie: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(arg, input=wejscie, capture_output=True)


def dekoduj(plik: Path) -> np.ndarray:
    """Plik → próbki float32 (n, 2), 44,1 kHz stereo."""
    r = _uruchom(["ffmpeg", "-v", "error", "-i", str(plik), "-f", "f32le", "-acodec", "pcm_f32le",
                  "-ar", str(FS), "-ac", str(KANALY), "-"])
    if r.returncode != 0 or not r.stdout:
        sys.exit("ffmpeg nie odczytał %s: %s" % (plik.name, r.stderr.decode("utf-8", "replace")[:300]))
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, KANALY).copy()


def koduj(x: np.ndarray, plik: Path, rodzaj: str) -> None:
    """Próbki → MP3 VBR V0 („mp3”), OGG Vorbis q6 („ogg”) albo bezstratny FLAC 16 bit („flac”); bez metadanych źródła."""
    kodek = {"mp3": ["-c:a", "libmp3lame", "-q:a", "0"], "ogg": ["-c:a", "libvorbis", "-q:a", "6"],
             "flac": ["-c:a", "flac", "-sample_fmt", "s16"]}[rodzaj]
    r = _uruchom(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(FS), "-ac", str(KANALY), "-i", "-",
                  "-map_metadata", "-1"] + kodek + [str(plik)], x.astype("<f4").tobytes())
    if r.returncode != 0:
        sys.exit("ffmpeg nie zapisał %s: %s" % (plik.name, r.stderr.decode("utf-8", "replace")[:300]))


def sonda(plik: Path) -> dict:
    r = _uruchom(["ffprobe", "-v", "error", "-show_entries",
                  "format=duration,bit_rate,format_name:stream=codec_name,sample_rate,channels", "-of", "json", str(plik)])
    d = json.loads(r.stdout.decode("utf-8", "replace") or "{}")
    f, s = d.get("format", {}), (d.get("streams") or [{}])[0]
    return {
        "dlugosc_s": round(float(f.get("duration", 0)), 3),
        "format": str(f.get("format_name", "")).split(",")[0],
        "kodek": s.get("codec_name"),
        "czestotliwosc_hz": int(s.get("sample_rate", 0)),
        "kanaly": int(s.get("channels", 0)),
        "bitrate_kbps": int(round(float(f.get("bit_rate", 0)) / 1000)),
    }


def ebur128(plik: Path) -> dict:
    """Głośność wg EBU R128 (ffmpeg): zintegrowana, zakres, true peak, największa głośność chwilowa (okno 400 ms)."""
    r = _uruchom(["ffmpeg", "-hide_banner", "-nostats", "-i", str(plik), "-filter_complex", "ebur128=peak=true",
                  "-f", "null", "-"])
    t = r.stderr.decode("utf-8", "replace")
    if "Summary:" not in t:
        sys.exit("ffmpeg ebur128 nie zmierzył %s" % plik.name)
    klatki, podsum = t.split("Summary:", 1)

    def liczba(wzor: str) -> float:
        m = re.search(wzor, podsum)
        return float(m.group(1)) if m else float("nan")

    chwilowe = [float(v) for v in re.findall(r"\bM:\s*(-?\d+(?:\.\d+)?)", klatki)]
    return {
        "lufs_zintegrowana": liczba(r"I:\s+(-?\d+(?:\.\d+)?) LUFS"),
        "lra_lu": liczba(r"LRA:\s+(-?\d+(?:\.\d+)?) LU"),
        "true_peak_dbtp": liczba(r"Peak:\s+(-?\d+(?:\.\d+)?) dBFS"),
        "glosnosc_chwilowa_max_lufs": round(max(chwilowe), 2) if chwilowe else float("nan"),
    }


# --------------------------------------------------------------------------- pomiary
def db(v: float) -> float:
    return 20.0 * math.log10(max(float(v), 1e-10))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if x.size else 0.0


def _widmo(mono: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Średnie widmo amplitudowe fragmentu (okna 2048, co 1024) i częstotliwości prążków."""
    n = 2048
    if len(mono) < n:
        mono = np.pad(mono, (0, n - len(mono)))
    ramki = sliding_window_view(mono, n)[::n // 2] * np.hanning(n)
    return np.abs(np.fft.rfft(ramki, axis=1)).mean(axis=0), np.fft.rfftfreq(n, 1.0 / FS)


def pomiary_probek(x: np.ndarray) -> dict:
    mono = x.mean(axis=1)
    szczyt = float(np.max(np.abs(x))) if x.size else 0.0
    glosne = np.nonzero(np.max(np.abs(x), axis=1) > 10 ** (PROG_CISZY_DB / 20))[0]
    cisza_p = glosne[0] / FS if len(glosne) else len(x) / FS
    cisza_k = (len(x) - 1 - glosne[-1]) / FS if len(glosne) else len(x) / FS
    pol = FS // 2
    okna = [rms(mono[i:i + pol]) for i in range(0, max(len(mono) - pol + 1, 1), pol)]
    mediana = float(np.median(okna)) if okna else 0.0
    w0, f = _widmo(mono[:2 * FS])
    w1, _ = _widmo(mono[-2 * FS:])
    r0, r1 = db(rms(mono[:2 * FS])), db(rms(mono[-2 * FS:]))
    return {
        "szczyt_dbfs": round(db(szczyt), 2),
        "srednia_rms_dbfs": round(db(rms(mono)), 2),
        "cisza_poczatek_s": round(cisza_p, 3),
        "cisza_koniec_s": round(cisza_k, 3),
        "poczatek_a_koniec": {
            "rms_pierwsze_2s_db": round(r0, 1),
            "rms_ostatnie_2s_db": round(r1, 1),
            "roznica_rms_db": round(r1 - r0, 1),
            "podobienstwo_widma_poczatek_koniec": round(float(w0 @ w1 / (np.linalg.norm(w0) * np.linalg.norm(w1) + 1e-12)), 3),
            "centroid_poczatek_hz": int(round(float(f @ w0 / (w0.sum() + 1e-12)))),
            "centroid_koniec_hz": int(round(float(f @ w1 / (w1.sum() + 1e-12)))),
            "rms_ostatnie_0_5s_wzgl_mediany_db": round(db(rms(mono[-pol:])) - db(mediana), 1),
            "rms_pierwsze_0_5s_wzgl_mediany_db": round(db(rms(mono[:pol])) - db(mediana), 1),
        },
    }


def pomiary(plik: Path, x: np.ndarray | None = None) -> dict:
    """Pomiary pliku w układzie pól manifestu (pomiary.oryginal / pelna_wyrownana / petla)."""
    if x is None:
        x = dekoduj(plik)
    p = sonda(plik)
    e = ebur128(plik)
    n = pomiary_probek(x)
    return {
        **p,
        "lufs_zintegrowana": e["lufs_zintegrowana"], "lra_lu": e["lra_lu"], "true_peak_dbtp": e["true_peak_dbtp"],
        "szczyt_dbfs": n["szczyt_dbfs"], "srednia_rms_dbfs": n["srednia_rms_dbfs"],
        "glosnosc_chwilowa_max_lufs": e["glosnosc_chwilowa_max_lufs"],
        "cisza_poczatek_s": n["cisza_poczatek_s"], "cisza_koniec_s": n["cisza_koniec_s"],
        "poczatek_a_koniec": n["poczatek_a_koniec"],
    }


# --------------------------------------------------------------------------- cechy do wyboru miejsca
def _stft(mono: np.ndarray, n_fft: int) -> np.ndarray:
    """Moc widma: klatka k jest wyśrodkowana na próbce k · HOP."""
    y = np.pad(mono, (n_fft // 2, n_fft // 2), mode="reflect")
    ramki = sliding_window_view(y, n_fft)[::HOP]
    okno = np.hanning(n_fft).astype(np.float32)
    wynik = np.empty((len(ramki), n_fft // 2 + 1), dtype=np.float32)
    for i in range(0, len(ramki), 512):                      # porcjami — mniej pamięci
        wynik[i:i + 512] = np.abs(np.fft.rfft(ramki[i:i + 512] * okno, axis=1)) ** 2
    return wynik


def _filtry_mel(n_fft: int, pasm: int = 40, f_od: float = 40.0, f_do: float = 10000.0) -> np.ndarray:
    def mel(f):
        return 2595.0 * np.log10(1.0 + f / 700.0)

    def hz(m):
        return 700.0 * (10 ** (m / 2595.0) - 1.0)

    srodki = hz(np.linspace(mel(f_od), mel(f_do), pasm + 2))
    f = np.fft.rfftfreq(n_fft, 1.0 / FS_A)
    filtry = np.zeros((pasm, len(f)), dtype=np.float32)
    for i in range(pasm):
        a, b, c = srodki[i], srodki[i + 1], srodki[i + 2]
        filtry[i] = np.clip(np.minimum((f - a) / (b - a), (c - f) / (c - b)), 0, None)
    return filtry


def _wygladz(v: np.ndarray, n: int) -> np.ndarray:
    """Średnia ruchoma wzdłuż czasu (oś 0), długość n klatek."""
    if n <= 1:
        return v
    jadro = np.ones(n) / n
    if v.ndim == 1:
        return np.convolve(v, jadro, mode="same")
    return np.stack([np.convolve(v[:, i], jadro, mode="same") for i in range(v.shape[1])], axis=1)


def cechy(x: np.ndarray) -> dict:
    mono = resample_poly(x.mean(axis=1).astype(np.float64), 1, FS // FS_A).astype(np.float32)
    s1 = _stft(mono, 1024)                                   # krótkie okno: rytm i barwa
    mel = 10.0 * np.log10(s1 @ _filtry_mel(1024).T + 1e-10)
    mel = np.maximum(mel, mel.max() - 80.0) - (mel.max() - 80.0)       # dB nad podłogą, ≥ 0
    przyrost = np.maximum(mel[2:] - mel[:-2], 0).mean(axis=1)
    uderzenia = _wygladz(np.concatenate([[0.0, 0.0], przyrost]), 3)
    s2 = _stft(mono, 4096)                                   # długie okno: harmonia
    f = np.fft.rfftfreq(4096, 1.0 / FS_A)
    chroma = np.zeros((len(s2), 12), dtype=np.float32)
    wybor = (f >= 55.0) & (f <= 5000.0)
    klasa = np.round(12.0 * np.log2(f[wybor] / 440.0) + 69.0).astype(int) % 12
    for k in range(12):
        chroma[:, k] = s2[:, wybor][:, klasa == k].sum(axis=1)
    chroma = _wygladz(np.sqrt(chroma), 21)                   # ok. 0,25 s
    chroma /= np.linalg.norm(chroma, axis=1, keepdims=True) + 1e-9
    n = min(len(mel), len(chroma))
    poziom = s1.sum(axis=1)                                   # moc klatki (liniowo) — do różnicy głośności przy szwie
    return {"uderzenia": uderzenia[:n].astype(np.float64), "chroma": chroma[:n].astype(np.float64),
            "mel": mel[:n].astype(np.float64), "poziom": poziom[:n].astype(np.float64), "klatek": n}


def koniec_zywej_muzyki(x: np.ndarray) -> float:
    """Koniec „żywej” muzyki: koniec ostatniego okna 0,5 s, którego RMS jest najwyżej 6 dB pod medianą utworu."""
    mono = x.mean(axis=1)
    pol = FS // 2
    okna = [rms(mono[i:i + pol]) for i in range(0, len(mono) - pol + 1, pol)]
    if not okna:
        return len(mono) / FS
    prog = float(np.median(okna)) * 10 ** (-6.0 / 20)
    ostatnie = max(i for i, v in enumerate(okna) if v >= prog)
    return round(min((ostatnie + 1) * 0.5, len(mono) / FS), 1)


def wybierz_miejsce(x: np.ndarray) -> dict:
    """Najlepsza para (początek, koniec) pętli. Zwraca wybor_miejsca + próbki S, E (44,1 kHz) przed dosunięciem."""
    c = cechy(x)
    na_s = FS_A / HOP
    ka, kb = int(round(PRZED_S * na_s)), int(round(PO_S * na_s))
    w = ka + kb
    zywa = koniec_zywej_muzyki(x)
    j_od = max(int(round((zywa - OKNO_KONCA_S) * na_s)), int(round((START_DO_S + PO_S + 5.0) * na_s)))
    j_do = min(int(round((zywa - PO_S) * na_s)), c["klatek"] - kb - 1)
    i_od, i_do = int(math.ceil(START_OD_S * na_s)), int(round(START_DO_S * na_s))
    if j_do <= j_od:
        sys.exit("utwór za krótki na pętlę (żywa muzyka do %.1f s)" % zywa)
    js = np.arange(j_od, j_do + 1)
    # okna wokół kandydatów na koniec
    u = sliding_window_view(c["uderzenia"], w)[js - ka]
    uz = (u - u.mean(axis=1, keepdims=True)) / (u.std(axis=1, keepdims=True) + 1e-9)
    ch = sliding_window_view(c["chroma"], w, axis=0)[js - ka]            # (J, 12, w)
    suma_mel = np.concatenate([np.zeros((1, c["mel"].shape[1])), np.cumsum(c["mel"], axis=0)])
    suma_poz = np.concatenate([[0.0], np.cumsum(c["poziom"])])

    def srednia(suma, a, b):
        roznica, n = suma[b] - suma[a], b - a
        return roznica / (n[:, None] if roznica.ndim == 2 and np.ndim(n) == 1 else n)

    mel_j = srednia(suma_mel, js - ka, js + kb)
    mel_j_n = mel_j / (np.linalg.norm(mel_j, axis=1, keepdims=True) + 1e-9)

    def moc_db(v):
        return 10.0 * np.log10(np.maximum(v, 1e-12))

    przed_j, po_j = moc_db(srednia(suma_poz, js - ka, js)), moc_db(srednia(suma_poz, js, js + kb))
    premia = PREMIA_DLUGOSCI * (js - j_od) / max(j_do - j_od, 1)   # przy zbliżonym dopasowaniu wygrywa dłuższa pętla
    najlepszy = None
    for i in range(i_od, int(round(START_DO_WSTEP_S * na_s)) + 1):
        if i == i_do + 1 and najlepszy[7] <= KARA_WSTEPU:
            break                                             # zwykły przypadek: początek pętli w pierwszych 1–3 s
        a = c["uderzenia"][i - ka:i + kb]
        az = (a - a.mean()) / (a.std() + 1e-9)
        rytm = np.maximum(uz @ az / w, 0.0)
        harmonia = np.einsum("jcw,wc->j", ch, c["chroma"][i - ka:i + kb]) / w
        m = srednia(suma_mel, i - ka, i + kb)
        barwa = mel_j_n @ (m / (np.linalg.norm(m) + 1e-9))
        wynik = WAGI[0] * rytm + WAGI[1] * harmonia + WAGI[2] * barwa
        kara = 0.01 * (np.maximum(np.abs(przed_j - moc_db(srednia(suma_poz, i - ka, i))) - 2.0, 0)
                       + np.maximum(np.abs(po_j - moc_db(srednia(suma_poz, i, i + kb))) - 2.0, 0))
        ocena = wynik - kara + premia
        k = int(np.argmax(ocena))
        if najlepszy is None or ocena[k] > najlepszy[0]:
            najlepszy = (float(ocena[k]), i, int(js[k]), float(wynik[k]), float(rytm[k]), float(harmonia[k]),
                         float(barwa[k]), float(kara[k]))
    _, i, j, wynik, rytm, harmonia, barwa, kara = najlepszy
    return {
        "wynik_dopasowania": round(wynik, 3), "rytm": round(rytm, 3), "harmonia": round(harmonia, 3),
        "barwa": round(barwa, 3), "kara_glosnosci": round(kara, 3), "koniec_zywej_muzyki_s": zywa,
        "_S": int(round(i * HOP / FS_A * FS)), "_E": int(round(j * HOP / FS_A * FS)),
    }


def zbuduj_petle(x: np.ndarray, s: int, e: int) -> tuple[np.ndarray, dict]:
    """Pętla x[s:e] z ostatnią sekundą = koniec wyciszany + sekunda sprzed s narastająca. s dosuwane co do próbki."""
    dl = int(PRZENIKANIE_S * FS)
    mono = x.mean(axis=1).astype(np.float64)
    koniec = mono[e - dl:e]
    maks = int(DOSUNIECIE_S * FS)
    maks = min(maks, s - dl)                                  # przed początkiem musi zostać sekunda
    najlepsze, kor = 0, -2.0
    nk = np.linalg.norm(koniec) + 1e-12
    for d in range(-maks, maks + 1):
        p = mono[s - dl + d:s + d]
        k = float(koniec @ p / (nk * (np.linalg.norm(p) + 1e-12)))
        if k > kor:
            najlepsze, kor = d, k
    s2 = s + najlepsze
    waga = ((np.arange(dl) + 1) / dl).astype(np.float32)[:, None]      # liniowo 0 → 1; ostatnia próbka = x[s2 - 1]
    petla = x[s2:e].copy()
    petla[-dl:] = x[e - dl:e] * (1.0 - waga) + x[s2 - dl:s2] * waga
    return petla, {
        "przenikanie_s": PRZENIKANIE_S, "ksztalt_przenikania": "liniowe",
        "korelacja_fali_w_przenikaniu": round(kor, 3), "przesuniecie_probki": int(najlepsze),
        "dlugosc_petli_s": round(len(petla) / FS, 3), "_start_s": round(s2 / FS, 3), "_koniec_s": round(e / FS, 3),
    }


# --------------------------------------------------------------------------- polecenia
def przetworz(oryginal: Path, wyjscie: Path, bezstratne: Path | None = None) -> dict:
    ident = oryginal.stem
    x = dekoduj(oryginal)
    p_org = pomiary(oryginal, x)
    wzm = round(min(CEL_LUFS - p_org["lufs_zintegrowana"], SZCZYT_MAX_DBTP - p_org["true_peak_dbtp"]), 1)
    miejsce = wybierz_miejsce(x)
    petla, budowa = zbuduj_petle(x, miejsce.pop("_S"), miejsce.pop("_E"))
    miejsce["start_s"], miejsce["koniec_s"] = budowa.pop("_start_s"), budowa.pop("_koniec_s")
    plik_mp3, plik_ogg = wyjscie / (ident + ".mp3"), wyjscie / (ident + "_petla.ogg")
    for _ in range(6):
        g = 10 ** (wzm / 20.0)
        koduj(x * g, plik_mp3, "mp3")
        koduj(petla * g, plik_ogg, "ogg")
        p_mp3, p_ogg = pomiary(plik_mp3), pomiary(plik_ogg)
        nadmiar = max(p_mp3["true_peak_dbtp"], p_ogg["true_peak_dbtp"]) - SZCZYT_MAX_DBTP
        if nadmiar <= 1e-6:
            break
        wzm = round(wzm - math.ceil(nadmiar * 10 - 1e-6) / 10.0, 1)
    if bezstratne:
        koduj(petla * g, bezstratne / (ident + "_petla.flac"), "flac")
    y = dekoduj(plik_ogg)
    p_ogg["skok_probki_na_szwie"] = round(float(np.max(np.abs(y[-1] - y[0]))), 4)
    # dla porównania: zwykła różnica sąsiednich próbek w 10 ms przed i po szwie (95. centyl) — skok na szwie
    # podobnej wielkości to po prostu przebieg fali, a nie trzask
    obok = np.abs(np.diff(np.concatenate([y[-FS // 100:], y[:FS // 100]]), axis=0)).max(axis=1)
    p_ogg["skok_sasiednich_probek_p95"] = round(float(np.percentile(obok, 95)), 4)
    kolejnosc = ["wynik_dopasowania", "rytm", "harmonia", "barwa", "start_s", "koniec_s", "koniec_zywej_muzyki_s",
                 "kara_glosnosci"]
    p_ogg["wybor_miejsca"] = {k: miejsce[k] for k in kolejnosc}
    p_ogg["budowa"] = budowa
    return {"id": ident, "wzmocnienie_db": wzm, "pliki": {"pelna_wyrownana": plik_mp3.name, "petla": plik_ogg.name},
            "pomiary": {"oryginal": p_org, "pelna_wyrownana": p_mp3, "petla": p_ogg}}


def analiza(plik: Path) -> dict:
    x = dekoduj(plik)
    miejsce = wybierz_miejsce(x)
    _, budowa = zbuduj_petle(x, miejsce.pop("_S"), miejsce.pop("_E"))
    miejsce["start_s"], miejsce["koniec_s"] = budowa.pop("_start_s"), budowa.pop("_koniec_s")
    return {"id": plik.stem, "wybor_miejsca": miejsce, "budowa": budowa}


def main() -> int:
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("polecenie", choices=["przetworz", "analiza", "pomiary"])
    ap.add_argument("pliki", nargs="+", type=Path)
    ap.add_argument("--wyjscie", type=Path, help="folder na gotowe pliki (przetworz)")
    ap.add_argument("--bezstratne", type=Path, help="przetworz: zapisz tu także pętle bez strat (<id>_petla.flac) — "
                                                     "źródło dla arkusza muzyki; folder poza gitem, np. …/oryginaly")
    ap.add_argument("--raport", type=Path, help="zapisz wynik jako JSON (lista wpisów)")
    a = ap.parse_args()
    if a.polecenie == "przetworz" and not a.wyjscie:
        ap.error("przetworz wymaga --wyjscie")
    wyniki = []
    for p in a.pliki:
        if not p.is_file():
            sys.exit("nie ma pliku %s" % p.name)
        if a.polecenie == "przetworz":
            a.wyjscie.mkdir(parents=True, exist_ok=True)
            if a.bezstratne:
                a.bezstratne.mkdir(parents=True, exist_ok=True)
            w = przetworz(p, a.wyjscie, a.bezstratne)
            pe, m = w["pomiary"]["petla"], w["pomiary"]["petla"]["wybor_miejsca"]
            print("%s: wzmocnienie %+.1f dB · pełna %.1f s, %.1f LUFS, szczyt %.1f dBTP · pętla %.3f s (%.3f–%.3f), "
                  "%.1f LUFS, szczyt %.1f dBTP, dopasowanie %.3f (rytm %.3f, harmonia %.3f, barwa %.3f), skok na szwie %.4f"
                  % (w["id"], w["wzmocnienie_db"], w["pomiary"]["pelna_wyrownana"]["dlugosc_s"],
                     w["pomiary"]["pelna_wyrownana"]["lufs_zintegrowana"], w["pomiary"]["pelna_wyrownana"]["true_peak_dbtp"],
                     pe["dlugosc_s"], m["start_s"], m["koniec_s"], pe["lufs_zintegrowana"], pe["true_peak_dbtp"],
                     m["wynik_dopasowania"], m["rytm"], m["harmonia"], m["barwa"], pe["skok_probki_na_szwie"]))
        elif a.polecenie == "analiza":
            w = analiza(p)
            m = w["wybor_miejsca"]
            print("%s: pętla %.3f–%.3f s (żywa muzyka do %.1f s), dopasowanie %.3f (rytm %.3f, harmonia %.3f, barwa %.3f, "
                  "kara %.3f), korelacja fali %.3f" % (w["id"], m["start_s"], m["koniec_s"], m["koniec_zywej_muzyki_s"],
                                                      m["wynik_dopasowania"], m["rytm"], m["harmonia"], m["barwa"],
                                                      m["kara_glosnosci"], w["budowa"]["korelacja_fali_w_przenikaniu"]))
        else:
            w = {"plik": p.name, "pomiary": pomiary(p)}
            print("%s: %.3f s, %.1f LUFS, szczyt %.1f dBTP" % (p.name, w["pomiary"]["dlugosc_s"],
                                                                w["pomiary"]["lufs_zintegrowana"], w["pomiary"]["true_peak_dbtp"]))
        wyniki.append(w)
    if a.raport:
        a.raport.parent.mkdir(parents=True, exist_ok=True)
        a.raport.write_text(json.dumps(wyniki, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
