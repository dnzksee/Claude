"""20 dakikalık bölüm için seslendirme: her karakter/bölüm metni tek seferde okutulur (az istek),
sonra sessizliklerden cümlelere bölünür. Kaynak: senaryo_renkli_kelebekler.py (DOSYALAR, SESLER).

Aynı akış, kullanıcının AI Studio'dan indirdiği dosyalar için de çalışır:
    python3 voice_batch.py                       # Gemini ile üret + böl
    python3 voice_batch.py --src ~/indirilenler  # hazır dosyaları (anlatici_2_mavi.wav ...) böl
Çıktı: assets/vo_ep1/<KİMLİK>.wav
"""
import argparse
import base64
import glob
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
from engine.toddler_voice import toddler

# hangi bölüm: UMAY_BOLUM=2 → senaryo_sekil_avi, assets/vo_ep2 (varsayılan 1. bölüm)
BOLUM = os.environ.get("UMAY_BOLUM", "1")
SENARYO = {"1": "senaryo_renkli_kelebekler", "2": "senaryo_sekil_avi"}[BOLUM]
_S = importlib.import_module(SENARYO)
DOSYALAR, SESLER, satirlar = _S.DOSYALAR, _S.SESLER, _S.satirlar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", f"vo_ep{BOLUM}")
RAW = os.path.join(ROOT, "build", f"vo_ep{BOLUM}_raw")
MODEL = "gemini-2.5-flash-preview-tts"
UMAY_TODDLER = (330.0, 1.20)
POST = ("highpass=f=70,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=5:release=90,loudnorm=I=-16:TP=-2,adelay=30,apad=pad_dur=0.08")


def gemini(prompt, voice, out):
    key = os.environ["GEMINI_API_KEY"]
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(6):
        try:
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
            part = json.load(urllib.request.urlopen(req, timeout=600))["candidates"][0]["content"]["parts"][0]["inlineData"]
            break
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as e:
            print("   tekrar deneniyor:", str(e)[:80], flush=True)
            # boş yanıt (ses yok) ya da günlük kota: en fazla bir kez daha dene, kotayı boşa harcama
            empty = isinstance(e, KeyError) or (isinstance(e, urllib.error.HTTPError) and e.code == 429 and attempt >= 1)
            if attempt == 5 or (empty and attempt >= 1):
                raise
            time.sleep(25 * (attempt + 1))
    pcm = base64.b64decode(part["data"])
    rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1].split(";")[0])
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def load(path):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "24000", tmp.name], check=True)
        with wave.open(tmp.name) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    return x, 24000


def _silences(x, fs, min_len=0.12, thr=-38):
    hop = int(fs * 0.01)
    fr = len(x) // hop
    rms = np.sqrt(np.mean(x[:fr * hop].reshape(fr, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    silent = db < thr
    runs, i = [], 0
    while i < fr:
        if silent[i]:
            j = i
            while j < fr and silent[j]:
                j += 1
            if i > 0 and j < fr and (j - i) * 0.01 >= min_len:
                runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return runs


def split(x, fs, texts):
    """Cümle sınırlarını seç: uzun sessizlikleri tercih et, ama her parçanın süresi metnin uzunluğuna uymalı
    (dinamik programlama). Böylece cümle içi duraklamalar ("Bir... iki...") yanlışlıkla kesilmez."""
    n = len(texts)
    total = len(x) / fs
    runs = _silences(x, fs)
    if len(runs) < n - 1:
        raise RuntimeError(f"yeterli sessizlik yok: {len(runs)} < {n - 1}")
    chars = np.array([max(len(t.replace(".", "").replace(" ", "")), 2) for t in texts], float)
    # cümle içi duraklamalar: "..." uzun, cümle ortasındaki . ! ? kısa
    pauses = np.array([0.8 * t.count("...") + 0.3 * sum(t.rstrip(" .!?").count(ch) for ch in "!?") +
                       0.3 * t.rstrip(" .!?").replace("...", "").count(".") for t in texts], float)
    top = sorted((b - a for a, b in runs), reverse=True)[: n - 1]
    rate = max((total - sum(top) - pauses.sum()) / chars.sum(), 0.03)   # saniye / harf
    C = len(runs)
    mids = [(a + b) / 2 for a, b in runs]
    INF = 1e18

    def seg_cost(k, t0, t1, sil0, sil1):
        d = (t1 - t0) - sil0 / 2 - sil1 / 2
        e = chars[k] * rate + pauses[k]
        return ((d - e) / (0.30 * e + 0.35)) ** 2

    # dp[k][j]: ilk k+1 parça, k. kesim j. sessizlikte
    dp = np.full((n - 1, C), INF)
    bk = np.zeros((n - 1, C), int)
    for j in range(C):
        a, b = runs[j]
        dp[0, j] = seg_cost(0, 0.0, mids[j], 0.0, b - a) - 2.0 * np.log(b - a)
    for k in range(1, n - 1):
        for j in range(k, C):
            a, b = runs[j]
            best, arg = INF, 0
            for i in range(k - 1, j):
                if dp[k - 1, i] >= INF:
                    continue
                pa, pb = runs[i]
                c = dp[k - 1, i] + seg_cost(k, mids[i], mids[j], pb - pa, b - a)
                if c < best:
                    best, arg = c, i
            dp[k, j] = best - 2.0 * np.log(b - a)
            bk[k, j] = arg
    best, jl = INF, 0
    for j in range(n - 2, C):
        a, b = runs[j]
        c = dp[n - 2, j] + seg_cost(n - 1, mids[j], total, b - a, 0.0)
        if c < best:
            best, jl = c, j
    cuts = [jl]
    for k in range(n - 2, 0, -1):
        cuts.append(bk[k, cuts[-1]])
    cuts = cuts[::-1]
    bounds = [0] + [int(mids[j] * fs) for j in cuts] + [len(x)]
    shortest = min(runs[j][1] - runs[j][0] for j in cuts)
    return [x[bounds[k]:bounds[k + 1]] for k in range(n)], shortest


def write(path, x, fs, who):
    if who == "umay":
        x = toddler(x, fs, *UMAY_TODDLER)
        x = x / (np.abs(x).max() + 1e-9) * 0.9
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        with wave.open(tmp.name, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(fs)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
        pre = "aresample=48000,highpass=f=90,lowpass=f=11000," if who == "umay" else "aresample=48000,"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-af", pre + POST, "-ac", "1",
                        "-ar", "48000", "-sample_fmt", "s16", path], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", help="AI Studio'dan indirilen dosyaların klasörü (verilmezse Gemini API ile üretilir)")
    ap.add_argument("--only", nargs="*", help="yalnızca bu dosya adları (ör. anlatici_2_mavi)")
    ap.add_argument("--chunk", type=int, default=0, help="uzun metni bu kadar satırlık parçalara böl (dakikalık sınırlar için)")
    ap.add_argument("--style", default=None, help="stil yönergesini değiştir (ör. 3.1 modeli yaş ifadesi kabul etmiyor)")
    ap.add_argument("--model", default=None, help="Gemini ses modeli (varsayılan gemini-2.5-flash-preview-tts)")
    a = ap.parse_args()
    if a.model:
        globals()["MODEL"] = a.model
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    for ad, who, bols in DOSYALAR:
        if a.only and ad not in a.only:
            continue
        all_lines = list(satirlar(who, bols))
        size = a.chunk if (a.chunk and not a.src) else len(all_lines)
        for ci in range(0, len(all_lines), size):
            lines = all_lines[ci:ci + size]
            part = ad if size == len(all_lines) else f"{ad}_p{ci // size + 1}"
            if a.src:
                cand = [f for f in glob.glob(os.path.join(a.src, ad + ".*"))]
                if not cand:
                    print(f"- {ad}: dosya yok, atlandı")
                    break
                raw = cand[0]
            else:
                raw = os.path.join(RAW, part + ".wav")
                if not os.path.exists(raw):
                    voice, style = SESLER[who]
                    if a.style:
                        style = a.style + " Leave a clear pause between each line."
                    style = style.replace("Leave a clear pause between each line.",
                                          "Leave a long, two-second silent pause between each line.")
                    text = "\n".join(f"{t}" for _, _, t, _ in lines)
                    print(f"* {part}: {len(lines)} cümle Gemini'ye okutuluyor ({voice})", flush=True)
                    gemini(f"{style} Read ALL {len(lines)} lines below, in order, without skipping any line:\n\n{text}", voice, raw)
                    time.sleep(65 if size < len(all_lines) else 10)
            x, fs = load(raw)
            segs, shortest = split(x, fs, [t for _, _, t, _ in lines])
            for (cid, _, _, _), seg in zip(lines, segs):
                write(os.path.join(OUT, f"{cid}.wav"), seg, fs, who)
            print(f"✓ {part}: {len(lines)} cümleye bölündü (en kısa ayraç {shortest:.2f} sn, toplam {len(x) / fs:.1f} sn)", flush=True)
        continue
        print(f"✓ {ad}: {len(lines)} cümleye bölündü (en kısa ayraç {shortest:.2f} sn, toplam {len(x) / fs:.1f} sn)", flush=True)


if __name__ == "__main__":
    main()
