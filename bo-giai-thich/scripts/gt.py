#!/usr/bin/env python
"""Hậu kỳ chung cho video giải thích/motion: QC + soát retention + gom bản giao.
  gt.py finish <video.mp4> --ratio 9:16|16:9 --out DIR [--srt file.srt] [--title "..."]
"""
import argparse, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SK = os.environ.get("SKILLS_AI") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = [sys.executable, "-I"]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["finish"]); ap.add_argument("video")
    ap.add_argument("--ratio", required=True, choices=["9:16", "16:9", "1:1", "4:5"]); ap.add_argument("--out", required=True)
    ap.add_argument("--srt"); ap.add_argument("--title", default="")
    a = ap.parse_args(); v = os.path.abspath(a.video); out = os.path.abspath(a.out)
    if not os.path.exists(v): sys.exit("Không thấy video: " + v)
    pk = os.path.join(out, "BAN_GIAO"); os.makedirs(os.path.join(pk, "anh_kiem"), exist_ok=True)
    shutil.copy2(v, pk)
    print("== QC =="); qc = subprocess.run(PY + [os.path.join(SK, "video-xuat-ban-qc/scripts/qc.py"), v, "--ratio", a.ratio, "--snap", os.path.join(pk, "anh_kiem"),
                                                "--json", os.path.join(pk, "qc.json")], text=True, encoding="utf-8", errors="replace")
    print("\n== Giữ chân (retention) ==")
    subprocess.run(PY + [os.path.join(SK, "video-marketing-playbook/scripts/retention.py"), v, "--json", os.path.join(pk, "retention.json")], text=True, encoding="utf-8", errors="replace")
    if a.srt and os.path.exists(a.srt): shutil.copy2(a.srt, os.path.join(pk, "phude.srt"))
    src = os.path.dirname(v)
    for fn in ("SOURCES.md", "CREDITS.md", "narration.txt", os.path.join("..", "SOURCES.md"), os.path.join("..", "CREDITS.md"), os.path.join("..", "narration.txt")):
        p = os.path.normpath(os.path.join(src, fn))
        if os.path.exists(p): shutil.copy2(p, pk)
    open(os.path.join(pk, "GHI_CHU.txt"), "w", encoding="utf-8").write(
        f"{a.title or os.path.basename(v)}\nKhung: {a.ratio}\nQC: {'FAIL' if qc.returncode else 'PASS/WARN'} (xem qc.json)\n"
        "Cần người xem/nghe: khung hình trong anh_kiem/, phát âm giọng đọc (chưa nghe bằng tai), số liệu so với SOURCES.md, giấy phép ảnh trong CREDITS.md.\n")
    print(f"\nBàn giao -> {pk}: {sorted(os.listdir(pk))}"); sys.exit(qc.returncode)

if __name__ == "__main__":
    main()
