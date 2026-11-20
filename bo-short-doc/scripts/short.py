#!/usr/bin/env python
"""BỘ SHORT DỌC: video thô talking-head -> short 9:16 hoàn thiện (1080x1920).
  short.py <video> --dir DIR [--style sang|nhanh|doi-thuong] [--items items.json] [--music nhac.mp3] [--no-asr]
                   [--look auto] [--out final.mp4]
Chuỗi: phân cảnh -> âm thanh (khử ồn, EQ, nén, -14 LUFS, nhạc ducking) -> màu -> chuẩn 1080x1920 -> zoom/chuyển cảnh
       -> chữ/icon/ảnh (items.json do Claude viết) -> QC. Mỗi bước ghi file trung gian s1..s5 trong DIR; dừng khi lỗi.
Cắt ghép (bỏ vấp/khoảng lặng) làm TRƯỚC bằng edit-video-toan-dien rồi đưa bản đã cắt vào đây.
"""
import argparse, json, os, shutil, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SK = os.environ.get("SKILLS_AI") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # thư mục chứa các skill
PY = [sys.executable, "-I"]
STYLES = {  # look màu, zoom tối đa, mật độ chuyển cảnh (1 = mọi mốc, 3 = thưa), độ trắng da
    "sang": dict(look="natural", zoom=1.15, density=3, skin=0.3, note="chữ nên dùng style serif/bold ít, nhịp thưa"),
    "nhanh": dict(look="bright", zoom=1.25, density=1, skin=0.3, note="chữ khối bold vàng, nhịp dày"),
    "doi-thuong": dict(look="natural", zoom=1.10, density=3, skin=0.2, note="chữ pill gọn, ít hiệu ứng"),
}

TIMINGS = []  # (bước, giây) -> in cuối + ghi timings.json để tối ưu quy trình

def step(name, script, args):
    print(f"\n=== {name} ===", flush=True); t0 = time.time()
    r = subprocess.run(PY + [os.path.join(SK, script)] + args, text=True, encoding="utf-8", errors="replace")
    TIMINGS.append((name, round(time.time() - t0, 1)))
    if r.returncode:
        sys.exit(f"Bước '{name}' lỗi (mã {r.returncode}). Dừng.")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("--dir", required=True)
    ap.add_argument("--style", default="nhanh", choices=STYLES); ap.add_argument("--items"); ap.add_argument("--music")
    ap.add_argument("--no-asr", action="store_true"); ap.add_argument("--out")
    ap.add_argument("--fixes", help="từ điển sửa chính tả phụ đề (JSON {\"sai\":\"đúng\"}) áp trước khi đốt phụ đề")
    ap.add_argument("--captions", nargs="?", const="bold", default=None, help="đốt phụ đề karaoke (style chữ: bold impact gilroy poppins anton roboto…; mặc định bold)")
    a = ap.parse_args()
    v = os.path.abspath(a.video); d = os.path.abspath(a.dir); os.makedirs(d, exist_ok=True)
    st = STYLES[a.style]; print(f"Phong cách '{a.style}': {st}")
    sc = os.path.join(d, "scenes.json")
    if not os.path.exists(sc):
        step("1 Phân cảnh", "video-thu-thap-phan-canh/scripts/ingest.py", [v, "--out", d] + (["--no-asr"] if a.no_asr else []))
    s1 = os.path.join(d, "s1_audio.mp4")
    step("2 Âm thanh", "video-am-thanh/scripts/audio.py", ["master", v, s1] + (["--music", a.music] if a.music else []))
    s2 = os.path.join(d, "s2_color.mp4")
    step("3 Màu + chất lượng", "video-mau-chat-luong/scripts/grade.py",
         [s1, s2, "--look", st["look"], "--auto-exposure", "--denoise", "--sharpen", "--skin", str(st["skin"])])
    s3 = os.path.join(d, "s3_1080.mp4")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", s2],
                           capture_output=True, text=True).stdout.strip().split(",")
    vertical = int(probe[1]) / int(probe[0]) > 1.7
    step("4 Chuẩn 1080x1920", "video-xuat-ban-qc/scripts/export.py",
         ["fmt", s2, s3, "--ratio", "9:16", "--fit", "crop" if vertical else "blur", "--crf", "16"])
    cur = s3
    plan = os.path.join(d, "plan_fx.json")
    step("5a Gợi ý zoom/chuyển cảnh", "video-zoom-chuyen-canh/scripts/fx.py",
         ["auto", sc, plan, "--density", str(st["density"]), "--max", str(st["zoom"])])
    s4 = os.path.join(d, "s4_fx.mp4")
    step("5b Zoom + chuyển cảnh", "video-zoom-chuyen-canh/scripts/fx.py", ["apply", cur, plan, s4]); cur = s4
    final = os.path.abspath(a.out) if a.out else os.path.join(d, "final_short.mp4")
    wj = os.path.join(d, "words.json"); cap_target = os.path.join(d, "s5_items.mp4") if a.captions else final  # có phụ đề thì phụ đề phủ SAU CÙNG
    if a.items:
        step("6 Chữ/icon/ảnh + bố cục", "video-minh-hoa-bo-cuc/scripts/overlay.py", ["render", cur, a.items, cap_target])
    else:
        shutil.copyfile(cur, cap_target)
    if a.captions:
        if not os.path.exists(wj): sys.exit("Phụ đề cần words.json (phiên âm): bỏ --no-asr hoặc chạy video-thu-thap-phan-canh ingest.py trước")
        if a.fixes:
            wf = os.path.join(d, "words_fixed.json"); step("6b Sửa chính tả phụ đề", "video-am-thanh/scripts/music.py", ["srtfix", wj, wf, "--dict", a.fixes]); wj = wf
        step("7 Phụ đề karaoke", "video-vfx-nang-cao/scripts/anim.py", ["caption", cap_target, final, "--words", wj, "--style", a.captions, "--group", "4"])
    qc = subprocess.run(PY + [os.path.join(SK, "video-xuat-ban-qc/scripts/qc.py"), final, "--ratio", "9:16", "--snap", os.path.join(d, "qc"),
                              "--json", os.path.join(d, "qc.json")], text=True, encoding="utf-8", errors="replace")
    print(f"\nXong -> {final}\nẢnh kiểm: {os.path.join(d, 'qc')}  (xem bằng mắt: chữ, đè mặt, dấu tiếng Việt). Chưa nghe bằng tai.")
    if TIMINGS:
        tot = sum(s for _, s in TIMINGS); print("\nThời gian từng bước:"); [print(f"  {n:34s} {s:7.1f}s  {s / max(tot, 1e-9) * 100:4.0f}%") for n, s in TIMINGS]
        print(f"  {'TỔNG':34s} {tot:7.1f}s → bước chậm nhất: {max(TIMINGS, key=lambda x: x[1])[0]}")
        json.dump([{"step": n, "sec": s} for n, s in TIMINGS], open(os.path.join(d, "timings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(qc.returncode)

if __name__ == "__main__":
    main()
