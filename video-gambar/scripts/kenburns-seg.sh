#!/usr/bin/env bash
# Satu segmen video Ken Burns dari satu gambar diam.
# Pakai: kenburns-seg.sh <gambar> <fg_lebar> <fg_tinggi> <ox> <oy> <zoom> <headline> <sub> <durasi_detik> <output.mp4>
# Contoh zoom 5 detik: "1+0.08*on/150" (masuk) atau "1.10-0.08*on/150" (keluar).
# Pembagi di dalam rumus zoom harus sama dengan durasi x 30.
# Teks headline dan sub tidak boleh mengandung koma, titik dua, atau kutip satu.
# Teruji 15 Nov 2026 pada proyek defence-steal-war (3 segmen 5 detik).
set -euo pipefail
[ "$#" -eq 10 ] || { echo "Pakai: $0 <gambar> <fg_lebar> <fg_tinggi> <ox> <oy> <zoom> <headline> <sub> <durasi> <output>" >&2; exit 1; }
IMG="$1"; FW="$2"; FH="$3"; OX="$4"; OY="$5"; ZOOM="$6"; HEAD="$7"; SUB="$8"; DUR="$9"; OUT="${10}"
FRAMES=$(( DUR * 30 ))
FONT=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf
[ -f "$FONT" ] || FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
FADE_OUT=$(awk "BEGIN{print $DUR - 0.25}")
ffmpeg -y -v error -loop 1 -i "$IMG" -filter_complex "
 [0:v]split[a][b];
 [a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42,eq=brightness=-0.08[bg];
 [b]scale=$FW:$FH[fg];
 [bg][fg]overlay=$OX:$OY,zoompan=z='$ZOOM':d=$FRAMES:s=1080x1920:fps=30,
 drawtext=fontfile=$FONT:text='$HEAD':fontcolor=white:fontsize=72:borderw=5:bordercolor=black@0.55:x=(w-text_w)/2:y=h*0.06,
 drawtext=fontfile=$FONT:text='$SUB':fontcolor=0xFFD94D:fontsize=44:borderw=4:bordercolor=black@0.55:x=(w-text_w)/2:y=h*0.115,
 fade=t=in:st=0:d=0.25,fade=t=out:st=$FADE_OUT:d=0.25,format=yuv420p[v]" \
 -map "[v]" -t "$DUR" -c:v libx264 -preset medium -crf 19 -r 30 "$OUT"
