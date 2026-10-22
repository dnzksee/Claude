"""Bir konunun bütün yayın paketini üretir (standart iş akışı).

    python3 paket.py malazgirt            # konular/malazgirt.py + konular/malazgirt_short.py
    python3 paket.py malazgirt --sessiz   # seslendirmesiz hızlı kontrol (720p)

Üretilenler (cikti/<konu>/ ve cikti/<konu>_short/):
  1. Uzun çizgi film (1920×1080) + gönderim için ~90 sn'lik parçalar
  2. Short (1080×1920)
  3. Her ikisi için youtube.md: başlık, açıklama (bölüm zaman damgalarıyla), etiketler
  4. altyazi.srt
Short konusu yoksa bunu görev olarak hatırlatır (konular/<konu>_short.py yazılmalı).
"""
import os
import subprocess
import sys

KOK = os.path.dirname(os.path.abspath(__file__))


def calistir(konu_yolu, sessiz):
    komut = [sys.executable, os.path.join(KOK, "uret.py"), konu_yolu]
    if sessiz:
        komut += ["--motor", "sessiz", "--olcek", "1.0"]
    print(">>", " ".join(os.path.relpath(k, KOK) if k.startswith(KOK) else k for k in komut[1:]), flush=True)
    return subprocess.run(komut, cwd=KOK).returncode


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ad = sys.argv[1].replace(".py", "").replace("konular/", "")
    sessiz = "--sessiz" in sys.argv
    eksik, sonuc = [], []
    uzun = os.path.join(KOK, "konular", f"{ad}.py")
    short = os.path.join(KOK, "konular", f"{ad}_short.py")
    for yol, tur in ((uzun, "uzun video"), (short, "Short")):
        if not os.path.exists(yol):
            eksik.append(f"{tur}: {os.path.relpath(yol, KOK)} yazılmalı")
            continue
        kod = calistir(yol, sessiz)
        if kod != 0:
            print(f"!! {tur} üretilemedi (çıkış kodu {kod}); seslendirme kotası dolduysa yarın aynı komutla devam edin.")
            sys.exit(kod)
        hedef = os.path.join(KOK, "cikti", os.path.splitext(os.path.basename(yol))[0])
        sonuc.append(hedef)
    if os.path.isdir(os.path.join(KOK, "cikti", ad)) and not sessiz:
        mp4 = os.path.join(KOK, "cikti", ad, f"{ad}.mp4")
        if os.path.exists(mp4):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c", "copy", "-f", "segment",
                            "-segment_time", "90", "-reset_timestamps", "1",
                            os.path.join(KOK, "cikti", ad, f"{ad}_parca%d.mp4")], check=True)
    print("\n=== YAYIN PAKETİ ===")
    for h in sonuc:
        for f in sorted(os.listdir(h)):
            if f.endswith((".mp4", ".md", ".srt")):
                print("  ", os.path.relpath(os.path.join(h, f), KOK))
    for e in eksik:
        print("  GÖREV:", e)


if __name__ == "__main__":
    main()
