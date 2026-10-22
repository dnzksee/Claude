"""YouTube yayın metni: başlık, açıklama (bölüm zaman damgalarıyla) ve etiketler.

uret.py her üretimin sonunda cikti/<konu>/youtube.md dosyasını yazar. Konu dosyasındaki isteğe bağlı
YOUTUBE sözlüğü kullanılır: baslik, kanca (açıklamanın ilk satırı), ozet, etiketler, hashtagler.
Short (FORMAT = "dikey") için kısa açıklama ve #shorts eklenir; uzun videonun linki için yer tutucu bırakılır.
"""

KANAL_ETIKETLERI = ["tarih", "savaş tarihi", "dünya tarihi", "tarih belgeseli", "animasyon", "çizgi film",
                    "Kroniknâme"]
KANAL_SATIRI = ("Kroniknâme: Spartalılardan Napolyon'a, İskender'den Fatih'e; tarihin büyük savaşları "
                "çizgi filmle anlatılıyor. Abone ol, bir sonraki sayfayı birlikte açalım!")


def _zaman(t):
    t = int(t)
    return f"{t // 60:02d}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}"


def _etiket_sinirla(etiketler, azami=490):
    """YouTube etiket alanı toplam ~500 karakter; tekrarları at, sığanı al."""
    sonuc, uz = [], 0
    for e in etiketler:
        e = e.strip()
        if not e or e.lower() in (x.lower() for x in sonuc):
            continue
        ek = len(e) + 2
        if uz + ek > azami:
            break
        sonuc.append(e)
        uz += ek
    return sonuc


def yayin_metni(konu, araliklar):
    """araliklar: [(t0, t1), ...] açılış, sahneler, kapanış (uret.yerlestir çıktısı)."""
    yt = getattr(konu, "YOUTUBE", {})
    short = getattr(konu, "FORMAT", "yatay") == "dikey"
    baslik = yt.get("baslik") or f"{konu.BASLIK} | {konu.ALT_BASLIK}"
    if short and "#shorts" not in baslik.lower():
        baslik = f"{baslik} #shorts"
    baslik = baslik[:100]
    kanca = yt.get("kanca") or konu.ACILIS[0]
    hashtag = yt.get("hashtagler", ["#tarih", "#savaş", "#Kroniknâme"])
    satirlar = [kanca, ""]
    if short:
        satirlar += [yt.get("ozet", " ".join(konu.ACILIS)), "",
                     "▶ Hikâyenin tamamı: [UZUN VİDEO LİNKİ]", "", KANAL_SATIRI, "", " ".join(hashtag + ["#shorts"])]
    else:
        satirlar += [yt.get("ozet", " ".join(konu.ACILIS[1:]) or konu.ALT_BASLIK), "", "Bölümler:",
                     f"00:00 Giriş"]
        for sh, (t0, _) in zip(konu.SAHNELER, araliklar[1:-1]):
            satirlar.append(f"{_zaman(t0)} {sh['baslik']}")
        satirlar.append(f"{_zaman(araliklar[-1][0])} Kapanış")
        satirlar += ["", "▶ Kısa versiyon (Shorts): [SHORT LİNKİ]", "", KANAL_SATIRI, "", " ".join(hashtag)]
    etiketler = _etiket_sinirla(yt.get("etiketler", []) + KANAL_ETIKETLERI + (["shorts"] if short else []))
    return baslik, "\n".join(satirlar), etiketler


def youtube_md(konu, araliklar):
    baslik, aciklama, etiketler = yayin_metni(konu, araliklar)
    return (f"# YouTube yayın bilgileri\n\n## Başlık ({len(baslik)}/100)\n```\n{baslik}\n```\n\n"
            f"## Açıklama\n```\n{aciklama}\n```\n\n## Etiketler ({len(', '.join(etiketler))}/500)\n"
            f"```\n{', '.join(etiketler)}\n```\n")
