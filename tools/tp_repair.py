#!/usr/bin/env python3
"""True-peak repair for masters that standardise_masters.py left above 0 dBTP.

standardise_masters.py picks a limiter ceiling from the SOURCE true peak, but
alimiter with a 5 ms attack lets heavily-limited material overshoot that ceiling
once MP3 inter-sample peaks are counted. On the 2026-10-05 onboardings the
observed overshoot was 2.1-2.3 dB, which put DNZ, Kesh-Zion and Canthus at
+0.36..+0.60 dBTP: outside the MASTER_README gate of "true peak below 0 dBTP".

Rather than re-deriving the chain, this keeps each artist's already-landed trim
and EQ, lowers the ceiling by the overshoot actually measured on the shipped
master, adds 0.3 dB of margin for the extra limiting, and compensates the trim
to hold -14 LUFS. Sources are always the ORIGINAL capture in epk/audio, never
the already-processed master, so nothing becomes a second-generation encode.

    tp_repair.py Artist [Artist ...]

With no arguments every artist in NEEDS is checked and only re-rendered if its
master is genuinely over the gate.
"""
import json, os, re, shutil, subprocess, sys, time, datetime

FF = os.path.expanduser("~/bin/ffmpeg")
R  = "/Users/bernie/Movies/Radio-ish"
ARCH = f"{R}/Archive/2026-09-26_superseded/mixes"
TMP = "/tmp/sdkz_bw/tpfix2"; os.makedirs(TMP, exist_ok=True)
TARGET_LUFS, TP_TARGET = -14.0, -1.0

STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast",
        "DNZ":"dnz","Kesh-Zion":"kesh_zion","Canthus":"canthus"}
# original capture per artist: epk/audio for the raw-session onboardings,
# the superseded mix folder for the artists whose canon was an earlier master.
SRCNAME = {"DNZ":"dnz_session_140704.wav",
           "Kesh-Zion":"kesh_session_145756.wav",
           "Canthus":"canthus_session_134936.wav"}
DECK = {"DJ Unknown":"denon"}
EQ = {
 "rx3":  "highpass=f=28,equalizer=f=220:t=q:w=0.8:g=-1.5,"
         "equalizer=f=3000:t=q:w=0.9:g=1.0,equalizer=f=9000:t=h:w=6000:g=1.5",
 "denon":"highpass=f=30,equalizer=f=220:t=q:w=0.8:g=-1.0,"
         "equalizer=f=3000:t=q:w=0.9:g=0.5,equalizer=f=9000:t=h:w=6000:g=0.8",
}

def run(a, t=21600):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace", timeout=t)
    return (p.stdout or "") + (p.stderr or "")

def lufs_tp(p):
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None, None
    d = json.loads(m.group(0))
    try: return float(d["input_i"]), float(d["input_tp"])
    except Exception: return None, None

def ff(a, out, label):
    o = run([FF,"-y","-hide_banner","-loglevel","error"] + a)
    if not (os.path.isfile(out) and os.path.getsize(out) > 1024):
        tail = o.strip().splitlines()[-1] if o.strip() else "no output"
        print(f"      ffmpeg {label}: {tail[:170]}", flush=True)
        return False
    return True

def source_for(artist, stem):
    for cand in (f"{R}/{artist}/epk/audio/{SRCNAME[artist]}" if artist in SRCNAME else None,
                 f"{ARCH}/{artist}/{stem}_mix.mp3", f"{ARCH}/{artist}/{stem}_mix.wav",
                 f"{ARCH}/{artist}/{stem}_mix_hq.mp3", f"{ARCH}/{artist}/{SRCNAME.get(artist,'')}"):
        if cand and os.path.isfile(cand) and os.path.getsize(cand) > 1024: return cand
    return None

want = sys.argv[1:]
if want:
    bad = set(want) - set(STEM)
    if bad: print(f"unknown artist(s): {', '.join(sorted(bad))}"); sys.exit(1)

say_log = open("/tmp/sdkz_bw/tpfix2.log", "a", buffering=1)
def say(m): print("  " + m, flush=True); say_log.write(m + "\n")

say(f"\n=== true-peak repair v2 — {datetime.date.today().isoformat()} ===")
results = []
for artist, stem in STEM.items():
    if want and artist not in want: continue
    d = f"{R}/{artist}/epk/mix"
    mix, hq, epk = f"{d}/{stem}_mix.mp3", f"{d}/{stem}_mix_hq.mp3", f"{d}/{stem}_mix_epk.mp3"
    if not (os.path.isfile(mix) and os.path.isfile(epk)):
        say(f"{artist:<24} [skip] no house trio on disk"); continue
    lm, tm = lufs_tp(mix); le, te = lufs_tp(epk)
    if None in (lm, tm, le, te):
        say(f"{artist:<24} [err] could not measure current master"); continue
    if tm <= TP_TARGET and te <= TP_TARGET:
        say(f"{artist:<24} {lm:.2f}/{tm:.2f} dBTP — already inside gate"); continue

    src = source_for(artist, stem)
    if not src:
        say(f"{artist:<24} [err] original source not found; refusing to re-encode the master"); continue

    old_l, old_tp = lufs_tp(src)
    if old_l is None:
        say(f"{artist:<24} [err] could not measure source"); continue
    # ceiling that survived standardise_masters.py for this source
    old_ceil = min(-1.5, (old_tp + (TARGET_LUFS - old_l)) - 2.5)
    deck     = DECK.get(artist, "rx3")

    t0 = time.time()
    # The limiter's overshoot grows as the ceiling drops, so a single computed
    # margin lands short. Iterate: lower the ceiling by whatever the previous
    # attempt still overshot, plus 0.3 dB, and re-render from the SOURCE each
    # time. Two passes is enough for material this hot in practice.
    wav = p48 = p44 = None
    new_ceil = trim = None
    lm2 = tm2 = le2 = te2 = None
    for attempt in range(1, 4):
        if attempt == 1:
            observed = max(tm, te) - old_ceil
            new_ceil = TP_TARGET - (observed + 0.3)
        else:
            overshoot = max(tm2, te2) - new_ceil
            new_ceil = TP_TARGET - (overshoot + 0.3)
        trim = (TARGET_LUFS - old_l) + 0.5 * abs(new_ceil - old_ceil)
        lim  = 10 ** (new_ceil / 20.0)

        wav = f"{TMP}/{stem}.wav"
        af = (f"{EQ[deck]},volume={trim:.2f}dB,"
              f"alimiter=level=disabled:limit={lim:.6f}:attack=5:release=50:level_in=1")
        if not ff(["-i",src,"-af",af,"-ar","48000","-ac","2","-c:a","pcm_s24le",wav], wav, "wav"):
            say(f"{artist:<24} [err] intermediate failed"); wav = None; break
        p48, p44 = f"{TMP}/{stem}.mp3", f"{TMP}/{stem}_epk.mp3"
        if not ff(["-i",wav,"-ar","48000","-ac","2","-c:a","libmp3lame","-b:a","320k",p48], p48, "mp3-48"):
            say(f"{artist:<24} [err] 48k encode failed"); wav = None; break
        if not ff(["-i",wav,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","320k",p44], p44, "mp3-44"):
            say(f"{artist:<24} [err] 44.1k encode failed"); wav = None; break
        os.remove(wav); wav = None

        lm2, tm2 = lufs_tp(p48); le2, te2 = lufs_tp(p44)
        say(f"{artist:<24} pass {attempt}: ceil {new_ceil:>6.2f} trim {trim:>6.2f} | "
            f"48k {lm2:>7.2f}/{tm2:>6.2f}  44.1k {le2:>7.2f}/{te2:>6.2f}  {time.time()-t0:>5.0f}s",
            )
        if tm2 <= TP_TARGET and te2 <= TP_TARGET:
            break
        say(f"{artist:<24}   still over, lowering ceiling by the overshoot actually measured")
    if not p48 or not (os.path.isfile(p48) and os.path.isfile(p44)):
        continue

    # never lose a shipped file: park the pre-repair master in the archive
    ad = f"{ARCH}/{artist}/tp_repair_{datetime.date.today().isoformat()}"
    if tm > 0:
        os.makedirs(ad, exist_ok=True)
        for f in (f"{stem}_mix.mp3", f"{stem}_mix_hq.mp3", f"{stem}_mix_epk.mp3"):
            if os.path.isfile(f"{d}/{f}"): shutil.move(f"{d}/{f}", f"{ad}/{f}")

    shutil.copy2(p48, mix); shutil.copy2(p48, hq); shutil.copy2(p44, epk)

    sd = f"{R}/Season One/Artists/{artist}/Mix"
    if os.path.isdir(sd):
        for f in os.listdir(sd):
            t = f"{sd}/{f}"
            if os.path.exists(t): os.remove(t)
            if os.path.isfile(f"{d}/{f}"): os.link(f"{d}/{f}", t)

    lm2, tm2 = lufs_tp(mix); le2, te2 = lufs_tp(epk)
    results.append(dict(artist=artist, source=os.path.basename(src), old_ceil=round(old_ceil,2),
                        new_ceil=round(new_ceil,2), trim=round(trim,2), before=[lm,tm,le,te],
                        mix_lufs=lm2, mix_tp=tm2, epk_lufs=le2, epk_tp=te2,
                        secs=round(time.time()-t0,1)))
    flag = "" if (tm2 <= TP_TARGET and te2 <= TP_TARGET) else "  ** STILL OVER **"
    say(f"{artist:<24} final ceil {new_ceil:.2f} trim {trim:.2f} | "
        f"48k {lm2:>7.2f}/{tm2:>6.2f}  44.1k {le2:>7.2f}/{te2:>6.2f}{flag}")

json.dump(results, open("/tmp/sdkz_bw/tpfix2.json","w"), indent=1, ensure_ascii=False)
bad = [r for r in results if r["mix_tp"] > TP_TARGET or r["epk_tp"] > TP_TARGET]
say(f"done: {len(results)} repaired, {len(results)-len(bad)} now at or under {TP_TARGET} dBTP")
for r in bad: say(f"  REVIEW {r['artist']}: {r['mix_tp']} / {r['epk_tp']}")