#!/bin/bash
# 逐句 TTS → 剪首尾静音 → 测时长 → 输出 durations.json
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p public/vo tmp
: > tmp/durations.txt
mapfile -t LINES < scripts/vo-lines.txt
for line in "${LINES[@]}"; do
  [ -z "$line" ] && continue
  idx="${line%%|*}"; text="${line#*|}"
  raw="tmp/vo-${idx}-raw.wav"
  out="public/vo/vo-${idx}.wav"
  ok=0
  for attempt in 1 2 3; do
    if mmx speech synthesize --text "$text" --voice male-qn-jingying-jingpin --speed 1.0 --pitch 0 \
        --format wav --sample-rate 44100 --out "$raw" </dev/null >/dev/null 2>&1 && [ -s "$raw" ]; then ok=1; break; fi
    sleep 2
  done
  if [ "$ok" != "1" ]; then echo "TTS FAIL $idx"; continue; fi
  # 剪首尾静音（保留 60ms 余量）
  ffmpeg -nostdin -y -v error -i "$raw" -af "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB:detection=peak,areverse,silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB:detection=peak,areverse" "$out"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")
  echo "${idx}|${d}" >> tmp/durations.txt
  echo "VO ${idx}: ${d}s"
done

python3 - <<'PY'
import json
d = {}
for line in open('tmp/durations.txt'):
    idx, dur = line.strip().split('|')
    d[idx] = float(dur)
json.dump(d, open('tmp/durations.json', 'w'), ensure_ascii=False, indent=1)
print('total voice =', round(sum(d.values()), 2), 's / count', len(d))
PY
