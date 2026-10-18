"""Günlük üretim: kuyruk.txt'deki projeleri sırayla ses.txt'deki anlatıcı sesiyle seslendirir ve render eder.

Gemini ücretsiz kotası günde birkaç istekle sınırlı olduğu için her gün çalıştırılır:
kota dolana kadar seslendirme yapar, bir videonun sesi tamamlandığında videoyu üretir,
artan kotayla sıradaki projeye geçer. Ses her zaman aynı model + ses.txt'deki aynı ses ile üretilir.

Çıktı satırları:
  ORNEK <mp3 yolu>        — ses seçimi için örnek (ses.txt yokken)
  SES_BEKLENIYOR          — örnekler hazır, kullanıcının ses seçimi bekleniyor
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
SES_DOSYASI = os.path.join(KOK, "ses.txt")  # seçilen anlatıcı sesi (tek satır, ör. "Charon")
ORNEK_KLASORU = os.path.join(KOK, "ses_ornekleri")
ORNEK_SESLER = ["Charon", "Orus", "Algenib", "Iapetus", "Kore"]
ORNEK_METIN = ("26 Ağustos 1071, bir Cuma günüydü. Rivayete göre Alparslan, o sabah askerleriyle birlikte "
               "Cuma namazını kıldı. Sonra beyaz bir elbise giydi ve atının kuyruğunu kendi eliyle bağladı. "
               "Ardından askerlerine döndü ve şöyle seslendi. Eğer şehit düşersem, bu beyaz elbise kefenim olsun.")


def ses_ornekleri():
    """Ses seçimi için aynı paragrafı aday seslerle seslendirir. Kota dolarsa False döner."""
    sys.path.insert(0, KOK)
    from motor.seslendirme import gemini_seslendir
    os.makedirs(ORNEK_KLASORU, exist_ok=True)
    for ses in ORNEK_SESLER:
        hedef = os.path.join(ORNEK_KLASORU, f"ornek_{ses}.mp3")
        if os.path.exists(hedef):
            continue
        try:
            gemini_seslendir(ORNEK_METIN, hedef, ses)
        except RuntimeError as hata:
            print(f"KOTA ses_ornekleri ({hata})", flush=True)
            return False
        print(f"ORNEK {hedef}", flush=True)
    return True


def main():
    if not os.path.exists(SES_DOSYASI):
        # Ses henüz seçilmedi: önce örnekleri üret, projeler seçimi bekler.
        if ses_ornekleri():
            print("SES_BEKLENIYOR örnekler hazır; kullanıcının seçimi ses.txt'ye yazılmalı", flush=True)
        return
    ses = open(SES_DOSYASI, encoding="utf-8").read().strip()
    projeler = [s.strip() for s in open(KUYRUK, encoding="utf-8")
                if s.strip() and not s.lstrip().startswith("#")]
    kota_doldu = False
    for proje in projeler:
        yol = os.path.join(KOK, "projeler", proje)
        son = os.path.join(yol, "cikti", f"{proje}_{ses.lower()}.mp4")
        if os.path.exists(son):
            continue
        if kota_doldu:
            print(f"BEKLEYEN {proje}")
            continue
        print(f"--- {proje}", flush=True)
        liste = os.path.join(yol, "gorseller.txt")
        if os.path.exists(liste):  # eksik kamu malı görselleri bir kez dene (engelliyse hemen geç)
            subprocess.call([sys.executable, os.path.join(KOK, "araclar", "commons_indir.py"), liste, "--hizli"],
                            cwd=KOK)
        kod = subprocess.call([sys.executable, os.path.join(KOK, "uret.py"), yol, "--motor", "gemini",
                               "--ses", ses], cwd=KOK)
        if kod == 0:
            shutil.move(os.path.join(yol, "cikti", "video.mp4"), son)
            # İndirmesi kolay, ~yarı boyutlu kopya (animasyon olduğu için kalite kaybı fark edilmez)
            kucuk = son.replace(".mp4", "_kucuk.mp4")
            subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", son, "-c:v", "libx264",
                             "-preset", "slow", "-crf", "30", "-tune", "animation", "-pix_fmt", "yuv420p",
                             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", kucuk])
            print(f"HAZIR {kucuk}", flush=True)
        elif kod == 2:
            print(f"KOTA {proje}", flush=True)
            kota_doldu = True
        else:
            print(f"HATA {proje} (çıkış kodu {kod})", flush=True)
            kota_doldu = True  # hata varken sıradakilere geçme


if __name__ == "__main__":
    main()
