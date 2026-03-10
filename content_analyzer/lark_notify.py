import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

LARK_WEBHOOK_URL = os.getenv('LARK_WEBHOOK_URL')

def send_report(results_win, results_fail):
    if not LARK_WEBHOOK_URL:
        print("Chưa cấu hình LARK_WEBHOOK_URL, bỏ qua việc gửi tin nhắn.")
        return
        
    today = datetime.now().strftime('%d/%m/%Y')
    total = len(results_win) + len(results_fail)
    
    if total == 0:
        return
        
    content_lines = []
    content_lines.append([
        {"tag": "text", "text": f"📅 Ngày: {today} | Tổng: {total} video | "},
        {"tag": "text", "text": f"🟢 WIN: {len(results_win)} | 🔴 FAIL: {len(results_fail)}"}
    ])
    
    if results_win:
        content_lines.append([{"tag": "text", "text": "\n━━━━━━━━━━━━━━━━━━━━"}])
        content_lines.append([{"tag": "text", "text": "🟢 VIDEO WIN — CẦN NHÂN BẢN"}])
        content_lines.append([{"tag": "text", "text": "━━━━━━━━━━━━━━━━━━━━"}])
        
        for r in results_win:
            content_lines.append([{"tag": "text", "text": build_win_summary(r)}])
            
    if results_fail:
        content_lines.append([{"tag": "text", "text": "\n━━━━━━━━━━━━━━━━━━━━"}])
        content_lines.append([{"tag": "text", "text": "🔴 VIDEO FAIL — CẦN SỬA"}])
        content_lines.append([{"tag": "text", "text": "━━━━━━━━━━━━━━━━━━━━"}])
        
        for r in results_fail:
            content_lines.append([{"tag": "text", "text": build_fail_summary(r)}])
            
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "vi_VN": {
                    "title": f"📊 Báo Cáo Content 3 Ngày — {today}",
                    "content": content_lines
                }
            }
        }
    }
    
    requests.post(LARK_WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))

def build_win_summary(result):
    checks = result.get('checks', {})
    metrics_str = " | ".join([
        f"CTR: {checks.get('CTR', (0,0))[0]}%",
        f"Hook: {checks.get('Hook 3s', (0,0))[0]}%",
        f"Ret50: {checks.get('Retention 50%', (0,0))[0]}%",
    ])
    return f"\n🎬 {result.get('script_id', 'N/A')} | {result.get('camp_name', 'N/A')}\n📊 {result.get('score', '0/5')} | {metrics_str}\n📝 Phân tích:\n{result.get('analysis', '')[:300]}...\n"

def build_fail_summary(result):
    checks = result.get('checks', {})
    metrics_str = " | ".join([
        f"CTR: {checks.get('CTR', (0,0))[0]}%",
        f"Hook: {checks.get('Hook 3s', (0,0))[0]}%",
        f"Ret50: {checks.get('Retention 50%', (0,0))[0]}%",
    ])
    return f"\n🎬 {result.get('script_id', 'N/A')} | {result.get('camp_name', 'N/A')}\n📊 {result.get('score', '0/5')} | {metrics_str}\n🩺 Chẩn đoán:\n{result.get('analysis', '')[:300]}...\n"
