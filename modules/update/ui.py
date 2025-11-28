"""
Ultimate_Bak3 - Update UI
Panel for addon updates.
"""

import bpy
import sys



class ADVBAKE_PT_update(bpy.types.Panel):
    """Update panel for addon updates"""
    bl_label = "Updates"
    bl_idname = "ADVBAKE_PT_update"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        # Show version in header
        try:
            main_mod = sys.modules.get("Ultimate_Bak3")
            if main_mod and hasattr(main_mod, "bl_info"):
                ver = main_mod.bl_info.get("version", (0, 0, 0))
                layout.label(text=f"v{ver[0]}.{ver[1]}.{ver[2]}", icon='URL')
            else:
                layout.label(text="", icon='URL')
        except:
            layout.label(text="", icon='URL')

    def draw(self, context):
        layout = self.layout
        
        # Import updater ops here to avoid circular imports
        try:
            from ... import addon_updater_ops
            from ... import __init__ as main_module
        except ImportError:
            addon_updater_ops = None
            main_module = None

        # --- Local Update Section ---
        box = layout.box()
        box.label(text="Local Update", icon='FILE_FOLDER')
        
        row = box.row()
        row.operator("advbake.install_from_zip", icon='IMPORT')
        
        row = box.row()
        row.operator("advbake.hot_reload", icon='FILE_REFRESH')
        
        # --- GitHub Update Section ---
        if addon_updater_ops:
            updater = addon_updater_ops.updater
            
            box = layout.box()
            row = box.row()
            row.label(text="GitHub Update", icon='WORLD')
            
            # Check button
            row = box.row()
            row.operator("advbake.check_update", icon='FILE_REFRESH', text="Check for Updates")
            
            # Only show status if check has been performed (update_ready is not None)
            if updater.update_ready is not None:
                box.separator()
                
                # Get current version
                main_mod = sys.modules.get("Ultimate_Bak3")
                if main_mod and hasattr(main_mod, "bl_info"):
                    current_ver = main_mod.bl_info.get("version", (0, 0, 0))
                    current_str = f"v{current_ver[0]}.{current_ver[1]}.{current_ver[2]}"
                else:
                    current_str = "v?.?.?"
                
                # Always show current version after check
                row = box.row()
                row.label(text=f"Current: {current_str}", icon='BLENDER')
                
                # Status display
                if updater.update_ready:
                    # Update Available
                    col = box.column(align=True)
                    col.alert = True  # Red background
                    col.label(text="⬆ Newer version available", icon='ERROR')
                    col.label(text=f"Latest: {updater.update_version}")
                    
                    # Update Now button
                    row = box.row()
                    row.scale_y = 1.2
                    op = row.operator(addon_updater_ops.AddonUpdaterUpdateNow.bl_idname, text="Update Now", icon='URL')
                    op.clean_install = True  # Ensure clean install
                    
                    # Ignore button - only show after check
                    row = box.row()
                    row.operator(addon_updater_ops.AddonUpdaterIgnore.bl_idname, text="Ignore Update", icon='CANCEL')
                    
                else:
                    # Up to date
                    row = box.row()
                    row.label(text="✓ Up to date", icon='CHECKMARK')
            
            # Only show "Update ignored" if user has explicitly ignored AND update is available
            elif updater.manual_only and updater.update_ready:
                row = box.row()
                row.label(text="(Update ignored)", icon='CANCEL')


# Registration
def register():
    bpy.utils.register_class(ADVBAKE_PT_update)


def unregister():
    bpy.utils.unregister_class(ADVBAKE_PT_update)
