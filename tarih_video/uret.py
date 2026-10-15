"""Bir savaş projesini baştan sona üretir: seslendirme -> altyazı -> animasyon -> MP4.

Kullanım:
    python3 uret.py projeler/malazgirt            # tam video
    python3 uret.py projeler/malazgirt --sessiz   # TTS olmadan (tahmini sürelerle) hızlı deneme

Proje klasöründe `senaryo.py` bulunur; içinde:
    BOLUMLER = [{"id": "giris", "metin": "..."}, ...]
    def kur(video, T): ...   # T["giris"] -> (baslangic, bitis) saniye
    def arka_plan(): ...     # harita.arka_plan_uret(...) döndürür
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor.sahne import Video, AltYazi  # noqa: E402
from motor.seslendirme import gemini_seslendir, edge_seslendir  # noqa: E402

BOSLUK = 0.7       # bölümler arası sessizlik (sn)
GIRIS_PAYI = 1.0   # video başındaki sessizlik


def _srt_zaman(s):
    s = max(0, s)
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(s * 1000 % 1000):03d}"


def _sure(yol):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", yol]).strip())


def _cumle_bol(satirlar, azami=65):
    """Uzun cümleleri virgül noktalarından bölüp süreyi karakter oranında paylaştır."""
    sonuc = []
    for t0, t1, m in satirlar:
        if len(m) <= azami:
            sonuc.append((t0, t1, m))
            continue
        parcalar, mevcut = [], ""
        for p in re.split(r"(?<=[,;:])\s+", m):
            if mevcut and len(mevcut) + len(p) > azami:
                parcalar.append(mevcut)
                mevcut = p
            else:
                mevcut = (mevcut + " " + p).strip()
        parcalar.append(mevcut)
        toplam = sum(len(p) for p in parcalar)
        t = t0
        for p in parcalar:
            d = (t1 - t0) * len(p) / toplam
            sonuc.append((t, t + d, p))
            t += d
    return sonuc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proje")
    ap.add_argument("--motor", choices=["gemini", "edge"],
                    default="gemini" if os.environ.get("GEMINI_API_KEY") else "edge",
                    help="seslendirme motoru (gemini = Google, edge = Microsoft)")
    ap.add_argument("--ses", default=None, help="gemini: Kore, Aoede, Charon... | edge: tr-TR-EmelNeural, tr-TR-AhmetNeural")
    ap.add_argument("--hiz", default="-4%", help="yalnızca edge: konuşma hızı, örn. -4%%, +0%%")
    ap.add_argument("--sessiz", action="store_true", help="TTS kullanma, süreleri metinden tahmin et")
    ap.add_argument("--altyazi-gom", action="store_true", default=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--onizleme", default="", help="virgülle ayrılmış saniyeler: PNG kare çıkar")
    a = ap.parse_args()
    a.ses = a.ses or ("Kore" if a.motor == "gemini" else "tr-TR-EmelNeural")

    proje = os.path.abspath(a.proje)
    cikti = os.path.join(proje, "cikti")
    os.makedirs(cikti, exist_ok=True)
    spec = importlib.util.spec_from_file_location("senaryo", os.path.join(proje, "senaryo.py"))
    sen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sen)

    # 1) Seslendirme ve zamanlama
    T, altyazilar, ses_parcalari = {}, [], []
    t = GIRIS_PAYI
    for i, b in enumerate(sen.BOLUMLER):
        mp3 = os.path.join(cikti, f"{i:02d}_{b['id']}.mp3")
        if a.sessiz:
            d = len(b["metin"]) / 14.0  # ~14 karakter/sn
            parca_alt = [(0, d, b["metin"])]
        else:
            # metin/ses değişmediyse önceki seslendirmeyi yeniden kullan
            meta, anahtar = mp3 + ".json", a.motor + a.ses + a.hiz + b["metin"]
            if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0 and os.path.exists(meta)
                    and json.load(open(meta, encoding="utf-8"))["anahtar"] == anahtar):
                print(f"Seslendiriliyor ({a.motor}/{a.ses}): {b['id']}", flush=True)
                if a.motor == "gemini":
                    zam = gemini_seslendir(b["metin"], mp3, a.ses)
                else:
                    zam = edge_seslendir(b["metin"], mp3, a.ses, a.hiz)
                json.dump({"anahtar": anahtar, "altyazi": zam}, open(meta, "w", encoding="utf-8"),
                          ensure_ascii=False)
            d = _sure(mp3)
            parca_alt = [tuple(x) for x in json.load(open(meta, encoding="utf-8"))["altyazi"]]
            ses_parcalari.append((t, mp3))
        ek = b.get("ek_sure", 0)  # anlatım bittikten sonra animasyonun sürmesi için
        T[b["id"]] = (t, t + d + ek)
        altyazilar += [(t + x0, t + x1, m) for x0, x1, m in _cumle_bol(parca_alt)]
        t += d + ek + BOSLUK
    toplam = t + 1.5

    # 2) Tam ses izi
    ses_yolu = None
    if ses_parcalari:
        ses_yolu = os.path.join(cikti, "seslendirme.m4a")
        girdiler, filtre = [], []
        for j, (bas, mp3) in enumerate(ses_parcalari):
            girdiler += ["-i", mp3]
            filtre.append(f"[{j}]adelay={int(bas * 1000)}:all=1[s{j}]")
        filtre.append("".join(f"[s{j}]" for j in range(len(ses_parcalari)))
                      + f"amix=inputs={len(ses_parcalari)}:normalize=0,apad=whole_dur={toplam}[cik]")
        fon = getattr(sen, "FON_MUZIGI", None)
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *girdiler,
                               "-filter_complex", ";".join(filtre), "-map", "[cik]",
                               "-t", str(toplam), "-c:a", "aac", "-b:a", "192k", ses_yolu])
        if fon and os.path.exists(os.path.join(proje, fon)):
            karisik = os.path.join(cikti, "ses_muzikli.m4a")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", ses_yolu,
                                   "-stream_loop", "-1", "-i", os.path.join(proje, fon),
                                   "-filter_complex", "[1]volume=0.12[m];[0][m]amix=inputs=2:duration=first:normalize=0[c]",
                                   "-map", "[c]", "-c:a", "aac", "-b:a", "192k", karisik])
            ses_yolu = karisik

    # 3) SRT (YouTube'a ayrı yüklemek için)
    with open(os.path.join(cikti, "altyazi.srt"), "w", encoding="utf-8") as f:
        for n, (x0, x1, m) in enumerate(altyazilar, 1):
            f.write(f"{n}\n{_srt_zaman(x0)} --> {_srt_zaman(x1)}\n{m}\n\n")
    json.dump({k: list(v) for k, v in T.items()}, open(os.path.join(cikti, "zamanlama.json"), "w"), indent=1)

    # YouTube bölüm (chapter) listesi
    with open(os.path.join(cikti, "youtube_bolumler.txt"), "w", encoding="utf-8") as f:
        for b in sen.BOLUMLER:
            if b.get("bolum"):
                s = 0 if b is sen.BOLUMLER[0] else int(T[b["id"]][0])
                f.write(f"{s // 60}:{s % 60:02d} {b['bolum']}\n")

    # 4) Animasyon
    video = Video(sen.arka_plan(), fps=a.fps)
    sen.kur(video, T)
    if a.altyazi_gom:
        video.ekle(AltYazi(altyazilar))
    mp4 = os.path.join(cikti, "video.mp4")
    print(f"Render: {toplam:.1f} sn -> {mp4}")
    onizleme = [float(x) for x in a.onizleme.split(",") if x]
    video.kaydet(mp4, toplam, ses=ses_yolu, onizleme_kareleri=onizleme)
    print("Bitti:", mp4)


if __name__ == "__main__":
    main()
