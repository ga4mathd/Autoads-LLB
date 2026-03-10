"""
Scheduler — Lollibooks Ads Care Engine
Chạy care_engine mỗi 2 tiếng + đúng 12h và 0h.

Cách dùng:
  python run_scheduler.py          # Chạy nền liên tục
  python run_scheduler.py --once   # Chạy 1 lần rồi thoát
"""

import sys
import time
import schedule
from datetime import datetime
import subprocess
import os

PYTHON = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
ENGINE = os.path.join(os.path.dirname(__file__), 'core', 'care_engine.py')


def run_engine():
    print(f"\n⏰ [{datetime.now().strftime('%H:%M %d/%m')}] Triggering care engine...")
    result = subprocess.run([PYTHON, ENGINE], capture_output=False)
    if result.returncode != 0:
        print(f"❌ care_engine exited with code {result.returncode}")


if __name__ == "__main__":
    if "--once" in sys.argv:
        run_engine()
        sys.exit(0)

    print("🚀 Scheduler khởi động. Chạy care engine mỗi 2 tiếng, 12:00, và 00:00")

    # Scan mỗi 2 tiếng
    schedule.every(2).hours.do(run_engine)
    # Đúng 12h và 0h
    schedule.every().day.at("12:00").do(run_engine)
    schedule.every().day.at("00:00").do(run_engine)

    # Chạy ngay lúc khởi động
    run_engine()

    while True:
        schedule.run_pending()
        time.sleep(60)
