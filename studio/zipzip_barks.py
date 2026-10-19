"""Zıpzıp'ın sesleri: gerçek (CC0) köpek havlamasından yavru köpek havlaması üretir.
Kaynak: assets/sfx/kopek_havlama_CC0.wav (bkz. assets/sfx/KAYNAKLAR.md)

    python3 zipzip_barks.py      # assets/vo_ep1/ içine Zıpzıp'ın tüm satırlarını yazar
"""
import os
import sys

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_batch as VB
from senaryo_renkli_kelebekler import satirlar, Z

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "sfx", "kopek_havlama_CC0.wav")
PUPPY = 1.8    # perde çarpanı (~10 yarım ton): orta boy köpek → yavru köpek


def build():
    x, fs = VB.load(SRC)
    cut = lambda a, b: x[int(a * fs):int(b * fs)]
    gap = lambda s: np.zeros(int(s * fs))

    def pitch(sig, k):
        idx = np.arange(0, len(sig) - 1, k)
        return np.interp(idx, np.arange(len(sig)), sig)

    def fade(sig, a=0.004, b=0.025):
        n = len(sig)
        e = np.ones(n)
        na, nb = min(int(a * fs), n // 3), min(int(b * fs), n // 3)
        e[:na] = np.linspace(0, 1, na)
        e[-nb:] = np.linspace(1, 0, nb)
        return sig * e

    A = fade(pitch(cut(0.0, 0.21), PUPPY))
    B = fade(pitch(cut(0.51, 0.75), PUPPY * 1.04))
    C = fade(pitch(cut(1.67, 1.86), PUPPY * 1.08))
    # soru gibi: sonu yükselen havlama
    half = len(B) // 2
    Q = fade(np.concatenate([B[:half], pitch(B[half:], 1.3)]))
    rng = np.random.default_rng(3)

    def sniff(d=0.13):
        n = int(d * fs)
        t = np.arange(n) / fs
        s = rng.standard_normal(n)
        s = s - np.convolve(s, np.ones(6) / 6, "same")
        return s * np.sin(np.pi * t / d) ** 1.5 * 0.25

    n = int(0.6 * fs)
    t = np.arange(n) / fs
    sh = sosfilt(butter(4, [2200, 6500], btype="band", fs=fs, output="sos"), rng.standard_normal(n))
    sh = sh / np.abs(sh).max() * np.clip(t / 0.04, 0, 1) * np.exp(-t / 0.25) * 0.9
    hap = lambda k: fade(pitch(A, k)[: int(0.12 * fs)])
    return fs, {
        "Hav!": A,
        "Hav hav!": np.concatenate([A, gap(0.13), B]),
        "Hav hav hav!": np.concatenate([A, gap(0.11), B, gap(0.11), C]),
        "Hav?": Q,
        "Hıh hıh!": np.concatenate([sniff(), gap(0.09), sniff()]),
        "Hap... hap... hapşuuu!": np.concatenate([hap(1.0), gap(0.35), hap(1.06), gap(0.4), hap(1.12), sh]),
    }


def brighten(sig, fs):
    """Boğukluğu al: 2,5–6 kHz bölgesini biraz öne çıkar (yavru köpeğin ince, parlak sesi)."""
    hi = sosfilt(butter(2, 2500, btype="high", fs=fs, output="sos"), sig)
    return sig + 0.9 * hi


def main():
    fs, S = build()
    S = {k: brighten(v, fs) for k, v in S.items()}
    n = 0
    for cid, _, txt, _ in satirlar(Z):
        VB.write(os.path.join(VB.OUT, f"{cid}.wav"), np.clip(S[txt], -1, 1), fs, Z)
        n += 1
    print(n, "Zıpzıp sesi yazıldı")


if __name__ == "__main__":
    main()
