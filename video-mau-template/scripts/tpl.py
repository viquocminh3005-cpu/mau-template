#!/usr/bin/env python
"""Mẫu dựng (template), quản lý phiên bản và theo dõi phản hồi/sửa.
  tpl.py list                                   các mẫu có sẵn
  tpl.py show <mẫu>
  tpl.py save <mẫu> --bo short|quangcao|catshort|youtube --style nhanh|sang|doi-thuong [--note "..."]   lưu mẫu riêng
  tpl.py run  <mẫu> <video> --dir DIR [--items items.json] [--brief brief.json] [--music nhac.mp3]   dựng theo mẫu rồi ghi phiên bản
  tpl.py ver add  DIR <file.mp4> [--note "..."]   ghi phiên bản (v001, v002...; liên kết cứng, không tốn thêm dung lượng)
  tpl.py ver list DIR
  tpl.py fb add   DIR "nội dung phản hồi" [--at 12.5] [--ver v002]   ghi phản hồi của khách/người dùng
  tpl.py fb list  DIR | tpl.py fb done DIR <id> | tpl.py fb todo DIR   việc còn lại cho lần sửa kế tiếp
"""
import argparse, datetime, hashlib, json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); TPL = os.path.join(HERE, "templates")
SK = os.environ.get("SKILLS_AI") or os.path.dirname(HERE); PY = [sys.executable, "-I"]

def jload(p, default=None):
    return json.load(open(p, encoding="utf-8-sig")) if os.path.exists(p) else default
def jsave(p, d): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def cmd_list():
    for f in sorted(os.listdir(TPL)):
        if f.endswith(".json"): t = jload(os.path.join(TPL, f)); print(f"{f[:-5]:26s} [{t['bo']:9s}] style={t.get('style', '-'):10s} {t.get('note', '')}")

def cmd_run(name, video, d, items, brief, music):
    t = jload(os.path.join(TPL, name + ".json"))
    if not t: sys.exit("Không có mẫu " + name)
    os.makedirs(d, exist_ok=True); bo = t["bo"]; out = os.path.join(d, f"{name}.mp4")
    if bo == "short":
        cmd = PY + [os.path.join(SK, "bo-short-doc/scripts/short.py"), video, "--dir", d, "--style", t["style"], "--out", out] + (["--items", items] if items else []) + (["--music", music] if music else [])
    elif bo == "quangcao":
        if not brief: sys.exit("Mẫu quảng cáo cần --brief brief.json")
        cmd = PY + [os.path.join(SK, "bo-quang-cao/scripts/ad.py"), "build", video, "--dir", d, "--brief", brief, "--style", t["style"]] + (["--music", music] if music else []); out = os.path.join(d, "ad_A.mp4")
    elif bo == "youtube":
        cmd = PY + [os.path.join(SK, "bo-youtube-dai/scripts/yt.py"), "build", video, "--dir", d, "--style", t["style"], "--chapter-min", str(t.get("chapter_min", 60))]; out = os.path.join(d, "final_youtube.mp4")
    elif bo == "catshort":
        sys.exit("Mẫu catshort: chạy cat_short.py pick/build theo bo-cat-short (cần duyệt đoạn)")
    else: sys.exit("bo không hỗ trợ: " + bo)
    print("Chạy:", " ".join(cmd[2:5]), "...", flush=True); rc = subprocess.run(cmd).returncode
    if rc == 0 and os.path.exists(out): ver_add(d, out, f"mẫu {name}")
    sys.exit(rc)

def ver_add(d, f, note=""):
    vp = os.path.join(d, "versions"); os.makedirs(vp, exist_ok=True); idx = os.path.join(vp, "versions.json"); log = jload(idx, [])
    n = len(log) + 1; dst = os.path.join(vp, f"v{n:03d}_{os.path.basename(f)}"); sha = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
    try: os.link(f, dst)
    except OSError: import shutil; shutil.copy2(f, dst)
    log.append({"ver": f"v{n:03d}", "file": os.path.basename(dst), "src": f, "sha": sha, "size_mb": round(os.path.getsize(f) / 1048576, 1),
                "time": datetime.datetime.now().isoformat(timespec="seconds"), "note": note}); jsave(idx, log); print(f"Ghi phiên bản v{n:03d} ({sha}) -> {dst}")

def ver_list(d):
    for v in jload(os.path.join(d, "versions", "versions.json"), []): print(f"{v['ver']}  {v['time']}  {v['size_mb']:6.1f} MB  {v['sha']}  {v['note']}")

def fb(d, cmd, a):
    p = os.path.join(d, "feedback.json"); log = jload(p, [])
    if cmd == "add":
        log.append({"id": len(log) + 1, "text": a.text, "at": a.at, "ver": a.ver, "status": "open", "time": datetime.datetime.now().isoformat(timespec="seconds")}); jsave(p, log); print(f"Ghi phản hồi #{len(log)}")
    elif cmd == "done":
        for x in log:
            if x["id"] == int(a.text): x["status"] = "done"
        jsave(p, log); print("Đã đánh dấu xong #" + a.text)
    else:
        sel = [x for x in log if cmd == "list" or x["status"] == "open"]
        for x in sel: print(f"#{x['id']} [{x['status']}] {('@' + str(x['at']) + 's ') if x.get('at') is not None else ''}{x['text']}")
        if cmd == "todo": print(f"\n{len(sel)} việc cần sửa cho phiên bản kế tiếp. Làm xong đánh dấu: tpl.py fb done DIR <id>, rồi ghi phiên bản mới.")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="c", required=True)
    sp.add_parser("list"); p = sp.add_parser("show"); p.add_argument("name")
    p = sp.add_parser("save"); p.add_argument("name"); p.add_argument("--bo", required=True); p.add_argument("--style", default="nhanh"); p.add_argument("--note", default="")
    p = sp.add_parser("run"); p.add_argument("name"); p.add_argument("video"); p.add_argument("--dir", required=True); p.add_argument("--items"); p.add_argument("--brief"); p.add_argument("--music")
    p = sp.add_parser("ver"); p.add_argument("sub", choices=["add", "list"]); p.add_argument("dir"); p.add_argument("file", nargs="?"); p.add_argument("--note", default="")
    p = sp.add_parser("fb"); p.add_argument("sub", choices=["add", "list", "done", "todo"]); p.add_argument("dir"); p.add_argument("text", nargs="?"); p.add_argument("--at", type=float); p.add_argument("--ver")
    a = ap.parse_args()
    if a.c == "list": cmd_list()
    elif a.c == "show": print(json.dumps(jload(os.path.join(TPL, a.name + ".json")), ensure_ascii=False, indent=1))
    elif a.c == "save": jsave(os.path.join(TPL, a.name + ".json"), {"bo": a.bo, "style": a.style, "note": a.note}); print("Đã lưu mẫu", a.name)
    elif a.c == "run": cmd_run(a.name, os.path.abspath(a.video), os.path.abspath(a.dir), a.items, a.brief, a.music)
    elif a.c == "ver": ver_add(a.dir, a.file, a.note) if a.sub == "add" else ver_list(a.dir)
    else: fb(a.dir, a.sub, a)

if __name__ == "__main__":
    main()
