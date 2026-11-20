# Araçlar (çok dilli seslendirme)

Bulut ortamı yenilenince çalışma klasörü silinir; araçlar burada yedeklidir.

Kurulum: `pip install faster-whisper soundfile requests demucs` + `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`,
`apt-get install -y fonts-noto-core fonts-noto-cjk libraqm0`. Anahtar: `GEMINI_API_KEY` ortam değişkeni.

Bir video için çalışma klasörü:
1. `ffmpeg -i <konu>/<konu>_1080p.mp4 -vn -ac 2 -ar 44100 tr_mix.wav`
2. `python3 -m demucs --two-stems vocals -n htdemucs -o sep tr_mix.wav` → `no_vocals.wav` = `arka.wav`, `vocals.wav` = `vokal.wav`
3. `<konu>/altyazi.srt` → `tr.srt`; `<konu>/dil_kaynak/<dil>.py` çevirileri buraya
4. `python3 dublaj.py . <dil> <DilAdi> hepsi` (üret → kontrol → onar → birleştir). Kota dolarsa ertesi gün aynı komut kaldığı yerden sürer.
5. Kapak: `python3 kapak_dil.py <konu>/dil_kaynak/kapak_arka.png kapak_<dil>.png <dil> "satır1" "satır2" "satır3" 950`
