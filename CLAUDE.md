# Umay ile Zıpzıp — çalışma kuralları

Kullanıcıyla her zaman **Türkçe** konuş. Proje: 2–5 yaş için Türkçe çizgi film serisi, YouTube kanalı **"Umay ile Zıpzıp"**.
Claude yönetmen, yazar ve tasarımcıdır.

## Her yeni bölümde teslim edilecekler (görev listesi)

1. **Bölüm videosu — yalnızca 1080p** (720p üretme). GitHub'da `videolar/` altında 100 MB altı parçalara bölünür
   (`bolumN_..._1080p_parcaK.mp4`, bölüm sınırlarından), `videolar/BENIOKU.md` güncellenir; parçalar sohbete de gönderilir.
2. **Shorts videosu** — 1080×1920, ≤60 sn, bölümün en akılda kalan kısmı (genelde tekerleme/şarkı):
   `python3 studio/short_yap.py --src ... --start ... --end ... --baslik ... --renk ... --out shorts/...`
3. **Küçük resim (kapak)** — 1280×720, `studio/kanal_gorselleri.py` içine bölüm için yeni bir `kapak_...` fonksiyonu eklenir → `kanal/`.
4. **YouTube metinleri** — `docs/youtube/bolumN_....md`: başlık (≤100 karakter), açıklama (bölüm zaman damgalarıyla,
   `ep*.py --plan` çıktısından), etiketler; Shorts için başlık + açıklama. Kitle: **çocuklara yönelik**.
5. Kanal görselleri ve açıklaması: `kanal/` ve `docs/youtube/kanal.md` (değişiklik istenirse güncellenir).
6. İstenirse WhatsApp için 16 MB altı parçalar (`whatsapp/`).

Her teslimden sonra değişiklikler commit + push edilir (dal: `claude/cocuk-animasyon-videosu-k4whnz`).

## Teknik notlar

- Bölüm motoru: `studio/ep1_renkli_kelebekler.py` (`--plan`, `--still`, `--style kagit|cizgi`, `--start/--end`, `--mux-only`).
- Sesler: anlatıcı Gemini **Aoede**, Umay **Leda** + WORLD küçük çocuk dönüşümü (`voice_batch.py`), Zıpzıp gerçek CC0 havlama (`zipzip_barks.py`).
- API anahtarlarını asla sohbete yazdırma/isteme. "Gemini" MCP sunucusu bir kripto borsasıdır, kullanılmaz.
- Süreç öldürürken kendi kabuğunu eşleyen `pkill -f` kullanma.
