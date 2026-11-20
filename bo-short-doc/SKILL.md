---
name: bo-short-doc
description: BỘ SHORT DỌC - đưa video thô talking-head (người nói trước camera) vào, ra short 9:16 1080x1920 hoàn thiện cho TikTok/Reels/Shorts. Tự chạy phân cảnh, âm thanh, màu, chuẩn khung, zoom/chuyển cảnh, chữ/icon/ảnh minh hoạ, QC. Người dùng chỉ cần nói video thô + phong cách (sang, nhịp nhanh, đời thường). Dùng khi nói "làm short", "làm reels/tiktok", "edit clip dọc", "đưa video thô, ra video hoàn chỉnh".
---

# Bộ Short dọc

Đầu vào: video thô + (tuỳ chọn) chủ đề, phong cách, nhạc. Đầu ra: `final_short.mp4` 1080x1920 + ảnh kiểm + `qc.json`.

## Quy trình
1. **Cắt ghép trước** nếu video thô có vấp/lặp/khoảng lặng dài: dùng `edit-video-toan-dien` (giai đoạn A) rồi lấy bản đã cắt làm đầu vào. Đã gọn thì bỏ qua.
2. **Phân cảnh** để hiểu nội dung:
   ```bash
   python -I "D:\EDIT VIDEO CLAUDE\SKILLS-AI\video-thu-thap-phan-canh\scripts\ingest.py" "<video>" --out "<DIR>"
   ```
   Đọc `scenes.json`, sửa chỗ nghe sai tên/thuật ngữ, xem vài ảnh cảnh.
3. **Viết `items.json`** (chữ/icon/ảnh nhấn) từ scenes: ≤1 chữ nhấn (≤5 từ) mỗi 8–10s, icon 0–1, ảnh minh hoạ chỉ khi đúng ý (tìm bằng `video-footage-tu-tim`, xem ảnh bằng mắt). Chọn style chữ theo phong cách: `sang` → `serif`; `nhanh` → `bold`; `doi-thuong` → `pill`. Hook: cụm chữ lớn ở 1–3 giây đầu.
4. **Chạy bộ:**
   ```bash
   python -I "D:\EDIT VIDEO CLAUDE\SKILLS-AI\bo-short-doc\scripts\short.py" "<video>" --dir "<DIR>" --style nhanh|sang|doi-thuong [--items items.json] [--music nhac.mp3] --out "<final.mp4>"
   ```
   Chuỗi: âm thanh (khử ồn, EQ, −14 LUFS, nhạc ducking) → màu (tự cân sáng, da) → chuẩn 1080x1920 → zoom/chuyển cảnh → chữ/icon/ảnh → QC.
5. **Xem ảnh kiểm** (`DIR/qc/qc_1..8.jpg`, ghép bằng `ffmpeg tile`): chữ đọc được, không đè mặt, đúng vùng an toàn, dấu đúng. Sửa `items.json`/`plan_fx.json` rồi chạy lại (các bước trung gian `s1_…s4_…` nằm trong DIR).
6. **Giao:** đường dẫn file, các lựa chọn mặc định đã áp, điều chưa kiểm (**chưa nghe bằng tai**), nguồn ảnh nếu có. Muốn gói đủ: `video-xuat-ban-qc export.py handover`.

## Phong cách → thông số
| Style | Màu | Zoom tối đa | Chuyển cảnh | Chữ |
|---|---|---|---|---|
| `sang` | natural + da nhẹ | 1.15 | thưa (1/3 mốc) | serif trắng, ít |
| `nhanh` | bright | 1.25 | dày | bold vàng |
| `doi-thuong` | natural | 1.10 | thưa | pill đen gọn |

## Lưu ý
- Không dùng thêm hệ chữ khác (`edit-video-cao-cap`, `edit-video-sub-va-hieu-ung`) lên cùng đoạn. Muốn sub karaoke cả video thì dùng skill đó thay bước 6 và bỏ `--items`.
- Nguồn dưới 1080p được nâng lên chuẩn (chất lượng không tăng thêm); báo người dùng.
- Nếu nguồn không phải 9:16, bước chuẩn khung dùng nền mờ, không cắt người.

## Đo thời gian từng bước
`short.py` in bảng thời gian từng bước và ghi `DIR/timings.json` (đã thử: bước chuẩn 1080×1920 chiếm ~48%, zoom ~35% trên clip 8s). Muốn nhanh hơn, giảm `--crf`/đổi `-preset` hoặc bỏ bước không cần; dùng bảng này để tối ưu quy trình trước khi đổi.

## Phụ đề và sửa chính tả
`short.py ... --captions [style] [--fixes fixes.json]` — đốt phụ đề karaoke sau cùng (style chữ: bold, impact, gilroy, poppins…; font từ thư viện của người dùng). `--fixes` là từ điển `{"sai":"đúng"}` áp lên `words.json` trước khi đốt (từ khoá như "Tên Thương Hiệu"). Cần phiên âm: không dùng `--no-asr`. Phụ đề và chữ nhấn (`--items`) dùng chung vùng dưới/trên: chữ nhấn đặt `top/upper`, không `lower`.
