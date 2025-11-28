# Changelog

## [3.2.6] - 2025-11-29
### Fixed
- **Version Bump**: Updated version to v3.2.6.

## [3.2.1] - 2025-11-28
### Added
- **Edit Preset UI**: Render settings now editable in preset edit popup (engine, samples, denoising, device).
- **All Preset Files Updated**: All 5 default presets now include render sections with optimized settings.

### Changed
- **Popup Width**: Increased edit preset dialog width to 450px to accommodate render settings.

## [3.2.0] - 2025-11-28
### Added
- **Render Settings in Presets**: Presets now save and restore render settings (engine, samples, denoising, device).
- **Cycles Support**: Full support for Cycles render settings in preset JSON.
- **Enhanced JSON Format**: Preset JSON now includes `render` section with engine-specific settings.

### Changed
- **Preset JSON Schema**: Updated to include render settings section.
- **Load/Save Logic**: Enhanced to handle render engine configuration.

## [3.1.0] - 2025-11-28
### Changed
- **Smart Auto Save**: Auto save now only saves newly created images from current automation session, not all images in scene.
- **Filter Logic**: Uses automation tag (`_automation_new`) or image prefix to identify images to save.
- **Better Reporting**: Changed "no images saved" from WARNING to INFO when no new images exist.

### Fixed
- **Auto Save Scope**: Fixed issue where auto save was saving ALL images including old textures and materials, not just freshly baked ones.

## [3.0.9] - 2025-11-28
### Fixed
- **Critical: Missing Properties**: Added missing `image_format`, `color_depth`, and `auto_save` properties to `ADVBAKE_Properties` class. This fixes the "Save Images: Failed" error in automation workflow.
- **Auto Save Images**: Now properly saves images with user-selected format (PNG, JPEG, TIFF, etc.).

## [3.0.8] - 2025-11-28
### Changed
- **Preset Module Consolidation**: Merged root `presets.py` (data functions) into `modules/presets.py` for simplified architecture. All preset functionality now in single module.
- **Import Cleanup**: Removed all `presets_data` imports and references. Functions now called directly within presets module.

### Fixed
- **Preset Dropdown**: Fixed preset list not populating - now imports from correct module path.
- **Preset Functions**: All save/load/edit/delete operations now working correctly.

## [3.0.7] - 2025-11-28
### Fixed
- **Critical: Panel bl_label Property**: Removed `@property` decorator from `bl_label` - Blender ignores properties for `bl_label`. Now uses static label "Updates" with version shown in panel header icon area.
- **Critical: Reload Logic**: Fixed NameError in reload branch - now uses `sys.modules["Ultimate_Bak3.presets"]` to reload root presets module instead of accessing undefined `presets_data` variable.
- **Panel Version Display**: Version now displays in panel header (e.g., "v3.0.7" with URL icon) instead of title.

## [3.0.6] - 2025-11-28
### Fixed
- **Preset Import**: Fixed namespace conflict - now uses absolute import `Ultimate_Bak3.presets` to access root presets module with `list_presets()` function.
- **Update Panel Title**: Changed to property-based dynamic label to properly display version in panel header.

## [3.0.5] - 2025-11-28
### Fixed
- **Update Panel**: Fixed `bl_info` access error that caused crashes when displaying update status. Now correctly imports from `sys.modules`.
- **Update Panel Title**: Added version number to "Updates" panel header (e.g., "Updates (v3.0.5)").
- **Preset List**: Fixed incorrect import in `properties.py` - now uses `presets_data.list_presets()` instead of `presets.list_presets()`.

## [3.0.4] - 2025-11-28
### Fixed
- **Installation Error**: Removed invalid `update_ready` property assignment that caused "property has no setter" error during addon installation.

## [3.0.3] - 2025-11-28
### Fixed
- **Hot Reload Logic**: Fixed an issue where the updater was not reconfigured after a hot reload, causing subsequent update checks to fail.
- **Update Check Stability**: Implemented a "Paranoid" fix to ensure the updater always has access to the correct version number, even if the internal state is inconsistent.
- **Syntax Fixes**: Resolved indentation errors in the update operator.

## [3.0.1] - 2025-11-28
### Fixed
- **Robust Update Check**: Added safeguard to prevent "current_version not yet defined" error. The system now auto-repairs configuration if state is lost during hot reload.

## [3.0.0] - 2025-11-28
### 🏗️ Major Refactor: Modular Architecture
- **Full Codebase Restructuring**: Transformed from monolithic structure to feature-based modules.
- **New Module System**:
  - `modules/update`: Robust update system with crash protection and hot reload.
  - `modules/presets`: Preset management and automation workflows.
  - `modules/uv`: UV preparation tools.
  - `modules/images`: Image creation and node management.
  - `modules/baking`: Baking operations (Standard & PBR).
  - `modules/materials`: Material application logic.
- **Improved Maintainability**: Each feature is now isolated, making updates safer and easier.
- **Enhanced Update System**: Fixed critical crashes during local updates by removing unsafe disable/enable cycles.

### 🚀 Improvements
- **Startup Performance**: Optimized module loading sequence.
- **Error Handling**: Better error reporting in automation and update processes.
- **Code Organization**: Clean separation of UI and logic.

---

## [2.8.5] - 2025-11-27
### Fixed
- Critical crash during local update (removed `addon_disable` call).
- Improved ZIP validation logic.
- Added timestamped backups for safer updates.

## [2.8.0] - 2025-11-26
### Added
- **Hot Reload**: Reload addon without restarting Blender.
- **Local Update**: Install from ZIP without restart.
- **GitHub Update**: Auto-check for updates.

## [2.7.0] - 2025-11-25
### Added
- **Preset System**: Save/Load bake settings.
- **Automation**: Multi-step baking workflows.
