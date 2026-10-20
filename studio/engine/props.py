"""1. bölüm (Renkli Kelebekler) için sahne nesneleri: ev, dere, göl, kuş, top, elma ağacı, uğur böceği, çilek,
ayçiçeği, civciv, piknik/limon, gökkuşağı ve ekran yazıları. Hepsi Painter.part diliyle çizilir."""
import math

import cairo

from .core import capsule, ellipse, circle, blob, rounded_rect, hash01, hexrgb, clamp, ease_out_back
from .characters import PAL, star, lighten_c, darken_c

COL = {
    "mavi": hexrgb("#3E7FE0"), "mavi_l": hexrgb("#8DB8F2"),
    "kirmizi": hexrgb("#E2383F"), "kirmizi_l": hexrgb("#F57F7A"),
    "sari": hexrgb("#FFC928"), "sari_l": hexrgb("#FFE58A"),
    "yesil": hexrgb("#5FAE4E"), "yesil_k": hexrgb("#3F8A3B"), "kahve": hexrgb("#9A6A45"),
    "krem": hexrgb("#FBEBD0"), "turuncu": hexrgb("#F7962F"), "mor": hexrgb("#9B6BD3"),
    "siyah": hexrgb("#2A1E1E"), "beyaz": (1.0, 1.0, 1.0),
}
WORD = {"mavi": "MAVİ", "kirmizi": "KIRMIZI", "sari": "SARI"}


# ---------------------------------------------------------------- AÇILIŞ: büyük ev
def big_house(p, x, y, s, door=0.0, grandma=0.0, t=0.0):
    W_, H_ = 300 * s, 250 * s
    p.part(lambda c: rounded_rect(c, x - W_ / 2, y - H_, W_, H_, 14 * s), COL["krem"], seed="bh_wall")
    p.part(lambda c: rounded_rect(c, x + 70 * s, y - H_ - 120 * s, 34 * s, 80 * s, 6 * s), hexrgb("#B8574A"), seed="bh_ch")

    def roof(c):
        c.move_to(x - W_ / 2 - 36 * s, y - H_ + 10 * s)
        c.curve_to(x - 100 * s, y - H_ - 70 * s, x - 40 * s, y - H_ - 135 * s, x, y - H_ - 140 * s)
        c.curve_to(x + 40 * s, y - H_ - 135 * s, x + 100 * s, y - H_ - 70 * s, x + W_ / 2 + 36 * s, y - H_ + 10 * s)
        c.close_path()

    p.part(roof, COL["kirmizi"], seed="bh_roof")
    # kapı (menteşe solda; açılınca panel daralır)
    dx, dy, dw, dh = x - 55 * s, y - 165 * s, 90 * s, 165 * s
    p.part(lambda c: rounded_rect(c, dx, dy, dw, dh, 40 * s), hexrgb("#5A3A28"), seed="bh_doorin")
    pw = dw * max(0.12, 1 - door)
    p.part(lambda c: rounded_rect(c, dx, dy, pw, dh, min(40 * s, pw / 2)), hexrgb("#8C5A3C"), seed="bh_door")
    if door < 0.5:
        p.part(lambda c: circle(c, dx + pw - 16 * s, dy + 90 * s, 7 * s), COL["sari"], seed="bh_knob")
    # pencere + anneanne
    wx, wy, wr = x + 85 * s, y - 165 * s, 44 * s
    p.part(lambda c: circle(c, wx, wy, wr + 8 * s), hexrgb("#8C5A3C"), seed="bh_wfr")
    p.part(lambda c: circle(c, wx, wy, wr), hexrgb("#FFE6A8"), seed="bh_win")
    if grandma > 0:
        gy = wy + (1 - grandma) * 60 * s
        p.part(lambda c: circle(c, wx, gy + 4 * s, 24 * s), PAL["skin"], seed="gm_face")
        p.part(lambda c: (circle(c, wx, gy - 26 * s, 13 * s), ellipse(c, wx, gy - 12 * s, 26 * s, 14 * s)), hexrgb("#D8D4D0"), seed="gm_hair")
        p.stroke(lambda c: (c.new_sub_path(), c.arc(wx - 9 * s, gy + 2 * s, 7 * s, 0, 6.28), c.new_sub_path(), c.arc(wx + 9 * s, gy + 2 * s, 7 * s, 0, 6.28)),
                 hexrgb("#6B4A3A"), width=2.2)
        p.stroke(lambda c: (c.move_to(wx - 8 * s, gy + 14 * s), c.curve_to(wx - 3 * s, gy + 20 * s, wx + 3 * s, gy + 20 * s, wx + 8 * s, gy + 14 * s)),
                 PAL["mouth"], width=2.6)
        hx = wx + 30 * s + math.sin(t * 7) * 8 * s
        p.part(lambda c: circle(c, hx, gy - 2 * s, 9 * s), PAL["skin"], seed="gm_hand")
    p.part(lambda c: circle(c, x - 100 * s, wy, 30 * s), hexrgb("#FFE6A8"), seed="bh_win2")
    for i, cc in enumerate((COL["mavi"], COL["kirmizi"], COL["sari"])):
        fx = x - 140 * s + i * 30 * s
        p.part(lambda c, fx=fx: rounded_rect(c, fx - 12 * s, y - 26 * s, 24 * s, 26 * s, 4 * s), hexrgb("#C9784A"), seed=f"bh_pot{i}")
        p.part(lambda c, fx=fx: blob(c, fx, y - 36 * s, 13 * s, n=6, seed=i), cc, seed=f"bh_pf{i}")


# ---------------------------------------------------------------- MAVİ
def stream(p, x0, x1, y, t, w=80):
    def band(c, off=0.0, ww=w):
        n = 24
        c.new_sub_path()
        for k in range(n + 1):
            xx = x0 + (x1 - x0) * k / n
            yy = y - ww / 2 + 7 * math.sin(xx * 0.012 + t * 1.5 + off)
            (c.move_to if k == 0 else c.line_to)(xx, yy)
        for k in range(n, -1, -1):
            xx = x0 + (x1 - x0) * k / n
            c.line_to(xx, y + ww / 2 + 6 * math.sin(xx * 0.014 - t * 1.2 + off))
        c.close_path()

    p.part(lambda c: band(c), COL["mavi"], seed="st_band", flat=True)
    p.part(lambda c: band(c, 1.0, w * 0.55), COL["mavi_l"], alpha=0.7, seed="st_band2", line=False, flat=True)
    for k in range(9):
        u = ((t * 0.12 + k / 9) % 1.0)
        rx = x0 + (x1 - x0) * u
        ry = y + (hash01(k) - 0.5) * w * 0.5
        p.part(lambda c, rx=rx, ry=ry: ellipse(c, rx, ry, 22, 4), COL["beyaz"], alpha=0.75, seed=f"st_r{k}", line=False)


def lake(p, cx, cy, rx, ry, t):
    """Masmavi küçük göl: çimenli kıyı, kumlu kenar, derinleşen su, gökyüzü yansıması, nilüferler, sazlar."""
    def shore(c, k, wob=0.04):
        c.new_sub_path()
        n = 40
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            r = 1 + wob * math.sin(3 * a + 0.7) + wob * 0.6 * math.sin(5 * a + 2.1)
            (c.move_to if i == 0 else c.line_to)(cx + math.cos(a) * rx * k * r, cy + math.sin(a) * ry * k * r)
        c.close_path()

    p.part(lambda c: shore(c, 1.10), hexrgb("#7CC062"), seed="lk_grass", lw=0.6)
    p.part(lambda c: shore(c, 1.03), hexrgb("#E9D3A0"), seed="lk_sand", lw=0.5)
    p.part(lambda c: shore(c, 0.96), None, grad=(hexrgb("#5FA8F0"), hexrgb("#2F6FD0"), cy - ry, cy + ry),
           seed="lk_water", lw=0.6)
    p.part(lambda c: ellipse(c, cx - rx * 0.12, cy - ry * 0.12, rx * 0.62, ry * 0.42), hexrgb("#9FD0FA"), alpha=0.55,
           seed="lk_sky", line=False, flat=True)
    # parıltılar ve halkalar
    for k in range(6):
        u = (t * 0.25 + k / 6) % 1.0
        hx = cx + (hash01(k, "lx") - 0.5) * rx * 1.2
        hy = cy + (hash01(k, "ly") - 0.5) * ry * 0.9
        a = math.sin(math.pi * u)
        p.part(lambda c, hx=hx, hy=hy, u=u: ellipse(c, hx, hy, 14 + 30 * u, 3 + 6 * u), COL["beyaz"], alpha=0.55 * a,
               seed=f"lk_r{k}", line=False)
    # nilüfer yaprakları
    for k, (dx, dy, r) in enumerate([(0.42, 0.18, 26), (0.55, -0.22, 20), (-0.5, 0.25, 22)]):
        lx, ly = cx + dx * rx, cy + dy * ry + 2 * math.sin(t * 1.1 + k)

        def pad(c, lx=lx, ly=ly, r=r):
            c.new_sub_path()
            c.move_to(lx, ly)
            c.arc(lx, ly, r, 0.35, 2 * math.pi - 0.1)
            c.close_path()

        p.ctx.save()
        p.ctx.translate(lx, ly)
        p.ctx.scale(1, 0.42)
        p.ctx.translate(-lx, -ly)
        p.part(pad, hexrgb("#4E9E45"), seed=f"lk_pad{k}", lw=0.5)
        p.ctx.restore()
    # sazlar (iki yanda)
    for side, bx in ((-1, cx - rx * 0.98), (1, cx + rx * 0.97)):
        for j in range(4):
            sx = bx + side * j * 14
            h = 70 + 22 * hash01(side, j)
            sw = 4 * math.sin(t * 1.3 + j + side)
            p.part(lambda c, sx=sx, h=h, sw=sw: capsule(c, sx, cy, sx + sw, cy - h, 3.5, 2), hexrgb("#4F9A44"),
                   seed=f"lk_reed{side}{j}", lw=0.4)
            if j % 2 == 0:
                p.part(lambda c, sx=sx, h=h, sw=sw: capsule(c, sx + sw, cy - h + 6, sx + sw, cy - h + 30, 6, 6), COL["kahve"],
                       seed=f"lk_cat{side}{j}", lw=0.4)
    # kıyı taşları
    for k, (dx, r) in enumerate([(-0.75, 16), (-0.62, 11), (0.7, 14), (0.15, 12)]):
        sx, sy = cx + dx * rx, cy + ry * 0.98 * math.sqrt(max(0.0, 1 - dx * dx))
        p.part(lambda c, sx=sx, sy=sy, r=r: ellipse(c, sx, sy, r, r * 0.6), hexrgb("#B7AFA4"), seed=f"lk_st{k}", lw=0.5)


def splash(p, x, y, u, seed=0):
    if not (0 < u < 1):
        return
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.32
        d = 20 + 90 * u
        dx, dy = math.cos(a) * d, math.sin(a) * d + 160 * u * u
        p.part(lambda c, dx=dx, dy=dy: ellipse(c, x + dx, y + dy, 8 * (1 - u * 0.5), 11 * (1 - u * 0.5)), COL["mavi_l"],
               alpha=1 - u, seed=f"spl{seed}{k}", lw=0.5)


def bird(p, x, y, s, t, sing=0.0, col=None, facing=-1):
    col = col or COL["mavi"]
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y - abs(math.sin(t * 2.0)) * 3 * s)
    ctx.scale(s * facing, s)
    p.part(lambda c: (c.move_to(-30, -20), c.line_to(-62, -34), c.line_to(-58, -14), c.close_path()), darken_c(col, 0.15), seed="bd_tail")
    p.part(lambda c: ellipse(c, 0, -28, 36, 30), col, seed="bd_body")
    p.part(lambda c: ellipse(c, 6, -20, 22, 18), lighten_c(col, 0.55), seed="bd_belly", line=False)
    wing = 0.25 * math.sin(t * 9) * sing
    ctx.save()
    ctx.translate(-8, -30)
    ctx.rotate(wing - 0.25)
    p.part(lambda c: ellipse(c, -8, 2, 22, 13, 0.4), darken_c(col, 0.2), seed="bd_wing")
    ctx.restore()
    p.part(lambda c: circle(c, 22, -56, 22), col, seed="bd_head")
    p.part(lambda c: circle(c, 30, -60, 5.5), PAL["eye"], seed="bd_eye", line=False)
    p.part(lambda c: circle(c, 31.5, -62, 2), COL["beyaz"], seed="bd_eyeh", line=False)
    op = (0.5 + 0.5 * math.sin(t * 14)) * sing
    p.part(lambda c: (c.move_to(40, -58 - op * 3), c.line_to(58, -54), c.line_to(40, -50 + op * 3), c.close_path()), COL["turuncu"], seed="bd_beak")
    for k in (-1, 1):
        p.stroke(lambda c, k=k: (c.move_to(k * 8, -2), c.line_to(k * 8, 6)), COL["turuncu"], width=3)
    ctx.restore()


def music_notes(p, x, y, t, seed=0):
    for k in range(3):
        u = ((t * 0.5 + k / 3) % 1.0)
        nx, ny = x + 20 + u * 70 + 12 * math.sin(u * 8 + k), y - 40 - u * 110
        a = math.sin(math.pi * u)
        p.part(lambda c, nx=nx, ny=ny: (ellipse(c, nx, ny, 9, 7, -0.4), rounded_rect(c, nx + 6, ny - 34, 4, 34, 2)),
               COL["siyah"], alpha=a, seed=f"note{seed}{k}", lw=0.4)


def branch(p, x0, y0, x1, y1):
    p.part(lambda c: capsule(c, x0, y0, x1, y1, 9, 6), COL["kahve"], seed=f"br{x0}")
    p.part(lambda c: (ellipse(c, (x0 + x1) / 2, y1 - 14, 20, 9, -0.5), ellipse(c, x1 - 10, y1 - 8, 16, 8, 0.4)), COL["yesil"], seed=f"brl{x0}")


def ball(p, x, y, r, rot=0.0, col=None):
    col = col or COL["mavi"]
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y - r)
    ctx.rotate(rot)
    p.part(lambda c: circle(c, 0, 0, r), col, seed="ball")
    p.part(lambda c: (ellipse(c, 0, 0, r * 0.98, r * 0.28)), COL["beyaz"], seed="ball_s", line=False)
    p.part(lambda c: star(c, 0, -r * 0.55, r * 0.22), COL["sari"], seed="ball_st", line=False)
    ctx.restore()


def bush(p, x, y, s, seed=0, col=None):
    col = col or COL["yesil"]
    p.part(lambda c: (blob(c, x, y - 40 * s, 70 * s, n=9, wobble=0.15, seed=seed, sy=0.7),
                      blob(c, x - 60 * s, y - 25 * s, 45 * s, n=7, seed=seed + 1), blob(c, x + 60 * s, y - 25 * s, 48 * s, n=7, seed=seed + 2)),
           col, seed=f"bush{seed}")


# ---------------------------------------------------------------- KIRMIZI
def apple(p, x, y, r, seed="ap"):
    p.part(lambda c: (circle(c, x - r * 0.35, y, r * 0.75), circle(c, x + r * 0.35, y, r * 0.75), circle(c, x, y + r * 0.15, r * 0.8)),
           COL["kirmizi"], seed=f"{seed}b")
    p.part(lambda c: ellipse(c, x - r * 0.35, y - r * 0.25, r * 0.22, r * 0.14, -0.6), COL["beyaz"], alpha=0.7, seed=f"{seed}h", line=False)
    p.part(lambda c: capsule(c, x, y - r * 0.6, x + r * 0.1, y - r * 1.05, 2.5, 2), COL["kahve"], seed=f"{seed}s", line=False)
    p.part(lambda c: ellipse(c, x + r * 0.35, y - r * 0.95, r * 0.32, r * 0.14, -0.4), COL["yesil"], seed=f"{seed}l")


def apple_tree(p, x, y, s, apples):
    """apples: [(dx, dy, r)] — ağaca göre konumlar."""
    p.part(lambda c: capsule(c, x, y, x + 6 * s, y - 210 * s, 24 * s, 16 * s), COL["kahve"], seed="at_tr")
    p.part(lambda c: (blob(c, x, y - 300 * s, 140 * s, n=10, wobble=0.12, seed=4),
                      blob(c, x - 110 * s, y - 230 * s, 90 * s, n=8, seed=5), blob(c, x + 115 * s, y - 225 * s, 95 * s, n=8, seed=6)),
           hexrgb("#5DA34F"), seed="at_cr")
    for i, (dx, dy, r) in enumerate(apples):
        apple(p, x + dx * s, y + dy * s, r * s, seed=f"ta{i}")


def ladybug(p, x, y, s, t, glow=-1, walk=0.0):
    p.part(lambda c: (c.move_to(x - 170 * s, y), c.curve_to(x - 90 * s, y - 120 * s, x + 110 * s, y - 110 * s, x + 170 * s, y),
                      c.curve_to(x + 90 * s, y + 40 * s, x - 90 * s, y + 40 * s, x - 170 * s, y), c.close_path()), COL["yesil"], seed="lb_leaf")
    p.stroke(lambda c: (c.move_to(x - 150 * s, y), c.curve_to(x - 40 * s, y - 30 * s, x + 60 * s, y - 30 * s, x + 160 * s, y)),
             COL["yesil_k"], width=3)
    bx = x - 20 * s + walk
    by = y - 45 * s
    for k in range(3):
        for side in (-1, 1):
            lx = bx - 30 * s + k * 30 * s
            ph = math.sin(t * 10 + k + side) * 4 * s * (walk != 0)
            p.stroke(lambda c, lx=lx, side=side, ph=ph: (c.move_to(lx, by + side * 10 * s), c.line_to(lx + ph, by + side * 46 * s)), COL["siyah"], width=3)
    p.part(lambda c: ellipse(c, bx + 62 * s, by, 26 * s, 24 * s), COL["siyah"], seed="lb_head")
    p.part(lambda c: (circle(c, bx + 72 * s, by - 10 * s, 6 * s), circle(c, bx + 72 * s, by + 10 * s, 6 * s)), COL["beyaz"], seed="lb_eye", line=False)
    p.part(lambda c: ellipse(c, bx, by, 64 * s, 52 * s), COL["kirmizi"], seed="lb_body")
    p.stroke(lambda c: (c.move_to(bx + 50 * s, by), c.line_to(bx - 64 * s, by)), COL["siyah"], width=3.5)
    spots = [(-28, -24), (14, -26), (-28, 24), (14, 26)]
    for i, (sx, sy) in enumerate(spots):
        if i == glow:
            p.glow(bx + sx * s, by + sy * s, 34 * s, COL["sari_l"], 0.9)
        p.part(lambda c, sx=sx, sy=sy: circle(c, bx + sx * s, by + sy * s, 11 * s), COL["siyah"], seed=f"lb_sp{i}", line=False)


def strawberry(p, x, y, s, rot=0.0, seed="sb"):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    p.part(lambda c: (c.move_to(0, 30), c.curve_to(-34, 10, -30, -22, 0, -20), c.curve_to(30, -22, 34, 10, 0, 30), c.close_path()),
           COL["kirmizi"], seed=f"{seed}b")
    for k in range(6):
        p.part(lambda c, k=k: ellipse(c, -12 + (k % 3) * 12, -6 + (k // 3) * 14, 2, 3), COL["sari_l"], seed=f"{seed}d{k}", line=False)
    p.part(lambda c: star(c, 0, -22, 14, n=5, inner=0.4), COL["yesil"], seed=f"{seed}c")
    ctx.restore()


def strawberry_patch(p, x, y, s, t):
    for k in range(4):
        p.part(lambda c, k=k: ellipse(c, x - 90 * s + k * 60 * s, y - 20 * s, 42 * s, 22 * s, (k - 1.5) * 0.4), COL["yesil"], seed=f"sbl{k}")
    for k, (dx, dy) in enumerate([(-80, -10), (-30, 0), (20, -14), (70, -4), (115, -12)]):
        strawberry(p, x + dx * s, y + dy * s, s * 0.9, rot=math.sin(t * 1.2 + k) * 0.05, seed=f"sb{k}")


# ---------------------------------------------------------------- SARI
def sunflower(p, x, y, s, t, h=330):
    sway = math.sin(t * 1.1) * 0.03
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(sway)
    p.part(lambda c: capsule(c, 0, 0, 0, -h * s, 9 * s, 7 * s), COL["yesil_k"], seed="sf_st")
    p.part(lambda c: (ellipse(c, -40 * s, -h * 0.45 * s, 46 * s, 18 * s, 0.5), ellipse(c, 42 * s, -h * 0.62 * s, 46 * s, 18 * s, -0.5)),
           COL["yesil"], seed="sf_lv")
    hy = -h * s
    for i in range(16):
        a = i * math.pi / 8 + t * 0.1
        p.part(lambda c, a=a: ellipse(c, math.cos(a) * 62 * s, hy + math.sin(a) * 62 * s, 34 * s, 15 * s, a), COL["sari"], seed=f"sf_p{i}")
    p.part(lambda c: circle(c, 0, hy, 46 * s), hexrgb("#7A4A2A"), seed="sf_c")
    for i in range(10):
        a = i * 2.4
        rr = 30 * s * math.sqrt((i + 1) / 10)
        p.part(lambda c, a=a, rr=rr: circle(c, math.cos(a) * rr, hy + math.sin(a) * rr, 4 * s), hexrgb("#4E2E1A"), seed=f"sf_d{i}", line=False)
    ctx.restore()


def chick(p, x, y, s, t, peep=0.0, hop=0.0, facing=-1):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y - hop)
    ctx.scale(s * facing, s)
    for k in (-1, 1):
        p.stroke(lambda c, k=k: (c.move_to(k * 10, -6), c.line_to(k * 10, 0), c.line_to(k * 10 + 8, 0)), COL["turuncu"], width=4)
    p.part(lambda c: ellipse(c, 0, -32, 34, 30), COL["sari"], seed="ck_body")
    p.part(lambda c: ellipse(c, -10, -30, 16, 11, 0.5 + 0.3 * math.sin(t * 12) * peep), darken_c(COL["sari"], 0.1), seed="ck_wing")
    p.part(lambda c: circle(c, 14, -66, 22), COL["sari"], seed="ck_head")
    p.part(lambda c: (ellipse(c, 10, -90, 4, 9, -0.3), ellipse(c, 17, -90, 4, 9, 0.3)), COL["sari"], seed="ck_tuft")
    p.part(lambda c: circle(c, 22, -70, 4.5), PAL["eye"], seed="ck_eye", line=False)
    op = (0.5 + 0.5 * math.sin(t * 16)) * peep
    p.part(lambda c: (c.move_to(34, -66 - op * 3), c.line_to(48, -62), c.line_to(34, -58 + op * 3), c.close_path()), COL["turuncu"], seed="ck_beak")
    p.part(lambda c: ellipse(c, 22, -58, 6, 4), PAL["cheek"], alpha=0.6, seed="ck_ch", line=False)
    ctx.restore()


def lemon(p, x, y, s, rot=0.0, seed="lm"):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    p.part(lambda c: (ellipse(c, 0, 0, 34, 24), ellipse(c, -34, 0, 7, 5), ellipse(c, 34, 0, 7, 5)), COL["sari"], seed=f"{seed}b")
    p.part(lambda c: ellipse(c, -10, -9, 12, 5, -0.2), COL["beyaz"], alpha=0.7, seed=f"{seed}h", line=False)
    p.part(lambda c: ellipse(c, 26, -24, 14, 6, -0.6), COL["yesil"], seed=f"{seed}l")
    ctx.restore()


def picnic(p, x, y, s, lemons=2):
    def cloth(c):
        c.move_to(x - 200 * s, y + 20 * s)
        c.line_to(x - 150 * s, y - 40 * s)
        c.line_to(x + 160 * s, y - 40 * s)
        c.line_to(x + 210 * s, y + 20 * s)
        c.close_path()

    p.part(cloth, hexrgb("#F4EEDF"), seed="pc_cl", flat=True)
    for k in range(5):
        xx = x - 150 * s + k * 78 * s
        p.part(lambda c, xx=xx: (c.move_to(xx - 6 * s, y - 40 * s), c.line_to(xx + 6 * s, y - 40 * s),
                                 c.line_to(xx + 18 * s, y + 20 * s), c.line_to(xx + 4 * s, y + 20 * s), c.close_path()),
               hexrgb("#BFE0B0"), seed=f"pc_st{k}", line=False, flat=True)
    bx, by = x + 40 * s, y - 20 * s
    p.stroke(lambda c: (c.new_sub_path(), c.arc_negative(bx, by - 50 * s, 55 * s, 0, math.pi)), hexrgb("#8C5A3C"), width=7)
    p.part(lambda c: rounded_rect(c, bx - 70 * s, by - 55 * s, 140 * s, 70 * s, 14 * s), hexrgb("#C98B53"), seed="pc_bs")
    for k in range(3):
        p.stroke(lambda c, k=k: (c.move_to(bx - 64 * s, by - 35 * s + k * 18 * s), c.line_to(bx + 64 * s, by - 35 * s + k * 18 * s)),
                 hexrgb("#9A6A45"), width=2.5)
    for k in range(lemons):
        lemon(p, bx - 30 * s + k * 50 * s, by - 62 * s, 0.9 * s, rot=(k - 0.5) * 0.4, seed=f"pl{k}")


# ---------------------------------------------------------------- FİNAL
RAINBOW = [hexrgb("#E2383F"), hexrgb("#F7962F"), hexrgb("#FFC928"), hexrgb("#5FAE4E"), hexrgb("#3E7FE0"), hexrgb("#9B6BD3")]


def rainbow(p, cx, by, R, prog, band=34):
    prog = clamp(prog)
    if prog <= 0:
        return
    a1 = math.pi + math.pi * prog
    for i, col in enumerate(RAINBOW):
        r0 = R - i * band
        r1 = r0 - band

        def arcband(c, r0=r0, r1=r1):
            c.new_sub_path()
            c.arc(cx, by, r0, math.pi, a1)
            c.arc_negative(cx, by, r1, a1, math.pi)
            c.close_path()

        p.part(arcband, col, seed=f"rb{i}")
    for side in (-1, 1):
        if side == 1 and prog < 1:
            continue
        p.part(lambda c, side=side: (blob(c, cx + side * (R - band * 3), by, 70, n=9, seed=side + 3, sy=0.6)), COL["beyaz"], seed=f"rbc{side}")


# ---------------------------------------------------------------- ekran yazıları
def draw_word(p, word, col, alpha, pop, x, y, size=190):
    if alpha <= 0.01:
        return
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(pop, pop)
    ctx.select_font_face("Baloo 2", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(word)
    x0 = -ext.width / 2 - ext.x_bearing
    y0 = -ext.height / 2 - ext.y_bearing
    pad = 40
    p.part(lambda c: rounded_rect(c, -ext.width / 2 - pad, -ext.height / 2 - pad * 0.7, ext.width + 2 * pad, ext.height + pad * 1.4, 50),
           COL["beyaz"], alpha=alpha * 0.92, seed=f"wbg{word}")

    def tp(c):
        c.move_to(x0, y0)
        c.text_path(word)

    p.part(tp, col, alpha=alpha, seed=f"w{word}", lw=1.4)
    ctx.restore()


def draw_badge(p, key, alpha):
    if alpha <= 0.01:
        return
    col = COL[key]
    ctx = p.ctx
    ctx.save()
    ctx.translate(150, 120)
    p.part(lambda c: circle(c, 0, 0, 62), col, alpha=alpha, seed="bdg_c")
    ctx.select_font_face("Baloo 2", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(30 if len(WORD[key]) > 4 else 36)
    ext = ctx.text_extents(WORD[key])

    def tp(c):
        c.move_to(-ext.width / 2 - ext.x_bearing, -ext.height / 2 - ext.y_bearing)
        c.text_path(WORD[key])

    p.part(tp, COL["beyaz"], alpha=alpha, seed="bdg_t", line=False)
    ctx.restore()
