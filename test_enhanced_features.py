#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Comprehensive Test Script for Enhanced SaiyanQuest Features

import pygame
import time
import random
import math
from typing import Dict, Any

# Import our enhanced systems
from saiyanquest.enhanced_game_integration import EnhancedGameIntegration
from saiyanquest.physics_manager import PhysicsManager, CollisionCategory, PhysicsBodyType
from saiyanquest.vehicle_physics import VehiclePhysicsSystem, VehicleState
from saiyanquest.character_ai import CharacterAIManager, StimulusType, Stimulus
from saiyanquest.world_3d_system import World3DSystem, BlockType, DistrictType


class EnhancedFeaturesDemo:
    """Demo application showcasing all enhanced features"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("SaiyanQuest Enhanced Features Demo")
        self.clock = pygame.time.Clock()
        
        # Initialize enhanced game integration
        self.game = EnhancedGameIntegration()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0
        
        # Demo state
        self.demo_mode = "physics"  # physics, vehicles, ai, world, integration
        self.demo_timer = 0.0
        self.demo_step = 0
        
        # Input state
        self.input_state = {
            'throttle': 0.0,
            'brake': 0.0,
            'steering': 0.0,
            'handbrake': False,
            'fire': False,
            'enter_exit_vehicle': False,
            'next_weapon': False,
            'prev_weapon': False
        }
        
        # Demo-specific state
        self.demo_vehicles = []
        self.demo_characters = []
        self.demo_stimuli = []
        
        print("🎮 Enhanced Features Demo initialized")
    
    def run(self):
        """Run the demo"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event.key)
            
            # Update demo
            self._update_demo(dt)
            
            # Render
            self._render()
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_keydown(self, key):
        """Handle key press events"""
        if key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_1:
            self.demo_mode = "physics"
            self._reset_demo()
        elif key == pygame.K_2:
            self.demo_mode = "vehicles"
            self._reset_demo()
        elif key == pygame.K_3:
            self.demo_mode = "ai"
            self._reset_demo()
        elif key == pygame.K_4:
            self.demo_mode = "world"
            self._reset_demo()
        elif key == pygame.K_5:
            self.demo_mode = "integration"
            self._reset_demo()
        elif key == pygame.K_w:
            self.input_state['throttle'] = 1.0
        elif key == pygame.K_s:
            self.input_state['brake'] = 1.0
        elif key == pygame.K_a:
            self.input_state['steering'] = -1.0
        elif key == pygame.K_d:
            self.input_state['steering'] = 1.0
        elif key == pygame.K_SPACE:
            self.input_state['handbrake'] = True
        elif key == pygame.K_f:
            self.input_state['fire'] = True
        elif key == pygame.K_e:
            self.input_state['enter_exit_vehicle'] = True
        elif key == pygame.K_r:
            self.input_state['next_weapon'] = True
    
    def _handle_keyup(self, key):
        """Handle key release events"""
        if key == pygame.K_w:
            self.input_state['throttle'] = 0.0
        elif key == pygame.K_s:
            self.input_state['brake'] = 0.0
        elif key == pygame.K_a:
            self.input_state['steering'] = 0.0
        elif key == pygame.K_d:
            self.input_state['steering'] = 0.0
        elif key == pygame.K_SPACE:
            self.input_state['handbrake'] = False
        elif key == pygame.K_f:
            self.input_state['fire'] = False
        elif key == pygame.K_e:
            self.input_state['enter_exit_vehicle'] = False
        elif key == pygame.K_r:
            self.input_state['next_weapon'] = False
    
    def _update_demo(self, dt):
        """Update demo based on current mode"""
        self.demo_timer += dt
        
        if self.demo_mode == "physics":
            self._update_physics_demo(dt)
        elif self.demo_mode == "vehicles":
            self._update_vehicles_demo(dt)
        elif self.demo_mode == "ai":
            self._update_ai_demo(dt)
        elif self.demo_mode == "world":
            self._update_world_demo(dt)
        elif self.demo_mode == "integration":
            self._update_integration_demo(dt)
    
    def _update_physics_demo(self, dt):
        """Update physics demo"""
        # Create some test bodies
        if self.demo_timer < 2.0 and len(self.demo_vehicles) < 5:
            x = random.uniform(100, 700)
            y = random.uniform(100, 300)
            
            # Create physics body
            body = self.game.physics_manager.create_body(
                PhysicsBodyType.DYNAMIC,
                (x, y),
                {
                    'type': 'circle',
                    'radius': 20,
                    'mass': 1.0,
                    'friction': 0.7,
                    'restitution': 0.3
                },
                CollisionCategory.VEHICLE
            )
            
            # Apply random force
            force_x = random.uniform(-1000, 1000)
            force_y = random.uniform(-1000, 1000)
            self.game.physics_manager.apply_force(body.body_id, (force_x, force_y))
            
            self.demo_vehicles.append(body.body_id)
        
        # Update physics
        self.game.physics_manager.update(dt)
    
    def _update_vehicles_demo(self, dt):
        """Update vehicles demo"""
        # Create vehicles
        if self.demo_timer < 3.0 and len(self.demo_vehicles) < 3:
            vehicle_types = ['sedan', 'sports_car', 'truck']
            vehicle_type = random.choice(vehicle_types)
            
            x = random.uniform(200, 600)
            y = random.uniform(200, 400)
            
            vehicle_id = self.game.vehicle_physics.create_vehicle(vehicle_type, (x, y))
            self.demo_vehicles.append(vehicle_id)
        
        # Update vehicles
        for vehicle_id in self.demo_vehicles:
            # Simple AI: drive forward with occasional steering
            throttle = 0.5
            brake = 0.0
            steering = random.uniform(-0.3, 0.3) if random.random() < 0.1 else 0.0
            handbrake = False
            
            self.game.vehicle_physics.update_vehicle(vehicle_id, dt, throttle, brake, steering, handbrake)
        
        # Update physics
        self.game.physics_manager.update(dt)
    
    def _update_ai_demo(self, dt):
        """Update AI demo"""
        # Create characters
        if self.demo_timer < 2.0 and len(self.demo_characters) < 5:
            x = random.uniform(100, 700)
            y = random.uniform(100, 500)
            
            character_id = self.game.character_ai.create_character(
                len(self.demo_characters) + 1000, (x, y)
            ).character_id
            self.demo_characters.append(character_id)
        
        # Create stimuli
        if self.demo_timer > 3.0 and len(self.demo_stimuli) < 3:
            stimulus_types = [StimulusType.GUNSHOT, StimulusType.EXPLOSION, StimulusType.LOUD_NOISE]
            stimulus_type = random.choice(stimulus_types)
            
            x = random.uniform(200, 600)
            y = random.uniform(200, 400)
            
            stimulus = Stimulus(
                stimulus_type=stimulus_type,
                position=(x, y),
                intensity=random.uniform(0.5, 1.0),
                radius=random.uniform(50, 150),
                timestamp=time.time()
            )
            
            self.game.character_ai.add_stimulus(stimulus)
            self.demo_stimuli.append(stimulus)
        
        # Update AI
        game_state = self.game._get_game_state_dict()
        self.game.character_ai.update_all_characters(dt, game_state)
        
        # Update physics
        self.game.physics_manager.update(dt)
    
    def _update_world_demo(self, dt):
        """Update world demo"""
        # Update world state
        self.game.world_3d.update_world_state(dt)
        
        # Create some test content
        if self.demo_timer < 1.0:
            # Create a test district
            district_id = self.game.world_3d.create_district(
                "Demo District", DistrictType.RESIDENTIAL, (100, 100, 300, 300)
            )
        
        # Test pathfinding
        if self.demo_timer > 2.0 and self.demo_timer < 3.0:
            path = self.game.world_3d.find_path((150, 150), (250, 250))
            if path:
                print(f"Path found with {len(path)} waypoints")
    
    def _update_integration_demo(self, dt):
        """Update integration demo"""
        # Update the full integrated game
        self.game.update(dt, self.input_state)
        
        # Update camera to follow player
        if self.game.state.player_vehicle_id:
            player_pos = self.game.vehicle_physics.get_vehicle_position(self.game.state.player_vehicle_id)
            self.camera_x = player_pos[0] - 600
            self.camera_y = player_pos[1] - 400
        elif self.game.state.player_character_id:
            player_pos = self.game.character_ai.character_controllers[self.game.state.player_character_id].physics_body.position
            self.camera_x = player_pos[0] - 600
            self.camera_y = player_pos[1] - 400
    
    def _reset_demo(self):
        """Reset demo state"""
        self.demo_timer = 0.0
        self.demo_step = 0
        self.demo_vehicles.clear()
        self.demo_characters.clear()
        self.demo_stimuli.clear()
        
        # Reset input
        for key in self.input_state:
            self.input_state[key] = False if key in ['handbrake', 'fire', 'enter_exit_vehicle', 'next_weapon', 'prev_weapon'] else 0.0
    
    def _render(self):
        """Render the demo"""
        self.screen.fill((20, 20, 40))  # Dark blue background
        
        if self.demo_mode == "physics":
            self._render_physics_demo()
        elif self.demo_mode == "vehicles":
            self._render_vehicles_demo()
        elif self.demo_mode == "ai":
            self._render_ai_demo()
        elif self.demo_mode == "world":
            self._render_world_demo()
        elif self.demo_mode == "integration":
            self._render_integration_demo()
        
        # Render UI
        self._render_ui()
    
    def _render_physics_demo(self):
        """Render physics demo"""
        # Draw physics bodies
        for body_id in self.demo_vehicles:
            body = self.game.physics_manager.get_body(body_id)
            if body:
                screen_x = int(body.position[0] - self.camera_x)
                screen_y = int(body.position[1] - self.camera_y)
                
                # Draw body
                pygame.draw.circle(self.screen, (255, 100, 100), (screen_x, screen_y), 20)
                
                # Draw velocity vector
                if body.velocity != (0, 0):
                    end_x = screen_x + int(body.velocity[0] * 0.1)
                    end_y = screen_y + int(body.velocity[1] * 0.1)
                    pygame.draw.line(self.screen, (255, 255, 0), (screen_x, screen_y), (end_x, end_y), 3)
    
    def _render_vehicles_demo(self):
        """Render vehicles demo"""
        # Draw vehicles
        for vehicle_id in self.demo_vehicles:
            position = self.game.vehicle_physics.get_vehicle_position(vehicle_id)
            angle = self.game.vehicle_physics.get_vehicle_angle(vehicle_id)
            speed = self.game.vehicle_physics.get_vehicle_speed(vehicle_id)
            
            screen_x = int(position[0] - self.camera_x)
            screen_y = int(position[1] - self.camera_y)
            
            # Draw vehicle as rectangle
            vehicle_rect = pygame.Rect(screen_x - 25, screen_y - 15, 50, 30)
            pygame.draw.rect(self.screen, (100, 200, 255), vehicle_rect)
            
            # Draw speed indicator
            speed_color = (255, 255, 0) if speed > 20 else (255, 100, 100)
            pygame.draw.circle(self.screen, speed_color, (screen_x, screen_y - 25), 5)
    
    def _render_ai_demo(self):
        """Render AI demo"""
        # Draw characters
        for character_id in self.demo_characters:
            controller = self.game.character_ai.character_controllers.get(character_id)
            if controller:
                position = controller.physics_body.position
                state = controller.ai.current_state.value
                fear_level = controller.ai.fear_level.value
                
                screen_x = int(position[0] - self.camera_x)
                screen_y = int(position[1] - self.camera_y)
                
                # Color based on fear level
                fear_colors = [(100, 255, 100), (255, 255, 100), (255, 200, 100), (255, 100, 100), (255, 50, 50)]
                color = fear_colors[min(fear_level, len(fear_colors) - 1)]
                
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), 8)
                
                # Draw state indicator
                pygame.draw.circle(self.screen, (255, 255, 255), (screen_x + 15, screen_y - 15), 3)
        
        # Draw stimuli
        for stimulus in self.demo_stimuli:
            screen_x = int(stimulus.position[0] - self.camera_x)
            screen_y = int(stimulus.position[1] - self.camera_y)
            
            # Color based on stimulus type
            stimulus_colors = {
                StimulusType.GUNSHOT: (255, 0, 0),
                StimulusType.EXPLOSION: (255, 100, 0),
                StimulusType.LOUD_NOISE: (255, 255, 0)
            }
            color = stimulus_colors.get(stimulus.stimulus_type, (255, 255, 255))
            
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 10)
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(stimulus.radius), 2)
    
    def _render_world_demo(self):
        """Render world demo"""
        # Draw districts
        for district in self.game.world_3d.districts.values():
            min_x, min_y, max_x, max_y = district.bounds
            
            screen_min_x = int(min_x - self.camera_x)
            screen_min_y = int(min_y - self.camera_y)
            screen_max_x = int(max_x - self.camera_x)
            screen_max_y = int(max_y - self.camera_y)
            
            district_rect = pygame.Rect(screen_min_x, screen_min_y, 
                                      screen_max_x - screen_min_x, screen_max_y - screen_min_y)
            
            # Color based on district type
            district_colors = {
                DistrictType.RESIDENTIAL: (100, 255, 100),
                DistrictType.COMMERCIAL: (100, 100, 255),
                DistrictType.INDUSTRIAL: (255, 100, 100),
                DistrictType.DOWNTOWN: (255, 255, 100)
            }
            color = district_colors.get(district.district_type, (255, 255, 255))
            
            pygame.draw.rect(self.screen, color, district_rect, 2)
        
        # Draw navigation sectors
        for sector in self.game.world_3d.navigation_sectors.values():
            min_x, min_y, max_x, max_y = sector.bounds
            
            screen_min_x = int(min_x - self.camera_x)
            screen_min_y = int(min_y - self.camera_y)
            screen_max_x = int(max_x - self.camera_x)
            screen_max_y = int(max_y - self.camera_y)
            
            sector_rect = pygame.Rect(screen_min_x, screen_min_y,
                                    screen_max_x - screen_min_x, screen_max_y - screen_min_y)
            
            color = (100, 100, 100) if sector.is_passable else (255, 100, 100)
            pygame.draw.rect(self.screen, color, sector_rect, 1)
    
    def _render_integration_demo(self):
        """Render integration demo"""
        # Draw all vehicles
        for vehicle_id in self.game.vehicle_physics.vehicles.keys():
            position = self.game.vehicle_physics.get_vehicle_position(vehicle_id)
            speed = self.game.vehicle_physics.get_vehicle_speed(vehicle_id)
            
            screen_x = int(position[0] - self.camera_x)
            screen_y = int(position[1] - self.camera_y)
            
            # Color based on speed
            speed_color = (255, 255, 0) if speed > 30 else (100, 200, 255)
            
            # Highlight player vehicle
            if vehicle_id == self.game.state.player_vehicle_id:
                pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 30, 3)
            
            pygame.draw.circle(self.screen, speed_color, (screen_x, screen_y), 15)
        
        # Draw all characters
        for character_id, controller in self.game.character_ai.character_controllers.items():
            position = controller.physics_body.position
            fear_level = controller.ai.fear_level.value
            
            screen_x = int(position[0] - self.camera_x)
            screen_y = int(position[1] - self.camera_y)
            
            # Color based on fear level
            fear_colors = [(100, 255, 100), (255, 255, 100), (255, 200, 100), (255, 100, 100), (255, 50, 50)]
            color = fear_colors[min(fear_level, len(fear_colors) - 1)]
            
            # Highlight player character
            if character_id == self.game.state.player_character_id:
                pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 12, 2)
            
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 6)
    
    def _render_ui(self):
        """Render UI"""
        # Demo mode indicator
        mode_text = f"Demo Mode: {self.demo_mode.upper()}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(mode_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # Controls
        controls_text = [
            "Controls:",
            "1-5: Switch demo modes",
            "WASD: Move (integration mode)",
            "Space: Handbrake",
            "F: Fire weapon",
            "E: Enter/Exit vehicle",
            "R: Switch weapon",
            "ESC: Quit"
        ]
        
        font_small = pygame.font.Font(None, 24)
        y_offset = 50
        for control in controls_text:
            text_surface = font_small.render(control, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # Statistics
        if self.demo_mode == "integration":
            stats = self.game.get_performance_statistics()
            stats_text = [
                f"FPS: {stats.get('fps', 0):.1f}",
                f"Vehicles: {stats.get('vehicles', 0)}",
                f"Characters: {stats.get('characters', 0)}",
                f"Distance: {stats.get('total_distance_km', 0):.2f} km",
                f"Crimes: {stats.get('crimes_committed', 0)}"
            ]
            
            y_offset = 300
            for stat in stats_text:
                text_surface = font_small.render(stat, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25


def main():
    """Main function"""
    print("🎮 Starting SaiyanQuest Enhanced Features Demo")
    print("This demo showcases all the new advanced features:")
    print("- Advanced Physics System with Box2D")
    print("- Enhanced Vehicle Physics with Tire Simulation")
    print("- Character AI with Fear Responses")
    print("- 3D World System with Multiple Layers")
    print("- Complete Game Integration")
    print("\nPress 1-5 to switch between demo modes")
    print("Press ESC to quit")
    
    demo = EnhancedFeaturesDemo()
    demo.run()
    
    print("✅ Demo completed")


if __name__ == "__main__":
    main()