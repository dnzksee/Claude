"""Yumuşak 2B kamera: kaydırma, yakınlaşma, hafif dönme, "punch zoom" vuruşu, sarsıntı ve nefes.

Dünya koordinatı 1280×720 ekranla aynıdır; kamera (x, y) bakılan noktadır, zoom 1 = tam kare.
"""
import math

from .cizim import G, Y
from .zaman import Iz


class Kamera:
    def __init__(self, x=G / 2, y=Y / 2, zoom=1.0, nefes=True):
        self.iz = Iz(dict(x=x, y=y, zoom=zoom, aci=0.0, sarsinti=0.0, vurus=0.0))
        self.nefes = nefes

    def git(self, t0, t1, x=None, y=None, zoom=None, aci=None, egri="yumusak"):
        h = {k: v for k, v in dict(x=x, y=y, zoom=zoom, aci=aci).items() if v is not None}
        self.iz.ekle(t1, h, sure=t1 - t0, egri=egri)
        return self

    def ayarla(self, t, x=None, y=None, zoom=None, aci=None):
        h = {k: v for k, v in dict(x=x, y=y, zoom=zoom, aci=aci).items() if v is not None}
        self.iz.ayarla(t, h)
        return self

    def punch(self, t, miktar=0.18, sure=0.9):
        """Ani yakınlaşma vuruşu: hızla içeri, yavaşça geri."""
        self.iz.ekle(t + 0.09, dict(vurus=miktar), sure=0.09, egri="yavasla")
        self.iz.ekle(t + sure, dict(vurus=0.0), sure=sure - 0.09, egri="yumusak")
        return self

    def sars(self, t, sure=0.5, guc=1.0):
        self.iz.ekle(t + 0.05, dict(sarsinti=guc), sure=0.05)
        self.iz.ekle(t + sure, dict(sarsinti=0.0), sure=sure - 0.05, egri="yavasla")
        return self

    def durum(self, t):
        d = self.iz.deger(t)
        z = d["zoom"] * (1 + d["vurus"])
        x, y, aci = d["x"], d["y"], d["aci"]
        if self.nefes:  # el kamerası gibi çok hafif salınım
            x += math.sin(t * 0.37) * 5
            y += math.sin(t * 0.29 + 1) * 3
            z *= 1 + 0.008 * math.sin(t * 0.21)
        if d["sarsinti"] > 0.001:
            s = d["sarsinti"]
            x += (math.sin(t * 71) + math.sin(t * 43)) * 7 * s
            y += (math.cos(t * 67) + math.sin(t * 51)) * 6 * s
            aci += math.sin(t * 59) * 0.8 * s
        return x, y, z, aci

    def uygula(self, cr, t, paralaks=1.0):
        """paralaks < 1: uzak katman (daha az kayar, daha az büyür)."""
        x, y, z, aci = self.durum(t)
        cr.translate(G / 2, Y / 2)
        cr.scale(1 + (z - 1) * paralaks, 1 + (z - 1) * paralaks)
        cr.rotate(math.radians(aci) * paralaks)
        cr.translate(-(G / 2 + (x - G / 2) * paralaks), -(Y / 2 + (y - Y / 2) * paralaks))
