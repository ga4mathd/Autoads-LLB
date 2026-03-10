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
CAMPAIGN_NAME = "[L24_VN]_AutoBot_Mess_ToiUuTinNhan_Test_V4"
ADSET_NAME = "Target_VN_30-45_FBOnly"
AD_NAME = "Ad_Video_0803"

print(f"🚀 Bắt đầu tạo Campaign TỰ ĐỘNG (Trạng thái PAUSED) cho Page ID: {PAGE_ID}...")

try:
    print("0. Lấy Thumbnail tự động từ Video ID...")
    vid_res = requests.get(f"{base_url}/{VIDEO_ID}", params={'fields': 'picture', 'access_token': access_token})
    thumb_url = vid_res.json().get('picture')
    print("   ✅ Đã lấy được Thumbnail URL")

    print("1. Đang tạo Campaign...")
    camp_res = requests.post(f"{base_url}/{ad_account_id}/campaigns", data={
        'access_token': access_token, 'name': CAMPAIGN_NAME, 'objective': 'OUTCOME_ENGAGEMENT',
        'status': 'PAUSED', 'special_ad_categories': '["NONE"]'
    })
    campaign_id = camp_res.json()['id']
    print(f"   ✅ Campaign ID: {campaign_id}")

    print("2. Đang tạo Ad Set...")
    targeting = {
        "geo_locations": {"countries": ["VN"]}, "age_min": 30, "age_max": 45,
        "publisher_platforms": ["facebook"], "facebook_positions": ["feed", "video_feeds"],
        "targeting_automation": {"advantage_audience": 0}
    }
    adset_res = requests.post(f"{base_url}/{ad_account_id}/adsets", data={
        'access_token': access_token, 'name': ADSET_NAME, 'campaign_id': campaign_id,
        'status': 'PAUSED', 'daily_budget': 1000, 'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'CONVERSATIONS', 'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
        'destination_type': 'MESSENGER', 'promoted_object': json.dumps({'page_id': PAGE_ID}),
        'targeting': json.dumps(targeting),
    })
    adset_id = adset_res.json()['id']
    print(f"   ✅ Ad Set ID: {adset_id}")

    print("3. Đang tạo Ad Creative (Gắn Video)...")
    creative_payload = {
        'access_token': access_token,
        'name': f"Creative_{AD_NAME}",
        'object_story_spec': json.dumps({
            'page_id': PAGE_ID,
            'video_data': {
                'video_id': VIDEO_ID,
                'image_url': thumb_url,
                'message': '🔥 Tự học cho bé tại nhà nhàn tênh. Đặt mua sách Lollibooks ngay hôm nay!',
                'call_to_action': {'type': 'MESSAGE_PAGE'}
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

    print(f"\n🎉 HOÀN TẤT! Đã lên xong toàn bộ luồng Campaign.")

except Exception as e:
    print(f"❌ Lỗi: {e}")
