"""Umay ile Zıpzıp, 1. Bölüm: "Renkli Kelebekler" (≈20 dk), kâğıt kesme.

Senaryo: senaryo_renkli_kelebekler.py (metin ve sahne sırası)
Bu dosya: istasyonlar (her sahnenin dünyadaki yeri), kamera, oyunculuk, nesne animasyonları,
büyük renk yazıları, dans araları, müzik ve efektler. Zamanlama seslendirme sürelerinden otomatik çıkar;
yeni ses kaydı gelince yeniden çalıştırmak yeterli.

    python3 ep1_renkli_kelebekler.py --plan                 # zaman çizelgesini yazdır
    python3 ep1_renkli_kelebekler.py --still 95 300         # kare önizleme
    python3 ep1_renkli_kelebekler.py --scale 0.5 --start 0 --end 120   # hızlı taslak
    python3 ep1_renkli_kelebekler.py                         # tam bölüm
"""
import argparse
import math
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import cairo
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.core import W, H, FPS, GROUND_Y, clamp, lerp, smooth, ease_io, ease_out_back, window, hash01, circle, ellipse, hexrgb
from engine.styles import Canvas, PAINTERS, PAPER, post_process
from engine.characters import PAL, draw_umay, draw_zipzip, draw_butterfly, draw_flower, draw_sparkles, umay_arm_pose, blend_pose, star
from engine import props as P
from engine import world
from senaryo_renkli_kelebekler import BOLUMLER, A, U, Z

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_DIR = os.path.join(ROOT, "assets", "vo_ep1")
STYLE = "kagit"
SPAN = 11900
WALK_V = 135.0          # Umay'ın yürüyüş hızı (px/sn): 3 yaşına uygun, sakin
STRIDE_W = 140.0        # yürüyüş adım döngüsü (px); karakter çiziminde de aynısı kullanılır
GAP = 0.55              # cümleler arası boşluk
DANCE_LEN = 48.0        # her renk sonundaki dans arası (tekerleme 2 kez)
SONG_LEN = 30.0         # açılış şarkısı
RECAP_PER = 20.0        # finalde her renk için "hatırlayalım"
FINAL_DANCE = 24.0      # gökkuşağı dansı
TARGET = 0              # hedef süre (sn); 0 = doldurma yok (sessiz beklemeler çocukları sıkıyordu)

BF_COL = {"mavi": (P.COL["mavi"], P.COL["mavi_l"]), "kirmizi": (P.COL["kirmizi"], P.COL["kirmizi_l"]),
          "sari": (P.COL["sari"], P.COL["turuncu"])}
REN = {"mavi": "mavi", "kırmızı": "kirmizi", "sarı": "sari"}

# ---------------------------------------------------------------- dünyadaki nesneler (x konumları)
HOUSE_X = 300
FLOWERS = [(2250, 848), (2335, 852), (2420, 848)]
STREAM = (3000, 3620, 965)
TREE_BIRD = 4060
BIRD = (4000, 560)
BUSH = (4860, 875)
BALL0 = (4790, 878)
APPLE_TREE = (6260, 860)
APPLES = [(-70, -300, 24), (80, -270, 24), (10, -370, 24), (-120, -220, 22)]
LADYBUG = (6930, 868)
STRAW = (7570, 885)
FAR_HOUSE = (7980, 770)
SUNFLOWER = (9170, 872)
CHICK0 = 9175
PICNIC = (9980, 905)
RAINBOW = (10720, 860, 470)

# istasyon: Umay'ın durduğu x, kamera (dx, cy, zoom), odak (kelebek/gözler), kelebek davranışı, ön/son süreler
SC = {
    "A1": dict(x=HOUSE_X + 20, cam=(160, 150, 1.0), pre=SONG_LEN, post=0.8, song=True),
    "A2": dict(x=HOUSE_X + 230, cam=(-40, 560, 1.12), pre=4.0, post=2.0),
    "A3": dict(x=980, cam=(140, 560, 1.0), pre=1.0, post=2.5),
    "M1": dict(x=1500, cam=(160, 540, 1.0), focus=(1720, 600), bf="hover", pre=3.0, post=2.5),
    "M2": dict(x=1500, cam=(220, 230, 1.0), focus=(1760, 300), bf="hover", up=True, pre=2.0, post=2.5),
    "M3": dict(x=2110, cam=(200, 640, 1.35), focus=(2335, 730), bf="land", pre=2.0, post=3.0),
    "M4": dict(x=2920, cam=(240, 610, 1.12), focus=(3160, 900), bf="hover", pre=2.0, post=3.5),
    "M5": dict(x=3820, cam=(200, 470, 1.15), focus=BIRD, bf="hover", pre=2.0, post=3.5),
    "M6": dict(x=4600, cam=(330, 600, 1.0), focus=(4860, 820), bf="hover", pre=2.0, post=3.0),
    "M7": dict(x=4600, cam=(140, 560, 1.0), focus=None, bf="dance", pre=1.0, post=3.0, dance_after="M34", away_after="M36"),
    "K1": dict(x=5450, cam=(160, 540, 1.0), focus=(5680, 600), bf="hover", pre=3.0, post=2.5),
    "K2": dict(x=6040, cam=(200, 520, 1.1), focus=(6270, 520), bf="land", pre=2.0, post=3.0),
    "K3": dict(x=6040, cam="collar", focus="collar", bf="land", pre=1.5, post=2.5),
    "K4": dict(x=6720, cam=(210, 790, 2.0), focus=(6930, 805), bf="hover", pre=2.0, post=3.0),
    "K5": dict(x=7380, cam=(170, 700, 1.3), focus=(7570, 840), bf="hover", pre=2.0, post=3.0),
    "K6": dict(x=7380, cam=(420, 600, 1.05), focus=(FAR_HOUSE[0], FAR_HOUSE[1] - 110), bf="hover", pre=1.5, post=2.5),
    "K7": dict(x=7380, cam=(140, 560, 1.0), focus=None, bf="dance", pre=1.0, post=3.0, dance_after="K31", away_after="K33"),
    "S1": dict(x=8350, cam=(160, 540, 1.0), focus=(8580, 600), bf="hover", pre=3.0, post=2.5),
    "S2": dict(x=8350, cam=(260, 230, 1.0), focus="sun", bf="hover", up=True, pre=2.0, post=2.5),
    "S3": dict(x=8350, cam="ribbon", focus="ribbon", bf="land", pre=1.5, post=2.5),
    "S4": dict(x=8980, cam=(190, 560, 1.1), focus=(SUNFLOWER[0], SUNFLOWER[1] - 300), bf="hover", pre=2.0, post=3.0),
    "S5": dict(x=8980, cam=(220, 650, 1.25), focus="chick", bf="hover", pre=1.5, post=3.0),
    "S6": dict(x=9800, cam=(160, 640, 1.25), focus=(PICNIC[0] + 30, PICNIC[1] - 90), bf="hover", pre=2.0, post=3.0),
    "S7": dict(x=9800, cam=(140, 560, 1.0), focus=None, bf="dance", pre=1.0, post=3.0, dance_after="S33", away_after="S35"),
    "F1": dict(x=10600, cam=(120, 520, 1.0), focus=None, bf="final", pre=4.0, post=2.5),
    "F2": dict(x=10600, cam=(120, 500, 1.0), focus=None, bf="final", pre=1.5, post=5.0, recap_after="F09", dance_after="F12"),
    "F3": dict(x=10600, cam=(90, 640, 1.3), focus=None, bf="final", pre=0.5, post=6.5, end=True),
}


def vo_path(cid):
    return os.path.join(VO_DIR, f"{cid}.wav")


LOCK_PATH = os.path.join(ROOT, "build", "ep1_slots.json")
LOCK = None
# sesi henüz gelmemiş satırlar için cömert sabit süreler (görüntü bunlarla render edilir; ses sonra yerleşir)
PENDING = {"zipzip": lambda cid, txt: 2.9 if "hapşu" in txt else (1.9 if txt.count("Hav") >= 3 else 1.5),
           "final": lambda cid, txt: 0.9 + 0.085 * len(txt) + 0.6 * txt.count("?")}


def _pending(cid, who, txt):
    if who == Z:
        return PENDING["zipzip"](cid, txt)
    if who == A and cid.startswith("F"):
        return PENDING["final"](cid, txt)
    return None


def vo_len(cid, text, who=None):
    global LOCK
    if LOCK is None:
        import json
        LOCK = json.load(open(LOCK_PATH)) if os.path.exists(LOCK_PATH) else {}
    if cid in LOCK:
        return LOCK[cid]
    p = vo_path(cid)
    pend = _pending(cid, who, text) if who else None
    if pend is not None and not os.path.exists(p):
        return pend
    if os.path.exists(p):
        with wave.open(p) as w:
            return w.getnframes() / w.getframerate()
    return 0.4 + 0.075 * len(text)


def save_lock(pl):
    import json
    slots = {ln["cid"]: round(ln["t1"] - ln["t0"], 3) for ln in pl.lines}
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    json.dump(slots, open(LOCK_PATH, "w"), indent=0)


def color_of(text):
    low = text.lower().replace("İ", "i")
    for k, v in REN.items():
        if k in low:
            return v
    return None


# ================================================================ ZAMAN ÇİZELGESİ
class Plan:
    def __init__(self):
        self.extra = 0.0
        self._reset()
        self.build()
        n_play = sum(1 for s in self.scenes if SC[s["code"]].get("focus") is not None)
        if self.duration < TARGET and n_play:
            self.extra = (TARGET - self.duration) / n_play
            self._reset()
            self.build()

    def _reset(self):
        self.lines, self.replays, self.segs, self.scenes = [], [], [], []
        self.ux_keys, self.chapter = [], []
        self.T = {}

    def _replay_block(self, t, lines, ch, reps, label):
        tt = t + 2.4
        for rep in range(reps):
            for c2, w2, x2, _ in lines:
                dd = vo_len(c2, x2, w2)
                self.replays.append(dict(cid=c2, who=w2, txt=x2, t0=tt, t1=tt + dd, ch=ch, color=color_of(x2), label=label))
                tt += max(dd + 1.0, 4.8)
            tt += 2.4
        return tt

    def build(self):
        t = 0.0
        tek_all = {}
        for b in BOLUMLER:
            if b["renk"]:
                sc_last = b["sahneler"][-1][3]
                tek_all[REN[b["renk"]]] = sc_last[:4]
        cur = SC["A1"]["x"]
        self.ux_keys.append((0.0, cur))
        for b in BOLUMLER:
            ch = REN.get(b["renk"]) if b["renk"] else None
            ch0 = None
            for code, _, desc, lines in b["sahneler"]:
                sc = SC[code]
                if sc["x"] != cur:
                    d = abs(sc["x"] - cur)
                    dur = max(3.0, d / WALK_V)
                    self.segs.append((t, t + dur, "travel", code))
                    self.ux_keys += [(t, cur), (t + dur, sc["x"])]
                    t += dur
                    cur = sc["x"]
                s0 = t
                ch0 = ch0 if ch0 is not None else s0
                if sc.get("song"):
                    self.segs.append((0.0, sc["pre"] - 1.0, "dance", code))
                t += sc.get("pre", 1.2)
                for cid, who, txt, wait in lines:
                    d = vo_len(cid, txt, who)
                    self.lines.append(dict(cid=cid, who=who, txt=txt, t0=t, t1=t + d, wait=wait, scene=code, ch=ch,
                                           color=color_of(txt)))
                    self.T[cid] = (t, t + d)
                    t += d + GAP
                    if wait:
                        self.segs.append((t - GAP * 0.5, t + wait, "wait", code))
                        t += wait + 0.3
                    if sc.get("dance_after") == cid:
                        d0 = t + 0.6
                        if ch:  # renk dansı: tekerleme 3 kez, müzikle
                            self.segs.append((d0, d0 + DANCE_LEN, "dance", code))
                            self._replay_block(d0, tek_all[ch], ch, 2, ch)
                            t = d0 + DANCE_LEN + 0.6
                        else:   # final: gökkuşağı dansı
                            self.segs.append((d0, d0 + FINAL_DANCE, "dance", code))
                            t = d0 + FINAL_DANCE + 0.6
                    if sc.get("recap_after") == cid:
                        for key in ("mavi", "kirmizi", "sari"):
                            r0 = t + 0.4
                            self.segs.append((r0, r0 + RECAP_PER, "recap", key))
                            self._replay_block(r0 - 1.6, tek_all[key], key, 1, key)
                            t = r0 + RECAP_PER
                t += sc.get("post", 2.0) + (self.extra if sc.get("focus") is not None else 0.0)
                self.segs.append((s0, t, "scene", code))
                self.scenes.append(dict(code=code, t0=s0, t1=t, x=sc["x"], ch=ch))
            if ch:
                self.chapter.append((ch0, t, ch))
        self.ux_keys.append((t, cur))
        self.duration = t

    @staticmethod
    def _is_tekerleme(ln, lines):
        # sahnenin son "uç uç uç" dahil 4 satırı
        idx = [l[0] for l in lines]
        return idx.index(ln[0]) < 4

    def seg_at(self, t, kind=None):
        for s in self.segs:
            if s[0] <= t < s[1] and (kind is None or s[2] == kind):
                return s
        return None

    def scene_at(self, t):
        for s in self.scenes:
            if s["t0"] <= t < s["t1"]:
                return s
        return self.scenes[-1] if t >= self.scenes[-1]["t1"] else self.scenes[0]

    def chapter_at(self, t):
        r = self.seg_at(t, "recap")
        if r:
            return r[3], r[0], r[1]
        for a, b, c in self.chapter:
            if a <= t < b:
                return c, a, b
        return None, 0, 0

    def line_at(self, t, who=None, pad=0.0):
        for ln in self.lines:
            if ln["t0"] - pad <= t < ln["t1"] + pad and (who is None or ln["who"] == who):
                return ln
        return None


PLAN = None
STATE = None


def plan():
    global PLAN
    if PLAN is None:
        PLAN = Plan()
    return PLAN


# ================================================================ dudak senkronu
ENV = {}


def envelope(cid):
    if cid not in ENV:
        p = vo_path(cid)
        if not os.path.exists(p):
            ENV[cid] = None
        else:
            with wave.open(p) as w:
                sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            hop_ = sr // (FPS * 2)
            n = len(x) // hop_
            r = np.sqrt(np.mean(x[:n * hop_].reshape(n, hop_) ** 2, axis=1))
            ENV[cid] = np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1.2)
    return ENV[cid]


def mouth_of(who, t):
    pl = plan()
    for ln in pl.lines + pl.replays:
        if ln["who"] != who or not (ln["t0"] <= t < ln["t1"]):
            continue
        e = envelope(ln["cid"])
        if e is None:
            return 0.4 + 0.3 * math.sin(t * 18)
        i = int((t - ln["t0"]) * FPS * 2)
        if 0 <= i < len(e):
            return clamp((e[i] - 0.12) / 0.7) ** 0.8
    return 0.0


def blink(t, seed, period=3.4):
    k = math.floor(t / period)
    for kk in (k - 1, k):
        st = kk * period + hash01(seed, kk) * 1.8
        if 0 <= t - st < 0.16:
            return math.sin(math.pi * (t - st) / 0.16)
    return 0.0


def hop(t, times, h=40, d=0.42):
    v = 0.0
    for t0 in times:
        if t0 <= t < t0 + d:
            v = max(v, h * math.sin(math.pi * (t - t0) / d))
    return v


# ================================================================ ön hesap: konumlar, kamera (yaylı yumuşatma)
def _spring(target, w=2.4, dt=1 / FPS):
    out = np.empty_like(target)
    x = target[0].copy()
    v = np.zeros_like(x)
    for i in range(len(target)):
        a = w * w * (target[i] - x) - 2 * w * v
        v += a * dt
        x += v * dt
        out[i] = x
    return out


class State:
    """Tüm kareler için konum/kamera dizileri (ana süreçte bir kez hesaplanır, işçilere kopyalanır)."""

    def __init__(self, pl):
        n = int(pl.duration * FPS) + 2
        self.n = n
        ts = np.arange(n) / FPS
        keys = pl.ux_keys
        ux = np.empty(n)
        for i, t in enumerate(ts):
            ux[i] = keys[-1][1]
            for (t0, x0), (t1, x1) in zip(keys, keys[1:]):
                if t0 <= t < t1:
                    u = (t - t0) / max(t1 - t0, 1e-6)
                    # yürüyüşte kenarlarda yumuşak hızlanma/yavaşlama
                    ux[i] = lerp(x0, x1, ease_io(u) if t1 - t0 < 4 else clamp(u * 1.0))
                    if t1 - t0 >= 4:
                        ux[i] = lerp(x0, x1, _ease_edges(u, t1 - t0))
                    break
        # Umay A1–A2: evin içinden kapıdan çıkar
        self.ux = ux
        self.facing = np.ones(n)
        zt = np.empty(n)
        for i, t in enumerate(ts):
            zt[i] = self._zip_target(pl, t, ux[i])
        self.zx = _spring(zt[:, None], w=3.2)[:, 0]
        self.ugait, self.uph = _gait(self.ux, WALK_V, 230, STRIDE_W, 210)
        self.zgait, self.zph = _gait(self.zx, 120, 220, 120, 190)
        cam = np.empty((n, 3))
        for i, t in enumerate(ts):
            cam[i] = self._cam_target(pl, t, ux[i], self.zx[i])
        self.cam = _spring(cam, w=2.0)
        # dünyanın sol kenarının dışını gösterme
        self.cam[:, 0] = np.maximum(self.cam[:, 0], W / (2 * self.cam[:, 2]) - world.MX + 20)
        # kelebek
        bf = np.empty((n, 2))
        for i, t in enumerate(ts):
            bf[i] = self._bf_target(pl, t, ux[i], self.zx[i])
        self.bf = _spring(bf, w=3.6)

    @staticmethod
    def _zip_target(pl, t, ux):
        base = ux - 175
        T = pl.T
        if t < pl.scenes[1]["t0"] + 1.0:
            base = max(ux - 175, HOUSE_X - 10) if ux > HOUSE_X + 40 else HOUSE_X - 10
        # dere: Zıpzıp kıyıya gider, patisini suya sokar
        if "M18" in T and T["M17"][0] - 0.5 < t < T["M21"][1] + 2.5:
            return STREAM[0] + 90
        # top: koşar, alır, getirir
        if "M28" in T:
            a = T["M28"][1]
            if a < t < a + 3.0:
                return lerp(base, BALL0[0] + 330, smooth((t - a) / 1.6))
            if a + 3.0 <= t < a + 6.5:
                return lerp(BALL0[0] + 330, ux + 140, smooth((t - a - 3.0) / 2.5))
            if a + 6.5 <= t < T["M30"][1] + 2:
                return ux + 140
        # çilek: koklamaya gider
        if "K23" in T and T["K22"][0] < t < T["K24"][1] + 1.5:
            return STRAW[0] - 190
        # ayçiçeği koklama
        if "S17" in T and T["S17"][0] - 0.5 < t < T["S19"][1] + 1.0:
            return SUNFLOWER[0] - 205
        # final sarılma: Umay'a yaklaşır
        if "F09" in T and t > T["F09"][0] - 0.5:
            return ux - 120
        return base

    @staticmethod
    def _cam_target(pl, t, ux, zx):
        sc = pl.scene_at(t)
        tr = pl.seg_at(t, "travel")
        if tr:
            return (ux + 200, 560, 1.0)
        spec = SC[sc["code"]]["cam"]
        if spec == "collar":
            return (zx + 40, GROUND_Y - 120, 2.1)
        if spec == "ribbon":
            return (ux + 60, GROUND_Y - 250, 2.0)
        dx, cy, z = spec
        if SC[sc["code"]].get("song"):
            u = smooth((t - 6.0) / (SONG_LEN - 8.0))
            return (sc["x"] + 160, lerp(150, 520, u), 1.0)
        if pl.seg_at(t, "dance") or pl.seg_at(t, "recap"):
            return (ux + 60, 560, 1.0)
        return (sc["x"] + dx, cy, z)

    @staticmethod
    def _bf_target(pl, t, ux, zx):
        sc = pl.scene_at(t)
        S = SC[sc["code"]]
        ch, c0, c1 = pl.chapter_at(t)
        wob = np.array([45 * math.sin(t * 1.3) + 16 * math.sin(t * 3.1), 30 * math.sin(t * 2.6) + 10 * math.cos(t * 4.1)])
        if not ch and S.get("bf") != "final":
            return np.array([ux + 600, 120.0])
        if pl.seg_at(t, "travel"):
            return np.array([ux + 300, 560.0]) + wob
        f = focus_point(pl, sc["code"], t, ux, zx)
        aw = S.get("away_after")
        if aw and t > pl.T[aw][1]:
            u = t - pl.T[aw][1]
            return np.array([ux + 300 + u * 260, 420 - u * 160])
        if t < c0 + 2.5:  # bölüm başında sağ üstten gelir
            u = (t - c0) / 2.5
            return np.array([lerp(ux + 1100, f[0] if f is not None else ux + 250, smooth(u)), lerp(150, f[1] if f is not None else 520, smooth(u))])
        if S.get("bf") == "dance" or pl.seg_at(t, "dance"):
            a = t * 1.4
            return np.array([ux + 40 + math.cos(a) * 260, 520 + math.sin(a) * 120])
        if f is None:
            return np.array([ux + 250, 520.0]) + wob
        if S.get("bf") == "land" and t > sc["t0"] + 2.2:
            return np.array([f[0], f[1] - 26])
        return np.array([f[0], f[1] - 60]) + wob


def _ease_edges(u, dur, ramp=1.2):
    """Uzun yürüyüşlerde başta/sonda yumuşak hız değişimi, ortada sabit hız."""
    r = clamp(ramp / dur, 0, 0.45)
    if u < r:
        return (u * u / (2 * r)) / (1 - r)
    if u > 1 - r:
        v = 1 - u
        return 1 - (v * v / (2 * r)) / (1 - r)
    return (u - r / 2) / (1 - r)


def _gait(xs, walk_v, run_v, stride_w, stride_r):
    dt = 1.0 / FPS
    v = np.abs(np.gradient(xs, dt))
    v = np.convolve(v, np.ones(5) / 5, mode="same")
    g = np.where(v < walk_v, v / walk_v, 1 + np.clip((v - walk_v) / (run_v - walk_v), 0, 1))
    g = np.where(v < 6, 0, g)
    stride = np.where(g > 1, lerp(stride_w, stride_r, np.clip(g - 1, 0, 1)), stride_w)
    ph = np.cumsum(v / stride * 2 * math.pi * dt)
    return g, ph


def focus_point(pl, code, t, ux, zx):
    f = SC[code].get("focus")
    if f is None:
        return None
    if f == "collar":
        return np.array([zx + 30, GROUND_Y - 92.0])
    if f == "ribbon":
        return np.array([ux + 78, GROUND_Y - 290.0])
    if f == "sun":
        cx = STATE.cam[int(t * FPS)][0] if STATE is not None else ux
        return np.array([cx + 430, 190.0])
    if f == "chick":
        return np.array([chick_x(pl, t), GROUND_Y - 70.0])
    return np.array(f, float)


def chick_x(pl, t):
    T = pl.T
    if "S20" not in T or t < T["S20"][0]:
        return CHICK0
    return lerp(CHICK0, CHICK0 + 140, smooth((t - T["S20"][0]) / 1.2))


# ================================================================ ÇİZİM
def draw_world_props(p, pl, t, cx, z):
    """Görüş alanındaki dünya nesneleri (karakterlerin arkasında kalanlar)."""
    T = pl.T
    vis = lambda x, w=600: abs(x - cx) < W / (2 * z) + w

    if vis(HOUSE_X, 500):
        d0 = exit_time(pl)
        door = smooth((t - d0 + 1.2) / 0.8) * (1 - smooth((t - d0 - 4.0) / 0.8))
        gm = 0.0
        if "A03" in T:
            gm = window(t, pl.scenes[1]["t0"] + 1.5, pl.scenes[1]["t1"] + 1.0, 0.8)
        P.big_house(p, HOUSE_X, GROUND_Y - 15, 1.15, door=door, grandma=gm, t=t)
    if vis(900, 300):
        world.fence(p, 820, 940, GROUND_Y - 30, 0.8)
    for i, (fx, fy) in enumerate(FLOWERS):
        if vis(fx, 200):
            pop = 1.0
            if "M13" in T:
                a, b = T["M13"]
                k = int(clamp((t - a) / max(b - a, 0.1)) * 3.999) if a <= t < b + 1.5 else -1
                if k == i:
                    p.glow(fx, fy - 140, 70, P.COL["sari_l"], 0.8)
                    pop = 1.18
            draw_flower(p, fx, fy, 1.1, P.COL["mavi"], center=P.COL["sari"], sway=math.sin(t * 1.5 + i) * 0.3, pop=pop, seed=f"bf{i}")
    if vis(TREE_BIRD, 400):
        world.tree(p, TREE_BIRD, GROUND_Y - 70, 1.45, 77, col=hexrgb("#5DA34F"))
        P.branch(p, TREE_BIRD - 150, 575, TREE_BIRD + 10, 568)
        sing = 1.0 if ("M25" in T and T["M22"][0] < t < T["M25"][1] + 1.5) else 0.0
        P.bird(p, BIRD[0], BIRD[1], 0.9, t, sing=sing)
        if sing:
            P.music_notes(p, BIRD[0], BIRD[1] - 40, t)
    if vis(FAR_HOUSE[0], 500):
        world.house(p, FAR_HOUSE[0], FAR_HOUSE[1], 0.55)
    if vis(APPLE_TREE[0], 500):
        apples = list(APPLES)
        if "K08" in T and t > T["K08"][1]:
            apples = apples[1:]
        P.apple_tree(p, APPLE_TREE[0], APPLE_TREE[1], 1.0, apples)
    if vis(SUNFLOWER[0], 400):
        P.sunflower(p, SUNFLOWER[0], SUNFLOWER[1], 1.0, t)
    if vis(STREAM[0], 800):
        P.stream(p, STREAM[0], STREAM[1], STREAM[2], t)


def draw_front_props(p, pl, t, cx, z, anchors):
    """Karakterlerin önünde kalanlar."""
    T = pl.T
    vis = lambda x, w=600: abs(x - cx) < W / (2 * z) + w
    if vis(BUSH[0], 500):
        # top
        bx, by, rot, held = ball_state(pl, t, anchors)
        if not held:
            P.ball(p, bx, by, 34, rot)
        P.bush(p, BUSH[0], BUSH[1], 1.0, seed=3)
    if vis(LADYBUG[0], 500):
        glow = -1
        if "K18" in T:
            a, b = T["K18"]
            if a <= t < b + 1.0:
                glow = int(clamp((t - a) / max(b - a, 0.1)) * 3.999)
        walk = 6 * math.sin(t * 0.8)
        P.ladybug(p, LADYBUG[0], LADYBUG[1], 0.75, t, glow=glow, walk=walk)
    if vis(STRAW[0], 400):
        P.strawberry_patch(p, STRAW[0], STRAW[1], 1.0, t)
    if vis(CHICK0, 400):
        if "S20" in T and t > T["S20"][0]:
            peep = 1.0 if ("S24" in T and T["S24"][0] < t < T["S24"][1] + 0.6) else 0.0
            hp = hop(t, [T["S20"][0] + 0.2, T["S20"][0] + 0.7, T["S21"][0] + 0.1], 26, 0.35)
            P.chick(p, chick_x(pl, t), GROUND_Y + 10, 1.1, t, peep=peep, hop=hp)
    if vis(PICNIC[0], 500):
        held = "S27" in T and t > T["S27"][0] - 0.6
        P.picnic(p, PICNIC[0], PICNIC[1], 1.0, lemons=1 if held else 2)
    if vis(STREAM[0], 800) and "M20" in T:
        u = (t - T["M20"][0]) / 0.9
        P.splash(p, STREAM[0] + 230, STREAM[2] - 30, u)


def exit_time(pl):
    """Umay'ın kapıdan çıktığı an (A1'den A2'ye yürüyüşün başı)."""
    for s_ in pl.segs:
        if s_[2] == "travel" and s_[3] == "A2":
            return s_[0]
    return 0.0


def idle_play(pl, t):
    """Sahnenin son cümlesinden sonra kalan oyun süresi: (aktif mi, sahne içi zaman)."""
    sc = pl.scene_at(t)
    last = max((l["t1"] for l in pl.lines if l["scene"] == sc["code"]), default=sc["t1"])
    if SC[sc["code"]].get("focus") is None or pl.seg_at(t, "travel") or pl.seg_at(t, "dance") or pl.seg_at(t, "recap"):
        return False, 0.0
    if t > last + 1.8 and t < sc["t1"] - 1.0:
        return True, t - last - 1.8
    return False, 0.0


def ball_state(pl, t, anchors):
    T = pl.T
    if "M28" not in T:
        return BALL0[0], BALL0[1], 0.0, False
    a = T["M28"][1]
    if t < T["M27"][0]:
        return BALL0[0], BALL0[1], 0.0, False
    if t < a - 0.3:  # Umay topu aldı (elinde)
        h = anchors.get("umay_hand")
        if h is not None and t > T["M27"][0] + 0.8:
            return h[0], h[1] + 34, 0.0, False
        return BALL0[0], BALL0[1], 0.0, False
    if t < a + 1.3:  # atış: parabol
        u = clamp((t - a + 0.3) / 1.6)
        x0, y0 = pl_ux(t) + 60, GROUND_Y - 200
        x1 = BALL0[0] + 360
        x = lerp(x0, x1, u)
        y = lerp(y0, GROUND_Y, u) - math.sin(math.pi * u) * 260
        return x, y, u * 8, False
    if t < a + 2.0:
        u = (t - a - 1.3) / 0.7
        return BALL0[0] + 360 + u * 40, GROUND_Y - abs(math.sin(u * math.pi * 2)) * 50 * (1 - u), 8 + u * 3, False
    if t < a + 6.5:  # Zıpzıp ağzında getirir
        n = anchors.get("nose")
        if n is not None and t > a + 2.6:
            return n[0] + 10, n[1] + 40, 0.0, False
        return BALL0[0] + 400, GROUND_Y, 11.0, False
    return pl_ux(t) + 140 + 70, GROUND_Y, 0.0, False


def pl_ux(t):
    return STATE.ux[min(int(t * FPS), STATE.n - 1)]


def umay_state(pl, t, i, focus, bfp):
    T = pl.T
    st = dict(phase=STATE.uph[i], gait=STATE.ugait[i], stride_w=STRIDE_W)
    ux = STATE.ux[i]
    # yön: yürürken gidiş yönü; durunca odağa bakar
    v = STATE.ux[min(i + 1, STATE.n - 1)] - STATE.ux[max(i - 1, 0)]
    f = 1
    if abs(v) > 0.3:
        f = 1 if v > 0 else -1
    elif focus is not None and focus[0] < ux - 60:
        f = -1
    if "F09" in T and t > T["F09"][0] - 0.3:
        f = -1
    st["facing"] = f
    ln = pl.line_at(t, U, pad=0.15)
    pose = "idle"
    happy = sour = 0.0
    jumps = []
    for l in pl.lines:
        if l["who"] == U and l["color"]:
            jumps.append(l["t0"] + 0.1)
        if l["who"] == A and l["color"] and l["txt"].lower().replace("İ", "i").startswith(("mavi!", "kırmızı!", "sarı!", "mavi, mavi", "evet")):
            jumps.append(l["t0"] + 0.15)
    if ln:
        txt = ln["txt"]
        if txt.startswith("Hoşça"):
            pose = "wave"
        elif txt.startswith(("Bak", "Kelebek", "Top", "Güneş", "Civciv", "Çilek", "Mavi! Kırmızı", "Mavi, kırmızı")):
            pose = "point"
        elif txt.startswith("Hi hi"):
            pose, happy = "laugh", 1.0
        elif "yakala" in txt:
            pose = "point"
        elif "Ham" in txt:
            pose, sour = "think", 1.0
        elif ln["color"]:
            pose = "cheer"
    wait = pl.seg_at(t, "wait")
    if wait and pose == "idle":
        pose = "think"
    play, pu = idle_play(pl, t)
    if play and pose == "idle":
        cyc = pu % 6.0
        if cyc < 2.2:
            pose = "point"
        elif 3.6 < cyc < 4.8:
            pose, happy = "cheer", 1.0
            jumps.append(t - (cyc - 3.7))
    if pl.seg_at(t, "dance"):
        beat = int(t / 0.6)
        pose = ["cheer", "wave", "cheer", "point"][beat % 4]
        jumps += [t - (t % 1.2)]
    # elmayı/limonu tutuyor
    if "K09" in T and T["K08"][1] < t < T["K09"][1] + 1.5:
        pose = "think"
    if "S28" in T and T["S27"][0] - 0.5 < t < T["S28"][1] + 0.3:
        pose = "think"
    if "S28" in T and T["S28"][0] < t < T["S29"][1] + 0.6:
        sour = 1.0
    if "F10" in T and T["F09"][0] - 0.3 < t < T["F12"][1] + 3.0:
        pose = "hug"
        happy = 1.0
    if SC[pl.scene_at(t)["code"]].get("end"):
        pose = "wave"
        f = 1
        st["facing"] = 1
    st["arms"] = umay_arm_pose(pose, t)
    st["jump"] = hop(t, jumps, 36)
    st["happy"] = happy
    st["sour"] = sour
    st["blink"] = blink(t, "umay")
    st["mouth"] = mouth_of(U, t)
    st["look"] = 0.0 if SC[pl.scene_at(t)["code"]].get("end") else 0.4
    tgt = bfp if bfp is not None else focus
    if tgt is not None:
        dx = (tgt[0] - ux) * f
        dy = tgt[1] - (GROUND_Y - 250)
        st["eye_dx"] = clamp(dx / 300, -1, 1)
        st["eye_dy"] = clamp(dy / 300, -1, 1)
        st["look"] = clamp(dx / 400, -0.5, 0.5)
    if SC[pl.scene_at(t)["code"]].get("up"):
        st["eye_dy"] = -1.0
        st["tilt"] = -0.08
    if wait:
        st["tilt"] = 0.1
    return st


def zipzip_state(pl, t, i, focus):
    T = pl.T
    st = dict(facing=1, phase=STATE.zph[i], gait=STATE.zgait[i])
    zx = STATE.zx[i]
    v = STATE.zx[min(i + 1, STATE.n - 1)] - STATE.zx[max(i - 1, 0)]
    if v < -0.4:
        st["facing"] = -1
    elif abs(v) <= 0.4 and focus is not None and focus[0] < zx - 80:
        st["facing"] = -1
    m = mouth_of(Z, t)
    if st["gait"] > 0.8 and m < 0.1:
        m = 0.3 + 0.08 * math.sin(t * 13)
    st["mouth"] = m
    zl = [l["t0"] + 0.05 for l in pl.lines if l["who"] == Z]
    st["jump"] = hop(t, zl, 34, 0.4)
    play, pu = idle_play(pl, t)
    st["wag"] = 1.8 if (pl.line_at(t, Z, 0.8) or pl.seg_at(t, "dance") or play) else 1.1
    if play:
        st["jump"] = max(st["jump"], hop(pu % 3.0, [1.2], 30, 0.4))
    st["blink"] = blink(t, "zipzip", 3.0)
    if focus is not None and focus[1] < GROUND_Y - 300:
        st["look_up"] = 0.6
        st["eye_dy"] = -0.8
    if "K24" in T and T["K23"][0] < t < pl.chapter_at(T["K23"][0])[2]:
        st["nose_color"] = P.COL["kirmizi"]
    if "S18" in T:
        a, b = T["S18"]
        if a - 0.6 <= t < a + (b - a) * 0.7:
            st["sneeze"] = -smooth((t - a + 0.6) / ((b - a) * 0.7 + 0.6))
        elif a + (b - a) * 0.7 <= t < b + 0.4:
            k = (t - a - (b - a) * 0.7) / ((b - a) * 0.3 + 0.4)
            st["sneeze"] = math.sin(math.pi * min(1, k * 2.2)) * (1 - k)
    if "S25" in T and T["S25"][0] - 0.3 < t < T["S25"][1] + 1.0:
        st["tilt"] = 0.22
    if "F11" in T and t > T["F09"][0]:
        st["happy"] = 1.0 if (t % 2.4) > 1.2 else 0.0
    if "M21" in T and T["M20"][0] < t < T["M21"][1] + 1.2:
        st["tilt"] = 0.15 * math.sin(t * 20) * (t < T["M20"][1] + 0.8)
    return st


def draw_overlay(p, pl, t):
    """Ekran yazıları: büyük renk adı, köşe rozeti, başlık, soru işareti, kapanış."""
    ch, c0, c1 = pl.chapter_at(t)
    if ch:
        P.draw_badge(p, ch, smooth((t - c0) / 0.8) * (1 - smooth((t - c1 + 0.8) / 0.8)))
    # büyük renk yazısı
    best = None
    for ln in pl.lines + pl.replays:
        if ln["color"] and ln["t0"] - 0.1 <= t < ln["t1"] + 1.4:
            best = ln
    dance = pl.seg_at(t, "dance") if ch else None
    dance = dance or pl.seg_at(t, "recap")
    if best or dance:
        key = best["color"] if best else ch
        t0 = best["t0"] if best else dance[0]
        t1 = best["t1"] + 1.4 if best else dance[1]
        a = smooth((t - t0 + 0.1) / 0.25) * (1 - smooth((t - t1 + 0.35) / 0.35))
        if dance and not best:
            a = window(t, dance[0] + 0.5, dance[1] - 0.5, 0.5)
        pop = ease_out_back(clamp((t - t0 + 0.1) / 0.45)) * (1 + 0.04 * math.sin(t * 10.5) * bool(dance))
        P.draw_word(p, P.WORD[key], P.COL[key], a, max(pop, 0.01), W / 2, 175, size=170)
    # başlık (açılış şarkısı boyunca) + etrafında uçan üç kelebek
    if t < SONG_LEN:
        a = window(t, 0.8, SONG_LEN - 3.0, 0.8)
        if a > 0:
            from ep01_renkli_kelebek import draw_title
            title_panel(p, a, 330)
            draw_title(p, a, max(ease_out_back((t - 0.5) / 0.9), 0.01) * (1 + 0.02 * math.sin(t * 5.2)), "Umay ile Zıpzıp", "Renkli Kelebekler")
            for k, key in enumerate(("mavi", "kirmizi", "sari")):
                ang = t * 0.9 + k * 2 * math.pi / 3
                col, edge = BF_COL[key]
                draw_butterfly(p, W / 2 + math.cos(ang) * 620, 380 + math.sin(ang) * 210, 1.1 * a, t * 14 + k, 0.2 * math.sin(t + k), col=col, edge=edge)
    # kapanış
    sc = pl.scene_at(t)
    if SC[sc["code"]].get("end"):
        from ep01_renkli_kelebek import draw_title
        u = t - sc["t0"]
        title_panel(p, clamp(u / 0.6), 230, h=270)
        draw_title(p, clamp(u / 0.6), max(ease_out_back(u / 0.8), 0.01), "Umay ile Zıpzıp", "Yakında yeni maceralarda!", y=200, sub_dy=120, size=130)


def title_panel(p, a, cy, h=300, w=1180):
    from engine.core import rounded_rect
    p.part(lambda c: rounded_rect(c, W / 2 - w / 2, cy - h / 2 - 40, w, h, 60), P.COL["beyaz"], alpha=0.9 * a, seed="tpanel")


def render_frame(i, layers):
    pl = plan()
    t = i / FPS
    cx, cy, z = STATE.cam[min(i, STATE.n - 1)]
    cam = (cx, cy, z)
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = PAPER[::-1]
    from ep01_renkli_kelebek import composite
    for L in layers:
        if L["name"] == "front":
            continue
        drift = t * 9 if L["name"] == "clouds" else 0.0
        M, _ = world.layer_matrix(L["p"], cam, drift)
        composite(rgb, cv2.warpAffine(L["img"], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE))
    if z > 1.05:
        rgb = cv2.GaussianBlur(rgb, (0, 0), (z - 1) * 2.0)

    dyn = Canvas()
    p = PAINTERS[STYLE](dyn, t=t, scale=z, frame=i)
    ctx = p.ctx
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    cam_m = ctx.get_matrix()
    inv = cairo.Matrix(*cam_m)
    inv.invert()
    # güneş (sonsuz uzakta: kamerayla yatayda kayar)
    sx_, sy_ = cx + 430 / z, 190
    p.glow(sx_, sy_, 230, hexrgb("#FFF3C4"), 0.8)
    for k in range(12):
        a = k * math.pi / 6 + t * 0.15
        p.part(lambda c, a=a: ellipse(c, sx_ + math.cos(a) * 112, sy_ + math.sin(a) * 112, 22, 8, a), hexrgb("#FFC94A"), seed=f"sr{k}")
    p.part(lambda c: circle(c, sx_, sy_, 76), hexrgb("#FFD45C"), seed="sun")
    if pl.T.get("S08") and pl.T["S08"][0] - 0.2 < t < pl.T["S09"][1] + 1.0:
        p.glow(sx_, sy_, 170, P.COL["sari_l"], 0.6 + 0.2 * math.sin(t * 6))

    sc = pl.scene_at(t)
    focus = focus_point(pl, sc["code"], t, STATE.ux[i], STATE.zx[i])
    draw_world_props(p, pl, t, cx, z)

    ux, zx = STATE.ux[i], STATE.zx[i]
    bfp = STATE.bf[min(i, STATE.n - 1)] if (pl.chapter_at(t)[0] or SC[sc["code"]].get("bf") == "final") else None
    # gölgeler
    for sx, w_ in (((ux, 62), (zx + 10, 90)) if t > exit_time(pl) else ()):
        p.part(lambda c, sx=sx, w_=w_: ellipse(c, sx, GROUND_Y + 4, w_, 12), hexrgb("#6E7FA6"), alpha=0.25, line=False, seed=f"sh{w_}")
    anchors = {}
    hidden = t < exit_time(pl) - 0.2
    zst = zipzip_state(pl, t, i, focus)
    ust = umay_state(pl, t, i, focus, bfp)
    if hidden:
        a_z = {"nose": (0, 0), "collar": (0, 0)}
        a_u = {}
    else:
        a_z = draw_zipzip(p, zx, GROUND_Y, 0.95, zst)
        a_u = draw_umay(p, ux, GROUND_Y, 1.0, ust)
    anchors["nose"] = inv.transform_point(*a_z["nose"])
    anchors["collar"] = inv.transform_point(*a_z["collar"])
    hands = a_u.get("hands", {})
    side = 1 if ust["facing"] > 0 else -1
    if 1 in hands:
        anchors["umay_hand"] = inv.transform_point(*hands[1])
    T = pl.T
    # elde tutulan: elma, limon, top
    if "K09" in T and T["K08"][1] - 0.2 < t < T["K09"][1] + 1.5 and "umay_hand" in anchors:
        hx, hy = anchors["umay_hand"]
        P.apple(p, hx, hy - 6, 24, seed="hand_ap")
    elif "K08" in T and T["K08"][1] - 1.0 < t < T["K08"][1] - 0.2:
        u = (t - T["K08"][1] + 1.0) / 0.8
        ax0, ay0 = APPLE_TREE[0] + APPLES[0][0], APPLE_TREE[1] + APPLES[0][1]
        P.apple(p, lerp(ax0, ux + 40, u), lerp(ay0, GROUND_Y - 180, u * u), 24, seed="fall_ap")
    if "S28" in T and T["S27"][0] - 0.6 < t < T["S29"][1] + 1.0 and "umay_hand" in anchors:
        hx, hy = anchors["umay_hand"]
        P.lemon(p, hx, hy - 4, 0.8, rot=0.3, seed="hand_lm")
    draw_front_props(p, pl, t, cx, z, anchors)

    # kelebek(ler)
    if SC[sc["code"]].get("bf") == "final":
        for k, key in enumerate(("mavi", "kirmizi", "sari")):
            a = t * 1.2 + k * 2 * math.pi / 3
            bx, by = ux + 30 + math.cos(a) * 280, 470 + math.sin(a) * 110 + 20 * math.sin(t * 3 + k)
            gl = 0.0
            for q, cid in ((0, "F03"), (1, "F05"), (2, "F07")):
                if q == k and cid in T and T[cid][0] < t < T[cid][1] + 4.0:
                    gl = 1.0
            if gl:
                p.glow(bx, by, 90, P.COL["sari_l"], 0.7)
            col, edge = BF_COL[key]
            draw_butterfly(p, bx, by, 0.9 + 0.25 * gl, t * 15 + k, 0.15 * math.sin(t * 2 + k), col=col, edge=edge)
    elif bfp is not None:
        ch = pl.chapter_at(t)[0]
        col, edge = BF_COL[ch]
        landed = SC[sc["code"]].get("bf") == "land" and t > sc["t0"] + 2.6 and not pl.seg_at(t, "travel")
        flap = (0.9 + 0.6 * math.sin(t * 2.4)) if landed else t * 15
        if pl.seg_at(t, "wait"):
            p.glow(bfp[0], bfp[1], 100 + 15 * math.sin(t * 6), P.COL["sari_l"], 0.35)
        bpos = bfp
        if SC[sc["code"]].get("focus") == "collar" and landed:
            bpos = (anchors["collar"][0], anchors["collar"][1] - 22)
        draw_butterfly(p, bpos[0], bpos[1], 0.85, flap, 0.15 * math.sin(t * 2) if not landed else -0.1, col=col, edge=edge)

    # soru bekleme: odakta parlama + soru işareti
    wseg = pl.seg_at(t, "wait")
    if wseg and focus is not None:
        u = (t - wseg[0]) / max(wseg[1] - wseg[0], 0.1)
        qa = window(t, wseg[0] + 0.2, wseg[1] - 0.2, 0.25)
        qx, qy = focus[0] + 70, focus[1] - 120 - 8 * math.sin(t * 4)
        p.part(lambda c: circle(c, qx, qy, 42), P.COL["beyaz"], alpha=qa, seed="qbg")
        ctx.save()
        ctx.select_font_face("Baloo 2", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(64)
        ext = ctx.text_extents("?")
        p.part(lambda c: (c.move_to(qx - ext.width / 2 - ext.x_bearing, qy - ext.height / 2 - ext.y_bearing), c.text_path("?")),
               P.COL["mor"], alpha=qa, seed="qm", line=False)
        ctx.restore()
    # ışıltılar: renk cevaplarında
    for ln in pl.lines:
        if ln["who"] == A and ln["color"] and ln["txt"][:1] in "MKSE" and ln["txt"].endswith("!") and len(ln["txt"]) < 26:
            u = (t - ln["t0"]) / 1.1
            if 0 < u < 1:
                tgt = focus if focus is not None else (ux + 150, 520)
                draw_sparkles(p, tgt[0], tgt[1] - 30, u, n=8, radius=130, seed=ln["cid"])
    # hapşırık polenleri
    if "S18" in T:
        a, b = T["S18"]
        u = (t - (a + (b - a) * 0.7)) / 1.0
        if 0 < u < 1:
            n_ = anchors["nose"]
            for k in range(8):
                ang = -0.9 + k * 0.25
                d = 30 + 140 * ease_io(u) * (0.6 + 0.6 * hash01(k))
                p.part(lambda c, ang=ang, d=d: circle(c, n_[0] + math.cos(ang) * d, n_[1] + math.sin(ang) * d * 0.6, 7 * (1 - u * 0.5)),
                       P.COL["sari"], alpha=1 - u, seed=f"pol{k}", lw=0.4)
    # kalpler (final)
    if "F09" in T and T["F09"][0] < t < T["F12"][1] + 4:
        for j in range(8):
            t0 = T["F09"][0] + j * 0.6
            u = (t - t0) / 2.4
            if 0 < u < 1:
                from ep01_renkli_kelebek import heart_path
                hx = (ux + zx) / 2 + 40 + math.sin(u * 6 + j) * 40 + (hash01(j) - 0.5) * 120
                hy = GROUND_Y - 300 - u * 260
                r = 14 * (0.6 + 0.4 * math.sin(math.pi * u))
                p.part(lambda c, hx=hx, hy=hy, r=r: heart_path(c, hx, hy, r), P.COL["kirmizi"], alpha=1 - u ** 3, seed=f"hrt{j}", lw=0.6)
    # dans: rengin nesneleri etrafta zıplar
    dseg = pl.seg_at(t, "dance")
    rseg = pl.seg_at(t, "recap")
    if rseg:
        draw_dance_items(p, pl, t, rseg, ux, rseg[3])
    elif dseg and pl.chapter_at(t)[0]:
        draw_dance_items(p, pl, t, dseg, ux, pl.chapter_at(t)[0])
    elif dseg and dseg[3] != "A1":
        for k, key in enumerate(("mavi", "kirmizi", "sari")):
            draw_dance_items(p, pl, t, dseg, ux, key, sub=k)
    dyn.surface.flush()

    # gökkuşağı arka planda (karakterlerin arkasında) — ayrı katman
    if "F09" in T and t > T["F09"][0] - 1.0:
        rb = Canvas()
        pr = PAINTERS[STYLE](rb, t=t, scale=z, frame=i)
        pr.ctx.set_matrix(cam_m)
        P.rainbow(pr, RAINBOW[0], RAINBOW[1], RAINBOW[2], smooth((t - T["F09"][0] + 1.0) / 3.0))
        rb.surface.flush()
        composite(rgb, rb.arr)
    composite(rgb, dyn.arr)
    for L in layers:
        if L["name"] == "front":
            M, _ = world.layer_matrix(L["p"], cam)
            composite(rgb, cv2.warpAffine(L["img"], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT))
    ov = Canvas()
    po = PAINTERS[STYLE](ov, t=t, scale=1.0, frame=i)
    draw_overlay(po, pl, t)
    ov.surface.flush()
    composite(rgb, ov.arr)
    # açılış/kapanış kararması
    fade = clamp(t / 0.8) * clamp((pl.duration - t) / 1.2)
    rgb = rgb * fade + PAPER[::-1][None, None, :] * (1 - fade)
    return (post_process(STYLE, rgb) * 255 + 0.5).astype(np.uint8)


def draw_dance_items(p, pl, t, dseg, ux, ch, sub=None):
    u = (t - dseg[0])
    items = {"mavi": ["flower", "drop", "bird", "ball"], "kirmizi": ["apple", "ladybug", "straw", "heart"],
             "sari": ["sunflower", "chick", "lemon", "star"]}[ch]
    if sub is not None:  # final dansı: üç rengin birer nesnesi gökkuşağı altında
        items = items[:1] if sub == 0 else items[:1]
    for k, it in enumerate(items):
        app = clamp((u - 0.6 - k * 0.5) / 0.5) * (1 - clamp((t - dseg[1] + 1.2) / 0.8))
        if app <= 0:
            continue
        if sub is not None:
            ang = math.pi * (0.25 + 0.25 * sub)
        else:
            ang = math.pi * (0.15 + 0.7 * k / (len(items) - 1))
        x = ux + 40 - math.cos(ang) * 470
        y = 600 - math.sin(ang) * 230 - abs(math.sin(t * math.pi / 0.6 + k)) * 26
        s = ease_out_back(app) * 0.95
        if it == "flower":
            draw_flower(p, x, y + 110, 0.8 * s, P.COL["mavi"], center=P.COL["sari"], seed="df")
        elif it == "drop":
            p.part(lambda c: (c.move_to(x, y - 50 * s), c.curve_to(x + 40 * s, y, x + 34 * s, y + 40 * s, x, y + 40 * s),
                              c.curve_to(x - 34 * s, y + 40 * s, x - 40 * s, y, x, y - 50 * s), c.close_path()), P.COL["mavi"], seed="dd")
        elif it == "bird":
            P.bird(p, x, y + 30, 0.8 * s, t, sing=1.0, facing=1)
        elif it == "ball":
            P.ball(p, x, y + 34 * s, 34 * s, t * 2)
        elif it == "apple":
            P.apple(p, x, y, 34 * s, seed="dap")
        elif it == "ladybug":
            ctx = p.ctx
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(0.45 * s, 0.45 * s)
            P.ladybug(p, 0, 40, 1.0, t)
            ctx.restore()
        elif it == "straw":
            P.strawberry(p, x, y, 1.4 * s, seed="dsb")
        elif it == "heart":
            from ep01_renkli_kelebek import heart_path
            p.part(lambda c: heart_path(c, x, y, 30 * s), P.COL["kirmizi"], seed="dhr")
        elif it == "sunflower":
            ctx = p.ctx
            ctx.save()
            ctx.translate(x, y + 70)
            ctx.scale(0.4 * s, 0.4 * s)
            P.sunflower(p, 0, 0, 1.0, t, h=180)
            ctx.restore()
        elif it == "chick":
            P.chick(p, x, y + 40, 1.0 * s, t, peep=1.0, facing=1)
        elif it == "lemon":
            P.lemon(p, x, y, 1.3 * s, rot=math.sin(t * 3) * 0.2, seed="dlm")
        elif it == "star":
            p.part(lambda c: star(c, x, y, 40 * s), P.COL["sari"], seed="dst")


# ================================================================ SES
def build_audio(path):
    from engine import audio as Au
    pl = plan()
    dur = pl.duration
    music, sfx, vo = Au.Bus(dur), Au.Bus(dur), Au.Bus(dur)
    BEAT = 0.6
    BAR = 4 * BEAT
    CH = {"C": ("C3", ["C4", "E4", "G4"]), "G": ("G2", ["B3", "D4", "G4"]), "Am": ("A2", ["A3", "C4", "E4"]), "F": ("F2", ["F3", "A3", "C4"])}
    PROG = ["C", "G", "Am", "F", "C", "F", "G", "C"]
    UKE_PROG = ["C", "G", "Am", "F", "C", "F", "G7", "C"]
    MEL = [
        [(0, "C5", 1), (1, "E5", 1), (2, "G5", 1), (3, "E5", 1)], [(0, "D5", 1), (1, "G5", 1), (2, "B4", 1), (3, "D5", 1)],
        [(0, "C5", 1), (1, "E5", 1), (2, "A5", 1.5), (3.5, "G5", 0.5)], [(0, "F5", 1), (1, "E5", 1), (2, "D5", 2)],
        [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "G5", 1), (2, "G5", 1), (3, "C6", 1)], [(0, "A5", 1), (1, "F5", 1), (2, "A5", 1), (3, "C6", 1)],
        [(0, "B5", 1), (1, "A5", 1), (2, "G5", 1), (3, "F5", 1)], [(0, "E5", 1), (1, "D5", 1), (2, "C5", 2)],
    ]
    hz = lambda nm: Au.midi_hz(Au.n(nm))

    def bar(t0, b, mode):
        root, tones = CH[PROG[b % 8]]
        if mode == "soft":
            music.add(t0, Au.pad([hz(x) for x in tones], BAR * 0.98, attack=0.6, release=0.8), 0.07)
            if b % 2 == 0:
                for k, nm in enumerate(("E5", "G5")):
                    music.add(t0 + k * 1.2, Au.glock(hz(nm)), 0.08)
            return
        energy = mode in ("travel", "dance")
        music.add(t0, Au.pad([hz(x) for x in tones], BAR * 0.95, attack=0.5, release=0.6), 0.05)
        for bt, down, g in ((0, 1, 0.19), (1, 1, 0.14), (1.5, 0, 0.09), (2.5, 0, 0.09), (3, 1, 0.14), (3.5, 0, 0.09)):
            if not energy and bt in (1.5, 2.5):
                continue
            music.add(t0 + bt * BEAT, Au.strum(UKE_PROG[b % 8], bool(down), 0.55 if energy else 0.8), g, pan=-0.25)
        for bt, nm, d in MEL[b % 8]:
            tt = t0 + bt * BEAT
            if mode == "dance":
                music.add(tt, Au.whistle(hz(nm), d * BEAT * 0.92), 0.16, pan=0.1)
                music.add(tt, Au.xylo(hz(nm)), 0.12, pan=0.2)
            elif mode == "travel":
                music.add(tt, Au.xylo(hz(nm)), 0.20, pan=0.15)
            else:
                music.add(tt, Au.kalimba(hz(nm)), 0.20, pan=0.1)
                music.add(tt, Au.glock(hz(nm) * 2, 1.0), 0.03, pan=0.3)
        if energy:
            for bt in range(4):
                music.add(t0 + bt * BEAT, Au.bass(Au.midi_hz(Au.n(root) + (12 if bt % 2 else 0)), 0.45, 0.2), 0.27)
            for bt in (0, 2):
                music.add(t0 + bt * BEAT, Au.soft_kick(), 0.26)
            for bt in (1, 3):
                music.add(t0 + bt * BEAT, Au.snap(), 0.13, pan=0.2)
            for e in range(8):
                music.add(t0 + e * BEAT / 2, Au.shaker(), 0.24 if e % 2 else 0.12, pan=0.35)
        else:
            music.add(t0, Au.bass(hz(root), 1.0, 0.4), 0.26)
            music.add(t0 + 2 * BEAT, Au.bass(Au.midi_hz(Au.n(root) + 7), 1.0, 0.4), 0.2)

    nb = int(dur / BAR) + 1
    for b in range(nb):
        t0 = b * BAR
        mid = t0 + BAR / 2
        if mid > dur - 4.0:
            break
        if pl.seg_at(mid, "wait") or pl.seg_at(t0, "wait"):
            mode = "soft"
        elif pl.seg_at(mid, "dance") or pl.seg_at(mid, "recap"):
            mode = "dance"
        elif pl.seg_at(mid, "travel"):
            mode = "travel"
        else:
            mode = "calm"
        bar(t0, b, mode)
    tend = (nb - 2) * BAR
    music.add(dur - 4.0, Au.pad([hz("C4"), hz("E4"), hz("G4"), hz("C5")], 3.0, attack=0.3, release=1.0), 0.09)
    music.add(dur - 4.0, Au.strum("C", True, 2.5, spread=0.03), 0.2, pan=-0.25)
    music.add(dur - 3.95, Au.kalimba(hz("C6"), 3.0), 0.22)

    # efektler
    T = pl.T
    sfx.add(0.9, Au.sparkle(base=Au.n("G5")), 0.28)
    for ln in pl.lines + pl.replays:
        if ln["color"]:
            sfx.add(ln["t0"], Au.pop(), 0.22)
    for ln in pl.lines:
        if ln["who"] == A and ln["color"] and ln["txt"][:1] in "MKSE" and ln["txt"].endswith("!") and len(ln["txt"]) < 26:
            sfx.add(ln["t0"] + 0.05, Au.sparkle(), 0.24)
        if ln["who"] in (U, Z):
            pass
    for s in pl.segs:
        if s[2] == "wait":
            sfx.add(s[0] + 0.2, Au.glock(hz("G6"), 0.8), 0.08)
    for k in range(4):
        if "M22" in T:
            sfx.add(T["M22"][0] + k * 1.6, Au.chirp_bird(k), 0.16, pan=0.4)
    if "M20" in T:
        sfx.add(T["M20"][0], Au.poof(0.4), 0.3)
    if "S18" in T:
        a, b = T["S18"]
        sfx.add(a + (b - a) * 0.7, Au.poof(), 0.35)
    if "S24" in T:
        for k in range(3):
            sfx.add(T["S24"][1] + 0.1 + k * 0.25, Au.chirp_bird(10 + k)[: int(0.15 * Au.SR)], 0.2)
    if "M28" in T:
        a = T["M28"][1]
        sfx.add(a - 0.3, Au.whoosh(0.7, 3), 0.25)
        sfx.add(a + 1.3, Au.boing(220, 160, 0.2), 0.3)
    for s in pl.segs:
        if s[2] == "travel":
            # ayak sesleri
            i0, i1 = int(s[0] * FPS), int(s[1] * FPS)
            ph = STATE.uph[i0:i1]
            st = np.nonzero(np.diff(np.floor(ph / math.pi)) > 0)[0]
            for k in st:
                sfx.add((i0 + k) / FPS, Au.bass(90, 0.06, 0.015), 0.07)
    if "F09" in T:
        for j in range(8):
            sfx.add(T["F09"][0] + j * 0.6, Au.glock(hz(["C6", "D6", "E6", "G6", "A6", "G6", "E6", "C7"][j]), 1.0), 0.08)
        sfx.add(T["F09"][0] - 0.8, Au.sparkle(base=Au.n("C6")), 0.25)

    spans = []
    for ln in pl.lines + pl.replays:
        p_ = vo_path(ln["cid"])
        if os.path.exists(p_):
            v = Au.load_wav(p_)
            slot = ln["t1"] - ln["t0"] + GAP * 0.8
            if len(v) / Au.SR > slot:  # yuvadan uzunsa hafifçe hızlandır (en fazla %20), sonra kes
                k = min(len(v) / Au.SR / slot, 1.2)
                v = np.interp(np.arange(0, len(v), k), np.arange(len(v)), v).astype(np.float32)[: int(slot * Au.SR)]
            vo.add(ln["t0"], v, 0.9, pan={U: 0.08, Z: -0.08}.get(ln["who"], 0.0))
            spans.append((ln["t0"], ln["t0"] + len(v) / Au.SR))
    duck = Au.duck_curve(dur, spans, depth=0.32)[: len(music.buf), None]
    music.buf = Au.lowpass(Au.reverb(music.buf, 1.8, 0.24), 8500)
    sfx.buf = Au.reverb(sfx.buf, 1.2, 0.12)
    t_ = np.arange(len(music.buf)) / Au.SR
    fade = np.clip((dur - 0.3 - t_) / 2.0, 0, 1) * np.clip(t_ / 0.5, 0, 1)
    mix = (music.buf * duck * 0.8 + sfx.buf * 0.9 + vo.buf * 1.1) * fade[:, None]
    Au.write_wav(path, Au.soft_limit(mix[: int(dur * Au.SR)]))
    return path


# ================================================================ render
_LAYERS = None
_SCALE = 1.0


def _worker(args):
    k, f0, f1, out = args
    ow, oh = int(W * _SCALE) // 2 * 2, int(H * _SCALE) // 2 * 2
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out],
                            stdin=subprocess.PIPE)
    for i in range(f0, f1):
        img = render_frame(i, _LAYERS)
        if _SCALE != 1.0:
            img = cv2.resize(img, (ow, oh), interpolation=cv2.INTER_AREA)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def setup():
    global STATE, _LAYERS
    pl = plan()
    STATE = State(pl)
    trees = tuple(x for x in range(120, SPAN + 1500, 2300) if all(abs(x - q) > 500 for q in (HOUSE_X, TREE_BIRD, APPLE_TREE[0], SUNFLOWER[0], RAINBOW[0], STRAW[0])))
    _LAYERS = world.build_layers(STYLE, cache_dir=os.path.join(ROOT, "build"), tag="_ep1", span=SPAN, sun=False,
                                 house_on_hill=False, trees_at=trees)
    return pl


def main():
    global _SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "umay_zipzip_bolum1_renkli_kelebekler.mp4"))
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--mux-only", action="store_true", help="görüntüyü yeniden render etmeden sesi yeniden kur ve ekle")
    a = ap.parse_args()
    pl = plan()
    if a.plan:
        for s in pl.scenes:
            print(f"{s['code']:3} {int(s['t0'] // 60)}:{s['t0'] % 60:04.1f} – {int(s['t1'] // 60)}:{s['t1'] % 60:04.1f}  x={s['x']}")
        print(f"toplam {int(pl.duration // 60)} dk {pl.duration % 60:.1f} sn · {len(pl.lines)} satır · {len(pl.replays)} tekrar")
        missing = [l['cid'] for l in pl.lines if not os.path.exists(vo_path(l['cid']))]
        print(f"eksik ses: {len(missing)}", missing[:12])
        return
    pl = setup()
    work = os.path.join(ROOT, "build")
    if a.audio_only:
        print(build_audio(os.path.join(work, "ep1_mix.wav")))
        return
    silent = os.path.join(work, "ep1_silent.mp4")
    if a.mux_only:
        wav = build_audio(os.path.join(work, "ep1_mix.wav"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", a.out], check=True)
        print(a.out)
        return
    if a.still:
        for s in a.still:
            p_ = os.path.join(work, f"ep1_still_{s:07.1f}.png")
            cv2.imwrite(p_, render_frame(int(s * FPS), _LAYERS))
            print(p_)
        return
    _SCALE = a.scale
    if a.start == 0 and a.end is None and a.scale == 1.0:
        save_lock(pl)   # bu render'ın zamanlaması sabitlenir; sonradan gelen sesler aynı yuvalara oturur
    end = a.end if a.end is not None else pl.duration
    f0, f1 = int(a.start * FPS), int(end * FPS)
    n = max(1, a.workers * 6)
    bounds = np.linspace(f0, f1, n + 1).astype(int)
    jobs = [(k, bounds[k], bounds[k + 1], os.path.join(work, f"ep1_seg_{k:03d}.mp4")) for k in range(n) if bounds[k + 1] > bounds[k]]
    with Pool(a.workers) as pool:
        segs = []
        for k, s in enumerate(pool.imap(_worker, jobs)):
            segs.append(s)
            print(f"  parça {k + 1}/{len(jobs)}", flush=True)
    lst = os.path.join(work, "ep1_concat.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    for s in segs:
        os.remove(s)
    wav = build_audio(os.path.join(work, "ep1_mix.wav"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-ss", str(a.start), "-t", str(end - a.start), "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
