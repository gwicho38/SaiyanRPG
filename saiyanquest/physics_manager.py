#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Physics System with Box2D Integration

import math
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

try:
    import Box2D
    from Box2D import b2World, b2Vec2, b2BodyDef, b2Body, b2FixtureDef, b2PolygonShape, b2CircleShape
    from Box2D import b2ContactListener, b2Contact, b2Manifold
    BOX2D_AVAILABLE = True
except ImportError:
    BOX2D_AVAILABLE = False
    print("Warning: Box2D not available, falling back to basic physics")
    # Create dummy classes for when Box2D is not available
    class b2ContactListener:
        pass
    class b2Contact:
        pass
    class b2Manifold:
        pass

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class PhysicsBodyType(Enum):
    """Types of physics bodies"""
    STATIC = "static"
    KINEMATIC = "kinematic" 
    DYNAMIC = "dynamic"


class CollisionCategory(Enum):
    """Collision categories for filtering"""
    PLAYER = 0x0001
    VEHICLE = 0x0002
    PEDESTRIAN = 0x0004
    PROJECTILE = 0x0008
    WORLD = 0x0010
    WATER = 0x0020
    EXPLOSION = 0x0040


@dataclass
class PhysicsBody:
    """Wrapper for Box2D physics body with game-specific data"""
    body_id: int
    body_type: PhysicsBodyType
    position: Tuple[float, float]
    angle: float
    velocity: Tuple[float, float]
    angular_velocity: float
    mass: float
    friction: float
    restitution: float
    collision_category: CollisionCategory
    user_data: Any = None
    is_sensor: bool = False

    # Box2D specific
    b2_body: Optional[Any] = None
    b2_fixture: Optional[Any] = None

    def set_position(self, x: float, y: float) -> None:
        """Set body position"""
        self.position = (x, y)
        if BOX2D_AVAILABLE and self.b2_body:
            self.b2_body.position = b2Vec2(x, y)

    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        """Set body velocity"""
        self.velocity = velocity
        if BOX2D_AVAILABLE and self.b2_body:
            self.b2_body.linearVelocity = b2Vec2(velocity[0], velocity[1])


@dataclass
class CollisionInfo:
    """Information about a collision"""
    body_a: PhysicsBody
    body_b: PhysicsBody
    contact_point: Tuple[float, float]
    normal: Tuple[float, float]
    impulse: float
    separation: float
    timestamp: float


class CustomContactListener(b2ContactListener):
    """Custom contact listener for handling collisions"""
    
    def __init__(self, physics_manager):
        super().__init__()
        self.physics_manager = physics_manager
        self.collisions: List[CollisionInfo] = []
    
    def BeginContact(self, contact: b2Contact):
        """Called when two fixtures begin to touch"""
        if not BOX2D_AVAILABLE:
            return
            
        fixture_a = contact.fixtureA
        fixture_b = contact.fixtureB
        
        body_a = fixture_a.body
        body_b = fixture_b.body
        
        # Get user data (our PhysicsBody objects)
        physics_body_a = body_a.userData
        physics_body_b = body_b.userData
        
        if physics_body_a and physics_body_b:
            # Calculate contact point
            world_manifold = contact.worldManifold
            contact_point = (world_manifold.points[0].x, world_manifold.points[0].y)
            normal = (world_manifold.normal.x, world_manifold.normal.y)
            
            collision = CollisionInfo(
                body_a=physics_body_a,
                body_b=physics_body_b,
                contact_point=contact_point,
                normal=normal,
                impulse=0.0,  # Will be calculated in PreSolve
                separation=contact.manifold.points[0].separation,
                timestamp=time.time()
            )
            
            self.collisions.append(collision)
            self.physics_manager._handle_collision(collision)
    
    def PreSolve(self, contact: b2Contact, old_manifold: b2Manifold):
        """Called before collision resolution"""
        pass
    
    def PostSolve(self, contact: b2Contact, impulse: b2Manifold):
        """Called after collision resolution"""
        pass
    
    def EndContact(self, contact: b2Contact):
        """Called when two fixtures cease to touch"""
        pass


class PhysicsManager:
    """Advanced physics manager with Box2D integration"""
    
    def __init__(self, gravity: Tuple[float, float] = (0, 0)):
        self.gravity = gravity
        self.bodies: Dict[int, PhysicsBody] = {}
        self.next_body_id = 1
        
        # Initialize Box2D world if available
        if BOX2D_AVAILABLE:
            self.world = b2World(b2Vec2(gravity[0], gravity[1]))
            self.contact_listener = CustomContactListener(self)
            self.world.contactListener = self.contact_listener
            print("✅ Box2D physics world initialized")
        else:
            self.world = None
            self.contact_listener = None
            print("⚠️ Using basic physics (Box2D not available)")
        
        # Physics settings
        self.time_step = 1.0 / 60.0  # 60 FPS
        self.velocity_iterations = 8
        self.position_iterations = 3
        
        # Collision callbacks
        self.collision_callbacks: Dict[Tuple[CollisionCategory, CollisionCategory], Callable] = {}
        
        # Debug settings
        self.debug_draw = False
        self.debug_collisions = True
        
        print(f"🔧 PhysicsManager initialized with gravity: {gravity}")
    
    def create_body(self, body_type: PhysicsBodyType, position: Tuple[float, float], 
                   shape_data: Dict, collision_category: CollisionCategory,
                   user_data: Any = None) -> PhysicsBody:
        """Create a new physics body"""
        body_id = self.next_body_id
        self.next_body_id += 1
        
        physics_body = PhysicsBody(
            body_id=body_id,
            body_type=body_type,
            position=position,
            angle=0.0,
            velocity=(0.0, 0.0),
            angular_velocity=0.0,
            mass=shape_data.get('mass', 1.0),
            friction=shape_data.get('friction', 0.3),
            restitution=shape_data.get('restitution', 0.1),
            collision_category=collision_category,
            user_data=user_data,
            is_sensor=shape_data.get('is_sensor', False)
        )
        
        if BOX2D_AVAILABLE and self.world:
            # Create Box2D body
            body_def = b2BodyDef()
            
            if body_type == PhysicsBodyType.STATIC:
                body_def.type = Box2D.b2_staticBody
            elif body_type == PhysicsBodyType.KINEMATIC:
                body_def.type = Box2D.b2_kinematicBody
            else:  # DYNAMIC
                body_def.type = Box2D.b2_dynamicBody
            
            body_def.position = b2Vec2(position[0], position[1])
            body_def.userData = physics_body
            
            b2_body = self.world.CreateBody(body_def)
            physics_body.b2_body = b2_body
            
            # Create fixture based on shape
            fixture_def = b2FixtureDef()
            fixture_def.density = physics_body.mass
            fixture_def.friction = physics_body.friction
            fixture_def.restitution = physics_body.restitution
            fixture_def.isSensor = physics_body.is_sensor
            
            # Set collision filtering
            fixture_def.filter.categoryBits = collision_category.value
            fixture_def.filter.maskBits = self._get_collision_mask(collision_category)
            
            # Create shape
            if shape_data['type'] == 'box':
                width = shape_data['width']
                height = shape_data['height']
                fixture_def.shape = b2PolygonShape(box=(width/2, height/2))
            elif shape_data['type'] == 'circle':
                radius = shape_data['radius']
                fixture_def.shape = b2CircleShape(radius=radius)
            elif shape_data['type'] == 'polygon':
                vertices = [b2Vec2(v[0], v[1]) for v in shape_data['vertices']]
                fixture_def.shape = b2PolygonShape(vertices=vertices)
            
            b2_fixture = b2_body.CreateFixture(fixture_def)
            physics_body.b2_fixture = b2_fixture
        
        self.bodies[body_id] = physics_body
        print(f"🔧 Created physics body {body_id} ({body_type.value}) at {position}")
        return physics_body
    
    def _get_collision_mask(self, category: CollisionCategory) -> int:
        """Get collision mask for a category"""
        # Default collision masks - can be customized
        masks = {
            CollisionCategory.PLAYER: 0xFFFF,  # Collide with everything
            CollisionCategory.VEHICLE: 0xFFFF,  # Collide with everything
            CollisionCategory.PEDESTRIAN: 0xFFFF,  # Collide with everything
            CollisionCategory.PROJECTILE: 0xFFFF,  # Collide with everything
            CollisionCategory.WORLD: 0xFFFF,  # Collide with everything
            CollisionCategory.WATER: CollisionCategory.VEHICLE.value | CollisionCategory.PEDESTRIAN.value,
            CollisionCategory.EXPLOSION: CollisionCategory.VEHICLE.value | CollisionCategory.PEDESTRIAN.value
        }
        return masks.get(category, 0xFFFF)
    
    def update(self, dt: float) -> None:
        """Update physics simulation"""
        if not BOX2D_AVAILABLE or not self.world:
            self._update_basic_physics(dt)
            return
        
        # Step the Box2D world
        self.world.Step(dt, self.velocity_iterations, self.position_iterations)
        
        # Update our physics body data from Box2D
        for body in self.bodies.values():
            if body.b2_body:
                b2_pos = body.b2_body.position
                b2_vel = body.b2_body.linearVelocity
                
                body.position = (b2_pos.x, b2_pos.y)
                body.angle = body.b2_body.angle
                body.velocity = (b2_vel.x, b2_vel.y)
                body.angular_velocity = body.b2_body.angularVelocity
        
        # Clear old collisions
        if self.contact_listener:
            self.contact_listener.collisions.clear()
    
    def _update_basic_physics(self, dt: float) -> None:
        """Fallback basic physics when Box2D is not available"""
        for body in self.bodies.values():
            if body.body_type == PhysicsBodyType.DYNAMIC:
                # Simple Euler integration
                new_x = body.position[0] + body.velocity[0] * dt
                new_y = body.position[1] + body.velocity[1] * dt
                body.position = (new_x, new_y)
                
                # Apply gravity
                if self.gravity != (0, 0):
                    new_vx = body.velocity[0] + self.gravity[0] * dt
                    new_vy = body.velocity[1] + self.gravity[1] * dt
                    body.velocity = (new_vx, new_vy)
    
    def apply_force(self, body_id: int, force: Tuple[float, float], 
                   point: Optional[Tuple[float, float]] = None) -> None:
        """Apply force to a body"""
        if body_id not in self.bodies:
            return
        
        body = self.bodies[body_id]
        
        if BOX2D_AVAILABLE and body.b2_body:
            if point:
                body.b2_body.ApplyForce(b2Vec2(force[0], force[1]), b2Vec2(point[0], point[1]), True)
            else:
                body.b2_body.ApplyForceToCenter(b2Vec2(force[0], force[1]), True)
        else:
            # Basic physics: F = ma, so a = F/m
            acceleration_x = force[0] / body.mass
            acceleration_y = force[1] / body.mass
            
            new_vx = body.velocity[0] + acceleration_x * self.time_step
            new_vy = body.velocity[1] + acceleration_y * self.time_step
            body.velocity = (new_vx, new_vy)
    
    def apply_impulse(self, body_id: int, impulse: Tuple[float, float],
                     point: Optional[Tuple[float, float]] = None) -> None:
        """Apply impulse to a body"""
        if body_id not in self.bodies:
            return
        
        body = self.bodies[body_id]
        
        if BOX2D_AVAILABLE and body.b2_body:
            if point:
                body.b2_body.ApplyLinearImpulse(b2Vec2(impulse[0], impulse[1]), b2Vec2(point[0], point[1]), True)
            else:
                body.b2_body.ApplyLinearImpulseToCenter(b2Vec2(impulse[0], impulse[1]), True)
        else:
            # Basic physics: impulse changes velocity directly
            new_vx = body.velocity[0] + impulse[0] / body.mass
            new_vy = body.velocity[1] + impulse[1] / body.mass
            body.velocity = (new_vx, new_vy)
    
    def set_velocity(self, body_id: int, velocity: Tuple[float, float]) -> None:
        """Set body velocity"""
        if body_id not in self.bodies:
            return
        
        body = self.bodies[body_id]
        body.velocity = velocity
        
        if BOX2D_AVAILABLE and body.b2_body:
            body.b2_body.linearVelocity = b2Vec2(velocity[0], velocity[1])
    
    def set_position(self, body_id: int, position: Tuple[float, float]) -> None:
        """Set body position"""
        if body_id not in self.bodies:
            return
        
        body = self.bodies[body_id]
        body.position = position
        
        if BOX2D_AVAILABLE and body.b2_body:
            body.b2_body.position = b2Vec2(position[0], position[1])
    
    def get_body(self, body_id: int) -> Optional[PhysicsBody]:
        """Get physics body by ID"""
        return self.bodies.get(body_id)
    
    def remove_body(self, body_id: int) -> None:
        """Remove a physics body"""
        if body_id not in self.bodies:
            return
        
        body = self.bodies[body_id]
        
        if BOX2D_AVAILABLE and body.b2_body and self.world:
            self.world.DestroyBody(body.b2_body)
        
        del self.bodies[body_id]
        print(f"🔧 Removed physics body {body_id}")
    
    def raycast(self, start: Tuple[float, float], end: Tuple[float, float],
                collision_category: Optional[CollisionCategory] = None) -> Optional[CollisionInfo]:
        """Perform raycast from start to end point"""
        if not BOX2D_AVAILABLE or not self.world:
            return self._basic_raycast(start, end)
        
        # Box2D raycast
        def raycast_callback(fixture, point, normal, fraction):
            # Return the closest hit
            return fraction
        
        hit_fixture = self.world.RayCastOne(
            b2Vec2(start[0], start[1]),
            b2Vec2(end[0], end[1]),
            raycast_callback
        )
        
        if hit_fixture:
            # Calculate hit point
            direction = (end[0] - start[0], end[1] - start[1])
            distance = math.sqrt(direction[0]**2 + direction[1]**2)
            hit_point = (start[0] + direction[0] * distance, start[1] + direction[1] * distance)
            
            return CollisionInfo(
                body_a=None,  # Raycast doesn't have a body A
                body_b=hit_fixture.body.userData,
                contact_point=hit_point,
                normal=(0, 0),  # Would need to calculate
                impulse=0.0,
                separation=0.0,
                timestamp=time.time()
            )
        
        return None
    
    def _basic_raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[CollisionInfo]:
        """Basic raycast implementation without Box2D"""
        # Simple line-circle intersection for basic physics
        direction = (end[0] - start[0], end[1] - start[1])
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        
        if length == 0:
            return None
        
        # Normalize direction
        direction = (direction[0] / length, direction[1] / length)
        
        # Check against all bodies (simplified)
        for body in self.bodies.values():
            if body.collision_category == CollisionCategory.WORLD:
                continue
            
            # Simple distance check (would need proper shape intersection)
            dx = body.position[0] - start[0]
            dy = body.position[1] - start[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 50:  # Arbitrary threshold
                return CollisionInfo(
                    body_a=None,
                    body_b=body,
                    contact_point=body.position,
                    normal=(0, 0),
                    impulse=0.0,
                    separation=0.0,
                    timestamp=time.time()
                )
        
        return None
    
    def _handle_collision(self, collision: CollisionInfo) -> None:
        """Handle collision events"""
        if not self.debug_collisions:
            return
        
        print(f"💥 Collision: {collision.body_a.body_id if collision.body_a else 'Raycast'} -> {collision.body_b.body_id}")
        
        # Call registered collision callbacks
        if collision.body_a and collision.body_b:
            callback_key = (collision.body_a.collision_category, collision.body_b.collision_category)
            if callback_key in self.collision_callbacks:
                self.collision_callbacks[callback_key](collision)
    
    def register_collision_callback(self, category_a: CollisionCategory, category_b: CollisionCategory,
                                  callback: Callable[[CollisionInfo], None]) -> None:
        """Register a collision callback for specific categories"""
        self.collision_callbacks[(category_a, category_b)] = callback
        print(f"🔧 Registered collision callback: {category_a.value} -> {category_b.value}")
    
    def draw_debug(self, screen, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Draw physics bodies for debugging"""
        if not self.debug_draw or not PYGAME_AVAILABLE:
            return
        
        for body in self.bodies.values():
            # Convert world position to screen position
            screen_x = body.position[0] - camera_offset[0]
            screen_y = body.position[1] - camera_offset[1]
            
            # Draw body outline
            color = (255, 0, 0) if body.body_type == PhysicsBodyType.DYNAMIC else (0, 255, 0)
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 5)
            
            # Draw velocity vector
            if body.velocity != (0, 0):
                end_x = screen_x + body.velocity[0] * 10
                end_y = screen_y + body.velocity[1] * 10
                pygame.draw.line(screen, (255, 255, 0), (screen_x, screen_y), (end_x, end_y), 2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get physics system statistics"""
        return {
            'total_bodies': len(self.bodies),
            'dynamic_bodies': len([b for b in self.bodies.values() if b.body_type == PhysicsBodyType.DYNAMIC]),
            'static_bodies': len([b for b in self.bodies.values() if b.body_type == PhysicsBodyType.STATIC]),
            'kinematic_bodies': len([b for b in self.bodies.values() if b.body_type == PhysicsBodyType.KINEMATIC]),
            'box2d_available': BOX2D_AVAILABLE,
            'collision_callbacks': len(self.collision_callbacks)
        }


# Global physics manager instance
_physics_manager = None

def initialize_physics(gravity: Tuple[float, float] = (0, 0)) -> PhysicsManager:
    """Initialize the global physics manager"""
    global _physics_manager
    if _physics_manager is None:
        _physics_manager = PhysicsManager(gravity)
    return _physics_manager

def get_physics_manager() -> Optional[PhysicsManager]:
    """Get the global physics manager instance"""
    return _physics_manager

# Test the physics system
if __name__ == "__main__":
    print("🧪 Testing PhysicsManager...")
    
    if PYGAME_AVAILABLE:
        # Initialize pygame for testing
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()
        
        # Create physics manager
        physics = PhysicsManager(gravity=(0, 0))  # Top-down game, no gravity
        
        # Create some test bodies
        ground = physics.create_body(
            PhysicsBodyType.STATIC,
            (400, 550),
            {'type': 'box', 'width': 800, 'height': 100, 'mass': 0},
            CollisionCategory.WORLD
        )
        
        box = physics.create_body(
            PhysicsBodyType.DYNAMIC,
            (400, 300),
            {'type': 'box', 'width': 50, 'height': 50, 'mass': 1.0},
            CollisionCategory.VEHICLE
        )
        
        # Apply some force
        physics.apply_force(box.body_id, (100, 0))
        
        # Test loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update physics
            dt = clock.tick(60) / 1000.0
            physics.update(dt)
            
            # Draw
            screen.fill((0, 0, 0))
            physics.draw_debug(screen)
            pygame.display.flip()
        
        pygame.quit()
    else:
        # Simple test without pygame
        physics = PhysicsManager(gravity=(0, 0))
        
        # Create some test bodies
        ground = physics.create_body(
            PhysicsBodyType.STATIC,
            (400, 550),
            {'type': 'box', 'width': 800, 'height': 100, 'mass': 0},
            CollisionCategory.WORLD
        )
        
        box = physics.create_body(
            PhysicsBodyType.DYNAMIC,
            (400, 300),
            {'type': 'box', 'width': 50, 'height': 50, 'mass': 1.0},
            CollisionCategory.VEHICLE
        )
        
        # Apply some force
        physics.apply_force(box.body_id, (100, 0))
        
        # Run simulation
        for i in range(300):  # 5 seconds at 60 FPS
            dt = 1.0 / 60.0
            physics.update(dt)
            
            if i % 60 == 0:  # Print every second
                body = physics.get_body(box.body_id)
                print(f"  Frame {i}: Position = ({body.position[0]:.1f}, {body.position[1]:.1f})")
    
    print("✅ PhysicsManager test completed")