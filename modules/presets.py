"""
Ultimate_Bak3 - Presets & Automation Module
Handles saving/loading presets and running automation workflows.
"""

import bpy
import os
import json
from .. import utils
from .. import auto_utils
from ..properties import ADVBAKE_Properties


# -------------------------------------------------------------------
# Preset Data Functions (merged from root presets.py)
# -------------------------------------------------------------------

def get_preset_dir():
    """Get the directory where presets are stored (in user scripts directory)."""
    import shutil
    
    # Use Blender's user scripts directory (safe from addon updates)
    user_preset_dir = bpy.utils.user_resource('SCRIPTS', path="presets", create=True)
    if user_preset_dir:
        user_preset_dir = os.path.join(user_preset_dir, "Ultimate_Bak3")
    else:
        # Fallback to addon directory if user_resource fails
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        user_preset_dir = os.path.join(addon_dir, "presets")
    
    # Create directory if it doesn't exist
    if not os.path.exists(user_preset_dir):
        os.makedirs(user_preset_dir)
    
    # Migration: Copy old presets from addon directory to new location (one-time)
    addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    old_preset_dir = os.path.join(addon_dir, "presets")
    
    if os.path.exists(old_preset_dir) and old_preset_dir != user_preset_dir:
        print(f"[Preset Migration] Checking for old presets in: {old_preset_dir}")
        migrated_count = 0
        
        for filename in os.listdir(old_preset_dir):
            if filename.endswith('.json'):
                old_path = os.path.join(old_preset_dir, filename)
                new_path = os.path.join(user_preset_dir, filename)
                
                # Only copy if it doesn't exist in new location
                if not os.path.exists(new_path):
                    try:
                        shutil.copy2(old_path, new_path)
                        migrated_count += 1
                        print(f"[Preset Migration] Migrated: {filename}")
                    except Exception as e:
                        print(f"[Preset Migration] Failed to migrate {filename}: {e}")
        
        if migrated_count > 0:
            print(f"[Preset Migration] Successfully migrated {migrated_count} preset(s)")
    
    return user_preset_dir


def save_preset(props, filepath: str, name: str, description: str = ""):
    """
    Save current addon settings to a preset file.
    
    Args:
        props: ADVBAKE_Properties instance
        filepath: Full path to save preset JSON
        name: Preset name
        description: Preset description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import bpy
        scene = bpy.context.scene
        
        # Gather render settings
        render_settings = {
            "engine": scene.render.engine,
        }
        
        # Cycles-specific settings
        if scene.render.engine == 'CYCLES':
            render_settings.update({
                "cycles_samples": scene.cycles.samples,
                "cycles_use_denoising": scene.cycles.use_denoising,
                "cycles_denoiser": scene.cycles.denoiser if scene.cycles.use_denoising else "OPTIX",
                "cycles_device": scene.cycles.device,
            })
        
        preset_data = {
            "name": name,
            "description": description,
            "version": "1.0",
            "settings": {
                "output_dir": props.output_dir,
                "image_size": props.image_size,
                "image_prefix": props.image_prefix,
                "image_format": props.image_format,
                "color_depth": props.color_depth,
                "auto_save": props.auto_save,
                "create_new_uv": props.create_new_uv,
                "uvmap_name": props.uvmap_name,
                "uv_mode": props.uv_mode,
                "unwrap_method": props.unwrap_method,
                "bake_type": props.bake_type,
                "use_selected_to_active": props.use_selected_to_active,
                "cage_extrusion": getattr(props, 'cage_extrusion', 0.1),
                "max_ray_distance": getattr(props, 'max_ray_distance', 0.0),
            },
            "render": render_settings
        }
        
        with open(filepath, 'w') as f:
            json.dump(preset_data, f, indent=4)
        
        print(f"[Preset] Saved: {filepath}")
        return True
    except Exception as e:
        print(f"[Preset] Error saving: {e}")
        return False


def load_preset(props, filepath: str):
    """
    Load preset from file and apply to current settings.
    
    Args:
        props: ADVBAKE_Properties instance
        filepath: Full path to preset JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import bpy
        
        with open(filepath, 'r') as f:
            preset_data = json.load(f)
        
        settings = preset_data.get("settings", {})
        render = preset_data.get("render", {})
        
        # Apply addon settings
        props.output_dir = settings.get("output_dir", "//bakes")
        props.image_size = settings.get("image_size", 2048)
        props.image_prefix = settings.get("image_prefix", "")
        props.image_format = settings.get("image_format", "PNG")
        props.color_depth = settings.get("color_depth", "8")
        props.auto_save = settings.get("auto_save", True)
        props.create_new_uv = settings.get("create_new_uv", True)
        props.uvmap_name = settings.get("uvmap_name", "UVMap_Bake")
        props.uv_mode = settings.get("uv_mode", "INDIVIDUAL")
        props.unwrap_method = settings.get("unwrap_method", "SMART")
        props.bake_type = settings.get("bake_type", "COMBINED")
        props.use_selected_to_active = settings.get("use_selected_to_active", False)
        
        # Apply render settings if present
        if render:
            scene = bpy.context.scene
            
            # Apply render engine
            if "engine" in render:
                scene.render.engine = render["engine"]
                print(f"  → Render Engine: {render['engine']}")
            
            # Apply Cycles settings if engine is Cycles
            if scene.render.engine == 'CYCLES':
                if "cycles_samples" in render:
                    scene.cycles.samples = render["cycles_samples"]
                    print(f"  → Samples: {render['cycles_samples']}")
                
                if "cycles_use_denoising" in render:
                    scene.cycles.use_denoising = render["cycles_use_denoising"]
                    print(f"  → Denoising: {render['cycles_use_denoising']}")
                
                if "cycles_denoiser" in render and scene.cycles.use_denoising:
                    scene.cycles.denoiser = render["cycles_denoiser"]
                    print(f"  → Denoiser: {render['cycles_denoiser']}")
                
                if "cycles_device" in render:
                    scene.cycles.device = render["cycles_device"]
                    print(f"  → Device: {render['cycles_device']}")
        
        print(f"[Preset] Loaded: {filepath}")
        return True
    except Exception as e:
        print(f"[Preset] Error loading: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_presets():
    """
    Get list of available presets.
    
    Returns:
        List of tuples: (identifier, name, description)
    """
    preset_dir = get_preset_dir()
    presets = []
    
    if not os.path.exists(preset_dir):
        return presets
    
    for filename in os.listdir(preset_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(preset_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                preset_id = filename[:-5]  # Remove .json
                name = data.get("name", preset_id)
                description = data.get("description", "")
                
                presets.append((preset_id, name, description))
            except:
                continue
    
    return presets


def delete_preset(filepath: str):
    """
    Delete a preset file.
    
    Args:
        filepath: Full path to preset file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"[Preset] Deleted: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"[Preset] Error deleting: {e}")
        return False


def get_preset_path(preset_id: str):
    """
    Get full path to preset file from identifier.
    
    Args:
        preset_id: Preset identifier (filename without extension)
        
    Returns:
        Full path to preset JSON file
    """
    preset_dir = get_preset_dir()
    return os.path.join(preset_dir, f"{preset_id}.json")


def validate_preset(filepath: str):
    """
    Validate preset file structure using auto-generated schema.
    
    Args:
        filepath: Path to preset file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Use auto-validation from utilities
        is_valid, issues = auto_utils.validate_preset_data(data, strict=False)
        
        if not is_valid:
            return (False, "; ".join(issues))
            
        return (True, "")
    except Exception as e:
        return (False, str(e))


# -------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------

class ADVBAKE_OT_save_preset(bpy.types.Operator):
    """Save current settings as a preset"""
    bl_idname = "advbake.save_preset"
    bl_label = "Save Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name for this preset",
        default="My Preset"
    )
    
    preset_description: bpy.props.StringProperty(
        name="Description",
        description="Description of this preset",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "preset_description")

    def execute(self, context):
        props = context.scene.advbake_props
        
        # Create safe filename
        safe_name = "".join(c for c in self.preset_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        if not safe_name:
            self.report({'ERROR'}, "Invalid preset name")
            return {'CANCELLED'}
        
        filepath = get_preset_path(safe_name)
        
        # Check if file exists
        if os.path.exists(filepath):
            self.report({'WARNING'}, f"Overwriting existing preset: {self.preset_name}")
        
        success = save_preset(props, filepath, self.preset_name, self.preset_description)
        
        if success:
            # Set to newly saved preset (triggers list refresh)
            props.selected_preset = safe_name
            
            self.report({'INFO'}, f"✓ Preset saved: {self.preset_name}")
            print(f"[Preset] Saved and selected: {safe_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save preset")
            return {'CANCELLED'}


class ADVBAKE_OT_load_preset(bpy.types.Operator):
    """Load selected preset and apply settings"""
    bl_idname = "advbake.load_preset"
    bl_label = "Load Preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.advbake_props
        
        if props.selected_preset == 'NONE':
            self.report({'WARNING'}, "No preset selected")
            return {'CANCELLED'}
        
        filepath = get_preset_path(props.selected_preset)
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Preset file not found: {props.selected_preset}")
            return {'CANCELLED'}
        
        success = load_preset(props, filepath)
        
        if success:
            # Get preset name from file for better feedback
            try:
                with open(filepath, 'r') as f:
                    preset_data_json = json.load(f)
                preset_name = preset_data_json.get("name", props.selected_preset)
            except:
                preset_name = props.selected_preset
            
            self.report({'INFO'}, f"✓ Preset loaded: {preset_name}")
            
            # Force UI refresh to show new settings
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to load preset")
            return {'CANCELLED'}


class ADVBAKE_OT_edit_preset(bpy.types.Operator):
    """Edit selected preset in a popup window"""
    bl_idname = "advbake.edit_preset"
    bl_label = "Edit Preset"
    bl_options = {'REGISTER', 'UNDO'}

    # Metadata
    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Display name for this preset"
    )
    
    preset_description: bpy.props.StringProperty(
        name="Description",
        description="Description of this preset"
    )
    
    # UV Settings
    uv_mode: bpy.props.EnumProperty(
        name="UV Mode",
        items=[
            ('INDIVIDUAL', "Individual", ""),
            ('SHARED', "Shared", "")
        ]
    )
    
    unwrap_method: bpy.props.EnumProperty(
        name="Unwrap Method",
        items=[
            ('SMART', "Smart UV Project", ""),
            ('UNWRAP', "Unwrap", ""),
            ('NONE', "None", "")
        ]
    )
    
    image_size: bpy.props.IntProperty(
        name="Image Size",
        min=64, max=16384,
        default=2048
    )
    
    image_prefix: bpy.props.StringProperty(
        name="Image Prefix",
        default=""
    )
    
    output_dir: bpy.props.StringProperty(
        name="Output Directory",
        subtype='DIR_PATH',
        default="//bakes"
    )
    
    image_format: bpy.props.EnumProperty(
        name="Image Format",
        items=[
            ('PNG', "PNG", ""),
            ('JPEG', "JPEG", ""),
            ('OPEN_EXR', "OpenEXR", ""),
            ('TARGA', "Targa", ""),
            ('BMP', "BMP", ""),
            ('TIFF', "TIFF", "")
        ]
    )
    
    color_depth: bpy.props.EnumProperty(
        name="Color Depth",
        items=[
            ('8', "8-bit", ""),
            ('16', "16-bit", ""),
            ('32', "32-bit", "")
        ]
    )
    
    bake_type: bpy.props.EnumProperty(
        name="Bake Type",
        items=[
            ('PBR', "PBR (Auto)", ""),
            ('COMBINED', "Combined", ""),
            ('AO', "Ambient Occlusion", ""),
            ('NORMAL', "Normal", ""),
            ('ROUGHNESS', "Roughness", ""),
            ('EMIT', "Emission", "")
        ]
    )

    # Render Settings
    render_engine: bpy.props.EnumProperty(
        name="Render Engine",
        items=[
            ('CYCLES', "Cycles", ""),
            ('BLENDER_EEVEE', "Eevee", "")
        ],
        default='CYCLES'
    )
    
    cycles_samples: bpy.props.IntProperty(
        name="Samples",
        min=1, max=4096,
        default=128
    )
    
    cycles_use_denoising: bpy.props.BoolProperty(
        name="Use Denoising",
        default=True
    )
    
    cycles_denoiser: bpy.props.EnumProperty(
        name="Denoiser",
        items=[
            ('OPTIX', "OptiX", ""),
            ('OPENIMAGEDENOISE', "OpenImageDenoise", "")
        ],
        default='OPTIX'
    )
    
    cycles_device: bpy.props.EnumProperty(
        name="Device",
        items=[
            ('GPU', "GPU Compute", ""),
            ('CPU', "CPU", "")
        ],
        default='GPU'
    )

    def invoke(self, context, event):
        props = context.scene.advbake_props
        
        if props.selected_preset == 'NONE':
            self.report({'WARNING'}, "No preset selected")
            return {'CANCELLED'}
        
        # Load preset data
        filepath = get_preset_path(props.selected_preset)
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Preset file not found")
            return {'CANCELLED'}
        
        try:
            with open(filepath, 'r') as f:
                preset_data_json = json.load(f)
            
            # Load metadata
            self.preset_name = preset_data_json.get("name", "")
            self.preset_description = preset_data_json.get("description", "")
            
            # Load settings
            settings = preset_data_json.get("settings", {})
            self.uv_mode = settings.get("uv_mode", "INDIVIDUAL")
            self.unwrap_method = settings.get("unwrap_method", "SMART")
            self.image_size = settings.get("image_size", 2048)
            self.image_prefix = settings.get("image_prefix", "")
            self.output_dir = settings.get("output_dir", "//bakes")
            self.image_format = settings.get("image_format", "PNG")
            self.color_depth = settings.get("color_depth", "8")
            self.bake_type = settings.get("bake_type", "COMBINED")
            
            # Load render settings
            render = preset_data_json.get("render", {})
            self.render_engine = render.get("engine", "CYCLES")
            self.cycles_samples = render.get("cycles_samples", 128)
            self.cycles_use_denoising = render.get("cycles_use_denoising", True)
            self.cycles_denoiser = render.get("cycles_denoiser", "OPTIX")
            self.cycles_device = render.get("cycles_device", "GPU")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load preset: {e}")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        
        # Metadata
        box = layout.box()
        box.label(text="Preset Information", icon='INFO')
        box.prop(self, "preset_name")
        box.prop(self, "preset_description")
        
        # UV Settings
        box = layout.box()
        box.label(text="UV Settings", icon='UV')
        box.prop(self, "uv_mode")
        box.prop(self, "unwrap_method")
        
        # Image Settings
        box = layout.box()
        box.label(text="Image Settings", icon='IMAGE_DATA')
        box.prop(self, "image_size")
        box.prop(self, "image_prefix")
        box.prop(self, "output_dir")
        box.prop(self, "image_format")
        box.prop(self, "color_depth")
        
        # Bake Settings
        box = layout.box()
        box.label(text="Bake Settings", icon='RENDER_STILL')
        box.prop(self, "bake_type")
        
        # Render Settings
        box = layout.box()
        box.label(text="Render Settings", icon='SCENE')
        box.prop(self, "render_engine")
        
        if self.render_engine == 'CYCLES':
            box.prop(self, "cycles_samples")
            box.prop(self, "cycles_use_denoising")
            if self.cycles_use_denoising:
                box.prop(self, "cycles_denoiser")
            box.prop(self, "cycles_device")

    def execute(self, context):
        props = context.scene.advbake_props
        preset_id = props.selected_preset
        filepath = get_preset_path(preset_id)
        
        # Read existing preset
        try:
            with open(filepath, 'r') as f:
                preset_data_json = json.load(f)
            
            # Update with edited values
            preset_data_json["name"] = self.preset_name
            preset_data_json["description"] = self.preset_description
            
            settings = preset_data_json.get("settings", {})
            settings["uv_mode"] = self.uv_mode
            settings["unwrap_method"] = self.unwrap_method
            settings["image_size"] = self.image_size
            settings["image_prefix"] = self.image_prefix
            settings["output_dir"] = self.output_dir
            settings["image_format"] = self.image_format
            settings["color_depth"] = self.color_depth
            settings["bake_type"] = self.bake_type
            
            # Update render settings
            if "render" not in preset_data_json:
                preset_data_json["render"] = {}
            
            preset_data_json["render"]["engine"] = self.render_engine
            preset_data_json["render"]["cycles_samples"] = self.cycles_samples
            preset_data_json["render"]["cycles_use_denoising"] = self.cycles_use_denoising
            preset_data_json["render"]["cycles_denoiser"] = self.cycles_denoiser
            preset_data_json["render"]["cycles_device"] = self.cycles_device
            
            # Save back to file
            with open(filepath, 'w') as f:
                json.dump(preset_data_json, f, indent=4)
            
            self.report({'INFO'}, f"✓ Preset updated: {self.preset_name}")
            print(f"[Preset] Updated: {self.preset_name}")
            
            # Refresh UI
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update preset: {e}")
            return {'CANCELLED'}


class ADVBAKE_OT_delete_preset(bpy.types.Operator):
    """Delete selected preset"""
    bl_idname = "advbake.delete_preset"
    bl_label = "Delete Preset"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        props = context.scene.advbake_props
        
        if props.selected_preset == 'NONE':
            self.report({'WARNING'}, "No preset selected")
            return {'CANCELLED'}
        
        filepath = get_preset_path(props.selected_preset)
        success = delete_preset(filepath)
        
        if success:
            self.report({'INFO'}, f"Preset deleted: {props.selected_preset}")
            # Refresh list
            props.property_unset("selected_preset")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to delete preset")
            return {'CANCELLED'}


class ADVBAKE_OT_auto_bake(bpy.types.Operator):
    """Run automated baking workflow with visual progress"""
    bl_idname = "advbake.auto_bake"
    bl_label = "Run Automation"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Modal state
    _timer = None
    _steps = []
    _current_step = 0
    _total_steps = 0
    _images_before_bake = set()
    _cancelled = False
    
    def modal(self, context, event):
        wm = context.window_manager
        
        # Handle cancel
        if event.type == 'ESC' or self._cancelled:
            self.cancel(context)
            self.report({'WARNING'}, "❌ Automation cancelled by user")
            return {'CANCELLED'}
        
        # Process next step on timer
        if event.type == 'TIMER':
            if self._current_step >= self._total_steps:
                # All steps complete
                self.finish(context)
                return {'FINISHED'}
            
            # Execute current step
            success = self.execute_step(context)
            
            if not success:
                self.cancel(context)
                return {'CANCELLED'}
            
            # Move to next step
            self._current_step += 1
            
            # Update progress
            progress = int((self._current_step / self._total_steps) * 100)
            wm.progress_update(progress)
            
            # Force UI redraw
            for window in wm.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
        
        return {'RUNNING_MODAL'}
    
    def execute_step(self, context):
        """Execute current automation step"""
        props = context.scene.advbake_props
        
        step_data = self._steps[self._current_step]
        step_name = step_data[0]
        operator_id = step_data[1]
        
        i = self._current_step + 1
        progress = int((i - 1) / self._total_steps * 100)
        
        # Progress header
        print(f"\n{'─'*60}")
        print(f"[Automation] Step {i}/{self._total_steps}: {step_name}")
        print(f"[Progress] {i-1}/{self._total_steps} steps completed ({progress}%)")
        print(f"{'─'*60}")
        
        # Status bar notification
        status_msg = f"⏳ Step {i}/{self._total_steps}: {step_name}"
        self.report({'INFO'}, status_msg)
        
        try:
            # Execute operator
            if operator_id == "object.bake":
                bake_type = step_data[2]
                print(f"  → Executing: object.bake(type={bake_type})")
                
                # Native bake shows its own progress bar
                result = bpy.ops.object.bake(type=bake_type)
                
                # Track images created during bake
                if step_name == "Bake" or "Bake" in step_name:
                    images_after_bake = set(bpy.data.images.keys())
                    new_images = images_after_bake - self._images_before_bake
                    
                    # Mark new images for saving
                    for img_name in new_images:
                        img = bpy.data.images.get(img_name)
                        if img:
                            img["_automation_new"] = True
                            print(f"  → Tagged new image: {img_name}")
            else:
                print(f"  → Executing: {operator_id}()")
                result = eval(f"bpy.ops.{operator_id}()")
            
            if 'CANCELLED' in result or 'ERROR' in result:
                print(f"  ✗ FAILED")
                self.report({'ERROR'}, f"❌ {step_name}: Failed")
                return False
            else:
                print(f"  ✓ Completed successfully")
                
                # Completion notification
                complete_msg = f"✓ {step_name}: Done"
                self.report({'INFO'}, complete_msg)
                return True
                
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            self.report({'ERROR'}, f"❌ {step_name}: Error - {str(e)}")
            return False
    
    def invoke(self, context, event):
        props = context.scene.advbake_props
        wm = context.window_manager
        
        # Build list of steps to execute
        self._steps = []
        if props.auto_include_uv:
            self._steps.append(("UV Preparation", "advbake.prepare_uv"))
        if props.auto_include_images:
            self._steps.append(("Create Images", "advbake.create_images"))
        if props.auto_include_bake:
            if props.bake_type == 'PBR':
                self._steps.append(("PBR Bake", "advbake.pbr_bake"))
            else:
                self._steps.append(("Bake", "object.bake", props.bake_type))
        if props.auto_include_save:
            self._steps.append(("Save Images", "advbake.auto_save_images"))
        if props.auto_include_material:
            if props.bake_type == 'PBR':
                self._steps.append(("Apply PBR Material", "advbake.apply_pbr_material"))
            else:
                self._steps.append(("Apply Material", "advbake.apply_baked_material"))
        
        if not self._steps:
            self.report({'WARNING'}, "No automation steps selected")
            return {'CANCELLED'}
        
        self._total_steps = len(self._steps)
        self._current_step = 0
        self._cancelled = False
        
        # Track newly created images BEFORE baking
        self._images_before_bake = set(bpy.data.images.keys())
        
        # Start progress
        wm.progress_begin(0, 100)
        
        # Execute steps sequentially with progress reporting
        print(f"\n{'='*60}")
        print(f"[Automation] Starting workflow with {self._total_steps} steps...")
        print(f"[Automation] Press ESC to cancel")
        print(f"{'='*60}\n")
        
        # Add timer for modal execution
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def finish(self, context):
        """Clean up and finish successfully"""
        wm = context.window_manager
        
        # Remove timer
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        # End progress
        wm.progress_end()
        
        print(f"\n{'='*60}")
        print(f"[Automation] ✓ Workflow complete!")
        print(f"[Automation] All {self._total_steps} steps executed successfully")
        print(f"{'='*60}\n")
        
        # Final status
        self.report({'INFO'}, f"✅ Automation: All {self._total_steps} Steps Done")
    
    def cancel(self, context):
        """Clean up on cancel"""
        wm = context.window_manager
        
        # Remove timer
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        # End progress
        wm.progress_end()
        
        print(f"\n{'='*60}")
        print(f"[Automation] ✗ Cancelled at step {self._current_step + 1}/{self._total_steps}")
        print(f"{'='*60}\n")
    
    def execute(self, context):
        """Fallback for non-modal execution"""
        return self.invoke(context, None)


# -------------------------------------------------------------------
# UI Panel
# -------------------------------------------------------------------

class ADVBAKE_PT_presets(bpy.types.Panel):
    """Preset and Automation panel"""
    bl_label = "0. Presets & Automation"
    bl_idname = "ADVBAKE_PT_presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ultimate Bak3"
    bl_order = 1  # After update panel

    def draw(self, context):
        layout = self.layout
        props = context.scene.advbake_props
        
        # Preset selector
        layout.label(text="Preset:", icon='PRESET')
        layout.prop(props, "selected_preset", text="")
        
        # Preset action buttons
        row = layout.row(align=True)
        row.operator("advbake.load_preset", icon='IMPORT', text="Load")
        row.operator("advbake.save_preset", icon='EXPORT', text="Save")
        
        # Edit and Delete in second row
        row = layout.row(align=True)
        row.operator("advbake.edit_preset", icon='GREASEPENCIL', text="Edit")
        row.operator("advbake.delete_preset", icon='TRASH', text="Delete")
        
        layout.separator()
        
        # Automation section
        box = layout.box()
        box.label(text="Automation Workflow", icon='PLAY')
        box.prop(props, "auto_enable_automation", text="Enable Automation")
        
        if props.auto_enable_automation:
            col = box.column(align=True)
            col.prop(props, "auto_include_uv", toggle=True)
            col.prop(props, "auto_include_images", toggle=True)
            col.prop(props, "auto_include_bake", toggle=True)
            col.prop(props, "auto_include_save", toggle=True)
            col.prop(props, "auto_include_material", toggle=True)
            
            layout.separator()
            row = layout.row()
            row.scale_y = 1.5
            row.operator("advbake.auto_bake", icon='PLAY', text="Run Automation")


# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------

classes = (
    ADVBAKE_OT_save_preset,
    ADVBAKE_OT_load_preset,
    ADVBAKE_OT_edit_preset,
    ADVBAKE_OT_delete_preset,
    ADVBAKE_OT_auto_bake,
    ADVBAKE_PT_presets,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
