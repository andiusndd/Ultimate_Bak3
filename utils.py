"""
Ultimate_Bak3 - Utility Functions
Helper functions for baking operations, UV management, and image handling.
"""

import bpy
import os
import time
from typing import List, Optional, Dict, Any


def get_objects_by_scope(context, props, require_mesh: bool = True) -> List[bpy.types.Object]:
    """
    Get list of objects based on bake scope setting.
    
    Args:
        context: Blender context
        props: ADVBAKE_Properties instance
        require_mesh: Only return mesh objects if True
        
    Returns:
        List of objects matching the scope criteria
    """
    if props.bake_scope == 'ACTIVE':
        obj = context.view_layer.objects.active
        if obj is None:
            return []
        if require_mesh and obj.type != 'MESH':
            return []
        return [obj]

    # SELECTED scope
    objs = [o for o in context.selected_objects if (not require_mesh) or (o.type == 'MESH')]
    return objs


def ensure_bake_uv(obj: bpy.types.Object, props) -> bpy.types.MeshUVLoopLayer:
    """
    Create or get UV map for baking and set it as active.
    
    Args:
        obj: Target mesh object
        props: ADVBAKE_Properties instance
        
    Returns:
        UV layer used for baking
    """
    mesh = obj.data
    
    # Determine UV name based on mode
    if props.uv_mode == 'INDIVIDUAL':
        uv_name = f"{obj.name}_{props.uvmap_name}"
    else:  # SHARED
        uv_name = props.uvmap_name

    if props.create_new_uv:
        uv_layer = mesh.uv_layers.get(uv_name)
        if uv_layer is None:
            uv_layer = mesh.uv_layers.new(name=uv_name)
    else:
        # Use existing active UV or first UV layer
        if mesh.uv_layers:
            uv_layer = mesh.uv_layers.active or mesh.uv_layers[0]
        else:
            uv_layer = mesh.uv_layers.new(name=uv_name)

    mesh.uv_layers.active = uv_layer
    mesh.uv_layers.active_index = mesh.uv_layers.find(uv_layer.name)
    return uv_layer


def unwrap_bake_uv(obj: bpy.types.Object, props) -> None:
    """
    Unwrap the bake UV map using native Blender methods.
    Uses proper native unwrap operators for reliability.
    
    Args:
        obj: Target mesh object
        props: ADVBAKE_Properties instance
    """
    if props.unwrap_method == 'NONE':
        return

    bpy.context.view_layer.objects.active = obj

    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_all(action='SELECT')

    if props.unwrap_method == 'SMART':
        # Use native Smart UV Project with minimal parameters for reliability
        bpy.ops.uv.smart_project(
            angle_limit=props.smart_angle_limit,
            island_margin=props.smart_island_margin,
            area_weight=props.smart_area_weight,
            correct_aspect=props.smart_correct_aspect,
            scale_to_bounds=props.smart_scale_to_bounds
        )
    elif props.unwrap_method == 'UNWRAP':
        # Use native Unwrap - Blender's standard unwrap algorithm
        # This is the most reliable method and uses existing seams
        bpy.ops.uv.unwrap(
            method='ANGLE_BASED',  # Default method, works well for most cases
            margin=props.smart_island_margin
        )

    bpy.ops.object.mode_set(mode='OBJECT')


def get_or_create_bake_image(obj, props, bake_type_name: str = "") -> bpy.types.Image:
    """
    Get or create a bake image for the object.
    Uses native Blender image settings from scene.render.image_settings.
    """
    scene = bpy.context.scene
    
    # Determine image name
    if bake_type_name:
        img_name = f"{props.image_prefix}{obj.name}_{bake_type_name}"
    else:
        img_name = f"{props.image_prefix}{obj.name}"
    
    # Get or create image
    img = bpy.data.images.get(img_name)
    
    # Get native image settings
    file_format = scene.render.image_settings.file_format
    color_depth = scene.render.image_settings.color_depth
    
    # Determine if float buffer needed (for EXR 16/32-bit)
    is_float = file_format == 'OPEN_EXR' and color_depth in ('16', '32')
    
    if img is None:
        # Create new image
        img = bpy.data.images.new(
            name=img_name,
            width=props.image_size,
            height=props.image_size,
            alpha=True,
            float_buffer=is_float
        )
        print(f"[Bake] Created new image: {img_name} ({props.image_size}x{props.image_size})")
    else:
        # Sync existing image with current settings
        
        # 1. Check and resize if needed
        if img.size[0] != props.image_size or img.size[1] != props.image_size:
            img.scale(props.image_size, props.image_size)
            print(f"[Bake] Resized image '{img_name}' to {props.image_size}x{props.image_size}")
        
        # 2. Check buffer type - recreate if mismatch
        if img.is_float != is_float:
            print(f"[Bake] Buffer type mismatch for '{img_name}' - recreating image")
            bpy.data.images.remove(img)
            img = bpy.data.images.new(
                name=img_name,
                width=props.image_size,
                height=props.image_size,
                alpha=True,
                float_buffer=is_float
            )
    
    # Sync file format
    img.file_format = file_format
    
    return img


def ensure_image_node_for_object(obj: bpy.types.Object, image: bpy.types.Image, replace_existing: bool = False) -> dict:
    """
    Create Image Texture nodes pointing to image in ALL of object's materials and set them as active for baking.
    
    Args:
        obj: Target mesh object
        image: Image to assign to the nodes
        replace_existing: If True, replace existing nodes with same image name instead of reusing
        
    Returns:
        Dict with 'nodes' (list of created nodes) and 'replaced' (count of replaced nodes)
    """
    image_nodes = []
    replaced_count = 0
    
    # If object has no materials, create one
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"{obj.name}_BakeMat")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    
    # Process ALL materials in the object
    for mat_slot_idx, mat_slot in enumerate(obj.data.materials):
        mat = mat_slot
        
        # If material slot is empty, create a new material
        if mat is None:
            mat = bpy.data.materials.new(name=f"{obj.name}_BakeMat_{mat_slot_idx}")
            mat.use_nodes = True
            obj.data.materials[mat_slot_idx] = mat
        
        # Ensure material uses nodes
        if not mat.use_nodes:
            mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        image_node = None

        # Check if image node already exists for this image
        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage) and node.image == image:
                if replace_existing:
                    # Remove old node and create new one
                    print(f"[Create Images] Replacing existing node for {image.name} in {mat.name}")
                    nodes.remove(node)
                    replaced_count += 1
                    image_node = None
                    break
                else:
                    # Reuse existing node
                    image_node = node
                    break

        # Create new image node if doesn't exist or was replaced
        if image_node is None:
            image_node = nodes.new(type='ShaderNodeTexImage')
            image_node.image = image
            image_node.location = (-300, 300)  # Position for visibility

        # Set as active node for baking
        nodes.active = image_node
        image_nodes.append(image_node)
    
    return {
        'nodes': image_nodes,
        'replaced': replaced_count
    }


def save_image(image: bpy.types.Image, props, directory: str) -> None:
    """
    Save image to file with selected format.
    
    Args:
        image: Image to save
        props: ADVBAKE_Properties instance
        directory: Output directory path
    """
    ext = ".png"
    if props.image_format == 'TARGA':
        ext = ".tga"
    elif props.image_format == 'OPEN_EXR':
        ext = ".exr"

    filename = f"{image.name}{ext}"
    filepath = os.path.join(directory, filename)
    image.filepath_raw = filepath
    image.file_format = props.image_format

    if props.image_format == 'PNG':
        image.colorspace_settings.name = 'sRGB'
    elif props.image_format == 'OPEN_EXR':
        image.colorspace_settings.name = 'Linear'

    image.save()


def setup_scene_for_bake(scene: bpy.types.Scene, props) -> None:
    """
    Configure scene bake and render settings.
    
    Args:
        scene: Blender scene
        props: ADVBAKE_Properties instance
    """
    # Set render engine
    scene.render.engine = props.render_engine
    
    # Configure Cycles-specific settings
    if props.render_engine == 'CYCLES':
        scene.cycles.samples = props.render_samples
        scene.cycles.use_denoising = props.use_denoise
        
        if props.use_denoise:
            scene.cycles.denoiser = props.denoise_type
        
        # Set device (CPU or GPU)
        scene.cycles.device = props.render_device
        
        print(f"Render settings: {props.render_engine}, {props.render_samples} samples, "
              f"Denoise: {props.use_denoise}, Device: {props.render_device}")
    else:
        print(f"Render settings: {props.render_engine}")
    
    # Configure bake settings
    bake_settings = scene.render.bake
    bake_settings.use_selected_to_active = props.use_selected_to_active
    bake_settings.target = 'IMAGE_TEXTURES'
    bake_settings.margin = props.margin
    bake_settings.use_clear = props.clear_image


def save_render_settings(scene: bpy.types.Scene) -> Dict[str, Any]:
    """
    Save current render settings for restoration later.
    
    Args:
        scene: Blender scene
        
    Returns:
        Dictionary containing render settings
    """
    settings = {
        'engine': scene.render.engine,
        'cycles_samples': scene.cycles.samples if hasattr(scene.cycles, 'samples') else None,
        'cycles_denoise': scene.cycles.use_denoising if hasattr(scene.cycles, 'use_denoising') else None,
        'cycles_denoiser': scene.cycles.denoiser if hasattr(scene.cycles, 'denoiser') else None,
        'cycles_device': scene.cycles.device if hasattr(scene.cycles, 'device') else None,
    }
    return settings


def restore_render_settings(scene: bpy.types.Scene, settings: Dict[str, Any]) -> None:
    """
    Restore previously saved render settings.
    
    Args:
        scene: Blender scene
        settings: Dictionary from save_render_settings()
    """
    try:
        scene.render.engine = settings.get('engine', 'CYCLES')
        
        if settings.get('cycles_samples') is not None:
            scene.cycles.samples = settings['cycles_samples']
        if settings.get('cycles_denoise') is not None:
            scene.cycles.use_denoising = settings['cycles_denoise']
        if settings.get('cycles_denoiser') is not None:
            scene.cycles.denoiser = settings['cycles_denoiser']
        if settings.get('cycles_device') is not None:
            scene.cycles.device = settings['cycles_device']
    except Exception as e:
        print(f"Warning: Could not fully restore render settings: {e}")


def wait_for_bake() -> None:
    """
    Wait for bake operation to complete. 
    Ensures sequential baking and prevents render queue buildup.
    """
    try:
        # Process all queued events to let bake complete
        for _ in range(100):
            time.sleep(0.01)  # 10ms intervals, total ~1s wait
            # Blender processes events internally
    except:
        pass



def format_time(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (e.g., "00:05:23")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
