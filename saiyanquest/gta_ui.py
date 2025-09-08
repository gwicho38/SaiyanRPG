#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style UI and HUD System for SaiyanQuest

import pygame
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from .character_system import Character, CharacterManager, CharacterType
from .gta_world import GTAWorld, WantedLevel
from .weapon_system import Weapon, WeaponInventory
from .vehicle_system import Vehicle
from .mission_system import Mission, Objective

class UIElement(Enum):
    HEALTH_BAR = "health_bar"
    ARMOR_BAR = "armor_bar"
    WANTED_LEVEL = "wanted_level"
    MONEY = "money"
    WEAPON_INFO = "weapon_info"
    MINIMAP = "minimap"
    MISSION_INFO = "mission_info"
    SPEEDOMETER = "speedometer"
    RADIO_INFO = "radio_info"
    TIME = "time"
    OBJECTIVE_MARKER = "objective_marker"

@dataclass
class UIColors:
    HEALTH_GREEN = (76, 175, 80)
    HEALTH_YELLOW = (255, 235, 59)
    HEALTH_RED = (244, 67, 54)
    ARMOR_BLUE = (33, 150, 243)
    MONEY_GREEN = (76, 175, 80)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    GOLD = (255, 193, 7)
    RED = (244, 67, 54)
    BLUE = (33, 150, 243)
    TRANSPARENT_BLACK = (0, 0, 0, 128)
    TRANSPARENT_WHITE = (255, 255, 255, 128)

class GTAFont:
    def __init__(self):
        # Initialize fonts (would load custom GTA fonts in real implementation)
        pygame.font.init()
        self.small = pygame.font.Font(None, 20)
        self.medium = pygame.font.Font(None, 28)
        self.large = pygame.font.Font(None, 36)
        self.xlarge = pygame.font.Font(None, 48)
        
        # Try to load a more appropriate font
        try:
            self.small = pygame.font.Font("assets/fonts/gta_font.ttf", 20)
            self.medium = pygame.font.Font("assets/fonts/gta_font.ttf", 28) 
            self.large = pygame.font.Font("assets/fonts/gta_font.ttf", 36)
            self.xlarge = pygame.font.Font("assets/fonts/gta_font.ttf", 48)
        except:
            pass  # Use default fonts if custom font not available

class GTAHUD:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = UIColors()
        self.fonts = GTAFont()
        
        # HUD visibility
        self.visible = True
        self.element_visibility: Dict[UIElement, bool] = {
            element: True for element in UIElement
        }
        
        # Animation states
        self.health_flash = 0.0
        self.wanted_flash = 0.0
        self.money_change_timer = 0.0
        self.last_money_amount = 0
        
        # Cached surfaces for performance
        self.cached_surfaces: Dict[str, pygame.Surface] = {}
        
    def update(self, dt: float, character: Character, world: GTAWorld) -> None:
        """Update HUD animations and states"""
        # Health flash when low
        if character.health < 25:
            self.health_flash += dt * 8
        else:
            self.health_flash = 0
            
        # Wanted level flash
        if world.wanted_level != WantedLevel.NONE:
            self.wanted_flash += dt * 6
        else:
            self.wanted_flash = 0
            
        # Money change detection
        if character.money != self.last_money_amount:
            self.money_change_timer = 2.0
            self.last_money_amount = character.money
        elif self.money_change_timer > 0:
            self.money_change_timer -= dt

    def render(self, surface: pygame.Surface, character: Character, world: GTAWorld,
              current_weapon: Optional[Weapon], current_vehicle: Optional[Vehicle],
              current_mission: Optional[Mission]) -> None:
        """Render the complete HUD"""
        if not self.visible:
            return
            
        # Render individual HUD elements
        self._render_health_armor(surface, character)
        self._render_wanted_level(surface, world.wanted_level)
        self._render_money_respect(surface, character)
        self._render_weapon_info(surface, current_weapon)
        self._render_minimap(surface, world, character.money, character.money)  # Placeholder for player position
        
        if current_vehicle:
            self._render_speedometer(surface, current_vehicle)
            self._render_radio_info(surface, current_vehicle)
            
        if current_mission:
            self._render_mission_info(surface, current_mission)
            
        self._render_time(surface, world.time_of_day)

    def _render_health_armor(self, surface: pygame.Surface, character: Character) -> None:
        """Render health and armor bars"""
        if not self.element_visibility[UIElement.HEALTH_BAR]:
            return
            
        bar_width = 150
        bar_height = 20
        x = 30
        y = surface.get_height() - 100
        
        # Health bar
        health_percent = character.health / character.physics.stats.max_health
        
        # Choose color based on health level
        if health_percent > 0.6:
            health_color = self.colors.HEALTH_GREEN
        elif health_percent > 0.3:
            health_color = self.colors.HEALTH_YELLOW
        else:
            health_color = self.colors.HEALTH_RED
            
        # Flash effect when health is low
        if character.health < 25:
            flash_alpha = abs(math.sin(self.health_flash)) * 0.5 + 0.5
            health_color = tuple(int(c * flash_alpha) for c in health_color)
        
        # Background
        pygame.draw.rect(surface, self.colors.DARK_GRAY, (x-2, y-2, bar_width+4, bar_height+4))
        pygame.draw.rect(surface, self.colors.BLACK, (x, y, bar_width, bar_height))
        
        # Health fill
        fill_width = int(bar_width * health_percent)
        if fill_width > 0:
            pygame.draw.rect(surface, health_color, (x, y, fill_width, bar_height))
        
        # Health text
        health_text = f"{int(character.health)}/{int(character.physics.stats.max_health)}"
        text_surface = self.fonts.small.render(health_text, True, self.colors.WHITE)
        text_x = x + (bar_width - text_surface.get_width()) // 2
        text_y = y + (bar_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Armor bar (if character has armor)
        armor = getattr(character, 'armor', 0)
        max_armor = getattr(character, 'max_armor', 100)
        
        if armor > 0:
            armor_y = y + bar_height + 5
            armor_percent = armor / max_armor
            
            # Background
            pygame.draw.rect(surface, self.colors.DARK_GRAY, (x-2, armor_y-2, bar_width+4, bar_height+4))
            pygame.draw.rect(surface, self.colors.BLACK, (x, armor_y, bar_width, bar_height))
            
            # Armor fill
            armor_fill_width = int(bar_width * armor_percent)
            if armor_fill_width > 0:
                pygame.draw.rect(surface, self.colors.ARMOR_BLUE, (x, armor_y, armor_fill_width, bar_height))
            
            # Armor text
            armor_text = f"{int(armor)}/{int(max_armor)}"
            armor_text_surface = self.fonts.small.render(armor_text, True, self.colors.WHITE)
            armor_text_x = x + (bar_width - armor_text_surface.get_width()) // 2
            armor_text_y = armor_y + (bar_height - armor_text_surface.get_height()) // 2
            surface.blit(armor_text_surface, (armor_text_x, armor_text_y))

    def _render_wanted_level(self, surface: pygame.Surface, wanted_level: WantedLevel) -> None:
        """Render wanted level stars"""
        if not self.element_visibility[UIElement.WANTED_LEVEL] or wanted_level == WantedLevel.NONE:
            return
            
        star_size = 25
        x = surface.get_width() - 200
        y = 30
        
        # Flash effect for wanted level
        flash_alpha = 1.0
        if wanted_level != WantedLevel.NONE:
            flash_alpha = abs(math.sin(self.wanted_flash)) * 0.3 + 0.7
        
        # Draw stars
        for i in range(5):
            star_x = x + i * (star_size + 5)
            
            if i < wanted_level.value:
                # Filled star
                color = tuple(int(c * flash_alpha) for c in self.colors.RED)
                self._draw_star(surface, star_x + star_size//2, y + star_size//2, star_size//2, color)
            else:
                # Empty star outline
                self._draw_star(surface, star_x + star_size//2, y + star_size//2, star_size//2, 
                              self.colors.GRAY, filled=False)

    def _draw_star(self, surface: pygame.Surface, x: int, y: int, size: int, 
                  color: Tuple[int, int, int], filled: bool = True) -> None:
        """Draw a star shape"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.4
            
            point_x = x + radius * math.cos(angle - math.pi/2)
            point_y = y + radius * math.sin(angle - math.pi/2)
            points.append((point_x, point_y))
        
        if filled:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, 2)

    def _render_money_respect(self, surface: pygame.Surface, character: Character) -> None:
        """Render money and respect display"""
        if not self.element_visibility[UIElement.MONEY]:
            return
            
        x = surface.get_width() - 200
        y = 80
        
        # Money
        money_text = f"${character.money:,}"
        money_color = self.colors.MONEY_GREEN
        
        # Change color if money recently changed
        if self.money_change_timer > 0:
            if character.money > self.last_money_amount:
                money_color = self.colors.HEALTH_GREEN  # Gained money
            else:
                money_color = self.colors.RED  # Lost money
        
        money_surface = self.fonts.medium.render(money_text, True, money_color)
        surface.blit(money_surface, (x, y))
        
        # Respect
        respect_text = f"Respect: {character.respect}"
        respect_surface = self.fonts.small.render(respect_text, True, self.colors.GOLD)
        surface.blit(respect_surface, (x, y + 30))

    def _render_weapon_info(self, surface: pygame.Surface, weapon: Optional[Weapon]) -> None:
        """Render current weapon information"""
        if not self.element_visibility[UIElement.WEAPON_INFO] or not weapon:
            return
            
        x = surface.get_width() - 200
        y = surface.get_height() - 120
        
        # Weapon name
        weapon_name = weapon.weapon_type.value.replace('_', ' ').title()
        name_surface = self.fonts.medium.render(weapon_name, True, self.colors.WHITE)
        surface.blit(name_surface, (x, y))
        
        # Ammo (if applicable)
        if hasattr(weapon, 'current_ammo') and weapon.stats.ammo_capacity > 0:
            if weapon.is_reloading:
                ammo_text = "RELOADING"
                ammo_color = self.colors.HEALTH_YELLOW
            else:
                ammo_text = f"{weapon.current_ammo}/{weapon.reserve_ammo}"
                ammo_color = self.colors.WHITE if weapon.current_ammo > 0 else self.colors.RED
            
            ammo_surface = self.fonts.small.render(ammo_text, True, ammo_color)
            surface.blit(ammo_surface, (x, y + 25))

    def _render_minimap(self, surface: pygame.Surface, world: GTAWorld, player_x: float, player_y: float) -> None:
        """Render the minimap"""
        if not self.element_visibility[UIElement.MINIMAP]:
            return
            
        minimap_size = 150
        x = surface.get_width() - minimap_size - 20
        y = surface.get_height() - minimap_size - 20
        
        # Use the world's minimap rendering
        world.render_minimap(surface, player_x, player_y, minimap_size)

    def _render_speedometer(self, surface: pygame.Surface, vehicle: Vehicle) -> None:
        """Render speedometer when in vehicle"""
        if not self.element_visibility[UIElement.SPEEDOMETER]:
            return
            
        x = 50
        y = surface.get_height() - 200
        radius = 60
        
        # Background circle
        pygame.draw.circle(surface, self.colors.DARK_GRAY, (x, y), radius + 2)
        pygame.draw.circle(surface, self.colors.BLACK, (x, y), radius)
        
        # Speed
        speed_kmh = vehicle.get_speed_kmh()
        max_speed = vehicle.stats.max_speed
        
        # Speed arc (0 to 180 degrees)
        speed_ratio = min(1.0, speed_kmh / max_speed)
        end_angle = math.pi * speed_ratio
        
        # Draw speed arc
        if speed_ratio > 0:
            arc_points = []
            for i in range(int(end_angle * 20)):
                angle = math.pi - i * math.pi / 20
                point_x = x + (radius - 10) * math.cos(angle)
                point_y = y - (radius - 10) * math.sin(angle)
                arc_points.append((point_x, point_y))
            
            if len(arc_points) > 1:
                pygame.draw.lines(surface, self.colors.HEALTH_GREEN, False, arc_points, 5)
        
        # Speed text
        speed_text = f"{int(speed_kmh)}"
        speed_surface = self.fonts.large.render(speed_text, True, self.colors.WHITE)
        text_rect = speed_surface.get_rect(center=(x, y))
        surface.blit(speed_surface, text_rect)
        
        # KM/H label
        kmh_surface = self.fonts.small.render("KM/H", True, self.colors.LIGHT_GRAY)
        kmh_rect = kmh_surface.get_rect(center=(x, y + 25))
        surface.blit(kmh_surface, kmh_rect)

    def _render_radio_info(self, surface: pygame.Surface, vehicle: Vehicle) -> None:
        """Render radio station info when in vehicle"""
        if not self.element_visibility[UIElement.RADIO_INFO]:
            return
            
        # Radio station (placeholder)
        station = getattr(vehicle, 'radio_station', 'Los Santos Rock Radio')
        song = getattr(vehicle, 'current_song', 'Welcome to the Jungle - Guns N\' Roses')
        
        x = 30
        y = 30
        
        # Background
        bg_width = 300
        bg_height = 50
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill(self.colors.TRANSPARENT_BLACK)
        surface.blit(bg_surface, (x, y))
        
        # Station name
        station_surface = self.fonts.small.render(station, True, self.colors.WHITE)
        surface.blit(station_surface, (x + 10, y + 5))
        
        # Current song
        song_surface = self.fonts.small.render(song, True, self.colors.LIGHT_GRAY)
        surface.blit(song_surface, (x + 10, y + 25))

    def _render_mission_info(self, surface: pygame.Surface, mission: Mission) -> None:
        """Render current mission information"""
        if not self.element_visibility[UIElement.MISSION_INFO]:
            return
            
        current_objective = mission.get_current_objective()
        if not current_objective:
            return
            
        x = 30
        y = surface.get_height() // 2 - 100
        
        # Background
        bg_width = 400
        bg_height = 80
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill(self.colors.TRANSPARENT_BLACK)
        surface.blit(bg_surface, (x, y))
        
        # Mission title
        title_surface = self.fonts.medium.render(mission.title, True, self.colors.GOLD)
        surface.blit(title_surface, (x + 10, y + 5))
        
        # Current objective
        objective_text = current_objective.description
        objective_surface = self.fonts.small.render(objective_text, True, self.colors.WHITE)
        surface.blit(objective_surface, (x + 10, y + 35))
        
        # Progress (if applicable)
        if current_objective.target_count > 1:
            progress_text = f"{current_objective.current_count}/{current_objective.target_count}"
            progress_surface = self.fonts.small.render(progress_text, True, self.colors.LIGHT_GRAY)
            surface.blit(progress_surface, (x + 300, y + 35))

    def _render_time(self, surface: pygame.Surface, time_of_day: float) -> None:
        """Render current game time"""
        if not self.element_visibility[UIElement.TIME]:
            return
            
        hours = int(time_of_day)
        minutes = int((time_of_day - hours) * 60)
        
        time_text = f"{hours:02d}:{minutes:02d}"
        time_surface = self.fonts.small.render(time_text, True, self.colors.WHITE)
        
        x = surface.get_width() - time_surface.get_width() - 20
        y = surface.get_height() - 30
        surface.blit(time_surface, (x, y))

    def render_objective_marker(self, surface: pygame.Surface, objective: Objective, 
                              player_x: float, player_y: float, camera_x: float, camera_y: float) -> None:
        """Render objective marker on screen"""
        if not self.element_visibility[UIElement.OBJECTIVE_MARKER]:
            return
            
        # Calculate screen position
        screen_x = objective.target_x - camera_x
        screen_y = objective.target_y - camera_y
        
        # Check if objective is on screen
        margin = 50
        if (margin <= screen_x <= self.screen_width - margin and 
            margin <= screen_y <= self.screen_height - margin):
            # Draw marker at objective location
            marker_size = 20
            pygame.draw.circle(surface, self.colors.GOLD, (int(screen_x), int(screen_y)), marker_size, 3)
            pygame.draw.circle(surface, self.colors.WHITE, (int(screen_x), int(screen_y)), marker_size - 5, 1)
        else:
            # Draw arrow pointing to objective
            self._render_offscreen_marker(surface, objective.target_x, objective.target_y, 
                                        player_x, player_y)

    def _render_offscreen_marker(self, surface: pygame.Surface, target_x: float, target_y: float,
                               player_x: float, player_y: float) -> None:
        """Render marker for offscreen objectives"""
        # Calculate angle to target
        angle = math.atan2(target_y - player_y, target_x - player_x)
        
        # Position on screen edge
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Distance from center to edge (considering screen bounds)
        distance = min(center_x - 50, center_y - 50)
        
        marker_x = center_x + distance * math.cos(angle)
        marker_y = center_y + distance * math.sin(angle)
        
        # Draw arrow
        arrow_size = 15
        arrow_points = [
            (marker_x + arrow_size * math.cos(angle), marker_y + arrow_size * math.sin(angle)),
            (marker_x + arrow_size * math.cos(angle + 2.5), marker_y + arrow_size * math.sin(angle + 2.5)),
            (marker_x + arrow_size * math.cos(angle - 2.5), marker_y + arrow_size * math.sin(angle - 2.5))
        ]
        
        pygame.draw.polygon(surface, self.colors.GOLD, arrow_points)

    def toggle_element_visibility(self, element: UIElement) -> None:
        """Toggle visibility of a HUD element"""
        self.element_visibility[element] = not self.element_visibility[element]

    def set_element_visibility(self, element: UIElement, visible: bool) -> None:
        """Set visibility of a HUD element"""
        self.element_visibility[element] = visible

    def toggle_hud_visibility(self) -> None:
        """Toggle entire HUD visibility"""
        self.visible = not self.visible

class GTAMenu:
    """Base class for GTA-style menus"""
    
    def __init__(self, title: str):
        self.title = title
        self.visible = False
        self.selected_index = 0
        self.menu_items: List[str] = []
        self.fonts = GTAFont()
        self.colors = UIColors()
        
    def show(self) -> None:
        """Show the menu"""
        self.visible = True
        
    def hide(self) -> None:
        """Hide the menu"""
        self.visible = False
        
    def navigate_up(self) -> None:
        """Navigate up in the menu"""
        if self.menu_items:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            
    def navigate_down(self) -> None:
        """Navigate down in the menu"""
        if self.menu_items:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            
    def get_selected_item(self) -> Optional[str]:
        """Get the currently selected menu item"""
        if 0 <= self.selected_index < len(self.menu_items):
            return self.menu_items[self.selected_index]
        return None
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the menu"""
        if not self.visible:
            return
            
        # Menu background
        menu_width = 400
        menu_height = len(self.menu_items) * 40 + 100
        menu_x = (surface.get_width() - menu_width) // 2
        menu_y = (surface.get_height() - menu_height) // 2
        
        # Background with transparency
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill(self.colors.TRANSPARENT_BLACK)
        surface.blit(menu_surface, (menu_x, menu_y))
        
        # Border
        pygame.draw.rect(surface, self.colors.WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_surface = self.fonts.large.render(self.title, True, self.colors.WHITE)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, menu_y + 30))
        surface.blit(title_surface, title_rect)
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            item_y = menu_y + 70 + i * 40
            
            if i == self.selected_index:
                # Highlight selected item with bright background and border
                highlight_rect = pygame.Rect(menu_x + 10, item_y - 5, menu_width - 20, 30)
                pygame.draw.rect(surface, self.colors.GOLD, highlight_rect)
                pygame.draw.rect(surface, (255, 255, 255), highlight_rect, 2)
                item_color = self.colors.BLACK
            else:
                item_color = self.colors.WHITE
                
            item_surface = self.fonts.medium.render(item, True, item_color)
            item_rect = item_surface.get_rect(center=(surface.get_width() // 2, item_y + 10))
            surface.blit(item_surface, item_rect)

class PauseMenu(GTAMenu):
    """Main pause menu"""
    
    def __init__(self):
        super().__init__("PAUSE MENU")
        self.menu_items = [
            "Resume",
            "Map",
            "Stats",
            "Settings",
            "Save Game", 
            "Load Game",
            "Quit Game"
        ]

class StatsMenu(GTAMenu):
    """Character statistics menu"""
    
    def __init__(self, character: Character):
        super().__init__("STATISTICS")
        self.character = character
        self._update_stats()
        
    def _update_stats(self) -> None:
        """Update stats display"""
        self.menu_items = [
            f"Level: {self.character.level}",
            f"Health: {self.character.health:.0f}/{self.character.physics.stats.max_health:.0f}",
            f"Money: ${self.character.money:,}",
            f"Respect: {self.character.respect}",
            f"Gang: {getattr(self.character.current_gang, 'value', self.character.current_gang).replace('_', ' ').title()}",
            f"Missions Completed: {self.character.missions_completed}",
            f"Territories: {len(self.character.territory_controlled)}",
            "Back"
        ]

class UIManager:
    """Manages all UI elements and menus"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.hud = GTAHUD(screen_width, screen_height)
        self.pause_menu = PauseMenu()
        self.current_menu: Optional[GTAMenu] = None
        
        # Input handling
        self.input_cooldown = 0.0
        
    def update(self, dt: float, character: Character, world: GTAWorld) -> None:
        """Update all UI elements"""
        self.hud.update(dt, character, world)
        
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
            
    def render(self, surface: pygame.Surface, character: Character, world: GTAWorld,
              current_weapon: Optional[Weapon], current_vehicle: Optional[Vehicle],
              current_mission: Optional[Mission]) -> None:
        """Render all UI elements"""
        # Render HUD
        self.hud.render(surface, character, world, current_weapon, current_vehicle, current_mission)
        
        # Render current menu
        if self.current_menu:
            self.current_menu.render(surface)
            
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events, return action if any"""
        if self.input_cooldown > 0:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_menu:
                    self.current_menu = None
                else:
                    self.current_menu = self.pause_menu
                    self.pause_menu.show()
                self.input_cooldown = 0.2
                return "menu_toggle"
                
            elif self.current_menu:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.current_menu.navigate_up()
                    self.input_cooldown = 0.1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.current_menu.navigate_down() 
                    self.input_cooldown = 0.1
                elif event.key == pygame.K_RETURN:
                    selected = self.current_menu.get_selected_item()
                    self.input_cooldown = 0.2
                    return f"menu_select_{selected.lower().replace(' ', '_')}" if selected else None
                    
        return None
    
    def show_menu(self, menu: GTAMenu) -> None:
        """Show a specific menu"""
        self.current_menu = menu
        menu.show()
        
    def hide_current_menu(self) -> None:
        """Hide the current menu"""
        if self.current_menu:
            self.current_menu.hide()
            self.current_menu = None