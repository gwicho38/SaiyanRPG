#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Classic GTA-style Asset Generator - Creates retro game assets

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

class ClassicGTAAssetGenerator:
    """Generates classic GTA-style sprites and assets"""
    
    def __init__(self):
        pygame.init()
        
        # Asset storage
        self.vehicle_sprites = {}
        self.character_sprites = {}
        self.building_sprites = {}
        self.effects_sprites = {}
        
        # Classic GTA color palette (inspired by original)
        self.colors = {
            # Vehicles
            'car_red': (198, 54, 54),
            'car_blue': (54, 126, 198),
            'car_yellow': (230, 230, 54),
            'car_green': (54, 198, 54),
            'car_white': (230, 230, 230),
            'car_black': (40, 40, 40),
            'police_blue': (54, 54, 198),
            'taxi_yellow': (255, 255, 0),
            
            # Buildings
            'concrete': (180, 180, 180),
            'brick': (139, 69, 19),
            'glass': (173, 216, 230),
            'roof': (105, 105, 105),
            
            # Characters
            'skin': (255, 220, 177),
            'shirt_blue': (100, 149, 237),
            'pants_black': (25, 25, 25),
            'hair_brown': (101, 67, 33),
            
            # Streets
            'asphalt': (64, 64, 64),
            'sidewalk': (169, 169, 169),
            'white': (255, 255, 255),
            'grass': (34, 139, 34),
            'water': (0, 119, 190)
        }
    
    def generate_classic_vehicles(self):
        """Generate classic GTA-style vehicle sprites"""
        print("🚗 Generating classic GTA vehicle sprites...")
        
        vehicles = [
            ('sedan', 32, 16, self.colors['car_blue']),
            ('sports_car', 28, 14, self.colors['car_red']),
            ('truck', 40, 20, self.colors['car_green']),
            ('taxi', 32, 16, self.colors['taxi_yellow']),
            ('police', 32, 16, self.colors['police_blue']),
            ('ambulance', 36, 18, self.colors['car_white']),
            ('fire_truck', 44, 22, self.colors['car_red']),
            ('bus', 48, 20, self.colors['car_yellow']),
            ('motorcycle', 16, 12, self.colors['car_black']),
            ('van', 36, 18, self.colors['car_white'])
        ]
        
        for vehicle_name, width, height, base_color in vehicles:
            # Create 4 rotation sprites for each vehicle
            sprites = {}
            
            for direction in ['north', 'east', 'south', 'west']:
                sprite = self._create_vehicle_sprite(width, height, base_color, direction)
                sprites[direction] = sprite
            
            self.vehicle_sprites[vehicle_name] = sprites
            print(f"  ✓ Generated {vehicle_name}")
        
        print(f"  Created {len(self.vehicle_sprites)} vehicle types")
    
    def _create_vehicle_sprite(self, width: int, height: int, color: Tuple[int, int, int], direction: str) -> pygame.Surface:
        """Create a single vehicle sprite"""
        if direction in ['north', 'south']:
            sprite = pygame.Surface((height, width), pygame.SRCALPHA)
            w, h = height, width
        else:
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            w, h = width, height
        
        # Main body
        pygame.draw.rect(sprite, color, (2, 2, w-4, h-4))
        
        # Windshield (darker)
        windshield_color = tuple(max(0, c - 50) for c in color)
        if direction == 'north':
            pygame.draw.rect(sprite, windshield_color, (3, 3, w-6, h//3))
        elif direction == 'south':
            pygame.draw.rect(sprite, windshield_color, (3, h*2//3, w-6, h//3-3))
        elif direction == 'east':
            pygame.draw.rect(sprite, windshield_color, (w*2//3, 3, w//3-3, h-6))
        else:  # west
            pygame.draw.rect(sprite, windshield_color, (3, 3, w//3, h-6))
        
        # Outline
        pygame.draw.rect(sprite, (0, 0, 0), (0, 0, w, h), 1)
        
        return sprite
    
    def generate_classic_characters(self):
        """Generate classic top-down character sprites"""
        print("👤 Generating classic character sprites...")
        
        characters = [
            ('player', self.colors['shirt_blue']),
            ('civilian_1', self.colors['shirt_blue']),
            ('civilian_2', (160, 82, 45)),  # Brown shirt
            ('police', (25, 25, 112)),       # Navy blue
            ('gangster', (128, 0, 0)),       # Dark red
            ('medic', (255, 255, 255)),      # White
            ('businessman', (0, 0, 0)),      # Black suit
        ]
        
        for char_name, shirt_color in characters:
            # Create 4-direction sprites
            sprites = {}
            
            for direction in ['north', 'east', 'south', 'west']:
                sprite = self._create_character_sprite(shirt_color, direction)
                sprites[direction] = sprite
            
            self.character_sprites[char_name] = sprites
            print(f"  ✓ Generated {char_name}")
        
        print(f"  Created {len(self.character_sprites)} character types")
    
    def _create_character_sprite(self, shirt_color: Tuple[int, int, int], direction: str) -> pygame.Surface:
        """Create a single character sprite (12x12)"""
        sprite = pygame.Surface((12, 12), pygame.SRCALPHA)
        
        # Head (skin color)
        if direction == 'north':
            pygame.draw.circle(sprite, self.colors['skin'], (6, 3), 2)
        elif direction == 'south':
            pygame.draw.circle(sprite, self.colors['skin'], (6, 3), 2)
        else:
            pygame.draw.circle(sprite, self.colors['skin'], (6, 3), 2)
        
        # Body (shirt color)
        pygame.draw.rect(sprite, shirt_color, (4, 5, 4, 4))
        
        # Legs (pants)
        pygame.draw.rect(sprite, self.colors['pants_black'], (4, 9, 4, 2))
        
        # Simple directional indicator
        if direction == 'north':
            pygame.draw.rect(sprite, (255, 255, 255), (5, 2, 2, 1))  # Eyes
        elif direction == 'south':
            pygame.draw.rect(sprite, self.colors['hair_brown'], (5, 1, 2, 2))  # Hair
        
        return sprite
    
    def generate_urban_buildings(self):
        """Generate urban building sprites"""
        print("🏢 Generating urban building sprites...")
        
        buildings = [
            ('house_small', 32, 32, self.colors['brick']),
            ('house_large', 48, 48, self.colors['concrete']),
            ('apartment', 64, 80, self.colors['concrete']),
            ('office_building', 80, 120, self.colors['glass']),
            ('shop', 40, 32, self.colors['brick']),
            ('restaurant', 48, 40, self.colors['brick']),
            ('gas_station', 64, 48, self.colors['white']),
            ('bank', 72, 56, self.colors['concrete']),
            ('hospital', 96, 80, self.colors['white']),
            ('police_station', 80, 64, self.colors['concrete']),
        ]
        
        for building_name, width, height, base_color in buildings:
            sprite = self._create_building_sprite(width, height, base_color, building_name)
            self.building_sprites[building_name] = sprite
            print(f"  ✓ Generated {building_name}")
        
        print(f"  Created {len(self.building_sprites)} building types")
    
    def _create_building_sprite(self, width: int, height: int, base_color: Tuple[int, int, int], building_type: str) -> pygame.Surface:
        """Create a single building sprite"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Main building body
        pygame.draw.rect(sprite, base_color, (0, 0, width, height))
        
        # Add details based on building type
        if 'office' in building_type:
            # Windows in grid pattern
            for y in range(8, height-8, 12):
                for x in range(8, width-8, 10):
                    pygame.draw.rect(sprite, self.colors['glass'], (x, y, 6, 8))
        
        elif 'house' in building_type:
            # Simple windows and door
            pygame.draw.rect(sprite, (139, 69, 19), (width//2-3, height-8, 6, 8))  # Door
            pygame.draw.rect(sprite, self.colors['glass'], (6, height//2, 8, 6))  # Window
            if width > 40:
                pygame.draw.rect(sprite, self.colors['glass'], (width-14, height//2, 8, 6))  # Second window
        
        elif building_type == 'gas_station':
            # Canopy
            pygame.draw.rect(sprite, self.colors['roof'], (8, height//2, width-16, 4))
            # Pumps
            pygame.draw.rect(sprite, (255, 0, 0), (16, height//2+4, 4, 8))
            pygame.draw.rect(sprite, (255, 0, 0), (width-20, height//2+4, 4, 8))
        
        # Outline
        pygame.draw.rect(sprite, (0, 0, 0), (0, 0, width, height), 2)
        
        return sprite
    
    def generate_effects_sprites(self):
        """Generate effect sprites (explosions, muzzle flashes, etc.)"""
        print("💥 Generating effect sprites...")
        
        effects = [
            ('explosion_small', 16, 5),
            ('explosion_medium', 24, 3),
            ('explosion_large', 32, 3),
            ('muzzle_flash', 8, 2),
            ('blood_splatter', 12, 4),
            ('smoke_puff', 16, 6),
        ]
        
        for effect_name, size, frames in effects:
            sprite_frames = []
            
            for frame in range(frames):
                sprite = self._create_effect_sprite(size, effect_name, frame)
                sprite_frames.append(sprite)
            
            self.effects_sprites[effect_name] = sprite_frames
            print(f"  ✓ Generated {effect_name} ({frames} frames)")
        
        print(f"  Created {len(self.effects_sprites)} effect types")
    
    def _create_effect_sprite(self, size: int, effect_type: str, frame: int) -> pygame.Surface:
        """Create a single effect sprite frame"""
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if 'explosion' in effect_type:
            # Animated explosion
            radius = int((frame + 1) * size / 6)
            colors = [(255, 255, 0), (255, 165, 0), (255, 0, 0), (128, 0, 0)]
            
            for i, color in enumerate(colors):
                if radius - i > 0:
                    pygame.draw.circle(sprite, color, (center, center), radius - i)
        
        elif effect_type == 'muzzle_flash':
            # Simple white/yellow flash
            pygame.draw.circle(sprite, (255, 255, 255), (center, center), size//3)
            pygame.draw.circle(sprite, (255, 255, 0), (center, center), size//4)
        
        elif effect_type == 'blood_splatter':
            # Red splatters
            for _ in range(frame + 3):
                x = center + random.randint(-size//3, size//3)
                y = center + random.randint(-size//3, size//3)
                pygame.draw.circle(sprite, (139, 0, 0), (x, y), random.randint(1, 3))
        
        elif effect_type == 'smoke_puff':
            # Gray smoke
            alpha = max(50, 255 - frame * 40)
            smoke_color = (128, 128, 128, alpha)
            pygame.draw.circle(sprite, smoke_color[:3], (center, center), size//3 + frame)
        
        return sprite
    
    def create_urban_tileset(self, tile_size: int = 16) -> pygame.Surface:
        """Create a comprehensive urban tileset"""
        print("🏙️ Creating urban tileset...")
        
        # Tileset dimensions (16x16 tiles)
        tileset_width = 16 * tile_size
        tileset_height = 16 * tile_size
        tileset = pygame.Surface((tileset_width, tileset_height))
        
        tiles = [
            # Row 1: Roads
            (self.colors['asphalt'], "road_horizontal"),
            (self.colors['asphalt'], "road_vertical"),
            (self.colors['asphalt'], "road_intersection"),
            (self.colors['asphalt'], "road_corner_tl"),
            (self.colors['asphalt'], "road_corner_tr"),
            (self.colors['asphalt'], "road_corner_bl"),
            (self.colors['asphalt'], "road_corner_br"),
            (self.colors['asphalt'], "road_t_up"),
            (self.colors['asphalt'], "road_t_down"),
            (self.colors['asphalt'], "road_t_left"),
            (self.colors['asphalt'], "road_t_right"),
            (self.colors['sidewalk'], "sidewalk"),
            (self.colors['grass'], "grass"),
            (self.colors['water'], "water"),
            (self.colors['concrete'], "concrete"),
            (self.colors['brick'], "brick"),
            
            # Add more tile types...
        ]
        
        for i, (color, tile_type) in enumerate(tiles):
            if i >= 256:  # Max tiles in 16x16 grid
                break
            
            x = (i % 16) * tile_size
            y = (i // 16) * tile_size
            
            # Fill base color
            pygame.draw.rect(tileset, color, (x, y, tile_size, tile_size))
            
            # Add specific details for tile types
            if 'road' in tile_type:
                self._add_road_markings(tileset, x, y, tile_size, tile_type)
            elif tile_type == 'sidewalk':
                # Add sidewalk pattern
                for px in range(0, tile_size, 4):
                    pygame.draw.line(tileset, (150, 150, 150), 
                                   (x + px, y), (x + px, y + tile_size))
            elif tile_type == 'grass':
                # Add grass texture
                for _ in range(tile_size // 2):
                    px = random.randint(x, x + tile_size - 1)
                    py = random.randint(y, y + tile_size - 1)
                    pygame.draw.circle(tileset, (20, 100, 20), (px, py), 1)
        
        return tileset
    
    def _add_road_markings(self, surface: pygame.Surface, x: int, y: int, size: int, road_type: str):
        """Add road markings to road tiles"""
        yellow = (255, 255, 0)
        white = (255, 255, 255)
        
        if road_type == "road_horizontal":
            # Horizontal center line
            pygame.draw.line(surface, yellow, (x, y + size//2), (x + size, y + size//2))
        elif road_type == "road_vertical":
            # Vertical center line
            pygame.draw.line(surface, yellow, (x + size//2, y), (x + size//2, y + size))
        elif road_type == "road_intersection":
            # No center lines in intersection
            pass
    
    def save_all_assets(self, output_dir: str = "gta_classic_assets"):
        """Save all generated assets to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save vehicles
        vehicles_path = output_path / "vehicles"
        vehicles_path.mkdir(exist_ok=True)
        
        for vehicle_name, directions in self.vehicle_sprites.items():
            for direction, sprite in directions.items():
                filename = vehicles_path / f"{vehicle_name}_{direction}.png"
                pygame.image.save(sprite, str(filename))
        
        # Save characters
        characters_path = output_path / "characters"
        characters_path.mkdir(exist_ok=True)
        
        for char_name, directions in self.character_sprites.items():
            for direction, sprite in directions.items():
                filename = characters_path / f"{char_name}_{direction}.png"
                pygame.image.save(sprite, str(filename))
        
        # Save buildings
        buildings_path = output_path / "buildings"
        buildings_path.mkdir(exist_ok=True)
        
        for building_name, sprite in self.building_sprites.items():
            filename = buildings_path / f"{building_name}.png"
            pygame.image.save(sprite, str(filename))
        
        # Save effects
        effects_path = output_path / "effects"
        effects_path.mkdir(exist_ok=True)
        
        for effect_name, frames in self.effects_sprites.items():
            for frame_num, sprite in enumerate(frames):
                filename = effects_path / f"{effect_name}_frame_{frame_num:02d}.png"
                pygame.image.save(sprite, str(filename))
        
        # Save tileset
        tileset = self.create_urban_tileset()
        tileset_filename = output_path / "urban_tileset.png"
        pygame.image.save(tileset, str(tileset_filename))
        
        # Create asset manifest
        manifest = {
            'vehicles': list(self.vehicle_sprites.keys()),
            'characters': list(self.character_sprites.keys()),
            'buildings': list(self.building_sprites.keys()),
            'effects': list(self.effects_sprites.keys()),
            'tileset': 'urban_tileset.png',
            'generated_by': 'SaiyanQuest GTA Classic Asset Generator',
            'tile_size': 16,
            'total_assets': (
                len(self.vehicle_sprites) * 4 +  # 4 directions each
                len(self.character_sprites) * 4 +
                len(self.building_sprites) +
                sum(len(frames) for frames in self.effects_sprites.values()) + 1  # tileset
            )
        }
        
        manifest_file = output_path / "asset_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"💾 Saved all assets to {output_path}")
        print(f"   📊 Total assets generated: {manifest['total_assets']}")
    
    def generate_all_assets(self):
        """Generate all classic GTA-style assets"""
        print("🎨 Generating Classic GTA Asset Pack")
        print("=" * 50)
        
        self.generate_classic_vehicles()
        self.generate_classic_characters()
        self.generate_urban_buildings()
        self.generate_effects_sprites()
        
        print("\n✅ Asset Generation Complete!")
        return {
            'vehicles': len(self.vehicle_sprites),
            'characters': len(self.character_sprites),  
            'buildings': len(self.building_sprites),
            'effects': len(self.effects_sprites)
        }

def main():
    """Generate classic GTA assets"""
    generator = ClassicGTAAssetGenerator()
    
    # Generate all assets
    stats = generator.generate_all_assets()
    
    # Save to files
    generator.save_all_assets()
    
    print("\n🎉 Classic GTA Asset Pack Complete!")
    print(f"   🚗 Vehicles: {stats['vehicles']} types x 4 directions = {stats['vehicles'] * 4} sprites")
    print(f"   👤 Characters: {stats['characters']} types x 4 directions = {stats['characters'] * 4} sprites")  
    print(f"   🏢 Buildings: {stats['buildings']} sprites")
    print(f"   💥 Effects: {sum(len(frames) for frames in generator.effects_sprites.values())} animation frames")
    print(f"   🏙️ Complete urban tileset generated")
    
    print("\n   Assets saved to: gta_classic_assets/")
    print("   Ready to integrate with SaiyanQuest GTA world!")

if __name__ == "__main__":
    main()