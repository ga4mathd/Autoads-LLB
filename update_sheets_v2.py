"""
Update Google Sheets v2:
- Thêm cột "Kịch bản" và "Link Drive Video" vào sheet LÊN ADS
- Thêm sheet "📈 INSIGHT KB" để bot ghi phân tích kịch bản
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CREDS_PATH = ".credentials/google_service_account.json"
SS_ID = "1ag_SaTrASiXd6qlos0cvwUkLay_8OMHdLYVxlGF0DRc"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
svc = build("sheets", "v4", credentials=creds)

# Lấy thông tin sheet hiện tại
info = svc.spreadsheets().get(spreadsheetId=SS_ID, fields="sheets.properties").execute()
sheets = {s["properties"]["title"]: s["properties"]["sheetId"] for s in info["sheets"]}
sid_ads = sheets["📋 LÊN ADS"]

WHITE  = {"red": 1,    "green": 1,    "blue": 1}
GREEN  = {"red": 0.13, "green": 0.37, "blue": 0.23}
ORANGE = {"red": 0.90, "green": 0.45, "blue": 0.10}
PURPLE = {"red": 0.36, "green": 0.19, "blue": 0.60}
GRAY   = {"red": 0.95, "green": 0.95, "blue": 0.95}
YELLOW = {"red": 1.0,  "green": 0.95, "blue": 0.60}

# ─── Xóa toàn bộ nội dung sheet LÊN ADS và viết lại cấu trúc mới ─────────────
print("🔄 Cập nhật sheet [LÊN ADS]...")

svc.spreadsheets().values().clear(
    spreadsheetId=SS_ID, range="📋 LÊN ADS!A1:Z1000"
).execute()

# Cấu trúc cột mới (18 cột):
# A: Kịch bản (*)    B: Tên Camp (*)     C: Market (*)       D: Loại Camp (*)
# E: Tên AdSet (*)   F: Tuổi Min         G: Tuổi Max         H: Giới tính
# I: Link Drive (*)  J: Caption (*)      K: CTA              L: Page ID (*)
# M: NS ngày (VND)   N: Ngày BĐ          O: Ngày KT
# P: Trạng thái      Q: Meta Video ID    R: Ghi chú bot

new_values = [
    # Row 1: nhóm
    ["🎬 KỊCH BẢN", "🎯 CAMPAIGN", "", "", "🎯 AD SET", "", "", "",
     "📁 VIDEO", "", "", "",
     "💰 NGÂN SÁCH", "", "",
     "🤖 BOT", "", ""],
    # Row 2: header chi tiết
    ["Kịch bản (*)", "Tên Camp (*)", "Market (*)", "Loại Camp (*)",
     "Tên AdSet (*)", "Tuổi Min", "Tuổi Max", "Giới tính",
     "Link Drive Video (*)", "Caption (*)", "CTA", "Page ID (*)",
     "NS ngày (VND) (*)", "Ngày bắt đầu", "Ngày kết thúc",
     "Trạng thái", "Meta Video ID (auto)", "Ghi chú bot"],
    # Row 3: ghi chú
    ["VD: VID01_GiaoVienTay", "VD: [L24P][AI] Vanh.VID01.10/3", "VN/KH/LA/PH", "MESSENGER_CONVERSATIONS",
     "Target_VN_30-45", "25", "55", "ALL",
     "https://drive.google.com/...", "Nội dung quảng cáo...", "MESSAGE_PAGE", "ID Page FB",
     "150000", "10/03/2026", "(trống = không hết hạn)",
     "🟡 CHỜ TẠO", "(bot tự điền)", ""],
    # Ví dụ mẫu
    ["VID05_GiaoVienTay", "[L24P000023][AI-Seller] Vanh.VID05.10/3", "VN", "MESSENGER_CONVERSATIONS",
     "Target_VN_30-45_FBOnly", 30, 45, "ALL",
     "https://drive.google.com/file/d/XXXX/view", "🔥 Cô giáo Tây dạy con bạn tiếng Anh tại nhà — Không cần ra trung tâm!", "MESSAGE_PAGE", "104293862687132",
     150000, "10/03/2026", "",
     "🟡 CHỜ TẠO", "", ""],
    ["VID12_HoatHinh", "[L24P000023][AI-Seller] Vanh.VID12.10/3", "VN", "MESSENGER_PURCHASE",
     "Target_VN_25-45_Female", 25, 45, "FEMALE",
     "https://drive.google.com/file/d/YYYY/view", "📚 Bé tự học qua hoạt hình — Lollibooks giúp con thích đọc sách!", "MESSAGE_PAGE", "104293862687132",
     200000, "10/03/2026", "",
     "🟡 CHỜ TẠO", "", ""],
]

svc.spreadsheets().values().update(
    spreadsheetId=SS_ID, range="📋 LÊN ADS!A1",
    valueInputOption="USER_ENTERED", body={"values": new_values}
).execute()

# Format requests
reqs = [
    # Unmerge toàn bộ row 1 trước
    {"unmergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 18}}},
    # Merge row 1 theo nhóm mới
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 1}, "mergeType": "MERGE_ALL"}},
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 1, "endColumnIndex": 4}, "mergeType": "MERGE_ALL"}},
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 4, "endColumnIndex": 8}, "mergeType": "MERGE_ALL"}},
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 8, "endColumnIndex": 12}, "mergeType": "MERGE_ALL"}},
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 12, "endColumnIndex": 15}, "mergeType": "MERGE_ALL"}},
    {"mergeCells": {"range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 15, "endColumnIndex": 18}, "mergeType": "MERGE_ALL"}},
    # Header color rows 1-2
    {
        "repeatCell": {
            "range": {"sheetId": sid_ads, "startRowIndex": 0, "endRowIndex": 2},
            "cell": {"userEnteredFormat": {
                "backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.13},
                "textFormat": {"foregroundColor": WHITE, "bold": True, "fontSize": 10},
                "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    },
    # Cột Kịch bản màu tím nổi bật
    {
        "repeatCell": {
            "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 0, "endColumnIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": {"red": 0.94, "green": 0.90, "blue": 0.98},
                "textFormat": {"bold": True},
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    },
    # Cột Meta Video ID (auto) màu xanh nhạt
    {
        "repeatCell": {
            "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 16, "endColumnIndex": 17},
            "cell": {"userEnteredFormat": {
                "backgroundColor": {"red": 0.85, "green": 0.93, "blue": 0.85},
                "textFormat": {"italic": True},
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    },
    # Row 3 (ghi chú) màu xám
    {
        "repeatCell": {
            "range": {"sheetId": sid_ads, "startRowIndex": 2, "endRowIndex": 3},
            "cell": {"userEnteredFormat": {
                "backgroundColor": GRAY,
                "textFormat": {"italic": True, "foregroundColor": {"red": 0.4, "green": 0.4, "blue": 0.4}},
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    },
    # Freeze 2 rows
    {
        "updateSheetProperties": {
            "properties": {"sheetId": sid_ads, "gridProperties": {"frozenRowCount": 2}},
            "fields": "gridProperties.frozenRowCount"
        }
    },
    # Dropdowns
    {"setDataValidation": {
        "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 2, "endColumnIndex": 3},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in ["VN", "KH", "LA", "PH"]]}, "showCustomUi": True, "strict": True}
    }},
    {"setDataValidation": {
        "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 3, "endColumnIndex": 4},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in ["MESSENGER_CONVERSATIONS", "MESSENGER_PURCHASE", "CONVERSION_SALES"]]}, "showCustomUi": True, "strict": True}
    }},
    {"setDataValidation": {
        "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 7, "endColumnIndex": 8},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in ["ALL", "MALE", "FEMALE"]]}, "showCustomUi": True, "strict": True}
    }},
    {"setDataValidation": {
        "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 10, "endColumnIndex": 11},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in ["MESSAGE_PAGE", "LEARN_MORE", "SHOP_NOW", "SIGN_UP"]]}, "showCustomUi": True, "strict": True}
    }},
    {"setDataValidation": {
        "range": {"sheetId": sid_ads, "startRowIndex": 3, "endRowIndex": 1000, "startColumnIndex": 15, "endColumnIndex": 16},
        "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in ["🟡 CHỜ TẠO", "🔄 ĐANG TẠO", "✅ ĐÃ TẠO", "❌ LỖI", "⏸️ BỎ QUA"]]}, "showCustomUi": True, "strict": True}
    }},
    # Column widths
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 160}, "fields": "pixelSize"}},  # Kịch bản
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 280}, "fields": "pixelSize"}},  # Tên camp
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 60},  "fields": "pixelSize"}},  # Market
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}},  # Loại camp
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 8, "endIndex": 9}, "properties": {"pixelSize": 220}, "fields": "pixelSize"}},  # Link Drive
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 9, "endIndex": 10}, "properties": {"pixelSize": 350}, "fields": "pixelSize"}}, # Caption
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 12, "endIndex": 13}, "properties": {"pixelSize": 130}, "fields": "pixelSize"}}, # NS ngày
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 15, "endIndex": 16}, "properties": {"pixelSize": 130}, "fields": "pixelSize"}}, # Trạng thái
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 16, "endIndex": 17}, "properties": {"pixelSize": 150}, "fields": "pixelSize"}}, # Video ID auto
    {"updateDimensionProperties": {"range": {"sheetId": sid_ads, "dimension": "COLUMNS", "startIndex": 17, "endIndex": 18}, "properties": {"pixelSize": 200}, "fields": "pixelSize"}}, # Ghi chú
]
svc.spreadsheets().batchUpdate(spreadsheetId=SS_ID, body={"requests": reqs}).execute()
print("✅ Sheet [LÊN ADS] cập nhật xong")

# ─── Thêm sheet mới: INSIGHT KB ───────────────────────────────────────────────
if "📈 INSIGHT KB" not in sheets:
    r = svc.spreadsheets().batchUpdate(spreadsheetId=SS_ID, body={"requests": [
        {"addSheet": {"properties": {"title": "📈 INSIGHT KB", "index": 4,
                                      "gridProperties": {"rowCount": 200, "columnCount": 12}}}}
    ]}).execute()
    sid_insight = r["replies"][0]["addSheet"]["properties"]["sheetId"]
    print(f"✅ Tạo sheet [INSIGHT KB] sid={sid_insight}")
else:
    sid_insight = sheets["📈 INSIGHT KB"]
    print(f"✅ Sheet [INSIGHT KB] đã có")

# Header Insight KB
insight_headers = [[
    "TUẦN", "KỊCH BẢN", "TÊN VIDEO / NỘI DUNG",
    "TỔNG SPEND (VND)", "TỔNG KQ", "CPA (VND)", "CPA ($)",
    "NS ĐÃ DÙNG (VND)", "SỐ CAMP", "ĐÁNH GIÁ", "GHI CHÚ", "CẬP NHẬT"
]]
svc.spreadsheets().values().update(
    spreadsheetId=SS_ID, range="📈 INSIGHT KB!A1",
    valueInputOption="RAW", body={"values": insight_headers}
).execute()

svc.spreadsheets().batchUpdate(spreadsheetId=SS_ID, body={"requests": [
    {
        "repeatCell": {
            "range": {"sheetId": sid_insight, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": PURPLE,
                "textFormat": {"foregroundColor": WHITE, "bold": True, "fontSize": 10},
                "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    },
    {
        "updateSheetProperties": {
            "properties": {"sheetId": sid_insight, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"
        }
    },
    # Cột CPA highlight vàng
    {
        "repeatCell": {
            "range": {"sheetId": sid_insight, "startRowIndex": 1, "endRowIndex": 200, "startColumnIndex": 5, "endColumnIndex": 7},
            "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    },
    # Cột Đánh giá
    {
        "setDataValidation": {
            "range": {"sheetId": sid_insight, "startRowIndex": 1, "endRowIndex": 200, "startColumnIndex": 9, "endColumnIndex": 10},
            "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                {"userEnteredValue": v} for v in ["🏆 WIN — Nhân", "⚠️ TRUNG BÌNH — Giữ", "💀 LOSE — Loại", "🔄 CẦN TEST THÊM"]
            ]}, "showCustomUi": True, "strict": True}
        }
    },
    # Column widths
    {"updateDimensionProperties": {"range": {"sheetId": sid_insight, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},  "properties": {"pixelSize": 180}, "fields": "pixelSize"}},
    {"updateDimensionProperties": {"range": {"sheetId": sid_insight, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3},  "properties": {"pixelSize": 250}, "fields": "pixelSize"}},
    {"updateDimensionProperties": {"range": {"sheetId": sid_insight, "dimension": "COLUMNS", "startIndex": 9, "endIndex": 10}, "properties": {"pixelSize": 160}, "fields": "pixelSize"}},
    {"updateDimensionProperties": {"range": {"sheetId": sid_insight, "dimension": "COLUMNS", "startIndex": 10, "endIndex": 11}, "properties": {"pixelSize": 250}, "fields": "pixelSize"}},
]}).execute()
print("✅ Sheet [INSIGHT KB] done")

print(f"\n🎉 Cập nhật hoàn tất!")
print(f"🔗 https://docs.google.com/spreadsheets/d/{SS_ID}")
