#!/usr/bin/env python3
"""Test metadata loading for all maps."""

import pygame
from saiyanquest.saiyanquest_map_renderer import SaiyanQuestMapRenderer

# Initialize pygame first
pygame.init()
pygame.display.set_mode((800, 600))

def test_all_maps_metadata():
    """Test loading metadata for all maps"""
    print("Testing metadata loading for all maps...")
    
    # Create renderer
    renderer = SaiyanQuestMapRenderer()
    
    # Test map discovery
    maps = renderer.discover_all_maps()
    print(f"Discovered {len(maps)} maps")
    
    successful_loads = 0
    failed_loads = 0
    
    for i, map_name in enumerate(maps[:20]):  # Test first 20 maps
        print(f"Testing {i+1}/{len(maps)}: {map_name}")
        
        # Test metadata loading
        metadata = renderer.get_map_metadata(map_name)
        
        if metadata:
            successful_loads += 1
            print(f"  ✓ {metadata['width']}x{metadata['height']} tiles")
        else:
            failed_loads += 1
            print(f"  ✗ Failed to load metadata")
    
    print(f"\nResults: {successful_loads} successful, {failed_loads} failed")
    return successful_loads, failed_loads

if __name__ == "__main__":
    successful, failed = test_all_maps_metadata()
    print(f"\n📊 Success rate: {successful}/{successful + failed} ({100 * successful / (successful + failed):.1f}%)")