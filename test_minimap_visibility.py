#!/usr/bin/env python3
"""
Test minimap visibility with enhanced debugging
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimap_visibility():
    """Test minimap visibility with debug info"""
    print("🗺️  Testing Minimap Visibility")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_ui import UIManager, UIElement
        from saiyanquest.character_system import CharacterManager
        from saiyanquest.character_physics import CharacterType
        from saiyanquest.gta_world_streamer import GTAWorldStreamer
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Minimap Visibility Test")
        
        print("✅ Pygame initialized")
        
        # Create UI and world components
        ui_manager = UIManager(800, 600)
        char_manager = CharacterManager()
        character = char_manager.create_character(CharacterType.PLAYER, 400, 300, True)
        world = GTAWorldStreamer()  # Use the actual world streamer
        
        print(f"✅ Components created")
        print(f"   Minimap visible: {ui_manager.hud.element_visibility[UIElement.MINIMAP]}")
        print(f"   World loaded chunks: {len(world.active_chunks)}")
        
        # Set character position and update world
        world.update_camera(400, 300)  # Center the camera on player
        
        # Test render with bright background to see contrast
        screen.fill((100, 50, 200))  # Purple background for contrast
        
        # Add debug markers first
        pygame.draw.rect(screen, (255, 255, 0), (0, 0, 50, 50))  # Yellow corner marker
        pygame.draw.rect(screen, (255, 0, 255), (750, 0, 50, 50))  # Magenta top-right marker
        
        # Render UI
        ui_manager.render(screen, character, world, None, None, None)
        
        # Add debug text
        font = pygame.font.Font(None, 36)
        debug_text = font.render("MINIMAP TEST - Look for white border in top-right", True, (255, 255, 255))
        screen.blit(debug_text, (10, 550))
        
        pygame.display.flip()
        
        print("📺 Rendering minimap test - showing for 5 seconds...")
        print("   Look for:")
        print("   - White bordered rectangle in top-right")
        print("   - Green squares (loaded chunks) inside minimap")
        print("   - Red dot (player position)")
        print("   - 'M' toggle indicator in corner")
        
        pygame.time.wait(5000)
        
        pygame.quit()
        print("✅ Minimap visibility test completed")
        return True
        
    except Exception as e:
        print(f"❌ Minimap visibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimap_visibility()
    sys.exit(0 if success else 1)