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

# Gemini: konuşan -> (ses, yönerge). Umay'a ek olarak 3 yaş dönüşümü uygulanır (engine/toddler_voice.py).
GEMINI_MODEL = "gemini-2.5-flash-preview-tts"
GEMINI = {
    "anlatici": ("Aoede", "Say in a sweet, warm, smiling preschool cartoon storyteller voice, lively, playful and expressive"),
    "umay": ("Leda", "Say slowly and sweetly, like a cute three-year-old toddler girl in a cartoon: sing-song, soft and breathy, "
                     "a tiny bit lispy, full of wonder, with little giggles"),
    "zipzip": ("Laomedeia", "Make the sound of a tiny, cute, playful cartoon puppy, high and happy, short and bouncy"),
}
UMAY_TODDLER = (330.0, 1.20)  # hedef perde (Hz), formant ölçeği: seçilen "en tatlı" ayar
# satıra özel duygu ipuçları (anlatıcı ve karakterler)
HINT = {
    "n0": "excited, like opening a storybook", "n1": "warm and smiling, stretch 'Günaydın' a little",
    "n2": "short curious pause, then joyful on the name", "n3": "slow, curious question asked directly to the child",
    "n3b": "cheerful and proud, like applauding", "n8": "bouncy and energetic", "n4": "delighted discovery",
    "n5": "tiny pause after 'Bir de', then joyful", "n9": "slowing down, soft and gentle, almost whispering",
    "n6": "mysterious, whispery, curious question", "n6b": "giggling surprise", "n10": "laughing while telling",
    "n7": "warm, loving, slow ending",
    "e1": "amazed and excited", "e2": "eager and bouncy", "e3": "sweet, a little sad goodbye", "e4": "a real happy giggle",
    "e5": "happy goodbye to the viewers",
    "p1": "two short happy barks", "p2": "build up a funny sneeze then a big cute sneeze", "p3": "one happy little bark",
}
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


def gemini_all(cues, only=None):
    import base64, json, time, urllib.request, urllib.error, wave
    import numpy as np
    from engine.toddler_voice import toddler
    key = os.environ["GEMINI_API_KEY"]
    for cid, _, who, text in cues:
        if only and cid not in only:
            continue
        voice, style = GEMINI[who]
        prompt = f"{style}; {HINT.get(cid, '')}: {text}"
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        for attempt in range(6):
            try:
                req = urllib.request.Request(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
                    data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
                part = json.load(urllib.request.urlopen(req, timeout=180))["candidates"][0]["content"]["parts"][0]["inlineData"]
                break
            except (urllib.error.HTTPError, urllib.error.URLError, KeyError):
                if attempt == 5:
                    raise
                time.sleep(20 * (attempt + 1))
        pcm = np.frombuffer(base64.b64decode(part["data"]), np.int16)
        rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1].split(";")[0])
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            x = pcm.astype(np.float64) / 32768
            if who == "umay":
                x = toddler(x, rate, *UMAY_TODDLER)
                x = x / (np.abs(x).max() + 1e-9) * 0.9
            with wave.open(tmp.name, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
                w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
            out = os.path.join(VO_DIR, f"{cid}.wav")
            pre = "aresample=48000,highpass=f=90,lowpass=f=11000," if who == "umay" else "aresample=48000,"
            finish(tmp.name, out, pre + "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                   "silenceremove=start_periods=1:start_threshold=-45dB,areverse,adelay=30,apad=pad_dur=0.08")
            print(out, flush=True)
        time.sleep(7)


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
    ap.add_argument("--engine", default="gemini", choices=["gemini", "edge", "piper"])
    ap.add_argument("--only", nargs="*", help="yalnızca bu kimlikleri üret (ör. n1 e2)")
    ap.add_argument("--model", help="piper için .onnx ses modeli")
    a = ap.parse_args()
    os.makedirs(VO_DIR, exist_ok=True)
    if a.engine == "gemini":
        gemini_all(CUES, a.only)
    elif a.engine == "edge":
        asyncio.run(edge_all(CUES))
    else:
        piper_all(CUES, a.model)


if __name__ == "__main__":
    main()
