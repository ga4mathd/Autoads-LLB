import os
import requests
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

access_token = os.getenv("META_ACCESS_TOKEN")
ad_account_id = os.getenv("META_AD_ACCOUNT_ID")
if not ad_account_id.startswith('act_'):
    ad_account_id = f'act_{ad_account_id}'

base_url = f"https://graph.facebook.com/v19.0"

PAGE_ID = "104293862687132"
VIDEO_ID = "1462075405587478"
PIXEL_ID = "1259289766031011"
LINK_WEB = "https://ai.lollibooks.net/ntgtcm"

CAMPAIGN_NAME = "[L24_VN]_AutoBot_Sales_CR_Test_V3"
ADSET_NAME = "Target_VN_30-45_Sales_CR_FB"
AD_NAME = "Ad_Video_Sales_NTGTCM_0803"

# CHUẨN HÓA CONTENT CHO SẢN PHẨM: "NGHỆ THUẬT GIAO TIẾP CHA MẸ"
AD_TEXT = """LÀM SAO ĐỂ CON CHỊU LẮNG NGHE MÀ CHA MẸ KHÔNG CẦN QUÁT MẮNG? 👨‍👩‍👧‍👦

Nhiều ba mẹ đau đầu vì con càng lớn càng bướng bỉnh, hay cãi lời và dần thu mình lại. Thực tế, con không hư, chỉ là do cách chúng ta giao tiếp chưa chạm được vào thế giới của con.

Cuốn sách "Nghệ Thuật Giao Tiếp Cha Mẹ" chính là chiếc chìa khóa gỡ rối cho hàng ngàn gia đình:
✨ Kỹ năng lắng nghe thấu cảm: Hiểu điều con chưa nói.
✨ Cách khen chê tinh tế: Giúp con tự tin, có trách nhiệm mà không sinh tâm lý chống đối.
✨ Chuyển hóa mệnh lệnh thành sự hợp tác: Dạy con tính kỷ luật mà không cần đòn roi hay lớn tiếng.

Đừng để khoảng cách giữa cha mẹ và con cái ngày một xa. Hãy bắt đầu thay đổi từ chính lời nói của bạn hôm nay!

🎁 Đăng ký ngay để nhận ưu đãi đặc biệt dành riêng cho ba mẹ trong hôm nay!"""

AD_HEADLINE = "Nghệ Thuật Giao Tiếp Cha Mẹ - Dạy Con Không Cần Quát Mắng!"

print(f"🚀 Bắt đầu tạo Campaign DOANH SỐ (Sự kiện: Hoàn tất đăng ký)...")

try:
    print("0. Lấy Thumbnail...")
    vid_res = requests.get(f"{base_url}/{VIDEO_ID}", params={'fields': 'picture', 'access_token': access_token})
    thumb_url = vid_res.json().get('picture')

    print("1. Đang tạo Campaign (Mục tiêu: Doanh số - SALES)...")
    camp_res = requests.post(f"{base_url}/{ad_account_id}/campaigns", data={
        'access_token': access_token, 'name': CAMPAIGN_NAME, 
        'objective': 'OUTCOME_SALES', # Mục tiêu Doanh số
        'status': 'PAUSED', 'special_ad_categories': '["NONE"]'
    })
    campaign_id = camp_res.json()['id']
    print(f"   ✅ Campaign ID: {campaign_id}")

    print("2. Đang tạo Ad Set (Sự kiện chuyển đổi: COMPLETE_REGISTRATION)...")
    targeting = {
        "geo_locations": {"countries": ["VN"]}, "age_min": 30, "age_max": 45,
        "publisher_platforms": ["facebook"],
        "facebook_positions": [
            "feed", 
            "marketplace", 
            "video_feeds", 
            "story", 
            "facebook_reels", 
            "instream_video", 
            "search"
        ],
        "targeting_automation": {"advantage_audience": 0}
    }
    
    # SỬA LẠI: Campaign Doanh số nhưng Tối ưu sự kiện Hoàn tất đăng ký (COMPLETE_REGISTRATION)
    promoted_object = {
        "pixel_id": PIXEL_ID,
        "custom_event_type": "COMPLETE_REGISTRATION" 
    }

    adset_res = requests.post(f"{base_url}/{ad_account_id}/adsets", data={
        'access_token': access_token, 'name': ADSET_NAME, 'campaign_id': campaign_id,
        'status': 'PAUSED', 'daily_budget': 1000, 'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'OFFSITE_CONVERSIONS', 
        'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
        'promoted_object': json.dumps(promoted_object),
        'targeting': json.dumps(targeting),
    })
    
    if adset_res.status_code != 200:
        print("Lỗi tạo Adset:", adset_res.json())
        exit(1)
    adset_id = adset_res.json()['id']
    print(f"   ✅ Ad Set ID: {adset_id}")

    print("3. Đang tạo Ad Creative (Chuẩn Content Nghệ thuật giao tiếp)...")
    creative_payload = {
        'access_token': access_token,
        'name': f"Creative_{AD_NAME}",
        'object_story_spec': json.dumps({
            'page_id': PAGE_ID,
            'video_data': {
                'video_id': VIDEO_ID,
                'image_url': thumb_url,
                'message': AD_TEXT,
                'title': AD_HEADLINE,
                'call_to_action': {
                    'type': 'LEARN_MORE',
                    'value': {'link': LINK_WEB}
                }
            }
        })
    }
    creative_res = requests.post(f"{base_url}/{ad_account_id}/adcreatives", data=creative_payload)
    if creative_res.status_code != 200:
        print("Lỗi tạo Creative:", creative_res.json())
        exit(1)
    creative_id = creative_res.json()['id']
    print(f"   ✅ Creative ID: {creative_id}")

    print("4. Đang Publish Ad...")
    ad_res = requests.post(f"{base_url}/{ad_account_id}/ads", data={
        'access_token': access_token, 'name': AD_NAME, 'adset_id': adset_id,
        'creative': json.dumps({'creative_id': creative_id}), 'status': 'PAUSED'
    })
    ad_id = ad_res.json()['id']
    print(f"   ✅ Ad ID: {ad_id}")

    print(f"\n🎉 HOÀN TẤT!")

except Exception as e:
    print(f"❌ Lỗi: {e}")
