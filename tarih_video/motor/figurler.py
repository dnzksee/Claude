"""Küçük asker figürleri (vektör, kodla çizilir): atlı, atlı okçu, piyade, okçu.

Figürler yandan görünüşlüdür; hareket yönüne göre sağa/sola döner, yürürken/dörtnala
koşarken bacakları ve gövdesi sallanır. Harita ve taktik sahnelerde aynı figürler kullanılır.
"""
import math
import random

import cairo

from .sahne import TARAFLAR, yumusat, HareketOku

KOYU = (0.10, 0.08, 0.06)
AT_RENKLERI = [(0.36, 0.22, 0.12), (0.22, 0.15, 0.10), (0.48, 0.32, 0.18), (0.30, 0.27, 0.25)]


def _cizgi(cr, w):
    cr.set_line_width(w)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)


def atli(cr, x, y, s, taraf, faz=0.0, hiz=0.0, yon=1, alfa=1.0, okcu=False, at_renk=None, sancak=False):
    """(x, y) toynak hizası; s ölçek (1 ≈ 30 px boy). hiz 0..1 dörtnala şiddeti."""
    tr = TARAFLAR[taraf]
    cr.save()
    cr.translate(x, y)
    cr.scale(s * yon, s)
    zipla = -abs(math.sin(faz * math.pi)) * 2.2 * hiz
    cr.translate(0, zipla)
    at = at_renk or AT_RENKLERI[0]
    # bacaklar (dörtnala: ön ve arka çiftler zıt fazda)
    _cizgi(cr, 2.2)
    for bx, ph in ((-7, 0.0), (-4.5, 0.5), (6, 0.25), (8.5, 0.75)):
        a = math.sin((faz + ph) * 2 * math.pi) * 0.6 * hiz
        cr.move_to(bx, -9)
        cr.line_to(bx + math.sin(a) * 6, -9 + math.cos(a) * 9)
    cr.set_source_rgba(*KOYU, alfa)
    cr.stroke()
    # gövde
    cr.save()
    cr.translate(0.5, -12)
    cr.scale(11, 4.6)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.restore()
    cr.set_source_rgba(*at, alfa)
    cr.fill_preserve()
    cr.set_source_rgba(*KOYU, alfa)
    cr.set_line_width(1.1)
    cr.stroke()
    # boyun + baş
    egim = math.sin(faz * 2 * math.pi) * 1.2 * hiz
    cr.move_to(8, -15)
    cr.line_to(13, -22 + egim)
    cr.line_to(17.5, -20 + egim)
    cr.line_to(16.5, -17.5 + egim)
    cr.line_to(12.5, -18 + egim)
    cr.line_to(10.5, -11)
    cr.close_path()
    cr.set_source_rgba(*at, alfa)
    cr.fill_preserve()
    cr.set_source_rgba(*KOYU, alfa)
    cr.set_line_width(1.0)
    cr.stroke()
    # kuyruk
    kuy = math.sin(faz * 2 * math.pi + 1) * 2 * hiz
    cr.move_to(-10.5, -14)
    cr.curve_to(-15, -13 + kuy, -16, -8 + kuy, -15, -5 + kuy)
    cr.set_source_rgba(*KOYU, alfa)
    _cizgi(cr, 1.8)
    cr.stroke()
    # süvari gövdesi (taraf rengi)
    cr.move_to(-3, -15)
    cr.line_to(3, -15)
    cr.line_to(2, -24)
    cr.line_to(-2.5, -24)
    cr.close_path()
    cr.set_source_rgba(*tr["renk"], alfa)
    cr.fill_preserve()
    cr.set_source_rgba(*KOYU, alfa)
    cr.set_line_width(1.0)
    cr.stroke()
    # baş + miğfer/başlık
    cr.arc(0, -27, 2.6, 0, 2 * math.pi)
    cr.set_source_rgba(0.85, 0.68, 0.52, alfa)
    cr.fill()
    cr.arc(0, -27.6, 2.8, math.pi, 2 * math.pi)
    cr.set_source_rgba(*tr["vurgu"], alfa)
    cr.fill()
    if okcu:
        # yay
        cr.arc(4.5, -21, 5, -1.2, 1.2)
        cr.set_source_rgba(*KOYU, alfa)
        _cizgi(cr, 1.3)
        cr.stroke()
    else:
        # mızrak
        cr.move_to(-6, -14)
        cr.line_to(16, -30)
        cr.set_source_rgba(0.35, 0.25, 0.15, alfa)
        _cizgi(cr, 1.2)
        cr.stroke()
        cr.move_to(16, -30)
        cr.line_to(19, -32.5)
        cr.set_source_rgba(0.75, 0.75, 0.78, alfa)
        _cizgi(cr, 1.6)
        cr.stroke()
    if sancak:
        dal = math.sin(faz * 2 * math.pi) * 1.5
        cr.move_to(-2, -24)
        cr.line_to(-2, -42)
        cr.set_source_rgba(*KOYU, alfa)
        _cizgi(cr, 1.0)
        cr.stroke()
        cr.move_to(-2, -42)
        cr.line_to(-12, -40 + dal)
        cr.line_to(-2, -36)
        cr.close_path()
        cr.set_source_rgba(*tr["renk"], alfa)
        cr.fill()
    cr.restore()


def piyade(cr, x, y, s, taraf, faz=0.0, hiz=0.0, yon=1, alfa=1.0, okcu=False):
    tr = TARAFLAR[taraf]
    cr.save()
    cr.translate(x, y)
    cr.scale(s * yon, s)
    cr.translate(0, -abs(math.sin(faz * math.pi)) * 1.2 * hiz)
    # bacaklar
    a = math.sin(faz * 2 * math.pi) * 0.5 * hiz
    cr.move_to(0, -9)
    cr.line_to(math.sin(a) * 5, 0)
    cr.move_to(0, -9)
    cr.line_to(-math.sin(a) * 5, 0)
    cr.set_source_rgba(*KOYU, alfa)
    _cizgi(cr, 1.8)
    cr.stroke()
    # gövde
    cr.move_to(-2.8, -9)
    cr.line_to(2.8, -9)
    cr.line_to(2.2, -18)
    cr.line_to(-2.2, -18)
    cr.close_path()
    cr.set_source_rgba(*tr["renk"], alfa)
    cr.fill_preserve()
    cr.set_source_rgba(*KOYU, alfa)
    cr.set_line_width(0.9)
    cr.stroke()
    cr.arc(0, -21, 2.4, 0, 2 * math.pi)
    cr.set_source_rgba(0.85, 0.68, 0.52, alfa)
    cr.fill()
    cr.arc(0, -21.5, 2.6, math.pi, 2 * math.pi)
    cr.set_source_rgba(*tr["vurgu"], alfa)
    cr.fill()
    if okcu:
        cr.arc(4, -15, 4.5, -1.3, 1.3)
        cr.set_source_rgba(*KOYU, alfa)
        _cizgi(cr, 1.2)
        cr.stroke()
    else:
        # mızrak
        cr.move_to(4.5, -3)
        cr.line_to(4.5, -32)
        cr.set_source_rgba(0.35, 0.25, 0.15, alfa)
        _cizgi(cr, 1.1)
        cr.stroke()
        cr.move_to(4.5, -32)
        cr.line_to(4.5, -35.5)
        cr.set_source_rgba(0.75, 0.75, 0.78, alfa)
        _cizgi(cr, 1.6)
        cr.stroke()
        # kalkan
        cr.save()
        cr.translate(2.5, -13.5)
        cr.scale(3.4, 5)
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgba(*tr["vurgu"], alfa)
        cr.fill_preserve()
        cr.set_source_rgba(*KOYU, alfa)
        cr.set_line_width(0.9)
        cr.stroke()
    cr.restore()


def toz(cr, x, y, s, t, alfa=1.0, tohum=0):
    """Hareket eden birliğin arkasında kalkan toz bulutu."""
    rnd = random.Random(tohum)
    for i in range(4):
        u = ((t * 1.7 + i * 0.25 + rnd.random()) % 1.0)
        r = (3 + 9 * u) * s
        cr.arc(x - 10 * s * u * 2, y - 2 * s - 6 * s * u, r, 0, 2 * math.pi)
        cr.set_source_rgba(0.72, 0.64, 0.50, 0.32 * (1 - u) * alfa)
        cr.fill()


FIGUR = {
    "atli": lambda cr, x, y, s, tr, f, h, yon, a, rnk: atli(cr, x, y, s, tr, f, h, yon, a, at_renk=rnk),
    "atli_okcu": lambda cr, x, y, s, tr, f, h, yon, a, rnk: atli(cr, x, y, s, tr, f, h, yon, a, okcu=True, at_renk=rnk),
    "piyade": lambda cr, x, y, s, tr, f, h, yon, a, rnk: piyade(cr, x, y, s, tr, f, h, yon, a),
    "okcu": lambda cr, x, y, s, tr, f, h, yon, a, rnk: piyade(cr, x, y, s, tr, f, h, yon, a, okcu=True),
}


class Kafile:
    """Bir yol boyunca ilerleyen küçük figür grubu (harita sahnelerinde akıncılar, ordular, elçiler).

    yol: dünya koordinatlarında noktalar; t0..t1 arasında baştan sona ilerler.
    t_son: kaybolma anı (varsayılan t1 + 2). ok=True ise arkasında ince bir iz oku çizilir.
    """

    katman = 3
    zoom_duyarli = True

    def __init__(self, taraf, yol, t0, t1, tur="atli", adet=6, olcek=1.0, t_son=None, ok=False,
                 sancak=True, yayilma=1.0, tohum=0):
        self.taraf, self.t0, self.t1, self.tur, self.adet, self.olcek = taraf, t0, t1, tur, adet, olcek
        self.t_son = t_son if t_son is not None else t1 + 2.0
        self.yol_ok = HareketOku(taraf, yol, t0, t1, t_son=self.t_son, kalinlik=7) if ok else None
        self.pts = (self.yol_ok or HareketOku(taraf, yol, t0, t1))._ornekle()
        rnd = random.Random(tohum)
        self.dizilis = []
        for i in range(adet):
            sira, kol = divmod(i, 3)
            self.dizilis.append((-sira * 26 * yayilma + rnd.uniform(-5, 5),
                                 (kol - 1) * 16 * yayilma + rnd.uniform(-4, 4), rnd.random(),
                                 rnd.choice(AT_RENKLERI)))
        self.sancak = sancak
        # yol uzunluğu boyunca birikimli mesafe
        self.mesafe = [0.0]
        for (x1, y1), (x2, y2) in zip(self.pts, self.pts[1:]):
            self.mesafe.append(self.mesafe[-1] + math.hypot(x2 - x1, y2 - y1))

    def _nokta(self, d):
        d = max(0.0, min(d, self.mesafe[-1]))
        for i in range(1, len(self.mesafe)):
            if self.mesafe[i] >= d:
                u = (d - self.mesafe[i - 1]) / max(self.mesafe[i] - self.mesafe[i - 1], 1e-6)
                (x1, y1), (x2, y2) = self.pts[i - 1], self.pts[i]
                return x1 + (x2 - x1) * u, y1 + (y2 - y1) * u, math.atan2(y2 - y1, x2 - x1)
        x, y = self.pts[-1]
        return x, y, 0.0

    def ciz(self, cr, t, kamera_zoom=1.0):
        """Ordu işareti: yol boyunca uzayan renkli iz, hız şeritleri ve başta taraf kalkanı."""
        from .amblem import kalkan
        if self.yol_ok:
            self.yol_ok.ciz(cr, t)
        if t < self.t0 - 0.3 or t > self.t_son + 0.8:
            return
        tr = TARAFLAR[self.taraf]
        renk, vurgu = tr["renk"], tr["vurgu"]
        a = min(yumusat((t - self.t0 + 0.3) / 0.5), 1 - yumusat((t - self.t_son) / 0.8))
        u = yumusat((t - self.t0) / max(self.t1 - self.t0, 0.01))
        hareket = 1.0 if self.t0 < t < self.t1 else 0.0
        bas = u * self.mesafe[-1]
        s = 1.6 * self.olcek / max(kamera_zoom, 1) ** 0.6
        buyukluk = 0.75 + 0.05 * min(self.adet, 12)
        r = 17 * s * buyukluk
        # iz: geride kalan yol, kuyruğa doğru incelir ve solar
        if not self.yol_ok and bas > 2:
            uz = min(bas, 420 * s)
            adim = max(4.0, uz / 40)
            n = int(uz / adim)
            onceki = self._nokta(bas - uz)
            for k in range(1, n + 1):
                q = k / n
                p = self._nokta(bas - uz + k * adim)
                cr.move_to(onceki[0], onceki[1])
                cr.line_to(p[0], p[1])
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                cr.set_line_width(r * (0.15 + 0.75 * q))
                cr.set_source_rgba(*renk, a * 0.55 * q)
                cr.stroke()
                onceki = p
        x, y, aci = self._nokta(bas)
        ca, sa = math.cos(aci), math.sin(aci)
        # hız şeritleri (ilerlerken kalkanın arkasında kayan üç ok başı)
        if hareket > 0.5:
            for k in range(3):
                faz = (t * 1.8 + k / 3) % 1.0
                geri = r * (1.3 + 1.6 * faz)
                px, py = x - ca * geri, y - sa * geri
                cr.save()
                cr.translate(px, py)
                cr.rotate(aci)
                cr.move_to(-r * 0.35, -r * 0.45)
                cr.line_to(r * 0.1, 0)
                cr.line_to(-r * 0.35, r * 0.45)
                cr.set_line_width(max(1.5, r * 0.16))
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                cr.set_line_join(cairo.LINE_JOIN_ROUND)
                cr.set_source_rgba(*vurgu, a * 0.8 * (1 - faz))
                cr.stroke()
                cr.restore()
            # öndeki yön oku
            cr.save()
            cr.translate(x + ca * r * 1.25, y + sa * r * 1.25)
            cr.rotate(aci)
            cr.move_to(r * 0.45, 0)
            cr.line_to(-r * 0.15, -r * 0.38)
            cr.line_to(-r * 0.15, r * 0.38)
            cr.close_path()
            cr.set_source_rgba(*vurgu, a * 0.95)
            cr.fill()
            cr.restore()
        # büyük ordular için arkada ikinci, küçük kalkan (kalabalık hissi)
        if self.adet >= 8:
            gx, gy, _ = self._nokta(bas - r * 2.2)
            kalkan(cr, self.taraf, gx - sa * r * 0.9, gy + ca * r * 0.9, r * 0.6, renk, vurgu, a * 0.85)
        if self.adet >= 11:
            gx, gy, _ = self._nokta(bas - r * 2.2)
            kalkan(cr, self.taraf, gx + sa * r * 0.9, gy - ca * r * 0.9, r * 0.6, renk, vurgu, a * 0.85)
        sallan = math.sin(t * 7 + self.adet) * r * 0.06 * hareket
        kalkan(cr, self.taraf, x, y + sallan, r, renk, vurgu, a)
