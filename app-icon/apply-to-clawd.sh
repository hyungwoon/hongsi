#!/usr/bin/env bash
# 홍시 아이콘을 "Clawd on Desk" 도크 아이콘으로 적용한다.
#
# 방식: 앱 번들의 Contents/Resources/icon.icns 를 직접 교체한다.
#   Clawd는 Electron 앱이라 실행 시 번들 icon.icns 로 도크 타일을 그린다.
#   (Finder 커스텀 아이콘 방식은 실행 중 Electron이 덮어써서 도크엔 안 먹힘)
#   리소스만 바꾸므로 코드 서명 seal 경고는 뜨지만 hardened runtime 실행엔 무관.
#
# 앱이 자동업데이트되어 아이콘이 원래대로 돌아가면 이 스크립트만 다시 실행하면 된다.
#
#   ./apply-to-clawd.sh                          # 기본(hongsi-app-icon.icns) 적용
#   ./apply-to-clawd.sh hongsi-app-icon.icns     # 특정 icns
#   ./apply-to-clawd.sh variants/face-happy.png  # png를 주면 즉석에서 icns 빌드
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${1:-$HERE/hongsi-app-icon.icns}"
APP="${2:-/Applications/Clawd on Desk.app}"
ICNS="$APP/Contents/Resources/icon.icns"
LSREG=/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister

[ -d "$APP" ] || { echo "❌ 앱 없음: $APP"; exit 1; }
[ -f "$SRC" ] || { echo "❌ 소스 없음: $SRC"; exit 1; }

# png를 주면 임시 icns로 변환
case "$SRC" in
  *.png) TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
         "$HERE/build-icns.sh" "$SRC" "$TMP/icon.icns" >/dev/null
         SRC="$TMP/icon.icns" ;;
esac

# 앱 원본 아이콘 백업(최초 1회만) — 복원용
[ -f "$HERE/clawd-icon-original.icns" ] || cp "$ICNS" "$HERE/clawd-icon-original.icns"
cp "$SRC" "$ICNS"

# 표시 이름(도크 라벨)도 변경 — CFBundleDisplayName만!
#   ⚠️ CFBundleName 은 절대 바꾸지 말 것: Electron이 여기서 헬퍼앱 이름
#   ("Clawd on Desk Helper.app")을 파생하므로 바꾸면 "Unable to find helper app"로 크래시.
PLIST="$APP/Contents/Info.plist"
DISPLAY_NAME="${DISPLAY_NAME:-Hongsi}"
[ -f "$HERE/clawd-info-original.plist" ] || cp "$PLIST" "$HERE/clawd-info-original.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $DISPLAY_NAME" "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $DISPLAY_NAME" "$PLIST"

# 실행 중 도크 타일: Clawd는 app.dock.setIcon(assets/dock-icon.png)로 도크를 런타임에 그린다.
#   → app.asar 안 dock-icon.png를 교체해야 실제 도크가 바뀐다. asar 무결성 해시 + Info.plist
#   헤더 해시도 재계산한다(아래 파이썬). 이게 도크 변경의 핵심 단계.
DOCK_PNG="${DOCK_PNG:-$HERE/hongsi-app-icon.png}"
python3 "$HERE/repack-dock-icon.py" apply "$DOCK_PNG" "$APP"

"$LSREG" -f "$APP" 2>/dev/null || true

# 실행 중이면 재시작해야 도크가 새 아이콘을 읽는다
if pgrep -f "MacOS/Clawd on Desk$" >/dev/null; then
  osascript -e 'quit app "Clawd on Desk"' 2>/dev/null || true
  sleep 2
fi
killall Dock 2>/dev/null || true
open -a "$APP" 2>/dev/null || true
echo "✅ 적용 완료: 아이콘=$(basename "${1:-hongsi-app-icon.icns}"), 이름=$DISPLAY_NAME → $APP (앱 재시작됨)"
