#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Memory-efficient GTA World Streamer - Loads world content on demand

import pygame
import json
import os
import glob
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import math
import random

# Import classic GTA asset loader and SaiyanQuest map renderer
from .gta_asset_loader import get_asset_loader
from .saiyanquest_map_renderer import get_saiyanquest_renderer

# For compatibility with the original GTA world system
from enum import Enum

class WantedLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4

@dataclass
class WorldTile:
    """Represents a tile chunk of the world"""
    x: int
    y: int
    size: int = 1024  # 64x64 tiles at 16px each
    maps: List[str] = None
    entities: List[Dict] = None
    loaded: bool = False
    surface: Optional[pygame.Surface] = None
    
    def __post_init__(self):
        if self.maps is None:
            self.maps = []
        if self.entities is None:
            self.entities = []

class GTAWorldStreamer:
    """Efficient world streaming system for massive GTA world"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # World configuration  
        self.world_width = 32000
        self.world_height = 24000
        self.tile_size = 16
        
        # Streaming configuration
        self.chunk_size = 1024  # 64x64 tiles per chunk
        self.chunks_x = self.world_width // self.chunk_size
        self.chunks_y = self.world_height // self.chunk_size
        
        # Current view area
        self.camera_x = 0
        self.camera_y = 0
        self.view_distance = 2048  # Load chunks within this distance
        
        # Loaded world tiles
        self.world_tiles: Dict[Tuple[int, int], WorldTile] = {}
        self.active_chunks: List[Tuple[int, int]] = []
        
        # Asset paths
        self.mod_path = Path("mods/saiyanquest")
        self.maps_path = self.mod_path / "maps"
        
        # Compatibility properties
        self.wanted_level = WantedLevel.NONE
        self.chaos_level = 0.0  # 0.0 = calm, 1.0 = chaos
        self.time_of_day = 12.0  # 0.0-24.0 hours
        self.weather = "clear"
        self.safe_houses = []
        # Import District class for compatibility
        try:
            from .gta_world import District, DistrictType
            self.districts = [
                District("Downtown", 16000, 12000, 3000, DistrictType.DOWNTOWN),
                District("Grove Street", 4000, 8000, 2000, DistrictType.RESIDENTIAL), 
                District("Vice Point", 28000, 4000, 2000, DistrictType.BEACH),
                District("Ocean Beach", 28000, 20000, 2000, DistrictType.BEACH),
                District("Little Havana", 4000, 20000, 2000, DistrictType.RESIDENTIAL)
            ]
        except ImportError:
            # Fallback to simple dicts if District class not available
            self.districts = [
                {"name": "Downtown", "x": 16000, "y": 12000, "size": 3000, "pedestrian_density": 0.8},
                {"name": "Grove Street", "x": 4000, "y": 8000, "size": 2000, "pedestrian_density": 0.6},
                {"name": "Vice Point", "x": 28000, "y": 4000, "size": 2000, "pedestrian_density": 0.4},
                {"name": "Ocean Beach", "x": 28000, "y": 20000, "size": 2000, "pedestrian_density": 0.4},
                {"name": "Little Havana", "x": 4000, "y": 20000, "size": 2000, "pedestrian_density": 0.6}
            ]
        
        # World data
        self.world_data = None
        self.maps_metadata = {}
        self.entities_data = []
        
        # Initialize
        self._discover_lightweight_assets()
    
    def _discover_lightweight_assets(self):
        """Discover TMX maps using actual map loader"""
        print("🔍 Discovering SaiyanQuest TMX maps...")
        
        # Get SaiyanQuest map renderer
        sq_renderer = get_saiyanquest_renderer()
        map_names = sq_renderer.discover_all_maps()
        
        for map_name in map_names:  # Load all available maps
            try:
                # Get actual map metadata from TMX
                metadata = sq_renderer.get_map_metadata(map_name)
                if not metadata:
                    continue
                
                # Assign position in world (can be improved with actual world layout)
                pos_x = random.randint(1000, self.world_width - metadata['pixel_width'] - 1000)
                pos_y = random.randint(1000, self.world_height - metadata['pixel_height'] - 1000)
                
                self.maps_metadata[map_name] = {
                    'path': str(self.maps_path / f"{map_name}.tmx"),
                    'position': (pos_x, pos_y),
                    'size': (metadata['pixel_width'], metadata['pixel_height']),
                    'tile_size': (metadata['width'], metadata['height']),
                    'properties': metadata.get('properties', {}),
                    'type': self._determine_map_type(map_name, metadata)
                }
                
            except Exception as e:
                continue
        
        print(f"   Found {len(self.maps_metadata)} TMX maps")
        
        # Create entities data
        self._create_entities_data()
        
        # Organize maps into chunks
        self._organize_maps_into_chunks()
    
    def _determine_map_type(self, map_name: str, metadata: dict) -> str:
        """Determine map type based on name and TMX properties"""
        properties = metadata.get('properties', {})
        
        # Check TMX properties first
        if 'map_type' in properties:
            return properties['map_type']
        
        # Fallback to name-based detection
        name_lower = map_name.lower()
        if any(word in name_lower for word in ['town', 'city', 'street']):
            return 'town'
        elif any(word in name_lower for word in ['route', 'road', 'path']):
            return 'route'  
        elif any(word in name_lower for word in ['house', 'home', 'building']):
            return 'indoor'
        elif any(word in name_lower for word in ['cave', 'dungeon']):
            return 'cave'
        elif any(word in name_lower for word in ['beach', 'ocean', 'water']):
            return 'beach'
        else:
            return 'outdoor'
    
    def _guess_map_type(self, map_name: str) -> str:
        """Guess map type from name"""
        name_lower = map_name.lower()
        
        if 'house' in name_lower or 'bedroom' in name_lower:
            return 'indoor'
        elif 'city' in name_lower or 'town' in name_lower:
            return 'city'
        elif 'route' in name_lower:
            return 'route'
        elif 'cave' in name_lower or 'tunnel' in name_lower:
            return 'underground'
        else:
            return 'outdoor'
    
    def _create_entities_data(self):
        """Create lightweight entity data"""
        # Generate entities without loading sprites
        entity_types = ['npc', 'vehicle', 'monster', 'item']
        
        for i in range(500):  # 500 entities across the world
            entity_type = random.choice(entity_types)
            
            self.entities_data.append({
                'id': f"{entity_type}_{i}",
                'type': entity_type,
                'position': (
                    random.randint(100, self.world_width - 100),
                    random.randint(100, self.world_height - 100)
                ),
                'sprite_name': f"{entity_type}_{random.randint(1, 50)}",
                'active': False  # Only activate when in view
            })
    
    def _organize_maps_into_chunks(self):
        """Organize maps into world chunks"""
        print("🗺️ Organizing maps into chunks...")
        
        for map_name, map_data in self.maps_metadata.items():
            pos_x, pos_y = map_data['position']
            
            # Determine which chunk this map belongs to
            chunk_x = pos_x // self.chunk_size
            chunk_y = pos_y // self.chunk_size
            
            # Create chunk if it doesn't exist
            chunk_key = (chunk_x, chunk_y)
            if chunk_key not in self.world_tiles:
                self.world_tiles[chunk_key] = WorldTile(
                    x=chunk_x * self.chunk_size,
                    y=chunk_y * self.chunk_size,
                    size=self.chunk_size
                )
            
            # Add map to chunk
            self.world_tiles[chunk_key].maps.append(map_name)
        
        # Add entities to chunks
        for entity in self.entities_data:
            pos_x, pos_y = entity['position']
            chunk_x = pos_x // self.chunk_size
            chunk_y = pos_y // self.chunk_size
            
            chunk_key = (chunk_x, chunk_y)
            if chunk_key in self.world_tiles:
                self.world_tiles[chunk_key].entities.append(entity)
        
        print(f"   Created {len(self.world_tiles)} world chunks")
    
    def update_camera(self, player_x: float, player_y: float):
        """Update camera and stream world content"""
        self.camera_x = player_x - self.screen_width // 2
        self.camera_y = player_y - self.screen_height // 2
        
        # Keep camera in bounds
        self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, self.world_height - self.screen_height))
        
        # Update active chunks based on camera position
        self._update_active_chunks()
    
    def _update_active_chunks(self):
        """Update which chunks should be loaded based on camera position"""
        # Calculate view center
        view_center_x = self.camera_x + self.screen_width // 2
        view_center_y = self.camera_y + self.screen_height // 2
        
        # Find chunks within view distance
        new_active_chunks = []
        
        for chunk_key, world_tile in self.world_tiles.items():
            # Calculate distance from view center to chunk center
            chunk_center_x = world_tile.x + self.chunk_size // 2
            chunk_center_y = world_tile.y + self.chunk_size // 2
            
            distance = math.sqrt(
                (view_center_x - chunk_center_x)**2 +
                (view_center_y - chunk_center_y)**2
            )
            
            if distance <= self.view_distance:
                new_active_chunks.append(chunk_key)
                
                # Load chunk if not already loaded
                if not world_tile.loaded:
                    self._load_chunk(world_tile)
        
        # Unload chunks that are too far
        for chunk_key in self.active_chunks:
            if chunk_key not in new_active_chunks:
                if chunk_key in self.world_tiles:
                    self._unload_chunk(self.world_tiles[chunk_key])
        
        self.active_chunks = new_active_chunks
    
    def _load_chunk(self, world_tile: WorldTile):
        """Load a world chunk with classic GTA assets"""
        if world_tile.loaded:
            return
        
        # Create chunk surface
        world_tile.surface = pygame.Surface((self.chunk_size, self.chunk_size))
        
        # Get asset loader for classic GTA assets
        asset_loader = get_asset_loader()
        
        # Determine chunk type (urban/rural) based on position
        chunk_center_x = world_tile.x + self.chunk_size // 2
        chunk_center_y = world_tile.y + self.chunk_size // 2
        is_urban = self._is_urban_area(chunk_center_x, chunk_center_y)
        
        if is_urban:
            # Urban area - use classic GTA urban background
            asset_loader.render_urban_background(world_tile.surface, world_tile.x, world_tile.y)
            
            # Add classic GTA urban entities
            classic_entities = asset_loader.create_urban_entities(
                world_tile.x, world_tile.y, self.chunk_size
            )
            world_tile.entities.extend(classic_entities)
        else:
            # Rural/suburban area - use SaiyanQuest background with some urban elements
            base_colors = [
                (34, 139, 34),   # Forest green
                (139, 69, 19),   # Saddle brown
                (194, 178, 128), # Sandy brown
            ]
            base_color = random.choice(base_colors)
            world_tile.surface.fill(base_color)
            
            # Add some scattered classic buildings
            if random.random() < 0.3:  # 30% chance of buildings in rural areas
                rural_entities = asset_loader.create_urban_entities(
                    world_tile.x, world_tile.y, self.chunk_size
                )
                # Reduce density for rural areas
                world_tile.entities.extend(rural_entities[:len(rural_entities)//3])
        
        # Draw roads across the chunk
        self._draw_chunk_roads(world_tile)
        
        # Draw SaiyanQuest map placeholders
        for map_name in world_tile.maps:
            if map_name in self.maps_metadata:
                self._draw_actual_tmx_map(world_tile, map_name)
        
        # Activate entities in this chunk
        for entity in world_tile.entities:
            entity['active'] = True
        
        world_tile.loaded = True
    
    def _is_urban_area(self, x: int, y: int) -> bool:
        """Determine if a coordinate is in an urban area (more classic GTA assets)"""
        # Create urban areas in the central parts of the world
        center_x = self.world_width // 2
        center_y = self.world_height // 2
        
        # Distance from world center
        dist_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        
        # Urban if within 8km of center, or near specific districts
        if dist_from_center < 8000:  # Central urban area
            return True
        
        # Additional urban pockets (inspired by GTA districts)
        urban_districts = [
            (4000, 4000),    # Northwest district
            (28000, 4000),   # Northeast district  
            (4000, 20000),   # Southwest district
            (28000, 20000),  # Southeast district
            (16000, 12000),  # Central downtown
        ]
        
        for district_x, district_y in urban_districts:
            dist_to_district = ((x - district_x) ** 2 + (y - district_y) ** 2) ** 0.5
            if dist_to_district < 3000:  # 3km radius urban districts
                return True
        
        return False
    
    def _unload_chunk(self, world_tile: WorldTile):
        """Unload a world chunk to save memory"""
        if not world_tile.loaded:
            return
        
        # Free surface memory
        world_tile.surface = None
        
        # Deactivate entities
        for entity in world_tile.entities:
            entity['active'] = False
        
        world_tile.loaded = False
    
    def _draw_chunk_roads(self, world_tile: WorldTile):
        """Draw roads on chunk surface"""
        road_color = (64, 64, 64)
        
        # Draw some random roads
        for _ in range(2):
            if random.random() > 0.5:
                # Horizontal road
                y = random.randint(100, self.chunk_size - 100)
                pygame.draw.rect(world_tile.surface, road_color,
                               (0, y - 20, self.chunk_size, 40))
            else:
                # Vertical road
                x = random.randint(100, self.chunk_size - 100)
                pygame.draw.rect(world_tile.surface, road_color,
                               (x - 20, 0, 40, self.chunk_size))
    
    def _draw_actual_tmx_map(self, world_tile: WorldTile, map_name: str):
        """Draw actual TMX map using SaiyanQuest's rendering system"""
        map_data = self.maps_metadata[map_name]
        
        # Calculate relative position within chunk
        map_x = map_data['position'][0] - world_tile.x
        map_y = map_data['position'][1] - world_tile.y
        
        # Only draw if within chunk bounds
        if (0 <= map_x < self.chunk_size and 0 <= map_y < self.chunk_size and
            map_x + map_data['size'][0] > 0 and map_y + map_data['size'][1] > 0):
            
            print(f"🎮 Drawing TMX map in chunk: {map_name} at ({map_x}, {map_y})")
            
            # Get SaiyanQuest renderer and render the map
            sq_renderer = get_saiyanquest_renderer()
            rendered_map = sq_renderer.render_map_to_surface(map_name)
            
            if rendered_map:
                print(f"   ✓ Rendered surface: {rendered_map.get_size()}")
                # Calculate clipping region for the chunk
                src_x = max(0, world_tile.x - map_data['position'][0])
                src_y = max(0, world_tile.y - map_data['position'][1])
                
                dst_x = max(0, map_x)
                dst_y = max(0, map_y)
                
                # Size of region to copy
                copy_width = min(
                    map_data['size'][0] - src_x,
                    self.chunk_size - dst_x,
                    rendered_map.get_width() - src_x
                )
                copy_height = min(
                    map_data['size'][1] - src_y, 
                    self.chunk_size - dst_y,
                    rendered_map.get_height() - src_y
                )
                
                if copy_width > 0 and copy_height > 0:
                    # Create source rect for the portion of the map to copy
                    src_rect = pygame.Rect(src_x, src_y, copy_width, copy_height)
                    
                    # Blit the map portion onto the chunk surface
                    world_tile.surface.blit(rendered_map, (dst_x, dst_y), src_rect)
                    
                    # Extract and store collision data
                    self._extract_map_collisions(world_tile, map_name, dst_x, dst_y)
    
    def _extract_map_collisions(self, world_tile: WorldTile, map_name: str, offset_x: int, offset_y: int):
        """Extract collision data from TMX map and add to chunk"""
        sq_renderer = get_saiyanquest_renderer()
        collisions = sq_renderer.get_map_collisions(map_name)
        
        for collision_rect in collisions:
            # Adjust collision position relative to chunk
            adjusted_rect = pygame.Rect(
                collision_rect.x + offset_x,
                collision_rect.y + offset_y,
                collision_rect.width,
                collision_rect.height
            )
            
            # Store collision data with the world tile
            if not hasattr(world_tile, 'collisions'):
                world_tile.collisions = []
            world_tile.collisions.append(adjusted_rect)
    
    def render_world(self, surface: pygame.Surface):
        """Render visible chunks to the screen"""
        # Clear screen
        surface.fill((25, 25, 112))  # Midnight blue (for unloaded areas)
        
        # Render active chunks
        for chunk_key in self.active_chunks:
            if chunk_key in self.world_tiles:
                world_tile = self.world_tiles[chunk_key]
                
                if world_tile.loaded and world_tile.surface:
                    # Calculate screen position
                    screen_x = world_tile.x - self.camera_x
                    screen_y = world_tile.y - self.camera_y
                    
                    # Only draw if visible on screen
                    if (-self.chunk_size <= screen_x <= self.screen_width and
                        -self.chunk_size <= screen_y <= self.screen_height):
                        
                        surface.blit(world_tile.surface, (screen_x, screen_y))
        
        # Render active entities
        self._render_entities(surface)
    
    def _render_entities(self, surface: pygame.Surface):
        """Render active entities including classic GTA assets"""
        entity_colors = {
            'npc': (255, 255, 0),     # Yellow
            'vehicle': (0, 0, 255),   # Blue
            'monster': (255, 0, 0),   # Red
            'item': (0, 255, 0),      # Green
        }
        
        rendered_count = 0
        
        # Render original SaiyanQuest entities
        for entity in self.entities_data:
            if entity.get('active', False):
                pos_x, pos_y = entity['position']
                
                # Convert to screen coordinates
                screen_x = pos_x - self.camera_x
                screen_y = pos_y - self.camera_y
                
                # Only render if on screen
                if 0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height:
                    color = entity_colors.get(entity['type'], (128, 128, 128))
                    pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 6)
                    rendered_count += 1
        
        # Render classic GTA entities from loaded chunks
        for chunk_key in self.active_chunks:
            if chunk_key in self.world_tiles:
                world_tile = self.world_tiles[chunk_key]
                
                if world_tile.loaded:
                    for entity in world_tile.entities:
                        if entity.get('active', False) and 'sprite' in entity:
                            # Convert to screen coordinates
                            screen_x = entity['x'] - self.camera_x
                            screen_y = entity['y'] - self.camera_y
                            
                            # Only render if on screen
                            if (-50 <= screen_x <= self.screen_width + 50 and
                                -50 <= screen_y <= self.screen_height + 50):
                                
                                sprite = entity['sprite']
                                if sprite:
                                    # Center sprite on position
                                    sprite_rect = sprite.get_rect()
                                    sprite_rect.center = (int(screen_x), int(screen_y))
                                    surface.blit(sprite, sprite_rect)
                                    rendered_count += 1
                                else:
                                    # Fallback to colored circle
                                    fallback_colors = {
                                        'building': (139, 69, 19),    # Brown
                                        'vehicle': (200, 200, 200),   # Light gray
                                        'pedestrian': (255, 220, 177) # Skin tone
                                    }
                                    color = fallback_colors.get(entity['type'], (128, 128, 128))
                                    pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 8)
                                    rendered_count += 1
        
        return rendered_count
    
    def render_minimap(self, surface: pygame.Surface, player_x: float, player_y: float, minimap_size: int = 200):
        """Render minimap showing chunk loading"""
        minimap_rect = pygame.Rect(surface.get_width() - minimap_size - 20, 20,
                                 minimap_size, minimap_size)
        
        # Draw minimap background
        pygame.draw.rect(surface, (0, 0, 0, 128), minimap_rect)
        pygame.draw.rect(surface, (255, 255, 255), minimap_rect, 2)
        
        # Calculate scale
        scale_x = minimap_size / self.world_width
        scale_y = minimap_size / self.world_height
        
        # Draw loaded chunks
        for chunk_key, world_tile in self.world_tiles.items():
            chunk_x = minimap_rect.x + int(world_tile.x * scale_x)
            chunk_y = minimap_rect.y + int(world_tile.y * scale_y)
            chunk_w = max(1, int(self.chunk_size * scale_x))
            chunk_h = max(1, int(self.chunk_size * scale_y))
            
            # Color based on load status
            if world_tile.loaded:
                color = (0, 255, 0)  # Green for loaded
            else:
                color = (64, 64, 64)  # Gray for unloaded
            
            pygame.draw.rect(surface, color, (chunk_x, chunk_y, chunk_w, chunk_h))
        
        # Draw player position
        player_mini_x = minimap_rect.x + int(player_x * scale_x)
        player_mini_y = minimap_rect.y + int(player_y * scale_y)
        pygame.draw.circle(surface, (255, 0, 0), (player_mini_x, player_mini_y), 3)
    
    def get_spawn_points(self) -> List[Tuple[float, float]]:
        """Get player spawn points"""
        spawn_points = []
        
        # Find house maps for spawning
        for map_name, map_data in self.maps_metadata.items():
            if 'house' in map_name.lower():
                pos = map_data['position']
                spawn_points.append((pos[0] + 50, pos[1] + 50))
        
        # Default spawn points if none found
        if not spawn_points:
            spawn_points = [
                (4000, 8000),   # Grove Street area
                (12000, 8000),  # Downtown
                (20000, 4000),  # Beach
            ]
        
        return spawn_points[:10]  # Limit to 10 spawn points
    
    def get_world_stats(self) -> Dict[str, Any]:
        """Get world statistics"""
        active_entities = sum(1 for e in self.entities_data if e.get('active', False))
        loaded_chunks = sum(1 for t in self.world_tiles.values() if t.loaded)
        
        return {
            'world_size': (self.world_width, self.world_height),
            'total_chunks': len(self.world_tiles),
            'loaded_chunks': loaded_chunks,
            'active_chunks': len(self.active_chunks),
            'total_entities': len(self.entities_data),
            'active_entities': active_entities,
            'total_maps': len(self.maps_metadata),
            'chunk_size': self.chunk_size
        }
    
    def is_collision(self, x: float, y: float) -> bool:
        """Simple collision detection"""
        # For now, just return False - could be enhanced with proper collision
        return False
    
    def save_world_data(self, filename: str = "gta_world_streamer.json"):
        """Save world data"""
        world_data = {
            'world_size': (self.world_width, self.world_height),
            'chunk_size': self.chunk_size,
            'maps': self.maps_metadata,
            'entities_count': len(self.entities_data),
            'chunks_count': len(self.world_tiles),
            'spawn_points': self.get_spawn_points()
        }
        
        with open(filename, 'w') as f:
            json.dump(world_data, f, indent=2)
        
        print(f"💾 Saved world streamer data to {filename}")
    
    def get_current_district(self, x: float, y: float):
        """Get the current district object for compatibility"""
        # Find the closest district
        closest_district = None
        min_distance = float('inf')
        
        for district in self.districts:
            if hasattr(district, 'x') and hasattr(district, 'y'):
                # District object
                dist_x = x - district.x
                dist_y = y - district.y
                distance = (dist_x ** 2 + dist_y ** 2) ** 0.5
            elif isinstance(district, dict):
                # District dict
                dist_x = x - district['x']
                dist_y = y - district['y']
                distance = (dist_x ** 2 + dist_y ** 2) ** 0.5
            else:
                continue  # Skip invalid district
            
            if distance < min_distance:
                min_distance = distance
                closest_district = district
        
        return closest_district if closest_district else self.districts[0]