#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""程序化配乐 + VO 铺设 + ducking → out/audio.wav（120BPM / 60.0s / 44.1k）"""
import json, os
import numpy as np
import wave

SR = 44100
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

SCHEDULE = [210, 240, 240, 180, 180, 210, 195, 240, 105]
assert sum(SCHEDULE) == 1800
STARTS = [sum(SCHEDULE[:i]) / 30.0 for i in range(len(SCHEDULE))]

def env(n, a=0.005, d=0.05, s=0.7, r=0.08):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([
        np.linspace(0, 1, max(1, a_n)),
        np.linspace(1, s, max(1, d_n)),
        np.full(s_n, s),
        np.linspace(s, 0, max(1, r_n)),
    ])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))

def sine(freq, n, phase=0.0):
    return np.sin(2 * np.pi * freq * np.arange(n) / SR + phase)

def saw(freq, n):
    t = np.arange(n) / SR
    return 2 * ((t * freq) % 1.0) - 1

def add(buf, sig, start_s, gain=1.0):
    i = int(start_s * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i] * gain

music = np.zeros(N, np.float32)

BEAT = 0.5  # 120BPM
BARS = int(DUR / (BEAT * 4))

# ---- 段落动力学 ----
def sec_of(t):
    """返回该时刻属于哪一段落：hook / groove / turn / method / end"""
    if t < STARTS[1]:
        return "hook"
    if t < STARTS[7]:
        return "groove"
    if t < STARTS[8]:
        return "turn"
    return "end"

# ---- 鼓 & 贝斯 ----
for bar in range(BARS):
    t0 = bar * BEAT * 4
    if t0 >= DUR:
        break
    sec = sec_of(t0 + 0.01)
    if sec == "turn":
        continue  # 转折幕留白
    # kick：四踩，轻重交替
    for b in range(4):
        tb = t0 + b * BEAT
        if tb >= DUR:
            continue
        n = int(0.18 * SR)
        f = np.linspace(120, 42, n)
        kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.06, 0.35, 0.06)
        add(music, kick, tb, 0.60 if b % 2 == 0 else 0.42)
    # backbeat 2/4
    for b in (1, 3):
        tb = t0 + b * BEAT
        n = int(0.12 * SR)
        noise = rng.normal(0, 1, n) * env(n, 0.001, 0.02, 0.15, 0.05)
        # 带通近似
        noise = np.convolve(noise, np.ones(6) / 6, mode="same")
        add(music, noise, tb, 0.28)
    # 贝斯：八分音符根音/八度泵
    roots = [55.0, 55.0, 65.41, 49.0]  # A1 A1 C2 G1
    root = roots[bar % 4]
    for e in range(8):
        te = t0 + e * BEAT / 2
        if te >= DUR:
            continue
        f = root * (2 if e % 2 else 1)
        n = int(0.20 * SR)
        sig = saw(f, n) * env(n, 0.004, 0.06, 0.5, 0.06)
        add(music, sig, te, 0.16)
    # 时钟 tick：16 分
    for s16 in range(16):
        ts = t0 + s16 * BEAT / 4
        if ts >= DUR:
            continue
        n = int(0.02 * SR)
        tick = rng.normal(0, 1, n) * env(n, 0.0005, 0.004, 0.0, 0.004)
        add(music, tick, ts, 0.06 if s16 % 4 else 0.10)

# ---- 钩子 riser ----
n = int(1.4 * SR)
sweep = rng.normal(0, 1, n) * np.linspace(0.0, 1.0, n) ** 2
sweep = np.convolve(sweep, np.ones(24) / 24, mode="same")
add(music, sweep, 0.2, 0.22)

# ---- 和声垫：科技感 supersaw（每两小节换一次） ----
chords = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66),
          (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
for bar in range(0, BARS, 2):
    t0 = bar * BEAT * 4
    if t0 >= DUR:
        break
    sec = sec_of(t0 + 0.01)
    if sec in ("turn",):
        continue
    ch = chords[(bar // 2) % 4]
    n = int(BEAT * 8 * SR)
    sig = np.zeros(n, np.float32)
    for f in ch:
        for det in (-0.6, 0.0, 0.6):
            sig += saw(f + det, n) * 0.16
    sig *= env(n, 0.35, 0.5, 0.55, 0.6)
    gain = 0.16 if sec == "groove" else 0.12
    add(music, sig, t0, gain)

# 收束：封底渐弱
fade = np.ones(N, np.float32)
i0 = int(STARTS[8] * SR)
fade[i0:] = np.linspace(1.0, 0.55, N - i0)
music *= fade

# ---- VO ----
vo = np.zeros(N, np.float32)
dur = json.load(open("tmp/durations.json"))
vo_windows = []
for i, frames in enumerate(SCHEDULE):
    idx = str(i + 1)
    path = f"public/vo/vo-{idx}.wav"
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        if w.getnchannels() > 1:
            data = data.reshape(-1, w.getnchannels()).mean(1)
    if sr != SR:
        # 简单线性重采样
        m = int(len(data) * SR / sr)
        data = np.interp(np.linspace(0, len(data) - 1, m), np.arange(len(data)), data)
    start = STARTS[i] + 5 / 30.0
    add(vo, data, start, 1.0)
    vo_windows.append((start, start + len(data) / SR))

# ---- ducking ----
ctrl = np.ones(N, np.float32)
for (a, b) in vo_windows:
    ia, ib = int(a * SR), int(b * SR)
    ra, rb = int(0.06 * SR), int(0.45 * SR)
    ctrl[max(0, ia - ra):ia] = np.linspace(1.0, 0.30, min(ra, ia - max(0, ia - ra)) if ia > ra else 1)[: max(0, ia - max(0, ia - ra))]
    ctrl[ia:ib] = 0.30
    if ib + rb < N:
        ctrl[ib:ib + rb] = np.linspace(0.30, 1.0, rb)
# 平滑
k = np.ones(2048, np.float32) / 2048
ctrl = np.convolve(ctrl, k, mode="same")

mix = music * ctrl * 1.0 + vo * 1.0
peak = np.max(np.abs(mix))
target = 10 ** (-1.0 / 20)  # -1 dBFS
mix = mix / peak * target

stereo = np.stack([mix, mix], axis=1)
pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
os.makedirs("out", exist_ok=True)
with wave.open("out/audio.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("audio.wav written; vo windows:", [(round(a, 2), round(b, 2)) for a, b in vo_windows])
