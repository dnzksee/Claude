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
    echo "BITTI $k $d"
  done
done
echo "HEPSI_BITTI"
