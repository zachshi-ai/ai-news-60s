#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布封面 cover.png：1080×1440（3:4）· 2026.10.25 期"""
import importlib.util
import numpy as np
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location("r", "render.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

W, H = 1080, 1440
PAD = 76
F, C = m.F, m.C
DATE = "2026.10.25"

img = Image.new("RGB", (W, H), C["bg"])
d = ImageDraw.Draw(img)
for y in range(0, 900):
    a = int(10 * (1 - y / 900) ** 2)
    d.line([(0, y), (W, y)], fill=(C["bg"][0] + a // 4, C["bg"][1] + a, C["bg"][2] + int(a * 1.6)))
rng = np.random.default_rng(25)
for _ in range(120):
    x, y = int(rng.uniform(0, W)), int(rng.uniform(0, H))
    v = int(rng.uniform(40, 90)); d.point((x, y), fill=(v, v, min(255, v + 20)))

d.text((PAD, 96), "扎克的自留地", font=F(30, "sans"), fill=C["text"])
d.text((PAD, 140), "AI 快讯 60 秒", font=F(26, "sans_r"), fill=C["dim"])
w = d.textbbox((0, 0), DATE, font=F(26, "sans_r"))[2]
d.text((W - PAD - w, 96), DATE, font=F(26, "sans_r"), fill=C["dim"])

# 月相
d.ellipse([W - PAD - 150, 200, W - PAD, 350], outline=C["cyan"], width=3)
d.ellipse([W - PAD - 122, 218, W - PAD - 18, 332], fill=C["bg"])

d.rectangle([PAD, 236, PAD + 380, 308], fill=C["magenta"])
d.text((PAD + 20, 250), "KIMI K3.1 PRO", font=F(30, "sans"), fill=C["bg"])

d.text((PAD, 372), "三万亿", font=F(140, "serif"), fill=C["text"])
d.text((PAD, 540), "参数", font=F(140, "serif"), fill=C["magenta"])
d.text((PAD, 730), "3T PARAMS · 1M CONTEXT", font=F(27, "sans_r"), fill=C["cyan"])

d.text((PAD, 800), "全球最大开源模型，权重 11 月 4 日前开放", font=F(26, "sans_r"), fill=C["dim"])

# 跑分卡
d.rounded_rectangle([PAD, 880, W - PAD, 1140], radius=22, fill=C["card"], outline=C["line"], width=2)
d.text((PAD + 30, 906), "官方口径", font=F(24, "sans_r"), fill=C["dim"])
d.text((PAD + 30, 946), "终端任务 65.7", font=F(42, "sans"), fill=C["magenta"])
d.text((PAD + 30, 1010), "接近 Opus 5.5，超过 GPT-6 Astra", font=F(26, "sans_r"), fill=C["text"])
d.text((PAD + 30, 1058), "输入 13 元 / 缓存 1.3 元 / 输出 68 元（每百万）", font=F(24, "sans_r"), fill=C["faint"])

d.line([PAD, 1190, W - PAD, 1190], fill=C["line"], width=2)
d.text((PAD, 1216), "实操：进 kimi.com → 选 3.1 Pro → 一份长资料试跑", font=F(25, "sans_r"), fill=C["faint"])
d.text((PAD, 1270), "跑分再高，也替不了你核对事实。", font=F(26, "sans_r"), fill=C["brand"])
d.text((PAD, 1324), "每天 60 秒，把 AI 讲明白。", font=F(26, "sans_r"), fill=C["faint"])

arr = np.asarray(img, np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.78)) ** 2)
vig = np.clip(1.05 - 0.34 * np.clip(r, 0, 1.4) ** 2, 0.60, 1.0)[..., None]
scan = np.ones((H, W, 1), np.float32); scan[::3, :, 0] = 0.945
grain = np.random.default_rng(25).normal(0, 4.0, (H, W, 1)).astype(np.float32)
out = np.clip(arr * scan * vig + grain, 0, 255).astype(np.uint8)
Image.fromarray(out).save("/root/AIdesign/ai-news-60s-20261025/out/ai-news-60s-20261025-cover.png")
print("cover ok 1080x1440")
