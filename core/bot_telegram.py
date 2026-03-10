import os
import requests
import time
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

def get_updates():
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        for update in data.get("result", []):
            if "message" in update and "chat" in update["message"]:
                chat = update["message"]["chat"]
                text = update["message"].get("text", "")
                if chat.get("type") in ["group", "supergroup"]:
                    return chat['id'], chat.get('title')
    else:
        print("Lỗi API Telegram:", res.status_code, res.text)
    return None, None

chat_id, title = get_updates()

if chat_id:
    print(f"🎉 Đã kết nối với Group: {title} (ID: {chat_id})")
    
    # Gửi tin nhắn test
    msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🤖 **[Hệ Thống Stella]**\nĐã nhận Group! Từ giờ tôi sẽ gửi báo cáo Ads tự động vào đây mỗi 2 tiếng.",
        "parse_mode": "Markdown"
    }
    msg_res = requests.post(msg_url, json=payload)
    if msg_res.status_code == 200:
        print("✅ Đã gửi tin nhắn test thành công.")
        
        # Lưu lại ID vào file để sau này dùng
        with open(os.path.join(os.path.dirname(__file__), 'telegram_group_id.txt'), 'w') as f:
            f.write(str(chat_id))
    else:
        print("❌ Lỗi gửi tin nhắn:", msg_res.text)
else:
    print("⏳ Không tìm thấy tin nhắn mới nhất trong Group. Bạn hãy vào Group và nhắn thêm 1 dòng nữa (vd: 'Hello Stella') để bot bắt được ID nhé.")
