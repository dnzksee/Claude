"""Taraf armaları: harita işaretleri, taktik bloklar ve portre madalyonlarında kullanılan sade semboller.

Her çizim orijinde, r yarıçaplı alana sığacak şekilde yapılır; renkler çağırandan gelir.
"""
import math

import cairo


def _cizgi(cr, w):
    cr.set_line_width(w)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)


def sembol(cr, taraf, r, renk, a):
    """Yalnız iç sembol (zemin yok). renk: sembol rengi."""
    cr.save()
    cr.set_source_rgba(*renk, a)
    if taraf == "selcuklu":  # yay ve ok
        _cizgi(cr, r * 0.13)
        cr.arc(r * 0.18, 0, r * 0.62, math.pi * 0.62, math.pi * 1.38)
        cr.stroke()
        _cizgi(cr, r * 0.05)
        ux, uy = r * 0.18 + r * 0.62 * math.cos(math.pi * 0.62), r * 0.62 * math.sin(math.pi * 0.62)
        cr.move_to(ux, uy)
        cr.line_to(ux, -uy)
        cr.stroke()
        _cizgi(cr, r * 0.08)
        cr.move_to(-r * 0.55, 0)
        cr.line_to(r * 0.55, 0)
        cr.stroke()
        cr.move_to(r * 0.72, 0)
        cr.line_to(r * 0.42, -r * 0.18)
        cr.line_to(r * 0.42, r * 0.18)
        cr.close_path()
        cr.fill()
    elif taraf in ("bizans", "hacli"):  # haç (Bizans: uçları genişleyen, Haçlı: düz)
        w = r * 0.2
        if taraf == "hacli":
            cr.rectangle(-w / 2, -r * 0.7, w, r * 1.4)
            cr.rectangle(-r * 0.7, -w / 2, r * 1.4, w)
            cr.fill()
        else:
            for k in range(4):
                cr.save()
                cr.rotate(k * math.pi / 2)
                cr.move_to(-w * 0.45, 0)
                cr.line_to(-w * 1.1, -r * 0.7)
                cr.line_to(w * 1.1, -r * 0.7)
                cr.line_to(w * 0.45, 0)
                cr.close_path()
                cr.fill()
                cr.restore()
    elif taraf == "fatimi":  # hilal
        cr.arc(0, 0, r * 0.6, 0, 2 * math.pi)
        cr.arc_negative(r * 0.22, -r * 0.08, r * 0.48, 2 * math.pi, 0)
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.fill()
    elif taraf == "gazneli":  # sekiz köşeli yıldız
        for k in range(2):
            cr.save()
            cr.rotate(k * math.pi / 4)
            s = r * 0.48
            cr.rectangle(-s, -s, 2 * s, 2 * s)
            cr.fill()
            cr.restore()
    elif taraf == "pecenek":  # damga
        _cizgi(cr, r * 0.14)
        cr.move_to(0, r * 0.65)
        cr.line_to(0, -r * 0.1)
        cr.line_to(-r * 0.5, -r * 0.6)
        cr.move_to(0, -r * 0.1)
        cr.line_to(r * 0.5, -r * 0.6)
        cr.stroke()
    elif taraf == "norman":  # şerit (chevron)
        _cizgi(cr, r * 0.2)
        cr.move_to(-r * 0.6, r * 0.35)
        cr.line_to(0, -r * 0.3)
        cr.line_to(r * 0.6, r * 0.35)
        cr.stroke()
    else:  # baklava
        cr.move_to(0, -r * 0.6)
        cr.line_to(r * 0.45, 0)
        cr.line_to(0, r * 0.6)
        cr.line_to(-r * 0.45, 0)
        cr.close_path()
        cr.fill()
    cr.restore()


def kalkan_yolu(cr, r):
    """Hanedan kalkanı biçimi (üst düz, alt sivri)."""
    cr.move_to(-r * 0.85, -r * 0.9)
    cr.line_to(r * 0.85, -r * 0.9)
    cr.line_to(r * 0.85, -r * 0.1)
    cr.curve_to(r * 0.85, r * 0.55, r * 0.35, r * 0.85, 0, r * 1.05)
    cr.curve_to(-r * 0.35, r * 0.85, -r * 0.85, r * 0.55, -r * 0.85, -r * 0.1)
    cr.close_path()


def kalkan(cr, taraf, x, y, r, renk, vurgu, a):
    """Gölgeli, çerçeveli, sembollü kalkan işareti."""
    cr.save()
    cr.translate(x, y)
    cr.save()
    cr.translate(r * 0.12, r * 0.16)
    kalkan_yolu(cr, r)
    cr.set_source_rgba(0, 0, 0, 0.35 * a)
    cr.fill()
    cr.restore()
    kalkan_yolu(cr, r)
    g = cairo.LinearGradient(0, -r, 0, r)
    g.add_color_stop_rgba(0, min(1, renk[0] * 1.3), min(1, renk[1] * 1.3), min(1, renk[2] * 1.3), a)
    g.add_color_stop_rgba(1, renk[0] * 0.75, renk[1] * 0.75, renk[2] * 0.75, a)
    cr.set_source(g)
    cr.fill_preserve()
    cr.set_source_rgba(*vurgu, a)
    cr.set_line_width(max(1.5, r * 0.11))
    cr.stroke()
    cr.translate(0, -r * 0.02)
    sembol(cr, taraf, r * 0.78, vurgu, a)
    cr.restore()
