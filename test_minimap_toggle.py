#!/usr/bin/env python3
"""
Test minimap toggle functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimap_toggle():
    """Test minimap toggle functionality"""
    print("🗺️  Testing Minimap Toggle")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_ui import UIManager, UIElement
        from saiyanquest.character_system import CharacterManager
        from saiyanquest.character_physics import CharacterType
        from saiyanquest.gta_world import GTAWorld
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Minimap Toggle Test")
        
        print("✅ Pygame initialized")
        
        # Create UI components
        ui_manager = UIManager(800, 600)
        char_manager = CharacterManager()
        character = char_manager.create_character(CharacterType.PLAYER, 400, 300, True)
        world = GTAWorld(800, 600)
        
        print(f"✅ UI components created")
        print(f"   Initial minimap visibility: {ui_manager.hud.element_visibility[UIElement.MINIMAP]}")
        
        # Test initial render
        screen.fill((0, 50, 0))  # Dark green
        ui_manager.render(screen, character, world, None, None, None)
        pygame.display.flip()
        
        print("📺 Initial render - showing for 2 seconds...")
        pygame.time.wait(2000)
        
        # Simulate M key press to toggle minimap
        m_key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
        result = ui_manager.handle_input(m_key_event)
        print(f"✅ M key pressed, result: {result}")
        print(f"   New minimap visibility: {ui_manager.hud.element_visibility[UIElement.MINIMAP]}")
        
        # Render with toggled state
        screen.fill((0, 50, 0))
        ui_manager.render(screen, character, world, None, None, None)
        pygame.display.flip()
        
        print("📺 After toggle - showing for 2 seconds...")
        pygame.time.wait(2000)
        
        # Wait for cooldown and update
        ui_manager.update(0.3, character, world)  # Simulate 0.3 seconds passing
        
        # Toggle again
        result2 = ui_manager.handle_input(m_key_event)
        print(f"✅ M key pressed again, result: {result2}")
        print(f"   Final minimap visibility: {ui_manager.hud.element_visibility[UIElement.MINIMAP]}")
        
        # Final render
        screen.fill((0, 50, 0))
        ui_manager.render(screen, character, world, None, None, None)
        pygame.display.flip()
        
        print("📺 Final state - showing for 2 seconds...")
        pygame.time.wait(2000)
        
        pygame.quit()
        print("✅ Minimap toggle test completed")
        return True
        
    except Exception as e:
        print(f"❌ Minimap toggle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimap_toggle()
    sys.exit(0 if success else 1)