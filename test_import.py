"""
Test script to debug addon import issues
Run this from Blender's Python console
"""

import sys
import traceback

print("\n" + "="*80)
print("ADDON IMPORT TEST")
print("="*80)

# Test 1: Import addon_updater_ops
print("\n[1] Testing addon_updater_ops import...")
try:
    from . import addon_updater_ops
    print("✓ addon_updater_ops imported successfully")
    if hasattr(addon_updater_ops, 'updater'):
        print(f"  - updater.addon: {addon_updater_ops.updater.addon}")
        print(f"  - updater.error: {addon_updater_ops.updater.error}")
        print(f"  - updater.error_msg: {addon_updater_ops.updater.error_msg}")
except Exception as e:
    print(f"✗ Failed to import addon_updater_ops: {e}")
    traceback.print_exc()

# Test 2: Import all modules
print("\n[2] Testing all module imports...")
try:
    from . import properties
    from . import operators
    from . import ui
    from . import utils
    print("✓ All core modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import modules: {e}")
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
