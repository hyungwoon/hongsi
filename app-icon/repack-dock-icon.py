#!/usr/bin/env python3
"""Clawd on Desk(Electron) app.asar 안 dock 아이콘을 교체한다.

Clawd는 app.dock.setIcon(assets/dock-icon.png)로 도크 타일을 런타임에 그린다.
번들 icon.icns/Info.plist 변경으론 실행 중 도크가 안 바뀌므로, asar 안 PNG를 직접 교체해야 한다.
asar는 무결성 검증(파일별 SHA256 + Info.plist 헤더 SHA256)이 걸려 있어 모두 재계산한다.

  python3 repack-dock-icon.py selftest          # 변경 없는 재패킹=원본 동일 검증(앱 안 건드림)
  python3 repack-dock-icon.py apply <png> [app] # dock-icon.png를 <png>로 교체 + Info.plist 해시 갱신

name/productName은 의도적으로 건드리지 않는다(userData 경로가 바뀌어 로그인/설정 유실 방지).
"""
import sys, struct, json, hashlib, os, plistlib, subprocess

TARGET = "/assets/dock-icon.png"   # asar 내부 경로
BLOCK = 4194304

def load(path):
    raw = open(path, "rb").read()
    s = struct.unpack("<4I", raw[:16]); jlen = s[3]
    hdr = json.loads(raw[16:16+jlen].decode("utf-8"))
    aligned = jlen + ((4 - jlen % 4) % 4)
    return raw, hdr, 16 + aligned

def iter_files(node, prefix=""):
    for k, v in node["files"].items():
        p = prefix + "/" + k
        if "files" in v: yield from iter_files(v, p)
        else: yield p, v

def integrity(b):
    blocks = [hashlib.sha256(b[i:i+BLOCK]).hexdigest() for i in range(0, len(b), BLOCK)] or [hashlib.sha256(b"").hexdigest()]
    return {"algorithm": "SHA256", "hash": hashlib.sha256(b).hexdigest(), "blockSize": BLOCK, "blocks": blocks}

def build(asar_path, replacements):
    raw, hdr, base = load(asar_path)
    entries = sorted((int(v["offset"]), p, v) for p, v in iter_files(hdr)
                     if not v.get("unpacked") and "offset" in v)
    out = bytearray()
    for off, p, v in entries:
        if p in replacements:
            b = replacements[p]; v["size"] = len(b); v["integrity"] = integrity(b)
        else:
            b = raw[base+off : base+off+int(v["size"])]
        v["offset"] = str(len(out)); out += b
    hs = json.dumps(hdr, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    jlen = len(hs); aligned = jlen + ((4 - jlen % 4) % 4)
    blob = struct.pack("<4I", 4, aligned+8, aligned+4, jlen) + hs + b"\0"*(aligned-jlen) + bytes(out)
    return blob, hashlib.sha256(hs).hexdigest()

def selftest(asar):
    raw = open(asar, "rb").read()
    blob, _ = build(asar, {})
    ok = blob == raw
    print(f"[selftest] 변경없는 재패킹 == 원본: {ok}  ({len(blob)} vs {len(raw)} bytes)")
    if not ok:
        # 첫 차이 위치
        for i in range(min(len(blob), len(raw))):
            if blob[i] != raw[i]: print(f"  첫 차이 @ {i}"); break
    return ok

def apply(asar, png, app):
    if not selftest(asar):
        print("❌ selftest 실패 — 중단(앱 안 건드림)"); sys.exit(1)
    # 원본 dock 아이콘 백업(최초 1회, 복원용) — 현재 asar이 순정일 때 추출됨
    here = os.path.dirname(os.path.abspath(__file__))
    obak = os.path.join(here, "clawd-dock-icon-original.png")
    if not os.path.exists(obak):
        raw0, hdr0, base0 = load(asar)
        v0 = hdr0["files"]["assets"]["files"]["dock-icon.png"]
        open(obak, "wb").write(raw0[base0+int(v0["offset"]):base0+int(v0["offset"])+int(v0["size"])])
        print(f"[backup] 원본 dock 아이콘 저장: {os.path.basename(obak)}")
    newpng = open(png, "rb").read()
    blob, hhash = build(asar, {TARGET: newpng})
    # 자체검증: 재파싱해서 dock-icon이 새 png인지, 나머지는 원본과 동일한지
    raw, hdr0, base0 = load(asar)
    tmp = asar + ".new"
    open(tmp, "wb").write(blob)
    raw2, hdr2, base2 = load(tmp)
    e2 = {p: v for p, v in iter_files(hdr2)}
    for p, v in iter_files(hdr0):
        if v.get("unpacked") or "offset" not in v: continue
        b0 = newpng if p == TARGET else raw[base0+int(v["offset"]):base0+int(v["offset"])+int(v["size"])]
        v2 = e2[p]; b2 = raw2[base2+int(v2["offset"]):base2+int(v2["offset"])+int(v2["size"])]
        if b0 != b2:
            print(f"❌ 검증 실패: {p} 내용 불일치"); os.remove(tmp); sys.exit(1)
    print(f"[verify] 전 파일 무결성 OK, dock-icon → {len(newpng)} bytes")
    # Info.plist 헤더 해시 갱신
    plist_path = os.path.join(app, "Contents/Info.plist")
    with open(plist_path, "rb") as f: pl = plistlib.load(f)
    old = pl["ElectronAsarIntegrity"]["Resources/app.asar"]["hash"]
    pl["ElectronAsarIntegrity"]["Resources/app.asar"]["hash"] = hhash
    with open(plist_path, "wb") as f: plistlib.dump(pl, f)
    # asar 교체
    os.replace(tmp, asar)
    print(f"[done] asar 교체 완료, Info.plist 헤더해시 {old[:12]}… → {hhash[:12]}…")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    app = sys.argv[3] if len(sys.argv) > 3 else "/Applications/Clawd on Desk.app"
    asar = os.path.join(app, "Contents/Resources/app.asar")
    if cmd == "selftest":
        sys.exit(0 if selftest(asar) else 1)
    elif cmd == "apply":
        apply(asar, sys.argv[2], app)
    else:
        print("usage: repack-dock-icon.py [selftest | apply <png> [app]]"); sys.exit(2)
