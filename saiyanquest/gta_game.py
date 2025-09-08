#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Main GTA-style Game Integration System for SaiyanQuest

import warnings
import os
# Suppress warnings early
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

import pygame
import math
import random
import sys
from typing import Dict, List, Tuple, Optional, Any

# Import all our GTA systems
from .gta_world import WantedLevel
from .gta_world_streamer import GTAWorldStreamer
from .vehicle_system import VehicleManager, Vehicle, VehicleType
from .ai_systems import AIManager, PedestrianManager
from .mission_system import MissionManager, Mission
from .crime_system import CrimeSystem
from .weapon_system import WeaponInventory, CombatSystem, Weapon, WeaponType
from .character_system import Character, CharacterManager, CharacterType
from .gta_ui import UIManager, GTAHUD
from .save_system import SaveManager, GameStateManager

class GTAGameState:
    """Main game state container"""
    
    def __init__(self):
        # Core systems
        self.world = GTAWorldStreamer()
        self.character_manager = CharacterManager()
        
        # Create player character
        self.player_character = self.character_manager.create_character(
            CharacterType.PLAYER, 4000, 8000, is_player=True
        )
        
        self.vehicle_manager = VehicleManager()
        self.ai_manager = AIManager()
        self.mission_manager = MissionManager()
        self.crime_system = CrimeSystem()
        self.weapon_inventory = WeaponInventory()
        self.combat_system = CombatSystem()
        self.save_manager = SaveManager()
        self.state_manager = GameStateManager()
        
        # Player state - position is managed by character system
        self.player_x = self.player_character.x
        self.player_y = self.player_character.y
        self.player_angle = 0.0
        self.player_speed = 0.0
        self.player_velocity_x = 0.0
        self.player_velocity_y = 0.0
        
        # Current player state
        self.current_vehicle: Optional[Vehicle] = None
        self.current_weapon: Optional[Weapon] = None
        self.current_mission: Optional[Mission] = None
        self.in_combat = False
        self.is_player_hidden = False
        
        # Game time
        self.game_time = 0.0
        self.real_time_played = 0.0
        
        # Input handling
        self.input_state = {
            'up': False, 'down': False, 'left': False, 'right': False,
            'fire': False, 'aim': False, 'reload': False, 'enter_exit_vehicle': False,
            'next_weapon': False, 'prev_weapon': False,
            'handbrake': False, 'horn': False
        }
        self.input_cooldowns = {
            'enter_exit_vehicle': 0.0,
            'next_weapon': 0.0,
            'prev_weapon': 0.0,
            'reload': 0.0,
            'mission_advance': 0.0
        }
        
        # Initialize systems
        self._initialize_game_world()
        
    def _initialize_game_world(self) -> None:
        """Initialize the game world with content"""
        # Create sample missions
        self.mission_manager.create_sample_missions()
        
        # Spawn some initial vehicles
        self._spawn_initial_vehicles()
        
        # Setup safe zones for wanted level system
        self._setup_safe_zones()
        
        # Set current weapon
        self.current_weapon = self.weapon_inventory.current_weapon
        
    def _spawn_initial_vehicles(self) -> None:
        """Spawn some vehicles around the world"""
        spawn_locations = [
            (2400, 3200, VehicleType.SEDAN),
            (2300, 3150, VehicleType.MUSCLE_CAR),  # Grove Street
            (4000, 2500, VehicleType.SPORTS_CAR),  # Downtown
            (1500, 1000, VehicleType.BICYCLE),     # Beach area
            (5000, 4500, VehicleType.TRUCK),       # Industrial
        ]
        
        for x, y, vehicle_type in spawn_locations:
            self.vehicle_manager.spawn_vehicle(vehicle_type, x, y)
    
    def _setup_safe_zones(self) -> None:
        """Setup safe zones where wanted level decreases faster"""
        # Create safe zones around spawn points (these are usually safe houses)
        spawn_points = self.world.get_spawn_points()
        for spawn_point in spawn_points:
            safe_zone = pygame.Rect(
                spawn_point[0] - 50,
                spawn_point[1] - 50,
                100, 100
            )
            self.crime_system.add_safe_zone(safe_zone)

class GTAGame:
    """Main GTA-style game class"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        pygame.init()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("SaiyanQuest - GTA Style")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.fps_target = 60
        
        # Game state
        self.game_state = GTAGameState()
        
        # UI
        self.ui_manager = UIManager(screen_width, screen_height)
        
        # Debug
        self.debug_mode = False
        self.show_fps = True
        
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps_target) / 1000.0
            dt = min(dt, 1.0 / 30.0)  # Cap delta time to prevent large jumps
            
            self._handle_events()
            
            if not self.paused:
                self._update(dt)
            
            self._render()
            
            if self.show_fps:
                self._show_fps()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
                
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event.key)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.button, event.pos)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event.button, event.pos)
            
            # Let UI handle events too
            ui_action = self.ui_manager.handle_input(event)
            if ui_action:
                self._handle_ui_action(ui_action)
    
    def _handle_keydown(self, key: int) -> None:
        """Handle key press events"""
        # Movement
        if key == pygame.K_w or key == pygame.K_UP:
            self.game_state.input_state['up'] = True
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.game_state.input_state['down'] = True
        elif key == pygame.K_a or key == pygame.K_LEFT:
            self.game_state.input_state['left'] = True
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            self.game_state.input_state['right'] = True
        
        # Actions
        elif key == pygame.K_SPACE:
            self.game_state.input_state['handbrake'] = True
        elif key == pygame.K_LCTRL:
            self.game_state.input_state['fire'] = True
        elif key == pygame.K_LSHIFT:
            self.game_state.input_state['aim'] = True
        elif key == pygame.K_r:
            self.game_state.input_state['reload'] = True
        elif key == pygame.K_f or key == pygame.K_RETURN:
            self.game_state.input_state['enter_exit_vehicle'] = True
        elif key == pygame.K_q:
            self.game_state.input_state['prev_weapon'] = True
        elif key == pygame.K_e:
            self.game_state.input_state['next_weapon'] = True
        elif key == pygame.K_h:
            self.game_state.input_state['horn'] = True
            
        # Quick save/load
        elif key == pygame.K_F5:
            self._quick_save()
        elif key == pygame.K_F9:
            self._quick_load()
            
        # Debug
        elif key == pygame.K_F1:
            self.debug_mode = not self.debug_mode
        elif key == pygame.K_F2:
            self.show_fps = not self.show_fps
        elif key == pygame.K_F3:
            self.ui_manager.hud.toggle_hud_visibility()
        
        # Cheats (for development)
        elif key == pygame.K_F10:
            self.game_state.crime_system.cheat_clear_wanted_level()
        elif key == pygame.K_F11:
            # TODO: Implement money system with new character system
            # self.game_state.character.money += 10000
            pass
        elif key == pygame.K_F12:
            # TODO: Fix health system with new character system
            self.game_state.player_character.heal(self.game_state.player_character.physics.stats.max_health)
    
    def _handle_keyup(self, key: int) -> None:
        """Handle key release events"""
        if key == pygame.K_w or key == pygame.K_UP:
            self.game_state.input_state['up'] = False
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.game_state.input_state['down'] = False
        elif key == pygame.K_a or key == pygame.K_LEFT:
            self.game_state.input_state['left'] = False
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            self.game_state.input_state['right'] = False
        elif key == pygame.K_SPACE:
            self.game_state.input_state['handbrake'] = False
        elif key == pygame.K_LCTRL:
            self.game_state.input_state['fire'] = False
        elif key == pygame.K_LSHIFT:
            self.game_state.input_state['aim'] = False
        elif key == pygame.K_r:
            self.game_state.input_state['reload'] = False
        elif key == pygame.K_f or key == pygame.K_RETURN:
            self.game_state.input_state['enter_exit_vehicle'] = False
        elif key == pygame.K_q:
            self.game_state.input_state['prev_weapon'] = False
        elif key == pygame.K_e:
            self.game_state.input_state['next_weapon'] = False
        elif key == pygame.K_h:
            self.game_state.input_state['horn'] = False
    
    def _handle_mouse_down(self, button: int, pos: Tuple[int, int]) -> None:
        """Handle mouse button press"""
        if button == 1:  # Left click
            self.game_state.input_state['fire'] = True
        elif button == 3:  # Right click
            self.game_state.input_state['aim'] = True
    
    def _handle_mouse_up(self, button: int, pos: Tuple[int, int]) -> None:
        """Handle mouse button release"""
        if button == 1:  # Left click
            self.game_state.input_state['fire'] = False
        elif button == 3:  # Right click
            self.game_state.input_state['aim'] = False
    
    def _handle_ui_action(self, action: str) -> None:
        """Handle UI actions"""
        if action == "menu_toggle":
            self.paused = not self.paused
        elif action == "menu_select_resume":
            self.paused = False
            self.ui_manager.hide_current_menu()
        elif action == "menu_select_save_game":
            self._show_save_menu()
        elif action == "menu_select_load_game":
            self._show_load_menu()
        elif action == "menu_select_quit_game":
            self.running = False
    
    def _update(self, dt: float) -> None:
        """Update game logic"""
        # Update timers
        self.game_state.game_time += dt
        self.game_state.real_time_played += dt
        # TODO: Implement time tracking with new character system
        # self.game_state.character.time_played += dt
        
        # Update input cooldowns
        for key in self.game_state.input_cooldowns:
            if self.game_state.input_cooldowns[key] > 0:
                self.game_state.input_cooldowns[key] -= dt
        
        # Update player
        self._update_player(dt)
        
        # Update world and camera
        self.game_state.world.update_camera(self.game_state.player_x, self.game_state.player_y)
        
        # Update vehicle manager
        self.game_state.vehicle_manager.update_all_vehicles(dt)
        
        # Update AI systems
        game_state_dict = self._get_game_state_dict()
        self.game_state.ai_manager.update(dt, self.game_state.player_x, 
                                        self.game_state.player_y, 
                                        self.game_state.world,
                                        self.game_state.vehicle_manager)
        
        # Update mission system
        if self.game_state.current_mission:
            self.game_state.current_mission.update(dt, game_state_dict)
            
        self.game_state.mission_manager.update(dt, game_state_dict)
        
        # Update crime system
        self.game_state.crime_system.update(dt, game_state_dict)
        
        # Update combat system
        self.game_state.combat_system.update(dt)
        
        # Check for projectile hits
        self._check_combat_hits()
        
        # Update weapons
        if self.game_state.current_weapon:
            self.game_state.current_weapon.update(dt)
        
        # Update character progression
        # TODO: Implement stamina regeneration with new character system
        # self.game_state.character.regenerate_stamina(dt)
        
        # Check for unlocks
        newly_unlocked = self.game_state.progression_system.check_unlocks(self.game_state.character)
        for unlock in newly_unlocked:
            print(f"Unlocked: {unlock}")
        
        # Camera is now handled by the world streamer
        
        # Update UI
        self.ui_manager.update(dt, self.game_state.character, self.game_state.world)
        
        # Auto-save
        self.game_state.state_manager.save_manager.auto_save(
            dt, self.game_state.character, self.game_state.world,
            self.game_state.vehicle_manager, self.game_state.mission_manager,
            self.game_state.crime_system, self.game_state.player_x,
            self.game_state.player_y, self.game_state.game_time
        )
    
    def _update_player(self, dt: float) -> None:
        """Update player movement and actions"""
        # Handle weapon switching
        self._handle_weapon_switching()
        
        # Handle vehicle entry/exit
        self._handle_vehicle_interaction()
        
        # Handle combat
        self._handle_combat(dt)
        
        if self.game_state.current_vehicle:
            # Player is in vehicle
            self._update_player_in_vehicle(dt)
        else:
            # Player on foot
            self._update_player_on_foot(dt)
        
        # Keep player in world bounds
        self.game_state.player_x = max(0, min(self.game_state.player_x, self.game_state.world.world_width))
        self.game_state.player_y = max(0, min(self.game_state.player_y, self.game_state.world.world_height))
    
    def _update_player_on_foot(self, dt: float) -> None:
        """Update player when on foot"""
        base_speed = 150.0  # pixels per second
        run_multiplier = 2.0
        
        # Get speed multiplier from character stats
        # TODO: Implement speed multiplier with new character system
        speed_multiplier = 1.0  # self.game_state.character.get_speed_multiplier()
        
        # Check if running (shift key or high movement input)
        is_running = self.game_state.input_state['aim']  # Using aim key as run key when on foot
        
        if is_running:
            # TODO: Implement stamina system with new character system
            if True:  # self.game_state.character.use_stamina(100 * dt):
                speed_multiplier *= run_multiplier
                # Train muscle and stamina from running
                # TODO: Implement skill training with new character system
                # self.game_state.character.train_skill(SkillType.DRIVING, 0.1)
        
        # Calculate movement
        move_x = 0.0
        move_y = 0.0
        
        if self.game_state.input_state['up']:
            move_y -= 1.0
        if self.game_state.input_state['down']:
            move_y += 1.0
        if self.game_state.input_state['left']:
            move_x -= 1.0
        if self.game_state.input_state['right']:
            move_x += 1.0
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707
        
        # Apply movement
        final_speed = base_speed * speed_multiplier
        self.game_state.player_velocity_x = move_x * final_speed
        self.game_state.player_velocity_y = move_y * final_speed
        
        # Update position
        self.game_state.player_x += self.game_state.player_velocity_x * dt
        self.game_state.player_y += self.game_state.player_velocity_y * dt
        
        # Update player speed for other systems
        self.game_state.player_speed = math.sqrt(
            self.game_state.player_velocity_x**2 + self.game_state.player_velocity_y**2
        ) * 3.6  # Convert to km/h
        
        # Update character stats based on movement
        distance_moved = math.sqrt(
            self.game_state.player_velocity_x**2 + self.game_state.player_velocity_y**2
        ) * dt
        # TODO: Implement distance tracking with new character system
        # self.game_state.character.distance_walked += distance_moved
        
        # Update angle based on movement direction
        if move_x != 0 or move_y != 0:
            self.game_state.player_angle = math.degrees(math.atan2(move_y, move_x))
    
    def _update_player_in_vehicle(self, dt: float) -> None:
        """Update player when in vehicle"""
        vehicle = self.game_state.current_vehicle
        
        # Apply vehicle controls
        if self.game_state.input_state['up']:
            vehicle.throttle = 1.0
        elif self.game_state.input_state['down']:
            vehicle.throttle = -0.5  # Reverse
        else:
            vehicle.throttle = 0.0
        
        if self.game_state.input_state['left']:
            vehicle.steering = -1.0
        elif self.game_state.input_state['right']:
            vehicle.steering = 1.0
        else:
            vehicle.steering = 0.0
        
        vehicle.handbrake = self.game_state.input_state['handbrake']
        
        # Horn
        if self.game_state.input_state['horn']:
            # Play horn sound (placeholder)
            pass
        
        # Update player position to match vehicle
        self.game_state.player_x = vehicle.x
        self.game_state.player_y = vehicle.y
        self.game_state.player_angle = vehicle.angle
        self.game_state.player_speed = vehicle.get_speed_kmh()
        
        # Update character driving skill
        if abs(vehicle.throttle) > 0.1:
            # TODO: Implement driving skill training with new character system
            # self.game_state.character.train_skill(SkillType.DRIVING, 0.5 * dt)
            # TODO: Implement distance tracking with new character system
            # self.game_state.character.distance_driven += vehicle.get_speed_kmh() * dt / 3600
            pass
        
        # Check for collisions with other vehicles or objects
        self._check_vehicle_collisions()
    
    def _handle_weapon_switching(self) -> None:
        """Handle weapon switching"""
        if (self.game_state.input_state['next_weapon'] and 
            self.game_state.input_cooldowns['next_weapon'] <= 0):
            
            self.game_state.weapon_inventory.next_weapon_in_category()
            self.game_state.current_weapon = self.game_state.weapon_inventory.current_weapon
            self.game_state.input_cooldowns['next_weapon'] = 0.3
            
        elif (self.game_state.input_state['prev_weapon'] and 
              self.game_state.input_cooldowns['prev_weapon'] <= 0):
            
            self.game_state.weapon_inventory.previous_weapon_in_category()
            self.game_state.current_weapon = self.game_state.weapon_inventory.current_weapon
            self.game_state.input_cooldowns['prev_weapon'] = 0.3
    
    def _handle_vehicle_interaction(self) -> None:
        """Handle entering/exiting vehicles"""
        if (self.game_state.input_state['enter_exit_vehicle'] and 
            self.game_state.input_cooldowns['enter_exit_vehicle'] <= 0):
            
            if self.game_state.current_vehicle:
                # Exit vehicle
                self.game_state.current_vehicle.exit_vehicle(self.game_state.character)
                self.game_state.current_vehicle = None
            else:
                # Try to enter nearby vehicle
                nearby_vehicle = self.game_state.vehicle_manager.get_nearest_vehicle(
                    self.game_state.player_x, self.game_state.player_y, 50.0
                )
                
                if nearby_vehicle:
                    if nearby_vehicle.enter_vehicle(self.game_state.character):
                        self.game_state.current_vehicle = nearby_vehicle
                        nearby_vehicle.start_engine()
                        
                        # Crime if stealing
                        if nearby_vehicle in self.game_state.vehicle_manager.traffic_vehicles:
                            self.game_state.crime_system.player_stole_item(
                                self.game_state.player_x, self.game_state.player_y,
                                "vehicle", 10000
                            )
            
            self.game_state.input_cooldowns['enter_exit_vehicle'] = 0.5
    
    def _handle_combat(self, dt: float) -> None:
        """Handle combat actions"""
        if not self.game_state.current_weapon:
            return
        
        # Reload
        if (self.game_state.input_state['reload'] and 
            self.game_state.input_cooldowns['reload'] <= 0):
            if self.game_state.current_weapon.reload():
                self.game_state.input_cooldowns['reload'] = 1.0
        
        # Fire weapon
        if self.game_state.input_state['fire']:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + self.game_state.world.camera_x
            world_mouse_y = mouse_y + self.game_state.world.camera_y
            
            current_time = self.game_state.game_time
            
            if self.game_state.combat_system.fire_weapon(
                self.game_state.current_weapon,
                self.game_state.player_x,
                self.game_state.player_y,
                world_mouse_x,
                world_mouse_y,
                current_time
            ):
                # Train weapon skill
                # TODO: Implement weapon skill training with new character system
                # weapon_skill = self._get_weapon_skill_type(self.game_state.current_weapon.category)
                # if weapon_skill:
                #     self.game_state.character.train_skill(weapon_skill, 0.2)
                pass  # Placeholder
    
    # TODO: Re-implement weapon skill mapping with new character system
    # def _get_weapon_skill_type(self, weapon_category) -> Optional[SkillType]:
    #     """Get skill type for weapon category"""
    #     from .weapon_system import WeaponCategory
    #     skill_map = {
    #         WeaponCategory.PISTOL: SkillType.PISTOL,
    #         WeaponCategory.RIFLE: SkillType.RIFLE,
    #         WeaponCategory.SHOTGUN: SkillType.SHOTGUN,
    #         WeaponCategory.SMG: SkillType.SMG,
    #         WeaponCategory.SNIPER: SkillType.SNIPER,
    #         WeaponCategory.HEAVY: SkillType.HEAVY,
    #         WeaponCategory.MELEE: SkillType.MELEE,
    #     }
    #     return skill_map.get(weapon_category)
    
    def _check_combat_hits(self) -> None:
        """Check for combat hits and apply damage"""
        # Get all possible targets
        targets = []
        
        # Add pedestrians as targets
        for pedestrian in self.game_state.ai_manager.pedestrian_manager.pedestrians:
            targets.append({
                'x': pedestrian.x,
                'y': pedestrian.y,
                'radius': 15,
                'type': 'pedestrian',
                'object': pedestrian
            })
        
        # Add vehicles as targets
        for vehicle in self.game_state.vehicle_manager.vehicles + self.game_state.vehicle_manager.traffic_vehicles:
            if vehicle != self.game_state.current_vehicle:
                vehicle_rect = vehicle.get_rect()
                targets.append({
                    'x': vehicle.x,
                    'y': vehicle.y,
                    'radius': max(vehicle_rect.width, vehicle_rect.height) // 2,
                    'type': 'vehicle',
                    'object': vehicle
                })
        
        # Check hits
        hits = self.game_state.combat_system.check_projectile_collisions(targets)
        
        for hit in hits:
            target = hit['target']
            damage = hit['damage']
            
            if target['type'] == 'pedestrian':
                pedestrian = target['object']
                pedestrian.health -= damage
                
                if pedestrian.health <= 0:
                    pedestrian.state = pedestrian.PedestrianState.DEAD
                    self.game_state.crime_system.player_used_weapon(
                        self.game_state.player_x, self.game_state.player_y,
                        pedestrian.pedestrian_type.value, True
                    )
                    # TODO: Implement kill tracking with new character system
                    # self.game_state.character.kills += 1
                else:
                    self.game_state.crime_system.player_used_weapon(
                        self.game_state.player_x, self.game_state.player_y,
                        pedestrian.pedestrian_type.value, False
                    )
            
            elif target['type'] == 'vehicle':
                vehicle = target['object']
                vehicle.take_damage(damage)
                
                if vehicle.health <= 0:
                    self.game_state.crime_system.player_damaged_property(
                        vehicle.x, vehicle.y, 5000
                    )
    
    def _check_vehicle_collisions(self) -> None:
        """Check for vehicle collisions"""
        if not self.game_state.current_vehicle:
            return
        
        player_vehicle = self.game_state.current_vehicle
        player_rect = player_vehicle.get_rect()
        
        # Check collision with other vehicles
        for vehicle in (self.game_state.vehicle_manager.vehicles + 
                       self.game_state.vehicle_manager.traffic_vehicles):
            if vehicle == player_vehicle:
                continue
            
            if player_rect.colliderect(vehicle.get_rect()):
                # Handle collision
                damage = min(20, player_vehicle.get_speed_kmh() * 0.5)
                vehicle.take_damage(damage)
                player_vehicle.take_damage(damage * 0.5)
                
                # Report crime
                crime = self.game_state.crime_system.crime_detector.check_vehicle_collision(
                    player_vehicle, vehicle, damage
                )
                if crime:
                    game_state_dict = self._get_game_state_dict()
                    self.game_state.crime_system.commit_crime(crime, game_state_dict)
    
    
    def _get_game_state_dict(self) -> Dict[str, Any]:
        """Get game state as dictionary for other systems"""
        return {
            'player_x': self.game_state.player_x,
            'player_y': self.game_state.player_y,
            'player_speed': self.game_state.player_speed,
            'player_vehicle': self.game_state.current_vehicle,
            'player_hidden': self.game_state.is_player_hidden,
            'game_time': self.game_state.game_time,
            'wanted_level': 0,  # TODO: Fix wanted level integration with streamer
            'nearby_pedestrians': self.game_state.ai_manager.get_nearby_pedestrians(
                self.game_state.player_x, self.game_state.player_y, 200
            ),
            'nearby_police': [],  # Would be populated by police AI
            'killed_targets': [],  # Would track killed targets
            'collected_items': {},  # Would track collected items
            'destroyed_vehicles': [],  # Would track destroyed vehicles
            'mission_time': 0.0 if not self.game_state.current_mission else 
                           self.game_state.game_time - self.game_state.current_mission.start_time
        }
    
    def _render(self) -> None:
        """Render the game"""
        self.screen.fill((50, 100, 50))  # Background color (grass-like)
        
        # Render world background
        self._render_world_background()
        
        # Render vehicles
        self._render_vehicles()
        
        # Render pedestrians
        self._render_pedestrians()
        
        # Render player
        self._render_player()
        
        # Render projectiles and effects
        self._render_combat_effects()
        
        # Render UI
        self.ui_manager.render(
            self.screen, self.game_state.character, self.game_state.world,
            self.game_state.current_weapon, self.game_state.current_vehicle,
            self.game_state.current_mission
        )
        
        # Render minimap
        self.game_state.world.render_minimap(self.screen, 
                                           self.game_state.player_x, 
                                           self.game_state.player_y)
        
        # Debug rendering
        if self.debug_mode:
            self._render_debug_info()
        
        pygame.display.flip()
    
    def _render_world_background(self) -> None:
        """Render world background elements"""
        # Use the streaming world renderer
        self.game_state.world.render_world(self.screen)
    
    def _render_vehicles(self) -> None:
        """Render all vehicles"""
        all_vehicles = (self.game_state.vehicle_manager.vehicles + 
                       self.game_state.vehicle_manager.traffic_vehicles)
        
        for vehicle in all_vehicles:
            screen_x = vehicle.x - self.game_state.world.camera_x
            screen_y = vehicle.y - self.game_state.world.camera_y
            
            # Only render if on screen
            if (-100 <= screen_x <= self.screen_width + 100 and 
                -100 <= screen_y <= self.screen_height + 100):
                
                # Choose color based on vehicle type
                if vehicle.vehicle_type.name.startswith('POLICE'):
                    color = (0, 0, 255)  # Blue
                elif vehicle.vehicle_type.name.startswith('FIRE'):
                    color = (255, 0, 0)  # Red
                elif vehicle.vehicle_type.name == 'TAXI':
                    color = (255, 255, 0)  # Yellow
                else:
                    color = (150, 150, 150)  # Gray
                
                # Render as simple rectangle for now
                rect = pygame.Rect(screen_x - vehicle.width//2, screen_y - vehicle.height//2,
                                 vehicle.width, vehicle.height)
                pygame.draw.rect(self.screen, color, rect)
                
                # Show health bar for damaged vehicles
                if vehicle.health < 100:
                    health_width = int((vehicle.width * vehicle.health) / 100)
                    health_rect = pygame.Rect(screen_x - vehicle.width//2, 
                                            screen_y - vehicle.height//2 - 10,
                                            health_width, 4)
                    pygame.draw.rect(self.screen, (255, 0, 0), health_rect)
    
    def _render_pedestrians(self) -> None:
        """Render all pedestrians"""
        for pedestrian in self.game_state.ai_manager.pedestrian_manager.pedestrians:
            screen_x = pedestrian.x - self.game_state.world.camera_x
            screen_y = pedestrian.y - self.game_state.world.camera_y
            
            # Only render if on screen
            if (-50 <= screen_x <= self.screen_width + 50 and 
                -50 <= screen_y <= self.screen_height + 50):
                
                # Choose color and size based on state
                if pedestrian.state.name == 'DEAD':
                    color = (100, 0, 0)  # Dark red
                    radius = 8
                elif pedestrian.state.name == 'FLEEING':
                    color = (255, 255, 0)  # Yellow
                    radius = 12
                else:
                    color = pedestrian.color
                    radius = 10
                
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
                
                # Show health bar for damaged pedestrians
                if pedestrian.health < 100 and pedestrian.state.name != 'DEAD':
                    health_width = int((20 * pedestrian.health) / 100)
                    health_rect = pygame.Rect(screen_x - 10, screen_y - 20, health_width, 3)
                    pygame.draw.rect(self.screen, (255, 0, 0), health_rect)
    
    def _render_player(self) -> None:
        """Render the player"""
        screen_x = self.game_state.player_x - self.game_state.world.camera_x
        screen_y = self.game_state.player_y - self.game_state.world.camera_y
        
        if self.game_state.current_vehicle:
            # Player is in vehicle - highlight the vehicle
            vehicle = self.game_state.current_vehicle
            rect = pygame.Rect(screen_x - vehicle.width//2, screen_y - vehicle.height//2,
                             vehicle.width, vehicle.height)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 3)  # White outline
        else:
            # Player on foot
            color = (255, 0, 255)  # Magenta for player
            radius = 15
            
            pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
            
            # Draw direction indicator
            direction_length = 25
            end_x = screen_x + math.cos(math.radians(self.game_state.player_angle)) * direction_length
            end_y = screen_y + math.sin(math.radians(self.game_state.player_angle)) * direction_length
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (screen_x, screen_y), (end_x, end_y), 2)
    
    def _render_combat_effects(self) -> None:
        """Render projectiles and combat effects"""
        # Render projectiles
        for projectile in self.game_state.combat_system.projectiles:
            screen_x = projectile.x - self.game_state.world.camera_x
            screen_y = projectile.y - self.game_state.world.camera_y
            
            if (-10 <= screen_x <= self.screen_width + 10 and 
                -10 <= screen_y <= self.screen_height + 10):
                
                if projectile.is_flame:
                    color = (255, 100, 0)  # Orange for flames
                    radius = 8
                else:
                    color = (255, 255, 0)  # Yellow for bullets
                    radius = 3
                
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
        
        # Render explosions
        for explosion in self.game_state.combat_system.explosions:
            screen_x = explosion['position'][0] - self.game_state.world.camera_x
            screen_y = explosion['position'][1] - self.game_state.world.camera_y
            
            if (-200 <= screen_x <= self.screen_width + 200 and 
                -200 <= screen_y <= self.screen_height + 200):
                
                alpha = explosion['lifetime'] / 2.0
                radius = int(explosion['radius'] * (2.0 - alpha))
                
                # Create explosion effect
                for i in range(3):
                    color_intensity = int(255 * alpha)
                    colors = [
                        (color_intensity, color_intensity//2, 0),  # Orange
                        (color_intensity, color_intensity//4, 0),  # Red-orange
                        (color_intensity//2, 0, 0)  # Dark red
                    ]
                    
                    pygame.draw.circle(self.screen, colors[i], 
                                     (int(screen_x), int(screen_y)), 
                                     radius - i * 10)
    
    def _render_debug_info(self) -> None:
        """Render debug information"""
        debug_font = pygame.font.Font(None, 24)
        y_offset = 10
        
        world_stats = self.game_state.world.get_world_stats()
        debug_info = [
            f"Player Pos: ({self.game_state.player_x:.1f}, {self.game_state.player_y:.1f})",
            f"Player Speed: {self.game_state.player_speed:.1f} km/h",
            f"Health: {self.game_state.player_character.health:.1f}/{self.game_state.player_character.physics.stats.max_health:.1f}",
            f"Money: $0",  # TODO: Implement money system
            f"Vehicle: {'Yes' if self.game_state.current_vehicle else 'No'}",
            f"Weapon: {self.game_state.current_weapon.weapon_type.value if self.game_state.current_weapon else 'None'}",
            f"World Chunks: {world_stats.get('loaded_chunks', 0)}/{world_stats.get('total_chunks', 0)}",
            f"Active Entities: {world_stats.get('active_entities', 0)}",
            f"Maps Available: {world_stats.get('total_maps', 0)}",
            f"Pedestrians: {len(self.game_state.ai_manager.pedestrian_manager.pedestrians)}",
            f"Vehicles: {len(self.game_state.vehicle_manager.vehicles + self.game_state.vehicle_manager.traffic_vehicles)}"
        ]
        
        for info in debug_info:
            text = debug_font.render(info, True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
    
    def _show_fps(self) -> None:
        """Show FPS counter"""
        fps = self.clock.get_fps()
        fps_font = pygame.font.Font(None, 36)
        fps_text = fps_font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
        self.screen.blit(fps_text, (self.screen_width - 120, 10))
    
    def _quick_save(self) -> None:
        """Quick save the game"""
        success = self.game_state.state_manager.save_manager.quick_save(
            self.game_state.character, self.game_state.world,
            self.game_state.vehicle_manager, self.game_state.mission_manager,
            self.game_state.crime_system, self.game_state.player_x,
            self.game_state.player_y, self.game_state.game_time
        )
        
        if success:
            print("Quick save completed")
        else:
            print("Quick save failed")
    
    def _quick_load(self) -> None:
        """Quick load the game"""
        save_data = self.game_state.state_manager.save_manager.quick_load()
        
        if save_data:
            # Apply save data
            player_x, player_y, game_time = self.game_state.state_manager.apply_save_data(
                save_data, self.game_state.character, self.game_state.world,
                self.game_state.vehicle_manager, self.game_state.mission_manager,
                self.game_state.crime_system
            )
            
            self.game_state.player_x = player_x
            self.game_state.player_y = player_y
            self.game_state.game_time = game_time
            self.game_state.current_vehicle = None  # Reset vehicle reference
            
            print("Quick load completed")
        else:
            print("Quick load failed - no save found")
    
    def _show_save_menu(self) -> None:
        """Show save game menu"""
        # This would show a proper save menu
        print("Save menu would appear here")
    
    def _show_load_menu(self) -> None:
        """Show load game menu"""
        # This would show a proper load menu
        print("Load menu would appear here")

def main():
    """Main entry point"""
    game = GTAGame()
    game.run()

if __name__ == "__main__":
    main()