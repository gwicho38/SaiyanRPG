#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced World Renderer - Integrates pixel art maps with GTA world

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .pixel_art_map_system import get_pixel_map_system, PixelArtMapSystem
from .gba_asset_generator import get_asset_generator, GBAAssetGenerator, AssetType
from .gta_world_streamer import GTAWorldStreamer

@dataclass
class RenderLayer:
    """Represents a rendering layer with priority and properties"""
    name: str
    priority: int  # Lower numbers render first (behind)
    visible: bool = True
    opacity: float = 1.0
    parallax_x: float = 1.0
    parallax_y: float = 1.0

class EnhancedWorldRenderer:
    """Enhanced world renderer combining pixel art maps with GTA systems"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Core systems
        self.pixel_map_system = get_pixel_map_system()
        self.asset_generator = get_asset_generator()
        self.world_streamer = GTAWorldStreamer(screen_width, screen_height)
        
        # Rendering layers
        self.render_layers = {
            'background': RenderLayer('background', 0),
            'terrain': RenderLayer('terrain', 1),
            'buildings': RenderLayer('buildings', 2),
            'vehicles': RenderLayer('vehicles', 3),
            'characters': RenderLayer('characters', 4),
            'effects': RenderLayer('effects', 5),
            'ui': RenderLayer('ui', 6),
            'debug': RenderLayer('debug', 7)
        }
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0
        
        # Rendering optimization
        self.render_cache = {}
        self.dirty_regions = set()
        
        # World state
        self.current_world_type = "mixed"  # city, nature, mixed
        self.world_loaded = False
        
        # Initialize
        self._generate_assets()
        self._create_world()
    
    def _generate_assets(self):
        """Generate GBA-style assets"""
        print("🎨 Generating GBA-style assets...")
        self.asset_generator.generate_all_assets()
        
        # Save assets for future use
        self.asset_generator.save_assets("gba_generated_assets")
    
    def _create_world(self):
        """Create the game world"""
        print("🌍 Creating enhanced pixel art world...")
        
        # Create a large procedural map
        map_width = 200  # 200x150 tiles = 3200x2400 pixels at 16px tiles
        map_height = 150
        
        success = self.pixel_map_system.create_procedural_map(
            map_width, map_height, self.current_world_type
        )
        
        if success:
            self.world_loaded = True
            print(f"   ✓ Created {self.current_world_type} world: {map_width}x{map_height}")
        else:
            print("   ❌ Failed to create world")
    
    def update_camera(self, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Update camera position and zoom"""
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.camera_zoom = zoom
        
        # Update pixel map system camera
        self.pixel_map_system.update_camera(camera_x, camera_y)
        
        # Update world streamer camera
        self.world_streamer.update_camera(camera_x, camera_y)
    
    def update(self, dt: float):
        """Update the world renderer"""
        # Update pixel map animations
        self.pixel_map_system.update_animations(dt)
        
        # Update world streamer
        # Note: world_streamer.update() would be called here if it had one
        
        # Clear dirty regions
        self.dirty_regions.clear()
    
    def render(self, surface: pygame.Surface):
        """Render the enhanced world"""
        if not self.world_loaded:
            # Render placeholder
            surface.fill((50, 100, 50))
            font = pygame.font.Font(None, 36)
            text = font.render("Loading World...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            surface.blit(text, text_rect)
            return
        
        # Render layers in priority order
        sorted_layers = sorted(self.render_layers.values(), key=lambda x: x.priority)
        
        for layer in sorted_layers:
            if layer.visible:
                self._render_layer(surface, layer)
    
    def _render_layer(self, surface: pygame.Surface, layer: RenderLayer):
        """Render a specific layer"""
        if layer.name == 'background':
            self._render_background(surface)
        elif layer.name == 'terrain':
            self._render_terrain(surface)
        elif layer.name == 'buildings':
            self._render_buildings(surface)
        elif layer.name == 'vehicles':
            self._render_vehicles(surface)
        elif layer.name == 'characters':
            self._render_characters(surface)
        elif layer.name == 'effects':
            self._render_effects(surface)
        elif layer.name == 'ui':
            self._render_ui(surface)
        elif layer.name == 'debug':
            self._render_debug(surface)
    
    def _render_background(self, surface: pygame.Surface):
        """Render background layer"""
        # Use pixel map system for background
        self.pixel_map_system.render(surface)
    
    def _render_terrain(self, surface: pygame.Surface):
        """Render terrain features"""
        # Additional terrain rendering can be added here
        pass
    
    def _render_buildings(self, surface: pygame.Surface):
        """Render buildings using GBA assets"""
        building_assets = self.asset_generator.get_assets_by_type(AssetType.BUILDING)
        
        # Place buildings procedurally
        for i in range(20):  # 20 buildings
            if not building_assets:
                break
                
            building = random.choice(building_assets)
            sprite = building.sprites.get('default')
            
            if sprite:
                # Calculate position (scattered around the world)
                world_x = random.randint(100, 3000)
                world_y = random.randint(100, 2000)
                
                # Convert to screen coordinates
                screen_x = world_x - self.camera_x
                screen_y = world_y - self.camera_y
                
                # Only render if on screen
                if (-100 <= screen_x <= self.screen_width + 100 and
                    -100 <= screen_y <= self.screen_height + 100):
                    
                    # Scale sprite
                    scaled_sprite = pygame.transform.scale(sprite, 
                        (sprite.get_width() * self.camera_zoom,
                         sprite.get_height() * self.camera_zoom))
                    
                    surface.blit(scaled_sprite, (int(screen_x), int(screen_y)))
    
    def _render_vehicles(self, surface: pygame.Surface):
        """Render vehicles using GBA assets"""
        vehicle_assets = self.asset_generator.get_assets_by_type(AssetType.VEHICLE)
        
        # Place vehicles procedurally
        for i in range(15):  # 15 vehicles
            if not vehicle_assets:
                break
                
            vehicle = random.choice(vehicle_assets)
            direction = random.choice(['north', 'south', 'east', 'west'])
            sprite = vehicle.sprites.get(direction)
            
            if sprite:
                # Calculate position (on roads)
                world_x = random.randint(200, 2800)
                world_y = random.randint(200, 1800)
                
                # Convert to screen coordinates
                screen_x = world_x - self.camera_x
                screen_y = world_y - self.camera_y
                
                # Only render if on screen
                if (-100 <= screen_x <= self.screen_width + 100 and
                    -100 <= screen_y <= self.screen_height + 100):
                    
                    # Scale sprite
                    scaled_sprite = pygame.transform.scale(sprite,
                        (sprite.get_width() * self.camera_zoom,
                         sprite.get_height() * self.camera_zoom))
                    
                    surface.blit(scaled_sprite, (int(screen_x), int(screen_y)))
    
    def _render_characters(self, surface: pygame.Surface):
        """Render characters using GBA assets"""
        character_assets = self.asset_generator.get_assets_by_type(AssetType.CHARACTER)
        
        # Place characters procedurally
        for i in range(25):  # 25 characters
            if not character_assets:
                break
                
            character = random.choice(character_assets)
            direction = random.choice(['north', 'south', 'east', 'west'])
            sprite = character.sprites.get(direction)
            
            if sprite:
                # Calculate position (scattered around)
                world_x = random.randint(50, 3100)
                world_y = random.randint(50, 1900)
                
                # Convert to screen coordinates
                screen_x = world_x - self.camera_x
                screen_y = world_y - self.camera_y
                
                # Only render if on screen
                if (-50 <= screen_x <= self.screen_width + 50 and
                    -50 <= screen_y <= self.screen_height + 50):
                    
                    # Scale sprite
                    scaled_sprite = pygame.transform.scale(sprite,
                        (sprite.get_width() * self.camera_zoom,
                         sprite.get_height() * self.camera_zoom))
                    
                    surface.blit(scaled_sprite, (int(screen_x), int(screen_y)))
    
    def _render_effects(self, surface: pygame.Surface):
        """Render effects using GBA assets"""
        effect_assets = self.asset_generator.get_assets_by_type(AssetType.EFFECT)
        
        # Place some random effects
        for i in range(5):  # 5 effects
            if not effect_assets:
                break
                
            effect = random.choice(effect_assets)
            frames = effect.sprites.get('frames', [])
            
            if frames:
                # Use first frame for now (animation would be handled elsewhere)
                sprite = frames[0]
                
                # Calculate position
                world_x = random.randint(100, 2900)
                world_y = random.randint(100, 1800)
                
                # Convert to screen coordinates
                screen_x = world_x - self.camera_x
                screen_y = world_y - self.camera_y
                
                # Only render if on screen
                if (-50 <= screen_x <= self.screen_width + 50 and
                    -50 <= screen_y <= self.screen_height + 50):
                    
                    # Scale sprite
                    scaled_sprite = pygame.transform.scale(sprite,
                        (sprite.get_width() * self.camera_zoom,
                         sprite.get_height() * self.camera_zoom))
                    
                    surface.blit(scaled_sprite, (int(screen_x), int(screen_y)))
    
    def _render_ui(self, surface: pygame.Surface):
        """Render UI elements"""
        # UI rendering would be handled by the UI system
        pass
    
    def _render_debug(self, surface: pygame.Surface):
        """Render debug information"""
        # Debug rendering
        font = pygame.font.Font(None, 24)
        
        # Camera info
        camera_text = f"Camera: ({self.camera_x:.1f}, {self.camera_y:.1f}) Zoom: {self.camera_zoom:.2f}"
        text_surface = font.render(camera_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 10))
        
        # World info
        world_info = self.pixel_map_system.get_map_info()
        world_text = f"World: {world_info['map_size'][0]}x{world_info['map_size'][1]} tiles"
        text_surface = font.render(world_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 35))
        
        # Asset info
        asset_count = len(self.asset_generator.generated_assets)
        asset_text = f"Assets: {asset_count} generated"
        text_surface = font.render(asset_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 60))
        
        # FPS (placeholder)
        fps_text = "FPS: 60"
        text_surface = font.render(fps_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 85))
    
    def check_collision(self, x: float, y: float) -> bool:
        """Check collision at world coordinates"""
        return self.pixel_map_system.get_collision_at(x, y)
    
    def get_tile_at(self, x: float, y: float):
        """Get tile information at world coordinates"""
        return self.pixel_map_system.get_tile_at(x, y)
    
    def set_layer_visibility(self, layer_name: str, visible: bool):
        """Set layer visibility"""
        if layer_name in self.render_layers:
            self.render_layers[layer_name].visible = visible
    
    def set_layer_opacity(self, layer_name: str, opacity: float):
        """Set layer opacity"""
        if layer_name in self.render_layers:
            self.render_layers[layer_name].opacity = max(0.0, min(1.0, opacity))
    
    def get_world_info(self) -> Dict[str, Any]:
        """Get comprehensive world information"""
        pixel_info = self.pixel_map_system.get_map_info()
        asset_info = {
            'total_assets': len(self.asset_generator.generated_assets),
            'vehicles': len(self.asset_generator.get_assets_by_type(AssetType.VEHICLE)),
            'characters': len(self.asset_generator.get_assets_by_type(AssetType.CHARACTER)),
            'buildings': len(self.asset_generator.get_assets_by_type(AssetType.BUILDING)),
            'effects': len(self.asset_generator.get_assets_by_type(AssetType.EFFECT))
        }
        
        return {
            'world_loaded': self.world_loaded,
            'world_type': self.current_world_type,
            'camera': (self.camera_x, self.camera_y, self.camera_zoom),
            'pixel_map': pixel_info,
            'assets': asset_info,
            'layers': {name: {'visible': layer.visible, 'opacity': layer.opacity} 
                      for name, layer in self.render_layers.items()}
        }
    
    def create_new_world(self, world_type: str, width: int = 200, height: int = 150):
        """Create a new world of the specified type"""
        print(f"🌍 Creating new {world_type} world...")
        
        self.current_world_type = world_type
        success = self.pixel_map_system.create_procedural_map(width, height, world_type)
        
        if success:
            self.world_loaded = True
            print(f"   ✓ Created {world_type} world: {width}x{height}")
        else:
            print(f"   ❌ Failed to create {world_type} world")
        
        return success

# Global enhanced world renderer instance
_enhanced_renderer = None

def get_enhanced_renderer() -> EnhancedWorldRenderer:
    """Get the global enhanced world renderer instance"""
    global _enhanced_renderer
    if _enhanced_renderer is None:
        _enhanced_renderer = EnhancedWorldRenderer()
    return _enhanced_renderer