# Umay ile Zıpzıp, 1. Bölüm: "Renkli Kelebekler" (13:46)

| Dosya | Kalite | Bölümde |
|---|---|---|
| `bolum1_renkli_kelebekler_720p_tek_parca.mp4` | 720p, tek parça | 0:00 – 13:46 |
| `bolum1_renkli_kelebekler_1080p_parca1.mp4` | 1080p | 0:00 – 4:41 · Açılış ve MAVİ |
| `bolum1_renkli_kelebekler_1080p_parca2.mp4` | 1080p | 4:41 – 9:12 · KIRMIZI |
| `bolum1_renkli_kelebekler_1080p_parca3.mp4` | 1080p | 9:12 – 13:46 · SARI ve final |

GitHub'da dosyaya tıklayıp **Download raw file** (indir) simgesiyle indirebilirsiniz.

1080p parçaları tek dosyada birleştirmek için (bilgisayarda, ffmpeg ile):
```
printf "file 'bolum1_renkli_kelebekler_1080p_parca%s.mp4'\n" 1 2 3 > liste.txt
ffmpeg -f concat -safe 0 -i liste.txt -c copy bolum1_renkli_kelebekler_1080p.mp4
```
