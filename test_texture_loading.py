#!/usr/bin/env python3
"""
Test texture loading and identify missing or problematic textures
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logging

def test_texture_loading():
    """Test texture loading and report issues"""
    print("🎨 Testing Texture Loading System")
    print("=" * 60)
    
    # Set up logging to capture warnings and errors
    logging.basicConfig(level=logging.WARNING)
    
    try:
        import pygame
        from saiyanquest.saiyanquest_map_renderer import SaiyanQuestMapRenderer
        from pathlib import Path
        
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Create map renderer
        renderer = SaiyanQuestMapRenderer()
        
        # Test loading several different maps to check texture issues
        test_maps = [
            "cotton_town",
            "route6", 
            "mansion",
            "flower_city",
            "healing_center",
            "player_house_bedroom"
        ]
        
        texture_issues = []
        successful_maps = []
        failed_maps = []
        
        print("Testing map texture loading...")
        print("-" * 40)
        
        for map_name in test_maps:
            print(f"\n📍 Testing map: {map_name}")
            
            # Try to load the map
            tmx_map = renderer.load_map(map_name)
            if not tmx_map:
                failed_maps.append(map_name)
                print(f"   ❌ Failed to load {map_name}")
                continue
                
            successful_maps.append(map_name)
            print(f"   ✓ Loaded {map_name} ({tmx_map.width}x{tmx_map.height})")
            print(f"   📦 Tilesets: {len(tmx_map.tilesets)}")
            
            # Check each tileset for missing textures
            for i, tileset in enumerate(tmx_map.tilesets):
                print(f"      {i+1}. {tileset.name} (firstgid: {tileset.firstgid}, tiles: {tileset.tilecount})")
                
                if hasattr(tileset, 'image') and tileset.image:
                    # Check if the tileset image file exists
                    tileset_path = Path("mods/saiyanquest/gfx/tilesets") / tileset.image
                    if tileset_path.exists():
                        print(f"         Image: {tileset.image} ✅")
                    else:
                        issue = f"{map_name}: Missing tileset image '{tileset.image}'"
                        texture_issues.append(issue)
                        print(f"         Image: {tileset.image} ❌ MISSING")
                else:
                    issue = f"{map_name}: Tileset '{tileset.name}' has no image attribute"
                    texture_issues.append(issue)
                    print(f"         ⚠️  No image attribute")
            
            # Try to render the map surface to catch runtime issues
            try:
                surface = renderer.render_map_to_surface(map_name)
                if surface:
                    print(f"   🎨 Rendered successfully: {surface.get_size()}")
                else:
                    issue = f"{map_name}: Failed to render to surface"
                    texture_issues.append(issue)
                    print(f"   ❌ Failed to render surface")
            except Exception as e:
                issue = f"{map_name}: Render error - {str(e)}"
                texture_issues.append(issue)
                print(f"   ❌ Render error: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("TEXTURE LOADING ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"📊 Maps tested: {len(test_maps)}")
        print(f"✅ Successfully loaded: {len(successful_maps)}")
        print(f"❌ Failed to load: {len(failed_maps)}")
        print(f"⚠️  Texture issues found: {len(texture_issues)}")
        
        if failed_maps:
            print(f"\n❌ Failed Maps:")
            for map_name in failed_maps:
                print(f"   • {map_name}")
        
        if texture_issues:
            print(f"\n⚠️  Texture Issues:")
            for issue in texture_issues:
                print(f"   • {issue}")
        else:
            print(f"\n🎉 No texture issues found!")
        
        # Check for common missing tileset files
        print(f"\n🔍 Checking common tileset directories...")
        tileset_dir = Path("mods/saiyanquest/gfx/tilesets")
        if tileset_dir.exists():
            tileset_files = list(tileset_dir.glob("*.png"))
            print(f"   Found {len(tileset_files)} PNG tileset files")
            
            # List a few examples
            for file in sorted(tileset_files)[:5]:
                print(f"     • {file.name}")
            if len(tileset_files) > 5:
                print(f"     ... and {len(tileset_files) - 5} more")
        else:
            print(f"   ❌ Tileset directory not found: {tileset_dir}")
        
        pygame.quit()
        return len(texture_issues) == 0
        
    except Exception as e:
        print(f"❌ Texture loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_texture_loading()
    sys.exit(0 if success else 1)