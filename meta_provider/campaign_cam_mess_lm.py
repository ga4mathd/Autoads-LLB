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

# Dùng chung Page ID và Video ID cũ (làm ví dụ)
PAGE_ID = "104293862687132"
VIDEO_ID = "1462075405587478"

CAMPAIGN_NAME = "[L24_CAM]_AutoBot_Mess_LM_NTGTCM_0803"
ADSET_NAME = "Target_KH_Mess_LM_FB"
AD_NAME = "Ad_Video_Khmer_0803"

# Dịch sang tiếng Khmer:
# Tiêu đề: សិល្បៈនៃការប្រាស្រ័យទាក់ទងជាមួយកូន - បង្រៀនកូនដោយមិនបាច់ស្រែក! (Nghệ Thuật Giao Tiếp Cha Mẹ - Dạy Con Không Cần Quát Mắng!)
AD_HEADLINE = "សិល្បៈនៃការប្រាស្រ័យទាក់ទងជាមួយកូន - បង្រៀនកូនដោយមិនបាច់ស្រែក!"

AD_TEXT = """តើធ្វើដូចម្តេចដើម្បីឱ្យកូនស្តាប់បង្គាប់ដោយមិនបាច់ស្រែកស្តីបន្ទោស? 👨‍👩‍👧‍👦

ឪពុកម្តាយជាច្រើនឈឺក្បាលព្រោះកូនកាន់តែធំ កាន់តែរឹងរូស ចូលចិត្តប្រកែក និងឃ្លាតឆ្ងាយ។ តាមពិតកូនមិនមែនខូចទេ គ្រាន់តែវិធីប្រាស្រ័យទាក់ទងរបស់យើងមិនទាន់ចូលដល់ពិភពលោករបស់ពួកគេ។

សៀវភៅ "សិល្បៈនៃការប្រាស្រ័យទាក់ទងរបស់មាតាបិតា" គឺជាកូនសោរដោះស្រាយបញ្ហាសម្រាប់គ្រួសាររាប់ពាន់៖
✨ ជំនាញស្តាប់ដោយយល់ចិត្ត៖ យល់ពីអ្វីដែលកូនមិនទាន់និយាយ។
✨ វិធីសរសើរ និងរិះគន់ប្រកបដោយភាពឆ្លាតវៃ៖ ជួយកូនឱ្យមានទំនុកចិត្ត មានការទទួលខុសត្រូវ ដោយមិនបង្កើតគំនិតប្រឆាំង។
✨ ប្តូរបញ្ជាទៅជាការសហការ៖ បង្រៀនកូនឱ្យមានវិន័យដោយមិនបាច់វាយដំ ឬស្រែកខ្លាំងៗ។

កុំបណ្តោយឱ្យគម្លាតរវាងឪពុកម្តាយ និងកូនកាន់តែឆ្ងាយ។ ចាប់ផ្តើមផ្លាស់ប្តូរពីពាក្យសម្តីរបស់អ្នកថ្ងៃនេះ!

🎁 ចុះឈ្មោះឥឡូវនេះដើម្បីទទួលបានការផ្តល់ជូនពិសេសសម្រាប់តែឪពុកម្តាយថ្ងៃនេះ!"""

print(f"🚀 Bắt đầu tạo Campaign Mess CĐ / Mess LM (Cam) - Tiếng Khmer...")

try:
    print("0. Lấy Thumbnail...")
    vid_res = requests.get(f"{base_url}/{VIDEO_ID}", params={'fields': 'picture', 'access_token': access_token})
    thumb_url = vid_res.json().get('picture')

    print("1. Đang tạo Campaign (Tương tác - Mess)...")
    camp_res = requests.post(f"{base_url}/{ad_account_id}/campaigns", data={
        'access_token': access_token, 'name': CAMPAIGN_NAME, 
        'objective': 'OUTCOME_ENGAGEMENT',
        'status': 'PAUSED', 'special_ad_categories': '["NONE"]'
    })
    campaign_id = camp_res.json()['id']
    print(f"   ✅ Campaign ID: {campaign_id}")

    print("2. Đang tạo Ad Set (Quốc gia: KH, Tối ưu: LƯỢT MUA QUA MESS)...")
    targeting = {
        "geo_locations": {"countries": ["KH"]}, 
        "age_min": 18, "age_max": 65, # Target rộng cho Cam
        "publisher_platforms": ["facebook"],
        "facebook_positions": [
            "feed", "marketplace", "video_feeds", "story", "facebook_reels", "instream_video", "search"
        ],
        "targeting_automation": {"advantage_audience": 0}
    }

    adset_res = requests.post(f"{base_url}/{ad_account_id}/adsets", data={
        'access_token': access_token, 'name': ADSET_NAME, 'campaign_id': campaign_id,
        'status': 'PAUSED', 'daily_budget': 1000, 'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'MESSAGING_PURCHASE_CONVERSION', # Tối ưu lượt mua qua tin nhắn
        'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
        'destination_type': 'MESSENGER',
        'promoted_object': json.dumps({'page_id': PAGE_ID}),
        'targeting': json.dumps(targeting),
    })
    
    if adset_res.status_code != 200:
        print("Lỗi tạo Adset:", adset_res.json())
        exit(1)
    adset_id = adset_res.json()['id']
    print(f"   ✅ Ad Set ID: {adset_id}")

    print("3. Đang tạo Ad Creative (Nội dung tiếng Khmer)...")
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
                    'type': 'MESSAGE_PAGE', # Nút bấm phải là Gửi tin nhắn
                    
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

    print(f"\n🎉 HOÀN TẤT! Đã lên xong camp Mess Lượt Mua thị trường KH.")

except Exception as e:
    print(f"❌ Lỗi: {e}")
