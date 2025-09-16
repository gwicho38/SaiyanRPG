#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# 3D World System with Multiple Layers and Advanced Collision Detection

import math
import struct
import time
import random
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager, CollisionCategory
from .math import Vector3


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


class WorldObjectType(Enum):
    """Types of world objects"""
    STATIC_MESH = "static_mesh"
    DYNAMIC_MESH = "dynamic_mesh"
    CHARACTER = "character"
    VEHICLE = "vehicle"
    BUILDING = "building"
    TERRAIN = "terrain"
    PARTICLE = "particle"
    LIGHT = "light"
    TRIGGER = "trigger"


class RenderLayer(Enum):
    """Rendering layers for 3D objects"""
    SKY = 0
    TERRAIN = 1
    BUILDINGS_LOW = 2
    BUILDINGS_HIGH = 3
    ROADS = 4
    OBJECTS_GROUND = 5
    VEHICLES = 6
    CHARACTERS = 7
    PARTICLES = 8
    EFFECTS = 9
    UI = 10


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


@dataclass
class WorldObject3D:
    """Base class for 3D world objects"""
    position: Vector3
    object_type: WorldObjectType
    render_layer: RenderLayer
    scale: Vector3 = None
    rotation: Vector3 = None
    color: Tuple[int, int, int] = (255, 255, 255)
    visible: bool = True
    collision_enabled: bool = True
    
    def __post_init__(self):
        if self.scale is None:
            self.scale = Vector3(1, 1, 1)
        if self.rotation is None:
            self.rotation = Vector3(0, 0, 0)
    
    def set_position(self, position: Vector3):
        """Set object position"""
        self.position = position
    
    def get_position(self) -> Vector3:
        """Get object position"""
        return self.position
    
    def set_rotation(self, rotation: Vector3):
        """Set object rotation"""
        self.rotation = rotation
    
    def get_rotation(self) -> Vector3:
        """Get object rotation"""
        return self.rotation
    
    def set_scale(self, scale: Vector3):
        """Set object scale"""
        self.scale = scale
    
    def get_scale(self) -> Vector3:
        """Get object scale"""
        return self.scale
    
    def set_visibility(self, visible: bool):
        """Set object visibility"""
        self.visible = visible
    
    def is_visible(self) -> bool:
        """Check if object is visible"""
        return self.visible
    
    def set_collision(self, enabled: bool):
        """Set collision enabled state"""
        self.collision_enabled = enabled
    
    def has_collision(self) -> bool:
        """Check if object has collision"""
        return self.collision_enabled


@dataclass
class StaticMesh3D:
    """3D static mesh object"""
    position: Vector3
    object_type: WorldObjectType
    render_layer: RenderLayer
    mesh_name: str
    scale: Vector3 = None
    rotation: Vector3 = None
    color: Tuple[int, int, int] = (255, 255, 255)
    visible: bool = True
    collision_enabled: bool = True
    
    def __post_init__(self):
        if self.scale is None:
            self.scale = Vector3(1, 1, 1)
        if self.rotation is None:
            self.rotation = Vector3(0, 0, 0)
    
    def set_position(self, position: Vector3):
        """Set object position"""
        self.position = position
    
    def get_position(self) -> Vector3:
        """Get object position"""
        return self.position
    
    def set_rotation(self, rotation: Vector3):
        """Set object rotation"""
        self.rotation = rotation
    
    def get_rotation(self) -> Vector3:
        """Get object rotation"""
        return self.rotation
    
    def set_scale(self, scale: Vector3):
        """Set object scale"""
        self.scale = scale
    
    def get_scale(self) -> Vector3:
        """Get object scale"""
        return self.scale
    
    def set_visibility(self, visible: bool):
        """Set object visibility"""
        self.visible = visible
    
    def is_visible(self) -> bool:
        """Check if object is visible"""
        return self.visible
    
    def set_collision(self, enabled: bool):
        """Set collision enabled state"""
        self.collision_enabled = enabled
    
    def has_collision(self) -> bool:
        """Check if object has collision"""
        return self.collision_enabled


class Camera3D:
    """3D camera for world rendering"""
    
    def __init__(self):
        self.position = Vector3(0, 10, 0)
        self.target = Vector3(0, 0, 0)
        self.up = Vector3(0, 1, 0)
        self.fov = 60.0
        self.near_distance = 0.1
        self.far_distance = 1000.0
        self.is_orthographic = False
        
    def move_to(self, position: Vector3):
        """Move camera to position"""
        self.position = position
    
    def look_at(self, target: Vector3):
        """Look at target position"""
        self.target = target
    
    def follow_object(self, obj: StaticMesh3D, smoothing: float = 0.1):
        """Follow an object with smoothing"""
        if obj:
            # Smooth camera movement towards object
            self.target = Vector3(
                self.target.x + (obj.position.x - self.target.x) * smoothing,
                self.target.y + (obj.position.y - self.target.y) * smoothing,
                self.target.z + (obj.position.z - self.target.z) * smoothing
            )


class WorldLayer:
    """A rendering layer containing objects"""
    
    def __init__(self, layer_type: RenderLayer):
        self.layer_type = layer_type
        self.objects: List[StaticMesh3D] = []
        self.visible = True
        self.rendered_objects = 0
    
    def add_object(self, obj: StaticMesh3D):
        """Add object to layer"""
        self.objects.append(obj)
    
    def remove_object(self, obj: StaticMesh3D):
        """Remove object from layer"""
        if obj in self.objects:
            self.objects.remove(obj)
    
    def set_visibility(self, visible: bool):
        """Set layer visibility"""
        self.visible = visible


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
        
        # 3D rendering system
        self.camera = Camera3D()
        self.layers: Dict[RenderLayer, WorldLayer] = {}
        self.world_bounds = {
            'min': Vector3(-500, -100, -500),
            'max': Vector3(500, 100, 500)
        }
        self.ambient_light = 0.8
        self.frame_count = 0
        
        # Initialize rendering layers
        for layer_type in RenderLayer:
            self.layers[layer_type] = WorldLayer(layer_type)
        
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
        for layer in range(min(len(self.map_tiles), new_layers)):
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
                0 <= layer < len(self.map_tiles))
    
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
                for layer in range(len(self.map_tiles)):
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
        for layer in range(len(self.map_tiles)):
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
            'world_size': f"{self.width}x{self.height}x{len(self.map_tiles)}",
            'total_blocks': self.width * self.height * len(self.map_tiles),
            'block_types': block_counts,
            'districts': len(self.districts),
            'district_types': district_counts,
            'navigation_sectors': len(self.navigation_sectors),
            'time_of_day': self.time_of_day,
            'weather': self.weather,
            'temperature': self.temperature,
            'water_level': self.water_level
        }
    
    def add_object(self, obj: StaticMesh3D) -> None:
        """Add object to appropriate layer"""
        if obj.render_layer in self.layers:
            self.layers[obj.render_layer].add_object(obj)
    
    def remove_object(self, obj: StaticMesh3D) -> None:
        """Remove object from layer"""
        if obj.render_layer in self.layers:
            self.layers[obj.render_layer].remove_object(obj)
    
    def set_layer_visibility(self, layer_type: RenderLayer, visible: bool) -> None:
        """Set layer visibility"""
        if layer_type in self.layers:
            self.layers[layer_type].set_visibility(visible)
    
    def move_camera(self, movement: Vector3) -> None:
        """Move camera by movement vector"""
        self.camera.position = Vector3(
            self.camera.position.x + movement.x,
            self.camera.position.y + movement.y,
            self.camera.position.z + movement.z
        )
    
    def follow_object(self, obj: StaticMesh3D, smoothing: float = 0.1) -> None:
        """Follow an object with camera"""
        self.camera.follow_object(obj, smoothing)
    
    def get_objects_in_radius(self, position: Vector3, radius: float) -> List[StaticMesh3D]:
        """Get objects within radius of position"""
        objects = []
        for layer in self.layers.values():
            for obj in layer.objects:
                if obj.visible:
                    distance = math.sqrt(
                        (obj.position.x - position.x)**2 +
                        (obj.position.y - position.y)**2 +
                        (obj.position.z - position.z)**2
                    )
                    if distance <= radius:
                        objects.append(obj)
        return objects
    
    def create_test_world(self) -> None:
        """Create a test world with sample objects"""
        # Add some test buildings
        for i in range(10):
            x = random.uniform(-50, 50)
            z = random.uniform(-50, 50)
            building = StaticMesh3D(
                Vector3(x, 0, z),
                WorldObjectType.BUILDING,
                RenderLayer.BUILDINGS_LOW,
                mesh_name=f"building_{i}"
            )
            building.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            self.add_object(building)
        
        # Add some ground objects
        for i in range(20):
            x = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            obj = StaticMesh3D(
                Vector3(x, 0, z),
                WorldObjectType.STATIC_MESH,
                RenderLayer.OBJECTS_GROUND,
                mesh_name=f"ground_obj_{i}"
            )
            obj.color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            self.add_object(obj)
        
        print("🌍 Test world created with sample objects")
    
    def update(self, dt: float) -> None:
        """Update world state"""
        self.frame_count += 1
        self.update_world_state(dt)
    
    def render(self, screen) -> None:
        """Render world to screen (simplified for testing)"""
        # This is a simplified render method for testing
        # In a real implementation, this would do proper 3D rendering
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get world statistics"""
        total_objects = sum(len(layer.objects) for layer in self.layers.values())
        rendered_objects = sum(layer.rendered_objects for layer in self.layers.values())
        culled_objects = total_objects - rendered_objects
        active_layers = sum(1 for layer in self.layers.values() if layer.visible and len(layer.objects) > 0)
        
        return {
            'total_objects': total_objects,
            'rendered_objects': rendered_objects,
            'culled_objects': culled_objects,
            'active_layers': active_layers,
            'frame_count': self.frame_count,
            'camera_position': (self.camera.position.x, self.camera.position.y, self.camera.position.z)
        }
    
    def load_tmx_map(self, map_name: str, mod_path: str = "mods/saiyanquest") -> bool:
        """Load a TMX map and convert it to 3D world format"""
        try:
            import pytmx
            from pathlib import Path
            
            map_file = Path(mod_path) / "maps" / f"{map_name}.tmx"
            if not map_file.exists():
                print(f"❌ TMX map file not found: {map_file}")
                return False
            
            print(f"🗺️ Loading TMX map: {map_name}")
            
            # Load TMX map
            tmx_map = pytmx.load_pygame(str(map_file), pixelalpha=True)
            
            # Update world dimensions
            self.width = tmx_map.width
            self.height = tmx_map.height
            
            # Resize world if needed
            if len(self.map_tiles) != self.layers or \
               len(self.map_tiles[0]) != self.height or \
               len(self.map_tiles[0][0]) != self.width:
                self._resize_world(self.width, self.height, self.layers)
            
            # Process each TMX layer
            for layer_idx, layer in enumerate(tmx_map.visible_layers):
                if isinstance(layer, pytmx.TiledTileLayer) and layer_idx < self.layers:
                    self._process_tmx_layer_to_3d(layer, tmx_map, layer_idx)
            
            # Create districts based on TMX properties
            self._create_districts_from_tmx(tmx_map)
            
            # Generate navigation sectors
            self.generate_navigation_sectors()
            
            print(f"✅ Loaded TMX map: {map_name} ({self.width}x{self.height})")
            print(f"   ✓ Processed {len(tmx_map.visible_layers)} layers")
            print(f"   ✓ Created {len(self.districts)} districts")
            print(f"   ✓ Generated {len(self.navigation_sectors)} navigation sectors")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load TMX map {map_name}: {e}")
            return False
    
    def _process_tmx_layer_to_3d(self, layer, tmx_map, layer_idx: int) -> None:
        """Process a TMX tile layer into 3D world blocks"""
        for y in range(layer.height):
            for x in range(layer.width):
                tile_id = layer.data[y][x]
                if tile_id == 0:  # Empty tile
                    continue
                
                # Get tile properties
                tile_props = tmx_map.get_tile_properties_by_gid(tile_id)
                
                # Determine block type based on tile properties or layer name
                block_type = self._determine_block_type_from_tmx(layer.name, tile_props)
                
                # Create block info
                block_info = MapBlockInfo(
                    block_type=block_type,
                    height=self._get_height_from_tmx(layer.name, tile_props),
                    water_level=self._get_water_level_from_tmx(layer.name, tile_props),
                    collision_enabled=self._get_collision_from_tmx(layer.name, tile_props),
                    walkable=self._get_walkable_from_tmx(layer.name, tile_props),
                    driveable=self._get_driveable_from_tmx(layer.name, tile_props),
                    flyable=self._get_flyable_from_tmx(layer.name, tile_props),
                    district_id=0,  # Will be set later
                    properties=tile_props or {}
                )
                
                self.set_block_info(x, y, layer_idx, block_info)
    
    def _determine_block_type_from_tmx(self, layer_name: str, tile_props: Dict) -> BlockType:
        """Determine block type from TMX layer name and properties"""
        layer_name_lower = layer_name.lower()
        
        if 'road' in layer_name_lower or 'street' in layer_name_lower:
            return BlockType.ROAD
        elif 'building' in layer_name_lower or 'house' in layer_name_lower:
            return BlockType.BUILDING
        elif 'water' in layer_name_lower or 'river' in layer_name_lower:
            return BlockType.WATER
        elif 'grass' in layer_name_lower or 'field' in layer_name_lower:
            return BlockType.GRASS
        elif 'sand' in layer_name_lower or 'beach' in layer_name_lower:
            return BlockType.SAND
        elif 'rock' in layer_name_lower or 'stone' in layer_name_lower:
            return BlockType.ROCK
        elif 'bridge' in layer_name_lower:
            return BlockType.BRIDGE
        elif 'railway' in layer_name_lower or 'train' in layer_name_lower:
            return BlockType.RAILWAY
        else:
            # Check tile properties
            if tile_props:
                if tile_props.get('collision', False):
                    return BlockType.SOLID
                elif tile_props.get('water', False):
                    return BlockType.WATER
                elif tile_props.get('road', False):
                    return BlockType.ROAD
            
            return BlockType.EMPTY
    
    def _get_height_from_tmx(self, layer_name: str, tile_props: Dict) -> float:
        """Get height from TMX data"""
        if tile_props and 'height' in tile_props:
            return float(tile_props['height'])
        
        # Default heights based on layer
        layer_name_lower = layer_name.lower()
        if 'building' in layer_name_lower:
            return 10.0
        elif 'bridge' in layer_name_lower:
            return 5.0
        else:
            return 0.0
    
    def _get_water_level_from_tmx(self, layer_name: str, tile_props: Dict) -> float:
        """Get water level from TMX data"""
        if tile_props and 'water_level' in tile_props:
            return float(tile_props['water_level'])
        
        if 'water' in layer_name.lower():
            return 1.0
        
        return 0.0
    
    def _get_collision_from_tmx(self, layer_name: str, tile_props: Dict) -> bool:
        """Get collision setting from TMX data"""
        if tile_props and 'collision' in tile_props:
            return bool(tile_props['collision'])
        
        # Default collision based on layer
        layer_name_lower = layer_name.lower()
        if any(term in layer_name_lower for term in ['building', 'wall', 'solid', 'collision']):
            return True
        
        return False
    
    def _get_walkable_from_tmx(self, layer_name: str, tile_props: Dict) -> bool:
        """Get walkable setting from TMX data"""
        if tile_props and 'walkable' in tile_props:
            return bool(tile_props['walkable'])
        
        # Default walkable based on layer
        layer_name_lower = layer_name.lower()
        if any(term in layer_name_lower for term in ['building', 'wall', 'solid']):
            return False
        
        return True
    
    def _get_driveable_from_tmx(self, layer_name: str, tile_props: Dict) -> bool:
        """Get driveable setting from TMX data"""
        if tile_props and 'driveable' in tile_props:
            return bool(tile_props['driveable'])
        
        # Default driveable based on layer
        layer_name_lower = layer_name.lower()
        if any(term in layer_name_lower for term in ['road', 'street', 'bridge']):
            return True
        elif any(term in layer_name_lower for term in ['building', 'wall', 'water']):
            return False
        
        return True
    
    def _get_flyable_from_tmx(self, layer_name: str, tile_props: Dict) -> bool:
        """Get flyable setting from TMX data"""
        if tile_props and 'flyable' in tile_props:
            return bool(tile_props['flyable'])
        
        # Most areas are flyable except solid buildings
        layer_name_lower = layer_name.lower()
        if 'building' in layer_name_lower and 'roof' not in layer_name_lower:
            return False
        
        return True
    
    def _create_districts_from_tmx(self, tmx_map) -> None:
        """Create districts based on TMX map properties"""
        # Look for district objects or properties
        for obj_group in tmx_map.objectgroups:
            for obj in obj_group:
                if obj.name and 'district' in obj.name.lower():
                    # Create district from object
                    district_type = DistrictType.RESIDENTIAL  # Default
                    
                    # Determine district type from properties
                    if obj.properties:
                        if obj.properties.get('commercial', False):
                            district_type = DistrictType.COMMERCIAL
                        elif obj.properties.get('industrial', False):
                            district_type = DistrictType.INDUSTRIAL
                        elif obj.properties.get('downtown', False):
                            district_type = DistrictType.DOWNTOWN
                    
                    # Create district bounds from object
                    bounds = (
                        int(obj.x // tmx_map.tilewidth),
                        int(obj.y // tmx_map.tileheight),
                        int((obj.x + obj.width) // tmx_map.tilewidth),
                        int((obj.y + obj.height) // tmx_map.tileheight)
                    )
                    
                    self.create_district(obj.name, district_type, bounds)
        
        # If no districts found, create a default one
        if not self.districts:
            self.create_district("Default District", DistrictType.RESIDENTIAL, (0, 0, self.width-1, self.height-1))


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