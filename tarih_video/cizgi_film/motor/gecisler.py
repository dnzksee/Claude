"""Sahne geçişleri: whip pan (hızlı savurma + hareket bulanıklığı), punch zoom (vuruşlu yakınlaşma
+ beyaz flaş), iris (daire maskeyle kapanıp açılma), kesme ve çapraz geçiş.

Her geçiş iki hazır kareyi (A: biten sahne, B: başlayan sahne) ve 0..1 ilerlemeyi alıp hedef
bağlama çizer. SURELER, geçişin toplam süresidir (saniye); sınırın iki yanına eşit yayılır.
"""
import math

import cairo

from .cizim import G, Y
from .zaman import yumusak, hizlan, yavasla

SURELER = {"whip": 0.5, "punch": 0.45, "iris": 1.1, "kes": 0.0, "capraz": 0.6}
# Geçişlerde efekt sesi yok (izleyici geri bildirimi: "kanal değiştirme" gibi rahatsız edici). İsteyen
# konu dosyası GECIS_SESLERI ile açabilir.
SESLER = {"whip": None, "punch": None, "iris": None, "kes": None, "capraz": None}


def whip(cr, A, B, u, yon=1):
    cr.set_source_rgb(0, 0, 0)
    cr.paint()
    hiz = math.sin(u * math.pi)  # ortada en hızlı
    bul = 260 * hiz
    if u < 0.5:
        k = hizlan(u / 0.5)
        _tek(cr, A, -yon * k * G * 0.9, bul)
    else:
        k = yavasla((u - 0.5) / 0.5)
        _tek(cr, B, yon * (1 - k) * G * 0.9, bul)


def _tek(cr, S, dx, bul):
    cr.save()
    cr.rectangle(0, 0, G, Y)
    cr.clip()
    # kenarlar boş kalmasın: kaynağı yatayda uzat; kopyaların ortalaması hareket bulanıklığı verir
    n = 15 if bul > 20 else 1
    for k in range(n):
        o = (k / max(n - 1, 1) - 0.5) * bul
        p = cairo.SurfacePattern(S)
        p.set_extend(cairo.EXTEND_PAD)
        m = cairo.Matrix()
        m.translate(-(dx + o), 0)
        p.set_matrix(m)
        cr.set_source(p)
        cr.paint_with_alpha(1.0 / (k + 1))
    cr.restore()


def punch(cr, A, B, u, merkez=(G / 2, Y / 2)):
    cx, cy = merkez
    if u < 0.5:
        k = hizlan(u / 0.5)
        s, kaynak = 1 + 0.9 * k, A
    else:
        k = 1 - yavasla((u - 0.5) / 0.5)
        s, kaynak = 1 + 0.35 * k, B
    cr.save()
    cr.translate(cx, cy)
    cr.scale(s, s)
    cr.translate(-cx, -cy)
    p = cairo.SurfacePattern(kaynak)
    p.set_extend(cairo.EXTEND_PAD)
    cr.set_source(p)
    cr.paint()
    cr.restore()
    flas = max(0.0, 1 - abs(u - 0.5) / 0.22)
    if flas > 0:
        cr.set_source_rgba(1, 1, 1, 0.85 * flas)
        cr.paint()


def iris(cr, A, B, u, merkez=(G / 2, Y / 2)):
    cr.set_source_rgb(0.04, 0.03, 0.05)
    cr.paint()
    rmax = math.hypot(G, Y) * 0.62
    if u < 0.5:
        r = rmax * (1 - yumusak(u / 0.42))
        kaynak = A
    else:
        r = rmax * yumusak((u - 0.58) / 0.42)
        kaynak = B
    if r <= 1:
        return
    cx, cy = merkez
    cr.save()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.clip()
    cr.set_source_surface(kaynak, 0, 0)
    cr.paint()
    cr.restore()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.set_source_rgb(0.04, 0.03, 0.05)
    cr.set_line_width(10)
    cr.stroke()


def capraz(cr, A, B, u):
    cr.set_source_surface(A, 0, 0)
    cr.paint()
    cr.set_source_surface(B, 0, 0)
    cr.paint_with_alpha(yumusak(u))


def uygula(tur, cr, A, B, u, **k):
    if tur == "whip":
        whip(cr, A, B, u, k.get("yon", 1))
    elif tur == "punch":
        punch(cr, A, B, u, k.get("merkez", (G / 2, Y / 2)))
    elif tur == "iris":
        iris(cr, A, B, u, k.get("merkez", (G / 2, Y / 2)))
    elif tur == "capraz":
        capraz(cr, A, B, u)
    else:
        cr.set_source_surface(B if u >= 0.5 else A, 0, 0)
        cr.paint()
