#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Open World System for SaiyanQuest

import pygame
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class DistrictType(Enum):
    DOWNTOWN = "downtown"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    BEACH = "beach"
    HILLS = "hills"
    AIRPORT = "airport"
    DOCKS = "docks"

class WantedLevel(Enum):
    NONE = 0
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5

@dataclass
class District:
    name: str
    district_type: DistrictType
    bounds: pygame.Rect
    spawn_points: List[Tuple[int, int]] = field(default_factory=list)
    crime_rate: float = 0.1  # Base crime rate for the district
    police_response_time: float = 30.0  # Seconds
    gang_territories: List[str] = field(default_factory=list)
    vehicle_spawn_types: List[str] = field(default_factory=list)
    pedestrian_density: float = 1.0
    traffic_density: float = 1.0

@dataclass 
class SafeHouse:
    name: str
    position: Tuple[int, int]
    owned: bool = False
    price: int = 0
    garage_capacity: int = 1
    save_point: bool = True
    amenities: List[str] = field(default_factory=list)

class GTAWorld:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera_x = 0
        self.camera_y = 0
        self.world_width = 8000  # Large open world
        self.world_height = 6000
        
        # Districts
        self.districts: Dict[str, District] = {}
        self.current_district: Optional[District] = None
        
        # Safe houses
        self.safe_houses: List[SafeHouse] = []
        
        # World state
        self.time_of_day = 12.0  # 24-hour format
        self.weather = "clear"
        self.wanted_level = WantedLevel.NONE
        self.chaos_level = 0.0  # 0.0 to 1.0, affects world events
        
        # Initialize the world
        self._create_districts()
        self._create_safe_houses()
        self._generate_spawn_points()

    def _create_districts(self) -> None:
        """Create the various districts of the open world"""
        
        # Downtown - Business district with skyscrapers
        self.districts["downtown"] = District(
            name="Downtown",
            district_type=DistrictType.DOWNTOWN,
            bounds=pygame.Rect(3500, 2000, 1000, 1500),
            crime_rate=0.3,
            police_response_time=15.0,
            vehicle_spawn_types=["sedan", "taxi", "police", "sports_car"],
            pedestrian_density=2.0,
            traffic_density=3.0
        )
        
        # Grove Street - Residential area
        self.districts["grove_street"] = District(
            name="Grove Street",
            district_type=DistrictType.RESIDENTIAL,
            bounds=pygame.Rect(1000, 3000, 2000, 1500),
            crime_rate=0.7,
            police_response_time=45.0,
            gang_territories=["grove_street_families"],
            vehicle_spawn_types=["low_rider", "muscle_car", "motorcycle"],
            pedestrian_density=1.2,
            traffic_density=1.0
        )
        
        # Industrial Zone
        self.districts["industrial"] = District(
            name="Industrial Zone",
            district_type=DistrictType.INDUSTRIAL,
            bounds=pygame.Rect(4500, 4000, 2000, 1500),
            crime_rate=0.4,
            police_response_time=60.0,
            vehicle_spawn_types=["truck", "van", "forklift"],
            pedestrian_density=0.5,
            traffic_density=1.5
        )
        
        # Santa Monica Beach
        self.districts["beach"] = District(
            name="Santa Monica Beach",
            district_type=DistrictType.BEACH,
            bounds=pygame.Rect(500, 500, 2500, 1000),
            crime_rate=0.1,
            police_response_time=30.0,
            vehicle_spawn_types=["convertible", "beach_buggy", "bicycle"],
            pedestrian_density=3.0,
            traffic_density=0.8
        )
        
        # Hollywood Hills
        self.districts["hills"] = District(
            name="Hollywood Hills",
            district_type=DistrictType.HILLS,
            bounds=pygame.Rect(2000, 500, 1500, 1500),
            crime_rate=0.05,
            police_response_time=20.0,
            vehicle_spawn_types=["luxury_car", "suv", "sports_car"],
            pedestrian_density=0.3,
            traffic_density=0.5
        )
        
        # Los Santos International Airport
        self.districts["airport"] = District(
            name="Los Santos Airport",
            district_type=DistrictType.AIRPORT,
            bounds=pygame.Rect(6000, 1000, 1500, 2000),
            crime_rate=0.2,
            police_response_time=10.0,
            vehicle_spawn_types=["taxi", "bus", "security_vehicle"],
            pedestrian_density=1.5,
            traffic_density=2.0
        )
        
        # Port of Los Santos
        self.districts["docks"] = District(
            name="Port of Los Santos",
            district_type=DistrictType.DOCKS,
            bounds=pygame.Rect(5500, 4500, 2000, 1000),
            crime_rate=0.6,
            police_response_time=40.0,
            gang_territories=["los_santos_vagos"],
            vehicle_spawn_types=["truck", "crane", "cargo_vehicle"],
            pedestrian_density=0.4,
            traffic_density=1.2
        )

    def _create_safe_houses(self) -> None:
        """Create safe houses throughout the world"""
        
        # Grove Street House (Free starter home)
        self.safe_houses.append(SafeHouse(
            name="Grove Street House",
            position=(2337, 3109),
            owned=True,
            price=0,
            garage_capacity=2,
            amenities=["bed", "save_point", "wardrobe"]
        ))
        
        # Downtown Penthouse
        self.safe_houses.append(SafeHouse(
            name="Downtown Penthouse",
            position=(4000, 2200),
            owned=False,
            price=500000,
            garage_capacity=5,
            amenities=["bed", "save_point", "wardrobe", "weapon_storage", "helicopter_pad"]
        ))
        
        # Beach House
        self.safe_houses.append(SafeHouse(
            name="Santa Monica Beach House",
            position=(1200, 800),
            owned=False,
            price=750000,
            garage_capacity=3,
            amenities=["bed", "save_point", "wardrobe", "boat_dock"]
        ))
        
        # Hollywood Hills Mansion
        self.safe_houses.append(SafeHouse(
            name="Hollywood Hills Mansion",
            position=(2500, 900),
            owned=False,
            price=1200000,
            garage_capacity=8,
            amenities=["bed", "save_point", "wardrobe", "weapon_storage", "pool", "tennis_court"]
        ))

    def _generate_spawn_points(self) -> None:
        """Generate spawn points for each district"""
        for district in self.districts.values():
            # Generate random spawn points within district bounds
            for _ in range(10):  # 10 spawn points per district
                x = random.randint(district.bounds.x, district.bounds.x + district.bounds.width)
                y = random.randint(district.bounds.y, district.bounds.y + district.bounds.height)
                district.spawn_points.append((x, y))

    def update_camera(self, player_x: int, player_y: int) -> None:
        """Update camera position to follow player"""
        self.camera_x = player_x - self.screen_width // 2
        self.camera_y = player_y - self.screen_height // 2
        
        # Keep camera within world bounds
        self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, self.world_height - self.screen_height))

    def get_current_district(self, x: int, y: int) -> Optional[District]:
        """Get the district at the given coordinates"""
        for district in self.districts.values():
            if district.bounds.collidepoint(x, y):
                self.current_district = district
                return district
        return None

    def update_time(self, dt: float) -> None:
        """Update game time (accelerated)"""
        self.time_of_day += dt * 0.5  # 1 real second = 30 game minutes
        if self.time_of_day >= 24.0:
            self.time_of_day = 0.0

    def get_lighting_factor(self) -> float:
        """Get lighting factor based on time of day (0.0 = night, 1.0 = day)"""
        if 6.0 <= self.time_of_day <= 18.0:
            return 1.0  # Day time
        elif self.time_of_day <= 6.0:
            # Early morning/night
            return 0.3 + (self.time_of_day / 6.0) * 0.7
        else:
            # Evening
            return 0.3 + ((24.0 - self.time_of_day) / 6.0) * 0.7

    def increase_wanted_level(self, amount: int = 1) -> None:
        """Increase player's wanted level"""
        current_level = self.wanted_level.value
        new_level = min(5, current_level + amount)
        self.wanted_level = WantedLevel(new_level)

    def decrease_wanted_level(self, amount: int = 1) -> None:
        """Decrease player's wanted level"""
        current_level = self.wanted_level.value
        new_level = max(0, current_level - amount)
        self.wanted_level = WantedLevel(new_level)

    def get_nearest_safe_house(self, x: int, y: int) -> Optional[SafeHouse]:
        """Get the nearest safe house to the given position"""
        if not self.safe_houses:
            return None
            
        nearest = None
        min_distance = float('inf')
        
        for safe_house in self.safe_houses:
            distance = ((x - safe_house.position[0]) ** 2 + (y - safe_house.position[1]) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = safe_house
                
        return nearest

    def can_enter_safe_house(self, safe_house: SafeHouse, player_money: int) -> bool:
        """Check if player can enter/buy a safe house"""
        if safe_house.owned:
            return True
        return player_money >= safe_house.price

    def buy_safe_house(self, safe_house: SafeHouse) -> bool:
        """Purchase a safe house"""
        if not safe_house.owned:
            safe_house.owned = True
            return True
        return False

    def is_in_gang_territory(self, x: int, y: int) -> Optional[str]:
        """Check if position is in gang territory"""
        district = self.get_current_district(x, y)
        if district and district.gang_territories:
            return district.gang_territories[0]  # Return first gang in territory
        return None

    def should_spawn_police(self) -> bool:
        """Determine if police should spawn based on wanted level"""
        if self.wanted_level == WantedLevel.NONE:
            return False
        
        # Higher wanted level = more frequent spawns
        spawn_chance = self.wanted_level.value * 0.1
        return random.random() < spawn_chance

    def get_police_spawn_distance(self) -> int:
        """Get distance at which police should spawn from player"""
        base_distance = 500
        return base_distance + (self.wanted_level.value * 200)

    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.camera_x
        screen_y = world_y - self.camera_y
        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        return world_x, world_y

    def render_minimap(self, surface: pygame.Surface, player_x: int, player_y: int, size: int = 200) -> None:
        """Render a minimap in the corner of the screen"""
        minimap_surface = pygame.Surface((size, size))
        minimap_surface.fill((20, 20, 20))  # Dark background
        
        # Calculate minimap scale
        scale_x = size / self.world_width
        scale_y = size / self.world_height
        
        # Draw districts on minimap
        for district in self.districts.values():
            rect = pygame.Rect(
                district.bounds.x * scale_x,
                district.bounds.y * scale_y,
                district.bounds.width * scale_x,
                district.bounds.height * scale_y
            )
            
            # Color code districts
            if district.district_type == DistrictType.DOWNTOWN:
                color = (100, 100, 150)
            elif district.district_type == DistrictType.RESIDENTIAL:
                color = (100, 150, 100)
            elif district.district_type == DistrictType.INDUSTRIAL:
                color = (150, 100, 50)
            elif district.district_type == DistrictType.BEACH:
                color = (100, 150, 200)
            elif district.district_type == DistrictType.HILLS:
                color = (150, 150, 100)
            else:
                color = (120, 120, 120)
                
            pygame.draw.rect(minimap_surface, color, rect)
        
        # Draw player position
        player_minimap_x = int(player_x * scale_x)
        player_minimap_y = int(player_y * scale_y)
        pygame.draw.circle(minimap_surface, (255, 255, 0), (player_minimap_x, player_minimap_y), 3)
        
        # Draw safe houses
        for safe_house in self.safe_houses:
            house_x = int(safe_house.position[0] * scale_x)
            house_y = int(safe_house.position[1] * scale_y)
            color = (0, 255, 0) if safe_house.owned else (255, 255, 255)
            pygame.draw.circle(minimap_surface, color, (house_x, house_y), 2)
        
        # Blit minimap to main surface
        surface.blit(minimap_surface, (surface.get_width() - size - 20, 20))