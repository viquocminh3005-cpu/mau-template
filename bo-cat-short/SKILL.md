---
name: bo-cat-short
description: BỘ CẮT SHORT HÀNG LOẠT - từ một video dài (podcast, livestream, bài giảng, phỏng vấn, video YouTube) tự gợi ý các đoạn hay, cắt đúng chỗ ngắt câu, rồi dựng từng đoạn thành short dọc 9:16 có hook, âm thanh/màu/khung chuẩn và QC; xuất kèm file mô tả tiêu đề. Dùng khi người dùng nói "cắt video dài thành nhiều short", "tách clip hay", "làm series short/Reels/TikTok từ video này", "lấy 5 đoạn hay nhất".
---

# Bộ Cắt short hàng loạt

Nền là `bo-short-doc` (mỗi short đi qua cùng chuỗi âm thanh → màu → 1080x1920 → zoom → chữ → QC). Script: `scripts/cat_short.py`.

## Quy trình
1. **Phân cảnh cả video dài** (có phiên âm):
   ```bash
   python -I "D:/EDIT VIDEO CLAUDE/SKILLS-AI/video-thu-thap-phan-canh/scripts/ingest.py" "<video dài>" --out "<DIR>" --max 20
   ```
   Video dài (>20 phút) phiên âm lâu (CPU): chạy nền, báo người dùng ước lượng; có GPU thì nhanh hơn nhiều.
2. **Gợi ý đoạn hay:**
   ```bash
   python -I cat_short.py pick "<DIR>/scenes.json" --out "<DIR>/clips.json" --min 45 --max 90 --n 6 --keywords "chủ đề,từ khoá"
   ```
   Chấm điểm: mở bằng câu gây tò mò/câu hỏi/số liệu, có từ khoá người dùng quan tâm, nhịp nói đều, kết trọn câu; không chồng lấn; luôn cắt ở ranh giới câu.
3. **Duyệt bằng mắt/tai (bắt buộc):** đọc `text` của từng đoạn đề xuất, bỏ đoạn thiếu ngữ cảnh ("như đã nói ở trên", "cái này", nói dở ý), đoạn nhạy cảm hoặc lỗi nói. Điều chỉnh `start/end` nếu cần cho trọn ý. **Viết lại `hook`** (≤7 từ, in hoa, gây tò mò hoặc nêu lợi ích), thêm `title`; `cta` (tuỳ chọn) cho đoạn cuối series. Hỏi người dùng nếu chọn đoạn có thông tin cá nhân/khách hàng.
4. **Dựng hàng loạt:**
   ```bash
   python -I cat_short.py build "<video dài>" --dir "<DIR>" --clips "<DIR>/clips.json" [--style nhanh|sang|doi-thuong] [--music nhac.mp3]
   ```
   Mỗi đoạn ra `DIR/short_NN.mp4` + `short_NN_mota.txt` (tiêu đề, hook, mốc gốc), QC riêng. Nguồn không phải 9:16 thì nền mờ, không cắt người (muốn lấp đầy khung theo mặt: dùng `edit-video-cao-cap/scripts/reframe.py` trước).
5. **Xem ảnh kiểm** `DIR/short_NN/qc/` của từng short; sửa `clips.json` rồi chạy lại đoạn lỗi (xoá file `short_NN.mp4` đó hoặc dùng clips.json chỉ chứa đoạn cần làm lại).
6. Giao: danh sách short (độ dài, hook, mốc gốc), cảnh báo QC, điều chưa kiểm (**chưa nghe bằng tai**, chưa có phụ đề từng chữ).

## Lưu ý
- **Phụ đề:** bộ này chưa đốt sub cả video. Short cần sub thì chạy `edit-video-sub-va-hieu-ung` (karaoke vàng) hoặc `edit-video-cao-cap` trên từng `short_NN.mp4` (không dùng chữ hook của bộ này cùng lúc nếu trùng vị trí), hoặc xuất `.srt` bằng `video-xuat-ban-qc export.py srt`.
- Skill `edit-video-toan-dien/scripts/shorts.py` là cách cắt khác (cắt theo luật skill gốc); bộ này dùng khi cần chấm điểm + dựng hoàn thiện một lệnh.
- Độ dài mặc định 45–90s; Reels/Shorts tối ưu 30–60s (đặt `--min 30 --max 60`).
- Cắt từ nội dung của người khác: chỉ khi người dùng có quyền sử dụng video gốc.
- Hook gợi ý tự động chỉ là bản nháp: không đăng mà chưa viết lại.
