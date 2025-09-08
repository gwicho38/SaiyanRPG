#!/usr/bin/env python3
"""Test world streamer discovery like the integration test does."""

import pygame
from saiyanquest.gta_world_streamer import GTAWorldStreamer

def test_world_discovery():
    """Test world discovery like in integration test"""
    print("Testing world discovery (without pygame init)...")
    
    # Create world streamer like the integration test does
    world_streamer = GTAWorldStreamer()
    
    print(f"Maps metadata: {len(world_streamer.maps_metadata)}")
    
    if world_streamer.maps_metadata:
        print("\nFirst few maps:")
        for i, (name, data) in enumerate(list(world_streamer.maps_metadata.items())[:5]):
            print(f"  {i+1}. {name}: {data['size']}")
    else:
        print("No maps found!")

def test_with_pygame():
    """Test world discovery with pygame init"""
    print("\nTesting world discovery (with pygame init)...")
    
    # Initialize pygame first
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Create world streamer
    world_streamer = GTAWorldStreamer()
    
    print(f"Maps metadata: {len(world_streamer.maps_metadata)}")
    
    if world_streamer.maps_metadata:
        print("\nFirst few maps:")
        for i, (name, data) in enumerate(list(world_streamer.maps_metadata.items())[:5]):
            print(f"  {i+1}. {name}: {data['size']}")

if __name__ == "__main__":
    # First test without pygame (like integration test)
    test_world_discovery()
    
    # Then test with pygame
    test_with_pygame()