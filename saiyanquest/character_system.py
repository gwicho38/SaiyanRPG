#!/usr/bin/env python3
"""
Comprehensive Character/Pedestrian System
Integrates physics, AI, animations, and visual effects for realistic characters.
Based on Carnage3D character mechanics.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .character_physics import CharacterPhysics, CharacterState, CharacterType, CharacterStats
from .character_ai import CharacterAI, CharacterController, CharacterAIManager, CharacterState, FearLevel
from .gta_asset_loader import get_asset_loader


class AnimationState(Enum):
    """Character animation states"""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    RAGDOLL = "ragdoll"
    GETTING_UP = "getting_up"
    TALKING = "talking"
    ENTERING_VEHICLE = "entering_vehicle"
    EXITING_VEHICLE = "exiting_vehicle"
    ATTACKING = "attacking"
    DYING = "dying"
    DEAD = "dead"


@dataclass
class CharacterAppearance:
    """Character visual appearance"""
    skin_color: Tuple[int, int, int] = (200, 180, 160)
    hair_color: Tuple[int, int, int] = (100, 70, 50)
    clothing_color: Tuple[int, int, int] = (50, 50, 150)
    height_scale: float = 1.0
    width_scale: float = 1.0


class Character:
    """Complete character system combining physics, AI, and visuals"""
    
    def __init__(self, character_type: CharacterType, x: float, y: float, 
                 is_player_controlled: bool = False):
        self.character_type = character_type
        self.is_player_controlled = is_player_controlled
        
        # Initialize core systems
        self.physics = CharacterPhysics(character_type, x, y)
        
        # Character identity
        self.name = self._generate_name(character_type)
        self.unique_id = random.randint(1000, 9999)
        
        # Initialize AI after unique_id is set
        self.ai = None if is_player_controlled else CharacterController(self.unique_id, self.physics.physics_body)
        
        # Visual properties
        self.appearance = self._generate_appearance(character_type)
        self.animation_state = AnimationState.IDLE
        self.animation_timer = 0.0
        self.animation_frame = 0
        
        # Player progression (for GTA compatibility)
        self.level = 1
        self.experience = 0
        self.money = 1000 if is_player_controlled else 0
        self.respect = 0
        self.current_gang = "NEUTRAL"  # Will be replaced with enum if needed
        self.missions_completed = 0
        self.territory_controlled = []
        
        # Weapon inventory system
        self.weapon_inventory = []
        self.current_weapon = None
        self.ammo = {}
        
        # Armor system
        self.armor = 0.0  # 0.0 to 1.0
        self.max_armor = 100.0
        
        # Game state
        self.spawn_time = time.time()
        self.last_update_time = 0.0
        
        # Interaction state
        self.interaction_cooldown = 0.0
        self.current_interaction = None
        
        # Effects and particles
        self.speech_bubble = None
        self.speech_timer = 0.0
        self.status_effects = []
        
        print(f"👤 Character created: {self.name} ({character_type.value}) at ({x:.1f}, {y:.1f})")
    
    def _generate_appearance(self, character_type: CharacterType) -> CharacterAppearance:
        """Generate random appearance based on character type"""
        appearance = CharacterAppearance()
        
        # Randomize skin color
        skin_tones = [
            (255, 220, 177),  # Light
            (241, 194, 125),  # Medium-light
            (224, 172, 105),  # Medium
            (198, 134, 66),   # Medium-dark
            (141, 85, 36),    # Dark
        ]
        appearance.skin_color = random.choice(skin_tones)
        
        # Hair color
        hair_colors = [
            (0, 0, 0),        # Black
            (101, 67, 33),    # Brown
            (255, 255, 0),    # Blonde
            (165, 42, 42),    # Red
            (128, 128, 128),  # Gray
        ]
        appearance.hair_color = random.choice(hair_colors)
        
        # Clothing based on character type
        type_clothing = {
            CharacterType.POLICE: (0, 0, 139),      # Dark blue
            CharacterType.GANG_MEMBER: (139, 0, 0), # Dark red
            CharacterType.BUSINESSMAN: (64, 64, 64), # Gray suit
            CharacterType.PARAMEDIC: (255, 255, 255), # White
            CharacterType.FIREFIGHTER: (255, 165, 0), # Orange
            CharacterType.ATHLETE: (0, 128, 0),      # Green
        }
        
        appearance.clothing_color = type_clothing.get(
            character_type, 
            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        )
        
        # Size variation
        appearance.height_scale = random.uniform(0.9, 1.1)
        appearance.width_scale = random.uniform(0.95, 1.05)
        
        return appearance
    
    def _generate_name(self, character_type: CharacterType) -> str:
        """Generate a random name"""
        first_names = [
            "Alex", "Blake", "Casey", "Drew", "Emery", "Finley", "Gray", "Hayden",
            "Indigo", "Jude", "Kit", "Lane", "Max", "Nova", "Orion", "Parker",
            "Quinn", "River", "Sage", "Taylor", "Unique", "Vale", "West", "Zara"
        ]
        
        last_names = [
            "Adams", "Baker", "Clark", "Davis", "Evans", "Fisher", "Garcia", "Harris",
            "Irving", "Jones", "Kelly", "Lopez", "Miller", "Nelson", "O'Brien", "Parker",
            "Quinn", "Roberts", "Smith", "Taylor", "Underwood", "Valdez", "Williams", "Young"
        ]
        
        # Add prefixes/suffixes based on type
        prefix = ""
        if character_type == CharacterType.POLICE:
            prefix = "Officer "
        elif character_type == CharacterType.PARAMEDIC:
            prefix = "Medic "
        elif character_type == CharacterType.FIREFIGHTER:
            prefix = "Fire "
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        return f"{prefix}{first_name} {last_name}"
    
    @property
    def x(self) -> float:
        """Get character X position"""
        return self.physics.x
    
    @property
    def y(self) -> float:
        """Get character Y position"""
        return self.physics.y
    
    @property
    def state(self) -> CharacterState:
        """Get character state"""
        return self.physics.state
    
    @property
    def health(self) -> float:
        """Get character health"""
        return self.physics.health
    
    @property
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.physics.state != CharacterState.DEAD
    
    def update(self, dt: float, world_context: Dict = None) -> None:
        """Update all character systems"""
        self.last_update_time = time.time()
        
        # Update core physics
        self.physics.update(dt)
        
        # Update AI if not player controlled
        if self.ai and not self.is_player_controlled:
            nearby_chars = world_context.get('nearby_characters', []) if world_context else []
            nearby_vehicles = world_context.get('nearby_vehicles', []) if world_context else []
            events = world_context.get('events', []) if world_context else []
            
            self.ai.update(dt, nearby_chars, nearby_vehicles, events)
        
        # Update animations
        self._update_animation(dt)
        
        # Update effects
        self._update_effects(dt)
        
        # Update interaction cooldown
        self.interaction_cooldown = max(0, self.interaction_cooldown - dt)
    
    def _update_animation(self, dt: float) -> None:
        """Update character animations"""
        self.animation_timer += dt
        
        # Map physics states to animation states
        state_mapping = {
            CharacterState.IDLE: AnimationState.IDLE,
            CharacterState.WALKING: AnimationState.WALKING,
            CharacterState.RUNNING: AnimationState.RUNNING,
            CharacterState.JUMPING: AnimationState.JUMPING,
            CharacterState.FALLING: AnimationState.FALLING,
            CharacterState.RAGDOLL: AnimationState.RAGDOLL,
            CharacterState.GETTING_UP: AnimationState.GETTING_UP,
            CharacterState.DEAD: AnimationState.DEAD,
            CharacterState.ENTERING_VEHICLE: AnimationState.ENTERING_VEHICLE,
            CharacterState.EXITING_VEHICLE: AnimationState.EXITING_VEHICLE,
        }
        
        # Override with AI behavior animations
        if self.ai:
            if self.ai.ai.current_state == CharacterState.TALKING:
                self.animation_state = AnimationState.TALKING
            elif self.ai.ai.current_state == CharacterState.SHOOTING:
                self.animation_state = AnimationState.ATTACKING
        
        # Default animation state mapping
        if self.animation_state not in [AnimationState.TALKING, AnimationState.ATTACKING]:
            self.animation_state = state_mapping.get(self.physics.state, AnimationState.IDLE)
        
        # Update animation frame (simplified frame counter)
        animation_speeds = {
            AnimationState.IDLE: 0.5,
            AnimationState.WALKING: 0.2,
            AnimationState.RUNNING: 0.1,
            AnimationState.TALKING: 0.3,
        }
        
        speed = animation_speeds.get(self.animation_state, 0.5)
        if self.animation_timer >= speed:
            self.animation_frame = (self.animation_frame + 1) % 4  # 4-frame animations
            self.animation_timer = 0.0
    
    def _update_effects(self, dt: float) -> None:
        """Update visual effects and status indicators"""
        # Update speech bubble
        if self.speech_timer > 0:
            self.speech_timer -= dt
            if self.speech_timer <= 0:
                self.speech_bubble = None
        
        # Update status effects
        for effect in self.status_effects[:]:  # Copy list to allow removal
            effect['duration'] -= dt
            if effect['duration'] <= 0:
                self.status_effects.remove(effect)
    
    # Player control methods
    def move(self, direction_x: float, direction_y: float) -> None:
        """Move character (player control)"""
        if self.is_player_controlled:
            self.physics.move(direction_x, direction_y)
    
    def run(self, is_running: bool) -> None:
        """Toggle running (player control)"""
        if self.is_player_controlled:
            self.physics.run(is_running)
    
    def jump(self) -> bool:
        """Make character jump (player control)"""
        if self.is_player_controlled:
            return self.physics.jump()
        return False
    
    # Interaction methods
    def interact_with(self, target: Any) -> bool:
        """Interact with another object"""
        if self.interaction_cooldown > 0:
            return False
        
        # Vehicle interaction
        if hasattr(target, 'vehicle_type'):  # It's a vehicle
            return self.enter_vehicle(target)
        
        # Character interaction
        elif hasattr(target, 'character_type'):  # It's another character
            return self.talk_to(target)
        
        return False
    
    def enter_vehicle(self, vehicle, seat: str = "passenger") -> bool:
        """Enter a vehicle"""
        if self.physics.state == CharacterState.IN_VEHICLE:
            return False
        
        # Check distance to vehicle
        distance = math.sqrt((vehicle.x - self.x)**2 + (vehicle.y - self.y)**2)
        if distance > 50:  # Too far
            return False
        
        if self.physics.enter_vehicle(vehicle, seat):
            self.interaction_cooldown = 2.0
            return True
        return False
    
    def exit_vehicle(self) -> bool:
        """Exit current vehicle"""
        if self.physics.exit_vehicle():
            self.interaction_cooldown = 2.0
            return True
        return False
    
    def talk_to(self, other_character) -> bool:
        """Start conversation with another character"""
        if not other_character.is_alive or not self.can_interact():
            return False
        
        # Check distance
        distance = math.sqrt((other_character.x - self.x)**2 + (other_character.y - self.y)**2)
        if distance > 60:  # Too far for conversation
            return False
        
        # Start conversation
        self.say(f"Hello, {other_character.name}!")
        other_character.say(f"Hi there, {self.name}!")
        
        # Set AI behaviors if not player controlled
        if self.ai:
            self.ai.current_state = CharacterState.TALKING
        if other_character.ai:
            other_character.ai.current_state = CharacterState.TALKING
        
        self.interaction_cooldown = 30.0  # Don't talk again soon
        other_character.interaction_cooldown = 30.0
        
        return True
    
    def say(self, message: str, duration: float = 3.0) -> None:
        """Display speech bubble"""
        self.speech_bubble = message
        self.speech_timer = duration
    
    def take_damage(self, damage: float, impact_force: Tuple[float, float] = (0, 0), 
                   damage_type: str = "physical") -> None:
        """Take damage"""
        # Apply armor protection
        armor_reduction = self.armor * 0.5  # Armor reduces damage by 50% of armor value
        actual_damage = max(0, damage - armor_reduction)
        
        self.physics.take_damage(actual_damage, impact_force)
        
        # Reduce armor when taking damage
        if self.armor > 0:
            armor_damage = min(self.armor, damage * 0.3)  # Armor takes 30% of damage
            self.armor -= armor_damage
        
        # Add visual effect
        self.add_status_effect("damaged", 2.0, (255, 0, 0))
        
        # AI reaction
        if self.ai and damage > 10:
            if damage > 50:
                self.ai.ai.fear_level = FearLevel.PANIC
                self.ai.ai.current_state = CharacterState.FLEEING
            else:
                self.ai.ai.current_state = CharacterState.FLEEING
    
    def heal(self, amount: float) -> None:
        """Heal character"""
        self.physics.heal(amount)
        self.add_status_effect("healed", 3.0, (0, 255, 0))
    
    def stun(self, duration: float) -> None:
        """Stun character"""
        self.physics.is_stunned = True
        self.physics.stun_timer = duration
        self.physics.set_state(CharacterState.STUNNED)
        self.add_status_effect("stunned", duration, (255, 255, 0))
    
    def add_status_effect(self, effect_type: str, duration: float, color: Tuple[int, int, int]) -> None:
        """Add visual status effect"""
        self.status_effects.append({
            'type': effect_type,
            'duration': duration,
            'color': color,
            'start_time': time.time()
        })
    
    def teleport(self, x: float, y: float) -> None:
        """Teleport character to position"""
        self.physics.teleport(x, y)
    
    def can_interact(self) -> bool:
        """Check if character can interact"""
        return (self.physics.can_interact() and 
                self.interaction_cooldown <= 0 and
                self.is_alive)
    
    def get_ai_status(self) -> Optional[Dict]:
        """Get AI status information"""
        if self.ai:
            return self.ai.get_status_info()
        return None
    
    def force_ai_behavior(self, behavior: CharacterState) -> None:
        """Force AI to specific behavior"""
        if self.ai:
            self.ai.current_state = behavior
    
    def set_ai_destination(self, x: float, y: float) -> None:
        """Set AI movement destination"""
        if self.ai:
            self.ai.set_destination(x, y)
    
    # Weapon inventory methods
    def add_weapon(self, weapon_name: str, ammo_count: int = 0) -> bool:
        """Add weapon to inventory"""
        if weapon_name not in self.weapon_inventory:
            self.weapon_inventory.append(weapon_name)
            self.ammo[weapon_name] = ammo_count
            if not self.current_weapon:
                self.current_weapon = weapon_name
            print(f"🔫 {self.name} picked up {weapon_name}")
            return True
        return False
    
    def remove_weapon(self, weapon_name: str) -> bool:
        """Remove weapon from inventory"""
        if weapon_name in self.weapon_inventory:
            self.weapon_inventory.remove(weapon_name)
            if weapon_name in self.ammo:
                del self.ammo[weapon_name]
            if self.current_weapon == weapon_name:
                self.current_weapon = self.weapon_inventory[0] if self.weapon_inventory else None
            print(f"🔫 {self.name} dropped {weapon_name}")
            return True
        return False
    
    def switch_weapon(self, weapon_name: str) -> bool:
        """Switch to different weapon"""
        if weapon_name in self.weapon_inventory:
            self.current_weapon = weapon_name
            print(f"🔫 {self.name} switched to {weapon_name}")
            return True
        return False
    
    def get_ammo(self, weapon_name: str) -> int:
        """Get ammo count for weapon"""
        return self.ammo.get(weapon_name, 0)
    
    def add_ammo(self, weapon_name: str, amount: int) -> None:
        """Add ammo for weapon"""
        if weapon_name in self.ammo:
            self.ammo[weapon_name] += amount
        else:
            self.ammo[weapon_name] = amount
    
    # Armor methods
    def add_armor(self, amount: float) -> None:
        """Add armor"""
        self.armor = min(self.max_armor, self.armor + amount)
        print(f"🛡️ {self.name} gained {amount} armor (total: {self.armor})")
    
    def remove_armor(self, amount: float) -> None:
        """Remove armor"""
        self.armor = max(0.0, self.armor - amount)
        print(f"🛡️ {self.name} lost {amount} armor (remaining: {self.armor})")
    
    def get_armor_percentage(self) -> float:
        """Get armor as percentage"""
        return (self.armor / self.max_armor) * 100.0
    
    def _get_sprite_name(self) -> str:
        """Get sprite name based on character type"""
        sprite_map = {
            CharacterType.PLAYER: "player",
            CharacterType.CIVILIAN: "civilian_1",
            CharacterType.POLICE: "police", 
            CharacterType.GANG_MEMBER: "gangster",
            CharacterType.PARAMEDIC: "medic",
            CharacterType.BUSINESSMAN: "businessman",
            CharacterType.TOURIST: "civilian_2",
            CharacterType.ATHLETE: "civilian_1",
            CharacterType.ELDERLY: "civilian_2",
            CharacterType.CHILD: "civilian_1",
            CharacterType.FIREFIGHTER: "civilian_1"
        }
        return sprite_map.get(self.character_type, "civilian_1")
    
    def _get_sprite_direction(self) -> str:
        """Convert facing angle to sprite direction"""
        # Normalize angle to 0-360
        angle = self.physics.facing_angle % 360
        
        # Map angle ranges to sprite directions
        if 315 <= angle or angle < 45:
            return "east"   # Right
        elif 45 <= angle < 135:
            return "south"  # Down  
        elif 135 <= angle < 225:
            return "west"   # Left
        else:
            return "north"  # Up
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render character using GTA sprite assets"""
        # Calculate screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Don't render if off-screen
        if (screen_x < -50 or screen_x > screen.get_width() + 50 or
            screen_y < -50 or screen_y > screen.get_height() + 50):
            return
        
        # Get asset loader
        asset_loader = get_asset_loader()
        
        # Handle special states with fallback rendering
        if self.physics.state == CharacterState.RAGDOLL:
            # Draw as lying down (simple fallback for now)
            width = int(20 * self.appearance.height_scale)  # Rotated
            height = int(12 * self.appearance.width_scale)
            body_rect = pygame.Rect(screen_x - width//2, screen_y - height//2, width, height)
            pygame.draw.ellipse(screen, self.appearance.clothing_color, body_rect)
        elif self.physics.state == CharacterState.DEAD:
            # Draw as cross/X
            pygame.draw.line(screen, (150, 0, 0), 
                           (screen_x - 8, screen_y - 8), (screen_x + 8, screen_y + 8), 2)
            pygame.draw.line(screen, (150, 0, 0),
                           (screen_x + 8, screen_y - 8), (screen_x - 8, screen_y + 8), 2)
        else:
            # Normal character - use sprite
            sprite_name = self._get_sprite_name()
            sprite_direction = self._get_sprite_direction()
            
            # Get sprite from asset loader
            sprite = asset_loader.get_character_sprite(sprite_name, sprite_direction)
            
            if sprite:
                # Scale sprite based on appearance
                original_size = sprite.get_size()
                scaled_width = int(original_size[0] * self.appearance.width_scale * 2)  # 2x for visibility
                scaled_height = int(original_size[1] * self.appearance.height_scale * 2)
                
                if scaled_width != original_size[0] or scaled_height != original_size[1]:
                    sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                
                # Center sprite on character position
                sprite_rect = sprite.get_rect()
                sprite_rect.center = (screen_x, screen_y)
                screen.blit(sprite, sprite_rect)
            else:
                # Fallback to circle if sprite not found
                pygame.draw.circle(screen, self.appearance.clothing_color, (screen_x, screen_y), 8)
                pygame.draw.circle(screen, self.appearance.skin_color, (screen_x, screen_y - 3), 4)
        
        # Character dimensions for UI elements (standard size)
        char_height = 24  # Approximate character height
        char_width = 24   # Approximate character width
        
        # Status effects
        for i, effect in enumerate(self.status_effects):
            effect_y = screen_y - char_height//2 - 10 - (i * 5)
            pygame.draw.circle(screen, effect['color'], (screen_x + char_width//2, effect_y), 3)
        
        # Speech bubble
        if self.speech_bubble:
            self._render_speech_bubble(screen, screen_x, screen_y - char_height//2 - 20)
        
        # Health bar if damaged
        if self.physics.health < self.physics.stats.max_health:
            self._render_health_bar(screen, screen_x, screen_y + char_height//2 + 5)
        
        # AI behavior indicator (debug)
        if self.ai and hasattr(self, 'show_debug') and self.show_debug:
            behavior_text = self.ai.behavior.value[:4].upper()
            font = pygame.font.Font(None, 16)
            text_surface = font.render(behavior_text, True, (255, 255, 255))
            screen.blit(text_surface, (screen_x - 15, screen_y + char_height//2 + 15))
    
    def _render_speech_bubble(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Render speech bubble"""
        if not self.speech_bubble:
            return
        
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.speech_bubble[:20], True, (0, 0, 0))  # Limit text length
        
        # Bubble background
        bubble_rect = text_surface.get_rect()
        bubble_rect.center = (x, y - 10)
        bubble_rect.inflate_ip(10, 6)
        
        pygame.draw.ellipse(screen, (255, 255, 255), bubble_rect)
        pygame.draw.ellipse(screen, (0, 0, 0), bubble_rect, 2)
        
        # Bubble pointer
        pygame.draw.polygon(screen, (255, 255, 255), [
            (x - 5, y + 5), (x + 5, y + 5), (x, y + 15)
        ])
        
        screen.blit(text_surface, bubble_rect)
    
    def _render_health_bar(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Render health bar"""
        bar_width = 20
        bar_height = 4
        
        # Background
        bg_rect = pygame.Rect(x - bar_width//2, y, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 0, 0), bg_rect)
        
        # Health fill
        health_ratio = self.physics.health / self.physics.stats.max_health
        fill_width = int(bar_width * health_ratio)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(x - bar_width//2, y, fill_width, bar_height)
            color = (0, 255, 0) if health_ratio > 0.6 else (255, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
            pygame.draw.rect(screen, color, fill_rect)
    
    def get_info(self) -> Dict:
        """Get comprehensive character information"""
        return {
            'name': self.name,
            'id': self.unique_id,
            'type': self.character_type.value,
            'position': (self.x, self.y),
            'state': self.physics.state.value,
            'health': self.physics.health,
            'max_health': self.physics.stats.max_health,
            'stamina': self.physics.stamina,
            'is_player_controlled': self.is_player_controlled,
            'alive': self.is_alive,
            'can_interact': self.can_interact(),
            'in_vehicle': self.physics.current_vehicle is not None,
            'ai_behavior': self.ai.behavior.value if self.ai else None,
            'speech': self.speech_bubble if self.speech_timer > 0 else None,
            'spawn_time': self.spawn_time,
            'age': time.time() - self.spawn_time
        }
    
    def add_money(self, amount: int) -> None:
        """Add money to character"""
        self.money += amount
        
    def spend_money(self, amount: int) -> bool:
        """Spend money if character has enough"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
        
    def gain_experience(self, amount: int) -> bool:
        """Gain experience and level up if needed"""
        self.experience += amount
        level_up = False
        
        # Simple leveling: 1000 XP per level
        while self.experience >= self.level * 1000:
            self.experience -= self.level * 1000
            self.level += 1
            level_up = True
            
        return level_up
    
    def destroy(self) -> None:
        """Clean up character"""
        self.physics.destroy()
        print(f"🗑️ Character destroyed: {self.name}")


class CharacterManager:
    """Manages all characters in the game world"""
    
    def __init__(self):
        self.characters: List[Character] = []
        self.player_character: Optional[Character] = None
        self.spawn_locations = []
        self.max_characters = 50
        self.spawn_timer = 0.0
        self.spawn_interval = 10.0  # Spawn new character every 10 seconds
        
        print("👥 Character manager initialized")
    
    def create_character(self, character_type: CharacterType, x: float, y: float,
                        is_player: bool = False) -> Character:
        """Create a new character"""
        character = Character(character_type, x, y, is_player)
        
        if is_player:
            self.player_character = character
        
        self.characters.append(character)
        return character
    
    def update_all_characters(self, dt: float, world_events: List[Dict] = None) -> None:
        """Update all characters"""
        self.spawn_timer += dt
        
        # Auto-spawn characters if below max
        if (len(self.characters) < self.max_characters and 
            self.spawn_timer >= self.spawn_interval):
            self._spawn_random_character()
            self.spawn_timer = 0.0
        
        # Update all characters
        for character in self.characters[:]:  # Copy list to allow removal
            if not character.is_alive and time.time() - character.last_update_time > 30.0:
                # Remove dead characters after 30 seconds
                character.destroy()
                self.characters.remove(character)
                continue
            
            # Prepare world context
            world_context = {
                'nearby_characters': self._get_nearby_characters(character, 200.0),
                'nearby_vehicles': [],  # Would be provided by vehicle manager
                'events': world_events or []
            }
            
            character.update(dt, world_context)
    
    def _spawn_random_character(self) -> None:
        """Spawn a random civilian character"""
        if self.spawn_locations:
            spawn_point = random.choice(self.spawn_locations)
        else:
            # Default spawn area
            spawn_point = (
                random.uniform(100, 700),
                random.uniform(100, 500)
            )
        
        # Random civilian types
        civilian_types = [
            CharacterType.CIVILIAN,
            CharacterType.BUSINESSMAN,
            CharacterType.TOURIST,
            CharacterType.ELDERLY,
            CharacterType.ATHLETE
        ]
        
        char_type = random.choice(civilian_types)
        self.create_character(char_type, spawn_point[0], spawn_point[1])
    
    def _get_nearby_characters(self, center_character: Character, radius: float) -> List[Character]:
        """Get characters within radius of center character"""
        nearby = []
        center_pos = (center_character.x, center_character.y)
        
        for character in self.characters:
            if character == center_character:
                continue
            
            distance = math.sqrt(
                (character.x - center_pos[0])**2 + 
                (character.y - center_pos[1])**2
            )
            
            if distance <= radius:
                nearby.append(character)
        
        return nearby
    
    def add_spawn_location(self, x: float, y: float) -> None:
        """Add a spawn location for new characters"""
        self.spawn_locations.append((x, y))
    
    def get_characters_in_area(self, center: Tuple[float, float], radius: float) -> List[Character]:
        """Get all characters in a specific area"""
        characters_in_area = []
        
        for character in self.characters:
            distance = math.sqrt(
                (character.x - center[0])**2 + 
                (character.y - center[1])**2
            )
            
            if distance <= radius:
                characters_in_area.append(character)
        
        return characters_in_area
    
    def render_all_characters(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render all visible characters"""
        for character in self.characters:
            character.render(screen, camera_offset)
    
    def get_character_count(self) -> int:
        """Get total character count"""
        return len(self.characters)
    
    def get_living_character_count(self) -> int:
        """Get living character count"""
        return sum(1 for char in self.characters if char.is_alive)
    
    def clear_all_characters(self) -> None:
        """Remove all characters"""
        for character in self.characters:
            character.destroy()
        self.characters.clear()
        self.player_character = None
        print("🧹 All characters cleared")