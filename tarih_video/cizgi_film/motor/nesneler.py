"""Metafor eşyaları ve efektler (hepsi kalın dış çizgili, cel gölgeli).

Her çizim fonksiyonu (cr, t, p) alır; orijinde, yaklaşık 100 px boyunda çizer. p: Nesne'nin
o anki parametreleri (seviye, yanik, metin...). Yeni bir eşya eklemek için CIZIMLER'e bir
fonksiyon eklemek yeterli.
"""
import math
import random

import cairo

from .cizim import (sekil, cizgi, ince_cizgi, yazi, daire_yolu, elips_yolu, kutu_yolu, egri_yolu, poligon_yolu,
                    satirlara_bol, koyu, acik, karistir, KONTUR, YAZI)
from .zaman import Iz

SARI = (1.0, 0.82, 0.2)
KIRMIZI = (0.92, 0.25, 0.22)
YESIL = (0.3, 0.78, 0.35)
MAVI = (0.25, 0.55, 0.95)
PEMBE = (0.97, 0.55, 0.68)
MOR = (0.55, 0.38, 0.85)
BEYAZ = (0.98, 0.97, 0.94)
GRI = (0.6, 0.62, 0.66)
KAHVE = (0.6, 0.38, 0.2)


def _ampul(cr, t, p):
    y = p.get("yanik", 0.0)
    if y > 0.02:
        for k in range(12):
            aci = k * math.pi / 6 + t * 0.4
            r0, r1 = 62, 80 + 10 * math.sin(t * 6 + k)
            ince_cizgi(cr, [(math.cos(aci) * r0, math.sin(aci) * r0 - 15), (math.cos(aci) * r1, math.sin(aci) * r1 - 15)],
                       kalin=6, renk=SARI, alfa=y, egri=False)
        g = cairo.RadialGradient(0, -15, 10, 0, -15, 110)
        g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.55 * y)
        g.add_color_stop_rgba(1, 1, 0.9, 0.5, 0)
        cr.set_source(g)
        cr.arc(0, -15, 110, 0, 2 * math.pi)
        cr.fill()
    cam = karistir((0.85, 0.9, 0.95), (1.0, 0.93, 0.45), y)
    sekil(cr, egri_yolu([(0, -60), (40, -40), (42, -10), (22, 20), (18, 34), (-18, 34), (-22, 20), (-42, -10),
                         (-40, -40)]), cam)
    sekil(cr, kutu_yolu(-19, 34, 38, 26, 5), GRI, golge=0.2)
    for yy in (41, 49):
        ince_cizgi(cr, [(-19, yy), (19, yy)], kalin=3, egri=False)
    ince_cizgi(cr, [(-10, 30), (-8, 0), (0, -10), (8, 0), (10, 30)], kalin=3, renk=(0.5, 0.4, 0.3) if y < 0.5 else (1, 0.6, 0.1))


def _beyin(cr, t, p):
    renk = p.get("renk", PEMBE)
    tepe = [(-70, 10), (-72, -30), (-50, -58), (-15, -66), (20, -64), (55, -52), (74, -20), (70, 20), (45, 40),
            (10, 45), (-30, 42), (-60, 32)]
    sekil(cr, egri_yolu(tepe), renk, olcek=140)
    for yol in ([(-50, -20), (-30, -40), (-10, -25), (-20, 0)], [(10, -50), (25, -25), (45, -35), (55, -5)],
                [(-40, 20), (-15, 15), (5, 30)], [(20, 10), (40, 15), (50, 30)], [(0, -60), (2, -10), (-2, 40)]):
        ince_cizgi(cr, yol, kalin=4, renk=koyu(renk, 0.6))
    sekil(cr, kutu_yolu(-12, 38, 24, 30, 8), koyu(renk, 0.85), golge=0.2)


def _disli(cr, t, p):
    renk = p.get("renk", (0.7, 0.72, 0.78))
    hiz = p.get("hiz", 1.0)
    dis = int(p.get("dis", 10))
    cr.save()
    cr.rotate(t * hiz)
    pts = []
    for k in range(dis * 2):
        aci = k * math.pi / dis
        r = 56 if k % 2 == 0 else 42
        for d in (-0.12, 0.12):
            pts.append((math.cos(aci + d) * r, math.sin(aci + d) * r))
    sekil(cr, poligon_yolu(pts), renk, olcek=110, parlama=False)
    sekil(cr, daire_yolu(16), koyu(renk, 0.6), golge=0)
    cr.restore()


def _saat(cr, t, p):
    sekil(cr, kutu_yolu(-10, -72, 20, 14, 4), GRI, golge=0.2)
    sekil(cr, daire_yolu(55), p.get("renk", KIRMIZI))
    sekil(cr, daire_yolu(44), BEYAZ, golge=0.12, parlama=False)
    for k in range(12):
        aci = k * math.pi / 6
        ince_cizgi(cr, [(math.cos(aci) * 36, math.sin(aci) * 36), (math.cos(aci) * 42, math.sin(aci) * 42)], kalin=3,
                   egri=False)
    aci = t * p.get("hiz", 2.0) - math.pi / 2
    ince_cizgi(cr, [(0, 0), (math.cos(aci) * 34, math.sin(aci) * 34)], kalin=5, renk=KIRMIZI, egri=False)
    cr.arc(0, 0, 5, 0, 2 * math.pi)
    cr.set_source_rgb(*KONTUR)
    cr.fill()


def _pil(cr, t, p):
    sev = max(0.0, min(1.0, p.get("seviye", 1.0)))
    sekil(cr, kutu_yolu(-14, -78, 28, 14, 4), GRI, golge=0.2)
    sekil(cr, kutu_yolu(-40, -66, 80, 136, 14), (0.25, 0.27, 0.32), parlama=False)
    renk = karistir(KIRMIZI, YESIL, min(1, sev * 1.6)) if sev < 0.6 else YESIL
    h = 116 * sev
    if h > 2:
        sekil(cr, kutu_yolu(-30, 60 - h, 60, h, 8), renk, kalin=3)
    if sev < 0.25 and int(t * 4) % 2 == 0:
        yazi(cr, "!", 0, 22, 60, renk=KIRMIZI)


def _isaret(metin, zemin, renk_yazi=(1, 1, 1)):
    def ciz(cr, t, p):
        sekil(cr, daire_yolu(52), p.get("renk", zemin))
        yazi(cr, metin, 0, 26, 78, renk=renk_yazi, kontur=0.1)
    return ciz


def _onay(cr, t, p):
    sekil(cr, daire_yolu(52), p.get("renk", YESIL))
    cizgi(cr, [(-24, 2), (-6, 20), (26, -18)], BEYAZ, kalin=12, egri=False)


def _carpi(cr, t, p):
    sekil(cr, daire_yolu(52), p.get("renk", KIRMIZI))
    cizgi(cr, [(-20, -20), (20, 20)], BEYAZ, kalin=12, egri=False)
    cizgi(cr, [(20, -20), (-20, 20)], BEYAZ, kalin=12, egri=False)


def _top(cr, t, p):
    sekil(cr, daire_yolu(34), p.get("renk", (0.95, 0.95, 0.9)))
    ince_cizgi(cr, [(-22, -24), (-8, 0), (-22, 24)], kalin=4, renk=KIRMIZI)
    ince_cizgi(cr, [(22, -24), (8, 0), (22, 24)], kalin=4, renk=KIRMIZI)


def _sopa(cr, t, p):
    cr.save()
    cr.rotate(-0.5)
    sekil(cr, egri_yolu([(-8, 70), (-7, 20), (-15, -40), (-14, -75), (0, -82), (14, -75), (15, -40), (7, 20),
                         (8, 70)]), p.get("renk", (0.85, 0.62, 0.35)), olcek=60)
    sekil(cr, kutu_yolu(-10, 58, 20, 18, 5), (0.2, 0.2, 0.25), golge=0.2)
    cr.restore()


def _kalp(cr, t, p):
    atis = 1 + 0.08 * max(0, math.sin(t * 7)) ** 8 * p.get("atis", 1)
    cr.save()
    cr.scale(atis, atis)
    sekil(cr, egri_yolu([(0, -25), (25, -55), (58, -35), (50, 5), (0, 52), (-50, 5), (-58, -35), (-25, -55)]),
          p.get("renk", KIRMIZI), olcek=110)
    cr.restore()


def _yildiz(cr, t, p):
    pts = []
    for k in range(10):
        r = 55 if k % 2 == 0 else 24
        aci = -math.pi / 2 + k * math.pi / 5
        pts.append((math.cos(aci) * r, math.sin(aci) * r))
    sekil(cr, poligon_yolu(pts), p.get("renk", SARI), olcek=105)


def _para(cr, t, p):
    don = abs(math.cos(t * p.get("hiz", 0.0)))
    cr.save()
    cr.scale(max(0.15, don), 1)
    sekil(cr, daire_yolu(48), SARI)
    sekil(cr, daire_yolu(36), (0.96, 0.7, 0.15), golge=0.1, parlama=False)
    yazi(cr, p.get("metin", "₺"), 0, 20, 52, renk=SARI, kontur=0.12)
    cr.restore()


def _kupa(cr, t, p):
    sekil(cr, egri_yolu([(-45, -60), (45, -60), (40, -10), (15, 15), (-15, 15), (-40, -10)]), SARI, olcek=110)
    for i in (-1, 1):
        ince_cizgi(cr, [(i * 42, -48), (i * 66, -40), (i * 58, -10), (i * 32, -6)], kalin=8, renk=KONTUR)
    sekil(cr, kutu_yolu(-8, 14, 16, 26, 3), SARI, golge=0.2)
    sekil(cr, kutu_yolu(-34, 40, 68, 20, 6), (0.55, 0.35, 0.2), golge=0.2)


def _tahta(cr, t, p):
    """Yazı tahtası; p['metin'] satırları '\\n' ile."""
    g, h = p.get("g", 420), p.get("h", 230)
    sekil(cr, kutu_yolu(-g / 2 - 14, -h / 2 - 14, g + 28, h + 28, 14), KAHVE, parlama=False)
    sekil(cr, kutu_yolu(-g / 2, -h / 2, g, h, 8), (0.16, 0.36, 0.3), golge=0.06, parlama=False, kalin=3)
    satirlar = str(p.get("metin", "")).split("\n")
    boy = p.get("boyut", 64)
    y0 = -(len(satirlar) - 1) * boy * 0.55 + boy * 0.32
    for i, s in enumerate(satirlar):
        yazi(cr, s, 0, y0 + i * boy * 1.1, boy, renk=(0.97, 0.97, 0.92), kontur=0, golge=False)


def _levha(cr, t, p):
    """Ahşap tabela."""
    metin = str(p.get("metin", ""))
    boy = p.get("boyut", 40)
    g = max(160, len(metin) * boy * 0.55 + 50)
    sekil(cr, kutu_yolu(-8, 0, 16, 90, 4), KAHVE, golge=0.25)
    sekil(cr, kutu_yolu(-g / 2, -60, g, 70, 10), (0.88, 0.66, 0.4), parlama=False)
    yazi(cr, metin, 0, -12, boy, renk=(0.4, 0.22, 0.1), kontur=0, golge=False)


def _balon(dusunce):
    def ciz(cr, t, p):
        metin = str(p.get("metin", ""))
        boy = p.get("boyut", 40)
        satirlar = satirlara_bol(cr, metin, boy, p.get("azami", 360)) or [""]
        from .cizim import yazi_genislik
        g = max(yazi_genislik(cr, s, boy) for s in satirlar) + 60
        h = len(satirlar) * boy * 1.1 + 36
        kuyruk = p.get("kuyruk", -1)  # -1: sol alt, +1: sağ alt
        renk = p.get("renk", BEYAZ)
        if dusunce:
            rnd = random.Random(7)
            pts = []
            n = 14
            for k in range(n):
                aci = k * 2 * math.pi / n
                pts.append((math.cos(aci) * (g / 2 + 10), math.sin(aci) * (h / 2 + 10)))
            for (x, y) in pts:
                sekil(cr, daire_yolu(30 + rnd.uniform(-4, 6), x * 0.86, y * 0.82), renk, golge=0, parlama=False)
            sekil(cr, elips_yolu(g / 2, h / 2), renk, kalin=0, golge=0, parlama=False)
            for k, r in enumerate((14, 9)):
                sekil(cr, daire_yolu(r, kuyruk * (g / 2 - 10 + k * 22), h / 2 + 30 + k * 26), renk, golge=0,
                      parlama=False)
        else:
            yol = kutu_yolu(-g / 2, -h / 2, g, h, 28)
            sekil(cr, yol, renk, golge=0.05, parlama=False)
            sekil(cr, poligon_yolu([(kuyruk * g * 0.12, h / 2 - 4), (kuyruk * g * 0.32, h / 2 + 40),
                                    (kuyruk * g * 0.3, h / 2 - 4)]), renk, golge=0, parlama=False)
            # kuyruğun balonla birleştiği yerdeki çizgiyi ört
            cr.new_path()
            cr.rectangle(min(kuyruk * g * 0.12, kuyruk * g * 0.3) + 5, h / 2 - 9, g * 0.18 - 10, 10)
            cr.set_source_rgb(*renk[:3])
            cr.fill()
        y0 = -h / 2 + 18 + boy * 0.85
        for i, s in enumerate(satirlar):
            yazi(cr, s, 0, y0 + i * boy * 1.1, boy, renk=p.get("yazi_renk", (0.12, 0.1, 0.14)), kontur=0, golge=False)
    return ciz


def _patlama(cr, t, p):
    """Çizgi roman patlaması ("POW!")."""
    rnd = random.Random(int(p.get("tohum", 3)))
    pts = []
    n = 16
    for k in range(n * 2):
        aci = k * math.pi / n
        r = (95 if k % 2 == 0 else 62) * rnd.uniform(0.9, 1.1)
        pts.append((math.cos(aci) * r * 1.35, math.sin(aci) * r))
    sekil(cr, poligon_yolu(pts), p.get("renk", SARI), olcek=150, parlama=False)
    yazi(cr, str(p.get("metin", "POW!")), 0, 18, p.get("boyut", 56), renk=p.get("yazi_renk", KIRMIZI), kontur=0.14)


def _ok(cr, t, p):
    """Kalın gösterge oku (sağa bakar; aci ile döndürülür)."""
    sekil(cr, poligon_yolu([(-60, -14), (20, -14), (20, -34), (64, 0), (20, 34), (20, 14), (-60, 14)]),
          p.get("renk", SARI), olcek=90)


def _terazi(cr, t, p):
    """Terazi: p['egim'] -1 (sol ağır) .. +1 (sağ ağır)."""
    e = p.get("egim", 0.0) * 0.35 + math.sin(t * 2) * 0.02
    sekil(cr, poligon_yolu([(-50, 110), (50, 110), (12, 90), (-12, 90)]), KAHVE)
    sekil(cr, kutu_yolu(-8, -60, 16, 155, 5), (0.75, 0.55, 0.3), golge=0.25)
    cr.save()
    cr.translate(0, -60)
    cr.rotate(e)
    sekil(cr, kutu_yolu(-150, -7, 300, 14, 6), (0.85, 0.65, 0.35))
    cr.restore()
    for i in (-1, 1):
        ux = i * 150 * math.cos(e)
        uy = -60 + i * 150 * math.sin(e)
        ince_cizgi(cr, [(ux, uy), (ux - 45, uy + 70)], kalin=3, egri=False)
        ince_cizgi(cr, [(ux, uy), (ux + 45, uy + 70)], kalin=3, egri=False)
        sekil(cr, egri_yolu([(ux - 60, uy + 70), (ux + 60, uy + 70), (ux + 35, uy + 92), (ux - 35, uy + 92)]),
              (0.8, 0.8, 0.85))
        etk = p.get("sol" if i < 0 else "sag")
        if etk:
            yazi(cr, etk, ux, uy + 60, 30, renk=(1, 1, 1), kontur=0.16)


def _alarm(cr, t, p):
    titre = math.sin(t * 50) * 6 * p.get("cal", 0.0)
    cr.save()
    cr.rotate(math.radians(titre))
    for i in (-1, 1):
        sekil(cr, daire_yolu(18, i * 38, -50), GRI, golge=0.2, parlama=False)
        ince_cizgi(cr, [(i * 30, 40), (i * 42, 62)], kalin=7, egri=False)
    _saat(cr, t * 6 if p.get("cal", 0) > 0.5 else 0, dict(renk=p.get("renk", MAVI), hiz=1.0))
    cr.restore()
    if p.get("cal", 0) > 0.5:
        for i in (-1, 1):
            for k in range(3):
                aci = -math.pi / 2 + i * (0.5 + k * 0.35)
                ince_cizgi(cr, [(math.cos(aci) * 72, math.sin(aci) * 72), (math.cos(aci) * 92, math.sin(aci) * 92)],
                           kalin=5, egri=False)


def _zzz(cr, t, p):
    for k in range(3):
        u = (t * 0.6 + k / 3) % 1.0
        yazi(cr, "z", 20 * k + u * 30, -u * 80, 26 + 14 * k, renk=BEYAZ, alfa=1 - u, kontur=0.14)


def _kitap(cr, t, p):
    sekil(cr, egri_yolu([(-70, -40), (0, -30), (70, -40), (70, 40), (0, 50), (-70, 40)], gerginlik=0.2),
          p.get("renk", MAVI), olcek=120)
    sekil(cr, egri_yolu([(-62, -34), (0, -24), (62, -34), (62, 32), (0, 42), (-62, 32)], gerginlik=0.2), BEYAZ,
          golge=0.05, parlama=False)
    ince_cizgi(cr, [(0, -24), (0, 42)], kalin=4, egri=False)
    for k in range(3):
        for i in (-1, 1):
            ince_cizgi(cr, [(i * 12, -10 + k * 14), (i * 50, -14 + k * 14)], kalin=2.5, renk=GRI, egri=False)


def _soru(cr, t, p):
    yazi(cr, "?", 0, 40, p.get("boyut", 130), renk=p.get("renk", SARI), kontur=0.12)


def _unlem(cr, t, p):
    yazi(cr, "!", 0, 40, p.get("boyut", 130), renk=p.get("renk", KIRMIZI), kontur=0.12)


def _yazi(cr, t, p):
    yazi(cr, str(p.get("metin", "")), 0, 0, p.get("boyut", 60), renk=p.get("renk", BEYAZ), kontur=0.14,
         aile=p.get("aile", YAZI))


def _isiltilar(cr, t, p):
    rnd = random.Random(int(p.get("tohum", 1)))
    for k in range(8):
        aci = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(40, 110)
        u = (t * 1.2 + k / 8) % 1.0
        s = math.sin(u * math.pi) * rnd.uniform(8, 15)
        x, y = math.cos(aci) * r, math.sin(aci) * r
        pts = []
        for j in range(8):
            rr = s if j % 2 == 0 else s * 0.35
            a2 = j * math.pi / 4
            pts.append((x + math.cos(a2) * rr, y + math.sin(a2) * rr))
        sekil(cr, poligon_yolu(pts), p.get("renk", SARI), kalin=2.5, golge=0, parlama=False)


CIZIMLER = {
    "ampul": _ampul, "beyin": _beyin, "disli": _disli, "saat": _saat, "pil": _pil, "onay": _onay, "carpi": _carpi,
    "top": _top, "sopa": _sopa, "kalp": _kalp, "yildiz": _yildiz, "para": _para, "kupa": _kupa, "tahta": _tahta,
    "levha": _levha, "konusma": _balon(False), "dusunce": _balon(True), "patlama": _patlama, "ok": _ok,
    "terazi": _terazi, "alarm": _alarm, "zzz": _zzz, "kitap": _kitap, "soru": _soru, "unlem": _unlem,
    "yazi": _yazi, "isiltilar": _isiltilar,
    "artı": _isaret("+", MAVI), "eksi": _isaret("−", KIRMIZI),
}


# ---------------------------------------------------------------- tarih eşyaları
CELIK = (0.72, 0.75, 0.8)
ALTIN = (0.98, 0.78, 0.25)
BIZANS = (0.5, 0.2, 0.55)
SELCUK = (0.1, 0.55, 0.55)


def _kilic(cr, t, p):
    """Dikey kılıç (ucu yukarı)."""
    sekil(cr, poligon_yolu([(-7, 30), (-7, -70), (0, -88), (7, -70), (7, 30)]), p.get("renk", CELIK), olcek=80)
    ince_cizgi(cr, [(0, 25), (0, -72)], kalin=2, renk=acik(CELIK, 0.6), egri=False)
    sekil(cr, kutu_yolu(-26, 28, 52, 10, 4), ALTIN, golge=0.2, parlama=False)
    sekil(cr, kutu_yolu(-5, 38, 10, 28, 3), (0.45, 0.25, 0.12), golge=0.2, parlama=False)
    sekil(cr, daire_yolu(7, 0, 70), ALTIN, golge=0.1, parlama=False, kalin=3)


def _yay(cr, t, p):
    """Türk yayı (çift kavisli) + gergin kiriş; p['ok']: oku takılı."""
    ince_cizgi(cr, [(-4, -62), (-4, 62)], kalin=2.5, renk=(0.95, 0.92, 0.85), egri=False)
    from .cizim import cizgi as kalin_cizgi
    kalin_cizgi(cr, [(-4, -62), (8, -50), (14, -25), (18, 0), (14, 25), (8, 50), (-4, 62)], p.get("renk", (0.55, 0.3, 0.12)),
                kalin=7, kontur=2.5)
    if p.get("ok", 0) > 0.5:
        ince_cizgi(cr, [(-4, 0), (60, 0)], kalin=3, renk=(0.5, 0.35, 0.2), egri=False)
        sekil(cr, poligon_yolu([(60, -6), (74, 0), (60, 6)]), CELIK, kalin=2, golge=0, parlama=False)


def _kalkan_yuvarlak(cr, t, p):
    renk = p.get("renk", BIZANS)
    sekil(cr, daire_yolu(55), renk, olcek=110)
    sekil(cr, daire_yolu(46), koyu(renk, 0.85), golge=0.0, parlama=False, kalin=3)
    sekil(cr, daire_yolu(13), ALTIN, golge=0.2, kalin=3)
    if p.get("hac", 1):
        for aci in (0, math.pi / 2):
            cr.save()
            cr.rotate(aci)
            ince_cizgi(cr, [(-40, 0), (-16, 0)], kalin=6, renk=ALTIN, egri=False)
            ince_cizgi(cr, [(16, 0), (40, 0)], kalin=6, renk=ALTIN, egri=False)
            cr.restore()


def _sancak(cr, t, p):
    renk = p.get("renk", SELCUK)
    sekil(cr, kutu_yolu(-4, -120, 8, 200, 3), (0.5, 0.32, 0.15), golge=0.25, parlama=False)
    sekil(cr, daire_yolu(7, 0, -122), ALTIN, golge=0.1, parlama=False, kalin=3)
    dal = math.sin(t * 4) * 6
    sekil(cr, egri_yolu([(4, -115), (40, -120 + dal), (80, -112 - dal), (95, -92), (80, -72 + dal), (40, -80 - dal),
                         (4, -75)], gerginlik=0.4), renk, olcek=90)
    if p.get("metin"):
        yazi(cr, str(p["metin"]), 48, -88, 22, renk=(1, 1, 1), kontur=0.12)


def _fil(cr, t, p):
    """Ağır zırhlı fil (Bizans ordusu metaforu). p['yuru']: adım salınımı."""
    renk = (0.62, 0.62, 0.68)
    adim = math.sin(t * 3) * p.get("yuru", 0.0)
    for i, x in enumerate((-70, -30, 40, 80)):
        dy = adim * (8 if i % 2 else -8)
        sekil(cr, kutu_yolu(x - 18, 20 + min(dy, 0), 36, 70 - abs(dy) * 0.3, 10), koyu(renk, 0.92), golge=0.15)
    sekil(cr, elips_yolu(120, 75, 0, -10), renk, olcek=200)
    # zırh örtüsü (çul)
    sekil(cr, egri_yolu([(-90, -60), (60, -70), (80, 10), (-95, 20)], gerginlik=0.3), p.get("ortu", BIZANS),
          olcek=160)
    ince_cizgi(cr, [(-85, 8), (75, 0)], kalin=6, renk=ALTIN)
    ince_cizgi(cr, [(-10, -42), (-10, -6)], kalin=9, renk=ALTIN, egri=False)
    ince_cizgi(cr, [(-28, -26), (8, -26)], kalin=9, renk=ALTIN, egri=False)
    # baş, kulak, hortum, fildişi
    sekil(cr, elips_yolu(46, 58, 120, -30), koyu(renk, 0.95), olcek=110)
    sekil(cr, egri_yolu([(80, -70), (40, -60), (30, -10), (60, 20), (95, 0)], gerginlik=0.5), koyu(renk, 0.85),
          olcek=90)
    hortum = math.sin(t * 2) * 10
    from .cizim import cizgi as kalin_cizgi
    kalin_cizgi(cr, [(150, -10), (170, 30), (178 + hortum, 70), (195 + hortum, 82)], koyu(renk, 0.95), kalin=24)
    sekil(cr, egri_yolu([(140, 5), (175, 20), (190, 8), (172, 12)], gerginlik=0.3), (0.98, 0.96, 0.88), golge=0.1,
          parlama=False, kalin=3)
    sekil(cr, egri_yolu([(118, -60), (160, -66), (160, -40), (120, -42)]), CELIK, golge=0.2, parlama=False, kalin=4)
    sekil(cr, elips_yolu(9, 12, 135, -40), (1, 1, 1), golge=0, parlama=False, kalin=3)
    cr.arc(137, -38, 5, 0, 2 * math.pi)
    cr.set_source_rgb(*KONTUR)
    cr.fill()
    if p.get("ter", 0) > 0.5:
        u = (t * 0.9) % 1
        sekil(cr, egri_yolu([(175, -80 + u * 30), (182, -66 + u * 30), (175, -60 + u * 30), (168, -66 + u * 30)]),
              (0.6, 0.85, 1.0), alfa=1 - u, kalin=3, golge=0)


def _ari(cr, x, y, s, t, kanat):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    for i in (-1, 1):
        cr.save()
        cr.translate(i * 4, -12)
        cr.rotate(i * (0.5 + 0.4 * math.sin(t * 60 + kanat)))
        sekil(cr, elips_yolu(7, 12, 0, -8), (0.92, 0.97, 1.0), kalin=2.5, golge=0, parlama=False)
        cr.restore()
    sekil(cr, elips_yolu(16, 11), SARI, kalin=3, golge=0.15)
    for dx in (-5, 3):
        cr.rectangle(dx, -10, 4, 20)
    cr.set_source_rgb(*KONTUR)
    cr.fill()
    cr.arc(13, -3, 2, 0, 2 * math.pi)
    cr.fill()
    cr.restore()


def _ari_suru(cr, t, p):
    """Arı sürüsü (hafif ve hızlı atlı okçular metaforu). p['hedef_x']: sürünün hücum ettiği nokta (yerel)."""
    n = int(p.get("adet", 12))
    hucum = p.get("hucum", 0.0)
    rnd = random.Random(5)
    for k in range(n):
        r0 = rnd.uniform(20, 90)
        hiz = rnd.uniform(2.5, 4.5) * (1 if k % 2 else -1)
        faz = rnd.uniform(0, 6.28)
        x = math.cos(t * hiz + faz) * r0 * 1.3
        y = math.sin(t * hiz * 1.3 + faz) * r0 * 0.7
        # hücumda öne atılıp geri döner (yaklaş-ok at-uzaklaş)
        dalga = max(0.0, math.sin(t * 3 + k * 0.7)) * hucum
        x += p.get("hedef_x", -250) * dalga
        _ari(cr, x, y, rnd.uniform(0.9, 1.3), t, k)


def _kapi(cr, t, p):
    """Taş kemer ve iki kanatlı kapı; p['acik'] 0..1."""
    acik = p.get("acik", 0.0)
    g = cairo.RadialGradient(0, -40, 10, 0, -40, 220)
    g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.9 * acik)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
    cr.set_source(g)
    cr.arc(0, -40, 220, 0, 2 * math.pi)
    cr.fill()
    tas = (0.78, 0.7, 0.58)
    sekil(cr, egri_yolu([(-170, 120), (-170, -90), (-120, -170), (0, -200), (120, -170), (170, -90), (170, 120)],
                        kapali=True, gerginlik=0.3), tas, olcek=300)
    ic = egri_yolu([(-110, 120), (-110, -70), (-70, -130), (0, -145), (70, -130), (110, -70), (110, 120)], gerginlik=0.3)
    sekil(cr, ic, (1.0, 0.93, 0.7) if acik > 0.02 else (0.25, 0.18, 0.12), golge=0, parlama=False)
    cr.save()
    cr.new_path()
    ic(cr)
    cr.clip()
    for i in (-1, 1):
        w = 110 * (1 - acik * 0.85)
        x0 = i * 110
        x1 = x0 - i * w
        renk = (0.55, 0.33, 0.16)
        sekil(cr, poligon_yolu([(x0, 125), (x0, -150), (x1, -150 + acik * 20), (x1, 125 - acik * 20)]), renk,
              golge=0.1, parlama=False)
        for k in range(1, 4):
            xx = x0 - i * w * k / 4
            ince_cizgi(cr, [(xx, -150), (xx, 125)], kalin=3, renk=koyu(renk, 0.7), egri=False)
    cr.restore()
    for k in range(5):
        aci = math.pi * (1.15 + k * 0.175)
        ince_cizgi(cr, [(math.cos(aci) * 140, -60 + math.sin(aci) * 125), (math.cos(aci) * 170, -60 + math.sin(aci) * 150)],
                   kalin=3, renk=koyu(tas, 0.65), egri=False)
    if p.get("metin"):
        yazi(cr, str(p["metin"]), 0, -158, 34, renk=(1, 0.95, 0.85), kontur=0.15)


def _damga(cr, t, p):
    cr.save()
    cr.rotate(-0.2)
    metin = str(p.get("metin", "ESİR"))
    boy = p.get("boyut", 46)
    from .cizim import yazi_genislik
    g = yazi_genislik(cr, metin, boy) + 40
    cr.new_path()
    kutu_yolu(-g / 2, -boy * 0.75, g, boy * 1.3, 8)(cr)
    cr.set_source_rgba(0.85, 0.12, 0.12, 0.95)
    cr.set_line_width(6)
    cr.stroke()
    yazi(cr, metin, 0, boy * 0.33, boy, renk=(0.85, 0.12, 0.12), kontur=0, golge=False)
    cr.restore()


def _ok_yagmuru(cr, t, p):
    """Soldan sağa (yon=1) ya da sağdan sola (yon=-1) kavis çizerek uçan oklar."""
    yon = p.get("yon", -1)
    gen = p.get("genislik", 520)
    yog = int(p.get("adet", 14))
    rnd = random.Random(int(p.get("tohum", 2)))
    for k in range(yog):
        faz = rnd.random()
        u = (t * p.get("hiz", 0.9) + faz) % 1.0
        x = (u - 0.5) * gen * yon
        y = -math.sin(u * math.pi) * 120 + rnd.uniform(-40, 40)
        egim = math.atan2(-math.cos(u * math.pi) * 120 * math.pi, gen * yon)
        cr.save()
        cr.translate(x, y)
        cr.rotate(egim)
        ince_cizgi(cr, [(-26, 0), (14, 0)], kalin=3, renk=(0.35, 0.22, 0.12), egri=False)
        cr.move_to(14, -5)
        cr.line_to(24, 0)
        cr.line_to(14, 5)
        cr.close_path()
        cr.set_source_rgb(*KONTUR)
        cr.fill()
        ince_cizgi(cr, [(-26, 0), (-32, -5)], kalin=2.5, renk=(0.9, 0.9, 0.9), egri=False)
        ince_cizgi(cr, [(-26, 0), (-32, 5)], kalin=2.5, renk=(0.9, 0.9, 0.9), egri=False)
        cr.restore()


def _pin(cr, t, p):
    """Harita iğnesi + şehir adı."""
    renk = p.get("renk", KIRMIZI)
    nab = 1 + 0.15 * max(0.0, math.sin(t * 4)) * p.get("nabiz", 0)
    cr.save()
    cr.scale(nab, nab)
    sekil(cr, egri_yolu([(0, 0), (-16, -26), (-16, -42), (0, -54), (16, -42), (16, -26)], gerginlik=0.4), renk, olcek=60)
    sekil(cr, daire_yolu(7, 0, -38), (1, 1, 1), golge=0, parlama=False, kalin=3)
    cr.restore()
    if p.get("metin"):
        yazi(cr, str(p["metin"]), p.get("yazi_dx", 0), p.get("yazi_dy", 30), p.get("boyut", 30), renk=(1, 1, 1),
             kontur=0.18)


def _hilal(cr, t, p):
    """Hilal (yay) düzeni: kalkan işaretlerinden oluşan kavis; p['kapan'] 0..1 uçları içe kapatır."""
    kapan = p.get("kapan", 0.0)
    renk = p.get("renk", SELCUK)
    n = int(p.get("adet", 9))
    for k in range(n):
        u = k / (n - 1) - 0.5
        aci = u * (math.pi * (0.9 + 0.7 * kapan))
        x = -math.cos(aci) * 160 + 160 - 40 * kapan * abs(u) * 2
        y = math.sin(aci) * 200
        cx, cy = x - 160, y + math.sin(t * 5 + k) * 3
        sekil(cr, daire_yolu(19, cx, cy), renk, kalin=3.5, golge=0.2, parlama=False)
        ince_cizgi(cr, [(cx + 4, cy - 11), (cx - 5, cy), (cx + 4, cy + 11)], kalin=3, renk=(1, 1, 1))
        ince_cizgi(cr, [(cx + 4, cy - 11), (cx + 4, cy + 11)], kalin=1.5, renk=(1, 1, 1), egri=False)
        ince_cizgi(cr, [(cx - 10, cy), (cx + 10, cy)], kalin=2, renk=(1, 1, 1), egri=False)


CIZIMLER.update({"kilic": _kilic, "yay": _yay, "kalkan": _kalkan_yuvarlak, "sancak": _sancak, "fil": _fil,
                 "ari_suru": _ari_suru, "kapi": _kapi, "damga": _damga, "ok_yagmuru": _ok_yagmuru, "pin": _pin,
                 "hilal": _hilal})


class Nesne:
    """Sahnedeki bir eşya. Sayısal parametreler (seviye, yanik, egim, cal...) anahtar kareyle
    canlandırılır; metin gibi sayı olmayanlar sabit kalır ya da degistir() ile anında değişir."""

    katman = 4

    def __init__(self, tur, x, y, olcek=1.0, aci=0.0, katman=None, sabit=False, **p):
        self.tur = tur
        self.sabit = sabit  # True: kameradan bağımsız (ekran üstü)
        if katman is not None:
            self.katman = katman
        sayisal = {k: v for k, v in p.items() if isinstance(v, (int, float))}
        self.metinler = [(-1e9, {k: v for k, v in p.items() if not isinstance(v, (int, float))})]
        self.iz = Iz(dict(x=x, y=y, olcek=0.0, aci=aci, alfa=1.0, sallan=0.0, **sayisal))
        self.hedef_olcek = olcek
        self.olaylar = []  # (t, sfx) — sahne, ses efektlerini buradan toplar

    def belir(self, t, sure=0.45, ses="pop"):
        self.iz.ayarla(t, dict(olcek=0.0))
        self.iz.ekle(t + sure, dict(olcek=self.hedef_olcek), sure=sure, egri="geri_tepme")
        if ses:
            self.olaylar.append((t, ses))
        return self

    def goster(self, t):
        """Animasyonsuz görünür yap."""
        self.iz.ayarla(t, dict(olcek=self.hedef_olcek))
        return self

    def kaybol(self, t, sure=0.3, ses=None):
        self.iz.ekle(t + sure, dict(olcek=0.0), sure=sure, egri="hizlan")
        if ses:
            self.olaylar.append((t, ses))
        return self

    def git(self, t0, t1, x=None, y=None, egri="yumusak"):
        h = {}
        if x is not None:
            h["x"] = x
        if y is not None:
            h["y"] = y
        self.iz.ekle(t1, h, sure=t1 - t0, egri=egri)
        return self

    def ayarla(self, t, sure=0.4, egri="yumusak", **p):
        """Sayısal parametreleri canlandırır (ör. seviye=0.2, yanik=1, olcek=1.4)."""
        if "olcek" in p:
            self.hedef_olcek = p["olcek"]
        self.iz.ekle(t + sure, p, sure=sure, egri=egri)
        return self

    def degistir(self, t, ses=None, **p):
        """Metin gibi sayısal olmayan parametreleri t anında değiştirir."""
        yeni = dict(self.metinler[-1][1])
        yeni.update(p)
        self.metinler.append((t, yeni))
        self.metinler.sort(key=lambda e: e[0])
        if ses:
            self.olaylar.append((t, ses))
        return self

    def salla(self, t0, t1):
        self.iz.ekle(t0 + 0.1, dict(sallan=1.0), sure=0.1)
        self.iz.ekle(t1, dict(sallan=0.0), sure=0.2)
        return self

    def ciz(self, cr, t):
        d = self.iz.deger(t)
        if d["olcek"] <= 0.01 or d["alfa"] <= 0.01:
            return
        p = {}
        for t0, m in self.metinler:
            if t >= t0:
                p = m
        p = dict(p)
        p.update(d)
        cr.save()
        cr.translate(d["x"], d["y"] + math.sin(t * 3.1) * 3 * (1 if self.tur not in ("tahta", "levha", "terazi") else 0))
        cr.rotate(math.radians(d["aci"] + math.sin(t * 18) * 8 * d["sallan"]))
        cr.scale(d["olcek"], d["olcek"])
        if d["alfa"] < 0.99:
            cr.push_group()
            CIZIMLER[self.tur](cr, t, p)
            cr.pop_group_to_source()
            cr.paint_with_alpha(d["alfa"])
        else:
            CIZIMLER[self.tur](cr, t, p)
        cr.restore()
