"""Ela ile Pamuk — Örnek Bölüm Kesiti: "Renkli Kelebek"  (≈76 sn)

Yönetmen / senarist / tasarımcı notları docs/ klasöründedir. Bu dosya bölümün
"çekim senaryosu"dur: kamera, oyunculuk, diyalog ve efekt zamanlamaları burada.

Kullanım:
    python3 ep01_renkli_kelebek.py --style suluboya   [--start 0 --end 76] [--workers 4] [--scale 1.0]
    stiller: suluboya | kagit | yumusak3b | kece
"""
import argparse
import math
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import cairo
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.core import (W, H, FPS, GROUND_Y, Track, Steps, Path2D, clamp, lerp, smooth, ease_io, ease_out_back,
                         ease_out_elastic, window, hash01, circle, ellipse, blob, noise_patch, hexrgb)
from engine.styles import Canvas, PAINTERS, PAPER, post_process
from engine.characters import (PAL, draw_ela, draw_pamuk, draw_butterfly, draw_flower, draw_sparkles,
                               ela_arm_pose, blend_pose, star)
from engine import world

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_DIR = os.path.join(ROOT, "assets", "vo")
DURATION = 76.0

# ============================================================== DİYALOG (seslendirme)
# (kimlik, başlangıç sn, konuşan, metin, konuşma hızı)
CUES = [
    ("n1", 5.6, "anlatici", "Günaydın! Bu, Ela.", 1.15),
    ("n2", 9.4, "anlatici", "Bu da Ela'nın en iyi arkadaşı... Pamuk!", 1.15),
    ("p1", 12.5, "pamuk", "Hav! Hav!", 1.0),
    ("e1", 15.0, "ela", "Bak Pamuk! Bir kelebek!", 1.05),
    ("n3", 19.6, "anlatici", "Kelebek ne renk?", 1.15),
    ("n3b", 24.0, "anlatici", "Sarı! Evet, sarı!", 1.1),
    ("e2", 27.6, "ela", "Hadi Pamuk! Kelebeği takip edelim!", 1.05),
    ("n4", 35.6, "anlatici", "Bak! Kırmızı bir çiçek!", 1.1),
    ("n5", 40.8, "anlatici", "Bir de... mavi çiçek!", 1.1),
    ("n6", 47.0, "anlatici", "Kelebek nereye kondu?", 1.15),
    ("n6b", 51.0, "anlatici", "Pamuk'un burnuna!", 1.1),
    ("p2", 53.5, "pamuk", "Hap... hapşuuu!", 1.0),
    ("e4", 55.6, "ela", "Hi hi hi hi!", 1.0),
    ("e3", 60.0, "ela", "Hoşça kal kelebek!", 1.05),
    ("n7", 64.6, "anlatici", "Ela ile Pamuk... en iyi iki arkadaş!", 1.15),
]

# ============================================================== KAMERA
CAM = Track([
    (0.0, (960, 140, 1.0)), (1.5, (960, 140, 1.0)), (5.6, (960, 540, 1.0), "io"),
    (9.6, (960, 540, 1.0)), (11.0, (800, 600, 1.22)), (13.9, (830, 590, 1.22)),
    (15.0, (1000, 540, 1.0)), (17.6, (1000, 540, 1.0)), (19.3, (1245, 520, 1.85)),
    (26.0, (1255, 520, 1.85)), (27.3, (1060, 540, 1.0)), (30.6, (1100, 540, 1.0)),
    (43.5, (3450, 540, 1.0), "lin"), (45.2, (3280, 560, 1.0)), (46.7, (3180, 700, 2.1)),
    (54.2, (3185, 700, 2.1)), (55.6, (3260, 560, 1.04)), (59.0, (3300, 540, 1.0)),
    (61.0, (3320, 520, 1.0)), (63.5, (3260, 560, 1.0)), (67.5, (3245, 650, 1.32)), (76.0, (3245, 650, 1.32)),
])

# ============================================================== OYUNCULAR
ELA_X = Track([(0, -150), (3.0, -150), (7.0, 700, "lin"), (8.0, 820, "out"), (30.6, 820),
               (31.4, 900, "in"), (43.4, 3230, "lin"), (44.2, 3300, "out")])
PAMUK_X = Track([(0, -320), (8.6, -320), (11.4, 560, "out"), (30.8, 560), (31.6, 650, "in"),
                 (43.6, 3050, "lin"), (44.4, 3120, "out"), (61.8, 3120), (62.4, 3190, "io")])
ELA_POSE = Steps([(0, "idle"), (8.1, "wave"), (9.6, "idle"), (15.1, "point"), (18.2, "idle"), (24.15, "cheer"),
                  (26.0, "idle"), (27.75, "cheer"), (29.0, "point"), (30.6, "idle"), (47.0, "think"),
                  (51.15, "cheer"), (52.5, "idle"), (55.5, "laugh"), (57.3, "idle"), (59.8, "wave"),
                  (61.9, "idle"), (62.4, "hug")], blend=0.3)
ELA_LOOK = Track([(0, 0.35), (7.9, 0.35), (8.3, 0.0), (9.6, 0.0), (10.1, -0.45), (12.8, -0.45), (14.9, 0.5),
                  (27.4, 0.5), (27.9, 0.3), (44.4, 0.3), (45.4, -0.5), (55.2, -0.5), (55.6, 0.0), (57.2, 0.0),
                  (58.0, 0.55), (61.3, 0.55), (61.7, 0.45)])
ELA_FACING = [(0, 1), (61.75, -1)]
HOPS_ELA = [24.2, 27.85, 51.2]
HOPS_PAMUK = [11.7, 24.3, 51.25, 62.45, 63.05]

BUTTERFLY = Path2D([
    (13.4, 2150, 260), (15.0, 1600, 380), (16.6, 1260, 520), (29.4, 1260, 520), (31.0, 1500, 480),
    (33.0, 1850, 600), (35.5, 2250, 500), (38.0, 2650, 610), (40.5, 3000, 520), (43.0, 3350, 560),
    (44.6, 3380, 640), (45.6, 3300, 700),
])
BUTTERFLY_AFTER = Path2D([(54.2, 3236, 742), (54.9, 3300, 600), (56.8, 3460, 470), (59.0, 3560, 420),
                          (61.4, 3700, 330), (64.5, 4350, 60)])
LAND_T0, LAND_T1 = 45.4, 46.2     # konma
TAKEOFF = 54.15                   # hapşırık

RED_FLOWER = (2080, 846, (0.93, 0.30, 0.30), 35.8)
BLUE_FLOWER = (3000, 846, (0.36, 0.55, 0.95), 41.0)
SPARKLES = [(24.0, "bf"), (35.85, "red"), (41.05, "blue"), (51.05, "nose")]
HEARTS_T = (62.7, 66.5)
IRIS = (68.0, 69.6, 69.9, 70.7)   # kapan başla/bitir, aç başla/bitir
END_CARD = 69.6


# ============================================================== yardımcılar
def hop(t, times, h=42, d=0.42):
    v = 0.0
    for t0 in times:
        if t0 <= t < t0 + d:
            v = max(v, h * math.sin(math.pi * (t - t0) / d))
    return v


def blink(t, seed, period=3.4):
    k = math.floor(t / period)
    for kk in (k - 1, k):
        start = kk * period + hash01(seed, kk) * 1.8
        if 0 <= t - start < 0.16:
            return math.sin(math.pi * (t - start) / 0.16)
    return 0.0


def facing_at(t, keys):
    f = keys[0][1]
    for k in keys:
        if t >= k[0]:
            f = k[1]
    return f


def _gait_tables(track, t_end, walk_v, run_v, stride_w, stride_r):
    dt = 1.0 / 240
    ts = np.arange(0, t_end + 1, dt)
    xs = np.array([track(t) for t in ts])
    v = np.abs(np.gradient(xs, dt))
    v = np.convolve(v, np.ones(24) / 24, mode="same")
    gait = np.where(v < walk_v, v / walk_v, 1 + np.clip((v - walk_v) / (run_v - walk_v), 0, 1))
    gait = np.where(v < 8, 0, gait)
    stride = np.where(gait > 1, lerp(stride_w, stride_r, np.clip(gait - 1, 0, 1)), stride_w)
    phase = np.cumsum(v / stride * 2 * math.pi * dt)
    return ts, gait, phase


GAIT = {}


def gait_at(name, t):
    if name not in GAIT:
        if name == "ela":
            GAIT[name] = _gait_tables(ELA_X, DURATION, 150, 230, 150, 210)
        else:
            GAIT[name] = _gait_tables(PAMUK_X, DURATION, 120, 220, 120, 190)
    ts, g, ph = GAIT[name]
    i = int(clamp(t * 240, 0, len(ts) - 1))
    return float(g[i]), float(ph[i])


ENV = {}


def load_envelopes():
    for cid, start, who, _, _ in CUES:
        path = os.path.join(VO_DIR, f"{cid}.wav")
        if not os.path.exists(path):
            continue
        with wave.open(path) as w:
            sr = w.getframerate()
            data = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        hop_ = sr // (FPS * 2)
        n = len(data) // hop_
        rms = np.sqrt(np.mean(data[:n * hop_].reshape(n, hop_) ** 2, axis=1))
        rms = rms / (np.percentile(rms, 95) + 1e-6)
        ENV[cid] = (start, who, np.clip(rms, 0, 1.2), FPS * 2)


def mouth(who, t):
    best = 0.0
    for cid, (start, w, env, rate) in ENV.items():
        if w != who:
            continue
        i = int((t - start) * rate)
        if 0 <= i < len(env):
            v = env[i]
            best = max(best, clamp((v - 0.12) / 0.7) ** 0.8)
    return best


def speaking(who, t):
    return any(w == who and 0 <= (t - s) * r < len(e) for (s, w, e, r) in ENV.values())


# ============================================================== SAHNE DURUMU
def butterfly_pos(t, nose_world):
    if t < LAND_T0:
        x, y = BUTTERFLY(t)
        x += 38 * math.sin(t * 1.4) + 14 * math.sin(t * 3.1)
        y += 26 * math.sin(t * 2.8) + 10 * math.cos(t * 4.3)
        return x, y, False
    if t < TAKEOFF:
        bx, by = BUTTERFLY(LAND_T0)
        u = smooth((t - LAND_T0) / (LAND_T1 - LAND_T0))
        nx, ny = nose_world
        nx, ny = nx + 2, ny - 30
        return lerp(bx, nx, u), lerp(by, ny, u), u >= 1
    x, y = BUTTERFLY_AFTER(t)
    x += 30 * math.sin(t * 1.6)
    y += 20 * math.sin(t * 3.0)
    return x, y, False


def cam_at(t):
    cx, cy, z = CAM(t)
    w = window(t, 31.6, 43.0, fade=1.0)
    if w > 0:
        cx = lerp(cx, ELA_X(t) + 250, w)
    # hapşırık sarsıntısı
    if TAKEOFF <= t < TAKEOFF + 0.45:
        k = 1 - (t - TAKEOFF) / 0.45
        cx += math.sin(t * 90) * 7 * k
        cy += math.cos(t * 77) * 5 * k
    return cx, cy, z


def ela_state(t, bf):
    g, ph = gait_at("ela", t)
    a, b, u = ELA_POSE.blend(t)
    arms = blend_pose(ela_arm_pose(a, t), ela_arm_pose(b, t), u)
    f = facing_at(t, ELA_FACING)
    x = ELA_X(t)
    st = dict(facing=f, phase=ph, gait=g, arms=arms, look=ELA_LOOK(t))
    st["blink"] = blink(t, "ela")
    st["mouth"] = mouth("ela", t)
    st["jump"] = hop(t, HOPS_ELA)
    if bf is not None and 14.5 < t < 61.6:
        dx, dy = bf[0] - x, bf[1] - (GROUND_Y - 250)
        st["eye_dx"] = clamp(dx / 300, -1, 1)
        st["eye_dy"] = clamp(dy / 300, -1, 1)
    st["brow"] = max(window(t, 15.0, 16.4, 0.3), window(t, 46.0, 48.0, 0.4) * 0.7)
    st["happy"] = 1.0 if (55.6 < t < 57.1 or 62.7 < t < 69 or 24.1 < t < 24.9) else 0.0
    st["tilt"] = 0.1 * window(t, 47.2, 50.8, 0.4) + 0.05 * math.sin(t * 9) * window(t, 55.6, 57.0, 0.2)
    st["smile"] = 1.0 - 0.5 * window(t, 47.2, 50.8, 0.4)
    if f < 0 and t > 62.4:
        st["look"] = 0.45
    return x, st


def pamuk_state(t, bf):
    g, ph = gait_at("pamuk", t)
    x = PAMUK_X(t)
    st = dict(facing=1, phase=ph, gait=g)
    st["blink"] = blink(t, "pamuk", 3.0)
    m = mouth("pamuk", t)
    if g > 0.8 and m < 0.1:
        m = 0.35 + 0.08 * math.sin(t * 13)  # koşarken dil dışarıda solur
    st["mouth"] = m
    st["jump"] = hop(t, HOPS_PAMUK, h=48, d=0.4)
    st["wag"] = 1.0 + 0.8 * max(window(t, 11.6, 14.2, 0.3), window(t, 24.0, 26.0), window(t, 31, 44, 0.5),
                                window(t, 51.0, 52.4), window(t, 55.6, 60), window(t, 62.3, 76))
    st["look_up"] = 0.6 * window(t, 14.5, 30.5, 0.5) + 0.3 * window(t, 55.0, 61.5, 0.5)
    st["eye_dy"] = -0.8 * window(t, 14.5, 30.5, 0.5)
    st["tilt"] = 0.16 * window(t, 15.6, 17.4, 0.3) - 0.1 * window(t, 46.6, 52.4, 0.3)
    st["cross"] = 1.0 if 46.3 < t < 52.6 else 0.0
    if 52.6 <= t < TAKEOFF:
        st["sneeze"] = -smooth((t - 52.6) / 1.1)
    elif TAKEOFF <= t < TAKEOFF + 0.5:
        k = (t - TAKEOFF) / 0.5
        st["sneeze"] = math.sin(math.pi * min(1, k * 2.2)) * (1 - k) + (-(1 - k) * 0.2)
    st["happy"] = 1.0 if (12.4 < t < 14.0 or 62.6 < t < 69 or 56 < t < 57.2 and st.get("sneeze", 0) == 0) else 0.0
    return x, st


# ============================================================== ÇİZİM
def heart_path(c, x, y, r):
    c.new_sub_path()
    c.move_to(x, y + r * 1.1)
    c.curve_to(x - r * 1.6, y, x - r * 0.9, y - r * 1.3, x, y - r * 0.4)
    c.curve_to(x + r * 0.9, y - r * 1.3, x + r * 1.6, y, x, y + r * 1.1)
    c.close_path()


def draw_title(p, alpha, pop, title, subtitle, y=330, sub_dy=135, size=150):
    if alpha <= 0.01:
        return
    ctx = p.ctx
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.scale(pop, pop)
    ctx.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    for text, sz, col, dy in ((title, size, PAL["dress"], 0), (subtitle, size * 0.46, hexrgb("#4E8FD6"), sub_dy)):
        if not text:
            continue
        ctx.set_font_size(sz)
        ext = ctx.text_extents(text)
        x0 = -ext.width / 2 - ext.x_bearing

        def tp(c, x0=x0, dy=dy, text=text):
            c.move_to(x0, dy)
            c.text_path(text)

        p.part(tp, col, alpha=alpha, seed=f"title{dy}", lw=1.3)
    ctx.restore()


def iris_alpha(t, center):
    """Çember geçişi (iris). Dışarıda kalan alanın örtücülüğünü döndürür (düşük çözünürlükte hesaplanır)."""
    c0, c1, o0, o1 = IRIS
    if t < c0 or t > o1:
        return None
    if t < c1:
        r = lerp(1500, 0, ease_io((t - c0) / (c1 - c0)) ** 0.85)
        cx, cy = center
    elif t < o0:
        r = 0
        cx, cy = W / 2, H / 2
    else:
        r = lerp(0, 1500, ease_io((t - o0) / (o1 - o0)))
        cx, cy = W / 2, H / 2
    sw, sh = W // 4, H // 4
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    d = np.sqrt((xx * 4 - cx) ** 2 + (yy * 4 - cy) ** 2) - r
    d += (noise_patch("blot", 0, 0, sh, sw) - 0.5) * 60
    a = np.clip(d / 10 + 0.5, 0, 1)
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]


def composite(dst, src_u8):
    s = src_u8.astype(np.float32) * (1 / 255.0)
    a = s[..., 3:4]
    dst *= (1 - a)
    dst += s[..., :3]


def render_end_card(style, t, frame):
    cv = Canvas()
    p = PAINTERS[style](cv, t=t, scale=1.0, frame=frame)
    sky = (hexrgb("#BFE0F5"), hexrgb("#FFF4E0"), 0, 1080)
    p.part(lambda c: c.rectangle(0, 0, W, H), None, grad=sky, line=False, flat=True, seed="ec_bg", wet=1.4)
    p.part(lambda c: blob(c, W / 2, 1180, 900, n=12, wobble=0.05, seed=3, sy=0.42), hexrgb("#9FD27A"), seed="ec_hill", flat=True, lw=0.6)
    u = t - END_CARD
    pop = ease_out_back(u / 0.8)
    draw_title(p, clamp(u / 0.5), max(pop, 0.01), "Ela ile Pamuk", "Yakında yeni maceralarda!", y=250, sub_dy=130)
    draw_flower(p, 300, 1000, 1.3, (0.93, 0.30, 0.30), sway=math.sin(t * 1.5) * 0.3, seed="ecf1")
    draw_flower(p, 1620, 1000, 1.3, (0.36, 0.55, 0.95), sway=math.sin(t * 1.3 + 1) * 0.3, seed="ecf2")
    draw_pamuk(p, 760, 960, 1.25, dict(wag=2.0, happy=1.0 if (t % 2.6) > 1.3 else 0.0, mouth=0.3, jump=hop(t, [71.0, 73.0], 40)))
    draw_ela(p, 1150, 960, 1.25, dict(arms=ela_arm_pose("wave", t), look=0.0, blink=blink(t, "ela2"),
                                      mouth=0.0, jump=hop(t, [71.5, 73.5], 30)))
    bx, by = 1180 + 200 * math.sin(t * 0.9), 560 + 60 * math.sin(t * 1.8)
    draw_butterfly(p, bx, by, 1.2, t * 13)
    cv.surface.flush()
    return cv.arr


def render_frame(i, style, layers):
    t = tc = i / FPS
    if style == "kece":  # stop-motion: oyuncular saniyede 12 poz, kamera akıcı
        t = math.floor(t * 12) / 12
    if t >= END_CARD:
        rgb = np.empty((H, W, 3), np.float32)
        rgb[:] = PAPER[::-1]
        composite(rgb, render_end_card(style, t, i))
        ia = iris_alpha(t, (W / 2, H / 2))
        if ia is not None:
            rgb = rgb * (1 - ia) + PAPER[::-1][None, None, :] * ia
        return (post_process(style, rgb) * 255 + 0.5).astype(np.uint8)

    cam = cam_at(tc)
    cx, cy, z = cam
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = PAPER[::-1]
    for L in layers:
        if L["name"] == "front":
            continue
        drift = t * 9 if L["name"] == "clouds" else 0.0
        M, zl = world.layer_matrix(L["p"], cam, drift)
        warped = cv2.warpAffine(L["img"], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        composite(rgb, warped)
    if z > 1.05:  # yakın çekimde alan derinliği
        rgb = cv2.GaussianBlur(rgb, (0, 0), (z - 1) * 2.2)

    dyn = Canvas()
    p = PAINTERS[style](dyn, t=t, scale=z, frame=i)
    ctx = p.ctx
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    cam_m = ctx.get_matrix()
    inv = cairo.Matrix(*cam_m)
    inv.invert()

    ex, est = ela_state(t, None)
    px, pst = pamuk_state(t, None)
    # gölgeler
    shadow_col = hexrgb("#6E7FA6")
    for sx_, j, w_ in ((ex, est["jump"], 62), (px + 10, pst["jump"], 92)):
        k = 1 - clamp(j / 120) * 0.5
        p.part(lambda c, sx_=sx_, w_=w_, k=k: ellipse(c, sx_, GROUND_Y + 4, w_ * k, 13 * k), shadow_col, alpha=0.28,
               line=False, seed=f"sh{w_}", wet=0.6)
    # isimlendirilen çiçekler
    for fx, fy, col, tn in (RED_FLOWER, BLUE_FLOWER):
        if abs(fx - cx) < W / z:
            pop = 1.0 + 0.35 * math.sin(math.pi * clamp((t - tn) / 0.35)) * (t < tn + 0.35) + \
                  (0.12 * (1 - ease_out_elastic((t - tn - 0.35) / 1.2)) if t > tn + 0.35 else 0)
            draw_flower(p, fx, fy, 1.15, col, sway=math.sin(t * 1.6 + fx) * 0.35, pop=pop, seed=f"nf{fx}")

    # Pamuk (önce, Ela'nın arkasında)
    anchors = draw_pamuk(p, px, GROUND_Y, 0.95, pst)
    nose_world = inv.transform_point(*anchors["nose"])
    bfx, bfy, landed = butterfly_pos(t, nose_world)
    # gözler kelebeği takip etsin
    ex, est = ela_state(t, (bfx, bfy))
    draw_ela(p, ex, GROUND_Y, 1.0, est)

    # kelebek
    if 13.3 < t < 64.6:
        flap = t * (3.0 if landed else 15.0)
        if landed:
            flap = 0.9 + 0.6 * math.sin(t * 2.4)
        rot = 0.15 * math.sin(t * 2.0) if not landed else -0.1
        if 21.0 < t < 24.0:
            p.glow(bfx, bfy, 110 + 15 * math.sin(t * 6), (1.0, 0.92, 0.45), 0.45)
        draw_butterfly(p, bfx, bfy, 0.85, flap, rot)
    if 48.6 < t < 51.2:
        p.glow(nose_world[0], nose_world[1], 60 + 8 * math.sin(t * 6), (1.0, 0.92, 0.45), 0.4)

    # hapşırık bulutu
    if TAKEOFF <= t < TAKEOFF + 0.9:
        k = (t - TAKEOFF) / 0.9
        for j in range(5):
            a = -0.6 + j * 0.3
            d = 30 + 120 * ease_io(k) * (0.7 + 0.5 * hash01(j))
            r = (10 + 16 * k) * (1 - k * 0.6)
            p.part(lambda c, a=a, d=d, r=r: circle(c, nose_world[0] + math.cos(a) * d, nose_world[1] + math.sin(a) * d * 0.6, r),
                   (1, 1, 1), alpha=1 - k, seed=f"pf{j}", lw=0.5)

    # ışıltılar
    for ts_, what in SPARKLES:
        u = (t - ts_) / 1.1
        if 0 < u < 1:
            if what == "bf":
                sx_, sy_ = bfx, bfy
            elif what == "red":
                sx_, sy_ = RED_FLOWER[0], RED_FLOWER[1] - 140
            elif what == "blue":
                sx_, sy_ = BLUE_FLOWER[0], BLUE_FLOWER[1] - 140
            else:
                sx_, sy_ = nose_world
            draw_sparkles(p, sx_, sy_, u, n=8, radius=130 if what != "nose" else 70, seed=what)
    # kalpler
    if HEARTS_T[0] < t < HEARTS_T[1] + 2:
        for j in range(7):
            t0 = HEARTS_T[0] + j * 0.55
            u = (t - t0) / 2.2
            if 0 < u < 1:
                hx = (ex + px + 60) / 2 + math.sin(u * 6 + j) * 40 + (hash01(j) - 0.5) * 120
                hy = GROUND_Y - 300 - u * 260
                r = 14 * (0.6 + 0.4 * math.sin(math.pi * u)) * (0.8 + 0.4 * hash01(j, 2))
                p.part(lambda c, hx=hx, hy=hy, r=r: heart_path(c, hx, hy, r), hexrgb("#F2575B"), alpha=1 - u ** 3, seed=f"hrt{j}", lw=0.6)

    dyn.surface.flush()
    composite(rgb, dyn.arr)
    for L in layers:
        if L["name"] == "front":
            M, _ = world.layer_matrix(L["p"], cam)
            composite(rgb, cv2.warpAffine(L["img"], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT))

    # başlık
    if t < 6.0:
        a = window(t, 1.0, 4.6, 0.6)
        if a > 0:
            ov = Canvas()
            po = PAINTERS[style](ov, t=t, scale=1.0, frame=i)
            pop = ease_out_back((t - 0.4) / 0.9)
            draw_title(po, a, max(pop, 0.01), "Ela ile Pamuk", "Renkli Kelebek")
            ov.surface.flush()
            composite(rgb, ov.arr)

    # iris
    scr = cam_m.transform_point((ex + px) / 2 + 40, GROUND_Y - 170)
    ia = iris_alpha(t, scr)
    if ia is not None:
        rgb = rgb * (1 - ia) + PAPER[::-1][None, None, :] * ia
    return (post_process(style, rgb) * 255 + 0.5).astype(np.uint8)



# ============================================================== SES / MÜZİK
def build_audio(path):
    from engine import audio as A
    rng = np.random.default_rng(7)
    music = A.Bus(DURATION)
    sfx = A.Bus(DURATION)
    vo = A.Bus(DURATION)
    BEAT = 0.6
    BAR = 4 * BEAT
    CHORDS = {"C": ("C3", ["C4", "E4", "G4"]), "G": ("G2", ["B3", "D4", "G4"]), "Am": ("A2", ["A3", "C4", "E4"]),
              "F": ("F2", ["F3", "A3", "C4"])}
    PROG = ["C", "G", "Am", "F", "C", "F", "G", "C"]
    MELODY = [
        [(0, "C5", 1), (1, "E5", 1), (2, "G5", 1), (3, "E5", 1)],
        [(0, "D5", 1), (1, "G5", 1), (2, "B4", 1), (3, "D5", 1)],
        [(0, "C5", 1), (1, "E5", 1), (2, "A5", 1.5), (3.5, "G5", 0.5)],
        [(0, "F5", 1), (1, "E5", 1), (2, "D5", 2)],
        [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "G5", 1), (2, "G5", 1), (3, "C6", 1)],
        [(0, "A5", 1), (1, "F5", 1), (2, "A5", 1), (3, "C6", 1)],
        [(0, "B5", 1), (1, "A5", 1), (2, "G5", 1), (3, "F5", 1)],
        [(0, "E5", 1), (1, "D5", 1), (2, "C5", 2)],
    ]
    hz = lambda name: A.midi_hz(A.n(name))

    def theme_bar(t0, b, energy=0):
        ch = PROG[b % 8]
        root, tones = CHORDS[ch]
        music.add(t0, A.pad([hz(x) for x in tones], BAR * 0.95, attack=0.4, release=0.6), 0.10)
        for k, (bt, note, d) in enumerate(MELODY[b % 8]):
            if energy:
                music.add(t0 + bt * BEAT, A.xylo(hz(note)), 0.30, pan=0.15)
                if d >= 1:
                    music.add(t0 + (bt + 0.5) * BEAT, A.xylo(hz(note)), 0.16, pan=0.15)
            else:
                music.add(t0 + bt * BEAT, A.kalimba(hz(note)), 0.34, pan=0.1)
        if energy:
            for bt in range(4):
                nn = A.n(root) + (12 if bt % 2 else 0)
                music.add(t0 + bt * BEAT, A.bass(A.midi_hz(nn), 0.45, 0.2), 0.42, pan=-0.1)
            for e in range(8):
                music.add(t0 + e * BEAT / 2, A.shaker(), 0.5 if e % 2 else 0.25, pan=0.35)
        else:
            music.add(t0, A.bass(hz(root), 1.0, 0.4), 0.38, pan=-0.1)
            music.add(t0 + 2 * BEAT, A.bass(A.midi_hz(A.n(root) + 7), 1.0, 0.4), 0.30, pan=-0.1)
            for e in (1, 3):
                music.add(t0 + e * BEAT, A.shaker(), 0.18, pan=0.35)

    # giriş
    music.add(0.0, A.pad([hz("C4"), hz("E4"), hz("G4")], 2.6), 0.16)
    music.add(2.6, A.pad([hz("A3"), hz("C4"), hz("F4")], 2.6), 0.16)
    for k, nn in enumerate(["C5", "E5", "G5", "C6", "A4", "C5", "F5", "A5"]):
        music.add(0.3 + k * 0.62, A.kalimba(hz(nn), 1.6), 0.26)
    # tema A
    for b in range(6):
        theme_bar(5.4 + b * BAR, b)
    # interaktif soru (müzik kutusu, sakin)
    music.add(19.8, A.pad([hz("C4"), hz("E4"), hz("G4"), hz("B4")], 4.0, attack=0.8), 0.12)
    for tt, nn in ((21.2, "E5"), (21.8, "G5"), (22.4, "A5"), (23.2, "G5")):
        music.add(tt, A.glock(hz(nn)), 0.16)
    for b in range(2):
        theme_bar(24.6 + b * BAR, 4 + b)
    for k, nn in enumerate(["G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5"]):
        music.add(29.4 + k * 0.15, A.xylo(hz(nn)), 0.25)
    # kovalamaca
    for b in range(6):
        theme_bar(30.6 + b * BAR, b, energy=1)
    # parmak ucu (gerilim ama sevimli)
    tip = ["A3", "C4", "E4", "C4", "F3", "A3", "C4", "A3"]
    music.add(45.0, A.pad([hz("A3"), hz("C4"), hz("E4")], 4.6), 0.10)
    music.add(49.6, A.pad([hz("F3"), hz("A3"), hz("C4")], 3.6), 0.10)
    for k in range(14):
        tt = 45.0 + k * BEAT
        if 47.0 <= tt < 48.8:
            continue
        music.add(tt, A.bass(hz(tip[k % 8]) * 2, 0.18, 0.06), 0.22, pan=(-0.3 if k % 2 else 0.3))
    for tt, nn in ((49.0, "E5"), (49.6, "G5"), (50.2, "A5")):
        music.add(tt, A.glock(hz(nn)), 0.14)
    music.add(52.6, A.pad([hz("G3"), hz("B3"), hz("D4"), hz("F4")], 1.6, attack=1.2, release=0.4), 0.14)
    # tema dönüşü
    for b in range(5):
        theme_bar(55.2 + b * BAR, b)
    theme_bar(67.2, 6)
    theme_bar(67.2 + BAR, 7)
    music.add(72.0, A.pad([hz("C4"), hz("E4"), hz("G4"), hz("C5")], 3.0, attack=0.3, release=1.0), 0.16)
    music.add(72.0, A.bass(hz("C3"), 2.5, 1.0), 0.35)
    music.add(72.0, A.kalimba(hz("C6"), 3.0), 0.3)

    # efektler
    for tt in (0.5, 2.2, 3.9, 6.8, 9.0, 57.5, 59.0, 65.5):
        sfx.add(tt, A.chirp_bird(int(tt * 10)), 0.16, pan=rng.uniform(-0.8, 0.8))
    sfx.add(0.9, A.sparkle(base=A.n("G5")), 0.30)
    for tt in (17.7, 26.2, 45.4, 54.6):
        sfx.add(tt, A.whoosh(0.8, int(tt)), 0.35)
    for tt in HOPS_ELA:
        sfx.add(tt, A.boing(420, 820), 0.2, pan=0.15)
    for tt in HOPS_PAMUK:
        sfx.add(tt, A.boing(300, 640), 0.2, pan=-0.15)
    sfx.add(RED_FLOWER[3], A.pop(), 0.35)
    sfx.add(BLUE_FLOWER[3], A.pop(), 0.35)
    for tt, _ in SPARKLES:
        sfx.add(tt, A.sparkle(), 0.30)
    sfx.add(LAND_T1, A.glock(hz("C7"), 1.0), 0.18)
    sfx.add(TAKEOFF, A.poof(), 0.45)
    sfx.add(TAKEOFF + 0.05, A.boing(700, 250, 0.35), 0.18)
    for j in range(7):
        sfx.add(HEARTS_T[0] + j * 0.55, A.glock(hz(["C6", "D6", "E6", "G6", "A6", "G6", "C7"][j]), 1.0), 0.10)
    sfx.add(END_CARD + 0.1, A.sparkle(base=A.n("C6")), 0.28)
    # ayak sesleri (koşu)
    for who, gain, pitch in (("ela", 0.10, 1.0), ("pamuk", 0.06, 1.6)):
        gait_at(who, 0)
        ts, g, ph = GAIT[who]
        steps = np.floor(ph / math.pi)
        idx = np.nonzero(np.diff(steps) > 0)[0]
        for i in idx:
            if g[i] > 0.6:
                tick = A.bass(90 * pitch, 0.06, 0.015)
                sfx.add(ts[i], tick, gain)
                sfx.add(ts[i], A.shaker(0.03), gain * 0.5)

    # seslendirme
    spans = []
    for cid, start, who, _, _ in CUES:
        p_ = os.path.join(VO_DIR, f"{cid}.wav")
        if os.path.exists(p_):
            v = A.load_wav(p_)
            vo.add(start, v, 0.9, pan={"ela": 0.08, "pamuk": -0.08}.get(who, 0.0))
            spans.append((start, start + len(v) / A.SR))
    duck = A.duck_curve(DURATION, spans, depth=0.4)[: len(music.buf), None]
    fade = np.ones(len(music.buf), np.float32)
    t = np.arange(len(fade)) / A.SR
    fade *= np.clip((DURATION - 0.3 - t) / 1.8, 0, 1)
    mix = (music.buf * duck * 0.7 + sfx.buf + vo.buf) * fade[:, None]
    mix = A.soft_limit(mix[: int(DURATION * A.SR)])
    A.write_wav(path, mix)
    return path


# ============================================================== render altyapısı
_LAYERS = None
_STYLE = None
_SCALE = 1.0


def _worker(args):
    seg_idx, f0, f1, out = args
    ow, oh = int(W * _SCALE) // 2 * 2, int(H * _SCALE) // 2 * 2
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                             "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "15", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(f0, f1):
        img = render_frame(i, _STYLE, _LAYERS)
        if _SCALE != 1.0:
            img = cv2.resize(img, (ow, oh), interpolation=cv2.INTER_AREA)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def main():
    global _LAYERS, _STYLE, _SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="suluboya", choices=list(PAINTERS))
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=DURATION)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--still", type=float, nargs="*", help="yalnızca bu saniyelerin karelerini PNG olarak kaydet")
    ap.add_argument("--work", default=os.path.join(ROOT, "build"))
    ap.add_argument("--audio-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    _STYLE, _SCALE = a.style, a.scale
    load_envelopes()
    _LAYERS = world.build_layers(a.style, cache_dir=a.work)
    if a.audio_only:
        print(build_audio(os.path.join(a.work, "mix.wav")))
        return
    if a.still:
        for s in a.still:
            img = render_frame(int(s * FPS), a.style, _LAYERS)
            path = os.path.join(a.work, f"still_{a.style}_{s:05.1f}.png")
            cv2.imwrite(path, img)
            print(path)
        return
    f0, f1 = int(a.start * FPS), int(a.end * FPS)
    n = max(1, a.workers * 3)
    bounds = np.linspace(f0, f1, n + 1).astype(int)
    jobs = [(k, bounds[k], bounds[k + 1], os.path.join(a.work, f"seg_{a.style}_{k:03d}.mp4")) for k in range(n)
            if bounds[k + 1] > bounds[k]]
    with Pool(a.workers) as pool:
        segs = []
        for k, s in enumerate(pool.imap(_worker, jobs)):
            segs.append(s)
            print(f"  parça {k + 1}/{len(jobs)} tamam", flush=True)
    lst = os.path.join(a.work, f"concat_{a.style}.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    out = a.out or os.path.join(a.work, f"video_{a.style}.mp4")
    silent = os.path.join(a.work, f"silent_{a.style}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    for s in segs:
        os.remove(s)
    wav = build_audio(os.path.join(a.work, "mix.wav"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-ss", str(a.start), "-t", str(a.end - a.start),
                    "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", out], check=True)
    os.remove(silent)
    print(out)


if __name__ == "__main__":
    main()
