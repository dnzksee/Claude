"""Animasyon yoğunluğunu artıran katmanlar.

- gorsel_yukle(): kamu malı görselleri (jpg/png) kırpıp cairo yüzeyine çevirir
- PortreKarti: hükümdar/komutan adı geçince köşeden kayan madalyon portre + isim levhası
- YilRozeti: bir yıl söylendiğinde üst ortada beliren yıl şeridi
- Ikon: haritada olay simgesi (kılıç, taç, alev, kale, parşömen) — zıplayarak belirir
- Tablo: minyatür/tablo üzerinde Ken Burns (yavaş yakınlaşma/kaydırma) + çerçeve + kaynak yazısı
- oto_katman(): anlatımdaki yıl, kişi ve yer adlarına otomatik görsel ekler
"""
import math
import os
import re

import cairo
import numpy as np
from PIL import Image

from .sahne import G, Y, TARAFLAR, yumusat, _yazi, _yuvarlak_dikdortgen
from .zamanlama import sade

VARLIK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "varliklar", "gorseller")
KREM = (0.97, 0.93, 0.84)
ALTIN = (0.90, 0.74, 0.42)
_gorsel_onbellek = {}


def gorsel_yukle(anahtar, kirp=None, azami=1600, dondur=0):
    """anahtar: varliklar/gorseller/<anahtar>.(jpg|png). kirp: (x0, y0, x1, y1) 0..1 oranları.
    dondur: kırpılan parçayı derece cinsinden döndürür (yatan bir figürü dikleştirmek için)."""
    k = (anahtar, kirp, azami, dondur)
    if k in _gorsel_onbellek:
        return _gorsel_onbellek[k]
    yol = next((os.path.join(VARLIK, anahtar + u) for u in (".jpg", ".png", ".jpeg")
                if os.path.exists(os.path.join(VARLIK, anahtar + u))), None)
    if yol is None:
        _gorsel_onbellek[k] = None
        return None
    im = Image.open(yol).convert("RGBA")
    if kirp:
        w, h = im.size
        im = im.crop((int(kirp[0] * w), int(kirp[1] * h), int(kirp[2] * w), int(kirp[3] * h)))
    if dondur:
        w0, h0 = im.size
        im = im.rotate(dondur, resample=Image.BICUBIC, expand=False)
        # döndürmeden kalan boş köşeleri atmak için ortadan kırp
        m = 0.15
        im = im.crop((int(w0 * m), int(h0 * m), int(w0 * (1 - m)), int(h0 * (1 - m))))
    if max(im.size) > azami:
        o = azami / max(im.size)
        im = im.resize((int(im.width * o), int(im.height * o)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    alfa = a[..., 3:4] / 255.0
    bgra = np.empty(a.shape, np.uint8)
    bgra[..., 0] = (a[..., 2:3] * alfa)[..., 0]
    bgra[..., 1] = (a[..., 1:2] * alfa)[..., 0]
    bgra[..., 2] = (a[..., 0:1] * alfa)[..., 0]
    bgra[..., 3] = a[..., 3]
    yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, im.width, im.height)
    hedef = np.ndarray((im.height, im.width, 4), np.uint8, buffer=yuzey.get_data(),
                       strides=(yuzey.get_stride(), 4, 1))
    hedef[:] = bgra
    yuzey.mark_dirty()
    _gorsel_onbellek[k] = yuzey
    return yuzey


def _gorsel_ciz(cr, yuzey, x, y, w, h, alfa=1.0, kaplama=True):
    """Yüzeyi (x,y,w,h) kutusuna sığdırarak (kaplama=True: taşırıp doldurarak) çizer."""
    iw, ih = yuzey.get_width(), yuzey.get_height()
    o = max(w / iw, h / ih) if kaplama else min(w / iw, h / ih)
    cr.save()
    cr.rectangle(x, y, w, h)
    cr.clip()
    cr.translate(x + (w - iw * o) / 2, y + (h - ih * o) / 2)
    cr.scale(o, o)
    cr.set_source_surface(yuzey, 0, 0)
    cr.get_source().set_filter(cairo.FILTER_GOOD)
    cr.paint_with_alpha(alfa)
    cr.restore()


def _temsili_portre(cr, r, kultur, renk, alfa):
    """Görsel yoksa: kültüre göre başlıklı stilize büst (madalyon içinde)."""
    cr.save()
    # omuzlar
    cr.move_to(-r * 0.85, r)
    cr.curve_to(-r * 0.8, r * 0.35, -r * 0.45, r * 0.25, 0, r * 0.25)
    cr.curve_to(r * 0.45, r * 0.25, r * 0.8, r * 0.35, r * 0.85, r)
    cr.close_path()
    cr.set_source_rgba(*renk, alfa)
    cr.fill()
    # boyun + baş
    cr.rectangle(-r * 0.12, r * 0.05, r * 0.24, r * 0.25)
    cr.set_source_rgba(0.80, 0.62, 0.46, alfa)
    cr.fill()
    cr.save()
    cr.translate(0, -r * 0.18)
    cr.scale(r * 0.27, r * 0.33)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.restore()
    cr.fill()
    # sakal
    cr.move_to(-r * 0.24, -r * 0.12)
    cr.curve_to(-r * 0.22, r * 0.22, r * 0.22, r * 0.22, r * 0.24, -r * 0.12)
    cr.curve_to(r * 0.1, r * 0.02, -r * 0.1, r * 0.02, -r * 0.24, -r * 0.12)
    cr.set_source_rgba(0.18, 0.12, 0.08, alfa)
    cr.fill()
    if kultur == "selcuklu":  # sarık + sorguç
        cr.save()
        cr.translate(0, -r * 0.48)
        cr.scale(r * 0.36, r * 0.2)
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgba(0.95, 0.93, 0.88, alfa)
        cr.fill()
        cr.move_to(r * 0.05, -r * 0.62)
        cr.curve_to(r * 0.2, -r * 0.9, r * 0.35, -r * 0.85, r * 0.3, -r * 0.7)
        cr.set_source_rgba(*ALTIN, alfa)
        cr.set_line_width(r * 0.05)
        cr.stroke()
    elif kultur == "bizans":  # taç (kamelaukion) + sarkıtlar
        cr.rectangle(-r * 0.3, -r * 0.62, r * 0.6, r * 0.2)
        cr.set_source_rgba(*ALTIN, alfa)
        cr.fill()
        cr.arc(0, -r * 0.62, r * 0.3, math.pi, 2 * math.pi)
        cr.fill()
        for dx in (-0.31, 0.31):
            cr.move_to(r * dx, -r * 0.42)
            cr.line_to(r * dx, -r * 0.1)
            cr.set_line_width(r * 0.04)
            cr.stroke()
    else:  # papalık / batı: basit başlık
        cr.move_to(-r * 0.28, -r * 0.42)
        cr.line_to(0, -r * 0.95)
        cr.line_to(r * 0.28, -r * 0.42)
        cr.close_path()
        cr.set_source_rgba(0.95, 0.93, 0.88, alfa)
        cr.fill()
    cr.restore()


class PortreKarti:
    """Ekran öğesi. kisi: KISILER sözlüğündeki kayıt (ad, unvan, yillar, taraf, gorsel, kirp, kultur)."""

    katman = 15
    ekran = True

    def __init__(self, kisi, t0, t1, taraf_konum="sol"):
        self.k, self.t0, self.t1, self.konum = kisi, t0, t1, taraf_konum
        self.yuzey = (gorsel_yukle(kisi["gorsel"], kisi.get("kirp"), 700, kisi.get("dondur", 0))
                      if kisi.get("gorsel") else None)

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        gir = yumusat((t - self.t0) / 0.55)
        cik = yumusat((t - self.t1 + 0.45) / 0.45)
        a = min(gir, 1 - cik)
        tr = TARAFLAR.get(self.k.get("taraf", "notr"), TARAFLAR.get("notr"))
        R = 92
        sol = self.konum == "sol"
        x0 = (150 if sol else G - 150) + (-(1 - gir) * 260 if sol else (1 - gir) * 260)
        y0 = 735
        cr.save()
        cr.translate(x0, y0)
        # isim levhası (madalyonun yanında)
        cr.select_font_face("Caladea", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(40)
        lw = max(cr.text_extents(self.k["ad"]).x_advance, 220) + 70
        lx = R - 20 if sol else -R + 20 - lw
        lev = yumusat((t - self.t0 - 0.2) / 0.5)
        cr.save()
        cr.rectangle(lx if sol else lx + lw * (1 - lev), -55, lw * lev, 112)
        cr.clip()
        _yuvarlak_dikdortgen(cr, lx, -52, lw, 104, 10)
        cr.set_source_rgba(0.07, 0.06, 0.05, 0.88 * a)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["vurgu"], 0.9 * a)
        cr.set_line_width(2)
        cr.stroke()
        tx = lx + (50 if sol else 20)
        _yazi(cr, self.k.get("unvan", "").upper(), tx, -14, 20, aile="Inter", hiza="sol", renk=ALTIN, alfa=a)
        _yazi(cr, self.k["ad"], tx, 26, 40, aile="Caladea", hiza="sol", renk=KREM, alfa=a)
        if self.k.get("yillar"):
            _yazi(cr, self.k["yillar"], tx, 48, 18, aile="Inter", kalin=False, hiza="sol",
                  renk=(0.8, 0.76, 0.68), alfa=a)
        cr.restore()
        # madalyon
        s = 0.7 + 0.3 * yumusat((t - self.t0) / 0.6)
        cr.scale(s, s)
        cr.arc(5, 8, R + 12, 0, 2 * math.pi)
        cr.set_source_rgba(0, 0, 0, 0.45 * a)
        cr.fill()
        cr.arc(0, 0, R + 10, 0, 2 * math.pi)
        cr.set_source_rgba(*tr["renk"], a)
        cr.fill()
        cr.save()
        cr.arc(0, 0, R, 0, 2 * math.pi)
        cr.clip()
        cr.set_source_rgb(0.85, 0.78, 0.62)
        cr.paint_with_alpha(a)
        if self.yuzey:
            yak = 1.0 + 0.06 * (t - self.t0) / max(self.t1 - self.t0, 1)  # yavaş yakınlaşma
            cr.scale(yak, yak)
            _gorsel_ciz(cr, self.yuzey, -R, -R, 2 * R, 2 * R, a)
        else:  # görsel yoksa: arma + baş harfler (uydurma yüz çizilmez)
            from .amblem import sembol
            g = cairo.RadialGradient(0, -R * 0.3, R * 0.1, 0, 0, R * 1.1)
            g.add_color_stop_rgba(0, *(min(1, c * 1.35) for c in tr["renk"]), a)
            g.add_color_stop_rgba(1, *(c * 0.55 for c in tr["renk"]), a)
            cr.set_source(g)
            cr.paint()
            sembol(cr, self.k.get("taraf", "notr"), R * 0.95, tr["vurgu"], a * 0.22)
            harf = self.k.get("monogram") or "".join(p[0] for p in self.k["ad"].replace(".", "").split()
                                                      if not set(p) <= set("IVX"))[:2].upper()
            _yazi(cr, harf, 0, R * 0.3, R * (0.95 if len(harf) == 1 else 0.75), aile="Caladea",
                  renk=tr["vurgu"], alfa=a)
        cr.restore()
        for rr, w in ((R + 10, 4), (R + 1, 2)):
            cr.arc(0, 0, rr, 0, 2 * math.pi)
            cr.set_source_rgba(*tr["vurgu"], a)
            cr.set_line_width(w)
            cr.stroke()
        cr.restore()


class YilRozeti:
    """Ekran öğesi: üst ortada yıl şeridi (yıl söylendiği anda)."""

    katman = 14
    ekran = True

    def __init__(self, yil, t0, t1=None):
        self.yil, self.t0 = yil, t0
        self.t1 = t1 if t1 is not None else t0 + 4.0

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        a = min(yumusat((t - self.t0) / 0.35), 1 - yumusat((t - self.t1 + 0.5) / 0.5))
        s = 1.25 - 0.25 * yumusat((t - self.t0) / 0.4)
        cr.save()
        cr.translate(G / 2, 78)
        cr.scale(s, s)
        w = 230
        cr.move_to(-w / 2 - 28, -34)
        cr.line_to(w / 2 + 28, -34)
        cr.line_to(w / 2 + 10, 0)
        cr.line_to(w / 2 + 28, 34)
        cr.line_to(-w / 2 - 28, 34)
        cr.line_to(-w / 2 - 10, 0)
        cr.close_path()
        cr.set_source_rgba(0.55, 0.13, 0.10, 0.92 * a)
        cr.fill_preserve()
        cr.set_source_rgba(*ALTIN, a)
        cr.set_line_width(2.5)
        cr.stroke()
        _yazi(cr, self.yil, 0, 19, 50, aile="Caladea", renk=KREM, alfa=a)
        cr.restore()


class Ikon:
    """Dünya öğesi (harita sahnelerinde). tur: kilic | tac | alev | kale | parsomen | yildiz."""

    katman = 4
    zoom_duyarli = True

    def __init__(self, tur, x, y, t0, t1=None, olcek=1.0, renk=None):
        self.tur, self.x, self.y, self.t0 = tur, x, y, t0
        self.t1 = t1 if t1 is not None else t0 + 5
        self.olcek, self.renk = olcek, renk

    def ciz(self, cr, t, kamera_zoom=1.0):
        if t < self.t0 or t > self.t1 + 0.5:
            return
        u = (t - self.t0)
        a = min(yumusat(u / 0.25), 1 - yumusat((t - self.t1) / 0.5))
        zipla = 1 + 0.35 * math.exp(-u * 5) * math.sin(u * 18)  # yaylanarak belirme
        s = self.olcek * zipla / max(kamera_zoom, 1) ** 0.7
        cr.save()
        cr.translate(self.x, self.y)
        cr.scale(s, s)
        # alt halka (dalga)
        dal = (u % 1.4) / 1.4
        cr.arc(0, 0, 26 + 30 * dal, 0, 2 * math.pi)
        cr.set_source_rgba(0.95, 0.85, 0.6, (1 - dal) * 0.6 * a)
        cr.set_line_width(3)
        cr.stroke()
        cr.arc(0, 0, 27, 0, 2 * math.pi)
        cr.set_source_rgba(0.08, 0.06, 0.05, 0.85 * a)
        cr.fill_preserve()
        cr.set_source_rgba(*ALTIN, a)
        cr.set_line_width(2.5)
        cr.stroke()
        getattr(self, "_" + self.tur)(cr, a, u)
        cr.restore()

    @staticmethod
    def _kilic(cr, a, u):
        for yon in (-1, 1):
            cr.save()
            cr.rotate(yon * math.pi / 4)
            cr.move_to(0, -19)
            cr.line_to(2.5, -15)
            cr.line_to(2.5, 9)
            cr.line_to(-2.5, 9)
            cr.line_to(-2.5, -15)
            cr.close_path()
            cr.set_source_rgba(0.88, 0.88, 0.92, a)
            cr.fill()
            cr.rectangle(-7, 9, 14, 3)
            cr.rectangle(-1.8, 12, 3.6, 7)
            cr.set_source_rgba(*ALTIN, a)
            cr.fill()
            cr.restore()
        # kıvılcım
        for k in range(5):
            v = ((u * 2 + k * 0.2) % 1.0)
            ang = k * 1.26
            cr.arc(math.cos(ang) * (8 + 22 * v), -6 + math.sin(ang) * (8 + 22 * v), 2 * (1 - v) + 0.4, 0, 2 * math.pi)
            cr.set_source_rgba(1, 0.8, 0.3, (1 - v) * a)
            cr.fill()

    @staticmethod
    def _tac(cr, a, u):
        cr.move_to(-15, 8)
        cr.line_to(-17, -10)
        cr.line_to(-8, -2)
        cr.line_to(0, -15)
        cr.line_to(8, -2)
        cr.line_to(17, -10)
        cr.line_to(15, 8)
        cr.close_path()
        cr.set_source_rgba(*ALTIN, a)
        cr.fill()
        for x in (-17, 0, 17):
            cr.arc(x, -12 if x else -17, 2.5, 0, 2 * math.pi)
            cr.set_source_rgba(0.85, 0.15, 0.12, a)
            cr.fill()

    @staticmethod
    def _alev(cr, a, u):
        for i, (dx, h, r_, g_) in enumerate(((-7, 16, 0.95, 0.35), (6, 19, 0.95, 0.45), (0, 24, 1.0, 0.65))):
            titre = math.sin(u * 14 + i * 2) * 2.5
            cr.move_to(dx - 8, 12)
            cr.curve_to(dx - 10, 0, dx - 2 + titre, -h * 0.6, dx + titre, -h)
            cr.curve_to(dx + 4 + titre, -h * 0.5, dx + 10, 0, dx + 8, 12)
            cr.close_path()
            cr.set_source_rgba(r_, g_, 0.1, 0.9 * a)
            cr.fill()

    @staticmethod
    def _kale(cr, a, u):
        cr.rectangle(-15, -6, 30, 18)
        for x in (-15, -5, 5):
            cr.rectangle(x, -12, 7, 6)
        cr.rectangle(-4, -20, 8, 14)
        cr.set_source_rgba(0.85, 0.8, 0.7, a)
        cr.fill()
        cr.rectangle(-3.5, 3, 7, 9)
        cr.set_source_rgba(0.15, 0.1, 0.08, a)
        cr.fill()
        cr.move_to(0, -20)
        cr.line_to(0, -30)
        cr.line_to(9, -27)
        cr.line_to(0, -24)
        cr.set_source_rgba(0.75, 0.15, 0.1, a)
        cr.fill()

    @staticmethod
    def _parsomen(cr, a, u):
        _yuvarlak_dikdortgen(cr, -13, -16, 26, 32, 3)
        cr.set_source_rgba(0.93, 0.86, 0.68, a)
        cr.fill()
        for yy in (-9, -3, 3):
            cr.move_to(-8, yy)
            cr.line_to(8, yy)
        cr.set_source_rgba(0.35, 0.25, 0.15, a)
        cr.set_line_width(1.5)
        cr.stroke()
        cr.arc(5, 10, 4.5, 0, 2 * math.pi)
        cr.set_source_rgba(0.75, 0.12, 0.1, a)
        cr.fill()

    @staticmethod
    def _yildiz(cr, a, u):
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = 17 if i % 2 == 0 else 7
            (cr.move_to if i == 0 else cr.line_to)(math.cos(ang) * r, math.sin(ang) * r)
        cr.close_path()
        cr.set_source_rgba(*ALTIN, a)
        cr.fill()


class Tablo:
    """Dünya öğesi: tam ekran minyatür/tablo, Ken Burns hareketiyle.
    bas/son: görselde (merkez_x, merkez_y, yakınlık) — merkez 0..1 oranları, yakınlık >= 1."""

    katman = 1

    def __init__(self, anahtar, t0, t1, bas=(0.5, 0.5, 1.0), son=(0.5, 0.5, 1.15), kaynak="", kirp=None):
        self.yuzey = gorsel_yukle(anahtar, kirp, 2400)
        self.t0, self.t1, self.bas, self.son, self.kaynak = t0, t1, bas, son, kaynak

    def ciz(self, cr, t):
        if self.yuzey is None or t < self.t0 - 1 or t > self.t1 + 1:
            return
        u = yumusat((t - self.t0) / max(self.t1 - self.t0, 0.1))
        mx = self.bas[0] + (self.son[0] - self.bas[0]) * u
        my = self.bas[1] + (self.son[1] - self.bas[1]) * u
        z = self.bas[2] + (self.son[2] - self.bas[2]) * u
        iw, ih = self.yuzey.get_width(), self.yuzey.get_height()
        # görüntü alanı: 1720x940 çerçeve içinde, görsel kaplayacak şekilde
        fx, fy, fw, fh = 100, 70, 1720, 900
        o = max(fw / iw, fh / ih) * z
        cr.save()
        cr.rectangle(fx, fy, fw, fh)
        cr.clip()
        ox = fx + fw / 2 - mx * iw * o
        oy = fy + fh / 2 - my * ih * o
        ox = min(fx, max(fx + fw - iw * o, ox))
        oy = min(fy, max(fy + fh - ih * o, oy))
        cr.translate(ox, oy)
        cr.scale(o, o)
        cr.set_source_surface(self.yuzey, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_GOOD)
        cr.paint()
        cr.restore()
        # iç kenar karartma
        grad = cairo.RadialGradient(G / 2, Y / 2, 300, G / 2, Y / 2, 1050)
        grad.add_color_stop_rgba(0, 0, 0, 0, 0)
        grad.add_color_stop_rgba(1, 0, 0, 0, 0.55)
        cr.rectangle(fx, fy, fw, fh)
        cr.set_source(grad)
        cr.fill()
        # çerçeve
        cr.rectangle(fx, fy, fw, fh)
        cr.set_source_rgba(*ALTIN, 0.9)
        cr.set_line_width(4)
        cr.stroke()
        cr.rectangle(fx - 10, fy - 10, fw + 20, fh + 20)
        cr.set_source_rgba(*ALTIN, 0.45)
        cr.set_line_width(1.5)
        cr.stroke()
        if self.kaynak:
            _yazi(cr, self.kaynak, fx + fw - 16, fy + fh - 16, 20, aile="Inter", kalin=False, hiza="sag",
                  renk=(0.95, 0.92, 0.85), alfa=0.85, kontur=((0, 0, 0), 4, 0.7), italik=True)


# ---------------------------------------------------------------- otomatik katman
_YIL = re.compile(r"^(\d{3,4})(?:'|’)?\w*[.,;:!?]?$")


def _eslesir(kelimeler, i, anahtar):
    """anahtar (bir ya da birkaç kelime) i. kelimeden başlıyor mu? Son kelimede ek payı (≤6 harf),
    önceki kelimelerde tam eşleşme aranır. Tek kelimeli anahtarlarda da ek payı uygulanır."""
    parca = [sade(p) for p in anahtar.split()]
    if i + len(parca) > len(kelimeler):
        return False
    for j, p in enumerate(parca):
        k = sade(kelimeler[i + j][1])
        son = j == len(parca) - 1
        if son:
            if not (k.startswith(p) and len(k) - len(p) <= 6):
                return False
        elif k != p:
            return False
    return True


def oto_katman(video, T, kisiler, koordinatlar=None, yil_bekleme=15.0, kisi_bekleme=60.0,
               haric_bolumler=(), haric_kisiler=()):
    """Anlatımda geçen yıllar için YilRozeti, kişiler için PortreKarti ekler.
    Harita sahnelerinde (sahne.harita tanımlıysa) geçen şehirleri nabız efektiyle vurgular.
    kisiler: {"Alparslan": {...}, "Selçuk Bey": {...}}; anahtar anlatımdaki yazılışıdır.
    "esanlam": ["Alp Arslan"] gibi ek yazılışlar verilebilir."""
    from .cografya import Sehir
    son_yil, son_kisi, son_yer = {}, {}, {}
    portre_mesgul = 0.0
    kisi_listesi = []
    for ad, kayit in kisiler.items():
        for yazilis in [ad] + list(kayit.get("esanlam", [])):
            kisi_listesi.append((yazilis, ad, kayit))
    kisi_listesi.sort(key=lambda x: -len(x[0].split()))  # önce çok kelimeli anahtarlar
    yerler = sorted((koordinatlar or {}).items(), key=lambda x: -len(x[0].split()))
    kelimeler = T.tum_kelimeler()
    for i, (t, kelime, bolum) in enumerate(kelimeler):
        if bolum in haric_bolumler:
            continue
        m = _YIL.match(kelime)
        if m and 500 <= int(m.group(1)) <= 2100:
            yil = m.group(1)
            if t - son_yil.get(yil, -1e9) > yil_bekleme:
                video.ekran(YilRozeti(yil, t - 0.1))
                son_yil[yil] = t
            continue
        bulundu = False
        for yazilis, ad, kisi in kisi_listesi:
            if _eslesir(kelimeler, i, yazilis):
                bulundu = True
                if (ad not in haric_kisiler and t - son_kisi.get(ad, -1e9) > kisi_bekleme
                        and t > portre_mesgul):
                    video.ekran(PortreKarti(kisi, t - 0.15, t + 4.6, "sag" if kisi.get("taraf") == "selcuklu" else "sol"))
                    son_kisi[ad] = t
                    portre_mesgul = t + 4.8
                break
        if bulundu:
            continue
        for ad, (lon, lat) in yerler:
            if _eslesir(kelimeler, i, ad):
                sahne = next((s for s in video.sahneler if s.t0 <= t <= s.t1), None)
                h = getattr(sahne, "harita", None) if sahne else None
                if h is not None and t - son_yer.get(ad, -1e9) > 8:
                    sahne.ekle(Sehir(h, lon, lat, ad, t - 0.1, t + 5.0, onemli=True, nabiz=True))
                    son_yer[ad] = t
                break
