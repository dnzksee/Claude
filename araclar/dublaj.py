"""Kroniknâme çok dilli seslendirme hattı (Gemini TTS, ses Kore).

Kullanım:  python3 dublaj.py <calisma_klasoru> <dil> <DilAdi> uret|kontrol|onar|birlestir|hepsi
Çalışma klasöründe olması gerekenler:
  <dil>.py   KANCA=(okunan, altyazı|None), CUMLE=[(okunan, altyazı|None), ...], GRUPLAR=[grup başı indeksleri]
  tr.srt     Türkçe videonun altyazısı: 1. satır kanca, sonra her cümle (zamanlama buradan alınır)
  arka.wav   müzik/efekt katmanı (demucs no_vocals), vokal.wav (demucs vocals; ses seviyesi için)
Çıktılar: ses_<dil>/NN.wav (00 = kanca), kontrol_<dil>.json, <ad>_<dil>_ses.mp3, altyazi_<dil>.srt
Sadece ana TTS modeli kullanılır (yedek modeller daha ince sesle okuyor). Günlük kota dolunca KotaBitti ile durur;
aynı komut ertesi gün kaldığı yerden devam eder (var olan cümleler yeniden okunmaz).
"""
import base64, difflib, importlib.util, json, os, re, subprocess, sys, time
import numpy as np
import requests
import soundfile as sf

ANAHTAR = os.environ["GEMINI_API_KEY"].replace("buraya_yeni_anahtar", "").strip().strip("'\"=").strip()  # ortamda kalan yer tutucuyu temizle
TTS = "gemini-3.8-flash-tts"
METIN_MODEL = "gemini-3.8-flash"
METIN_YEDEK = "gemini-3.5-flash"   # yalnızca yazıya dökme kontrolü için
SR = 24000
ESIK = 0.85
URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"


class KotaBitti(Exception):
    pass


class KrediBitti(Exception):
    pass


_son = [0.0]


def _post(model, body, aralik=0.0):
    bekle = _son[0] + aralik - time.time()
    if bekle > 0:
        time.sleep(bekle)
    for deneme in range(8):
        _son[0] = time.time()
        try:
            r = requests.post(URL.format(model), json=body, headers={"x-goog-api-key": ANAHTAR}, timeout=300)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            time.sleep(15)   # ağ/zaman aşımı: yeniden dene
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            if re.search(r'"quotaId":\s*"[^"]*PerDay', r.text) and not re.search(r'"quotaId":\s*"[^"]*PerMinute', r.text):
                raise KotaBitti(f"{model}: günlük kota doldu")
            time.sleep(20 + 10 * deneme)
            continue
        if r.status_code == 402:
            raise KrediBitti(f"{model}: Gemini ön ödemeli kredi bitti (AI Studio'dan yüklenmeli)")
        if r.status_code >= 500:
            if model != TTS and deneme >= 2:
                break
            time.sleep(10)
            continue
        raise RuntimeError(f"{model} {r.status_code}: {r.text[:300]}")
    raise RuntimeError(f"{model}: çok fazla deneme")


def _sayac():
    """Bu makinede bugün yapılan TTS istek sayısı. TTS_SINIR aşılırsa durur (Türkçe videolara kota bırakmak için)."""
    # Gemini günlük kotası Pasifik saatiyle gece yarısı (≈08:00 UTC) sıfırlanır; sayaç da o güne göre tutulur
    from datetime import datetime
    from zoneinfo import ZoneInfo
    gun = datetime.now(ZoneInfo("America/Los_Angeles")).strftime('%Y-%m-%d')
    yol = os.path.expanduser(f"~/.tts_sayac_pt_{gun}")
    n = int(open(yol).read()) if os.path.exists(yol) else 0
    if n >= int(os.environ.get("TTS_SINIR", "60")):
        raise KotaBitti(f"günlük dublaj sınırı ({n} istek) doldu; kalan kota Türkçe videolara")
    open(yol, "w").write(str(n + 1))


def tts(metin, diladi):
    _sayac()
    stil = (f"Read the following in {diladi} like a very excited, energetic documentary narrator, "
            "full of wonder and amazement:\n")
    body = {"contents": [{"parts": [{"text": stil + metin}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}}}
    d = _post(TTS, body, aralik=6.5)
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return np.frombuffer(base64.b64decode(p["inlineData"]["data"]), dtype="<i2").astype(np.float32) / 32768
    raise RuntimeError("TTS yanıtında ses yok")


def dokum(x, diladi):
    """Gemini ile yazıya dökme (kontrol için)."""
    import io
    if len(x) < 0.3 * SR:
        return ""
    b = io.BytesIO(); sf.write(b, x, SR, format="WAV", subtype="PCM_16")
    istem = (f"Transcribe this {diladi} audio exactly, written in the standard {diladi} script "
             "(Urdu in Urdu/Arabic script, never Devanagari). Write numbers as digits. Output only the transcription.")
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(b.getvalue()).decode()}},
                                    {"text": istem}]}]}
    try:
        d = _post(METIN_MODEL, body, aralik=1.0)
    except RuntimeError:   # ana metin modeli yoğun (503): yalnızca kontrol için yedek modele geç (TTS değişmez)
        d = _post(METIN_YEDEK, body, aralik=1.0)
    try:
        return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"]).strip()
    except (KeyError, IndexError):
        return ""


norm = lambda t: re.sub(r"[\W_]", "", t.lower())
benz = lambda a, b: difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()

_wm = [None]


def kelimeler(x, dil, ipucu):
    from faster_whisper import WhisperModel
    if _wm[0] is None:
        _wm[0] = WhisperModel(os.environ.get("WHISPER", "medium"), device="cpu", compute_type="int8")
    x16 = np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)  # Whisper 16 kHz ister
    segs, _ = _wm[0].transcribe(x16, language=dil, word_timestamps=True, beam_size=5, initial_prompt=(ipucu[:200] if dil == "ur" else None),
                                vad_filter=True, vad_parameters={"min_silence_duration_ms": 300}, condition_on_previous_text=False)
    return [(w.start, w.end, w.word) for s in segs for w in (s.words or [])]


def enerji(x, a, b):
    """[a,b] sn aralığındaki en sessiz 20 ms'nin ortası."""
    i0, i1 = max(0, int(a * SR)), min(len(x), int(b * SR))
    if i1 - i0 < 480:
        return (a + b) / 2
    f = 480
    e = [np.sqrt(np.mean(x[i:i + f] ** 2)) for i in range(i0, i1 - f, 120)]
    return (i0 + int(np.argmin(e)) * 120 + f / 2) / SR


def bol(x, cumleler, dil):
    """Grup sesini cümlelere böler: Whisper kelime zamanları + karakter hizalama. Baştaki/sondaki fazlalık atılır."""
    w = kelimeler(x, dil, " ".join(cumleler))
    hyp, hw = "", []
    for k, (_, _, t) in enumerate(w):
        n = norm(t); hyp += n; hw += [k] * len(n)
    ref, rbas = "", []
    for c in cumleler:
        rbas.append(len(ref)); ref += norm(c)
    rbas.append(len(ref))
    esle = {}
    for a, b, n in difflib.SequenceMatcher(None, hyp, ref, autojunk=False).get_matching_blocks():
        if n < 3:          # tek tük harf eşleşmeleri (okunan talimat vb.) sınırları kaydırmasın
            continue
        for j in range(n):
            esle[b + j] = a + j
    if len(esle) < 0.6 * len(ref):
        raise ValueError(f"hizalama zayıf ({len(esle)}/{len(ref)})")
    bas_t, son_t = [], []
    for i in range(len(cumleler)):
        r0, r1 = rbas[i], rbas[i + 1] - 1
        ileri = [esle[r] for r in range(r0, r1 + 1) if r in esle]
        if not ileri:
            raise ValueError(f"cümle {i} bulunamadı")
        bas_t.append(w[hw[ileri[0]]][0]); son_t.append(w[hw[ileri[-1]]][1])
    kes = [max(0.0, bas_t[0] - 0.12)]
    for i in range(len(cumleler) - 1):
        a, b = son_t[i], max(son_t[i] + 0.02, bas_t[i + 1])
        kes.append(enerji(x, a - 0.05, b + 0.05))
    kes.append(min(len(x) / SR, son_t[-1] + 0.35))
    return [kirp(x[int(kes[i] * SR):int(kes[i + 1] * SR)]) for i in range(len(cumleler))]


def kirp(x, esik=0.012):
    f = 240
    if len(x) < 2 * f:
        return x
    e = np.array([np.sqrt(np.mean(x[i:i + f] ** 2)) for i in range(0, len(x) - f, f)])
    ses = np.where(e > esik)[0]
    if not len(ses):
        return x
    a = max(0, ses[0] * f - int(0.04 * SR)); b = min(len(x), (ses[-1] + 1) * f + int(0.08 * SR))
    return x[a:b]


def srt_oku(yol):
    bloklar = re.split(r"\n\s*\n", open(yol, encoding="utf-8").read().strip())
    zs = []
    for b in bloklar:
        m = re.search(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", b)
        if m:
            g = list(map(int, m.groups()))
            zs.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000))
    return zs


def srt_zaman(t):
    ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


class Proje:
    def __init__(self, P, dil, diladi):
        self.P, self.dil, self.diladi = P, dil, diladi
        spec = importlib.util.spec_from_file_location(dil, f"{P}/{dil}.py")
        E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
        self.E = E
        self.metin = [E.KANCA[0]] + [s for s, _ in E.CUMLE]
        self.alt = [E.KANCA[1] or E.KANCA[0]] + [a or s for s, a in E.CUMLE]
        self.zs = srt_oku(f"{P}/tr.srt")
        assert len(self.zs) == len(self.metin), f"tr.srt {len(self.zs)} satır, metin {len(self.metin)}"
        self.sure = sf.info(f"{P}/arka.wav").duration
        self.bas = [a for a, _ in self.zs] + [self.sure - 0.5]
        self.d = f"{P}/ses_{dil}"; os.makedirs(self.d, exist_ok=True)
        self.kf = f"{P}/kontrol_{dil}.json"
        self.kontrol_v = json.load(open(self.kf)) if os.path.exists(self.kf) else {}

    yol = lambda s, k: f"{s.d}/{k:02d}.wav"
    pencere = lambda s, k: s.bas[k + 1] - s.bas[k] - 0.1
    oku = lambda s, k: sf.read(s.yol(k), dtype="float32")[0]

    def uret(self):
        kes = [0] + [g + 1 for g in self.E.GRUPLAR[1:]] + [len(self.metin)]   # kanca grup 0'a eklenir
        for g in range(len(kes) - 1):
            ks = list(range(kes[g], kes[g + 1]))
            if all(os.path.exists(self.yol(k)) for k in ks):
                continue
            for deneme in range(int(os.environ.get("GRUP_DENEME", "2"))):  # ücretsiz kotada (10/gün) boşa harcamamak için 2
                ham = f"{self.d}/ham{g}.wav"
                if deneme == 0 and os.path.exists(ham):
                    x = sf.read(ham, dtype="float32")[0]
                else:
                    x = tts("\n\n".join(self.metin[k] for k in ks), self.diladi); sf.write(ham, x, SR)
                try:
                    parcalar = bol(x, [self.metin[k] for k in ks], self.dil)
                    break
                except ValueError as e:
                    print(f"  grup {g}: bölme başarısız ({e}), yeniden", flush=True)
            else:
                print(f"  grup {g}: atlandı", flush=True); continue
            for k, p in zip(ks, parcalar):
                sf.write(self.yol(k), p, SR)
            print(f"{self.dil} grup {g} tamam ({len(ks)} cümle)", flush=True)

    def kontrol(self, hepsi=False):
        for k in range(len(self.metin)):
            if not os.path.exists(self.yol(k)):
                self.kontrol_v[str(k)] = [0.0, "(yok)"]; continue
            if not hepsi and str(k) in self.kontrol_v and self.kontrol_v[str(k)][0] >= ESIK:
                continue
            d = dokum(self.oku(k), self.diladi)
            self.kontrol_v[str(k)] = [round(benz(self.metin[k], d), 3), d]
        json.dump(self.kontrol_v, open(self.kf, "w"), ensure_ascii=False, indent=1)
        return self.kotu()

    def kotu(self):
        out = []
        for k in range(len(self.metin)):
            r = self.kontrol_v.get(str(k), [0, ""])[0]
            uzun = os.path.exists(self.yol(k)) and len(self.oku(k)) / SR > self.pencere(k) + 0.8
            if r < ESIK or uzun:
                out.append(k)
        return out

    def onar(self):
        kotu = self.kotu()
        if len(kotu) > 12:     # bu kadar çok sorun bölmede hata demektir; kotayı tek tek onarımla harcama
            raise RuntimeError(f"{self.dil}: {len(kotu)} sorunlu cümle, önce üretimi kontrol et: {kotu}")
        for k in kotu:
            en = None
            if os.path.exists(self.yol(k)):
                y = self.oku(k); en = (self.kontrol_v[str(k)][0] - max(0, len(y) / SR - self.pencere(k) - 0.4) * 0.1, y, self.kontrol_v[str(k)])
            for deneme in range(2):
                try:
                    x = tts(self.metin[k], self.diladi)
                    y = bol(x, [self.metin[k]], self.dil)[0]
                except ValueError:
                    continue
                d = dokum(y, self.diladi); r = benz(self.metin[k], d)
                skor = r - max(0, len(y) / SR - self.pencere(k) - 0.4) * 0.1
                if en is None or skor > en[0]:
                    en = (skor, y, [round(r, 3), d])
                if r >= 0.92 and len(y) / SR <= self.pencere(k) + 0.4:
                    break
            if en:
                sf.write(self.yol(k), en[1], SR); self.kontrol_v[str(k)] = en[2]
                json.dump(self.kontrol_v, open(self.kf, "w"), ensure_ascii=False, indent=1)
                print(f"  {k}: {en[2][0]:.2f} {len(en[1]) / SR:.1f}/{self.pencere(k):.1f} sn | {en[2][1][:60]}", flush=True)

    def birlestir(self, ad):
        arka, sr = sf.read(f"{self.P}/arka.wav", dtype="float32")
        vokal, _ = sf.read(f"{self.P}/vokal.wav", dtype="float32")
        v = vokal.mean(1) if vokal.ndim > 1 else vokal
        hedef = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
        ses = np.zeros(len(arka), np.float32)
        srt, son, gec = [], 0.0, []
        for k in range(len(self.metin)):
            y = self.oku(k)
            y = np.interp(np.arange(0, len(y), SR / sr), np.arange(len(y)), y).astype(np.float32)
            L = len(y) / sr
            t = self.bas[k]
            if L > self.pencere(k):
                t -= min(0.4, L - self.pencere(k))
            t = max(t, son + 0.15)
            if t > self.bas[k] + 0.05:
                gec.append((k, round(t - self.bas[k], 2)))
            i = int(t * sr); y = y[: max(0, len(ses) - i)]
            ses[i:i + len(y)] += y
            son = t + L
            srt.append(f"{k + 1}\n{srt_zaman(t)} --> {srt_zaman(min(son, self.sure))}\n{self.alt[k]}\n")
        s = np.sqrt(np.mean(ses[np.abs(ses) > 0.02] ** 2))
        ses *= hedef / s
        mix = arka + (ses[:, None] if arka.ndim > 1 else ses)
        mix /= max(1.0, np.abs(mix).max() / 0.98)
        tmp = f"{self.P}/_mix_{self.dil}.wav"; sf.write(tmp, mix, sr)
        cikti = f"{self.P}/{ad}_{self.dil}_ses.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:a", "libmp3lame", "-b:a", "192k", cikti], check=True)
        os.remove(tmp)
        open(f"{self.P}/altyazi_{self.dil}.srt", "w", encoding="utf-8").write("\n".join(srt))
        print(f"{self.dil}: {cikti} | gecikme (cümle, sn): {gec} en fazla {max([g for _, g in gec], default=0)}", flush=True)


if __name__ == "__main__":
    P, dil, diladi, is_ = sys.argv[1:5]
    pr = Proje(P, dil, diladi)
    ad = os.path.basename(os.path.abspath(P))
    try:
        if is_ in ("uret", "hepsi"):
            pr.uret()
        if is_ in ("kontrol", "hepsi"):
            print(f"{dil}: kontrol sonrası sorunlu: {pr.kontrol()}", flush=True)
        if is_ in ("onar", "hepsi"):
            pr.onar(); print(f"{dil}: onar sonrası sorunlu: {pr.kotu()}", flush=True)
        if is_ in ("birlestir", "hepsi"):
            pr.birlestir(ad)
    except KotaBitti as e:
        print("KOTA:", e, flush=True); sys.exit(3)
    except KrediBitti as e:
        print("KREDI:", e, flush=True); sys.exit(4)
