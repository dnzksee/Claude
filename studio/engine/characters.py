"""Karakterler: Umay (4 yaşında kız), Zıpzıp (köpek), kelebek, çiçekler, ışıltılar.
Hepsi Painter.part / stroke diliyle çizilir; böylece her teknikte aynı model kullanılır."""
import math

from .core import capsule, ellipse, circle, blob, clamp, lerp, hexrgb

# ---------------------------------------------------------------- RENK PALETİ (dizi kimliği)
PAL = {
    "skin": hexrgb("#FAD3B8"),
    "cheek": hexrgb("#F5918C"),
    "hair": hexrgb("#7A4426"),
    "dress": hexrgb("#EE6A5E"),      # mercan kırmızısı elbise
    "dress_l": hexrgb("#FBEFE6"),
    "ribbon": hexrgb("#FFC93C"),     # sarı kurdeleler
    "shoe": hexrgb("#FFB03A"),
    "eye": hexrgb("#2B1D1A"),
    "mouth": hexrgb("#9C2F36"),
    "tongue": hexrgb("#F2878A"),
    "dog": hexrgb("#F8EAD6"),        # krem-beyaz Zıpzıp
    "dog_d": hexrgb("#E6D2B6"),
    "dog_muzzle": hexrgb("#FFFDF8"),
    "caramel": hexrgb("#D9955A"),    # karamel kulak ve göz lekesi
    "collar": hexrgb("#E2383F"),
    "gold": hexrgb("#F6C342"),
    "nose": hexrgb("#2A1E1E"),
    "bf_wing": hexrgb("#FFD23F"),
    "bf_edge": hexrgb("#F7882F"),
    "bf_body": hexrgb("#4A3426"),
    "leaf": hexrgb("#6DB55A"),
    "stem": hexrgb("#4E9A47"),
    "white": (1.0, 1.0, 1.0),
}


# ---------------------------------------------------------------- POZLAR
def umay_arm_pose(name, t):
    """Kol açıları: (sol omuz, sol dirsek, sağ omuz, sağ dirsek). Açı aşağıdan dışa doğru."""
    if name == "idle":
        b = math.sin(t * 2.1) * 0.03
        return (0.15 + b, -0.14, 0.15 + b, -0.14)
    if name == "wave":
        return (0.15, -0.14, 2.55, 0.35 + 0.45 * math.sin(t * 7.0))
    if name == "point":
        return (0.15, -0.14, 2.05 + 0.04 * math.sin(t * 3), 0.05)
    if name == "cheer":
        w = math.sin(t * 7.0) * 0.12
        return (2.55 + w, 0.25, 2.55 - w, 0.25)
    if name == "laugh":
        return (0.38, -1.95, 0.38, -1.95)
    if name == "hug":
        return (0.55, -1.6, 1.35, 0.55)
    if name == "think":
        return (0.15, -0.14, 0.55, -2.4)
    return (0.15, -0.14, 0.15, -0.14)


def blend_pose(a, b, u):
    return tuple(lerp(x, y, u) for x, y in zip(a, b))


# ---------------------------------------------------------------- UMAY
def draw_umay(p, x, y, s, st):
    """st: facing, phase, gait(0 dur, 1 yürü, 2 koş), arms(4'lü), look, eye_dx, eye_dy,
    blink, mouth, smile, happy, brow, tilt, jump, lean"""
    ctx = p.ctx
    t = p.t
    f = st.get("facing", 1)
    ph = st.get("phase", 0.0)
    gait = st.get("gait", 0.0)
    walk_amt = clamp(gait)
    run_amt = clamp(gait - 1)
    stride = lerp(st.get("stride_w", 150), 210, run_amt)   # bir tam döngüde alınan yol (gait tablosuyla aynı)
    lift = lerp(13, 24, run_amt) * walk_amt
    bob = -abs(math.sin(ph)) * lerp(4, 9, run_amt) * walk_amt
    breathe = math.sin(t * 2.2) * 1.2 * (1 - walk_amt)
    jump = st.get("jump", 0.0)
    look = st.get("look", 0.0)
    tilt = st.get("tilt", 0.0)
    lean = st.get("lean", 0.0) + 0.06 * run_amt

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * f, s)

    # --- bacaklar: basan ayak yerde sabit kalır, adım atan ayak kavisle öne gelir; diz öne bükülür
    ctx.save()
    ctx.translate(0, -jump)
    L1 = L2 = 41.0
    for side, off, shade in ((-1, math.pi, 0.07), (1, 0.0, 0.0)):   # önce uzak bacak (arkada, biraz koyu)
        u = ((ph + off) % (2 * math.pi)) / (2 * math.pi)
        q = stride / 4
        if u < 0.5:                       # basma: ayak geriye kayar (gövde ilerler)
            fx, lf, toe = q * (1 - 4 * u), 0.0, 0.0
        else:                             # adım: ayak havada öne gelir
            v = (u - 0.5) * 2
            fx = -q + 2 * q * (v * v * (3 - 2 * v))
            lf = math.sin(math.pi * v) * lift
            toe = -0.3 * math.sin(math.pi * v)
        fx *= walk_amt
        hx, hy = side * 4.0, -96.0 + bob * 0.6
        axx, ayy = fx + side * 3.0, -16.0 - lf
        dx, dy = axx - hx, ayy - hy
        d = min(math.hypot(dx, dy), L1 + L2 - 0.5)
        hh = math.sqrt(max(L1 * L1 - (d / 2) ** 2, 0.0))
        nx_, ny_ = -dy / max(d, 1e-6), dx / max(d, 1e-6)
        if nx_ < 0:
            nx_, ny_ = -nx_, -ny_
        kx, ky = hx + dx / 2 + nx_ * hh, hy + dy / 2 + ny_ * hh
        skin = darken_c(PAL["skin"], shade)
        p.part(lambda c, a=(hx, hy, kx, ky), b=(kx, ky, axx, ayy): (capsule(c, *a, 10, 9.5), capsule(c, *b, 9.5, 9)),
               skin, seed=f"umay_leg{side}")
        p.part(lambda c, axx=axx, ayy=ayy, toe=toe: ellipse(c, axx + 8, ayy + 7, 17, 10, toe), darken_c(PAL["shoe"], shade),
               seed=f"umay_shoe{side}")
    ctx.restore()

    ctx.save()
    ctx.translate(0, bob - jump + breathe * 0.3)
    ctx.translate(0, -100)
    ctx.rotate(lean)
    ctx.translate(0, 100)

    # --- arka saç + kuyruklar (başın arkasında)
    ctx.save()
    ctx.translate(0, -196)
    ctx.rotate(tilt)
    ctx.translate(0, 196)
    sway = math.sin(ph * 2 - 0.8) * 0.07 * walk_amt + math.sin(t * 1.7) * 0.03 + tilt * 0.6
    p.part(lambda c: blob(c, look * 4, -262, 80, n=9, wobble=0.05, seed=3, sx=1.02, sy=0.98), PAL["hair"], seed="umay_bhair")
    for side in (-1, 1):
        ctx.save()
        ctx.translate(side * 74, -268)
        ctx.rotate(sway + side * 0.15 * (jump > 1))
        p.part(lambda c: blob(c, side * 20, 14, 31, n=8, wobble=0.1, seed=side + 5), PAL["hair"], seed=f"umay_pig{side}")
        p.part(lambda c: (ellipse(c, side * 4, -8, 15, 9, 0.6 * side), ellipse(c, side * 4, -8, 15, 9, -0.6 * side + math.pi)),
               PAL["ribbon"], seed=f"umay_bow{side}")
        p.part(lambda c: circle(c, side * 4, -8, 6), PAL["ribbon"], seed=f"umay_bowk{side}")
        ctx.restore()
    ctx.restore()

    # --- boyun + elbise
    p.part(lambda c: capsule(c, 0, -205, 0, -180, 10), PAL["skin"], seed="umay_neck", line=False)
    sw = math.sin(ph * 2 + 1.2) * 2.5 * walk_amt + math.sin(t * 1.3) * 1.2

    def dress(c):
        c.move_to(-22, -192)
        c.curve_to(-34, -189, -40, -178, -42, -160)
        c.curve_to(-48, -138, -60, -112, -64 + sw, -92)
        c.curve_to(-30 + sw, -80, 30 + sw, -80, 64 + sw, -92)
        c.curve_to(60, -112, 48, -138, 42, -160)
        c.curve_to(40, -178, 34, -189, 22, -192)
        c.curve_to(10, -186, -10, -186, -22, -192)
        c.close_path()

    p.part(dress, PAL["dress"], seed="umay_dress")
    p.part(lambda c: (ellipse(c, -12, -187, 14, 8, 0.25), ellipse(c, 12, -187, 14, 8, -0.25)), PAL["dress_l"], seed="umay_collar")

    def heart(c, hx=24, hy=-128, r=8):
        c.move_to(hx, hy + r * 1.1)
        c.curve_to(hx - r * 1.6, hy, hx - r * 0.9, hy - r * 1.3, hx, hy - r * 0.4)
        c.curve_to(hx + r * 0.9, hy - r * 1.3, hx + r * 1.6, hy, hx, hy + r * 1.1)
        c.close_path()

    p.part(heart, PAL["ribbon"], seed="umay_heart", lw=0.6)

    # --- kollar
    arms = st.get("arms", umay_arm_pose("idle", t))
    if walk_amt > 0:
        # kollar bacaklara ters salınır: öne giden kolun dirseği bükülür (derinlik hissi), geri giden düzleşir.
        # Koşarken dirsekler bükük, eller göğüs hizasında sırayla pompalar.
        k = walk_amt
        sn = math.sin(ph)
        sw_w = 0.10 * sn
        el_w = 0.22 * max(0.0, sn), 0.22 * max(0.0, -sn)        # (sol, sağ) dirsek bükümü (içe)
        run_l = (0.55 - 0.18 * sn, -2.35 - 0.25 * sn)
        run_r = (0.55 + 0.18 * sn, -2.35 + 0.25 * sn)
        walk_l = (arms[0] + sw_w, arms[1] - el_w[0])
        walk_r = (arms[2] - sw_w, arms[3] - el_w[1])
        rl = blend_pose(walk_l, run_l, run_amt)
        rr = blend_pose(walk_r, run_r, run_amt)
        arms = blend_pose(arms, (rl[0], rl[1], rr[0], rr[1]), k)
    hands = {}
    for side, (sa, ea) in ((-1, arms[0:2]), (1, arms[2:4])):
        sx_, sy_ = side * 33, -176
        ex, ey = sx_ + side * math.sin(sa) * 42, sy_ + math.cos(sa) * 42
        fa = sa + ea
        hx, hy = ex + side * math.sin(fa) * 38, ey + math.cos(fa) * 38
        p.part(lambda c, a=(sx_, sy_, ex, ey), b=(ex, ey, hx, hy): (capsule(c, *a, 9.5, 9), capsule(c, *b, 9, 8.5), circle(c, b[2], b[3], 11.5)),
               PAL["skin"], seed=f"umay_arm{side}")
        p.part(lambda c, sx_=sx_, sy_=sy_: ellipse(c, sx_, sy_ + 2, 16, 14), PAL["dress"], seed=f"umay_sleeve{side}")
        hands[side] = ctx.user_to_device(hx, hy)

    # --- baş
    ctx.save()
    ctx.translate(0, -196)
    ctx.rotate(tilt)
    ctx.translate(0, 196)
    p.part(lambda c: ellipse(c, look * 3, -262, 71, 67), PAL["skin"], seed="umay_head")
    lx = look * 15
    for side in (-1, 1):
        p.part(lambda c, side=side: ellipse(c, side * 45 + look * 9, -226, 13, 9), PAL["cheek"],
               alpha=0.55, line=False, seed=f"umay_cheek{side}")
    # gözler
    blink = st.get("blink", 0.0)
    happy = st.get("happy", 0.0)
    edx, edy = st.get("eye_dx", 0.0) * f, st.get("eye_dy", 0.0)
    for side in (-1, 1):
        ex, ey = side * 25 + lx + edx * 3.0, -248 + edy * 3.0
        if st.get("sour", 0) > 0.5:
            p.stroke(lambda c, ex=ex, ey=ey, side=side: (c.move_to(ex - 9 * side, ey - 7), c.line_to(ex + 7 * side, ey), c.line_to(ex - 9 * side, ey + 7)),
                     PAL["eye"], width=4.5)
        elif happy > 0.5:
            p.stroke(lambda c, ex=ex, ey=ey: (c.move_to(ex - 10, ey + 3), c.curve_to(ex - 5, ey - 9, ex + 5, ey - 9, ex + 10, ey + 3)),
                     PAL["eye"], width=4.5)
        elif blink > 0.75:
            p.stroke(lambda c, ex=ex, ey=ey: (c.move_to(ex - 10, ey + 1), c.curve_to(ex - 5, ey + 6, ex + 5, ey + 6, ex + 10, ey + 1)),
                     PAL["eye"], width=4.0)
        else:
            ry = 14.5 * (1 - blink)
            p.part(lambda c, ex=ex, ey=ey, ry=ry: ellipse(c, ex, ey, 10.5, ry), PAL["eye"], line=False, seed=f"umay_eye{side}")
            p.part(lambda c, ex=ex, ey=ey: (circle(c, ex + 3.5, ey - 5.5, 4.2), circle(c, ex - 3.5, ey + 5, 2.0)),
                   PAL["white"], line=False, seed=f"umay_hl{side}", wet=0.3)
        br = st.get("brow", 0.0)
        p.stroke(lambda c, ex=ex, ey=ey, br=br, side=side: (c.move_to(ex - 9, ey - 21 - br * 7 + side * br * 2),
                                                           c.curve_to(ex - 4, ey - 26 - br * 8, ex + 4, ey - 26 - br * 8, ex + 9, ey - 21 - br * 7 - side * br * 2)),
                 PAL["hair"], width=3.6)
    # burun
    p.stroke(lambda c: (c.move_to(lx * 1.05 - 4, -234), c.curve_to(lx * 1.05 - 1, -230, lx * 1.05 + 2, -230, lx * 1.05 + 4, -233)),
             darken_c(PAL["skin"], 0.35), width=3.0)
    # ağız
    mo = st.get("mouth", 0.0)
    sm = st.get("smile", 1.0)
    mx_ = lx * 0.95
    if st.get("sour", 0) > 0.5:
        p.stroke(lambda c: (c.move_to(mx_ - 12, -214), c.line_to(mx_ - 6, -219), c.line_to(mx_, -214), c.line_to(mx_ + 6, -219), c.line_to(mx_ + 12, -214)),
                 PAL["mouth"], width=4.0)
    elif mo > 0.07:
        hh = 6 + 18 * mo

        def mouth(c):
            c.move_to(mx_ - 13, -217)
            c.curve_to(mx_ - 10, -217 + hh, mx_ + 10, -217 + hh, mx_ + 13, -217)
            c.curve_to(mx_ + 6, -215, mx_ - 6, -215, mx_ - 13, -217)
            c.close_path()

        p.part(mouth, PAL["mouth"], seed="umay_mouth", lw=0.7)
        p.part(lambda c: ellipse(c, mx_, -217 + hh * 0.72, 7, hh * 0.22 + 1), PAL["tongue"], line=False, seed="umay_tongue")
    else:
        p.stroke(lambda c: (c.move_to(mx_ - 12, -218), c.curve_to(mx_ - 6, -218 + 9 * sm, mx_ + 6, -218 + 9 * sm, mx_ + 12, -218)),
                 PAL["mouth"], width=3.8)
    # perçem
    bx = look * 7

    def bangs(c):
        cx, cy, r = bx, -264, 74
        c.move_to(cx + r * math.cos(math.radians(-8)), cy + r * math.sin(math.radians(-8)))
        c.arc_negative(cx, cy, r, math.radians(-8), math.radians(-172))
        xs = [cx - 72, cx - 38, cx - 4, cx + 32, cx + 72]
        yf = -282
        c.line_to(xs[0], yf + 6)
        for i in range(4):
            xa, xb = xs[i], xs[i + 1]
            c.curve_to(xa + 7, yf + 20, xb - 9, yf + 18, xb, yf - 2 + (8 if i == 3 else 0))
        c.close_path()

    p.part(bangs, PAL["hair"], seed="umay_bangs")
    p.part(lambda c: ellipse(c, bx - 28, -312, 16, 6, -0.4), lighten_c(PAL["hair"], 0.35), alpha=0.6, line=False, seed="umay_hairhl")
    ctx.restore()
    ctx.restore()
    ctx.restore()
    return {"hands": hands}


def lighten_c(c, k):
    return tuple(v + (1 - v) * k for v in c)


def darken_c(c, k):
    return tuple(v * (1 - k) for v in c)


# ---------------------------------------------------------------- ZIPZIP
def draw_zipzip(p, x, y, s, st):
    """st: facing, phase, gait, tilt, mouth, wag, blink, happy, cross, sneeze, jump, look_up"""
    ctx = p.ctx
    t = p.t
    f = st.get("facing", 1)
    ph = st.get("phase", 0.0)
    gait = st.get("gait", 0.0)
    walk_amt = clamp(gait)
    run_amt = clamp(gait - 1)
    amp = lerp(0.42, 0.7, run_amt) * walk_amt
    lift = lerp(7, 15, run_amt) * walk_amt
    bob = -abs(math.sin(ph)) * lerp(4, 9, run_amt) * walk_amt
    jump = st.get("jump", 0.0)
    sneeze = st.get("sneeze", 0.0)
    wag = st.get("wag", 1.0)
    breathe = math.sin(t * 3.0) * 1.0

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * f, s)
    sq = 1.0 + 0.06 * max(0.0, sneeze) - 0.04 * min(0.0, sneeze)
    ctx.scale(sq, 1 / sq)

    legs_back = [(-36, 1, "fb"), (34, -1, "ff")]
    legs_front = [(-30, -1, "nb"), (40, 1, "nf")]

    def leg(lx, sign, name, col):
        a = math.sin(ph) * amp * sign
        lf = max(0.0, math.cos(ph) * sign) * lift
        hy = -58 + bob - jump
        fx, fy = lx + math.sin(a) * 52, hy + math.cos(a) * 52 - lf
        p.part(lambda c: capsule(c, lx, hy, fx, fy, 12, 10.5), col, seed=f"pm_leg{name}")
        p.part(lambda c: ellipse(c, fx + 4, fy + 2, 14, 8.5), col, seed=f"pm_paw{name}")

    for lx, sign, name in legs_back:
        leg(lx + 6, sign, name, PAL["dog_d"])

    ctx.save()
    ctx.translate(0, bob - jump + breathe * 0.4)
    # kuyruk
    wa = math.sin(t * lerp(9, 16, clamp(wag - 1))) * 0.45 * min(wag, 1.6)
    ctx.save()
    ctx.translate(-54, -78)
    ctx.rotate(0.55 + wa)
    p.part(lambda c: (capsule(c, 0, 0, -22, -14, 10, 9), capsule(c, -22, -14, -34, -36, 9, 8), circle(c, -36, -42, 13)),
           PAL["dog"], seed="pm_tail")
    ctx.restore()
    # gövde
    p.part(lambda c: blob(c, 0, -68, 62, n=10, wobble=0.04, seed=11, sx=1.0, sy=0.62), PAL["dog"], seed="pm_body")
    p.part(lambda c: ellipse(c, -18, -60, 22, 15, 0.2), PAL["caramel"], alpha=0.85, seed="pm_spot", lw=0.6)
    ctx.restore()

    for lx, sign, name in legs_front:
        leg(lx, sign, name, PAL["dog"])

    # baş
    ctx.save()
    ctx.translate(0, bob - jump)
    ctx.translate(42, -92)
    head_rot = st.get("tilt", 0.0) - 0.22 * clamp(-sneeze) + 0.18 * clamp(sneeze) - 0.25 * st.get("look_up", 0.0)
    ctx.rotate(head_rot)
    ctx.translate(-42, 92)
    # uzak kulak
    ear_sw = math.sin(ph * 1.0 - 1.0) * 0.25 * walk_amt + math.sin(t * 2.5) * 0.04 + head_rot * -0.8
    p.part(lambda c: blob(c, 30, -162, 20, n=7, wobble=0.1, seed=21, sx=0.8, sy=1.2), PAL["caramel"], seed="pm_fear")
    # yaka
    p.part(lambda c: (ellipse(c, 28, -96, 13, 28, -0.45)), PAL["collar"], seed="pm_collar")
    p.part(lambda c: circle(c, 36, -70, 8), PAL["gold"], seed="pm_tag")
    p.part(lambda c: blob(c, 56, -126, 48, n=9, wobble=0.05, seed=31, sx=1.05, sy=0.95), PAL["dog"], seed="pm_head")
    p.part(lambda c: ellipse(c, 60, -136, 18, 16, 0.2), PAL["caramel"], alpha=0.9, seed="pm_patch", lw=0.5)
    p.part(lambda c: ellipse(c, 88, -110, 29, 21, -0.1), PAL["dog_muzzle"], seed="pm_muzzle")
    p.part(lambda c: ellipse(c, 74, -112, 9, 6), PAL["cheek"], alpha=0.45, line=False, seed="pm_cheek")
    # gözler
    cross = st.get("cross", 0.0)
    blink = st.get("blink", 0.0)
    happy = st.get("happy", 0.0)
    squint = clamp(-sneeze * 1.5)
    edy = st.get("eye_dy", 0.0)
    for (ex, ey, rx, ry, nm) in ((62, -137, 8, 10, "n"), (90, -140, 6.5, 9, "f")):
        if happy > 0.5 or squint > 0.6:
            p.stroke(lambda c, ex=ex, ey=ey: (c.move_to(ex - 7, ey + 2), c.curve_to(ex - 3, ey - 7, ex + 3, ey - 7, ex + 7, ey + 2)),
                     PAL["eye"], width=4.0)
        elif cross > 0.5:
            p.part(lambda c, ex=ex, ey=ey, rx=rx: circle(c, ex, ey, rx + 4), PAL["white"], seed=f"pm_scl{nm}", lw=0.8)
            dxp = 3.5 if nm == "n" else -3.0
            p.part(lambda c, ex=ex, ey=ey, dxp=dxp: circle(c, ex + dxp, ey + 3.5, 5), PAL["eye"], line=False, seed=f"pm_pup{nm}")
        elif blink > 0.75:
            p.stroke(lambda c, ex=ex, ey=ey: (c.move_to(ex - 7, ey), c.curve_to(ex - 3, ey + 5, ex + 3, ey + 5, ex + 7, ey)),
                     PAL["eye"], width=3.6)
        else:
            ey2 = ey + edy * 2.5
            p.part(lambda c, ex=ex, ey=ey2, rx=rx, ry=ry: ellipse(c, ex, ey, rx, ry * (1 - blink)), PAL["eye"], line=False, seed=f"pm_eye{nm}")
            p.part(lambda c, ex=ex, ey=ey2: circle(c, ex + 2.5, ey - 4, 3.2), PAL["white"], line=False, seed=f"pm_hl{nm}", wet=0.3)
    # burun
    p.part(lambda c: blob(c, 113, -118, 11, n=6, wobble=0.05, seed=41, sx=1.1, sy=0.8), st.get("nose_color", PAL["nose"]), seed="pm_nose", lw=0.5)
    p.part(lambda c: ellipse(c, 110, -122, 4, 2.5, -0.3), PAL["white"], alpha=0.8, line=False, seed="pm_nosehl", wet=0.2)
    nose_dev = ctx.user_to_device(114, -124)
    collar_dev = ctx.user_to_device(30, -92)
    # ağız
    mo = st.get("mouth", 0.0)
    if mo > 0.07:
        p.part(lambda c: (c.move_to(78, -98), c.curve_to(82, -98 + 22 * mo + 4, 104, -98 + 22 * mo + 4, 108, -102), c.close_path()),
               PAL["mouth"], seed="pm_mouth", lw=0.6)
        p.part(lambda c: ellipse(c, 93, -98 + 16 * mo, 8, 5 + 4 * mo), PAL["tongue"], line=False, seed="pm_tongue")
    else:
        p.stroke(lambda c: (c.move_to(112, -108), c.curve_to(110, -100, 100, -96, 92, -100)), PAL["eye"], width=3.2)
        p.stroke(lambda c: (c.move_to(92, -100), c.curve_to(88, -96, 82, -96, 78, -101)), PAL["eye"], width=3.2)
    # yakın kulak (sarkık, ikincil hareket)
    ctx.save()
    ctx.translate(36, -158)
    ctx.rotate(ear_sw + 0.15)

    def ear(c):
        c.move_to(-4, -4)
        c.curve_to(14, -10, 20, 18, 12, 46)
        c.curve_to(8, 60, -12, 60, -14, 44)
        c.curve_to(-18, 20, -16, 2, -4, -4)
        c.close_path()

    p.part(ear, PAL["caramel"], seed="pm_ear")
    ctx.restore()
    ctx.restore()
    ctx.restore()
    return {"nose": nose_dev, "collar": collar_dev}


# ---------------------------------------------------------------- KELEBEK
def draw_butterfly(p, x, y, s, flap, rot=0.0, col=None, edge=None):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    k = 0.18 + 0.82 * abs(math.cos(flap))
    for side in (-1, 1):
        ctx.save()
        ctx.scale(side * k, 1)
        p.part(lambda c: (c.move_to(2, -2), c.curve_to(10, -46, 52, -52, 50, -22), c.curve_to(48, -4, 22, 2, 2, -2), c.close_path()),
               col or PAL["bf_wing"], seed=f"bf_uw{side}")
        p.part(lambda c: (c.move_to(2, 2), c.curve_to(30, 0, 40, 26, 26, 34), c.curve_to(14, 40, 4, 22, 2, 2), c.close_path()),
               lighten_c(edge or PAL["bf_edge"], 0.15), seed=f"bf_lw{side}")
        p.part(lambda c: (circle(c, 38, -30, 7), circle(c, 24, 22, 5)), edge or PAL["bf_edge"], line=False, seed=f"bf_sp{side}")
        ctx.restore()
    p.part(lambda c: capsule(c, 0, -14, 0, 20, 4.5, 3.5), PAL["bf_body"], seed="bf_body", lw=0.4)
    p.stroke(lambda c: (c.move_to(-1, -16), c.curve_to(-4, -28, -10, -34, -12, -36), c.move_to(1, -16), c.curve_to(4, -28, 10, -34, 12, -36)),
             PAL["bf_body"], width=2.2)
    p.part(lambda c: (circle(c, -12, -37, 3), circle(c, 12, -37, 3)), PAL["bf_body"], line=False, seed="bf_ant")
    ctx.restore()


# ---------------------------------------------------------------- ÇİÇEK
def draw_flower(p, x, y, s, color, center=None, sway=0.0, pop=1.0, seed="fl"):
    ctx = p.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    tx, ty = sway * 12, -120
    p.part(lambda c: capsule(c, 0, 0, tx, ty, 4.5, 4), PAL["stem"], seed=f"{seed}st", lw=0.6)
    p.part(lambda c: (ellipse(c, -16, -40, 18, 8, 0.5), ellipse(c, 16 + sway * 3, -64, 18, 8, -0.5)), PAL["leaf"], seed=f"{seed}lf")
    ctx.translate(tx, ty)
    ctx.scale(pop, pop)
    ctx.rotate(sway * 0.2)
    for i in range(6):
        a = i * math.pi / 3
        p.part(lambda c, a=a: ellipse(c, math.cos(a) * 22, math.sin(a) * 22, 19, 13, a), color, seed=f"{seed}p{i}")
    p.part(lambda c: circle(c, 0, 0, 13), center or PAL["ribbon"], seed=f"{seed}c")
    ctx.restore()


def star(ctx, cx, cy, r, n=5, inner=0.45, rot=-math.pi / 2):
    ctx.new_sub_path()
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / n
        if i == 0:
            ctx.move_to(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
        else:
            ctx.line_to(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
    ctx.close_path()


def draw_sparkles(p, x, y, t_rel, color=(1.0, 0.85, 0.25), n=7, radius=120, seed=0):
    """t_rel: 0..1 patlamanın ilerleyişi."""
    if t_rel <= 0 or t_rel >= 1:
        return
    from .core import hash01
    for i in range(n):
        a = 2 * math.pi * i / n + hash01(seed, i) * 0.6
        d = radius * (0.3 + 0.9 * t_rel) * (0.7 + 0.5 * hash01(seed, i, "d"))
        sx_, sy_ = x + math.cos(a) * d, y + math.sin(a) * d
        sz = 16 * math.sin(math.pi * t_rel) * (0.7 + 0.6 * hash01(seed, i, "s"))
        if sz < 1:
            continue
        p.glow(sx_, sy_, sz * 2.2, color, 0.35)
        p.part(lambda c, sx_=sx_, sy_=sy_, sz=sz, i=i: star(c, sx_, sy_, sz, rot=t_rel * 2 + i), color, seed=f"spk{seed}{i}", lw=0.5)
