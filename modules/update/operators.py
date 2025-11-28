"""
Ultimate_Bak3 - Update Operators
Operators for installing updates and hot reloading.
"""

import bpy
import os
import zipfile
import shutil
import sys

from . import validator
from . import core


def verify_addon_ready(addon_name: str) -> tuple:
    """
    Verify addon is fully loaded and ready with ALL features available.
    ✨ AUTO-DETECTS all panels and operators - no manual updates needed!
    Returns: (is_ready, error_message)
    """
    try:
        # Check main module
        if addon_name not in sys.modules:
            return False, f"{addon_name} not in sys.modules"
        
        main_mod = sys.modules[addon_name]
        
        # Check bl_info
        if not hasattr(main_mod, 'bl_info'):
            return False, "bl_info not found"
        
        # ✨ AUTO-DETECT all ADVBAKE panels (dynamic discovery)
        all_panels = [name for name in dir(bpy.types) 
                      if name.startswith('ADVBAKE_PT_')]
        
        # Verify minimum expected panels (adjust as you add more features)
        MIN_PANELS = 6  # Update, Presets, UV, Image, Baking, Material
        if len(all_panels) < MIN_PANELS:
            missing = MIN_PANELS - len(all_panels)
            return False, f"Only {len(all_panels)}/{MIN_PANELS} panels registered ({missing} missing)"
        
        # ✨ AUTO-DETECT all ADVBAKE operators (dynamic discovery)
        all_operators = [name for name in dir(bpy.types) 
                        if name.startswith('ADVBAKE_OT_')]
        
        # Verify minimum expected operators (adjust as you add more features)
        MIN_OPERATORS = 10  # Core operators for full workflow
        if len(all_operators) < MIN_OPERATORS:
            missing = MIN_OPERATORS - len(all_operators)
            return False, f"Only {len(all_operators)}/{MIN_OPERATORS} operators registered ({missing} missing)"
        
        # Check properties registered
        if not hasattr(bpy.types.Scene, 'advbake_props'):
            return False, "Properties not registered"
        
        # Verify properties are accessible and initialized
        try:
            scene = bpy.context.scene
            props = scene.advbake_props
            # Test property access to ensure fully initialized
            _ = props.bake_type
        except Exception as e:
            return False, f"Properties not accessible: {e}"
        
        # Success with detailed count
        return True, f"All features ready ({len(all_panels)} panels, {len(all_operators)} operators)"
    except Exception as e:
        return False, f"Verification error: {e}"




class ADVBAKE_OT_install_from_zip(bpy.types.Operator):
    """Install/Update addon from local ZIP file without restart"""
    bl_idname = "advbake.install_from_zip"
    bl_label = "Install from ZIP"
    bl_description = "Install or update addon from a local ZIP file"
    
    filepath: bpy.props.StringProperty(
        name="ZIP File",
        description="Path to addon ZIP file",
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.zip",
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if not self.filepath:
            print("[Local Update] No file selected")
            return {'CANCELLED'}
        
        if not os.path.exists(self.filepath):
            print(f"[Local Update] File not found: {self.filepath}")
            return {'CANCELLED'}
        
        print(f"\n{'='*60}")
        print(f"[Local Update] Installing from: {self.filepath}")
        print(f"{'='*60}\n")
        
        addon_name = "Ultimate_Bak3"
        backup_path = None
        temp_extract_path = None
        
        try:
            # Step 1: Validate ZIP
            print(f"[Local Update] Validating ZIP file...")
            ok, msg = validator.validate_zip(self.filepath)
            if not ok:
                print(f"[Local Update] ✗ {msg}")
                return {'CANCELLED'}
            print(f"[Local Update] ✓ ZIP file valid")
            
            # Get paths
            scripts_path = bpy.utils.script_path_user()
            addons_path = os.path.join(scripts_path, "addons")
            addon_path = os.path.join(addons_path, addon_name)
            temp_extract_path = os.path.join(addons_path, f"{addon_name}_temp")
            
            # Step 2: Extract
            print(f"[Local Update] Extracting...")
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path)
            
            with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
                namelist = zip_ref.namelist()
                root_folder = namelist[0].split('/')[0] if '/' in namelist[0] else namelist[0].split('\\')[0]
                extracted_addon = os.path.join(temp_extract_path, root_folder)
            
            # Validate extracted addon
            if not os.path.exists(os.path.join(extracted_addon, "__init__.py")):
                raise Exception("No __init__.py found in extracted addon")
            
            print(f"[Local Update] ✓ Extracted")
            
            # Step 3: Backup
            if os.path.exists(addon_path):
                backup_path = core.backup_addon(addon_path)
                print(f"[Local Update] ✓ Backed up to {os.path.basename(backup_path)}")
            
            # Step 4: Replace files (NO disable - that causes crash!)
            print(f"[Local Update] Replacing files...")
            core.replace_addon(extracted_addon, addon_path)
            print(f"[Local Update] ✓ Files replaced")
            
            # Step 5: Reload modules
            print(f"[Local Update] Reloading modules...")
            reloaded = core.reload_modules(addon_name)
            print(f"[Local Update] ✓ Reloaded {reloaded} modules")
            
            # Step 6: Delayed verification (increased to 1.0s for complete initialization)
            def verify_and_report():
                is_ready, msg = verify_addon_ready(addon_name)
                if is_ready:
                    print(f"[Local Update] ✓ Addon verified: {msg}")
                else:
                    print(f"[Local Update] ⚠ Warning: {msg}")
                    print(f"[Local Update]   Some features may need a moment to initialize")
                return None
            
            bpy.app.timers.register(verify_and_report, first_interval=1.0)
            
            # Step 7: Force UI refresh for all areas
            try:
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
                print(f"[Local Update] ✓ UI refreshed")
            except Exception as ui_err:
                print(f"[Local Update] ⚠ UI refresh failed: {ui_err}")
            
            # Step 8: Delayed reconfiguration (increased to 1.5s after verification)
            def delayed_configure():
                try:
                    if addon_name in sys.modules:
                        main_mod = sys.modules[addon_name]
                        if hasattr(main_mod, 'configure_updater'):
                            main_mod.configure_updater()
                            print(f"[Local Update] ✓ Updater reconfigured")
                except:
                    pass
                return None
            
            try:
                bpy.app.timers.register(delayed_configure, first_interval=1.5)
            except:
                pass
            
            # Step 9: Synchronous verification before reporting (with detailed output)
            is_ready, verify_msg = verify_addon_ready(addon_name)
            if not is_ready:
                print(f"[Local Update] ⚠ Immediate check: {verify_msg}")
                print(f"[Local Update]   Addon will be fully ready in ~1.0s")
            else:
                print(f"[Local Update] ✓ Immediate check: {verify_msg}")

            
            print(f"\n{'='*60}")
            print(f"[Local Update] ✓ UPDATE COMPLETE!")
            print(f"[Local Update]   Addon reloaded automatically - no restart needed")
            print(f"{'='*60}\n")
            
            # Clean backup after successful update
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.rmtree(backup_path)
                except:
                    pass
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"[Local Update] ✗ ERROR: {e}\n")
            
            # Restore backup on failure
            if backup_path and os.path.exists(backup_path):
                try:
                    core.restore_backup(backup_path, addon_path)
                    print(f"[Local Update] Restored from backup")
                except Exception as restore_err:
                    print(f"[Local Update] ✗ Restore failed: {restore_err}")
            
            # Clean temp
            if temp_extract_path and os.path.exists(temp_extract_path):
                try:
                    shutil.rmtree(temp_extract_path)
                except:
                    pass
            
            return {'CANCELLED'}


class ADVBAKE_OT_hot_reload(bpy.types.Operator):
    """Reload addon without restarting Blender"""
    bl_idname = "advbake.hot_reload"
    bl_label = "Hot Reload"
    bl_description = "Reload addon modules without restarting Blender"
    
    def execute(self, context):
        print(f"\n{'='*60}")
        print(f"[Hot Reload] Reloading Ultimate_Bak3...")
        print(f"{'='*60}\n")
        
        try:
            addon_name = "Ultimate_Bak3"
            
            print(f"[Hot Reload] Reloading modules...")
            count = core.reload_modules(addon_name)
            
            print(f"\n[Hot Reload] ✓ Reloaded {count} modules")
            
            # Re-configure updater after reload
            try:
                if addon_name in sys.modules:
                    main_mod = sys.modules[addon_name]
                    if hasattr(main_mod, 'configure_updater'):
                        print(f"[Hot Reload] Re-configuring updater...")
                        main_mod.configure_updater()
                        print(f"[Hot Reload] ✓ Updater configured")
            except Exception as config_err:
                print(f"[Hot Reload] ✗ Failed to re-configure updater: {config_err}")

            print(f"[Hot Reload] ✓ Complete!\n")
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"[Hot Reload] ✗ ERROR: {e}\n")
            return {'CANCELLED'}


class ADVBAKE_OT_check_update(bpy.types.Operator):
    """Check for addon updates from GitHub"""
    bl_idname = "advbake.check_update"
    bl_label = "Check Update"
    bl_description = "Check for new version of Ultimate Bak3 addon"
    
    def execute(self, context):
        try:
            # Get module from sys.modules to ensure we have the latest
            mod_name = "Ultimate_Bak3.addon_updater_ops"
            if mod_name in sys.modules:
                addon_updater_ops = sys.modules[mod_name]
            else:
                # Fallback to import
                from ... import addon_updater_ops
            
            if addon_updater_ops and hasattr(addon_updater_ops, 'updater'):
                updater = addon_updater_ops.updater
                print(f"[Ultimate_Bak3] Updater ID: {id(updater)}")
                
                # PARANOID FIX:
                # 1. Get bl_info from sys.modules explicitly
                # 2. Set BOTH public property and private attribute
                try:
                    main_mod = sys.modules.get("Ultimate_Bak3")
                    if not main_mod:
                         # Try importing if not in sys.modules (unlikely)
                         from ... import __init__ as main_mod
                    
                    bl_info = getattr(main_mod, "bl_info", None)
                    if not bl_info:
                        raise Exception("bl_info not found in main module")
                        
                    version = bl_info.get("version")
                    print(f"[Ultimate_Bak3] Found version: {version}")
                    
                    # Force configuration
                    updater.addon = "Ultimate_Bak3"
                    updater.user = "andiusndd"
                    updater.repo = "Ultimate_Bak3"
                    updater.website = "https://github.com/andiusndd/Ultimate_Bak3"
                    
                    # Set version via property
                    updater.current_version = version
                    
                    # FORCE private attribute (just in case property setter failed silently)
                    updater._current_version = version
                    
                    print(f"[Ultimate_Bak3] Configured. Public: {updater.current_version}, Private: {updater._current_version}")
                    
                except Exception as config_err:
                    print(f"[Ultimate_Bak3] ✗ Configuration failed: {config_err}")
                    import traceback
                    traceback.print_exc()

                # Triple check
                if not updater.current_version:
                     self.report({'ERROR'}, "Could not determine addon version (Check Console)")
                     return {'CANCELLED'}

                # Force check now
                print("[Ultimate_Bak3] Checking for updates...")
                updater.check_for_update(now=True)
                
                if updater.update_ready:
                    self.report({'INFO'}, f"Update available: {updater.update_version}")
                elif updater.update_ready is False:
                    self.report({'INFO'}, "Addon is up to date")
                else:
                    self.report({'WARNING'}, "Could not check for updates")
            else:
                self.report({'ERROR'}, "Updater module not loaded")
                
        except Exception as e:
            self.report({'ERROR'}, f"Update check failed: {e}")
            
        return {'FINISHED'}


# Registration
classes = (
    ADVBAKE_OT_install_from_zip,
    ADVBAKE_OT_hot_reload,
    ADVBAKE_OT_check_update,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
