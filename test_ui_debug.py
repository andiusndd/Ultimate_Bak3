"""
Debug script to test updater UI display
Run this in Blender's Python console
"""

import bpy

# Get the updater
try:
    from Ultimate_Bak3 import addon_updater_ops
    from Ultimate_Bak3 import __init__ as main_module
    
    print("\n" + "="*60)
    print("UPDATER DEBUG INFO")
    print("="*60)
    
    if addon_updater_ops and hasattr(addon_updater_ops, 'updater'):
        updater = addon_updater_ops.updater
        
        print(f"✓ Updater found")
        print(f"  - update_ready: {updater.update_ready}")
        print(f"  - update_version: {updater.update_version}")
        print(f"  - current_version: {updater.current_version}")
        print(f"  - _ignore_this_session: {getattr(updater, '_ignore_this_session', 'N/A')}")
        
        if hasattr(updater, 'json') and updater.json:
            print(f"  - json.ignore: {updater.json.get('ignore', 'N/A')}")
            print(f"  - json.last_check: {updater.json.get('last_check', 'N/A')}")
        
        # Get current version from bl_info
        current_ver = main_module.bl_info.get("version", (0, 0, 0))
        print(f"  - bl_info version: {current_ver}")
        
        print("\nUI Display Logic:")
        if updater.update_ready is None:
            print("  → Will NOT show (update_ready is None - no check performed yet)")
        elif updater.update_ready == True:
            print("  → Will show UPDATE AVAILABLE")
        elif updater.update_ready == False:
            print("  → Will show UP TO DATE")
        
    else:
        print("✗ Updater not found!")
        
    print("="*60 + "\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
