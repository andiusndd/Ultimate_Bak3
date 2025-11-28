"""
Ultimate_Bak3 - Auto-Validation Utilities
Provides automatic schema validation, error recovery, metadata generation, and console shortcuts.
"""

import bpy
import json
import os
from typing import Dict, List, Tuple, Any


# ===================================================================
# PRESET SCHEMA VALIDATION
# ===================================================================

def get_property_schema(prop_class) -> Dict[str, Dict[str, Any]]:
    """
    ✨ Auto-extract schema from PropertyGroup class.
    
    Args:
        prop_class: PropertyGroup class (e.g., ADVBAKE_Properties)
        
    Returns:
        Dict mapping property names to their metadata
    """
    schema = {}
    
    # Get all annotations (property definitions)
    if hasattr(prop_class, '__annotations__'):
        for prop_name in prop_class.__annotations__:
            if prop_name.startswith('_'):
                continue
            
            # Get the property itself
            prop_value = getattr(prop_class, prop_name, None)
            if prop_value is not None:
                schema[prop_name] = {
                    'name': prop_name,
                    'type': type(prop_value).__name__,
                    'required': True
                }
    
    return schema


def validate_preset_data(preset_data: Dict, strict: bool = False) -> Tuple[bool, List[str]]:
    """
    ✨ Validate preset data against auto-generated schema.
    
    Args:
        preset_data: Preset dictionary to validate
        strict: If True, require ALL properties. If False, only check structure.
        
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    # Basic structure check
    if not isinstance(preset_data, dict):
        return False, ["Preset data must be a dictionary"]
    
    if 'settings' not in preset_data:
        issues.append("Missing 'settings' key")
    
    if 'name' not in preset_data:
        issues.append("Missing 'name' key")
    
    # Get schema from properties
    try:
        from .properties import ADVBAKE_Properties
        schema = get_property_schema(ADVBAKE_Properties)
        
        settings = preset_data.get('settings', {})
        
        # Check for unknown properties (might be from newer version)
        unknown_props = [k for k in settings.keys() if k not in schema]
        if unknown_props:
            issues.append(f"Unknown properties (possibly from newer version): {', '.join(unknown_props[:5])}")
        
        # In strict mode, check all required properties
        if strict:
            missing_props = [k for k in schema.keys() if k not in settings]
            if missing_props:
                issues.append(f"Missing required properties: {', '.join(missing_props[:5])}")
    
    except Exception as e:
        issues.append(f"Schema validation error: {e}")
    
    is_valid = len(issues) == 0
    return is_valid, issues


# ===================================================================
# ERROR RECOVERY / BACKUP SYSTEM
# ===================================================================

class AutoBackup:
    """✨ Auto-backup state before risky operations with rollback support."""
    
    @staticmethod
    def backup_materials(obj) -> List:
        """
        Backup all materials from an object.
        
        Args:
            obj: Blender object
            
        Returns:
            List of materials (can be None entries)
        """
        if not obj or not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'):
            return []
        
        return [mat for mat in obj.data.materials]
    
    @staticmethod
    def restore_materials(obj, materials: List) -> bool:
        """
        Restore materials to an object.
        
        Args:
            obj: Blender object
            materials: List of materials to restore
            
        Returns:
            True if successful
        """
        try:
            if not obj or not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'):
                return False
            
            obj.data.materials.clear()
            for mat in materials:
                obj.data.materials.append(mat)
            
            return True
        except Exception as e:
            print(f"[AutoBackup] Failed to restore materials: {e}")
            return False
    
    @staticmethod
    def backup_uv_maps(obj) -> Dict:
        """
        Backup UV map states (active, active_render).
        
        Args:
            obj: Blender object
            
        Returns:
            Dict with UV map states
        """
        if not obj or not hasattr(obj, 'data') or not hasattr(obj.data, 'uv_layers'):
            return {}
        
        backup = {}
        for uv in obj.data.uv_layers:
            backup[uv.name] = {
                'active': uv.active,
                'active_render': uv.active_render,
                'active_index': obj.data.uv_layers.active_index if uv.active else -1
            }
        
        return backup
    
    @staticmethod
    def restore_uv_maps(obj, uv_backup: Dict) -> bool:
        """
        Restore UV map states.
        
        Args:
            obj: Blender object
            uv_backup: Dict from backup_uv_maps()
            
        Returns:
            True if successful
        """
        try:
            if not obj or not hasattr(obj, 'data') or not hasattr(obj.data, 'uv_layers'):
                return False
            
            for uv_name, state in uv_backup.items():
                uv = obj.data.uv_layers.get(uv_name)
                if uv:
                    uv.active = state['active']
                    uv.active_render = state['active_render']
                    if state['active']:
                        obj.data.uv_layers.active = uv
            
            return True
        except Exception as e:
            print(f"[AutoBackup] Failed to restore UV maps: {e}")
            return False
    
    @staticmethod
    def create_state_snapshot(obj) -> Dict:
        """
        Create complete state snapshot of an object.
        
        Args:
            obj: Blender object
            
        Returns:
            Dict containing all backed up state
        """
        return {
            'materials': AutoBackup.backup_materials(obj),
            'uv_maps': AutoBackup.backup_uv_maps(obj),
            'object_name': obj.name if obj else None
        }
    
    @staticmethod
    def restore_state_snapshot(obj, snapshot: Dict) -> bool:
        """
        Restore complete state from snapshot.
        
        Args:
            obj: Blender object
            snapshot: Snapshot from create_state_snapshot()
            
        Returns:
            True if successful
        """
        success = True
        
        if 'materials' in snapshot:
            success = success and AutoBackup.restore_materials(obj, snapshot['materials'])
        
        if 'uv_maps' in snapshot:
            success = success and AutoBackup.restore_uv_maps(obj, snapshot['uv_maps'])
        
        return success


# ===================================================================
# METADATA GENERATION
# ===================================================================

def generate_addon_metadata(bl_info: Dict) -> Dict:
    """
    ✨ Auto-generate metadata for documentation/GitHub.
    
    Args:
        bl_info: Addon bl_info dictionary
        
    Returns:
        Dict containing addon metadata
    """
    try:
        from .properties import ADVBAKE_Properties
        from . import modules
        
        # Count properties
        prop_count = len([p for p in dir(ADVBAKE_Properties) if not p.startswith('_')])
        
        # Get modules
        module_list = [m for m in dir(modules) if not m.startswith('_')]
        
        # Get panels and operators
        panels = [name for name in dir(bpy.types) if name.startswith('ADVBAKE_PT_')]
        operators = [name for name in dir(bpy.types) if name.startswith('ADVBAKE_OT_')]
        
        metadata = {
            'name': bl_info.get('name', 'Ultimate Bak3'),
            'version': f"{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}",
            'blender_version': f"{bl_info['blender'][0]}.{bl_info['blender'][1]}.{bl_info['blender'][2]}",
            'stats': {
                'modules': len(module_list),
                'panels': len(panels),
                'operators': len(operators),
                'properties': prop_count
            },
            'components': {
                'modules': module_list,
                'panels': panels,
                'operators': operators
            }
        }
        
        return metadata
    except Exception as e:
        print(f"Error generating metadata: {e}")
        return {}


def save_metadata_file(bl_info: Dict, filepath: str = None):
    """Save metadata to JSON file"""
    if not filepath:
        addon_dir = os.path.dirname(__file__)
        filepath = os.path.join(addon_dir, 'addon_metadata.json')
    
    metadata = generate_addon_metadata(bl_info)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"[Metadata] Saved to {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"[Metadata] Failed to save: {e}")
        return False


# ===================================================================
# CONSOLE SHORTCUTS
# ===================================================================

def register_console_shortcuts():
    """
    ✨ Register convenient console shortcuts for all operators.
    Example: advbake_auto_bake() instead of bpy.ops.advbake.auto_bake()
    """
    import builtins
    
    count = 0
    for name in dir(bpy.types):
        if name.startswith('ADVBAKE_OT_'):
            op_class = getattr(bpy.types, name)
            bl_idname = op_class.bl_idname
            
            # Create shortcut name: advbake_ot_foo_bar -> advbake_foo_bar
            shortcut_name = name.lower().replace('advbake_ot_', 'advbake_')
            
            # Create wrapper function
            def create_wrapper(op_id):
                def wrapper(**kwargs):
                    return eval(f"bpy.ops.{op_id}(**kwargs)")
                return wrapper
            
            # Register in builtins (available in console)
            setattr(builtins, shortcut_name, create_wrapper(bl_idname))
            count += 1
            
    print(f"[Console] Registered {count} shortcuts (try typing 'advbake_')")


# ===================================================================
# EXPORTS
# ===================================================================

__all__ = [
    'get_property_schema',
    'validate_preset_data',
    'AutoBackup',
    'generate_addon_metadata',
    'save_metadata_file',
    'register_console_shortcuts',
]
