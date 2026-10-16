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
from motor.seslendirme import gemini_seslendir, edge_seslendir, cumlelere_bol  # noqa: E402

BOSLUK = 0.8       # YouTube bölümleri arası ek sessizlik (sn)
PARCA_BOSLUK = 0.15  # aynı bölümdeki parçalar arası ek sessizlik
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


def _parcala(mp3, cumleler, sayilar):
    """Bölüm sesini parçalara ayır. sayilar: her parçadaki cümle sayısı.
    Döndürür: [(parca_mp3, sure, [(t0, t1, cumle), ...]), ...] (zamanlar parçaya göre)."""
    toplam = _sure(mp3)
    if len(cumleler) != sum(sayilar):  # güvenlik: eşleşmezse orantılı dağıt
        print(f"  uyarı: {os.path.basename(mp3)} cümle sayısı {len(cumleler)} != {sum(sayilar)}")
    kesimler, i = [0.0], 0
    for n in sayilar[:-1]:
        i += n
        if 0 < i < len(cumleler):
            kesimler.append((cumleler[i - 1][1] + cumleler[i][0]) / 2)
        else:
            kesimler.append(toplam * i / max(sum(sayilar), 1))
    kesimler.append(toplam)
    sonuc = []
    for k in range(len(sayilar)):
        k0, k1 = kesimler[k], kesimler[k + 1]
        pmp3 = mp3.replace(".mp3", f"_p{k:02d}.mp3")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ss", f"{k0:.3f}",
                               "-to", f"{k1:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", pmp3])
        alt = [(max(0, c0 - k0), min(k1, c1) - k0, m) for c0, c1, m in cumleler if k0 - 0.05 <= c0 < k1]
        sonuc.append((pmp3, _sure(pmp3), alt))
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
    ap.add_argument("--sadece-kareler", action="store_true",
                    help="video üretme; yalnızca --onizleme karelerini (veya her parçanın ortasını) PNG kaydet")
    a = ap.parse_args()
    a.ses = a.ses or ("Kore" if a.motor == "gemini" else "tr-TR-EmelNeural")

    proje = os.path.abspath(a.proje)
    cikti = os.path.join(proje, "cikti")
    os.makedirs(cikti, exist_ok=True)
    spec = importlib.util.spec_from_file_location("senaryo", os.path.join(proje, "senaryo.py"))
    sen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sen)

    # 1) Seslendirme: her "bolum" (YouTube bölümü) tek seferde seslendirilir, sonra
    #    cümle aralarındaki sessizliklerden animasyon parçalarına bölünür.
    gruplar = []
    for b in sen.BOLUMLER:
        if b.get("bolum") or not gruplar:
            gruplar.append([])
        gruplar[-1].append(b)

    T, altyazilar, ses_parcalari = {}, [], []
    t = GIRIS_PAYI
    for gi, grup in enumerate(gruplar):
        metin = " ".join(b["metin"].strip() for b in grup)
        if a.sessiz:
            parcalar = []
            for b in grup:
                d = len(b["metin"]) / 12.0
                parcalar.append((None, d, [(0, d, b["metin"])]))
        else:
            mp3 = os.path.join(cikti, f"g{gi:02d}_{grup[0]['id']}.mp3")
            meta, anahtar = mp3 + ".json", a.motor + a.ses + a.hiz + metin
            if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0 and os.path.exists(meta)
                    and json.load(open(meta, encoding="utf-8"))["anahtar"] == anahtar):
                print(f"Seslendiriliyor ({a.motor}/{a.ses}) [{gi + 1}/{len(gruplar)}]: "
                      f"{grup[0].get('bolum', grup[0]['id'])} ({len(metin)} karakter)", flush=True)
                if a.motor == "gemini":
                    zam = gemini_seslendir(metin, mp3, a.ses)
                else:
                    zam = edge_seslendir(metin, mp3, a.ses, a.hiz)
                json.dump({"anahtar": anahtar, "altyazi": zam}, open(meta, "w", encoding="utf-8"),
                          ensure_ascii=False)
            cumleler = [tuple(x) for x in json.load(open(meta, encoding="utf-8"))["altyazi"]]
            parcalar = _parcala(mp3, cumleler, [len(cumlelere_bol(b["metin"])) for b in grup])
        for b, (pmp3, d, palt) in zip(grup, parcalar):
            if pmp3:
                ses_parcalari.append((t, pmp3))
            ek = b.get("ek_sure", 0)  # anlatım bittikten sonra animasyonun sürmesi için
            T[b["id"]] = (t, t + d + ek)
            altyazilar += [(t + x0, t + x1, m) for x0, x1, m in _cumle_bol(palt)]
            t += d + ek + PARCA_BOSLUK
        t += BOSLUK
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
    video = Video(sen.arka_plan() if hasattr(sen, "arka_plan") else None, fps=a.fps)
    sen.kur(video, T)
    if a.altyazi_gom:
        video.ekle(AltYazi(altyazilar))
    if a.sadece_kareler:
        import cairo
        from motor.sahne import G as _G, Y as _Y
        yuzey = cairo.ImageSurface(cairo.FORMAT_ARGB32, _G, _Y)
        cr = cairo.Context(yuzey)
        zamanlar = [float(x) for x in a.onizleme.split(",") if x] or \
            [(T[b["id"]][0] + T[b["id"]][1]) / 2 for b in sen.BOLUMLER]
        for i, zt in enumerate(zamanlar):
            cr.set_source_rgb(0, 0, 0)
            cr.paint()
            video.kare(cr, zt)
            yuzey.write_to_png(os.path.join(cikti, f"onizleme_{i:02d}_{zt:07.1f}.png"))
        print(f"{len(zamanlar)} kare kaydedildi, toplam süre {toplam / 60:.1f} dk")
        return
    mp4 = os.path.join(cikti, "video.mp4")
    print(f"Render: {toplam:.1f} sn -> {mp4}")
    onizleme = [float(x) for x in a.onizleme.split(",") if x]
    video.kaydet(mp4, toplam, ses=ses_yolu, onizleme_kareleri=onizleme)
    print("Bitti:", mp4)


if __name__ == "__main__":
    main()
