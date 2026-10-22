"""Tek parça okunan seslendirmeyi cümlelere ayırır (cümle cümle zamanlama).

Gemini zaman damgası vermez. Sessizlikler bulunur, sonra N-1 cümle sınırı bütün olası seçimler
arasından dinamik programlamayla seçilir: her cümlenin süresi hece sayısıyla orantılı olmalı,
sınırlar ise tercihen uzun duraklamalara düşmeli. (Açgözlü eşleştirme tek bir hatada bütün
sonraki cümleleri kaydırıyordu; burada hata yayılmaz.)
"""
import math
import re
import subprocess

UNLU = set("aeıioöuüâîûAEIİOÖUÜÂÎÛ")


def hece(metin):
    return max(1, sum(1 for c in metin if c in UNLU))


def sessizlikler(ses, esik="-38dB", sure=0.12):
    cikti = subprocess.run(["ffmpeg", "-i", ses, "-af", f"silencedetect=noise={esik}:d={sure}", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    bas = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", cikti)]
    bit = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", cikti)]
    return list(zip(bas, bit))


def ses_suresi(ses):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", ses]).decode())


def hizala(ses, cumleler, duraklama_odulu=2.2):
    """[(t0, t1, cümle)] döndürür."""
    toplam = ses_suresi(ses)
    sess = sessizlikler(ses)
    # Gemini sesi başta kısa bir tık, sonda ~0,15 sn'lik cızırtıyla bitiyor: kenara yakın (0,5 sn) ilk/son
    # sessizliğin dışında kalan her şey konuşma sayılmaz ve kesilir.
    bas = sess[0][1] if sess and sess[0][0] < 0.5 else 0.0
    son = sess[-1][0] if sess and sess[-1][1] > toplam - 0.5 else toplam
    aday = [s for s in sess if s[0] > bas + 0.05 and s[1] < son - 0.05]
    n, m = len(cumleler), len(aday)
    if n == 1:
        return [(bas, son, cumleler[0])]
    if m < n - 1:
        raise RuntimeError("cümle sınırı için yeterli duraklama yok")
    heceler = [hece(c) for c in cumleler]
    # bitiş noktaları: aday sessizlikler + sesin sonu
    bitis = [(s[0], s[1], min(s[1] - s[0], 0.9)) for s in aday] + [(son, son, 0.9)]
    k = (son - bas) / sum(heceler)
    for _ in range(2):  # hızı (sn/hece) sonuçtan yeniden tahmin ederek iki tur
        INF = float("inf")
        f = [[INF] * (m + 1) for _ in range(n)]
        geri = [[-1] * (m + 1) for _ in range(n)]

        def maliyet(i, a, j):
            d = bitis[j][0] - a
            if d <= 0.15:
                return INF
            e = k * heceler[i]
            return 3.0 * math.log(d / e) ** 2 - duraklama_odulu * bitis[j][2]

        for j in range(m + 1):
            f[0][j] = maliyet(0, bas, j)
        for i in range(1, n):
            for j in range(i, m + 1):
                en, ei = INF, -1
                for p in range(i - 1, j):
                    if f[i - 1][p] == INF:
                        continue
                    c = f[i - 1][p] + maliyet(i, bitis[p][1], j)
                    if c < en:
                        en, ei = c, p
                f[i][j], geri[i][j] = en, ei
        # son cümle sesin sonunda biter
        yol = [m]
        for i in range(n - 1, 0, -1):
            yol.append(geri[i][yol[-1]])
        yol.reverse()
        sonuc, a = [], bas
        for i, j in enumerate(yol):
            sonuc.append((a, bitis[j][0], cumleler[i]))
            a = bitis[j][1]
        konusma = sum(t1 - t0 for t0, t1, _ in sonuc)
        k = konusma / sum(heceler)
    return sonuc
