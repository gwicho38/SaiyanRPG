#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GBA-Style Asset Generator - Creates pixel art assets for SaiyanQuest GTA

import pygame
import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class AssetType(Enum):
    VEHICLE = "vehicle"
    CHARACTER = "character"
    BUILDING = "building"
    EFFECT = "effect"
    TILE = "tile"

class VehicleType(Enum):
    SEDAN = "sedan"
    SPORTS_CAR = "sports_car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    POLICE = "police"
    TAXI = "taxi"

class CharacterType(Enum):
    CIVILIAN = "civilian"
    GANGSTER = "gangster"
    POLICE = "police"
    BUSINESSMAN = "businessman"
    TOURIST = "tourist"

@dataclass
class PixelAsset:
    """Represents a pixel art asset"""
    asset_type: AssetType
    name: str
    sprites: Dict[str, pygame.Surface]  # direction -> sprite
    size: Tuple[int, int]
    colors: List[Tuple[int, int, int]]
    properties: Dict[str, Any]

class GBAAssetGenerator:
    """Generates GBA-style pixel art assets"""
    
    def __init__(self):
        self.tile_size = 16
        self.scale_factor = 2
        self.generated_assets: Dict[str, PixelAsset] = {}
        
        # Color palettes for different asset types
        self.color_palettes = {
            'vehicle': {
                'primary': [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 255)],
                'secondary': [(128, 128, 128), (64, 64, 64), (192, 192, 192)],
                'accent': [(255, 255, 255), (0, 0, 0)]
            },
            'character': {
                'skin': [(255, 220, 177), (238, 203, 173), (205, 186, 150)],
                'clothes': [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (128, 0, 128)],
                'hair': [(139, 69, 19), (101, 67, 33), (255, 255, 0), (0, 0, 0)]
            },
            'building': {
                'wall': [(139, 69, 19), (160, 82, 45), (205, 133, 63), (222, 184, 135)],
                'roof': [(128, 128, 128), (64, 64, 64), (192, 192, 192)],
                'window': [(135, 206, 235), (70, 130, 180)]
            }
        }
    
    def generate_all_assets(self) -> Dict[str, PixelAsset]:
        """Generate all GBA-style assets"""
        print("🎨 Generating GBA-style Pixel Art Assets...")
        
        # Generate vehicles
        self._generate_vehicles()
        
        # Generate characters
        self._generate_characters()
        
        # Generate buildings
        self._generate_buildings()
        
        # Generate effects
        self._generate_effects()
        
        print(f"   ✓ Generated {len(self.generated_assets)} assets")
        return self.generated_assets
    
    def _generate_vehicles(self):
        """Generate vehicle sprites in 4 directions"""
        vehicle_types = [
            (VehicleType.SEDAN, (24, 16)),
            (VehicleType.SPORTS_CAR, (20, 12)),
            (VehicleType.TRUCK, (32, 20)),
            (VehicleType.MOTORCYCLE, (16, 12)),
            (VehicleType.BUS, (40, 24)),
            (VehicleType.POLICE, (24, 16)),
            (VehicleType.TAXI, (24, 16))
        ]
        
        for vehicle_type, size in vehicle_types:
            # Generate 4 directional sprites
            sprites = {}
            colors = self._get_random_colors('vehicle')
            
            for direction in ['north', 'south', 'east', 'west']:
                sprite = self._create_vehicle_sprite(vehicle_type, direction, size, colors)
                sprites[direction] = sprite
            
            asset = PixelAsset(
                asset_type=AssetType.VEHICLE,
                name=vehicle_type.value,
                sprites=sprites,
                size=size,
                colors=colors,
                properties={'vehicle_type': vehicle_type.value}
            )
            
            self.generated_assets[f"vehicle_{vehicle_type.value}"] = asset
    
    def _create_vehicle_sprite(self, vehicle_type: VehicleType, direction: str, size: Tuple[int, int], colors: List[Tuple[int, int, int]]) -> pygame.Surface:
        """Create a vehicle sprite for a specific direction"""
        width, height = size
        sprite = pygame.Surface((width, height))
        sprite.fill((0, 0, 0, 0))  # Transparent background
        
        primary_color = colors[0]
        secondary_color = colors[1]
        accent_color = colors[2]
        
        if direction == 'north':  # Facing up
            # Main body
            body_rect = pygame.Rect(2, 4, width-4, height-8)
            pygame.draw.rect(sprite, primary_color, body_rect)
            
            # Windows
            window_rect = pygame.Rect(4, 6, width-8, height-12)
            pygame.draw.rect(sprite, (135, 206, 235), window_rect)
            
            # Wheels
            pygame.draw.circle(sprite, (64, 64, 64), (6, height-2), 3)
            pygame.draw.circle(sprite, (64, 64, 64), (width-6, height-2), 3)
            
            # Headlights
            pygame.draw.circle(sprite, (255, 255, 200), (width//2, 2), 2)
            
        elif direction == 'south':  # Facing down
            # Main body
            body_rect = pygame.Rect(2, 4, width-4, height-8)
            pygame.draw.rect(sprite, primary_color, body_rect)
            
            # Windows
            window_rect = pygame.Rect(4, 6, width-8, height-12)
            pygame.draw.rect(sprite, (135, 206, 235), window_rect)
            
            # Wheels
            pygame.draw.circle(sprite, (64, 64, 64), (6, height-2), 3)
            pygame.draw.circle(sprite, (64, 64, 64), (width-6, height-2), 3)
            
            # Taillights
            pygame.draw.circle(sprite, (255, 0, 0), (width//2, height-2), 2)
            
        elif direction == 'east':  # Facing right
            # Main body
            body_rect = pygame.Rect(4, 2, width-8, height-4)
            pygame.draw.rect(sprite, primary_color, body_rect)
            
            # Windows
            window_rect = pygame.Rect(6, 4, width-12, height-8)
            pygame.draw.rect(sprite, (135, 206, 235), window_rect)
            
            # Wheels
            pygame.draw.circle(sprite, (64, 64, 64), (width-2, 6), 3)
            pygame.draw.circle(sprite, (64, 64, 64), (width-2, height-6), 3)
            
            # Headlight
            pygame.draw.circle(sprite, (255, 255, 200), (width-2, height//2), 2)
            
        else:  # west - Facing left
            # Main body
            body_rect = pygame.Rect(4, 2, width-8, height-4)
            pygame.draw.rect(sprite, primary_color, body_rect)
            
            # Windows
            window_rect = pygame.Rect(6, 4, width-12, height-8)
            pygame.draw.rect(sprite, (135, 206, 235), window_rect)
            
            # Wheels
            pygame.draw.circle(sprite, (64, 64, 64), (2, 6), 3)
            pygame.draw.circle(sprite, (64, 64, 64), (2, height-6), 3)
            
            # Headlight
            pygame.draw.circle(sprite, (255, 255, 200), (2, height//2), 2)
        
        # Add vehicle-specific details
        if vehicle_type == VehicleType.POLICE:
            # Police lights
            pygame.draw.rect(sprite, (255, 0, 0), (width//2-2, 1, 4, 2))
        elif vehicle_type == VehicleType.TAXI:
            # Taxi sign
            pygame.draw.rect(sprite, (255, 255, 0), (width//2-3, 1, 6, 2))
        
        return sprite
    
    def _generate_characters(self):
        """Generate character sprites in 4 directions"""
        character_types = [
            (CharacterType.CIVILIAN, (12, 16)),
            (CharacterType.GANGSTER, (12, 16)),
            (CharacterType.POLICE, (12, 16)),
            (CharacterType.BUSINESSMAN, (12, 16)),
            (CharacterType.TOURIST, (12, 16))
        ]
        
        for char_type, size in character_types:
            sprites = {}
            colors = self._get_random_colors('character')
            
            for direction in ['north', 'south', 'east', 'west']:
                sprite = self._create_character_sprite(char_type, direction, size, colors)
                sprites[direction] = sprite
            
            asset = PixelAsset(
                asset_type=AssetType.CHARACTER,
                name=char_type.value,
                sprites=sprites,
                size=size,
                colors=colors,
                properties={'character_type': char_type.value}
            )
            
            self.generated_assets[f"character_{char_type.value}"] = asset
    
    def _create_character_sprite(self, char_type: CharacterType, direction: str, size: Tuple[int, int], colors: List[Tuple[int, int, int]]) -> pygame.Surface:
        """Create a character sprite for a specific direction"""
        width, height = size
        sprite = pygame.Surface((width, height))
        sprite.fill((0, 0, 0, 0))  # Transparent background
        
        skin_color = colors[0]
        clothes_color = colors[1]
        hair_color = colors[2]
        
        # Head
        head_rect = pygame.Rect(width//2-2, 2, 4, 4)
        pygame.draw.rect(sprite, skin_color, head_rect)
        
        # Hair
        hair_rect = pygame.Rect(width//2-3, 1, 6, 3)
        pygame.draw.rect(sprite, hair_color, hair_rect)
        
        # Body
        body_rect = pygame.Rect(width//2-3, 6, 6, 8)
        pygame.draw.rect(sprite, clothes_color, body_rect)
        
        # Arms
        if direction in ['north', 'south']:
            # Arms at sides
            pygame.draw.rect(sprite, skin_color, (width//2-4, 7, 2, 6))
            pygame.draw.rect(sprite, skin_color, (width//2+2, 7, 2, 6))
        else:
            # Arms extended
            pygame.draw.rect(sprite, skin_color, (width//2-5, 7, 2, 6))
            pygame.draw.rect(sprite, skin_color, (width//2+3, 7, 2, 6))
        
        # Legs
        pygame.draw.rect(sprite, clothes_color, (width//2-2, 14, 2, 2))
        pygame.draw.rect(sprite, clothes_color, (width//2, 14, 2, 2))
        
        # Character-specific details
        if char_type == CharacterType.POLICE:
            # Police hat
            hat_rect = pygame.Rect(width//2-2, 0, 4, 2)
            pygame.draw.rect(sprite, (0, 0, 0), hat_rect)
        elif char_type == CharacterType.GANGSTER:
            # Gangster hat
            hat_rect = pygame.Rect(width//2-3, 0, 6, 2)
            pygame.draw.rect(sprite, (0, 0, 0), hat_rect)
        
        return sprite
    
    def _generate_buildings(self):
        """Generate building sprites"""
        building_types = [
            ("house", (32, 24)),
            ("apartment", (24, 32)),
            ("office", (40, 40)),
            ("shop", (24, 20)),
            ("warehouse", (48, 24))
        ]
        
        for building_name, size in building_types:
            colors = self._get_random_colors('building')
            sprite = self._create_building_sprite(building_name, size, colors)
            
            asset = PixelAsset(
                asset_type=AssetType.BUILDING,
                name=building_name,
                sprites={'default': sprite},  # Buildings don't have directions
                size=size,
                colors=colors,
                properties={'building_type': building_name}
            )
            
            self.generated_assets[f"building_{building_name}"] = asset
    
    def _create_building_sprite(self, building_name: str, size: Tuple[int, int], colors: List[Tuple[int, int, int]]) -> pygame.Surface:
        """Create a building sprite"""
        width, height = size
        sprite = pygame.Surface((width, height))
        sprite.fill((0, 0, 0, 0))  # Transparent background
        
        wall_color = colors[0]
        roof_color = colors[1]
        window_color = colors[2]
        
        # Main building
        building_rect = pygame.Rect(0, height//2, width, height//2)
        pygame.draw.rect(sprite, wall_color, building_rect)
        
        # Roof
        if building_name == "house":
            # Triangular roof
            roof_points = [(0, height//2), (width//2, height//4), (width, height//2)]
            pygame.draw.polygon(sprite, roof_color, roof_points)
        else:
            # Flat roof
            roof_rect = pygame.Rect(0, height//2-2, width, 2)
            pygame.draw.rect(sprite, roof_color, roof_rect)
        
        # Windows
        if building_name in ["house", "apartment", "office"]:
            window_size = 4
            for x in range(4, width-4, 8):
                for y in range(height//2+4, height-4, 8):
                    window_rect = pygame.Rect(x, y, window_size, window_size)
                    pygame.draw.rect(sprite, window_color, window_rect)
        
        # Door
        door_rect = pygame.Rect(width//2-2, height-8, 4, 8)
        pygame.draw.rect(sprite, (139, 69, 19), door_rect)
        
        return sprite
    
    def _generate_effects(self):
        """Generate effect sprites"""
        effect_types = [
            ("explosion", 8, (16, 16)),
            ("smoke", 6, (12, 12)),
            ("sparkle", 4, (8, 8)),
            ("fire", 6, (12, 16))
        ]
        
        for effect_name, frame_count, size in effect_types:
            frames = []
            for frame in range(frame_count):
                sprite = self._create_effect_sprite(effect_name, frame, frame_count, size)
                frames.append(sprite)
            
            asset = PixelAsset(
                asset_type=AssetType.EFFECT,
                name=effect_name,
                sprites={'frames': frames},
                size=size,
                colors=[(255, 0, 0), (255, 255, 0), (255, 100, 0)],
                properties={'frame_count': frame_count, 'effect_type': effect_name}
            )
            
            self.generated_assets[f"effect_{effect_name}"] = asset
    
    def _create_effect_sprite(self, effect_name: str, frame: int, total_frames: int, size: Tuple[int, int]) -> pygame.Surface:
        """Create an effect sprite frame"""
        width, height = size
        sprite = pygame.Surface((width, height))
        sprite.fill((0, 0, 0, 0))  # Transparent background
        
        if effect_name == "explosion":
            # Explosion effect
            radius = int((frame + 1) * width // total_frames)
            color_intensity = int(255 * (1 - frame / total_frames))
            color = (255, color_intensity, 0)
            
            pygame.draw.circle(sprite, color, (width//2, height//2), radius)
            
        elif effect_name == "smoke":
            # Smoke effect
            alpha = int(255 * (1 - frame / total_frames))
            color = (128, 128, 128)
            
            for i in range(3):
                x = random.randint(0, width)
                y = random.randint(0, height)
                pygame.draw.circle(sprite, color, (x, y), 2)
            
        elif effect_name == "sparkle":
            # Sparkle effect
            if frame % 2 == 0:
                pygame.draw.circle(sprite, (255, 255, 255), (width//2, height//2), 2)
                pygame.draw.circle(sprite, (255, 255, 0), (width//2, height//2), 1)
        
        elif effect_name == "fire":
            # Fire effect
            flame_height = int(height * (1 - frame / total_frames))
            colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
            
            for i, color in enumerate(colors):
                if flame_height > i * 2:
                    pygame.draw.circle(sprite, color,
                                     (width//2, height - flame_height//2 + i),
                                     flame_height//4 - i)
        
        return sprite
    
    def _get_random_colors(self, palette_type: str) -> List[Tuple[int, int, int]]:
        """Get random colors from a palette"""
        palette = self.color_palettes.get(palette_type, {})
        colors = []
        
        for color_group in palette.values():
            colors.append(random.choice(color_group))
        
        return colors
    
    def save_assets(self, output_dir: str = "gba_assets"):
        """Save generated assets to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"💾 Saving GBA assets to {output_path}")
        
        for asset_name, asset in self.generated_assets.items():
            asset_dir = output_path / asset.asset_type.value
            asset_dir.mkdir(exist_ok=True)
            
            if asset.asset_type == AssetType.EFFECT:
                # Save effect frames
                frames = asset.sprites.get('frames', [])
                for i, frame in enumerate(frames):
                    frame_file = asset_dir / f"{asset_name}_frame_{i:02d}.png"
                    pygame.image.save(frame, str(frame_file))
            else:
                # Save directional sprites
                for direction, sprite in asset.sprites.items():
                    sprite_file = asset_dir / f"{asset_name}_{direction}.png"
                    pygame.image.save(sprite, str(sprite_file))
        
        # Save asset manifest
        manifest = {
            'assets': {
                asset_name: {
                    'type': asset.asset_type.value,
                    'name': asset.name,
                    'size': asset.size,
                    'colors': asset.colors,
                    'properties': asset.properties
                }
                for asset_name, asset in self.generated_assets.items()
            }
        }
        
        import json
        manifest_file = output_path / "asset_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"   ✓ Saved {len(self.generated_assets)} assets")
    
    def get_asset(self, asset_name: str) -> Optional[PixelAsset]:
        """Get a specific asset by name"""
        return self.generated_assets.get(asset_name)
    
    def get_assets_by_type(self, asset_type: AssetType) -> List[PixelAsset]:
        """Get all assets of a specific type"""
        return [asset for asset in self.generated_assets.values() 
                if asset.asset_type == asset_type]
    
    def get_random_asset(self, asset_type: AssetType) -> Optional[PixelAsset]:
        """Get a random asset of a specific type"""
        assets = self.get_assets_by_type(asset_type)
        return random.choice(assets) if assets else None

# Global asset generator instance
_asset_generator = None

def get_asset_generator() -> GBAAssetGenerator:
    """Get the global asset generator instance"""
    global _asset_generator
    if _asset_generator is None:
        _asset_generator = GBAAssetGenerator()
    return _asset_generator