"""Çizgi film çizim yardımcıları: kalın siyah dış çizgi, cel gölge (düz renk + tek ton gölge),
parlama, yazı, bulanık katman.

Temel kalıp: şeklin yolunu çizen bir fonksiyon verilir; sekil() onu doldurur, içine gölge hilali
ve parlama koyar, en son kalın siyah çizgiyle çevreler.
"""
import math

import cairo

G, Y = 1280, 720
KONTUR = (0.07, 0.06, 0.09)
KALIN = 5.0          # varsayılan dış çizgi kalınlığı (piksel, 720p)
ISIK = (-0.55, -0.75)  # ışık sol üstten gelir; gölge sağ alta düşer
YAZI = "Baloo 2"
YAZI2 = "Baloo 2"  # Fredoka Türkçe harfleri (ğ, ş, İ) içermiyor


def koyu(renk, k=0.72):
    return tuple(c * k for c in renk[:3])


def acik(renk, k=0.35):
    return tuple(c + (1 - c) * k for c in renk[:3])


def karistir(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


# ---------------------------------------------------------------- temel yollar
def daire_yolu(r, x=0.0, y=0.0):
    def yol(cr):
        cr.new_sub_path()
        cr.arc(x, y, r, 0, 2 * math.pi)
    return yol


def elips_yolu(rx, ry, x=0.0, y=0.0):
    def yol(cr):
        cr.save()
        cr.translate(x, y)
        cr.scale(rx, ry)
        cr.new_sub_path()
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
    return yol


def kutu_yolu(x, y, w, h, r=10):
    def yol(cr):
        rr = min(r, w / 2, h / 2)
        cr.new_sub_path()
        cr.arc(x + w - rr, y + rr, rr, -math.pi / 2, 0)
        cr.arc(x + w - rr, y + h - rr, rr, 0, math.pi / 2)
        cr.arc(x + rr, y + h - rr, rr, math.pi / 2, math.pi)
        cr.arc(x + rr, y + rr, rr, math.pi, 1.5 * math.pi)
        cr.close_path()
    return yol


def egri_yolu(noktalar, kapali=True, gerginlik=0.5):
    """Noktalardan geçen yumuşak (Catmull-Rom) eğri."""
    def yol(cr):
        n = len(noktalar)
        p = noktalar
        cr.move_to(*p[0])
        aralik = range(n) if kapali else range(n - 1)
        for i in aralik:
            p0 = p[(i - 1) % n] if kapali or i > 0 else p[0]
            p1, p2 = p[i], p[(i + 1) % n]
            p3 = p[(i + 2) % n] if kapali or i + 2 < n else p2
            c1 = (p1[0] + (p2[0] - p0[0]) * gerginlik / 3, p1[1] + (p2[1] - p0[1]) * gerginlik / 3)
            c2 = (p2[0] - (p3[0] - p1[0]) * gerginlik / 3, p2[1] - (p3[1] - p1[1]) * gerginlik / 3)
            cr.curve_to(*c1, *c2, *p2)
        if kapali:
            cr.close_path()
    return yol


def poligon_yolu(noktalar):
    def yol(cr):
        cr.move_to(*noktalar[0])
        for p in noktalar[1:]:
            cr.line_to(*p)
        cr.close_path()
    return yol


# ---------------------------------------------------------------- cel boyama
def sekil(cr, yol, renk, alfa=1.0, kalin=KALIN, golge=0.18, parlama=True, golge_renk=None, olcek=None):
    """yol: cr'ye yol çizen fonksiyon. golge: gölge hilalinin şekil boyutuna oranı (0 = gölgesiz).
    olcek: gölge kaydırması için şeklin yaklaşık boyu (verilmezse yol sınırlarından ölçülür)."""
    cr.save()
    cr.new_path()
    yol(cr)
    x0, y0, x1, y1 = cr.fill_extents()
    boy = olcek or max(x1 - x0, y1 - y0, 1)
    cr.clip_preserve()
    cr.set_source_rgba(*renk[:3], alfa)
    cr.fill()
    if golge > 0:
        # gölge: şeklin ışığa doğru kaydırılmış kopyasının dışında kalan hilal
        dx, dy = -ISIK[0] * boy * golge, -ISIK[1] * boy * golge
        cr.new_path()
        cr.push_group()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_DEST_OUT)
        cr.translate(-dx, -dy)
        yol(cr)
        cr.fill()
        maske = cr.pop_group()
        cr.set_source_rgba(*(golge_renk or koyu(renk)), alfa)
        cr.mask(maske)
    if parlama and boy > 14 and min(x1 - x0, y1 - y0) > 2:
        cx, cy = x0 + (x1 - x0) * 0.3, y0 + (y1 - y0) * 0.27
        cr.save()
        cr.translate(cx, cy)
        cr.rotate(-0.6)
        cr.scale((x1 - x0) * 0.13, (y1 - y0) * 0.07)
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgba(1, 1, 1, 0.45 * alfa)
        cr.fill()
    cr.restore()
    if kalin > 0:
        cr.save()
        cr.new_path()
        yol(cr)
        cr.set_source_rgba(*KONTUR, alfa)
        cr.set_line_width(kalin)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke()
        cr.restore()


def cizgi(cr, noktalar, renk, kalin=10, alfa=1.0, kontur=KALIN * 0.8, egri=True):
    """Dış çizgili kalın çizgi (kol, bacak, ip): önce siyah geniş, üstüne renkli dar çizgi."""
    def yol():
        cr.new_path()
        if egri and len(noktalar) > 2:
            egri_yolu(noktalar, kapali=False)(cr)
        else:
            cr.move_to(*noktalar[0])
            for p in noktalar[1:]:
                cr.line_to(*p)
    cr.save()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    yol()
    cr.set_source_rgba(*KONTUR, alfa)
    cr.set_line_width(kalin + 2 * kontur)
    cr.stroke()
    yol()
    cr.set_source_rgba(*renk[:3], alfa)
    cr.set_line_width(kalin)
    cr.stroke()
    cr.restore()


def ince_cizgi(cr, noktalar, kalin=4, renk=KONTUR, alfa=1.0, egri=True):
    cr.save()
    cr.new_path()
    if egri and len(noktalar) > 2:
        egri_yolu(noktalar, kapali=False)(cr)
    else:
        cr.move_to(*noktalar[0])
        for p in noktalar[1:]:
            cr.line_to(*p)
    cr.set_source_rgba(*renk[:3], alfa)
    cr.set_line_width(kalin)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.stroke()
    cr.restore()


def yer_golgesi(cr, x, y, rx, ry=None, alfa=0.25):
    cr.save()
    cr.translate(x, y)
    cr.scale(rx, ry or rx * 0.22)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.restore()
    cr.set_source_rgba(0, 0, 0, alfa)
    cr.fill()


# ---------------------------------------------------------------- yazı
def yazi(cr, metin, x, y, boyut, renk=(1, 1, 1), hiza="orta", aile=YAZI, kalin=True, kontur=0.16,
         alfa=1.0, kontur_renk=KONTUR, golge=True):
    """Dış çizgili çizgi film yazısı. y: taban çizgisi. kontur: boyuta oranla çizgi kalınlığı."""
    cr.save()
    cr.select_font_face(aile, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if kalin else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(boyut)
    ext = cr.text_extents(metin)
    if hiza == "orta":
        x -= ext.x_advance / 2
    elif hiza == "sag":
        x -= ext.x_advance
    if golge and kontur:
        cr.move_to(x + boyut * 0.05, y + boyut * 0.07)
        cr.text_path(metin)
        cr.set_source_rgba(0, 0, 0, 0.35 * alfa)
        cr.set_line_width(boyut * kontur)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke_preserve()
        cr.fill()
    cr.move_to(x, y)
    cr.text_path(metin)
    if kontur:
        cr.set_source_rgba(*kontur_renk, alfa)
        cr.set_line_width(boyut * kontur)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.stroke_preserve()
    cr.set_source_rgba(*renk[:3], alfa)
    cr.fill()
    cr.restore()
    return ext.x_advance


def yazi_genislik(cr, metin, boyut, aile=YAZI, kalin=True):
    cr.save()
    cr.select_font_face(aile, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if kalin else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(boyut)
    w = cr.text_extents(metin).x_advance
    cr.restore()
    return w


def satirlara_bol(cr, metin, boyut, azami_g, aile=YAZI):
    kelimeler, satirlar, s = metin.split(), [], ""
    for k in kelimeler:
        dene = (s + " " + k).strip()
        if s and yazi_genislik(cr, dene, boyut, aile) > azami_g:
            satirlar.append(s)
            s = k
        else:
            s = dene
    if s:
        satirlar.append(s)
    return satirlar


# ---------------------------------------------------------------- yüzeyler
def yuzey(g=G, y=Y):
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, int(g), int(y))


def bulaniklastir(kaynak, miktar=8.0):
    """Ucuz ve yumuşak bulanıklık: küçült, iki kademede geri büyüt (alan derinliği için)."""
    g, y = kaynak.get_width(), kaynak.get_height()
    k = max(1.0, miktar)
    ara = kaynak
    for adim in (k ** 0.5, k):
        kg, ky = max(2, int(g / adim)), max(2, int(y / adim))
        kucuk = cairo.ImageSurface(cairo.FORMAT_ARGB32, kg, ky)
        c = cairo.Context(kucuk)
        c.scale(kg / ara.get_width(), ky / ara.get_height())
        c.set_source_surface(ara, 0, 0)
        c.get_source().set_filter(cairo.FILTER_GOOD)
        c.paint()
        ara = kucuk
    sonuc = cairo.ImageSurface(cairo.FORMAT_ARGB32, g, y)
    c = cairo.Context(sonuc)
    c.scale(g / ara.get_width(), y / ara.get_height())
    c.set_source_surface(ara, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BILINEAR)
    c.get_source().set_extend(cairo.EXTEND_PAD)
    c.paint()
    return sonuc
