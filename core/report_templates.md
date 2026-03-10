# LOLLIBOOKS — MẪU BÁO CÁO TELEGRAM CHO BOT ADS

> Tất cả mẫu dưới đây bot phải tuân thủ đúng format. Không được thêm bớt emoji hoặc thay đổi thứ tự section.
> Đơn vị tiền: VNĐ (VN), USD (KH/PH). Không được nhầm.

---

## 1. BÁO CÁO QUÉT ĐỊNH KỲ (mỗi 2 tiếng)

⏰ QUÉT {giờ}h — {tên tài khoản}
📅 {ngày/tháng/năm}

━━━ ❌ TẮT ━━━
• {Tên camp} → {KILL-XX}: {lý do ngắn}
 Spend: {số}k | Đơn: {số} | CPA: {số}k
• {Tên camp} → {KILL-XX}: {lý do ngắn}
 Spend: {số}k | Đơn: {số} | CPA: {số}k

━━━ 💰 REDISTRIBUTE ━━━
• {số}k từ [{camp chết}] → [{camp nhận}] (CPA {số}k)

━━━ 🚀 SCALE ━━━
• {Tên camp} tăng NS 30% ({NS cũ}k → {NS mới}k)
 CPA: {số}k | Đơn hôm nay: {số}

━━━ ⚠️ CẢNH BÁO ━━━
• {Tên camp}: Frequency {số} / CTR giảm {số}%
 → Team thay creative

━━━ TỔNG KẾT ━━━
✅ Active: {số} camp
💸 Spend hôm nay: {số}k
📦 Đơn hôm nay: {số}
📊 CPA TB tài khoản: {số}k

Ví dụ thực tế:

⏰ QUÉT 14h — Lollibooks VN 01
📅 09/03/2026

━━━ ❌ TẮT ━━━
• [VN]_0903_[VID12_GiaoVienTay]_Broad → KILL-01: Spend 155k, 0 đơn
 Spend: 155k | Đơn: 0 | CPA: --
• [VN]_0903_[VID08_HoatHinh]_Interest → KILL-03: CPA 185k, LS 3 ngày 118k
 Spend: 185k | Đơn: 1 | CPA: 185k

━━━ 💰 REDISTRIBUTE ━━━
• 45k từ [VID12_GiaoVienTay] → [VID05_GiaoVienTay] (CPA 62k)

━━━ 🚀 SCALE ━━━
• [VN]_0903_[VID05_GiaoVienTay]_Broad tăng NS 30% (150k → 195k)
 CPA: 62k | Đơn hôm nay: 3

━━━ ⚠️ CẢNH BÁO ━━━
• [VN]_0903_[VID03_Review]_Broad: Frequency 2.7 / CTR giảm 32%
 → Team thay creative

━━━ TỔNG KẾT ━━━
✅ Active: 8 camp
💸 Spend hôm nay: 520k
📦 Đơn hôm nay: 7
📊 CPA TB tài khoản: 74k

---

## 2. BÁO CÁO CAMP TIÊU CHẬM (12h trưa)

🐌 CAMP TIÊU CHẬM — 12h {ngày/tháng/năm}
TK: {tên tài khoản}

• {Tên camp}
 NS ngày: {số}k | Đã tiêu: {số}k ({số}%)
 → Chuyển {số}k vào [{camp ngon nhất}] (CPA {số}k)

• {Tên camp}
 NS ngày: {số}k | Đã tiêu: {số}k ({số}%)
 → Không có camp CPA < 105k → Giữ NS, không redistribute

📌 Tổng NS giải phóng: {số}k

---

## 3. BÁO CÁO BẬT LẠI CAMP (0h đêm)

🔄 REVIEW CAMP CŨ — 00h {ngày/tháng/năm}
TK: {tên tài khoản}

━━━ ✅ BẬT LẠI ━━━
• {Tên camp} → REVIVE-01
 CPA 3 ngày: {số}k | CPA 7 ngày: {số}k
 → Bật lại, giữ NS {số}k

• {Tên camp} → REVIVE-02
 CPA 7 ngày: {số}k (ngon) | CPA 3 ngày: {số}k (đắt)
 → Bật lại, giảm NS về $10

━━━ ☠️ CREATIVE CHẾT ━━━
• {Tên camp}: Bị tắt {số} lần / 7 ngày → Không bật lại
• {Tên camp}: Bị tắt {số} lần / 7 ngày → Không bật lại

━━━ ⏸️ GIỮ TẮT ━━━
• {Tên camp}: CPA 3 ngày {số}k, CPA 7 ngày {số}k → Chưa đủ điều kiện

📌 Tổng bật lại: {số} camp | Tổng creative chết: {số}

---

## 4. BÁO CÁO CUỐI NGÀY (23h)

📊 BÁO CÁO NGÀY — {ngày/tháng/năm}
TK: {tên tài khoản}

━━━ TỔNG QUAN ━━━
💸 Tổng spend: {số}k
📦 Tổng đơn: {số}
📊 CPA TB: {số}k
🎯 Target CPA: 105k
{✅ DƯỚI TARGET / ❌ TRÊN TARGET}: {chênh lệch}k ({số}%)

━━━ TOP 3 CAMP NGON NHẤT ━━━
🥇 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k
🥈 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k
🥉 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k

━━━ TOP 3 CAMP TỆ NHẤT ━━━
💀 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k | Lý do tắt: {KILL-XX}
💀 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k | Lý do tắt: {KILL-XX}
💀 {Tên camp}
 Spend: {số}k | Đơn: {số} | CPA: {số}k | Lý do tắt: {KILL-XX}

━━━ HÀNH ĐỘNG TRONG NGÀY ━━━
❌ Tắt: {số} camp
🚀 Scale: {số} camp
💰 Redistribute: {số}k
⚠️ Creative fatigue: {số} camp
🔄 Bật lại: {số} camp
☠️ Creative chết: {số}

━━━ DOANH THU ƯỚC TÍNH ━━━
📦 {số} đơn × 299k = {tổng}k
💸 Chi phí: {số}k
💹 ROAS: {số}x
💵 Lãi gộp ước tính: {số}k

---

## 5. BÁO CÁO TUẦN (Chủ nhật 21h)

📈 BÁO CÁO TUẦN {số tuần} — {ngày bắt đầu} → {ngày kết thúc}
TK: {tên tài khoản}

━━━ TỔNG QUAN TUẦN ━━━
💸 Tổng spend: {số}k
📦 Tổng đơn: {số}
📊 CPA TB tuần: {số}k
💹 ROAS tuần: {số}x
💵 Lãi gộp ước tính: {số}k

━━━ XU HƯỚNG CPA THEO NGÀY ━━━
T2: {số}k {'📉'/'📈'/'➡️'}
T3: {số}k {'📉'/'📈'/'➡️'}
T4: {số}k {'📉'/'📈'/'➡️'}
T5: {số}k {'📉'/'📈'/'➡️'}
T6: {số}k {'📉'/'📈'/'➡️'}
T7: {số}k {'📉'/'📈'/'➡️'}
CN: {số}k {'📉'/'📈'/'➡️'}

━━━ INSIGHT KỊCH BẢN ━━━
🏆 Nhóm thắng:
• {Mã kịch bản}: {số} đơn, CPA {số}k, spend {số}k
• {Mã kịch bản}: {số} đơn, CPA {số}k, spend {số}k

💀 Nhóm thua:
• {Mã kịch bản}: {số} đơn, CPA {số}k, spend {số}k
• {Mã kịch bản}: {số} đơn, CPA {số}k, spend {số}k

━━━ LỆNH CHO TEAM ━━━
🎬 Video: {Gợi ý cụ thể dựa trên data}
📝 Content: {Gợi ý cụ thể dựa trên data}
🎯 Targeting: {Gợi ý cụ thể dựa trên data}

━━━ SO SÁNH VỚI TUẦN TRƯỚC ━━━
Spend: {số}k → {số}k ({+/-}{số}%)
Đơn: {số} → {số} ({+/-}{số}%)
CPA: {số}k → {số}k ({+/-}{số}%)
ROAS: {số}x → {số}x ({+/-}{số}%)

---

## 6. BÁO CÁO LỖI HỆ THỐNG

🚨 LỖI HỆ THỐNG — {giờ} {ngày/tháng/năm}

Loại lỗi: {API Meta timeout / API key hết hạn / Rate limit / Khác}
Chi tiết: {mô tả ngắn}
Ảnh hưởng: Bỏ qua quét lúc {giờ}
Hành động: Thử lại vòng tiếp theo lúc {giờ}

⚠️ Nếu lỗi liên tục 3 lần → Gửi tag @{admin} để xử lý thủ công

---

## QUY TẮC CHUNG CHO BOT

1. Không bao giờ gửi báo cáo rỗng. Nếu quét không có thay đổi gì → không gửi.
2. Luôn ghi mã rule (KILL-01, SCALE-01...) để team tra ngược lý do.
3. Tiền VN = đơn vị "k" (nghìn VNĐ). Tiền KH/PH = đơn vị "$".
4. Tên camp phải chứa mã kịch bản [VIDxx] để insight tuần hoạt động.
5. Báo cáo cuối ngày và tuần luôn phải có ROAS = Doanh thu / Chi phí.
6. Báo cáo tuần phải có phần "Lệnh cho team" — đây là phần giá trị nhất.
7. Nếu tất cả camp đều tệ trong ngày → báo cáo cuối ngày phải flag rõ: "⚠️ Không có camp nào đạt target. Cần review creative/offer NGAY."
