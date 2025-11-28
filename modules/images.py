"""
Ultimate_Bak3 - Image Creation Module
Handles creating bake images and cleaning nodes.
"""

import bpy
from .. import utils


class ADVBAKE_OT_create_images(bpy.types.Operator):
    """Create target images for baking"""
    bl_idname = "advbake.create_images"
    bl_label = "Create Images"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.advbake_props
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        
        if not objects:
            self.report({'ERROR'}, "No valid mesh objects found!")
            return {'CANCELLED'}
        
        count = 0
        for obj in objects:
            # Create image
            img = utils.get_or_create_bake_image(obj, props)
            
            # Setup material nodes
            utils.ensure_image_node_for_object(obj, img)
            
            count += 1
            
        self.report({'INFO'}, f"Created images for {count} objects")
        return {'FINISHED'}


class ADVBAKE_OT_clean_unused_nodes(bpy.types.Operator):
    """Clean unused image nodes from materials"""
    bl_idname = "advbake.clean_unused_nodes"
    bl_label = "Clean Unused Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.advbake_props
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        
        removed_count = 0
        
        for obj in objects:
            if not obj.data.materials:
                continue
                
            for mat in obj.data.materials:
                if not mat or not mat.use_nodes:
                    continue
                    
                nodes = mat.node_tree.nodes
                to_remove = []
                
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        # Check if node is connected
                        is_connected = False
                        for output in node.outputs:
                            if output.is_linked:
                                is_connected = True
                                break
                        
                        if not is_connected:
                            to_remove.append(node)
                
                for node in to_remove:
                    nodes.remove(node)
                    removed_count += 1
        
        self.report({'INFO'}, f"Removed {removed_count} unused nodes")
        return {'FINISHED'}


class ADVBAKE_PT_image_creation(bpy.types.Panel):
    """Image Creation workflow step"""
    bl_label = "2. Image Creation"
    bl_idname = "ADVBAKE_PT_image_creation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.advbake_props
        
        # Settings
        layout.prop(props, "output_dir")
        layout.prop(props, "image_size")
        layout.prop(props, "image_prefix")
        
        # Use native image format settings
        row = layout.row(align=True)
        row.prop(scene.render.image_settings, "file_format", text="Format")
        row.prop(scene.render.image_settings, "color_depth", text="Depth")

        # Action buttons
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        row.operator("advbake.create_images", icon='IMAGE_DATA', text="Create Images")
        
        # Clean unused nodes button
        row = layout.row()
        row.scale_y = 1.0
        row.operator("advbake.clean_unused_nodes", icon='TRASH', text="Clean Unused Nodes")


classes = (
    ADVBAKE_OT_create_images,
    ADVBAKE_OT_clean_unused_nodes,
    ADVBAKE_PT_image_creation,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
