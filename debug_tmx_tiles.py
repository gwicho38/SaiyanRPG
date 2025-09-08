#!/usr/bin/env python3
"""Debug script to analyze TMX tile data and tileset mapping."""

import base64
import zlib
import struct
import pygame
import pytmx
from pathlib import Path

# Initialize pygame
pygame.init()
pygame.display.set_mode((1, 1))

def decode_layer_data(data_string):
    """Decode base64/zlib compressed tile data."""
    # Remove whitespace
    data_string = data_string.strip()
    
    # Decode base64
    compressed_data = base64.b64decode(data_string)
    
    # Decompress zlib
    raw_data = zlib.decompress(compressed_data)
    
    # Convert to array of 32-bit integers (tile GIDs)
    tile_count = len(raw_data) // 4
    gids = struct.unpack(f'<{tile_count}I', raw_data)
    
    return gids

def analyze_tmx_map(map_path):
    """Analyze a TMX map's tile usage and tileset references."""
    print(f"\n=== Analyzing {map_path.name} ===")
    
    # Load the TMX map
    tmx_map = pytmx.load_pygame(str(map_path))
    
    print(f"Map size: {tmx_map.width}x{tmx_map.height}")
    print(f"Tile size: {tmx_map.tilewidth}x{tmx_map.tileheight}")
    print(f"Number of layers: {len(tmx_map.layers)}")
    print(f"Number of tilesets: {len(tmx_map.tilesets)}")
    
    # Analyze tilesets
    print("\nTilesets:")
    for i, tileset in enumerate(tmx_map.tilesets):
        print(f"  {i+1}. {tileset.name}")
        print(f"     firstgid: {tileset.firstgid}")
        print(f"     lastgid: {tileset.firstgid + tileset.tilecount - 1}")
        print(f"     tilecount: {tileset.tilecount}")
        if hasattr(tileset, 'source') and tileset.source:
            print(f"     source: {tileset.source}")
        
        # Check if image exists
        if hasattr(tileset, 'image') and tileset.image:
            image_path = map_path.parent / tileset.image
            if image_path.exists():
                print(f"     image: {tileset.image} ✓")
            else:
                print(f"     image: {tileset.image} ✗ MISSING")
    
    # Analyze layers
    print("\nLayers:")
    all_gids = set()
    empty_areas = []
    
    for layer in tmx_map.layers:
        if hasattr(layer, 'data'):  # Tile layer
            print(f"  Layer: {layer.name}")
            unique_gids = set()
            non_zero_count = 0
            zero_count = 0
            
            # Track empty areas (consecutive zeros)
            layer_empty_areas = []
            for y in range(tmx_map.height):
                for x in range(tmx_map.width):
                    gid = layer.data[y][x]
                    if gid > 0:
                        unique_gids.add(gid)
                        all_gids.add(gid)
                        non_zero_count += 1
                    else:
                        zero_count += 1
                        # Check if this starts a larger empty area
                        if x < tmx_map.width - 2 and y < tmx_map.height - 2:
                            empty_block = True
                            for dy in range(3):
                                for dx in range(3):
                                    if layer.data[y + dy][x + dx] != 0:
                                        empty_block = False
                                        break
                                if not empty_block:
                                    break
                            if empty_block:
                                layer_empty_areas.append((x, y))
            
            print(f"    Non-zero tiles: {non_zero_count}/{tmx_map.width * tmx_map.height}")
            print(f"    Empty tiles: {zero_count}/{tmx_map.width * tmx_map.height}")
            print(f"    Unique GIDs: {len(unique_gids)}")
            if unique_gids:
                print(f"    GID range: {min(unique_gids)} - {max(unique_gids)}")
            if layer_empty_areas:
                print(f"    Large empty areas (3x3+): {len(layer_empty_areas)} areas")
                empty_areas.extend([(layer.name, x, y) for x, y in layer_empty_areas[:5]])
    
    # Check which tilesets are actually used
    print(f"\nTotal unique GIDs across all layers: {len(all_gids)}")
    if all_gids:
        print(f"Overall GID range: {min(all_gids)} - {max(all_gids)}")
        
        print("\nTileset usage analysis:")
        for tileset in tmx_map.tilesets:
            tileset_gids = [gid for gid in all_gids 
                           if tileset.firstgid <= gid < tileset.firstgid + tileset.tilecount]
            print(f"  {tileset.name}: {len(tileset_gids)} tiles used")
            if len(tileset_gids) == 0:
                print(f"    WARNING: Tileset {tileset.name} is not used in any layer!")
    
    # Report any large empty areas that might indicate missing textures
    if empty_areas:
        print(f"\n⚠️ Large empty areas found (could indicate missing textures):")
        for layer_name, x, y in empty_areas[:10]:
            print(f"    {layer_name}: 3x3+ empty area at ({x}, {y})")

if __name__ == "__main__":
    # Test with multiple maps
    maps_dir = Path("/Users/lefv/repos/SaiyanQuest/mods/saiyanquest/maps")
    test_maps = [
        "flower_city.tmx",
        "azure_town_hall.tmx", 
        "37707_town.tmx"
    ]
    
    for map_name in test_maps:
        map_path = maps_dir / map_name
        if map_path.exists():
            analyze_tmx_map(map_path)
        else:
            print(f"Map file not found: {map_path}")