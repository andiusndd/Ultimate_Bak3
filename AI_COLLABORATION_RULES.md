# AI Collaboration Rules for Blender Addon Development

> **Best practices for working with AI assistants on modular, automated Blender addon projects**

Based on the Ultimate Bak3 project architecture and development experience.

---

## 🎯 Core Principles

### 1. **Modular Thinking First**
When requesting features from AI:
- ✅ **DO**: "Create a self-contained module for UV unwrapping with its own operators and UI"
- ❌ **DON'T**: "Add UV unwrapping to the main file"

**Why**: Modular requests lead to maintainable, auto-discoverable code.

### 2. **Automation Over Manual Work**
When designing systems:
- ✅ **DO**: "Design a system that auto-discovers and registers modules"
- ❌ **DON'T**: "Add manual import statements for each module"

**Why**: Automation reduces human error and maintenance burden.

### 3. **Validation & Safety First**
When implementing features:
- ✅ **DO**: "Add schema validation and error recovery with rollback"
- ❌ **DON'T**: "Just implement the feature without error handling"

**Why**: Professional code prevents data loss and handles edge cases.

---

## 📝 Communication Guidelines

### Rule 1: Be Specific About Architecture
**Good Request:**
```
Create a new module `modules/export.py` that:
- Has its own operators (ADVBAKE_OT_export_*)
- Has its own panel (ADVBAKE_PT_export)
- Implements register()/unregister()
- Uses AutoBackup for state management
- Validates inputs with schema
```

**Bad Request:**
```
Add export functionality
```

### Rule 2: Reference Existing Patterns
**Good Request:**
```
Follow the same pattern as modules/materials.py:
- Use AutoBackup.create_snapshot() before changes
- Implement validation helpers (validate_object, validate_uv_map)
- Add comprehensive error reporting
```

**Bad Request:**
```
Make it work like materials
```

### Rule 3: Specify Integration Points
**Good Request:**
```
Integrate with auto_utils.py:
- Use validate_preset_data() for preset validation
- Use AutoBackup for state snapshots
- Register console shortcuts via register_console_shortcuts()
```

**Bad Request:**
```
Make it work with the existing system
```

---

## 🏗️ Architecture Requests

### Rule 4: Always Request Auto-Discovery Compatible Code
**Template:**
```python
# modules/new_feature.py

import bpy
from .. import utils
from .. import auto_utils

class ADDONNAME_OT_action(bpy.types.Operator):
    """Operator implementation"""
    bl_idname = "addonname.action"
    bl_label = "Action"
    
    def execute(self, context):
        # Implementation
        return {'FINISHED'}

class ADDONNAME_PT_panel(bpy.types.Panel):
    """Panel implementation"""
    bl_label = "Feature"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Addon Name'
    
    def draw(self, context):
        # UI layout
        pass

def register():
    bpy.utils.register_class(ADDONNAME_OT_action)
    bpy.utils.register_class(ADDONNAME_PT_panel)

def unregister():
    bpy.utils.unregister_class(ADDONNAME_PT_panel)
    bpy.utils.unregister_class(ADDONNAME_OT_action)
```

**Request Format:**
```
Create a new module following the template above for [feature name].
Include:
- Operators with proper bl_idname naming
- Panel with bl_order for positioning
- Validation helpers
- Error recovery
- Console shortcuts compatibility
```

### Rule 5: Request Comprehensive Testing
**Good Request:**
```
After implementation, provide:
1. Syntax validation command (python -m py_compile)
2. Runtime test script for Blender console
3. Integration test with existing modules
4. Expected console output
```

**Bad Request:**
```
Test if it works
```

---

## 🔧 Code Quality Standards

### Rule 6: Demand Professional Code
**Checklist for AI:**
```
□ Comprehensive docstrings
□ Type hints where applicable
□ Error handling with try-except
□ User-friendly error messages
□ Console logging for debugging
□ Follows PEP 8 style
□ No duplicate code
□ No hardcoded values
```

**Request Format:**
```
Implement [feature] with:
- Full docstrings (Google style)
- Type hints for function signatures
- Try-except blocks with specific error handling
- self.report() for user feedback
- print() statements for debug logging
```

### Rule 7: Request Defensive Programming
**Pattern to Request:**
```python
# Always request this pattern
snapshot = auto_utils.AutoBackup.create_state_snapshot(obj)
try:
    # Risky operation
    result = perform_operation(obj)
except Exception as e:
    # Rollback on error
    auto_utils.AutoBackup.restore_state_snapshot(obj, snapshot)
    self.report({'ERROR'}, f"Operation failed: {e}")
    return {'CANCELLED'}
```

**Request Format:**
```
Implement [operation] with:
- State snapshot before changes
- Automatic rollback on any exception
- Detailed error reporting
- User-friendly error messages
```

---

## 📚 Documentation Requests

### Rule 8: Request Documentation Alongside Code
**Good Request:**
```
Create the feature AND:
1. Add docstring to README.md "Adding New Features" section
2. Update ARCHITECTURE.md with integration points
3. Add example usage to walkthrough.md
4. Include console test commands
```

**Bad Request:**
```
Create the feature (no documentation mentioned)
```

### Rule 9: Request Code Comments for Complex Logic
**Good Request:**
```
For complex algorithms, add:
- Step-by-step comments explaining the logic
- Why certain approaches were chosen
- Edge cases being handled
- Performance considerations
```

**Example:**
```python
def complex_algorithm(data):
    """
    Process data using optimized algorithm.
    
    Algorithm choice: Binary search over linear search
    Reason: O(log n) vs O(n) for large datasets
    Edge cases: Empty data, single item, duplicates
    """
    # Step 1: Sort data for binary search (O(n log n))
    sorted_data = sorted(data)
    
    # Step 2: Binary search (O(log n))
    # ...
```

---

## 🐛 Debugging & Fixing

### Rule 10: Provide Context When Reporting Issues
**Good Bug Report:**
```
Issue: Missing Update panel after installation

Context:
- Addon version: 3.2.4
- Blender version: 3.6
- Installation method: ZIP install
- Console output: [paste output]
- Expected: Update panel in N-Panel
- Actual: Panel not visible

Files involved:
- modules/__init__.py (auto-discovery)
- modules/update/__init__.py (package)
- __init__.py (main registration)

Hypothesis: Auto-discovery not detecting packages, only .py files
```

**Bad Bug Report:**
```
It doesn't work
```

### Rule 11: Request Systematic Debugging
**Good Request:**
```
Debug the issue by:
1. Check syntax with py_compile
2. Verify imports in modules/__init__.py
3. Test auto-discovery with print statements
4. Check registration flow in console
5. Verify panel registration with dir(bpy.types)
```

**Bad Request:**
```
Fix the bug
```

---

## 🚀 Feature Development Workflow

### Rule 12: Follow Phased Approach
**Request Template:**
```
Phase 1 - Planning:
- Review existing architecture
- Identify integration points
- Design module structure

Phase 2 - Implementation:
- Create module file
- Implement operators
- Implement UI
- Add validation
- Add error recovery

Phase 3 - Testing:
- Syntax validation
- Runtime testing
- Integration testing

Phase 4 - Documentation:
- Update README.md
- Add code comments
- Create usage examples
```

### Rule 13: Request Incremental Development
**Good Approach:**
```
Step 1: Create basic module structure with register/unregister
Step 2: Add operator with minimal functionality
Step 3: Add validation and error handling
Step 4: Add UI panel
Step 5: Integrate with auto_utils
Step 6: Add tests and documentation
```

**Bad Approach:**
```
Create the entire feature at once
```

---

## 🔍 Code Review Requests

### Rule 14: Request Comprehensive Reviews
**Good Request:**
```
Review the implementation for:
1. Auto-discovery compatibility
2. Error handling completeness
3. Code duplication
4. Performance issues
5. Security concerns
6. Documentation quality
7. Test coverage
```

### Rule 15: Request Specific Improvements
**Good Request:**
```
Optimize this code for:
- Reduce time complexity from O(n²) to O(n log n)
- Add caching for repeated calculations
- Use list comprehension instead of loops
- Extract magic numbers to constants
```

**Bad Request:**
```
Make it better
```

---

## 🎓 Learning & Knowledge Transfer

### Rule 16: Request Explanations
**Good Request:**
```
Explain why this approach was chosen:
- Why auto-discovery over manual imports?
- Why schema validation over manual checks?
- Why error recovery over simple try-except?
- What are the trade-offs?
```

### Rule 17: Request Best Practices
**Good Request:**
```
What are the best practices for:
- Blender operator design
- PropertyGroup organization
- Panel layout optimization
- Performance in large scenes
- Memory management
```

---

## 📊 Metrics & Validation

### Rule 18: Request Measurable Outcomes
**Good Request:**
```
Verify that:
- All 6 modules are discovered (print count)
- All 15 operators are registered (check bpy.types)
- All 6 panels are visible (check N-Panel)
- Console shortcuts work (test in console)
- No syntax errors (py_compile all files)
```

### Rule 19: Request Performance Benchmarks
**Good Request:**
```
Benchmark:
- Module discovery time
- Registration time
- Operator execution time
- Memory usage before/after
```

---

## 🔄 Iteration & Refinement

### Rule 20: Request Iterative Improvements
**Pattern:**
```
Version 1: Basic functionality
Version 2: Add validation
Version 3: Add error recovery
Version 4: Add automation
Version 5: Optimize performance
Version 6: Polish UI/UX
```

**Request Format:**
```
Current version: [describe]
Next iteration: [specific improvements]
Success criteria: [measurable goals]
```

---

## 💡 Pro Tips for AI Collaboration

### 1. **Use Examples from Existing Code**
```
"Follow the same pattern as modules/materials.py lines 128-220"
```

### 2. **Reference Specific Files**
```
"Integrate with auto_utils.py AutoBackup class"
```

### 3. **Provide Expected Output**
```
Expected console output:
✓ Registered: new_feature
[Console] Registered 16 shortcuts
```

### 4. **Request Verification Steps**
```
After implementation, verify:
1. python -m py_compile modules/new_feature.py
2. Check bpy.types for ADDONNAME_PT_new_feature
3. Test operator in console: addonname_new_action()
```

### 5. **Ask for Alternatives**
```
Provide 2-3 implementation approaches with pros/cons
```

---

## 🚫 Common Pitfalls to Avoid

### ❌ DON'T: Vague Requests
```
"Add a feature"
"Fix the bug"
"Make it better"
```

### ✅ DO: Specific Requests
```
"Add a UV unwrapping module following the template in modules/materials.py"
"Fix the auto-discovery bug where packages are not detected"
"Optimize the image search algorithm from O(n²) to O(n log n)"
```

### ❌ DON'T: Assume AI Knows Context
```
"Update that function"
"Fix the issue we discussed"
```

### ✅ DO: Provide Full Context
```
"Update the validate_preset_data() function in auto_utils.py to handle missing fields gracefully"
"Fix the issue in modules/__init__.py where os.path.dirname() is called without importing os"
```

### ❌ DON'T: Request Everything at Once
```
"Create a complete export system with all features"
```

### ✅ DO: Break Down Requests
```
"Step 1: Create basic export module structure
Step 2: Add FBX export operator
Step 3: Add validation
Step 4: Add UI panel"
```

---

## 📋 Quick Reference Checklist

When requesting AI assistance, ensure:

```
□ Specific feature/fix described
□ Existing patterns referenced
□ Integration points identified
□ Error handling requested
□ Validation requested
□ Testing steps included
□ Documentation updates mentioned
□ Success criteria defined
□ Expected output provided
□ Verification steps listed
```

---

## 🎯 Example: Perfect AI Request

```
Task: Create a new texture export module

Requirements:
1. File: modules/export.py
2. Follow pattern: modules/materials.py (validation, error recovery)
3. Operators:
   - ADVBAKE_OT_export_textures (export all baked images)
   - ADVBAKE_OT_export_single (export selected image)
4. Panel: ADVBAKE_PT_export (bl_order = 6)
5. Features:
   - Use AutoBackup for state management
   - Validate export path exists
   - Support multiple formats (PNG, EXR, TIFF)
   - Batch export with progress reporting
6. Integration:
   - Use utils.get_objects_by_scope()
   - Use auto_utils.validate_data() for settings
   - Register console shortcuts
7. Testing:
   - Syntax: python -m py_compile modules/export.py
   - Runtime: Test in Blender console
   - Integration: Export workflow with existing modules
8. Documentation:
   - Add to README.md "Adding New Features"
   - Include usage example
   - Document console shortcuts

Expected Output:
✓ Registered: export
[Console] Registered 17 shortcuts (2 new)

Success Criteria:
- Module auto-discovered and registered
- Panel visible in N-Panel
- Operators work without errors
- Console shortcuts functional
- All files compile without syntax errors
```

---

## 🎓 Conclusion

Following these rules ensures:
- ✅ **Consistent code quality**
- ✅ **Maintainable architecture**
- ✅ **Efficient collaboration**
- ✅ **Professional results**
- ✅ **Reduced debugging time**
- ✅ **Better documentation**

**Remember**: AI is a powerful tool, but clear communication and specific requests are key to success!

---

**Based on**: Ultimate Bak3 v3.2.4 Architecture  
**Last Updated**: 2025-11-29  
**Maintained by**: andiusndd
