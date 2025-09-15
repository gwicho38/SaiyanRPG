#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Pixel Art Map System - GBA-style graphics for SaiyanQuest GTA

import pygame
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import time

# Import pytmx with try/except for optional dependency
try:
    import pytmx
    PYTMX_AVAILABLE = True
except ImportError:
    PYTMX_AVAILABLE = False
    pytmx = None

class TileType(Enum):
    """Types of tiles for different rendering layers"""
    BACKGROUND = "background"
    COLLISION = "collision" 
    FOREGROUND = "foreground"
    WATER = "water"
    ANIMATED = "animated"
    DECORATION = "decoration"

class AnimationType(Enum):
    """Types of tile animations"""
    WATER = "water"
    FIRE = "fire"
    SMOKE = "smoke"
    SPARKLE = "sparkle"
    GRASS = "grass"

@dataclass
class PixelTile:
    """Represents a single pixel art tile"""
    tile_id: int
    x: int
    y: int
    tile_type: TileType
    sprite: Optional[pygame.Surface] = None
    animation_type: Optional[AnimationType] = None
    animation_frames: List[pygame.Surface] = None
    animation_speed: float = 0.5  # seconds per frame
    collision: bool = False
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.animation_frames is None:
            self.animation_frames = []
        if self.properties is None:
            self.properties = {}

@dataclass
class TileLayer:
    """A layer of tiles for rendering"""
    name: str
    tiles: Dict[Tuple[int, int], PixelTile]
    visible: bool = True
    opacity: float = 1.0
    parallax_x: float = 1.0
    parallax_y: float = 1.0

class PixelArtMapSystem:
    """Main system for managing pixel art maps with GBA-style graphics"""
    
    def __init__(self, mod_path: str = "mods/saiyanquest"):
        self.mod_path = Path(mod_path)
        self.tile_size = 16  # Standard GBA tile size
        self.scale_factor = 2  # Scale for modern displays
        
        # Tile management
        self.tilesets: Dict[str, pygame.Surface] = {}
        self.tile_cache: Dict[int, pygame.Surface] = {}
        self.animated_tiles: Dict[int, List[pygame.Surface]] = {}
        
        # Map data
        self.current_map: Optional[str] = None
        self.map_layers: Dict[str, TileLayer] = {}
        self.map_width = 0
        self.map_height = 0
        
        # Rendering optimization
        self.visible_tiles: Set[Tuple[int, int]] = set()
        self.dirty_chunks: Set[Tuple[int, int]] = set()
        self.chunk_size = 32  # 32x32 tiles per chunk
        self.chunk_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        
        # Animation system
        self.animation_timer = 0.0
        self.current_frame = 0
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Initialize
        self._load_tilesets()
        self._create_default_tiles()
    
    def _load_tilesets(self):
        """Load tilesets from the SaiyanQuest mod directory"""
        print("🎨 Loading Pixel Art Tilesets...")
        
        # Look for tilesets in the gfx directory
        gfx_path = self.mod_path / "gfx" / "tilesets"
        if gfx_path.exists():
            for tileset_file in gfx_path.glob("*.png"):
                tileset_name = tileset_file.stem
                try:
                    tileset_surface = pygame.image.load(str(tileset_file))
                    # Convert to ensure proper pixel format
                    tileset_surface = tileset_surface.convert_alpha()
                    self.tilesets[tileset_name] = tileset_surface
                    print(f"   ✓ Loaded tileset: {tileset_name} ({tileset_surface.get_size()})")
                except Exception as e:
                    print(f"   ❌ Failed to load tileset {tileset_name}: {e}")
        
        # If no tilesets found, create a basic one
        if not self.tilesets:
            self._create_basic_tileset()
    
    def _create_basic_tileset(self):
        """Create a basic tileset if none are available"""
        print("🎨 Creating basic GBA-style tileset...")
        
        # Create a 256x256 tileset with various tile types
        tileset_size = 256
        tileset = pygame.Surface((tileset_size, tileset_size))
        tileset.fill((0, 0, 0, 0))  # Transparent background
        
        # Create different tile types
        tile_colors = {
            'grass': (34, 139, 34),      # Forest green
            'dirt': (139, 69, 19),       # Saddle brown  
            'stone': (128, 128, 128),    # Gray
            'water': (30, 144, 255),     # Dodger blue
            'road': (64, 64, 64),        # Dark gray
            'sidewalk': (192, 192, 192), # Light gray
            'building': (139, 69, 19),   # Brown
            'roof': (160, 82, 45),       # Saddle brown
        }
        
        # Draw tiles in a grid pattern
        tiles_per_row = tileset_size // self.tile_size
        for i, (tile_name, color) in enumerate(tile_colors.items()):
            if i >= tiles_per_row * tiles_per_row:
                break
                
            tile_x = (i % tiles_per_row) * self.tile_size
            tile_y = (i // tiles_per_row) * self.tile_size
            
            # Draw basic tile
            tile_rect = pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size)
            pygame.draw.rect(tileset, color, tile_rect)
            
            # Add some texture based on tile type
            if tile_name == 'grass':
                # Add grass texture
                for j in range(3):
                    grass_x = tile_x + random.randint(2, self.tile_size - 2)
                    grass_y = tile_y + random.randint(2, self.tile_size - 2)
                    pygame.draw.circle(tileset, (0, 100, 0), (grass_x, grass_y), 1)
            elif tile_name == 'water':
                # Add water texture
                for j in range(2):
                    wave_x = tile_x + random.randint(0, self.tile_size)
                    wave_y = tile_y + random.randint(0, self.tile_size)
                    pygame.draw.circle(tileset, (100, 200, 255), (wave_x, wave_y), 2)
            elif tile_name == 'road':
                # Add road markings
                center_y = tile_y + self.tile_size // 2
                pygame.draw.line(tileset, (255, 255, 255), 
                               (tile_x, center_y), (tile_x + self.tile_size, center_y), 2)
        
        self.tilesets['basic'] = tileset
        print(f"   ✓ Created basic tileset: {tileset.get_size()}")
    
    def _create_default_tiles(self):
        """Create default tile definitions"""
        # Create tile definitions based on the basic tileset
        tile_definitions = {
            0: {'type': TileType.BACKGROUND, 'name': 'grass', 'collision': False},
            1: {'type': TileType.BACKGROUND, 'name': 'dirt', 'collision': False},
            2: {'type': TileType.BACKGROUND, 'name': 'stone', 'collision': True},
            3: {'type': TileType.WATER, 'name': 'water', 'collision': True, 'animation': AnimationType.WATER},
            4: {'type': TileType.BACKGROUND, 'name': 'road', 'collision': False},
            5: {'type': TileType.BACKGROUND, 'name': 'sidewalk', 'collision': False},
            6: {'type': TileType.BACKGROUND, 'name': 'building', 'collision': True},
            7: {'type': TileType.BACKGROUND, 'name': 'roof', 'collision': True},
        }
        
        # Create animated tiles
        self._create_animated_tiles()
    
    def _create_animated_tiles(self):
        """Create animated tile frames"""
        # Water animation frames
        water_frames = []
        for frame in range(4):
            frame_surface = pygame.Surface((self.tile_size, self.tile_size))
            frame_surface.fill((0, 0, 0, 0))
            
            # Create water effect
            base_color = (30, 144, 255)
            wave_offset = frame * 2
            
            for y in range(0, self.tile_size, 4):
                wave_x = int(math.sin((y + wave_offset) * 0.5) * 2)
                pygame.draw.line(frame_surface, base_color,
                               (self.tile_size//2 + wave_x, y),
                               (self.tile_size//2 + wave_x, y + 2), 2)
            
            water_frames.append(frame_surface)
        
        self.animated_tiles[3] = water_frames  # Tile ID 3 is water
        
        # Fire animation frames
        fire_frames = []
        for frame in range(6):
            frame_surface = pygame.Surface((self.tile_size, self.tile_size))
            frame_surface.fill((0, 0, 0, 0))
            
            # Create fire effect
            colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
            for i, color in enumerate(colors):
                flame_height = self.tile_size - (frame * 2) - (i * 2)
                if flame_height > 0:
                    pygame.draw.circle(frame_surface, color,
                                     (self.tile_size//2, self.tile_size - flame_height//2),
                                     flame_height//4)
            
            fire_frames.append(frame_surface)
        
        # Add fire tiles to animated tiles (tile IDs 8-10)
        for i in range(3):
            self.animated_tiles[8 + i] = fire_frames
    
    def load_map_from_tmx(self, map_name: str) -> bool:
        """Load a map from TMX format and convert to pixel art system"""
        print(f"🗺️ Loading pixel art map: {map_name}")
        
        # Load TMX map
        map_file = self.mod_path / "maps" / f"{map_name}.tmx"
        if not map_file.exists():
            print(f"   ❌ Map file not found: {map_file}")
            return False
        
        try:
            if not PYTMX_AVAILABLE:
                print(f"   ⚠️ pytmx not available, skipping TMX loading")
                return False
                
            from saiyanquest.graphics import scaled_image_loader
            
            tmx_map = pytmx.load_pygame(str(map_file), image_loader=scaled_image_loader, pixelalpha=True)
            
            # Convert TMX map to pixel art format
            self.map_width = tmx_map.width
            self.map_height = tmx_map.height
            self.current_map = map_name
            
            # Clear existing layers
            self.map_layers.clear()
            self.dirty_chunks.clear()
            self.chunk_cache.clear()
            
            # Process each layer
            for layer in tmx_map.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    self._process_tmx_layer(layer, tmx_map)
            
            print(f"   ✓ Loaded map: {map_name} ({self.map_width}x{self.map_height})")
            print(f"   ✓ Created {len(self.map_layers)} layers")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to load map {map_name}: {e}")
            return False
    
    def _process_tmx_layer(self, layer, tmx_map):
        """Process a TMX tile layer into pixel art format"""
        layer_name = layer.name
        tile_layer = TileLayer(name=layer_name)
        
        # Determine layer properties
        if 'collision' in layer_name.lower():
            layer_type = TileType.COLLISION
        elif 'foreground' in layer_name.lower():
            layer_type = TileType.FOREGROUND
        elif 'water' in layer_name.lower():
            layer_type = TileType.WATER
        else:
            layer_type = TileType.BACKGROUND
        
        # Process each tile
        for x, y, gid in layer:
            if gid == 0:  # Empty tile
                continue
            
            # Get tile properties from TMX
            tile_properties = {}
            if hasattr(tmx_map, 'get_tile_properties_by_gid'):
                props = tmx_map.get_tile_properties_by_gid(gid)
                if props:
                    tile_properties = dict(props)
            
            # Create pixel tile
            pixel_tile = PixelTile(
                tile_id=gid,
                x=x,
                y=y,
                tile_type=layer_type,
                collision=tile_properties.get('collision', False),
                properties=tile_properties
            )
            
            # Get tile sprite
            tile_sprite = self._get_tile_sprite(gid)
            if tile_sprite:
                pixel_tile.sprite = tile_sprite
                
                # Check for animation
                if gid in self.animated_tiles:
                    pixel_tile.animation_type = AnimationType.WATER  # Default to water
                    pixel_tile.animation_frames = self.animated_tiles[gid]
                    pixel_tile.tile_type = TileType.ANIMATED
            
            tile_layer.tiles[(x, y)] = pixel_tile
        
        self.map_layers[layer_name] = tile_layer
    
    def _get_tile_sprite(self, tile_id: int) -> Optional[pygame.Surface]:
        """Get sprite for a tile ID"""
        if tile_id in self.tile_cache:
            return self.tile_cache[tile_id]
        
        # Extract tile from tileset
        tiles_per_row = 16  # Assume 16 tiles per row
        tile_x = (tile_id % tiles_per_row) * self.tile_size
        tile_y = (tile_id // tiles_per_row) * self.tile_size
        
        # Use the first available tileset
        if self.tilesets:
            tileset_name = list(self.tilesets.keys())[0]
            tileset = self.tilesets[tileset_name]
            
            # Check bounds
            if (tile_x + self.tile_size <= tileset.get_width() and 
                tile_y + self.tile_size <= tileset.get_height()):
                
                tile_rect = pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size)
                tile_sprite = tileset.subsurface(tile_rect)
                
                # Scale for display
                scaled_size = (self.tile_size * self.scale_factor, 
                              self.tile_size * self.scale_factor)
                tile_sprite = pygame.transform.scale(tile_sprite, scaled_size)
                
                self.tile_cache[tile_id] = tile_sprite
                return tile_sprite
        
        return None
    
    def create_procedural_map(self, width: int, height: int, map_type: str = "city") -> bool:
        """Create a procedural pixel art map"""
        print(f"🗺️ Creating procedural {map_type} map: {width}x{height}")
        
        self.map_width = width
        self.map_height = height
        self.current_map = f"procedural_{map_type}"
        
        # Clear existing data
        self.map_layers.clear()
        self.dirty_chunks.clear()
        self.chunk_cache.clear()
        
        # Create layers
        background_layer = TileLayer(name="background")
        collision_layer = TileLayer(name="collision")
        decoration_layer = TileLayer(name="decoration")
        
        if map_type == "city":
            self._generate_city_map(background_layer, collision_layer, decoration_layer)
        elif map_type == "nature":
            self._generate_nature_map(background_layer, collision_layer, decoration_layer)
        elif map_type == "mixed":
            self._generate_mixed_map(background_layer, collision_layer, decoration_layer)
        else:
            self._generate_basic_map(background_layer, collision_layer, decoration_layer)
        
        # Add layers to map
        self.map_layers["background"] = background_layer
        self.map_layers["collision"] = collision_layer
        self.map_layers["decoration"] = decoration_layer
        
        print(f"   ✓ Created procedural map with {len(self.map_layers)} layers")
        return True
    
    def _generate_city_map(self, bg_layer: TileLayer, col_layer: TileLayer, dec_layer: TileLayer):
        """Generate a city-style map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                # Determine tile type based on position and noise
                noise_val = self._simple_noise(x, y, 0.1)
                
                if noise_val < 0.3:
                    # Roads
                    tile_id = 4  # Road tile
                    collision = False
                elif noise_val < 0.6:
                    # Buildings
                    tile_id = 6  # Building tile
                    collision = True
                else:
                    # Sidewalks/grass
                    tile_id = 5 if random.random() < 0.5 else 0
                    collision = tile_id == 5
                
                # Create background tile
                bg_tile = PixelTile(
                    tile_id=tile_id,
                    x=x, y=y,
                    tile_type=TileType.BACKGROUND,
                    sprite=self._get_tile_sprite(tile_id),
                    collision=collision
                )
                bg_layer.tiles[(x, y)] = bg_tile
                
                # Add collision tile if needed
                if collision:
                    col_tile = PixelTile(
                        tile_id=2,  # Stone collision
                        x=x, y=y,
                        tile_type=TileType.COLLISION,
                        sprite=self._get_tile_sprite(2),
                        collision=True
                    )
                    col_layer.tiles[(x, y)] = col_tile
    
    def _generate_nature_map(self, bg_layer: TileLayer, col_layer: TileLayer, dec_layer: TileLayer):
        """Generate a nature-style map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                noise_val = self._simple_noise(x, y, 0.05)
                
                if noise_val < 0.2:
                    # Water
                    tile_id = 3  # Water tile
                    collision = True
                elif noise_val < 0.4:
                    # Stone/rocks
                    tile_id = 2
                    collision = True
                else:
                    # Grass/dirt
                    tile_id = 0 if random.random() < 0.7 else 1
                    collision = False
                
                bg_tile = PixelTile(
                    tile_id=tile_id,
                    x=x, y=y,
                    tile_type=TileType.BACKGROUND,
                    sprite=self._get_tile_sprite(tile_id),
                    collision=collision
                )
                bg_layer.tiles[(x, y)] = bg_tile
                
                if collision:
                    col_tile = PixelTile(
                        tile_id=2,
                        x=x, y=y,
                        tile_type=TileType.COLLISION,
                        sprite=self._get_tile_sprite(2),
                        collision=True
                    )
                    col_layer.tiles[(x, y)] = col_tile
    
    def _generate_mixed_map(self, bg_layer: TileLayer, col_layer: TileLayer, dec_layer: TileLayer):
        """Generate a mixed urban/nature map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                # Create zones
                center_x, center_y = self.map_width // 2, self.map_height // 2
                dist_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                if dist_from_center < self.map_width * 0.3:
                    # Urban center
                    tile_id = 4 if random.random() < 0.3 else 6
                    collision = tile_id == 6
                elif dist_from_center < self.map_width * 0.6:
                    # Suburban
                    tile_id = 0 if random.random() < 0.6 else 5
                    collision = tile_id == 5
                else:
                    # Rural/nature
                    tile_id = 0 if random.random() < 0.8 else 1
                    collision = False
                
                bg_tile = PixelTile(
                    tile_id=tile_id,
                    x=x, y=y,
                    tile_type=TileType.BACKGROUND,
                    sprite=self._get_tile_sprite(tile_id),
                    collision=collision
                )
                bg_layer.tiles[(x, y)] = bg_tile
                
                if collision:
                    col_tile = PixelTile(
                        tile_id=2,
                        x=x, y=y,
                        tile_type=TileType.COLLISION,
                        sprite=self._get_tile_sprite(2),
                        collision=True
                    )
                    col_layer.tiles[(x, y)] = col_tile
    
    def _generate_basic_map(self, bg_layer: TileLayer, col_layer: TileLayer, dec_layer: TileLayer):
        """Generate a basic map"""
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_id = 0  # Grass
                collision = False
                
                bg_tile = PixelTile(
                    tile_id=tile_id,
                    x=x, y=y,
                    tile_type=TileType.BACKGROUND,
                    sprite=self._get_tile_sprite(tile_id),
                    collision=collision
                )
                bg_layer.tiles[(x, y)] = bg_tile
    
    def _simple_noise(self, x: int, y: int, scale: float) -> float:
        """Simple noise function for procedural generation"""
        return (math.sin(x * scale) + math.cos(y * scale)) / 2.0
    
    def update_camera(self, camera_x: float, camera_y: float):
        """Update camera position and visible tiles"""
        self.camera_x = camera_x
        self.camera_y = camera_y
        
        # Calculate visible tile range
        tile_size_scaled = self.tile_size * self.scale_factor
        start_x = max(0, int(camera_x // tile_size_scaled) - 1)
        start_y = max(0, int(camera_y // tile_size_scaled) - 1)
        end_x = min(self.map_width, int((camera_x + self.screen_width) // tile_size_scaled) + 1)
        end_y = min(self.map_height, int((camera_y + self.screen_height) // tile_size_scaled) + 1)
        
        # Update visible tiles set
        self.visible_tiles.clear()
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.visible_tiles.add((x, y))
    
    def update_animations(self, dt: float):
        """Update tile animations"""
        self.animation_timer += dt
        
        if self.animation_timer >= 0.5:  # 0.5 seconds per frame
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % 4  # Assume 4 frames max
            
            # Mark animated tiles as dirty
            for layer in self.map_layers.values():
                for tile in layer.tiles.values():
                    if tile.animation_frames:
                        chunk_x = tile.x // self.chunk_size
                        chunk_y = tile.y // self.chunk_size
                        self.dirty_chunks.add((chunk_x, chunk_y))
    
    def render(self, surface: pygame.Surface):
        """Render the pixel art map"""
        if not self.map_layers:
            return
        
        # Render layers in order
        layer_order = ["background", "collision", "decoration", "foreground"]
        
        for layer_name in layer_order:
            if layer_name in self.map_layers:
                layer = self.map_layers[layer_name]
                if layer.visible:
                    self._render_layer(surface, layer)
    
    def _render_layer(self, surface: pygame.Surface, layer: TileLayer):
        """Render a specific layer"""
        tile_size_scaled = self.tile_size * self.scale_factor
        
        for (x, y), tile in layer.tiles.items():
            if (x, y) not in self.visible_tiles:
                continue
            
            # Calculate screen position
            screen_x = x * tile_size_scaled - self.camera_x
            screen_y = y * tile_size_scaled - self.camera_y
            
            # Only render if on screen
            if (-tile_size_scaled <= screen_x <= self.screen_width and
                -tile_size_scaled <= screen_y <= self.screen_height):
                
                # Get sprite to render
                sprite = tile.sprite
                
                # Handle animated tiles
                if tile.animation_frames and self.current_frame < len(tile.animation_frames):
                    sprite = tile.animation_frames[self.current_frame]
                    if sprite:
                        # Scale animated sprite
                        scaled_size = (self.tile_size * self.scale_factor, 
                                      self.tile_size * self.scale_factor)
                        sprite = pygame.transform.scale(sprite, scaled_size)
                
                if sprite:
                    # Apply layer opacity
                    if layer.opacity < 1.0:
                        sprite = sprite.copy()
                        sprite.set_alpha(int(255 * layer.opacity))
                    
                    surface.blit(sprite, (int(screen_x), int(screen_y)))
    
    def get_collision_at(self, x: float, y: float) -> bool:
        """Check if there's collision at world coordinates"""
        tile_x = int(x // (self.tile_size * self.scale_factor))
        tile_y = int(y // (self.tile_size * self.scale_factor))
        
        # Check collision layer
        if "collision" in self.map_layers:
            collision_layer = self.map_layers["collision"]
            if (tile_x, tile_y) in collision_layer.tiles:
                return True
        
        # Check background tiles with collision
        for layer in self.map_layers.values():
            if (tile_x, tile_y) in layer.tiles:
                tile = layer.tiles[(tile_x, tile_y)]
                if tile.collision:
                    return True
        
        return False
    
    def get_tile_at(self, x: float, y: float) -> Optional[PixelTile]:
        """Get the tile at world coordinates"""
        tile_x = int(x // (self.tile_size * self.scale_factor))
        tile_y = int(y // (self.tile_size * self.scale_factor))
        
        # Check layers in reverse order (foreground first)
        layer_order = ["foreground", "decoration", "collision", "background"]
        
        for layer_name in layer_order:
            if layer_name in self.map_layers:
                layer = self.map_layers[layer_name]
                if (tile_x, tile_y) in layer.tiles:
                    return layer.tiles[(tile_x, tile_y)]
        
        return None
    
    def get_map_info(self) -> Dict[str, Any]:
        """Get information about the current map"""
        return {
            'map_name': self.current_map,
            'map_size': (self.map_width, self.map_height),
            'tile_size': self.tile_size,
            'scale_factor': self.scale_factor,
            'layers': list(self.map_layers.keys()),
            'visible_tiles': len(self.visible_tiles),
            'total_tiles': sum(len(layer.tiles) for layer in self.map_layers.values()),
            'animated_tiles': len(self.animated_tiles),
            'tilesets_loaded': len(self.tilesets)
        }

# Global pixel art map system instance
_pixel_map_system = None

def get_pixel_map_system() -> PixelArtMapSystem:
    """Get the global pixel art map system instance"""
    global _pixel_map_system
    if _pixel_map_system is None:
        _pixel_map_system = PixelArtMapSystem()
    return _pixel_map_system