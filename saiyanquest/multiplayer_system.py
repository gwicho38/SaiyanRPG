#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Multiplayer System with Split-Screen Support

import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager
from .vehicle_physics import VehiclePhysicsSystem
from .character_ai import CharacterAIManager
from .world_3d_system import World3DSystem


class GameMode(Enum):
    """Multiplayer game modes"""
    FREE_ROAM = "free_roam"
    DEATHMATCH = "deathmatch"
    TEAM_DEATHMATCH = "team_deathmatch"
    CAPTURE_THE_FLAG = "capture_the_flag"
    RACE = "race"
    COOPERATIVE = "cooperative"


class PlayerState(Enum):
    """Player states"""
    CONNECTED = "connected"
    READY = "ready"
    PLAYING = "playing"
    SPECTATING = "spectating"
    DISCONNECTED = "disconnected"


@dataclass
class Player:
    """Player information"""
    player_id: int
    name: str
    state: PlayerState
    character_id: Optional[int]
    vehicle_id: Optional[int]
    score: int
    kills: int
    deaths: int
    team_id: Optional[int]
    connection_time: float
    last_activity: float


@dataclass
class Camera:
    """Camera for split-screen"""
    camera_id: int
    player_id: int
    x: float
    y: float
    zoom: float
    angle: float
    viewport: Tuple[int, int, int, int]  # x, y, width, height


class SplitScreenManager:
    """Manages split-screen layouts"""
    
    def __init__(self, screen_width: int = 1200, screen_height: int = 800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cameras: Dict[int, Camera] = {}
        
        print("📺 SplitScreenManager initialized")
    
    def setup_split_screen(self, num_players: int) -> Dict[int, Camera]:
        """Setup split-screen layout for number of players"""
        self.cameras.clear()
        
        if num_players == 1:
            # Single player - full screen
            camera = Camera(
                camera_id=0,
                player_id=0,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, 0, self.screen_width, self.screen_height)
            )
            self.cameras[0] = camera
            
        elif num_players == 2:
            # Two players - side by side
            width = self.screen_width // 2
            height = self.screen_height
            
            camera1 = Camera(
                camera_id=0,
                player_id=0,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, 0, width, height)
            )
            camera2 = Camera(
                camera_id=1,
                player_id=1,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(width, 0, width, height)
            )
            
            self.cameras[0] = camera1
            self.cameras[1] = camera2
            
        elif num_players == 3:
            # Three players - top player full width, bottom two split
            top_width = self.screen_width
            top_height = self.screen_height // 2
            bottom_width = self.screen_width // 2
            bottom_height = self.screen_height // 2
            
            camera1 = Camera(
                camera_id=0,
                player_id=0,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, 0, top_width, top_height)
            )
            camera2 = Camera(
                camera_id=1,
                player_id=1,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, top_height, bottom_width, bottom_height)
            )
            camera3 = Camera(
                camera_id=2,
                player_id=2,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(bottom_width, top_height, bottom_width, bottom_height)
            )
            
            self.cameras[0] = camera1
            self.cameras[1] = camera2
            self.cameras[2] = camera3
            
        elif num_players == 4:
            # Four players - 2x2 grid
            width = self.screen_width // 2
            height = self.screen_height // 2
            
            camera1 = Camera(
                camera_id=0,
                player_id=0,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, 0, width, height)
            )
            camera2 = Camera(
                camera_id=1,
                player_id=1,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(width, 0, width, height)
            )
            camera3 = Camera(
                camera_id=2,
                player_id=2,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(0, height, width, height)
            )
            camera4 = Camera(
                camera_id=3,
                player_id=3,
                x=0, y=0,
                zoom=1.0,
                angle=0.0,
                viewport=(width, height, width, height)
            )
            
            self.cameras[0] = camera1
            self.cameras[1] = camera2
            self.cameras[2] = camera3
            self.cameras[3] = camera4
        
        print(f"📺 Setup split-screen for {num_players} players")
        return self.cameras.copy()
    
    def update_camera(self, camera_id: int, x: float, y: float, zoom: float = 1.0, angle: float = 0.0):
        """Update camera position and properties"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            camera.x = x
            camera.y = y
            camera.zoom = zoom
            camera.angle = angle
    
    def get_camera(self, camera_id: int) -> Optional[Camera]:
        """Get camera by ID"""
        return self.cameras.get(camera_id)


class MultiplayerManager:
    """Main multiplayer management system"""
    
    def __init__(self, physics_manager: PhysicsManager, 
                 vehicle_physics: VehiclePhysicsSystem,
                 character_ai: CharacterAIManager,
                 world_3d: World3DSystem):
        self.physics_manager = physics_manager
        self.vehicle_physics = vehicle_physics
        self.character_ai = character_ai
        self.world_3d = world_3d
        
        # Multiplayer state
        self.players: Dict[int, Player] = {}
        self.next_player_id = 1
        self.max_players = 4
        self.current_game_mode = GameMode.FREE_ROAM
        
        # Split-screen management
        self.split_screen = SplitScreenManager()
        
        # Game state
        self.game_started = False
        self.game_start_time = 0.0
        self.round_time = 0.0
        self.max_round_time = 300.0  # 5 minutes
        
        # Teams
        self.teams: Dict[int, List[int]] = {}  # team_id -> player_ids
        self.next_team_id = 1
        
        print("👥 MultiplayerManager initialized")
    
    def add_player(self, name: str) -> int:
        """Add a new player"""
        if len(self.players) >= self.max_players:
            print(f"❌ Cannot add player {name}: maximum players reached")
            return -1
        
        player_id = self.next_player_id
        self.next_player_id += 1
        
        player = Player(
            player_id=player_id,
            name=name,
            state=PlayerState.CONNECTED,
            character_id=None,
            vehicle_id=None,
            score=0,
            kills=0,
            deaths=0,
            team_id=None,
            connection_time=time.time(),
            last_activity=time.time()
        )
        
        self.players[player_id] = player
        
        # Create character for player
        spawn_position = self._get_spawn_position()
        character_id = self.character_ai.create_character(
            player_id + 1000, spawn_position
        ).character_id
        player.character_id = character_id
        
        # Setup split-screen
        self.split_screen.setup_split_screen(len(self.players))
        
        print(f"👥 Added player {name} (ID: {player_id})")
        return player_id
    
    def remove_player(self, player_id: int) -> bool:
        """Remove a player"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        
        # Remove character
        if player.character_id:
            self.character_ai.remove_character(player.character_id)
        
        # Remove from teams
        if player.team_id and player.team_id in self.teams:
            if player_id in self.teams[player.team_id]:
                self.teams[player.team_id].remove(player_id)
        
        del self.players[player_id]
        
        # Update split-screen
        self.split_screen.setup_split_screen(len(self.players))
        
        print(f"👥 Removed player {player_id}")
        return True
    
    def set_player_ready(self, player_id: int) -> bool:
        """Set player as ready"""
        if player_id not in self.players:
            return False
        
        self.players[player_id].state = PlayerState.READY
        print(f"👥 Player {player_id} is ready")
        return True
    
    def start_game(self, game_mode: GameMode) -> bool:
        """Start multiplayer game"""
        if len(self.players) < 1:
            print("❌ Cannot start game: no players")
            return False
        
        # Check if all players are ready
        ready_players = [p for p in self.players.values() if p.state == PlayerState.READY]
        if len(ready_players) != len(self.players):
            print("❌ Cannot start game: not all players ready")
            return False
        
        self.current_game_mode = game_mode
        self.game_started = True
        self.game_start_time = time.time()
        self.round_time = 0.0
        
        # Setup teams based on game mode
        self._setup_teams()
        
        # Set all players to playing state
        for player in self.players.values():
            player.state = PlayerState.PLAYING
        
        print(f"🎮 Started {game_mode.value} game with {len(self.players)} players")
        return True
    
    def _setup_teams(self):
        """Setup teams based on game mode"""
        self.teams.clear()
        
        if self.current_game_mode == GameMode.TEAM_DEATHMATCH:
            # Split players into two teams
            player_ids = list(self.players.keys())
            mid_point = len(player_ids) // 2
            
            team1_id = self.next_team_id
            self.next_team_id += 1
            team2_id = self.next_team_id
            self.next_team_id += 1
            
            self.teams[team1_id] = player_ids[:mid_point]
            self.teams[team2_id] = player_ids[mid_point:]
            
            # Assign team IDs to players
            for player_id in self.teams[team1_id]:
                self.players[player_id].team_id = team1_id
            for player_id in self.teams[team2_id]:
                self.players[player_id].team_id = team2_id
                
        elif self.current_game_mode == GameMode.CAPTURE_THE_FLAG:
            # Similar to team deathmatch
            self._setup_teams()  # Same logic
        else:
            # Free-for-all modes - no teams
            pass
    
    def _get_spawn_position(self) -> Tuple[float, float]:
        """Get spawn position for new player"""
        # Simple spawn logic - spawn around the center
        center_x, center_y = 500, 500
        radius = 50
        
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        
        x = center_x + math.cos(angle) * distance
        y = center_y + math.sin(angle) * distance
        
        return (x, y)
    
    def update(self, dt: float) -> None:
        """Update multiplayer system"""
        if not self.game_started:
            return
        
        # Update round time
        self.round_time += dt
        
        # Check for game end conditions
        if self.round_time >= self.max_round_time:
            self._end_game()
            return
        
        # Update player cameras
        self._update_cameras()
        
        # Update game mode specific logic
        if self.current_game_mode == GameMode.DEATHMATCH:
            self._update_deathmatch(dt)
        elif self.current_game_mode == GameMode.TEAM_DEATHMATCH:
            self._update_team_deathmatch(dt)
        elif self.current_game_mode == GameMode.RACE:
            self._update_race(dt)
    
    def _update_cameras(self):
        """Update player cameras"""
        for player in self.players.values():
            if player.state != PlayerState.PLAYING:
                continue
            
            # Get player position
            position = self._get_player_position(player)
            if position:
                # Update camera for this player
                camera_id = list(self.players.keys()).index(player.player_id)
                self.split_screen.update_camera(camera_id, position[0], position[1])
    
    def _get_player_position(self, player: Player) -> Optional[Tuple[float, float]]:
        """Get player's current position"""
        if player.vehicle_id:
            return self.vehicle_physics.get_vehicle_position(player.vehicle_id)
        elif player.character_id:
            controller = self.character_ai.character_controllers.get(player.character_id)
            if controller:
                return controller.physics_body.position
        return None
    
    def _update_deathmatch(self, dt: float):
        """Update deathmatch game mode"""
        # Check for win conditions
        # In deathmatch, could be first to X kills or highest score after time limit
        pass
    
    def _update_team_deathmatch(self, dt: float):
        """Update team deathmatch game mode"""
        # Check team scores
        team_scores = {}
        for team_id, player_ids in self.teams.items():
            team_score = sum(self.players[pid].kills for pid in player_ids)
            team_scores[team_id] = team_score
        
        # Check for win condition
        max_score = max(team_scores.values()) if team_scores else 0
        if max_score >= 50:  # First team to 50 kills wins
            self._end_game()
    
    def _update_race(self, dt: float):
        """Update race game mode"""
        # Check for race completion
        # Could check if any player has completed the race
        pass
    
    def _end_game(self):
        """End the current game"""
        self.game_started = False
        
        # Calculate final scores
        winner = self._determine_winner()
        
        print(f"🎮 Game ended. Winner: {winner}")
        
        # Reset player states
        for player in self.players.values():
            player.state = PlayerState.READY
    
    def _determine_winner(self) -> str:
        """Determine game winner"""
        if self.current_game_mode == GameMode.DEATHMATCH:
            # Player with most kills
            best_player = max(self.players.values(), key=lambda p: p.kills)
            return best_player.name
        elif self.current_game_mode == GameMode.TEAM_DEATHMATCH:
            # Team with most kills
            team_scores = {}
            for team_id, player_ids in self.teams.items():
                team_score = sum(self.players[pid].kills for pid in player_ids)
                team_scores[team_id] = team_score
            
            winning_team = max(team_scores.keys(), key=lambda t: team_scores[t])
            return f"Team {winning_team}"
        else:
            return "Game completed"
    
    def get_player_input(self, player_id: int) -> Dict[str, Any]:
        """Get input for a specific player"""
        # In a real implementation, this would get input from the player's controller
        # For now, return mock input
        return {
            'throttle': 0.0,
            'brake': 0.0,
            'steering': 0.0,
            'handbrake': False,
            'fire': False,
            'aim': False,
            'reload': False,
            'next_weapon': False,
            'prev_weapon': False,
            'enter_exit_vehicle': False,
            'interact': False,
            'jump': False,
            'crouch': False,
            'sprint': False
        }
    
    def get_multiplayer_statistics(self) -> Dict[str, Any]:
        """Get multiplayer statistics"""
        return {
            'total_players': len(self.players),
            'max_players': self.max_players,
            'game_mode': self.current_game_mode.value,
            'game_started': self.game_started,
            'round_time': self.round_time,
            'players': {
                pid: {
                    'name': player.name,
                    'state': player.state.value,
                    'score': player.score,
                    'kills': player.kills,
                    'deaths': player.deaths,
                    'team_id': player.team_id
                }
                for pid, player in self.players.items()
            },
            'teams': self.teams,
            'cameras': len(self.split_screen.cameras)
        }


# Test the multiplayer system
if __name__ == "__main__":
    print("🧪 Testing Multiplayer System...")
    
    # Create dependencies
    from saiyanquest.physics_manager import PhysicsManager
    from saiyanquest.vehicle_physics import VehiclePhysicsSystem
    from saiyanquest.character_ai import CharacterAIManager
    from saiyanquest.world_3d_system import World3DSystem
    
    physics_manager = PhysicsManager(gravity=(0, 0))
    vehicle_physics = VehiclePhysicsSystem(physics_manager)
    character_ai = CharacterAIManager(physics_manager)
    world_3d = World3DSystem(1000, 1000, 2)
    
    # Create multiplayer manager
    multiplayer = MultiplayerManager(physics_manager, vehicle_physics, character_ai, world_3d)
    
    # Add players
    player1_id = multiplayer.add_player("Player1")
    player2_id = multiplayer.add_player("Player2")
    player3_id = multiplayer.add_player("Player3")
    player4_id = multiplayer.add_player("Player4")
    
    # Set players ready
    multiplayer.set_player_ready(player1_id)
    multiplayer.set_player_ready(player2_id)
    multiplayer.set_player_ready(player3_id)
    multiplayer.set_player_ready(player4_id)
    
    # Start game
    multiplayer.start_game(GameMode.TEAM_DEATHMATCH)
    
    # Run simulation
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update multiplayer
        multiplayer.update(dt)
        
        # Update physics
        physics_manager.update(dt)
        
        if frame % 60 == 0:  # Print every second
            stats = multiplayer.get_multiplayer_statistics()
            print(f"  Frame {frame}: Players = {stats['total_players']}, "
                  f"Game Mode = {stats['game_mode']}, "
                  f"Round Time = {stats['round_time']:.1f}s")
    
    print("✅ Multiplayer System test completed")