#!/usr/bin/env bash
# sheets.sh <video> <out_dir> [fps=1] [cols=8]
# Contact sheets with burned-in timestamps, an audio waveform and a probe summary.
set -euo pipefail
VID="${1:?video path}"; OUT="${2:?output dir}"; FPS="${3:-1}"; COLS="${4:-8}"; ROWS=6
mkdir -p "$OUT"
FONT=""
for f in /System/Library/Fonts/Supplemental/Arial.ttf /System/Library/Fonts/Helvetica.ttc /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf; do
  [ -f "$f" ] && FONT="fontfile=$f:" && break
done
STAMP=""
if ffmpeg -hide_banner -filters 2>/dev/null | grep -q ' drawtext '; then
  STAMP=",drawtext=${FONT}text='%{pts\\:hms}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6"
else
  echo "note: ffmpeg has no drawtext; no timestamps burned in. Tile n (from 0, left-to-right, top-to-bottom) on sheet k = second ((k-1)*$((COLS*ROWS)) + n)/${FPS}."
fi
ffmpeg -v error -y -i "$VID" -vf "fps=${FPS},scale=320:-2${STAMP},tile=${COLS}x${ROWS}:padding=4:color=gray" "$OUT/sheet_%02d.png"
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VID" | grep -q .; then
  ffmpeg -v error -y -i "$VID" -filter_complex "showwavespic=s=2400x300:split_channels=0:colors=0x3D6B59" -frames:v 1 "$OUT/audio_wave.png"
fi
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size -of default=nw=1 "$VID" > "$OUT/probe.txt"
echo "sheets: $(ls "$OUT"/sheet_*.png | wc -l | tr -d ' ') ($((COLS*ROWS)) tiles each, ${FPS} fps) -> $OUT"
cat "$OUT/probe.txt"
