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
rm -f "$APP/Icon"$'\r'; SetFile -a c "$APP" 2>/dev/null || true   # Finder 커스텀 아이콘 잔재 제거
"$LSREG" -f "$APP" 2>/dev/null || true
if pgrep -f "MacOS/Clawd on Desk$" >/dev/null; then
  osascript -e 'quit app "Clawd on Desk"' 2>/dev/null || true; sleep 2
fi
killall Dock 2>/dev/null || true
open -a "$APP" 2>/dev/null || true
echo "✅ 원래 아이콘으로 복원: $APP (앱 재시작됨)"
