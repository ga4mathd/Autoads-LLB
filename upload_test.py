import os
import requests
from dotenv import load_dotenv
from storage_provider.google_drive import GoogleDriveProvider
from meta_provider.asset_manager import MetaAssetManager

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

creds_path = os.path.join(os.path.dirname(__file__), '.credentials', 'google_service_account.json')
folder_id = '1Twnw7GZeA7K7ufspJX1TgpKQsp7ZeEbN'

access_token = os.getenv("META_ACCESS_TOKEN")
ad_account_id = os.getenv("META_AD_ACCOUNT_ID")

print("1. Đang quét thư mục Google Drive...")
try:
    drive = GoogleDriveProvider(creds_path)
    files = drive.list_files(folder_id)

    if not files:
        print("❌ Thư mục vẫn trống. Bạn chắc đã upload đúng thư mục và share quyền chưa?")
        exit(1)

    target_file = files[0]
    print(f"✅ Tìm thấy file trên Drive: {target_file['name']} (ID: {target_file['id']})")

    temp_path = os.path.join(os.path.dirname(__file__), 'temp', target_file['name'])
    
    print(f"2. Kéo file từ Drive xuống trạm trung chuyển (Bot)...")
    drive.download_file(target_file['id'], temp_path)
    
    file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
    print(f"✅ Đã tải thành công: {temp_path} ({file_size_mb:.2f} MB)")

    print(f"3. Đang đẩy file lên kho tài sản (Asset Library) của Meta Ads...")
    meta = MetaAssetManager(access_token, ad_account_id)
    
    video_id = meta.upload_video(temp_path, title=target_file['name'])
    
    print(f"🎉 THÀNH CÔNG! Video đã chính thức nằm trên tài khoản Meta.")
    print(f"👉 META VIDEO ID (Mã này dùng để lên camp): {video_id}")
    
    # Dọn dẹp trạm trung chuyển
    os.remove(temp_path)
    print("🧹 Đã xóa file trên trạm, giải phóng dung lượng.")

except requests.exceptions.RequestException as e:
    print(f"❌ Lỗi khi gửi API Meta: {e}")
    if hasattr(e, 'response') and e.response is not None:
         print(e.response.json())
except Exception as e:
    print(f"❌ Có lỗi xảy ra: {e}")
