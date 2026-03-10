import os, requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

token = os.getenv('META_ACCESS_TOKEN')
account = os.getenv('META_AD_ACCOUNT_ID')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
USD_TO_VND = 25400
GROUP_ID = open('core/telegram_group_id.txt').read().strip()


def usd_to_vnd(usd):
    return int(usd * USD_TO_VND)


def extract_orders(actions):
    amap = {a["action_type"]: int(a.get("value", 0)) for a in actions}
    return (
        amap.get("omni_complete_registration", 0)
        or amap.get("onsite_conversion.messaging_conversation_started_7d", 0)
        or amap.get("offsite_conversion.fb_pixel_complete_registration", 0)
    )


# Lấy insights hôm nay
res = requests.get(
    f"https://graph.facebook.com/v19.0/{account}/insights",
    params={
        "access_token": token,
        "level": "campaign",
        "fields": "campaign_id,campaign_name,spend,actions",
        "date_preset": "today",
        "limit": 500,
    },
    timeout=20,
)

camps = []
total_spend = 0
total_orders = 0

for item in res.json().get("data", []):
    spend_usd = float(item.get("spend", 0))
    if spend_usd < 0.01:
        continue
    orders = extract_orders(item.get("actions", []))
    spend_vnd = usd_to_vnd(spend_usd)
    cpa_usd = (spend_usd / orders) if orders > 0 else 0
    total_spend += spend_vnd
    total_orders += orders
    camps.append(
        {
            "name": item["campaign_name"],
            "spend_vnd": spend_vnd,
            "spend_usd": spend_usd,
            "orders": orders,
            "cpa_usd": cpa_usd,
        }
    )

# Sort: có đơn & CPA tốt lên trước, 0 đơn xuống dưới
camps.sort(key=lambda x: x["cpa_usd"] if x["cpa_usd"] > 0 else 9999)

now_str = datetime.now().strftime("%H:%M %d/%m/%Y")
CPA_OK = 4.13    # ~105k VND ngưỡng target
CPA_GOOD = 3.0   # ~75k VND ngưỡng scale

lines = [
    f"📊 <b>BÁO CÁO ADS — {now_str}</b>",
    f"💸 Tổng spend: {total_spend:,.0f}đ  |  📦 Tổng KQ: {total_orders}",
    "",
]

for c in camps:
    cpa_str = f"${c['cpa_usd']:.2f}" if c["cpa_usd"] > 0 else "—"
    if c["orders"] == 0:
        icon = "⚫"
    elif c["cpa_usd"] <= CPA_GOOD:
        icon = "🟢"
    elif c["cpa_usd"] <= CPA_OK:
        icon = "🟡"
    else:
        icon = "🔴"

    lines.append(
        f"{icon} <b>{c['name'][:42]}</b>\n"
        f"   Spend: {c['spend_vnd']:,.0f}đ (${c['spend_usd']:.2f}) | KQ: {c['orders']} | CPA: {cpa_str}"
    )

text = "\n".join(lines)

r = requests.post(
    f"https://api.telegram.org/bot{bot_token}/sendMessage",
    json={"chat_id": GROUP_ID, "text": text, "parse_mode": "HTML"},
)

if r.status_code == 200:
    print("✅ Đã gửi báo cáo vào nhóm!")
else:
    print(f"❌ Lỗi: {r.text}")

print("\n--- Preview ---")
print(text)
