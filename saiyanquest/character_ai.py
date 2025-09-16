#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Character AI System with Fear Responses and Behaviors

import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager, PhysicsBody, CollisionCategory, PhysicsBodyType


class CharacterState(Enum):
    """Character states"""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    SHOOTING = "shooting"
    STUNNED = "stunned"
    DEAD = "dead"
    BURNING = "burning"
    IN_VEHICLE = "in_vehicle"
    ENTERING_VEHICLE = "entering_vehicle"
    EXITING_VEHICLE = "exiting_vehicle"
    FLEEING = "fleeing"
    HIDING = "hiding"
    INVESTIGATING = "investigating"
    TALKING = "talking"
    JUMPING = "jumping"
    FALLING = "falling"
    GETTING_UP = "getting_up"
    RAGDOLL = "ragdoll"
    DYING = "dying"


class FearLevel(Enum):
    """Fear levels"""
    CALM = 0
    ALERT = 1
    SCARED = 2
    TERRIFIED = 3
    PANIC = 4


class StimulusType(Enum):
    """Types of stimuli that characters can react to"""
    GUNSHOT = "gunshot"
    EXPLOSION = "explosion"
    POLICE_SIREN = "police_siren"
    VEHICLE_CRASH = "vehicle_crash"
    PLAYER_NEARBY = "player_nearby"
    VIOLENCE = "violence"
    FIRE = "fire"
    LOUD_NOISE = "loud_noise"


@dataclass
class Stimulus:
    """A stimulus that affects character behavior"""
    stimulus_type: StimulusType
    position: Tuple[float, float]
    intensity: float  # 0.0 to 1.0
    radius: float
    timestamp: float
    source: Optional[Any] = None


@dataclass
class CharacterAI:
    """AI controller for a character"""
    character_id: int
    current_state: CharacterState
    fear_level: FearLevel
    target_position: Optional[Tuple[float, float]]
    current_target: Optional[Any]
    
    # Behavior parameters
    aggression: float  # 0.0 to 1.0
    intelligence: float  # 0.0 to 1.0
    courage: float  # 0.0 to 1.0
    curiosity: float  # 0.0 to 1.0
    
    # Movement
    movement_speed: float
    run_speed: float
    current_direction: Tuple[float, float]
    
    # Memory
    known_stimuli: List[Stimulus]
    memory_duration: float
    last_update_time: float
    
    # Vehicle interaction
    target_vehicle: Optional[int]
    vehicle_interaction_timer: float
    
    # Combat
    weapon_skill: float
    accuracy: float
    reaction_time: float
    
    # Social
    group_id: Optional[int]
    social_radius: float


class CharacterController:
    """Controller for character actions and behaviors"""
    
    def __init__(self, character_id: int, physics_body: PhysicsBody):
        self.character_id = character_id
        self.physics_body = physics_body
        
        # Initialize AI
        self.ai = CharacterAI(
            character_id=character_id,
            current_state=CharacterState.IDLE,
            fear_level=FearLevel.CALM,
            target_position=None,
            current_target=None,
            aggression=random.uniform(0.2, 0.8),
            intelligence=random.uniform(0.3, 0.9),
            courage=random.uniform(0.1, 0.7),
            curiosity=random.uniform(0.4, 0.8),
            movement_speed=1.5,  # m/s
            run_speed=3.0,  # m/s
            current_direction=(0, 0),
            known_stimuli=[],
            memory_duration=30.0,  # seconds
            last_update_time=time.time(),
            target_vehicle=None,
            vehicle_interaction_timer=0.0,
            weapon_skill=random.uniform(0.1, 0.6),
            accuracy=random.uniform(0.3, 0.8),
            reaction_time=random.uniform(0.5, 2.0),
            group_id=None,
            social_radius=50.0
        )
        
        # Behavior state
        self.state_timer = 0.0
        self.idle_timer = 0.0
        self.flee_timer = 0.0
        
        # Pathfinding
        self.path: List[Tuple[float, float]] = []
        self.path_index = 0
        self.path_update_timer = 0.0
        
        print(f"🤖 CharacterController created for character {character_id}")
    
    def update(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update character AI"""
        current_time = time.time()
        self.ai.last_update_time = current_time
        
        # Update timers
        self.state_timer += dt
        self.idle_timer += dt
        self.flee_timer += dt
        self.path_update_timer += dt
        
        # Clean old stimuli from memory
        self._clean_stimuli_memory(current_time)
        
        # Update fear level based on stimuli
        self._update_fear_level(game_state)
        
        # Update behavior based on current state
        self._update_behavior(dt, game_state)
        
        # Update movement
        self._move_towards_target(self.ai.movement_speed if self.ai.current_state.value in ['walking', 'investigating'] else self.ai.run_speed if self.ai.current_state.value == 'running' else 0.0)
        
        # Update vehicle interaction
        self._update_vehicle_interaction(dt, game_state)
    
    def _clean_stimuli_memory(self, current_time: float) -> None:
        """Remove old stimuli from memory"""
        self.ai.known_stimuli = [
            stimulus for stimulus in self.ai.known_stimuli
            if current_time - stimulus.timestamp < self.ai.memory_duration
        ]
    
    def _update_fear_level(self, game_state: Dict[str, Any]) -> None:
        """Update character fear level based on nearby stimuli"""
        character_pos = self.physics_body.position
        fear_score = 0.0
        
        # Check for nearby stimuli
        for stimulus in self.ai.known_stimuli:
            distance = math.sqrt(
                (stimulus.position[0] - character_pos[0])**2 +
                (stimulus.position[1] - character_pos[1])**2
            )
            
            if distance < stimulus.radius:
                # Calculate fear contribution
                distance_factor = 1.0 - (distance / stimulus.radius)
                fear_contribution = stimulus.intensity * distance_factor
                
                # Different stimuli have different fear weights
                fear_weights = {
                    StimulusType.GUNSHOT: 0.8,
                    StimulusType.EXPLOSION: 1.0,
                    StimulusType.POLICE_SIREN: 0.6,
                    StimulusType.VEHICLE_CRASH: 0.4,
                    StimulusType.PLAYER_NEARBY: 0.3,
                    StimulusType.VIOLENCE: 0.9,
                    StimulusType.FIRE: 0.7,
                    StimulusType.LOUD_NOISE: 0.2
                }
                
                fear_score += fear_contribution * fear_weights.get(stimulus.stimulus_type, 0.5)
        
        # Apply courage modifier
        fear_score *= (1.0 - self.ai.courage)
        
        # Update fear level
        if fear_score > 0.8:
            self.ai.fear_level = FearLevel.PANIC
        elif fear_score > 0.6:
            self.ai.fear_level = FearLevel.TERRIFIED
        elif fear_score > 0.4:
            self.ai.fear_level = FearLevel.SCARED
        elif fear_score > 0.2:
            self.ai.fear_level = FearLevel.ALERT
        else:
            self.ai.fear_level = FearLevel.CALM
    
    def _update_behavior(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update character behavior based on current state and fear level"""
        if self.ai.current_state == CharacterState.DEAD:
            return
        
        # State transitions based on fear level
        if self.ai.fear_level in [FearLevel.PANIC, FearLevel.TERRIFIED]:
            if self.ai.current_state != CharacterState.FLEEING:
                self._change_state(CharacterState.FLEEING)
                self.flee_timer = 0.0
        elif self.ai.fear_level == FearLevel.SCARED:
            if self.ai.current_state not in [CharacterState.FLEEING, CharacterState.HIDING]:
                if random.random() < 0.7:  # 70% chance to flee
                    self._change_state(CharacterState.FLEEING)
                else:
                    self._change_state(CharacterState.HIDING)
        elif self.ai.fear_level == FearLevel.ALERT:
            if self.ai.current_state == CharacterState.IDLE:
                self._change_state(CharacterState.INVESTIGATING)
        elif self.ai.fear_level == FearLevel.CALM:
            if self.ai.current_state in [CharacterState.FLEEING, CharacterState.HIDING]:
                if self.flee_timer > 5.0:  # Stop fleeing after 5 seconds
                    self._change_state(CharacterState.IDLE)
        
        # Behavior-specific updates
        if self.ai.current_state == CharacterState.IDLE:
            self._update_idle_behavior(dt)
        elif self.ai.current_state == CharacterState.WALKING:
            self._update_walking_behavior(dt)
        elif self.ai.current_state == CharacterState.RUNNING:
            self._update_running_behavior(dt)
        elif self.ai.current_state == CharacterState.FLEEING:
            self._update_fleeing_behavior(dt, game_state)
        elif self.ai.current_state == CharacterState.HIDING:
            self._update_hiding_behavior(dt)
        elif self.ai.current_state == CharacterState.INVESTIGATING:
            self._update_investigating_behavior(dt, game_state)
        elif self.ai.current_state == CharacterState.SHOOTING:
            self._update_shooting_behavior(dt, game_state)
    
    def _change_state(self, new_state: CharacterState) -> None:
        """Change character state"""
        old_state = self.ai.current_state
        self.ai.current_state = new_state
        self.state_timer = 0.0
        
        print(f"🤖 Character {self.character_id}: {old_state.value} -> {new_state.value}")
    
    def _update_idle_behavior(self, dt: float) -> None:
        """Update idle behavior"""
        # Random chance to start walking
        if self.idle_timer > 2.0 and random.random() < 0.1:
            self._change_state(CharacterState.WALKING)
            self._generate_random_target()
    
    def _update_walking_behavior(self, dt: float) -> None:
        """Update walking behavior"""
        if self.ai.target_position:
            self._move_towards_target(self.ai.movement_speed)
        else:
            # Random chance to stop walking
            if random.random() < 0.05:
                self._change_state(CharacterState.IDLE)
    
    def _update_running_behavior(self, dt: float) -> None:
        """Update running behavior"""
        if self.ai.target_position:
            self._move_towards_target(self.ai.run_speed)
        else:
            self._change_state(CharacterState.IDLE)
    
    def _update_fleeing_behavior(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update fleeing behavior"""
        # Find the safest direction (away from threats)
        character_pos = self.physics_body.position
        flee_direction = self._calculate_flee_direction(character_pos)
        
        if flee_direction:
            # Move in flee direction
            target_x = character_pos[0] + flee_direction[0] * 100
            target_y = character_pos[1] + flee_direction[1] * 100
            self.ai.target_position = (target_x, target_y)
            
            self._move_towards_target(self.ai.run_speed)
        else:
            # No clear flee direction, just run randomly
            if random.random() < 0.3:
                self._generate_random_target()
                self._move_towards_target(self.ai.run_speed)
    
    def _update_hiding_behavior(self, dt: float) -> None:
        """Update hiding behavior"""
        # Look for nearby hiding spots (simplified)
        # In a real implementation, this would check for buildings, alleys, etc.
        if random.random() < 0.1:
            self._change_state(CharacterState.IDLE)
    
    def _update_investigating_behavior(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update investigating behavior"""
        # Move towards the most recent stimulus
        if self.ai.known_stimuli:
            latest_stimulus = max(self.ai.known_stimuli, key=lambda s: s.timestamp)
            self.ai.target_position = latest_stimulus.position
            self._move_towards_target(self.ai.movement_speed)
        else:
            self._change_state(CharacterState.IDLE)
    
    def _update_shooting_behavior(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update shooting behavior"""
        # This would integrate with the weapon system
        # For now, just transition back to other states
        if self.state_timer > 2.0:
            if self.ai.fear_level == FearLevel.CALM:
                self._change_state(CharacterState.IDLE)
            else:
                self._change_state(CharacterState.FLEEING)
    
    def _calculate_flee_direction(self, character_pos: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """Calculate the best direction to flee"""
        if not self.ai.known_stimuli:
            return None
        
        # Calculate weighted average of threat directions
        threat_x = 0.0
        threat_y = 0.0
        total_weight = 0.0
        
        for stimulus in self.ai.known_stimuli:
            distance = math.sqrt(
                (stimulus.position[0] - character_pos[0])**2 +
                (stimulus.position[1] - character_pos[1])**2
            )
            
            if distance > 0:
                # Weight by intensity and inverse distance
                weight = stimulus.intensity / distance
                
                # Direction from stimulus to character (away from threat)
                direction_x = (character_pos[0] - stimulus.position[0]) / distance
                direction_y = (character_pos[1] - stimulus.position[1]) / distance
                
                threat_x += direction_x * weight
                threat_y += direction_y * weight
                total_weight += weight
        
        if total_weight > 0:
            # Normalize
            threat_x /= total_weight
            threat_y /= total_weight
            
            # Normalize to unit vector
            length = math.sqrt(threat_x**2 + threat_y**2)
            if length > 0:
                return (threat_x / length, threat_y / length)
        
        return None
    
    def _generate_random_target(self) -> None:
        """Generate a random target position"""
        character_pos = self.physics_body.position
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(20, 100)
        
        target_x = character_pos[0] + math.cos(angle) * distance
        target_y = character_pos[1] + math.sin(angle) * distance
        
        self.ai.target_position = (target_x, target_y)
    
    def _move_towards_target(self, speed: float) -> None:
        """Move towards the target position"""
        if not self.ai.target_position:
            return
        
        character_pos = self.physics_body.position
        target_pos = self.ai.target_position
        
        # Calculate direction
        dx = target_pos[0] - character_pos[0]
        dy = target_pos[1] - character_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5.0:  # 5 meter threshold
            # Normalize direction
            direction_x = dx / distance
            direction_y = dy / distance
            
            # Set velocity
            velocity_x = direction_x * speed
            velocity_y = direction_y * speed
            
            self.physics_body.velocity = (velocity_x, velocity_y)
            self.ai.current_direction = (direction_x, direction_y)
        else:
            # Reached target
            self.physics_body.velocity = (0, 0)
            self.ai.target_position = None
    
    def _update_vehicle_interaction(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update vehicle interaction behavior"""
        if self.ai.current_state == CharacterState.IN_VEHICLE:
            return
        
        # Look for nearby vehicles
        character_pos = self.physics_body.position
        nearby_vehicles = self._find_nearby_vehicles(character_pos, 30.0, game_state)
        
        if nearby_vehicles and self.ai.fear_level in [FearLevel.PANIC, FearLevel.TERRIFIED]:
            # Try to enter a vehicle to escape
            vehicle_id = nearby_vehicles[0]  # Take the first one
            self.ai.target_vehicle = vehicle_id
            self._change_state(CharacterState.ENTERING_VEHICLE)
    
    def _find_nearby_vehicles(self, position: Tuple[float, float], radius: float, 
                             game_state: Dict[str, Any]) -> List[int]:
        """Find nearby vehicles"""
        # This would integrate with the vehicle system
        # For now, return empty list
        return []
    
    def add_stimulus(self, stimulus: Stimulus) -> None:
        """Add a stimulus to the character's memory"""
        self.ai.known_stimuli.append(stimulus)
        print(f"🤖 Character {self.character_id} received stimulus: {stimulus.stimulus_type.value}")
    
    def get_character_info(self) -> Dict[str, Any]:
        """Get character information"""
        return {
            'character_id': self.character_id,
            'state': self.ai.current_state.value,
            'fear_level': self.ai.fear_level.value,
            'position': self.physics_body.position,
            'velocity': self.physics_body.velocity,
            'aggression': self.ai.aggression,
            'intelligence': self.ai.intelligence,
            'courage': self.ai.courage,
            'curiosity': self.ai.curiosity,
            'known_stimuli_count': len(self.ai.known_stimuli)
        }


class CharacterAIManager:
    """Manager for all character AI systems"""
    
    def __init__(self, physics_manager: PhysicsManager):
        self.physics_manager = physics_manager
        self.character_controllers: Dict[int, CharacterController] = {}
        self.stimuli_queue: List[Stimulus] = []
        
        print("🤖 CharacterAIManager initialized")
    
    def create_character(self, character_id: int, position: Tuple[float, float]) -> CharacterController:
        """Create a new character with AI"""
        # Create physics body
        physics_body = self.physics_manager.create_body(
            PhysicsBodyType.DYNAMIC,
            position,
            {
                'type': 'circle',
                'radius': 0.5,
                'mass': 70.0,  # Average human mass
                'friction': 0.7,
                'restitution': 0.1
            },
            CollisionCategory.PEDESTRIAN,
            user_data={'character_id': character_id, 'type': 'character'}
        )
        
        # Create AI controller
        controller = CharacterController(character_id, physics_body)
        self.character_controllers[character_id] = controller
        
        print(f"🤖 Created character {character_id} with AI at {position}")
        return controller
    
    def update_all_characters(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update all character AI systems"""
        # Process stimuli queue
        self._process_stimuli_queue()
        
        # Update all character controllers
        for controller in self.character_controllers.values():
            controller.update(dt, game_state)
    
    def _process_stimuli_queue(self) -> None:
        """Process queued stimuli"""
        for stimulus in self.stimuli_queue:
            # Find characters within stimulus radius
            for controller in self.character_controllers.values():
                character_pos = controller.physics_body.position
                distance = math.sqrt(
                    (stimulus.position[0] - character_pos[0])**2 +
                    (stimulus.position[1] - character_pos[1])**2
                )
                
                if distance <= stimulus.radius:
                    controller.add_stimulus(stimulus)
        
        # Clear processed stimuli
        self.stimuli_queue.clear()
    
    def add_stimulus(self, stimulus: Stimulus) -> None:
        """Add a stimulus to be processed"""
        self.stimuli_queue.append(stimulus)
    
    def remove_character(self, character_id: int) -> None:
        """Remove a character"""
        if character_id in self.character_controllers:
            controller = self.character_controllers[character_id]
            self.physics_manager.remove_body(controller.physics_body.body_id)
            del self.character_controllers[character_id]
            print(f"🤖 Removed character {character_id}")
    
    def get_character_statistics(self) -> Dict[str, Any]:
        """Get character AI statistics"""
        states = {}
        fear_levels = {}
        
        for controller in self.character_controllers.values():
            state = controller.ai.current_state.value
            fear_level = controller.ai.fear_level.value
            
            states[state] = states.get(state, 0) + 1
            fear_levels[fear_level] = fear_levels.get(fear_level, 0) + 1
        
        return {
            'total_characters': len(self.character_controllers),
            'states': states,
            'fear_levels': fear_levels,
            'pending_stimuli': len(self.stimuli_queue)
        }


# Test the character AI system
if __name__ == "__main__":
    print("🧪 Testing CharacterAI system...")
    
    # Create physics manager
    physics_manager = PhysicsManager(gravity=(0, 0))
    
    # Create character AI manager
    ai_manager = CharacterAIManager(physics_manager)
    
    # Create some test characters
    character1 = ai_manager.create_character(1, (100, 100))
    character2 = ai_manager.create_character(2, (200, 200))
    
    # Create a stimulus (gunshot)
    gunshot = Stimulus(
        stimulus_type=StimulusType.GUNSHOT,
        position=(150, 150),
        intensity=0.8,
        radius=100.0,
        timestamp=time.time()
    )
    
    ai_manager.add_stimulus(gunshot)
    
    # Test update loop
    start_time = time.time()
    
    while time.time() - start_time < 10.0:  # Run for 10 seconds
        dt = 1.0 / 60.0  # 60 FPS
        
        # Update AI
        ai_manager.update_all_characters(dt, {})
        
        # Update physics
        physics_manager.update(dt)
        
        # Print character info
        for controller in ai_manager.character_controllers.values():
            info = controller.get_character_info()
            print(f"Character {info['character_id']}: {info['state']}, Fear: {info['fear_level']}")
        
        time.sleep(dt)
    
    print("✅ CharacterAI system test completed")