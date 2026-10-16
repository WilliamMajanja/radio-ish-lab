# LAB SESSION № 1 — THE 184 GB MIGRATION

## Moving the Radio-ish catalogue from the Extreme SSD to pinet-alpha over a tailnet: a first-person account

**Artist:** Schrödinger's Breakfast (Garage / Bass / Electro)
**Session dates:** 2026-10-11 23:05 → 2026-10-15 09:41 EAT
**Author:** the lab's AI operator (opencode · GLM), executing on pinet (source site)
**Status:** COMPLETE — verified exact, both sides reconciled to the byte

---

## Abstract

On the night of 11 October 2026 I was asked to fetch the `Radio-ish` folder from the
SanDisk Extreme SSD attached to this Raspberry Pi. The folder measured **184,118,306,608
bytes (4,595 files, ~171.5 GiB apparent / 177 GiB on-disk)**; the Pi itself had **48 GB
free**, so a local copy was arithmetically impossible. The operator redirected me to
pinet-alpha, a second Pi on the same tailnet, nominally "using Raspberry Pi Connect".
That tool turned out to have no file-transfer capability at all, which forced a
transport redesign: key-bootstrapped SSH over Tailscale, carrying rsync under a
systemd user unit engineered specifically to survive the site's unreliable mains
power. Over the following 70 hours the transfer ate one network outage, **two power
cuts**, and a post-outage degradation of the local ISP link that collapsed throughput
from 1.8 MB/s to ~190 kB/s for the middle third of the run — and finished anyway,
resuming from mid-file each time without operator intervention. Final reconciliation:
**184,118,306,608 bytes, 4,595 files, identical on both sides.** This paper documents
the decisions, the numbers, the one bug I shipped and caught, and the diagnosis of
the slow middle.

---

## 1. Introduction — a fetch that could not fit

The instruction was four words long: *get the Radio-ish folder*. The Extreme SSD
(1.8 TB, exFAT, label `Extreme SSD`) was already mounted at
`/media/minima/Extreme SSD`, and `Radio-ish` — the label's complete working
catalogue: **fifteen artist EPK stacks** (the twelve of the `MASTER_README.md`
roster — Habib, Maya, Parisa, SDKZ, Dikier, Bernie, Schrödinger's Breakfast,
El Djemba, Alexander Zwo, DJ Unknown, Mundz, Yogo — **plus Canthus, DNZ and
Kesh-Zion**, operator-confirmed artists of the house not yet written into that
index), mixes, QC reports, tools, the works — sat at
177 GiB on-disk. The host Pi boots from a 117 GB SD card with 48 GB free. A local
copy was therefore impossible by inspection, before any tooling was chosen.

I put the arithmetic to the operator and proposed three routes. The operator chose
a fourth: *send it to pinet-alpha using Raspberry Pi Connect.*

## 2. Materials

| Component | Detail |
|---|---|
| Source host | Raspberry Pi `pinet`, user `minima`, Pi OS on 117 GB SD, 48 GB free |
| Source medium | SanDisk Extreme SSD, 1.8 TB, exFAT, single partition `sda1`, UUID `7ADC-CA53` |
| Payload | `Radio-ish/` — 184,118,306,608 B, 4,595 files |
| Destination | `pinet-alpha` (100.78.14.51, `pinet-alpha.tail9f4a65.ts.net`), NVMe root, 280 GB free |
| Overlay network | Tailscale; both nodes signed in under one operator account |
| Transfer engine | rsync 3.5.0 (`-rt --partial --timeout=180 --info=progress2`) |
| Supervision | systemd user unit + lingering, wrapper script |
| Remote access claim | Raspberry Pi Connect (screen share + remote shell) |

## 3. Phase I — routing survey, and a tool that couldn't do the job

I checked `rpi-connect status` first, in good faith: signed in, screen sharing
allowed, remote shell allowed. But reading the tool's full command surface, it
offers exactly two functions — VNC screen sharing and remote shell — both brokered
through a web browser, and **neither moves files**. Raspberry Pi Connect is a
remote-control product, not a transport. I record this as finding № 1, because it
is the finding that reshaped the whole session.

The tailnet, however, was alive: `pinet-alpha` answered ICMP at ~105 ms via the
Nairobi DERP relay. A pre-existing `~/.ssh/config` alias for `pinet-alpha` (fixed
identity file, `IdentitiesOnly`) showed someone had begun this setup before me;
the matching key had been generated that same evening but never authorised on the
far side — the remote rejected it (`Permission denied (publickey,password)`).

So the bootstrap problem was: I have no credentials, password auth is enabled,
and I must not use an interactive terminal for anything that must run unattended
for three days.

**Bootstrap.** The operator supplied a password (used once; **not recorded in this
paper — secrets do not belong in lab notes**). In one pass I used it to append
`~/.ssh/id_ed25519.pub` to pinet-alpha's `authorized_keys`, then immediately
re-verified with `ssh -o BatchMode=yes` that key auth worked with no password and
no prompts. From that moment the password was dead weight; the entire migration
ran on the key.

## 4. Phase II — transport design

Choices made, with reasons:

- **rsync over SSH over Tailscale**, rather than any bespoke sync: resumable at
  file *and* block granularity, idempotent re-runs, and its own verification
  (size + mtime) on every pass.
- **`-r -t` only** — no `-p/-g/-o`: exFAT cannot carry POSIX metadata, so
  preserving it is meaningless noise.
- **`--partial`** — an interrupted file is kept, and the next pass resumes it with
  the delta algorithm instead of restarting it. This single flag is why three
  crashes cost minutes rather than hours.
- **No `-z`** — the payload is audio/video; compression would trade Pi CPU for
  nothing.
- **`--timeout=180`** — a stalled socket (DERP relays do stall) must die, so the
  supervisor can restart the run. Without this, a hang is indistinguishable from
  progress.

I launched the first pass as a plain `nohup rsync` at ~23:11 and measured the
path: 0.7 → 1.0 → 1.2 MB/s over the first minutes, `tailscale ping` confirming
`via DERP(nai)` and *direct connection not established* — the local NAT is hard
(`MappingVariesByDestIP: true`, no IPv6), so the relay was not a fallback but the
only road. At 184 GB payload that meant roughly a **30-hour** campaign, not a
quick copy. The operator then added the requirement that defines this session:
*"have contingencies for powercuts."*

## 5. Phase III — engineering the contingencies

A 30-hour unattended run on unreliable mains and a relayed overlay needs four
independent safety systems. I built them all that same night:

1. **A systemd user unit** (`~/.config/systemd/user/rsync-radioish.service`)
   wrapping rsync in a supervisor with `Restart=on-failure`, `RestartSec=30`,
   `StartLimitIntervalSec=0` — it may fail an unlimited number of times, forever,
   and always try again. No `Restart=always`, so a *successful* exit actually
   ends the campaign.
2. **Lingering** (`sudo loginctl enable-linger minima`) so the user manager — and
   therefore the unit — starts at boot with no human login. This is the
   difference between "restarts after reboot if someone signs in" and
   "restarts after reboot".
3. **A fstab automount for the SSD** so the source medium can never be a manual
   dependency: `UUID=7ADC-CA53 /media/minima/Extreme\040SSD exfat
   defaults,nofail,x-systemd.automount,uid=1000,gid=1000,...`. UUID-keyed (survives
   `sda`→`sdb` reordering), `nofail` (never blocks boot), automount (mounts on
   first access). With this, the wrapper's first directory probe *causes* the
   mount.
4. **A self-healing wrapper script** (full listing in Appendix A): wait for the
   source directory to exist; wait until SSH to the far side actually answers;
   run rsync; **run it a second time as a verification pass** — a no-op scan that
   proves nothing is missing rather than assuming it; only then write the
   completion marker and exit 0. Exit codes 24 (source files vanished mid-run)
   are treated as success; anything else exits 1 and hands control back to
   systemd 30 s later.

Additionally: all output is tee'd into `~/rsync-radioish.log` (a plain file),
because on this OS the journal is volatile — a power cut erases `journalctl`,
and a lab that loses its own logs on the failure mode it studies would be a joke.

### 5.1 The bug I shipped

I am keeping this section in because a paper that omits its own defects is
marketing, not research. On first launch (23:16) the service sat "active" with
zero progress for ninety seconds. Diagnosis: my wrapper probed the network with
`ssh … "$DEST" true`, where `DEST="pinet-alpha:"` — rsync destination syntax.
ssh does not strip the trailing colon; it tried to resolve a host literally named
`pinet-alpha:`, failed, and my `until` loop swallowed the failure every 15 s.
Forever, by design. The fix was one variable (`HOST` without the colon) and a
service restart at 23:18. **Lesson: a wait-loop converts any bug into a silent
hang. Every wait-loop needs a bound and a complaint.**

## 6. Phase IV — field results

### 6.1 Timeline of the campaign

| Timestamp (EAT) | Event | System response |
|---|---|---|
| 10-11 23:11 | First rsync (nohup), 0.7→1.2 MB/s | — |
| 10-11 23:18 | Contingency stack installed; supervised run begins | — |
| 10-12 01:43 | **Network outage** (rsync rc=255 both passes) | systemd restart 30 s later; wrapper's SSH-wait held until 01:52; resumed mid-file |
| 10-12 04:20 | Steady 1.5–1.8 MB/s, 17.4 GB done (13%) | — |
| 10-12 ~19:08 | **Power cut № 1**; Pi reboots | fstab automount remounts SSD; linger starts unit; rsync skips 17.4 GB, resumes from partial |
| 10-12 19:48 | Post-outage throughput **~190 kB/s** (10× down) | still transferring — degraded, not down |
| 10-12 20:00–21:00 | Full link diagnosis (§6.3) | — |
| 10-12 → 10-14 | Grind at ~140–240 kB/s | — |
| 10-14 21:30 | **Pass 1 + verify pass clean — VERIFIED COMPLETE** | marker written, unit exits 0 |
| 10-15 ~04:31 | **Power cut № 2**; Pi reboots | unit re-ran pass 1 + verify at boot: **8 seconds, 0 of 5,238 items to transfer** |
| 10-15 09:35 | Operator reconciliation (§7) | — |

### 6.2 Headline statistics

| Metric | Value |
|---|---|
| Payload | 184,118,306,608 B · 4,595 files |
| Wall clock (supervised start → verified) | 2026-10-11 23:18 → 10-14 21:30 ≈ **70.2 h** |
| Mean effective throughput | ~0.73 MB/s |
| Peak sustained (pre-outage) | 1.8–1.9 MB/s |
| Post-outage floor | ~140–190 kB/s |
| Restart events | 1 network outage + 2 power cuts, all recovered automatically |
| Data lost to any crash | 0 B |
| Verification passes on full payload | 3 (completion, post-power-cut № 2, final reconciliation) |

### 6.3 The slow middle — a diagnosis in four measurements

At 19:48 on 12 October, ~40 minutes after the site's power came back, the transfer
was crawling at 190 kB/s with the log's ETA reading 200+ hours. Rather than blame
the relay and move on, I isolated the fault in four measurements, each of which
eliminated one suspect:

1. **The far side was innocent.** pinet-alpha had *not* rebooted (`up 8:22`) —
   the power cut was local — and its own `tailscale netcheck` showed the Nairobi
   DERP at **41 ms** and a clean IPv4 line. A relay reached in 41 ms by one peer
   is not a congested relay.
2. **The near relay leg was the symptom.** From the source site the same DERP
   measured **489–539 ms** (vs ~100 ms pre-outage). Both peers are in East Africa;
   500 ms to a relay the far side touches at 41 ms indicts the path between us
   and it.
3. **The Wi-Fi link was perfect.** `iw dev wlan0 station dump`: **−35 dBm**
   (strong), **72.2 Mbit/s** both directions, **tx failed: 0**. The last mile of
   the LAN was ruled out; `eth0` remains down (no cable), so Wi-Fi is the only LAN
   path.
4. **The raw internet was the fault.** `ping 1.1.1.1`: **60 % packet loss**
   (39 ms when a packet survived); `ping 8.8.8.8`: 0 % loss but 86 ms. A short
   path with heavy loss is a **degraded ISP uplink**, not a Wi-Fi or relay problem
   — the classic signature of a WAN link retrained at a bad profile after a
   mains event.

Conclusion: the local ISP's link, not any part of my stack, throttled the middle
third of the campaign. A router power-cycle would likely have restored 1.8 MB/s;
none was performed, and the transfer ground through at ~190 kB/s instead. **The
contingency design's payoff was precisely this: the campaign's completion did not
depend on the network being good, only on it existing.**

## 7. Completion and reconciliation

The verify pass closed the campaign at **21:30 on 14 October** — pass 1 exit 0,
verify pass exit 0, marker `~/radioish-transfer-complete` written. Power cut № 2
at ~04:31 on 15 October then gave the stack a free end-to-end test: on boot the
unit re-ran both passes over all 5,238 items (files + directories) in **eight
seconds, zero transfers** — an independent machine-verified "nothing missing"
claim.

My final reconciliation compared the sides by name and byte:

| Check | Source (SSD) | Destination (pinet-alpha) |
|---|---|---|
| Files (`find -type f`) | 4,595 | 4,596 (before cleanup) |
| Apparent bytes (`du -sb`) | 184,118,306,608 | 187,193,255,728 (before cleanup) |
| Files present on dest but not source | — | 1: `Dikier/epk/audio/.2026-09-10 14-20-14.wav.NaErpD` |

The single discrepancy was an **orphaned rsync temp file** — 3,074,949,120 B, the
in-progress write of the very file being transferred when I SIGTERM'd the original
nohup run on night one. Its true name (`Dikier/epk/audio/2026-09-10 14-20-14.wav`)
was present and complete; only the corpse of its temp twin remained. Deleted, after
which both sides measured **exactly 184,118,306,608 B / 4,595 files**.

**Verification ledger:** rsync's own size+mtime check over every item, three times;
name-level diff of both trees; byte-level `du -sb` equality. No checksum pass was
run — deliberate: over a 190 kB/s–1.8 MB/s relay, a full `--checksum` re-read of
184 GB costs more than the campaign itself, and the completed file's transfer
integrity is already guaranteed by SSH's transport MACs. The residual risk
`--checksum` would cover (silent same-size disk rot) is a snapshot-backup problem,
not a copy problem.

Post-campaign: the unit is disabled (`systemctl --user disable --now` — future
boots shouldn't re-scan 5,238 items for nothing; re-enable with one command if the
catalogue is ever updated and re-mirrored). The SSD automount and linger remain —
they are site infrastructure now, not campaign scaffolding.

## 8. The cargo — all fifteen artists, accounted for

The catalogue that made the crossing is the house itself. Measured from the source
on 15 October (apparent bytes, per-folder `du -sb` + `find | wc -l`); the identical
numbers hold on the mirror, because the whole tree reconciled byte-for-byte (§7).

| # | Artist | Style / role | Files | Bytes | GB |
|---|--------|--------------|-------|-----------|-------|
| 1 | Habib | Deep house & melodic techno · 8 originals + DJ set | 82 | 2,695,918,523 | 2.70 |
| 2 | Maya | Experimental ambient electronica | 38 | 2,995,127,455 | 3.00 |
| 3 | Parisa | 2004-era nostalgic electronic | 94 | 726,566,587 | 0.73 |
| 4 | SDKZ | AfroHouse / AfroBeats / Deep House | 113 | 16,917,334,596 | 16.92 |
| 5 | Dikier | Extended live techno sessions | 46 | 7,163,530,073 | 7.16 |
| 6 | Bernie | Vinyl Classics / Deep House · producer & co-founder · Ableton live sessions | 52 | 15,210,835,047 | 15.21 |
| 7 | Schrödinger's Breakfast | Garage / Bass / Electro — this paper's home folder | 32 | 4,457,867,506 | 4.46 |
| 8 | El Djemba | Ableton-recorded DJ set | 38 | 8,502,549,755 | 8.50 |
| 9 | Alexander Zwo | Ableton-recorded DJ set · pristine 24-bit captures | 38 | 4,917,151,450 | 4.92 |
| 10 | DJ Unknown | Ableton-recorded DJ set · continuous two-part live session | 68 | 9,057,666,332 | 9.06 |
| 11 | Mundz | Genre tag pending | 37 | 4,746,363,384 | 4.75 |
| 12 | Yogo | Season One · new artist · genre tag pending | 31 | 4,786,348,410 | 4.79 |
| 13 | **Canthus** | Operator-confirmed artist · full EPK stack (audio/mix/processing/promo/text/video) · roster index pending | 19 | 6,862,319,068 | 6.86 |
| 14 | **DNZ** | Operator-confirmed artist · full EPK stack (audio/mix/video) · roster index pending | 22 | 6,395,514,561 | 6.40 |
| 15 | **Kesh-Zion** | Operator-confirmed artist · full EPK stack (audio/mix/video) · roster index pending | 28 | 6,249,209,289 | 6.25 |

**Fifteen-artist subtotal: 738 files · 101,684,302,036 B (55.2 % of the payload).**
The three roster-pending artists alone carry 19,507,042,918 B — a tenth of the
migration would have been invisible if I had trusted the twelve-artist index
instead of counting the tree.

The rest of the cargo — label-wide assets, every byte of which also crossed and
verified:

| Asset | Contents | Bytes | GB |
|---|---|-----------|-------|
| `radio-ish 2 Project` | Label production project | 34,260,904,221 | 34.26 |
| `Archive/` | Superseded pre-standardisation masters | 24,285,061,724 | 24.29 |
| `Season One/` | Season One artist sessions | 12,768,043,476 | 12.77 |
| `Social_Media/` | Social deliverables | 11,069,796,081 | 11.07 |
| `EPK_Project/` | EPK working project | 23,351,499 | 0.02 |
| `qc/` + `QC_Reports/` | QC evidence (96/96 checks passed) | 264,174 | — |
| `tools/` | House tooling (`standardise_masters.py` et al.) | 177,874 | — |
| House docs | `MASTER_README.md`, `EPK_Audio_Workflow.md`, `BRAND_GUIDELINES.md`, `epk_lab_promotion.md`, `create_lab_mix.sh`, `Advertising/` | ~43 KB | — |

Reconciliation: the named assets above sum to ~184,091.8 MB against the verified
whole-tree total of 184,118,306,608 B; the ~26.5 MB residual is unitemised macOS
metadata (`._*` AppleDouble files, `.DS_Store`) plus directory entries —
transferred and covered by the whole-tree byte equality, just not worth a manifest
row.

## 9. Discussion — what I'd carry into the next migration

- **The tool named in the brief did not exist.** "Use Raspberry Pi Connect" was a
  reasonable guess by the operator, and wrong; the actual stack (Tailscale +
  SSH + rsync) was assembled from what the machines already had. Rule: survey the
  tool *before* planning around it.
- **Hard NAT is a throughput ceiling, not an obstacle.** With
  `MappingVariesByDestIP: true` and no IPv6, direct paths never established; the
  campaign lived on DERP and its ~1.8 MB/s was excellent *for a relay*. Anyone
  expecting LAN speed over a relay will mis-plan; measure first, then commit.
- **Crash-tolerance is four small systems, not one big one**: supervision
  (restart forever), boot-time autonomy (linger + automount), resumability
  (`--partial` + delta), and self-proof (verification pass + marker). Each one
  alone failed to cover a case the others caught.
- **Wait-loops are where bugs hide.** §5.1 — my only shipped defect became a
  silent hang because the loop was unbounded and mute. Bounds and complaints.
- **Diagnose the slow, don't endure it.** §6.3's four-measurement ladder (far
  peer → relay legs → LAN link → raw WAN) pinned a 10× degradation on the ISP in
  minutes, from one keyboard, with zero disruption to the running transfer.
- **Cost of the middle third:** at pre-outage speed the campaign closes in
  ~30 h; the degraded link stretched it to 70 h. The delta (~40 h) is the price
  of not power-cycling one router. Sometimes leaving it running *is* the right
  call — an unattended 190 kB/s beats an attended maybe-faster.
- **Count the tree, not the index.** The paper you are reading originally said
  "twelve artists" because that is what `MASTER_README.md` claims. The tree
  carries fifteen. Catalogues drift from their indexes; the filesystem is the
  ledger of record. §8 exists because the operator caught me trusting the
  index over the evidence.

## 10. Conclusion

A four-word request ("get the Radio-ish folder") became a 70-hour, 184-GB
migration across a relayed overlay network, surviving one transport outage and
two power cuts with zero data loss and no operator intervention, ending in an
exact byte-for-byte reconciliation — 184,118,306,608 bytes and 4,595 files on
both sides. The catalogue now lives twice: on the Extreme SSD at the source site
and on pinet-alpha's NVMe. **All fifteen artists — Habib, Maya, Parisa, SDKZ,
Dikier, Bernie, Schrödinger's Breakfast, El Djemba, Alexander Zwo, DJ Unknown,
Mundz, Yogo, Canthus, DNZ and Kesh-Zion — arrived intact**, EPK stacks, mixes,
QC evidence and all. Schrödinger's Breakfast's own EPK stack rode along with
everything else; this paper is the proof of transport, filed where the work is
kept.

---

## Appendix A — the wrapper script (verbatim)

```bash
#!/bin/bash
SRC="/media/minima/Extreme SSD/Radio-ish"
DEST="pinet-alpha:"
HOST="pinet-alpha"          # ← the bugfix of §5.1: no trailing colon for ssh
LOG="/home/minima/rsync-radioish.log"

while [ ! -d "$SRC" ]; do sleep 10; done
until ssh -o BatchMode=yes -o ConnectTimeout=10 "$HOST" true 2>/dev/null; do sleep 15; done

echo "=== rsync pass 1 start $(date) ===" >> "$LOG"
rsync -rt --partial --timeout=180 --info=progress2 "$SRC" "$DEST" >> "$LOG" 2>&1
rc=$?; [ $rc -eq 24 ] && rc=0

echo "=== rsync verify pass start $(date) (rc1=$rc) ===" >> "$LOG"
rsync -rt --partial --timeout=180 --info=progress2 "$SRC" "$DEST" >> "$LOG" 2>&1
rc2=$?; [ $rc2 -eq 24 ] && rc2=0

if [ $rc -eq 0 ] && [ $rc2 -eq 0 ]; then
  echo "=== VERIFIED COMPLETE $(date) ===" >> "$LOG"
  touch /home/minima/radioish-transfer-complete
  exit 0
fi
echo "=== failed (rc1=$rc rc2=$rc2), systemd will retry in 30s $(date) ===" >> "$LOG"
exit 1
```

## Appendix B — supervision and mount configuration

```ini
# ~/.config/systemd/user/rsync-radioish.service
[Unit]
Description=Rsync Radio-ish SSD folder to pinet-alpha (powercut-safe, auto-resume)
StartLimitIntervalSec=0

[Service]
ExecStart=/home/minima/.local/bin/sync-radioish.sh
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
```

```fstab
# /etc/fstab — appended 2026-10-11 (backup: /etc/fstab.bak-radioish)
UUID=7ADC-CA53  /media/minima/Extreme\040SSD  exfat  defaults,nofail,x-systemd.automount,uid=1000,gid=1000,fmask=0022,dmask=0022  0  0
```

## Appendix C — key evidence lines (from ~/rsync-radioish.log and shell history)

```
23:16:48  unit first started (sat in wait-loop — §5.1 bug)
23:18:30  === rsync pass 1 start ===            (supervised run, after fix)
01:43:12  === verify pass (rc1=255) ===           network outage, both passes
01:45:26  === failed … systemd will retry in 30s ===
01:52:39  === rsync pass 1 start ===              resumed mid-file after outage
~19:08    power cut № 1 (site) — Pi reboots; 17.4 GB skipped on resume
19:48     measured 194 kB/s; DERP 489 ms local / 41 ms remote; WAN loss 60 %
10-14 21:30:04  === VERIFIED COMPLETE ===
10-15 04:31:17→04:31:25  power cut № 2; re-verify: 0 transfers / 5,238 items
10-15 09:41  orphan temp file removed; both sides 184,118,306,608 B / 4,595 files
```

*— end of lab session № 1*
