#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA World Builder - Integrates all SaiyanQuest maps and textures into open world

import os
import glob
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pygame
import pytmx
import pyscroll
from pathlib import Path
import random
import math

@dataclass
class MapData:
    """Data for a single map in the world"""
    name: str
    path: str
    tmx_data: Optional[Any] = None
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (0, 0)
    connections: Dict[str, str] = None
    map_type: str = "outdoor"  # outdoor, indoor, dungeon, city
    district: str = "central"
    loaded: bool = False
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = {}

class WorldSector(Enum):
    """Different sectors of the massive open world"""
    GROVE_STREET = "grove_street"  # Starting area, residential
    DOWNTOWN = "downtown"  # City center, shops, missions
    BEACH = "beach"  # Coastal area
    INDUSTRIAL = "industrial"  # Factories, warehouses
    COUNTRYSIDE = "countryside"  # Routes, forests, farms
    MOUNTAINS = "mountains"  # High terrain, caves
    DESERT = "desert"  # Wasteland areas
    ISLANDS = "islands"  # Offshore locations
    UNDERGROUND = "underground"  # Subway, caves, tunnels

@dataclass
class SpriteAsset:
    """Represents a sprite that can be used in the world"""
    name: str
    path: str
    category: str  # npc, vehicle, monster, item, effect
    surface: Optional[pygame.Surface] = None
    frames: List[pygame.Surface] = None
    
    def __post_init__(self):
        if self.frames is None:
            self.frames = []

class GTAWorldBuilder:
    """Builds the massive GTA open world from all SaiyanQuest assets"""
    
    def __init__(self):
        self.maps: Dict[str, MapData] = {}
        self.sprites: Dict[str, SpriteAsset] = {}
        self.tilesets: Dict[str, pygame.Surface] = {}
        
        # World configuration
        self.world_width = 32000  # Massive world - 2000 tiles wide
        self.world_height = 24000  # 1500 tiles tall
        self.tile_size = 16
        
        # Map placement grid (divide world into sectors)
        self.sector_size = 4000  # Each sector is 250x250 tiles
        self.sectors: Dict[WorldSector, List[MapData]] = {
            sector: [] for sector in WorldSector
        }
        
        # Asset directories
        self.mod_path = Path("mods/saiyanquest")
        self.maps_path = self.mod_path / "maps"
        self.gfx_path = self.mod_path / "gfx"
        self.sprites_path = self.gfx_path / "sprites"
        self.tilesets_path = self.gfx_path / "tilesets"
        
        # Map connectivity graph
        self.map_graph: Dict[str, List[str]] = {}
        
        # Loaded resources
        self.composite_surface = None
        self.collision_map = None
        
    def discover_all_assets(self) -> None:
        """Discover all maps, sprites, and tilesets in the game"""
        print("🔍 Discovering all SaiyanQuest assets...")
        
        # Discover maps
        self._discover_maps()
        
        # Discover sprites
        self._discover_sprites()
        
        # Discover tilesets
        self._discover_tilesets()
        
        print(f"📊 Found: {len(self.maps)} maps, {len(self.sprites)} sprites, {len(self.tilesets)} tilesets")
    
    def _discover_maps(self) -> None:
        """Find all TMX map files"""
        map_files = glob.glob(str(self.maps_path / "*.tmx"))
        
        for map_file in map_files:
            map_name = Path(map_file).stem
            
            # Parse basic map info
            try:
                tree = ET.parse(map_file)
                root = tree.getroot()
                
                width = int(root.get('width', 0))
                height = int(root.get('height', 0))
                
                # Get map properties
                map_type = "outdoor"
                properties = root.find('properties')
                if properties is not None:
                    for prop in properties.findall('property'):
                        if prop.get('name') == 'map_type':
                            map_type = prop.get('value', 'outdoor')
                
                # Create map data
                map_data = MapData(
                    name=map_name,
                    path=map_file,
                    size=(width * self.tile_size, height * self.tile_size),
                    map_type=map_type
                )
                
                # Assign to sector based on name/type
                map_data.district = self._determine_sector(map_name, map_type)
                
                self.maps[map_name] = map_data
                
            except Exception as e:
                print(f"  ⚠️ Could not parse {map_name}: {e}")
    
    def _discover_sprites(self) -> None:
        """Find all sprite assets"""
        # Player/NPC sprites
        npc_sprites = glob.glob(str(self.sprites_path / "player" / "*.png"))
        for sprite_file in npc_sprites:
            name = Path(sprite_file).stem
            self.sprites[f"npc_{name}"] = SpriteAsset(
                name=name,
                path=sprite_file,
                category="npc"
            )
        
        # Battle sprites (monsters that can be vehicles/creatures)
        battle_sprites = glob.glob(str(self.sprites_path / "battle" / "*" / "*.png"))
        for sprite_file in battle_sprites[:100]:  # Limit for performance
            name = Path(sprite_file).stem
            folder = Path(sprite_file).parent.name
            
            # Determine if this could be a vehicle
            if any(keyword in name.lower() for keyword in 
                   ['car', 'truck', 'bike', 'copter', 'plane', 'boat', 'mech', 'robot']):
                category = "vehicle"
            else:
                category = "monster"
            
            self.sprites[f"{category}_{name}"] = SpriteAsset(
                name=name,
                path=sprite_file,
                category=category
            )
    
    def _discover_tilesets(self) -> None:
        """Find all tileset images"""
        tileset_files = glob.glob(str(self.tilesets_path / "*.png"))
        
        for tileset_file in tileset_files:
            name = Path(tileset_file).stem
            try:
                surface = pygame.image.load(tileset_file)
                self.tilesets[name] = surface
            except Exception as e:
                print(f"  ⚠️ Could not load tileset {name}: {e}")
    
    def _determine_sector(self, map_name: str, map_type: str) -> str:
        """Determine which world sector a map belongs to"""
        name_lower = map_name.lower()
        
        # Check for specific keywords
        if 'city' in name_lower or 'town' in name_lower:
            return WorldSector.DOWNTOWN.value
        elif 'route' in name_lower or 'path' in name_lower:
            return WorldSector.COUNTRYSIDE.value
        elif 'beach' in name_lower or 'coast' in name_lower:
            return WorldSector.BEACH.value
        elif 'cave' in name_lower or 'tunnel' in name_lower:
            return WorldSector.UNDERGROUND.value
        elif 'mountain' in name_lower or 'peak' in name_lower:
            return WorldSector.MOUNTAINS.value
        elif 'house' in name_lower or 'home' in name_lower:
            return WorldSector.GROVE_STREET.value
        elif 'factory' in name_lower or 'warehouse' in name_lower:
            return WorldSector.INDUSTRIAL.value
        elif 'desert' in name_lower or 'sand' in name_lower:
            return WorldSector.DESERT.value
        elif 'island' in name_lower or 'isle' in name_lower:
            return WorldSector.ISLANDS.value
        else:
            # Default based on map type
            if map_type == "indoor":
                return WorldSector.GROVE_STREET.value
            else:
                return WorldSector.COUNTRYSIDE.value
    
    def build_open_world_layout(self) -> None:
        """Arrange all maps into a massive connected open world"""
        print("🗺️ Building open world layout...")
        
        # Group maps by sector
        for map_name, map_data in self.maps.items():
            sector = WorldSector(map_data.district)
            self.sectors[sector].append(map_data)
        
        # Place sectors in the world
        sector_positions = {
            WorldSector.GROVE_STREET: (1, 1),  # Center-west (starting area)
            WorldSector.DOWNTOWN: (3, 2),       # Center
            WorldSector.BEACH: (5, 1),          # East coast
            WorldSector.INDUSTRIAL: (2, 0),     # North-west
            WorldSector.COUNTRYSIDE: (3, 3),    # South
            WorldSector.MOUNTAINS: (4, 0),      # North-east
            WorldSector.DESERT: (1, 3),         # South-west
            WorldSector.ISLANDS: (6, 2),        # Far east (offshore)
            WorldSector.UNDERGROUND: (3, 4),    # Below main map
        }
        
        # Place maps within each sector
        for sector, maps in self.sectors.items():
            if not maps:
                continue
            
            sector_pos = sector_positions.get(sector, (0, 0))
            base_x = sector_pos[0] * self.sector_size
            base_y = sector_pos[1] * self.sector_size
            
            # Arrange maps in a grid within the sector
            cols = max(1, int(math.sqrt(len(maps))))
            
            for i, map_data in enumerate(maps):
                row = i // cols
                col = i % cols
                
                # Calculate position with some spacing
                x = base_x + (col * 1000) + random.randint(-100, 100)
                y = base_y + (row * 800) + random.randint(-100, 100)
                
                map_data.position = (x, y)
                
                print(f"  📍 Placed {map_data.name} at ({x}, {y}) in {sector.value}")
        
        # Build connectivity graph
        self._build_connectivity()
    
    def _build_connectivity(self) -> None:
        """Build connections between adjacent maps"""
        print("🔗 Building map connectivity...")
        
        # For each map, find nearby maps and create connections
        for name1, map1 in self.maps.items():
            self.map_graph[name1] = []
            
            for name2, map2 in self.maps.items():
                if name1 == name2:
                    continue
                
                # Check if maps are adjacent
                dist = math.sqrt(
                    (map1.position[0] - map2.position[0])**2 +
                    (map1.position[1] - map2.position[1])**2
                )
                
                # Connect if within reasonable distance
                if dist < 1500:  # Adjacent maps
                    self.map_graph[name1].append(name2)
                    
                    # Determine connection direction
                    dx = map2.position[0] - map1.position[0]
                    dy = map2.position[1] - map1.position[1]
                    
                    if abs(dx) > abs(dy):
                        direction = "east" if dx > 0 else "west"
                    else:
                        direction = "south" if dy > 0 else "north"
                    
                    map1.connections[direction] = name2
    
    def create_composite_world_map(self, screen: pygame.Surface) -> pygame.Surface:
        """Create a composite surface of the entire world"""
        print("🎨 Creating composite world map...")
        
        # Create massive surface for the world
        self.composite_surface = pygame.Surface((self.world_width, self.world_height))
        
        # Fill with base terrain (grass)
        base_color = (34, 139, 34)  # Forest green
        self.composite_surface.fill(base_color)
        
        # Draw ocean areas
        self._draw_ocean_areas()
        
        # Draw roads connecting sectors
        self._draw_road_network()
        
        # Place each map on the composite
        maps_loaded = 0
        for map_name, map_data in self.maps.items():
            if maps_loaded < 50:  # Limit for performance
                self._render_map_to_composite(map_data)
                maps_loaded += 1
        
        print(f"  ✅ Composite map created: {self.world_width}x{self.world_height} pixels")
        return self.composite_surface
    
    def _draw_ocean_areas(self) -> None:
        """Draw ocean/water areas on the world"""
        ocean_color = (0, 119, 190)  # Ocean blue
        
        # East coast ocean
        ocean_rect = pygame.Rect(self.world_width - 4000, 0, 4000, self.world_height)
        pygame.draw.rect(self.composite_surface, ocean_color, ocean_rect)
        
        # Some lakes and rivers
        for _ in range(10):
            lake_x = random.randint(1000, self.world_width - 2000)
            lake_y = random.randint(1000, self.world_height - 2000)
            lake_w = random.randint(200, 800)
            lake_h = random.randint(200, 600)
            pygame.draw.ellipse(self.composite_surface, ocean_color,
                              (lake_x, lake_y, lake_w, lake_h))
    
    def _draw_road_network(self) -> None:
        """Draw major highways connecting sectors"""
        road_color = (64, 64, 64)  # Dark gray
        road_width = 40
        
        # Major highways
        highways = [
            # East-West highway
            ((0, self.world_height // 2), (self.world_width, self.world_height // 2)),
            # North-South highway
            ((self.world_width // 2, 0), (self.world_width // 2, self.world_height)),
            # Coastal highway
            ((self.world_width - 4200, 100), (self.world_width - 4200, self.world_height - 100)),
            # Ring road around downtown
            ((12000, 8000), (12000, 12000)),
            ((12000, 12000), (16000, 12000)),
            ((16000, 12000), (16000, 8000)),
            ((16000, 8000), (12000, 8000)),
        ]
        
        for start, end in highways:
            pygame.draw.line(self.composite_surface, road_color, start, end, road_width)
        
        # Secondary roads
        for _ in range(20):
            start_x = random.randint(0, self.world_width)
            start_y = random.randint(0, self.world_height)
            end_x = start_x + random.randint(-2000, 2000)
            end_y = start_y + random.randint(-2000, 2000)
            
            end_x = max(0, min(end_x, self.world_width))
            end_y = max(0, min(end_y, self.world_height))
            
            pygame.draw.line(self.composite_surface, road_color,
                           (start_x, start_y), (end_x, end_y), road_width // 2)
    
    def _render_map_to_composite(self, map_data: MapData) -> None:
        """Render a single map to the composite surface"""
        try:
            # Try to load the map with pytmx
            if not map_data.loaded:
                map_data.tmx_data = pytmx.load_pygame(map_data.path, pixelalpha=True)
                map_data.loaded = True
            
            # Create a surface for this map
            map_surface = pygame.Surface(map_data.size)
            
            # Render all visible layers
            if map_data.tmx_data:
                for layer in map_data.tmx_data.visible_layers:
                    if isinstance(layer, pytmx.TiledTileLayer):
                        for x, y, gid in layer:
                            tile = map_data.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                map_surface.blit(tile, (x * self.tile_size, y * self.tile_size))
            
            # Blit to composite at map position
            self.composite_surface.blit(map_surface, map_data.position)
            
        except Exception as e:
            # If can't load, just draw a placeholder
            placeholder_color = (100, 100, 100)
            rect = pygame.Rect(map_data.position[0], map_data.position[1],
                              map_data.size[0], map_data.size[1])
            pygame.draw.rect(self.composite_surface, placeholder_color, rect)
    
    def populate_world_with_sprites(self) -> List[Dict[str, Any]]:
        """Populate the world with NPCs, vehicles, and objects using existing sprites"""
        print("👥 Populating world with sprites...")
        
        entities = []
        
        # Place NPCs in residential/city areas
        npc_sprites = [s for s in self.sprites.values() if s.category == "npc"]
        for i in range(min(200, len(npc_sprites))):  # Place up to 200 NPCs
            sprite = random.choice(npc_sprites)
            
            # Place in appropriate sector
            sector = random.choice([WorldSector.GROVE_STREET, WorldSector.DOWNTOWN])
            sector_maps = self.sectors[sector]
            
            if sector_maps:
                map_data = random.choice(sector_maps)
                x = map_data.position[0] + random.randint(0, map_data.size[0])
                y = map_data.position[1] + random.randint(0, map_data.size[1])
                
                entities.append({
                    'type': 'npc',
                    'sprite': sprite.name,
                    'position': (x, y),
                    'behavior': random.choice(['wander', 'patrol', 'stationary', 'shop']),
                    'dialogue': f"Hello, I'm {sprite.name.replace('_', ' ').title()}!"
                })
        
        # Place vehicles on roads and parking areas
        vehicle_sprites = [s for s in self.sprites.values() if s.category == "vehicle"]
        for i in range(min(100, len(vehicle_sprites))):  # Place up to 100 vehicles
            sprite = random.choice(vehicle_sprites) if vehicle_sprites else None
            
            if sprite:
                # Place near roads
                x = random.randint(0, self.world_width)
                y = random.randint(0, self.world_height)
                
                # Snap to road grid
                x = (x // 100) * 100 + 50
                y = (y // 100) * 100 + 50
                
                entities.append({
                    'type': 'vehicle',
                    'sprite': sprite.name,
                    'position': (x, y),
                    'parked': random.random() > 0.3,  # 70% parked
                    'speed': random.randint(30, 120)
                })
        
        # Place monsters in wild areas
        monster_sprites = [s for s in self.sprites.values() if s.category == "monster"]
        for i in range(min(150, len(monster_sprites))):  # Place up to 150 monsters
            sprite = random.choice(monster_sprites)
            
            # Place in wild sectors
            sector = random.choice([WorldSector.COUNTRYSIDE, WorldSector.MOUNTAINS, 
                                   WorldSector.DESERT])
            sector_maps = self.sectors[sector]
            
            if sector_maps:
                map_data = random.choice(sector_maps) if sector_maps else None
                if map_data:
                    x = map_data.position[0] + random.randint(0, map_data.size[0])
                    y = map_data.position[1] + random.randint(0, map_data.size[1])
                    
                    entities.append({
                        'type': 'monster',
                        'sprite': sprite.name,
                        'position': (x, y),
                        'level': random.randint(1, 50),
                        'aggressive': random.random() > 0.7
                    })
        
        print(f"  ✅ Placed {len(entities)} entities in the world")
        return entities
    
    def generate_collision_map(self) -> None:
        """Generate collision data for the entire world"""
        print("🚧 Generating collision map...")
        
        # Create collision grid (1 bit per tile)
        grid_width = self.world_width // self.tile_size
        grid_height = self.world_height // self.tile_size
        
        self.collision_map = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Add collisions from loaded maps
        for map_name, map_data in self.maps.items():
            if map_data.tmx_data:
                # Get collision objects from TMX
                for obj in map_data.tmx_data.objects:
                    if obj.type == "collision":
                        # Convert to world coordinates
                        world_x = map_data.position[0] + obj.x
                        world_y = map_data.position[1] + obj.y
                        
                        # Mark tiles as collision
                        start_tile_x = int(world_x // self.tile_size)
                        start_tile_y = int(world_y // self.tile_size)
                        end_tile_x = int((world_x + obj.width) // self.tile_size)
                        end_tile_y = int((world_y + obj.height) // self.tile_size)
                        
                        for ty in range(start_tile_y, min(end_tile_y + 1, grid_height)):
                            for tx in range(start_tile_x, min(end_tile_x + 1, grid_width)):
                                if 0 <= tx < grid_width and 0 <= ty < grid_height:
                                    self.collision_map[ty][tx] = 1
        
        print(f"  ✅ Collision map generated: {grid_width}x{grid_height} tiles")
    
    def get_spawn_points(self) -> List[Tuple[int, int]]:
        """Get player spawn points across the world"""
        spawn_points = []
        
        # Primary spawn in Grove Street (player house)
        if "player_house" in self.maps:
            house = self.maps["player_house"]
            spawn_points.append((house.position[0] + 100, house.position[1] + 100))
        
        # Hospital spawns
        for map_name, map_data in self.maps.items():
            if "hospital" in map_name or "healing" in map_name:
                spawn_points.append((map_data.position[0] + 50, map_data.position[1] + 50))
        
        # Safe house spawns
        for map_name, map_data in self.maps.items():
            if "house" in map_name or "home" in map_name:
                spawn_points.append((map_data.position[0] + 50, map_data.position[1] + 50))
        
        # Default spawn if no specific points found
        if not spawn_points:
            spawn_points.append((self.world_width // 4, self.world_height // 2))
        
        return spawn_points
    
    def save_world_data(self, filename: str = "gta_world_data.json") -> None:
        """Save world configuration to file"""
        print(f"💾 Saving world data to {filename}...")
        
        world_data = {
            'world_size': (self.world_width, self.world_height),
            'tile_size': self.tile_size,
            'maps': {
                name: {
                    'position': map_data.position,
                    'size': map_data.size,
                    'type': map_data.map_type,
                    'district': map_data.district,
                    'connections': map_data.connections
                }
                for name, map_data in self.maps.items()
            },
            'sectors': {
                sector.value: [m.name for m in maps]
                for sector, maps in self.sectors.items()
            },
            'spawn_points': self.get_spawn_points(),
            'total_maps': len(self.maps),
            'total_sprites': len(self.sprites)
        }
        
        with open(filename, 'w') as f:
            json.dump(world_data, f, indent=2)
        
        print(f"  ✅ World data saved!")

def build_gta_world():
    """Main function to build the GTA world from SaiyanQuest assets"""
    print("🚀 Starting GTA World Builder...")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("SaiyanQuest GTA - World Builder")
    
    # Create world builder
    builder = GTAWorldBuilder()
    
    # Discover all assets
    builder.discover_all_assets()
    
    # Build world layout
    builder.build_open_world_layout()
    
    # Create composite map
    composite_map = builder.create_composite_world_map(screen)
    
    # Populate with entities
    entities = builder.populate_world_with_sprites()
    
    # Generate collisions
    builder.generate_collision_map()
    
    # Save world data
    builder.save_world_data()
    
    print("\n" + "=" * 50)
    print("✅ GTA World Building Complete!")
    print(f"📊 World Statistics:")
    print(f"  • World Size: {builder.world_width}x{builder.world_height} pixels")
    print(f"  • Maps Integrated: {len(builder.maps)}")
    print(f"  • Sprites Available: {len(builder.sprites)}")
    print(f"  • Entities Placed: {len(entities)}")
    print(f"  • Spawn Points: {len(builder.get_spawn_points())}")
    
    return builder

if __name__ == "__main__":
    builder = build_gta_world()
    
    # Keep window open to show result
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Show a preview (scaled down)
        if builder.composite_surface:
            preview = pygame.transform.scale(builder.composite_surface, (1280, 720))
            screen = pygame.display.get_surface()
            screen.blit(preview, (0, 0))
            pygame.display.flip()
        
        clock.tick(30)
    
    pygame.quit()