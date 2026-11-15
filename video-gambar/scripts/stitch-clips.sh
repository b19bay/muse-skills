#!/usr/bin/env bash
# Gabungkan klip-klip video menjadi satu berkas dengan ffmpeg (concat demuxer).
# Pakai: stitch-clips.sh <output.mp4> <clip1.mp4> <clip2.mp4> [...]
# Semua klip harus punya codec, resolusi, dan fps yang sama. Klip hasil
# media.generate_video umumnya sudah seragam bila dibuat dari satu proyek.
# Skrip mencetak durasi total hasil gabungan (detik) ke stdout.
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Pakai: $0 <output.mp4> <clip1.mp4> <clip2.mp4> [...]" >&2
  exit 1
fi

out="$1"; shift
list="$(mktemp)"
trap 'rm -f "$list"' EXIT

for f in "$@"; do
  [ -f "$f" ] || { echo "Klip tidak ditemukan: $f" >&2; exit 1; }
  printf "file '%s'\n" "$(realpath "$f")" >> "$list"
done

ffmpeg -y -v error -f concat -safe 0 -i "$list" -c copy "$out"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"
