#!/usr/bin/env python3
"""
Advanced Character AI System
Implements intelligent pedestrian behavior, pathfinding, and decision making.
Based on Carnage3D AI mechanics.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .character_physics import CharacterPhysics, CharacterState, CharacterType


class AIBehavior(Enum):
    """AI behavior types"""
    IDLE = "idle"
    WANDERING = "wandering"
    WALKING_TO_DESTINATION = "walking_to_destination"
    FOLLOWING_PATH = "following_path"
    FLEEING = "fleeing"
    SEEKING_SHELTER = "seeking_shelter"
    INVESTIGATING = "investigating"
    ATTACKING = "attacking"
    CALLING_POLICE = "calling_police"
    DRIVING = "driving"
    ENTERING_VEHICLE = "entering_vehicle"
    EXITING_VEHICLE = "exiting_vehicle"
    TALKING = "talking"
    SHOPPING = "shopping"
    WORKING = "working"
    PANICKING = "panicking"


class ThreatLevel(Enum):
    """Threat assessment levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


@dataclass
class AIMemory:
    """AI memory system for tracking events and locations"""
    last_threat_position: Optional[Tuple[float, float]] = None
    last_threat_time: float = 0.0
    known_safe_locations: List[Tuple[float, float]] = None
    known_dangerous_locations: List[Tuple[float, float]] = None
    witnessed_crimes: List[Dict] = None
    conversation_partners: List[Any] = None
    
    def __post_init__(self):
        if self.known_safe_locations is None:
            self.known_safe_locations = []
        if self.known_dangerous_locations is None:
            self.known_dangerous_locations = []
        if self.witnessed_crimes is None:
            self.witnessed_crimes = []
        if self.conversation_partners is None:
            self.conversation_partners = []


class CharacterAI:
    """AI controller for character behavior"""
    
    def __init__(self, character_physics: CharacterPhysics):
        self.character = character_physics
        self.character_type = character_physics.character_type
        
        # AI behavior state
        self.behavior = AIBehavior.IDLE
        self.behavior_timer = 0.0
        self.behavior_data = {}  # Behavior-specific data
        
        # Personality traits (0.0 to 1.0)
        self.traits = self._generate_personality()
        
        # AI memory and awareness
        self.memory = AIMemory()
        self.awareness_radius = 150.0  # pixels
        self.vision_angle = 140.0  # degrees
        self.hearing_radius = 200.0  # pixels
        
        # Pathfinding
        self.destination = None
        self.path_nodes = []
        self.current_path_index = 0
        self.stuck_timer = 0.0
        self.last_position = (self.character.x, self.character.y)
        
        # Threat assessment
        self.current_threat_level = ThreatLevel.NONE
        self.threats = []  # List of perceived threats
        self.allies = []   # List of allies/friends
        
        # Social behavior
        self.conversation_cooldown = 0.0
        self.social_interaction_range = 50.0
        
        # Decision making
        self.decision_timer = 0.0
        self.decision_interval = 2.0  # Make decisions every 2 seconds
        
        print(f"🧠 Character AI initialized: {self.character_type.value}")
        print(f"   Personality: Courage={self.traits['courage']:.2f}, "
              f"Curiosity={self.traits['curiosity']:.2f}, Social={self.traits['social']:.2f}")
    
    def _generate_personality(self) -> Dict[str, float]:
        """Generate personality traits based on character type"""
        base_traits = {
            'courage': 0.5,      # Willingness to face danger
            'curiosity': 0.5,    # Tendency to investigate
            'social': 0.5,       # Likelihood to interact with others
            'aggression': 0.2,   # Tendency toward violence
            'lawfulness': 0.7,   # Respect for law and order
            'helpfulness': 0.6,  # Willingness to help others
            'panic_threshold': 0.5,  # Threshold before panicking
        }
        
        # Modify traits based on character type
        type_modifiers = {
            CharacterType.POLICE: {
                'courage': 0.8, 'lawfulness': 0.9, 'aggression': 0.6,
                'panic_threshold': 0.8
            },
            CharacterType.GANG_MEMBER: {
                'courage': 0.7, 'aggression': 0.8, 'lawfulness': 0.2,
                'social': 0.3
            },
            CharacterType.CIVILIAN: {
                'courage': 0.4, 'curiosity': 0.6, 'social': 0.7
            },
            CharacterType.ELDERLY: {
                'courage': 0.3, 'curiosity': 0.3, 'social': 0.8,
                'panic_threshold': 0.3
            },
            CharacterType.CHILD: {
                'curiosity': 0.9, 'social': 0.6, 'courage': 0.2,
                'panic_threshold': 0.2
            },
            CharacterType.ATHLETE: {
                'courage': 0.7, 'aggression': 0.4, 'social': 0.5
            }
        }
        
        modifiers = type_modifiers.get(self.character_type, {})
        
        # Apply modifiers with some randomization
        traits = {}
        for trait, base_value in base_traits.items():
            modified_value = modifiers.get(trait, base_value)
            # Add random variation (±0.2)
            traits[trait] = max(0.0, min(1.0, modified_value + random.uniform(-0.2, 0.2)))
        
        return traits
    
    def update(self, dt: float, nearby_characters: List[Any] = None,
               nearby_vehicles: List[Any] = None, events: List[Dict] = None) -> None:
        """Update AI behavior"""
        # Update timers
        self.behavior_timer += dt
        self.decision_timer += dt
        self.conversation_cooldown = max(0, self.conversation_cooldown - dt)
        
        # Only update AI if character can act
        if not self.character.can_interact():
            return
        
        # Process events (crimes, explosions, etc.)
        if events:
            self._process_events(events)
        
        # Update awareness and threat assessment
        self._update_awareness(nearby_characters, nearby_vehicles)
        
        # Make decisions periodically
        if self.decision_timer >= self.decision_interval:
            self._make_decision(nearby_characters, nearby_vehicles)
            self.decision_timer = 0.0
        
        # Execute current behavior
        self._execute_behavior(dt, nearby_characters, nearby_vehicles)
        
        # Update pathfinding
        if self.destination:
            self._update_pathfinding(dt)
    
    def _process_events(self, events: List[Dict]) -> None:
        """Process world events and update memory"""
        for event in events:
            event_type = event.get('type')
            event_pos = event.get('position', (0, 0))
            distance = self._calculate_distance(event_pos, (self.character.x, self.character.y))
            
            # Only process events within hearing/sight range
            if distance > self.hearing_radius:
                continue
            
            if event_type == 'gunshot':
                self._react_to_gunshot(event_pos, distance)
            elif event_type == 'explosion':
                self._react_to_explosion(event_pos, distance)
            elif event_type == 'car_crash':
                self._react_to_crash(event_pos, distance)
            elif event_type == 'crime_witnessed':
                self._witness_crime(event)
            elif event_type == 'police_siren':
                self._react_to_siren(event_pos, distance)
    
    def _react_to_gunshot(self, position: Tuple[float, float], distance: float) -> None:
        """React to hearing gunshots"""
        panic_chance = 1.0 - (self.traits['courage'] * 0.8)
        
        if random.random() < panic_chance:
            self._enter_panic_mode()
            self.memory.last_threat_position = position
            self.memory.last_threat_time = time.time()
        elif self.traits['curiosity'] > 0.6 and self.character_type == CharacterType.POLICE:
            # Police investigate gunshots
            self.set_destination(position[0], position[1])
            self.behavior = AIBehavior.INVESTIGATING
    
    def _react_to_explosion(self, position: Tuple[float, float], distance: float) -> None:
        """React to explosions"""
        # Everyone flees from explosions
        self._enter_panic_mode()
        self._flee_from_position(position)
    
    def _witness_crime(self, event: Dict) -> None:
        """Witness a crime and decide how to react"""
        crime_type = event.get('crime_type', 'unknown')
        perpetrator = event.get('perpetrator')
        
        # Add to memory
        self.memory.witnessed_crimes.append({
            'type': crime_type,
            'time': time.time(),
            'position': event.get('position'),
            'perpetrator': perpetrator
        })
        
        # Decide reaction based on personality
        if self.traits['lawfulness'] > 0.7 and self.traits['courage'] > 0.5:
            # Call police
            self.behavior = AIBehavior.CALLING_POLICE
            self.behavior_timer = 0.0
        else:
            # Flee
            self._enter_panic_mode()
    
    def _update_awareness(self, nearby_characters: List[Any], nearby_vehicles: List[Any]) -> None:
        """Update awareness of surroundings"""
        self.threats.clear()
        self.allies.clear()
        
        # Assess nearby characters
        if nearby_characters:
            for other_char in nearby_characters:
                if other_char == self.character:
                    continue
                
                distance = self._calculate_distance(
                    (other_char.x, other_char.y),
                    (self.character.x, self.character.y)
                )
                
                if distance <= self.awareness_radius:
                    self._assess_character_threat(other_char, distance)
        
        # Assess nearby vehicles
        if nearby_vehicles:
            for vehicle in nearby_vehicles:
                distance = self._calculate_distance(
                    (vehicle.x, vehicle.y),
                    (self.character.x, self.character.y)
                )
                
                if distance <= self.awareness_radius:
                    self._assess_vehicle_threat(vehicle, distance)
    
    def _assess_character_threat(self, other_char: Any, distance: float) -> None:
        """Assess threat level of another character"""
        threat_level = 0
        
        # Check character type
        if hasattr(other_char, 'character_type'):
            if other_char.character_type == CharacterType.GANG_MEMBER:
                threat_level += 2
            elif other_char.character_type == CharacterType.POLICE and self.character_type == CharacterType.GANG_MEMBER:
                threat_level += 3
        
        # Check character state
        if hasattr(other_char, 'state'):
            if other_char.state == CharacterState.RAGDOLL:
                threat_level -= 1  # Less threatening when down
        
        # Check if armed (would need weapon system)
        # if other_char.is_armed:
        #     threat_level += 2
        
        if threat_level > 1:
            self.threats.append({
                'character': other_char,
                'threat_level': threat_level,
                'distance': distance
            })
        elif threat_level < 0:
            self.allies.append(other_char)
    
    def _assess_vehicle_threat(self, vehicle: Any, distance: float) -> None:
        """Assess threat from vehicles"""
        if hasattr(vehicle, 'get_speed_kmh'):
            speed = vehicle.get_speed_kmh()
            
            # Fast-moving vehicles are threats
            if speed > 50 and distance < 100:
                self.threats.append({
                    'vehicle': vehicle,
                    'threat_level': min(3, int(speed / 30)),
                    'distance': distance
                })
    
    def _make_decision(self, nearby_characters: List[Any], nearby_vehicles: List[Any]) -> None:
        """Make behavioral decisions based on current state"""
        # Assess overall threat level
        max_threat = max([t['threat_level'] for t in self.threats]) if self.threats else 0
        self.current_threat_level = ThreatLevel(min(4, max_threat))
        
        # Decision tree based on threat level and personality
        if self.current_threat_level.value >= 3:
            # High threat - flee or fight
            if self.traits['courage'] < 0.4:
                self._enter_panic_mode()
            elif self.character_type == CharacterType.POLICE:
                self._engage_threat()
        
        elif self.current_threat_level.value >= 2:
            # Medium threat - be cautious
            if self.behavior in [AIBehavior.IDLE, AIBehavior.WANDERING]:
                self._seek_safety()
        
        elif self.current_threat_level == ThreatLevel.NONE:
            # No threats - normal behavior
            self._choose_peaceful_behavior(nearby_characters, nearby_vehicles)
    
    def _choose_peaceful_behavior(self, nearby_characters: List[Any], nearby_vehicles: List[Any]) -> None:
        """Choose behavior when there are no threats"""
        # Random behavior selection based on personality
        if self.behavior == AIBehavior.IDLE and self.behavior_timer > 3.0:
            if self.traits['curiosity'] > 0.6 and random.random() < 0.3:
                self._start_wandering()
            elif self.traits['social'] > 0.6 and nearby_characters and random.random() < 0.2:
                self._initiate_conversation(nearby_characters)
        
        elif self.behavior == AIBehavior.WANDERING and self.behavior_timer > 10.0:
            if random.random() < 0.4:
                self.behavior = AIBehavior.IDLE
                self.behavior_timer = 0.0
    
    def _execute_behavior(self, dt: float, nearby_characters: List[Any], nearby_vehicles: List[Any]) -> None:
        """Execute the current behavior"""
        if self.behavior == AIBehavior.IDLE:
            self._execute_idle(dt)
        
        elif self.behavior == AIBehavior.WANDERING:
            self._execute_wandering(dt)
        
        elif self.behavior == AIBehavior.WALKING_TO_DESTINATION:
            self._execute_walking_to_destination(dt)
        
        elif self.behavior == AIBehavior.FLEEING:
            self._execute_fleeing(dt)
        
        elif self.behavior == AIBehavior.PANICKING:
            self._execute_panicking(dt)
        
        elif self.behavior == AIBehavior.INVESTIGATING:
            self._execute_investigating(dt)
        
        elif self.behavior == AIBehavior.CALLING_POLICE:
            self._execute_calling_police(dt)
        
        elif self.behavior == AIBehavior.TALKING:
            self._execute_talking(dt, nearby_characters)
    
    def _execute_idle(self, dt: float) -> None:
        """Execute idle behavior"""
        self.character.move(0, 0)  # Stop movement
        
        # Occasionally look around
        if random.random() < 0.1:
            self.character.facing_angle = random.uniform(0, 360)
    
    def _execute_wandering(self, dt: float) -> None:
        """Execute wandering behavior"""
        if not self.destination:
            # Pick random destination within reasonable range
            angle = random.uniform(0, 360)
            distance = random.uniform(100, 300)
            
            dest_x = self.character.x + math.cos(math.radians(angle)) * distance
            dest_y = self.character.y + math.sin(math.radians(angle)) * distance
            
            self.set_destination(dest_x, dest_y)
        
        # Move toward destination
        self._move_toward_destination()
        
        # Change direction occasionally
        if self.behavior_timer > random.uniform(5, 15):
            self.destination = None
            self.behavior_timer = 0.0
    
    def _execute_walking_to_destination(self, dt: float) -> None:
        """Execute walking to specific destination"""
        if self.destination:
            self._move_toward_destination()
            
            # Check if reached destination
            distance = self._calculate_distance(
                (self.character.x, self.character.y),
                self.destination
            )
            
            if distance < 20:  # Reached destination
                self.destination = None
                self.behavior = AIBehavior.IDLE
                self.behavior_timer = 0.0
        else:
            self.behavior = AIBehavior.IDLE
    
    def _execute_fleeing(self, dt: float) -> None:
        """Execute fleeing behavior"""
        if self.threats:
            # Flee from closest threat
            closest_threat = min(self.threats, key=lambda t: t['distance'])
            threat_pos = self._get_threat_position(closest_threat)
            
            if threat_pos:
                # Move away from threat
                flee_angle = math.atan2(
                    self.character.y - threat_pos[1],
                    self.character.x - threat_pos[0]
                )
                
                move_x = math.cos(flee_angle)
                move_y = math.sin(flee_angle)
                
                self.character.move(move_x, move_y)
                self.character.run(True)  # Run when fleeing
        
        # Stop fleeing after some time if no more threats
        if not self.threats and self.behavior_timer > 10.0:
            self.behavior = AIBehavior.SEEKING_SHELTER
    
    def _execute_panicking(self, dt: float) -> None:
        """Execute panic behavior"""
        # Erratic movement when panicking
        if random.random() < 0.3:
            move_x = random.uniform(-1, 1)
            move_y = random.uniform(-1, 1)
            self.character.move(move_x, move_y)
            self.character.run(True)
        
        # Gradually calm down
        if self.behavior_timer > 15.0 and not self.threats:
            self.behavior = AIBehavior.IDLE
            self.behavior_timer = 0.0
    
    def _execute_investigating(self, dt: float) -> None:
        """Execute investigation behavior"""
        if self.memory.last_threat_position:
            self.set_destination(*self.memory.last_threat_position)
            self._move_toward_destination()
            
            # Stop investigating after reaching location
            if self.destination:
                distance = self._calculate_distance(
                    (self.character.x, self.character.y),
                    self.destination
                )
                if distance < 30:
                    self.behavior = AIBehavior.IDLE
                    self.destination = None
    
    def _execute_calling_police(self, dt: float) -> None:
        """Execute calling police behavior"""
        # Stop moving while calling
        self.character.move(0, 0)
        
        # After 5 seconds, finish call
        if self.behavior_timer > 5.0:
            self.behavior = AIBehavior.IDLE
            self.behavior_timer = 0.0
            print(f"📞 {self.character_type.value} called police")
    
    def _execute_talking(self, dt: float, nearby_characters: List[Any]) -> None:
        """Execute conversation behavior"""
        # Stop moving while talking
        self.character.move(0, 0)
        
        # End conversation after some time
        if self.behavior_timer > random.uniform(10, 30):
            self.behavior = AIBehavior.IDLE
            self.behavior_timer = 0.0
            self.conversation_cooldown = 60.0  # Don't talk again for a minute
    
    def _move_toward_destination(self) -> None:
        """Move character toward current destination"""
        if not self.destination:
            return
        
        # Calculate direction to destination
        dx = self.destination[0] - self.character.x
        dy = self.destination[1] - self.character.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 10:  # Move if not close enough
            # Normalize direction
            move_x = dx / distance
            move_y = dy / distance
            
            self.character.move(move_x, move_y)
        else:
            self.character.move(0, 0)
    
    def _update_pathfinding(self, dt: float) -> None:
        """Update pathfinding and stuck detection"""
        current_pos = (self.character.x, self.character.y)
        distance_moved = self._calculate_distance(current_pos, self.last_position)
        
        # Check if stuck
        if distance_moved < 5:  # Not moving much
            self.stuck_timer += dt
            
            if self.stuck_timer > 3.0:  # Stuck for 3 seconds
                self._handle_stuck()
        else:
            self.stuck_timer = 0.0
        
        self.last_position = current_pos
    
    def _handle_stuck(self) -> None:
        """Handle being stuck by finding new destination"""
        # Try random direction
        angle = random.uniform(0, 360)
        distance = 50
        
        new_x = self.character.x + math.cos(math.radians(angle)) * distance
        new_y = self.character.y + math.sin(math.radians(angle)) * distance
        
        self.set_destination(new_x, new_y)
        self.stuck_timer = 0.0
    
    def _start_wandering(self) -> None:
        """Start wandering behavior"""
        self.behavior = AIBehavior.WANDERING
        self.behavior_timer = 0.0
        self.destination = None
    
    def _enter_panic_mode(self) -> None:
        """Enter panic state"""
        self.behavior = AIBehavior.PANICKING
        self.behavior_timer = 0.0
        print(f"😱 {self.character_type.value} is panicking!")
    
    def _flee_from_position(self, threat_pos: Tuple[float, float]) -> None:
        """Flee from a specific position"""
        self.behavior = AIBehavior.FLEEING
        self.behavior_timer = 0.0
        
        # Set destination away from threat
        flee_angle = math.atan2(
            self.character.y - threat_pos[1],
            self.character.x - threat_pos[0]
        )
        
        flee_distance = 200
        dest_x = self.character.x + math.cos(flee_angle) * flee_distance
        dest_y = self.character.y + math.sin(flee_angle) * flee_distance
        
        self.set_destination(dest_x, dest_y)
    
    def _seek_safety(self) -> None:
        """Seek safe location"""
        self.behavior = AIBehavior.SEEKING_SHELTER
        self.behavior_timer = 0.0
        
        # For now, just move to a random safe location
        if self.memory.known_safe_locations:
            safe_spot = random.choice(self.memory.known_safe_locations)
            self.set_destination(*safe_spot)
        else:
            # Default: move away from threats
            if self.threats:
                closest_threat = min(self.threats, key=lambda t: t['distance'])
                threat_pos = self._get_threat_position(closest_threat)
                if threat_pos:
                    self._flee_from_position(threat_pos)
    
    def _engage_threat(self) -> None:
        """Engage with threat (for police/security)"""
        self.behavior = AIBehavior.ATTACKING
        self.behavior_timer = 0.0
        
        if self.threats:
            closest_threat = min(self.threats, key=lambda t: t['distance'])
            threat_pos = self._get_threat_position(closest_threat)
            if threat_pos:
                self.set_destination(*threat_pos)
    
    def _initiate_conversation(self, nearby_characters: List[Any]) -> None:
        """Start conversation with nearby character"""
        if self.conversation_cooldown > 0:
            return
        
        # Find suitable conversation partner
        for other_char in nearby_characters:
            if other_char == self.character:
                continue
            
            distance = self._calculate_distance(
                (other_char.x, other_char.y),
                (self.character.x, self.character.y)
            )
            
            if distance < self.social_interaction_range and other_char.can_interact():
                self.behavior = AIBehavior.TALKING
                self.behavior_timer = 0.0
                self.behavior_data['conversation_partner'] = other_char
                print(f"💬 {self.character_type.value} started conversation")
                break
    
    def _get_threat_position(self, threat: Dict) -> Optional[Tuple[float, float]]:
        """Get position of a threat"""
        if 'character' in threat:
            char = threat['character']
            return (char.x, char.y)
        elif 'vehicle' in threat:
            vehicle = threat['vehicle']
            return (vehicle.x, vehicle.y)
        return None
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def set_destination(self, x: float, y: float) -> None:
        """Set movement destination"""
        self.destination = (x, y)
        if self.behavior == AIBehavior.IDLE:
            self.behavior = AIBehavior.WALKING_TO_DESTINATION
    
    def force_behavior(self, behavior: AIBehavior) -> None:
        """Force specific behavior (for scripted events)"""
        self.behavior = behavior
        self.behavior_timer = 0.0
    
    def get_status_info(self) -> Dict:
        """Get AI status information"""
        return {
            'behavior': self.behavior.value,
            'threat_level': self.current_threat_level.value,
            'destination': self.destination,
            'threats_detected': len(self.threats),
            'personality': self.traits,
            'health': self.character.health,
            'stamina': self.character.stamina,
            'state': self.character.state.value
        }