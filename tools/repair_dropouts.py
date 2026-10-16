#!/usr/bin/env python3
"""Repair drop-out holes in a source recording before mastering.

A hole is a run of 50 ms windows whose sample peak is at or below ABS dBFS and
which is surrounded by audible music (the median level on both sides is at or
above SURROUND dBFS). Runs closer than MERGE seconds are merged.

Each hole [s0,s1) is bridged with an equal-power cross-fade between the equally
long blocks immediately before and after it, reversed so the fill is continuous
with the audio on BOTH edges (sample at s0 continues the pre audio, sample at
s1-1 meets the post audio). No clicks, no level change, length preserved.
Detection runs PASS times so holes revealed after a nearby cluster is filled
are also repaired.

Usage:
  repair_dropouts.py IN OUT.wav [ABS SURROUND MIN MERGE] [PASS]
  repair_dropouts.py IN --dry [ABS SURROUND MIN MERGE]
"""
import os, subprocess, sys
import numpy as np

FF = os.environ.get("RADIOISH_FFMPEG", "ffmpeg")
SR = 48000
WIN = SR // 20              # 50 ms

ABS = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != "--dry" else -48.0
SURROUND = float(sys.argv[4]) if len(sys.argv) > 4 else -35.0
MIN = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
MERGE = float(sys.argv[6]) if len(sys.argv) > 6 else 0.10
PASSES = int(sys.argv[7]) if len(sys.argv) > 7 else 2

src, dst = sys.argv[1], sys.argv[2]
dry = "--dry" in sys.argv
# /tmp is a tmpfs here; a 3.5 h source raw buffer would be held in RAM.
TMPD = os.environ.get("RADIOISH_TMP", os.path.expanduser("~/gainfix_tmp"))
os.makedirs(TMPD, exist_ok=True)
tmp = f"{TMPD}/_repair_{os.getpid()}.raw"


def hhmmss(t):
    t = int(t)
    return f"{t // 3600}:{(t % 3600) // 60:02d}:{t % 60:02d}"


def window_peaks(a):
    nw = a.shape[0] // WIN
    peaks = np.empty(nw, dtype=np.float32)
    for k in range(0, nw, 20000):
        m = min(nw, k + 20000)
        blk = np.asarray(a[k * WIN:m * WIN]).reshape(m - k, WIN * 2)
        peaks[k:m] = np.abs(blk).max(axis=1)
    return 20.0 * np.log10(np.maximum(peaks, 1e-7))


def find_holes(w):
    runs, i = [], 0
    while i < len(w):
        if w[i] <= ABS:
            j = i
            while j < len(w) and w[j] <= ABS:
                j += 1
            runs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and (r[0] - merged[-1][1]) * 0.05 <= MERGE:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    holes = []
    for i0, i1 in merged:
        if (i1 - i0) * 0.05 < MIN:
            continue
        before = w[max(0, i0 - 20):i0]
        after = w[i1:i1 + 20]
        b = float(np.median(before)) if len(before) else -99
        af = float(np.median(after)) if len(after) else -99
        if min(b, af) >= SURROUND:
            holes.append((i0 * WIN, i1 * WIN, b, af, float(w[i0:i1].min())))
    return holes


subprocess.run([FF, "-y", "-v", "error", "-i", src, "-ac", "2", "-ar", str(SR),
                "-f", "f32le", tmp], check=True)
n = os.path.getsize(tmp) // 8
a = np.memmap(tmp, dtype="<f4", mode="r+" if not dry else "r", shape=(n, 2))

if dry:
    holes = find_holes(window_peaks(a))
    print(f"{src}: {len(holes)} holes to repair")
    for s0, s1, b, af, mp in holes:
        print(f"   {hhmmss(s0 / SR)}-{hhmmss(s1 / SR)} dur={(s1 - s0) / SR:.2f}s "
              f"minPeak={mp:.1f} before={b:.1f} after={af:.1f}")
    del a
    os.remove(tmp)
    sys.exit(0)

total = 0
for p in range(PASSES):
    holes = find_holes(window_peaks(a))
    if not holes:
        break
    if p == 0:
        for s0, s1, b, af, mp in holes:
            print(f"   {hhmmss(s0 / SR)}-{hhmmss(s1 / SR)} dur={(s1 - s0) / SR:.2f}s "
                  f"minPeak={mp:.1f} before={b:.1f} after={af:.1f}")
    done = 0
    for s0, s1, *_ in holes:
        L = s1 - s0
        if L < 2 or s0 - L < 0 or s1 + L > n:
            continue
        pre = a[s0 - L:s0].copy()
        post = a[s1:s1 + L].copy()
        wgt = (np.arange(L) / (L - 1)) * (np.pi / 2)
        fill = pre[::-1] * np.cos(wgt)[:, None] + post[::-1] * np.sin(wgt)[:, None]
        a[s0:s1] = fill
        done += 1
    print(f"pass {p + 1}: repaired {done}/{len(holes)} holes")
    total += done
    if done == 0:
        break
a.flush()
del a

subprocess.run([FF, "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                "-i", tmp, "-c:a", "pcm_s24le", dst], check=True)
os.remove(tmp)
print(f"repaired {total} holes -> {dst}")
