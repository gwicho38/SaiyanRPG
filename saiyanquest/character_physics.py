#!/usr/bin/env python3
"""
Advanced Character/Pedestrian Physics System
Implements realistic character movement, ragdoll physics, and collision handling.
Based on Carnage3D pedestrian mechanics.
"""

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .physics_manager import (
    PhysicsManager, PhysicsBody, PhysicsBodyType,
    CollisionCategory
)


class CharacterState(Enum):
    """Character physical states"""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    RAGDOLL = "ragdoll"
    GETTING_UP = "getting_up"
    IN_VEHICLE = "in_vehicle"
    ENTERING_VEHICLE = "entering_vehicle"
    EXITING_VEHICLE = "exiting_vehicle"
    CLIMBING = "climbing"
    SWIMMING = "swimming"
    DEAD = "dead"
    STUNNED = "stunned"


class CharacterType(Enum):
    """Types of characters/pedestrians"""
    CIVILIAN = "civilian"
    POLICE = "police"
    GANG_MEMBER = "gang_member"
    PARAMEDIC = "paramedic"
    FIREFIGHTER = "firefighter"
    BUSINESSMAN = "businessman"
    TOURIST = "tourist"
    ATHLETE = "athlete"
    ELDERLY = "elderly"
    CHILD = "child"
    PLAYER = "player"


@dataclass
class CharacterStats:
    """Character physical attributes"""
    max_health: float = 100.0
    max_stamina: float = 100.0
    walk_speed: float = 50.0  # pixels/second
    run_speed: float = 150.0  # pixels/second
    jump_force: float = 300.0
    mass: float = 70.0  # kg
    strength: float = 1.0
    agility: float = 1.0
    reaction_time: float = 0.3  # seconds


class CharacterPhysics:
    """Physics component for a character"""
    
    def __init__(self, character_type: CharacterType, x: float, y: float):
        self.character_type = character_type
        self.physics_manager = PhysicsManager(gravity=(0, 0))
        
        # Physical properties - initialize stats first
        self.stats = self._get_character_stats(character_type)
        self.stats.radius = 0.4  # Add radius to stats
        
        # Create physics body for character
        self.physics_body = self._create_character_body(x, y)
        
        # Character state
        self.state = CharacterState.IDLE
        self.previous_state = CharacterState.IDLE
        self.state_timer = 0.0
        self.health = self.stats.max_health
        self.stamina = self.stats.max_stamina
        self.is_grounded = True
        self.is_stunned = False
        self.stun_timer = 0.0
        
        # Movement state
        self.movement_vector = (0.0, 0.0)
        self.facing_angle = 0.0
        self.target_velocity = (0.0, 0.0)
        
        # Ragdoll physics
        self.ragdoll_active = False
        self.ragdoll_joints = []
        self.ragdoll_timer = 0.0
        self.can_get_up = True
        
        # Vehicle interaction
        self.current_vehicle = None
        self.vehicle_seat = None
        
        # Collision tracking
        self.ground_contacts = 0
        self.wall_contacts = 0
        self.last_collision_force = 0.0
        
        print(f"👤 Character physics initialized: {character_type.value} at ({x:.1f}, {y:.1f})")
    
    def _create_character_body(self, x: float, y: float) -> PhysicsBody:
        """Create Box2D body for character"""
        # Convert pixels to meters
        physics_x = x / 16.0
        physics_y = y / 16.0
        
        # Character is represented as a capsule (circle for now)
        body = self.physics_manager.create_body(
            PhysicsBodyType.DYNAMIC,
            position=(physics_x, physics_y),
            shape_data={'type': 'circle', 'radius': 0.4, 'mass': self.stats.mass},
            collision_category=CollisionCategory.PEDESTRIAN,
            user_data=self
        )
        
        # Set up character physics properties
        if body.b2_body:
            body.b2_body.fixedRotation = True  # Characters don't rotate in top-down view
        
        return body
    
    def _get_character_stats(self, character_type: CharacterType) -> CharacterStats:
        """Get stats based on character type"""
        stats_map = {
            CharacterType.CIVILIAN: CharacterStats(),
            CharacterType.POLICE: CharacterStats(
                max_health=120, max_stamina=120, 
                run_speed=160, strength=1.2, agility=1.1
            ),
            CharacterType.GANG_MEMBER: CharacterStats(
                max_health=110, strength=1.3, agility=0.9
            ),
            CharacterType.ATHLETE: CharacterStats(
                max_stamina=150, run_speed=180, 
                jump_force=350, agility=1.3
            ),
            CharacterType.ELDERLY: CharacterStats(
                max_health=60, max_stamina=50,
                walk_speed=30, run_speed=60,
                strength=0.6, agility=0.5, reaction_time=0.6
            ),
            CharacterType.CHILD: CharacterStats(
                max_health=50, max_stamina=80,
                walk_speed=40, run_speed=100,
                mass=35, strength=0.4, agility=1.2
            ),
            CharacterType.PLAYER: CharacterStats(
                max_health=100, max_stamina=100,
                run_speed=170, strength=1.0, agility=1.0
            )
        }
        
        return stats_map.get(character_type, CharacterStats())
    
    @property
    def x(self) -> float:
        """Get character X position in pixels"""
        return self.physics_body.position[0] * 16.0
    
    @property
    def y(self) -> float:
        """Get character Y position in pixels"""
        return self.physics_body.position[1] * 16.0
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Get character velocity in pixels/second"""
        vx, vy = self.physics_body.velocity
        return (vx * 16.0, vy * 16.0)
    
    def update(self, dt: float) -> None:
        """Update character physics"""
        # Update state timer
        self.state_timer += dt
        
        # Update stun timer
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
                if self.state == CharacterState.STUNNED:
                    self.set_state(CharacterState.IDLE)
        
        # Update stamina
        if self.state == CharacterState.RUNNING:
            self.stamina = max(0, self.stamina - 10 * dt)
            if self.stamina == 0:
                self.set_state(CharacterState.WALKING)
        else:
            self.stamina = min(self.stats.max_stamina, self.stamina + 5 * dt)
        
        # Update movement based on state
        if not self.is_stunned and not self.ragdoll_active:
            self._update_movement(dt)
        
        # Update ragdoll physics
        if self.ragdoll_active:
            self._update_ragdoll(dt)
        
        # Check ground contact
        self._check_ground_contact()
        
        # Update facing angle based on movement
        if abs(self.movement_vector[0]) > 0.1 or abs(self.movement_vector[1]) > 0.1:
            self.facing_angle = math.degrees(
                math.atan2(self.movement_vector[1], self.movement_vector[0])
            )
    
    def _update_movement(self, dt: float) -> None:
        """Update character movement physics"""
        if self.state == CharacterState.IN_VEHICLE:
            return  # No movement while in vehicle
        
        # Calculate target velocity based on state
        speed = 0.0
        if self.state == CharacterState.WALKING:
            speed = self.stats.walk_speed
        elif self.state == CharacterState.RUNNING:
            speed = self.stats.run_speed
        
        # Apply movement vector
        if speed > 0 and (abs(self.movement_vector[0]) > 0.1 or abs(self.movement_vector[1]) > 0.1):
            # Normalize movement vector
            length = math.sqrt(self.movement_vector[0]**2 + self.movement_vector[1]**2)
            if length > 0:
                norm_x = self.movement_vector[0] / length
                norm_y = self.movement_vector[1] / length
                
                # Calculate target velocity in meters/second
                target_vx = norm_x * speed / 16.0
                target_vy = norm_y * speed / 16.0
                
                # Apply force to reach target velocity
                current_vx, current_vy = self.physics_body.velocity
                force_x = (target_vx - current_vx) * self.stats.mass * 10
                force_y = (target_vy - current_vy) * self.stats.mass * 10
                
                self.physics_body.apply_force((force_x, force_y))
        
        # Handle jumping
        if self.state == CharacterState.JUMPING and self.is_grounded:
            jump_impulse = self.stats.jump_force * self.stats.mass / 16.0
            self.physics_body.apply_impulse((0, -jump_impulse))
            self.is_grounded = False
    
    def _check_ground_contact(self) -> None:
        """Check if character is on the ground"""
        # Simple ground check - would be enhanced with actual collision detection
        if self.physics_body.velocity[1] < 0.1 and self.state != CharacterState.JUMPING:
            self.is_grounded = True
        else:
            self.is_grounded = False
    
    def _update_ragdoll(self, dt: float) -> None:
        """Update ragdoll physics state"""
        self.ragdoll_timer += dt
        
        # Check if character can get up
        if self.ragdoll_timer > 2.0 and self.can_get_up:
            # Check if velocity is low enough to get up
            speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            if speed < 50:  # Low velocity threshold
                self.exit_ragdoll()
    
    def set_state(self, new_state: CharacterState) -> None:
        """Change character state"""
        if self.state != new_state:
            self.previous_state = self.state
            self.state = new_state
            self.state_timer = 0.0
            
            # Handle state transitions
            if new_state == CharacterState.RAGDOLL:
                self.enter_ragdoll()
            elif self.previous_state == CharacterState.RAGDOLL:
                self.exit_ragdoll()
    
    def move(self, direction_x: float, direction_y: float) -> None:
        """Set movement direction (-1 to 1 for each axis)"""
        self.movement_vector = (direction_x, direction_y)
        
        # Update state based on movement
        if abs(direction_x) > 0.1 or abs(direction_y) > 0.1:
            if self.state == CharacterState.IDLE:
                self.set_state(CharacterState.WALKING)
        else:
            if self.state in [CharacterState.WALKING, CharacterState.RUNNING]:
                self.set_state(CharacterState.IDLE)
    
    def run(self, is_running: bool) -> None:
        """Toggle between walking and running"""
        if is_running and self.stamina > 0:
            if self.state == CharacterState.WALKING:
                self.set_state(CharacterState.RUNNING)
        else:
            if self.state == CharacterState.RUNNING:
                self.set_state(CharacterState.WALKING)
    
    def jump(self) -> bool:
        """Make character jump"""
        if self.is_grounded and not self.is_stunned and self.stamina > 10:
            self.set_state(CharacterState.JUMPING)
            self.stamina -= 10
            return True
        return False
    
    def enter_ragdoll(self, impulse: Tuple[float, float] = (0, 0)) -> None:
        """Enter ragdoll physics mode"""
        self.ragdoll_active = True
        self.ragdoll_timer = 0.0
        self.set_state(CharacterState.RAGDOLL)
        
        # Remove rotation constraint
        if self.physics_body.b2_body:
            self.physics_body.b2_body.fixedRotation = False
        
        # Apply impulse if provided (e.g., from collision)
        if abs(impulse[0]) > 0.1 or abs(impulse[1]) > 0.1:
            # Apply impulse through physics manager
            from .physics_manager import get_physics_manager
            physics_manager = get_physics_manager()
            if physics_manager:
                physics_manager.apply_impulse(
                    self.physics_body.body_id,
                    (impulse[0] / 16.0, impulse[1] / 16.0)
                )
        
        # Add some random angular velocity for realistic tumbling
        angular_vel = random.uniform(-5, 5)
        if self.physics_body.b2_body:
            self.physics_body.b2_body.angularVelocity = angular_vel
        
        print(f"💫 Character entered ragdoll mode")
    
    def exit_ragdoll(self) -> None:
        """Exit ragdoll physics mode"""
        self.ragdoll_active = False
        if self.physics_body.b2_body:
            self.physics_body.b2_body.fixedRotation = True
        # Reset rotation through physics manager
        from .physics_manager import get_physics_manager
        physics_manager = get_physics_manager()
        if physics_manager and self.physics_body.b2_body:
            self.physics_body.b2_body.angle = 0
        self.set_state(CharacterState.GETTING_UP)
        
        # Getting up animation would play here
        # For now, go straight to idle after a delay
        self.state_timer = 0.0
        
        print(f"🚶 Character exiting ragdoll mode")
    
    def take_damage(self, damage: float, impact_force: Tuple[float, float] = (0, 0)) -> None:
        """Apply damage to character"""
        self.health = max(0, self.health - damage)
        
        # Stun based on damage
        if damage > 20:
            self.is_stunned = True
            self.stun_timer = damage * 0.02  # Stun duration based on damage
            
            if self.state not in [CharacterState.RAGDOLL, CharacterState.DEAD]:
                self.set_state(CharacterState.STUNNED)
        
        # Enter ragdoll if damage is severe or health depleted
        if damage > 50 or self.health <= 0:
            self.enter_ragdoll(impact_force)
            
            if self.health <= 0:
                self.set_state(CharacterState.DEAD)
                self.can_get_up = False
                print(f"☠️ Character died")
    
    def heal(self, amount: float) -> None:
        """Heal character"""
        self.health = min(self.stats.max_health, self.health + amount)
        
        # Revive if dead and healed
        if self.state == CharacterState.DEAD and self.health > 0:
            self.can_get_up = True
            self.exit_ragdoll()
    
    def on_collision(self, other_body: PhysicsBody, impact_force: float) -> None:
        """Handle collision with another physics body"""
        self.last_collision_force = impact_force
        
        # Take damage from high-speed collisions
        if impact_force > 500:  # High impact threshold
            damage = (impact_force - 500) * 0.1
            
            # Calculate impact direction
            other_pos = other_body.position
            my_pos = self.physics_body.position
            impact_x = (my_pos[0] - other_pos[0]) * impact_force
            impact_y = (my_pos[1] - other_pos[1]) * impact_force
            
            self.take_damage(damage, (impact_x, impact_y))
            print(f"💥 Character hit with force {impact_force:.1f}, damage: {damage:.1f}")
    
    def enter_vehicle(self, vehicle, seat: str = "driver") -> bool:
        """Enter a vehicle"""
        if self.state == CharacterState.IN_VEHICLE:
            return False
        
        self.current_vehicle = vehicle
        self.vehicle_seat = seat
        self.set_state(CharacterState.ENTERING_VEHICLE)
        
        # Disable character physics body while in vehicle
        if self.physics_body.b2_body:
            self.physics_body.b2_body.active = False
        
        # Animation timer for entering
        self.state_timer = 0.0
        
        print(f"🚗 Character entering vehicle as {seat}")
        return True
    
    def exit_vehicle(self) -> bool:
        """Exit current vehicle"""
        if not self.current_vehicle:
            return False
        
        self.set_state(CharacterState.EXITING_VEHICLE)
        
        # Position character next to vehicle
        exit_offset = 30  # pixels
        exit_x = self.current_vehicle.x + exit_offset
        exit_y = self.current_vehicle.y
        
        self.physics_body.set_position(exit_x / 16.0, exit_y / 16.0)
        if self.physics_body.b2_body:
            self.physics_body.b2_body.active = True
        
        self.current_vehicle = None
        self.vehicle_seat = None
        
        # Animation timer for exiting
        self.state_timer = 0.0
        
        print(f"🚶 Character exited vehicle")
        return True
    
    def teleport(self, x: float, y: float) -> None:
        """Teleport character to position"""
        self.physics_body.set_position(x / 16.0, y / 16.0)
        self.physics_body.set_velocity((0, 0))
        print(f"⚡ Character teleported to ({x:.1f}, {y:.1f})")
    
    def set_position_quiet(self, x: float, y: float) -> None:
        """Set character position silently (for sprite syncing)"""
        self.physics_body.set_position(x / 16.0, y / 16.0)
    
    def get_speed(self) -> float:
        """Get current movement speed in pixels/second"""
        vx, vy = self.velocity
        return math.sqrt(vx*vx + vy*vy)
    
    def is_moving(self) -> bool:
        """Check if character is moving"""
        return self.get_speed() > 10.0
    
    def can_interact(self) -> bool:
        """Check if character can interact with objects"""
        return (not self.is_stunned and 
                self.state not in [CharacterState.RAGDOLL, CharacterState.DEAD,
                                  CharacterState.IN_VEHICLE])
    
    def destroy(self) -> None:
        """Clean up character physics"""
        if self.physics_body:
            self.physics_manager.remove_body(self.physics_body.body_id)
            self.physics_body = None
        print(f"🗑️ Character physics destroyed")