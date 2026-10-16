#!/usr/bin/env python3
"""Print a two-pass loudnorm audio filter for a slice of a file.

Usage: loudnorm_filter.py <ffmpeg> <audio> <start> <duration>
Measures the exact -ss/-t slice, then prints the linear loudnorm filter that
lands the clip on -14 LUFS / -1.0 dBTP with a peak-safe limiter.
"""
import json, re, subprocess, sys

ff, audio, start, dur = sys.argv[1:5]
o = subprocess.run(
    [ff, "-hide_banner", "-nostats", "-ss", start, "-t", dur, "-i", audio,
     "-af", "loudnorm=I=-14:TP=-1.0:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True, errors="replace").stderr
m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
if not m:
    sys.exit(0)  # no measurement -> caller keeps its default
d = json.loads(m.group(0))
try:
    finite = all(abs(float(d[k])) < 99 for k in
                 ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"))
except (TypeError, ValueError):
    finite = False
if not finite:
    sys.exit(0)
print(f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:"
      f"measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:"
      f"offset={d['target_offset']}:linear=true,alimiter=level=false:limit=0.9")
