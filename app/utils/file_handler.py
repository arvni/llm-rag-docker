import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

class FileHandler:
    """File management utilities"""
    
    def __init__(self, upload_path: str):
        self.upload_path = Path(upload_path)
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, uploaded_file, subdir: str = "") -> str:
        """Save uploaded file to disk"""
        if subdir:
            save_path = self.upload_path / subdir
            save_path.mkdir(parents=True, exist_ok=True)
        else:
            save_path = self.upload_path
        
        file_path = save_path / uploaded_file.name
        
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            logger.info(f"File saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving file {uploaded_file.name}: {e}")
            raise
    
    def get_uploaded_files(self) -> List[Dict]:
        """Get list of uploaded files"""
        files = []
        
        for file_path in self.upload_path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        return files
    
    def delete_file(self, filename: str) -> bool:
        """Delete uploaded file"""
        try:
            file_path = self.upload_path / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up files older than specified days"""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for file_path in self.upload_path.rglob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path.name}")
                except Exception as e:
                    logger.error(f"Error cleaning up {file_path.name}: {e}")