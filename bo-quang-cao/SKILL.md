---
name: bo-quang-cao
description: BỘ QUẢNG CÁO / MARKETING - đưa video thô (talking-head, demo sản phẩm, UGC) và brief ngắn, ra video quảng cáo 9:16 hoàn thiện với hook 1-3 giây, lợi ích, bằng chứng thật, CTA; tạo nhiều phiên bản A/B (đổi hook/CTA/phong cách), bản rút gọn 15-30 giây, và soát lời quảng cáo rủi ro. Dùng khi người dùng nói "làm video quảng cáo", "video bán hàng", "ads TikTok/Facebook/Reels", "hook + CTA", "tạo bản A/B", "rút gọn thành 15 giây", "UGC", "problem-solution", "demo sản phẩm".
---

# Bộ Quảng cáo

Nền là `bo-short-doc` (âm thanh, màu, khung, zoom, chữ, QC) cộng lớp **kịch bản quảng cáo** + A/B + rút gọn + soát lời. Script: `scripts/ad.py`.

## Đầu vào cần có (hỏi nếu thiếu, không tự bịa)
1. Video thô (hoặc nhiều đoạn đã cắt).
2. **Brief** (người dùng nói miệng, em ghi thành `brief.json`): sản phẩm, hook, 2–4 lợi ích, lời kêu gọi (CTA), màu thương hiệu, và bằng chứng *thật* nếu có.
3. Nền tảng/độ dài mục tiêu: mặc định 9:16, 20–45 giây (Reels/TikTok/Facebook).

## Quy tắc nội dung
- **Chỉ dùng số liệu, đánh giá, tên khách hàng, kết quả do người dùng cung cấp.** Không tự bịa "10.000 khách tin dùng", "tăng 300% doanh thu", review giả. Không có bằng chứng thì bỏ mục bằng chứng.
- Chạy `ad.py lint` trước khi dựng: bắt cam kết tuyệt đối ("100%", "chắc chắn"), so sánh tuyệt đối ("số 1", "tốt nhất"), tuyên bố y tế/sức khoẻ, thu nhập/tài chính, khuyến mãi tuyệt đối. Cảnh báo = báo người dùng và đề xuất cách viết nhẹ hơn (có căn cứ, có điều kiện), không tự ý bỏ.
- Hook trong 1–3 giây đầu, nói thẳng lợi ích hoặc đánh vào vấn đề; không chào hỏi dài. CTA cụ thể, một hành động duy nhất.

## Khung kịch bản (chọn theo loại)
| Loại | Cấu trúc | Chữ/minh hoạ |
|---|---|---|
| **Problem–Solution** | Hook vấn đề (0–3s) → hậu quả (3–8s) → giải pháp/sản phẩm → 2–3 lợi ích → CTA | hook to, lợi ích dạng ✓, CTA cuối |
| **Demo sản phẩm** | Hook kết quả → demo thao tác → lợi ích từng bước → CTA | zoom vào thao tác, mũi tên chỉ, ảnh/screen chèn (footage) |
| **UGC / trải nghiệm** | Mở bằng câu nói tự nhiên → kể trải nghiệm → kết quả → CTA mềm | ít chữ, style `doi-thuong`, không zoom mạnh |
| **Social proof** | Hook kết quả → bằng chứng THẬT (lower third nguồn) → lợi ích → CTA | chỉ khi có dữ liệu thật |
| **Giới thiệu chuyên gia** | Hook câu hỏi → kiến thức → uy tín (lower third tên/chức danh) → CTA | style `sang` |

## Quy trình
1. **Cắt ghép** (nếu cần) bằng `edit-video-toan-dien`; đã gọn thì bỏ qua.
2. Ghi `brief.json` → `ad.py lint brief.json`, xử lý cảnh báo cùng người dùng.
3. (Tuỳ chọn) rút gọn: `ad.py cutdown video scenes.json --len 20 --out cut.mp4 --brief brief.json` (giữ cảnh mở, cảnh nhiều lợi ích, cảnh chốt). Phân cảnh lại trên bản rút gọn.
4. Dựng: `ad.py build video --dir DIR --brief brief.json [--style nhanh|sang|doi-thuong] [--music nhac.mp3]`
   - `variants` trong brief = bản A/B (đổi `hook`, `cta`, `style`): mỗi biến thể ra `DIR/ad_<tên>.mp4` có QC riêng.
   - Hoặc `ad.py plan scenes.json brief.json DIR` chỉ sinh `items_<tên>.json` để chỉnh tay rồi chạy `bo-short-doc/short.py --items`.
5. Xem ảnh kiểm (`DIR/var_*/qc/`): hook đọc được trong 1 giây, lợi ích không đè mặt, CTA trong vùng an toàn, dấu tiếng Việt đúng. Chỉnh `items.json` rồi chạy lại.
6. Footage minh hoạ/ảnh sản phẩm: `video-footage-tu-tim`; hiệu ứng (freeze, tăng tốc, before/after): `video-hieu-ung-nang-cao` (làm trước khi phủ chữ).
7. Giao: các phiên bản, khác biệt giữa chúng (để thử nghiệm), cảnh báo lời quảng cáo còn lại, **chưa nghe bằng tai**. Không đăng/chạy quảng cáo thay người dùng.

## A/B hợp lý
Chỉ đổi **một yếu tố** mỗi cặp (hook, hoặc CTA, hoặc phong cách) để biết cái nào thắng. Đặt tên biến thể rõ (`A-hook-loiich`, `B-hook-vande`). Đọc số liệu quảng cáo (nếu người dùng cung cấp) để điều chỉnh vòng sau; không tự suy ra kết quả.

## Giới hạn
Chưa tự quay/tạo hình sản phẩm; ảnh sản phẩm người dùng cung cấp hoặc tìm ảnh minh hoạ miễn phí (kiểm giấy phép, không dùng logo/ảnh thương hiệu khác). Chữ phủ không thay thế voice-over: video không có tiếng thì cần file voice (Edge TTS có sẵn trong `tao-video-giai-thich-noi-bat`).
