#!/usr/bin/env python3
"""
Test that characters are rendered as sprites instead of circles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_character_sprite_rendering():
    """Test character sprite rendering system"""
    print("🎮 Testing Character Sprite Rendering")
    print("=" * 50)
    
    try:
        import pygame
        from saiyanquest.character_system import Character, CharacterManager
        from saiyanquest.character_physics import CharacterType
        from saiyanquest.gta_asset_loader import get_asset_loader
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Character Sprite Test")
        
        # Get asset loader and verify it has character sprites
        asset_loader = get_asset_loader()
        print(f"Asset loader loaded {len(asset_loader.character_sprites)} character types")
        
        # Create character manager
        char_manager = CharacterManager()
        
        # Create different character types
        test_characters = [
            (CharacterType.PLAYER, 100, 100, "Player"),
            (CharacterType.CIVILIAN, 200, 100, "Civilian"),
            (CharacterType.POLICE, 300, 100, "Police"),
            (CharacterType.GANG_MEMBER, 400, 100, "Gang Member"),
            (CharacterType.PARAMEDIC, 500, 100, "Paramedic"),
            (CharacterType.BUSINESSMAN, 600, 100, "Businessman"),
        ]
        
        characters = []
        for char_type, x, y, name in test_characters:
            character = char_manager.create_character(char_type, x, y, False)
            characters.append((character, name))
            print(f"Created {name}: sprite='{character._get_sprite_name()}', direction='{character._get_sprite_direction()}'")
        
        # Test sprite retrieval
        print(f"\nSprite Asset Tests:")
        for character, name in characters:
            sprite_name = character._get_sprite_name()
            sprite_direction = character._get_sprite_direction()
            sprite = asset_loader.get_character_sprite(sprite_name, sprite_direction)
            if sprite:
                size = sprite.get_size()
                print(f"  ✓ {name}: {sprite_name}_{sprite_direction} ({size[0]}x{size[1]})")
            else:
                print(f"  ❌ {name}: {sprite_name}_{sprite_direction} - NOT FOUND")
        
        # Quick render test
        screen.fill((50, 100, 50))  # Dark green background
        
        for character, name in characters:
            character.render(screen, (0, 0))
        
        pygame.display.flip()
        pygame.time.wait(2000)  # Show for 2 seconds
        
        pygame.quit()
        print("\n✅ Character sprite rendering test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Character sprite test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_character_sprite_rendering()
    sys.exit(0 if success else 1)