#!/usr/bin/env python3
"""
Test script for the GTA World Builder
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_world_builder():
    """Test the GTA world builder"""
    print("🌍 Testing GTA World Builder with SaiyanQuest Assets")
    print("=" * 60)
    
    # Change to correct directory
    if not os.path.exists("mods/saiyanquest"):
        print("❌ SaiyanQuest mod directory not found!")
        print("   Make sure you're running this from the project root.")
        return False
    
    try:
        from saiyanquest.gta_world_builder import GTAWorldBuilder, WorldSector
        
        # Create world builder
        builder = GTAWorldBuilder()
        
        # Test asset discovery
        print("\n📁 Discovering assets...")
        builder.discover_all_assets()
        
        print(f"   Found {len(builder.maps)} maps:")
        for i, (name, map_data) in enumerate(list(builder.maps.items())[:10]):
            print(f"     • {name}: {map_data.size[0]}x{map_data.size[1]}px ({map_data.map_type})")
            if i >= 9:
                print(f"     ... and {len(builder.maps)-10} more")
                break
        
        print(f"   Found {len(builder.sprites)} sprites:")
        sprite_counts = {}
        for sprite in builder.sprites.values():
            sprite_counts[sprite.category] = sprite_counts.get(sprite.category, 0) + 1
        for category, count in sprite_counts.items():
            print(f"     • {category}: {count} sprites")
        
        print(f"   Found {len(builder.tilesets)} tilesets")
        
        # Test world layout building
        print("\n🗺️ Building world layout...")
        builder.build_open_world_layout()
        
        for sector, maps in builder.sectors.items():
            if maps:
                print(f"   {sector.value}: {len(maps)} maps")
        
        # Test save functionality
        print("\n💾 Testing save functionality...")
        builder.save_world_data("test_world_data.json")
        
        # Test spawn points
        spawn_points = builder.get_spawn_points()
        print(f"   Generated {len(spawn_points)} spawn points")
        
        print("\n✅ World Builder Test Successful!")
        print(f"   Ready to build a {builder.world_width}x{builder.world_height} world")
        
        return True
        
    except Exception as e:
        print(f"❌ World Builder Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_world():
    """Test the enhanced world system"""
    print("\n🌟 Testing Enhanced World System")
    print("=" * 60)
    
    try:
        from saiyanquest.gta_world_enhanced import GTAWorldEnhanced
        
        # Create enhanced world (without pygame display for testing)
        world = GTAWorldEnhanced(1280, 720)
        
        print(f"   World size: {world.world_width}x{world.world_height}")
        print(f"   Districts: {len(world.districts)}")
        
        for name, district in world.districts.items():
            print(f"     • {name}: {len(district['maps'])} maps")
        
        # Test spawn points
        spawn_points = world.get_spawn_points()
        print(f"   Spawn points: {len(spawn_points)}")
        
        # Test world stats
        stats = world.get_world_stats()
        print(f"   World stats: {stats}")
        
        print("\n✅ Enhanced World Test Successful!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced World Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("SaiyanQuest GTA World Builder Test Suite")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 2
    
    # Test world builder
    if test_world_builder():
        tests_passed += 1
    
    # Test enhanced world
    if test_enhanced_world():
        tests_passed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready to launch GTA mode with real assets!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)