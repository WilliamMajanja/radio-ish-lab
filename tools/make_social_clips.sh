#!/bin/bash
# make_social_clips.sh — Radio-ish Lab · Season One social clip set.
#
# Builds the platform matrix in SOCIAL_PLAYBOOK.md from REAL sources for every
# artist that does not already have a shipped set (Yogo + DJ Unknown are done).
#
#   video  : cropped/scaled from each artist's live performance .mov
#            (Parisa's source is corrupt, so it falls back to a still cover/banner)
#   audio  : the artist's OWN mastered *_mix_epk.mp3 — never the raw camera mic,
#            so every clip passes the "never post raw" sound gate in §7
#
# Usage: tools/make_social_clips.sh [Artist ...]     # default: all pending artists
set -u
R="$HOME/Radio-ish"
FF=ffmpeg
FP=ffprobe
S="$R/Social_Media/promo"
DATE="${DATE:-2026-10-15}"

# platform|ratio|duration
PLATFORMS=(
  "tiktok|9:16|30"
  "shorts|9:16|30"
  "snap|9:16|30"
  "reels|9:16|45"
  "x|16:9|60"
  "fb|16:9|60"
)

# artist|slug|video source (relative) or FALLBACK|start offset seconds
ROWS=(
  "SDKZ|sdkz|SDKZ/epk/video/2026-09-03 16-10-55.mov|1200"
  "Bernie|bernie|Bernie/epk/video/2026-09-07 14-50-28.mov|1200"
  "Dikier|dikier|Dikier/epk/video/2026-09-10 14-20-42.mov|1200"
  "Habib|habib|Habib/epk/video/2026-08-31 13-23-56.mov|60"
  "Maya|maya|Maya/epk/video/2026-09-05 15-01-00.mov|1200"
  "Mundz|mundz|Mundz/epk/video/mundz_set_p1.mov|600"
  "El Djemba|el_djemba|El Djemba/epk/video/2026-09-14 13-57-24.mov|1200"
  "Alexander Zwo|alexander_zwo|Alexander Zwo/epk/video/2026-09-14 16-53-40.mov|1200"
  "Parisa|parisa|FALLBACK|900"
  "Schrödinger’s Breakfast|schrodingers_breakfast|Schrödinger’s Breakfast/epk/video/2026-09-21 13-34-28.mov|1200"
)

FILTER=("$@")

for ROW in "${ROWS[@]}"; do
  IFS='|' read -r NAME SLUG SRC START <<< "$ROW"
  if [ ${#FILTER[@]} -gt 0 ]; then
    hit=0; for F in "${FILTER[@]}"; do [ "$F" = "$NAME" ] && hit=1; done
    [ $hit -eq 1 ] || continue
  fi
  OUTDIR="$S/$NAME"
  AUDIO="$R/$NAME/epk/mix/${SLUG}_mix_epk.mp3"
  mkdir -p "$OUTDIR"
  [ -s "$AUDIO" ] || { echo "  [err] $NAME — no mix_epk mp3"; continue; }

  for P in "${PLATFORMS[@]}"; do
    IFS='|' read -r PLAT RATIO DUR <<< "$P"
    OUT="$OUTDIR/${SLUG}_${DATE}_${PLAT}.mp4"
    if [ "$RATIO" = "9:16" ]; then
      WF="crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,fps=30"
      STILL="$OUTDIR/cover_1080x1920.png"
    else
      WF="scale=1920:1080:flags=lanczos,fps=30"
      STILL="$OUTDIR/banner_1920x1080.png"
    fi
    # two-pass loudness: land every clip on -14 LUFS / -1.0 dBTP so clips cut
    # from quiet passages are not inaudible next to clips cut from loud ones
    AF="$(python3 "$R/tools/loudnorm_filter.py" "$FF" "$AUDIO" "$START" "$DUR")"
    [ -n "$AF" ] || AF="alimiter=level=false:limit=0.9"

    if [ "$SRC" = "FALLBACK" ]; then
      [ -s "$STILL" ] || { echo "  [skip] $NAME $PLAT — no still $STILL"; continue; }
      "$FF" -y -hide_banner -loglevel error -loop 1 -i "$STILL" \
        -ss "$START" -t "$DUR" -i "$AUDIO" \
        -map 0:v:0 -map 1:a:0 \
        -vf "$WF" -c:v libx264 -preset ultrafast -crf 21 -pix_fmt yuv420p -r 30 \
        -af "$AF" -c:a aac -b:a 192k -ar 48000 -ac 2 -t "$DUR" -movflags +faststart "$OUT"
    else
      "$FF" -y -hide_banner -loglevel error -ss "$START" -t "$DUR" -i "$R/$SRC" \
        -ss "$START" -t "$DUR" -i "$AUDIO" \
        -map 0:v:0 -map 1:a:0 \
        -vf "$WF" -c:v libx264 -preset ultrafast -crf 21 -pix_fmt yuv420p -r 30 \
        -af "$AF" -c:a aac -b:a 192k -ar 48000 -ac 2 -t "$DUR" -movflags +faststart "$OUT"
    fi

    if [ -s "$OUT" ]; then
      D=$("$FP" -v error -show_entries format=duration -of csv=p=0 "$OUT")
      V=$("$FP" -v error -select_streams v:0 -show_entries stream=width,height,codec_name -of csv=p=0 "$OUT")
      echo "  [ok] $NAME $PLAT  $(stat -c%s "$OUT") B  ${D}s  $V"
    else
      echo "  [err] $NAME $PLAT — render failed"
    fi
  done
done
