"""Kanal görselleri (Kroniknâme): YouTube profil resmi seçenekleri (800×800) ve kanal kapağı (2560×1440).

    python3 araclar/kanal_gorselleri.py      # kanal/ klasörüne PNG'ler
Çizgi film tarzı videolardakiyle aynı: kalın siyah dış çizgi, düz renk, cel gölge.
"""
import math
import os
import sys

import cairo

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
os.environ.setdefault("CIZGI_OLCEK", "1")

from motor.cizim import sekil, yazi, ince_cizgi, daire_yolu, kutu_yolu, egri_yolu, poligon_yolu, koyu, KONTUR  # noqa: E402
from motor.nesneler import _kilic  # noqa: E402

CIKTI = os.path.join(KOK, "kanal")
KIRMIZI = (0.62, 0.14, 0.12)
KOYU_KIRMIZI = (0.3, 0.06, 0.06)
ALTIN = (1.0, 0.78, 0.18)
PARSOMEN = (0.97, 0.9, 0.72)


def zemin(cr, w, h, ust=KIRMIZI, alt=KOYU_KIRMIZI, isin=True):
    g = cairo.RadialGradient(w / 2, h * 0.45, 10, w / 2, h / 2, max(w, h) * 0.75)
    g.add_color_stop_rgb(0, *ust)
    g.add_color_stop_rgb(1, *alt)
    cr.set_source(g)
    cr.paint()
    if isin:
        cr.save()
        cr.translate(w / 2, h * 0.47)
        for k in range(24):
            cr.rotate(math.pi / 12)
            cr.move_to(0, 0)
            cr.line_to(max(w, h), -max(w, h) * 0.07)
            cr.line_to(max(w, h), max(w, h) * 0.07)
            cr.close_path()
            cr.set_source_rgba(1, 1, 1, 0.07)
            cr.fill()
        cr.restore()


def kiliclar(cr, x, y, s):
    for yon in (-1, 1):
        cr.save()
        cr.translate(x, y)
        cr.rotate(yon * 0.62)
        cr.scale(s, s)
        _kilic(cr, 0, {})
        cr.restore()


def kitap(cr, x, y, s):
    """Açık kitap (nâme): deri cilt, kavisli sayfalar, satırlar, kurdele."""
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    sekil(cr, egri_yolu([(-150, -55), (0, -40), (150, -55), (155, 70), (0, 88), (-155, 70)], gerginlik=0.25),
          (0.55, 0.16, 0.12), olcek=300, parlama=False)
    for i in (-1, 1):
        sayfa = egri_yolu([(0, -42), (i * 70, -62), (i * 140, -50), (i * 140, 62), (i * 70, 52), (0, 74)],
                          gerginlik=0.35)
        sekil(cr, sayfa, PARSOMEN, olcek=170, golge=0.08, parlama=False)
        for k in range(5):
            yy = -32 + k * 20
            ince_cizgi(cr, [(i * 22, yy + 6), (i * 70, yy - 4), (i * 120, yy + 1)], kalin=3.5,
                       renk=(0.6, 0.48, 0.32))
    ince_cizgi(cr, [(0, -42), (0, 74)], kalin=5, egri=False)
    sekil(cr, poligon_yolu([(12, 70), (30, 70), (30, 120), (21, 108), (12, 120)]), (0.85, 0.15, 0.15), kalin=4,
          golge=0.15, parlama=False)
    cr.restore()


def halka(cr, w, h, r, kalin):
    cr.arc(w / 2, h / 2, r, 0, 2 * math.pi)
    cr.set_source_rgb(*KONTUR)
    cr.set_line_width(kalin + 10)
    cr.stroke()
    cr.arc(w / 2, h / 2, r, 0, 2 * math.pi)
    cr.set_source_rgb(*ALTIN)
    cr.set_line_width(kalin)
    cr.stroke()


def profil(ad, cizim):
    W = 800
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, W)
    cr = cairo.Context(s)
    zemin(cr, W, W)
    cizim(cr, W)
    halka(cr, W, W, 372, 18)  # YouTube daire kırpar; altın çerçeve dairenin içinde kalır
    yol = os.path.join(CIKTI, ad)
    s.write_to_png(yol)
    return yol


def secenek_a(cr, W):
    """Videolardaki logo: kalkan + çapraz kılıçlar."""
    sekil(cr, daire_yolu(230, W / 2, W / 2), KIRMIZI, olcek=460)
    sekil(cr, daire_yolu(185, W / 2, W / 2), ALTIN, golge=0.12, parlama=False, kalin=10)
    kiliclar(cr, W / 2, W / 2 + 10, 2.6)


def secenek_b(cr, W):
    """Kılıçlar + açık kitap (kronik + nâme)."""
    kiliclar(cr, W / 2, W / 2 - 40, 2.9)
    kitap(cr, W / 2, W / 2 + 120, 1.75)


def secenek_c(cr, W):
    """Kılıçlar + kitap + kanal adı."""
    kiliclar(cr, W / 2, W / 2 - 95, 2.3)
    kitap(cr, W / 2, W / 2 + 45, 1.4)
    yazi(cr, "KRONİKNÂME", W / 2, W / 2 + 255, 84, renk=ALTIN, kontur=0.16)


def kapak():
    """YouTube kanal kapağı 2560×1440; her cihazda görünen güvenli alan ortadaki 1546×423."""
    w, h = 2560, 1440
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(s)
    zemin(cr, w, h)
    cr.save()
    cr.translate(w / 2 - 560, h / 2)
    kiliclar(cr, 0, -20, 1.5)
    kitap(cr, 0, 70, 0.95)
    cr.restore()
    yazi(cr, "KRONİKNÂME", w / 2 + 120, h / 2 + 30, 150, renk=ALTIN, kontur=0.15)
    yazi(cr, "Tarihin büyük savaşları, çizgi filmle", w / 2 + 120, h / 2 + 115, 54, renk=(1, 0.95, 0.85),
         kontur=0.18)
    yol = os.path.join(CIKTI, "kapak_2560x1440.png")
    s.write_to_png(yol)
    return yol


if __name__ == "__main__":
    os.makedirs(CIKTI, exist_ok=True)
    for ad, f in (("profil_A_kalkan.png", secenek_a), ("profil_B_kitap.png", secenek_b),
                  ("profil_C_yazili.png", secenek_c)):
        print(profil(ad, f))
    print(kapak())
