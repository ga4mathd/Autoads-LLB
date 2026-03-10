import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.getenv('COMMAND_STATION_SHEET_ID')
SHEET_NAME = 'Lên Camp'

def get_client():
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.credentials', 'google_service_account.json')
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)

def get_videos_to_analyze():
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    
    all_rows = sheet.get_all_records(head=2)
    today = datetime.now().date()
    three_days_ago = today - timedelta(days=3)
    
    videos_to_analyze = []
    
    for i, row in enumerate(all_rows, start=3):
        start_date_str = row.get('Ngày bắt đầu', '')
        classification = row.get('Phân loại', '')
        post_id = row.get('ID Bài viết (*)', '')
        
        if classification or not post_id or not start_date_str:
            continue
            
        try:
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            continue
            
        if start_date <= three_days_ago:
            videos_to_analyze.append({
                'row_number': i,
                'script_id': row.get('Kịch bản (*)', ''),
                'camp_name': row.get('Tên Camp (*)', ''),
                'market': row.get('Market (*)', ''),
                'camp_type': row.get('Loại Camp (*)', ''),
                'adset': row.get('Tên AdSet (*)', ''),
                'age_min': row.get('Tuổi Min', ''),
                'age_max': row.get('Tuổi Max', ''),
                'post_id': post_id,
                'video_link': row.get('Link Drive Video (*)', ''),
                'caption': row.get('Caption (*)', ''),
                'cta': row.get('CTA', ''),
                'budget': row.get('NS ngày (VND) (*)', ''),
                'start_date': start_date_str,
            })
            
    return videos_to_analyze

def write_analysis(row_number, metrics, result):
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    
    # Cột P-AA
    sheet.update(f'P{row_number}', [[
        metrics.get('impressions', 0),
        metrics.get('reach', 0),
        metrics.get('ctr', 0),
        metrics.get('cpm', 0),
        metrics.get('cpc', 0),
        metrics.get('cpa', 0),
        metrics.get('video_views', 0),
        metrics.get('hook_rate_3s', 0),
        metrics.get('retention_25', 0),
        metrics.get('retention_50', 0),
        metrics.get('retention_75', 0),
        metrics.get('retention_100', 0),
    ]])
    
    # Cột AB-AF
    sheet.update(f'AB{row_number}', [[
        result['classification'],
        result['score'],
        result['analysis'],
        result['recommendations'],
        datetime.now().strftime('%d/%m/%Y %H:%M'),
    ]])
