# 🐶 Pixel Pup × Clawd on Desk — 설치 A to Z

## 0. 이게 뭔가요?
- **Clawd on Desk**: 데스크톱에 사는 픽셀 펫 앱. **Claude Code**(터미널 AI 코딩 도구)의 작업 상태에 맞춰 펫이 움직입니다.
- **Pixel Pup**: 그 펫을 **슈나우저 강아지**로 바꾸는 커스텀 테마(이 가이드의 `pixel-dog.zip`).
- ⚠️ **전제**: Claude Code가 설치·실행 중이어야 강아지가 반응합니다. (없으면 그냥 가만히 있어요.)
- 지원 OS: macOS · Windows · Linux

---

## 1. 앱 설치 — Clawd on Desk

### 방법 A. 릴리스 다운로드 (가장 쉬움, 추천)
1. https://github.com/rullerzhou-afk/clawd-on-desk/releases 접속
2. 본인 OS용 설치파일이 있으면 받아서 설치
3. 한국어 안내: 저장소의 **README.ko-KR.md**

### 방법 B. 소스로 실행 (개발자용 / 릴리스 파일이 없을 때)
[Node.js](https://nodejs.org) (LTS) 설치 후 터미널에서:
```bash
git clone https://github.com/rullerzhou-afk/clawd-on-desk.git
cd clawd-on-desk
npm install
npm start
```
- 첫 실행 시 **Claude Code 훅을 자동 등록**(`~/.claude/settings.json`)해서 작업에 반응하게 됩니다.
- 맥은 **상단 메뉴바 아이콘**으로 제어합니다(독 아이콘 없음).

---

## 2. 강아지 테마 설치 — Pixel Pup

1. 받은 **`pixel-dog.zip`** 압축 해제 → `pixel-dog` 폴더가 나옵니다.
2. 그 폴더를 **통째로** 아래 `themes` 폴더에 넣으세요 (없으면 폴더 생성):
   | OS | 경로 |
   |----|------|
   | macOS | `~/Library/Application Support/clawd-on-desk/themes/` |
   | Windows | `%APPDATA%\clawd-on-desk\themes\` |
   | Linux | `~/.config/clawd-on-desk/themes/` |
3. 앱 **메뉴바(트레이) 아이콘 → Settings → Theme → "Pixel Pup"** 선택
4. 목록에 안 보이면 앱 재시작

> 폴더 구조는 이래야 합니다: `themes/pixel-dog/theme.json`, `themes/pixel-dog/assets/…`, `themes/pixel-dog/sounds/…`

---

## 3. 강아지가 언제 어떤 모습이 되나

| 상황 (Claude Code) | 강아지 모습 |
|---|---|
| 평소 / 끌어서 이동 중 | 엎드려 숨쉬기 (기본) |
| 프롬프트 받고 생각할 때 | 📖 안경 쓰고 책 읽기 (눈이 좌우로 스캔) |
| 작업 중 (툴 사용) | 💻 노트북 타이핑 (앞발 토닥토닥) |
| 세션 **2개 이상** 동시 작업 | 🤹 공 저글링 |
| 작업 **완료** | 🎉 컨페티 + 완료음(`complete.mp3`) |
| 알림 | 🟠 큰 "!" 뱃지 + 알림음(`confirm.mp3`) |
| 에러(파일 편집 실패 등) | 🔴 큰 "!" + 몸 흔들기 |
| 오래 가만 두면 | 💤 Zzz 잠 |
| 클릭 / 더블클릭 | 해피 / 저글링 (쓰다듬기 반응) |

---

## 4. 소리
- 완료음·알림음이 테마에 포함돼 있습니다(zip 안 `sounds/`).
- 안 들리면: 앱 설정에서 음소거(Mute)·볼륨 확인.
- 참고: 완료 시점에 **백그라운드 작업이 돌고 있으면** 앱이 "아직 일하는 중"으로 보고 축하(컨페티·소리)를 잠깐 미룹니다 — 정상 동작이에요.

---

## 5. 안 될 때
- **강아지가 안 움직임** → Claude Code가 실행 중인지 확인.
- **테마가 목록에 없음** → 폴더 위치/구조 확인(`themes/pixel-dog/theme.json`) 후 앱 재시작.
- **깨진 이미지/안 뜸** → `pixel-dog` 폴더가 통째로(assets·sounds 포함) 들어갔는지 확인.

즐기세요! 🐾
