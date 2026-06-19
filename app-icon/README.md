# 홍시 앱 아이콘 (Clawd on Desk 도크 아이콘)

홍시 슈나우저를 **Clawd on Desk** 앱의 도크 아이콘으로 쓰기 위한 패키지.

`apply-to-clawd.sh`가 세 곳을 한 번에 바꾼다:

1. **실행 중 도크 타일** ← 핵심. Clawd는 Electron이라 `app.dock.setIcon(assets/dock-icon.png)`로
   도크를 런타임에 그린다. 그래서 `app.asar` 안 `dock-icon.png`를 홍시로 교체해야 실제 도크가 바뀐다.
   asar는 무결성 검증(파일별 SHA256 + `Info.plist`의 헤더 SHA256)이 걸려 있어 모두 재계산한다.
2. **번들 아이콘** `Contents/Resources/icon.icns` ← Finder/미실행 상태 표시용.
3. **표시 이름** `CFBundleDisplayName` = Hongsi ← Finder/도크 라벨.

> 리소스만 바꾸므로 코드서명 seal 경고는 뜨지만 hardened runtime 실행엔 무관(앱 정상 실행 확인됨).
> 실행 파일/엔타이틀먼트는 안 건드린다. **`CFBundleName`·`package.json`의 name/productName도 안 건드린다**
> (전자는 헬퍼앱 크래시, 후자는 userData 경로가 바뀌어 로그인/설정 유실).

> ⚠️ 앱이 **자동업데이트되면 전부 원래대로 덮어써진다**. 그때마다 `apply-to-clawd.sh`만 다시
> 실행하면 복구된다. 원본은 `clawd-*-original.*` / `clawd-app.asar.backup`으로 백업된다(최초 apply 때 자동).

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
| `repack-dock-icon.py` | app.asar 안 `dock-icon.png` 교체 + 무결성/Info.plist 해시 재계산 (apply/revert가 호출) |
| `clawd-dock-icon-original.png` | 앱 **원본 도크 아이콘** 백업 (revert용, gitignore) |
| `clawd-app.asar.backup` | 원본 app.asar 통째 백업 (비상 복원용, 7.7MB, gitignore) |
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

## 동작 원리

**왜 단순 교체로는 안 됐나:** Clawd는 Electron 앱이라 실행될 때 코드에서
`app.dock.setIcon(nativeImage.createFromPath(".../assets/dock-icon.png"))`로 도크 타일을 직접 그린다.
그래서 번들 `icon.icns`나 Finder 커스텀 아이콘을 바꿔도 **실행 중 도크는 안 바뀐다**.
도크를 진짜로 바꾸려면 `app.asar` 안 `dock-icon.png`를 교체해야 한다.

**asar 교체 (`repack-dock-icon.py`):**
1. `selftest` — 변경 없는 재패킹이 원본과 바이트 100% 동일한지 확인(아니면 중단)
2. 최초 1회 원본 `dock-icon.png` 추출 백업
3. `dock-icon.png`를 홍시 PNG로 교체, 그 파일의 무결성 블록(SHA256) 재계산
4. 모든 파일 오프셋 재배치 + 헤더 재직렬화 → 헤더 SHA256 재계산
5. `Info.plist`의 `ElectronAsarIntegrity:Resources/app.asar:hash`를 새 헤더 해시로 갱신
   (이게 안 맞으면 Electron이 실행을 거부)
6. 재패킹 후 전 파일을 재추출해 원본과 일치하는지 자체검증

복원(`revert-clawd.sh`)은 같은 도구로 `dock-icon.png`를 원본으로 되돌리고(해시 자동 ac26f470으로 복귀),
`icon.icns`·`Info.plist`도 백업본으로 되돌린다.
필요 도구(`python3`/`sips`/`iconutil`/`lsregister`/`osascript`)는 모두 macOS 기본 제공.
