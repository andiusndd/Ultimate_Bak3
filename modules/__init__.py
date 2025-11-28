"""
Ultimate_Bak3 - Modules Package
Feature-based modular structure for better maintainability.
"""

import os
import importlib

# ✨ Auto-generate __all__ from .py files AND packages in this directory
_module_dir = os.path.dirname(__file__)
_module_items = []

# Scan for .py files (modules)
for item in os.listdir(_module_dir):
    if item.endswith('.py') and item != '__init__.py' and not item.startswith('_'):
        _module_items.append(item[:-3])  # Remove .py extension
    # Scan for packages (directories with __init__.py)
    elif os.path.isdir(os.path.join(_module_dir, item)) and not item.startswith('_'):
        init_file = os.path.join(_module_dir, item, '__init__.py')
        if os.path.exists(init_file):
            _module_items.append(item)

# Sort for deterministic order
__all__ = sorted(_module_items)

# ✨ Import modules/packages so they are available in package namespace
# This is CRITICAL for get_addon_modules() in root __init__.py to work!
for module_name in _module_items:
    try:
        importlib.import_module(f".{module_name}", package=__name__)
    except Exception as e:
        print(f"[Ultimate Bak3] Error importing module '{module_name}': {e}")

# Debug: print discovered modules (comment out in production)
# print(f"[Modules] Auto-discovered & Imported: {__all__}")
