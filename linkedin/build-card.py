#!/usr/bin/env python3
"""홍시 상태별 LinkedIn 정방형 카드 생성기 (상태당 1장 · 총 9장).

- hongsi/assets/*.svg 9종을 RAW로 HTML에 인라인 → file:// 더블클릭으로 동작.
- 카드는 단일 인라인 SVG: 캐릭터(중첩 SVG, CSS 애니 실제 재생) + 한국어 설명 텍스트.
- 화면: 한 번에 한 상태만 마운트(펫끼리 클래스/keyframe 이름이 겹쳐서) → 충돌 없음.
- PNG: 카드 SVG 직렬화→canvas 래스터화 (정지 스냅샷). 단일/전체9장 버튼 제공.
- MP4(모션): 브라우저는 CSS-SVG 애니를 프레임 캡처 못함 → render-all.mjs(Playwright+ffmpeg)로 생성.

재생성: python3 build-card.py   (states.json·hongsi-states-card.html 갱신)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASSETS = ROOT / "hongsi" / "assets"
OUT_HTML = HERE / "hongsi-states-card.html"
OUT_STATES = HERE / "states.json"

# 표시 순서 = 강아지의 하루 흐름 (대기→일→소통→휴식)
STATES = [
    {"key": "idle",         "file": "idle.svg",         "label": "대기",       "en": "idle",         "desc": "숨 쉬며 가만히 대기해요"},
    {"key": "thinking",     "file": "thinking.svg",     "label": "생각 중",    "en": "thinking",     "desc": "골똘히 읽고 고민하는 중"},
    {"key": "working",      "file": "working.svg",      "label": "작업 중",    "en": "working",      "desc": "열심히 타이핑하는 중"},
    {"key": "juggling",     "file": "juggling.svg",     "label": "멀티태스킹", "en": "juggling",     "desc": "여러 세션을 동시에 저글링"},
    {"key": "attention",    "file": "happy.svg",        "label": "반가움",     "en": "attention",    "desc": "쓰다듬으면 신나서 기뻐해요"},
    {"key": "notification", "file": "notification.svg", "label": "알림",       "en": "notification", "desc": "확인할 게 있어요!"},
    {"key": "error",        "file": "error.svg",        "label": "삐짐",       "en": "error",        "desc": "문제가 생겨 뾰로통해요"},
    {"key": "sleeping",     "file": "sleeping.svg",     "label": "수면",       "en": "sleeping",     "desc": "오래 쉬면 새근새근 잠들어요"},
    {"key": "waking",       "file": "waking.svg",       "label": "기상",       "en": "waking",       "desc": "하품하며 천천히 깨어나요"},
]


def main() -> None:
    pups = {s["key"]: (ASSETS / s["file"]).read_text(encoding="utf-8") for s in STATES}
    meta = [{"key": s["key"], "label": s["label"], "en": s["en"], "desc": s["desc"]} for s in STATES]

    OUT_STATES.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    html = (TEMPLATE
            .replace("/*__PUPS__*/", json.dumps(pups))
            .replace("/*__STATES__*/", json.dumps(meta, ensure_ascii=False)))
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"생성: {OUT_HTML.name}  ({OUT_HTML.stat().st_size/1_000_000:.2f} MB)")
    print(f"생성: {OUT_STATES.name}  ({len(STATES)}개 상태)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>홍시 상태별 카드 · 9장</title>
<style>
  :root{
    --bg:#070a0f; --panel:#161b25; --border:#262e3d;
    --persimmon:#ff7a33; --persimmon-soft:#ffb27a; --ink:#f5f3ee; --muted:#98a2b3;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Pretendard","Segoe UI",sans-serif}
  .wrap{min-height:100vh;display:flex;flex-direction:column;align-items:center;gap:18px;padding:28px 16px 60px}
  .toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:center;max-width:760px}
  .toolbar h1{font-size:15px;font-weight:600;color:var(--muted);margin:0 6px 0 0}
  button{font:inherit;font-weight:600;font-size:14px;cursor:pointer;border-radius:10px;padding:9px 16px;
    border:1px solid var(--border);background:var(--panel);color:var(--ink);transition:.15s}
  button:hover{border-color:var(--persimmon);color:var(--persimmon-soft)}
  button.primary{background:var(--persimmon);border-color:var(--persimmon);color:#1a0d04}
  button.primary:hover{background:#ff8c4d}
  select{font:inherit;font-size:14px;padding:9px 11px;border-radius:10px;border:1px solid var(--border);
    background:var(--panel);color:var(--ink)}
  .tabs{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;max-width:760px}
  .tabs button{padding:7px 13px;font-size:13px;border-radius:8px}
  .tabs button.on{background:var(--persimmon);border-color:var(--persimmon);color:#1a0d04}
  .stage{width:min(560px,92vw);aspect-ratio:1/1;border-radius:18px;overflow:hidden;
    box-shadow:0 22px 64px rgba(0,0,0,.55);border:1px solid var(--border)}
  .stage svg{display:block;width:100%;height:100%}
  .hint{color:var(--muted);font-size:13px;max-width:560px;text-align:center;line-height:1.65}
  .hint code{background:var(--panel);padding:2px 7px;border-radius:6px;color:var(--persimmon-soft)}
  /* 캡처 모드: 크롬 숨기고 카드만 1080×1080 풀블리드 (Playwright 녹화/스냅샷용) */
  body.capture .wrap{padding:0;gap:0}
  body.capture .toolbar,body.capture .tabs,body.capture .hint{display:none}
  body.capture .stage{width:1080px;height:1080px;border-radius:0;border:none;box-shadow:none}
</style>
</head>
<body>
<div class="wrap">
  <div class="toolbar">
    <h1>🐶 홍시 상태별 카드 · 9장</h1>
    <label>해상도
      <select id="scale">
        <option value="1">1080</option>
        <option value="2" selected>2160 (2×)</option>
        <option value="3">3240 (3×)</option>
      </select>
    </label>
    <button class="primary" id="dl">⬇ 이 상태 PNG</button>
    <button id="dlAll">⬇ 전체 9장 PNG</button>
  </div>
  <div class="tabs" id="tabs"></div>
  <div class="stage" id="stage"></div>
  <p class="hint">탭으로 상태를 바꿔 보세요. 화면 속 캐릭터는 <b>실제로 움직이며</b>, PNG는 정지 스냅샷으로 저장됩니다.
  <br>모션 <code>.mp4</code> 9개는 <code>node render-all.mjs</code> 로 생성합니다 (브라우저는 SVG 애니를 영상으로 못 굽습니다).</p>
</div>

<script>
const PUPS   = /*__PUPS__*/;
const STATES = /*__STATES__*/;
const SIZE = 1080;
const NS = "http://www.w3.org/2000/svg";
const FF = "-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', sans-serif";

// 펫 SVG 루트에 위치·크기 주입 (중첩 SVG로 배치, 자체 viewBox 유지 → 비율 보존)
function positionedPup(key){
  return PUPS[key].replace("<svg",
    '<svg x="120" y="120" width="840" height="600" preserveAspectRatio="xMidYMid meet"');
}

function cardMarkup(st, idx){
  const cx = SIZE/2;
  const num = String(idx+1).padStart(2,"0");
  return `<svg xmlns="${NS}" viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}" id="card-svg"
       font-family="${FF}">
    <defs>
      <radialGradient id="bg" cx="50%" cy="32%" r="88%">
        <stop offset="0%" stop-color="#19212f"/>
        <stop offset="58%" stop-color="#0e1117"/>
        <stop offset="100%" stop-color="#080b10"/>
      </radialGradient>
      <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ff8c4d"/><stop offset="100%" stop-color="#ff6a2a"/>
      </linearGradient>
    </defs>
    <rect width="${SIZE}" height="${SIZE}" fill="url(#bg)"/>

    <!-- 워드마크 -->
    <circle cx="76" cy="74" r="9" fill="#ff7a33"/>
    <text x="98" y="84" fill="#ff8c4d" font-size="32" font-weight="800">홍시</text>
    <text x="160" y="84" fill="#cfd6e2" font-size="24" font-weight="600" letter-spacing="0.06em">Hongsi</text>
    <text x="${SIZE-64}" y="84" fill="#5d6677" font-size="24" font-weight="700"
          text-anchor="end" letter-spacing="0.12em">${num} / 09</text>

    <!-- 캐릭터 (애니메이션) -->
    ${positionedPup(st.key)}

    <!-- 설명 -->
    <line x1="${cx-44}" y1="800" x2="${cx+44}" y2="800" stroke="url(#acc)" stroke-width="5" stroke-linecap="round"/>
    <text x="${cx}" y="884" fill="#f5f3ee" font-size="80" font-weight="800" text-anchor="middle">${st.label}</text>
    <text x="${cx}" y="930" fill="#ff9457" font-size="26" font-weight="700" text-anchor="middle"
          letter-spacing="0.16em">${st.en.toUpperCase()}</text>
    <text x="${cx}" y="992" fill="#9aa3b2" font-size="36" font-weight="500" text-anchor="middle">${st.desc}</text>
  </svg>`;
}

const stage = document.getElementById("stage");
const tabsEl = document.getElementById("tabs");
let current = 0;

function render(idx){
  current = idx;
  const doc = new DOMParser().parseFromString(cardMarkup(STATES[idx], idx), "image/svg+xml");
  stage.replaceChildren(doc.documentElement);   // 한 번에 하나만 마운트 → CSS 충돌 차단
  [...tabsEl.children].forEach((b,i)=>b.classList.toggle("on", i===idx));
}

STATES.forEach((st,i)=>{
  const b = document.createElement("button");
  b.textContent = `${i+1}. ${st.label}`;
  b.onclick = ()=>render(i);
  tabsEl.appendChild(b);
});

// ---- PNG (카드 SVG 래스터화) ----
function rasterize(idx, scale){
  return new Promise((resolve, reject)=>{
    const doc = new DOMParser().parseFromString(cardMarkup(STATES[idx], idx), "image/svg+xml");
    const xml = new XMLSerializer().serializeToString(doc.documentElement);
    const url = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(xml)));
    const img = new Image();
    img.onload = ()=>{
      const c = document.createElement("canvas");
      c.width = SIZE*scale; c.height = SIZE*scale;
      const ctx = c.getContext("2d");
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, 0, 0, c.width, c.height);
      c.toBlob(b=>resolve(b), "image/png");
    };
    img.onerror = ()=>reject(new Error("svg load fail"));
    img.src = url;
  });
}
function triggerDownload(blob, name){
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
}
const getScale = ()=>parseInt(document.getElementById("scale").value,10);

document.getElementById("dl").onclick = async ()=>{
  const st = STATES[current];
  triggerDownload(await rasterize(current, getScale()), `hongsi-${String(current+1).padStart(2,"0")}-${st.key}.png`);
};
document.getElementById("dlAll").onclick = async ()=>{
  const s = getScale();
  for (let i=0;i<STATES.length;i++){
    triggerDownload(await rasterize(i, s), `hongsi-${String(i+1).padStart(2,"0")}-${STATES[i].key}.png`);
    await new Promise(r=>setTimeout(r, 350));
  }
};

// ---- 캡처 모드(?capture=1&state=key): 카드만 풀블리드 ----
const params = new URLSearchParams(location.search);
if (params.get("capture")==="1"){
  document.body.classList.add("capture");
  const key = params.get("state");
  const i = Math.max(0, STATES.findIndex(s=>s.key===key));
  render(i);
} else {
  render(0);
}
window.hongsiRender = render;   // 외부 제어용
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
