import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('META_ACCESS_TOKEN')
ad_account_id = os.getenv('META_AD_ACCOUNT_ID')

if not access_token or not ad_account_id:
    print("Error: Missing token or account ID.")
    exit(1)

# Ensure account ID has 'act_' prefix
if not ad_account_id.startswith('act_'):
    ad_account_id = f'act_{ad_account_id}'

url = f"https://graph.facebook.com/v19.0/{ad_account_id}/insights"

params = {
    'level': 'campaign',
    'fields': 'campaign_name,spend,actions,cost_per_action_type',
    'date_preset': 'today',
    'access_token': access_token
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        print(f"✅ Success! Pulled data for {len(data['data'])} campaigns today.")
        for item in data['data']:
            name = item.get('campaign_name', 'Unknown')
            spend = item.get('spend', '0')
            print(f"- Campaign: {name} | Spend: ${spend}")
    else:
        print("✅ Success! Connection works, but no active spend/data for today yet.")

except requests.exceptions.RequestException as e:
    print("❌ API Error:")
    if hasattr(e, 'response') and e.response is not None:
         print(e.response.json())
    else:
         print(e)
