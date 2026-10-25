import pathlib
p = pathlib.Path("render.py")
s = p.read_text(encoding="utf-8")

pairs = [
    # S1 钩子
    ('    fbig = F(190, "serif")\n    draw.text((PADX, 700), "许愿式", font=fbig, fill=C["text"])\n    draw.text((PADX, 920), "编程", font=fbig, fill=C["text"])',
     '    fbig = F(150, "serif")\n    draw.text((PADX, 730), "许愿式", font=fbig, fill=C["text"])\n    draw.text((PADX, 915), "编程", font=fbig, fill=C["text"])'),
    ('text(draw, (PADX, 1180), "WISH-DRIVEN  PROGRAMMING"', 'text(draw, (PADX, 1120), "WISH-DRIVEN  PROGRAMMING"'),
    ('text(draw, (PADX, 1270), "从一句话，到一个能跑起来的项目"', 'text(draw, (PADX, 1205), "从一句话，到一个能跑起来的项目"'),
    ('text(draw, (PADX, 1336), "这一次，是官方自己说的"', 'text(draw, (PADX, 1270), "这一次，是官方自己说的"'),
    ('x = chip(draw, x, 1470, lab, C["line"], fs=30)', 'x = chip(draw, x, 1420, lab, C["line"], fs=31)'),
    # S2 新版本
    ('        y = 760 + i * 200\n        card(draw, [PADX, y, PADX + CW, y + 160])\n        draw.rectangle([PADX, y, PADX + 8, y + 160], fill=C["cyan"])\n        text(draw, (PADX + 44, y + 30), k, F(50, "sans"), C["text"])\n        text(draw, (PADX + 44, y + 96), v, F(34, "sans_r"), C["dim"])',
     '        y = 750 + i * 212\n        card(draw, [PADX, y, PADX + CW, y + 180])\n        draw.rectangle([PADX, y, PADX + 8, y + 180], fill=C["cyan"])\n        text(draw, (PADX + 44, y + 34), k, F(54, "sans"), C["text"])\n        text(draw, (PADX + 44, y + 108), v, F(37, "sans_r"), C["dim"])'),
    ('    draw.rectangle([PADX, 1380, PADX + CW, 1500], fill=(12, 30, 44))\n    center_text(draw, W // 2, 1412,',
     '    draw.rectangle([PADX, 1420, PADX + CW, 1548], fill=(12, 30, 44))\n    center_text(draw, W // 2, 1454,'),
    # S3 帕累托
    ('draw.text((PADX, 800), f"{val:.1f}", font=F(250, "serif"), fill=C["brand"])',
     'draw.text((PADX, 806), f"{val:.1f}", font=F(212, "serif"), fill=C["brand"])'),
    ('text(draw, (760, 900), "DeepSWE v1.1", F(46, "sans"), C["text"])\n    text(draw, (760, 968), "官方更新日志口径", F(32, "sans_r"), C["dim"])',
     'text(draw, (712, 884), "DeepSWE v1.1", F(50, "sans"), C["text"])\n    text(draw, (712, 956), "官方更新日志口径", F(34, "sans_r"), C["dim"])'),
    # S4 从零建
    ('        card(draw, [x, y, x + bw, y + 400])', '        card(draw, [x, y, x + bw, y + 420])'),
    ('text(draw, (PADX, 1110), "许愿式编程 = 说清目标", F(84, "serif"), fade_col(C["text"], p))\n        text(draw, (PADX, 1220), "剩下它自己搭", F(84, "serif"), fade_col(C["text"], p))',
     'text(draw, (PADX, 1250), "许愿式编程 = 说清目标", F(80, "serif"), fade_col(C["text"], p))\n        text(draw, (PADX, 1362), "剩下它自己搭", F(80, "serif"), fade_col(C["text"], p))'),
    # S5 搜索接口
    ('        y = 640 + i * 320\n        card(draw, [PADX, y, PADX + CW, y + 280])\n        draw.rectangle([PADX, y, PADX + 8, y + 280], fill=C["cyan"])',
     '        y = 620 + i * 340\n        card(draw, [PADX, y, PADX + CW, y + 300])\n        draw.rectangle([PADX, y, PADX + 8, y + 300], fill=C["cyan"])'),
    ('text(draw, (PADX + 48, y + 34), k, F(56, "serif"), C["text"])\n        text(draw, (PADX + 48, y + 124), v, F(34, "sans_r"), C["dim"])\n        text(draw, (PADX + 48, y + 192), n, F(46, "sans"), C["brand"])',
     'text(draw, (PADX + 48, y + 40), k, F(58, "serif"), C["text"])\n        text(draw, (PADX + 48, y + 134), v, F(37, "sans_r"), C["dim"])\n        text(draw, (PADX + 48, y + 208), n, F(50, "sans"), C["brand"])'),
    # S6 操作01
    ('        y = 640 + i * 180', '        y = 645 + i * 205'),
    ('text(draw, (PADX + 36, y + 70), v, F(32, "sans_r"), C["dim"])',
     'text(draw, (PADX + 36, y + 74), v, F(35, "sans_r"), C["dim"])'),
    # S7 操作02
    ('        y = 610 + i * 240\n        draw.ellipse([PADX, y, PADX + 76, y + 76], outline=C["magenta"], width=3)\n        text(draw, (PADX + 20, y + 16), n, F(34, "sans"), C["magenta"])\n        text(draw, (PADX + 110, y - 4), k, F(48, "sans"), C["text"])\n        text(draw, (PADX + 110, y + 66), v, F(32, "sans_r"), C["dim"])\n        if i < 2:\n            draw.line([PADX + 38, y + 80, PADX + 38, y + 196], fill=C["faint"], width=2)',
     '        y = 640 + i * 272\n        draw.ellipse([PADX, y, PADX + 94, y + 94], outline=C["magenta"], width=3)\n        text(draw, (PADX + 26, y + 26), n, F(36, "sans"), C["magenta"])\n        text(draw, (PADX + 126, y - 2), k, F(52, "sans"), C["text"])\n        text(draw, (PADX + 126, y + 76), v, F(36, "sans_r"), C["dim"])\n        if i < 2:\n            draw.line([PADX + 47, y + 98, PADX + 47, y + 250], fill=C["faint"], width=2)'),
    ('text(draw, (PADX, 1360), "把它当实习生：先给小事，再给整活。", F(48, "serif"), fade_col(C["text"], p))',
     'text(draw, (PADX, 1470), "把它当实习生：先给小事，再给整活。", F(50, "serif"), fade_col(C["text"], p))'),
    # S8 冷静一刻
    ('text(draw, (PADX + 230, y + 122), "你的场景", F(76, "serif"), C["text"])',
     'text(draw, (PADX + 220, y + 132), "你的场景", F(70, "serif"), C["text"])'),
    # S9 封底
    ('text(draw, (PADX, 600), "扎克的自留地", F(136, "serif"), C["text"])',
     'text(draw, (PADX, 620), "扎克的自留地", F(120, "serif"), C["text"])'),
    # footer chrome
    ('    y = 1798\n    f = F(28, "sans_r")', '    y = 1786\n    f = F(30, "sans_r")'),
    ('bx0, bx1, by = PADX, W - PADX, 1856', 'bx0, bx1, by = PADX, W - PADX, 1846'),
]

for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("render.py 尺寸修订完成，共", len(pairs), "处")
