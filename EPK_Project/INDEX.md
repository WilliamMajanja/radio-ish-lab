# EPK_Project — INDEX (refreshed 2026-10-15)

All 10 artists represented in EPK_Project have a canonical hq master, genre,
and 30-second promo segment. Segments are 48 kHz / 320 kbps; loudness figures
below are measured from the segment files actually on disk (EBU R128).

## Artist map

| artist | genre | hq master (epk/mix/) | 30s promo segment | I (LUFS) |
|---|---|---|---|---|
| Habib | Deep House | habib_mix_hq.mp3 | Habib/habib_30s.mp3 | **−14.0** |
| Maya | Ambient | maya_mix_hq.mp3 | Maya/maya_30s.mp3 | **−14.3** |
| Parisa | House | parisa_mix_hq.mp3 | Parisa/parisa_30s.mp3 | −14.0 |
| SDKZ | Techno | sdkz_mix_hq.mp3 | SDKZ/sdkz_30s.mp3 | −14.9 |
| Dikier | Techno | dikier_mix_hq.mp3 | Dikier/dikier_30s.mp3 | −14.5 |
| Bernie | Techno | bernie_mix_hq.mp3 | Bernie/bernie_30s.mp3 | −14.3 |
| El Djemba | House/Techno | el_djemba_mix_hq.mp3 | `El Djemba/el djemba_30s.mp3` | −14.1 |
| Alexander Zwo | House/Techno | alexander_zwo_mix_hq.mp3 | `Alexander Zwo/alexander zwo_30s.mp3` | −14.2 |
| DJ Unknown | House/Techno | dj_unknown_mix_hq.mp3 | DJ Unknown/dj_unknown_30s.mp3 | −14.6 |
| Mundz | Live/Deep-Tech | mundz_mix_hq.mp3 | Mundz/mundz_30s.mp3 | −13.9 |

## Pipeline notes

- Canon is the `_mix_hq.mp3` 48 kHz/320 kbps master. Segments are cut from canon
  at a representative in-set offset with
  `loudnorm=I=-14:TP=-1.5:LRA=11`, 48 kHz, 320 kbps.
- Old root-level legacy segs (`maya_30s.mp3`, `parisa_45s.mp3`) remain for
  backwards compat but the per-artist dirs are authoritative now.

## Completion status

- All listed artists have a 30-second promo segment; the Bernie segment uses
  the canonical `bernie_30s.mp3` spelling. El Djemba and Alexander Zwo retain
  spaces in their existing segment filenames, as shown above.
- The stale Maya promo measured −43.8 LUFS. It has been re-cut at 120 s from
  the current `maya_mix_hq.mp3` and now measures −14.3 LUFS.

## 2026-09-14 loudness-refresh history

Two quiet ambient/deep-house canonicals were lifted to broadcast headroom and
re-verified (real ebur128, both co-located in each artist's `epk/mix/`):

| artist | remastered master | I (LUFS) | LRA (LU) |
|---|---|---|---|
| Habib | `habib_mix_remaster.mp3` | **−12.3** | 5.5 |
| Maya | `maya_mix_remaster.mp3` | **−13.3** | 5.9 |

The Maya promo has since been re-cut from the current house-standardized
`maya_mix_hq.mp3` master. Master chain, loudness method, and SHA256SUMS for the
current deliverables are documented alongside their respective QC reports.
