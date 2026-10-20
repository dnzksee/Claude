# Bilgi Sarmanı — 2B çizgi film belgesel (explainer) hattı

Kalın siyah dış çizgiler, cel gölgeli düz renkler, abartılı mimikli karakterler, bulanık
(alan derinlikli) arka planlar, yumuşak 2B kamera ve whip pan / punch zoom / iris geçişleri.
Yapı: açılış kartı → 4–5 metaforik sahne (her birinde bölüm etiketi) → kapanış kartı; altyazı her yerde.

## Çalıştırma
```bash
cp varliklar/fontlar/*.ttf ~/.fonts && fc-cache -f      # Baloo 2 (SIL OFL)
python3 uret.py konular/hizli_yavas.py                     # tam üretim (1280×720, 24 fps)
python3 uret.py konular/hizli_yavas.py --motor sessiz --sadece-kareler   # kota harcamadan önizleme
python3 uret.py konular/hizli_yavas.py --onizleme 5,40,90 --sadece-kareler
```
Çıktılar `cikti/<konu>/` içinde: `<konu>.mp4`, `altyazi.srt`, `zamanlama.json`, `ses_miks.wav`.

## Seslendirme
- Anlatıcı sesi `ses.txt` dosyasında: **Kore** (Gemini TTS). Tarih kanalı ayrıdır (`tarih_video/ses.txt`, Iapetus).
- Seslendirme kodu tarih kanalıyla ortaktır (`tarih_video/motor/seslendirme.py`: aynı model, aynı doğrulama).
- Metin cümle cümle işlenir: cümleler tek istekte okunur (aynı ses tınısı, az kota), sonra
  sessizliklerden kesilip her cümle kendi zamanına yerleştirilir. Animasyon bu zamanlara bağlıdır.
- Önbellek: aynı metin tekrar seslendirilmez (`cikti/<konu>/ses/`).

## Yeni konu eklemek
`konular/hizli_yavas.py` dosyasını kopyalayın ve şunları değiştirin:
- `BASLIK`, `ALT_BASLIK`, `ACILIS`, `KAPANIS`, `KAPANIS_YAZI`
- `KARAKTERLER`: renk, saç (`diken | kivircik | duz | topuz | kel`), gözlük
- `SAHNELER`: `baslik`, `arkaplan` (`oda | sinif | doga | sahne | beyin | sehir | uzay`),
  `gecis` (`whip | punch | iris | capraz | kes`), `metin` (her öğe tek cümle) ve `kurgu(s)`.

Kurgu fonksiyonunda:
```python
cabuk = s.karakter("Çabuk", x=360)                 # KARAKTERLER'deki tasarım
cabuk.ifade(s.c(1), "saskin").poz(s.c(1), "isaret")  # s.c(i): i. cümlenin başladığı an
cabuk.gir(s.c(0), "sol", x=400, kos=True); cabuk.zipla(s.c(2, 0.5))
s.nesne("ampul", 640, 200, yanik=0).belir(s.c(2)).ayarla(s.c(3), yanik=1)
s.kamera.git(s.c(1), s.c(1) + 1, x=500, zoom=1.3); s.kamera.punch(s.c(2)); s.kamera.sars(s.c(3))
s.sfx("ding", s.c(4))
```
- İfadeler: notr, mutlu, kahkaha, saskin, kizgin, uzgun, dusunceli, yorgun, gururlu, panik, utangac, kararli, uykulu
- Pozlar: dur, el_salla, isaret, kollar_yukari, dusun, omuz_silk, eller_belde, yorgun, sunum, kutlama, dur_isareti, kafa_kasi
- Eşyalar: ampul, beyin, disli, saat, pil, onay, carpi, top, sopa, kalp, yildiz, para, kupa, tahta, levha,
  konusma, dusunce, patlama, ok, terazi, alarm, zzz, kitap, soru, unlem, yazi, isiltilar
- Efektler: whoosh, punch, iris, pop, ding, bzzt, boing, tik, zil, swoosh_yukari, alkis, kayit

## Motor (`motor/`)
| Dosya | İçerik |
|---|---|
| `cizim.py` | dış çizgi + cel gölge boyama, yazı, bulanıklık |
| `karakter.py` | iskelet karakter, ifade/poz ön ayarları, yürüme, zıplama (ezil-uza), göz kırpma |
| `nesneler.py` | metafor eşyaları ve `Nesne` (belir/kaybol/ayarla/değiştir) |
| `arkaplan.py` | bulanık arka planlar + keskin zemin |
| `kamera.py` | kaydırma, yakınlaşma, punch zoom, sarsıntı, paralaks |
| `gecisler.py` | whip pan, punch zoom, iris, çapraz geçiş |
| `ses.py` | özgün müzik + efekt sentezi, konuşma altında müzik kısma, miksaj |
| `kartlar.py` | logo, açılış/kapanış kartı, bölüm etiketi, altyazı |
| `video.py` | sahne, zaman çizelgesi, ffmpeg çıktısı |

Müzik ve efektlerin hepsi kodla üretilir (telifsiz).
