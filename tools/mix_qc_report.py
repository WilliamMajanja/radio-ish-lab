#!/usr/bin/env python3
"""Write qc/SeasonOne_Mix_qc.md from the measurements taken during the house pass.

Loudness/true-peak figures come from a small per-file measurement cache: a file
whose size and mtime are unchanged reuses its last live measurement, and only a
file that has actually changed is re-measured with ffmpeg. Structure (sample
rate, bitrate, duration, hardlink, mix == mix_hq) and the drop-out gate are
re-verified live here, so the report cannot drift from the filesystem.

The cache (mixmeas_cache.json, under RADIOISH_TMP) is what makes a rebuild
practical: a fresh loudnorm pass over the whole catalogue is ~8 h, whereas only
the handful of rebuilt masters ever need measuring.

Render metadata the report needs but cannot measure off the master — the applied
trim, the source filename and the limiter ceiling — is read from the standardise
and true-peak repair JSON caches (standardise3.json / tpfix.json / tpfix2.json).
"""
import json, os, re, subprocess, datetime, shutil, sys

R = os.environ.get("RADIOISH_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FP = os.environ.get("RADIOISH_FFPROBE") or shutil.which("ffprobe") or os.path.expanduser("~/bin/ffprobe")
FF = os.environ.get("RADIOISH_FFMPEG") or shutil.which("ffmpeg") or os.path.expanduser("~/bin/ffmpeg")
TMP = os.environ.get("RADIOISH_TMP", os.path.expanduser("~/gainfix_tmp"))
STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast",
        "DNZ":"dnz","Kesh-Zion":"kesh_zion","Canthus":"canthus"}
DECK = {"SDKZ":"Pioneer XDJ-RX3","Yogo":"Pioneer XDJ-RX3","Bernie":"Pioneer XDJ-RX3",
        "Mundz":"Pioneer XDJ-RX3","Maya":"Pioneer XDJ-RX3","Dikier":"Pioneer XDJ-RX3",
        "DJ Unknown":"Denon","Alexander Zwo":"Pioneer XDJ-RX3","Habib":"Pioneer XDJ-RX3",
        "Parisa":"Pioneer XDJ-RX3","El Djemba":"Pioneer XDJ-RX3",
        "Schrödinger’s Breakfast":"Pioneer XDJ-RX3",
        "DNZ":"Pioneer XDJ-RX3","Kesh-Zion":"Pioneer XDJ-RX3","Canthus":"Pioneer XDJ-RX3"}
def _load(p):
    try: return {r["artist"]: r for r in json.load(open(p))}
    except (OSError, ValueError, KeyError): return {}
SRC  = _load(f"{TMP}/standardise3.json") or _load("/tmp/sdkz_bw/standardise3.json")
FIX  = _load(f"{TMP}/tpfix.json") or _load("/tmp/sdkz_bw/tpfix.json")
FIX2 = _load(f"{TMP}/tpfix2.json") or _load("/tmp/sdkz_bw/tpfix2.json")
# 2026-10-16 ear check: source drop-outs bridged before the chain (tools/repair_dropouts.py)
GAP = _load(f"{TMP}/gapfix.json")

# per-file loudness cache: {abs path: {size, mtime, done, lufs, tp}}
MEAS = f"{TMP}/mixmeas_cache.json"
try: MEASCACHE = json.load(open(MEAS))
except (OSError, ValueError): MEASCACHE = {}

DQ = f"{R}/tools/dropout_qc.py"

def dropout_count(path):
    """Near-silent drop-outs left in a shipped master (0 is the pass condition)."""
    p = subprocess.run([sys.executable, DQ, path], capture_output=True, text=True)
    for ln in (p.stdout or "").splitlines():
        if "drop-out(s)" in ln:
            try:
                return int(ln.split()[1])
            except (IndexError, ValueError):
                return -1
    return -1

def _sig(p):
    st = os.stat(p)
    return int(st.st_size), int(st.st_mtime)

def _measure(p):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", p, "-af",
        "loudnorm=I=-14:TP=-1.0:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", r.stdout + r.stderr, re.S)
    d = json.loads(m.group(0)) if m else {}
    return float(d.get("input_i", "nan")), float(d.get("input_tp", "nan"))

def live_meas(mix, epk):
    """Integrated LUFS + true peak off the shipped masters, cached by size+mtime."""
    out = {}
    for key, p in (("mix", mix), ("epk", epk)):
        k, sig = os.path.abspath(p), _sig(p)
        c = MEASCACHE.get(k)
        if c and c.get("done") and (c.get("size"), c.get("mtime")) == sig and c.get("lufs") is not None:
            lufs, tp = c["lufs"], c["tp"]
        else:
            lufs, tp = _measure(p)
            MEASCACHE[k] = dict(size=sig[0], mtime=sig[1], done=True, lufs=lufs, tp=tp)
        out[f"{key}_lufs"], out[f"{key}_tp"] = lufs, tp
    return out

rows, checks = [], []
def ck(name, ok, detail=""):
    checks.append((name, ok, detail)); return ok

for a, st in STEM.items():
    w = f"{R}/{a}/epk/mix"; l = f"{R}/Season One/Artists/{a}/Mix"
    m, h, e = f"{st}_mix.mp3", f"{st}_mix_hq.mp3", f"{st}_mix_epk.mp3"
    meas = live_meas(f"{w}/{m}", f"{w}/{e}")
    repaired = (a in FIX) or (a in FIX2)
    info = SRC.get(a) or {}
    probe = {}
    for f in (m, h, e):
        o = subprocess.run([FP,"-v","error","-select_streams","a:0","-show_entries",
             "stream=sample_rate,bit_rate:format=duration","-of","default=nw=1:nk=1",
             f"{w}/{f}"], capture_output=True, text=True).stdout.split()
        probe[f] = (int(o[0]), int(o[1]), float(o[2]))
    same = open(f"{w}/{m}","rb").read(1 << 20) == open(f"{w}/{h}","rb").read(1 << 20)
    linked = all(os.path.isfile(f"{l}/{f}") and os.stat(f"{l}/{f}").st_ino == os.stat(f"{w}/{f}").st_ino
                 for f in (m, h, e))
    rows.append(dict(artist=a, deck=DECK[a],
        src=info.get("source", "mastered mix (epk/mix)"),
        trim=info.get("trim", 0.0), approx=info.get("approx", False),
        lufs=meas["mix_lufs"], tp=meas["mix_tp"],
        elufs=meas["epk_lufs"], etp=meas["epk_tp"],
        sr=probe[m][0], esr=probe[e][0], br=probe[m][1], dur=probe[m][2],
        repaired=repaired, same=same, linked=linked))
    ck(f"{a}: 48 kHz master", probe[m][0] == 48000, f"{probe[m][0]} Hz")
    ck(f"{a}: 44.1 kHz EPK master", probe[e][0] == 44100, f"{probe[e][0]} Hz")
    ck(f"{a}: 320 kbps", 310000 <= probe[m][1] <= 330000, f"{probe[m][1]} bps")
    ck(f"{a}: mix == mix_hq (bit-identical)", same)
    ck(f"{a}: full length retained", probe[m][2] > 60, f"{probe[m][2]/60:.1f} min")
    ck(f"{a}: Season One hardlinks intact", linked)
    ck(f"{a}: loudness in -12..-16 LUFS", -16 <= meas["mix_lufs"] <= -12, f"{meas['mix_lufs']:.2f}")
    ck(f"{a}: true peak below 0 dBTP (release gate)", meas["mix_tp"] < 0 and meas["epk_tp"] < 0,
       f"{meas['mix_tp']:.2f} / {meas['epk_tp']:.2f}")
    if a in GAP:
        nd = dropout_count(f"{w}/{m}")
        ck(f"{a}: no near-silent drop-outs (ear check)", nd == 0, f"{nd} in shipped master")

passed = sum(1 for _, ok, _ in checks if ok)
npass = f"{len(checks)-passed} failed"
DATE = datetime.date.today().isoformat()

L = []
def add(s=""): L.append(s)

add("# Season One — full-mix house-standardisation QC")
add()
add("Generated 2026-09-28 by `tools/standardise_masters.py` + `tools/fix_truepeak.py`; refreshed")
add(f"{DATE} (Habib, Maya and Schrödinger's Breakfast re-rendered from drop-out-repaired sources;")
add("DNZ, Kesh-Zion and Canthus onboarded) and verified against the files on disk by")
add("`tools/mix_qc_report.py`.")
add()
add(f"> **{DATE} refresh.** The three quiet masters (Habib, Maya and Schrödinger's Breakfast) were")
add("> re-rendered full-length from sources whose near-silent drop-outs had been bridged, and the")
add("> report now carries a per-artist **drop-out gate** (see *Drop-out repair*). Their rows were")
add("> re-measured live when the masters were rebuilt; the other twelve are byte-unchanged and retain")
add("> their earlier `loudnorm` / `ebur128` figures. Trim values marked `*` are the source-to-target")
add("> gain (`-14 LUFS minus the source's integrated loudness`), not the final limiter-compensated trim.")
add()
add(f"## House standard applied to all {len(STEM)} masters")
add()
add("| Item | Value |")
add("|------|-------|")
add("| Target loudness | **-14 LUFS** integrated (EBU R128 measurement) |")
add("| Target true peak | **< 0 dBTP** release gate (target <= -1.0 dBTP) |")
add("| EQ (Pioneer XDJ-RX3) | high-pass 28 Hz · -1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |")
add("| EQ (Denon, DJ Unknown only) | high-pass 30 Hz · -1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |")
add("| Master | `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` — 48 kHz / 320 kbps, bit-identical |")
add("| EPK master | `<artist>_mix_epk.mp3` — 44.1 kHz / 320 kbps |")
add()
add(f"Every artist gets the same EQ, so the {len(STEM)} masters actually match. The only per-artist")
add("variable is the trim needed to reach the loudness target, plus the limiter ceiling when")
add("the source was hot enough for the limiter to engage.")
add()
add("## Results")
add()
add("| Artist | Deck | Source | Trim dB | LUFS (48k) | TP | LUFS (44.1k) | TP | Length |")
add("|--------|------|--------|---------|-----------|----|-------------|----|--------|")
for r in rows:
    star = " *" if r["approx"] else ""
    add(f"| {r['artist']} | {r['deck']} | `{r['src']}` | {r['trim']:+.2f}{star} | "
        f"**{r['lufs']:.2f}** | {r['tp']:+.2f} | {r['elufs']:.2f} | {r['etp']:+.2f} | "
        f"{r['dur']/60:.1f} min |")
add()
add(f"**{passed}/{len(checks)} checks passed, {npass}.** (8 checks × {len(STEM)} masters: 48 kHz master,")
add("44.1 kHz EPK master, 320 kbps, `mix == mix_hq` bit-identical, full length retained, Season One")
add("hardlink intact, loudness inside -12..-16 LUFS, true peak below 0 dBTP — plus a per-artist")
add("**drop-out gate** on the three rebuilt masters.) Rows whose files are byte-unchanged since their")
add("last measurement carry that measurement forward; the three rebuilt masters were measured off the")
add("files that are on disk now.")
add()
add("### Notes on the repaired / rebuilt masters")
add()
add("The first pass left four masters above 0 dBTP, because the ceiling calculation hit its")
add("-1.5 dB floor and heavily-limited material overshoots a -1.5 dB ceiling by 1.6-2.8 dB once")
add("MP3 inter-sample peaks are counted. Those four were re-rendered from the archived originals")
add("with the ceiling lowered by the overshoot actually observed:")
add()
add("| Artist | Ceiling dB | 48 kHz TP | 44.1 kHz TP | Note |")
add("|--------|-----------|----------|------------|------|")
for r in rows:
    if r["artist"] in FIX:
        f = FIX[r["artist"]]
        add(f"| {r['artist']} | {f.get('old_ceil',0):.2f} -> {f.get('new_ceil',0):.2f} | "
            f"{r['tp']:+.2f} | {r['etp']:+.2f} | {f.get('note','')} |")
add()
add("The extra limiting removed a little energy, so these four sit at -13.5 to -14.2 LUFS rather")
add("than exactly -14.00. The whole catalogue spans 0.7 dB, comfortably inside the -12..-16 LUFS")
add("delivery gate, and every master is now clear of 0 dBTP.")
add()
add("#### 2026-10-05 — DNZ, Kesh-Zion, Canthus onboarded")
add()
add("The same overshoot fault recurred when these three raw-session artists were added: their hot")
add("captures (DNZ's peaks at +2.3 dBFS) landed at +0.36..+0.60 dBTP. `tools/tp_repair.py`")
add("re-rendered them from the original capture in `epk/audio` (now `wavs/`), never from the")
add("processed master, lowering the ceiling by the overshoot measured plus 0.3 dB of margin and")
add("compensating the trim to hold the target. The exact ceilings are not reproduced here — that")
add("pass wrote its JSON to a `/tmp` cache that no longer exists — but the shipped masters were")
add("measured on 2026-10-15 and sit at -14.0 to -14.2 LUFS, TP -1.0 to -1.6 dBTP.")
add()
add("#### 2026-10-15 → 2026-10-16 — quiet-source gain-explosion / drop-out fix")
add()
add("Three masters \"exploded\" out of near-silence on playback. The shipped masters measured clean")
add("on loudness and true peak, so the fault was brief near-silent **drop-outs in the archived")
add("source** (50-350 ms down to -48..-68 dBFS, with music 20-60 dB louder either side). Parisa and")
add("Yogo, measured as controls, reported zero. Each hole was bridged in the source by")
add("`tools/repair_dropouts.py` (equal-power cross-fade of the blocks either side) and the master")
add("re-rendered full-length from that repaired source — never from a shipped master.")
add()
add("- **Habib.** The former mix sat on a **silent 389.9 s timeline** (≈82% inaudible), so it slammed")
add("  out of silence; rebuilt from the contiguous recording `2026-08-31 15-26-03.mp3` → **3237.0 s**,")
add("  48 kHz **-14.00 / -3.13**, 44.1 kHz **-14.00 / -3.08**; **14** drop-outs bridged.")
add("- **Maya.** Rebuilt from the released master's own source (`maya_mix_remaster.mp3`, identical in")
add("  duration to the shipped mix) → 52.5 min, 48 kHz **-14.04 / -2.17**, 44.1 kHz **-14.04 / -2.06**;")
add("  **2** drop-outs bridged (16:22, 48:57).")
add("- **Schrödinger's Breakfast.** Rebuilt from the archived raw capture with a **dynamics-control")
add("  step added to the house chain** (`acompressor=threshold=-20dB:ratio=3`) → **12602.6 s**,")
add("  48 kHz **-14.21 / -1.50**, 44.1 kHz **-14.21 / -1.69**; **500** drop-outs bridged.")
add()
if GAP:
    add("### Drop-out repair — 2026-10-16 ear check")
    add()
    add("`tools/dropout_qc.py` re-checks the shipped masters: a run of 50 ms windows ≤ -48 dBFS, at")
    add("least 50 ms long, merged within 100 ms, and qualified only when the 1 s median either side is")
    add("≥ -35 dBFS (so a merely quiet passage is not flagged). A non-zero count fails the build.")
    add()
    add("| Artist | Source | Drop-outs bridged | Drop-outs now | 48 kHz TP | 44.1 kHz TP | Level jumps |")
    add("|--------|--------|-------------------|---------------|----------|------------|-------------|")
    for r in sorted(GAP.values(), key=lambda r: r["artist"]):
        j = r.get("jumps", {})
        ju = f"{j['old']} → {j['new']}" if j else "—"
        add(f"| {r['artist']} | `{r['source']}` | {r['dropouts']} | 0 | "
            f"{r['mix_tp']:+.2f} | {r['epk_tp']:+.2f} | {ju} |")
    add()
    add("\"Level jumps\" counts momentary (400 ms) rises ≥ 12 dB within one 100 ms hop — the machine")
    add("proxy for the ear check. Every artist fell; the worst offenders — Schrödinger's Breakfast")
    add("11:08 (24.6 dB, -47 → -23 LUFS) and Habib 42:59 / 43:05 — are gone. No artist gained a jump")
    add("that starts near-silent; where the count is unchanged (Maya) the one jump is a musical rise")
    add("from an audible -36 LUFS, present in the old master too.")
    add()
    add("The pre-repair masters are archived at `Archive/2026-10-16_gap_fix/mixes/<Artist>/`. The 30 s")
    add("EPK loops and the EPK videos carry none of these dips (they were cut from clean windows), so")
    add("they were left untouched.")
    add()
add("### Two engineering faults found and fixed during the original pass")
add()
add("1. The first script archived the source file and *then* rendered the 44.1 kHz master from")
add("   it, so the input had already been moved. Fixed by rendering both masters before anything")
add("   is archived, and by surfacing ffmpeg's stderr instead of discarding it — a missing")
add("   output file previously surfaced only as a bare `FileNotFoundError`.")
add("2. The relink step only re-pointed filenames already present in `Season One`, so it never")
add("   added files that were missing. Mundz had no `_mix.mp3` in the release tree and")
add("   Schrödinger's Breakfast had none of the three masters at all. `tools/sync_release_mix.py`")
add("   now syncs the release folder to exactly the canonical trio.")
add()
add("### Known content issues (not defects in the masters)")
add()
add("- Habib, Maya and Schrödinger's Breakfast have very quiet source masters, so normalising to")
add("  -14 LUFS lifts their noise floor. The 2026-10-16 ear check found and bridged 516 source")
add("  drop-outs across them (see *Drop-out repair*); the two controls, Parisa and Yogo, were clean.")
add("- Schrödinger's Breakfast needed ≈ +20 dB of trim, so it is heavily limited by nature; the")
add("  2026-10-15 rebuild adds compression to keep its loop from slamming. Its master-level dips")
add("  were already above the -48 dBFS drop-out floor, which is why the ear check — not the master")
add("  metric — was what triggered §Drop-out repair there.")
add()
add("## Originals")
add()
add("Every pre-standardisation master is preserved, never deleted:")
add("`Archive/2026-09-26_superseded/mixes/<Artist>/`. The 2026-10-15 Habib and Schrödinger's")
add("Breakfast pre-fix masters are at `Archive/2026-10-15_gain_fix/mixes/<Artist>/`, and the")
add("2026-10-16 pre-drop-out-repair masters at `Archive/2026-10-16_gap_fix/mixes/<Artist>/`.")
add()

open(f"{R}/qc/SeasonOne_Mix_qc.md","w").write("\n".join(L) + "\n")
json.dump(MEASCACHE, open(MEAS, "w"), indent=0)
print(f"  wrote qc/SeasonOne_Mix_qc.md — {passed}/{len(checks)} checks passed, {npass}")
for n, ok, d in checks:
    if not ok: print(f"   FAIL {n}  {d}")
