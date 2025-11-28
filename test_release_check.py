"""
Test script to verify release checking logic
Run this in Blender Python console to test
"""

# Test the operator logic
def test_check_update():
    print("\n" + "="*80)
    print("TEST: Check Latest Release")
    print("="*80)
    
    try:
        # Import updater
        from addon_updater_ops import updater
        
        print(f"Current version: {updater.current_version}")
        print(f"Use releases: {updater.use_releases}")
        print(f"Repository: {updater.user}/{updater.repo}")
        
        # Reset state
        updater._update_ready = None
        updater._update_version = None
        updater._update_link = None
        print("\n✓ State reset")
        
        # Check for updates
        print("\nChecking for updates from GitHub...")
        update_ready, version, link = updater.check_for_update(now=True)
        
        print(f"\nResults:")
        print(f"  - Update ready: {update_ready}")
        print(f"  - Latest version: {version}")
        print(f"  - Tag latest: {updater.tag_latest}")
        print(f"  - Download link: {link}")
        
        if update_ready:
            release_name = updater.tag_latest if updater.tag_latest else "Unknown"
            print(f"\n✓ UPDATE AVAILABLE: {release_name}")
        else:
            print(f"\n✓ UP TO DATE")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*80 + "\n")

if __name__ == "__main__":
    test_check_update()
