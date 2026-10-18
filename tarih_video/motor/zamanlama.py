"""Kelime zamanlaması: anlatıcının bir kelimeyi söylediği anı tahmin eder.

Cümle başı/sonu zamanları sesteki duraklamalardan bilinir. Cümle içinde:
  1) virgül/iki nokta gibi ara duraklar sesteki kısa sessizliklerle eşleştirilir,
  2) her ifade içindeki kelimeler hece sayısına göre dağıtılır (Türkçede hece ≈ ünlü sayısı).
Hata payı tipik olarak ±0,3 sn; animasyonu bir kelimeye bağlamak için yeterli.

Senaryoda kullanım:  T.kelime("s5", "Pasinler")  ->  saniye
"""
import re
import subprocess

UNLULER = set("aeıioöuüâîûAEIİOÖUÜÂÎÛ")
SAYI_HECE = {1: 1, 2: 3, 3: 4, 4: 5}  # rakam sayısı -> okunuşta yaklaşık hece


def hece(kelime):
    sayi = re.sub(r"\D", "", kelime)
    if sayi and len(sayi) == len(re.sub(r"[^\w]", "", kelime)):
        return SAYI_HECE.get(len(sayi), len(sayi) + 1)
    n = sum(1 for h in kelime if h in UNLULER)
    return max(1, n) + (len(sayi) if sayi else 0)


def sade(k):
    k = k.replace("İ", "i").replace("I", "ı").lower()
    return re.sub(r"[^a-zçğıöşüâîû0-9]", "", k)


def sessizlikler(ses, esik="-34dB", sure=0.12):
    cikti = subprocess.run(["ffmpeg", "-hide_banner", "-i", ses, "-af",
                            f"silencedetect=n={esik}:d={sure}", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    bas = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", cikti)]
    bit = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", cikti)]
    return list(zip(bas, bit))


def cumle_kelimeleri(t0, t1, metin, sess=()):
    """Bir cümlenin kelimelerine zaman ver. Döner: [(t, kelime), ...]"""
    kelimeler = metin.split()
    if not kelimeler:
        return []
    heceler = [hece(k) for k in kelimeler]
    toplam = sum(heceler)
    sure = t1 - t0
    ic = [s for s in sess if t0 + 0.15 < s[0] and s[1] < t1 - 0.15]
    # Bağlantı noktaları: (kelime indeksi, o kelimenin başladığı an). Virgülden sonraki kelime,
    # hece oranıyla beklenen ana en yakın iç sessizliğin bitişine oturtulur (yakınsa).
    baglar = [(0, t0)]
    birikim = 0
    kullanilan = set()
    for i, k in enumerate(kelimeler[:-1]):
        birikim += heceler[i]
        if k[-1:] in ",;:":
            beklenen = t0 + sure * birikim / toplam
            aday = min(((abs((s[0] + s[1]) / 2 - beklenen), j) for j, s in enumerate(ic)
                        if j not in kullanilan), default=None)
            if aday and aday[0] <= max(0.5, 0.12 * sure):
                kullanilan.add(aday[1])
                s = ic[aday[1]]
                if s[0] > baglar[-1][1]:
                    baglar.append((i + 1, s[1], s[0]))
    baglar.append((len(kelimeler), t1))
    sonuc = []
    for n in range(len(baglar) - 1):
        i0, a = baglar[n][0], baglar[n][1]
        i1 = baglar[n + 1][0]
        b = baglar[n + 1][2] if len(baglar[n + 1]) > 2 else baglar[n + 1][1]  # sessizlik başı
        h = sum(heceler[i0:i1]) or 1
        t = a
        for i in range(i0, i1):
            sonuc.append((t, kelimeler[i]))
            t += (b - a) * heceler[i] / h
    return sonuc


class Zaman(dict):
    """bolum id -> (baslangic, bitis). Ek olarak kelime anlarını tutar."""

    def __init__(self):
        super().__init__()
        self.kelimeler = {}  # bolum id -> [(t, kelime)]

    def kelime(self, bolum, aranan, kacinci=1, ofset=0.0):
        """`aranan` ifadesinin (bir ya da birkaç kelime) bölümde `kacinci` kez söylendiği an.
        Ekleri yok sayar: "Pasinler" -> "Pasinler Ovası'nda" eşleşir."""
        parca = [sade(x) for x in aranan.split()]
        liste = self.kelimeler.get(bolum, [])
        bulunan = 0
        for i in range(len(liste)):
            if all(i + j < len(liste) and sade(liste[i + j][1]).startswith(p) for j, p in enumerate(parca)):
                bulunan += 1
                if bulunan == kacinci:
                    return liste[i][0] + ofset
        if bolum not in self:
            raise KeyError(f"bölüm yok: {bolum}")
        # bulunamazsa bölüm başına düş, ama uyar
        print(f"  uyarı: '{aranan}' {bolum} bölümünde bulunamadı; bölüm başı kullanıldı")
        return self[bolum][0] + ofset

    def tum_kelimeler(self):
        """Tüm videodaki (t, kelime, bolum) listesi — otomatik ipucu katmanı için."""
        out = []
        for b, l in self.kelimeler.items():
            out += [(t, k, b) for t, k in l]
        return sorted(out)
