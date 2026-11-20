---
name: bo-giai-thich
description: BỘ GIẢI THÍCH / MOTION - từ một chủ đề, nội dung, link hoặc voice-over, ra video giải thích hoàn chỉnh. Điều phối đúng skill tạo video (giải thích nổi bật dọc 9:16, giải thích ngang 16:9 tài liệu, motion graphics có voice-over, hoạt hình người que), rồi làm bước sau chung - kiểm QC, soát giữ chân, phụ đề SRT, mô tả, bàn giao, xuất đa khung. Dùng khi người dùng nói "làm video giải thích về…", "video motion graphics từ chủ đề/link/repo", "video infographic", "làm video từ voice-over này", "video người que", "tạo video không cần quay".
---

# Bộ Giải thích / Motion

Không cần video thô: đầu vào là **chủ đề / nội dung dán vào / link / voice-over**. Bộ này chọn skill tạo video phù hợp và lo phần hậu kỳ chung. Script: `scripts/gt.py`.

## Chọn skill tạo video
| Muốn | Dùng | Cần |
|---|---|---|
| Video giải thích công nghệ/AI/repo/bài viết, dọc 45–100s, giọng đọc tự tạo | **tao-video-giai-thich-noi-bat** | chủ đề hoặc nội dung/link; Edge TTS miễn phí |
| Phim tài liệu/giải thích ngang 4–10 phút (lịch sử, khoa học, kinh tế, công nghệ) có bản đồ, số liệu, ảnh thật | **tao-video-giai-thich** | chủ đề; ưu tiên chạy Opus 5.5+; internet cho ảnh Wikimedia |
| Hoạt hình minh hoạ (giấy nhăn + đạo cụ / đồ hoạ phẳng) khớp voice-over | **tao-video-motion-graphics** | **file voice-over do người dùng cung cấp** |
| Hoạt hình người que từ voice-over | **tao-video-nguoi-que** | **file voice-over** |
Người dùng không nói rõ → dọc/ngắn/mạng xã hội = `noi-bat`; ngang/dài/YouTube = `giai-thich`; có sẵn voice = `motion-graphics`/`nguoi-que`.

## Quy trình
1. **Chốt đầu vào:** chủ đề + góc nhìn + đối tượng + độ dài + khung hình. Nội dung có số liệu/ngày tháng: kiểm nguồn chính, ghi `SOURCES.md` (skill con làm); không tự bịa số liệu. Chủ đề thiếu rõ thì hỏi một lần.
2. **Chạy skill con** theo SKILL.md của nó (nghiên cứu → kịch bản → giọng → hoạt cảnh → render). Dự án và video xuất nằm trên ổ D (`noi-bat`: `D:\EDIT VIDEO CLAUDE\VIDEO-XUAT\tao-video-giai-thich-noi-bat\<slug>`; các skill khác: đặt thư mục ra `D:\EDIT VIDEO CLAUDE\VIEC-DANG-LAM\<dự án>`). Thương hiệu: dùng đúng tên người dùng cung cấp, không tự gắn tên/logo khác.
3. **Hậu kỳ chung (script `gt.py`):**
   ```bash
   python -I "D:/EDIT VIDEO CLAUDE/SKILLS-AI/bo-giai-thich/scripts/gt.py" finish "<video.mp4>" --ratio 9:16|16:9 --out "<thư mục bàn giao>" [--srt "<subtitles.srt>"]
   ```
   Chạy QC (giải mã, khung, −14 LUFS, khoảng lặng, khung đen), trích 8 khung, soát retention (vùng chết), gom `BAN_GIAO/` (video, SRT, ảnh kiểm, báo cáo, ghi chú).
4. **Xem khung hình** (≥8) và đối chiếu lời: chữ không tràn/đè, dấu tiếng Việt đúng, số liệu đúng nguồn, ảnh đúng chủ đề. **Nghe lại** (em chưa nghe được): phát âm TTS, từ viết tắt, số.
5. **Xuất thêm khung** nếu cần: `video-xuat-ban-qc export.py fmt … --ratio 1:1|4:5|16:9` (cắt hoặc nền mờ). Đổi khung xong kiểm lại chữ trong vùng an toàn.
6. Muốn chèn đoạn giải thích vào video quay sẵn: xuất clip rồi dùng `video-footage-tu-tim insert` hoặc `video-hieu-ung-nang-cao` (PiP/split).

## Lưu ý
- TTS Edge cần internet, thỉnh thoảng từ chối ngẫu nhiên (tự thử lại; câu bị từ chối mãi thì viết lại câu).
- Thời gian render: ~1,5 phút/phút video; chạy nền, báo ước lượng.
- `tao-video-giai-thich` có thể nhắc đổi sang model mạnh hơn: làm theo nhắc của skill đó.
- Không đăng thay người dùng; nhạc/ảnh chỉ nguồn tự do hoặc người dùng có quyền (ghi `CREDITS.md`).
