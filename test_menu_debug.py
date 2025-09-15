#!/usr/bin/env python3
"""
Quick test of menu navigation fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_menu_navigation():
    """Test menu navigation with simplified debug output"""
    print("🎮 Testing Menu Navigation Fix")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_ui import UIManager, GTAMenu
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Menu Navigation Test")
        
        # Create UI manager (this creates the pause menu)
        ui_manager = UIManager(800, 600)
        
        # Use the existing pause menu
        test_menu = ui_manager.pause_menu
        ui_manager.current_menu = test_menu
        test_menu.show()
        
        print("Menu created with 3 options")
        print(f"Initial selection: {test_menu.get_selected_item()}")
        
        # Simulate key events
        events_to_test = [
            (pygame.K_DOWN, "DOWN"),
            (pygame.K_DOWN, "DOWN"), 
            (pygame.K_UP, "UP"),
            (pygame.K_s, "S"),
            (pygame.K_w, "W")
        ]
        
        for key, name in events_to_test:
            event = pygame.event.Event(pygame.KEYDOWN, key=key)
            action = ui_manager.handle_input(event)
            print(f"{name} key -> Action: {action}, Selection: {test_menu.get_selected_item()}")
        
        pygame.quit()
        print("\n✅ Menu navigation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Menu navigation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_menu_navigation()
    sys.exit(0 if success else 1)