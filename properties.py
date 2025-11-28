"""
Ultimate_Bak3 - Property Definitions
Property groups for add-on settings and configuration.
"""

import bpy
import math  # For angle conversions


class ADVBAKE_Properties(bpy.types.PropertyGroup):
    """Property group containing all bake settings and configuration."""
    
    # --------- Output / Image ---------
    output_dir: bpy.props.StringProperty(
        name="Output Folder",
        description="Folder to save baked textures",
        subtype='DIR_PATH',
        default="//bakes"
    )

    image_size: bpy.props.IntProperty(
        name="Image Size",
        description="Resolution for square bake image",
        default=2048,
        min=256,
        max=16384
    )

    image_prefix: bpy.props.StringProperty(
        name="Image Name Prefix",
        description="Prefix for baked images",
        default=""
    )

    image_format: bpy.props.EnumProperty(
        name="Image Format",
        description="File format for saved images",
        items=[
            ('PNG', "PNG", "PNG format (lossless)"),
            ('JPEG', "JPEG", "JPEG format (lossy)"),
            ('OPEN_EXR', "OpenEXR", "OpenEXR format (HDR)"),
            ('TARGA', "Targa", "Targa format"),
            ('BMP', "BMP", "BMP format"),
            ('TIFF', "TIFF", "TIFF format"),
        ],
        default='PNG'
    )

    color_depth: bpy.props.EnumProperty(
        name="Color Depth",
        description="Bit depth for image files",
        items=[
            ('8', "8-bit", "8 bits per channel"),
            ('16', "16-bit", "16 bits per channel"),
            ('32', "32-bit", "32 bits per channel (float)"),
        ],
        default='8'
    )

    auto_save: bpy.props.BoolProperty(
        name="Auto Save Images",
        description="Automatically save images after baking",
        default=True
    )

    # --------- UV / Unwrap ---------
    create_new_uv: bpy.props.BoolProperty(
        name="Create New Bake UVMap",
        description="Create a separate UV map for baking (keeps original UV for shading)",
        default=True
    )


    uvmap_name: bpy.props.StringProperty(
        name="Bake UVMap Name",
        description="Name of UV map used for baking",
        default="UVMap_Bake"
    )

    uv_mode: bpy.props.EnumProperty(
        name="UV Mode",
        description="How to name UV maps for multiple objects",
        items=[
            ('SHARED', "Shared UV", "All objects use the same UV map name (for atlas baking)"),
            ('INDIVIDUAL', "Individual UV", "Each object gets unique UV map name (ObjectName_UVMapName)")
        ],
        default='INDIVIDUAL'
    )

    unwrap_method: bpy.props.EnumProperty(
        name="Unwrap Method",
        description="Method used for bake UV unwrapping",
        items=[
            ('SMART', "Smart UV Project", "Automatic Smart UV Project"),
            ('UNWRAP', "Unwrap", "Standard Unwrap using seams"),
            ('NONE', "None", "Do not modify UVs")
        ],
        default='SMART'
    )

    # Smart UV Project parameters - EXACT Blender defaults for consistency
    smart_angle_limit: bpy.props.FloatProperty(
        name="Angle Limit",
        description="Lower angles for more projection groups, higher for less distortion",
        default=math.radians(66.0),  # 66° in radians (Blender stores angles as radians internally)
        min=math.radians(1.0),
        max=math.radians(89.0),
        subtype='ANGLE'  # Displays as degrees in UI (66°)
    )

    smart_island_margin: bpy.props.FloatProperty(
        name="Island Margin",
        description="Margin between UV islands",
        default=0.0,  # Blender default
        min=0.0,
        max=1.0
    )

    smart_area_weight: bpy.props.FloatProperty(
        name="Area Weight",
        description="Weight projection by face area",
        default=0.0,  # Blender default
        min=0.0,
        max=1.0
    )

    smart_correct_aspect: bpy.props.BoolProperty(
        name="Correct Aspect",
        description="Map UVs accounting for image aspect ratio",
        default=True  # Blender default
    )

    smart_scale_to_bounds: bpy.props.BoolProperty(
        name="Scale to Bounds",
        description="Scale UV coordinates to bounds after unwrapping",
        default=False  # Blender default
    )

    # --------- Bake settings ---------
    bake_type: bpy.props.EnumProperty(
        name="Bake Type",
        description="Bake pass / type",
        items=[
            ('PBR', "PBR (Auto-Bake All)", "Automatically bake all PBR maps: BaseColor, Roughness, Normal, AO, Metallic, Emission"),
            ('COMBINED', "Combined", "Full lighting + material"),
            ('AO', "Ambient Occlusion", "Ambient occlusion"),
            ('SHADOW', "Shadow", "Shadow pass"),
            ('POSITION', "Position", "World space position"),
            ('NORMAL', "Normal", "Normal map"),
            ('UV', "UV", "UV coordinates"),
            ('ROUGHNESS', "Roughness", "Roughness map"),
            ('EMIT', "Emit", "Emission"),
            ('ENVIRONMENT', "Environment", "Environment lighting"),
            ('DIFFUSE', "Diffuse", "Diffuse color/shading"),
            ('GLOSSY', "Glossy", "Glossy reflection"),
            ('TRANSMISSION', "Transmission", "Transmission"),
        ],
        default='COMBINED'
    )

    use_selected_to_active: bpy.props.BoolProperty(
        name="Selected to Active",
        description="Use selected meshes as source and active as target (for normal / AO high→low bake)",
        default=False
    )

    clear_image: bpy.props.BoolProperty(
        name="Clear Image Before Bake",
        description="Clear image to background color before baking",
        default=True
    )

    # --------- Scope (single / multi) ---------
    bake_scope: bpy.props.EnumProperty(
        name="Bake Scope",
        description="Scope of objects to bake",
        items=[
            ('ACTIVE', "Active Object Only", "Bake only the active mesh object"),
            ('SELECTED', "All Selected Meshes", "Bake all selected mesh objects")
        ],
        default='SELECTED'
    )

    # --------- Preset Management ---------
    def update_preset_list(self, context):
        """Callback to refresh preset list"""
        # Import root presets module (not modules.presets)
        # Use absolute import to avoid namespace conflict
        from .modules import presets as presets_module
        preset_items = []
        for preset_id, name, desc in presets_module.list_presets():
            preset_items.append((preset_id, name, desc))
        
        if not preset_items:
            preset_items.append(('NONE', "No Presets", ""))
        
        return preset_items

    selected_preset: bpy.props.EnumProperty(
        name="Preset",
        description="Select a baking preset",
        items=update_preset_list
    )

    # --------- Automation Settings ---------
    auto_enable_automation: bpy.props.BoolProperty(
        name="Enable Automation",
        description="Run multiple baking steps automatically",
        default=False
    )

    auto_include_uv: bpy.props.BoolProperty(
        name="UV Preparation",
        description="Include UV preparation in automation",
        default=True
    )

    auto_include_images: bpy.props.BoolProperty(
        name="Create Images",
        description="Include image creation in automation",
        default=True
    )

    auto_include_bake: bpy.props.BoolProperty(
        name="Bake",
        description="Include baking in automation",
        default=True
    )

    auto_include_save: bpy.props.BoolProperty(
        name="Save Images",
        description="Include image saving in automation",
        default=True
    )

    auto_include_material: bpy.props.BoolProperty(
        name="Apply Material",
        description="Include material application in automation",
        default=False
    )


# Registration
def register():
    try:
        bpy.utils.unregister_class(ADVBAKE_Properties)
    except:
        pass
    bpy.utils.register_class(ADVBAKE_Properties)
    bpy.types.Scene.advbake_props = bpy.props.PointerProperty(type=ADVBAKE_Properties)


def unregister():
    del bpy.types.Scene.advbake_props
    bpy.utils.unregister_class(ADVBAKE_Properties)
