import os
import requests
from dotenv import load_dotenv

load_dotenv()
access_token = os.getenv("META_ACCESS_TOKEN")
ad_account_id = os.getenv("META_AD_ACCOUNT_ID")

if not ad_account_id.startswith("act_"):
    ad_account_id = f"act_{ad_account_id}"

url = f"https://graph.facebook.com/v19.0/{ad_account_id}/insights"
params = {
    "level": "ad",
    "fields": "campaign_name,ad_name,ad_id,spend,actions,video_play_actions,video_avg_time_watched_actions",
    "date_preset": "last_7d",
    "access_token": access_token
}

try:
    response = requests.get(url, params=params)
    data = response.json()
    
    print("🎥 Đang phân tích sâu VIDEO METRICS của các Ads...\n")
    
    for item in data.get("data", []):
        spend = float(item.get("spend", 0))
        if spend < 5: continue # Bỏ qua các ad tiêu ít
        
        regs = 0
        if "actions" in item:
            for a in item["actions"]:
                if a["action_type"] in ["complete_registration", "offsite_conversion.fb_pixel_complete_registration", "omni_complete_registration"]:
                    regs = int(a.get("value", 0))
                    break
        
        cpa = spend / regs if regs > 0 else 0
        
        # Video Metrics
        video_plays = 0
        video_thruplay = 0
        if "video_play_actions" in item:
            for v in item["video_play_actions"]:
                if v["action_type"] == "video_view":
                    video_plays = int(v.get("value", 0))
                    
        # Lấy ThruPlay (Xem 15s hoặc hết video)
        if "actions" in item:
            for a in item["actions"]:
                if a["action_type"] == "video_view": # Trong API đôi khi video_view là Thruplay/3s tuỳ config, ta đếm để so sánh tương đối
                    pass
        
        # Thử lấy thời gian xem trung bình (nếu có)
        avg_watch_time = 0.0
        if "video_avg_time_watched_actions" in item:
            for v in item["video_avg_time_watched_actions"]:
                 if v["action_type"] == "video_view":
                     avg_watch_time = float(v.get("value", 0))

        # Tính toán
        play_rate = (video_plays / regs) if regs > 0 else 0 # Tỷ lệ View ra 1 Đăng ký
        
        print(f"⭐ Ad: {item['ad_name']} (Camp: {item['campaign_name']})")
        print(f"   Spend: ${spend:.2f} | Regs: {regs} | CPA: ${cpa:.2f}")
        print(f"   Video Plays (3s+): {video_plays} views")
        print(f"   Avg Watch Time: {avg_watch_time:.2f} giây")
        if regs > 0:
            print(f"   Trung bình cần {int(video_plays/regs)} lượt xem video để ra 1 đơn.")
        print("-" * 40)

except requests.exceptions.RequestException as e:
    print("❌ API Error:", e)
