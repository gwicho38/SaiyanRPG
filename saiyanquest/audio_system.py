#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Audio System with Spatial Audio Support

import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    PYGAME_AUDIO_AVAILABLE = True
except ImportError:
    PYGAME_AUDIO_AVAILABLE = False
    print("Warning: pygame audio not available, using mock audio system")


class AudioType(Enum):
    """Types of audio sources"""
    AMBIENT = "ambient"
    VEHICLE_ENGINE = "vehicle_engine"
    VEHICLE_BRAKE = "vehicle_brake"
    VEHICLE_HORN = "vehicle_horn"
    WEAPON_GUNSHOT = "weapon_gunshot"
    WEAPON_EXPLOSION = "weapon_explosion"
    CHARACTER_FOOTSTEP = "character_footstep"
    CHARACTER_VOICE = "character_voice"
    ENVIRONMENTAL = "environmental"
    UI_SOUND = "ui_sound"
    MUSIC = "music"


class AudioPriority(Enum):
    """Audio priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AudioSource:
    """Audio source with spatial properties"""
    source_id: int
    audio_type: AudioType
    position: Tuple[float, float]
    volume: float  # 0.0 to 1.0
    pitch: float  # 0.5 to 2.0
    loop: bool
    priority: AudioPriority
    max_distance: float
    rolloff_factor: float
    is_3d: bool
    is_playing: bool = False
    start_time: float = 0.0
    duration: float = 0.0


@dataclass
class AudioListener:
    """Audio listener (usually the player)"""
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    orientation: Tuple[float, float]  # Forward direction vector


class SpatialAudioSystem:
    """Spatial audio system with 3D positioning"""
    
    def __init__(self):
        self.audio_sources: Dict[int, AudioSource] = {}
        self.next_source_id = 1
        
        # Audio listener (player)
        self.listener = AudioListener(
            position=(0.0, 0.0),
            velocity=(0.0, 0.0),
            orientation=(1.0, 0.0)
        )
        
        # Audio settings
        self.master_volume = 1.0
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        self.ambient_volume = 0.4
        
        # Distance attenuation
        self.reference_distance = 50.0
        self.max_distance = 200.0
        
        # Audio cache
        self.audio_cache: Dict[str, Any] = {}
        
        # Initialize audio system
        self._initialize_audio()
        
        print("🔊 SpatialAudioSystem initialized")
    
    def _initialize_audio(self):
        """Initialize the audio system"""
        if PYGAME_AUDIO_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ Pygame audio initialized")
            except Exception as e:
                print(f"❌ Failed to initialize pygame audio: {e}")
                # Note: Can't modify global here, but that's okay for this implementation
        
        if not PYGAME_AUDIO_AVAILABLE:
            print("⚠️ Using mock audio system")
    
    def create_audio_source(self, audio_type: AudioType, position: Tuple[float, float],
                          volume: float = 1.0, pitch: float = 1.0, loop: bool = False,
                          priority: AudioPriority = AudioPriority.NORMAL,
                          max_distance: float = 100.0, is_3d: bool = True) -> int:
        """Create a new audio source"""
        source_id = self.next_source_id
        self.next_source_id += 1
        
        audio_source = AudioSource(
            source_id=source_id,
            audio_type=audio_type,
            position=position,
            volume=volume,
            pitch=pitch,
            loop=loop,
            priority=priority,
            max_distance=max_distance,
            rolloff_factor=1.0,
            is_3d=is_3d
        )
        
        self.audio_sources[source_id] = audio_source
        print(f"🔊 Created audio source {source_id} ({audio_type.value}) at {position}")
        return source_id
    
    def play_audio(self, source_id: int, sound_name: str = None) -> bool:
        """Play audio from a source"""
        if source_id not in self.audio_sources:
            return False
        
        audio_source = self.audio_sources[source_id]
        
        # Calculate spatial volume
        spatial_volume = self._calculate_spatial_volume(audio_source)
        
        if spatial_volume <= 0.01:  # Too quiet to hear
            return False
        
        # Apply volume settings
        final_volume = spatial_volume * self.master_volume
        
        if audio_source.audio_type == AudioType.MUSIC:
            final_volume *= self.music_volume
        elif audio_source.audio_type == AudioType.AMBIENT:
            final_volume *= self.ambient_volume
        else:
            final_volume *= self.sfx_volume
        
        # Play audio (mock implementation)
        audio_source.is_playing = True
        audio_source.start_time = time.time()
        
        # In a real implementation, this would play actual audio
        print(f"🔊 Playing {audio_source.audio_type.value} at volume {final_volume:.2f}")
        
        return True
    
    def stop_audio(self, source_id: int) -> bool:
        """Stop audio from a source"""
        if source_id not in self.audio_sources:
            return False
        
        audio_source = self.audio_sources[source_id]
        audio_source.is_playing = False
        
        print(f"🔊 Stopped audio source {source_id}")
        return True
    
    def update_audio_source(self, source_id: int, position: Tuple[float, float] = None,
                           volume: float = None, pitch: float = None) -> bool:
        """Update audio source properties"""
        if source_id not in self.audio_sources:
            return False
        
        audio_source = self.audio_sources[source_id]
        
        if position is not None:
            audio_source.position = position
        
        if volume is not None:
            audio_source.volume = max(0.0, min(1.0, volume))
        
        if pitch is not None:
            audio_source.pitch = max(0.5, min(2.0, pitch))
        
        return True
    
    def set_listener_position(self, position: Tuple[float, float], 
                             velocity: Tuple[float, float] = (0.0, 0.0),
                             orientation: Tuple[float, float] = (1.0, 0.0)):
        """Set the audio listener position (usually the player)"""
        self.listener.position = position
        self.listener.velocity = velocity
        self.listener.orientation = orientation
    
    def _calculate_spatial_volume(self, audio_source: AudioSource) -> float:
        """Calculate volume based on spatial positioning"""
        if not audio_source.is_3d:
            return audio_source.volume
        
        # Calculate distance
        dx = audio_source.position[0] - self.listener.position[0]
        dy = audio_source.position[1] - self.listener.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Distance attenuation
        if distance >= audio_source.max_distance:
            return 0.0
        
        # Linear rolloff
        volume_factor = 1.0 - (distance / audio_source.max_distance)
        volume_factor = max(0.0, min(1.0, volume_factor))
        
        # Apply rolloff factor
        volume_factor = volume_factor ** audio_source.rolloff_factor
        
        return audio_source.volume * volume_factor
    
    def update(self, dt: float) -> None:
        """Update audio system"""
        # Update playing audio sources
        current_time = time.time()
        
        for audio_source in self.audio_sources.values():
            if audio_source.is_playing:
                # Check if audio should stop (for non-looping sounds)
                if not audio_source.loop and audio_source.duration > 0:
                    if current_time - audio_source.start_time >= audio_source.duration:
                        audio_source.is_playing = False
    
    def remove_audio_source(self, source_id: int) -> bool:
        """Remove an audio source"""
        if source_id in self.audio_sources:
            self.stop_audio(source_id)
            del self.audio_sources[source_id]
            print(f"🔊 Removed audio source {source_id}")
            return True
        return False
    
    def set_master_volume(self, volume: float):
        """Set master volume"""
        self.master_volume = max(0.0, min(1.0, volume))
        print(f"🔊 Master volume set to {self.master_volume:.2f}")
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"🔊 SFX volume set to {self.sfx_volume:.2f}")
    
    def set_music_volume(self, volume: float):
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))
        print(f"🔊 Music volume set to {self.music_volume:.2f}")
    
    def get_audio_statistics(self) -> Dict[str, Any]:
        """Get audio system statistics"""
        playing_count = sum(1 for source in self.audio_sources.values() if source.is_playing)
        
        type_counts = {}
        for source in self.audio_sources.values():
            audio_type = source.audio_type.value
            type_counts[audio_type] = type_counts.get(audio_type, 0) + 1
        
        return {
            'total_sources': len(self.audio_sources),
            'playing_sources': playing_count,
            'master_volume': self.master_volume,
            'sfx_volume': self.sfx_volume,
            'music_volume': self.music_volume,
            'ambient_volume': self.ambient_volume,
            'listener_position': self.listener.position,
            'audio_types': type_counts
        }


class VehicleAudioSystem:
    """Specialized audio system for vehicles"""
    
    def __init__(self, spatial_audio: SpatialAudioSystem):
        self.spatial_audio = spatial_audio
        self.vehicle_audio_sources: Dict[int, Dict[str, int]] = {}  # vehicle_id -> {engine, brake, horn}
        
        print("🚗 VehicleAudioSystem initialized")
    
    def create_vehicle_audio(self, vehicle_id: int, position: Tuple[float, float]) -> None:
        """Create audio sources for a vehicle"""
        # Engine sound
        engine_source = self.spatial_audio.create_audio_source(
            AudioType.VEHICLE_ENGINE,
            position,
            volume=0.6,
            loop=True,
            priority=AudioPriority.HIGH,
            max_distance=150.0
        )
        
        # Brake sound
        brake_source = self.spatial_audio.create_audio_source(
            AudioType.VEHICLE_BRAKE,
            position,
            volume=0.4,
            loop=False,
            priority=AudioPriority.NORMAL,
            max_distance=100.0
        )
        
        # Horn sound
        horn_source = self.spatial_audio.create_audio_source(
            AudioType.VEHICLE_HORN,
            position,
            volume=0.8,
            loop=False,
            priority=AudioPriority.HIGH,
            max_distance=200.0
        )
        
        self.vehicle_audio_sources[vehicle_id] = {
            'engine': engine_source,
            'brake': brake_source,
            'horn': horn_source
        }
        
        # Start engine sound
        self.spatial_audio.play_audio(engine_source)
        
        print(f"🚗 Created audio for vehicle {vehicle_id}")
    
    def update_vehicle_audio(self, vehicle_id: int, position: Tuple[float, float], 
                           speed: float, throttle: float, brake: float, horn: bool) -> None:
        """Update vehicle audio based on current state"""
        if vehicle_id not in self.vehicle_audio_sources:
            return
        
        audio_sources = self.vehicle_audio_sources[vehicle_id]
        
        # Update engine sound
        engine_source = audio_sources['engine']
        
        # Engine pitch based on speed
        engine_pitch = 0.8 + (speed / 50.0) * 0.4  # 0.8 to 1.2
        engine_volume = 0.3 + throttle * 0.4  # 0.3 to 0.7
        
        self.spatial_audio.update_audio_source(
            engine_source, position, engine_volume, engine_pitch
        )
        
        # Brake sound
        if brake > 0.1:
            brake_source = audio_sources['brake']
            brake_volume = brake * 0.5
            self.spatial_audio.update_audio_source(brake_source, position, brake_volume)
            
            if not self.spatial_audio.audio_sources[brake_source].is_playing:
                self.spatial_audio.play_audio(brake_source)
        else:
            brake_source = audio_sources['brake']
            self.spatial_audio.stop_audio(brake_source)
        
        # Horn sound
        if horn:
            horn_source = audio_sources['horn']
            if not self.spatial_audio.audio_sources[horn_source].is_playing:
                self.spatial_audio.play_audio(horn_source)
    
    def remove_vehicle_audio(self, vehicle_id: int) -> None:
        """Remove audio sources for a vehicle"""
        if vehicle_id in self.vehicle_audio_sources:
            audio_sources = self.vehicle_audio_sources[vehicle_id]
            
            for source_id in audio_sources.values():
                self.spatial_audio.remove_audio_source(source_id)
            
            del self.vehicle_audio_sources[vehicle_id]
            print(f"🚗 Removed audio for vehicle {vehicle_id}")


class EnvironmentalAudioSystem:
    """Environmental audio system for ambient sounds"""
    
    def __init__(self, spatial_audio: SpatialAudioSystem):
        self.spatial_audio = spatial_audio
        self.ambient_sources: Dict[str, int] = {}
        
        # Create ambient audio sources
        self._create_ambient_sources()
        
        print("🌍 EnvironmentalAudioSystem initialized")
    
    def _create_ambient_sources(self):
        """Create ambient audio sources"""
        # City ambient
        city_ambient = self.spatial_audio.create_audio_source(
            AudioType.AMBIENT,
            (500, 500),  # Center of world
            volume=0.3,
            loop=True,
            priority=AudioPriority.LOW,
            max_distance=500.0,
            is_3d=False  # Global ambient
        )
        self.ambient_sources['city'] = city_ambient
        
        # Wind ambient
        wind_ambient = self.spatial_audio.create_audio_source(
            AudioType.AMBIENT,
            (0, 0),
            volume=0.2,
            loop=True,
            priority=AudioPriority.LOW,
            max_distance=300.0,
            is_3d=False
        )
        self.ambient_sources['wind'] = wind_ambient
        
        # Start ambient sounds
        self.spatial_audio.play_audio(city_ambient)
        self.spatial_audio.play_audio(wind_ambient)
    
    def update_environmental_audio(self, weather: str, time_of_day: float) -> None:
        """Update environmental audio based on conditions"""
        # Adjust volume based on time of day
        if 6.0 <= time_of_day <= 18.0:  # Daytime
            day_factor = 1.0
        else:  # Nighttime
            day_factor = 0.6
        
        # Adjust based on weather
        if weather == "rainy":
            weather_factor = 1.2
        elif weather == "windy":
            weather_factor = 1.1
        else:
            weather_factor = 1.0
        
        # Update ambient volumes
        for source_name, source_id in self.ambient_sources.items():
            base_volume = 0.3 if source_name == 'city' else 0.2
            new_volume = base_volume * day_factor * weather_factor
            
            self.spatial_audio.update_audio_source(source_id, volume=new_volume)


# Test the audio system
if __name__ == "__main__":
    print("🧪 Testing Audio System...")
    
    # Create audio system
    spatial_audio = SpatialAudioSystem()
    vehicle_audio = VehicleAudioSystem(spatial_audio)
    environmental_audio = EnvironmentalAudioSystem(spatial_audio)
    
    # Test vehicle audio
    vehicle_id = 1
    vehicle_audio.create_vehicle_audio(vehicle_id, (100, 100))
    
    # Simulate vehicle movement
    for frame in range(180):  # 3 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Simulate vehicle movement
        speed = 10.0 + math.sin(frame * 0.1) * 5.0
        throttle = 0.5 + math.sin(frame * 0.05) * 0.3
        brake = 0.0
        horn = frame % 120 == 0  # Honk every 2 seconds
        
        position = (100 + frame * 0.5, 100 + math.sin(frame * 0.02) * 10)
        
        # Update vehicle audio
        vehicle_audio.update_vehicle_audio(vehicle_id, position, speed, throttle, brake, horn)
        
        # Update listener position
        spatial_audio.set_listener_position((100 + frame * 0.3, 100))
        
        # Update audio system
        spatial_audio.update(dt)
        
        if frame % 60 == 0:  # Print every second
            stats = spatial_audio.get_audio_statistics()
            print(f"  Frame {frame}: Sources = {stats['total_sources']}, "
                  f"Playing = {stats['playing_sources']}")
    
    # Clean up
    vehicle_audio.remove_vehicle_audio(vehicle_id)
    
    print("✅ Audio System test completed")