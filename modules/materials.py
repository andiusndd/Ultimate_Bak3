"""
Ultimate_Bak3 - Material Application Module
Handles applying baked textures to materials.
"""

import bpy
import os
from .. import utils
from .. import auto_utils


class ADVBAKE_OT_apply_baked_material(bpy.types.Operator):
    """Create and apply a new material using the baked texture"""
    bl_idname = "advbake.apply_baked_material"
    bl_label = "Apply Baked Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def validate_object(self, obj):
        """Validate object is ready for material application. Returns (is_valid, error_message)"""
        if not obj.data:
            return False, f"{obj.name}: No mesh data"
        
        if not obj.data.uv_layers:
            return False, f"{obj.name}: No UV layers"
        
        return True, "OK"
    
    def validate_uv_map(self, obj, uv_name: str):
        """Validate UV map exists and is usable. Returns (is_valid, message)"""
        if not obj.data.uv_layers:
            return False, "No UV layers found"
        
        uv_layer = obj.data.uv_layers.get(uv_name)
        if not uv_layer:
            # Try to find similar name (partial match)
            similar = [uv.name for uv in obj.data.uv_layers if uv_name in uv.name]
            if similar:
                return True, f"Using similar UV: {similar[0]}"
            return False, f"UV map '{uv_name}' not found"
        
        return True, "OK"
    
    def find_latest_bake_image(self, obj, props):
        """
        Find the most recently created baked image for this object.
        Searches with multiple patterns and fallbacks.
        """
        # Pattern 1: {prefix}{obj_name}_*
        pattern = f"{props.image_prefix}{obj.name}_"
        candidates = [img for img in bpy.data.images if img.name.startswith(pattern)]
        
        if not candidates and props.image_prefix:
            # Pattern 2: Try without prefix
            pattern_no_prefix = f"{obj.name}_"
            candidates = [img for img in bpy.data.images if img.name.startswith(pattern_no_prefix)]
        
        if not candidates:
            # Pattern 3: Last resort - use utils function (fallback)
            return utils.get_or_create_bake_image(obj, props)
        
        # Return most recent (sort by name, assuming timestamp or alphabetical order)
        candidates.sort(key=lambda x: x.name, reverse=True)
        return candidates[0]
    
    def manage_uv_maps(self, obj, target_uv_name: str):
        """
        Set target UV as active, others as inactive. 
        Returns True if target UV was found and activated.
        """
        if not obj.data.uv_layers:
            return False
        
        target_found = False
        for uv in obj.data.uv_layers:
            # Exact match or partial match
            if uv.name == target_uv_name or target_uv_name in uv.name:
                uv.active = True
                uv.active_render = True
                obj.data.uv_layers.active = uv
                target_found = True
                print(f"[Material] ✓ Activated UV: {uv.name} for {obj.name}")
            else:
                uv.active = False
                uv.active_render = False
        
        return target_found
    
    def verify_material_applied(self, obj, expected_mat_name: str):
        """
        Verify material was applied correctly.
        Returns (is_valid, message)
        """
        if not obj.data.materials:
            return False, "No materials on object"
        
        if len(obj.data.materials) != 1:
            return False, f"Expected 1 material, found {len(obj.data.materials)}"
        
        mat = obj.data.materials[0]
        if not mat:
            return False, "Material slot is empty"
        
        if not mat.use_nodes:
            return False, "Material doesn't use nodes"
        
        # Check for image texture node
        has_image = any(node.type == 'TEX_IMAGE' for node in mat.node_tree.nodes)
        if not has_image:
            return False, "No image texture node found"
        
        return True, "Material applied correctly"


    def execute(self, context):
        props = context.scene.advbake_props
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        
        if not objects:
            self.report({'ERROR'}, "No objects found")
            return {'CANCELLED'}
        
        count = 0
        errors = []
        warnings = []
        
        for obj in objects:
            # Create state snapshot for error recovery
            snapshot = auto_utils.AutoBackup.create_state_snapshot(obj)
            
            try:
                # Step 1: Validate object
                ok, msg = self.validate_object(obj)
                if not ok:
                    errors.append(msg)
                    continue
                
                # Step 2: Validate UV map exists
                ok, msg = self.validate_uv_map(obj, props.uvmap_name)
                if not ok:
                    warnings.append(f"{obj.name}: {msg}")
                    # Continue anyway, might work with default UV
                
                # Step 3: Find the newly created image by suffix/pattern
                img = self.find_latest_bake_image(obj, props)
                if not img:
                    warnings.append(f"No baked image found for {obj.name}")
                    continue
                
                print(f"[Material] Using image: {img.name} for {obj.name}")
                
                # Step 4: Clear ALL old materials FIRST
                old_mat_count = len(obj.data.materials)
                obj.data.materials.clear()
                if old_mat_count > 0:
                    print(f"[Material] Cleared {old_mat_count} old material(s) from {obj.name}")
                
                # Step 5: Create material with texture node
                mat_name = f"{obj.name}_Baked"
                mat = bpy.data.materials.new(name=mat_name)
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                
                # Clear default nodes
                nodes.clear()
                
                # Create Principled BSDF
                bsdf = nodes.new('ShaderNodeBsdfPrincipled')
                bsdf.location = (0, 0)
                
                # Create Output
                output = nodes.new('ShaderNodeOutputMaterial')
                output.location = (300, 0)
                links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
                
                # Create Image Texture
                tex_image = nodes.new('ShaderNodeTexImage')
                tex_image.image = img
                tex_image.location = (-300, 0)
                
                # Link based on bake type
                if props.bake_type == 'COMBINED' or props.bake_type == 'DIFFUSE':
                    links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
                elif props.bake_type == 'ROUGHNESS':
                    links.new(tex_image.outputs['Color'], bsdf.inputs['Roughness'])
                    tex_image.image.colorspace_settings.name = 'Non-Color'
                elif props.bake_type == 'NORMAL':
                    normal_map = nodes.new('ShaderNodeNormalMap')
                    normal_map.location = (-150, -150)
                    links.new(tex_image.outputs['Color'], normal_map.inputs['Color'])
                    links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
                    tex_image.image.colorspace_settings.name = 'Non-Color'
                elif props.bake_type == 'EMIT':
                    links.new(tex_image.outputs['Color'], bsdf.inputs['Emission'])
                
                # Step 6: Assign new material
                obj.data.materials.append(mat)
                
                # Step 7: Manage UV maps - activate the bake UV, deactivate others
                uv_ok = self.manage_uv_maps(obj, props.uvmap_name)
                if not uv_ok:
                    warnings.append(f"{obj.name}: Could not activate UV '{props.uvmap_name}'")
                
                # Step 8: Verify material was applied correctly
                ok, msg = self.verify_material_applied(obj, mat.name)
                if not ok:
                    raise Exception(f"Verification failed: {msg}")
                
                count += 1
                
            except Exception as e:
                # ROLLBACK on error
                print(f"[Material] ⚠ Error processing {obj.name}: {e}")
                print(f"[Material] ↺ Rolling back changes for {obj.name}...")
                
                if auto_utils.AutoBackup.restore_state_snapshot(obj, snapshot):
                    print(f"[Material] ✓ Rollback successful")
                    errors.append(f"{obj.name}: {e} (Changes reverted)")
                else:
                    print(f"[Material] ✗ Rollback failed!")
                    errors.append(f"{obj.name}: {e} (Rollback FAILED)")
                continue
        
        # Report results with detailed feedback
        if errors:
            self.report({'ERROR'}, f"Errors: {'; '.join(errors)}")
        if warnings:
            self.report({'WARNING'}, f"Warnings: {'; '.join(warnings)}")
        if count > 0:
            self.report({'INFO'}, f"Applied baked material to {count} object(s)")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No materials were applied")
            return {'CANCELLED'}


class ADVBAKE_OT_apply_pbr_material(bpy.types.Operator):
    """Create and apply a PBR material using all baked maps"""
    bl_idname = "advbake.apply_pbr_material"
    bl_label = "Apply PBR Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.advbake_props
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        
        if not objects:
            self.report({'ERROR'}, "No objects found")
            return {'CANCELLED'}
            
        count = 0
        for obj in objects:
            # Create new material
            mat_name = f"{obj.name}_PBR_Baked"
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()
            
            # Nodes
            output = nodes.new('ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Map types to BSDF inputs
            # (Suffix, BSDF Input, IsData)
            maps = [
                ('BaseColor', 'Base Color', False),
                ('Roughness', 'Roughness', True),
                ('Metallic', 'Metallic', True),
                ('Emission', 'Emission', False),
                ('AO', None, True), # AO usually mixed with color or separate
                ('Normal', 'Normal', True)
            ]
            
            y_offset = 300
            
            for suffix, input_name, is_data in maps:
                # Find image
                img_name = f"{props.image_prefix}{obj.name}_{suffix}"
                img = bpy.data.images.get(img_name)
                
                if img:
                    tex = nodes.new('ShaderNodeTexImage')
                    tex.image = img
                    tex.location = (-400, y_offset)
                    if is_data:
                        tex.image.colorspace_settings.name = 'Non-Color'
                    
                    if input_name == 'Normal':
                        normal_map = nodes.new('ShaderNodeNormalMap')
                        normal_map.location = (-200, y_offset)
                        links.new(tex.outputs['Color'], normal_map.inputs['Color'])
                        links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
                    elif input_name:
                        links.new(tex.outputs['Color'], bsdf.inputs[input_name])
                    
                    y_offset -= 300
            
            # Assign material
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            
            count += 1
            
        self.report({'INFO'}, f"Applied PBR material to {count} objects")
        return {'FINISHED'}


class ADVBAKE_PT_material(bpy.types.Panel):
    """Material Application workflow step"""
    bl_label = "4. Material Application"
    bl_idname = "ADVBAKE_PT_material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        
        # Standard apply material
        row = layout.row()
        row.scale_y = 1.3
        row.operator("advbake.apply_baked_material", icon='MATERIAL', text="Apply Material")
        
        # PBR apply material
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        row.operator("advbake.apply_pbr_material", icon='NODE_MATERIAL', text="Apply PBR Material")


classes = (
    ADVBAKE_OT_apply_baked_material,
    ADVBAKE_OT_apply_pbr_material,
    ADVBAKE_PT_material,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
