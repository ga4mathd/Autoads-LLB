import os
import requests

class MetaAssetManager:
    def __init__(self, access_token: str, ad_account_id: str):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        if not self.ad_account_id.startswith('act_'):
            self.ad_account_id = f'act_{self.ad_account_id}'
        self.base_url = f"https://graph.facebook.com/v19.0/{self.ad_account_id}"

    def upload_video(self, file_path: str, title: str = "Auto Uploaded Video") -> str:
        """Tải video lên Meta bằng kỹ thuật Chunked Upload (hỗ trợ file > 1GB)"""
        url = f"{self.base_url}/advideos"
        file_size = os.path.getsize(file_path)

        # BƯỚC 1: Khởi tạo (START)
        start_payload = {
            'upload_phase': 'start',
            'access_token': self.access_token,
            'file_size': file_size
        }
        res = requests.post(url, data=start_payload)
        res.raise_for_status()
        start_data = res.json()
        
        upload_session_id = start_data['upload_session_id']
        video_id = start_data['video_id']
        start_offset = int(start_data['start_offset'])
        end_offset = int(start_data['end_offset'])
        
        # BƯỚC 2: Truyền dữ liệu (TRANSFER)
        with open(file_path, 'rb') as f:
            while start_offset < file_size:
                chunk_size = end_offset - start_offset
                f.seek(start_offset)
                chunk_data = f.read(chunk_size)
                
                transfer_payload = {
                    'upload_phase': 'transfer',
                    'upload_session_id': upload_session_id,
                    'access_token': self.access_token,
                    'start_offset': start_offset
                }
                files = {
                    'video_file_chunk': ('chunk', chunk_data, 'application/octet-stream')
                }
                res = requests.post(url, data=transfer_payload, files=files)
                res.raise_for_status()
                transfer_data = res.json()
                
                start_offset = int(transfer_data['start_offset'])
                end_offset = int(transfer_data['end_offset'])
                print(f"   ⏳ Đã tải lên: {start_offset / (1024*1024):.1f}MB / {file_size / (1024*1024):.1f}MB")

        # BƯỚC 3: Hoàn tất (FINISH)
        finish_payload = {
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            'access_token': self.access_token,
            'title': title,
            'description': 'Uploaded via OpenClaw Bot'
        }
        res = requests.post(url, data=finish_payload)
        res.raise_for_status()
        finish_data = res.json()
        
        if finish_data.get('success'):
            return video_id
        else:
            raise Exception("Facebook báo lỗi ở bước Finish.")
