#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# 3D World System with Multiple Layers and Advanced Collision Detection

import math
import struct
import time
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager, CollisionCategory


class BlockType(Enum):
    """Types of world blocks"""
    EMPTY = 0
    SOLID = 1
    WATER = 2
    BUILDING = 3
    ROAD = 4
    GRASS = 5
    SAND = 6
    ROCK = 7
    BRIDGE = 8
    RAILWAY = 9
    SPECIAL = 10


class DistrictType(Enum):
    """Types of districts"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    DOWNTOWN = "downtown"
    SUBURBS = "suburbs"
    WATERFRONT = "waterfront"
    AIRPORT = "airport"
    PORT = "port"


@dataclass
class MapBlockInfo:
    """Information about a world block"""
    block_type: BlockType
    height: float
    water_level: float
    collision_enabled: bool
    walkable: bool
    driveable: bool
    flyable: bool
    district_id: int
    properties: Dict[str, Any]


@dataclass
class District:
    """A district in the world"""
    district_id: int
    name: str
    district_type: DistrictType
    bounds: Tuple[int, int, int, int]  # min_x, min_y, max_x, max_y
    center: Tuple[float, float]
    population_density: float
    crime_level: float
    police_presence: float
    spawn_points: List[Tuple[float, float]]
    special_properties: Dict[str, Any]


@dataclass
class NavigationSector:
    """Navigation sector for pathfinding"""
    sector_id: int
    bounds: Tuple[int, int, int, int]
    connections: List[int]  # Connected sector IDs
    center: Tuple[float, float]
    is_passable: bool
    movement_cost: float


class World3DSystem:
    """3D world system with multiple layers and advanced features"""
    
    def __init__(self, width: int = 1000, height: int = 1000, layers: int = 3):
        self.width = width
        self.height = height
        self.layers = layers
        
        # 3D tile array: [layer][y][x]
        self.map_tiles: List[List[List[MapBlockInfo]]] = [
            [[MapBlockInfo(
                block_type=BlockType.EMPTY,
                height=0.0,
                water_level=0.0,
                collision_enabled=False,
                walkable=True,
                driveable=True,
                flyable=True,
                district_id=0,
                properties={}
            ) for x in range(width)] for y in range(height)] for layer in range(layers)
        ]
        
        # Districts
        self.districts: Dict[int, District] = {}
        self.next_district_id = 1
        
        # Navigation sectors
        self.navigation_sectors: Dict[int, NavigationSector] = {}
        self.sector_size = 50  # 50x50 tiles per sector
        self.next_sector_id = 1
        
        # World properties
        self.water_level = 0.0
        self.time_of_day = 12.0  # Hours (0-24)
        self.weather = "clear"
        self.temperature = 20.0  # Celsius
        
        # Collision detection
        self.collision_cache: Dict[Tuple[int, int, int], bool] = {}
        self.cache_timeout = 1.0  # seconds
        
        print(f"🌍 World3DSystem initialized: {width}x{height}x{layers}")
    
    def load_map_data(self, filename: str) -> bool:
        """Load compressed map data from file"""
        try:
            with open(filename, 'rb') as f:
                # Read header
                header = struct.unpack('<4sIIII', f.read(20))
                magic, version, map_width, map_height, map_layers = header
                
                if magic != b'MAP3':
                    print(f"❌ Invalid map file format: {filename}")
                    return False
                
                # Resize world if needed
                if map_width != self.width or map_height != self.height or map_layers != self.layers:
                    self._resize_world(map_width, map_height, map_layers)
                
                # Read tile data
                for layer in range(map_layers):
                    for y in range(map_height):
                        for x in range(map_width):
                            tile_data = struct.unpack('<BffffBBBB', f.read(17))
                            block_type, height, water_level, prop1, prop2, collision, walkable, driveable, flyable = tile_data
                            
                            self.map_tiles[layer][y][x] = MapBlockInfo(
                                block_type=BlockType(block_type),
                                height=height,
                                water_level=water_level,
                                collision_enabled=bool(collision),
                                walkable=bool(walkable),
                                driveable=bool(driveable),
                                flyable=bool(flyable),
                                district_id=0,  # Will be set later
                                properties={'prop1': prop1, 'prop2': prop2}
                            )
                
                # Read districts
                district_count = struct.unpack('<I', f.read(4))[0]
                for _ in range(district_count):
                    district_data = struct.unpack('<I32sBffffffff', f.read(57))
                    district_id, name_bytes, district_type, min_x, min_y, max_x, max_y, center_x, center_y, pop_density, crime_level = district_data
                    
                    name = name_bytes.decode('utf-8').rstrip('\x00')
                    
                    district = District(
                        district_id=district_id,
                        name=name,
                        district_type=DistrictType(district_type),
                        bounds=(int(min_x), int(min_y), int(max_x), int(max_y)),
                        center=(center_x, center_y),
                        population_density=pop_density,
                        crime_level=crime_level,
                        police_presence=0.0,
                        spawn_points=[],
                        special_properties={}
                    )
                    
                    self.districts[district_id] = district
                
                print(f"✅ Loaded map data from {filename}")
                return True
                
        except Exception as e:
            print(f"❌ Error loading map data: {e}")
            return False
    
    def save_map_data(self, filename: str) -> bool:
        """Save compressed map data to file"""
        try:
            with open(filename, 'wb') as f:
                # Write header
                header = struct.pack('<4sIIII', b'MAP3', 1, self.width, self.height, self.layers)
                f.write(header)
                
                # Write tile data
                for layer in range(self.layers):
                    for y in range(self.height):
                        for x in range(self.width):
                            tile = self.map_tiles[layer][y][x]
                            tile_data = struct.pack('<BffffBBBB',
                                tile.block_type.value,
                                tile.height,
                                tile.water_level,
                                tile.properties.get('prop1', 0.0),
                                tile.properties.get('prop2', 0.0),
                                int(tile.collision_enabled),
                                int(tile.walkable),
                                int(tile.driveable),
                                int(tile.flyable)
                            )
                            f.write(tile_data)
                
                # Write districts
                district_data = struct.pack('<I', len(self.districts))
                f.write(district_data)
                
                for district in self.districts.values():
                    name_bytes = district.name.encode('utf-8')[:32].ljust(32, b'\x00')
                    district_data = struct.pack('<I32sBffffffff',
                        district.district_id,
                        name_bytes,
                        district.district_type.value,
                        district.bounds[0], district.bounds[1],
                        district.bounds[2], district.bounds[3],
                        district.center[0], district.center[1],
                        district.population_density,
                        district.crime_level
                    )
                    f.write(district_data)
                
                print(f"✅ Saved map data to {filename}")
                return True
                
        except Exception as e:
            print(f"❌ Error saving map data: {e}")
            return False
    
    def _resize_world(self, new_width: int, new_height: int, new_layers: int) -> None:
        """Resize the world"""
        self.width = new_width
        self.height = new_height
        self.layers = new_layers
        
        # Create new tile array
        new_tiles = [
            [[MapBlockInfo(
                block_type=BlockType.EMPTY,
                height=0.0,
                water_level=0.0,
                collision_enabled=False,
                walkable=True,
                driveable=True,
                flyable=True,
                district_id=0,
                properties={}
            ) for x in range(new_width)] for y in range(new_height)] for layer in range(new_layers)
        ]
        
        # Copy existing data
        for layer in range(min(self.layers, new_layers)):
            for y in range(min(self.height, new_height)):
                for x in range(min(self.width, new_width)):
                    new_tiles[layer][y][x] = self.map_tiles[layer][y][x]
        
        self.map_tiles = new_tiles
        print(f"🌍 Resized world to {new_width}x{new_height}x{new_layers}")
    
    def get_block_info(self, x: int, y: int, layer: int = 0) -> Optional[MapBlockInfo]:
        """Get block information at coordinates"""
        if not self._is_valid_coordinate(x, y, layer):
            return None
        
        return self.map_tiles[layer][y][x]
    
    def set_block_info(self, x: int, y: int, layer: int, block_info: MapBlockInfo) -> None:
        """Set block information at coordinates"""
        if not self._is_valid_coordinate(x, y, layer):
            return
        
        self.map_tiles[layer][y][x] = block_info
        
        # Clear collision cache for this position
        cache_key = (x, y, layer)
        if cache_key in self.collision_cache:
            del self.collision_cache[cache_key]
    
    def _is_valid_coordinate(self, x: int, y: int, layer: int) -> bool:
        """Check if coordinates are valid"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                0 <= layer < self.layers)
    
    def trace_segment_2d(self, start: Tuple[float, float], end: Tuple[float, float], 
                        layer: int = 0) -> Optional[Tuple[float, float, MapBlockInfo]]:
        """Trace a 2D line segment and return collision info"""
        # Convert world coordinates to tile coordinates
        start_x, start_y = start
        end_x, end_y = end
        
        # Calculate direction and distance
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return None
        
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Step along the line
        step_size = 0.5  # Half tile size for accuracy
        steps = int(distance / step_size) + 1
        
        for i in range(steps):
            t = i * step_size / distance
            if t > 1.0:
                t = 1.0
            
            # Current position
            current_x = start_x + dx * t * distance
            current_y = start_y + dy * t * distance
            
            # Convert to tile coordinates
            tile_x = int(current_x)
            tile_y = int(current_y)
            
            # Check collision
            block_info = self.get_block_info(tile_x, tile_y, layer)
            if block_info and block_info.collision_enabled:
                return (current_x, current_y, block_info)
        
        return None
    
    def is_position_walkable(self, x: float, y: float, layer: int = 0) -> bool:
        """Check if a position is walkable"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, layer)
        
        if not block_info:
            return False
        
        return block_info.walkable
    
    def is_position_driveable(self, x: float, y: float, layer: int = 0) -> bool:
        """Check if a position is driveable"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, layer)
        
        if not block_info:
            return False
        
        return block_info.driveable
    
    def is_position_flyable(self, x: float, y: float, layer: int = 0) -> bool:
        """Check if a position is flyable"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, layer)
        
        if not block_info:
            return False
        
        return block_info.flyable
    
    def get_height_at_position(self, x: float, y: float, layer: int = 0) -> float:
        """Get height at a position"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, layer)
        
        if not block_info:
            return 0.0
        
        return block_info.height
    
    def get_water_level_at_position(self, x: float, y: float, layer: int = 0) -> float:
        """Get water level at a position"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, layer)
        
        if not block_info:
            return 0.0
        
        return block_info.water_level
    
    def create_district(self, name: str, district_type: DistrictType, 
                       bounds: Tuple[int, int, int, int]) -> int:
        """Create a new district"""
        district_id = self.next_district_id
        self.next_district_id += 1
        
        min_x, min_y, max_x, max_y = bounds
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        
        district = District(
            district_id=district_id,
            name=name,
            district_type=district_type,
            bounds=bounds,
            center=(center_x, center_y),
            population_density=0.5,
            crime_level=0.3,
            police_presence=0.2,
            spawn_points=[],
            special_properties={}
        )
        
        self.districts[district_id] = district
        
        # Update block district IDs
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                for layer in range(self.layers):
                    block_info = self.get_block_info(x, y, layer)
                    if block_info:
                        block_info.district_id = district_id
        
        print(f"🌍 Created district '{name}' ({district_type.value}) with ID {district_id}")
        return district_id
    
    def get_district_at_position(self, x: float, y: float) -> Optional[District]:
        """Get district at a position"""
        tile_x, tile_y = int(x), int(y)
        block_info = self.get_block_info(tile_x, tile_y, 0)
        
        if not block_info:
            return None
        
        return self.districts.get(block_info.district_id)
    
    def generate_navigation_sectors(self) -> None:
        """Generate navigation sectors for pathfinding"""
        self.navigation_sectors.clear()
        self.next_sector_id = 1
        
        sectors_x = (self.width + self.sector_size - 1) // self.sector_size
        sectors_y = (self.height + self.sector_size - 1) // self.sector_size
        
        for sector_y in range(sectors_y):
            for sector_x in range(sectors_x):
                sector_id = self.next_sector_id
                self.next_sector_id += 1
                
                # Calculate sector bounds
                min_x = sector_x * self.sector_size
                min_y = sector_y * self.sector_size
                max_x = min(min_x + self.sector_size - 1, self.width - 1)
                max_y = min(min_y + self.sector_size - 1, self.height - 1)
                
                # Calculate sector center
                center_x = (min_x + max_x) / 2.0
                center_y = (min_y + max_y) / 2.0
                
                # Check if sector is passable
                is_passable = self._is_sector_passable(min_x, min_y, max_x, max_y)
                
                # Calculate movement cost
                movement_cost = self._calculate_sector_movement_cost(min_x, min_y, max_x, max_y)
                
                sector = NavigationSector(
                    sector_id=sector_id,
                    bounds=(min_x, min_y, max_x, max_y),
                    connections=[],
                    center=(center_x, center_y),
                    is_passable=is_passable,
                    movement_cost=movement_cost
                )
                
                self.navigation_sectors[sector_id] = sector
        
        # Calculate sector connections
        self._calculate_sector_connections()
        
        print(f"🌍 Generated {len(self.navigation_sectors)} navigation sectors")
    
    def _is_sector_passable(self, min_x: int, min_y: int, max_x: int, max_y: int) -> bool:
        """Check if a sector is passable"""
        walkable_count = 0
        total_count = 0
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                block_info = self.get_block_info(x, y, 0)
                if block_info:
                    total_count += 1
                    if block_info.walkable:
                        walkable_count += 1
        
        # Sector is passable if more than 50% is walkable
        return walkable_count > total_count * 0.5 if total_count > 0 else False
    
    def _calculate_sector_movement_cost(self, min_x: int, min_y: int, max_x: int, max_y: int) -> float:
        """Calculate movement cost for a sector"""
        total_cost = 0.0
        count = 0
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                block_info = self.get_block_info(x, y, 0)
                if block_info:
                    count += 1
                    # Different block types have different movement costs
                    if block_info.block_type == BlockType.ROAD:
                        total_cost += 1.0
                    elif block_info.block_type == BlockType.GRASS:
                        total_cost += 1.5
                    elif block_info.block_type == BlockType.SAND:
                        total_cost += 2.0
                    elif block_info.block_type == BlockType.ROCK:
                        total_cost += 3.0
                    else:
                        total_cost += 1.0
        
        return total_cost / count if count > 0 else 1.0
    
    def _calculate_sector_connections(self) -> None:
        """Calculate connections between sectors"""
        for sector_id, sector in self.navigation_sectors.items():
            connections = []
            
            # Check adjacent sectors
            min_x, min_y, max_x, max_y = sector.bounds
            
            # Check left sector
            if min_x > 0:
                left_sector = self._find_sector_at_position(min_x - 1, min_y)
                if left_sector and left_sector.is_passable:
                    connections.append(left_sector.sector_id)
            
            # Check right sector
            if max_x < self.width - 1:
                right_sector = self._find_sector_at_position(max_x + 1, min_y)
                if right_sector and right_sector.is_passable:
                    connections.append(right_sector.sector_id)
            
            # Check top sector
            if min_y > 0:
                top_sector = self._find_sector_at_position(min_x, min_y - 1)
                if top_sector and top_sector.is_passable:
                    connections.append(top_sector.sector_id)
            
            # Check bottom sector
            if max_y < self.height - 1:
                bottom_sector = self._find_sector_at_position(min_x, max_y + 1)
                if bottom_sector and bottom_sector.is_passable:
                    connections.append(bottom_sector.sector_id)
            
            sector.connections = connections
    
    def _find_sector_at_position(self, x: int, y: int) -> Optional[NavigationSector]:
        """Find sector at a position"""
        for sector in self.navigation_sectors.values():
            min_x, min_y, max_x, max_y = sector.bounds
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return sector
        return None
    
    def find_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Find path between two points using navigation sectors"""
        # Convert world coordinates to tile coordinates
        start_tile = (int(start[0]), int(start[1]))
        end_tile = (int(end[0]), int(end[1]))
        
        # Find start and end sectors
        start_sector = self._find_sector_at_position(start_tile[0], start_tile[1])
        end_sector = self._find_sector_at_position(end_tile[0], end_tile[1])
        
        if not start_sector or not end_sector:
            return []
        
        if start_sector.sector_id == end_sector.sector_id:
            return [start, end]
        
        # Use A* pathfinding between sectors
        path_sectors = self._find_sector_path(start_sector.sector_id, end_sector.sector_id)
        
        if not path_sectors:
            return []
        
        # Convert sector path to world coordinates
        path = [start]
        
        for sector_id in path_sectors[1:-1]:  # Skip start and end sectors
            sector = self.navigation_sectors[sector_id]
            path.append(sector.center)
        
        path.append(end)
        return path
    
    def _find_sector_path(self, start_sector_id: int, end_sector_id: int) -> List[int]:
        """Find path between sectors using A* algorithm"""
        # Simplified A* implementation
        open_set = [start_sector_id]
        came_from = {}
        g_score = {start_sector_id: 0}
        f_score = {start_sector_id: self._heuristic_distance(start_sector_id, end_sector_id)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end_sector_id:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_sector_id)
                return path[::-1]
            
            open_set.remove(current)
            
            # Check neighbors
            current_sector = self.navigation_sectors[current]
            for neighbor_id in current_sector.connections:
                tentative_g_score = g_score[current] + current_sector.movement_cost
                
                if neighbor_id not in g_score or tentative_g_score < g_score[neighbor_id]:
                    came_from[neighbor_id] = current
                    g_score[neighbor_id] = tentative_g_score
                    f_score[neighbor_id] = tentative_g_score + self._heuristic_distance(neighbor_id, end_sector_id)
                    
                    if neighbor_id not in open_set:
                        open_set.append(neighbor_id)
        
        return []
    
    def _heuristic_distance(self, sector_id1: int, sector_id2: int) -> float:
        """Calculate heuristic distance between sectors"""
        sector1 = self.navigation_sectors[sector_id1]
        sector2 = self.navigation_sectors[sector_id2]
        
        dx = sector1.center[0] - sector2.center[0]
        dy = sector1.center[1] - sector2.center[1]
        
        return math.sqrt(dx**2 + dy**2)
    
    def update_world_state(self, dt: float) -> None:
        """Update world state (time, weather, etc.)"""
        # Update time of day
        self.time_of_day += dt * 0.1  # 1 hour per 10 seconds
        if self.time_of_day >= 24.0:
            self.time_of_day -= 24.0
        
        # Update weather (simplified)
        import random
        if random.random() < 0.001:  # 0.1% chance per frame
            weather_options = ["clear", "cloudy", "rainy", "foggy"]
            self.weather = random.choice(weather_options)
        
        # Update temperature based on time and weather
        base_temp = 20.0
        time_factor = math.sin((self.time_of_day - 6) * math.pi / 12) * 10.0  # Daily temperature cycle
        
        weather_factors = {
            "clear": 0.0,
            "cloudy": -2.0,
            "rainy": -5.0,
            "foggy": -1.0
        }
        
        self.temperature = base_temp + time_factor + weather_factors.get(self.weather, 0.0)
    
    def get_world_statistics(self) -> Dict[str, Any]:
        """Get world statistics"""
        block_counts = {}
        district_counts = {}
        
        # Count block types
        for layer in range(self.layers):
            for y in range(self.height):
                for x in range(self.width):
                    block_info = self.map_tiles[layer][y][x]
                    block_type = block_info.block_type.value
                    block_counts[block_type] = block_counts.get(block_type, 0) + 1
        
        # Count district types
        for district in self.districts.values():
            district_type = district.district_type.value
            district_counts[district_type] = district_counts.get(district_type, 0) + 1
        
        return {
            'world_size': f"{self.width}x{self.height}x{self.layers}",
            'total_blocks': self.width * self.height * self.layers,
            'block_types': block_counts,
            'districts': len(self.districts),
            'district_types': district_counts,
            'navigation_sectors': len(self.navigation_sectors),
            'time_of_day': self.time_of_day,
            'weather': self.weather,
            'temperature': self.temperature,
            'water_level': self.water_level
        }


# Test the 3D world system
if __name__ == "__main__":
    print("🧪 Testing World3DSystem...")
    
    # Create world system
    world = World3DSystem(100, 100, 2)
    
    # Create some districts
    residential_id = world.create_district("Downtown", DistrictType.DOWNTOWN, (0, 0, 49, 49))
    commercial_id = world.create_district("Business District", DistrictType.COMMERCIAL, (50, 0, 99, 49))
    
    # Set some blocks
    for y in range(10, 20):
        for x in range(10, 20):
            block_info = MapBlockInfo(
                block_type=BlockType.BUILDING,
                height=10.0,
                water_level=0.0,
                collision_enabled=True,
                walkable=False,
                driveable=False,
                flyable=True,
                district_id=residential_id,
                properties={'height': 10.0}
            )
            world.set_block_info(x, y, 0, block_info)
    
    # Generate navigation sectors
    world.generate_navigation_sectors()
    
    # Test pathfinding
    path = world.find_path((5, 5), (95, 95))
    print(f"Path found with {len(path)} waypoints")
    
    # Test collision detection
    collision = world.trace_segment_2d((5, 5), (15, 15))
    if collision:
        print(f"Collision detected at {collision[0]:.1f}, {collision[1]:.1f}")
    
    # Update world state
    world.update_world_state(1.0)
    
    # Print statistics
    stats = world.get_world_statistics()
    print(f"World statistics: {stats}")
    
    # Save and load test
    world.save_map_data("test_world.map")
    world2 = World3DSystem()
    world2.load_map_data("test_world.map")
    
    print("✅ World3DSystem test completed")