---
name: video-mau-template
description: Mẫu dựng (template) dùng lại, quản lý phiên bản video và theo dõi phản hồi/sửa - có sẵn 6 mẫu (short sang, short nhanh, short đời thường, quảng cáo vấn đề-giải pháp, YouTube podcast, cắt short 60s), lưu mẫu riêng, chạy một lệnh theo mẫu, ghi phiên bản v001, v002 (không tốn thêm dung lượng), ghi phản hồi của khách theo mốc thời gian và danh sách việc còn phải sửa. Dùng khi người dùng nói "dùng mẫu", "lưu mẫu này", "làm lại như video trước", "quản lý phiên bản", "bản v2", "khách góp ý", "danh sách cần sửa", "tối ưu quy trình".
---

# Mẫu dựng · phiên bản · phản hồi

Script `scripts/tpl.py`. Mẫu lưu ở `templates/*.json`.

```bash
T="D:/EDIT VIDEO CLAUDE/SKILLS-AI/video-mau-template/scripts/tpl.py"
python -I $T list
python -I $T run short-nhanh "<video>" --dir "D:/EDIT VIDEO CLAUDE/VIEC-DANG-LAM/<dự án>" [--items items.json] [--music nhac.mp3]
python -I $T run quang-cao-problem-solution "<video>" --dir DIR --brief brief.json
python -I $T save <mẫu mới> --bo short|quangcao|catshort|youtube --style nhanh|sang|doi-thuong --note "…"
python -I $T ver add DIR <file.mp4> --note "…"   |   ver list DIR
python -I $T fb add DIR "phản hồi" --at 12.5 --ver v002   |   fb list DIR   |   fb todo DIR   |   fb done DIR <id>
```

## Mẫu có sẵn
| Mẫu | Bộ | Dùng khi |
|---|---|---|
| `short-sang` | bo-short-doc | short dọc sang, nhịp thưa |
| `short-nhanh` | bo-short-doc | short dọc nhịp nhanh, chữ khối vàng |
| `short-doi-thuong` | bo-short-doc | UGC/đời thường, chữ pill gọn |
| `quang-cao-problem-solution` | bo-quang-cao | quảng cáo nhiều bản A/B (cần `brief.json`) |
| `youtube-podcast` | bo-youtube-dai | video dài 16:9, chương + SRT + thumbnail |
| `cat-short-60s` | bo-cat-short | cắt video dài thành short (cần duyệt đoạn) |

## Phiên bản
- `run` tự ghi phiên bản đầu (`DIR/versions/v001_*.mp4` + `versions.json`: thời gian, mã kiểm SHA, ghi chú). Mỗi lần xuất bản mới (sửa theo phản hồi) → `ver add`. Dùng **liên kết cứng** nên không tốn thêm dung lượng ổ D.
- Đặt ghi chú ngắn nói rõ thay đổi ("hook đổi sang vấn đề", "giảm nhạc −4 dB") để so sánh/quay lại bản cũ.

## Phản hồi & sửa
1. Nhận phản hồi (chat, email, ghi chú nghe xem): `fb add DIR "…" --at <giây> --ver vNNN`, mỗi ý một dòng.
2. `fb todo DIR` ra danh sách việc còn mở; xử lý bằng skill phù hợp (chữ → `video-minh-hoa-bo-cuc`, âm → `video-am-thanh`, màu → `video-mau-chat-luong`, nhịp → `video-zoom-chuyen-canh`…).
3. Xuất bản mới → `ver add` → `fb done DIR <id>` cho từng việc đã làm; báo người dùng các việc đã xong/chưa xong và lý do.
- Không tự quyết điểm phản hồi mâu thuẫn nhau: hỏi người dùng; không xoá phản hồi cũ.

## Lưu ý
Mẫu chỉ lưu **tham số dựng** (bộ, phong cách…), không lưu nội dung chữ: `items.json`/`brief.json` vẫn do Claude viết cho từng video.
