# 홍시 앱 아이콘 (Clawd on Desk 도크 아이콘)

홍시 슈나우저를 **Clawd on Desk** 앱의 도크 아이콘으로 쓰기 위한 패키지.

> **방식:** 번들 안 `Contents/Resources/icon.icns`를 교체한다. Clawd는 Electron 앱이라
> 실행 시 이 icns로 도크 타일을 그리기 때문에, Finder 커스텀 아이콘 방식은 도크엔 안 먹힌다.
> 리소스만 바꾸므로 서명 seal 경고는 뜨지만 hardened runtime 실행엔 무관(앱 정상 실행 확인됨).
> 실행 파일/엔타이틀먼트는 안 건드린다.

> ⚠️ 앱이 **자동업데이트되면 icon.icns가 원래대로 덮어써진다**. 그때마다 `apply-to-clawd.sh`만
> 다시 실행하면 복구된다. 원본은 `clawd-icon-original.icns`로 백업돼 있다.

## 빠른 사용

```bash
cd app-icon
./apply-to-clawd.sh                      # 기본(idle 얼굴확대) 적용
./apply-to-clawd.sh variants/face-happy.png   # 다른 포즈로 적용
./revert-clawd.sh                        # 원래 아이콘으로 복원
```

도크에 바로 안 바뀌면 잠시 기다리거나 로그아웃/로그인. (스크립트가 `killall Dock`까지 함)

## 구성

| 파일 | 용도 |
|------|------|
| `hongsi-app-icon.png` | **현재 기본 아이콘** 원본 (1024px, = `variants/face-idle.png`) |
| `hongsi-app-icon.icns` | 실제 적용에 쓰는 .icns (apply 기본 소스) |
| `clawd-icon-original.icns` | **앱 원본 아이콘 백업** (revert 복원용, 최초 apply 때 자동 생성) |
| `clawd-info-original.plist` | **앱 원본 Info.plist 백업** (이름 복원용, 최초 apply 때 자동 생성) |
| `apply-to-clawd.sh` | 도크 아이콘 설정 (Finder 커스텀 아이콘) |
| `revert-clawd.sh` | 원래대로 복원 |
| `build-icns.sh` | `<1024.png>` → `.icns` 변환 |
| `variants/face-*.png` | 9개 포즈 × 감색 배경 + 얼굴확대 (아이콘 후보) |
| `variants/tr-*.png` | 9개 포즈 × 투명 전신 (참고) |
| `preview.html` | 후보 비교 페이지 (`open preview.html`) |

## 앱 이름 (도크 라벨)

`apply-to-clawd.sh`는 아이콘과 함께 도크 표시 이름도 **Hongsi**로 바꾼다(`CFBundleDisplayName`).
다른 이름으로 하려면 환경변수로:

```bash
DISPLAY_NAME="홍시" ./apply-to-clawd.sh
```

> ⚠️ **`CFBundleName`은 절대 바꾸지 말 것.** Electron이 이 값에서 헬퍼 앱 이름
> (`Clawd on Desk Helper.app`)을 파생하기 때문에, 바꾸면 `Unable to find helper app`로
> 앱이 즉시 크래시한다. 표시 이름은 `CFBundleDisplayName`만 바꾸면 된다.
>
> 메뉴바(애플 메뉴 옆 굵은 앱 메뉴)는 Electron이 `app.asar` 안 `package.json`의
> productName에서 읽을 수 있어 그대로 "Clawd on Desk"일 수 있다. 도크 라벨/Finder 이름은 바뀐다.

## 기본 아이콘 바꾸기

다른 포즈를 기본으로 삼으려면 그 파일을 기본 이름으로 복사:

```bash
cp variants/face-happy.png hongsi-app-icon.png
./build-icns.sh hongsi-app-icon.png hongsi-app-icon.icns   # icns도 갱신(선택)
./apply-to-clawd.sh
```

## 아이콘을 다시 만들려면 (에셋 수정 후)

`variants/face-*.png`는 `../hongsi/assets/*.svg`를 감색 둥근사각형 배경 위에
얼굴 영역(viewBox `215 15 690 690`)으로 크롭해 1024px로 렌더한 것이다.
SVG 렌더는 macOS 기본 `qlmanage`(QuickLook)를 쓴다 — 외부 의존성 없음.
재생성 로직은 커밋 히스토리의 생성 스크립트 참고.

## 동작 원리 (번들 icon.icns 교체)

1. 최초 1회 원본 `icon.icns`를 `clawd-icon-original.icns`로 백업
2. `hongsi-app-icon.icns`를 `$APP/Contents/Resources/icon.icns`로 복사
3. `lsregister -f "$APP"` — LaunchServices에 번들 재등록(아이콘 다시 읽힘)
4. 실행 중이면 앱 종료 후 `open` — Electron이 새 icns로 도크 타일을 그림

복원(`revert-clawd.sh`)은 `clawd-icon-original.icns`를 다시 덮어쓰고 재등록·재시작.
필요 도구(`sips`/`iconutil`/`lsregister`/`osascript`)는 모두 macOS 기본 제공.

> 참고: Finder 표시 아이콘만 바꾸고 싶을 땐 Finder 커스텀 아이콘(`Icon\r` + `SetFile -a C`)도
> 가능하지만, 실행 중인 Electron 도크 타일에는 적용되지 않아 여기선 쓰지 않는다.
