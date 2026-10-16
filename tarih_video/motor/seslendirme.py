"""Seslendirme motorları: Gemini TTS (örn. 'Kore' sesi) ve Microsoft Edge TTS.

Her iki motor da: metin -> mp3 + [(t0, t1, cümle), ...] altyazı zamanlaması döndürür.
Gemini zaman damgası vermediği için cümle sınırları sessizlik tespitiyle bulunur.
"""
import asyncio
import base64
import json
import os
import re
import ssl
import subprocess
import time
import urllib.error
import urllib.request

GEMINI_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
# Not: gemini-3.8-flash-tts, metne eklenen her ton talimatını ("belgesel gibi oku:", "[sakin]")
# sesli okuyor ve ayrı sistem talimatını desteklemiyor. Bu yüzden metin talimatsız gönderilir.
SURUM = "v2-talimatsiz"  # önbellek anahtarına girer; seslendirme mantığı değişince artırın
DOGRULAMA_MODELI = os.environ.get("GEMINI_DOGRULAMA_MODELI", "gemini-flash-latest")


def cumlelere_bol(metin):
    return [c.strip() for c in re.split(r"(?<=[.!?…])\s+", metin.strip()) if c.strip()]


def _sessizlikler(ses, esik="-35dB", sure=0.22):
    cikti = subprocess.run(["ffmpeg", "-hide_banner", "-i", ses, "-af",
                            f"silencedetect=n={esik}:d={sure}", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    bas = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", cikti)]
    bit = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", cikti)]
    return list(zip(bas, bit))


def _sure(ses):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", ses]).strip())


def cumle_zamanla(ses, metin):
    """Cümle sınırlarını karakter oranıyla tahmin edip en yakın sessizliğe oturtur."""
    cumleler = cumlelere_bol(metin)
    toplam = _sure(ses)
    sess = _sessizlikler(ses)
    bas_konus = sess[0][1] if sess and sess[0][0] < 0.05 else 0.0
    son_konus = sess[-1][0] if sess and sess[-1][1] > toplam - 0.05 else toplam
    ic = [s for s in sess if s[0] > bas_konus + 0.05 and s[1] < son_konus - 0.05]
    uzun = sum(len(c) for c in cumleler)
    sonuc, t, birikim, kullanilan = [], bas_konus, 0, -1
    for i, c in enumerate(cumleler):
        birikim += len(c)
        if i == len(cumleler) - 1:
            sonuc.append((t, son_konus, c))
            break
        tahmin = bas_konus + (son_konus - bas_konus) * birikim / uzun
        adaylar = [(abs((s[0] + s[1]) / 2 - tahmin), j) for j, s in enumerate(ic) if j > kullanilan]
        if adaylar and min(adaylar)[0] < 2.5:
            j = min(adaylar)[1]
            kullanilan = j
            sonuc.append((t, ic[j][0], c))
            t = ic[j][1]
        else:
            sonuc.append((t, tahmin, c))
            t = tahmin
    return sonuc


def gemini_seslendir(metin, mp3, ses="Kore", deneme=8):
    anahtar = os.environ["GEMINI_API_KEY"]
    govde = json.dumps({
        "contents": [{"parts": [{"text": metin}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": ses}}}},
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    for k in range(deneme):
        istek = urllib.request.Request(url, govde, {"Content-Type": "application/json", "x-goog-api-key": anahtar})
        try:
            with urllib.request.urlopen(istek, timeout=300) as y:
                veri = json.load(y)
            parca = veri["candidates"][0]["content"]["parts"][0]["inlineData"]
            break
        except urllib.error.HTTPError as h:
            govde_hata = h.read().decode(errors="replace")
            if h.code not in (429, 500, 503) or k == deneme - 1:
                raise RuntimeError(f"Gemini TTS hatası {h.code}: {govde_hata[:400]}")
            bekle = re.search(r'"retryDelay":\s*"(\d+)', govde_hata)
            bekle = int(bekle.group(1)) + 2 if bekle else 10 * (k + 1)
            if bekle > 300:
                raise RuntimeError(f"Gemini günlük kotası doldu ({GEMINI_MODEL}); yaklaşık {bekle // 3600} saat "
                                   "sonra tekrar deneyin ya da GEMINI_TTS_MODEL ile başka model seçin.")
            print(f"  Gemini sınırı ({h.code}), {bekle} sn bekleniyor...", flush=True)
            time.sleep(bekle)
        except (KeyError, IndexError):
            if k == deneme - 1:
                raise RuntimeError(f"Gemini ses döndürmedi: {json.dumps(veri)[:400]}")
            time.sleep(5)
    oran = re.search(r"rate=(\d+)", parca["mimeType"])
    pcm = mp3 + ".pcm"
    open(pcm, "wb").write(base64.b64decode(parca["data"]))
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar",
                           oran.group(1) if oran else "24000", "-ac", "1", "-i", pcm,
                           "-c:a", "libmp3lame", "-b:a", "192k", mp3])
    os.remove(pcm)
    return cumle_zamanla(mp3, metin)


def _sade(m):
    m = m.lower().replace("i̇", "i")
    return re.sub(r"[^a-zçğıöşü0-9 ]", " ", m).split()


def baslangic_dogrula(mp3, metin, saniye=12):
    """Sesin ilk saniyelerini yazıya döktürüp metnin başıyla karşılaştırır.
    Ses, metinde olmayan bir şeyle başlıyorsa (ör. talimat okunmuşsa) False döner.
    Doğrulama servisine ulaşılamazsa None döner (üretimi engellemez)."""
    kesit = mp3 + ".kesit.mp3"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-t", str(saniye), "-ac", "1",
                           "-ar", "16000", kesit])
    govde = json.dumps({"contents": [{"parts": [
        {"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(open(kesit, "rb").read()).decode()}},
        {"text": "Bu Türkçe ses kaydını kelimesi kelimesine yazıya dök. Sadece metni yaz."}]}]}).encode()
    os.remove(kesit)
    try:
        istek = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{DOGRULAMA_MODELI}:generateContent",
            govde, {"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
        with urllib.request.urlopen(istek, timeout=120) as y:
            yazi = json.load(y)["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as hata:
        print(f"  uyarı: başlangıç doğrulaması yapılamadı ({hata.__class__.__name__})", flush=True)
        return None
    # sayılar rakamla ya da yazıyla dökülebildiği için karşılaştırma dışı
    sayisiz = lambda ks: [k for k in ks if not k.isdigit()]
    duyulan, beklenen = sayisiz(_sade(yazi))[:3], sayisiz(_sade(metin))[:12]
    # duyulan ilk kelimeler metnin başında geçmeli (talimat okunduysa geçmez)
    tamam = len(duyulan) > 0 and all(k in beklenen for k in duyulan)
    if not tamam:
        print(f"  ses doğrulaması başarısız. Duyulan: {yazi[:80]!r}", flush=True)
    return tamam


def edge_seslendir(metin, mp3, ses="tr-TR-EmelNeural", hiz="+0%"):
    import edge_tts
    from edge_tts import communicate
    ca = os.environ.get("SSL_CERT_FILE")
    if ca and os.path.exists(ca):
        communicate._SSL_CTX = ssl.create_default_context(cafile=ca)

    async def _calis():
        c = edge_tts.Communicate(metin, ses, rate=hiz, boundary="SentenceBoundary")
        satirlar = []
        with open(mp3, "wb") as f:
            async for p in c.stream():
                if p["type"] == "audio":
                    f.write(p["data"])
                elif p["type"] == "SentenceBoundary":
                    t0 = p["offset"] / 1e7
                    satirlar.append((t0, t0 + p["duration"] / 1e7, p["text"]))
        return satirlar

    for k in range(5):
        try:
            return asyncio.run(_calis())
        except Exception:
            if k == 4:
                raise
            time.sleep(2 * (k + 1))
