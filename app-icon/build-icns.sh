#!/usr/bin/env bash
# 1024px PNG → macOS .icns (16~1024 전 사이즈 포함). 번들 직접 교체용 또는 보관용.
#   ./build-icns.sh hongsi-app-icon.png            # → hongsi-app-icon.icns
#   ./build-icns.sh variants/face-happy.png out.icns
set -euo pipefail
SRC="${1:?사용법: build-icns.sh <1024.png> [out.icns]}"
OUT="${2:-${SRC%.*}.icns}"
[ -f "$SRC" ] || { echo "❌ 소스 없음: $SRC"; exit 1; }
SET="$(mktemp -d)/icon.iconset"; mkdir -p "$SET"
for s in 16 32 128 256 512; do
  sips -z "$s" "$s"            "$SRC" --out "$SET/icon_${s}x${s}.png"     >/dev/null
  sips -z $((s*2)) $((s*2))    "$SRC" --out "$SET/icon_${s}x${s}@2x.png"  >/dev/null
done
sips -z 1024 1024 "$SRC" --out "$SET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$SET" -o "$OUT"
rm -rf "$(dirname "$SET")"
echo "✅ $OUT"
