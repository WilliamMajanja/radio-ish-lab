# RELEASE CHECKLIST — Radio-ish Lab · Season One

Generated from real on-disk state. Every box below is either **done (verified)** or **open (named gap)**.

> **Currency (2026-10-16):** figures below now track the current catalogue — **15 artists**
> (12 original Season One acts + DNZ, Kesh-Zion, Canthus onboarded 2026-10-05). Where an item
> records something that legitimately covers only the original 12 (house-standard cover art,
> press one-pagers, the 62-entry EPK manifest), it says so.

## 1 · Toolchain
- [x] `ffmpeg` installed — `~/bin/ffmpeg`, static **arm64**, `ffmpeg version 4.4` — verified with `-version`
- [x] `ffprobe` installed — `~/bin/ffprobe`, static **arm64**, `ffprobe version n4.4.1` — verified with `-version`
- [x] `gh` installed — `~/bin/gh`, official release **arm64**, v2.101.0 — archive SHA-256 verified
- [x] No system install — both binaries live in `~/bin`, nothing written to `/usr/local` or `/opt`
- [x] Checksums recorded — SHA-256 of both binaries in `qc/SeasonOne_EPK_SHA256SUMS`
- [x] `ffmpeg` has the filters the EPK needs: `drawtext` (fine-print burn-in), `overlay`, `scale`
- [x] **Finalisation host note.** The original build machine was macOS (static `~/bin` binaries, whose
      SHA-256s are preserved in `qc/SeasonOne_EPK_SHA256SUMS` as provenance lines). The Yogo / Mundz /
      Schrödinger's Breakfast EPK videos were re-rendered here on the Linux host with system `ffmpeg`
      7.1.5 (`tools/render_epks_alpha.sh`), meeting the same h264/aac spec. `tools/regen_qc.py` runs
      on either host.

## 2 · Audio — seamless 30 s EPK loop per artist
- [x] 15/15 loops built from **real** audio on disk (multitrack master, or mastered EPK mix where no master exists)
- [x] 15/15 exact **30.000000 s** (verified with `afinfo` + `ffprobe`)
- [x] 15/15 **48 kHz / 24-bit stereo**
- [x] 15/15 **seamless** — 0.5 s equal-power crossfade, file ends on the sample it begins with; measured seam is at or below each track's own natural sample step
- [x] **Loudness QC — DONE.** All 15 loops at **-14 LUFS / -1.0 dBTP**; every EPK video inside the
      `-12…-16 LUFS` gate with true peak below 0 dBTP. `qc/SeasonOne_EPK_qc.md` — **150/150 checks**.
      Three defects found and fixed by this pass: three loops clipped past 0 dBTP, six sat outside
      the LUFS gate, and **Habib's loop had been cut from a silent 30 s window** near the head of
      its mix (effectively silent at -72 dBFS). All loops now 24-bit, matching the published spec.
- [x] 12/12 loops mirrored into `Season One/Artists/<Artist>/EPK/Audio/` (the three onboardings'
      EPK stacks are not yet mirrored — see §11)

## 3 · Full-length mixes — house standardisation
- [x] All 15 masters standardised to **one gain and one EQ** — `-14 LUFS`, true peak below 0 dBTP
- [x] Identical chain for every artist, so the catalogue is genuinely consistent, not just nominally
- [x] Pioneer XDJ-RX3 EQ for 14 artists; gentler Denon variant for DJ Unknown
- [x] `<artist>_mix.mp3` + `_mix_hq.mp3` — 48 kHz/320 kbps, **bit-identical**, encoded once
- [x] `<artist>_mix_epk.mp3` — 44.1 kHz/320 kbps, rendered from the same intermediate as the masters
- [x] **True-peak repair.** First pass left 4 masters above 0 dBTP (El Djemba +1.27, Bernie +0.83,
      Schrödinger +0.74, DJ Unknown +0.09) because the ceiling formula hit its -1.5 dB floor and
      heavily-limited material overshoots once MP3 inter-sample peaks count. All four re-rendered
      from the archived originals with the ceiling lowered by the overshoot measured.
- [x] All pre-standardisation masters preserved, never deleted — `Archive/2026-09-26_superseded/mixes/`
- [x] `qc/SeasonOne_Mix_qc.md` — per-artist trim, loudness, true peak, limiter ceiling — **123/123 checks**
      (8 checks × 15 masters + a drop-out gate on the three rebuilt)
- [x] **Ear check on the three quiet sources** — done 2026-10-16. The masters measured clean on
      loudness and true peak; the fault was brief near-silent **drop-outs in the archived source**
      (50-350 ms down to -48...-68 dBFS with music 20-60 dB louder either side). Bridged with
      `tools/repair_dropouts.py` and all three masters re-rendered full-length from the repaired
      sources — 516 drop-outs total. `tools/dropout_qc.py` re-checks the shipped files; see §12.

## 4 · Images — cover standard
- [x] 12/12 Season One artists: `cover_1080x1920_bw.png`, 1080×1920, **black background + white graphics**
- [x] DNZ / Kesh-Zion / Canthus ship a house-styled `*_titlecard_1080x1920.png` instead — all 15
      pass the cover check in `qc/SeasonOne_EPK_qc.md`
- [x] **Yogo-specific cover** — now a Yogo 1080×1920 house-standard cover (mirrored waveform drawn
      from Yogo's own 30 s loop). No longer a copy of the SDKZ cover; the SDKZ duplicate is archived
      at `Yogo/epk/_archive/pre_cover/`.
- [x] **Schrödinger's Breakfast artwork** — `cover_1080x1920_bw.png` now generated to the same
      house standard; EPK video re-rendered onto it. Original typographic title card kept in
      `epk/promo/` as a reference.

## 5 · Video — EPK mp4 per artist
- [x] 15/15 rendered — `h264` 1080×1920 `yuv420p` + `aac` 48 kHz stereo, 30.000 s (12 mirrored into `Season One/`)
- [x] `+faststart` for streaming
- [x] **Fine print burned in** (artist, style/genres, `RADIO-ISH LAB · SEASON ONE`, `30s seamless loop · 1080x1920`)
- [x] Every stream/duration claim verified with `ffprobe`, not assumed
- [x] Post-AAC true-peak repair applied where the encode overshot (Bernie, Schrödinger)

## 6 · Text — press publications
- [x] 15/15 `epk/text/FINE_PRINT_<TAG>_B4.md` on disk (500–800 B each); 15 mirrored into `Season One/Artists/<Artist>/Press/`
- [x] Genres sourced from `MASTER_README.md`, not invented
- [x] **Bernie tightened** — `Vinyl Classics / Deep House`, leading with Vinyl Classics so it no longer collides with SDKZ's Deep House
- [x] **12/12 press one-pagers** — `epk/index.md` **copied** into `Season One/Artists/<Artist>/Press/`.
      Mundz, Yogo and Schrödinger were missing these; created in this pass. The three onboardings
      have no `index.md` yet.
- [x] **Yogo + Mundz genres** — assigned from the published masters, not invented: Yogo
      `House / Techno`, Mundz `Live / Deep-Tech`. Fine print, press pages, EPK videos and the
      `MASTER_README.md` roster re-rendered to match.

## 7 · Release tree integrity
- [x] **45/45** mix files in `Season One/Artists/` verified as **hardlinks** to their working originals
      (same inode — cannot drift); the EPK/Press files are byte-verified **copies**
- [x] 45/45 mix hardlinks intact (`mix`, `mix_hq`, `mix_epk` × 15)
- [x] 65/65 EPK + press copies byte-identical to their working originals (37 EPK files +
      28 Press files; `DJ Unknown` release notes carries a dated addendum applied to both sides so
      the pair still matches)
- [x] 4/4 top-level Docs are identical **copies** of the top-level docs
- [x] **Two breaks found and fixed.** The relink step only refreshed filenames already present, so
      it never added missing ones: Mundz had no `_mix.mp3` in the release tree, and Schrödinger's
      Breakfast had none of the three masters. `tools/sync_release_mix.py` now syncs rather than
      refreshes, and archives (never deletes) non-matrix files it finds.
- [x] No tracked file exceeds GitHub's 100 MB limit — push is safe
- [x] All 27 top-level folders accounted for; no empty or orphaned directories

## 8 · Production publications
- [x] `qc/SeasonOne_EPK_qc.md` — loop/video stats table + per-artist checks + named gaps — **150/150**
- [x] `qc/SeasonOne_Mix_qc.md` — mix house standard + per-artist measured results — **123/123**
- [x] `qc/SeasonOne_EPK_SHA256SUMS` — **62 entries**: 12 loops + 12 EPK videos + 12 covers +
      12 fine prints + 12 press index pages + both binaries — all 60 deliverable hashes verified OK
      (the 2 toolchain lines are absolute macOS provenance paths and do not resolve off that host)
- [x] `qc/SeasonOne_Media_SHA256SUMS` — **689 files / 160.0 GiB**, AppleDouble sidecars excluded
- [x] This release checklist
- [x] **`MASTER_README.md` roster** — all 15 artists listed, header corrected from 9

## 9 · Press release gate
- [x] Loop loudness QC (§2)
- [x] Mix house standardisation (§3)
- [x] MASTER_README roster updated (§8)
- [x] Per-artist press one-pagers (§6)
- [x] Release tree integrity, no breaks or unhandled folders (§7)
- [x] Yogo + Mundz genre tags (§6) — assigned from the masters, fine print + mp4 re-rendered
- [x] Yogo cover art and Schrödinger's Breakfast artwork (§4)
- [x] Ear check on the three quiet-source masters (§3) — carried out 2026-10-16; the objective
      figures had hidden a drop-out defect. Fixed in §12.
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
- [x] **Season One tree re-synced** — 45/45 mix hardlinks restored (incl. Habib/Schrödinger via
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
      **120/120 checks passed.** (Since regenerated to **123/123** with the drop-out gate — see §12.)
- [x] Ear check on the quiet-source masters (unchanged from §3) — completed 2026-10-16, see §12.

## 11 · 2026-10-16 — documentation pass (update)

Repo documentation audited against on-disk state; nothing media-side was touched.

- [x] **`README.md` created** — project overview: roster, house standard, repository layout,
      verification commands, pipeline, working rules, status. Every figure in it checked against
      the tree and the QC reports.
- [x] **Five missed documents added to git** (they existed only inside gitignored working folders):
      - `Season One/Artists/DNZ/Press/FINE_PRINT_DNZ_B4.md`
      - `Season One/Artists/Kesh-Zion/Press/FINE_PRINT_KESH_ZION_B4.md`
      - `Season One/Artists/Canthus/Press/FINE_PRINT_CANTHUS_B4.md`
      - `Season One/Artists/DJ Unknown/Press/RELEASE_NOTES.md`
        (dated addendum: loudness/chain figures pre-date standardisation — current **-13.65 LUFS /
        -1.60 dBTP** per `qc/SeasonOne_Mix_qc.md`; same addendum written to the working original so
        the mirror stays byte-identical)
      - `LAB_SESSION_1_PINET-ALPHA_MIGRATION.md` (top level — the 184 GB catalogue migration record,
        previously only in `Schrödinger’s Breakfast/epk/lab session/`)
- [x] **`MASTER_README.md` corrected** — roster 12 → **15** (DNZ, Kesh-Zion, Canthus, status
      `ONBOARDED`), `96/96` → `120/120`, "all 12 masters" → "all 15", `~97 GB` → `~70 GB`,
      `Docs/` described as copies (they were never hardlinks), `Find It Fast` QC paths corrected.
      Mirrored to `Season One/Docs/`.
- [x] **`.gitignore` header corrected** — 139 → **234** files over 100 MB, `~97 GB` → `~160 GiB`,
      per-artist working folders `~70 GB`.
- [x] **This checklist and `Season One/README.md` brought in line with measured state**
      (12/12 → 15/15 where the catalogue is now 15, hardlink claims corrected to copies).
- [ ] **`MASTER_README.md` / release docs still name only the original 12 in `epk_lab_promotion.md`**
      — left alone deliberately: it is a dated label pitch, not a live index.

## 12 · 2026-10-16 — quiet-source drop-out repair (ear check)

The §3 ear check found "gain explosions" on the three quiet sources. Loudness and true peak on the
shipped masters were already clean, so the fault was not in the chain — it was brief near-silent
**drop-outs in the ARCHIVED SOURCE**: 50-350 ms windows down to -48…-68 dBFS, with music 20-60 dB
louder either side, so level leapt within one 100 ms window. Parisa and Yogo, measured as controls,
reported **zero**, confirming these are real defects and not a threshold artefact.

- [x] **Drop-out detector** `tools/dropout_qc.py` — runs of 50 ms windows ≤ -48 dBFS, ≥ 50 ms long,
      merged within 100 ms, qualified only when the 1 s median either side is ≥ -35 dBFS. Non-zero
      count fails the build (`exit 1`).
- [x] **Source repair** `tools/repair_dropouts.py` — equal-power cross-fade of the equally long
      blocks immediately before and after each hole (reversed, so the fill is continuous on both
      edges); iterated until no qualifying hole remains. Length is preserved and no second-
      generation encode is involved.
- [x] **Bridged drop-outs (source-side):** Habib **14** (`Habib/epk/audio/2026-08-31 15-26-03.mp3`),
      Maya **2** (`Archive/2026-09-26_superseded/mixes/Maya/maya_mix_remaster.mp3`, identity
      confirmed by exact-duration match with the shipped mix), Schrödinger's Breakfast **500**
      (`Archive/2026-09-26_superseded/mixes/Schrödinger’s Breakfast/4-Audio 0001 [2026-09-21 130546].wav`)
      — **516 in total**.
- [x] **All three masters re-rendered full-length from the repaired sources**, never from a shipped
      master. True peaks: Habib -3.13 / -3.08 dBTP, Maya -2.17 / -2.06, Schrödinger -1.50 / -1.69
      (48 kHz / 44.1 kHz) — all inside the ≤ -0.9 gate.
- [x] **Drop-out re-check on the shipped files:** Habib 6 → **0**, Maya 2 → **0**, Schrödinger
      **0** (its master-level dips were already lifted above the -48 floor by the +19.5 dB trim, which
      is why the ear check, not the master metric, was the trigger there).
- [x] **Level-jump count (momentary rises ≥ 12 dB within one hop):** Habib 11 → **9** (the two
      removed are exactly the 42:59 / 43:05 drop-out leaps), Maya 1 → **1** (the survivor is a
      musical rise from an audible -36 LUFS, present in the old master), Schrödinger **42 → 31**
      (worst, 11:08, was 24.6 dB from -47 LUFS); loudest-content metric `max_M` unchanged at -7.7, so
      dynamics were not squashed. No artist gained a near-silent-origin jump.
- [x] **Pre-repair masters archived** — `Archive/2026-10-16_gap_fix/mixes/<Artist>/`, never deleted.
- [x] **Release tree re-pointed** — `Season One/Artists/<Artist>/Mix/*` are hardlinks to the new
      `epk/mix` trio for all three artists (verified by inode).
- [x] **Downstream assets unaffected** — the three 30 s EPK loops and the three EPK videos were cut
      from clean windows and report 0 drop-outs, so they were left as-is.
- [x] **`tools/mix_qc_report.py` extended** — a per-artist drop-out gate and a "Drop-out repair"
      section (3 further checks: Habib, Maya, Schrödinger's Breakfast), plus the level-jump column.
- [x] **`qc/SeasonOne_Mix_qc.md` regenerated — done.** The tool's render-metadata caches
      (`standardise3.json` / `tpfix.json` / `tpfix2.json`) were reconstructed from the committed
      report + `gapfix.json`, and `tools/mix_qc_report.py` now keeps a per-file loudness cache
      (`mixmeas_cache.json`, keyed by size+mtime) so only a changed file is re-measured — every
      other row carries its last live measurement forward. Regenerated report:
      **123/123 checks passed, 0 failed** (120 structural + 3 drop-out gates). The three rebuilt
      masters' figures are the loudness/true-peak `loudnorm` measurements taken when they were
      re-rendered (`gapfix.json`, i.e. off the files now on disk). `tools/dropout_qc.py` confirms
      Habib / Maya / Schrödinger all **0** drop-outs.

## 13 · 2026-10-17 — public microsite + CI

The metadata repo now builds a public EPK microsite and ships through CI.

- [x] **Site generator** `tools/build_site.py` — renders `_site/` from tracked files only: the
      15-artist roster with covers, each artist's `Press/FINE_PRINT_*.md` (plus `index.md` /
      `RELEASE_NOTES.md` where present), the docs and the QC evidence. Artists without a mirrored
      cover fall back to a monogram and the genre is read from the fine print (`New artist — TBA`
      for the three onboardings). `_site/` is gitignored — the site is a view, never a source.
- [x] **Integrity gate** `tools/ci_check.py` — rejects committed media / oversized files, malformed
      `SHA256SUMS`, a season that isn't 15 artists, artists with no `Style / genres:` line, drift
      between the mirrored docs, Python / shell / JSON syntax errors, and (with `--site`) broken
      intra-site links. Run locally: **all checks passed**, 34 pages, 0 broken links.
- [x] **Site image** `deploy/Dockerfile` — multi-stage build (python + `markdown` → nginx) serving
      the site; built and smoke-tested locally (HTTP 200, cover served).
- [x] **Workflows** — `ci.yml` (integrity + site build/link check + markdownlint + shellcheck),
      `pages.yml` (deploy to GitHub Pages), `release.yml` (site bundle + press-kit zip +
      `SHA256SUMS` on tag `v*`), `package.yml` (GHCR image on tag `v*`). Linted clean with
      `actionlint`; release packaging dry-run locally.
- [x] **Local verification** — site builds (15 artists, 16 docs), all 8 doc mirrors byte-identical,
      `ci_check.py` green, Docker image builds and serves, markdownlint / shellcheck clean.
- [ ] **Enable Pages** — repo **Settings → Pages → Source: GitHub Actions** (`pages.yml` requests
      `enablement: true`, so the first push to `main` should self-enable; confirm the deploy job).
- [ ] **Cut the first tag** — push a `v…` tag to exercise `release.yml` and `package.yml` end-to-end.

