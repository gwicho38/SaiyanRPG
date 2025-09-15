#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced Game Integration System - Brings all new features together

import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .physics_manager import PhysicsManager, CollisionCategory, PhysicsBodyType
from .vehicle_physics import VehiclePhysicsSystem, VehicleState
from .character_ai import CharacterAIManager, StimulusType, Stimulus
from .world_3d_system import World3DSystem, BlockType, DistrictType


@dataclass
class GameIntegrationState:
    """State container for the enhanced game integration"""
    # Core systems
    physics_manager: PhysicsManager
    vehicle_physics: VehiclePhysicsSystem
    character_ai: CharacterAIManager
    world_3d: World3DSystem
    
    # Game state
    player_vehicle_id: Optional[int]
    player_character_id: Optional[int]
    game_time: float
    real_time_played: float
    
    # Statistics
    total_vehicles_spawned: int
    total_characters_spawned: int
    total_crimes_committed: int
    total_distance_traveled: float
    
    # Performance tracking
    frame_times: List[float]
    physics_update_times: List[float]
    ai_update_times: List[float]


class EnhancedGameIntegration:
    """Enhanced game integration system that coordinates all advanced features"""
    
    def __init__(self):
        # Initialize core systems
        self.physics_manager = PhysicsManager(gravity=(0, 0))  # Top-down game
        self.vehicle_physics = VehiclePhysicsSystem(self.physics_manager)
        self.character_ai = CharacterAIManager(self.physics_manager)
        self.world_3d = World3DSystem(1000, 1000, 3)  # Large world with 3 layers
        
        # Initialize game state
        self.state = GameIntegrationState(
            physics_manager=self.physics_manager,
            vehicle_physics=self.vehicle_physics,
            character_ai=self.character_ai,
            world_3d=self.world_3d,
            player_vehicle_id=None,
            player_character_id=None,
            game_time=0.0,
            real_time_played=0.0,
            total_vehicles_spawned=0,
            total_characters_spawned=0,
            total_crimes_committed=0,
            total_distance_traveled=0.0,
            frame_times=[],
            physics_update_times=[],
            ai_update_times=[]
        )
        
        # Setup collision callbacks
        self._setup_collision_callbacks()
        
        # Initialize world
        self._initialize_world()
        
        print("🎮 EnhancedGameIntegration initialized with all advanced features")
    
    def _setup_collision_callbacks(self) -> None:
        """Setup collision callbacks between different systems"""
        # Vehicle vs Pedestrian collisions
        self.physics_manager.register_collision_callback(
            CollisionCategory.VEHICLE, CollisionCategory.PEDESTRIAN,
            self._handle_vehicle_pedestrian_collision
        )
        
        # Vehicle vs Vehicle collisions
        self.physics_manager.register_collision_callback(
            CollisionCategory.VEHICLE, CollisionCategory.VEHICLE,
            self._handle_vehicle_vehicle_collision
        )
        
        # Projectile vs Vehicle collisions
        self.physics_manager.register_collision_callback(
            CollisionCategory.PROJECTILE, CollisionCategory.VEHICLE,
            self._handle_projectile_vehicle_collision
        )
        
        # Projectile vs Pedestrian collisions
        self.physics_manager.register_collision_callback(
            CollisionCategory.PROJECTILE, CollisionCategory.PEDESTRIAN,
            self._handle_projectile_pedestrian_collision
        )
    
    def _initialize_world(self) -> None:
        """Initialize the game world with content"""
        # Create districts
        downtown_id = self.world_3d.create_district(
            "Downtown", DistrictType.DOWNTOWN, (0, 0, 499, 499)
        )
        
        residential_id = self.world_3d.create_district(
            "Residential", DistrictType.RESIDENTIAL, (500, 0, 999, 499)
        )
        
        commercial_id = self.world_3d.create_district(
            "Commercial", DistrictType.COMMERCIAL, (0, 500, 499, 999)
        )
        
        industrial_id = self.world_3d.create_district(
            "Industrial", DistrictType.INDUSTRIAL, (500, 500, 999, 999)
        )
        
        # Generate navigation sectors
        self.world_3d.generate_navigation_sectors()
        
        # Spawn initial content
        self._spawn_initial_content()
        
        print("🌍 World initialized with districts and navigation")
    
    def _spawn_initial_content(self) -> None:
        """Spawn initial vehicles and characters"""
        # Spawn player character
        self.state.player_character_id = self.character_ai.create_character(
            1, (500, 500)  # Center of downtown
        ).character_id
        
        # Spawn some vehicles
        vehicle_types = ['sedan', 'sports_car', 'truck', 'motorcycle']
        for i in range(20):
            vehicle_type = random.choice(vehicle_types)
            x = random.uniform(100, 900)
            y = random.uniform(100, 900)
            
            vehicle_id = self.vehicle_physics.create_vehicle(vehicle_type, (x, y))
            self.state.total_vehicles_spawned += 1
        
        # Spawn some pedestrians
        for i in range(50):
            x = random.uniform(50, 950)
            y = random.uniform(50, 950)
            
            character_id = self.character_ai.create_character(i + 2, (x, y)).character_id
            self.state.total_characters_spawned += 1
        
        print(f"🚗 Spawned {self.state.total_vehicles_spawned} vehicles and {self.state.total_characters_spawned} characters")
    
    def update(self, dt: float, input_state: Dict[str, Any]) -> None:
        """Update all game systems"""
        start_time = time.time()
        
        # Update game time
        self.state.game_time += dt
        self.state.real_time_played += dt
        
        # Update world state
        self.world_3d.update_world_state(dt)
        
        # Update physics
        physics_start = time.time()
        self.physics_manager.update(dt)
        physics_time = time.time() - physics_start
        self.state.physics_update_times.append(physics_time)
        
        # Update vehicle physics
        self._update_vehicles(dt, input_state)
        
        # Update character AI
        ai_start = time.time()
        game_state_dict = self._get_game_state_dict()
        self.character_ai.update_all_characters(dt, game_state_dict)
        ai_time = time.time() - ai_start
        self.state.ai_update_times.append(ai_time)
        
        # Update dynamic content
        self._update_dynamic_content(dt)
        
        # Process input
        self._process_input(input_state)
        
        # Update statistics
        self._update_statistics(dt)
        
        # Track frame time
        frame_time = time.time() - start_time
        self.state.frame_times.append(frame_time)
        
        # Keep only recent frame times (last 60 frames)
        if len(self.state.frame_times) > 60:
            self.state.frame_times = self.state.frame_times[-60:]
        if len(self.state.physics_update_times) > 60:
            self.state.physics_update_times = self.state.physics_update_times[-60:]
        if len(self.state.ai_update_times) > 60:
            self.state.ai_update_times = self.state.ai_update_times[-60:]
    
    def _update_vehicles(self, dt: float, input_state: Dict[str, Any]) -> None:
        """Update all vehicles"""
        for vehicle_id in list(self.vehicle_physics.vehicles.keys()):
            vehicle_data = self.vehicle_physics.vehicles[vehicle_id]
            
            # Get input for player vehicle
            if vehicle_id == self.state.player_vehicle_id:
                throttle = input_state.get('throttle', 0.0)
                brake = input_state.get('brake', 0.0)
                steering = input_state.get('steering', 0.0)
                handbrake = input_state.get('handbrake', False)
            else:
                # AI vehicle behavior
                throttle, brake, steering, handbrake = self._get_ai_vehicle_input(vehicle_id)
            
            # Update vehicle physics
            self.vehicle_physics.update_vehicle(vehicle_id, dt, throttle, brake, steering, handbrake)
    
    def _get_ai_vehicle_input(self, vehicle_id: int) -> Tuple[float, float, float, bool]:
        """Get AI input for a vehicle"""
        vehicle_data = self.vehicle_physics.vehicles[vehicle_id]
        position = self.vehicle_physics.get_vehicle_position(vehicle_id)
        speed = self.vehicle_physics.get_vehicle_speed(vehicle_id)
        
        # Simple AI: drive forward with occasional steering
        throttle = 0.3 if speed < 20.0 else 0.1  # Slow down if going too fast
        brake = 0.0
        steering = random.uniform(-0.2, 0.2) if random.random() < 0.1 else 0.0  # Occasional steering
        handbrake = False
        
        return throttle, brake, steering, handbrake
    
    def _update_dynamic_content(self, dt: float) -> None:
        """Update dynamic content (spawning, despawning, etc.)"""
        # Spawn new vehicles occasionally
        import random
        if random.random() < 0.01:  # 1% chance per frame
            self._spawn_random_vehicle()
        
        # Spawn new pedestrians occasionally
        if random.random() < 0.005:  # 0.5% chance per frame
            self._spawn_random_character()
        
        # Remove vehicles that are too far from player
        self._cleanup_distant_vehicles()
        
        # Remove characters that are too far from player
        self._cleanup_distant_characters()
    
    def _spawn_random_vehicle(self) -> None:
        """Spawn a random vehicle"""
        vehicle_types = ['sedan', 'sports_car', 'truck', 'motorcycle']
        vehicle_type = random.choice(vehicle_types)
        
        # Spawn near the edge of the world
        if random.random() < 0.5:
            x = random.choice([0, 999])
            y = random.uniform(0, 999)
        else:
            x = random.uniform(0, 999)
            y = random.choice([0, 999])
        
        vehicle_id = self.vehicle_physics.create_vehicle(vehicle_type, (x, y))
        self.state.total_vehicles_spawned += 1
    
    def _spawn_random_character(self) -> None:
        """Spawn a random character"""
        x = random.uniform(50, 950)
        y = random.uniform(50, 950)
        
        character_id = self.character_ai.create_character(
            self.state.total_characters_spawned + 1000, (x, y)
        ).character_id
        self.state.total_characters_spawned += 1
    
    def _cleanup_distant_vehicles(self) -> None:
        """Remove vehicles that are too far from the player"""
        if not self.state.player_vehicle_id:
            return
        
        player_pos = self.vehicle_physics.get_vehicle_position(self.state.player_vehicle_id)
        max_distance = 500.0  # 500 units
        
        vehicles_to_remove = []
        for vehicle_id in self.vehicle_physics.vehicles.keys():
            if vehicle_id == self.state.player_vehicle_id:
                continue
            
            vehicle_pos = self.vehicle_physics.get_vehicle_position(vehicle_id)
            distance = ((vehicle_pos[0] - player_pos[0])**2 + 
                       (vehicle_pos[1] - player_pos[1])**2)**0.5
            
            if distance > max_distance:
                vehicles_to_remove.append(vehicle_id)
        
        for vehicle_id in vehicles_to_remove:
            self.vehicle_physics.remove_vehicle(vehicle_id)
    
    def _cleanup_distant_characters(self) -> None:
        """Remove characters that are too far from the player"""
        if not self.state.player_character_id:
            return
        
        player_pos = self.character_ai.character_controllers[self.state.player_character_id].physics_body.position
        max_distance = 300.0  # 300 units
        
        characters_to_remove = []
        for character_id, controller in self.character_ai.character_controllers.items():
            if character_id == self.state.player_character_id:
                continue
            
            character_pos = controller.physics_body.position
            distance = ((character_pos[0] - player_pos[0])**2 + 
                       (character_pos[1] - player_pos[1])**2)**0.5
            
            if distance > max_distance:
                characters_to_remove.append(character_id)
        
        for character_id in characters_to_remove:
            self.character_ai.remove_character(character_id)
    
    def _process_input(self, input_state: Dict[str, Any]) -> None:
        """Process player input"""
        # Handle vehicle entry/exit
        if input_state.get('enter_exit_vehicle', False):
            self._handle_vehicle_entry_exit()
        
        # Handle weapon switching
        if input_state.get('next_weapon', False):
            self._switch_weapon(1)
        elif input_state.get('prev_weapon', False):
            self._switch_weapon(-1)
        
        # Handle shooting
        if input_state.get('fire', False):
            self._handle_shooting()
    
    def _handle_vehicle_entry_exit(self) -> None:
        """Handle vehicle entry/exit"""
        if self.state.player_vehicle_id:
            # Exit vehicle
            self.state.player_vehicle_id = None
            print("🚗 Player exited vehicle")
        else:
            # Find nearby vehicle to enter
            if self.state.player_character_id:
                player_pos = self.character_ai.character_controllers[self.state.player_character_id].physics_body.position
                
                # Find closest vehicle
                closest_vehicle = None
                closest_distance = float('inf')
                
                for vehicle_id in self.vehicle_physics.vehicles.keys():
                    vehicle_pos = self.vehicle_physics.get_vehicle_position(vehicle_id)
                    distance = ((vehicle_pos[0] - player_pos[0])**2 + 
                               (vehicle_pos[1] - player_pos[1])**2)**0.5
                    
                    if distance < 10.0 and distance < closest_distance:  # Within 10 units
                        closest_vehicle = vehicle_id
                        closest_distance = distance
                
                if closest_vehicle:
                    self.state.player_vehicle_id = closest_vehicle
                    print(f"🚗 Player entered vehicle {closest_vehicle}")
    
    def _switch_weapon(self, direction: int) -> None:
        """Switch weapon"""
        # This would integrate with the weapon system
        print(f"🔫 Switching weapon: {direction}")
    
    def _handle_shooting(self) -> None:
        """Handle shooting"""
        # Create gunshot stimulus
        if self.state.player_character_id:
            player_pos = self.character_ai.character_controllers[self.state.player_character_id].physics_body.position
            
            gunshot = Stimulus(
                stimulus_type=StimulusType.GUNSHOT,
                position=player_pos,
                intensity=0.8,
                radius=100.0,
                timestamp=time.time()
            )
            
            self.character_ai.add_stimulus(gunshot)
            self.state.total_crimes_committed += 1
            print("🔫 Player fired weapon")
    
    def _update_statistics(self, dt: float) -> None:
        """Update game statistics"""
        # Update distance traveled
        if self.state.player_vehicle_id:
            speed = self.vehicle_physics.get_vehicle_speed(self.state.player_vehicle_id)
            self.state.total_distance_traveled += speed * dt
    
    def _get_game_state_dict(self) -> Dict[str, Any]:
        """Get game state dictionary for AI systems"""
        player_pos = (0, 0)
        player_speed = 0.0
        
        if self.state.player_vehicle_id:
            player_pos = self.vehicle_physics.get_vehicle_position(self.state.player_vehicle_id)
            player_speed = self.vehicle_physics.get_vehicle_speed(self.state.player_vehicle_id)
        elif self.state.player_character_id:
            player_pos = self.character_ai.character_controllers[self.state.player_character_id].physics_body.position
        
        return {
            'player_x': player_pos[0],
            'player_y': player_pos[1],
            'player_speed': player_speed,
            'player_vehicle': self.state.player_vehicle_id,
            'player_hidden': False,
            'game_time': self.state.game_time,
            'time_of_day': self.world_3d.time_of_day,
            'weather': self.world_3d.weather,
            'temperature': self.world_3d.temperature
        }
    
    # Collision handlers
    def _handle_vehicle_pedestrian_collision(self, collision_info) -> None:
        """Handle vehicle hitting pedestrian"""
        print(f"💥 Vehicle {collision_info.body_b.body_id} hit pedestrian {collision_info.body_a.body_id}")
        
        # Create collision stimulus
        collision_stimulus = Stimulus(
            stimulus_type=StimulusType.VEHICLE_CRASH,
            position=collision_info.contact_point,
            intensity=0.6,
            radius=50.0,
            timestamp=time.time()
        )
        
        self.character_ai.add_stimulus(collision_stimulus)
        self.state.total_crimes_committed += 1
    
    def _handle_vehicle_vehicle_collision(self, collision_info) -> None:
        """Handle vehicle hitting vehicle"""
        print(f"💥 Vehicle collision: {collision_info.body_a.body_id} <-> {collision_info.body_b.body_id}")
        
        # Create collision stimulus
        collision_stimulus = Stimulus(
            stimulus_type=StimulusType.VEHICLE_CRASH,
            position=collision_info.contact_point,
            intensity=0.7,
            radius=75.0,
            timestamp=time.time()
        )
        
        self.character_ai.add_stimulus(collision_stimulus)
    
    def _handle_projectile_vehicle_collision(self, collision_info) -> None:
        """Handle projectile hitting vehicle"""
        print(f"💥 Projectile hit vehicle {collision_info.body_b.body_id}")
        
        # Create explosion stimulus
        explosion_stimulus = Stimulus(
            stimulus_type=StimulusType.EXPLOSION,
            position=collision_info.contact_point,
            intensity=0.9,
            radius=100.0,
            timestamp=time.time()
        )
        
        self.character_ai.add_stimulus(explosion_stimulus)
    
    def _handle_projectile_pedestrian_collision(self, collision_info) -> None:
        """Handle projectile hitting pedestrian"""
        print(f"💥 Projectile hit pedestrian {collision_info.body_b.body_id}")
        
        # Create violence stimulus
        violence_stimulus = Stimulus(
            stimulus_type=StimulusType.VIOLENCE,
            position=collision_info.contact_point,
            intensity=0.8,
            radius=80.0,
            timestamp=time.time()
        )
        
        self.character_ai.add_stimulus(violence_stimulus)
        self.state.total_crimes_committed += 1
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.state.frame_times:
            return {}
        
        avg_frame_time = sum(self.state.frame_times) / len(self.state.frame_times)
        avg_physics_time = sum(self.state.physics_update_times) / len(self.state.physics_update_times)
        avg_ai_time = sum(self.state.ai_update_times) / len(self.state.ai_update_times)
        
        return {
            'fps': 1.0 / avg_frame_time if avg_frame_time > 0 else 0,
            'avg_frame_time_ms': avg_frame_time * 1000,
            'avg_physics_time_ms': avg_physics_time * 1000,
            'avg_ai_time_ms': avg_ai_time * 1000,
            'physics_bodies': len(self.physics_manager.bodies),
            'vehicles': len(self.vehicle_physics.vehicles),
            'characters': len(self.character_ai.character_controllers),
            'total_distance_km': self.state.total_distance_traveled / 1000.0,
            'crimes_committed': self.state.total_crimes_committed,
            'game_time_hours': self.state.game_time / 3600.0
        }
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive game statistics"""
        return {
            'performance': self.get_performance_statistics(),
            'physics': self.physics_manager.get_statistics(),
            'vehicles': self.vehicle_physics.get_vehicle_statistics(),
            'characters': self.character_ai.get_character_statistics(),
            'world': self.world_3d.get_world_statistics(),
            'game_state': {
                'player_vehicle_id': self.state.player_vehicle_id,
                'player_character_id': self.state.player_character_id,
                'total_vehicles_spawned': self.state.total_vehicles_spawned,
                'total_characters_spawned': self.state.total_characters_spawned,
                'total_crimes_committed': self.state.total_crimes_committed,
                'total_distance_traveled': self.state.total_distance_traveled,
                'game_time': self.state.game_time,
                'real_time_played': self.state.real_time_played
            }
        }


# Test the enhanced game integration
if __name__ == "__main__":
    print("🧪 Testing EnhancedGameIntegration...")
    
    # Create enhanced game integration
    game = EnhancedGameIntegration()
    
    # Test update loop
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 10.0:  # Run for 10 seconds
        dt = 1.0 / 60.0  # 60 FPS
        
        # Simulate input
        input_state = {
            'throttle': 0.5 if frame_count % 120 < 60 else 0.0,  # Accelerate for 1 second, coast for 1 second
            'brake': 0.0,
            'steering': 0.3 if frame_count % 240 < 60 else -0.3 if frame_count % 240 < 120 else 0.0,
            'handbrake': False,
            'fire': frame_count % 300 == 0,  # Fire every 5 seconds
            'enter_exit_vehicle': frame_count == 100,  # Enter vehicle after 100 frames
            'next_weapon': False,
            'prev_weapon': False
        }
        
        # Update game
        game.update(dt, input_state)
        
        frame_count += 1
        
        # Print statistics every 60 frames (1 second)
        if frame_count % 60 == 0:
            stats = game.get_performance_statistics()
            print(f"FPS: {stats.get('fps', 0):.1f}, "
                  f"Vehicles: {stats.get('vehicles', 0)}, "
                  f"Characters: {stats.get('characters', 0)}, "
                  f"Distance: {stats.get('total_distance_km', 0):.2f} km")
    
    # Print final comprehensive statistics
    print("\n📊 Final Statistics:")
    final_stats = game.get_comprehensive_statistics()
    for category, stats in final_stats.items():
        print(f"\n{category.upper()}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print("✅ EnhancedGameIntegration test completed")