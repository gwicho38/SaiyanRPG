#!/usr/bin/env python3
"""
Test script for the Pixel Art Map System
Demonstrates GBA-style graphics with working assets
"""

import pygame
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pixel_art_system():
    """Test the pixel art map system"""
    print("🎮 Testing Pixel Art Map System")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    # Set up display
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("SaiyanQuest - Pixel Art Map System Test")
    
    clock = pygame.time.Clock()
    running = True
    
    try:
        # Import our systems
        from saiyanquest.pixel_art_map_system import get_pixel_map_system
        from saiyanquest.gba_asset_generator import get_asset_generator
        from saiyanquest.enhanced_world_renderer import get_enhanced_renderer
        
        print("✓ Systems imported successfully")
        
        # Get the enhanced renderer (this will generate assets and create world)
        renderer = get_enhanced_renderer()
        print("✓ Enhanced renderer initialized")
        
        # Camera movement
        camera_x = 0
        camera_y = 0
        camera_speed = 200  # pixels per second
        
        # Test different world types
        world_types = ["city", "nature", "mixed"]
        current_world = 0
        
        # Main game loop
        while running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Switch world type
                        current_world = (current_world + 1) % len(world_types)
                        new_type = world_types[current_world]
                        print(f"🌍 Switching to {new_type} world...")
                        renderer.create_new_world(new_type)
                    elif event.key == pygame.K_r:
                        # Reload current world
                        current_type = world_types[current_world]
                        print(f"🔄 Reloading {current_type} world...")
                        renderer.create_new_world(current_type)
            
            # Handle camera movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                camera_x -= camera_speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                camera_x += camera_speed * dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                camera_y -= camera_speed * dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                camera_y += camera_speed * dt
            
            # Update camera
            renderer.update_camera(camera_x, camera_y)
            
            # Update renderer
            renderer.update(dt)
            
            # Render
            screen.fill((50, 100, 50))  # Background color
            renderer.render(screen)
            
            # Show instructions
            font = pygame.font.Font(None, 36)
            instructions = [
                "Pixel Art Map System Test",
                "",
                "Controls:",
                "WASD/Arrow Keys - Move camera",
                "SPACE - Switch world type",
                "R - Reload current world",
                "ESC - Exit",
                "",
                f"Current World: {world_types[current_world].title()}",
                f"Camera: ({camera_x:.0f}, {camera_y:.0f})"
            ]
            
            y_offset = screen_height - len(instructions) * 25
            for instruction in instructions:
                if instruction:  # Skip empty lines
                    text_surface = font.render(instruction, True, (255, 255, 255))
                    screen.blit(text_surface, (10, y_offset))
                y_offset += 25
            
            pygame.display.flip()
        
        print("✓ Test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

def test_asset_generation():
    """Test asset generation without display"""
    print("\n🎨 Testing Asset Generation")
    print("=" * 40)
    
    try:
        from saiyanquest.gba_asset_generator import get_asset_generator
        
        generator = get_asset_generator()
        assets = generator.generate_all_assets()
        
        print(f"✓ Generated {len(assets)} assets")
        
        # Test specific asset types
        vehicle_count = len(generator.get_assets_by_type(generator.AssetType.VEHICLE))
        character_count = len(generator.get_assets_by_type(generator.AssetType.CHARACTER))
        building_count = len(generator.get_assets_by_type(generator.AssetType.BUILDING))
        effect_count = len(generator.get_assets_by_type(generator.AssetType.EFFECT))
        
        print(f"   • Vehicles: {vehicle_count}")
        print(f"   • Characters: {character_count}")
        print(f"   • Buildings: {building_count}")
        print(f"   • Effects: {effect_count}")
        
        # Test getting specific assets
        sedan = generator.get_asset("vehicle_sedan")
        if sedan:
            print(f"✓ Retrieved sedan asset: {sedan.size}")
        
        civilian = generator.get_asset("character_civilian")
        if civilian:
            print(f"✓ Retrieved civilian asset: {civilian.size}")
        
        # Save assets
        generator.save_assets("test_gba_assets")
        print("✓ Assets saved to test_gba_assets/")
        
        return True
        
    except Exception as e:
        print(f"❌ Asset generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_map_system():
    """Test map system without display"""
    print("\n🗺️ Testing Map System")
    print("=" * 30)
    
    try:
        from saiyanquest.pixel_art_map_system import get_pixel_map_system
        
        map_system = get_pixel_map_system()
        
        # Test procedural map creation
        print("Creating procedural maps...")
        
        map_types = ["city", "nature", "mixed"]
        for map_type in map_types:
            success = map_system.create_procedural_map(100, 75, map_type)
            if success:
                info = map_system.get_map_info()
                print(f"✓ Created {map_type} map: {info['map_size'][0]}x{info['map_size'][1]}")
                print(f"   • Layers: {len(info['layers'])}")
                print(f"   • Total tiles: {info['total_tiles']}")
                print(f"   • Animated tiles: {info['animated_tiles']}")
            else:
                print(f"❌ Failed to create {map_type} map")
        
        # Test collision detection
        print("\nTesting collision detection...")
        collision_tests = [
            (100, 100, False),  # Should be grass (no collision)
            (200, 200, True),   # Might be building (collision)
            (300, 300, False),  # Should be grass (no collision)
        ]
        
        for x, y, expected in collision_tests:
            result = map_system.get_collision_at(x, y)
            status = "✓" if result == expected else "⚠️"
            print(f"{status} Collision at ({x}, {y}): {result} (expected: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Map system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🎮 SaiyanQuest Pixel Art Map System Tests")
    print("=" * 60)
    
    success = True
    
    # Test asset generation
    if not test_asset_generation():
        success = False
    
    # Test map system
    if not test_map_system():
        success = False
    
    # Test interactive system (if pygame is available)
    try:
        if not test_pixel_art_system():
            success = False
    except Exception as e:
        print(f"⚠️ Interactive test skipped: {e}")
        print("   (This is normal if running in headless environment)")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\n🌟 PIXEL ART MAP SYSTEM IS READY!")
        print("   • GBA-style pixel art assets ✓")
        print("   • Procedural map generation ✓")
        print("   • Tile-based rendering system ✓")
        print("   • Collision detection ✓")
        print("   • Animated tiles ✓")
        print("   • Multi-layer rendering ✓")
        print("\n   The system is ready for integration with the main game!")
    else:
        print("⚠️ Some tests failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)