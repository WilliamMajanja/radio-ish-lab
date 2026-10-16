# Season One — EPK QC report

**Generated:** 2026-10-15  

**Scope:** 15 artists · 150/150 checks passed

**Toolchain:** `/usr/bin/ffmpeg` / `/usr/bin/ffprobe` (measured this run)


> This report supersedes the earlier version, which described 16-bit loops and
> pre-fix EPK renders. All figures below were measured on the current files.


## Loudness standard

`MASTER_README.md` gates release audio at **-12..-16 LUFS** and **true peak <= ~0 dBFS**.
Loops are mastered to **-14 LUFS / -1.0 dBTP**. EPK videos carry small extra
attenuation because AAC and MP3 encoding add inter-sample overshoot.


## Per-artist results

| Artist | Loop | LUFS | TP | Video | LUFS | TP | Cover |
|---|---|---|---|---|---|---|---|
| SDKZ | 8,640,158 B 24-bit | -14.00 | -6.34 | 1,802,365 B | -14.02 | -5.50 | cover_1080x1920_bw.png |
| Yogo | 8,640,102 B 24-bit | -14.01 | -7.29 | 1,379,658 B | -14.06 | -5.82 | cover_1080x1920_bw.png |
| Bernie | 8,640,102 B 24-bit | -14.02 | -1.00 | 1,717,872 B | -14.74 | -1.38 | cover_1080x1920_bw.png |
| Mundz | 8,640,102 B 24-bit | -14.00 | -4.58 | 1,799,855 B | -14.05 | -4.66 | cover_1080x1920_bw.png |
| Maya | 8,640,342 B 24-bit | -14.00 | -6.00 | 1,832,283 B | -14.03 | -5.30 | cover_1080x1920_bw.png |
| Dikier | 8,640,102 B 24-bit | -14.00 | -2.69 | 1,818,788 B | -14.02 | -2.80 | cover_1080x1920_bw.png |
| DJ Unknown | 8,640,102 B 24-bit | -14.00 | -3.69 | 1,793,294 B | -14.02 | -2.91 | cover_1080x1920_bw.png |
| Alexander Zwo | 8,640,102 B 24-bit | -14.00 | -8.92 | 1,778,830 B | -14.08 | -5.18 | cover_1080x1920_bw.png |
| Habib | 8,640,218 B 24-bit | -14.00 | -6.68 | 1,736,563 B | -14.04 | -3.95 | cover_1080x1920_bw.png |
| Parisa | 8,640,102 B 24-bit | -13.99 | -3.47 | 1,771,443 B | -14.00 | -3.44 | cover_1080x1920_bw.png |
| El Djemba | 8,640,102 B 24-bit | -14.00 | -1.15 | 1,790,586 B | -14.06 | -1.25 | cover_1080x1920_bw.png |
| Schrödinger’s Breakfast | 8,640,102 B 24-bit | -14.00 | -6.64 | 1,311,704 B | -14.13 | -6.07 | cover_1080x1920_bw.png |
| DNZ | 8,640,102 B 24-bit | -14.00 | -5.12 | 1,196,055 B | -14.03 | -4.08 | DNZ_titlecard_1080x1920.png |
| Kesh-Zion | 8,640,102 B 24-bit | -14.00 | -1.99 | 1,253,152 B | -14.04 | -1.35 | KESH_ZION_titlecard_1080x1920.png |
| Canthus | 8,640,102 B 24-bit | -14.15 | -0.99 | 1,225,799 B | -14.19 | -0.92 | CANTHUS_titlecard_1080x1920.png |

## Checks

- [x] SDKZ: loop 48 kHz stereo
- [x] SDKZ: loop 30.000000 s exactly
- [x] SDKZ: loop LUFS in -12..-16
- [x] SDKZ: loop true peak <= -1.0 dBTP
- [x] SDKZ: loop 24-bit (8.64 MB)
- [x] SDKZ: cover 1080x1920 PNG
- [x] SDKZ: video 1080x1920 h264
- [x] SDKZ: video 30.000 s
- [x] SDKZ: video audio 48 kHz stereo aac
- [x] SDKZ: fine print present
- [x] YOGO: loop 48 kHz stereo
- [x] YOGO: loop 30.000000 s exactly
- [x] YOGO: loop LUFS in -12..-16
- [x] YOGO: loop true peak <= -1.0 dBTP
- [x] YOGO: loop 24-bit (8.64 MB)
- [x] YOGO: cover 1080x1920 PNG
- [x] YOGO: video 1080x1920 h264
- [x] YOGO: video 30.000 s
- [x] YOGO: video audio 48 kHz stereo aac
- [x] YOGO: fine print present
- [x] BERNIE: loop 48 kHz stereo
- [x] BERNIE: loop 30.000000 s exactly
- [x] BERNIE: loop LUFS in -12..-16
- [x] BERNIE: loop true peak <= -1.0 dBTP
- [x] BERNIE: loop 24-bit (8.64 MB)
- [x] BERNIE: cover 1080x1920 PNG
- [x] BERNIE: video 1080x1920 h264
- [x] BERNIE: video 30.000 s
- [x] BERNIE: video audio 48 kHz stereo aac
- [x] BERNIE: fine print present
- [x] MUNDZ: loop 48 kHz stereo
- [x] MUNDZ: loop 30.000000 s exactly
- [x] MUNDZ: loop LUFS in -12..-16
- [x] MUNDZ: loop true peak <= -1.0 dBTP
- [x] MUNDZ: loop 24-bit (8.64 MB)
- [x] MUNDZ: cover 1080x1920 PNG
- [x] MUNDZ: video 1080x1920 h264
- [x] MUNDZ: video 30.000 s
- [x] MUNDZ: video audio 48 kHz stereo aac
- [x] MUNDZ: fine print present
- [x] MAYA: loop 48 kHz stereo
- [x] MAYA: loop 30.000000 s exactly
- [x] MAYA: loop LUFS in -12..-16
- [x] MAYA: loop true peak <= -1.0 dBTP
- [x] MAYA: loop 24-bit (8.64 MB)
- [x] MAYA: cover 1080x1920 PNG
- [x] MAYA: video 1080x1920 h264
- [x] MAYA: video 30.000 s
- [x] MAYA: video audio 48 kHz stereo aac
- [x] MAYA: fine print present
- [x] DIKIER: loop 48 kHz stereo
- [x] DIKIER: loop 30.000000 s exactly
- [x] DIKIER: loop LUFS in -12..-16
- [x] DIKIER: loop true peak <= -1.0 dBTP
- [x] DIKIER: loop 24-bit (8.64 MB)
- [x] DIKIER: cover 1080x1920 PNG
- [x] DIKIER: video 1080x1920 h264
- [x] DIKIER: video 30.000 s
- [x] DIKIER: video audio 48 kHz stereo aac
- [x] DIKIER: fine print present
- [x] DJ_UNKNOWN: loop 48 kHz stereo
- [x] DJ_UNKNOWN: loop 30.000000 s exactly
- [x] DJ_UNKNOWN: loop LUFS in -12..-16
- [x] DJ_UNKNOWN: loop true peak <= -1.0 dBTP
- [x] DJ_UNKNOWN: loop 24-bit (8.64 MB)
- [x] DJ_UNKNOWN: cover 1080x1920 PNG
- [x] DJ_UNKNOWN: video 1080x1920 h264
- [x] DJ_UNKNOWN: video 30.000 s
- [x] DJ_UNKNOWN: video audio 48 kHz stereo aac
- [x] DJ_UNKNOWN: fine print present
- [x] ALEXANDER_ZWO: loop 48 kHz stereo
- [x] ALEXANDER_ZWO: loop 30.000000 s exactly
- [x] ALEXANDER_ZWO: loop LUFS in -12..-16
- [x] ALEXANDER_ZWO: loop true peak <= -1.0 dBTP
- [x] ALEXANDER_ZWO: loop 24-bit (8.64 MB)
- [x] ALEXANDER_ZWO: cover 1080x1920 PNG
- [x] ALEXANDER_ZWO: video 1080x1920 h264
- [x] ALEXANDER_ZWO: video 30.000 s
- [x] ALEXANDER_ZWO: video audio 48 kHz stereo aac
- [x] ALEXANDER_ZWO: fine print present
- [x] HABIB: loop 48 kHz stereo
- [x] HABIB: loop 30.000000 s exactly
- [x] HABIB: loop LUFS in -12..-16
- [x] HABIB: loop true peak <= -1.0 dBTP
- [x] HABIB: loop 24-bit (8.64 MB)
- [x] HABIB: cover 1080x1920 PNG
- [x] HABIB: video 1080x1920 h264
- [x] HABIB: video 30.000 s
- [x] HABIB: video audio 48 kHz stereo aac
- [x] HABIB: fine print present
- [x] PARISA: loop 48 kHz stereo
- [x] PARISA: loop 30.000000 s exactly
- [x] PARISA: loop LUFS in -12..-16
- [x] PARISA: loop true peak <= -1.0 dBTP
- [x] PARISA: loop 24-bit (8.64 MB)
- [x] PARISA: cover 1080x1920 PNG
- [x] PARISA: video 1080x1920 h264
- [x] PARISA: video 30.000 s
- [x] PARISA: video audio 48 kHz stereo aac
- [x] PARISA: fine print present
- [x] EL_DJEMBA: loop 48 kHz stereo
- [x] EL_DJEMBA: loop 30.000000 s exactly
- [x] EL_DJEMBA: loop LUFS in -12..-16
- [x] EL_DJEMBA: loop true peak <= -1.0 dBTP
- [x] EL_DJEMBA: loop 24-bit (8.64 MB)
- [x] EL_DJEMBA: cover 1080x1920 PNG
- [x] EL_DJEMBA: video 1080x1920 h264
- [x] EL_DJEMBA: video 30.000 s
- [x] EL_DJEMBA: video audio 48 kHz stereo aac
- [x] EL_DJEMBA: fine print present
- [x] SCHRODINGERS_BREAKFAST: loop 48 kHz stereo
- [x] SCHRODINGERS_BREAKFAST: loop 30.000000 s exactly
- [x] SCHRODINGERS_BREAKFAST: loop LUFS in -12..-16
- [x] SCHRODINGERS_BREAKFAST: loop true peak <= -1.0 dBTP
- [x] SCHRODINGERS_BREAKFAST: loop 24-bit (8.64 MB)
- [x] SCHRODINGERS_BREAKFAST: cover 1080x1920 PNG
- [x] SCHRODINGERS_BREAKFAST: video 1080x1920 h264
- [x] SCHRODINGERS_BREAKFAST: video 30.000 s
- [x] SCHRODINGERS_BREAKFAST: video audio 48 kHz stereo aac
- [x] SCHRODINGERS_BREAKFAST: fine print present
- [x] DNZ: loop 48 kHz stereo
- [x] DNZ: loop 30.000000 s exactly
- [x] DNZ: loop LUFS in -12..-16
- [x] DNZ: loop true peak <= -1.0 dBTP
- [x] DNZ: loop 24-bit (8.64 MB)
- [x] DNZ: cover 1080x1920 PNG
- [x] DNZ: video 1080x1920 h264
- [x] DNZ: video 30.000 s
- [x] DNZ: video audio 48 kHz stereo aac
- [x] DNZ: fine print present
- [x] KESH_ZION: loop 48 kHz stereo
- [x] KESH_ZION: loop 30.000000 s exactly
- [x] KESH_ZION: loop LUFS in -12..-16
- [x] KESH_ZION: loop true peak <= -1.0 dBTP
- [x] KESH_ZION: loop 24-bit (8.64 MB)
- [x] KESH_ZION: cover 1080x1920 PNG
- [x] KESH_ZION: video 1080x1920 h264
- [x] KESH_ZION: video 30.000 s
- [x] KESH_ZION: video audio 48 kHz stereo aac
- [x] KESH_ZION: fine print present
- [x] CANTHUS: loop 48 kHz stereo
- [x] CANTHUS: loop 30.000000 s exactly
- [x] CANTHUS: loop LUFS in -12..-16
- [x] CANTHUS: loop true peak <= -1.0 dBTP
- [x] CANTHUS: loop 24-bit (8.64 MB)
- [x] CANTHUS: cover 1080x1920 PNG
- [x] CANTHUS: video 1080x1920 h264
- [x] CANTHUS: video 30.000 s
- [x] CANTHUS: video audio 48 kHz stereo aac
- [x] CANTHUS: fine print present

**150/150 passed**


## Known gaps

- **Yogo + Mundz genres** are now assigned from the published masters (House / Techno,
  Live / Deep-Tech), not invented; fine print, press pages and EPK videos re-rendered to match.
- **Yogo cover** is now a Yogo-specific 1080x1920 house-standard cover (waveform drawn from
  its own 30 s loop); no longer a copy of the SDKZ cover.
- **Schrodinger's Breakfast** now has a house-standard cover_1080x1920_bw.png; the original
  typographic title card is kept in epk/promo/ as a reference.
- **Habib / Maya / Schrodinger's Breakfast** source masters are very quiet
  (loudest 30 s window -35.5 / -27.8 / -26.0 dBFS RMS), so normalising to -14 LUFS
  raises the noise floor. Objective noise-floor figures are in qc/SeasonOne_Mix_qc.md;
  an in-person ear check is still recommended before press.
