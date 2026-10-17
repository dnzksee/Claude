# Umay ile Zıpzıp 🎨🐶

2–5 yaş için Türkçe animasyon dizisi: dört yaşındaki **Umay** ve en iyi arkadaşı köpek **Zıpzıp**.

## Örnek kesit: "Renkli Kelebek" (76 sn)

**Seçilen teknik: Kâğıt kesme** (katmanlı kâğıt, yumuşak gölgeler, stop-motion titreşimi)

| Dosya | Açıklama |
|---|---|
| `renders/umay_zipzip_renkli_kelebek_KAGIT_KESME.mp4` | Güncel örnek: Umay ile Zıpzıp |
| `renders/eski_denemeler/` | Teknik seçimi için yapılan ilk denemeler (suluboya, kâğıt kesme, yumuşak 3B, keçe; eski isimlerle) |

## Belgeler
- `docs/01_dizi_kitabi.md`: karakterler, renk paleti, pedagojik ilkeler, teknik karşılaştırması
- `docs/02_bolum_formati_25_30_dk.md`: 25–30 dakikalık bölüm iskeleti ve ilk sezon hikâye fikirleri
- `docs/03_ornek_kesit_cekim_listesi.md`: çekim listesi, animasyon notları, 6:30'a genişletme planı

## Üretim altyapısı (`studio/`)
Tamamen kodla üretilen bir 2B animasyon stüdyosu:

```
studio/
  engine/core.py        yumuşatma eğrileri, anahtar kare izleri, döşenebilir gürültü
  engine/styles.py      çizim teknikleri: Suluboya, Kâğıt Kesme, Yumuşak 3B, Keçe + son işlem
  engine/characters.py  Umay, Zıpzıp, kelebek, çiçekler (iskelet tabanlı, pozlanabilir)
  engine/world.py       6 katmanlı paralaks dünya (gökyüzü, bulut, tepeler, ev, çayır, ön plan)
  engine/audio.py       özgün müzik ve efekt sentezi (kalimba, müzik kutusu, ksilofon…)
  ep01_renkli_kelebek.py  bölüm senaryosu: kamera, oyunculuk, diyalog, müzik zamanlaması
  make_voices.py        geçici Türkçe seslendirme (Piper TTS)
```

### Çalıştırma
```bash
pip install pycairo opencv-python-headless numpy
cd studio
python3 ep01_renkli_kelebek.py --style kagit        # diğerleri: suluboya | yumusak3b | kece
python3 ep01_renkli_kelebek.py --style suluboya --still 22 48   # yalnızca kare önizleme
python3 ep01_renkli_kelebek.py --style kagit --scale 0.5        # hızlı, düşük çözünürlüklü taslak
```
Yazı tipleri (`assets/fonts`, SIL OFL lisanslı) sisteme kurulu olmalı: `cp assets/fonts/*.ttf ~/.fonts && fc-cache -f`.

### Seslendirme
`assets/vo/` içindeki sesler **geçici** (yapay zekâ TTS) seslerdir. Yayın için profesyonel seslendirme önerilir: Umay için 6–9 yaş arası bir çocuk ya da çocuk sesi yapabilen bir sanatçı, sıcak bir anlatıcı. Yeni kayıtları aynı dosya adlarıyla `assets/vo/` içine koymanız yeterli; dudak senkronu ve müzik kısma otomatik güncellenir.
