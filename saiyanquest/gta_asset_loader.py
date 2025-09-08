#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA Asset Loader - Loads classic GTA-style assets

import pygame
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

class GTAAssetLoader:
    """Loads and manages classic GTA-style assets"""
    
    def __init__(self, assets_path: str = "gta_classic_assets"):
        self.assets_path = Path(assets_path)
        self.vehicle_sprites = {}
        self.character_sprites = {}
        self.building_sprites = {}
        self.effect_sprites = {}
        self.urban_tileset = None
        self.manifest = {}
        
        if self.assets_path.exists():
            self._load_manifest()
            self._load_all_assets()
    
    def _load_manifest(self):
        """Load the asset manifest"""
        manifest_file = self.assets_path / "asset_manifest.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                self.manifest = json.load(f)
    
    def _load_all_assets(self):
        """Load all assets from disk"""
        print("🎨 Loading Classic GTA Assets...")
        
        # Load vehicles (4 directions each)
        vehicles_path = self.assets_path / "vehicles"
        if vehicles_path.exists():
            for vehicle_name in self.manifest.get('vehicles', []):
                self.vehicle_sprites[vehicle_name] = {}
                for direction in ['north', 'south', 'east', 'west']:
                    sprite_file = vehicles_path / f"{vehicle_name}_{direction}.png"
                    if sprite_file.exists():
                        self.vehicle_sprites[vehicle_name][direction] = pygame.image.load(str(sprite_file))
        
        # Load characters (4 directions each)
        characters_path = self.assets_path / "characters"
        if characters_path.exists():
            for char_name in self.manifest.get('characters', []):
                self.character_sprites[char_name] = {}
                for direction in ['north', 'south', 'east', 'west']:
                    sprite_file = characters_path / f"{char_name}_{direction}.png"
                    if sprite_file.exists():
                        self.character_sprites[char_name][direction] = pygame.image.load(str(sprite_file))
        
        # Load buildings
        buildings_path = self.assets_path / "buildings"
        if buildings_path.exists():
            for building_name in self.manifest.get('buildings', []):
                sprite_file = buildings_path / f"{building_name}.png"
                if sprite_file.exists():
                    self.building_sprites[building_name] = pygame.image.load(str(sprite_file))
        
        # Load effects (multiple frames each)
        effects_path = self.assets_path / "effects"
        if effects_path.exists():
            for effect_name in self.manifest.get('effects', []):
                self.effect_sprites[effect_name] = []
                frame_num = 0
                while True:
                    sprite_file = effects_path / f"{effect_name}_frame_{frame_num:02d}.png"
                    if sprite_file.exists():
                        self.effect_sprites[effect_name].append(pygame.image.load(str(sprite_file)))
                        frame_num += 1
                    else:
                        break
        
        # Load urban tileset
        tileset_file = self.assets_path / "urban_tileset.png"
        if tileset_file.exists():
            self.urban_tileset = pygame.image.load(str(tileset_file))
        
        print(f"   ✓ Loaded {len(self.vehicle_sprites)} vehicle types")
        print(f"   ✓ Loaded {len(self.character_sprites)} character types")
        print(f"   ✓ Loaded {len(self.building_sprites)} building types")
        print(f"   ✓ Loaded {len(self.effect_sprites)} effect types")
        print(f"   ✓ Loaded urban tileset: {tileset_file.exists()}")
    
    def get_vehicle_sprite(self, vehicle_type: str, direction: str) -> Optional[pygame.Surface]:
        """Get vehicle sprite for specific type and direction"""
        return self.vehicle_sprites.get(vehicle_type, {}).get(direction)
    
    def get_character_sprite(self, character_type: str, direction: str) -> Optional[pygame.Surface]:
        """Get character sprite for specific type and direction"""
        return self.character_sprites.get(character_type, {}).get(direction)
    
    def get_building_sprite(self, building_type: str) -> Optional[pygame.Surface]:
        """Get building sprite for specific type"""
        return self.building_sprites.get(building_type)
    
    def get_effect_sprites(self, effect_type: str) -> List[pygame.Surface]:
        """Get all frames for an effect animation"""
        return self.effect_sprites.get(effect_type, [])
    
    def get_random_vehicle_type(self) -> str:
        """Get a random vehicle type"""
        return random.choice(list(self.vehicle_sprites.keys()))
    
    def get_random_character_type(self) -> str:
        """Get a random character type"""
        return random.choice(list(self.character_sprites.keys()))
    
    def get_random_building_type(self) -> str:
        """Get a random building type"""
        return random.choice(list(self.building_sprites.keys()))
    
    def create_urban_entities(self, chunk_x: int, chunk_y: int, chunk_size: int = 1024) -> List[Dict]:
        """Create urban entities for a chunk using classic GTA assets"""
        entities = []
        
        # Add some buildings to urban areas
        num_buildings = random.randint(2, 8)
        for _ in range(num_buildings):
            building_type = self.get_random_building_type()
            x = chunk_x + random.randint(50, chunk_size - 100)
            y = chunk_y + random.randint(50, chunk_size - 100)
            
            entities.append({
                'type': 'building',
                'x': x,
                'y': y,
                'sprite_type': building_type,
                'sprite': self.get_building_sprite(building_type)
            })
        
        # Add some vehicles
        num_vehicles = random.randint(1, 4)
        for _ in range(num_vehicles):
            vehicle_type = self.get_random_vehicle_type()
            direction = random.choice(['north', 'south', 'east', 'west'])
            x = chunk_x + random.randint(50, chunk_size - 50)
            y = chunk_y + random.randint(50, chunk_size - 50)
            
            entities.append({
                'type': 'vehicle',
                'x': x,
                'y': y,
                'sprite_type': vehicle_type,
                'direction': direction,
                'sprite': self.get_vehicle_sprite(vehicle_type, direction)
            })
        
        # Add some pedestrians
        num_peds = random.randint(2, 6)
        for _ in range(num_peds):
            char_type = self.get_random_character_type()
            direction = random.choice(['north', 'south', 'east', 'west'])
            x = chunk_x + random.randint(20, chunk_size - 20)
            y = chunk_y + random.randint(20, chunk_size - 20)
            
            entities.append({
                'type': 'pedestrian',
                'x': x,
                'y': y,
                'sprite_type': char_type,
                'direction': direction,
                'sprite': self.get_character_sprite(char_type, direction)
            })
        
        return entities
    
    def render_urban_background(self, surface: pygame.Surface, chunk_x: int, chunk_y: int):
        """Render urban background using the tileset"""
        if not self.urban_tileset:
            # Fallback to simple urban pattern
            surface.fill((64, 64, 64))  # Asphalt
            
            # Add some basic road markings
            chunk_size = surface.get_width()
            for i in range(0, chunk_size, 64):
                for j in range(0, chunk_size, 64):
                    # Road lines
                    pygame.draw.line(surface, (255, 255, 255), 
                                   (i + 32, j), (i + 32, j + 64), 2)
                    pygame.draw.line(surface, (255, 255, 255), 
                                   (i, j + 32), (i + 64, j + 32), 2)
        else:
            # Use the actual tileset (would need tile mapping logic)
            # For now, tile the urban tileset across the chunk
            tileset_w = self.urban_tileset.get_width()
            tileset_h = self.urban_tileset.get_height()
            chunk_size = surface.get_width()
            
            for x in range(0, chunk_size, tileset_w):
                for y in range(0, chunk_size, tileset_h):
                    surface.blit(self.urban_tileset, (x, y))
    
    def get_stats(self) -> Dict:
        """Get asset loading statistics"""
        return {
            'vehicles_loaded': len(self.vehicle_sprites),
            'characters_loaded': len(self.character_sprites),
            'buildings_loaded': len(self.building_sprites),
            'effects_loaded': len(self.effect_sprites),
            'tileset_loaded': self.urban_tileset is not None,
            'total_assets': self.manifest.get('total_assets', 0)
        }

# Global asset loader instance
_asset_loader = None

def get_asset_loader() -> GTAAssetLoader:
    """Get the global asset loader instance"""
    global _asset_loader
    if _asset_loader is None:
        _asset_loader = GTAAssetLoader()
    return _asset_loader