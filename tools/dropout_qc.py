#!/usr/bin/env python3
"""QC: report near-silent drop-outs ("gain explosions") in a shipped master.

A drop-out is a run of 50 ms windows whose sample peak sits at or below ABS dBFS
while audible music surrounds it (median of the 1 s before AND after >=
SURROUND dBFS). Those dips are what the ear check heard as explosions: the
master measures clean on loudness and true peak, but the level leaps 12-60 dB
between one window and the next.

Controls: Parisa and Yogo, which the ear check passed, report zero — so a
non-zero count here is a real defect, not an artefact of the threshold.

Usage:  dropout_qc.py [--abs -48] [--surround -35] [--min-dur 0.05] FILE ...
Exit status is 1 when any file still carries a drop-out.
"""
import os, subprocess, sys

FF = os.environ.get("RADIOISH_FFMPEG", "ffmpeg")
SR = 48000
WIN = SR // 20

args = sys.argv[1:]
ABS, SURROUND, MIN = -48.0, -35.0, 0.05
files = []
i = 0
while i < len(args):
    if args[i] == "--abs":
        ABS = float(args[i + 1]); i += 2
    elif args[i] == "--surround":
        SURROUND = float(args[i + 1]); i += 2
    elif args[i] == "--min-dur":
        MIN = float(args[i + 1]); i += 2
    else:
        files.append(args[i]); i += 1

def hhmmss(t):
    t = int(t)
    return f"{t // 3600}:{(t % 3600) // 60:02d}:{t % 60:02d}"

bad = 0
for path in files:
    p = subprocess.Popen([FF, "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR),
                          "-f", "s16le", "-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, bufsize=1 << 20)
    chunks, buf = [], b""
    step = WIN * 4 * 4096
    while True:
        c = p.stdout.read(step)
        if not c:
            break
        buf += c
        m = len(buf) // (WIN * 4) * (WIN * 4)
        if m:
            import numpy as np
            b = np.abs(np.frombuffer(buf[:m], dtype="<i2").astype(np.float32))
            chunks.append(b.reshape(-1, WIN * 2).max(axis=1))
            buf = buf[m:]
    p.wait()
    import numpy as np
    w = 20.0 * np.log10(np.maximum(np.concatenate(chunks), 1.0) / 32768.0)

    runs, holes, i = [], [], 0
    while i < len(w):
        if w[i] <= ABS:
            j = i
            while j < len(w) and w[j] <= ABS:
                j += 1
            runs.append([i, j]); i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and (r[0] - merged[-1][1]) * 0.05 <= 0.10:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    for i0, i1 in merged:
        if (i1 - i0) * 0.05 < MIN:
            continue
        b4 = w[max(0, i0 - 20):i0]
        af = w[i1:i1 + 20]
        lo = min(float(np.median(b4)) if len(b4) else -99,
                 float(np.median(af)) if len(af) else -99)
        if lo >= SURROUND:
            holes.append((i0 * WIN, i1 * WIN, float(w[i0:i1].min())))

    flag = "" if not holes else "  ** DROP-OUTS **"
    print(f"{os.path.basename(path):<46} {len(holes):>4} drop-out(s){flag}")
    for s0, s1, mp in holes[:12]:
        print(f"    {hhmmss(s0 / SR)}-{hhmmss(s1 / SR)}  {(s1 - s0) / SR:.2f}s  {mp:.1f} dBFS")
    if len(holes) > 12:
        print(f"    ... and {len(holes) - 12} more")
    if holes:
        bad += 1

sys.exit(1 if bad else 0)
