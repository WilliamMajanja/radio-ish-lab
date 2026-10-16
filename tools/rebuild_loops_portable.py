#!/usr/bin/env python3
"""Portable rebuild of the B4 30 s loop for named artists.

Same proven algorithm as tools/rebuild_loops3.py (strongest 30 s window, no
compression in the seam, linear loudnorm to -14 LUFS / -1.0 dBTP, 24-bit 48 kHz
seam construction C), but repo-relative with a configurable ffmpeg so it runs on
the Linux host. Used to regenerate loops after a master is re-rendered.

Usage: rebuild_loops_portable.py <artist> <src> <tag> [<artist> <src> <tag> ...]
"""
import json, math, os, re, struct, subprocess, sys

FF = os.environ.get("RADIOISH_FFMPEG", "ffmpeg")
FP = os.environ.get("RADIOISH_FFPROBE", "ffprobe")
R = os.environ.get("RADIOISH_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = "/tmp/opencode/loopsfix"; os.makedirs(TMP, exist_ok=True)
SR, CH, WIN = 48000, 2, 30
WSPAN = SR * WIN * CH

def run(a):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace")
    return p.stdout + p.stderr

def window_rms(src):
    p = subprocess.Popen([FF, "-v", "error", "-i", src, "-ac", str(CH), "-ar", str(SR),
                          "-f", "s16le", "-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, bufsize=1 << 20)
    out, carry, total = [], b"", 0
    def take(buf):
        nonlocal total
        n = (len(buf) // (WSPAN * 2)) * WSPAN
        if n == 0:
            return buf
        s = struct.unpack(f"<{n}h", buf[:n * 2])
        total += n
        for i in range(n // WSPAN):
            w = s[i * WSPAN:(i + 1) * WSPAN]
            acc = 0
            for v in w:
                acc += v * v
            rms = math.sqrt(acc / len(w))
            out.append(20 * math.log10(rms / 32768.0) if rms > 0 else -200.0)
        return buf[n * 2:]
    while True:
        buf = p.stdout.read(1 << 22)
        if not buf:
            break
        carry = take(carry + buf)
    p.stdout.close(); p.wait()
    return out

def best_offset(rms):
    c = [(v, i) for i, v in enumerate(rms) if 0 < i < len(rms) - 1 and v > -60]
    if not c:
        c = list(enumerate(rms))
    if not c:
        return None, -200.0
    v, i = max(c)
    return i * WIN, v

def seam(src, start, out):
    # Two inputs + the classic acrossfade form. The old single-input
    # asplit+atrim graph yields no frames on ffmpeg 7.1 (the [h] branch trimmed
    # to exactly 0.5 s leaves acrossfade d=0.5 no margin). [m] is
    # src[start+0.5 .. start+30.5] and [h] is src[start .. start+1]; the output is
    # trimmed to 30 s, i.e. m's body + the 0.5 s crossfade into h = a seamless loop.
    A = "aformat=sample_fmts=s32:sample_rates=48000:channel_layouts=stereo"
    fc = f"[0:a]{A}[m];[1:a]{A}[h];[m][h]acrossfade=d=0.5:c1=tri:c2=tri[o]"
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-ss", f"{start + 0.5:.6f}", "-t", "30", "-i", src,
         "-ss", str(start), "-t", "1", "-i", src,
         "-filter_complex", fc, "-map", "[o]", "-t", "30", "-ar", "48000", "-ac", "2",
         "-c:a", "pcm_s24le", out])
    return os.path.isfile(out) and os.path.getsize(out) > 8_000_000

def loud(p):
    o = run([FF, "-hide_banner", "-nostats", "-i", p, "-af",
             "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m:
        return None
    d = json.loads(m.group(0))
    try:
        if not all(abs(float(d[k])) < 99 for k in
                   ("input_i", "input_tp", "input_thresh", "target_offset")):
            return None
    except (TypeError, ValueError):
        return None
    return d

def norm2(d, tmp, dst):
    af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={d['input_i']}:"
          f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
          f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", tmp, "-af", af,
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", dst])
    return os.path.isfile(dst) and os.path.getsize(dst) > 8_000_000

def dur(p):
    try:
        return float(run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())
    except ValueError:
        return 0.0

args = sys.argv[1:]
if len(args) % 3:
    sys.exit("usage: rebuild_loops_portable.py <artist> <src> <tag> ...")
report = []
for k in range(0, len(args), 3):
    name, src, tag = args[k:k + 3]
    if not os.path.isfile(src):
        print(f"  {name:<26} [err] source missing: {src}"); continue
    rms = window_rms(src)
    off, pickdb = best_offset(rms)
    if off is None:
        print(f"  {name:<26} [err] no usable window"); continue
    tmp = f"{TMP}/{tag}_seam.wav"
    if not seam(src, off, tmp):
        print(f"  {name:<26} [err] seam render failed"); continue
    d = loud(tmp)
    dst = f"{R}/{name}/epk/audio/{tag}_B4_30s_loop.wav"
    if not d or not norm2(d, tmp, dst):
        print(f"  {name:<26} [err] loudnorm failed"); continue
    chk = loud(dst)
    li, lt = chk["input_i"], chk["input_tp"]
    dd = dur(dst); bits = "24" if os.path.getsize(dst) > 8_000_000 else "16"
    ok = abs(dd - 30.0) < 0.001 and float(lt) <= -0.9 and -16.0 <= float(li) <= -12.0 and bits == "24"
    print(f"  {name:<26} offset={off} pick={pickdb:.1f} dur={dd:.6f} lufs={li} tp={lt} {bits}bit "
          f"{'PASS' if ok else 'CHECK'}")
    report.append(dict(artist=name, tag=tag, src=src, offset=off, pick_rms=round(pickdb, 2),
                       dur=dd, lufs=li, tp=lt, bytes=os.path.getsize(dst)))
json.dump(report, open(f"{TMP}/loops.json", "w"), indent=1, ensure_ascii=False)
