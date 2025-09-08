#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Weapon and Combat System for SaiyanQuest

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class WeaponCategory(Enum):
    MELEE = "melee"
    PISTOL = "pistol" 
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    SMG = "smg"
    SNIPER = "sniper"
    HEAVY = "heavy"
    EXPLOSIVE = "explosive"
    THROWN = "thrown"

class WeaponType(Enum):
    # Melee
    FIST = "fist"
    KNIFE = "knife"
    BAT = "baseball_bat"
    KATANA = "katana"
    CHAINSAW = "chainsaw"
    
    # Pistols
    PISTOL = "pistol"
    DESERT_EAGLE = "desert_eagle"
    
    # SMGs
    UZI = "uzi"
    TEC9 = "tec9"
    MP5 = "mp5"
    
    # Rifles
    AK47 = "ak47"
    M16 = "m16"
    
    # Shotguns
    SHOTGUN = "shotgun"
    SAWED_OFF = "sawed_off_shotgun"
    COMBAT_SHOTGUN = "combat_shotgun"
    
    # Sniper
    SNIPER_RIFLE = "sniper_rifle"
    
    # Heavy Weapons
    MINIGUN = "minigun"
    FLAME_THROWER = "flame_thrower"
    ROCKET_LAUNCHER = "rocket_launcher"
    
    # Explosives
    GRENADE = "grenade"
    MOLOTOV = "molotov_cocktail"
    C4 = "c4"

@dataclass
class WeaponStats:
    damage: float
    fire_rate: float  # Shots per second
    accuracy: float   # 0.0 to 1.0
    range: float      # Maximum effective range
    ammo_capacity: int
    reload_time: float
    spread: float     # Bullet spread in degrees
    recoil: float     # 0.0 to 1.0
    weight: float
    
    @classmethod
    def get_stats(cls, weapon_type: WeaponType) -> 'WeaponStats':
        """Get weapon stats for a given weapon type"""
        stats_map = {
            # Melee
            WeaponType.FIST: cls(10, 2.0, 1.0, 2, 0, 0, 0, 0, 0),
            WeaponType.KNIFE: cls(30, 1.5, 1.0, 3, 0, 0, 0, 0, 0.5),
            WeaponType.BAT: cls(25, 1.0, 1.0, 4, 0, 0, 0, 0, 2.0),
            WeaponType.KATANA: cls(40, 2.0, 1.0, 4, 0, 0, 0, 0, 1.5),
            WeaponType.CHAINSAW: cls(50, 8.0, 1.0, 3, 100, 0, 0, 0, 8.0),
            
            # Pistols
            WeaponType.PISTOL: cls(25, 3.0, 0.8, 50, 15, 2.0, 5, 0.2, 1.2),
            WeaponType.DESERT_EAGLE: cls(45, 1.5, 0.7, 60, 7, 2.5, 8, 0.6, 2.0),
            
            # SMGs
            WeaponType.UZI: cls(20, 12.0, 0.6, 40, 32, 2.5, 10, 0.3, 3.5),
            WeaponType.TEC9: cls(18, 15.0, 0.5, 35, 50, 3.0, 12, 0.4, 3.0),
            WeaponType.MP5: cls(22, 10.0, 0.7, 45, 30, 2.8, 8, 0.2, 4.0),
            
            # Rifles
            WeaponType.AK47: cls(35, 8.0, 0.7, 80, 30, 3.5, 6, 0.4, 4.8),
            WeaponType.M16: cls(32, 10.0, 0.8, 85, 30, 3.0, 4, 0.3, 4.5),
            
            # Shotguns
            WeaponType.SHOTGUN: cls(80, 1.0, 0.6, 25, 8, 4.0, 25, 0.8, 4.0),
            WeaponType.SAWED_OFF: cls(90, 1.5, 0.4, 15, 2, 2.0, 35, 1.0, 2.5),
            WeaponType.COMBAT_SHOTGUN: cls(75, 2.0, 0.7, 30, 10, 3.5, 20, 0.6, 4.5),
            
            # Sniper
            WeaponType.SNIPER_RIFLE: cls(100, 0.3, 0.95, 200, 5, 4.0, 1, 0.1, 6.0),
            
            # Heavy Weapons
            WeaponType.MINIGUN: cls(30, 20.0, 0.6, 100, 1000, 8.0, 15, 0.8, 50.0),
            WeaponType.FLAME_THROWER: cls(50, 10.0, 0.9, 20, 100, 5.0, 30, 0.2, 25.0),
            WeaponType.ROCKET_LAUNCHER: cls(200, 0.5, 1.0, 150, 1, 6.0, 0, 1.0, 15.0),
            
            # Thrown/Explosives
            WeaponType.GRENADE: cls(150, 1.0, 0.8, 30, 1, 0, 0, 0, 0.5),
            WeaponType.MOLOTOV: cls(100, 1.0, 0.7, 25, 1, 0, 0, 0, 0.3),
            WeaponType.C4: cls(300, 0.1, 1.0, 5, 1, 0, 0, 0, 1.0),
        }
        return stats_map.get(weapon_type, cls(10, 2.0, 1.0, 2, 0, 0, 0, 0, 0))
    
class Weapon:
    def __init__(self, weapon_type: WeaponType):
        self.weapon_type = weapon_type
        self.category = self._get_category()
        self.stats = WeaponStats.get_stats(weapon_type)
        
        # Ammo system
        self.current_ammo = self.stats.ammo_capacity
        self.reserve_ammo = 0
        self.is_reloading = False
        self.reload_timer = 0.0
        
        # Firing state
        self.last_fire_time = 0.0
        self.can_fire = True
        self.is_automatic = self._is_automatic()
        
        # Weapon state
        self.durability = 100.0  # 0 to 100
        self.modifications = []
        self.silencer = False
        self.laser_sight = False
        
    def _get_category(self) -> WeaponCategory:
        """Get weapon category based on type"""
        category_map = {
            WeaponType.FIST: WeaponCategory.MELEE,
            WeaponType.KNIFE: WeaponCategory.MELEE,
            WeaponType.BAT: WeaponCategory.MELEE,
            WeaponType.KATANA: WeaponCategory.MELEE,
            WeaponType.CHAINSAW: WeaponCategory.MELEE,
            
            WeaponType.PISTOL: WeaponCategory.PISTOL,
            WeaponType.DESERT_EAGLE: WeaponCategory.PISTOL,
            
            WeaponType.UZI: WeaponCategory.SMG,
            WeaponType.TEC9: WeaponCategory.SMG,
            WeaponType.MP5: WeaponCategory.SMG,
            
            WeaponType.AK47: WeaponCategory.RIFLE,
            WeaponType.M16: WeaponCategory.RIFLE,
            
            WeaponType.SHOTGUN: WeaponCategory.SHOTGUN,
            WeaponType.SAWED_OFF: WeaponCategory.SHOTGUN,
            WeaponType.COMBAT_SHOTGUN: WeaponCategory.SHOTGUN,
            
            WeaponType.SNIPER_RIFLE: WeaponCategory.SNIPER,
            
            WeaponType.MINIGUN: WeaponCategory.HEAVY,
            WeaponType.FLAME_THROWER: WeaponCategory.HEAVY,
            WeaponType.ROCKET_LAUNCHER: WeaponCategory.HEAVY,
            
            WeaponType.GRENADE: WeaponCategory.THROWN,
            WeaponType.MOLOTOV: WeaponCategory.THROWN,
            WeaponType.C4: WeaponCategory.EXPLOSIVE,
        }
        return category_map.get(self.weapon_type, WeaponCategory.MELEE)
    
    
    def _is_automatic(self) -> bool:
        """Check if weapon is automatic"""
        automatic_weapons = {
            WeaponType.UZI, WeaponType.TEC9, WeaponType.MP5,
            WeaponType.AK47, WeaponType.M16, WeaponType.MINIGUN,
            WeaponType.FLAME_THROWER, WeaponType.CHAINSAW
        }
        return self.weapon_type in automatic_weapons
    
    def can_fire_now(self, current_time: float) -> bool:
        """Check if weapon can fire now"""
        if self.is_reloading or not self.can_fire:
            return False
            
        if self.category == WeaponCategory.MELEE:
            return True
            
        if self.current_ammo <= 0:
            return False
            
        time_since_last_shot = current_time - self.last_fire_time
        return time_since_last_shot >= (1.0 / self.stats.fire_rate)
    
    def fire(self, current_time: float) -> bool:
        """Attempt to fire the weapon"""
        if not self.can_fire_now(current_time):
            return False
            
        if self.category != WeaponCategory.MELEE and self.current_ammo > 0:
            self.current_ammo -= 1
            
        self.last_fire_time = current_time
        self.durability = max(0, self.durability - 0.1)
        
        return True
    
    def reload(self) -> bool:
        """Start reloading the weapon"""
        if (self.is_reloading or 
            self.current_ammo >= self.stats.ammo_capacity or 
            self.reserve_ammo <= 0 or
            self.category == WeaponCategory.MELEE):
            return False
            
        self.is_reloading = True
        self.reload_timer = self.stats.reload_time
        return True
    
    def update(self, dt: float) -> None:
        """Update weapon state"""
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self._complete_reload()
    
    def _complete_reload(self) -> None:
        """Complete the reload process"""
        ammo_needed = self.stats.ammo_capacity - self.current_ammo
        ammo_to_reload = min(ammo_needed, self.reserve_ammo)
        
        self.current_ammo += ammo_to_reload
        self.reserve_ammo -= ammo_to_reload
        self.is_reloading = False
        self.reload_timer = 0
    
    def add_ammo(self, amount: int) -> None:
        """Add ammo to reserve"""
        self.reserve_ammo += amount
    
    def get_damage_at_range(self, distance: float) -> float:
        """Get damage accounting for range falloff"""
        if distance <= self.stats.range * 0.3:
            return self.stats.damage
        elif distance <= self.stats.range:
            # Linear falloff
            falloff_factor = 1.0 - ((distance - self.stats.range * 0.3) / (self.stats.range * 0.7))
            return self.stats.damage * max(0.2, falloff_factor)
        else:
            return self.stats.damage * 0.2  # Minimum damage at long range

class Projectile:
    def __init__(self, x: float, y: float, angle: float, weapon: Weapon, target_x: float = 0, target_y: float = 0):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.weapon = weapon
        
        # Calculate velocity based on weapon and spread
        spread_angle = random.uniform(-weapon.stats.spread/2, weapon.stats.spread/2)
        self.angle += spread_angle
        
        # Projectile speed (pixels per second)
        if weapon.category == WeaponCategory.THROWN:
            self.speed = 300
        elif weapon.weapon_type == WeaponType.ROCKET_LAUNCHER:
            self.speed = 400
        else:
            self.speed = 800
            
        self.velocity_x = math.cos(math.radians(self.angle)) * self.speed
        self.velocity_y = math.sin(math.radians(self.angle)) * self.speed
        
        # Projectile properties
        self.damage = weapon.stats.damage
        self.penetration = 1 if weapon.category in [WeaponCategory.RIFLE, WeaponCategory.SNIPER] else 0
        self.explosive = weapon.weapon_type in [WeaponType.ROCKET_LAUNCHER, WeaponType.GRENADE]
        self.explosive_radius = 100 if self.explosive else 0
        
        # State
        self.active = True
        self.distance_traveled = 0
        self.max_range = weapon.stats.range * 10  # Convert to pixels
        
        # Special effects
        self.is_flame = weapon.weapon_type == WeaponType.FLAME_THROWER
        self.lifetime = 2.0 if self.is_flame else 5.0
        
    def update(self, dt: float) -> None:
        """Update projectile movement"""
        if not self.active:
            return
            
        # Move projectile
        old_x, old_y = self.x, self.y
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update distance traveled
        self.distance_traveled += math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        
        # Check if projectile should be destroyed
        self.lifetime -= dt
        if (self.lifetime <= 0 or 
            self.distance_traveled > self.max_range):
            self.active = False
            
        # Apply gravity to thrown weapons
        if self.weapon.category == WeaponCategory.THROWN:
            self.velocity_y += 500 * dt  # Gravity
    
    def get_damage(self) -> float:
        """Get damage accounting for distance falloff"""
        return self.weapon.get_damage_at_range(self.distance_traveled)
    
    def explode(self) -> Dict:
        """Handle explosion (for explosive projectiles)"""
        if not self.explosive:
            return {}
            
        return {
            'position': (self.x, self.y),
            'radius': self.explosive_radius,
            'damage': self.damage * 2,  # Explosive damage bonus
            'type': 'explosion'
        }

class WeaponInventory:
    def __init__(self):
        self.weapons: Dict[WeaponCategory, List[Weapon]] = {
            category: [] for category in WeaponCategory
        }
        self.current_weapon: Optional[Weapon] = None
        self.current_category = WeaponCategory.MELEE
        self.category_index = 0
        self.weapon_index_in_category = 0
        
        # Start with fists
        fists = Weapon(WeaponType.FIST)
        self.add_weapon(fists)
        self.equip_weapon(fists)
        
    def add_weapon(self, weapon: Weapon) -> bool:
        """Add a weapon to inventory"""
        category_weapons = self.weapons[weapon.category]
        
        # Check if we already have this weapon type
        for existing_weapon in category_weapons:
            if existing_weapon.weapon_type == weapon.weapon_type:
                # Just add ammo if it's the same weapon
                existing_weapon.add_ammo(weapon.reserve_ammo)
                return False
                
        category_weapons.append(weapon)
        return True
    
    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a specific weapon"""
        if weapon in self.weapons[weapon.category]:
            self.current_weapon = weapon
            self.current_category = weapon.category
            self._update_indices()
    
    def next_weapon_in_category(self) -> None:
        """Switch to next weapon in current category"""
        if not self.weapons[self.current_category]:
            return
            
        self.weapon_index_in_category = (self.weapon_index_in_category + 1) % len(self.weapons[self.current_category])
        self.current_weapon = self.weapons[self.current_category][self.weapon_index_in_category]
    
    def previous_weapon_in_category(self) -> None:
        """Switch to previous weapon in current category"""
        if not self.weapons[self.current_category]:
            return
            
        self.weapon_index_in_category = (self.weapon_index_in_category - 1) % len(self.weapons[self.current_category])
        self.current_weapon = self.weapons[self.current_category][self.weapon_index_in_category]
    
    def next_category(self) -> None:
        """Switch to next weapon category"""
        categories = list(WeaponCategory)
        current_index = categories.index(self.current_category)
        
        # Find next category that has weapons
        for i in range(1, len(categories)):
            next_index = (current_index + i) % len(categories)
            next_category = categories[next_index]
            
            if self.weapons[next_category]:
                self.current_category = next_category
                self.weapon_index_in_category = 0
                self.current_weapon = self.weapons[next_category][0]
                break
    
    def previous_category(self) -> None:
        """Switch to previous weapon category"""
        categories = list(WeaponCategory)
        current_index = categories.index(self.current_category)
        
        # Find previous category that has weapons
        for i in range(1, len(categories)):
            prev_index = (current_index - i) % len(categories)
            prev_category = categories[prev_index]
            
            if self.weapons[prev_category]:
                self.current_category = prev_category
                self.weapon_index_in_category = 0
                self.current_weapon = self.weapons[prev_category][0]
                break
    
    def _update_indices(self) -> None:
        """Update weapon indices after equipping a weapon"""
        if self.current_weapon:
            category_weapons = self.weapons[self.current_category]
            self.weapon_index_in_category = category_weapons.index(self.current_weapon)
    
    def get_all_weapons(self) -> List[Weapon]:
        """Get all weapons in inventory"""
        all_weapons = []
        for category_weapons in self.weapons.values():
            all_weapons.extend(category_weapons)
        return all_weapons
    
    def has_weapon_type(self, weapon_type: WeaponType) -> bool:
        """Check if inventory has a specific weapon type"""
        for weapon in self.get_all_weapons():
            if weapon.weapon_type == weapon_type:
                return True
        return False

class CombatSystem:
    """Main combat system managing weapons and projectiles"""
    
    def __init__(self):
        self.projectiles: List[Projectile] = []
        self.explosions: List[Dict] = []  # Active explosions
        self.muzzle_flashes: List[Dict] = []  # Muzzle flash effects
        
        # Aiming
        self.auto_aim = True
        self.aim_assistance_radius = 100
        
    def fire_weapon(self, weapon: Weapon, start_x: float, start_y: float, 
                   target_x: float, target_y: float, current_time: float) -> bool:
        """Fire a weapon"""
        if not weapon.fire(current_time):
            return False
        
        # Calculate firing angle
        angle = math.degrees(math.atan2(target_y - start_y, target_x - start_x))
        
        # Create muzzle flash
        if weapon.category != WeaponCategory.MELEE:
            self.muzzle_flashes.append({
                'x': start_x,
                'y': start_y,
                'angle': angle,
                'lifetime': 0.1,
                'weapon_type': weapon.weapon_type
            })
        
        # Handle different weapon types
        if weapon.category == WeaponCategory.MELEE:
            return self._handle_melee_attack(weapon, start_x, start_y, angle)
        elif weapon.weapon_type == WeaponType.SHOTGUN:
            return self._handle_shotgun_blast(weapon, start_x, start_y, angle, current_time)
        elif weapon.weapon_type == WeaponType.FLAME_THROWER:
            return self._handle_flame_thrower(weapon, start_x, start_y, angle, current_time)
        else:
            # Standard projectile
            projectile = Projectile(start_x, start_y, angle, weapon, target_x, target_y)
            self.projectiles.append(projectile)
            return True
    
    def _handle_melee_attack(self, weapon: Weapon, x: float, y: float, angle: float) -> bool:
        """Handle melee weapon attacks"""
        # Create a short-range "projectile" for melee
        melee_projectile = Projectile(x, y, angle, weapon)
        melee_projectile.speed = 0  # Instant hit
        melee_projectile.max_range = weapon.stats.range
        melee_projectile.lifetime = 0.1
        self.projectiles.append(melee_projectile)
        return True
    
    def _handle_shotgun_blast(self, weapon: Weapon, x: float, y: float, angle: float, current_time: float) -> bool:
        """Handle shotgun multiple pellets"""
        pellet_count = 8
        for i in range(pellet_count):
            pellet_angle = angle + random.uniform(-weapon.stats.spread, weapon.stats.spread)
            projectile = Projectile(x, y, pellet_angle, weapon)
            projectile.damage = weapon.stats.damage / pellet_count  # Distribute damage
            self.projectiles.append(projectile)
        return True
    
    def _handle_flame_thrower(self, weapon: Weapon, x: float, y: float, angle: float, current_time: float) -> bool:
        """Handle flame thrower continuous fire"""
        # Create multiple flame projectiles for area effect
        for i in range(3):
            flame_angle = angle + random.uniform(-10, 10)
            projectile = Projectile(x, y, flame_angle, weapon)
            projectile.is_flame = True
            projectile.speed = 200  # Slower than bullets
            self.projectiles.append(projectile)
        return True
    
    def update(self, dt: float) -> None:
        """Update combat system"""
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if not projectile.active:
                # Handle explosion if needed
                if projectile.explosive:
                    explosion = projectile.explode()
                    if explosion:
                        self.explosions.append(explosion)
                        explosion['lifetime'] = 2.0
                
                self.projectiles.remove(projectile)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion['lifetime'] -= dt
            if explosion['lifetime'] <= 0:
                self.explosions.remove(explosion)
        
        # Update muzzle flashes
        for flash in self.muzzle_flashes[:]:
            flash['lifetime'] -= dt
            if flash['lifetime'] <= 0:
                self.muzzle_flashes.remove(flash)
    
    def check_projectile_collisions(self, targets: List[Dict]) -> List[Dict]:
        """Check projectile collisions with targets"""
        hits = []
        
        for projectile in self.projectiles[:]:
            if not projectile.active:
                continue
                
            for target in targets:
                target_x = target.get('x', 0)
                target_y = target.get('y', 0)
                target_radius = target.get('radius', 20)
                
                distance = math.sqrt((projectile.x - target_x)**2 + (projectile.y - target_y)**2)
                
                if distance <= target_radius:
                    hit_info = {
                        'target': target,
                        'projectile': projectile,
                        'damage': projectile.get_damage(),
                        'position': (projectile.x, projectile.y),
                        'weapon_type': projectile.weapon.weapon_type
                    }
                    hits.append(hit_info)
                    
                    # Remove projectile unless it penetrates
                    if projectile.penetration <= 0:
                        projectile.active = False
                    else:
                        projectile.penetration -= 1
                        
        return hits
    
    def get_auto_aim_target(self, start_x: float, start_y: float, targets: List[Dict]) -> Optional[Tuple[float, float]]:
        """Get auto-aim target position"""
        if not self.auto_aim or not targets:
            return None
        
        closest_target = None
        closest_distance = self.aim_assistance_radius
        
        for target in targets:
            target_x = target.get('x', 0)
            target_y = target.get('y', 0)
            
            distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_target = target
        
        if closest_target:
            return (closest_target['x'], closest_target['y'])
        
        return None