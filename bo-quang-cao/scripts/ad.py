#!/usr/bin/env python
"""BỘ QUẢNG CÁO: từ video thô + brief -> video quảng cáo 9:16, nhiều phiên bản A/B, bản rút gọn.
  ad.py lint    brief.json                         soát lời quảng cáo (cam kết tuyệt đối, so sánh vượt trội, y tế/tài chính...)
  ad.py plan    scenes.json brief.json out_dir     sinh items_<biến thể>.json (hook, lợi ích, bằng chứng, CTA) từ brief
  ad.py cutdown video scenes.json --len 20 --out cut.mp4 [--brief brief.json]   rút gọn: giữ hook + cảnh nhiều lợi ích + chốt
  ad.py build   video --dir DIR --brief brief.json [--style nhanh|sang|doi-thuong] [--music nhac.mp3]   chạy mọi biến thể -> DIR/ad_<tên>.mp4
brief.json: {"product","hook","hook_alt":["..."],"problem","benefits":["..",".."],"proof":"(chỉ khi có thật)","cta","brand_color":"#FFD400",
             "variants":[{"name":"A","hook":"..","style":"nhanh","cta":".."}]}
Không bao giờ tự bịa số liệu/đánh giá/khách hàng: chỉ dùng chữ người dùng cung cấp trong brief.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SK = os.environ.get("SKILLS_AI") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = [sys.executable, "-I"]

RISKY = [  # (mẫu, lý do) — soát để tránh vi phạm quy định quảng cáo/nền tảng
    (r"100\s*%|tuyệt đối|chắc chắn (có )?(hiệu quả|thành công|giàu)", "cam kết tuyệt đối/kết quả chắc chắn"),
    (r"số\s*1|số một|tốt nhất|rẻ nhất|duy nhất|hàng đầu", "so sánh/tuyệt đối hoá cần có căn cứ xác minh"),
    (r"chữa (khỏi|dứt)|điều trị|trị (dứt|khỏi)|giảm cân (nhanh|thần tốc)|tăng \d+\s*(cm|kg)", "tuyên bố y tế/sức khoẻ cần giấy phép"),
    (r"kiếm \d+|thu nhập \d+|làm giàu|x\d+ (doanh thu|tiền)|lãi \d+", "tuyên bố thu nhập/tài chính cần chứng minh"),
    (r"miễn phí 100|free 100|không mất (một )?đồng", "khuyến mãi tuyệt đối: xác minh điều kiện"),
]

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")

def lint(brief):
    texts = [brief.get(k, "") for k in ("hook", "problem", "proof", "cta")] + list(brief.get("benefits", [])) + list(brief.get("hook_alt", []))
    texts += [v.get(k, "") for v in brief.get("variants", []) for k in ("hook", "cta")]
    warn = []
    for t in texts:
        for pat, why in RISKY:
            if t and re.search(pat, t.lower()):
                warn.append(f"⚠ '{t}' → {why}")
    return warn

def variants_of(brief):
    vs = brief.get("variants") or [{"name": "A"}]
    out = []
    for i, v in enumerate(vs):
        out.append({"name": v.get("name", chr(65 + i)), "hook": v.get("hook") or brief.get("hook", ""),
                    "cta": v.get("cta") or brief.get("cta", ""), "style": v.get("style")})
    return out

def make_items(scenes, brief, v):
    sc = scenes["scenes"]; dur = scenes["info"]["duration"]; col = brief.get("brand_color", "#FFD400"); items = []
    if v["hook"]:  # hook: 1-3s đầu, to, ở trên
        items.append({"type": "text", "text": v["hook"], "t0": 0.2, "t1": 3.2, "style": "bold", "color": col, "slot": "top"})
    ben = brief.get("benefits", [])
    win0, win1 = 3.5, max(4.5, dur - 4.0)  # cửa sổ giữa hook và CTA; lợi ích hiện lần lượt, không bao giờ chồng thời gian
    slot_len = (win1 - win0) / max(1, len(ben))
    for i, b in enumerate(ben):
        t0 = round(win0 + i * slot_len + 0.2, 2); t1 = round(min(win1, t0 + min(3.4, slot_len - 0.4)), 2)
        if t1 - t0 > 1.0:
            items.append({"type": "text", "text": b, "t0": t0, "t1": t1, "style": "pill"})
            items.append({"type": "icon", "name": "check", "t0": t0, "t1": t1})
    if brief.get("proof"):  # bằng chứng: CHỈ khi người dùng cung cấp
        items.append({"type": "lower", "text": brief["proof"].replace(" - ", "|") if "|" not in brief["proof"] else brief["proof"],
                      "t0": round(max(4.0, dur * 0.55), 2), "t1": round(min(dur - 4.2, dur * 0.55 + 3.5), 2), "color": col})
    if v["cta"]:  # CTA: 3.5s cuối
        t0 = round(max(0, dur - 3.8), 2)
        items.append({"type": "text", "text": v["cta"], "t0": t0, "t1": round(dur - 0.1, 2), "style": "bold", "color": col, "slot": "upper"})
        items.append({"type": "arrow", "dir": "down", "t0": t0, "t1": round(dur - 0.1, 2), "color": "#FF3B30", "slot": "lower"})
    return [i for i in items if i["t1"] > i["t0"]]

def cmd_plan(scenes_json, brief_json, out_dir):
    scenes = json.load(open(scenes_json, encoding="utf-8-sig")); brief = json.load(open(brief_json, encoding="utf-8-sig"))
    os.makedirs(out_dir, exist_ok=True)
    for w in lint(brief): print(w)
    for v in variants_of(brief):
        p = os.path.join(out_dir, f"items_{v['name']}.json")
        json.dump({"items": make_items(scenes, brief, v)}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Biến thể {v['name']}: hook='{v['hook']}' cta='{v['cta']}' -> {p}")

def cmd_cutdown(video, scenes_json, length, out, brief_json):
    d = json.load(open(scenes_json, encoding="utf-8-sig")); sc = d["scenes"]
    kws = []
    if brief_json:
        b = json.load(open(brief_json, encoding="utf-8-sig")); kws = norm(" ".join(b.get("benefits", []) + [b.get("product", "")])).split()
    def score(s): return sum(1 for w in set(kws) if len(w) > 2 and w in norm(s["text"]))
    keep = {sc[0]["id"], sc[-1]["id"]}; total = sc[0]["duration"] + (sc[-1]["duration"] if len(sc) > 1 else 0)
    for s in sorted(sc[1:-1], key=lambda s: (-score(s), s["start"])):
        if total + s["duration"] <= length:
            keep.add(s["id"]); total += s["duration"]
    parts = [s for s in sc if s["id"] in keep]
    fc = "".join(f"[0:v]trim={p['start']}:{p['end']},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={p['start']}:{p['end']},asetpts=PTS-STARTPTS,aresample=48000[a{i}];"
                 for i, p in enumerate(parts))
    fc += "".join(f"[v{i}][a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[V][A]"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-filter_complex", fc, "-map", "[V]", "-map", "[A]", "-c:v", "libx264", "-crf", "18",
                        "-c:a", "aac", out], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode: sys.exit(r.stderr[-1200:])
    print(f"Rút gọn {total:.1f}s ({len(parts)} cảnh: {[p['id'] for p in parts]}) -> {out}. Chạy lại phân cảnh trên bản này trước khi phủ chữ.")

def cmd_build(video, d, brief_json, style, music):
    brief = json.load(open(brief_json, encoding="utf-8-sig")); os.makedirs(d, exist_ok=True)
    for w in lint(brief): print(w)
    sc = os.path.join(d, "scenes.json")
    if not os.path.exists(sc):
        subprocess.run(PY + [os.path.join(SK, "video-thu-thap-phan-canh/scripts/ingest.py"), video, "--out", d], check=True)
    scenes = json.load(open(sc, encoding="utf-8-sig")); res = []
    for v in variants_of(brief):
        vd = os.path.join(d, f"var_{v['name']}"); os.makedirs(vd, exist_ok=True)
        shutil_copy = os.path.join(vd, "scenes.json"); open(shutil_copy, "w", encoding="utf-8").write(open(sc, encoding="utf-8-sig").read())
        items = os.path.join(vd, "items.json"); json.dump({"items": make_items(scenes, brief, v)}, open(items, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        out = os.path.join(d, f"ad_{v['name']}.mp4")
        cmd = PY + [os.path.join(SK, "bo-short-doc/scripts/short.py"), video, "--dir", vd, "--style", v["style"] or style, "--items", items, "--out", out]
        if music: cmd += ["--music", music]
        print(f"\n##### Biến thể {v['name']} ({v['style'] or style}) #####", flush=True)
        r = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace"); res.append((v["name"], out, r.returncode))
    print("\nTổng kết:"); [print(f"  {n}: {o}  (QC mã {c})") for n, o, c in res]

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("lint"); p.add_argument("brief")
    p = sp.add_parser("plan"); p.add_argument("scenes"); p.add_argument("brief"); p.add_argument("out_dir")
    p = sp.add_parser("cutdown"); p.add_argument("video"); p.add_argument("scenes"); p.add_argument("--len", type=float, default=20); p.add_argument("--out", required=True); p.add_argument("--brief")
    p = sp.add_parser("build"); p.add_argument("video"); p.add_argument("--dir", required=True); p.add_argument("--brief", required=True)
    p.add_argument("--style", default="nhanh"); p.add_argument("--music")
    a = ap.parse_args()
    if a.c == "lint":
        w = lint(json.load(open(a.brief, encoding="utf-8-sig"))); print("\n".join(w) if w else "Không phát hiện lời rủi ro (vẫn cần người duyệt)")
    elif a.c == "plan": cmd_plan(a.scenes, a.brief, a.out_dir)
    elif a.c == "cutdown": cmd_cutdown(a.video, a.scenes, a.len, a.out, a.brief)
    else: cmd_build(a.video, a.dir, a.brief, a.style, a.music)

if __name__ == "__main__":
    main()
