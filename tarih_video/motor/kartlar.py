"""Bilgi kartı sahneleri: karakter kartı, zaman çizelgesi, ordu karşılaştırması, alıntı."""
import math

import cairo
import numpy as np

from .harita import DUNYA_G, DUNYA_Y, OLCEK, _gurultu
from .sahne import TARAFLAR, yumusat, _yazi, _yuvarlak_dikdortgen

KREM = (0.97, 0.93, 0.84)
ALTIN = (0.90, 0.74, 0.42)


def koyu_arka_plan(harita=None, tohum=11):
    """Koyu, sıcak tonlu dokulu zemin. harita verilirse silik bir harita izi eklenir."""
    G, Y = DUNYA_G * OLCEK, DUNYA_Y * OLCEK
    rng = np.random.default_rng(tohum)
    n = _gurultu(G, Y, rng, oktav=5, baslangic=4)
    ince = _gurultu(G, Y, rng, oktav=2, baslangic=120)
    yy, xx = np.mgrid[0:Y, 0:G].astype(np.float32)
    vin = np.clip(1 - 0.75 * (((xx / G - 0.5) * 2) ** 2 * 0.6 + ((yy / Y - 0.5) * 2) ** 2), 0.15, 1)
    taban = np.array((38, 30, 24), np.float32)
    renk = taban[None, None, :] * (0.75 + 0.5 * n + 0.12 * ince)[..., None] * (0.55 + 0.6 * vin)[..., None]
    renk = np.clip(renk, 0, 255).astype(np.uint8)
    yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, G, Y)
    t = np.ndarray((Y, G, 4), np.uint8, buffer=yuzey.get_data(), strides=(yuzey.get_stride(), 4, 1))
    t[..., 0], t[..., 1], t[..., 2], t[..., 3] = renk[..., 2], renk[..., 1], renk[..., 0], 255
    yuzey.mark_dirty()
    if harita is not None:
        cr = cairo.Context(yuzey)
        cr.set_source_surface(harita.yuzey, 0, 0)
        cr.paint_with_alpha(0.10)
    return yuzey


def _sar(cr, metin, genislik):
    satirlar, mevcut = [], ""
    for k in metin.split():
        dene = (mevcut + " " + k).strip()
        if cr.text_extents(dene).x_advance > genislik and mevcut:
            satirlar.append(mevcut)
            mevcut = k
        else:
            mevcut = dene
    if mevcut:
        satirlar.append(mevcut)
    return satirlar


def _alfa(t, t0, t1, gir=0.7, cik=0.7):
    if t < t0 or t > t1:
        return 0.0
    return min(yumusat((t - t0) / gir), 1 - yumusat((t - t1 + cik) / cik))


class KarakterKarti:
    """Sol: armalı madalyon, sağ: isim, unvan, yıllar ve sırayla beliren maddeler."""

    katman = 5

    def __init__(self, ad, unvan, yillar, taraf, t0, t1, maddeler=(), monogram=None):
        self.ad, self.unvan, self.yillar, self.taraf = ad, unvan, yillar, taraf
        self.t0, self.t1, self.maddeler = t0, t1, maddeler
        self.monogram = monogram or "".join(p[0] for p in ad.split()[:2]).upper()

    def ciz(self, cr, t):
        a = _alfa(t, self.t0, self.t1)
        if a <= 0:
            return
        tr = TARAFLAR[self.taraf]
        r, g, b = tr["renk"]
        mx, my, R = 520, 520, 250
        don = (t - self.t0) * 0.15
        # madalyon
        cr.save()
        cr.translate(mx, my)
        s = 0.9 + 0.1 * yumusat((t - self.t0) / 1.2)
        cr.scale(s, s)
        cr.arc(8, 14, R + 26, 0, 2 * math.pi)
        cr.set_source_rgba(0, 0, 0, 0.45 * a)
        cr.fill()
        grad = cairo.RadialGradient(-60, -80, 20, 0, 0, R + 20)
        grad.add_color_stop_rgba(0, min(1, r * 1.5), min(1, g * 1.5), min(1, b * 1.5), a)
        grad.add_color_stop_rgba(1, r * 0.55, g * 0.55, b * 0.55, a)
        cr.arc(0, 0, R + 20, 0, 2 * math.pi)
        cr.set_source(grad)
        cr.fill()
        for rr, w in ((R + 20, 6), (R - 4, 2)):
            cr.arc(0, 0, rr, 0, 2 * math.pi)
            cr.set_source_rgba(*tr["vurgu"], a)
            cr.set_line_width(w)
            cr.stroke()
        # dönen süs noktaları
        for i in range(36):
            ang = don + i * 2 * math.pi / 36
            cr.arc(math.cos(ang) * (R + 8), math.sin(ang) * (R + 8), 3.2 if i % 3 else 5, 0, 2 * math.pi)
            cr.set_source_rgba(*tr["vurgu"], 0.9 * a)
            cr.fill()
        mb = 190 if len(self.monogram) <= 2 else 130
        _yazi(cr, self.monogram, 0, mb * 0.33, mb, aile="Caladea", renk=tr["vurgu"], alfa=a,
              kontur=((0, 0, 0), 6, 0.35))
        cr.restore()

        # metin bloğu
        x = 900
        kay = (1 - yumusat((t - self.t0) / 0.9)) * 40
        _yazi(cr, self.unvan.upper(), x + kay, 300, 30, aile="Inter", hiza="sol", renk=ALTIN, alfa=a)
        _yazi(cr, self.ad, x + kay, 395, 92, aile="Caladea", hiza="sol", renk=KREM, alfa=a)
        _yazi(cr, self.yillar, x + kay, 450, 34, aile="Caladea", hiza="sol", italik=True, kalin=False,
              renk=(0.85, 0.8, 0.7), alfa=a)
        cr.rectangle(x + kay, 485, 520 * yumusat((t - self.t0 - 0.3) / 1.0), 3)
        cr.set_source_rgba(*tr["renk"], a)
        cr.fill()
        y = 560
        cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(34)
        for (tm, metin) in self.maddeler:
            am = a * yumusat((t - tm) / 0.6)
            if am <= 0:
                cr.set_font_size(34)
                y += 56 * len(_sar(cr, metin, 860)) + 18
                continue
            dx = (1 - yumusat((t - tm) / 0.6)) * 30
            cr.rectangle(x + dx, y - 22, 12, 12)
            cr.set_source_rgba(*tr["vurgu"], am)
            cr.fill()
            cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(34)
            for satir in _sar(cr, metin, 860):
                _yazi(cr, satir, x + 34 + dx, y, 34, aile="Inter", kalin=False, hiza="sol",
                      renk=KREM, alfa=am)
                y += 48
            y += 26


class ZamanCizelgesi:
    """Yatay zaman çizgisi; olaylar sırayla belirir. olaylar: [(t, yil, metin, taraf), ...]"""

    katman = 5

    def __init__(self, baslik, olaylar, t0, t1):
        self.baslik, self.olaylar, self.t0, self.t1 = baslik, olaylar, t0, t1

    def ciz(self, cr, t):
        a = _alfa(t, self.t0, self.t1)
        if a <= 0:
            return
        _yazi(cr, self.baslik.upper(), DUNYA_G / 2, 170, 44, aile="Caladea", renk=KREM, alfa=a)
        cr.rectangle(DUNYA_G / 2 - 140, 195, 280, 3)
        cr.set_source_rgba(*ALTIN, a)
        cr.fill()
        x0, x1, y = 170, DUNYA_G - 170, 540
        n = len(self.olaylar)
        xs = [x0 + (x1 - x0) * (i + 0.5) / n for i in range(n)]
        # ilerleme çizgisi
        cr.rectangle(x0, y - 2, x1 - x0, 4)
        cr.set_source_rgba(1, 1, 1, 0.18 * a)
        cr.fill()
        son = x0
        for (tm, *_), x in zip(self.olaylar, xs):
            if t >= tm:
                son = x0 + (x - x0) * yumusat((t - tm) / 0.8) if son < x else son
                son = max(son, x0 + (x - x0) * yumusat((t - tm) / 0.8))
        cr.rectangle(x0, y - 3, son - x0, 6)
        cr.set_source_rgba(*ALTIN, a)
        cr.fill()
        for i, ((tm, yil, metin, taraf), x) in enumerate(zip(self.olaylar, xs)):
            ae = a * yumusat((t - tm) / 0.7)
            if ae <= 0:
                continue
            tr = TARAFLAR[taraf]
            ust = i % 2 == 0
            cr.arc(x, y, 16 * (0.6 + 0.4 * ae), 0, 2 * math.pi)
            cr.set_source_rgba(*tr["renk"], ae)
            cr.fill_preserve()
            cr.set_source_rgba(*tr["vurgu"], ae)
            cr.set_line_width(4)
            cr.stroke()
            yon = -1 if ust else 1
            cr.move_to(x, y + yon * 20)
            cr.line_to(x, y + yon * 70)
            cr.set_source_rgba(*tr["vurgu"], 0.7 * ae)
            cr.set_line_width(2)
            cr.stroke()
            yy = y - 100 if ust else y + 120
            _yazi(cr, yil, x, yy, 50, aile="Caladea", renk=tr["vurgu"], alfa=ae)
            cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(28)
            satirlar = _sar(cr, metin, (x1 - x0) / n - 20)
            if ust:
                ty = yy - 60 - (len(satirlar) - 1) * 38
            else:
                ty = yy + 50
            for s in satirlar:
                _yazi(cr, s, x, ty, 28, aile="Inter", kalin=False, renk=KREM, alfa=ae)
                ty += 38


class Karsilastirma:
    """İki ordunun yan yana karşılaştırması. sol/sag: dict(taraf, baslik, sayi, alt, maddeler=[(t, metin)])"""

    katman = 5

    def __init__(self, sol, sag, t0, t1, baslik=None):
        self.sol, self.sag, self.t0, self.t1, self.baslik = sol, sag, t0, t1, baslik

    def _panel(self, cr, p, x, t, a, gecikme):
        tr = TARAFLAR[p["taraf"]]
        ap = a * yumusat((t - self.t0 - gecikme) / 0.8)
        if ap <= 0:
            return
        w, h, y = 760, 700, 190
        _yuvarlak_dikdortgen(cr, x, y, w, h, 18)
        cr.set_source_rgba(0.06, 0.05, 0.04, 0.72 * ap)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["renk"], ap)
        cr.set_line_width(3)
        cr.stroke()
        cr.rectangle(x, y, w, 90)
        cr.set_source_rgba(*tr["renk"], 0.9 * ap)
        cr.fill()
        _yazi(cr, p["baslik"].upper(), x + w / 2, y + 60, 40, aile="Caladea", renk=KREM, alfa=ap)
        _yazi(cr, p["sayi"], x + w / 2, y + 230, 104, aile="Caladea", renk=tr["vurgu"], alfa=ap)
        _yazi(cr, p.get("alt", ""), x + w / 2, y + 285, 28, aile="Inter", kalin=False,
              renk=(0.85, 0.8, 0.7), alfa=ap)
        yy = y + 370
        for (tm, metin) in p.get("maddeler", ()):
            am = ap * yumusat((t - tm) / 0.6)
            cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(31)
            satirlar = _sar(cr, metin, w - 110)
            if am > 0:
                cr.arc(x + 50, yy - 10, 7, 0, 2 * math.pi)
                cr.set_source_rgba(*tr["vurgu"], am)
                cr.fill()
                for i, s in enumerate(satirlar):
                    _yazi(cr, s, x + 74, yy + i * 42, 31, aile="Inter", kalin=False, hiza="sol",
                          renk=KREM, alfa=am)
            yy += 42 * len(satirlar) + 24

    def ciz(self, cr, t):
        a = _alfa(t, self.t0, self.t1)
        if a <= 0:
            return
        if self.baslik:
            _yazi(cr, self.baslik.upper(), DUNYA_G / 2, 140, 40, aile="Caladea", renk=KREM, alfa=a)
        self._panel(cr, self.sol, 150, t, a, 0)
        self._panel(cr, self.sag, DUNYA_G - 150 - 760, t, a, 0.5)
        _yazi(cr, "&", DUNYA_G / 2, 600, 90, aile="Caladea", renk=ALTIN,
              alfa=a * yumusat((t - self.t0 - 0.9) / 0.6), italik=True)


class AlintiKarti:
    """Ortada büyük alıntı + kaynak. Metin kelime kelime belirmez, bir bütün olarak açılır."""

    katman = 5

    def __init__(self, metin, kim, t0, t1, taraf=None):
        self.metin, self.kim, self.t0, self.t1, self.taraf = metin, kim, t0, t1, taraf

    def ciz(self, cr, t):
        a = _alfa(t, self.t0, self.t1, gir=1.0)
        if a <= 0:
            return
        renk = TARAFLAR[self.taraf]["vurgu"] if self.taraf else ALTIN
        _yazi(cr, "“", 300, 420, 360, aile="Caladea", renk=renk, alfa=0.35 * a)
        cr.select_font_face("Caladea", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(58)
        satirlar = _sar(cr, self.metin, 1300)
        y = DUNYA_Y / 2 - (len(satirlar) - 1) * 40 - 30
        kay = (1 - yumusat((t - self.t0) / 1.2)) * 20
        for s in satirlar:
            _yazi(cr, s, DUNYA_G / 2, y + kay, 58, aile="Caladea", kalin=False, italik=True,
                  renk=KREM, alfa=a)
            y += 80
        cr.rectangle(DUNYA_G / 2 - 60, y + 6, 120, 3)
        cr.set_source_rgba(*renk, a)
        cr.fill()
        _yazi(cr, "— " + self.kim, DUNYA_G / 2, y + 70, 34, aile="Inter", renk=renk, alfa=a)


class BuyukYazi:
    """Sahne içinde ortalanmış büyük başlık (örn. '1071' veya 'Haçlı Seferleri')."""

    katman = 6

    def __init__(self, ana, t0, t1, ust=None, alt=None, boyut=150):
        self.ana, self.t0, self.t1, self.ust, self.alt, self.boyut = ana, t0, t1, ust, alt, boyut

    def ciz(self, cr, t):
        a = _alfa(t, self.t0, self.t1)
        if a <= 0:
            return
        s = 1.08 - 0.08 * yumusat((t - self.t0) / 1.5)
        cr.save()
        cr.translate(DUNYA_G / 2, DUNYA_Y / 2)
        cr.scale(s, s)
        if self.ust:
            _yazi(cr, self.ust.upper(), 0, -self.boyut * 0.75, 34, aile="Inter", kalin=False, renk=ALTIN, alfa=a)
        _yazi(cr, self.ana, 0, self.boyut * 0.33, self.boyut, aile="Caladea", renk=KREM, alfa=a,
              kontur=((0, 0, 0), 8, 0.4))
        if self.alt:
            _yazi(cr, self.alt, 0, self.boyut * 0.33 + 80, 40, aile="Caladea", kalin=False, italik=True,
                  renk=(0.88, 0.83, 0.72), alfa=a)
        cr.restore()
