#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-news-60s-flash · 云端自建模板（Python/PIL + numpy + ffmpeg）
2026.10.25 期：Kimi K3.1 Pro 三万亿参数开源模型
3:4 母版 1440×1920 / 30fps / 1800 帧 = 60.0s
视觉语言：月相观测台（深空黑蓝 + 月光银 + 月白金光）
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1440, 1920
FPS = 30
PADX = 96
CW = W - PADX * 2
DATE = "2026.10.25"
BRAND = "扎克的自留地"
COL = "AI 快讯 60 秒"
TOPIC = "Kimi K3.1 Pro"

C = {
    "bg":      (8, 10, 16),
    "text":    (230, 236, 244),
    "dim":     (146, 156, 170),
    "faint":   (100, 110, 126),
    "cyan":    (190, 212, 240),
    "magenta": (233, 196, 106),
    "brand":   (255, 96, 78),
    "line":    (30, 36, 48),
    "card":    (14, 18, 26),
}

SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SANS_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def F(size, kind="sans"):
    path, idx = {"sans": (SANS, 2), "sans_r": (SANS_R, 2), "serif": (SERIF, 2)}[kind]
    return ImageFont.truetype(path, size, index=idx)

def tw(draw, s, f):
    b = draw.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]

def text(draw, xy, s, f, fill, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)

def center_text(draw, cx, y, s, f, fill):
    draw.text((cx, y), s, font=f, fill=fill, anchor="ma")

def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

def clamp01(x):
    return max(0.0, min(1.0, x))

def fade_col(color, p):
    p = clamp01(p)
    return tuple(int(color[i] * p + C["bg"][i] * (1 - p)) for i in range(3))

def slide(p):
    return int((1 - ease_out(p)) * 26)

# ---------- 视觉元件 ----------
def card(draw, box, stroke=None, r=22, fill=None):
    draw.rounded_rectangle(box, radius=r, fill=fill or C["card"], outline=stroke or C["line"], width=2)

def section_tag(draw, num, label, y=290, color=None):
    color = color or C["cyan"]
    w = 92 if len(num) <= 2 else 152
    draw.rectangle([PADX, y, PADX + w, y + 56], fill=color)
    text(draw, (PADX + 16, y + 6), num, F(34, "sans"), C["bg"])
    text(draw, (PADX + w + 20, y + 8), label, F(38, "sans_r"), C["dim"])

def title_block(draw, s, y=380, size=100, color=None, gap=1.18):
    color = color or C["text"]
    f = F(size, "serif")
    for i, ln in enumerate(s.split("\n")):
        text(draw, (PADX, y + i * int(size * gap)), ln, f, color)

def chip(draw, x, y, label, color, fs=28):
    f = F(fs, "sans_r")
    w, _ = tw(draw, label, f)
    pad = 20
    draw.rounded_rectangle([x, y, x + w + pad * 2, y + fs + 26], radius=(fs + 26) // 2,
                           outline=color, width=2)
    text(draw, (x + pad, y + 10), label, f, color)
    return x + w + pad * 2 + 16

def bottom_band(draw, lines, y=1636, color=None):
    color = color or C["faint"]
    draw.line([PADX, y, W - PADX, y], fill=C["line"], width=2)
    f = F(28, "sans_r")
    for i, ln in enumerate(lines):
        text(draw, (PADX, y + 30 + i * 44), ln, f, color)

def moon(draw, cx, cy, r, alpha=1.0):
    """月相LOGO：外环 + 缺口"""
    col = tuple(int(c * alpha + C["bg"][i] * (1 - alpha)) for i, c in enumerate(C["cyan"]))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3)
    draw.ellipse([cx - r * 0.55, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=C["bg"])

# ---------- 合成层 ----------
def make_backdrop():
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    for y in range(0, 1200):
        a = int(10 * (1 - y / 1200) ** 2)
        d.line([(0, y), (W, y)], fill=(C["bg"][0] + a // 4, C["bg"][1] + a, C["bg"][2] + int(a * 1.6)))
    # 星点
    rng = np.random.default_rng(25)
    for _ in range(140):
        x, y = int(rng.uniform(0, W)), int(rng.uniform(0, H))
        v = int(rng.uniform(40, 90))
        d.point((x, y), fill=(v, v, min(255, v + 20)))
    for x in range(0, W, 144):
        d.line([(x, 0), (x, H)], fill=(11, 14, 21))
    return img

BACKDROP = make_backdrop()

def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.74)) ** 2 + ((yy - H / 2) / (H * 0.74)) ** 2)
    v = np.clip(1.05 - 0.36 * np.clip(r, 0, 1.4) ** 2, 0.56, 1.0)
    return v[..., None].astype(np.float32)

def make_scanlines():
    lines = np.ones((H, W, 1), np.float32)
    lines[::3, :, 0] = 0.94
    return lines

VIGNETTE = make_vignette()
SCAN = make_scanlines()
RNG = np.random.default_rng(20261025)
GRAIN = [RNG.normal(0, 4.4, (H, W, 1)).astype(np.float32) for _ in range(8)]

def finish(arr, frame_idx):
    out = arr * SCAN * VIGNETTE + GRAIN[frame_idx % 8]
    return np.clip(out, 0, 255).astype(np.uint8)

def flash(arr, strength):
    if strength <= 0:
        return arr
    return np.clip(arr + 255 * strength, 0, 255)

def chroma_title(img, box, dx):
    if dx <= 0.4:
        return img
    region = img.crop(box)
    a = np.asarray(region, np.float32)
    shifted = a.copy()
    shifted[..., 0] = np.roll(a[..., 0], -int(dx), axis=1)
    shifted[..., 2] = np.roll(a[..., 2], int(dx), axis=1)
    out = img.copy()
    out.paste(Image.fromarray(np.clip(shifted, 0, 255).astype(np.uint8)), box)
    return out

# ---------- Chrome ----------
CHAPTERS = ["钩子", "发布", "跑分", "价格", "入口", "长任务", "代码与3D", "省钱验收", "封底"]

def draw_chrome(draw, idx, hide_brand=False):
    if not hide_brand:
        text(draw, (PADX, 58), BRAND, F(32, "sans"), C["text"])
        text(draw, (PADX, 102), f"{COL} · {DATE}", F(30, "sans_r"), C["dim"])
    f2 = F(30, "sans_r")
    w, _ = tw(draw, TOPIC, f2)
    text(draw, (W - PADX - w, 58), TOPIC, f2, C["magenta"])

def draw_footer(draw, idx, total=9):
    y = 1786
    f = F(30, "sans_r")
    text(draw, (PADX, y), CHAPTERS[idx], f, C["dim"])
    lab = f"SC.{idx + 1:02d}/{total:02d}"
    w, _ = tw(draw, lab, f)
    text(draw, (W - PADX - w - 8, y), lab, f, C["faint"])
    bx0, bx1, by = PADX, W - PADX, 1846
    draw.rectangle([bx0, by, bx1, by + 6], fill=(24, 30, 40))
    prog = (idx + 0.5) / total
    draw.rectangle([bx0, by, bx0 + int((bx1 - bx0) * prog), by + 6], fill=C["cyan"])

# ---------- 各幕 ----------
def s1_hook(draw, t, fi):
    text(draw, (PADX, 360), "2026.10.25 · 开源大模型", F(42, "sans_r"), C["dim"])
    moon(draw, W - PADX - 90, 430, 78)
    y = 440
    draw.rectangle([PADX, y, PADX + 400, y + 76], fill=C["magenta"])
    text(draw, (PADX + 24, y + 16), "KIMI K3.1 PRO", F(36, "sans"), C["bg"])

    fbig = F(156, "serif")
    text(draw, (PADX, 620), "三万亿", fbig, C["text"])
    text(draw, (PADX, 800), "参数", fbig, C["magenta"])
    text(draw, (PADX, 1006), "3T PARAMS · 1M CONTEXT", F(32, "sans_r"), C["cyan"])

    f2 = F(38, "sans_r")
    text(draw, (PADX, 1096), "全球参数规模最大的开源模型，权重十一月四号前放开", f2, C["dim"])
    x = PADX
    for lab in ["终端 65.7", "Highspeed 2-3x", "缓存 1.3 元"]:
        x = chip(draw, x, 1220, lab, C["dim"])
    bottom_band(draw, ["本期：它强在哪、贵不贵，以及今晚怎么用起来"], y=1500)

def s2_launch(draw, t, fi):
    section_tag(draw, "01", "发布")
    title_block(draw, "不是新基座\n是重后训练", y=372, size=92)
    rows = [("3 万亿级 / 2.8 万亿总参", "MoE，单次激活约 1040 亿"),
            ("100 万 token 上下文", "整本手册、整个仓库一次读"),
            ("K3 上后训练 + 大规模 RL", "重点补长程代码、3D、金融")]
    for i, (k, v) in enumerate(rows):
        pp = ease_out((t - 0.14 - i * 0.13) / 0.32)
        if pp <= 0:
            continue
        yy = 690 + i * 208 + slide(pp)
        card(draw, [PADX, yy, PADX + CW, yy + 172])
        draw.rectangle([PADX, yy, PADX + 8, yy + 172], fill=C["cyan"])
        text(draw, (PADX + 44, yy + 32), k, F(44, "sans"), C["text"])
        text(draw, (PADX + 44, yy + 106), v, F(32, "sans_r"), C["dim"])

    pp = ease_out((t - 0.62) / 0.5)
    if pp > 0:
        yy = 1340
        draw.rectangle([PADX, yy, PADX + CW, yy + 150], fill=(20, 26, 38))
        text(draw, (PADX + 36, yy + 30), "入口一次开五个：网页 / App / Work / Code / API", F(34, "sans"), C["magenta"])
        text(draw, (PADX + 36, yy + 88), "同步上了 Highspeed 高速版，速度约 2–3 倍", F(30, "sans_r"), C["dim"])
    bottom_band(draw, ["信源：月之暗面官方发布 · 每经 / 中新社 / 华尔街见闻（10.24）"], y=1636)

def s3_score(draw, t, fi):
    section_tag(draw, "02", "跑分")
    title_block(draw, "贴着最强闭源跑", y=372, size=92)
    bars = [("Kimi K3.1 Pro", 0.657, C["magenta"], "65.7"),
            ("Claude Opus 5.5", 0.664, C["faint"], "66.4"),
            ("GPT-6 Astra", 0.582, C["faint"], "58.2")]
    for i, (name, v, col, lab) in enumerate(bars):
        pp = ease_out((t - 0.14 - i * 0.14) / 0.4)
        if pp <= 0:
            continue
        yy = 640 + i * 160
        text(draw, (PADX, yy), name, F(32, "sans_r"), C["text"] if i == 0 else C["dim"])
        bx, bw = PADX + 470, 640
        draw.rounded_rectangle([bx, yy + 6, bx + bw, yy + 38], radius=16, fill=(24, 30, 42))
        draw.rounded_rectangle([bx, yy + 6, bx + int(bw * v * pp), yy + 38], radius=16, fill=col)
        text(draw, (bx + bw + 24, yy), lab, F(36, "sans"), col)

    text(draw, (PADX, 1140), "Terminal-Bench 4.0（终端任务）", F(28, "sans_r"), C["dim"])
    pp = ease_out((t - 0.6) / 0.45)
    if pp > 0:
        draw.rectangle([PADX, 1210, PADX + CW, 1420], fill=(20, 26, 38))
        text(draw, (PADX + 34, 1236), "SWE-Marathon 51.7% > Opus 46.3%", F(34, "sans"), C["magenta"])
        text(draw, (PADX + 34, 1300), "14 项基准 6 项第一；Code Arena 第 8", F(32, "sans_r"), C["text"])
        text(draw, (PADX + 34, 1360), "但都是厂商自测，环境不同不能直接横比", F(28, "sans_r"), C["faint"])
    bottom_band(draw, ["官方口径；不同测试环境与工具不同，分数不等于你的场景"], y=1636)

def s4_price(draw, t, fi):
    section_tag(draw, "03", "价格")
    title_block(draw, "便宜的是输入\n贵的是输出", y=372, size=88)
    rows = [("缓存命中", "1.3 元", "重复的前缀最划算"),
            ("未命中输入", "13 元", "新资料按原价算"),
            ("输出", "68 元", "话越多，账单越长")]
    for i, (k, v, note) in enumerate(rows):
        pp = ease_out((t - 0.14 - i * 0.14) / 0.32)
        if pp <= 0:
            continue
        yy = 660 + i * 190 + slide(pp)
        text(draw, (PADX, yy), k, F(36, "sans_r"), C["dim"])
        text(draw, (PADX + 380, yy - 10), v, F(56, "serif"), C["magenta"])
        text(draw, (PADX + 700, yy + 6), note, F(28, "sans_r"), C["faint"])
        draw.line([PADX, yy + 118, W - PADX, yy + 118], fill=C["line"], width=2)

    pp = ease_out((t - 0.62) / 0.45)
    if pp > 0:
        draw.rectangle([PADX, 1270, PADX + CW, 1470], fill=C["text"])
        text(draw, (PADX + 34, 1296), "单位：元 / 百万 token", F(26, "sans_r"), (70, 78, 90))
        text(draw, (PADX + 34, 1344), "Highspeed 约为标准版 2 倍价", F(38, "sans"), C["bg"])
        text(draw, (PADX + 34, 1404), "媒体口径：约为 GPT-6 Astra 的五分之一", F(28, "sans_r"), (70, 78, 90))
    bottom_band(draw, ["官方定价；以 platform.kimi.com 实际计费为准"], y=1636)

def s5_entry(draw, t, fi):
    section_tag(draw, "操作 01", "先进得去", color=C["magenta"])
    title_block(draw, "三个入口，先试网页", y=372, size=92)
    steps = [("01", "打开 kimi.com 或 App", "登录后直接进对话"),
             ("02", "模型选 K3.1 Pro", "模型列表里认准 3.1，不是 3"),
             ("03", "赶时间切 Highspeed", "同智能，速度快 2–3 倍，价格翻倍"),
             ("04", "写代码再上 Kimi Code", "要跑终端、改仓库时用它")]
    for i, (n, k, v) in enumerate(steps):
        pp = ease_out((t - 0.12 - i * 0.14) / 0.32)
        if pp <= 0:
            continue
        yy = 596 + i * 214 + slide(pp)
        draw.ellipse([PADX, yy, PADX + 76, yy + 76], outline=C["magenta"], width=3)
        text(draw, (PADX + 20, yy + 18), n, F(30, "sans"), C["magenta"])
        text(draw, (PADX + 104, yy - 6), k, F(42, "sans"), C["text"])
        text(draw, (PADX + 104, yy + 62), v, F(30, "sans_r"), C["dim"])
        if i < 3:
            draw.line([PADX + 38, yy + 80, PADX + 38, yy + 196], fill=C["line"], width=2)
    pp = ease_out((t - 0.72) / 0.45)
    if pp > 0:
        draw.rectangle([PADX, 1470, PADX + CW, 1566], fill=(20, 26, 38))
        text(draw, (PADX + 32, 1494), "先别碰 API，网页版就能验证值不值得用。", F(32, "sans"), C["cyan"])
    bottom_band(draw, ["模型名认错版本，是最常见的白花钱"], y=1636)

def s6_long(draw, t, fi):
    section_tag(draw, "操作 02", "派长任务", color=C["magenta"])
    title_block(draw, "先计划，再分段", y=372, size=96)
    steps = [("01", "一次给全资料", "手册、数据、旧版都丢进去"),
             ("02", "写清目标和验收", "要什么文件、什么算做完"),
             ("03", "先要一份计划", "它列步骤，你删多余的"),
             ("04", "分段验收", "每段跑完看一眼，别等最后")]
    for i, (n, k, v) in enumerate(steps):
        pp = ease_out((t - 0.12 - i * 0.13) / 0.3)
        if pp <= 0:
            continue
        yy = 620 + i * 196 + slide(pp)
        draw.rectangle([PADX, yy + 4, PADX + 40, yy + 44], outline=C["magenta"], width=3)
        if pp > 0.55:
            draw.line([PADX + 8, yy + 26, PADX + 17, yy + 36], fill=C["magenta"], width=4)
            draw.line([PADX + 17, yy + 36, PADX + 32, yy + 12], fill=C["magenta"], width=4)
        text(draw, (PADX + 70, yy), k, F(44, "sans"), C["text"])
        text(draw, (PADX + 70, yy + 64), v, F(30, "sans_r"), C["dim"])
    pp = ease_out((t - 0.7) / 0.45)
    if pp > 0:
        draw.rectangle([PADX, 1430, PADX + CW, 1530], fill=(20, 26, 38))
        text(draw, (PADX + 30, 1456), "一百万上下文，不等于它全记得住。", F(34, "sans"), C["cyan"])
    bottom_band(draw, ["关键结论让它回引原文，方便你核对"], y=1636)

def s7_code(draw, t, fi):
    section_tag(draw, "操作 03", "代码与 3D", color=C["magenta"])
    title_block(draw, "让它自己跑起来", y=372, size=96)
    rows = [("给环境", "把终端、预览、仓库权限开给它"),
            ("给样例", "一段能跑的输入，比十句描述有用"),
            ("让它自检", "跑测试、看报错、自己改一轮"),
            ("你来定稿", "架构和取舍，仍然你拍板")]
    for i, (k, v) in enumerate(rows):
        pp = ease_out((t - 0.12 - i * 0.13) / 0.3)
        if pp <= 0:
            continue
        yy = 640 + i * 190 + slide(pp)
        text(draw, (PADX, yy), k, F(40, "sans"), C["magenta"] if i < 2 else C["cyan"])
        text(draw, (PADX + 260, yy + 6), v, F(31, "sans_r"), C["text"])
        draw.line([PADX, yy + 116, W - PADX, yy + 116], fill=C["line"], width=2)
    pp = ease_out((t - 0.7) / 0.45)
    if pp > 0:
        text(draw, (PADX, 1400), "3D 也一样：给草图，让它操作 Blender 出模型。", F(34, "serif"), fade_col(C["text"], pp))
    bottom_band(draw, ["演示案例不等于稳定复现，先小后大"], y=1636)

def s8_thrift(draw, t, fi):
    section_tag(draw, "操作 04", "省钱与验收", color=C["magenta"])
    title_block(draw, "三招，把账单压住", y=372, size=92)
    rows = [("固定前缀", "系统提示别改，命中缓存只要 1.3 元"),
            ("控制输出", "要结论不要长篇，输出 68 元最贵"),
            ("先跑小样", "用 1% 的样本验证，再全量跑"),
            ("人工核验", "金融数字、事实引用必须复核")]
    for i, (k, v) in enumerate(rows):
        pp = ease_out((t - 0.12 - i * 0.12) / 0.3)
        if pp <= 0:
            continue
        yy = 630 + i * 180 + slide(pp)
        text(draw, (PADX, yy), k, F(40, "sans"), C["text"])
        text(draw, (PADX + 260, yy + 8), v, F(30, "sans_r"), C["dim"])
        draw.line([PADX, yy + 104, W - PADX, yy + 104], fill=C["line"], width=2)
    pp = ease_out((t - 0.68) / 0.45)
    if pp > 0:
        draw.rectangle([PADX, 1400, PADX + CW, 1500], fill=(48, 22, 18))
        text(draw, (PADX + 30, 1426), "跑分再高，也替不了你核对事实。", F(34, "sans"), (255, 200, 190))
    bottom_band(draw, ["官方内部测试称事实错误率从 23.4% 降到 8.3%，仍不是零"], y=1636)

def s9_end(draw, t, fi):
    text(draw, (PADX, 600), "扎克的自留地", F(120, "serif"), C["text"])
    x = PADX
    x = chip(draw, x, 790, "AI 快讯 60 秒", C["cyan"])
    x = chip(draw, x, 790, DATE, C["dim"])
    text(draw, (PADX, 918), "把 AI 讲明白，也把账算清楚", F(38, "sans_r"), C["dim"])
    draw.rectangle([PADX, 1090, PADX + 580, 1186], fill=C["magenta"])
    text(draw, (PADX + 40, 1116), "关注我 · 明天见", F(48, "sans"), C["bg"])
    f = F(27, "sans_r")
    text(draw, (PADX, 1330), "信源：月之暗面官方发布 · 每经 / 中新社 / 华尔街见闻（10.24）", f, C["faint"])
    text(draw, (PADX, 1374), "跑分与价格为官方口径，以平台实际为准", f, C["faint"])
    bottom_band(draw, ["今晚就能做：进 kimi.com → 选 3.1 Pro → 一份长资料试跑"], y=1490)

SCENES = [s1_hook, s2_launch, s3_score, s4_price, s5_entry,
          s6_long, s7_code, s8_thrift, s9_end]

SCHEDULE = [210, 240, 240, 180, 180, 210, 195, 240, 105]
assert sum(SCHEDULE) == 1800, sum(SCHEDULE)
IMPACT = [5, 5, 5, 5, 5, 5, 5, 5, 2]

def render_scene(idx, frame_in, total_frames, frame_global):
    img = BACKDROP.copy()
    draw = ImageDraw.Draw(img)
    t = frame_in / max(1, total_frames)
    SCENES[idx](draw, t, frame_in)
    draw_chrome(draw, idx, hide_brand=(idx == 8))
    draw_footer(draw, idx)
    if idx == 0:
        dx = max(0.0, 9.0 * (1 - frame_in / 8.0)) if frame_in < 8 else 0.0
        img = chroma_title(img, (PADX, 600, W - PADX, 1100), dx)
    return np.asarray(img, np.float32)

def main():
    outdir = "out"
    os.makedirs(outdir, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
           "-pix_fmt", "yuv420p", f"{outdir}/video-only.mp4"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    g = 0
    for idx, n in enumerate(SCHEDULE):
        for k in range(n):
            arr = render_scene(idx, k, n, g)
            fi = IMPACT[idx]
            st = 0.0
            if k == fi:
                st = 0.55 if idx == 0 else (0.14 if idx == 7 else 0.28)
            arr = flash(arr, st)
            proc.stdin.write(finish(arr, g).tobytes())
            g += 1
            if g % 300 == 0:
                print(f"rendered {g}/1800", flush=True)
    proc.stdin.close()
    proc.wait()
    print("video-only done")

if __name__ == "__main__":
    main()
