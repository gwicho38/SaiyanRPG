#!/usr/bin/env python3
"""
Advanced Vehicle Visual Effects and Animations
Implements particle systems, lighting effects, and visual feedback for vehicles.
Based on Carnage3D visual effects systems.
"""

import pygame
import math
import random
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ParticleType(Enum):
    """Types of particles for vehicle effects"""
    EXHAUST_SMOKE = "exhaust_smoke"
    TIRE_SMOKE = "tire_smoke"
    ENGINE_STEAM = "engine_steam"
    SPARKS = "sparks"
    FIRE = "fire"
    EXPLOSION = "explosion"
    DUST = "dust"
    WATER_SPRAY = "water_spray"
    BRAKE_DUST = "brake_dust"


class EffectIntensity(Enum):
    """Intensity levels for effects"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


@dataclass
class Particle:
    """Individual particle for effects"""
    x: float
    y: float
    vx: float  # Velocity X
    vy: float  # Velocity Y
    life: float  # Current life (0.0 to 1.0)
    max_life: float  # Maximum life in seconds
    size: float
    color: Tuple[int, int, int, int]  # RGBA
    particle_type: ParticleType
    rotation: float = 0.0
    rotation_speed: float = 0.0
    gravity_affected: bool = True
    fade_alpha: bool = True
    
    def update(self, dt: float) -> bool:
        """Update particle. Returns False if particle should be removed."""
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity if affected
        if self.gravity_affected:
            self.vy += 200.0 * dt  # Gravity acceleration
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update life
        self.life -= dt / self.max_life
        
        # Update alpha based on life if fade enabled
        if self.fade_alpha and self.life < 1.0:
            alpha = max(0, int(255 * self.life))
            self.color = (self.color[0], self.color[1], self.color[2], alpha)
        
        # Apply drag based on particle type
        drag_factor = 0.98
        if self.particle_type == ParticleType.TIRE_SMOKE:
            drag_factor = 0.95
        elif self.particle_type == ParticleType.EXHAUST_SMOKE:
            drag_factor = 0.97
        
        self.vx *= drag_factor
        self.vy *= drag_factor
        
        return self.life > 0.0


class ParticleSystem:
    """Manages particles for vehicle effects"""
    
    def __init__(self, max_particles: int = 1000):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
        
    def add_particle(self, particle: Particle) -> None:
        """Add a particle to the system"""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
    
    def emit_particles(self, particle_type: ParticleType, x: float, y: float, 
                      count: int, intensity: EffectIntensity = EffectIntensity.MEDIUM,
                      direction: float = 0.0, spread: float = 45.0) -> None:
        """Emit multiple particles of a specific type"""
        base_config = self._get_particle_config(particle_type, intensity)
        
        for _ in range(count):
            # Calculate velocity with spread
            angle = direction + random.uniform(-spread/2, spread/2)
            speed = random.uniform(base_config['min_speed'], base_config['max_speed'])
            
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            
            # Add some randomness to position
            px = x + random.uniform(-5, 5)
            py = y + random.uniform(-5, 5)
            
            particle = Particle(
                x=px, y=py, vx=vx, vy=vy,
                life=1.0,
                max_life=random.uniform(base_config['min_life'], base_config['max_life']),
                size=random.uniform(base_config['min_size'], base_config['max_size']),
                color=self._random_color(base_config['base_color'], base_config['color_variation']),
                particle_type=particle_type,
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-90, 90),
                gravity_affected=base_config['gravity_affected'],
                fade_alpha=base_config['fade_alpha']
            )
            
            self.add_particle(particle)
    
    def _get_particle_config(self, particle_type: ParticleType, intensity: EffectIntensity) -> Dict:
        """Get configuration for particle type"""
        intensity_multiplier = intensity.value / 2.0
        
        configs = {
            ParticleType.EXHAUST_SMOKE: {
                'base_color': (80, 80, 80, 180),
                'color_variation': 30,
                'min_speed': 20 * intensity_multiplier,
                'max_speed': 50 * intensity_multiplier,
                'min_life': 1.0,
                'max_life': 3.0,
                'min_size': 8,
                'max_size': 20,
                'gravity_affected': False,
                'fade_alpha': True
            },
            ParticleType.TIRE_SMOKE: {
                'base_color': (200, 200, 200, 200),
                'color_variation': 20,
                'min_speed': 10 * intensity_multiplier,
                'max_speed': 30 * intensity_multiplier,
                'min_life': 0.5,
                'max_life': 2.0,
                'min_size': 5,
                'max_size': 15,
                'gravity_affected': False,
                'fade_alpha': True
            },
            ParticleType.ENGINE_STEAM: {
                'base_color': (255, 255, 255, 150),
                'color_variation': 10,
                'min_speed': 15 * intensity_multiplier,
                'max_speed': 40 * intensity_multiplier,
                'min_life': 2.0,
                'max_life': 4.0,
                'min_size': 10,
                'max_size': 25,
                'gravity_affected': False,
                'fade_alpha': True
            },
            ParticleType.SPARKS: {
                'base_color': (255, 200, 100, 255),
                'color_variation': 50,
                'min_speed': 50 * intensity_multiplier,
                'max_speed': 120 * intensity_multiplier,
                'min_life': 0.2,
                'max_life': 0.8,
                'min_size': 2,
                'max_size': 4,
                'gravity_affected': True,
                'fade_alpha': True
            },
            ParticleType.FIRE: {
                'base_color': (255, 100, 0, 200),
                'color_variation': 100,
                'min_speed': 10 * intensity_multiplier,
                'max_speed': 30 * intensity_multiplier,
                'min_life': 0.3,
                'max_life': 1.5,
                'min_size': 8,
                'max_size': 18,
                'gravity_affected': False,
                'fade_alpha': True
            },
            ParticleType.DUST: {
                'base_color': (150, 120, 80, 120),
                'color_variation': 40,
                'min_speed': 5 * intensity_multiplier,
                'max_speed': 20 * intensity_multiplier,
                'min_life': 1.0,
                'max_life': 3.0,
                'min_size': 3,
                'max_size': 8,
                'gravity_affected': True,
                'fade_alpha': True
            },
            ParticleType.WATER_SPRAY: {
                'base_color': (100, 150, 255, 180),
                'color_variation': 30,
                'min_speed': 30 * intensity_multiplier,
                'max_speed': 80 * intensity_multiplier,
                'min_life': 0.5,
                'max_life': 1.5,
                'min_size': 2,
                'max_size': 6,
                'gravity_affected': True,
                'fade_alpha': True
            }
        }
        
        return configs.get(particle_type, configs[ParticleType.EXHAUST_SMOKE])
    
    def _random_color(self, base_color: Tuple[int, int, int, int], variation: int) -> Tuple[int, int, int, int]:
        """Generate a random color variation"""
        r = max(0, min(255, base_color[0] + random.randint(-variation, variation)))
        g = max(0, min(255, base_color[1] + random.randint(-variation, variation)))
        b = max(0, min(255, base_color[2] + random.randint(-variation, variation)))
        return (r, g, b, base_color[3])
    
    def update(self, dt: float) -> None:
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render all particles"""
        for particle in self.particles:
            # Calculate screen position
            screen_x = int(particle.x - camera_offset[0])
            screen_y = int(particle.y - camera_offset[1])
            
            # Skip particles outside screen bounds
            if (screen_x < -particle.size or screen_x > screen.get_width() + particle.size or
                screen_y < -particle.size or screen_y > screen.get_height() + particle.size):
                continue
            
            # Create surface for particle with alpha
            particle_surface = pygame.Surface((int(particle.size * 2), int(particle.size * 2)), pygame.SRCALPHA)
            
            # Draw particle based on type
            if particle.particle_type == ParticleType.SPARKS:
                # Draw sparks as small bright rectangles
                spark_rect = pygame.Rect(0, 0, max(2, int(particle.size)), max(1, int(particle.size/2)))
                pygame.draw.rect(particle_surface, particle.color[:3], spark_rect)
            elif particle.particle_type == ParticleType.FIRE:
                # Draw fire as circles with flickering
                flicker_size = particle.size * (0.8 + 0.4 * random.random())
                pygame.draw.circle(particle_surface, particle.color[:3], 
                                 (int(particle.size), int(particle.size)), int(flicker_size))
            else:
                # Draw most particles as circles
                pygame.draw.circle(particle_surface, particle.color[:3], 
                                 (int(particle.size), int(particle.size)), int(particle.size))
            
            # Apply alpha
            particle_surface.set_alpha(particle.color[3])
            
            # Blit to screen
            screen.blit(particle_surface, (screen_x - particle.size, screen_y - particle.size))
    
    def get_particle_count(self) -> int:
        """Get current particle count"""
        return len(self.particles)
    
    def clear_particles(self) -> None:
        """Clear all particles"""
        self.particles.clear()


class VehicleLightingSystem:
    """Manages vehicle lighting effects"""
    
    def __init__(self):
        self.headlight_beams: List[Dict] = []
        self.light_states = {}
        self.emergency_light_phase = 0.0
        
    def update(self, dt: float, electrical_status: Dict) -> None:
        """Update lighting effects"""
        self.emergency_light_phase += dt * 4.0  # 4Hz flashing
        
        # Update light states from electrical system
        self.light_states = electrical_status.get('active_components', [])
        
        # Update headlight beams
        self._update_headlight_beams(dt)
    
    def _update_headlight_beams(self, dt: float) -> None:
        """Update headlight beam effects"""
        # Headlight beams fade over time
        for beam in self.headlight_beams:
            beam['intensity'] *= 0.95  # Fade out
        
        # Remove faded beams
        self.headlight_beams = [b for b in self.headlight_beams if b['intensity'] > 0.1]
    
    def add_headlight_beam(self, x: float, y: float, angle: float, intensity: float = 1.0) -> None:
        """Add a headlight beam effect"""
        beam = {
            'x': x,
            'y': y, 
            'angle': angle,
            'intensity': intensity,
            'width': 60,  # degrees
            'length': 200,  # pixels
            'color': (255, 255, 200)
        }
        self.headlight_beams.append(beam)
    
    def render_lights(self, screen: pygame.Surface, vehicle_x: float, vehicle_y: float, 
                     vehicle_angle: float, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render vehicle lighting effects"""
        screen_x = int(vehicle_x - camera_offset[0])
        screen_y = int(vehicle_y - camera_offset[1])
        
        # Render headlight beams
        if 'headlights' in self.light_states:
            self._render_headlight_beams(screen, screen_x, screen_y, vehicle_angle)
        
        # Render brake lights
        if 'brake_lights' in self.light_states:
            self._render_brake_lights(screen, screen_x, screen_y, vehicle_angle)
        
        # Render emergency lights
        if 'emergency_lights' in self.light_states:
            self._render_emergency_lights(screen, screen_x, screen_y, vehicle_angle)
        
        # Render turn signals
        if 'turn_signals' in self.light_states:
            self._render_turn_signals(screen, screen_x, screen_y, vehicle_angle)
    
    def _render_headlight_beams(self, screen: pygame.Surface, x: int, y: int, angle: float) -> None:
        """Render headlight beam cones"""
        beam_length = 150
        beam_width = 40
        
        # Calculate headlight positions (front of vehicle)
        front_offset = 15
        side_offset = 8
        
        left_light_x = x + math.cos(math.radians(angle)) * front_offset - math.sin(math.radians(angle)) * side_offset
        left_light_y = y + math.sin(math.radians(angle)) * front_offset + math.cos(math.radians(angle)) * side_offset
        
        right_light_x = x + math.cos(math.radians(angle)) * front_offset + math.sin(math.radians(angle)) * side_offset
        right_light_y = y + math.sin(math.radians(angle)) * front_offset - math.cos(math.radians(angle)) * side_offset
        
        # Draw light cones
        for light_x, light_y in [(left_light_x, left_light_y), (right_light_x, right_light_y)]:
            # Create beam polygon
            beam_points = []
            beam_points.append((int(light_x), int(light_y)))
            
            for i in range(-beam_width//2, beam_width//2 + 1, 5):
                beam_angle = angle + i
                end_x = light_x + math.cos(math.radians(beam_angle)) * beam_length
                end_y = light_y + math.sin(math.radians(beam_angle)) * beam_length
                beam_points.append((int(end_x), int(end_y)))
            
            # Draw beam with transparency
            if len(beam_points) > 2:
                beam_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.polygon(beam_surface, (255, 255, 200, 50), beam_points)
                screen.blit(beam_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                
                # Draw bright center line
                end_x = light_x + math.cos(math.radians(angle)) * beam_length
                end_y = light_y + math.sin(math.radians(angle)) * beam_length
                pygame.draw.line(screen, (255, 255, 150), (int(light_x), int(light_y)), (int(end_x), int(end_y)), 2)
    
    def _render_brake_lights(self, screen: pygame.Surface, x: int, y: int, angle: float) -> None:
        """Render brake lights"""
        # Calculate rear light positions
        rear_offset = -15
        side_offset = 8
        
        left_light_x = x + math.cos(math.radians(angle)) * rear_offset - math.sin(math.radians(angle)) * side_offset
        left_light_y = y + math.sin(math.radians(angle)) * rear_offset + math.cos(math.radians(angle)) * side_offset
        
        right_light_x = x + math.cos(math.radians(angle)) * rear_offset + math.sin(math.radians(angle)) * side_offset
        right_light_y = y + math.sin(math.radians(angle)) * rear_offset - math.cos(math.radians(angle)) * side_offset
        
        # Draw brake lights as red circles
        pygame.draw.circle(screen, (255, 50, 50), (int(left_light_x), int(left_light_y)), 4)
        pygame.draw.circle(screen, (255, 50, 50), (int(right_light_x), int(right_light_y)), 4)
        
        # Add glow effect
        glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 0, 0, 30), (10, 10), 10)
        screen.blit(glow_surface, (int(left_light_x) - 10, int(left_light_y) - 10), special_flags=pygame.BLEND_ALPHA_SDL2)
        screen.blit(glow_surface, (int(right_light_x) - 10, int(right_light_y) - 10), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_emergency_lights(self, screen: pygame.Surface, x: int, y: int, angle: float) -> None:
        """Render flashing emergency lights"""
        # Alternate between red and blue
        flash_cycle = int(self.emergency_light_phase) % 2
        color = (255, 0, 0) if flash_cycle == 0 else (0, 0, 255)
        
        # Emergency lights on roof
        roof_y = y - 10
        
        if int(self.emergency_light_phase * 2) % 2:  # Flash at 2Hz
            # Left emergency light
            pygame.draw.circle(screen, color, (x - 8, int(roof_y)), 6)
            # Right emergency light  
            pygame.draw.circle(screen, (0, 0, 255) if flash_cycle == 0 else (255, 0, 0), (x + 8, int(roof_y)), 6)
            
            # Add bright flash effect
            flash_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*color, 100), (20, 20), 20)
            screen.blit(flash_surface, (x - 20, int(roof_y) - 20), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_turn_signals(self, screen: pygame.Surface, x: int, y: int, angle: float) -> None:
        """Render turn signal indicators"""
        if int(self.emergency_light_phase * 1.5) % 2:  # Flash at 1.5Hz
            # Front turn signals (orange)
            front_offset = 12
            side_offset = 12
            
            signal_x = x + math.cos(math.radians(angle)) * front_offset
            signal_y = y + math.sin(math.radians(angle)) * front_offset
            
            # Left signal
            left_x = signal_x - math.sin(math.radians(angle)) * side_offset
            left_y = signal_y + math.cos(math.radians(angle)) * side_offset
            pygame.draw.circle(screen, (255, 165, 0), (int(left_x), int(left_y)), 3)
            
            # Right signal
            right_x = signal_x + math.sin(math.radians(angle)) * side_offset
            right_y = signal_y - math.cos(math.radians(angle)) * side_offset
            pygame.draw.circle(screen, (255, 165, 0), (int(right_x), int(right_y)), 3)


class VehicleEffectsSystem:
    """Main system for managing all vehicle visual effects"""
    
    def __init__(self, max_particles: int = 1000):
        self.particle_system = ParticleSystem(max_particles)
        self.lighting_system = VehicleLightingSystem()
        self.damage_effects_timer = 0.0
        
    def update(self, dt: float, vehicle) -> None:
        """Update all effects systems"""
        # Update particle system
        self.particle_system.update(dt)
        
        # Update lighting system
        electrical_status = vehicle.get_electrical_status()
        self.lighting_system.update(dt, electrical_status)
        
        # Generate effects based on vehicle state
        self._generate_engine_effects(vehicle)
        self._generate_tire_effects(vehicle)
        self._generate_damage_effects(vehicle, dt)
        self._generate_environmental_effects(vehicle)
    
    def _generate_engine_effects(self, vehicle) -> None:
        """Generate engine-related effects"""
        if not vehicle.engine_on:
            return
        
        # Exhaust smoke based on throttle
        if vehicle.throttle > 0.1:
            intensity = EffectIntensity.LOW
            if vehicle.throttle > 0.5:
                intensity = EffectIntensity.MEDIUM
            if vehicle.throttle > 0.8:
                intensity = EffectIntensity.HIGH
            
            # Calculate exhaust position (rear of vehicle)
            exhaust_x = vehicle.x - math.cos(math.radians(vehicle.angle)) * 20
            exhaust_y = vehicle.y - math.sin(math.radians(vehicle.angle)) * 20
            
            # Emit exhaust particles
            particle_count = max(1, int(vehicle.throttle * 3))
            self.particle_system.emit_particles(
                ParticleType.EXHAUST_SMOKE, 
                exhaust_x, exhaust_y, 
                particle_count, intensity,
                direction=vehicle.angle + 180,  # Behind vehicle
                spread=30
            )
        
        # Engine overheating effects
        engine_temp = vehicle.get_engine_temperature()
        if engine_temp > 100:
            steam_intensity = EffectIntensity.LOW
            if engine_temp > 120:
                steam_intensity = EffectIntensity.HIGH
            
            # Steam from engine bay
            hood_x = vehicle.x + math.cos(math.radians(vehicle.angle)) * 10
            hood_y = vehicle.y + math.sin(math.radians(vehicle.angle)) * 10
            
            if random.random() < 0.3:  # 30% chance per frame
                self.particle_system.emit_particles(
                    ParticleType.ENGINE_STEAM,
                    hood_x, hood_y,
                    random.randint(1, 3), steam_intensity,
                    direction=vehicle.angle - 90,  # Upward
                    spread=45
                )
    
    def _generate_tire_effects(self, vehicle) -> None:
        """Generate tire-related effects"""
        # Tire smoke from skidding
        tire_stats = vehicle.get_tire_stats()
        skidding_wheels = vehicle.get_skidding_wheels()
        
        if skidding_wheels:
            for wheel in skidding_wheels:
                # Calculate wheel position
                wheel_x, wheel_y = self._get_wheel_position(vehicle, wheel)
                
                # Emit tire smoke
                smoke_intensity = EffectIntensity.MEDIUM
                if len(skidding_wheels) > 2:
                    smoke_intensity = EffectIntensity.HIGH
                
                self.particle_system.emit_particles(
                    ParticleType.TIRE_SMOKE,
                    wheel_x, wheel_y,
                    random.randint(2, 5), smoke_intensity,
                    direction=random.uniform(0, 360),
                    spread=90
                )
        
        # Brake dust when braking hard
        if vehicle.brake > 0.7:
            for wheel in ['front_left', 'front_right', 'rear_left', 'rear_right']:
                wheel_x, wheel_y = self._get_wheel_position(vehicle, wheel)
                
                if random.random() < 0.2:  # 20% chance
                    self.particle_system.emit_particles(
                        ParticleType.BRAKE_DUST,
                        wheel_x, wheel_y,
                        1, EffectIntensity.LOW,
                        direction=random.uniform(0, 360),
                        spread=180
                    )
    
    def _generate_damage_effects(self, vehicle, dt: float) -> None:
        """Generate damage-related effects"""
        self.damage_effects_timer += dt
        
        # Fire effects for burning vehicles
        if vehicle.is_burning:
            if self.damage_effects_timer > 0.1:  # Every 100ms
                # Fire from multiple points on vehicle
                fire_points = [
                    (vehicle.x + random.uniform(-15, 15), vehicle.y + random.uniform(-10, 10))
                ]
                
                for fx, fy in fire_points:
                    self.particle_system.emit_particles(
                        ParticleType.FIRE,
                        fx, fy,
                        random.randint(3, 8), EffectIntensity.HIGH,
                        direction=-90,  # Upward
                        spread=45
                    )
                self.damage_effects_timer = 0.0
        
        # Sparks from damaged vehicle scraping ground
        if vehicle.damage_level > 0.7 and vehicle.get_speed_kmh() > 20:
            if random.random() < vehicle.damage_level * 0.1:  # Damage-based probability
                spark_x = vehicle.x + random.uniform(-20, 20)
                spark_y = vehicle.y + random.uniform(-15, 15)
                
                self.particle_system.emit_particles(
                    ParticleType.SPARKS,
                    spark_x, spark_y,
                    random.randint(2, 6), EffectIntensity.MEDIUM,
                    direction=vehicle.angle + 180 + random.uniform(-30, 30),
                    spread=60
                )
    
    def _generate_environmental_effects(self, vehicle) -> None:
        """Generate environment-based effects"""
        speed_kmh = vehicle.get_speed_kmh()
        
        # Dust clouds when driving on dirt/off-road
        # (This would be enhanced with terrain detection)
        if speed_kmh > 30 and random.random() < 0.05:  # 5% chance when moving fast
            dust_x = vehicle.x - math.cos(math.radians(vehicle.angle)) * 25
            dust_y = vehicle.y - math.sin(math.radians(vehicle.angle)) * 25
            
            self.particle_system.emit_particles(
                ParticleType.DUST,
                dust_x, dust_y,
                random.randint(1, 3), EffectIntensity.LOW,
                direction=vehicle.angle + 180 + random.uniform(-45, 45),
                spread=60
            )
    
    def _get_wheel_position(self, vehicle, wheel: str) -> Tuple[float, float]:
        """Get the position of a specific wheel"""
        # Simplified wheel positions relative to vehicle center
        wheel_offsets = {
            'front_left': (-8, -12),
            'front_right': (8, -12),
            'rear_left': (-8, 12),
            'rear_right': (8, 12)
        }
        
        offset_x, offset_y = wheel_offsets.get(wheel, (0, 0))
        
        # Rotate offset based on vehicle angle
        cos_angle = math.cos(math.radians(vehicle.angle))
        sin_angle = math.sin(math.radians(vehicle.angle))
        
        rotated_x = offset_x * cos_angle - offset_y * sin_angle
        rotated_y = offset_x * sin_angle + offset_y * cos_angle
        
        return vehicle.x + rotated_x, vehicle.y + rotated_y
    
    def render(self, screen: pygame.Surface, vehicle, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render all vehicle effects"""
        # Render particle effects
        self.particle_system.render(screen, camera_offset)
        
        # Render lighting effects
        self.lighting_system.render_lights(
            screen, vehicle.x, vehicle.y, vehicle.angle, camera_offset
        )
    
    def get_effects_info(self) -> Dict:
        """Get information about active effects"""
        return {
            'particle_count': self.particle_system.get_particle_count(),
            'max_particles': self.particle_system.max_particles,
            'particle_usage': f"{self.particle_system.get_particle_count()}/{self.particle_system.max_particles}",
            'active_lights': len(self.lighting_system.light_states),
            'headlight_beams': len(self.lighting_system.headlight_beams)
        }
    
    def clear_effects(self) -> None:
        """Clear all active effects"""
        self.particle_system.clear_particles()
        self.lighting_system.headlight_beams.clear()