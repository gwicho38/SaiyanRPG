#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA Pixel Integration - Integrates pixel art maps with GTA game

import pygame
import sys
import os
from typing import Dict, List, Tuple, Optional, Any

# Import existing GTA systems
from .gta_game import GTAGame, GTAGameState
from .gta_world_streamer import GTAWorldStreamer

# Import new pixel art systems
from .enhanced_world_renderer import get_enhanced_renderer, EnhancedWorldRenderer
from .pixel_art_map_system import get_pixel_map_system, PixelArtMapSystem
from .gba_asset_generator import get_asset_generator, GBAAssetGenerator

class GTAPixelGame(GTAGame):
    """Enhanced GTA game with pixel art maps"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        # Initialize base GTA game
        super().__init__(screen_width, screen_height)
        
        # Replace world system with enhanced renderer
        self.enhanced_renderer = get_enhanced_renderer()
        self.pixel_map_system = get_pixel_map_system()
        self.asset_generator = get_asset_generator()
        
        # Override world system
        self.game_state.world = self.enhanced_renderer
        
        # Pixel art specific settings
        self.pixel_art_mode = True
        self.show_debug_info = True
        self.current_world_type = "mixed"
        
        print("🎮 GTA Pixel Art Game initialized")
        print(f"   • Screen: {screen_width}x{screen_height}")
        print(f"   • World type: {self.current_world_type}")
        print(f"   • Pixel art mode: {self.pixel_art_mode}")
    
    def _render_world_background(self) -> None:
        """Override world rendering to use pixel art system"""
        if self.pixel_art_mode:
            # Use enhanced renderer
            self.enhanced_renderer.render(self.screen)
        else:
            # Fall back to original world rendering
            super()._render_world_background()
    
    def _handle_keydown(self, key: int) -> None:
        """Handle key press events with pixel art additions"""
        # Call parent handler first
        super()._handle_keydown(key)
        
        # Additional pixel art controls
        if key == pygame.K_p:
            # Toggle pixel art mode
            self.pixel_art_mode = not self.pixel_art_mode
            print(f"🎨 Pixel art mode: {'ON' if self.pixel_art_mode else 'OFF'}")
        
        elif key == pygame.K_t:
            # Toggle world type
            world_types = ["city", "nature", "mixed"]
            current_index = world_types.index(self.current_world_type)
            next_index = (current_index + 1) % len(world_types)
            self.current_world_type = world_types[next_index]
            
            print(f"🌍 Switching to {self.current_world_type} world...")
            self.enhanced_renderer.create_new_world(self.current_world_type)
        
        elif key == pygame.K_l:
            # Toggle layer visibility
            self._toggle_layer_visibility()
        
        elif key == pygame.K_i:
            # Show world info
            self._show_world_info()
    
    def _toggle_layer_visibility(self):
        """Toggle visibility of different rendering layers"""
        layers = ["buildings", "vehicles", "characters", "effects"]
        for layer in layers:
            current_visibility = self.enhanced_renderer.render_layers[layer].visible
            self.enhanced_renderer.set_layer_visibility(layer, not current_visibility)
            print(f"👁️ {layer} layer: {'ON' if not current_visibility else 'OFF'}")
    
    def _show_world_info(self):
        """Show detailed world information"""
        info = self.enhanced_renderer.get_world_info()
        print("\n🌍 World Information:")
        print(f"   • World loaded: {info['world_loaded']}")
        print(f"   • World type: {info['world_type']}")
        print(f"   • Camera: ({info['camera'][0]:.1f}, {info['camera'][1]:.1f})")
        print(f"   • Map size: {info['pixel_map']['map_size'][0]}x{info['pixel_map']['map_size'][1]}")
        print(f"   • Total tiles: {info['pixel_map']['total_tiles']}")
        print(f"   • Assets: {info['assets']['total_assets']}")
        print(f"     - Vehicles: {info['assets']['vehicles']}")
        print(f"     - Characters: {info['assets']['characters']}")
        print(f"     - Buildings: {info['assets']['buildings']}")
        print(f"     - Effects: {info['assets']['effects']}")
    
    def _update(self, dt: float) -> None:
        """Update game logic with pixel art enhancements"""
        # Update enhanced renderer
        self.enhanced_renderer.update(dt)
        
        # Call parent update
        super()._update(dt)
    
    def _render_debug_info(self) -> None:
        """Enhanced debug information"""
        if not self.debug_mode:
            return
        
        debug_font = pygame.font.Font(None, 24)
        y_offset = 10
        
        # Get world info
        world_info = self.enhanced_renderer.get_world_info()
        
        debug_info = [
            f"Player Pos: ({self.game_state.player_x:.1f}, {self.game_state.player_y:.1f})",
            f"Player Speed: {self.game_state.player_speed:.1f} km/h",
            f"Health: {self.game_state.player_character.health:.1f}/{self.game_state.player_character.physics.stats.max_health:.1f}",
            f"Vehicle: {'Yes' if self.game_state.current_vehicle else 'No'}",
            f"Weapon: {self.game_state.current_weapon.weapon_type.value if self.game_state.current_weapon else 'None'}",
            f"",
            f"=== PIXEL ART INFO ===",
            f"Pixel Art Mode: {'ON' if self.pixel_art_mode else 'OFF'}",
            f"World Type: {self.current_world_type.title()}",
            f"Map Size: {world_info['pixel_map']['map_size'][0]}x{world_info['pixel_map']['map_size'][1]}",
            f"Total Tiles: {world_info['pixel_map']['total_tiles']}",
            f"Visible Tiles: {world_info['pixel_map']['visible_tiles']}",
            f"Assets: {world_info['assets']['total_assets']}",
            f"",
            f"=== CONTROLS ===",
            f"P - Toggle Pixel Art Mode",
            f"T - Switch World Type",
            f"L - Toggle Layer Visibility",
            f"I - Show World Info",
        ]
        
        for info in debug_info:
            if info:  # Skip empty lines
                text = debug_font.render(info, True, (255, 255, 255))
                self.screen.blit(text, (10, y_offset))
            y_offset += 25

def create_pixel_art_gta_game() -> GTAPixelGame:
    """Create a GTA game with pixel art integration"""
    print("🎮 Creating Pixel Art GTA Game...")
    
    # Create the enhanced game
    game = GTAPixelGame()
    
    print("✓ Pixel Art GTA Game created successfully!")
    return game

def run_pixel_art_demo():
    """Run a demo of the pixel art GTA game"""
    print("🎮 SaiyanQuest Pixel Art GTA Demo")
    print("=" * 50)
    
    try:
        # Create the game
        game = create_pixel_art_gta_game()
        
        print("\n🎮 Starting Pixel Art GTA Game...")
        print("Controls:")
        print("  WASD/Arrow Keys - Move player")
        print("  F - Enter/Exit vehicle")
        print("  Space - Handbrake")
        print("  Ctrl - Fire weapon")
        print("  P - Toggle Pixel Art Mode")
        print("  T - Switch World Type")
        print("  L - Toggle Layer Visibility")
        print("  I - Show World Info")
        print("  F1 - Toggle Debug Mode")
        print("  ESC - Exit")
        
        # Run the game
        game.run()
        
        print("✓ Demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test the integration without running the full game"""
    print("🧪 Testing Pixel Art GTA Integration")
    print("=" * 40)
    
    try:
        # Test creating the enhanced game
        game = create_pixel_art_gta_game()
        
        # Test world info
        world_info = game.enhanced_renderer.get_world_info()
        print(f"✓ World loaded: {world_info['world_loaded']}")
        print(f"✓ World type: {world_info['world_type']}")
        print(f"✓ Assets generated: {world_info['assets']['total_assets']}")
        
        # Test layer visibility
        game.enhanced_renderer.set_layer_visibility("buildings", False)
        print("✓ Layer visibility control working")
        
        # Test world switching
        game.enhanced_renderer.create_new_world("city")
        print("✓ World switching working")
        
        print("✓ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run integration test
        success = test_integration()
    else:
        # Run full demo
        success = run_pixel_art_demo()
    
    sys.exit(0 if success else 1)