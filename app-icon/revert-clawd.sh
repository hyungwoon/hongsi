#!/usr/bin/env bash
# "Clawd on Desk" 도크 아이콘을 백업해둔 앱 원본 아이콘으로 되돌린다.
#   ./revert-clawd.sh ["/Applications/Clawd on Desk.app"]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="${1:-/Applications/Clawd on Desk.app}"
ICNS="$APP/Contents/Resources/icon.icns"
BACKUP="$HERE/clawd-icon-original.icns"
LSREG=/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister

[ -d "$APP" ] || { echo "❌ 앱 없음: $APP"; exit 1; }
[ -f "$BACKUP" ] || { echo "❌ 원본 백업 없음: $BACKUP (이미 원본이거나 백업 유실)"; exit 1; }

cp "$BACKUP" "$ICNS"
# 실행 중 도크 아이콘: app.asar 안 dock-icon.png를 원본으로 되돌림(+무결성/Info.plist 헤더해시 갱신)
DOCK_ORIG="$HERE/clawd-dock-icon-original.png"
[ -f "$DOCK_ORIG" ] && python3 "$HERE/repack-dock-icon.py" apply "$DOCK_ORIG" "$APP"
# 이름/해시도 원래대로 (Info.plist 백업 복원 — asar이 원본이라 헤더해시도 일치)
[ -f "$HERE/clawd-info-original.plist" ] && cp "$HERE/clawd-info-original.plist" "$APP/Contents/Info.plist"
rm -f "$APP/Icon"$'\r'; SetFile -a c "$APP" 2>/dev/null || true   # Finder 커스텀 아이콘 잔재 제거
"$LSREG" -f "$APP" 2>/dev/null || true
if pgrep -f "MacOS/Clawd on Desk$" >/dev/null; then
  osascript -e 'quit app "Clawd on Desk"' 2>/dev/null || true; sleep 2
fi
killall Dock 2>/dev/null || true
open -a "$APP" 2>/dev/null || true
echo "✅ 원래 아이콘으로 복원: $APP (앱 재시작됨)"
