"""
Ultimate_Bak3 - ZIP Validator
Validate ZIP files for local updates.
"""

import zipfile
import os

__all__ = ['validate_zip']


def validate_zip(zip_path: str) -> tuple[bool, str]:
    """
    Validate ZIP file for addon update.
    
    Args:
        zip_path: Path to ZIP file
        
    Returns:
        (success, message): (True, "OK") if valid, (False, error_msg) otherwise
    """
    if not os.path.exists(zip_path):
        return False, "File không tồn tại"
    
    if not zipfile.is_zipfile(zip_path):
        return False, "File không phải ZIP hợp lệ"
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Test integrity
            if z.testzip() is not None:
                return False, "ZIP bị hỏng"
            
            # Check not empty
            if not z.namelist():
                return False, "ZIP rỗng"
        
        return True, "OK"
    
    except Exception as e:
        return False, f"Lỗi validation: {e}"
