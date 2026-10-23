"""Temel araçlar: sabitler, yumuşatma eğrileri, anahtar kare izleri, gürültü dokuları, şekil yardımcıları."""
import math
import os

import cv2
import numpy as np

# kare ölçüsü: varsayılan yatay 1920x1080; dikey Shorts için UMAY_KARE=1080x1920 (modüller içe aktarılmadan önce)
W, H = (int(v) for v in os.environ.get("UMAY_KARE", "1920x1080").split("x"))
FPS = 24
GROUND_Y = 880.0


# ---------------------------------------------------------------- yumuşatma
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1
    return 1 + t * t * ((s + 1) * t + s)


def ease_out_elastic(t):
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1


EASES = {
    "lin": clamp,
    "io": ease_io,
    "s": smooth,
    "in": lambda t: clamp(t) ** 2,
    "out": lambda t: 1 - (1 - clamp(t)) ** 2,
    "back": ease_out_back,
    "elastic": ease_out_elastic,
    "hold": lambda t: 0.0 if t < 1 else 1.0,
}


def window(t, t0, t1, fade=0.3):
    """t0..t1 aralığında 1, kenarlarda yumuşak geçişli 0..1."""
    if t < t0 - fade or t > t1 + fade:
        return 0.0
    if t < t0:
        return smooth((t - (t0 - fade)) / fade)
    if t > t1:
        return 1.0 - smooth((t - t1) / fade)
    return 1.0


class Track:
    """(zaman, değer[, yumuşatma]) anahtarlarından değer üreten iz. Yumuşatma, o anahtara varan parçaya uygulanır."""

    def __init__(self, keys):
        self.keys = sorted(keys, key=lambda k: k[0])

    def __call__(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1]
        for i in range(1, len(ks)):
            if t < ks[i][0]:
                t0, v0 = ks[i - 1][0], ks[i - 1][1]
                t1, v1 = ks[i][0], ks[i][1]
                e = ks[i][2] if len(ks[i]) > 2 else "io"
                u = EASES[e]((t - t0) / (t1 - t0))
                if isinstance(v0, (tuple, list)):
                    return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
                return lerp(v0, v1, u)
        return ks[-1][1]


class Steps:
    """Ayrık değer izi (poz adları gibi). blend() ile geçiş ağırlığı da verir."""

    def __init__(self, keys, blend=0.35):
        self.keys = sorted(keys, key=lambda k: k[0])
        self.blend_time = blend

    def blend(self, t):
        """(önceki, şimdiki, ağırlık) döndürür."""
        ks = self.keys
        idx = 0
        for i, k in enumerate(ks):
            if t >= k[0]:
                idx = i
        cur = ks[idx][1]
        if idx == 0:
            return cur, cur, 1.0
        prev = ks[idx - 1][1]
        u = ease_io((t - ks[idx][0]) / self.blend_time)
        return prev, cur, u


def catmull(points, u):
    """points: [(x,y)...], u: 0..len-1 arası sürekli parametre."""
    n = len(points)
    i = int(clamp(math.floor(u), 0, n - 2))
    f = u - i
    p0 = points[max(i - 1, 0)]
    p1 = points[i]
    p2 = points[i + 1]
    p3 = points[min(i + 2, n - 1)]
    out = []
    for k in range(2):
        a, b, c, d = p0[k], p1[k], p2[k], p3[k]
        out.append(0.5 * ((2 * b) + (-a + c) * f + (2 * a - 5 * b + 4 * c - d) * f * f + (-a + 3 * b - 3 * c + d) * f ** 3))
    return tuple(out)


class Path2D:
    """Zamanlı yol: [(t, x, y)] — catmull-rom ile pürüzsüz."""

    def __init__(self, keys):
        self.keys = sorted(keys)

    def __call__(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1], ks[0][2]
        if t >= ks[-1][0]:
            return ks[-1][1], ks[-1][2]
        for i in range(1, len(ks)):
            if t < ks[i][0]:
                f = (t - ks[i - 1][0]) / (ks[i][0] - ks[i - 1][0])
                return catmull([(k[1], k[2]) for k in ks], i - 1 + f)
        return ks[-1][1], ks[-1][2]


def hash01(*args):
    """Deterministik sözde rastgele 0..1."""
    h = 2166136261
    for a in args:
        for ch in str(a):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5BD1E995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFFFF) / float(0xFFFFFF)


# ---------------------------------------------------------------- gürültü
def fractal_noise(h, w, seed, scale, octaves=4, persistence=0.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        gh, gw = max(2, int(h / scale) + 3), max(2, int(w / scale) + 3)
        g = rng.random((gh, gw)).astype(np.float32)
        up = cv2.resize(g, (int(gw * scale), int(gh * scale)), interpolation=cv2.INTER_CUBIC)[:h, :w]
        out += up * amp
        tot += amp
        amp *= persistence
        scale = max(scale / 2.0, 1.0)
    out /= tot
    out -= out.min()
    out /= max(out.max(), 1e-6)
    return out


_TILES = {}
TILE = 1024


def periodic_noise(n, seed, scale, octaves=4, persistence=0.5):
    """Kenarları birbirine kusursuz eklenen (döşenebilir) fraktal gürültü."""
    rng = np.random.default_rng(seed)
    out = np.zeros((n, n), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        cells = max(2, n // scale)
        g = rng.random((cells, cells)).astype(np.float32)
        g = np.pad(g, 3, mode="wrap")
        up = cv2.resize(g, ((cells + 6) * scale, (cells + 6) * scale), interpolation=cv2.INTER_CUBIC)
        out += up[3 * scale:3 * scale + n, 3 * scale:3 * scale + n] * amp
        tot += amp
        amp *= persistence
        scale = max(scale // 2, 1)
    out -= out.min()
    out /= max(out.max(), 1e-6)
    return out


def tile(name):
    """Önceden üretilmiş, döşenebilir gürültü dokuları (ilk kullanımda üretilir)."""
    if name not in _TILES:
        specs = {
            "blot": (11, 128, 4),      # renk birikintileri
            "wx": (21, 16, 3),         # kenar titreşimi x
            "wy": (31, 16, 3),         # kenar titreşimi y
            "gran": (41, 2, 2),        # granülasyon
            "fiber": (51, 8, 3),       # kâğıt lifi
        }
        seed, sc, oc = specs[name]
        _TILES[name] = np.ascontiguousarray(periodic_noise(TILE, seed, sc, oc))
    return _TILES[name]


def noise_patch(name, ox, oy, h, w):
    t = tile(name)
    ys = (np.arange(h) + int(oy)) % TILE
    xs = (np.arange(w) + int(ox)) % TILE
    return t[ys][:, xs]


# ---------------------------------------------------------------- şekil yardımcıları
def capsule(ctx, x0, y0, x1, y1, r0, r1=None):
    """İki noktayı birleştiren yuvarlak uçlu kalın çubuk (kol, bacak) — tek kapalı yol."""
    if r1 is None:
        r1 = r0
    a = math.atan2(y1 - y0, x1 - x0)
    ctx.new_sub_path()
    ctx.arc(x1, y1, r1, a - math.pi / 2, a + math.pi / 2)
    ctx.arc(x0, y0, r0, a + math.pi / 2, a + 3 * math.pi / 2)
    ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry, rot=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    if rot:
        ctx.rotate(rot)
    ctx.scale(max(rx, 1e-3), max(ry, 1e-3))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def circle(ctx, cx, cy, r):
    ctx.new_sub_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)


def blob(ctx, cx, cy, r, n=8, wobble=0.12, seed=0, sx=1.0, sy=1.0):
    """Organik, hafif düzensiz yuvarlak (bulut, ağaç tacı, çalı)."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + wobble * (hash01(seed, i) * 2 - 1))
        pts.append((cx + math.cos(a) * rr * sx, cy + math.sin(a) * rr * sy))
    smooth_closed(ctx, pts)


def smooth_closed(ctx, pts, tension=1.0):
    """Noktalardan geçen kapalı, pürüzsüz eğri."""
    n = len(pts)
    ctx.new_sub_path()
    ctx.move_to(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        ctx.curve_to(*c1, *c2, *p2)
    ctx.close_path()


def rounded_rect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
