// 홍시 상태별 9장 PNG + 모션 MP4 일괄 생성.
//   PNG : 카드 SVG를 페이지 내에서 canvas 래스터화 (정지 스냅샷)
//   MP4 : Playwright가 실제 CSS 애니 재생 프레임을 webm 녹화 → ffmpeg로 mp4(h264) 변환
//         (브라우저 단독으로는 SVG 애니를 영상으로 굽지 못해 이 경로가 필요)
// 사용: node render-all.mjs           (PNG+MP4 전부)
//      node render-all.mjs --png      (PNG만)
//      node render-all.mjs --mp4      (MP4만)
// 출력: ./out/hongsi-NN-<state>.png|.mp4

import { createRequire } from "module";
import { fileURLToPath, pathToFileURL } from "url";
import { execFileSync } from "child_process";
import path from "path";
import fs from "fs";

const require = createRequire(import.meta.url);
// npx 캐시에 설치된 playwright 사용 (전역/로컬 어디든 해석)
const { chromium } = require(
  process.env.PLAYWRIGHT_PATH ||
  "/Users/supercent/.npm/_npx/e41f203b7505f1fb/node_modules/playwright"
);

const HERE = path.dirname(fileURLToPath(import.meta.url));
const HTML = pathToFileURL(path.join(HERE, "hongsi-states-card.html")).href;
const STATES = JSON.parse(fs.readFileSync(path.join(HERE, "states.json"), "utf-8"));
const OUT = path.join(HERE, "out");
const TMP = path.join(HERE, ".vid-tmp");

const args = process.argv.slice(2);
const doPNG = !args.includes("--mp4");
const doMP4 = !args.includes("--png");
const PNG_SCALE = 2;       // 2160px
const VIDEO_SECONDS = 6;   // 상태별 녹화 길이

const SIZE = 1080;
const pad2 = (n) => String(n).padStart(2, "0");
const stem = (i, st) => `hongsi-${pad2(i + 1)}-${st.key}`;

fs.mkdirSync(OUT, { recursive: true });

async function renderPNG(browser, i, st) {
  const page = await browser.newPage({ viewport: { width: SIZE, height: SIZE } });
  await page.goto(`${HTML}?capture=1&state=${st.key}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(250);
  const b64 = await page.evaluate(async (scale) => {
    const svg = document.getElementById("card-svg");
    const xml = new XMLSerializer().serializeToString(svg);
    const url = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(xml)));
    const img = new Image();
    await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = url; });
    const S = 1080, c = document.createElement("canvas");
    c.width = S * scale; c.height = S * scale;
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return c.toDataURL("image/png").split(",")[1];
  }, PNG_SCALE);
  const file = path.join(OUT, `${stem(i, st)}.png`);
  fs.writeFileSync(file, Buffer.from(b64, "base64"));
  await page.close();
  return file;
}

async function renderMP4(browser, i, st) {
  const ctx = await browser.newContext({
    viewport: { width: SIZE, height: SIZE },
    recordVideo: { dir: TMP, size: { width: SIZE, height: SIZE } },
  });
  const page = await ctx.newPage();
  await page.goto(`${HTML}?capture=1&state=${st.key}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(VIDEO_SECONDS * 1000);
  await page.close();
  await ctx.close();                 // close 후에야 webm 파일이 flush됨
  const webm = await page.video().path();
  const mp4 = path.join(OUT, `${stem(i, st)}.mp4`);
  // h264 + yuv420p = LinkedIn/모든 플레이어 호환. 짝수 해상도 보장.
  execFileSync("ffmpeg", [
    "-y", "-i", webm,
    "-movflags", "+faststart",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1080:1080:flags=lanczos,fps=30",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20",
    "-an", mp4,
  ], { stdio: ["ignore", "ignore", "inherit"] });
  fs.rmSync(webm, { force: true });
  return mp4;
}

const browser = await chromium.launch();
try {
  for (let i = 0; i < STATES.length; i++) {
    const st = STATES[i];
    const made = [];
    if (doPNG) made.push(path.basename(await renderPNG(browser, i, st)));
    if (doMP4) made.push(path.basename(await renderMP4(browser, i, st)));
    console.log(`[${i + 1}/${STATES.length}] ${st.label.padEnd(6)} → ${made.join(" + ")}`);
  }
} finally {
  await browser.close();
  fs.rmSync(TMP, { recursive: true, force: true });
}
console.log(`\n완료 → ${OUT}`);
