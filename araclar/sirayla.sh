#!/bin/bash
# Kalan tüm video/dil seslendirmelerini sırayla yürütür; kota dolunca (kod 3) durur.
# Kullanım: bash araclar/sirayla.sh   (depo kökünden; TTS_SINIR ortamdan okunur)
# Çalışma klasörü: /home/user/is/<konu> (tr_mix.wav, arka.wav, vokal.wav, tr.srt). Yoksa hazırlar.
# Biten (repo'da <konu>/<dil>/<konu>_<dil>_ses.mp3 olan) dilleri atlar. Biten her dil için
# mp3+srt'yi <konu>/<dil>/ içine kopyalar ve "BITTI <konu> <dil>" yazar (commit/push çağıran yapar).
DEPO=$(cd "$(dirname "$0")/.." && pwd)
IS=/home/user/is
SIRA="pekmez celeste tavsan lagari preveze fetih"
DILLER="en:English es:Spanish ru:Russian ar:Arabic ur:Urdu ko:Korean"
for k in $SIRA; do
  for x in $DILLER; do
    d=${x%%:*}; ad=${x#*:}
    [ -f "$DEPO/$k/$d/${k}_${d}_ses.mp3" ] && continue
    w=$IS/$k; mkdir -p "$w"
    if [ ! -f "$w/arka.wav" ]; then
      (cd "$DEPO" && git lfs pull -I "$k/${k}_1080p.mp4")
      ffmpeg -v error -y -i "$DEPO/$k/${k}_1080p.mp4" -vn -ac 2 -ar 44100 "$w/tr_mix.wav"
      (cd "$w" && python3 -m demucs --two-stems vocals -n htdemucs -o sep tr_mix.wav >/dev/null 2>&1 \
        && cp sep/htdemucs/tr_mix/no_vocals.wav arka.wav && cp sep/htdemucs/tr_mix/vocals.wav vokal.wav)
    fi
    cp "$DEPO/$k/altyazi.srt" "$w/tr.srt"
    cp "$DEPO/$k/dil_kaynak/$d.py" "$w/"
    (cd "$w" && set -o pipefail && python3 -W ignore "$DEPO/araclar/dublaj.py" . "$d" "$ad" hepsi 2>&1 | grep --line-buffered -v "^\s*$")
    c=$?
    [ "$c" -eq 3 ] && { echo "KOTA_BITTI $k $d"; exit 3; }
    [ "$c" -eq 4 ] && { echo "KREDI_BITTI $k $d"; exit 4; }
    [ "$c" -ne 0 ] && { echo "HATA $k $d ($c)"; exit "$c"; }
    [ -f "$w/${k}_${d}_ses.mp3" ] || { echo "HATA $k $d (mp3 yok)"; exit 1; }
    mkdir -p "$DEPO/$k/$d"
    cp "$w/${k}_${d}_ses.mp3" "$w/altyazi_${d}.srt" "$DEPO/$k/$d/"
    # ses videoyla aynı uzunlukta mı (en fazla 0.5 sn fark)
    sv=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DEPO/$k/${k}_1080p.mp4")
    sa=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DEPO/$k/$d/${k}_${d}_ses.mp3")
    python3 -c "import sys; sys.exit(0 if abs($sv-$sa) <= 0.5 else 1)" || { echo "HATA $k $d (süre: video $sv, ses $sa)"; exit 1; }
    # teslim: dnzksee/Claude, kroniknane-videolar dalı
    (cd "$DEPO" && git add "$k/$d/${k}_${d}_ses.mp3" "$k/$d/altyazi_${d}.srt" "$k/$d/kapak_${d}.png" "$k/youtube_diller.md" \
      && git commit -q -m "$k: $d ses ve altyazı" -m "Co-Authored-By: Claude <noreply@anthropic.com>" \
      && for i in 1 2 3 4; do git push -q -u origin kroniknane-videolar && break; sleep $((2**i)); done)
    echo "BITTI $k $d"
  done
done
echo "HEPSI_BITTI"
