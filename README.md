# 홍시 (Hongsi) 🐶

형운의 데스크탑 펫. 픽셀아트 **슈나우저 강아지**로, [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk)(데스크톱 펫 앱) 위에 올라가 **Claude Code의 작업 상태**에 맞춰 숨쉬고·책 읽고·타이핑하고·저글링하고·축하한다.

> 홍시는 munsujin의 **Pixel Pup** 테마를 기반으로 한 개인 펫 브랜딩이다. 에셋 원작자 표기는 `theme.json`의 `author`에 보존돼 있다.

- **펫 이름**: 홍시 (Hongsi) — 앱 테마 선택기에 `Hongsi`로 표시
- **테마 폴더 id**: `hongsi/` (앱이 폴더명으로 테마를 인식)
- **version**: 2.3.0 · **schemaVersion**: 1
- **에셋**: SVG 9종(`assets/`) + 사운드 2종(`sounds/`: `complete.mp3`, `confirm.mp3`)

## 구성

```
hongsi/
├── theme.json        # 상태→에셋 매핑, 타이밍, 히트박스, 레이아웃 (name: "Hongsi")
├── assets/*.svg      # idle/thinking/working/happy/sleeping/waking/error/notification/juggling
├── sounds/*.mp3      # complete(완료음) / confirm(알림음)
└── 설치방법.txt
```

`theme.json` 핵심:
- `states`: Claude Code 상태별 SVG (idle·thinking·working·attention·sleeping·waking·error·notification·juggling)
- `workingTiers`: 세션 `minSessions: 2` → `juggling.svg`(2개 이상 동시 작업이면 공 저글링), 1개 → `working.svg`
- `reactions`: drag / clickLeft(happy) / annoyed(error) / double(juggling)
- `sounds`: complete · confirm

## 설치

자세한 A→Z는 [`Pixel-Pup-가이드.md`](./Pixel-Pup-가이드.md) 참고 (원본 가이드 — 폴더명만 `hongsi`로 읽으면 됨).

1. Clawd on Desk 앱 설치 — https://github.com/rullerzhou-afk/clawd-on-desk/releases
2. `hongsi/` 폴더를 통째로 themes 폴더에 복사:
   | OS | 경로 |
   |----|------|
   | macOS | `~/Library/Application Support/clawd-on-desk/themes/` |
   | Windows | `%APPDATA%\clawd-on-desk\themes\` |
   | Linux | `~/.config/clawd-on-desk/themes/` |
3. 메뉴바(트레이) 아이콘 → Settings → Theme → **Hongsi** 선택 (안 보이면 앱 재시작)

> 앱은 기동 시 `clawd-prefs.json`의 `"theme"` 필드를 읽으므로, 메뉴바 클릭 대신 그 값을 `"hongsi"`로 바꾸고 재실행해도 적용된다.

### 한 줄 설치 (macOS)

```bash
cp -R hongsi ~/Library/Application\ Support/clawd-on-desk/themes/hongsi
```

## 동작 매핑

| 상황 (Claude Code) | 홍시 |
|---|---|
| 평소 / 드래그 | 엎드려 숨쉬기 (idle) |
| 프롬프트 생각 중 | 안경 쓰고 책 읽기 (thinking) |
| 툴 사용 중 | 노트북 타이핑 (working) |
| 세션 2+ 동시 | 공 저글링 (juggling) |
| 작업 완료 | 컨페티 + `complete.mp3` |
| 알림 / 에러 | "!" 뱃지 + `confirm.mp3` / 몸 흔들기 |
| 장시간 유휴 | Zzz 수면 |
