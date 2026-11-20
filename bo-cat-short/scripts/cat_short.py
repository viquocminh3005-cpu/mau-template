#!/usr/bin/env python
"""BỘ CẮT SHORT HÀNG LOẠT: video dài -> nhiều short dọc 9:16, mỗi short có hook, âm thanh/màu/khung chuẩn, QC.
  cat_short.py pick  <scenes.json> --out clips.json [--min 45 --max 90 --n 5 --keywords a,b,c]   gợi ý đoạn hay (cắt đúng chỗ ngắt câu)
  cat_short.py build <video> --dir DIR --clips clips.json [--style nhanh|sang|doi-thuong] [--music nhac.mp3]
Quy trình: ingest video dài (video-thu-thap-phan-canh) -> pick -> Claude duyệt/sửa clips.json (title, hook) -> build.
clips.json: [{"id":1,"start":120.4,"end":185.0,"title":"...","hook":"CHỮ HOOK NGẮN","score":7,"reason":"..."}]
"""
import argparse, json, os, re, subprocess, sys, unicodedata
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SK = os.environ.get("SKILLS_AI") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = [sys.executable, "-I"]
HOOK_CUES = ["tai sao", "bi quyet", "su that", "dung", "sai lam", "bi mat", "khong ai", "cach", "dieu", "vi sao", "nguy hiem", "bao nhieu",
             "quan trong", "dau tien", "thu nhat", "mien phi", "bat ngo", "that ra"]

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")

def run(cmd, **k):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **k)

def score_window(ws, kws):
    text = norm(" ".join(s["text"] for s in ws)); first = norm(ws[0]["text"])
    dur = ws[-1]["end"] - ws[0]["start"]; words = len(text.split())
    sc = 0.0
    sc += 2.0 * sum(1 for c in HOOK_CUES if c in first)          # mở bằng câu gây tò mò
    sc += 1.0 * len(re.findall(r"\d+", first))                    # có con số ngay đầu
    sc += 1.5 if "?" in ws[0]["text"] else 0
    sc += 1.0 * sum(text.count(norm(k)) for k in kws)             # đúng chủ đề người dùng quan tâm
    wps = words / max(dur, 1)
    sc += 1.5 if 2.2 <= wps <= 3.8 else 0                         # nhịp nói đều, không lặng/lắp
    sc += 1.0 if ws[-1]["text"].rstrip()[-1:] in ".!?" else 0     # kết ở cuối câu trọn ý
    return round(sc, 2)

def cmd_pick(scenes_json, out, mn, mx, n, kws):
    d = json.load(open(scenes_json, encoding="utf-8-sig")); sc = d["scenes"]; cands = []
    for i in range(len(sc)):
        for j in range(i, len(sc)):
            dur = sc[j]["end"] - sc[i]["start"]
            if dur > mx: break
            if dur >= mn:
                ws = sc[i:j + 1]; cands.append((score_window(ws, kws), sc[i]["start"], sc[j]["end"], ws))
    cands.sort(key=lambda c: -c[0]); chosen = []
    for s, a, b, ws in cands:  # chọn từ điểm cao xuống, không chồng lấn đoạn đã chọn
        if all(b <= c["start"] or a >= c["end"] for c in chosen):
            first = ws[0]["text"].strip(); hook = " ".join(first.replace("?", "").split()[:7]).upper()
            chosen.append({"id": len(chosen) + 1, "start": round(a, 2), "end": round(b, 2), "score": s, "title": first[:60], "hook": hook,
                           "reason": "mở câu hook/có số/đúng từ khoá; nhịp nói đều; kết trọn câu"})
        if len(chosen) >= n: break
    chosen.sort(key=lambda c: c["start"])
    for i, c in enumerate(chosen, 1): c["id"] = i
    json.dump(chosen, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(chosen)} đoạn gợi ý -> {out}")
    for c in chosen: print(f"  #{c['id']} {c['start']:7.1f}-{c['end']:7.1f} ({c['end'] - c['start']:.0f}s) điểm {c['score']}  {c['title']}")
    print("Hook là chữ GỢI Ý tự động: hãy viết lại cho gọn, gây tò mò (≤7 từ) trước khi build.")

def clip_scenes(parent, a, b):
    """scenes.json của riêng đoạn: dịch mốc về 0, bỏ cảnh ngoài đoạn."""
    sc = []
    for s in parent["scenes"]:
        if s["end"] <= a or s["start"] >= b: continue
        st, en = max(s["start"], a) - a, min(s["end"], b) - a
        sc.append({**{k: v for k, v in s.items() if k != "thumb"}, "id": len(sc) + 1, "start": round(st, 2), "end": round(en, 2), "duration": round(en - st, 2)})
    info = dict(parent["info"]); info["duration"] = round(b - a, 2)
    return {"source": "clip", "info": info, "visual_cuts": [], "scenes": sc}

def cmd_build(video, d, clips_json, style, music):
    clips = json.load(open(clips_json, encoding="utf-8-sig")); os.makedirs(d, exist_ok=True)
    scj = os.path.join(d, "scenes.json")
    if not os.path.exists(scj):
        r = subprocess.run(PY + [os.path.join(SK, "video-thu-thap-phan-canh/scripts/ingest.py"), video, "--out", d, "--max", "20"]); r.check_returncode()
    parent = json.load(open(scj, encoding="utf-8-sig")); out_rows = []
    for c in clips:
        cd = os.path.join(d, f"short_{c['id']:02d}"); os.makedirs(cd, exist_ok=True)
        raw = os.path.join(cd, "raw.mp4"); a, b = c["start"], c["end"]
        r = run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", video, "-af", f"afade=t=in:d=0.04,afade=t=out:st={b - a - 0.08}:d=0.08",
                 "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", raw])
        if r.returncode: print(f"  #{c['id']} cắt lỗi: {r.stderr[-300:]}"); continue
        json.dump(clip_scenes(parent, a, b), open(os.path.join(cd, "scenes.json"), "w", encoding="utf-8"), ensure_ascii=False)
        dur = b - a; items = []
        if c.get("hook"): items.append({"type": "text", "text": c["hook"], "t0": 0.2, "t1": min(3.4, dur - 0.5), "style": "bold", "slot": "top"})
        if c.get("cta"): items.append({"type": "text", "text": c["cta"], "t0": round(dur - 3.5, 2), "t1": round(dur - 0.1, 2), "style": "pill", "slot": "upper"})
        ij = os.path.join(cd, "items.json"); json.dump({"items": items}, open(ij, "w", encoding="utf-8"), ensure_ascii=False)
        out = os.path.join(d, f"short_{c['id']:02d}.mp4")
        cmd = PY + [os.path.join(SK, "bo-short-doc/scripts/short.py"), raw, "--dir", cd, "--style", c.get("style") or style, "--items", ij, "--out", out]
        if music: cmd += ["--music", music]
        print(f"\n########## Short #{c['id']}: {c.get('title', '')[:50]} ({dur:.0f}s) ##########", flush=True)
        rc = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace").returncode
        out_rows.append((c["id"], out, rc, c.get("title", ""), c.get("hook", "")))
        with open(os.path.join(d, f"short_{c['id']:02d}_mota.txt"), "w", encoding="utf-8") as f:  # tiêu đề + mô tả để đăng
            f.write(f"TIÊU ĐỀ: {c.get('title', '')}\nHOOK: {c.get('hook', '')}\nĐOẠN GỐC: {a:.1f}s–{b:.1f}s\n")
    print("\n===== TỔNG KẾT =====")
    for i, o, rc, t, h in out_rows: print(f"  #{i}: {o}  QC={'PASS/WARN' if rc == 0 else 'FAIL'}  hook='{h}'")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("pick"); p.add_argument("scenes"); p.add_argument("--out", required=True)
    p.add_argument("--min", type=float, default=45); p.add_argument("--max", type=float, default=90); p.add_argument("--n", type=int, default=5)
    p.add_argument("--keywords", default="")
    p = sp.add_parser("build"); p.add_argument("video"); p.add_argument("--dir", required=True); p.add_argument("--clips", required=True)
    p.add_argument("--style", default="nhanh"); p.add_argument("--music")
    a = ap.parse_args()
    if a.c == "pick": cmd_pick(a.scenes, a.out, a.min, a.max, a.n, [k for k in a.keywords.split(",") if k])
    else: cmd_build(os.path.abspath(a.video), os.path.abspath(a.dir), a.clips, a.style, a.music)

if __name__ == "__main__":
    main()
