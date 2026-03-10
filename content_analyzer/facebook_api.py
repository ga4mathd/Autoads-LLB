import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')
API_VERSION = 'v19.0'
BASE_URL = f'https://graph.facebook.com/{API_VERSION}'

def pull_ad_metrics(post_id, start_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = start_date + timedelta(days=3)
    
    ad_id = find_ad_by_post_id(post_id)
    if not ad_id:
        print(f"Không tìm thấy ad cho post_id: {post_id}")
        return empty_metrics()
        
    url = f'{BASE_URL}/{ad_id}/insights'
    params = {
        'access_token': ACCESS_TOKEN,
        'time_range': {
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d'),
        },
        'fields': ','.join([
            'impressions', 'reach', 'ctr', 'cpm', 'cpc',
            'cost_per_action_type', 'video_play_actions',
            'video_3_sec_watched_actions', 'video_p25_watched_actions',
            'video_p50_watched_actions', 'video_p75_watched_actions',
            'video_p95_watched_actions', 'video_p100_watched_actions',
            'video_thruplay_watched_actions', 'spend', 'actions'
        ]),
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'data' not in data or not data['data']:
        return empty_metrics()
        
    insights = data['data'][0]
    
    impressions = int(insights.get('impressions', 0))
    views_3s = extract_video_metric(insights, 'video_3_sec_watched_actions')
    views_p25 = extract_video_metric(insights, 'video_p25_watched_actions')
    views_p50 = extract_video_metric(insights, 'video_p50_watched_actions')
    views_p75 = extract_video_metric(insights, 'video_p75_watched_actions')
    views_p100 = extract_video_metric(insights, 'video_p100_watched_actions')
    video_views = extract_video_metric(insights, 'video_play_actions')
    
    hook_rate_3s = round((views_3s / impressions * 100), 2) if impressions > 0 else 0
    retention_25 = round((views_p25 / impressions * 100), 2) if impressions > 0 else 0
    retention_50 = round((views_p50 / impressions * 100), 2) if impressions > 0 else 0
    retention_75 = round((views_p75 / impressions * 100), 2) if impressions > 0 else 0
    retention_100 = round((views_p100 / impressions * 100), 2) if impressions > 0 else 0
    
    cpa = 0
    cost_per_action = insights.get('cost_per_action_type', [])
    for action in cost_per_action:
        if action.get('action_type') in ['offsite_conversion.fb_pixel_purchase', 'onsite_conversion.messaging_first_reply', 'lead']:
            cpa = float(action.get('value', 0))
            break
            
    return {
        'impressions': impressions,
        'reach': int(insights.get('reach', 0)),
        'ctr': float(insights.get('ctr', 0)),
        'cpm': float(insights.get('cpm', 0)),
        'cpc': float(insights.get('cpc', 0)),
        'cpa': cpa,
        'spend': float(insights.get('spend', 0)),
        'video_views': video_views,
        'hook_rate_3s': hook_rate_3s,
        'retention_25': retention_25,
        'retention_50': retention_50,
        'retention_75': retention_75,
        'retention_100': retention_100,
        'views_3s_raw': views_3s,
        'views_p25_raw': views_p25,
        'views_p50_raw': views_p50,
        'views_p75_raw': views_p75,
        'views_p100_raw': views_p100,
    }

def find_ad_by_post_id(post_id):
    url = f'{BASE_URL}/{AD_ACCOUNT_ID}/ads'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,creative{effective_object_story_id}',
        'filtering': f'[{{"field":"effective_status","operator":"IN","value":["ACTIVE","PAUSED","COMPLETED"]}}]',
        'limit': 500,
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    for ad in data.get('data', []):
        creative = ad.get('creative', {})
        story_id = creative.get('effective_object_story_id', '')
        if story_id and post_id in story_id:
            return ad['id']
            
    return None

def extract_video_metric(insights, field_name):
    actions = insights.get(field_name, [])
    if actions and isinstance(actions, list):
        return int(actions[0].get('value', 0))
    return 0

def empty_metrics():
    return {
        'impressions': 0, 'reach': 0, 'ctr': 0, 'cpm': 0, 'cpc': 0, 'cpa': 0, 'spend': 0, 'video_views': 0,
        'hook_rate_3s': 0, 'retention_25': 0, 'retention_50': 0, 'retention_75': 0, 'retention_100': 0,
        'views_3s_raw': 0, 'views_p25_raw': 0, 'views_p50_raw': 0, 'views_p75_raw': 0, 'views_p100_raw': 0,
    }
