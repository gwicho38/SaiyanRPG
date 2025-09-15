#!/usr/bin/env python3
"""
Debug the UI rendering to see why it's not showing up
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_rendering():
    """Test UI rendering system"""
    print("🖥️  Testing UI Rendering System")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_ui import UIManager, GTAHUD
        from saiyanquest.character_system import CharacterManager
        from saiyanquest.character_physics import CharacterType
        from saiyanquest.gta_world import GTAWorld
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("UI Debug Test")
        
        print("✅ Pygame initialized")
        
        # Create UI manager
        ui_manager = UIManager(800, 600)
        print(f"✅ UI manager created")
        print(f"   HUD visible: {ui_manager.hud.visible}")
        
        # Create character for testing
        char_manager = CharacterManager()
        character = char_manager.create_character(CharacterType.PLAYER, 400, 300, True)
        print(f"✅ Test character created: {character.name}")
        
        # Create world for testing  
        world = GTAWorld(800, 600)
        print(f"✅ Test world created")
        print(f"   World camera: ({world.camera_x}, {world.camera_y})")
        print(f"   World wanted level: {world.wanted_level}")
        
        # Test HUD rendering
        print(f"\n🎨 Testing HUD rendering...")
        screen.fill((50, 50, 50))  # Dark gray background
        
        try:
            ui_manager.hud.render(screen, character, world, None, None, None)
            print("✅ HUD render completed without errors")
        except Exception as e:
            print(f"❌ HUD render failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test full UI manager rendering
        print(f"\n🎨 Testing UI Manager rendering...")
        try:
            ui_manager.render(screen, character, world, None, None, None)
            print("✅ UI Manager render completed without errors")
        except Exception as e:
            print(f"❌ UI Manager render failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Show the result for a moment
        pygame.display.flip()
        pygame.time.wait(3000)  # Show for 3 seconds
        
        pygame.quit()
        print("\n✅ UI rendering test completed")
        return True
        
    except Exception as e:
        print(f"❌ UI rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_rendering()
    sys.exit(0 if success else 1)