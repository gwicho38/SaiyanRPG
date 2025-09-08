#!/usr/bin/env python3
"""Quick TMX map test without pygame initialization issues."""

import os
import sys
from pathlib import Path

def test_map_discovery():
    """Test basic TMX map discovery without loading issues"""
    maps_path = Path("/Users/lefv/repos/SaiyanQuest/mods/saiyanquest/maps")
    
    if not maps_path.exists():
        print(f"Maps path does not exist: {maps_path}")
        return
    
    # Find all TMX files
    tmx_files = list(maps_path.glob("*.tmx"))
    print(f"Found {len(tmx_files)} TMX files")
    
    # Test basic XML parsing without pygame
    import xml.etree.ElementTree as ET
    
    working_maps = []
    broken_maps = []
    
    for tmx_file in tmx_files[:5]:  # Test first 5 maps
        try:
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            
            # Check if this is a valid TMX
            if root.tag == 'map':
                width = int(root.get('width', 0))
                height = int(root.get('height', 0))
                if width > 0 and height > 0:
                    working_maps.append(tmx_file.stem)
                else:
                    broken_maps.append((tmx_file.stem, "Invalid dimensions"))
            else:
                broken_maps.append((tmx_file.stem, "Not a TMX map"))
                
        except Exception as e:
            broken_maps.append((tmx_file.stem, str(e)))
    
    print(f"\nWorking maps: {len(working_maps)}")
    for map_name in working_maps:
        print(f"  ✓ {map_name}")
        
    print(f"\nBroken maps: {len(broken_maps)}")
    for map_name, error in broken_maps:
        print(f"  ✗ {map_name}: {error}")

if __name__ == "__main__":
    test_map_discovery()