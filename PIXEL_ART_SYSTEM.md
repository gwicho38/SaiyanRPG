# SaiyanQuest Pixel Art Map System

## Overview

The Pixel Art Map System brings GBA-style graphics to SaiyanQuest GTA, creating a unique blend of classic pixel art aesthetics with modern open-world gameplay mechanics.

## Features

### 🎨 GBA-Style Graphics
- **16x16 pixel tiles** with 2x scaling for modern displays
- **Pixel-perfect rendering** with no anti-aliasing
- **Limited color palettes** reminiscent of Game Boy Advance
- **Sprite-based assets** for vehicles, characters, and buildings

### 🗺️ Procedural Map Generation
- **City maps**: Urban areas with roads, buildings, and sidewalks
- **Nature maps**: Rural areas with grass, water, and natural features
- **Mixed maps**: Combination of urban and rural elements
- **Collision detection** with tile-based collision system

### 🚗 Dynamic Asset Generation
- **Vehicles**: 7 different types (sedan, sports car, truck, motorcycle, bus, police, taxi)
- **Characters**: 5 different types (civilian, gangster, police, businessman, tourist)
- **Buildings**: 5 different types (house, apartment, office, shop, warehouse)
- **Effects**: 4 different types (explosion, smoke, sparkle, fire)

### 🎬 Animation System
- **Animated tiles** for water, fire, and other effects
- **4-directional sprites** for vehicles and characters
- **Frame-based animations** with configurable timing
- **Smooth interpolation** between animation frames

## Architecture

### Core Components

1. **PixelArtMapSystem** (`pixel_art_map_system.py`)
   - Manages tile-based maps
   - Handles collision detection
   - Renders pixel art tiles
   - Manages animated tiles

2. **GBAAssetGenerator** (`gba_asset_generator.py`)
   - Generates pixel art assets procedurally
   - Creates sprites for different asset types
   - Manages color palettes
   - Saves assets to disk

3. **EnhancedWorldRenderer** (`enhanced_world_renderer.py`)
   - Integrates pixel art maps with GTA systems
   - Manages rendering layers
   - Handles camera and zoom
   - Optimizes rendering performance

4. **GTAPixelIntegration** (`gta_pixel_integration.py`)
   - Integrates pixel art system with existing GTA game
   - Provides enhanced controls
   - Manages world switching
   - Handles debug information

## Usage

### Running the Pixel Art GTA Game

```bash
# Run the pixel art version
python run_pixel_art_gta.py

# Or run the test script
python test_pixel_art_maps.py
```

### Controls

- **WASD/Arrow Keys**: Move player
- **F**: Enter/Exit vehicle
- **Space**: Handbrake
- **Ctrl**: Fire weapon
- **P**: Toggle Pixel Art Mode
- **T**: Switch World Type (city/nature/mixed)
- **L**: Toggle Layer Visibility
- **I**: Show World Info
- **F1**: Toggle Debug Mode
- **ESC**: Exit

### Programmatic Usage

```python
from saiyanquest.pixel_art_map_system import get_pixel_map_system
from saiyanquest.gba_asset_generator import get_asset_generator
from saiyanquest.enhanced_world_renderer import get_enhanced_renderer

# Get the systems
map_system = get_pixel_map_system()
asset_generator = get_asset_generator()
renderer = get_enhanced_renderer()

# Create a procedural map
map_system.create_procedural_map(200, 150, "city")

# Generate assets
assets = asset_generator.generate_all_assets()

# Render the world
renderer.render(screen)
```

## Technical Details

### Tile System
- **Tile Size**: 16x16 pixels
- **Scale Factor**: 2x for modern displays (32x32 effective)
- **Layers**: Background, Collision, Foreground, Decoration
- **Animation**: Frame-based with configurable timing

### Asset Generation
- **Procedural Creation**: Assets are generated programmatically
- **Color Palettes**: Limited palettes for authentic GBA feel
- **Sprite Directions**: 4 directions (north, south, east, west)
- **Animation Frames**: Multiple frames for effects

### Rendering Optimization
- **Visible Tile Culling**: Only renders tiles on screen
- **Chunk-based Loading**: Loads/unloads map chunks as needed
- **Sprite Caching**: Caches rendered sprites for performance
- **Layer Management**: Separate rendering layers for different elements

## File Structure

```
saiyanquest/
├── pixel_art_map_system.py      # Core tile-based map system
├── gba_asset_generator.py       # Procedural asset generation
├── enhanced_world_renderer.py   # Integrated world rendering
├── gta_pixel_integration.py     # GTA game integration
└── ...

test_pixel_art_maps.py           # Test script
run_pixel_art_gta.py             # Main entry point
PIXEL_ART_SYSTEM.md              # This documentation
```

## Performance

### Optimization Features
- **Frustum Culling**: Only renders visible tiles
- **Chunk Streaming**: Loads/unloads map areas dynamically
- **Sprite Caching**: Reuses rendered sprites
- **Layer Culling**: Skips invisible layers

### Performance Metrics
- **Target FPS**: 60 FPS
- **Map Size**: Up to 200x150 tiles (3200x2400 pixels)
- **Asset Count**: 50+ procedurally generated assets
- **Memory Usage**: Optimized for large worlds

## Integration with Existing Systems

The pixel art system integrates seamlessly with existing SaiyanQuest systems:

- **GTA Game Loop**: Uses existing game loop and input handling
- **Vehicle System**: Renders vehicles with pixel art sprites
- **Character System**: Renders characters with pixel art sprites
- **Physics System**: Uses existing collision detection
- **UI System**: Integrates with existing UI elements

## Future Enhancements

### Planned Features
- **Custom Tilesets**: Support for user-created tilesets
- **Map Editor**: Visual map editing tools
- **Asset Import**: Import custom pixel art assets
- **Multiplayer**: Pixel art rendering for multiple players
- **Modding**: Support for pixel art mods

### Performance Improvements
- **GPU Rendering**: Hardware-accelerated tile rendering
- **Compression**: Compressed tile storage
- **Streaming**: Improved world streaming
- **Caching**: Enhanced sprite caching

## Troubleshooting

### Common Issues

1. **Assets not loading**
   - Check that the `gba_generated_assets` directory exists
   - Run the asset generator manually: `python -c "from saiyanquest.gba_asset_generator import get_asset_generator; get_asset_generator().generate_all_assets()"`

2. **Performance issues**
   - Reduce map size in `create_procedural_map()`
   - Disable debug mode (F1)
   - Toggle off unnecessary layers (L key)

3. **Rendering artifacts**
   - Ensure pygame is properly initialized
   - Check that the display mode supports the required resolution

### Debug Information

Enable debug mode (F1) to see:
- Camera position and zoom
- Map size and tile count
- Asset information
- Layer visibility status
- Performance metrics

## Contributing

To contribute to the pixel art system:

1. **Asset Creation**: Add new asset types to `gba_asset_generator.py`
2. **Tile Types**: Add new tile types to `pixel_art_map_system.py`
3. **Rendering**: Enhance rendering in `enhanced_world_renderer.py`
4. **Integration**: Improve integration in `gta_pixel_integration.py`

## License

This pixel art system is part of SaiyanQuest and follows the same GPL-3.0 license.