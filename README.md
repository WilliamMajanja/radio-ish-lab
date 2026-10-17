# Radio-ish Lab

> **One house. Every sound.** — A DJ & Performing Artist Lab releasing **Season One**,
> built to a Mixmag-grade production and delivery bar.

**Season One** gives every artist the same press-ready package: a house-standardised mix
trio, a seamless 30-second EPK loop, a vertical EPK video, a 1080×1920 cover, burned-in
fine print and a press one-pager — every deliverable measured, checksummed and
cross-verified before anything ships.

This repository holds the **release metadata** for that package: the documentation, press
copy, QC evidence, SHA-256 manifests and the reproducible ffmpeg/Python pipeline that
produced it. The audio and video masters themselves stay on local and backup storage.

**Radio-ish Lab is created by William Majanja and DJ Bernie Cyber.** Production is funded by
**B4 Hotel Management**.

---

## At a glance

| | |
|---|---|
| **Created by** | **William Majanja** and **DJ Bernie Cyber** |
| **Funded by** | **B4 Hotel Management** |
| **Artists** | 15 — 12 original Season One acts plus DNZ, Kesh-Zion and Canthus |
| **Mix masters** | 15 × 3 files — `mix` / `mix_hq` (48 kHz 320k, bit-identical) + `mix_epk` (44.1 kHz 320k) |
| **EPK stack per artist** | seamless loop · EPK video · cover · fine print · press one-pager |
| **EPK QC** | `qc/SeasonOne_EPK_qc.md` — **150/150 checks passed** |
| **Mix QC** | `qc/SeasonOne_Mix_qc.md` — **123/123 checks passed** |
| **Checksums** | 62-entry EPK manifest + **689-file / 160 GiB** media manifest |
| **Social** | 90 short-form clips across 12 artists, plus per-artist caption packs |
| **In git** | docs, press copy, QC evidence, checksums, pipeline — ~150 files |
| **Not in git** | ~160 GiB of masters, sessions, footage and artwork (see `.gitignore`) |

---

## Roster

Genres come from `MASTER_README.md` — **nothing is invented**. Where no genre has been
confirmed yet, the field says so rather than guessing.

| # | Artist | Style / role |
|---|--------|--------------|
| 1 | **Habib** | Deep house & melodic techno — 8 original tracks + DJ set |
| 2 | **Maya** | Experimental ambient electronica |
| 3 | **Parisa** | 2004-era nostalgic electronic |
| 4 | **SDKZ** | AfroHouse / AfroBeats / Deep House — six-hour continuous session |
| 5 | **Dikier** | Extended live techno sessions |
| 6 | **Bernie** | Vinyl Classics / Deep House — producer & co-founder · Ableton live sessions |
| 7 | **Schrödinger's Breakfast** | Garage / Bass / Electro |
| 8 | **El Djemba** | Ableton-recorded DJ set |
| 9 | **Alexander Zwo** | Ableton-recorded DJ set |
| 10 | **DJ Unknown** | Ableton-recorded DJ set — continuous two-part live session |
| 11 | **Mundz** | Live / Deep-Tech |
| 12 | **Yogo** | House / Techno |
| 13 | **DNZ** | Season One · new artist (genre not yet published) |
| 14 | **Kesh-Zion** | Season One · new artist (genre not yet published) |
| 15 | **Canthus** | Season One · new artist (genre not yet published) |

---

## The house standard

Every master gets the **same gain and the same EQ**, so the catalogue is genuinely
consistent rather than nominally so. Only the per-artist trim differs — and only because
each source arrived at a different level.

### Full-length mixes

| Deliverable | Spec |
|-------------|------|
| Loudness | **−14 LUFS** integrated (EBU R128) |
| True peak | **below 0 dBTP** release gate (target ≤ −1.0 dBTP) |
| EQ — Pioneer XDJ-RX3 | high-pass 28 Hz · −1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |
| EQ — Denon (DJ Unknown only) | high-pass 30 Hz · −1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |
| `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` | 48 kHz / 320 kbps, **bit-identical** — encoded once, installed under both names |
| `<artist>_mix_epk.mp3` | 44.1 kHz / 320 kbps — CD / streamer deliverable |

Per-artist trim, measured loudness, true peak and limiter ceiling: `qc/SeasonOne_Mix_qc.md`.

### EPK stack

| Deliverable | Spec |
|-------------|------|
| Seamless loop | exactly **30.000000 s**, 48 kHz, 24-bit stereo. Seamless *by construction*: the chosen window's `A[0.5:30.5]` is crossfaded against `A[0:0.5]`, so the file ends on the sample it begins with |
| Cover | 1080×1920, **black background + white graphics** |
| EPK video | h264 1080×1920 `yuv420p` + aac 48 kHz stereo, 30.000 s, `+faststart`, fine print burned into the lower third |
| Fine print | artist · style/genres · `RADIO-ISH LAB · SEASON ONE` · `30s seamless loop · 1080x1920` |

---

## Repository layout

```
Radio-ish/
├── README.md                  <- you are here
├── LICENSE                    <- proprietary — © 2026 William Majanja
├── MASTER_README.md           <- master production index: roster, architecture, deliverable matrix
├── EPK_Audio_Workflow.md      <- mastering / QA convention (single source of truth)
├── BRAND_GUIDELINES.md        <- voice, handles, watermarks, hashtag system
├── epk_lab_promotion.md       <- label pitch / promotion one-pager
├── LAB_SESSION_1_PINET-ALPHA_MIGRATION.md <- engineering record: the 184 GB catalogue migration
│
├── Season One/                <- THE RELEASE TREE (delivery view)
│   ├── README.md              <- release standard + canonical filenames
│   ├── Artists/<Artist>/
│   │   ├── EPK/Audio|Cover|Video/   <- loop · cover · <TAG>_B4_EPK_30s.mp4
│   │   ├── Mix/                     <- mix / mix_hq / mix_epk  (hardlinks)
│   │   └── Press/                   <- FINE_PRINT_<TAG>_B4.md + index.md
│   ├── QC/                    <- QC report, SHA256SUMS, release checklist
│   └── Docs/                  <- copies of the four top-level docs
│
├── {Artist}/epk/              <- WORKING FOLDERS (source of truth, ~70 GB)
│   ├── index.md               <- human-readable EPK
│   ├── audio/  processing/    <- original recordings, stems, intermediates
│   ├── mix/                   <- DELIVERABLES
│   ├── promo/  video/         <- cover art, original footage, EPK mp4
│   └── _archive/              <- superseded files (never deleted)
│
├── Social_Media/              <- platform-ready clips + captions (SOCIAL_PLAYBOOK.md)
├── Advertising/               <- ad copy one-pagers + campaign concepts
├── EPK_Project/               <- lab mix builds and segments
├── wavs/  mixes/              <- staged originals / master copies for delivery
├── qc/                        <- generated QA reports + checksums
├── QC_Reports/                <- per-artist QC records (2026-09)
├── Archive/                   <- superseded files, never deleted (gitignored)
└── tools/                     <- the pipeline that builds and verifies all of the above
```

**Working vs release.** `{Artist}/epk/` is the source of truth and holds the heavy material.
`Season One/` is the delivery view: mix deliverables are **hardlinks** to the canonical
working files (same inode, zero extra disk, cannot drift), and the EPK copies are verified
byte-for-byte against them.

---

## Verification

The claims in this repository are backed by files, not adjectives.

```bash
# Verify the 60 deliverable checksums in the EPK manifest. The file also carries
# two provenance lines for the original macOS build machine's ffmpeg/ffprobe,
# which cannot resolve on another host — so drop absolute paths first.
grep -v '^#' qc/SeasonOne_EPK_SHA256SUMS | awk '$2 !~ /^\//' | shasum -a 256 -c -

# Full-media manifest — 689 files, 160 GiB, all paths relative.
shasum -a 256 -c qc/SeasonOne_Media_SHA256SUMS

# Regenerate the EPK QC report + checksums from what is on disk.
python3 tools/regen_qc.py

# Refresh the media manifest (detects silent edits to any tracked media).
python3 tools/media_manifest.py

# Rebuild the mix QC report. Only files whose size+mtime changed are re-measured
# (a cold full loudnorm pass over the catalogue is ~8 h; a normal run is minutes).
python3 tools/mix_qc_report.py

# Confirm no near-silent drop-out survives in a shipped master (exit 0 = clean).
python3 tools/dropout_qc.py "Habib/epk/mix/habib_mix.mp3"
```

| Evidence | Scope |
|----------|-------|
| `qc/SeasonOne_EPK_qc.md` | 15 artists · **150/150 checks** (loop spec, video spec, cover, fine print) |
| `qc/SeasonOne_Mix_qc.md` | 15 masters · **123/123 checks** (sample rate, bitrate, bit-identical pair, length, hardlink, loudness gate, true-peak gate, drop-out gate) |
| `qc/SeasonOne_EPK_SHA256SUMS` | 62 entries — 60 deliverable hashes (12 artists × 5) + 2 toolchain provenance lines |
| `qc/SeasonOne_Media_SHA256SUMS` | 689 files · 160 GiB |
| `qc/SeasonOne_Release_Checklist.md` | 92 verified items · 3 open |

---

## Pipeline

All tooling has been ported to this Linux host: it resolves the system `ffmpeg` / `ffprobe`
(via `RADIOISH_FFMPEG` / `RADIOISH_FFPROBE` or `PATH`) and Python 3, with no dependency on the
original macOS paths.

| Tool | What it does |
|------|--------------|
| `tools/standardise_masters.py` | Apply the house gain + EQ chain to every master |
| `tools/fix_truepeak.py` / `tp_repair.py` | Lower the limiter ceiling by the true-peak overshoot actually measured, re-rendering from the original capture |
| `tools/fix_gain_explosions.py` | Rebuild a master whose released mix exploded out of silence (full-length from the real recording, with dynamics control). Also bridges source drop-outs first when `repair=True` |
| `tools/repair_dropouts.py` | Bridge brief near-silent drop-outs in an archived source with an equal-power cross-fade, in place of the hole, before re-rendering |
| `tools/dropout_qc.py` | Fail the build if a shipped master still contains a near-silent drop-out (`exit 1`) |
| `tools/rebuild_loops3.py` / `rebuild_loops_portable.py` | Pick the strongest 30 s window, build a seam, master to −14 LUFS |
| `tools/render_epks_alpha.sh` | Render the vertical EPK video — cover + seamless loop + burned-in fine print (Linux port of `render_epks.sh`) |
| `tools/make_epk_cover.py` | House-standard 1080×1920 cover from the artist's own loop |
| `tools/make_social_clips.sh` | Bulk-render the six-cut platform set from live footage + mastered mix |
| `tools/sync_release_mix.py` | Sync `Season One/Artists/<Artist>/Mix/` to exactly the canonical trio as hardlinks |
| `tools/regen_qc.py` | Rebuild the EPK QC report + SHA-256 manifest from disk |
| `tools/mix_qc_report.py` | Rebuild the mix QC report; re-measures only files whose size+mtime changed (the rest carry their last live measurement forward) |
| `tools/media_manifest.py` | SHA-256 the whole media tree (skips `.git`, `Archive/`, AppleDouble `._*`) |
| `tools/audit_masters.py` / `loudness_qc.py` | Independent loudness / peak audits |
| `tools/build_site.py` | Render the public EPK microsite from tracked files only |
| `tools/ci_check.py` | Repo integrity gate: media guard, manifest shape, artist/floor checks, mirror drift, broken links |

---

## Publishing & CI

The metadata in this repo also builds a public **EPK microsite** and ships as a release.

- `tools/build_site.py` renders the microsite from tracked files alone — the artist roster and
  covers, each artist's `Press/FINE_PRINT_*.md` (and `index.md` / `RELEASE_NOTES.md` where they
  exist), the docs and the QC evidence — into `_site/`. No HTML is hand-authored; the site is a
  view of the repository.
  ```bash
  pip install -r tools/requirements.txt
  python3 tools/build_site.py --out _site
  ```
- `tools/ci_check.py` is the integrity gate the CI runs: it rejects committed media and oversized
  files, malformed `SHA256SUMS`, a season that isn't 15 artists, artists without a genre line,
  drift between the mirrored docs, and — with `--site` — any broken intra-site link.

| Workflow | Trigger | Does |
|----------|---------|------|
| `.github/workflows/ci.yml` | push / PR | integrity gate · site build + link check · markdownlint · shellcheck |
| `.github/workflows/pages.yml` | push to `main` | builds the site and deploys it to **GitHub Pages** |
| `.github/workflows/release.yml` | tag `v*` | attaches the site bundle, a press-kit zip and `SHA256SUMS` to a GitHub Release |
| `.github/workflows/package.yml` | tag `v*` | publishes the site image to **GHCR** |

The site is `https://williammajanja.github.io/radio-ish-lab/`. The GHCR image is a multi-stage
build (`deploy/Dockerfile`) that builds the site and serves it with nginx:

```bash
docker build -f deploy/Dockerfile -t radio-ish-lab:season-one .
docker run --rm -p 8080:80 radio-ish-lab:season-one
```

---

## Social & distribution

`Social_Media/SOCIAL_PLAYBOOK.md` is the platform system: specs, cadence, hooks and the
posting rules. `tools/make_social_clips.sh` renders the asset set in bulk — TikTok / Shorts
/ Snap at 30 s (9:16), Reels at 45 s (9:16), X / Facebook at 60 s (16:9) — cropping the
artist's own live footage and laying the artist's **mastered** `*_mix_epk.mp3` under it,
never the raw camera mic. Caption packs live beside each artist's clips.

Full-length mixes are destined for Bandcamp / SoundCloud / Mixcloud at 320 kbps.

---

## Working rules

These are the conventions that keep the tree trustworthy:

1. **Nothing is invented.** Genres, specs and claims come from the docs on disk; unconfirmed
   fields are marked unconfirmed.
2. **Never delete.** Superseded files move to `{Artist}/epk/_archive/` or `Archive/`, never
   overwritten or removed.
3. **Render from originals only.** Re-encodes always start from the archived original, never
   from an already-processed master — no second-generation encodes.
4. **Hardlink identical duplicates.** Copies that must exist twice cost zero extra space.
5. **Filter AppleDouble `._*`.** The project was authored on macOS; sidecars are metadata, not media.
6. **Ship with evidence.** No deliverable ships without a QC report saying OK and a checksum.

---

## Status & open items

Objective checks are green (EPK **150/150**, mix **123/123**, manifests regenerated,
release tree verified). What still needs a human or an outside resource:

- **Ear check.** The objective ear check on the three quiet sources was carried out **2026-10-16**:
  516 near-silent drop-outs were bridged and `tools/dropout_qc.py` now reports **0** on all three
  (see §12 of the checklist). What remains is subjective — normalising these quiet sources to
  −14 LUFS lifts their noise floor, so someone should still listen for hiss before press.
- **Platform uploads.** Clips and captions are ready; posting needs credentials and can't be
  done from the build machine.
- **The three onboardings (DNZ, Kesh-Zion, Canthus).** Their masters are hardlinked into
  `Season One/` and their fine print is mirrored into `Press/`, but their EPK (Audio/Cover/Video)
  copies and a press `index.md` are **not yet mirrored** into the release tree or captured in the
  EPK checksum manifest, their genre line is still the `Season One · new artist` placeholder, and
  they have no social clips yet.
- **Artwork.** Covers are house-standard typographic builds generated from each artist's own
  loop; no artist-supplied artwork has been supplied yet.

---

## Where to read next

| Read | For |
|------|-----|
| `MASTER_README.md` | The production index — roster, folder architecture, deliverable matrix |
| `Season One/README.md` | The release standard and canonical filenames |
| `EPK_Audio_Workflow.md` | The mastering/QA convention behind every master |
| `BRAND_GUIDELINES.md` | Voice, handles, hashtags, watermarks, ID3 tags |
| `Social_Media/SOCIAL_PLAYBOOK.md` | Platform specs, hooks and posting cadence |
| `qc/SeasonOne_Release_Checklist.md` | Verified items vs open gaps |
| `LAB_SESSION_1_PINET-ALPHA_MIGRATION.md` | How the 184 GB catalogue was migrated onto the build host |

---

## License

**Proprietary — © 2026 William Majanja. All rights reserved.** See [`LICENSE`](LICENSE).

Radio-ish Lab is created by **William Majanja** and **DJ Bernie Cyber**; production is funded by
**B4 Hotel Management**.

No permission is granted to copy, reproduce, modify, distribute or reuse any part of this
repository — code, tooling, documentation, press copy, artwork or metadata — without the
prior written consent of the owner. "Radio-ish Lab" and its marks are trademarks of the owner.
