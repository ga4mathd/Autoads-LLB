from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def list_files(self, folder_id: str) -> list:
        """Trả về danh sách các file trong thư mục"""
        pass

    @abstractmethod
    def download_file(self, file_id: str, dest_path: str) -> str:
        """Tải file về máy cục bộ và trả về đường dẫn file"""
        pass
