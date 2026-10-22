"""YouTube kanalı "Umay ile Zıpzıp" görselleri: profil logosu, banner, filigran, yazı logosu, bölüm kapakları.
Karakterler bölümlerdeki çizim motoruyla, Batı çizgi filmi (cizgi) stilinde çizilir.

    python3 kanal_gorselleri.py          # kanal/ klasörüne hepsini yazar
"""
import math
import os
import sys

import cairo
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.core import circle, ellipse, rounded_rect, hexrgb, blob
from engine.styles import Canvas, PAINTERS
from engine.characters import PAL, draw_umay, draw_zipzip, draw_butterfly, draw_flower, umay_arm_pose, star
from engine import world
from engine import props as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "kanal")
STYLE = "cizgi"
SKY = (hexrgb("#3F96E6"), hexrgb("#BFE2F8"))
TITLE_COL = hexrgb("#F2665C")
SUB_COL = hexrgb("#2F6FD0")


def painter(cv):
    return PAINTERS[STYLE](cv, t=0.0, scale=1.0, frame=0)


def save(cv, name, alpha=False):
    cv.surface.flush()
    a = cv.arr.astype(np.float32) / 255.0
    if alpha:
        al = a[..., 3:4]
        rgb = np.where(al > 0, a[..., :3] / np.maximum(al, 1e-4), 0)
        img = np.concatenate([rgb, al], axis=2)
    else:
        img = a[..., :3]
    path = os.path.join(OUT, name)
    cv2.imwrite(path, (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    print(path)
    return path


def text(p, s, x, y, size, col, lw=1.3, anchor="c"):
    ctx = p.ctx
    ctx.save()
    ctx.select_font_face("Baloo 2", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    x0 = x - ext.width / 2 - ext.x_bearing if anchor == "c" else x - ext.x_bearing
    y0 = y - ext.height / 2 - ext.y_bearing

    def tp(c):
        c.move_to(x0, y0)
        c.text_path(s)

    p.part(tp, col, lw=lw, seed=f"tx{s}{size}", flat=True)
    ctx.restore()
    return ext.width


def wordmark(p, x, y, size):
    """'Umay ile Zıpzıp' yazı logosu: iki satır, Umay kırmızı, Zıpzıp mavi, arada sarı 'ile'."""
    text(p, "Umay", x, y - size * 0.55, size, TITLE_COL, lw=1.6)
    text(p, "ile", x, y + size * 0.05, size * 0.42, hexrgb("#F2A61C"), lw=1.1)
    text(p, "Zıpzıp", x, y + size * 0.62, size, SUB_COL, lw=1.6)


def sun_burst(p, cx, cy, r0, r1, n, col, alpha=1.0):
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = a0 + math.pi / n
        p.part(lambda c, a0=a0, a1=a1: (c.move_to(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0),
                                        c.line_to(cx + math.cos(a0) * r1, cy + math.sin(a0) * r1),
                                        c.line_to(cx + math.cos(a1) * r1, cy + math.sin(a1) * r1), c.close_path()),
               col, alpha=alpha, line=False, flat=True, seed=f"sb{i}")


def duo(p, x, y, s, wave=True):
    """Umay (el sallar) + Zıpzıp (mutlu) yan yana; x, y: Umay'ın ayakları."""
    draw_zipzip(p, x + 175 * s, y, 1.0 * s, {"facing": -1, "happy": 1.0, "mouth": 0.6, "wag": 1.0})
    arms = umay_arm_pose("wave", 0.3) if wave else umay_arm_pose("idle", 0.0)
    draw_umay(p, x, y, 1.0 * s, {"facing": 1, "arms": arms, "happy": 0.7, "mouth": 0.5, "smile": 1.0})


# --------------------------------------------------------------- profil (800x800, daire içinde okunur)
def profil():
    N = 800
    cv = Canvas(N, N)
    p = painter(cv)
    p.part(lambda c: c.rectangle(0, 0, N, N), None, grad=(SKY[0], SKY[1], 0, N), line=False, flat=True, seed="pbg")
    sun_burst(p, N / 2, N * 0.42, 60, 620, 16, hexrgb("#FFFFFF"), alpha=0.16)
    p.part(lambda c: blob(c, N / 2, N * 1.18, N * 0.75, n=12, wobble=0.04, seed=3, sy=0.55), hexrgb("#7CC062"), seed="phill", flat=True)
    draw_butterfly(p, N * 0.80, N * 0.22, 1.1, 0.3, rot=0.2, col=P.COL["mavi"])
    ctx = p.ctx
    ctx.save()
    ctx.translate(N * 0.66, N * 1.0)
    ctx.scale(1.75, 1.75)
    draw_zipzip(p, -250, 0, 1.0, {"facing": 1, "happy": 1.0, "mouth": 0.6})
    draw_umay(p, 0, 0, 1.0, {"facing": 1, "arms": umay_arm_pose("cheer", 0.3), "happy": 0.7, "mouth": 0.5})
    ctx.restore()
    return save(cv, "profil_logo_800.png")


# --------------------------------------------------------------- banner (2560x1440; güvenli alan ortada 1546x423)
def banner():
    BW, BH = 2560, 1440
    cv = Canvas(BW, BH)
    p = painter(cv)
    p.part(lambda c: c.rectangle(0, 0, BW, BH), None, grad=(SKY[0], SKY[1], 0, BH * 0.75), line=False, flat=True, seed="bbg")
    for i, (cx, cy, k) in enumerate([(330, 470, 1.3), (2250, 450, 1.1), (900, 330, 0.8), (1800, 360, 0.9)]):
        world.cloud(p, cx, cy, k, i)
    p.part(lambda c: world.hills(c, -100, BW + 100, 880, 120, 3, bottom=BH + 50, step=420), hexrgb("#9CC3C6"), seed="bfar", line=False, flat=True)
    p.part(lambda c: world.hills(c, -100, BW + 100, 930, 90, 11, bottom=BH + 50, step=520), hexrgb("#8CC66A"), seed="bmid", flat=True)
    p.part(lambda c: world.hills(c, -100, BW + 100, 930, 25, 19, bottom=BH + 50, step=600), hexrgb("#7CC062"), seed="bgr", flat=True)
    for i, x in enumerate((140, 420, 2140, 2420)):
        draw_flower(p, x, 1010, 0.9, [P.COL["mavi"], P.COL["kirmizi"], P.COL["sari"], P.COL["mavi"]][i],
                    center=hexrgb("#FFE36E"), seed=f"bfl{i}")
    # güvenli alan (masaüstünde görünen şerit): x 507..2053, y 508..931 — Umay solda, yazı ortada, Zıpzıp sağda
    ctx = p.ctx
    ctx.save()
    ctx.translate(700, 930)
    ctx.scale(1.2, 1.2)
    draw_umay(p, 0, 0, 1.0, {"facing": 1, "arms": umay_arm_pose("cheer", 0.3), "happy": 0.7, "mouth": 0.5})
    ctx.restore()
    ctx.save()
    ctx.translate(1900, 930)
    ctx.scale(1.2, 1.2)
    draw_zipzip(p, 0, 0, 1.0, {"facing": -1, "happy": 1.0, "mouth": 0.6})
    ctx.restore()
    draw_butterfly(p, 1700, 560, 0.9, 0.4, rot=0.15, col=P.COL["mavi"])
    text(p, "Umay ile Zıpzıp", 1270, 640, 125, TITLE_COL, lw=1.8)
    text(p, "Renkler · Şarkılar · Minik maceralar", 1270, 765, 54, hexrgb("#FFFFFF"), lw=1.2)
    text(p, "2–5 yaş için", 1270, 845, 48, hexrgb("#FFC928"), lw=1.1)
    return save(cv, "banner_2560x1440.png")


# --------------------------------------------------------------- filigran (150x150, saydam) ve yazı logosu
def filigran():
    N = 300
    cv = Canvas(N, N)
    p = painter(cv)
    p.part(lambda c: circle(c, N / 2, N / 2, N * 0.47), hexrgb("#FFFFFF"), seed="fbg", flat=True)
    p.part(lambda c: circle(c, N / 2, N / 2, N * 0.41), None, grad=(SKY[0], SKY[1], 20, N), line=False, flat=True, seed="fsky")
    ctx = p.ctx
    ctx.save()
    ctx.translate(N * 0.5, N * 0.40)
    ctx.scale(1.25, 1.25)
    draw_zipzip(p, -95, 125, 1.0, {"facing": 1, "happy": 1.0, "mouth": 0.6})
    ctx.restore()
    big = save(cv, "_filigran_300.png", alpha=True)
    im = cv2.imread(big, cv2.IMREAD_UNCHANGED)
    path = os.path.join(OUT, "filigran_150.png")
    cv2.imwrite(path, cv2.resize(im, (150, 150), interpolation=cv2.INTER_AREA))
    os.remove(big)
    print(path)


def yazi_logo():
    cv = Canvas(1400, 700)
    p = painter(cv)
    wordmark(p, 700, 330, 200)
    draw_butterfly(p, 1110, 150, 0.9, 0.3, rot=0.25, col=P.COL["mavi"])
    return save(cv, "yazi_logo_saydam.png", alpha=True)


# --------------------------------------------------------------- bölüm kapağı (1280x720)
def kapak_bolum1():
    KW, KH = 1920, 1080
    cv = Canvas(KW, KH)
    p = painter(cv)
    p.part(lambda c: c.rectangle(0, 0, KW, KH), None, grad=(SKY[0], SKY[1], 0, KH), line=False, flat=True, seed="kbg")
    sun_burst(p, 520, 640, 80, 1500, 18, hexrgb("#FFFFFF"), alpha=0.14)
    p.part(lambda c: blob(c, 520, 1250, 900, n=12, wobble=0.04, seed=3, sy=0.45), hexrgb("#7CC062"), seed="khill", flat=True)
    for i, (x, col) in enumerate(((90, "mavi"), (880, "kirmizi"), (990, "sari"))):
        draw_flower(p, x, 1060, 1.3, P.COL[col], center=hexrgb("#FFE36E") if col != "mavi" else hexrgb("#2A5FC2"), seed=f"kf{i}")
    ctx = p.ctx
    ctx.save()
    ctx.translate(560, 1010)
    ctx.scale(1.85, 1.85)
    draw_zipzip(p, -250, 0, 1.0, {"facing": 1, "happy": 1.0, "mouth": 0.7, "look_up": 0.5})
    draw_umay(p, 0, 0, 1.0, {"facing": 1, "arms": umay_arm_pose("point", 0.3), "happy": 0.8, "mouth": 0.7, "eye_dy": -2})
    ctx.restore()
    for i, (x, y, col, r) in enumerate(((1020, 250, "mavi", -0.2), (1500, 180, "kirmizi", 0.25), (1300, 420, "sari", 0.05))):
        draw_butterfly(p, x, y, 1.9, 0.35, rot=r, col=P.COL[col])
    # büyük yazı: renkler
    for i, (w, col) in enumerate((("MAVİ", "mavi"), ("KIRMIZI", "kirmizi"), ("SARI", "sari"))):
        ctx.save()
        ctx.translate(1450, 620 + i * 150)
        ctx.rotate(-0.05 + 0.04 * i)
        text(p, w, 0, 0, 150, P.COL[col], lw=2.0)
        ctx.restore()
    text(p, "Renkli Kelebekler", 1450, 1010, 78, hexrgb("#FFFFFF"), lw=1.5)
    path = save(cv, "_kapak.png")
    im = cv2.imread(path)
    out = os.path.join(OUT, "kapak_bolum1_renkli_kelebekler_1280x720.jpg")
    cv2.imwrite(out, cv2.resize(im, (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    os.remove(path)
    print(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    profil()
    banner()
    filigran()
    yazi_logo()
    kapak_bolum1()
