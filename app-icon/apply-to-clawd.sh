#!/usr/bin/env bash
# 홍시 아이콘을 "Clawd on Desk" 도크 아이콘으로 설정한다.
# Finder 커스텀 아이콘 방식 — 앱 번들의 Mach-O/서명을 건드리지 않으므로 안전하고 되돌리기 쉽다.
# 앱이 자동업데이트되어 아이콘이 원래대로 돌아가면 이 스크립트를 다시 실행만 하면 된다.
#
#   ./apply-to-clawd.sh                       # 기본 아이콘(hongsi-app-icon.png) 적용
#   ./apply-to-clawd.sh variants/face-happy.png   # 다른 포즈로 적용
#   ./apply-to-clawd.sh <png> "/Applications/다른앱.app"
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PNG="${1:-$HERE/hongsi-app-icon.png}"
APP="${2:-/Applications/Clawd on Desk.app}"

[ -f "$PNG" ] || { echo "❌ 아이콘 PNG 없음: $PNG"; exit 1; }
[ -d "$APP" ] || { echo "❌ 앱 없음: $APP"; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp "$PNG" "$TMP/icon.png"
sips -i "$TMP/icon.png" >/dev/null                 # PNG 리소스 포크에 icns 추가
DeRez -only icns "$TMP/icon.png" > "$TMP/icon.rsrc" # icns 리소스 추출
ICONF="$APP/Icon"$'\r'                              # 번들 안 특수 Icon 파일(끝에 CR)
rm -f "$ICONF"
Rez -append "$TMP/icon.rsrc" -o "$ICONF"           # Icon 파일에 아이콘 기록
SetFile -a C "$APP"                                 # 번들에 "커스텀 아이콘 있음" 플래그
SetFile -a V "$ICONF"                               # Icon 파일 숨김
touch "$APP"
killall Dock 2>/dev/null || true
echo "✅ 적용 완료: $(basename "$PNG") → $APP"
echo "   도크에 바로 안 보이면 잠시 후 자동 갱신되거나, 로그아웃/로그인 하세요."
