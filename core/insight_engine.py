"""
Insight Engine — Lollibooks Ads System
Phân tích kịch bản (KB) win/lose theo tuần.
Flow:
  1. Đọc sheet [LÊN ADS] → map "Kịch bản" → tên camp
  2. Lấy Meta insights theo từng camp (7 ngày)
  3. Group by kịch bản → tính CPA, spend, KQ per KB
  4. Xếp hạng WIN / TRUNG BÌNH / LOSE
  5. Ghi vào sheet [INSIGHT KB]
  6. Gửi báo cáo tuần vào nhóm Telegram (MẪU 5)
"""

import os
import re
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

ACCESS_TOKEN  = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")
if not AD_ACCOUNT_ID.startswith("act_"):
    AD_ACCOUNT_ID = f"act_{AD_ACCOUNT_ID}"
SS_ID         = os.getenv("GOOGLE_SHEETS_ID")
BOT_TOKEN     = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID      = open(os.path.join(BASE_DIR, "core/telegram_group_id.txt")).read().strip()

USD_TO_VND    = 25400
CPA_TARGET    = 105000
CPA_GOOD      = 75000
PRICE_PER_ORDER = 299000
ACCOUNT_NAME  = "Lollibooks VN 01"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds  = Credentials.from_service_account_file(
    os.path.join(BASE_DIR, ".credentials/google_service_account.json"), scopes=SCOPES
)
svc = build("sheets", "v4", credentials=creds)

META_BASE = "https://graph.facebook.com/v19.0"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def usd_to_vnd(usd): return int(usd * USD_TO_VND)

def extract_orders(actions):
    amap = {a["action_type"]: int(a.get("value", 0)) for a in actions}
    return (
        amap.get("omni_complete_registration", 0)
        or amap.get("onsite_conversion.messaging_conversation_started_7d", 0)
        or amap.get("offsite_conversion.fb_pixel_complete_registration", 0)
    )

def k(vnd): return f"{round(vnd/1000)}k"


# ─── 1. Đọc mapping KB từ Google Sheets ──────────────────────────────────────

def load_kb_mapping() -> dict:
    """
    Trả về: {"[L24P000023][AI-Seller] Vanh.VID05.10/3": "VID05_GiaoVienTay", ...}
    Đọc từ sheet [LÊN ADS]: cột A = KB, cột B = Tên camp
    """
    result = svc.spreadsheets().values().get(
        spreadsheetId=SS_ID,
        range="📋 LÊN ADS!A4:B1000"  # bỏ 3 dòng header + ghi chú
    ).execute()
    rows = result.get("values", [])
    mapping = {}
    for row in rows:
        if len(row) >= 2 and row[0] and row[1]:
            kb   = row[0].strip()
            name = row[1].strip()
            if kb and name:
                mapping[name] = kb
    return mapping


# ─── 2. Lấy Meta insights 7 ngày ─────────────────────────────────────────────

def get_weekly_insights() -> dict:
    """
    Trả về: {campaign_name: {spend_vnd, orders, cpa_vnd, spend_usd}}
    """
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    res = requests.get(f"{META_BASE}/{AD_ACCOUNT_ID}/insights", params={
        "access_token": ACCESS_TOKEN,
        "level": "campaign",
        "fields": "campaign_name,spend,actions",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "limit": 500,
    }, timeout=20)

    result = {}
    for item in res.json().get("data", []):
        name      = item.get("campaign_name", "")
        spend_usd = float(item.get("spend", 0))
        orders    = extract_orders(item.get("actions", []))
        spend_vnd = usd_to_vnd(spend_usd)
        cpa_vnd   = (spend_vnd // orders) if orders > 0 else 999999
        result[name] = {
            "spend_usd": spend_usd,
            "spend_vnd": spend_vnd,
            "orders":    orders,
            "cpa_vnd":   cpa_vnd,
        }
    return result


# ─── 3. Group by kịch bản ────────────────────────────────────────────────────

def group_by_kb(kb_map: dict, insights: dict) -> dict:
    """
    Gộp insights theo kịch bản.
    Camp không có KB trong sheets → gắn vào "UNKNOWN"
    Trả về: {kb_code: {spend_vnd, orders, cpa_vnd, camps, content_name}}
    """
    kb_data = defaultdict(lambda: {
        "spend_vnd": 0, "orders": 0, "camps": 0,
        "content_name": ""
    })

    for camp_name, data in insights.items():
        if data["spend_vnd"] < 1000:  # bỏ qua camp gần như không chạy
            continue

        # Tìm KB: ưu tiên sheet mapping, fallback tìm pattern [VIDxx] trong tên camp
        kb = kb_map.get(camp_name)
        if not kb:
            match = re.search(r'\[(VID\d+[_\w]*)\]', camp_name)
            kb = match.group(1) if match else "UNKNOWN"

        kb_data[kb]["spend_vnd"] += data["spend_vnd"]
        kb_data[kb]["orders"]    += data["orders"]
        kb_data[kb]["camps"]     += 1
        if not kb_data[kb]["content_name"]:
            kb_data[kb]["content_name"] = camp_name[:50]

    # Tính CPA per KB
    for kb, d in kb_data.items():
        d["cpa_vnd"] = (d["spend_vnd"] // d["orders"]) if d["orders"] > 0 else 999999

    return dict(kb_data)


# ─── 4. Xếp hạng ─────────────────────────────────────────────────────────────

def rank_kb(kb_data: dict) -> tuple:
    """Trả về (winners, mid, losers) — đã sort theo CPA."""
    items = [(kb, d) for kb, d in kb_data.items()]
    items.sort(key=lambda x: x[1]["cpa_vnd"])

    winners = [(kb, d) for kb, d in items if d["cpa_vnd"] < CPA_GOOD and d["orders"] >= 3]
    mid     = [(kb, d) for kb, d in items if CPA_GOOD <= d["cpa_vnd"] <= CPA_TARGET and d["orders"] >= 1]
    losers  = [(kb, d) for kb, d in items if d["cpa_vnd"] > CPA_TARGET or d["orders"] == 0]
    return winners, mid, losers


# ─── 5. Ghi vào sheet INSIGHT KB ─────────────────────────────────────────────

def write_to_sheet(week_label: str, kb_data: dict, winners, mid, losers):
    """Ghi hàng mới vào sheet [INSIGHT KB]."""
    now_str = datetime.now().strftime("%H:%M %d/%m/%Y")

    def rating(kb):
        if any(k == kb for k, _ in winners): return "🏆 WIN — Nhân"
        if any(k == kb for k, _ in mid):     return "⚠️ TRUNG BÌNH — Giữ"
        return "💀 LOSE — Loại"

    rows = []
    for kb, d in sorted(kb_data.items(), key=lambda x: x[1]["cpa_vnd"]):
        cpa_usd = d["cpa_vnd"] / USD_TO_VND
        rows.append([
            week_label, kb, d["content_name"],
            d["spend_vnd"], d["orders"], d["cpa_vnd"],
            round(cpa_usd, 2),
            d["spend_vnd"],   # NS đã dùng = spend
            d["camps"],
            rating(kb),
            "", now_str
        ])

    if rows:
        svc.spreadsheets().values().append(
            spreadsheetId=SS_ID,
            range="📈 INSIGHT KB!A2",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows}
        ).execute()
        print(f"✅ Đã ghi {len(rows)} dòng vào sheet INSIGHT KB")


# ─── 6. Gửi báo cáo tuần Telegram (MẪU 5) ────────────────────────────────────

def send_weekly_telegram(week_num: int, date_range: str, kb_data: dict,
                          winners, mid, losers,
                          daily_cpas: list, prev_week: dict = None):
    """Gửi báo cáo tuần theo MẪU 5."""
    total_spend = sum(d["spend_vnd"] for d in kb_data.values())
    total_orders = sum(d["orders"] for d in kb_data.values())
    avg_cpa = (total_spend // total_orders) if total_orders > 0 else 0
    revenue = total_orders * PRICE_PER_ORDER
    profit  = revenue - total_spend
    roas    = round(revenue / total_spend, 1) if total_spend > 0 else 0

    # Xu hướng CPA theo ngày
    days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    trend_lines = []
    for i, (day, cpa) in enumerate(zip(days, daily_cpas)):
        if i == 0 or daily_cpas[i-1] == 0:
            icon = "➡️"
        elif cpa < daily_cpas[i-1]:
            icon = "📉"  # CPA giảm = tốt
        elif cpa > daily_cpas[i-1]:
            icon = "📈"
        else:
            icon = "➡️"
        trend_lines.append(f"{day}: {k(cpa)} {icon}" if cpa > 0 else f"{day}: — {icon}")

    lines = [
        f"📈 BÁO CÁO TUẦN {week_num} — {date_range}",
        f"TK: {ACCOUNT_NAME}",
        "",
        "━━━ TỔNG QUAN TUẦN ━━━",
        f"💸 Tổng spend: {k(total_spend)}",
        f"📦 Tổng đơn: {total_orders}",
        f"📊 CPA TB tuần: {k(avg_cpa)}",
        f"💹 ROAS tuần: {roas}x",
        f"💵 Lãi gộp ước tính: {k(profit)}",
        "",
        "━━━ XU HƯỚNG CPA THEO NGÀY ━━━",
        *trend_lines,
    ]

    if winners or losers:
        lines += ["", "━━━ INSIGHT KỊCH BẢN ━━━"]
        if winners:
            lines.append("🏆 Nhóm thắng:")
            for kb, d in winners[:3]:
                lines.append(f"• {kb}: {d['orders']} đơn, CPA {k(d['cpa_vnd'])}, spend {k(d['spend_vnd'])}")
        if losers:
            lines.append("💀 Nhóm thua:")
            for kb, d in losers[:3]:
                cpa_str = k(d['cpa_vnd']) if d['orders'] > 0 else "--"
                lines.append(f"• {kb}: {d['orders']} đơn, CPA {cpa_str}, spend {k(d['spend_vnd'])}")

    # Lệnh cho team
    lines += ["", "━━━ LỆNH CHO TEAM ━━━"]
    if winners:
        win_kbs = ", ".join(kb for kb, _ in winners[:2])
        lines.append(f"🎬 Video: Nhân bản {win_kbs} — test thêm hook mới với cùng concept")
    else:
        lines.append("🎬 Video: Chưa có KB nào win — cần brainstorm concept hoàn toàn mới")

    if losers:
        lose_kbs = ", ".join(kb for kb, _ in losers[:2])
        lines.append(f"📝 Content: Ngừng {lose_kbs} — không đầu tư thêm creative")
    
    lines.append(f"🎯 Targeting: {'Giữ nguyên — đang hiệu quả' if avg_cpa < CPA_TARGET else 'Cần test broad vs interest mới'}")

    if prev_week:
        prev_spend  = prev_week.get("spend_vnd", 0)
        prev_orders = prev_week.get("orders", 0)
        prev_cpa    = prev_week.get("cpa_vnd", 0)
        prev_roas   = prev_week.get("roas", 0)

        def chg(new, old):
            if old == 0: return "+∞%"
            pct = (new - old) / old * 100
            return f"+{pct:.0f}%" if pct >= 0 else f"{pct:.0f}%"

        lines += [
            "", "━━━ SO SÁNH VỚI TUẦN TRƯỚC ━━━",
            f"Spend: {k(prev_spend)} → {k(total_spend)} ({chg(total_spend, prev_spend)})",
            f"Đơn: {prev_orders} → {total_orders} ({chg(total_orders, prev_orders)})",
            f"CPA: {k(prev_cpa)} → {k(avg_cpa)} ({chg(avg_cpa, prev_cpa)})",
            f"ROAS: {prev_roas}x → {roas}x ({chg(roas, prev_roas)})",
        ]

    text = "\n".join(lines)
    res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={"chat_id": GROUP_ID, "text": text})
    return res.status_code == 200


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_weekly_insight(prev_week: dict = None):
    now = datetime.now()
    week_num   = now.isocalendar()[1]
    since_date = (now - timedelta(days=7)).strftime("%d/%m")
    until_date = now.strftime("%d/%m/%Y")
    week_label = f"Tuần {week_num} ({since_date}→{until_date})"
    date_range = f"{since_date} → {until_date}"

    print(f"🔍 Phân tích insight tuần {week_num}...")
    kb_map    = load_kb_mapping()
    print(f"  ✅ {len(kb_map)} camp có KB mapping từ sheets")
    insights  = get_weekly_insights()
    print(f"  ✅ {len(insights)} camp có data từ Meta")
    kb_data   = group_by_kb(kb_map, insights)
    print(f"  ✅ {len(kb_data)} kịch bản sau khi gộp: {list(kb_data.keys())}")
    winners, mid, losers = rank_kb(kb_data)

    # Daily CPA placeholder (7 ngày gần nhất) — cần gọi insights từng ngày nếu muốn chi tiết
    daily_cpas = [0] * 7  # TODO: fetch per-day insights nếu cần

    write_to_sheet(week_label, kb_data, winners, mid, losers)
    ok = send_weekly_telegram(week_num, date_range, kb_data, winners, mid, losers, daily_cpas, prev_week)
    print(f"  {'✅' if ok else '❌'} Đã gửi báo cáo tuần Telegram")

    return {
        "spend_vnd": sum(d["spend_vnd"] for d in kb_data.values()),
        "orders":    sum(d["orders"] for d in kb_data.values()),
        "cpa_vnd":   sum(d["cpa_vnd"] for d in kb_data.values() if d["orders"] > 0) // max(len([d for d in kb_data.values() if d["orders"] > 0]), 1),
        "roas":      round(sum(d["orders"] * PRICE_PER_ORDER for d in kb_data.values()) / max(sum(d["spend_vnd"] for d in kb_data.values()), 1), 1)
    }


if __name__ == "__main__":
    run_weekly_insight()
