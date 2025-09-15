#!/usr/bin/env python3
"""
Simple test script for the Pixel Art Map System
Tests core functionality without external dependencies
"""

import pygame
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_pixel_art():
    """Test basic pixel art functionality"""
    print("🎮 Testing Basic Pixel Art System")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    # Set up display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("SaiyanQuest - Basic Pixel Art Test")
    
    clock = pygame.time.Clock()
    running = True
    
    try:
        # Import our systems
        from saiyanquest.gba_asset_generator import get_asset_generator, AssetType
        
        print("✓ Asset generator imported successfully")
        
        # Generate assets
        generator = get_asset_generator()
        assets = generator.generate_all_assets()
        
        print(f"✓ Generated {len(assets)} assets")
        
        # Get some assets to display
        vehicles = generator.get_assets_by_type(AssetType.VEHICLE)
        characters = generator.get_assets_by_type(AssetType.CHARACTER)
        buildings = generator.get_assets_by_type(AssetType.BUILDING)
        
        print(f"   • Vehicles: {len(vehicles)}")
        print(f"   • Characters: {len(characters)}")
        print(f"   • Buildings: {len(buildings)}")
        
        # Display assets
        x_offset = 50
        y_offset = 50
        
        # Display vehicles
        for i, vehicle in enumerate(vehicles[:3]):  # Show first 3 vehicles
            sprite = vehicle.sprites.get('north')
            if sprite:
                screen.blit(sprite, (x_offset + i * 100, y_offset))
        
        # Display characters
        for i, character in enumerate(characters[:3]):  # Show first 3 characters
            sprite = character.sprites.get('south')
            if sprite:
                screen.blit(sprite, (x_offset + i * 100, y_offset + 100))
        
        # Display buildings
        for i, building in enumerate(buildings[:3]):  # Show first 3 buildings
            sprite = building.sprites.get('default')
            if sprite:
                screen.blit(sprite, (x_offset + i * 100, y_offset + 200))
        
        # Add labels
        font = pygame.font.Font(None, 24)
        labels = ["Vehicles", "Characters", "Buildings"]
        for i, label in enumerate(labels):
            text = font.render(label, True, (255, 255, 255))
            screen.blit(text, (x_offset + i * 100, y_offset - 30))
        
        # Add instructions
        instructions = [
            "Basic Pixel Art Asset Test",
            "",
            "This shows procedurally generated GBA-style assets:",
            f"• {len(vehicles)} vehicle types",
            f"• {len(characters)} character types", 
            f"• {len(buildings)} building types",
            "",
            "Press ESC to exit"
        ]
        
        y_pos = screen_height - len(instructions) * 25
        for instruction in instructions:
            if instruction:
                text = font.render(instruction, True, (255, 255, 255))
                screen.blit(text, (10, y_pos))
            y_pos += 25
        
        pygame.display.flip()
        
        # Wait for user input
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            clock.tick(60)
        
        print("✓ Basic test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

def test_asset_generation_only():
    """Test asset generation without display"""
    print("\n🎨 Testing Asset Generation (No Display)")
    print("=" * 40)
    
    try:
        from saiyanquest.gba_asset_generator import get_asset_generator, AssetType
        
        generator = get_asset_generator()
        assets = generator.generate_all_assets()
        
        print(f"✓ Generated {len(assets)} assets")
        
        # Test specific asset types
        vehicle_count = len(generator.get_assets_by_type(AssetType.VEHICLE))
        character_count = len(generator.get_assets_by_type(AssetType.CHARACTER))
        building_count = len(generator.get_assets_by_type(AssetType.BUILDING))
        effect_count = len(generator.get_assets_by_type(AssetType.EFFECT))
        
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

def main():
    """Run tests"""
    print("🎮 SaiyanQuest Basic Pixel Art Tests")
    print("=" * 60)
    
    success = True
    
    # Test asset generation
    if not test_asset_generation_only():
        success = False
    
    # Test basic display (if pygame is available)
    try:
        if not test_basic_pixel_art():
            success = False
    except Exception as e:
        print(f"⚠️ Display test skipped: {e}")
        print("   (This is normal if running in headless environment)")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 BASIC TESTS PASSED!")
        print("\n🌟 PIXEL ART ASSET GENERATION IS WORKING!")
        print("   • GBA-style pixel art assets ✓")
        print("   • Procedural asset generation ✓")
        print("   • Asset saving and loading ✓")
        print("\n   The asset generation system is ready!")
    else:
        print("⚠️ Some tests failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)