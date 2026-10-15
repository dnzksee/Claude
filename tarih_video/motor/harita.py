"""Prosedürel savaş alanı arka planı (bozkır / çöl / orman tonları, tepeler, nehir).

Her şey kod ile üretilir: telifli harita görüntüsü kullanılmaz.
Dünya koordinatları 1920x1080'dir; arka plan kamera yakınlaştırması için 2x çözünürlükte üretilir.
"""
import math
import numpy as np
import cairo

DUNYA_G, DUNYA_Y = 1920, 1080
OLCEK = 2  # arka plan çözünürlük çarpanı

ZEMINLER = {
    # (koyu, açık, tepe vurgusu)
    "bozkir": ((122, 112, 70), (196, 182, 128), (150, 130, 92)),
    "col": ((176, 140, 86), (232, 206, 150), (190, 150, 100)),
    "yesil": ((70, 98, 58), (150, 170, 108), (110, 120, 80)),
    "kar": ((170, 178, 186), (238, 240, 242), (190, 196, 204)),
}


def _gurultu(g, y, rng, oktav=6, baslangic=4):
    """Basit fraktal değer gürültüsü (0..1)."""
    sonuc = np.zeros((y, g), np.float32)
    genlik, toplam = 1.0, 0.0
    for o in range(oktav):
        n = baslangic * (2 ** o)
        izgara = rng.random((n + 1, int(n * g / y) + 2)).astype(np.float32)
        # bilineer büyütme
        ys = np.linspace(0, n, y, dtype=np.float32)
        xs = np.linspace(0, izgara.shape[1] - 1.001, g, dtype=np.float32)
        y0, x0 = ys.astype(int).clip(0, n - 1), xs.astype(int)
        fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
        fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
        a = izgara[y0][:, x0]
        b = izgara[y0][:, x0 + 1]
        c = izgara[y0 + 1][:, x0]
        d = izgara[y0 + 1][:, x0 + 1]
        sonuc += genlik * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        toplam += genlik
        genlik *= 0.5
    return sonuc / toplam


def arka_plan_uret(zemin="bozkir", tepeler=(), nehirler=(), yollar=(), etiketler=(),
                   yerlesimler=(), tohum=7):
    """Arka planı cairo ImageSurface olarak döndürür (2x çözünürlük).

    tepeler:     [(x, y, yaricap, yukseklik), ...]  dünya koordinatı
    nehirler:    [[(x, y), ...], ...]  nehir hattı noktaları
    yollar:      [[(x, y), ...], ...]
    etiketler:   [(x, y, metin, boyut), ...]
    yerlesimler: [(x, y, ad), ...]
    """
    rng = np.random.default_rng(tohum)
    G, Y = DUNYA_G * OLCEK, DUNYA_Y * OLCEK
    koyu, acik, tepe_renk = (np.array(c, np.float32) for c in ZEMINLER[zemin])

    n = _gurultu(G, Y, rng)
    ince = _gurultu(G, Y, rng, oktav=3, baslangic=60)

    # Yükseklik haritası: gürültü + tepeler
    kaba = _gurultu(G, Y, rng, oktav=3, baslangic=3)
    yuk = kaba * 0.12
    yy, xx = np.mgrid[0:Y, 0:G].astype(np.float32)
    for (tx, ty, r, h) in tepeler:
        d2 = ((xx - tx * OLCEK) ** 2 + (yy - ty * OLCEK) ** 2) / (r * OLCEK) ** 2
        yuk += h * np.exp(-d2 * 2.2) * (0.8 + 0.4 * n)

    # Gölgelendirme (kuzeybatıdan ışık)
    gy, gx = np.gradient(yuk)
    golge = np.clip(0.5 + (-gx - gy) * 300, 0, 1)

    t = np.clip(n * 1.3 - 0.15, 0, 1)[..., None]
    renk = koyu * (1 - t) + acik * t
    tepe_maske = np.clip(yuk - 0.25, 0, 1)[..., None] * 1.6
    renk = renk * (1 - np.clip(tepe_maske, 0, 0.7)) + tepe_renk * np.clip(tepe_maske, 0, 0.7)
    renk *= (0.7 + 0.6 * golge)[..., None]
    # topoğrafik eş yükselti çizgileri (yalnızca tepelerde)
    es = np.abs((yuk * 9) % 1.0 - 0.5)
    cizgi = np.clip((0.06 - np.abs(es - 0.5 + 0.03)) / 0.06, 0, 1) * np.clip((yuk - 0.3) * 4, 0, 1)
    renk *= (1 - 0.22 * cizgi)[..., None]
    renk *= (0.93 + 0.14 * ince)[..., None]

    # Kenar karartma (vinyet)
    vx = (xx / G - 0.5) * 2
    vy = (yy / Y - 0.5) * 2
    vin = 1 - 0.28 * np.clip(vx ** 2 + vy ** 2 - 0.35, 0, 1)
    renk *= vin[..., None]
    renk = np.clip(renk, 0, 255).astype(np.uint8)

    yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, G, Y)
    tampon = np.ndarray((Y, G, 4), np.uint8, buffer=yuzey.get_data(), strides=(yuzey.get_stride(), 4, 1))
    tampon[..., 0] = renk[..., 2]
    tampon[..., 1] = renk[..., 1]
    tampon[..., 2] = renk[..., 0]
    tampon[..., 3] = 255
    yuzey.mark_dirty()

    cr = cairo.Context(yuzey)
    cr.scale(OLCEK, OLCEK)

    for yol in yollar:
        _yumusak_cizgi(cr, yol)
        cr.set_source_rgba(0.42, 0.33, 0.22, 0.45)
        cr.set_line_width(5)
        cr.set_dash([14, 9])
        cr.stroke()
        cr.set_dash([])

    for nehir in nehirler:
        for gen, renk_n in ((30, (0.30, 0.38, 0.30, 0.35)), (20, (0.20, 0.42, 0.55, 1)),
                            (9, (0.42, 0.66, 0.78, 0.9))):
            _yumusak_cizgi(cr, nehir)
            cr.set_source_rgba(*renk_n)
            cr.set_line_width(gen)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.stroke()

    # Dağınık çalılık / kaya noktaları
    for _ in range(900):
        x, y = rng.random() * DUNYA_G, rng.random() * DUNYA_Y
        r = 1.2 + rng.random() * 2.8
        cr.arc(x, y, r, 0, 2 * math.pi)
        cr.set_source_rgba(0.25, 0.22, 0.12, 0.25 + rng.random() * 0.2)
        cr.fill()

    for (x, y, ad) in yerlesimler:
        _yerlesim(cr, x, y, ad)

    for (x, y, metin, boyut) in etiketler:
        cr.select_font_face("Caladea", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(boyut)
        ext = cr.text_extents(metin)
        cr.move_to(x - ext.width / 2, y)
        cr.text_path(metin)
        cr.set_source_rgba(0.95, 0.9, 0.78, 0.55)
        cr.set_line_width(4)
        cr.stroke_preserve()
        cr.set_source_rgba(0.25, 0.18, 0.1, 0.8)
        cr.fill()

    return yuzey


def _yerlesim(cr, x, y, ad):
    # Basit sur + kule simgesi
    cr.set_source_rgba(0.28, 0.2, 0.14, 0.9)
    cr.rectangle(x - 22, y - 10, 44, 20)
    cr.fill()
    for dx in (-22, -6, 10):
        cr.rectangle(x + dx, y - 18, 12, 8)
        cr.fill()
    cr.select_font_face("Caladea", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(26)
    ext = cr.text_extents(ad)
    cr.move_to(x - ext.width / 2, y + 44)
    cr.text_path(ad)
    cr.set_source_rgba(0.96, 0.92, 0.8, 0.85)
    cr.set_line_width(5)
    cr.stroke_preserve()
    cr.set_source_rgb(0.2, 0.14, 0.08)
    cr.fill()


def _yumusak_cizgi(cr, noktalar):
    """Catmull-Rom eğrisi ile noktalardan yumuşak yol."""
    p = list(noktalar)
    cr.move_to(*p[0])
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[i]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < len(p) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        cr.curve_to(*c1, *c2, *p2)
