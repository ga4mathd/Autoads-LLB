"""
Setup Google Sheets — Lollibooks Ads Command Center
Tạo 1 spreadsheet với 4 sheets qua Sheets API (không cần Drive quota).
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CREDS_PATH = ".credentials/google_service_account.json"
SHEET_TITLE = "Lollibooks Ads Command Center"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
sheets_svc = build("sheets", "v4", credentials=creds)
drive_svc  = build("drive",  "v3", credentials=creds)

# ─── Màu sắc dùng chung ──────────────────────────────────────────────────────
BLACK  = {"red": 0.13, "green": 0.13, "blue": 0.13}
BLUE   = {"red": 0.18, "green": 0.34, "blue": 0.60}
GREEN  = {"red": 0.13, "green": 0.37, "blue": 0.23}
WHITE  = {"red": 1,    "green": 1,    "blue": 1}
YELLOW = {"red": 1.0,  "green": 0.95, "blue": 0.60}
GRAY   = {"red": 0.95, "green": 0.95, "blue": 0.95}


def header_fmt(sheet_id, color, row_count=2):
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": row_count},
            "cell": {"userEnteredFormat": {
                "backgroundColor": color,
                "textFormat": {"foregroundColor": WHITE, "bold": True, "fontSize": 10},
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    }

def freeze(sheet_id, rows=1, cols=0):
    return {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {
                "frozenRowCount": rows, "frozenColumnCount": cols
            }},
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
        }
    }

def col_width(sheet_id, col_idx, px):
    return {
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": col_idx, "endIndex": col_idx + 1},
            "properties": {"pixelSize": px},
            "fields": "pixelSize"
        }
    }

def dropdown(sheet_id, start_row, end_row, col, values):
    return {
        "setDataValidation": {
            "range": {"sheetId": sheet_id, "startRowIndex": start_row,
                      "endRowIndex": end_row, "startColumnIndex": col, "endColumnIndex": col + 1},
            "rule": {
                "condition": {"type": "ONE_OF_LIST",
                              "values": [{"userEnteredValue": v} for v in values]},
                "showCustomUi": True, "strict": True
            }
        }
    }

def merge(sheet_id, r1, r2, c1, c2):
    return {
        "mergeCells": {
            "range": {"sheetId": sheet_id, "startRowIndex": r1, "endRowIndex": r2,
                      "startColumnIndex": c1, "endColumnIndex": c2},
            "mergeType": "MERGE_ALL"
        }
    }


# ─── Tạo spreadsheet với 4 sheets cùng lúc ───────────────────────────────────
ss_id = "1ag_SaTrASiXd6qlos0cvwUkLay_8OMHdLYVxlGF0DRc"
print(f"🔗 Dùng sheet có sẵn: {ss_id}")

# Lấy danh sách sheet hiện có
existing = sheets_svc.spreadsheets().get(spreadsheetId=ss_id, fields="sheets.properties").execute()
existing_titles = {s["properties"]["title"]: s["properties"]["sheetId"] for s in existing["sheets"]}
print(f"📄 Sheets hiện có: {list(existing_titles.keys())}")

# Tạo thêm sheet còn thiếu
needed = ["📋 LÊN ADS", "📊 DASHBOARD", "📜 LOG", "⚙️ CONFIG"]
add_reqs = []
for title in needed:
    if title not in existing_titles:
        add_reqs.append({"addSheet": {"properties": {"title": title}}})

if add_reqs:
    r = sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=ss_id, body={"requests": add_reqs}
    ).execute()
    for reply in r.get("replies", []):
        if "addSheet" in reply:
            p = reply["addSheet"]["properties"]
            existing_titles[p["title"]] = p["sheetId"]

# Đổi tên sheet mặc định "Sheet1" → xóa nếu không cần
default_sheets = [t for t in existing_titles if t not in needed]
delete_reqs = []
for t in default_sheets:
    delete_reqs.append({"deleteSheet": {"sheetId": existing_titles[t]}})
if delete_reqs:
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=ss_id, body={"requests": delete_reqs}
    ).execute()
    print(f"🗑️ Xoá sheet thừa: {default_sheets}")

# Reload để lấy sheetId chính xác
existing = sheets_svc.spreadsheets().get(spreadsheetId=ss_id, fields="sheets.properties").execute()
existing_titles = {s["properties"]["title"]: s["properties"]["sheetId"] for s in existing["sheets"]}

sid_ads    = existing_titles["📋 LÊN ADS"]
sid_dash   = existing_titles["📊 DASHBOARD"]
sid_log    = existing_titles["📜 LOG"]
sid_config = existing_titles["⚙️ CONFIG"]

print(f"✅ Sheet IDs: ads={sid_ads}, dash={sid_dash}, log={sid_log}, config={sid_config}")


# ─── SHEET 1: LÊN ADS ────────────────────────────────────────────────────────
# Row 1: nhóm cột, Row 2: tên cột chi tiết
ads_values = [
    # Row 1: nhóm
    ["🎯 CAMPAIGN", "", "", "🎯 AD SET", "", "", "",
     "🎬 CREATIVE", "", "", "",
     "💰 NGÂN SÁCH", "", "",
     "🤖 BOT", ""],
    # Row 2: header chi tiết
    ["Tên Camp (*)", "Market (*)", "Loại Camp (*)",
     "Tên AdSet (*)", "Tuổi Min", "Tuổi Max", "Giới tính",
     "Video ID (*)", "Caption (*)", "CTA", "Page ID (*)",
     "NS ngày (VND) (*)", "Ngày bắt đầu", "Ngày kết thúc",
     "Trạng thái", "Ghi chú bot"],
    # Row 3: ghi chú nhắc
    ["VD: [L24P][AI] Vanh.NTGT.10/3", "VN/KH/LA/PH", "MESSENGER_CONVERSATIONS",
     "VD: Target_VN_30-45", "25", "55", "ALL",
     "ID video trên Meta", "Nội dung quảng cáo", "MESSAGE_PAGE", "ID Page FB",
     "150000", "10/03/2026", "(để trống = không hết hạn)",
     "🟡 CHỜ TẠO", ""],
    # Row 4-5: ví dụ thật
    ["[L24P000023][AI-Seller] Vanh.NTGT.10/3", "VN", "MESSENGER_CONVERSATIONS",
     "Target_VN_30-45_FBOnly", 30, 45, "ALL",
     "1462075405587478", "🔥 Tự học cho bé tại nhà nhàn tênh. Đặt mua sách Lollibooks ngay!", "MESSAGE_PAGE", "104293862687132",
     150000, "10/03/2026", "",
     "🟡 CHỜ TẠO", ""],
    ["[LPAK-CAM][AI-Seller] Vanh.TBLB.Scale", "VN", "MESSENGER_PURCHASE",
     "Target_VN_25-45_Female", 25, 45, "FEMALE",
     "1462075405587478", "📚 Bộ sách Lollibooks — Bé học mà chơi, ba mẹ nhàn tênh!", "MESSAGE_PAGE", "104293862687132",
     200000, "10/03/2026", "",
     "🟡 CHỜ TẠO", ""],
]

sheets_svc.spreadsheets().values().update(
    spreadsheetId=ss_id, range="📋 LÊN ADS!A1",
    valueInputOption="USER_ENTERED", body={"values": ads_values}
).execute()

# Batch format sheet 1
reqs_ads = [
    # Merge header row 1 theo nhóm
    merge(sid_ads, 0,1, 0,3), merge(sid_ads, 0,1, 3,7),
    merge(sid_ads, 0,1, 7,11), merge(sid_ads, 0,1, 11,14),
    merge(sid_ads, 0,1, 14,16),
    # Header color
    header_fmt(sid_ads, BLACK, row_count=2),
    # Ghi chú row 3 màu nhạt
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
    freeze(sid_ads, rows=2, cols=0),
    # Dropdowns
    dropdown(sid_ads, 3, 1000, 1,  ["VN", "KH", "LA", "PH"]),
    dropdown(sid_ads, 3, 1000, 2,  ["MESSENGER_CONVERSATIONS", "MESSENGER_PURCHASE", "CONVERSION_SALES"]),
    dropdown(sid_ads, 3, 1000, 6,  ["ALL", "MALE", "FEMALE"]),
    dropdown(sid_ads, 3, 1000, 9,  ["MESSAGE_PAGE", "LEARN_MORE", "SHOP_NOW", "SIGN_UP"]),
    dropdown(sid_ads, 3, 1000, 14, ["🟡 CHỜ TẠO", "🔄 ĐANG TẠO", "✅ ĐÃ TẠO", "❌ LỖI", "⏸️ BỎ QUA"]),
    # Column widths
    col_width(sid_ads,  0, 280),   # Tên camp
    col_width(sid_ads,  1, 60),    # Market
    col_width(sid_ads,  2, 180),   # Loại camp
    col_width(sid_ads,  3, 200),   # Tên adset
    col_width(sid_ads,  7, 150),   # Video ID
    col_width(sid_ads,  8, 350),   # Caption
    col_width(sid_ads, 11, 130),   # NS ngày
    col_width(sid_ads, 14, 130),   # Trạng thái
    col_width(sid_ads, 15, 200),   # Ghi chú bot
]
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=ss_id, body={"requests": reqs_ads}
).execute()
print("✅ Sheet 1 [LÊN ADS] done")


# ─── SHEET 2: DASHBOARD ───────────────────────────────────────────────────────
dash_values = [[
    "TÀI KHOẢN", "NGÀY", "TÊN CAMP", "TRẠNG THÁI",
    "SPEND (VND)", "KẾT QUẢ", "CPA (VND)", "CPA ($)",
    "NS NGÀY (VND)", "% SPENT", "FREQUENCY", "CTR (%)",
    "RULE ÁP DỤNG", "CẬP NHẬT LÚC"
]]
sheets_svc.spreadsheets().values().update(
    spreadsheetId=ss_id, range="📊 DASHBOARD!A1",
    valueInputOption="RAW", body={"values": dash_values}
).execute()

reqs_dash = [
    header_fmt(sid_dash, BLUE, row_count=1),
    freeze(sid_dash, rows=1),
    col_width(sid_dash, 0, 140), col_width(sid_dash, 2, 280),
    col_width(sid_dash, 3, 100), col_width(sid_dash, 4, 110),
    col_width(sid_dash, 12, 120), col_width(sid_dash, 13, 150),
]
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=ss_id, body={"requests": reqs_dash}
).execute()
print("✅ Sheet 2 [DASHBOARD] done")


# ─── SHEET 3: LOG ─────────────────────────────────────────────────────────────
log_values = [[
    "THỜI GIAN", "TÀI KHOẢN", "TÊN CAMP",
    "HÀNH ĐỘNG", "RULE", "CHI TIẾT",
    "GIÁ TRỊ TRƯỚC", "GIÁ TRỊ SAU", "STATUS"
]]
sheets_svc.spreadsheets().values().update(
    spreadsheetId=ss_id, range="📜 LOG!A1",
    valueInputOption="RAW", body={"values": log_values}
).execute()

reqs_log = [
    header_fmt(sid_log, BLACK, row_count=1),
    freeze(sid_log, rows=1),
    col_width(sid_log, 0, 140), col_width(sid_log, 2, 260),
    col_width(sid_log, 5, 300),
]
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=ss_id, body={"requests": reqs_log}
).execute()
print("✅ Sheet 3 [LOG] done")


# ─── SHEET 4: CONFIG ──────────────────────────────────────────────────────────
config_values = [
    ["THAM SỐ", "GIÁ TRỊ", "ĐƠN VỊ", "MÔ TẢ"],
    ["CPA_TARGET",        105000,   "VND",        "Ngưỡng CPA tối đa — vượt qua bị xét tắt"],
    ["CPA_SCALE",          75000,   "VND",        "Ngưỡng CPA để trigger tăng NS 30%"],
    ["MAX_DAILY_BUDGET",5080000,   "VND",        "NS tối đa 1 camp/ngày (~$200)"],
    ["USD_TO_VND",         25400,   "VND/$",      "Tỷ giá quy đổi"],
    ["KILL_01_THRESHOLD", 150000,   "VND",        "Spend tối đa trước khi tắt nếu 0 đơn"],
    ["KILL_02_THRESHOLD", 105000,   "VND",        "Spend đủ điều kiện xét lịch sử"],
    ["KILL_03_MAX",       210000,   "VND",        "Spend tối đa khi chỉ có 1 đơn"],
    ["NOON_SPEND_PCT",        30,   "%",          "% NS cần tiêu đến 12h trưa"],
    ["SCALE_PCT",             30,   "%",          "% tăng NS khi SCALE"],
    ["ALERT_FREQUENCY",      2.5,   "",           "Frequency ngưỡng cảnh báo mỏi creative"],
    ["ALERT_CTR_DROP",        30,   "%",          "% CTR giảm ngưỡng cảnh báo"],
    ["KILL_LOCK_TIMES",        2,   "lần/7 ngày", "Bị tắt N lần → khóa vĩnh viễn"],
    ["SCAN_INTERVAL",          2,   "giờ",        "Tần suất quét tự động"],
    ["PRICE_PER_ORDER",   299000,   "VND",        "Giá bán 1 đơn (dùng tính ROAS)"],
    ["ACCOUNT_NAME", "Lollibooks VN 01", "",      "Tên tài khoản hiển thị trong báo cáo"],
]
sheets_svc.spreadsheets().values().update(
    spreadsheetId=ss_id, range="⚙️ CONFIG!A1",
    valueInputOption="USER_ENTERED", body={"values": config_values}
).execute()

reqs_config = [
    header_fmt(sid_config, GREEN, row_count=1),
    freeze(sid_config, rows=1),
    col_width(sid_config, 0, 160), col_width(sid_config, 1, 120),
    col_width(sid_config, 2, 100), col_width(sid_config, 3, 380),
    # Highlight cột Giá trị màu vàng nhạt
    {
        "repeatCell": {
            "range": {"sheetId": sid_config, "startRowIndex": 1, "endRowIndex": 50,
                      "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {"userEnteredFormat": {
                "backgroundColor": YELLOW,
                "textFormat": {"bold": True},
                "horizontalAlignment": "CENTER",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    },
]
sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=ss_id, body={"requests": reqs_config}
).execute()
print("✅ Sheet 4 [CONFIG] done")


# Lưu ID vào file
with open(".sheets_id", "w") as f:
    f.write(ss_id)

print(f"\n🎉 HOÀN TẤT!")
print(f"📋 Spreadsheet ID: {ss_id}")
print(f"🔗 https://docs.google.com/spreadsheets/d/{ss_id}")
