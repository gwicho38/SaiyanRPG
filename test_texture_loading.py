#!/usr/bin/env python3
"""Test texture loading during actual gameplay simulation."""

import pygame
from saiyanquest.gta_game import GTAGameState

def test_texture_loading():
    """Test texture loading with gameplay simulation"""
    print("🎮 Starting texture loading test...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("GTA Texture Loading Test")
    clock = pygame.time.Clock()
    
    try:
        # Create game state
        print("📍 Creating GTA game state...")
        game = GTAGameState()
        
        print("🏃 Simulating player movement to trigger map loading...")
        
        # Move player around to trigger different map chunks
        positions = [
            (1000, 1000),   # Starting position
            (2000, 2000),   # Move to trigger new chunks  
            (3000, 1500),   # Another position
            (1500, 3000),   # More movement
        ]
        
        for pos in positions:
            print(f"\n🚶 Moving player to {pos}")
            game.character.position = pos
            
            # Update world streamer camera position
            game.world.camera_x = pos[0] - 400  # Center camera on player
            game.world.camera_y = pos[1] - 300
            
            # Update active chunks (this should trigger map loading)
            game.world._update_active_chunks()
            print(f"   Active chunks: {len(game.world.active_chunks)}")
            
            # Render world to trigger actual texture loading  
            print(f"   🎬 Rendering world...")
            game.world.render_world(screen)
            
            for chunk_key in game.world.active_chunks:
                if chunk_key in game.world.world_tiles:
                    world_tile = game.world.world_tiles[chunk_key]
                    print(f"   Processing chunk {chunk_key} at ({world_tile.x}, {world_tile.y})")
                    if hasattr(world_tile, 'maps') and world_tile.maps:
                        print(f"   - Maps in chunk: {world_tile.maps}")
            
            # Small delay to see output
            pygame.time.wait(500)
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        print("🏁 Test completed")

if __name__ == "__main__":
    test_texture_loading()