#!/usr/bin/env bash
# "Clawd on Desk" 도크 아이콘을 원래(앱 기본)대로 되돌린다.
#   ./revert-clawd.sh ["/Applications/Clawd on Desk.app"]
set -euo pipefail
APP="${1:-/Applications/Clawd on Desk.app}"
[ -d "$APP" ] || { echo "❌ 앱 없음: $APP"; exit 1; }
rm -f "$APP/Icon"$'\r'
SetFile -a c "$APP"          # 커스텀 아이콘 플래그 해제(소문자 c)
touch "$APP"
killall Dock 2>/dev/null || true
echo "✅ 원래 아이콘으로 복원: $APP"
