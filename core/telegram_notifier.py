"""
Telegram Notifier — Lollibooks Ads System
Format tuân thủ report_templates.md. Không tự ý thêm emoji hay đổi thứ tự section.
Đơn vị: VNĐ (VN) = "k", USD (KH/PH) = "$"
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

_group_id_path = os.path.join(os.path.dirname(__file__), 'telegram_group_id.txt')
with open(_group_id_path, 'r') as f:
    GROUP_ID = f.read().strip()

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
ACCOUNT_NAME = "Lollibooks VN 01"


def _send(text: str) -> bool:
    """Gửi tin nhắn raw vào nhóm (plain text, không parse_mode để giữ format ━━━)."""
    res = requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": GROUP_ID,
        "text": text,
    })
    if res.status_code != 200:
        print(f"[TelegramNotifier] ❌ Lỗi gửi: {res.text}")
        return False
    return True


def _vnd_k(vnd: int) -> str:
    """Số VNĐ → chuỗi 'XXXk'"""
    return f"{round(vnd / 1000)}k"


def _usd(usd: float) -> str:
    return f"${usd:.2f}"


# ─── MẪU 1: QUÉT ĐỊNH KỲ (mỗi 2 tiếng) ─────────────────────────────────────

def send_periodic_scan(
    hour: int,
    date_str: str,                  # "09/03/2026"
    kills: list,                    # [{"name", "rule", "spend_vnd", "orders", "cpa_vnd", "reason"}]
    redistributes: list,            # [{"amount_vnd", "from_name", "to_name", "to_cpa_vnd"}]
    scales: list,                   # [{"name", "pct", "old_budget_vnd", "new_budget_vnd", "cpa_vnd", "orders"}]
    alerts: list,                   # [{"name", "frequency", "ctr_drop_pct"}]
    active_count: int,
    total_spend_vnd: int,
    total_orders: int,
    avg_cpa_vnd: int,
) -> bool:
    """Báo cáo quét định kỳ — MẪU 1."""
    # Bỏ qua nếu không có hành động nào
    if not kills and not redistributes and not scales and not alerts:
        return True  # không gửi báo cáo rỗng (quy tắc 1)

    lines = [
        f"⏰ QUÉT {hour}h — {ACCOUNT_NAME}",
        f"📅 {date_str}",
    ]

    if kills:
        lines.append("\n━━━ ❌ TẮT ━━━")
        for k in kills:
            cpa_str = _vnd_k(k['cpa_vnd']) if k['orders'] > 0 else "--"
            lines.append(f"• {k['name']} → {k['rule']}: {k['reason']}")
            lines.append(f"  Spend: {_vnd_k(k['spend_vnd'])} | Đơn: {k['orders']} | CPA: {cpa_str}")

    if redistributes:
        lines.append("\n━━━ 💰 REDISTRIBUTE ━━━")
        for r in redistributes:
            lines.append(
                f"• {_vnd_k(r['amount_vnd'])} từ [{r['from_name']}] → [{r['to_name']}] "
                f"(CPA {_vnd_k(r['to_cpa_vnd'])})"
            )

    if scales:
        lines.append("\n━━━ 🚀 SCALE ━━━")
        for s in scales:
            lines.append(
                f"• {s['name']} tăng NS {s['pct']}% "
                f"({_vnd_k(s['old_budget_vnd'])} → {_vnd_k(s['new_budget_vnd'])})"
            )
            lines.append(f"  CPA: {_vnd_k(s['cpa_vnd'])} | Đơn hôm nay: {s['orders']}")

    if alerts:
        lines.append("\n━━━ ⚠️ CẢNH BÁO ━━━")
        for a in alerts:
            parts = []
            if a.get('frequency', 0) > 2.5:
                parts.append(f"Frequency {a['frequency']:.1f}")
            if a.get('ctr_drop_pct', 0) > 0:
                parts.append(f"CTR giảm {a['ctr_drop_pct']:.0f}%")
            lines.append(f"• {a['name']}: {' / '.join(parts)}")
            lines.append("  → Team thay creative")

    lines.append("\n━━━ TỔNG KẾT ━━━")
    lines.append(f"✅ Active: {active_count} camp")
    lines.append(f"💸 Spend hôm nay: {_vnd_k(total_spend_vnd)}")
    lines.append(f"📦 Đơn hôm nay: {total_orders}")
    lines.append(f"📊 CPA TB tài khoản: {_vnd_k(avg_cpa_vnd) if avg_cpa_vnd < 999999 else '--'}")

    return _send("\n".join(lines))


# ─── MẪU 2: TIÊU CHẬM (12h trưa) ────────────────────────────────────────────

def send_slow_spend_report(
    date_str: str,
    slow_camps: list,   # [{"name", "budget_vnd", "spent_vnd", "redirect_vnd", "to_name", "to_cpa_vnd"}]
    total_freed_vnd: int,
) -> bool:
    """Báo cáo camp tiêu chậm 12h — MẪU 2."""
    if not slow_camps:
        return True

    lines = [
        f"🐌 CAMP TIÊU CHẬM — 12h {date_str}",
        f"TK: {ACCOUNT_NAME}",
    ]

    for c in slow_camps:
        pct = int(c['spent_vnd'] / c['budget_vnd'] * 100) if c['budget_vnd'] > 0 else 0
        lines.append(f"\n• {c['name']}")
        lines.append(f"  NS ngày: {_vnd_k(c['budget_vnd'])} | Đã tiêu: {_vnd_k(c['spent_vnd'])} ({pct}%)")
        if c.get('to_name'):
            lines.append(
                f"  → Chuyển {_vnd_k(c['redirect_vnd'])} vào [{c['to_name']}] "
                f"(CPA {_vnd_k(c['to_cpa_vnd'])})"
            )
        else:
            lines.append("  → Không có camp CPA < 105k → Giữ NS, không redistribute")

    lines.append(f"\n📌 Tổng NS giải phóng: {_vnd_k(total_freed_vnd)}")
    return _send("\n".join(lines))


# ─── MẪU 3: BẬT LẠI CAMP (0h đêm) ──────────────────────────────────────────

def send_midnight_revive(
    date_str: str,
    revived: list,      # [{"name", "rule", "cpa_3d_vnd", "cpa_7d_vnd", "budget_vnd"}]
    dead_creatives: list,  # [{"name", "kill_count"}]
    kept_paused: list,  # [{"name", "cpa_3d_vnd", "cpa_7d_vnd"}]
) -> bool:
    """Báo cáo bật lại camp 0h — MẪU 3."""
    if not revived and not dead_creatives and not kept_paused:
        return True

    lines = [
        f"🔄 REVIEW CAMP CŨ — 00h {date_str}",
        f"TK: {ACCOUNT_NAME}",
    ]

    if revived:
        lines.append("\n━━━ ✅ BẬT LẠI ━━━")
        for r in revived:
            budget_str = _vnd_k(r['budget_vnd']) if r['rule'] == 'REVIVE-01' else "$10"
            note = "giữ NS" if r['rule'] == 'REVIVE-01' else "giảm NS về $10"
            lines.append(f"• {r['name']} → {r['rule']}")
            lines.append(f"  CPA 3 ngày: {_vnd_k(r['cpa_3d_vnd'])} | CPA 7 ngày: {_vnd_k(r['cpa_7d_vnd'])}")
            lines.append(f"  → Bật lại, {note}")

    if dead_creatives:
        lines.append("\n━━━ ☠️ CREATIVE CHẾT ━━━")
        for d in dead_creatives:
            lines.append(f"• {d['name']}: Bị tắt {d['kill_count']} lần / 7 ngày → Không bật lại")

    if kept_paused:
        lines.append("\n━━━ ⏸️ GIỮ TẮT ━━━")
        for k in kept_paused:
            lines.append(
                f"• {k['name']}: CPA 3 ngày {_vnd_k(k['cpa_3d_vnd'])}, "
                f"CPA 7 ngày {_vnd_k(k['cpa_7d_vnd'])} → Chưa đủ điều kiện"
            )

    total_revived = len(revived)
    total_dead = len(dead_creatives)
    lines.append(f"\n📌 Tổng bật lại: {total_revived} camp | Tổng creative chết: {total_dead}")

    return _send("\n".join(lines))


# ─── MẪU 4: CUỐI NGÀY (23h) ──────────────────────────────────────────────────

def send_daily_report(
    date_str: str,
    total_spend_vnd: int,
    total_orders: int,
    avg_cpa_vnd: int,
    target_cpa_vnd: int,
    roas: float,
    price_per_order_vnd: int,
    top3: list,         # [{"name", "spend_vnd", "orders", "cpa_vnd"}]
    worst3: list,       # [{"name", "spend_vnd", "orders", "cpa_vnd", "kill_rule"}]
    actions: dict,      # {kills, scales, redistribute_vnd, fatigue, revived, dead_creatives}
) -> bool:
    """Báo cáo cuối ngày — MẪU 4."""
    revenue_vnd = total_orders * price_per_order_vnd
    profit_vnd = revenue_vnd - total_spend_vnd
    diff_vnd = target_cpa_vnd - avg_cpa_vnd
    diff_pct = abs(diff_vnd) / target_cpa_vnd * 100 if target_cpa_vnd > 0 else 0
    on_target = avg_cpa_vnd <= target_cpa_vnd

    lines = [
        f"📊 BÁO CÁO NGÀY — {date_str}",
        f"TK: {ACCOUNT_NAME}",
        "\n━━━ TỔNG QUAN ━━━",
        f"💸 Tổng spend: {_vnd_k(total_spend_vnd)}",
        f"📦 Tổng đơn: {total_orders}",
        f"📊 CPA TB: {_vnd_k(avg_cpa_vnd)}",
        f"🎯 Target CPA: {_vnd_k(target_cpa_vnd)}",
    ]

    if total_orders == 0 or avg_cpa_vnd >= 999999:
        lines.append("⚠️ Không có camp nào đạt target. Cần review creative/offer NGAY.")
    elif on_target:
        lines.append(f"✅ DƯỚI TARGET: -{_vnd_k(abs(diff_vnd))} ({diff_pct:.0f}%)")
    else:
        lines.append(f"❌ TRÊN TARGET: +{_vnd_k(abs(diff_vnd))} ({diff_pct:.0f}%)")

    if top3:
        lines.append("\n━━━ TOP 3 CAMP NGON NHẤT ━━━")
        medals = ["🥇", "🥈", "🥉"]
        for i, c in enumerate(top3[:3]):
            lines.append(f"{medals[i]} {c['name']}")
            lines.append(
                f"  Spend: {_vnd_k(c['spend_vnd'])} | Đơn: {c['orders']} | CPA: {_vnd_k(c['cpa_vnd'])}"
            )

    if worst3:
        lines.append("\n━━━ TOP 3 CAMP TỆ NHẤT ━━━")
        for c in worst3[:3]:
            cpa_str = _vnd_k(c['cpa_vnd']) if c.get('orders', 0) > 0 else "--"
            lines.append(f"💀 {c['name']}")
            lines.append(
                f"  Spend: {_vnd_k(c['spend_vnd'])} | Đơn: {c.get('orders', 0)} | CPA: {cpa_str} "
                f"| Lý do tắt: {c.get('kill_rule', 'N/A')}"
            )

    lines.append("\n━━━ HÀNH ĐỘNG TRONG NGÀY ━━━")
    lines.append(f"❌ Tắt: {actions.get('kills', 0)} camp")
    lines.append(f"🚀 Scale: {actions.get('scales', 0)} camp")
    lines.append(f"💰 Redistribute: {_vnd_k(actions.get('redistribute_vnd', 0))}")
    lines.append(f"⚠️ Creative fatigue: {actions.get('fatigue', 0)} camp")
    lines.append(f"🔄 Bật lại: {actions.get('revived', 0)} camp")
    lines.append(f"☠️ Creative chết: {actions.get('dead_creatives', 0)}")

    lines.append("\n━━━ DOANH THU ƯỚC TÍNH ━━━")
    lines.append(f"📦 {total_orders} đơn × {_vnd_k(price_per_order_vnd)} = {_vnd_k(revenue_vnd)}")
    lines.append(f"💸 Chi phí: {_vnd_k(total_spend_vnd)}")
    lines.append(f"💹 ROAS: {roas:.1f}x")
    lines.append(f"💵 Lãi gộp ước tính: {_vnd_k(profit_vnd)}")

    return _send("\n".join(lines))


# ─── MẪU 6: LỖI HỆ THỐNG ────────────────────────────────────────────────────

def send_system_error(
    error_type: str,
    detail: str,
    affected_hour: str,
    next_retry_hour: str,
    admin_tag: str = "",
    consecutive_errors: int = 1,
) -> bool:
    """Báo cáo lỗi hệ thống — MẪU 6."""
    now_str = datetime.now().strftime("%H:%M %d/%m/%Y")
    lines = [
        f"🚨 LỖI HỆ THỐNG — {now_str}",
        f"\nLoại lỗi: {error_type}",
        f"Chi tiết: {detail}",
        f"Ảnh hưởng: Bỏ qua quét lúc {affected_hour}",
        f"Hành động: Thử lại vòng tiếp theo lúc {next_retry_hour}",
    ]
    if consecutive_errors >= 3 and admin_tag:
        lines.append(f"\n⚠️ Lỗi liên tục 3 lần → @{admin_tag} xử lý thủ công")
    return _send("\n".join(lines))


# ─── SHORTCUT: GỬI TIN TÙY CHỈNH ────────────────────────────────────────────

def send_custom(message: str) -> bool:
    return _send(message)


if __name__ == "__main__":
    # Test gửi mẫu quét định kỳ
    ok = send_periodic_scan(
        hour=19,
        date_str="09/03/2026",
        kills=[{
            "name": "[L24P000023][AI-Seller] Vanh.NTGT.9/3",
            "rule": "KILL-01",
            "spend_vnd": 162000,
            "orders": 0,
            "cpa_vnd": 0,
            "reason": "Spend 162k, 0 đơn"
        }],
        redistributes=[{
            "amount_vnd": 162000,
            "from_name": "Vanh.NTGT.9/3",
            "to_name": "TTTDT_HPT_ con gai v1",
            "to_cpa_vnd": 61000
        }],
        scales=[{
            "name": "[L24C030033] TTTDT_HPT_ con gai v1",
            "pct": 30,
            "old_budget_vnd": 1143500,
            "new_budget_vnd": 1486550,
            "cpa_vnd": 61000,
            "orders": 10
        }],
        alerts=[],
        active_count=3,
        total_spend_vnd=2348484,
        total_orders=27,
        avg_cpa_vnd=86981,
    )
    print("✅ Test OK" if ok else "❌ Test FAILED")
