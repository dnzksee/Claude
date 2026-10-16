"""Savaş animasyonu motoru.

Bir `Video` nesnesine birlikler, komutanlar, oklar, ok yağmuru, yazılar ve kamera
hareketleri eklenir; `video.kaydet()` ffmpeg ile 1080p MP4 üretir.

Tüm zamanlar saniye cinsindendir. Konumlar 1920x1080 dünya koordinatıdır.
Birlik görünümü kasıtlı olarak "dikdörtgen blok + birlik tipi işareti" şeklindedir
(örnek kanaldaki daire/yıldız dilinden farklı, kendi görsel kimliğimiz).
"""
import math
import random
import subprocess
import cairo

from .harita import DUNYA_G, DUNYA_Y, OLCEK

G, Y = 1920, 1080

TARAFLAR = {}


def taraf_tanimla(ad, renk, vurgu=(0.95, 0.85, 0.55)):
    """renk: (r,g,b) 0..1 — birlik dolgu rengi; vurgu: çerçeve/işaret rengi."""
    TARAFLAR[ad] = {"renk": renk, "vurgu": vurgu}


# ---------------------------------------------------------------- yardımcılar
def yumusat(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Iz:
    """Özellik başına ayrı anahtar kare izi. Farklı özellikler (konum, saydamlık, açı...)
    birbirinden bağımsız ve üst üste binen zamanlarda canlandırılabilir."""

    def __init__(self, baslangic):
        self.izler = {o: [(-1e9, float(v))] for o, v in baslangic.items()}

    def _tek(self, o, t):
        k = self.izler[o]
        if t <= k[0][0]:
            return k[0][1]
        for i in range(1, len(k)):
            if t <= k[i][0]:
                (t0, a), (t1, b) = k[i - 1], k[i]
                return a + (b - a) * (yumusat((t - t0) / (t1 - t0)) if t1 > t0 else 1)
        return k[-1][1]

    def ekle(self, t, ozl, sure=None):
        """t anında ozl değerlerine ulaş. sure verilirse geçiş t-sure'de başlar, yoksa ani olur."""
        for o, v in ozl.items():
            bas_t = t - (sure or 0)
            v0 = self._tek(o, bas_t)
            # bu aralığa düşen eski kareleri at, yeni geçişi yerleştir
            k = [kk for kk in self.izler[o] if not (bas_t <= kk[0] <= t)]
            k += [(bas_t, v0), (t, float(v))] if sure else [(t, float(v))]
            self.izler[o] = sorted(k, key=lambda kk: kk[0])
        return self

    def deger(self, t):
        return {o: self._tek(o, t) for o in self.izler}


def _yazi(cr, metin, x, y, boyut, aile="Inter", kalin=True, renk=(1, 1, 1), alfa=1.0,
          hiza="orta", kontur=None, italik=False):
    cr.select_font_face(aile, cairo.FONT_SLANT_ITALIC if italik else cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD if kalin else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(boyut)
    ext = cr.text_extents(metin)
    if hiza == "orta":
        x -= ext.x_advance / 2
    elif hiza == "sag":
        x -= ext.x_advance
    cr.move_to(x, y)
    cr.text_path(metin)
    if kontur:
        cr.set_source_rgba(*kontur[0], alfa * kontur[2] if len(kontur) > 2 else alfa)
        cr.set_line_width(kontur[1])
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke_preserve()
    cr.set_source_rgba(*renk, alfa)
    cr.fill()
    return ext


def _yuvarlak_dikdortgen(cr, x, y, g, y_, r):
    cr.new_sub_path()
    cr.arc(x + g - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + g - r, y + y_ - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + y_ - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


# ---------------------------------------------------------------- öğeler
class Birlik:
    """Dikdörtgen birlik bloğu. tip: piyade | suvari | okcu | atli_okcu | agir_suvari"""

    katman = 2

    def __init__(self, taraf, tip, x, y, g=220, d=46, aci=0, alfa=0.0, etiket=None):
        self.taraf, self.tip, self.etiket = taraf, tip, etiket
        self.iz = Iz({"x": x, "y": y, "g": g, "d": d, "aci": aci, "alfa": alfa, "titresim": 0})

    # kısa yollar ----------------------------------------------------
    def belir(self, t, sure=1.0):
        self.iz.ekle(t + sure, {"alfa": 1}, sure=sure)
        return self

    def kaybol(self, t, sure=1.0):
        self.iz.ekle(t + sure, {"alfa": 0}, sure=sure)
        return self

    def git(self, t0, t1, **ozl):
        self.iz.ekle(t1, ozl, sure=t1 - t0)
        return self

    def savas(self, t0, t1):
        """Çarpışma sırasında blok titrer."""
        self.iz.ekle(t0 + 0.3, {"titresim": 1}, sure=0.3)
        self.iz.ekle(t1, {"titresim": 1})
        self.iz.ekle(t1 + 0.3, {"titresim": 0}, sure=0.3)
        return self

    def merkez(self, t):
        d = self.iz.deger(t)
        return d["x"], d["y"]

    def ciz(self, cr, t):
        d = self.iz.deger(t)
        if d["alfa"] <= 0.01:
            return
        tr = TARAFLAR[self.taraf]
        r, g_, b = tr["renk"]
        a = d["alfa"]
        cr.save()
        jx = math.sin(t * 37) * 2.5 * d["titresim"]
        jy = math.cos(t * 29) * 2.0 * d["titresim"]
        cr.translate(d["x"] + jx, d["y"] + jy)
        cr.rotate(math.radians(d["aci"]))
        w, h = d["g"], d["d"]

        if self.tip == "atli_okcu":
            self._atli_okcu(cr, w, h, (r, g_, b), tr["vurgu"], a, t)
            cr.restore()
            return

        # gölge
        _yuvarlak_dikdortgen(cr, -w / 2 + 5, -h / 2 + 7, w, h, 6)
        cr.set_source_rgba(0, 0, 0, 0.32 * a)
        cr.fill()
        # gövde
        _yuvarlak_dikdortgen(cr, -w / 2, -h / 2, w, h, 6)
        grad = cairo.LinearGradient(0, -h / 2, 0, h / 2)
        grad.add_color_stop_rgba(0, min(1, r * 1.25), min(1, g_ * 1.25), min(1, b * 1.25), 0.95 * a)
        grad.add_color_stop_rgba(1, r * 0.8, g_ * 0.8, b * 0.8, 0.95 * a)
        cr.set_source(grad)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["vurgu"], a)
        cr.set_line_width(3)
        cr.stroke()
        # ön hat (cephe) çizgisi: birliğin baktığı yön üst kenardır
        cr.move_to(-w / 2 + 6, -h / 2 + 4)
        cr.line_to(w / 2 - 6, -h / 2 + 4)
        cr.set_source_rgba(1, 1, 1, 0.55 * a)
        cr.set_line_width(3)
        cr.stroke()
        # tip işareti (kutu içinde)
        self._isaret(cr, min(h * 0.62, 34), tr["vurgu"], a)
        cr.restore()

    def _isaret(self, cr, s, vurgu, a):
        cr.set_source_rgba(*vurgu, a)
        cr.set_line_width(3)
        cr.rectangle(-s * 0.8, -s / 2, s * 1.6, s)
        cr.stroke()
        if self.tip == "piyade":
            cr.move_to(-s * 0.8, -s / 2); cr.line_to(s * 0.8, s / 2)
            cr.move_to(-s * 0.8, s / 2); cr.line_to(s * 0.8, -s / 2)
            cr.stroke()
        elif self.tip in ("suvari", "agir_suvari"):
            cr.move_to(-s * 0.8, s / 2); cr.line_to(s * 0.8, -s / 2)
            cr.stroke()
            if self.tip == "agir_suvari":
                cr.move_to(-s * 0.8, -s / 2); cr.line_to(s * 0.8, s / 2)
                cr.stroke()
                cr.rectangle(-s * 0.8, -s / 2, s * 1.6, s)
                cr.set_line_width(5); cr.stroke()
        elif self.tip == "okcu":
            cr.arc(0, s * 0.15, s * 0.42, math.pi * 1.1, math.pi * 1.9)
            cr.stroke()
            cr.move_to(0, s * 0.35); cr.line_to(0, -s * 0.45)
            cr.stroke()

    def _atli_okcu(self, cr, w, h, renk, vurgu, a, t):
        """Atlı okçular: dağınık küçük üçgen kümesi (hareketli, canlı görünür)."""
        rnd = random.Random(id(self) & 0xFFFF)
        n = max(6, int(w * h / 700))
        for i in range(n):
            px = (rnd.random() - 0.5) * w
            py = (rnd.random() - 0.5) * h
            px += math.sin(t * 2.3 + i) * 3
            py += math.cos(t * 1.7 + i * 1.3) * 3
            s = 15
            cr.move_to(px, py - s)
            cr.line_to(px + s * 0.85, py + s * 0.6)
            cr.line_to(px - s * 0.85, py + s * 0.6)
            cr.close_path()
            cr.set_source_rgba(0, 0, 0, 0.3 * a)
            cr.fill_preserve()
            cr.set_source_rgba(*renk, a)
            cr.fill_preserve()
            cr.set_source_rgba(*vurgu, a)
            cr.set_line_width(2)
            cr.stroke()


class Komutan:
    """Sancak + isim levhası. Bir birliğe bağlanabilir ya da kendi izi olabilir."""

    katman = 4
    zoom_duyarli = True

    def __init__(self, ad, taraf, birlik=None, x=0, y=0, ofset=(0, -70), alfa=0.0, unvan=None):
        self.ad, self.taraf, self.birlik, self.ofset, self.unvan = ad, taraf, birlik, ofset, unvan
        self.iz = Iz({"x": x, "y": y, "alfa": alfa, "esir": 0})

    def belir(self, t, sure=0.8):
        self.iz.ekle(t + sure, {"alfa": 1}, sure=sure)
        return self

    def kaybol(self, t, sure=0.8):
        self.iz.ekle(t + sure, {"alfa": 0}, sure=sure)
        return self

    def esir(self, t):
        self.iz.ekle(t + 0.6, {"esir": 1}, sure=0.6)
        return self

    def ciz(self, cr, t, kamera_zoom=1.0):
        d = self.iz.deger(t)
        a = d["alfa"]
        if a <= 0.01:
            return
        if self.birlik:
            bx, by = self.birlik.merkez(t)
            x, y = bx + self.ofset[0], by + self.ofset[1]
        else:
            x, y = d["x"], d["y"]
        tr = TARAFLAR[self.taraf]
        cr.save()
        cr.translate(x, y)
        s = 1 / max(kamera_zoom, 0.8) ** 0.5  # yakınlaşınca levha aşırı büyümesin
        cr.scale(s, s)
        # sancak direği
        cr.move_to(0, 22); cr.line_to(0, -44)
        cr.set_source_rgba(0.2, 0.15, 0.1, a)
        cr.set_line_width(4); cr.stroke()
        # dalgalanan bayrak
        dal = math.sin(t * 4) * 3
        cr.move_to(2, -44)
        cr.curve_to(14, -48 + dal, 26, -40 - dal, 38, -44 + dal)
        cr.line_to(38, -22 + dal)
        cr.curve_to(26, -18 - dal, 14, -26 + dal, 2, -22)
        cr.close_path()
        cr.set_source_rgba(*tr["renk"], a)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["vurgu"], a)
        cr.set_line_width(2); cr.stroke()
        # isim levhası
        cr.select_font_face("Caladea", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(26)
        ext = cr.text_extents(self.ad)
        lw = ext.x_advance + 36
        lh = 40 if not self.unvan else 60
        _yuvarlak_dikdortgen(cr, -lw / 2, 26, lw, lh, 8)
        cr.set_source_rgba(0.08, 0.07, 0.06, 0.82 * a)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["vurgu"], a)
        cr.set_line_width(2); cr.stroke()
        # taraf rengi şerit
        cr.rectangle(-lw / 2 + 6, 26 + lh - 7, lw - 12, 3)
        cr.set_source_rgba(*tr["renk"], a); cr.fill()
        _yazi(cr, self.ad, 0, 55, 26, aile="Caladea", renk=(0.98, 0.93, 0.8), alfa=a)
        if self.unvan:
            _yazi(cr, self.unvan, 0, 76, 16, aile="Inter", kalin=False, renk=(0.85, 0.8, 0.7), alfa=a)
        if d["esir"] > 0.01:
            e = d["esir"]
            cr.save()
            cr.translate(lw / 2 + 40, 40)
            cr.rotate(-0.18)
            cr.scale(1.6 - 0.6 * e, 1.6 - 0.6 * e)
            _yuvarlak_dikdortgen(cr, -70, -23, 140, 46, 6)
            cr.set_source_rgba(0.98, 0.94, 0.86, 0.85 * e * a)
            cr.fill_preserve()
            cr.set_source_rgba(0.75, 0.1, 0.08, e * a)
            cr.set_line_width(5); cr.stroke()
            _yazi(cr, "ESİR", 0, 12, 34, renk=(0.75, 0.1, 0.08), alfa=e * a)
            cr.restore()
        cr.restore()


class HareketOku:
    """Zamanla uzayan kalın hareket oku. noktalar dünya koordinatı."""

    katman = 1

    def __init__(self, taraf, noktalar, t0, t1, t_son=None, kalinlik=26, renk=None):
        self.taraf, self.p, self.t0, self.t1 = taraf, noktalar, t0, t1
        self.t_son = t_son if t_son is not None else t1 + 2.5
        self.kalinlik, self.renk = kalinlik, renk

    def _ornekle(self, n=80):
        p = self.p
        out = []
        for i in range(len(p) - 1):
            p0 = p[i - 1] if i > 0 else p[i]
            p1, p2 = p[i], p[i + 1]
            p3 = p[i + 2] if i + 2 < len(p) else p2
            for k in range(n):
                u = k / n
                u2, u3 = u * u, u * u * u
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)
                out.append((x, y))
        out.append(p[-1])
        return out

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t_son + 0.8:
            return
        ilerleme = yumusat((t - self.t0) / max(self.t1 - self.t0, 0.01))
        alfa = 1 - yumusat((t - self.t_son) / 0.8)
        pts = self._ornekle()
        k = max(2, int(len(pts) * ilerleme))
        pts = pts[:k]
        renk = self.renk or TARAFLAR[self.taraf]["renk"]
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        aci = math.atan2(y2 - y1, x2 - x1)
        w = self.kalinlik
        # gövde (gölge + dolgu)
        for kalin, rgba in ((w + 8, (0, 0, 0, 0.25)), (w + 4, (*TARAFLAR[self.taraf]["vurgu"], 0.9)), (w, (*renk, 0.85))):
            cr.move_to(*pts[0])
            for p in pts[1:]:
                cr.line_to(*p)
            cr.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3] * alfa)
            cr.set_line_width(kalin)
            cr.set_line_cap(cairo.LINE_CAP_BUTT)
            cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.stroke()
        # uç
        cr.save()
        cr.translate(x2, y2)
        cr.rotate(aci)
        cr.move_to(w * 1.6, 0)
        cr.line_to(-w * 0.3, -w * 1.2)
        cr.line_to(-w * 0.3, w * 1.2)
        cr.close_path()
        cr.set_source_rgba(*renk, 0.95 * alfa)
        cr.fill_preserve()
        cr.set_source_rgba(*TARAFLAR[self.taraf]["vurgu"], alfa)
        cr.set_line_width(3)
        cr.stroke()
        cr.restore()


class OkYagmuru:
    """Kaynak birlikten hedef birliğe parabolik uçan oklar (parçacık efekti)."""

    katman = 3

    def __init__(self, kaynak, hedef, t0, t1, yogunluk=14, ucus=1.1, tohum=1):
        self.kaynak, self.hedef, self.t0, self.t1 = kaynak, hedef, t0, t1
        rnd = random.Random(tohum)
        self.oklar = []
        n = int((t1 - t0) * yogunluk)
        for _ in range(n):
            self.oklar.append((t0 + rnd.random() * (t1 - t0 - ucus), ucus * (0.8 + rnd.random() * 0.4),
                               (rnd.random() - 0.5) * 120, (rnd.random() - 0.5) * 50,
                               (rnd.random() - 0.5) * 200, (rnd.random() - 0.5) * 40))

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1 + 1:
            return
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for (ts, sure, kx, ky, hx, hy) in self.oklar:
            u = (t - ts) / sure
            if not 0 <= u <= 1:
                continue
            sx, sy = self.kaynak.merkez(ts)
            ex, ey = self.hedef.merkez(ts + sure)
            sx, sy, ex, ey = sx + kx, sy + ky, ex + hx, ey + hy
            yay = -160
            def nokta(v):
                return sx + (ex - sx) * v, sy + (ey - sy) * v + yay * 4 * v * (1 - v)
            x, y = nokta(u)
            px, py = nokta(max(0, u - 0.06))
            cr.move_to(px, py)
            cr.line_to(x, y)
            cr.set_source_rgba(0.12, 0.09, 0.06, 0.85)
            cr.set_line_width(2.4)
            cr.stroke()


class EtiketBalonu:
    """Haritada bir noktaya bağlı kısa açıklama (örn. 'Sahte ricat!')."""

    katman = 5
    zoom_duyarli = True

    def __init__(self, metin, t0, t1, x=0, y=0, birlik=None, ofset=(0, -90), renk=(0.98, 0.93, 0.8)):
        self.metin, self.t0, self.t1, self.x, self.y = metin, t0, t1, x, y
        self.birlik, self.ofset, self.renk = birlik, ofset, renk

    def ciz(self, cr, t, kamera_zoom=1.0):
        if t < self.t0 or t > self.t1:
            return
        a = min(yumusat((t - self.t0) / 0.4), 1 - yumusat((t - self.t1 + 0.4) / 0.4))
        if self.birlik:
            bx, by = self.birlik.merkez(t)
            x, y = bx + self.ofset[0], by + self.ofset[1]
        else:
            x, y = self.x, self.y
        cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(28)
        ext = cr.text_extents(self.metin)
        w, h = ext.x_advance + 32, 48
        cr.save()
        cr.translate(x, y)
        s = (0.85 + 0.15 * a) / max(kamera_zoom, 1) ** 0.75
        cr.scale(s, s)
        _yuvarlak_dikdortgen(cr, -w / 2, -h / 2, w, h, 10)
        cr.set_source_rgba(0.08, 0.07, 0.06, 0.85 * a)
        cr.fill()
        cr.move_to(-10, h / 2); cr.line_to(0, h / 2 + 14); cr.line_to(10, h / 2)
        cr.close_path(); cr.fill()
        _yazi(cr, self.metin, 0, 10, 28, renk=self.renk, alfa=a)
        cr.restore()


# ---------------------------------------------------------------- ekran katmanı (kameradan bağımsız)
class BaslikKarti:
    katman = 10
    ekran = True

    def __init__(self, ust, ana, alt, t0, t1):
        self.ust, self.ana, self.alt, self.t0, self.t1 = ust, ana, alt, t0, t1

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        a = min(yumusat((t - self.t0) / 0.8), 1 - yumusat((t - self.t1 + 0.8) / 0.8))
        cr.rectangle(0, 0, G, Y)
        grad = cairo.LinearGradient(0, 0, 0, Y)
        grad.add_color_stop_rgba(0, 0, 0, 0, 0.35 * a)
        grad.add_color_stop_rgba(0.5, 0, 0, 0, 0.6 * a)
        grad.add_color_stop_rgba(1, 0, 0, 0, 0.35 * a)
        cr.set_source(grad)
        cr.fill()
        kay = (1 - a) * 30
        _yazi(cr, self.ust, G / 2, Y / 2 - 90 + kay, 30, aile="Inter", kalin=False,
              renk=(0.9, 0.82, 0.62), alfa=a)
        _yazi(cr, self.ana, G / 2, Y / 2 + 10 + kay, 104, aile="Caladea",
              renk=(0.99, 0.95, 0.85), alfa=a, kontur=((0, 0, 0), 6, 0.5))
        cr.rectangle(G / 2 - 220 * a, Y / 2 + 40, 440 * a, 3)
        cr.set_source_rgba(0.9, 0.75, 0.4, a)
        cr.fill()
        _yazi(cr, self.alt, G / 2, Y / 2 + 95 + kay, 38, aile="Caladea", kalin=False,
              renk=(0.92, 0.88, 0.78), alfa=a, italik=True)


class BolumEtiketi:
    """Sol üstte bölüm adı + tarih (YouTube bölüm başlıklarıyla uyumlu)."""

    katman = 10
    ekran = True

    def __init__(self, metin, t0, t1, alt=None):
        self.metin, self.t0, self.t1, self.alt = metin, t0, t1, alt

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        a = min(yumusat((t - self.t0) / 0.6), 1 - yumusat((t - self.t1 + 0.6) / 0.6))
        x = 60 - (1 - a) * 40
        cr.rectangle(x, 58, 6, 70 if self.alt else 46)
        cr.set_source_rgba(0.9, 0.72, 0.35, a)
        cr.fill()
        _yazi(cr, self.metin.upper(), x + 22, 95, 34, aile="Inter", hiza="sol",
              renk=(1, 0.97, 0.9), alfa=a, kontur=((0, 0, 0), 5, 0.6))
        if self.alt:
            _yazi(cr, self.alt, x + 22, 124, 22, aile="Inter", kalin=False, hiza="sol",
                  renk=(0.95, 0.88, 0.72), alfa=a, kontur=((0, 0, 0), 4, 0.6))


class Lejant:
    katman = 10
    ekran = True

    def __init__(self, ogeler, t0, t1):
        """ogeler: [(taraf, 'Bizans'), ...]"""
        self.ogeler, self.t0, self.t1 = ogeler, t0, t1

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        a = min(yumusat((t - self.t0) / 0.6), 1 - yumusat((t - self.t1 + 0.6) / 0.6))
        x, y = G - 330, 60
        _yuvarlak_dikdortgen(cr, x, y, 270, 30 + 44 * len(self.ogeler), 10)
        cr.set_source_rgba(0.08, 0.07, 0.06, 0.7 * a)
        cr.fill()
        for i, (taraf, ad) in enumerate(self.ogeler):
            yy = y + 22 + i * 44
            _yuvarlak_dikdortgen(cr, x + 20, yy, 46, 26, 4)
            cr.set_source_rgba(*TARAFLAR[taraf]["renk"], a)
            cr.fill_preserve()
            cr.set_source_rgba(*TARAFLAR[taraf]["vurgu"], a)
            cr.set_line_width(2)
            cr.stroke()
            _yazi(cr, ad, x + 84, yy + 21, 24, aile="Inter", hiza="sol", renk=(1, 0.96, 0.88), alfa=a)


class AltYazi:
    """Seslendirme ile senkron alt yazı (videoya gömülü). Ayrıca .srt de üretilir."""

    katman = 20
    ekran = True

    def __init__(self, satirlar):
        """satirlar: [(t0, t1, metin), ...]"""
        self.satirlar = satirlar

    @staticmethod
    def _sar(cr, metin, genislik):
        kelimeler, satirlar, mevcut = metin.split(), [], ""
        for k in kelimeler:
            dene = (mevcut + " " + k).strip()
            if cr.text_extents(dene).x_advance > genislik and mevcut:
                satirlar.append(mevcut)
                mevcut = k
            else:
                mevcut = dene
        if mevcut:
            satirlar.append(mevcut)
        return satirlar

    def ciz(self, cr, t):
        for (t0, t1, metin) in self.satirlar:
            if t0 <= t <= t1:
                cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(44)
                satirlar = self._sar(cr, metin, 1500)
                taban = Y - 70 - (len(satirlar) - 1) * 56
                for i, s in enumerate(satirlar):
                    _yazi(cr, s, G / 2, taban + i * 56, 44, renk=(1, 1, 1),
                          kontur=((0, 0, 0), 8, 0.9))
                return


# ---------------------------------------------------------------- video
class Sahne:
    """Kendi arka planı, kamerası ve öğeleri olan zaman aralığı. Sahneler arasında çapraz geçiş yapılır."""

    GECIS = 0.8

    def __init__(self, t0, t1, arka_plan):
        self.t0, self.t1, self.arka_plan = t0, t1, arka_plan
        self.ogeler = []
        self.kamera = Iz({"x": DUNYA_G / 2, "y": DUNYA_Y / 2, "zoom": 1.0})

    def ekle(self, *ogeler):
        self.ogeler.extend(ogeler)
        return ogeler[0] if len(ogeler) == 1 else ogeler

    def kamera_git(self, t0, t1, x=None, y=None, zoom=None):
        ozl = {k: v for k, v in (("x", x), ("y", y), ("zoom", zoom)) if v is not None}
        self.kamera.ekle(t1, ozl, sure=t1 - t0)

    def kamera_ayarla(self, t, x=None, y=None, zoom=None):
        ozl = {k: v for k, v in (("x", x), ("y", y), ("zoom", zoom)) if v is not None}
        self.kamera.ekle(t, ozl)

    def kare(self, cr, t):
        k = self.kamera.deger(t)
        z = k["zoom"]
        yari_g, yari_y = G / 2 / z, Y / 2 / z
        kx = min(max(k["x"], yari_g), DUNYA_G - yari_g) if z >= 1 else DUNYA_G / 2
        ky = min(max(k["y"], yari_y), DUNYA_Y - yari_y) if z >= 1 else DUNYA_Y / 2
        cr.save()
        cr.translate(G / 2, Y / 2)
        cr.scale(z, z)
        cr.translate(-kx, -ky)
        cr.save()
        cr.scale(1 / OLCEK, 1 / OLCEK)
        cr.set_source_surface(self.arka_plan, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_GOOD)
        cr.paint()
        cr.restore()
        for o in sorted(self.ogeler, key=lambda o: o.katman):
            if getattr(o, "zoom_duyarli", False):
                o.ciz(cr, t, z)
            else:
                o.ciz(cr, t)
        cr.restore()


class Video:
    def __init__(self, arka_plan=None, fps=30):
        self.fps = fps
        self.sahneler = []
        self.ekran_ogeleri = []
        self.karartma = Iz({"a": 1.0})  # 1 = tamamen siyah
        self._varsayilan = self.sahne(0, 1e9, arka_plan) if arka_plan is not None else None

    def sahne(self, t0, t1, arka_plan):
        s = Sahne(t0, t1, arka_plan)
        self.sahneler.append(s)
        return s

    # tek sahneli kullanım için kısa yollar
    @property
    def kamera(self):
        return self._varsayilan.kamera

    def kamera_git(self, *a, **k):
        self._varsayilan.kamera_git(*a, **k)

    def ekle(self, *ogeler):
        for o in ogeler:
            (self.ekran_ogeleri if getattr(o, "ekran", False) else self._varsayilan.ogeler).append(o)
        return ogeler[0] if len(ogeler) == 1 else ogeler

    def ekran(self, *ogeler):
        self.ekran_ogeleri.extend(ogeler)
        return ogeler[0] if len(ogeler) == 1 else ogeler

    def acilis(self, t, sure=1.0):
        self.karartma.ekle(t + sure, {"a": 0}, sure=sure)

    def kapanis(self, t, sure=1.0):
        self.karartma.ekle(t + sure, {"a": 1}, sure=sure)

    def kare(self, cr, t):
        aktif = [s for s in self.sahneler if s.t0 <= t <= s.t1 + Sahne.GECIS]
        aktif.sort(key=lambda s: s.t0)
        for i, s in enumerate(aktif):
            gelis = yumusat((t - s.t0) / Sahne.GECIS) if i > 0 else 1.0
            if gelis >= 0.999:
                s.kare(cr, t)
            else:
                cr.push_group()
                s.kare(cr, t)
                cr.pop_group_to_source()
                cr.paint_with_alpha(gelis)

        for o in sorted(self.ekran_ogeleri, key=lambda o: o.katman):
            o.ciz(cr, t)

        kar = self.karartma.deger(t)["a"]
        if kar > 0.001:
            cr.rectangle(0, 0, G, Y)
            cr.set_source_rgba(0, 0, 0, kar)
            cr.fill()

    def kaydet(self, cikti, sure, ses=None, onizleme_kareleri=()):
        """MP4 olarak kaydet. onizleme_kareleri: PNG olarak da kaydedilecek zamanlar."""
        yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, G, Y)
        cr = cairo.Context(yuzey)
        komut = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                 "-s", f"{G}x{Y}", "-r", str(self.fps), "-i", "-"]
        if ses:
            komut += ["-i", ses, "-c:a", "aac", "-b:a", "192k", "-shortest"]
        komut += ["-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "animation", "-pix_fmt", "yuv420p",
                  "-movflags", "+faststart", cikti]
        p = subprocess.Popen(komut, stdin=subprocess.PIPE)
        toplam = int(sure * self.fps)
        onizleme = sorted(onizleme_kareleri)
        for i in range(toplam):
            t = i / self.fps
            cr.set_source_rgb(0, 0, 0)
            cr.paint()
            self.kare(cr, t)
            yuzey.flush()
            p.stdin.write(bytes(yuzey.get_data()))
            while onizleme and t >= onizleme[0]:
                yuzey.write_to_png(cikti.rsplit(".", 1)[0] + f"_kare_{onizleme.pop(0):05.1f}.png")
            if i % (self.fps * 10) == 0:
                print(f"  {t:6.1f}s / {sure:.1f}s", flush=True)
        p.stdin.close()
        p.wait()
        if p.returncode:
            raise RuntimeError("ffmpeg hata verdi")
