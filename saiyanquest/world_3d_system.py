#!/usr/bin/env python3
"""
3D World System with Layers - Based on Carnage3D's Architecture
Provides multi-layered 3D world rendering with depth sorting and camera management.
"""

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from abc import ABC, abstractmethod

# 3D Math utilities
@dataclass
class Vector3:
    """3D vector for world positions and calculations"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self) -> 'Vector3':
        l = self.length()
        if l > 0:
            return Vector3(self.x / l, self.y / l, self.z / l)
        return Vector3(0, 0, 0)
    
    def dot(self, other: 'Vector3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def distance_to(self, other: 'Vector3') -> float:
        return (self - other).length()

@dataclass
class Matrix4:
    """4x4 transformation matrix for 3D operations"""
    data: List[List[float]] = field(default_factory=lambda: [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    @staticmethod
    def identity() -> 'Matrix4':
        return Matrix4()
    
    @staticmethod
    def translation(x: float, y: float, z: float) -> 'Matrix4':
        m = Matrix4.identity()
        m.data[0][3] = x
        m.data[1][3] = y
        m.data[2][3] = z
        return m
    
    @staticmethod
    def rotation_y(angle: float) -> 'Matrix4':
        """Rotation around Y-axis (yaw)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        m = Matrix4.identity()
        m.data[0][0] = cos_a
        m.data[0][2] = sin_a
        m.data[2][0] = -sin_a
        m.data[2][2] = cos_a
        return m
    
    def multiply(self, other: 'Matrix4') -> 'Matrix4':
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.data[i][j] = sum(
                    self.data[i][k] * other.data[k][j]
                    for k in range(4)
                )
        return result
    
    def transform_point(self, point: Vector3) -> Vector3:
        """Transform a 3D point by this matrix"""
        x = self.data[0][0] * point.x + self.data[0][1] * point.y + self.data[0][2] * point.z + self.data[0][3]
        y = self.data[1][0] * point.x + self.data[1][1] * point.y + self.data[1][2] * point.z + self.data[1][3]
        z = self.data[2][0] * point.x + self.data[2][1] * point.y + self.data[2][2] * point.z + self.data[2][3]
        return Vector3(x, y, z)

# World Layer System
class RenderLayer(IntEnum):
    """Rendering layers ordered by depth (back to front)"""
    BACKGROUND = 0      # Sky, distant mountains
    TERRAIN_BASE = 1    # Ground base layer
    ROADS = 2          # Road surfaces
    WALKWAYS = 3       # Sidewalks, paths
    BUILDINGS_LOW = 4  # Lower building parts
    SHADOWS = 5        # Dynamic shadows
    OBJECTS_GROUND = 6 # Objects on ground level
    VEHICLES = 7       # Cars, bikes, etc.
    CHARACTERS = 8     # Pedestrians, player
    BUILDINGS_HIGH = 9 # Upper building parts
    PARTICLES = 10     # Smoke, sparks, effects
    WATER = 11         # Transparent water surfaces
    UI_WORLD = 12      # 3D UI elements (health bars)
    LIGHTING = 13      # Dynamic lighting overlay
    DEBUG = 14         # Debug visualizations

class WorldObjectType(Enum):
    """Types of objects in the 3D world"""
    STATIC_MESH = "static_mesh"      # Buildings, props
    DYNAMIC_OBJECT = "dynamic_object" # Destructible objects
    VEHICLE = "vehicle"              # Cars, bikes
    CHARACTER = "character"          # Pedestrians, player
    PARTICLE_SYSTEM = "particles"    # Effects
    LIGHT_SOURCE = "light"           # Lights
    TRIGGER_VOLUME = "trigger"       # Invisible triggers
    WATER_SURFACE = "water"          # Water bodies

@dataclass
class RenderBatch:
    """Group of similar objects to render together for performance"""
    layer: RenderLayer
    texture_id: Optional[str] = None
    shader_id: Optional[str] = None
    objects: List['WorldObject3D'] = field(default_factory=list)
    is_transparent: bool = False
    
    def sort_by_depth(self, camera_pos: Vector3):
        """Sort objects by distance from camera for proper depth rendering"""
        self.objects.sort(
            key=lambda obj: obj.position.distance_to(camera_pos),
            reverse=self.is_transparent  # Transparent objects render back-to-front
        )

class WorldObject3D(ABC):
    """Base class for all 3D world objects"""
    
    def __init__(self, position: Vector3, object_type: WorldObjectType, layer: RenderLayer):
        self.position = position
        self.rotation = Vector3(0, 0, 0)  # Euler angles
        self.scale = Vector3(1, 1, 1)
        self.object_type = object_type
        self.layer = layer
        self.visible = True
        self.cast_shadows = True
        self.receive_shadows = True
        self.bounding_box = self._calculate_bounding_box()
        self.last_render_frame = 0
        
        # Transform matrix
        self.transform_matrix = Matrix4.identity()
        self.transform_dirty = True
        
        print(f"🌍 3D Object created: {object_type.value} at {position.x:.1f}, {position.y:.1f}, {position.z:.1f}")
    
    @abstractmethod
    def _calculate_bounding_box(self) -> Tuple[Vector3, Vector3]:
        """Calculate object bounding box (min, max)"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update object state"""
        pass
    
    @abstractmethod
    def render_2d_projection(self, surface: pygame.Surface, camera: 'Camera3D', 
                           screen_pos: Tuple[int, int], scale: float) -> None:
        """Render object as 2D projection on screen"""
        pass
    
    def update_transform_matrix(self) -> None:
        """Update transformation matrix from position, rotation, scale"""
        if not self.transform_dirty:
            return
            
        # Build transformation matrix: Translation * Rotation * Scale
        translation = Matrix4.translation(self.position.x, self.position.y, self.position.z)
        rotation_y = Matrix4.rotation_y(math.radians(self.rotation.y))  # Simplified - just Y rotation
        
        self.transform_matrix = translation.multiply(rotation_y)
        self.transform_dirty = False
    
    def set_position(self, position: Vector3) -> None:
        """Update object position"""
        self.position = position
        self.transform_dirty = True
        self.bounding_box = self._calculate_bounding_box()
    
    def set_rotation(self, rotation: Vector3) -> None:
        """Update object rotation"""
        self.rotation = rotation
        self.transform_dirty = True
    
    def get_distance_to_camera(self, camera_pos: Vector3) -> float:
        """Get distance from object to camera for LOD and culling"""
        return self.position.distance_to(camera_pos)
    
    def is_in_frustum(self, camera: 'Camera3D') -> bool:
        """Check if object is within camera frustum (simplified)"""
        # Simplified frustum culling - just check distance for now
        distance = self.get_distance_to_camera(camera.position)
        return distance <= camera.far_distance

class StaticMesh3D(WorldObject3D):
    """Static mesh object like buildings, props"""
    
    def __init__(self, position: Vector3, mesh_id: str, layer: RenderLayer = RenderLayer.BUILDINGS_LOW):
        super().__init__(position, WorldObjectType.STATIC_MESH, layer)
        self.mesh_id = mesh_id
        self.texture_id: Optional[str] = None
        self.color = (128, 128, 128)  # Default gray
        self.health = 100.0
        self.destructible = False
        
    def _calculate_bounding_box(self) -> Tuple[Vector3, Vector3]:
        # Simple box for now - would be loaded from mesh data in real implementation
        size = 2.0
        return (
            Vector3(self.position.x - size, self.position.y - size, self.position.z - size),
            Vector3(self.position.x + size, self.position.y + size, self.position.z + size)
        )
    
    def update(self, delta_time: float) -> None:
        # Static meshes don't update unless destructible
        if self.destructible and self.health <= 0:
            self.visible = False
    
    def render_2d_projection(self, surface: pygame.Surface, camera: 'Camera3D', 
                           screen_pos: Tuple[int, int], scale: float) -> None:
        # Simple 2D representation as colored rectangle
        size = max(4, int(20 * scale))
        rect = pygame.Rect(screen_pos[0] - size//2, screen_pos[1] - size//2, size, size)
        pygame.draw.rect(surface, self.color, rect)
        
        # Draw outline for depth
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

class Camera3D:
    """3D camera system for world rendering"""
    
    def __init__(self, position: Vector3 = Vector3(0, 5, 10)):
        self.position = position
        self.target = Vector3(0, 0, 0)
        self.up_vector = Vector3(0, 1, 0)
        
        # Camera parameters
        self.fov = math.radians(75)  # Field of view
        self.near_distance = 0.1
        self.far_distance = 1000.0
        self.aspect_ratio = 16.0 / 9.0
        
        # Projection settings for top-down GTA-style
        self.is_orthographic = False
        self.orthographic_size = 100.0
        
        # Movement parameters
        self.movement_speed = 10.0
        self.rotation_speed = 2.0
        self.zoom_speed = 5.0
        
        # Camera state
        self.view_matrix = Matrix4.identity()
        self.projection_matrix = Matrix4.identity()
        self.view_dirty = True
        self.projection_dirty = True
        
        print(f"📹 3D Camera initialized at {position.x:.1f}, {position.y:.1f}, {position.z:.1f}")
    
    def look_at(self, target: Vector3) -> None:
        """Point camera at target position"""
        self.target = target
        self.view_dirty = True
    
    def move_to(self, position: Vector3) -> None:
        """Move camera to position"""
        self.position = position
        self.view_dirty = True
    
    def follow_target(self, target_pos: Vector3, offset: Vector3, smoothing: float = 0.1) -> None:
        """Smoothly follow a target with offset"""
        desired_pos = target_pos + offset
        self.position = Vector3(
            self.position.x + (desired_pos.x - self.position.x) * smoothing,
            self.position.y + (desired_pos.y - self.position.y) * smoothing,
            self.position.z + (desired_pos.z - self.position.z) * smoothing
        )
        self.look_at(target_pos)
    
    def world_to_screen(self, world_pos: Vector3, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Convert 3D world position to 2D screen coordinates"""
        # Simplified projection - proper matrix multiplication would be used in real 3D
        
        # Distance-based scaling (closer = larger)
        distance = world_pos.distance_to(self.position)
        if distance < 0.1:
            distance = 0.1
        
        scale = 50.0 / distance  # Adjust scale factor as needed
        
        # Convert world coordinates to screen coordinates
        # For top-down GTA-style view, we mainly use X and Z (Y is height)
        relative_pos = world_pos - self.position
        
        # Simple orthographic-style projection
        screen_x = int(screen_width / 2 + relative_pos.x * scale)
        screen_y = int(screen_height / 2 + relative_pos.z * scale)  # Z becomes Y on screen
        
        return (screen_x, screen_y)
    
    def get_view_distance_scale(self, world_pos: Vector3) -> float:
        """Get scaling factor based on distance from camera"""
        distance = world_pos.distance_to(self.position)
        if distance < 1.0:
            return 1.0
        return min(1.0, 20.0 / distance)  # Objects get smaller with distance

class World3DLayer:
    """Individual rendering layer in the 3D world"""
    
    def __init__(self, layer_type: RenderLayer):
        self.layer_type = layer_type
        self.objects: List[WorldObject3D] = []
        self.render_batches: Dict[str, RenderBatch] = {}
        self.visible = True
        self.alpha = 1.0
        
        # Performance tracking
        self.rendered_objects = 0
        self.culled_objects = 0
    
    def add_object(self, obj: WorldObject3D) -> None:
        """Add object to this layer"""
        self.objects.append(obj)
        self._add_to_batch(obj)
        print(f"🎬 Object added to layer {self.layer_type.name}: {obj.object_type.value}")
    
    def remove_object(self, obj: WorldObject3D) -> None:
        """Remove object from this layer"""
        if obj in self.objects:
            self.objects.remove(obj)
            self._remove_from_batch(obj)
    
    def _add_to_batch(self, obj: WorldObject3D) -> None:
        """Add object to appropriate render batch"""
        batch_key = f"{obj.object_type.value}"
        if batch_key not in self.render_batches:
            self.render_batches[batch_key] = RenderBatch(
                layer=self.layer_type,
                is_transparent=(self.layer_type in [RenderLayer.WATER, RenderLayer.PARTICLES])
            )
        self.render_batches[batch_key].objects.append(obj)
    
    def _remove_from_batch(self, obj: WorldObject3D) -> None:
        """Remove object from its render batch"""
        batch_key = f"{obj.object_type.value}"
        if batch_key in self.render_batches:
            if obj in self.render_batches[batch_key].objects:
                self.render_batches[batch_key].objects.remove(obj)
    
    def update(self, delta_time: float) -> None:
        """Update all objects in this layer"""
        for obj in self.objects[:]:  # Copy list to allow modifications
            obj.update(delta_time)
            if not obj.visible:
                self.remove_object(obj)
    
    def render(self, surface: pygame.Surface, camera: Camera3D) -> None:
        """Render all objects in this layer"""
        if not self.visible:
            return
            
        self.rendered_objects = 0
        self.culled_objects = 0
        
        # Sort render batches for proper depth ordering
        for batch in self.render_batches.values():
            batch.sort_by_depth(camera.position)
        
        # Render each batch
        for batch in self.render_batches.values():
            self._render_batch(batch, surface, camera)
    
    def _render_batch(self, batch: RenderBatch, surface: pygame.Surface, camera: Camera3D) -> None:
        """Render a batch of similar objects"""
        screen_width, screen_height = surface.get_size()
        
        for obj in batch.objects:
            if not obj.visible:
                continue
                
            # Frustum culling
            if not obj.is_in_frustum(camera):
                self.culled_objects += 1
                continue
            
            # Convert world position to screen position
            screen_pos = camera.world_to_screen(obj.position, screen_width, screen_height)
            
            # Skip if off-screen
            if (screen_pos[0] < -50 or screen_pos[0] > screen_width + 50 or
                screen_pos[1] < -50 or screen_pos[1] > screen_height + 50):
                self.culled_objects += 1
                continue
            
            # Get scale based on distance
            scale = camera.get_view_distance_scale(obj.position)
            
            # Render object
            obj.render_2d_projection(surface, camera, screen_pos, scale)
            self.rendered_objects += 1

class World3DSystem:
    """Complete 3D world system with layered rendering"""
    
    def __init__(self, screen_width: int = 1400, screen_height: int = 900):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera system
        self.camera = Camera3D(Vector3(0, 20, 0))  # Above world looking down
        self.camera.is_orthographic = True
        
        # Layer system
        self.layers: Dict[RenderLayer, World3DLayer] = {}
        for layer_type in RenderLayer:
            self.layers[layer_type] = World3DLayer(layer_type)
        
        # World bounds
        self.world_bounds = {
            'min': Vector3(-500, -10, -500),
            'max': Vector3(500, 100, 500)
        }
        
        # Performance tracking
        self.frame_count = 0
        self.total_objects = 0
        self.rendered_objects = 0
        self.culled_objects = 0
        
        # Lighting system (basic)
        self.ambient_light = 0.3
        self.sun_direction = Vector3(0.5, -1, 0.3).normalize()
        self.sun_intensity = 0.7
        
        print("🌍 3D World System initialized")
        print(f"   Screen: {screen_width}x{screen_height}")
        print(f"   Layers: {len(self.layers)}")
        print(f"   World bounds: {self.world_bounds['min'].x:.0f}x{self.world_bounds['min'].z:.0f} to {self.world_bounds['max'].x:.0f}x{self.world_bounds['max'].z:.0f}")
    
    def add_object(self, obj: WorldObject3D) -> None:
        """Add object to appropriate layer"""
        if obj.layer in self.layers:
            self.layers[obj.layer].add_object(obj)
            self.total_objects += 1
    
    def remove_object(self, obj: WorldObject3D) -> None:
        """Remove object from its layer"""
        if obj.layer in self.layers:
            self.layers[obj.layer].remove_object(obj)
            self.total_objects -= 1
    
    def create_test_world(self) -> None:
        """Create a test world with various objects"""
        print("🏗️ Creating test 3D world...")
        
        # Create ground plane objects
        for x in range(-20, 21, 5):
            for z in range(-20, 21, 5):
                ground = StaticMesh3D(
                    Vector3(x * 5, 0, z * 5),
                    "ground_tile",
                    RenderLayer.TERRAIN_BASE
                )
                ground.color = (60, 80, 40)  # Dark green ground
                self.add_object(ground)
        
        # Create buildings
        building_positions = [
            (30, 0, 30), (-30, 0, 30), (30, 0, -30), (-30, 0, -30),
            (50, 0, 0), (-50, 0, 0), (0, 0, 50), (0, 0, -50),
            (70, 0, 20), (-70, 0, -20)
        ]
        
        for i, (x, y, z) in enumerate(building_positions):
            building = StaticMesh3D(
                Vector3(x, y + 5, z),  # Elevated
                f"building_{i}",
                RenderLayer.BUILDINGS_LOW
            )
            # Vary building colors
            colors = [(100, 100, 120), (120, 100, 100), (100, 120, 100), (120, 120, 100)]
            building.color = colors[i % len(colors)]
            self.add_object(building)
        
        # Create roads (simple)
        for x in range(-100, 101, 10):
            road = StaticMesh3D(
                Vector3(x, 0.1, 0),
                "road_segment",
                RenderLayer.ROADS
            )
            road.color = (40, 40, 40)  # Dark gray road
            self.add_object(road)
        
        for z in range(-100, 101, 10):
            road = StaticMesh3D(
                Vector3(0, 0.1, z),
                "road_segment",
                RenderLayer.ROADS
            )
            road.color = (40, 40, 40)  # Dark gray road
            self.add_object(road)
        
        # Create some decorative objects
        for i in range(20):
            x = (i - 10) * 8 + random.uniform(-3, 3)
            z = (i - 10) * 6 + random.uniform(-3, 3)
            prop = StaticMesh3D(
                Vector3(x, 1, z),
                f"prop_{i}",
                RenderLayer.OBJECTS_GROUND
            )
            prop.color = (80, 60, 40)  # Brown props
            self.add_object(prop)
        
        print(f"✅ Test world created with {self.total_objects} objects")
    
    def update(self, delta_time: float) -> None:
        """Update all world layers and objects"""
        # Update all layers
        for layer in self.layers.values():
            layer.update(delta_time)
        
        # Update camera
        # (Camera updates would be handled by game logic)
        
        self.frame_count += 1
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the entire 3D world in layer order"""
        # Clear background
        surface.fill((135, 206, 235))  # Sky blue background
        
        # Reset performance counters
        self.rendered_objects = 0
        self.culled_objects = 0
        
        # Render layers in order (back to front)
        for layer_type in RenderLayer:
            layer = self.layers[layer_type]
            layer.render(surface, self.camera)
            
            # Accumulate performance stats
            self.rendered_objects += layer.rendered_objects
            self.culled_objects += layer.culled_objects
    
    def move_camera(self, offset: Vector3) -> None:
        """Move camera by offset"""
        new_pos = self.camera.position + offset
        
        # Clamp camera within world bounds
        new_pos.x = max(self.world_bounds['min'].x, 
                       min(self.world_bounds['max'].x, new_pos.x))
        new_pos.z = max(self.world_bounds['min'].z, 
                       min(self.world_bounds['max'].z, new_pos.z))
        
        self.camera.move_to(new_pos)
    
    def follow_object(self, target_obj: WorldObject3D, smoothing: float = 0.1) -> None:
        """Make camera follow an object"""
        offset = Vector3(0, 20, 10)  # Above and behind
        self.camera.follow_target(target_obj.position, offset, smoothing)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get world system performance statistics"""
        return {
            'total_objects': self.total_objects,
            'rendered_objects': self.rendered_objects,
            'culled_objects': self.culled_objects,
            'active_layers': sum(1 for layer in self.layers.values() if layer.visible),
            'camera_position': (self.camera.position.x, self.camera.position.y, self.camera.position.z),
            'frame_count': self.frame_count
        }
    
    def set_layer_visibility(self, layer: RenderLayer, visible: bool) -> None:
        """Toggle layer visibility for debugging"""
        if layer in self.layers:
            self.layers[layer].visible = visible
    
    def get_objects_in_radius(self, center: Vector3, radius: float) -> List[WorldObject3D]:
        """Get all objects within radius of center point"""
        objects = []
        for layer in self.layers.values():
            for obj in layer.objects:
                if obj.position.distance_to(center) <= radius:
                    objects.append(obj)
        return objects