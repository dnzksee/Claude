"""Geçici (yer tutucu) Türkçe seslendirme.

Varsayılan motor: Microsoft nöral TTS ("tr-TR-EmelNeural", edge-tts ile). Doğal ve sıcak bir sestir.
Üç karakter aynı sesten farklı perde ve hızla ayrılır:
  anlatıcı: doğal, biraz yavaş  ·  Umay: ince çocuk sesi  ·  Zıpzıp: en tiz, çizgi film tadında

Yayın için: aynı sesler Azure Speech hizmetinde ticari lisansla kullanılabilir ya da
profesyonel seslendirme sanatçılarıyla kayıt yapılır. Yeni kayıtları aynı dosya adlarıyla
assets/vo/ içine koymak yeterli; dudak senkronu ve müzik kısma otomatik güncellenir.

    pip install edge-tts
    python3 make_voices.py                 # nöral ses (internet gerekir)
    python3 make_voices.py --engine piper --model /yol/tr_TR-dfki-medium.onnx   # çevrimdışı yedek
"""
import argparse
import asyncio
import os
import ssl
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_renkli_kelebek import CUES, VO_DIR

# konuşan: (ses, perde, hız)
EDGE = {
    "anlatici": ("tr-TR-EmelNeural", "+0Hz", "-6%"),
    "umay": ("tr-TR-EmelNeural", "+45Hz", "+2%"),
    "zipzip": ("tr-TR-EmelNeural", "+90Hz", "+8%"),
}
PIPER_PITCH = {"anlatici": 1.0, "umay": 1.38, "zipzip": 1.28}
POST = ",highpass=f=70,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=90,loudnorm=I=-16:TP=-2"


def finish(src, out, pre="aresample=48000"):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", pre + POST, "-ac", "1",
                    "-ar", "48000", "-sample_fmt", "s16", out], check=True)


async def edge_all(cues):
    import edge_tts
    import edge_tts.communicate as comm
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
    if ca:
        comm._SSL_CTX = ssl.create_default_context(cafile=ca)
    for cid, _, who, text in cues:
        voice, pitch, rate = EDGE[who]
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(text, voice, pitch=pitch, rate=rate).save(tmp.name)
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2 ** attempt)
            out = os.path.join(VO_DIR, f"{cid}.wav")
            finish(tmp.name, out, "aresample=48000,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,adelay=30,apad=pad_dur=0.08")
            print(out)


def piper_all(cues, model):
    for cid, _, who, text in cues:
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            subprocess.run([sys.executable, "-m", "piper", "-m", model, "--length-scale", "1.1",
                            "--sentence-silence", "0.2", "-f", tmp.name], input=text.encode(), check=True,
                           stderr=subprocess.DEVNULL)
            k = PIPER_PITCH[who]
            pre = f"asetrate=22050*{k},aresample=48000,atempo={1 / k:.4f}" if k != 1.0 else "aresample=48000"
            out = os.path.join(VO_DIR, f"{cid}.wav")
            finish(tmp.name, out, pre)
            print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="edge", choices=["edge", "piper"])
    ap.add_argument("--model", help="piper için .onnx ses modeli")
    a = ap.parse_args()
    os.makedirs(VO_DIR, exist_ok=True)
    if a.engine == "edge":
        asyncio.run(edge_all(CUES))
    else:
        piper_all(CUES, a.model)


if __name__ == "__main__":
    main()
