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
    'fields': 'campaign_name,spend,actions,action_values,purchase_roas',
    'date_preset': 'last_7d', # Lấy 7 ngày qua để đảm bảo có số liệu doanh thu
    'access_token': access_token
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        print(f"✅ Dữ liệu 7 ngày qua (Last 7 Days):")
        for item in data['data']:
            name = item.get('campaign_name', 'Unknown')
            spend = item.get('spend', '0')
            
            # Lấy số lượt mua (Purchases)
            purchases = 0
            if 'actions' in item:
                for action in item['actions']:
                    if action['action_type'] in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        purchases += int(action.get('value', 0))
            
            # Lấy doanh thu (Revenue / Action Values)
            revenue = 0.0
            if 'action_values' in item:
                for val in item['action_values']:
                    if val['action_type'] in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        revenue += float(val.get('value', 0.0))
                        
            # Lấy ROAS
            roas = 0.0
            if 'purchase_roas' in item:
                for r in item['purchase_roas']:
                    if r['action_type'] in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        roas = float(r.get('value', 0.0))
            
            print(f"- Camp: {name}\n  Spend: ${spend} | Purchases: {purchases} | Revenue: ${revenue:.2f} | ROAS: {roas:.2f}\n")
    else:
        print("✅ Không có dữ liệu chi tiêu/doanh thu trong 7 ngày qua.")

except requests.exceptions.RequestException as e:
    print("❌ API Error:", e.response.json() if hasattr(e, 'response') and e.response is not None else e)
