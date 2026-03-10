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
    "fields": "campaign_name,ad_name,ad_id,spend,actions",
    "date_preset": "today",
    "access_token": access_token
}

good_camps = [
    "[LPAK-CAM] [AI-Seller]Vanh.TBLB",
    "[L24P000023][AI-Seller] Vanh.NTGT.5/3",
    "[L24C030033][AI-Seller] TTTDT_HPT_ con gai v1"
]

try:
    response = requests.get(url, params=params)
    data = response.json()
    
    print("🔍 Đang trích xuất nội dung của các Ads ra số rẻ nhất hôm nay...\n")
    
    found_ads = []
    
    for item in data.get("data", []):
        camp_name = item.get("campaign_name", "")
        if camp_name in good_camps:
            spend = float(item.get("spend", 0))
            regs = 0
            if "actions" in item:
                for a in item["actions"]:
                    if a["action_type"] in ["complete_registration", "offsite_conversion.fb_pixel_complete_registration", "omni_complete_registration"]:
                        regs = int(a.get("value", 0))
                        break
            
            if regs > 0:
                found_ads.append({"ad_id": item["ad_id"], "ad_name": item["ad_name"], "camp_name": camp_name, "spend": spend, "regs": regs})
    
    # Sort by cheapest
    found_ads.sort(key=lambda x: x["spend"]/x["regs"] if x["regs"]>0 else 999)
    
    # Chỉ lấy top 3 ads rẻ nhất để phân tích sâu
    for idx, ad in enumerate(found_ads[:3]):
        ad_id = ad["ad_id"]
        cpa = ad["spend"] / ad["regs"]
        
        # Get creative ID
        ad_url = f"https://graph.facebook.com/v19.0/{ad_id}"
        ad_res = requests.get(ad_url, params={"fields": "creative", "access_token": access_token}).json()
        
        body_text = "Không tìm thấy text"
        creative_name = "Unknown"
        
        if "creative" in ad_res and "id" in ad_res["creative"]:
            creative_id = ad_res["creative"]["id"]
            
            # Get creative details
            cr_url = f"https://graph.facebook.com/v19.0/{creative_id}"
            cr_res = requests.get(cr_url, params={"fields": "name,body,object_story_spec", "access_token": access_token}).json()
            
            creative_name = cr_res.get("name", "Unknown")
            body_text = cr_res.get("body", "")
            
            # If body is empty, extract from object_story_spec (video/link posts)
            if not body_text and "object_story_spec" in cr_res:
                spec = cr_res["object_story_spec"]
                if "video_data" in spec:
                    body_text = spec["video_data"].get("message", "")
                elif "link_data" in spec:
                    body_text = spec["link_data"].get("message", "")
                    
        print(f"⭐ TOP {idx+1}: {ad['camp_name']}")
        print(f"   Ad Name: {ad['ad_name']}")
        print(f"   Chỉ số: Spend ${ad['spend']:.2f} | Regs: {ad['regs']} | CPA: ${cpa:.2f}")
        print(f"   Nội dung text (Snippet):\n   {repr(body_text[:300])}...\n")

except requests.exceptions.RequestException as e:
    print("❌ API Error:", e)
