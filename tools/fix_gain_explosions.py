#!/usr/bin/env python3
"""Fix gain explosions in two Season One masters + rebuild their loops.

Diagnosis (measured, see qc notes):
  * Habib  — released mix is ~82% near-silence (built on a silent 389.9 s
             timeline) with a few loud islands, so it "explodes" out of silence.
             Rebuilt full-length from the real contiguous recording.
  * Schrodinger's Breakfast — the 30 s EPK loop was cut from an unusually
             dynamic 30 s window and linearly normalised to -14 LUFS, so its
             bursts (rms -7 dB) slam against -44 dB dips. A dynamics-control
             step is added to the house chain; the loop is rebuilt from the
             fixed master.

House chain (unchanged) + inserted dynamics control:
  EQ (rx3), acompressor, volume=trim, alimiter   -> 48k/24-bit intermediate
  measure -> trim correction -> encode mix/mix_hq (48 kHz 320k) + mix_epk (44.1 kHz 320k)

Portable Linux port of the macOS pipeline (system ffmpeg, repo-relative root).
"""
import datetime, json, os, re, shutil, subprocess, sys

FF = os.environ.get("RADIOISH_FFMPEG", "ffmpeg")
FP = os.environ.get("RADIOISH_FFPROBE", "ffprobe")
R = os.environ.get("RADIOISH_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Intermediates are multi-GB 24-bit WAVs. /tmp is a tmpfs here, so writing them
# there consumes RAM and the OOM killer truncates the render; default to disk.
TMP = os.environ.get("RADIOISH_TMP", os.path.expanduser("~/gainfix_tmp"))
os.makedirs(TMP, exist_ok=True)
TARGET, TP_CEIL = -14.0, -0.9
ARCH = f"{R}/Archive/2026-10-15_gain_fix/mixes"

EQ = ("highpass=f=28,equalizer=f=220:t=q:w=0.8:g=-1.5,"
      "equalizer=f=3000:t=q:w=0.9:g=1.0,equalizer=f=9000:t=h:w=6000:g=1.5")

JOBS = [
    dict(artist="Habib", stem="habib",
         src=f"{R}/Habib/epk/audio/2026-08-31 15-26-03.mp3",
         comp="acompressor=threshold=-16dB:ratio=2:attack=15:release=300:makeup=1",
         note="rebuilt full-length from the real recording (was 82% silence)"),
    dict(artist="Schrödinger’s Breakfast", stem="schrodingers_breakfast",
         src=f"{R}/Archive/2026-09-26_superseded/mixes/Schrödinger’s Breakfast/4-Audio 0001 [2026-09-21 130546].wav",
         comp="acompressor=threshold=-20dB:ratio=3:attack=15:release=300:makeup=1",
         # source is a very quiet raw capture (-33.46 LUFS) needing +19.5 dB, and
         # its loud intro defeats a -1.5 dBFS sample ceiling after MP3 overshoot;
         # follows fix_truepeak.py: new_ceil = TP_TARGET - (observed_overshoot+0.3),
         # here observed was 2.64 dB (TP -0.76 at ceiling -3.4) -> about -3.94 dBFS.
         ceil_db=-4.2, src_i=-33.46, src_tp=-10.80,
         note="dynamics-control added to tame the loop's burst swings"),
]

want = set(sys.argv[1:])
if want:
    JOBS = [j for j in JOBS if j["artist"] in want]

def run(a, t=21600):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace", timeout=t)
    return (p.stdout or "") + (p.stderr or "")

def lufs_tp(p):
    o = run([FF, "-hide_banner", "-nostats", "-i", p, "-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json", "-f", "null", "-"], t=7200)
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m:
        return None, None
    d = json.loads(m.group(0))
    try:
        return float(d["input_i"]), float(d["input_tp"])
    except Exception:
        return None, None

def dur(p):
    o = run([FP, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", p])
    try:
        return float(o.strip().splitlines()[0])
    except Exception:
        return None

def ff(a, out, label):
    o = run([FF, "-y", "-hide_banner", "-loglevel", "error"] + a)
    if not (os.path.isfile(out) and os.path.getsize(out) > 1024):
        tail = o.strip().splitlines()[-1] if o.strip() else "no output"
        print(f"      [err] {label}: {tail[:170]}", flush=True)
        return False
    return True

logp = f"{TMP}/fix.log"
log = open(logp, "a", buffering=1)
def say(m):
    print(m, flush=True); log.write(m + "\n")

say(f"\n=== gain-explosion fix — {datetime.date.today().isoformat()} ===")
results = []
for j in JOBS:
    artist, stem, src, comp = j["artist"], j["stem"], j["src"], j["comp"]
    d = f"{R}/{artist}/epk/mix"
    mix, hq, epk = f"{d}/{stem}_mix.mp3", f"{d}/{stem}_mix_hq.mp3", f"{d}/{stem}_mix_epk.mp3"
    if not os.path.isfile(src):
        say(f"{artist:<26} [err] source missing: {src}"); continue
    if "src_i" in j:
        l0, tp0 = j["src_i"], j.get("src_tp")
    else:
        l0, tp0 = lufs_tp(src)
    if l0 is None:
        say(f"{artist:<26} [err] could not measure source"); continue
    trim = TARGET - l0
    # Only pre-drop the ceiling when the post-trim peak would actually clip; a
    # quiet source (pred <= -1.5 dBFS) just gets the plain -1.5 dB safety ceiling,
    # otherwise the limiter would engage on material that never needed limiting.
    pred = tp0 + trim if tp0 is not None else -1.5
    if "ceil_db" in j:
        ceil_db = j["ceil_db"]
    else:
        ceil_db = -1.5 if pred <= -1.5 else min(-1.5, pred - 2.5)
    lim = 10 ** (ceil_db / 20.0)
    wav = f"{TMP}/{stem}.wav"
    af = f"{EQ},{comp},volume={trim:.2f}dB,alimiter=level=disabled:limit={lim:.6f}:attack=5:release=50:level_in=1"
    say(f"{artist:<26} src I={l0:.2f} TP={tp0:.2f}  trim={trim:.2f} ceil={ceil_db:.1f}")
    if not ff(["-i", src, "-af", af, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", wav], wav, "wav"):
        say(f"{artist:<26} [err] intermediate render failed"); continue
    sd, od = dur(src), dur(wav)
    if sd and od and abs(od - sd) > 1.0:
        say(f"{artist:<26} [err] render truncated: {od:.0f}s of {sd:.0f}s — aborting"
            f" (out of disk? OOM?)")
        os.remove(wav); continue
    lw, tw = lufs_tp(wav)
    if lw is not None and abs(lw - TARGET) > 0.25:
        corr = TARGET - lw
        af2 = (f"volume={corr:.2f}dB,alimiter=level=disabled:"
               f"limit={lim:.6f}:attack=5:release=50:level_in=1")
        tmpw = f"{TMP}/{stem}_c.wav"
        if ff(["-i", wav, "-af", af2, "-c:a", "pcm_s24le", tmpw], tmpw, "wav-correct"):
            os.replace(tmpw, wav); trim += corr
    p48, p44 = f"{TMP}/{stem}.mp3", f"{TMP}/{stem}_epk.mp3"
    if not ff(["-i", wav, "-ar", "48000", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "320k", p48], p48, "mp3-48"):
        say(f"{artist:<26} [err] 48k encode failed"); continue
    if not ff(["-i", wav, "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "320k", p44], p44, "mp3-44"):
        say(f"{artist:<26} [err] 44.1k encode failed"); continue
    if od and abs((dur(p48) or od) - od) > 1.0:
        say(f"{artist:<26} [err] 48k mp3 truncated; not deploying"); continue
    ad = f"{ARCH}/{artist}"; os.makedirs(ad, exist_ok=True)
    for f in (os.path.basename(mix), os.path.basename(hq), os.path.basename(epk)):
        p = f"{d}/{f}"
        if os.path.isfile(p) and not os.path.exists(f"{ad}/{f}"):
            shutil.move(p, f"{ad}/{f}")
    shutil.copy2(p48, mix); shutil.copy2(p48, hq); shutil.copy2(p44, epk)
    os.remove(wav)
    lm, tm = lufs_tp(mix); le, te = lufs_tp(epk)
    results.append(dict(artist=artist, source=os.path.basename(src), src_lufs=l0, src_tp=tp0,
                        trim=round(trim, 2), ceiling=round(ceil_db, 2), dynamics=comp,
                        mix_lufs=lm, mix_tp=tm, epk_lufs=le, epk_tp=te, note=j["note"]))
    say(f"{artist:<26} -> 48k {lm:.2f}/{tm:.2f}   44.1k {le:.2f}/{te:.2f}")

json.dump(results, open(f"{TMP}/fix.json", "w"), indent=1, ensure_ascii=False)
say(f"done: {len(results)} master(s) rebuilt")
