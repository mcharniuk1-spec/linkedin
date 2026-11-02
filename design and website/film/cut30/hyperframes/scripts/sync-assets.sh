#!/bin/bash
# Copies the brand assets this film uses from the repository's asset tree (no binaries are stored in this folder), vendors GSAP from node_modules,
# and synthesises the audio stems. Run from the hyperframes folder after `npm ci --ignore-scripts`.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
A="$HERE/../../../assets/public/assets/identity"
mkdir -p "$HERE/assets/fonts" "$HERE/assets/heroes" "$HERE/assets/portraits" "$HERE/assets/brand" "$HERE/assets/audio"
cp "$A/font-source/fraunces/fraunces-latin-full-normal.woff2" "$HERE/assets/fonts/fraunces.woff2"
cp "$A/font-source/mona-sans/mona-sans-latin-wght-normal.woff2" "$HERE/assets/fonts/mona-sans.woff2"
cp "$A/font-source/geist-mono/geist-mono-latin-wght-normal.woff2" "$HERE/assets/fonts/geist-mono.woff2"
cp "$A"/v10/heroes/*.webp "$HERE/assets/heroes/"
for n in 01 02 03 04 06 09; do cp "$A/../library-r12/portraits/portrait-$n.webp" "$HERE/assets/portraits/"; done
cp "$A"/v10/mark-b01.svg "$A"/v10/mark-b01-inverse.svg "$A"/v10/lockup-b01.svg "$A"/v10/lockup-b01-inverse.svg "$A"/v10/icons-d05.svg "$HERE/assets/brand/"
cp "$HERE/node_modules/gsap/dist/gsap.min.js" "$HERE/assets/gsap.min.js"
if command -v say >/dev/null 2>&1; then python3 -I "$HERE/scripts/make_audio.py"; else python3 -I "$HERE/scripts/make_audio.py" --no-guide; fi
echo "assets synced"
