#!/usr/bin/env bash
# Scratch narration: the SAPI temp lines, lowered and shaped toward the brief's "low-register, close, dry" voice.
# Placeholder only. Replace 08_audio/vo/final/V01..V10.wav with the real take and rebuild with sound.py --vo final.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IN="$ROOT/08_audio/vo/temp"
OUT="$ROOT/08_audio/vo/scratch"
mkdir -p "$OUT"
for f in "$IN"/V*.wav; do
  n=$(basename "$f")
  ffmpeg -loglevel error -y -i "$f" -af "rubberband=pitch=0.86:formant=preserved:tempo=1.0,highpass=f=70,equalizer=f=180:t=q:w=1.0:g=3,equalizer=f=3200:t=q:w=1.2:g=-2,deesser=i=0.4,lowpass=f=9500,acompressor=threshold=-20dB:ratio=3:attack=8:release=120,aecho=0.8:0.4:18:0.12" -ar 48000 -ac 1 "$OUT/$n"
  echo "$n"
done
