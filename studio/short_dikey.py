"""Dikey (1080x1920) YouTube Shorts: bölümden seçilen anlar, kamera karakterlere yakın, doğrudan dikey çizilir.
Ses: bölümün konuşma + efekt kaydından kesilir, altına kesintisiz yeni bir müzik yatağı konur. Sonda kanal kartı.

    python3 short_dikey.py --out ../shorts/short_bolum1_mavi.mp4
"""
import argparse
import math
import os
import subprocess
import sys
from multiprocessing import Pool

os.environ["UMAY_KARE"] = "1080x1920"   # engine içe aktarılmadan önce
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np

import ep1_renkli_kelebekler as E
from engine import world
from engine import audio as Au
from engine.core import W, H, FPS, GROUND_Y, clamp, smooth, ease_out_back
from engine.styles import Canvas
from engine.characters import draw_umay, draw_zipzip, draw_butterfly, umay_arm_pose
from engine import props as P
import kanal_gorselleri as K

ROOT = E.ROOT
WORK = os.path.join(ROOT, "build", "short")
ZOOM = 1.9                  # dikey kadrajda karakterler büyük (ekran yüksekliğinin ~1/3'ü)
GROUND_AT = 0.70            # zemin ekranın bu yüksekliğinde
# 1. bölüm, mavi: (başlangıç, bitiş) sn — bölüm zaman çizelgesinden
KLIPLER = [
    (57.5, 62.6),    # Bak! Bir kelebek geliyor! — Kelebek! Kelebek!
    (63.0, 64.4),    # Kelebek ne renk?
    (67.6, 72.9),    # Mavi! Evet, mavi! — Mavi kelebek! — Hav hav!
    (86.2, 87.5),    # Gökyüzü ne renk?
    (91.0, 95.4),    # Mavi! Gökyüzü de mavi! — Gökyüzü mavi!
    (108.6, 114.6),  # Bir... iki... üç! — Üç mavi çiçek!
    (133.4, 134.6),  # Su ne renk?
    (138.1, 142.5),  # Mavi! — Hav! — Hi hi! Zıpzıp ıslandı!
    (160.0, 164.6),  # Bu Cik-Cik... Cik cik cik!
    (178.0, 184.4),  # Top! Mavi top! — Zıpzıp, yakala! — Aferin!
    (188.6, 200.2),  # Mavi tekerlemesi
]
KART = 3.0                   # sondaki kanal kartı (sn)
KANCA = ("Mavi şeyleri", "bulalım!")   # ilk saniyelerde büyük başlık (izleyiciyi yakalar)
KANCA_SN = 2.6


def kadraj(pl, st):
    """Dikey kamera: Umay ile Zıpzıp'ın ortası, yaylı yumuşatma."""
    n = st.n
    cam = np.empty((n, 3))
    cy = GROUND_Y - (GROUND_AT - 0.5) * H / ZOOM
    for i in range(n):
        t = i / FPS
        lo, hi = min(st.ux[i], st.zx[i]) - 140, max(st.ux[i], st.zx[i]) + 140
        mid = (lo + hi) / 2                   # ikisi birden kadrajda
        cx = mid
        sc = pl.scene_at(t)
        if sc is not None and not pl.seg_at(t, "travel"):
            fp = E.focus_point(pl, sc["code"], t, st.ux[i], st.zx[i])
            if fp is not None and abs(fp[0] - mid) < 700:
                cx = mid + np.clip((fp[0] - mid) * 0.5, -110, 110)   # konuşulan nesneye doğru, karakterleri kaybetmeden
        cam[i] = (cx, cy, ZOOM)
    cam = E._spring(cam, w=2.0)
    cam[:, 0] = np.maximum(cam[:, 0], W / (2 * ZOOM) - world.MX + 20)
    return cam


def kart_kare(u):
    """Kapanış kartı: kanal adı + karakterler + "Tam bölüm kanalda!" (u: 0..1 ilerleme)."""
    cv = Canvas(W, H)
    p = K.painter(cv)
    p.part(lambda c: c.rectangle(0, 0, W, H), None, grad=(K.SKY[0], K.SKY[1], 0, H), line=False, flat=True, seed="kbg")
    K.sun_burst(p, W / 2, 760, 80, 1600, 18, (1, 1, 1), alpha=0.14)
    p.part(lambda c: c.rectangle(0, 1390, W, H - 1390), (0.49, 0.75, 0.38), seed="kgr", flat=True)
    pop = ease_out_back(clamp(u / 0.25))
    ctx = p.ctx
    ctx.save()
    ctx.translate(W / 2, 330)
    ctx.scale(max(pop, 0.01), max(pop, 0.01))
    K.text(p, "Umay ile Zıpzıp", 0, 0, 120, K.TITLE_COL, lw=1.8)
    ctx.restore()
    hop = abs(math.sin(u * math.pi * 4)) * 30
    ctx.save()
    ctx.translate(W / 2 + 70, 1400 - hop)
    ctx.scale(1.9, 1.9)
    draw_zipzip(p, -250, hop / 1.9 * 0.5, 1.0, {"facing": 1, "happy": 1.0, "mouth": 0.6})
    draw_umay(p, 0, 0, 1.0, {"facing": 1, "arms": umay_arm_pose("cheer", u * 3), "happy": 0.8, "mouth": 0.6})
    ctx.restore()
    for k, (x, y, col) in enumerate(((170, 560, "mavi"), (900, 620, "kirmizi"), (560, 520, "sari"))):
        draw_butterfly(p, x, y + 18 * math.sin(u * 9 + k), 1.3, u * 14 + k, 0.2 * math.sin(u * 5 + k), col=P.COL[col])
    a = clamp((u - 0.15) / 0.2)
    if a > 0:
        K.text(p, "Tam bölüm kanalda!", W / 2, 1560, 92, (1, 1, 1), lw=1.6)
        K.text(p, "Renkli Kelebekler", W / 2, 1700, 70, (1.0, 0.89, 0.43), lw=1.3)
    cv.surface.flush()
    return cv.arr[..., :3].copy()


def kanca(img, u):
    """Açılış başlığını karenin üstüne bindir (u: 0..1)."""
    cv = Canvas(W, H)
    p = K.painter(cv)
    pop = ease_out_back(clamp(u / 0.18)) * (1 - clamp((u - 0.85) / 0.15))
    if pop > 0.01:
        ctx = p.ctx
        ctx.save()
        ctx.translate(W / 2, 470)
        ctx.scale(pop, pop)
        ctx.rotate(-0.04)
        K.text(p, KANCA[0], 0, -80, 128, (1, 1, 1), lw=2.0)
        K.text(p, KANCA[1], 0, 70, 150, P.COL["mavi"], lw=2.2)
        ctx.restore()
    cv.surface.flush()
    a = cv.arr[..., 3:4].astype(np.float32) / 255
    return (img.astype(np.float32) * (1 - a) + cv.arr[..., :3].astype(np.float32)).clip(0, 255).astype(np.uint8)


def _iş(args):
    k, frames, out = args
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                             "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for pos, f in frames:
        img = E.render_frame(f, E._LAYERS) if f >= 0 else kart_kare((-f - 1) / (KART * FPS))
        if pos < KANCA_SN * FPS:
            img = kanca(img, pos / (KANCA_SN * FPS))
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def ses(pl, out):
    """Konuşma + efekt kesitleri art arda, altında kesintisiz müzik; konuşmada müzik kısılır."""
    stem = os.path.join(WORK, "ep1_konusma_efekt.wav")
    if not os.path.exists(stem):
        E.build_audio(stem, with_music=False)
    import wave
    with wave.open(stem) as w_:
        x = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    sr = Au.SR
    parts, spans, t = [], [], 0.0
    for a, b in KLIPLER:
        seg = x[int(a * sr):int(b * sr)].copy()
        r = int(0.012 * sr)
        seg[:r] *= np.linspace(0, 1, r)[:, None]
        seg[-r:] *= np.linspace(1, 0, r)[:, None]
        parts.append(seg)
        for ln in pl.lines:
            if ln["t1"] > a and ln["t0"] < b:
                spans.append((t + max(ln["t0"], a) - a, t + min(ln["t1"], b) - a))
        t += b - a
    dur = t + KART
    parts.append(np.zeros((int(KART * sr), x.shape[1]), np.float32))
    vo = np.concatenate(parts)[: int(dur * sr)]
    tek0 = sum(b - a for a, b in KLIPLER[:-1])          # tekerleme başlangıcı
    music = E.music_bed(dur + 0.5, lambda t0, mid: "dance" if mid > tek0 - 0.3 else "travel")
    mbuf = Au.lowpass(Au.reverb(music.buf, 1.8, 0.24), 8500)[: len(vo)]
    duck = Au.duck_curve(dur + 0.5, spans, depth=0.35)[: len(vo), None]
    tt = np.arange(len(vo)) / sr
    fade = np.clip((dur - 0.2 - tt) / 1.0, 0, 1) * np.clip(tt / 0.15, 0, 1)
    mix = (mbuf * duck * 0.85 + vo * 1.05) * fade[:, None] * 0.5   # sıkıştırmadan; ses düzeyi muxta ayarlanır
    Au.write_wav(out, Au.soft_limit(mix))
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "shorts", "short_bolum1_mavi.mp4"))
    ap.add_argument("--still", type=float, nargs="*", help="yalnız bu bölüm saniyelerinden dikey kare çiz")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    E.STYLE = "cizgi"
    orig = world.build_layers
    world.build_layers = lambda style, cache_dir=None, tag="", **kw: orig(style, cache_dir, tag + f"_{W}x{H}", **kw)
    pl = E.setup()
    E.STATE.cam = kadraj(pl, E.STATE)
    if a.still:
        for s in a.still:
            p_ = os.path.join(WORK, f"dikey_{s:06.1f}.png")
            cv2.imwrite(p_, E.render_frame(int(s * FPS), E._LAYERS))
            print(p_)
        cv2.imwrite(os.path.join(WORK, "dikey_kart.png"), kart_kare(0.6))
        return
    frames = [f for a_, b_ in KLIPLER for f in range(int(a_ * FPS), int(b_ * FPS))]
    frames += [-(k + 1) for k in range(int(KART * FPS))]
    n = max(1, a.workers * 3)
    idx = list(enumerate(frames))
    bounds = np.linspace(0, len(idx), n + 1).astype(int)
    jobs = [(k, idx[bounds[k]:bounds[k + 1]], os.path.join(WORK, f"seg_{k:03d}.mp4")) for k in range(n) if bounds[k + 1] > bounds[k]]
    with Pool(a.workers) as pool:
        segs = list(pool.imap(_iş, jobs))
    lst = os.path.join(WORK, "liste.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    silent = os.path.join(WORK, "sessiz.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    for s in segs:
        os.remove(s)
    wav = os.path.join(WORK, "ses.wav")
    dur = ses(pl, wav)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-tune", "animation", "-pix_fmt", "yuv420p",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur:.3f}", a.out], check=True)
    print(a.out, f"{dur:.1f} sn")


if __name__ == "__main__":
    main()
