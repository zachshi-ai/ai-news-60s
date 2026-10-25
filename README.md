# AI 快讯 60 秒

一条 60 秒竖屏短视频的完整生产线：9 句旁白 → 逐句 TTS → 程序化配乐 → 九幕渲染 → 封面与发布文案。全流程脚本化，一次跑完，不依赖剪辑软件。

## 成片规格

- 母版 1440×1920（3:4），30fps，1800 帧 / 60.0s
- 封面 1080×1440（3:4）
- 音轨：VO + 程序化配乐（120BPM），ducking 后混成 `audio.wav`
- 九幕结构：钩子 → 发布 → 跑分 → 价格 → 实操 ×4 → 封底

## 目录结构

```
pipeline/
  make-vo.sh       9 句旁白逐句 TTS，剪首尾静音，输出时长表
  make-audio.py    120BPM 程序化配乐 + VO 混音 + ducking
  render.py        九幕画面渲染（PIL + numpy）→ rawvideo → video-only.mp4
  make-cover.py    发布封面 1080×1440
  patch-size.py    字幕/字号批量微调
editions/
  20261020 … 20261025/     逐期归档：选题、场景表、信源与口径、旁白、发布文案
  20261026-shangshouji/    同一条流水线产出的「上手记」栏目
samples/           两期样片与封面（快讯 / 上手记）
```

## 跑一期

每期的约定是：`scripts/` 放当期脚本与 `vo-lines.txt`，`public/vo/` 放旁白，`tmp/` 放中间产物，`out/` 放交付物。

```bash
ED=editions/20261025
mkdir -p $ED/scripts $ED/public/vo $ED/tmp $ED/out
cp pipeline/* $ED/scripts/

cd $ED
bash scripts/make-vo.sh        # TTS → public/vo/*.wav + tmp/durations.json
python3 scripts/make-audio.py  # → out/audio.wav
python3 scripts/render.py      # → out/video-only.mp4
python3 scripts/make-cover.py  # → out/cover.png
```

`render.py` 与 `make-audio.py` 从脚本内的场景表 / 配乐表读取时间轴，改期只需改表；`SCHEDULE` 之和必须等于 1800 帧。

## 设计约束

- **先定字数再写文案**：9 句旁白实测总长必须 ≤ 48s，留 12s 给停顿与本片的白闪
- **跑分必须标注口径**：厂商自测、环境不同，不可直接横比，片中提示两次
- **实操优先**：四幕实操合计约 27.5s，占正片 46%，每幕拆 4 个可照做的动作
- **视觉纪律**：深空底色 + 单一强调色，色差大字只出现在钩子幕，白闪对齐旁白起点
- **信源可核**：每期 README 记录官方口径、评测口径、价格口径与不确定项

## 依赖

`ffmpeg`、`python3`（Pillow、numpy）、`mmx` CLI（TTS 用 `mmx speech synthesize`）。

## 说明

`editions/` 内的文案与数据为公开信息整理，用作流程示例；`samples/` 是其中一期成片。代码 MIT。
