#!/usr/bin/env python3
"""
Advanced Physics Manager - Based on Carnage3D's PhysicsManager
Provides Box2D physics integration for realistic vehicle and character simulation.
"""

import Box2D
from Box2D import b2World, b2BodyDef, b2FixtureDef, b2PolygonShape, b2CircleShape, b2ContactListener
from Box2D import b2_dynamicBody, b2_staticBody, b2_kinematicBody
from Box2D import b2Vec2, b2AABB, b2Contact, b2ContactImpulse, b2RayCastCallback, b2QueryCallback
import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntFlag
import pygame

class CollisionCategory(IntFlag):
    """Collision categories for filtering"""
    NONE = 0x0000
    MAP = 0x0001
    VEHICLE = 0x0002
    PEDESTRIAN = 0x0004
    PROJECTILE = 0x0008
    WATER = 0x0010
    PICKUP = 0x0020
    ALL = 0xFFFF

@dataclass
class PhysicsBodyConfig:
    """Configuration for creating physics bodies"""
    body_type: int = b2_dynamicBody
    position: Tuple[float, float] = (0.0, 0.0)
    angle: float = 0.0
    linear_damping: float = 0.1
    angular_damping: float = 0.1
    category: CollisionCategory = CollisionCategory.NONE
    mask: CollisionCategory = CollisionCategory.ALL
    is_sensor: bool = False
    density: float = 1.0
    friction: float = 0.3
    restitution: float = 0.1

@dataclass
class CollisionInfo:
    """Information about a collision event"""
    body_a: 'PhysicsBody'
    body_b: 'PhysicsBody'
    contact_point: Tuple[float, float]
    normal: Tuple[float, float]
    impulse: float
    
class PhysicsBody:
    """Wrapper for Box2D body with game-specific functionality"""
    
    def __init__(self, body: Box2D.b2Body, game_object: Any = None):
        self.body = body
        self.game_object = game_object
        self.body.userData = self
        
        # Store original properties for reset/respawn
        self.original_position = body.position
        self.original_angle = body.angle
        
    @property
    def position(self) -> Tuple[float, float]:
        """Get body position in world coordinates"""
        pos = self.body.position
        return (pos.x, pos.y)
    
    @property
    def angle(self) -> float:
        """Get body angle in radians"""
        return self.body.angle
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Get linear velocity"""
        vel = self.body.linearVelocity
        return (vel.x, vel.y)
    
    @property
    def angular_velocity(self) -> float:
        """Get angular velocity"""
        return self.body.angularVelocity
    
    def set_position(self, x: float, y: float):
        """Set body position"""
        self.body.position = (x, y)
    
    def set_angle(self, angle: float):
        """Set body angle"""
        self.body.angle = angle
    
    def apply_force(self, force: Tuple[float, float], point: Optional[Tuple[float, float]] = None):
        """Apply force to body"""
        if point is None:
            self.body.ApplyForceToCenter(force, True)
        else:
            self.body.ApplyForce(force, point, True)
    
    def apply_impulse(self, impulse: Tuple[float, float], point: Optional[Tuple[float, float]] = None):
        """Apply impulse to body"""
        if point is None:
            self.body.ApplyLinearImpulse(impulse, self.body.worldCenter, True)
        else:
            self.body.ApplyLinearImpulse(impulse, point, True)
    
    def set_velocity(self, velocity: Tuple[float, float]):
        """Set linear velocity directly"""
        self.body.linearVelocity = velocity
    
    def set_angular_velocity(self, angular_velocity: float):
        """Set angular velocity directly"""
        self.body.angularVelocity = angular_velocity
    
    def destroy(self):
        """Mark body for destruction"""
        if self.body:
            self.body.userData = None
            # Body will be destroyed by PhysicsManager

class ContactListener(b2ContactListener):
    """Custom contact listener for collision handling"""
    
    def __init__(self, physics_manager):
        super().__init__()
        self.physics_manager = physics_manager
        
    def BeginContact(self, contact: b2Contact):
        """Called when two fixtures begin to touch"""
        fixture_a = contact.fixtureA
        fixture_b = contact.fixtureB
        
        body_a = fixture_a.body.userData
        body_b = fixture_b.body.userData
        
        if body_a and body_b:
            # Get contact information
            world_manifold = contact.worldManifold
            
            collision_info = CollisionInfo(
                body_a=body_a,
                body_b=body_b,
                contact_point=world_manifold.points[0] if world_manifold.points else (0, 0),
                normal=world_manifold.normal,
                impulse=0.0  # Will be calculated in PostSolve
            )
            
            # Notify game objects of collision
            if hasattr(body_a.game_object, 'on_collision_begin'):
                body_a.game_object.on_collision_begin(collision_info)
            if hasattr(body_b.game_object, 'on_collision_begin'):
                body_b.game_object.on_collision_begin(collision_info)
    
    def EndContact(self, contact: b2Contact):
        """Called when two fixtures cease to touch"""
        fixture_a = contact.fixtureA
        fixture_b = contact.fixtureB
        
        body_a = fixture_a.body.userData
        body_b = fixture_b.body.userData
        
        if body_a and body_b:
            # Notify game objects of collision end
            if hasattr(body_a.game_object, 'on_collision_end'):
                body_a.game_object.on_collision_end(body_b)
            if hasattr(body_b.game_object, 'on_collision_end'):
                body_b.game_object.on_collision_end(body_a)
    
    def PostSolve(self, contact: b2Contact, impulse: b2ContactImpulse):
        """Called after collision response is calculated"""
        if impulse.normalImpulses[0] > 2.0:  # Significant collision
            fixture_a = contact.fixtureA
            fixture_b = contact.fixtureB
            
            body_a = fixture_a.body.userData
            body_b = fixture_b.body.userData
            
            if body_a and body_b:
                # Calculate collision intensity
                collision_force = impulse.normalImpulses[0]
                
                # Notify game objects of significant collision
                if hasattr(body_a.game_object, 'on_collision_impact'):
                    body_a.game_object.on_collision_impact(body_b, collision_force)
                if hasattr(body_b.game_object, 'on_collision_impact'):
                    body_b.game_object.on_collision_impact(body_a, collision_force)

class PhysicsManager:
    """
    Advanced Physics Manager based on Carnage3D's implementation.
    Manages Box2D physics world and all physics bodies.
    """
    
    def __init__(self):
        # Physics world configuration
        self.gravity = b2Vec2(0, 0)  # Top-down game, no gravity
        self.world = b2World(gravity=self.gravity, doSleep=True)
        
        # Contact listener for collision handling
        self.contact_listener = ContactListener(self)
        self.world.contactListener = self.contact_listener
        
        # Physics simulation parameters
        self.time_step = 1.0 / 60.0  # 60 Hz
        self.velocity_iterations = 8
        self.position_iterations = 3
        self.accumulator = 0.0
        
        # Body management
        self.physics_bodies: List[PhysicsBody] = []
        self.bodies_to_destroy: List[PhysicsBody] = []
        
        # Map collision bodies (static)
        self.map_bodies: List[PhysicsBody] = []
        
        # Performance tracking
        self.simulation_time = 0.0
        self.collision_count = 0
        
        print("🔧 PhysicsManager initialized with Box2D")
        print(f"   Time step: {self.time_step}s")
        print(f"   Iterations: {self.velocity_iterations}v, {self.position_iterations}p")
    
    def create_body(self, config: PhysicsBodyConfig, game_object: Any = None) -> PhysicsBody:
        """Create a physics body with the specified configuration"""
        
        # Create Box2D body definition
        body_def = b2BodyDef()
        body_def.type = config.body_type
        body_def.position = config.position
        body_def.angle = config.angle
        body_def.linearDamping = config.linear_damping
        body_def.angularDamping = config.angular_damping
        
        # Create the body
        body = self.world.CreateBody(body_def)
        
        # Wrap in our PhysicsBody class
        physics_body = PhysicsBody(body, game_object)
        self.physics_bodies.append(physics_body)
        
        return physics_body
    
    def create_box_fixture(self, physics_body: PhysicsBody, width: float, height: float, 
                          config: PhysicsBodyConfig) -> None:
        """Create a box-shaped fixture for a physics body"""
        
        # Create box shape
        box_shape = b2PolygonShape()
        box_shape.SetAsBox(width / 2, height / 2)
        
        # Create fixture definition
        fixture_def = b2FixtureDef()
        fixture_def.shape = box_shape
        fixture_def.density = config.density
        fixture_def.friction = config.friction
        fixture_def.restitution = config.restitution
        fixture_def.isSensor = config.is_sensor
        
        # Set collision filtering
        fixture_def.filter.categoryBits = config.category.value
        fixture_def.filter.maskBits = config.mask.value
        
        # Create the fixture
        physics_body.body.CreateFixture(fixture_def)
    
    def create_circle_fixture(self, physics_body: PhysicsBody, radius: float,
                             config: PhysicsBodyConfig, offset: Tuple[float, float] = (0, 0)) -> None:
        """Create a circle-shaped fixture for a physics body"""
        
        # Create circle shape
        circle_shape = b2CircleShape()
        circle_shape.radius = radius
        circle_shape.pos = offset
        
        # Create fixture definition
        fixture_def = b2FixtureDef()
        fixture_def.shape = circle_shape
        fixture_def.density = config.density
        fixture_def.friction = config.friction
        fixture_def.restitution = config.restitution
        fixture_def.isSensor = config.is_sensor
        
        # Set collision filtering
        fixture_def.filter.categoryBits = config.category.value
        fixture_def.filter.maskBits = config.mask.value
        
        # Create the fixture
        physics_body.body.CreateFixture(fixture_def)
    
    def create_polygon_fixture(self, physics_body: PhysicsBody, vertices: List[Tuple[float, float]],
                              config: PhysicsBodyConfig) -> None:
        """Create a polygon-shaped fixture for a physics body"""
        
        # Create polygon shape
        polygon_shape = b2PolygonShape()
        polygon_shape.vertices = vertices
        
        # Create fixture definition
        fixture_def = b2FixtureDef()
        fixture_def.shape = polygon_shape
        fixture_def.density = config.density
        fixture_def.friction = config.friction
        fixture_def.restitution = config.restitution
        fixture_def.isSensor = config.is_sensor
        
        # Set collision filtering
        fixture_def.filter.categoryBits = config.category.value
        fixture_def.filter.maskBits = config.mask.value
        
        # Create the fixture
        physics_body.body.CreateFixture(fixture_def)
    
    def create_vehicle_body(self, position: Tuple[float, float], width: float, height: float,
                           game_object: Any = None) -> PhysicsBody:
        """Create a physics body optimized for vehicles"""
        
        config = PhysicsBodyConfig(
            body_type=b2_dynamicBody,
            position=position,
            linear_damping=0.8,  # Higher damping for realistic vehicle behavior
            angular_damping=3.0,  # Prevent excessive spinning
            category=CollisionCategory.VEHICLE,
            mask=CollisionCategory.MAP | CollisionCategory.VEHICLE | CollisionCategory.PEDESTRIAN,
            density=1.0,
            friction=0.7,
            restitution=0.2
        )
        
        physics_body = self.create_body(config, game_object)
        self.create_box_fixture(physics_body, width, height, config)
        
        return physics_body
    
    def create_pedestrian_body(self, position: Tuple[float, float], radius: float,
                              game_object: Any = None) -> PhysicsBody:
        """Create a physics body optimized for pedestrians"""
        
        config = PhysicsBodyConfig(
            body_type=b2_dynamicBody,
            position=position,
            linear_damping=5.0,  # High damping for responsive control
            angular_damping=10.0,  # Minimal rotation
            category=CollisionCategory.PEDESTRIAN,
            mask=CollisionCategory.MAP | CollisionCategory.VEHICLE | CollisionCategory.PEDESTRIAN,
            density=0.8,
            friction=0.8,
            restitution=0.0
        )
        
        physics_body = self.create_body(config, game_object)
        self.create_circle_fixture(physics_body, radius, config)
        
        return physics_body
    
    def create_map_collision(self, x: float, y: float, width: float, height: float) -> PhysicsBody:
        """Create static collision body for map geometry"""
        
        config = PhysicsBodyConfig(
            body_type=b2_staticBody,
            position=(x + width/2, y + height/2),
            category=CollisionCategory.MAP,
            mask=CollisionCategory.ALL,
            density=0.0,
            friction=0.5,
            restitution=0.1
        )
        
        physics_body = self.create_body(config)
        self.create_box_fixture(physics_body, width, height, config)
        self.map_bodies.append(physics_body)
        
        return physics_body
    
    def ray_cast(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> Optional[Dict]:
        """Cast a ray and return the first intersection"""
        
        class RaycastCallback(b2RayCastCallback):
            def __init__(self):
                super().__init__()
                self.hit = False
                self.point = None
                self.normal = None
                self.fixture = None
                self.fraction = 1.0
                
            def ReportFixture(self, fixture, point, normal, fraction):
                self.hit = True
                self.point = point
                self.normal = normal
                self.fixture = fixture
                self.fraction = fraction
                return fraction  # Continue to find closest hit
        
        callback = RaycastCallback()
        self.world.RayCast(callback, point1, point2)
        
        if callback.hit:
            physics_body = callback.fixture.body.userData if callback.fixture.body.userData else None
            return {
                'hit': True,
                'point': (callback.point.x, callback.point.y),
                'normal': (callback.normal.x, callback.normal.y),
                'fraction': callback.fraction,
                'physics_body': physics_body
            }
        
        return {'hit': False}
    
    def query_aabb(self, lower_bound: Tuple[float, float], upper_bound: Tuple[float, float]) -> List[PhysicsBody]:
        """Query all bodies within an axis-aligned bounding box"""
        
        class QueryCallback(b2QueryCallback):
            def __init__(self):
                super().__init__()
                self.bodies = []
                
            def ReportFixture(self, fixture):
                physics_body = fixture.body.userData
                if physics_body:
                    self.bodies.append(physics_body)
                return True  # Continue querying
        
        callback = QueryCallback()
        aabb = b2AABB()
        aabb.lowerBound = lower_bound
        aabb.upperBound = upper_bound
        
        self.world.QueryAABB(callback, aabb)
        return callback.bodies
    
    def update_frame(self, delta_time: float):
        """Update physics simulation with fixed timestep"""
        
        # Accumulate time
        self.accumulator += delta_time
        
        # Simulate with fixed timestep
        while self.accumulator >= self.time_step:
            self.world.Step(self.time_step, self.velocity_iterations, self.position_iterations)
            self.accumulator -= self.time_step
        
        # Clear forces for next step
        self.world.ClearForces()
        
        # Clean up destroyed bodies
        self._cleanup_destroyed_bodies()
        
        # Update simulation time
        self.simulation_time += self.time_step
    
    def destroy_body(self, physics_body: PhysicsBody):
        """Mark a physics body for destruction"""
        if physics_body in self.physics_bodies:
            self.bodies_to_destroy.append(physics_body)
    
    def _cleanup_destroyed_bodies(self):
        """Remove destroyed bodies from the world"""
        for physics_body in self.bodies_to_destroy:
            if physics_body in self.physics_bodies:
                self.physics_bodies.remove(physics_body)
            if physics_body in self.map_bodies:
                self.map_bodies.remove(physics_body)
            
            # Destroy the Box2D body
            if physics_body.body:
                self.world.DestroyBody(physics_body.body)
                physics_body.body = None
        
        self.bodies_to_destroy.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get physics simulation statistics"""
        return {
            'body_count': len(self.physics_bodies),
            'map_bodies': len(self.map_bodies),
            'simulation_time': self.simulation_time,
            'time_step': self.time_step,
            'world_bodies': self.world.bodyCount,
            'world_joints': self.world.jointCount,
            'world_contacts': self.world.contactCount
        }
    
    def debug_draw_bodies(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Draw physics bodies for debugging (simple wireframe)"""
        for physics_body in self.physics_bodies:
            body = physics_body.body
            
            # Convert world position to screen position
            world_pos = body.position
            screen_x = int((world_pos.x - camera_offset[0]) * 16)  # 16 pixels per meter
            screen_y = int((world_pos.y - camera_offset[1]) * 16)
            
            # Draw different colors based on body type
            if body.type == b2_staticBody:
                color = (255, 0, 0)  # Red for static
            elif body.type == b2_dynamicBody:
                color = (0, 255, 0)  # Green for dynamic
            else:
                color = (0, 0, 255)  # Blue for kinematic
            
            # Draw a simple representation
            pygame.draw.circle(surface, color, (screen_x, screen_y), 8, 2)
            
            # Draw velocity vector
            if body.type == b2_dynamicBody:
                vel = body.linearVelocity
                if vel.length > 0.1:
                    end_x = screen_x + int(vel.x * 10)
                    end_y = screen_y + int(vel.y * 10)
                    pygame.draw.line(surface, color, (screen_x, screen_y), (end_x, end_y), 2)

# Global physics manager instance
_physics_manager: Optional[PhysicsManager] = None

def get_physics_manager() -> PhysicsManager:
    """Get the global physics manager instance"""
    global _physics_manager
    if _physics_manager is None:
        _physics_manager = PhysicsManager()
    return _physics_manager

def initialize_physics() -> PhysicsManager:
    """Initialize the physics system"""
    global _physics_manager
    _physics_manager = PhysicsManager()
    return _physics_manager

def shutdown_physics():
    """Shutdown the physics system"""
    global _physics_manager
    if _physics_manager:
        # Clean up all bodies
        _physics_manager.bodies_to_destroy = _physics_manager.physics_bodies.copy()
        _physics_manager._cleanup_destroyed_bodies()
        _physics_manager = None