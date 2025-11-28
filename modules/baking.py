"""
Ultimate_Bak3 - Baking Module
Handles baking operations (Standard & PBR).
"""

import bpy
import os
from .. import utils


class ADVBAKE_OT_bake_only(bpy.types.Operator):
    """Perform bake operation"""
    bl_idname = "advbake.bake_only"
    bl_label = "Bake Only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.advbake_props
        
        # Save render settings
        original_settings = utils.save_render_settings(scene)
        
        try:
            # Setup bake settings
            utils.setup_bake_settings(scene, props)
            
            # Bake
            bpy.ops.object.bake(type=props.bake_type)
            
            self.report({'INFO'}, "Bake complete")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Bake failed: {e}")
            return {'CANCELLED'}
            
        finally:
            # Restore settings
            utils.restore_render_settings(scene, original_settings)


class ADVBAKE_OT_auto_save_images(bpy.types.Operator):
    """Save all baked images to output folder"""
    bl_idname = "advbake.auto_save_images"
    bl_label = "Auto Save All Images"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.advbake_props
        
        # Ensure output directory exists
        output_dir = bpy.path.abspath(props.output_dir)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.report({'ERROR'}, f"Could not create output directory: {e}")
                return {'CANCELLED'}
        
        saved_count = 0
        skipped_count = 0
        
        print(f"\n{'='*60}")
        print(f"[Auto Save] Saving images to: {output_dir}")
        
        # Iterate through all images in blend file
        for img in bpy.data.images:
            # Skip internal/viewer images
            if img.name in {'Render Result', 'Viewer Node'}:
                continue
                
            # Skip images with no data (generated but not baked/painted)
            if not img.has_data:
                skipped_count += 1
                continue
            
            # FILTER: Only save images matching criteria
            should_save = False
            
            # Check 1: If image has automation tag (created during automation)
            if img.get("_automation_new", False):
                should_save = True
                print(f"[Auto Save] {img.name} - marked by automation")
            
            # Check 2: If image name starts with prefix (if prefix is set)
            elif props.image_prefix and img.name.startswith(props.image_prefix):
                should_save = True
                print(f"[Auto Save] {img.name} - matches prefix '{props.image_prefix}'")
            
            # Check 3: Fallback - if no prefix and no tag, skip old images
            elif not props.image_prefix:
                # No prefix set and no automation tag = likely old image, skip
                print(f"[Auto Save] {img.name} - skipped (no tag, no prefix match)")
                skipped_count += 1
                continue
            else:
                # Has prefix but doesn't match
                print(f"[Auto Save] {img.name} - skipped (doesn't match prefix)")
                skipped_count += 1
                continue
            
            if not should_save:
                skipped_count += 1
                continue
                
            # Check if this image looks like a bake result
            # (Optional: could filter by prefix if strict mode enabled)
            
            try:
                # Determine file extension based on settings
                file_ext = '.png'
                if props.image_format == 'JPEG': file_ext = '.jpg'
                elif props.image_format == 'TARGA': file_ext = '.tga'
                elif props.image_format == 'OPEN_EXR': file_ext = '.exr'
                elif props.image_format == 'BMP': file_ext = '.bmp'
                elif props.image_format == 'TIFF': file_ext = '.tif'
                
                # Construct path
                filename = f"{img.name}{file_ext}"
                filepath = os.path.join(output_dir, filename)
                
                # Update image settings
                img.filepath_raw = filepath
                img.file_format = props.image_format
                
                # Save
                img.save()
                print(f"[Auto Save] ✓ Saved: {filename}")
                saved_count += 1
                
                # Clear automation tag after successful save
                if "_automation_new" in img.keys():
                    del img["_automation_new"]
                
            except Exception as e:
                print(f"[Auto Save] ✗ Failed to save {img.name}: {e}")
        
        print(f"{'='*60}\n")
        
        if saved_count > 0:
            self.report({'INFO'}, f"Saved {saved_count} images to {props.output_dir}")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, f"No new images to save (skipped {skipped_count})")
            return {'FINISHED'}  # Changed to FINISHED (not error if no new images)


class ADVBAKE_OT_pbr_bake(bpy.types.Operator):
    """Automatically bake all PBR maps (BaseColor, Roughness, Normal, AO, Metallic, Emission)"""
    bl_idname = "advbake.pbr_bake"
    bl_label = "PBR Auto Bake"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.advbake_props
        
        # PBR map definitions: (Blender bake type, suffix for image name)
        pbr_maps = [
            ('DIFFUSE', 'BaseColor'),
            ('ROUGHNESS', 'Roughness'),
            ('NORMAL', 'Normal'),
            ('AO', 'AO'),
            ('GLOSSY', 'Metallic'),
            ('EMIT', 'Emission'),
        ]
        
        # Get target objects
        objects = utils.get_objects_by_scope(context, props, require_mesh=True)
        if not objects:
            self.report({'ERROR'}, "No valid mesh objects found in Bake Scope!")
            return {'CANCELLED'}
        
        total_maps = len(pbr_maps) * len(objects)
        current_map = 0
        
        for obj in objects:
            # Create all images first
            images = {}
            for bake_type, suffix in pbr_maps:
                images[suffix] = utils.get_or_create_bake_image(obj, props, suffix)
            
            # Bake each map
            for bake_type, suffix in pbr_maps:
                current_map += 1
                print(f"[PBR Bake] {current_map}/{total_maps}: {obj.name} - {suffix}")
                
                # Setup image node for this map
                utils.ensure_image_node_for_object(obj, images[suffix])
                
                # Select object and set active
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Bake
                try:
                    bpy.ops.object.bake(type=bake_type)
                except Exception as e:
                    print(f"[PBR Bake] Warning: Failed to bake {suffix} for {obj.name}: {e}")
                    continue
                
                # Save image
                if props.output_dir:
                    output_path = bpy.path.abspath(props.output_dir)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    
                    file_ext = '.png' if props.image_format == 'PNG' else ('.tga' if props.image_format == 'TARGA' else '.exr')
                    file_path = os.path.join(output_path, images[suffix].name + file_ext)
                    images[suffix].filepath_raw = file_path
                    images[suffix].file_format = props.image_format
                    images[suffix].save()
        
        self.report({'INFO'}, f"PBR bake complete: {len(objects)} object(s), {total_maps} maps")
        return {'FINISHED'}


class ADVBAKE_PT_baking(bpy.types.Panel):
    """Baking workflow step"""
    bl_label = "3. Baking"
    bl_idname = "ADVBAKE_PT_baking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.advbake_props
        
        # Bake settings
        layout.prop(props, "bake_type")
        layout.prop(props, "bake_scope")
        row = layout.row(align=True)
        row.prop(props, "use_selected_to_active", text="Selected to Active")
        row.prop(props, "clear_image")
        
        # Use native bake margin
        layout.prop(scene.render.bake, "margin", text="Bake Margin")

        # Render settings - use native properties
        box = layout.box()
        box.label(text="Render Settings:", icon='SETTINGS')
        col = box.column(align=True)
        
        # Native render engine
        col.prop(scene.render, "engine", text="Render Engine")
        
        if scene.render.engine == 'CYCLES':
            # Native Cycles settings
            col.prop(scene.cycles, "samples", text="Samples")
            col.prop(scene.cycles, "use_denoising", text="Denoise")
            
            if scene.cycles.use_denoising:
                col.prop(scene.cycles, "denoiser", text="Denoiser")
            
            col.prop(scene.cycles, "device", text="Device")

        # Action button
        layout.separator()
        row = layout.row()
        row.scale_y = 1.3
        
        if props.bake_type == 'PBR':
            # PBR auto-bake button
            row.operator("advbake.pbr_bake", icon='RENDER_STILL', text="Bake PBR Maps")
        else:
            # Standard bake
            bake_op = row.operator("object.bake", icon='RENDER_STILL', text="Bake")
            bake_op.type = props.bake_type


classes = (
    ADVBAKE_OT_bake_only,
    ADVBAKE_OT_auto_save_images,
    ADVBAKE_OT_pbr_bake,
    ADVBAKE_PT_baking,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
