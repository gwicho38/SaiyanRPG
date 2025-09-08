#!/usr/bin/env python3
"""Audit all TMX maps for missing tileset images."""

import pygame
from pathlib import Path
from saiyanquest.saiyanquest_map_renderer import SaiyanQuestMapRenderer

def audit_missing_textures():
    """Check all TMX maps for missing tileset images"""
    print("🔍 Auditing TMX maps for missing tileset images...")
    
    # Initialize pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Create renderer
    renderer = SaiyanQuestMapRenderer()
    mod_path = Path("mods/saiyanquest")
    tilesets_path = mod_path / "gfx/tilesets"
    
    # Get all maps
    maps = renderer.discover_all_maps()
    print(f"📊 Checking {len(maps)} maps...")
    
    missing_images = {}
    maps_with_missing = []
    total_missing = 0
    
    for i, map_name in enumerate(maps[:50]):  # Check first 50 maps
        if i % 10 == 0:
            print(f"   Progress: {i}/{len(maps[:50])}")
        
        tmx_map = renderer.load_map(map_name)
        if not tmx_map:
            continue
            
        map_missing = []
        for tileset in tmx_map.tilesets:
            if hasattr(tileset, 'image') and tileset.image:
                image_path = tilesets_path / tileset.image
                if not image_path.exists():
                    missing_info = f"{tileset.name} -> {tileset.image}"
                    map_missing.append(missing_info)
                    
                    if tileset.image not in missing_images:
                        missing_images[tileset.image] = []
                    missing_images[tileset.image].append(map_name)
                    total_missing += 1
        
        if map_missing:
            maps_with_missing.append((map_name, map_missing))
    
    print(f"\n📋 AUDIT RESULTS:")
    print(f"   Maps checked: {min(50, len(maps))}")
    print(f"   Maps with missing images: {len(maps_with_missing)}")
    print(f"   Total missing references: {total_missing}")
    print(f"   Unique missing images: {len(missing_images)}")
    
    if missing_images:
        print(f"\n❌ MISSING TILESET IMAGES:")
        for image_file, map_names in missing_images.items():
            print(f"   {image_file}")
            print(f"     Referenced by: {', '.join(map_names[:5])}")
            if len(map_names) > 5:
                print(f"     ... and {len(map_names) - 5} more maps")
    
    if maps_with_missing:
        print(f"\n🗺️ MAPS WITH MISSING IMAGES (first 10):")
        for map_name, missing_list in maps_with_missing[:10]:
            print(f"   {map_name}:")
            for missing in missing_list:
                print(f"     - {missing}")
    
    # Check what tileset images we DO have
    existing_images = list(tilesets_path.glob("*.png"))
    print(f"\n✅ AVAILABLE TILESET IMAGES: {len(existing_images)}")
    
    return len(maps_with_missing), total_missing, len(missing_images)

if __name__ == "__main__":
    maps_affected, total_refs, unique_files = audit_missing_textures()
    
    if total_refs == 0:
        print("\n🎉 NO MISSING TEXTURES FOUND! All tileset images exist.")
    else:
        print(f"\n⚠️ SUMMARY: {maps_affected} maps affected by {unique_files} missing image files")
        print("   This could explain why some maps show no textures.")