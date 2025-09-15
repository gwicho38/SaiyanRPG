#!/usr/bin/env python3
"""
Final verification of texture loading - check for actual runtime errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_texture_runtime():
    """Test if textures cause any runtime issues in the actual game"""
    print("🎨 Final Texture Runtime Verification")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_world_streamer import GTAWorldStreamer
        from saiyanquest.gta_asset_loader import get_asset_loader
        
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Test the main world streamer system
        print("Testing GTAWorldStreamer (main texture system)...")
        streamer = GTAWorldStreamer(800, 600)
        
        # Get world statistics
        stats = streamer.get_world_stats()
        print(f"✅ World initialized: {stats['total_maps']} maps found")
        print(f"✅ Chunks created: {stats['total_chunks']}")
        
        # Test moving camera to different areas to trigger texture loading
        test_positions = [
            (4000, 8000),   # Default spawn area
            (8000, 4000),   # Different area
            (16000, 12000), # Far area
        ]
        
        texture_errors = []
        
        for x, y in test_positions:
            print(f"\nTesting camera position ({x}, {y})...")
            try:
                streamer.update_camera(x, y)
                current_stats = streamer.get_world_stats()
                print(f"  ✅ Loaded {current_stats['loaded_chunks']} chunks")
                print(f"  ✅ Active entities: {current_stats['active_entities']}")
            except Exception as e:
                texture_errors.append(f"Camera position ({x}, {y}): {e}")
                print(f"  ❌ Error: {e}")
        
        # Test asset loader
        print(f"\nTesting GTA Classic Assets...")
        asset_loader = get_asset_loader()
        print(f"  ✅ Loaded {len(asset_loader.character_sprites)} character types")
        print(f"  ✅ Loaded {len(asset_loader.vehicle_sprites)} vehicle types")
        
        # Test a simple render to catch texture issues
        print(f"\nTesting surface rendering...")
        test_surface = pygame.Surface((400, 300))
        try:
            streamer.render_world(test_surface)
            print(f"  ✅ World rendering successful")
        except Exception as e:
            texture_errors.append(f"Surface rendering: {e}")
            print(f"  ❌ Rendering error: {e}")
        
        pygame.quit()
        
        # Summary
        print(f"\n" + "=" * 50)
        print("FINAL TEXTURE VERIFICATION RESULTS")
        print("=" * 50)
        
        if texture_errors:
            print(f"❌ Found {len(texture_errors)} runtime texture errors:")
            for error in texture_errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ NO TEXTURE RUNTIME ERRORS FOUND!")
            print("✅ All texture systems working correctly")
            print("✅ Map rendering functioning properly")
            print("✅ Asset loading successful")
            print("\n🎉 Texture system is healthy!")
            return True
        
    except Exception as e:
        print(f"❌ Texture runtime test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_texture_runtime()
    sys.exit(0 if success else 1)