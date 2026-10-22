"""Kuş bakışı savaş alanı: çizgi film tarzı ordu birlikleri, ok akınları, toz, yakın plan pencereleri.

OrduBirligi: tepeden görülen küçük asker/atlı jetonlarından oluşan küme; önünde/arkasında arma sancağı.
Konum, yön (aci: 0 = sağa bakar), yayılma, dağılma anahtar karelerle canlandırılır; hareket ederken
jetonlar sallanır, atlılar toz kaldırır. OkAkini iki birlik arasında kavisli ok yağmuru çizer.
YakinPlan, ekranın bir köşesinde çerçeveli pencerede bir karakteri gösterir (savaştan duygu anı).
"""
import importlib.util
import math
import os
import random

import cairo

from .cizim import G, Y, sekil, ince_cizgi, daire_yolu, elips_yolu, kutu_yolu, poligon_yolu, koyu, acik, yazi, KONTUR
from .zaman import Iz, yumusak

_amb = None


def _amblem():
    """Arma çizimleri tarih_video/motor/amblem.py ile ortak (çift başlı kartal, haç...)."""
    global _amb
    if _amb is None:
        yol = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "motor", "amblem.py")
        spec = importlib.util.spec_from_file_location("ortak_amblem", yol)
        _amb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_amb)
    return _amb


TARAF = {  # renk, vurgu, başlık rengi
    "bizans": ((0.5, 0.2, 0.55), (0.98, 0.8, 0.3), (0.75, 0.77, 0.82)),
    "selcuklu": ((0.1, 0.55, 0.5), (0.95, 0.97, 0.92), (0.2, 0.35, 0.6)),
    "notr": ((0.6, 0.45, 0.25), (0.95, 0.9, 0.8), (0.4, 0.3, 0.2)),
}
AT = [(0.45, 0.28, 0.15), (0.3, 0.2, 0.12), (0.58, 0.4, 0.22), (0.35, 0.3, 0.28)]


class OrduBirligi:
    """tur: piyade | agir (zırhlı süvari) | atli_okcu | suvari. sira×kol jeton dizilir (önü aci yönünde)."""

    katman = 3

    def __init__(self, taraf, tur, x, y, sira=3, kol=6, aci=0.0, alfa=0.0, tohum=0, ad=None, aralik=None, olcek=1.6):
        self.taraf, self.tur, self.ad, self.olcek = taraf, tur, ad, olcek
        self.atli = tur in ("agir", "atli_okcu", "suvari")
        self.aralik = aralik or tuple(v * olcek for v in ((26, 20) if self.atli else (18, 16)))
        rnd = random.Random(tohum)
        self.jetonlar = []
        for i in range(sira):
            for j in range(kol):
                dx = -(i - (sira - 1) / 2) * self.aralik[0] + rnd.uniform(-3, 3)
                dy = (j - (kol - 1) / 2) * self.aralik[1] + (self.aralik[1] / 2 if i % 2 else 0) + rnd.uniform(-3, 3)
                self.jetonlar.append((dx, dy, rnd.random(), rnd.choice(AT), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
        self.iz = Iz(dict(x=x, y=y, aci=aci, alfa=alfa, yayilma=1.0, titre=0.0, dagil=0.0))

    # ------------------------------------------------------------ hareket
    def belir(self, t, sure=0.6):
        self.iz.ekle(t + sure, dict(alfa=1.0), sure=sure)
        return self

    def kaybol(self, t, sure=0.6):
        self.iz.ekle(t + sure, dict(alfa=0.0), sure=sure)
        return self

    def git(self, t0, t1, x=None, y=None, aci=None, yayilma=None, egri="yumusak"):
        h = {k: v for k, v in dict(x=x, y=y, aci=aci, yayilma=yayilma).items() if v is not None}
        self.iz.ekle(t1, h, sure=t1 - t0, egri=egri)
        return self

    def don(self, t, aci, sure=0.6):
        self.iz.ekle(t + sure, dict(aci=aci), sure=sure)
        return self

    def titre(self, t0, t1, guc=1.0):
        self.iz.ekle(t0 + 0.15, dict(titre=guc), sure=0.15)
        self.iz.ekle(t1, dict(titre=0.0), sure=0.3)
        return self

    def dagil(self, t, sure=1.5):
        """Bozgun: jetonlar rastgele yönlere saçılır ve solar."""
        self.iz.ekle(t + sure, dict(dagil=1.0), sure=sure, egri="yavasla")
        return self

    def merkez(self, t):
        return self.iz("x", t), self.iz("y", t)

    # ------------------------------------------------------------ çizim
    def ciz(self, cr, t):
        d = self.iz.deger(t)
        a = d["alfa"] * (1 - d["dagil"] * 0.85)
        if a <= 0.01:
            return
        renk, vurgu, baslik = TARAF.get(self.taraf, TARAF["notr"])
        once = self.iz.deger(t - 0.15)
        hiz = math.hypot(d["x"] - once["x"], d["y"] - once["y"]) / 0.15
        hareket = min(1.0, hiz / 60)
        ac = math.radians(d["aci"])
        ca, sa = math.cos(ac), math.sin(ac)
        noktalar = []
        for (dx, dy, faz, atr, rx, ry) in self.jetonlar:
            dx *= d["yayilma"]
            dy *= d["yayilma"]
            dx += rx * 70 * d["dagil"] + math.sin(t * 9 + faz * 20) * 4 * d["titre"]
            dy += ry * 70 * d["dagil"] + math.cos(t * 8 + faz * 17) * 4 * d["titre"]
            x = d["x"] + dx * ca - dy * sa
            y = d["y"] + dx * sa + dy * ca
            noktalar.append((y, x, faz, atr))
        # toz (atlılar hareket ederken arkada)
        if self.atli and hareket > 0.3:
            for (y, x, faz, _) in noktalar[::3]:
                for k in range(2):
                    u = (t * 1.6 + faz + k * 0.5) % 1.0
                    px, py = x - ca * (14 + u * 30), y - sa * (14 + u * 30)
                    cr.arc(px, py + 4, 6 + u * 10, 0, 2 * math.pi)
                    cr.set_source_rgba(0.85, 0.78, 0.6, 0.35 * (1 - u) * hareket * a)
                    cr.fill()
        for (y, x, faz, atr) in sorted(noktalar):
            bob = math.sin(t * 12 + faz * 30) * 1.6 * hareket
            self._jeton(cr, x, y + bob, ac, renk, baslik, atr, a, faz, t)
        # sancak (kümenin arkasında)
        if d["dagil"] < 0.5:
            arka = (len(self.jetonlar) and max(abs(j[0]) for j in self.jetonlar)) * d["yayilma"] + 18
            bx, by = d["x"] - ca * arka, d["y"] - sa * arka
            cr.save()
            cr.translate(bx, by)
            cr.scale(1.35, 1.35)
            self._sancak(cr, 0, 0, renk, vurgu, a * (1 - d["dagil"] * 2), t)
            cr.restore()
        if self.ad and d["alfa"] > 0.5 and d["dagil"] < 0.3:
            yazi(cr, self.ad, d["x"], d["y"] + max(abs(j[1]) for j in self.jetonlar) * d["yayilma"] + 36, 25,
                 renk=(1, 1, 1), alfa=a, kontur=0.2)

    def _jeton(self, cr, x, y, ac, renk, baslik, atr, a, faz, t):
        cr.save()
        cr.translate(x, y)
        cr.rotate(ac)
        cr.scale(self.olcek, self.olcek)
        if self.atli:  # at (uzun gövde + baş), üstünde süvari
            sekil(cr, elips_yolu(13, 6.5), atr, alfa=a, kalin=2.2, golge=0.15, parlama=False)
            sekil(cr, elips_yolu(5, 3.5, 13, 0), koyu(atr, 0.9), alfa=a, kalin=2, golge=0, parlama=False)
            sekil(cr, daire_yolu(6.2, -1, 0), renk, alfa=a, kalin=2.2, golge=0.2, parlama=False)
            sekil(cr, daire_yolu(3.4, -1, 0), baslik, alfa=a, kalin=1.6, golge=0, parlama=False)
            if self.tur == "atli_okcu":
                cr.arc(3, 0, 6, -1.0, 1.0)
                cr.set_source_rgba(0.45, 0.28, 0.12, a)
                cr.set_line_width(2)
                cr.stroke()
            if self.tur == "agir":
                ince_cizgi(cr, [(2, -5), (16, -5)], kalin=2, renk=(0.8, 0.82, 0.86), alfa=a, egri=False)
        else:  # piyade: gövde, miğfer, önde kalkan
            sekil(cr, daire_yolu(6.5), renk, alfa=a, kalin=2.2, golge=0.2, parlama=False)
            sekil(cr, daire_yolu(3.6), baslik, alfa=a, kalin=1.6, golge=0, parlama=False)
            sekil(cr, kutu_yolu(5, -6, 4, 12, 2), acik(renk, 0.3), alfa=a, kalin=1.8, golge=0, parlama=False)
        cr.restore()

    def _sancak(self, cr, x, y, renk, vurgu, a, t):
        if a <= 0.01:
            return
        ince_cizgi(cr, [(x, y), (x, y - 46)], kalin=3.5, renk=(0.35, 0.22, 0.1), alfa=a, egri=False)
        dal = math.sin(t * 5 + x * 0.01) * 3
        yol = poligon_yolu([(x + 2, y - 46), (x + 34, y - 44 + dal), (x + 34, y - 22 + dal), (x + 2, y - 24)])
        sekil(cr, yol, renk, alfa=a, kalin=2.5, golge=0.1, parlama=False)
        cr.save()
        cr.translate(x + 18, y - 34 + dal * 0.5)
        _amblem().sembol(cr, self.taraf if self.taraf in ("bizans", "selcuklu") else "notr", 10, vurgu, a)
        cr.restore()


class OkAkini:
    """kaynak birlikten hedef birliğe kavisli ok yağmuru (t0..t1 arası sürekli)."""

    katman = 6

    def __init__(self, kaynak, hedef, t0, t1, yogunluk=10, tohum=0):
        self.k, self.h, self.t0, self.t1, self.n = kaynak, hedef, t0, t1, yogunluk
        rnd = random.Random(tohum)
        self.oklar = [(rnd.random(), rnd.uniform(-30, 30), rnd.uniform(-30, 30), rnd.uniform(-25, 25),
                       rnd.uniform(-25, 25)) for _ in range(yogunluk)]

    def ciz(self, cr, t):
        if not (self.t0 <= t <= self.t1 + 0.9):
            return
        for faz, ax, ay, bx, by in self.oklar:
            t_at = self.t0 + ((t - self.t0 - faz * 0.9) // 0.9) * 0.9 + faz * 0.9
            u = (t - t_at) / 0.9
            if t_at < self.t0 or t_at > self.t1 or not 0 <= u <= 1:
                continue
            x0, y0 = self.k.merkez(t_at)
            x1, y1 = self.h.merkez(t_at + 0.9)
            x0, y0, x1, y1 = x0 + ax, y0 + ay, x1 + bx, y1 + by
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            yuk = math.sin(u * math.pi) * 60  # tepeden bakışta yükseklik: gölgeden ayrılma
            aci = math.atan2(y1 - y0 - math.cos(u * math.pi) * 60 * math.pi * 0.3, x1 - x0)
            # gölge
            cr.save()
            cr.translate(x, y)
            cr.rotate(math.atan2(y1 - y0, x1 - x0))
            cr.move_to(-10, 0)
            cr.line_to(10, 0)
            cr.set_source_rgba(0, 0, 0, 0.2)
            cr.set_line_width(2)
            cr.stroke()
            cr.restore()
            cr.save()
            cr.translate(x, y - yuk * 0.5)
            cr.rotate(aci)
            cr.scale(1.5, 1.5)
            ince_cizgi(cr, [(-14, 0), (10, 0)], kalin=2.6, renk=(0.3, 0.18, 0.1), egri=False)
            ince_cizgi(cr, [(-14, 0), (-19, -4)], kalin=2, renk=(0.95, 0.95, 0.95), egri=False)
            ince_cizgi(cr, [(-14, 0), (-19, 4)], kalin=2, renk=(0.95, 0.95, 0.95), egri=False)
            cr.move_to(10, -3.5)
            cr.line_to(17, 0)
            cr.line_to(10, 3.5)
            cr.close_path()
            cr.set_source_rgb(*KONTUR)
            cr.fill()
            cr.restore()


class YakinPlan:
    """Ekran köşesinde çizgi roman karesi gibi yakın plan; içinde bir karakter canlandırılır."""

    katman = 16
    ekran = True

    def __init__(self, karakter, t0, t1, konum="sag_alt", zemin=(0.98, 0.85, 0.55), baslik=None):
        self.k, self.t0, self.t1, self.konum, self.zemin, self.baslik = karakter, t0, t1, konum, zemin, baslik
        self.w, self.h = 300, 270

    def ciz(self, cr, t):
        if not (self.t0 <= t <= self.t1):
            return
        gir = min(1.0, (t - self.t0) / 0.35)
        cik = min(1.0, (self.t1 - t) / 0.3)
        s = yumusak(min(gir, cik))
        if s <= 0.01:
            return
        x = G - self.w - 40 if "sag" in self.konum else 40
        y = Y - self.h - 120 if "alt" in self.konum else 70
        cr.save()
        cr.translate(x + self.w / 2, y + self.h / 2)
        cr.scale(s, s)
        cr.rotate(-0.025 if "sag" in self.konum else 0.025)
        cr.translate(-self.w / 2, -self.h / 2)
        sekil(cr, kutu_yolu(6, 8, self.w, self.h, 14), (0, 0, 0), alfa=0.35, kalin=0, golge=0, parlama=False)
        yol = kutu_yolu(0, 0, self.w, self.h, 14)
        cr.save()
        cr.new_path()
        yol(cr)
        cr.clip()
        g = cairo.RadialGradient(self.w / 2, self.h * 0.45, 10, self.w / 2, self.h / 2, self.w * 0.8)
        g.add_color_stop_rgb(0, *acik(self.zemin, 0.3))
        g.add_color_stop_rgb(1, *koyu(self.zemin, 0.8))
        cr.set_source(g)
        cr.paint()
        for k in range(14):  # hız çizgileri
            cr.save()
            cr.translate(self.w / 2, self.h * 0.45)
            cr.rotate(k * math.pi / 7 + t * 0.2)
            cr.move_to(60, -4)
            cr.line_to(260, -12)
            cr.line_to(260, 12)
            cr.line_to(60, 4)
            cr.set_source_rgba(1, 1, 1, 0.18)
            cr.fill()
            cr.restore()
        cr.translate(self.w / 2, self.h + 40)
        cr.scale(0.82, 0.82)
        self.k.ciz(cr, t)
        cr.restore()
        cr.new_path()
        yol(cr)
        cr.set_source_rgb(*KONTUR)
        cr.set_line_width(7)
        cr.stroke()
        if self.baslik:
            sekil(cr, kutu_yolu(12, -18, len(self.baslik) * 13 + 30, 36, 10), (0.12, 0.1, 0.14), kalin=4,
                  golge=0, parlama=False)
            yazi(cr, self.baslik, 27, 8, 24, renk=(1, 1, 1), hiza="sol", kontur=0)
        cr.restore()


class Karartma:
    """Gün batımı / akşam tonu (ekran üstü renk perdesi)."""

    katman = 15
    ekran = True

    def __init__(self, t0, t1, renk=(0.95, 0.45, 0.2), azami=0.35):
        self.t0, self.t1, self.renk, self.azami = t0, t1, renk, azami

    def ciz(self, cr, t):
        if t < self.t0:
            return
        u = yumusak((t - self.t0) / max(self.t1 - self.t0, 0.01))
        cr.set_source_rgba(*self.renk, self.azami * u)
        cr.paint()
