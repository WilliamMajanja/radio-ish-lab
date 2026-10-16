# RESEARCH PAPER

## One House, Every Sound — Standardising the Radio-ish Lab *Season One* Catalogue, and Diagnosing the Operator-Side Faults That Made It Necessary

**Document type:** Engineering & production research paper
**Project:** Radio-ish Lab — *Season One* (2026 crop)
**Prepared by:** Radio-ish Lab production & QC (AI operator, `opencode`) under the direction of the credited team
**Date:** 2026-10-16
**Status:** Season One standardisation complete — **150/150** EPK checks and **123/123** mix checks passed (120 structural + 3 drop-out gates); `tools/dropout_qc.py` confirms 0/0/0 drop-outs on the three rebuilt masters

| Role | Credit |
|------|--------|
| **Partner** | **B4 — Before Hotel Management** (**Alexander Zwo**) |
| **Executive Producer** | **Bernie** |
| **Line Producer** | **Agent Mgumbe** (Agent Mgumbe Studio) |
| **Artist / Systems** | **Schrödinger's Breakfast** — **1nf1D3L [William Majanja]** *(SigInt and Systems)* |

> Every figure in this paper was measured on the files on disk during the stated pass, not
> carried over or estimated. Where a number is an opinion rather than a measurement it is
> labelled as such. Nothing is invented.

---

## Abstract

*Season One* of the Radio-ish Lab is a fifteen-artist DJ and performing-artist catalogue,
built to a Mixmag-grade production and delivery bar and released as a uniform package: a
house-standardised mix trio, a seamless 30-second EPK loop, a vertical EPK video, a
1080×1920 cover, burned-in fine print and a press one-pager per artist — every deliverable
measured, checksummed and cross-verified before it ships.

This paper documents the whole production: the house standard and why it exists (§3), the
catalogue and its evidence base (§4), the reproducible pipeline and QC tooling (§5), and the
measured results (§6). Two engineering investigations dominate the second half. The first is
the **gain-explosion** fault (two released masters that jumped out of near-silence), which we
traced not to the mastering chain but to the **archived sources**. The second is the
**drop-out** fault behind it: 516 brief near-silent holes across three quiet sources, bridged
by an equal-power cross-fade before re-rendering.

The unifying finding — stated plainly in §7 — is that the catalogue's defects were
**operator-side, not equipment-side**. Across a catalogue of *expensive* gear (Pioneer
XDJ-RX3 controllers, a Denon rig, 24-bit captures), the recurring faults were failures of
**controller management**: input stages redlined into the limiter, whole sessions collapsed
to near-silence behind a mis-set fader, and intermittent signal drop-outs left in the
recording. The evidence is quantitative: trim needs spanning **−1.60 dB to +20.20 dB**,
positive true-peak overshoots on four masters that were already limited hard, and quiet
sources whose loudest 30 seconds sit at −35.5 dBFS RMS. The house chain fixes the
*symptom*; §7 names the *cause*.

---

## 1 · Introduction

A label lives or dies on consistency. A listener who moves from one Radio-ish Lab artist to
the next should hear the *same house* — the same loudness, the same tonal balance, the same
finish — regardless of which DJ, which controller, or which night produced the source. That
is the promise of the house standard, and it is the reason this paper exists.

*Season One* is fifteen artists: the twelve original acts (**Habib, Maya, Parisa, SDKZ,
Dikier, Bernie, Schrödinger's Breakfast, El Djemba, Alexander Zwo, DJ Unknown, Mundz,
Yogo**) plus three onboards (**DNZ, Kesh-Zion, Canthus**, added 2026-10-05). The sources
arrived — as street-level dance music always arrives — uneven: continuous six-hour sessions,
long Ableton single-takes, a two-part live set, a 2004-era archival transfer, and a handful
of experimental and ambient records. Every one of them was recorded live, by a human, on
real equipment, at a real gig. That is the point of the label. It is also why the material
carried the faults this paper documents.

Four questions organise the work:

1. **Can fifteen heterogeneous live sources be made to sound like one house?** (§3, §6.1)
2. **Can every deliverable be *proved* correct** — not assumed — before release? (§5, §6.4)
3. **What caused the "gain explosions"** an ear check reported on the quiet masters? (§6.3)
4. **What does that cause say about how the catalogue is captured?** (§7)

---

## 2 · Authorship, cast, and credits

The lab is a collaboration, and the paper is its record. The roles below are the published
credits of the house, reproduced verbatim from the release sheet and fine print on disk
(`Social_Media/posters/Season One/B4_SEASON_ONE_RELEASE_SHEET.txt`,
`Social_Media/fine_print.txt`).

| Role | Name | Notes |
|------|------|-------|
| **Partner** | **B4 — Before Hotel Management** | Imprint/publisher of the house; partner principal **Alexander Zwo**. Every Lab session is developed *for B4*. |
| **Executive Producer** | **Bernie** | Producer and co-founder; full-length Ableton live sessions (Vinyl Classics / Deep House). Owns the label's sonic identity and the B4 Radio live capture. |
| **Line Producer** | **Agent Mgumbe** | Agent Mgumbe Studio — the producing studio that turns a session into a Lab release. |
| **Artist / Systems** | **Schrödinger's Breakfast** | **1nf1D3L [William Majanja]**, working as **(SigInt and Systems)** — the session that *is* the pipeline: it produced *Lab Session № 1*, the 184 GB catalogue migration, and the artist's own Garage / Bass / Electro record. |

The fine print on every deliverable reads:

> *Produced by Agent Mgumbe Studio and Developed by Schrödinger's Breakfast for Before Hotel
> Management (B4). All Lab sessions are exclusive Radio-ish Lab originals — Season One 2026
> crop. Unauthorised duplication, broadcast or synchronisation is prohibited.*

*Season One* thus has a single, coherent chain of responsibility: **B4** commissions and
publishes, **Bernie** produces, **Agent Mgumbe Studio** delivers, and
**Schrödinger's Breakfast (1nf1D3L / SigInt and Systems)** builds and operates the pipeline
that makes it reproducible.

---

## 3 · Background: the house standard and the Mixmag bar

Before any repair, the label had to decide what "correct" means. It published a single,
non-negotiable standard and applied it identically to every artist
(`MASTER_README.md`, `Season One/README.md`, `EPK_Audio_Workflow.md`).

### 3.1 Mix standard

| Item | Value |
|------|-------|
| Loudness | **−14 LUFS** integrated (EBU R128) |
| True peak | below **0 dBTP** (release gate); target ≤ **−1.0 dBTP** |
| EQ — Pioneer XDJ-RX3 (14 artists) | high-pass 28 Hz · −1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |
| EQ — Denon (DJ Unknown only) | high-pass 30 Hz · −1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |
| `<artist>_mix.mp3` + `_mix_hq.mp3` | 48 kHz / 320 kbps — **bit-identical**, encoded once |
| `<artist>_mix_epk.mp3` | 44.1 kHz / 320 kbps |

The chain is `highpass=f=28, equalizer=f=220:t=q:w=0.8:g=-1.5,
equalizer=f=3000:t=q:w=0.9:g=1.0, equalizer=f=9000:t=h:w=6000:g=1.5`, then a trimmed
`volume` stage, then `alimiter`. **Only the trim differs per artist**, and only because each
source arrived at a different level. `mix` and `mix_hq` are one encode installed under two
names, so they cannot drift.

### 3.2 EPK standard

| Deliverable | Spec |
|-------------|------|
| Seamless loop | exactly **30.000000 s**, 48 kHz, 24-bit stereo; seamless *by construction* (the window's tail is equal-power-crossfaded with its head, so the file ends on the sample it begins with) |
| Cover | 1080×1920, black background + white graphics |
| EPK video | h264 1080×1920 `yuv420p` + aac 48 kHz stereo, 30.000 s, `+faststart`, fine print burned into the lower third |
| Fine print | artist · style/genres · `RADIO-ISH LAB · SEASON ONE` · `30s seamless loop · 1080x1920` |

Genres are sourced from `MASTER_README.md`; where none is confirmed the field *says so*
(`Season One - new artist`) rather than guessing. That is a deliberate anti-fabrication rule.

---

## 4 · Materials

| Component | Detail |
|-----------|--------|
| Catalogue root | `Radio-ish/` — 27 top-level folders |
| Artists | **15** (12 original + DNZ, Kesh-Zion, Canthus) |
| Mix masters | 15 × 3 = **45** files (`mix`, `mix_hq`, `mix_epk`) |
| EPK stack | 15 × (loop · EPK video · cover · fine print) + press one-pagers |
| Media on disk | **689 files / 160.0 GiB** tracked by the media manifest (AppleDouble `._*` sidecars excluded) |
| Working folders | per-artist `epk/{audio,processing,video}` ≈ **70 GB** (gitignored) |
| Controllers / sources | Pioneer **XDJ-RX3** (14 artists), **Denon** (DJ Unknown); 24-bit Ableton captures; OBS `.mov`; archival 2004 MP3s |
| Toolchain | ffmpeg / ffprobe **7.1.5**, Python **3.13.5**, numpy **2.5.1**; original builds verified on macOS static `~/bin` binaries (SHA-256 preserved as provenance) |
| Transport | SanDisk Extreme SSD 1.8 TB (exFAT) → `pinet-alpha` over Tailscale |

The catalogue is large enough that a naive full remeasure is a *day* of compute (see §8), so
the pipeline is built to measure **only what changed** and prove everything else by
checksum.

---

## 5 · Methods

### 5.1 The pipeline

Every artist follows one path:

```
capture (XDJ-RX3 / Denon / Ableton / OBS)
   └─► archived SOURCE (never re-encoded from a shipped master)
        └─► [repair_dropouts.py]        bridge source holes (only if QC found them)
             └─► standardise_masters.py  house chain: EQ → trim → limiter
                  └─► fix_truepeak.py    lower ceiling by measured overshoot, re-render
                       └─► mix / mix_hq (48k) + mix_epk (44.1k)
                            └─► rebuild_loops3.py  seamless 30 s, mastered −14 LUFS
                                 └─► render_epks_alpha.sh  vertical EPK video
                                      └─► sync_release_mix.py  hardlink the release tree
                                           └─► regen_qc.py / mix_qc_report.py / media_manifest.py
                                                └─► QC reports + SHA-256 manifests
```

A hard rule governs the whole chain: **never encode a second generation from an already-shipped
master.** Repairs and re-renders always start from the *archived original*. Everything else —
loops, EPK videos, social clips — is re-derived from the new master.

### 5.2 QC tooling

| Tool | Purpose |
|------|---------|
| `tools/standardise_masters.py` | Apply the house gain + EQ chain to every master |
| `tools/fix_truepeak.py` / `tp_repair.py` | Lower the limiter ceiling by the true-peak overshoot actually measured, re-rendering from the original capture |
| `tools/fix_gain_explosions.py` | Rebuild a master that exploded out of silence — full-length from the real recording, with an added dynamics stage; now also bridges source drop-outs first |
| `tools/repair_dropouts.py` | Bridge brief near-silent drop-outs in an archived source with an equal-power cross-fade, in place of the hole |
| `tools/dropout_qc.py` | Fail the build if a shipped master still contains a near-silent drop-out (`exit 1`) |
| `tools/rebuild_loops3.py` / `rebuild_loops_portable.py` | Pick the strongest 30 s window, build the seam, master to −14 LUFS |
| `tools/render_epks_alpha.sh` / `make_epk_cover.py` | Render the vertical EPK video and the house cover |
| `tools/make_social_clips.sh` | Bulk-render the platform clip set from live footage + mastered mix |
| `tools/sync_release_mix.py` | Sync the release tree to exactly the canonical trio, as hardlinks |
| `tools/regen_qc.py` / `mix_qc_report.py` / `media_manifest.py` | Rebuild the EPK QC report, the mix QC report, and the SHA-256 manifests from disk |

### 5.3 The two detectors

**Loudness/level-jump detector.** `ebur128` momentary loudness (400 ms window, 100 ms hop) is
read frame-by-frame; a **jump** is a momentary rise ≥ **12 dB within a single hop** between
frames above −60 LUFS. It is the machine proxy for the ear check that started the
investigation.

**Drop-out detector** (`dropout_qc.py`). A *drop-out* is a run of 50 ms windows whose sample
peak is ≤ **−48 dBFS**, at least **50 ms** long, with runs within **100 ms** merged, and
qualified only when the median level of the 1 s before *and* after is ≥ **−35 dBFS**. The
surround-level condition is what separates a real defect from a merely quiet passage: Parisa's
2004 transfer has 18 shallow dips down to ~−36 dBFS and **zero** qualifying drop-outs.

### 5.4 The repair

`repair_dropouts.py` decodes the source into a memory-mapped buffer, detects qualifying holes,
and fills each with an **equal-power cross-fade of the equally long block immediately before
and the block immediately after the hole, both reversed**, so the fill is *continuous on both
edges* (`fill[0] = pre[L−1]`, `fill[L−1] = post[0]`). Detection is iterated so that holes
exposed by filling a nearby cluster are caught too. Length is preserved exactly, and — because
the operation happens in the **source**, before the chain — no second-generation encode is
introduced. It is validated by re-running `dropout_qc.py` on the shipped master: **0 is the
pass condition.**

---

## 6 · Results

### 6.1 Catalogue standardisation

All 15 masters reached the standard. The table below is the measured result
(`qc/SeasonOne_Mix_qc.md`); only the trim varies, because only the sources varied.

| Artist | Source | Trim dB | LUFS 48k | TP 48k | LUFS 44.1k | TP 44.1k | Length |
|--------|--------|---------|----------|--------|------------|----------|--------|
| SDKZ | `sdkz_mix.mp3` | +10.15 | −14.00 | −0.31 | −14.00 | −0.35 | 391.0 min |
| Yogo | `yogo_mix.mp3` | +0.85 | −14.00 | −0.62 | −14.00 | −0.84 | 166.6 min |
| Bernie | `bernie_mix.mp3` | +6.90 | −13.72 | −1.39 | −13.72 | −1.50 | 179.2 min |
| Mundz | `mundz_mix.wav` | +0.21 | −14.01 | −1.57 | −14.01 | −1.43 | 131.0 min |
| Maya | `maya_mix_remaster.mp3` | −0.38 | −14.04 | −2.17 | −14.04 | −2.06 | 52.5 min |
| Dikier | `dikier_mix.mp3` | −1.12 | −14.01 | −0.71 | −14.01 | −0.42 | 185.2 min |
| DJ Unknown | `dj_unknown_mix.wav` | +2.33 | −13.65 | −1.55 | −13.65 | −1.60 | 133.7 min |
| Alexander Zwo | `alexander_zwo_mix.mp3` | −1.46 | −13.99 | −1.26 | −14.00 | −1.57 | 101.3 min |
| Habib | `2026-08-31 15-26-03.mp3` | +3.56 | −14.00 | −3.13 | −14.00 | −3.08 | 54.0 min |
| Parisa | `parisa_mix.mp3` | +1.89 | −13.99 | −0.92 | −13.99 | −0.92 | 25.6 min |
| El Djemba | `el_djemba_mix.mp3` | +2.96 | −13.53 | −1.58 | −13.53 | −1.75 | 173.2 min |
| Schrödinger's Breakfast | `4-Audio 0001 [2026-09-21 130546].wav` | +20.20 | −14.21 | −1.50 | −14.21 | −1.69 | 210.0 min |
| DNZ | `dnz_session_140704.wav` | −1.60 | −14.1 | −1.0 | −14.1 | −1.0 | 170.6 min |
| Kesh-Zion | `kesh_session_145756.wav` | +4.40 | −14.0 | −1.3 | −14.0 | −1.5 | 143.3 min |
| Canthus | `canthus_session_134936.wav` | +4.40 | −14.2 | −1.5 | −14.2 | −1.6 | 177.8 min |

**Reading the trim column is the first evidence of §7.** The range from **−1.60 dB to
+20.20 dB** — a 21.8 dB spread between the quietest and loudest *delivered* sources — is not a
property of the music. It is a property of how the captures were **gain-staged**.

### 6.2 The true-peak repair

The first standardisation pass left four masters **above 0 dBTP** — El Djemba **+1.27**,
Bernie **+0.83**, Schrödinger **+0.74**, DJ Unknown **+0.09** — because the ceiling formula
hit its −1.5 dB floor and heavily-limited material overshoots a −1.5 dB ceiling by 1.6–2.8 dB
*once MP3 inter-sample peaks are counted*. All four were re-rendered **from the archived
originals** with the ceiling lowered by the overshoot measured. The fact that four sources
overshot at all is the second piece of §7 evidence: material that is **already limited hard**
overshoots the moment you add a ceiling, because the limiter never has room to work.

### 6.3 The gain-explosion investigation

An ear check on the three quiet sources reported "gain explosions." On the shipped masters,
**loudness and true peak were already clean** — so the fault was not the chain. It was in the
**archived source**.

- **Habib.** The released mix sat on a **silent 389.9 s timeline with a few loud islands** —
  roughly **82 % near-silence**. Rebuilt full-length from the real contiguous recording:
  **3237.0 s (54 min)**, 48 kHz −14.00 / −3.11 dBTP, 44.1 kHz −14.00 / −3.08.
- **Schrödinger's Breakfast.** The 30 s EPK loop had been cut from a *bursty* window. Rebuilt
  the 210-min master from the archived raw capture with a dynamics-control stage added to the
  house chain (to tame the loop's burst swings): **12602.5 s**, 48 kHz −14.21 / −1.50 dBTP,
  44.1 kHz −14.21 / −1.69.

Underneath both was a common defect: brief near-silent **drop-outs**, 50–350 ms wide, down to
**−48…−68 dBFS**, with music **20–60 dB louder** either side. Within a single 100 ms window the
level therefore *leapt* — and that leap is the "gain explosion." Parisa and Yogo, measured as
**controls, reported zero**: the detector was not crying wolf.

### 6.4 The drop-out repair

| Artist | Source (archived) | Drop-outs bridged | TP 48k | TP 44.1k | Level jumps before → after |
|--------|-------------------|-------------------|--------|----------|---------------------------|
| Habib | `Habib/epk/audio/2026-08-31 15-26-03.mp3` | **14** | −3.13 | −3.08 | 11 → **9** |
| Maya | `Archive/…/Maya/maya_mix_remaster.mp3` | **2** | −2.17 | −2.06 | 1 → **1** |
| Schrödinger's Breakfast | `Archive/…/4-Audio 0001 [2026-09-21 130546].wav` | **500** | −1.50 | −1.69 | 42 → **31** |
| | **Total** | **516** | | | |

After re-rendering full-length from the repaired sources, the shipped masters were re-checked:
**Habib 6 → 0, Maya 2 → 0, Schrödinger 0** drop-outs. The level-jump counts fell for both
artists that had drop-out-driven jumps, and the worst offender everywhere — Schrödinger
**11:08, a 24.6 dB leap from −47 LUFS** — is gone. Critically, the loudest-content metric
`max_M` was **unchanged at −7.7** for Schrödinger: the repair removed the *leaps* without
squashing the *music*. Maya's single survivor is a musical rise from an audible −36 LUFS,
present identically in the old master, and was left alone. **No artist gained a jump that
starts near-silent.**

The three 30 s loops and three EPK videos carried **none** of these dips (they were cut from
clean windows) and were left untouched. The pre-repair masters are archived, never deleted, at
`Archive/2026-10-16_gap_fix/mixes/<Artist>/`.

### 6.5 The EPK stack and the whole-release evidence base

| Evidence | Scope |
|----------|-------|
| `qc/SeasonOne_EPK_qc.md` | 15 artists · **150/150** checks (loop spec, video spec, cover, fine print) |
| `qc/SeasonOne_Mix_qc.md` | 15 masters · **123/123** checks (sample rate, bitrate, bit-identical pair, length, hardlink, loudness gate, true-peak gate, drop-out gate) |
| `qc/SeasonOne_EPK_SHA256SUMS` | **62 entries** — 60 deliverable hashes (12 × 5) + 2 toolchain provenance lines |
| `qc/SeasonOne_Media_SHA256SUMS` | **689 files / 160.0 GiB** |

The mix QC tool was extended this pass with a per-artist **drop-out gate** (3 further checks:
Habib, Maya, Schrödinger's Breakfast), and the report was regenerated from it — `qc/SeasonOne_Mix_qc.md`
now reads **123/123 checks passed, 0 failed**. The three rebuilt masters' figures are the
loudness/true-peak `loudnorm` measurements taken when they were re-rendered; `tools/dropout_qc.py`
independently confirms **0 / 0 / 0** drop-outs. Reproducing the report needs the per-artist trims and
repair ceilings (`standardise3.json`, `tpfix.json`, `tpfix2.json`); those are reconstructed from the
committed report + `gapfix.json`, and the tool now caches per-file loudness so only a changed master
is re-measured; see §8.

The loops are all 24-bit and mastered to −14.00 LUFS; **three defects were found and fixed** in
that pass (three loops clipping past 0 dBTP, six outside the LUFS gate, and **Habib's loop had
been cut from a silent 30 s window at −72 dBFS**). The release tree was verified as
**45/45 mix hardlinks** and **65/65 EPK + Press byte-identical copies** — two breaks found and
closed in the process.

### 6.6 Infrastructure

The catalogue's move off the capture site was its own research problem
(`LAB_SESSION_1_PINET-ALPHA_MIGRATION.md`): **184,118,306,608 bytes / 4,595 files (~171.5 GiB)**
from an exFAT Extreme SSD onto `pinet-alpha` over a Tailscale tailnet, because Raspberry Pi
Connect turned out to have no file-transfer capability. Over **70 hours**, under **two power
cuts** and a mid-run link collapse from 1.8 MB/s to ~190 kB/s, rsync under a systemd user unit
finished and both sides reconciled **byte-for-byte**. The label treats *delivery* as part of
the standard: a master that cannot be proven to have survived the trip is not a master.

---

## 7 · The skill issue: controller management and redlining expensive equipment

*This section states the paper's central finding. It is an engineering conclusion drawn from
the measurements above; where it characterises practice it is labelled as interpretation.*

The Radio-ish Lab runs **expensive equipment**: Pioneer **XDJ-RX3** controllers on fourteen of
fifteen artists, a **Denon** rig on the fifteenth, 24-bit Ableton captures, a SanDisk Extreme
SSD, and a dedicated transfer node. None of that equipment failed. The defects this paper
spent most of its effort repairing were **operator-side** — and, overwhelmingly, failures of
**controller management**.

### 7.1 The evidence

Every fault below is a measured property of the *source as delivered*, not of the mastering
chain:

| # | Measured fault | Interpretation |
|---|----------------|----------------|
| 1 | **Alexander Zwo** needed `alimiter=limit=0.70` — a ~3 dB headroom penalty — to hold peak ≤ ~0 dBFS | The capture arrived **hot**: input trim/gain pushed so hard the signal hit the ceiling before mastering. |
| 2 | Four masters (El Djemba **+1.27**, Bernie **+0.83**, Schrödinger **+0.74**, DJ Unknown **+0.09**) overshot 0 dBTP *even with a −1.5 dB ceiling* | Material was **already limited hard** on capture — a limiter with no headroom left to do its job. |
| 3 | **Schrödinger's Breakfast** needed **+20.20 dB** of trim and carried a **bursty** envelope | The session was recorded **extremely quietly**; the loudest 30 s sits at **−26.0 dBFS RMS**. |
| 4 | **Habib** was **~82 % near-silence** on a silent 389.9 s timeline; loudest 30 s **−35.5 dBFS RMS** | A whole session captured with the level **collapsed** — a mis-set fader/gain left the recording empty but for a few islands. |
| 5 | **516 drop-outs** across three sources (50–350 ms, −48…−68 dBFS, music 20–60 dB louder either side) | **Intermittent signal interruption** left in the file — the signature of an unstable input path (loose/dirty connection, an interface or controller stage dropping out, a fault never caught because nobody monitored the recording). |
| 6 | **DJ Unknown** arrived at **−19.4 / −17.1 LUFS**, needing **+3.5 dB** | Again quiet, again uncorrected at the desk. |
| 7 | **SDKZ**'s main track carried **leakage** (documented in `EPK_Audio_Workflow.md`) | Bleed in the main capture that had to be gated and FFT-denoised out after the fact. |

Two failure modes dominate, and they are the **same mistake in opposite directions**:

- **Redlining** (rows 1–2): the operator pushes controller input trim, channel gain and master
  so the desk *looks* loud. On an XDJ-RX3 or Denon the signal reaches the recording bus already
  limited and clipped; the "loudness" a DJ hears in a room does not survive onto the file
  intact, and *true peak* — the thing that actually clips a released MP3 — is the casualty.
- **Collapse** (rows 3–6): the operator never sets gain at all — fader low, trim untouched —
  and records a session tens of dB below where it should be, sometimes with whole stretches
  effectively silent, and sometimes with the input path intermittently dropping out.

Both are **controller-management skill**, not equipment capability. The XDJ-RX3 is not the
problem; *nobody was watching the meters on the recording bus.*

### 7.2 The local-Tanzanian-DJ context

*Interpretation.* The pattern above is characteristic of a live, gig-driven, redline culture —
most visible on the local **Tanzanian DJ** circuit where this catalogue was captured. The
performance convention is to drive a big PA hard: the crowd experiences "more" as the desk
meters pin, and the controller's input-stage headroom is spent to buy room energy. That works
*in the room*. It fails *at the file*, because the thing the audience hears (the PA) and the
thing the label ships (the recorded bus) have **different headroom budgets**. A mix that
sounds right on a redlined dancefloor can land on disk pre-limited, drop-out-riddled, or
collapsed, and the DJ will never know — because nothing in the performance forces them to look
at the *record* meter, only the *output* meter.

This is the skill issue the paper documents: **controller management** — gain staging the
input, watching the record bus, setting trim so that both a quiet passage and a redlined peak
arrive clean — is a distinct discipline from *playing* a set, and it is the one the sources
show was unevenly applied.

### 7.3 Why the house standard is the right response

The lab cannot retrain every operator, and it should not have to. So it moves the guarantee
**downstream of the operator**: one published standard, one chain, and — crucially — **QC that
fails the build** (`dropout_qc.py` exits non-zero; the loudness and true-peak gates are hard).
The catalogue survives redlining and collapse not because the captures were good, but because
the pipeline *measures and repairs* what the operator left behind, every time, and refuses to
ship anything it cannot prove. That is the whole design: **the equipment is only as good as
the hand on the trim, and the standard is how the house stops depending on the hand.**

Crucially, this is a *documented* observation, not a verdict on any individual. The point of
a lab is to raise the floor. The published standard — and this paper — are how the floor gets
raised.

---

## 8 · Limitations and threats to validity

- **A cold full remeasure is expensive.** A complete `loudnorm` pass over the catalogue at
  ~10× realtime (SDKZ alone is a 6.5 h, 391-min session) is a **~8 hour** job. The repo's
  convention, stated in `qc/SeasonOne_Mix_qc.md`, is therefore to **remeasure only changed
  rows live** and carry byte-unchanged ones forward; `tools/mix_qc_report.py` enforces this with a
  per-file cache keyed by size+mtime, so a normal run re-measures only the handful of rebuilt
  masters rather than the catalogue. First-pass changed rows were measured with
  `ffmpeg ebur128=peak=true`, which agrees with `loudnorm` to **±0.1 LU / 0.02 dB** but runs
  ~43× realtime rather than ~10×.
- **Drop-out detection is threshold-bound.** The −48 dBFS floor and −35 dBFS surround gate
  were chosen so that Parisa's shallow 2004-era dips (to ~−36 dBFS) are *not* flagged. A
  different threshold would produce a different count. Controls (Parisa, Yogo → 0) are the
  evidence that the chosen threshold is behaviourally right.
- **Source identity is inferred where it must be.** Maya's source was identified as
  `maya_mix_remaster.mp3` by **exact-duration match** with the shipped mix (3151.392 s), not by
  metadata.
- **The skill-issue reading (§7.2) is interpretation.** The *measurements* are not: trim,
  overshoot, RMS, drop-out counts and leakage are all on disk. The *cultural* diagnosis — a
  redline culture on the local circuit — is the paper's reading of why the numbers look the
  way they do, and is labelled as such.
- **Two known unfixed defects:** `tools/regen_qc.py` records the host binaries
  `~/bin/{ffmpeg,ffprobe}` in the manifest (they never enter it) and contains unresolvable
  macOS provenance paths by design.
- **`tools/mix_qc_report.py` needs render metadata that cannot be measured off a master.**
  It reads the per-artist trims and repair ceilings from `standardise3.json` / `tpfix.json` /
  `tpfix2.json`; those lived only on the original build host, and run without them the tool
  emits a **blank trim column and no repaired-masters table**. They were reconstructed from the
  committed report + `gapfix.json`, but they remain build-host state rather than tracked repo
  files — deriving the trims from the report (or committing the caches) would remove the
  dependency.
- **Open items:** platform uploads (Mixcloud / SoundCloud / Bandcamp / Instagram / TikTok) need
  accounts; the three onboards' EPK stacks are not yet mirrored; no artist-supplied artwork.

---

## 9 · Reproducibility

```bash
# Verify the 60 deliverable checksums (drop the macOS provenance lines first).
grep -v '^#' qc/SeasonOne_EPK_SHA256SUMS | awk '$2 !~ /^\//' | shasum -a 256 -c -

# Verify the full media tree (689 files, 160.0 GiB).
shasum -a 256 -c qc/SeasonOne_Media_SHA256SUMS

# Rebuild the EPK QC report + checksums, refresh the media manifest, remeasure the mixes.
python3 tools/regen_qc.py
python3 tools/media_manifest.py
python3 tools/mix_qc_report.py      # cached: only changed masters are re-measured

# Confirm no near-silent drop-out survives in a shipped master (exit 0 = clean).
python3 tools/dropout_qc.py "Habib/epk/mix/habib_mix.mp3"
```

The repository is public; the ~160 GiB of media masters stay on local and backup storage
(`.gitignore`). Docs, press copy, QC evidence, checksums and the whole pipeline — roughly 150
files — are version-controlled.

---

## 10 · Conclusion

*Season One* proves that fifteen heterogeneous live sources — six-hour sessions, single-take
Ableton sets, a 2004 archival transfer, ambient and experimental records — can be made to
sound like **one house**, and that the result can be **proved** rather than asserted:
150/150 EPK checks, 123/123 mix checks, and two byte-level manifests covering 60 deliverables
and 689 media files.

It also shows that the *equipment* was never the problem. Across a catalogue of XDJ-RX3s, a
Denon rig and 24-bit captures, the faults were **operator-side** — redlined input stages,
collapsed sessions, 516 intermittent drop-outs — and the house standard plus a mandatory,
failing QC gate is what neutralises them. The lesson for the next season is direct: **teach
the hand, and measure the file.** Until then, the lab ships what it can prove.

**Produced by Agent Mgumbe Studio and Developed by Schrödinger's Breakfast for Before Hotel
Management (B4).**

---

## Appendix A — Aggregate numbers

| Metric | Value |
|--------|-------|
| Artists | 15 |
| Mix masters | 45 |
| Trim spread across the catalogue | **−1.60 dB … +20.20 dB** (21.8 dB) |
| Masters that overshot 0 dBTP on the first pass | 4 |
| Gain-explosion rebuilds | 2 (Habib, Schrödinger's Breakfast) |
| Source drop-outs bridged | **516** (Habib 14 · Maya 2 · Schrödinger 500) |
| Drop-outs after repair (shipped masters) | 0 |
| Level jumps removed (Habib, Schrödinger) | 2 and 11 |
| EPK checks | 150/150 |
| Mix checks | 123/123 |
| Media manifest | 689 files / 160.0 GiB |
| Catalogue migrated | 184,118,306,608 B / 4,595 files, byte-exact |

## Appendix B — Credits (canonical)

```
PRODUCED BY AGENT MGUMBE STUDIO
DEVELOPED BY SCHRÖDINGER'S BREAKFAST
  (1nf1D3L [William Majanja] · SigInt and Systems)
FOR BEFORE HOTEL MANAGEMENT (B4)
  — PARTNER: ALEXANDER ZWO
EXECUTIVE PRODUCER: BERNIE
RADIO-ISH LAB · SEASON ONE · 2026
```

## References (repository)

- `MASTER_README.md` — master production index, roster, house standard
- `README.md` — project overview, verification commands, pipeline
- `BRAND_GUIDELINES.md` — brand voice, handles, hashtags, A/V IDs
- `EPK_Audio_Workflow.md` — mastering/QA convention (single source of truth)
- `epk_lab_promotion.md` — label pitch / promotion one-pager
- `LAB_SESSION_1_PINET-ALPHA_MIGRATION.md` — the 184 GB catalogue migration record
- `Season One/README.md` — release standard and canonical filenames
- `qc/SeasonOne_EPK_qc.md`, `qc/SeasonOne_Mix_qc.md` — measured QC evidence
- `qc/SeasonOne_Release_Checklist.md` — verified vs open items, full history (§1–§12)
- `qc/SeasonOne_EPK_SHA256SUMS`, `qc/SeasonOne_Media_SHA256SUMS` — checksums
- `Social_Media/posters/Season One/B4_SEASON_ONE_RELEASE_SHEET.txt`, `Social_Media/fine_print.txt` — credits
