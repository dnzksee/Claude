"""Sahne, zaman çizelgesi ve kare üretimi (ffmpeg'e ham BGRA kareler akıtılır).

Sahne: bir arka plan + kamera + karakterler + eşyalar + ekran üstü öğeler. Konu dosyası her sahne
için bir kurgu fonksiyonu yazar; fonksiyon, cümle zamanlarını s.c(i) ile alır ve oyunculuğu bu
anlara bağlar (animasyon seslendirmeyle senkron kalır).
"""
import math
import subprocess

import cairo

from .arkaplan import arka_plan, zemin_ciz, AG, AY, KAPLA
from .cizim import G, Y, OLCEK
from .gecisler import SURELER, uygula
from .kamera import Kamera
from .karakter import Karakter
from .nesneler import Nesne


class Sahne:
    def __init__(self, no, baslik, arkaplan, t0, t1, cumleler, gecis="whip", arkaplan_p=None, tasarimlar=None,
                 bulanik=7.0, zemin=True, paralaks=0.35):
        self.no, self.baslik = no, baslik
        self.arkaplan, self.arkaplan_p = arkaplan, dict(arkaplan_p or {})
        self.t0, self.t1 = t0, t1
        self.cumleler = cumleler  # [(t0, t1, metin)] — video zamanında
        self.gecis = gecis
        self.kamera = Kamera()
        self.ogeler = []
        self.ekran_ogeleri = []
        self.sesler = []  # (t, ad, kazanc)
        self.tasarimlar = tasarimlar or {}
        self.bulanik = bulanik
        self.zemin = zemin
        self.paralaks = paralaks  # arka planın kamerayla kayma oranı (harita: 1 = sabit zemin gibi)
        if paralaks >= 0.99:  # arka plan dünyayla birlikte hareket ediyorsa kamera kenarından taşmasın
            px, py = (AG * KAPLA - G) / 2, (AY * KAPLA - Y) / 2
            self.kamera.sinir = (-px + 4, G + px - 4, -py + 4, Y + py - 4)
        self._arka = None

    # ------------------------------------------------------------ zaman kısayolları
    def c(self, i, oran=0.0):
        """i. cümlenin başlangıcı (oran: cümlenin ne kadarı geçmişken; 0..1). Negatif i sondan sayar."""
        a, b, _ = self.cumleler[i]
        return a + (b - a) * oran

    def bitis(self, i):
        return self.cumleler[i][1]

    @property
    def son(self):
        return self.t1

    # ------------------------------------------------------------ öğe ekleme
    def ekle(self, *ogeler):
        for o in ogeler:
            (self.ekran_ogeleri if getattr(o, "ekran", False) else self.ogeler).append(o)
        return ogeler[0] if len(ogeler) == 1 else ogeler

    def karakter(self, ad, **k):
        d = dict(self.tasarimlar.get(ad, {}))
        d.update(k)
        return self.ekle(Karakter(ad, **d))

    def nesne(self, tur, x, y, **p):
        n = Nesne(tur, x, y, **p)
        if n.sabit:
            n.ekran = True
        return self.ekle(n)

    def yer(self, lon, lat):
        """Harita arka planlı sahnede (boylam, enlem) -> dünya koordinatı."""
        from .arkaplan import harita_xy
        return harita_xy(self.arkaplan_p, lon, lat)

    def birlik(self, taraf, tur, x, y, **k):
        from .birlikler import OrduBirligi
        return self.ekle(OrduBirligi(taraf, tur, x, y, **k))

    def ok_akini(self, kaynak, hedef, t0, t1, yogunluk=10, tohum=0, ses=True):
        from .birlikler import OkAkini
        if ses:
            for k in range(int((t1 - t0) / 0.6)):
                self.sfx("ok", t0 + k * 0.6, 0.5)
        return self.ekle(OkAkini(kaynak, hedef, t0, t1, yogunluk, tohum))

    def yakin_plan(self, ad, t0, t1, konum="sag_alt", baslik=None, zemin=(0.98, 0.85, 0.55), **k):
        """Köşe penceresinde yakın plan karakter (sahne dünyasına eklenmez; döndürülen karakter canlandırılır)."""
        from .birlikler import YakinPlan
        from .karakter import Karakter
        d = dict(self.tasarimlar.get(ad, {}))
        d.update(k)
        d.setdefault("x", 0)
        d["y"] = 0
        kar = Karakter(ad, **d)
        self.ekle(YakinPlan(kar, t0, t1, konum=konum, zemin=zemin, baslik=baslik or ad))
        return kar

    def sfx(self, ad, t, kazanc=1.0):
        self.sesler.append((t, ad, kazanc))

    def tum_sesler(self):
        s = list(self.sesler)
        for o in self.ogeler + self.ekran_ogeleri:
            for t, ad in getattr(o, "olaylar", []):
                s.append((t, ad, 0.8))
        return s

    # ------------------------------------------------------------ çizim
    def ciz(self, cr, t):
        if self._arka is None:
            self._arka = arka_plan(self.arkaplan, self.bulanik, **self.arkaplan_p)
        cr.save()
        self.kamera.uygula(cr, t, paralaks=self.paralaks)
        cr.translate(-(AG * KAPLA - G) / 2, -(AY * KAPLA - Y) / 2)
        cr.scale(1 / OLCEK, 1 / OLCEK)  # yüzey piksel ölçeğinde
        cr.set_source_surface(self._arka, 0, 0)
        cr.paint()
        cr.restore()
        cr.save()
        self.kamera.uygula(cr, t)
        if self.zemin:
            zemin_ciz(cr, self.arkaplan, self.arkaplan_p.get("zemin"))
        for o in sorted(self.ogeler, key=lambda o: (o.katman, getattr(o, "sira", 0))):
            o.ciz(cr, t)
        cr.restore()
        for o in sorted(self.ekran_ogeleri, key=lambda o: o.katman):
            o.ciz(cr, t)


class Video:
    def __init__(self, fps=24):
        self.fps = fps
        self.sahneler = []
        self.ust = []  # bütün videonun üstündeki öğeler (altyazı)

    def ekle(self, sahne):
        self.sahneler.append(sahne)
        return sahne

    @property
    def sure(self):
        return self.sahneler[-1].t1

    def gecis_anlari(self):
        """[(sinir_zamani, gecis_turu, sure)] — geçiş, sonraki sahnenin 'gecis' alanından gelir."""
        return [(a.t1, b.gecis, SURELER.get(b.gecis, 0.5)) for a, b in zip(self.sahneler, self.sahneler[1:])]

    def _sahne_bul(self, t):
        for i, s in enumerate(self.sahneler):
            if t < s.t1 or i == len(self.sahneler) - 1:
                return i
        return len(self.sahneler) - 1

    def _sahne_kare(self, sahne, t):
        y = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(G * OLCEK), int(Y * OLCEK))
        cr = cairo.Context(y)
        cr.scale(OLCEK, OLCEK)
        sahne.ciz(cr, t)
        return y

    def kare(self, t):
        yuz = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(G * OLCEK), int(Y * OLCEK))
        cr = cairo.Context(yuz)
        cr.scale(OLCEK, OLCEK)
        i = self._sahne_bul(t)
        gecis = None
        for k, (sinir, tur, d) in enumerate(self.gecis_anlari()):
            if d > 0 and sinir - d / 2 <= t < sinir + d / 2:
                gecis = (k, tur, (t - (sinir - d / 2)) / d)
        if gecis:
            k, tur, u = gecis
            A = self._sahne_kare(self.sahneler[k], t)
            B = self._sahne_kare(self.sahneler[k + 1], t)
            uygula(tur, cr, A, B, u)
        else:
            self.sahneler[i].ciz(cr, t)
        for o in self.ust:
            o.ciz(cr, t)
        return yuz

    def kaydet(self, mp4, ses_wav, crf=20):
        n = int(math.ceil(self.sure * self.fps))
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{int(G * OLCEK)}x{int(Y * OLCEK)}",
             "-r", str(self.fps), "-i", "-", "-i", ses_wav, "-c:v", "libx264", "-preset", "medium",
             "-crf", str(crf), "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-shortest", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
        for f in range(n):
            t = f / self.fps
            ff.stdin.write(bytes(self.kare(t).get_data()))
            if f % (self.fps * 10) == 0:
                print(f"  {t:6.1f}s / {self.sure:.1f}s", flush=True)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg hata verdi")
