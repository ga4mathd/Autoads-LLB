import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('META_ACCESS_TOKEN')
ad_account_id = os.getenv('META_AD_ACCOUNT_ID')

if not ad_account_id.startswith('act_'):
    ad_account_id = f'act_{ad_account_id}'

url = f"https://graph.facebook.com/v19.0/{ad_account_id}/insights"

params = {
    'level': 'campaign',
    'fields': 'campaign_name,spend,actions,cost_per_action_type',
    'date_preset': 'last_7d',
    'access_token': access_token
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        print(f"✅ Dữ liệu 7 ngày qua (Last 7 Days) - CPA Complete Registration:")
        for item in data['data']:
            name = item.get('campaign_name', 'Unknown')
            spend = float(item.get('spend', 0))
            
            # Lấy số lượt Hoàn tất đăng ký (Complete Registration)
            registrations = 0
            if 'actions' in item:
                for action in item['actions']:
                    if action['action_type'] in ['complete_registration', 'offsite_conversion.fb_pixel_complete_registration', 'omni_complete_registration']:
                        registrations = int(action.get('value', 0))
                        break # Chỉ lấy 1 loại đại diện để tránh cộng dồn sai
            
            # Lấy CPA Hoàn tất đăng ký
            cpa = 0.0
            if 'cost_per_action_type' in item:
                for cost in item['cost_per_action_type']:
                    if cost['action_type'] in ['complete_registration', 'offsite_conversion.fb_pixel_complete_registration', 'omni_complete_registration']:
                        cpa = float(cost.get('value', 0.0))
                        break
            
            if spend > 0:
                print(f"- Camp: {name}")
                print(f"  Spend: ${spend:.2f} | Registrations: {registrations} | CPA: ${cpa:.2f}\n")
    else:
        print("✅ Không có dữ liệu chi tiêu trong 7 ngày qua.")

except requests.exceptions.RequestException as e:
    print("❌ API Error:", e.response.json() if hasattr(e, 'response') and e.response is not None else e)
