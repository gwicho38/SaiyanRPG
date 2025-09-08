#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# TMX Map Loader - Exact copy of SaiyanQuest map system

import pygame
import pytmx
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

class TMXMapLoader:
    """Loads and renders TMX maps exactly like SaiyanQuest"""
    
    def __init__(self, mod_path: str = "mods/saiyanquest"):
        self.mod_path = Path(mod_path)
        self.maps_path = self.mod_path / "maps"
        self.loaded_maps: Dict[str, pytmx.TiledMap] = {}
        self.rendered_maps: Dict[str, pygame.Surface] = {}
        
        # Cache for tileset images to avoid reloading
        self.tileset_cache: Dict[str, pygame.Surface] = {}
        
    def load_map(self, map_name: str) -> Optional[pytmx.TiledMap]:
        """Load a TMX map file"""
        if map_name in self.loaded_maps:
            return self.loaded_maps[map_name]
        
        map_file = self.maps_path / f"{map_name}.tmx"
        if not map_file.exists():
            logging.warning(f"Map file not found: {map_file}")
            return None
        
        try:
            # Load the TMX map with proper image loader
            from saiyanquest.graphics import scaled_image_loader
            tmx_map = pytmx.load_pygame(
                str(map_file), 
                image_loader=scaled_image_loader,
                pixelalpha=True
            )
            self.loaded_maps[map_name] = tmx_map
            return tmx_map
        except Exception as e:
            logging.error(f"Failed to load map {map_name}: {e}")
            return None
    
    def render_map(self, map_name: str) -> Optional[pygame.Surface]:
        """Render a TMX map to a surface exactly like SaiyanQuest"""
        if map_name in self.rendered_maps:
            return self.rendered_maps[map_name]
        
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return None
        
        try:
            # Calculate map dimensions
            map_width = tmx_map.width * tmx_map.tilewidth
            map_height = tmx_map.height * tmx_map.tileheight
            
            # Create surface for the rendered map
            map_surface = pygame.Surface((map_width, map_height))
            map_surface.fill((0, 0, 0, 0))  # Transparent background
            
            # Render each layer
            for layer in tmx_map.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    self._render_tile_layer(map_surface, tmx_map, layer)
                elif hasattr(layer, 'objects') and hasattr(layer, '__iter__'):
                    # Object layers contain NPCs, items, etc. - handle separately
                    pass
                elif hasattr(layer, 'image'):
                    self._render_image_layer(map_surface, layer)
            
            self.rendered_maps[map_name] = map_surface
            return map_surface
            
        except Exception as e:
            logging.error(f"Failed to render map {map_name}: {e}")
            return None
    
    def _render_tile_layer(self, surface: pygame.Surface, tmx_map: pytmx.TiledMap, layer: pytmx.TiledTileLayer):
        """Render a tile layer exactly like SaiyanQuest"""
        for x, y, gid in layer:
            if gid == 0:  # Empty tile
                continue
            
            # Get tile image
            tile = tmx_map.get_tile_image_by_gid(gid)
            if tile:
                # Calculate position
                pos_x = x * tmx_map.tilewidth
                pos_y = y * tmx_map.tileheight
                
                # Blit tile to surface
                surface.blit(tile, (pos_x, pos_y))
    
    def _render_image_layer(self, surface: pygame.Surface, layer: pytmx.TiledImageLayer):
        """Render an image layer"""
        if layer.image:
            surface.blit(layer.image, (layer.offset_x, layer.offset_y))
    
    def get_map_size(self, map_name: str) -> Optional[Tuple[int, int]]:
        """Get the pixel size of a map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return None
        
        return (tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight)
    
    def get_map_collisions(self, map_name: str) -> List[pygame.Rect]:
        """Extract collision objects from the map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return []
        
        collisions = []
        for layer in tmx_map.layers:
            if hasattr(layer, 'objects') and hasattr(layer, 'name') and layer.name == "Collisions":
                for obj in layer:
                    if obj.type == "collision":
                        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        collisions.append(rect)
        
        return collisions
    
    def get_map_npcs(self, map_name: str) -> List[Dict[str, Any]]:
        """Extract NPC objects from the map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return []
        
        npcs = []
        for layer in tmx_map.layers:
            if hasattr(layer, 'objects') and hasattr(layer, '__iter__'):
                for obj in layer:
                    if hasattr(obj, 'type') and obj.type in ['npc', 'character', 'monster']:
                        npc_data = {
                            'type': obj.type,
                            'x': obj.x,
                            'y': obj.y,
                            'width': getattr(obj, 'width', 16),
                            'height': getattr(obj, 'height', 16),
                            'properties': dict(obj.properties) if hasattr(obj, 'properties') else {}
                        }
                        npcs.append(npc_data)
        
        return npcs
    
    def get_map_spawns(self, map_name: str) -> List[Tuple[int, int]]:
        """Extract spawn points from the map"""
        tmx_map = self.load_map(map_name)
        if not tmx_map:
            return []
        
        spawns = []
        for layer in tmx_map.layers:
            if hasattr(layer, 'objects') and hasattr(layer, '__iter__'):
                for obj in layer:
                    if hasattr(obj, 'type') and obj.type in ['spawn', 'player_spawn']:
                        spawns.append((int(obj.x), int(obj.y)))
        
        return spawns
    
    def discover_all_maps(self) -> List[str]:
        """Discover all TMX maps in the SaiyanQuest directory"""
        maps = []
        if not self.maps_path.exists():
            return maps
        
        for tmx_file in self.maps_path.glob("*.tmx"):
            map_name = tmx_file.stem
            maps.append(map_name)
        
        return sorted(maps)
    
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
    
    def clear_cache(self):
        """Clear all cached maps to free memory"""
        self.loaded_maps.clear()
        self.rendered_maps.clear()
        self.tileset_cache.clear()
    
    def preload_maps(self, map_names: List[str]):
        """Preload multiple maps"""
        for map_name in map_names:
            self.load_map(map_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics"""
        return {
            'loaded_maps': len(self.loaded_maps),
            'rendered_maps': len(self.rendered_maps),
            'tileset_cache_size': len(self.tileset_cache),
            'available_maps': len(self.discover_all_maps())
        }

# Global TMX loader instance
_tmx_loader = None

def get_tmx_loader() -> TMXMapLoader:
    """Get the global TMX loader instance"""
    global _tmx_loader
    if _tmx_loader is None:
        _tmx_loader = TMXMapLoader()
    return _tmx_loader