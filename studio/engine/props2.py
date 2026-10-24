"""2. bölüm (Şekil Avı) sahne nesneleri: şekil kutusu ve parçaları, kurabiyeler, el arabası, şekil evi (kare pencere,
üçgen çatı), hediye kutusu ve kemik, kareli piknik örtüsü, kâğıt gemi, karpuz dilimi, üçgen flamalar, şekil çerçeveleri.
Hepsi Painter.part diliyle çizilir (her stil kendi yöntemiyle boyar)."""
import math

from .core import capsule, ellipse, circle, rounded_rect, hexrgb, clamp, ease_out_back
from .characters import lighten_c, darken_c
from .props import COL

# şekil → parça rengi (her şekil hep aynı renkte: çocuk şekli renkle karıştırmasın diye tek renk)
SHAPE_COL = {"daire": COL["sari"], "kare": COL["mavi"], "ucgen": COL["kirmizi"]}
SHAPE_WORD = {"daire": "DAİRE", "kare": "KARE", "ucgen": "ÜÇGEN"}


def shape_path(c, kind, x, y, r, rot=0.0):
    """r: şeklin 'yarıçapı' (kare için yarım kenar, üçgen için çevrel çember yarıçapı)."""
    c.new_sub_path()
    if kind == "daire":
        c.arc(x, y, r, 0, 2 * math.pi)
        c.close_path()
        return
    n = 4 if kind == "kare" else 3
    a0 = (math.pi / 4 if kind == "kare" else -math.pi / 2) + rot
    rr = r * (math.sqrt(2) if kind == "kare" else 1.15)
    # hafif yuvarlatılmış köşeler (çocuk oyuncağı gibi)
    pts = [(x + math.cos(a0 + 2 * math.pi * k / n) * rr, y + math.sin(a0 + 2 * math.pi * k / n) * rr + (r * 0.18 if n == 3 else 0))
           for k in range(n)]
    cr = r * 0.16
    for k in range(n):
        p0, p1, p2 = pts[k - 1], pts[k], pts[(k + 1) % n]
        ax, ay = p1[0] + (p0[0] - p1[0]) * cr / math.dist(p0, p1) * 2, p1[1] + (p0[1] - p1[1]) * cr / math.dist(p0, p1) * 2
        bx, by = p1[0] + (p2[0] - p1[0]) * cr / math.dist(p2, p1) * 2, p1[1] + (p2[1] - p1[1]) * cr / math.dist(p2, p1) * 2
        if k == 0:
            c.move_to(ax, ay)
        else:
            c.line_to(ax, ay)
        c.curve_to(p1[0], p1[1], p1[0], p1[1], bx, by)
    c.close_path()


def shape_vertices(kind, x, y, r, rot=0.0):
    n = 4 if kind == "kare" else 3
    a0 = (math.pi / 4 if kind == "kare" else -math.pi / 2) + rot
    rr = r * (math.sqrt(2) if kind == "kare" else 1.15)
    return [(x + math.cos(a0 + 2 * math.pi * k / n) * rr, y + math.sin(a0 + 2 * math.pi * k / n) * rr + (r * 0.18 if n == 3 else 0))
            for k in range(n)]


def piece(p, kind, x, y, r, rot=0.0, glow=0.0, seed="pc"):
    """Şekil kutusunun oyuncak parçası (kalın, parlak)."""
    col = SHAPE_COL[kind]
    if glow > 0:
        p.glow(x, y, r * 2.4, lighten_c(col, 0.5), 0.7 * glow)
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot if kind == "daire" else 0.0)
    p.part(lambda c: shape_path(c, kind, 0, 0, r, 0 if kind == "daire" else rot), col, seed=f"{seed}{kind}")
    if kind == "daire":
        p.part(lambda c: circle(c, 0, 0, r * 0.18), darken_c(col, 0.2), seed=f"{seed}{kind}k", line=False)
    ctx.restore()


def edge_highlight(p, kind, x, y, r, k, rot=0.0, col=None):
    """Kenar sayarken k. kenarı parlat (0'dan başlar)."""
    vs = shape_vertices(kind, x, y, r, rot)
    a, b = vs[k % len(vs)], vs[(k + 1) % len(vs)]
    p.stroke(lambda c: (c.move_to(*a), c.line_to(*b)), col or (1, 1, 1), width=9, alpha=0.95)
    for q in (a, b):
        p.part(lambda c, q=q: circle(c, q[0], q[1], 9), (1, 1, 1), seed=f"ev{k}", line=False)


def shape_box(p, x, y, s, filled=(), glow=None, lid_shake=0.0):
    """Şekil kutusu: mor ahşap kutu, üstünde üç delik (daire, kare, üçgen). filled: deliğine oturmuş parçalar.
    x, y: kutunun tabanının ortası."""
    W_, H_ = 210 * s, 120 * s
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(lid_shake)
    p.part(lambda c: rounded_rect(c, -W_ / 2, -H_, W_, H_, 14 * s), hexrgb("#9B6BD3"), seed="sb_body")
    p.part(lambda c: rounded_rect(c, -W_ / 2 - 8 * s, -H_ - 18 * s, W_ + 16 * s, 26 * s, 10 * s), hexrgb("#B48BE6"), seed="sb_lid")
    for k, kind in enumerate(("daire", "kare", "ucgen")):
        hx = (-62 + 62 * k) * s
        hy = -H_ - 5 * s
        ctx.save()
        ctx.translate(hx, hy)
        ctx.scale(1, 0.42)
        if kind in filled:
            p.part(lambda c, kind=kind: shape_path(c, kind, 0, 0, 22 * s), SHAPE_COL[kind], seed=f"sb_f{kind}")
        else:
            p.part(lambda c, kind=kind: shape_path(c, kind, 0, 0, 22 * s), hexrgb("#4B2F6E"), seed=f"sb_h{kind}", lw=0.7)
        ctx.restore()
        if glow and glow.get(kind, 0) > 0:
            p.glow(x + hx, y + hy, 60 * s, lighten_c(SHAPE_COL[kind], 0.5), 0.8 * glow[kind])
    # ön yüzde küçük şekil çıkartmaları
    for k, kind in enumerate(("daire", "kare", "ucgen")):
        p.part(lambda c, k=k, kind=kind: shape_path(c, kind, (-60 + 60 * k) * s, -H_ * 0.45, 14 * s), lighten_c(SHAPE_COL[kind], 0.25),
               seed=f"sb_st{kind}", lw=0.6)
    ctx.restore()


def stump(p, x, y, s):
    p.part(lambda c: rounded_rect(c, x - 55 * s, y - 70 * s, 110 * s, 72 * s, 10 * s), hexrgb("#9A6A45"), seed="st_b")
    p.part(lambda c: ellipse(c, x, y - 70 * s, 55 * s, 16 * s), hexrgb("#D9A86C"), seed="st_t")
    p.part(lambda c: ellipse(c, x, y - 70 * s, 32 * s, 8 * s), hexrgb("#C08A55"), seed="st_r", line=False)


def cookie(p, x, y, r, glow=0.0, bite=False, seed="ck"):
    if glow > 0:
        p.glow(x, y, r * 2.2, COL["sari_l"], 0.8 * glow)

    def body(c):
        circle(c, x, y, r)
        if bite:
            c.new_sub_path()
            c.arc_negative(x + r * 0.8, y - r * 0.6, r * 0.42, 0, 2 * math.pi)

    p.part(body, hexrgb("#E8B46A"), seed=f"{seed}b")
    for k in range(5):
        a = k * 2.3 + 0.4
        p.part(lambda c, a=a, k=k: circle(c, x + math.cos(a) * r * (0.25 + 0.12 * k % 2 + 0.3), y + math.sin(a) * r * 0.5, r * 0.11),
               hexrgb("#6B3F25"), seed=f"{seed}c{k}", line=False)


def cookie_plate(p, x, y, s, glow_idx=-1):
    """Kütüğün üstünde tabak ve üç kurabiye (yandan, hafif perspektif)."""
    p.part(lambda c: ellipse(c, x, y, 95 * s, 22 * s), (1, 1, 1), seed="pl")
    for k in range(3):
        cx = x + (k - 1) * 58 * s
        cookie(p, cx, y - 20 * s, 26 * s, glow=1.0 if k == glow_idx else 0.0, seed=f"ck{k}")


def wheelbarrow(p, x, y, s, rot=0.0, glow=0.0):
    """El arabası: büyük yuvarlak tekerlek (daire örneği)."""
    wx, wy, wr = x + 70 * s, y - 42 * s, 42 * s
    p.part(lambda c: capsule(c, x - 120 * s, y - 120 * s, x - 190 * s, y - 85 * s, 8 * s, 7 * s), COL["kahve"], seed="wb_h1")
    p.part(lambda c: (c.move_to(x - 120 * s, y - 150 * s), c.line_to(x + 110 * s, y - 150 * s), c.line_to(x + 70 * s, y - 80 * s),
                      c.line_to(x - 90 * s, y - 80 * s), c.close_path()), hexrgb("#5FAE4E"), seed="wb_tub")
    p.part(lambda c: capsule(c, x - 80 * s, y - 80 * s, x - 70 * s, y - 2 * s, 6 * s, 5 * s), COL["kahve"], seed="wb_leg")
    if glow > 0:
        p.glow(wx, wy, wr * 2.2, COL["sari_l"], 0.7 * glow)
    p.part(lambda c: circle(c, wx, wy, wr), hexrgb("#3A3A44"), seed="wb_w")
    p.part(lambda c: circle(c, wx, wy, wr * 0.62), hexrgb("#C9CBD6"), seed="wb_rim")
    for k in range(4):
        a = rot + k * math.pi / 2
        p.stroke(lambda c, a=a: (c.move_to(wx, wy), c.line_to(wx + math.cos(a) * wr * 0.6, wy + math.sin(a) * wr * 0.6)), (0.35, 0.35, 0.42), width=4)
    p.part(lambda c: circle(c, wx, wy, wr * 0.16), hexrgb("#7A7C88"), seed="wb_hub")


def shape_house(p, x, y, s, window_glow=0.0, roof_glow=0.0, wave=0.0):
    """Şekil evi: kare duvar, KARE pencere (haçlı), ÜÇGEN çatı, yuvarlak kapı tokmağı."""
    Wd, Hd = 300 * s, 230 * s
    p.part(lambda c: rounded_rect(c, x - Wd / 2, y - Hd, Wd, Hd, 10 * s), hexrgb("#FBEBD0"), seed="shw")
    if roof_glow > 0:
        p.glow(x, y - Hd - 80 * s, 230 * s, COL["kirmizi_l"], 0.6 * roof_glow)
    p.part(lambda c: (c.move_to(x - Wd / 2 - 40 * s, y - Hd + 8 * s), c.line_to(x, y - Hd - 190 * s),
                      c.line_to(x + Wd / 2 + 40 * s, y - Hd + 8 * s), c.close_path()), hexrgb("#E2574C"), seed="shr")
    p.part(lambda c: rounded_rect(c, x + 60 * s, y - Hd - 150 * s, 34 * s, 80 * s, 4 * s), hexrgb("#B8574A"), seed="shch")
    # kapı
    p.part(lambda c: rounded_rect(c, x - 110 * s, y - 140 * s, 80 * s, 140 * s, 12 * s), hexrgb("#8C5A3C"), seed="shd")
    p.part(lambda c: circle(c, x - 45 * s, y - 70 * s, 7 * s), COL["sari"], seed="shdk")
    # kare pencere
    wx, wy, ww = x + 70 * s, y - 135 * s, 50 * s
    if window_glow > 0:
        p.glow(wx, wy, 130 * s, COL["mavi_l"], 0.7 * window_glow)
    p.part(lambda c: rounded_rect(c, wx - ww - 8 * s, wy - ww - 8 * s, 2 * ww + 16 * s, 2 * ww + 16 * s, 6 * s), hexrgb("#FFFFFF"), seed="shwf")
    p.part(lambda c: rounded_rect(c, wx - ww, wy - ww, 2 * ww, 2 * ww, 4 * s), hexrgb("#9FD0FA"), seed="shwg")
    p.part(lambda c: (rounded_rect(c, wx - 4 * s, wy - ww, 8 * s, 2 * ww, 2 * s), rounded_rect(c, wx - ww, wy - 4 * s, 2 * ww, 8 * s, 2 * s)),
           hexrgb("#FFFFFF"), seed="shwx", lw=0.6)
    p.part(lambda c: rounded_rect(c, wx - ww - 14 * s, wy + ww + 6 * s, 2 * ww + 28 * s, 16 * s, 5 * s), hexrgb("#E8D5B0"), seed="shws")
    # çiçek saksısı (pencere önünde)
    for k in range(3):
        p.part(lambda c, k=k: circle(c, wx - 30 * s + k * 30 * s, wy + ww - 2 * s, 9 * s), [COL["kirmizi"], COL["sari"], COL["mor"]][k],
               seed=f"shfl{k}", lw=0.5)
    return (wx, wy, ww), (x, y - Hd - 70 * s)


def gift_box(p, x, y, s, open_u=0.0, glow=0.0):
    """Kurdeleli hediye kutusu (kare). open_u: kapak açılması 0..1."""
    a = 72 * s
    if glow > 0:
        p.glow(x, y - a, a * 2.2, COL["mavi_l"], 0.7 * glow)
    p.part(lambda c: rounded_rect(c, x - a, y - 2 * a, 2 * a, 2 * a, 6 * s), hexrgb("#F59AC0"), seed="gb_b")
    p.part(lambda c: rounded_rect(c, x - 10 * s, y - 2 * a, 20 * s, 2 * a, 3 * s), COL["sari"], seed="gb_r", lw=0.6)
    lift = 90 * s * ease_out_back(clamp(open_u))
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y - 2 * a - lift)
    ctx.rotate(-0.5 * clamp(open_u))
    p.part(lambda c: rounded_rect(c, -a - 10 * s, -24 * s, 2 * a + 20 * s, 28 * s, 6 * s), hexrgb("#F7B5D2"), seed="gb_l")
    p.part(lambda c: (ellipse(c, -22 * s, -36 * s, 24 * s, 14 * s, 0.5), ellipse(c, 22 * s, -36 * s, 24 * s, 14 * s, -0.5)), COL["sari"], seed="gb_bow")
    ctx.restore()


def bone(p, x, y, s, rot=0.0):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    p.part(lambda c: (rounded_rect(c, -40 * s, -9 * s, 80 * s, 18 * s, 9 * s), circle(c, -42 * s, -10 * s, 13 * s), circle(c, -42 * s, 10 * s, 13 * s),
                      circle(c, 42 * s, -10 * s, 13 * s), circle(c, 42 * s, 10 * s, 13 * s)), hexrgb("#FFF6E5"), seed="bone")
    ctx.restore()


def checker_blanket(p, x, y, s, glow_idx=(), cols=4, rows=2):
    """Kareli piknik örtüsü (önden, hafif yatık). glow_idx: parlayan karelerin sırası (soldan sağa ön sıra)."""
    q = 62 * s
    x0 = x - cols * q / 2
    for r in range(rows):
        for k in range(cols):
            yy = y - (rows - r) * q * 0.55
            dark = (r + k) % 2 == 0
            col = COL["mavi"] if dark else (1, 1, 1)
            idx = k if r == rows - 1 else -1
            if idx in glow_idx:
                col = lighten_c(COL["mavi"], 0.45) if not dark else lighten_c(COL["mavi"], 0.2)
            sk = 0.12 * (k - cols / 2 + 0.5) * q

            def cell(c, k=k, yy=yy, sk=sk):
                c.move_to(x0 + k * q + sk * 0.8, yy)
                c.line_to(x0 + (k + 1) * q + sk * 0.8 + 0.12 * q, yy)
                c.line_to(x0 + (k + 1) * q + sk + 0.12 * q, yy + q * 0.55)
                c.line_to(x0 + k * q + sk, yy + q * 0.55)
                c.close_path()

            p.part(cell, col, seed=f"cb{r}{k}", lw=0.6, flat=True)
            if idx in glow_idx:
                p.glow(x0 + (k + 0.5) * q, yy + q * 0.27, q, COL["mavi_l"], 0.6)


def paper_boat(p, x, y, s, t, glow=0.0):
    """Kâğıt gemi: beyaz gövde, ÜÇGEN kırmızı yelken."""
    bob = 4 * math.sin(t * 2.2)
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y + bob)
    ctx.rotate(0.04 * math.sin(t * 1.7))
    if glow > 0:
        p.glow(0, -90 * s, 120 * s, COL["kirmizi_l"], 0.7 * glow)
    p.part(lambda c: capsule(c, 0, -10 * s, 0, -150 * s, 4 * s, 4 * s), COL["kahve"], seed="pb_m")
    p.part(lambda c: (c.move_to(6 * s, -150 * s), c.line_to(6 * s, -30 * s), c.line_to(95 * s, -38 * s), c.close_path()),
           COL["kirmizi"], seed="pb_s")
    p.part(lambda c: (c.move_to(-110 * s, -30 * s), c.line_to(110 * s, -30 * s), c.line_to(70 * s, 10 * s), c.line_to(-70 * s, 10 * s),
                      c.close_path()), hexrgb("#FFFFFF"), seed="pb_h")
    ctx.restore()
    return (x + 45 * s, y + bob - 85 * s)


def watermelon_slice(p, x, y, s, rot=0.0, bitten=0, seed="wm"):
    """Karpuz dilimi (üçgen): yeşil kabuk, kırmızı iç, siyah çekirdekler. bitten: ısırık sayısı."""
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    r = 60 * s

    def flesh(c):
        c.move_to(0, -r * 1.1)
        c.line_to(-r * 0.8, r * 0.5)
        c.curve_to(-r * 0.3, r * 0.68, r * 0.3, r * 0.68, r * 0.8, r * 0.5)
        c.close_path()
        for b in range(bitten):
            c.new_sub_path()
            c.arc_negative(-r * 0.05 + b * r * 0.25, -r * 1.05 + b * r * 0.22, r * 0.28, 0, 2 * math.pi)

    p.part(lambda c: (c.move_to(-r * 0.86, r * 0.52), c.curve_to(-r * 0.3, r * 0.82, r * 0.3, r * 0.82, r * 0.86, r * 0.52),
                      c.line_to(r * 0.8, r * 0.5), c.curve_to(r * 0.3, r * 0.68, -r * 0.3, r * 0.68, -r * 0.8, r * 0.5), c.close_path()),
           hexrgb("#3F8A3B"), seed=f"{seed}rind")
    p.part(flesh, hexrgb("#F2665C"), seed=f"{seed}fl")
    for k, (dx, dy) in enumerate(((-0.25, 0.15), (0.2, 0.1), (0.0, -0.25), (-0.05, 0.38), (0.32, 0.35))):
        if dy * r < -r * 1.05 + bitten * r * 0.3:
            continue
        p.part(lambda c, dx=dx, dy=dy: ellipse(c, dx * r, dy * r, 4 * s, 7 * s, 0.3), hexrgb("#2A1E1E"), seed=f"{seed}sd{k}", line=False)
    ctx.restore()


def bunting(p, x0, x1, y, t, n=9, sag=40):
    """İki direk arasında üçgen flamalar."""
    for xp in (x0, x1):
        p.part(lambda c, xp=xp: capsule(c, xp, y + 260, xp, y - 20, 6, 5), COL["kahve"], seed=f"bt_p{xp}")
    cols = [COL["kirmizi"], COL["kirmizi_l"]]

    def yat(u):
        return y + sag * 4 * u * (1 - u)

    p.stroke(lambda c: [c.move_to(x0, y)] + [c.line_to(x0 + (x1 - x0) * k / 20, yat(k / 20)) for k in range(21)], (0.35, 0.25, 0.2), width=3)
    for k in range(n):
        u0, u1 = (k + 0.15) / n, (k + 0.85) / n
        sw = 6 * math.sin(t * 2.5 + k)
        a, b = (x0 + (x1 - x0) * u0, yat(u0)), (x0 + (x1 - x0) * u1, yat(u1))
        tip = ((a[0] + b[0]) / 2 + sw, (a[1] + b[1]) / 2 + 62)
        p.part(lambda c, a=a, b=b, tip=tip: (c.move_to(*a), c.line_to(*b), c.line_to(*tip), c.close_path()), cols[k % 2], seed=f"bt{k}", lw=0.6)


def outline_shape(p, kind, x, y, r, prog, alpha=1.0, rot=0.0):
    """Nesnenin etrafına şeklin çizgisi çizilir (prog 0..1 çizilme ilerlemesi), kesik çizgi, şeklin renginde."""
    if prog <= 0 or alpha <= 0.01:
        return
    col = SHAPE_COL[kind]
    ctx = p.ctx
    ctx.save()
    ctx.new_path()
    if kind == "daire":
        ctx.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * clamp(prog))
    else:
        vs = shape_vertices(kind, x, y, r, rot)
        vs = vs + [vs[0]]
        segs = len(vs) - 1
        total = clamp(prog) * segs
        ctx.move_to(*vs[0])
        for k in range(segs):
            if total <= k:
                break
            u = min(1.0, total - k)
            a, b = vs[k], vs[k + 1]
            ctx.line_to(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    path = ctx.copy_path()
    ctx.restore()

    def draw(c):
        c.append_path(path)

    sc = p.scale
    ctx.save()
    ctx.new_path()
    ctx.append_path(path)
    ctx.identity_matrix()
    ctx.set_line_cap(1)
    ctx.set_line_join(1)
    ctx.set_dash([])
    ctx.set_source_rgba(1, 1, 1, 0.9 * alpha)
    ctx.set_line_width(16 * sc)
    ctx.stroke_preserve()
    ctx.set_source_rgba(*col, alpha)
    ctx.set_line_width(9 * sc)
    ctx.stroke()
    ctx.restore()


def draw_shape_badge(p, key, alpha):
    """Sol üst köşe rozeti: şeklin kendisi ve adı."""
    if alpha <= 0.01:
        return
    import cairo
    col = SHAPE_COL[key]
    ctx = p.ctx
    ctx.save()
    ctx.translate(150, 120)
    p.part(lambda c: circle(c, 0, 0, 74), (1, 1, 1), alpha=alpha * 0.95, seed="bdg_bg")
    p.part(lambda c: shape_path(c, key, 0, -10, 34), col, alpha=alpha, seed="bdg_s")
    ctx.select_font_face("Baloo 2", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(26)
    w = SHAPE_WORD[key]
    ext = ctx.text_extents(w)
    p.part(lambda c: (c.move_to(-ext.width / 2 - ext.x_bearing, 52), c.text_path(w)), darken_c(col, 0.15), alpha=alpha, seed="bdg_t",
           lw=0.5)
    ctx.restore()
