"""Sahne arka planları: çizgi film tarzında çizilir, sonra alan derinliği için bulanıklaştırılır.

Arka plan ekrandan büyük (1600×900) çizilir; kamera hareket ederken daha yavaş kayar (paralaks).
Zemin (karakterlerin bastığı yer) ayrıca keskin çizilir. Yeni arka plan: ARKAPLANLAR'a bir
fonksiyon eklemek yeterli.
"""
import math
import random

import cairo

from .cizim import (sekil, ince_cizgi, daire_yolu, elips_yolu, kutu_yolu, egri_yolu, poligon_yolu, koyu, acik,
                    bulaniklastir, KONTUR)

AG, AY = 1600, 900   # arka plan boyutu
ZEMIN_Y = 610        # zemin çizgisi (dünya koordinatı)


def _gok(cr, ust, alt):
    g = cairo.LinearGradient(0, 0, 0, AY)
    g.add_color_stop_rgb(0, *ust)
    g.add_color_stop_rgb(1, *alt)
    cr.set_source(g)
    cr.paint()


def _bulut(cr, x, y, s):
    for dx, dy, r in ((-50, 8, 34), (-15, -14, 44), (30, -4, 38), (62, 12, 26), (0, 14, 34)):
        sekil(cr, daire_yolu(r * s, x + dx * s, y + dy * s), (0.98, 0.98, 1.0), kalin=0, golge=0.12, parlama=False)


def oda(cr, p):
    duvar = p.get("duvar", (0.98, 0.86, 0.62))
    cr.set_source_rgb(*duvar)
    cr.paint()
    for x in range(0, AG, 70):  # duvar kâğıdı şeritleri
        cr.rectangle(x, 0, 30, AY)
    cr.set_source_rgba(*koyu(duvar, 0.93), 1)
    cr.fill()
    # pencere
    sekil(cr, kutu_yolu(1020, 150, 330, 280, 12), (0.95, 0.95, 0.95), golge=0.08, kalin=7)
    sekil(cr, kutu_yolu(1040, 170, 290, 240, 6), (0.55, 0.8, 0.98), golge=0, kalin=5, parlama=False)
    _bulut(cr, 1150, 260, 0.9)
    ince_cizgi(cr, [(1185, 170), (1185, 410)], kalin=7, egri=False)
    ince_cizgi(cr, [(1040, 290), (1330, 290)], kalin=7, egri=False)
    # raf + kitaplar
    sekil(cr, kutu_yolu(180, 300, 380, 22, 6), (0.62, 0.4, 0.22), golge=0.2)
    rnd = random.Random(4)
    x = 200
    for _ in range(8):
        w = rnd.randint(22, 36)
        h = rnd.randint(70, 110)
        sekil(cr, kutu_yolu(x, 300 - h, w, h, 4), rnd.choice([(0.85, 0.3, 0.3), (0.3, 0.55, 0.85), (0.35, 0.7, 0.4),
                                                              (0.95, 0.75, 0.25), (0.6, 0.4, 0.75)]), kalin=4, golge=0.15,
              parlama=False)
        x += w + 4
    # çerçeve
    sekil(cr, kutu_yolu(640, 140, 220, 160, 8), (0.75, 0.5, 0.25), kalin=6)
    sekil(cr, kutu_yolu(658, 158, 184, 124, 4), (0.65, 0.85, 0.75), kalin=4, golge=0)
    sekil(cr, poligon_yolu([(670, 270), (730, 190), (790, 270)]), (0.35, 0.6, 0.45), kalin=4, golge=0.1)
    # süpürgelik
    cr.rectangle(0, 700, AG, AY - 700)
    cr.set_source_rgb(*koyu(duvar, 0.75))
    cr.fill()


def sinif(cr, p):
    oda(cr, dict(duvar=p.get("duvar", (0.82, 0.92, 0.86))))
    sekil(cr, kutu_yolu(420, 170, 760, 330, 10), (0.55, 0.36, 0.2), kalin=7)
    sekil(cr, kutu_yolu(440, 190, 720, 290, 6), (0.18, 0.38, 0.32), kalin=4, golge=0.05, parlama=False)


def doga(cr, p):
    _gok(cr, p.get("gok_ust", (0.38, 0.68, 0.98)), p.get("gok_alt", (0.78, 0.92, 1.0)))
    sekil(cr, daire_yolu(70, 1300, 160), (1.0, 0.86, 0.3), kalin=6, golge=0.1)
    for x, y, s in ((250, 150, 1.2), (700, 220, 0.9), (1050, 120, 1.0), (1500, 260, 0.8)):
        _bulut(cr, x, y, s)
    sekil(cr, egri_yolu([(-50, 620), (200, 430), (520, 520), (800, 400), (1150, 500), (1450, 410), (1700, 560),
                         (1700, 950), (-50, 950)], gerginlik=0.6), (0.45, 0.72, 0.42), olcek=500)
    sekil(cr, egri_yolu([(-50, 700), (300, 580), (700, 650), (1100, 560), (1700, 680), (1700, 950), (-50, 950)],
                        gerginlik=0.6), (0.4, 0.68, 0.35), olcek=400)
    rnd = random.Random(2)
    for _ in range(7):
        x = rnd.uniform(0, AG)
        y = rnd.uniform(560, 640)
        sekil(cr, kutu_yolu(x - 8, y - 70, 16, 70, 4), (0.55, 0.36, 0.2), kalin=4, golge=0.2)
        sekil(cr, daire_yolu(48, x, y - 100), (0.3, 0.6, 0.3), kalin=5)


def sahne(cr, p):
    _gok(cr, (0.22, 0.12, 0.32), (0.12, 0.06, 0.18))
    for x in (500, 1100):  # spot ışıkları
        g = cairo.LinearGradient(x, 0, x, 800)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.35)
        g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0.0)
        cr.move_to(x - 30, 0)
        cr.line_to(x + 30, 0)
        cr.line_to(x + 260, 800)
        cr.line_to(x - 260, 800)
        cr.close_path()
        cr.set_source(g)
        cr.fill()
    for i in (-1, 1):  # perdeler
        x0 = 0 if i < 0 else AG
        pts = [(x0, -20), (x0 + i * -330, -20)]
        for k in range(7):
            pts.append((x0 + i * (-300 + k * 40 + (15 if k % 2 else 0)), 200 + k * 100))
        pts += [(x0, 900)]
        sekil(cr, egri_yolu(pts, gerginlik=0.4), (0.78, 0.12, 0.18), olcek=400)
        for k in range(4):
            ince_cizgi(cr, [(x0 + i * -(60 + k * 60), 0), (x0 + i * -(80 + k * 50), 880)], kalin=4,
                       renk=koyu((0.78, 0.12, 0.18), 0.55))
    sekil(cr, kutu_yolu(-20, -20, AG + 40, 90, 0), (0.78, 0.12, 0.18), kalin=6)
    for x in range(0, AG, 80):
        sekil(cr, egri_yolu([(x, 70), (x + 80, 70), (x + 40, 110)]), (0.95, 0.75, 0.2), kalin=4, golge=0.15,
              parlama=False)


def beyin(cr, p):
    _gok(cr, (0.98, 0.72, 0.8), (0.86, 0.5, 0.7))
    rnd = random.Random(11)
    noktalar = [(rnd.uniform(0, AG), rnd.uniform(0, AY)) for _ in range(26)]
    for i, a in enumerate(noktalar):
        for b in noktalar[i + 1:]:
            if math.dist(a, b) < 300:
                ince_cizgi(cr, [a, ((a[0] + b[0]) / 2 + 30, (a[1] + b[1]) / 2 - 20), b], kalin=5,
                           renk=(0.75, 0.38, 0.6), alfa=0.8)
    for (x, y) in noktalar:
        g = cairo.RadialGradient(x, y, 2, x, y, 40)
        g.add_color_stop_rgba(0, 1, 1, 0.8, 0.9)
        g.add_color_stop_rgba(1, 1, 0.9, 0.9, 0.0)
        cr.set_source(g)
        cr.arc(x, y, 40, 0, 2 * math.pi)
        cr.fill()
        sekil(cr, daire_yolu(12, x, y), (1.0, 0.92, 0.6), kalin=4, golge=0.15, parlama=False)
    for _ in range(9):  # beyin kıvrımları
        x, y = rnd.uniform(0, AG), rnd.uniform(0, AY)
        ince_cizgi(cr, [(x, y), (x + 60, y - 40), (x + 120, y + 10), (x + 170, y - 30)], kalin=8,
                   renk=(0.9, 0.55, 0.72))


def sehir(cr, p):
    _gok(cr, p.get("gok_ust", (1.0, 0.62, 0.45)), p.get("gok_alt", (1.0, 0.88, 0.62)))
    rnd = random.Random(5)
    for katman, (renk, taban) in enumerate((((0.55, 0.45, 0.65), 650), ((0.38, 0.32, 0.5), 700))):
        x = -40
        while x < AG:
            w = rnd.randint(90, 170)
            h = rnd.randint(180, 420) - katman * 60
            sekil(cr, kutu_yolu(x, taban - h, w, h + 300, 6), renk, kalin=5, golge=0.12, parlama=False)
            for wy in range(taban - h + 25, taban - 20, 42):
                for wx in range(x + 16, x + w - 24, 34):
                    if rnd.random() < 0.6:
                        cr.rectangle(wx, wy, 16, 22)
                        cr.set_source_rgba(1, 0.92, 0.6, 0.85)
                        cr.fill()
            x += w + rnd.randint(0, 20)


def uzay(cr, p):
    _gok(cr, (0.05, 0.05, 0.16), (0.16, 0.08, 0.3))
    rnd = random.Random(9)
    for _ in range(220):
        x, y, r = rnd.uniform(0, AG), rnd.uniform(0, AY), rnd.uniform(0.8, 2.6)
        cr.arc(x, y, r, 0, 2 * math.pi)
        cr.set_source_rgba(1, 1, 1, rnd.uniform(0.4, 1))
        cr.fill()
    sekil(cr, daire_yolu(150, 1250, 250), (0.95, 0.6, 0.35), kalin=7)
    sekil(cr, elips_yolu(240, 34, 1250, 260), (0.9, 0.85, 0.6), kalin=6, golge=0, parlama=False)


def duz(cr, p):
    _gok(cr, p.get("ust", (0.98, 0.9, 0.7)), p.get("alt", (0.98, 0.78, 0.5)))
    # hafif ışınlar (kart arka planı)
    cr.save()
    cr.translate(AG / 2, AY / 2)
    for k in range(18):
        cr.rotate(math.pi / 9)
        cr.move_to(0, 0)
        cr.line_to(1200, -110)
        cr.line_to(1200, 110)
        cr.close_path()
        cr.set_source_rgba(1, 1, 1, 0.12)
        cr.fill()
    cr.restore()


ARKAPLANLAR = {"oda": oda, "sinif": sinif, "doga": doga, "sahne": sahne, "beyin": beyin, "sehir": sehir, "uzay": uzay,
               "duz": duz}

ZEMINLER = {
    "oda": (0.72, 0.5, 0.32), "sinif": (0.66, 0.48, 0.32), "doga": (0.42, 0.7, 0.36), "sahne": (0.55, 0.32, 0.18),
    "beyin": (0.82, 0.45, 0.62), "sehir": (0.5, 0.5, 0.55), "uzay": (0.35, 0.32, 0.45), "duz": None,
}

_onbellek = {}


def arka_plan(ad, bulanik=7.0, **p):
    """Bulanıklaştırılmış arka plan yüzeyi (önbellekli)."""
    anahtar = (ad, bulanik, tuple(sorted(p.items())))
    if anahtar not in _onbellek:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, AG, AY)
        cr = cairo.Context(s)
        ARKAPLANLAR[ad](cr, p)
        _onbellek[anahtar] = bulaniklastir(s, bulanik) if bulanik > 1 else s
    return _onbellek[anahtar]


def zemin_ciz(cr, ad, renk=None):
    """Keskin zemin (dünya koordinatında, karakterlerle aynı düzlem)."""
    renk = renk or ZEMINLER.get(ad)
    if not renk:
        return
    cr.save()
    cr.new_path()
    cr.rectangle(-800, ZEMIN_Y, 1280 + 1600, 900)
    cr.set_source_rgb(*renk)
    cr.fill()
    g = cairo.LinearGradient(0, ZEMIN_Y, 0, ZEMIN_Y + 140)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.18)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0)
    cr.rectangle(-800, ZEMIN_Y, 1280 + 1600, 140)
    cr.set_source(g)
    cr.fill()
    cr.move_to(-800, ZEMIN_Y)
    cr.line_to(2100, ZEMIN_Y)
    cr.set_source_rgb(*KONTUR)
    cr.set_line_width(5)
    cr.stroke()
    if ad in ("oda", "sinif", "sahne"):  # tahta döşeme
        for k in range(1, 5):
            y = ZEMIN_Y + k * 28 * (1 + k * 0.2)
            cr.move_to(-800, y)
            cr.line_to(2100, y)
            cr.set_source_rgba(*koyu(renk, 0.75), 1)
            cr.set_line_width(3)
            cr.stroke()
    cr.restore()
