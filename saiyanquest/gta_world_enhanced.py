#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced GTA World System with Real SaiyanQuest Assets

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pyscroll
import pytmx
from pathlib import Path

from .gta_world import WantedLevel, DistrictType  # Import from original
from .gta_world_builder import GTAWorldBuilder, MapData, SpriteAsset, WorldSector

class GTAWorldEnhanced:
    """Enhanced GTA world system using real SaiyanQuest maps and sprites"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Import from original world system
        self.wanted_level = WantedLevel.NONE
        self.districts = {}
        self.safe_houses = []
        
        # New enhanced features
        self.world_builder = None
        self.world_data = None
        self.composite_surface = None
        self.entities = []  # NPCs, vehicles, monsters from sprites
        
        # World rendering
        self.camera_x = 0
        self.camera_y = 0
        self.render_distance = 2000  # Only render within this distance
        
        # Map data
        self.world_width = 32000
        self.world_height = 24000
        self.tile_size = 16
        
        # Time and weather (keep from original)
        self.time_of_day = 12.0  # 24-hour format
        self.weather = "clear"
        self.temperature = 72.0
        
        # Initialize world
        self._initialize_enhanced_world()
    
    def _initialize_enhanced_world(self):
        """Initialize the enhanced world with SaiyanQuest assets"""
        print("🌍 Initializing Enhanced GTA World...")
        
        # Check if we have pre-built world data
        world_data_file = "gta_world_data.json"
        
        if os.path.exists(world_data_file):
            print("📄 Loading pre-built world data...")
            self._load_world_data(world_data_file)
        else:
            print("🏗️ Building new world from SaiyanQuest assets...")
            self._build_new_world()
    
    def _load_world_data(self, filename: str):
        """Load pre-built world data"""
        try:
            with open(filename, 'r') as f:
                self.world_data = json.load(f)
            
            self.world_width, self.world_height = self.world_data['world_size']
            self.tile_size = self.world_data['tile_size']
            
            # Convert world data to districts (compatibility with original system)
            self._convert_world_data_to_districts()
            
            print(f"  ✅ Loaded world: {len(self.world_data['maps'])} maps")
            
        except Exception as e:
            print(f"  ⚠️ Failed to load world data: {e}")
            self._build_new_world()
    
    def _build_new_world(self):
        """Build new world using the world builder"""
        try:
            # Initialize pygame for world building
            pygame.init()
            temp_screen = pygame.display.set_mode((800, 600))
            
            # Create and run world builder
            self.world_builder = GTAWorldBuilder()
            self.world_builder.discover_all_assets()
            self.world_builder.build_open_world_layout()
            
            # Get composite map and entities
            self.composite_surface = self.world_builder.create_composite_world_map(temp_screen)
            self.entities = self.world_builder.populate_world_with_sprites()
            
            # Generate collision data
            self.world_builder.generate_collision_map()
            
            # Save for future use
            self.world_builder.save_world_data()
            
            # Extract world data
            self.world_width = self.world_builder.world_width
            self.world_height = self.world_builder.world_height
            
            # Convert to districts
            self._convert_builder_data_to_districts()
            
            print(f"  ✅ Built new world: {len(self.world_builder.maps)} maps")
            
        except Exception as e:
            print(f"  ⚠️ Failed to build new world: {e}")
            self._create_fallback_world()
    
    def _convert_world_data_to_districts(self):
        """Convert loaded world data to district format for compatibility"""
        if not self.world_data:
            return
        
        # Group maps by district for compatibility with original system
        district_map = {}
        for map_name, map_info in self.world_data['maps'].items():
            district = map_info.get('district', 'central')
            if district not in district_map:
                district_map[district] = []
            district_map[district].append({
                'name': map_name,
                'position': map_info['position'],
                'size': map_info['size'],
                'type': map_info['type']
            })
        
        # Create district objects (simplified for compatibility)
        for district_name, maps in district_map.items():
            self.districts[district_name] = {
                'name': district_name,
                'maps': maps,
                'bounds': self._calculate_district_bounds(maps),
                'type': self._map_district_type(district_name)
            }
    
    def _convert_builder_data_to_districts(self):
        """Convert world builder data to district format"""
        if not self.world_builder:
            return
        
        # Convert sectors to districts
        for sector, maps in self.world_builder.sectors.items():
            if maps:
                district_maps = []
                for map_data in maps:
                    district_maps.append({
                        'name': map_data.name,
                        'position': map_data.position,
                        'size': map_data.size,
                        'type': map_data.map_type
                    })
                
                self.districts[sector.value] = {
                    'name': sector.value,
                    'maps': district_maps,
                    'bounds': self._calculate_district_bounds(district_maps),
                    'type': self._map_district_type(sector.value)
                }
    
    def _calculate_district_bounds(self, maps: List[Dict]) -> pygame.Rect:
        """Calculate bounding rectangle for district maps"""
        if not maps:
            return pygame.Rect(0, 0, 1000, 1000)
        
        min_x = min(m['position'][0] for m in maps)
        min_y = min(m['position'][1] for m in maps)
        max_x = max(m['position'][0] + m['size'][0] for m in maps)
        max_y = max(m['position'][1] + m['size'][1] for m in maps)
        
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def _map_district_type(self, district_name: str) -> DistrictType:
        """Map district name to DistrictType enum"""
        mapping = {
            'downtown': DistrictType.DOWNTOWN,
            'grove_street': DistrictType.RESIDENTIAL,
            'industrial': DistrictType.INDUSTRIAL,
            'beach': DistrictType.BEACH,
            'mountains': DistrictType.HILLS,
            'islands': DistrictType.DOCKS,
            'countryside': DistrictType.RESIDENTIAL,
            'desert': DistrictType.INDUSTRIAL,
            'underground': DistrictType.INDUSTRIAL
        }
        return mapping.get(district_name, DistrictType.DOWNTOWN)
    
    def _create_fallback_world(self):
        """Create a simple fallback world if building fails"""
        print("  🏗️ Creating fallback world...")
        
        # Create basic districts
        district_info = [
            ("downtown", (12000, 8000), (4000, 4000)),
            ("grove_street", (4000, 10000), (3000, 3000)),
            ("beach", (20000, 4000), (8000, 6000)),
            ("industrial", (8000, 2000), (6000, 4000)),
        ]
        
        for name, pos, size in district_info:
            self.districts[name] = {
                'name': name,
                'maps': [],
                'bounds': pygame.Rect(pos[0], pos[1], size[0], size[1]),
                'type': self._map_district_type(name)
            }
    
    def update_camera(self, player_x: float, player_y: float):
        """Update camera position to follow player"""
        self.camera_x = player_x - self.screen_width // 2
        self.camera_y = player_y - self.screen_height // 2
        
        # Keep camera in world bounds
        self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, self.world_height - self.screen_height))
    
    def render_world(self, surface: pygame.Surface, player_x: float, player_y: float):
        """Render the visible portion of the world"""
        if self.composite_surface:
            # Render from composite surface
            source_rect = pygame.Rect(
                int(self.camera_x), 
                int(self.camera_y),
                self.screen_width, 
                self.screen_height
            )
            
            # Ensure source rect is within bounds
            source_rect.clamp_ip(pygame.Rect(0, 0, self.world_width, self.world_height))
            
            surface.blit(self.composite_surface, (0, 0), source_rect)
        else:
            # Fallback rendering
            self._render_fallback_world(surface)
        
        # Render entities within view distance
        self._render_entities(surface)
    
    def _render_fallback_world(self, surface: pygame.Surface):
        """Render a simple fallback world"""
        # Fill with grass color
        surface.fill((34, 139, 34))
        
        # Render district boundaries
        for district_name, district in self.districts.items():
            bounds = district['bounds']
            
            # Convert world coordinates to screen coordinates
            screen_rect = pygame.Rect(
                bounds.x - int(self.camera_x),
                bounds.y - int(self.camera_y),
                bounds.width,
                bounds.height
            )
            
            # Only render if visible
            if screen_rect.colliderect(pygame.Rect(0, 0, self.screen_width, self.screen_height)):
                # Different colors for different district types
                colors = {
                    DistrictType.DOWNTOWN: (100, 100, 100),
                    DistrictType.RESIDENTIAL: (60, 120, 60),
                    DistrictType.INDUSTRIAL: (120, 80, 40),
                    DistrictType.BEACH: (194, 178, 128),
                    DistrictType.HILLS: (139, 69, 19),
                }
                
                color = colors.get(district['type'], (100, 100, 100))
                pygame.draw.rect(surface, color, screen_rect)
                pygame.draw.rect(surface, (255, 255, 255), screen_rect, 2)
    
    def _render_entities(self, surface: pygame.Surface):
        """Render NPCs, vehicles, and other entities"""
        if not self.entities:
            return
        
        # Only render entities within view distance
        for entity in self.entities:
            entity_x, entity_y = entity['position']
            
            # Check if entity is within render distance
            distance = ((entity_x - (self.camera_x + self.screen_width//2))**2 + 
                       (entity_y - (self.camera_y + self.screen_height//2))**2)**0.5
            
            if distance <= self.render_distance:
                # Convert to screen coordinates
                screen_x = entity_x - self.camera_x
                screen_y = entity_y - self.camera_y
                
                # Only render if on screen
                if 0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height:
                    self._render_entity(surface, entity, screen_x, screen_y)
    
    def _render_entity(self, surface: pygame.Surface, entity: Dict, screen_x: float, screen_y: float):
        """Render a single entity (NPC, vehicle, monster)"""
        entity_type = entity.get('type', 'unknown')
        
        # Choose color based on entity type
        colors = {
            'npc': (255, 255, 0),     # Yellow for NPCs
            'vehicle': (0, 0, 255),   # Blue for vehicles
            'monster': (255, 0, 0),   # Red for monsters
        }
        
        color = colors.get(entity_type, (128, 128, 128))
        
        # Render as simple circle for now
        pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 8)
        
        # Add a small label
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.Font(None, 20)
            label = entity.get('sprite', entity_type)[:8]  # First 8 chars
            text = font.render(label, True, (255, 255, 255))
            surface.blit(text, (screen_x - 20, screen_y - 20))
    
    def get_current_district(self, x: float, y: float) -> Optional[str]:
        """Get the district name at given coordinates"""
        for district_name, district in self.districts.items():
            if district['bounds'].collidepoint(x, y):
                return district_name
        return None
    
    def get_spawn_points(self) -> List[Tuple[float, float]]:
        """Get available spawn points in the world"""
        if self.world_data and 'spawn_points' in self.world_data:
            return self.world_data['spawn_points']
        elif self.world_builder:
            return self.world_builder.get_spawn_points()
        else:
            # Fallback spawn points
            return [
                (4100.0, 10100.0),  # Grove Street
                (12100.0, 8100.0),  # Downtown
                (20100.0, 4100.0),  # Beach
            ]
    
    def update_time(self, dt: float):
        """Update time of day (from original system)"""
        # 24 hours = 24 * 60 real seconds = 1440 seconds
        time_speed = 24.0 / 1440.0  # 24 hours in 24 real minutes
        self.time_of_day += time_speed * dt
        
        if self.time_of_day >= 24.0:
            self.time_of_day -= 24.0
    
    def is_collision(self, x: float, y: float) -> bool:
        """Check if position has collision"""
        if self.world_builder and self.world_builder.collision_map:
            tile_x = int(x // self.tile_size)
            tile_y = int(y // self.tile_size)
            
            if (0 <= tile_y < len(self.world_builder.collision_map) and 
                0 <= tile_x < len(self.world_builder.collision_map[0])):
                return self.world_builder.collision_map[tile_y][tile_x] == 1
        
        return False
    
    def get_nearby_entities(self, x: float, y: float, radius: float = 100.0) -> List[Dict]:
        """Get entities near a position"""
        nearby = []
        
        for entity in self.entities:
            entity_x, entity_y = entity['position']
            distance = ((x - entity_x)**2 + (y - entity_y)**2)**0.5
            
            if distance <= radius:
                entity_with_distance = entity.copy()
                entity_with_distance['distance'] = distance
                nearby.append(entity_with_distance)
        
        return sorted(nearby, key=lambda e: e['distance'])
    
    def render_minimap(self, surface: pygame.Surface, player_x: float, player_y: float):
        """Render minimap of the world"""
        minimap_size = 200
        minimap_rect = pygame.Rect(surface.get_width() - minimap_size - 20, 20, 
                                  minimap_size, minimap_size)
        
        # Draw minimap background
        pygame.draw.rect(surface, (0, 0, 0, 128), minimap_rect)
        pygame.draw.rect(surface, (255, 255, 255), minimap_rect, 2)
        
        # Calculate scale
        scale_x = minimap_size / self.world_width
        scale_y = minimap_size / self.world_height
        
        # Draw districts
        for district in self.districts.values():
            bounds = district['bounds']
            
            mini_rect = pygame.Rect(
                minimap_rect.x + int(bounds.x * scale_x),
                minimap_rect.y + int(bounds.y * scale_y),
                max(1, int(bounds.width * scale_x)),
                max(1, int(bounds.height * scale_y))
            )
            
            district_color = (50, 50, 50)
            pygame.draw.rect(surface, district_color, mini_rect)
        
        # Draw player position
        player_mini_x = minimap_rect.x + int(player_x * scale_x)
        player_mini_y = minimap_rect.y + int(player_y * scale_y)
        pygame.draw.circle(surface, (255, 0, 0), (player_mini_x, player_mini_y), 3)
    
    def get_world_stats(self) -> Dict[str, Any]:
        """Get statistics about the world"""
        return {
            'world_size': (self.world_width, self.world_height),
            'districts': len(self.districts),
            'entities': len(self.entities),
            'maps_loaded': len(self.world_data['maps']) if self.world_data else 0,
            'current_time': f"{int(self.time_of_day):02d}:{int((self.time_of_day % 1) * 60):02d}",
            'weather': self.weather,
            'wanted_level': self.wanted_level.value
        }