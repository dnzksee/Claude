"""Gerçek coğrafyalı strateji haritası (Natural Earth verisi, kamu malı).

Harita(kapsam) -> arka plan yüzeyi + proj(lon, lat) -> (x, y) dünya koordinatı.
Harita öğeleri: Bolge (imparatorluk alanı), Sehir, Rota (sefer yolu + hareket eden ordu işareti).
"""
import json
import math
import os

import cairo
import numpy as np

from .harita import DUNYA_G, DUNYA_Y, OLCEK, _gurultu
from .sahne import TARAFLAR, yumusat, _yazi, _yuvarlak_dikdortgen, HareketOku

VERI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "veri")

_onbellek = {}


def _kara_poligonlari():
    """world-atlas land-50m TopoJSON -> [[(lon,lat),...], ...] halkalar."""
    if "kara" in _onbellek:
        return _onbellek["kara"]
    topo = json.load(open(os.path.join(VERI, "land-50m.json")))
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    yaylar = []
    for yay in topo["arcs"]:
        x = y = 0
        nokt = []
        for dx, dy in yay:
            x += dx
            y += dy
            nokt.append((x * sx + tx, y * sy + ty))
        yaylar.append(nokt)

    def halka(indeksler):
        out = []
        for i in indeksler:
            p = yaylar[i] if i >= 0 else yaylar[~i][::-1]
            out.extend(p if not out else p[1:])
        return out

    halkalar = []
    for geo in topo["objects"]["land"]["geometries"]:
        polys = geo["arcs"] if geo["type"] == "MultiPolygon" else [geo["arcs"]]
        for poly in polys:
            for h in poly:
                halkalar.append(halka(h))
    _onbellek["kara"] = halkalar
    return halkalar


def _geojson(dosya):
    if dosya not in _onbellek:
        _onbellek[dosya] = json.load(open(os.path.join(VERI, dosya)))["features"]
    return _onbellek[dosya]


# Sıradağlar (lon, lat) — haritaya dağ simgesi olarak çizilir
SIRADAGLAR = [
    [(39.5, 43.4), (42.5, 42.9), (45.0, 42.2), (47.5, 41.5), (49.0, 40.9)],      # Kafkaslar
    [(29.5, 37.0), (32.0, 36.6), (34.5, 37.2), (36.5, 37.8), (38.5, 38.3), (41.0, 38.4)],  # Toroslar
    [(31.0, 41.1), (34.0, 41.3), (37.0, 40.8), (40.0, 40.6), (42.0, 40.9)],      # Kuzey Anadolu
    [(44.5, 37.2), (46.0, 35.0), (47.8, 33.4), (50.0, 31.2), (52.5, 29.5), (55.0, 28.0)],  # Zagros
    [(48.5, 37.3), (51.0, 36.2), (53.5, 36.6), (56.0, 37.3), (59.0, 37.2)],      # Elburz / Kopet
    [(67.0, 35.0), (70.0, 35.6), (73.0, 36.2)],                                    # Hindukuş
    [(22.0, 42.0), (24.5, 42.6), (26.5, 42.7)],                                    # Balkanlar
]

NEHIRLER = ("Euphrates", "Tigris", "Nile", "Volga", "Amu  Darya", "Syr Darya", "Danube")


class Harita:
    """kapsam: (lon_bati, lon_dogu, lat_merkez). Dünya 1920x1080 olacak şekilde ölçeklenir."""

    def __init__(self, lon0, lon1, lat_merkez, etiketler=(), tohum=3, dag_olcek=1.0):
        self.lon0, self.lon1 = lon0, lon1
        self.c = math.cos(math.radians(lat_merkez))
        self.s = DUNYA_G / ((lon1 - lon0) * self.c)
        yari_lat = DUNYA_Y / self.s / 2
        self.lat1 = lat_merkez + yari_lat
        self.etiketler = etiketler
        self.tohum = tohum
        self.dag_olcek = dag_olcek
        self._yuzey = None

    def proj(self, lon, lat):
        return (lon - self.lon0) * self.c * self.s, (self.lat1 - lat) * self.s

    def kara_yolu(self, cr):
        for h in _kara_poligonlari():
            if not h:
                continue
            lons = [p[0] for p in h]
            if max(lons) < self.lon0 - 15 or min(lons) > self.lon1 + 15:
                continue
            x, y = self.proj(*h[0])
            cr.move_to(x, y)
            for p in h[1:]:
                cr.line_to(*self.proj(*p))
            cr.close_path()

    def _gol_yolu(self, cr):
        for f in _geojson("lakes.json"):
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                for h in poly[:1]:
                    lons = [p[0] for p in h]
                    if max(lons) < self.lon0 - 5 or min(lons) > self.lon1 + 5:
                        continue
                    cr.move_to(*self.proj(*h[0]))
                    for p in h[1:]:
                        cr.line_to(*self.proj(*p))
                    cr.close_path()

    @property
    def yuzey(self):
        if self._yuzey is None:
            self._yuzey = self._uret()
        return self._yuzey

    def _uret(self):
        G, Y = DUNYA_G * OLCEK, DUNYA_Y * OLCEK
        rng = np.random.default_rng(self.tohum)
        n = _gurultu(G, Y, rng, oktav=6, baslangic=5)
        ince = _gurultu(G, Y, rng, oktav=3, baslangic=80)
        yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, G, Y)
        cr = cairo.Context(yuzey)
        cr.scale(OLCEK, OLCEK)

        # deniz
        cr.set_source_rgb(0.47, 0.60, 0.64)
        cr.paint()
        # kıyı dalga çizgileri (eski harita stili)
        for gen, a in ((46, 0.10), (30, 0.12), (18, 0.16), (9, 0.22)):
            self.kara_yolu(cr)
            cr.set_source_rgba(0.85, 0.9, 0.88, a)
            cr.set_line_width(gen)
            cr.stroke()
        # kara
        self.kara_yolu(cr)
        cr.set_source_rgb(0.86, 0.79, 0.62)
        cr.fill_preserve()
        cr.set_source_rgba(0.36, 0.27, 0.17, 0.9)
        cr.set_line_width(2.2)
        cr.stroke()
        # göller
        self._gol_yolu(cr)
        cr.set_source_rgb(0.47, 0.60, 0.64)
        cr.fill_preserve()
        cr.set_source_rgba(0.36, 0.27, 0.17, 0.8)
        cr.set_line_width(1.5)
        cr.stroke()
        # nehirler
        for f in _geojson("rivers.json"):
            if f["properties"].get("name") not in NEHIRLER:
                continue
            g = f["geometry"]
            hatlar = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
            for h in hatlar:
                cr.move_to(*self.proj(*h[0]))
                for p in h[1:]:
                    cr.line_to(*self.proj(*p))
                cr.set_source_rgba(0.30, 0.47, 0.56, 0.85)
                cr.set_line_width(2.6)
                cr.set_line_join(cairo.LINE_JOIN_ROUND)
                cr.stroke()
        # dağ simgeleri
        rnd = np.random.default_rng(self.tohum + 1)
        for hat in SIRADAGLAR:
            pts = [self.proj(*p) for p in hat]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                d = math.hypot(x2 - x1, y2 - y1)
                adim = 26 * self.dag_olcek
                for k in range(int(d / adim) + 1):
                    u = k * adim / max(d, 1)
                    x = x1 + (x2 - x1) * u + rnd.normal() * 6 * self.dag_olcek
                    y = y1 + (y2 - y1) * u + rnd.normal() * 6 * self.dag_olcek
                    self._dag(cr, x, y, (14 + rnd.random() * 8) * self.dag_olcek)

        # doku: gürültüyü çarpımsal uygula
        tampon = np.ndarray((Y, G, 4), np.uint8, buffer=yuzey.get_data(), strides=(yuzey.get_stride(), 4, 1))
        carpan = (0.86 + 0.2 * n + 0.08 * ince)
        yy, xx = np.mgrid[0:Y, 0:G].astype(np.float32)
        vin = 1 - 0.32 * np.clip(((xx / G - 0.5) * 2) ** 2 + ((yy / Y - 0.5) * 2) ** 2 - 0.3, 0, 1)
        carpan = (carpan * vin)[..., None]
        tampon[..., :3] = np.clip(tampon[..., :3].astype(np.float32) * carpan, 0, 255).astype(np.uint8)
        yuzey.mark_dirty()

        # sabit etiketler (denizler, bölgeler)
        cr = cairo.Context(yuzey)
        cr.scale(OLCEK, OLCEK)
        for (lon, lat, metin, boyut, tur) in self.etiketler:
            x, y = self.proj(lon, lat)
            if tur == "deniz":
                _yazi(cr, metin, x, y, boyut, aile="Caladea", kalin=False, italik=True,
                      renk=(0.2, 0.32, 0.38), alfa=0.8)
            else:
                cr.select_font_face("Caladea", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                harfli = " ".join(metin.upper())
                _yazi(cr, harfli, x, y, boyut, aile="Caladea", renk=(0.42, 0.32, 0.2), alfa=0.5)
        return yuzey

    @staticmethod
    def _dag(cr, x, y, s):
        cr.move_to(x - s, y + s * 0.45)
        cr.line_to(x - s * 0.15, y - s * 0.6)
        cr.line_to(x + s, y + s * 0.45)
        cr.close_path()
        cr.set_source_rgba(0.66, 0.56, 0.40, 0.75)
        cr.fill()
        cr.move_to(x - s * 0.15, y - s * 0.6)
        cr.line_to(x + s, y + s * 0.45)
        cr.line_to(x + s * 0.2, y + s * 0.45)
        cr.close_path()
        cr.set_source_rgba(0.40, 0.31, 0.2, 0.55)
        cr.fill()
        cr.move_to(x - s, y + s * 0.45)
        cr.line_to(x - s * 0.15, y - s * 0.6)
        cr.line_to(x + s, y + s * 0.45)
        cr.set_source_rgba(0.33, 0.25, 0.15, 0.8)
        cr.set_line_width(1.4)
        cr.stroke()


# ---------------------------------------------------------------- harita öğeleri
class Bolge:
    """İmparatorluk/devlet alanı. Poligon kaba çizilebilir; kara ile kırpılır."""

    katman = 0

    def __init__(self, harita, taraf, poligon, t0, t1=1e9, ad=None, etiket_konum=None, etiket_boyut=34,
                 alfa=0.42):
        self.taraf, self.t0, self.t1, self.ad = taraf, t0, t1, ad
        self.alfa = alfa
        self.etiket_boyut = etiket_boyut
        self.etiket = harita.proj(*etiket_konum) if etiket_konum else None
        r, g, b = TARAFLAR[taraf]["renk"]
        self.yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, DUNYA_G * OLCEK, DUNYA_Y * OLCEK)
        cr = cairo.Context(self.yuzey)
        cr.scale(OLCEK, OLCEK)
        harita.kara_yolu(cr)
        cr.clip()
        pts = [harita.proj(*p) for p in poligon]
        cr.move_to(*pts[0])
        for p in pts[1:]:
            cr.line_to(*p)
        cr.close_path()
        yol = cr.copy_path()
        cr.set_source_rgba(r, g, b, 1)
        cr.fill()
        # iç kenar parlaması
        cr.append_path(yol)
        cr.set_source_rgba(min(1, r * 0.6), min(1, g * 0.6), min(1, b * 0.6), 1)
        cr.set_line_width(10)
        cr.stroke()
        cr.append_path(yol)
        cr.set_source_rgba(*TARAFLAR[taraf]["vurgu"], 1)
        cr.set_line_width(2.5)
        cr.set_dash([12, 6])
        cr.stroke()

    def kaybol(self, t):
        self.t1 = t
        return self

    def ciz(self, cr, t):
        if t < self.t0 or t > self.t1 + 1.0:
            return
        a = min(yumusat((t - self.t0) / 1.2), 1 - yumusat((t - self.t1) / 1.0))
        cr.save()
        cr.scale(1 / OLCEK, 1 / OLCEK)
        cr.set_source_surface(self.yuzey, 0, 0)
        cr.paint_with_alpha(self.alfa * a)
        cr.restore()
        if self.ad and self.etiket:
            x, y = self.etiket
            _yazi(cr, self.ad.upper(), x, y, self.etiket_boyut, aile="Caladea", renk=(1, 0.97, 0.9),
                  alfa=a, kontur=((*[c * 0.45 for c in TARAFLAR[self.taraf]["renk"]],), 6, 0.9))


class Sehir:
    katman = 3
    zoom_duyarli = True

    def __init__(self, harita, lon, lat, ad, t0, t1=1e9, onemli=False, yon="sag", nabiz=False):
        self.x, self.y = harita.proj(lon, lat)
        self.ad, self.t0, self.t1, self.onemli, self.yon, self.nabiz = ad, t0, t1, onemli, yon, nabiz

    def ciz(self, cr, t, kamera_zoom=1.0):
        if t < self.t0 or t > self.t1 + 0.6:
            return
        a = min(yumusat((t - self.t0) / 0.6), 1 - yumusat((t - self.t1) / 0.6))
        z = 1 / max(kamera_zoom, 1) ** 0.75   # yakınlaşınca simge/yazı büyümesin
        r = (11 if self.onemli else 7) * z
        if self.nabiz:
            u = ((t - self.t0) % 1.6) / 1.6
            cr.arc(self.x, self.y, r + 30 * u * z, 0, 2 * math.pi)
            cr.set_source_rgba(0.75, 0.12, 0.08, (1 - u) * 0.7 * a)
            cr.set_line_width(3 * z)
            cr.stroke()
        cr.arc(self.x, self.y, r, 0, 2 * math.pi)
        cr.set_source_rgba(0.98, 0.95, 0.88, a)
        cr.fill_preserve()
        cr.set_source_rgba(0.2, 0.13, 0.08, a)
        cr.set_line_width(3 * z)
        cr.stroke()
        cr.arc(self.x, self.y, r * 0.45, 0, 2 * math.pi)
        cr.set_source_rgba(0.55, 0.12, 0.08, a)
        cr.fill()
        boyut = (34 if self.onemli else 27) * z
        dx = {"sag": r + 10 * z, "sol": -(r + 10 * z), "ust": 0, "alt": 0}[self.yon]
        dy = {"sag": boyut * 0.35, "sol": boyut * 0.35, "ust": -r - 12 * z, "alt": r + boyut + 4 * z}[self.yon]
        hiza = {"sag": "sol", "sol": "sag", "ust": "orta", "alt": "orta"}[self.yon]
        _yazi(cr, self.ad, self.x + dx, self.y + dy, boyut, aile="Caladea", hiza=hiza,
              renk=(0.16, 0.1, 0.06), alfa=a, kontur=((0.97, 0.93, 0.83), 6 * z, 0.9))


class Rota:
    """Sefer yolu: uzayan ok + yol boyunca ilerleyen ordu sancağı."""

    katman = 2
    zoom_duyarli = True

    def __init__(self, harita, taraf, noktalar, t0, t1, t_son=None, kalinlik=16, etiket=None):
        pts = [harita.proj(*p) for p in noktalar]
        self.ok = HareketOku(taraf, pts, t0, t1, t_son=t_son if t_son is not None else t1 + 4,
                             kalinlik=kalinlik)
        self.taraf, self.t0, self.t1, self.etiket = taraf, t0, t1, etiket

    def ciz(self, cr, t, kamera_zoom=1.0):
        self.ok.ciz(cr, t)
        if not (self.t0 <= t <= self.ok.t_son + 0.8) or not self.etiket:
            return
        pts = self.ok._ornekle()
        u = yumusat((t - self.t0) / max(self.t1 - self.t0, 0.01))
        x, y = pts[min(len(pts) - 1, int(u * (len(pts) - 1)))]
        a = 1 - yumusat((t - self.ok.t_son) / 0.8)
        z = 1 / max(kamera_zoom, 1) ** 0.75
        cr.save()
        cr.translate(x, y - 22 * z)
        cr.scale(z, z)
        tr = TARAFLAR[self.taraf]
        cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(24)
        w = cr.text_extents(self.etiket).x_advance + 26
        _yuvarlak_dikdortgen(cr, -w / 2, -52, w, 36, 8)
        cr.set_source_rgba(*tr["renk"], 0.95 * a)
        cr.fill_preserve()
        cr.set_source_rgba(*tr["vurgu"], a)
        cr.set_line_width(2)
        cr.stroke()
        _yazi(cr, self.etiket, 0, -26, 24, renk=(1, 1, 1), alfa=a)
        cr.restore()
