"""YouTube kapak resmi (küçük resim): 1280×720 PNG (dikey konularda 1080×1920).

Konu dosyasındaki KAPAK sözlüğü:
  vurgu: iri manşet (kısa çığlık, ör. "İMPARATOR ESİR!")
  ust, alt: şerit yazısı (konu adı ve yıl)
  sol/sag: (karakter adı, {ifade, poz, ...}); kanal kuralı: batı solda, doğu sağda
  sol_arma/sag_arma: sancaktaki arma (amblem.sembol taraf adı); sol_renk/sag_renk: zemin rengi
  ok: "sol" | "sag" | None; manşetten o taraftaki karaktere kırmızı ok
"""
import math
import random

import cairo

from .cizim import sekil, yazi, kutu_yolu, poligon_yolu, egri_yolu, yazi_genislik, koyu, acik, KONTUR
from .karakter import Karakter
from .kartlar import logo, MARKA
from .birlikler import _amblem

KIRMIZI = (0.86, 0.12, 0.1)


def _yarim_zemin(cr, w, h, pts, merkez, renk):
    """Bir tarafın ışınlı radyal zemini (pts çokgeniyle sınırlı)."""
    cr.save()
    cr.new_path()
    for i, p in enumerate(pts):
        (cr.move_to if i == 0 else cr.line_to)(*p)
    cr.close_path()
    cr.clip()
    g = cairo.RadialGradient(*merkez, 30, *merkez, w * 0.7)
    g.add_color_stop_rgb(0, *acik(renk, 0.25))
    g.add_color_stop_rgb(1, *koyu(renk, 0.3))
    cr.set_source(g)
    cr.paint()
    cr.translate(*merkez)
    for k in range(18):
        cr.rotate(math.pi / 9)
        cr.move_to(0, 0)
        cr.line_to(w * 1.3, -w * 0.1)
        cr.line_to(w * 1.3, w * 0.1)
        cr.close_path()
        cr.set_source_rgba(1, 1, 1, 0.07)
        cr.fill()
    cr.restore()


def _simsek(w, h, x_ust, x_alt):
    """Ortadaki zikzak ayrım çizgisi (yukarıdan aşağı)."""
    rnd = random.Random(7)
    pts, n = [], 9
    for i in range(n + 1):
        u = i / n
        x = x_ust + (x_alt - x_ust) * u + (rnd.uniform(18, 34) * (1 if i % 2 else -1) if 0 < i < n else 0)
        pts.append((x, -20 + (h + 40) * u))
    return pts


def _sancak(cr, amb, x, y, boy, renk, arma, egim=0.0, yirtik=False, yon=1):
    """Direk + dalgalı bayrak + arma. (x, y): direğin dibi."""
    cr.save()
    cr.translate(x, y)
    cr.rotate(math.radians(egim))
    sekil(cr, kutu_yolu(-9, -boy, 18, boy + 40, 6), (0.45, 0.28, 0.12), golge=0.25, parlama=False, kalin=6)
    sekil(cr, egri_yolu([(0, -boy - 40), (16, -boy - 6), (0, -boy + 6), (-16, -boy - 6)], gerginlik=0.2),
          MARKA, kalin=5, golge=0.15, parlama=False)
    bw, bh, ust = 300, 230, -boy + 10
    kenar = [(9 * yon, ust), (bw * 0.5 * yon, ust + 22), (bw * yon, ust - 6)]
    if yirtik:
        kenar += [(bw * 0.86 * yon, ust + bh * 0.3), (bw * 0.98 * yon, ust + bh * 0.48),
                  (bw * 0.8 * yon, ust + bh * 0.62), (bw * 0.92 * yon, ust + bh * 0.85)]
    else:
        kenar += [(bw * 1.02 * yon, ust + bh * 0.5), (bw * 0.97 * yon, ust + bh)]
    kenar += [(bw * 0.5 * yon, ust + bh + 26), (9 * yon, ust + bh)]
    sekil(cr, poligon_yolu(kenar), renk, kalin=7, golge=0.22, olcek=260)
    cr.save()
    cr.translate(bw * 0.5 * yon, ust + bh * 0.52)
    amb.sembol(cr, arma, 100, MARKA, 1.0)
    cr.restore()
    cr.restore()


def _ok(cr, x0, y0, x1, y1, kavis=-0.3):
    """Kalın, siyah konturlu kırmızı ok (x0,y0 → x1,y1)."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * kavis, my + dx * kavis
    noktalar = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1,
                 (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1) for u in [i / 24 for i in range(25)]]
    son = noktalar[-4]
    aci = math.atan2(y1 - son[1], x1 - son[0])
    kalin = 30
    for renk, ek in ((KONTUR, 14), (KIRMIZI, 0)):
        cr.set_source_rgb(*renk)
        cr.set_line_width(kalin + ek)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(*noktalar[0])
        for p in noktalar[1:-3]:
            cr.line_to(*p)
        cr.stroke()
    uc = 62
    bas = [(x1, y1), (x1 - math.cos(aci - 0.55) * uc, y1 - math.sin(aci - 0.55) * uc),
           (x1 - math.cos(aci + 0.55) * uc, y1 - math.sin(aci + 0.55) * uc)]
    sekil(cr, poligon_yolu(bas), KIRMIZI, kalin=7, golge=0.15, parlama=False)


def _manset(cr, metin, x, y, boy, aci):
    """Eğik, kalın konturlu, alt gölgeli iri yazı."""
    cr.save()
    cr.translate(x, y)
    cr.rotate(math.radians(aci))
    yazi(cr, metin, 8, 12, boy, renk=(0, 0, 0), kontur=0.2, golge=False, alfa=0.55)
    yazi(cr, metin, 0, 0, boy, renk=MARKA, kontur=0.17, golge=False)
    cr.restore()


def _serit(cr, metin, x, y, boy, aci):
    """Kırmızı şerit içinde beyaz yazı."""
    cr.save()
    cr.translate(x, y)
    cr.rotate(math.radians(aci))
    gw = yazi_genislik(cr, metin, boy) + 70
    sekil(cr, poligon_yolu([(-gw / 2 - 22, -boy * 0.95), (gw / 2 + 10, -boy * 0.95), (gw / 2 + 32, boy * 0.35),
                            (-gw / 2, boy * 0.35)]), KIRMIZI, kalin=7, golge=0.2, olcek=120)
    yazi(cr, metin, 4, boy * 0.02, boy, renk=(1, 1, 1), kontur=0.14)
    cr.restore()


def _vinyet(cr, w, h):
    g = cairo.RadialGradient(w / 2, h / 2, h * 0.45, w / 2, h / 2, w * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    cr.set_source(g)
    cr.paint()


def _kivilcim(cr, w, h):
    rnd = random.Random(3)
    for _ in range(70):
        x, y, r = rnd.uniform(0, w), rnd.uniform(h * 0.25, h), rnd.uniform(1.5, 4.5)
        cr.arc(x, y, r, 0, 2 * math.pi)
        cr.set_source_rgba(1, rnd.uniform(0.6, 0.9), 0.3, rnd.uniform(0.35, 0.85))
        cr.fill()


def kapak_resmi(konu, yol):
    k = konu.KAPAK
    dikey = getattr(konu, "FORMAT", "yatay") == "dikey"
    w, h = (1080, 1920) if dikey else (1280, 720)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(s)
    tasarim = getattr(konu, "KARAKTERLER", {})
    sol_ad, sag_ad = k["sol"][0], k["sag"][0]
    sol_renk = k.get("sol_renk", tasarim.get(sol_ad, {}).get("govde", (0.45, 0.2, 0.55)))
    sag_renk = k.get("sag_renk", (0.85, 0.3, 0.12))
    amb = _amblem()

    # zemin: iki taraf, ortada şimşek
    sim = _simsek(w, h, w * 0.56, w * 0.44)
    _yarim_zemin(cr, w, h, [(-10, -30)] + sim + [(-10, h + 30)], (w * 0.22, h * 0.55), sol_renk)
    _yarim_zemin(cr, w, h, [(w + 10, -30)] + sim + [(w + 10, h + 30)], (w * 0.78, h * 0.55), sag_renk)
    for kal, renk, alfa in ((34, (1, 0.9, 0.5), 0.25), (16, (1, 0.95, 0.7), 0.8), (6, (1, 1, 1), 1.0)):
        cr.set_source_rgba(*renk, alfa)
        cr.set_line_width(kal)
        cr.set_line_join(cairo.LINE_JOIN_MITER)
        cr.move_to(*sim[0])
        for p in sim[1:]:
            cr.line_to(*p)
        cr.stroke()
    _kivilcim(cr, w, h)

    # sancaklar: yenilenin bayrağı yırtık ve devrik, kazananınki dimdik
    yenilen = k.get("ok", "sol")
    _sancak(cr, amb, w * 0.035, h + 40, 520, k.get("sol_sancak", koyu(sol_renk, 0.85)), k.get("sol_arma", "bizans"),
            egim=-12 if yenilen == "sol" else -4, yirtik=yenilen == "sol", yon=1)
    _sancak(cr, amb, w * 0.975, h + 40, 520, k.get("sag_sancak", (0.1, 0.5, 0.46)), k.get("sag_arma", "selcuklu"),
            egim=3 if yenilen == "sol" else 12, yirtik=yenilen == "sag", yon=-1)

    # karakterler: kazanan büyük ve öne, yenilen biraz küçük
    kars = {}
    for taraf, (ad, ayar) in (("sol", k["sol"]), ("sag", k["sag"])):
        d = dict(tasarim.get(ad, {}))
        d.update(ayar)
        d["yon"] = 1 if taraf == "sol" else -1
        buyuk = taraf != yenilen
        x = w * (0.27 if taraf == "sol" else 0.7)
        kars[taraf] = Karakter(ad, x=x, y=h + (120 if buyuk else 100),
                               olcek=(1.9 if buyuk else 1.62) * (1.2 if dikey else 1.0), **d)
    for taraf in (yenilen, "sag" if yenilen == "sol" else "sol"):
        kars[taraf].ciz(cr, 1.3)

    # manşet + şerit
    boy = 116
    while yazi_genislik(cr, k["vurgu"], boy) > w - 150 and boy > 60:
        boy -= 4
    _manset(cr, k["vurgu"], w / 2, 40 + boy * 0.85, boy, -3)
    serit = " ".join(x for x in (k.get("ust"), k.get("alt")) if x)
    if serit:
        _serit(cr, serit, w / 2 + 30, 40 + boy * 0.85 + 84, 52, -3)

    # ok: manşetten yenilenin başına
    if k.get("ok", "sol"):
        hx, hy = kars[yenilen].bas_konumu(1.3)
        isaret = 1 if yenilen == "sol" else -1
        _ok(cr, w / 2 - isaret * 10, 40 + boy * 0.85 + 135, hx + isaret * 145, hy + 10, kavis=-0.25 * isaret)

    _vinyet(cr, w, h)
    logo(cr, getattr(konu, "LOGO", "kilic"), 62, h - 62, 38)  # sağ alt köşe YouTube süre etiketinin altında kalır
    s.write_to_png(yol)
    return yol
