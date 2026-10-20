"""Çizim teknikleri. Karakterler ve dekor tek bir 'part' (parça) dilinde tanımlanır;
her teknik (suluboya / kâğıt kesme / yumuşak 3B) bu parçaları kendi yöntemiyle boyar."""
import math

import cairo
import cv2
import numpy as np

from .core import W, H, hash01, noise_patch, fractal_noise

INK = (0.30, 0.20, 0.16)
PAPER = np.array([0.985, 0.965, 0.925], np.float32)  # sıcak suluboya kâğıdı (RGB)


class Canvas:
    """numpy BGRA (önçarpımlı) bellek üzerinde cairo yüzeyi."""

    def __init__(self, w=W, h=H, fill=None):
        self.w, self.h = w, h
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
        assert stride == w * 4
        self.arr = np.zeros((h, w, 4), np.uint8)
        self.surface = cairo.ImageSurface.create_for_data(self.arr, cairo.FORMAT_ARGB32, w, h, stride)
        self.ctx = cairo.Context(self.surface)
        if fill is not None:
            self.ctx.set_source_rgb(*fill)
            self.ctx.paint()

    def numpy_begin(self):
        self.surface.flush()

    def numpy_end(self):
        self.surface.mark_dirty()


def _device_path(ctx, path_fn):
    ctx.new_path()
    path_fn(ctx)
    ctx.save()
    ctx.identity_matrix()
    ext = ctx.fill_extents()
    dpath = ctx.copy_path()
    ctx.restore()
    ctx.new_path()
    return dpath, ext


def _a8(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
    return s, cairo.Context(s)


def _a8_array(s, w, h):
    s.flush()
    stride = s.get_stride()
    return np.ndarray((h, stride), np.uint8, s.get_data())[:, :w].astype(np.float32) / 255.0


def lighten(c, k):
    return tuple(x + (1 - x) * k for x in c)


def darken(c, k):
    return tuple(x * (1 - k) for x in c)


class Painter:
    """Ortak arayüz. scale: ekrandaki büyüklük çarpanı (kamera yakınlaştırması)."""

    style = "base"

    def __init__(self, canvas, t=0.0, scale=1.0, frame=0):
        self.cv = canvas
        self.ctx = canvas.ctx
        self.t = t
        self.scale = scale
        self.frame = frame
        self.counter = 0

    def _seed(self, seed):
        self.counter += 1
        return seed if seed is not None else self.counter

    # alt sınıflar uygular
    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        raise NotImplementedError

    def stroke(self, path_fn, color=INK, width=3.0, alpha=1.0):
        ctx = self.ctx
        ctx.new_path()
        path_fn(ctx)
        ctx.save()
        ctx.identity_matrix()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(width * self.scale)
        ctx.set_source_rgba(*color, alpha)
        ctx.stroke()
        ctx.restore()

    def glow(self, x, y, r, color, alpha=1.0):
        """Yumuşak ışık lekesi (ışıltı, güneş parlaması). x,y kullanıcı koordinatı."""
        ctx = self.ctx
        dx, dy = ctx.user_to_device(x, y)
        rr = abs(ctx.user_to_device_distance(r, 0)[0]) + 1e-3
        ctx.save()
        ctx.identity_matrix()
        g = cairo.RadialGradient(dx, dy, 0, dx, dy, rr)
        g.add_color_stop_rgba(0, *color, alpha)
        g.add_color_stop_rgba(0.35, *color, alpha * 0.45)
        g.add_color_stop_rgba(1, *color, 0)
        ctx.set_source(g)
        ctx.arc(dx, dy, rr, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

    def finish(self, frame_rgb):
        return frame_rgb


# ===================================================================== SULUBOYA
class WatercolorPainter(Painter):
    style = "suluboya"

    def __init__(self, canvas, t=0.0, scale=1.0, frame=0, boil=True):
        super().__init__(canvas, t, scale, frame)
        # "kaynama": kenar titreşimi saniyede 8 kez değişir, el yapımı his verir
        self.boil = (frame // 3) % 3 if boil else 0

    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        seed = self._seed(seed)
        ctx = self.ctx
        ax, ay = ctx.user_to_device(0, 0)
        dpath, (x0, y0, x1, y1) = _device_path(ctx, path_fn)
        if x1 - x0 < 0.5 or y1 - y0 < 0.5:
            return
        s = self.scale
        pad = int(10 * s) + 6
        bx0, by0 = max(int(math.floor(x0)) - pad, 0), max(int(math.floor(y0)) - pad, 0)
        bx1, by1 = min(int(math.ceil(x1)) + pad, self.cv.w), min(int(math.ceil(y1)) + pad, self.cv.h)
        w, h = bx1 - bx0, by1 - by0
        if w <= 2 or h <= 2:
            return
        ms, mc = _a8(w, h)
        mc.translate(-bx0, -by0)
        mc.append_path(dpath)
        mc.fill()
        mask = _a8_array(ms, w, h)

        hs = int(hash01(seed) * 997)
        ox, oy = int(ax - bx0) * -1 + hs * 7, int(ay - by0) * -1 + hs * 3
        bo = self.boil * 211
        amp = 2.4 * min(s, 2.0) * wet
        nx = noise_patch("wx", ox + bo, oy, h, w) - 0.5
        ny = noise_patch("wy", ox, oy + bo, h, w) - 0.5
        gy, gx = np.indices((h, w), dtype=np.float32)
        m = cv2.remap(mask, gx + nx * amp * 2, gy + ny * amp * 2, cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        m = cv2.GaussianBlur(m, (0, 0), 0.7 * min(s, 2.0))
        inner = cv2.GaussianBlur(m, (0, 0), 4.0 * min(s, 2.5) + 1.0)
        edge = np.clip(m - inner, 0, 1)
        blot = noise_patch("blot", ox * 0.5, oy * 0.5, h, w)
        gran = noise_patch("gran", bx0, by0, h, w)
        tden = 0.93 + 0.42 * (blot - 0.5) * wet + 1.5 * edge * wet + 0.16 * (gran - 0.5)

        if grad is not None:
            ct, cb = np.array(grad[0], np.float32), np.array(grad[1], np.float32)
            gy0, gy1 = grad[2], grad[3]
            rows = np.clip((np.arange(by0, by1, dtype=np.float32) - gy0) / max(gy1 - gy0, 1), 0, 1)[:, None, None]
            col = ct[None, None, :] * (1 - rows) + cb[None, None, :] * rows
        else:
            col = np.array(color, np.float32)[None, None, :]
        rgb = 1.0 - (1.0 - col) * tden[..., None]
        rgb *= (1.0 - 0.10 * edge * wet)[..., None]
        rgb = np.clip(rgb, 0, 1)
        a = np.clip(m * alpha, 0, 1)
        self._over(bx0, by0, rgb, a)

        if line and lw > 0:
            # dış hat, maskenin kenarından çıkarılır: üst üste binen alt-yolların iç çizgileri görünmez
            k = max(3, int(round(2.8 * lw * (0.55 + 0.45 * s))))
            kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
            lm = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kern)
            lm = cv2.GaussianBlur(lm, (0, 0), 0.6)
            lm = cv2.remap(lm, gx + nx * amp, gy + ny * amp, cv2.INTER_LINEAR, borderValue=0)
            press = 0.55 + 0.6 * noise_patch("blot", ox * 3 + 500, oy * 3, h, w)
            la = np.clip(lm * press * 0.85 * alpha, 0, 1)
            ink = np.array(INK, np.float32)[None, None, :] * 0.8 + col * 0.2 * 0.6
            self._over(bx0, by0, np.broadcast_to(ink, (h, w, 3)), la)

    def _over(self, bx, by, rgb, a):
        cv = self.cv
        cv.numpy_begin()
        reg = cv.arr[by:by + a.shape[0], bx:bx + a.shape[1]].astype(np.float32) / 255.0
        a3 = a[..., None]
        src = rgb[..., ::-1] * a3  # RGB -> BGR, önçarpımlı
        reg[..., :3] = src + reg[..., :3] * (1 - a3)
        reg[..., 3] = a + reg[..., 3] * (1 - a)
        cv.arr[by:by + a.shape[0], bx:bx + a.shape[1]] = np.clip(reg * 255 + 0.5, 0, 255).astype(np.uint8)
        cv.numpy_end()

    def stroke(self, path_fn, color=INK, width=3.0, alpha=1.0):
        super().stroke(path_fn, color, width * 0.9, alpha * 0.85)


# ===================================================================== KÂĞIT KESME
class PaperPainter(Painter):
    style = "kagit"

    def __init__(self, canvas, t=0.0, scale=1.0, frame=0, jitter=True, shadow=1.0):
        super().__init__(canvas, t, scale, frame)
        self.hold = frame // 2 if jitter else 0  # stop-motion: her poz 2 kare tutulur
        self.jitter = jitter
        self.shadow = shadow

    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        seed = self._seed(seed)
        ctx = self.ctx
        dpath, (x0, y0, x1, y1) = _device_path(ctx, path_fn)
        if x1 - x0 < 0.5:
            return
        s = self.scale
        jx = jy = 0.0
        if self.jitter:
            jx = (hash01(seed, self.hold, "x") - 0.5) * 1.4 * s
            jy = (hash01(seed, self.hold, "y") - 0.5) * 1.4 * s
        tone = 0.95 + 0.07 * hash01(seed, "tone")
        c = tuple(min(1.0, v * tone) for v in color) if color is not None else (1, 1, 1)
        ctx.save()
        ctx.identity_matrix()
        # yumuşak, katmanlı gölge
        for k, (dx, dy, al) in enumerate(((2.0, 3.0, 0.16), (4.5, 6.5, 0.10), (7.0, 10.0, 0.05))):
            ctx.new_path()
            ctx.translate(dx * s * self.shadow + jx, dy * s * self.shadow + jy)
            ctx.append_path(dpath)
            ctx.set_source_rgba(0.12, 0.08, 0.16, al * alpha * self.shadow)
            ctx.fill()
            ctx.identity_matrix()
        ctx.new_path()
        ctx.translate(jx, jy)
        ctx.append_path(dpath)
        if grad is not None:
            g = cairo.LinearGradient(0, grad[2], 0, grad[3])
            g.add_color_stop_rgba(0, *grad[0], alpha)
            g.add_color_stop_rgba(1, *grad[1], alpha)
            ctx.set_source(g)
        else:
            ctx.set_source_rgba(*c, alpha)
        ctx.fill_preserve()
        # kesik kenarın açık rengi
        ctx.set_source_rgba(1, 1, 1, 0.22 * alpha)
        ctx.set_line_width(1.2 * s)
        ctx.stroke()
        ctx.restore()

    def stroke(self, path_fn, color=INK, width=3.0, alpha=1.0):
        super().stroke(path_fn, color, width * 1.1, alpha)


# ===================================================================== YUMUŞAK 3B
class SoftPainter(Painter):
    style = "yumusak3b"

    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        self._seed(seed)
        ctx = self.ctx
        dpath, (x0, y0, x1, y1) = _device_path(ctx, path_fn)
        if x1 - x0 < 0.5:
            return
        ctx.save()
        ctx.identity_matrix()
        ctx.append_path(dpath)
        w, h = x1 - x0, y1 - y0
        if grad is not None:
            g = cairo.LinearGradient(0, grad[2], 0, grad[3])
            g.add_color_stop_rgba(0, *grad[0], alpha)
            g.add_color_stop_rgba(1, *grad[1], alpha)
        elif flat:
            g = cairo.LinearGradient(0, y0, 0, y1)
            g.add_color_stop_rgba(0, *lighten(color, 0.18), alpha)
            g.add_color_stop_rgba(1, *darken(color, 0.12), alpha)
        else:
            cx, cy = x0 + w * 0.36, y0 + h * 0.30
            r = max(w, h) * 0.9 + 1
            g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
            g.add_color_stop_rgba(0, *lighten(color, 0.38), alpha)
            g.add_color_stop_rgba(0.45, *color, alpha)
            g.add_color_stop_rgba(1, *darken(color, 0.30), alpha)
        ctx.set_source(g)
        ctx.fill()
        if not flat and grad is None and min(w, h) > 14:
            # kenar ışığı (rim light)
            ctx.append_path(dpath)
            ctx.clip()
            ctx.translate(-1.6 * self.scale, -1.6 * self.scale)
            ctx.append_path(dpath)
            ctx.set_source_rgba(1, 1, 1, 0.16 * alpha)
            ctx.set_line_width(3.0 * self.scale)
            ctx.stroke()
        ctx.restore()


# ===================================================================== KEÇE (el işi)
def _shift(img, dx, dy):
    M = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)


class FeltPainter(WatercolorPainter):
    """Keçeden kesilmiş, kenarları dikişli, hafif dolgulu parçalar; stop-motion titreşimi."""

    style = "kece"

    def __init__(self, canvas, t=0.0, scale=1.0, frame=0, jitter=True):
        super().__init__(canvas, t, scale, frame, boil=False)
        self.hold = frame // 2
        self.jitter = jitter

    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        seed = self._seed(seed)
        ctx = self.ctx
        ax, ay = ctx.user_to_device(0, 0)
        dpath, (x0, y0, x1, y1) = _device_path(ctx, path_fn)
        if x1 - x0 < 0.5 or y1 - y0 < 0.5:
            return
        s = self.scale
        sc = min(s, 2.0)
        jx = jy = 0.0
        if self.jitter:
            jx = (hash01(seed, self.hold, "x") - 0.5) * 1.3 * sc
            jy = (hash01(seed, self.hold, "y") - 0.5) * 1.3 * sc
        pad = int(14 * sc) + 8
        bx0, by0 = max(int(math.floor(x0)) - pad, 0), max(int(math.floor(y0)) - pad, 0)
        bx1, by1 = min(int(math.ceil(x1)) + pad, self.cv.w), min(int(math.ceil(y1)) + pad, self.cv.h)
        w, h = bx1 - bx0, by1 - by0
        if w <= 2 or h <= 2:
            return
        ms, mc = _a8(w, h)
        mc.translate(-bx0 + jx, -by0 + jy)
        mc.append_path(dpath)
        mc.fill()
        mask = _a8_array(ms, w, h)

        hs = int(hash01(seed) * 997)
        ox, oy = bx0 - int(ax) + hs * 7, by0 - int(ay) + hs * 3
        # tüylü kenar: ince, yüksek frekanslı titreşim
        nx = noise_patch("gran", ox, oy, h, w) - 0.5
        ny = noise_patch("gran", ox + 333, oy + 77, h, w) - 0.5
        gy, gx = np.indices((h, w), dtype=np.float32)
        m = cv2.remap(mask, gx + nx * 2.6 * sc, gy + ny * 2.6 * sc, cv2.INTER_LINEAR, borderValue=0)
        m = cv2.GaussianBlur(m, (0, 0), 0.7)
        # dolgu hacmi: kenarlar koyu, sol üst kenarda ışık
        inner = cv2.GaussianBlur(m, (0, 0), 6.0 * sc + 2.0)
        shade = 0.78 + 0.24 * np.clip(inner * 1.7, 0, 1)
        hl = np.clip(inner - _shift(inner, 2.5 * sc, 2.5 * sc), 0, 1) * 0.9
        fib = noise_patch("fiber", ox, oy, h, w)
        fine = noise_patch("gran", bx0 * 3, by0 * 3, h, w)
        tex = 0.90 + 0.13 * fib + 0.07 * (fine - 0.5)

        if grad is not None:
            ct, cb = np.array(grad[0], np.float32), np.array(grad[1], np.float32)
            rows = np.clip((np.arange(by0, by1, dtype=np.float32) - grad[2]) / max(grad[3] - grad[2], 1), 0, 1)[:, None, None]
            col = ct[None, None, :] * (1 - rows) + cb[None, None, :] * rows
            base = tuple(float(v) for v in (ct + cb) / 2)
        else:
            col = np.array(color, np.float32)[None, None, :]
            base = color
        rgb = np.clip(col * (shade * tex)[..., None] + hl[..., None] * 0.35, 0, 1)

        # alttaki parçaya düşen yumuşak gölge
        sh = cv2.GaussianBlur(_shift(m, 2.5 * sc, 3.5 * sc), (0, 0), 2.5 * sc + 0.5)
        self._over(bx0, by0, np.zeros((h, w, 3), np.float32), np.clip(sh * 0.30 * alpha, 0, 1))
        self._over(bx0, by0, rgb, np.clip(m * alpha, 0, 1))

        # dikiş
        if line and lw > 0 and min(x1 - x0, y1 - y0) > 26:
            inset = max(3, int(round(5.5 * sc)))
            er = cv2.erode((m > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * inset + 1, 2 * inset + 1)))
            contours, _ = cv2.findContours(er, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                lum = 0.3 * base[0] + 0.59 * base[1] + 0.11 * base[2]
                thread = darken(base, 0.38) if lum > 0.78 else lighten(base, 0.62)
                surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
                c = cairo.Context(surf)
                c.set_line_width(1.9 * sc * lw ** 0.3)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.set_dash([6.0 * sc, 4.5 * sc])
                c.set_source_rgba(*thread, 0.95 * alpha)
                for cnt in contours:
                    pts = cnt[::2, 0, :].astype(np.float32)
                    if len(pts) < 6:
                        continue
                    k = np.ones(5, np.float32) / 5
                    px_ = np.convolve(np.concatenate([pts[-2:, 0], pts[:, 0], pts[:2, 0]]), k, "valid")
                    py_ = np.convolve(np.concatenate([pts[-2:, 1], pts[:, 1], pts[:2, 1]]), k, "valid")
                    c.move_to(px_[0], py_[0])
                    for a_, b_ in zip(px_[1:], py_[1:]):
                        c.line_to(a_, b_)
                    c.close_path()
                c.stroke()
                surf.flush()
                arr = np.ndarray((h, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :w].astype(np.float32) / 255
                a = arr[..., 3]
                rgbt = arr[..., :3][..., ::-1] / np.maximum(a, 1e-4)[..., None]
                self._over(bx0, by0, np.clip(rgbt, 0, 1), a)

    def stroke(self, path_fn, color=INK, width=3.0, alpha=1.0):
        """Nakış: ağız, kaş gibi çizgiler kısa ilmeklerle işlenmiş gibi."""
        ctx = self.ctx
        ctx.new_path()
        path_fn(ctx)
        ctx.save()
        ctx.identity_matrix()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(width * self.scale * 1.05)
        ctx.set_dash([5.0 * self.scale, 1.6 * self.scale])
        ctx.set_source_rgba(*color, alpha)
        ctx.stroke()
        ctx.restore()


# ===================================================================== BATI ÇİZGİ FİLMİ (cel)
OUTLINE = (0.07, 0.06, 0.08)


class CartoonPainter(Painter):
    """Temiz siyah kontur + düz renk + tek tonluk cel gölge (sağ alt) ve küçük parlama (sol üst).
    Kontur, dolgunun altına iki kat kalın çizilir: üst üste binen alt-yolların iç çizgileri dolguyla örtülür."""

    style = "cizgi"
    jitter = False

    def part(self, path_fn, color, line=True, alpha=1.0, seed=None, grad=None, lw=1.0, wet=1.0, flat=False):
        self._seed(seed)
        ctx = self.ctx
        dpath, (x0, y0, x1, y1) = _device_path(ctx, path_fn)
        w, h = x1 - x0, y1 - y0
        if w < 0.5 or h < 0.5:
            return
        s = self.scale
        m = min(w, h)
        ctx.save()
        ctx.identity_matrix()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if line and lw > 0 and alpha > 0.6 and m > 4:
            ow = min(3.4 * lw * s, 0.16 * m + 1.0)
            ctx.append_path(dpath)
            ctx.set_source_rgba(*OUTLINE, alpha)
            ctx.set_line_width(2 * ow)
            ctx.stroke()
        ctx.append_path(dpath)
        if grad is not None:
            g = cairo.LinearGradient(0, grad[2], 0, grad[3])
            g.add_color_stop_rgba(0, *grad[0], alpha)
            g.add_color_stop_rgba(1, *grad[1], alpha)
            ctx.set_source(g)
        else:
            ctx.set_source_rgba(*color, alpha)
        ctx.fill()
        if not flat and grad is None and color is not None and m > 12 and alpha > 0.6:
            # cel gölge: şeklin kendisinden, sol üste kaydırılmış kopyası çıkarılır
            d = min(max(0.13 * m, 2.0), 22.0 * s)
            ctx.append_path(dpath)
            ctx.clip()
            ctx.append_path(dpath)
            ctx.set_source_rgba(*darken(color, 0.22), alpha)
            ctx.fill()
            ctx.translate(-d, -d * 0.9)
            ctx.append_path(dpath)
            ctx.set_source_rgba(*color, alpha)
            ctx.fill()
            ctx.identity_matrix()
            if m > 30:
                # küçük parlama
                ctx.translate(x0 + w * 0.28, y0 + h * 0.24)
                ctx.scale(w * 0.10, h * 0.06)
                ctx.arc(0, 0, 1, 0, 2 * math.pi)
                ctx.identity_matrix()
                ctx.set_source_rgba(1, 1, 1, 0.35 * alpha)
                ctx.fill()
        ctx.restore()

    def stroke(self, path_fn, color=INK, width=3.0, alpha=1.0):
        super().stroke(path_fn, OUTLINE if color == INK else color, width * 1.15, alpha)


PAINTERS = {"suluboya": WatercolorPainter, "kagit": PaperPainter, "yumusak3b": SoftPainter, "kece": FeltPainter,
            "cizgi": CartoonPainter}


# ===================================================================== son işlem (post)
_POST = {}


def _post_assets(style):
    if style not in _POST:
        fib = fractal_noise(H, W, 7, 5.0, 3)
        gran = fractal_noise(H, W, 8, 1.5, 2)
        broad = fractal_noise(H, W, 9, 220.0, 3)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        vig = np.clip(1.0 - 0.22 * np.clip(d - 0.55, 0, 1) ** 1.6, 0, 1)
        if style == "suluboya":
            tex = 0.955 + 0.05 * fib + 0.03 * gran - 0.03 * broad
        elif style == "kagit":
            tex = 0.93 + 0.075 * fib + 0.03 * gran
        elif style == "kece":
            tex = 0.95 + 0.04 * fib + 0.025 * gran
        else:
            tex = np.ones((H, W), np.float32)
        _POST[style] = ((tex * vig).astype(np.float32)[..., None])
    return _POST[style]


def post_process(style, rgb):
    """rgb: float32 (H,W,3) BGR, 0..1."""
    tex = _post_assets(style)
    out = rgb * tex
    if style == "suluboya":
        out = out * np.array([0.985, 0.995, 1.0], np.float32)  # hafif sıcak ton (BGR)
    elif style == "kece":
        out = out * np.array([0.97, 0.99, 1.0], np.float32)
        out = (out - 0.5) * 1.03 + 0.51
    elif style == "yumusak3b":
        bright = np.clip(out - 0.72, 0, 1)
        bloom = cv2.GaussianBlur(bright, (0, 0), 18)
        out = out + bloom * 0.55
        out = (out - 0.5) * 1.04 + 0.5
    return np.clip(out, 0, 1)
