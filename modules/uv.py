"""
Ultimate_Bak3 - UV Preparation Module
Handles UV unwrapping and preparation.
"""

import bpy
from .. import utils


class ADVBAKE_OT_prepare_uv(bpy.types.Operator):
    """Prepare UVs for selected objects"""
    bl_idname = "advbake.prepare_uv"
    bl_label = "Prepare UV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.advbake_props
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        
        if not objects:
            self.report({'ERROR'}, "No valid mesh objects found!")
            return {'CANCELLED'}
        
        count = 0
        for obj in objects:
            # Create new UV map if requested
            if props.create_new_uv:
                uv_map = obj.data.uv_layers.new(name=props.uvmap_name)
                if uv_map:
                    obj.data.uv_layers.active = uv_map
            
            # Select object for unwrapping
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            # Unwrap
            if props.unwrap_method == 'SMART':
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project(
                    angle_limit=props.smart_angle_limit,
                    island_margin=props.smart_island_margin,
                    area_weight=props.smart_area_weight,
                    correct_aspect=props.smart_correct_aspect,
                    scale_to_bounds=props.smart_scale_to_bounds
                )
                bpy.ops.object.mode_set(mode='OBJECT')
            elif props.unwrap_method == 'UNWRAP':
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.unwrap(
                    method='ANGLE_BASED', 
                    margin=props.smart_island_margin
                )
                bpy.ops.object.mode_set(mode='OBJECT')
            
            count += 1
            
        self.report({'INFO'}, f"Prepared UVs for {count} objects")
        return {'FINISHED'}


class ADVBAKE_PT_uv_prep(bpy.types.Panel):
    """UV Preparation workflow step"""
    bl_label = "1. UV Preparation"
    bl_idname = "ADVBAKE_PT_uv_prep"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        props = context.scene.advbake_props
        
        # Settings
        layout.prop(props, "uv_mode")
        layout.prop(props, "create_new_uv")
        layout.prop(props, "uvmap_name")
        layout.prop(props, "unwrap_method")

        # Smart UV parameters (conditional)
        if props.unwrap_method in {'SMART', 'UNWRAP'}:
            box = layout.box()
            box.label(text="Unwrap Parameters:", icon='SETTINGS')
            col = box.column(align=True)
            col.prop(props, "smart_island_margin")
            
            if props.unwrap_method == 'SMART':
                col.prop(props, "smart_angle_limit")
                col.prop(props, "smart_area_weight")
                col.prop(props, "smart_correct_aspect")
                col.prop(props, "smart_scale_to_bounds")

        # Action button
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        row.operator("advbake.prepare_uv", icon='UV', text="Prepare UV")


classes = (ADVBAKE_OT_prepare_uv, ADVBAKE_PT_uv_prep)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
