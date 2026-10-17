"""Dekor: paralaks katmanları halinde çayır dünyası. Her katman bir kez boyanır, karelerde kamera ile kaydırılır."""
import math

import cv2
import numpy as np

from .core import W, H, GROUND_Y, blob, capsule, circle, ellipse, hash01, rounded_rect, smooth_closed, hexrgb
from .characters import PAL, star
from .styles import Canvas, PAINTERS

SPAN = 3600  # kameranın sağa gidebileceği en uzak mesafe (dünya px)
MX, MY = 200, 450


def hills(c, x0, x1, base, amp, seed, bottom=1300, step=220):
    pts = []
    x = x0
    i = 0
    while x <= x1 + step:
        y = base - amp * (0.4 + 0.6 * hash01(seed, i)) * (0.6 + 0.4 * math.sin(i * 1.3 + seed))
        pts.append((x, y))
        x += step * (0.8 + 0.5 * hash01(seed, i, "w"))
        i += 1
    c.new_sub_path()
    c.move_to(x0, bottom)
    c.line_to(*pts[0])
    for a, b in zip(pts, pts[1:]):
        mx = (a[0] + b[0]) / 2
        c.curve_to(mx, a[1], mx, b[1], *b)
    c.line_to(pts[-1][0], bottom)
    c.close_path()


def cloud(p, x, y, s, seed):
    def shape(c):
        for i in range(5):
            cx = x + (i - 2) * 46 * s
            cy = y - (1 - abs(i - 2) / 2.5) * 34 * s
            circle(c, cx, cy, (46 - abs(i - 2) * 8) * s * (0.9 + 0.2 * hash01(seed, i)))
        rounded_rect(c, x - 110 * s, y - 20 * s, 220 * s, 46 * s, 22 * s)

    p.part(shape, (1.0, 1.0, 1.0), seed=f"cl{seed}", line=False, alpha=0.95)
    p.part(lambda c: ellipse(c, x, y + 14 * s, 100 * s, 14 * s), hexrgb("#D9E4F2"), seed=f"clb{seed}", line=False, alpha=0.7)


def tree(p, x, y, s, seed, col=None):
    col = col or hexrgb("#5DA34F")
    p.part(lambda c: capsule(c, x, y, x + 4 * s, y - 120 * s, 13 * s, 9 * s), hexrgb("#9A6A45"), seed=f"tt{seed}", lw=0.7)
    p.part(lambda c: (blob(c, x, y - 170 * s, 78 * s, n=9, wobble=0.12, seed=seed),
                      blob(c, x - 50 * s, y - 130 * s, 50 * s, n=7, wobble=0.12, seed=seed + 1),
                      blob(c, x + 52 * s, y - 128 * s, 52 * s, n=7, wobble=0.12, seed=seed + 2)), col, seed=f"tc{seed}")
    p.part(lambda c: blob(c, x - 22 * s, y - 196 * s, 34 * s, n=7, wobble=0.15, seed=seed + 3),
           tuple(min(1, v * 1.18) for v in col), seed=f"th{seed}", line=False, alpha=0.7)
    for k in range(3):
        fx = x + (hash01(seed, k) - 0.5) * 110 * s
        fy = y - 150 * s + (hash01(seed, k, 1) - 0.5) * 90 * s
        p.part(lambda c, fx=fx, fy=fy: circle(c, fx, fy, 7 * s), hexrgb("#F2665C"), seed=f"tf{seed}{k}", lw=0.5)


def house(p, x, y, s):
    """Umay'ın evi: krem duvar, kırmızı çatı, sarı ışıklı pencere."""
    p.part(lambda c: rounded_rect(c, x - 70 * s, y - 110 * s, 140 * s, 110 * s, 8 * s), hexrgb("#FBEBD0"), seed="hw")
    p.part(lambda c: rounded_rect(c, x + 30 * s, y - 185 * s, 22 * s, 50 * s, 4 * s), hexrgb("#B8574A"), seed="hch")

    def roof(c):
        c.move_to(x - 92 * s, y - 104 * s)
        c.curve_to(x - 60 * s, y - 150 * s, x - 20 * s, y - 182 * s, x, y - 186 * s)
        c.curve_to(x + 20 * s, y - 182 * s, x + 60 * s, y - 150 * s, x + 92 * s, y - 104 * s)
        c.close_path()

    p.part(roof, hexrgb("#E2574C"), seed="hr")
    p.part(lambda c: rounded_rect(c, x - 18 * s, y - 62 * s, 36 * s, 62 * s, 16 * s), hexrgb("#8C5A3C"), seed="hd")
    p.part(lambda c: circle(c, x + 42 * s, y - 64 * s, 17 * s), hexrgb("#FFE08A"), seed="hwin")
    p.part(lambda c: circle(c, x - 44 * s, y - 64 * s, 17 * s), hexrgb("#FFE08A"), seed="hwin2")


def fence(p, x0, x1, y, s):
    def f(c):
        x = x0
        while x <= x1:
            rounded_rect(c, x, y - 60 * s, 12 * s, 60 * s, 5 * s)
            x += 46 * s
        rounded_rect(c, x0 - 6, y - 46 * s, x1 - x0 + 24 * s, 9 * s, 4 * s)
        rounded_rect(c, x0 - 6, y - 24 * s, x1 - x0 + 24 * s, 9 * s, 4 * s)

    p.part(f, hexrgb("#F4E2C6"), seed=f"fn{x0}", lw=0.7)


def tiny_flower(p, x, y, s, col, seed):
    def f(c):
        for i in range(5):
            a = i * 2 * math.pi / 5 + hash01(seed) * 3
            circle(c, x + math.cos(a) * 6 * s, y + math.sin(a) * 6 * s, 5 * s)

    p.part(f, col, seed=f"tf{seed}", lw=0.45)
    p.part(lambda c: circle(c, x, y, 3.5 * s), hexrgb("#FFE36E"), seed=f"tfc{seed}", line=False)


def grass_tuft(p, x, y, s, seed, col=None):
    col = col or hexrgb("#5CA54A")

    def f(c):
        for i in range(5):
            a = (i - 2) * 0.32 + (hash01(seed, i) - 0.5) * 0.3
            h = (60 + 40 * hash01(seed, i, "h")) * s
            bx = x + (i - 2) * 9 * s
            tx, ty = bx + math.sin(a) * h, y - math.cos(a) * h
            c.new_sub_path()
            c.move_to(bx - 7 * s, y)
            c.curve_to(bx - 4 * s, y - h * 0.5, tx - 2 * s, ty + h * 0.2, tx, ty)
            c.curve_to(tx + 2 * s, ty + h * 0.2, bx + 4 * s, y - h * 0.5, bx + 7 * s, y)
            c.close_path()

    p.part(f, col, seed=f"gt{seed}", lw=0.7)


LAYERS = [  # ad, paralaks
    ("sky", 0.10),
    ("clouds", 0.18),
    ("far", 0.35),
    ("mid", 0.62),
    ("ground", 1.0),
    ("front", 1.3),
]


def layer_size(par):
    return int(W + SPAN * par + 2 * MX), 1750


def paint_layer(name, par, style):
    lw_, lh = layer_size(par)
    cv = Canvas(lw_, lh)
    p = PAINTERS[style](cv, t=0.0, scale=1.0, frame=0)
    if style in ("kagit", "kece"):
        p.jitter = False
    ctx = p.ctx
    ctx.translate(MX, MY)
    x1 = lw_ - MX
    if name == "sky":
        top, hor = hexrgb("#8EC5EC"), hexrgb("#FFF1DA")
        p.part(lambda c: c.rectangle(-MX, -MY, lw_, lh), None, grad=(top, hor, 0, MY + 900), line=False, wet=1.6, flat=True, seed="sky")
        sx, sy = 1500, 175
        p.glow(sx, sy, 300, hexrgb("#FFF3C4"), 0.9)
        p.part(lambda c: circle(c, sx, sy, 78), hexrgb("#FFD45C"), seed="sun", lw=0.6)
        if style == "kagit":
            for i in range(12):
                a = i * math.pi / 6
                p.part(lambda c, a=a: ellipse(c, sx + math.cos(a) * 118, sy + math.sin(a) * 118, 22, 9, a), hexrgb("#FFC94A"), seed=f"ray{i}")
    elif name == "clouds":
        for i in range(9):
            cx = -100 + i * (lw_ / 8.5) + hash01(i, "cx") * 120
            cy = 90 + hash01(i, "cy") * 230
            cloud(p, cx, cy, 0.8 + 0.6 * hash01(i, "cs"), i)
    elif name == "far":
        p.part(lambda c: hills(c, -MX, x1, 660, 150, 3, step=320), hexrgb("#9CC3C6"), seed="far1", line=False, flat=True, wet=1.3)
        p.part(lambda c: hills(c, -MX, x1, 700, 110, 7, step=260), hexrgb("#8FBF9C"), seed="far2", line=False, flat=True, wet=1.3)
    elif name == "mid":
        p.part(lambda c: hills(c, -MX, x1, 770, 120, 11, step=420), hexrgb("#8CC66A"), seed="mid1", flat=True, lw=0.6)
        house(p, 420, 690, 0.85)
        fence(p, 540, 760, 712, 0.6)
        for i in range(10):
            tx = 900 + i * 330 + hash01(i, "tx") * 160
            tree(p, tx, 700 + hash01(i, "ty") * 40, 0.55 + 0.25 * hash01(i, "ts"), 100 + i,
                 col=hexrgb("#4F9A4C") if i % 2 else hexrgb("#6AAE54"))
    elif name == "ground":
        p.part(lambda c: hills(c, -MX, x1, 800, 22, 19, step=500), None,
               grad=(hexrgb("#A6D879"), hexrgb("#6FB257"), MY + 790, MY + 1250), seed="gr", flat=True, lw=0.6)

        def road(c):
            c.new_sub_path()
            c.move_to(-MX, 852)
            xs = list(range(-MX, x1 + 300, 300))
            for a, b in zip(xs, xs[1:]):
                c.curve_to(a + 150, 846 + 8 * math.sin(a * 0.01), b - 150, 846 + 8 * math.sin(b * 0.01), b, 850 + 6 * math.sin(b * 0.013))
            c.line_to(xs[-1], 915)
            for a, b in zip(reversed(xs[1:]), reversed(xs[:-1])):
                c.curve_to(a - 150, 918 + 6 * math.sin(a * 0.017), b + 150, 918 + 6 * math.sin(b * 0.017), b, 915 + 5 * math.sin(b * 0.02))
            c.close_path()

        p.part(road, hexrgb("#F2DFB0"), seed="road", lw=0.5, wet=1.2)
        tree(p, 120, 800, 1.25, 7, col=hexrgb("#57A04B"))
        tree(p, 2380, 805, 1.1, 8, col=hexrgb("#62A851"))
        tree(p, 4300, 805, 1.2, 9, col=hexrgb("#57A04B"))
        cols = [hexrgb("#F2665C"), hexrgb("#FFFFFF"), hexrgb("#7FA8F0"), hexrgb("#F8A6C8"), hexrgb("#FFD24D")]
        rng = np.random.default_rng(5)
        for i in range(260):
            fx = -MX + rng.random() * (lw_)
            fy = 812 + rng.random() * 430
            if 840 < fy < 930:
                continue
            tiny_flower(p, fx, fy, 0.6 + 0.6 * (fy - 800) / 450, cols[i % len(cols)], 1000 + i)
        for i in range(70):
            gx = -MX + rng.random() * lw_
            gy = 800 + rng.random() * 40
            grass_tuft(p, gx, gy, 0.35, 2000 + i, col=hexrgb("#73B95A"))
    elif name == "front":
        rng = np.random.default_rng(9)
        x = -MX
        i = 0
        while x < x1:
            grass_tuft(p, x, 1110 + rng.random() * 30, 1.5 + rng.random() * 0.6, 3000 + i, col=hexrgb("#4E9E45"))
            if i % 3 == 1:
                p.part(lambda c, x=x: blob(c, x + 80, 1110, 70, n=9, wobble=0.15, seed=i, sy=0.7), hexrgb("#5BAA4E"), seed=f"bush{i}")
                tiny_flower(p, x + 60, 1070, 1.6, hexrgb("#F2665C"), 4000 + i)
                tiny_flower(p, x + 110, 1085, 1.5, hexrgb("#FFFFFF"), 4100 + i)
            x += 380 + rng.random() * 380
            i += 1
    cv.surface.flush()
    return cv.arr.copy()


def build_layers(style, cache_dir=None):
    out = []
    for name, par in LAYERS:
        img = None
        path = None
        if cache_dir:
            import os
            path = os.path.join(cache_dir, f"layer_{style}_{name}.png")
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            img = paint_layer(name, par, style)
            if path:
                cv2.imwrite(path, img)
        out.append({"name": name, "p": par, "img": img})
    return out


def layer_matrix(par, cam, drift=0.0):
    cx, cy, z = cam
    zl = 1 + (z - 1) * min(par, 1.0) if par <= 1 else z * (1 + (par - 1) * 0.15)
    dx, dy = cx - W / 2, cy - H / 2
    tx = W / 2 - zl * (MX + W / 2 + dx * par - drift)
    ty = H / 2 - zl * (MY + H / 2 + dy * par)
    return np.array([[zl, 0, tx], [0, zl, ty]], np.float32), zl
