"""
Ultimate_Bak3 - Update Core
Core update operations: backup, replace, restore, reload.
"""

import os
import shutil
import importlib
import sys
import time
from pathlib import Path

__all__ = ['backup_addon', 'replace_addon', 'restore_backup', 'reload_modules']


def backup_addon(addon_dir: str) -> str:
    """
    Create timestamped backup of addon directory.
    
    Args:
        addon_dir: Path to addon directory
        
    Returns:
        Path to backup directory
    """
    src = Path(addon_dir)
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = src.parent / f"{src.name}_backup_{ts}"
    
    # Remove old backup if exists
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    # Create backup
    shutil.copytree(src, backup_dir)
    
    return str(backup_dir)


def replace_addon(src_dir: str, dst_dir: str) -> None:
    """
    Replace addon directory with new version.
    
    Args:
        src_dir: Source directory (extracted addon)
        dst_dir: Destination directory (current addon location)
    """
    # Remove old addon
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    
    # Move new addon to location
    shutil.move(src_dir, dst_dir)


def restore_backup(backup_dir: str, dst_dir: str) -> None:
    """
    Restore addon from backup.
    
    Args:
        backup_dir: Path to backup directory
        dst_dir: Destination directory (current addon location)
    """
    # Remove failed update
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    
    # Restore from backup
    shutil.copytree(backup_dir, dst_dir)


def reload_modules(addon_name: str) -> int:
    """
    Reload all addon modules without restarting Blender.
    
    This preserves the current logic which scans sys.modules
    instead of using dir() - more robust for dynamic imports.
    
    Args:
        addon_name: Name of addon package (e.g., "Ultimate_Bak3")
        
    Returns:
        Number of modules successfully reloaded
    """
    # Find all modules that belong to this addon
    modules_to_reload = [
        m for m in list(sys.modules.keys()) 
        if m.startswith(addon_name)
    ]
    modules_to_reload.sort()
    
    reloaded = 0
    for module_name in modules_to_reload:
        try:
            importlib.reload(sys.modules[module_name])
            reloaded += 1
        except:
            # If reload fails, remove from sys.modules
            # Next import will load fresh
            try:
                del sys.modules[module_name]
            except:
                pass
    
    return reloaded
