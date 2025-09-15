#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced Integration System - Phase 3 Features Integration

import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .enhanced_game_integration import EnhancedGameIntegration
from .traffic_management import TrafficManager, TrafficDensity, TrafficBehavior
from .audio_system import SpatialAudioSystem, VehicleAudioSystem, EnvironmentalAudioSystem, AudioType
from .input_controls import InputManager, ControlScheme, InputAction


@dataclass
class Phase3IntegrationState:
    """State container for Phase 3 integration"""
    # Core systems from Phase 1-2
    base_game: EnhancedGameIntegration
    
    # Phase 3 systems
    traffic_manager: TrafficManager
    spatial_audio: SpatialAudioSystem
    vehicle_audio: VehicleAudioSystem
    environmental_audio: EnvironmentalAudioSystem
    input_manager: InputManager
    
    # Integration state
    player_audio_sources: Dict[int, int]  # vehicle_id -> audio_source_id
    traffic_audio_sources: Dict[int, Dict[str, int]]  # vehicle_id -> {engine, brake, horn}
    
    # Statistics
    total_audio_sources: int
    total_traffic_vehicles: int
    input_events_processed: int


class EnhancedIntegrationPhase3:
    """Enhanced integration system with Phase 3 features"""
    
    def __init__(self):
        # Initialize base game integration
        self.base_game = EnhancedGameIntegration()
        
        # Initialize Phase 3 systems
        self.traffic_manager = TrafficManager(
            self.base_game.vehicle_physics,
            self.base_game.world_3d
        )
        
        self.spatial_audio = SpatialAudioSystem()
        self.vehicle_audio = VehicleAudioSystem(self.spatial_audio)
        self.environmental_audio = EnvironmentalAudioSystem(self.spatial_audio)
        self.input_manager = InputManager()
        
        # Initialize integration state
        self.state = Phase3IntegrationState(
            base_game=self.base_game,
            traffic_manager=self.traffic_manager,
            spatial_audio=self.spatial_audio,
            vehicle_audio=self.vehicle_audio,
            environmental_audio=self.environmental_audio,
            input_manager=self.input_manager,
            player_audio_sources={},
            traffic_audio_sources={},
            total_audio_sources=0,
            total_traffic_vehicles=0,
            input_events_processed=0
        )
        
        # Setup audio integration
        self._setup_audio_integration()
        
        # Setup traffic integration
        self._setup_traffic_integration()
        
        print("🎮 EnhancedIntegrationPhase3 initialized with all Phase 3 features")
    
    def _setup_audio_integration(self):
        """Setup audio system integration"""
        # Create audio for existing vehicles
        for vehicle_id in self.base_game.vehicle_physics.vehicles.keys():
            position = self.base_game.vehicle_physics.get_vehicle_position(vehicle_id)
            self.vehicle_audio.create_vehicle_audio(vehicle_id, position)
            self.state.total_audio_sources += 3  # engine, brake, horn
        
        print(f"🔊 Audio integration setup complete: {self.state.total_audio_sources} sources")
    
    def _setup_traffic_integration(self):
        """Setup traffic system integration"""
        # Set initial traffic density
        self.traffic_manager.set_traffic_density(TrafficDensity.MODERATE)
        
        print("🚦 Traffic integration setup complete")
    
    def update(self, dt: float) -> None:
        """Update all integrated systems"""
        # Get player position for audio listener and traffic management
        player_position = self._get_player_position()
        
        # Update input system
        input_state = self.input_manager.update_input_state(dt)
        self.state.input_events_processed += 1
        
        # Convert input to game input format
        game_input = self._convert_input_to_game_format(input_state)
        
        # Update base game
        self.base_game.update(dt, game_input)
        
        # Update traffic management
        self.traffic_manager.update(dt, player_position)
        
        # Update audio systems
        self._update_audio_systems(dt, player_position)
        
        # Update environmental audio
        self.environmental_audio.update_environmental_audio(
            self.base_game.world_3d.weather,
            self.base_game.world_3d.time_of_day
        )
        
        # Update spatial audio
        self.spatial_audio.update(dt)
        
        # Update statistics
        self._update_statistics()
    
    def _get_player_position(self) -> Tuple[float, float]:
        """Get current player position"""
        if self.base_game.state.player_vehicle_id:
            return self.base_game.vehicle_physics.get_vehicle_position(
                self.base_game.state.player_vehicle_id
            )
        elif self.base_game.state.player_character_id:
            controller = self.base_game.character_ai.character_controllers.get(
                self.base_game.state.player_character_id
            )
            if controller:
                return controller.physics_body.position
        
        return (500, 500)  # Default center position
    
    def _convert_input_to_game_format(self, input_state) -> Dict[str, Any]:
        """Convert input manager state to game input format"""
        vehicle_inputs = self.input_manager.get_vehicle_inputs()
        weapon_inputs = self.input_manager.get_weapon_inputs()
        interaction_inputs = self.input_manager.get_interaction_inputs()
        
        return {
            'throttle': vehicle_inputs['throttle'],
            'brake': vehicle_inputs['brake'],
            'steering': vehicle_inputs['steering'],
            'handbrake': vehicle_inputs['handbrake'],
            'fire': weapon_inputs['fire'],
            'aim': weapon_inputs['aim'],
            'reload': weapon_inputs['reload'],
            'next_weapon': weapon_inputs['next_weapon'],
            'prev_weapon': weapon_inputs['prev_weapon'],
            'enter_exit_vehicle': interaction_inputs['enter_exit_vehicle'],
            'interact': interaction_inputs['interact'],
            'jump': interaction_inputs['jump'],
            'crouch': interaction_inputs['crouch'],
            'sprint': interaction_inputs['sprint']
        }
    
    def _update_audio_systems(self, dt: float, player_position: Tuple[float, float]):
        """Update audio systems"""
        # Update spatial audio listener position
        player_velocity = (0.0, 0.0)  # Could calculate from position delta
        self.spatial_audio.set_listener_position(player_position, player_velocity)
        
        # Update vehicle audio for all vehicles
        for vehicle_id in self.base_game.vehicle_physics.vehicles.keys():
            position = self.base_game.vehicle_physics.get_vehicle_position(vehicle_id)
            speed = self.base_game.vehicle_physics.get_vehicle_speed(vehicle_id)
            
            # Get vehicle inputs (simplified - could be from AI or player)
            if vehicle_id == self.base_game.state.player_vehicle_id:
                vehicle_inputs = self.input_manager.get_vehicle_inputs()
                throttle = vehicle_inputs['throttle']
                brake = vehicle_inputs['brake']
                horn = vehicle_inputs['horn']
            else:
                # AI vehicle inputs (simplified)
                throttle = random.uniform(0.0, 0.5)
                brake = random.uniform(0.0, 0.2)
                horn = random.random() < 0.01  # 1% chance per frame
            
            # Update vehicle audio
            self.vehicle_audio.update_vehicle_audio(
                vehicle_id, position, speed, throttle, brake, horn
            )
    
    def _update_statistics(self):
        """Update integration statistics"""
        self.state.total_traffic_vehicles = len(self.traffic_manager.traffic_vehicles)
        self.state.total_audio_sources = len(self.spatial_audio.audio_sources)
    
    def set_control_scheme(self, scheme: ControlScheme):
        """Set the control scheme"""
        self.input_manager.set_control_scheme(scheme)
        print(f"🎮 Control scheme set to {scheme.value}")
    
    def set_traffic_density(self, density: TrafficDensity):
        """Set traffic density"""
        self.traffic_manager.set_traffic_density(density)
        print(f"🚦 Traffic density set to {density.name}")
    
    def set_audio_volume(self, volume_type: str, volume: float):
        """Set audio volume"""
        if volume_type == "master":
            self.spatial_audio.set_master_volume(volume)
        elif volume_type == "sfx":
            self.spatial_audio.set_sfx_volume(volume)
        elif volume_type == "music":
            self.spatial_audio.set_music_volume(volume)
        else:
            print(f"❌ Unknown volume type: {volume_type}")
    
    def create_audio_event(self, audio_type: AudioType, position: Tuple[float, float],
                          volume: float = 1.0, priority: str = "normal") -> int:
        """Create a one-time audio event"""
        from saiyanquest.audio_system import AudioPriority
        
        priority_map = {
            "low": AudioPriority.LOW,
            "normal": AudioPriority.NORMAL,
            "high": AudioPriority.HIGH,
            "critical": AudioPriority.CRITICAL
        }
        
        audio_priority = priority_map.get(priority, AudioPriority.NORMAL)
        
        source_id = self.spatial_audio.create_audio_source(
            audio_type, position, volume, priority=audio_priority
        )
        
        # Play the audio
        self.spatial_audio.play_audio(source_id)
        
        return source_id
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all systems"""
        base_stats = self.base_game.get_comprehensive_statistics()
        
        # Add Phase 3 statistics
        phase3_stats = {
            'traffic': self.traffic_manager.get_traffic_statistics(),
            'audio': self.spatial_audio.get_audio_statistics(),
            'input': self.input_manager.get_input_statistics(),
            'integration': {
                'total_audio_sources': self.state.total_audio_sources,
                'total_traffic_vehicles': self.state.total_traffic_vehicles,
                'input_events_processed': self.state.input_events_processed,
                'player_audio_sources': len(self.state.player_audio_sources),
                'traffic_audio_sources': len(self.state.traffic_audio_sources)
            }
        }
        
        # Merge statistics
        comprehensive_stats = base_stats.copy()
        comprehensive_stats['phase3'] = phase3_stats
        
        return comprehensive_stats
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        base_perf = self.base_game.get_performance_statistics()
        
        # Add Phase 3 performance metrics
        phase3_perf = {
            'traffic_vehicles': self.state.total_traffic_vehicles,
            'audio_sources': self.state.total_audio_sources,
            'input_events': self.state.input_events_processed,
            'traffic_density': self.traffic_manager.traffic_density.name,
            'control_scheme': self.input_manager.current_scheme.value
        }
        
        # Merge performance stats
        performance_stats = base_perf.copy()
        performance_stats.update(phase3_perf)
        
        return performance_stats


# Test the Phase 3 integration
if __name__ == "__main__":
    print("🧪 Testing Enhanced Integration Phase 3...")
    
    # Create enhanced integration
    integration = EnhancedIntegrationPhase3()
    
    # Test different control schemes
    print("Testing control schemes:")
    integration.set_control_scheme(ControlScheme.KEYBOARD_MOUSE)
    integration.set_control_scheme(ControlScheme.GAMEPAD_CLASSIC)
    
    # Test traffic density
    print("Testing traffic density:")
    integration.set_traffic_density(TrafficDensity.HEAVY)
    integration.set_traffic_density(TrafficDensity.LIGHT)
    
    # Test audio volume
    print("Testing audio volume:")
    integration.set_audio_volume("master", 0.8)
    integration.set_audio_volume("sfx", 0.9)
    integration.set_audio_volume("music", 0.7)
    
    # Test audio events
    print("Testing audio events:")
    gunshot_id = integration.create_audio_event(
        AudioType.WEAPON_GUNSHOT, (400, 300), 0.8, "high"
    )
    explosion_id = integration.create_audio_event(
        AudioType.WEAPON_EXPLOSION, (600, 500), 1.0, "critical"
    )
    
    # Run simulation
    print("Running integrated simulation...")
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update integration
        integration.update(dt)
        
        if frame % 60 == 0:  # Print every second
            perf_stats = integration.get_performance_statistics()
            print(f"  Frame {frame}: FPS = {perf_stats.get('fps', 0):.1f}, "
                  f"Vehicles = {perf_stats.get('vehicles', 0)}, "
                  f"Traffic = {perf_stats.get('traffic_vehicles', 0)}, "
                  f"Audio = {perf_stats.get('audio_sources', 0)}")
    
    # Get comprehensive statistics
    print("\n📊 Comprehensive Statistics:")
    comprehensive_stats = integration.get_comprehensive_statistics()
    
    for category, stats in comprehensive_stats.items():
        print(f"\n{category.upper()}:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
    
    print("✅ Enhanced Integration Phase 3 test completed")