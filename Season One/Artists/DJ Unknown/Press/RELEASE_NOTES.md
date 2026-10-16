# DJ Unknown — RELEASE NOTES

**Release:** DJ Unknown — Continuous Set
**Label:** Radio-ish Lab
**Date:** 2026-09-19
**Artist:** DJ Unknown
**Genre:** House / Techno
**Duration:** 02:13:41.75 (single continuous set)
**Status:** Release-ready · QC OK

> **Figures below are pre-standardisation (noted 2026-10-16).** This note records the
> release state on 2026-09-19. The Season One standardisation pass since replaced the
> mastering chain, loudness figures and the "Roster 9/9" reference (the roster is now 15).
> Current verified figures for this master: **-13.65 LUFS integrated / -1.60 dBTP** —
> `qc/SeasonOne_Mix_qc.md`.

---

## Audio deliverables (canonical set)

| File | Sample rate | Bitrate | Notes |
|---|---|---|---|
| `mix/dj_unknown_mix.wav` | 48 kHz / 24-bit | lossless | archival master, WAV |
| `mix/dj_unknown_mix.mp3` | 48 kHz | 320 kbps | mastered master (hardlink of hq) |
| `mix/dj_unknown_mix_hq.mp3` | 48 kHz | 320 kbps | HQ mastered master |
| `mix/dj_unknown_mix_epk.mp3` | 44.1 kHz | 320 kbps | EPK / streaming master |
| `EPK_Project/DJ Unknown/dj_unknown_30s.mp3` | 48 kHz | 320 kbps | 30s broadcast promo seg |

### Loudness & QC
- EBU R128 integrated: **−15.3 LUFS** (full length), LRA 5.8 LU
- Sample peak: **−0.76 dBFS** (below 0 dBFS QC gate)
- 30s promo: I **−14.6 LUFS**
- Hashes: `QC_Reports/DJ Unknown_SHA256SUMS` · `EPK_Project/DJ Unknown/SHA256SUMS`

### Source / provenance
Ableton Live 24-bit/44.1k captures (hardlinked, non-destructive):
- `4-Audio 0001 [2026-09-19 152055].wav` → `audio/2026-09-19 15-20-55.wav` (36:46)
- `4-Audio 0003 [2026-09-19 160731].wav` → `audio/2026-09-19 16-07-31.wav` (1:36:55)
- `4-Audio 0002 [2026-09-19 152134].wav` → `audio/2026-09-19 15-21-34.wav` (06:19) — overlapping early take of the 0001 window; kept in `audio/`, not in the master.

Master = concat(0001, 0003). Chain (Ableton EPK_Master preset, executed via
ffmpeg): `afftdn nr=1.2` → highpass 40Hz → `volume +3.5dB` → glue comp 2.5:1/−16dB →
subtractive EQ 225/−3, 450/−2 → `alimiter 0.85`. Full recipe in `EPK_Audio_Workflow.md`.

---

## Visual deliverables

| Asset | Spec | Location |
|---|---|---|
| Session video pt.2 | 1080p60 original .mov + H.264 MP4 | `epk/video/` |
| Session video pt.1 | 1080p60 original .mov + H.264 MP4 | `epk/video/` |
| TikTok/Shorts/Snap clip | 9:16 1080×1920 · 30s · H.264+AAC 48k | `Social_Media/promo/DJ Unknown/` |
| Reels clip | 9:16 1080×1920 · 45s | `Social_Media/promo/DJ Unknown/` |
| X / Facebook clips | 16:9 1920×1080 · 60s | `Social_Media/promo/DJ Unknown/` |
| Cover art | 1080×1920 PNG | `Social_Media/promo/DJ Unknown/cover_1080x1920.png` |
| Banner | 1920×1080 PNG | `Social_Media/promo/DJ Unknown/banner_1920x1080.png` |
| Caption pack | per-platform | `Social_Media/promo/DJ Unknown/captions.md` |

All clips carry the `@radioish.lab` watermark (bottom-right, white ~60% opacity)
and use the mastered mix as the audible teaser (−14 LUFS gate). Watermark-free
H.264 proxies live in `epk/video/`.

---

## Platform release plan (ready to post)

1. **Day −1 teasers:** TikTok / Reels / Shorts / Snap 30–45s clips from
   `Social_Media/promo/DJ Unknown/` (hooks in `captions.md`).
2. **Day 0 drop:** full mix on Bandcamp / Mixcloud / SoundCloud →
   `Social_Media/{Bandcamp/DJ_Unknown_Release,Mixcloud,SoundCloud}/`.
3. **Day +2 spotlight:** 60s X + Facebook clips, cover/banner variants.

### Platform copies (mirrored, hardlinked, zero waste)
- `Social_Media/Bandcamp/DJ_Unknown_Release/dj_unknown_mix.mp3`
- `Social_Media/Mixcloud/dj_unknown_mix.mp3`
- `Social_Media/SoundCloud/dj_unknown_2026-09-19_master.mp3`

---

## Registry updates
- Roster 9/9 in `MASTER_README.md` · `epk_lab_promotion.md` · `EPK_Audio_Workflow.md`
- QC: `QC_Reports/DJ Unknown_qc_20260919_1830.md` · `QC_MASTER.md` (I −15.3)
- EPK promo index: `EPK_Project/INDEX.md` · seg in `EPK_Project/DJ Unknown/`
- QC tooling registered: `qc_checks.sh`, `qc_loud.py`, `build_segs.py`

🎛 live from the lab · #RadioishLab #LiveFromTheLab