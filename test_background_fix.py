#!/usr/bin/env python3
"""
Test the background fix by running game briefly and taking screenshot
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_background():
    """Quick test of background rendering"""
    print("🎮 Testing Background Fix")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.gta_game import GTAGame
        
        # Initialize and run briefly
        game = GTAGame()
        print("✅ Game initialized")
        
        # Run a few update cycles to let chunks load
        for _ in range(10):
            game._update()
            game._render()
            
        pygame.time.wait(2000)  # Show for 2 seconds
        game._cleanup()
        
        print("✅ Background test completed")
        return True
        
    except Exception as e:
        print(f"❌ Background test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_background()
    sys.exit(0 if success else 1)