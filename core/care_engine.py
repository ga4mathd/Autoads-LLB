"""
Care Engine — Lollibooks Ads System
Đọc insights từ Meta API, áp rules, gọi Telegram Notifier.
Chạy mỗi 2 tiếng (hoặc trigger tay).
"""

import os
import sys
import json
import fcntl
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Lock file để tránh chạy 2 instance cùng lúc
LOCK_FILE = os.path.join(os.path.dirname(__file__), '.care_engine.lock')

# Add parent dir
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.telegram_notifier import (
    send_periodic_scan,
    send_slow_spend_report,
    send_midnight_revive
)

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")
if not AD_ACCOUNT_ID.startswith("act_"):
    AD_ACCOUNT_ID = f"act_{AD_ACCOUNT_ID}"

BASE_URL = "https://graph.facebook.com/v19.0"

# Load rules config
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'vn_conversion_rules.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

CPA_TARGET = CONFIG["cpa_target"]       # 105,000 VND
CPA_SCALE  = CONFIG["cpa_scale"]        # 75,000 VND
USD_TO_VND = 25400                       # VCB ngày 09/03/2026


def vnd_to_usd(vnd: int) -> float:
    return vnd / USD_TO_VND

def usd_to_vnd(usd: float) -> int:
    return int(usd * USD_TO_VND)

def _extract_orders(actions: list) -> int:
    """
    Đếm kết quả từ actions — khớp với cột 'Kết quả' trong Meta Ads Manager.
    Ưu tiên omni_complete_registration (gộp on+off-site, không double-count).
    Fallback: onsite_conversion.messaging_conversation_started_7d (camp Messenger).
    """
    action_map = {a["action_type"]: int(a.get("value", 0)) for a in actions}

    # Ưu tiên 1: pixel complete registration (omni = gộp, không x3)
    if action_map.get("omni_complete_registration", 0) > 0:
        return action_map["omni_complete_registration"]

    # Ưu tiên 2: camp Messenger conversations
    if action_map.get("onsite_conversion.messaging_conversation_started_7d", 0) > 0:
        return action_map["onsite_conversion.messaging_conversation_started_7d"]

    # Fallback: pixel event dạng cũ
    return action_map.get("offsite_conversion.fb_pixel_complete_registration", 0)


def get_all_campaigns() -> list:
    """Lấy TẤT CẢ campaigns kèm daily_budget (có pagination)."""
    all_camps = []
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,daily_budget",
        "limit": 200
    }
    url = f"{BASE_URL}/{AD_ACCOUNT_ID}/campaigns"
    while url:
        res = requests.get(url, params=params, timeout=20)
        data = res.json()
        all_camps.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")
        url = next_url if next_url else None
        params = {}
    return all_camps


def get_bulk_insights(date_preset: str = None, since: str = None, until: str = None) -> dict:
    """
    Lấy insights TẤT CẢ campaigns trong 1 API call (level=campaign).
    Trả về dict: campaign_id → {spend_usd, spend_vnd, orders, impressions, clicks, frequency, ctr}
    """
    params = {
        "access_token": ACCESS_TOKEN,
        "level": "campaign",
        "fields": "campaign_id,spend,actions,impressions,clicks,frequency",
        "limit": 500
    }
    if date_preset:
        params["date_preset"] = date_preset
    elif since and until:
        params["time_range"] = json.dumps({"since": since, "until": until})

    res = requests.get(f"{BASE_URL}/{AD_ACCOUNT_ID}/insights", params=params, timeout=30)
    result = {}
    for item in res.json().get("data", []):
        cid = item.get("campaign_id")
        if not cid:
            continue
        spend_usd = float(item.get("spend", 0))
        impressions = int(item.get("impressions", 0))
        clicks = int(item.get("clicks", 0))
        frequency = float(item.get("frequency", 0))
        orders = _extract_orders(item.get("actions", []))
        result[cid] = {
            "spend_usd": spend_usd,
            "spend_vnd": usd_to_vnd(spend_usd),
            "orders": orders,
            "impressions": impressions,
            "clicks": clicks,
            "frequency": frequency,
            "ctr": (clicks / impressions * 100) if impressions > 0 else 0.0
        }
    return result


def get_bulk_insights_range(days: int) -> dict:
    """CPA trung bình N ngày gần nhất cho TẤT CẢ campaigns."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    raw = get_bulk_insights(since=since, until=until)
    result = {}
    for cid, d in raw.items():
        orders = d["orders"]
        cpa_vnd = (d["spend_vnd"] // orders) if orders > 0 else 999999
        result[cid] = {"cpa_vnd": cpa_vnd, "orders": orders}
    return result


def set_campaign_status(campaign_id: str, status: str):
    """Bật/tắt campaign. status = 'ACTIVE' | 'PAUSED'"""
    res = requests.post(f"{BASE_URL}/{campaign_id}", data={
        "access_token": ACCESS_TOKEN,
        "status": status
    })
    return res.status_code == 200


def set_campaign_budget(campaign_id: str, daily_budget_usd: float):
    """Cập nhật daily budget (USD)."""
    budget_cents = int(daily_budget_usd * 100)  # Meta dùng cents (USD)
    res = requests.post(f"{BASE_URL}/{campaign_id}", data={
        "access_token": ACCESS_TOKEN,
        "daily_budget": budget_cents
    })
    return res.status_code == 200


def run_care():
    """Main care loop — chạy 1 lần scan."""
    # Prevent double-run (lock file)
    lock_fd = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("⚠️ Care engine đang chạy ở nơi khác. Bỏ qua.")
        lock_fd.close()
        return

    now_str = datetime.now().strftime("%H:%M %d/%m/%Y")
    print(f"\n🔍 [Care Engine] Scan lúc {now_str}")

    print("  📡 Đang tải campaigns...")
    campaigns = get_all_campaigns()
    if not campaigns:
        print("⚠️ Không có campaign nào.")
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        return

    print(f"  ✅ {len(campaigns)} campaigns. Đang tải insights (3 calls)...")
    insights_today  = get_bulk_insights(date_preset="today")
    insights_3d     = get_bulk_insights_range(3)
    insights_7d     = get_bulk_insights_range(7)
    print("  ✅ Insights OK. Đang xử lý rules...")

    hour = datetime.now().hour
    is_midnight = hour == 0
    is_noon = hour == 12

    report_camps = []      # Chỉ lưu camp có spend > 0 hoặc ACTIVE
    kills = []
    scales = []
    alerts = []
    redistributes = []
    revives = []
    kept_paused = []
    dead_creatives = []
    slow_camps = []
    active_count = 0
    total_spend_vnd = 0
    total_orders = 0

    # Tìm camp có CPA tốt nhất để dồn NS sang (dùng cho KILL_02, SCALE_02)
    active_good_camps = []

    for camp in campaigns:
        cid = camp["id"]
        name = camp["name"]
        status = camp["status"]
        daily_budget_usd = float(camp.get("daily_budget", 0)) / 100  # cents → USD

        today = insights_today.get(cid, {"spend_usd": 0, "spend_vnd": 0, "orders": 0, "frequency": 0.0, "ctr": 0.0})
        spend_vnd = today["spend_vnd"]
        spend_usd = today["spend_usd"]
        orders = today["orders"]
        frequency = today["frequency"]
        ctr = today["ctr"]

        cpa_today_vnd = (spend_vnd // orders) if orders > 0 else 999999
        cpa_3d = insights_3d.get(cid, {}).get("cpa_vnd", 999999)
        cpa_7d = insights_7d.get(cid, {}).get("cpa_vnd", 999999)

        total_spend_vnd += spend_vnd
        total_orders += orders

        print(f"  📋 {name[:40]} | {status} | Spend: {spend_vnd:,.0f}đ | Đơn: {orders} | CPA: {cpa_today_vnd:,.0f}đ")

        # Chỉ đưa vào báo cáo nếu ACTIVE hoặc có spend hôm nay
        if status == "ACTIVE":
            active_count += 1
        if status == "ACTIVE" or spend_vnd > 0:
            report_camps.append({
                "name": name,
                "status": status,
                "spend_vnd": spend_vnd,
                "orders": orders,
                "cpa_vnd": cpa_today_vnd if orders > 0 else 0
            })

        # ====== KILL RULES (chỉ check campaign ACTIVE) ======
        if status == "ACTIVE":

            # KILL_01: Spend >= 150k VÀ 0 đơn → Tắt
            if spend_vnd >= 150000 and orders == 0:
                print(f"  🔴 KILL_01 triggered: {name}")
                set_campaign_status(cid, "PAUSED")
                kills.append({"name": name, "rule": "KILL_01", "spend_vnd": spend_vnd, "orders": orders, "cpa_vnd": cpa_today_vnd, "reason": "Spend ≥ 150k, không có đơn nào."})
                continue

            # KILL_02: Spend >= 105k, 0 đơn. Lịch sử 3 ngày CPA tốt → cho tiêu đến 150k
            if spend_vnd >= 105000 and orders == 0:
                if cpa_3d < CPA_TARGET:
                    print(f"  ⚠️ KILL_02: {name} — Chờ đến 150k (lịch sử tốt)")
                    # Không tắt — chờ thêm (sẽ catch bởi KILL_01 khi đủ 150k)
                else:
                    print(f"  🔴 KILL_02 triggered (lịch sử xấu): {name}")
                    set_campaign_status(cid, "PAUSED")
                    kills.append({"name": name, "rule": "KILL_02", "spend_vnd": spend_vnd, "orders": orders, "cpa_vnd": cpa_today_vnd, "reason": f"Spend ≥ 105k, 0 đơn. Lịch sử 3 ngày CPA {cpa_3d:,.0f}đ ≥ {CPA_TARGET:,.0f}đ → Tắt ngay."})
                    continue

            # KILL_03: Spend 105k-210k, chỉ 1 đơn
            if 105000 <= spend_vnd <= 210000 and orders == 1:
                if cpa_3d < CPA_TARGET:
                    print(f"  ⚠️ KILL_03: {name} — 1 đơn, lịch sử tốt, chờ đến 210k")
                else:
                    print(f"  🔴 KILL_03 triggered: {name}")
                    set_campaign_status(cid, "PAUSED")
                    kills.append({"name": name, "rule": "KILL_03", "spend_vnd": spend_vnd, "orders": orders, "cpa_vnd": cpa_today_vnd, "reason": f"Spend 105-210k, chỉ 1 đơn. Lịch sử 3 ngày CPA {cpa_3d:,.0f}đ ≥ {CPA_TARGET:,.0f}đ → Tắt."})
                    continue

            # KILL_04: 12h trưa — chưa đạt 30% ngân sách
            if is_noon:
                expected_noon = daily_budget_usd * 0.3 * USD_TO_VND
                if spend_vnd < expected_noon:
                    print(f"  🔴 KILL_04 triggered: {name} — 12h chưa đạt 30% NS")
                    set_campaign_status(cid, "PAUSED")
                    kills.append({"name": name, "rule": "KILL_04", "spend_vnd": spend_vnd, "orders": orders, "cpa_vnd": cpa_today_vnd, "reason": f"12h trưa spend {spend_vnd:,.0f}đ < 30% NS ({expected_noon:,.0f}đ). Chuyển NS sang camp tốt hơn."})
                    continue

            # SCALE_01: CPA hôm nay < 75k → Tăng NS 30%
            if orders > 0 and cpa_today_vnd < CPA_SCALE:
                max_budget = CONFIG["max_daily_budget_usd"]
                new_budget = min(daily_budget_usd * 1.3, max_budget)
                if new_budget > daily_budget_usd:
                    print(f"  🟢 SCALE_01: {name} — CPA {cpa_today_vnd:,.0f}đ < {CPA_SCALE:,.0f}đ → Tăng NS")
                    set_campaign_budget(cid, new_budget)
                    scales.append({"name": name, "pct": 30, "old_budget_vnd": usd_to_vnd(daily_budget_usd), "new_budget_vnd": usd_to_vnd(new_budget), "cpa_vnd": cpa_today_vnd, "orders": orders})

            # ALERT_01: Frequency > 2.5 HOẶC CTR giảm 30%
            if frequency > 2.5:
                print(f"  ⚠️ ALERT_01: {name} — Frequency {frequency:.2f} > 2.5")
                alerts.append({"name": name, "frequency": frequency, "ctr_drop_pct": 0})

            # Ghi nhận camp tốt (cho SCALE_02 / KILL_04 chuyển NS)
            if orders > 0 and cpa_today_vnd < CPA_TARGET:
                active_good_camps.append({
                    "id": cid,
                    "name": name,
                    "cpa": cpa_today_vnd,
                    "orders": orders,
                    "budget_usd": daily_budget_usd
                })

        # ====== REVIVE RULES (chỉ check campaign PAUSED, chạy lúc 0h) ======
        elif status == "PAUSED" and is_midnight:

            # REVIVE_01: CPA 3 ngày < 105k & 7 ngày < 105k & spend gần nhất <= 200k
            if cpa_3d < CPA_TARGET and cpa_7d < CPA_TARGET and spend_vnd <= 200000:
                print(f"  🔵 REVIVE_01: {name} — CPA tốt → Bật lại NS cũ")
                set_campaign_status(cid, "ACTIVE")
                revives.append({"name": name, "rule": "REVIVE_01", "cpa_3d_vnd": cpa_3d, "cpa_7d_vnd": cpa_7d, "budget_vnd": usd_to_vnd(daily_budget_usd)})

            # REVIVE_02: CPA 7 ngày < 105k nhưng 3 ngày >= 105k → Bật lại $10 test
            elif cpa_7d < CPA_TARGET and cpa_3d >= CPA_TARGET:
                print(f"  🔵 REVIVE_02: {name} — CPA 7 ngày tốt, 3 ngày xấu → Bật $10 test")
                set_campaign_budget(cid, 10.0)
                set_campaign_status(cid, "ACTIVE")
                revives.append({"name": name, "rule": "REVIVE_02", "cpa_3d_vnd": cpa_3d, "cpa_7d_vnd": cpa_7d, "budget_vnd": usd_to_vnd(10.0)})

    # Gửi báo cáo tổng
    date_str = datetime.now().strftime("%d/%m/%Y")
    avg_cpa = (total_spend_vnd // total_orders) if total_orders > 0 else 999999
    
    send_periodic_scan(
        hour=hour,
        date_str=date_str,
        kills=kills,
        redistributes=redistributes,
        scales=scales,
        alerts=alerts,
        active_count=active_count,
        total_spend_vnd=total_spend_vnd,
        total_orders=total_orders,
        avg_cpa_vnd=avg_cpa
    )
    
    if is_midnight and (revives or dead_creatives or kept_paused):
        send_midnight_revive(date_str, revives, dead_creatives, kept_paused)
    print(f"\n✅ Scan hoàn tất. Tổng spend: {total_spend_vnd:,.0f}đ | Đơn: {total_orders}")

    # Release lock
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()


if __name__ == "__main__":
    run_care()
