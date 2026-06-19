# 홍시 (Hongsi)

> 형운의 데스크탑 펫 테마. Clawd on Desk 앱용 픽셀아트 슈나우저(`Hongsi`). munsujin의 Pixel Pup 테마 기반 개인 브랜딩.

## Mission

홍시 테마 에셋(SVG + 사운드 + `theme.json`)을 **재사용 가능한 단일 패키지**로 보관한다. 다른 머신·다른 펫 앱 설정에 그대로 끌어다 쓸 수 있게 폴더 id를 `hongsi`로 통일.

## 구조

- `hongsi/` — 테마 패키지 (이 폴더를 통째로 `themes/`에 복사하면 끝)
  - `theme.json` (`name: "Hongsi"`), `assets/*.svg` 9종, `sounds/*.mp3` 2종, `설치방법.txt`
- `Pixel-Pup-가이드.md` — 앱+테마 설치 원본 가이드 (폴더명만 `hongsi`로 치환해 읽기)
- `README.md` — 요약 + 동작 매핑
- `app-icon/` — **Clawd on Desk 도크 아이콘+이름** 패키지 (홍시 슈나우저 감색 배경+얼굴확대, 도크 라벨 "Hongsi"). 핵심: Clawd는 Electron이라 `app.dock.setIcon(asar 안 assets/dock-icon.png)`로 도크를 런타임에 그림 → **`app.asar` 안 dock-icon.png를 교체**해야 실제 도크가 바뀜(`repack-dock-icon.py`가 무결성 SHA256 + `Info.plist`의 ElectronAsarIntegrity 헤더해시까지 재계산). 보조로 번들 `icon.icns`+`CFBundleDisplayName`도 변경. ⚠️ **절대 금지**: `CFBundleName`(헬퍼앱 이름 파생→크래시)·`package.json` name/productName(userData 경로 변경→로그인 유실). 앱 업데이트 시 초기화 → `app-icon/apply-to-clawd.sh` 재실행으로 복구(원본 백업 `clawd-*-original.*`/`clawd-app.asar.backup`은 gitignore, 최초 apply 때 자동생성). 복원 `revert-clawd.sh`, 후보 비교 `preview.html`, 상세 `app-icon/README.md`.

## 진입 가이드

- 테마만 쓸 거면: `hongsi/`를 OS별 themes 경로에 복사 → 앱 Settings에서 `Hongsi` 선택.
- 앱은 **폴더명**으로 테마를 인식한다(`theme.json`에 별도 id 필드 없음). 폴더명 = prefs `"theme"` 값 = `hongsi`.
- 표시 이름(Hongsi)은 `theme.json`의 `name`. 폴더명과 표시명은 독립.

## 실행 모드

코드 빌드 없음 — 순수 정적 에셋 레포. 에셋/매핑 수정 시 `theme.json` 스키마(`schemaVersion: 1`) 유지.

## GitHub

HYUNGWOON 레이어 → `hyungwoon`(개인) 계정 / `hyungwoon` 개인 repo. 커밋 신원 `hyungwoon <hyungwoon.kr@gmail.com>` (폴더 위치로 `includeIf` 자동 강제).
