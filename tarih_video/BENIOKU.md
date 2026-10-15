# Tarih Savaş Videoları — Üretim Sistemi

Yatay (1920x1080) YouTube videoları: Türkçe seslendirme + altyazı + taktik savaş animasyonu.

## Kurulum
```
pip install pycairo numpy edge-tts
# ffmpeg sistemde kurulu olmalı
```

## Yeni video üretmek
1. `projeler/malazgirt/` klasörünü kopyala (örn. `projeler/kadesh/`).
2. `senaryo.py` içinde:
   - `BOLUMLER`: anlatım metni, bölüm bölüm (her biri bir YouTube bölümü olur)
   - `arka_plan()`: zemin tipi (bozkir / col / yesil / kar), tepeler, nehirler, şehirler
   - `kur(video, T)`: birlikler, komutanlar, oklar, kamera hareketleri.
     `T["bolum_id"]` o bölümün başlangıç ve bitiş saniyesini verir, böylece animasyon seslendirmeyle kendiliğinden senkron olur.
3. Çalıştır:
```
python3 uret.py projeler/kadesh                  # tam video
python3 uret.py projeler/kadesh --sessiz         # hızlı deneme (TTS yok)
python3 uret.py projeler/kadesh --ses tr-TR-EmelNeural   # kadın ses
```

## Çıktılar (`projeler/<ad>/cikti/`)
- `video.mp4`: altyazısı gömülü final video
- `altyazi.srt`: YouTube'a ayrıca yüklenecek altyazı dosyası
- `youtube_bolumler.txt`: video açıklamasına yapıştırılacak bölüm zaman damgaları

## Motor öğeleri (`motor/sahne.py`)
| Öğe | Ne işe yarar |
|---|---|
| `Birlik(taraf, tip, x, y, g, d)` | Birlik bloğu. Tipler: piyade, suvari, agir_suvari, okcu, atli_okcu. `.belir() .git() .savas() .kaybol()` |
| `Komutan(ad, taraf, birlik)` | Sancak ve isim levhası. `.esir(t)` ile ESİR damgası basar |
| `HareketOku` | Zamanla uzayan hareket oku |
| `OkYagmuru` | Bir birlikten diğerine uçan oklar |
| `EtiketBalonu` | Haritada kısa açıklama ("Sahte ricat!") |
| `BaslikKarti`, `BolumEtiketi`, `Lejant` | Ekran yazıları |
| `video.kamera_git()` | Kamerayı kaydırır, yakınlaştırır |
