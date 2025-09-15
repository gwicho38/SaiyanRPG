#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Weapon & Combat System with Projectile Physics

import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager, CollisionCategory, PhysicsBodyType


class WeaponType(Enum):
    """Types of weapons"""
    FISTS = "fists"
    KNIFE = "knife"
    PISTOL = "pistol"
    SHOTGUN = "shotgun"
    ASSAULT_RIFLE = "assault_rifle"
    SNIPER_RIFLE = "sniper_rifle"
    GRENADE = "grenade"
    RPG = "rpg"
    FLAMETHROWER = "flamethrower"
    MINIGUN = "minigun"


class ProjectileType(Enum):
    """Types of projectiles"""
    BULLET = "bullet"
    SHELL = "shell"
    GRENADE = "grenade"
    ROCKET = "rocket"
    FLAME = "flame"
    EXPLOSIVE = "explosive"


class DamageType(Enum):
    """Types of damage"""
    PHYSICAL = "physical"
    EXPLOSIVE = "explosive"
    FIRE = "fire"
    ELECTRIC = "electric"
    POISON = "poison"


@dataclass
class WeaponStats:
    """Weapon statistics"""
    damage: float
    range: float
    accuracy: float  # 0.0 to 1.0
    fire_rate: float  # rounds per second
    recoil: float
    spread: float  # degrees
    penetration: float
    ammo_capacity: int
    reload_time: float
    weight: float
    cost: int


@dataclass
class Projectile:
    """Projectile with physics"""
    projectile_id: int
    projectile_type: ProjectileType
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    damage: float
    damage_type: DamageType
    range: float
    penetration: float
    owner_id: int
    physics_body_id: Optional[int]
    creation_time: float
    lifetime: float
    has_exploded: bool = False


@dataclass
class Weapon:
    """Weapon with stats and state"""
    weapon_id: int
    weapon_type: WeaponType
    stats: WeaponStats
    current_ammo: int
    total_ammo: int
    is_reloading: bool
    last_shot_time: float
    recoil_accumulation: float
    heat_level: float  # For overheating weapons
    condition: float  # 0.0 to 1.0 (weapon wear)
    owner_id: int


@dataclass
class HitResult:
    """Result of a projectile hit"""
    hit: bool
    target_id: Optional[int]
    target_type: Optional[str]
    position: Tuple[float, float]
    damage_dealt: float
    penetration: bool
    ricochet: bool
    distance_traveled: float


class ProjectilePhysics:
    """Physics system for projectiles"""
    
    def __init__(self, physics_manager: PhysicsManager):
        self.physics_manager = physics_manager
        self.projectiles: Dict[int, Projectile] = {}
        self.next_projectile_id = 1
        
        print("💥 ProjectilePhysics initialized")
    
    def create_projectile(self, projectile_type: ProjectileType, position: Tuple[float, float],
                         velocity: Tuple[float, float], damage: float, damage_type: DamageType,
                         range: float, penetration: float, owner_id: int) -> int:
        """Create a new projectile"""
        projectile_id = self.next_projectile_id
        self.next_projectile_id += 1
        
        # Create physics body for projectile
        physics_body_id = None
        if projectile_type in [ProjectileType.BULLET, ProjectileType.SHELL]:
            # Small, fast projectiles
            physics_body_id = self.physics_manager.create_body(
                PhysicsBodyType.DYNAMIC,
                position,
                {
                    'type': 'circle',
                    'radius': 0.1,
                    'mass': 0.01,
                    'friction': 0.0,
                    'restitution': 0.0
                },
                CollisionCategory.PROJECTILE,
                user_data={'projectile_id': projectile_id, 'type': 'projectile'}
            )
            
            # Set initial velocity
            self.physics_manager.set_velocity(physics_body_id, velocity)
        
        # Create projectile data
        projectile = Projectile(
            projectile_id=projectile_id,
            projectile_type=projectile_type,
            position=position,
            velocity=velocity,
            damage=damage,
            damage_type=damage_type,
            range=range,
            penetration=penetration,
            owner_id=owner_id,
            physics_body_id=physics_body_id,
            creation_time=time.time(),
            lifetime=range / math.sqrt(velocity[0]**2 + velocity[1]**2) if velocity != (0, 0) else 5.0
        )
        
        self.projectiles[projectile_id] = projectile
        
        print(f"💥 Created {projectile_type.value} projectile {projectile_id}")
        return projectile_id
    
    def update_projectiles(self, dt: float) -> List[HitResult]:
        """Update all projectiles and return hit results"""
        hit_results = []
        current_time = time.time()
        
        for projectile_id, projectile in list(self.projectiles.items()):
            # Check lifetime
            if current_time - projectile.creation_time > projectile.lifetime:
                self._remove_projectile(projectile_id)
                continue
            
            # Update projectile physics
            if projectile.physics_body_id:
                physics_body = self.physics_manager.get_body(projectile.physics_body_id)
                if physics_body:
                    projectile.position = physics_body.position
                    projectile.velocity = physics_body.velocity
                    
                    # Check for hits
                    hit_result = self._check_projectile_hit(projectile)
                    if hit_result.hit:
                        hit_results.append(hit_result)
                        self._handle_projectile_hit(projectile, hit_result)
                        self._remove_projectile(projectile_id)
            else:
                # Simple projectile without physics body
                projectile.position = (
                    projectile.position[0] + projectile.velocity[0] * dt,
                    projectile.position[1] + projectile.velocity[1] * dt
                )
                
                # Check for hits
                hit_result = self._check_projectile_hit(projectile)
                if hit_result.hit:
                    hit_results.append(hit_result)
                    self._handle_projectile_hit(projectile, hit_result)
                    self._remove_projectile(projectile_id)
        
        return hit_results
    
    def _check_projectile_hit(self, projectile: Projectile) -> HitResult:
        """Check if projectile has hit something"""
        # Simple hit detection - in a real implementation, this would be more sophisticated
        # For now, we'll use a basic distance check
        
        # Check against all physics bodies
        for body_id, physics_body in self.physics_manager.bodies.items():
            if body_id == projectile.physics_body_id:
                continue
            
            # Calculate distance
            dx = physics_body.position[0] - projectile.position[0]
            dy = physics_body.position[1] - projectile.position[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            # Check if hit
            if distance < 1.0:  # Within 1 unit
                return HitResult(
                    hit=True,
                    target_id=body_id,
                    target_type=physics_body.user_data.get('type', 'unknown') if physics_body.user_data else 'unknown',
                    position=projectile.position,
                    damage_dealt=projectile.damage,
                    penetration=False,
                    ricochet=False,
                    distance_traveled=0.0
                )
        
        return HitResult(
            hit=False,
            target_id=None,
            target_type=None,
            position=projectile.position,
            damage_dealt=0.0,
            penetration=False,
            ricochet=False,
            distance_traveled=0.0
        )
    
    def _handle_projectile_hit(self, projectile: Projectile, hit_result: HitResult):
        """Handle projectile hit"""
        if projectile.projectile_type == ProjectileType.EXPLOSIVE:
            # Create explosion
            self._create_explosion(hit_result.position, projectile.damage)
        elif projectile.projectile_type == ProjectileType.GRENADE:
            # Create grenade explosion
            self._create_explosion(hit_result.position, projectile.damage * 2.0)
        
        print(f"💥 Projectile {projectile.projectile_id} hit {hit_result.target_type} for {hit_result.damage_dealt} damage")
    
    def _create_explosion(self, position: Tuple[float, float], damage: float):
        """Create explosion effect"""
        # In a real implementation, this would create visual and audio effects
        print(f"💥 Explosion at {position} with {damage} damage")
    
    def _remove_projectile(self, projectile_id: int):
        """Remove projectile from system"""
        if projectile_id in self.projectiles:
            projectile = self.projectiles[projectile_id]
            
            # Remove physics body
            if projectile.physics_body_id:
                self.physics_manager.remove_body(projectile.physics_body_id)
            
            del self.projectiles[projectile_id]
    
    def get_projectile_statistics(self) -> Dict[str, Any]:
        """Get projectile system statistics"""
        type_counts = {}
        for projectile in self.projectiles.values():
            projectile_type = projectile.projectile_type.value
            type_counts[projectile_type] = type_counts.get(projectile_type, 0) + 1
        
        return {
            'total_projectiles': len(self.projectiles),
            'projectile_types': type_counts
        }


class WeaponManager:
    """Weapon management system"""
    
    def __init__(self, projectile_physics: ProjectilePhysics):
        self.projectile_physics = projectile_physics
        self.weapons: Dict[int, Weapon] = {}
        self.weapon_templates: Dict[WeaponType, WeaponStats] = {}
        self.next_weapon_id = 1
        
        # Initialize weapon templates
        self._initialize_weapon_templates()
        
        print("🔫 WeaponManager initialized")
    
    def _initialize_weapon_templates(self):
        """Initialize weapon templates with realistic stats"""
        self.weapon_templates = {
            WeaponType.FISTS: WeaponStats(
                damage=10.0, range=1.0, accuracy=0.8, fire_rate=2.0,
                recoil=0.0, spread=0.0, penetration=0.0, ammo_capacity=0,
                reload_time=0.0, weight=0.0, cost=0
            ),
            WeaponType.KNIFE: WeaponStats(
                damage=25.0, range=1.5, accuracy=0.9, fire_rate=1.5,
                recoil=0.0, spread=0.0, penetration=0.0, ammo_capacity=0,
                reload_time=0.0, weight=0.5, cost=50
            ),
            WeaponType.PISTOL: WeaponStats(
                damage=35.0, range=50.0, accuracy=0.7, fire_rate=3.0,
                recoil=0.3, spread=2.0, penetration=0.2, ammo_capacity=12,
                reload_time=2.0, weight=1.0, cost=200
            ),
            WeaponType.SHOTGUN: WeaponStats(
                damage=80.0, range=20.0, accuracy=0.6, fire_rate=1.0,
                recoil=0.8, spread=8.0, penetration=0.1, ammo_capacity=8,
                reload_time=3.0, weight=3.0, cost=500
            ),
            WeaponType.ASSAULT_RIFLE: WeaponStats(
                damage=45.0, range=100.0, accuracy=0.8, fire_rate=8.0,
                recoil=0.5, spread=1.5, penetration=0.5, ammo_capacity=30,
                reload_time=2.5, weight=4.0, cost=800
            ),
            WeaponType.SNIPER_RIFLE: WeaponStats(
                damage=120.0, range=200.0, accuracy=0.95, fire_rate=0.5,
                recoil=1.0, spread=0.5, penetration=0.8, ammo_capacity=5,
                reload_time=4.0, weight=6.0, cost=1500
            ),
            WeaponType.GRENADE: WeaponStats(
                damage=150.0, range=30.0, accuracy=0.9, fire_rate=0.3,
                recoil=0.0, spread=0.0, penetration=0.0, ammo_capacity=1,
                reload_time=5.0, weight=2.0, cost=300
            ),
            WeaponType.RPG: WeaponStats(
                damage=200.0, range=150.0, accuracy=0.9, fire_rate=0.2,
                recoil=0.0, spread=0.0, penetration=0.0, ammo_capacity=1,
                reload_time=6.0, weight=8.0, cost=2000
            ),
            WeaponType.FLAMETHROWER: WeaponStats(
                damage=20.0, range=15.0, accuracy=0.5, fire_rate=10.0,
                recoil=0.2, spread=15.0, penetration=0.0, ammo_capacity=100,
                reload_time=8.0, weight=10.0, cost=1200
            ),
            WeaponType.MINIGUN: WeaponStats(
                damage=30.0, range=80.0, accuracy=0.6, fire_rate=20.0,
                recoil=0.7, spread=3.0, penetration=0.6, ammo_capacity=200,
                reload_time=10.0, weight=15.0, cost=3000
            )
        }
    
    def create_weapon(self, weapon_type: WeaponType, owner_id: int) -> int:
        """Create a new weapon"""
        weapon_id = self.next_weapon_id
        self.next_weapon_id += 1
        
        stats = self.weapon_templates[weapon_type]
        
        weapon = Weapon(
            weapon_id=weapon_id,
            weapon_type=weapon_type,
            stats=stats,
            current_ammo=stats.ammo_capacity,
            total_ammo=stats.ammo_capacity * 3,  # 3 extra magazines
            is_reloading=False,
            last_shot_time=0.0,
            recoil_accumulation=0.0,
            heat_level=0.0,
            condition=1.0,
            owner_id=owner_id
        )
        
        self.weapons[weapon_id] = weapon
        
        print(f"🔫 Created {weapon_type.value} weapon {weapon_id} for owner {owner_id}")
        return weapon_id
    
    def fire_weapon(self, weapon_id: int, position: Tuple[float, float], 
                   direction: Tuple[float, float], owner_id: int) -> bool:
        """Fire a weapon"""
        if weapon_id not in self.weapons:
            return False
        
        weapon = self.weapons[weapon_id]
        current_time = time.time()
        
        # Check if weapon can fire
        if weapon.is_reloading:
            return False
        
        if weapon.current_ammo <= 0:
            self._start_reload(weapon)
            return False
        
        # Check fire rate
        time_since_last_shot = current_time - weapon.last_shot_time
        if time_since_last_shot < 1.0 / weapon.stats.fire_rate:
            return False
        
        # Check overheating
        if weapon.heat_level > 0.8:
            return False
        
        # Fire weapon
        self._fire_projectile(weapon, position, direction, owner_id)
        
        # Update weapon state
        weapon.current_ammo -= 1
        weapon.last_shot_time = current_time
        weapon.recoil_accumulation += weapon.stats.recoil
        weapon.heat_level += 0.1
        
        # Auto-reload if empty
        if weapon.current_ammo <= 0:
            self._start_reload(weapon)
        
        return True
    
    def _fire_projectile(self, weapon: Weapon, position: Tuple[float, float], 
                        direction: Tuple[float, float], owner_id: int):
        """Fire projectile from weapon"""
        # Calculate projectile properties
        base_speed = 100.0  # Base projectile speed
        
        # Apply accuracy and spread
        spread_angle = random.uniform(-weapon.stats.spread, weapon.stats.spread) * math.pi / 180.0
        accuracy_factor = random.uniform(0.0, weapon.stats.accuracy)
        
        # Calculate final direction
        angle = math.atan2(direction[1], direction[0]) + spread_angle
        final_direction = (
            math.cos(angle) * accuracy_factor,
            math.sin(angle) * accuracy_factor
        )
        
        # Calculate velocity
        velocity = (
            final_direction[0] * base_speed,
            final_direction[1] * base_speed
        )
        
        # Determine projectile type
        if weapon.weapon_type == WeaponType.SHOTGUN:
            projectile_type = ProjectileType.SHELL
        elif weapon.weapon_type in [WeaponType.GRENADE, WeaponType.RPG]:
            projectile_type = ProjectileType.EXPLOSIVE
        elif weapon.weapon_type == WeaponType.FLAMETHROWER:
            projectile_type = ProjectileType.FLAME
        else:
            projectile_type = ProjectileType.BULLET
        
        # Create projectile
        self.projectile_physics.create_projectile(
            projectile_type=projectile_type,
            position=position,
            velocity=velocity,
            damage=weapon.stats.damage,
            damage_type=DamageType.PHYSICAL,
            range=weapon.stats.range,
            penetration=weapon.stats.penetration,
            owner_id=owner_id
        )
    
    def _start_reload(self, weapon: Weapon):
        """Start weapon reload"""
        if weapon.is_reloading or weapon.current_ammo >= weapon.stats.ammo_capacity:
            return
        
        weapon.is_reloading = True
        weapon.reload_start_time = time.time()
        
        print(f"🔫 Weapon {weapon.weapon_id} started reloading")
    
    def update_weapons(self, dt: float):
        """Update all weapons"""
        current_time = time.time()
        
        for weapon in self.weapons.values():
            # Update reload
            if weapon.is_reloading:
                if current_time - weapon.reload_start_time >= weapon.stats.reload_time:
                    # Reload complete
                    ammo_needed = weapon.stats.ammo_capacity - weapon.current_ammo
                    ammo_to_add = min(ammo_needed, weapon.total_ammo)
                    
                    weapon.current_ammo += ammo_to_add
                    weapon.total_ammo -= ammo_to_add
                    weapon.is_reloading = False
                    
                    print(f"🔫 Weapon {weapon.weapon_id} reloaded")
            
            # Cool down weapon
            weapon.heat_level = max(0.0, weapon.heat_level - dt * 0.2)
            
            # Reduce recoil
            weapon.recoil_accumulation = max(0.0, weapon.recoil_accumulation - dt * 2.0)
    
    def get_weapon_statistics(self) -> Dict[str, Any]:
        """Get weapon system statistics"""
        type_counts = {}
        for weapon in self.weapons.values():
            weapon_type = weapon.weapon_type.value
            type_counts[weapon_type] = type_counts.get(weapon_type, 0) + 1
        
        return {
            'total_weapons': len(self.weapons),
            'weapon_types': type_counts
        }


class CombatSystem:
    """Comprehensive combat system"""
    
    def __init__(self, physics_manager: PhysicsManager):
        self.physics_manager = physics_manager
        self.projectile_physics = ProjectilePhysics(physics_manager)
        self.weapon_manager = WeaponManager(self.projectile_physics)
        
        # Combat statistics
        self.total_shots_fired = 0
        self.total_hits = 0
        self.total_damage_dealt = 0.0
        self.total_kills = 0
        
        print("⚔️ CombatSystem initialized")
    
    def update(self, dt: float) -> List[HitResult]:
        """Update combat system"""
        # Update weapons
        self.weapon_manager.update_weapons(dt)
        
        # Update projectiles and get hits
        hit_results = self.projectile_physics.update_projectiles(dt)
        
        # Process hits
        for hit_result in hit_results:
            self._process_hit(hit_result)
        
        return hit_results
    
    def _process_hit(self, hit_result: HitResult):
        """Process a hit result"""
        self.total_hits += 1
        self.total_damage_dealt += hit_result.damage_dealt
        
        print(f"⚔️ Hit: {hit_result.damage_dealt} damage to {hit_result.target_type}")
    
    def fire_weapon(self, weapon_id: int, position: Tuple[float, float], 
                   direction: Tuple[float, float], owner_id: int) -> bool:
        """Fire a weapon"""
        success = self.weapon_manager.fire_weapon(weapon_id, position, direction, owner_id)
        if success:
            self.total_shots_fired += 1
        return success
    
    def create_weapon(self, weapon_type: WeaponType, owner_id: int) -> int:
        """Create a weapon"""
        return self.weapon_manager.create_weapon(weapon_type, owner_id)
    
    def get_combat_statistics(self) -> Dict[str, Any]:
        """Get combat statistics"""
        accuracy = (self.total_hits / self.total_shots_fired * 100) if self.total_shots_fired > 0 else 0.0
        
        return {
            'total_shots_fired': self.total_shots_fired,
            'total_hits': self.total_hits,
            'total_damage_dealt': self.total_damage_dealt,
            'total_kills': self.total_kills,
            'accuracy': accuracy,
            'weapons': self.weapon_manager.get_weapon_statistics(),
            'projectiles': self.projectile_physics.get_projectile_statistics()
        }


# Test the weapon and combat system
if __name__ == "__main__":
    print("🧪 Testing Weapon & Combat System...")
    
    # Create dependencies
    from saiyanquest.physics_manager import PhysicsManager
    
    physics_manager = PhysicsManager(gravity=(0, 0))
    combat_system = CombatSystem(physics_manager)
    
    # Create some weapons
    pistol_id = combat_system.create_weapon(WeaponType.PISTOL, 1)
    rifle_id = combat_system.create_weapon(WeaponType.ASSAULT_RIFLE, 1)
    shotgun_id = combat_system.create_weapon(WeaponType.SHOTGUN, 1)
    
    # Test firing
    print("Testing weapon firing...")
    for frame in range(60):  # 1 second at 60 FPS
        dt = 1.0 / 60.0
        
        # Fire weapons occasionally
        if frame % 20 == 0:  # Every 1/3 second
            combat_system.fire_weapon(pistol_id, (100, 100), (1, 0), 1)
        if frame % 15 == 0:  # Every 1/4 second
            combat_system.fire_weapon(rifle_id, (200, 200), (0, 1), 1)
        if frame % 60 == 0:  # Every second
            combat_system.fire_weapon(shotgun_id, (300, 300), (-1, 0), 1)
        
        # Update combat system
        hit_results = combat_system.update(dt)
        
        # Update physics
        physics_manager.update(dt)
        
        if frame % 30 == 0:  # Print every 0.5 seconds
            stats = combat_system.get_combat_statistics()
            print(f"  Frame {frame}: Shots = {stats['total_shots_fired']}, "
                  f"Hits = {stats['total_hits']}, "
                  f"Damage = {stats['total_damage_dealt']:.1f}")
    
    print("✅ Weapon & Combat System test completed")