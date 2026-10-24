"""Umay ile Zıpzıp, 2. Bölüm: "Şekil Avı" (≈10 dk), Batı çizgi filmi stili.

Senaryo: senaryo_sekil_avi.py. Bu dosya: istasyonlar, kamera, oyunculuk (şekil kutusu, parçalar, kenar sayma,
şekil çerçeveleri), büyük şekil yazıları, dans araları, müzik ve efektler. Zamanlama seslendirme sürelerinden çıkar.

    python3 ep2_sekil_avi.py --plan
    python3 ep2_sekil_avi.py --still 30 90
    python3 ep2_sekil_avi.py                 # tam bölüm → renders/umay_zipzip_bolum2_sekil_avi.mp4
"""
import argparse
import json
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
from engine.characters import draw_umay, draw_zipzip, draw_flower, draw_sparkles, umay_arm_pose, darken_c
from engine import props as P
from engine import props2 as Q
from engine import world
from senaryo_sekil_avi import BOLUMLER, A, U, Z
from ep1_renkli_kelebekler import _spring, _gait, _ease_edges, hop, blink, music_bed, title_panel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_DIR = os.path.join(ROOT, "assets", "vo_ep2")
LOCK_PATH = os.path.join(ROOT, "build", "ep2_slots.json")
OUT_DEFAULT = os.path.join(ROOT, "renders", "umay_zipzip_bolum2_sekil_avi.mp4")
STYLE = "cizgi"
DOF = {"clouds": 1.6, "far": 4.5, "mid": 2.4}
SPAN = 11600
WALK_V = 135.0
STRIDE_W = 140.0
GAP = 0.55
DANCE_LEN = 9.0
SONG_LEN = 6.0
FINAL_DANCE = 10.0
SKY = ("#3F96E6", "#BFE2F8")
KINDS = ("daire", "kare", "ucgen")

# ---------------------------------------------------------------- dünyadaki nesneler
HOUSE_X = 300
BOX0 = HOUSE_X + 210                 # kutu ilk açılışta kapının önünde
DAIRE_ROLL = (1460, 2700)            # D1: yuvarlanıp kaçan parça
BALL0 = (2290, 878)
BUSH = (2380, 880)
STUMP_D = (2990, 885)                # kurabiyeler
WHEEL_X = 3720                       # el arabası
PIECE_D = (3655, GROUND_Y - 34)      # tekerleğin yanındaki daire parça
FLOWERBED = [4440, 4520, 4620, 4700]
PIECE_K = (4570, GROUND_Y - 6)
HOUSE2_X = 5380                      # kare pencereli ev
GIFT = (6130, 890)
BLANKET = (6850, 960)
LAKE = (7780, 990, 380, 78)
PIECE_T = (7540, GROUND_Y - 4)
BOAT_X = (7600, 8020)
STUMP_T = (8480, 885)                # karpuz
HOUSE3_X = 9420                      # üçgen çatılı ev
BUNTING = (9930, 10420, 560)

SC = {
    "A1": dict(x=HOUSE_X + 20, cam=(160, 150, 1.0), pre=SONG_LEN, post=0.8, song=True),
    "A2": dict(x=HOUSE_X + 330, cam=(-40, 590, 1.15), focus=(BOX0, GROUND_Y - 120), pre=3.5, post=1.5),
    "A3": dict(x=HOUSE_X + 330, cam=(60, 560, 1.05), focus=(BOX0, GROUND_Y - 120), pre=0.8, post=3.0),
    "D1": dict(x=1300, cam=(260, 580, 1.0), focus="roll", pre=1.0, post=2.0),
    "D2": dict(x=1300, cam=(220, 230, 1.0), focus="sun", up=True, pre=2.0, post=2.5),
    "D3": dict(x=2060, cam=(200, 640, 1.25), focus=(BALL0[0], BALL0[1] - 40), pre=2.0, post=3.0),
    "D4": dict(x=2760, cam=(210, 680, 1.4), focus=(STUMP_D[0], STUMP_D[1] - 110), pre=2.0, post=3.0),
    "D5": dict(x=3450, cam=(200, 640, 1.25), focus=(PIECE_D[0], PIECE_D[1]), box=True, pre=2.0, post=3.0),
    "D6": dict(x=3450, cam=(140, 560, 1.0), focus=None, pre=1.0, post=2.5, dance_after="D25"),
    "K1": dict(x=4320, cam=(230, 700, 1.45), focus=(PIECE_K[0], PIECE_K[1] - 20), pre=3.0, post=1.5),
    "K2": dict(x=4320, cam=(170, 680, 1.35), focus="box", box=True, pre=1.0, post=2.5),
    "K3": dict(x=5060, cam=(250, 560, 1.05), focus=(HOUSE2_X + 70, GROUND_Y - 135), pre=2.0, post=2.5),
    "K4": dict(x=5900, cam=(200, 640, 1.25), focus=(GIFT[0], GIFT[1] - 90), pre=2.0, post=3.0),
    "K5": dict(x=6600, cam=(220, 700, 1.3), focus=(BLANKET[0], BLANKET[1] - 40), pre=2.0, post=2.5),
    "K6": dict(x=6600, cam=(140, 560, 1.0), focus=None, pre=1.0, post=2.5, dance_after="K25"),
    "T1": dict(x=7330, cam=(190, 720, 1.45), focus=(PIECE_T[0], PIECE_T[1] - 20), pre=3.0, post=2.0),
    "T2": dict(x=7330, cam=(360, 650, 1.1), focus="boat", pre=1.5, post=2.5),
    "T3": dict(x=8250, cam=(200, 650, 1.3), focus=(STUMP_T[0], STUMP_T[1] - 110), pre=2.0, post=3.0),
    "T4": dict(x=9100, cam=(260, 520, 1.0), focus=(HOUSE3_X, GROUND_Y - 330), box=True, pre=2.0, post=3.0),
    "T5": dict(x=9800, cam=(160, 560, 1.0), focus=None, pre=1.0, post=2.5, dance_after="T22"),
    "F1": dict(x=10700, cam=(120, 600, 1.15), focus="box", box=True, pre=2.5, post=2.0),
    "F2": dict(x=10700, cam=(160, 470, 1.0), focus=None, box=True, pre=1.0, post=4.0, dance_after="F10"),
    "F3": dict(x=10700, cam=(90, 640, 1.3), focus=None, box=True, pre=0.5, post=6.5, end=True),
}

# çerçeve: cümle → (şekil, hedef, yarıçap). hedef "sun" ise güneşin ekran konumu
OUTLINES = {
    "D03": ("daire", "roll", 50), "D07": ("daire", "sun", 130), "D11": ("daire", (BALL0[0], BALL0[1] - 34), 60),
    "D13": ("daire", (STUMP_D[0], STUMP_D[1] - 112), 130), "D19": ("daire", (WHEEL_X + 84, GROUND_Y - 50), 75),
    "K02": ("kare", (PIECE_K[0], PIECE_K[1] - 40), 60), "K13": ("kare", (HOUSE2_X + 70, GROUND_Y - 135), 78),
    "K16": ("kare", (GIFT[0], GIFT[1] - 72), 92),
    "T02": ("ucgen", (PIECE_T[0], PIECE_T[1] - 44), 62), "T08": ("ucgen", "sail", 75),
    "T10": ("ucgen", (STUMP_T[0], STUMP_T[1] - 125), 72), "T15": ("ucgen", (HOUSE3_X, GROUND_Y - 330), 215),
}
EDGES = {"K04": ("kare", 4), "T04": ("ucgen", 3)}       # kenar sayma
TIK = {"D21": "daire", "K10": "kare", "T17": "ucgen"}  # parça deliğine oturur
PIECE_R = 34


def vo_path(cid):
    return os.path.join(VO_DIR, f"{cid}.wav")


LOCK = None


def vo_len(cid, text, who=None):
    global LOCK
    if LOCK is None:
        LOCK = json.load(open(LOCK_PATH)) if os.path.exists(LOCK_PATH) else {}
    if cid in LOCK:
        return LOCK[cid]
    p = vo_path(cid)
    if os.path.exists(p):
        with wave.open(p) as w:
            return w.getnframes() / w.getframerate()
    return 0.4 + 0.075 * len(text)


def save_lock(pl):
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    json.dump({ln["cid"]: round(ln["t1"] - ln["t0"], 3) for ln in pl.lines}, open(LOCK_PATH, "w"), indent=0)


def shape_of(text):
    low = text.lower().replace("İ", "i").replace("I", "ı")
    if "üçgen" in low:
        return "ucgen"
    if "kare" in low:
        return "kare"
    if "daire" in low or "yuvarlak" in low:
        return "daire"
    return None


# ================================================================ ZAMAN ÇİZELGESİ
class Plan:
    def __init__(self):
        self.lines, self.segs, self.scenes, self.ux_keys, self.chapter = [], [], [], [], []
        self.replays = []
        self.T = {}
        self.build()

    def build(self):
        t = 0.0
        cur = SC["A1"]["x"]
        self.ux_keys.append((0.0, cur))
        for b in BOLUMLER:
            ch = b["sekil"]
            ch0 = None
            for code, _, _, lines in b["sahneler"]:
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
                    self.lines.append(dict(cid=cid, who=who, txt=txt, t0=t, t1=t + d, wait=wait, scene=code, ch=ch, shape=shape_of(txt)))
                    self.T[cid] = (t, t + d)
                    t += d + GAP
                    if wait:
                        self.segs.append((t - GAP * 0.5, t + wait, "wait", code))
                        t += wait + 0.3
                    if sc.get("dance_after") == cid:
                        d0 = t + 0.6
                        L = DANCE_LEN if ch else FINAL_DANCE
                        self.segs.append((d0, d0 + L, "dance", code))
                        t = d0 + L + 0.6
                t += sc.get("post", 2.0)
                self.segs.append((s0, t, "scene", code))
                self.scenes.append(dict(code=code, t0=s0, t1=t, x=sc["x"], ch=ch))
            if ch:
                self.chapter.append((ch0, t, ch))
        self.ux_keys.append((t, cur))
        self.duration = t

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
    for ln in plan().lines:
        if ln["who"] != who or not (ln["t0"] <= t < ln["t1"]):
            continue
        e = envelope(ln["cid"])
        if e is None:
            return 0.4 + 0.3 * math.sin(t * 18)
        i = int((t - ln["t0"]) * FPS * 2)
        if 0 <= i < len(e):
            return clamp((e[i] - 0.12) / 0.7) ** 0.8
    return 0.0


def Tq(cid, k=0, default=None):
    v = plan().T.get(cid)
    return v[k] if v else default


# ================================================================ ön hesap
class State:
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
                    ux[i] = lerp(x0, x1, ease_io(u) if t1 - t0 < 4 else _ease_edges(u, t1 - t0))
                    break
        self.ux = ux
        zt = np.array([self._zip_target(pl, t, ux[i]) for i, t in enumerate(ts)])
        self.zx = _spring(zt[:, None], w=3.2)[:, 0]
        self.ugait, self.uph = _gait(self.ux, WALK_V, 230, STRIDE_W, 210)
        self.zgait, self.zph = _gait(self.zx, 120, 220, 120, 190)
        cam = np.array([self._cam_target(pl, t, ux[i], self.zx[i]) for i, t in enumerate(ts)])
        self.cam = _spring(cam, w=2.0)
        self.cam[:, 0] = np.maximum(self.cam[:, 0], W / (2 * self.cam[:, 2]) - world.MX + 20)

    @staticmethod
    def _zip_target(pl, t, ux):
        T = pl.T
        base = ux - 175
        if t < pl.scenes[1]["t0"] + 1.0:
            base = max(ux - 175, HOUSE_X - 10) if ux > HOUSE_X + 40 else HOUSE_X - 10
        # A3: kutuya zıplar
        if "A08" in T and T["A08"][0] - 0.8 < t < T["A09"][1]:
            return BOX0 - 40
        # D1: yuvarlanan parçanın peşinden koşar, sonra döner
        if "D01" in T and T["D01"][0] < t < T["D05"][0]:
            return min(roll_x(pl, t) - 80, DAIRE_ROLL[1] - 200)
        # D3: topu burnuyla iter
        if "D09" in T and T["D09"][0] < t < T["D12"][1] + 1.0:
            return BALL0[0] - 140
        # D4: kurabiyeleri koklar
        if "D16" in T and T["D15"][1] - 0.3 < t < T["D17"][1] + 1.0:
            return STUMP_D[0] - 150
        # K2: parçayı alıp kutuya götürür
        if "K06" in T and T["K06"][0] - 1.5 < t < T["K08"][0]:
            return lerp(PIECE_K[0] - 110, ux + 150 - 150, smooth((t - T["K06"][0] + 0.5) / 1.6))
        # K4: kemik
        if "K17" in T and T["K17"][0] < t < T["K18"][1] + 1.5:
            return GIFT[0] - 140
        # T3: karpuzun yanında
        if "T12" in T and T["T11"][0] < t < T["T13"][1] + 1.0:
            return ux + 150
        return base

    @staticmethod
    def _cam_target(pl, t, ux, zx):
        sc = pl.scene_at(t)
        if pl.seg_at(t, "travel"):
            return (ux + 200, 560, 1.0)
        S = SC[sc["code"]]
        dx, cy, z = S["cam"]
        if S.get("song"):
            u = smooth((t - 0.5) / max(SONG_LEN - 1.0, 1.0))
            return (sc["x"] + 160, lerp(150, 520, u), 1.0)
        if pl.seg_at(t, "dance"):
            return (ux + 60, 560, 1.0)
        # kenar sayarken parçaya yaklaş
        for cid in EDGES:
            if cid in pl.T and pl.T[cid][0] - 0.6 < t < pl.T[cid][1] + 0.6:
                px = PIECE_K if cid.startswith("K") else PIECE_T
                return (px[0] - 30, px[1] - 90, 2.1)
        if sc["code"] == "D1" and "D01" in pl.T:
            return (lerp(sc["x"] + dx, min(roll_x(pl, t), 2200), 0.5), cy, z)
        return (sc["x"] + dx, cy, z)


def roll_x(pl, t):
    """D1'de yuvarlanan daire parçanın x'i."""
    T = pl.T
    if "D01" not in T:
        return DAIRE_ROLL[0]
    u = clamp((t - T["D01"][0] + 0.3) / (T["D05"][1] - T["D01"][0] + 1.5))
    return lerp(DAIRE_ROLL[0], DAIRE_ROLL[1], u ** 1.2)


def box_mode(pl, t):
    """Kutu nerede: 'house' (açılış), 'back' (Zıpzıp'ın sırtında), 'ground' (Umay'ın yanında) + geçiş oranı."""
    if "A09" in pl.T and t < pl.T["A09"][1] + 2.5:
        return "house", 0.0
    sc = pl.scene_at(t)
    if pl.seg_at(t, "travel"):
        return "back", 0.0
    if SC[sc["code"]].get("box"):
        return "ground", smooth((t - sc["t0"]) / 0.9)
    return "back", 0.0


def box_ground_x(pl, t):
    return pl_ux(t) + 150


def pl_ux(t):
    return STATE.ux[min(max(int(t * FPS), 0), STATE.n - 1)]


def focus_point(pl, code, t, ux, zx):
    f = SC[code].get("focus")
    if f is None:
        return None
    if f == "sun":
        cx = STATE.cam[min(int(t * FPS), STATE.n - 1)][0] if STATE is not None else ux
        return np.array([cx + 430, 190.0])
    if f == "roll":
        return np.array([roll_x(pl, t), GROUND_Y - 40.0])
    if f == "box":
        return np.array([ux + 150, GROUND_Y - 120.0])
    if f == "boat":
        return np.array([boat_x(pl, t), LAKE[1] - 90.0])
    return np.array(f, float)


def boat_x(pl, t):
    T = pl.T
    if "T06" not in T:
        return BOAT_X[0]
    return lerp(BOAT_X[0], BOAT_X[1], smooth((t - T["T06"][0]) / 14.0))


def sun_pos(cx, z):
    return cx + 430 / z, 190.0


# ================================================================ parçalar
def filled_at(pl, t):
    if "F07" in pl.T and t > pl.T["F07"][0] - 0.5:   # finalde parçalar kutudan uçup resim olur
        return ()
    return tuple(k for cid, k in TIK.items() if cid in pl.T and t >= pl.T[cid][0])


def piece_state(pl, t, kind, anchors, box_top):
    """Bir parçanın konumu: (x, y, dönüş, ölçek) ya da None (kutunun içinde/görünmez)."""
    T = pl.T
    if kind in filled_at(pl, t):
        return None
    # açılış: kutudan fırlar, sağa uçar
    if "A09" in T:
        a = T["A09"][0]
        if t < a:
            return None
        if t < a + 1.6:
            u = (t - a) / 1.6
            k = KINDS.index(kind)
            x = lerp(BOX0, BOX0 + 700 + 260 * k, u)
            y = lerp(GROUND_Y - 150, GROUND_Y - 60, u) - math.sin(math.pi * u) * (330 + 60 * k)
            return x, y, u * 9, 1.0
    if kind == "daire":
        if "D01" in T and t < Tq("D05", 1, 0) + 1.5:
            x = roll_x(pl, t)
            return x, GROUND_Y - PIECE_R, (x - DAIRE_ROLL[0]) / PIECE_R, 1.0
        if "D18" in T and t < T["D18"][1]:
            return PIECE_D[0], PIECE_D[1], 0.0, 1.0
        if "D20" in T and t < T["D21"][0]:
            h = anchors.get("umay_hand")
            u = clamp((t - T["D20"][0]) / max(T["D21"][0] - T["D20"][0], 0.1))
            if h is not None and u < 0.55:
                return h[0], h[1] + 10, 0.0, 0.9
            return lerp(h[0] if h else box_top[0], box_top[0] - 62, smooth((u - 0.55) / 0.45)), box_top[1] - 60 * (1 - u), 0.0, 0.9
        return None
    if kind == "kare":
        if "K06" in T and t < T["K06"][0] - 0.5:
            return PIECE_K[0], PIECE_K[1] - PIECE_R, 0.0, 1.0
        n = anchors.get("nose")
        if "K08" in T and t < T["K08"][0]:
            # Zıpzıp ağzında taşır, daire deliğe dener (titreyerek)
            u = clamp((t - T["K07"][0]) / max(T["K07"][1] - T["K07"][0] + 0.5, 0.1))
            if n is not None and t < T["K07"][0]:
                return n[0] + 22, n[1] + 20, 0.0, 0.9
            return box_top[0] - 62 + 4 * math.sin(t * 40) * (1 - u), box_top[1] - 8, 0.0, 0.9
        if "K09" in T and t < T["K09"][0]:
            u = clamp((t - T["K08"][0]) / 0.9)
            return lerp(box_top[0] - 62, pl_ux(t) + 60, u), box_top[1] - 10 - math.sin(math.pi * u) * 160, u * 6, 0.9
        if "K10" in T and t < T["K10"][0]:
            h = anchors.get("umay_hand")
            u = clamp((t - T["K09"][0]) / max(T["K10"][0] - T["K09"][0], 0.1))
            if h is not None and u < 0.55:
                return h[0], h[1] + 10, 0.0, 0.9
            return lerp(h[0] if h else box_top[0], box_top[0], smooth((u - 0.55) / 0.45)), box_top[1] - 60 * (1 - u), 0.0, 0.9
        return None
    if kind == "ucgen":
        if "T05" in T and t < T["T05"][1] + 0.8:
            return PIECE_T[0], PIECE_T[1] - PIECE_R, 0.0, 1.0
        if "T16" in T and t < T["T16"][0]:
            # kutunun kapağının üstünde, gevşek duruyor
            if t < T["T05"][1] + 1.6:
                u = (t - T["T05"][1] - 0.8) / 0.8
                return lerp(PIECE_T[0], box_top[0] + 40, u), lerp(PIECE_T[1] - PIECE_R, box_top[1] - 26, u) - math.sin(math.pi * u) * 60, 0.0, 0.8
            return box_top[0] + 40, box_top[1] - 26, 0.0, 0.7
        if "T17" in T and t < T["T17"][0]:
            u = clamp((t - T["T16"][0]) / max(T["T17"][0] - T["T16"][0], 0.1))
            return lerp(box_top[0] + 40, box_top[0] + 62, smooth(u)), box_top[1] - 26 - math.sin(math.pi * u) * 70, 0.0, 0.8
        return None
    return None


# ================================================================ ÇİZİM
def draw_world_props(p, pl, t, cx, z):
    T = pl.T
    vis = lambda x, w=600: abs(x - cx) < W / (2 * z) + w
    if vis(HOUSE_X, 500):
        gm = window(t, pl.scenes[1]["t0"] + 0.5, pl.scenes[2]["t1"], 0.8)
        P.big_house(p, HOUSE_X, GROUND_Y - 15, 1.15, door=0.0, grandma=gm, t=t)
    if vis(900, 300):
        world.fence(p, 820, 940, GROUND_Y - 30, 0.8)
    if vis(STUMP_D[0], 400):
        Q.stump(p, STUMP_D[0], STUMP_D[1], 1.0)
        gi = -1
        if "D14" in T:
            a, b = T["D14"]
            if a <= t < b + 1.2:
                gi = int(clamp((t - a) / max(b - a, 0.1)) * 3.999)
        Q.cookie_plate(p, STUMP_D[0], STUMP_D[1] - 72, 1.0, glow_idx=gi)
    if vis(WHEEL_X, 400):
        rot = 0.0
        if "D19" in T and T["D19"][0] < t < T["D19"][1] + 1.5:
            rot = (t - T["D19"][0]) * 3.0
        Q.wheelbarrow(p, WHEEL_X, GROUND_Y, 1.2, rot=rot)
    for i, fx in enumerate(FLOWERBED):
        if vis(fx, 200):
            col = [P.COL["kirmizi"], P.COL["sari"], P.COL["mor"], P.COL["turuncu"]][i]
            draw_flower(p, fx, GROUND_Y - 4 + (i % 2) * 6, 0.85, col, center=hexrgb("#FFE36E"), sway=math.sin(t * 1.4 + i) * 0.3, seed=f"fb{i}")
    for hx, code in ((HOUSE2_X, "K13"), (HOUSE3_X, "T15")):
        if vis(hx, 500):
            wg = window(t, Tq("K11", 0, 1e9), Tq("K14", 1, -1) + 1.0, 0.5) if code == "K13" else 0.0
            rg = window(t, Tq("T14", 0, 1e9), Tq("T15", 1, -1) + 1.5, 0.5) if code == "T15" else 0.0
            Q.shape_house(p, hx, GROUND_Y - 10, 1.0, window_glow=wg, roof_glow=rg)
    if vis(GIFT[0], 400):
        op = smooth((t - Tq("K15", 1, 1e9)) / 0.8)
        Q.gift_box(p, GIFT[0], GIFT[1], 0.85, open_u=op, glow=window(t, Tq("K16", 0, 1e9), Tq("K16", 1, -1) + 1.0, 0.4))
    if vis(LAKE[0], 800):
        P.lake(p, *LAKE, t)
        Q.paper_boat(p, boat_x(pl, t), LAKE[1] - 6, 0.85, t, glow=window(t, Tq("T07", 0, 1e9), Tq("T09", 1, -1) + 0.8, 0.4))
    if vis(STUMP_T[0], 400):
        Q.stump(p, STUMP_T[0], STUMP_T[1], 1.0)
        p.part(lambda c: ellipse(c, STUMP_T[0], STUMP_T[1] - 74, 90, 20), (1, 1, 1), seed="wpl")
        held = "T10" in T and t > T["T10"][1] - 0.2
        for k in range(1 if held else 2):
            Q.watermelon_slice(p, STUMP_T[0] - 30 + 60 * k, STUMP_T[1] - 118, 0.75, rot=-0.15 + 0.3 * k, seed=f"wm{k}")
    if vis(BUNTING[0], 800):
        Q.bunting(p, BUNTING[0], BUNTING[1], BUNTING[2], t)


def draw_front_props(p, pl, t, cx, z, anchors):
    T = pl.T
    vis = lambda x, w=600: abs(x - cx) < W / (2 * z) + w
    if vis(BUSH[0], 500):
        roll = 0.0
        if "D09" in T and T["D09"][0] < t < T["D12"][1] + 1.0:
            roll = 30 * math.sin((t - T["D09"][0]) * 2.2)
        P.ball(p, BALL0[0] + roll, BALL0[1], 34, roll / 34)
        P.bush(p, BUSH[0], BUSH[1], 1.0, seed=3)
    if vis(BLANKET[0], 500):
        gi = ()
        if "K20" in T:
            a, b = T["K20"]
            if a <= t < b + 1.2:
                gi = tuple(range(int(clamp((t - a) / max(b - a, 0.1)) * 3.999)))
        Q.checker_blanket(p, BLANKET[0], BLANKET[1], 1.7, glow_idx=gi)
    if "D18" in T and vis(WHEEL_X, 400):
        pass


def exit_time(pl):
    for s_ in pl.segs:
        if s_[2] == "travel" and s_[3] == "A2":
            return s_[0]
    return 0.0


def idle_play(pl, t):
    sc = pl.scene_at(t)
    last = max((l["t1"] for l in pl.lines if l["scene"] == sc["code"]), default=sc["t1"])
    if SC[sc["code"]].get("focus") is None or pl.seg_at(t, "travel") or pl.seg_at(t, "dance"):
        return False, 0.0
    if last + 1.8 < t < sc["t1"] - 1.0:
        return True, t - last - 1.8
    return False, 0.0


def umay_state(pl, t, i, focus):
    T = pl.T
    st = dict(phase=STATE.uph[i], gait=STATE.ugait[i], stride_w=STRIDE_W)
    ux = STATE.ux[i]
    v = STATE.ux[min(i + 1, STATE.n - 1)] - STATE.ux[max(i - 1, 0)]
    f = 1
    if abs(v) > 0.3:
        f = 1 if v > 0 else -1
    elif focus is not None and focus[0] < ux - 60:
        f = -1
    st["facing"] = f
    ln = pl.line_at(t, U, pad=0.15)
    pose, happy, sour = "idle", 0.0, 0.0
    jumps = []
    for l in pl.lines:
        if l["shape"] and (l["who"] == U or (l["who"] == A and l["txt"][:3] in ("Dai", "Kar", "Üçg", "İşt", "Tık"))):
            jumps.append(l["t0"] + 0.12)
    if ln:
        txt = ln["txt"]
        if txt.startswith("Hoşça"):
            pose = "wave"
        elif txt.startswith(("Dur", "Ooo", "Zıpzıp, bu", "Ev!")):
            pose = "point"
        elif txt.startswith("Hi hi"):
            pose, happy = "laugh", 1.0
        elif "Ham" in txt:
            pose, happy = "think", 1.0
        elif "deliğe" in txt:
            pose = "point"
        elif ln["shape"] or txt.startswith(("Günaydın", "Parçaları")):
            pose = "cheer"
    if pl.seg_at(t, "wait") and pose == "idle":
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
        pose = ["cheer", "wave", "cheer", "point"][int(t / 0.6) % 4]
        jumps.append(t - (t % 1.2))
    # karpuz elde
    if "T11" in T and T["T10"][1] - 0.2 < t < T["T13"][1] + 1.0:
        pose = "think"
    if SC[pl.scene_at(t)["code"]].get("end"):
        pose, f = "wave", 1
        st["facing"] = 1
    st["arms"] = umay_arm_pose(pose, t)
    st["jump"] = hop(t, jumps, 36)
    st["happy"] = happy
    st["sour"] = sour
    st["blink"] = blink(t, "umay")
    st["mouth"] = mouth_of(U, t)
    st["look"] = 0.0 if SC[pl.scene_at(t)["code"]].get("end") else 0.4
    if focus is not None:
        dx = (focus[0] - ux) * f
        dy = focus[1] - (GROUND_Y - 250)
        st["eye_dx"] = clamp(dx / 300, -1, 1)
        st["eye_dy"] = clamp(dy / 300, -1, 1)
        st["look"] = clamp(dx / 400, -0.5, 0.5)
    if SC[pl.scene_at(t)["code"]].get("up"):
        st["eye_dy"] = -1.0
        st["tilt"] = -0.08
    if pl.seg_at(t, "wait"):
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
    if "A08" in T:
        zl.append(T["A08"][1] + 0.1)      # kutuya zıplar
    st["jump"] = hop(t, zl, 34, 0.4)
    if "A08" in T and T["A08"][1] < t < T["A08"][1] + 0.9:
        st["jump"] = max(st["jump"], 120 * math.sin(math.pi * (t - T["A08"][1]) / 0.9))
    play, pu = idle_play(pl, t)
    st["wag"] = 1.8 if (pl.line_at(t, Z, 0.8) or pl.seg_at(t, "dance") or play) else 1.1
    if play:
        st["jump"] = max(st["jump"], hop(pu % 3.0, [1.2], 30, 0.4))
    st["blink"] = blink(t, "zipzip", 3.0)
    if focus is not None and focus[1] < GROUND_Y - 300:
        st["look_up"] = 0.6
        st["eye_dy"] = -0.8
    if "K07" in T and T["K07"][0] - 0.3 < t < T["K08"][1] + 0.5:
        st["tilt"] = 0.22
    if "T12" in T:
        a, b = T["T12"]
        if a - 0.6 <= t < a + (b - a) * 0.7:
            st["sneeze"] = -smooth((t - a + 0.6) / ((b - a) * 0.7 + 0.6))
        elif a + (b - a) * 0.7 <= t < b + 0.4:
            k = (t - a - (b - a) * 0.7) / ((b - a) * 0.3 + 0.4)
            st["sneeze"] = math.sin(math.pi * min(1, k * 2.2)) * (1 - k)
    if "F10" in T and t > T["F07"][0]:
        st["happy"] = 1.0 if (t % 2.4) > 1.2 else 0.0
    return st


def line_with(pl, t, test, pad_after=1.4):
    best = None
    for ln in pl.lines:
        if test(ln) and ln["t0"] - 0.1 <= t < ln["t1"] + pad_after:
            best = ln
    return best


def draw_overlay(p, pl, t):
    ch, c0, c1 = pl.chapter_at(t)
    if ch:
        Q.draw_shape_badge(p, ch, smooth((t - c0) / 0.8) * (1 - smooth((t - c1 + 0.8) / 0.8)))
    best = line_with(pl, t, lambda l: l["shape"] is not None and l["scene"][0] != "F" or l["cid"] in ("F02", "F04", "F06"))
    dance = pl.seg_at(t, "dance") if ch else None
    if best or dance:
        key = best["shape"] if best else ch
        if best and best["cid"] in ("F02", "F04", "F06"):
            key = {"F02": "daire", "F04": "kare", "F06": "ucgen"}[best["cid"]]
        t0 = best["t0"] if best else dance[0]
        t1 = best["t1"] + 1.4 if best else dance[1]
        a = smooth((t - t0 + 0.1) / 0.25) * (1 - smooth((t - t1 + 0.35) / 0.35))
        if dance and not best:
            a = window(t, dance[0] + 0.5, dance[1] - 0.5, 0.5)
        pop = ease_out_back(clamp((t - t0 + 0.1) / 0.45)) * (1 + 0.04 * math.sin(t * 10.5) * bool(dance))
        P.draw_word(p, Q.SHAPE_WORD[key], Q.SHAPE_COL[key], a, max(pop, 0.01), W / 2, 175, size=170)
    # başlık
    t_end = pl.T["A02"][1] + 0.8 if "A02" in pl.T else SONG_LEN
    if t < t_end + 1.0:
        a = window(t, 0.6, t_end, 0.6)
        if a > 0:
            from ep01_renkli_kelebek import draw_title
            title_panel(p, a, 330)
            draw_title(p, a, max(ease_out_back((t - 0.5) / 0.9), 0.01) * (1 + 0.02 * math.sin(t * 5.2)), "Umay ile Zıpzıp", "Şekil Avı")
            for k, kind in enumerate(KINDS):
                ang = t * 0.9 + k * 2 * math.pi / 3
                Q.piece(p, kind, W / 2 + math.cos(ang) * 620, 380 + math.sin(ang) * 210, 44 * a, rot=t * 0.8 + k, seed=f"tp{k}")
    sc = pl.scene_at(t)
    if SC[sc["code"]].get("end"):
        from ep01_renkli_kelebek import draw_title
        u = t - sc["t0"]
        title_panel(p, clamp(u / 0.6), 230, h=270)
        draw_title(p, clamp(u / 0.6), max(ease_out_back(u / 0.8), 0.01), "Umay ile Zıpzıp", "Yakında yeni maceralarda!", y=200, sub_dy=120, size=130)


def final_picture(p, pl, t, ux):
    """F2: parçalar kutudan uçar, gökyüzünde ev resmi olur (kare ev, üçgen çatı, daire güneş)."""
    T = pl.T
    if "F07" not in T or t < T["F07"][0] - 0.5:
        return
    u = smooth((t - T["F07"][0] + 0.5) / 2.0)
    fade = 1 - smooth((t - Tq("F11", 0, 1e9) + 0.6) / 0.6)    # kapanış kartından önce söner
    if fade <= 0.01:
        return
    bx, by = box_ground_x(pl, t), GROUND_Y - 130
    targets = {"kare": (ux + 120, 430, 120), "ucgen": (ux + 120, 255, 175), "daire": (ux - 260, 250, 75)}
    for kind, (tx, ty, tr) in targets.items():
        k = KINDS.index(kind)
        x = lerp(bx + (k - 1) * 62, tx, u)
        y = lerp(by, ty, u) - math.sin(math.pi * u) * 120
        r = lerp(22, tr, u) * (fade if u > 0.99 else 1.0)
        gl = window(t, T["F08"][0] + 1.0 * k, T["F08"][0] + 1.0 * k + 1.2, 0.3) if "F08" in T else 0.0
        if kind == "daire" and u > 0.95:
            for q in range(10):
                a = q * math.pi / 5 + t * 0.4
                p.stroke(lambda c, a=a: (c.move_to(x + math.cos(a) * (r + 18), y + math.sin(a) * (r + 18)),
                                         c.line_to(x + math.cos(a) * (r + 48), y + math.sin(a) * (r + 48))), Q.SHAPE_COL["daire"], width=8)
        if kind == "kare" and u > 0.95:
            Q.piece(p, kind, x, y, r, glow=gl, seed="fpk")
            p.part(lambda c: (c.rectangle(x - 26, y + 18, 52, r - 18)), hexrgb("#8C5A3C"), seed="fpdoor")
            p.part(lambda c: (c.rectangle(x + 40, y - 70, 50, 50)), hexrgb("#9FD0FA"), seed="fpwin")
        else:
            Q.piece(p, kind, x, y, r, glow=gl, seed=f"fp{kind}")


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
        border = cv2.BORDER_CONSTANT if L["name"] == "clouds" else cv2.BORDER_REPLICATE
        composite(rgb, cv2.warpAffine(L["img"], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=border))
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
    sx_, sy_ = sun_pos(cx, z)
    p.glow(sx_, sy_, 230, hexrgb("#FFF3C4"), 0.8)
    for k in range(12):
        a = k * math.pi / 6 + t * 0.15
        p.part(lambda c, a=a: ellipse(c, sx_ + math.cos(a) * 112, sy_ + math.sin(a) * 112, 22, 8, a), hexrgb("#FFC94A"), seed=f"sr{k}")
    p.part(lambda c: circle(c, sx_, sy_, 76), hexrgb("#FFD45C"), seed="sun")

    sc = pl.scene_at(t)
    T = pl.T
    ux, zx = STATE.ux[i], STATE.zx[i]
    focus = focus_point(pl, sc["code"], t, ux, zx)
    draw_world_props(p, pl, t, cx, z)
    for sx, w_ in (((ux, 62), (zx + 10, 90)) if t > exit_time(pl) else ()):
        p.part(lambda c, sx=sx, w_=w_: ellipse(c, sx, GROUND_Y + 4, w_, 12), hexrgb("#6E7FA6"), alpha=0.25, line=False, seed=f"sh{w_}")

    # kutu (zeminde ise karakterlerin arkasında)
    mode, mu = box_mode(pl, t)
    filled = filled_at(pl, t)
    gl = {}
    for q, cid in (("daire", "F01"), ("kare", "F03"), ("ucgen", "F05")):
        if cid in T and T[cid][0] < t < T[cid][1] + 4.0:
            gl[q] = 1.0
    shake = 0.0
    if "A08" in T and T["A08"][1] + 0.5 < t < T["A09"][0] + 0.8:
        shake = 0.08 * math.sin(t * 40)
    if "K08" in T and T["K08"][0] - 0.2 < t < T["K08"][0] + 0.4:
        shake = 0.06 * math.sin(t * 50)
    box_top = None
    if mode == "house":
        bx, by = BOX0, GROUND_Y
        a_box = smooth((t - Tq("A05", 0, 0)) / 0.8)
        if a_box > 0.01:
            Q.shape_box(p, bx, by, 0.75, filled=filled, lid_shake=shake)
        box_top = (bx, by - 0.75 * 128)
    elif mode == "ground":
        bx, by = box_ground_x(pl, t), GROUND_Y
        Q.shape_box(p, bx, by, 0.75, filled=filled, glow=gl, lid_shake=shake)
        box_top = (bx, by - 0.75 * 128)

    anchors = {}
    hidden = t < exit_time(pl) - 0.2
    zst = zipzip_state(pl, t, i, focus)
    ust = umay_state(pl, t, i, focus)
    if hidden:
        a_z, a_u = {"nose": (0, 0), "collar": (0, 0)}, {}
    else:
        a_z = draw_zipzip(p, zx, GROUND_Y, 0.95, zst)
    anchors["nose"] = inv.transform_point(*a_z["nose"])
    anchors["collar"] = inv.transform_point(*a_z["collar"])
    if mode == "back" and not hidden:
        # Zıpzıp'ın sırtında küçük çanta gibi (Umay'dan önce çizilir: Zıpzıp arkada kalınca kutu da arkada kalır)
        cxl, cyl = anchors["collar"]
        bx = cxl - 70 * zst["facing"]
        by = cyl - 18 + 4 * math.sin(STATE.zph[i] * 2)
        Q.shape_box(p, bx, by, 0.42, filled=filled)
        box_top = (bx, by - 0.42 * 128)
    if not hidden:
        a_u = draw_umay(p, ux, GROUND_Y, 1.0, ust)
    hands = a_u.get("hands", {})
    if 1 in hands:
        anchors["umay_hand"] = inv.transform_point(*hands[1])
    if box_top is None:
        box_top = (BOX0, GROUND_Y - 96)
    # parçalar
    for kind in KINDS:
        ps = piece_state(pl, t, kind, anchors, box_top)
        if ps:
            x, y, rot, s = ps
            Q.piece(p, kind, x, y, PIECE_R * s, rot=rot, glow=0.6 if pl.seg_at(t, "wait") else 0.0, seed=f"pz{kind}")
    # tık!
    for cid, kind in TIK.items():
        if cid in T:
            u = (t - T[cid][0]) / 0.9
            if 0 < u < 1 and box_top:
                draw_sparkles(p, box_top[0], box_top[1] - 20, u, color=Q.SHAPE_COL[kind], n=9, radius=140, seed=cid)
    # karpuz elde
    if "T11" in T and T["T10"][1] - 0.2 < t < T["T13"][1] + 1.0 and "umay_hand" in anchors:
        hx, hy = anchors["umay_hand"]
        bitten = 1 if t > T["T11"][0] + 0.4 else 0
        Q.watermelon_slice(p, hx, hy - 30, 0.6, rot=0.2, bitten=bitten, seed="wmh")
    # kemik
    if "K17" in T and T["K15"][1] + 0.6 < t < pl.chapter_at(T["K17"][0])[2]:
        u = clamp((t - T["K15"][1] - 0.6) / 1.0)
        n_ = anchors["nose"]
        if t < T["K17"][1]:
            Q.bone(p, GIFT[0], GIFT[1] - 140 - 60 * ease_out_back(u), 0.8, rot=0.2)
        else:
            Q.bone(p, n_[0] + 18 * zst["facing"], n_[1] + 22, 0.7, rot=0.1)
    draw_front_props(p, pl, t, cx, z, anchors)
    final_picture(p, pl, t, ux)

    # şekil çerçeveleri
    for cid, (kind, tgt, r) in OUTLINES.items():
        if cid not in T:
            continue
        a0, a1 = T[cid]
        if not (a0 - 0.2 < t < a1 + 2.2):
            continue
        prog = clamp((t - a0) / 0.9)
        alpha = 1 - smooth((t - a1 - 1.6) / 0.6)
        if tgt == "sun":
            x, y = sx_, sy_
        elif tgt == "roll":
            x, y = roll_x(pl, t), GROUND_Y - PIECE_R
        elif tgt == "sail":
            x, y = boat_x(pl, t) + 40, LAKE[1] - 80
        else:
            x, y = tgt
        Q.outline_shape(p, kind, x, y, r, prog, alpha)
    # kenar sayma: her sayıda bir kenar parlar
    for cid, (kind, n) in EDGES.items():
        if cid in T:
            a0, a1 = T[cid]
            if a0 < t < a1 + 1.0:
                pc = PIECE_K if kind == "kare" else PIECE_T
                k = int(clamp((t - a0) / max(a1 - a0, 0.1)) * (n + 0.999))
                for q in range(min(k, n)):
                    Q.edge_highlight(p, kind, pc[0], pc[1] - PIECE_R, PIECE_R, q, col=(1, 1, 1))
    # soru bekleme
    wseg = pl.seg_at(t, "wait")
    if wseg and focus is not None:
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
    # cevaplarda ışıltı
    for ln in pl.lines:
        if ln["who"] == A and ln["shape"] and ln["txt"][:3] in ("Dai", "Kar", "Üçg") and ln["txt"].endswith("!"):
            u = (t - ln["t0"]) / 1.1
            if 0 < u < 1:
                tgt = focus if focus is not None else (ux + 150, 520)
                draw_sparkles(p, tgt[0], tgt[1] - 30, u, n=8, radius=130, seed=ln["cid"])
    # hapşırık: karpuz suyu damlaları
    if "T12" in T:
        a, b = T["T12"]
        u = (t - (a + (b - a) * 0.7)) / 1.0
        if 0 < u < 1:
            n_ = anchors["nose"]
            for k in range(8):
                ang = -0.9 + k * 0.25
                d = 30 + 140 * ease_io(u) * (0.6 + 0.6 * hash01(k))
                p.part(lambda c, ang=ang, d=d: circle(c, n_[0] + math.cos(ang) * d, n_[1] + math.sin(ang) * d * 0.6, 7 * (1 - u * 0.5)),
                       hexrgb("#F2665C"), alpha=1 - u, seed=f"jc{k}", lw=0.4)
    # dans: şekiller zıplar
    dseg = pl.seg_at(t, "dance")
    if dseg and dseg[3] != "A1":
        ch = pl.chapter_at(t)[0]
        kinds = [ch] * 4 if ch else []       # finalde nesne yok: gökyüzündeki ev resmi yeter
        for k, kind in enumerate(kinds):
            app = clamp((t - dseg[0] - 0.6 - k * 0.4) / 0.5) * (1 - clamp((t - dseg[1] + 1.2) / 0.8))
            if app <= 0:
                continue
            ang = math.pi * (0.15 + 0.7 * k / 3)
            x = ux + 40 - math.cos(ang) * 470
            y = 600 - math.sin(ang) * 230 - abs(math.sin(t * math.pi / 0.6 + k)) * 26
            Q.piece(p, kind, x, y, 40 * ease_out_back(app), rot=t * 2 + k, seed=f"dn{k}")
    dyn.surface.flush()
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
    fade = clamp(t / 0.8) * clamp((pl.duration - t) / 1.2)
    rgb = rgb * fade + PAPER[::-1][None, None, :] * (1 - fade)
    return (post_process(STYLE, rgb) * 255 + 0.5).astype(np.uint8)


# ================================================================ ses
def build_audio(path, with_music=True):
    from engine import audio as Au
    pl = plan()
    dur = pl.duration
    sfx, vo = Au.Bus(dur), Au.Bus(dur)
    hz = lambda nm: Au.midi_hz(Au.n(nm))

    def mode_at(t0, mid):
        if pl.seg_at(mid, "wait") or pl.seg_at(t0, "wait"):
            return "soft"
        if pl.seg_at(mid, "dance"):
            return "dance"
        if pl.seg_at(mid, "travel"):
            return "travel"
        return "calm"

    music = music_bed(dur, mode_at)
    T = pl.T
    sfx.add(0.9, Au.sparkle(base=Au.n("G5")), 0.28)
    for ln in pl.lines:
        if ln["shape"] and ln["who"] == A and ln["txt"][:3] in ("Dai", "Kar", "Üçg"):
            sfx.add(ln["t0"], Au.pop(), 0.22)
            sfx.add(ln["t0"] + 0.05, Au.sparkle(), 0.22)
    for s in pl.segs:
        if s[2] == "wait":
            sfx.add(s[0] + 0.2, Au.glock(hz("G6"), 0.8), 0.08)
    for cid in TIK:                         # tık!
        if cid in T:
            sfx.add(T[cid][0], Au.pop(), 0.4)
            for k, nm in enumerate(("C6", "E6", "G6")):
                sfx.add(T[cid][0] + 0.08 + k * 0.09, Au.glock(hz(nm), 0.7), 0.12)
    for cid, (kind, n) in EDGES.items():  # kenar sayma
        if cid in T:
            a, b = T[cid]
            for k in range(n):
                sfx.add(a + (b - a) * (k + 0.5) / (n + 0.6), Au.xylo(hz(["C5", "E5", "G5", "C6"][k])), 0.14)
    if "A09" in T:
        sfx.add(T["A09"][0] - 0.1, Au.boing(300, 180, 0.25), 0.3)
        sfx.add(T["A09"][0], Au.whoosh(0.9, 5), 0.3)
    if "K08" in T:
        sfx.add(T["K08"][0], Au.boing(260, 140, 0.25), 0.32)
    if "K15" in T:
        sfx.add(T["K15"][1], Au.sparkle(base=Au.n("C6")), 0.25)
    if "T12" in T:
        a, b = T["T12"]
        sfx.add(a + (b - a) * 0.7, Au.poof(), 0.35)
    if "F07" in T:
        sfx.add(T["F07"][0] - 0.5, Au.whoosh(1.2, 7), 0.3)
        for j in range(6):
            sfx.add(T["F07"][0] + 1.5 + j * 0.25, Au.glock(hz(["C6", "D6", "E6", "G6", "A6", "C7"][j]), 1.0), 0.08)
    for s in pl.segs:
        if s[2] == "travel":
            i0, i1 = int(s[0] * FPS), int(s[1] * FPS)
            ph = STATE.uph[i0:i1]
            for k in np.nonzero(np.diff(np.floor(ph / math.pi)) > 0)[0]:
                sfx.add((i0 + k) / FPS, Au.bass(90, 0.06, 0.015), 0.07)
    spans = []
    for ln in pl.lines:
        p_ = vo_path(ln["cid"])
        if os.path.exists(p_):
            v = Au.load_wav(p_)
            slot = ln["t1"] - ln["t0"] + GAP * 0.8
            if len(v) / Au.SR > slot:
                k = min(len(v) / Au.SR / slot, 1.2)
                v = np.interp(np.arange(0, len(v), k), np.arange(len(v)), v).astype(np.float32)[: int(slot * Au.SR)]
            vo.add(ln["t0"], v, 0.9, pan={U: 0.08, Z: -0.08}.get(ln["who"], 0.0))
            spans.append((ln["t0"], ln["t0"] + len(v) / Au.SR))
    duck = Au.duck_curve(dur, spans, depth=0.32)[: len(music.buf), None]
    music.buf = Au.lowpass(Au.reverb(music.buf, 1.8, 0.24), 8500)
    sfx.buf = Au.reverb(sfx.buf, 1.2, 0.12)
    t_ = np.arange(len(music.buf)) / Au.SR
    fade = np.clip((dur - 0.3 - t_) / 2.0, 0, 1) * np.clip(t_ / 0.5, 0, 1)
    mix = ((music.buf * duck * 0.8 if with_music else 0.0) + sfx.buf * 0.9 + vo.buf * 1.1) * fade[:, None]
    Au.write_wav(path, Au.soft_limit(mix[: int(dur * Au.SR)]))
    return path


# ================================================================ render
_LAYERS = None


def _worker(args):
    k, f0, f1, out = args
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out],
                            stdin=subprocess.PIPE)
    for i in range(f0, f1):
        proc.stdin.write(render_frame(i, _LAYERS).tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def setup():
    global STATE, _LAYERS
    pl = plan()
    STATE = State(pl)
    avoid = (HOUSE_X, BUSH[0], STUMP_D[0], WHEEL_X, HOUSE2_X, GIFT[0], STUMP_T[0], HOUSE3_X, BUNTING[0], BUNTING[1], 10700)
    trees = tuple(x for x in range(120, SPAN + 1500, 2300) if all(abs(x - q) > 450 for q in avoid))
    _LAYERS = world.build_layers(STYLE, cache_dir=os.path.join(ROOT, "build"), tag=f"_ep2_{W}x{H}", span=SPAN, sun=False,
                                 house_on_hill=False, trees_at=trees, sky=SKY)
    for L in _LAYERS:
        sig = DOF.get(L["name"], 0)
        if sig:
            L["img"] = cv2.GaussianBlur(L["img"], (0, 0), sig)
    return pl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    pl = plan()
    if a.plan:
        for s in pl.scenes:
            print(f"{s['code']:3} {int(s['t0'] // 60)}:{s['t0'] % 60:04.1f} – {int(s['t1'] // 60)}:{s['t1'] % 60:04.1f}  x={s['x']}")
        print(f"toplam {int(pl.duration // 60)} dk {pl.duration % 60:.1f} sn · {len(pl.lines)} satır")
        missing = [l['cid'] for l in pl.lines if not os.path.exists(vo_path(l['cid']))]
        print(f"eksik ses: {len(missing)}", missing[:12])
        return
    pl = setup()
    work = os.path.join(ROOT, "build")
    if a.still:
        for s in a.still:
            p_ = os.path.join(work, f"ep2_still_{s:07.1f}.png")
            cv2.imwrite(p_, render_frame(int(s * FPS), _LAYERS))
            print(p_)
        return
    if a.start == 0 and a.end is None:
        save_lock(pl)
    end = a.end if a.end is not None else pl.duration
    f0, f1 = int(a.start * FPS), int(end * FPS)
    n = max(1, a.workers * 6)
    bounds = np.linspace(f0, f1, n + 1).astype(int)
    jobs = [(k, bounds[k], bounds[k + 1], os.path.join(work, f"ep2_seg_{k:03d}.mp4")) for k in range(n) if bounds[k + 1] > bounds[k]]
    with Pool(a.workers) as pool:
        segs = []
        for k, s in enumerate(pool.imap(_worker, jobs)):
            segs.append(s)
            print(f"  parça {k + 1}/{len(jobs)}", flush=True)
    lst = os.path.join(work, "ep2_concat.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    silent = os.path.join(work, "ep2_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    for s in segs:
        os.remove(s)
    wav = build_audio(os.path.join(work, "ep2_mix.wav"))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-ss", str(a.start), "-t", str(end - a.start), "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
