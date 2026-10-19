"""Zıpzıp'ın sesleri: gerçek (CC0) küçük köpek kaydından tek tek havlamalar kesilir.
Kaynak: assets/sfx/kopek_havlama_CC0_garuda1982.mp3 (bkz. assets/sfx/KAYNAKLAR.md)

    python3 zipzip_barks.py      # assets/vo_ep1/ içine Zıpzıp'ın tüm satırlarını yazar
"""
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_batch as VB
from senaryo_renkli_kelebekler import satirlar, Z

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "sfx", "kopek_havlama_CC0_garuda1982.mp3")
FS = 48000
# kayıttaki tek havlamalar (sn); Gemini dinleyip 9/10 "net, canlı, tatlı yavru" dedikleri
HAV1 = (2.455, 2.625)    # en dolgun, en güçlü
HAV2 = (8.005, 8.195)    # biraz daha tiz, oyuncu
HAV3 = (14.305, 14.465)  # parlak, arkadaş canlısı
HAV4 = (1.645, 1.820)
HAV5 = (6.295, 6.455)
YOUNG = 1.1      # perde: ~1,5 yarım ton yukarı — biraz daha yavru, daha kıvrak


def load_full():
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SRC, "-ac", "1", "-ar", str(FS), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return sosfiltfilt(butter(4, 140, btype="high", fs=FS, output="sos"), x)


def build():
    x = load_full()

    def pitch(sig, k):
        idx = np.arange(0, len(sig) - 1, k)
        return np.interp(idx, np.arange(len(sig)), sig)

    cut = lambda ab: pitch(x[int(ab[0] * FS):int(ab[1] * FS)], YOUNG)
    gap = lambda s: np.zeros(int(s * FS))

    def fade(sig, a=0.003, b=0.02):
        n = len(sig)
        e = np.ones(n)
        na, nb = min(int(a * FS), n // 3), min(int(b * FS), n // 3)
        e[:na] = np.linspace(0, 1, na)
        e[-nb:] = np.linspace(1, 0, nb) ** 2
        return sig * e

    def norm(sig, peak=0.9):
        return sig / (np.abs(sig).max() + 1e-9) * peak

    A = norm(fade(cut(HAV1)))
    B = norm(fade(cut(HAV2)), 0.85)
    C = norm(fade(cut(HAV3)), 0.9)
    # soru gibi: sonu yukarı kıvrılan havlama
    h = cut(HAV2)
    k = len(h) // 2
    Q = norm(fade(np.concatenate([h[:k], pitch(h[k:], 1.22)]), b=0.03), 0.8)
    hap = lambda ab, k: norm(fade(pitch(cut(ab), k)[: int(0.09 * FS)]), 0.45)
    rng = np.random.default_rng(3)

    def sniff(d=0.12):
        n = int(d * FS)
        t = np.arange(n) / FS
        s = sosfilt(butter(2, [1500, 7000], btype="band", fs=FS, output="sos"), rng.standard_normal(n))
        return norm(s * np.sin(np.pi * t / d) ** 1.5, 0.35)

    n = int(0.55 * FS)
    t = np.arange(n) / FS
    sh = sosfilt(butter(4, [2200, 7000], btype="band", fs=FS, output="sos"), rng.standard_normal(n))
    sh = norm(sh) * np.clip(t / 0.03, 0, 1) * np.exp(-t / 0.22) * 0.6
    return {
        "Hav!": A,
        "Hav hav!": np.concatenate([A, gap(0.10), B]),
        "Hav hav hav!": np.concatenate([A, gap(0.09), B, gap(0.09), C]),
        "Hav?": Q,
        "Hıh hıh!": np.concatenate([sniff(), gap(0.08), sniff()]),
        "Hap... hap... hapşuuu!": np.concatenate([hap(HAV4, 1.0), gap(0.3), hap(HAV5, 1.05), gap(0.32), hap(HAV3, 1.1), sh]),
    }


def brighten(sig):
    """3–6 kHz varlık bölgesini hafifçe aç: net, canlı, boğuk olmayan havlama."""
    pres = sosfilt(butter(2, [2500, 6500], btype="band", fs=FS, output="sos"), sig)
    return sig + 0.6 * pres


def main():
    S = {k: brighten(v) for k, v in build().items()}
    n = 0
    for cid, _, txt, _ in satirlar(Z):
        VB.write(os.path.join(VB.OUT, f"{cid}.wav"), np.clip(S[txt], -1, 1), FS, Z)
        n += 1
    print(n, "Zıpzıp sesi yazıldı")


if __name__ == "__main__":
    main()
