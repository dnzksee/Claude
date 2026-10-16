"""Günlük üretim: kuyruk.txt'deki projeleri sırayla Kore sesiyle seslendirir ve render eder.

Gemini ücretsiz kotası günde birkaç istekle sınırlı olduğu için her gün çalıştırılır:
kota dolana kadar seslendirme yapar, bir videonun sesi tamamlandığında videoyu üretir,
artan kotayla sıradaki projeye geçer. Ses her zaman aynı model + aynı ses (Kore) ile üretilir.

Çıktı satırları:
  HAZIR <video yolu>      — tamamlanan video
  KOTA <proje>            — kota doldu, yarın devam
  BEKLEYEN <proje>        — kuyrukta sırada bekleyen proje
"""
import os
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
KUYRUK = os.path.join(KOK, "kuyruk.txt")


def main():
    projeler = [s.strip() for s in open(KUYRUK, encoding="utf-8")
                if s.strip() and not s.lstrip().startswith("#")]
    kota_doldu = False
    for proje in projeler:
        yol = os.path.join(KOK, "projeler", proje)
        son = os.path.join(yol, "cikti", f"{proje}_kore.mp4")
        if os.path.exists(son):
            continue
        if kota_doldu:
            print(f"BEKLEYEN {proje}")
            continue
        print(f"--- {proje}", flush=True)
        kod = subprocess.call([sys.executable, os.path.join(KOK, "uret.py"), yol, "--motor", "gemini",
                               "--ses", "Kore"], cwd=KOK)
        if kod == 0:
            shutil.move(os.path.join(yol, "cikti", "video.mp4"), son)
            print(f"HAZIR {son}", flush=True)
        elif kod == 2:
            print(f"KOTA {proje}", flush=True)
            kota_doldu = True
        else:
            print(f"HATA {proje} (çıkış kodu {kod})", flush=True)
            kota_doldu = True  # hata varken sıradakilere geçme


if __name__ == "__main__":
    main()
