import os
from storage_provider.google_drive import GoogleDriveProvider

# Path to the credentials file
creds_path = os.path.join(os.path.dirname(__file__), '.credentials', 'google_service_account.json')
folder_id = '1Twnw7GZeA7K7ufspJX1TgpKQsp7ZeEbN'

try:
    print(f"🔄 Đang kết nối Google Drive API...")
    drive = GoogleDriveProvider(creds_path)
    
    print(f"📂 Đang đọc thư mục: {folder_id}\n")
    files = drive.list_files(folder_id)
    
    if not files:
        print("✅ Kết nối thành công, nhưng thư mục này đang TRỐNG.")
        print("💡 Hãy thử upload 1 file ảnh hoặc text bất kỳ vào thư mục đó, rồi tôi quét lại nhé.")
    else:
        print(f"✅ Kết nối thành công! Tìm thấy {len(files)} file(s):")
        for f in files:
            print(f"  - Tên file: {f['name']} | Loại: {f['mimeType']} | ID: {f['id']}")

except Exception as e:
    print(f"❌ Lỗi kết nối: {e}")
