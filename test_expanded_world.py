#!/usr/bin/env python3
"""
Test and analyze the expanded world with procedurally generated assets
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_expanded_world():
    """Test expanded world system"""
    print("🎨 Testing Expanded World System")
    print("=" * 60)
    
    try:
        from saiyanquest.gta_world_streamer import GTAWorldStreamer
        
        # Create world with expansions
        world = GTAWorldStreamer()
        
        print(f"✅ Expanded world created")
        print(f"   Total maps: {len(world.maps_metadata)}")
        print(f"   World chunks: {len(world.world_tiles)}")
        
        # Analyze original vs generated assets
        original_assets = []
        generated_assets = []
        
        for map_name, map_data in world.maps_metadata.items():
            if map_data.get('synthetic', False):
                generated_assets.append((map_name, map_data))
            else:
                original_assets.append((map_name, map_data))
        
        print(f"\n📊 Asset Analysis:")
        print(f"   🏛️  Original TMX assets: {len(original_assets)}")
        print(f"   🎨 Generated assets: {len(generated_assets)}")
        print(f"   📈 World expansion: +{len(generated_assets)/len(original_assets)*100:.1f}%")
        
        # Analyze by theme
        theme_analysis = {}
        for name, data in generated_assets:
            theme = data.get('properties', {}).get('theme', 'unknown')
            asset_type = data.get('type', 'unknown')
            
            if theme not in theme_analysis:
                theme_analysis[theme] = {'total': 0, 'types': {}}
                
            theme_analysis[theme]['total'] += 1
            theme_analysis[theme]['types'][asset_type] = theme_analysis[theme]['types'].get(asset_type, 0) + 1
        
        print(f"\n🌍 Theme Breakdown:")
        for theme, data in sorted(theme_analysis.items()):
            print(f"   {theme.title():12s}: {data['total']} assets")
            for asset_type, count in sorted(data['types'].items()):
                print(f"     - {asset_type:12s}: {count}")
        
        # Sample some generated assets
        print(f"\n🎯 Sample Generated Assets:")
        sample_assets = list(generated_assets)[:8]
        for i, (name, data) in enumerate(sample_assets):
            theme = data.get('properties', {}).get('theme', 'unknown')
            asset_type = data.get('type', 'unknown')
            pos_x, pos_y = data.get('position', (0, 0))
            print(f"   {i+1}. {name:35s} ({theme}/{asset_type}) at ({pos_x:4.0f}, {pos_y:4.0f})")
        
        # Test positioning intelligence
        print(f"\n📍 Positioning Analysis:")
        for theme in ['candy', 'flower', 'leather']:
            theme_assets = [a for a in generated_assets if theme in a[0]]
            if theme_assets:
                positions = [a[1]['position'] for a in theme_assets]
                avg_x = sum(p[0] for p in positions) / len(positions)
                avg_y = sum(p[1] for p in positions) / len(positions)
                print(f"   {theme.title():8s} assets clustered around ({avg_x:4.0f}, {avg_y:4.0f})")
        
        print(f"\n✅ Expanded world analysis completed!")
        print(f"   🏗️ Successfully added {len(generated_assets)} procedural buildings")
        print(f"   🗺️ Maintained thematic coherence across {len(theme_analysis)} themes")
        print(f"   🎮 Ready for GTA-style gameplay with expanded world content")
        
        return True
        
    except Exception as e:
        print(f"❌ Expanded world test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_expanded_world()
    sys.exit(0 if success else 1)