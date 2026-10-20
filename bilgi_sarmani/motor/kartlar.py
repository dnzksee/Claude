"""Ekran üstü öğeler: Bilgi Sarmanı logosu, açılış/kapanış kartı, bölüm başlığı etiketi, altyazı."""
import math

import cairo

from .cizim import (G, Y, sekil, yazi, yazi_genislik, satirlara_bol, daire_yolu, kutu_yolu, ince_cizgi, koyu,
                    KONTUR, YAZI)
from .zaman import geri_tepme, yumusak, yavasla, hizlan

MARKA = (1.0, 0.78, 0.18)     # sarmal sarısı
MARKA2 = (0.18, 0.6, 0.95)    # mavi


def sarmal(cr, x, y, r, t=0.0, alfa=1.0, don=0.4):
    """Bilgi Sarmanı logosu: dönen kalın sarmal."""
    cr.save()
    cr.translate(x, y)
    cr.rotate(t * don)
    sekil(cr, daire_yolu(r), MARKA2, alfa=alfa, olcek=r * 2)
    noktalar = []
    for k in range(120):
        u = k / 119
        aci = u * 2.6 * 2 * math.pi
        rr = r * 0.12 + u * r * 0.68
        noktalar.append((math.cos(aci) * rr, math.sin(aci) * rr))
    for kalin, renk in ((r * 0.2, KONTUR), (r * 0.12, MARKA)):
        cr.new_path()
        cr.move_to(*noktalar[0])
        for p in noktalar[1:]:
            cr.line_to(*p)
        cr.set_source_rgba(*renk, alfa)
        cr.set_line_width(kalin)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke()
    cr.restore()


class AcilisKarti:
    """Ekranın ortasında logo + başlık + alt başlık; harf harf zıplayarak gelir."""

    katman = 20
    ekran = True

    def __init__(self, baslik, alt, t0, t1, kanal="BİLGİ SARMANI"):
        self.baslik, self.alt, self.t0, self.t1, self.kanal = baslik, alt, t0, t1, kanal

    def ciz(self, cr, t):
        if t < self.t0 - 0.1 or t > self.t1 + 0.6:
            return
        u = t - self.t0
        cik = 1 - yumusak((t - self.t1) / 0.5)
        s = geri_tepme(u / 0.6) * cik
        if s > 0.01:
            sarmal(cr, G / 2, 190, 70 * s, t, alfa=cik)
        yazi(cr, self.kanal, G / 2, 300, 30, renk=(1, 1, 1), alfa=min(1, max(0, (u - 0.3) / 0.4)) * cik, kontur=0.2)
        # başlık: her kelime ayrı zıplar
        satirlar = satirlara_bol(cr, self.baslik, 84, 1100)
        for si, satir in enumerate(satirlar):
            kel = satir.split()
            toplam = yazi_genislik(cr, satir, 84)
            x = G / 2 - toplam / 2
            for ki, k in enumerate(kel):
                gecikme = 0.5 + (si * 3 + ki) * 0.12
                v = geri_tepme(max(0.0, min(1.0, (u - gecikme) / 0.45)))
                w = yazi_genislik(cr, k + " ", 84)
                if v > 0.01:
                    cr.save()
                    cx, cy = x + yazi_genislik(cr, k, 84) / 2, 400 + si * 92
                    cr.translate(cx, cy)
                    cr.scale(v, v)
                    cr.rotate(math.sin(t * 2 + ki) * 0.02)
                    yazi(cr, k, 0, 0, 84, renk=MARKA if ki % 2 == 0 else (1, 1, 1), alfa=cik, kontur=0.17)
                    cr.restore()
                x += w
        a2 = min(1, max(0, (u - 1.4) / 0.5)) * cik
        if a2 > 0:
            yazi(cr, self.alt, G / 2, 400 + len(satirlar) * 92 + 6, 36, renk=(1, 0.95, 0.85), alfa=a2, kontur=0.18)


class KapanisKarti:
    katman = 20
    ekran = True

    def __init__(self, metin, alt, t0, t1):
        self.metin, self.alt, self.t0, self.t1 = metin, alt, t0, t1

    def ciz(self, cr, t):
        if t < self.t0 - 0.1:
            return
        u = t - self.t0
        s = geri_tepme(u / 0.6)
        sarmal(cr, G / 2, 215, 95 * s, t)
        a = min(1, max(0, (u - 0.4) / 0.5))
        for i, satir in enumerate(satirlara_bol(cr, self.metin, 64, 1050)):
            yazi(cr, satir, G / 2, 385 + i * 74, 64, renk=(1, 1, 1), alfa=a, kontur=0.17)
        a2 = min(1, max(0, (u - 1.2) / 0.5))
        if a2 > 0:
            # abone ol düğmesi
            nab = 1 + 0.05 * math.sin(t * 5)
            cr.save()
            cr.translate(G / 2, 535)
            cr.scale(nab * a2, nab * a2)
            sekil(cr, kutu_yolu(-170, -38, 340, 76, 38), (0.9, 0.15, 0.15))
            yazi(cr, self.alt, 0, 14, 38, renk=(1, 1, 1), kontur=0.14)
            cr.restore()


class BolumEtiketi:
    """Sahne başında ekranın ortasına iri gelir, sonra sol üst köşeye küçük etiket olarak yerleşir."""

    katman = 18
    ekran = True

    def __init__(self, no, baslik, t0, t1, renk=MARKA):
        self.no, self.baslik, self.t0, self.t1, self.renk = no, baslik, t0, t1, renk

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1:
            return
        u = t - self.t0
        gir = geri_tepme(u / 0.5)
        yerles = yumusak((u - 2.2) / 0.6)
        cik = 1 - yumusak((t - self.t1 + 0.35) / 0.35)
        # büyük konum -> köşe
        bx, by, bs = G / 2, 200, 1.0
        kx, ky, ks = 30, 30, 0.42
        x = bx + (kx - bx) * yerles
        y = by + (ky - by) * yerles
        s = (bs + (ks - bs) * yerles) * gir * cik
        if s < 0.02:
            return
        ust = f"BÖLÜM {self.no}"
        boy = 64
        w = max(yazi_genislik(cr, self.baslik, boy), yazi_genislik(cr, ust, 30)) + 70
        cr.save()
        cr.translate(x, y)
        cr.scale(s, s)
        ox = -w / 2 * (1 - yerles)  # ortalıyken merkezden, köşedeyken sol kenardan
        cr.rotate(-0.03 * (1 - yerles))
        sekil(cr, kutu_yolu(ox, 0, w, 130, 22), (0.12, 0.1, 0.16), golge=0, parlama=False, kalin=7)
        sekil(cr, kutu_yolu(ox + 18, -26, yazi_genislik(cr, ust, 30) + 40, 48, 16), self.renk, golge=0.1,
              parlama=False)
        yazi(cr, ust, ox + 38, 8, 30, renk=KONTUR, kontur=0, golge=False)
        yazi(cr, self.baslik, ox + 35, 98, boy, renk=(1, 1, 1), hiza="sol", kontur=0.12)
        cr.restore()


class Altyazi:
    """Alt orta altyazı; satırlar (t0, t1, metin)."""

    katman = 19
    ekran = True

    def __init__(self, satirlar, boyut=34):
        self.satirlar, self.boyut = satirlar, boyut

    def ciz(self, cr, t):
        for t0, t1, metin in self.satirlar:
            if t0 <= t < t1:
                a = min(1, (t - t0) / 0.12, (t1 - t) / 0.12)
                satir = satirlara_bol(cr, metin, self.boyut, 1100)
                for i, s in enumerate(satir[-2:]):
                    y = Y - 34 - (len(satir[-2:]) - 1 - i) * (self.boyut * 1.2)
                    yazi(cr, s, G / 2, y, self.boyut, renk=(1, 1, 1), alfa=a, kontur=0.22)
                return
