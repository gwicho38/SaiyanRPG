#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# SaiyanQuest Map Renderer - Uses pyscroll like actual SaiyanQuest

import pygame
import pyscroll
import pytmx
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import warnings
import os

# Suppress all PNG warnings and pyscroll warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['PYTHONWARNINGS'] = 'ignore'

# Keep default video driver for compatibility

# Set logging level to reduce noise
logging.basicConfig(level=logging.WARNING)

class SaiyanQuestMapRenderer:
    """Renders SaiyanQuest TMX maps using pyscroll (exactly like SaiyanQuest)"""
    
    def __init__(self, mod_path: str = "mods/saiyanquest"):
        self.mod_path = Path(mod_path)
        self.maps_path = self.mod_path / "maps"
        self.loaded_maps: Dict[str, pytmx.TiledMap] = {}
        self.rendered_maps: Dict[str, pygame.Surface] = {}
        self.renderers: Dict[str, pyscroll.BufferedRenderer] = {}
        
        # Screen size for rendering
        self.render_size = (800, 600)
        
        # Ensure pygame is initialized for TMX loading
        self._ensure_pygame_initialized()
    
    def _ensure_pygame_initialized(self):
        """Ensure pygame is initialized for TMX loading operations"""
        if not pygame.get_init():
            pygame.init()
        
        # Ensure display is initialized (needed for surface conversions)
        try:
            if not pygame.display.get_surface():
                # Create minimal display for loading operations
                pygame.display.set_mode((1, 1))
        except pygame.error:
            # Display not initialized, create it
            pygame.display.set_mode((1, 1))
        
    def load_map(self, map_name: str) -> Optional[pytmx.TiledMap]:
        """Load a TMX map file using SaiyanQuest's method"""
        if map_name in self.loaded_maps:
            return self.loaded_maps[map_name]
        
        map_file = self.maps_path / f"{map_name}.tmx"
        if not map_file.exists():
            logging.warning(f"Map file not found: {map_file}")
            return None
        
        try:
            # Load TMX map the same way SaiyanQuest does
            # Suppress warnings during loading
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tmx_map = pytmx.load_pygame(
                    str(map_file),
                    pixelalpha=True
                )
            
            self.loaded_maps[map_name] = tmx_map
            return tmx_map
            
        except Exception as e:
            # Suppress common missing tileset errors to reduce noise
            error_msg = str(e)
            if any(pattern in error_msg for pattern in [
                "Cannot find tileset file",
                "No file 'mods/saiyanquest/maps/../gfx/tilesets/",
                "Cave_Tiles_by_ArMM1998",
                "My_SaiyanQuest_sheet"
            ]):
                # These are expected for some maps - just debug log
                logging.debug(f"Missing optional tileset for {map_name}: {e}")
            else:
                # Log actual errors
                logging.error(f"Failed to load map {map_name}: {e}")
            return None
    
    def render_map_to_surface(self, map_name: str) -> Optional[pygame.Surface]:
        """Render entire map to a surface using pyscroll like SaiyanQuest"""
        if map_name in self.rendered_maps:
            return self.rendered_maps[map_name]
        
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            print(f"🚫 Failed to load TMX map: {map_name}")
            return None
        
        print(f"🗺️ Rendering map: {map_name} ({tmx_map.width}x{tmx_map.height})")
        print(f"   Tilesets: {len(tmx_map.tilesets)}")
        for i, tileset in enumerate(tmx_map.tilesets):
            print(f"   - {i+1}. {tileset.name} (firstgid: {tileset.firstgid}, tiles: {tileset.tilecount})")
            if hasattr(tileset, 'image') and tileset.image:
                tileset_path = self.mod_path / "gfx/tilesets" / tileset.image
                if tileset_path.exists():
                    print(f"      Image: {tileset.image} ✓")
                else:
                    print(f"      Image: {tileset.image} ✗ MISSING")
        
        try:
            # Create pyscroll data exactly like SaiyanQuest does
            visual_data = pyscroll.data.TiledMapData(tmx_map)
            
            # Calculate full map size
            map_width = tmx_map.width * tmx_map.tilewidth
            map_height = tmx_map.height * tmx_map.tileheight
            
            # Create renderer for the full map size (without tall_sprites to avoid warnings)
            renderer = pyscroll.BufferedRenderer(
                visual_data,
                (map_width, map_height),
                clamp_camera=True
            )
            
            # Create surface to render the entire map
            map_surface = pygame.Surface((map_width, map_height))
            
            # Render the entire map to the surface
            renderer.center((map_width // 2, map_height // 2))
            renderer.draw(map_surface, pygame.Rect(0, 0, map_width, map_height))
            
            # Cache the rendered surface
            self.rendered_maps[map_name] = map_surface
            self.renderers[map_name] = renderer
            
            return map_surface
            
        except Exception as e:
            logging.error(f"Failed to render map {map_name}: {e}")
            return None
    
    def get_map_size(self, map_name: str) -> Optional[Tuple[int, int]]:
        """Get the pixel size of a map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return None
        
        return (tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight)
    
    def get_map_metadata(self, map_name: str) -> Dict[str, Any]:
        """Get map metadata from TMX properties"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return {}
        
        metadata = {
            'width': tmx_map.width,
            'height': tmx_map.height,
            'tile_width': tmx_map.tilewidth,
            'tile_height': tmx_map.tileheight,
            'pixel_width': tmx_map.width * tmx_map.tilewidth,
            'pixel_height': tmx_map.height * tmx_map.tileheight,
            'properties': dict(tmx_map.properties) if hasattr(tmx_map, 'properties') else {}
        }
        
        return metadata
    
    def get_map_collisions(self, map_name: str) -> List[pygame.Rect]:
        """Extract collision objects from the map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return []
        
        collisions = []
        for layer in tmx_map.layers:
            if hasattr(layer, 'objects') and hasattr(layer, 'name'):
                if layer.name.lower() in ['collisions', 'collision']:
                    for obj in layer:
                        if hasattr(obj, 'type') and obj.type == "collision":
                            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            collisions.append(rect)
        
        return collisions
    
    def discover_all_maps(self) -> List[str]:
        """Discover all TMX maps in the SaiyanQuest directory"""
        maps = []
        if not self.maps_path.exists():
            return maps
        
        for tmx_file in self.maps_path.glob("*.tmx"):
            map_name = tmx_file.stem
            maps.append(map_name)
        
        return sorted(maps)
    
    def clear_cache(self):
        """Clear all cached maps to free memory"""
        self.loaded_maps.clear()
        self.rendered_maps.clear()
        self.renderers.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get renderer statistics"""
        return {
            'loaded_maps': len(self.loaded_maps),
            'rendered_maps': len(self.rendered_maps),
            'available_maps': len(self.discover_all_maps())
        }

# Global SaiyanQuest map renderer instance
_sq_renderer = None

def get_saiyanquest_renderer() -> SaiyanQuestMapRenderer:
    """Get the global SaiyanQuest map renderer instance"""
    global _sq_renderer
    if _sq_renderer is None:
        _sq_renderer = SaiyanQuestMapRenderer()
    return _sq_renderer