"""Tarih kanalı — 2B çizgi film belgesel (explainer) üretimi.

Kullanım:
    python3 uret.py konular/malazgirt.py                  # seslendir + müzik + efekt + video
    python3 uret.py konular/malazgirt.py --motor sessiz   # seslendirme olmadan taslak (süre tahmini)
    python3 uret.py konular/malazgirt.py --onizleme 5,32,70 --sadece-kareler

Akış: metin -> cümle cümle seslendirme (Gemini, tarih kanalının anlatıcısı) -> her cümle kendi zamanına
yerleştirilir -> sahneler bu zamanlara göre kurulur -> müzik (konuşma altında kısılır) +
efektler + seslendirme miksajı -> 1280×720, 24 fps MP4 + SRT altyazı.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

import numpy as np

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)

def konu_yukle(yol):
    spec = importlib.util.spec_from_file_location("konu", yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _on_ayar():
    """Motor yüklenmeden önce: konunun tuval biçimi (yatay/dikey) ve çıktı ölçeği ortama yazılır;
    motor modülleri G, Y, OLCEK değerlerini yüklenirken okur."""
    konumlu = [x for x in sys.argv[1:] if not x.startswith("-")]
    if konumlu and os.path.exists(konumlu[0]):
        os.environ.setdefault("CIZGI_FORMAT", getattr(konu_yukle(konumlu[0]), "FORMAT", "yatay"))
    if "--olcek" in sys.argv:
        os.environ["CIZGI_OLCEK"] = sys.argv[sys.argv.index("--olcek") + 1]


_on_ayar()
from motor import ses as S  # noqa: E402
from motor.gecisler import SURELER, SESLER  # noqa: E402
from motor.kartlar import AcilisKarti, KapanisKarti, BolumEtiketi, Altyazi, Filigran, KANAL  # noqa: E402
from motor.video import Sahne, Video  # noqa: E402


def _tarih_seslendirme():
    """Seslendirme kodu tarih projesinin ana hattıyla ortaktır (aynı Gemini ayarları, doğrulama)."""
    yol = os.path.join(os.path.dirname(KOK), "motor", "seslendirme.py")
    spec = importlib.util.spec_from_file_location("ortak_seslendirme", yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def anlatici_sesi():
    """Kanalın anlatıcı sesi: tarih_video/ses.txt (bütün tarih videolarında aynı ses: Iapetus)."""
    yol = os.path.join(os.path.dirname(KOK), "ses.txt")
    with open(yol, encoding="utf-8") as f:
        return [s.strip() for s in f if s.strip() and not s.startswith("#")][0]


# ---------------------------------------------------------------- seslendirme
def _tam_dogrula(ortak, mp3, metin):
    """Sesin tamamını yazıya döktürüp metinle karşılaştırır. Gemini bazen okumayı yarıda kesip
    baştan yeniden başlıyor ya da cümle atlıyor; bu, süre ve benzerlik kontrolüyle yakalanır.
    True/False; doğrulama servisine ulaşılamazsa None."""
    import base64
    import difflib
    import urllib.request
    from motor.hizalama import hece, ses_suresi
    sure = ses_suresi(mp3)
    oran = sure / hece(metin)
    if not 0.11 < oran < 0.27:  # normal okuma ≈ 0.15-0.2 sn/hece; baştan yeniden okumada çok uzar
        print(f"  süre şüpheli: {sure:.1f} sn, hece başına {oran:.3f} sn", flush=True)
        return False
    kes = mp3 + ".dogrula.mp3"
    import subprocess
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", "16000", kes])
    govde = json.dumps({"contents": [{"parts": [
        {"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(open(kes, "rb").read()).decode()}},
        {"text": "Bu Türkçe ses kaydını kelimesi kelimesine yazıya dök. Sayıları yazıyla yaz. Sadece metni yaz."}]}]}).encode()
    os.remove(kes)
    duyulan = None
    for model in ortak.DOGRULAMA_MODELLERI:
        try:
            istek = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model.strip()}:generateContent",
                govde, {"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            with urllib.request.urlopen(istek, timeout=180) as y:
                duyulan = " ".join(p.get("text", "") for p in json.load(y)["candidates"][0]["content"]["parts"])
            if duyulan.strip():
                break
        except Exception:
            continue
    if not duyulan:
        print("  uyarı: tam doğrulama yapılamadı", flush=True)
        return None
    # kelime düzeyinde (karakter düzeyinde uzun metinlerde difflib'in otomatik "junk" sezgisi yanıltıyor)
    # şapkalı harfler korunur, kesme işareti kelimeyi bölmez (Kroniknâme'de = kroniknamede)
    duz = str.maketrans({"â": "a", "î": "i", "û": "u", "Â": "A", "Î": "I", "Û": "U", "'": "", "’": ""})
    benzerlik = difflib.SequenceMatcher(None, ortak._sade(duyulan.translate(duz)), ortak._sade(metin.translate(duz)),
                                        autojunk=False).ratio()
    if benzerlik < 0.8:
        print(f"  ses metinle uyuşmuyor (benzerlik {benzerlik:.2f}): {duyulan[:100]!r}...", flush=True)
        return False
    return True


def seslendir(birimler, motor, ses, klasor):
    """birimler: [[cümle, ...], ...] (açılış, sahneler, kapanış). Her cümlenin ses parçasını döndürür:
    [[np.array, ...], ...]. Her birim (sahne) tek istekte okunur: sahne içinde ses tınısı ve
    tonlama bütün kalır, uzun metinlerde görülen "baştan yeniden okuma" hatası olasılığı azalır.
    Ses sonra sessizliklerden cümle cümle kesilir (motor/hizalama.py)."""
    from motor.hizalama import hizala
    os.makedirs(klasor, exist_ok=True)
    if motor == "sessiz":
        return [[np.zeros(int(S.SR * max(1.2, len(c) * 0.068))) for c in b] for b in birimler]
    ortak = _tarih_seslendirme()
    sonuc = []
    for b in birimler:
        metin = " ".join(b)
        anahtar = hashlib.sha1(f"{motor}|{ses}|{ortak.SURUM}|{ortak.GEMINI_MODEL}|{metin}".encode()).hexdigest()[:12]
        mp3 = os.path.join(klasor, f"vo_{anahtar}.mp3")
        if not os.path.exists(mp3):
            print(f"  seslendiriliyor ({len(metin)} karakter, {len(b)} cümle)...", flush=True)
            gecici = mp3 + ".tmp.mp3"
            for deneme in range(3):
                if motor == "gemini":
                    ortak.gemini_seslendir(metin, gecici, ses)
                    if _tam_dogrula(ortak, gecici, metin) is False:
                        print("  yeniden deneniyor", flush=True)
                        continue
                else:
                    ortak.edge_seslendir(metin, gecici, ses)
                break
            else:
                raise RuntimeError("seslendirme 3 denemede de doğrulanamadı")
            os.replace(gecici, mp3)
        if ANLATIM_HIZI != 1.0:  # perdeyi koruyarak tempo (aynı ses, daha akıcı anlatım)
            hizli = mp3[:-4] + f"_x{ANLATIM_HIZI:.2f}.wav"
            if not os.path.exists(hizli):
                import subprocess
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", f"atempo={ANLATIM_HIZI}",
                                "-ar", str(S.SR), "-ac", "1", hizli], check=True)
            kaynak = hizli
        else:
            kaynak = mp3
        zam = hizala(kaynak, b)
        dalga = S.ses_oku(kaynak)
        parcalar = []
        for t0, t1, _ in zam:
            a, z = max(0, int((t0 - 0.04) * S.SR)), min(len(dalga), int((t1 + 0.1) * S.SR))
            parca = _duraklama_kisalt(dalga[a:z].copy())
            n = min(len(parca) // 4, int(0.02 * S.SR))
            if n:
                parca[:n] *= np.linspace(0, 1, n)
                parca[-n:] *= np.linspace(1, 0, n)
            parcalar.append(parca)
        sonuc.append(parcalar)
    return sonuc


# ---------------------------------------------------------------- zaman çizelgesi
BOSLUK = 0.2         # aynı sahnedeki cümleler arası (akıcı belgesel temposu)
ONCE = {"acilis": 1.6, "sahne": 0.9, "kapanis": 0.8}
SONRA = {"acilis": 0.7, "sahne": 0.7, "kapanis": 3.0}
ANLATIM_HIZI = 1.08  # seslendirme temposu (perde korunur)
DURAKLAMA_AZAMI = 0.3  # cümle içindeki duraklamaların en uzun hâli (sn)


def _duraklama_kisalt(parca, esik_db=-38.0):
    """Cümle içindeki uzun sessizlikleri DURAKLAMA_AZAMI'ya indirir (kısa yumuşak geçişle)."""
    pen = int(0.01 * S.SR)
    if len(parca) < pen * 10:
        return parca
    n = len(parca) // pen
    rms = np.sqrt((parca[:n * pen].reshape(n, pen) ** 2).mean(axis=1))
    esik = max(np.abs(parca).max(), 1e-6) * 10 ** (esik_db / 20)
    sessiz = rms < esik
    azami = int(DURAKLAMA_AZAMI / 0.01)
    parcalar, i, son = [], 0, 0
    while i < n:
        if sessiz[i]:
            j = i
            while j < n and sessiz[j]:
                j += 1
            if j - i > azami and i > 0 and j < n:  # baştaki/sondaki sessizliğe dokunma
                kes0, kes1 = (i + azami // 2) * pen, (j - azami // 2) * pen
                parcalar.append(parca[son:kes0])
                son = kes1
            i = j
        else:
            i += 1
    parcalar.append(parca[son:])
    sonuc = parcalar[0]
    x = int(0.01 * S.SR)
    for p in parcalar[1:]:  # 10 ms çapraz geçiş: tık sesi olmasın
        if len(sonuc) > x and len(p) > x:
            karisim = sonuc[-x:] * np.linspace(1, 0, x) + p[:x] * np.linspace(0, 1, x)
            sonuc = np.concatenate([sonuc[:-x], karisim, p[x:]])
        else:
            sonuc = np.concatenate([sonuc, p])
    return sonuc


def yerlestir(birimler, parcalar, turler, aralar=None):
    """Her birimin [t0, t1] aralığı ve cümle zamanları; bir de tek parça seslendirme dizisi.
    aralar: her birim için {cümle_no: ek_saniye} — anlatıcının sustuğu aksiyon araları (seslendirmeyi değiştirmez)."""
    aralar = aralar or [{}] * len(birimler)
    t = 0.0
    araliklar, cumle_zaman, konusmalar = [], [], []
    yerlesim = []
    for b, pp, tur, ara in zip(birimler, parcalar, turler, aralar):
        bas = t
        t += ONCE[tur]
        cz = []
        for ci, (c, p) in enumerate(zip(b, pp)):
            sure = len(p) / S.SR
            cz.append((t, t + sure, c))
            yerlesim.append((t, p))
            konusmalar.append((t, t + sure))
            t += sure + BOSLUK + ara.get(ci, 0.0)
        t += SONRA[tur] - BOSLUK
        araliklar.append((bas, t))
        cumle_zaman.append(cz)
    vo = np.zeros(int((t + 1) * S.SR))
    for t0, p in yerlesim:
        a = int(t0 * S.SR)
        vo[a:a + len(p)] += p
    return araliklar, cumle_zaman, konusmalar, vo


def altyazi_satirlari(cumle_zaman, azami=78):
    """Uzun cümleleri virgül/noktalı virgülden bölüp süreyi karakter oranıyla paylaştırır."""
    satirlar = []
    for cz in cumle_zaman:
        for t0, t1, c in cz:
            parcalar = [c]
            if len(c) > azami:
                parcalar = [p.strip() for p in re.split(r"(?<=[,;:])\s+", c) if p.strip()]
                birlesik, s = [], ""
                for p in parcalar:
                    if s and len(s) + len(p) + 1 > azami:
                        birlesik.append(s)
                        s = p
                    else:
                        s = (s + " " + p).strip()
                if s:
                    birlesik.append(s)
                parcalar = birlesik
            toplam = sum(len(p) for p in parcalar)
            t = t0
            for p in parcalar:
                d = (t1 - t0) * len(p) / toplam
                satirlar.append((t, t + d + (0.25 if p is parcalar[-1] else 0), p))
                t += d
    return satirlar


def _srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


# ---------------------------------------------------------------- ana akış
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("konu", help="konular/<ad>.py")
    ap.add_argument("--motor", choices=["gemini", "edge", "sessiz"], default=None,
                    help="varsayılan: GEMINI_API_KEY varsa gemini, yoksa edge")
    ap.add_argument("--ses", default=None, help="varsayılan: ses.txt (kanal anlatıcısı)")
    ap.add_argument("--onizleme", default="", help="virgülle saniyeler: PNG kare")
    ap.add_argument("--sadece-kareler", action="store_true")
    ap.add_argument("--olcek", type=float, default=1.5, help="1.5: 1080p (varsayılan), 1.0: 720p hızlı taslak")
    a = ap.parse_args()

    konu = konu_yukle(a.konu)
    globals().update(getattr(konu, "TEMPO", {}))  # Shorts gibi hızlı tempolu konular için BOSLUK/ONCE/SONRA
    ad = os.path.splitext(os.path.basename(a.konu))[0]
    cikti = os.path.join(KOK, "cikti", ad)
    os.makedirs(cikti, exist_ok=True)
    motor = a.motor or ("gemini" if os.environ.get("GEMINI_API_KEY") else "edge")
    ses = a.ses or (anlatici_sesi() if motor == "gemini" else "tr-TR-EmelNeural")
    print(f"Konu: {konu.BASLIK} | seslendirme: {motor} / {ses}")

    birimler = [konu.ACILIS] + [sh["metin"] for sh in konu.SAHNELER] + [konu.KAPANIS]
    turler = ["acilis"] + ["sahne"] * len(konu.SAHNELER) + ["kapanis"]
    parcalar = seslendir(birimler, motor, ses, os.path.join(cikti, "ses"))
    aralar = [{}] + [sh.get("aralar", {}) for sh in konu.SAHNELER] + [{}]
    araliklar, cz, konusmalar, vo = yerlestir(birimler, parcalar, turler, aralar)

    tasarimlar = getattr(konu, "KARAKTERLER", {})
    video = Video(fps=24)
    # açılış kartı
    t0, t1 = araliklar[0]
    ac = video.ekle(Sahne(0, "", "duz", t0, t1, cz[0], gecis="kes", zemin=False, bulanik=1,
                          arkaplan_p=getattr(konu, "KART_RENK", {"ust": (0.2, 0.45, 0.9), "alt": (0.1, 0.2, 0.55)})))
    ac.ekle(AcilisKarti(konu.BASLIK, konu.ALT_BASLIK, 0.25, t1 - 0.3, kanal=getattr(konu, "KANAL", KANAL),
                        logo=getattr(konu, "LOGO", "kilic")))
    ac.sfx("pop", 0.75, 0.6)
    if hasattr(konu, "acilis"):
        konu.acilis(ac)
    # içerik sahneleri
    for i, sh in enumerate(konu.SAHNELER):
        t0, t1 = araliklar[i + 1]
        s = video.ekle(Sahne(i + 1, sh["baslik"], sh.get("arkaplan", "oda"), t0, t1, cz[i + 1],
                             gecis=sh.get("gecis", "whip"), arkaplan_p=sh.get("arkaplan_p"), tasarimlar=tasarimlar,
                             bulanik=sh.get("bulanik", 1.0 if sh.get("arkaplan") in ("harita", "ova") else 7.0),
                             paralaks=1.0 if sh.get("arkaplan") in ("harita", "ova") else 0.35,
                             zemin=sh.get("zemin", sh.get("arkaplan") not in ("harita", "ova"))))
        if getattr(konu, "BOLUM_ETIKETI", True):
            s.ekle(BolumEtiketi(i + 1, sh["baslik"], t0 + 0.15, t1 + 0.6))
        sh["kurgu"](s)
    # kapanış kartı
    t0, t1 = araliklar[-1]
    kp = video.ekle(Sahne(len(konu.SAHNELER) + 1, "", "duz", t0, t1, cz[-1], gecis=getattr(konu, "KAPANIS_GECIS", "iris"),
                          zemin=False, bulanik=1,
                          arkaplan_p=getattr(konu, "KART_RENK", {"ust": (0.2, 0.45, 0.9), "alt": (0.1, 0.2, 0.55)})))
    kp.ekle(KapanisKarti(getattr(konu, "KAPANIS_YAZI", konu.BASLIK), "ABONE OL", t0 + 0.3, t1,
                         logo=getattr(konu, "LOGO", "kilic"), kanal=getattr(konu, "KANAL", KANAL)))
    video.ust.append(Filigran(araliklar[1][0] + 0.5, araliklar[-1][0], kanal=getattr(konu, "KANAL", KANAL),
                              tur=getattr(konu, "LOGO", "kilic")))
    kp.sfx("ding", t0 + 1.6, 0.35)

    satirlar = altyazi_satirlari(cz, azami=getattr(konu, "ALTYAZI_AZAMI", 78))
    video.ust.append(Altyazi(satirlar, boyut=getattr(konu, "ALTYAZI_BOYUT", 34)))
    with open(os.path.join(cikti, "altyazi.srt"), "w", encoding="utf-8") as f:
        for k, (t0, t1, m) in enumerate(satirlar, 1):
            f.write(f"{k}\n{_srt(t0)} --> {_srt(t1)}\n{m}\n\n")
    with open(os.path.join(cikti, "zamanlama.json"), "w", encoding="utf-8") as f:
        json.dump({"sahneler": araliklar, "cumleler": cz}, f, ensure_ascii=False, indent=1)
    from yayin import youtube_md
    with open(os.path.join(cikti, "youtube.md"), "w", encoding="utf-8") as f:
        f.write(youtube_md(konu, araliklar))
    print(f"Toplam süre: {video.sure / 60:.1f} dk ({len(satirlar)} altyazı satırı)")

    if a.onizleme or a.sadece_kareler:
        zamanlar = [float(x) for x in a.onizleme.split(",") if x] or \
                   [(s.t0 + s.t1) / 2 for s in video.sahneler]
        for k, zt in enumerate(zamanlar):
            video.kare(zt).write_to_png(os.path.join(cikti, f"onizleme_{k:02d}_{zt:06.1f}.png"))
        print(f"{len(zamanlar)} kare kaydedildi -> {cikti}")
        if a.sadece_kareler:
            return

    efektler = []
    for s in video.sahneler:
        efektler += s.tum_sesler()
    sesler = dict(SESLER, **getattr(konu, "GECIS_SESLERI", {}))
    for sinir, tur, d in video.gecis_anlari():
        if sesler.get(tur):
            efektler.append((max(0, sinir - d / 2 - 0.05), sesler[tur], 0.9))
    wav = os.path.join(cikti, "ses_miks.wav")
    S.miksaj(video.sure, vo, konusmalar, efektler, muzik_seviye=getattr(konu, "MUZIK_SEVIYE", 0.22),
             efekt_seviye=getattr(konu, "EFEKT_SEVIYE", 0.45), cikis_wav=wav)
    mp4 = os.path.join(cikti, f"{ad}.mp4")
    video.kaydet(mp4, wav)
    print(f"Bitti: {mp4}")


if __name__ == "__main__":
    main()
