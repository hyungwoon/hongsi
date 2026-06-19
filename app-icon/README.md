# 홍시 앱 아이콘 (Clawd on Desk 도크 아이콘)

홍시 슈나우저를 **Clawd on Desk** 앱의 도크 아이콘으로 쓰기 위한 패키지.
앱 번들의 서명/실행파일을 건드리지 않는 **Finder 커스텀 아이콘** 방식이라 안전하고 되돌리기 쉽다.

> ⚠️ 이 방식은 앱이 **자동업데이트되면 초기화**된다. 그때마다 `apply-to-clawd.sh`만 다시 실행하면 복구된다.

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
| `hongsi-app-icon.png` | **현재 기본 아이콘** (1024px, = `variants/face-idle.png`) |
| `hongsi-app-icon.icns` | 보관용 .icns (번들 직접 교체나 타 용도) |
| `apply-to-clawd.sh` | 도크 아이콘 설정 (Finder 커스텀 아이콘) |
| `revert-clawd.sh` | 원래대로 복원 |
| `build-icns.sh` | `<1024.png>` → `.icns` 변환 |
| `variants/face-*.png` | 9개 포즈 × 감색 배경 + 얼굴확대 (아이콘 후보) |
| `variants/tr-*.png` | 9개 포즈 × 투명 전신 (참고) |
| `preview.html` | 후보 비교 페이지 (`open preview.html`) |

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

## 동작 원리 (Finder 커스텀 아이콘)

1. `sips -i icon.png` — PNG 리소스 포크에 `icns` 리소스 추가
2. `DeRez -only icns` — 그 리소스를 추출
3. `Rez -append … -o "$APP/Icon"$'\r'` — 번들 안 특수 `Icon`(끝 CR) 파일에 기록
4. `SetFile -a C "$APP"` — 번들에 "커스텀 아이콘 있음" 플래그
5. `SetFile -a V "Icon"` — Icon 파일 숨김

복원은 `Icon` 파일 삭제 + `SetFile -a c`(소문자)로 플래그 해제.
필요 도구(`sips`/`DeRez`/`Rez`/`SetFile`/`iconutil`)는 모두 macOS + Xcode CLT 기본 제공.
