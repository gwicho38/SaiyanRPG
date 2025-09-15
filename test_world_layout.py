#!/usr/bin/env python3
"""
Test and visualize the new intelligent world layout
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_world_layout():
    """Test and visualize world layout"""
    print("🗺️  Testing Intelligent World Layout")
    print("=" * 60)
    
    try:
        from saiyanquest.gta_world_streamer import GTAWorldStreamer
        
        # Create world streamer (this will run our intelligent positioning)
        world = GTAWorldStreamer()
        
        print(f"✅ World created with intelligent layout")
        print(f"   Total maps: {len(world.maps_metadata)}")
        print(f"   World chunks: {len(world.world_tiles)}")
        
        # Analyze the layout
        towns = []
        routes = []
        indoor = []
        other = []
        
        for map_name, map_data in world.maps_metadata.items():
            map_type = map_data.get('type', 'unknown')
            pos_x, pos_y = map_data['position']
            
            if 'city' in map_name.lower() or 'town' in map_name.lower():
                towns.append((map_name, pos_x, pos_y, map_type))
            elif map_type == 'route':
                routes.append((map_name, pos_x, pos_y, map_type))
            elif map_type == 'indoor':
                indoor.append((map_name, pos_x, pos_y, map_type))
            else:
                other.append((map_name, pos_x, pos_y, map_type))
        
        print(f"\n📊 World Layout Analysis:")
        print(f"   🏘️  Towns/Cities: {len(towns)}")
        print(f"   🛣️  Routes: {len(routes)}")  
        print(f"   🏠 Indoor areas: {len(indoor)}")
        print(f"   🌍 Other areas: {len(other)}")
        
        print(f"\n🏘️  Major Towns/Cities (showing top 10):")
        for i, (name, x, y, type_) in enumerate(towns[:10]):
            print(f"   {i+1:2d}. {name:25s} at ({x:4.0f}, {y:4.0f}) - {type_}")
        
        print(f"\n🛣️  Route Connections (showing first 10):")
        for i, (name, x, y, type_) in enumerate(routes[:10]):
            print(f"   {i+1:2d}. {name:25s} at ({x:4.0f}, {y:4.0f}) - {type_}")
        
        # Check hub distribution
        print(f"\n🎯 Hub Analysis:")
        world_center_x = world.world_width // 2
        world_center_y = world.world_height // 2
        
        hubs = {
            'Northwest': (world_center_x - 2000, world_center_y - 2000),
            'Northeast': (world_center_x + 2000, world_center_y - 2000),
            'Center': (world_center_x, world_center_y),
            'Southwest': (world_center_x - 2000, world_center_y + 2000),
            'Southeast': (world_center_x + 2000, world_center_y + 2000),
        }
        
        for hub_name, (hub_x, hub_y) in hubs.items():
            nearby_towns = 0
            nearby_routes = 0
            for name, x, y, type_ in towns:
                distance = ((x - hub_x)**2 + (y - hub_y)**2)**0.5
                if distance < 1000:  # Within 1000 units
                    nearby_towns += 1
            
            for name, x, y, type_ in routes:
                distance = ((x - hub_x)**2 + (y - hub_y)**2)**0.5
                if distance < 1500:  # Within 1500 units
                    nearby_routes += 1
                    
            print(f"   {hub_name:10s}: {nearby_towns} towns, {nearby_routes} routes nearby")
        
        print(f"\n✅ World layout analysis completed!")
        return True
        
    except Exception as e:
        print(f"❌ World layout test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_world_layout()
    sys.exit(0 if success else 1)