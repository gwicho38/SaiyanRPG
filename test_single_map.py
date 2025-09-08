#!/usr/bin/env python3
"""Test single map loading with proper pygame initialization."""

import pygame
from saiyanquest.saiyanquest_map_renderer import SaiyanQuestMapRenderer

# Initialize pygame first
pygame.init()
pygame.display.set_mode((800, 600))

def test_single_map():
    """Test loading a single map"""
    print("Testing single map loading...")
    
    # Create renderer
    renderer = SaiyanQuestMapRenderer()
    
    # Test map discovery
    maps = renderer.discover_all_maps()
    print(f"Discovered {len(maps)} maps")
    
    if len(maps) > 0:
        # Try loading first map
        map_name = maps[0]
        print(f"Testing map: {map_name}")
        
        # Test metadata loading
        metadata = renderer.get_map_metadata(map_name)
        print(f"Metadata: {metadata}")
        
        if metadata:
            print("✓ Map loaded successfully!")
            return True
        else:
            print("✗ Failed to load map metadata")
            return False
    
    return False

if __name__ == "__main__":
    success = test_single_map()
    if success:
        print("\n🎉 Map loading works!")
    else:
        print("\n❌ Map loading failed")