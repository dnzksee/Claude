"""Ses: özgün müzik ve efekt sentezi (telifsiz, kodla üretilir) ve miksaj.

- muzik(sure): merak uyandıran belgesel altlığı (pad + pluck arpej + bas + hafif ritim), 8 ölçülük döngü.
- efekt(ad): whoosh, punch, iris, pop, ding, bzzt, boing, tik, zil, alkis, swoosh_yukari.
- miksaj(...): seslendirme + efektler + müzik; müzik konuşma altında otomatik kısılır (ducking).
"""
import math
import subprocess

import numpy as np

SR = 44100


def _zarf(n, atak=0.01, birak=0.2):
    e = np.ones(n)
    a, b = int(atak * SR), int(birak * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if b:
        e[-b:] *= np.linspace(1, 0, b)
    return e


def _alcak_geciren(x, kesim):
    """Tek kutuplu alçak geçiren (yumuşak tını)."""
    a = math.exp(-2 * math.pi * kesim / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):  # efektler kısa; döngü yeterince hızlı
        s = (1 - a) * x[i] + a * s
        y[i] = s
    return y


def _lp_hizli(x, kesim):
    """Uzun sinyaller için FFT tabanlı yumuşak alçak geçiren."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / kesim) ** 4)
    return np.fft.irfft(X, len(x))


def _nota(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def _pluck(f, sure, parlak=0.5):
    """Karplus-Strong telli çalgı."""
    n = int(sure * SR)
    p = max(2, int(SR / f))
    rnd = np.random.default_rng(int(f * 10))
    tampon = rnd.uniform(-1, 1, p)
    cikis = np.empty(n)
    for i in range(n):
        v = tampon[i % p]
        cikis[i] = v
        tampon[i % p] = 0.5 * (v + tampon[(i + 1) % p]) * (0.994 + 0.004 * parlak)
    return cikis * _zarf(n, 0.002, 0.05)


def muzik(sure, bpm=88, ton=57, seviye=1.0):
    """ton: kök nota (MIDI; 57 = La). Akor dizisi: i - VI - III - VII (La minör: Am F C G)."""
    vurus = 60.0 / bpm
    olcu = 4 * vurus
    akorlar = [(0, 3, 7), (-4, 0, 3), (3, 7, 10), (-2, 2, 5)]  # Am, F, C, G (köke göre)
    dongu_n = int(8 * olcu * SR)
    t = np.arange(dongu_n) / SR
    dongu = np.zeros(dongu_n)
    rnd = np.random.default_rng(3)
    for o in range(8):
        akor = akorlar[(o // 2) % 4]
        bas_i = int(o * olcu * SR)
        uz = int(olcu * SR)
        tt = t[:uz]
        zarf = _zarf(uz, 0.35, 0.4)
        # pad: hafif akortsuz sinüs katmanları
        pad = np.zeros(uz)
        for ar in akor:
            f = _nota(ton + ar)
            for d in (-0.15, 0.15):
                pad += np.sin(2 * np.pi * f * (1 + d / 100) * tt) * 0.5
                pad += np.sin(2 * np.pi * 2 * f * (1 + d / 100) * tt) * 0.12
        dongu[bas_i:bas_i + uz] += pad * zarf * 0.05
        # bas: 1. ve 3. vuruş
        for v in (0, 2):
            b0 = bas_i + int(v * vurus * SR)
            bn = int(vurus * 1.6 * SR)
            f = _nota(ton - 12 + akor[0])
            bt = np.arange(bn) / SR
            dongu[b0:b0 + bn] += np.sin(2 * np.pi * f * bt) * np.exp(-bt * 2.5) * 0.22
        # pluck arpej (sekizlikler)
        sira = [0, 1, 2, 1, 2, 0, 1, 2]
        for k in range(8):
            p0 = bas_i + int(k * vurus / 2 * SR)
            ar = akor[sira[k]] + (12 if k in (3, 6) else 0)
            sn = _pluck(_nota(ton + 12 + ar), vurus * 1.2)
            son = min(len(dongu), p0 + len(sn))
            dongu[p0:son] += sn[:son - p0] * 0.09 * (0.8 + 0.2 * rnd.random())
        # ritim: yumuşak davul ve hi-hat
        for v in range(4):
            k0 = bas_i + int(v * vurus * SR)
            kn = int(0.25 * SR)
            kt = np.arange(kn) / SR
            if v in (0, 2):
                dongu[k0:k0 + kn] += np.sin(2 * np.pi * (50 + 70 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.25
            h0 = k0 + int(vurus / 2 * SR)
            hn = int(0.05 * SR)
            if h0 + hn < len(dongu):
                dongu[h0:h0 + hn] += rnd.uniform(-1, 1, hn) * np.exp(-np.arange(hn) / SR * 90) * 0.025
    dongu = _lp_hizli(dongu, 5000)
    n = int(sure * SR)
    tekrar = int(math.ceil(n / dongu_n)) + 1
    m = np.tile(dongu, tekrar)[:n]
    m *= _zarf(n, 1.5, 3.0)
    m /= max(np.abs(m).max(), 1e-6)
    return m * 0.5 * seviye


# ---------------------------------------------------------------- efektler
def efekt(ad):
    rnd = np.random.default_rng(abs(hash(ad)) % 2 ** 32)
    if ad == "whoosh":  # yumuşak rüzgâr/hava hışırtısı (tizler kesik, cızırtı yok)
        n = int(0.6 * SR)
        g = rnd.uniform(-1, 1, n)
        t = np.arange(n) / SR
        zarf = np.sin(np.pi * t / t[-1]) ** 3
        a = _alcak_geciren(_alcak_geciren(g, 500), 700)
        return a / max(np.abs(a).max(), 1e-6) * zarf * 0.35
    if ad == "punch":
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        thump = np.sin(2 * np.pi * (45 + 120 * np.exp(-t * 25)) * t) * np.exp(-t * 9)
        tik = rnd.uniform(-1, 1, n) * np.exp(-t * 80) * 0.5
        return (thump + tik) * 0.9
    if ad == "iris":
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        f = 300 + 900 * (t / t[-1]) ** 2
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) * 0.35
    if ad == "pop":
        n = int(0.14 * SR)
        t = np.arange(n) / SR
        f = 900 * np.exp(-t * 18) + 380
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * 0.55
    if ad == "ding":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in
                ((1318, 0.5, 3), (2637, 0.25, 5), (3951, 0.12, 8), (1975, 0.15, 4)))
        return s * _zarf(n, 0.003, 0.2) * 0.8
    if ad == "bzzt":  # yumuşak "yanlış" tonu (iki inen nota)
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        f = np.where(t < 0.22, 330.0, 247.0)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * _zarf(n, 0.01, 0.15) * 0.3
    if ad == "boing":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = 180 + 260 * (t / t[-1]) + 40 * np.sin(2 * np.pi * 14 * t)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.5
    if ad == "tik":
        n = int(0.05 * SR)
        return rnd.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR * 120) * 0.5
    if ad == "zil":
        n = int(1.4 * SR)
        t = np.arange(n) / SR
        zil = np.sin(2 * np.pi * 2200 * t) * (np.sin(2 * np.pi * 22 * t) > 0)
        return _alcak_geciren(zil, 3000) * _zarf(n, 0.01, 0.3) * 0.3
    if ad == "swoosh_yukari":  # yumuşak yükselen nefes (ton süpürmesi yok)
        n = int(0.5 * SR)
        g = rnd.uniform(-1, 1, n)
        t = np.arange(n) / SR
        a = _alcak_geciren(g, 400) * (1 - t / t[-1]) + _alcak_geciren(g, 1200) * (t / t[-1])
        return a / max(np.abs(a).max(), 1e-6) * np.sin(np.pi * t / t[-1]) ** 2 * 0.25
    if ad == "kilic_sesi":  # kılıç çarpışması: inharmonik metal tını + vuruş
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in
                ((1870, 0.5, 9), (2930, 0.35, 12), (4410, 0.2, 16), (6020, 0.1, 22)))
        vurus = _alcak_geciren(rnd.uniform(-1, 1, n), 3000) * np.exp(-t * 60)
        return (s + vurus * 0.6) * 0.45
    if ad == "kalabalik":  # uzaktan savaş uğultusu
        n = int(4.0 * SR)
        t = np.arange(n) / SR
        g = _lp_hizli(rnd.uniform(-1, 1, n), 350)
        g /= max(np.abs(g).max(), 1e-6)
        mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t) * np.sin(2 * np.pi * 0.23 * t + 1)
        return g * mod * _zarf(n, 0.8, 1.2) * 0.5
    if ad == "ok":  # tek okun vızıltısı
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        g = _alcak_geciren(rnd.uniform(-1, 1, n), 1500)
        return g / max(np.abs(g).max(), 1e-6) * np.sin(np.pi * t / t[-1]) ** 2 * 0.3
    if ad == "alkis":
        n = int(1.6 * SR)
        s = np.zeros(n)
        for _ in range(60):
            p = int(rnd.uniform(0, n - 3000))
            m = 2000
            s[p:p + m] += rnd.uniform(-1, 1, m) * np.exp(-np.arange(m) / SR * 160) * rnd.uniform(0.3, 1)
        return _alcak_geciren(s, 5000) * _zarf(n, 0.05, 0.6) * 0.5
    if ad == "kayit":  # daktilo/kalem tıkırtısı dizisi
        n = int(1.0 * SR)
        s = np.zeros(n)
        for k in range(9):
            p = int(k * 0.1 * SR + rnd.uniform(0, 0.03) * SR)
            m = 900
            if p + m < n:
                s[p:p + m] += rnd.uniform(-1, 1, m) * np.exp(-np.arange(m) / SR * 200)
        return s * 0.35
    raise KeyError(f"bilinmeyen efekt: {ad}")


# ---------------------------------------------------------------- miksaj
def kis_zarfi(sure, konusmalar, alt=0.22, atak=0.25, birak=1.6, pay=0.25, birlestir=1.6):
    """Müzik kazancı: konuşma sırasında 'alt' seviyeye iner, uzun aralarda yavaşça yükselir.
    birlestir: bundan kısa duraklamalarda müzik kısık kalır (cümle aralarında 'pompalama' olmasın)."""
    n = int(sure * SR)
    hedef = np.ones(n)
    birlesik = []
    for t0, t1 in sorted(konusmalar):
        if birlesik and t0 - birlesik[-1][1] < birlestir:
            birlesik[-1][1] = max(birlesik[-1][1], t1)
        else:
            birlesik.append([t0, t1])
    for t0, t1 in birlesik:
        a, b = max(0, int((t0 - pay) * SR)), min(n, int((t1 + pay) * SR))
        hedef[a:b] = alt
    # asimetrik yumuşatma: iniş hızlı, çıkış yavaş (blok blok, vektörel)
    kucuk = hedef[::441]  # 10 ms çözünürlük
    cikis = np.empty_like(kucuk)
    s = 1.0
    ka, kb = math.exp(-0.01 / atak), math.exp(-0.01 / birak)
    for i, h in enumerate(kucuk):
        k = ka if h < s else kb
        s = h + (s - h) * k
        cikis[i] = s
    return np.interp(np.arange(n), np.arange(len(cikis)) * 441, cikis)


def miksaj(sure, vo, konusmalar, efektler, muzik_seviye=0.22, efekt_seviye=0.45, cikis_wav=None):
    """vo: SR örnekli mono dizi (zaman çizelgesine yerleşmiş). efektler: [(t, ad, kazanc)].
    Müzik ve efektler konuşma altında kısılır; anlatıcı her zaman öndedir."""
    n = int(sure * SR)
    ses = np.zeros(n)
    v = vo[:n]
    tepe = max(np.abs(v).max(), 1e-6)
    ses[:len(v)] += v / tepe * 0.85
    kis = kis_zarfi(sure, konusmalar)
    ses += muzik(sure) * muzik_seviye * kis
    fx = np.zeros(n)
    for t, ad, kazanc in efektler:
        e = efekt(ad) * kazanc
        a = int(t * SR)
        if a >= n:
            continue
        b = min(n, a + len(e))
        fx[a:b] += e[:b - a]
    # efektler de konuşma altında yarıya iner; ani tepeler yumuşak sınırlanır
    fx = np.tanh(fx * 1.5) / 1.5
    ses += fx * efekt_seviye * (0.5 + 0.5 * (kis - 0.22) / 0.78)
    ses = np.tanh(ses * 1.1) / math.tanh(1.1)  # yumuşak sınırlayıcı
    sol = ses
    sag = np.concatenate([np.zeros(int(0.012 * SR)), ses])[:n] * 0.15 + ses * 0.85  # hafif genişlik
    stereo = np.stack([sol, sag], axis=1)
    if cikis_wav:
        veri = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        cikis_wav], input=veri.tobytes(), check=True)
    return stereo


def ses_oku(yol):
    """Herhangi bir ses dosyasını SR mono float dizisine çevirir."""
    ham = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", yol, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(ham, np.float32).astype(np.float64)
