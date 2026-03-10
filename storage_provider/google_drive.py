import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from .base import StorageProvider

class GoogleDriveProvider(StorageProvider):
    def __init__(self, credentials_path: str):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.scopes)
        self.service = build('drive', 'v3', credentials=self.creds)

    def list_files(self, folder_id: str) -> list:
        """Lấy danh sách file trong 1 thư mục"""
        query = f"'{folder_id}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])

    def download_file(self, file_id: str, dest_path: str) -> str:
        """Tải file từ Drive về thư mục hiện tại"""
        request = self.service.files().get_media(fileId=file_id)
        
        # Đảm bảo thư mục đích tồn tại
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with io.FileIO(dest_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # print(f"Download {int(status.progress() * 100)}%.")
                
        return dest_path
