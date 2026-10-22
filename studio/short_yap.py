"""YouTube Shorts: bölüm videosundan bir parçayı dikey 1080x1920 yapar.
Üstte kanal yazı logosu ve başlık, ortada video (kare kesit, net), altta çağrı yazısı.

    python3 short_yap.py --src ../renders/umay_zipzip_bolum1_renkli_kelebekler.mp4 --start 187.8 --end 243.8 \\
        --baslik "Mavi Tekerlemesi" --alt "Sen de söyle!" --alt2 "Tam bölüm: Renkli Kelebekler" \\
        --out ../shorts/short_bolum1_mavi_tekerlemesi.mp4
"""
import argparse
import os
import subprocess
import sys

import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.core import hexrgb
from engine.styles import Canvas
from engine.characters import draw_butterfly
from engine import props as P
import kanal_gorselleri as K

SW, SH = 1080, 1920
VY = 430          # videonun üst kenarı
CROP = 960        # kaynaktan alınan kare (1920x1080 içinde, alta yaslı ortada)


def arka_plan(path, baslik, alt, alt2, renk):
    cv = Canvas(SW, SH)
    p = K.painter(cv)
    p.part(lambda c: c.rectangle(0, 0, SW, SH), None, grad=(K.SKY[0], K.SKY[1], 0, SH), line=False, flat=True, seed="sbg")
    K.sun_burst(p, SW / 2, 230, 60, 1200, 18, (1, 1, 1), alpha=0.14)
    K.text(p, "Umay ile Zıpzıp", SW / 2, 120, 96, K.TITLE_COL, lw=1.6)
    K.text(p, baslik, SW / 2, 290, 108, P.COL[renk], lw=2.0)
    draw_butterfly(p, 80, 70, 0.7, 0.3, rot=-0.2, col=P.COL[renk])
    draw_butterfly(p, SW - 80, 70, 0.7, 0.5, rot=0.25, col=P.COL[renk])
    y0 = VY + SW
    p.part(lambda c: c.rectangle(0, y0, SW, SH - y0), hexrgb("#7CC062"), seed="sgr", flat=True)
    K.text(p, alt, SW / 2, y0 + 140, 110, (1, 1, 1), lw=1.8)
    K.text(p, alt2, SW / 2, y0 + 285, 56, hexrgb("#FFE36E"), lw=1.2)
    cv.surface.flush()
    cv2.imwrite(path, cv.arr[..., :3].copy())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--baslik", required=True)
    ap.add_argument("--alt", default="Sen de söyle!")
    ap.add_argument("--alt2", default="")
    ap.add_argument("--renk", default="mavi", choices=["mavi", "kirmizi", "sari"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = a.end - a.start
    assert d <= 60.0, "Shorts en fazla 60 sn olsun"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    bg = os.path.splitext(a.out)[0] + "_arka.png"
    arka_plan(bg, a.baslik, a.alt, a.alt2, a.renk)
    x0, y0 = (1920 - CROP) // 2, 1080 - CROP
    fc = (f"[1:v]crop={CROP}:{CROP}:{x0}:{y0},scale={SW}:{SW}:flags=lanczos,setsar=1[v];"
          f"[0:v][v]overlay=0:{VY}:shortest=1,format=yuv420p[o];"
          f"[1:a]afade=t=in:d=0.3,afade=t=out:st={d - 1.2}:d=1.2[a]")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "24", "-i", bg,
                    "-ss", str(a.start), "-t", str(d), "-i", a.src, "-filter_complex", fc, "-map", "[o]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-r", "24", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", str(d), a.out], check=True)
    os.remove(bg)
    print(a.out)


if __name__ == "__main__":
    main()
