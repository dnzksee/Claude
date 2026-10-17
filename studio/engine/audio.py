"""Müzik ve ses efekti sentezi (özgün, telifsiz). 48 kHz stereo.

Çocuk kulağı için ilkeler: yumuşak tınılar (kalimba, müzik kutusu, ksilofon), ani yüksek ses yok,
konuşma sırasında müzik otomatik kısılır (ducking), toplam seviye sakin."""
import math
import os
import wave

import numpy as np

SR = 48000


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def n(name):
    """'C5' -> midi"""
    return NOTE[name[:-1]] + 12 * (int(name[-1]) + 1)


class Bus:
    def __init__(self, dur):
        self.buf = np.zeros((int(dur * SR) + SR, 2), np.float32)

    def add(self, t, sig, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= len(self.buf) or i + len(sig) <= 0:
            return
        if i < 0:
            sig = sig[-i:]
            i = 0
        sig = sig[: len(self.buf) - i]
        l = math.cos((pan + 1) * math.pi / 4) * gain
        r = math.sin((pan + 1) * math.pi / 4) * gain
        if sig.ndim == 1:
            self.buf[i:i + len(sig), 0] += sig * l
            self.buf[i:i + len(sig), 1] += sig * r
        else:
            self.buf[i:i + len(sig)] += sig * np.array([l, r], np.float32) * 1.414


def _t(d):
    return np.arange(int(d * SR), dtype=np.float32) / SR


def env_adsr(n_, a=0.005, d=0.1, s=0.0, r=0.1, dur=None):
    t = np.arange(n_, dtype=np.float32) / SR
    e = np.ones(n_, np.float32)
    e = np.where(t < a, t / max(a, 1e-4), e)
    return e


def kalimba(f, dur=1.4, bright=1.0):
    t = _t(dur)
    att = np.clip(t / 0.003, 0, 1)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.55)
    s += 0.18 * bright * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.12)
    s += 0.07 * bright * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.05)
    return (s * att).astype(np.float32)


def glock(f, dur=1.8):
    t = _t(dur)
    att = np.clip(t / 0.002, 0, 1)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
    s += 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.3)
    s += 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.1)
    return (s * att * 0.7).astype(np.float32)


def xylo(f, dur=0.5):
    t = _t(dur)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.13) + 0.3 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.03)
    return (s * np.clip(t / 0.002, 0, 1)).astype(np.float32)


def bass(f, dur=0.6, decay=0.35):
    t = _t(dur)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    e = np.clip(t / 0.008, 0, 1) * np.exp(-t / decay)
    e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return (s * e).astype(np.float32)


def pad(freqs, dur, attack=0.9, release=1.2):
    t = _t(dur + release)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0.0, 0.0045):
            ph = np.random.default_rng(int(f)).random() * 6.28
            s += np.sin(2 * np.pi * f * (1 + det) * t + ph) + 0.15 * np.sin(4 * np.pi * f * (1 + det) * t)
    s /= max(1, len(freqs) * 3)
    e = np.clip(t / attack, 0, 1) * np.clip((dur + release - t) / release, 0, 1)
    vib = 1 + 0.08 * np.sin(2 * np.pi * 0.25 * t)
    return (s * e * vib).astype(np.float32)


def shaker(dur=0.07):
    t = _t(dur)
    x = np.random.default_rng(int(dur * 1e6) % 999).standard_normal(len(t)).astype(np.float32)
    x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-t / 0.018) * 0.25


def chirp_bird(seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(rng.integers(2, 5)):
        d = 0.06 + rng.random() * 0.05
        t = _t(d)
        f0, f1 = 2600 + rng.random() * 1500, 3600 + rng.random() * 1800
        f = f0 + (f1 - f0) * (t / d)
        ph = 2 * np.pi * np.cumsum(f) / SR
        out.append(np.sin(ph) * np.sin(np.pi * t / d) ** 2)
        out.append(np.zeros(int(0.04 * SR)))
    return np.concatenate(out).astype(np.float32) * 0.35


def boing(f0=300, f1=700, d=0.22):
    t = _t(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.12) * np.clip(t / 0.004, 0, 1)).astype(np.float32) * 0.6


def pop(d=0.12):
    t = _t(d)
    f = 900 * np.exp(-t / 0.03) + 250
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.04)).astype(np.float32) * 0.7


def whoosh(d=0.8, seed=1):
    t = _t(d)
    x = np.random.default_rng(seed).standard_normal(len(t)).astype(np.float32)
    # basit band-geçiren: iki tek kutuplu süzgeç farkı, kesim frekansı süpürülür
    out = np.zeros_like(x)
    lp1 = lp2 = 0.0
    fc = 400 + 2200 * np.sin(np.pi * t / d)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(len(x)):
        lp1 += a[i] * (x[i] - lp1)
        lp2 += 0.02 * (lp1 - lp2)
        out[i] = lp1 - lp2
    return out * np.sin(np.pi * t / d) ** 2 * 0.35


def sparkle(seed=0, base=n("C6")):
    s = np.zeros(int(1.6 * SR), np.float32)
    for k, step in enumerate([0, 4, 7, 12, 16]):
        g = glock(midi_hz(base + step), 1.2) * (0.55 - k * 0.06)
        i = int(k * 0.06 * SR)
        s[i:i + len(g)] += g[: len(s) - i]
    return s


def poof(d=0.5):
    t = _t(d)
    x = np.random.default_rng(3).standard_normal(len(t)).astype(np.float32)
    k = np.ones(40) / 40
    x = np.convolve(x, k, mode="same")
    return x * np.exp(-t / 0.12) * np.clip(t / 0.01, 0, 1) * 1.5


def load_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
    if sr != SR:
        idx = np.arange(0, len(data), sr / SR)
        data = np.interp(idx, np.arange(len(data)), data).astype(np.float32)
    return data


def write_wav(path, stereo):
    x = np.clip(stereo, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def duck_curve(dur, spans, depth=0.35, fade=0.25):
    """Konuşma aralıklarında müziği kısar."""
    t = np.arange(int(dur * SR) + SR, dtype=np.float32) / SR
    g = np.ones_like(t)
    for a, b in spans:
        w = np.clip(np.minimum((t - (a - fade)) / fade, ((b + fade) - t) / fade), 0, 1)
        g = np.minimum(g, 1 - (1 - depth) * w)
    return g


def soft_limit(x, ceiling=0.89):
    peak = np.max(np.abs(x)) + 1e-9
    x = x / peak * 1.05
    return np.tanh(x * 1.2) / np.tanh(1.2) * ceiling


# ---------------------------------------------------------------- v2: sıcak, eğlenceli ama yumuşak tınılar
_PLUCK = {}


def pluck(f, dur=0.9, bright=1.0):
    """Ukulele benzeri telli çalgı (toplamsal sentez, önbellekli)."""
    key = (round(f, 2), dur, bright)
    if key not in _PLUCK:
        t = _t(dur)
        s = np.zeros_like(t)
        for k in range(1, 12):
            if f * k > 11000:
                break
            s += (1 / k ** 1.3) * np.sin(2 * np.pi * f * k * t + k * 0.7) * np.exp(-t * (2.4 + 1.2 * k * bright))
        s *= np.clip(t / 0.0025, 0, 1)
        r = int(0.03 * SR)
        s[-r:] *= np.linspace(1, 0, r)
        _PLUCK[key] = (s * 0.45).astype(np.float32)
    return _PLUCK[key]


UKE = {"C": ["G4", "C4", "E4", "C5"], "G": ["G4", "D4", "G4", "B4"], "Am": ["A4", "C4", "E4", "A4"],
       "F": ["A4", "C4", "F4", "A4"], "G7": ["G4", "D4", "F4", "B4"]}


def strum(chord, down=True, dur=0.75, spread=0.011):
    names = UKE[chord] if down else UKE[chord][::-1]
    out = np.zeros(int((dur + spread * 5) * SR), np.float32)
    for i, nm in enumerate(names):
        s = pluck(midi_hz(n(nm)), dur, 0.85 if down else 1.15)
        o = int(i * spread * SR)
        out[o:o + len(s)] += s * (1.0 - 0.07 * i)
    return out


def whistle(f, dur):
    """Neşeli ıslık melodisi: hafif vibratolu sinüs."""
    t = _t(dur + 0.12)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.12) / 0.2, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    s = np.sin(ph) + 0.08 * np.sin(2 * ph)
    e = np.clip(t / 0.035, 0, 1) * np.clip((dur + 0.12 - t) / 0.1, 0, 1)
    breath = np.random.default_rng(int(f)).standard_normal(len(t)).astype(np.float32)
    breath = np.convolve(breath, np.ones(6) / 6, "same") * 0.015
    return ((s + breath) * e * 0.5).astype(np.float32)


def snap(d=0.08):
    t = _t(d)
    x = np.random.default_rng(5).standard_normal(len(t)).astype(np.float32)
    x = x - np.convolve(x, np.ones(8) / 8, "same")
    return x * np.exp(-t / 0.012) * 0.5


def soft_kick(d=0.25):
    t = _t(d)
    f = 48 + 50 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.09) * np.clip(t / 0.003, 0, 1)).astype(np.float32) * 0.8


def reverb(stereo, seconds=1.7, wet=0.22, seed=11):
    """Sıcak oda yankısı (sentetik dürtü yanıtı ile evrişim)."""
    from scipy.signal import fftconvolve
    t = _t(seconds)
    out = stereo * (1 - wet * 0.5)
    for ch in range(2):
        ir = np.random.default_rng(seed + ch).standard_normal(len(t)).astype(np.float32)
        ir = np.convolve(ir, np.ones(12) / 12, "same")  # koyu (yumuşak) yankı
        ir *= np.exp(-t * 6.9 / seconds) * np.clip(t / 0.01, 0, 1)
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        out[:, ch] += fftconvolve(stereo[:, ch], ir)[: len(stereo)].astype(np.float32) * wet
    return out


def lowpass(stereo, fc=9000, order=2):
    from scipy.signal import butter, sosfilt
    sos = butter(order, fc / (SR / 2), output="sos")
    return sosfilt(sos, stereo, axis=0).astype(np.float32)
