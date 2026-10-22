# Tarih kanalı — 2B çizgi film belgesel (explainer) hattı

Kalın siyah dış çizgiler, cel gölgeli düz renkler, abartılı mimikli karakterler, bulanık
(alan derinlikli) arka planlar, yumuşak 2B kamera ve whip pan / punch zoom / iris geçişleri.
Yapı: açılış kartı → 4–5 metaforik sahne (her birinde bölüm etiketi) → kapanış kartı; altyazı her yerde.

## Standart iş akışı (her konu)
```bash
python3 paket.py malazgirt     # uzun video (1080p) + Short (dikey) + youtube.md'ler + altyazı
```
Konu planı ve görev listesi: `KONU_PLANI.md`. Kanal görselleri ve açıklaması: `kanal/`
(`python3 araclar/kanal_gorselleri.py`). Kanal kuralı: batıdaki taraf solda, doğudaki taraf sağda.

## Çalıştırma
```bash
cd tarih_video/cizgi_film
cp varliklar/fontlar/*.ttf ~/.fonts && fc-cache -f      # Baloo 2 (SIL OFL)
python3 uret.py konular/malazgirt.py                     # tam üretim (1280×720, 24 fps)
python3 uret.py konular/malazgirt.py --motor sessiz --sadece-kareler   # kota harcamadan önizleme
python3 uret.py konular/malazgirt.py --onizleme 5,40,90 --sadece-kareler
```
Çıktılar `cikti/<konu>/` içinde: `<konu>.mp4`, `altyazi.srt`, `zamanlama.json`, `ses_miks.wav`.

## Seslendirme
- Anlatıcı sesi tarih projesinin ayarından gelir: `tarih_video/ses.txt` → **Iapetus** (Gemini TTS).
- Seslendirme kodu tarih projesinin ana hattıyla ortaktır (`tarih_video/motor/seslendirme.py`).
- Her sahne ayrı istekte okunur, sesin tamamı yazıya döktürülüp metinle karşılaştırılır (Gemini bazen
  okumayı yarıda kesip baştan başlıyor); sonra duraklamalardan cümle cümle kesilir (`motor/hizalama.py`)
  ve her cümle kendi zamanına yerleştirilir. Animasyon bu zamanlara bağlıdır.
- Günlük ücretsiz kota ≈ 10 istek: bir konu (açılış + 5 sahne + kapanış) 7 istek harcar.
- Önbellek: aynı metin tekrar seslendirilmez (`cikti/<konu>/ses/`).

## Yeni konu eklemek
`konular/malazgirt.py` dosyasını kopyalayın ve şunları değiştirin:
- `BASLIK`, `ALT_BASLIK`, `ACILIS`, `KAPANIS`, `KAPANIS_YAZI`
- `KARAKTERLER`: renk, saç (`diken | kivircik | duz | topuz | kel`), gözlük, başlık
  (`bork | tac | migfer | sarik`), sakal, kaftan (`etek=True`), kemer, elde (`yay | kilic | kalkan | sancak`)
- Kanal kuralı: batıdaki taraf solda, doğudaki taraf sağda (Bizans–Selçuklu, Makedon–Pers, Roma–Kartaca...).
- `YOUTUBE = dict(baslik=..., kanca=..., ozet=..., etiketler=[...], hashtagler=[...])`: yayın metni için.
- Short için `FORMAT = "dikey"`, `TEMPO`, `ALTYAZI_BOYUT`, `BOLUM_ETIKETI = False` (bkz. `konular/malazgirt_short.py`).
- `SAHNELER`: `baslik`, `arkaplan` (`bozkir | cadir | harita | oda | sinif | doga | sahne | beyin | sehir | uzay`; harita için
  `arkaplan_p=dict(kapsam=(lon0, lon1, lat), bolgeler=[...], etiketler=[...])`, kurguda `s.yer(lon, lat)`),
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
  konusma, dusunce, patlama, ok, terazi, alarm, zzz, kitap, soru, unlem, yazi, isiltilar,
  kilic, yay, kalkan, sancak, fil, ari_suru, kapi, damga, ok_yagmuru, pin, hilal
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
