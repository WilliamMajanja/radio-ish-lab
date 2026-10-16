# RELEASE CHECKLIST — Radio-ish Lab · Season One

Generated from real on-disk state. Every box below is either **done (verified)** or **open (named gap)**.

## 1 · Toolchain
- [x] `ffmpeg` installed — `~/bin/ffmpeg`, static **arm64**, `ffmpeg version 4.4` — verified with `-version`
- [x] `ffprobe` installed — `~/bin/ffprobe`, static **arm64**, `ffprobe version n4.4.1` — verified with `-version`
- [x] `gh` installed — `~/bin/gh`, official release **arm64**, v2.101.0 — archive SHA-256 verified
- [x] No system install — both binaries live in `~/bin`, nothing written to `/usr/local` or `/opt`
- [x] Checksums recorded — SHA-256 of both binaries in `qc/SeasonOne_EPK_SHA256SUMS`
- [x] `ffmpeg` has the filters the EPK needs: `drawtext` (fine-print burn-in), `overlay`, `scale`
- [x] **Finalisation host note.** The original build machine was macOS (static `~/bin` binaries, whose
      SHA-256s are preserved in `qc/SeasonOne_EPK_SHA256SUMS`). The Yogo / Mundz / Schrödinger's
      Breakfast EPK videos were re-rendered here on the Linux host with system `ffmpeg` 7.1.5
      (`tools/render_epks_alpha.sh`), meeting the same h264/aac spec. `tools/regen_qc.py` runs on
      either host.

## 2 · Audio — seamless 30 s EPK loop per artist
- [x] 12/12 loops built from **real** audio on disk (multitrack master, or mastered EPK mix where no master exists)
- [x] 12/12 exact **30.000000 s** (verified with `afinfo` + `ffprobe`)
- [x] 12/12 **48 kHz / 24-bit stereo**
- [x] 12/12 **seamless** — 0.5 s equal-power crossfade, file ends on the sample it begins with; measured seam is at or below each track's own natural sample step
- [x] **Loudness QC — DONE.** All 12 loops at **-14 LUFS / -1.0 dBTP**; every EPK video inside the
      `-12…-16 LUFS` gate with true peak below 0 dBTP. `qc/SeasonOne_EPK_qc.md` — 120/120 checks.
      Three defects found and fixed by this pass: three loops clipped past 0 dBTP, six sat outside
      the LUFS gate, and **Habib's loop had been cut from a silent 30 s window** near the head of
      its mix (effectively silent at -72 dBFS). All loops now 24-bit, matching the published spec.

## 3 · Full-length mixes — house standardisation
- [x] All 12 masters standardised to **one gain and one EQ** — `-14 LUFS`, true peak below 0 dBTP
- [x] Identical chain for every artist, so the catalogue is genuinely consistent, not just nominally
- [x] Pioneer XDJ-RX3 EQ for 11 artists; gentler Denon variant for DJ Unknown
- [x] `<artist>_mix.mp3` + `_mix_hq.mp3` — 48 kHz/320 kbps, **bit-identical**, encoded once
- [x] `<artist>_mix_epk.mp3` — 44.1 kHz/320 kbps, rendered from the same intermediate as the masters
- [x] **True-peak repair.** First pass left 4 masters above 0 dBTP (El Djemba +1.27, Bernie +0.83,
      Schrödinger +0.74, DJ Unknown +0.09) because the ceiling formula hit its -1.5 dB floor and
      heavily-limited material overshoots once MP3 inter-sample peaks count. All four re-rendered
      from the archived originals with the ceiling lowered by the overshoot measured.
- [x] All pre-standardisation masters preserved, never deleted — `Archive/2026-09-26_superseded/mixes/`
- [x] `qc/SeasonOne_Mix_qc.md` — per-artist trim, loudness, true peak, limiter ceiling — **96/96 checks**
- [ ] **Ear check on the three quiet sources** — Habib, Maya and Schrödinger's Breakfast have very
      quiet masters, so normalising to -14 LUFS lifts their noise floor

## 4 · Images — cover standard
- [x] 12/12 artists: `cover_1080x1920_bw.png`, 1080×1920, **black background + white graphics**
- [x] **Yogo-specific cover** — now a Yogo 1080×1920 house-standard cover (mirrored waveform drawn
      from Yogo's own 30 s loop). No longer a copy of the SDKZ cover; the SDKZ duplicate is archived
      at `Yogo/epk/_archive/pre_cover/`.
- [x] **Schrödinger's Breakfast artwork** — `cover_1080x1920_bw.png` now generated to the same
      house standard; EPK video re-rendered onto it. Original typographic title card kept in
      `epk/promo/` as a reference.

## 5 · Video — EPK mp4 per artist
- [x] 12/12 rendered — `h264` 1080×1920 `yuv420p` + `aac` 48 kHz stereo, 30.000 s
- [x] `+faststart` for streaming
- [x] **Fine print burned in** (artist, style/genres, `RADIO-ISH LAB · SEASON ONE`, `30s seamless loop · 1080x1920`)
- [x] Every stream/duration claim verified with `ffprobe`, not assumed
- [x] Post-AAC true-peak repair applied where the encode overshot (Bernie, Schrödinger)

## 6 · Text — press publications
- [x] 12/12 `epk/text/FINE_PRINT_<TAG>_B4.md` on disk (500–800 B each)
- [x] Genres sourced from `MASTER_README.md`, not invented
- [x] **Bernie tightened** — `Vinyl Classics / Deep House`, leading with Vinyl Classics so it no longer collides with SDKZ's Deep House
- [x] **12/12 press one-pagers** — `epk/index.md` hardlinked into `Season One/Artists/<Artist>/Press/`.
      Mundz, Yogo and Schrödinger were missing these; created in this pass.
- [x] **Yogo + Mundz genres** — assigned from the published masters, not invented: Yogo
      `House / Techno`, Mundz `Live / Deep-Tech`. Fine print, press pages, EPK videos and the
      `MASTER_README.md` roster re-rendered to match.

## 7 · Release tree integrity
- [x] **96/96** files in `Season One/` verified as hardlinks to their working originals
- [x] 36/36 mix hardlinks intact (`mix`, `mix_hq`, `mix_epk` × 12)
- [x] 4/4 top-level Docs hardlinks intact
- [x] **Two breaks found and fixed.** The relink step only refreshed filenames already present, so
      it never added missing ones: Mundz had no `_mix.mp3` in the release tree, and Schrödinger's
      Breakfast had none of the three masters. `tools/sync_release_mix.py` now syncs rather than
      refreshes, and archives (never deletes) non-matrix files it finds.
- [x] No tracked file exceeds GitHub's 100 MB limit — push is safe
- [x] All 22 top-level folders accounted for; no empty or orphaned directories

## 8 · Production publications
- [x] `qc/SeasonOne_EPK_qc.md` — loop/video stats table + 13 checks + named gaps
- [x] `qc/SeasonOne_Mix_qc.md` — mix house standard + per-artist measured results
- [x] `qc/SeasonOne_EPK_SHA256SUMS` — **62 entries**: 12 loops + 12 EPK videos + 12 covers +
      12 fine prints + 12 press index pages + both binaries — all 62 verified OK
- [x] This release checklist
- [x] **`MASTER_README.md` roster** — all 12 artists listed, header corrected from 9

## 9 · Press release gate
- [x] Loop loudness QC (§2)
- [x] Mix house standardisation (§3)
- [x] MASTER_README roster updated (§8)
- [x] Per-artist press one-pagers (§6)
- [x] Release tree integrity, no breaks or unhandled folders (§7)
- [x] Yogo + Mundz genre tags (§6) — assigned from the masters, fine print + mp4 re-rendered
- [x] Yogo cover art and Schrödinger's Breakfast artwork (§4)
- [ ] Ear check on the three quiet-source masters (§3) — objective noise-floor figures are
      published; the in-person listen still needs a human
- [x] Social_Media 9:16 + 16:9 clips for the remaining 10 artists — **done.** `tools/make_social_clips.sh`
      (the generator `SOCIAL_PLAYBOOK.md` referenced but that was missing) rendered the full platform
      set per artist (tiktok/shorts/snap 30 s + reels 45 s 9:16 · x/fb 60 s 16:9) from each artist's
      own live footage + mastered `*_mix_epk.mp3`. 60/60 verified. Parisa's source `.mov` is corrupt
      (`moov atom not found`), so her clips fall back to a still cover/banner + mix audio. A
      `captions.md` pack is written for each of the 10.
- [ ] **Platform uploads** (Mixcloud / SoundCloud / Bandcamp / Instagram / TikTok / etc.) — the clips
      and caption packs are ready; posting needs platform credentials/accounts and cannot be done from
      this machine.
- [x] GitHub repo published — public remote verified; `gh` authenticated

## 10 · 2026-10-15 — gain-explosion fix (update)

Two masters "exploded" out of near-silence on playback. Root cause found and fixed; all
dependent artifacts re-rendered. Every figure below was measured on the current files.

- [x] **Habib — released mix was ~82% near-silence.** The shipped mix sat on a silent
      389.9 s timeline with a few loud islands. Rebuilt full-length from the real contiguous
      recording: **3237.0 s (54 min)**, 48 kHz **-14.00 / -3.11 dBTP**, 44.1 kHz **-14.00 / -3.08**.
- [x] **Schrödinger's Breakfast — the 30 s EPK loop was cut from a bursty window.** Rebuilt the
      210-min master from the archived raw capture with a dynamics-control stage added to the
      house chain (tames the loop's burst swings): **12602.5 s (210 min)**,
      48 kHz **-14.21 / -1.50 dBTP**, 44.1 kHz **-14.21 / -1.69**.
- [x] **Loops rebuilt** from the fixed masters — Habib (offset 3150, **-14.00 / -6.68**),
      Schrödinger's (offset 2460, **-14.00 / -6.64**); the burst swings are gone.
- [x] **EPK videos re-rendered** — `HABIB_B4_EPK_30s.mp4`, `SCHRODINGERS_BREAKFAST_B4_EPK_30s.mp4`
      (h264 1080×1920 + aac 48 kHz, 30.000 s).
- [x] **Social-clip audio bug fixed.** Every non-Parisa clip had been muxed with the *camera-mic*
      audio instead of the mastered mix (missing stream mapping). Added `-map 0:v:0 -map 1:a:0`
      in `tools/make_social_clips.sh`; **all 60 clips re-rendered** at ~-14 LUFS.
- [x] **Season One tree re-synced** — 36/36 mix hardlinks restored (incl. Habib/Schrödinger via
      `tools/sync_release_mix.py`); the 48 EPK tree copies refreshed to match the working files.
- [x] **Manifests regenerated** — `qc/SeasonOne_EPK_SHA256SUMS` (62 entries, **150/150** checks via
      `tools/regen_qc.py`); `qc/SeasonOne_Media_SHA256SUMS` (**689 files, 160.0 GiB**, AppleDouble
      sidecars now excluded).
- [x] **New dirs** — `wavs/` (15 original per-artist WAVs, moved out of `*/epk/audio/`) and
      `mixes/` (15 master `_mix_hq` copies), staged for Telegram sharing.
- [x] **Tooling hardened** — `rebuild_loops_portable.py` seam rewired for ffmpeg 7.1 (the old
      single-input `acrossfade` graph produced no frames); `fix_gain_explosions.py` writes
      intermediates to disk (not `/tmp` tmpfs → OOM truncation) and validates render duration;
      `sync_release_mix.py`, `mix_qc_report.py`, `media_manifest.py` ported off macOS paths.
- [x] **`qc/SeasonOne_Mix_qc.md` refreshed** — now covers all **15** masters (Habib and
      Schrödinger's Breakfast rebuilt, DNZ/Kesh-Zion/Canthus onboarded). Changed/added rows were
      re-measured live with `ffmpeg ebur128=peak=true` (agrees with `loudnorm` to ±0.1 LU /
      0.02 dB, but runs ~43× realtime vs ~10×, so a full `loudnorm` re-measure would take ~8 h).
      **120/120 checks passed.**
- [ ] Ear check on the quiet-source masters (unchanged from §3).
