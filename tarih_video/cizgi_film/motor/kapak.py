"""YouTube kapak resmi (küçük resim): 1280×720 PNG (dikey konularda 1080×1920).

Konu dosyasındaki KAPAK sözlüğü: ust (iri başlık), alt (yıl), vurgu (patlama içindeki kısa çığlık),
sol/sag: (karakter adı, {ifade, poz, ...}). Kanal kuralı: batı solda, doğu sağda.
"""
import math

import cairo

from .cizim import sekil, yazi, kutu_yolu, poligon_yolu, yazi_genislik, koyu, KONTUR
from .karakter import Karakter
from .kartlar import logo, MARKA


def _isinlar(cr, w, h, renk1, renk2):
    g = cairo.RadialGradient(w / 2, h * 0.55, 20, w / 2, h / 2, w * 0.75)
    g.add_color_stop_rgb(0, *renk1)
    g.add_color_stop_rgb(1, *renk2)
    cr.set_source(g)
    cr.paint()
    cr.save()
    cr.translate(w / 2, h * 0.55)
    for k in range(20):
        cr.rotate(math.pi / 10)
        cr.move_to(0, 0)
        cr.line_to(w * 1.2, -w * 0.09)
        cr.line_to(w * 1.2, w * 0.09)
        cr.close_path()
        cr.set_source_rgba(1, 1, 1, 0.09)
        cr.fill()
    cr.restore()


def kapak_resmi(konu, yol):
    k = konu.KAPAK
    dikey = getattr(konu, "FORMAT", "yatay") == "dikey"
    w, h = (1080, 1920) if dikey else (1280, 720)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(s)
    _isinlar(cr, w, h, (0.85, 0.3, 0.15), (0.3, 0.05, 0.05))
    tasarim = getattr(konu, "KARAKTERLER", {})
    for taraf, (ad, ayar) in (("sol", k["sol"]), ("sag", k["sag"])):
        d = dict(tasarim.get(ad, {}))
        d.update(ayar)
        d["yon"] = 1 if taraf == "sol" else -1
        x = w * (0.17 if taraf == "sol" else 0.83)
        kar = Karakter(ad, x=x, y=h + 60, olcek=(1.95 if not dikey else 2.4), **d)
        kar.ciz(cr, 1.3)
    # orta: patlama + vurgu
    rx, ry = w / 2, h * 0.66
    pts = []
    for i in range(32):
        r = (175 if i % 2 == 0 else 120) * (1 + 0.08 * math.sin(i * 1.7))
        a = i * math.pi / 16
        pts.append((rx + math.cos(a) * r * 1.4, ry + math.sin(a) * r * 0.75))
    sekil(cr, poligon_yolu(pts), MARKA, kalin=8, golge=0.1, parlama=False)
    boy = 54
    while yazi_genislik(cr, k["vurgu"], boy) > 380 and boy > 30:
        boy -= 2
    yazi(cr, k["vurgu"], rx, ry + boy * 0.35, boy, renk=(0.85, 0.12, 0.1), kontur=0.12)
    # başlık
    boy = 150
    while yazi_genislik(cr, k["ust"], boy) > w - 120:
        boy -= 4
    yazi(cr, k["ust"], w / 2, 40 + boy * 0.85, boy, renk=MARKA, kontur=0.13)
    if k.get("alt"):
        yazi(cr, k["alt"], w / 2, 40 + boy * 0.85 + 78, 74, renk=(1, 1, 1), kontur=0.16)
    logo(cr, getattr(konu, "LOGO", "kilic"), w - 70, h - 70, 46)
    s.write_to_png(yol)
    return yol
