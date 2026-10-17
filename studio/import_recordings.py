"""Gerçek (insan) ses kayıtlarını içe aktarır: telefon kaydını temizler ve videoya hazır hâle getirir.

Dosyalar seslendirme rehberindeki kimliklerle adlandırılmalı: n1.m4a, e1.mp3, p1.wav ...
(bkz. docs/04_seslendirme_rehberi.md)

    python3 import_recordings.py --src ~/kayitlar
    python3 ep01_renkli_kelebek.py --style kagit      # yeni seslerle yeniden üret

İşlemler: uğultu süzme, hafif gürültü temizleme, baş/son sessizliği kesme, dinamik sıkıştırma,
yayın seviyesine (-16 LUFS) getirme, 48 kHz mono.
"""
import argparse
import glob
import os
import subprocess
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_renkli_kelebek import CUES, DURATION, VO_DIR

CLEAN = ("highpass=f=80,afftdn=nf=-25,"
         "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=100,"
         "loudnorm=I=-16:TP=-2,adelay=30,apad=pad_dur=0.08")
EXTS = (".m4a", ".mp3", ".wav", ".ogg", ".aac", ".flac", ".opus", ".mp4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="kayıtların bulunduğu klasör")
    a = ap.parse_args()
    os.makedirs(VO_DIR, exist_ok=True)
    starts = [c[1] for c in CUES] + [DURATION]
    found = 0
    for i, (cid, start, who, text) in enumerate(CUES):
        src = next((f for f in glob.glob(os.path.join(a.src, cid + ".*")) if f.lower().endswith(EXTS)), None)
        if not src:
            print(f"  - {cid:4} bulunamadı, mevcut ses korunuyor  ({text})")
            continue
        out = os.path.join(VO_DIR, f"{cid}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", CLEAN, "-ac", "1", "-ar", "48000",
                        "-sample_fmt", "s16", out], check=True)
        with wave.open(out) as w:
            d = w.getnframes() / w.getframerate()
        slot = starts[i + 1] - start
        note = "" if d <= slot else f"  ⚠ {d - slot:.1f} sn uzun, sahne zamanlaması kaydırılmalı"
        print(f"  ✓ {cid:4} {d:4.1f} sn{note}")
        found += 1
    print(f"{found}/{len(CUES)} kayıt içe aktarıldı.")


if __name__ == "__main__":
    main()
