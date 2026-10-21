"""İskelet tabanlı çizgi film karakteri: büyük kafa, abartılı mimik, pozlanabilir kollar.

Konum (x, y) ayakların yere bastığı noktadır; olcek=1 iken karakter ≈ 280 px boyundadır.
Bütün parametreler anahtar kare izindedir (Iz); ifade ve pozlar hazır ön ayarlardan seçilir,
geçişler yumuşak ya da "geri tepmeli" (çizgi film esnekliği) olur. Göz kırpma, nefes alma ve
yürüme salınımı otomatiktir.
"""
import math
import random

from .cizim import (sekil, cizgi, ince_cizgi, daire_yolu, elips_yolu, kutu_yolu, egri_yolu, poligon_yolu, yer_golgesi,
                    koyu, acik, KONTUR)
from .zaman import Iz, yumusak

# ifade: göz açıklığı, kaş açısı (+ kızgın), kaş yüksekliği, ağız eğrisi (+ gülümseme), ağız açıklığı,
#        yanak kızarması, ter, bakış
IFADELER = {
    "notr":      dict(goz=1.0, kas_aci=0.0, kas_y=0.0, agiz_egri=0.3, agiz_acik=0.0, yanak=0.0, ter=0.0),
    "mutlu":     dict(goz=0.9, kas_aci=-0.1, kas_y=0.25, agiz_egri=1.0, agiz_acik=0.35, yanak=0.8, ter=0.0),
    "kahkaha":   dict(goz=0.15, kas_aci=-0.2, kas_y=0.4, agiz_egri=1.0, agiz_acik=1.0, yanak=1.0, ter=0.0),
    "saskin":    dict(goz=1.45, kas_aci=-0.35, kas_y=1.0, agiz_egri=0.0, agiz_acik=0.85, yanak=0.0, ter=0.0),
    "kizgin":    dict(goz=0.8, kas_aci=1.0, kas_y=-0.45, agiz_egri=-0.7, agiz_acik=0.25, yanak=0.0, ter=0.0),
    "uzgun":     dict(goz=0.85, kas_aci=-0.8, kas_y=0.25, agiz_egri=-0.85, agiz_acik=0.0, yanak=0.0, ter=0.0),
    "dusunceli": dict(goz=0.75, kas_aci=-0.25, kas_y=0.2, agiz_egri=-0.15, agiz_acik=0.0, yanak=0.0, ter=0.0,
                      bakis_x=0.6, bakis_y=-0.9),
    "yorgun":    dict(goz=0.4, kas_aci=-0.45, kas_y=-0.1, agiz_egri=-0.35, agiz_acik=0.2, yanak=0.0, ter=1.0),
    "gururlu":   dict(goz=0.55, kas_aci=-0.1, kas_y=0.45, agiz_egri=1.0, agiz_acik=0.0, yanak=0.4, ter=0.0),
    "panik":     dict(goz=1.5, kas_aci=-0.8, kas_y=0.85, agiz_egri=-0.75, agiz_acik=0.7, yanak=0.0, ter=1.0),
    "utangac":   dict(goz=0.7, kas_aci=-0.5, kas_y=0.1, agiz_egri=0.35, agiz_acik=0.0, yanak=1.0, ter=1.0,
                      bakis_y=0.8),
    "kararli":   dict(goz=0.85, kas_aci=0.55, kas_y=-0.2, agiz_egri=0.45, agiz_acik=0.0, yanak=0.0, ter=0.0),
    "uykulu":    dict(goz=0.08, kas_aci=-0.2, kas_y=-0.1, agiz_egri=0.1, agiz_acik=0.15, yanak=0.0, ter=0.0),
}

# poz: kol açıları (derece; 0 = aşağı sarkık, + dışa/yukarı), dirsek bükümü, gövde eğimi
POZLAR = {
    "dur":           dict(kolL=14, dirsekL=10, kolR=14, dirsekR=10, egim=0),
    "el_salla":      dict(kolL=14, dirsekL=10, kolR=150, dirsekR=25, egim=-3),
    "isaret":        dict(kolL=14, dirsekL=10, kolR=92, dirsekR=0, egim=-4),
    "kollar_yukari": dict(kolL=122, dirsekL=25, kolR=122, dirsekR=25, egim=0),
    "dusun":         dict(kolL=30, dirsekL=-95, kolR=25, dirsekR=165, egim=4),
    "omuz_silk":     dict(kolL=30, dirsekL=60, kolR=30, dirsekR=60, egim=0),
    "eller_belde":   dict(kolL=40, dirsekL=-77, kolR=40, dirsekR=-77, egim=-2),
    "yorgun":        dict(kolL=4, dirsekL=0, kolR=4, dirsekR=0, egim=10),
    "sunum":         dict(kolL=14, dirsekL=10, kolR=70, dirsekR=-40, egim=-3),
    "kutlama":       dict(kolL=120, dirsekL=-10, kolR=150, dirsekR=10, egim=0),
    "dur_isareti":   dict(kolL=14, dirsekL=10, kolR=80, dirsekR=-80, egim=3),
    "kafa_kasi":     dict(kolL=14, dirsekL=10, kolR=120, dirsekR=120, egim=3),
}

TEN = (0.98, 0.80, 0.64)


class Karakter:
    katman = 5

    def __init__(self, ad, govde=(0.95, 0.5, 0.15), sac="diken", sac_renk=(0.25, 0.15, 0.08), ten=TEN,
                 gozluk=False, pantolon=(0.22, 0.25, 0.38), ayakkabi=(0.15, 0.12, 0.12), x=-300, y=600,
                 olcek=1.0, yon=1, ifade="notr", poz="dur", sapka=None, sapka_renk=None, sakal=None, etek=False,
                 kemer=None, elde=None):
        """sapka: bork | tac | migfer | sarik | None; sakal: renk ya da None; etek: kaftan;
        elde: {"R": "yay"|"kilic"|"sancak"|"kalkan", "L": ...} (eşya adı ya da (ad, parametreler))."""
        self.ad, self.govde, self.sac, self.sac_renk, self.ten = ad, govde, sac, sac_renk, ten
        self.gozluk, self.pantolon, self.ayakkabi = gozluk, pantolon, ayakkabi
        self.sapka, self.sapka_renk, self.sakal, self.etek, self.kemer = sapka, sapka_renk, sakal, etek, kemer
        self.elde = elde or {}
        bas = dict(x=x, y=y, olcek=olcek, alfa=1.0, yon=yon, zipla=0.0, ezil=0.0, bas_egim=0.0, yuru=0.0,
                   titre=0.0, salla=0.0, bakis_x=0.0, bakis_y=0.0, hiz_cizgi=0.0)
        bas.update(IFADELER[ifade])
        bas.update(POZLAR[poz])
        bas.setdefault("bakis_x", 0.0)
        self.iz = Iz(bas)
        self.kirpma = random.Random(ad).uniform(0, 3)

    # ------------------------------------------------------------ oyunculuk
    def ifade(self, t, ad, sure=0.25):
        d = dict(bakis_x=0.0, bakis_y=0.0)
        d.update(IFADELER[ad])
        self.iz.ekle(t + sure, d, sure=sure, egri="geri_tepme")
        return self

    def poz(self, t, ad, sure=0.35):
        self.iz.ekle(t + sure, POZLAR[ad], sure=sure, egri="geri_tepme")
        return self

    def bak(self, t, bx, by=0.0, sure=0.2):
        self.iz.ekle(t + sure, dict(bakis_x=bx, bakis_y=by), sure=sure)
        return self

    def don(self, t, yon, sure=0.2):
        self.iz.ekle(t + sure, dict(yon=yon), sure=sure)
        return self

    def git(self, t0, t1, x=None, y=None, kos=False):
        """Yürüyerek/koşarak gider; yüzünü gidiş yönüne çevirir."""
        hedef = {}
        if x is not None:
            hedef["x"] = x
            simdi = self.iz("x", t0)
            if abs(x - simdi) > 1:
                self.don(t0, 1 if x > simdi else -1, 0.12)
        if y is not None:
            hedef["y"] = y
        self.iz.ekle(t1, hedef, sure=t1 - t0, egri="yumusak" if not kos else "dogrusal")
        guc = 1.6 if kos else 1.0
        self.iz.ekle(t0 + 0.15, dict(yuru=guc, hiz_cizgi=1.0 if kos else 0.0), sure=0.15)
        self.iz.ekle(t1 + 0.15, dict(yuru=0.0, hiz_cizgi=0.0), sure=0.2)
        return self

    def gir(self, t, taraf="sol", x=400, sure=1.2, kos=False):
        self.iz.ayarla(t - 0.01, dict(x=-180 if taraf == "sol" else 1460, alfa=1.0))
        return self.git(t, t + sure, x=x, kos=kos)

    def cik(self, t, taraf="sag", sure=1.0, kos=False):
        return self.git(t, t + sure, x=-220 if taraf == "sol" else 1500, kos=kos)

    def belir(self, t, sure=0.4):
        """Yerinde 'pat' diye ortaya çıkar (ezilip uzayarak)."""
        o = self.iz("olcek", t)
        ilk = self.iz.izler["olcek"][0]
        self.iz.izler["olcek"][0] = (ilk[0], ilk[1], 0.01, ilk[3])  # belirmeden önce görünmez
        self.iz.ayarla(t, dict(olcek=0.01))
        self.iz.ekle(t + sure, dict(olcek=o), sure=sure, egri="geri_tepme")
        return self

    def zipla(self, t, yukseklik=70, sure=0.55):
        """Hazırlık (çömel) -> sıçra (uza) -> düş (ezil) -> toparlan."""
        self.iz.ekle(t + 0.1, dict(ezil=0.5), sure=0.1)
        self.iz.ekle(t + 0.1 + sure / 2, dict(zipla=yukseklik, ezil=-0.4), sure=sure / 2, egri="yavasla")
        self.iz.ekle(t + 0.1 + sure, dict(zipla=0.0, ezil=0.0), sure=sure / 2, egri="hizlan")
        self.iz.ekle(t + 0.2 + sure, dict(ezil=0.45), sure=0.1)
        self.iz.ekle(t + 0.5 + sure, dict(ezil=0.0), sure=0.3, egri="elastik")
        return self

    def salla(self, t0, t1):
        self.iz.ekle(t0 + 0.1, dict(salla=1.0), sure=0.1)
        self.iz.ekle(t1, dict(salla=0.0), sure=0.2)
        return self

    def titre(self, t0, t1, guc=1.0):
        self.iz.ekle(t0 + 0.1, dict(titre=guc), sure=0.1)
        self.iz.ekle(t1, dict(titre=0.0), sure=0.2)
        return self

    def bas_egim(self, t, aci, sure=0.3):
        self.iz.ekle(t + sure, dict(bas_egim=aci), sure=sure, egri="geri_tepme")
        return self

    def kaybol(self, t, sure=0.3):
        self.iz.ekle(t + sure, dict(alfa=0.0), sure=sure)
        return self

    # ------------------------------------------------------------ çizim
    def bas_konumu(self, t):
        """Başın merkezi (balon, ikon yerleştirmek için)."""
        d = self.iz.deger(t)
        s = d["olcek"]
        return d["x"], d["y"] - (215 + d["zipla"]) * s

    def ciz(self, cr, t):
        d = self.iz.deger(t)
        if d["alfa"] <= 0.01 or d["olcek"] <= 0.02:
            return
        a, s = d["alfa"], d["olcek"]
        yon = max(-1.0, min(1.0, d["yon"]))
        faz = t * 2 * math.pi * (1.9 if d["yuru"] > 1.2 else 1.5)
        yuru = d["yuru"]
        nefes = math.sin(t * 2.4 + self.kirpma) * 0.012
        sek = abs(math.sin(faz)) * 7 * min(yuru, 1.5)
        tx = math.sin(t * 60) * 4 * d["titre"]
        x, y = d["x"] + tx, d["y"]
        yer_golgesi(cr, x, y + 2, 60 * s * (1 - min(d["zipla"], 120) / 300), alfa=0.22 * a)
        cr.save()
        cr.translate(x, y - (d["zipla"] + sek) * s)
        ez = d["ezil"]
        cr.scale(s * (1 + ez * 0.35), s * (1 - ez * 0.3 + nefes))
        if d["hiz_cizgi"] > 0.05:
            for k in range(4):
                yy = -60 - k * 45
                uz = 90 + 40 * math.sin(t * 20 + k)
                ince_cizgi(cr, [(-yon * 70, yy), (-yon * (70 + uz), yy)], kalin=5, alfa=a * d["hiz_cizgi"] * 0.7)
        cr.rotate(math.radians(d["egim"] * yon + math.sin(faz) * 3 * yuru))
        # bacaklar
        for k, isaret in enumerate((-1, 1)):
            aci = math.sin(faz + k * math.pi) * 28 * min(yuru, 1.6)
            kx, ky = isaret * 17, -70
            ax = kx + math.sin(math.radians(aci)) * 66
            ay = ky + math.cos(math.radians(aci)) * 66
            cizgi(cr, [(kx, ky), (ax, ay)], self.pantolon, kalin=22, alfa=a, egri=False)
            sekil(cr, elips_yolu(19, 11, ax + yon * 8, ay - 2), self.ayakkabi, alfa=a, kalin=4, golge=0.15)
        # gövde (armut) / kaftan
        if self.etek:
            sekil(cr, egri_yolu([(-36, -80), (36, -80), (52, -18), (0, -10), (-52, -18)], gerginlik=0.35),
                  koyu(self.govde, 0.9), alfa=a, olcek=90)
        govde = egri_yolu([(-32, -150), (32, -150), (42, -95), (38, -66), (-38, -66), (-42, -95)])
        sekil(cr, govde, self.govde, alfa=a, olcek=95)
        if self.etek:  # kaftan yakası
            ince_cizgi(cr, [(-18, -150), (yon * 6, -95), (6 * yon, -66)], kalin=4, renk=koyu(self.govde, 0.6), alfa=a)
        if self.kemer:
            sekil(cr, kutu_yolu(-40, -84, 80, 13, 5), self.kemer, alfa=a, golge=0.15, parlama=False, kalin=4)
        # kollar
        self._kollar(cr, d, faz, yuru, yon, a, t)
        # baş
        cr.save()
        cr.translate(0, -212)
        cr.rotate(math.radians(d["bas_egim"] + math.sin(faz * 2) * 2 * yuru))
        self._bas(cr, d, yon, a, t)
        cr.restore()
        cr.restore()

    def _kollar(self, cr, d, faz, yuru, yon, a, t):
        for taraf in ("L", "R"):
            isaret = -1 if taraf == "L" else 1
            ks = d["kol" + taraf] + math.sin(faz + (0 if taraf == "L" else math.pi)) * 25 * min(yuru, 1.6)
            dr = d["dirsek" + taraf]
            if taraf == "R" and d["salla"] > 0.01:
                dr += math.sin(t * 16) * 28 * d["salla"]
            # sağ/sol kol, yüz yönüne göre ayna (yon<0 iken sağ kol ekranın solunda)
            yon_isaret = isaret * (1 if yon >= 0 else -1)
            ox, oy = yon_isaret * 31, -140
            r1, r2 = math.radians(ks), math.radians(ks + dr)
            ex, ey = ox + yon_isaret * math.sin(r1) * 46, oy + math.cos(r1) * 46
            hx, hy = ex + yon_isaret * math.sin(r2) * 44, ey + math.cos(r2) * 44
            cizgi(cr, [(ox, oy), (ex, ey), (hx, hy)], self.govde, kalin=17, alfa=a, egri=False)
            esya = self.elde.get(taraf)
            if esya:
                self._esya(cr, esya, hx, hy, r2, yon_isaret, a, t)
            sekil(cr, daire_yolu(11, hx, hy), self.ten, alfa=a, kalin=4, golge=0.15, parlama=False)

    def _esya(self, cr, esya, hx, hy, aci, isaret, a, t):
        from .nesneler import CIZIMLER
        ad, p = (esya, {}) if isinstance(esya, str) else esya
        cr.save()
        cr.translate(hx, hy)
        if ad == "kalkan":  # kalkan gövdenin önünde, dik durur
            cr.scale(0.75, 0.75)
        elif ad == "yay":
            cr.scale(isaret * 0.85, 0.85)
        elif ad == "sancak":
            cr.translate(0, 40)
            cr.scale(isaret * 0.9, 0.9)
        else:  # kılıç: önkolun yönünde tutulur
            cr.rotate(-isaret * aci + math.pi)
            cr.translate(0, -30)
            cr.scale(0.75, 0.75)
        if a < 0.99:
            cr.push_group()
            CIZIMLER[ad](cr, t, p)
            cr.pop_group_to_source()
            cr.paint_with_alpha(a)
        else:
            CIZIMLER[ad](cr, t, p)
        cr.restore()

    def _bas(self, cr, d, yon, a, t):
        R = 64
        fx = yon * 9  # yüz, baktığı yöne hafif kayar (3/4 görünüş hissi)
        # arka saç (topuz / uzun)
        if self.sac == "topuz":
            sekil(cr, daire_yolu(26, -yon * 10, -R - 6), self.sac_renk, alfa=a, kalin=5)
        # kulaklar
        for i in (-1, 1):
            sekil(cr, elips_yolu(11, 15, i * (R - 4) + fx * 0.2, 6), self.ten, alfa=a, kalin=4, golge=0.1,
                  parlama=False)
        sekil(cr, egri_yolu([(-R, -5), (-R * 0.7, -R * 0.82), (0, -R), (R * 0.7, -R * 0.82), (R, -5),
                             (R * 0.8, R * 0.6), (0, R * 0.95), (-R * 0.8, R * 0.6)]), self.ten, alfa=a, olcek=130)
        if self.sakal:  # sakal (ağızdan önce, ağız üstüne çizilir)
            sekil(cr, egri_yolu([(-R * 0.82, 0), (-R * 0.55, R * 0.5), (fx * 0.5, R * 1.25), (R * 0.55, R * 0.5),
                                 (R * 0.82, 0), (R * 0.5, R * 0.35), (fx, R * 0.42), (-R * 0.5, R * 0.35)],
                                gerginlik=0.45), self.sakal, alfa=a, olcek=110, parlama=False)
        if self.sapka not in ("migfer", "tac", "bork", "sarik"):
            self._sac(cr, R, yon, a)
        else:
            self._sac_kisa(cr, R, yon, a)
        # yanak
        if d["yanak"] > 0.02:
            for i in (-1, 1):
                cr.save()
                cr.translate(i * 34 + fx, 22)
                cr.scale(14, 8)
                cr.arc(0, 0, 1, 0, 2 * math.pi)
                cr.restore()
                cr.set_source_rgba(0.95, 0.35, 0.35, 0.45 * d["yanak"] * a)
                cr.fill()
        # gözler
        goz = d["goz"]
        kirp = (t + self.kirpma) % 3.7
        if kirp < 0.12:
            goz *= abs(kirp - 0.06) / 0.06 * 0.9 + 0.05
        for i in (-1, 1):
            gx, gy = i * 23 + fx, -4
            ry = max(1.5, 17 * goz)
            if goz > 0.18:
                sekil(cr, elips_yolu(14 + 2 * max(goz - 1, 0), ry, gx, gy), (1, 1, 1), alfa=a, kalin=3.5,
                      golge=0.0, parlama=False)
                cr.save()
                cr.new_path()
                elips_yolu(14 + 2 * max(goz - 1, 0), ry, gx, gy)(cr)
                cr.clip()
                px = gx + d["bakis_x"] * 6 + yon * 2
                py = gy + d["bakis_y"] * 6
                cr.arc(px, py, 7.5, 0, 2 * math.pi)
                cr.set_source_rgba(*KONTUR, a)
                cr.fill()
                cr.arc(px - 2.5, py - 3, 2.6, 0, 2 * math.pi)
                cr.set_source_rgba(1, 1, 1, a)
                cr.fill()
                cr.restore()
            else:  # kapalı / kısık göz: kavis
                ince_cizgi(cr, [(gx - 13, gy + 1), (gx, gy - 5 if d["agiz_egri"] > 0.5 else gy + 4), (gx + 13, gy + 1)],
                           kalin=4.5, alfa=a)
            # kaş
            ky = gy - 25 - d["kas_y"] * 9 - max(goz - 1, 0) * 8
            egim = d["kas_aci"] * 9 * -i
            ince_cizgi(cr, [(gx - 13, ky - egim), (gx, ky - abs(egim) * 0.2 - 2), (gx + 13, ky + egim)],
                       kalin=6, alfa=a)
        if self.gozluk:
            for i in (-1, 1):
                cr.new_path()
                cr.arc(i * 23 + fx, -4, 21, 0, 2 * math.pi)
                cr.set_source_rgba(0.75, 0.9, 1.0, 0.18 * a)
                cr.fill_preserve()
                cr.set_source_rgba(*KONTUR, a)
                cr.set_line_width(4.5)
                cr.stroke()
            ince_cizgi(cr, [(-3 + fx, -6), (3 + fx, -6)], kalin=4.5, alfa=a, egri=False)
        # burun
        ince_cizgi(cr, [(fx + yon * 2, 8), (fx + yon * 7, 16), (fx, 18)], kalin=3.5, alfa=a)
        # ağız
        self._agiz(cr, fx, 36, d, a)
        if self.sakal:  # bıyık
            for i in (-1, 1):
                ince_cizgi(cr, [(fx, 27), (fx + i * 14, 25), (fx + i * 24, 33)], kalin=7, renk=self.sakal, alfa=a)
        if self.sapka:
            self._sapka(cr, R, yon, a, t)
        # ter damlası
        if d["ter"] > 0.05:
            u = (t * 0.8) % 1.0
            dx, dy = R * 0.82, -R * 0.45 + u * 30
            sekil(cr, egri_yolu([(dx, dy - 14), (dx + 8, dy + 2), (dx, dy + 9), (dx - 8, dy + 2)]),
                  (0.6, 0.85, 1.0), alfa=a * d["ter"] * (1 - u * 0.6), kalin=3, golge=0.1)

    def _agiz(self, cr, x, y, d, a):
        g = 26
        egri = d["agiz_egri"]
        acik = d["agiz_acik"]
        if acik < 0.08:
            ince_cizgi(cr, [(x - g / 2, y - egri * 4), (x, y + egri * 8), (x + g / 2, y - egri * 4)], kalin=5,
                       alfa=a)
            return
        ust = y - egri * 5 - acik * 4
        alt = y + 6 + acik * 24 + max(egri, 0) * 4
        gen = g / 2 * (1 + 0.25 * max(egri, 0)) * (0.75 if egri < 0.2 and acik > 0.6 else 1)
        yol = egri_yolu([(x - gen, ust), (x, ust + egri * 6), (x + gen, ust), (x + gen * 0.6, alt - 4),
                         (x, alt), (x - gen * 0.6, alt - 4)])
        sekil(cr, yol, (0.45, 0.08, 0.1), alfa=a, kalin=4, golge=0.0, parlama=False)
        cr.save()
        cr.new_path()
        yol(cr)
        cr.clip()
        cr.save()
        cr.translate(x, alt + 2)
        cr.scale(gen * 0.75, 9)
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgba(0.95, 0.45, 0.5, a)
        cr.fill()
        if egri > 0.4:  # dişler
            cr.rectangle(x - gen, ust - 2, gen * 2, 7)
            cr.set_source_rgba(1, 1, 1, a)
            cr.fill()
        cr.restore()

    def _sac_kisa(self, cr, R, yon, a):
        """Başlık altında görünen kısa saç (kulak hizası)."""
        for i in (-1, 1):
            sekil(cr, egri_yolu([(i * R * 0.98, -R * 0.35), (i * R * 1.02, R * 0.15), (i * R * 0.78, R * 0.1),
                                 (i * R * 0.8, -R * 0.4)]), self.sac_renk, alfa=a, kalin=4, golge=0.1, parlama=False)

    def _sapka(self, cr, R, yon, a, t):
        from .nesneler import ALTIN, CELIK
        if self.sapka == "bork":  # Türk börkü: kürk kenar, yüksek tepe, sorguç
            tepe = self.sapka_renk or (0.85, 0.2, 0.15)
            sekil(cr, egri_yolu([(-R * 0.78, -R * 0.62), (-R * 0.55, -R * 1.55), (0, -R * 1.78), (R * 0.55, -R * 1.55),
                                 (R * 0.78, -R * 0.62)], gerginlik=0.45), tepe, alfa=a, olcek=120)
            sekil(cr, egri_yolu([(-R * 1.02, -R * 0.42), (-R * 0.95, -R * 0.82), (0, -R * 0.95), (R * 0.95, -R * 0.82),
                                 (R * 1.02, -R * 0.42), (0, -R * 0.55)], gerginlik=0.4), (0.95, 0.9, 0.82), alfa=a,
                  olcek=110)
            for k in range(7):  # kürk dokusu
                x = -R * 0.85 + k * R * 0.28
                ince_cizgi(cr, [(x, -R * 0.62), (x + 4, -R * 0.78)], kalin=2.5, renk=(0.7, 0.62, 0.5), alfa=a)
            sal = math.sin(t * 3) * 4
            sekil(cr, egri_yolu([(R * 0.1, -R * 1.6), (R * 0.45 + sal, -R * 2.25), (R * 0.62 + sal, -R * 2.45),
                                 (R * 0.42, -R * 1.95), (R * 0.25, -R * 1.6)]), (0.98, 0.96, 0.92), alfa=a, kalin=3.5,
                  golge=0.15, parlama=False)
            sekil(cr, daire_yolu(8, R * 0.15, -R * 1.62), ALTIN, alfa=a, kalin=3, golge=0.1, parlama=False)
        elif self.sapka == "tac":  # Bizans tacı (kamelaukion) + inci sarkıtlar
            for i in (-1, 1):
                for k in range(4):
                    sekil(cr, daire_yolu(5, i * R * 0.86, -R * 0.45 + k * 13), (0.98, 0.98, 0.95), alfa=a, kalin=2.5,
                          golge=0, parlama=False)
            sekil(cr, egri_yolu([(-R * 0.82, -R * 0.55), (-R * 0.75, -R * 1.25), (0, -R * 1.5), (R * 0.75, -R * 1.25),
                                 (R * 0.82, -R * 0.55)], gerginlik=0.4), ALTIN, alfa=a, olcek=120)
            sekil(cr, kutu_yolu(-R * 0.9, -R * 0.78, R * 1.8, R * 0.3, 6), koyu(ALTIN, 0.85), alfa=a, golge=0.15,
                  parlama=False)
            for k, renk in enumerate(((0.85, 0.15, 0.2), (0.2, 0.55, 0.9), (0.85, 0.15, 0.2))):
                sekil(cr, daire_yolu(7, (k - 1) * R * 0.5, -R * 0.63), renk, alfa=a, kalin=2.5, golge=0, parlama=False)
            ince_cizgi(cr, [(0, -R * 1.5), (0, -R * 1.85)], kalin=6, renk=ALTIN, alfa=a, egri=False)
            ince_cizgi(cr, [(-12, -R * 1.72), (12, -R * 1.72)], kalin=6, renk=ALTIN, alfa=a, egri=False)
        elif self.sapka == "migfer":  # konik miğfer + burun siperi
            renk = self.sapka_renk or CELIK
            sekil(cr, egri_yolu([(-R * 1.0, -R * 0.3), (-R * 0.85, -R * 1.0), (0, -R * 1.65), (R * 0.85, -R * 1.0),
                                 (R * 1.0, -R * 0.3), (0, -R * 0.5)], gerginlik=0.35), renk, alfa=a, olcek=120)
            sekil(cr, kutu_yolu(-R * 1.02, -R * 0.52, R * 2.04, R * 0.22, 5), koyu(renk, 0.8), alfa=a, golge=0.1,
                  parlama=False)
            sekil(cr, kutu_yolu(yon * 9 - 5, -R * 0.4, 10, R * 0.55, 4), koyu(renk, 0.85), alfa=a, golge=0.1,
                  parlama=False, kalin=3.5)
            if self.sapka_renk is None:
                sekil(cr, egri_yolu([(-6, -R * 1.62), (0, -R * 1.95), (6, -R * 1.62)]), (0.85, 0.2, 0.2), alfa=a,
                      kalin=3, golge=0.1, parlama=False)
        elif self.sapka == "sarik":
            renk = self.sapka_renk or (0.97, 0.95, 0.9)
            sekil(cr, elips_yolu(R * 1.08, R * 0.62, 0, -R * 0.82), renk, alfa=a, olcek=120)
            for k in range(3):
                ince_cizgi(cr, [(-R * 0.95, -R * (0.6 + k * 0.2)), (0, -R * (0.75 + k * 0.22)), (R * 0.95, -R * (0.95 + k * 0.1))],
                           kalin=3, renk=koyu(renk, 0.8), alfa=a)

    def _sac(self, cr, R, yon, a):
        r = self.sac_renk
        if self.sac == "diken":
            pts = [(-R * 0.98, -8)]
            for i in range(7):
                u = i / 6
                ax = -R * 0.95 + u * R * 1.9
                ay = -R * 0.8 - math.sin(u * math.pi) * R * 0.25
                pts.append((ax - 8, ay + 12))
                pts.append((ax + yon * 10, ay - 28 - 10 * math.sin(u * math.pi)))
            pts.append((R * 0.98, -8))
            pts.append((R * 0.6, -R * 0.55))
            pts.append((0, -R * 0.62))
            pts.append((-R * 0.6, -R * 0.55))
            sekil(cr, poligon_yolu(pts), r, alfa=a, olcek=110)
        elif self.sac == "kivircik":
            for i in range(9):
                u = i / 8
                aci = math.pi * (1.05 + u * 0.9)
                cx, cy = math.cos(aci) * R * 0.95, math.sin(aci) * R * 0.95 - 4
                sekil(cr, daire_yolu(22, cx, cy), r, alfa=a, kalin=4.5, golge=0.15, parlama=False)
        elif self.sac in ("duz", "topuz"):
            sekil(cr, egri_yolu([(-R * 1.02, 4), (-R * 0.9, -R * 0.75), (0, -R * 1.08), (R * 0.9, -R * 0.75),
                                 (R * 1.02, 4), (R * 0.75, -R * 0.45), (yon * R * 0.2, -R * 0.55),
                                 (-R * 0.75, -R * 0.45)]), r, alfa=a, olcek=110)
        elif self.sac == "kel":
            ince_cizgi(cr, [(-R * 0.4, -R * 0.75), (-R * 0.2, -R * 0.82)], kalin=4, renk=acik(self.ten, 0.5), alfa=a)
