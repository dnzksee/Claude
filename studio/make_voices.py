"""Geçici (yer tutucu) Türkçe seslendirme: Piper TTS ile üretir.
Gerçek yapımda bu dosyalar profesyonel seslendirme sanatçılarının kayıtlarıyla değiştirilir
(aynı dosya adlarıyla assets/vo/ içine koymak yeterli; dudak senkronu otomatik güncellenir).

    pip install piper-tts
    python3 make_voices.py --model /yol/tr_TR-dfki-medium.onnx
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_renkli_kelebek import CUES, VO_DIR

# konuşana göre ses perdesi: Ela çocuk sesi, Pamuk sevimli/yüksek, anlatıcı doğal
PITCH = {"anlatici": 1.0, "ela": 1.38, "pamuk": 1.28}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    a = ap.parse_args()
    os.makedirs(VO_DIR, exist_ok=True)
    for cid, _, who, text, speed in CUES:
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            subprocess.run([sys.executable, "-m", "piper", "-m", a.model, "--length-scale", str(speed),
                            "--sentence-silence", "0.2", "-f", tmp.name], input=text.encode(), check=True,
                           stderr=subprocess.DEVNULL)
            k = PITCH[who]
            filt = f"asetrate=22050*{k},aresample=48000,atempo={1 / k:.4f}" if k != 1.0 else "aresample=48000"
            filt += ",highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-2"
            out = os.path.join(VO_DIR, f"{cid}.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-af", filt, "-ac", "1",
                            "-ar", "48000", "-sample_fmt", "s16", out], check=True)
            print(out)


if __name__ == "__main__":
    main()
