import schedule
import time
from datetime import datetime
from google_sheet import get_videos_to_analyze, write_analysis
from facebook_api import pull_ad_metrics
from analyzer import classify_and_analyze
from lark_notify import send_report

def daily_analysis():
    print(f"[{datetime.now()}] Bắt đầu phân tích content...")
    videos = get_videos_to_analyze()
    if not videos:
        print("Không có video nào cần phân tích hôm nay.")
        return
        
    print(f"Tìm thấy {len(videos)} video cần phân tích.")
    results_win, results_fail = [], []
    
    for video in videos:
        metrics = pull_ad_metrics(video['post_id'], video['start_date'])
        result = classify_and_analyze(video, metrics)
        write_analysis(video['row_number'], metrics, result)
        
        if result['classification'] == 'WIN':
            results_win.append(result)
        else:
            results_fail.append(result)
            
    send_report(results_win, results_fail)
    print(f"[{datetime.now()}] Hoàn tất. WIN: {len(results_win)}, FAIL: {len(results_fail)}")

if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        daily_analysis()
    else:
        schedule.every().day.at("08:00").do(daily_analysis)
        while True:
            schedule.run_pending()
            time.sleep(60)
