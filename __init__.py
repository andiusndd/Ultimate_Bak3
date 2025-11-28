bl_info = {
    "name": "Ultimate Bak3",
    "author": "andiusndd",
    "version": (3, 2, 7),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Ultimate Bak3",
    "description": "Advanced texture baking tool with presets and automation",
    "warning": "",
    "wiki_url": "https://github.com/andiusndd/Ultimate_Bak3",
    "tracker_url": "https://github.com/andiusndd/Ultimate_Bak3/issues",
    "category": "Render",
}

import bpy
import importlib
import sys
import os

# --- Auto-Discovery Helper ---
def get_addon_modules():
    """✨ Auto-discover all feature modules in the modules directory"""
    from . import modules
    import inspect
    
    discovered = []
    for name in dir(modules):
        # Skip private/special attributes
        if name.startswith('_'):
            continue
        
        attr = getattr(modules, name)
        # Check if it's a module with register/unregister functions
        if inspect.ismodule(attr) and hasattr(attr, 'register') and hasattr(attr, 'unregister'):
            discovered.append((name, attr))
    
    return discovered


# --- Module Imports with Auto-Discovery ---
if "properties" in locals():
    # Reloading mode
    importlib.reload(properties)
    importlib.reload(utils)
    
    # ✨ Auto-reload all feature modules
    from . import modules
    for module_name, module_obj in get_addon_modules():
        try:
            importlib.reload(module_obj)
            print(f"  ↻ Reloaded: {module_name}")
        except Exception as e:
            print(f"  ✗ Failed to reload {module_name}: {e}")
    
    # Reload updater modules
    if "addon_updater" in locals():
        importlib.reload(addon_updater)
    if "addon_updater_ops" in locals():
        importlib.reload(addon_updater_ops)
else:
    # Initial import
    from . import properties
    from . import utils
    
    # ✨ Auto-import all feature modules (no manual listing needed!)
    from . import modules
    # Modules are auto-discovered via get_addon_modules() during registration
    
    # Import updater modules
    try:
        from . import addon_updater
        from . import addon_updater_ops
    except Exception as e:
        print(f"Warning: Could not import addon_updater modules: {e}")
        addon_updater_ops = None


# --- Updater Configuration ---
def configure_updater():
    """Configure the addon updater"""
    if not addon_updater_ops:
        return

    updater = addon_updater_ops.updater
    updater.addon = "Ultimate_Bak3"
    updater.user = "andiusndd"
    updater.repo = "Ultimate_Bak3"
    updater.current_version = bl_info["version"]
    updater.website = "https://github.com/andiusndd/Ultimate_Bak3"
    updater.fake_install = False 
    updater.show_popups = True
    updater.version_min_update = (0, 0, 0)
    
    # Configuration
    updater.use_releases = True
    updater.backup_current = True 
    updater.overwrite_patterns = ["*.py", "presets/*.json"]
    updater.remove_pre_update_patterns = ["*.pyc", "__pycache__"]
    
    # Auto-check settings
    updater.auto_reload_post_update = False 
    updater.interval_months = 0
    updater.interval_days = 7
    updater.interval_hours = 0
    updater.interval_minutes = 0


# --- Registration ---

def register():
    print(f"\n{'='*40}")
    print(f"Ultimate Bak3 v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]} Loading...")
    print(f"{'='*40}")

    # 1. Register Properties (Global Settings)
    properties.register()
    
    # 2. ✨ Auto-register ALL feature modules (dynamic discovery)
    addon_modules = get_addon_modules()
    print(f"  → Discovered {len(addon_modules)} feature modules")
    
    for module_name, module_obj in addon_modules:
        try:
            module_obj.register()
            print(f"  ✓ Registered: {module_name}")
        except Exception as e:
            print(f"  ✗ Failed to register {module_name}: {e}")
    
    # 3. Register Updater
    if addon_updater_ops:
        addon_updater_ops.register(bl_info)
        
        # Configure updater
        configure_updater()
        
        # Add persistent handlers
        if not hasattr(bpy.app.handlers, "load_post"):
            # Fallback for older Blender versions
            pass
        else:
            # Ensure handler isn't added twice
            has_handler = False
            for handler in bpy.app.handlers.load_post:
                if getattr(handler, "__name__", "") == "updater_run_install_popup_handler":
                    has_handler = True
                    break
            
            if not has_handler:
                bpy.app.handlers.load_post.append(addon_updater_ops.updater_run_install_popup_handler)
    
    # 4. ✨ Auto-Features Registration
    try:
        from . import auto_utils
        # Register console shortcuts
        auto_utils.register_console_shortcuts()
        # Generate metadata (optional, good for dev)
        # auto_utils.save_metadata_file(bl_info)
    except Exception as e:
        print(f"Warning: Failed to register auto-features: {e}")
    
    print("✓ Ultimate Bak3 Registered Successfully\n")


def unregister():
    print(f"\n{'='*40}")
    print(f"Unregistering Ultimate Bak3...")
    print(f"{'='*40}")

    # 1. Unregister Updater
    if addon_updater_ops:
        addon_updater_ops.unregister()
        
        # Remove handlers
        if hasattr(bpy.app.handlers, "load_post"):
            handlers_to_remove = []
            for handler in bpy.app.handlers.load_post:
                if getattr(handler, "__name__", "") == "updater_run_install_popup_handler":
                    handlers_to_remove.append(handler)
            
            for handler in handlers_to_remove:
                bpy.app.handlers.load_post.remove(handler)

    # 2. ✨ Auto-unregister ALL feature modules (reverse order for safety)
    addon_modules = get_addon_modules()
    for module_name, module_obj in reversed(addon_modules):
        try:
            module_obj.unregister()
            print(f"  ✓ Unregistered: {module_name}")
        except Exception as e:
            print(f"  ✗ Failed to unregister {module_name}: {e}")
    
    # 3. Unregister Properties
    properties.unregister()
    
    print("✓ Ultimate Bak3 Unregistered\n")


if __name__ == "__main__":
    register()
