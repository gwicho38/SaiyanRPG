#!/usr/bin/env python3
"""
Test if UI debug markers are visible without full game initialization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_markers():
    """Test UI markers without full game loop"""
    print("🖥️  Testing UI Debug Markers")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_ui import UIManager
        from saiyanquest.character_system import CharacterManager
        from saiyanquest.character_physics import CharacterType
        from saiyanquest.gta_world import GTAWorld
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("UI Markers Test")
        
        print("✅ Pygame initialized")
        
        # Create minimal objects needed for UI
        ui_manager = UIManager(800, 600)
        char_manager = CharacterManager()
        character = char_manager.create_character(CharacterType.PLAYER, 400, 300, True)
        world = GTAWorld(800, 600)
        
        print(f"✅ UI components created")
        
        # Test UI rendering with debug markers
        screen.fill((0, 0, 0))  # Black background
        
        try:
            ui_manager.render(screen, character, world, None, None, None)
            print("✅ UI Manager render completed")
        except Exception as e:
            print(f"❌ UI Manager render failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Show the result for 5 seconds to see if markers are visible
        pygame.display.flip()
        print("📺 Showing result for 5 seconds...")
        pygame.time.wait(5000)
        
        pygame.quit()
        print("✅ UI markers test completed")
        return True
        
    except Exception as e:
        print(f"❌ UI markers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_markers()
    sys.exit(0 if success else 1)