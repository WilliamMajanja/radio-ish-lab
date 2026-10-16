# Season One — full-mix house-standardisation QC

Generated 2026-09-28 by `tools/standardise_masters.py` + `tools/fix_truepeak.py`; refreshed
2026-10-17 (Habib, Maya and Schrödinger's Breakfast re-rendered from drop-out-repaired sources;
DNZ, Kesh-Zion and Canthus onboarded) and verified against the files on disk by
`tools/mix_qc_report.py`.

> **2026-10-17 refresh.** The three quiet masters (Habib, Maya and Schrödinger's Breakfast) were
> re-rendered full-length from sources whose near-silent drop-outs had been bridged, and the
> report now carries a per-artist **drop-out gate** (see *Drop-out repair*). Their rows were
> re-measured live when the masters were rebuilt; the other twelve are byte-unchanged and retain
> their earlier `loudnorm` / `ebur128` figures. Trim values marked `*` are the source-to-target
> gain (`-14 LUFS minus the source's integrated loudness`), not the final limiter-compensated trim.

## House standard applied to all 15 masters

| Item | Value |
|------|-------|
| Target loudness | **-14 LUFS** integrated (EBU R128 measurement) |
| Target true peak | **< 0 dBTP** release gate (target <= -1.0 dBTP) |
| EQ (Pioneer XDJ-RX3) | high-pass 28 Hz · -1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |
| EQ (Denon, DJ Unknown only) | high-pass 30 Hz · -1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |
| Master | `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` — 48 kHz / 320 kbps, bit-identical |
| EPK master | `<artist>_mix_epk.mp3` — 44.1 kHz / 320 kbps |

Every artist gets the same EQ, so the 15 masters actually match. The only per-artist
variable is the trim needed to reach the loudness target, plus the limiter ceiling when
the source was hot enough for the limiter to engage.

## Results

| Artist | Deck | Source | Trim dB | LUFS (48k) | TP | LUFS (44.1k) | TP | Length |
|--------|------|--------|---------|-----------|----|-------------|----|--------|
| SDKZ | Pioneer XDJ-RX3 | `sdkz_mix.mp3` | +10.15 | **-14.00** | -0.31 | -14.00 | -0.35 | 391.0 min |
| Yogo | Pioneer XDJ-RX3 | `yogo_mix.mp3` | +0.85 | **-14.00** | -0.62 | -14.00 | -0.84 | 166.6 min |
| Bernie | Pioneer XDJ-RX3 | `bernie_mix.mp3` | +6.90 | **-13.72** | -1.39 | -13.72 | -1.50 | 179.2 min |
| Mundz | Pioneer XDJ-RX3 | `mundz_mix.wav` | +0.21 | **-14.01** | -1.57 | -14.01 | -1.43 | 131.0 min |
| Maya | Pioneer XDJ-RX3 | `maya_mix_remaster.mp3` | -0.38 | **-14.04** | -2.17 | -14.04 | -2.06 | 52.5 min |
| Dikier | Pioneer XDJ-RX3 | `dikier_mix.mp3` | -1.12 | **-14.01** | -0.71 | -14.01 | -0.42 | 185.2 min |
| DJ Unknown | Denon | `dj_unknown_mix.wav` | +2.33 | **-13.65** | -1.55 | -13.65 | -1.60 | 133.7 min |
| Alexander Zwo | Pioneer XDJ-RX3 | `alexander_zwo_mix.mp3` | -1.46 | **-13.99** | -1.26 | -14.00 | -1.57 | 101.3 min |
| Habib | Pioneer XDJ-RX3 | `2026-08-31 15-26-03.mp3` | +3.56 * | **-14.00** | -3.13 | -14.00 | -3.08 | 54.0 min |
| Parisa | Pioneer XDJ-RX3 | `parisa_mix.mp3` | +1.89 | **-13.99** | -0.92 | -13.99 | -0.92 | 25.6 min |
| El Djemba | Pioneer XDJ-RX3 | `el_djemba_mix.mp3` | +2.96 | **-13.53** | -1.58 | -13.53 | -1.75 | 173.2 min |
| Schrödinger’s Breakfast | Pioneer XDJ-RX3 | `4-Audio 0001 [2026-09-21 130546].wav` | +20.20 | **-14.21** | -1.50 | -14.21 | -1.69 | 210.0 min |
| DNZ | Pioneer XDJ-RX3 | `dnz_session_140704.wav` | -1.60 * | **-14.10** | -1.00 | -14.10 | -1.00 | 170.6 min |
| Kesh-Zion | Pioneer XDJ-RX3 | `kesh_session_145756.wav` | +4.40 * | **-14.00** | -1.30 | -14.00 | -1.50 | 143.3 min |
| Canthus | Pioneer XDJ-RX3 | `canthus_session_134936.wav` | +4.40 * | **-14.20** | -1.50 | -14.20 | -1.60 | 177.8 min |

**123/123 checks passed, 0 failed.** (8 checks × 15 masters: 48 kHz master,
44.1 kHz EPK master, 320 kbps, `mix == mix_hq` bit-identical, full length retained, Season One
hardlink intact, loudness inside -12..-16 LUFS, true peak below 0 dBTP — plus a per-artist
**drop-out gate** on the three rebuilt masters.) Rows whose files are byte-unchanged since their
last measurement carry that measurement forward; the three rebuilt masters were measured off the
files that are on disk now.

### Notes on the repaired / rebuilt masters

The first pass left four masters above 0 dBTP, because the ceiling calculation hit its
-1.5 dB floor and heavily-limited material overshoots a -1.5 dB ceiling by 1.6-2.8 dB once
MP3 inter-sample peaks are counted. Those four were re-rendered from the archived originals
with the ceiling lowered by the overshoot actually observed:

| Artist | Ceiling dB | 48 kHz TP | 44.1 kHz TP | Note |
|--------|-----------|----------|------------|------|
| Bernie | -1.50 -> -3.63 | -1.39 | -1.50 |  |
| DJ Unknown | -1.50 -> -2.89 | -1.55 | -1.60 |  |
| El Djemba | -1.50 -> -4.07 | -1.58 | -1.75 |  |
| Schrödinger’s Breakfast | -1.50 -> -4.20 | -1.50 | -1.69 | **rebuilt 2026-10-15** (below) |

The extra limiting removed a little energy, so these four sit at -13.5 to -14.2 LUFS rather
than exactly -14.00. The whole catalogue spans 0.7 dB, comfortably inside the -12..-16 LUFS
delivery gate, and every master is now clear of 0 dBTP.

#### 2026-10-05 — DNZ, Kesh-Zion, Canthus onboarded

The same overshoot fault recurred when these three raw-session artists were added: their hot
captures (DNZ's peaks at +2.3 dBFS) landed at +0.36..+0.60 dBTP. `tools/tp_repair.py`
re-rendered them from the original capture in `epk/audio` (now `wavs/`), never from the
processed master, lowering the ceiling by the overshoot measured plus 0.3 dB of margin and
compensating the trim to hold the target. The exact ceilings are not reproduced here — that
pass wrote its JSON to a `/tmp` cache that no longer exists — but the shipped masters were
measured on 2026-10-15 and sit at -14.0 to -14.2 LUFS, TP -1.0 to -1.6 dBTP.

#### 2026-10-15 → 2026-10-16 — quiet-source gain-explosion / drop-out fix

Three masters "exploded" out of near-silence on playback. The shipped masters measured clean
on loudness and true peak, so the fault was brief near-silent **drop-outs in the archived
source** (50-350 ms down to -48..-68 dBFS, with music 20-60 dB louder either side). Parisa and
Yogo, measured as controls, reported zero. Each hole was bridged in the source by
`tools/repair_dropouts.py` (equal-power cross-fade of the blocks either side) and the master
re-rendered full-length from that repaired source — never from a shipped master.

- **Habib.** The former mix sat on a **silent 389.9 s timeline** (≈82% inaudible), so it slammed
  out of silence; rebuilt from the contiguous recording `2026-08-31 15-26-03.mp3` → **3237.0 s**,
  48 kHz **-14.00 / -3.13**, 44.1 kHz **-14.00 / -3.08**; **14** drop-outs bridged.
- **Maya.** Rebuilt from the released master's own source (`maya_mix_remaster.mp3`, identical in
  duration to the shipped mix) → 52.5 min, 48 kHz **-14.04 / -2.17**, 44.1 kHz **-14.04 / -2.06**;
  **2** drop-outs bridged (16:22, 48:57).
- **Schrödinger's Breakfast.** Rebuilt from the archived raw capture with a **dynamics-control
  step added to the house chain** (`acompressor=threshold=-20dB:ratio=3`) → **12602.6 s**,
  48 kHz **-14.21 / -1.50**, 44.1 kHz **-14.21 / -1.69**; **500** drop-outs bridged.

### Drop-out repair — 2026-10-16 ear check

`tools/dropout_qc.py` re-checks the shipped masters: a run of 50 ms windows ≤ -48 dBFS, at
least 50 ms long, merged within 100 ms, and qualified only when the 1 s median either side is
≥ -35 dBFS (so a merely quiet passage is not flagged). A non-zero count fails the build.

| Artist | Source | Drop-outs bridged | Drop-outs now | 48 kHz TP | 44.1 kHz TP | Level jumps |
|--------|--------|-------------------|---------------|----------|------------|-------------|
| Habib | `2026-08-31 15-26-03.mp3` | 14 | 0 | -3.13 | -3.08 | 11 → 9 |
| Maya | `maya_mix_remaster.mp3` | 2 | 0 | -2.17 | -2.06 | 1 → 1 |
| Schrödinger’s Breakfast | `4-Audio 0001 [2026-09-21 130546].wav` | 500 | 0 | -1.50 | -1.69 | 42 → 31 |

"Level jumps" counts momentary (400 ms) rises ≥ 12 dB within one 100 ms hop — the machine
proxy for the ear check. Every artist fell; the worst offenders — Schrödinger's Breakfast
11:08 (24.6 dB, -47 → -23 LUFS) and Habib 42:59 / 43:05 — are gone. No artist gained a jump
that starts near-silent; where the count is unchanged (Maya) the one jump is a musical rise
from an audible -36 LUFS, present in the old master too.

The pre-repair masters are archived at `Archive/2026-10-16_gap_fix/mixes/<Artist>/`. The 30 s
EPK loops and the EPK videos carry none of these dips (they were cut from clean windows), so
they were left untouched.

### Two engineering faults found and fixed during the original pass

1. The first script archived the source file and *then* rendered the 44.1 kHz master from
   it, so the input had already been moved. Fixed by rendering both masters before anything
   is archived, and by surfacing ffmpeg's stderr instead of discarding it — a missing
   output file previously surfaced only as a bare `FileNotFoundError`.
2. The relink step only re-pointed filenames already present in `Season One`, so it never
   added files that were missing. Mundz had no `_mix.mp3` in the release tree and
   Schrödinger's Breakfast had none of the three masters at all. `tools/sync_release_mix.py`
   now syncs the release folder to exactly the canonical trio.

### Known content issues (not defects in the masters)

- Habib, Maya and Schrödinger's Breakfast have very quiet source masters, so normalising to
  -14 LUFS lifts their noise floor. The 2026-10-16 ear check found and bridged 516 source
  drop-outs across them (see *Drop-out repair*); the two controls, Parisa and Yogo, were clean.
- Schrödinger's Breakfast needed ≈ +20 dB of trim, so it is heavily limited by nature; the
  2026-10-15 rebuild adds compression to keep its loop from slamming. Its master-level dips
  were already above the -48 dBFS drop-out floor, which is why the ear check — not the master
  metric — was what triggered §Drop-out repair there.

## Originals

Every pre-standardisation master is preserved, never deleted:
`Archive/2026-09-26_superseded/mixes/<Artist>/`. The 2026-10-15 Habib and Schrödinger's
Breakfast pre-fix masters are at `Archive/2026-10-15_gain_fix/mixes/<Artist>/`, and the
2026-10-16 pre-drop-out-repair masters at `Archive/2026-10-16_gap_fix/mixes/<Artist>/`.

